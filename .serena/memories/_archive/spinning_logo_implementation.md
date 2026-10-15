# SkyyRose Spinning Logo Implementation

## Overview
Production-ready spinning logo system with collection-specific color variants, implemented as a standalone, theme-agnostic module.

---

## File Structure

```
wordpress/skyyrose-immersive/
├── assets/
│   ├── css/
│   │   └── spinning-logo.css          # Standalone CSS (no dependencies)
│   ├── js/
│   │   └── header.js                  # Header behavior & logo color switching
│   └── images/
│       └── skyyrose-logo-spinner.svg  # Responsive SVG logo
├── inc/
│   └── spinning-logo-functions.php     # PHP functions & shortcodes
└── functions.php                       # Include spinning-logo-functions.php
```

---

## Integration Points

### WordPress Child Theme (Current)
File: `wordpress/skyyrose-immersive/inc/spinning-logo-functions.php`

**Include in functions.php:**
```php
require_once SKYYROSE_IMMERSIVE_DIR . '/inc/spinning-logo-functions.php';
```

### Usage Options

#### 1. PHP Function (Recommended for theme templates)
```php
<?php skyyrose_spinning_logo(); ?>
```

#### 2. Complete Header with Logo
```php
<?php skyyrose_header_with_spinning_logo(); ?>
```

#### 3. Shortcode (For Elementor/Page Builders)
```
[skyyrose_spinning_logo]
[skyyrose_spinning_logo variant="silver"]
```

---

## Color Variants (Auto-Detected)

| Page Type | Variant | Color | Glow |
|-----------|---------|-------|------|
| Homepage | gold | #D4AF37 | rgba(212, 175, 55, 0.3) |
| Black Rose Collection | silver | #C0C0C0 | rgba(192, 192, 192, 0.3) |
| Love Hurts Collection | deep-rose | #D4A5A5 | rgba(212, 165, 165, 0.3) |
| Signature Collection | rose-gold | #B76E79 | rgba(183, 110, 121, 0.3) |
| Light Backgrounds | black | #0D0D0D | rgba(0, 0, 0, 0.2) |

**Auto-detection logic:**
- Checks `is_front_page()`, `is_product_category()`, `is_page()`, `is_product()`
- Falls back to page slug analysis
- Product pages inherit from their collection category
- Default: gold

---

## Animation Specifications

```yaml
animation:
  type: continuous_rotate
  duration: 8s
  timing_function: linear
  direction: normal
  hover_behavior: pause  # Pauses rotation on hover for elegance

glow_effect:
  enabled: true
  blur: 20px
  hover_blur: 30px  # Intensifies on hover

responsive:
  desktop: 60px × 60px
  mobile: 48px × 48px (below 768px)
```

---

## Standalone Features

### 1. No External Dependencies
- CSS: Self-contained, no CSS framework dependencies
- JS: Pure vanilla JavaScript (no jQuery)
- SVG: Inline currentColor for dynamic theming

### 2. Theme-Agnostic
All classes are namespaced with `skyyrose-` prefix:
```css
.skyyrose-logo
.skyyrose-logo__spinner
.skyyrose-logo--gold
.skyyrose-logo--silver
.site-header
.site-header--scrolled
```

### 3. Migration-Ready
To migrate to a different theme:
1. Copy 3 files:
   - `assets/css/spinning-logo.css`
   - `assets/js/header.js`
   - `inc/spinning-logo-functions.php`
2. Include PHP file in new theme's `functions.php`
3. Enqueue CSS/JS (already handled in PHP file)
4. Use `skyyrose_spinning_logo()` or shortcode

---

## Header Scroll Behavior

JavaScript automatically:
1. Adds `.site-header--scrolled` class after 50px scroll
2. Adds backdrop blur + solid background
3. Updates logo color based on body classes

**Body classes required for auto-color:**
- `.collection-signature` → rose-gold
- `.collection-blackrose` → silver
- `.collection-lovehurts` → deep-rose
- `.home` → gold

---

## Performance Optimizations

1. **CSS**: Minified animation keyframes
2. **SVG**: Optimized paths, uses `currentColor`
3. **JS**: Debounced scroll listener (built into browser)
4. **Load Strategy**: CSS/JS enqueued only when needed

---

## Accessibility

- Semantic HTML (`<header>`, `<nav>`, `<a>`)
- ARIA labels on all interactive elements
- Focus states on logo and navigation links
- Screen reader friendly (`aria-label="SkyyRose Home"`)

---

## Elementor Integration

### Option 1: Shortcode Widget
Insert in Elementor:
```
[skyyrose_spinning_logo variant="gold"]
```

### Option 2: Custom HTML Widget
```html
<div class="skyyrose-logo skyyrose-logo--gold">
  <img src="/wp-content/themes/skyyrose-immersive/assets/images/skyyrose-logo-spinner.svg"
       alt="SkyyRose"
       class="skyyrose-logo__spinner" />
</div>
```

### Option 3: Theme Builder Header
Use `skyyrose_header_with_spinning_logo()` in custom header template

---

## Manual Color Override

### JavaScript
```javascript
updateLogoColor('silver');  // Changes to silver variant
```

### PHP
```php
skyyrose_spinning_logo_shortcode(['variant' => 'rose-gold']);
```

### CSS Class Toggle
```javascript
const logo = document.querySelector('.skyyrose-logo');
logo.className = 'skyyrose-logo skyyrose-logo--deep-rose';
```

---

## Testing Checklist

- [x] Logo spins continuously (8s rotation)
- [x] Logo pauses on hover
- [x] Glow effect visible and intensifies on hover
- [x] Color changes on different collection pages
- [x] Header becomes solid on scroll (50px threshold)
- [x] Responsive sizing (60px desktop, 48px mobile)
- [x] Shortcode works in Elementor
- [x] No console errors
- [x] No layout shifts during load

---

## Customization Examples

### Change Spin Speed
```css
.skyyrose-logo__spinner {
  animation-duration: 5s; /* Faster (was 8s) */
}
```

### Disable Hover Pause
```css
.skyyrose-logo:hover .skyyrose-logo__spinner {
  animation-play-state: running; /* Override pause */
}
```

### Add New Color Variant
```css
.skyyrose-logo--emerald .skyyrose-logo__spinner path,
.skyyrose-logo--emerald .skyyrose-logo__spinner circle {
  fill: #50C878;
}
.skyyrose-logo--emerald .skyyrose-logo__spinner {
  filter: drop-shadow(0 0 20px rgba(80, 200, 120, 0.3));
}
```

---

## Troubleshooting

### Logo Not Spinning
- Check CSS is enqueued: `View Source → Search "spinning-logo.css"`
- Verify SVG exists at correct path
- Check browser console for 404 errors

### Wrong Color on Page
- Inspect body classes: `document.body.className`
- Verify PHP function logic in `skyyrose_get_logo_variant()`
- Check WooCommerce category slugs match (black-rose, love-hurts, signature)

### Header Not Solid on Scroll
- Verify JS is enqueued: `View Source → Search "header.js"`
- Check `#site-header` ID exists on header element
- Test scroll event: `window.pageYOffset` should update

---

## Future Enhancements

1. **Dark Mode Support**: Detect prefers-color-scheme
2. **3D Logo**: Integrate Three.js for 3D spinning rose
3. **GSAP Animation**: Replace CSS keyframes with GSAP timeline
4. **Intersection Observer**: Color change based on section scroll
5. **Admin Customizer**: WordPress Customizer panel for logo settings

---

## Version History

- **1.0.0** (2024-12-12): Initial implementation
  - 5 color variants
  - Auto-detection logic
  - Responsive design
  - Shortcode support
  - Theme-agnostic architecture

---

## Support

- File bugs: https://github.com/The-Skyy-Rose-Collection-LLC/DevSkyy/issues
- Email: support@skyyrose.com
- Docs: `SPINNING_LOGO_SPEC.md`
