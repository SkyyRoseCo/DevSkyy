# tests/services/test_three_d_providers.py
"""Comprehensive tests for 3D provider implementations.

Tests for:
- TripoProvider (Tripo3D API)
- ReplicateProvider (Replicate API)
- HuggingFaceProvider (HuggingFace Spaces)

Author: DevSkyy Platform Team
"""

from __future__ import annotations

import sys
import tempfile
from datetime import UTC, datetime
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest
from services.three_d.provider_interface import (
    OutputFormat,
    ProviderHealth,
    ProviderStatus,
    ThreeDCapability,
    ThreeDGenerationError,
    ThreeDProviderError,
    ThreeDRequest,
    ThreeDTimeoutError,
)

# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture
def temp_output_dir():
    """Create a temporary output directory for tests."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir


@pytest.fixture
def mock_tripo_config(temp_output_dir):
    """Create mock Tripo provider config."""
    from services.three_d.tripo_provider import TripoProviderConfig

    return TripoProviderConfig(
        api_key="test-tripo-api-key",
        output_dir=temp_output_dir,
        timeout_seconds=60.0,
    )


@pytest.fixture
def mock_replicate_config(temp_output_dir):
    """Create mock Replicate provider config."""
    from services.three_d.replicate_provider import ReplicateProviderConfig

    return ReplicateProviderConfig(
        api_token="test-replicate-token",
        image_to_3d_model="test/model:v1",
        text_to_3d_model="test/text-model:v1",
        timeout_seconds=60.0,
        poll_interval=0.1,
        output_dir=temp_output_dir,
    )


@pytest.fixture
def mock_huggingface_config(temp_output_dir):
    """Create mock HuggingFace provider config."""
    from services.three_d.huggingface_provider import (
        HuggingFaceModel,
        HuggingFaceProviderConfig,
    )

    return HuggingFaceProviderConfig(
        default_text_model=HuggingFaceModel.SHAP_E,
        default_image_model=HuggingFaceModel.TRELLIS,
        output_dir=temp_output_dir,
        texture_size=1024,
        seed=42,
        timeout_seconds=60.0,
    )


@pytest.fixture
def text_request():
    """Create a text-to-3D request."""
    return ThreeDRequest(
        prompt="luxury black hoodie with gold accents",
        product_name="Black Rose Hoodie",
        collection="BLACK_ROSE",
        garment_type="hoodie",
        output_format=OutputFormat.GLB,
        correlation_id="test-correlation-123",
    )


@pytest.fixture
def image_request(temp_output_dir):
    """Create an image-to-3D request."""
    # Create a dummy image file
    image_path = Path(temp_output_dir) / "test_image.jpg"
    image_path.write_bytes(b"fake image data")

    return ThreeDRequest(
        image_path=str(image_path),
        product_name="Test Hoodie",
        output_format=OutputFormat.GLB,
        correlation_id="test-correlation-456",
    )


@pytest.fixture
def image_url_request():
    """Create an image-to-3D request with URL."""
    return ThreeDRequest(
        image_url="https://example.com/product.jpg",
        product_name="Test Product",
        output_format=OutputFormat.GLB,
        correlation_id="test-correlation-789",
    )


# =============================================================================
# TripoProvider Tests
# =============================================================================


class TestTripoProviderConfig:
    """Tests for TripoProviderConfig."""

    def test_config_from_env(self, monkeypatch):
        """Test config creation from environment variables."""
        monkeypatch.setenv("TRIPO_API_KEY", "env-api-key")
        monkeypatch.setenv("THREE_D_OUTPUT_DIR", "/tmp/test-output")

        from services.three_d.tripo_provider import TripoProviderConfig

        config = TripoProviderConfig.from_env()
        assert config.api_key == "env-api-key"
        assert config.output_dir == "/tmp/test-output"
        assert config.timeout_seconds == 300.0

    def test_config_default_values(self, monkeypatch):
        """Test config default values when env vars not set."""
        monkeypatch.delenv("TRIPO_API_KEY", raising=False)
        monkeypatch.delenv("TRIPO3D_API_KEY", raising=False)
        monkeypatch.delenv("THREE_D_OUTPUT_DIR", raising=False)

        from services.three_d.tripo_provider import TripoProviderConfig

        config = TripoProviderConfig()
        assert config.api_key == ""
        assert config.output_dir == "./assets/3d-models-generated"

    def test_config_tripo3d_api_key_fallback(self, monkeypatch):
        """Test that TRIPO3D_API_KEY works as fallback."""
        monkeypatch.delenv("TRIPO_API_KEY", raising=False)
        monkeypatch.setenv("TRIPO3D_API_KEY", "fallback-key")

        from services.three_d.tripo_provider import TripoProviderConfig

        config = TripoProviderConfig.from_env()
        assert config.api_key == "fallback-key"


class TestTripoProvider:
    """Tests for TripoProvider."""

    def test_provider_name(self, mock_tripo_config):
        """Test provider name property."""
        from services.three_d.tripo_provider import TripoProvider

        provider = TripoProvider(mock_tripo_config)
        assert provider.name == "tripo"

    def test_provider_capabilities(self, mock_tripo_config):
        """Test provider capabilities property."""
        from services.three_d.tripo_provider import TripoProvider

        provider = TripoProvider(mock_tripo_config)
        capabilities = provider.capabilities

        assert ThreeDCapability.TEXT_TO_3D in capabilities
        assert ThreeDCapability.IMAGE_TO_3D in capabilities
        assert ThreeDCapability.TEXTURE_GENERATION in capabilities

    def test_generate_correlation_id(self, mock_tripo_config):
        """Test correlation ID generation."""
        from services.three_d.tripo_provider import TripoProvider

        provider = TripoProvider(mock_tripo_config)
        corr_id = provider._generate_correlation_id()

        assert corr_id is not None
        assert len(corr_id) == 36  # UUID format

    @pytest.mark.asyncio
    async def test_generate_from_text_missing_prompt(self, mock_tripo_config):
        """Test generate_from_text raises error when prompt is missing."""
        from services.three_d.tripo_provider import TripoProvider

        provider = TripoProvider(mock_tripo_config)
        request = ThreeDRequest(prompt=None, correlation_id="test-123")

        with pytest.raises(ThreeDProviderError) as exc_info:
            await provider.generate_from_text(request)

        assert "Text prompt is required" in str(exc_info.value)
        assert exc_info.value.provider == "tripo"

    @pytest.mark.asyncio
    async def test_generate_from_text_success(self, mock_tripo_config, text_request):
        """Test successful text-to-3D generation."""
        from services.three_d.tripo_provider import TripoProvider

        provider = TripoProvider(mock_tripo_config)

        mock_result = {
            "task_id": "tripo-task-123",
            "model_url": "https://tripo.ai/models/123.glb",
            "model_path": "/tmp/model.glb",
            "format": "glb",
            "duration_seconds": 30.0,
            "metadata": {"quality": "high"},
        }

        mock_agent = AsyncMock()
        mock_agent._tool_generate_from_text = AsyncMock(return_value=mock_result)

        with patch.object(provider, "_get_agent", return_value=mock_agent):
            response = await provider.generate_from_text(text_request)

        assert response.success is True
        assert response.task_id == "tripo-task-123"
        assert response.model_url == "https://tripo.ai/models/123.glb"
        assert response.provider == "tripo"
        assert response.output_format == OutputFormat.GLB

    @pytest.mark.asyncio
    async def test_generate_from_text_timeout(self, mock_tripo_config, text_request):
        """Test timeout handling in text-to-3D generation."""
        from services.three_d.tripo_provider import TripoProvider

        provider = TripoProvider(mock_tripo_config)

        mock_agent = AsyncMock()
        mock_agent._tool_generate_from_text = AsyncMock(
            side_effect=TimeoutError("Generation timed out")
        )

        with patch.object(provider, "_get_agent", return_value=mock_agent):
            with pytest.raises(ThreeDTimeoutError) as exc_info:
                await provider.generate_from_text(text_request)

        assert "timed out" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_generate_from_text_no_result(self, mock_tripo_config, text_request):
        """Test handling when agent returns no result."""
        from services.three_d.tripo_provider import TripoProvider

        provider = TripoProvider(mock_tripo_config)

        mock_agent = AsyncMock()
        mock_agent._tool_generate_from_text = AsyncMock(return_value=None)

        with patch.object(provider, "_get_agent", return_value=mock_agent):
            with pytest.raises(ThreeDGenerationError) as exc_info:
                await provider.generate_from_text(text_request)

        assert "no result" in str(exc_info.value).lower()

    @pytest.mark.asyncio
    async def test_generate_from_image_missing_source(self, mock_tripo_config):
        """Test generate_from_image raises error when image source is missing."""
        from services.three_d.tripo_provider import TripoProvider

        provider = TripoProvider(mock_tripo_config)
        request = ThreeDRequest(correlation_id="test-123")

        with pytest.raises(ThreeDProviderError) as exc_info:
            await provider.generate_from_image(request)

        assert "Image URL or path is required" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_generate_from_image_success(self, mock_tripo_config, image_request):
        """Test successful image-to-3D generation."""
        from services.three_d.tripo_provider import TripoProvider

        provider = TripoProvider(mock_tripo_config)

        mock_result = {
            "task_id": "tripo-img-task-456",
            "model_url": "https://tripo.ai/models/456.glb",
            "model_path": "/tmp/model.glb",
            "format": "glb",
            "duration_seconds": 45.0,
            "metadata": {},
        }

        mock_agent = AsyncMock()
        mock_agent._tool_generate_from_image = AsyncMock(return_value=mock_result)

        with patch.object(provider, "_get_agent", return_value=mock_agent):
            response = await provider.generate_from_image(image_request)

        assert response.success is True
        assert response.task_id == "tripo-img-task-456"

    @pytest.mark.asyncio
    async def test_generate_from_image_file_not_found(self, mock_tripo_config):
        """Test handling file not found error."""
        from services.three_d.tripo_provider import TripoProvider

        provider = TripoProvider(mock_tripo_config)
        request = ThreeDRequest(
            image_path="/nonexistent/path/image.jpg",
            correlation_id="test-123",
        )

        mock_agent = AsyncMock()
        mock_agent._tool_generate_from_image = AsyncMock(
            side_effect=FileNotFoundError("Image file not found")
        )

        with patch.object(provider, "_get_agent", return_value=mock_agent):
            with pytest.raises(ThreeDProviderError) as exc_info:
                await provider.generate_from_image(request)

        assert "not found" in str(exc_info.value).lower()
        assert exc_info.value.retryable is False

    @pytest.mark.asyncio
    async def test_generate_from_image_connection_error(self, mock_tripo_config, image_request):
        """Test connection error is marked as retryable."""
        from services.three_d.tripo_provider import TripoProvider

        provider = TripoProvider(mock_tripo_config)

        mock_agent = AsyncMock()
        mock_agent._tool_generate_from_image = AsyncMock(
            side_effect=ConnectionError("Network unavailable")
        )

        with patch.object(provider, "_get_agent", return_value=mock_agent):
            with pytest.raises(ThreeDProviderError) as exc_info:
                await provider.generate_from_image(image_request)

        assert exc_info.value.retryable is True

    @pytest.mark.asyncio
    async def test_health_check_no_api_key(self, temp_output_dir):
        """Test health check returns unavailable when API key is missing."""
        from services.three_d.tripo_provider import (
            TripoProvider,
            TripoProviderConfig,
        )

        config = TripoProviderConfig(
            api_key="",
            output_dir=temp_output_dir,
        )
        provider = TripoProvider(config)

        health = await provider.health_check()

        assert health.status == ProviderStatus.UNAVAILABLE
        assert "not configured" in health.error_message.lower()

    @pytest.mark.asyncio
    async def test_health_check_sdk_not_installed(self, mock_tripo_config):
        """Test health check when SDK is not installed."""
        from services.three_d.tripo_provider import TripoProvider

        provider = TripoProvider(mock_tripo_config)

        with (
            patch.dict("sys.modules", {"tripo3d": None}),
            patch("services.three_d.tripo_provider.TripoProvider.health_check") as mock_health,
        ):
            mock_health.return_value = ProviderHealth(
                provider="tripo",
                status=ProviderStatus.UNAVAILABLE,
                capabilities=provider.capabilities,
                last_check=datetime.now(UTC),
                error_message="tripo3d SDK not installed",
            )
            health = await provider.health_check()

        assert health.status == ProviderStatus.UNAVAILABLE

    @pytest.mark.asyncio
    async def test_close_provider(self, mock_tripo_config):
        """Test provider cleanup."""
        from services.three_d.tripo_provider import TripoProvider

        provider = TripoProvider(mock_tripo_config)

        # Create a mock agent
        mock_agent = AsyncMock()
        mock_agent.close = AsyncMock()
        provider._agent = mock_agent

        await provider.close()

        mock_agent.close.assert_called_once()
        assert provider._agent is None


# =============================================================================
# ReplicateProvider Tests
# =============================================================================


class TestReplicateProviderConfig:
    """Tests for ReplicateProviderConfig."""

    def test_config_from_env(self, monkeypatch):
        """Test config creation from environment variables."""
        monkeypatch.setenv("REPLICATE_API_TOKEN", "env-replicate-token")
        monkeypatch.setenv("THREE_D_OUTPUT_DIR", "/tmp/replicate-output")

        from services.three_d.replicate_provider import ReplicateProviderConfig

        config = ReplicateProviderConfig.from_env()
        assert config.api_token == "env-replicate-token"
        assert config.output_dir == "/tmp/replicate-output"

    def test_config_default_models(self, monkeypatch):
        """Test default model configurations."""
        monkeypatch.delenv("REPLICATE_IMAGE_TO_3D_MODEL", raising=False)
        monkeypatch.delenv("REPLICATE_TEXT_TO_3D_MODEL", raising=False)

        from services.three_d.replicate_provider import ReplicateProviderConfig

        config = ReplicateProviderConfig()
        assert "wonder3d" in config.image_to_3d_model
        assert "shap-e" in config.text_to_3d_model


class TestReplicateProvider:
    """Tests for ReplicateProvider."""

    def test_provider_name(self, mock_replicate_config):
        """Test provider name property."""
        from services.three_d.replicate_provider import ReplicateProvider

        provider = ReplicateProvider(mock_replicate_config)
        assert provider.name == "replicate"

    def test_provider_capabilities(self, mock_replicate_config):
        """Test provider capabilities property."""
        from services.three_d.replicate_provider import ReplicateProvider

        provider = ReplicateProvider(mock_replicate_config)
        capabilities = provider.capabilities

        assert ThreeDCapability.IMAGE_TO_3D in capabilities
        assert ThreeDCapability.TEXT_TO_3D in capabilities

    @pytest.mark.asyncio
    async def test_generate_from_text_missing_prompt(self, mock_replicate_config):
        """Test generate_from_text raises error when prompt is missing."""
        from services.three_d.replicate_provider import ReplicateProvider

        provider = ReplicateProvider(mock_replicate_config)
        request = ThreeDRequest(prompt=None, correlation_id="test-123")

        with pytest.raises(ThreeDProviderError) as exc_info:
            await provider.generate_from_text(request)

        assert "Text prompt is required" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_generate_from_text_success(
        self, mock_replicate_config, text_request, temp_output_dir
    ):
        """Test successful text-to-3D generation."""
        from services.ml.replicate_client import (
            ReplicatePrediction,
            ReplicatePredictionStatus,
        )
        from services.three_d.replicate_provider import ReplicateProvider

        provider = ReplicateProvider(mock_replicate_config)

        mock_prediction = ReplicatePrediction(
            id="pred-123",
            status=ReplicatePredictionStatus.SUCCEEDED,
            output=["https://replicate.com/output/model.glb"],
        )

        mock_client = AsyncMock()
        mock_client.run_prediction = AsyncMock(return_value=mock_prediction)
        mock_client.connect = AsyncMock()

        # Create a test model file
        model_content = b"fake GLB content"
        mock_response = MagicMock()
        mock_response.content = model_content
        mock_response.raise_for_status = MagicMock()

        mock_http_client = AsyncMock()
        mock_http_client.get = AsyncMock(return_value=mock_response)
        mock_http_client.is_closed = False

        with (
            patch.object(provider, "_get_client", return_value=mock_client),
            patch.object(provider, "_get_http_client", return_value=mock_http_client),
        ):
            response = await provider.generate_from_text(text_request)

        assert response.success is True
        assert response.provider == "replicate"
        assert response.model_url == "https://replicate.com/output/model.glb"

    @pytest.mark.asyncio
    async def test_generate_from_text_prediction_failed(self, mock_replicate_config, text_request):
        """Test handling of failed prediction."""
        from services.ml.replicate_client import (
            ReplicatePrediction,
            ReplicatePredictionStatus,
        )
        from services.three_d.replicate_provider import ReplicateProvider

        provider = ReplicateProvider(mock_replicate_config)

        mock_prediction = ReplicatePrediction(
            id="pred-123",
            status=ReplicatePredictionStatus.FAILED,
            error="Model failed to generate",
        )

        mock_client = AsyncMock()
        mock_client.run_prediction = AsyncMock(return_value=mock_prediction)

        with patch.object(provider, "_get_client", return_value=mock_client):
            with pytest.raises(ThreeDGenerationError) as exc_info:
                await provider.generate_from_text(text_request)

        assert "failed" in str(exc_info.value).lower()

    @pytest.mark.asyncio
    async def test_generate_from_text_no_output(self, mock_replicate_config, text_request):
        """Test handling when prediction returns no output URL."""
        from services.ml.replicate_client import (
            ReplicatePrediction,
            ReplicatePredictionStatus,
        )
        from services.three_d.replicate_provider import ReplicateProvider

        provider = ReplicateProvider(mock_replicate_config)

        mock_prediction = ReplicatePrediction(
            id="pred-123",
            status=ReplicatePredictionStatus.SUCCEEDED,
            output=None,
        )

        mock_client = AsyncMock()
        mock_client.run_prediction = AsyncMock(return_value=mock_prediction)

        with patch.object(provider, "_get_client", return_value=mock_client):
            with pytest.raises(ThreeDGenerationError) as exc_info:
                await provider.generate_from_text(text_request)

        assert "No model URL" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_generate_from_text_timeout(self, mock_replicate_config, text_request):
        """Test timeout handling in text-to-3D generation."""
        from services.ml.replicate_client import ReplicateTimeoutError
        from services.three_d.replicate_provider import ReplicateProvider

        provider = ReplicateProvider(mock_replicate_config)

        mock_client = AsyncMock()
        mock_client.run_prediction = AsyncMock(
            side_effect=ReplicateTimeoutError("Prediction timed out")
        )

        with patch.object(provider, "_get_client", return_value=mock_client):
            with pytest.raises(ThreeDTimeoutError):
                await provider.generate_from_text(text_request)

    @pytest.mark.asyncio
    async def test_generate_from_image_missing_source(self, mock_replicate_config):
        """Test generate_from_image raises error when image source is missing."""
        from services.three_d.replicate_provider import ReplicateProvider

        provider = ReplicateProvider(mock_replicate_config)
        request = ThreeDRequest(correlation_id="test-123")

        with pytest.raises(ThreeDProviderError) as exc_info:
            await provider.generate_from_image(request)

        assert "Image URL or path is required" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_generate_from_image_success(
        self, mock_replicate_config, image_url_request, temp_output_dir
    ):
        """Test successful image-to-3D generation."""
        from services.ml.replicate_client import (
            ReplicatePrediction,
            ReplicatePredictionStatus,
        )
        from services.three_d.replicate_provider import ReplicateProvider

        provider = ReplicateProvider(mock_replicate_config)

        mock_prediction = ReplicatePrediction(
            id="pred-img-456",
            status=ReplicatePredictionStatus.SUCCEEDED,
            output="https://replicate.com/output/3d_model.glb",
        )

        mock_client = AsyncMock()
        mock_client.image_to_3d = AsyncMock(return_value=mock_prediction)

        mock_response = MagicMock()
        mock_response.content = b"fake GLB content"
        mock_response.raise_for_status = MagicMock()

        mock_http_client = AsyncMock()
        mock_http_client.get = AsyncMock(return_value=mock_response)
        mock_http_client.is_closed = False

        with (
            patch.object(provider, "_get_client", return_value=mock_client),
            patch.object(provider, "_get_http_client", return_value=mock_http_client),
        ):
            response = await provider.generate_from_image(image_url_request)

        assert response.success is True
        assert response.provider == "replicate"
        assert response.model_url == "https://replicate.com/output/3d_model.glb"

    @pytest.mark.asyncio
    async def test_download_model_http_error(self, mock_replicate_config):
        """Test download model HTTP error handling."""
        from services.three_d.replicate_provider import ReplicateProvider

        provider = ReplicateProvider(mock_replicate_config)

        mock_http_client = AsyncMock()
        mock_http_client.get = AsyncMock(side_effect=httpx.HTTPError("Connection failed"))
        mock_http_client.is_closed = False

        with patch.object(provider, "_get_http_client", return_value=mock_http_client):
            with pytest.raises(ThreeDProviderError) as exc_info:
                await provider._download_model(
                    "https://example.com/model.glb",
                    OutputFormat.GLB,
                    "test-corr-id",
                )

        assert "Failed to download" in str(exc_info.value)
        assert exc_info.value.retryable is True

    @pytest.mark.asyncio
    async def test_health_check_no_api_token(self, temp_output_dir):
        """Test health check returns unavailable when API token is missing."""
        from services.three_d.replicate_provider import (
            ReplicateProvider,
            ReplicateProviderConfig,
        )

        config = ReplicateProviderConfig(
            api_token="",
            output_dir=temp_output_dir,
        )
        provider = ReplicateProvider(config)

        health = await provider.health_check()

        assert health.status == ProviderStatus.UNAVAILABLE
        assert "not configured" in health.error_message.lower()

    @pytest.mark.asyncio
    async def test_health_check_success(self, mock_replicate_config):
        """Test successful health check."""
        from services.three_d.replicate_provider import ReplicateProvider

        provider = ReplicateProvider(mock_replicate_config)

        mock_client = AsyncMock()
        mock_client.connect = AsyncMock()

        with patch.object(provider, "_get_client", return_value=mock_client):
            health = await provider.health_check()

        assert health.status == ProviderStatus.AVAILABLE
        assert health.latency_ms is not None

    @pytest.mark.asyncio
    async def test_health_check_connection_error(self, mock_replicate_config):
        """Test health check when connection fails."""
        from services.three_d.replicate_provider import ReplicateProvider

        provider = ReplicateProvider(mock_replicate_config)

        mock_client = AsyncMock()
        mock_client.connect = AsyncMock(side_effect=Exception("Connection failed"))

        with patch.object(provider, "_get_client", return_value=mock_client):
            health = await provider.health_check()

        assert health.status == ProviderStatus.UNAVAILABLE
        assert "Connection failed" in health.error_message

    @pytest.mark.asyncio
    async def test_close_provider(self, mock_replicate_config):
        """Test provider cleanup."""
        from services.three_d.replicate_provider import ReplicateProvider

        provider = ReplicateProvider(mock_replicate_config)

        mock_client = AsyncMock()
        mock_client.close = AsyncMock()
        provider._client = mock_client

        mock_http_client = AsyncMock()
        mock_http_client.is_closed = False
        mock_http_client.aclose = AsyncMock()
        provider._http_client = mock_http_client

        await provider.close()

        mock_client.close.assert_called_once()
        mock_http_client.aclose.assert_called_once()
        assert provider._client is None
        assert provider._http_client is None


# =============================================================================
# HuggingFaceProvider Tests
# =============================================================================


class TestHuggingFaceProviderConfig:
    """Tests for HuggingFaceProviderConfig."""

    def test_config_from_env(self, monkeypatch):
        """Test config creation from environment variables."""
        monkeypatch.setenv("THREE_D_OUTPUT_DIR", "/tmp/hf-output")

        from services.three_d.huggingface_provider import HuggingFaceProviderConfig

        config = HuggingFaceProviderConfig.from_env()
        assert config.output_dir == "/tmp/hf-output"

    def test_config_default_values(self):
        """Test default configuration values."""
        from services.three_d.huggingface_provider import (
            HuggingFaceModel,
            HuggingFaceProviderConfig,
        )

        config = HuggingFaceProviderConfig()
        assert config.default_text_model == HuggingFaceModel.SHAP_E
        assert config.default_image_model == HuggingFaceModel.TRELLIS
        assert config.texture_size == 1024
        assert config.seed == 42


class TestHuggingFaceModel:
    """Tests for HuggingFaceModel enum."""

    def test_all_models_defined(self):
        """Test all expected models are defined."""
        from services.three_d.huggingface_provider import HuggingFaceModel

        assert HuggingFaceModel.TRELLIS.value == "trellis"
        assert HuggingFaceModel.TRIPOSR.value == "triposr"
        assert HuggingFaceModel.INSTANTMESH.value == "instantmesh"
        assert HuggingFaceModel.SHAP_E.value == "shap_e"
        assert HuggingFaceModel.HUNYUAN3D.value == "hunyuan3d"

    def test_model_spaces_mapping(self):
        """Test model to space mapping exists for all models."""
        from services.three_d.huggingface_provider import (
            HUGGINGFACE_SPACES,
            HuggingFaceModel,
        )

        for model in HuggingFaceModel:
            assert model in HUGGINGFACE_SPACES
            assert HUGGINGFACE_SPACES[model]  # Not empty

    def test_model_capabilities_mapping(self):
        """Test model capabilities mapping exists for all models."""
        from services.three_d.huggingface_provider import (
            MODEL_CAPABILITIES,
            HuggingFaceModel,
        )

        for model in HuggingFaceModel:
            assert model in MODEL_CAPABILITIES
            assert len(MODEL_CAPABILITIES[model]) > 0


class TestHuggingFaceProvider:
    """Tests for HuggingFaceProvider."""

    def test_provider_name(self, mock_huggingface_config):
        """Test provider name property."""
        from services.three_d.huggingface_provider import HuggingFaceProvider

        provider = HuggingFaceProvider(mock_huggingface_config)
        assert provider.name == "huggingface"

    def test_provider_capabilities(self, mock_huggingface_config):
        """Test provider capabilities property."""
        from services.three_d.huggingface_provider import HuggingFaceProvider

        provider = HuggingFaceProvider(mock_huggingface_config)
        capabilities = provider.capabilities

        assert ThreeDCapability.TEXT_TO_3D in capabilities
        assert ThreeDCapability.IMAGE_TO_3D in capabilities
        assert ThreeDCapability.MULTI_VIEW in capabilities

    def test_select_model_from_metadata(self, mock_huggingface_config):
        """Test model selection from request metadata."""
        from services.three_d.huggingface_provider import (
            HuggingFaceModel,
            HuggingFaceProvider,
        )

        provider = HuggingFaceProvider(mock_huggingface_config)
        request = ThreeDRequest(
            prompt="test",
            metadata={"hf_model": "triposr"},
        )

        model = provider._select_model(request)
        assert model == HuggingFaceModel.TRIPOSR

    def test_select_model_text_request(self, mock_huggingface_config):
        """Test model selection for text request."""
        from services.three_d.huggingface_provider import (
            HuggingFaceModel,
            HuggingFaceProvider,
        )

        provider = HuggingFaceProvider(mock_huggingface_config)
        request = ThreeDRequest(prompt="test prompt")

        model = provider._select_model(request)
        assert model == HuggingFaceModel.SHAP_E

    def test_select_model_image_request(self, mock_huggingface_config):
        """Test model selection for image request."""
        from services.three_d.huggingface_provider import (
            HuggingFaceModel,
            HuggingFaceProvider,
        )

        provider = HuggingFaceProvider(mock_huggingface_config)
        request = ThreeDRequest(image_url="https://example.com/image.jpg")

        model = provider._select_model(request)
        assert model == HuggingFaceModel.TRELLIS

    def test_select_model_invalid_metadata(self, mock_huggingface_config):
        """Test model selection with invalid metadata falls back to default."""
        from services.three_d.huggingface_provider import (
            HuggingFaceModel,
            HuggingFaceProvider,
        )

        provider = HuggingFaceProvider(mock_huggingface_config)
        request = ThreeDRequest(
            prompt="test",
            metadata={"hf_model": "nonexistent_model"},
        )

        model = provider._select_model(request)
        assert model == HuggingFaceModel.SHAP_E  # Falls back to default text model

    @pytest.mark.asyncio
    async def test_generate_from_text_missing_prompt(self, mock_huggingface_config):
        """Test generate_from_text raises error when prompt is missing."""
        from services.three_d.huggingface_provider import HuggingFaceProvider

        provider = HuggingFaceProvider(mock_huggingface_config)
        request = ThreeDRequest(prompt=None, correlation_id="test-123")

        with pytest.raises(ThreeDProviderError) as exc_info:
            await provider.generate_from_text(request)

        assert "Text prompt is required" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_generate_from_text_unsupported_model(self, mock_huggingface_config):
        """Test error when model doesn't support text-to-3D."""
        from services.three_d.huggingface_provider import HuggingFaceProvider

        provider = HuggingFaceProvider(mock_huggingface_config)
        request = ThreeDRequest(
            prompt="test prompt",
            metadata={"hf_model": "trellis"},  # TRELLIS doesn't support text-to-3D
            correlation_id="test-123",
        )

        with pytest.raises(ThreeDProviderError) as exc_info:
            await provider.generate_from_text(request)

        assert "does not support text-to-3D" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_generate_from_text_gradio_not_installed(
        self, mock_huggingface_config, text_request
    ):
        """Test error handling when gradio_client is not installed."""
        from services.three_d.huggingface_provider import HuggingFaceProvider

        provider = HuggingFaceProvider(mock_huggingface_config)

        with (
            patch.dict("sys.modules", {"gradio_client": None}),
            patch(
                "services.three_d.huggingface_provider.HuggingFaceProvider._run_shap_e"
            ) as mock_run,
        ):
            mock_run.side_effect = ThreeDProviderError(
                "gradio_client not installed",
                provider="huggingface",
                correlation_id=text_request.correlation_id,
            )
            with pytest.raises(ThreeDProviderError) as exc_info:
                await provider.generate_from_text(text_request)

        assert "gradio_client" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_generate_from_text_success(
        self, mock_huggingface_config, text_request, temp_output_dir
    ):
        """Test successful text-to-3D generation."""
        from services.three_d.huggingface_provider import HuggingFaceProvider

        provider = HuggingFaceProvider(mock_huggingface_config)

        # Create a temporary model file
        temp_model = Path(temp_output_dir) / "temp_model.glb"
        temp_model.write_bytes(b"fake GLB content")

        with patch.object(
            provider,
            "_run_shap_e",
            return_value={"model_path": str(temp_model)},
        ):
            response = await provider.generate_from_text(text_request)

        assert response.success is True
        assert "huggingface" in response.provider
        assert response.output_format == OutputFormat.GLB

    @pytest.mark.asyncio
    async def test_generate_from_text_timeout(self, mock_huggingface_config, text_request):
        """Test timeout handling in text-to-3D generation."""
        from services.three_d.huggingface_provider import HuggingFaceProvider

        provider = HuggingFaceProvider(mock_huggingface_config)

        with (
            patch.object(
                provider,
                "_run_shap_e",
                side_effect=TimeoutError("Generation timed out"),
            ),
            pytest.raises(ThreeDTimeoutError),
        ):
            await provider.generate_from_text(text_request)

    @pytest.mark.asyncio
    async def test_generate_from_image_missing_source(self, mock_huggingface_config):
        """Test generate_from_image raises error when image source is missing."""
        from services.three_d.huggingface_provider import HuggingFaceProvider

        provider = HuggingFaceProvider(mock_huggingface_config)
        request = ThreeDRequest(correlation_id="test-123")

        with pytest.raises(ThreeDProviderError) as exc_info:
            await provider.generate_from_image(request)

        assert "Image URL or path is required" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_generate_from_image_unsupported_model(self, mock_huggingface_config):
        """Test error when model doesn't support image-to-3D."""
        from services.three_d.huggingface_provider import HuggingFaceProvider

        provider = HuggingFaceProvider(mock_huggingface_config)
        request = ThreeDRequest(
            image_url="https://example.com/image.jpg",
            metadata={"hf_model": "shap_e"},  # SHAP-E doesn't support image-to-3D
            correlation_id="test-123",
        )

        with pytest.raises(ThreeDProviderError) as exc_info:
            await provider.generate_from_image(request)

        assert "does not support image-to-3D" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_generate_from_image_success_trellis(
        self, mock_huggingface_config, image_request, temp_output_dir
    ):
        """Test successful image-to-3D generation with TRELLIS."""
        from services.three_d.huggingface_provider import HuggingFaceProvider

        provider = HuggingFaceProvider(mock_huggingface_config)

        temp_model = Path(temp_output_dir) / "temp_model.glb"
        temp_model.write_bytes(b"fake GLB content")

        with patch.object(
            provider,
            "_run_trellis",
            return_value={
                "model_path": str(temp_model),
                "video_info": {},
                "download_path": str(temp_model),
            },
        ):
            response = await provider.generate_from_image(image_request)

        assert response.success is True
        assert "trellis" in response.provider

    @pytest.mark.asyncio
    async def test_generate_from_image_success_triposr(
        self, mock_huggingface_config, image_request, temp_output_dir
    ):
        """Test successful image-to-3D generation with TripoSR."""
        from services.three_d.huggingface_provider import HuggingFaceProvider

        provider = HuggingFaceProvider(mock_huggingface_config)
        image_request.metadata = {"hf_model": "triposr"}

        temp_model = Path(temp_output_dir) / "temp_model.glb"
        temp_model.write_bytes(b"fake GLB content")

        with patch.object(
            provider,
            "_run_triposr",
            return_value={"model_path": str(temp_model)},
        ):
            response = await provider.generate_from_image(image_request)

        assert response.success is True
        assert "triposr" in response.provider

    @pytest.mark.asyncio
    async def test_generate_from_image_file_size_included(
        self, mock_huggingface_config, image_request, temp_output_dir
    ):
        """Test that file size is included in response."""
        from services.three_d.huggingface_provider import HuggingFaceProvider

        provider = HuggingFaceProvider(mock_huggingface_config)

        content = b"fake GLB content with some size"
        temp_model = Path(temp_output_dir) / "temp_model.glb"
        temp_model.write_bytes(content)

        with patch.object(
            provider,
            "_run_trellis",
            return_value={
                "model_path": str(temp_model),
                "video_info": {},
                "download_path": str(temp_model),
            },
        ):
            response = await provider.generate_from_image(image_request)

        assert response.file_size_bytes is not None
        assert response.file_size_bytes > 0

    @pytest.mark.asyncio
    async def test_health_check_gradio_not_available(self, mock_huggingface_config):
        """Test health check when gradio_client is not available."""
        from services.three_d.huggingface_provider import HuggingFaceProvider

        provider = HuggingFaceProvider(mock_huggingface_config)

        with (
            patch.dict("sys.modules", {"gradio_client": None}),
            patch(
                "services.three_d.huggingface_provider.HuggingFaceProvider.health_check"
            ) as mock_health,
        ):
            mock_health.return_value = ProviderHealth(
                provider="huggingface",
                status=ProviderStatus.UNAVAILABLE,
                capabilities=provider.capabilities,
                last_check=datetime.now(UTC),
                error_message="gradio_client not installed",
            )
            health = await provider.health_check()

        assert health.status == ProviderStatus.UNAVAILABLE

    @pytest.mark.asyncio
    async def test_health_check_success(self, mock_huggingface_config):
        """Test successful health check."""
        from services.three_d.huggingface_provider import HuggingFaceProvider

        provider = HuggingFaceProvider(mock_huggingface_config)

        # Mock the gradio_client import inside health_check
        mock_client_class = MagicMock()
        mock_gradio_module = MagicMock()
        mock_gradio_module.Client = mock_client_class

        with patch.dict("sys.modules", {"gradio_client": mock_gradio_module}):
            health = await provider.health_check()

        assert health.provider == "huggingface"
        assert health.status == ProviderStatus.AVAILABLE
        assert health.latency_ms is not None

    @pytest.mark.asyncio
    async def test_close_provider(self, mock_huggingface_config):
        """Test provider cleanup (no-op for HuggingFace)."""
        from services.three_d.huggingface_provider import HuggingFaceProvider

        provider = HuggingFaceProvider(mock_huggingface_config)

        # Should not raise
        await provider.close()

    @pytest.mark.asyncio
    async def test_generate_from_image_instantmesh_fallback(
        self, mock_huggingface_config, temp_output_dir
    ):
        """Test image-to-3D generation with InstantMesh falls back to TRELLIS."""
        from services.three_d.huggingface_provider import HuggingFaceProvider

        provider = HuggingFaceProvider(mock_huggingface_config)

        request = ThreeDRequest(
            image_url="https://example.com/image.jpg",
            metadata={"hf_model": "instantmesh"},
            correlation_id="test-instantmesh",
        )

        temp_model = Path(temp_output_dir) / "temp_model.glb"
        temp_model.write_bytes(b"fake GLB content")

        with patch.object(
            provider,
            "_run_trellis",
            return_value={
                "model_path": str(temp_model),
                "video_info": {},
                "download_path": str(temp_model),
            },
        ):
            response = await provider.generate_from_image(request)

        assert response.success is True
        # InstantMesh falls back to TRELLIS

    @pytest.mark.asyncio
    async def test_generate_from_image_hunyuan3d_fallback(
        self, mock_huggingface_config, temp_output_dir
    ):
        """Test image-to-3D generation with Hunyuan3D falls back to TRELLIS."""
        from services.three_d.huggingface_provider import HuggingFaceProvider

        provider = HuggingFaceProvider(mock_huggingface_config)

        request = ThreeDRequest(
            image_url="https://example.com/image.jpg",
            metadata={"hf_model": "hunyuan3d"},
            correlation_id="test-hunyuan3d",
        )

        temp_model = Path(temp_output_dir) / "temp_model.glb"
        temp_model.write_bytes(b"fake GLB content")

        with patch.object(
            provider,
            "_run_trellis",
            return_value={
                "model_path": str(temp_model),
                "video_info": {},
                "download_path": str(temp_model),
            },
        ):
            response = await provider.generate_from_image(request)

        assert response.success is True

    @pytest.mark.asyncio
    async def test_generate_from_text_hunyuan3d_uses_shap_e(
        self, mock_huggingface_config, temp_output_dir
    ):
        """Test text-to-3D generation with Hunyuan3D uses SHAP-E as fallback."""
        from services.three_d.huggingface_provider import HuggingFaceProvider

        provider = HuggingFaceProvider(mock_huggingface_config)

        request = ThreeDRequest(
            prompt="test luxury product",
            metadata={"hf_model": "hunyuan3d"},
            correlation_id="test-hunyuan3d-text",
        )

        temp_model = Path(temp_output_dir) / "temp_model.glb"
        temp_model.write_bytes(b"fake GLB content")

        with patch.object(
            provider,
            "_run_shap_e",
            return_value={"model_path": str(temp_model)},
        ):
            response = await provider.generate_from_text(request)

        assert response.success is True

    @pytest.mark.asyncio
    async def test_generate_from_image_general_exception(
        self, mock_huggingface_config, image_request
    ):
        """Test general exception handling in image-to-3D generation."""
        from services.three_d.huggingface_provider import HuggingFaceProvider

        provider = HuggingFaceProvider(mock_huggingface_config)

        with (
            patch.object(
                provider,
                "_run_trellis",
                side_effect=RuntimeError("Unexpected error"),
            ),
            pytest.raises(ThreeDGenerationError) as exc_info,
        ):
            await provider.generate_from_image(image_request)

        assert "Unexpected error" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_generate_from_text_general_exception(
        self, mock_huggingface_config, text_request
    ):
        """Test general exception handling in text-to-3D generation."""
        from services.three_d.huggingface_provider import HuggingFaceProvider

        provider = HuggingFaceProvider(mock_huggingface_config)

        with (
            patch.object(
                provider,
                "_run_shap_e",
                side_effect=RuntimeError("Unexpected error"),
            ),
            pytest.raises(ThreeDGenerationError) as exc_info,
        ):
            await provider.generate_from_text(text_request)

        assert "Unexpected error" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_health_check_returns_provider_health(self, mock_huggingface_config):
        """Test health check returns valid ProviderHealth object."""
        from services.three_d.huggingface_provider import HuggingFaceProvider

        provider = HuggingFaceProvider(mock_huggingface_config)

        # Run health check
        health = await provider.health_check()

        # Verify it returns a ProviderHealth object with expected properties
        assert health.provider == "huggingface"
        assert isinstance(health.capabilities, list)
        assert health.last_check is not None
        # Status depends on whether gradio_client is installed


# =============================================================================
# Integration Tests (Common Patterns)
# =============================================================================


class TestProviderCommonPatterns:
    """Test common patterns across all providers."""

    @pytest.mark.asyncio
    async def test_all_providers_have_required_attributes(
        self, mock_tripo_config, mock_replicate_config, mock_huggingface_config
    ):
        """Test all providers implement required I3DProvider attributes."""
        from services.three_d.huggingface_provider import HuggingFaceProvider
        from services.three_d.replicate_provider import ReplicateProvider
        from services.three_d.tripo_provider import TripoProvider

        providers = [
            TripoProvider(mock_tripo_config),
            ReplicateProvider(mock_replicate_config),
            HuggingFaceProvider(mock_huggingface_config),
        ]

        for provider in providers:
            # Test name property
            assert isinstance(provider.name, str)
            assert len(provider.name) > 0

            # Test capabilities property
            capabilities = provider.capabilities
            assert isinstance(capabilities, list)
            assert all(isinstance(c, ThreeDCapability) for c in capabilities)

            # Test methods exist
            assert hasattr(provider, "generate_from_text")
            assert hasattr(provider, "generate_from_image")
            assert hasattr(provider, "health_check")
            assert hasattr(provider, "close")

    @pytest.mark.asyncio
    async def test_all_providers_generate_correlation_ids(
        self, mock_tripo_config, mock_replicate_config, mock_huggingface_config
    ):
        """Test all providers can generate correlation IDs."""
        from services.three_d.huggingface_provider import HuggingFaceProvider
        from services.three_d.replicate_provider import ReplicateProvider
        from services.three_d.tripo_provider import TripoProvider

        providers = [
            TripoProvider(mock_tripo_config),
            ReplicateProvider(mock_replicate_config),
            HuggingFaceProvider(mock_huggingface_config),
        ]

        for provider in providers:
            corr_id = provider._generate_correlation_id()
            assert corr_id is not None
            assert len(corr_id) == 36  # UUID format

    def test_output_directory_created(self, mock_replicate_config, mock_huggingface_config):
        """Test that providers create output directory on initialization."""
        from services.three_d.huggingface_provider import HuggingFaceProvider
        from services.three_d.replicate_provider import ReplicateProvider

        # These providers create output directory in __init__
        ReplicateProvider(mock_replicate_config)
        HuggingFaceProvider(mock_huggingface_config)

        assert Path(mock_replicate_config.output_dir).exists()
        assert Path(mock_huggingface_config.output_dir).exists()


# =============================================================================
# ThreeDRequest Tests
# =============================================================================


class TestThreeDRequest:
    """Tests for ThreeDRequest model."""

    def test_is_text_request(self):
        """Test is_text_request method."""
        text_req = ThreeDRequest(prompt="test prompt")
        image_req = ThreeDRequest(image_url="https://example.com/image.jpg")

        assert text_req.is_text_request() is True
        assert image_req.is_text_request() is False

    def test_is_image_request(self):
        """Test is_image_request method."""
        text_req = ThreeDRequest(prompt="test prompt")
        image_url_req = ThreeDRequest(image_url="https://example.com/image.jpg")
        image_path_req = ThreeDRequest(image_path="/path/to/image.jpg")

        assert text_req.is_image_request() is False
        assert image_url_req.is_image_request() is True
        assert image_path_req.is_image_request() is True

    def test_get_image_source_url(self):
        """Test get_image_source returns URL when set."""
        request = ThreeDRequest(image_url="https://example.com/image.jpg")
        assert request.get_image_source() == "https://example.com/image.jpg"

    def test_get_image_source_path(self):
        """Test get_image_source returns path when set."""
        request = ThreeDRequest(image_path="/path/to/image.jpg")
        assert request.get_image_source() == "/path/to/image.jpg"

    def test_get_image_source_prefers_url(self):
        """Test get_image_source prefers URL over path."""
        request = ThreeDRequest(
            image_url="https://example.com/image.jpg",
            image_path="/path/to/image.jpg",
        )
        assert request.get_image_source() == "https://example.com/image.jpg"

    def test_default_values(self):
        """Test default values are set correctly."""
        request = ThreeDRequest()

        assert request.output_format == OutputFormat.GLB
        assert request.texture_size == 1024
        assert request.metadata == {}


# =============================================================================
# Error Classes Tests
# =============================================================================


class TestErrorClasses:
    """Tests for error classes."""

    def test_three_d_provider_error(self):
        """Test ThreeDProviderError initialization."""
        error = ThreeDProviderError(
            "Test error",
            provider="test_provider",
            correlation_id="test-123",
            retryable=True,
        )

        assert "Test error" in str(error)
        assert error.provider == "test_provider"
        assert error.retryable is True

    def test_three_d_generation_error(self):
        """Test ThreeDGenerationError initialization."""
        error = ThreeDGenerationError(
            "Generation failed",
            task_id="task-123",
            provider="test_provider",
            correlation_id="test-456",
        )

        assert "Generation failed" in str(error)
        assert error.task_id == "task-123"
        assert error.provider == "test_provider"

    def test_three_d_timeout_error(self):
        """Test ThreeDTimeoutError initialization."""
        error = ThreeDTimeoutError(
            "Timeout after 300s",
            timeout_seconds=300.0,
            provider="test_provider",
            correlation_id="test-789",
        )

        assert error.timeout_seconds == 300.0
        assert error.retryable is True  # Timeouts are always retryable


# =============================================================================
# Regression Tests: #18a — Sync I/O in Async HuggingFace Methods
# =============================================================================


class TestHuggingFaceAsyncIO:
    """
    Regression tests for P1 finding #18a.

    All three Gradio predict calls (_run_trellis, _run_triposr, _run_shap_e)
    must be dispatched via asyncio.to_thread — not called synchronously in the
    async method body, which would block the event loop for the full generation
    duration (often 30-120 seconds).
    """

    @pytest.fixture
    def provider(self, mock_huggingface_config):
        from services.three_d.huggingface_provider import HuggingFaceProvider

        return HuggingFaceProvider(mock_huggingface_config)

    @staticmethod
    def _install_mock_gradio_client(monkeypatch, client: MagicMock) -> None:
        """Exercise the provider's lazy import without requiring the ml extra."""
        monkeypatch.setitem(
            sys.modules,
            "gradio_client",
            SimpleNamespace(
                Client=MagicMock(return_value=client), handle_file=MagicMock(return_value="handle")
            ),
        )

    @pytest.mark.asyncio
    async def test_run_trellis_dispatches_predict_via_to_thread(
        self, provider, tmp_path, monkeypatch
    ):
        """_run_trellis must use asyncio.to_thread for client.predict()."""
        import asyncio

        fake_glb = tmp_path / "model.glb"
        fake_glb.write_bytes(b"glb")

        mock_client = MagicMock()
        mock_client.predict.return_value = (
            {"video": "info"},
            str(fake_glb),
            str(fake_glb),
        )
        self._install_mock_gradio_client(monkeypatch, mock_client)

        with (patch("asyncio.to_thread", wraps=asyncio.to_thread) as mock_to_thread,):
            await provider._run_trellis(str(fake_glb), "corr-001")
            mock_to_thread.assert_called_once()

    @pytest.mark.asyncio
    async def test_run_triposr_dispatches_predict_via_to_thread(
        self, provider, tmp_path, monkeypatch
    ):
        """_run_triposr must use asyncio.to_thread for client.predict()."""
        import asyncio

        fake_mesh = tmp_path / "model.obj"
        fake_mesh.write_bytes(b"obj")

        mock_client = MagicMock()
        mock_client.predict.return_value = (str(fake_mesh),)
        self._install_mock_gradio_client(monkeypatch, mock_client)

        with (patch("asyncio.to_thread", wraps=asyncio.to_thread) as mock_to_thread,):
            await provider._run_triposr(str(fake_mesh), "corr-002")
            mock_to_thread.assert_called_once()

    @pytest.mark.asyncio
    async def test_run_shap_e_dispatches_predict_via_to_thread(
        self, provider, tmp_path, monkeypatch
    ):
        """_run_shap_e must use asyncio.to_thread for client.predict()."""
        import asyncio

        fake_mesh = tmp_path / "model.obj"
        fake_mesh.write_bytes(b"obj")

        mock_client = MagicMock()
        mock_client.predict.return_value = (str(fake_mesh),)
        self._install_mock_gradio_client(monkeypatch, mock_client)

        with (patch("asyncio.to_thread", wraps=asyncio.to_thread) as mock_to_thread,):
            await provider._run_shap_e("a 3D hooded sweatshirt", "corr-003")
            mock_to_thread.assert_called_once()
