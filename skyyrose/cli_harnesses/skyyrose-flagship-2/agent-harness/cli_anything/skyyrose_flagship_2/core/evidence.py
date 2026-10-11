"""
Evidence shared by the Fashion Theme Team and God Mode X.

Each gate run becomes a ledger entry carrying the Fashion Theme Team
release-engineer fields: candidate id, gate id, command, status, tool versions,
environment, timestamp, artifact path and hash, owner, and reviewer.

``build_record`` turns the runs for ONE candidate into a God Mode X
``task-evidence`` schema-1 record, which God Mode X's own
``check_completion.py`` validates. The Fashion Theme Team verdict sits in an
extra ``fashion_theme_team`` block, because its rules are stricter:
  - FAIL when any included gate failed.
  - BLOCKED until a reviewer who is not the gate owner records a PASS review
    of this exact candidate (a builder cannot review its own candidate).
    Reviews from every session in the CLI home count, and each reviewer's
    latest review is the one that stands: one FAIL means FAIL. Independence
    gates PASS only; a FAIL stands even if its reviewer later runs a gate.
  - BLOCKED when the installed deps cannot be identified at export.
  - PASS only means ready for founder review. It never authorises a deploy.

The claim is never inflated to satisfy the checker. A dirty tree yields
``partial`` and a failed gate yields ``blocked``, and God Mode X is expected to
reject both.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from cli_anything.skyyrose_flagship_2.core.candidate import Candidate
from cli_anything.skyyrose_flagship_2.core.gates import Gate
from cli_anything.skyyrose_flagship_2.core.session import SessionError, read_log_header
from cli_anything.skyyrose_flagship_2.utils.backend import (
    DEPS_LOCK_REL,
    ScriptResult,
    Toolchain,
    environment_label,
    harness_sha256,
    sha256_file,
)

CATEGORIES = (
    "functional",
    "integration",
    "runtime",
    "regression",
    "error_recovery",
    "security_data",
    "accessibility",
    "performance",
    "quality",
    "external_contract",
    "operational_release",
)
_NOT_APPLICABLE_REASON = {
    "operational_release": "No release is performed: this CLI has no deploy path.",
    "accessibility": "No flagship-2 npm gate audits accessibility; that needs a separate browser review.",
    "error_recovery": "The theme gates do not exercise error-recovery behaviour.",
}
DEFAULT_EXCLUSIONS = (
    "Production or staging deploy",
    "Paid image-generation or judge-provider calls",
    "V2 certification pin changes (founder-approved recert only)",
    "Eyes-on visual review of rendered pages",
)


class EvidenceError(RuntimeError):
    """Evidence cannot be built or validated."""


def _phase(ok: bool, text: str) -> dict[str, str]:
    return {"status": "PASS" if ok else "FAIL", "observation": text}


def _now() -> str:
    return datetime.now(UTC).isoformat(timespec="seconds")


OWNER_SOURCES = ("env", "git")
UNVERIFIED_OWNER = "gate owner supplied via SKYYROSE2_GATE_OWNER is unverified"


def _is_git_config_injection(name: str) -> bool:
    """Env vars that hand git a config value per command, with no file on disk."""
    return name in {"GIT_CONFIG_COUNT", "GIT_CONFIG_PARAMETERS"} or name.startswith(
        ("GIT_CONFIG_KEY_", "GIT_CONFIG_VALUE_")
    )


def default_owner(repo: Path | None = None) -> tuple[str, str]:
    """
    (owner, source). ``source`` is ``env`` when SKYYROSE2_GATE_OWNER supplied the
    name, else ``git``. Neither is proof of identity; the source is recorded so a
    reviewer can see which runs had a freely chosen owner name.

    The ``git`` lookup runs in *repo* and ignores per-command config injection
    (GIT_CONFIG_COUNT/KEY_n/VALUE_n, GIT_CONFIG_PARAMETERS), so an env-only name
    cannot read as ``git``. It is still self-declared: whoever can write the git
    config files (or point HOME / GIT_CONFIG_GLOBAL at another one) chooses it.
    """
    env = os.environ.get("SKYYROSE2_GATE_OWNER")
    if env:
        return env, "env"
    clean_env = {k: v for k, v in os.environ.items() if not _is_git_config_injection(k)}
    try:
        out = subprocess.run(
            ["git", "config", "user.name"],
            capture_output=True,
            text=True,
            timeout=10,
            cwd=repo,
            env=clean_env,
        )
        name = out.stdout.strip()
    except (OSError, subprocess.TimeoutExpired):
        name = ""
    if not name:
        raise EvidenceError(
            "No gate owner: set git user.name or SKYYROSE2_GATE_OWNER. Evidence needs a named owner."
        )
    return name, "git"


# ---------------------------------------------------------------------------
# Run ledger entries
# ---------------------------------------------------------------------------


def run_entry(
    *,
    gate: Gate,
    result: ScriptResult,
    before: Candidate,
    after: Candidate,
    toolchain: Toolchain,
    log_path: Path,
    owner: str,
    owner_source: str,
) -> dict[str, Any]:
    """
    Build one ledger entry for one gate run.

    A check gate is evidence for the tree it ran against, and it fails if it
    changed any tracked file. A build gate is evidence for the tree it produced.
    """
    if owner_source not in OWNER_SOURCES:
        raise EvidenceError(f"owner_source must be one of {OWNER_SOURCES}, got {owner_source!r}")
    status, why = derive_status(
        log_header(
            gate=gate,
            result=result,
            before=before,
            after=after,
            owner=owner,
            owner_source=owner_source,
        )
    )
    if status == "PASS":
        why = f"{why} in {result.duration_s}s"
    bound = after if gate.kind == "build" else before
    tail = (result.stdout.strip().splitlines() or [""])[-1][:300]
    return {
        "gate_id": gate.name,
        "kind": gate.kind,
        "command": " ".join(result.command),
        "cwd": result.cwd,
        "status": status,
        "status_reason": why,
        "returncode": result.returncode,
        "duration_s": result.duration_s,
        "started_at": result.started_at,
        "observed_at": _now(),
        "candidate_id": bound.candidate_id,
        "revision": bound.revision,
        "target_artifact": bound.artifact,
        "candidate_changed": before.candidate_id != after.candidate_id,
        "changed_paths": result.changed_paths,
        "categories": list(gate.categories),
        "toolchain_ok": toolchain.ok,
        "tool_versions": toolchain.versions(),
        "environment": environment_label(toolchain),
        "artifact": {"path": str(log_path), "sha256": sha256_file(log_path)},
        "stdout_tail": tail,
        "owner": owner,
        "owner_source": owner_source,
        "reviewer": None,
        "harness_sha256": harness_sha256(),
    }


def log_header(
    *,
    gate: Gate,
    result: ScriptResult,
    before: Candidate,
    after: Candidate,
    owner: str,
    owner_source: str,
) -> dict[str, Any]:
    """The facts a run's status is derived from; written as the first line of its log."""
    return {
        "gate_id": gate.name,
        "kind": gate.kind,
        "command": " ".join(result.command),
        "returncode": result.returncode,
        "timed_out": result.timed_out,
        "changed_paths": result.changed_paths,
        "candidate_before": before.candidate_id,
        "candidate_after": after.candidate_id,
        "started_at": result.started_at,
        "owner": owner,
        "owner_source": owner_source,
        "harness_sha256": harness_sha256(),
    }


def derive_status(header: dict[str, Any]) -> tuple[str, str]:
    """Single rule for PASS/FAIL, used at run time and re-applied to the log at export."""
    if header["timed_out"]:
        return "FAIL", "timed out"
    if header["returncode"] != 0:
        return "FAIL", f"exit {header['returncode']}"
    if header["kind"] == "check" and header["changed_paths"]:
        return "FAIL", f"read-only gate changed tracked files: {', '.join(header['changed_paths'])}"
    return "PASS", "exit 0"


def _norm(name: str) -> str:
    return name.strip().casefold()


def review_entry(
    *, candidate: Candidate, reviewer: str, disposition: str, note: str, owners: set[str]
) -> dict[str, Any]:
    """
    *owners* are the ``owner`` values recorded on this candidate's runs, never the
    current environment, so changing SKYYROSE2_GATE_OWNER cannot launder a self-review.
    """
    if disposition not in {"PASS", "FAIL"}:
        raise EvidenceError("disposition must be PASS or FAIL")
    if not owners:
        raise EvidenceError(f"No gate runs on candidate {candidate.candidate_id} to review.")
    if _norm(reviewer) in {_norm(o) for o in owners}:
        raise EvidenceError(
            f"Reviewer {reviewer!r} ran gates on this candidate. The Fashion Theme Team requires an "
            "independent reviewer; a builder cannot review its own candidate."
        )
    if not note.strip():
        raise EvidenceError("A review needs a note naming what was inspected")
    return {
        "candidate_id": candidate.candidate_id,
        "revision": candidate.revision,
        "reviewer": reviewer,
        "disposition": disposition,
        "note": note,
        "reviewed_at": _now(),
        "harness_sha256": harness_sha256(),
    }


# ---------------------------------------------------------------------------
# Record builder
# ---------------------------------------------------------------------------


def runs_for(
    runs: list[dict[str, Any]], candidate: Candidate, harness: str | None = None
) -> tuple[list[dict[str, Any]], int, dict[str, int]]:
    """
    Latest run per gate for *candidate* produced by this harness version.

    Returns (included, stale_count, earlier_failures_per_gate). Runs on another
    candidate or by other harness code are stale. An earlier FAIL that a later
    PASS superseded is counted, never silently dropped.
    """
    harness = harness or harness_sha256()
    latest: dict[str, dict[str, Any]] = {}
    failures: dict[str, int] = {}
    stale = 0
    for run in runs:
        if (
            run.get("candidate_id") != candidate.candidate_id
            or run.get("harness_sha256") != harness
        ):
            stale += 1
            continue
        previous = latest.get(run["gate_id"])
        if previous is not None and previous["status"] != "PASS":
            failures[run["gate_id"]] = failures.get(run["gate_id"], 0) + 1
        latest[run["gate_id"]] = run
    return list(latest.values()), stale, failures


def owner_sources_for(runs: list[dict[str, Any]], candidate: Candidate) -> dict[str, list[str]]:
    """
    {owner: sorted owner_source values} over every run on *candidate*, by any
    harness version, in any session, superseded or not. A run recorded before
    owner_source existed reports ``unrecorded``, which counts as unverified.
    """
    sources: dict[str, set[str]] = {}
    for r in runs:
        if r.get("candidate_id") == candidate.candidate_id and r.get("owner"):
            sources.setdefault(r["owner"], set()).add(str(r.get("owner_source") or "unrecorded"))
    return {owner: sorted(found) for owner, found in sorted(sources.items())}


def run_owners(runs: list[dict[str, Any]], candidate: Candidate) -> set[str]:
    """Everyone who ran a gate on *candidate*, by any harness version."""
    return set(owner_sources_for(runs, candidate))


def _check_log(run: dict[str, Any], src: Path) -> None:
    """Re-derive the run's status from its hashed log so an edited ledger is caught."""
    try:
        header = read_log_header(src)
        derived, _ = derive_status(header)
    except (SessionError, KeyError) as exc:
        raise EvidenceError(f"Log for {run['gate_id']} is not a valid run log: {exc}") from exc
    bound = header["candidate_after"] if run["kind"] == "build" else header["candidate_before"]
    if (
        header["gate_id"] != run["gate_id"]
        or derived != run["status"]
        or bound != run["candidate_id"]
        or header["harness_sha256"] != run.get("harness_sha256")
        or header.get("owner") != run.get("owner")
        or header.get("owner_source") != run.get("owner_source")
        or run.get("owner_source") not in OWNER_SOURCES
    ):
        raise EvidenceError(
            f"Ledger entry for {run['gate_id']} disagrees with its log (ledger {run['status']}, "
            f"log {derived}; owner/source {run.get('owner')}/{run.get('owner_source')} vs "
            f"{header.get('owner')}/{header.get('owner_source')}); the session file was edited. "
            "Rerun the gate."
        )


def latest_reviews(
    reviews: list[dict[str, Any]], candidate: Candidate, harness: str, owners: set[str]
) -> list[dict[str, Any]]:
    """
    The reviews that decide the Fashion Theme Team verdict for *candidate*.

    - Every FAIL on this candidate stands, whatever harness or session recorded
      it, and no later review can withdraw it. Reviewer names are self-declared,
      so a "withdrawal" is indistinguishable from someone else typing the same
      name. The only way past a FAIL is a new candidate, i.e. a code change.
    - A PASS counts only for this exact harness code, from someone who is not
      an owner of the candidate's runs (latest PASS per reviewer).

    A review with any other disposition fails closed.

    *reviews* may come from many sessions; the result is ordered by ``reviewed_at``.
    """
    blocked = {_norm(o) for o in owners}
    on_candidate = [r for r in reviews if r.get("candidate_id") == candidate.candidate_id]
    for r in on_candidate:
        if r.get("disposition") not in {"PASS", "FAIL"} or not isinstance(r.get("reviewer"), str):
            raise EvidenceError(
                f"Malformed review on candidate {candidate.candidate_id}: {r!r}. "
                "Refusing to decide a verdict from an unreadable ledger."
            )
    fails = [r for r in on_candidate if r["disposition"] == "FAIL"]
    passes: dict[str, dict[str, Any]] = {}
    for r in sorted(on_candidate, key=lambda r: str(r.get("reviewed_at", ""))):
        key = _norm(r["reviewer"])
        if r["disposition"] == "PASS" and r.get("harness_sha256") == harness and key not in blocked:
            passes[key] = r
    return sorted([*fails, *passes.values()], key=lambda r: str(r.get("reviewed_at", "")))


def _ftt_verdict(
    included: list[dict[str, Any]],
    gates_ok: bool,
    reviews: list[dict[str, Any]],
    candidate: Candidate,
    owner_sources: dict[str, list[str]],
    deps_known: bool,
) -> dict[str, Any]:
    """
    *gates_ok* is the environment-matched result (a run under other deps or
    tools is not a PASS), not just each run's own status. *deps_known* is False
    when the export cannot identify the installed deps; that blocks, never passes.
    """
    owners = set(owner_sources)
    standing = latest_reviews(reviews, candidate, harness_sha256(), owners)
    failed = [r for r in standing if r["disposition"] == "FAIL"]
    passed = [r for r in standing if r["disposition"] == "PASS"]
    deciding = failed[-1] if failed else (passed[-1] if passed else None)
    if not gates_ok:
        status, reason = (
            "FAIL",
            "At least one gate failed, or ran in a different environment, on this candidate.",
        )
    elif failed:
        names = ", ".join(r["reviewer"] for r in failed)
        status, reason = "FAIL", f"Reviewer(s) {names} recorded FAIL."
    elif not deps_known:
        status, reason = "BLOCKED", f"Installed deps are unidentified ({DEPS_LOCK_REL} missing)."
    elif candidate.dirty:
        status, reason = "BLOCKED", "Candidate has uncommitted changes; commit before handoff."
    elif not passed:
        status, reason = (
            "BLOCKED",
            "Awaiting an independent reviewer (not the gate owner) for this candidate.",
        )
    else:
        status, reason = (
            "PASS",
            "Gates passed and an independent reviewer accepted. Ready for founder review only.",
        )
    reviewer = deciding["reviewer"] if deciding else None
    return {
        "status": status,
        "reason": reason,
        "candidate_id": candidate.candidate_id,
        "owners": sorted(owners),
        "owner_sources": owner_sources,
        "reviewer": reviewer,
        "review": deciding,
        "reviews_considered": standing,
        "gates": [
            {
                k: r[k]
                for k in (
                    "gate_id",
                    "command",
                    "status",
                    "tool_versions",
                    "environment",
                    "observed_at",
                    "artifact",
                    "owner",
                    "owner_source",
                )
            }
            | {"candidate_id": r["candidate_id"], "reviewer": reviewer}
            for r in included
        ],
        "note": "PASS means ready for founder review only; it never authorises a deploy or merge.",
    }


def build_record(
    *,
    session_runs: list[dict[str, Any]],
    reviews: list[dict[str, Any]],
    candidate: Candidate,
    toolchain: Toolchain,
    out_dir: Path,
    task_id: str | None = None,
    objective: str | None = None,
    other_runs: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """
    *reviews* should hold every session's reviews (see ``session.other_sessions``).
    *other_runs* are runs from other sessions; they never become evidence, but
    whoever ran a gate on this candidate there is an owner and cannot review it.
    """
    harness = harness_sha256()
    included, stale, earlier_failures = runs_for(session_runs, candidate, harness)
    if not included:
        raise EvidenceError(
            f"No gate runs recorded for candidate {candidate.candidate_id} with this harness "
            f"version ({stale} run(s) belong to other candidates or harness code). Run a gate first."
        )
    # Every run on this candidate (any session, superseded or not) feeds the owner
    # set, so every one of them feeds owner_sources and the unverified-owner finding.
    owner_sources = owner_sources_for([*session_runs, *(other_runs or [])], candidate)
    deps_known = toolchain.deps_sha256 is not None
    logs_dir = out_dir / "logs"
    logs_dir.mkdir(parents=True, exist_ok=True)
    target = {
        "artifact": candidate.artifact,
        "revision": candidate.revision,
        "environment": environment_label(toolchain),
    }
    covered: set[str] = set()
    criteria, subtasks, artifacts, findings = [], [], [], []
    for index, run in enumerate(included, start=1):
        src = Path(run["artifact"]["path"])
        if not src.is_file() or sha256_file(src) != run["artifact"]["sha256"]:
            raise EvidenceError(
                f"Log for {run['gate_id']} is missing or changed since the run: {src}"
            )
        _check_log(run, src)
        rel = f"logs/{src.name}"
        shutil.copyfile(src, out_dir / rel)
        artifacts.append({"path": rel, "sha256": run["artifact"]["sha256"]})
        cid = f"C{index}"
        cats = run["categories"] or ["regression"]
        covered.update(cats)
        env_match = run["status"] == "PASS" and run["environment"] == target["environment"]
        passed = env_match and deps_known
        reason = run["status_reason"]
        if run["status"] == "PASS" and not env_match:
            reason = (
                f"Run environment {run['environment']} differs from the export environment; rerun."
            )
        elif env_match and not deps_known:
            reason = (
                f"Installed deps are unidentified ({DEPS_LOCK_REL} missing, deps=none), so this "
                "run is not evidence; run `npm ci` in the theme and rerun."
            )
        criteria.append(
            {
                "id": cid,
                "description": f"`{run['command']}` in {run['cwd']} exits 0 without changing tracked files "
                f"on candidate {run['candidate_id']}",
                "required": True,
                "categories": cats,
                "status": "PASS" if passed else "FAIL",
                "reason": reason,
                "evidence": (
                    [
                        {
                            "method": "command",
                            "reference": rel,
                            "observation": f"{reason}; last line: {run['stdout_tail'] or '(no stdout)'}",
                            "observed_at": run["observed_at"],
                            **target,
                        }
                    ]
                    if passed
                    else []
                ),
            }
        )
        subtasks.append(
            {
                "id": f"T{index}",
                "criterion_ids": [cid],
                "status": "PASS" if passed else "FAIL",
                "observation": f"{run['gate_id']}: {reason}",
            }
        )
        if not passed:
            findings.append(
                {
                    "severity": "P1",
                    "in_scope": True,
                    "status": "OPEN",
                    "description": f"Gate {run['gate_id']} did not pass: {reason}",
                }
            )
    for gate_id, count in sorted(earlier_failures.items()):
        findings.append(
            {
                "severity": "P3",
                "in_scope": True,
                "status": "OPEN",
                "description": f"Gate {gate_id} failed {count} earlier time(s) on this candidate "
                "before the included run; check for flakiness.",
            }
        )
    env_owners = [o for o, src in owner_sources.items() if any(s != "git" for s in src)]
    if env_owners:
        findings.append(
            {
                "severity": "P3",
                "in_scope": True,
                "status": "OPEN",
                "description": f"{UNVERIFIED_OWNER} (owner(s): {', '.join(env_owners)}; "
                "counted over every run on this candidate in any session, superseded or "
                "not); independence checks rely on that name.",
            }
        )
    if candidate.dirty:
        findings.append(
            {
                "severity": "P2",
                "in_scope": True,
                "status": "OPEN",
                "description": f"Uncommitted changes in {len(candidate.dirty_paths)} tracked path(s); "
                "evidence binds to a dirty digest, not a commit.",
            }
        )

    all_pass = all(c["status"] == "PASS" for c in criteria)
    gates_ok = all(
        r["status"] == "PASS" and r["environment"] == target["environment"] for r in included
    )
    toolchain_ok = all(r["toolchain_ok"] for r in included)
    no_mutation = all(not (r["kind"] == "check" and r["changed_paths"]) for r in included)
    claim = "blocked" if not all_pass else ("partial" if candidate.dirty else "verified")
    categories = {
        name: (
            {"applicability": "REQUIRED", "reason": "Exercised by an included gate."}
            if name in covered
            else {
                "applicability": "NOT APPLICABLE",
                "reason": _NOT_APPLICABLE_REASON.get(
                    name,
                    f"No included gate exercises {name}; this record certifies only the listed gates.",
                ),
            }
        )
        for name in CATEGORIES
    }
    record = {
        "schema_version": 1,
        "task_id": task_id or f"flagship2-gates-{candidate.candidate_id}",
        "objective": objective
        or f"The listed SkyyRose Flagship 2 gates pass on candidate {candidate.candidate_id}.",
        "scope": f"Local npm gates of wordpress-theme/skyyrose-flagship-2 at {candidate.revision}",
        "exclusions": list(DEFAULT_EXCLUSIONS),
        "authority": "Local check/build gates only via cli-anything-skyyrose-flagship-2; no deploy, "
        "no paid calls, no pin moves. Stops at evidence for founder review.",
        "claim": claim,
        "target": target,
        "categories": categories,
        "criteria": criteria,
        "phases": {
            "entry": _phase(
                toolchain_ok,
                f"Toolchain {toolchain.versions()} vs pins {toolchain.pins}; "
                f"candidate {candidate.candidate_id} captured before each run.",
            ),
            "task": _phase(
                all_pass,
                f"{sum(c['status'] == 'PASS' for c in criteria)}/{len(criteria)} gates passed.",
            ),
            "integration": _phase(
                no_mutation,
                (
                    "No read-only gate changed a tracked file."
                    if no_mutation
                    else "A read-only gate changed tracked files."
                ),
            ),
            "final": _phase(
                not candidate.dirty, f"Candidate re-read at export: {candidate.revision}."
            ),
        },
        "subtasks": subtasks,
        "findings": findings,
        "artifacts": artifacts,
        "release": {
            "performed": False,
            "authorized": False,
            "authorization_reference": "",
            "action": "",
            "target": "",
            "recovery": "",
            "evidence": [],
        },
        "fashion_theme_team": _ftt_verdict(
            included, gates_ok, reviews, candidate, owner_sources, deps_known
        ),
        "cli": {
            "harness_sha256": harness,
            "stale_runs_excluded": stale,
            "earlier_failures": earlier_failures,
            "candidate": candidate.to_dict(),
            "limitation": "The session ledger is unsigned. Each status is re-derived from its "
            "hashed log, but someone with write access to both could still forge a run. "
            "Reviewer identity is self-declared, and so is every gate owner: SKYYROSE2_GATE_OWNER "
            "is flagged, and a git-sourced owner is whatever the git config files say "
            "(per-command GIT_CONFIG_* injection is ignored; see fashion_theme_team.owner_sources). "
            f"The deps digest covers only {DEPS_LOCK_REL}; edits inside node_modules that "
            "npm does not record there (patch-package, manual edits, npm link) are invisible.",
        },
    }
    return record


def write_record(record: dict[str, Any], out_dir: Path) -> Path:
    path = out_dir / "task-evidence.json"
    path.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    return path


# ---------------------------------------------------------------------------
# God Mode X validation
# ---------------------------------------------------------------------------

CHECKER_REL = "skills/instructions/scripts/check_completion.py"


def find_checker(explicit: str | None = None) -> Path:
    roots = [explicit, os.environ.get("GOD_MODE_X_ROOT"), str(Path.home() / "god-mode-x")]
    for root in roots:
        if root:
            path = Path(root).expanduser() / CHECKER_REL
            if path.is_file():
                return path
    raise EvidenceError(
        "God Mode X checker not found. Clone SkyyRoseCo/god-mode-x and set GOD_MODE_X_ROOT "
        f"(looked for {CHECKER_REL} under {', '.join(r for r in roots if r)})."
    )


def validate_with_god_mode_x(record_path: Path, checker: Path) -> dict[str, Any]:
    proc = subprocess.run(
        [sys.executable, "-I", str(checker), str(record_path)],
        capture_output=True,
        text=True,
        timeout=120,
    )
    try:
        verdict = json.loads(proc.stdout)
    except json.JSONDecodeError as exc:
        raise EvidenceError(
            f"God Mode X checker gave non-JSON output (exit {proc.returncode}): {proc.stderr[-400:]}"
        ) from exc
    verdict["exit_code"] = proc.returncode
    verdict["checker"] = str(checker)
    return verdict
