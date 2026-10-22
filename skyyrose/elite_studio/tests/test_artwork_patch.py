"""Boundary and provenance tests for source-artwork repair, not visual approval."""

from dataclasses import replace
import hashlib

import numpy as np
from PIL import Image
import pytest

from skyyrose.elite_studio.creative.artwork_patch import (
    ArtworkGrant,
    ArtworkPatch,
    ArtworkRepair,
    identity,
    repair,
    verify,
)
from skyyrose.elite_studio.creative.local_composite import AssetRef, CompositeError


@pytest.fixture
def job(tmp_path):
    def save(name, data, mode):
        path = tmp_path / name
        Image.fromarray(data.astype(np.uint8), mode=mode).save(path)
        return AssetRef(name, hashlib.sha256(path.read_bytes()).hexdigest())

    yy, xx = np.indices((200, 200))
    target = save("target.png", np.stack([xx, yy, xx + 20], axis=2), "RGB")
    source = np.zeros((10, 10, 3), dtype=np.uint8)
    source[:, :5, 0] = 220
    source[:, 5:, 2] = 220
    src = save("source.png", source, "RGB")
    alpha = save("alpha.png", np.full((10, 10), 255), "L")
    region = np.zeros((200, 200), dtype=np.uint8)
    region[18:34, 18:34] = 255
    region_ref = save("region.png", region, "L")
    cleanup = np.zeros_like(region)
    cleanup[20:31, 20:31] = 255
    cleanup_ref = save("cleanup.png", cleanup, "L")
    patch = ArtworkPatch(
        "one",
        src,
        (0, 0, 10, 10),
        alpha,
        region_ref,
        cleanup_ref,
        (40, 0),
        ((20, 20), (29, 20), (29, 29), (20, 29)),
    )
    request = ArtworkRepair("owned-job", target, (patch,), "output/frame.png")
    grant = ArtworkGrant(identity(request), "output", "Recorded current owner request")
    return tmp_path, request, grant


def test_actual_source_orientation_and_outside_preservation(job):
    root, request, grant = job
    receipt = repair(request, root=root, grant=grant)
    assert verify(request, receipt, root=root, grant=grant)["status"] == "PASS"
    output = np.array(Image.open(root / request.output))
    assert output[23, 22].tolist() == [220, 0, 0]
    assert output[23, 27].tolist() == [0, 0, 220]
    original = np.array(Image.open(root / request.target.path))
    region = np.array(Image.open(root / request.patches[0].repair_mask.path))
    np.testing.assert_array_equal(output[region == 0], original[region == 0])
    assert receipt["publication_authorized"] is False
    assert receipt["provider_authorized"] is False


def test_wrong_source_hash_refuses_without_output(job):
    root, req, _ = job
    patch = replace(req.patches[0], source=AssetRef("source.png", "0" * 64))
    req = replace(req, patches=(patch,))
    with pytest.raises(CompositeError, match="identity changed"):
        repair(req, root=root, grant=ArtworkGrant(identity(req), "output", "Owner"))
    assert not (root / req.output).exists()


def test_wrong_target_hash_refuses(job):
    root, req, _ = job
    req = replace(req, target=AssetRef("target.png", "0" * 64))
    with pytest.raises(CompositeError, match="identity changed"):
        repair(req, root=root, grant=ArtworkGrant(identity(req), "output", "Owner"))


@pytest.mark.parametrize("change", ["mask", "region", "donor", "quad", "output"])
def test_request_change_cannot_reuse_authority(job, change):
    root, req, grant = job
    patch = req.patches[0]
    if change == "mask":
        patch = replace(patch, source_mask=AssetRef("partial.png", "0" * 64))
    elif change == "region":
        patch = replace(patch, repair_mask=AssetRef("broad.png", "0" * 64))
    elif change == "donor":
        patch = replace(patch, donor_offset=(3, 0))
    elif change == "quad":
        patch = replace(patch, quad=((22, 20), (31, 20), (31, 29), (22, 29)))
    else:
        req = replace(req, output="outside.png")
    req = replace(req, patches=(patch,))
    with pytest.raises(CompositeError, match="authority required"):
        repair(req, root=root, grant=grant)


@pytest.mark.parametrize(
    "quad",
    [
        ((29, 20), (20, 20), (20, 29), (29, 29)),
        ((20, 20), (29, 29), (29, 20), (20, 29)),
        ((20, 20), (20, 20), (20, 20), (20, 20)),
        ((-1, 20), (29, 20), (29, 29), (-1, 29)),
        ((20, 20), (70, 20), (70, 29), (20, 29)),
    ],
)
def test_mirroring_singular_clipping_or_escape_refused(job, quad):
    root, req, _ = job
    req = replace(req, patches=(replace(req.patches[0], quad=quad),))
    with pytest.raises(CompositeError):
        repair(req, root=root, grant=ArtworkGrant(identity(req), "output", "Owner"))


def test_donor_escape_refused(job):
    root, req, _ = job
    req = replace(req, patches=(replace(req.patches[0], donor_offset=(199, 0)),))
    with pytest.raises(CompositeError, match="donor escapes"):
        repair(req, root=root, grant=ArtworkGrant(identity(req), "output", "Owner"))


def test_overlapping_repairs_refused(job):
    root, req, _ = job
    req = replace(req, patches=(req.patches[0], replace(req.patches[0], name="two")))
    with pytest.raises(CompositeError, match="overlapping"):
        repair(req, root=root, grant=ArtworkGrant(identity(req), "output", "Owner"))


def test_output_tampering_refused_and_original_not_overwritten(job):
    root, req, grant = job
    receipt = repair(req, root=root, grant=grant)
    im = Image.open(root / req.output)
    im.putpixel((0, 0), (255, 255, 255))
    im.save(root / req.output)
    result = verify(req, receipt, root=root, grant=grant)
    assert result["status"] == "FAIL"
    assert result["outside_regions_unchanged"] is False
    with pytest.raises(CompositeError, match="Immutable"):
        repair(req, root=root, grant=grant)


def test_cylinder_keeps_whole_source_orientation(job):
    root, req, _ = job
    req = replace(req, patches=(replace(req.patches[0], wrap_degrees=100),))
    grant = ArtworkGrant(identity(req), "output", "Owner")
    receipt = repair(req, root=root, grant=grant)
    im = np.array(Image.open(root / req.output))
    assert im[23, 21, 0] > 200
    assert im[23, 28, 2] > 200
    assert verify(req, receipt, root=root, grant=grant)["status"] == "PASS"


@pytest.mark.parametrize(
    "field,value",
    [
        ("publication_authorized", True),
        ("provider_authorized", True),
        ("producer_sha256", "0" * 64),
        ("request", {}),
        ("authority", {}),
        ("visual_review", "PASS"),
    ],
)
def test_receipt_contract_tampering_fails(job, field, value):
    root, req, grant = job
    receipt = repair(req, root=root, grant=grant)
    receipt[field] = value
    assert verify(req, receipt, root=root, grant=grant)["status"] == "FAIL"


@pytest.mark.parametrize("operation", ["delete", "change"])
def test_cleaned_intermediate_integrity(job, operation):
    root, req, grant = job
    receipt = repair(req, root=root, grant=grant)
    p = (root / req.output).with_suffix(".cleaned.png")
    if operation == "delete":
        p.unlink()
    else:
        with Image.open(p) as source:
            im = source.copy()
        im.putpixel((21, 21), (255, 255, 255))
        im.save(p)
    result = verify(req, receipt, root=root, grant=grant)
    assert result["status"] == "FAIL"
    assert result["cleaned_intermediate"] is False


def test_tagged_target_requires_normalization_before_binding(job):
    from PIL import ImageCms

    root, req, _ = job
    p = root / req.target.path
    with Image.open(p) as source:
        im = source.copy()
    im.save(p, icc_profile=ImageCms.ImageCmsProfile(ImageCms.createProfile("sRGB")).tobytes())
    req = replace(req, target=AssetRef(req.target.path, hashlib.sha256(p.read_bytes()).hexdigest()))
    with pytest.raises(CompositeError, match="Normalize target"):
        repair(req, root=root, grant=ArtworkGrant(identity(req), "output", "Owner"))


@pytest.mark.parametrize("mode", ["local_interpolation", "clone"])
def test_cleanup_modes_keep_outside_identical(job, mode):
    root, req, _ = job
    req = replace(req, patches=(replace(req.patches[0], cleanup_mode=mode),))
    grant = ArtworkGrant(identity(req), "output", "Owner")
    receipt = repair(req, root=root, grant=grant)
    assert verify(req, receipt, root=root, grant=grant)["outside_regions_unchanged"]


def test_unknown_cleanup_mode_refuses(job):
    root, req, _ = job
    req = replace(req, patches=(replace(req.patches[0], cleanup_mode="invent"),))
    with pytest.raises(CompositeError, match="Unsupported fabric"):
        repair(req, root=root, grant=ArtworkGrant(identity(req), "output", "Owner"))


@pytest.mark.parametrize("gain", [1, 1.05])
def test_fractional_edges_do_not_double_attenuate_or_leak_hidden_rgb(job, gain):
    root, req, _ = job
    Image.new("RGB", (200, 200), "white").save(root / "target.png")
    rgb = np.zeros((10, 10, 3), np.uint8)
    rgb[:, :, 0] = 255
    rgb[:, 0] = [0, 0, 255]
    Image.fromarray(rgb).save(root / "source.png")
    alpha = np.full((10, 10), 255, np.uint8)
    alpha[:, 0] = 0
    Image.fromarray(alpha).save(root / "alpha.png")

    def ref(n):
        return AssetRef(n, hashlib.sha256((root / n).read_bytes()).hexdigest())

    patch = replace(
        req.patches[0],
        source=ref("source.png"),
        source_mask=ref("alpha.png"),
        quad=((20.5, 20.5), (29.5, 20.5), (29.5, 29.5), (20.5, 29.5)),
        light_gain=gain,
    )
    req = replace(req, target=ref("target.png"), patches=(patch,))
    grant = ArtworkGrant(identity(req), "output", "Owner")
    repair(req, root=root, grant=grant)
    result = np.array(Image.open(root / req.output))[18:34, 18:34]
    # Independent analytic expectation: red over white stays fully red even
    # at fractional coverage; hidden blue never makes blue != green.
    assert result[:, :, 0].min() == 255
    np.testing.assert_array_equal(result[:, :, 1], result[:, :, 2])
    assert np.any((result[:, :, 1] > 0) & (result[:, :, 1] < 255))


def test_separate_panel_donor_preserves_boundary_ownership(job):
    root, req, _ = job
    mask = np.zeros((200, 200), np.uint8)
    mask[25:, :] = 255
    Image.fromarray(mask).save(root / "split.png")
    ref = AssetRef("split.png", hashlib.sha256((root / "split.png").read_bytes()).hexdigest())
    patch = replace(req.patches[0], split_donor_mask=ref, split_donor_offset=(0, 40))
    req = replace(req, patches=(patch,))
    grant = ArtworkGrant(identity(req), "output", "Owner")
    receipt = repair(req, root=root, grant=grant)
    cleaned = np.array(Image.open((root / req.output).with_suffix(".cleaned.png")))
    assert cleaned[30, 30].tolist() == [30, 70, 50]
    assert cleaned[21, 21].tolist() == [61, 21, 81]
    assert verify(req, receipt, root=root, grant=grant)["status"] == "PASS"


def test_fabric_interpolation_cannot_sample_neighbor_skin(job):
    root, req, _ = job
    im = np.full((200, 200, 3), [190, 90, 50], np.uint8)
    im[:, :33] = [80, 20, 140]
    im[23:30, 25:30] = [240, 240, 240]
    Image.fromarray(im).save(root / "target.png")
    domain = np.zeros((200, 200), np.uint8)
    domain[:, :33] = 255
    Image.fromarray(domain).save(root / "fabric.png")

    def ref(n):
        return AssetRef(n, hashlib.sha256((root / n).read_bytes()).hexdigest())

    patch = replace(
        req.patches[0], cleanup_mode="fabric_interpolation", fabric_mask=ref("fabric.png")
    )
    req = replace(req, target=ref("target.png"), patches=(patch,))
    grant = ArtworkGrant(identity(req), "output", "Owner")
    receipt = repair(req, root=root, grant=grant)
    cleaned = np.array(Image.open((root / req.output).with_suffix(".cleaned.png")))
    assert np.max(np.abs(cleaned[27:30, 26:30].astype(int) - [80, 20, 140])) <= 3
    assert verify(req, receipt, root=root, grant=grant)["outside_regions_unchanged"]


def test_cleaned_intermediate_symlink_cannot_escape_root(job, tmp_path_factory):
    root, req, grant = job
    receipt = repair(req, root=root, grant=grant)
    cleaned = (root / req.output).with_suffix(".cleaned.png")
    outside = tmp_path_factory.mktemp("outside") / "private.png"
    outside.write_bytes(cleaned.read_bytes())
    cleaned.unlink()
    cleaned.symlink_to(outside)
    with pytest.raises(CompositeError, match="escapes allowed root"):
        verify(req, receipt, root=root, grant=grant)


@pytest.mark.parametrize("mode", ["clone", "fabric_interpolation"])
def test_subpixel_panel_coverage_preserves_separate_donors(job, mode):
    root, req, _ = job
    target = np.zeros((200, 200, 3), np.uint8)
    target[25:, :] = 255
    # Old artwork must never become an interpolation donor.
    target[20:31, 20:31] = [230, 30, 30]
    Image.fromarray(target).save(root / "target.png")
    split = np.zeros((200, 200), np.uint8)
    split[25:, :] = 255
    split[24, :] = 128
    Image.fromarray(split).save(root / "split.png")
    Image.new("L", (200, 200), 255).save(root / "fabric.png")

    def ref(name):
        return AssetRef(name, hashlib.sha256((root / name).read_bytes()).hexdigest())

    patch = replace(
        req.patches[0],
        cleanup_mode=mode,
        donor_offset=(40, -15),
        split_donor_mask=ref("split.png"),
        split_donor_offset=(40, 40),
        fabric_mask=ref("fabric.png"),
    )
    req = replace(req, target=ref("target.png"), patches=(patch,))
    grant = ArtworkGrant(identity(req), "output", "Owner")
    receipt = repair(req, root=root, grant=grant)
    cleaned = np.array(Image.open((root / req.output).with_suffix(".cleaned.png")))
    assert np.max(np.abs(cleaned[24, 22:29].astype(int) - 128)) <= 3
    assert cleaned[22, 25].max() <= 3
    assert cleaned[28, 25].min() >= 252
    assert verify(req, receipt, root=root, grant=grant)["status"] == "PASS"
