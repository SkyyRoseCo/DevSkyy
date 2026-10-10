"""Unit tests for the TRELLIS.2 subprocess wrapper.

These are pure offline tests — they exercise the agent's plumbing
(availability probe, safe filename helper, runner-script generation)
without invoking the real CUDA pipeline. The actual GPU run is gated
behind an env flag and a separate live test.
"""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

import pytest

from agents.trellis_agent import TrellisAgent, TrellisAgentError, TrellisRunResult


@pytest.mark.unit
def test_trellis_run_result_dump_has_required_keys() -> None:
    """Result dict must match MeshyGenerationResult shape so round-table
    dispatch stays uniform."""
    result = TrellisRunResult(
        task_id="t1",
        status="completed",
        local_path="/tmp/x.glb",
        duration_seconds=12.5,
    )
    dump = result.model_dump()
    required = {
        "task_id",
        "status",
        "model_urls",
        "thumbnail_url",
        "local_path",
        "format",
        "metadata",
        "duration_seconds",
    }
    assert required.issubset(dump.keys()), f"missing keys: {required - dump.keys()}"
    assert dump["task_id"] == "t1"
    assert dump["status"] == "completed"
    assert dump["format"] == "glb"
    assert dump["duration_seconds"] == 12.5


@pytest.mark.unit
def test_is_available_returns_false_when_repo_missing(tmp_path: Path) -> None:
    """When the TRELLIS repo path doesn't exist, the agent must
    short-circuit availability rather than try to launch a subprocess."""
    agent = TrellisAgent(
        conda_env="nonexistent_env_xyz_should_not_exist",
        trellis_repo_path=tmp_path / "does_not_exist",
    )
    with patch.object(TrellisAgent, "_resolve_conda_python") as resolve:
        assert agent.is_available() is False
        # Second call uses the cached result; neither call may launch Conda.
        assert agent.is_available() is False
    resolve.assert_not_called()


@pytest.mark.unit
def test_is_available_resolves_existing_repo_once(tmp_path: Path) -> None:
    agent = TrellisAgent(trellis_repo_path=tmp_path)
    with patch.object(
        TrellisAgent, "_resolve_conda_python", return_value="/test/python"
    ) as resolve:
        assert agent.is_available() is True
        assert agent.is_available() is True
    resolve.assert_called_once_with(agent.conda_env)
    assert agent._python_path == "/test/python"


@pytest.mark.unit
def test_safe_filename_sanitises_unsafe_chars() -> None:
    assert TrellisAgent._safe_filename("Black/Rose Crewneck!") == "black-rose-crewneck-"[
        :48
    ].rstrip("-")
    assert TrellisAgent._safe_filename("") == "product"
    assert TrellisAgent._safe_filename("////") == "product"
    long_name = "x" * 200
    assert len(TrellisAgent._safe_filename(long_name)) <= 48


@pytest.mark.unit
def test_build_runner_script_embeds_paths_and_params() -> None:
    """The generated runner must inline the input / output paths and
    pipeline tuning knobs — no shell variable substitution allowed since
    we exec the script directly, not through a shell."""
    input_image = Path("/tmp/input image.png")
    output_glb = Path("/tmp/out.glb")
    script = TrellisAgent._build_runner_script(
        input_image=input_image,
        output_glb=output_glb,
        model_repo="microsoft/TRELLIS.2-4B",
        decimation_target=500_000,
        texture_size=2048,
    )
    assert repr(str(input_image)) in script
    assert repr(str(output_glb)) in script
    assert "microsoft/TRELLIS.2-4B" in script
    assert "500000" in script
    assert "2048" in script
    assert "Trellis2ImageTo3DPipeline" in script
    assert "o_voxel.postprocess.to_glb" in script


@pytest.mark.unit
@pytest.mark.asyncio
async def test_image_to_3d_raises_when_unavailable(tmp_path: Path) -> None:
    """If the env is missing, the agent must raise TrellisAgentError
    rather than spawning a doomed subprocess."""
    agent = TrellisAgent(
        conda_env="nonexistent_env_xyz",
        trellis_repo_path=tmp_path / "missing",
    )
    with pytest.raises(TrellisAgentError) as exc:
        await agent.image_to_3d(image_path=str(tmp_path / "x.png"))
    assert "missing" in str(exc.value).lower() or "conda" in str(exc.value).lower()


@pytest.mark.unit
@pytest.mark.asyncio
async def test_image_to_3d_rejects_non_glb_format(tmp_path: Path) -> None:
    agent = TrellisAgent(trellis_repo_path=tmp_path)
    with pytest.raises(TrellisAgentError) as exc:
        await agent.image_to_3d(image_path="anything", output_format="fbx")
    assert "glb" in str(exc.value).lower()


@pytest.mark.unit
def test_resolve_conda_python_honours_override(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The TRELLIS_PYTHON env var must short-circuit conda lookup so
    users can point at a custom env path."""
    fake_py = tmp_path / "python"
    fake_py.write_text("#!/bin/sh\necho py\n")
    fake_py.chmod(0o755)
    monkeypatch.setenv("TRELLIS_PYTHON", str(fake_py))
    resolved = TrellisAgent._resolve_conda_python("anything")
    assert resolved == str(fake_py)


@pytest.mark.unit
def test_resolve_conda_python_returns_none_when_nothing_found(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("TRELLIS_PYTHON", raising=False)
    monkeypatch.delenv("CONDA_EXE", raising=False)
    # Point PATH at an empty dir so `which conda` fails too.
    monkeypatch.setenv("PATH", "/var/empty")
    assert TrellisAgent._resolve_conda_python("trellis_should_not_exist_anywhere") is None
