"""Dimensions compare matching decoration locations, never unrelated back marks."""

from skyyrose.core.product_truth import project_product


def record(spec, dossier):
    return {
        "sku": "fixture",
        "catalog": {"branding_spec": spec},
        "dossier": {"branding_block": dossier},
    }


def conflicts(raw):
    return [
        x
        for x in project_product(raw, ["front"], [])["conflicts"]
        if x["field"] == "decoration_dimensions" and x["status"] == "CONFLICTED"
    ]


def test_front_patch_is_not_compared_with_back_neck_or_back_logo():
    raw = record(
        "FRONT: Authentic Collection patch at lower hem, 3 inches wide x 4 inches tall. BACK: rose and monogram.",
        """### Front
- **front-left-hem** (3in wide × 4in tall): Authentic Collection patch.
### Back
- **back-neck** (~2in wide): monogram.
- **back-center** (~10in–12in tall): rose.
### Sleeves / Collar / Hem / Other
- **collar / V-neck binding** (1/4in–3/8in wide): piping.""",
    )
    assert not conflicts(raw)


def test_same_front_patch_swapped_axes_still_conflict():
    raw = record(
        "FRONT: Authentic Collection patch at lower hem, 3 inches wide x 4 inches tall.",
        "### Front\n- **front-left-hem** (4in wide × 3in tall): Authentic Collection patch.",
    )
    assert conflicts(raw)


def test_different_front_objects_do_not_collide():
    raw = record(
        "FRONT: Chest lettering 9in wide. Hem patch 3in wide x 4in tall.",
        "### Front\n- **front-chest** (9in wide): lettering.\n- **front-left-hem** (3in wide × 4in tall): patch.\n- **front-placket binding** (1/4in wide): piping.",
    )
    assert not conflicts(raw)


def test_unmapped_mismatching_dimensions_fail_closed():
    assert conflicts(record("10 inches wide", "12 inches wide"))
