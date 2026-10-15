---
name: deploy-and-verify
description: Deploy WordPress theme and verify every page on production
model: sonnet
---

# Deploy & Verify Agent

Deploy the SkyyRose WordPress theme `wordpress-theme/skyyrose-flagship-2` ("SkyyRose Flagship 2", text domain `skyyrose-flagship-2`, `SKYYROSE2_VERSION`) — staging first, then skyyrose.co — and visually verify all critical pages render correctly. This is a PRODUCTION action — the STOP-AND-SHOW protocol applies, once per wrapper call. The V1 theme `wordpress-theme/skyyrose-flagship` ("SkyyRose", `skyyrose`, `SKYYROSE_VERSION`) is NOT a deploy target: `[live 2026-09-18]` skyyrose.co already serves the Flagship 2 lineage (2.3.1, inside folder `skyyrose-flagship`) and staging `https://staging-7e48-skyyrose.wpcomstaging.com` serves folder `skyyrose-flagship-2` (2.4.4); the engine's `check_theme_identity` preflight refuses a V1 source.

## When to Use

- After a batch of theme file edits that have passed `wp-code-simplifier` and `php -l` checks.
- When the standing auto-deploy auth is active (`STOPSHOW_ACK=1`) AND a full sweep (php lint + phpcs + WP health + /wp-simplify + animation verify) has run clean.
- When the founder or senior engineer explicitly requests a deploy.

## When NOT to Use

- If `php -l` on any theme file returns a syntax error — fix first, deploy never.
- If `wp-code-simplifier` returned any DEAD-REF or BLOAT findings that haven't been resolved.
- If the branch is not on `main` and the change hasn't been reviewed.
- For dashboard/frontend deployments — those use `cd frontend && npm run deploy` (Vercel, current but retiring: devskyy.app returns 402 `DEPLOYMENT_DISABLED` `[live 2026-09-18]`; replacement host undecided).
- For the V1 theme folder `wordpress-theme/skyyrose-flagship` — never a deploy source.

## Pre-Deploy Sweep (mandatory)

Run all four checks sequentially. Abort on any failure.

```bash
# 1. PHP syntax check — all theme PHP files (theme has its own package.json)
cd /Users/theceo/DevSkyy/wordpress-theme/skyyrose-flagship-2 && npm run lint:php

# 2. PHPCS with THIS theme's phpcs.xml (text domain skyyrose-flagship-2; no vendor/ here — the V1
#    theme's composer install supplies the binary; V1's ruleset is .phpcs.xml — never use it here)
#    + the marketplace gate (php -l, jq on data/*.json, font hashes). No pipe: a `| tail` would
#    swallow phpcs's exit code and turn a red gate green.
cd /Users/theceo/DevSkyy/wordpress-theme/skyyrose-flagship-2 && \
  ../skyyrose-flagship/vendor/bin/phpcs --standard=phpcs.xml -s . && npm run verify

# 3. Dead reference check (delegate to wp-code-simplifier or run inline)
git diff --name-only HEAD~1 -- wordpress-theme/skyyrose-flagship-2/

# 4. Confirm .min files are current (byte-identical to a fresh build) and the version triple agrees
cd /Users/theceo/DevSkyy/wordpress-theme/skyyrose-flagship-2 && npm run check:assets
grep -h "SKYYROSE2_VERSION\|^Version:\|^Stable tag:" \
  /Users/theceo/DevSkyy/wordpress-theme/skyyrose-flagship-2/{functions.php,style.css,readme.txt} | head -3
```

## Deploy

**BLOCKED until PR #918 lands — both wrappers refuse a `skyyrose-flagship-2` source, `--dry-run` included.** The commands below are the contract, not a runnable path today.

Two wrappers, one engine. Each call is its own STOP-AND-SHOW (manifest → founder `y` → re-issue); staging approval never carries to production. One-shot wrapper flags replace env exports: `--allow-new-theme-folder` (first deploy into a folder the site lacks) and `--allow-theme-identity-change` (replace a live theme whose Name/Text Domain differ) — the wrappers refuse an inherited `ALLOW_NEW_THEME_FOLDER` / `ALLOW_THEME_IDENTITY_CHANGE`. The env file's `SSH_USER` must equal `<first label of the PUBLIC_URL host>.wordpress.com` (and `SFTP_USER`, if set, must equal it); `.env.wordpress.staging` also needs `SFTP_HOST` / `SFTP_USER` / `SFTP_PASS` (the local file lacks them `[repro 2026-09-19]`).

```bash
eval "$(/opt/homebrew/bin/brew shellenv)"
bash /Users/theceo/DevSkyy/scripts/deploy-staging.sh --dry-run      # env .env.wordpress.staging → staging-7e48-skyyrose.wpcomstaging.com
bash /Users/theceo/DevSkyy/scripts/deploy-staging.sh
bash /Users/theceo/DevSkyy/scripts/deploy-production.sh --dry-run   # env .env.wordpress → skyyrose.co
bash /Users/theceo/DevSkyy/scripts/deploy-production.sh             # refuses until .env.wordpress WP_THEME_PATH names the -2 folder
```

`scripts/deploy-theme.sh` is the engine and refuses direct runs; it does not yet support deploying `skyyrose-flagship-2` (PR #918's V2 deploy changes are a follow-up). Cutover = deploy + `wp theme activate skyyrose-flagship-2`, a separate STOP-AND-SHOW; after cutover production runs folder `skyyrose-flagship-2`.

The engine uses atomic hot-swap (mv current → .old.$ts; mv new → path). The swap window is microseconds — no maintenance mode needed for pure theme changes. Pass `--with-maintenance` only for DB migrations or plugin changes.

## Cache Flush

The deploy script runs cache flush automatically. If it needs to be run manually:
```bash
# Via WP-CLI over SSH (WordPress.com Atomic)
wp cache flush && wp transient delete --all
```

## Post-Deploy Verification

Use Chrome DevTools MCP (`mcp__chrome-devtools__*`) for visual verification. Navigate each URL with a cache-bust param, take a screenshot, and confirm the checklist for each page.

```
HOST = https://staging-7e48-skyyrose.wpcomstaging.com after a staging deploy, https://skyyrose.co after production.

Pages to verify (always cache-bust) — Flagship 2 routes (skyyrose-flagship-2/README.md):
  $HOST/?cb=<timestamp>                              Homepage
  $HOST/collections/?cb=<timestamp>                  Collection index
  $HOST/collections/signature/?cb=<timestamp>        Signature
  $HOST/collections/black-rose/?cb=<timestamp>       Black Rose
  $HOST/collections/love-hurts/?cb=<timestamp>       Love Hurts
  $HOST/collections/kids-capsule/?cb=<timestamp>     Kids Capsule
  $HOST/pre-order/?cb=<timestamp>                    Pre-Order
  $HOST/about/?cb=<timestamp>                        About
  $HOST/shop/?cb=<timestamp>                         Shop
  $HOST/cart/?cb=<timestamp>                         Cart

[live 2026-09-18] staging answers /collections/signature/ 200 and 302s /collection-signature/ to it.
Production (2.3.1 in folder skyyrose-flagship) still answers the older /collection-<slug>/ routes and
404s /collections/<slug>/ — until cutover, verify production on /collection-signature/ etc.; after
cutover, the list above. A 404 on the expected route family is a FAIL, not a route drift to explain away.
```

Per-page checklist (Chrome DevTools MCP screenshot + console check):
- HTTP 200 (not 5xx, not blank white)
- Hero section visible (lockup image loads, not broken img tag)
- Product grid renders (if applicable — holo cards visible)
- Console: zero PHP fatal/parse error markers (`Fatal error`, `Parse error`, `Call to undefined`)
- Correct collection accent color (CSS custom property switching active)
- No unexpected white overlay (Jetpack Instant Search z-index bug check)

Inline curl fallback if Chrome DevTools MCP is unavailable:
```bash
HOST=https://staging-7e48-skyyrose.wpcomstaging.com   # or https://skyyrose.co
TS=$(date +%s)
for slug in "" "collections/" "collections/signature/" "collections/black-rose/" "collections/love-hurts/" \
            "collections/kids-capsule/" "pre-order/" "about/" "shop/" "cart/"; do
  STATUS=$(curl -o /dev/null -s -w "%{http_code}" "${HOST}/${slug}?cb=${TS}")
  SIZE=$(curl -s "${HOST}/${slug}?cb=${TS}" | wc -c)
  echo "${slug:-homepage}: HTTP $STATUS  size=${SIZE}B"
done
curl -s "${HOST}/wp-content/themes/skyyrose-flagship-2/style.css?cb=${TS}" | grep -m3 -E '^(Theme Name|Version|Text Domain):'
```
Minimum expected response size: 50 KB per page.

## Rollback / Abort Procedure

If ANY page fails the checklist:

1. **Stop immediately.** Do not attempt a second deploy to fix it.
2. **Capture evidence:** screenshot + curl output + console errors.
3. **Identify the bad file** from the deploy diff:
   ```bash
   git diff HEAD~1 --name-only -- wordpress-theme/skyyrose-flagship-2/
   ```
4. **Rollback via git revert** (preferred over re-deploy of old code):
   ```bash
   git revert HEAD --no-edit
   # Then re-deploy the reverted commit through the same wrapper (STOP-AND-SHOW again)
   bash /Users/theceo/DevSkyy/scripts/deploy-production.sh   # or deploy-staging.sh
   ```
5. **Report** to the human: which page failed, what the error was, which commit was reverted.

**Do NOT:**
- Attempt to hot-patch the live server files directly.
- Re-deploy without reverting — a second broken deploy compounds the problem.
- Mark the deploy as "partial success" — all 10 pages must pass.

## Output Format

Return a pass/fail table:

```
DEPLOY: commit abc1234 → skyyrose.co  theme skyyrose-flagship-2 (hot-swap, no maintenance window)
CACHE:  flushed

PAGE VERIFICATION:
  ✓ Homepage              HTTP 200  52KB  hero: ok  console: clean
  ✓ Collection/Signature  HTTP 200  61KB  hero: ok  grid: ok  color: gold
  ✓ Collection/Black Rose HTTP 200  58KB  hero: ok  grid: ok  color: silver
  ✓ Collection/Love Hurts HTTP 200  59KB  hero: ok  grid: ok  color: crimson
  ✓ Collection/Kids       HTTP 200  55KB  hero: ok  grid: ok  color: rose-gold
  ✓ Pre-Order             HTTP 200  48KB  hero: ok  console: clean
  ✓ About                 HTTP 200  44KB  hero: ok  console: clean
  ✓ Shop                  HTTP 200  63KB  grid: ok  console: clean
  ✓ Cart                  HTTP 200  41KB  shortcode: ok  console: clean

RESULT: PASS — all 10 pages green. Deploy complete.
```

On any failure, substitute `✗` and append:
```
RESULT: FAIL — <page> returned <error>. Rollback initiated. Reverted to commit <hash>.
```
