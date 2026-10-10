"""render_reference bindings must resolve inside the repository only.

A binding path flows into references.get_logo_reference and from there its
bytes are uploaded to OpenAI, so an absolute or parent-traversing path in the
registry would exfiltrate an arbitrary local file.
"""

from __future__ import annotations

import pytest

from skyyrose.core.catalog_loader import PROJECT_ROOT
from skyyrose.elite_studio.logo_registry import LogoRegistry, RegistryContractError


def _registry(path_text: str) -> LogoRegistry:
    return LogoRegistry(
        {
            "sku_logos": {
                "zz-001": {
                    "placements": [],
                    "render_reference": {"status": "BOUND", "path": path_text},
                }
            }
        }
    )


@pytest.mark.parametrize(
    "path_text",
    ["/etc/passwd", "../../etc/passwd", "assets/../../outside.png"],
)
def test_render_reference_path_cannot_leave_the_repository(path_text: str) -> None:
    with pytest.raises(RegistryContractError, match="repository"):
        _registry(path_text).primary_reference_for("zz-001")


def test_render_reference_path_resolves_inside_the_repository() -> None:
    relative = "assets/products/references/zz-001-front.png"
    assert (
        _registry(relative).primary_reference_for("zz-001") == (PROJECT_ROOT / relative).resolve()
    )
