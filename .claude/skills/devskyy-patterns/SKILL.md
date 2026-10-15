---
name: devskyy-patterns
description: >
  Coding patterns extracted from DevSkyy git history (200 commits re-analyzed
  2026-09-11). Commit conventions, co-change rules (CSS→.min rebuild, version
  triple, buglog discipline), hotspot files, monorepo architecture, theme build
  workflow, and test locations. Use when writing commits, editing theme CSS/JS,
  fixing bugs, or navigating the repo structure.
version: 2.0.0
source: local-git-analysis
analyzed_commits: 200
generated: 2026-09-11
---

# DevSkyy Patterns

Re-analyzed from the last 200 commits (2026-09-11). Observed practices, not
aspirations.

## Commit Conventions

**Conventional commits with mandatory scope for theme/sot/security/ci work.**

| Type     | Freq | Scope examples                                       |
| -------- | ---- | ---------------------------------------------------- |
| `fix:`   | 27%  | `(theme)` `(security)` `(ci)` `(sot)` `(deps)`       |
| `feat:`  | 20%  | `(theme)` `(plugin)` `(comfy)` `(dashboard)` `(sot)` |
| `chore:` | 16%  | `(theme)` `(wolf)` `(deps)` `(claude-md)` `(v2)`     |
| `docs:`  | 14%  | `(skills)` `(lessons)` `(comfy)`                     |
| `ci:`    | 5%   | `(catalog)` `(security)`                             |
| `deps:`  | 4%   | `(npm)` — batch-bump style                           |
| `perf:`  | 4%   | `(theme)`                                            |

Pattern: `type(scope): imperative-mood description`

```
fix(theme): correct hero overflow on mobile viewport
feat(sot): bind BR-007 four-angle authority
chore(theme): bump version triple to 2.2.5
```

**Scope decision tree:**

- `wordpress-theme/**` → `(theme)`; `.wolf/**` → `(wolf)`; `assets/products/**`
  → `(sot)`
- `Comfy/**` → `(comfy)`; `.github/workflows/**` → `(ci)`; `plugins/**` →
  `(plugin)`
- `frontend/**` → `(dashboard)`; security/vuln fix → `(security)` or `(deps)`

## Co-Change Rules (hard)

### 1. Theme Version Triple

Any version bump must touch all three in one commit:

```
functions.php   ← SKYYROSE_VERSION constant (~52 enqueue cache-busts)
style.css       ← Version: header
readme.txt      ← Stable tag
```

Commit: `chore(theme): bump version triple to X.Y.Z`

### 2. CSS Source → .min Rebuild (always)

Every `.css` source edit requires a rebuilt `.min.css` in the **same commit**.

```bash
cd wordpress-theme && npm run build:css                   # rebuilds all 61 .min files
cd skyyrose-flagship && node scripts/build-css.js --check # verify sync
```

CI `🏗️ WordPress Theme` will fail on any `.min` drift — no exceptions.

### 3. Bug Fix → Buglog Update (30 of 200 commits)

Significant bug fixes update `.wolf/buglog.json` in the same commit. Record:
bug-ID, description, fix summary, recurrence count.

### 4. Design Token Edits → Freshness Guard

Edits to `design-tokens.css`, `skyyrose-catalog.csv`, or `visual-manifest.json`
trigger the collection-SOT check. Run before staging:

```bash
bash scripts/freshness-guard.sh       # check
bash scripts/freshness-guard.sh --fix # regenerate derived files + re-stage
```

### 5. Fix → Learning (behavioral)

Corrective commits carry the lesson in the same commit:

- `tasks/lessons.md` — behavioral lessons
- `docs/engineering-learnings.md` — engineering lessons
- `.wolf/buglog.json` — bug record

## Hotspot Files (most-changed in 200 commits)

| File                                 | Touches | Risk                               |
| ------------------------------------ | ------- | ---------------------------------- |
| `.wolf/buglog.json`                  | 30      | Updated with every significant fix |
| `functions.php`                      | 21      | Version bump + hook registration   |
| `style.css`                          | 20      | Version bump + theme metadata      |
| `readme.txt`                         | 19      | Version bump only                  |
| `CLAUDE.md`                          | 16      | Agent config — reads frequently    |
| `inc/enqueue.php`                    | 11      | All CSS/JS registration lives here |
| `template-parts/collection/page.php` | 10      | Collection layout                  |
| `.github/workflows/ci.yml`           | 8       | CI pipeline                        |

## Theme Build Workflow

```bash
# 1. Edit source CSS/JS
# 2. Rebuild
cd wordpress-theme && npm run build        # CSS + JS + editorial index
# — or targeted —
cd wordpress-theme && npm run build:css    # CSS only

# 3. Verify sync (no drift)
cd wordpress-theme/skyyrose-flagship && node scripts/build-css.js --check

# 4. Run freshness guard if design-tokens.css touched
bash scripts/freshness-guard.sh

# 5. Commit source + .min + any version bump together
git add wordpress-theme/skyyrose-flagship/assets/css/
git commit -- <explicit paths>             # never bare git add .
```

## Monorepo Architecture

```
DevSkyy/
├── main_enterprise.py          # FastAPI entry (Python 3.11+)
├── api/                        # Route handlers
├── agents/                     # EnhancedSuperAgent + ADK agents
├── src/                        # Shared TypeScript (vitest)
│   ├── components/             # PascalCase.tsx
│   ├── hooks/                  # use*.ts
│   ├── lib/                    # Three.js, cart, checkout
│   └── types/
├── frontend/                   # Next.js 16 App Router dashboard
├── wordpress-theme/
│   ├── skyyrose-flagship/      # v1 — current production theme (skyyrose.co)
│   │   ├── assets/css/         # design-tokens.css → source → .min
│   │   ├── assets/js/          # source → .min
│   │   ├── inc/                # PHP modules (enqueue, WC, security)
│   │   ├── template-parts/     # Partials (BEM class naming)
│   │   └── data/               # SOT scripts + catalog
│   └── skyyrose-flagship-2/    # v2 — STAGING; replaces v1 on approval
│       ├── assets/sot/         # self-contained SOT (logos, heroes, fonts, video)
│       ├── data/               # generated: registry, font-provenance, image-opt
│       ├── scripts/            # build-assets.mjs, verify-marketplace.sh, package-theme.sh
│       └── dist/               # skyyrose-flagship-2.zip (packaged release)
├── Comfy/                      # ComfyUI + OODA ledgers
├── plugins/fashion-theme-team/ # Elite Web Builder runtime
├── tests/                      # Python pytest (test_*.py)
└── .wolf/                      # buglog, cerebrum, anatomy
```

**Workspace isolation:** `frontend/node_modules` ≠ root. WordPress build runs
from `wordpress-theme/` (not `skyyrose-flagship/`). ADK uses `.venv-agents/`.

## Testing Locations

| Layer                | Framework         | Location                                                   |
| -------------------- | ----------------- | ---------------------------------------------------------- |
| Python API           | pytest            | `tests/test_*.py`                                          |
| TypeScript shared    | vitest            | `src/**/__tests__/*.test.ts`                               |
| Frontend Next.js     | vitest/playwright | `frontend/tests/`                                          |
| WordPress PHP        | PHPUnit           | `wordpress-theme/skyyrose-flagship/tests/`                 |
| Three.js/Collections | vitest            | filter: `vitest … collections` (**not** `src/collections`) |

## Anti-Patterns (observed and corrected)

- Committing source CSS without `.min` rebuild → inert in production
- Using `src/collections` as vitest filter when directory doesn't exist → "no
  tests found"
- Bumping `SKYYROSE_VERSION` without the style.css + readme.txt triple → cache
  not busted
- `npm audit fix --force` on shared branch without reviewing breaking changes
- `git stash` in a shared worktree → pops another session's stash
- Editing WC core templates instead of hooks → all WC changes via theme
  overrides + hooks
- Staging auto-injected `<claude-mem-context>` CLAUDE.md churn → session noise,
  exclude

V2-specific anti-patterns → `wordpress-theme/skyyrose-flagship-2/CLAUDE.md`
