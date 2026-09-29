"""Fabric classification from founder registry prose + lossless sheen/anisotropy patching."""

from __future__ import annotations

import pytest

from skyyrose.core.product_registry import load_registry
from skyyrose.elite_studio.pipeline3d.glb_container import read_glb, write_glb
from skyyrose.elite_studio.pipeline3d.glb_materials import (
    SHEEN_PRESETS,
    AnisotropyParams,
    FabricClass,
    MaterialPatchError,
    SheenPreset,
    UnclassifiedFabricError,
    apply_fabric_extensions,
    classify_fabric,
    classify_product,
    strip_negations,
)
from tests.elite_studio.pipeline3d.glb_fixture import (
    build_triangle_glb,
    pack_glb,
    triangle_document,
)

# Verbatim founder specifications (registry products[sku].garment.materials.specification).
BR_006 = (
    "Black satin bomber-style hooded jacket — **lustrous black satin** exterior fabric, "
    "**plush black sherpa** interior lining (visible inside the body and inside the hood). "
    "Hooded (sherpa-lined hood). **Front closure is a ZIPPER underneath with a button-overlap "
    "storm-flap covering it** — the zipper runs the full center-front length, and a "
    "buttoned/snapped storm flap overlaps the zipper line for a clean satin front (this is a "
    "two-layer placket). NOT a denim jacket. NOT a fleece hoodie. NOT a leather jacket."
)
SG_015 = (
    "Two-piece matching set sold as a single SKU — **lightweight nylon zip-front hooded "
    "windbreaker JACKET + matching nylon track-style PANTS**. Both pieces are constructed from "
    "smooth lightweight **nylon windbreaker fabric** (NOT cotton-fleece — this is the lighter "
    "water-resistant sibling of the Mint & Lavender Hoodie set). NOT cotton-fleece (this is the "
    "windbreaker variant, not the cousin sg-006 fleece hoodie + sg-014 fleece pants). NOT a "
    "fleece hoodie (different fabric, different weight, different construction)."
)
SG_011 = "White 100% cotton construction."
BR_011 = (
    "Solid **black** base body fabric with **teal/turquoise (cyan)** accent\ncolorway. "
    "Mid-weight knit fabric, hockey-jersey-weight. NOT a sherpa jacket\n(distinct from br-006 "
    "which is a separate satin bomber)."
)
LH_005 = (
    "A **black PU/faux-leather fanny pack (waist-belt bag / cross-body sling)** — small "
    "rectangular bag body in pebbled-textured black faux-leather, single front-pocket with a "
    "horizontal zipper closure, **adjustable black nylon webbing strap** with a **plastic "
    "quick-release buckle** (clip-on/clip-off side-release buckle), worn at the waist or across "
    "the chest. NOT a leather handbag."
)


@pytest.mark.parametrize(
    ("spec", "expected"),
    [
        (BR_006, FabricClass.SATIN),
        (SG_015, FabricClass.NYLON),
        (SG_011, FabricClass.COTTON),
        (BR_011, FabricClass.JERSEY),
        (LH_005, FabricClass.FAUX_LEATHER),
    ],
    ids=["br-006-satin", "sg-015-nylon", "sg-011-cotton", "br-011-jersey", "lh-005-leather"],
)
def test_founder_specs_classify_by_exterior_fabric(spec, expected):
    assert classify_fabric(spec).fabric_class is expected


def test_negated_clauses_never_classify():
    stripped = strip_negations(BR_006)
    assert "fleece" not in stripped
    assert "leather" not in stripped
    assert "satin" in stripped


def test_negation_inside_parentheses_stops_at_closing_paren():
    stripped = strip_negations("Soft mesh body (NOT cotton — heavier cotton elsewhere) shell.")
    assert "cotton" not in stripped
    assert "shell" in stripped


def test_negation_span_swallows_trailing_parenthetical():
    assert "satin" not in strip_negations(BR_011)
    assert classify_fabric("NOT a satin jacket (satin is elsewhere). Nylon.").keyword == "nylon"


def test_markdown_emphasis_and_newlines_are_normalised():
    match = classify_fabric("Mid-weight\n**knit jersey** fabric.")
    assert (match.fabric_class, match.keyword) == (FabricClass.JERSEY, "jersey")


def test_unmatched_specification_fails_closed():
    with pytest.raises(UnclassifiedFabricError):
        classify_fabric("Solid black base fabric.")


def test_fully_negated_specification_fails_closed():
    with pytest.raises(UnclassifiedFabricError):
        classify_fabric("NOT cotton. NOT fleece.")


def test_every_registry_product_classifies():
    products = load_registry()["products"]
    unclassified = []
    for sku, product in products.items():
        spec = product["garment"]["materials"]["specification"]
        try:
            classify_fabric(spec)
        except UnclassifiedFabricError:
            unclassified.append(sku)
    assert unclassified == []


def test_every_class_has_an_explicit_preset_entry():
    assert set(SHEEN_PRESETS) == set(FabricClass)
    assert SHEEN_PRESETS[FabricClass.FAUX_LEATHER] is None


@pytest.mark.parametrize("bad", [(-0.1, 0.5), (0.5, 1.1)])
def test_sheen_preset_rejects_out_of_range(bad):
    with pytest.raises(ValueError):
        SheenPreset(color=bad[0], roughness=bad[1])


def test_anisotropy_rejects_out_of_range_strength():
    with pytest.raises(ValueError):
        AnisotropyParams(strength=1.5)


def _material_exts(data: bytes) -> list[dict]:
    return [m.get("extensions", {}) for m in read_glb(data).document["materials"]]


def test_sheen_added_to_every_material_with_preset_values():
    out = apply_fabric_extensions(build_triangle_glb(materials=2), SheenPreset(0.35, 0.9))
    for ext in _material_exts(out):
        assert ext["KHR_materials_sheen"] == {
            "sheenColorFactor": [0.35, 0.35, 0.35],
            "sheenRoughnessFactor": 0.9,
        }
        assert "KHR_materials_anisotropy" not in ext


def test_extensions_used_merged_sorted_and_not_required():
    base = read_glb(build_triangle_glb())
    doc = {**base.document, "extensionsUsed": ["KHR_texture_transform", "KHR_materials_sheen"]}
    out = read_glb(apply_fabric_extensions(write_glb(doc, base.tail), SheenPreset(0.2, 0.8)))
    assert out.document["extensionsUsed"] == ["KHR_materials_sheen", "KHR_texture_transform"]
    assert "extensionsRequired" not in out.document


def test_anisotropy_is_opt_in():
    params = AnisotropyParams(strength=0.4, rotation=0.25)
    out = apply_fabric_extensions(build_triangle_glb(), SheenPreset(0.15, 0.3), anisotropy=params)
    assert _material_exts(out)[0]["KHR_materials_anisotropy"] == {
        "anisotropyStrength": 0.4,
        "anisotropyRotation": 0.25,
    }
    assert "KHR_materials_anisotropy" in read_glb(out).document["extensionsUsed"]


def test_patch_is_idempotent_and_preserves_binary_payload():
    source = build_triangle_glb()
    once = apply_fabric_extensions(source, SheenPreset(0.2, 0.8))
    assert apply_fabric_extensions(once, SheenPreset(0.2, 0.8)) == once
    assert read_glb(once).tail == read_glb(source).tail


def test_patch_preserves_existing_material_extensions():
    base = read_glb(build_triangle_glb())
    material = {**base.document["materials"][0], "extensions": {"KHR_materials_ior": {"ior": 1.4}}}
    doc = {**base.document, "materials": [material]}
    out = apply_fabric_extensions(write_glb(doc, base.tail), SheenPreset(0.2, 0.8))
    assert _material_exts(out)[0]["KHR_materials_ior"] == {"ior": 1.4}


def test_patch_does_not_mutate_input_document_objects():
    source = build_triangle_glb()
    apply_fabric_extensions(source, SheenPreset(0.2, 0.8))
    assert "extensions" not in read_glb(source).document["materials"][0]


def test_glb_without_materials_fails_closed():
    with pytest.raises(MaterialPatchError):
        apply_fabric_extensions(
            pack_glb({"asset": {"version": "2.0"}}, None), SheenPreset(0.2, 0.8)
        )


# Founder-verified 2026-09-17: each class read against that product's
# garment.materials.specification prose in the registry. This map is the guard the
# "every SKU classifies" test cannot be — a reworded spec that flips a preset fails HERE.
GOLDEN_FABRIC_CLASSES = {
    "br-001": FabricClass.FLEECE,
    "br-002": FabricClass.FLEECE,
    "br-003": FabricClass.JERSEY,
    "br-004": FabricClass.FLEECE,
    "br-005": FabricClass.JERSEY,
    "br-006": FabricClass.SATIN,
    "br-007": FabricClass.JERSEY,
    "br-008": FabricClass.JERSEY,
    "br-009": FabricClass.JERSEY,
    "br-010": FabricClass.JERSEY,
    "br-011": FabricClass.JERSEY,
    "br-012": FabricClass.JERSEY,
    "br-014": FabricClass.JERSEY,
    "br-015": FabricClass.JERSEY,
    "kids-001": FabricClass.FLEECE,
    "kids-002": FabricClass.FLEECE,
    "lh-002": FabricClass.FLEECE,
    "lh-003": FabricClass.JERSEY,
    "lh-004": FabricClass.SATIN,
    "lh-005": FabricClass.FAUX_LEATHER,
    "lh-006": FabricClass.FLEECE,
    "sg-001": FabricClass.JERSEY,
    "sg-002": FabricClass.COTTON,
    "sg-003": FabricClass.JERSEY,
    "sg-005": FabricClass.COTTON,
    "sg-006": FabricClass.FLEECE,
    "sg-007": FabricClass.KNIT,
    "sg-009": FabricClass.NYLON,
    "sg-011": FabricClass.COTTON,
    "sg-012": FabricClass.COTTON,
    "sg-013": FabricClass.FLEECE,
    "sg-014": FabricClass.FLEECE,
    "sg-015": FabricClass.NYLON,
}


def test_golden_fabric_class_per_registry_sku():
    products = load_registry()["products"]
    assert set(products) == set(GOLDEN_FABRIC_CLASSES), "registry SKUs changed — review the map"
    actual = {sku: classify_product(product).fabric_class for sku, product in products.items()}
    assert actual == GOLDEN_FABRIC_CLASSES


@pytest.mark.parametrize(
    ("specification", "expected"),
    [
        ("No satin here; cotton fleece hoodie.", FabricClass.FLEECE),
        ("Cotton fleece hoodie, unlike the satin bomber.", FabricClass.FLEECE),
        ("Isn't satin. Cotton.", FabricClass.COTTON),
        ("_NOT_ a fleece hoodie. Satin shell.", FabricClass.SATIN),
        ("Nylon shell, never satin.", FabricClass.NYLON),
        ("Cotton tee, rather than the satin bomber.", FabricClass.COTTON),
        ("Cotton jersey, distinct from the satin bomber.", FabricClass.JERSEY),
    ],
)
def test_negation_forms_never_select_the_ruled_out_fabric(specification, expected):
    assert classify_fabric(specification).fabric_class is expected


@pytest.mark.parametrize(
    "specification",
    ["non-satin cotton hoodie.", "Not satin, not cotton, not fleece."],
)
def test_over_stripped_specification_fails_closed(specification):
    with pytest.raises(UnclassifiedFabricError):
        classify_fabric(specification)


def test_refuses_to_overwrite_a_sheen_that_carries_textures():
    document = triangle_document(12)
    document["materials"][0]["extensions"] = {
        "KHR_materials_sheen": {
            "sheenColorFactor": [1.0, 1.0, 1.0],
            "sheenColorTexture": {"index": 3},
        }
    }
    glb = pack_glb(document, b"\x00" * 12)
    with pytest.raises(MaterialPatchError, match="sheenColorTexture"):
        apply_fabric_extensions(glb, SHEEN_PRESETS[FabricClass.COTTON])


@pytest.mark.parametrize(
    ("mutate", "message"),
    [
        (lambda doc: doc["materials"][0].update({"extensions": None}), "expected an object"),
        (lambda doc: doc.update({"extensionsUsed": {"KHR_x": 1}}), "expected a list"),
        (
            lambda doc: doc["materials"][0].update({"extensions": {"KHR_materials_sheen": 7}}),
            "non-object KHR_materials_sheen",
        ),
    ],
)
def test_malformed_extension_containers_fail_closed(mutate, message):
    document = triangle_document(12)
    mutate(document)
    glb = pack_glb(document, b"\x00" * 12)
    with pytest.raises(MaterialPatchError, match=message):
        apply_fabric_extensions(glb, SHEEN_PRESETS[FabricClass.COTTON])
