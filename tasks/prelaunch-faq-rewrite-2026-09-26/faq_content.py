"""FAQ rewrite for page 9711 (/faq/) — single source for the markup, review page and evidence.

Every answer carries the sources that back it. `build_faq.py` renders the three
deliverables from this module and fails closed when a quote no longer matches its page
or registry field.
"""

SHIP = ("policy_page", "9712 /shipping-returns/ (Shipping Policy)")
REFUND = ("policy_page", "10146 /refund-policy/ (Refund & Return Policy)")
RETEX = ("policy_page", "10406 /returns-exchanges/ (Returns + Exchanges)")
SIZE = ("policy_page", "10409 /size-guide/ (Size Guide)")
TOS = ("policy_page", "9718 /terms-of-service/ (Terms of Service)")


def src(page, quote):
    kind, ref = page
    return {"kind": kind, "ref": ref, "quote": quote}


def reg(ref, quote):
    return {"kind": "registry", "ref": ref, "quote": quote}


INTRO = (
    "Straight answers on orders, sizing, shipping, and returns, with links to the policies "
    "behind them. If your question isn’t here, reach us through the "
    '<a href="/contact/">Contact page</a>.'
)

# (category, [(question, answer_html, [sources])])
SECTIONS = [
    (
        "Orders and pre-orders",
        [
            (
                "How do pre-orders work?",
                "A pre-order is charged in full at checkout, not when it ships. Pre-order "
                "pieces ship separately from any in-stock pieces in the same order, so you may "
                "get more than one shipment and tracking number. Full terms are in our "
                '<a href="/shipping-returns/">Shipping Policy</a>.',
                [
                    src(
                        SHIP,
                        "Your card is charged in full at the time of pre-order, not at the time of shipment.",
                    ),
                    src(
                        SHIP,
                        "Pre-order items ship separately from any in-stock items included in the same order. You may receive multiple shipments and tracking numbers for a single order containing both in-stock and pre-order items.",
                    ),
                ],
            ),
            (
                "When will my pre-order ship?",
                "Each pre-order piece has its own estimated ship date rather than a fixed window "
                "after a collection launch, and that date is an estimate that can change. For the "
                'current estimate on a piece, ask us through the <a href="/contact/">Contact '
                "page</a> before you order. We email you a tracking number when it ships.",
                [
                    src(
                        SHIP,
                        "The estimated ship date for each pre-order item is displayed on the product page at the time of purchase. These dates are estimates and may be subject to change due to production, supply chain, or logistics factors.",
                    ),
                    src(
                        SHIP,
                        "You will receive an email notification when your pre-order item has been dispatched, including a tracking number.",
                    ),
                ],
            ),
            (
                "Can I cancel a pre-order?",
                "You can cancel a pre-order for a full refund up to 48 hours before its "
                "estimated ship date by contacting us with your order number. After that, the "
                "order can’t be cancelled, and our standard "
                '<a href="/refund-policy/">return policy</a> applies once it’s delivered.',
                [
                    src(
                        REFUND,
                        "You may cancel a pre-order for a full refund up to 48 hours before the estimated ship date shown in your order confirmation.",
                    ),
                    src(
                        REFUND,
                        "Once the 48-hour pre-cancellation window has passed, your order enters production or fulfillment and can no longer be cancelled before shipment. After your pre-order is delivered, the standard return policy set out in this document applies in full.",
                    ),
                ],
            ),
            (
                "How long does it take to process my order?",
                "Orders are processed within 1–3 business days after payment is confirmed. During "
                "new collection drops and major holidays, processing can take up to 5 business days. "
                "Carrier transit time comes after processing; see our "
                '<a href="/shipping-returns/">Shipping Policy</a>.',
                [
                    src(
                        SHIP,
                        "All orders are processed within 1–3 business days (Monday through Friday, excluding US federal holidays) from the date payment is confirmed. During new collection drops or major holiday periods (e.g., Black Friday/Cyber Monday, Christmas), processing may extend to up to 5 business days due to elevated order volume.",
                    ),
                    src(
                        SHIP,
                        "Processing time is separate from and in addition to the carrier transit times listed in the sections below.",
                    ),
                ],
            ),
            (
                "What payment methods do you accept?",
                "We accept payment through Stripe and PayPal, and all prices are charged in US "
                'dollars. See our <a href="/terms-of-service/">Terms of Service</a> for the full '
                "order terms.",
                [
                    src(
                        TOS,
                        "All prices on the Site are displayed and charged in US Dollars (USD). We accept payment via Stripe and PayPal.",
                    ),
                ],
            ),
        ],
    ),
    (
        "Sizing and fit",
        [
            (
                "What sizes do you carry?",
                "Most adult pieces come in S–3XL. A few run differently: The Bridge Series "
                "'Stay Golden' Shirt comes in XS–2XL, The Bridge Series 'The Bay Bridge' Shirt "
                "comes in S–2XL, and The Fannie and The Signature Beanie are One Size. The sizes "
                "for each piece are listed on its product page, and our "
                '<a href="/size-guide/">Size Guide</a> explains how to choose.',
                [
                    reg(
                        "aggregate: products[*].catalog.sizes where catalog.published == '1'",
                        "SIZES_AGGREGATE",
                    ),
                    reg("products[sg-002].catalog.sizes", "XS|S|M|L|XL|2XL"),
                    reg("products[sg-005].catalog.sizes", "S|M|L|XL|2XL"),
                    reg("products[lh-005].catalog.sizes", "One Size"),
                    reg("products[sg-007].catalog.sizes", "One Size"),
                ],
            ),
            (
                "What sizes does the Kids Capsule come in?",
                "The Kids Colorblock Hoodie Set, in Red/Black and Purple/Black, comes in 2T, 3T, "
                '4T, 5, 6, and 7. Our <a href="/size-guide/">Size Guide</a> explains how to '
                "compare against a piece your child already wears.",
                [
                    reg("products[kids-001].catalog.sizes", "2T|3T|4T|5|6|7"),
                    reg("products[kids-002].catalog.sizes", "2T|3T|4T|5|6|7"),
                ],
            ),
            (
                "How do I choose my size?",
                'Our <a href="/size-guide/">Size Guide</a> shows you how to lay a similar piece you '
                "already own flat and compare it. If you’re between sizes or unsure, send us your "
                'question through the <a href="/contact/">Contact page</a> before you order.',
                [
                    src(SIZE, "Lay a similar garment flat without stretching it."),
                    src(SIZE, "Client Services can help compare measurements before purchase."),
                ],
            ),
        ],
    ),
    (
        "Shipping",
        [
            (
                "Where do you ship?",
                "We ship across the United States, including Alaska and Hawaii, and to 40+ "
                "countries. International shipping is calculated at checkout from your destination "
                "and the size and weight of your order, and you’ll see the exact cost before you "
                'pay. Details are in our <a href="/shipping-returns/">Shipping Policy</a>.',
                [
                    src(
                        SHIP,
                        "orders delivered within the contiguous United States, Alaska, and Hawaii",
                    ),
                    src(
                        SHIP,
                        "SkyyRose ships to 40+ countries worldwide. Shipping rates for international orders are calculated dynamically at checkout based on the destination country and the total weight and dimensions of your order. You will see the exact shipping cost before completing your purchase.",
                    ),
                ],
            ),
            (
                "How much does US shipping cost?",
                "Standard shipping (5–7 business days) is $17 and Express shipping (2–3 business "
                "days) is $22. Standard shipping is free on orders of $200.00 or more before taxes. "
                'Delivery estimates start once your order ships; see our <a href="/shipping-returns/">'
                "Shipping Policy</a> for details.",
                [
                    src(SHIP, "Standard Shipping 5–7 business days $17"),
                    src(SHIP, "Express Shipping 2–3 business days $22"),
                    src(
                        SHIP,
                        "Free Standard Shipping 5–7 business days Free on orders $200.00 or more (before taxes)",
                    ),
                    src(
                        SHIP,
                        "Delivery time estimates begin on the day of shipment (after processing) and are provided by the carrier.",
                    ),
                ],
            ),
            (
                "Will I pay customs or import duties?",
                "Orders shipped outside the US may be charged import duties, customs fees, or taxes "
                "by the destination country. Those charges are the recipient’s responsibility and "
                "are not included in the shipping cost shown at checkout, as set out in our "
                '<a href="/shipping-returns/">Shipping Policy</a>.',
                [
                    src(
                        SHIP,
                        "When an order is shipped to a destination outside the United States, it may be subject to import duties, customs fees, value-added tax (VAT), goods and services tax (GST), or other charges levied by the destination country. These charges are the sole responsibility of the recipient.",
                    ),
                    src(
                        SHIP,
                        "These amounts are not included in the shipping cost displayed at checkout or charged at the time of purchase.",
                    ),
                ],
            ),
            (
                "How do I track my order?",
                "When your order ships, you’ll get a confirmation email with your tracking number "
                "and a link to the carrier’s tracking page. You can also sign in to your account and "
                "check the order status under My Orders. Our "
                '<a href="/shipping-returns/">Shipping Policy</a> covers tracking in full.',
                [
                    src(
                        SHIP,
                        "Once your order has been shipped, you will receive a shipping confirmation email containing your tracking number and a direct link to the carrier’s tracking portal.",
                    ),
                    src(
                        SHIP,
                        "Log in to your account on skyyrose.co and view the order status under My Orders.",
                    ),
                ],
            ),
            (
                "What if my package is lost, or marked delivered but not received?",
                "Check your shipping address and every spot a carrier might leave it. If it still "
                'hasn’t turned up, <a href="/contact/">contact us</a> with your order number and '
                "tracking number. For a "
                "package marked Delivered, reach out within 7 days of that date so we can start a "
                "carrier claim.",
                [
                    src(
                        SHIP,
                        "Verify the shipping address on your order confirmation matches your intended delivery address.",
                    ),
                    src(
                        SHIP,
                        "Contact us at info@shopskyyrose.com with your order number and tracking number. We will open an investigation with the carrier on your behalf.",
                    ),
                    src(
                        SHIP,
                        "contact us at info@shopskyyrose.com within 7 days of the marked delivery date so we can initiate a carrier claim.",
                    ),
                ],
            ),
        ],
    ),
    (
        "Returns and exchanges",
        [
            (
                "What is your return policy?",
                "You can return eligible pieces within 30 days of confirmed delivery. They must be "
                "unworn, unwashed, and unaltered, with all original tags attached, in their original "
                'packaging. Read our full <a href="/refund-policy/">return policy</a> before you '
                "send anything back.",
                [
                    src(
                        REFUND,
                        "We accept returns on eligible items within 30 days of the confirmed delivery date shown in your shipping confirmation.",
                    ),
                    src(
                        RETEX,
                        "Eligible returns must be requested within 30 days of confirmed delivery and meet the policy’s unworn, unwashed, unaltered, tagged, and original-packaging requirements.",
                    ),
                ],
            ),
            (
                "How do I start a return?",
                'Contact us through the <a href="/contact/">Contact page</a> before you ship '
                "anything. Include your order number, the email used at checkout, the piece and "
                "size, and a brief reason, but never payment-card details. For US orders, we send "
                "you a prepaid USPS return label.",
                [
                    src(RETEX, "Start with Client Services before shipping anything."),
                    src(
                        RETEX,
                        "Send the order number, the email used at checkout, the piece and size, and a brief reason for the request. Do not email payment-card details.",
                    ),
                    src(REFUND, "with a prepaid USPS return shipping label attached"),
                ],
            ),
            (
                "Can I exchange for a different size or color?",
                "US exchanges for a different size or color of the same style are free: we confirm "
                "the replacement is available and send a prepaid USPS label, and you ship the "
                "original back within 14 days of receiving it. International customers pay return "
                "shipping to our US facility, and the replacement ships at no additional charge "
                'after inspection. The full steps are on <a href="/returns-exchanges/">Returns and '
                "Exchanges</a>.",
                [
                    src(
                        RETEX,
                        "US exchanges for a different size or color of the same style are free. Client Services confirms replacement availability, sends a prepaid USPS return label, and the original item must be shipped within 14 days of receiving that label.",
                    ),
                    src(
                        RETEX,
                        "International customers pay return shipping to the US facility; after inspection, an eligible replacement ships at no additional charge.",
                    ),
                ],
            ),
            (
                "When will I get my refund?",
                "Approved refunds go back to your original payment method within 5–7 business days "
                "of when we receive and inspect your return. Your bank may take longer to post it, "
                "so allow up to 10 business days in total. Original shipping costs are not refunded "
                "unless the item arrived damaged, defective, or incorrect; see our "
                '<a href="/refund-policy/">return policy</a>.',
                [
                    src(
                        REFUND,
                        "Approved refunds are issued to the original payment method used at checkout within 5–7 business days of our receipt and inspection of the returned item.",
                    ),
                    src(REFUND, "please allow up to 10 business days total before contacting us."),
                    src(
                        REFUND,
                        "Original outbound shipping costs are non-refundable, except in cases where the item arrived damaged, defective, or materially different from what was ordered",
                    ),
                ],
            ),
            (
                "What can’t be returned?",
                "Final Sale items, pieces that have been worn, washed, or altered, items without "
                "their original tags, gift cards, and customized or personalized pieces can’t be "
                "returned or exchanged, unless they arrive damaged, defective, or incorrect. The "
                'full list is in our <a href="/refund-policy/">return policy</a>.',
                [
                    src(
                        REFUND,
                        "The following items are not eligible for return or exchange under any circumstances, unless they arrive damaged, defective, or incorrect",
                    ),
                    src(REFUND, "Final Sale items — any item marked"),
                    src(REFUND, "Gift cards — digital and physical gift cards are non-refundable"),
                    src(REFUND, "Customized or personalized pieces"),
                ],
            ),
            (
                "My order arrived damaged, defective, or wrong. What do I do?",
                '<a href="/contact/">Contact us</a> within 7 days of confirmed delivery with your '
                "order number and clear "
                "photos of the issue. We’ll make it right at no cost to you, with a replacement or a "
                "full refund that includes original shipping.",
                [
                    src(REFUND, "we will make it right at no cost to you."),
                    src(
                        REFUND,
                        "Contact us at info@shopskyyrose.com within 7 days of the confirmed delivery date.",
                    ),
                    src(
                        REFUND,
                        "Include your order number and clear photographs showing the damage, defect, or incorrect item",
                    ),
                    src(REFUND, "Full refund — including original outbound shipping costs"),
                ],
            ),
            (
                "How do international returns work?",
                "International returns follow the same 30-day eligibility rules. You arrange and pay "
                "for return shipping to our US facility, and we recommend a tracked, insured service. "
                "Refunds exclude original shipping, and duties or taxes paid on delivery are "
                'generally not refundable by SkyyRose; see our <a href="/refund-policy/">return '
                "policy</a>.",
                [
                    src(
                        REFUND,
                        "International customers who wish to return an item must follow the same eligibility and process requirements described in Sections 2 and 3",
                    ),
                    src(
                        REFUND,
                        "International customers are responsible for arranging and paying for return shipping to our US facility. We recommend using a tracked, insured service.",
                    ),
                    src(
                        REFUND,
                        "(excluding original shipping costs and any duties or taxes collected at destination)",
                    ),
                    src(
                        REFUND,
                        "Original outbound duties, import taxes, and customs fees paid at time of delivery are generally not refundable by SkyyRose.",
                    ),
                ],
            ),
        ],
    ),
    (
        "The collections",
        [
            (
                "What collections does SkyyRose make?",
                "Four: Signature, Black Rose, Love Hurts, and the Kids Capsule. Each is its own "
                "chapter of one Oakland-rooted house.",
                [
                    reg(
                        "aggregate: products[*].collection where catalog.published == '1'",
                        "COLLECTIONS_AGGREGATE",
                    ),
                    src(SHIP, "SkyyRose LLC · skyyrose.co · Oakland, California"),
                ],
            ),
        ],
    ),
    (
        "Contact",
        [
            (
                "How do I reach SkyyRose?",
                'Send us a message through the <a href="/contact/">Contact page</a>. If it’s about '
                "an order, include your order number, and never send payment-card details by email.",
                [
                    src(
                        REFUND,
                        "Include your order number in all correspondence to help us assist you quickly.",
                    ),
                    src(RETEX, "Do not email payment-card details."),
                ],
            ),
        ],
    ),
]

FOUNDER_DECISIONS = [
    {
        "id": "FD-1",
        "topic": "Responsibly sourced fabrics / fair-trade certified facilities",
        "detail": "The current FAQ says each collection “uses responsibly sourced fabrics and partners with fair-trade certified facilities.” It is left out of the new FAQ and is not described as false. Supply the wording you want published, and any certification or supplier evidence you want referenced, if you want a sourcing answer.",
    },
    {
        "id": "FD-2",
        "topic": "Public customer-service email",
        "detail": "The published policies (9712, 10146, 9718) use support@skyyrose.co. The rendered staging /contact/ page shows corey@skyyrose.co, because the V2 template contact.php prints get_option('admin_email'). Page 9457's stored post_content also lists corey@skyyrose.co. The new FAQ hard-codes no address and links to /contact/. Decide which address customers should see.",
    },
    {
        "id": "FD-3",
        "topic": "“Gender-neutral” claim",
        "detail": "The current FAQ says all collections are gender-neutral. No registry field or policy page states this, so it is left out. Confirm the wording if you want it published.",
    },
    {
        "id": "FD-4",
        "topic": "Pre-order ship-date display",
        "detail": "The Shipping Policy (9712 §6) and the Terms of Service (9718 §7) say each pre-order's estimated ship date is displayed on the product page. The rendered staging PDP for br-006 instead says “This label does not reserve stock or defer payment. Contact Client Services for shipping estimates before ordering” (from v2-preorder.php), and it shows no date. The FAQ states only what both sides agree on (each item has its own estimate, which can change) and routes people to Contact. Decide whether PDPs will show a date or the policy wording changes.",
    },
    {
        "id": "FD-5",
        "topic": "Size charts and care instructions",
        "detail": "The FAQ promises no product measurements or care answer. Current registry gaps are recorded in faq-evidence.json. Preserve founder specifications; request only missing details needed for a proposed answer.",
    },
]

REMOVED_CLAIMS = [
    {
        "old": "Pre-orders ship within 4–6 weeks of the collection launch date.",
        "reason": "This contradicts the Shipping Policy (9712 §6): each pre-order item has its own estimated ship date, payment is taken in full, and pre-order items ship separately from in-stock items. It was replaced with the policy's own terms.",
    },
    {
        "old": "All SKYYROSE collections are gender-neutral and available in sizes XS through 3XL.",
        "reason": "The size range is false per the registry. Only sg-002 offers XS, and sg-002 stops at 2XL. Most adult pieces are S–3XL, sg-005 is S–2XL, lh-005 and sg-007 are One Size, and Kids is 2T–7. “Gender-neutral” has no source (FD-3).",
    },
    {
        "old": "Refer to our size guide on each product page for detailed measurements.",
        "reason": "The registry holds no garment size charts, so no detailed measurements are published (FD-5).",
    },
    {
        "old": "Yes. We ship worldwide.",
        "reason": "This contradicts the Shipping Policy, which says “SkyyRose ships to 40+ countries” and reserves the right to restrict destinations.",
    },
    {
        "old": "We accept returns within 30 days of delivery for unworn items in original packaging. See our Shipping & Returns page for full details.",
        "reason": "This was incomplete: it left out the unwashed, unaltered and tags-attached conditions, and it pointed to the Shipping page instead of the Refund & Return Policy. It was rewritten from 10146 §2 and 10406.",
    },
    {
        "old": "Each collection uses responsibly sourced fabrics and partners with fair-trade certified facilities. / We prioritize ethical manufacturing and sustainable materials wherever possible.",
        "reason": "This is an open founder decision (FD-1). It is left out and is not described as false.",
    },
    {
        "old": "Email us at support@skyyrose.co or use our Contact page.",
        "reason": "The address is not hard-coded, because three different addresses are in use (FD-2). The FAQ links to /contact/.",
    },
    {
        "old": "We respond within 24 hours.",
        "reason": "Founder directive: no response-time promise anywhere in the FAQ. The policy-page reply windows are also left out: the 24-hour label reply, the 2-business-day damage response and the 2-business-day refund follow-up.",
    },
]

POLICY_CONTRADICTIONS = [
    "Reply-time promises disagree. 9712 §9 says “We aim to respond to all inquiries within 1–2 business days.” 10146 §11 says “within 1 business day and within 24 hours for return label requests.” Page 9457's stored post_content says “Responses within 24 hours.” That last one is not rendered on staging, where the V2 contact.php template serves /contact/.",
    "The pre-order cancellation anchor differs. 10146 §8 says the cancellation window runs to the “estimated ship date shown in your order confirmation.” 9718 §7 says it runs to the “estimated ship date shown on the product page at the time of purchase.”",
    "Pre-order ship date. 9712 §6 and 9718 §7 say the estimated ship date is displayed on the product page. The V2 theme copy (v2-preorder.php, rendered on the staging br-006 PDP and /pre-order/) says the label does not establish a shipping date and tells customers to contact Client Services for estimates.",
    "Size Guide 10409 refers to “the measurements published for the piece.” Compare current registry sizing references and displayed measurements before promising a chart.",
    "Customer email: policies use support@skyyrose.co. The rendered /contact/ uses admin_email (corey@skyyrose.co), and 9457 post_content uses corey@skyyrose.co.",
]

OUT_OF_SCOPE_FINDINGS = [
    "Page 9335 (/pre-order/) stored post_content, read through REST, holds a legacy gateway. It has phantom SKUs that are not in the registry (SR-BR-THORN-H, SR-LH-HB-H, SR-SG-FND-B …), “up to 20% off retail”, XXL and 28–36 waist sizes, and “380gsm”/“450gsm” claims. On staging this content is NOT rendered, because /pre-order/ serves the V2 template instead. It would surface on any theme that renders post_content.",
    "Staging WooCommerce names br-006 “BLACK Rose Sherpa Jacket”, while the registry catalog.name is “The Bomber Sherpa”. This is catalog drift, reported only.",
    "Staging /faq/ currently emits no FAQPage JSON-LD. The old markup uses h3 questions, which neither extractor branch matches, and staging may also be suppressed by skyyrose2_seo_is_nonproduction_request().",
]
