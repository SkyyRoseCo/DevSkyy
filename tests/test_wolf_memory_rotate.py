"""Tests for scripts/wolf_memory_rotate.py — the handoff-log rotation."""

from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "wolf_memory_rotate.py"
_spec = importlib.util.spec_from_file_location("wolf_memory_rotate", SCRIPT)
rot = importlib.util.module_from_spec(_spec)
assert _spec.loader is not None
_spec.loader.exec_module(rot)


def make_log(path: Path, sections: int = 40, rows: int = 20) -> bytes:
    lines = ["# Memory", ""]
    for s in range(sections):
        lines.append(f"## Session {s:03d}")
        lines += [
            f"| 10:{r:02d} | section {s} row {r} | file.py | done | ~1k |" for r in range(rows)
        ]
        lines.append("")
    data = ("\n".join(lines) + "\n").encode()
    path.write_bytes(data)
    return data


@pytest.fixture
def memory(tmp_path: Path) -> Path:
    (tmp_path / ".wolf").mkdir()
    return tmp_path / ".wolf" / "memory.md"


def archives(memory: Path) -> list[Path]:
    return sorted((memory.parent / "memory-archive").glob("memory-*.md"))


def test_under_threshold_is_a_no_op(memory: Path) -> None:
    data = make_log(memory, sections=2)
    out = rot.rotate(
        memory,
        max_bytes=10_000,
        keep_bytes=5_000,
        archive_dir=memory.parent / "memory-archive",
        dry_run=False,
    )
    assert out["rotated"] is False
    assert memory.read_bytes() == data
    assert archives(memory) == []


def test_rotation_loses_no_bytes_and_cuts_on_a_section(memory: Path) -> None:
    data = make_log(memory)
    out = rot.rotate(
        memory,
        max_bytes=10_000,
        keep_bytes=4_000,
        archive_dir=memory.parent / "memory-archive",
        dry_run=False,
    )
    assert out["rotated"] is True
    kept = memory.read_bytes()
    assert kept.startswith(rot.BANNER)
    tail = kept[len(rot.BANNER) :]
    assert tail.startswith(b"## Session ")  # clean entry boundary
    assert len(kept) < 4_000 + len(rot.BANNER)
    (archive,) = archives(memory)
    body = archive.read_bytes().split(b"\n\n", 1)[1]  # drop the archive title
    assert body + tail == data  # every byte accounted for, in order
    assert data.endswith(b"section 39 row 19 | file.py | done | ~1k |\n\n")
    assert kept.endswith(b"section 39 row 19 | file.py | done | ~1k |\n\n")


def test_second_rotation_does_not_archive_the_banner(memory: Path) -> None:
    make_log(memory)
    adir = memory.parent / "memory-archive"
    rot.rotate(memory, max_bytes=10_000, keep_bytes=4_000, archive_dir=adir, dry_run=False)
    with memory.open("ab") as fh:
        fh.write(
            b"".join(f"| 11:00 | later row {i} | x | done | ~1k |\n".encode() for i in range(200))
        )
    # Force a distinct archive name for the second pass.
    first = archives(memory)[0]
    first.rename(first.with_name("memory-00000000-000000.md"))
    rot.rotate(memory, max_bytes=10_000, keep_bytes=4_000, archive_dir=adir, dry_run=False)
    newest = archives(memory)[-1].read_bytes()
    assert rot.BANNER not in newest
    assert memory.read_bytes().count(rot.BANNER) == 1


def test_dry_run_changes_nothing(memory: Path) -> None:
    data = make_log(memory)
    out = rot.rotate(
        memory,
        max_bytes=10_000,
        keep_bytes=4_000,
        archive_dir=memory.parent / "memory-archive",
        dry_run=True,
    )
    assert out["rotated"] is False and out["archived_bytes"] > 0
    assert memory.read_bytes() == data
    assert archives(memory) == []


def test_appends_during_rotation_are_carried_over(
    memory: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A row appended by another agent between snapshot and swap must survive."""
    make_log(memory)
    late = b"| 12:00 | codex @ main sid:ffffffff | appended mid-rotation | x | done | ~1k |\n"
    real_write = Path.write_bytes

    def write_then_append(self: Path, payload: bytes) -> int:
        n = real_write(self, payload)
        if "memory-archive" in str(self):  # archive written → simulate a concurrent append
            with memory.open("ab") as fh:
                fh.write(late)
        return n

    monkeypatch.setattr(Path, "write_bytes", write_then_append)
    out = rot.rotate(
        memory,
        max_bytes=10_000,
        keep_bytes=4_000,
        archive_dir=memory.parent / "memory-archive",
        dry_run=False,
    )
    assert out["carried_over_bytes"] == len(late)
    assert memory.read_bytes().endswith(late)


def test_cli_rejects_keep_not_below_max(memory: Path) -> None:
    make_log(memory)
    with pytest.raises(SystemExit):
        rot.main(["--file", str(memory), "--max-bytes", "100", "--keep-bytes", "100"])


def test_missing_file_is_reported_not_raised(tmp_path: Path) -> None:
    out = rot.rotate(tmp_path / "nope.md", 100, 50, tmp_path / "a", dry_run=False)
    assert out["rotated"] is False and "not found" in out["reason"]


def test_single_line_file_has_no_boundary(memory: Path) -> None:
    memory.write_bytes(b"x" * 5_000)  # one huge line: nowhere safe to cut
    out = rot.rotate(memory, 1_000, 500, memory.parent / "memory-archive", dry_run=False)
    assert out["rotated"] is False and "boundary" in out["reason"]
    assert memory.read_bytes() == b"x" * 5_000


def test_find_cut_keeps_everything_when_file_fits(memory: Path) -> None:
    assert rot.find_cut(b"# Memory\n| a |\n", keep_bytes=1_000) == 0


def test_cli_quiet_prints_only_on_rotation(
    memory: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    make_log(memory, sections=1)
    rot.main(["--file", str(memory), "--quiet"])
    assert capsys.readouterr().out == ""  # under threshold → silent
    make_log(memory)
    rot.main(["--file", str(memory), "--max-bytes", "10000", "--keep-bytes", "4000", "--quiet"])
    assert '"rotated": true' in capsys.readouterr().out
