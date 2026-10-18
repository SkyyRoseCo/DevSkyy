"""Offline regressions: no model calls or authenticated provider success implied."""

from __future__ import annotations

import asyncio
import json
import os
import subprocess
import sys
import threading
import time
from pathlib import Path

import pytest

from skyyrose.godmode_runtime import agent_adapters as a


def worker(packet):
    return dict(
        packet_sha256=a.digest(packet),
        summary="Checked supplied packet",
        findings=[],
        covered_skus=["BR-008"],
    )


def test_schema_and_binding():
    packet = {"products": [{"sku": "BR-008"}]}
    value = worker(packet)
    assert a.validate_artifact("claude-worker", value, packet) == value
    review = dict(
        packet_sha256=a.digest(packet),
        worker_sha256=a.digest(value),
        summary="Reviewed",
        findings=[],
        verdict="PASS",
    )
    assert a.validate_artifact("codex-reviewer", review, packet, value) == review
    with pytest.raises(a.AdapterError, match="worker_binding"):
        a.validate_artifact("codex-reviewer", review, packet, {**value, "summary": "changed"})
    with pytest.raises(a.AdapterError, match="packet_binding"):
        a.validate_artifact("claude-worker", value, {"changed": True})


@pytest.mark.parametrize(
    "mutation",
    [{"findings": "no"}, {"extra": True}, {"summary": "x" * 4001}, {"covered_skus": ["x", "x"]}],
)
def test_invalid_artifacts_rejected(mutation):
    with pytest.raises(a.AdapterError, match="schema"):
        a.validate_artifact("claude-worker", {**worker({}), **mutation}, {})


def test_claude_tools_and_sessions_disabled(tmp_path):
    options = a.claude_options("claude-opus-5-5", str(tmp_path))
    for key in ("tools", "allowed_tools", "plugins", "skills", "setting_sources"):
        assert options[key] == []
    assert options["disallowed_tools"] == ["*"]
    assert options["mcp_servers"] == {} and options["strict_mcp_config"] is True
    assert options["permission_mode"] == "dontAsk"
    assert options["max_budget_usd"] <= 1 and options["max_turns"] <= 2
    assert options["resume"] is None and options["continue_conversation"] is False
    assert options["extra_args"] == {"no-session-persistence": None}
    assert asyncio.run(a._deny_tool("Read", {}, None)).behavior == "deny"
    assert asyncio.run(a._deny_hook({}))["hookSpecificOutput"]["permissionDecision"] == "deny"


def test_codex_no_inherited_tools_config_and_rules():
    command = a.codex_command("/codex", "gpt-6.1-sol", "/isolated", "/schema", "/out")
    for flag in ("--ephemeral", "--ignore-user-config", "--ignore-rules", "--strict-config"):
        assert flag in command
    assert command[command.index("--sandbox") + 1] == "read-only"
    for config in (
        'web_search="disabled"',
        "features.shell_tool=false",
        "features.plugins=false",
        "features.hooks=false",
        "features.apps=false",
        "mcp_servers={}",
        "project_doc_max_bytes=0",
        "features.rollout_budget.limit_tokens=8000",
    ):
        assert config in command
    assert "--dangerously-bypass-approvals-and-sandbox" not in command


def test_stale_contract_never_dispatches(monkeypatch):
    monkeypatch.setattr(a, "adapter_contract", lambda: {"available": True, "revision": 2})
    monkeypatch.setattr(a, "_supervised", lambda *x: pytest.fail("must not dispatch"))
    with pytest.raises(a.AdapterError, match="contract"):
        a.run_stage("claude-worker", {}, {"available": True, "revision": 1}, lambda: False)


@pytest.mark.parametrize("raw", [b"{", b"[]", b'{"status":"FAILED"}', b'{"status":"SUCCEEDED"}'])
def test_malformed_or_unsuccessful_response(monkeypatch, raw):
    contract = {"available": True}
    monkeypatch.setattr(a, "adapter_contract", lambda: contract)
    monkeypatch.setattr(a, "_supervised", lambda *x: raw)
    with pytest.raises(a.AdapterError):
        a.run_stage("claude-worker", {}, contract, lambda: False)


def test_supervisor_timeout_and_cancel_without_model(monkeypatch):
    original = subprocess.Popen

    def sleeping(*args, **kwargs):
        args = ([sys.executable, "-c", "import time;time.sleep(30)"],)
        return original(*args, **kwargs)

    monkeypatch.setattr(a.subprocess, "Popen", sleeping)
    with pytest.raises(a.AdapterError, match="timeout"):
        a._supervised(b"{}", lambda: False, 0.15)
    cancelled = threading.Event()
    timer = threading.Timer(0.1, cancelled.set)
    timer.start()
    with pytest.raises(a.AdapterError, match="cancelled"):
        a._supervised(b"{}", cancelled.is_set, 5)
    timer.join()


@pytest.mark.skipif(os.name != "posix", reason="POSIX process groups")
def test_watchdog_parent_sigkill_kills_descendant(tmp_path):
    # Real parent process owns the only write end. SIGKILL cannot run cleanup.
    marker = tmp_path / "pids"
    code = """import os,subprocess,sys,time
r,w=os.pipe()
p=subprocess.Popen([sys.executable,"-c",sys.argv[2],str(r),sys.argv[1]],pass_fds=(r,),start_new_session=True)
os.close(r)
while True: time.sleep(1)
"""
    child = """import os,sys,threading,subprocess,time
sys.path.insert(0,sys.argv[3])
from skyyrose.godmode_runtime.agent_adapters import _watch_parent
threading.Thread(target=_watch_parent,args=(int(sys.argv[1]),5),daemon=True).start()
p=subprocess.Popen([sys.executable,"-c","import time;time.sleep(30)"])
open(sys.argv[2],"w").write(str(os.getpid())+" "+str(p.pid))
while True: time.sleep(1)
"""
    child = child.replace("sys.argv[3]", repr(str(Path.cwd())))
    parent = subprocess.Popen([sys.executable, "-c", code, str(marker), child])
    try:
        deadline = time.monotonic() + 5
        while not marker.exists() and time.monotonic() < deadline:
            time.sleep(0.02)
        assert marker.exists()
        pids = [int(v) for v in marker.read_text().split()]
        parent.kill()
        parent.wait()
        deadline = time.monotonic() + 3
        while time.monotonic() < deadline:
            alive = [
                pid
                for pid in pids
                if subprocess.run(
                    ["ps", "-o", "stat=", "-p", str(pid)], capture_output=True, text=True
                )
                .stdout.strip()
                .strip("Z")
            ]
            if not alive:
                break
            time.sleep(0.05)
        assert not alive, "supervisor/descendant survived parent SIGKILL"
    finally:
        parent.kill() if parent.poll() is None else None
        parent.wait()


def test_packet_limit_is_explicit_and_never_truncated(monkeypatch):
    contract = {"available": True}
    monkeypatch.setattr(a, "adapter_contract", lambda: contract)
    monkeypatch.setattr(a, "_supervised", lambda *x: pytest.fail("oversize dispatch forbidden"))
    with pytest.raises(a.AdapterError, match="packet_too_large"):
        a.run_stage("claude-worker", {"text": "x" * a.MAX_PACKET_BYTES}, contract, lambda: False)


def test_codex_child_uses_only_chatgpt_auth_and_no_cross_provider_key(monkeypatch, tmp_path):
    auth_home = tmp_path / "original"
    auth_home.mkdir()
    (auth_home / "auth.json").write_text(
        json.dumps({"auth_mode": "chatgpt", "tokens": {"access_token": "SYNTHETIC"}})
    )
    (auth_home / "config.toml").write_text("unsafe = true")
    monkeypatch.setenv("CODEX_HOME", str(auth_home))
    monkeypatch.setenv("ANTHROPIC_API_KEY", "SYNTHETIC")
    monkeypatch.setenv("HOME", str(tmp_path))
    captured = {}

    class FakeProcess:
        returncode = 0

        def __init__(self, command, **kwargs):
            import io

            self.stdin = io.BytesIO()
            captured["home"] = Path(os.environ["CODEX_HOME"])
            captured["files"] = [v.name for v in captured["home"].iterdir()]
            assert "ANTHROPIC_API_KEY" not in os.environ
            target = Path(command[command.index("--output-last-message") + 1])
            target.write_text(json.dumps({"review": "fixture"}))

        def poll(self):
            return 0

    monkeypatch.setattr(a.subprocess, "Popen", FakeProcess)
    result = a._child(
        {
            "stage": "codex-reviewer",
            "packet": {},
            "worker": {},
            "contract": {
                "codex_executable": "/codex",
                "codex_model": "gpt-6.1-sol",
                "codex_auth_sha256": a.digest(
                    {
                        "codex-auth": {
                            "auth_mode": "chatgpt",
                            "tokens": {"access_token": "SYNTHETIC"},
                        }
                    }
                ),
            },
        }
    )
    assert result["status"] == "SUCCEEDED"
    assert captured["files"] == ["auth.json"]
    assert not captured["home"].exists()


def test_contract_explicit_models_authpresence_and_source_binding(monkeypatch, tmp_path):
    monkeypatch.setenv("CODEX_HOME", str(tmp_path))
    monkeypatch.setenv("ANTHROPIC_API_KEY", "SYNTHETIC")
    monkeypatch.delenv("GOD_MODE_CLAUDE_MODEL", raising=False)
    monkeypatch.delenv("GOD_MODE_CODEX_MODEL", raising=False)
    (tmp_path / "auth.json").write_text('{"auth_mode":"chatgpt"}')
    monkeypatch.setattr(a.subprocess, "check_output", lambda *x, **y: b"codex-cli fixture")
    monkeypatch.setattr(a.shutil, "which", lambda *x: "/codex")
    monkeypatch.setattr(a, "_executable_digest", lambda path: "f" * 64)
    contract = a.adapter_contract()
    assert contract["available"] is True
    assert contract["claude_model"] == "claude-opus-5-5"
    assert contract["codex_model"] == "gpt-6.1-sol"
    assert len(contract["implementation_sha256"]) == 64
    monkeypatch.delenv("ANTHROPIC_API_KEY")
    assert a.adapter_contract()["available"] is False


@pytest.mark.parametrize("changed_provider", ["claude", "codex"])
def test_auth_identity_change_invalidates_contract_before_dispatch(
    monkeypatch, tmp_path, changed_provider
):
    monkeypatch.setenv("CODEX_HOME", str(tmp_path))
    monkeypatch.setenv("ANTHROPIC_API_KEY", "SYNTHETIC-KEY-A")
    auth = tmp_path / "auth.json"
    auth.write_text('{"auth_mode":"chatgpt","tokens":{"access_token":"SYNTHETIC-A"}}')
    monkeypatch.setattr(a.subprocess, "check_output", lambda *x, **y: b"codex-cli fixture")
    monkeypatch.setattr(a.shutil, "which", lambda *x: "/codex")
    monkeypatch.setattr(a, "_executable_digest", lambda path: "f" * 64)
    contract = a.adapter_contract()
    assert contract == a.adapter_contract()
    assert "SYNTHETIC" not in json.dumps(contract)
    if changed_provider == "claude":
        monkeypatch.setenv("ANTHROPIC_API_KEY", "SYNTHETIC-KEY-B")
    else:
        auth.write_text('{"auth_mode":"chatgpt","tokens":{"access_token":"SYNTHETIC-B"}}')
    monkeypatch.setattr(a, "_supervised", lambda *x: pytest.fail("changed auth must not dispatch"))
    with pytest.raises(a.AdapterError, match="contract"):
        a.run_stage("claude-worker", {}, contract, lambda: False)


def test_auth_json_format_does_not_change_identity(monkeypatch, tmp_path):
    monkeypatch.setenv("CODEX_HOME", str(tmp_path))
    monkeypatch.setenv("ANTHROPIC_API_KEY", "SYNTHETIC")
    monkeypatch.setattr(a.subprocess, "check_output", lambda *x, **y: b"codex-cli fixture")
    monkeypatch.setattr(a.shutil, "which", lambda *x: "/codex")
    monkeypatch.setattr(a, "_executable_digest", lambda path: "f" * 64)
    auth = tmp_path / "auth.json"
    auth.write_text('{"auth_mode":"chatgpt","tokens":{}}')
    before = a.adapter_contract()
    auth.write_text('{ "tokens": {}, "auth_mode": "chatgpt" }')
    assert a.adapter_contract() == before
    assert before["timeout_seconds"] == 100


def test_supervisor_reports_safe_local_failure_without_network():
    raw = json.dumps(
        {
            "stage": "claude-worker",
            "packet": {},
            "contract": {"claude_auth_sha256": "intentionally-wrong"},
        }
    ).encode()
    with pytest.raises(a.AdapterError, match="claude_auth_changed_supervisor_starting"):
        a._supervised(raw, lambda: False, 5)


@pytest.mark.parametrize(
    "exc,code",
    [
        (TypeError("SECRET_VALUE"), "adapter_type_error"),
        (RuntimeError("unknown option --SECRET_VALUE"), "cli_unsupported_option"),
        (a.AdapterError("SECRET_VALUE"), "provider_error"),
    ],
)
def test_failure_diagnostics_do_not_echo_private_data(exc, code):
    result = a._safe_failure(exc)
    assert result["error_code"] == code
    assert "SECRET_VALUE" not in json.dumps(result)
    assert result["usage"] == {"known": False, "retry_safe": False}


def test_actual_installed_sdk_accepts_streaming_with_deny_callback(monkeypatch, tmp_path):
    import claude_agent_sdk

    original_query = claude_agent_sdk.query

    class ReachedTransport(Exception):
        pass

    class OfflineTransport:
        async def connect(self):
            raise ReachedTransport()

    async def offline_query(*, prompt, options):
        async for message in original_query(
            prompt=prompt, options=options, transport=OfflineTransport()
        ):
            yield message

    monkeypatch.setattr(claude_agent_sdk, "query", offline_query)
    payload = {
        "stage": "claude-worker",
        "packet": {},
        "worker": None,
        "contract": {"claude_model": "claude-opus-5-5"},
    }
    with pytest.raises(ReachedTransport):
        asyncio.run(a._claude(payload, str(tmp_path)))


def test_streaming_prompt_is_one_exact_source_message():
    payload = {
        "stage": "claude-worker",
        "packet": {"products": [{"sku": "BR-008"}]},
        "worker": None,
    }

    async def collect():
        return [message async for message in a._claude_prompt(payload)]

    messages = asyncio.run(collect())
    assert len(messages) == 1
    assert messages[0]["message"]["content"] == a._prompt(payload)
    assert messages[0]["message"]["role"] == "user"
    assert messages[0]["session_id"] == ""


def test_claude_reasoning_and_output_are_bounded(tmp_path):
    options = a.claude_options("claude-opus-5-5", str(tmp_path))
    assert options["thinking"] == {"type": "adaptive"}
    assert options["effort"] == "medium"
    assert options["env"] == {"CLAUDE_CODE_MAX_OUTPUT_TOKENS": "8192"}


def test_lifecycle_evidence_uses_only_fixed_phase_enums():
    data = b'{"phase":"claude_initialized"}\n{"phase":"SECRET_PROVIDER_TEXT"}\ninvalid\n'
    assert a._last_phase(data, "supervisor_starting") == "claude_initialized"


def test_timeout_preserves_safe_last_lifecycle_phase(monkeypatch):
    original = subprocess.Popen

    def sleeping(*args, **kwargs):
        args = (
            [
                sys.executable,
                "-c",
                "import time,json;print(json.dumps(dict(phase='claude_initialized')),flush=True);time.sleep(30)",
            ],
        )
        return original(*args, **kwargs)

    monkeypatch.setattr(a.subprocess, "Popen", sleeping)
    with pytest.raises(a.AdapterError, match="timeout_claude_initialized"):
        a._supervised(b"{}", lambda: False, 0.25)


@pytest.mark.parametrize("mode", ["valid", "codefence", "malformed", "wrong-model", "token-limit"])
def test_claude_success_plaintext_is_strictly_locally_validated(monkeypatch, tmp_path, mode):
    import claude_agent_sdk

    packet = {"products": [{"sku": "BR-008"}]}
    artifact = worker(packet)
    text = json.dumps(artifact)
    if mode == "codefence":
        text = "```json\n" + text + "\n```"
    elif mode == "malformed":
        text = "{"

    async def offline_query(*, prompt, options):
        assert options.output_format is None
        assert options.tools == [] and options.disallowed_tools == ["*"]
        messages = [message async for message in prompt]
        assert "ONLY one JSON object" in messages[0]["message"]["content"]
        yield claude_agent_sdk.AssistantMessage(
            content=[claude_agent_sdk.TextBlock(text=text)],
            model="claude-sonnet-4-6" if mode == "wrong-model" else "claude-opus-5-5",
        )
        yield claude_agent_sdk.ResultMessage(
            subtype="success",
            duration_ms=1,
            duration_api_ms=1,
            is_error=False,
            num_turns=1,
            session_id="fixture",
            total_cost_usd=0,
            result=text,
            stop_reason="max_tokens" if mode == "token-limit" else "end_turn",
        )

    monkeypatch.setattr(claude_agent_sdk, "query", offline_query)
    payload = {
        "stage": "claude-worker",
        "packet": packet,
        "worker": None,
        "contract": {"claude_model": "claude-opus-5-5"},
    }
    if mode == "valid":
        result = asyncio.run(a._claude(payload, str(tmp_path)))
        assert result["artifact"] == artifact
        assert result["usage"]["returned_models"] == ["claude-opus-5-5"]
    elif mode == "wrong-model":
        with pytest.raises(a.AdapterError, match="claude_returned_model_mismatch"):
            asyncio.run(a._claude(payload, str(tmp_path)))
    elif mode == "token-limit":
        with pytest.raises(a.AdapterError, match="claude_output_token_limit"):
            asyncio.run(a._claude(payload, str(tmp_path)))
    else:
        with pytest.raises(a.AdapterError, match="claude_invalid_json_text"):
            asyncio.run(a._claude(payload, str(tmp_path)))


def test_nested_exception_groups_retain_only_whitelisted_causes(monkeypatch):
    class MessageParseError(Exception):
        pass

    group = ExceptionGroup(
        "PRIVATE_OUTER",
        [
            RuntimeError("PRIVATE_A"),
            ExceptionGroup("PRIVATE_INNER", [MessageParseError("PRIVATE_B")]),
        ],
    )
    monkeypatch.setattr(a, "_CURRENT_PHASE", "claude_initialized")
    result = a._safe_failure(group)
    assert result["error_code"] == "sdk_message_parse_failed"
    assert result["error_categories"] == ["provider_error", "sdk_message_parse_failed"]
    assert result["phase"] == "claude_initialized"
    assert "PRIVATE" not in json.dumps(result)
    assert result["usage"] == {"known": False, "retry_safe": False}


def test_every_typed_failure_retains_fixed_last_phase(monkeypatch):
    monkeypatch.setattr(a, "_CURRENT_PHASE", "claude_response_received")
    assert a._safe_failure(TypeError("PRIVATE"))["phase"] == "claude_response_received"


def test_opus55_cli_request_uses_adaptive_not_manual_budget(tmp_path):
    from claude_agent_sdk import ClaudeAgentOptions
    from claude_agent_sdk._internal.transport.subprocess_cli import SubprocessCLITransport

    transport = SubprocessCLITransport(
        prompt="not submitted",
        options=ClaudeAgentOptions(**a.claude_options("claude-opus-5-5", str(tmp_path))),
    )
    transport._cli_path = "/offline/claude"
    command = transport._build_command()
    assert command[command.index("--thinking") + 1] == "adaptive"
    assert "--max-thinking-tokens" not in command
    assert (
        a.claude_options("claude-opus-5-5", str(tmp_path))["env"]["CLAUDE_CODE_MAX_OUTPUT_TOKENS"]
        == "8192"
    )


def test_specific_provider_error_survives_generic_sdk_cleanup(monkeypatch, tmp_path):
    import asyncio

    import claude_agent_sdk
    from claude_agent_sdk import AssistantMessage, TextBlock

    async def stream(**kwargs):
        yield AssistantMessage(
            content=[
                TextBlock(text="thinking is not supported: synthetic-secret-should-not-escape")
            ],
            model="claude-opus-5-5",
            error="invalid_request",
        )
        raise Exception("generic cleanup with synthetic-secret")

    monkeypatch.setattr(claude_agent_sdk, "query", stream)
    with pytest.raises(a.AdapterError, match="^provider_thinking_unsupported$") as failure:
        asyncio.run(
            a._claude(
                {
                    "contract": {"claude_model": "claude-opus-5-5"},
                    "stage": "claude-worker",
                    "packet": {},
                    "worker": None,
                },
                str(tmp_path),
            )
        )
    assert "synthetic-secret" not in str(failure.value)


def test_actual_codex_configuration_includes_required_budget_fields(tmp_path):
    import os
    import shutil
    import subprocess

    executable = shutil.which("codex")
    if not executable:
        pytest.skip("Installed Codex CLI unavailable")
    command = a.codex_command(
        executable, "gpt-6.1-sol", str(tmp_path), str(tmp_path / "schema"), str(tmp_path / "out")
    )
    overrides = []
    for index, value in enumerate(command):
        if value == "-c":
            overrides.extend(command[index : index + 2])
    check = subprocess.run(
        [executable, *overrides, "features", "list"],
        capture_output=True,
        text=True,
        env={"PATH": os.environ["PATH"], "HOME": str(tmp_path), "CODEX_HOME": str(tmp_path)},
        timeout=10,
    )
    assert check.returncode == 0, "Installed CLI rejected the adapter configuration"
    assert "rollout_budget" in check.stdout
    assert "features.rollout_budget.reminder_at_remaining_tokens=[2000]" in overrides


def test_recorded_usage_limit_classified_without_provider_text(monkeypatch, tmp_path):
    import claude_agent_sdk
    from claude_agent_sdk import AssistantMessage, TextBlock

    # Recorded rejection wording; trailing credential is an illustrative leak test.
    text = (
        "You have reached your specified API usage limits. "
        "You will regain access on 2026-11-01 at 00:00 UTC. synthetic-secret-123"
    )

    async def stream(**kwargs):
        yield AssistantMessage(
            content=[TextBlock(text=text)], model="claude-opus-5-5", error="invalid_request"
        )
        raise Exception("SDK cleanup error")

    monkeypatch.setattr(claude_agent_sdk, "query", stream)
    with pytest.raises(a.AdapterError) as caught:
        asyncio.run(
            a._claude(
                {
                    "contract": {"claude_model": "claude-opus-5-5"},
                    "stage": "claude-worker",
                    "packet": {},
                    "worker": None,
                },
                str(tmp_path),
            )
        )
    failure = a._safe_failure(caught.value)
    assert failure["error_code"] == "provider_usage_limit_reached"
    assert failure["usage"] == {"known": False, "retry_safe": False}
    assert "synthetic-secret" not in json.dumps(failure)
    assert "2026-11-01" not in json.dumps(failure)
    assert a._safe_failure(RuntimeError(text))["error_code"] == "provider_usage_limit_reached"


def test_diagnostic_markers_are_strictly_allowlisted():
    assert a.AdapterError("provider_error", ["usage", "secret-value", "api"]).markers == [
        "usage",
        "api",
    ]


def test_unreadable_cli_digest_is_unavailable(tmp_path):
    assert a._executable_digest(str(tmp_path / "missing")) is None


def test_successful_analysis_cannot_poison_provider_diagnosis(monkeypatch, tmp_path):
    import claude_agent_sdk
    from claude_agent_sdk import AssistantMessage, TextBlock

    async def stream(**kwargs):
        yield AssistantMessage(
            content=[
                TextBlock(
                    text="A finding discusses specified API usage limits and thinking enabled."
                )
            ],
            model="claude-opus-5-5",
            error=None,
        )
        raise Exception("Unrelated cleanup failure")

    monkeypatch.setattr(claude_agent_sdk, "query", stream)
    with pytest.raises(Exception) as caught:
        asyncio.run(
            a._claude(
                {
                    "contract": {"claude_model": "claude-opus-5-5"},
                    "stage": "claude-worker",
                    "packet": {},
                    "worker": None,
                },
                str(tmp_path),
            )
        )
    assert not isinstance(caught.value, a.AdapterError)
    assert a._safe_failure(caught.value)["error_code"] == "provider_error"


def test_worker_instruction_routes_skill_audit_without_changing_reviewer():
    def prompt(workflow, stage="claude-worker"):
        return a._prompt({"stage": stage, "packet": {"workflow": workflow}, "worker": None}).split(
            "\nSOURCE DATA"
        )[0]

    skill = prompt("fashion-skill-analysis")
    campaign = prompt("fashion-campaign-analysis")
    assert skill.startswith("Audit the eight supplied migrated skill contracts")
    assert "required_skill_ids" in skill and "all 15 required_skus exactly once" in skill
    assert campaign.startswith("Analyze source completeness, collection/SKU coverage")
    assert (
        prompt("fashion-skill-analysis", "codex-reviewer").splitlines()[0]
        == prompt("fashion-campaign-analysis", "codex-reviewer").splitlines()[0]
    )
    assert (
        "FAIL missing SKU coverage, unsupported claims or unsafe workflow recommendations"
        in prompt("fashion-skill-analysis", "codex-reviewer")
    )
