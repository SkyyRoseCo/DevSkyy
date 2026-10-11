"""Native visual-review receipt contract used by the product registry.

The product registry validates reviewed card fronts against a pixel-inspection
receipt. That contract lives in core so the registry (the bottom layer) never
imports the creative production engine. These models confer no authority:
a valid receipt proves only that a recorded review has the required shape.
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from skyyrose.core.context_resolver import SourceReference

SHA = r"^[a-f0-9]{64}$"

LUXURY_CRITERIA = frozenset(
    {
        "garment_artwork_identity",
        "editorial_composition",
        "cinematic_light",
        "credible_material_response",
        "collection_specific_storytelling",
        "fashion_commerce_intent",
    }
)
REVIEW_CHECKS = LUXURY_CRITERIA | {
    "product_fidelity",
    "artwork_fidelity",
    "optical_integration",
    "product_readability",
}


class _Record(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, revalidate_instances="always")

    @model_validator(mode="after")
    def no_empty_text(self):
        def visit(value):
            if isinstance(value, str) and not value.strip():
                raise ValueError("Blank text is not evidence or a requirement")
            if isinstance(value, (tuple, list)):
                for item in value:
                    visit(item)

        for name in type(self).model_fields:
            visit(getattr(self, name))
        return self


class NativeVisualReceipt(_Record):
    operation_id: str
    job_digest: str = Field(pattern=SHA)
    sources_digest: str = Field(pattern=SHA)
    candidate: SourceReference
    full_size_pixels: SourceReference
    desktop_card: SourceReference
    mobile_card: SourceReference
    reviewer: str = Field(min_length=1)
    status: Literal["PASS", "REVISE"]
    method: Literal["ACTUAL_PIXEL_INSPECTION", "SIMULATED_FIXTURE"]
    checks: dict[str, Literal["PASS", "REVISE"]]
