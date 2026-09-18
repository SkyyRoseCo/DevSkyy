# Film distribution and sales measurement

Public primary documentation checked September 12, 2026. These are documented capabilities and analytical recommendations, not an account audit or executed campaign. No accounts, audience lists, messages, campaigns or spend were accessed. Authentication: not applicable.

## Recommended execution

Make one creative production support three commercial jobs: attention, product conviction and purchase. A collection short establishes a desire or relationship; a product cut lets the actual garment be inspected; the destination makes the exact product immediately purchasable. This is a strategic recommendation, not evidence that a particular film will sell.

1. **Define the sale before the scene.** Select an available hero SKU with verified variants, fulfillment timing, returns and margin. Record the buyer question the film should answer. For Black Rose: can someone recognize the actual sherpa bomber and its silhouette, rather than merely remember an atmospheric train? Keep the source performer and authentic garment footage.
2. **Package the film into distinct assets.** Create an independently understandable collection short; two alternative openings with the same middle/end; and a clean product-detail cut. Preserve wordless film masters. Use the platform's surrounding caption, product link and CTA to state the item and purchase action. Treat each opening as a hypothesis—product-first recognition versus character-first curiosity—not cosmetic variations in color grade.
3. **Choose a sales-oriented test when sales are the outcome.** TikTok differentiates Video Views (attention/engagement) from Sales (selling through a shop, website or app). Its March 2026 Sales documentation says legacy Website Conversions/Product Sales objectives merged, with phased advertiser availability. For the WooCommerce destination, use Website rather than assuming TikTok Shop/GMV Max applies. Account availability and event selection still need verification. [1][2]
4. **Keep the click promise intact.** Send the Black Rose cut to the exact bomber page or a tightly edited shoppable Black Rose landing page with that item visible immediately. Show the same product, color and construction, then front/back, material detail, sizing, stock/pre-order status and checkout. The main film may link to a shoppable collection index. TikTok's creative guidance requires ad-to-landing-page consistency and recommends safe-zone placement of important visual elements. [3]
5. **Reintroduce the brand to reachable people.** Begin email relaunch communication with subscribed, engaged recipients; distinguish past purchasers, recent product interest and new subscribers. A previous purchase alone is not proof of email consent. Klaviyo's documented segment includes subscribed status plus recent engagement, and warns that Apple Mail Privacy Protection inflates opens. Use clicks and on-site behavior as additional evidence. Suppressed profiles are separately ineligible for marketing; preserve existing suppression/consent state. [4][5]
6. **Test one decision at a time.** Hold destination, offer, audience and rest of edit steady while comparing openings. TikTok split testing separates audiences so each sees one ad group and supports creative testing. Prefer this over calling two unevenly delivered ads a controlled experiment. Predefine a purchase-oriented primary outcome, evaluation window and stop conditions using available volume and margin. No universal budget, duration or ROAS target follows from the documentation. [6]
7. **Diagnose the whole path before replacing creative.** Watch time diagnoses attention; outbound clicks and landing sessions diagnose transfer; product views, cart and checkout diagnose shopping; valid purchases and refunds establish commercial outcomes. Strong attention with weak product visits suggests an unclear product/CTA; strong visits with weak purchase suggests product, offer, stock, shipping or checkout friction. These are hypotheses to investigate, not automatic causal conclusions.

## Measurement specification

Maintain stable campaign/creative identifiers in UTMs and records: collection, SKU, premise, opening, edit version, destination. Track `view_item`, `add_to_cart`, `begin_checkout`, `purchase` and `refund` with consistent item identifiers. Reconcile purchase records against WooCommerce orders; count a purchase when payment/order completion is confirmed, not because someone clicks the purchase button. GA4 ecommerce events require implementation and are not automatically collected. DebugView can verify receipt before standard reports populate. [7]

Use each order's unique non-personal `transaction_id`, value and currency. Google documents web-stream deduplication for repeated purchase IDs and warns that empty/reused IDs can undercount. Verify duplicate refreshes and refunds explicitly. [8]

Keep four views separate: platform delivery, attributed conversions, store orders/net sales and contribution after variable costs. GA4 attribution allocates credit across touchpoints; its documentation says conversions may be reattributed for up to seven days. Consequently, daily figures are provisional. Do not sum different platforms' claimed sales and call that unique revenue. Attribution credit is not an experiment demonstrating incremental sales. [9]

Shopify documentation is useful corroboration, not a recommendation to migrate the WooCommerce store: its marketing reports explicitly include only trackable marketing sales, and its Any Click model can award more total credit than received orders. This illustrates why attribution-model definitions must accompany reported ROAS. [10]

## Important boundaries and unresolved evidence

Meta's current objective-help page redirected to login/temporary-block content, so its current interface and optimization claims were not independently verified here. Do not cite the login page as evidence of a working Meta sales setup. TikTok documentation supports the objective distinction directly. No evidence here ranks Meta versus TikTok for SkyyRose: that requires actual customer/channel and commercial data.

Seven days can sequence releases, but cannot guarantee statistical certainty or profitable customer acquisition. Extend evaluation when purchase volume or attribution lag is insufficient. Scale only after source/identity quality, functional purchase flow and an economically acceptable result agree; an attractive watch-time result alone cannot certify readiness.

## Sources

1. TikTok, [How to choose the right objective](https://ads.tiktok.com/resources/help/article/choose-right-objective?lang=en), April 2025.
2. TikTok, [About the Sales advertising objective](https://ads.tiktok.com/resources/help/article/sales-advertising-objective-tiktok), March 2026.
3. TikTok, [Creative Guidance—Safe Zone and Ad formats and functionality](https://ads.tiktok.com/business/creativecenter/quicktok/online/tiktok_creative_accelerator/pc/en), date not displayed.
4. Klaviyo, [How to create an engaged segment of email subscribers](https://help.klaviyo.com/hc/en-us/articles/115000200072), September 4, 2025.
5. Klaviyo, [Understanding suppressed email profiles](https://help.klaviyo.com/hc/en-us/articles/115005246108), March 30, 2026.
6. TikTok, [About Split Testing](https://ads.tiktok.com/resources/help/article/split-testing?lang=en), January 2026.
7. Google, [Set up ecommerce events](https://support.google.com/analytics/answer/12200568?hl=en), date not displayed.
8. Google, [Minimize duplicate key events with transaction IDs](https://support.google.com/analytics/answer/12313109), date not displayed.
9. Google, [Get started with attribution](https://support.google.com/analytics/answer/10596866), date not displayed.
10. Shopify, [Marketing reports](https://help.shopify.com/en/manual/reports-and-analytics/shopify-reports/report-types/marketing-reports), date not displayed; cross-platform illustration only.
