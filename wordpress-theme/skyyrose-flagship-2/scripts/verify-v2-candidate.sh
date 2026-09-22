#!/usr/bin/env bash
# V2 candidate self-healing gate: source failures fail before staging does.
set -euo pipefail

THEME_DIR="${1:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"
REPO_ROOT="$(cd "$THEME_DIR/../.." && pwd)"

require_file() {
	if [[ ! -f "$THEME_DIR/$1" ]]; then
		echo "FAIL missing required V2 route: $1" >&2
		exit 1
	fi
}

for route in \
	front-page.php page.php home.php single.php archive.php search.php 404.php page-wishlist.php \
	template-collection.php functions.php header.php footer.php \
	template-parts/home/kids-capsule-reveal.php \
	template-parts/journal-press-fallback.php \
	template-immersive-signature.php template-immersive-black-rose.php \
	template-immersive-love-hurts.php template-immersive-kids-capsule.php \
	woocommerce/archive-product.php woocommerce/content-product.php woocommerce/single-product.php \
	woocommerce/cart/cart.php woocommerce/checkout/form-checkout.php woocommerce/checkout/thankyou.php; do
	require_file "$route"
done

for approved_visual in \
	assets/sot/images/hero/black-rose-lake-merritt-monument-v2.png \
	assets/sot/images/hero/black-rose-typography-star-salon-v3.png \
	assets/sot/images/hero/love-hurts-golden-gate-monument-v2.png \
	assets/sot/images/hero/signature-golden-gate-monuments-v2.webp \
	assets/sot/images/hero/black-rose-bay-bridge-monuments-v4.webp \
	assets/sot/images/hero/love-hurts-rose-aisle-monuments-v3.webp \
	assets/sot/images/hero/kids-capsule-heir-throne-v3.webp \
	assets/sot/images/home/on-model/signature-sg-005.webp \
	assets/sot/images/home/on-model/black-rose-br-004.webp \
	assets/sot/images/home/on-model/love-hurts-lh-004.webp \
	assets/sot/images/home/on-model/kids-capsule-kids-001.webp \
	assets/sot/images/home/on-model/kids-capsule-mascot-red-guard.webp \
	assets/sot/images/home/on-model/kids-capsule-mascot-purple-guard.webp \
	assets/sot/images/products/kids-002-purple-set.jpeg \
	assets/sot/images/products/kids-001-product-proof-400.webp \
	assets/sot/images/products/kids-002-product-proof-400.webp \
	assets/sot/brand/skyyrose-logo-animated-384w.webp \
	assets/sot/brand/skyyrose-logo-still-384w.webp; do
	require_file "$approved_visual"
done

if ! rg -q "function skyyrose2_asset_suffix" "$THEME_DIR/functions.php"; then
	echo "FAIL asset fallback missing: V2 must never enqueue absent minified bundles" >&2
	exit 1
fi

if ! rg -q "skyyrose2_seo_head" "$THEME_DIR/functions.php" || ! rg -q "skyyrose2_schema_head" "$THEME_DIR/functions.php"; then
	echo "FAIL SEO metadata/schema adapter missing" >&2
	exit 1
fi

if ! rg -q "woocommerce_add_to_cart_fragments" "$THEME_DIR/functions.php"; then
	echo "FAIL cart fragment adapter missing" >&2
	exit 1
fi

if ! rg -q "function skyyrose2_registry_reconciliation_report" "$THEME_DIR/functions.php" || \
	! rg -q "admin_notices.*skyyrose2_registry_reconciliation_notice|add_action\( 'admin_notices', 'skyyrose2_registry_reconciliation_notice'" "$THEME_DIR/functions.php"; then
	echo "FAIL published WooCommerce SKU to presentation-registry reconciliation missing" >&2
	exit 1
fi

if ! rg -q "data-brand-animation" "$THEME_DIR/functions.php" || ! rg -q "data-brand-animation" "$THEME_DIR/assets/js/theme.js"; then
	echo "FAIL optimized SkyyRose global header animation adapter missing" >&2
	exit 1
fi

if rg -q "preventDefault" "$THEME_DIR/assets/js/theme.js"; then
	echo "FAIL scroll/input cancellation detected in V2 motion runtime" >&2
	exit 1
fi

if ! rg -q "data-home-model-loop" "$THEME_DIR/front-page.php" || \
	! rg -q "data-home-model-toggle" "$THEME_DIR/front-page.php" || \
	! rg -q "data-loop-copy" "$THEME_DIR/front-page.php"; then
	echo "FAIL V2 homepage model loop markup or accessible controls missing" >&2
	exit 1
fi

hero_model_block="$(sed -n '/\$hero_models = array(/,/^);/p' "$THEME_DIR/front-page.php")"
hero_model_count="$(printf '%s\n' "$hero_model_block" | rg -c "'slug'[[:space:]]*=>" || true)"
if [ "$hero_model_count" -ne 3 ] || printf '%s\n' "$hero_model_block" | rg -q "kids-capsule"; then
	echo "FAIL V2 homepage opening hero must contain only Signature, Black Rose, and Love Hurts; Kids Capsule is reserved for its dedicated reveal" >&2
	exit 1
fi

for opening_collection in signature black-rose love-hurts; do
	if ! printf '%s\n' "$hero_model_block" | rg -q "'slug'[[:space:]]*=>[[:space:]]*'$opening_collection'"; then
		echo "FAIL V2 homepage opening hero missing $opening_collection" >&2
		exit 1
	fi
done

if ! rg -q "heroModelLoop" "$THEME_DIR/assets/js/theme.js" || \
	! rg -q "sr-home-model-loop" "$THEME_DIR/assets/css/theme.css" || \
	! rg -q "prefers-reduced-motion: reduce" "$THEME_DIR/assets/css/theme.css"; then
	echo "FAIL V2 homepage model loop runtime or motion fallback missing" >&2
	exit 1
fi

if ! rg -q "data-feature-id=\"kids-royal-procession-v1\"" "$THEME_DIR/template-parts/home/kids-capsule-reveal.php" || \
	! rg -q "data-house-royal-procession" "$THEME_DIR/template-parts/home/kids-capsule-reveal.php" || \
	! rg -q "data-procession-chapter=\"invitation\"" "$THEME_DIR/template-parts/home/kids-capsule-reveal.php" || \
	! rg -q "data-procession-chapter=\"guardians\"" "$THEME_DIR/template-parts/home/kids-capsule-reveal.php" || \
	! rg -q "data-procession-chapter=\"heir\"" "$THEME_DIR/template-parts/home/kids-capsule-reveal.php"; then
	echo "FAIL Kids Capsule Royal Procession semantic chapter contract missing" >&2
	exit 1
fi

if ! rg -q "function skyyrose2_get_products_by_skus" "$THEME_DIR/functions.php" || \
	! rg -Fq "array( 'kids-001', 'kids-002' )" "$THEME_DIR/front-page.php" || \
	! rg -q "required_collection" "$THEME_DIR/functions.php"; then
	echo "FAIL Kids Capsule exact-SKU collection resolver missing" >&2
	exit 1
fi

if ! rg -q "function skyyrose2_presentation_registry" "$THEME_DIR/functions.php" || \
	! rg -q "woocommerce_cart_is_empty" "$THEME_DIR/woocommerce/cart/cart.php" || \
	! rg -Fq "function_exists( 'wc_get_page_permalink' )" "$THEME_DIR/404.php" || \
	rg -Fq "if ( empty( \$products ) && 'pre-order' === \$collection )" "$THEME_DIR/functions.php"; then
	echo "FAIL V2 truth and WooCommerce compatibility contract missing" >&2
	exit 1
fi

if ! rg -q '"state": "FROZEN"' "$REPO_ROOT/.fashion-theme/candidate-manifest.json" || \
	rg -q '"state": "BLOCKED"|"state": "UNFROZEN"|"status": "UNKNOWN"' "$REPO_ROOT/.fashion-theme/catalog-binding.json" "$REPO_ROOT/.fashion-theme/shot-manifest.json"; then
	echo "FAIL candidate-bound evidence is blocked, unknown, or unfrozen" >&2
	exit 1
fi

reveal_line="$(rg -n "template-parts/home/kids-capsule-reveal" "$THEME_DIR/front-page.php" | cut -d: -f1)"
collections_line="$(rg -n 'section id="collections"' "$THEME_DIR/front-page.php" | cut -d: -f1)"
if [ -z "$reveal_line" ] || [ -z "$collections_line" ] || [ "$reveal_line" -le "$collections_line" ]; then
	echo "FAIL Kids Capsule reveal must exist exactly once after the three-world opening" >&2
	exit 1
fi

if [ "$(rg -c "template-parts/home/kids-capsule-reveal" "$THEME_DIR/front-page.php")" -ne 1 ]; then
	echo "FAIL Kids Capsule reveal placement is duplicated" >&2
	exit 1
fi

if ! rg -q "Kids Capsule Royal Procession" "$THEME_DIR/assets/js/kids-capsule-reveal.js" || \
	rg -q "preventDefault|wheel|touchmove" "$THEME_DIR/assets/js/kids-capsule-reveal.js" || \
	! rg -q "prefers-reduced-motion: reduce" "$THEME_DIR/assets/css/theme.css" || \
	! rg -q "sr-kids-procession" "$THEME_DIR/assets/css/theme.css"; then
	echo "FAIL Kids Capsule progressive enhancement or fallback contract missing" >&2
	exit 1
fi

if rg -q '\$[0-9]|[0-9]+[.]?[0-9]* USD|hard.?coded (price|stock)' "$THEME_DIR/template-parts/home/kids-capsule-reveal.php"; then
	echo "FAIL hard-coded commerce truth detected in Kids Capsule reveal" >&2
	exit 1
fi

# Anti-generic floor: collection storytelling must be implemented as distinct
# compositions and card systems, never merely a shared template with recolored copy.
for collection in signature black-rose love-hurts kids-capsule; do
	if ! rg -Fq "[data-collection=\"$collection\"] .sr2-collection-identity" "$THEME_DIR/assets/css/theme.css"; then
		echo "FAIL generic collection hero: missing $collection composition" >&2
		exit 1
	fi
	if ! rg -Fq ".sr2-c-product-portal[data-presentation=\"$collection\"]" "$THEME_DIR/assets/css/theme.css"; then
		echo "FAIL generic product card: missing $collection card direction" >&2
		exit 1
	fi
	for width in 640w 970w; do
		statue="$THEME_DIR/assets/sot/images/product-card-portals/$collection-portal-statue-$width.webp"
		if [[ ! -s "$statue" ]]; then
			echo "FAIL collection portal statue missing: $collection $width" >&2
			exit 1
		fi
	done
done

if ! rg -q 'data-card-direction="ornate-frame"' "$THEME_DIR/template-parts/commerce/product-card.php" || \
	! rg -q 'data-portal-frame="<\?php echo esc_attr' "$THEME_DIR/template-parts/commerce/product-card.php" || \
	! rg -q 'sr2-c-product-portal__statue' "$THEME_DIR/template-parts/commerce/product-card.php" || \
	! rg -q 'sr2-c-product-portal__reel' "$THEME_DIR/template-parts/commerce/product-card.php" || \
	! rg -q 'sr2-c-product-portal__frame-crest' "$THEME_DIR/template-parts/commerce/product-card.php" || \
	! rg -q 'skyyrose2_product_verified_card_media' "$THEME_DIR/template-parts/commerce/product-card.php" || \
	! rg -q 'return array_slice\( \$ordered, 0, 3 \);' "$THEME_DIR/functions.php" || \
	! rg -q 'skyyrose2_render_product_loop_card\( \$piece' "$THEME_DIR/functions.php" || \
	! rg -q 'data-reel-count' "$THEME_DIR/template-parts/commerce/product-card.php"; then
	echo "FAIL approved ornate product-card frame or verified view reel missing" >&2
	exit 1
fi

if ! rg -q 'skyyrose2_product_verified_card_media' "$THEME_DIR/template-parts/commerce/product-hero.php" || \
	! rg -q 'woocommerce_product_get_image_id' "$THEME_DIR/template-parts/commerce/product-hero.php" || \
	! rg -q 'On-model product imagery is being verified' "$THEME_DIR/template-parts/commerce/product-hero.php"; then
	echo "FAIL product page does not enforce the approved on-model media sequence" >&2
	exit 1
fi

if ! jq -e '
	(.products | length) == 33 and
	all(.products[]; (.views[0].role // "") == "on_model_front")
' "$THEME_DIR/data/opening-product-media.json" >/dev/null; then
	echo "FAIL every product card requires an approved on-model lead" >&2
	exit 1
fi

if ! rg -q 'data-quick-view' "$THEME_DIR/template-parts/commerce/product-card.php" || \
	! rg -q 'sr2-quick-view' "$THEME_DIR/template-parts/commerce/quick-view.php" || \
	! rg -q 'showModal' "$THEME_DIR/assets/js/theme.js"; then
	echo "FAIL product-card quick-view layer missing" >&2
	exit 1
fi

# Every served monument hero has deterministic desktop/tablet/mobile WebP
# derivatives. Originals remain in the SOT for provenance; the storefront
# never pays the cost of serving the multi-megabyte source PNGs.
for hero_base in signature-golden-gate-monuments-v2 black-rose-bay-bridge-monuments-v4 love-hurts-rose-aisle-monuments-v3 kids-capsule-heir-throne-v3; do
	for width in 1440 1024 640; do
		variant="assets/sot/images/hero/responsive/${hero_base}-${width}w.webp"
		require_file "$variant"
		variant_bytes="$(stat -f '%z' "$THEME_DIR/$variant")"
		if [ "$variant_bytes" -gt 260000 ]; then
			echo "FAIL responsive hero exceeds 260KB: $variant ($variant_bytes)" >&2
			exit 1
		fi
	done
done

if ! rg -q 'function skyyrose2_collection_scene_product' "$THEME_DIR/functions.php" || \
	! rg -q 'sr2-world__product' "$THEME_DIR/template-collection.php"; then
	echo "FAIL collection Scroll World product proof binding missing" >&2
	exit 1
fi

if ! rg -q 'function skyyrose2_immersive_url' "$THEME_DIR/functions.php" || \
	! rg -q 'Enter the full scene' "$THEME_DIR/template-collection.php" || \
	! rg -q "'immersive-signature'.*template-immersive-signature.php" "$THEME_DIR/inc/presentation-registry.php"; then
	echo "FAIL dedicated immersive collection routes are not provisioned and linked" >&2
	exit 1
fi

if ! rg -q "'worlds'.*'path'.*'worlds'" "$THEME_DIR/inc/presentation-registry.php" || \
	! rg -q "'immersive-signature'.*'slug'.*'signature'.*'parent'.*'worlds'" "$THEME_DIR/inc/presentation-registry.php" || \
	! rg -Fq "sanitize_title( ! empty( \$data['slug'] ) ? \$data['slug'] : \$slug )" "$THEME_DIR/inc/demo-import.php"; then
	echo "FAIL immersive importer path/slug contract missing" >&2
	exit 1
fi

if ! rg -q "template-parts/journal-press-fallback" "$THEME_DIR/home.php" || \
	! rg -q "template-parts/journal-press-fallback" "$THEME_DIR/index.php"; then
	echo "FAIL Journal press fallback is not shared by the production archive templates" >&2
	exit 1
fi

if ! rg -q "privacy-policy" "$THEME_DIR/functions.php" || \
	! rg -q "accessibility" "$THEME_DIR/functions.php"; then
	echo "FAIL footer discoverability for legal and accessibility pages is missing" >&2
	exit 1
fi

if ! rg -q 'sr2-scene-effect--bridge-lights' "$THEME_DIR/template-collection.php" || \
	! rg -q 'sr2-scene-effect--petals' "$THEME_DIR/template-collection.php" || \
	! rg -q 'sr2-cloud-roll' "$THEME_DIR/assets/css/theme.css" || \
	! rg -q 'sr2-petal-fall' "$THEME_DIR/assets/css/theme.css"; then
	echo "FAIL collection-specific hero atmosphere animation contract missing" >&2
	exit 1
fi

find "$THEME_DIR" -name '*.php' -print0 | xargs -0 -n1 php -l >/dev/null
node --check "$THEME_DIR/assets/js/theme.js"
node --check "$THEME_DIR/assets/js/kids-capsule-reveal.js"
jq empty "$REPO_ROOT/.fashion-theme/v2-remodel-ledger.json" "$REPO_ROOT/.fashion-theme/catalog-binding.json" "$REPO_ROOT/.fashion-theme/shot-manifest.json"

transparency_manifest="$THEME_DIR/data/brand-asset-transparency.json"
if [[ ! -f "$transparency_manifest" ]]; then
	echo "FAIL standalone brand-asset transparency manifest missing" >&2
	exit 1
fi
jq empty "$transparency_manifest"
while IFS= read -r asset; do
	if [[ ! -f "$THEME_DIR/$asset" ]]; then
		echo "FAIL transparent brand asset missing: $asset" >&2
		exit 1
	fi
done < <(jq -r '.transparent_assets[]' "$transparency_manifest")

if command -v identify >/dev/null 2>&1; then
	while IFS= read -r asset; do
		alpha_report="$(identify -format '%[channels]|%[opaque]\n' "$THEME_DIR/$asset" | head -n 1)"
		if [[ "$alpha_report" != *a* ]] || [[ "$alpha_report" != *"|False"* ]]; then
			echo "FAIL brand asset is not transparently encoded: $asset ($alpha_report)" >&2
			exit 1
		fi
	done < <(jq -r '.transparent_assets[]' "$transparency_manifest")
else
	echo "WARN ImageMagick identify unavailable; brand alpha bytes not re-audited" >&2
fi
git -C "$REPO_ROOT" diff --check -- "$THEME_DIR" "$REPO_ROOT/.fashion-theme" "$REPO_ROOT/.wolf"

echo "PASS V2 candidate source gate"
