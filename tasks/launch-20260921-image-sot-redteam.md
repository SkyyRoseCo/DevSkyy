# Image and product SOT red-team — 2026-09-21

## Scope and result

Read-only audit of the current local product registry against live `origin/main`, the V2 approved-card manifest, its image binaries, founder-authored product dossier facts, and the three corresponding main-theme front-model images. No registry, image, staging, or product-fact changes were made during this audit. The local registry already has the approved-front references, but two of the three approved model fronts have visible fidelity gaps against their current founder-authored product specifications.

**Blockers:** BR-002 does not show the specified white ribbed ankle cuffs; KIDS-002 does not visibly show the specified one-sleeve circular patch. BR-005's placement matches its current left-hip/body-side specification.

## Authority and freshness

The repository root `logo-registry.json` resolves to `wordpress-theme/skyyrose-flagship/data/logo-registry.json`, the editable product SOT. Reads used `from skyyrose.core.product import get_product` for `br-002`, `br-005`, and `kids-002`. The three front image records resolve to:

- BR-002: `assets/images/products/black-rose-joggers/black-rose-joggers-approved-front-model.webp`
- BR-005: `assets/images/products/black-rose-hoodie-signature-edition/black-rose-hoodie-signature-edition-approved-front-model.webp`
- KIDS-002: `assets/images/products/kids-purple-set/kids-purple-set-approved-front-model.webp`

`git ls-remote origin refs/heads/main` returned `9917f0e6b7b9dfc4087f8c900ab2e3465d01a7ed`, equal to local cached `origin/main`. This establishes the remote ref freshness at audit time. The live origin registry still points these SKUs' `catalog.front_model_image` values at the old `assets/images/products/ghost/...` paths. The local working registry points those three roles at the approved model fronts above. This comparison is scoped to these three SKUs; it does not justify replacing the dirty local registry with origin. The garment specifications and logo placements compared here match `origin/main`; differences in these records include the image-role updates and source/provenance strings (`founder product dossier` locally vs `derived_from_dossier` on origin), not conflicting garment facts.

The approved-card manifest is `/Users/theceo/.codex/worktrees/abe0/DevSkyy/wordpress-theme/skyyrose-flagship-2/data/approved-card-fronts.json`. Its `products` entries mark the three assets `FOUNDER_APPROVED_V2_CARD`; each `sha256` matches both the V2 binary and the copied V1 binary byte-for-byte:

| SKU | Manifest source path | SHA-256 | Visual audit |
| --- | --- | --- | --- |
| BR-002 | `assets/approved-card-fronts/br-002-onmodel.webp` | `6e395127c4b6f09a1602db3c30963bb31a42559fe64dfbca990832c3dbc951ba` | Fidelity blocker: ankle ribbing is black; no white ankle cuffs are visible. White waistband and white drawstrings are visible. |
| BR-005 | `assets/approved-card-fronts/br-005-onmodel.webp` | `19f888f11bc6e3a282088281040ee8b27be1e5473e1b4b53fc5ad5509e80a19b` | Large cluster appears on wearer-left body/hip; sleeve is clean. Consistent with current dossier placement. |
| KIDS-002 | `assets/approved-card-fronts/kids-002-onmodel.webp` | `88c0ca36b22a95ce1ee7969b50b4e256718ffda584027dfd97e219605aa3e51b` | Fidelity blocker: the single required circular sleeve patch is not visible. Color-blocking, chest mark, and pants mark appear consistent. |

## Product-specific findings

### BR-002 — do not mark its front as fully conformant

The current `get_product('br-002')` specification requires a white ribbed waistband and white ribbed ankle cuffs. The founder-authored dossier at `wordpress-theme/skyyrose-flagship/data/dossiers/black-rose-joggers.md` also defines the waistband and both ankle cuffs as white; it states the flat drawstring is white and explicitly says not to render a black drawstring. The approved model front visibly has a white waistband and white drawstrings. At both ankles, however, the trouser fabric ends in black ribbing, with white socks below. The image does not show white ribbed cuffs. This is a clear pixel-level mismatch to the authoritative specification.

The `.wolf/memory.md` note says “white instead of black drawstring.” That statement conflicts with the current founder-authored dossier and the visible white strings in the approved front, so I did not treat that recollection as an authoritative product correction. No current product fact authorizes changing the drawstring to black. The visible cuff mismatch remains a blocker. Exact role/source: current SOT `products.br-002.garment.features.specification`; dossier above; approved card manifest entry `products.br-002`.

### BR-005 — placement matches the founder specification

The current SOT places the right-chest silicone cutout and the embroidered cluster on the body side, with note “On body side, NOT on arm.” The founder-authored dossier identifies the large cluster as wearer-left hip/side body, not sleeve. The approved model front shows the large cluster at the wearer-left hip/body side and no rose cluster on the sleeves. The hoodie source/reference photos also show side-body placement. This is consistent with the founder's current direct correction recorded in `.wolf/memory.md`; the contrary reading came from an earlier review of a folded flatlay, not a competing product specification.

A legacy text item in the current product corrections says the logo “is on the sleeve” and is supposed to be on the side. It describes the observed bad render and desired correction, rather than authorizing a sleeve placement. The present garment placement fields and dossier are unambiguous. The visible image verifies location, but not the physical silicone relief at this scale.

### KIDS-002 — one required patch is missing from the visible front

The current SOT requires one circular patch on the right arm (`logos.placements`, `position: right_arm`); its founder dossier says exactly one upper-sleeve patch on one sleeve, with the opposite sleeve plain. The approved front shows the chest cluster, purple/lavender color blocks, and one pants cluster. Neither visible upper sleeve shows the circular patch. This means the image cannot be marked as a fully faithful front view, even though other visible elements look consistent. Do not infer a sleeve orientation or patch design from the approved image; the product dossier and real-photo reference remain authoritative.

## Evidence level and required next decision

- **Source verified:** current main SOT through `get_product`; founder-authored dossier; current V2 approved-card manifest; live `origin/main` ref and targeted registry comparison.
- **Hash verified:** approved front files are byte-identical across the V2 source and main-theme copies; hashes are listed above.
- **Pixel inspected:** all three V1-bound front binaries were opened directly at high detail. Findings above are visual observations, not proof of physical garment construction or a live staging response.
- **Not performed:** no staging-browser verification, image regeneration, image upload, product-fact edit, registry update, or deployment.

A founder-authorized replacement/correction should be identified for BR-002's white cuffs and KIDS-002's single sleeve patch before either is reported as passing product-image fidelity. Preserve the existing approved images and SOT bindings until that decision is made. The origin/main comparison supports the local role correction over the stale ghost bindings, but it does not change the visual-fidelity blockers.
