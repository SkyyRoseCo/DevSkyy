"""Thin, real subprocess wrappers around `git worktree`/status/push-state.

No mocking anywhere in this module's tests (bug-231) — it exists purely to
shell out to git, so faking git would only test the fake.
"""

from __future__ import annotations

import subprocess
from dataclasses import dataclass, field
from enum import StrEnum
from pathlib import Path


def _run(args: list[str], cwd: Path, check: bool = True) -> subprocess.CompletedProcess:
    result = subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True)
    if check and result.returncode != 0:
        raise subprocess.CalledProcessError(result.returncode, args, result.stdout, result.stderr)
    return result


def _reject_option_like(**values: str | Path) -> None:
    """Refuse any caller-supplied value git would parse as an option.

    Refs and paths are passed positionally, so a leading "-" turns data into a
    flag: base_ref="--force" was accepted by `git worktree add`. Checked here,
    where argv is built, so no caller can skip it.
    """
    for name, value in values.items():
        if str(value).startswith("-"):
            raise ValueError(f"{name} must not start with '-': {str(value)!r}")


def _resolves(ref: str, cwd: Path) -> bool:
    return _run(["rev-parse", "--verify", "--quiet", ref], cwd=cwd, check=False).returncode == 0


def _require_local_branch_name(repo_root: Path, branch: str) -> bool:
    """Return whether refs/heads/<branch> exists; refuse anything that is not a
    local branch name.

    `rev-parse --verify <name>` is a REVISION check: tags, SHAs, HEAD and
    remote-tracking refs all pass it. Adopting one of those made
    `git worktree add <path> <name>` produce a DETACHED worktree, whose commits
    belong to no branch — removing it orphaned them (reflog only).
    """
    if _run(["check-ref-format", "--branch", branch], cwd=repo_root, check=False).returncode != 0:
        raise ValueError(f"branch {branch!r} is not a valid branch name")
    if _resolves(f"refs/heads/{branch}", repo_root):
        return True
    if _resolves(branch, repo_root):
        raise ValueError(
            f"branch {branch!r} is not a local branch but resolves to another revision "
            "(tag, commit or remote-tracking ref) — pass a branch name; adopting it would "
            "create a detached worktree whose commits belong to no branch"
        )
    return False


def add_worktree(repo_root: Path, worktree_path: Path, branch: str, base_ref: str) -> None:
    """Create a worktree for `branch`, creating the branch from `base_ref` if it
    doesn't already exist locally (adopts an existing branch instead of failing).
    """
    _reject_option_like(worktree_path=worktree_path, branch=branch, base_ref=base_ref)
    branch_exists = _require_local_branch_name(repo_root, branch)
    if branch_exists:
        _run(["worktree", "add", str(worktree_path), branch], cwd=repo_root)
    else:
        _run(["worktree", "add", "-b", branch, str(worktree_path), base_ref], cwd=repo_root)


def remove_worktree(repo_root: Path, worktree_path: Path, force: bool = False) -> None:
    _reject_option_like(worktree_path=worktree_path)
    args = ["worktree", "remove", str(worktree_path)]
    if force:
        args.append("--force")
    _run(args, cwd=repo_root)


def list_worktrees(repo_root: Path) -> list[dict[str, str]]:
    """Parse `git worktree list --porcelain` into a list of {path, branch, head}."""
    result = _run(["worktree", "list", "--porcelain"], cwd=repo_root)
    entries: list[dict[str, str]] = []
    current: dict[str, str] = {}
    for line in result.stdout.splitlines():
        if not line:
            if current:
                entries.append(current)
                current = {}
            continue
        key, _, value = line.partition(" ")
        if key == "worktree":
            current["path"] = value
        elif key == "HEAD":
            current["head"] = value
        elif key == "branch":
            current["branch"] = value.removeprefix("refs/heads/")
    if current:
        entries.append(current)
    return entries


def is_dirty(worktree_path: Path) -> bool:
    result = _run(["status", "--porcelain"], cwd=worktree_path)
    return bool(result.stdout.strip())


class PushState(StrEnum):
    UP_TO_DATE = "up_to_date"
    UNPUSHED = "unpushed"
    NEVER_PUSHED = "never_pushed"
    NO_NEW_COMMITS = "no_new_commits"
    # "I could not determine this" — distinct from "nothing to report" so the
    # release gate can refuse instead of reading a failed check as a pass.
    UNKNOWN = "unknown"


@dataclass
class PushStatus:
    state: PushState
    unpushed_commits: list[str] = field(default_factory=list)
    reason: str = ""


def _commit_subjects(worktree_path: Path, range_spec: str) -> list[str]:
    """Subjects of the commits in `range_spec`.

    Raises rather than returning [] when git cannot evaluate the range: an empty
    list means "no commits", and a caller that cannot tell that apart from "the
    check failed" turns a failed check into a pass (bug-230 shape).
    """
    result = _run(["log", range_spec, "--oneline"], cwd=worktree_path, check=False)
    if result.returncode != 0:
        raise ValueError(
            f"git could not evaluate the commit range {range_spec!r}: "
            f"{result.stderr.strip() or 'unknown git error'}"
        )
    return [line for line in result.stdout.splitlines() if line.strip()]


def push_status(worktree_path: Path, branch: str, base_ref: str) -> PushStatus:
    """Classify how safe it is to release this worktree, as an explicit state
    rather than letting a missing-upstream git command raise past the caller.

    Uses only locally known remote-tracking refs — does not fetch. A stale
    remote-tracking ref could under-report "unpushed" commits; running
    `git fetch` first gets a fresher answer, but this tool never forces a
    network call on its own.
    """
    _reject_option_like(branch=branch, base_ref=base_ref)
    upstream = _run(
        ["rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{u}"],
        cwd=worktree_path,
        check=False,
    )
    if upstream.returncode == 0:
        upstream_ref = upstream.stdout.strip()
        unpushed = _commit_subjects(worktree_path, f"{upstream_ref}..HEAD")
        if unpushed:
            return PushStatus(
                PushState.UNPUSHED, unpushed, f"{len(unpushed)} commit(s) not on {upstream_ref}"
            )
        return PushStatus(PushState.UP_TO_DATE)

    remote_ref = f"origin/{branch}"
    has_remote_ref = _run(
        ["rev-parse", "--verify", "--quiet", remote_ref], cwd=worktree_path, check=False
    )
    if has_remote_ref.returncode == 0:
        unpushed = _commit_subjects(worktree_path, f"{remote_ref}..HEAD")
        if unpushed:
            return PushStatus(
                PushState.UNPUSHED, unpushed, f"{len(unpushed)} commit(s) not on {remote_ref}"
            )
        return PushStatus(PushState.UP_TO_DATE)

    # No upstream configured and no matching remote-tracking ref at all: the
    # base_ref comparison is the last gate, so an unresolvable base_ref is a
    # refusal, never "no new commits".
    if not _resolves(base_ref, worktree_path):
        return PushStatus(
            PushState.UNKNOWN,
            reason=(
                f"base_ref {base_ref!r} does not resolve in this worktree — cannot tell "
                "whether it holds unpushed commits"
            ),
        )
    ahead_of_base = _commit_subjects(worktree_path, f"{base_ref}..HEAD")
    if not ahead_of_base:
        return PushStatus(
            PushState.NO_NEW_COMMITS, reason=f"branch has no commits beyond {base_ref}"
        )
    return PushStatus(
        PushState.NEVER_PUSHED,
        ahead_of_base,
        f"{len(ahead_of_base)} commit(s) exist only in this worktree, on no remote",
    )
