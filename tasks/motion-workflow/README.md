# Motion + three.js workflow (scaffold)

Status: **intake**. The founder is still supplying files; no workflow design is committed.

## Files

| File | Purpose |
| --- | --- |
| `sources.json` | Ledger of every input supplied, in order. Append only. |
| `catalog.json` | Taxonomy of motion.dev/examples (exact slugs, by framework). Not exhaustive. |
| `research-more-sources.md` | Deep-research report: ranked top 15 free/open sources for fashion motion + rejects. |
| `references.json` | Nine inspiration galleries: pattern/effect taxonomy and fit. Home pages only. |
| `remotion.json` | The Remotion starter at repo-root my-video/: stack, skills, dev server, constraints. |
| `rive.json` | Scaffold of rive-app/rive-runtime: C++ core vs the @rive-app/* web family, asset dependency. Not installed. |
| `twgl.json` | Scaffold of greggman/twgl.js: API, overlap with three.js, narrow niche. Not installed. |
| `cobe.json` | Scaffold of shuding/cobe: globe API, DOM binding, brand constraints. Not installed. |
| `drei.json` | Scaffold of pmndrs/drei: installed version, peers, helpers used vs available. |
| `confetti.json` | Scaffold of catdad/canvas-confetti: API, options, brand constraints. Not installed. |
| `deckgl.json` | Scaffold of visgl/deck.gl: modules, layers, versions, fit assessment. Not installed. |

## Constraints carried in from CLAUDE.md

- **Surface split.** React output goes to `frontend/` (devskyy.app). The WordPress theme (skyyrose.co) is vanilla JS with no bundler, so only `js-*` examples apply, vendored self-hosted and built into `.min`. Never mix `frontend/node_modules` with root.
- **STOP-AND-SHOW** before any deploy, WC write, media upload, or paid call.
- **Product facts** come only through `get_product(sku)`. Founder corrections are authoritative.
- **Context7 first** for Motion API usage (`/websites/motion_dev`, High reputation, 1083 snippets).
- **Brand.** Motion must respect reduced-motion and the brand type/colour tokens; no tagline is authorized.

## Open decisions (founder)

1. ~~Where `motion` lives~~ Resolved: installed in `frontend/`, reverted from root. Open: `motion` and the pre-existing `framer-motion` overlap; migrate imports to `motion/react` or keep both?
2. Whether to register `https://mcp.motion.dev` in `.mcp.json` (hand-edit; `claude mcp -s project` strips parked entries).
3. Target form of the workflow: `Workflow` script, saved `.claude/workflows/` entry, or skill.
4. Motion+ licence status. The gallery examples need the Motion+ Gallery component; the page text does not mark which examples are paid.

## Known gaps

- The examples page advertises 490+; the catalog lists what the fetched text enumerated.
- No example source code has been read yet, only the index. Per-example fetches are needed before any is cited as working.
