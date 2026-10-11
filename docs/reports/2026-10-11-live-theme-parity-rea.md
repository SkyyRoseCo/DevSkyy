# Live theme parity — skyyrose.co vs repo (2026-10-11)

Read-only. No production writes, no paid calls. Checker:
`wordpress-theme/skyyrose-flagship-2/scripts/verify-live-parity.py` (tests:
`scripts/test-verify-live-parity.py`, 11 offline cases).

## Method

Pages: `/`, `/shop/`, `/collections/black-rose/`, `/product/br-001/`.

1. **HTTP bytes** — every theme `.js/.mjs/.css` URL in the page HTML is fetched;
   served sha256 must equal the repo file, and the `?ver=` 12-hex hash
   (`functions.php` `skyyrose2_asset_version`) must match the served bytes.
2. **Jetpack Boost bundles** — `/_jb_static/??…` concatenates CSS, hiding
   per-file `?ver=`. Each repo `*.min.css` is checked for byte containment
   (exact, or after `url()` normalisation — Boost rewrites relative paths).
3. **REA runtime** — each page opened in an isolated headless Chromium (loopback
   CDP, throwaway profile); `rea-agents@6.4.0 analyze-web-bundle` records every
   script that executed with its sha256; each theme script must match a repo
   file.

## Results

| Check                 | Verified                        | Findings          |
| --------------------- | ------------------------------- | ----------------- |
| HTTP bytes (theme JS) | 17                              | 0                 |
| Boost CSS bundles     | 46 (42 exact, 4 url-normalised) | 0                 |
| REA executed scripts  | 15                              | 0                 |
| Brand font policy     | —                               | 5 (homepage only) |

- **Theme JS/CSS parity: PASS** `[live]`+`[repo]`. Every theme asset served or
  executed on the four pages is byte-identical to
  `wordpress-theme/skyyrose-flagship-2/`.
- **Version:** live renders `2.5.2`; repo is `2.5.3`. 2.5.3 (7971aa8fd) changed
  only PHP (`inc/seo-indexing.php` image sitemap), so asset parity holds; **the
  image-sitemap fix is not deployed.** No severity claimed.
- **Font policy FAIL — homepage** `[live]`: Elementor enqueues Google font
  stylesheets from `fonts-api.wp.com` (handles `elementor-gf-*`): Roboto, Roboto
  Slab, Inter and **Playfair Display** (cut 2026-07-10). Source is Elementor's
  site font setting, not the theme. Fixing it changes a production setting →
  STOP-AND-SHOW.
- **Not checkable live (by design)** `[repo]`: product GLB viewer
  (`glb_runtime.publication_authorized=false`, 0 entries) and mascot
  (`skyyrose2_mascot_enabled()` returns false) ship to no page. Their absence is
  correct, not a pass.
- **Unconfirmed observation:** one headless capture of
  `/collections/black-rose/` received HTML referencing `?ver=2.5.0-…` assets
  (bytes still matched). Not reproduced in 8 Chrome-header curl fetches (edge
  reported HIT/MISS/STALE/UPDATING); no severity.
- **False positive avoided:** `archive-theme.min.css` partially overlaps the
  homepage bundle because it is derived from `theme.min.css`
  (`inc/archive-style-bundle.php:28`), which is byte-exact in the bundle; it is
  an archive-page asset, not drift.

## Gotchas recorded

- REA rejects a target whose URL carries a query string (`target_not_allowed`):
  open the bare URL and pass `--allowed-origins https://skyyrose.co`. Captures
  therefore see what the edge cache serves visitors.
- REA needs a loopback CDP endpoint (`--remote-debugging-address=127.0.0.1`);
  use a throwaway `--user-data-dir`, never the founder's browser profile.

## Re-run after review hardening (same day)

Checker now fetches bare visitor URLs without following redirects, verifies
every distinct `(path, query)` reference, requires a content-hashed `?ver=` on
hash-sized assets, reproduces Boost's exact `url()` rewrite, verifies Boost
**JS** bundles and the homepage inline blocks (`#skyyrose2-critical-home`,
`#skyyrose2-visual-recovery-early`), treats leftover theme code in any bundle as
drift, and scans all CSS for cut families.

Result `[live]`: **91 asset checks verified, 0 drift, 0 unmatched theme code, 0
incomplete** (53 concat-exact incl. 3 theme scripts inside JS bundles, 17
http-bytes, 15 REA runtime, 4 Boost-url CSS, 2 inline blocks). Policy findings:
the 4 Elementor `fonts-api.wp.com` stylesheets on `/`, plus cut families
declared on every checked page by `.skyyrose-modal__name` (Playfair Display),
`.skyyrose-immersive` (Cormorant Garamond) and `.skyyrose-immersive__hud-hint`
(Bebas Neue) — CSS that is **not in this repo** (`git grep` finds no match), so
it ships from another live source (likely a plugin).
