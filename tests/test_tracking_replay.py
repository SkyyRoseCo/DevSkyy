"""Replay evidence must survive a competing writer during execution."""

import importlib.util
import sys
from pathlib import Path

import pytest


def test_replay_preserves_record_created_after_preflight(tmp_path, monkeypatch):
    script = (
        Path(__file__).resolve().parents[1] / "tasks/e2e-tracking-fixes-20260929/run_local_e2e.py"
    )
    spec = importlib.util.spec_from_file_location("tracking_replay", script)
    runner = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(runner)
    output = tmp_path / "record.json"

    async def competing_writer(directory, checks):
        output.write_text("previous evidence", encoding="utf-8")
        return {}

    monkeypatch.setattr(runner, "website_replay", competing_writer)
    monkeypatch.setattr(runner, "creative_replay", lambda directory, checks: ({}, {}))
    monkeypatch.setattr(
        sys,
        "argv",
        [
            str(script),
            "--fixture-directory",
            str(tmp_path / "fixture"),
            "--record",
            str(output),
        ],
    )
    with pytest.raises(FileExistsError):
        runner.main()
    assert output.read_text(encoding="utf-8") == "previous evidence"
