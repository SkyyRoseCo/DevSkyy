# Product library reconciliation

The sole editable authority remains `logo-registry.json`; read `get_product(sku)`.

- Inventory: 5,132 image locations across this worktree and supplemental main-checkout asset roots. Same-path, same-byte supplemental copies are omitted. Non-product images are included in this census; this is not a claim that 5,132 product photographs were verified.
- Visual source-photo review: 213 hash-distinct flatlay/source-photo candidates on 11 contact sheets. 92 source images are bound to 27 products. Six SKUs still lack an individually reviewed source photo in this intake.
- Library: all 33 products grouped by collection under `assets/products/catalog`; 270 distinct product exports, all 2400 × 2400 PNG. Native originals remain intact. Existing registry-bound storefront images are labelled as existing bindings, not newly founder-approved images.
- Main-only intake: 17 source files copied byte-for-byte into product originals, with original-location provenance and SHA-256 bindings.
- Unresolved/other material: separate local review links under `assets/products/outside-verified-products`. Filename matches never establish product identity. Original review material is retained, including older designs.

## Misleading source names found

White Love Hurts jogger photos under LH-002 names belong to LH-006. Fannie images under LH-001 names belong to LH-005. Black baseball imagery named as white belongs to BR-003; white baseball imagery named BR-003 belongs to BR-015. A Signature Edition hoodie named BR-004 belongs to BR-005. The purple Stay Golden shirt filed under SG-005 belongs to SG-002. These are image-identity corrections, not changes to founder product specifications.

## Retouch method and limits

`retouch-pilot/comparison.jpg` compares a source against a conservative local plain-fabric smoothing experiment. The chest artwork and collar are pixel-identical in decoded RGB; no AI, warping or hue transformation is used. Deep folds remain. The test is not a final ecommerce image and is not promoted into product bindings.

For stronger results, use individually masked healing/clone work sampled from the same fabric, preserving every seam and graphic, followed by source comparison. Adobe documents sampled healing and nondestructive retouching in its [photo retouching guide](https://helpx.adobe.com/in_hi/photoshop/how-to/photo-touch-up.html) and [ecommerce photography guide](https://blog.adobe.com/en/publish/2022/04/11/ecommerce-product-photography-tips-tricks). Those guides support the general method; they do not validate this local experiment. No external retouch service was used.

## Founder fit and care

The 2026-09-29 statement is preserved verbatim in every SKU dossier and the change record. All 33 fit fields derive `gender neutral relaxed fit`. Basic care guidance is labelled agent-authored at the founder's request; drying on low heat is founder-confirmed. Heavy polyester was described as present in some products; exact SKU assignments, percentages and the phrase “this fabrics” remain unresolved and were not guessed.

Reproducible standardized PNG binaries are retained locally and ignored by Git (about 500 MB). Source originals, imports, source/export hashes, indexes and the deterministic builder are versioned. Rebuild after checkout before running the library validation. This follows the repository convention of keeping reproducible media derivatives out of source control.

Renderer reference classification was checked against [the required imagery prompting reference](/Users/theceo/.codex/creative-standards/imagery-prompting.md). Scope: preserve exact physical artwork bindings and keep technical drawings distinct from physical rear-photo evidence. No creative concept or generation was submitted; provider seed, camera, scene and video controls are not applicable to this source-classification fix.
