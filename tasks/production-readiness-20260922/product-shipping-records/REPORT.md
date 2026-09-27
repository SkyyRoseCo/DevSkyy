# Product shipping records — 2026-09-23

Created canonical shipping records for all 33 existing SKUs. No duplicate products or WooCommerce mutations.

Each record separates unpackaged item weight (grams) from a single sellable unit packed parcel: total weight (grams), outer length/width/height (centimeters), and packaging reference. Units define the input convention, not measured facts. All six values per SKU remain null: no actual shipping measurements were supplied or found in the canonical records. Fabric GSM, sizing and artwork dimensions are not parcel measurements. No customs code, country of origin or carrier was inferred.

`get_product(sku)` exposes the shipping object and six named gaps per SKU (198 gaps total). These are completion records, not rate-ready products. Multi-item parcel packing and variation-specific differences still require actual fulfillment specifications.

## Evidence and scope

- `completion-sheet.csv` and `shipping-records.json` are generated consumers, never editable sources of truth. Regenerate with `PYTHONPATH=. python3 tasks/production-readiness-20260922/product-shipping-records/generate_sheet.py`.
- `preservation.json` proves all33 existing product records equal the parent-captured baseline after excluding the new shipping key.
- `source-divergence.json` records main-checkout/RC differences without reconciling unrelated facts. Main's correction entries have no entries absent from RC, but some garment, dossier, catalog and image values differ. Registry version is not treated as proof of freshness. RC remains based on the earlier exact origin/main import.
- Root AGENTS.md read. Local .wolf/memory.md absent; main-checkout notes consulted as context only. No memory edited.
- Authentication not applicable: local schema/data work only. No external shipping connection established.

## Validation

`python3 -m unittest discover -s tests -p test_product_shipping_records.py -v`: 5 tests passed (fixture unknown fields/gaps, populated fixture, invalid values/units, preservation/idempotence, preserving existing shipping records). Real records are not required to stay null by the tests.

`python3 scripts/sync_product_registry.py` and `--check`: passed, compatibility projections remain consistent. `git diff --check`: passed.

## Files changed by this task

- `skyyrose/core/product_registry.py`: atomic, locked, missing-only shipping initializer, explicit empty schema, and fail-closed measurement validation.
- `skyyrose/core/product.py`: expose shipping and absent field paths.
- `wordpress-theme/skyyrose-flagship/data/logo-registry.json`: shipping objects for33.
- `tests/test_product_shipping_records.py`: focused regression coverage.
- This report directory: generated completion sheet, evidence, generator and report.

Existing dirty files and founder facts preserved. No commit, push, deployment, live product mutation, order or carrier account operation performed.

Follow-up validation rejects missing/unsupported units, malformed shapes, nonpositive/nonfinite/bool/string measurements, and blank packaging references. Black formatting applied to touched Python files. Local default `python3 -m black` was unavailable; installed `black` CLI succeeded.
