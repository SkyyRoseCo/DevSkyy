# Root Reorganization Plan — 2026-07-07

**Status: PROPOSED — nothing moves until founder approves.**
Census method: `git ls-files` + single-pass `rg -F` reference scan (excluding .git, node_modules, .venv, caches, lockfiles). All items below are git-tracked unless noted, so every move is reversible.

## Baseline

- 307 items at repo root: 191 files + ~85 dirs + 9 intentional SOT symlinks.
- Caches (`.mypy_cache`, `.pytest_cache`, `.ruff_cache`, `__pycache__`, `.playwright-mcp`, `devskyy.db`, `.DS_Store`) are already gitignored and untracked — no action needed.
- SOT symlinks (`skyyrose-catalog.csv`, `sot-images.json`, `cerebrum.md`, `anatomy.md`, `buglog.json`, `visual-manifest.json`, `logo-registry.json`, `hub-manifest.json`, `adk`) are intentional per SOT.md — **do not touch**.

## A. Screenshot/QA artifacts → `screenshots/root-audit/` (~100 files, ~10 MB)

All root `*.png` `*.jpg` `*.jpeg` + Playwright `*snapshot*.yml` + `render-review.html`.
Reference census across 103 files found only 4 with any references:

| File | Refs | Action |
|------|------|--------|
| `sig-hero.jpg` | 4 (incl. `tests/agents/test_skyyrose_agents.py`) | Move + update referencers in same commit |
| `glb-models.html` | 1 external (`tasks/archive/2026-h1/v7-product-card-merge.md`) | Move + update doc link |
| `render-review.html` | 1 (doc) | Move + update doc link |
| remaining ~99 files | 0 | Move, no ref fixes needed |

- [ ] `git mv` all → `screenshots/root-audit/`; fix the 3 referencers in the same commit.

## B. Loose root docs → `docs/`

| File | Refs | Action |
|------|------|--------|
| `G1-BUNDLE.md`, `HANDOFF.md`, `INITIAL.md`, `INITIAL_EXAMPLE.md` | 0 | → `docs/archive/2026/` |
| `CONTEXT.md` | 2 | → `docs/` + update referencers |
| `DESIGN.md` | 5 | → `docs/` + update referencers |
| `REMEDIATION_MAP.md` | 1 | → `docs/` + update referencer |
| `.impeccable.md`, `.plugin-fix-complete` | 0 | → `docs/archive/2026/` (or delete — tracked, reversible) |

Stays at root: `README.md`, `CLAUDE.md`, `SOT.md`, `CHANGELOG.md` (12 refs).

## C. `.env` sprawl (16 variants → keep the live set, archive the rest)

Keep at root (live/config): `.env`, `.env.example`, `.env.docker`, `.env.docker.example`, `.env.wordpress`, `.env.wordpress.example`, `.env.hf` (95 refs), `.env.judge-{gemini-vision,gpt-vision,opus-thinking}` (6–7 refs each — eval scripts read them by path; moving would touch many scripts, not worth it).

| File | Refs | Action |
|------|------|--------|
| `.env.backup-2026-05-26` | 0 (also 0 bytes) | Delete — STOP-AND-SHOW (untracked env file) |
| `.env.example.hg7` | 0 | Delete or fold into `.env.example` |
| `.env.elite-web-builder` | 3 | Verify consumers, then decide |

## D. One-off scripts → `scripts/`

`install_agy.sh` (0 refs), `run_generation.sh` (0), `pre-build-check.sh` (0 — verify not called from CI/package.json before moving), `claude-mem-settings.sh` (1), `setup-claude-config.sh` (2), `autonomous_agent_demo.py` (4 — refs look doc-side; verify).
- [ ] `git mv` each → `scripts/`, update referencers in same commit.

## E. Data/report files

| File | Refs | Action |
|------|------|--------|
| `redirects.csv` | 5 | → `data/` + update referencers |
| `skyyrose_clothing_barcodes.txt` | 2 | → `data/` + update referencers |
| `autotrain_config.yaml` | 3 | → `config/` + update referencers |
| `deployment_summary.json`, `wordpress-health-check-results.json` | ≤1 | → `.reports/` or delete (generated output) |
| `SKyyRose Flagship.zip` (1.8 MB), `elite_web_builder.zip` | 0 | → `.archive/` — STOP-AND-SHOW (potentially expensive assets) |
| `devskyy.db` | runtime SQLite (gitignored) | Leave in place |

## F. Phase 2 — root directory consolidation (separate pass, needs per-dir census)

~85 root dirs. Flagged overlaps, NOT actioned in this plan:
- `archive/` vs `.archive/` — two archive conventions
- `screenshots/`, `renders/`, `generated_assets/`, `generated_3d_models/`, `graphify-out/`, `round_table_outputs/` — output-dir sprawl
- experiment dirs: `aos/`, `prototypes/`, `editorial-staging/`, `ds-bundle/`, `dev/`, `examples/` — census each before proposing moves
- tool-config dirs (`.aidesigner`, `.codex`, `.cursor`, `.gemini`, `.ralph`, `.ralph-tui`, `.serena`, `.swarm`, `.zap`, `.zed`, …) — harmless; leave

## Execution protocol (on approval)

1. One batch: `git mv` + referencer edits per section (A–E), single commit per section.
2. Deletions and zip moves: STOP-AND-SHOW individually before executing.
3. Verify: `pytest -x --timeout=10`, `ruff check`, `git status` clean, spot-check the 3 fixed referencers.
4. Update `.wolf/anatomy.md` + append `.wolf/memory.md`; log lesson if anything was mis-censused.

## Review

_(filled in after execution)_
