from __future__ import annotations

import importlib.util
import io
import json
import shutil
import subprocess
import sys
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

import pytest

ROOT = Path(__file__).resolve().parents[1]


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


planning = load_module(
    "adversarial_planning_cli",
    ROOT
    / ".claude"
    / "skills"
    / "adversarial-planning"
    / "scripts"
    / "adversarial_planning_cli.py",
)
syncer = load_module(
    "sync_adversarial_planning_skill",
    ROOT / "scripts" / "sync_adversarial_planning_skill.py",
)


_REAL_DEFAULT_SETTINGS_PATHS = planning.default_claude_settings_paths


def doctor_report(*, terminal_failure: bool = False) -> dict[str, Any]:
    checks = [
        {"id": check_id, "status": "pass"} for check_id in sorted(planning.CRITICAL_DOCTOR_CHECKS)
    ]
    if terminal_failure:
        checks.append(
            {
                "id": "terminal.env",
                "status": "fail",
                "message": "TERM=dumb - colors and cursor control are disabled",
            }
        )
    return {
        "overallStatus": "fail" if terminal_failure else "pass",
        "checks": checks,
    }


def test_claude_fable_alias_readiness_requires_model_alias_documentation():
    assert planning._claude_advertises_fable(
        "Usage: claude [options]\n--model <model> Model session. Provide an alias "
        "for latest model (e.g. 'fable', 'sonnet')."
    )
    assert not planning._claude_advertises_fable(
        "Usage: claude [options]\n--model <model> Choose a model. Examples include fable."
    )


def test_preflight_blocks_when_claude_no_longer_advertises_fable(tmp_path):
    calls = []

    def fake_command(argv, **_kwargs):
        calls.append(argv)
        if argv == ["claude", "--version"]:
            output = "Claude Code test\n"
        elif argv == ["claude", "--help"]:
            output = "--model <model> Select a model.\n"
        else:
            pytest.fail("authentication and providers must not run without fable")
        return subprocess.CompletedProcess(argv, 0, stdout=output, stderr="")

    with pytest.raises(planning.GateBlocked, match="does not advertise the required fable"):
        planning.preflight(
            tmp_path,
            command=fake_command,
            env={"TERM": "dumb", "CODEX_HOME": str(tmp_path / "codex-home")},
            stdin_tty=False,
            stdout_tty=False,
            stderr_tty=False,
        )
    assert calls == [["claude", "--version"], ["claude", "--help"]]


def test_doctor_allows_only_the_noninteractive_dumb_terminal_exception():
    ready, reasons = planning.doctor_is_ready(
        doctor_report(terminal_failure=True),
        term="dumb",
        noninteractive=True,
    )
    assert ready
    assert "terminal.env cosmetic failure ignored" in reasons[0]
    for term, noninteractive in (("xterm-256color", True), ("dumb", False)):
        ready, _ = planning.doctor_is_ready(
            doctor_report(terminal_failure=True),
            term=term,
            noninteractive=noninteractive,
        )
        assert not ready


def test_doctor_accepts_current_object_map_shape_and_redacts_diagnostic_details():
    source = doctor_report(terminal_failure=True)
    source["checks"] = {
        check["id"]: {
            **check,
            "summary": "TERM=dumb - colors and cursor control are disabled",
            "details": {"environment": "/private/user/path"},
        }
        for check in source["checks"]
    }
    ready, _ = planning.doctor_is_ready(
        source,
        term="dumb",
        noninteractive=True,
    )
    assert ready
    safe = planning._doctor_safe_summary(source)
    assert safe["checks"][-1] == {"id": "terminal.env", "status": "fail"}
    assert "/private/user/path" not in json.dumps(safe)


@pytest.mark.parametrize(
    "mutate",
    [
        lambda checks: checks[0].update(status="fail"),
        lambda checks: checks.append({"id": "mystery", "status": "unrecognized"}),
    ],
)
def test_doctor_blocks_real_and_unknown_failures(mutate):
    report = doctor_report()
    mutate(report["checks"])
    ready, reasons = planning.doctor_is_ready(
        report,
        term="dumb",
        noninteractive=True,
    )
    assert not ready
    assert reasons


def test_doctor_blocks_terminal_error_with_non_cosmetic_message():
    report = doctor_report(terminal_failure=True)
    report["checks"][-1]["message"] = "terminal initialization failed unexpectedly"
    assert not planning.doctor_is_ready(
        report,
        term="dumb",
        noninteractive=True,
    )[0]


def test_doctor_rejects_extra_failure_details_and_duplicate_check_ids():
    report = doctor_report(terminal_failure=True)
    report["checks"][-1][
        "summary"
    ] = "TERM=dumb - colors and cursor control are disabled; security runtime validation disabled"
    assert not planning.doctor_is_ready(
        report,
        term="dumb",
        noninteractive=True,
    )[0]

    duplicate = doctor_report()
    duplicate["checks"].append({"id": duplicate["checks"][0]["id"], "status": "pass"})
    assert not planning.doctor_is_ready(
        duplicate,
        term="dumb",
        noninteractive=True,
    )[0]


def test_missing_claude_auth_stops_before_provider_readiness_or_model_calls(tmp_path):
    calls = []

    def fake_command(argv, **_kwargs):
        calls.append(argv)
        if argv == ["claude", "--version"]:
            output = "Claude Code test\\n"
        elif argv == ["claude", "--help"]:
            output = "--model <model> Provide an alias for the latest model (e.g. 'fable')."
        elif argv == ["codex", "--version"]:
            output = "codex-cli test\\n"
        elif argv == ["claude", "auth", "status", "--json"]:
            output = '{"loggedIn": false}'
        else:
            pytest.fail("provider check must not proceed after failed auth")
        return subprocess.CompletedProcess(argv, 0, stdout=output, stderr="")

    with pytest.raises(planning.GateBlocked, match="authentication is not ready"):
        planning.preflight(
            tmp_path,
            command=fake_command,
            env={"TERM": "dumb", "CODEX_HOME": str(tmp_path / "codex-home")},
            stdin_tty=False,
            stdout_tty=False,
            stderr_tty=False,
        )
    assert calls == [
        ["claude", "--version"],
        ["claude", "--help"],
        ["codex", "--version"],
        ["claude", "auth", "status", "--json"],
    ]


def test_live_preflight_schema_and_terminal_exception_are_fail_closed(tmp_path):
    home = tmp_path / "codex-home"
    home.mkdir()
    report = doctor_report(terminal_failure=True)
    report["checks"] = {
        check["id"]: {
            "id": check["id"],
            "status": check["status"],
            "summary": check.get("message", "ok"),
            "details": {"redacted": True},
        }
        for check in report["checks"]
    }

    def fake_command(argv, **_kwargs):
        if argv == ["claude", "--version"]:
            return subprocess.CompletedProcess(argv, 0, stdout="Claude Code test", stderr="")
        if argv == ["claude", "--help"]:
            return subprocess.CompletedProcess(
                argv,
                0,
                stdout="--model <model> Provide an alias for the latest model (e.g. 'fable').",
                stderr="",
            )
        if argv == ["codex", "--version"]:
            return subprocess.CompletedProcess(argv, 0, stdout="codex-cli test", stderr="")
        if argv == ["claude", "auth", "status", "--json"]:
            return subprocess.CompletedProcess(
                argv, 0, stdout='{"loggedIn":true,"authMethod":"claude.ai"}', stderr=""
            )
        if argv == ["codex", "doctor", "--json"]:
            return subprocess.CompletedProcess(argv, 1, stdout=json.dumps(report), stderr="")
        if argv[0] == "git":
            if argv[1:] == ["rev-parse", "--show-toplevel"]:
                output = str(tmp_path)
            elif argv[1:] == ["rev-parse", "--git-common-dir"]:
                output = ".git"
            elif argv[1:] == ["rev-parse", "HEAD"]:
                output = "a" * 40
            elif argv[1:] == ["status", "--porcelain", "-z", "--untracked-files=all"]:
                output = ""
            else:
                pytest.fail("unexpected git identity query")
            return subprocess.CompletedProcess(argv, 0, stdout=output, stderr="")
        raise AssertionError("unexpected readiness command")

    result = planning.preflight(
        tmp_path,
        command=fake_command,
        env={"TERM": "dumb", "CODEX_HOME": str(home)},
        stdin_tty=False,
        stdout_tty=False,
        stderr_tty=False,
    )
    assert result["doctor_notes"] == [
        "terminal.env cosmetic failure ignored for noninteractive TERM=dumb"
    ]
    assert "details" not in json.dumps(result["doctor"])
    assert result["checkout_identity"]["root"] == str(tmp_path)


@pytest.mark.parametrize(
    "environment",
    [
        {"CLAUDE_CODE_USE_BEDROCK": "1"},
        {"ANTHROPIC_BASE_URL": "https://proxy.example.test"},
    ],
)
def test_preflight_blocks_unverified_claude_provider_routes(tmp_path, environment):
    def fake_command(argv, **_kwargs):
        if argv == ["claude", "--version"]:
            return subprocess.CompletedProcess(argv, 0, stdout="Claude Code test", stderr="")
        if argv == ["claude", "--help"]:
            return subprocess.CompletedProcess(
                argv,
                0,
                stdout="--model <model> Provide an alias for the latest model (e.g. 'fable').",
                stderr="",
            )
        if argv == ["codex", "--version"]:
            return subprocess.CompletedProcess(argv, 0, stdout="codex-cli test", stderr="")
        if argv == ["claude", "auth", "status", "--json"]:
            return subprocess.CompletedProcess(
                argv, 0, stdout='{"loggedIn":true,"authMethod":"claude.ai"}', stderr=""
            )
        raise AssertionError("provider mismatch must block before Codex doctor")

    env = {
        **environment,
        "TERM": "dumb",
        "CODEX_HOME": str(tmp_path / "codex-home"),
    }
    with pytest.raises(planning.GateBlocked, match="Claude"):
        planning.preflight(
            tmp_path,
            command=fake_command,
            env=env,
            stdin_tty=False,
            stdout_tty=False,
            stderr_tty=False,
        )


def test_execution_gate_blocks_overlap_but_allows_unrelated_dirty_files(monkeypatch, tmp_path):
    runner = planning.CliRunner(tmp_path)

    def fake_status(path):
        return subprocess.CompletedProcess(
            ["git", "status"],
            0,
            stdout=" M source.json" + chr(0),
            stderr="",
        )

    monkeypatch.setattr(planning, "run_command", lambda argv, **kwargs: fake_status(kwargs["cwd"]))
    with pytest.raises(planning.GateBlocked, match="overlaps existing dirty work"):
        runner.pre_execution_gate(
            {
                "steps": [{"files": ["source.json"]}],
            }
        )
    runner.pre_execution_gate(
        {
            "steps": [{"files": ["new-plan-output.json"]}],
        }
    )
    with pytest.raises(planning.GateBlocked, match="escapes"):
        runner.pre_execution_gate(
            {
                "steps": [{"files": ["../outside.txt"]}],
            }
        )


def test_codex_model_resolution_obeys_trusted_project_then_user_config(tmp_path):
    repo = tmp_path / "repo"
    home = tmp_path / "home"
    (repo / ".codex").mkdir(parents=True)
    (home / ".codex").mkdir(parents=True)
    (repo / ".codex" / "config.toml").write_text(
        'model = "project-model"\nmodel_provider = "openai"\n',
        encoding="utf-8",
    )
    user_path = home / ".codex" / "config.toml"
    user_path.write_text(
        f'model = "user-model"\n[projects.{json.dumps(str(repo.resolve()))}]\n'
        'trust_level = "trusted"\n',
        encoding="utf-8",
    )
    model = planning.resolve_codex_model(
        repo,
        {"CODEX_HOME": str(home / ".codex")},
    )
    assert model.model == "project-model"
    assert model.source == "trusted project config model"
    assert model.provider == "OpenAI Codex CLI"


def test_project_provider_table_cannot_mask_user_openai_endpoint(tmp_path):
    repo = tmp_path / "repo"
    home = tmp_path / "home"
    (repo / ".codex").mkdir(parents=True)
    (home / ".codex").mkdir(parents=True)
    user_path = home / ".codex" / "config.toml"
    user_path.write_text(
        '[model_providers.openai]\nbase_url = "https://unverified.invalid/v1"\n'
        f'[projects.{json.dumps(str(repo.resolve()))}]\ntrust_level = "trusted"\n',
        encoding="utf-8",
    )
    (repo / ".codex" / "config.toml").write_text(
        '[model_providers.unrelated]\nbase_url = "https://example.invalid/v1"\n',
        encoding="utf-8",
    )

    with pytest.raises(planning.GateBlocked, match="unverified endpoint"):
        planning.resolve_codex_model(repo, {"CODEX_HOME": str(home / ".codex")})


def test_codex_openai_base_url_override_is_validated(tmp_path):
    repo = tmp_path / "repo"
    home = tmp_path / "home"
    (home / ".codex").mkdir(parents=True)
    (home / ".codex" / "config.toml").write_text(
        'openai_base_url = "https://unverified.invalid/v1"\n',
        encoding="utf-8",
    )

    with pytest.raises(planning.GateBlocked, match="unverified endpoint"):
        planning.resolve_codex_model(repo, {"CODEX_HOME": str(home / ".codex")})


def test_project_provider_setting_cannot_mask_user_non_openai_provider(tmp_path):
    repo = tmp_path / "repo"
    home = tmp_path / "home"
    (repo / ".codex").mkdir(parents=True)
    (home / ".codex").mkdir(parents=True)
    (home / ".codex" / "config.toml").write_text(
        'model_provider = "anthropic"\n'
        f'[projects.{json.dumps(str(repo.resolve()))}]\ntrust_level = "trusted"\n',
        encoding="utf-8",
    )
    (repo / ".codex" / "config.toml").write_text(
        'model_provider = "openai"\n',
        encoding="utf-8",
    )

    with pytest.raises(planning.GateBlocked, match="not configured for the independent OpenAI"):
        planning.resolve_codex_model(repo, {"CODEX_HOME": str(home / ".codex")})


def test_project_provider_routes_are_ignored_when_user_uses_default_openai(tmp_path):
    repo = tmp_path / "repo"
    home = tmp_path / "home"
    (repo / ".codex").mkdir(parents=True)
    (home / ".codex").mkdir(parents=True)
    (home / ".codex" / "config.toml").write_text(
        f'[projects.{json.dumps(str(repo.resolve()))}]\ntrust_level = "trusted"\n',
        encoding="utf-8",
    )
    (repo / ".codex" / "config.toml").write_text(
        'model_provider = "anthropic"\n'
        'openai_base_url = "https://unverified.invalid/v1"\n'
        "[model_providers.openai]\n"
        'base_url = "https://unverified.invalid/v1"\n',
        encoding="utf-8",
    )
    model = planning.resolve_codex_model(repo, {"CODEX_HOME": str(home / ".codex")})

    assert model.provider == "OpenAI Codex CLI"


def test_untrusted_project_config_is_ignored_and_builtin_is_not_guessed(tmp_path):
    repo = tmp_path / "repo"
    home = tmp_path / "home"
    (repo / ".codex").mkdir(parents=True)
    (home / ".codex").mkdir(parents=True)
    (repo / ".codex" / "config.toml").write_text('model = "untrusted-model"\n')
    (home / ".codex" / "config.toml").write_text('model = "user-model"\n')
    model = planning.resolve_codex_model(
        repo,
        {"CODEX_HOME": str(home / ".codex")},
    )
    assert model.model == "user-model"
    assert model.source == "user config model"
    (home / ".codex" / "config.toml").write_text('model_provider = "anthropic"\n')
    with pytest.raises(planning.GateBlocked, match="not configured for the independent OpenAI"):
        planning.resolve_codex_model(repo, {"CODEX_HOME": str(home / ".codex")})
    (home / ".codex" / "config.toml").write_text("")
    model = planning.resolve_codex_model(repo, {"CODEX_HOME": str(home / ".codex")})
    assert model.model == "resolved by Codex CLI at invocation"


def test_codex_profile_declaration_is_not_passed_as_a_cli_override(tmp_path):
    repo = tmp_path / "repo"
    home = tmp_path / "home"
    (home / ".codex").mkdir(parents=True)
    (home / ".codex" / "config.toml").write_text(
        'profile = "review"\nmodel = "user-model"\n'
        '[profiles.review]\nmodel = "profile-model"\nmodel_provider = "openai"\n',
        encoding="utf-8",
    )
    model = planning.resolve_codex_model(
        repo,
        {"CODEX_HOME": str(home / ".codex")},
    )
    assert model.model == "user-model"
    assert model.source == "user config model"
    assert model.profile is None


def test_manifest_is_mode_bound_and_requires_fresh_hash_bound_y():
    now = datetime(2026, 10, 4, tzinfo=UTC)
    preflight = {
        "claude_version": "Claude Code test",
        "claude_auth": {"logged_in": True, "method": "test", "scope": "CLI status"},
        "codex_version": "Codex test",
        "codex_model": {
            "name": "resolved by Codex CLI at invocation",
            "source": "Codex CLI effective configuration (runtime-resolved)",
            "provider": "OpenAI Codex CLI",
            "profile": None,
        },
        "checkout_identity": {
            "root": "/repo",
            "git_common_dir_sha256": "a" * 64,
            "head": "b" * 40,
            "status_sha256": "c" * 64,
        },
        "doctor": {"overall_status": "pass", "checks": []},
        "doctor_notes": [],
        "doctor_environment": {"term": "xterm-256color", "noninteractive": False},
    }
    task = "Review an offline fixture."
    manifest = planning.prepare_manifest(task, "plan_only", "local_cli", preflight, now=now)
    assert manifest["debate"]["max_rounds"] == 3
    assert manifest["debate"]["max_calls"] == 6
    assert manifest["cost_estimate"] == "unknown"
    assert manifest["quota_estimate"] == "unknown"
    planning.validate_approval(
        manifest,
        task=task,
        typed_y="y",
        approved_manifest_sha256=manifest["manifest_sha256"],
        current_preflight=preflight,
        now=now + timedelta(minutes=1),
    )
    for approval, approval_hash, changed_task, current in (
        ("Y", manifest["manifest_sha256"], task, preflight),
        ("y", "wrong-hash", task, preflight),
        ("y", manifest["manifest_sha256"], task + " changed", preflight),
        ("y", manifest["manifest_sha256"], task, {**preflight, "codex_version": "changed"}),
        (
            "y",
            manifest["manifest_sha256"],
            task,
            {
                **preflight,
                "checkout_identity": {**preflight["checkout_identity"], "head": "d" * 40},
            },
        ),
    ):
        with pytest.raises(planning.GateBlocked):
            planning.validate_approval(
                manifest,
                task=changed_task,
                typed_y=approval,
                approved_manifest_sha256=approval_hash,
                current_preflight=current,
                now=now + timedelta(minutes=1),
            )
    with pytest.raises(planning.GateBlocked, match="expired"):
        planning.validate_approval(
            manifest,
            task=task,
            typed_y="y",
            approved_manifest_sha256=manifest["manifest_sha256"],
            current_preflight=preflight,
            now=now + timedelta(minutes=11),
        )
    execute = planning.prepare_manifest(task, "plan_and_execute", "local_cli", preflight, now=now)
    assert execute["debate"]["max_calls"] == 8
    with pytest.raises(planning.GateBlocked, match="Workflow execution is unavailable"):
        planning.prepare_manifest(task, "plan_and_execute", "workflow", preflight, now=now)


@pytest.mark.parametrize("record", [None, []])
@pytest.mark.parametrize("provider_key", ["claude", "codex"])
def test_malformed_manifest_provider_records_block_cleanly(record, provider_key):
    now = datetime(2026, 10, 4, tzinfo=UTC)
    preflight = {
        "claude_version": "Claude Code test",
        "claude_auth": {"logged_in": True, "method": "test", "scope": "CLI status"},
        "codex_version": "Codex test",
        "codex_model": {
            "name": "resolved by Codex CLI at invocation",
            "source": "Codex CLI effective configuration (runtime-resolved)",
            "provider": "OpenAI Codex CLI",
            "profile": None,
        },
        "checkout_identity": {
            "root": "/repo",
            "git_common_dir_sha256": "a" * 64,
            "head": "b" * 40,
            "status_sha256": "c" * 64,
        },
        "doctor": {"overall_status": "pass", "checks": []},
        "doctor_notes": [],
        "doctor_environment": {"term": "xterm-256color", "noninteractive": False},
    }
    task = "Review an offline fixture."
    manifest = planning.prepare_manifest(task, "plan_only", "local_cli", preflight, now=now)
    manifest[provider_key] = record

    with pytest.raises(planning.GateBlocked, match="provider records are malformed"):
        planning.validate_approval(
            manifest,
            task=task,
            typed_y="y",
            approved_manifest_sha256=manifest["manifest_sha256"],
            current_preflight=preflight,
            now=now + timedelta(minutes=1),
        )


class FakeRunner:
    def __init__(self, challenges=None, actions=None, plan_flags=None):
        self.plan_flags = {
            "requires_image_generation": False,
            "requires_publish_or_deploy": False,
            **(plan_flags or {}),
        }
        self.challenges = challenges or [
            {"satisfied": True, "blocking_objections": [], "specific_challenge": ""}
        ]
        self.actions = actions or ["Check source facts and prepare an offline remediation plan."]
        self.rounds = 0
        self.executions = 0
        self.gates = 0
        self.reviews = 0
        self.tasks: list[str] = []

    def plan(self, task, prior, transcript):
        self.tasks.append(task)
        action = self.actions[min(self.rounds, len(self.actions) - 1)]
        return {
            "summary": "Evidence-bound plan",
            "steps": [
                {"action": action, "files": ["source.json"], "verify": "Compare exact source hash."}
            ],
            "risks": [],
            "blocking_unknowns": [],
            **self.plan_flags,
        }

    def challenge(self, task, plan, round_number, transcript):
        self.rounds += 1
        challenge = self.challenges[min(round_number - 1, len(self.challenges) - 1)]
        return {
            **challenge,
            "codex_verbatim": json.dumps(challenge, sort_keys=True),
        }

    def pre_execution_gate(self, plan):
        self.gates += 1

    def execute(self, task, plan):
        self.executions += 1
        return {
            "summary": "Completed as planned.",
            "changed_paths": [],
            "checks": ["PASS"],
            "blockers": [],
            "codex_verbatim": (
                '{"summary":"Completed as planned.","changed_paths":[],"checks":["PASS"],"blockers":[]}'
            ),
        }

    def review(self, task, plan, execution):
        self.reviews += 1
        return {"ship": True, "deviations": [], "summary": "Execution evidence matches plan."}


def test_plan_only_never_executes_even_after_convergence():
    runner = FakeRunner()
    result = planning.run_debate("A bounded task.", "plan_only", runner)
    assert result["status"] == "PLAN_READY"
    assert runner.executions == runner.reviews == 0


def test_unresolved_debate_stops_at_three_and_never_executes():
    objection = {
        "satisfied": False,
        "blocking_objections": ["Source evidence is missing."],
        "specific_challenge": "Provide source.",
    }
    runner = FakeRunner(challenges=[objection])
    result = planning.run_debate("A task with a blocking gap.", "plan_and_execute", runner)
    assert result["status"] == "NEEDS_REVIEW"
    assert result["rounds"] == 3
    assert runner.executions == 0


def test_plan_blocking_unknowns_prevent_convergence_even_if_challenger_says_yes():
    runner = FakeRunner()

    def unresolved_plan(_task, _prior, _transcript):
        return {
            "summary": "Plan has an unresolved source gap.",
            "steps": [
                {"action": "Check source.", "files": ["source.json"], "verify": "Compare hashes."}
            ],
            "risks": [],
            "blocking_unknowns": ["The source owner is not identified."],
            "requires_image_generation": False,
            "requires_publish_or_deploy": False,
        }

    runner.plan = unresolved_plan
    result = planning.run_debate("A task with a source gap.", "plan_and_execute", runner)
    assert result["status"] == "NEEDS_REVIEW"
    assert result["rounds"] == 3
    assert runner.executions == 0


def test_plan_and_execute_reviews_actual_execution_result():
    runner = FakeRunner()
    result = planning.run_debate("A bounded task.", "plan_and_execute", runner)
    assert result["status"] == "EXECUTION_COMPLETE"
    assert runner.executions == runner.reviews == 1


def test_execution_review_with_deviations_cannot_return_complete():
    runner = FakeRunner()
    runner.review = lambda _task, _plan, _execution: {
        "ship": True,
        "deviations": ["An unplanned file changed."],
        "summary": "Needs a human decision.",
    }
    result = planning.run_debate("A bounded task.", "plan_and_execute", runner)
    assert result["status"] == "NEEDS_REVIEW"


def test_generation_and_publishing_need_separate_typed_approvals():
    runner = FakeRunner(actions=["Generate images and deploy the approved set."])
    result = planning.run_debate("A creative task.", "plan_and_execute", runner)
    assert result["status"] == "NEEDS_REVIEW"
    assert runner.executions == 0
    result = planning.run_debate(
        "A creative task.",
        "plan_and_execute",
        FakeRunner(actions=["Generate images and deploy the approved set."]),
        gate_approver=lambda name, _plan: "y" if name == "image generation" else "",
    )
    assert result["status"] == "NEEDS_REVIEW"
    assert "publishing/deployment" in result["reason"]
    result = planning.run_debate(
        "A creative task.",
        "plan_and_execute",
        FakeRunner(actions=["Generate images and deploy the approved set."]),
        gate_approver=lambda _name, _plan: "y",
    )
    assert result["status"] == "EXECUTION_COMPLETE"


def test_reviewing_existing_imagery_does_not_request_generation_or_publish_approval():
    runner = FakeRunner(actions=["Review existing imagery and map it to its registered source."])
    result = planning.run_debate("Reconcile the media inventory.", "plan_and_execute", runner)
    assert result["status"] == "EXECUTION_COMPLETE"
    assert runner.executions == 1


def test_local_runner_uses_fable_and_never_sets_a_codex_model(monkeypatch, tmp_path):
    captured = []

    def fake_run(argv, *, cwd, input_text=None, env=None):
        captured.append((argv, input_text))
        if argv[0] == "claude":
            return subprocess.CompletedProcess(
                argv, 0, stdout='{"structured_output": {"summary":"ok"}}', stderr=""
            )
        output = Path(argv[argv.index("--output-last-message") + 1])
        output.write_text('{"satisfied":true,"blocking_objections":[],"specific_challenge":""}')
        return subprocess.CompletedProcess(argv, 0, stdout="{}", stderr="")

    monkeypatch.setattr(planning, "run_command", fake_run)
    runner = planning.CliRunner(tmp_path)
    runner._claude(
        "prompt",
        {"type": "object", "required": ["summary"], "properties": {"summary": {"type": "string"}}},
    )
    runner._codex("prompt", planning.CHALLENGE_SCHEMA, "read-only")
    claude_argv, claude_input = captured[0]
    codex_argv, codex_input = captured[1]
    assert claude_argv[claude_argv.index("--model") + 1] == "fable"
    assert "--fallback-model" not in claude_argv
    assert codex_argv[0:2] == ["codex", "exec"]
    assert "--model" not in codex_argv
    assert "--profile" not in codex_argv
    assert codex_argv[codex_argv.index("--sandbox") + 1] == "read-only"
    assert claude_input == codex_input == "prompt"


@pytest.fixture(autouse=True)
def _no_ambient_claude_settings(monkeypatch):
    """Preflight must never read the developer's real Claude settings in tests."""
    monkeypatch.setattr(planning, "default_claude_settings_paths", lambda _repo, _env: [])


@pytest.fixture(autouse=True)
def _isolated_ledger_dir(monkeypatch, tmp_path):
    """No test may write a single-use claim into the real per-user ledger."""
    monkeypatch.setattr(planning, "default_ledger_dir", lambda: tmp_path / "ledger-state")


def _prepared_run(
    monkeypatch,
    tmp_path,
    plan_action="Inspect source.txt without changing repository facts.",
    plan_flags=None,
    on_execute=None,
):
    """Prepare a real manifest in a throwaway repo with every provider call stubbed."""
    repo = tmp_path / "repo"
    repo.mkdir()
    subprocess.run(["git", "init", "-q"], cwd=repo, check=True, shell=False)
    subprocess.run(
        ["git", "config", "user.email", "test@example.invalid"],
        cwd=repo,
        check=True,
        shell=False,
    )
    subprocess.run(
        ["git", "config", "user.name", "Adversarial Planning Test"],
        cwd=repo,
        check=True,
        shell=False,
    )
    (repo / "source.txt").write_text("source fixture\n", encoding="utf-8")
    subprocess.run(["git", "add", "source.txt"], cwd=repo, check=True, shell=False)
    subprocess.run(
        ["git", "commit", "-q", "-m", "initial fixture"],
        cwd=repo,
        check=True,
        shell=False,
    )
    identity = planning.checkout_identity(repo)
    preflight = {
        "claude_version": "Claude Code test",
        "claude_auth": {"logged_in": True, "method": "claude.ai", "scope": "CLI status"},
        "codex_version": "Codex test",
        "codex_model": {
            "name": "resolved by Codex CLI at invocation",
            "source": "Codex CLI effective configuration (runtime-resolved)",
            "provider": "OpenAI Codex CLI",
            "profile": None,
        },
        "doctor": {
            "overall_status": "pass",
            "checks": [
                {"id": check_id, "status": "ok"}
                for check_id in sorted(planning.CRITICAL_DOCTOR_CHECKS)
            ],
        },
        "doctor_notes": [],
        "doctor_environment": {"term": "dumb", "noninteractive": True},
        "checkout_identity": identity,
    }
    monkeypatch.setattr(planning, "preflight", lambda _repo: preflight)
    task_file = tmp_path / "task.md"
    task_file.write_text("Inspect source.txt and make a scoped plan.\n", encoding="utf-8")
    manifest_path = tmp_path / "run" / "manifest.json"
    assert (
        planning.main(
            [
                "prepare",
                "--task-file",
                str(task_file),
                "--manifest",
                str(manifest_path),
                "--mode",
                "plan_and_execute",
                "--repo",
                str(repo),
            ]
        )
        == 0
    )
    raw_manifest = manifest_path.read_text(encoding="utf-8")
    assert raw_manifest.endswith("\n")
    assert not raw_manifest.endswith("\\n")
    manifest = json.loads(raw_manifest)

    plan = {
        "summary": "Inspect the tracked fixture source.",
        "steps": [
            {
                "action": plan_action,
                "files": ["source.txt"],
                "verify": "Read the committed source fixture.",
            }
        ],
        "risks": [],
        "blocking_unknowns": [],
        "requires_image_generation": False,
        "requires_publish_or_deploy": False,
        **(plan_flags or {}),
    }
    challenge = {
        "satisfied": True,
        "blocking_objections": [],
        "specific_challenge": "No blocking objection.",
    }
    execution = {
        "summary": "Inspected source.txt.",
        "changed_paths": [],
        "checks": ["source.txt read"],
        "blockers": [],
    }
    review = {"ship": True, "deviations": [], "summary": "Output matches the bounded plan."}
    provider_calls = []

    def fake_run(argv, *, cwd, input_text=None, env=None):
        if argv[0] == "git":
            return subprocess.run(
                argv,
                cwd=cwd,
                input=input_text,
                text=True,
                capture_output=True,
                check=False,
                shell=False,
                env=env,
            )
        provider_calls.append((argv, input_text))
        if argv[0] == "claude":
            response = (
                review
                if input_text and "Review the actual execution report" in input_text
                else plan
            )
            return subprocess.CompletedProcess(
                argv, 0, stdout=json.dumps({"structured_output": response}), stderr=""
            )
        output_path = Path(argv[argv.index("--output-last-message") + 1])
        read_only = argv[argv.index("--sandbox") + 1] == "read-only"
        if not read_only and on_execute is not None:
            on_execute(repo)
        response = challenge if read_only else execution
        output_path.write_text(json.dumps(response), encoding="utf-8")
        return subprocess.CompletedProcess(argv, 0, stdout="{}", stderr="")

    monkeypatch.setattr(planning, "run_command", fake_run)
    return repo, task_file, manifest_path, manifest, provider_calls


def _run_argv(repo, task_file, manifest_path):
    return [
        "run",
        "--task-file",
        str(task_file),
        "--manifest",
        str(manifest_path),
        "--repo",
        str(repo),
    ]


def test_main_round_trips_manifest_and_runs_cli_contract_with_real_newlines(
    monkeypatch, tmp_path, capsys
):
    repo, task_file, manifest_path, manifest, provider_calls = _prepared_run(monkeypatch, tmp_path)
    answers = iter(["y", manifest["manifest_sha256"]])
    monkeypatch.setattr("builtins.input", lambda _prompt: next(answers))
    assert planning.main(_run_argv(repo, task_file, manifest_path), stdin_tty=True) == 0
    assert "EXECUTION_COMPLETE" in capsys.readouterr().out
    assert len(provider_calls) == 4
    assert all("--model" not in argv for argv, _ in provider_calls if argv[0] == "codex")
    assert all("--profile" not in argv for argv, _ in provider_calls if argv[0] == "codex")
    first_claude_prompt = next(prompt for argv, prompt in provider_calls if argv[0] == "claude")
    assert "TASK:\n" in first_claude_prompt
    assert "TASK:\\n" not in first_claude_prompt


def test_piped_stdin_cannot_self_approve_and_no_provider_is_called(monkeypatch, tmp_path, capsys):
    repo, task_file, manifest_path, manifest, provider_calls = _prepared_run(monkeypatch, tmp_path)
    answers = iter(["y", manifest["manifest_sha256"]])
    monkeypatch.setattr("builtins.input", lambda _prompt: next(answers))
    assert planning.main(_run_argv(repo, task_file, manifest_path), stdin_tty=False) == 2
    assert "interactive terminal" in capsys.readouterr().err
    assert provider_calls == []
    assert not Path(f"{manifest_path}.consumed").exists()


def test_stdin_tty_defaults_to_the_real_stdin(monkeypatch, tmp_path):
    repo, task_file, manifest_path, _manifest, provider_calls = _prepared_run(monkeypatch, tmp_path)
    monkeypatch.setattr(planning.sys, "stdin", io.StringIO("y\n"))
    assert planning.main(_run_argv(repo, task_file, manifest_path)) == 2
    assert provider_calls == []


def test_separate_plan_gate_refuses_non_interactive_stdin(monkeypatch, tmp_path, capsys):
    repo, task_file, manifest_path, manifest, provider_calls = _prepared_run(
        monkeypatch, tmp_path, plan_action="Generate images for the source fixture."
    )
    answers = iter(["y", manifest["manifest_sha256"]])
    monkeypatch.setattr("builtins.input", lambda _prompt: next(answers))
    ttys = iter([True, False])

    def tty_only_for_the_manifest_prompt(stdin_tty=None):
        if not next(ttys):
            raise planning.GateBlocked("approval must be typed on an interactive terminal")

    monkeypatch.setattr(planning, "require_interactive_terminal", tty_only_for_the_manifest_prompt)
    assert planning.main(_run_argv(repo, task_file, manifest_path), stdin_tty=True) == 2
    assert "interactive terminal" in capsys.readouterr().err
    executions = [argv for argv, _ in provider_calls if "workspace-write" in argv]
    assert executions == []
    assert len(provider_calls) == 2


def test_approved_manifest_is_one_time_and_the_claim_survives_failure(
    monkeypatch, tmp_path, capsys
):
    repo, task_file, manifest_path, manifest, provider_calls = _prepared_run(monkeypatch, tmp_path)
    answers = iter(["y", manifest["manifest_sha256"]] * 2)
    monkeypatch.setattr("builtins.input", lambda _prompt: next(answers))
    original_gate = planning.CliRunner.pre_execution_gate

    def fail_after_claim(self, plan):
        raise planning.GateBlocked("checkout changed")

    monkeypatch.setattr(planning.CliRunner, "pre_execution_gate", fail_after_claim)
    assert planning.main(_run_argv(repo, task_file, manifest_path), stdin_tty=True) == 2
    ledger = Path(f"{manifest_path.resolve()}.consumed")
    claim = json.loads(ledger.read_text(encoding="utf-8"))
    assert claim["manifest_sha256"] == manifest["manifest_sha256"]
    assert datetime.fromisoformat(claim["consumed_at"]).tzinfo is not None
    assert (ledger.stat().st_mode & 0o777) == 0o600
    calls_after_first = len(provider_calls)
    monkeypatch.setattr(planning.CliRunner, "pre_execution_gate", original_gate)
    capsys.readouterr()
    assert planning.main(_run_argv(repo, task_file, manifest_path), stdin_tty=True) == 2
    assert "manifest already consumed" in capsys.readouterr().err
    assert len(provider_calls) == calls_after_first


def test_consume_manifest_is_an_atomic_exclusive_create(tmp_path):
    manifest_path = tmp_path / "manifest.json"
    ledger = planning.consume_manifest(manifest_path, "a" * 64)
    assert ledger == Path(f"{manifest_path.resolve()}.consumed")
    with pytest.raises(planning.GateBlocked, match="already consumed"):
        planning.consume_manifest(manifest_path, "a" * 64)


def test_prepare_refuses_a_path_whose_approval_was_consumed(monkeypatch, tmp_path, capsys):
    repo, task_file, manifest_path, _manifest, _calls = _prepared_run(monkeypatch, tmp_path)
    planning.consume_manifest(manifest_path, "a" * 64)
    capsys.readouterr()
    argv = ["prepare", "--task-file", str(task_file), "--manifest", str(manifest_path)]
    assert planning.main([*argv, "--repo", str(repo)]) == 2
    assert "choose a new --manifest path" in capsys.readouterr().err


def test_runner_without_the_execution_gate_is_rejected_before_any_call():
    class GatelessRunner:
        calls = 0

        def plan(self, task, prior, transcript):
            self.calls += 1

        challenge = execute = review = plan

    runner = GatelessRunner()
    with pytest.raises(planning.GateBlocked, match="execution gate"):
        planning.run_debate("A bounded task.", "plan_and_execute", runner)
    assert runner.calls == 0


def test_codex_execution_blockers_override_positive_review():
    runner = FakeRunner()
    runner.execute = lambda _task, _plan: {
        "summary": "Not completed.",
        "changed_paths": [],
        "checks": ["BLOCKED"],
        "blockers": ["Required source is missing."],
        "codex_verbatim": (
            '{"summary":"Not completed.","changed_paths":[],"checks":["BLOCKED"],'
            '"blockers":["Required source is missing."]}'
        ),
    }
    runner.review = lambda _task, _plan, _execution: {
        "ship": True,
        "deviations": [],
        "summary": "Mock review incorrectly approved.",
    }
    result = planning.run_debate("A bounded task.", "plan_and_execute", runner)
    assert result["status"] == "NEEDS_REVIEW"
    assert result["execution"]["blockers"] == ["Required source is missing."]


def test_command_wrapper_never_uses_shell_and_passes_prompt_via_stdin(monkeypatch, tmp_path):
    captured = {}

    def fake_subprocess_run(argv, **kwargs):
        captured["argv"] = argv
        captured.update(kwargs)
        return subprocess.CompletedProcess(argv, 0, stdout="", stderr="")

    monkeypatch.setattr(planning.subprocess, "run", fake_subprocess_run)
    planning.run_command(["codex", "exec", "-"], cwd=tmp_path, input_text="plan text")
    assert captured["shell"] is False
    assert captured["input"] == "plan text"
    assert captured["argv"] == ["codex", "exec", "-"]


def test_r5_mocked_plan_preserves_all_37_gates_and_love_hurts_artwork_source():
    fixture_path = ROOT / "tests" / "fixtures" / "adversarial_planning" / "r5_reconciliation.json"
    fixture = json.loads(fixture_path.read_text(encoding="utf-8"))
    assert fixture["required_roles"] == 81
    assert fixture["covered_roles"] == 44
    assert fixture["gated_roles"] == sum(fixture["gated_by_role"].values()) == 37
    assert fixture["love_hurts_gated_skus"] == ["lh-002", "lh-005"]
    assert {"lh-002", "lh-005"} <= set(fixture["gated_bindings"]["card_front"])
    assert {"lh-002", "lh-005"} <= set(fixture["gated_bindings"]["pdp_on_model_front"])
    assert (
        fixture["founder_artwork_source"]["artwork_sha256"]
        == "a9b96c60811a92b34dd8b5700317603a16f0976ea863c5d255a4762935d363a8"
    )
    task = (
        "Using only the R5 reconciliation snapshot and the canonical product registry, prepare a source-bound "
        "remediation plan for all 37 gated roles. Resolve LH-002 and LH-005 against founder-approved artwork "
        "before selecting imagery. Do not generate imagery, call a provider, or publish."
    )
    plan = {
        "summary": "Map every held role to its source and a falsifiable review step.",
        "steps": [
            {
                "action": "Read founder-approved artwork through get_product for lh-002 and lh-005 before selecting sources; use "
                + fixture["founder_artwork_source"]["artwork_path"],
                "files": ["wordpress-theme/skyyrose-flagship/data/logo-registry.json"],
                "verify": "Both product records resolve the founder artwork source hash from the R1 adoption evidence.",
            },
            {
                "action": "Retain all 37 R5 gated role bindings in a remediation checklist.",
                "files": [fixture_path.as_posix()],
                "verify": "Role counts sum to 37 and include both Love Hurts SKUs.",
            },
        ],
        "risks": ["Local role reconciliation is not media approval."],
        "blocking_unknowns": [],
        "requires_image_generation": False,
        "requires_publish_or_deploy": False,
    }
    runner = FakeRunner()
    runner.plan = lambda _task, _prior, _transcript: plan
    result = planning.run_debate(task, "plan_only", runner)
    evidence = json.dumps(result)
    assert result["status"] == "PLAN_READY"
    assert "lh-002" in evidence and "lh-005" in evidence
    assert fixture["founder_artwork_source"]["artwork_path"] in evidence
    assert runner.executions == 0
    assert fixture["external_actions"] == {
        "provider_calls": 0,
        "media_generation": False,
        "staging_deployment": False,
        "acceptance": False,
    }


def test_workflow_adapter_blocks_before_any_agent_call():
    node = shutil.which("node")
    if not node:
        pytest.skip("Node is unavailable for the Workflow fail-closed test")
    harness = ROOT / "tests" / "fixtures" / "adversarial_planning" / "workflow-harness.mjs"
    workflow_file = (
        ROOT
        / ".claude"
        / "skills"
        / "adversarial-planning"
        / "scripts"
        / "adversarial-planning.wf.js"
    )
    payload = {
        "workflowPath": workflow_file.as_posix(),
        "args": {"task": "Make a plan.", "mode": "plan_and_execute"},
        "debate": [],
    }
    try:
        subprocess.run([node, "--version"], capture_output=True, check=True, timeout=15)
    except (OSError, subprocess.SubprocessError) as exc:
        pytest.skip(f"Node is installed but cannot execute here: {type(exc).__name__}")
    result = subprocess.run(
        [node, harness.as_posix()],
        input=json.dumps(payload),
        text=True,
        capture_output=True,
        check=False,
        shell=False,
        cwd=ROOT,
        timeout=15,
    )
    assert result.returncode == 0, result.stderr
    output = json.loads(result.stdout)
    assert output["result"]["status"] == "BLOCKED"
    assert "durable atomic one-time execution ledger" in output["result"]["reason"]
    assert output["calls"] == []


def _copy_tree(source: Path, target: Path):
    if source.exists():
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(source, target)


def test_skill_sync_detects_drift_and_requires_explicit_replace_and_prune(tmp_path):
    repo = tmp_path / "repo"
    home = tmp_path / "home"
    canonical = repo / syncer.CANONICAL_RELATIVE
    canonical.mkdir(parents=True)
    (canonical / "SKILL.md").write_text("canonical\n", encoding="utf-8")
    (canonical / "scripts").mkdir()
    (canonical / "scripts" / "runner.js").write_text("canonical runner\n", encoding="utf-8")
    for mirror in (
        repo / syncer.TRACKED_MIRRORS[0],
        repo / syncer.PROJECT_ACTIVE_MIRROR,
        home / syncer.HOME_ACTIVE_MIRROR,
    ):
        _copy_tree(canonical, mirror)
    source_cache = canonical / "scripts" / "__pycache__" / "runner.cpython-314.pyc"
    source_cache.parent.mkdir(parents=True)
    source_cache.write_bytes(b"canonical bytecode is not a mirror input")
    home_mirror = home / syncer.HOME_ACTIVE_MIRROR
    (home_mirror / "SKILL.md").write_text("divergent\n", encoding="utf-8")
    (home_mirror / "obsolete.md").write_text("review before pruning\n", encoding="utf-8")
    mirror_cache = home_mirror / "scripts" / "__pycache__" / "runner.cpython-314.pyc"
    mirror_cache.parent.mkdir(parents=True)
    mirror_cache.write_bytes(b"preserve mirror-local bytecode")
    assert any("divergent" in error for error in syncer.check_mirrors(repo, home))
    with pytest.raises(syncer.SyncError, match="review/merge"):
        syncer.sync_mirrors(repo, home)
    with pytest.raises(syncer.SyncError, match="target-only"):
        syncer.sync_mirrors(repo, home, replace_divergent=True)
    syncer.sync_mirrors(repo, home, replace_divergent=True, prune=True)
    assert syncer.check_mirrors(repo, home) == []
    assert not (home_mirror / "obsolete.md").exists()
    assert mirror_cache.read_bytes() == b"preserve mirror-local bytecode"


def test_skill_sync_preflights_all_targets_before_replacing_any(tmp_path):
    repo = tmp_path / "repo"
    home = tmp_path / "home"
    canonical = repo / syncer.CANONICAL_RELATIVE
    canonical.mkdir(parents=True)
    (canonical / "SKILL.md").write_text("canonical\n", encoding="utf-8")
    tracked = repo / syncer.TRACKED_MIRRORS[0]
    project = repo / syncer.PROJECT_ACTIVE_MIRROR
    tracked.mkdir(parents=True)
    project.mkdir(parents=True)
    (tracked / "SKILL.md").write_text("tracked stale\n", encoding="utf-8")
    (project / "SKILL.md").write_text("project stale\n", encoding="utf-8")
    (project / "extra.md").write_text("must be reviewed\n", encoding="utf-8")

    with pytest.raises(syncer.SyncError, match="target-only"):
        syncer.sync_mirrors(repo, home, replace_divergent=True, prune=False)
    assert (tracked / "SKILL.md").read_text(encoding="utf-8") == "tracked stale\n"


def test_skill_sync_rolls_back_all_targets_if_a_later_swap_fails(tmp_path, monkeypatch):
    repo = tmp_path / "repo"
    home = tmp_path / "home"
    canonical = repo / syncer.CANONICAL_RELATIVE
    canonical.mkdir(parents=True)
    (canonical / "SKILL.md").write_text("canonical\n", encoding="utf-8")
    tracked = repo / syncer.TRACKED_MIRRORS[0]
    project = repo / syncer.PROJECT_ACTIVE_MIRROR
    for target, content in ((tracked, "tracked stale\n"), (project, "project stale\n")):
        target.mkdir(parents=True)
        (target / "SKILL.md").write_text(content, encoding="utf-8")
    original_rename = Path.rename

    def fail_second_install(self, target):
        target_path = Path(target)
        if ".stage-" in self.name and target_path == project:
            raise OSError("fixture rename failure")
        return original_rename(self, target)

    monkeypatch.setattr(Path, "rename", fail_second_install)
    with pytest.raises(syncer.SyncError, match="rolled back"):
        syncer.sync_mirrors(repo, home, replace_divergent=True)
    assert (tracked / "SKILL.md").read_text(encoding="utf-8") == "tracked stale\n"
    assert (project / "SKILL.md").read_text(encoding="utf-8") == "project stale\n"
    assert not list(repo.rglob("*.stage-*"))
    assert not list(repo.rglob("*.backup-*"))


def test_skill_sync_cleans_partial_staging_copy_failure(tmp_path, monkeypatch):
    repo = tmp_path / "repo"
    canonical = repo / syncer.CANONICAL_RELATIVE
    canonical.mkdir(parents=True)
    (canonical / "SKILL.md").write_text("canonical\n", encoding="utf-8")
    targets = [repo / path for path in syncer.TRACKED_MIRRORS]
    targets.append(repo / syncer.PROJECT_ACTIVE_MIRROR)
    for index, target in enumerate(targets):
        target.mkdir(parents=True)
        (target / "SKILL.md").write_text(f"stale {index}\n", encoding="utf-8")

    original_copytree = shutil.copytree
    call_count = 0

    def fail_after_second_copy(source, destination, **kwargs):
        nonlocal call_count
        call_count += 1
        original_copytree(source, destination, **kwargs)
        if call_count == 2:
            raise OSError("fixture staging copy failure")

    monkeypatch.setattr(syncer.shutil, "copytree", fail_after_second_copy)
    with pytest.raises(syncer.SyncError, match="rolled back"):
        syncer.sync_mirrors(repo, tmp_path / "home", replace_divergent=True)

    for index, target in enumerate(targets):
        assert (target / "SKILL.md").read_text(encoding="utf-8") == f"stale {index}\n"
    assert not list(repo.rglob("*.stage-*"))
    assert not list(repo.rglob("*.backup-*"))


def test_skill_sync_check_treats_the_gitignored_project_mirror_as_optional(tmp_path):
    repo = tmp_path / "repo"
    home = tmp_path / "home"
    canonical = repo / syncer.CANONICAL_RELATIVE
    canonical.mkdir(parents=True)
    (canonical / "SKILL.md").write_text("canonical\n", encoding="utf-8")
    _copy_tree(canonical, repo / syncer.TRACKED_MIRRORS[0])
    # Fresh clone: the tracked mirror matches and .agents does not exist.
    assert syncer.check_mirrors(repo, home) == []
    # The tracked mirror stays required.
    shutil.rmtree(repo / syncer.TRACKED_MIRRORS[0])
    assert any("required distribution is missing" in e for e in syncer.check_mirrors(repo, home))
    _copy_tree(canonical, repo / syncer.TRACKED_MIRRORS[0])
    # When the project mirror is present it is still compared.
    project = repo / syncer.PROJECT_ACTIVE_MIRROR
    _copy_tree(canonical, project)
    assert syncer.check_mirrors(repo, home) == []
    (project / "SKILL.md").write_text("drifted\n", encoding="utf-8")
    assert any("divergent files" in e for e in syncer.check_mirrors(repo, home))


def test_tty_presence_is_not_bound_into_the_readiness_digest(monkeypatch, tmp_path, capsys):
    repo, task_file, manifest_path, manifest, provider_calls = _prepared_run(monkeypatch, tmp_path)
    prepared = planning.preflight(repo)
    assert prepared["doctor_environment"]["noninteractive"] is True
    at_a_terminal = {
        **prepared,
        "doctor_environment": {**prepared["doctor_environment"], "noninteractive": False},
    }
    monkeypatch.setattr(planning, "preflight", lambda _repo: at_a_terminal)
    answers = iter(["y", manifest["manifest_sha256"]])
    monkeypatch.setattr("builtins.input", lambda _prompt: next(answers))
    assert planning.main(_run_argv(repo, task_file, manifest_path), stdin_tty=True) == 0
    assert "EXECUTION_COMPLETE" in capsys.readouterr().out
    assert len(provider_calls) == 4


def test_readiness_is_still_recomputed_from_tty_state_at_run():
    report = doctor_report(terminal_failure=True)
    assert planning.doctor_is_ready(report, term="dumb", noninteractive=True)[0] is True
    assert planning.doctor_is_ready(report, term="dumb", noninteractive=False)[0] is False


def test_copying_a_manifest_cannot_mint_a_fresh_claim(tmp_path):
    ledger_dir = tmp_path / "state" / "ledger"
    digest = "a" * 64
    planning.consume_manifest(tmp_path / "one.json", digest, ledger_dir=ledger_dir)
    assert (ledger_dir / f"{digest}.consumed").is_file()
    assert (ledger_dir.stat().st_mode & 0o777) == 0o700
    with pytest.raises(planning.GateBlocked, match="already consumed"):
        planning.consume_manifest(tmp_path / "copy.json", digest, ledger_dir=ledger_dir)
    assert not (tmp_path / "copy.json.consumed").exists()


def test_consume_manifest_rejects_a_malformed_hash(tmp_path):
    with pytest.raises(planning.GateBlocked, match="malformed"):
        planning.consume_manifest(tmp_path / "m.json", "../escape", ledger_dir=tmp_path / "l")


def _approve(monkeypatch, manifest, extra=()):
    answers = iter(["y", manifest["manifest_sha256"], *extra])
    monkeypatch.setattr("builtins.input", lambda _prompt: next(answers))


def _review_prompts(provider_calls):
    return [p for argv, p in provider_calls if argv[0] == "claude" and "Review the actual" in p]


def test_execution_outside_the_declared_paths_blocks_without_reverting(
    monkeypatch, tmp_path, capsys
):
    def stray_write(repo):
        (repo / "stray.txt").write_text("not in the plan\n", encoding="utf-8")

    repo, task_file, manifest_path, manifest, provider_calls = _prepared_run(
        monkeypatch, tmp_path, on_execute=stray_write
    )
    _approve(monkeypatch, manifest)
    assert planning.main(_run_argv(repo, task_file, manifest_path), stdin_tty=True) == 2
    err = capsys.readouterr().err
    assert "BLOCKED" in err and "stray.txt" in err
    assert (repo / "stray.txt").exists()
    assert _review_prompts(provider_calls) == []


def test_in_plan_edit_passes_and_reviewer_receives_the_real_diff(monkeypatch, tmp_path, capsys):
    def edit_only_source(repo):
        (repo / "source.txt").write_text("source fixture\nEDITED LINE\n", encoding="utf-8")

    repo, task_file, manifest_path, manifest, provider_calls = _prepared_run(
        monkeypatch, tmp_path, on_execute=edit_only_source
    )
    _approve(monkeypatch, manifest)
    assert planning.main(_run_argv(repo, task_file, manifest_path), stdin_tty=True) == 0
    (prompt,) = _review_prompts(provider_calls)
    assert "REPOSITORY DIFF:" in prompt and "+EDITED LINE" in prompt
    assert "EXECUTION_COMPLETE" in capsys.readouterr().out


def test_truncated_review_diff_can_never_pass(monkeypatch, tmp_path, capsys):
    def edit_source(repo):
        (repo / "source.txt").write_text("x" * 5000 + "\n", encoding="utf-8")

    monkeypatch.setattr(planning, "MAX_REVIEW_DIFF_BYTES", 200)
    repo, task_file, manifest_path, manifest, provider_calls = _prepared_run(
        monkeypatch, tmp_path, on_execute=edit_source
    )
    _approve(monkeypatch, manifest)
    assert planning.main(_run_argv(repo, task_file, manifest_path), stdin_tty=True) == 3
    out = capsys.readouterr().out
    assert "NEEDS_REVIEW" in out and "truncated" in out
    assert "[TRUNCATED" in _review_prompts(provider_calls)[0]


@pytest.mark.parametrize(
    "flag",
    ["requires_image_generation", "requires_publish_or_deploy"],
)
def test_structured_flags_trigger_the_separate_gate_without_keywords(flag):
    runner = FakeRunner(actions=["Upload the site to production."], plan_flags={flag: True})
    result = planning.run_debate("A task.", "plan_and_execute", runner)
    assert result["status"] == "NEEDS_REVIEW"
    assert runner.executions == 0


def test_plan_missing_the_required_flags_is_a_schema_failure():
    runner = FakeRunner()
    original_plan = runner.plan

    def plan_without_flags(task, prior, transcript):
        plan = original_plan(task, prior, transcript)
        del plan["requires_publish_or_deploy"]
        return plan

    runner.plan = plan_without_flags
    with pytest.raises(planning.GateBlocked, match="requires_publish_or_deploy"):
        planning.run_debate("A task.", "plan_and_execute", runner)
    assert runner.executions == 0


@pytest.mark.parametrize(
    "value",
    [
        "https://api.openai.com/v1",
        "https://api.openai.com/v1/",
        "https://api.openai.com",
        "https://api.openai.com/",
    ],
)
def test_openai_base_url_env_accepts_only_the_first_party_endpoint(value):
    planning._validate_openai_env({"OPENAI_BASE_URL": value})


@pytest.mark.parametrize(
    "value",
    [
        "https://third-party.example/v1",
        "http://api.openai.com/v1",
        "https://api.openai.com.evil.example/v1",
        "https://user:pw@api.openai.com/v1",
        "https://api.openai.com:8443/v1",
        "https://api.openai.com/v1/extra",
        "https://api.openai.com/v1?x=1",
        "",
    ],
)
def test_openai_base_url_env_override_blocks_everything_else(value):
    with pytest.raises(planning.GateBlocked, match="OPENAI_BASE_URL"):
        planning._validate_openai_env({"OPENAI_BASE_URL": value})


def test_codex_model_resolution_blocks_a_foreign_openai_base_url_from_the_environment(tmp_path):
    home = tmp_path / "codex-home"
    home.mkdir()
    env = {"CODEX_HOME": str(home), "OPENAI_BASE_URL": "https://third-party.example/v1"}
    with pytest.raises(planning.GateBlocked, match="OPENAI_BASE_URL"):
        planning.resolve_codex_model(tmp_path, env)
    assert planning.resolve_codex_model(tmp_path, {"CODEX_HOME": str(home)}).provider


@pytest.mark.parametrize(
    "settings",
    [
        {"env": {"ANTHROPIC_BASE_URL": "https://gateway.example"}},
        {"env": {"CLAUDE_CODE_USE_BEDROCK": "1"}},
        {"env": {"CLAUDE_CODE_USE_VERTEX": True}},
        {"env": {"CLAUDE_CODE_USE_FOUNDRY": "true"}},
        {"env": {"ANTHROPIC_AUTH_TOKEN": "secret-value"}},
        {"apiKeyHelper": "/bin/print-key"},
        {"env": "not-an-object"},
        ["not", "an", "object"],
    ],
)
def test_claude_settings_files_cannot_reroute_the_provider(tmp_path, settings):
    path = tmp_path / "settings.json"
    path.write_text(json.dumps(settings), encoding="utf-8")
    with pytest.raises(planning.GateBlocked) as caught:
        planning._validate_claude_settings(path)
    assert "secret-value" not in str(caught.value)


def test_claude_settings_absent_or_clean_pass_but_malformed_blocks(tmp_path):
    planning._validate_claude_settings(tmp_path / "missing.json")
    clean = tmp_path / "clean.json"
    clean.write_text(
        json.dumps({"env": {"ANTHROPIC_BASE_URL": "https://api.anthropic.com/"}}), encoding="utf-8"
    )
    planning._validate_claude_settings(clean)
    broken = tmp_path / "broken.json"
    broken.write_text("{not json", encoding="utf-8")
    with pytest.raises(planning.GateBlocked, match="not valid JSON"):
        planning._validate_claude_settings(broken)


def test_preflight_reads_injected_claude_settings_before_any_provider_call(tmp_path):
    settings = tmp_path / "settings.local.json"
    settings.write_text(json.dumps({"env": {"CLAUDE_CODE_USE_BEDROCK": "1"}}), encoding="utf-8")
    calls = []

    def fake_command(argv, **_kwargs):
        calls.append(argv)
        outputs = {
            ("claude", "--version"): "Claude Code test",
            (
                "claude",
                "--help",
            ): "--model <model> Provide an alias for the latest model (e.g. 'fable').",
            ("codex", "--version"): "codex-cli test",
            ("claude", "auth", "status", "--json"): '{"loggedIn":true,"authMethod":"claude.ai"}',
        }
        if tuple(argv) not in outputs:
            raise AssertionError("must block before Codex doctor")
        return subprocess.CompletedProcess(argv, 0, stdout=outputs[tuple(argv)], stderr="")

    with pytest.raises(planning.GateBlocked, match="non-Anthropic provider"):
        planning.preflight(
            tmp_path,
            command=fake_command,
            env={"TERM": "dumb", "CODEX_HOME": str(tmp_path / "codex-home")},
            stdin_tty=False,
            stdout_tty=False,
            stderr_tty=False,
            claude_settings_paths=[settings],
        )
    assert ["codex", "doctor", "--json"] not in calls


def test_default_claude_settings_paths_cover_user_project_local_and_managed(tmp_path):
    paths = _REAL_DEFAULT_SETTINGS_PATHS(tmp_path, {"CLAUDE_CONFIG_DIR": str(tmp_path / "cfg")})
    assert paths[:3] == [
        tmp_path / "cfg" / "settings.json",
        tmp_path / ".claude" / "settings.json",
        tmp_path / ".claude" / "settings.local.json",
    ]
    assert any(path.name == "managed-settings.json" for path in paths[3:])
