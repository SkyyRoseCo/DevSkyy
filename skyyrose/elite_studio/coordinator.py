"""
Coordinator — Orchestrates the Multi-Agent Pipeline

Directs the team of agents through the production workflow:
  1. Vision Agent (Gemini + OpenAI) -> product analysis
  2. Generator Agent (Gemini 3 Pro) -> fashion model image
  3. Quality Agent (Claude Sonnet) -> verification

Handles batch processing, rate limiting, and result reporting.
"""

from __future__ import annotations

import asyncio
import inspect
import json
import re
import time
from typing import Any, Protocol

from .agents.compositor_agent import CompositorAgent
from .agents.generator_agent import GeneratorAgent
from .agents.quality_agent import QualityAgent
from .agents.vision_agent import DualVisionGate as VisionAgent
from .budget import BudgetExceededError, RunBudget
from .config import BATCH_DELAY_SECONDS, OUTPUT_DIR
from .models import ProductionResult
from .utils import discover_all_skus

# Worst-case per-stage cost estimates (USD). Pre-check ceilings use these so the
# budget gate fires BEFORE money is spent. Actual spend is recorded post-call
# from the engine response when available, otherwise these estimates.
_GENERATOR_EST_COST_USD = 0.12  # GPT $0.08 + Gemini $0.04 (dual-path)
_COMPOSITOR_EST_COST_USD = 0.115  # mirrors graph/nodes/_shared.py

# SKU format guard — the catalog enforces this shape (e.g. "br-001", "sig-014").
# Validating BEFORE any path construction defeats traversal attacks via
# malicious SKU values like "../../../etc/passwd" or absolute paths. Mirrors
# the regex used in skyyrose/elite_studio/upload.py — kept locally to avoid a
# circular-import dependency between coordinator and upload.
_SKU_RE = re.compile(r"^[a-z]{2,4}-\d{3}$")

# ---------------------------------------------------------------------------
# Logger protocol — decouples presentation from orchestration
# ---------------------------------------------------------------------------


class Logger(Protocol):
    """Minimal logging interface for coordinator output."""

    def info(self, msg: str) -> None: ...
    def step(self, step_num: int, total: int, label: str) -> None: ...
    def ok(self, msg: str) -> None: ...
    def fail(self, msg: str) -> None: ...
    def error(self, msg: str) -> None: ...
    def separator(self) -> None: ...


class PrintLogger:
    """Default logger that prints to stdout."""

    def info(self, msg: str) -> None:
        print(f"  {msg}")

    def step(self, step_num: int, total: int, label: str) -> None:
        print(f"\n  [{step_num}/{total}] {label}...")

    def ok(self, msg: str) -> None:
        print(f"  OK: {msg}")

    def fail(self, msg: str) -> None:
        print(f"  FAIL: {msg}")

    def error(self, msg: str) -> None:
        print(f"  ERROR: {msg}")

    def separator(self) -> None:
        print(f"{'=' * 60}")


class NullLogger:
    """Silent logger for tests."""

    def info(self, msg: str) -> None:
        pass

    def step(self, step_num: int, total: int, label: str) -> None:
        pass

    def ok(self, msg: str) -> None:
        pass

    def fail(self, msg: str) -> None:
        pass

    def error(self, msg: str) -> None:
        pass

    def separator(self) -> None:
        pass


# ---------------------------------------------------------------------------
# Coordinator
# ---------------------------------------------------------------------------


class Coordinator:
    """Orchestrates the multi-agent production pipeline.

    The coordinator delegates to specialized agents and manages
    the production flow. Each agent operates independently with
    its own provider connections and retry logic.

    Agent Team:
        vision  -> VisionAgent  (Gemini Flash + OpenAI GPT-4o)
        gen     -> GeneratorAgent  (Gemini 3 Pro)
        qc      -> QualityAgent  (Claude Sonnet)
        comp    -> CompositorAgent  (Opus + FLUX, optional)
    """

    def __init__(
        self,
        vision: VisionAgent | None = None,
        generator: GeneratorAgent | None = None,
        quality: QualityAgent | None = None,
        compositor: CompositorAgent | None = None,
        logger: Logger | None = None,
        budget: RunBudget | None = None,
    ):
        self.vision = vision or VisionAgent()
        self.generator = generator or GeneratorAgent()
        self.quality = quality or QualityAgent()
        self.compositor = compositor
        self.log = logger or PrintLogger()
        # Shared per-run cost ceiling. Each paid stage pre-checks via
        # ``ensure_within_budget`` and increments via ``spend`` after success.
        # When None, paid stages run uncapped — caller MUST pass a budget for
        # production batch runs to avoid runaway spend.
        self.budget = budget

    def produce(self, sku: str, view: str = "front") -> ProductionResult:
        """Run full production pipeline for a single product.

        Steps:
            1. Vision analysis (dual-provider)
            2. Image generation (Gemini 3 Pro)
            3. Quality verification (Claude Sonnet)

        Each step can fail independently. If vision fails, we stop.
        If generation fails, we stop. If QC fails, we still return
        the result (the image exists, just flagged).
        """
        self.log.separator()
        self.log.info(f"ELITE PRODUCTION STUDIO — {sku.upper()} | {view}")
        self.log.separator()

        # Step 1: Vision Analysis
        self.log.step(1, 3, "Vision Analysis")
        vision_result = self.vision.analyze(sku, view)

        if not vision_result.success:
            self.log.fail(vision_result.error)
            return ProductionResult(
                sku=sku,
                view=view,
                status="error",
                step="vision",
                error=vision_result.error,
                vision=vision_result,
            )

        providers = ", ".join(vision_result.providers_used)
        self.log.ok(f"{vision_result.provider_count} providers ({providers})")

        # Step 2: Image Generation — budget-gated before paid dispatch
        self.log.step(2, 3, "Image Generation")
        if self.budget is not None:
            try:
                self.budget.ensure_within_budget(_GENERATOR_EST_COST_USD, stage="generation")
            except BudgetExceededError as exc:
                self.log.fail(f"budget exceeded before generation: {exc}")
                return ProductionResult(
                    sku=sku,
                    view=view,
                    status="error",
                    step="generation",
                    error=f"budget exceeded: {exc}",
                    vision=vision_result,
                )

        gen_result = self.generator.generate(
            sku=sku,
            view=view,
            generation_spec=vision_result.unified_spec,
            budget=self.budget,
        )

        if not gen_result.success:
            self.log.fail(gen_result.error)
            return ProductionResult(
                sku=sku,
                view=view,
                status="error",
                step="generation",
                error=gen_result.error,
                vision=vision_result,
                generation=gen_result,
            )

        self.log.ok(gen_result.output_path)

        # Step 3: Quality Control
        self.log.step(3, 3, "Quality Control")
        qc_result = self.quality.verify(
            image_path=gen_result.output_path,
            expected_spec=vision_result.unified_spec,
            sku=sku,
            view=view,
        )

        if inspect.isawaitable(qc_result):
            qc_result = asyncio.run(qc_result)

        if qc_result.success:
            self.log.ok(f"{qc_result.overall_status} ({qc_result.recommendation})")
        else:
            self.log.info(f"QC blocked ({qc_result.error})")

        if not (
            qc_result.success
            and qc_result.overall_status == "pass"
            and qc_result.recommendation == "approve"
        ):
            return ProductionResult(
                sku=sku,
                view=view,
                status="error",
                step="quality",
                error=qc_result.error or "Quality gate did not approve candidate",
                output_path=gen_result.output_path,
                vision=vision_result,
                generation=gen_result,
                quality=qc_result,
            )

        # Step 4: Scene Compositing (optional) — budget-gated paid dispatch
        comp_result = None
        if self.compositor and gen_result.success:
            self.log.step(4, 4, "Scene Compositing")
            try:
                from .agents.compositor_agent import SCENE_LOOKBOOK
                from .utils import discover_scene_images

                # Pre-check budget once before scanning lookbook so a doomed
                # batch doesn't fire even the cheap discovery work.
                if self.budget is not None:
                    self.budget.ensure_within_budget(_COMPOSITOR_EST_COST_USD, stage="compositing")

                # Find scenes for this SKU
                for scene_name, sku_map in SCENE_LOOKBOOK.items():
                    if sku in sku_map:
                        scenes = discover_scene_images(
                            scene_name.rsplit("-", 2)[0]
                            if scene_name.count("-") > 2
                            else scene_name
                        )
                        if scenes:
                            comp_result = self.compositor.composite(
                                sku=sku,
                                scene_image_path=str(scenes[0]),
                                model_image_path=gen_result.output_path,
                                collection=scene_name.rsplit("-", 2)[0],
                                scene_name=scene_name,
                                budget=self.budget,
                            )
                            if comp_result.success:
                                self.log.ok(f"Composited: {comp_result.output_path}")
                            else:
                                self.log.error(f"Compositing failed: {comp_result.error}")
                        break
            except BudgetExceededError as exc:
                self.log.error(f"Compositing skipped — budget exceeded: {exc}")
            except Exception as exc:
                self.log.error(f"Compositing raised {type(exc).__name__}: {exc}")

        self.log.separator()
        self.log.info(f"COMPLETE: {sku.upper()}")
        self.log.separator()

        return ProductionResult(
            sku=sku,
            view=view,
            status="success",
            output_path=gen_result.output_path,
            vision=vision_result,
            generation=gen_result,
            quality=qc_result,
            compositing=comp_result,
        )

    def produce_batch(
        self,
        skus: list[str] | None = None,
        view: str = "front",
        skip_existing: bool = True,
        ceiling_usd: float | None = None,
    ) -> list[ProductionResult]:
        """Run production for multiple products.

        Args:
            skus: List of SKUs to process. None = all products.
            view: Image view angle.
            skip_existing: Skip products that already have generated images.
            ceiling_usd: Override cost ceiling for this batch. When set,
                a fresh ``RunBudget`` is created and replaces ``self.budget``
                for the duration of the batch. When None and ``self.budget``
                is also None, a ``RunBudget`` with the env-default ceiling
                (``ELITE_STUDIO_BUDGET_USD``) is created — production batch
                MUST run with a budget anchor to prevent runaway spend.

        Returns:
            List of ProductionResult for each product.
        """
        all_skus = skus or discover_all_skus()

        # Ensure a budget anchor exists for the whole batch. Once exceeded,
        # remaining SKUs short-circuit with a clean error per-iteration.
        if ceiling_usd is not None:
            self.budget = RunBudget(ceiling_usd=ceiling_usd)
        elif self.budget is None:
            self.budget = RunBudget()

        # Filter out already-generated products. SKU is validated before path
        # construction so a malformed catalog entry cannot escape OUTPUT_DIR.
        if skip_existing:
            remaining = []
            for sku in all_skus:
                if not _SKU_RE.fullmatch(sku):
                    self.log.error(f"[skip] invalid SKU {sku!r} (must match {_SKU_RE.pattern})")
                    continue
                output = OUTPUT_DIR / sku / f"{sku}-model-{view}-gemini.jpg"
                if output.exists():
                    self.log.info(f"[skip] {sku} — already generated")
                else:
                    remaining.append(sku)
            all_skus = remaining

        total = len(all_skus)
        self.log.info(f"BATCH PRODUCTION — {total} products")
        self.log.separator()

        results: list[ProductionResult] = []

        for i, sku in enumerate(all_skus, 1):
            self.log.step(i, total, sku)
            try:
                result = self.produce(sku, view)
                results.append(result)
            except Exception as exc:
                self.log.fail(str(exc))
                results.append(
                    ProductionResult(
                        sku=sku,
                        view=view,
                        status="error",
                        error=str(exc),
                    )
                )

            # Rate limit between products
            if i < total:
                self.log.info(f"[pause] {BATCH_DELAY_SECONDS}s rate limit...")
                time.sleep(BATCH_DELAY_SECONDS)

        # Write report
        self._write_report(results)
        self._print_summary(results)

        return results

    def _write_report(self, results: list[ProductionResult]) -> None:
        """Write batch report to JSON."""
        report_path = OUTPUT_DIR / "BATCH_REPORT.json"
        report_data = []
        for r in results:
            entry: dict[str, Any] = {
                "id": r.sku,
                "status": r.status,
                "step": r.step,
                "output_path": r.output_path,
            }
            if r.error:
                entry["error"] = r.error
            if r.vision:
                entry["vision_providers"] = list(r.vision.providers_used)
            if r.quality and r.quality.success:
                entry["qc_status"] = r.quality.overall_status
                entry["qc_recommendation"] = r.quality.recommendation
            report_data.append(entry)

        report_path.write_text(json.dumps(report_data, indent=2))
        self.log.info(f"Report: {report_path}")

    def _print_summary(self, results: list[ProductionResult]) -> None:
        """Print batch summary."""
        success = sum(1 for r in results if r.status == "success")
        failed = len(results) - success
        self.log.separator()
        self.log.info(f"BATCH COMPLETE: {success}/{len(results)} succeeded, {failed} failed")

        qc_pass = sum(1 for r in results if r.quality and r.quality.overall_status == "pass")
        qc_warn = sum(1 for r in results if r.quality and r.quality.overall_status == "warn")
        qc_fail = sum(1 for r in results if r.quality and r.quality.overall_status == "fail")
        if qc_pass or qc_warn or qc_fail:
            self.log.info(f"QC: {qc_pass} pass, {qc_warn} warn, {qc_fail} fail")

        self.log.separator()
