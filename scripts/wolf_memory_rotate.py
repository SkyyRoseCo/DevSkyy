#!/usr/bin/env python3
"""Rotate .wolf/memory.md so the live handoff log stays small.

Every agent reads the tail of ``.wolf/memory.md`` at session start to see where
the others left off (CLAUDE.md / AGENTS.md "Session handoff log"). Left alone it
grows without bound, and agents pay for every byte. When the file exceeds
``--max-bytes``, everything except roughly the last ``--keep-bytes`` moves into
``.wolf/memory-archive/memory-<timestamp>.md``. Nothing is deleted: archived
chunk + kept tail reproduce the original bytes exactly (minus this script's own
banner, which is regenerated).

Safe against concurrent appenders. Agents append with plain ``>>`` and take no
lock, so before swapping the new file in, any bytes appended since the snapshot
are carried over; the swap itself is an atomic ``os.replace``. A sidecar
``flock`` keeps two rotations from interleaving.

Usage:
    python scripts/wolf_memory_rotate.py            # rotate if over threshold
    python scripts/wolf_memory_rotate.py --dry-run  # report what would happen
"""

from __future__ import annotations

import argparse
import fcntl
import json
import os
import sys
import tempfile
from datetime import datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_FILE = REPO_ROOT / ".wolf" / "memory.md"
BANNER = (
    b"# Memory\n\n"
    b"> Live handoff log: newest rows at the bottom. Older entries are archived in\n"
    b"> `.wolf/memory-archive/` (rotated by `scripts/wolf_memory_rotate.py`).\n\n"
)
MAX_CARRYOVER_ROUNDS = 5


def find_cut(data: bytes, keep_bytes: int) -> int:
    """Byte offset where the kept tail starts, on a clean entry boundary.

    Prefers the first ``## `` section header inside the keep window, else the
    first table row (``| ``), else any line start. Returns 0 if nothing to cut.
    """
    start = max(len(data) - keep_bytes, 0)
    if start == 0:
        return 0
    window = data[start:]
    for marker in (b"\n## ", b"\n| ", b"\n"):
        idx = window.find(marker)
        if idx != -1:
            return start + idx + 1
    return 0


def strip_banner(chunk: bytes) -> bytes:
    return chunk[len(BANNER) :] if chunk.startswith(BANNER) else chunk


def rotate(path: Path, max_bytes: int, keep_bytes: int, archive_dir: Path, dry_run: bool) -> dict:
    if not path.is_file():
        return {"rotated": False, "reason": f"{path} not found"}
    size = path.stat().st_size
    if size <= max_bytes:
        return {
            "rotated": False,
            "reason": "under threshold",
            "bytes": size,
            "max_bytes": max_bytes,
        }

    lock_path = path.with_name(path.name + ".rotate.lock")
    with open(lock_path, "w") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        data = path.read_bytes()
        cut = find_cut(data, keep_bytes)
        old = strip_banner(data[:cut])
        if cut == 0 or not old.strip():
            return {"rotated": False, "reason": "no entry boundary to cut at", "bytes": len(data)}

        stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        archive = archive_dir / f"memory-{stamp}.md"
        kept = BANNER + data[cut:]
        result = {
            "rotated": not dry_run,
            "bytes_before": len(data),
            "bytes_after": len(kept),
            "archived_bytes": len(old),
            "archive": str(archive),
        }
        if dry_run:
            return result

        archive_dir.mkdir(parents=True, exist_ok=True)
        header = f"# Memory archive — rotated {stamp}\n\n".encode()
        archive.write_bytes(header + old)

        fd, tmp_name = tempfile.mkstemp(dir=path.parent, prefix=".memory.", suffix=".tmp")
        tmp = Path(tmp_name)
        try:
            with os.fdopen(fd, "wb") as out:
                out.write(kept)
                seen = len(data)
                # Carry over rows other agents appended since the snapshot.
                for _ in range(MAX_CARRYOVER_ROUNDS):
                    with open(path, "rb") as live:
                        live.seek(seen)
                        extra = live.read()
                    if not extra:
                        break
                    out.write(extra)
                    seen += len(extra)
                    result["carried_over_bytes"] = result.get("carried_over_bytes", 0) + len(extra)
                out.flush()
                os.fsync(out.fileno())
            os.chmod(tmp, path.stat().st_mode & 0o777)
            os.replace(tmp, path)
        finally:
            tmp.unlink(missing_ok=True)
        result["bytes_after"] = path.stat().st_size
        return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--file", type=Path, default=DEFAULT_FILE)
    parser.add_argument("--max-bytes", type=int, default=128 * 1024)
    parser.add_argument("--keep-bytes", type=int, default=64 * 1024)
    parser.add_argument("--archive-dir", type=Path, default=None)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--quiet", action="store_true", help="print only when a rotation happens")
    args = parser.parse_args(argv)
    if args.keep_bytes >= args.max_bytes:
        parser.error("--keep-bytes must be smaller than --max-bytes")

    archive_dir = args.archive_dir or args.file.parent / "memory-archive"
    result = rotate(args.file, args.max_bytes, args.keep_bytes, archive_dir, args.dry_run)
    if not args.quiet or result.get("rotated"):
        print(json.dumps(result))
    return 0


if __name__ == "__main__":
    sys.exit(main())
