"""bug-322 follow-up: audit stale SIG-COMMERCE scene-contract bindings.

The sig-commerce-1/2/3 contracts under ``Comfy/scene-contracts/`` (and two
ledger evidence entries) still bind files by absolute path inside the removed
``~/.codex/worktrees/final-scenes-e2e`` worktree. This tool has two phases:

  local phase  — pure git, zero network: for every stale binding, find
                 same-named blobs in the recovery branch, hash them, and
                 compare against the contract's pinned sha256. Also checks
                 whether the repo-relative target already exists locally.
  delegation   — builds an OpenAI Agents API multi-agent session (one
                 subagent per collection) that reviews the local report and
                 drafts per-collection contract patches. PAID and gated:
                 requires --fire, a live access + model probe, the printed
                 manifest, and an explicit y.

This script never edits the contracts; it produces the report a human reviews
before the repoint-and-patch follow-up (mirrors the BR-2/LH-2 precedent).

Examples:
  python scripts/bug322_sig_commerce_audit.py --check-access
  python scripts/bug322_sig_commerce_audit.py --local-only --out /tmp/report.json
  python scripts/bug322_sig_commerce_audit.py --fire
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from collections import Counter
from collections.abc import Callable, Sequence
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Protocol

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from integrations.openai_agents_api import (  # noqa: E402
    AgentsApiClient,
    AgentsApiError,
    AgentSpec,
    MultiAgentConfig,
    PaidCallNotConfirmed,
    SessionRequest,
    format_session_manifest,
)

CONTRACTS_DIR = PROJECT_ROOT / "Comfy" / "scene-contracts"
CONTRACT_GLOB = "sig-commerce-*.json"
LEDGER_NAME = "scene-ooda-ledger.json"
STALE_PREFIX = "/Users/theceo/.codex/worktrees/final-scenes-e2e/DevSkyy/"
RECOVERY_BRANCH = "codex/final-scenes-e2e-20260830"
# gpt-6-astra returns HTTP 404 "That model does not exist" for this account's
# key as of 2026-09-15 (probed live). --fire probes it again and fails with an
# actionable message instead of creating a session that would error.
AGENT_MODEL = "gpt-6-astra"
MAX_SUBAGENTS = 3
COLLECTIONS = ("SIG-COMMERCE-1", "SIG-COMMERCE-2", "SIG-COMMERCE-3")
TASK_LABEL = "bug-322 SIG-COMMERCE contract binding audit"

STATUS_ALREADY_LOCAL = "ALREADY_LOCAL"
STATUS_RECOVERABLE = "RECOVERABLE"
STATUS_HASH_MISMATCH = "HASH_MISMATCH"
STATUS_MISSING = "MISSING"
STATUS_RECOVERABLE_ELSEWHERE = "RECOVERABLE_ELSEWHERE"
RECOVERABLE_STATUSES = frozenset(
    {STATUS_RECOVERABLE, STATUS_ALREADY_LOCAL, STATUS_RECOVERABLE_ELSEWHERE}
)
# --deep feeds cat-file --batch in stdin chunks capped by cumulative blob size so
# a chunk of multi-MB renders never balloons memory.
DEEP_SCAN_CHUNK_BYTES = 64 * 1024 * 1024


class GitRunner(Protocol):
    def __call__(self, args: Sequence[str], stdin: bytes | None = None) -> bytes: ...


def run_git(args: Sequence[str], stdin: bytes | None = None, cwd: Path = PROJECT_ROOT) -> bytes:
    """Run a git plumbing command and return stdout bytes (raises on failure)."""
    completed = subprocess.run(
        ["git", *args], cwd=cwd, input=stdin, capture_output=True, check=True, timeout=600
    )
    return completed.stdout


@dataclass(frozen=True)
class Binding:
    contract: str
    json_path: str
    stale_path: str
    expected_sha256: str | None

    @property
    def relative_target(self) -> str:
        return self.stale_path[len(STALE_PREFIX) :]

    @property
    def basename(self) -> str:
        return self.relative_target.rsplit("/", 1)[-1]

    @property
    def collection(self) -> str:
        for name in COLLECTIONS:
            if f"/{name}/" in self.stale_path:
                return name
        return "UNKNOWN"


@dataclass(frozen=True)
class Candidate:
    path: str
    sha256: str
    match: bool


@dataclass(frozen=True)
class ObjectStoreMatch:
    """A blob anywhere in .git whose bytes hash to the contract's sha256."""

    blob: str
    size: int
    paths: tuple[str, ...]
    commits: tuple[str, ...]
    refs: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "blob": self.blob,
            "size": self.size,
            "paths": list(self.paths),
            "commits": list(self.commits),
            "refs": list(self.refs),
        }


@dataclass(frozen=True)
class BindingResult:
    binding: Binding
    status: str
    branch_candidates: tuple[Candidate, ...]
    branch_match_path: str | None
    worktree: Candidate | None
    object_store: ObjectStoreMatch | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            **asdict(self.binding),
            "collection": self.binding.collection,
            "relative_target": self.binding.relative_target,
            "status": self.status,
            "branch_match_path": self.branch_match_path,
            "branch_candidates": [asdict(c) for c in self.branch_candidates],
            "worktree": asdict(self.worktree) if self.worktree else None,
            "object_store_match": self.object_store.to_dict() if self.object_store else None,
            "proposed_path": (
                self.binding.relative_target if self.status in RECOVERABLE_STATUSES else None
            ),
        }


def _walk(node: Any, path: str, contract: str, out: list[Binding]) -> None:
    if isinstance(node, dict):
        raw = node.get("path")
        if isinstance(raw, str) and raw.startswith(STALE_PREFIX):
            sha = node.get("sha256", node.get("expected_sha256"))
            out.append(Binding(contract, path, raw, sha if isinstance(sha, str) else None))
        for key, value in node.items():
            _walk(value, f"{path}.{key}" if path else key, contract, out)
    elif isinstance(node, list):
        for index, value in enumerate(node):
            _walk(value, f"{path}.{index}", contract, out)


def extract_bindings(contracts_dir: Path = CONTRACTS_DIR) -> list[Binding]:
    """Every ``{"path": <stale>}`` object across the SIG-COMMERCE contracts."""
    found: list[Binding] = []
    for contract_path in sorted(contracts_dir.glob(CONTRACT_GLOB)):
        data = json.loads(contract_path.read_text(encoding="utf-8"))
        _walk(data, "", contract_path.name, found)
    return found


def _walk_strings(node: Any, path: str, out: list[tuple[str, str]]) -> None:
    if isinstance(node, str):
        if node.startswith(STALE_PREFIX):
            out.append((path, node))
    elif isinstance(node, dict):
        for key, value in node.items():
            _walk_strings(value, f"{path}.{key}" if path else key, out)
    elif isinstance(node, list):
        for index, value in enumerate(node):
            _walk_strings(value, f"{path}.{index}", out)


def extract_ledger_references(ledger_path: Path) -> list[Binding]:
    """Bare stale path strings in the OODA ledger (evidence lists; no sha pinned)."""
    if not ledger_path.is_file():
        return []
    data = json.loads(ledger_path.read_text(encoding="utf-8"))
    refs: list[tuple[str, str]] = []
    _walk_strings(data, "", refs)
    return [Binding(ledger_path.name, json_path, raw, None) for json_path, raw in refs]


def branch_exists(git: GitRunner, branch: str) -> bool:
    try:
        git(["rev-parse", "--verify", "--quiet", f"{branch}^{{commit}}"])
    except (subprocess.CalledProcessError, OSError):
        return False
    return True


def branch_head(git: GitRunner, branch: str) -> str:
    return git(["rev-parse", branch]).decode("utf-8").strip()


def list_branch_files(git: GitRunner, branch: str) -> list[str]:
    output = git(["ls-tree", "-r", "--name-only", "-z", branch]).decode("utf-8")
    return [entry for entry in output.split("\0") if entry]


def blob_sha256(git: GitRunner, branch: str, path: str) -> str:
    return hashlib.sha256(git(["cat-file", "blob", f"{branch}:{path}"])).hexdigest()


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _matches(expected: str | None, actual: str) -> bool:
    return True if expected is None else expected.lower() == actual.lower()


def _branch_candidates(
    binding: Binding, git: GitRunner, branch: str, branch_files: Sequence[str]
) -> tuple[Candidate, ...]:
    exact = [p for p in branch_files if p == binding.relative_target]
    by_name = [
        p for p in branch_files if p.rsplit("/", 1)[-1] == binding.basename and p not in exact
    ]
    candidates = []
    for path in [*exact, *by_name]:
        sha = blob_sha256(git, branch, path)
        candidates.append(Candidate(path, sha, _matches(binding.expected_sha256, sha)))
    return tuple(candidates)


def _worktree_candidate(binding: Binding, project_root: Path) -> Candidate | None:
    local = project_root / binding.relative_target
    if not local.is_file():
        return None
    sha = file_sha256(local)
    return Candidate(binding.relative_target, sha, _matches(binding.expected_sha256, sha))


def audit_binding(
    binding: Binding,
    *,
    git: GitRunner,
    branch: str,
    branch_files: Sequence[str],
    project_root: Path,
) -> BindingResult:
    candidates = _branch_candidates(binding, git, branch, branch_files)
    branch_match = next((c.path for c in candidates if c.match), None)
    worktree = _worktree_candidate(binding, project_root)
    if worktree and worktree.match:
        status = STATUS_ALREADY_LOCAL
    elif branch_match:
        status = STATUS_RECOVERABLE
    elif candidates or worktree:
        status = STATUS_HASH_MISMATCH
    else:
        status = STATUS_MISSING
    return BindingResult(binding, status, candidates, branch_match, worktree)


def _list_all_blobs(git: GitRunner) -> list[tuple[str, int]]:
    """Every blob in the object store, reachable or not (packs + loose)."""
    output = git(
        [
            "cat-file",
            "--batch-all-objects",
            "--unordered",
            "--batch-check=%(objectname) %(objecttype) %(objectsize)",
        ]
    ).decode("utf-8")
    blobs = []
    for line in output.splitlines():
        parts = line.split()
        if len(parts) == 3 and parts[1] == "blob":
            blobs.append((parts[0], int(parts[2])))
    return blobs


def _chunks_by_size(blobs: Sequence[tuple[str, int]], cap: int) -> list[list[str]]:
    chunks: list[list[str]] = [[]]
    used = 0
    for oid, size in blobs:
        if chunks[-1] and used + size > cap:
            chunks.append([])
            used = 0
        chunks[-1].append(oid)
        used += size
    return [c for c in chunks if c]


def _sha256_batch(git: GitRunner, oids: Sequence[str]) -> dict[str, str]:
    """sha256 of each blob's content via one ``cat-file --batch`` call."""
    output = git(["cat-file", "--batch"], stdin=("\n".join(oids) + "\n").encode("utf-8"))
    digests: dict[str, str] = {}
    pos = 0
    while pos < len(output):
        newline = output.index(b"\n", pos)
        header = output[pos:newline].split()
        pos = newline + 1
        if len(header) < 3:
            continue
        size = int(header[2])
        digests[header[0].decode("utf-8")] = hashlib.sha256(output[pos : pos + size]).hexdigest()
        pos += size + 1
    return digests


def scan_object_store(git: GitRunner, wanted: set[str]) -> dict[str, tuple[str, int]]:
    """Map each wanted sha256 to (blob oid, size) by hashing every blob in .git."""
    wanted_lower = {w.lower() for w in wanted}
    blobs = _list_all_blobs(git)
    sizes = dict(blobs)
    found: dict[str, tuple[str, int]] = {}
    for chunk in _chunks_by_size(blobs, DEEP_SCAN_CHUNK_BYTES):
        for oid, digest in _sha256_batch(git, chunk).items():
            if digest in wanted_lower and digest not in found:
                found[digest] = (oid, sizes[oid])
        if len(found) == len(wanted_lower):
            break
    return found


def _blob_paths(git: GitRunner) -> dict[str, set[str]]:
    paths: dict[str, set[str]] = {}
    for line in git(["rev-list", "--objects", "--all", "--reflog"]).decode("utf-8").splitlines():
        oid, _, path = line.partition(" ")
        if path:
            paths.setdefault(oid, set()).add(path)
    return paths


def _provenance(git: GitRunner, oid: str, size: int, paths: set[str]) -> ObjectStoreMatch:
    commits = (
        git(
            [
                "log",
                "--all",
                "--reflog",
                f"--find-object={oid}",
                "--format=%H %ad %s",
                "--date=short",
            ]
        )
        .decode("utf-8")
        .splitlines()
    )
    refs: list[str] = []
    for commit in commits:
        refs = (
            git(["for-each-ref", "--contains", commit.split()[0], "--format=%(refname:short)"])
            .decode("utf-8")
            .splitlines()
        )
        if refs:
            break
    return ObjectStoreMatch(oid, size, tuple(sorted(paths)), tuple(commits[:6]), tuple(refs[:12]))


def deep_rescue(results: Sequence[BindingResult], git: GitRunner) -> list[BindingResult]:
    """Upgrade MISSING/HASH_MISMATCH rows whose exact bytes exist anywhere in .git."""
    wanted = {
        r.binding.expected_sha256
        for r in results
        if r.status not in RECOVERABLE_STATUSES and r.binding.expected_sha256
    }
    if not wanted:
        return list(results)
    found = scan_object_store(git, wanted)
    if not found:
        return list(results)
    paths = _blob_paths(git)
    matches = {
        sha: _provenance(git, oid, size, paths.get(oid, set()))
        for sha, (oid, size) in found.items()
    }
    upgraded = []
    for r in results:
        sha = (r.binding.expected_sha256 or "").lower()
        if r.status not in RECOVERABLE_STATUSES and sha in matches:
            r = BindingResult(
                r.binding,
                STATUS_RECOVERABLE_ELSEWHERE,
                r.branch_candidates,
                r.branch_match_path,
                r.worktree,
                matches[sha],
            )
        upgraded.append(r)
    return upgraded


def run_local_audit(
    *,
    contracts_dir: Path = CONTRACTS_DIR,
    project_root: Path = PROJECT_ROOT,
    branch: str = RECOVERY_BRANCH,
    git: GitRunner = run_git,
    deep: bool = False,
) -> dict[str, Any]:
    """Phase 1: pure-git report. Fails closed if the recovery branch is absent.

    ``deep`` additionally hashes every blob in the object store (all refs,
    reflogs, stashes, unreachable objects) for the still-unresolved sha256s.
    """
    if not branch_exists(git, branch):
        raise RuntimeError(
            f"recovery branch {branch!r} not found. Fetch it (git fetch origin {branch}) "
            "or pass --branch; the audit cannot verify hashes without it."
        )
    bindings = extract_bindings(contracts_dir)
    ledger_refs = extract_ledger_references(contracts_dir / LEDGER_NAME)
    branch_files = list_branch_files(git, branch)
    results = [
        audit_binding(
            b, git=git, branch=branch, branch_files=branch_files, project_root=project_root
        )
        for b in [*bindings, *ledger_refs]
    ]
    if deep:
        results = deep_rescue(results, git)
    contract_results = results[: len(bindings)]
    ledger_results = results[len(bindings) :]
    return {
        "schema": "skyyrose.bug322-sig-commerce-audit/1",
        "bug": "bug-322",
        "recovery_branch": branch,
        "recovery_branch_head": branch_head(git, branch),
        "deep_object_store_scan": deep,
        "stale_prefix": STALE_PREFIX,
        "target_form": "repo-relative path under renders/scroll-world/ (gitignored; git add -f)",
        "summary": _summarize(contract_results),
        "contract_bindings": [r.to_dict() for r in contract_results],
        "ledger_references": [r.to_dict() for r in ledger_results],
    }


def _summarize(results: Sequence[BindingResult]) -> dict[str, Any]:
    per_collection: dict[str, dict[str, int]] = {}
    for result in results:
        bucket = per_collection.setdefault(result.binding.collection, Counter())
        bucket[result.status] += 1
    overall = Counter(r.status for r in results)
    return {
        "total_bindings": len(results),
        "by_status": dict(sorted(overall.items())),
        "by_collection": {k: dict(sorted(v.items())) for k, v in sorted(per_collection.items())},
    }


def coordinator_instructions() -> str:
    return (
        "You coordinate a source-binding audit for three SkyyRose scene contracts "
        f"({', '.join(COLLECTIONS)}). The input is a JSON report produced by a local git "
        "audit; you have no filesystem or network access and must reason only over it.\n"
        "Delegate exactly one subagent per collection. Each subagent receives only its "
        "collection's `contract_bindings` entries and must: (1) confirm, for each binding, "
        "whether `status` is consistent with `branch_candidates`/`worktree` evidence "
        "(RECOVERABLE requires a candidate whose sha256 equals expected_sha256); "
        "(2) draft a JSON patch list for its collection only, one entry per binding: "
        "{contract, json_path, old_path, new_path, expected_sha256, sha256_verified, action} "
        "where new_path is the report's `proposed_path` for verified bindings and action is "
        "REPOINT | RESTORE_THEN_REPOINT | HUMAN_RECOVERY_NEEDED; (3) never propose edits to "
        "another collection's contract file and never invent a hash, path, or file.\n"
        "Combine the three subagent outputs into one consolidated report with sections per "
        "collection, list every binding that is not sha256-verified as a blocker, and end "
        "with the exact list of files a human must recover by other means. Do not claim any "
        "binding is verified unless the report's evidence shows a matching sha256."
    )


def build_session_request(report: dict[str, Any], model: str = AGENT_MODEL) -> SessionRequest:
    """Phase 2 request: environment none, 3 parallel subagents, report as input."""
    return SessionRequest(
        agent=AgentSpec(
            model=model,
            instructions=coordinator_instructions(),
            multi_agent=MultiAgentConfig(enabled=True, max_concurrent_subagents=MAX_SUBAGENTS),
        ),
        input=json.dumps(report, indent=1, sort_keys=True),
        environment_type="none",
        stream=True,
    )


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="bug322-sig-commerce-audit",
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument(
        "--check-access", action="store_true", help="Free GET /v1/agents/sessions probe."
    )
    mode.add_argument(
        "--local-only", action="store_true", help="Phase 1 only: git audit, no network."
    )
    mode.add_argument(
        "--fire",
        action="store_true",
        help="Phase 1 then phase 2 (PAID Agents API session; manifest + y required).",
    )
    parser.add_argument(
        "--deep",
        action="store_true",
        help=(
            "Also sha256-scan EVERY blob in .git (all refs, reflogs, stash, unreachable "
            "objects) for still-missing bindings. Local only; ~15s per 8GB of objects."
        ),
    )
    parser.add_argument("--out", type=Path, help="Write the local-phase JSON report here.")
    parser.add_argument("--branch", default=RECOVERY_BRANCH, help="Recovery branch to search.")
    parser.add_argument("--model", default=AGENT_MODEL, help="agent.model for --fire.")
    parser.add_argument(
        "--yes", action="store_true", help="Skip the interactive y/N prompt after the manifest."
    )
    parser.add_argument(
        "--keep-session", action="store_true", help="Do not DELETE the session afterwards."
    )
    parser.add_argument("--contracts-dir", type=Path, default=CONTRACTS_DIR, help=argparse.SUPPRESS)
    parser.add_argument("--project-root", type=Path, default=PROJECT_ROOT, help=argparse.SUPPRESS)
    return parser


def _print_summary(report: dict[str, Any]) -> None:
    summary = report["summary"]
    print(
        f"Recovery branch {report['recovery_branch']} @ {report['recovery_branch_head'][:12]} — "
        f"{summary['total_bindings']} contract bindings"
    )
    for collection, counts in summary["by_collection"].items():
        rendered = ", ".join(f"{k}={v}" for k, v in counts.items())
        print(f"  {collection:<15} {rendered}")
    print(f"  {'TOTAL':<15} " + ", ".join(f"{k}={v}" for k, v in summary["by_status"].items()))
    for entry in report["contract_bindings"]:
        if entry["status"] == STATUS_RECOVERABLE_ELSEWHERE:
            match = entry["object_store_match"]
            where = match["paths"][0] if match["paths"] else f"dangling blob {match['blob']}"
            ref = match["refs"][0] if match["refs"] else "(reflog-only)"
            print(f"    {entry['status']:<21} {entry['contract']} {entry['json_path']}")
            print(f"      ← {ref}:{where}")
        elif entry["status"] not in RECOVERABLE_STATUSES:
            print(f"    {entry['status']:<21} {entry['contract']} {entry['json_path']}")
    ledger = report["ledger_references"]
    if ledger:
        statuses = ", ".join(f"{e['status']}" for e in ledger)
        print(f"  ledger refs     {len(ledger)} ({statuses})")


def _check_access(client_factory: Callable[[], AgentsApiClient]) -> int:
    try:
        with client_factory() as client:
            probe = client.probe_access()
    except AgentsApiError as exc:
        print(f"ERROR: {exc}")
        return 3
    status = probe.status_code if probe.status_code is not None else "no response"
    print(f"Agents API access: {'OK' if probe.ok else 'DENIED'} (HTTP {status}) — {probe.detail}")
    return 0 if probe.ok else 3


def _confirm(prompt_fn: Callable[[str], str]) -> bool:
    return prompt_fn("Proceed? [y/N] ").strip().lower() in ("y", "yes")


def _fire(
    report: dict[str, Any],
    args: argparse.Namespace,
    client_factory: Callable[[], AgentsApiClient],
    prompt_fn: Callable[[str], str],
) -> int:
    request = build_session_request(report, model=args.model)
    try:
        client = client_factory()
    except AgentsApiError as exc:
        print(f"ERROR: {exc}")
        return 3
    with client:
        access = client.probe_access()
        if not access.ok:
            print(f"ABORT: Agents API access denied (HTTP {access.status_code}): {access.detail}")
            return 3
        model = client.probe_model(args.model)
        if not model.ok:
            print(
                f"ABORT: model {args.model!r} is not available to this API key "
                f"(HTTP {model.status_code}): {model.detail}\n"
                "  gpt-6-astra 404'd for this org on 2026-09-15 (likely ID/org verification "
                "gating). Request access in the OpenAI console or re-run with --model <id>."
            )
            return 3
        print(format_session_manifest(request, TASK_LABEL))
        if not args.yes and not _confirm(prompt_fn):
            print("Not confirmed. No session created.")
            return 2
        try:
            outcome = client.create_session(
                request, confirm=True, task_label=TASK_LABEL, echo=lambda _: None
            )
        except (PaidCallNotConfirmed, AgentsApiError) as exc:
            print(f"ERROR: {exc}")
            return 4
        return _report_outcome(client, outcome, keep_session=args.keep_session)


def _report_outcome(client: AgentsApiClient, outcome: Any, *, keep_session: bool) -> int:
    print(f"\nTurn state : {outcome.state.value}")
    print(f"Session id : {outcome.session_id or '(not observed in stream)'}")
    print(f"Subagents  : {len(outcome.subagent_ids)} {list(outcome.subagent_ids)}")
    print(f"Delegations: {[d.item_type for d in outcome.delegations]}")
    if outcome.error:
        print(f"Error      : {outcome.error}")
    if outcome.state.value == "disconnected" and outcome.session_id:
        saved = client.recover_after_disconnect(outcome)
        print(f"Recovered session state (retrieve-before-retry): {json.dumps(saved)[:500]}")
    print("\n=== Agent output ===")
    print(outcome.output_text or "(no output_text in terminal event — inspect events)")
    if outcome.session_id and not keep_session:
        client.delete_session(outcome.session_id)
        print(f"\nDeleted session {outcome.session_id}")
    return 0 if outcome.succeeded else 4


def main(
    argv: list[str] | None = None,
    *,
    git: GitRunner = run_git,
    client_factory: Callable[[], AgentsApiClient] = AgentsApiClient,
    prompt_fn: Callable[[str], str] = input,
) -> int:
    args = _build_parser().parse_args(argv)
    if args.check_access:
        return _check_access(client_factory)
    try:
        report = run_local_audit(
            contracts_dir=args.contracts_dir,
            project_root=args.project_root,
            branch=args.branch,
            git=git,
            deep=args.deep,
        )
    except (RuntimeError, subprocess.CalledProcessError) as exc:
        print(f"ERROR: {exc}")
        return 1
    _print_summary(report)
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print(f"Report written: {args.out}")
    if args.local_only:
        print("\nLOCAL ONLY — no OpenAI calls made.")
        return 0
    return _fire(report, args, client_factory, prompt_fn)


if __name__ == "__main__":
    sys.exit(main())
