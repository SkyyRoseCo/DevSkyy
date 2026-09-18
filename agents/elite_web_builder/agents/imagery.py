"""Imagery Agent — Highest-level image generation for the SkyyRose brand.

Bridges the Elite Web Builder team to the existing 10-agent Elite Studio
image pipeline (`skyyrose/elite_studio/agents/`). The pipeline covers:

    1. vision_agent            — read reference assets + extract product DNA
    2. prompt_enrichment_agent — turn DNA + brand spec into a generation prompt
    3. generator_agent         — multi-engine generation (GPT-Image / Gemini Pro / FLUX)
    4. compositor_agent        — 6-stage composite (BRIA → Opus → IC-Light → FLUX Fill → GPS shadows → Gemini QA)
    5. quality_agent           — dual-LLM QA (Claude + Gemini) with 0..100 scoring
    6. variant_agent           — A/B variants for copy/marketing reuse
    7. color_correction_agent  — final color grade against brand tokens
    8. upscaling_agent         — 4x upscale for hero/lookbook deliverables
    9. safety_agent            — brand-safety + likeness + IP checks
   10. tryon_agent             — virtual try-on for lifestyle compositing

Model: Claude Opus 4.6 (the brain that prompts FLUX/Gemini as "hands")
Budget: every batch is protected by the ``--max-cost`` ceiling wired into
        ``scripts/nano-banana-run.py`` — halts the pipeline before crossing
        a declared USD cap to prevent runaway fallback spend.
"""

from __future__ import annotations

from agents.base import AgentCapability, AgentRole, AgentSpec

IMAGERY_SPEC = AgentSpec(
    role=AgentRole.IMAGERY,
    name="imagery",
    system_prompt=(
        "You are the SkyyRose Imagery Lead. You orchestrate the 10-agent "
        "Elite Studio image pipeline to produce commercial-grade fashion "
        "photography at the highest available quality tier.\n\n"
        "Core responsibilities:\n"
        "- Every render follows the canonical catalog "
        "(wordpress-theme/skyyrose-flagship/data/skyyrose-catalog.csv) — "
        "never invent products.\n"
        "- For every SKU you render, look up branding_spec and apply it "
        "character-perfect. Misspelled text is a FAIL.\n"
        "- Choose the right pipeline for the deliverable:\n"
        "    * product front/back/flat-lay  → nano-banana produce pipeline\n"
        "    * lifestyle / on-model scene   → compositor 6-stage\n"
        "    * lookbook / editorial spread  → master orchestrator\n"
        "    * social ad creative           → variant_agent + safety_agent\n"
        "- Every paid dispatch respects the STOP-AND-SHOW protocol in "
        "CLAUDE.md: show the manifest (SKU × variant × estimated cost) "
        "before spending a dollar.\n"
        "- Every paid dispatch carries a --max-cost ceiling.\n"
        "- QA gate: scores < 50 auto-reject and move to _rejected/. Never "
        "promote a reject to the live theme without owner confirmation.\n\n"
        "Output rules:\n"
        "- All produced webp files land in "
        "wordpress-theme/skyyrose-flagship/assets/images/products/ "
        "with the naming convention {sku}-{view}-render.webp.\n"
        "- After writing a render, bind it in the product registry via "
        "skyyrose.core.product_registry.update_catalog_fields(sku, "
        "{'front_model_image' | 'back_model_image': path}), then run "
        "python scripts/sync_product_registry.py so the projections "
        "(catalog CSV, per-collection sot.json, data/sot-images.json) "
        "follow. Renders are discovered via "
        "skyyrose.core.product.get_product(sku)['images'], not filename "
        "convention.\n"
        "- Set render_source_override through the same registry write API "
        "when a real photograph should supersede an AI render for a SKU.\n"
        "- Log every run to logs/ with timestamp + PID + cost summary."
    ),
    capabilities=[
        AgentCapability(
            name="product_front_back",
            description="Generate product front/back renders (on-model or flat-lay) via nano-banana produce",
            tags=("imagery", "product", "flat-lay", "on-model"),
        ),
        AgentCapability(
            name="lifestyle_compositing",
            description="6-stage compositor — place subject into immersive collection scene",
            tags=("imagery", "lifestyle", "compositor", "flux-fill"),
        ),
        AgentCapability(
            name="editorial_spread",
            description="Master orchestrator — concept → live product via FLUX luxury pipeline",
            tags=("imagery", "editorial", "orchestrator"),
        ),
        AgentCapability(
            name="upscale_4x",
            description="Upscale hero/lookbook renders 4x for print + landing-page hero use",
            tags=("imagery", "upscale", "flux-upscaler"),
        ),
        AgentCapability(
            name="color_grade",
            description="Final color correction against brand tokens (rose gold, gold, crimson, silver)",
            tags=("imagery", "color", "brand-tokens"),
        ),
        AgentCapability(
            name="qa_gate",
            description="Dual-LLM quality audit (Claude + Gemini) — 0..100 score + pass/fail",
            tags=("imagery", "qa", "claude", "gemini"),
        ),
        AgentCapability(
            name="safety_ip_check",
            description="Brand-safety, likeness, and IP audit before any render ships",
            tags=("imagery", "safety", "ip", "brand"),
        ),
    ],
    knowledge_files=[
        "knowledge/imagery.md",
        "knowledge/photo_generation.md",
        "knowledge/canonical_catalog.md",
    ],
)
