"""The recorded maker correction must reach every BR-007 dossier consumer."""

from skyyrose.core.product import get_product


def test_br007_dossier_preserves_side_lettering_and_zip_pockets() -> None:
    product = get_product("br-007")
    prose = product["dossier"]["full_text"]
    assert "Love Hurts is only on the side not across the back" in prose
    assert "No Love Hurts wordmark across the back" in prose
    assert "back-upper / back-yoke** (large cursive across the upper back)" not in prose
    assert "NO front pockets visible from outside" not in prose
    assert "two zippered side hand pockets and one zippered back" in prose
    assert product["catalog"]["price"] == "65"
    assert product["catalog"]["is_preorder"] == "0"
