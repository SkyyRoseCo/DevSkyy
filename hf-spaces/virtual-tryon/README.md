---
title: SkyyRose Virtual Try-On
emoji: 👗
colorFrom: pink
colorTo: purple
sdk: gradio
sdk_version: 6.26.0
app_file: app.py
pinned: true
license: mit
---

# SkyyRose Virtual Try-On

**Where Love Meets Luxury** - Try on SkyyRose merchandise using AI-powered
virtual try-on.

## Features

- 📸 Upload your photo
- 👕 Select any SkyyRose product
- 🎨 AI-powered virtual try-on with FASHN technology
- 💎 Three exclusive collections: SIGNATURE, BLACK ROSE, LOVE HURTS

## Collections

### SIGNATURE Collection

Premium, sophisticated streetwear with timeless elegance

### BLACK ROSE Collection

Gothic, bold designs with romantic darkness

### LOVE HURTS Collection

Edgy, passionate pieces with rebellious luxury

## Technology

Powered by FASHN AI for realistic garment transfer and virtual try-on
experiences.

---

**SkyyRose** - Premium luxury streetwear brand Website: <https://skyyrose.co>

## Local compatibility checks

Use an isolated Python 3.13 environment and install this Space's requirements.
The Gradio requirement and `sdk_version` intentionally select the same tested
release; update them together. Gradio 6 accepts the theme on `launch()`.

```bash
python3 -m pip install -r hf-spaces/virtual-tryon/requirements.txt pytest
GRADIO_ANALYTICS_ENABLED=False HF_HUB_OFFLINE=1 python3 -m pytest hf-spaces/virtual-tryon/tests -q
```

These offline tests construct the real Gradio interface, exercise Pillow image
inputs/outputs, and run the submitted callback against fake HTTP responses. They
do not authenticate to FASHN, generate paid output, launch a public server, or
deploy the Space. Live provider behavior and deployment remain separate checks.
