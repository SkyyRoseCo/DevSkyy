"""
TripoGenerateAgent — Elite Studio Tripo3D multiview image generator.

Wraps the official tripo3d SDK to produce 4-view product imagery
(front/left/back/right) for SkyyRose garment SKUs via the
generate_multiview_image template.

Cost: ~10 credits per SKU (~$0.040 on Professional plan).
Balance probe (get_balance) costs 0 credits.

STOP-AND-SHOW gate is enforced at the dispatch layer (scripts/tripo_dispatch.py).
This agent dispatches unconditionally when called — callers are responsible for
obtaining explicit user confirmation before invoking.

------------------------------------------------------------------------
Tripo template surface (verified via Context7 / platform.tripo3d.ai docs,
2026-05-11)
------------------------------------------------------------------------

Tripo exposes four image-gen templates with very different capabilities. We
only wire the first one below. The others are documented so the next
session can extend cleanly when branded SKUs need a prompt-capable path.

  | Template                  | Accepts                              | Wired here? |
  |---------------------------|--------------------------------------|-------------|
  | generate_multiview_image  | image only (NO prompt, NO ref)       | YES         |
  | text_to_image             | prompt + negative_prompt             | no          |
  | generate_image            | prompt + template + model_version +  | no          |
  |                           | multi-image refs via [N] syntax      |             |
  | edit_multiview_image      | original_task_id + per-view prompts  | no          |

Why this matters for the hallucination cluster (bug-096): the only template
we wire is the one with zero anchors. Branded SKUs cannot be rendered safely
through ``generate_multiview_image`` because the API itself accepts no
prompt, no logo overlay, no palette token — FLUX.1 Kontext inside the
template freelances on whatever isn't visible in the single source image.

If a future caller needs branded multiview output via Tripo, the path is:
  1. Call ``generate_multiview_image`` on a clean tech-flat to seed a task
  2. Call ``edit_multiview_image`` with the task_id + per-view prompts
     derived from the dossier branding_spec
That two-step pattern needs a separate method on this agent (not yet
implemented). The hardcoded ``_MULTIVIEW_TEMPLATE`` constant below is the
single template this agent currently supports.

"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from pathlib import Path

from adk.base import ADKProvider, AgentConfig
from adk.super_agents import BaseSuperAgent

logger = logging.getLogger(__name__)

_DEFAULT_OUTPUT_DIR = "renders/output/tripo"
_MULTIVIEW_TEMPLATE = "generate_multiview_image"
CREDITS_PER_SKU = 10  # ~$0.040/call on Professional plan


@dataclass
class TripoGenerateResult:
    """Result of a single-SKU Tripo multiview generation."""

    success: bool
    sku: str
    template: str = _MULTIVIEW_TEMPLATE
    output_dir: str = ""
    views: list[str] = field(default_factory=list)
    task_id: str = ""
    credits_used: int = 0
    error: str = ""


class TripoGenerateAgent(BaseSuperAgent):
    """Tripo3D multiview garment image generator, wired into the ADK SuperAgent hierarchy."""

    def __init__(
        self,
        output_dir: str = _DEFAULT_OUTPUT_DIR,
        config: AgentConfig | None = None,
    ) -> None:
        if config is None:
            config = AgentConfig(
                name="tripo_generate_architect",
                provider=ADKProvider.GOOGLE,
                model="gemini-2.0-flash",
                system_prompt=(
                    "You are the Tripo3D generation architect for SkyyRose. "
                    "Your mission is production-quality multiview garment imagery."
                ),
            )
        super().__init__(config)
        self._output_dir = Path(output_dir)

    async def get_balance(self) -> int:
        """Free pre-flight balance check — consumes 0 credits."""
        from tripo3d import TripoClient

        async with TripoClient() as client:
            return await client.get_balance()

    async def generate_multiview(
        self,
        sku: str,
        image_path: str | Path,
    ) -> TripoGenerateResult:
        """Generate 4-view product imagery (front/left/back/right) for a single SKU.

        Args:
            sku: Product SKU string (used for output subdirectory naming).
            image_path: Absolute path to the source garment flat/tech image.

        Returns:
            TripoGenerateResult with downloaded view paths on success, or error detail.
        """
        from tripo3d import TaskStatus, TripoClient

        image_path = Path(image_path)
        if not image_path.exists():
            return TripoGenerateResult(
                success=False,
                sku=sku,
                error=f"Source image not found: {image_path}",
            )

        sku_output_dir = self._output_dir / sku
        sku_output_dir.mkdir(parents=True, exist_ok=True)

        try:
            async with TripoClient() as client:
                logger.info("Tripo generate_multiview_image: SKU=%s source=%s", sku, image_path)
                task_id = await client.generate_multiview_image(
                    image=str(image_path),
                )
                logger.info("Tripo task created: task_id=%s", task_id)

                task = await client.wait_for_task(task_id, verbose=True)

                if task.status != TaskStatus.SUCCESS:
                    return TripoGenerateResult(
                        success=False,
                        sku=sku,
                        task_id=task_id,
                        error=f"Task ended with status={task.status}",
                    )

                downloaded = await client.download_task_models(task, str(sku_output_dir))
                view_paths = [p for p in downloaded.values() if p]
                for kind, path in downloaded.items():
                    if path:
                        logger.info("  %s → %s", kind, path)

                return TripoGenerateResult(
                    success=True,
                    sku=sku,
                    task_id=task_id,
                    output_dir=str(sku_output_dir),
                    views=view_paths,
                    credits_used=CREDITS_PER_SKU,
                )

        except Exception as exc:
            logger.exception("TripoGenerateAgent failed for SKU=%s: %s", sku, exc)
            return TripoGenerateResult(
                success=False,
                sku=sku,
                error=str(exc),
            )
