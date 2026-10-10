# Reference design asset map — 2026-09-21

Read-only mapping of the supplied Veritas fashion reference into existing SkyyRose V2 SOT assets. No generation, paid calls, catalog writes, media edits, or deployment. Product role claims remain subject to the unified registry and existing image QA. BR-002 and KIDS-002 approved fronts are excluded from featured slots because the preceding red-team audit found visible fidelity blockers; BR-005 is retained only where the side-body placement is visible and useful.

## Recommended composition

| Reference slot | Existing asset | Desktop treatment | Mobile treatment | Why it fits |
|---|---|---|---|---|
| Full-bleed hero / quiet cinematic opening | `wordpress-theme/skyyrose-flagship-2/assets/sot/images/hero/signature-golden-gate-monuments-v2.webp` (1672x941) | `cover`, focal point center-right; reserve left third for eyebrow, headline, CTA | use responsive `.../hero/responsive/signature-golden-gate-monuments-v2-640w.webp`; keep focal point around monument/bridge, reduce text width | dark, editorial Bay landscape with metallic rose-gold type; supports the supplied reference's luxury landscape language without inventing a new image |
| Hero alternate / darker Black Rose story | `.../assets/sot/images/hero/black-rose-lake-merritt-monument-v2.png` (1672x941) | `cover`, focal point center-right; preserve lake/city negative space | `.../hero/responsive/black-rose-lake-merritt-monument-v2-640w.webp`; crop vertically around star/rose monument | strongest dark monochrome equivalent to the supplied reference's black fashion mood |
| Collection/editorial split image | `.../assets/sot/images/immersive/scene-signature-oakland-atelier-gpt2.webp` (1920x1080) | 50/50 image-copy split; crop right-side rose/counter detail; keep skyline visible | image above copy, 4:3 crop centered on rose and counter; do not crop to a product claim | material/atelier image creates the “designed for what's next” editorial transition |
| Dark collection split alternative | `.../assets/sot/images/immersive/scene-black-rose-moon-court-gpt2.webp` | image left, copy right; keep emblem and horizon | 4:3 crop centered on emblem; preserve dark contrast behind light type | matches the reference's black gallery / architectural tone |
| Product card 1 | `.../assets/approved-card-fronts/br-001-onmodel.webp` (V2 worktree `/Users/theceo/.codex/worktrees/abe0/DevSkyy/...`) | 4:5 card, full garment visible, `object-position:center 45%` | 1-column card, keep head-to-hem and lower logo in frame | existing approved front and safe Black Rose featured candidate |
| Product card 2 | `.../assets/approved-card-fronts/br-004-onmodel.webp` | 4:5, center garment; retain chest artwork | 1-column, avoid face-only crop | existing approved hoodie front; suitable monochrome card |
| Product card 3 | `.../assets/approved-card-fronts/sg-005-onmodel.webp` | 4:5, preserve full silhouette | 1-column, keep garment and lower hem | existing approved Signature candidate; adds warm metallic contrast |
| Product card 4 | `.../assets/approved-card-fronts/lh-004-onmodel.webp` | 4:5, preserve jacket front and rose environment | 1-column, crop from head through hem | existing approved Love Hurts front; supplies the reference's editorial model energy |
| Optional product card 5 | `.../assets/approved-card-fronts/br-003-onmodel.webp` | 4:5 or 3:4, preserve jersey front numbers | mobile crop centered on garment chest | existing approved front, but use only after normal product-role and source binding checks |
| Philosophy / full-width story band | `.../assets/sot/images/hero/love-hurts-rose-aisle-monuments-v3.webp` (1672x941) | full-width `cover`; keep central figure and aisle; copy in left/right safe zone | use 640w responsive source; central crop, text below image instead of overlay | supplies the supplied reference's human-scale, cinematic “a more human future” beat |
| Journal / detail tile | `.../assets/sot/images/hero/black-rose-bay-bridge-monuments-v4.webp` | wide 16:9 tile; keep bridge and emblem | use 1024/640 responsive counterpart, crop to bridge/emblem | editorial bridge imagery works for journal teaser and preserves Bay identity |
| Video teaser poster | `.../assets/video/jersey-series-bart-poster.webp` | 16:9 tile with play control; no autoplay requirement change | 4:5 or 16:9 poster crop with play control | existing video-linked poster; keeps motion feature intact |
| Video alternate poster | `.../assets/video/skyyrose-tour-around-the-bay-poster.webp` | 16:9 tile, preserve route/brand mark | same poster with focal point centered | supports a journal/story tile while retaining verified video connection |

## Approved card source hashes

The approved-card manifest at `/Users/theceo/.codex/worktrees/abe0/DevSkyy/wordpress-theme/skyyrose-flagship-2/data/approved-card-fronts.json` marks these suitable card candidates as `FOUNDER_APPROVED_V2_CARD`:

- BR-001 `fcaddcf8a93e22283137b2a165cfb7ab216d0dab45853e5da7b4a23818071aa8`
- BR-003 `43e75a7280e7b3bda87bacde28971274bf7633400b06b13b77a873c005647ea9`
- BR-004 `8c415f0fe1e5ab113e74f7a7040563b5396f2672f400cf9d30f99db839de32c8`
- BR-007 `b2e523f08f8bae826e45c0a01584dee54c735c7dda2fc81edcf65c420ac9030d`
- SG-005 `052915cfb4aaa7f3d1fdd01d222661289cb7a1eab0fdec9b68a8be8dda8f28f0`
- LH-004 `1c5aed2f72b85b5afc7a25515931e450e68dfa66011b0345c13605020b89fddc`
- KIDS-001 `c6bd2ddd555c4359c302eebb051d5fbad4d34bec0b324b44f3447831f3ec9c9a`

These are asset-manifest facts, not a substitute for current product-role routing. Use `get_product(sku)` before binding any product card. Keep BR-002 and KIDS-002 out of the featured set until their visual blockers are corrected through a founder-authorized source decision.

## Layout and crop rules

- Keep the reference's dark graphite background, warm bone typography, restrained tracking, and thin rules in CSS/theme work; image mapping alone does not change motion, hover, navigation, or video features.
- Use `object-fit: cover` for full-bleed hero/editorial sections, with per-asset focal positions above. Use `object-fit: contain` or generous `object-position` for product fronts when the garment edge, logo, or lower hem is a product fact.
- Desktop hero assets are 16:9-class. Use the existing 640w/1024w/1440w responsive variants where present; do not stretch 640w to desktop. For mobile, place copy below the image when an overlay would cover the garment or emblem.
- Existing high-end animation and video sources remain unchanged. The two poster assets are only verified visual entry points; actual video route/link validation remains a separate E2E check.
