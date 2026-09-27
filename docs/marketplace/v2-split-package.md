# SkyyRose V2 split package prototype

This prototype separates the verified `2.4.4` theme bundle into two install
artifacts without changing the runtime path of any file:

- `skyyrose-flagship-2-core.zip` contains PHP, templates, compiled CSS and
  JavaScript, runtime JSON, translations, licenses, and the WordPress theme
  screenshot.
- `skyyrose-flagship-2-required-media.zip` contains every shipped image, video,
  font, 3D model, and WebAssembly binary beneath `assets/`. This package is
  **required brand media**, not optional demo content. The storefront is not a
  complete SkyyRose experience until it is installed and verified.

The verified source bundle is
`wordpress-theme/skyyrose-flagship-2/dist/skyyrose-flagship-2.zip`, SHA-256
`e1a35cc901854714f471e1256e6f2aa60a4610788c07f033a65f7cc65f67ce5d`.
The split builder refuses a different source hash when the release command
passes `--expected-sha256`.

## Build

From the repository root:

```bash
python3 tools/v2-marketplace-package/build_split_package.py \
  --full-zip wordpress-theme/skyyrose-flagship-2/dist/skyyrose-flagship-2.zip \
  --expected-sha256 e1a35cc901854714f471e1256e6f2aa60a4610788c07f033a65f7cc65f67ce5d \
  --output-dir wordpress-theme/skyyrose-flagship-2/dist-marketplace-2.4.4-e1a35cc9
```

The build is deterministic. `split-release.json` records every artifact hash.
The three payload manifests record every original path, byte count, and SHA-256.
`optional-demo-manifest.json` is intentionally empty because the verified
bundle does not contain a separable demo-only payload.

## Install and rollback

Do not activate the core archive by itself. Install it into the WordPress themes
directory, then run the integrity-checked companion installer before activation:

```bash
RELEASE_DIR=wordpress-theme/skyyrose-flagship-2/dist-marketplace-2.4.4-e1a35cc9
python3 "$RELEASE_DIR/install-required-media.py" \
  --theme-dir /path/to/wp-content/themes/skyyrose-flagship-2 \
  --media-zip "$RELEASE_DIR/skyyrose-flagship-2-required-media.zip" \
  --media-manifest "$RELEASE_DIR/required-media-manifest.json" \
  --full-manifest "$RELEASE_DIR/full-payload-manifest.json" \
  --release-manifest "$RELEASE_DIR/split-release.json" \
  --expected-release-sha256 e15da9ce8e0883b568c67c9ff52d634b1096b0037a484fb1304e2715e95079cc
```

Obtain the expected release-manifest SHA-256 from the separately published
release record; do not copy it from the same untrusted download location. The
installer rejects POSIX and Windows traversal paths, duplicate or nonregular
entries, unmanifested files, excessive expansion ratios/sizes, missing files,
changed sizes, and hash mismatches. It reconstructs and verifies the
complete theme in a sibling staging directory, renames the existing core to
`.skyyrose-flagship-2-rollback`, then places the complete theme at the original
path. If the final rename fails, it restores the core. Keep the rollback copy
until the site has passed visual and commerce acceptance. To roll back after a
successful install, deactivate the theme, move the installed directory aside,
and rename `.skyyrose-flagship-2-rollback` to `skyyrose-flagship-2`.

## Release checks

```bash
python3 tools/v2-marketplace-package/test_split_package.py
```

The test proves deterministic artifact hashes, disjoint package membership,
exact union with the verified full bundle, structural exclusion of environment
files and build-dependency directories plus a scan for common secret formats,
preservation of all original paths and hashes, and successful
atomic reconstruction. Existing theme verification remains mandatory before a
new source bundle is accepted.

## Marketplace boundary

This is a packaging prototype, not marketplace certification. A distribution
channel still needs a supported buyer-facing upload/import experience, maximum
archive-size validation, licensing review for every font and media file,
third-party library notices, demo-content rules, update-channel behavior,
hosting filesystem/permission compatibility, support documentation, and an
external reviewer-environment test. No required SkyyRose media may be described
or sold as optional merely to satisfy an archive-size limit.
