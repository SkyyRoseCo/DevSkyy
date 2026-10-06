"""Tests for SkyyRose dual agent setup.

Tests the Imagery Agent and Content Agent individually and together.
"""

from __future__ import annotations

import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from agents.base_super_agent import SuperAgentType
from agents.skyyrose_content_agent import (
    BrandDNA,
    ContentRequest,
    ContentStatus,
    ContentType,
    GeneratedContent,
    SkyyRoseContentAgent,
)
from agents.skyyrose_imagery_agent import (
    GeneratedImage,
    ImageryBatch,
    ImageryPurpose,
    ImageryRequest,
    ModelPose,
    SkyyRoseImageryAgent,
)
from llm.base import CompletionResponse
from orchestration.brand_context import Collection

# =============================================================================
# Imagery Agent Tests
# =============================================================================


class TestSkyyRoseImageryAgent:
    """Tests for SkyyRose Imagery Agent."""

    @pytest.fixture
    def agent(self) -> SkyyRoseImageryAgent:
        """Create imagery agent with mocked dependencies."""
        with patch("agents.skyyrose_imagery_agent.BrandContextInjector"):
            agent = SkyyRoseImageryAgent()
        return agent

    @pytest.fixture
    def sample_request(self) -> ImageryRequest:
        """Sample imagery request."""
        return ImageryRequest(
            purpose=ImageryPurpose.HERO_BANNER,
            collection=Collection.SIGNATURE,
            model_pose=ModelPose.EDITORIAL,
            brand_assets=["Gold Rose Pendant", "Silk Scarf"],
            additional_context="Summer campaign hero",
        )

    def test_agent_initialization(self, agent: SkyyRoseImageryAgent) -> None:
        """Agent should initialize with correct config."""
        assert agent.AGENT_NAME == "skyyrose_imagery_agent"
        assert agent.agent_type.value == "creative"
        assert agent._generation_log == []

    def test_build_imagery_prompt_contains_collection(
        self,
        agent: SkyyRoseImageryAgent,
        sample_request: ImageryRequest,
    ) -> None:
        """Prompt should contain collection-specific styling."""
        agent.brand_context = MagicMock()
        agent.brand_context.get_3d_generation_context.return_value = "Brand context here"

        prompt = agent._build_imagery_prompt(sample_request)

        assert "Signature" in prompt
        assert "gold" in prompt.lower()
        assert "regal" in prompt.lower()
        assert "Gold Rose Pendant" in prompt
        assert "Summer campaign hero" in prompt

    def test_build_prompt_black_rose_collection(
        self,
        agent: SkyyRoseImageryAgent,
    ) -> None:
        """Black Rose prompts should include gothic/silver styling."""
        agent.brand_context = MagicMock()
        agent.brand_context.get_3d_generation_context.return_value = ""

        request = ImageryRequest(
            purpose=ImageryPurpose.COLLECTION_SHOWCASE,
            collection=Collection.BLACK_ROSE,
            model_pose=ModelPose.DRAMATIC,
        )
        prompt = agent._build_imagery_prompt(request)

        assert "Black Rose" in prompt
        assert "silver" in prompt.lower() or "midnight" in prompt.lower()
        assert "dramatic" in prompt.lower()

    def test_build_prompt_love_hurts_collection(
        self,
        agent: SkyyRoseImageryAgent,
    ) -> None:
        """Love Hurts prompts should include romantic/rose gold styling."""
        agent.brand_context = MagicMock()
        agent.brand_context.get_3d_generation_context.return_value = ""

        request = ImageryRequest(
            purpose=ImageryPurpose.LIFESTYLE,
            collection=Collection.LOVE_HURTS,
            model_pose=ModelPose.CASUAL_ELEGANT,
        )
        prompt = agent._build_imagery_prompt(request)

        assert "Love Hurts" in prompt
        assert "rose gold" in prompt.lower() or "romantic" in prompt.lower()

    def test_all_purposes_have_directives(self, agent: SkyyRoseImageryAgent) -> None:
        """Every ImageryPurpose should have a corresponding directive."""
        from agents.skyyrose_imagery_agent import PURPOSE_DIRECTIVES

        for purpose in ImageryPurpose:
            assert purpose in PURPOSE_DIRECTIVES, f"Missing directive for {purpose}"

    def test_all_poses_have_directives(self, agent: SkyyRoseImageryAgent) -> None:
        """Every ModelPose should have a corresponding directive."""
        from agents.skyyrose_imagery_agent import POSE_DIRECTIVES

        for pose in ModelPose:
            assert pose in POSE_DIRECTIVES, f"Missing directive for {pose}"

    @pytest.mark.asyncio
    async def test_generate_image_gemini_success(
        self,
        agent: SkyyRoseImageryAgent,
        sample_request: ImageryRequest,
    ) -> None:
        """Should generate image via Gemini successfully."""
        agent.brand_context = MagicMock()
        agent.brand_context.get_3d_generation_context.return_value = ""

        # Mock Gemini provider
        mock_gemini = AsyncMock()
        mock_response = MagicMock()
        mock_response.image_url = "https://cdn.example.com/skyyrose-sig-hero.jpg"
        mock_gemini.generate_product_image = AsyncMock(return_value=mock_response)

        agent._gemini = mock_gemini

        image = await agent.generate_image(sample_request)

        assert image.url == "https://cdn.example.com/skyyrose-sig-hero.jpg"
        assert image.purpose == ImageryPurpose.HERO_BANNER
        assert image.collection == Collection.SIGNATURE
        assert image.provider == "gemini"
        assert len(agent._generation_log) == 1

    @pytest.mark.asyncio
    async def test_generate_image_gemini_fails_uses_fallback(
        self,
        agent: SkyyRoseImageryAgent,
        sample_request: ImageryRequest,
    ) -> None:
        """Should fall back to provider factory when Gemini fails."""
        agent.brand_context = MagicMock()
        agent.brand_context.get_3d_generation_context.return_value = ""

        # Mock Gemini to fail
        mock_gemini = AsyncMock()
        mock_gemini.generate_product_image = AsyncMock(side_effect=Exception("Gemini API error"))
        agent._gemini = mock_gemini

        # Mock provider factory as fallback
        mock_factory = AsyncMock()
        mock_response = MagicMock()
        mock_response.thumbnail_url = "https://fallback.com/image.jpg"
        mock_response.model_url = None
        mock_response.provider = "tripo3d"
        mock_factory.generate = AsyncMock(return_value=mock_response)
        mock_factory.initialize = AsyncMock()
        agent._provider_factory = mock_factory

        image = await agent.generate_image(sample_request)

        assert image.url == "https://fallback.com/image.jpg"
        assert image.provider == "tripo3d"

    @pytest.mark.asyncio
    async def test_generate_batch(
        self,
        agent: SkyyRoseImageryAgent,
    ) -> None:
        """Batch generation should process all requests."""
        agent.brand_context = MagicMock()
        agent.brand_context.get_3d_generation_context.return_value = ""

        # Mock Gemini
        mock_gemini = AsyncMock()
        mock_response = MagicMock()
        mock_response.image_url = "https://cdn.example.com/image.jpg"
        mock_gemini.generate_product_image = AsyncMock(return_value=mock_response)
        agent._gemini = mock_gemini

        requests = [
            ImageryRequest(
                purpose=ImageryPurpose.HERO_BANNER,
                collection=Collection.SIGNATURE,
            ),
            ImageryRequest(
                purpose=ImageryPurpose.LIFESTYLE,
                collection=Collection.BLACK_ROSE,
            ),
        ]

        batch = await agent.generate_batch(requests)

        assert isinstance(batch, ImageryBatch)
        assert len(batch.images) == 2
        assert batch.completed_at is not None

    @pytest.mark.asyncio
    async def test_generate_theme_assets_all_collections(
        self,
        agent: SkyyRoseImageryAgent,
    ) -> None:
        """Theme asset generation should cover all collections."""
        agent.brand_context = MagicMock()
        agent.brand_context.get_3d_generation_context.return_value = ""

        # Mock Gemini
        mock_gemini = AsyncMock()
        mock_response = MagicMock()
        mock_response.image_url = "https://cdn.example.com/image.jpg"
        mock_gemini.generate_product_image = AsyncMock(return_value=mock_response)
        agent._gemini = mock_gemini

        batch = await agent.generate_theme_assets()

        # 5 image types × 3 collections = 15 images
        assert len(batch.images) == 15
        assert len(batch.errors) == 0

    @pytest.mark.asyncio
    async def test_upload_to_wordpress(
        self,
        agent: SkyyRoseImageryAgent,
    ) -> None:
        """Should upload image to WordPress media library."""
        image = GeneratedImage(
            url="https://cdn.example.com/test.jpg",
            purpose=ImageryPurpose.HERO_BANNER,
            collection=Collection.SIGNATURE,
            model_pose=ModelPose.EDITORIAL,
            prompt_used="test prompt",
            provider="gemini",
        )

        # Mock WP client and HTTP download
        mock_wp_client = AsyncMock()
        mock_wp_client.upload_media = AsyncMock(
            return_value={"id": 456, "url": "https://skyyrose.co/image.jpg"}
        )

        mock_response = MagicMock()
        mock_response.content = b"fake image data"
        mock_response.headers = {"content-type": "image/jpeg"}
        mock_response.raise_for_status = MagicMock()

        with patch("httpx.AsyncClient") as mock_client_cls:
            mock_client_instance = AsyncMock()
            mock_client_instance.get = AsyncMock(return_value=mock_response)
            mock_client_instance.__aenter__ = AsyncMock(return_value=mock_client_instance)
            mock_client_instance.__aexit__ = AsyncMock(return_value=False)
            mock_client_cls.return_value = mock_client_instance

            result = await agent.upload_to_wordpress(image, mock_wp_client)

        assert result.wp_media_id == 456
        assert result.uploaded_at is not None

    def test_get_generation_log(self, agent: SkyyRoseImageryAgent) -> None:
        """Should return generation history."""
        agent._generation_log = [
            GeneratedImage(
                url="test.jpg",
                purpose=ImageryPurpose.HERO_BANNER,
                collection=Collection.SIGNATURE,
                model_pose=ModelPose.EDITORIAL,
                prompt_used="test",
                provider="gemini",
            )
        ]

        log = agent.get_generation_log()
        assert len(log) == 1
        assert log[0].collection == Collection.SIGNATURE


# =============================================================================
# Content Agent Tests
# =============================================================================


class TestSkyyRoseContentAgent:
    """Tests for SkyyRose Content Agent."""

    @pytest.fixture
    def agent(self, tmp_path) -> SkyyRoseContentAgent:
        """Create content agent with mocked dependencies."""
        with patch("agents.skyyrose_content_agent.BrandContextInjector") as mock_injector:
            mock_instance = MagicMock()
            mock_instance.get_system_prompt.return_value = "Brand system prompt"
            mock_instance.get_product_context.return_value = "Product context"
            mock_instance.inject.side_effect = lambda msgs, **kwargs: msgs
            mock_injector.return_value = mock_instance
            agent = SkyyRoseContentAgent()
        # Override learning state path to avoid filesystem writes
        agent._learning_state_path = str(tmp_path / "skyyrose_learning.json")
        return agent

    @pytest.fixture
    def sample_request(self) -> ContentRequest:
        """Sample content request."""
        return ContentRequest(
            content_type=ContentType.COLLECTION_PAGE,
            collection=Collection.SIGNATURE,
            title="Signature Collection",
            target_url="/collection/signature/",
            seo_keywords=["skyyrose signature", "luxury jewelry"],
            additional_direction="Focus on the gold aesthetic",
        )

    def test_agent_initialization(self, agent: SkyyRoseContentAgent) -> None:
        """Agent should initialize with correct config."""
        assert agent.AGENT_NAME == "skyyrose_content_agent"
        assert agent.agent_type.value == "creative"
        assert agent._brand_dna is None
        assert agent._content_log == []
        assert agent._learning_records == []

    def test_brand_dna_to_prompt_context(self) -> None:
        """Brand DNA should produce comprehensive prompt context."""
        dna = BrandDNA(
            top_performing_headlines=["Headline A", "Headline B"],
            top_performing_themes=["collection_page", "lifestyle"],
        )
        context = dna.to_prompt_context()

        assert "SKYYROSE" in context
        assert "Luxury Grows from Concrete" not in context
        assert "Signature Collection" in context
        assert "Black Rose Collection" in context
        assert "Love Hurts Collection" in context
        assert "Headline A" in context
        assert "collection_page" in context

    @pytest.mark.asyncio
    async def test_gather_brand_dna_without_wp_client(
        self,
        agent: SkyyRoseContentAgent,
    ) -> None:
        """Should gather brand DNA without WordPress client."""
        dna = await agent.gather_brand_dna()

        assert dna is not None
        assert dna.brand_name == "SkyyRose"
        assert len(dna.collections) == 3
        assert "signature" in dna.collections
        assert "black-rose" in dna.collections
        assert "love-hurts" in dna.collections

    @pytest.mark.asyncio
    async def test_gather_brand_dna_with_wp_client(
        self,
        agent: SkyyRoseContentAgent,
    ) -> None:
        """Should gather existing pages when WP client provided."""
        mock_wp_client = AsyncMock()
        mock_wp_client._wp_request = AsyncMock(
            return_value=[
                {"title": {"rendered": "Home"}, "slug": "home", "link": "/"},
                {"title": {"rendered": "About"}, "slug": "about", "link": "/about/"},
            ]
        )

        dna = await agent.gather_brand_dna(wp_client=mock_wp_client)

        assert "Home" in dna.existing_pages
        assert "About" in dna.existing_pages
        assert "home" in dna.site_navigation_structure

    @pytest.mark.asyncio
    async def test_gather_brand_dna_caches(
        self,
        agent: SkyyRoseContentAgent,
    ) -> None:
        """Should return cached DNA on subsequent calls."""
        dna1 = await agent.gather_brand_dna()
        dna2 = await agent.gather_brand_dna()

        assert dna1 is dna2  # Same object, not re-gathered

    @pytest.mark.asyncio
    async def test_gather_brand_dna_refresh(
        self,
        agent: SkyyRoseContentAgent,
    ) -> None:
        """Should refresh DNA when forced."""
        dna1 = await agent.gather_brand_dna()
        dna2 = await agent.gather_brand_dna(refresh=True)

        assert dna1 is not dna2  # New object after refresh

    @pytest.mark.asyncio
    async def test_generate_content_requires_brand_dna(
        self,
        agent: SkyyRoseContentAgent,
        sample_request: ContentRequest,
    ) -> None:
        """Should gather brand DNA if not loaded before generation."""
        # Mock Gemini
        mock_gemini = AsyncMock()
        mock_gemini.complete = AsyncMock(
            return_value=CompletionResponse(
                content=json.dumps(
                    {
                        "title": "Signature Collection",
                        "body_html": "<h1>Signature Collection</h1><p>Luxury gold.</p>",
                        "excerpt": "Defining luxury.",
                        "seo_title": "SkyyRose Signature Collection",
                        "seo_description": "Luxury gold jewelry collection from SkyyRose Oakland.",
                        "seo_keywords": ["skyyrose", "signature", "gold"],
                    }
                ),
                model="gemini-2.0-flash",
                provider="google",
                total_tokens=150,
                latency_ms=1200.0,
            )
        )
        mock_gemini.connect = AsyncMock()
        agent._gemini = mock_gemini

        # Brand DNA not loaded
        assert agent._brand_dna is None

        content = await agent.generate_content(sample_request)

        # DNA should have been gathered
        assert agent._brand_dna is not None
        # Content should be generated
        assert content.title == "Signature Collection"
        assert "<h1>" in content.body_html

    @pytest.mark.asyncio
    async def test_generate_content_uses_gemini(
        self,
        agent: SkyyRoseContentAgent,
        sample_request: ContentRequest,
    ) -> None:
        """Content generation should route to Gemini."""
        # Pre-load brand DNA
        agent._brand_dna = BrandDNA()

        # Mock Gemini
        mock_gemini = AsyncMock()
        mock_gemini.complete = AsyncMock(
            return_value=CompletionResponse(
                content=json.dumps(
                    {
                        "title": "Test Title",
                        "body_html": "<p>Test body</p>",
                        "excerpt": "Test excerpt",
                        "seo_title": "Test SEO",
                        "seo_description": "Test meta",
                        "seo_keywords": ["test"],
                    }
                ),
                model="gemini-2.0-flash",
                provider="google",
                total_tokens=100,
                latency_ms=800.0,
            )
        )
        mock_gemini.connect = AsyncMock()
        agent._gemini = mock_gemini

        content = await agent.generate_content(sample_request)

        assert mock_gemini.complete.called
        assert content.gemini_tokens_used == 100
        assert content.metadata["gemini_model"] == "gemini-2.0-flash"

    @pytest.mark.asyncio
    async def test_generate_content_parses_json_from_markdown(
        self,
        agent: SkyyRoseContentAgent,
        sample_request: ContentRequest,
    ) -> None:
        """Should extract JSON even when wrapped in markdown code blocks."""
        agent._brand_dna = BrandDNA()

        json_payload = json.dumps(
            {
                "title": "Wrapped Title",
                "body_html": "<p>Body</p>",
                "excerpt": "Excerpt",
                "seo_title": "SEO",
                "seo_description": "Meta",
                "seo_keywords": ["k1"],
            }
        )

        # Gemini often wraps JSON in markdown
        mock_gemini = AsyncMock()
        mock_gemini.complete = AsyncMock(
            return_value=CompletionResponse(
                content=f"Here's the content:\n\n```json\n{json_payload}\n```",
                model="gemini-2.0-flash",
                provider="google",
                total_tokens=80,
                latency_ms=600.0,
            )
        )
        mock_gemini.connect = AsyncMock()
        agent._gemini = mock_gemini

        content = await agent.generate_content(sample_request)

        assert content.title == "Wrapped Title"
        assert content.seo_title == "SEO"

    @pytest.mark.asyncio
    async def test_publish_to_wordpress_as_draft(
        self,
        agent: SkyyRoseContentAgent,
    ) -> None:
        """Should publish to WordPress as draft with brand metadata."""
        content = GeneratedContent(
            content_type=ContentType.COLLECTION_PAGE,
            collection=Collection.SIGNATURE,
            title="Signature Page",
            body_html="<p>Content</p>",
            excerpt="Short excerpt",
            seo_title="SEO Title",
            seo_description="SEO Description",
            correlation_id="test-123",
        )

        mock_wp_client = AsyncMock()
        mock_wp_client.create_post = AsyncMock(return_value={"id": 789, "status": "draft"})

        result = await agent.publish_to_wordpress(content, mock_wp_client, status="draft")

        assert result.wp_post_id == 789
        assert result.status == ContentStatus.DRAFTED

        # Verify brand metadata was included
        call_kwargs = mock_wp_client.create_post.call_args[1]
        assert call_kwargs["meta"]["_skyyrose_collection"] == "SIGNATURE"
        assert call_kwargs["meta"]["_skyyrose_content_agent"] is True

    def test_record_feedback_updates_learning(
        self,
        agent: SkyyRoseContentAgent,
    ) -> None:
        """Feedback should update learning records and brand DNA."""
        agent._brand_dna = BrandDNA()

        # Add a content record
        content = GeneratedContent(
            content_id="content-abc",
            content_type=ContentType.COLLECTION_PAGE,
            collection=Collection.SIGNATURE,
            title="Great Headline",
        )
        agent._content_log.append(content)

        from agents.base_super_agent import LearningRecord

        agent._learning_records.append(
            LearningRecord(
                task_id="content-abc",
                task_type="collection_page",
                prompt_hash="abc123",
                technique_used="gemini_direct",
                llm_provider="google",
                success=True,
                latency_ms=1000.0,
                cost_usd=0.001,
            )
        )

        # Record high score
        agent.record_feedback("content-abc", score=0.95)

        # Should have updated DNA
        assert "Great Headline" in agent._brand_dna.top_performing_headlines
        assert "collection_page" in agent._brand_dna.top_performing_themes

    def test_record_feedback_low_score_doesnt_add_to_top(
        self,
        agent: SkyyRoseContentAgent,
    ) -> None:
        """Low-scoring content should NOT be added to top performers."""
        agent._brand_dna = BrandDNA()

        content = GeneratedContent(
            content_id="content-bad",
            content_type=ContentType.BLOG_POST,
            title="Bad Headline",
        )
        agent._content_log.append(content)

        from agents.base_super_agent import LearningRecord

        agent._learning_records.append(
            LearningRecord(
                task_id="content-bad",
                task_type="blog_post",
                prompt_hash="def456",
                technique_used="gemini_direct",
                llm_provider="google",
                success=True,
                latency_ms=1000.0,
                cost_usd=0.001,
            )
        )

        agent.record_feedback("content-bad", score=0.3)

        assert "Bad Headline" not in agent._brand_dna.top_performing_headlines

    def test_get_learning_summary(
        self,
        agent: SkyyRoseContentAgent,
    ) -> None:
        """Should return learning summary stats."""
        agent._brand_dna = BrandDNA(
            top_performing_headlines=["H1", "H2", "H3"],
            top_performing_themes=["collection_page"],
        )

        from agents.base_super_agent import LearningRecord

        agent._learning_records = [
            LearningRecord(
                task_id="t1",
                task_type="test",
                prompt_hash="h1",
                technique_used="g",
                llm_provider="google",
                success=True,
                latency_ms=1000.0,
                cost_usd=0.0,
                user_feedback=0.8,
            ),
            LearningRecord(
                task_id="t2",
                task_type="test",
                prompt_hash="h2",
                technique_used="g",
                llm_provider="google",
                success=True,
                latency_ms=1000.0,
                cost_usd=0.0,
                user_feedback=0.9,
            ),
        ]

        summary = agent.get_learning_summary()

        assert summary["total_feedback_records"] == 2
        assert summary["avg_feedback_score"] == pytest.approx(0.85)
        assert len(summary["top_headlines"]) == 3

    @pytest.mark.asyncio
    async def test_create_collection_page_convenience(
        self,
        agent: SkyyRoseContentAgent,
    ) -> None:
        """Convenience method should generate collection page content."""
        agent._brand_dna = BrandDNA()

        mock_gemini = AsyncMock()
        mock_gemini.complete = AsyncMock(
            return_value=CompletionResponse(
                content=json.dumps(
                    {
                        "title": "Black Rose Collection",
                        "body_html": "<h1>Black Rose</h1><p>Gothic luxury.</p>",
                        "excerpt": "Into the darkness.",
                        "seo_title": "Black Rose Collection | SkyyRose",
                        "seo_description": "Gothic luxury jewelry.",
                        "seo_keywords": ["black rose", "skyyrose"],
                    }
                ),
                model="gemini-2.0-flash",
                provider="google",
                total_tokens=200,
                latency_ms=1500.0,
            )
        )
        mock_gemini.connect = AsyncMock()
        agent._gemini = mock_gemini

        content = await agent.create_collection_page(Collection.BLACK_ROSE)

        assert "Black Rose" in content.title
        assert content.collection == Collection.BLACK_ROSE

    @pytest.mark.asyncio
    async def test_build_messages_includes_brand_dna(
        self,
        agent: SkyyRoseContentAgent,
        sample_request: ContentRequest,
    ) -> None:
        """Generated messages should contain full brand DNA context."""
        agent._brand_dna = BrandDNA(
            top_performing_headlines=["Top Headline"],
        )

        messages = agent._build_generation_messages(sample_request)

        # System message should contain brand DNA
        system_msg = messages[0]
        assert system_msg.role.value == "system"
        assert "SKYYROSE" in system_msg.content
        assert "Luxury Grows from Concrete" not in system_msg.content
        assert "Top Headline" in system_msg.content

        # User message should contain request details
        user_msg = messages[1]
        assert user_msg.role.value == "user"
        assert "collection_page" in user_msg.content
        assert "Signature" in user_msg.content


# =============================================================================
# Dual Agent Integration Tests
# =============================================================================


class TestDualAgentIntegration:
    """Tests for imagery + content agents working together."""

    @pytest.fixture
    def imagery_agent(self) -> SkyyRoseImageryAgent:
        """Create imagery agent."""
        with patch("agents.skyyrose_imagery_agent.BrandContextInjector"):
            return SkyyRoseImageryAgent()

    @pytest.fixture
    def content_agent(self, tmp_path) -> SkyyRoseContentAgent:
        """Create content agent."""
        with patch("agents.skyyrose_content_agent.BrandContextInjector") as mock_injector:
            mock_instance = MagicMock()
            mock_instance.get_system_prompt.return_value = "Brand prompt"
            mock_instance.get_product_context.return_value = "Product context"
            mock_instance.inject.side_effect = lambda msgs, **kwargs: msgs
            mock_injector.return_value = mock_instance
            agent = SkyyRoseContentAgent()
            agent._learning_state_path = str(tmp_path / "dual_learning.json")
            return agent

    @pytest.mark.asyncio
    async def test_imagery_feeds_content_agent(
        self,
        imagery_agent: SkyyRoseImageryAgent,
        content_agent: SkyyRoseContentAgent,
    ) -> None:
        """Imagery agent output should be usable as content agent input."""
        imagery_agent.brand_context = MagicMock()
        imagery_agent.brand_context.get_3d_generation_context.return_value = ""

        # Generate imagery
        mock_gemini_img = AsyncMock()
        mock_img_resp = MagicMock()
        mock_img_resp.image_url = "https://cdn.skyyrose.co/sig-hero.jpg"
        mock_gemini_img.generate_product_image = AsyncMock(return_value=mock_img_resp)
        imagery_agent._gemini = mock_gemini_img

        img_request = ImageryRequest(
            purpose=ImageryPurpose.HERO_BANNER,
            collection=Collection.SIGNATURE,
        )
        image = await imagery_agent.generate_image(img_request)

        # Feed imagery URLs to content agent
        content_agent._brand_dna = BrandDNA()

        mock_gemini_content = AsyncMock()
        mock_gemini_content.complete = AsyncMock(
            return_value=CompletionResponse(
                content=json.dumps(
                    {
                        "title": "Signature Collection",
                        "body_html": '<h1>Signature</h1><img src="https://cdn.skyyrose.co/sig-hero.jpg" />',
                        "excerpt": "Gold luxury.",
                        "seo_title": "Signature | SkyyRose",
                        "seo_description": "Luxury gold collection.",
                        "seo_keywords": ["signature"],
                    }
                ),
                model="gemini-2.0-flash",
                provider="google",
                total_tokens=120,
                latency_ms=900.0,
            )
        )
        mock_gemini_content.connect = AsyncMock()
        content_agent._gemini = mock_gemini_content

        content_request = ContentRequest(
            content_type=ContentType.COLLECTION_PAGE,
            collection=Collection.SIGNATURE,
            reference_imagery=[image.url],  # Pass imagery agent output
        )
        content = await content_agent.generate_content(content_request)

        # Verify the imagery URL was passed through in the request
        call_args = mock_gemini_content.complete.call_args
        messages = call_args[1].get("messages") or call_args[0][0]
        user_msg_content = next(m.content for m in messages if m.role.value == "user")
        assert "1 images" in user_msg_content  # reference_imagery count

    def test_both_agents_use_same_brand_context(
        self,
        imagery_agent: SkyyRoseImageryAgent,
        content_agent: SkyyRoseContentAgent,
    ) -> None:
        """Both agents should reference SkyyRose brand consistently."""
        assert "SkyyRose" in imagery_agent.SYSTEM_PROMPT
        assert "SkyyRose" in content_agent.SYSTEM_PROMPT
        assert "Luxury Grows from Concrete" not in imagery_agent.SYSTEM_PROMPT
        assert "Luxury Grows from Concrete" not in content_agent.SYSTEM_PROMPT

    def test_both_agents_are_creative_type(
        self,
        imagery_agent: SkyyRoseImageryAgent,
        content_agent: SkyyRoseContentAgent,
    ) -> None:
        """Both agents should be CREATIVE type."""
        assert imagery_agent.agent_type == SuperAgentType.CREATIVE
        assert content_agent.agent_type == SuperAgentType.CREATIVE
