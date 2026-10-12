# SKYYROSE-FLAGSHIP-2 — harness SOP

## What the "software" is

The flagship-2 theme has no GUI of its own. Its operator surface is a set of 45
npm scripts in `wordpress-theme/skyyrose-flagship-2/package.json`. Those
scripts call `scripts/*.{py,mjs,sh,php}` and `tools/v2-runtime/*` and
`tools/v2-source-certification/*`. This harness follows the cli-anything
backend rule and calls those scripts through `npm run`. It reimplements none of
them.

## Backend engine and data model

| Concern | Source of truth |
|---|---|
| Gate commands | `package.json` `scripts`, read every time the CLI runs |
| Toolchain pins | `tools/v2-source-certification/build-inputs.json` (`node`, `npm`, `python`) |
| Product registry pin | `build-inputs.json` `current_registry_sha256` + `input_hashes[logo-registry.json]` |
| Version triple | `functions.php` `SKYYROSE2_VERSION`, `style.css` `Version:`, `readme.txt` `Stable tag:` |
| Product facts | `logo-registry.json` via `skyyrose.core.product.get_product` (not read by this CLI) |

## GUI action → CLI mapping

| Human workflow today | CLI |
|---|---|
| `npm run check:registry` in the theme directory | `check run check:registry` |
| `npm run verify` with the pinned Node on PATH | `check run verify` / `check all` |
| `npm run build:assets` | `build run build:assets` |
| hand-edit three files to bump a version | `version bump --to X.Y.Z` |
| compare the registry sha with build-inputs by hand | `pin status` |
| write handoff evidence by hand | `evidence export` / `evidence review` |

## Collaboration contract

- **God Mode X** (`SkyyRoseCo/god-mode-x`): the record follows its
  `task-evidence` schema 1 exactly, and the CLI validates it by running God Mode
  X's own `skills/instructions/scripts/check_completion.py`. That script is
  never copied into this repo.
- **Fashion Theme Team** (`fashion-theme-team` plugin): every gate entry carries
  the theme-release-engineer fields. The verdict follows the team's rules:
  - no self-review;
  - BLOCKED until an independent review exists;
  - PASS means ready for founder review only.

## Deliberate omissions

- Deploy, cache purge, and WooCommerce writes: production work stays
  STOP-AND-SHOW in `scripts/deploy-theme.sh`.
- Recertification (moving V2 pins) requires founder approval. `pin status`
  only reports drift.
- `render:*`, `certify:*`, `workflow:*`, `author:*`, and the image-judge
  scripts are refused because they can make provider calls.
- Undo/redo: gate runs are an append-only ledger. A build is undone with
  `git checkout`, not by the CLI.
- Preview: there is no truthful local preview backend (see README).
