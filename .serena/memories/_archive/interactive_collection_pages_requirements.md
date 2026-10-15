# Interactive Collection Pages Requirements - SkyyRose

**Date Created**: 2026-01-11
**Project**: DevSkyy Interactive Collection Experiences
**Status**: Active Development

---

## BLACK ROSE Collection

**Theme**: Dark but Elegant Aesthetics

**Interactive Experience**:
- **Scene**: Interactive rose garden with Three.js
- **Roses**: Black, white, and metallic roses
- **Environment**: Night sky with clouds
- **Header**: Rotating BLACK ROSE logo (persistent in header)
- **Mood**: Gothic luxury, mysterious, powerful
- **Color Palette**: #1a1a1a (black), #ffffff (white), metallic/silver accents, #8b0000 (dark red accents)

**Technical Notes**:
- Use existing `src/collections/BlackRoseExperience.ts`
- Enhance with rose garden scene (multiple roses, not just one)
- Night sky with moving clouds (shader/particle system)
- Logo rotation animation in header (CSS 3D transform or Three.js)

---

## LOVE HURTS Collection

**Theme**: Beauty and the Beast (from the Beast's perspective)

**Interactive Experience**:
- **Scene**: Interactive castle experience
- **Main Feature**: Enchanted Rose (like Beauty and the Beast)
- **Perspective**: From the Beast's side (dark, emotional, passionate)
- **Environment**: Gothic castle interior with dim lighting
- **Rose Mechanic**: Enchanted rose under glass dome, petals falling, glowing effects
- **Mood**: Passion meets pain, raw emotion, romantic darkness
- **Color Palette**: #b76e79 (rose pink), #1a0a0a (dark background), #dc143c (crimson), gold accents

**Technical Notes**:
- Use existing `src/collections/LoveHurtsExperience.ts`
- Enhance with castle environment (stone walls, archways, candles)
- Enchanted rose with glass dome (particle effects for glow)
- Petal falling animation (physics/particles)
- Dark, moody lighting (point lights, shadows)

---

## SIGNATURE Collection

**Theme**: Tribute to Oakland/San Francisco

**Interactive Experience**:
- **Scene**: City landmarks showcase
- **Featured Landmarks**:
  - Golden Gate Bridge
  - Bay Bridge
  - Oakland landmarks (Lake Merritt, Fox Theater, Jack London Square)
  - San Francisco landmarks (Alcatraz, Coit Tower, Painted Ladies)
- **Style**: Minimalist, elegant, modern
- **Environment**: Day/night cycle or golden hour lighting
- **Camera**: Smooth transitions between landmarks
- **Mood**: Timeless luxury, urban sophistication
- **Color Palette**: #d4af37 (gold), #f5f5f0 (cream), #2a2a2a (dark text), #8b7355 (bronze)

**Technical Notes**:
- Use existing `src/collections/SignatureExperience.ts`
- Model key landmarks (simplified geometric style)
- Camera path that tours the landmarks
- Golden hour lighting (warm tones)
- Fog/atmosphere for SF vibes

---

## Common Requirements (All Collections)

1. **Three.js Integration**: All collections MUST have interactive Three.js components
2. **Responsive**: Mobile, tablet, desktop optimized
3. **Performance**: 60fps, lazy-loading, code-splitting
4. **WordPress Integration**: Fetch products from WooCommerce API
5. **2D/2.5D Assets**: Use existing assets from `assets/2d-25d-assets/`
6. **Luxury Feel**: Premium animations, smooth transitions
7. **Brand DNA**: SkyyRose colors, typography, rebellious elegance

---

## File References

**Existing Three.js Experiences**:
- `src/collections/BlackRoseExperience.ts`
- `src/collections/LoveHurtsExperience.ts`
- `src/collections/SignatureExperience.ts`

**Base Classes**:
- `src/collections/BaseCollectionExperience.ts`

**Components**:
- `src/components/collections/CollectionLayout.tsx` (in progress)

**Types**:
- `src/types/collections.ts`

---

## PRD Reference

See `.ralph/prd-interactive-collections.json` for full user stories and acceptance criteria.

**Current Story**: COLL-001 (Base CollectionLayout component)
**Next Stories**: COLL-002 (BLACK ROSE Three.js), COLL-003 (WordPress API), etc.

---

## Design Inspiration

**BLACK ROSE**: Gothic rose gardens, night photography, metal roses, dark luxury brands
**LOVE HURTS**: Beauty and the Beast castle, enchanted objects, romantic gothic architecture
**SIGNATURE**: Oakland/SF street photography, urban minimalism, golden hour cityscapes

---

**CRITICAL**: All interactive experiences must be immersive, performant, and embody SkyyRose's brand identity of "luxury meets rebellion."
