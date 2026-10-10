---
applyTo: 'wordpress-theme/**/*.php,wordpress-theme/**/*.inc,wordpress-theme/**/*.js,wordpress-theme/**/*.jsx,wordpress-theme/**/*.ts,wordpress-theme/**/*.tsx,wordpress-theme/**/*.css,wordpress-theme/**/*.scss'
---

# WordPress and WooCommerce review guidance

- Review against the actual theme or package being changed. V1 and
  `skyyrose-flagship-2` have separate build and verification commands; consult
  that package's `package.json` and nearby `AGENTS.md` files.
- The V1 SkyyRose theme declares PHP 8.2. Do not flag PHP 8 features as
  incompatible based on a generic PHP 7.4 baseline. Follow the package's WPCS,
  PHP lint, JavaScript/CSS lint, and build configuration where applicable.
- WordPress security findings should identify a concrete missing boundary:
  validate/sanitize untrusted input, escape output for its context, check a
  capability for privileged writes, verify a nonce for CSRF-sensitive actions,
  provide a restrictive REST `permission_callback`, and use `$wpdb->prepare()`
  for variable SQL values. Avoid reporting a missing nonce as a defect when an
  authenticated REST mechanism or another valid boundary already protects the
  operation.
- Check WooCommerce hooks and APIs for correct lifecycle, idempotency, and error
  behavior. Keep customer data and credentials out of logs and responses.
  Preserve translations for user-facing strings and enqueue assets through
  WordPress APIs.
- Product imagery and facts must follow repository-wide registry authority.
  Check that image bindings resolve to approved source assets; filenames alone
  do not establish product identity. Review generated `.min.css`/`.min.js`
  against their source and build output; do not recommend hand-editing generated
  bundles.
- For V1, the owning package is `wordpress-theme/`; its `verify:full` runs lint
  and rebuilds CSS/JS/editorial assets. For V2, use
  `wordpress-theme/skyyrose-flagship-2/` scripts and its own source-integrity,
  verify, and packaging gates. A lint or preview pass does not establish live
  commerce or deployment success.
