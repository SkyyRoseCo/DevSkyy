#!/usr/bin/env python3
"""Read-only classified Git/checkout inventory and bounded static path references.

JSON goes to stdout. No relocation, deletion, network, credential loading, or
submodule traversal occurs. Duplicate logical bytes are candidates, not savings.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import stat
import subprocess
import sys
import unicodedata
from collections import Counter, defaultdict
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path, PurePosixPath

TEXT_SUFFIXES = {
    ".py",
    ".ts",
    ".tsx",
    ".js",
    ".jsx",
    ".mjs",
    ".cjs",
    ".php",
    ".css",
    ".scss",
    ".html",
    ".md",
    ".json",
    ".yaml",
    ".yml",
    ".toml",
    ".sh",
    ".txt",
    ".xml",
    ".ini",
}
MEDIA_SUFFIXES = {
    ".png",
    ".jpg",
    ".jpeg",
    ".webp",
    ".svg",
    ".gif",
    ".mp4",
    ".mov",
    ".wav",
    ".mp3",
    ".glb",
    ".gltf",
    ".fbx",
    ".obj",
    ".blend",
    ".psd",
    ".ai",
    ".heic",
    ".exr",
}


def git(root: Path, *args: str) -> bytes:
    """NUL-safe callers; avoid optional index writes and external fsmonitor."""
    return subprocess.check_output(
        [
            "git",
            "--no-lazy-fetch",
            "--no-optional-locks",
            "-c",
            "core.fsmonitor=false",
            "-C",
            str(root),
            *args,
        ],
        stderr=subprocess.PIPE,
        env=dict(os.environ, GIT_NO_LAZY_FETCH="1", GIT_TERMINAL_PROMPT="0"),
    )


def decode(value: bytes) -> str:
    return os.fsdecode(value)


def sensitive(path: str) -> bool:
    """Conservative path policy; even credential templates remain metadata-only."""
    parts = PurePosixPath(path).parts
    lowered = [part.casefold() for part in parts]
    if any(
        (parent == ".codex" and name.startswith("config") and name.endswith(".toml"))
        or (parent == ".claude" and name.startswith("settings") and name.endswith(".json"))
        for parent, name in zip(lowered, lowered[1:], strict=False)
    ):
        return True
    return any(
        part.lower().startswith(".env")
        or any(
            word in part.lower()
            for word in ("credential", "secret", "private_key", "private-key", "password")
        )
        or part.lower()
        in {
            ".ssh",
            ".aws",
            ".gnupg",
            "keys",
            "keychain",
            ".git",
            ".netrc",
            ".npmrc",
            ".pypirc",
            ".mcp.json",
            "auth.json",
            "tokens.json",
            "token.json",
        }
        or part.lower().startswith(("id_rsa", "id_ed25519"))
        or part.lower().endswith((".pem", ".key", ".p12", ".pfx", ".keystore"))
        for part in parts
    )


def category(path: str) -> str:
    """Heuristic purpose independent of Git status; never a deletion classifier."""
    p = PurePosixPath(path)
    parts = {part.lower() for part in p.parts}
    if sensitive(path):
        return "sensitive"
    if parts & {"node_modules", "vendor", ".venv", "venv"}:
        return "dependencies"
    if parts & {"__pycache__", ".cache", ".pytest_cache", ".mypy_cache", ".ruff_cache"}:
        return "cache"
    if parts & {"dist", "build", ".next", "coverage"} or p.name.endswith(
        (".min.js", ".min.css", ".map", ".pyc")
    ):
        return "generated_candidate"
    if parts & {"archive", "archives", "_archive", "_prototype"}:
        return "archive_or_prototype"
    if parts & {"tests", "test", "fixtures", "__tests__"}:
        return "tests_or_fixtures"
    if p.suffix.lower() in MEDIA_SUFFIXES:
        return "media_ownership_unresolved"
    if p.suffix.lower() in {".zip", ".tar", ".gz", ".tgz", ".7z"}:
        return "package_or_archive"
    if parts & {"docs"} or p.suffix.lower() == ".md":
        return "documentation"
    if p.name in {"package.json", "pyproject.toml", "composer.json"} or "lock" in p.name:
        return "package_manifest_or_lock"
    if p.suffix.lower() in {".toml", ".ini", ".yaml", ".yml"} or p.name.startswith("Dockerfile"):
        return "configuration_or_build"
    if p.suffix.lower() in TEXT_SUFFIXES:
        return "source_or_text"
    return "unclassified"


def valid_path(path: str) -> str:
    p = PurePosixPath(path)
    if not path or p.is_absolute() or any(part in {"..", ".git"} for part in p.parts):
        raise ValueError("candidate must be a repository-relative path outside Git internals")
    if p.as_posix() != path or "\0" in path:
        raise ValueError("candidate path must be normalized")
    return path


@contextmanager
def parent_fd(root: Path, path: str) -> Iterator[tuple[int, str]]:
    """Open each ancestor by descriptor, refusing symlinks even during races."""
    valid_path(path)
    flags = os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW
    fd = os.open(root, flags)
    try:
        parts = PurePosixPath(path).parts
        for part in parts[:-1]:
            next_fd = os.open(part, flags, dir_fd=fd)
            os.close(fd)
            fd = next_fd
        yield fd, parts[-1]
    finally:
        os.close(fd)


def signature(info: os.stat_result) -> tuple[int, ...]:
    return info.st_dev, info.st_ino, info.st_size, info.st_mtime_ns, info.st_ctime_ns


def read_regular(root: Path, path: str, limit: int) -> bytes:
    if sensitive(path):
        raise ValueError("sensitive paths are metadata-only")
    with parent_fd(root, path) as (parent, name):
        fd = os.open(name, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=parent)
        try:
            before = os.fstat(fd)
            if not stat.S_ISREG(before.st_mode) or before.st_size > limit:
                raise OSError("not a bounded regular file")
            chunks = []
            remaining = limit + 1
            while remaining:
                chunk = os.read(fd, min(65536, remaining))
                if not chunk:
                    break
                chunks.append(chunk)
                remaining -= len(chunk)
            data = b"".join(chunks)
            after = os.fstat(fd)
            current = os.stat(name, dir_fd=parent, follow_symlinks=False)
            if (
                len(data) > limit
                or signature(before) != signature(after)
                or signature(after) != signature(current)
            ):
                raise OSError("file changed during scan")
            return data
        finally:
            os.close(fd)


def collisions(paths: list[str]) -> dict[str, list[list[str]]]:
    result = {}
    for name, transform in (
        ("casefold", str.casefold),
        ("unicode_nfc", lambda s: unicodedata.normalize("NFC", s)),
    ):
        groups = defaultdict(list)
        for path in sorted(set(paths)):
            groups[transform(path)].append(path)
        result[name] = sorted(sorted(group) for group in groups.values() if len(group) > 1)
    return result


def snapshot_inventory(root: Path, revision: str) -> dict:
    sha = (
        git(root, "rev-parse", "--verify", "--end-of-options", revision + "^{commit}")
        .decode()
        .strip()
    )
    entries = []
    duplicates = defaultdict(list)
    sizes = {}
    for row in git(root, "ls-tree", "-r", "-l", "-z", sha).split(b"\0"):
        if not row:
            continue
        meta, raw_path = row.split(b"\t", 1)
        mode, kind, oid, size = meta.split()
        path = decode(raw_path)
        entry = {
            "path": path,
            "git_mode": mode.decode(),
            "kind": kind.decode(),
            "category": category(path),
        }
        if kind == b"blob":
            entry["size_bytes"] = int(size)
        if not sensitive(path):
            entry["git_oid"] = oid.decode()
            if mode in {b"100644", b"100755"}:
                duplicates[oid.decode()].append(path)
                sizes[oid.decode()] = int(size)
        entries.append(entry)
    groups = [
        {
            "git_oid": oid,
            "size_bytes": sizes[oid],
            "paths": sorted(paths),
            "ownership": "unresolved",
        }
        for oid, paths in sorted(duplicates.items())
        if len(paths) > 1
    ]
    return {
        "sha": sha,
        "entries": sorted(entries, key=lambda e: e["path"]),
        "blob_entries": sum(e["kind"] == "blob" for e in entries),
        "gitlink_entries": sum(e["kind"] == "commit" for e in entries),
        "logical_blob_bytes": sum(e.get("size_bytes", 0) for e in entries),
        "duplicate_candidates": groups,
        "repeated_logical_bytes": sum(g["size_bytes"] * (len(g["paths"]) - 1) for g in groups),
        "duplicate_coverage": "regular Git blobs only; sensitive paths and symlinks excluded",
    }


def working_inventory(
    root: Path, hash_worktree: bool, max_file_bytes: int, max_total_bytes: int
) -> tuple[list[dict], dict]:
    paths = {}
    for label, args in (
        ("ignored", ("--others", "--ignored", "--exclude-standard")),
        ("untracked", ("--others", "--exclude-standard")),
        ("tracked", ("--cached",)),
    ):
        for raw in git(root, "ls-files", "-z", *args).split(b"\0"):
            if raw:
                paths[decode(raw).rstrip("/")] = label
    gitlinks = set()
    for row in git(root, "ls-files", "--stage", "-z").split(b"\0"):
        if row:
            meta, raw = row.split(b"\t", 1)
            if meta.startswith(b"160000 "):
                gitlinks.add(decode(raw))
    entries = []
    consumed = 0
    for path, label in sorted(paths.items()):
        entry = {
            "path": path,
            "git_category": label,
            "category": category(path),
            "analysis": "metadata_only",
        }
        if path in gitlinks:
            entry.update(kind="gitlink", status="not_traversed")
        else:
            try:
                with parent_fd(root, path) as (fd, name):
                    info = os.stat(name, dir_fd=fd, follow_symlinks=False)
                kind = (
                    "regular"
                    if stat.S_ISREG(info.st_mode)
                    else (
                        "symlink"
                        if stat.S_ISLNK(info.st_mode)
                        else "directory" if stat.S_ISDIR(info.st_mode) else "special"
                    )
                )
                entry.update(kind=kind, status="present", size_bytes=info.st_size)
                if (
                    hash_worktree
                    and label == "tracked"
                    and kind == "regular"
                    and not sensitive(path)
                ):
                    if info.st_size > max_file_bytes:
                        entry["analysis"] = "file_budget"
                    elif consumed + info.st_size > max_total_bytes:
                        entry["analysis"] = "total_budget"
                    else:
                        consumed += info.st_size
                        try:
                            data = read_regular(root, path, min(max_file_bytes, info.st_size))
                            entry.update(sha256=hashlib.sha256(data).hexdigest(), analysis="hashed")
                        except OSError:
                            entry["analysis"] = "unreadable_or_changed"
            except FileNotFoundError:
                entry.update(kind="unknown", status="missing")
            except OSError as error:
                entry.update(kind="unknown", status="inaccessible", errno=error.errno)
        entries.append(entry)
    return entries, {
        "hash_requested": hash_worktree,
        "hash_bytes_attempted": consumed,
        "hash_scope": "tracked regular non-sensitive files only",
    }


def reference_layer(path: str) -> str:
    if path.startswith("docs/") or path.endswith(".md"):
        return "documentation"
    if (
        path.startswith(".github/")
        or PurePosixPath(path).name.startswith("Dockerfile")
        or category(path) in {"package_manifest_or_lock", "configuration_or_build"}
    ):
        return "build_or_configuration"
    if category(path) == "tests_or_fixtures":
        return "test_or_fixture"
    return "source_runtime_unverified"


def reference_graph(
    root: Path,
    entries: list[dict],
    candidates: list[str],
    max_file_bytes: int,
    max_total_bytes: int,
) -> dict:
    edges, skipped, scanned = [], [], []
    consumed = 0
    for entry in entries:
        path = entry["path"]
        reason = None
        if sensitive(path):
            reason = "sensitive"
        elif entry["git_category"] != "tracked":
            reason = "not_tracked"
        elif entry.get("kind") != "regular" or entry["status"] != "present":
            reason = "not_present_regular"
        elif category(path) in {"dependencies", "cache", "generated_candidate"}:
            reason = "generated_or_dependency"
        elif PurePosixPath(path).suffix.lower() not in TEXT_SUFFIXES and not PurePosixPath(
            path
        ).name.startswith(("Dockerfile", "Makefile")):
            reason = "unsupported_format"
        elif entry["size_bytes"] > max_file_bytes:
            reason = "file_budget"
        elif consumed + entry["size_bytes"] > max_total_bytes:
            reason = "total_budget"
        if reason:
            skipped.append({"path": path, "reason": reason})
            continue
        consumed += entry["size_bytes"]
        try:
            data = read_regular(root, path, min(max_file_bytes, entry["size_bytes"]))
            if b"\0" in data:
                reason = "binary"
            else:
                text = data.decode("utf-8")
        except UnicodeError:
            reason = "non_utf8"
        except OSError:
            reason = "unreadable_or_changed"
        if reason:
            skipped.append({"path": path, "reason": reason})
            continue
        scanned.append(path)
        for number, line in enumerate(text.splitlines(), 1):
            for target in candidates:
                match = (
                    "exact_literal"
                    if target in line
                    else "casefold_literal" if target.casefold() in line.casefold() else None
                )
                if match:
                    edges.append(
                        {
                            "source": path,
                            "line": number,
                            "target": target,
                            "match": match,
                            "layer": reference_layer(path),
                        }
                    )
    return {
        "candidates": candidates,
        "edges": edges,
        "scanned": scanned,
        "skipped": skipped,
        "bytes_attempted": consumed,
        "coverage_complete": not skipped,
        "evidence": "literal substring locations including comments/examples; no runtime proof",
        "unsupported": [
            "relative basename references",
            "computed paths",
            "module imports/aliases",
            "generated rewrites",
            "CMS/database/CDN bindings",
            "external integrations",
            "untracked/ignored content",
        ],
    }


def build_report(
    root: Path,
    snapshot: str = "HEAD",
    hash_worktree: bool = False,
    candidates: list[str] | None = None,
    max_file_bytes: int = 2 * 1024 * 1024,
    max_total_bytes: int = 64 * 1024 * 1024,
) -> dict:
    root = root.resolve(strict=True)
    if (
        Path(decode(git(root, "rev-parse", "--show-toplevel").removesuffix(b"\n"))).resolve()
        != root
    ):
        raise ValueError("root must be the repository top-level")
    if max_file_bytes < 0 or max_total_bytes < 0:
        raise ValueError("budgets cannot be negative")
    candidates = sorted({valid_path(path) for path in (candidates or [])})
    tree = snapshot_inventory(root, snapshot)
    worktree, hash_coverage = working_inventory(
        root, hash_worktree, max_file_bytes, max_total_bytes
    )
    known = {e["path"] for e in tree["entries"]} | {
        e["path"] for e in worktree if e["git_category"] == "tracked"
    }
    if any(path not in known for path in candidates):
        raise ValueError("candidate must be a recorded tracked path")
    totals = defaultdict(lambda: {"files": 0, "apparent_bytes": 0})
    for entry in worktree:
        key = entry["git_category"] + ":" + entry["category"]
        totals[key]["files"] += 1
        if entry.get("kind") in {"regular", "symlink"}:
            totals[key]["apparent_bytes"] += entry.get("size_bytes", 0)
    # Git status/diff can read tracked secrets and execute clean filters.
    # Compare object metadata only; never claim a content-clean working tree.
    index_entries = set()
    for row in git(root, "ls-files", "--stage", "-z").split(b"\0"):
        if row:
            meta, path = row.split(b"\t", 1)
            mode, oid, stage = meta.split()
            index_entries.add((path, mode, oid, stage))
    head_entries = set()
    for row in git(root, "ls-tree", "-r", "-z", "HEAD").split(b"\0"):
        if row:
            meta, path = row.split(b"\t", 1)
            mode, kind, oid = meta.split()
            head_entries.add((path, mode, oid, b"0"))
    return {
        "schema_version": 1,
        "checkout": {
            "head": git(root, "rev-parse", "HEAD").decode().strip(),
            "branch": git(root, "branch", "--show-current").decode().strip() or None,
            "dirty": None,
            "dirty_evidence": "UNKNOWN: working contents not compared; Git status/filter execution prohibited",
            "index_changed_from_head": index_entries != head_entries,
            "untracked_paths_present": any(e["git_category"] == "untracked" for e in worktree),
        },
        "snapshot": tree,
        "worktree": worktree,
        "worktree_summary": dict(sorted(totals.items())),
        "hash_coverage": hash_coverage,
        "path_collisions": collisions(sorted(known)),
        "references": (
            reference_graph(root, worktree, candidates, max_file_bytes, max_total_bytes)
            if candidates
            else {"status": "NOT RUN", "reason": "no candidates selected"}
        ),
        "registered_worktrees": [
            decode(v)
            for v in git(root, "worktree", "list", "--porcelain", "-z").split(b"\0")
            if v.startswith(
                (b"worktree ", b"HEAD ", b"branch ", b"detached", b"locked", b"prunable")
            )
        ],
        "local_branches": git(
            root, "for-each-ref", "--format=%(refname:short) %(objectname)", "refs/heads/"
        )
        .decode()
        .splitlines(),
        "classification_counts": dict(
            sorted(Counter(e["category"] for e in tree["entries"]).items())
        ),
        "limits": {
            "max_file_bytes": max_file_bytes,
            "max_total_bytes_per_analysis": max_total_bytes,
        },
        "limitations": [
            "apparent/logical bytes, not allocated disk usage or savings",
            "purpose classifications are heuristics; ownership unresolved",
            "Git supplies registered paths; submodule/nested contents and submodule dirty status excluded",
            "working inventory is not atomic; runtime/remote consumers NOT RUN",
            "no moves/deletions approved or executed",
        ],
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--snapshot", default="HEAD")
    parser.add_argument("--hash-worktree", action="store_true")
    parser.add_argument("--candidate", action="append", default=[])
    parser.add_argument("--max-file-bytes", type=int, default=2 * 1024 * 1024)
    parser.add_argument("--max-total-bytes", type=int, default=64 * 1024 * 1024)
    parser.add_argument(
        "--require-complete-references",
        action="store_true",
        help="exit 1 on unrun/partial graph; never a removal approval",
    )
    args = parser.parse_args(argv)
    try:
        report = build_report(
            args.root,
            args.snapshot,
            args.hash_worktree,
            args.candidate,
            args.max_file_bytes,
            args.max_total_bytes,
        )
    except (OSError, ValueError, subprocess.CalledProcessError):
        print(
            "inventory failed: invalid repository/path/revision or inaccessible input",
            file=sys.stderr,
        )
        return 2
    print(json.dumps(report, indent=2, sort_keys=True, ensure_ascii=True))
    return int(
        args.require_complete_references
        and not report["references"].get("coverage_complete", False)
    )


if __name__ == "__main__":
    raise SystemExit(main())
