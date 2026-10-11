"""
Candidate identity: which exact tree a gate result is evidence for.

A result is bound to the HEAD commit, the theme subtree object, and a digest
of every tracked change against HEAD. Any edit, commit or checkout produces a
new candidate id, so evidence from an older tree is recognisably stale.
"""

from __future__ import annotations

import hashlib
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from cli_anything.skyyrose_flagship_2.utils.backend import (
    REGISTRY_REL,
    THEME_REL,
    content_digest,
    git,
    load_build_inputs,
    sha256_file,
    tracked_changes,
)


@dataclass(frozen=True)
class Candidate:
    candidate_id: str
    head: str
    branch: str | None
    theme_tree: str
    dirty: bool
    dirty_paths: tuple[str, ...]
    dirty_digest: str | None

    @property
    def revision(self) -> str:
        """Revision string used as the evidence target; never claims a dirty tree is HEAD."""
        if not self.dirty:
            return self.head
        return f"{self.head}+dirty.{(self.dirty_digest or '')[:12]}"

    @property
    def artifact(self) -> str:
        return f"{THEME_REL}@tree:{self.theme_tree}"

    def to_dict(self) -> dict[str, object]:
        out = asdict(self)
        out["dirty_paths"] = list(self.dirty_paths)
        out["revision"] = self.revision
        out["artifact"] = self.artifact
        return out


def capture(repo: Path) -> Candidate:
    head = str(git(repo, "rev-parse", "HEAD")).strip()
    branch = str(git(repo, "branch", "--show-current")).strip() or None
    theme_tree = str(git(repo, "rev-parse", f"HEAD:{THEME_REL}")).strip()
    changed = tracked_changes(repo)
    digest = content_digest(repo, changed) if changed else None
    seed = f"{head}\n{theme_tree}\n{digest or 'clean'}".encode()
    return Candidate(
        candidate_id=hashlib.sha256(seed).hexdigest()[:16],
        head=head,
        branch=branch,
        theme_tree=theme_tree,
        dirty=bool(changed),
        dirty_paths=tuple(sorted(changed)),
        dirty_digest=digest,
    )


def pin_status(repo: Path) -> dict[str, Any]:
    """
    Compare the live product registry with the V2 certification pins (read-only).

    Moving a pin is a founder-approved recertification and is deliberately not
    offered by this CLI.
    """
    inputs = load_build_inputs(repo)
    actual = sha256_file((repo / REGISTRY_REL).resolve())
    pinned_current = inputs.get("current_registry_sha256")
    pinned_input = (inputs.get("input_hashes") or {}).get(REGISTRY_REL)
    in_sync = actual == pinned_current == pinned_input
    return {
        "registry": REGISTRY_REL,
        "actual_sha256": actual,
        "current_registry_sha256": pinned_current,
        "input_hash_sha256": pinned_input,
        "in_sync": in_sync,
        "action": None
        if in_sync
        else "Registry drifted from the V2 pin: check:source-integrity and verify will fail. "
        "Recertifying needs founder approval; this CLI does not move pins.",
    }
