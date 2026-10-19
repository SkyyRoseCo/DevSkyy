# SkyyRose WordPress Child Theme - Deployment Guide

## Package Location

`/Users/coreyfoster/DevSkyy/skyyrose-shoptimizer-child.zip` (700KB)

## WordPress Deployment Steps

### 1. Upload Theme

```bash
# Via WordPress Admin
1. Navigate to: Appearance → Themes → Add New → Upload Theme
2. Choose file: skyyrose-shoptimizer-child.zip
3. Click "Install Now"
4. Click "Activate"

# Via FTP/SFTP
1. Unzip locally
2. Upload `shoptimizer-child/` folder to:
   /wp-content/themes/shoptimizer-child/
3. Activate via WP Admin → Appearance → Themes
```

### 2. Verify Assets Loaded

Check logos exist at:

- `/wp-content/themes/shoptimizer-child/assets/logos/black-rose-trophy-cosmic.png`
- `/wp-content/themes/shoptimizer-child/assets/logos/love-hurts-trophy-red.png`
- `/wp-content/themes/shoptimizer-child/assets/logos/signature-rose-rosegold.png`
- `/wp-content/themes/shoptimizer-child/assets/logos/sr-monogram-rosegold.png`
- `/wp-content/themes/shoptimizer-child/assets/logos/love-hurts-text-logo.png`

### 3. Configure Collection on Pages

**Edit any page** → Sidebar → **"🌹 SkyyRose Collection Settings"**

**Options**:

- Collection: BLACK ROSE / LOVE HURTS / SIGNATURE
- Checkbox: "Show collection logo at top of page"

**Auto-applied**:

- Body class: `collection-{name}`
- Header logo: Rotating 80px logo
- Page header: Rotating 500px collection trophy
- Footer logos: Dual rotating logos

### 4. Shortcodes Available

```html
[collection_logo collection="black-rose" size="large"]
[collection_logo collection="love-hurts" size="medium"]
[collection_logo collection="signature" size="hero"]
[collection_logo collection="sr" size="small"]
```

**Size Options**: `small` (200px), `medium` (400px), `large` (600px), `hero` (800px)

### 5. Rotating Animations

**8 Locations**:

1. Site Header (80px, rotate3DContinuous, 10s)
2. Collection Page Headers (500px, rotate3D + gentleFloat + sparkle, 8s)
3. Product Badges (60px, rotate3D, 6s)
4. Breadcrumbs (40px, rotate3DContinuous, 10s)
5. Footer (100px + 60px, rotate3DContinuous + pulse)
6. Page Titles on hover (50px, rotate3D, 4s)
7. Mega Menu Items (40px, spinGlow, 4s)
8. Loading Screens (100px)

**Animation Types**:

- `rotate3D`: 8s 3D tilt rotation
- `rotate3DContinuous`: 10s perpetual with scale
- `spinGlow`: 4-8s 2D with pulsing glow
- `sparkle`: 2s multi-layer box-shadow
- `heartbeat`: 2s scale pulse (LOVE HURTS only)

### 6. Collection Styling

**BLACK ROSE**: Gothic silver (#C0C0C0), white (#FFF), black (#0A0A0A), cosmic galaxy glow

**LOVE HURTS**: Crimson (#DC143C), rose (#B76E79), gold (#FFD700), warm red glow + heartbeat

**SIGNATURE**: Rose gold (#C9A962), pink (#B76E79), black (#1A1815), elegant shimmer

### 7. Hard Refresh After Activation

Press: `Ctrl+Shift+R` (Windows/Linux) or `Cmd+Shift+R` (Mac)

### 8. Performance Notes

- **Total assets**: 680KB (5 logos)
- **CSS animations**: Hardware-accelerated (GPU)
- **Load impact**: <0.5s first load, cached after
- **Mobile**: Optimized with reduced sizes
- **Accessibility**: Respects `prefers-reduced-motion`

## Theme Features

### Auto-Functions (No Configuration)

✅ Collection body classes applied automatically
✅ Logos rotate in header/footer globally
✅ Product badges auto-detect WooCommerce categories
✅ Breadcrumbs show rotating icon
✅ Meta box for per-page collection selection

### Customization

**Change animation speed** - Edit `style.css` animation durations
**Disable animations** - Add `animation: none !important;` to selectors
**Change logo sizes** - Modify width/height in CSS
**Add new locations** - Use CSS `::before` pseudo-elements with logo URLs

## WordPress Credentials

**URL**: <https://skyyrose.co>
**WooCommerce API Key**: (stored in DevSkyy env: `WOOCOMMERCE_KEY`)
**WooCommerce Secret**: (stored in DevSkyy env: `WOOCOMMERCE_SECRET`)

## Support

Issues: Contact via DevSkyy backend or skyyrose.co/contact
