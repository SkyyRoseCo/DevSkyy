#!/usr/bin/env bash
set -euo pipefail

THEME_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$THEME_DIR"

find . -name '*.php' -not -path './vendor/*' -print0 | xargs -0 -n1 php -l >/dev/null
for document in theme.json data/product-presentation-registry.json data/image-optimization.json data/opening-product-media.json data/font-provenance.json data/collection-hero-motion.json; do
	jq empty "$document"
done

# Page typography is a shippable dependency; collection scripts remain artwork
# until their provenance is independently recorded. A font filename is never
# treated as a license grant.
font_manifest="data/font-provenance.json"
license_path="$(jq -r '.license_bundle.text_path' "$font_manifest")"
license_hash="$(jq -r '.license_bundle.text_sha256' "$font_manifest")"
test -s "$license_path" || { echo "Missing font license bundle: $license_path" >&2; exit 1; }
if [[ "$(shasum -a 256 "$license_path" | awk '{print $1}')" != "$license_hash" ]]; then
	echo "Font license bundle hash drift: $license_path" >&2
	exit 1
fi
while IFS=$'\t' read -r font_path font_hash; do
	test -s "$font_path" || { echo "Missing registered page font: $font_path" >&2; exit 1; }
	if [[ "$(shasum -a 256 "$font_path" | awk '{print $1}')" != "$font_hash" ]]; then
		echo "Page font hash drift: $font_path" >&2
		exit 1
	fi
done < <(jq -r '.page_fonts[] | [.path, .sha256] | @tsv' "$font_manifest")
while IFS= read -r artwork_face; do
	if rg -Fq "$artwork_face" assets/css theme.json; then
		echo "Unproven collection artwork face registered as page typography: $artwork_face" >&2
		exit 1
	fi
done < <(jq -r '.artwork_only[] | .family + "|" + .path' "$font_manifest" | cut -d'|' -f1)

python3 scripts/build-product-presentation-registry.py --check
python3 ../../tools/v2-source-certification/check-commerce-projection.py --check
python3 scripts/validate-opening-product-media.py
python3 scripts/validate-collection-hero-motion.py
python3 scripts/build-pot.py --check
php scripts/test-marketplace-registry.php
node scripts/build-assets.mjs --check
node scripts/build-critical-css.mjs --check

while IFS= read -r base; do
	for width in 640 1024 1440; do
		asset="assets/sot/images/hero/responsive/${base}-${width}w.webp"
		test -s "$asset" || { echo "Missing optimized hero derivative: $asset" >&2; exit 1; }
		bytes="$(wc -c < "$asset" | tr -d '[:space:]')"
		if [ "$bytes" -gt 260000 ]; then
			echo "Optimized hero derivative exceeds 260KB: $asset" >&2
			exit 1
		fi
	done
done < <(jq -r '.hero_bases[]' data/image-optimization.json)

# Editorial scenes that are configured for responsive delivery are governed by
# the same byte budget as hero imagery. This prevents a later template change
# from silently restoring an original multi-megabyte scene to mobile visitors.
editorial_max_bytes="$(jq -r '.policy.max_served_editorial_bytes' data/image-optimization.json)"
while IFS=$'\t' read -r derivative_root basename widths; do
	while IFS= read -r width; do
		asset="${derivative_root}/${basename}-${width}w.webp"
		test -s "$asset" || { echo "Missing optimized editorial derivative: $asset" >&2; exit 1; }
		bytes="$(wc -c < "$asset" | tr -d '[:space:]')"
		if [ "$bytes" -gt "$editorial_max_bytes" ]; then
			echo "Optimized editorial derivative exceeds ${editorial_max_bytes} bytes: $asset" >&2
			exit 1
		fi
	done < <(printf '%s\n' "$widths" | jq -r '.[]')
done < <(jq -r '.editorial_derivative_sets[]? | [.derivative_root, .basename, (.widths | tojson)] | @tsv' data/image-optimization.json)

# Logos are reusable brand graphics, not scenery. They must remain compositable
# over the collection worlds, so alpha-channel loss is a shipping failure.
while IFS= read -r asset; do
	test -s "$asset" || { echo "Missing transparent brand asset: $asset" >&2; exit 1; }
	if ! identify -format '%[channels]' "$asset" | grep -q 'a'; then
		echo "Brand asset lost its transparent alpha channel: $asset" >&2
		exit 1
	fi
done < <(jq -r '.transparent_brand_assets[]' data/image-optimization.json)

product_media_max_bytes="$(jq -r '.delivery.max_bytes' data/opening-product-media.json)"
while IFS= read -r derivative; do
	test -s "$derivative" || { echo "Missing opening product-media derivative: $derivative" >&2; exit 1; }
	bytes="$(wc -c < "$derivative" | tr -d '[:space:]')"
	if [ "$bytes" -gt "$product_media_max_bytes" ]; then
		echo "Opening product-media derivative exceeds ${product_media_max_bytes} bytes: $derivative" >&2
		exit 1
	fi
done < <(jq -r '.products[] | .views[]? | .derivative // empty' data/opening-product-media.json)

STYLE_VERSION="$(sed -n 's/^Version:[[:space:]]*//p' style.css | head -n1)"
PACKAGE_VERSION="$(jq -r '.version' package.json)"
STABLE_TAG="$(sed -n 's/^Stable tag:[[:space:]]*//p' readme.txt | head -n1)"
if [[ -z "$STYLE_VERSION" || "$STYLE_VERSION" != "$PACKAGE_VERSION" || "$STYLE_VERSION" != "$STABLE_TAG" ]]; then
	echo "Theme version drift: style=$STYLE_VERSION package=$PACKAGE_VERSION readme=$STABLE_TAG" >&2
	exit 1
fi

for required in \
	404.php archive.php front-page.php home.php index.php page.php search.php single.php \
	template-collection.php woocommerce/archive-product.php woocommerce/cart/cart.php \
	woocommerce/checkout/form-checkout.php woocommerce/checkout/thankyou.php \
	woocommerce/content-product.php woocommerce/single-product.php \
	theme.json screenshot.png readme.txt README.md CHANGELOG.md LICENSE.txt rtl.css editor-style.css \
	npm-shrinkwrap.json \
	languages/skyyrose-flagship-2.pot; do
	test -s "$required" || { echo "Missing required marketplace artifact: $required" >&2; exit 1; }
done

if rg -n --glob '!node_modules/**' --glob '!dist/**' --glob '!scripts/verify-marketplace.sh' --glob '!README.md' --glob '!readme.txt' --glob '!CHANGELOG.md' --glob '!assets/js/lib/three-r170/**' \
	'\b(TODO|FIXME|Lorem ipsum|dummy data)\b' .; then
	echo 'Placeholder marker found in delivered theme.' >&2
	exit 1
fi

if rg -n --glob '!scripts/verify-marketplace.sh' 'Cormorant Garamond|Playfair Display|Bebas Neue|Yellowtail' \
	theme.json editor-style.css rtl.css assets/css inc template-parts ./*.php; then
	echo 'Retired font found in marketplace architecture.' >&2
	exit 1
fi

echo 'SkyyRose Flagship 2 marketplace verification passed.'
