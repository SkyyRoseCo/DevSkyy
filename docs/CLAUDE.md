# DevSkyy docs/ — Canonical Index for AI Agents

When working on **anything visual, brand-touching, or collection-specific**, read these FIRST before generating any code, mockup, copy, or design proposal. They are locked canon. Conflicts with these docs = bugs.

## Brand canon (read before all design / visual / copy work)

| Doc | What it locks | When to read |
|-----|---------------|--------------|
| `docs/brand/visual-references.md` | The Five canonical visual references (Kith / Oaklandish / Culture Kings / Fear of God / Palm Angels) + the locked-out European-luxury-house lineage | Any aesthetic, mockup, design proposal, brand pitch, agent visual brief |
| `docs/brand/collection-stories.md` | Per-collection canon: Black Rose / Love Hurts / Signature / Kids Capsule — origin, voice, mood, founder-locked taglines | Any copy, any collection page, any product description |
| `wordpress-theme/skyyrose-flagship/data/collections/<slug>/identity.json` | **Per-collection identity SOT (canon seed):** palette (named hex), fonts {script,caps,body}, story seed, lockup. `design-tokens.css`, `sot.json`, `index.html` are GENERATED from it. Edit identity.json, never the generated files. | Any collection palette/font/identity work. See `data/collections/README.md` |
| `docs/brand/corey-questions.md` + `docs/brand/canon-audit-2026-05-23.md` | Founder voice locks (verbatim) + canon audit history | Voice-frame copy, founder-quote attribution |
| `docs/brand/asset-hierarchy.md` | 3-tier brand asset map; brand-primary monogram = `sr-monogram-rose-gold` | Any brand-mark placement decision |

## Active specs (in-flight or just-locked work)

| Spec | Status | Scope |
|------|--------|-------|
| `docs/superpowers/specs/2026-05-25-v2-mockup-design.md` | Spec retained; mockup ERASED 2026-06-10 | v2 design ref `docs/brand/design-mockups/v2.html` deleted by founder (wrong/pre-OAI imagery). Spec survives as composition reference — magazine-as-site, 4 frames (Cover / Hero / Voice / Spread) |
| `docs/superpowers/specs/2026-05-25-footer-logo-swap.md` | Locked + committed 2026-05-25 | Single-file edit: footer monogram swap to canonical branding tier |

## Locked rules (do not break)

These come from `~/.claude/projects/-Users-theceo-DevSkyy/memory/` and apply to every agent / session:

1. **Hero titles = collection lockup IMAGES, never type-rendered.** Each collection has a canonical brand-script lockup in `assets/images/hero-overlays/` (BR/LH/SIG) or `assets/images/logos/` (Kids). Fonts (per `data/brand/typography.json` + per-collection `identity.json` — Italiana/Yellowtail retired 2026-07-10) apply only to interior surfaces.
2. **Each collection has its own canon — never mix quotes.** "Hurts is the bloodline that raised me" = Love Hurts ONLY. Black Rose canon = armor / "you already stood up" / "concrete answering back". Never substitute one collection's voice for another.
3. **Always reference The Five.** Kith / Oaklandish / Culture Kings / Fear of God / Palm Angels. Never Bottega / Numéro / Hedi Slimane / Rick Owens / 032c / Acne FW24 / Givenchy by Tisci / Khaite / Bode / The Row — those are locked OUT.
4. **One product registry is the source of truth.** `logo-registry.json` at the repo root (a symlink to `wordpress-theme/skyyrose-flagship/data/logo-registry.json`) is the ONE editable product SOT. Its `products[sku]` records own commerce fields, garment color, sizes and sizing references, fit, materials, features, the design specification, and image/source bindings; its logo/placement sections own graphics and decoration dimensions. `skyyrose-catalog.csv`, the per-SKU dossiers, `sot-images.json`, `inc/product-catalog.php`, and every generated manifest are projections or consumers — never author a product fact in them. Read through ONE entry point — `from skyyrose.core.product import get_product` — which returns the complete record for a SKU in a single call and names anything absent in its `gaps` list (`python -m skyyrose.core.product <sku>` for non-Python callers); the narrow readers (`product_registry`, `catalog_loader`, `dossier_loader`, `sot_images`, `LogoRegistry`) remain for single-field needs. Write catalog fields through the registry update API, then run `python scripts/sync_product_registry.py` (`--check` before handoff). Corey's corrections land in the registry first and are recorded as `FOUNDER_CONFIRMED`. Never reference retired SKUs or invent SKUs.
5. **No mock data in production code.** Even in spec docs, name real verified files and paths only.
6. **Product imagery resolves through the SOT only.** The registry's `products[sku]` owns the image/source bindings; every surface (WP, dashboard, MCP, pipelines, agents, skills, plugins) resolves a SKU's image through `skyyrose.core.sot_images.resolve_image()` (whose `data/sot-images.json` manifest is a generated projection of those bindings) — front-first (on-model render before flat packshot), never a hardcoded `assets/images/products/...` literal or a `/images/scenes/*` fabrication. Policy + backlog: `docs/brand/sot-imagery-policy.md`. Guard: `tests/test_sot_no_adhoc_imagery.py`.

## Folder index

| Folder | Purpose |
|--------|---------|
| `docs/brand/` | Brand canon (read these first for any creative work) |
| `docs/superpowers/specs/` | Active design specs (read before invoking writing-plans for related work) |
| `docs/brand/design-mockups/` | Output target for design refs |
| `docs/SKYYROSE_WORDPRESS_PLAN.md` | High-level WordPress development plan (references canon docs above) |

## Conflict policy

If a doc anywhere in this folder conflicts with the canon docs above, **the canon doc wins**. Update the conflicting doc to reference the canon. Do not edit the canon without founder sign-off. New canon decisions get appended to the relevant `docs/brand/*.md` file with a date stamp + founder-locked note.
