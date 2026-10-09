#!/usr/bin/env python3
"""Fail-closed Claude/Fable plus Codex planning runner.

Preparation is offline apart from CLI auth/config/provider-readiness diagnostics.
No model request is sent until a fresh manifest is displayed and explicitly
approved. Codex is invoked without a model override.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile
import tomllib
import uuid
from collections.abc import Callable
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any, Protocol, runtime_checkable
from urllib.parse import urlsplit

MAX_ROUNDS = 3
MANIFEST_TTL_MINUTES = 10
CONSUMED_SUFFIX = ".consumed"
CRITICAL_DOCTOR_CHECKS = {
    "auth.credentials",
    "config.load",
    "installation",
    "network.provider_reachability",
    "runtime.provenance",
}
KNOWN_DOCTOR_STATUSES = {"pass", "ok", "idle", "note", "warn", "fail"}
NONBLOCKING_TERMINAL_DIAGNOSTIC = "term=dumb - colors and cursor control are disabled"

PLAN_SCHEMA = {
    "type": "object",
    "required": ["summary", "steps", "risks", "blocking_unknowns"],
    "additionalProperties": False,
    "properties": {
        "summary": {"type": "string"},
        "steps": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["action", "files", "verify"],
                "additionalProperties": False,
                "properties": {
                    "action": {"type": "string"},
                    "files": {"type": "array", "items": {"type": "string"}},
                    "verify": {"type": "string"},
                },
            },
        },
        "risks": {"type": "array", "items": {"type": "string"}},
        "blocking_unknowns": {"type": "array", "items": {"type": "string"}},
    },
}
CHALLENGE_SCHEMA = {
    "type": "object",
    "required": ["satisfied", "blocking_objections", "specific_challenge"],
    "additionalProperties": False,
    "properties": {
        "satisfied": {"type": "boolean"},
        "blocking_objections": {"type": "array", "items": {"type": "string"}},
        "specific_challenge": {"type": "string"},
    },
}
REVIEW_SCHEMA = {
    "type": "object",
    "required": ["ship", "deviations", "summary"],
    "additionalProperties": False,
    "properties": {
        "ship": {"type": "boolean"},
        "deviations": {"type": "array", "items": {"type": "string"}},
        "summary": {"type": "string"},
    },
}
EXECUTION_SCHEMA = {
    "type": "object",
    "required": ["summary", "changed_paths", "checks", "blockers"],
    "additionalProperties": False,
    "properties": {
        "summary": {"type": "string"},
        "changed_paths": {"type": "array", "items": {"type": "string"}},
        "checks": {"type": "array", "items": {"type": "string"}},
        "blockers": {"type": "array", "items": {"type": "string"}},
    },
}


class GateBlocked(RuntimeError):
    """Raised when a required readiness or authorization gate fails."""


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def digest(value: Any) -> str:
    raw = value.encode("utf-8") if isinstance(value, str) else canonical_json(value).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def parse_json(text: str, label: str) -> dict[str, Any]:
    try:
        value = json.loads(text)
    except json.JSONDecodeError as exc:
        raise GateBlocked(f"{label} did not return valid JSON") from exc
    if not isinstance(value, dict):
        raise GateBlocked(f"{label} returned an unexpected JSON shape")
    return value


def doctor_is_ready(
    report: dict[str, Any],
    *,
    term: str,
    noninteractive: bool,
) -> tuple[bool, list[str]]:
    raw_checks = report.get("checks")
    if isinstance(raw_checks, dict):
        checks = []
        for key, value in raw_checks.items():
            if not isinstance(value, dict):
                return False, ["doctor report contains an unrecognized check"]
            if "id" in value and value["id"] != key:
                return False, ["doctor report contains a conflicting check identity"]
            checks.append({"id": key, **value})
    elif isinstance(raw_checks, list):
        checks = raw_checks
    else:
        checks = []
    if not checks:
        return False, ["doctor report has no checks"]
    by_id: dict[str, dict[str, Any]] = {}
    failures: list[dict[str, Any]] = []
    problems: list[str] = []
    for item in checks:
        if not isinstance(item, dict) or not isinstance(item.get("id"), str):
            problems.append("doctor report contains an unrecognized check")
            continue
        check_id = item["id"]
        status = item.get("status")
        if status not in KNOWN_DOCTOR_STATUSES:
            problems.append(f"unrecognized doctor status for {check_id}")
            continue
        if check_id in by_id:
            problems.append(f"doctor report contains duplicate check identity: {check_id}")
            continue
        by_id[check_id] = item
        if status == "fail":
            failures.append(item)
    missing = CRITICAL_DOCTOR_CHECKS - by_id.keys()
    if missing:
        problems.append("doctor report lacks critical checks: " + ", ".join(sorted(missing)))
    for check_id in CRITICAL_DOCTOR_CHECKS & by_id.keys():
        if by_id[check_id].get("status") not in {"pass", "ok"}:
            problems.append(f"critical check is not healthy: {check_id}")
    overall = report.get("overallStatus")
    if overall not in {"pass", "ok", "warn", "fail"}:
        problems.append("doctor report has an unrecognized overall status")
    if not failures:
        if overall == "fail":
            problems.append("doctor reports failure without a classified failed check")
        return not problems, problems
    if len(failures) == 1 and failures[0].get("id") == "terminal.env":
        check = failures[0]
        diagnostics = {
            re.sub(r"\s+", " ", str(check.get(key, "")).strip().lower())
            for key in ("message", "detail", "reason", "summary")
            if check.get(key)
        }
        cosmetic = bool(diagnostics) and diagnostics == {NONBLOCKING_TERMINAL_DIAGNOSTIC}
        if term == "dumb" and noninteractive and cosmetic and not problems:
            return True, ["terminal.env cosmetic failure ignored for noninteractive TERM=dumb"]
    problems.append("doctor reports a blocking failure")
    return False, problems


def _load_toml(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        with path.open("rb") as stream:
            value = tomllib.load(stream)
    except (OSError, tomllib.TOMLDecodeError) as exc:
        raise GateBlocked(f"Codex configuration cannot be read: {path}") from exc
    if not isinstance(value, dict):
        raise GateBlocked(f"Codex configuration has an unexpected shape: {path}")
    return value


def _project_is_trusted(user_config: dict[str, Any], repo: Path) -> bool:
    projects = user_config.get("projects", {})
    if not isinstance(projects, dict):
        return False
    target = str(repo.resolve())
    entry = projects.get(target, {})
    return isinstance(entry, dict) and entry.get("trust_level") == "trusted"


def _claude_advertises_fable(help_text: str) -> bool:
    normalized = re.sub(r"\s+", " ", help_text)
    return bool(
        re.search(
            r"--model\s+<model>.*?\balias\b.*?['`]fable['`]",
            normalized,
            flags=re.IGNORECASE,
        )
    )


def _validate_openai_endpoint(value: Any) -> None:
    if not isinstance(value, str):
        raise GateBlocked("Codex OpenAI endpoint configuration is malformed")
    try:
        parsed = urlsplit(value)
        port = parsed.port
    except ValueError as exc:
        raise GateBlocked("Codex OpenAI provider uses an unverified endpoint") from exc
    if (
        parsed.scheme != "https"
        or parsed.hostname not in {"api.openai.com", "chatgpt.com"}
        or parsed.username is not None
        or parsed.password is not None
        or port is not None
        or parsed.query
        or parsed.fragment
    ):
        raise GateBlocked("Codex OpenAI provider uses an unverified endpoint")


def _validate_openai_routing(system: dict[str, Any], user: dict[str, Any]) -> str:
    """Validate provider routing from machine/user config only.

    Codex deliberately ignores provider-routing keys in trusted project config.
    Provider tables are inspected per setting so a higher layer's unrelated
    provider entry cannot hide a lower layer's active OpenAI endpoint.
    """
    provider = user.get("model_provider", system.get("model_provider", "openai"))
    if not isinstance(provider, str) or provider != "openai":
        raise GateBlocked("Codex is not configured for the independent OpenAI provider")

    # Top-level openai_base_url is a supported override for the built-in
    # provider. Apply scalar precedence from the documented system -> user order.
    endpoint = system.get("openai_base_url")
    endpoint_source = "system"
    if "openai_base_url" in user:
        endpoint = user["openai_base_url"]
        endpoint_source = "user"
    if endpoint is not None:
        _validate_openai_endpoint(endpoint)
    elif "openai_base_url" in system or "openai_base_url" in user:
        raise GateBlocked(f"Codex {endpoint_source} OpenAI endpoint configuration is malformed")

    # Provider tables are merged by provider id and individual field, following
    # system -> user precedence. Project-local tables are intentionally omitted.
    openai_details: dict[str, Any] = {}
    for source_name, config in (("system", system), ("user", user)):
        provider_table = config.get("model_providers", {})
        if not isinstance(provider_table, dict):
            raise GateBlocked(f"Codex {source_name} model provider configuration is malformed")
        if "openai" not in provider_table:
            continue
        details = provider_table["openai"]
        if not isinstance(details, dict):
            raise GateBlocked(f"Codex {source_name} OpenAI provider configuration is malformed")
        openai_details.update(details)
    if "base_url" in openai_details:
        _validate_openai_endpoint(openai_details["base_url"])
    return provider


@dataclass(frozen=True)
class CodexModel:
    model: str
    source: str
    provider: str
    profile: str | None = None


def resolve_codex_model(repo: Path, env: dict[str, str] | None = None) -> CodexModel:
    """Report known model declarations without overriding Codex at invocation.

    Codex remains the runtime authority. A model that can be changed by a
    cloud-managed or built-in default is reported as runtime-resolved.
    """
    environment = env or os.environ
    codex_home = Path(environment.get("CODEX_HOME", str(Path.home() / ".codex")))
    user_path = codex_home / "config.toml"
    project_path = repo / ".codex" / "config.toml"
    user = _load_toml(user_path)
    project = _load_toml(project_path)
    trusted_project = _project_is_trusted(user, repo)
    project = project if trusted_project else {}
    system = (
        _load_toml(Path("/etc/codex/config.toml"))
        if Path("/etc/codex/config.toml").exists()
        else {}
    )
    merged: dict[str, Any] = {}
    # Known layers are merged low to high. Profiles are intentionally not
    # selected: this runner passes no --profile flag and lets Codex resolve it.
    merged.update(system)
    merged.update(user)
    merged.update(project)
    _validate_openai_routing(system, user)
    model = merged.get("model")
    if model is not None and not isinstance(model, str):
        raise GateBlocked("configured Codex model is malformed")
    if project.get("model"):
        selected_source = "trusted project config model"
    elif user.get("model"):
        selected_source = "user config model"
    elif system.get("model"):
        # Cloud-managed configuration outranks system configuration and is not
        # exposed by the supported read-only CLI diagnostics.
        model = "resolved by Codex CLI at invocation"
        selected_source = "Codex CLI managed/system configuration (runtime-resolved)"
    else:
        model = "resolved by Codex CLI at invocation"
        selected_source = "Codex CLI effective configuration (runtime-resolved)"
    return CodexModel(model=model, source=selected_source, provider="OpenAI Codex CLI")


def checkout_identity(
    repo: Path,
    *,
    command: Callable[..., subprocess.CompletedProcess[str]] | None = None,
    env: dict[str, str] | None = None,
) -> dict[str, str]:
    """Bind a manifest to its Git checkout and pre-run working-tree state."""
    working_dir = repo.resolve()
    environment = dict(os.environ if env is None else env)
    command_runner = command or run_command

    def git_output(arguments: list[str]) -> str:
        result = command_runner(["git", *arguments], cwd=working_dir, env=environment)
        if result.returncode:
            raise GateBlocked("cannot identify the active Git checkout")
        return result.stdout

    root = Path(git_output(["rev-parse", "--show-toplevel"]).strip()).resolve()
    common_dir_value = Path(git_output(["rev-parse", "--git-common-dir"]).strip())
    common_dir = (
        (root / common_dir_value).resolve()
        if not common_dir_value.is_absolute()
        else common_dir_value.resolve()
    )
    head = git_output(["rev-parse", "HEAD"]).strip()
    status = git_output(["status", "--porcelain", "-z", "--untracked-files=all"])
    if working_dir != root:
        raise GateBlocked("--repo must identify the Git worktree root")
    if not re.fullmatch(r"[0-9a-fA-F]{40,64}", head):
        raise GateBlocked("Git returned an unrecognized HEAD identity")
    return {
        "root": str(root),
        "git_common_dir_sha256": digest(str(common_dir)),
        "head": head.lower(),
        "status_sha256": digest(status),
    }


def _doctor_safe_summary(report: dict[str, Any]) -> dict[str, Any]:
    raw_checks = report.get("checks", [])
    if isinstance(raw_checks, dict):
        checks = [
            ({"id": key, **value} if isinstance(value, dict) and "id" not in value else value)
            for key, value in raw_checks.items()
        ]
    else:
        checks = raw_checks
    safe_checks = []
    if isinstance(checks, list):
        for item in checks:
            if isinstance(item, dict):
                safe_checks.append(
                    {
                        "id": item.get("id") if isinstance(item.get("id"), str) else "unknown",
                        "status": (
                            item.get("status") if isinstance(item.get("status"), str) else "unknown"
                        ),
                    }
                )
    return {
        "overall_status": report.get("overallStatus", "unknown"),
        "checks": safe_checks,
    }


def run_command(
    argv: list[str],
    *,
    cwd: Path,
    input_text: str | None = None,
    env: dict[str, str] | None = None,
) -> subprocess.CompletedProcess[str]:
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


def preflight(
    repo: Path,
    *,
    command: Callable[..., subprocess.CompletedProcess[str]] = run_command,
    env: dict[str, str] | None = None,
    stdin_tty: bool | None = None,
    stdout_tty: bool | None = None,
    stderr_tty: bool | None = None,
) -> dict[str, Any]:
    environment = dict(os.environ if env is None else env)

    def checked(argv: list[str]) -> subprocess.CompletedProcess[str]:
        result = command(argv, cwd=repo, env=environment)
        if result.returncode:
            raise GateBlocked(f"{argv[0]} readiness command failed")
        return result

    claude_version = checked(["claude", "--version"]).stdout.strip().splitlines()
    claude_help = checked(["claude", "--help"]).stdout
    if not _claude_advertises_fable(claude_help):
        raise GateBlocked("Claude CLI does not advertise the required fable model alias")
    codex_version = checked(["codex", "--version"]).stdout.strip().splitlines()
    auth_result = checked(["claude", "auth", "status", "--json"])
    auth = parse_json(auth_result.stdout, "Claude auth status")
    if auth.get("loggedIn") is not True:
        raise GateBlocked("Claude authentication is not ready")
    auth_method = auth.get("authMethod")
    if auth_method not in {"claude.ai", "console", "api_key"}:
        raise GateBlocked("Claude authentication provider cannot be verified as Anthropic")
    if any(
        environment.get(name, "").strip().lower() in {"1", "true", "yes"}
        for name in (
            "CLAUDE_CODE_USE_BEDROCK",
            "CLAUDE_CODE_USE_VERTEX",
            "CLAUDE_CODE_USE_FOUNDRY",
        )
    ):
        raise GateBlocked("Claude is configured for a non-Anthropic provider")
    anthropic_base_url = environment.get("ANTHROPIC_BASE_URL")
    if anthropic_base_url and anthropic_base_url.rstrip("/") != "https://api.anthropic.com":
        raise GateBlocked("Claude uses an unverified Anthropic API endpoint")
    doctor_result = command(
        ["codex", "doctor", "--json"],
        cwd=repo,
        env=environment,
    )
    doctor = parse_json(doctor_result.stdout, "Codex doctor")
    interactive = (
        (sys.stdin.isatty() if stdin_tty is None else stdin_tty)
        or (sys.stdout.isatty() if stdout_tty is None else stdout_tty)
        or (sys.stderr.isatty() if stderr_tty is None else stderr_tty)
    )
    ready, reasons = doctor_is_ready(
        doctor,
        term=environment.get("TERM", ""),
        noninteractive=not interactive,
    )
    if doctor_result.returncode and reasons != [
        "terminal.env cosmetic failure ignored for noninteractive TERM=dumb"
    ]:
        ready = False
        reasons = ["Codex doctor exited nonzero without the sole terminal exception"]
    if not ready:
        raise GateBlocked("Codex doctor blocked: " + "; ".join(reasons))
    codex_model = resolve_codex_model(repo, environment)
    noninteractive = not interactive
    return {
        "claude_version": claude_version[0] if claude_version else "unknown",
        "claude_auth": {
            "logged_in": True,
            "method": auth_method,
            "scope": "Claude Code CLI model requests for this host",
        },
        "codex_version": codex_version[0] if codex_version else "unknown",
        "codex_model": {
            "name": codex_model.model,
            "source": codex_model.source,
            "provider": codex_model.provider,
            "profile": codex_model.profile,
        },
        "doctor": _doctor_safe_summary(doctor),
        "doctor_notes": reasons,
        "doctor_environment": {
            "term": environment.get("TERM", ""),
            "noninteractive": noninteractive,
        },
        "checkout_identity": checkout_identity(repo, command=command, env=environment),
    }


def _bound_doctor_environment(environment: dict[str, Any]) -> dict[str, Any]:
    """The part of the doctor environment that is bound into the readiness digest.

    Whether a terminal is attached differs legitimately between ``prepare`` (often an
    agent without a TTY) and ``run`` (a human at one). Readiness is still recomputed
    from that flag at every preflight; only the flag itself is left out of the digest.
    """
    return {"term": environment.get("term", "")}


def prepare_manifest(
    task: str,
    mode: str,
    runner: str,
    preflight_result: dict[str, Any],
    *,
    now: datetime | None = None,
) -> dict[str, Any]:
    if mode not in {"plan_only", "plan_and_execute"}:
        raise GateBlocked("mode must be plan_only or plan_and_execute")
    if runner != "local_cli":
        raise GateBlocked(
            "Workflow execution is unavailable until its runtime provides fresh provider "
            "attestation and durable one-time execution state; use local_cli"
        )
    moment = now or datetime.now(UTC)
    rounds = MAX_ROUNDS
    max_calls = rounds * 2
    max_claude_calls = rounds
    max_codex_calls = rounds
    if mode == "plan_and_execute":
        max_calls += 2
        max_claude_calls += 1
        max_codex_calls += 1
    preflight_identity = {
        "claude_version": preflight_result["claude_version"],
        "claude_auth": preflight_result["claude_auth"],
        "codex_version": preflight_result["codex_version"],
        "codex_model": preflight_result["codex_model"],
        "checkout_identity": preflight_result["checkout_identity"],
        "doctor": preflight_result["doctor"],
        "doctor_notes": preflight_result["doctor_notes"],
        "doctor_environment": _bound_doctor_environment(preflight_result["doctor_environment"]),
    }
    unsigned = {
        "schema": "adversarial-planning-spend-manifest/v1",
        "manifest_id": str(uuid.uuid4()),
        "created_at": moment.isoformat(),
        "expires_at": (moment + timedelta(minutes=MANIFEST_TTL_MINUTES)).isoformat(),
        "mode": mode,
        "runner": runner,
        "task_sha256": digest(task),
        "claude": {
            "provider": "Anthropic",
            "model": "fable",
            "model_source": "Claude Code model alias",
            "authentication": preflight_result["claude_auth"],
            "max_calls": max_claude_calls,
        },
        "codex": {
            **preflight_result["codex_model"],
            "max_calls": max_codex_calls,
        },
        "debate": {"max_rounds": rounds, "max_calls": max_calls},
        "call_count_unit": "provider CLI invocations; internal model turns are not observable here",
        "cost_estimate": "unknown",
        "quota_estimate": "unknown",
        "separate_gates": {
            "image_generation": "not authorized by this manifest",
            "publishing_or_deployment": "not authorized by this manifest",
        },
        "doctor": preflight_result["doctor"],
        "doctor_notes": preflight_result["doctor_notes"],
        "doctor_environment": preflight_result["doctor_environment"],
        "checkout_identity": preflight_result["checkout_identity"],
        "preflight_identity": preflight_identity,
        "preflight_sha256": digest(preflight_identity),
    }
    unsigned["manifest_sha256"] = digest(unsigned)
    return unsigned


def validate_approval(
    manifest: dict[str, Any],
    *,
    task: str,
    typed_y: str,
    approved_manifest_sha256: str,
    current_preflight: dict[str, Any],
    now: datetime | None = None,
) -> None:
    if typed_y != "y":
        raise GateBlocked("approval must be the exact lowercase character y")
    if approved_manifest_sha256 != manifest.get("manifest_sha256"):
        raise GateBlocked("approval is not bound to the displayed manifest")
    if digest(task) != manifest.get("task_sha256"):
        raise GateBlocked("task changed after the manifest was displayed")
    if manifest.get("schema") != "adversarial-planning-spend-manifest/v1":
        raise GateBlocked("unsupported manifest schema")
    mode = manifest.get("mode")
    if manifest.get("runner") != "local_cli" or mode not in {"plan_only", "plan_and_execute"}:
        raise GateBlocked("manifest runner or mode is not supported by this local CLI")
    claude_manifest = manifest.get("claude")
    codex_manifest = manifest.get("codex")
    if not isinstance(claude_manifest, dict) or not isinstance(codex_manifest, dict):
        raise GateBlocked("manifest provider records are malformed")
    expected_calls = 6 if mode == "plan_only" else 8
    expected_claude_calls = 3 if mode == "plan_only" else 4
    expected_codex_calls = 3 if mode == "plan_only" else 4
    if (
        manifest.get("debate") != {"max_rounds": MAX_ROUNDS, "max_calls": expected_calls}
        or manifest.get("call_count_unit")
        != "provider CLI invocations; internal model turns are not observable here"
        or claude_manifest.get("provider") != "Anthropic"
        or claude_manifest.get("model") != "fable"
        or claude_manifest.get("max_calls") != expected_claude_calls
        or codex_manifest.get("provider") != "OpenAI Codex CLI"
        or codex_manifest.get("max_calls") != expected_codex_calls
    ):
        raise GateBlocked("manifest runner, provider identity, or call cap is invalid")
    manifest_copy = dict(manifest)
    displayed_hash = manifest_copy.pop("manifest_sha256", None)
    if displayed_hash != digest(manifest_copy):
        raise GateBlocked("manifest contents no longer match the displayed hash")
    identity = manifest.get("preflight_identity")
    if not isinstance(identity, dict) or digest(identity) != manifest.get("preflight_sha256"):
        raise GateBlocked("manifest readiness evidence failed its integrity check")
    try:
        expires = datetime.fromisoformat(manifest["expires_at"])
    except (KeyError, TypeError, ValueError) as exc:
        raise GateBlocked("manifest expiry is invalid") from exc
    if expires.tzinfo is None:
        raise GateBlocked("manifest expiry must include a timezone")
    if (now or datetime.now(UTC)) > expires:
        raise GateBlocked("manifest expired; prepare a fresh manifest")
    fresh_digest = digest(
        {
            "claude_version": current_preflight["claude_version"],
            "claude_auth": current_preflight["claude_auth"],
            "codex_version": current_preflight["codex_version"],
            "codex_model": current_preflight["codex_model"],
            "doctor": current_preflight["doctor"],
            "doctor_notes": current_preflight["doctor_notes"],
            "doctor_environment": _bound_doctor_environment(
                current_preflight["doctor_environment"]
            ),
            "checkout_identity": current_preflight["checkout_identity"],
        }
    )
    if fresh_digest != manifest.get("preflight_sha256"):
        raise GateBlocked("CLI readiness or effective Codex configuration changed")


def _validate_shape(value: dict[str, Any], schema: dict[str, Any], label: str) -> None:
    expected_type = schema.get("type")
    if expected_type == "object":
        if not isinstance(value, dict):
            raise GateBlocked(f"{label} must be an object")
        missing = set(schema.get("required", [])) - value.keys()
        if missing:
            raise GateBlocked(f"{label} is missing required fields: {', '.join(sorted(missing))}")
        properties = schema.get("properties", {})
        if schema.get("additionalProperties") is False:
            unknown = set(value) - properties.keys()
            if unknown:
                raise GateBlocked(f"{label} has unexpected fields: {', '.join(sorted(unknown))}")
        for key, child_schema in properties.items():
            if key in value:
                _validate_value(value[key], child_schema, f"{label}.{key}")
    else:
        _validate_value(value, schema, label)


def _validate_value(value: Any, schema: dict[str, Any], label: str) -> None:
    expected_type = schema.get("type")
    if expected_type == "string":
        valid = isinstance(value, str)
    elif expected_type == "boolean":
        valid = isinstance(value, bool)
    elif expected_type == "array":
        valid = isinstance(value, list)
        if valid and "items" in schema:
            for index, item in enumerate(value):
                _validate_value(item, schema["items"], f"{label}[{index}]")
    elif expected_type == "object":
        valid = isinstance(value, dict)
    else:
        valid = True
    if not valid:
        raise GateBlocked(f"{label} has the wrong type; expected {expected_type}")
    if expected_type == "object":
        _validate_shape(value, schema, label)


@runtime_checkable
class PlanningRunner(Protocol):
    """Everything run_debate needs from a provider runner; none of it is optional."""

    def plan(
        self, task: str, prior: dict[str, Any] | None, transcript: list[dict[str, Any]]
    ) -> dict[str, Any]: ...

    def challenge(
        self, task: str, plan: dict[str, Any], round_number: int, transcript: list[dict[str, Any]]
    ) -> dict[str, Any]: ...

    def pre_execution_gate(self, plan: dict[str, Any]) -> None: ...

    def execute(self, task: str, plan: dict[str, Any]) -> dict[str, Any]: ...

    def review(
        self, task: str, plan: dict[str, Any], execution: dict[str, Any]
    ) -> dict[str, Any]: ...


def require_interactive_terminal(stdin_tty: bool | None = None) -> None:
    """Refuse to read an approval from anything but a human at a terminal."""
    if not (sys.stdin.isatty() if stdin_tty is None else stdin_tty):
        raise GateBlocked("approval must be typed on an interactive terminal")


def default_ledger_dir() -> Path:
    """Fixed per-user directory holding hash-keyed single-use claims."""
    state_home = os.environ.get("XDG_STATE_HOME") or str(Path.home() / ".local" / "state")
    return Path(state_home) / "devskyy" / "adversarial-planning"


def _claim(ledger: Path, payload: dict[str, str]) -> None:
    try:
        descriptor = os.open(ledger, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    except FileExistsError as exc:
        raise GateBlocked("manifest already consumed") from exc
    with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
        handle.write(json.dumps(payload) + "\n")


def consume_manifest(
    manifest_path: Path,
    manifest_sha256: str,
    *,
    ledger_dir: Path | None = None,
    now: datetime | None = None,
) -> Path:
    """Claim an approved manifest exactly once, atomically, before any provider call.

    Two exclusive-create claims are made: one keyed by manifest hash in a per-user
    directory (so copying the manifest elsewhere cannot mint a fresh claim) and one
    beside the manifest path. Neither is ever released: a run that fails after
    claiming still burned its approval, so a replay inside the manifest TTL needs a
    freshly displayed manifest.
    """
    if not re.fullmatch(r"[0-9a-f]{64}", manifest_sha256):
        raise GateBlocked("manifest hash is malformed")
    directory = ledger_dir or default_ledger_dir()
    directory.mkdir(mode=0o700, parents=True, exist_ok=True)
    payload = {
        "manifest_sha256": manifest_sha256,
        "consumed_at": (now or datetime.now(UTC)).isoformat(),
    }
    _claim(directory / f"{manifest_sha256}{CONSUMED_SUFFIX}", payload)
    ledger = Path(f"{manifest_path.resolve()}{CONSUMED_SUFFIX}")
    _claim(ledger, payload)
    return ledger


def run_debate(
    task: str,
    mode: str,
    runner: PlanningRunner,
    *,
    image_generation_approval: str = "",
    publishing_approval: str = "",
    gate_approver: Callable[[str, dict[str, Any]], str] | None = None,
) -> dict[str, Any]:
    if not isinstance(runner, PlanningRunner):
        raise GateBlocked("runner does not implement the required execution gate")
    plan: dict[str, Any] | None = None
    transcript = []
    converged = False
    for round_number in range(1, MAX_ROUNDS + 1):
        plan = runner.plan(task, plan, transcript)
        _validate_shape(plan, PLAN_SCHEMA, "Fable plan")
        challenge_envelope = runner.challenge(task, plan, round_number, transcript)
        if not isinstance(challenge_envelope, dict):
            raise GateBlocked("Codex challenge response has an unexpected shape")
        challenge = dict(challenge_envelope)
        codex_verbatim = challenge.pop("codex_verbatim", None)
        if not isinstance(codex_verbatim, str) or not codex_verbatim.strip():
            raise GateBlocked("Codex challenge response did not preserve its raw output")
        _validate_shape(challenge, CHALLENGE_SCHEMA, "Codex challenge")
        transcript.append(
            {
                "round": round_number,
                "plan": plan,
                "challenge": {**challenge, "codex_verbatim": codex_verbatim},
            }
        )
        if (
            challenge["satisfied"] is True
            and not challenge["blocking_objections"]
            and not plan["blocking_unknowns"]
        ):
            converged = True
            break
    if not converged:
        return {
            "status": "NEEDS_REVIEW",
            "rounds": len(transcript),
            "plan": plan,
            "transcript": transcript,
            "reason": "blocking objections remain after the three-round cap",
        }
    if mode == "plan_only":
        return {
            "status": "PLAN_READY",
            "rounds": len(transcript),
            "plan": plan,
            "transcript": transcript,
        }
    if mode != "plan_and_execute":
        raise GateBlocked("unknown execution mode")
    runner.pre_execution_gate(plan)
    scope = " ".join(step["action"] for step in plan.get("steps", [])).lower()
    scope = re.sub(r"\b(?:do not|don't|never|without|no)\b[^.;,\n]*", "", scope)
    if re.search(
        r"\b(?:generate|create|produce|render|submit|invoke|call)\b.{0,60}"
        r"\b(?:images?|visuals?|artwork|media|videos?|backgrounds?|scenes?|assets?)\b"
        r"|\bimage[- ]?gen\b|\bvideo generation\b",
        scope,
    ):
        if not image_generation_approval and gate_approver:
            image_generation_approval = gate_approver("image generation", plan)
        if image_generation_approval != "y":
            return {
                "status": "NEEDS_REVIEW",
                "rounds": len(transcript),
                "plan": plan,
                "transcript": transcript,
                "reason": "separate image-generation authorization is required",
            }
    if re.search(r"\b(?:publish|deploy|go live)\b|\brelease to live\b", scope):
        if not publishing_approval and gate_approver:
            publishing_approval = gate_approver("publishing or deployment", plan)
        if publishing_approval != "y":
            return {
                "status": "NEEDS_REVIEW",
                "rounds": len(transcript),
                "plan": plan,
                "transcript": transcript,
                "reason": "separate publishing/deployment authorization is required",
            }
    execution_envelope = runner.execute(task, plan)
    if not isinstance(execution_envelope, dict):
        raise GateBlocked("Codex execution response has an unexpected shape")
    execution = dict(execution_envelope)
    codex_verbatim = execution.pop("codex_verbatim", None)
    if not isinstance(codex_verbatim, str) or not codex_verbatim.strip():
        raise GateBlocked("Codex execution response did not preserve its raw output")
    _validate_shape(execution, EXECUTION_SCHEMA, "Codex execution result")
    execution_evidence = {**execution, "codex_verbatim": codex_verbatim}
    review = runner.review(task, plan, execution_evidence)
    _validate_shape(review, REVIEW_SCHEMA, "Fable execution review")
    status = (
        "EXECUTION_COMPLETE"
        if review["ship"] is True and not review["deviations"] and not execution["blockers"]
        else "NEEDS_REVIEW"
    )
    return {
        "status": status,
        "rounds": len(transcript),
        "plan": plan,
        "transcript": transcript,
        "execution": execution_evidence,
        "review": review,
    }


class CliRunner:
    def __init__(self, repo: Path, expected_checkout_identity: dict[str, str] | None = None):
        self.repo = repo
        self.expected_checkout_identity = expected_checkout_identity

    def _claude(self, prompt: str, schema: dict[str, Any]) -> dict[str, Any]:
        command = [
            "claude",
            "--print",
            "--model",
            "fable",
            "--no-session-persistence",
            "--output-format",
            "json",
            "--json-schema",
            json.dumps(schema),
            "--tools",
            "Read,Grep,Glob",
            "--max-turns",
            "8",
        ]
        result = run_command(command, cwd=self.repo, input_text=prompt)
        if result.returncode:
            raise GateBlocked("Claude/Fable request failed; no fallback model is permitted")
        response = parse_json(result.stdout, "Claude/Fable response")
        structured = response.get("structured_output")
        if isinstance(structured, dict):
            return structured
        raw = response.get("result")
        if isinstance(raw, str):
            parsed = parse_json(raw, "Claude/Fable structured response")
            return parsed
        raise GateBlocked("Claude/Fable response did not contain structured output")

    def _codex(
        self, prompt: str, schema: dict[str, Any], sandbox: str
    ) -> tuple[dict[str, Any], str]:
        with tempfile.TemporaryDirectory(prefix="adversarial-planning-") as directory:
            temp = Path(directory)
            schema_path = temp / "schema.json"
            output_path = temp / "last-message.txt"
            schema_path.write_text(json.dumps(schema), encoding="utf-8")
            command = [
                "codex",
                "exec",
                "--json",
                "--ephemeral",
                "--sandbox",
                sandbox,
                "--output-schema",
                str(schema_path),
                "--output-last-message",
                str(output_path),
            ]
            command.append("-")
            result = run_command(command, cwd=self.repo, input_text=prompt)
            if result.returncode:
                raise GateBlocked("Codex request failed; no model fallback is permitted")
            raw = output_path.read_text(encoding="utf-8") if output_path.exists() else ""
            parsed = parse_json(raw, "Codex structured response")
            return parsed, raw

    def pre_execution_gate(self, plan: dict[str, Any]) -> None:
        if self.expected_checkout_identity is not None:
            current_identity = checkout_identity(self.repo)
            if current_identity != self.expected_checkout_identity:
                raise GateBlocked("execution checkout changed after manifest approval")
        paths: set[str] = set()
        for step in plan.get("steps", []):
            for name in step.get("files", []):
                if not isinstance(name, str) or not name or any(char in name for char in "*?[]"):
                    raise GateBlocked("plan contains a non-explicit file path")
                candidate = Path(name)
                if candidate.is_absolute():
                    raise GateBlocked("plan contains an absolute path; execution is blocked")
                resolved = (self.repo / candidate).resolve()
                try:
                    relative = resolved.relative_to(self.repo.resolve()).as_posix()
                except ValueError as exc:
                    raise GateBlocked("plan path escapes the active repository") from exc
                if relative == ".":
                    raise GateBlocked("plan grants write access to the repository root")
                paths.add(relative)
        status = run_command(
            ["git", "status", "--porcelain", "-z", "--untracked-files=all"],
            cwd=self.repo,
        )
        if status.returncode:
            raise GateBlocked("cannot inspect checkout state before execution")
        dirty_paths = []
        for record in status.stdout.split(chr(0)):
            if len(record) >= 4:
                if "R" in record[:2] or "C" in record[:2]:
                    raise GateBlocked("checkout contains a rename/copy that needs manual review")
                dirty_paths.append(record[3:])
        overlaps = sorted(
            planned
            for planned in paths
            if any(
                planned == dirty
                or planned.startswith(dirty + "/")
                or dirty.startswith(planned + "/")
                for dirty in dirty_paths
            )
        )
        if overlaps:
            raise GateBlocked("plan overlaps existing dirty work: " + ", ".join(overlaps))

    def plan(
        self, task: str, prior: dict[str, Any] | None, transcript: list[dict[str, Any]]
    ) -> dict[str, Any]:
        if prior is None:
            prompt = (
                "Create a source-bound implementation plan. Identify concrete steps, affected files, "
                "a falsifiable check for each step, risks, and blocking unknowns. Do not execute.\n\n"
                "TASK:\n" + task
            )
        else:
            latest = transcript[-1]["challenge"]
            prompt = (
                "Revise only in response to the independent Codex challenge. Preserve sound parts. "
                "If a blocking objection cannot be resolved from evidence, list it as a blocking unknown. "
                "Do not execute.\nCURRENT PLAN:\n"
                + canonical_json(prior)
                + "\nCODEX CHALLENGE:\n"
                + canonical_json(latest)
            )
        return self._claude(prompt, PLAN_SCHEMA)

    def challenge(
        self, task: str, plan: dict[str, Any], round_number: int, transcript: list[dict[str, Any]]
    ) -> dict[str, Any]:
        prompt = (
            "Independently challenge this plan. Identify blocking errors, missing evidence, unsafe assumptions, "
            "and checks that cannot falsify completion. Satisfied is true only if there are no unresolved "
            "blocking objections. Return your direct assessment in the required schema.\nTASK:\n"
            + task
            + "\nPLAN:\n"
            + canonical_json(plan)
        )
        value, raw = self._codex(prompt, CHALLENGE_SCHEMA, "read-only")
        value["codex_verbatim"] = raw
        return value

    def execute(self, task: str, plan: dict[str, Any]) -> dict[str, Any]:
        prompt = (
            "Execute only the converged plan in this repository. Do not generate media, publish, or deploy "
            "unless separately authorized by the operator. Report changed paths, checks and exact outcomes.\nTASK:\n"
            + task
            + "\nPLAN:\n"
            + canonical_json(plan)
        )
        value, raw = self._codex(prompt, EXECUTION_SCHEMA, "workspace-write")
        return {**value, "codex_verbatim": raw}

    def review(self, task: str, plan: dict[str, Any], execution: dict[str, Any]) -> dict[str, Any]:
        prompt = (
            "Review the actual execution report and repository changes against the plan. You have read-only "
            "tools; inspect named files/diffs if needed. Do not change files. Do not infer success from plan text.\n"
            "TASK:\n"
            + task
            + "\nPLAN:\n"
            + canonical_json(plan)
            + "\nEXECUTION EVIDENCE:\n"
            + canonical_json(execution)
        )
        return self._claude(prompt, REVIEW_SCHEMA)


def _read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except OSError as exc:
        raise GateBlocked(f"cannot read input file: {path}") from exc


def main(
    argv: list[str] | None = None,
    *,
    stdin_tty: bool | None = None,
    ledger_dir: Path | None = None,
) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="action", required=True)
    prep = sub.add_parser("prepare")
    prep.add_argument("--task-file", type=Path, required=True)
    prep.add_argument("--manifest", type=Path, required=True)
    prep.add_argument("--mode", choices=("plan_only", "plan_and_execute"), default="plan_only")
    prep.add_argument("--runner", choices=("local_cli",), default="local_cli")
    prep.add_argument("--repo", type=Path, default=Path.cwd())
    run = sub.add_parser("run")
    run.add_argument("--task-file", type=Path, required=True)
    run.add_argument("--manifest", type=Path, required=True)
    run.add_argument("--repo", type=Path, default=Path.cwd())
    args = parser.parse_args(argv)
    try:
        task = _read_text(args.task_file)
        fresh = preflight(args.repo.resolve())
        if args.action == "prepare":
            if Path(f"{args.manifest.resolve()}{CONSUMED_SUFFIX}").exists():
                raise GateBlocked(
                    "manifest path already has a consumed-approval ledger; choose a new --manifest path"
                )
            manifest = prepare_manifest(task, args.mode, args.runner, fresh)
            args.manifest.parent.mkdir(parents=True, exist_ok=True)
            args.manifest.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
            print(json.dumps(manifest, indent=2))
            return 0
        manifest = parse_json(_read_text(args.manifest), "manifest")
        if manifest.get("runner") != "local_cli":
            raise GateBlocked("this manifest selected the Workflow runner, not local_cli")
        print(json.dumps(manifest, indent=2))
        require_interactive_terminal(stdin_tty)
        typed_y = input("Type lowercase y to approve these exact providers, mode, and call cap: ")
        approved_hash = input("Re-enter the displayed manifest_sha256: ").strip()
        fresh = preflight(args.repo.resolve())
        validate_approval(
            manifest,
            task=task,
            typed_y=typed_y,
            approved_manifest_sha256=approved_hash,
            current_preflight=fresh,
        )
        consume_manifest(args.manifest, manifest["manifest_sha256"], ledger_dir=ledger_dir)
        runner = CliRunner(args.repo.resolve(), fresh["checkout_identity"])

        def ask_separate_gate(name: str, plan: dict[str, Any]) -> str:
            require_interactive_terminal(stdin_tty)
            plan_hash = digest(plan)
            print(
                json.dumps(
                    {
                        "separate_authorization": name,
                        "converged_plan": plan,
                        "plan_sha256": plan_hash,
                    },
                    indent=2,
                )
            )
            typed_y = input(f"Authorize only {name} in this exact plan; type lowercase y: ")
            approved_hash = input("Re-enter the displayed plan_sha256: ").strip()
            return typed_y if approved_hash == plan_hash else ""

        result = run_debate(
            task,
            manifest["mode"],
            runner,
            gate_approver=ask_separate_gate,
        )
        print(json.dumps(result, indent=2))
        return 0 if result["status"] in {"PLAN_READY", "EXECUTION_COMPLETE"} else 3
    except (GateBlocked, OSError, EOFError) as exc:
        print(json.dumps({"status": "BLOCKED", "reason": str(exc)}, indent=2), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
