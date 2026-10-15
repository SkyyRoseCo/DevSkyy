# Catalog reconciliation — first pass

This is a derived audit snapshot, not an editable product fact store. Product authority remains `wordpress-theme/skyyrose-flagship/data/logo-registry.json`; read products through `get_product`. Founder facts and exact corrections remain authoritative. No founder specification was changed or newly inferred. Offline workflow; authentication not applicable. No generation, spend, publishing, or live WooCommerce audit.

## Completed

- Read all 33 complete product records; inspected every populated fit/materials field and searched all 25 originally empty-fit dossiers for explicit fit language.
- Reviewed all 33 storefront front/back assignments in six contact sheets. This is overview triage, not full-resolution fidelity approval. Missing slots remain visible in the sheets.
- Inspected 14 existing rear-reference candidates and selected fallback images. Filename matches were not promoted to authority.
- Replaced artwork/lining text incorrectly stored as fit for br-010 and lh-004 with null. The original wording remains in the unchanged dossiers and the before/after audit.
- Cleared wrong rear bindings for lh-002 (white pants assigned to black SKU), sg-005 (isolated artwork), and sg-015 (front view).
- Cleared sg-011's incorrect hub rear assignment, revealing its existing back packshot through the explicit fallback chain. This is not a new on-model back asset.
- Regenerated both CSV projections, collection SOTs, lookbook SOT, and the SOT imagery manifest. Preserved all original image files.

## Source issues that remain

The registry already records unresolved Signature beanie variant/technique reconciliation and exact secondary SR artwork binding (sg-002, sg-005, sg-015). The bridge front-source issue is resolved only for fronts. These issues are retained in inventory.json; none was silently marked resolved.

The Windbreaker has an existing full front/back design plate and separate component crops. They are useful candidates, but component crops alone do not represent this two-piece SKU. The separate SR artwork issue remains. No front/back render binding was added merely to eliminate the gap.

A candidate named lh-001-fannie-pack-techflat-back.jpeg visibly shows front decoration and is unsuitable as proof of the undecorated back. Several bridge shorts candidates carry front details despite a back filename. These examples demonstrate why filenames cannot authorize bindings.

Further review queue from the overview: sg-001 and sg-003 rear assignments show apparent front details; sg-007 rear image shows the decorated face; sg-009 rear slot shows an open jacket/lining; lh-004 rear slot is a composite. Verify these at full resolution against their existing authority before changing them. These are triage observations, not new founder facts or acceptance judgments.

Most missing fit statements cannot be recovered through a fit-keyword search of the current dossier. Phrases such as relaxed arms/hood are pose instructions, not fit. lh-005 has an adjustable strap statement, but no garment-fit value was invented for the accessory. All 33 garment-size-chart bindings remain absent; a filename search within assets/products found no explicitly named sizing chart, which is not proof none exists elsewhere.

## Remaining counts after honest corrections

- Fit specification absent: 27 products (previously 25; two misleading values exposed).
- Render front/back bindings missing: 16 across 15 products, unchanged.
- Storefront back role absent: 6 products (previously 3); sg-011 additionally uses an explicit back-packshot fallback.
- Back packshot absent: 17 products (previously 16).
- Editorial enrichment and alt-text maps: unchanged; all 33 need that separate pass.

## Per-product work queue

Every row is derived from the current registry snapshot. Full paths, file hashes, gaps, original values, and reasons are in inventory.json. A bound image means a file is assigned, not approved.

| SKU | Missing fit | Missing render views | Missing storefront roles |
|---|---|---|---|
| br-001 | No | None | back_packshot |
| br-002 | No | None | None |
| br-003 | Yes | None | None |
| br-004 | Yes | back | None |
| br-005 | Yes | back | None |
| br-006 | Yes | None | None |
| br-007 | Yes | None | None |
| br-008 | Yes | None | back, back_packshot |
| br-009 | Yes | None | back, back_packshot |
| br-010 | Yes | None | back, back_packshot |
| br-011 | Yes | None | None |
| br-012 | Yes | None | None |
| br-014 | Yes | None | back_packshot |
| br-015 | Yes | None | back_packshot |
| kids-001 | Yes | None | back_packshot |
| kids-002 | Yes | None | back_packshot |
| lh-002 | No | back | back, back_packshot |
| lh-003 | Yes | None | None |
| lh-004 | Yes | None | None |
| lh-005 | Yes | back | back_packshot |
| lh-006 | No | back | None |
| sg-001 | Yes | back | None |
| sg-002 | Yes | back | back_packshot |
| sg-003 | Yes | back | back_packshot |
| sg-005 | Yes | back | back, back_packshot |
| sg-006 | Yes | back | None |
| sg-007 | No | back | back_packshot |
| sg-009 | Yes | back | None |
| sg-011 | Yes | back | None |
| sg-012 | Yes | back | None |
| sg-013 | Yes | None | back_packshot |
| sg-014 | No | None | back_packshot |
| sg-015 | Yes | front, back | back, back_packshot |

## Verification

- 46 focused tests passed: dossier prose, readiness, unified registry, and registry readers.
- Registry CSV/dossier synchronization check passed.
- All 27 catalog consistency checks passed after regenerating downstream projections.
- Exact comparison against base: all 33 dossiers, correction lists, and render_sources unchanged.
- Every populated storefront role in the inventory resolves to an existing file; SHA-256 recorded.
- Frontend lint could not start: missing @next/eslint-plugin-next in this checkout. No frontend application code changed.
- Frontend type-check failed with missing React Query/Radix dependencies and TypeScript errors in existing application files; this pass is not a green full-frontend build.
- No live store, checkout, deployment, or full-image fidelity acceptance is claimed.

## Evidence

`overview-before-1.jpg` through `overview-before-6.jpg` show bindings before corrections. `reference-candidates-1.jpg`, `reference-candidates-2.jpg`, and `fallback-review.jpg` capture reviewed candidate/fallback pixels. The screenshots are contact sheets for triage only, not new product assets. inventory.json contains the registry hashes and exact original image paths/hashes for each correction.

## Full-resolution rear review — second pass

Supersedes the overview-only suspicions above. Reviewed six flagged/fallback image files at original-detail request and four source candidates (large images may be resized by the display tool). Evidence: rear-review.json.

- sg-007: cleared the decorated-face rear binding; back now explicitly absent.
- sg-009: cleared the open-lining rear binding; the existing exterior-back image now resolves through the explicit fallback. This does not certify all garment details.
- sg-001: the image shows a rear-style welt pocket; do not call it a front view. The pocket conflicts with dossier prose and needs source reconciliation. Product facts and the current binding were retained.
- sg-003: rear identity remains unresolved; retained binding, no render-source promotion.
- lh-004: retained composite because the rear artwork panel is visibly included. A dedicated back-only image remains desirable.
- Four Signature reference candidates inspected; no candidate promoted past unresolved identity/artwork issues.

Current missing storefront back count: 7. Explicit back fallbacks: sg-009 and sg-011. Missing render slots remain 16. No binaries, founder facts, dossiers, corrections, or render sources changed.

All 27 catalog consistency checks and 46 focused tests pass. Earlier frontend environment failures remain unresolved and this is not a full frontend build or deployment acceptance.

## Image library, fit/care and material review (2026-09-29)

See [image-library/README.md](image-library/README.md) and [the all-33 material review](image-library/material-review/REVIEW.md). Current intake: 92 reviewed photo/detail bindings across 27 products; all 33 collection/SKU folders; 270 standardized 2400-square exports. Material hypotheses remain outside the authoritative product fields pending founder confirmation. Fit is updated for all 33; basic garment care for 32, with the Fannie accessory-care exception awaiting confirmation.
