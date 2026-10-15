"""PATH shims for the deploy-script tests -- no network, ever.

`install_shims(tmp_path, routes)` writes a `bin/` directory containing:

* ``curl``  -- a route-driven stand-in. The routes file maps a URL *path* to
  ``status|redirect_url|body`` and the shim honours ``-o``, ``-w`` (``%{http_code}``
  / ``%{redirect_url}``) and ``-L`` (follows one hop). Status ``000`` makes it
  exit 7 like a connection failure. Every requested URL is appended to
  ``CURL_SHIM_LOG`` so tests can prove *which* URL a script fetched.
* ``ssh scp sftp sshpass lftp rsync`` -- fail loudly (exit 97, ``SHIM-BLOCKED``
  on stderr) AND append ``<tool> <argv>`` to ``SHIM_CALL_LOG`` (a file inside
  the shim dir, path baked into each shim so a script that redirects stderr
  cannot hide the call). A test that ever reaches one of these has escaped
  dry-run; harnesses assert ``blocked_calls(env) == []``.

Returns the environment overrides (PATH prefix + shim variables) to merge into
the subprocess env. Routes are ``(path, status, body, redirect_url)`` tuples;
``body`` may contain ``\\n`` escapes (expanded with ``printf %b``) but no ``|``.
"""

from __future__ import annotations

import os
from pathlib import Path

NETWORK_TOOLS = ("ssh", "scp", "sftp", "sshpass", "lftp", "rsync")

_CURL_SHIM = r"""#!/usr/bin/env bash
# Route-driven curl stand-in for tests. See tests/scripts/deploy_shims.py.
set -u
out=""; fmt=""; url=""; follow=0
while [[ $# -gt 0 ]]; do
    case "$1" in
        -o) out="$2"; shift 2 ;;
        -w) fmt="$2"; shift 2 ;;
        -A|--max-time|--connect-timeout|--retry|--retry-delay|-X|-H|--user-agent) shift 2 ;;
        -L|--location) follow=1; shift ;;
        -*) [[ "$1" == -[a-zA-Z]*L* ]] && follow=1; shift ;;
        *) url="$1"; shift ;;
    esac
done
printf '%s\n' "$url" >> "${CURL_SHIM_LOG:-/dev/null}"

path_of() {
    local rest="${1#*://}" p
    if [[ "$rest" == */* ]]; then p="/${rest#*/}"; else p="/"; fi
    printf '%s' "${p%%\?*}"
}
lookup() {
    local want="$1" line
    while IFS= read -r line; do
        if [[ "${line%%|*}" == "$want" ]]; then printf '%s\n' "$line"; return 0; fi
    done < "${CURL_SHIM_ROUTES:?CURL_SHIM_ROUTES unset}"
    return 1
}

status=404; redirect=""; body=""
if line=$(lookup "$(path_of "$url")"); then
    IFS='|' read -r _ status redirect body <<< "$line"
fi
if (( follow )) && [[ "$status" == 30* && -n "$redirect" ]]; then
    if line=$(lookup "$(path_of "$redirect")"); then
        IFS='|' read -r _ status redirect body <<< "$line"
    else
        status=404; redirect=""; body=""
    fi
fi
if [[ "$status" == "000" ]]; then
    exit 7
fi
if [[ -n "$out" ]]; then printf '%b' "$body" > "$out"; else printf '%b' "$body"; fi
if [[ -n "$fmt" ]]; then
    fmt="${fmt//%\{http_code\}/$status}"
    fmt="${fmt//%\{redirect_url\}/$redirect}"
    printf '%s' "$fmt"
fi
exit 0
"""

_BLOCKED_SHIM = """#!/usr/bin/env bash
printf '%s %s\\n' "$(basename "$0")" "$*" >> "__CALL_LOG__"
echo "SHIM-BLOCKED: $(basename "$0") $*" >&2
exit 97
"""


def style_css(theme_name: str, text_domain: str, version: str = "1.0.0") -> str:
    """A minimal WP style.css header body for a curl route (uses \\n escapes)."""
    return (
        f"/*\\nTheme Name: {theme_name}\\nVersion: {version}\\nText Domain: {text_domain}\\n*/\\n"
    )


def install_shims(
    tmp_path: Path, routes: list[tuple[str, str, str, str]] | None = None
) -> dict[str, str]:
    bin_dir = tmp_path / "shim-bin"
    bin_dir.mkdir(parents=True, exist_ok=True)
    curl = bin_dir / "curl"
    curl.write_text(_CURL_SHIM)
    curl.chmod(0o755)
    call_log = bin_dir / "blocked-calls.log"
    call_log.write_text("")
    for tool in NETWORK_TOOLS:
        shim = bin_dir / tool
        shim.write_text(_BLOCKED_SHIM.replace("__CALL_LOG__", str(call_log)))
        shim.chmod(0o755)
    routes_file = tmp_path / "curl-routes.txt"
    routes_file.write_text(
        "".join(
            f"{path}|{status}|{redirect}|{body}\n"
            for path, status, body, redirect in (routes or [])
        )
    )
    log_file = tmp_path / "curl-shim.log"
    log_file.write_text("")
    return {
        "PATH": f"{bin_dir}{os.pathsep}{os.environ.get('PATH', '')}",
        "CURL_SHIM_ROUTES": str(routes_file),
        "CURL_SHIM_LOG": str(log_file),
        "SHIM_CALL_LOG": str(call_log),
    }


def fetched_urls(env: dict[str, str]) -> list[str]:
    return Path(env["CURL_SHIM_LOG"]).read_text().splitlines()


def blocked_calls(env: dict[str, str]) -> list[str]:
    """Every ssh/scp/sftp/sshpass/lftp/rsync invocation (``<tool> <argv>``)."""
    return Path(env["SHIM_CALL_LOG"]).read_text().splitlines()
