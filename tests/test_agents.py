"""
Tests for agents module
=======================

Agent instantiation and workflow tests.
"""

import pytest

from agents import (
    COLLECTION_PROMPTS,
    GARMENT_TEMPLATES,
    FashnConfig,
    FashnTryOnAgent,
    GarmentCategory,
    Model3DUploadResult,
    ModelFormat,
    TripoAssetAgent,
    TripoConfig,
    TryOnMode,
    WordPressAssetAgent,
    WordPressAssetConfig,
)
from agents.core.base import AgentCapability
from orchestration.asset_pipeline import (
    AssetPipelineResult,
    PipelineConfig,
    PipelineStage,
    ProductAssetPipeline,
    ProductCategory,
)


class TestFashnAgent:
    """Test FASHN virtual try-on agent."""

    def test_instantiate(self):
        """Should instantiate agent."""
        agent = FashnTryOnAgent()

        assert agent.name == "fashn_tryon"
        assert AgentCapability.VIRTUAL_TRYON in agent.get_capabilities()

    def test_config_from_env(self):
        """Should create config from environment."""
        config = FashnConfig.from_env()

        assert config.base_url == "https://api.fashn.ai/v1"
        assert config.timeout == 120.0

    def test_garment_categories(self):
        """Should have garment categories."""
        assert GarmentCategory.TOPS.value == "tops"
        assert GarmentCategory.BOTTOMS.value == "bottoms"
        assert GarmentCategory.DRESSES.value == "dresses"

    def test_tryon_modes(self):
        """Should have try-on modes."""
        assert TryOnMode.QUALITY.value == "quality"
        assert TryOnMode.BALANCED.value == "balanced"
        assert TryOnMode.FAST.value == "fast"


class TestTripoAgent:
    """Test Tripo3D asset generation agent."""

    def test_instantiate(self):
        """Should instantiate agent."""
        agent = TripoAssetAgent()

        assert agent.name == "tripo_asset"
        assert AgentCapability.THREE_D_GENERATION in agent.get_capabilities()

    def test_config_from_env(self, monkeypatch):
        """Should use the default API URL when no override is configured."""
        monkeypatch.delenv("TRIPO_API_BASE_URL", raising=False)
        config = TripoConfig.from_env()

        assert config.base_url == "https://api.tripo3d.ai/v2"
        assert config.timeout == 300.0

    def test_config_from_env_preserves_base_url_override(self, monkeypatch):
        """Should retain a caller's explicitly configured API URL."""
        override = "https://override.example.test/v2"
        monkeypatch.setenv("TRIPO_API_BASE_URL", override)

        config = TripoConfig.from_env()

        assert config.base_url == override

    def test_model_formats(self):
        """Should have model formats."""
        assert ModelFormat.GLB.value == "glb"
        assert ModelFormat.FBX.value == "fbx"
        assert ModelFormat.USDZ.value == "usdz"

    def test_collection_prompts(self):
        """Should have collection prompts."""
        assert "BLACK_ROSE" in COLLECTION_PROMPTS
        assert "LOVE_HURTS" in COLLECTION_PROMPTS
        assert "SIGNATURE" in COLLECTION_PROMPTS

        black_rose = COLLECTION_PROMPTS["BLACK_ROSE"]
        assert "style" in black_rose
        assert "colors" in black_rose
        assert "mood" in black_rose

    def test_garment_templates(self):
        """Should have garment templates."""
        assert "hoodie" in GARMENT_TEMPLATES
        assert "bomber" in GARMENT_TEMPLATES
        assert "tee" in GARMENT_TEMPLATES

        assert "luxury" in GARMENT_TEMPLATES["hoodie"].lower()

    def test_build_prompt(self):
        """Should build brand-aware prompts."""
        agent = TripoAssetAgent()

        prompt = agent._build_prompt(
            product_name="Heart aRose Bomber",
            collection="BLACK_ROSE",
            garment_type="bomber",
            additional_details="Rose gold zipper",
        )

        assert "Heart aRose Bomber" in prompt
        assert "dark elegance" in prompt  # From collection
        assert "premium bomber jacket" in prompt  # From template
        assert "Rose gold zipper" in prompt


class TestWordPressAssetAgent:
    """Test WordPress asset agent."""

    def test_instantiate(self):
        """Should instantiate agent."""
        agent = WordPressAssetAgent()

        assert agent.name == "wordpress_asset"
        assert AgentCapability.WORDPRESS_MANAGEMENT in agent.get_capabilities()
        assert AgentCapability.PRODUCT_MANAGEMENT in agent.get_capabilities()


class TestAgentCapabilities:
    """Test agent capabilities."""

    def test_all_agents_have_capabilities(self):
        """All agents should declare capabilities."""
        agents = [
            FashnTryOnAgent(),
            TripoAssetAgent(),
            WordPressAssetAgent(),
        ]

        for agent in agents:
            caps = agent.get_capabilities()
            assert len(caps) > 0, f"{agent.name} has no capabilities"

    def test_unique_agent_names(self):
        """Agents should have unique names."""
        agents = [
            FashnTryOnAgent(),
            TripoAssetAgent(),
            WordPressAssetAgent(),
        ]

        names = [a.name for a in agents]
        assert len(names) == len(set(names)), "Duplicate agent names"


class TestTripoConfigValidation:
    """Test Tripo3D configuration validation."""

    def test_config_validate_success(self):
        """Should validate config with API key."""
        config = TripoConfig(api_key="test-key-12345")
        # Should not raise
        config.validate()

    def test_config_validate_missing_key(self):
        """Should raise on missing API key."""
        config = TripoConfig(api_key="")
        with pytest.raises(ValueError, match="TRIPO_API_KEY"):
            config.validate()

    def test_config_texture_settings(self):
        """Should have texture quality settings."""
        config = TripoConfig.from_env()
        assert hasattr(config, "texture_quality")
        assert hasattr(config, "texture_resolution")
        assert hasattr(config, "pbr_enabled")

    def test_config_retry_settings(self):
        """Should have retry settings."""
        config = TripoConfig.from_env()
        assert config.retry_min_wait >= 1
        assert config.retry_max_wait >= config.retry_min_wait


class TestFashnConfigValidation:
    """Test FASHN configuration validation."""

    def test_config_validate_success(self):
        """Should validate config with API key."""
        config = FashnConfig(api_key="test-key-12345")
        # Should not raise
        config.validate()

    def test_config_validate_missing_key(self):
        """Should raise on missing API key."""
        config = FashnConfig(api_key="")
        with pytest.raises(ValueError, match="FASHN_API_KEY"):
            config.validate()

    def test_config_batch_settings(self):
        """Should have batch processing settings."""
        config = FashnConfig.from_env()
        assert hasattr(config, "batch_size")
        assert hasattr(config, "batch_delay")
        assert config.batch_size > 0


class TestWordPressAssetConfig:
    """Test WordPress asset configuration."""

    def test_config_from_env(self):
        """Should create config from environment."""
        config = WordPressAssetConfig.from_env()
        assert config.site_id is not None  # May be empty string from env
        assert config.base_url  # Should have default value

    def test_3d_upload_result_model(self):
        """Should have 3D upload result model."""
        result = Model3DUploadResult(
            success=True,
            media_id=123,
            cdn_url="https://example.com/model.glb",
        )
        assert result.success is True
        assert result.media_id == 123
        assert result.cdn_url == "https://example.com/model.glb"


class TestAssetPipeline:
    """Test asset pipeline orchestrator."""

    def test_pipeline_config_from_env(self):
        """Should create pipeline config from environment."""
        config = PipelineConfig.from_env()
        assert config.enable_3d_generation is True
        assert config.enable_virtual_tryon is True
        assert config.enable_wordpress_upload is True

    def test_pipeline_instantiation(self):
        """Should instantiate pipeline."""
        pipeline = ProductAssetPipeline()
        assert pipeline.config is not None

    def test_product_categories(self):
        """Should have product categories."""
        assert ProductCategory.APPAREL.value == "apparel"
        assert ProductCategory.ACCESSORY.value == "accessory"
        assert ProductCategory.FOOTWEAR.value == "footwear"

    def test_pipeline_stages(self):
        """Should have pipeline stages."""
        assert PipelineStage.INITIALIZED.value == "initialized"
        assert PipelineStage.GENERATING_3D.value == "generating_3d"
        assert PipelineStage.GENERATING_TRYON.value == "generating_tryon"
        assert PipelineStage.UPLOADING_ASSETS.value == "uploading_assets"
        assert PipelineStage.COMPLETED.value == "completed"
        assert PipelineStage.FAILED.value == "failed"

    def test_pipeline_result_model(self):
        """Should create pipeline result."""
        result = AssetPipelineResult(
            product_id="test-123",
            status="processing",
        )
        assert result.product_id == "test-123"
        assert result.status == "processing"
        assert result.stage == PipelineStage.INITIALIZED
        assert result.assets_3d == []
        assert result.assets_tryon == []
        assert result.errors == []

    def test_pipeline_lazy_agent_creation(self):
        """Should lazily create agents."""
        pipeline = ProductAssetPipeline()
        # Agents should not be created yet
        assert pipeline._tripo_agent is None
        assert pipeline._fashn_agent is None
        assert pipeline._wordpress_agent is None

        # Access should create them
        _ = pipeline.tripo_agent
        assert pipeline._tripo_agent is not None
