"""Validated visual evidence and locally computed QA decisions; no provider I/O."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)

    @field_validator("*", mode="after")
    @classmethod
    def nonblank_text(cls, value):
        if isinstance(value, str) and not value.strip():
            raise ValueError("Visible evidence and notes cannot be blank")
        return value


class Finding(StrictModel):
    status: Literal["match", "mismatch", "not_visible"]
    evidence: str = Field(min_length=1, max_length=600)


class Identity(StrictModel):
    silhouette: Finding
    construction: Finding
    artwork: Finding
    lettering: Finding
    color: Finding
    placement: Finding


class VisualScore(StrictModel):
    score: int = Field(ge=0, le=100)
    evidence: str = Field(min_length=1, max_length=600)


class Scene(StrictModel):
    lighting: VisualScore
    edges: VisualScore
    shadows: VisualScore
    scale: Finding
    perspective: Finding
    occlusion: Finding


class JudgeResponse(StrictModel):
    identity: Identity
    scene: Scene | None
    ghost_fidelity: VisualScore | None
    notes: str = Field(min_length=1, max_length=1000)

    def decision(self, mode: str) -> dict:
        identity = list(self.identity.model_dump().values())
        mismatch = any(f["status"] == "mismatch" for f in identity)
        hidden = any(f["status"] == "not_visible" for f in identity)
        identity_score = 100 * sum(f["status"] == "match" for f in identity) / len(identity)
        if mode == "scene_composite":
            if self.scene is None or self.ghost_fidelity is not None:
                raise ValueError("Scene mode requires scene rubric only")
            total = (
                self.scene.lighting.score * 0.35
                + self.scene.edges.score * 0.30
                + self.scene.shadows.score * 0.35
            )
            integrated = all(
                getattr(self.scene, key).status == "match"
                for key in ("scale", "perspective", "occlusion")
            )
            # A floating/cutout subject is never rescued by averaging.
            integrated = integrated and all(
                getattr(self.scene, key).score > 0 for key in ("lighting", "edges", "shadows")
            )
        elif mode == "flat_lay":
            if self.ghost_fidelity is None or self.scene is not None:
                raise ValueError("Flat-lay mode requires ghost fidelity rubric only")
            branding = (self.identity.artwork, self.identity.lettering, self.identity.placement)
            branding_score = 100 * sum(f.status == "match" for f in branding) / len(branding)
            total = identity_score * 0.30 + self.ghost_fidelity.score * 0.40 + branding_score * 0.30
            integrated = self.ghost_fidelity.score > 0
        else:
            raise ValueError("Unknown QA mode")
        return {
            "status": "evaluated",
            "score": round(total, 2),
            "identity_score": round(identity_score, 2),
            "identity_mismatch": mismatch,
            "missing_evidence": hidden,
            "accepted": total >= 80 and not mismatch and not hidden and integrated,
            "findings": self.model_dump(),
        }


def parse_response(text: str, mode: str) -> dict:
    """No fallback scores, markdown stripping, numeric coercion or inferred totals."""
    return JudgeResponse.model_validate_json(text).decision(mode)
