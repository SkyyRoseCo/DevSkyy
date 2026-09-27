# Reference redesign and skill-readiness handoff — 2026-09-21

## Delivered

The audited skill entrypoints and Fashion Theme Team redesign routes are usable
for this task. Maintained correct/incorrect examples, instruction precedence,
product authority, environment discovery, and evidence boundaries were repaired.
All 18 bundled public authority captures were freshly retrieved; canonical,
installed, and DevSkyy-vendor full plugin verifiers passed. Both distributions
have zero drift. Example coverage remains PARTIAL outside the declared scope.
See [skill audit](skill-readiness-audit-20260921.md).

The reference-based homepage composition and global shell are installed on
https://staging-7e48-skyyrose.wpcomstaging.com/. Fifteen allowlisted runtime
files passed before/after SHA guards. Five editorial section templates were
added; existing hero motion, concierge, collection-world rail, native product
cards, commerce routes, menus, search, and bag hooks were retained. The existing
worlds rail is available in a native keyboard-operable disclosure.

The theme-owned returns-exchanges summary was updated to match the published
policy with compare-and-swap guards. The formal shipping policy and configuration
were preserved. Both normal and cache-busted service URLs passed readback.

## Verification

- Full theme verification passed; final generated CSS/JS freshness and critical
  rendering checks passed after the last mobile-card refinement.
- Critical CSS: 16,371 bytes / 16,384-byte hard cap.
- Local final browser interactions passed at 390, 768 and 1440 widths.
- Independent normal-URL staging browser checks passed at 390 and 1440: Ask Skyy,
  Escape/focus restoration, pause/play, worlds keyboard navigation, paused hidden
  videos, control bounds, no horizontal overflow and no page errors. Four served
  CSS/JS hashes matched the frozen source.
- Final public menu/search/bag/Quick View interactions passed at 390 and 1440;
  exact four featured product identities were checked in the rendered DOM.
- Final full theme ZIP: 563 runtime entries, SHA-256
  `b013b1155970287d20e0b19ada41c6d6c8a3d6a4c464e2510e3da895263fb39a`.
- Independent clean WordPress 7.1.1 / WooCommerce 11.1.1 installation: all 563
  hashes and lengths matched; activation and eight home/shop/cart/account
  desktop/mobile checks passed. Rollback restored 178 core files and the baseline.
- Split package: 178 core files plus 385 required-media files, stored in
  `/Users/theceo/.codex/worktrees/marketplace-split/DevSkyy/wordpress-theme/skyyrose-flagship-2/dist-marketplace-2.4.4-b013b115`.

Evidence: [staging evidence](evidence/reference-staging-20260921/README.md),
[policy readback](evidence/staging-policy-public-readback-20260921.json),
[installation report](/Users/theceo/.codex/worktrees/marketplace-split/DevSkyy/tasks/clean-install-b013b115.md).
Remote scoped rollback archive was downloaded; local SHA-256
`6f6b262362819352524e31a905098797f58f6d4c7d1c036915b81cb8e72570a7`.

## Remaining production decisions and boundaries

No production deployment or payment transaction occurred. The user explicitly
deferred payment testing until production. Merchant tax-engine/registration and
international fulfillment inputs remain unresolved; no tax rates, carrier
weights or destinations were invented.

The product-image red team still identifies BR-002 ankle-cuff and KIDS-002 sleeve-
patch fidelity gaps. Those products were excluded from the new four-piece home
feature. Existing bindings were preserved; no paid generation or new product
fact was introduced. This is not an all-catalog visual-fidelity certification.

This release is a verified staging candidate using existing SkyyRose imagery.
It is not founder acceptance, production payment certification, or marketplace
approval. Earlier installation/verification evidence remains historical and was
not substituted for this exact final candidate.
