# PR 998 V2 analytics runtime baseline reconciliation

## Scope and lineage

- Candidate inspected: `b640c3b3b36e825ba3eb9110522205ab8471ca3b` on
  `codex/brand-maintenance-neon-migration`.
- Reviewed source change: `d33ac90e468e3739e1854056c3f6e47ee287d6b8`.
- Previous source: `b10a410c84cfc65e348aa2983aa942b71c4af4a0` (the source change
  parent).
- Every replaced baseline digest was independently matched to the exact
  corresponding previous-source blob.
- `check-current-scenes.py` explicitly permits affected runtime baseline entries
  to be reconciled with lineage and regression evidence in `tasks/`. Its guards
  are unchanged.

The three changes are the analytics bootstrap require in `functions.php`, the
Cookie settings control in `inc/global-shell.php`, and an escaped existing
product SKU attribute in `template-parts/commerce/product-card.php`, plus
mandatory PHP formatting applied by the existing commit hooks. This is
source-identity reconciliation, not new founder visual approval, scene
certification, deployment authorization, or a claim of live collection.

| Runtime file                               | Previous SHA-256                                                   | Current SHA-256                                                    |
| ------------------------------------------ | ------------------------------------------------------------------ | ------------------------------------------------------------------ |
| `functions.php`                            | `2eb3fe1140dce2caa3de7f908ef1b71dbd72294a290a9afc487721f09f7ca558` | `40b14fd7cbeca559b56b144593f15cf24576e250ffd6d65ef409613f1b2d0b67` |
| `inc/global-shell.php`                     | `ff46acdf2650491ea7ac2fb7c7e5ab88f5b9b1a734efb022773c3d3ac63e1398` | `f8498a2fcea2119fdcb25bd773948e7baf402ccaef08074835455e401b7470a9` |
| `template-parts/commerce/product-card.php` | `f0918516bffc1635935ce836534af2275ec45e68895ca0f223395d7425f12bc6` | `3b2100f09f5120158d4a01f18fda4a9c971b33d919865696c9486bb64dbca4b4` |

The runtime-baseline input pin changed is `build-inputs.json` →
`input_hashes["tools/v2-source-certification/runtime-php-baseline.json"]`:
`984b41d0cf5dd1bc952be8f474038b60a78ef981b8b124105c6d9653591bf02a` →
`08df4e075b5e86aa4fb7c6eefb7b121df0dbeaa397b0f7738a85ca244a5442df`. Its old
value matched the exact HEAD baseline manifest. No product record, scene cast,
approval state, media binding, or runtime source was changed in this repair.

## Explicit package closure

The first complete build/verify reached the packager and exposed 16 newly added,
unclassified analytics paths. Added exactly those paths to
`package-boundary.json`:

- Release runtime (7): `assets/css/cookie-consent.css`,
  `assets/css/cookie-consent.min.css`, `assets/js/experience-analyzer.js`,
  `assets/js/experience-analyzer.min.js`, `inc/analytics.php`,
  `inc/analytics-protocol.php`, `template-parts/cookie-consent.php`.
- Authoring only (9): `scripts/sync-analytics.py` and
  `tests/analytics/{README.md,bootstrap.php,browser-consent.test.cjs,consent.test.cjs,relay.php,rendered-card.cjs,rendered-card.php,test_sync_analytics.py}`.

The boundary's corresponding build-input pin changed from
`116a4c28d537a842d3c34de8383c242d67e476a6b6079d6f66af9ab594baa4af` to
`c1e5eb65ffb4a574482ee7214176e8e817a92028dbf6b02fef900b37f9396487`. The old
digest was verified against the exact HEAD blob. No wildcard exclusions,
packager checks, runtime guards, or package version changed.

## Generated translation references

The full native build regenerated `languages/skyyrose-flagship-2.pot` line
references after the source commit hooks formatted PHP. Removing only the `#:`
reference lines makes the previous/current catalogs identical: no message IDs or
translations changed. Retaining the regenerated references is required for CI's
post-build clean-diff gate.

## Local verification

- Current-scenes guard: passed after the three scoped digest updates.
- Negative integrity tests: 17 passed.
- Canonical registry compatibility projections: passed.
- Product presentation registry tests: 3 passed.
- Native fixture preparation: all 7 pinned WordPress 7.1 / WooCommerce 11.1.0
  file hashes passed.
- Full first package build/verify: passed, 580 runtime entries.
- ZIP contents: all 7 new analytics runtime files present; all 9 authoring
  additions excluded; no tests/scripts in the release archive.
- Full repeat build/verify/package: passed. `cmp` confirmed byte-identical
  580-entry ZIPs, SHA-256
  `406bf1bd55e1e162c64188c9a048b48ae6ab518cf2ca33f94260d42603d48c57`.
- SHA-256 snapshots of every modified tracked file before/after the repeat are
  identical, and the modified-file sets match. Because the intended repair is
  uncommitted, this is the local equivalent of confirming the build introduces
  no additional diff; CI must still run `git diff --exit-code` on the committed
  candidate.
- Full pipeline logs: `/tmp/pr998-v2-package-first.log` and
  `/tmp/pr998-v2-package-second.log`. The first archive copy is
  `/tmp/pr998-v2-first-qualified.zip`.
- No tests, guards, toolchain pins, approved scenes, product truth, or runtime
  code were weakened/changed by this repair. Package output remains explicitly
  `deployment_authorized: false` and records the local source as dirty until
  this scoped repair is committed.

Toolchain: Python 3.12.12 / Pillow 12.3.0 from the existing virtual environment;
Node 22.23.2 and npm 10.9.8 selected through npm exec; cwebp 1.6.0 on macOS
ARM64. CI remains the separate Ubuntu ARM64 execution gate. All checks are
offline/source or read-only fixture downloads; no live authenticated commerce,
staging, production, or provider execution occurred.
