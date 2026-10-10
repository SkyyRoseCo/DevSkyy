#!/usr/bin/env python3
"""
SkyyRose 3D Model Studio - Gradio Interface

Generate and improve 3D models from images with 95% fidelity enforcement.

Usage:
    python gradio_3d_app.py

Then open http://localhost:7860 in your browser.
"""

from __future__ import annotations

import asyncio
import logging
import os

import gradio as gr

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import 3D modules
try:
    from ai_3d.generation_pipeline import (
        GenerationConfig,
        GenerationQuality,
        ModelFormat,
        ThreeDGenerationPipeline,
        ThreeDProvider,
    )
    from ai_3d.quality_enhancer import EnhancementConfig, ModelQualityEnhancer
    from imagery.model_fidelity import MINIMUM_FIDELITY_SCORE, ModelFidelityValidator

    PIPELINE_AVAILABLE = True
except ImportError as e:
    logger.warning(f"3D pipeline not fully available: {e}")
    PIPELINE_AVAILABLE = False
    MINIMUM_FIDELITY_SCORE = 95.0

# SkyyRose Brand Colors
SKYYROSE_PINK = "#B76E79"
SKYYROSE_BLACK = "#1A1A1A"

# Custom CSS
CSS = """
.gradio-container {
    max-width: 1400px !important;
}
.skyyrose-header {
    background: linear-gradient(135deg, #B76E79 0%, #1A1A1A 100%);
    padding: 20px;
    border-radius: 12px;
    margin-bottom: 20px;
    text-align: center;
}
.skyyrose-header h1 {
    color: white !important;
    font-size: 2.5em !important;
    margin: 0 !important;
}
.skyyrose-header p {
    color: rgba(255,255,255,0.8) !important;
    font-size: 1.1em !important;
}
.fidelity-pass {
    background-color: #10B981 !important;
    color: white !important;
    padding: 10px 20px;
    border-radius: 8px;
    font-weight: bold;
}
.fidelity-fail {
    background-color: #EF4444 !important;
    color: white !important;
    padding: 10px 20px;
    border-radius: 8px;
    font-weight: bold;
}
.status-box {
    padding: 15px;
    border-radius: 8px;
    margin: 10px 0;
}
"""


def get_provider_status() -> str:
    """Get status of available 3D providers."""
    providers = []

    if os.getenv("TRIPO_API_KEY"):
        providers.append("✅ Tripo3D")
    else:
        providers.append("❌ Tripo3D (set TRIPO_API_KEY)")

    if os.getenv("HUGGINGFACE_API_KEY") or os.getenv("HF_TOKEN"):
        providers.append("✅ HuggingFace")
    else:
        providers.append("❌ HuggingFace (set HF_TOKEN)")

    if os.getenv("MESHY_API_KEY"):
        providers.append("✅ Meshy")
    else:
        providers.append("❌ Meshy (set MESHY_API_KEY)")

    return "\n".join(providers)


async def generate_3d_from_image(
    image_path: str,
    prompt: str,
    provider: str,
    quality: str,
    output_format: str,
    enforce_fidelity: bool,
    progress=gr.Progress(),
) -> tuple[str | None, str, str]:
    """
    Generate a 3D model from an uploaded image.

    Returns:
        Tuple of (model_path, status_message, fidelity_report)
    """
    if not PIPELINE_AVAILABLE:
        return None, "❌ 3D pipeline not available. Check imports.", ""

    if not image_path:
        return None, "❌ Please upload an image first.", ""

    try:
        progress(0.1, desc="Initializing pipeline...")
        pipeline = ThreeDGenerationPipeline()

        # Check if any providers available
        available = pipeline.get_available_providers()
        if not available:
            return None, "❌ No 3D providers available. Set API keys.", ""

        # Build config
        config = GenerationConfig(
            provider=(
                ThreeDProvider(provider.lower()) if provider != "auto" else ThreeDProvider.AUTO
            ),
            quality=GenerationQuality(quality.lower()),
            output_format=ModelFormat(output_format.lower()),
            enforce_fidelity=enforce_fidelity,
            minimum_fidelity=MINIMUM_FIDELITY_SCORE,
        )

        progress(0.2, desc="Preprocessing image...")
        progress(0.4, desc="Generating 3D model...")

        # Run generation
        result = await pipeline.generate_from_image(
            image_path=image_path,
            config=config,
            prompt=prompt if prompt else None,
        )

        progress(0.9, desc="Validating fidelity...")

        if result.success:
            fidelity_status = "✅ PASSED" if result.fidelity_passed else "❌ FAILED"
            status = f"""
## ✅ Generation Complete!

**Provider Used:** {result.provider_used.value if result.provider_used else "N/A"}
**Generation Time:** {result.generation_time_seconds:.2f}s
**Fidelity Score:** {result.fidelity_score:.1f}% ({fidelity_status})
**Model Path:** {result.model_path}
"""

            # Build fidelity report
            report = ""
            if result.fidelity_report:
                fr = result.fidelity_report
                report = f"""
### Fidelity Report

| Metric | Score | Status |
|--------|-------|--------|
| Geometry | {fr.geometry.overall_score:.1f}% | {"✅" if fr.geometry.overall_score >= 95 else "⚠️"} |
| Textures | {fr.textures.overall_score:.1f}% | {"✅" if fr.textures.overall_score >= 95 else "⚠️"} |
| Materials | {fr.materials.overall_score:.1f}% | {"✅" if fr.materials.overall_score >= 95 else "⚠️"} |
| **Overall** | **{fr.overall_score:.1f}%** | **{fidelity_status}** |

**Threshold:** {MINIMUM_FIDELITY_SCORE}%
"""
                if fr.issues:
                    report += "\n**Issues Found:**\n"
                    for issue in fr.issues:
                        report += f"- {issue}\n"

            progress(1.0, desc="Done!")
            return result.model_path, status, report
        else:
            error_msg = "\n".join(result.errors) if result.errors else "Unknown error"
            return None, f"## ❌ Generation Failed\n\n{error_msg}", ""

    except Exception as e:
        logger.exception("Generation failed")
        return None, f"## ❌ Error\n\n{str(e)}", ""


async def enhance_3d_model(
    model_file,
    target_fidelity: float,
    optimize_mesh: bool,
    upscale_textures: bool,
    repair_mesh: bool,
    progress=gr.Progress(),
) -> tuple[str | None, str]:
    """
    Enhance an existing 3D model.

    Returns:
        Tuple of (enhanced_model_path, status_message)
    """
    if not PIPELINE_AVAILABLE:
        return None, "❌ Enhancement module not available."

    if model_file is None:
        return None, "❌ Please upload a 3D model file (.glb, .gltf, .obj)"

    try:
        progress(0.1, desc="Loading model...")

        enhancer = ModelQualityEnhancer()

        config = EnhancementConfig(
            target_fidelity=target_fidelity,
            mesh_optimization=optimize_mesh,
            texture_upscale=upscale_textures,
            repair_mesh=repair_mesh,
        )

        progress(0.3, desc="Analyzing model...")

        # First analyze
        analysis = await enhancer.analyze_model(model_file.name)

        progress(0.5, desc="Enhancing model...")

        # Enhance
        enhanced_path = await enhancer.enhance(model_file.name, config)

        if enhanced_path:
            progress(0.9, desc="Validating...")

            # Validate enhanced model
            validator = ModelFidelityValidator()
            report = await validator.validate(enhanced_path)

            status = f"""
## ✅ Enhancement Complete!

**Original Issues:**
{chr(10).join(f"- {issue}" for issue in analysis.get("issues", [])) or "- None detected"}

**Enhanced Model:** {enhanced_path}
**Final Fidelity:** {report.overall_score:.1f}%
**Status:** {"✅ PASSED" if report.passed else "❌ Below threshold"}
"""
            progress(1.0, desc="Done!")
            return str(enhanced_path), status
        else:
            return None, "## ❌ Enhancement Failed\n\nCould not enhance the model."

    except Exception as e:
        logger.exception("Enhancement failed")
        return None, f"## ❌ Error\n\n{str(e)}"


async def validate_3d_model(model_file, progress=gr.Progress()) -> str:
    """
    Validate a 3D model's fidelity.

    Returns:
        Fidelity report as markdown
    """
    if not PIPELINE_AVAILABLE:
        return "❌ Validation module not available."

    if model_file is None:
        return "❌ Please upload a 3D model file (.glb, .gltf, .obj)"

    try:
        progress(0.2, desc="Loading model...")

        validator = ModelFidelityValidator()

        progress(0.5, desc="Validating...")

        report = await validator.validate(model_file.name)

        progress(1.0, desc="Done!")

        status = "✅ PASSED" if report.passed else "❌ FAILED"

        result = f"""
# 3D Model Fidelity Report

## Overall Score: {report.overall_score:.1f}% {status}

**Threshold:** {MINIMUM_FIDELITY_SCORE}%

---

## Geometry Analysis

| Metric | Value |
|--------|-------|
| Vertex Count | {report.geometry.vertex_count:,} |
| Face Count | {report.geometry.face_count:,} |
| Is Watertight | {"✅" if report.geometry.is_watertight else "❌"} |
| Has Holes | {"❌ Yes" if report.geometry.has_holes else "✅ No"} |
| Geometry Score | {report.geometry.overall_score:.1f}% |

## Texture Analysis

| Metric | Value |
|--------|-------|
| Has Textures | {"✅" if report.textures.has_textures else "❌"} |
| Resolution | {report.textures.resolution or "N/A"} |
| Texture Score | {report.textures.overall_score:.1f}% |

## Material Analysis

| Metric | Value |
|--------|-------|
| Has Materials | {"✅" if report.materials.has_materials else "❌"} |
| Is PBR | {"✅" if report.materials.is_pbr else "❌"} |
| Material Score | {report.materials.overall_score:.1f}% |

---

## Issues Found

"""
        if report.issues:
            for issue in report.issues:
                result += f"- ⚠️ {issue}\n"
        else:
            result += "✅ No issues detected!\n"

        result += "\n\n---\n\n*Validated against SkyyRose 95% Fidelity Standard*"

        return result

    except Exception as e:
        logger.exception("Validation failed")
        return f"## ❌ Validation Error\n\n{str(e)}"


def run_async(coro):
    """Helper to run async functions in Gradio."""
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    return loop.run_until_complete(coro)


# Sync wrappers for Gradio
def generate_3d_sync(*args, **kwargs):
    return run_async(generate_3d_from_image(*args, **kwargs))


def enhance_3d_sync(*args, **kwargs):
    return run_async(enhance_3d_model(*args, **kwargs))


def validate_3d_sync(*args, **kwargs):
    return run_async(validate_3d_model(*args, **kwargs))


def create_app() -> gr.Blocks:
    """Create the Gradio application."""

    with gr.Blocks(
        title="SkyyRose 3D Model Studio",
        css=CSS,
        theme=gr.themes.Soft(
            primary_hue="pink",
            secondary_hue="gray",
        ),
    ) as app:
        # Header
        gr.HTML("""
        <div class="skyyrose-header">
            <h1>🌹 SkyyRose 3D Model Studio</h1>
            <p>AI-Powered 3D Generation with 95% Fidelity</p>
        </div>
        """)

        # Provider Status
        with gr.Accordion("🔌 Provider Status", open=False):
            gr.Markdown(get_provider_status())

        # Main Tabs
        with gr.Tabs():
            # Tab 1: Generate from Image
            with gr.TabItem("📸 Image to 3D"):
                gr.Markdown("""
                ### Generate 3D Models from Product Images
                Upload a product image to create a production-ready 3D model.
                All models are validated against the **95% fidelity threshold**.
                """)

                with gr.Row():
                    with gr.Column(scale=1):
                        image_input = gr.Image(
                            label="Product Image",
                            type="filepath",
                            height=300,
                        )
                        prompt_input = gr.Textbox(
                            label="Description (Optional)",
                            placeholder="e.g., Luxury rose gold bracelet with diamond accents",
                            lines=2,
                        )

                        with gr.Row():
                            provider_dropdown = gr.Dropdown(
                                label="Provider",
                                choices=["auto", "tripo", "huggingface", "meshy"],
                                value="auto",
                            )
                            quality_dropdown = gr.Dropdown(
                                label="Quality",
                                choices=["draft", "standard", "high", "production"],
                                value="production",
                            )

                        with gr.Row():
                            format_dropdown = gr.Dropdown(
                                label="Format",
                                choices=["glb", "gltf", "obj", "fbx"],
                                value="glb",
                            )
                            enforce_fidelity = gr.Checkbox(
                                label="Enforce 95% Fidelity",
                                value=True,
                            )

                        generate_btn = gr.Button(
                            "🚀 Generate 3D Model",
                            variant="primary",
                            size="lg",
                        )

                    with gr.Column(scale=1):
                        status_output = gr.Markdown(
                            label="Status",
                            value="*Upload an image and click Generate*",
                        )
                        fidelity_output = gr.Markdown(
                            label="Fidelity Report",
                        )
                        model_output = gr.File(
                            label="Download 3D Model",
                        )

                generate_btn.click(
                    fn=generate_3d_sync,
                    inputs=[
                        image_input,
                        prompt_input,
                        provider_dropdown,
                        quality_dropdown,
                        format_dropdown,
                        enforce_fidelity,
                    ],
                    outputs=[model_output, status_output, fidelity_output],
                )

            # Tab 2: Enhance Model
            with gr.TabItem("✨ Enhance Model"):
                gr.Markdown("""
                ### Improve Existing 3D Models
                Upload a 3D model to enhance its quality and meet the 95% fidelity threshold.
                """)

                with gr.Row():
                    with gr.Column(scale=1):
                        model_input = gr.File(
                            label="Upload 3D Model",
                            file_types=[".glb", ".gltf", ".obj", ".fbx"],
                        )

                        fidelity_slider = gr.Slider(
                            label="Target Fidelity (%)",
                            minimum=80,
                            maximum=100,
                            value=95,
                            step=1,
                        )

                        with gr.Row():
                            optimize_mesh = gr.Checkbox(
                                label="Optimize Mesh",
                                value=True,
                            )
                            upscale_textures = gr.Checkbox(
                                label="Upscale Textures",
                                value=True,
                            )
                            repair_mesh = gr.Checkbox(
                                label="Repair Mesh",
                                value=True,
                            )

                        enhance_btn = gr.Button(
                            "✨ Enhance Model",
                            variant="primary",
                            size="lg",
                        )

                    with gr.Column(scale=1):
                        enhance_status = gr.Markdown(
                            value="*Upload a model and click Enhance*",
                        )
                        enhanced_model = gr.File(
                            label="Download Enhanced Model",
                        )

                enhance_btn.click(
                    fn=enhance_3d_sync,
                    inputs=[
                        model_input,
                        fidelity_slider,
                        optimize_mesh,
                        upscale_textures,
                        repair_mesh,
                    ],
                    outputs=[enhanced_model, enhance_status],
                )

            # Tab 3: Validate Model
            with gr.TabItem("🔍 Validate Model"):
                gr.Markdown("""
                ### Validate 3D Model Fidelity
                Check if your 3D model meets the SkyyRose 95% fidelity standard.
                """)

                with gr.Row():
                    with gr.Column(scale=1):
                        validate_input = gr.File(
                            label="Upload 3D Model",
                            file_types=[".glb", ".gltf", ".obj", ".fbx"],
                        )

                        validate_btn = gr.Button(
                            "🔍 Validate Model",
                            variant="primary",
                            size="lg",
                        )

                    with gr.Column(scale=2):
                        validate_output = gr.Markdown(
                            value="*Upload a model and click Validate*",
                        )

                validate_btn.click(
                    fn=validate_3d_sync,
                    inputs=[validate_input],
                    outputs=[validate_output],
                )

            # Tab 4: Batch Processing
            with gr.TabItem("📦 Batch Processing"):
                gr.Markdown("""
                ### Batch 3D Model Generation
                Upload multiple images to generate 3D models in batch.

                *Coming soon...*
                """)

                gr.File(
                    label="Upload Images",
                    file_count="multiple",
                    file_types=["image"],
                )

                gr.Markdown("""
                **Batch processing will:**
                1. Process all uploaded images
                2. Generate 3D models with 95% fidelity enforcement
                3. Provide a downloadable ZIP with all models
                """)

        # Footer
        gr.HTML("""
        <div style="text-align: center; padding: 20px; color: #666; margin-top: 20px;">
            <p>🌹 <strong>SkyyRose 3D Model Studio</strong> | Powered by AI | 95% Fidelity Standard</p>
            <p style="font-size: 0.9em;">© 2024 SkyyRose LLC</p>
        </div>
        """)

    return app


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("🌹 SkyyRose 3D Model Studio")
    print("=" * 60)
    print(f"\n📊 Fidelity Threshold: {MINIMUM_FIDELITY_SCORE}%")
    print(f"🔌 Pipeline Available: {PIPELINE_AVAILABLE}")
    print("\n🔧 Provider Status:")
    print(get_provider_status())
    print("\n" + "=" * 60)
    print("Starting Gradio server...")
    print("=" * 60 + "\n")

    app = create_app()
    app.launch(
        server_name="0.0.0.0",  # nosec B104 — 0.0.0.0 required in containerized/cloud deployment; network isolation at infra layer
        server_port=7860,
        share=False,  # Set to True for public URL
        show_error=True,
    )
