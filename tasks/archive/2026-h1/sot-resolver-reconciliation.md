# SOT-First Product Image Resolver — Build + Reconciliation

**Built 2026-06-30. Source-only; deploy STOP-AND-SHOW gated.**

## What was built
1. **Runtime resolver** — `skyyrose_sot_product_image( $sku, $view )` + `skyyrose_sot_product_image_uri()`
   in `inc/collection-sot-reader.php`. Reads the deployed per-collection `data/collections/<slug>/sot.json`
   (front-first: front_model_image → image), falls back to catalog CSV columns, then placeholder.
   Reuses the existing cached loader `skyyrose_get_collection_sot()`.
2. **11 tiles converted** — `front-page.php` (7 refs) + `template-landing-kids-capsule.php` (4 refs) now
   call the resolver by SKU+view. Zero `/images/products/...` literals remain.
3. **Gate** — `check_no_hardcoded_product_images` in `scripts/validate_catalog_consistency.py` fails the
   build if any template hardcodes an `/images/products/...` path. "SOT seen before everything," enforced.

## Verification (all ran 2026-06-30)
- Resolver runtime harness: **8/8** SKU+view → correct SOT path (real catalog + real sot.json).
- php -l + PHPCS: clean on resolver + both templates.
- Validator: **17/17** checks pass; new gate **proven can-fail** (flags a violation, ignores the resolver call).
- black + ruff clean; 6 catalog tests pass (no regression).
- Eyes-on (pixels) all 6 new SOT images = correct garment for SKU+collection.

## Reconciliation — what each tile renders now vs. after
| Tile (SKU) | Was (hardcoded) | Now (SOT front) | Verdict |
|---|---|---|---|
| br-006 ×3 | sherpa packshot 1024² 59KB | br-006-onmodel 1024×1536 240KB | **ADOPT** — on-model upgrade, correct garment |
| lh-004 ×2 | varsity 896×1200 103KB | lh-004-onmodel 1024×1536 298KB | **ADOPT** — same varsity-bomber, on-model |
| sg-009 | sherpa packshot 1024² 60KB | sg-009-onmodel 1024×1536 223KB | **ADOPT** — on-model upgrade |
| sg-006 | hoodie packshot 1024² 60KB | sg-006-onmodel 1024×1536 203KB | **ADOPT** — on-model upgrade |
| kids-001 front | red-set on-model 896×1200 83KB | kids-001-onmodel 1024×1536 152KB | **ADOPT** — on-model, correct |
| kids-001 back | red-set-back | (same) | no change |
| kids-002 back | purple-set-back | (same) | no change |
| **kids-002 front** | purple-set on-model 896×1200 142KB | **ghost-mannequin** 1024² 60KB | **KEEP** — founder-verified, see below |

## kids-002 front — resolved (founder verdict, not a gap)
- `assets/hub/manifest.json` records **`kids-002-front`** (usage `product-card`) as `verdict: "verified"`,
  `verified_by: "founder verdict 2026-06-25"`, source = the ghost-mannequin render.
- A separate hub entry, **`kids-002-front-product-card-alt`**, independently verifies a Gemini-upscaled
  on-model shot for the distinct `product-card-alt` usage slot — so the on-model image isn't unused,
  it's verified for a different surface.
- I initially read the ghost as "likely a leftover" from pixels + catalog precedence alone, recommended
  repointing the catalog `front_model_image` to the on-model shot, and executed it (CSV edit + regen of
  both `sot.json` and `sot-images.json`). That contradicted the recorded founder verdict. Caught before
  any further action; reverted in full (CSV + both regenerated artifacts confirmed byte-identical to the
  founder-verified state via `git diff --stat` = empty). No deploy occurred at any point.
- **Lesson:** the asset hub (`assets/hub/manifest.json`) is the highest-authority source for which image
  is correct per usage slot — check it before any image-swap recommendation, not just CSV/sot-images.json/
  pixels. Logged in `tasks/lessons.md` and `.wolf/cerebrum.md`.

## Deploy gate
Source-only. The 6-file resolver build (`56e636c0e` on `feat/sot-image-resolver`) is unaffected by the
kids-002 episode — it never touched catalog data, only template wiring. Going live needs
`deploy-theme.sh` → skyyrose.co (STOP-AND-SHOW), then post-verify (curl 200 + Playwright mobile/desktop).
