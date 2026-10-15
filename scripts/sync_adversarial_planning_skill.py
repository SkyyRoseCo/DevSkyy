#!/usr/bin/env python3
"""Sync and verify the maintained adversarial-planning skill copies.

The editable source is ``.claude/skills/adversarial-planning``.  The plugin
package and active ``.agents`` installations are mirrors.  Divergent mirrors
are never overwritten unless ``--replace-divergent`` is explicit, and extra
files are never removed unless ``--prune`` is explicit.
"""

from __future__ import annotations

import argparse
import hashlib
import shutil
import sys
import uuid
from collections.abc import Iterable
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
CANONICAL_RELATIVE = Path(".claude/skills/adversarial-planning")
TRACKED_MIRRORS = (Path("skyyrose-suite/plugins/skyyrose-core/skills/adversarial-planning"),)
PROJECT_ACTIVE_MIRROR = Path(".agents/skills/adversarial-planning")
HOME_ACTIVE_MIRROR = Path(".agents/skills/adversarial-planning")


class SyncError(RuntimeError):
    """Raised when syncing could overwrite content without explicit approval."""


def _tree_hashes(directory: Path) -> dict[str, str]:
    if not directory.is_dir() or directory.is_symlink():
        raise SyncError(f"expected a real skill directory: {directory}")
    hashes: dict[str, str] = {}
    for path in sorted(directory.rglob("*")):
        if "__pycache__" in path.parts or path.suffix in {".pyc", ".pyo"}:
            continue
        if path.is_symlink():
            raise SyncError(f"symlinks are not supported in skill mirrors: {path}")
        if path.is_file():
            rel = path.relative_to(directory).as_posix()
            hashes[rel] = hashlib.sha256(path.read_bytes()).hexdigest()
    return hashes


def _copy_python_caches(source: Path, target: Path) -> None:
    """Preserve mirror-local disposable bytecode while replacing skill files."""
    for path in sorted(source.rglob("*")):
        if "__pycache__" not in path.parts and path.suffix not in {".pyc", ".pyo"}:
            continue
        if path.is_symlink():
            raise SyncError(f"symlinks are not supported in skill caches: {path}")
        destination = target / path.relative_to(source)
        if path.is_dir():
            destination.mkdir(parents=True, exist_ok=True)
        elif path.is_file():
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(path, destination)


def _target_paths(repo_root: Path, home: Path | None = None) -> list[tuple[Path, bool]]:
    """Return (path, required) pairs; only tracked mirrors are required.

    The project ``.agents`` mirror is gitignored, so a fresh clone legitimately lacks
    it: ``--check`` skips it when absent and still compares it when present.
    """
    targets = [(repo_root / path, True) for path in TRACKED_MIRRORS]
    targets.append((repo_root / PROJECT_ACTIVE_MIRROR, False))
    home_path = (home or Path.home()) / HOME_ACTIVE_MIRROR
    if home_path.exists():
        targets.append((home_path, False))
    return targets


def _differences(source_hashes: dict[str, str], target_hashes: dict[str, str]) -> list[str]:
    differences = []
    for relative in sorted(source_hashes.keys() | target_hashes.keys()):
        if source_hashes.get(relative) != target_hashes.get(relative):
            differences.append(relative)
    return differences


def check_mirrors(repo_root: Path = REPO_ROOT, home: Path | None = None) -> list[str]:
    source = repo_root / CANONICAL_RELATIVE
    source_hashes = _tree_hashes(source)
    errors: list[str] = []
    for target, required in _target_paths(repo_root, home):
        if not target.exists():
            if required:
                errors.append(f"required distribution is missing: {target}")
            continue
        try:
            target_hashes = _tree_hashes(target)
        except SyncError as exc:
            errors.append(str(exc))
            continue
        different = _differences(source_hashes, target_hashes)
        if different:
            errors.append(f"{target}: divergent files: {', '.join(different)}")
    return errors


def _sync_plan(
    repo_root: Path,
    home: Path | None,
    *,
    replace_divergent: bool,
    prune: bool,
) -> tuple[Path, dict[str, str], list[Path]]:
    source = repo_root / CANONICAL_RELATIVE
    source_hashes = _tree_hashes(source)
    targets: list[Path] = []
    project_mirror = repo_root / PROJECT_ACTIVE_MIRROR
    for target, required in _target_paths(repo_root, home):
        if target.is_symlink():
            raise SyncError(f"skill mirror must not be a symlink: {target}")
        if not target.exists() and not required and target != project_mirror:
            continue
        if target.exists():
            if not target.is_dir():
                raise SyncError(f"skill mirror is not a directory: {target}")
            target_hashes = _tree_hashes(target)
            differences = _differences(source_hashes, target_hashes)
            if not differences:
                continue
            if not replace_divergent:
                raise SyncError(
                    f"{target} differs ({', '.join(differences)}); review/merge it, then "
                    "rerun with --replace-divergent"
                )
            extra_files = set(target_hashes) - set(source_hashes)
            if extra_files and not prune:
                raise SyncError(
                    f"{target} has target-only files ({', '.join(sorted(extra_files))}); "
                    "review/merge them, then rerun with --prune"
                )
        targets.append(target)
    return source, source_hashes, targets


def sync_mirrors(
    repo_root: Path = REPO_ROOT,
    home: Path | None = None,
    *,
    replace_divergent: bool = False,
    prune: bool = False,
) -> list[Path]:
    # Validate every source/target and every required option before mutation.
    source, source_hashes, targets = _sync_plan(
        repo_root,
        home,
        replace_divergent=replace_divergent,
        prune=prune,
    )
    if not targets:
        return []

    staged: list[dict[str, object]] = []
    swapped: list[dict[str, object]] = []
    try:
        for target in targets:
            target.parent.mkdir(parents=True, exist_ok=True)
            stage = target.parent / f".{target.name}.stage-{uuid.uuid4().hex}"
            backup = target.parent / f".{target.name}.backup-{uuid.uuid4().hex}"
            staged.append(
                {
                    "target": target,
                    "stage": stage,
                    "backup": backup,
                    "had_target": target.exists() or target.is_symlink(),
                    "installed": False,
                }
            )
            shutil.copytree(
                source,
                stage,
                copy_function=shutil.copy2,
                ignore=shutil.ignore_patterns("__pycache__", "*.pyc", "*.pyo"),
            )
            if target.exists():
                _copy_python_caches(target, stage)
            if _tree_hashes(stage) != source_hashes:
                raise SyncError(f"staged copy did not match the canonical source: {target}")

        for item in staged:
            target = item["target"]
            backup = item["backup"]
            stage = item["stage"]
            assert isinstance(target, Path) and isinstance(backup, Path) and isinstance(stage, Path)
            if item["had_target"]:
                target.rename(backup)
            swapped.append(item)
            stage.rename(target)
            item["installed"] = True

    except Exception as exc:
        rollback_errors = []
        for item in reversed(swapped):
            target = item["target"]
            backup = item["backup"]
            assert isinstance(target, Path) and isinstance(backup, Path)
            try:
                if item["installed"] and (target.exists() or target.is_symlink()):
                    shutil.rmtree(target)
                if item["had_target"] and backup.exists():
                    backup.rename(target)
            except OSError as rollback_exc:
                rollback_errors.append(type(rollback_exc).__name__)
        for item in staged:
            stage = item["stage"]
            assert isinstance(stage, Path)
            if stage.exists():
                shutil.rmtree(stage, ignore_errors=True)
        if rollback_errors:
            raise SyncError(
                "mirror update failed and rollback needs attention: " + ", ".join(rollback_errors)
            ) from exc
        if isinstance(exc, SyncError):
            raise
        raise SyncError("mirror update failed; all changed targets were rolled back") from exc

    for item in staged:
        backup = item["backup"]
        assert isinstance(backup, Path)
        if backup.exists():
            shutil.rmtree(backup, ignore_errors=True)
    return targets


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument("--check", action="store_true", help="fail if any maintained mirror drifts")
    action.add_argument("--sync", action="store_true", help="copy canonical files to mirrors")
    parser.add_argument(
        "--replace-divergent",
        action="store_true",
        help="replace a reviewed divergent mirror (never implicit)",
    )
    parser.add_argument(
        "--prune",
        action="store_true",
        help="remove target-only files after they have been reviewed and merged",
    )
    parser.add_argument("--repo", type=Path, default=REPO_ROOT)
    parser.add_argument("--home", type=Path, default=Path.home())
    return parser


def main(argv: Iterable[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        if args.check:
            errors = check_mirrors(args.repo, args.home)
            if errors:
                for error in errors:
                    print(f"DRIFT: {error}", file=sys.stderr)
                return 1
            print("PASS: all present adversarial-planning mirrors match the canonical source")
            return 0

        updated = sync_mirrors(
            args.repo,
            args.home,
            replace_divergent=args.replace_divergent,
            prune=args.prune,
        )
    except SyncError as exc:
        print(f"BLOCKED: {exc}", file=sys.stderr)
        return 2
    for path in updated:
        print(f"SYNCED: {path}")
    if not updated:
        print("PASS: mirrors already match the canonical source")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
