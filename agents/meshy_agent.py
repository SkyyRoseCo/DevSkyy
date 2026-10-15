"""
Meshy 3D Asset Generation Agent
================================

Generate 3D models using the Meshy API for the SkyyRose 3D pipeline.

Features:
- Text-to-3D generation (preview + refine modes)
- Image-to-3D generation
- Collection-aware prompt enhancement (BLACK_ROSE, LOVE_HURTS, SIGNATURE)
- Multiple output formats (GLB, FBX, OBJ, USDZ)
- Job queue management with polling
- Mesh quality validation

API Documentation: https://docs.meshy.ai/
Pricing: Credit-based, per-generation

Author: DevSkyy Platform Team
Version: 1.0.0
"""

from __future__ import annotations

import asyncio
import logging
import os
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum
from pathlib import Path
from typing import Any

import httpx
from pydantic import BaseModel, Field

from agents.core.base import (
    AgentCapability,
    AgentConfig,
    ExecutionResult,
    LLMCategory,
    PlanStep,
    RetrievalContext,
    SuperAgent,
    ValidationResult,
)
from agents.core.validation_scoring import compute_validation_scores
from core.runtime.tool_registry import (
    ToolCallContext,
    ToolCategory,
    ToolRegistry,
    ToolSeverity,
    ToolSpec,
    get_tool_registry,
)

logger = logging.getLogger(__name__)


# =============================================================================
# Configuration & Enums
# =============================================================================


class MeshyTaskStatus(StrEnum):
    """Meshy API task statuses."""

    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    SUCCEEDED = "SUCCEEDED"
    FAILED = "FAILED"
    EXPIRED = "EXPIRED"


class MeshyArtStyle(StrEnum):
    """Meshy generation art styles."""

    REALISTIC = "realistic"
    SCULPTURE = "sculpture"
    PBR = "pbr"


class MeshyTopology(StrEnum):
    """Mesh topology types."""

    QUAD = "quad"
    TRIANGLE = "triangle"


class MeshyMode(StrEnum):
    """Meshy generation modes."""

    PREVIEW = "preview"
    REFINE = "refine"


class OutputFormat(StrEnum):
    """3D model output formats."""

    GLB = "glb"
    FBX = "fbx"
    OBJ = "obj"
    USDZ = "usdz"


@dataclass
class MeshyConfig:
    """Meshy API configuration."""

    api_key: str = field(default_factory=lambda: os.getenv("MESHY_API_KEY", ""))
    base_url: str = "https://api.meshy.ai"
    timeout: float = 300.0  # 5 minutes max wait for generation
    poll_interval: float = 5.0  # Seconds between status checks
    max_poll_attempts: int = 120  # 10 minutes at 5s intervals
    output_dir: str = "./generated_assets/meshy"

    # Generation defaults
    default_art_style: str = MeshyArtStyle.REALISTIC.value
    default_topology: str = MeshyTopology.QUAD.value
    default_target_polycount: int = 30000

    @classmethod
    def from_env(cls) -> MeshyConfig:
        """Create config from environment variables."""
        return cls(
            api_key=os.getenv("MESHY_API_KEY", ""),
            output_dir=os.getenv("MESHY_OUTPUT_DIR", "./generated_assets/meshy"),
        )

    def validate(self) -> None:
        """Validate configuration."""
        if not self.api_key:
            raise ValueError(
                "MESHY_API_KEY environment variable is required. "
                "Get your API key from: https://app.meshy.ai/settings/api"
            )


# =============================================================================
# SkyyRose Brand Prompts
# =============================================================================

SKYYROSE_BRAND_DNA = (
    "SkyyRose luxury streetwear, gender-neutral, premium materials, "
    "elevated street poetry, intellectual luxury. "
    "Rose gold (#B76E79), obsidian black (#0D0D0D), ivory (#F5F5F0)."
)

COLLECTION_STYLES = {
    "BLACK_ROSE": {
        "prompt_prefix": "dark gothic elegance, limited edition luxury",
        "colors": "deep obsidian black with subtle rose gold accents, matte finish",
        "mood": "mysterious, cathedral-like, sophisticated, rare",
        "negative": "bright colors, cartoon, low quality, childish",
    },
    "LOVE_HURTS": {
        "prompt_prefix": "emotional expression, passionate storytelling through design",
        "colors": "deep crimson reds, black, heart motifs, blood rose accents",
        "mood": "passionate, vulnerable, powerful, romantic darkness",
        "negative": "happy, cartoon, pastel, low quality",
    },
    "SIGNATURE": {
        "prompt_prefix": "timeless luxury essentials, foundation wardrobe",
        "colors": "clean neutrals, warm ivory, rose gold hardware details",
        "mood": "classic, versatile, elevated basics, refined",
        "negative": "loud patterns, cartoon, low quality, cheap",
    },
}

GARMENT_TEMPLATES = {
    "hoodie": "luxury streetwear hoodie, premium heavyweight cotton, relaxed oversized fit, kangaroo pocket",
    "bomber": "premium bomber jacket, satin lining, ribbed cuffs and hem, quality metal hardware",
    "track_pants": "luxury track pants, side stripe detail, tapered fit, premium fabric",
    "tee": "premium heavyweight t-shirt, relaxed boxy fit, quality construction",
    "sweatshirt": "luxury crewneck sweatshirt, heavyweight fleece, ribbed details",
    "jacket": "structured jacket, premium materials, tailored streetwear fit",
    "shorts": "luxury shorts, premium cotton, embroidered details",
    "cap": "structured cap, quality embroidery, adjustable strap, premium build",
    "beanie": "luxury knit beanie, soft premium yarn, embroidered logo",
}


# =============================================================================
# Models
# =============================================================================


class MeshyTask(BaseModel):
    """Meshy generation task tracking."""

    task_id: str
    status: MeshyTaskStatus = MeshyTaskStatus.PENDING
    progress: int = 0
    mode: str = MeshyMode.PREVIEW.value
    model_urls: dict[str, str] = Field(default_factory=dict)
    thumbnail_url: str | None = None
    error: str | None = None
    created_at: str = ""
    finished_at: str | None = None


class MeshyGenerationResult(BaseModel):
    """Result of a Meshy 3D generation."""

    task_id: str
    status: str
    model_urls: dict[str, str] = Field(default_factory=dict)
    thumbnail_url: str | None = None
    local_path: str | None = None
    format: str = OutputFormat.GLB.value
    metadata: dict[str, Any] = Field(default_factory=dict)
    duration_seconds: float = 0.0


class MeshyAssetValidation(BaseModel):
    """3D asset validation result."""

    is_valid: bool = True
    file_size_mb: float = 0.0
    polycount: int | None = None
    warnings: list[str] = Field(default_factory=list)
    errors: list[str] = Field(default_factory=list)


# =============================================================================
# Meshy Agent
# =============================================================================


class MeshyAgent(SuperAgent):
    """
    Meshy 3D Asset Generation Agent.

    Generates 3D models for SkyyRose products using the Meshy API.
    Supports text-to-3D and image-to-3D with collection-aware prompting.

    Usage:
        agent = MeshyAgent()

        # Text-to-3D
        result = await agent.run({
            "action": "text_to_3d",
            "product_name": "Heart aRose Bomber",
            "collection": "BLACK_ROSE",
            "garment_type": "bomber",
            "additional_details": "Rose gold zipper, embroidered rose on back",
        })

        # Image-to-3D
        result = await agent.run({
            "action": "image_to_3d",
            "image_url": "https://example.com/design.jpg",
            "product_name": "Custom Hoodie",
        })

        # Check task status
        result = await agent.run({
            "action": "get_status",
            "task_id": "task_abc123",
            "task_type": "text_to_3d",
        })
    """

    def __init__(
        self,
        config: MeshyConfig | None = None,
        registry: ToolRegistry | None = None,
    ) -> None:
        agent_config = AgentConfig(
            name="meshy_asset",
            description="Meshy 3D Asset Generation Agent for text/image-to-3D",
            version="1.0.0",
            capabilities={
                AgentCapability.THREE_D_GENERATION,
                AgentCapability.IMAGE_GENERATION,
            },
            llm_category=LLMCategory.CATEGORY_B,
            tool_category=ToolCategory.MEDIA,
            default_timeout=300.0,
        )

        super().__init__(agent_config, registry or get_tool_registry())

        self.meshy_config = config or MeshyConfig.from_env()

        # Ensure output directory exists
        Path(self.meshy_config.output_dir).mkdir(parents=True, exist_ok=True)

        # Track active jobs
        self._active_jobs: dict[str, MeshyTask] = {}

    def _register_tools(self) -> None:
        """Register Meshy-specific tools."""
        self.registry.register(
            ToolSpec(
                name="meshy_text_to_3d",
                description="Generate 3D model from text description via Meshy API",
                category=ToolCategory.MEDIA,
                severity=ToolSeverity.MEDIUM,
                timeout_seconds=300.0,
                idempotent=False,
            ),
            self._tool_text_to_3d,
        )

        self.registry.register(
            ToolSpec(
                name="meshy_image_to_3d",
                description="Generate 3D model from image via Meshy API",
                category=ToolCategory.MEDIA,
                severity=ToolSeverity.MEDIUM,
                timeout_seconds=300.0,
                idempotent=False,
            ),
            self._tool_image_to_3d,
        )

        self.registry.register(
            ToolSpec(
                name="meshy_get_task_status",
                description="Get status of a Meshy generation task",
                category=ToolCategory.MEDIA,
                severity=ToolSeverity.READ_ONLY,
            ),
            self._tool_get_task_status,
        )

        self.registry.register(
            ToolSpec(
                name="meshy_validate_asset",
                description="Validate a generated 3D asset",
                category=ToolCategory.MEDIA,
                severity=ToolSeverity.READ_ONLY,
            ),
            self._tool_validate_asset,
        )

    # -------------------------------------------------------------------------
    # HTTP Client Helpers
    # -------------------------------------------------------------------------

    def _get_headers(self) -> dict[str, str]:
        """Build authorization headers for Meshy API."""
        return {
            "Authorization": f"Bearer {self.meshy_config.api_key}",
            "Content-Type": "application/json",
        }

    async def _api_request(
        self,
        method: str,
        endpoint: str,
        *,
        json_data: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Make an authenticated request to the Meshy API.

        Args:
            method: HTTP method (GET, POST).
            endpoint: API endpoint path (e.g., /v2/text-to-3d).
            json_data: Optional JSON body for POST requests.

        Returns:
            Parsed JSON response.

        Raises:
            ValueError: If API key is missing.
            PermissionError: If authentication fails.
            ConnectionError: If request fails.
        """
        if not self.meshy_config.api_key:
            raise ValueError(
                "MESHY_API_KEY environment variable is required. "
                "Get your API key from: https://app.meshy.ai/settings/api"
            )

        url = f"{self.meshy_config.base_url}{endpoint}"

        async with httpx.AsyncClient(timeout=self.meshy_config.timeout) as client:
            try:
                response = await client.request(
                    method,
                    url,
                    headers=self._get_headers(),
                    json=json_data,
                )
            except httpx.ConnectError as e:
                raise ConnectionError(
                    f"Cannot connect to Meshy API at {self.meshy_config.base_url}: {e}"
                ) from e
            except httpx.TimeoutException as e:
                raise TimeoutError(
                    f"Meshy API request timed out after {self.meshy_config.timeout}s"
                ) from e

        if response.status_code == 401:
            raise PermissionError(
                "Meshy API authentication failed. "
                "Check that your MESHY_API_KEY is valid and not expired."
            )
        if response.status_code == 429:
            raise ConnectionError("Meshy API rate limit exceeded. Wait and try again.")
        if response.status_code >= 400:
            error_detail = response.text[:200] if response.text else "Unknown error"
            raise ConnectionError(f"Meshy API error ({response.status_code}): {error_detail}")

        return response.json()

    # -------------------------------------------------------------------------
    # Core API Methods
    # -------------------------------------------------------------------------

    async def text_to_3d(
        self,
        prompt: str,
        *,
        negative_prompt: str = "",
        mode: str = MeshyMode.PREVIEW.value,
        art_style: str | None = None,
        topology: str | None = None,
        target_polycount: int | None = None,
    ) -> str:
        """
        Create a text-to-3D generation task.

        Args:
            prompt: Text description of the 3D model.
            negative_prompt: What to avoid in generation.
            mode: "preview" for fast draft, "refine" for high quality.
            art_style: Art style preset (realistic, sculpture, pbr).
            topology: Mesh topology (quad, triangle).
            target_polycount: Target polygon count.

        Returns:
            Task ID string.
        """
        payload: dict[str, Any] = {
            "mode": mode,
            "prompt": prompt,
            "negative_prompt": negative_prompt,
            "art_style": art_style or self.meshy_config.default_art_style,
            "topology": topology or self.meshy_config.default_topology,
            "target_polycount": target_polycount or self.meshy_config.default_target_polycount,
        }

        logger.info("Creating Meshy text-to-3D task: %s", prompt[:80])
        result = await self._api_request("POST", "/v2/text-to-3d", json_data=payload)

        task_id = result.get("result") or result.get("id", "")
        if not task_id:
            raise ValueError("Meshy API returned no task ID. Response may be malformed.")

        # Track the job
        self._active_jobs[task_id] = MeshyTask(
            task_id=task_id,
            status=MeshyTaskStatus.PENDING,
            mode=mode,
            created_at=datetime.now(UTC).isoformat(),
        )

        logger.info("Meshy text-to-3D task created: %s", task_id)
        return task_id

    async def image_to_3d(self, image_url: str) -> str:
        """
        Create an image-to-3D generation task.

        Args:
            image_url: URL of the source image.

        Returns:
            Task ID string.
        """
        payload = {"image_url": image_url}

        logger.info("Creating Meshy image-to-3D task from: %s", image_url[:80])
        result = await self._api_request("POST", "/v2/image-to-3d", json_data=payload)

        task_id = result.get("result") or result.get("id", "")
        if not task_id:
            raise ValueError("Meshy API returned no task ID. Response may be malformed.")

        self._active_jobs[task_id] = MeshyTask(
            task_id=task_id,
            status=MeshyTaskStatus.PENDING,
            created_at=datetime.now(UTC).isoformat(),
        )

        logger.info("Meshy image-to-3D task created: %s", task_id)
        return task_id

    async def generate_preview(
        self,
        image_url: str,
        product_name: str = "preview",
        minimum_fidelity: float = 60.0,
    ) -> dict[str, Any]:
        """Generate a fast preview GLB and run the trimesh fidelity gate.

        Replaces the deprecated HF Shap-E preview path. Used by the asset
        pipeline as a $0.20-cheap quality gate before committing to a full
        Tripo3D production run.

        Args:
            image_url: Public URL of the source image. Local paths must be
                hosted first (Meshy API requires a URL).
            product_name: Name used for the local download filename.
            minimum_fidelity: Threshold (0-100) below which `passed` is False.
                Default 60 — relaxed vs the 95 production threshold because
                this is a fast preview, not a final asset.

        Returns:
            dict with keys:
                passed (bool): Whether fidelity_score >= minimum_fidelity.
                fidelity_score (float): Overall fidelity 0-100.
                local_path (str | None): Local GLB path if downloaded.
                model_url (str | None): Meshy-hosted GLB URL.
                task_id (str): The Meshy task ID.
                grade (str): FidelityGrade enum value (excellent/good/...).
                duration_seconds (float): End-to-end wall time.
                error (str | None): Reason if passed is False due to error.
        """
        started_at = datetime.now(UTC)
        task_id = await self.image_to_3d(image_url)
        task = await self.poll_until_complete(task_id, task_type="image-to-3d")

        model_urls = task.model_urls or {}
        glb_url = model_urls.get("glb")

        local_path: str | None = None
        if glb_url:
            output_dir = str(Path(self.meshy_config.output_dir) / "previews")
            safe_name = product_name.lower().replace(" ", "_")[:40]
            filename = f"{safe_name}_{task_id[:8]}_preview.glb"
            try:
                local_path = await self._download_model(glb_url, output_dir, filename)
            except Exception as e:
                logger.warning("Meshy preview download failed: %s", e)

        if not local_path:
            return {
                "passed": False,
                "fidelity_score": 0.0,
                "local_path": None,
                "model_url": glb_url,
                "task_id": task_id,
                "grade": "FAILED",
                "duration_seconds": (datetime.now(UTC) - started_at).total_seconds(),
                "error": "Preview download failed — no local GLB to validate",
            }

        # Lazy import — keeps trimesh out of cold-start path
        from imagery.model_fidelity import validate_model_fidelity

        try:
            report = await validate_model_fidelity(
                local_path,
                enforce=False,
                minimum_threshold=minimum_fidelity,
            )
            return {
                "passed": report.passed,
                "fidelity_score": float(report.overall_score),
                "local_path": local_path,
                "model_url": glb_url,
                "task_id": task_id,
                "grade": report.grade.value,
                "duration_seconds": (datetime.now(UTC) - started_at).total_seconds(),
                "error": None,
            }
        except Exception as e:
            logger.warning("Meshy preview fidelity gate failed: %s", e)
            return {
                "passed": False,
                "fidelity_score": 0.0,
                "local_path": local_path,
                "model_url": glb_url,
                "task_id": task_id,
                "grade": "FAILED",
                "duration_seconds": (datetime.now(UTC) - started_at).total_seconds(),
                "error": f"Validation error: {e}",
            }

    async def get_task_status(
        self,
        task_id: str,
        task_type: str = "text-to-3d",
    ) -> MeshyTask:
        """
        Get the current status of a generation task.

        Args:
            task_id: The Meshy task ID.
            task_type: Either "text-to-3d" or "image-to-3d".

        Returns:
            Updated MeshyTask with current status.
        """
        endpoint = f"/v2/{task_type}/{task_id}"
        data = await self._api_request("GET", endpoint)

        status_str = data.get("status", "PENDING")
        try:
            status = MeshyTaskStatus(status_str)
        except ValueError:
            logger.warning("Unknown Meshy status: %s, treating as PENDING", status_str)
            status = MeshyTaskStatus.PENDING

        task = MeshyTask(
            task_id=task_id,
            status=status,
            progress=data.get("progress", 0),
            model_urls=data.get("model_urls", {}),
            thumbnail_url=data.get("thumbnail_url"),
            error=data.get("task_error"),
            finished_at=data.get("finished_at"),
        )

        # Update local tracking
        self._active_jobs[task_id] = task
        return task

    async def poll_until_complete(
        self,
        task_id: str,
        task_type: str = "text-to-3d",
    ) -> MeshyTask:
        """
        Poll a task until it completes or fails.

        Args:
            task_id: The Meshy task ID.
            task_type: Either "text-to-3d" or "image-to-3d".

        Returns:
            Final MeshyTask with results.

        Raises:
            TimeoutError: If max poll attempts exceeded.
            RuntimeError: If task fails.
        """
        for attempt in range(self.meshy_config.max_poll_attempts):
            task = await self.get_task_status(task_id, task_type)

            if task.status == MeshyTaskStatus.SUCCEEDED:
                logger.info(
                    "Meshy task %s completed (attempt %d/%d)",
                    task_id,
                    attempt + 1,
                    self.meshy_config.max_poll_attempts,
                )
                return task

            if task.status == MeshyTaskStatus.FAILED:
                error_msg = task.error or "Unknown generation error"
                raise RuntimeError(
                    f"Meshy task {task_id} failed: {error_msg}. "
                    "Try simplifying the prompt or using a different art style."
                )

            if task.status == MeshyTaskStatus.EXPIRED:
                raise RuntimeError(f"Meshy task {task_id} expired. Recreate the task.")

            logger.debug(
                "Meshy task %s: %s (%d%%) - poll %d/%d",
                task_id,
                task.status.value,
                task.progress,
                attempt + 1,
                self.meshy_config.max_poll_attempts,
            )
            await asyncio.sleep(self.meshy_config.poll_interval)

        raise TimeoutError(
            f"Meshy task {task_id} did not complete within "
            f"{self.meshy_config.max_poll_attempts * self.meshy_config.poll_interval:.0f}s. "
            "The generation may still be running -- check status manually."
        )

    # -------------------------------------------------------------------------
    # Prompt Building
    # -------------------------------------------------------------------------

    def _build_prompt(
        self,
        product_name: str,
        collection: str,
        garment_type: str,
        additional_details: str = "",
    ) -> tuple[str, str]:
        """
        Build a collection-aware prompt with brand DNA for Meshy generation.

        Returns:
            Tuple of (prompt, negative_prompt).
        """
        collection_key = collection.upper()
        style = COLLECTION_STYLES.get(collection_key, COLLECTION_STYLES["SIGNATURE"])

        garment_base = GARMENT_TEMPLATES.get(
            garment_type.lower(),
            "luxury streetwear garment, premium quality",
        )

        prompt_parts = [
            f"3D model of {product_name}",
            garment_base,
            style["prompt_prefix"],
            f"Colors: {style['colors']}",
            f"Mood: {style['mood']}",
            SKYYROSE_BRAND_DNA,
            "High quality mesh, clean topology, PBR materials",
            "Fashion product visualization, e-commerce ready",
        ]

        if additional_details:
            prompt_parts.append(additional_details)

        prompt = ". ".join(prompt_parts)
        negative_prompt = style.get("negative", "low quality, blurry, deformed")

        return prompt, negative_prompt

    # -------------------------------------------------------------------------
    # Download Helper
    # -------------------------------------------------------------------------

    async def _download_model(
        self,
        url: str,
        output_dir: str,
        filename: str,
    ) -> str:
        """
        Download a model file from a URL.

        Args:
            url: Download URL for the model.
            output_dir: Local directory to save to.
            filename: Output filename.

        Returns:
            Local file path.
        """
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        file_path = output_path / filename

        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.get(url)
            response.raise_for_status()
            file_path.write_bytes(response.content)

        logger.info(
            "Downloaded model to: %s (%.1f MB)", file_path, file_path.stat().st_size / (1024 * 1024)
        )
        return str(file_path)

    # -------------------------------------------------------------------------
    # SuperAgent Implementation
    # -------------------------------------------------------------------------

    async def _plan(
        self,
        request: dict[str, Any],
        context: ToolCallContext,
    ) -> list[PlanStep]:
        """Create execution plan based on request action."""
        action = request.get("action", "text_to_3d")
        steps: list[PlanStep] = []

        if action == "text_to_3d":
            steps.append(
                PlanStep(
                    step_id="gen_text",
                    tool_name="meshy_text_to_3d",
                    description="Generate 3D model from text description",
                    inputs={
                        "product_name": request.get("product_name", "Product"),
                        "collection": request.get("collection", "SIGNATURE"),
                        "garment_type": request.get("garment_type", "tee"),
                        "additional_details": request.get("additional_details", ""),
                        "output_format": request.get("output_format", OutputFormat.GLB.value),
                        "mode": request.get("mode", MeshyMode.PREVIEW.value),
                    },
                    priority=0,
                ),
            )
        elif action == "image_to_3d":
            steps.append(
                PlanStep(
                    step_id="gen_image",
                    tool_name="meshy_image_to_3d",
                    description="Generate 3D model from image",
                    inputs={
                        "image_url": request.get("image_url", ""),
                        "product_name": request.get("product_name", "Product"),
                        "output_format": request.get("output_format", OutputFormat.GLB.value),
                    },
                    priority=0,
                ),
            )
        elif action == "get_status":
            steps.append(
                PlanStep(
                    step_id="check_status",
                    tool_name="meshy_get_task_status",
                    description="Check Meshy task status",
                    inputs={
                        "task_id": request.get("task_id", ""),
                        "task_type": request.get("task_type", "text-to-3d"),
                    },
                    priority=0,
                ),
            )
            return steps  # No validation step for status checks
        else:
            raise ValueError(
                f"Unknown action: {action}. Use text_to_3d, image_to_3d, or get_status."
            )

        # Add validation step for generation actions
        steps.append(
            PlanStep(
                step_id="validate",
                tool_name="meshy_validate_asset",
                description="Validate generated 3D asset",
                inputs={"local_path": "{local_path}"},
                depends_on=[steps[0].step_id],
                priority=1,
            ),
        )

        return steps

    async def _retrieve(
        self,
        request: dict[str, Any],
        plan: list[PlanStep],
        context: ToolCallContext,
    ) -> RetrievalContext:
        """Retrieve brand context for generation."""
        collection = request.get("collection", "SIGNATURE").upper()
        collection_style = COLLECTION_STYLES.get(collection, COLLECTION_STYLES["SIGNATURE"])

        return RetrievalContext(
            query=f"SkyyRose {collection} collection 3D generation context",
            documents=[
                {"content": SKYYROSE_BRAND_DNA, "type": "brand_dna"},
                {"content": str(collection_style), "type": "collection_style"},
            ],
            sources=["brand_guidelines", "collection_prompts"],
        )

    async def _execute_step(
        self,
        step: PlanStep,
        retrieval_context: RetrievalContext,
        context: ToolCallContext,
    ) -> ExecutionResult:
        """Execute a single step."""
        started_at = datetime.now(UTC)

        try:
            result = await self.registry.execute(
                step.tool_name,
                step.inputs,
                context,
            )

            return ExecutionResult(
                tool_name=step.tool_name,
                step_id=step.step_id,
                success=result.success,
                result=result.result,
                error=result.error,
                duration_seconds=result.duration_seconds,
                started_at=started_at,
                completed_at=datetime.now(UTC),
                retries=result.retries,
            )
        except Exception as e:
            return ExecutionResult(
                tool_name=step.tool_name,
                step_id=step.step_id,
                success=False,
                error=str(e),
                error_type=type(e).__name__,
                started_at=started_at,
                completed_at=datetime.now(UTC),
            )

    async def _validate(
        self,
        results: list[ExecutionResult],
        context: ToolCallContext,
    ) -> ValidationResult:
        """Validate execution results."""
        validation = ValidationResult(is_valid=True)

        asset_validation: dict[str, Any] | None = None
        for result in results:
            if not result.success:
                validation.add_error(f"{result.tool_name} failed: {result.error}")
            if result.tool_name == "meshy_validate_asset" and result.result:
                asset_validation = result.result
                if not asset_validation.get("is_valid", True):
                    for error in asset_validation.get("errors", []):
                        validation.add_error(error)
                for warning in asset_validation.get("warnings", []):
                    validation.add_warning(warning)

        if not validation.errors:
            quality, confidence = compute_validation_scores(
                asset_validation,
                warning_count=len(validation.warnings),
            )
            validation.quality_score = quality
            validation.confidence_score = confidence

        return validation

    async def _emit(
        self,
        results: list[ExecutionResult],
        validation: ValidationResult,
        context: ToolCallContext,
    ) -> dict[str, Any]:
        """Emit final structured output."""
        output: dict[str, Any] = {
            "status": "success" if validation.is_valid else "error",
            "agent": self.name,
            "request_id": context.request_id,
            "validation": validation.to_dict(),
        }

        # Find generation result
        for result in results:
            if result.tool_name.startswith("meshy_") and result.success:
                if result.tool_name != "meshy_validate_asset":
                    output["data"] = result.result
                    break

        output["results"] = [r.to_dict() for r in results]

        return output

    # -------------------------------------------------------------------------
    # Tool Implementations
    # -------------------------------------------------------------------------

    async def _tool_text_to_3d(
        self,
        product_name: str,
        collection: str = "SIGNATURE",
        garment_type: str = "tee",
        additional_details: str = "",
        output_format: str = "glb",
        mode: str = "preview",
    ) -> dict[str, Any]:
        """
        Generate a 3D model from a text description via Meshy API.

        Builds a SkyyRose brand-aware prompt, submits to Meshy, polls until
        complete, and downloads the resulting model.

        Args:
            product_name: Name of the product.
            collection: SkyyRose collection (BLACK_ROSE, LOVE_HURTS, SIGNATURE).
            garment_type: Type of garment (hoodie, tee, bomber, etc.).
            additional_details: Extra prompt details.
            output_format: Output format (glb, fbx, obj, usdz).
            mode: Generation mode (preview for fast, refine for quality).

        Returns:
            MeshyGenerationResult dict with model URLs and metadata.

        Raises:
            ValueError: If API key is missing or API returns unexpected data.
            PermissionError: If API authentication fails.
            ConnectionError: If API request fails.
            TimeoutError: If generation times out.
            RuntimeError: If generation fails.
        """
        started_at = datetime.now(UTC)

        # Build collection-aware prompt
        prompt, negative_prompt = self._build_prompt(
            product_name,
            collection,
            garment_type,
            additional_details,
        )

        logger.info(
            "Meshy text-to-3D: product=%s, collection=%s, mode=%s",
            product_name,
            collection,
            mode,
        )

        # Submit generation task
        task_id = await self.text_to_3d(
            prompt=prompt,
            negative_prompt=negative_prompt,
            mode=mode,
            art_style=self.meshy_config.default_art_style,
            topology=self.meshy_config.default_topology,
            target_polycount=self.meshy_config.default_target_polycount,
        )

        # Poll until complete
        task = await self.poll_until_complete(task_id, task_type="text-to-3d")

        # Download the model in the requested format
        local_path = None
        model_urls = task.model_urls or {}
        download_url = model_urls.get(output_format) or model_urls.get("glb")

        if download_url:
            output_dir = str(Path(self.meshy_config.output_dir) / collection.lower())
            safe_name = product_name.lower().replace(" ", "_")[:40]
            filename = f"{safe_name}_{task_id[:8]}.{output_format}"

            try:
                local_path = await self._download_model(
                    download_url,
                    output_dir,
                    filename,
                )
            except Exception as e:
                logger.warning("Failed to download model: %s", e)

        duration = (datetime.now(UTC) - started_at).total_seconds()

        result = MeshyGenerationResult(
            task_id=task_id,
            status=task.status.value,
            model_urls=model_urls,
            thumbnail_url=task.thumbnail_url,
            local_path=local_path,
            format=output_format,
            metadata={
                "product_name": product_name,
                "collection": collection,
                "garment_type": garment_type,
                "prompt": prompt,
                "negative_prompt": negative_prompt,
                "mode": mode,
            },
            duration_seconds=duration,
        )

        return result.model_dump()

    async def _tool_image_to_3d(
        self,
        image_url: str,
        product_name: str = "Product",
        output_format: str = "glb",
    ) -> dict[str, Any]:
        """
        Generate a 3D model from an image via Meshy API.

        Args:
            image_url: URL of the source image.
            product_name: Name for the generated product.
            output_format: Output format (glb, fbx, obj, usdz).

        Returns:
            MeshyGenerationResult dict with model URLs and metadata.

        Raises:
            ValueError: If image_url is empty or API returns unexpected data.
            PermissionError: If API authentication fails.
            ConnectionError: If API request fails.
            TimeoutError: If generation times out.
            RuntimeError: If generation fails.
        """
        if not image_url:
            raise ValueError("image_url is required for image-to-3D generation.")

        started_at = datetime.now(UTC)

        logger.info("Meshy image-to-3D: product=%s, image=%s", product_name, image_url[:80])

        # Submit generation task
        task_id = await self.image_to_3d(image_url)

        # Poll until complete
        task = await self.poll_until_complete(task_id, task_type="image-to-3d")

        # Download the model in the requested format
        local_path = None
        model_urls = task.model_urls or {}
        download_url = model_urls.get(output_format) or model_urls.get("glb")

        if download_url:
            output_dir = str(Path(self.meshy_config.output_dir) / "images")
            safe_name = product_name.lower().replace(" ", "_")[:40]
            filename = f"{safe_name}_{task_id[:8]}.{output_format}"

            try:
                local_path = await self._download_model(
                    download_url,
                    output_dir,
                    filename,
                )
            except Exception as e:
                logger.warning("Failed to download model: %s", e)

        duration = (datetime.now(UTC) - started_at).total_seconds()

        result = MeshyGenerationResult(
            task_id=task_id,
            status=task.status.value,
            model_urls=model_urls,
            thumbnail_url=task.thumbnail_url,
            local_path=local_path,
            format=output_format,
            metadata={
                "product_name": product_name,
                "source_image": image_url,
            },
            duration_seconds=duration,
        )

        return result.model_dump()

    async def _tool_get_task_status(
        self,
        task_id: str,
        task_type: str = "text-to-3d",
    ) -> dict[str, Any]:
        """
        Get the current status of a Meshy generation task.

        Args:
            task_id: The Meshy task ID.
            task_type: Either "text-to-3d" or "image-to-3d".

        Returns:
            MeshyTask dict with current status and results.
        """
        if not task_id:
            raise ValueError("task_id is required.")

        task = await self.get_task_status(task_id, task_type)
        return task.model_dump()

    async def _tool_validate_asset(
        self,
        local_path: str,
        max_polycount: int = 100000,
        max_file_size_mb: float = 50.0,
        min_file_size_kb: float = 10.0,
    ) -> dict[str, Any]:
        """
        Validate a generated 3D asset for production quality.

        Checks file existence, size, format, and optionally mesh geometry
        if trimesh is available.

        Args:
            local_path: Path to the 3D model file.
            max_polycount: Maximum polygon count for web delivery.
            max_file_size_mb: Maximum file size in MB.
            min_file_size_kb: Minimum file size in KB (detect incomplete files).

        Returns:
            MeshyAssetValidation dict.
        """
        validation = MeshyAssetValidation(
            is_valid=True,
            warnings=[],
            errors=[],
        )

        # If local_path is a template placeholder or empty, skip validation
        if not local_path or local_path.startswith("{"):
            validation.warnings.append("No local file to validate (model available via URL only)")
            return validation.model_dump()

        path = Path(local_path)

        # Check file existence
        if not path.exists():
            validation.is_valid = False
            validation.errors.append(f"Model file not found: {local_path}")
            return validation.model_dump()

        # File size checks
        file_size = path.stat().st_size
        size_mb = file_size / (1024 * 1024)
        size_kb = file_size / 1024
        validation.file_size_mb = round(size_mb, 2)

        if size_mb > max_file_size_mb:
            validation.is_valid = False
            validation.errors.append(f"File too large: {size_mb:.1f}MB (max: {max_file_size_mb}MB)")
        elif size_mb > max_file_size_mb * 0.7:
            validation.warnings.append(
                f"Large file: {size_mb:.1f}MB. Consider optimization for web."
            )

        if size_kb < min_file_size_kb:
            validation.is_valid = False
            validation.errors.append(f"File too small: {size_kb:.1f}KB. Model may be incomplete.")

        # Format check
        supported = {".glb", ".gltf", ".obj", ".fbx", ".usdz", ".stl"}
        if path.suffix.lower() not in supported:
            validation.warnings.append(
                f"Unexpected format: {path.suffix}. Recommended: .glb for web."
            )

        # GLB header validation
        if path.suffix.lower() == ".glb" and path.exists():
            try:
                with open(path, "rb") as f:
                    magic = f.read(4)
                    if magic != b"glTF":
                        validation.is_valid = False
                        validation.errors.append("Invalid GLB file: missing glTF magic number")
            except Exception as e:
                validation.errors.append(f"Failed to read GLB header: {e}")

        # Mesh analysis with trimesh (optional)
        try:
            import trimesh

            mesh = trimesh.load(str(path), force="mesh")

            if hasattr(mesh, "faces") and mesh.faces is not None:
                polycount = len(mesh.faces)
                validation.polycount = polycount

                if polycount > max_polycount:
                    validation.warnings.append(
                        f"High polycount: {polycount:,} (recommended: <{max_polycount:,})"
                    )

            if hasattr(mesh, "is_watertight") and not mesh.is_watertight:
                validation.warnings.append("Mesh is not watertight (has holes)")

        except ImportError:
            logger.debug("trimesh not installed -- skipping mesh analysis")
        except Exception as e:
            validation.warnings.append(f"Mesh analysis failed: {e}")

        # Log outcome
        if validation.is_valid and not validation.warnings:
            logger.info("Asset validation passed: %s", local_path)
        elif validation.is_valid:
            logger.warning(
                "Asset validated with warnings: %s -- %s", local_path, validation.warnings
            )
        else:
            logger.error("Asset validation failed: %s -- %s", local_path, validation.errors)

        return validation.model_dump()

    async def close(self) -> None:
        """Close agent resources. httpx clients are created per-request, so this is a no-op."""
        logger.debug("MeshyAgent close called (no persistent connections)")


# =============================================================================
# Module-Level Singleton
# =============================================================================

#: Default agent instance. Lazy-initialized on first import.
#: Usage: ``from agents.meshy_agent import meshy_agent``
meshy_agent: MeshyAgent | None = None


def get_meshy_agent(config: MeshyConfig | None = None) -> MeshyAgent:
    """
    Get or create the module-level MeshyAgent singleton.

    Args:
        config: Optional config override. If None, reads from env vars.

    Returns:
        MeshyAgent instance.
    """
    global meshy_agent
    if meshy_agent is None:
        meshy_agent = MeshyAgent(config=config)
    return meshy_agent


# =============================================================================
# Exports
# =============================================================================

__all__ = [
    "MeshyAgent",
    "MeshyConfig",
    "MeshyTask",
    "MeshyGenerationResult",
    "MeshyAssetValidation",
    "MeshyTaskStatus",
    "MeshyArtStyle",
    "MeshyTopology",
    "MeshyMode",
    "OutputFormat",
    "SKYYROSE_BRAND_DNA",
    "COLLECTION_STYLES",
    "GARMENT_TEMPLATES",
    "meshy_agent",
    "get_meshy_agent",
]
