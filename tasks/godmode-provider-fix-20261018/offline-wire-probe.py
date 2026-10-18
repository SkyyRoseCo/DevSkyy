"""Offline wire probe: localhost only, dummy key, no provider requests or secrets."""

import asyncio
import json
import os
import sys
import tempfile
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
import claude_agent_sdk
from claude_agent_sdk import ClaudeAgentOptions, query

from skyyrose.godmode_runtime.agent_adapters import claude_options

captures = []


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *args):
        pass

    def do_POST(self):
        body = json.loads(self.rfile.read(int(self.headers.get("content-length", "0"))))
        captures.append(
            {
                "path": self.path,
                "model": body.get("model"),
                "thinking": body.get("thinking"),
                "output_config": body.get("output_config"),
                "max_tokens": body.get("max_tokens"),
                "tool_choice": body.get("tool_choice"),
                "tools_count": len(body.get("tools", [])),
                "context_management": body.get("context_management"),
                "message_role_sequence": [m.get("role") for m in body.get("messages", [])],
                "system_cache_controls": [
                    m.get("cache_control") for m in body.get("system", []) if isinstance(m, dict)
                ],
                "betas": self.headers.get("anthropic-beta"),
                "header_names": sorted(self.headers.keys()),
                "body_keys": sorted(body),
            }
        )
        value = json.dumps(
            {
                "type": "error",
                "error": {
                    "type": "invalid_request_error",
                    "message": "Offline wire probe intentionally returns 400",
                },
                "request_id": "offline-fixture",
            }
        ).encode()
        self.send_response(400)
        self.send_header("content-type", "application/json")
        self.send_header("content-length", str(len(value)))
        self.end_headers()
        self.wfile.write(value)


async def run(cli, label, port):
    before = len(captures)
    with tempfile.TemporaryDirectory(prefix="godmode-wire-") as directory:
        options = claude_options("claude-opus-5-5", directory)
        options.update(
            cli_path=str(cli),
            env={
                "ANTHROPIC_API_KEY": "sk-ant-offline-synthetic-not-a-key",
                "ANTHROPIC_BASE_URL": f"http://127.0.0.1:{port}",
                "CLAUDE_CODE_MAX_OUTPUT_TOKENS": "4096",
                "CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC": "1",
                "HOME": directory,
            },
        )

        async def prompt():
            yield {
                "type": "user",
                "message": {
                    "role": "user",
                    "content": 'Return only the JSON object {"probe":true}.',
                },
                "parent_tool_use_id": None,
                "session_id": "",
            }

        outcome = "no-result"
        try:
            async with asyncio.timeout(35):
                async for message in query(prompt=prompt(), options=ClaudeAgentOptions(**options)):
                    if getattr(message, "api_error_status", None):
                        outcome = "http_" + str(message.api_error_status)
        except Exception as exc:
            outcome = type(exc).__name__
    return {"cli": label, "outcome": outcome, "requests": captures[before:]}


async def main():
    # Replace inherited provider credentials/config with fixed offline values.
    for name in list(os.environ):
        if name.startswith(("ANTHROPIC_", "CLAUDE_")):
            os.environ.pop(name, None)
    os.environ["CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC"] = "1"
    server = HTTPServer(("127.0.0.1", 0), Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    sdk = Path(claude_agent_sdk.__file__).parent / "_bundled" / "claude"
    global_cli = Path("/Users/theceo/.local/bin/claude").resolve()
    results = []
    try:
        for cli, label in [(sdk, "sdk-bundled"), (global_cli, "global-cli")]:
            results.append(await run(cli, label, server.server_port))
    finally:
        server.shutdown()
    print(
        json.dumps(
            {
                "authentication": "not applicable; synthetic local HTTP fixture",
                "external_model_calls": False,
                "results": results,
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    asyncio.run(main())
