"""Real PNG output and nontrivial negative source-preservation fixtures."""

import hashlib
from dataclasses import replace

import pytest
from PIL import Image, ImageDraw, PngImagePlugin

from skyyrose.elite_studio.creative.local_composite import (
    AssetRef,
    CompositeError,
    CompositeRequest,
    LocalCompositeGrant,
    Placement,
    compose,
    verify_composite,
)


def asset(root, name, image):
    path = root / name
    image.save(path)
    return AssetRef(name, hashlib.sha256(path.read_bytes()).hexdigest())


@pytest.fixture
def fixture(tmp_path):
    source = Image.new("RGB", (24, 24), (30, 30, 35))
    draw = ImageDraw.Draw(source)
    draw.rectangle((8, 7, 15, 15), fill=(200, 90, 80))  # graphic
    draw.rectangle((2, 19, 21, 21), fill=(245, 245, 240))  # trim
    mask = Image.new("L", source.size, 0)
    ImageDraw.Draw(mask).rectangle((1, 1, 22, 22), fill=128)
    ImageDraw.Draw(mask).rectangle((2, 2, 21, 21), fill=255)
    request = CompositeRequest(
        "test-job",
        asset(tmp_path, "source.png", source),
        asset(tmp_path, "mask.png", mask),
        asset(tmp_path, "background.png", Image.new("RGB", (60, 50), (90, 160, 220))),
        Placement(12, 8),
        "outputs/candidate.png",
    )
    grant = LocalCompositeGrant("test-job", request.source.sha256, "outputs", "owner-request:test")
    return tmp_path, request, grant


def test_actual_artifact_and_immutable_rerun(fixture):
    root, request, grant = fixture
    manifest = compose(request, root=root, grant=grant)
    output = root / request.output_path
    before = output.read_bytes()
    with Image.open(output) as image:
        assert image.size == (60, 50)
        assert image.format == "PNG"
    result = verify_composite(request, manifest, root=root)
    assert result["status"] == "PASS"
    assert result["criteria"]["opaque_interior"]["result"] == "PASS"
    assert result["criteria"]["antialiased_boundary"]["result"] == "PASS"
    assert compose(request, root=root, grant=grant) == manifest
    assert output.read_bytes() == before
    assert manifest["publication_authorized"] is False
    assert manifest["provider_authorized"] is False


@pytest.mark.parametrize("scale", [0.5, 1.25, 1.5])
def test_uniform_scale_preserves_declared_layer(fixture, scale):
    root, request, grant = fixture
    request = replace(request, placement=Placement(3, 4, scale))
    manifest = compose(request, root=root, grant=grant)
    assert verify_composite(request, manifest, root=root)["status"] == "PASS"


@pytest.mark.parametrize(
    "defect,box,color",
    [
        ("altered_logo", (21, 17, 24, 20), (0, 250, 20)),
        ("recolored_product", (15, 11, 31, 25), (60, 30, 150)),
        ("wrong_trim", (14, 27, 33, 29), (0, 0, 0)),
        ("occluded_product", (14, 10, 32, 26), (90, 160, 220)),
        ("boundary_erasure", (13, 9, 13, 26), (90, 160, 220)),
    ],
)
def test_known_defects_fail_even_when_attacker_updates_output_hash(fixture, defect, box, color):
    root, request, grant = fixture
    manifest = compose(request, root=root, grant=grant)
    path = root / request.output_path
    with Image.open(path) as image:
        ImageDraw.Draw(image).rectangle(box, fill=color)
        png = PngImagePlugin.PngInfo()
        png.add(b"sRGB", b"\x00")
        image.save(path, pnginfo=png)
    # Pixel proof must be independent of caller's output hash assertion.
    tampered_manifest = dict(manifest, output_sha256=hashlib.sha256(path.read_bytes()).hexdigest())
    result = verify_composite(request, tampered_manifest, root=root)
    assert result["status"] == "FAIL", defect
    assert any(item["result"] == "FAIL" for item in result["criteria"].values())
    with pytest.raises(CompositeError, match="verification failed"):
        compose(request, root=root, grant=grant)


@pytest.mark.parametrize(
    "mask",
    [
        Image.new("L", (23, 24), 255),
        Image.new("L", (24, 24), 0),
        Image.new("L", (24, 24), 128),
        Image.new("RGB", (24, 24), "white"),
    ],
)
def test_invalid_masks_block(fixture, mask):
    root, request, grant = fixture
    request = replace(request, mask=asset(root, "bad-mask.png", mask))
    with pytest.raises(CompositeError):
        compose(request, root=root, grant=grant)
    assert not (root / request.output_path).exists()


def test_action_grant_cannot_come_from_brief_dict(fixture):
    root, request, grant = fixture
    with pytest.raises(CompositeError, match="Missing trusted"):
        compose(request, root=root)
    with pytest.raises(CompositeError, match="Missing trusted"):
        compose(request, root=root, grant={"action": "local_composite", "approved": True})
    for wrong in (
        replace(grant, job_id="other"),
        replace(grant, action="publish"),
        replace(grant, source_sha256="0" * 64),
        replace(grant, output_root="elsewhere"),
        replace(grant, approval_reference=""),
    ):
        with pytest.raises(CompositeError):
            compose(request, root=root, grant=wrong)


def test_clipping_and_unsupported_transforms_block(fixture):
    root, request, grant = fixture
    for placement in (Placement(-1, 0), Placement(50, 40), Placement(0, 0, 5)):
        with pytest.raises(CompositeError, match="clipping"):
            compose(replace(request, placement=placement), root=root, grant=grant)
    for arguments in ({"rotation": 5}, {"scale_x": 2}, {"warp": [1, 2]}, {"recolor": "blue"}):
        with pytest.raises(TypeError):
            Placement(0, 0, **arguments)


def test_changed_source_and_changed_contract_invalidate(fixture):
    root, request, grant = fixture
    manifest = compose(request, root=root, grant=grant)
    with pytest.raises(CompositeError, match="different source/contract"):
        compose(replace(request, placement=Placement(13, 8)), root=root, grant=grant)
    path = root / request.source.path
    path.write_bytes(path.read_bytes() + b"changed")
    with pytest.raises(CompositeError, match="Source identity changed"):
        verify_composite(request, manifest, root=root)


def test_path_escape_and_incomplete_artifact_fail_closed(fixture):
    root, request, grant = fixture
    with pytest.raises(CompositeError, match="escapes"):
        compose(replace(request, output_path="../outside.png"), root=root, grant=grant)
    (root / "outputs").mkdir()
    (root / request.output_path).write_bytes(b"old output")
    with pytest.raises(CompositeError, match="Incomplete existing"):
        compose(request, root=root, grant=grant)
    assert (root / request.output_path).read_bytes() == b"old output"


def test_opaque_rgba_source_preserves_rgb_without_double_alpha(fixture):
    root, request, grant = fixture
    with Image.open(root / request.source.path) as image:
        rgba = image.convert("RGBA")
    request = replace(request, source=asset(root, "source-rgba.png", rgba))
    grant = replace(grant, source_sha256=request.source.sha256)
    manifest = compose(request, root=root, grant=grant)
    assert verify_composite(request, manifest, root=root)["status"] == "PASS"
    rgba.putalpha(128)
    request = replace(
        request, source=asset(root, "source-translucent.png", rgba), output_path="outputs/other.png"
    )
    grant = replace(grant, source_sha256=request.source.sha256)
    with pytest.raises(CompositeError, match="fully opaque"):
        compose(request, root=root, grant=grant)


def test_manifest_provenance_cannot_be_modified(fixture):
    root, request, grant = fixture
    manifest = compose(request, root=root, grant=grant)
    changed = dict(manifest, inputs={"claim": "made up reference"})
    assert verify_composite(request, changed, root=root)["status"] == "FAIL"


def test_tagged_rgb_conversion_is_declared_and_checked(fixture):
    from PIL import ImageCms

    root, request, grant = fixture
    path = root / "profile-source.png"
    with Image.open(root / request.source.path) as image:
        image.save(
            path, icc_profile=ImageCms.ImageCmsProfile(ImageCms.createProfile("sRGB")).tobytes()
        )
    request = replace(
        request, source=AssetRef(path.name, hashlib.sha256(path.read_bytes()).hexdigest())
    )
    grant = replace(grant, source_sha256=request.source.sha256)
    manifest = compose(request, root=root, grant=grant)
    assert manifest["inputs"]["source"]["color_conversion"] == "embedded ICC to sRGB"
    assert manifest["inputs"]["source"]["icc_sha256"]
    assert verify_composite(request, manifest, root=root)["status"] == "PASS"


@pytest.mark.parametrize(
    "kind,payload",
    [
        (b"iCCP", b"invalid\x00\x00broken-compressed-profile"),
        (b"gAMA", (100000).to_bytes(4, "big")),
        (b"cHRM", b"\x00" * 32),
        (b"sRGB", b"\x00"),
    ],
)
def test_competing_raw_color_chunks_fail_even_with_updated_checksum(fixture, kind, payload):
    import zlib

    root, request, grant = fixture
    manifest = compose(request, root=root, grant=grant)
    path = root / request.output_path
    data = path.read_bytes()
    chunk = (
        len(payload).to_bytes(4, "big")
        + kind
        + payload
        + (zlib.crc32(kind + payload) & 0xFFFFFFFF).to_bytes(4, "big")
    )
    # Insert after IHDR, before IDAT. Decoded RGB pixels are unchanged.
    data = data[:33] + chunk + data[33:]
    path.write_bytes(data)
    changed = dict(manifest, output_sha256=hashlib.sha256(data).hexdigest())
    assessment = verify_composite(request, changed, root=root)
    assert assessment["status"] == "FAIL"
    assert assessment["color_profile"] == "FAIL"


def test_historical_producer_revalidated_by_current_verifier_without_execution(
    fixture, monkeypatch
):
    from skyyrose.elite_studio.creative import local_composite

    root, request, grant = fixture
    # Explicit inert historical source fixture; never imported or executed.
    snapshot = root / "historical-producer.py"
    snapshot.write_text('raise RuntimeError("historical code must never execute")\n')
    old_digest = hashlib.sha256(snapshot.read_bytes()).hexdigest()
    with monkeypatch.context() as patched:
        patched.setattr(local_composite, "_implementation_digest", lambda: old_digest)
        manifest = compose(request, root=root, grant=grant)
    output_before = (root / request.output_path).read_bytes()
    assert verify_composite(request, manifest, root=root)["status"] == "FAIL"
    reference = AssetRef(snapshot.name, old_digest)
    assessment = verify_composite(request, manifest, root=root, producer_implementation=reference)
    assert assessment["status"] == "PASS"
    assert assessment["producer_implementation_sha256"] == old_digest
    assert assessment["verifier_implementation_sha256"] != old_digest
    assert assessment["verification_mode"] == "CURRENT_VERIFIER_HISTORICAL_PRODUCER"
    assert (root / request.output_path).read_bytes() == output_before
    with pytest.raises(CompositeError, match="snapshot identity changed"):
        verify_composite(
            request, manifest, root=root, producer_implementation=AssetRef(snapshot.name, "0" * 64)
        )
    snapshot.write_text("different historical source")
    replacement = AssetRef(snapshot.name, hashlib.sha256(snapshot.read_bytes()).hexdigest())
    assert (
        verify_composite(request, manifest, root=root, producer_implementation=replacement)[
            "status"
        ]
        == "FAIL"
    )


def resized_mask_fixture(root, loss):
    """Original masks satisfy the contract; only their resize loses protection."""
    if loss == "opaque_interior":
        size, scale = 32, 0.125
        mask = Image.new("L", (size, size), 0)
        ImageDraw.Draw(mask).rectangle((12, 12, 19, 19), fill=255)
    else:
        assert loss == "entire_layer"
        size, scale = 256, 0.015625
        mask = Image.new("L", (size, size), 0)
        mask.putpixel((128, 128), 255)
    assert mask.getextrema()[1] == 255
    resized = mask.resize((4, 4), Image.Resampling.BICUBIC)
    assert resized.getextrema()[1] < 255
    assert (resized.getbbox() is None) == (loss == "entire_layer")
    request = CompositeRequest(
        "resize-loss-job",
        asset(root, "source.png", Image.new("RGB", (size, size), (220, 40, 30))),
        asset(root, "mask.png", mask),
        asset(root, "background.png", Image.new("RGB", (12, 12), (20, 80, 160))),
        Placement(3, 4, scale),
        "outputs/resize-loss.png",
    )
    grant = LocalCompositeGrant(
        request.job_id, request.source.sha256, "outputs", "owner-request:offline-regression"
    )
    return request, grant


def receipt_for_resized_fixture(root, request, grant, *, historical=False, background_only=False):
    """Build a self-consistent receipt without invoking the guarded producer.

    Historical implementation bytes are deliberately inert data. Identity helpers
    bind the receipt; fixture PNG construction never calls implementation code.
    """
    from dataclasses import asdict

    from skyyrose.elite_studio.creative import local_composite

    producer = None
    producer_digest = local_composite._implementation_digest()
    if historical:
        snapshot = root / "inert-historical-producer.py"
        snapshot.write_text('raise RuntimeError("historical code must never execute")\n')
        producer_digest = hashlib.sha256(snapshot.read_bytes()).hexdigest()
        producer = AssetRef(snapshot.name, producer_digest)
    _, _, _, metadata = local_composite._inputs(request, root)
    with Image.open(root / request.background.path) as image:
        output = image.copy()
    if not background_only:
        dimensions = tuple(metadata["transform"]["resized_dimensions"])
        with Image.open(root / request.source.path) as source:
            layer = source.resize(dimensions, Image.Resampling.BICUBIC)
        with Image.open(root / request.mask.path) as mask:
            alpha = mask.resize(dimensions, Image.Resampling.BICUBIC)
        output.paste(layer, (request.placement.x, request.placement.y), alpha)
    path = root / request.output_path
    path.parent.mkdir(parents=True)
    png = PngImagePlugin.PngInfo()
    png.add(b"sRGB", b"\x00")
    output.save(path, format="PNG", pnginfo=png, icc_profile=None)
    manifest = {
        "version": "1.0",
        "job_id": request.job_id,
        "request": asdict(request),
        "request_identity": local_composite._request_identity(request, metadata, producer_digest),
        "inputs": metadata,
        "authority": asdict(grant),
        "output_path": request.output_path,
        "output_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        "output_dimensions": list(output.size),
        "output_format": "PNG",
        "publication_authorized": False,
        "provider_authorized": False,
    }
    return manifest, producer


@pytest.mark.parametrize("loss", ["opaque_interior", "entire_layer"])
def test_resized_mask_loss_blocks_before_artifact_reservation(tmp_path, loss):
    request, grant = resized_mask_fixture(tmp_path, loss)
    with pytest.raises(CompositeError, match="opaque protected interior"):
        compose(request, root=tmp_path, grant=grant)
    path = tmp_path / request.output_path
    assert not path.exists()
    assert not path.with_suffix(".png.manifest.json").exists()


@pytest.mark.parametrize("loss", ["opaque_interior", "entire_layer"])
@pytest.mark.parametrize("historical", [False, True])
def test_resized_mask_loss_is_required_verifier_failure(tmp_path, loss, historical):
    request, grant = resized_mask_fixture(tmp_path, loss)
    manifest, producer = receipt_for_resized_fixture(
        tmp_path, request, grant, historical=historical
    )
    path = tmp_path / request.output_path
    before = path.read_bytes()
    result = verify_composite(request, manifest, root=tmp_path, producer_implementation=producer)
    assert result["request_identity"] == "PASS"
    assert result["artifact_identity"] == "PASS"
    assert result["status"] == "FAIL"
    interior = result["criteria"]["opaque_interior"]
    assert interior["pixel_count"] == 0
    assert interior["max_channel_error"] is None
    assert interior["required"] is True
    assert interior["applicable"] is True
    assert interior["result"] == "FAIL"
    assert interior["reason"]
    assert path.read_bytes() == before
    if historical:
        assert result["verification_mode"] == "CURRENT_VERIFIER_HISTORICAL_PRODUCER"


def test_resized_mask_forged_background_receipt_cannot_certify_empty_layer(tmp_path):
    request, grant = resized_mask_fixture(tmp_path, "entire_layer")
    manifest, _ = receipt_for_resized_fixture(tmp_path, request, grant, background_only=True)
    with Image.open(tmp_path / request.output_path) as output:
        with Image.open(tmp_path / request.background.path) as background:
            assert output.tobytes() == background.tobytes()
    result = verify_composite(request, manifest, root=tmp_path)
    assert result["request_identity"] == "PASS"
    assert result["artifact_identity"] == "PASS"
    assert result["status"] == "FAIL"
    assert result["criteria"]["opaque_interior"]["result"] == "FAIL"
    assert result["criteria"]["opaque_interior"]["pixel_count"] == 0


@pytest.mark.parametrize("full_canvas", [False, True])
def test_resized_mask_absent_optional_regions_are_not_applicable(fixture, full_canvas):
    root, request, grant = fixture
    request = replace(request, mask=asset(root, "opaque-mask.png", Image.new("L", (24, 24), 255)))
    if full_canvas:
        request = replace(
            request,
            background=asset(root, "full-canvas.png", Image.new("RGB", (24, 24), "blue")),
            placement=Placement(0, 0),
        )
    manifest = compose(request, root=root, grant=grant)
    result = verify_composite(request, manifest, root=root)
    assert result["status"] == "PASS"
    assert result["criteria"]["opaque_interior"]["result"] == "PASS"
    optional = ["antialiased_boundary"]
    if full_canvas:
        optional.append("unprotected_background")
    for name in optional:
        criterion = result["criteria"][name]
        assert criterion["pixel_count"] == 0
        assert criterion["max_channel_error"] is None
        assert criterion["required"] is False
        assert criterion["applicable"] is False
        assert criterion["result"] == "NOT APPLICABLE"
        assert criterion["reason"]


@pytest.mark.parametrize("size,scale", [(1, 1.0), (16, 0.0625), (16, 0.5), (16, 1.5)])
def test_resized_mask_valid_small_downscale_and_upscale_still_pass(tmp_path, size, scale):
    target = round(size * scale)
    request = CompositeRequest(
        "valid-resize-job",
        asset(tmp_path, "source.png", Image.new("RGB", (size, size), (220, 40, 30))),
        asset(tmp_path, "mask.png", Image.new("L", (size, size), 255)),
        asset(tmp_path, "background.png", Image.new("RGB", (target, target), (20, 80, 160))),
        Placement(0, 0, scale),
        "outputs/valid-resize.png",
    )
    grant = LocalCompositeGrant(
        request.job_id, request.source.sha256, "outputs", "owner-request:offline-regression"
    )
    manifest = compose(request, root=tmp_path, grant=grant)
    result = verify_composite(request, manifest, root=tmp_path)
    assert result["status"] == "PASS"
    assert result["criteria"]["opaque_interior"]["pixel_count"] == target * target
    assert result["criteria"]["opaque_interior"]["result"] == "PASS"
    with Image.open(tmp_path / request.output_path) as output:
        assert output.size == (target, target)
        assert output.getextrema() == ((220, 220), (40, 40), (30, 30))


def test_resized_mask_guard_keeps_pixel_and_receipt_identity_checks(fixture):
    root, request, grant = fixture
    request = replace(request, placement=Placement(3, 4, 0.5))
    manifest = compose(request, root=root, grant=grant)
    path = root / request.output_path
    with Image.open(root / request.background.path) as background:
        png = PngImagePlugin.PngInfo()
        png.add(b"sRGB", b"\x00")
        background.save(path, pnginfo=png, icc_profile=None)
    changed = dict(manifest, output_sha256=hashlib.sha256(path.read_bytes()).hexdigest())
    result = verify_composite(request, changed, root=root)
    assert result["request_identity"] == "PASS"
    assert result["artifact_identity"] == "PASS"
    assert result["status"] == "FAIL"
    assert result["criteria"]["opaque_interior"]["pixel_count"] > 0
    assert result["criteria"]["opaque_interior"]["result"] == "FAIL"
    result = verify_composite(request, dict(changed, request_identity="0" * 64), root=root)
    assert result["request_identity"] == "FAIL"
    assert result["status"] == "FAIL"
