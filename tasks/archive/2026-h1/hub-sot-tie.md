# Tie asset-hub → SOT (founder: "wire + sync renders live")

Goal: the verified hub becomes the upstream authority feeding `data/sot-images.json`;
verified renders physically staged into the theme so they serve. Deploy stays gated.

- [x] 1. Track SOT inputs: `git add` asset_hub.py + test + ingester + contactsheet; `git add -f` manifest.json (blobs stay ignored). Drift guard needs the hub present at CI.
- [x] 2. Sync the 7 verified non-theme renders → `wordpress-theme/.../assets/images/products/hub/<sku>-<face><ext>`; `git add` them (staging for deploy, deploy still gated).
- [x] 3. `asset_hub.served_theme_path(sku, face)` — theme-rel path a verified entry serves from (stripped theme source, or synced hub/ path).
- [x] 4. Wire `sot_images._index()` override: verified + on-disk-under-theme → overrides catalog front/back. Existence-guarded.
- [x] 5. Regenerate `make sot-manifest`; diff before/after.
- [x] 6. SOT.md row + root symlink `hub-manifest.json`; update LOCKED memory (feedback_sot_imagery_everywhere) + project_asset_hub.
- [x] 7. Verify: test_asset_hub + test_sot_images + test_sot_no_adhoc_imagery + drift guard (`sot_images_current`) green; every emitted sot path resolves on disk under theme.

7 needing sync: br-007-back(gemini), br-007-front, lh-003-front, sg-003-front, sg-011-back(pipeline), sg-014-front, sg-015-front (rest oai-image-2).
