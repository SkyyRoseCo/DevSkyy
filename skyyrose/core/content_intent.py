"""Validated artifact intent, shot functions and coverage planning (no channel specs)."""

from __future__ import annotations

import re
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

CONTENT_FAMILIES = {
    "commerce": [
        "product_card",
        "catalog",
        "pdp_hero",
        "front",
        "back",
        "side",
        "product_detail",
        "material_detail",
        "graphic_detail",
        "on_body",
        "fit",
        "lifestyle",
        "product_video",
        "product_3d",
        "collection_media",
    ],
    "web": [
        "homepage_hero",
        "collection_hero",
        "cinematic_sequence",
        "interactive_story",
        "spatial_experience",
        "3d_experience",
        "experimental_shopping_experience",
        "interactive_shopping_experience",
    ],
    "campaign": [
        "campaign_key_art",
        "editorial_still",
        "editorial_shoot",
        "lookbook",
        "collection_story",
        "launch_campaign",
        "editorial",
    ],
    "film": [
        "commercial",
        "brand_film",
        "collection_film",
        "fashion_film",
        "short_film",
        "narrative_film",
        "product_film",
        "teaser",
        "trailer",
        "experimental_film",
    ],
    "social": [
        "instagram_feed",
        "carousel",
        "stories",
        "reels",
        "tiktok",
        "shorts",
        "social_teaser",
    ],
    "advertising": [
        "awareness",
        "launch",
        "product_acquisition",
        "consideration",
        "retargeting",
        "commercial_cutdown",
        "paid_social_variant",
    ],
    "crm": ["email_hero", "email_product_module", "launch_email", "mms_sms_creative"],
    "physical": ["print", "packaging", "retail", "signage", "event", "billboard", "installation"],
}
SHOT_ROLES = (
    "WORLD_ESTABLISHING",
    "PRODUCT_HERO",
    "FRONT",
    "BACK",
    "SIDE",
    "DETAIL",
    "MATERIAL",
    "GRAPHIC",
    "ON_BODY",
    "FIT",
    "LIFESTYLE",
    "EDITORIAL",
    "CHARACTER",
    "NARRATIVE",
    "EXPERIMENTAL",
    "CTA",
    "PRODUCT_EDITORIAL",
)
FILM_PLANNING_FIELDS = (
    "purpose",
    "story",
    "theme",
    "narrative_arc",
    "product_role",
    "characters",
    "location",
    "cinematography",
    "materials",
    "lighting",
    "camera",
    "sound",
    "music",
    "dialogue",
    "voiceover",
    "product_continuity",
    "master_format",
    "derivatives",
)
INTERACTIVE_PLANNING_FIELDS = (
    "product_truth",
    "discovery_model",
    "interaction_model",
    "fallback",
    "accessibility",
    "commerce_route",
    "performance",
    "recoverable_control",
)


class TaxonomyRegistry:
    """Explicit additions are validated; duplicate registrations cannot change meaning."""

    def __init__(self) -> None:
        self._terms: dict[str, dict[str, str]] = {
            "medium": dict.fromkeys(
                ("image", "video", "3d", "interactive", "audio", "text", "physical", "mixed"),
                "general",
            ),
            "production_type": {},
            "content_role": {},
            "shot_role": {k.lower(): "shot" for k in SHOT_ROLES},
            "distribution_channel": dict.fromkeys(
                (
                    "web",
                    "instagram",
                    "tiktok",
                    "youtube",
                    "facebook",
                    "pinterest",
                    "email",
                    "sms",
                    "mms",
                    "print",
                    "retail",
                    "ooh",
                    "event",
                ),
                "distribution",
            ),
            "intended_use": dict.fromkeys(
                ("internal", "concept", "customer_facing", "paid", "ecommerce", "research"), "use"
            ),
        }
        for family, tokens in CONTENT_FAMILIES.items():
            for dimension in ("content_role", "production_type"):
                self._terms[dimension].update(dict.fromkeys(tokens, family))
        self._terms["production_type"].update(
            dict.fromkeys(
                (
                    "photoshoot",
                    "product_scan",
                    "controlled_render",
                    "source_composite",
                    "photography",
                    "3d_asset",
                    "location_production",
                    "character_system",
                    "campaign_environment",
                ),
                "general",
            )
        )

    def register(self, dimension: str, token: str, family: str) -> None:
        if dimension not in self._terms:
            raise ValueError(f"Unknown taxonomy dimension: {dimension}")
        if not re.fullmatch(r"[a-z0-9]+(?:_[a-z0-9]+)*", token):
            raise ValueError("Taxonomy extensions require a lowercase snake_case token")
        if family not in {*CONTENT_FAMILIES, "general", "shot", "distribution", "use"}:
            raise ValueError(f"Unknown taxonomy family: {family}")
        existing = self._terms[dimension].get(token)
        if existing is not None and existing != family:
            raise ValueError("Existing taxonomy meaning cannot be overwritten")
        self._terms[dimension][token] = family

    def validate(self, dimension: str, value: str) -> str:
        normalized = value.strip().lower()
        if normalized not in self._terms[dimension]:
            raise ValueError(f"Unregistered {dimension}: {value}")
        return normalized

    def family(self, dimension: str, token: str) -> str:
        return self._terms[dimension][self.validate(dimension, token)]

    def snapshot(self) -> dict[str, dict[str, str]]:
        return {key: dict(sorted(values.items())) for key, values in sorted(self._terms.items())}


TAXONOMY = TaxonomyRegistry()


def register_taxonomy_term(dimension: str, token: str, family: str) -> None:
    TAXONOMY.register(dimension, token, family)


class IntentModel(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, str_strip_whitespace=True)


class ShotIntent(IntentModel):
    shot_id: str = Field(min_length=1)
    shot_role: str
    purpose: str = Field(min_length=1)
    exact_product: bool = False
    product_skus: list[str] = Field(default_factory=list)

    @field_validator("shot_role")
    @classmethod
    def role(cls, value: str) -> str:
        return TAXONOMY.validate("shot_role", value).upper()

    @model_validator(mode="after")
    def product_binding(self) -> ShotIntent:
        if bool(self.product_skus) != self.exact_product:
            raise ValueError("Exact-product shots require explicit SKUs; SKU shots must be exact")
        if any(not sku.strip() for sku in self.product_skus):
            raise ValueError("SKU cannot be blank")
        if len(set(self.product_skus)) != len(self.product_skus):
            raise ValueError("Duplicate shot SKU")
        return self


class FilmPlan(IntentModel):
    """Missing fields are planning gaps; 'not applicable' needs an explicit explanation."""

    purpose: str | None = None
    story: str | None = None
    theme: str | None = None
    narrative_arc: str | None = None
    product_role: str | None = None
    characters: str | None = None
    location: str | None = None
    cinematography: str | None = None
    materials: str | None = None
    lighting: str | None = None
    camera: str | None = None
    sound: str | None = None
    music: str | None = None
    dialogue: str | None = None
    voiceover: str | None = None
    product_continuity: str | None = None
    master_format: str | None = None
    derivatives: str | None = None


class InteractivePlan(IntentModel):
    product_truth: str | None = None
    discovery_model: str | None = None
    interaction_model: str | None = None
    fallback: str | None = None
    accessibility: str | None = None
    commerce_route: str | None = None
    performance: str | None = None
    recoverable_control: str | None = None


class ContentIntent(IntentModel):
    medium: str
    production_type: str
    content_role: str
    shot_role: str | None = None
    distribution_channels: list[str] = Field(default_factory=list)
    intended_use: str
    audience: str = Field(min_length=1)
    representation_mode: Literal["EXACT_PRODUCT", "PRODUCT_CONCEPT", "BRAND_ABSTRACT"]
    lifecycle_stage: Literal["M1", "M2", "M3", "M4", "M5", "M6", "M7", "M8", "M9"]
    shots: list[ShotIntent] = Field(default_factory=list)
    film_plan: FilmPlan | None = None
    interactive_plan: InteractivePlan | None = None

    @field_validator("medium", "production_type", "content_role", "intended_use")
    @classmethod
    def registered_term(cls, value: str, info) -> str:
        normalized = TAXONOMY.validate(info.field_name, value)
        return normalized.upper() if info.field_name == "intended_use" else normalized

    @field_validator("shot_role")
    @classmethod
    def registered_shot(cls, value: str | None) -> str | None:
        return TAXONOMY.validate("shot_role", value).upper() if value is not None else None

    @field_validator("distribution_channels")
    @classmethod
    def registered_channels(cls, values: list[str]) -> list[str]:
        result = [TAXONOMY.validate("distribution_channel", value) for value in values]
        if len(result) != len(set(result)):
            raise ValueError("Duplicate distribution channels")
        return result

    @model_validator(mode="after")
    def independent_dimensions(self) -> ContentIntent:
        if (
            TAXONOMY.family("production_type", self.production_type) == "film"
            and self.medium != "video"
        ):
            raise ValueError("Film production requires video medium")
        if self.production_type == "editorial_still" and self.medium != "image":
            raise ValueError("Editorial still requires image medium")
        if len({shot.shot_id for shot in self.shots}) != len(self.shots):
            raise ValueError("Duplicate shot IDs")
        if (
            any(shot.exact_product for shot in self.shots)
            and self.representation_mode != "EXACT_PRODUCT"
        ):
            raise ValueError("Real-product shots require EXACT_PRODUCT intent")
        return self


def planning_requirements(intent: ContentIntent) -> list[str]:
    if TAXONOMY.family("production_type", intent.production_type) == "film":
        return list(FILM_PLANNING_FIELDS)
    if (
        intent.medium == "interactive"
        or "experience" in intent.content_role
        or intent.content_role == "interactive_story"
    ):
        return list(INTERACTIVE_PLANNING_FIELDS)
    return []


def missing_planning_fields(intent: ContentIntent) -> list[str]:
    plan = (
        intent.film_plan
        if TAXONOMY.family("production_type", intent.production_type) == "film"
        else intent.interactive_plan
    )
    return [
        field
        for field in planning_requirements(intent)
        if plan is None or not (getattr(plan, field, None) or "").strip()
    ]


def intent_missing_context(intent: ContentIntent) -> list[str]:
    """Stable interface for lifecycle-sensitive planning gap evaluation."""
    return missing_planning_fields(intent)


def verification_requirements(intent: ContentIntent) -> dict[str, list[str]]:
    """Return criterion IDs, never a claim that the artifact passed them."""
    gates = {"CONSTITUTION": ["constitutional_expression"]}
    if intent.representation_mode == "EXACT_PRODUCT":
        gates["PRODUCT_FIDELITY"] = ["exact_product_fidelity"]
    if intent.distribution_channels:
        gates["CHANNEL"] = ["execution_time_channel_specifications"]
    role = intent.content_role
    if role == "product_card":
        gates["CREATIVE_QA"] = [
            "immediate_product_readability",
            "crop_resilience",
            "catalog_consistency",
        ]
        gates.setdefault("CHANNEL", []).append("channel_technical_requirements")
    elif role in {"product_detail", "material_detail", "graphic_detail", "pdp_hero"}:
        gates["PRODUCT_FIDELITY"] = [
            "exact_visual_truth",
            "required_product_detail",
            "material_construction_accuracy",
        ]
    elif TAXONOMY.family("content_role", role) == "campaign":
        gates["CREATIVE_QA"] = [
            "creative_direction",
            "composition",
            "novelty",
            "intended_narrative",
        ]
    if TAXONOMY.family("production_type", intent.production_type) == "film":
        gates["CREATIVE_QA"] = [f"film_{field}" for field in FILM_PLANNING_FIELDS]
        gates["TECHNICAL_QA"] = ["master_and_derivative_requirements"]
    if intent.medium == "interactive" or "experience" in role or role == "interactive_story":
        gates["CREATIVE_QA"] = ["discovery_model", "interaction_model", "recoverable_control"]
        gates["ACCESSIBILITY"] = ["accessible_interaction", "usable_fallback"]
        gates["TECHNICAL_QA"] = ["performance", "fallback_behavior"]
        gates["COMMERCE_INTEGRITY"] = ["product_truth", "commerce_route"]
    shot_roles = {shot.shot_role for shot in intent.shots}
    if intent.shot_role:
        shot_roles.add(intent.shot_role)
    if intent.representation_mode == "EXACT_PRODUCT":
        criteria = gates.setdefault("PRODUCT_FIDELITY", [])
        if shot_roles & {"DETAIL", "MATERIAL", "GRAPHIC"}:
            criteria.extend(["required_product_detail", "material_construction_accuracy"])
        if shot_roles & {"ON_BODY", "FIT"}:
            criteria.append("fit_and_on_body_accuracy")
        gates["PRODUCT_FIDELITY"] = list(dict.fromkeys(criteria))
    return gates


class DerivativeApplication(IntentModel):
    application_id: str = Field(min_length=1)
    content_intent: ContentIntent
    source_coverage: list[str] = Field(min_length=1)
    adaptation_intent: str = Field(min_length=1)
    platform_requirements: Literal["RESOLVE_AT_EXECUTION"] = "RESOLVE_AT_EXECUTION"

    @field_validator("source_coverage")
    @classmethod
    def meaningful_coverage(cls, values: list[str]) -> list[str]:
        if any(not value.strip() for value in values):
            raise ValueError("Source coverage must name actual capture requirements")
        return values


class DerivativePlan(IntentModel):
    source_asset_id: str = Field(min_length=1)
    source_production_type: str
    applications: list[DerivativeApplication] = Field(min_length=1)
    coverage_rationale: str = Field(min_length=1)

    @field_validator("source_production_type")
    @classmethod
    def registered_source(cls, value: str) -> str:
        return TAXONOMY.validate("production_type", value)

    @model_validator(mode="after")
    def unique_applications(self) -> DerivativePlan:
        if len({item.application_id for item in self.applications}) != len(self.applications):
            raise ValueError("Duplicate derivative application IDs")
        return self
