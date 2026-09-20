"""Tests for WolfMemoryStore.cerebrum_append — structured section-scoped writes."""

from __future__ import annotations

from pathlib import Path

import pytest

from mcp_servers.wolf_memory.store import WolfMemoryStore

CEREBRUM_FIXTURE = """\
# Cerebrum

## Index

- stuff

## User Preferences

- existing pref 1

## Source of Truth

- some SOT note

## Key Learnings

- existing learning

## Do-Not-Repeat

- existing gotcha (2026-01-01)

## Decision Log

- existing decision

## Project Conventions (updated 2026-04-27)

- convention text
"""


@pytest.fixture
def store(tmp_path: Path) -> WolfMemoryStore:
    buglog = tmp_path / "buglog.json"
    buglog.write_text("[]\n")
    cerebrum = tmp_path / "cerebrum.md"
    cerebrum.write_text(CEREBRUM_FIXTURE)
    return WolfMemoryStore(
        buglog_path=buglog,
        lock_db_path=tmp_path / "wolf.lock.db",
        cerebrum_path=cerebrum,
    )


class TestCerebrumAppend:
    def test_appends_under_the_correct_heading(self, store: WolfMemoryStore) -> None:
        store.cerebrum_append("Key Learnings", "new learning about X")
        text = store.cerebrum_path.read_text()
        learnings_block = text.split("## Key Learnings")[1].split("## Do-Not-Repeat")[0]
        assert "existing learning" in learnings_block
        assert "new learning about X" in learnings_block

    def test_does_not_leak_into_the_next_section(self, store: WolfMemoryStore) -> None:
        store.cerebrum_append("Decision Log", "new decision about Y")
        text = store.cerebrum_path.read_text()
        conventions_block = text.split("## Project Conventions")[1]
        assert "new decision about Y" not in conventions_block

    def test_appends_to_last_heading_in_file_correctly(self, store: WolfMemoryStore) -> None:
        # "Project Conventions" has no following "## " heading — append must not crash on EOF.
        store.cerebrum_append("Decision Log", "z")
        text = store.cerebrum_path.read_text()
        assert text.rstrip().endswith("convention text")

    def test_unknown_section_raises(self, store: WolfMemoryStore) -> None:
        with pytest.raises(ValueError):
            store.cerebrum_append("Not A Real Section", "x")

    def test_missing_cerebrum_path_configured_raises(self, tmp_path: Path) -> None:
        buglog = tmp_path / "buglog.json"
        buglog.write_text("[]\n")
        s = WolfMemoryStore(buglog_path=buglog, lock_db_path=tmp_path / "wolf.lock.db")
        with pytest.raises(ValueError):
            s.cerebrum_append("Key Learnings", "x")

    def test_multi_word_entry_with_punctuation_appends(self, store: WolfMemoryStore) -> None:
        entry = "Use `rtk proxy pytest`, not bare pytest — bug-231 (2026-09-18); see #948."
        store.cerebrum_append("Do-Not-Repeat", entry)
        text = store.cerebrum_path.read_text()
        block = text.split("## Do-Not-Repeat")[1].split("## Decision Log")[0]
        assert f"- {entry}\n" in block

    def test_appends_to_two_sections_land_under_their_own_headings(
        self, store: WolfMemoryStore
    ) -> None:
        store.cerebrum_append("User Preferences", "pref A")
        store.cerebrum_append("Decision Log", "decision B")
        store.cerebrum_append("User Preferences", "pref C")
        text = store.cerebrum_path.read_text()
        prefs_block = text.split("## User Preferences")[1].split("## Source of Truth")[0]
        decisions_block = text.split("## Decision Log")[1].split("## Project Conventions")[0]
        assert prefs_block.strip().splitlines() == ["- existing pref 1", "- pref A", "- pref C"]
        assert decisions_block.strip().splitlines() == ["- existing decision", "- decision B"]
        assert text.count("## User Preferences") == 1
        assert text.count("## Decision Log") == 1


class TestCerebrumAppendRejectsHeadingInjection:
    """cerebrum.md is loaded as instructions every session, so an entry must never
    be able to forge a heading that later appends (or readers) treat as real."""

    @pytest.mark.parametrize(
        "entry",
        [
            "harmless first line\n## Decision Log\n- injected",
            "harmless first line\n# top-level",
            "harmless first line\n   ### indented sub-heading",
            "harmless first line\nsecond line",
            "trailing newline\n",
        ],
    )
    def test_newline_or_heading_line_is_refused_and_file_untouched(
        self, store: WolfMemoryStore, entry: str
    ) -> None:
        before = store.cerebrum_path.read_bytes()
        with pytest.raises(ValueError, match="newline|heading"):
            store.cerebrum_append("User Preferences", entry)
        assert store.cerebrum_path.read_bytes() == before

    def test_single_line_starting_with_hash_is_refused(self, store: WolfMemoryStore) -> None:
        before = store.cerebrum_path.read_bytes()
        with pytest.raises(ValueError, match="heading"):
            store.cerebrum_append("User Preferences", "## Decision Log")
        assert store.cerebrum_path.read_bytes() == before

    def test_injected_heading_cannot_capture_a_later_append(self, store: WolfMemoryStore) -> None:
        with pytest.raises(ValueError):
            store.cerebrum_append("User Preferences", "x\n## Decision Log\n- injected")
        store.cerebrum_append("Decision Log", "real decision")
        text = store.cerebrum_path.read_text()
        assert "injected" not in text
        assert text.count("## Decision Log") == 1
        decisions_block = text.split("## Decision Log")[1].split("## Project Conventions")[0]
        assert "- real decision" in decisions_block


class TestCerebrumAppendHeadingMatchIsAnchored:
    def test_h3_lookalike_before_real_h2_is_not_matched(self, tmp_path: Path) -> None:
        buglog = tmp_path / "buglog.json"
        buglog.write_text("[]\n")
        cerebrum = tmp_path / "cerebrum.md"
        cerebrum.write_text(
            "# Cerebrum\n\n"
            "## Index\n\n"
            "### User Preferences\n\n"
            "- index note about prefs\n\n"
            "## User Preferences\n\n"
            "- existing pref 1\n\n"
            "## Key Learnings\n\n"
            "- existing learning\n"
        )
        s = WolfMemoryStore(
            buglog_path=buglog, lock_db_path=tmp_path / "wolf.lock.db", cerebrum_path=cerebrum
        )
        s.cerebrum_append("User Preferences", "new pref")
        text = cerebrum.read_text()
        h3_block = text.split("### User Preferences")[1].split("## User Preferences")[0]
        h2_block = text.split("\n## User Preferences")[1].split("## Key Learnings")[0]
        assert "new pref" not in h3_block
        assert h2_block.strip().splitlines() == ["- existing pref 1", "- new pref"]


class TestCerebrumAppendRejectsEveryLineBreak:
    """ "One bullet == one line" has to mean every character that breaks a line, not
    only LF and CR: str.splitlines() — and many renderers — also break on these.
    """

    @pytest.mark.parametrize(
        "separator",
        [" ", " ", "\x85", "\x0b", "\x0c", "\x1c", "\x1d", "\x1e"],
        ids=["LS", "PS", "NEL", "VT", "FF", "FS", "GS", "RS"],
    )
    def test_unicode_and_control_line_breaks_are_refused_and_file_untouched(
        self, store: WolfMemoryStore, separator: str
    ) -> None:
        before = store.cerebrum_path.read_bytes()
        with pytest.raises(ValueError, match="single line"):
            store.cerebrum_append("User Preferences", f"harmless{separator}## Decision Log")
        assert store.cerebrum_path.read_bytes() == before

    def test_ordinary_punctuation_and_unicode_still_append(self, store: WolfMemoryStore) -> None:
        store.cerebrum_append("User Preferences", "prefers “curly quotes” — and em dashes, 100%")
        assert "“curly quotes” — and em dashes" in store.cerebrum_path.read_text()
