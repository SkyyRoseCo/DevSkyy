# Ghost-Mannequin Render Pipeline + Repo Consolidation — Handoff (2026-06-02)

## Goal
Produce clean **2D ghost-mannequin product renders** for all 33 SKUs → display on skyyrose.co PDPs.
(Pivoted away from displaying the 33 Meshy 3D GLB meshes — those are parked, compressed at `renders/3d/web/*.glb` 51MB, if rotatable 3D ever wanted.)

## TWO OPEN DECISIONS (founder's call — start here)
1. **Sequencing:** consolidate repo first / batch the 10 ready renders first / parallel? Nothing has rendered live yet; founder has twice wanted visible progress.
2. **br-003 transfer test** needs a clean per-call `y` (auto-mode classifier rejected the approval that was bundled with the consolidation directive). Command ready (see below).

---

## A. RENDER PIPELINE (working — v4 recipe LOCKED)

**Engine:** Seedream-4 via fal — `fal-ai/bytedance/seedream/v4/edit` (image-to-image).
**Script:** `scripts/seedream_ghost_mannequin.py --sku <sku> [--go] [--style-ref <path>] [--out <path>]`
- Dry-run default (no spend). `--go` dispatches (paid, ~$0.06/image).
- Reads flatlay→else techflat from `assets/product-source/{sku}__*/`, builds fidelity-preserving prompt from `spec.json`.
- `--style-ref` = uploads a 2nd image (the target look); prompt says "IMAGE 1 garment in IMAGE 2 presentation."
**Key:** `FAL_KEY` lives in `.env.hf` (69 chars, on theceo mac). Script loads `.env`, `.env.hf`, `.env.secrets`.
**Gate:** `.claude/hooks/paid-api-stopgate.sh` rule added — `seedream_ghost_mannequin.py.*--go` is BLOCKED until `STOPSHOW_ACK=1` is the **LEADING prefix** (no `cd` before it; use absolute paths).

**Run pattern (after founder `y`):**
```
STOPSHOW_ACK=1 /Users/theceo/DevSkyy/.venv/bin/python /Users/theceo/DevSkyy/scripts/seedream_ghost_mannequin.py --sku <sku> --go --style-ref /Users/theceo/DevSkyy/assets/product-source/_style-reference/love-hurts-ghost-mannequin-ref.jpeg --out <abs-out-path>
```

**Prompt dialing history (lh-004, ~$0.30 spent, 4 probes):**
- v1 (prompt only): worn volume ✓ but mannequin HEAD ✗
- v2 (hollow prompt): hollow ✓ but went FLAT (flat-lay) ✗
- v3 (+ style-ref): ghost-mannequin form ✓ but DIRTY body + leather sleeves ✗ (cause: word "worn" → distressed)
- **v4 (style-ref + fabric lock, "worn" removed): CLEAN ghost-mannequin, matches founder reference. THIS IS THE RECIPE.**
  Saved: `assets/product-source/lh-004__love-hurts-bomber-jacket/renders/seedream-probe-v4-clean.png`

**Style reference:** founder's approved ghost-mannequin example at `assets/product-source/_style-reference/love-hurts-ghost-mannequin-ref.jpeg` (the Love Hurts hoodie). Founder originally pulled from Photos: `~/Pictures/Photos Library.photoslibrary/...2089A163...jpeg`.

**OPEN render question (the br-003 test answers it):** the only style-ref is a JACKET. Does it transfer to other garment shapes (jersey/beanie/shorts) without bleeding jacket geometry? RECIPES.json shows 10 SKUs READY (jacket+hoodie families use this ref), 22 NEED a type-ref, 1 (sg-012) NEED a pic. Founder pushed back on uploading per-type refs ("flatlays ARE the references") — so TEST the one ref across types first; if a type fails, fix via prompt, don't ask founder to upload.

**br-003 test command (needs founder `y` first):**
```
STOPSHOW_ACK=1 /Users/theceo/DevSkyy/.venv/bin/python /Users/theceo/DevSkyy/scripts/seedream_ghost_mannequin.py --sku br-003 --go --style-ref /Users/theceo/DevSkyy/assets/product-source/_style-reference/love-hurts-ghost-mannequin-ref.jpeg --out /Users/theceo/DevSkyy/assets/product-source/br-003__black-is-beautiful-jersey-series-0-baseball-classic/renders/seedream-transfer-test.png
```

---

## B. SOURCE OF TRUTH (built this session)

`assets/product-source/{sku}__{slug}/` — 33 folders, each:
- `flatlay/` — founder's real product photos (dropped via Finder; mixed filenames; front/back NOT sorted)
- `techflat/` — clean garment flats (21 prefilled from `assets/techflats/split/`)
- `logos/` — dossier-defined applied logos + collection mark
- `spec.json` — extracted from dossier: construction/fabric + logo_placements (region·technique·color) + logos + sources + status
- `assets/product-source/INDEX.json` — manifest (sku → all paths + status)
- `assets/product-source/RECIPES.json` — per-SKU: family + source_kind + style_ref
- `assets/product-source/MAP-DRAFT.csv`, `README.md`

**Status:** 25 ready (have flatlay), 7 techflat-only (jerseys br-008/009/010/011 + sg-013/014/015 — OK per flatlay>techflat rule), 1 awaiting (sg-012 empty — founder cleaning held Signature pics in Photoroom).
**Regenerate after new pics land:** re-run the spec/INDEX python (inline in session history ~2026-06-01) — it reads catalog + dossiers + folders.

**Source rule (founder, LOCKED):** use MY flatlays, NOT prior AI renders (`*-front-model` etc.). If no flatlay → techflat. Never the AI renders.

---

## C. LOGO REFACTOR (done this session)
`black-rose-logo.md` was dual-role (Black Rose logo AND shared three-rose-cluster art). Extracted to collection-neutral `data/brand-logos/three-rose-cluster.md` (+ renamed image `three-rose-cluster.jpeg`); `black-rose-logo.md` now a pointer; 20 dossiers repointed (paths only, prose untouched). Verified: all resolve, test unaffected. NOT a bug originally — Signature dossiers intentionally reuse the cluster recolored (purple/blue). Lesson logged in `tasks/lessons.md`.

---

## D. REPO CONSOLIDATION (new directive — NOT started)
Founder: "get rid of conflicting files, like the CSV is source of truth, for the ENTIRE repo, so agents call 1 file/folder in 1 call instead of searching 300 and burning tokens."

**Plan (advisor-vetted — index first, deletions later, don't bundle):**
1. **INDEX (safe, zero deletions, the token win):** `.wolf/anatomy.md` ALREADY is this mechanism (4000 lines, 2610 entries) but STALE — 0 coverage of product-source/catalog. Refresh it + add a top-level canonical-sources map (products→`skyyrose-catalog.csv`+`product-source/INDEX.json`; logos→`data/brand-logos/`; fonts→…; etc.). Extend anatomy.md, do NOT build parallel system.
2. **DEDUP (risky, per-cluster, STOP-AND-SHOW each `rm`):** evidence-based clusters already surfaced — product images scattered across `products/`(503)÷`product-source/`÷`golden/`÷`photo-scan/`; empty `golden/{sku}/flatlays|techflat/` dirs; multiple env files w/ same keys (`.env.hf` has FAL_KEY); 56 empty CLAUDE.md stubs; retired catalogs (per wordpress-theme/CLAUDE.md).
Repo = 7,482 tracked files.

---

## GOTCHAS (cost the most time this session)
- **STOPSHOW_ACK=1 must be the LEADING prefix** of the Bash command — a leading `cd` breaks it. Use absolute paths instead.
- **Image-read quota** is per-conversation; heavy this session. Don't batch-read renders; send to founder + trust, or read sparingly.
- **lh-004 catalog vs dossier conflict:** catalog `description` says "satin bomber, black"; dossier (canon) says white body + black raglan sleeves, hooded varsity, "NOT satin bomber." Trust DOSSIER. Prompt built from dossier `spec.json`, not catalog blurb.
- **Founder wants visible progress** — don't disappear into refactors silently; gate big detours.
- Memory: `project_ghost_mannequin_render_pivot.md` has the full architecture record.
