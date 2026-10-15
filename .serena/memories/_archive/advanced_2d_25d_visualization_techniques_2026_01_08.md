# Advanced 2D/2.5D Product Visualization Techniques

**Created**: 2026-01-08
**Purpose**: Document proven techniques for creating professional product visualizations for WooCommerce/WordPress

---

## Overview

Successfully implemented 4 advanced visualization techniques using Pillow + OpenCV for SkyyRose products. Generated 104/104 variations (26 products × 4 types).

**Output Directory**: `/assets/2d-25d-assets/`

---

## Technique 1: Drop Shadow (Professional Depth)

**Purpose**: Add professional depth perception with realistic offset shadows

**Implementation** (Context7 Pillow GaussianBlur):

```python
def create_drop_shadow(image: Image.Image, offset: Tuple[int, int] = (15, 15),
                       blur_radius: int = 25, opacity: int = 180) -> Image.Image:
    """Create professional drop shadow effect."""
    # Create canvas with space for shadow
    shadow_size = (image.width + abs(offset[0]) + blur_radius * 2,
                   image.height + abs(offset[1]) + blur_radius * 2)
    shadow = Image.new("RGBA", shadow_size, (0, 0, 0, 0))

    # Extract alpha channel as shadow mask
    shadow_mask = Image.new("RGBA", image.size, (0, 0, 0, opacity))
    shadow_mask.putalpha(image.split()[3])

    # Paste and blur (Context7 technique)
    shadow.paste(shadow_mask, shadow_pos)
    shadow = shadow.filter(ImageFilter.GaussianBlur(blur_radius))

    # Composite original over shadow
    shadow.paste(image, image_pos, image)
    return shadow
```

**Parameters**:

- Offset: (15, 15) pixels - diagonal shadow
- Blur radius: 25px - soft, professional shadow
- Opacity: 180/255 - visible but not harsh

**Output**: `{product}_shadow.jpg`

---

## Technique 2: Depth Effect (Simulated Depth of Field)

**Purpose**: Create photography-style depth of field with selective focus

**Implementation** (Context7 OpenCV Canny + Pillow):

```python
def create_depth_effect(image: Image.Image, focal_strength: float = 0.7) -> Image.Image:
    """Depth of field using edge detection."""
    # Convert to OpenCV
    img_array = np.array(image)
    gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)

    # Detect edges (Context7 Canny technique)
    edges = cv2.Canny(gray, 50, 150)

    # Create focus mask (dilate edges)
    kernel = np.ones((21, 21), np.uint8)
    focus_mask = cv2.dilate(edges, kernel, iterations=1)
    focus_mask = cv2.GaussianBlur(focus_mask, (51, 51), 0)

    # Blur unfocused areas
    blurred = image.filter(ImageFilter.GaussianBlur(radius=8 * focal_strength))

    # Composite focused/blurred
    result = Image.composite(image, blurred, ImageOps.invert(focus_pil))
    return result
```

**Parameters**:

- Canny edges: (50, 150) thresholds
- Kernel: 21×21 for edge dilation
- Focal strength: 0.7 (70% blur on non-focal areas)

**Output**: `{product}_depth.jpg`

---

## Technique 3: Parallax Layers (2.5D Web Animation)

**Purpose**: Create parallax-ready layered image for interactive web effects

**Implementation** (OpenCV Contour Detection):

```python
def create_parallax_layers(image: Image.Image) -> Image.Image:
    """Separate foreground/background for parallax."""
    # Find product boundaries
    edges = cv2.Canny(gray, 30, 100)
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Get largest contour (product)
    largest_contour = max(contours, key=cv2.contourArea)

    # Create foreground mask
    mask = np.zeros(gray.shape, np.uint8)
    cv2.drawContours(mask, [largest_contour], -1, 255, -1)
    mask = cv2.GaussianBlur(mask, (21, 21), 0)

    # Create layers
    foreground = image.copy()
    background = image.filter(ImageFilter.GaussianBlur(5))
    background = ImageEnhance.Brightness(background).enhance(0.9)

    # Canvas with 20px offset space
    canvas = Image.new("RGBA", (image.width + 20, image.height + 20), (0, 0, 0, 0))
    canvas.paste(background, (10, 10), background)
    canvas.paste(foreground, (5, 5), mask_pil)
    return canvas
```

**Parameters**:

- Canny edges: (30, 100) - detect product boundary
- Background blur: 5px
- Background brightness: 0.9 (10% darker)
- Canvas offset: 20px total (10px background, 5px foreground)

**Output**: `{product}_parallax.png` (PNG for transparency)

**Web Usage**:

```css
.parallax-container {
    position: relative;
    overflow: hidden;
}
.parallax-layer {
    transition: transform 0.1s ease-out;
}
/* Move background 10px, foreground 5px on hover */
```

---

## Technique 4: Enhanced Detail (Sharpened Textures)

**Purpose**: Enhance product details with professional sharpening

**Implementation** (Context7 DETAIL + SHARPEN filters):

```python
def create_enhanced_detail(image: Image.Image, sharpness: float = 2.0) -> Image.Image:
    """Enhance details with Context7 techniques."""
    # Apply DETAIL filter (Context7)
    enhanced = image.filter(ImageFilter.DETAIL)

    # Apply SHARPEN filter
    enhanced = enhanced.filter(ImageFilter.SHARPEN)

    # Enhance sharpness programmatically
    enhancer = ImageEnhance.Sharpness(enhanced)
    enhanced = enhancer.enhance(sharpness)

    # Slight contrast boost
    contrast = ImageEnhance.Contrast(enhanced)
    enhanced = contrast.enhance(1.1)
    return enhanced
```

**Parameters**:

- Sharpness: 2.0 (200% enhancement)
- Contrast: 1.1 (110% - subtle boost)

**Output**: `{product}_detail.jpg`

---

## Execution Results

**Generated**: 104/104 variations (100% success rate)

**Breakdown**:

- 26 drop shadow images
- 26 depth effect images
- 26 parallax layer images
- 26 enhanced detail images

**Total Assets**: `/Users/coreyfoster/DevSkyy/assets/2d-25d-assets/` (104 files)

---

## Future Enhancements

**Potential Improvements**:

1. **3D Depth Maps**: Use MiDaS depth estimation for more accurate depth effects
2. **AI Upscaling**: Apply Real-ESRGAN before visualization for 4K quality
3. **Smart Object Detection**: Use YOLO/Detectron2 for automatic product segmentation
4. **HDR Processing**: Tone mapping for luxury product photography look
5. **Adaptive Parallax**: Generate multiple layer depths (background, mid, foreground)
6. **Video Variations**: Generate rotating 360° parallax videos
7. **AR-Ready Depth**: Export depth maps for WebXR/AR experiences

**Library Alternatives**:

- **Kornia**: GPU-accelerated PyTorch vision library (faster than OpenCV)
- **Albumentations**: Advanced augmentation library with 70+ transforms
- **Scikit-image**: Scientific image processing (morphology, filters)

---

## WordPress Integration Notes

**Custom CSS** for parallax effects should be added to WooCommerce product pages:

```css
.woocommerce-product-gallery__image.parallax-enabled {
    position: relative;
    overflow: hidden;
}

.woocommerce-product-gallery__image.parallax-enabled img {
    transition: transform 0.15s cubic-bezier(0.4, 0.0, 0.2, 1);
}

.woocommerce-product-gallery__image.parallax-enabled:hover img {
    transform: scale(1.05);
}
```

**JavaScript** for interactive parallax:

```javascript
document.querySelectorAll('.parallax-enabled').forEach(container => {
    container.addEventListener('mousemove', (e) => {
        const rect = container.getBoundingClientRect();
        const x = (e.clientX - rect.left) / rect.width - 0.5;
        const y = (e.clientY - rect.top) / rect.height - 0.5;
        const img = container.querySelector('img');
        img.style.transform = `translate(${x * 10}px, ${y * 10}px) scale(1.05)`;
    });
});
```

---

**Last Applied**: 2026-01-08
**Success Rate**: 100% (104/104 generated)
**Status**: Production-ready, awaiting WordPress upload
