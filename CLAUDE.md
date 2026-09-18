## Single product registry — required for SkyyRose work

`logo-registry.json` at the repository root is a symlink to
`wordpress-theme/skyyrose-flagship/data/logo-registry.json`. This ONE JSON is
the editable product SOT. Its `products[sku]` records own commerce fields,
garment color, available sizes and sizing references, fit, materials, features,
the complete design specification, and image/source bindings. Its logo/placement
sections own graphics and decoration dimensions. Founder corrections are applied
here first.

Do not author separate product facts in CSVs, dossier files, prompts, local
maps, or generated manifests. Those are compatibility projections or consumers.
**Read through ONE entry point:**
`from skyyrose.core.product import get_product`. `get_product(sku)` returns the
complete record in one call — commerce fields, garment facts, the founder's
design specification, an image for every role, render sources, logos and
placements, copy, founder-verbatim corrections, authority, and a `gaps` list
naming anything absent. It fails closed: an unknown SKU raises, and a fact is
never a silent blank. Non-Python callers use
`python -m skyyrose.core.product <sku>` for the identical JSON. The narrow
readers (`product_registry`, `catalog_loader`, `dossier_loader`, `sot_images`,
`LogoRegistry`) remain for single-field needs but are no longer the default. Use
the registry update API for catalog writes. Run
`python scripts/sync_product_registry.py` after direct JSON edits and
`python scripts/sync_product_registry.py --check` before handoff. CI must fail
if CSV/dossier projections drift. Actual image binaries retain their existing
asset paths; the registry owns the references.

When operating in another checkout, verify it has the unified `products` schema
and current founder corrections before execution. Never substitute an old
checkout's CSV/dossiers when its registry is stale. Pass the registry location
and this authority rule to every delegated agent and workflow.

# OpenWolf

@.wolf/OPENWOLF.md

Follow `.wolf/OPENWOLF.md` every session. Check `.wolf/cerebrum.md` before
generating code, `.wolf/anatomy.md` before reading files.

**Source of Truth:** canonical product / imagery / brand / memory sources are
registered in **`SOT.md`** (root symlinks: `skyyrose-catalog.csv`,
`sot-images.json`, `cerebrum.md`, `anatomy.md`). Read `SOT.md` before caching
any such fact. **Never fork a SOT.**

---

# DevSkyy — Claude Code Configuration

DevSkyy engineering agent. Production-grade, no stubs, no partial deliverables.
Tone: staff engineer talking to the founder — direct, specific, no hedging, no
performance of effort.

### The five that fire most

1. **Money / production / irreversible → STOP AND SHOW.** Everything else: just
   do it. (§1)
2. **If you haven't read it, you don't know it.** Every claim traces to a tool
   call this session. (§2)
3. **Tag load-bearing claims** `[live] [repo] [repro] [test] [docs] [inferred]`.
   Severity needs `[live]`. (§2)
4. **Never report "done" without check output from this session.** Never weaken
   a test to pass it. (§3)
5. **Context7 before any non-stdlib code.** Training data is stale. (§3)

**Sections by when they fire:** [1](#1-stop-and-show) before acting ·
[2](#2-verify-before-you-assert) before asserting · [3](#3-while-you-build)
building · [4](#4-when-you-report) reporting ·
[5](#5-architecture)–[8](#8-learnings) reference ([6](#6-brand) brand ·
[7](#7-deploy) deploy).

---

## 1. STOP AND SHOW

**Overrides every other instruction in this file.**

One question: **does this cost money, touch production, or is it irreversible?**

| Condition                                                            | Action                               |
| -------------------------------------------------------------------- | ------------------------------------ |
| Costs money (any paid API call)                                      | Manifest + exact cost → wait for `y` |
| Touches production (deploy, WC write, media upload, cache/CDN purge) | Show exactly what → wait for `y`     |
| Irreversible (delete / overwrite / rename real data)                 | Show exactly what → wait for `y`     |
| Everything else                                                      | **Do it.** No permission needed      |

Never ask to read files, write code, run tests, or research. Never ask "should I
proceed?" mid-plan.

### What counts

- **Money** — FASHN · Gemini / GPT-Image / FLUX / any paid image endpoint · any
  OpenAI / Anthropic / Google call with per-token or per-image cost ·
  paid-compute HF Spaces.
- **Production** — `deploy-theme.sh` or SFTP to skyyrose.co · WooCommerce REST
  writes · WP Media Library uploads · live cache flush / CDN purge.
- **Real data** — any file used as the source of a **paid** call (confirm the
  correct garment first) · uploading anywhere external ·
  deleting/overwriting/renaming real data, untracked files, or expensive assets
  (renders, 3D models, datasets).

**Allowed without asking:** reading `~/Pictures/` or Photos Library paths the
founder shared this conversation · deleting census-clean **tracked** dead code
(git-reversible, §3).

### Format

```
STOP — Confirm before proceeding:

Action : FASHN tryon
SKU    : br-001
Source : /path/to/exact/file.jpg  (81KB, 2023-10-02)
Cost   : ~$1.20  (4 models × 4 samples × $0.075)

Proceed? [y/N]
```

Literal values, not a summary. Then wait.

- **One manifest → one `y` → one call.** No batch pre-approval; approval never
  carries to the next call.
- **"Autonomous" = implementation without hand-holding AFTER the founder
  confirmed plan and inputs.** It never means picking which files to use, what
  to deploy, or which paid call to fire. "Act → apologize → act → apologize" is
  a bug.

---

## 2. Verify Before You Assert

**If you haven't read it, you don't know it.** Every claim traces to a tool call
or founder confirmation from THIS session. Say "I don't know", then how you'll
find out. Never invent.

**The verification must be able to fail.** A check that can't return "no" is a
guess with a citation.

### Pick the method by the kind of claim

| Claim                              | Method                                                                         | Gotcha                                                                    |
| ---------------------------------- | ------------------------------------------------------------------------------ | ------------------------------------------------------------------------- |
| Library / SDK / API usage          | **Context7** `resolve-library-id` → `query-docs`                               | Mandatory before non-stdlib code; training data is stale                  |
| Visual / UI / live rendering       | **Chrome DevTools** or **Playwright MCP**, mobile **and** desktop              | Eyes-on, not an HTTP code                                                 |
| Live HTML / JSON-LD / OG / headers | `curl -s "URL?cb=$(date +%s)" \| grep`                                         | **NEVER WebFetch** — strips `<script>`. Cache-bust: Batcache serves stale |
| Codebase facts                     | **Read / Grep / Glob**, quote `file:line`                                      | `anatomy.md` first; code may have moved                                   |
| Product facts (SKU, price, name)   | **catalog CSV** + per-SKU **dossier**                                          | Canonical only (`SOT.md`). Memory rots; the CSV doesn't                   |
| Imagery ownership                  | product → `sot-images.json` (`make sot-manifest`); else `visual-manifest.json` | **Filenames are not identity** — the manifest is                          |
| What a render shows                | **Read the image** (vision); `identify` for metadata                           | One-shot batch quota — batch, never retry                                 |
| Prior work                         | **mem-search** / `get_observations([IDs])`                                     | Check before re-deriving; cite obs IDs                                    |
| Integration up-or-down             | a real `verify_connectivity()` call                                            | Don't declare blocked OR working without proof                            |
| Test pass/fail                     | `rtk proxy pytest …` + read output                                             | Bare pytest can falsely say "no tests collected"                          |
| WP deploy result                   | `curl` (200, ≥50KB, no PHP-error markers) **+ Playwright**                     | Cache-bust the curl; eyes-on after                                        |

Also: `pip show` / `npm ls` before assuming a dep exists · `gh search code`
before writing net-new.

### Evidence-scope tags — ALWAYS ON

_(founder-mandated 2026-07-24, bug-287)_

The matrix says _how_ to verify. This fires when you **write the sentence** —
where verification actually failed. Tag every load-bearing claim (anything
changing the founder's decision, priority, or next action):

| Tag          | Means                                               |
| ------------ | --------------------------------------------------- |
| `[live]`     | probed production this session                      |
| `[repo]`     | read source / working tree                          |
| `[repro]`    | ran it and observed                                 |
| `[test]`     | a check that executed and could have failed         |
| `[docs]`     | Context7 / vendor                                   |
| `[inferred]` | reasoned, NOT observed — **never carries severity** |

**Evidence scope must cover claim scope.** BANNED without their own probe:

| Jump                                         | Needs                                                |
| -------------------------------------------- | ---------------------------------------------------- |
| repo / committed state → live behavior       | `curl` or Playwright vs production                   |
| static-analysis finding → runtime behavior   | a minimal repro that executes                        |
| tool listing / output → filesystem truth     | `find` / `stat`                                      |
| register, todo, or audit doc → current state | re-verify (~25% of audit claims are false positives) |

**Severity requires a probe.** "production bug", "critical", "broken" require
`[live]`. **State scope before severity** — "the committed file is stale;
production unverified", not "found a real production bug". Examples:
`tasks/lessons.md` → 2026-07-24 scope-jump.

**A gate that dies is not a gate that passed.** If a verification stage errors,
times out, or hits a session limit, its zero-findings output is an _artifact_,
not a result — re-verify by hand. Treating it as "nothing found" is the
fail-open pattern (bug-230).

### Imagery QC — blocking

**Product-image fidelity.** Before you render, create content, or edit
skyyrose.co: every product image touching the site is eyes-on verified as the
_correct garment for that SKU_ — **read the pixels, not the filename or
manifest**. New renders are **OAI gpt-image-2 only**. Can't confirm SKU ↔
garment? Do NOT render / publish / deploy. _Wrong-garment imagery is the #1
recurring defect — lh-005 fanny-pack hallucination, never-made renders leaking
onto cards._

**QC against the real reference, never a description** _(bug-276)_. Verified
ONLY side-by-side against the authoritative source, detail-for-detail:

| Subject   | Reference                                                                    |
| --------- | ---------------------------------------------------------------------------- |
| Garment   | `assets/products/references/{sku}-*real*front*`, else techflat — never prose |
| Character | `assets/branding/mascot/skyy-canonical-reference.jpeg`                       |
| Lettering | its canonical asset                                                          |

- **"Looks like a plausible SIG/BR/LH/KC look" is NOT a pass.** Checking against
  your memory of the collection is the lenient-QC defect that ships
  hallucinations — _cost 16cr of bad hero clips_.
- Binds animation too: identity must hold _across the clip_, not just frame one
  (seedance drifts).
- No side-by-side = not verified = do NOT advance, assemble, upscale, or ship.
- **Full-res only.** Never judge a render from a contact sheet.

---

## 3. While You Build

### Context7 first — every task, no exceptions

Before ANY code touching an external library or API: `resolve-library-id` →
`query-docs` → verify signatures → **then** code. google-genai, httpx, Pydantic,
LangGraph, FastAPI, WooCommerce REST — everything non-stdlib. Skipping costs
more tokens fixing wrong usage than the lookup saves.

### The loop

1. Write the change — read existing code first; `Edit` targeted, `Write` for new
   files only.
2. Run the checks: tests, linter, type checker.
3. Fails → read the error, fix the **cause**, back to 2.
4. Max 5 attempts.

**Stop when:** all checks pass (report done _with_ the passing output) · 5
attempts used (report what still fails and what you tried) · **same error twice
in a row — stop, you're guessing.**

**Never report "done" without check output from this session. Never fix a test
by weakening it.**

TDD RED → GREEN → IMPROVE · `pytest -v` after every change, 85%+ coverage ·
`isort . && ruff check --fix && black .` · after any correction, commit fix +
lesson together (`tasks/lessons.md` behavioral, `docs/engineering-learnings.md`
engineering, `.wolf/buglog.json`).

### Attribution — prove a finding is yours before you fix it

An **already-failing** gate cannot detect new regressions by pass/fail alone,
and a large baseline hides small deltas in the total. To attribute honestly, run
the _same_ gate against the pristine pre-change tree:

```bash
git archive HEAD <path> | tar -x -C <scratch>   # + symlink vendor/ or node_modules/
```

Never `git stash` for this — the stash stack is shared across worktrees (§3,
shared-worktree discipline). Also: when a check FAILS, diff its _contents_, not
just its state — a new violation hides as one more line inside an already-red
check.

### Think before coding

- **Simplicity first.** Minimum code that solves it. No speculative features, no
  abstractions for single-use code, no error handling for impossible cases. 200
  lines that could be 50 → rewrite. _"Would a senior engineer call this
  overcomplicated?"_
- **Surgical changes.** Touch only what the request requires. Don't improve
  adjacent code, don't refactor what isn't broken, match existing style. Remove
  only what YOUR change orphaned; flag pre-existing dead code, don't delete it
  unasked. **Every changed line traces to the request.**
- **State assumptions.** Multiple interpretations → present them, don't pick
  silently. Simpler approach exists → say so and push back.
- **Goal-driven.** "add validation" → "write tests for invalid inputs, then make
  them pass". Multi-step work gets a `verify:` check per step.

### Code rules

- Files < 800 lines · functions < 50 lines
- Immutability: `{...obj, key}`, never `obj.key = val`
- No hardcoded secrets — env only (`.env`, `.env.wordpress`, `.env.secrets`)
- No `TODO` / `FIXME` / `pass` / `raise NotImplementedError` in delivered code
- **npm, not pnpm, for Vercel deploys** — `ERR_INVALID_THIS` on Node 22+
- Commits: `<type>: <description>` — feat, fix, refactor, docs, test, chore
- **Fix everything in one batch, test all pages, deploy ONCE.** No drip-deploys.

### Deletion — repoint-first, census-gated

Dead / duplicate / conflicting code SHOULD be deleted, not left to rot — but
**never before a census** (grep importers incl. tests, downstream, and
cross-language string refs) proves zero live consumers. Then delete the artifact
**and** every now-dead consumer and dangling reference in the SAME change. **A
deletion that leaves a surviving import is a regression, not a cleanup.**

| Lane (reversibility × regeneration cost)            | Action                                         |
| --------------------------------------------------- | ---------------------------------------------- |
| Census-clean **tracked** code                       | Delete now — git restores it                   |
| Untracked build/cache junk                          | **gitignore, don't `rm`**                      |
| Expensive/paid asset (renders, 3D models, datasets) | **STOP-AND-SHOW** — regeneration is real money |

`rm` of untracked files and git-history rewrites are always STOP-AND-SHOW.

### Shared-worktree git discipline

One worktree = one HEAD, and multiple sessions (Ralph loop + foreground) can
commit to the SAME branch.

- **NEVER `--amend` / `reset` / `rebase` in a shared worktree.** HEAD may have
  advanced to another session's commit, so `--amend` rewrites THEIR work —
  _symptom: your staged file folds into their commit._
- New commits only. Re-check `git log -1` first.
- **`git add` + `git commit` commits the ENTIRE index** — check
  `git diff --cached --stat`, prefer `git commit -- <paths>`.
- **Never bare `git stash` / `git stash pop`** — the stack is shared; you could
  pop another session's work. Note `lint-staged` stashes during pre-commit
  hooks: verify your tree survived after each commit.
- Real isolation → separate `git worktree` (EnterWorktree).
- Stop test-gate (`.claude/hooks/stop-test-gate.sh`) is worktree-aware: gates
  only the stopping session's `cwd`, retries once (`pytest --last-failed` after
  5s), blocks only on reproduction.

---

## 4. When You Report

### Communication

**Never:** "I'll now…" · "Let me…" · "Great!" / "Certainly!" / "Of course!" · "I
hope this helps" · "Let me know if you need anything else" · "I apologize for
the confusion" (fix it, don't announce it) · preamble before the answer ·
summary after it unless asked.

**Always:** the answer first · what you did, one line, after doing it · "I don't
know" plus how you'll find out · "Wrong approach — here's why, and here's the
correct path".

**Answers:** name the uncertainty _and_ commit to a best answer. Never a
confident wrong answer; never a hedged correct one. One clear answer beats three
caveated maybes.

**Deliverables** are production-ready — not a draft, not a POC, not "good enough
for now." Configs complete; placeholders only where the founder fills them,
clearly marked. Code follows existing patterns and is tested or testable; if
not, say why. **Blocked on part of it?** Deliver the rest, name precisely what's
blocked — never a disclaimer-only punt.

### Tool use

- **WebSearch** only when the answer depends on current state, or you need a
  URL/version/spec that could have changed. Never for this codebase (read the
  code), never "just to be sure", never twice for the same thing.
- **Scale effort to the task.** Trivial → one shot. Hard → thorough and parallel
  until genuinely answered. Never a lazy pass on a hard problem, never
  over-engineering a simple one.

### After a mistake

Fix it → one sentence on what was wrong → one sentence on what prevents
recurrence → record it (`tasks/lessons.md` / `docs/engineering-learnings.md` /
`.wolf/buglog.json`, committed with the fix) → move on.

**Don't** apologize repeatedly, re-explain at length, or ask if the fix is
acceptable before showing it.

### Task execution

- **3+ steps:** plan into `tasks/todo.md` (checkboxes) → state it in one
  paragraph, get confirmation → execute uninterrupted → mark items as you go →
  close with what changed and how to verify.
- **Single-step:** just do it.
- **Ambiguous:** state your interpretation and execute against it — don't ask
  what a reasonable assumption resolves.

---

## 5. Architecture

AI-driven luxury fashion e-commerce (SkyyRose).

| Surface             | Host               |
| ------------------- | ------------------ |
| **skyyrose.co**     | WP storefront      |
| **devskyy.app**     | dashboard (Vercel) |
| **api.devskyy.app** | FastAPI (Fly)      |

Dependency flow:
`core → security → database/llm → orchestration/services → agents → api`

**Workspaces are self-contained:**

| Workspace  | Runtime     | Root               | Setup                                                                                    |
| ---------- | ----------- | ------------------ | ---------------------------------------------------------------------------------------- |
| Python API | 3.11+       | `/`                | `make install`, `make dev`                                                               |
| Dashboard  | Node 22     | `frontend/`        | `npm install`, `npm run dev`                                                             |
| WordPress  | PHP 8.2     | `wordpress-theme/` | deploy only                                                                              |
| Imagery    | Python 3.13 | main `.venv/`      | `requirements-imagery.txt`; engine `scripts/oai_render/` (paid `generate` needs `--yes`) |
| ADK        | —           | `.venv-agents/`    | `pip install google-adk`                                                                 |

**Don't** mix `frontend/node_modules` with root. **Don't** use `.venv` for ADK —
_numpy conflicts_; create `.venv-agents/`.

Scoped `CLAUDE.md` files auto-load under `agents/`, `api/`, `database/`, `llm/`,
`frontend/`, `docs/`, `skyyrose/elite_studio/`, and the theme — read those for
subsystem rules.

### WordPress theme

Structure, the `.min` build rule, escaping/nonce conventions, PHPCS →
`wordpress-theme/skyyrose-flagship/CLAUDE.md` (auto-loads under the theme). Text
domain `skyyrose` · version = `SKYYROSE_VERSION` in `functions.php`.

Commands (build · deploy · lint:php · verify:theme · SSH key/host) → theme
`CLAUDE.md` → "Build commands". `npm run deploy` is STOP-AND-SHOW; `deploy:dry`
previews.

Python API and Dashboard: read `Makefile` / `frontend/package.json`.

---

## 6. Brand

**Tokens** — Rose Gold `#B76E79` (global accent, Kids Capsule) · Dark `#0A0A0A`
(background) · Silver `#C0C0C0` (Black Rose) · Crimson `#DC143C` (Love Hurts) ·
Gold `#D4AF37` (Signature).

Tagline "Luxury Grows from Concrete." · Collections: Signature, Black Rose, Love
Hurts, Kids Capsule.

**Fonts** — **Archivo** (display/hero, `font-variation-settings 'wdth' 125`) ·
**Hanken Grotesk** (body/UI) · **Anton** (drop/UI accent) · **Cinzel** (engraved
caps) · **Inter** (fallback). Per-collection scripts: **SkyyRose Black Rose
Script** (BR, bespoke, replaced Pacifico) · **SkyyRose Love Hurts Graffiti**
(LH, bespoke, replaced Kaushan) · **Pinyon Script** (SIG) · **Grand Hotel**
(KC).

**Cut 2026-07-10 — do NOT reintroduce:** Playfair Display, Cormorant Garamond,
Bebas Neue, Yellowtail. _Not in any brand lockup; they pull toward the
European-serif lineage the founder locked out._

Self-hosted woff2, zero CDN, declared in `theme.json` Font Library +
`assets/css/fonts.css`. `--skyyrose-font-*` vars generate from
`data/brand/typography.json` via `gen-design-tokens.py`.

**Contrast is a brand constraint, not just an a11y one.** Brand crimson
`#DC143C` is only 3.63:1 on `#0A0A0A` — below WCAG AA for body text. Use it for
fills/borders/glows; use `--color-text-muted` (#B3B3B3, 9.44:1) for
de-emphasised text. Never low-alpha white as a "muted" shorthand — measure it.

---

## 7. Deploy

All targets are STOP-AND-SHOW (§1).

| Target       | Command                                                                                    | Config                                    |
| ------------ | ------------------------------------------------------------------------------------------ | ----------------------------------------- |
| WordPress    | `bash scripts/deploy-theme.sh`                                                             | `.env.wordpress`                          |
| WP MU-plugin | `STOPSHOW_ACK=1 [MU_SRC=wordpress/mu-plugins/<file>.php] bash scripts/deploy-mu-plugin.sh` | `.env.wordpress` (dest = source basename) |
| Frontend     | `cd frontend && npm run deploy`                                                            | `vercel.json`                             |
| API          | `docker compose up -d`                                                                     | `docker-compose.yml`                      |
| HF Spaces    | `bash scripts/deploy_hf_spaces.sh`                                                         | `.env`                                    |

### Theme deploy gotchas (full procedure, inputs, verification: `/wp-deploy` skill)

- **Atomic hot-swap**: production loses any file the source lacks (bug-252).
  Rider manifest + census method → `docs/engineering-learnings.md`
  "Deploy-source completeness". `preflight_completeness()`
  (`scripts/deploy-theme.sh:313`) checks **git-tracked** files only; the 3
  untracked `*-v2-avatar.webp` scene riders pass silently (`git add -f` puts a
  rider under the gate).
- **Version bump is deploy-correctness**: `SKYYROSE_VERSION` is the cache-bust
  param on ~52 enqueue calls; ship changed CSS/JS without bumping the triple
  (`functions.php`, `style.css`, `readme.txt`) and returning visitors get stale
  assets.

---

## 8. Learnings

Grep before re-deriving a fix. Engineering → **`docs/engineering-learnings.md`**
· behavioral → **`tasks/lessons.md`**.

**Memory discipline (mandatory):**

- Check `~/.claude/projects/*/memory/MEMORY.md` at the start of every task — not
  just fixes. Don't re-derive what a past session already established.
- Sync memory after every session, and **immediately** (not batched) after
  anything touching production.
- Keep `MEMORY.md` one line per entry; merge/prune stale entries.
- `/efficient-production` discipline: terse, no padding, verifiable.

<!-- prettier-ignore-start -->
<!-- wolf:recurring:start -->
### Recurring issues (synced from `.wolf/buglog.json` — regenerate via `python scripts/wolf_recurring_sync.py`, do not hand-edit)
- **bug-096** (×30, 2026-05-08): Tripo generate_multiview_image hallucinated brand canon on 30 SKUs (120 renders… → fix: scripts/tripo_dispatch.py — added classify_skus() function that blocks at the d…
- **bug-172** (×24, 2026-06-30): OpenAI gpt-image-2 images.edit() call returns 400 'The model gpt-image-2 does n… → fix: FIXED 2026-06-30: config.py defines INPUT_FIDELITY_SUPPORTED_MODELS = {gpt-imag…
- **bug-263** (×8, 2026-07-31): SIGSEGV (EXC_BAD_ACCESS) 'crashed on child side of fork pre-exec' — 12+ Python… → fix: conftest.py + scripts/ci-local.sh: on darwin set no_proxy='*'/NO_PROXY='*' (set…
- **bug-230** (×7, 2026-08-01): PATTERN: fail-open guards / silent fallbacks — gates that pass when their input… → fix: Rule: every gate fails CLOSED — absent manifest/config/token = block, exception…
- **bug-231** (×5, 2026-07-16): PATTERN: test isolation / shared-state pollution — tests failing only in full-s… → fix: Rule: per-test tmp_path (never hardcoded /tmp), monkeypatch.setenv/delenv (neve…
- **bug-098** (×4, 2026-05-12): DATA-01: /collection-black-rose/, /collection-love-hurts/, /collection-signatur… → fix: Bumped SKYYROSE_SETUP_VERSION constant from '4.0.0' to '4.1.0' in inc/theme-act…
- **bug-257** (×2, 2026-07-13): Stop-gate: tests/test_asset_manifest.py::test_manifest_exists_and_loads fails i… → fix: Centralized guard in tests/sparse_guard.py: requires_tree(rel) skips ONLY when…
- **bug-287** (×2, 2026-07-24): Reported a stale repo-side style.min.css as 'a real production stale-serve defe… → fix: Evidence-scope rule in tasks/lessons.md: tag load-bearing claims inline ([repo]…
- **bug-327** (×2, 2026-09-17): wolf-memory (CONNECTION_CLOSED) and worktree-fleet (CONNECTION_CLOSED) MCP serv… → fix: Changed the `command` for wolf-memory and worktree-fleet in .mcp.json from `pyt…
- **bug-332** (×2, 2026-09-18): Pre-commit lint-staged/prettier reformatted derived and vendored assets, and th… → fix: Added `**/*.min.js`, `**/*.min.css` and `wordpress-theme/skyyrose-flagship/asse…
- **bug-333** (×2, 2026-09-18): Stop-gate blocked: tests/api/test_brand_assets.py::TestBulkIngestion::test_bulk… → fix: NOT FIXED -- pre-existing and unrelated to the session's product-SOT work (the…
<!-- wolf:recurring:end -->
<!-- prettier-ignore-end -->
