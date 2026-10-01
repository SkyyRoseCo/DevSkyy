"""Anonymous local WordPress/WooCommerce fixture; no order or external request."""

import hashlib
import json
import re
from pathlib import Path

from playwright.sync_api import expect, sync_playwright

ROOT = Path(__file__).resolve().parents[4]
OUT = Path(__file__).resolve().parent
ORIGIN = "http://127.0.0.1:19365"
THEME = ROOT / "wordpress-theme/skyyrose-flagship-2"


def capture(page, name):
    page.screenshot(path=str(OUT / f"{name}.png"), full_page=True)
    (OUT / f"{name}.html").write_text(page.content())


def run(browser, mobile):
    name = "wp-native-mobile" if mobile else "wp-native-desktop"
    context = browser.new_context(
        viewport={"width": 390, "height": 844} if mobile else {"width": 1280, "height": 900},
        is_mobile=mobile,
        has_touch=mobile,
        reduced_motion="reduce",
        service_workers="block",
    )
    requests, blocked, errors = [], [], []

    def restrict(route):
        if route.request.url.startswith(ORIGIN + "/"):
            requests.append({"url": route.request.url, "method": route.request.method})
            route.continue_()
        else:
            blocked.append(route.request.url)
            route.abort()

    context.route("**/*", restrict)
    context.tracing.start(screenshots=True, snapshots=True, sources=True)
    page = context.new_page()
    page.set_default_timeout(10000)
    page.on("pageerror", lambda error: errors.append(str(error)))
    try:
        page.goto(ORIGIN + "/?product=synthetic-integration-br-003")
        expect(page.locator("form.variations_form")).to_be_visible()
        product_name = page.locator(".product_title").inner_text()
        expect(page.locator("[data-sr2-pdp-status]")).to_have_attribute("data-state", "incomplete")
        if page.get_by_role("button", name="Decline", exact=True).is_visible():
            page.get_by_role("button", name="Decline", exact=True).click()
        assert page.locator("[data-product-glb], [data-viewer-stage]").count() == 0
        assert page.locator("canvas").count() == 0
        assert not any(
            "product-glb" in row["url"] or "three-r170" in row["url"] for row in requests
        )
        # Exercise keyboard on actual native WooCommerce variation controls.
        page.get_by_label("Size", exact=True).focus()
        page.keyboard.press("s")
        page.keyboard.press("Tab")
        expect(page.locator("[data-sr2-pdp-status]")).to_have_attribute("data-state", "valid")
        expect(page.locator("[name=variation_id]")).to_have_value("370")
        expect(page.locator(".single_add_to_cart_button")).not_to_have_class("disabled")
        expect(page.locator(".sr2-variation-order-status")).to_have_text(
            "Pre-order option. Full payment at checkout."
        )
        page.locator(".sr2-variation-order-status").click(trial=True)
        capture(page, name + "-selected-s")
        # Reset and reselect exercises native recovery without synthetic DOM values.
        page.get_by_role("link", name="Clear options").focus()
        page.keyboard.press("Enter")
        expect(page.locator("[data-sr2-pdp-status]")).to_have_attribute("data-state", "incomplete")
        expect(page.locator("[name=variation_id]")).to_have_value(re.compile(r"^(?:0)?$"))
        page.get_by_label("Size", exact=True).focus()
        page.keyboard.press("m")
        page.keyboard.press("Tab")
        expect(page.locator("[data-sr2-pdp-status]")).to_have_attribute("data-state", "valid")
        expect(page.locator("[name=variation_id]")).to_have_value("371")
        variation_text = page.locator(".woocommerce-variation-availability").inner_text()
        assert "Pre-order" not in variation_text
        page.locator(".sr2-variation-order-status").click(trial=True)
        capture(page, name + "-selected-m")
        page.locator(".single_add_to_cart_button").focus()
        page.keyboard.press("Enter")
        expect(page.locator(".woocommerce-message")).to_contain_text("has been added to your cart")
        expect(page.locator(".single_add_to_cart_button")).to_have_text("Add to cart")
        assert page.locator(".single_add_to_cart_button").get_attribute("aria-busy") != "true"
        capture(page, name + "-cart-success")
        success_link = page.locator(".woocommerce-message a").first
        cart_url = success_link.get_attribute("href")
        assert cart_url.startswith(ORIGIN + "/")
        success_link.click()
        cart = page.locator(".woocommerce-cart-form, .wc-block-cart")
        expect(cart).to_be_visible()
        expect(cart).to_contain_text(product_name)
        capture(page, name + "-native-cart")
        assert page.locator("[data-product-glb], [data-viewer-stage]").count() == 0
        assert not any(
            "product-glb" in row["url"] or "three-r170" in row["url"] for row in requests
        )
        assert not errors, errors
        result = {
            "scope": "REPRODUCED_LOCAL_WORDPRESS_WOOCOMMERCE_ANONYMOUS_SYNTHETIC_CATALOG",
            "authentication": "NOT_APPLICABLE",
            "site": ORIGIN,
            "active_theme_source": str(THEME),
            "fixture_product_ids": {"parent": 369, "S": 370, "M": 371},
            "fixture_product_name": product_name,
            "browser_version": browser.version,
            "viewport": page.viewport_size,
            "mobile": mobile,
            "native_cart_url": cart_url,
            "observed_M_availability": variation_text,
            "assertions": [
                "No GLB root, empty stage, canvas, or GLB/Three download",
                "Keyboard native S selection resolves 370 with current preorder label",
                "Keyboard reset returns incomplete selection then M resolves 371",
                "Keyboard native POST add-to-cart succeeds and busy state recovers",
                "Local native View cart link opens real WooCommerce cart with synthetic line",
            ],
            "requests": requests,
            "external_requests_blocked_before_transmission": blocked,
            "page_errors": errors,
            "orders_or_payments": "NOT_ATTEMPTED",
            "asset_approval": "NOT_ESTABLISHED",
            "source_sha256": {
                str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest()
                for path in [
                    THEME / "functions.php",
                    THEME / "inc/product-glb.php",
                    THEME / "assets/js/theme.min.js",
                    THEME / "data/product-presentation-registry.json",
                ]
                if path.exists()
            },
        }
        (OUT / f"{name}.json").write_text(json.dumps(result, indent=2) + "\n")
        print(json.dumps({"scenario": name, "result": "PASS", "M_availability": variation_text}))
    except Exception:
        capture(page, name + "-failure")
        raise
    finally:
        context.tracing.stop(path=str(OUT / f"{name}-trace.zip"))
        context.close()


if __name__ == "__main__":
    with sync_playwright() as runtime:
        chromium = runtime.chromium.launch()
        try:
            run(chromium, False)
            run(chromium, True)
        finally:
            chromium.close()
