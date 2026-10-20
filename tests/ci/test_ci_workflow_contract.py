"""Contract for the GitHub Actions workflows that gate ``main``.

Branch protection matches required checks by the job ``name`` string, so a
rename silently turns a required check into one that never reports and blocks
every PR. These tests pin the names, the fail-closed install and change
detection, the lint toolchain pins, and the review-bot retry/trigger shape.
"""

from __future__ import annotations

import json
import os
import re
import subprocess
from fnmatch import fnmatch
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[2]
WORKFLOWS = ROOT / ".github" / "workflows"
ACTIONS = ROOT / ".github" / "actions"
LINT_REQUIREMENTS = ROOT / "requirements-lint.txt"

# Mirrors `gh api repos/SkyyRoseCo/DevSkyy/branches/main/protection`
# (required_status_checks.contexts), read 2026-10-11.
REQUIRED_CHECKS = {
    "ci.yml": {
        "🔍 Lint & Static Analysis",
        "🐍 Python Tests",
        "🔐 Security Scan",
        "⚛️ Frontend Tests",
        "🏗️ WordPress Theme",
        "🎭 Playwright E2E Tests",
        "🔌 API Integration Tests",
    },
    "security-gate.yml": {"🔑 Secrets Scan"},
}
# Jobs that may be skipped on a PR whose changes cannot affect them.
PATH_FILTERED_JOBS = {"frontend-tests", "e2e-tests", "wordpress-theme"}
PINNED_SHA = re.compile(r"^[^@\s]+@[0-9a-f]{40}$")
CLAUDE_ACTION = "anthropics/claude-code-action@"


def load(name: str) -> dict:
    return yaml.safe_load((WORKFLOWS / name).read_text())


def triggers(workflow: dict) -> dict:
    # PyYAML reads the bare key `on` as boolean True.
    return workflow.get("on", workflow.get(True)) or {}


def all_steps(workflow: dict) -> list[dict]:
    return [s for job in workflow["jobs"].values() for s in job.get("steps", [])]


@pytest.mark.parametrize("filename", sorted(REQUIRED_CHECKS))
def test_required_check_names_unchanged(filename: str) -> None:
    names = {job.get("name") for job in load(filename)["jobs"].values()}
    missing = REQUIRED_CHECKS[filename] - names
    assert not missing, f"{filename} lost required check(s) {missing}; have {sorted(names)}"


def test_every_action_is_pinned_to_a_commit_sha() -> None:
    files = [*WORKFLOWS.glob("*.yml"), *ACTIONS.glob("*/action.yml")]
    unpinned = []
    for path in files:
        doc = yaml.safe_load(path.read_text())
        steps = all_steps(doc) if "jobs" in doc else doc["runs"]["steps"]
        for s in steps:
            uses = s.get("uses", "")
            if uses and not uses.startswith("./") and not PINNED_SHA.match(uses):
                unpinned.append(f"{path.name}: {uses}")
    assert not unpinned, unpinned


def test_python_installs_fail_closed() -> None:
    """`pip install -e ".[a,b]" || pip install -e .` tests a smaller env on failure."""
    offenders = []
    for path in [*WORKFLOWS.glob("*.yml"), *ACTIONS.glob("*/action.yml")]:
        for line in path.read_text().splitlines():
            if re.search(r"pip install[^|#]*-e[^|#]*\|\|", line):
                offenders.append(f"{path.name}: {line.strip()}")
    assert not offenders, offenders


def test_python_jobs_use_the_shared_setup_action() -> None:
    jobs = load("ci.yml")["jobs"]
    for job_id in ("python-tests", "security", "e2e-tests", "api-integration"):
        uses = [s.get("uses") for s in jobs[job_id]["steps"]]
        assert "./.github/actions/setup-python-env" in uses, f"{job_id}: {uses}"


def test_concurrency_cancels_stale_pr_runs_but_never_main() -> None:
    for name in ("ci.yml", "security-gate.yml"):
        conc = load(name)["concurrency"]
        assert "github.sha" in conc["group"], f"{name}: pushes to main must not share a group"
        assert conc["cancel-in-progress"] == "${{ github.event_name == 'pull_request' }}", name


def test_change_detection_fails_closed() -> None:
    jobs = load("ci.yml")["jobs"]
    assert "changes" in jobs
    for job_id in PATH_FILTERED_JOBS:
        cond = jobs[job_id]["if"]
        assert "changes" in jobs[job_id]["needs"], job_id
        # A failed detector must run the job, never skip it into a passing check.
        assert "needs.changes.result != 'success'" in cond, f"{job_id}: {cond}"
        assert "github.event_name != 'pull_request'" in cond, f"{job_id}: {cond}"
        assert "!cancelled()" in cond, f"{job_id}: {cond}"


def test_pipeline_summary_fails_on_any_failed_or_cancelled_job() -> None:
    summary = load("ci.yml")["jobs"]["summary"]
    assert set(summary["needs"]) >= {
        "lint",
        "python-tests",
        "security",
        "frontend-tests",
        "wordpress-theme",
        "e2e-tests",
        "api-integration",
    }
    script = "\n".join(s.get("run", "") for s in summary["steps"])
    assert "exit 1" in script and "failure" in script and "cancelled" in script


def test_security_scanners_run_once() -> None:
    security = load("ci.yml")["jobs"]["security"]
    lines = [ln.strip() for s in security["steps"] for ln in s.get("run", "").splitlines()]
    for tool in ("semgrep scan", "bandit -r", "pip-audit "):
        runs = [ln for ln in lines if ln.startswith(tool)]
        assert len(runs) == 1, f"{tool!r} runs {len(runs)}x: {runs}"
    # --strict fails on the editable project itself (devskyy is not on PyPI), and
    # also rejects --skip-editable; audit a frozen set that excludes it instead.
    audit = next(ln for ln in lines if ln.startswith("pip-audit "))
    assert "--strict" in audit and "-r audit-requirements.txt" in audit, audit
    assert any("--exclude-editable > audit-requirements.txt" in ln for ln in lines)


def test_lint_tools_are_exact_pins_from_one_file() -> None:
    pins = {}
    for line in LINT_REQUIREMENTS.read_text().splitlines():
        line = line.split("#", 1)[0].strip()
        if line:
            name, sep, version = line.partition("==")
            assert sep and version, f"not an exact pin: {line!r}"
            pins[name] = version
    assert set(pins) == {"ruff", "black", "isort", "mypy"}, pins
    lint = load("ci.yml")["jobs"]["lint"]
    script = "\n".join(s.get("run", "") for s in lint["steps"])
    assert "-r requirements-lint.txt" in script
    assert not re.search(r"pip install[^\n]*\b(ruff|black|isort|mypy)\b", script), script


@pytest.mark.parametrize(
    "filename", ["claude-code-review.yml", "pr-green-loop.yml", "pr-agent.yml"]
)
def test_review_bots_retry_only_fast_failures_and_never_fail_open(filename: str) -> None:
    steps = all_steps(load(filename))
    runs = [s for s in steps if s.get("uses", "").startswith(CLAUDE_ACTION)]
    assert len(runs) == 2, f"{filename}: expected first attempt + retry, got {len(runs)}"
    first, retry = runs
    assert first.get("continue-on-error") is True and first.get("id"), first
    assert first["with"] == retry["with"], "the retry must repeat the same request"
    assert not retry.get("continue-on-error"), "the retry must be able to fail the check"
    by_id = {s["id"]: s for s in steps if "id" in s}
    decide = by_id["retry-decision"]
    assert f"steps.{first['id']}.outcome == 'failure'" in decide["if"], decide
    assert '"$elapsed" -lt 120' in decide["run"], "only a fast (outage) failure is retried"
    assert "steps.retry-decision.outputs.retry == 'true'" in retry["if"], retry
    # continue-on-error must never turn a real failure green: when the first attempt
    # failed and was not retried, a later step fails the job.
    fail = steps[-1]
    assert f"steps.{first['id']}.outcome == 'failure'" in fail["if"], fail
    assert "steps.retry-decision.outputs.retry != 'true'" in fail["if"], fail
    assert "exit 1" in fail["run"] and not fail.get("continue-on-error")


def test_claude_review_cancels_stale_reviews() -> None:
    conc = load("claude-code-review.yml")["concurrency"]
    assert "pull_request.number" in conc["group"] and conc["cancel-in-progress"] is True


def test_green_loop_starts_from_a_finished_ci_run() -> None:
    wf = load("pr-green-loop.yml")
    on = triggers(wf)
    assert set(on) == {"workflow_run"}, on
    assert on["workflow_run"]["workflows"] == [load("ci.yml")["name"]]
    assert on["workflow_run"]["types"] == ["completed"]
    cond = wf["jobs"]["green-loop"]["if"]
    assert "github.event.workflow_run.conclusion == 'failure'" in cond
    assert "github.event.workflow_run.head_repository.full_name == github.repository" in cond
    prompt = "\n".join(str(s.get("with", {}).get("prompt", "")) for s in all_steps(wf))
    assert "non-gating" not in prompt, "Playwright E2E is a required check"
    assert "--watch" not in prompt, "the loop must not hold a runner waiting on CI"
    # A rerun re-tests the old SHA and GITHUB_TOKEN pushes trigger nothing, so a
    # deterministic step (not the model) dispatches both gating workflows on the fix.
    assert "gh run rerun" not in prompt and "gh workflow run" not in prompt
    dispatch = next(s for s in all_steps(wf) if s.get("name") == "Dispatch CI on the bot fix")
    assert "!cancelled()" in dispatch["if"], "a failed retry may still have pushed a fix"
    assert "gh workflow run ci.yml" in dispatch["run"]
    assert "gh workflow run security-gate.yml" in dispatch["run"]
    assert "workflow_dispatch" in triggers(load("security-gate.yml"))
    assert "workflow_dispatch" in triggers(load("ci.yml"))
    decide = next(s for s in all_steps(wf) if s.get("id") == "retry-decision")
    assert "git ls-remote" in decide["run"], "never retry after the first attempt pushed"


def test_workflow_changes_run_every_filtered_job() -> None:
    """A CI change must exercise the jobs it gates, never skip them."""
    step = next(s for s in load("ci.yml")["jobs"]["changes"]["steps"] if s.get("id") == "filter")
    filters = yaml.safe_load(step["with"]["filters"])
    probes = [".github/workflows/ci.yml", ".github/actions/setup-python-env/action.yml"]
    for group in ("app", "theme"):
        patterns = filters[group]
        includes = [p for p in patterns if not p.startswith("!")]
        # fnmatch's `*` also crosses `/`, so it over-matches excludes: a pass here is safe.
        excludes = [p[1:] for p in patterns if p.startswith("!")]
        for path in probes:
            assert any(fnmatch(path, p) for p in includes), (group, path)
            assert not any(fnmatch(path, p) for p in excludes), (group, path)


BOT_ATTEMPTS = {
    "claude-code-review.yml": ("claude-review", "claude-review-retry"),
    "pr-agent.yml": ("pr-agent-run", "pr-agent-run-retry"),
    "pr-green-loop.yml": ("green-loop-run", "green-loop-run-retry"),
}
BASH = "/bin/bash"


def run_script(script: str, cwd: Path, env: dict[str, str]) -> subprocess.CompletedProcess:
    # GitHub runs `run:` blocks as `bash -e {0}` when no shell is given.
    return subprocess.run(
        [BASH, "-e", "-c", script],
        cwd=cwd,
        env={"PATH": os.environ["PATH"], **env},
        capture_output=True,
        text=True,
        timeout=60,
    )


def step_named(workflow: dict, name: str) -> dict:
    return next(s for s in all_steps(workflow) if s.get("name") == name)


def test_review_bot_resets_plugin_state_before_its_retry() -> None:
    """The first attempt registers the marketplace; re-adding it fails the retry."""
    steps = all_steps(load("claude-code-review.yml"))
    names = [s.get("name") for s in steps]
    reset = steps[names.index("Reset plugin state before retrying")]
    assert names.index("Wait before retrying") < names.index(reset["name"])
    assert names.index(reset["name"]) < names.index("Retry Run Claude Code Review")
    assert reset["if"] == "steps.retry-decision.outputs.retry == 'true'"
    assert 'rm -rf "$HOME/.claude/plugins"' in reset["run"]


@pytest.mark.parametrize("filename", sorted(BOT_ATTEMPTS))
def test_bots_guard_the_succeeding_attempt_inline(filename: str) -> None:
    first, retry = BOT_ATTEMPTS[filename]
    wf = load(filename)
    steps = all_steps(wf)
    by_id = {s["id"]: i for i, s in enumerate(steps) if "id" in s}
    guard_at = next(
        i for i, s in enumerate(steps) if s.get("name") == "Fail when Claude did not actually run"
    )
    guard = steps[guard_at]
    assert by_id[first] < by_id[retry] < guard_at
    assert f"steps.{first}.outcome == 'success'" in guard["if"]
    assert f"steps.{retry}.outcome == 'success'" in guard["if"]
    # Both attempts write the same path: read only the attempt that succeeded,
    # never fall back to a failed attempt's stale file.
    assert guard["env"]["EXECUTION_FILE"] == (
        f"${{{{ steps.{retry}.outcome == 'success' && steps.{retry}.outputs.execution_file"
        f" || steps.{first}.outcome == 'success' && steps.{first}.outputs.execution_file"
        " || '' }}"
    )
    # The workspace holds PR code, so a ./ action could be rewritten by the PR.
    assert not [s["uses"] for s in steps if s.get("uses", "").startswith("./")]


def _result(turns: int, cost: float) -> str:
    return json.dumps(
        [
            {"type": "system", "subtype": "init", "session_id": "s"},
            {
                "type": "result",
                "subtype": "success",
                "is_error": False,
                "num_turns": turns,
                "total_cost_usd": cost,
            },
        ]
    )


@pytest.mark.parametrize(
    ("content", "passes", "message"),
    [
        (_result(26, 0.7898919499999999), True, "Claude ran: 26 turns"),
        # The revoked-token signature, from run 38102829095.
        (_result(4, 0), False, "never reached the model"),
        (json.dumps([{"type": "system", "subtype": "init"}]), False, "never reached the model"),
        ("{not json", False, "not readable JSON"),
        ("", False, "no execution file"),
        (None, False, "no execution file"),
    ],
    ids=["real-review", "zero-cost", "no-result", "corrupt", "empty", "missing"],
)
@pytest.mark.parametrize("filename", sorted(BOT_ATTEMPTS))
def test_guard_fails_a_run_that_never_reached_the_model(
    filename: str, content: str | None, passes: bool, message: str, tmp_path: Path
) -> None:
    script = step_named(load(filename), "Fail when Claude did not actually run")["run"]
    execution_file = tmp_path / "claude-execution-output.json"
    if content is not None:
        execution_file.write_text(content)
    result = run_script(script, tmp_path, {"EXECUTION_FILE": str(execution_file)})
    assert (result.returncode == 0) is passes, result.stdout + result.stderr
    assert message in result.stdout
    if message == "never reached the model":
        # The red check must carry the fix: a dead token is not a code problem.
        assert "gh secret set CLAUDE_CODE_OAUTH_TOKEN" in result.stdout


def _git(*args: str, cwd: Path) -> str:
    return subprocess.run(
        ["git", *args], cwd=cwd, check=True, capture_output=True, text=True
    ).stdout.strip()


def _commit(repo: Path, message: str) -> str:
    _git(
        "-c",
        "user.name=t",
        "-c",
        "user.email=t@t",
        "commit",
        "-q",
        "--allow-empty",
        "-m",
        message,
        cwd=repo,
    )
    return _git("rev-parse", "HEAD", cwd=repo)


@pytest.fixture
def advanced_main(tmp_path: Path) -> tuple[Path, str, str]:
    """A checkout of main commit A whose remote main has since moved on to B."""
    upstream = tmp_path / "upstream"
    upstream.mkdir()
    _git("init", "-q", "-b", "main", cwd=upstream)
    tested = _commit(upstream, "A")
    work = tmp_path / "work"
    _git("clone", "-q", "--depth=1", f"file://{upstream}", str(work), cwd=tmp_path)
    tip = _commit(upstream, "B")
    return work, tested, tip


@pytest.mark.parametrize(
    ("event", "ref", "expected"),
    [
        ("push", "refs/heads/main", "tested"),
        ("pull_request", "refs/pull/1/merge", "tip"),
        ("schedule", "refs/heads/main", "tip"),
    ],
)
def test_published_id_fetch_pins_push_runs_and_tracks_main_elsewhere(
    event: str, ref: str, expected: str, advanced_main: tuple[Path, str, str]
) -> None:
    """A push run compares against itself; others against main's moved-on tip."""
    work, tested, tip = advanced_main
    # The shallow fetch below was rejected as non-fast-forward without `+`.
    _git("update-ref", "refs/remotes/origin/main", tested, cwd=work)
    step = step_named(load("ci.yml"), "Fetch origin/main for published-id comparison")
    result = run_script(
        step["run"],
        work,
        {
            "GITHUB_EVENT_NAME": event,
            "GITHUB_REF": ref,
            "GITHUB_SHA": tested,
            "HOME": os.environ.get("HOME", str(work)),
        },
    )
    assert result.returncode == 0, result.stderr
    want = tested if expected == "tested" else tip
    assert _git("rev-parse", "refs/remotes/origin/main", cwd=work) == want


def _security_step(name: str) -> dict:
    return next(s for s in load("ci.yml")["jobs"]["security"]["steps"] if s.get("name") == name)


def _fake_tools(bin_dir: Path, pip_audit_body: str) -> None:
    """Stub uv, sleep and pip-audit so the real step script runs offline."""
    bin_dir.mkdir()
    for name, body in {
        "uv": "exit 0",
        "sleep": "exit 0",
        "pip-audit": pip_audit_body,
    }.items():
        tool = bin_dir / name
        tool.write_text(f"#!/bin/bash\n{body}\n")
        tool.chmod(0o755)


REPORT = '{"dependencies": [{"name": "x", "version": "1", "vulns": [{"id": "V", "fix_versions": ["2"]}]}]}'


@pytest.mark.parametrize(
    ("pip_audit_body", "exit_code", "report", "calls"),
    [
        ("exit 0", "0", "false", 1),
        # Findings: exit 1 with a report, never retried.
        (f"echo '{REPORT}' > pip-audit-results.json; exit 1", "1", "true", 1),
        # A crash (connection reset) writes nothing: retried once, still not a pass.
        ("echo ConnectionResetError >&2; exit 1", "1", "false", 2),
        # A crash, then a clean scan.
        ("[ -f crashed ] && exit 0; touch crashed; exit 1", "0", "false", 2),
    ],
    ids=["clean", "findings", "crash-twice", "crash-then-clean"],
)
def test_pip_audit_retries_only_a_run_without_a_report(
    pip_audit_body: str, exit_code: str, report: str, calls: int, tmp_path: Path
) -> None:
    bin_dir = tmp_path / "bin"
    _fake_tools(bin_dir, f"echo call >> calls.log\n{pip_audit_body}")
    output = tmp_path / "github_output"
    result = subprocess.run(
        [BASH, "-e", "-c", _security_step("Run pip-audit (dependency vulnerabilities)")["run"]],
        cwd=tmp_path,
        env={"PATH": f"{bin_dir}:{os.environ['PATH']}", "GITHUB_OUTPUT": str(output)},
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert result.returncode == 0, result.stderr
    outputs = dict(line.split("=", 1) for line in output.read_text().splitlines())
    assert outputs == {"pip_audit_exit": exit_code, "pip_audit_report": report}
    assert len((tmp_path / "calls.log").read_text().splitlines()) == calls


@pytest.mark.parametrize(
    ("pip_exit", "pip_report", "passes", "message"),
    [
        ("0", "false", True, ""),
        ("1", "true", False, "found FIXABLE"),
        ("1", "false", False, "errored twice without producing a report"),
        ("", "", False, "did not run to completion"),
    ],
    ids=["clean", "findings", "tool-error", "never-ran"],
)
def test_security_gate_tells_a_finding_from_a_scan_error(
    pip_exit: str, pip_report: str, passes: bool, message: str, tmp_path: Path
) -> None:
    script = (
        _security_step("Fail on security findings")["run"]
        .replace("${{ steps.pip_audit.outputs.pip_audit_exit }}", pip_exit)
        .replace("${{ steps.pip_audit.outputs.pip_audit_report }}", pip_report)
        .replace("${{ steps.bandit.outputs.bandit_exit }}", "0")
        .replace("${{ steps.semgrep.outputs.semgrep_exit }}", "0")
    )
    assert "${{" not in script, "an expression the test does not substitute"
    result = run_script(script, tmp_path, {})
    assert (result.returncode == 0) is passes, result.stdout + result.stderr
    assert message in result.stdout


# Redis for the service containers comes from this repo's own GHCR copy. ECR
# Public replaced Docker Hub in #1018, then hit its own anonymous data limit
# (2026-10-20, bug-408); #1114 moved to mirror.gcr.io, which is still an
# anonymous public pull. Only the copy job pulls publicly now, and only when
# the copy is missing or on the weekly refresh.
REDIS_MIRROR = "ghcr.io/skyyroseco/devskyy/redis:7-alpine"
REDIS_SOURCES = (
    "mirror.gcr.io/library/redis:7-alpine",
    "public.ecr.aws/docker/library/redis:7-alpine",
    "docker.io/library/redis:7-alpine",
)


def _redis_jobs() -> dict[str, dict]:
    jobs = load("ci.yml")["jobs"]
    return {job_id: job for job_id, job in jobs.items() if "redis" in job.get("services", {})}


def test_redis_services_pull_the_ghcr_copy_with_the_job_token() -> None:
    redis_jobs = _redis_jobs()
    assert set(redis_jobs) == {"python-tests", "api-integration"}, sorted(redis_jobs)
    for job_id, job in redis_jobs.items():
        service = job["services"]["redis"]
        assert service["image"] == REDIS_MIRROR, f"{job_id}: {service['image']}"
        assert service["credentials"] == {
            "username": "${{ github.actor }}",
            "password": "${{ secrets.GITHUB_TOKEN }}",
        }, job_id
        assert job["permissions"] == {"contents": "read", "packages": "read"}, job_id
        assert "ci-images" in job["needs"], f"{job_id}: {job['needs']}"
    # A failed copy must leave Python Tests red, never skip it into a passing
    # required check. API Integration already needs a green Python Tests.
    assert "!cancelled()" in redis_jobs["python-tests"]["if"]
    assert "python-tests" in redis_jobs["api-integration"]["needs"]


def test_ci_images_job_copies_redis_and_reports_to_the_summary() -> None:
    jobs = load("ci.yml")["jobs"]
    job = jobs["ci-images"]
    assert job["permissions"] == {"contents": "read", "packages": "write"}
    assert "needs" not in job, "the copy must not wait on anything"
    env = _ci_images_step()["env"]
    assert env["MIRROR"] == REDIS_MIRROR
    assert tuple(env["SOURCES"].split()) == REDIS_SOURCES
    assert env["REFRESH"] == "${{ github.event_name == 'schedule' }}"
    assert "ci-images" in jobs["summary"]["needs"]


def _ci_images_step() -> dict:
    return step_named(load("ci.yml"), "Ensure the Redis copy exists")


FAKE_DOCKER = """#!/bin/bash
echo "$*" >> "$DOCKER_LOG"
case "$1" in
  login) cat >/dev/null; exit 0 ;;
  manifest) [ "$FAKE_MIRROR_EXISTS" = 1 ] ;;
  pull) [[ " $FAKE_PULLABLE " == *" $2 "* ]] ;;
  tag|push) exit 0 ;;
  *) exit 2 ;;
esac
"""


def _run_ci_images(tmp_path: Path, *, exists: bool, refresh: bool, pullable: str) -> tuple:
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    docker = bin_dir / "docker"
    docker.write_text(FAKE_DOCKER)
    docker.chmod(0o755)
    log = tmp_path / "docker.log"
    log.touch()
    step = _ci_images_step()
    env = {
        **{k: str(v) for k, v in step["env"].items() if "${{" not in str(v)},
        "REFRESH": "true" if refresh else "false",
        "GH_TOKEN": "token",
        "GITHUB_ACTOR": "actor",
        "PATH": f"{bin_dir}:{os.environ['PATH']}",
        "DOCKER_LOG": str(log),
        "FAKE_MIRROR_EXISTS": "1" if exists else "0",
        "FAKE_PULLABLE": pullable,
    }
    assert "${{" not in step["run"], "an expression the test does not substitute"
    result = subprocess.run(
        [BASH, "-e", "-c", step["run"]],
        cwd=tmp_path,
        env=env,
        capture_output=True,
        text=True,
        timeout=60,
    )
    return result, log.read_text().splitlines()


def test_ci_images_leaves_an_existing_copy_alone(tmp_path: Path) -> None:
    result, calls = _run_ci_images(tmp_path, exists=True, refresh=False, pullable="")
    assert result.returncode == 0, result.stdout + result.stderr
    assert not [c for c in calls if c.split()[0] in {"pull", "push"}], calls


def test_ci_images_falls_back_to_the_next_source(tmp_path: Path) -> None:
    result, calls = _run_ci_images(tmp_path, exists=False, refresh=False, pullable=REDIS_SOURCES[1])
    assert result.returncode == 0, result.stdout + result.stderr
    assert [c for c in calls if c.startswith("pull")] == [f"pull {s}" for s in REDIS_SOURCES[:2]]
    assert f"tag {REDIS_SOURCES[1]} {REDIS_MIRROR}" in calls
    assert f"push {REDIS_MIRROR}" in calls


def test_ci_images_refresh_recopies_an_existing_image(tmp_path: Path) -> None:
    result, calls = _run_ci_images(tmp_path, exists=True, refresh=True, pullable=REDIS_SOURCES[0])
    assert result.returncode == 0, result.stdout + result.stderr
    assert f"push {REDIS_MIRROR}" in calls


def test_ci_images_fails_when_no_source_can_be_pulled(tmp_path: Path) -> None:
    result, calls = _run_ci_images(tmp_path, exists=False, refresh=False, pullable="")
    assert result.returncode != 0
    assert not [c for c in calls if c.startswith("push")], calls
    assert "no Redis source could be pulled" in result.stdout
