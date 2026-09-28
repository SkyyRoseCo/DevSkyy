# Staging acceptance — candidate 1acde81ed

The deployed WordPress staging candidate passed the scripted public browsing and
cart-to-checkout flow at 1440×900 and 390×844. The reproducible harness is
[`run.cjs`](run.cjs), with machine-readable measurements and screenshots in
[`artifacts/`](artifacts/). Both viewport results are `PASS_TO_CHECKOUT`; no
order was submitted.

| Check                                                                                            | Desktop                                                                               | Mobile                                                                    |
| ------------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------- | ------------------------------------------------------------------------- |
| Homepage, pre-order, BR-004 PDP, cart, checkout                                                  | HTTP 200 each                                                                         | HTTP 200 each                                                             |
| Monument bytes                                                                                   | SHA-256 matches local candidate                                                       | SHA-256 matches local candidate                                           |
| Deployed `home-art-direction.min.css` and `content-page.min.css`                                 | Both byte-match local candidate                                                       | Both byte-match local candidate                                           |
| Hero art below fixed header                                                                      | Desktop overlay is intentional                                                        | Homepage and pre-order art begin at y=64px, matching header bottom y=64px |
| Jersey Series                                                                                    | 8 slides; next changes 1/8 to 2/8                                                     | 8 slides; next changes 1/8 to 2/8                                         |
| Pre-order edit                                                                                   | 15 cards; first The Fannie card matches linked PDP                                    | Same                                                                      |
| BR-004 M to checkout                                                                             | Variation 10507, confirmed Woo add notice and cart cookie, one cart and checkout line | Same                                                                      |
| Cart/checkout total                                                                              | $40 item + $17 standard shipping = $57                                                | Same                                                                      |
| Visible broken images, horizontal overflow, page errors, failed same-site requests, mascot nodes | None                                                                                  | None                                                                      |

The first desktop attempt reached an empty cart because the harness clicked
while the Woo variation was still `resolving`; `variation_id` alone did not
prove purchase readiness.
[`desktop-cart-recheck.json`](artifacts/desktop-cart-recheck.json) records the
transition from `resolving` to `valid` and the successful Woo confirmation. The
final harness waits for `valid`, the native add-to-cart notice, and the Woo cart
cookie before navigating.

The staging checkout currently lists no payment methods. No payment, order,
email, or production commerce completion was tested. BR-001, BR-004, and BR-007
still lack approved product fronts; BR-004's PDP says product imagery is
unavailable. A clean broken-image check does not change that product-image
limitation. Public pages were cache-busted for the final candidate because the
initial non-busted run mixed stale page HTML with current content; the served
asset hash checks verify deployed bytes, while canonical cache freshness remains
a separate operational concern.

## Canonical URL follow-up

[`canonical-check.cjs`](canonical-check.cjs) then loaded `/`, `/pre-order/`, and
`/product/br-004/` without query parameters in fresh desktop and mobile browser
contexts, waiting for styles to load. The first mobile pre-order response showed
the old y=0 artwork position while the edge reported
`x-ac: 3.sjc _atomic_bur UPDATING`. A second canonical check after the edge
update passed all six route/viewport states: both mobile hero media start at
y=64px, matching the fixed header bottom; the glass monument URL is current;
mascot nodes are absent; every route returned HTTP 200. Homepage reported
`x-ac: 1.sjc _atomic_bur HIT`, `cache-control: max-age=212, must-revalidate`,
and Last-Modified `Mon, 28 Sep 2026 20:45:27 GMT`. Pre-order and PDP reported
`x-ac: 3.sjc _atomic_bur HIT`. The settled canonical result and screenshots are
in [`artifacts/canonical-results.json`](artifacts/canonical-results.json) and
adjacent `canonical-*.png` files. This is a sampled edge result, not a claim
that every geographic cache node was inspected.
