"""DualVisionGate — Phase B2 dual-agent vision consensus.

Promoted to ADK SuperAgent for comprehensive "Back Data" (telemetry) and
high-fidelity dual-agent vision consensus.

Agent A: OpenAI gpt-4o (chat.completions vision)
Agent B: Gemini Flash (gemini_rest.py)
Mode:    Consensus — both must return YES to proceed.

Per the elite-team policy in llm/model_ids.py: vision is OpenAI + Gemini.
Claude is not used for vision (vision is a Claude weakness); the previous
Claude leg was migrated to gpt-4o in commit-{policy}.

VisionAgent is aliased to DualVisionGate for nodes.py backwards compatibility.
"""

from __future__ import annotations

import base64
import json
import logging
from pathlib import Path

from adk.base import ADKProvider, AgentConfig
from adk.super_agents import BaseSuperAgent

from ..gemini_rest import analyze_vision as gemini_analyze_vision
from ..models import PreflightResult, SynthesizedVision, VisionAnalysis

logger = logging.getLogger(__name__)

# Products images live under the canonical WP theme products dir.
# Resolved absolutely via :mod:`skyyrose.core.paths` so the lookup is cwd-stable.
from skyyrose.core.product import get_product, render_reference  # noqa: E402

from ..config import OPENAI_VISION_MODEL as _OPENAI_MODEL
from ..config import VISION_GEMINI_MODEL as _GEMINI_VISION_MODEL


def _reference_path(sku: str, view: str = "front") -> str:
    """Resolve the exact registry view; legacy callers default explicitly to front."""
    return render_reference(get_product(sku), view)["path"]


def _load_image_b64(path: str) -> str:
    with open(path, "rb") as f:
        return base64.standard_b64encode(f.read()).decode("utf-8")


_PREFLIGHT_PROMPT = (
    "You are verifying a product reference image for an e-commerce imagery pipeline. "
    "The product name from the catalog is: '{name}'. "
    "Looking at this image, does it show the correct garment type? "
    "Reply with exactly one word YES or NO on the first line, then one sentence of reasoning."
)

_VISION_SPEC_PROMPT = (
    "You are analyzing a product reference image for SkyyRose luxury fashion brand. "
    "Product: '{name}' (SKU: {sku}). Branding spec: {branding}. "
    "Describe the garment type, colorway, fabric texture, and any visible branding/logos. "
    "Be specific — this description drives AI image generation."
)


class DualVisionGate(BaseSuperAgent):
    """Dual-agent vision consensus gate promoted to ADK SuperAgent."""

    def __init__(self, config: AgentConfig | None = None) -> None:
        if config is None:
            config = AgentConfig(
                name="legendary_vision_gate",
                provider=ADKProvider.GOOGLE,
                model=_GEMINI_VISION_MODEL,
                system_prompt="You are the Legendary Vision Gate for SkyyRose. You ensure product integrity with 100% precision.",
            )
        super().__init__(config)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    async def verify_reference(
        self,
        image_path: str,
        sku: str,
        expected_garment: str,
        view: str = "front",
    ) -> PreflightResult:
        """Both models must return YES. Either NO blocks the SKU. Capture Back Data."""
        try:
            product = get_product(sku)
            evidence = render_reference(product, view)
            if Path(image_path).resolve() != Path(evidence["path"]):
                raise ValueError("Supplied reference does not match the SKU/view binding")
        except (KeyError, ValueError, OSError) as exc:
            return PreflightResult(False, sku, "BLOCKED", "BLOCKED", str(exc))
        # Trigger ADK for observability
        adk_prompt = f"PREFLIGHT TASK: SKU={sku}, Image={image_path}, Expected={expected_garment}"
        logger.info(f"Running Legendary Preflight for {sku} via ADK...")
        await self.execute(adk_prompt)

        prompt = _PREFLIGHT_PROMPT.format(name=expected_garment)

        try:
            a_text = await self._call_openai(image_path, prompt)
            b_text = await self._call_gemini(image_path, prompt)
        except Exception as exc:
            logger.error(f"Preflight vision calls failed: {exc}")
            return PreflightResult(
                passed=False,
                sku=sku,
                agent_a_verdict="ERROR",
                agent_b_verdict="ERROR",
                blocking_reason=str(exc),
            )

        a_yes = a_text.strip().upper().startswith("YES")
        b_yes = b_text.strip().upper().startswith("YES")

        if a_yes and b_yes:
            return PreflightResult(
                passed=True,
                sku=sku,
                reference_evidence=evidence,
                agent_a_verdict=a_text[:120],
                agent_b_verdict=b_text[:120],
            )

        blocking = []
        if not a_yes:
            blocking.append(f"Agent A (OpenAI): {a_text[:200]}")
        if not b_yes:
            blocking.append(f"Agent B (Gemini): {b_text[:200]}")

        return PreflightResult(
            passed=False,
            sku=sku,
            agent_a_verdict=a_text[:120],
            agent_b_verdict=b_text[:120],
            blocking_reason=" | ".join(blocking),
        )

    async def analyze(self, sku: str, view: str) -> SynthesizedVision:
        """Synthesize a generation spec from the reference image with Back Data."""
        try:
            product = get_product(sku)
            evidence = render_reference(product, view)
        except (KeyError, ValueError, OSError) as exc:
            return SynthesizedVision(success=False, error=f"Reference blocked: {exc}")
        ref = evidence["path"]
        name = product["name"]
        branding = product["dossier"]["branding_block"]
        # Observability must never dispatch before SKU/view validation.
        await self.execute(f"VISION ANALYSIS TASK: SKU={sku}, VIEW={view}")

        prompt = _VISION_SPEC_PROMPT.format(sku=sku, name=name, branding=branding)
        prompt += (
            "\nAUTHORITATIVE PRODUCT CONSTRAINTS (do not infer dimensions or fiber composition from pixels):\n"
            + json.dumps(
                {"dossier": product["dossier"], "corrections": product.get("corrections", [])},
                ensure_ascii=False,
            )
        )

        try:
            a_text = await self._call_openai(ref, prompt)
            a_result = VisionAnalysis(
                success=True,
                provider="openai",
                model=_OPENAI_MODEL,
                analysis=a_text,
                char_count=len(a_text),
            )
        except Exception as exc:
            a_result = VisionAnalysis(
                success=False, provider="openai", model=_OPENAI_MODEL, error=str(exc)
            )

        try:
            b_text = await self._call_gemini(ref, prompt)
            b_result = VisionAnalysis(
                success=True,
                provider="google",
                model=_GEMINI_VISION_MODEL,
                analysis=b_text,
                char_count=len(b_text),
            )
        except Exception as exc:
            b_result = VisionAnalysis(
                success=False, provider="google", model=_GEMINI_VISION_MODEL, error=str(exc)
            )

        if not a_result.success and not b_result.success:
            return SynthesizedVision(
                success=False,
                error="Both vision agents failed",
                individual_results=(a_result, b_result),
            )

        texts = [r.analysis for r in (a_result, b_result) if r.success and r.analysis]
        unified = "\n\n---\n\n".join(texts)

        return SynthesizedVision(
            success=True,
            unified_spec=unified,
            reference_evidence=evidence,
            providers_used=tuple(r.provider for r in (a_result, b_result) if r.success),
            individual_results=(a_result, b_result),
        )

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    async def _call_openai(self, image_path: str, prompt: str) -> str:
        from ..config import get_openai_client

        client = get_openai_client()

        ext = Path(image_path).suffix.lower().lstrip(".")
        media_type = "image/jpeg" if ext in ("jpg", "jpeg") else f"image/{ext}"
        b64 = _load_image_b64(image_path)
        msg = client.chat.completions.create(
            model=_OPENAI_MODEL,
            max_tokens=512,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:{media_type};base64,{b64}"},
                        },
                    ],
                }
            ],
        )
        return msg.choices[0].message.content

    async def _call_gemini(self, image_path: str, prompt: str) -> str:
        ext = Path(image_path).suffix.lower().lstrip(".")
        mime = "image/jpeg" if ext in ("jpg", "jpeg") else f"image/{ext}"
        b64 = _load_image_b64(image_path)
        result = gemini_analyze_vision(
            model=_GEMINI_VISION_MODEL,
            prompt=prompt,
            image_b64=b64,
            mime_type=mime,
        )
        if not result.get("success"):
            raise RuntimeError(result.get("error", "Gemini vision failed"))
        return result["text"]


# Backwards-compatible alias — nodes.py imports VisionAgent
VisionAgent = DualVisionGate
