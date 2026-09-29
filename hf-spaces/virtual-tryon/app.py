"""
SkyyRose Virtual Try-On
=======================

Try on SkyyRose merchandise using FASHN AI.

Upload a photo of yourself and select a product to see how it looks on you!

Features:
- Virtual try-on with FASHN API
- SkyyRose product catalog integration
- Real-time image processing
- High-quality fashion visualization

Author: DevSkyy Platform Team
Version: 1.0.0
"""

import asyncio
import base64
import io
import os

import aiohttp
import gradio as gr
from PIL import Image

# =============================================================================
# Configuration
# =============================================================================

FASHN_API_KEY = os.getenv("FASHN_API_KEY", "")
FASHN_API_BASE_URL = os.getenv("FASHN_API_BASE_URL", "https://api.fashn.ai/v1")
POLL_INTERVAL = 1.0
TIMEOUT = 120.0

# Sample products (in production, this would be loaded from WooCommerce)
SAMPLE_PRODUCTS = {
    "BLACK ROSE - Gothic Hoodie": "https://skyyrose.co/wp-content/uploads/black-rose-hoodie.jpg",
    "SIGNATURE - Luxury Tee": "https://skyyrose.co/wp-content/uploads/signature-tee.jpg",
    "LOVE HURTS - Statement Tee": "https://skyyrose.co/wp-content/uploads/love-hurts-tee.jpg",
}


# =============================================================================
# FASHN API Integration
# =============================================================================


async def encode_image_to_base64(image: Image.Image) -> str:
    """Encode PIL Image to base64 data URL."""
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    buffer.seek(0)

    b64 = base64.b64encode(buffer.read()).decode()
    return f"data:image/png;base64,{b64}"


async def fashn_api_request(
    method: str,
    endpoint: str,
    data: dict = None,
    headers: dict = None,
) -> dict:
    """Make authenticated request to FASHN API."""
    if not FASHN_API_KEY:
        raise ValueError(
            "FASHN_API_KEY not configured. Get your API key from: https://fashn.ai/dashboard"
        )

    url = f"{FASHN_API_BASE_URL}/{endpoint.lstrip('/')}"

    request_headers = {
        "Authorization": f"Bearer {FASHN_API_KEY}",
        "Content-Type": "application/json",
    }
    if headers:
        request_headers.update(headers)

    timeout = aiohttp.ClientTimeout(total=TIMEOUT)

    async with aiohttp.ClientSession(
        headers=request_headers, timeout=timeout
    ) as session:  # noqa: SIM117
        async with session.request(method, url, json=data) as response:
            result = await response.json()

            if response.status >= 400:
                error_msg = result.get("error", {}).get("message", str(result))
                raise Exception(f"FASHN API error ({response.status}): {error_msg}")

            return result


async def poll_prediction(prediction_id: str) -> dict:
    """Poll prediction until complete."""
    while True:
        result = await fashn_api_request("GET", f"/predictions/{prediction_id}")

        status = result.get("status", "processing")

        if status == "succeeded":
            return result

        if status == "failed":
            error = result.get("error", "Unknown error")
            raise Exception(f"Prediction failed: {error}")

        if status == "canceled":
            raise Exception("Prediction was canceled")

        await asyncio.sleep(POLL_INTERVAL)


async def virtual_tryon_async(
    model_image: Image.Image,
    garment_image: Image.Image,
    category: str = "tops",
    mode: str = "balanced",
) -> Image.Image:
    """
    Perform virtual try-on using FASHN API.

    Args:
        model_image: Image of the person
        garment_image: Image of the garment
        category: Garment category (tops, bottoms, dresses, etc.)
        mode: Quality mode (quality, balanced, fast)

    Returns:
        Result image with garment on person
    """
    # Encode images to base64
    model_data = await encode_image_to_base64(model_image)
    garment_data = await encode_image_to_base64(garment_image)

    # Create prediction
    response = await fashn_api_request(
        "POST",
        "/run",
        {
            "model_image": model_data,
            "garment_image": garment_data,
            "category": category,
            "mode": mode,
            "output_width": 576,
            "output_height": 864,
        },
    )

    prediction_id = response.get("id")
    if not prediction_id:
        raise ValueError("No prediction ID returned")

    # Poll for result
    result = await poll_prediction(prediction_id)

    # Get output URL
    output = result.get("output", [])
    if not output:
        raise ValueError("No output generated")

    image_url = output[0] if isinstance(output, list) else output

    # Download result image
    timeout = aiohttp.ClientTimeout(total=30.0)
    async with aiohttp.ClientSession(timeout=timeout) as session:  # noqa: SIM117
        async with session.get(image_url) as response:
            if response.status >= 400:
                raise Exception(f"Download failed: {response.status}")

            image_data = await response.read()
            return Image.open(io.BytesIO(image_data))


def virtual_tryon(
    model_image: Image.Image,
    garment_image: Image.Image,
    category: str = "tops",
    mode: str = "balanced",
) -> Image.Image:
    """
    Synchronous wrapper for virtual try-on.

    Args:
        model_image: Image of the person
        garment_image: Image of the garment
        category: Garment category
        mode: Quality mode

    Returns:
        Result image
    """
    if not FASHN_API_KEY:
        # Return informative placeholder if API key not configured
        placeholder = Image.new("RGB", (576, 864), color=(240, 240, 240))
        return placeholder

    try:
        return asyncio.run(virtual_tryon_async(model_image, garment_image, category, mode))
    except Exception:
        # Create error image
        error_img = Image.new("RGB", (576, 864), color=(240, 240, 240))
        return error_img


# =============================================================================
# Gradio Interface
# =============================================================================


def create_app() -> gr.Blocks:
    """Create Gradio application."""

    with gr.Blocks(title="SkyyRose Virtual Try-On") as app:
        gr.Markdown("""
            # 🌹 SkyyRose Virtual Try-On

            **Where Love Meets Luxury**

            Try on SkyyRose merchandise using AI-powered virtual try-on.
            Upload your photo and select a product to see how it looks on you!
            """)

        with gr.Row():
            with gr.Column(scale=1):
                model_input = gr.Image(
                    label="Upload Your Photo",
                    type="pil",
                    sources=["upload", "clipboard"],
                )

                garment_input = gr.Image(
                    label="Select Product Image",
                    type="pil",
                    sources=["upload", "clipboard"],
                )

                with gr.Accordion("Advanced Settings", open=False):
                    category_select = gr.Dropdown(
                        choices=["tops", "bottoms", "dresses", "outerwear", "full_body"],
                        value="tops",
                        label="Garment Category",
                    )

                    mode_select = gr.Radio(
                        choices=[
                            ("Quality (Slower, Better)", "quality"),
                            ("Balanced (Recommended)", "balanced"),
                            ("Fast (Quicker, Good)", "fast"),
                        ],
                        value="balanced",
                        label="Processing Mode",
                    )

                submit_btn = gr.Button("✨ Try On", variant="primary", size="lg")

            with gr.Column(scale=1):
                output = gr.Image(label="Result", type="pil")

                gr.Markdown("""
                    ### Tips for Best Results
                    - Use a **clear, well-lit** photo
                    - Face the camera directly
                    - Wear **fitted clothing** (easier for AI to replace)
                    - Stand with arms slightly away from body
                    - Use **high-resolution** images
                    """)

        gr.Markdown("""
            ## SkyyRose Collections

            ### 🖤 BLACK ROSE
            Gothic luxury and dark elegance. Embrace the darkness with sophistication.

            ### ✨ SIGNATURE
            Understated luxury streetwear. Where minimalism meets premium quality.

            ### 💔 LOVE HURTS
            Emotional authenticity and artistic passion. Wear your heart boldly.

            ---

            ### How It Works
            1. **Upload Your Photo** - A clear, front-facing photo works best
            2. **Select Product** - Choose from SkyyRose merchandise or upload your own
            3. **Click Try On** - AI will generate a photorealistic image of you wearing the product
            4. **Download & Share** - Save your result and share on social media!

            ### Privacy & Security
            - Images are processed securely via FASHN API
            - No images are stored on our servers
            - Results are temporary and auto-deleted after 24 hours

            ---

            *Powered by [FASHN AI](https://fashn.ai) | Visit [SkyyRose.co](https://skyyrose.co) |
            Follow [@skyyrose_co](https://instagram.com/skyyrose_co)*
            """)

        submit_btn.click(
            fn=virtual_tryon,
            inputs=[model_input, garment_input, category_select, mode_select],
            outputs=output,
        )

    return app


# =============================================================================
# Main
# =============================================================================

if __name__ == "__main__":
    app = create_app()
    app.launch(
        theme=gr.themes.Soft(primary_hue="rose", secondary_hue="stone"),
        server_name="0.0.0.0",  # nosec B104 — 0.0.0.0 required in containerized/cloud deployment; network isolation at infra layer
        server_port=7860,
        share=False,
    )
