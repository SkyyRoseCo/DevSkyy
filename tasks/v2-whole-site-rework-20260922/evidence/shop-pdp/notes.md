# Agent C evidence — shop archive, taxonomy, PDP, card (2026-09-22)

Fixture: `php -S 127.0.0.1:8792 -t <repo>` (plain document root, no router), browsed at
`/tools/v2-theme-preview.php?route=…`. Capture script: `capture.cjs` (Playwright chromium from
/Users/theceo/DevSkyy/node_modules, 1440×900 and 390×844, fullPage, scroll-through so native lazy
images load, `pageerror` + console errors + failed requests + ≥400 responses collected into
`browser-results.json`). Final run: `captured` timestamp inside `browser-results.json` (20:37:54Z).

## Routes captured
| file | route | result |
| --- | --- | --- |
| shop-1440.png / shop-390.png | `?route=shop` | 200 · 5 cards · 4 / 1 columns · 0 framed cards · 0 page errors · 0 failed requests |
| product-br-004-{1440,390}.png | `?route=product&sku=br-004` | 200 · approved styling view only (opening-media status REJECTED_AUTHENTICITY → native gallery suppressed) · 4 related cards · sticky gallery at 1440 (`position: sticky`), static at 390 |
| product-sg-005-{1440,390}.png | `?route=product&sku=sg-005` | 200 · native gallery path · 4 related cards |
| product-lh-004-{1440,390}.png | `?route=product&sku=lh-004` | 200 · crimson accent via `data-collection="love-hurts"` |
| product-kids-001-{1440,390}.png | `?route=product&sku=kids-001` | 200 · rose accent |
| product-br-003-{1440,390}.png | `?route=product&sku=br-003` | 422 fail-closed (jersey has no verified fixture media) — expected; the one ≥400 response and console error in the run is this page itself |
| shop-quick-view-{1440,390}.png | quick view opened from the first shop card | dialog open, name/price/availability/excerpt/image populated from the card, status = fixture "open the piece" copy (no `sr2-quick-view-product` meta in the fixture), focus on Close, opener `aria-expanded="true"`; Escape closes and returns focus to the opener |
| product-br-004-size-guide-1440.png | size guide opened from the buy column | dialog open, 3 steps, focus on Close; Escape closes, focus returns to `[data-size-guide-open]` |

## Journey (browser-results.json → `journey`)
- Variation: `#preview-size` set to `M` (fixture select; native `wc-add-to-cart-variation` is not loaded in the fixture).
- Buy-column tab order (from the first control): size select → quantity → "Secure this piece" → "Fit + size guide" → "Shipping + Returns" → tab "Description" → tab "Additional information" → first related card media → related title. DOM order = visual order (no CSS `order`).
- 0 `pageerror`, 0 console errors, 0 failed requests on every 200 route at both widths.

## Judged against §1 (eyes-on, fresh copies read by hash-suffixed name)
- Shop: quiet arrival band (eyebrow "The House Edit", Archivo h1, collection hairline links; count + native ordering + filters disclosure right), then the garment grid on #111 tiles at 3:4, contain-fit; no frames. One focal point (the grid).
- PDP: gallery left / buy column right at 1440, stacked at 390; tabs as a 60ch reading column; related grid uses the same card; closing `.sr2-chapter` for the collection with the hero picture at 16:9 (3:2 on mobile).
- Dialogs: house dialog language (#111 panel, hairline border, accent top rule, `.sr2-dialog-head` + `.sr2-icon-button` close, `.sr2-control` actions).

## Left open / not verified here
- Real WooCommerce gallery (FlexSlider thumbs, zoom, variation image swaps) and the native ordering auto-submit are not exercised by the fixture — CSS for `.flex-control-thumbs`, `.woocommerce-tabs`, `table.shop_attributes`, `.related ul.products` is written against Woo 11.1 markup but only the fixture's mirrored structure was seen in a browser.
- `woocommerce_product_related_products_heading` filter ("More from <collection>") cannot fire in the fixture (add_filter is a no-op there); the fixture prints "More from the house".
- Kids Capsule closing chapter on mobile crops the `hero_mobile` lockup art at 3:2 with `--sr2-focal` default (50% 40%); founder-approved asset, but worth a focal review.
- Fixture preview-gallery thumbnails (`.sr2-preview-gallery__thumbs`) are fixture chrome, not Woo markup.
