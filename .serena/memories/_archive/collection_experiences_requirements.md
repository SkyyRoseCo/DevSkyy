# Collection Interactive Experiences — Requirements

## Collections Overview

### BLACK ROSE
- **Theme**: Dark Gothic Elegance
- **3D Scene**: Interactive rose garden (black/white/metallic roses, night sky, particle petals)
- **Colors**: #1a1a1a, #ffffff, #8b0000, metallic silver
- **File**: `src/collections/BlackRoseExperience.ts`

### LOVE HURTS
- **Theme**: Beauty and the Beast (Beast's perspective)
- **3D Scene**: Enchanted castle (rose under glass dome, candle flicker, petal physics)
- **Colors**: #b76e79, #1a0a0a, #dc143c, gold accents
- **File**: `src/collections/LoveHurtsExperience.ts`

### SIGNATURE
- **Theme**: Oakland/SF Tribute
- **3D Scene**: City landmarks tour (Golden Gate, Bay Bridge, Lake Merritt, Fox Theater)
- **Colors**: #d4af37 (gold), #f5f5f0 (cream), #8b7355 (bronze)
- **File**: `src/collections/SignatureExperience.ts`

## Common Requirements
- Three.js with 60fps target
- Responsive (mobile/tablet/desktop)
- WordPress WooCommerce product integration
- Lazy-loading + code-splitting for 3D assets
- SkyyRose brand DNA throughout

## File Structure
- **Base**: `src/collections/BaseCollectionExperience.ts`
- **Showroom**: `src/collections/ShowroomExperience.ts`
- **Runway**: `src/collections/RunwayExperience.ts`
- **Hotspots**: `src/collections/HotspotManager.ts`
- **AR**: `src/collections/ARTryOnViewer.ts`, `WebXRARViewer.ts`
- **WooCommerce**: `src/collections/WooCommerceProductLoader.ts`
- **WordPress templates**: `wordpress-theme/skyyrose-flagship/template-immersive-*.php`
- **Collection catalogs**: `wordpress-theme/skyyrose-flagship/template-collection-*.php`
