"""Offline GLB cleanup and decimation with the real Trimesh backend."""

import numpy as np
import pytest
import trimesh
from services.three_d.trellis.config import TrellisConfig
from services.three_d.trellis.garment_aware import GarmentCategory
from services.three_d.trellis.postprocess import MeshPostprocessor


@pytest.mark.parametrize("target", [100, 2000])
def test_glb_cleanup_decimation_and_normalization(tmp_path, monkeypatch, target):
    mesh = trimesh.creation.icosphere(subdivisions=3, radius=4)
    mesh.apply_translation([12, -7, 3])
    original_faces = len(mesh.faces)
    mesh.faces[0] = mesh.faces[0][::-1]
    # A zero-area triangle must be removed without dropping valid geometry.
    mesh.faces = np.vstack([mesh.faces, [0, 0, 0]])
    src = tmp_path / "raw.glb"
    dst = tmp_path / "clean.glb"
    mesh.export(src, file_type="glb")
    config = TrellisConfig(output_dir=str(tmp_path / "output"), cache_dir=str(tmp_path / "cache"))
    post = MeshPostprocessor(config)
    monkeypatch.setattr(post, "_target_polycount", lambda category, sampling: target)
    warnings = []

    count, size = post._clean_and_decimate(
        src=src,
        dst=dst,
        category=GarmentCategory.HOODIE,
        sampling=config.sampling,
        warnings=warnings,
    )

    result = trimesh.load(dst, force="mesh")
    assert warnings == []
    assert count == len(result.faces) == min(target, original_faces)
    assert result.nondegenerate_faces().all()
    assert result.is_winding_consistent
    assert size == dst.stat().st_size > 0
    np.testing.assert_allclose(result.bounds.mean(axis=0), 0, atol=1e-6)
    assert float(result.extents.max()) == pytest.approx(1, abs=1e-6)
