"""Regression matrix for .claude/hooks/paid-api-stopgate.sh (and its .codex mirror).

Feeds real PreToolUse payloads (``{"tool_name": "Bash", "tool_input": {"command": ...}}``)
and asserts the gate's exit code and category text. Exit 2 = STOP-AND-SHOW.
"""

from __future__ import annotations

import pytest

from tests.hooks.conftest import HOOK_DIRS, install_hook, run_hook

HOOK = "paid-api-stopgate.sh"
ABS = "/Users/theceo/DevSkyy/.claude/worktrees/hooks-cutover"

STAGING = "WordPress STAGING deploy (staging-7e48-skyyrose.wpcomstaging.com)"
PRODUCTION = "WordPress PRODUCTION deploy (skyyrose.co)"
VERCEL = "Dashboard production deploy (Vercel — retiring; devskyy.app returns 402)"
WP_MUTATION = "WordPress production mutation"
FLY = "API production deploy (Fly, api.devskyy.app)"

# Read-only / non-executing commands the gate must let through (exit 0).
ALLOWED = [
    pytest.param(
        f"/usr/bin/grep -n x {ABS}/scripts/deploy-theme.sh | head; "
        f"wc -l {ABS}/scripts/deploy-theme.sh {ABS}/scripts/verify-deploy.sh",
        id="grep-wc-deploy-scripts",
    ),
    pytest.param(
        # The exact read-only command the pristine gate blocked on 2026-09-18
        # (hooks-audit §4a): `verify-deploy.sh ` was taken for an interpreter.
        f"/usr/bin/grep -n x {ABS}/scripts/deploy-theme.sh | head; "
        f"wc -l {ABS}/scripts/deploy-theme.sh {ABS}/scripts/verify-deploy.sh {ABS}/scripts/deploy-mu-plugin.sh",
        id="grep-wc-deploy-scripts-false-positive-2026-09-18",
    ),
    pytest.param('/usr/bin/grep -rlE "vercel --prod" somefile', id="grep-vercel-prod-literal"),
    pytest.param(
        'for p in scripts/deploy-staging.sh scripts/deploy-theme.sh; do git cat-file -e "HEAD:$p"; done',
        id="path-ending-in-sh-is-not-an-interpreter",
    ),
    pytest.param(f"cat {ABS}/scripts/deploy-production.sh", id="cat-deploy-production"),
    pytest.param(f"sed -n 1,40p {ABS}/scripts/deploy-staging.sh", id="sed-deploy-staging"),
    pytest.param(
        'echo "wp theme activate skyyrose-flagship-2"', id="echo-wp-theme-activate-is-text"
    ),
    pytest.param("jq -r .x file | grep 'wp search-replace'", id="grep-wp-search-replace-literal"),
    pytest.param("echo fly deploy", id="fly-deploy-not-in-command-position"),
    pytest.param("wp theme list", id="wp-theme-list-read-only"),
    pytest.param("wp option get stylesheet", id="wp-option-get-read-only"),
    pytest.param("vercel ls", id="vercel-ls-read-only"),
    pytest.param("npm run deploy:dry", id="npm-run-deploy-dry"),
    pytest.param("STOPSHOW_ACK=1 bash scripts/deploy-staging.sh", id="ack-staging"),
    pytest.param(
        "ENV_FILE=.env.wordpress STOPSHOW_ACK=1 bash scripts/deploy-production.sh",
        id="ack-after-other-env-assignment",
    ),
    pytest.param("git status", id="git-status"),
    # `bash -n` parses without executing -- a syntax check is not a deploy.
    pytest.param("bash -n scripts/deploy-theme.sh", id="bash-n-syntax-check"),
    pytest.param(
        "for t in a b; do python3 -m pytest $t; done; bash -n scripts/deploy-staging.sh && echo ok",
        id="loop-then-syntax-check-2026-09-19",
    ),
    pytest.param('grep -n "bash scripts/deploy-theme.sh" docs/RUNBOOK.md', id="quoted-mention"),
    pytest.param("npm run deploy:staging:dry", id="npm-deploy-staging-dry"),
    pytest.param("npm run deploy:production:dry", id="npm-deploy-production-dry"),
    pytest.param("npm run deploy:verify", id="npm-deploy-verify"),
    pytest.param("npm run deploy:verify:staging", id="npm-deploy-verify-staging"),
    pytest.param("npm run build", id="npm-run-build"),
    pytest.param("git push -u origin chore/hooks-two-theme-cutover", id="git-push-non-force"),
    pytest.param('git commit -m "never git push --force"', id="force-push-mentioned-in-message"),
    pytest.param("fly logs -a devskyy-api", id="fly-logs"),
    pytest.param("vercel env ls", id="vercel-env-ls"),
]

# Executing commands the gate must block (exit 2) with the named category.
BLOCKED = [
    pytest.param("bash scripts/deploy-theme.sh", PRODUCTION, id="bash-deploy-theme-engine"),
    pytest.param("bash scripts/deploy-staging.sh", STAGING, id="bash-deploy-staging"),
    pytest.param(
        "bash scripts/deploy-production.sh --dry-run",
        PRODUCTION,
        id="bash-deploy-production-dry-run",
    ),
    pytest.param("cd frontend && vercel --prod", VERCEL, id="vercel-prod"),
    pytest.param("wp theme activate skyyrose-flagship-2", WP_MUTATION, id="wp-theme-activate"),
    pytest.param("wp search-replace a b", WP_MUTATION, id="wp-search-replace"),
    pytest.param("fly deploy", FLY, id="fly-deploy"),
    pytest.param(
        "ENV_FILE=.env.wordpress.staging bash scripts/deploy-staging.sh",
        STAGING,
        id="env-prefixed-staging",
    ),
    pytest.param(
        f"{ABS}/scripts/deploy-production.sh", PRODUCTION, id="absolute-path-command-position"
    ),
    pytest.param("./scripts/deploy-production.sh", PRODUCTION, id="relative-path-command-position"),
    pytest.param("bash -x scripts/deploy-theme.sh", PRODUCTION, id="interpreter-with-flag"),
    pytest.param(
        "/bin/sh scripts/deploy-mu-plugin.sh", PRODUCTION, id="absolute-interpreter-mu-plugin"
    ),
    pytest.param("cd wordpress-theme && npm run deploy", "npm run deploy", id="npm-run-deploy"),
    pytest.param("npx vercel deploy --prod", VERCEL, id="npx-vercel-deploy-prod"),
    pytest.param(
        "ssh user@sftp.wp.com wp theme activate skyyrose-flagship-2", WP_MUTATION, id="wp-over-ssh"
    ),
    pytest.param(
        "wp --path=/srv/wp option update stylesheet skyyrose-flagship-2",
        WP_MUTATION,
        id="wp-option-update-stylesheet",
    ),
    pytest.param("wp db reset --yes", WP_MUTATION, id="wp-db-reset"),
    pytest.param("wp theme delete skyyrose-flagship", WP_MUTATION, id="wp-theme-delete"),
    pytest.param("flyctl deploy --remote-only", FLY, id="flyctl-deploy"),
    pytest.param(
        "curl -X POST https://api.fashn.ai/v1/run",
        "FASHN direct HTTP (paid)",
        id="fashn-http-still-gated",
    ),
    pytest.param("git push --force origin main", "Force push", id="force-push"),
    # Wrapped / quoted / compound executions (review 2026-09-19: the command-position
    # anchor let every one of these through while origin/main blocked them).
    pytest.param("(bash scripts/deploy-theme.sh)", PRODUCTION, id="subshell"),
    pytest.param("timeout 60 bash scripts/deploy-theme.sh", PRODUCTION, id="timeout-wrapper"),
    pytest.param("nohup bash scripts/deploy-production.sh &", PRODUCTION, id="nohup-background"),
    pytest.param("time bash scripts/deploy-staging.sh", STAGING, id="time-wrapper"),
    pytest.param("exec bash scripts/deploy-theme.sh", PRODUCTION, id="exec-wrapper"),
    pytest.param("command bash scripts/deploy-theme.sh", PRODUCTION, id="command-wrapper"),
    pytest.param(
        "caffeinate -i bash scripts/deploy-production.sh", PRODUCTION, id="caffeinate-wrapper"
    ),
    pytest.param('bash -c "bash scripts/deploy-staging.sh"', STAGING, id="bash-c-body"),
    pytest.param('bash "scripts/deploy-production.sh"', PRODUCTION, id="double-quoted-path"),
    pytest.param("bash 'scripts/deploy-production.sh'", PRODUCTION, id="single-quoted-path"),
    pytest.param("bash scripts/deploy-staging.sh; echo done", STAGING, id="semicolon-after"),
    pytest.param("bash scripts/deploy-production.sh|tee log", PRODUCTION, id="pipe-after"),
    pytest.param("  bash scripts/deploy-production.sh", PRODUCTION, id="leading-whitespace"),
    pytest.param(
        "cd x && \\\n  bash scripts/deploy-production.sh", PRODUCTION, id="continued-line"
    ),
    pytest.param(
        "echo x | xargs -I{} bash scripts/deploy-theme.sh", PRODUCTION, id="xargs-wrapper"
    ),
    pytest.param(
        "if bash scripts/deploy-production.sh; then echo ok; fi", PRODUCTION, id="if-condition"
    ),
    pytest.param("rtk proxy bash scripts/deploy-production.sh", PRODUCTION, id="rtk-proxy"),
    # npm scripts this branch added, other package managers, flags before the script.
    pytest.param("npm run deploy:production", "npm run deploy", id="npm-deploy-production"),
    pytest.param("npm run deploy:staging", "npm run deploy", id="npm-deploy-staging"),
    pytest.param(
        "npm run --prefix wordpress-theme deploy", "npm run deploy", id="npm-prefix-deploy"
    ),
    pytest.param("pnpm run deploy", "npm run deploy", id="pnpm-deploy"),
    pytest.param("yarn deploy", "npm run deploy", id="yarn-deploy"),
    # Flags with separate values / quoted remote commands.
    pytest.param(
        'ssh user@host "wp theme activate skyyrose-flagship-2"', WP_MUTATION, id="ssh-quoted-wp"
    ),
    pytest.param(
        "ssh -p 22 user@host wp theme activate skyyrose-flagship-2",
        WP_MUTATION,
        id="ssh-flag-value-wp",
    ),
    pytest.param("fly -a devskyy-api deploy", FLY, id="fly-short-flag-value"),
    pytest.param("vercel --cwd frontend --prod", VERCEL, id="vercel-flag-value"),
    pytest.param("git push origin +main", "Force push", id="force-push-plus-refspec"),
    pytest.param("git push origin main --force", "Force push", id="force-push-trailing-flag"),
]


def _payload(command: str) -> dict:
    return {"tool_name": "Bash", "tool_input": {"command": command}}


@pytest.mark.parametrize("command", ALLOWED)
def test_read_only_commands_pass(flavor: str, command: str) -> None:
    result = run_hook(HOOK_DIRS[flavor] / HOOK, _payload(command))
    assert result.returncode == 0, f"false positive:\n{result.stderr}"
    assert "BLOCKED" not in result.stderr


@pytest.mark.parametrize(("command", "category"), BLOCKED)
def test_executing_commands_block_with_category(flavor: str, command: str, category: str) -> None:
    result = run_hook(HOOK_DIRS[flavor] / HOOK, _payload(command))
    assert result.returncode == 2, f"gate let through: {command!r}\n{result.stderr}"
    assert "BLOCKED" in result.stderr
    assert category in result.stderr, result.stderr


def test_engine_note_names_the_wrappers(flavor: str) -> None:
    result = run_hook(HOOK_DIRS[flavor] / HOOK, _payload("bash scripts/deploy-theme.sh"))
    assert result.returncode == 2
    assert "engine" in result.stderr
    assert "deploy-staging.sh" in result.stderr and "deploy-production.sh" in result.stderr


def test_non_bash_tool_ignored(flavor: str) -> None:
    payload = {"tool_name": "Edit", "tool_input": {"file_path": "scripts/deploy-theme.sh"}}
    result = run_hook(HOOK_DIRS[flavor] / HOOK, payload)
    assert result.returncode == 0


def test_ack_only_honoured_in_leading_env_position(flavor: str) -> None:
    result = run_hook(
        HOOK_DIRS[flavor] / HOOK,
        _payload('bash scripts/deploy-staging.sh --label="STOPSHOW_ACK=1"'),
    )
    assert result.returncode == 2


def test_removed_rules_name_absent_scripts() -> None:
    """The rules that pointed at deleted scripts are gone from both copies."""
    for flavor in HOOK_DIRS:
        text = (HOOK_DIRS[flavor] / HOOK).read_text()
        for stale in ("renders\\.fashn", "renders\\.generate", "seedream_ghost_mannequin"):
            assert (
                f"'{stale}" not in text and f"{stale}\\.py.*--go" not in text
            ), f"{flavor}: stale rule {stale}"


def test_internal_error_fails_closed(tmp_path) -> None:
    """Any exit other than 0/2 from a PreToolUse hook lets the command run, so an
    internal error (here: an unbound variable under `set -u`) must become a block."""
    hook = install_hook(tmp_path, HOOK)
    text = hook.read_text()
    anchor = "command=$(read_field \"$payload\" '.tool_input.command')\n"
    assert anchor in text
    hook.write_text(text.replace(anchor, anchor + ': "$UNBOUND_FOR_FAIL_CLOSED_TEST"\n', 1))
    result = run_hook(hook, _payload("git status"))
    assert result.returncode == 2, result.stderr
    assert "internal error" in result.stderr


def test_codex_mirror_is_identical() -> None:
    assert (HOOK_DIRS["claude"] / HOOK).read_bytes() == (HOOK_DIRS["codex"] / HOOK).read_bytes()
