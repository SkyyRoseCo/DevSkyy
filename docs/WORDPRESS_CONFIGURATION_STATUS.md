# SkyyRose WordPress configuration and ownership

**Last updated:** 2026-10-01. **Operational baseline:**
`a662e707d698a687d7d1d2efed3975b9aa7325b9`.

This record describes the current scoped storefront release and the captured
native configuration. Use [PRODUCTION_STATUS.md](PRODUCTION_STATUS.md) for the
dated target/CI/acceptance snapshot and [RUNBOOK.md](RUNBOOK.md) for execution
and recovery. Captured configuration must be refreshed immediately before
operation; source implementation alone does not establish current authenticated
runtime.

## Targets and theme state

| Target                                                             | Captured state                                                                            | Boundary                                                     |
| ------------------------------------------------------------------ | ----------------------------------------------------------------------------------------- | ------------------------------------------------------------ |
| Production `https://skyyrose.co`                                   | Active stylesheet `skyyrose-flagship` V1                                                  | V2 cutover not dispatched at the current snapshot            |
| Existing staging `https://staging-7e48-skyyrose.wpcomstaging.com/` | Active `skyyrose-flagship-2` V2 2.5.0; reviewed ZIP installed and 599 file hashes matched | Staging qualification is separate from production acceptance |
| Platform versions                                                  | WordPress 7.1.2, WooCommerce 11.1.2, PHP 8.4.26                                           | Authenticated captured versions; recheck for hosting drift   |

WordPress.com provides the native hosting/cache layer. Site identity comes from
actual authenticated target/readback evidence; an available credential or public
page cannot establish the intended account/site/scope. SSH and SFTP use their
respective `ssh.wp.com` and `sftp.wp.com` endpoints. Keep credentials in the
local or intended host's secret store and retain only redacted identity/outcome
evidence.

## Production native commerce baseline

Production currently has **33 published simple products**, native IDs/prices,
full-payment checkout, unmanaged quantities, no native size variations, and null
shipping-date promises. Staging's 220 product/variation records are a different
configuration. Do not synchronize staging into production or treat registry
edition size as a remaining stock balance.

| Native configuration       | Captured production value                                                                    | Cutover requirement                                           |
| -------------------------- | -------------------------------------------------------------------------------------------- | ------------------------------------------------------------- |
| Collections root           | Existing page 9327                                                                           | Preserve content/template/meta preimages                      |
| WooCommerce cart           | Existing page 9451                                                                           | Preserve ID, native shortcode/content, and option             |
| WooCommerce checkout       | Existing page 9452                                                                           | Preserve ID, native shortcode/content, and option             |
| WooCommerce shop           | Existing page 9836                                                                           | Preserve ID and option                                        |
| WooCommerce account        | Existing page 9710                                                                           | Preserve ID and option                                        |
| Search                     | Active Jetpack Search                                                                        | Preserve working actual positive/empty native Search          |
| Platform tracking controls | Stats inactive; WooCommerce analytics inactive; attribution `no` in reviewed target snapshot | Recheck current readback; controls alone do not prove privacy |
| Search privacy extension   | Separate reviewed MU artifact; preimage absent in the captured candidate                     | Install only with exact binding and operation ownership       |

The release may add only the ten owned new routes below, preserving the existing
Collections parent. They are planned additions, not claims that production pages
already exist or are published:

- `/collections/signature/`, `/collections/black-rose/`,
  `/collections/love-hurts/`, `/collections/kids-capsule/`
- `/worlds/` and its four collection children
- `/size-guide/`

The
[page plan](../tasks/production-final-pass-20261001/evidence/production-v2-page-plan-final.json),
[planner](../tasks/production-final-pass-20261001/plan_v2_pages.py), and
[operator](../tasks/production-final-pass-20261001/apply_v2_pages.php) own this
release's source/preimage/ownership checks and draft/publish/recovery journal.
Exact returned IDs and paths must come from actual readback. Reject collisions,
slug suffixes, unexpected rows, or merchant modifications.

## Source and data authority

The one editable product source is [logo-registry.json](../logo-registry.json),
a symlink to
[wordpress-theme/skyyrose-flagship/data/logo-registry.json](../wordpress-theme/skyyrose-flagship/data/logo-registry.json).
Complete reads use `from skyyrose.core.product import get_product`, or
`python -m skyyrose.core.product <sku>` for non-Python consumers. Unknown SKUs
raise and absent facts are named in `gaps`. CSVs, dossiers, asset manifests, and
the V2 presentation registry are projections/consumers, not editable fact
stores.

Corey's latest specifications as founder/maker are `FOUNDER_CONFIRMED`. Preserve
his exact wording, dimensions, ranges, artwork, materials, and placements. Apply
scoped corrections to the unified registry first and regenerate compatibility
projections; do not require independent manufacturer proof or invent missing
measurements. This documentation update changes no product records.

V2 template/bootstrap sources are at
[wordpress-theme/skyyrose-flagship-2/](../wordpress-theme/skyyrose-flagship-2/).
Native WooCommerce owns the actual store IDs, product types, prices, cart,
checkout, orders, and payments. The V2 presentation layer does not authorize a
product import, variation conversion, price edit, or inventory cap. See the
[WordPress codemap](CODEMAPS/wordpress.md).

## Search privacy, activation, and caches

The
[Search privacy MU extension](../tools/production-runtime/search-tracking-privacy.php)
and [publisher](../tools/production-runtime/publish-search-privacy.php) are
separate from the unchanged theme ZIP. Use exclusive operation ownership,
durable external intent, and inode-bound recovery. A same-byte foreign file is
not this operation's recoverable file.

The required order is: install inactive V2/ten drafts; install the MU extension;
record actual object/global edge-cache clears; require desktop/mobile actual
Search on still-active V1; guard all ten captured activation-option preimages;
switch through WordPress core and finish next-bootstrap/readback; publish only
ten owned drafts; clear caches and verify file/native configuration; record
actual deployment and six-profile acceptance evidence.

The captured snapshot disables three platform tracking controls, but active
Search originally emitted optional tracking. Privacy requires actual observed
request/handle/cookie evidence after the reviewed extension and cache clears.
CLI purge failures and supported authenticated hosting-clear confirmations are
distinct evidence; preserve both. Public HTTP 200 or a stale cached page is not
a cache-clear or privacy receipt.

## Deliberate scope limits

No product type, size/variation, stock, price, date, order, payment, or customer
changes are included. There is no database synchronization, demo importer, new
generation/paid provider run, asset upload, GLB acceptance, mascot activation,
other-service deployment, deletion, or backup pruning in this cutover. Existing
approved media remains the visual release boundary.

Source/offline procedure approval is distinct from execution clearance,
`V1_SEARCH_CHECKPOINT_PASS`, `DEPLOYED`, and `PRODUCTION_ACCEPTED`. Unknown
outcomes stop mutation and require read-only reconciliation; reviewed rollback
restores only owned unchanged state and exact captured V1 activation/options.
See [the runbook's recovery procedure](RUNBOOK.md#stop-reconcile-and-recover).
