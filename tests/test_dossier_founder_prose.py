"""The founder's garment prose reaches render prompts verbatim.

A dossier's **Garment type lock** is the founder's own description of the
garment, and it is consumed word for word by render prompts. A previous
projection overwrote it with machine-extracted structured fields, prefixed
"FOUNDER_CONFIRMED structured specifications (take precedence over legacy
dossier prose)" -- labelling derived text as founder-confirmed and ranking it
above the founder's own words, then leaking "Available sizes: S | M | ..." into
every prompt. These tests pin the authority the right way round.
"""

from __future__ import annotations

import pytest

from skyyrose.core.dossier_loader import parse_dossier_markdown, project_registry_dossier
from skyyrose.core.product_registry import load_registry

# Text that only the old overriding projection ever produced.
_OVERRIDE_MARKERS = (
    "take precedence over legacy dossier prose",
    "FOUNDER_CONFIRMED structured specifications",
    "Available sizes:",
)


@pytest.fixture(scope="module")
def products() -> dict:
    return load_registry()["products"]


def test_garment_type_lock_is_the_founders_prose_verbatim(products: dict) -> None:
    """The projected lock equals what the founder wrote -- nothing prepended or swapped."""
    for sku, product in products.items():
        authored = parse_dossier_markdown(product["dossier"]["content"]).garment_type_lock
        projected = project_registry_dossier(product).garment_type_lock
        assert projected == authored, f"{sku}: garment_type_lock was rewritten by the projection"


def test_no_machine_override_reaches_a_prompt_bearing_field(products: dict) -> None:
    for sku, product in products.items():
        dossier = project_registry_dossier(product)
        for marker in _OVERRIDE_MARKERS:
            assert (
                marker not in dossier.garment_type_lock
            ), f"{sku}: {marker!r} in garment_type_lock"
            assert marker not in dossier.raw, f"{sku}: {marker!r} written into the dossier markdown"


def test_projected_markdown_is_the_authored_markdown(products: dict) -> None:
    """The generated dossier mirror is the founder's document, not a rewrite of it."""
    for sku, product in products.items():
        assert (
            project_registry_dossier(product).raw == product["dossier"]["content"]
        ), f"{sku}: projection altered the authored dossier markdown"


def test_machine_split_garment_fields_are_labelled_derived(products: dict) -> None:
    """fit/materials/features were extracted from the prose, so they say so."""
    for sku, product in products.items():
        for section in ("fit", "materials", "features"):
            source = product["garment"][section]["source"]
            assert source == "derived_from_dossier", (
                f"{sku}.garment.{section}.source is {source!r}; machine-extracted fields "
                "must not claim founder authorship"
            )
