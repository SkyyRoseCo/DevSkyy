# Asset Hub Build — todo

Single source of truth for ALL imagery (product renders + scene + web/site + ads),
separated by collection + site, usage-tagged, verified-only-serves. Spec: `assets/hub/HUB-SPEC.md`.
Research backing: `assets/hub/RESEARCH-similar-brands.md`.

## Phase 1 — Hub skeleton + manifest + migrate verified  (FREE / reversible)
- [ ] HUB-SPEC: fold in research additions (provenance block, campaign/ads lifecycle tier, attribute-anchored verify)
- [ ] `assets/hub/build_hub.py` — deterministic migrator (session eyes-on verdicts + June review-state QC)
- [ ] Run: create hub tree, copy verified product masters, register scenes + lockups + logos/hero-overlays
- [ ] Write `assets/hub/manifest.json` (scope, usage[], sku, face, engine, verdict, verified_by, provenance, source)
- [ ] Self-verify: every verified/migrated path exists; print coverage (verified vs pending); git diff scope

## Phase 2 — Promote → serve + repoint + guard + fix defects  (FREE / reversible, NO deploy)
- [ ] Generate served webp/avif derivatives from hub masters
- [ ] Fix br-010 back in place (verified gemini-corrected master → served back) — the one defect with a free verified fix
- [ ] Repoint catalog front/back cols for OK-now set; rebuild `sot.json` + `sot-images.json`
- [ ] Guard test: served product image must trace to a hub master; no consumer reads off-hub trees
- [ ] pytest imagery suite green; eyes-on the br-010 fix

## Phase 3 — Census + delete off-hub conflicts  (STOP-AND-SHOW — deletion policy)
- [ ] grep census per file; show exact delete list; await y

## Phase 4 — OAI-2 re-render gaps  (STOP-AND-SHOW — paid + cost + y)
- [ ] Manifest of pending SKUs (sg-002 F/B, lh-002 B, all FLAG/unmapped fronts + backs); cost; await y

## Known verified (this session, eyes-on 2026-06-25)
br-004 F+B · br-010 F + B(gemini-corrected) · lh-002 F · sg-001 F+B · kids-001 F+B
## Known wrong → pending re-render
sg-002 F+B · lh-002 B · (br-010 B old comet-G superseded by gemini-corrected)
