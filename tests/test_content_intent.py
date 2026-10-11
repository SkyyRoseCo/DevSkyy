"""Intent dimensions, explicit taxonomy extension, verification and source coverage."""

import pytest
from pydantic import ValidationError

from skyyrose.core.content_intent import (
    CONTENT_FAMILIES,
    FILM_PLANNING_FIELDS,
    INTERACTIVE_PLANNING_FIELDS,
    SHOT_ROLES,
    ContentIntent,
    DerivativePlan,
    FilmPlan,
    ShotIntent,
    TaxonomyRegistry,
    missing_planning_fields,
    verification_requirements,
)


def intent(**updates):
    return ContentIntent.model_validate(
        dict(
            medium="image",
            audience="SkyyRose audience",
            production_type="editorial_still",
            content_role="editorial",
            shot_role="product_editorial",
            intended_use="internal",
            representation_mode="EXACT_PRODUCT",
            lifecycle_stage="M2",
        )
        | updates
    )


def test_static_frame_is_not_film_or_distribution():
    result = intent()
    assert result.medium == "image"
    assert result.shot_role == "PRODUCT_EDITORIAL"
    assert result.distribution_channels == []
    with pytest.raises(ValidationError, match="Film production"):
        intent(production_type="short_film")
    with pytest.raises(ValidationError, match="Unregistered distribution_channel"):
        intent(distribution_channels=["film"])


@pytest.mark.parametrize(
    "field,value",
    [
        ("medium", "iamge"),
        ("content_role", "editroial"),
        ("production_type", "filmish"),
        ("shot_role", "FRNOT"),
        ("intended_use", "maybe"),
    ],
)
def test_unregistered_terms_fail(field, value):
    with pytest.raises(ValidationError, match="Unregistered"):
        intent(**{field: value})


def test_registry_extensions_are_explicit_and_cannot_overwrite():
    registry = TaxonomyRegistry()
    with pytest.raises(ValueError):
        registry.validate("content_role", "new_editorial")
    registry.register("content_role", "new_editorial", "campaign")
    assert registry.validate("content_role", "NEW_EDITORIAL") == "new_editorial"
    with pytest.raises(ValueError, match="overwritten"):
        registry.register("content_role", "new_editorial", "commerce")
    with pytest.raises(ValueError):
        registry.register("content_role", "bad token", "campaign")
    with pytest.raises(ValueError):
        registry.register("content_role", "valid_token", "unknown")
    snapshot = registry.snapshot()
    snapshot["content_role"].clear()
    assert registry.validate("content_role", "new_editorial")


def test_all_required_families_are_registered():
    registry = TaxonomyRegistry()
    assert len(CONTENT_FAMILIES) == 8
    for tokens in CONTENT_FAMILIES.values():
        for token in tokens:
            assert registry.validate("content_role", token) == token
    assert len(SHOT_ROLES) == 17


def test_shots_preserve_per_frame_function_and_product_mode():
    world = ShotIntent(shot_id="1", shot_role="WORLD_ESTABLISHING", purpose="Introduce place")
    product = ShotIntent(
        shot_id="2",
        shot_role="PRODUCT_HERO",
        purpose="Show garment",
        exact_product=True,
        product_skus=["br-001"],
    )
    result = intent(shots=[world, product], distribution_channels=["Instagram"])
    assert result.distribution_channels == ["instagram"]
    assert not result.shots[0].exact_product
    assert result.shots[1].exact_product
    with pytest.raises(ValidationError, match="EXACT_PRODUCT"):
        intent(representation_mode="BRAND_ABSTRACT", shots=[product])
    with pytest.raises(ValidationError):
        ShotIntent(shot_id="3", shot_role="FRONT", purpose="Show front", product_skus=["br-001"])
    with pytest.raises(ValidationError, match="Duplicate shot"):
        intent(shots=[world, world])


def test_verification_varies_with_intent():
    card = verification_requirements(intent(content_role="product_card"))
    detail = verification_requirements(intent(content_role="material_detail"))
    editorial = verification_requirements(intent())
    assert "crop_resilience" in card["CREATIVE_QA"]
    assert "material_construction_accuracy" in detail["PRODUCT_FIDELITY"]
    assert "novelty" in editorial["CREATIVE_QA"]
    abstract = verification_requirements(intent(representation_mode="BRAND_ABSTRACT"))
    assert "PRODUCT_FIDELITY" not in abstract


def test_film_planning_gaps_and_verification():
    film = intent(
        medium="video",
        production_type="short_film",
        content_role="collection_story",
        film_plan=FilmPlan(purpose="Explore continuation"),
    )
    gaps = missing_planning_fields(film)
    assert "purpose" not in gaps
    assert "music" in gaps and "product_continuity" in gaps
    requirements = verification_requirements(film)
    assert requirements["CREATIVE_QA"] == [f"film_{field}" for field in FILM_PLANNING_FIELDS]


def test_interactive_requirements_include_accessibility_and_commerce():
    interactive = intent(
        medium="interactive",
        production_type="interactive_story",
        content_role="experimental_shopping_experience",
    )
    assert missing_planning_fields(interactive) == list(INTERACTIVE_PLANNING_FIELDS)
    gates = verification_requirements(interactive)
    assert "recoverable_control" in gates["CREATIVE_QA"]
    assert "usable_fallback" in gates["ACCESSIBILITY"]
    assert "commerce_route" in gates["COMMERCE_INTEGRITY"]


def test_derivatives_plan_coverage_and_expression_without_platform_dimensions():
    plan = DerivativePlan(
        source_asset_id="daylight-shoot",
        source_production_type="photoshoot",
        coverage_rationale="Capture product detail and wide scene separately",
        applications=[
            dict(
                application_id="editorial",
                content_intent=intent(),
                source_coverage=["front garment plate", "wide environment"],
                adaptation_intent="Build a scene around intact product photography",
            )
        ],
    )
    assert plan.applications[0].platform_requirements == "RESOLVE_AT_EXECUTION"
    data = plan.model_dump()
    data["applications"][0]["width"] = 1080
    with pytest.raises(ValidationError, match="Extra inputs"):
        DerivativePlan.model_validate(data)


def test_shot_specific_verification_in_carousel():
    result = verification_requirements(
        intent(
            content_role="carousel",
            shots=[
                ShotIntent(
                    shot_id="material",
                    shot_role="MATERIAL",
                    purpose="Show knit",
                    exact_product=True,
                    product_skus=["br-001"],
                )
            ],
        )
    )
    assert "material_construction_accuracy" in result["PRODUCT_FIDELITY"]


def test_blank_audience_is_not_resolved_context():
    with pytest.raises(ValidationError):
        intent(audience="   ")
