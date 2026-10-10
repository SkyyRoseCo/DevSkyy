from __future__ import annotations

import importlib.util
from pathlib import Path

import numpy as np
import pytest
from PIL import Image

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "build_edge_connected_matte.py"
SPEC = importlib.util.spec_from_file_location("build_edge_connected_matte", SCRIPT)
assert SPEC and SPEC.loader
matte = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(matte)


def test_removes_only_edge_connected_near_white_pixels() -> None:
    rgb = np.full((7, 7, 3), 255, dtype=np.uint8)
    rgb[1:6, 1:6] = (20, 20, 20)
    rgb[2:5, 2:5] = (250, 250, 250)

    background = matte.edge_connected_background(rgb)

    assert background[0, 0]
    assert not background[3, 3], "enclosed garment whites must remain protected"
    assert not background[1, 1]


def test_colored_edge_pixel_is_not_classified_as_background() -> None:
    rgb = np.full((3, 3, 3), 255, dtype=np.uint8)
    rgb[0, 1] = (255, 220, 220)

    background = matte.edge_connected_background(rgb, maximum_chroma=22)

    assert not background[0, 1]
    assert background[0, 0]


def test_build_matte_never_clobbers_existing_evidence(tmp_path: Path) -> None:
    source = tmp_path / "source.png"
    Image.new("RGB", (4, 4), "white").save(source)
    output = tmp_path / "protected.png"
    proof = tmp_path / "proof.png"
    receipt = tmp_path / "receipt.json"
    output.write_bytes(b"existing")

    with pytest.raises(FileExistsError, match="already exists"):
        matte.build_matte(
            source,
            output,
            proof,
            receipt,
            minimum_channel=238,
            maximum_chroma=22,
            role="test",
        )

    assert output.read_bytes() == b"existing"
    assert not proof.exists()
    assert not receipt.exists()
