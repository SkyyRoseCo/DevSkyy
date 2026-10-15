# V2 source certification

Scope: recover reproducible source for `skyyrose-flagship-2`, not new visual
approval, product synchronization, runtime remediation or deployment.

## Ownership and inputs

The sole editable product authority is root `logo-registry.json`, a symlink to
`wordpress-theme/skyyrose-flagship/data/logo-registry.json`. Current collection,
preorder, garment classification and merchandising assignments are read through
`skyyrose.core.product.get_product`. CSV and dossiers are compatibility projections.
Existing Jersey Series assignments were migrated unchanged into that registry;
their provenance is recorded as route configuration, not new founder testimony.

`inputs/product-sot.json` is an immutable historical media receipt identity at
the upstream revision in `build-inputs.json`. It is not another editable catalog.
Its original logical path was `data/product-sot.json`. Updating media bindings
requires reviewed source evidence and corresponding receipt reconciliation.
The consumer checks historical SKU/commerce/collection bindings against current
registry facts before building. It does not silently adopt stale product facts.
Historical media verification labels describe those media receipts, not the
validity of the founder's product specifications.

The immutable Woo sync projection is a verification input, not an instruction
to sync products. `check-commerce-projection.py` preserves the historical
compiler's product-field generation and checks it against the pinned upstream
projection without loading another checkout or making network calls. Its two
intentional adaptations are the immutable-input reader and output location.

## Commands

Use Node 22.23.2, npm 10.9.8, Python 3.12.12, PHP CLI >=8.3, jq, ripgrep,
ImageMagick (`identify`), Git and Bash. CI installs its PHP/ImageMagick packages
on Ubuntu 24.04. PHP is a lint/test tool; it does not generate archive bytes.

```sh
python3.12 -m venv .artifacts/v2-venv
. .artifacts/v2-venv/bin/activate
python -m pip install -r tools/v2-source-certification/requirements.txt
npm --prefix wordpress-theme/skyyrose-flagship-2 ci --ignore-scripts --no-audit --no-fund
python -m unittest discover -s tools/v2-source-certification -p 'test_*.py'
npm --prefix wordpress-theme/skyyrose-flagship-2 run package:theme
git diff --exit-code
```

The interpreter must actually be 3.12.12; a similarly named interpreter is not
proof. A fresh environment may also be provisioned with `uv venv --python
3.12.12`. No provider credentials, generation calls, SSH or WordPress writes are
required. The root Python application's large environment is not a dependency.

## Scene contract transition

Runtime order is blueprint -> selected placeholder -> C1 composition -> K1
motion. All nine current chapters end in K1 motion, which clears model layers
and uses its own poster. The historical founder-scene validator checks a
different representation: old base plates, alpha layers, source/output pixel
diffs, and the BR3 surgical edit. Those inputs are not the active K1 composition
pipeline. The validator is retained unchanged as `check:legacy-founder-scenes`;
it still fails when its historical assets are absent. It has not been turned
into a permissive validator.

The current gate checks the nine scene identities, exact effective casts,
collection membership, SOT binding, existing wiring flags, poster hashes, both
delivery renditions and all runtime PHP bytes. The K1 receipt and full-theme
deployment payload match the recovered manifest and encoded assets. They are
preserved in `tasks/v2-source-certification-20260905/provenance/` as evidence,
not build paths. The base BR2 cast was two SKUs; C1 added `br-004`, explicitly
recorded in the composition contract. K1 retains that cast. Current K1 delivery
is H.264 desktop/mobile with static poster fallback. The old scene-generation
contract's two-codec/100-percent candidate rubric remains a gate for that
authoring workflow; this phase does not claim a new generated candidate passed
it or override any rejected/stale product media.

Integrity checks certify the bytes and preserved recorded decisions; they do
not independently reapprove garment fidelity or run a new visual review.

## Generated output policy

`generated-outputs.json` enumerates all 16 outputs: fourteen minified CSS/JS
files, registry and POT. Minifiers are npm-shrinkwrap pinned. Minified outputs
have no trailing newline. Registry uses sorted JSON keys and final LF. POT
scans runtime PHP, is sorted and has a fixed header date. The current extracted message count is reported by the build. A source audit found one missing
`_n()` plural record (`%d published view` / `%d published views`); the extractor
now emits that record with plural translations and has regression coverage. Generated outputs remain
tracked and shipped. Pre-rendered media is an immutable input, not regenerated
by the canonical build.

The retired font reference in the one-shot C1 authoring script does not belong
to the runtime gate. That script remains preserved and excluded from release.
Runtime CSS also contained the retired name; its unavailable face was removed
while retaining the existing Georgia/serif fallback. No new font is bundled.
The runtime retired-font gate now includes CSS, which the old gate omitted.

## Integrity and package boundary

All 33 approved-front hashes and dimensions are checked at build and package
time; no per-request hashing was added. The opening-media validator still
checks source and derivative hashes, SKU sets and product hashes. The exact
16 stale / 9 missing-front / 5 rejected / 3 approved states stay locked.

`package-boundary.json` classifies every recovered theme file. Inclusion is
explicit and unknown/new files stop packaging. Source CSS/JS remain because
the existing enqueue code supports source fallback. Runtime image and video
delivery files, required fallbacks, PHP/templates, runtime JSON, translations
and theme/license documentation ship. Creative scripts, build tooling, QA
contact sheets/metadata and authoring masters do not. They remain in source.
The packager also rejects AppleDouble (`._*`), `.DS_Store`, and `__MACOSX`
entries even if accidentally marked for release. These filesystem sidecars
are not application assets. Theme README/changelog and license documentation
remain intentional handoff material, not evidence of additional runtime work.
Workstation paths in historical receipts are preserved as evidence but never
resolved by the build or shipped in the ZIP.

Packaging runs the full build and verification before writing a ZIP. Entries
are sorted, dated 1980-01-01, permission-normalized, and stored without an
additional compressor (media is already compressed). ZIP bytes are checked
against every selected file. `dist/release-manifest.json` is a sidecar to avoid
self-referential archive hashes. It binds commit, clean-state flag, build-input
hash, catalog/SOT, registry, runtime manifests, all package files, toolchain,
version and archive hash. A dirty-source sidecar is investigative, not a release.

CI is verification-only. No job has deployment credentials or write permission.
Its repeated-build check complements the separate isolated-checkout experiment.
The known jQuery defer defect and all runtime PHP/Woo surfaces are intentionally
preserved. Source certification is not runtime launch approval.

Before committing, a Git tree export can be packaged with `V2_SOURCE_TREE`
set to its exact 40-character tree ID. Such a sidecar records `git_commit` and
`source_clean` as null; it must never be represented as a clean commit build.
The final certification also builds a genuinely clean checkout of the committed
candidate with this override absent.
