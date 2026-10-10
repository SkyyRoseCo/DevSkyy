"""
Custom MCP Tools for the Multi-Agent System.

These tools give Claude agents access to SkyyRose-specific operations:
product catalog, theme files, brand voice, and the Elite Studio pipeline.

Each tool is decorated with @tool and registered as an SDK MCP server.
"""

from __future__ import annotations

import json
from typing import Any

from claude_agent_sdk import create_sdk_mcp_server, tool

from .config import ASSETS_DIR, PRODUCT_DATA_DIR, REPO_DIR, THEME_DIR

# ---------------------------------------------------------------------------
# Product Catalog Tools
# ---------------------------------------------------------------------------


@tool(
    "get_product_catalog",
    "Get the full SkyyRose product catalog with pricing, collections, and SKUs",
    {"collection": str},
)
async def get_product_catalog(args: dict[str, Any]) -> dict[str, Any]:
    """Load the canonical SkyyRose product catalog.

    Resolves through ``skyyrose.core.catalog_loader.read_catalog_rows``, which
    reads ``wordpress-theme/skyyrose-flagship/data/skyyrose-catalog.csv`` — the
    only authoritative product data source. Other product-data files were
    retired 2026-04-19 / 2026-04-25 / 2026-05-27 and are not consulted.
    """
    from skyyrose.core.catalog_loader import read_catalog_rows

    collection = args.get("collection", "all")
    products = list(read_catalog_rows())

    if collection != "all":
        products = [
            p for p in products if (p.get("collection") or "").lower() == collection.lower()
        ]

    return _text(json.dumps(products, indent=2, default=str))


@tool(
    "get_product_overrides",
    "Get the per-SKU canonical dossier (branding + garment-type-lock spec) for a product",
    {"sku": str},
)
async def get_product_overrides(args: dict[str, Any]) -> dict[str, Any]:
    """Load the canonical dossier for a SKU.

    Per the canonical-sources-only rule (locked 2026-05-27), product spec
    overrides live in ``data/dossiers/{slug}.md`` — Corey-authored garment
    specs — NOT the retired ``prompts/overrides/{sku}.json`` store. The tool
    name is kept for back-compat with existing agent prompts; behavior is
    redirected to the dossier loader.
    """
    from skyyrose.core.dossier_loader import get_product_with_dossier

    sku = args["sku"].strip().lower()
    try:
        result = get_product_with_dossier(sku)
    except Exception as exc:  # noqa: BLE001 — surface any loader error to the agent
        return _text(f"Dossier load failed for SKU {sku!r}: {exc}")

    if result is None:
        return _text(f"No dossier found for SKU: {sku}")

    return _text(json.dumps(result, indent=2, default=str))


@tool(
    "list_product_images",
    "List all generated/source images for a product SKU",
    {"sku": str},
)
async def list_product_images(args: dict[str, Any]) -> dict[str, Any]:
    """List product images across all directories."""
    sku = args["sku"].strip().lower()
    results: list[str] = []

    search_dirs = [
        REPO_DIR / "skyyrose" / "assets" / "images" / "products" / sku,
        REPO_DIR / "assets" / "products" / "source-photos",
        THEME_DIR / "assets" / "images" / "products",
    ]

    for d in search_dirs:
        if d.is_dir():
            for f in sorted(d.iterdir()):
                if f.suffix.lower() in {".jpg", ".jpeg", ".png", ".webp"}:
                    if sku in f.stem.lower():
                        results.append(str(f.relative_to(REPO_DIR)))

    if not results:
        return _text(f"No images found for SKU: {sku}")

    return _text("\n".join(results))


# ---------------------------------------------------------------------------
# Theme Audit Tools
# ---------------------------------------------------------------------------


@tool(
    "list_theme_templates",
    "List all WordPress theme PHP templates with their purpose",
    {},
)
async def list_theme_templates(args: dict[str, Any]) -> dict[str, Any]:
    """Discover all PHP templates in the theme."""
    templates: list[dict[str, str]] = []

    for php_file in sorted(THEME_DIR.rglob("*.php")):
        rel = str(php_file.relative_to(THEME_DIR))
        # Read first 5 lines for docblock
        lines = php_file.read_text(errors="replace").split("\n")[:5]
        header = " ".join(lines).strip()[:200]
        templates.append({"file": rel, "header": header})

    return _text(json.dumps(templates, indent=2))


@tool(
    "get_theme_css_stats",
    "Get CSS file statistics — sizes, line counts, minified status",
    {},
)
async def get_theme_css_stats(args: dict[str, Any]) -> dict[str, Any]:
    """Analyze CSS files in the theme."""
    css_dir = ASSETS_DIR / "css"
    stats: list[dict[str, Any]] = []

    for css_file in sorted(css_dir.glob("*.css")):
        if css_file.name.endswith(".min.css"):
            continue
        content = css_file.read_text(errors="replace")
        min_file = css_dir / css_file.name.replace(".css", ".min.css")
        stats.append(
            {
                "file": css_file.name,
                "lines": content.count("\n") + 1,
                "size_kb": round(css_file.stat().st_size / 1024, 1),
                "has_minified": min_file.exists(),
                "min_size_kb": (
                    round(min_file.stat().st_size / 1024, 1) if min_file.exists() else None
                ),
            }
        )

    return _text(json.dumps(stats, indent=2))


@tool(
    "check_font_loading",
    "Verify self-hosted font configuration — no external Google Fonts requests",
    {},
)
async def check_font_loading(args: dict[str, Any]) -> dict[str, Any]:
    """Audit font loading for GDPR compliance."""
    issues: list[str] = []

    # Check for external Google Fonts references
    for php_file in THEME_DIR.rglob("*.php"):
        content = php_file.read_text(errors="replace")
        if "fonts.googleapis.com" in content or "fonts.gstatic.com" in content:
            rel = str(php_file.relative_to(THEME_DIR))
            issues.append(f"GDPR VIOLATION: {rel} references external Google Fonts")

    for css_file in (ASSETS_DIR / "css").glob("*.css"):
        if css_file.name.endswith(".min.css"):
            continue
        content = css_file.read_text(errors="replace")
        if "fonts.googleapis.com" in content:
            issues.append(f"GDPR VIOLATION: {css_file.name} references external Google Fonts")

    # Check font files exist
    fonts_dir = ASSETS_DIR / "fonts"
    font_files = list(fonts_dir.glob("*.woff2")) if fonts_dir.exists() else []

    # Check @font-face declarations
    fonts_css = ASSETS_DIR / "css" / "fonts.css"
    font_face_count = 0
    if fonts_css.exists():
        font_face_count = fonts_css.read_text().count("@font-face")

    result = {
        "gdpr_compliant": len(issues) == 0,
        "issues": issues,
        "self_hosted_fonts": len(font_files),
        "font_face_declarations": font_face_count,
        "font_files": [f.name for f in font_files],
    }

    return _text(json.dumps(result, indent=2))


# ---------------------------------------------------------------------------
# Brand Voice Tools
# ---------------------------------------------------------------------------


@tool(
    "get_brand_guidelines",
    "Get SkyyRose brand voice guidelines, colors, and identity rules",
    {},
)
async def get_brand_guidelines(args: dict[str, Any]) -> dict[str, Any]:
    """Return canonical brand guidelines."""
    guidelines = {
        "brand": "SkyyRose",
        "tagline": "",
        "retired_taglines": ["Where Love Meets Luxury"],
        "founder": "Corey Foster",
        "colors": {
            "rose_gold": "#B76E79",
            "dark": "#0A0A0A",
            "silver": "#C0C0C0",
            "crimson": "#DC143C",
            "gold": "#D4AF37",
            "white": "#FFFFFF",
        },
        "typography": {
            "display": "Archivo",
            "body": "Hanken Grotesk",
            "mono": "SF Mono",
            "cta": "Anton",
            "accent": "Cinzel",
        },
        "collections": {
            "black_rose": {
                "aesthetic": "Gothic luxury, dark florals, power",
                "mood": "Rebellious elegance",
            },
            "love_hurts": {
                "aesthetic": "Passionate, romantic, bold",
                "mood": "Emotional intensity",
            },
            "signature": {
                "aesthetic": "Bay Area pride, streetwear meets high fashion",
                "mood": "Cultural authenticity",
            },
        },
        "voice": {
            "tone": "Confident, aspirational, authentic",
            "never_use": ["cheap", "discount", "basic", "affordable"],
            "always_convey": ["luxury", "craftsmanship", "identity", "culture"],
        },
    }
    return _text(json.dumps(guidelines, indent=2))


@tool(
    "generate_product_copy",
    "Generate brand-voice product description for a SKU",
    {"sku": str, "style": str},
)
async def generate_product_copy(args: dict[str, Any]) -> dict[str, Any]:
    """Generate product copy placeholder — the subagent will use its LLM for actual copy."""
    sku = args["sku"]
    style = args.get("style", "editorial")

    # Load product data
    override_path = PRODUCT_DATA_DIR / "prompts" / "overrides" / f"{sku}.json"
    product_info = {}
    if override_path.exists():
        product_info = json.loads(override_path.read_text())

    return _text(
        json.dumps(
            {
                "sku": sku,
                "style": style,
                "product_data": product_info,
                "instruction": (
                    "Use the brand guidelines and product data to write copy. "
                    f"Style: {style}. Voice: luxury, authentic, aspirational."
                ),
            },
            indent=2,
        )
    )


# ---------------------------------------------------------------------------
# Elite Studio Pipeline Tools
# ---------------------------------------------------------------------------


@tool(
    "elite_studio_status",
    "Check Elite Studio production status — which products have been generated",
    {},
)
async def elite_studio_status(args: dict[str, Any]) -> dict[str, Any]:
    """Check which products have generated images."""
    from ..elite_studio.config import OUTPUT_DIR
    from ..elite_studio.utils import discover_all_skus

    all_skus = discover_all_skus()
    generated = []
    missing = []

    for sku in all_skus:
        output = OUTPUT_DIR / sku / f"{sku}-model-front-gemini.jpg"
        if output.exists():
            generated.append(sku)
        else:
            missing.append(sku)

    return _text(
        json.dumps(
            {
                "total": len(all_skus),
                "generated": len(generated),
                "missing": len(missing),
                "generated_skus": generated,
                "missing_skus": missing,
            },
            indent=2,
        )
    )


@tool(
    "elite_studio_produce",
    "Run Elite Studio production pipeline for a single product SKU",
    {"sku": str, "view": str},
)
async def elite_studio_produce(args: dict[str, Any]) -> dict[str, Any]:
    """Run the full Elite Studio pipeline for one product."""
    from ..elite_studio.coordinator import Coordinator, NullLogger

    sku = args["sku"].strip().lower()
    view = args.get("view", "front")

    coord = Coordinator(logger=NullLogger())
    result = coord.produce(sku, view)

    return _text(
        json.dumps(
            {
                "sku": result.sku,
                "view": result.view,
                "status": result.status,
                "output_path": result.output_path,
                "error": result.error,
                "step": result.step,
                "vision_providers": list(result.vision.providers_used) if result.vision else [],
                "qc_status": result.quality.overall_status if result.quality else None,
                "qc_recommendation": result.quality.recommendation if result.quality else None,
            },
            indent=2,
        )
    )


# ---------------------------------------------------------------------------
# Deployment Tools
# ---------------------------------------------------------------------------


@tool(
    "check_vercel_status",
    "Check Vercel deployment status for the frontend",
    {},
)
async def check_vercel_status(args: dict[str, Any]) -> dict[str, Any]:
    """Check current Vercel deployment status."""
    import subprocess

    try:
        result = subprocess.run(
            ["vercel", "ls", "--json", "--limit", "3"],
            capture_output=True,
            text=True,
            timeout=30,
            cwd=str(REPO_DIR),
        )
        return _text(result.stdout or result.stderr)
    except FileNotFoundError:
        return _text("Vercel CLI not installed. Install with: npm i -g vercel")
    except subprocess.TimeoutExpired:
        return _text("Vercel command timed out")


@tool(
    "git_status_summary",
    "Get a summary of git status — changed files, branch, last commit",
    {},
)
async def git_status_summary(args: dict[str, Any]) -> dict[str, Any]:
    """Get git status summary."""
    import subprocess

    results: dict[str, str] = {}

    for cmd_name, cmd in [
        ("branch", ["git", "branch", "--show-current"]),
        ("status", ["git", "status", "--short"]),
        ("last_commit", ["git", "log", "--oneline", "-5"]),
    ]:
        try:
            r = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=10,
                cwd=str(REPO_DIR),
            )
            results[cmd_name] = r.stdout.strip()
        except Exception as e:
            results[cmd_name] = f"Error: {e}"

    return _text(json.dumps(results, indent=2))


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _text(content: str) -> dict[str, Any]:
    """Wrap text in MCP tool result format."""
    return {"content": [{"type": "text", "text": content}]}


# ---------------------------------------------------------------------------
# Tool Registry
# ---------------------------------------------------------------------------

CUSTOM_TOOLS = [
    get_product_catalog,
    get_product_overrides,
    list_product_images,
    list_theme_templates,
    get_theme_css_stats,
    check_font_loading,
    get_brand_guidelines,
    generate_product_copy,
    elite_studio_status,
    elite_studio_produce,
    check_vercel_status,
    git_status_summary,
]

# Create the SDK MCP server from all tools
skyyrose_mcp_server = create_sdk_mcp_server(
    name="skyyrose-tools",
    version="1.0.0",
    tools=CUSTOM_TOOLS,
)
