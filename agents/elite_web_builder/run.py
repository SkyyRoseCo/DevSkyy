#!/usr/bin/env python3
"""
Elite Web Builder — Runner

Loads environment, initializes the Director, feeds the PRD, and reports results.

Usage:
    .venv/bin/python run.py                    # Full PRD execution
    .venv/bin/python run.py --dry-run          # Planning only (no agent execution)
    .venv/bin/python run.py --prd custom.md    # Custom PRD file
"""

from __future__ import annotations

import argparse
import asyncio
import json
import logging
import os
import sys
import time
from pathlib import Path
from typing import Any

# ---------------------------------------------------------------------------
# Environment setup (MUST happen before any SDK imports)
# ---------------------------------------------------------------------------

ROOT = Path(__file__).resolve().parent
PROJECT_ROOT = ROOT.parent.parent  # DevSkyy/

# skyyrose.core.env_loader handles the .env file cascade + Gemini alias
# normalization. Primary key file: DevSkyy/.env.elite-web-builder.
# Append (not insert) so ROOT's local `agents/` package still wins import
# resolution over the repo-root `agents/` directory.
if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))
from skyyrose.core.env_loader import load_project_env  # noqa: E402

load_project_env(PROJECT_ROOT)

# Verify required keys before expensive imports
_REQUIRED_KEYS = {
    "ANTHROPIC_API_KEY": "Anthropic (Director + Frontend + Backend)",
    "GEMINI_API_KEY": "Google (Design System + Performance)",
    "OPENAI_API_KEY": "OpenAI (SEO Content)",
}

_missing_keys = [
    f"  {k} — needed for: {desc}" for k, desc in _REQUIRED_KEYS.items() if not os.getenv(k)
]
if _missing_keys:
    print("\n  Elite Web Builder — missing API keys:\n")
    for line in _missing_keys:
        print(line)
    print(
        "\n  Populate DevSkyy/.env.elite-web-builder (primary) or export the "
        "variables in your shell. The file is gitignored — each dev keeps "
        "their own copy.\n"
    )
    sys.exit(1)

# ---------------------------------------------------------------------------
# Now safe to import heavy modules
# ---------------------------------------------------------------------------

# Ensure elite_web_builder root is on path
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from director import Director  # noqa: E402

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("elite_web_builder")


# ---------------------------------------------------------------------------
# Default PRD (from knowledge files)
# ---------------------------------------------------------------------------

DEFAULT_PRD = """\
Build the SkyyRose Flagship WordPress theme — a marketplace-ready luxury streetwear \
e-commerce theme for WordPress.com Atomic with WooCommerce.

## Design Philosophy (MANDATORY — applies to ALL visual output)
Every page, component, and interaction must follow these principles:
- Landing pages and marketing content: MAXIMIZE emotional impact and "wow factor". \
Design should make someone stop scrolling and say "whoa". Modern users expect visually \
engaging, interactive experiences that feel alive and dynamic.
- Default to contemporary cutting-edge design: dark modes, glassmorphism, micro-animations, \
3D elements, bold typography, vibrant gradients. Static designs are the EXCEPTION, not the rule.
- Include thoughtful animations on EVERYTHING: hover effects, scroll reveals, entrance \
transitions, pulsing accents, parallax, spring physics. Even subtle movements dramatically \
improve engagement.
- When faced with design decisions, lean BOLD and UNEXPECTED over safe and conventional: \
vibrant colors over muted, dynamic layouts over traditional grids, expressive typography \
over conservative, immersive effects over minimal.
- Push boundaries with advanced CSS (custom properties, clamp(), container queries, \
:has(), scroll-driven animations), complex keyframe animations, and creative JavaScript \
interactions. The goal is PREMIUM and CUTTING-EDGE.
- Complex interactive features (immersive scenes, Three.js if ever used): prioritize smooth \
frame rates, responsive controls, efficient rendering, stable interactions.
- Accessibility is NON-NEGOTIABLE: proper contrast, semantic markup, keyboard nav, ARIA \
labels, focus indicators — but make accessibility beautiful, not an afterthought.
- Create fully functional working implementations, not placeholders.

## Site Identity
- Brand: The Skyy Rose Collection
- URL: https://skyyrose.co
- Platform: WordPress.com Atomic (SSH/SFTP, custom PHP, full plugin access)
- Theme: skyyrose-flagship
- WooCommerce: Full integration (products, cart, checkout, payment)
- Tagline: "Oakland Luxury Streetwear"

## Marketplace-Ready Theme Requirements
This theme must be structured as a PROFESSIONAL commercial-grade WordPress theme:
- Complete theme.json for Full Site Editing (colors, fonts, spacing, layout presets)
- Proper functions.php with conditional asset loading per template
- Organized file structure: assets/css/, assets/js/, assets/images/, woocommerce/
- WordPress Customizer integration for brand colors and logo
- Child-theme compatible (no hardcoded paths)
- Translation-ready with __() and esc_html__() wrappers
- Screenshot.png (1200x900) showing the dark luxury design
- style.css header with theme metadata (name, version, author, description, tags)
- README.txt with setup instructions, requirements, changelog
- GPL-2.0+ license compatible

## Design System Requirements
- MANDATORY dark theme: #0A0A0A page background (NOT white), #111111 card backgrounds
- Glass morphism: rgba(17,17,17,0.95) with backdrop-filter: blur(20px) for panels
- Fonts: Hanken Grotesk (body/UI) + Archivo (display/headings) + Anton (UI caps) + Cinzel (engraved-caps accent); Inter = fallback only — self-hosted woff2 ONLY (assets/fonts/ + theme.json Font Library / assets/css/fonts.css; NO Google Fonts CDN, no @import, no preconnect)
  - Do NOT use Montserrat, Playfair Display, Cormorant Garamond, Bebas Neue, or system defaults
- Film grain SVG overlay at 3% opacity on ALL pages (luxury texture effect)
- Official collection colors (OWNER-CONFIRMED, do not change):
  - BLACK ROSE: Black #000000, White #FFFFFF, Metallic Silver #C0C0C0
  - LOVE HURTS: Red #FF0000, Crimson #DC143C, Black #000000, White #FFFFFF
  - SIGNATURE: Rose Gold #B76E79 (PRIMARY brand color), Gold #D4AF37
  - KIDS CAPSULE: Pink #FFB6C1, Lavender #E6E6FA
- CSS custom properties in :root for ALL design tokens (colors, fonts, spacing, transitions)
- Responsive breakpoints: 1200px (tablet landscape), 768px (tablet), 480px (mobile)
- Spacing scale: xs 0.5rem, sm 1rem, md 1.5rem, lg 2rem, xl 3rem, 2xl 4rem
- Transitions: smooth (0.3s ease), spring (0.6s cubic-bezier(0.16, 1, 0.3, 1))

## Pages to Build (9 from static HTML reference + 2 new)
Static HTML designs in wp-playground/SKyyRose Flagship/Flagship static/ are the CANONICAL \
design reference. Every PHP template must faithfully reproduce these designs.

1. front-page.php — Hero (100vh, floating orbs, gradient headline) + collections showcase \
(3 cards 600px tall) + featured products (4-card grid) + brand story (2-col) + newsletter
2. template-collection-black-rose.php — Floating roses animation, 8 products (br-001..008), \
gothic garden mood, metallic silver accent
3. template-collection-love-hurts.php — 15 floating hearts, 4 products (lh-002/003/004/005), \
passionate drama mood, crimson accent, pulsing collection badge
4. template-collection-signature.php — Art deco overlay, 14 products (sg-001..014), \
elevated luxury mood, rose gold accent, pulsing gold ring (600px)
5. template-collection-kids-capsule.php — Pink/lavender theme, 2 products (kids-001..002), \
playful rounded cards, joyful voice (NEW — no static reference, derive from other collections)
6. woocommerce/single-product.php — Sticky gallery (main + 4 thumbs) + product info panel \
+ color/size selectors + quantity + accordions (Details, Sizing, Shipping) + related 4-grid
7. template-about.php — Hero + story sections (alternating grid) + timeline (2019-2024) \
+ values (4 cards) + founder section
8. template-contact.php — Contact info + form (name, email, subject, message) + FAQ accordion (5)
9. woocommerce/cart/cart.php — Dark luxury cart with 150px item images + sticky order summary (400px)
10. woocommerce/checkout/form-checkout.php — 4-step progress (Cart > Info > Payment > Confirm) \
+ multi-step form + sticky order summary (420px)
11. 404.php — Dark bg, "404" in Archivo with gold gradient, collection quick links, CTA (NEW)

## Shared Components
- Header: Fixed dark navbar rgba(10,10,10,0.95) + blur(20px), SR Monogram logo (48px), \
gradient text "SKYY ROSE", nav links + icon buttons (search, account, cart with count badge), \
mobile hamburger slide-in from right
- Footer: 5-column grid (2fr 1fr 1fr 1fr 1fr) — Brand/Shop/Help/Legal/Social, \
newsletter signup bar, copyright, stacks to single column on mobile
- Product Card: #111 bg, 3:4 aspect image, hover: translateY(-8px) + shadow, \
quick actions overlay (wishlist, quickview, add-to-cart), name (Hanken Grotesk 600), \
price in collection accent color
- Toast Notifications: fixed bottom-right, slide-in, dark glass, auto-dismiss 3s

## drakerelated.com-Style Product Display & Immersive Scenes
The ENTIRE product browsing experience follows the drakerelated.com interaction pattern — \
Drake's official lifestyle site that uses room-based exploration with hotspot beacons.

### Immersive Pages (3 scenes — image-based, NOT Three.js/WebGL)
- template-immersive-black-rose.php — "The Garden": Gothic garden, wrought-iron racks, \
roses, cathedral backdrop, 5 products visible IN the scene on racks/mannequins/benches
- template-immersive-love-hurts.php — "The Ballroom": Baroque ballroom + candlelit manor \
(2 scene views), chandeliers, rose petals, 5 products on chairs/mannequins/pedestals
- template-immersive-signature.php — "The Runway" (MULTI-ROOM, 3 scenes): \
  Room 1 "The Runway" — Bay Bridge glass venue, garment racks, 5 products \
  Room 2 "The Showroom" — Grand hall, display cases, 5 products \
  Room 3 "The Fitting Room" — Intimate dressing area, mirrors, 4 beanies on stands/shelves \
  Arrow/swipe navigation between rooms with 0.6s crossfade transitions

### drakerelated.com Interaction Pattern (CRITICAL)
- Full-screen scene IMAGE as viewport backdrop (object-fit: cover, responsive)
- Products physically VISIBLE in the scene image (on racks, mannequins, furniture, shelves) — \
NOT abstract dots on a generic background
- Hotspot beacons: 32px pulsing circles with collection accent border, positioned via \
percentage-based coordinates (e.g., left: 34.2%; top: 48.7%) — responsive across all screens
- Hotspot click = DUAL action: (1) glassmorphism slide-up panel with product thumbnail, \
name, price, sizes, add-to-cart, (2) "View Details" link to collection or product page
- Hotspots are <a> tags wrapping beacons for SEO crawlability + keyboard navigation
- Room-to-room navigation arrows at screen edges (Signature has 3 rooms)
- Smooth crossfade transitions between scenes (not hard cuts)
- Minimal UI overlay — scene image is the star, UI is glass/transparent
- Vignette overlay: radial-gradient(ellipse at center, transparent 35%, rgba(2,0,4,0.8))
- Film grain + collection tab bar (fixed bottom) on all immersive pages

## Pre-Order Gateway Page
- template-preorder-gateway.php — Glassmorphism design, ultra-dark (#020004) background
- Loading screen with SR Monogram (breathe animation) + progress bar
- Collection tabs: All | Black Rose | Love Hurts | Signature (fixed bottom, accent per tab)
- Product grid: auto-fill minmax(180px, 1fr)
- Product modal: 360° preview area, sizes, add-to-cart + wishlist
- Cart sidebar: slide-in from right (400px), items list, total, checkout button
- Sign-in panel: slide-in from right (420px), email/password, member perks list
- Exclusive member banner with early access CTA

## AI Fashion Model Photography Integration
ALL product images are AI-generated fashion model photos showing real models wearing the \
EXACT SkyyRose products with correct branding techniques (embroidered, silicone, printed, etc.)

### Image Pipeline
- Generated via: Gemini 2.5 Flash Image (primary), DALL-E 3 (fallback)
- Output structure: products/{sku}/{sku}-model-{view}.jpg (front + back per product)
- 204+ fashion model photos across 28 SKU folders (ALREADY GENERATED)
- Each image verified by dual AI vision (Claude Sonnet + Gemini Flash) for logo accuracy
- Branding techniques ML-verified per product (28 override files with logoFingerprint)

### WordPress Image Embedding (MANDATORY pattern)
```php
<picture>
  <source srcset="products/{sku}/{sku}-model-front.webp" type="image/webp">
  <img src="products/{sku}/{sku}-model-front.jpg"
       alt="{Product Name} — Model wearing {garment type}"
       width="1024" height="1536" loading="lazy" class="product-image">
</picture>
```
- All images: WebP primary + JPEG fallback via <picture> element
- Responsive srcset: 480px, 768px, 1024px, 2048px sizes
- Alt text format: "{Canonical Product Name} — Model wearing {garment type}"
- Lazy loading on all images below the fold

### Where AI Model Photos Appear
| Image Type | Template | Placement |
|-----------|----------|-----------|
| Fashion model (front) | Collection landing pages, product hero, lookbook grid | Primary product image |
| Fashion model (back) | Single product thumbnails, lookbook secondary | Hover/alternate view |
| Scene backgrounds | Immersive pages | Full-screen backdrop with hotspots |
| Collection logos | Hero sections, header, footer, watermarks | Brand identity |
| Ad creatives | Homepage hero, marketing banners | Promotional sections |

## Technical Requirements
- WordPress PHP templates with proper hooks (wp_enqueue_scripts, wp_head, wp_footer)
- WooCommerce template overrides in woocommerce/ subdirectory
- Functions.php with conditional asset loading per template (immersive CSS/JS only on immersive pages)
- theme.json for Full Site Editing support (colors, fonts, spacing, layout)
- WCAG 2.2 AA accessibility: 4.5:1 contrast ratios, keyboard navigation, ARIA landmarks, \
skip-to-content link, focus indicators, alt text on all images, form labels
- Lighthouse > 80 mobile: critical CSS inlined, images lazy-loaded, WebP with JPEG fallback, \
deferred non-critical JS, font-display: swap
- SEO: schema.org Product markup (name, price, image, availability), meta tags, Open Graph, \
Twitter Cards, canonical URLs, structured breadcrumbs
- Security: CSP headers, XML-RPC disabled, no inline scripts where possible, input sanitization, \
nonce verification on forms, esc_html/esc_attr on all output

## Logo Assets (already optimized in branding/optimized/)
- SR Monogram: header (48px), footer (64px), loading screen (120px breathe animation), favicon set (16-512px)
- Collection logos: collection hero sections, immersive page watermarks (bottom-right, 8% opacity)
- 5 sizes: favicon (64px), icon (200px), nav (400px), hero (1024px), og (1200px)
- Dual format: PNG (transparency) + WebP (performance)
- Logo placement map: header=SR Monogram, footer=SR Monogram + text, favicon=SR Monogram, \
collection hero=collection-specific logo centered above heading, product cards=NO logo

## Products — canonical sources
Resolve every product reference — SKU, name, collection, price, pre-order \
flag, image filename, dossier slug — through ONE OF:
  - `wordpress-theme/skyyrose-flagship/data/skyyrose-catalog.csv` (the catalog)
  - `wordpress-theme/skyyrose-flagship/data/dossiers/{slug}.md` (per-SKU spec)
Read via `core/ground_truth.py` at story generation time. Never inline a \
product list in this PRD — caused drift on retired SKUs (sg-004, lh-001) \
historically. 32 SKUs across four collections (Black Rose, Love Hurts, \
Signature, Kids Capsule); collection-level scope decisions can use those \
four labels without consulting the catalog.
"""


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


async def run(prd_text: str, dry_run: bool = False) -> None:
    """Execute the Elite Web Builder pipeline."""

    print("")
    print("  ╔══════════════════════════════════════════╗")
    print("  ║   ELITE WEB BUILDER — Agent Team Deploy  ║")
    print("  ╠══════════════════════════════════════════╣")
    print(f"  ║   Mode:   {'DRY RUN (plan only)' if dry_run else 'LIVE EXECUTION':<32}║")
    print("  ║   Agents: 7 specialists + Director      ║")
    print("  ║   Keys:   3/3 verified                  ║")
    print("  ╚══════════════════════════════════════════╝")
    print("")

    # Initialize Director
    logger.info("Initializing Director with default routing...")
    director = Director.from_config()

    if dry_run:
        # Planning only — decompose PRD into stories but don't execute
        logger.info("DRY RUN: Planning stories only (no LLM calls for execution)")
        logger.info("PRD length: %d chars", len(prd_text))
        print("\n  PRD Preview (first 500 chars):\n")
        for line in prd_text[:500].split("\n"):
            print(f"    {line}")
        print(f"\n    ... ({len(prd_text) - 500} more chars)\n")
        print("  To run live: .venv/bin/python run.py\n")
        return

    # Full execution
    logger.info("Starting PRD execution...")
    logger.info("PRD length: %d chars", len(prd_text))

    start = time.time()
    report = await director.execute_prd(prd_text)
    elapsed = time.time() - start

    # Report results
    print("")
    print("  ╔══════════════════════════════════════════╗")
    print("  ║          EXECUTION REPORT                ║")
    print("  ╠══════════════════════════════════════════╣")
    print(f"  ║   All Green:  {'YES' if report.all_green else 'NO':<28}║")
    print(f"  ║   Stories:    {len(report.stories):<28}║")
    print(f"  ║   Elapsed:    {elapsed:.1f}s{'':<24}║")
    print(f"  ║   Instincts:  {report.instincts_learned:<28}║")
    print("  ╚══════════════════════════════════════════╝")
    print("")

    if report.status_summary:
        print("  Status Breakdown:")
        for status, count in sorted(report.status_summary.items()):
            icon = "✅" if status == "green" else "❌" if status == "failed" else "⏳"
            print(f"    {icon} {status}: {count}")
        print("")

    if report.failures:
        print("  Failures:")
        for failure in report.failures:
            print(f"    ❌ {failure}")
        print("")

    # Print story details
    if report.stories:
        print("  Stories:")
        for sid, story in sorted(report.stories.items()):
            status_icon = {
                "green": "✅",
                "failed": "❌",
                "pending": "⏳",
            }.get(story.status.value, "❓")
            print(f"    {status_icon} {sid}: {story.title} [{story.agent_role.value}]")
        print("")

    # Save report to disk
    output_dir = ROOT / "output"
    output_dir.mkdir(parents=True, exist_ok=True)

    # 1. Summary report (status only — lightweight)
    report_path = output_dir / "last_report.json"
    report_data = {
        "all_green": report.all_green,
        "elapsed_ms": report.elapsed_ms,
        "failures": report.failures,
        "instincts_learned": report.instincts_learned,
        "story_count": len(report.stories),
        "status_summary": report.status_summary,
        "stories": {
            sid: {
                "title": s.title,
                "status": s.status.value,
                "agent_role": s.agent_role.value,
            }
            for sid, s in report.stories.items()
        },
    }
    report_path.write_text(json.dumps(report_data, indent=2))
    logger.info("Report saved to %s", report_path)

    # 2. Save each story's generated content to individual files
    stories_dir = output_dir / "stories"
    stories_dir.mkdir(parents=True, exist_ok=True)
    saved_count = 0

    for sid, story in sorted(report.stories.items()):
        story_data: dict[str, Any] = {
            "id": sid,
            "title": story.title,
            "description": story.description,
            "agent_role": story.agent_role.value,
            "status": story.status.value,
            "depends_on": story.depends_on,
            "acceptance_criteria": story.acceptance_criteria,
        }

        if story.output is not None:
            story_data["output"] = {
                "agent": story.output.agent,
                "content": story.output.content,
                "files_changed": list(story.output.files_changed),
                "metadata": story.output.metadata,
            }
            saved_count += 1
        else:
            story_data["output"] = None

        story_path = stories_dir / f"{sid}.json"
        story_path.write_text(json.dumps(story_data, indent=2, ensure_ascii=False))

    logger.info(
        "Saved %d/%d story outputs to %s",
        saved_count,
        len(report.stories),
        stories_dir,
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Elite Web Builder — deploy the agent team",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Planning only — preview the PRD without executing agents",
    )
    parser.add_argument(
        "--prd",
        type=str,
        default=None,
        help="Path to custom PRD file (default: built-in SkyyRose PRD)",
    )
    args = parser.parse_args()

    # Load PRD
    if args.prd:
        prd_path = Path(args.prd)
        if not prd_path.exists():
            print(f"  PRD file not found: {prd_path}")
            sys.exit(1)
        prd_text = prd_path.read_text()
    else:
        prd_text = DEFAULT_PRD

    asyncio.run(run(prd_text, dry_run=args.dry_run))


if __name__ == "__main__":
    main()
