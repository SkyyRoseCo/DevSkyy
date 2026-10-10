"""Unit tests for the decoration-mask deriver.

The mask deriver is the riskiest novel piece of the FLUX synthesis
pipeline — its correctness is what makes decoration drift impossible.
These tests exercise:

    * dossier markdown parsing (region + technique + color extraction)
    * decoration vs. structural entry filtering
    * front/back view scoping
    * gemini-flash response parsing (well-formed, malformed, empty)
    * static-template fallback
    * mask rasterization (binary, dimension-matched, sane coverage)

No network calls — Gemini is fully mocked.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from skyyrose.elite_studio.synthesis.stages.mask_deriver import (
    DECORATION_TECHNIQUES,
    MAX_MASK_AREA_FRAC,
    MIN_MASK_AREA_FRAC,
    BrandingEntry,
    MaskDeriver,
    OverMaskError,
    _coverage_fraction,
    _parse_gemini_boxes,
    _rasterize_boxes,
    filter_decoration_entries,
    parse_branding_entries,
)

# A realistic excerpt from black-rose-crewneck.md style dossier.
SAMPLE_BRANDING_BLOCK = """
### Front
- **front-body** (entire black field, between the crew-neck collar and the waistband): Solid black cotton-fleece body fabric. **Technique:** stitched. **Color:** black.
- **front-center-chest** (~3in tall, centered on the chest below the crew-neck opening): Embossed Black Rose three-rose-cluster, tonal black-on-black pressed into the fabric. **Technique:** embossed. **Color:** black on black.

### Back
- **back-yoke** (~1.75in × 0.75in, top-center back below the crew-neck collar seam): Small woven brand label. **Technique:** woven-label. **Color:** brand-label palette.
- **back-body** (entire back field): Solid black, no decoration. **Technique:** stitched. **Color:** black.

### Sleeves / Collar / Hem / Other
- **collar-inside** (~1.5in × 0.5in interior tag): Branded woven size tag. **Technique:** woven-label. **Color:** brand-label palette.
"""


# --- parse_branding_entries ---


def test_parse_extracts_region_technique_color():
    entries = parse_branding_entries(SAMPLE_BRANDING_BLOCK)
    by_region = {e.region: e for e in entries}
    assert "front-body" in by_region
    assert "front-center-chest" in by_region
    assert by_region["front-center-chest"].technique == "embossed"
    assert "black on black" in by_region["front-center-chest"].color
    assert by_region["back-yoke"].technique == "woven-label"


def test_parse_handles_empty_block():
    assert parse_branding_entries("") == []


def test_parse_skips_non_entry_markdown():
    block = """
## Some heading
Random prose here.
- not an entry
- **front-center-chest** (~3in): Description. **Technique:** embossed. **Color:** black.
"""
    entries = parse_branding_entries(block)
    assert len(entries) == 1
    assert entries[0].region == "front-center-chest"


# --- BrandingEntry.is_decoration & matches_view ---


def test_is_decoration_excludes_stitched():
    e = BrandingEntry("front-body", "body", "stitched", "black")
    assert not e.is_decoration()


@pytest.mark.parametrize("technique", sorted(DECORATION_TECHNIQUES))
def test_is_decoration_includes_all_decoration_techniques(technique: str):
    e = BrandingEntry("front-center-chest", "thing", technique, "black")
    assert e.is_decoration()


def test_matches_view_front_excludes_back_regions():
    e = BrandingEntry("back-yoke", "x", "embossed", "x")
    assert not e.matches_view("front")
    assert e.matches_view("back")


def test_matches_view_unprefixed_appears_in_both():
    e = BrandingEntry("collar-inside", "x", "woven-label", "x")
    assert e.matches_view("front")
    assert e.matches_view("back")


# --- filter_decoration_entries ---


def test_filter_keeps_decoration_drops_structural():
    entries = parse_branding_entries(SAMPLE_BRANDING_BLOCK)
    front = filter_decoration_entries(entries, view="front")
    regions = {e.region for e in front}
    # Decoration entries kept
    assert "front-center-chest" in regions
    # Structural / body entries dropped (technique=stitched)
    assert "front-body" not in regions
    # Back regions dropped from front view
    assert "back-yoke" not in regions
    # Unprefixed regions kept
    assert "collar-inside" in regions


def test_filter_back_view_drops_front_regions():
    entries = parse_branding_entries(SAMPLE_BRANDING_BLOCK)
    back = filter_decoration_entries(entries, view="back")
    regions = {e.region for e in back}
    assert "back-yoke" in regions
    assert "front-center-chest" not in regions


# --- _parse_gemini_boxes ---


def test_parse_gemini_boxes_well_formed():
    raw = """[
        {"region": "front-center-chest", "bbox": [380, 200, 620, 420]},
        {"region": "collar-inside", "bbox": [400, 40, 600, 140]}
    ]"""
    boxes = _parse_gemini_boxes(raw, image_size=(1024, 1024))
    assert len(boxes) == 2
    assert boxes[0]["region"] == "front-center-chest"
    assert boxes[0]["bbox"] == [380, 200, 620, 420]
    assert boxes[0]["source"] == "gemini-flash"


def test_parse_gemini_boxes_strips_code_fence():
    raw = '```json\n[{"region":"x","bbox":[1,2,3,4]}]\n```'
    boxes = _parse_gemini_boxes(raw, image_size=(100, 100))
    assert len(boxes) == 1
    assert boxes[0]["bbox"] == [1, 2, 3, 4]


def test_parse_gemini_boxes_clips_to_image_bounds():
    raw = '[{"region":"x","bbox":[-50, -10, 9999, 9999]}]'
    boxes = _parse_gemini_boxes(raw, image_size=(1024, 1024))
    assert boxes[0]["bbox"] == [0, 0, 1024, 1024]


def test_parse_gemini_boxes_rejects_zero_area():
    raw = '[{"region":"x","bbox":[100, 100, 100, 100]}]'
    with pytest.raises(Exception):
        _parse_gemini_boxes(raw, image_size=(1024, 1024))


def test_parse_gemini_boxes_swaps_inverted():
    """If Gemini returns x2<x1, we sort the coords."""
    raw = '[{"region":"x","bbox":[600, 400, 200, 100]}]'
    boxes = _parse_gemini_boxes(raw, image_size=(1024, 1024))
    assert boxes[0]["bbox"] == [200, 100, 600, 400]


def test_parse_gemini_boxes_empty_response_raises():
    with pytest.raises(Exception):
        _parse_gemini_boxes("", image_size=(1024, 1024))


def test_parse_gemini_boxes_invalid_json_raises():
    with pytest.raises(Exception):
        _parse_gemini_boxes("not json at all", image_size=(1024, 1024))


# --- _rasterize_boxes + _coverage_fraction ---


def test_rasterize_produces_binary_mask_matching_image_size():
    boxes = [{"region": "x", "bbox": [10, 10, 50, 50]}]
    mask = _rasterize_boxes(boxes, image_size=(100, 100))
    assert mask.size == (100, 100)
    assert mask.mode == "L"
    pixels = set(mask.get_flattened_data())
    # Mask must be strictly binary (0 or 255).
    assert pixels.issubset({0, 255})


def test_coverage_fraction_zero_for_empty_mask():
    mask = _rasterize_boxes([], image_size=(100, 100))
    assert _coverage_fraction(mask) == 0.0


def test_coverage_fraction_full_for_full_box():
    boxes = [{"region": "x", "bbox": [0, 0, 100, 100]}]
    mask = _rasterize_boxes(boxes, image_size=(100, 100))
    assert _coverage_fraction(mask) == pytest.approx(1.0, abs=0.01)


def test_coverage_fraction_partial_box():
    # PIL ImageDraw.rectangle is end-inclusive, so [10,10,50,50] → 41×41 = 1681 px
    boxes = [{"region": "x", "bbox": [10, 10, 50, 50]}]
    mask = _rasterize_boxes(boxes, image_size=(100, 100))
    assert 0.15 < _coverage_fraction(mask) < 0.20


# --- MaskDeriver integration (end-to-end with stub PIL image + mock gemini) ---


def _make_blank_jpeg(tmp_path: Path, size: tuple[int, int] = (1024, 1024)) -> Path:
    from PIL import Image

    p = tmp_path / "stage1.jpg"
    Image.new("RGB", size, (200, 200, 200)).save(p)
    return p


def test_derive_uses_gemini_when_available(tmp_path):
    image_path = _make_blank_jpeg(tmp_path)

    def mock_gemini(*, image_path, prompt):
        return '[{"region":"front-center-chest","bbox":[380,200,620,420]}]'

    deriver = MaskDeriver(gemini_caller=mock_gemini)
    dossier = {
        "name": "Black Rose Crewneck",
        "sku": "br-001",
        "branding_block": SAMPLE_BRANDING_BLOCK,
    }
    result = deriver.derive(image_path=image_path, dossier=dossier, view="front", out_dir=tmp_path)
    assert result.method == "gemini-flash"
    assert result.mask_path.exists()
    assert MIN_MASK_AREA_FRAC <= result.coverage_frac <= MAX_MASK_AREA_FRAC
    assert any(b["region"] == "front-center-chest" for b in result.region_boxes)


def test_derive_falls_back_to_static_template_on_gemini_failure(tmp_path):
    image_path = _make_blank_jpeg(tmp_path)

    def failing_gemini(*, image_path, prompt):
        return "garbage not json"  # triggers _GeminiUnusable

    deriver = MaskDeriver(gemini_caller=failing_gemini)
    dossier = {
        "name": "Black Rose Crewneck",
        "sku": "br-001",
        "branding_block": SAMPLE_BRANDING_BLOCK,
    }
    result = deriver.derive(image_path=image_path, dossier=dossier, view="front", out_dir=tmp_path)
    assert result.method == "static-template"
    assert result.mask_path.exists()
    # Static template produces non-empty boxes for known regions
    assert len(result.region_boxes) >= 1
    assert result.coverage_frac > 0


def test_derive_writes_empty_mask_when_no_decoration_entries(tmp_path):
    image_path = _make_blank_jpeg(tmp_path)
    dossier = {
        "name": "Plain Garment",
        "sku": "x-000",
        "branding_block": (
            "- **front-body** (entire field): plain. **Technique:** stitched. **Color:** white."
        ),
    }
    deriver = MaskDeriver()
    result = deriver.derive(image_path=image_path, dossier=dossier, view="front", out_dir=tmp_path)
    assert result.method == "fallback-empty"
    assert result.coverage_frac == 0.0
    assert result.mask_path.exists()


# ── allowed_regions filtering ────────────────────────────────────────────────


def test_derive_allowed_regions_restricts_to_subset(tmp_path):
    image_path = _make_blank_jpeg(tmp_path)

    def mock_gemini(*, image_path, prompt):
        return '[{"region":"front-center-chest","bbox":[380,200,620,420]}]'

    deriver = MaskDeriver(gemini_caller=mock_gemini)
    dossier = {
        "name": "Black Rose Crewneck",
        "sku": "br-001",
        "branding_block": SAMPLE_BRANDING_BLOCK,
    }
    result = deriver.derive(
        image_path=image_path,
        dossier=dossier,
        view="front",
        out_dir=tmp_path,
        allowed_regions=["front-center-chest"],
    )
    regions = {b["region"] for b in result.region_boxes}
    assert "front-center-chest" in regions
    # collar-inside is a decoration entry for front view but not in allowed_regions
    assert "collar-inside" not in regions


def test_derive_allowed_regions_empty_produces_empty_mask(tmp_path):
    image_path = _make_blank_jpeg(tmp_path)
    deriver = MaskDeriver()
    dossier = {
        "name": "Black Rose Crewneck",
        "sku": "br-001",
        "branding_block": SAMPLE_BRANDING_BLOCK,
    }
    result = deriver.derive(
        image_path=image_path,
        dossier=dossier,
        view="front",
        out_dir=tmp_path,
        allowed_regions=[],
    )
    assert result.method == "fallback-empty"
    assert result.coverage_frac == 0.0


def test_derive_raises_over_mask_error_on_excessive_coverage(tmp_path):
    image_path = _make_blank_jpeg(tmp_path)

    def mock_gemini(*, image_path, prompt):
        # Full-image bbox → coverage == 1.0, well above MAX_MASK_AREA_FRAC (0.40)
        return '[{"region":"front-center-chest","bbox":[0,0,1024,1024]}]'

    deriver = MaskDeriver(gemini_caller=mock_gemini)
    dossier = {
        "name": "Black Rose Crewneck",
        "sku": "br-001",
        "branding_block": SAMPLE_BRANDING_BLOCK,
    }
    with pytest.raises(OverMaskError):
        deriver.derive(image_path=image_path, dossier=dossier, view="front", out_dir=tmp_path)
