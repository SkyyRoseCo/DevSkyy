# design-sync Notes

## Preview images

Updated 2026-06-22: all placehold.co URLs replaced with real hosted skyyrose.co imagery
(verified 200 before use). Sources:

### HoloCard.tsx — WooCommerce product renders (i0.wp.com Jetpack CDN)

| Component | SKU | Name | Price | URL |
|-----------|-----|------|-------|-----|
| BlackRose | br-001 | BLACK Rose Crewneck | $35 | https://i0.wp.com/skyyrose.co/wp-content/uploads/2026/06/black-rose-crewneck-front-model.webp?fit=1024%2C1024&ssl=1 |
| LoveHurts | lh-002 | Love Hurts Joggers (Black) | $95 | https://i0.wp.com/skyyrose.co/wp-content/uploads/2026/06/love-hurts-joggers-front-model.webp?fit=1024%2C1024&ssl=1 |
| Signature | sg-003 | The Bridge Series 'Stay Golden' Shorts | $65 | https://i0.wp.com/skyyrose.co/wp-content/uploads/2026/06/bridge-stay-golden-shorts-front-model.webp?fit=1024%2C1024&ssl=1 |
| KidsCapsule | kids-001 | Kids Colorblock Hoodie Set — Red/Black | $65 | https://i0.wp.com/skyyrose.co/wp-content/uploads/2026/06/kids-red-set-front-model.webp?fit=896%2C1200&ssl=1 |

Names/prices match live WC catalog (read-only API, 2026-06-22).

### CollectionHero.tsx — Canonical brand-script lockup images (theme asset CDN)

| Component | Asset | URL |
|-----------|-------|-----|
| BlackRose | br-brand-script-logotype.webp | https://skyyrose.co/wp-content/themes/skyyrose-flagship/assets/images/hero-overlays/br-brand-script-logotype.webp |
| LoveHurts | lh-logo-combined.png | https://skyyrose.co/wp-content/themes/skyyrose-flagship/assets/images/hero-overlays/lh-logo-combined.png |
| Signature | sig-brand-skyy-rose-gold.webp | https://skyyrose.co/wp-content/themes/skyyrose-flagship/assets/images/hero-overlays/sig-brand-skyy-rose-gold.webp |
| KidsCapsule | sr-monogram-rose-gold.webp (no dedicated Kids script exists) | https://skyyrose.co/wp-content/themes/skyyrose-flagship/assets/images/logos/sr-monogram-rose-gold.webp |

All 7 URLs returned HTTP 200 (curl -sI verified). No data-URI fallbacks needed.

## Font delivery

Fonts do NOT ship via `dist/skyyrose-ds.css` (Vite would base64-inline woff2 into the CSS).
They ship via `cfg.extraFonts` → `design-system/skyyrose-storefront/src/fonts/fonts.css`.
The converter copies woff2 files and the @font-face CSS into `ds-bundle/fonts/`.

## Canon font set (11 woff2 files, 8 families)

Only fonts referenced by DS components or tokens are included. Provenance:
- `wordpress-theme/skyyrose-flagship/data/logo-registry.json` → `collections.<slug>.fonts`
  blesses: Cinzel (caps), Hanken Grotesk (body), per-collection name-scripts —
  Black Rose=SkyyRose Black Rose Script, Love Hurts=SkyyRose Love Hurts Graffiti,
  Signature=Pinyon Script, Kids Capsule=Grand Hotel
- `design-tokens.css` :root blesses: Archivo (display), Hanken Grotesk + Inter (body),
  Anton (UI), SF Mono/Menlo (mono)

⚠ DRIFT (2026-07-13): `CANON_WOFF2`/`CURATED` in `scripts/sync-theme-assets.mjs` still pin
the pre-2026-07-11 set (Playfair/Cormorant/Bebas/Yellowtail/Kaushan) — update both maps to
the roster above and re-run `npm run sync` before trusting the DS font bundle.

Excluded (legacy/retired — in theme.json but referenced by nothing in the DS):
- Barlow, Oswald, Instrument Serif

The `CANON_WOFF2` set in `scripts/sync-theme-assets.mjs` is the enforcement point.
Sync copies only those 11 files and removes any others from `src/fonts/`. `sync:check`
flags any legacy files that remain.

If font family names drift (e.g., theme.json fontFamilies updated), run:
```
npm --prefix design-system/skyyrose-storefront run sync
npm --prefix design-system/skyyrose-storefront run sync:check
```

## Re-sync risks

- `src/fonts/fonts.css` is generated from `theme.json` — never hand-edit it
- `src/tokens/tokens.css` and `src/styles/commercial-polish.css` are verbatim copies from the WP theme
- Any WP theme CSS change requires `npm run sync` in `design-system/skyyrose-storefront/`

## projectId

`.design-sync/config.json` has no `projectId` yet. Task 8 adds it after the project is
created in claude.ai/design. Do not add a placeholder value.

## Collection scripts

The collection name-scripts (SkyyRose Black Rose Script, SkyyRose Love Hurts Graffiti,
Pinyon Script, Grand Hotel) are NOT all in `theme.json` fontFamilies — script fonts are
covered by the `CURATED` map in `sync-theme-assets.mjs` and included in `CANON_WOFF2`
(⚠ those maps still list the retired Yellowtail/Kaushan Script — see DRIFT note above).
If a new collection script font is added, update both maps.
