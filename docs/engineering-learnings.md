# Engineering Learnings

> Extracted from `CLAUDE.md` on 2026-06-16 to shrink per-session context. This is a searchable knowledge base, not per-turn behavioral rules. **Grep this before re-deriving a fix.**


### Architecture
- `agents/base_super_agent/agent.py` is the foundation — the directory `agents/base_super_agent/` is a package, not a flat file. (Cerebrum: never create `agents/base_super_agent.py` as a flat file; Python silently ignores the .py if the package exists.)
- DataLoaders → `api/graphql/dataloaders/` (not `core/`)
- Integration tests → `tests/integration/` (not `tests/api/`)

### Python Packaging
- Every top-level package directory MUST contain `__init__.py`. No implicit namespace packages. `mypy.ini` has `namespace_packages = False` to enforce this.
- Why: implicit namespace packages let mypy resolve the same `.py` file under two module names (e.g., `preflight` and `renders.preflight`), producing "Source file found twice under different module names" errors that silently block commits.
- If you add a new top-level package dir (e.g., `newthing/`), add `newthing/__init__.py` in the same commit — even if empty, a one-line docstring is fine.
- `.claude/worktrees/` are LIVE git worktrees (per `git worktree list`). Pre-commit's `mypy . --ignore-missing-imports --exclude '\.claude/'` keeps duplicate file paths out of module discovery.

### Google ADK
- Agent names: underscores only (valid Python identifiers)
- Loop per-product with `time.sleep(8)` to avoid 429s
- Use `.venv-agents/` (ADK conflicts with numpy)

### Security
- Validate backend URLs against allowlist; block `169.254.x.x`, `file://`, `gopher://`
- Cap in-memory tracking with LRU eviction
- Whitelist config keys before `**unpacking`
- No `innerHTML` in JS — all DOM construction via `createElement`

### WordPress
- CDN caches CSS aggressively — bump `SKYYROSE_VERSION` or use `?nocache=` to verify
- `enqueue.php` template slug map must match actual template filenames exactly
- Collection pages use unified `collection-pages.css` + `collection-pages.js` (one CSS replaces 4 separate files)
- Collection pages use `col-*` classes with `data-collection` attribute for palette switching via CSS custom properties
- Collection pages use IntersectionObserver scroll-reveal (`.col-reveal`), NOT GSAP — GSAP only for preorder/about/immersive
- Holo card grid: only `.product-grid`, `.product-grid__items`, `.br-product-grid__items` should be `display: grid`
- Don't duplicate content sections — if showcase cards show collections, don't add separate narrative cards with same data
- Showcase card content should be visible by default (`opacity: 1`), not hidden until hover — mobile has no hover
- When removing a PHP section, also remove its CSS rules AND responsive breakpoint overrides
- Premium animation system: `animations-premium.css` + `premium-interactions.js` loaded globally — use `rv-clip-*`, `rv-blur*`, `rv-split-*`, `stagger-grid`, `magnetic`, `btn-sweep`, `btn-border-draw` classes
- `php-lint.sh` needs explicit Homebrew PHP path (`/opt/homebrew/bin/php`) — lint-staged subshell doesn't inherit brew paths
- Image cache-bust: append `?v=' . SKYYROSE_VERSION` to branding image URLs in templates
- Cursor disappearing: caused by Jetpack Instant Search invisible overlay (z-index max, opacity 0, pointer-events auto) — fix with `pointer-events: none !important` in design-tokens.css
- `front-page.php` uses its own inline footer (`.ft` class) + `wp_footer()` instead of `get_footer()` — shared template parts (mobile-nav, cookie-consent, size-guide, toast-container) must be manually included before `wp_footer()`
- Jetpack Instant Search hijacks search results with a white overlay — our custom `search.php` only renders when Instant Search is disabled
- Any new template part added to `footer.php` must ALSO be added to `front-page.php` before `wp_footer()`
- Landing pages use `lp-*` classes with `[data-collection]` palette switching (same pattern as collection pages but `--lp-*` CSS vars)
- Landing pages use `.lp-rv` scroll-reveal (IntersectionObserver) — NOT `.col-reveal` or GSAP
- Landing page templates registered as slug `'landing'` in enqueue.php — loads `landing-pages.css` + `landing-pages.js` + holo cards
- Hero overlays live in `assets/images/hero-overlays/` (deployed with theme) — source PNGs in `assets/techflats/hero-overlays/` (repo root)
- Landing page template parts in `template-parts/landing/` accept `$args` arrays: hero.php, product-grid.php, faq.php
- Product grid template part pulls from `product-catalog.php` by SKU array — if SKU not in catalog, card is silently skipped
- **Theme name is "SkyyRose"** (not "SkyyRose Flagship") — text domain is `skyyrose`, @package is `SkyyRose`, folder stays `skyyrose-flagship/` for deploy compat
- **Version source = `SKYYROSE_VERSION`** in `functions.php` — style.css and readme.txt sync to it; never hardcode a release number in docs (check the constant, don't assume)
- **PHPCS WordPress standard enforced** — `.phpcs.xml` in theme root, run `vendor/bin/phpcs` before commits. Composer installed at `~/.local/bin/composer`
- Leading-underscore functions (`_skyyrose_*`) renamed to `skyyrose_*` — WPCS requires theme prefix without underscore
- `skyyrose_nav_fallback()` (was `skyyrose_flagship_nav_fallback()`) — used as fallback_cb in header.php wp_nav_menu calls
- Builder detection: `skyyrose_active_builder()` returns slug ('elementor'|'divi'|'beaver-builder'|'bricks'|'gutenberg')
- Block patterns registered in `inc/patterns.php` — pattern files in `patterns/` directory
- Store API v1 cart was in `assets/src/js/cart.js` (268L, exposed `window.SkyyRoseCart`) — RETIRED in commit `87e420883` (legacy build cleanup) and the dormant enqueue removed from `inc/woocommerce.php` on 2026-04-27. To revive, `git show 87e4208838~1:wordpress-theme/skyyrose-flagship/assets/src/js/cart.js > <path>` and re-add the `wp_enqueue_script` block.
- Brand palette helper is **`skyyrose_brand_colors()`** (12 keys: rose_gold, gold, crimson, silver, dark, deep_black, deep_red, purple, navy, deep_blue, soft_pink, lavender) in `inc/brand-colors.php:41`. Do not invent `skyyrose_brand_palette()` — it doesn't exist. Builder palette callbacks pull hex values from this helper; only `#FFFFFF` (white) stays inline since white isn't part of the brand.
- Builder integrations (Divi, Beaver, Bricks) use a shared scaffold: `skyyrose_register_builder_compat($slug, $config)` in `inc/builders/shared.php`. Each builder file passes a `theme_support` callback and a `palette_callback` that receives `skyyrose_brand_colors()` plus the hook's args. Elementor keeps its richer integration inline (widgets, breakpoints, schemes, Google-Fonts disable) but calls `skyyrose_brand_colors()` for the schemes hex values.
- **`design-tokens.css` is enqueued globally** by `inc/enqueue.php:71-76` at priority 10 inside `skyyrose_enqueue_global_styles()`. Per-builder enqueues are forbidden — `wp_enqueue_style('skyyrose-design-tokens', ...)` should appear in `inc/enqueue.php` only. The `skyyrose-product-card-holo` enqueue inside `inc/builders/elementor.php:127` is allowed because it's Elementor-frontend-conditional, not redundant.
- Bootstrap order in `functions.php:118-148` matters: `detection.php` → `shared.php` → builder-specific files. The shared helper must load before the four builder files since they call `skyyrose_register_builder_compat()` at file-include time.
- **Per-collection palette is owned by `assets/css/design-tokens.css`** under `:root` (default) + `[data-collection="signature"|"black-rose"|"love-hurts"]` selectors. Tokens: `--skyyrose-accent`, `--skyyrose-accent-rgb`, `--skyyrose-accent-dark`, `--skyyrose-secondary`, `--skyyrose-bg`, `--skyyrose-text`, `--skyyrose-text-muted`, `--skyyrose-font-display`, `--skyyrose-font-body`, `--skyyrose-font-mono`, `--skyyrose-font-ui`, `--skyyrose-ease`, `--skyyrose-radius`. Feature CSS (`landing-pages.css`, `system/animations-premium.css`) and PHP inline styles consume these via `var(--skyyrose-*)` directly — no `--col-*` or `--lp-*` aliases exist. To add a new collection: add a `[data-collection="<new-slug>"]` block to design-tokens.css and emit the attribute on the page wrapper. Retired in U-4 (2026-05-04); do not reintroduce the legacy aliases.
- **Single scroll-reveal IntersectionObserver** lives in `assets/js/premium-interactions.js` inside the IIFE. Selector list managed via the `revealSelectors` variable: `.rv-clip-{up,left,right,diagonal}, .rv-blur, .rv-blur-down, .stagger-grid, .rv-split-{char,word,line}, .col-reveal, .lp-rv, .abt-page .rv`. Toggles `.is-visible` once per element, then `unobserve`s. Threshold `0.12`, rootMargin `0px 0px -40px 0px`. Reduced-motion early-return forces `.is-visible` on all matching elements. To add new reveal classes: extend `revealSelectors` (single source of truth shared by both the Motion One inView() path and the IntersectionObserver fallback). Per-page reveal observers were retired in U-1 (2026-05-04); `landing-pages.js` and `about.js` no longer have local observers. **Exception (intentional):** `assets/js/homepage-v2.js` keeps its own front-page observer — different class (`.vis`), no `unobserve`, separate semantics. Other observers in the theme (product-card-holo entrance stagger, experience-analyzer, preorder-gateway, single-product, page-transitions prefetch, experiences/* 3D scene) serve different purposes and stay separate.
- **About page reveal CSS lives in BOTH `about.css` source AND `about.min.css`** as of U-1. Pre-existing source/min drift was repaired during U-1 — `.abt-page .rv` and `.abt-page .rv.is-visible` rules are now in source. The toggled state class changed from `.vis` to `.is-visible` to align with the unified observer.
- **Theme page creation is one-shot, gated by `SKYYROSE_SETUP_VERSION`** (`inc/theme-activation-setup.php`). Init hook (`add_action('init', ..., 30)`) calls `skyyrose_run_activation_setup()` exactly once per setup version — gate: `if (get_option('skyyrose_activation_setup_version') === SKYYROSE_SETUP_VERSION) return;`. To re-create theme-owned pages that were deleted from WP admin, bump the constant in source. Next request fires `wp_insert_post()` for any missing slug returned by `get_page_by_path()`, assigning `_wp_page_template` meta. Bumped `4.0.0 → 4.1.0` on 2026-05-12 (theme 1.1.2, commit `016f7025f`) to fix DATA-01 where all four `/collection-{slug}/` URLs were serving page-id-9822 (homepage) because the collection pages had been deleted. Post-deploy: pages now resolve to page-id 9454/9455/9456/9651. **DO NOT touch the DB or ask the user to re-create pages manually — bump the constant.**
- **Cursor/global enqueues that must vary by template gate on `skyyrose_get_current_template_slug()`.** Helper defined in `inc/enqueue.php`, maps `template-immersive-*.php → 'immersive'`. Any enqueue inside `skyyrose_enqueue_global_scripts()` (priority 10, every page) that should be suppressed on immersive must wrap in `if ('immersive' !== skyyrose_get_current_template_slug()) { wp_enqueue_script(...); }`. **CURS-03 fix** (theme 1.1.2, commit `016f7025f`): `skyyrose-luxury-cursor` enqueue at `inc/enqueue.php:247-263` was unconditional; cursor JS shipped to immersive pages where the cursor is CSS-hidden. Now gated; cursor JS no longer downloads on `/experience-{slug}/` URLs. If an asset is CSS-hidden on a template, the JS enqueue should also be suppressed — don't ship dead bytes. The slug helper is the project's canonical mechanism; do not introduce parallel `is_page_template()` checks.

- **Sherpa render identity (2026-06-10, founder-confirmed):** the red-rose closed-jacket render mis-filed at `black-rose-sherpa-jacket/black-rose-sherpa-jacket-front-model.webp` is the SIGNATURE Sherpa — renamed to `signature-sherpa-jacket-front-closed.webp` and wired as sg-009 `front_model_image` (was ghost). br-006's true front model = flat `black-rose-sherpa-jacket-front-model.webp` (hooded satin, silver rose). Never reuse `black-rose-sherpa-jacket/` subdir filenames as identity evidence — verify the pixels.

### WordPress Deploy
- Dirty working tree on main blocks `git merge` — always stash unrelated changes before merging worktree branches
- `mv: preserving permissions` warnings during deploy are cosmetic (WordPress.com hosting restriction) — files transfer correctly
- After deploy: verify HTTP status on homepage + search + 404 + cart + shop AND verify new asset URLs return 200
- Search page uses `'search'` slug in `enqueue.php` — must come BEFORE the `is_home() || is_archive() || is_search()` blog catch-all
- Size guide modal, cookie consent, mobile nav are all `get_template_part()` calls in `footer.php` — order matters (size guide → cookie consent → mobile nav → toast container)
- Pre-order functions extracted to `inc/woocommerce-preorder.php` — woocommerce.php no longer has pre-order meta boxes
- `toast.js` provides global `window.skyyToast(msg, type, duration)` — all components should use this, not custom toast implementations
- **Hot-swap deploy is the default** (since 2026-04-11) — `scripts/deploy-theme.sh` uses atomic mv on the remote (`mv current → .old.$ts; mv new → path`) instead of the old `wp maintenance-mode` + `rm -rf && mv` pattern. The swap window is microseconds instead of ~60 seconds, so Jetpack Uptime stops firing false-positive "site is down" alerts on every deploy. Pass `--with-maintenance` only when deploying DB migrations or plugin changes that require the site to be locked.
- **Deploy script has a post-verify gate** — `verify_live()` curls `https://skyyrose.co/?deploy_verify=$ts` after cache flush and asserts HTTP 200, response size >= 50 KB, and absence of PHP error markers (`Fatal error`, `Parse error`, `Call to undefined`, `There has been a critical error`). Deploy exits non-zero on failure. Override target URL via `PUBLIC_URL` env var.
- **Jetpack Uptime alerts during deploy are a lagging indicator** — if one fires immediately after a deploy, it almost always points at a 503 window from `--with-maintenance` mode. Ignore the first alert within ~5 min of a legacy maintenance-mode deploy; investigate only if Jetpack's next poll cycle still reports down.

### Audit Discipline
- **[2026-05-24] WebFetch strips `<script>` tags during HTML → Markdown conversion. Never use it to audit JSON-LD, OpenGraph script blocks, inline JS, or any content inside `<script>`.** Use `curl -s URL | grep` or `curl -s URL | grep -oE '<meta property="og:..."'` instead. **Why:** the 2026-05-23 SEO audit reported "zero JSON-LD on all 4 pages, OG tags absent" as a P0 finding. Live curl + grep showed 2 JSON-LD blocks per page (Product, BreadcrumbList, ItemList, Organization) + full OG markup. The audit agent had used WebFetch which stripped both. Cost: ~1500 tokens of bad analysis + a near-miss on shipping a "fix" for a non-bug. **How to apply:** any structured-data audit agent brief must explicitly forbid WebFetch and require curl + grep for inspection.
- **[2026-05-24] WP.com Batcache serves stale HTML for ~minutes after `wp cache flush`. Always cache-bust post-deploy verifies with a unique query param.** Use `curl -s "https://skyyrose.co/?cb=$(date +%s)"` not `curl -s https://skyyrose.co/`. **Why:** PERF-03 from the audit was reported as a real bug because un-cache-busted curl showed `<div style="background-image">` (pre-deploy markup), but the deploy had already shipped the v1.5.17 LCP refactor with `<picture><img fetchpriority="high">`. Cache-busted curl confirmed source matched live.
- **[2026-05-24] Cerebrum claim "All innerHTML Uses Cleared" (obs #6378) is stale.** As of theme v1.1.2, `assets/js/smart-showcase.js:34,107,115` and `assets/js/immersive-wc-bridge.js:56` still have active `innerHTML` writes. Two HIGH security findings open per security-audit.md. Fix path: `createElement` for the hardcoded template, `DOMParser.parseFromString` for the WC AJAX fragment parse.
- **[2026-05-24] aos/cognition/reflector.py `classify_failure` is the public name (renamed from `_classify_failure`).** `aos/kernel/kernel.py:466` imports and calls it. Helpers used cross-module become public — strip the underscore.
- **[2026-05-24] WordPress Site Title canonical = "SkyyRose"** — not "The Skyy Rose Collection". Lives in wp-admin → Settings → General, propagates through every `<title>` + `og:site_name`.
- **[2026-05-24] Cart page must use `[woocommerce_cart]` shortcode, NOT Elementor HTML widget.** Theme's `woocommerce/cart/cart.php` override only renders along the shortcode path. Elementor widget content bypasses → coupon input has no backend (100% broken), "Continue Shopping" goes to homepage, checkout URL hardcoded to `/?page_id=9452`.
- **[2026-05-24] "Complete the Look" cross-sell unhooked per founder canon.** `add_action('woocommerce_single_product_summary', 'skyyrose_complete_the_look', 50)` at `inc/woocommerce.php:541` commented out. Template + function retained for one-line reactivation if revisited. Founder rule: no related products on PDP, garment is the protagonist.
- **[2026-05-24] Multi-agent audit P0 false-positive rate ~25%.** The 2026-05-23 audit reported 12 P0s; verification collapsed to 9 actionable. Always curl + grep live state before drafting any audit fix. The audit is the starting point, not the truth.
- **[2026-05-24] Cavecrew chain (investigator → builder → reviewer) compresses subagent tool-result tokens ~60-70% vs vanilla Explore + Edit + Code Reviewer.** For audit-driven sprints with 5+ delegations, this is the difference between finishing the session and hitting handoff. Don't use for prose-heavy review or architecture critique — vanilla is correct there.
- **[2026-06-15] Never count files by piping rtk-proxied git output through `wc -l` — `rtk proxy` injects display headers (e.g. `--- Changes ---`) that `wc -l` miscounts as content, inflating the number.** During the CLAUDE.md mass-deletion this produced a phantom 126-vs-123 discrepancy in staged deletions; the real count was exactly 123. **How to verify:** count by the actual path pattern with `git diff --cached --name-only --diff-filter=D | grep -c 'CLAUDE\.md$'` (or `git status --porcelain | grep -c ...`) — grep on the path matches only real entries, headers can't slip in. Also know the two removal mechanisms differ: `git rm <f>` stages a tracked file's deletion in the index (shows under `--diff-filter=D`); plain `rm -f <f>` only touches the working tree for an untracked-not-ignored file (nothing staged). A mixed-class cleanup needs both, and only the `git rm` half appears in `--cached` counts.

### Hooks (macOS)
- Canonicalize paths (`/tmp` → `/private/tmp`)
- Use `${VAR:-default}` for testable paths
- Reject flag-like targets: `case "$target" in -*) exit 0 ;; esac`

### Vercel
- `rootDirectory` set → reads that dir's `vercel.json`, not root
- **`outputFileTracingRoot` above the Vercel project root causes a doubled-path bug.** With `rootDirectory=frontend`, Vercel's project cwd is `/vercel/path1/`. If `frontend/next.config.ts` sets `outputFileTracingRoot: path.resolve(__dirname, '..')` = `/vercel/`, the post-build trace stage emits paths relative to that root (`path1/.next/...`), then Vercel re-prepends the project cwd when resolving — yielding `/vercel/path1/path1/.next/routes-manifest.json` and crashing with `ENOENT: no such file or directory`. **Fix**: gate the override on `process.env.VERCEL` so it only applies locally. On Vercel, only `frontend/` is uploaded, so the override isn't needed (no ambiguous-lockfile warning to suppress). See `frontend/next.config.ts` (PR #494, 2026-05-07).
- A failed Vercel build does NOT take production down. Vercel keeps the alias on the last green deployment when new builds fail — the site stays up serving stale code. Symptom: every recent deploy shows `state: ERROR` in `vercel list_deployments`, but `curl https://devskyy.app/` returns 200. Treat as P1 (deploy pipeline blocked) not P0 (site down).

### Frontend (Next.js 16, `frontend/`)
- **Cache Components mode (`cacheComponents: true`) requires `<Suspense>` boundaries around every request-time data reader.** That includes `usePathname()`, `useSearchParams()`, `use(params)`, `use(searchParams)`, `cookies()`, and `headers()`. Without a `<Suspense>` wrapper, the build fails with `Error: Route "X": Uncached data was accessed outside of <Suspense>. This delays the entire page from rendering, resulting in a slow user experience` and exits 1 during static prerender.
- **Two patterns to wrap them**:
  1. **Wrap at the mount point** (best for layouts that compose dynamic chrome like sidebars, mascots): in the parent layout, do `<Suspense fallback={null}><Component /></Suspense>`.
  2. **Internal split** (best for reusable components and pages): rename the original function to `*Content`, then export a small wrapper that does `<Suspense fallback={<Skeleton/>}><Content /></Suspense>`.
- For decorative chrome (sidebar, tab bar, mascot bubble), `fallback={null}` is fine — the component would render nothing pre-hydration anyway. For data-heavy pages, the fallback is a skeleton matching the eventual content shape.
- Routes that correctly use the pattern show as `◐ (Partial Prerender)` in the build's route table — that's the desired Cache Components outcome (static shell + streaming dynamic content). See `frontend/app/admin/elite-studio/operations/[id]/page.tsx` for the canonical split. (PR #493, 2026-05-07).
- **`middleware.ts` is deprecated in favor of `proxy.ts` in Next.js 16** — not removed: both conventions still resolve (`MIDDLEWARE_FILENAME` and `PROXY_FILENAME` both exist in `next/dist/lib/constants`; a lone `middleware.ts` only warns, `proxy.ts` alone is clean, and having BOTH is a hard error). The named export `middleware` → `proxy`; `export const config.matcher` is unchanged; config flags rename (`skipMiddlewareUrlNormalize` → `skipProxyUrlNormalize`). A `proxy.ts` exporting `proxy` + `config` IS the registered gate and DOES run — do NOT assume a `proxy.ts` with no `middleware.ts` means the gate is dead. (A code-review agent flagged exactly that false alarm from pre-16 knowledge; Context7 + reading the installed `next@16.2.7` package confirmed it runs.) Caveat: `proxy` runs the **nodejs** runtime — edge is NOT supported in `proxy`; keep a `middleware.ts` if you need edge. `frontend/proxy.ts` is the dashboard's auth gate. (2026-06-30)

---

### Git & Repo Hygiene
- **`.gitignore` does NOT support trailing inline comments.** `pattern  # note` is parsed as a literal pattern (a filename containing spaces and `#`), so it silently matches nothing — the rule looks "done" but ignores nothing. Comments go on their own line. Always `git check-ignore <file>` to confirm a new ignore rule actually fires. (2026-06-30)
- **Graceful-degrade vs fail-loud for a gitignored data dependency.** `skyyrose/core/asset_hub.py` reads `assets/hub/manifest.json` (gitignored) and is hard-imported by `build-collection-sot.py`. `_manifest()` catches `FileNotFoundError → {}` (absent manifest = truthful "nothing promoted yet"; every consumer degrades to None/empty, hard importers stay safe on a manifest-less env) but lets `JSONDecodeError` propagate (corrupt manifest = data-integrity failure, never silently masked). Pinned by `tests/test_asset_hub_degrade.py` (both the degrade AND the corrupt-raises case). The reusable rule: **absent is normal, corrupt is a bug.** (2026-06-30)
- **Agent SDK (`claude-agent-sdk`): `tools=[]` removes built-in tools to drop below the CLI's tool-search threshold.** Otherwise the model runs a `ToolSearch` round-trip before every custom MCP tool call (~52% extra cost, measured). `allowed_tools` is *permission* (pre-approve), `tools` is *availability* (presence); tool-search keys off availability count. **Permission ≠ presence** — pre-approving 3 tools doesn't help; you must remove the ~15 built-ins. See `devskyy-sdk-app/main.py`. (2026-06-30)


## 3D Character Animation Pipeline — hardening checklist (2026-07-06, deep-research synthesis, cited in session)

**Retarget (same-topology rigs, Blender world-space constraint-bake):**
- `transform_apply(scale=True)` on BOTH armatures BEFORE constraints (glTF imports carry 0.01 object scale; multiplying ratios into object.scale produces ~100x root-translation bake errors and glTF export round-trip bugs).
- `COPY_ROTATION` world/world with `mix_mode='REPLACE'` explicitly — other mixes double-count rest orientation (Blender #85350).
- Bake every frame (`step=1`, `visual_keying=True`, `clear_constraints=True`), then run a quaternion continuity pass per bone (seed from rest quat; `dot(q, q_prev) < 0` → negate all 4 components) — Blender bakes emit double-cover sign flips (T71924/T83351); the Euler discontinuity filter does NOT fix quaternions. Simplify curves only AFTER.
- `nla.action_pushdown()` before baking the next clip on the same armature.

**Clips for fixed-canvas web (Three.js):**
- In-place conversion at SOURCE: flatten Hips location X/Z fcurves to first value (keep Y bob); `SkeletonUtils.extractRootMotion` does not exist in shipped three.js.
- `THREE.LoopRepeat` blends NOTHING at the wrap — trim clips to true cycle boundaries or pose-match last key to frame 0.
- Trim sub-ranges via NLA strip `action_frame_start/end` + `nla.bake(use_current_action=False)` — direct keyframe surgery desyncs Bezier handles; F-curve modifiers evaluate against the old range.
- glTF import attaches CUSTOM SPLIT NORMALS — `shade_smooth` is a no-op until `customdata_custom_splitnormals_clear()`.
- gltf-transform `--compress meshopt` is unreadable by plain GLTFLoader+DRACOLoader — draco only. Draco needs self-hosted decoders + `'wasm-unsafe-eval'` in CSP script-src.

**QC (what single-frame screenshots miss):**
- Sample uniform phases PLUS gesture apexes (local maxima of per-bone angular displacement); scrub deterministically via `mixer.setTime`, never rAF deltas.
- Bone-level assertions: elbow hyperextension = 3-joint dot-product angle > ~170°; root drift = Hips XZ vs t=0; loop closure = per-bone stable quat angle `2·asin(|vec(q1·conj(q2))|)`; ALL thresholds are tunables calibrated on known-good clips — no industry constants exist.
- gltf-validator checks structure only — pose plausibility must be hand-built.
- Auto-rig face contamination: face verts pick up neck/spine/shoulder weights → face smears during motion. Fix: 100% Head-bone weights above the anatomical neck (find by cross-sectional radius scan — the neck JOINT can sit at shoulder height on chibi rigs).

## Deploy integrity — tracked view vs working tree (2026-07-07)

- **"Exists on disk" ≠ "exists after a clean-tree deploy."** `.gitignore` blanket-ignores theme webp (`wordpress-theme/skyyrose-flagship/assets/**/*.webp`), while the products dir convention is tracked-for-deploy — so a repoint PR can reference a binary that works from a dirty working tree and 404s from a clean checkout (bug-175: `br-014-giants-back.webp`, PR #724). Land referenced binaries with `git add -f` in the same change as the repoint.
- **Census against `git ls-files` / `git cat-file -e HEAD:<path>`, never `ls`.** Guard now permanent: `tests/test_sot_assets_tracked.py` sweeps data/sot-images.json + all collection sot.json + the catalog CSV and fails on any referenced-but-untracked image.
- **Parametrizing a deploy script's source requires parametrizing its destination.** `deploy-mu-plugin.sh` gained `MU_SRC` but kept a hardcoded SCP dest — deploying plugin B would silently overwrite plugin A on production (bug-174). Derive dest from `basename "$SRC"`.
- **SOT regen must use the default `--updated GENERATED` stamp** — the guard test byte-compares against default generator output; a date stamp breaks determinism by design.

## Deploy-source completeness — gitignored live riders (2026-07-13)

## Root npm audit remediation (2026-08-27)

- **Do not treat an audit threshold as a substitute for dependency repair.** Root `npm audit` reported 22 high findings through the current Jest and OpenWolf/Puppeteer toolchains even after both direct packages were at their latest available releases. The supported remediation is to remove the unpatchable dependency paths: root unit tests run under Vitest, and design QC uses the maintained Playwright path. Retain `npm run security:audit:production` in CI for runtime deployment gating, but continue to run the full audit locally and in dependency-maintenance review.
- **A committed root lockfile is part of the security control.** CI must use `npm ci`, never a fresh `npm install`, before running the audit and test gates; otherwise audit output is not reproducible from the reviewed commit.

- **The live theme dir contains 17 functional assets that exist in NO git commit** — blanket-gitignored binaries that have ridden along on every deploy from the primary checkout's working tree (`deploy-theme.sh` is git-unaware; it tars the directory on disk). The hot-swap replaces the remote dir wholesale, so **any deploy from a clean checkout / fresh worktree / CI deletes them from production** (BR/LH hero emblems vanish via `page.php`'s `file_exists` gate; mascot/avatar/scene refs 404). Overlay them into the deploy source first, or `git add -f` them (preferred, per the 2026-07-07 rule above).
- **Rider manifest (verified against the live server listing, 2026-07-13):**
  - `assets/images/emblems/black-rose-emblem.png` + `.webp`
  - `assets/images/emblems/love-hurts-emblem.png` + `.webp`
  - `assets/images/mascot/skyy-canonical-v2.png`
  - `assets/images/avatar/skyy-rose-reference.avif` + `.jpeg` + `.webp`
  - `assets/scenes/black-rose/black-rose-rooftop-garden-lookbook.webp` + `black-rose-rooftop-garden-v2-avatar.webp` (note: the v2-avatar file drops the `-lookbook` infix — do NOT curl `…-lookbook-v2-avatar.webp`, it 404s)
  - `assets/scenes/love-hurts/love-hurts-cathedral-rose-chamber-lookbook.webp` + `love-hurts-cathedral-rose-chamber-v2-avatar.webp`
  - `assets/scenes/signature/signature-golden-gate-showroom-lookbook.webp` + `signature-golden-gate-showroom-v2-avatar.webp`
  - `assets/images/products/br-008-front-only.jpg`
  - `data/product-references/techflat-review.json` + `techflat-vision-analysis.json`
  - `assets/branding/tsrc-lockup-static@2x.webp` + `tsrc-lockup-rotating@2x.webp` — discovered 2026-07-19 (header lockup poster/fallback + rotating variant; live-only until then, absent from the 2026-07-13 census). Pulled from live (byte-verified 5,854 / 636,270 B) and `git add -f` tracked with the v1.12.0 sweep, so the ls-files completeness gate now protects them.
- **Proof this bites:** live 1.10.3 was deployed from a source missing the *tracked* `signature-emblem.webp` (committed `700d43178`) → Signature emblem 404 on production, while the *ignored* BR/LH emblems stayed 200 (they were on the deploying tree's disk). "Committed" and "on the deploy tree" are independent axes — a complete deploy source needs both checked.
- **Exact census method (read-only):** `ssh <deploy creds> "find $WP_THEME_PATH -type f"` vs `(cd $THEME_DIR && find . -type f | sed 's|^\./||' | sort)`, then `comm -23`. The 2026-07-13 diff: 100 live-only files = 17 functional riders + 83 junk (~40 `CLAUDE.local.md`, `._*` AppleDouble forks, `__pycache__`, lock/cache files). The junk SHOULD fall off on the next deploy — the ~40 `CLAUDE.local.md` are internal agent instructions sitting on a public webserver.
- **Tar-exclude gap:** `--exclude='CLAUDE.md'` does NOT match `CLAUDE.local.md` — that is how they shipped. **SHIPPED 2026-07-13:** `CLAUDE.local.md`, `._*`, `__pycache__` added to `tar_excludes`; verified empirically with bsdtar 3.5.3 (bare-name exclude patterns match at any depth — nested `inc/CLAUDE.local.md`, AppleDouble forks, whole `__pycache__/` dirs all dropped; keepers intact, 8/8 assertions). The next deploy's hot-swap scrubs the ~40 live `CLAUDE.local.md` automatically.
- **Byte-size = identity spot-check:** live emblem sizes (35,996 / 39,686 B) matched the primary-checkout files exactly — confirm provenance this way before overlaying.
- **Staged deploy-ready source for v1.10.4:** worktree `.claude/worktrees/deploy-v1104` = clean `origin/main @ 9aaa88a52` (triple-verified 1.10.4, 1734 tracked files) + the 17 riders already overlaid.
- **Preflight source-completeness gate SHIPPED 2026-07-13** — `preflight_completeness()` in `scripts/deploy-theme.sh`, fail-closed, runs before the PHP lint sweep: (1) version triple 3-way equality (unparseable = block), (2) every `git ls-files` path exists on disk (non-git source → warn + floor only), (3) critical-asset floor ≥3 emblem webp / ≥10 woff2 / `skyy.glb` present. Emergency override `PREFLIGHT_SKIP_COMPLETENESS=1` (logged loudly). Verified 4/4 behavior tests under `set -euo pipefail` incl. positive run on origin/main (1755/1755 tracked files, triple 1.11.0). Note: 14 of the 17 riders are now git-tracked (`1dc868199`); the ls-files check therefore protects them too.
- **RETRACTED 2026-07-14 — the "ADDITIVE transport" claim above was WRONG; `deploy-theme.sh` is wholesale-replace. Read the code, not the HTTP status.** The prior entry inferred "additive" from "never-tracked scenes still 200 after deploy", but that inference is unsound and the deterministic code disproves it:
  - **Code is authoritative (`scripts/deploy-theme.sh:633`, the remote swap):** `tar -xf … && (mv "$WP_THEME_PATH" "$WP_THEME_PATH.old.$swap"; ) && mv skyyrose-flagship "$WP_THEME_PATH"`. The live dir is renamed **aside in full** and the fresh extraction moved in — **wholesale-replace**. There is no "extract-over-existing" step; anything absent from the tar is gone from live. (Independently re-read + confirmed by two adversarial reviewers, 2026-07-14.)
  - **Why the 200s did NOT prove additive:** the deploy source carried those scene files as **untracked riders on disk** — a wholesale deploy from a source-that-has-the-file preserves it (the exact rider mechanism of bug-252), so 200 is fully consistent with wholesale. The premise "`deploy-v1104`'s `scenes/` was empty" was also false — `copy-riders.sh` overlaid the scene webp into it. Live-header check (2026-07-14): the never-tracked `…-v2-avatar.webp` serves from **origin** (`x-ac: MISS`), i.e. it is physically on the prod filesystem because a source *had* it, not because the transport spared a deletion. And the actual prod 1.10.4 deploy was run by the founder's separate (uninspectable) tool — do not generalize its behavior onto `deploy-theme.sh`.
  - **Fail-safe stance (governs):** treat `deploy-theme.sh` as wholesale-replace. The completeness gate + rider tracking are **LOAD-BEARING, not belt-and-suspenders** — a clean-tree / fresh-worktree / CI deploy through this script WILL delete any file the source lacks (line 152 holds). Cost asymmetry decides it: assume-wholesale-when-additive = harmless redundancy; assume-additive-when-wholesale = riders deleted, production breaks.
  - **Still true (the one salvageable sub-claim):** the `try_lftp()` fallback's `mirror --reverse --delete` is unreachable on this host (hardcodes a nonexistent `~/.ssh/skyyrose-deploy` key). But that path is not the reason for deletion — the primary tar+swap path deletes by design.
- **Junk does NOT self-clean via a normal deploy IF the deploy runs from the same dirty working tree that carries the junk** — but a clean-tree deploy (which the excludes now scrub) drops the ~40 exposed `CLAUDE.local.md`. Since the `tar_excludes`/`RSYNC_EXCLUDES` gap was closed 2026-07-13, any deploy now stops *shipping* them; existing exposed copies persist until a clean-tree deploy overwrites the live dir or they are removed server-side (`rm`, a STOP-AND-SHOW production write).
- **CONFIRMED 2026-07-27 — the 3 still-untracked `*-v2-avatar.webp` riders are now 404 on production.** `[live]` cache-busted curl of all 17 documented riders: 14 return 200 (the 14 that got `git add -f` tracked in `1dc868199`), but `black-rose-rooftop-garden-v2-avatar.webp`, `love-hurts-cathedral-rose-chamber-v2-avatar.webp`, and `signature-golden-gate-showroom-v2-avatar.webp` all 404 — their `-lookbook.webp` siblings are still 200. `[repo]` confirms they are absent from `git ls-files` AND absent from the main checkout's disk entirely (`find` returns nothing) — exactly the bug-252 failure mode: a clean-tree/CI deploy since these were last live-verified wholesale-replaced the live dir with a source that never had them. They are NOT lost — `[repo]` found byte-identical copies still sitting in a different worktree, `.claude/worktrees/collections-scroll-world/wordpress-theme/skyyrose-flagship/assets/scenes/{black-rose,love-hurts,signature}/`. **Fix (not yet applied — needs a STOP-AND-SHOW production-write confirm):** copy the 3 files from that worktree into the main checkout and `git add -f` them, same treatment as the other 14, so the ls-files completeness gate protects them too; then redeploy. Full JS/CSS bundle content otherwise verified byte-identical between live and repo via SHA-256 (11 JS + 3 CSS enqueued files, all MATCH) — this is the one confirmed drift, not a broader pattern.

## Formatter ownership — one registry, two checks (2026-09-20)

**The failure mode.** A file whose bytes a program owns (a serializer, a
generator, a minifier) plus a formatter that also rewrites it is two writers on
one file: each "fixes" the other's output forever. Prettier rewrites 1,643 lines
of `.wolf/buglog.json`, after which the wolf-memory MCP server's serializer
writes it straight back on the next `bug_log`. The same shape broke `.min`
assets (bug-332, twice) and desynchronizes byte-comparing gates
(`sync_product_registry.py --check`, `check:assets`, `freshness-guard`) for
reasons unrelated to the change under review.

**Why it kept recurring.** The knowledge lived in two hand-maintained lists —
`.prettierignore` and `lint-staged.config.mjs`'s `isByteStableOrManaged` — with
nothing tying them together. A new generated file could land in one, the other,
or (as with `.wolf/buglog.json` and `.wolf/anatomy.md`) neither. Nothing failed
until someone staged the file.

**The fix.** `data/machine-managed-files.json` is the one list: each entry names
the `pattern`, real `samples`, the `owner` program and `why`. Two gates, chosen
so neither depends on the other being runnable:

| Gate | Needs | Catches |
| --- | --- | --- |
| `tests/test_machine_managed_files.py` | Python only — runs in the main CI pytest job (`ci.yml:153`) | Registry ↔ `.prettierignore` drift in both directions, a second hardcoded list in `lint-staged.config.mjs`, registry entries pointing at deleted files, a truncated registry |
| `scripts/verify-formatter-ignores.mjs` (`npm run verify:formatter-ignores`) | node + root `node_modules` — pre-commit hook and the root TypeScript CI job | What prettier and lint-staged would ACTUALLY do, via prettier's own ignore resolution and the real task functions |

**Adding a generated file:** add it to the registry, then to `.prettierignore`.
The Python gate fails if you do one without the other, and lint-staged reads the
registry directly, so there is no third place to update.

**Two traps worth knowing.** (1) lint-staged reads the same registry, so its
half of the node check would be tautological — the script therefore runs a
positive control: an unowned file (`README.md`) must still be selected by at
least one task, or the filter is inert and its verdict is worthless. (2) The
pre-commit hook says out loud when it skips for want of `node_modules` rather
than passing silently, and the node script reports an unloadable prettier as an
explicit UNVERIFIED failure instead of aborting before the lint-staged half.

### A parity check between two lists dies quietly when one list moves (bug-353)

The gate this replaced derived the managed paths by regex-scraping
`lint-staged.config.mjs`, then diffed them against `.prettierignore`. When the
hardcoded regexes became a registry read, the scraper returned `[]` — and:

```python
missing = [p for p in patterns if not prettierignore_covers(p, lines)]
assert not missing          # patterns == []  ->  missing == []  ->  PASSES
```

Two sibling tests failed loudly; **this one went green while testing nothing**.
That is bug-230's fail-open inside the very gate meant to prevent churn, and it
generalizes past formatters:

> Any check shaped `violations = [x for x in DERIVED if bad(x)]; assert not
> violations` passes when `DERIVED` is empty. If `DERIVED` comes from parsing
> another file, a refactor of that file silently disarms the check.

**The rule:** a gate that iterates a derived collection needs a **floor on the
collection itself** — not merely non-empty, a count, so silent shrinkage fails
too. `test_registry_is_not_empty` asserts `>= 22`. Verify the floor by mutation,
not by inspection: truncate the input and confirm the gate goes red
(`[empty] exit=1 … expected at least 14`, `[shrunk to 3] exit=1`). Prefer a
declared registry over list-to-list parity for exactly this reason — the
registry is still there to compare against after either consumer moves.

---

## 2026-09-21 — CI reality, merge attribution, and two silent-defect classes

### CI: what actually gates, and what doesn't

Re-verified against the workflow file and the GitHub API, because a memory note
claiming "E2E is non-gating" was stale and would have licensed merging past a red
browser run.

- **Playwright E2E IS gating.** `.github/workflows/ci.yml` Stage 3 `e2e-tests`
  carries *"Browser regressions must fail CI now that the suite covers current
  behavior"*, and `continue-on-error` appears **nowhere** in the file. It also
  starts late (`needs: [python-tests, frontend-tests]`) and runs 10+ minutes, so a
  PR sitting at 21/22 green with E2E pending is normal, not stalled.
- **`main` has NO branch protection.**
  `gh api repos/SkyyRoseCo/DevSkyy/branches/main/protection` →
  `required_status_checks` ABSENT, `enforce_admins` false,
  `required_pull_request_reviews` ABSENT. "Green" is the CI workflow's own
  conclusion, never a server-enforced gate — **nothing stops a merge with red or
  pending checks.** Any drive-to-green automation must wait for every job itself;
  there is no backstop.
- **A CONFLICTING PR runs almost no CI.** GitHub builds no merge ref for it, so
  `pull_request`-triggered workflows never fire — only push-triggered ones
  (CodeQL). The PR looks *stalled* rather than failing. Resolve the conflict
  first, then checks appear. (Observed on #960.)

### Merge attribution needs a THREE-way diff, not a two-way one

Verifying that a merge kept both sides, I diffed my branch against `origin/main`
and got 24 "lost" keys. All 24 were **my own changes reflected back** — a two-way
diff cannot distinguish "they changed it" from "I changed it."

The only correct reference point is the merge base:

```bash
base=$(git merge-base <mine> origin/main)
# theirs = keys where origin/main differs from $base
# ours   = keys where <mine>   differs from $base
# merged must carry theirs' value for (theirs - ours), ours' for (ours - theirs)
# and (theirs n ours) is the only set needing human eyes
```

With the base applied: 7 incoming keys, 24 of ours, **0 overlap, 0 lost**. The
failure mode is silent — a plausible list of regressions that is really your own
work. Pairs with the attribution rule in root `CLAUDE.md` section 3.

### An untracked binary behind a SOT binding is a latent 404

A theme deploy is an atomic hot-swap that ships only **git-tracked** files.
`.gitignore:297` blanket-ignores `wordpress-theme/skyyrose-flagship/assets/**/*.webp`,
so three founder-approved on-model fronts were present on disk, referenced by the
registry/CSV/`sot.json`, and invisible to every local check — while a clean-tree
deploy would have 404'd those product cards.

`tests/test_sot_assets_tracked.py` catches this class **because it asks git, not
the filesystem**. Fix order is non-negotiable: `git add -f` the binaries FIRST,
repoint bindings SECOND. A repoint ahead of the add re-creates the 404.

Identity of an image asset is established by **content, not filename**: hash the
file and compare against the approved manifest. Here, `sha256` equality with the
`FOUNDER_APPROVED_V2_CARD` entries disproved a repo doc
(`tasks/launch-20260921-image-coverage.md:17`) that called those same files
ghost/mannequin shots.

### A confidently wrong value hides from the queries built to find gaps

8 Jersey Series SKUs needed a fit statement. Seven had `fit: null` and surfaced
instantly in a "fit is null" query. The eighth (br-010) held a **mis-extracted
fabric sentence** — decoration prose with a stray markdown bold marker sitting in
a sizing field. It passed every structural/completeness check *because it was
populated*, and would have shipped garment-fabric text into a PDP sizing field.

Origin, for the record: `git log -S'derived_from_dossier' -- scripts skyyrose` is
**empty**. No code in this repo ever produced those values — they arrived as
pre-split *data* from a keyword-sentence extractor that was never committed, and
the old `dossier_loader.py` let them override founder prose under a "takes
precedence over legacy dossier prose" heading. `test_dossier_founder_prose` now
forbids exactly that.

Still wrong at time of writing, reported not fixed: `lh-004` (hood-lining
decoration prose in `fit` — **should be nulled, not kept**, until the founder
supplies a statement); `br-002`, `sg-007`, `sg-014` (over-broad silhouette
sentences). **Prefer null over wrong:** null is discoverable, wrong is not.

### A gate that can never be satisfied is a deadlock, not a gate

`.claude/hooks/stop-test-gate.sh` ARMS on "any `*.py` is dirty" but ASSERTS "the
whole suite is green". Those are different questions. When the red test is not the
stopping session's to fix — pre-existing, another session's WIP, or needing a
permission the agent lacks — it re-blocks every Stop forever and the session can
never end. This is the recurring bug-333 pattern.

Reviewed fix (block once per distinct failure signature + tree state, then report
`STILL RED — needs a human` and let Stop through; fails closed on an unparseable
run) is written but **NOT applied** — editing the gate that constrains the agent
is correctly a human decision.
