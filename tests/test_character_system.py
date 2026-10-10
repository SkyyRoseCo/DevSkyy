"""
Tests for Character Creation System — Phase 3.

Covers: CharacterSpec, CharacterSheet, CharacterCreationAgent,
ConsistencyManager, SpriteGenerator, Rosie mascot, brand DNA presence.
"""

from __future__ import annotations

import pytest

# ---------------------------------------------------------------------------
# CharacterSpec tests
# ---------------------------------------------------------------------------


class TestCharacterSpec:
    def test_create_basic_spec(self):
        from skyyrose.elite_studio.character.models import CharacterSpec

        spec = CharacterSpec(
            name="Test Character",
            style="pixar-chibi",
            body_description="Young character",
            face_features="Round face, bright eyes",
            outfit_base="SkyyRose hoodie",
            brand_elements=("rose gold accents", "SkyyRose logo"),
            reference_paths=(),
        )
        assert spec.name == "Test Character"
        assert spec.style == "pixar-chibi"
        assert len(spec.brand_elements) == 2

    def test_spec_is_frozen(self):
        from skyyrose.elite_studio.character.models import CharacterSpec

        spec = CharacterSpec(
            name="Frozen Test",
            style="realistic",
            body_description="Body",
            face_features="Face",
            outfit_base="Outfit",
            brand_elements=(),
            reference_paths=(),
        )
        with pytest.raises((AttributeError, TypeError)):
            spec.name = "modified"  # type: ignore[misc]

    def test_spec_default_embedding_path(self):
        from skyyrose.elite_studio.character.models import CharacterSpec

        spec = CharacterSpec(
            name="Default",
            style="illustration",
            body_description="",
            face_features="",
            outfit_base="",
            brand_elements=(),
            reference_paths=(),
        )
        assert spec.embedding_path == ""

    def test_character_pose_is_frozen(self):
        from skyyrose.elite_studio.character.models import CharacterPose

        pose = CharacterPose(
            success=True,
            character_name="Rosie",
            pose="wave",
            product_sku="br-001",
            generation_prompt="Test prompt",
        )
        with pytest.raises((AttributeError, TypeError)):
            pose.pose = "modified"  # type: ignore[misc]

    def test_character_sheet_is_frozen(self):
        from skyyrose.elite_studio.character.models import CharacterSheet, CharacterSpec

        spec = CharacterSpec(
            name="Sheet Test",
            style="pixar-chibi",
            body_description="",
            face_features="",
            outfit_base="",
            brand_elements=(),
            reference_paths=(),
        )
        sheet = CharacterSheet(
            success=True,
            spec=spec,
            front_view_prompt="front",
            side_view_prompt="side",
            back_view_prompt="back",
            expression_grid_prompt="grid",
            sprite_description="sprite",
        )
        with pytest.raises((AttributeError, TypeError)):
            sheet.success = False  # type: ignore[misc]


# ---------------------------------------------------------------------------
# CharacterCreationAgent tests
# ---------------------------------------------------------------------------


class TestCharacterCreationAgent:
    def setup_method(self):
        from skyyrose.elite_studio.character.agent import CharacterCreationAgent
        from skyyrose.elite_studio.character.models import CharacterSpec

        self.agent = CharacterCreationAgent()
        self.CharacterSpec = CharacterSpec

    def test_create_sheet_returns_success(self):
        spec = self.CharacterSpec(
            name="Test Char",
            style="pixar-chibi",
            body_description="Young Black girl, Pixar style",
            face_features="Round face, bright eyes, natural hair",
            outfit_base="SkyyRose hoodie and joggers",
            brand_elements=("rose gold accents",),
            reference_paths=(),
        )
        sheet = self.agent.create_sheet(spec)
        assert sheet.success is True
        assert sheet.spec.name == "Test Char"

    def test_create_sheet_generates_all_prompts(self):
        spec = self.CharacterSpec(
            name="Multi Prompt",
            style="pixar-chibi",
            body_description="Character body",
            face_features="Character face",
            outfit_base="Character outfit",
            brand_elements=(),
            reference_paths=(),
        )
        sheet = self.agent.create_sheet(spec)
        assert len(sheet.front_view_prompt) > 20
        assert len(sheet.side_view_prompt) > 20
        assert len(sheet.back_view_prompt) > 20
        assert len(sheet.expression_grid_prompt) > 20
        assert len(sheet.sprite_description) > 20

    def test_front_view_prompt_mentions_front(self):
        spec = self.CharacterSpec(
            name="View Test",
            style="pixar-chibi",
            body_description="Body",
            face_features="Face",
            outfit_base="Outfit",
            brand_elements=(),
            reference_paths=(),
        )
        sheet = self.agent.create_sheet(spec)
        assert "front" in sheet.front_view_prompt.lower()
        assert "side" in sheet.side_view_prompt.lower()
        assert "back" in sheet.back_view_prompt.lower()

    def test_expression_grid_mentions_expressions(self):
        spec = self.CharacterSpec(
            name="Expr Test",
            style="illustration",
            body_description="",
            face_features="Expressive face",
            outfit_base="Outfit",
            brand_elements=(),
            reference_paths=(),
        )
        sheet = self.agent.create_sheet(spec)
        prompt = sheet.expression_grid_prompt.lower()
        assert "expression" in prompt or "grid" in prompt or "smile" in prompt

    def test_generate_pose_wave(self):
        spec = self.CharacterSpec(
            name="Pose Test",
            style="pixar-chibi",
            body_description="Body",
            face_features="Face",
            outfit_base="Outfit",
            brand_elements=(),
            reference_paths=(),
        )
        pose = self.agent.generate_pose(spec, "wave")
        assert pose.success is True
        assert pose.pose == "wave"
        assert (
            "wave" in pose.generation_prompt.lower() or "waving" in pose.generation_prompt.lower()
        )

    def test_generate_pose_with_product_sku(self):
        spec = self.CharacterSpec(
            name="SKU Pose",
            style="pixar-chibi",
            body_description="Body",
            face_features="Face",
            outfit_base="Outfit",
            brand_elements=(),
            reference_paths=(),
        )
        pose = self.agent.generate_pose(spec, "idle", product_sku="br-004")
        assert pose.success is True
        assert pose.product_sku == "br-004"
        assert "br-004" in pose.generation_prompt


# ---------------------------------------------------------------------------
# Rosie mascot tests
# ---------------------------------------------------------------------------


class TestRosieMascot:
    def setup_method(self):
        from skyyrose.elite_studio.character.agent import CharacterCreationAgent

        self.agent = CharacterCreationAgent()

    def test_create_skyyrose_rosie_returns_success(self):
        sheet = self.agent.create_skyyrose_rosie()
        assert sheet.success is True
        assert sheet.spec.name == "Skyy"

    def test_rosie_is_pixar_chibi(self):
        sheet = self.agent.create_skyyrose_rosie()
        assert sheet.spec.style == "pixar-chibi"

    def test_rosie_has_brand_elements(self):
        sheet = self.agent.create_skyyrose_rosie()
        elements_text = " ".join(sheet.spec.brand_elements)
        # Skyy wears Love Hurts collection — crimson accents + Oakland tagline
        assert "love hurts" in elements_text.lower() or "crimson" in elements_text.lower()

    def test_rosie_wears_love_hurts_varsity(self):
        sheet = self.agent.create_skyyrose_rosie()
        outfit = sheet.spec.outfit_base.lower()
        # Skyy wears the canonical Love Hurts varsity jacket as seen in the reference image
        assert "varsity" in outfit or "love hurts" in outfit

    def test_rosie_has_natural_afro(self):
        sheet = self.agent.create_skyyrose_rosie()
        face = sheet.spec.face_features.lower()
        # Skyy has a full natural afro (not afro puffs — canonical reference shows unrestrained hair)
        assert "afro" in face

    def test_rosie_front_prompt_has_quality_markers(self):
        sheet = self.agent.create_skyyrose_rosie()
        prompt = sheet.front_view_prompt.lower()
        assert "pixar" in prompt or "quality" in prompt or "3d" in prompt

    def test_rosie_brand_dna_present_in_prompts(self):
        sheet = self.agent.create_skyyrose_rosie()
        all_prompts = " ".join(
            [
                sheet.front_view_prompt,
                sheet.side_view_prompt,
                sheet.back_view_prompt,
            ]
        )
        assert "skyyrose" in all_prompts.lower() or "SkyyRose" in all_prompts

    def test_rosie_prompts_retain_brand_identity(self):
        sheet = self.agent.create_skyyrose_rosie()
        all_prompts = " ".join(
            [
                sheet.front_view_prompt,
                sheet.back_view_prompt,
                sheet.expression_grid_prompt,
            ]
        )
        assert "skyyrose" in all_prompts.lower()

    def test_rosie_is_young_black_girl(self):
        sheet = self.agent.create_skyyrose_rosie()
        body = sheet.spec.body_description.lower()
        assert "black girl" in body or ("young" in body and "girl" in body)

    def test_rosie_has_oakland_reference(self):
        sheet = self.agent.create_skyyrose_rosie()
        all_text = (
            sheet.spec.body_description + sheet.spec.face_features + sheet.front_view_prompt
        ).lower()
        assert (
            "oakland" in all_text
            or "bay area" in all_text
            or "oakland" in " ".join(sheet.spec.brand_elements).lower()
        )


# ---------------------------------------------------------------------------
# ConsistencyManager tests
# ---------------------------------------------------------------------------


class TestConsistencyManager:
    def setup_method(self):
        from skyyrose.elite_studio.character.consistency import ConsistencyManager
        from skyyrose.elite_studio.character.models import CharacterSpec

        self.manager = ConsistencyManager()
        self.CharacterSpec = CharacterSpec

    def _make_spec(self, name: str = "TestChar") -> object:
        return self.CharacterSpec(
            name=name,
            style="pixar-chibi",
            body_description="Test body",
            face_features="Test face with big eyes",
            outfit_base="SkyyRose hoodie",
            brand_elements=("rose gold accent",),
            reference_paths=(),
        )

    def test_register_returns_id(self):
        spec = self._make_spec()
        char_id = self.manager.register_character(spec)
        assert char_id != ""
        assert isinstance(char_id, str)

    def test_get_consistency_prompt_for_registered(self):
        spec = self._make_spec()
        char_id = self.manager.register_character(spec)
        prompt = self.manager.get_consistency_prompt(char_id)
        assert len(prompt) > 0
        assert "TestChar" in prompt

    def test_get_consistency_prompt_unknown_returns_empty(self):
        prompt = self.manager.get_consistency_prompt("nonexistent-id")
        assert prompt == ""

    def test_list_characters_contains_registered(self):
        spec = self._make_spec("ListChar")
        char_id = self.manager.register_character(spec)
        chars = self.manager.list_characters()
        ids = [c["character_id"] for c in chars]
        assert char_id in ids

    def test_list_characters_has_name_and_style(self):
        spec = self._make_spec("StyleCheck")
        self.manager.register_character(spec)
        chars = self.manager.list_characters()
        matching = [c for c in chars if c["name"] == "StyleCheck"]
        assert len(matching) == 1
        assert matching[0]["style"] == "pixar-chibi"

    def test_unregister_removes_character(self):
        spec = self._make_spec("RemoveMe")
        char_id = self.manager.register_character(spec)
        result = self.manager.unregister(char_id)
        assert result is True
        assert self.manager.get_consistency_prompt(char_id) == ""

    def test_unregister_unknown_returns_false(self):
        assert self.manager.unregister("does-not-exist") is False

    def test_build_consistency_prompt_function(self):
        from skyyrose.elite_studio.character.consistency import build_consistency_prompt

        spec = self._make_spec("Prompt Test")
        prompt = build_consistency_prompt(spec, "standing in Oakland alley")
        assert "CONSISTENCY ANCHOR" in prompt
        assert "Prompt Test" in prompt
        assert "oakland alley" in prompt.lower()


# ---------------------------------------------------------------------------
# SpriteGenerator tests
# ---------------------------------------------------------------------------


class TestSpriteGenerator:
    def setup_method(self):
        from skyyrose.elite_studio.character.sprite_generator import SpriteGenerator, SpriteSpec

        self.generator = SpriteGenerator()
        self.SpriteSpec = SpriteSpec

    def test_generate_sprite_prompts_basic(self):
        spec = self.SpriteSpec(
            character_name="TestSprite",
            poses=("idle", "wave"),
            style="2d",
            background="transparent",
        )
        result = self.generator.generate_sprite_prompts(spec)
        assert result.success is True
        assert "idle" in result.sprite_prompts
        assert "wave" in result.sprite_prompts

    def test_sprite_prompts_mention_poses(self):
        spec = self.SpriteSpec(
            character_name="PoseCheck",
            poses=("celebrate",),
            style="illustrated",
            background="white",
        )
        result = self.generator.generate_sprite_prompts(spec)
        prompt = result.sprite_prompts["celebrate"].lower()
        assert "celebrat" in prompt or "arms raised" in prompt

    def test_sprite_result_has_css_hint(self):
        spec = self.SpriteSpec(
            character_name="CSSTest",
            poses=("walk_1", "walk_2", "idle"),
            style="2d",
            background="transparent",
        )
        result = self.generator.generate_sprite_prompts(spec)
        assert len(result.css_animation_hint) > 0

    def test_sprite_result_is_frozen(self):
        spec = self.SpriteSpec(
            character_name="FreezeTest",
            poses=("idle",),
            style="2d",
            background="transparent",
        )
        result = self.generator.generate_sprite_prompts(spec)
        with pytest.raises((AttributeError, TypeError)):
            result.success = False  # type: ignore[misc]

    def test_generate_rosie_mascot_7_poses(self):
        result = self.generator.generate_skyyrose_mascot_sprites()
        assert result.success is True
        assert result.character_name == "Rosie"
        expected_poses = {"idle", "walk_1", "walk_2", "wave", "point", "celebrate", "think"}
        assert set(result.sprite_prompts.keys()) == expected_poses

    def test_rosie_sprites_contain_brand_dna(self):
        result = self.generator.generate_skyyrose_mascot_sprites()
        all_prompts = " ".join(result.sprite_prompts.values())
        assert "SkyyRose" in all_prompts or "skyyrose" in all_prompts.lower()
        assert "skyyrose" in all_prompts.lower()

    def test_rosie_sprite_css_hint_mentions_walk(self):
        result = self.generator.generate_skyyrose_mascot_sprites()
        assert "walk" in result.css_animation_hint.lower()

    def test_rosie_sprite_prompts_mention_rosie_identity(self):
        result = self.generator.generate_skyyrose_mascot_sprites()
        for pose, prompt in result.sprite_prompts.items():
            assert (
                "Rosie" in prompt or "rosie" in prompt.lower()
            ), f"Pose {pose} prompt missing Rosie identity"
