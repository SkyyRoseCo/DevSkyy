"""Real V2 init/renderer, local synthetic native resolver and triangle GLB only.

No registry acceptance, product truth, external HTTP, or WordPress state is changed.
PageTransitionEvent coverage is a lifecycle regression, not real browser bfcache proof.
"""

import hashlib
import html
import json
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit

import pytest
from playwright.sync_api import expect, sync_playwright

from test_viewer_browser import glb

ROOT = Path(__file__).resolve().parents[2]
THEME = ROOT / "wordpress-theme/skyyrose-flagship-2"
JS = THEME / "assets/js"
EVIDENCE = ROOT / "tasks/integration-release-20261001/evidence/browser"
REGISTRY = "a" * 64
pytestmark = pytest.mark.integration


def fixture_html(port):
    product = {
        "sku": "fixture-native",
        "native_sku": "fixture-native-m",
        "product_id": 501,
        "variation_id": 512,
        "attributes": {"attribute_pa_size": "m"},
        "url": f"http://127.0.0.1:{port}/native-product",
        "name": "Synthetic triangle - no product fidelity claim",
    }
    payload = glb()
    binding = {
        **product,
        "asset_url": "/triangle.glb",
        "sha256": hashlib.sha256(payload).hexdigest(),
        "byte_length": len(payload),
        "registry_sha256": REGISTRY,
        "qc_binding": "PASS",
        "product_fidelity": "PASS",
        "creative_approval": "FOUNDER_APPROVED",
        "license": "PASS",
        "runtime_budget": "PASS",
        "approval_id": "SYNTHETIC-TEST-ONLY",
        "publication_authorized": True,
    }
    config = {
        "sku": product["sku"],
        "productId": product["product_id"],
        "registrySha": REGISTRY,
        "manifest": {
            "schema": "skyyrose.accepted-glb-runtime.v1",
            "registry_sha256": REGISTRY,
            "publication_authorized": True,
            "entries": [binding],
        },
        "endpoint": "/native-resolve",
        "vendorBase": f"http://127.0.0.1:{port}/vendor/",
    }
    return (
        f"""<!doctype html><html lang="en"><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Real V2 init - synthetic local acceptance only</title>
<style>body{{font:18px system-ui;margin:16px}}button,a,select{{padding:12px;min-height:24px}}
[hidden]{{display:none!important}}[data-viewer-stage]{{height:360px;width:100%;touch-action:none}}
[data-viewer-stage]>div{{height:100%;width:100%}}canvas{{display:block;width:100%;height:100%}}
:focus-visible{{outline:3px solid #124faa;outline-offset:2px}}</style>
<main class="summary"><h1>Synthetic local V2 init fixture</h1>
<p>Real theme modules; synthetic native identity and triangle. Authentication not applicable.</p>
<form class="variations_form"><label for="size">Size</label>
<select id="size" name="attribute_pa_size"><option value="">Choose size</option>
<option value="s">Small</option><option value="m">Medium</option></select>
<input type="hidden" name="variation_id" value="0">
<button type="button" id="native-cart">Add to cart fixture control</button></form>
<section id="viewer" data-product-glb data-config="{html.escape(json.dumps(config), quote=True)}" aria-label="Product view">
<a href="/native-product">Product details</a>
<button type="button" data-viewer-open="fixture-native" hidden>Explore in 3D</button>
<p data-viewer-status role="status" aria-live="polite">Choose a product option.</p>
<div data-viewer-stage tabindex="0" role="group" aria-label="Interactive product view. Use arrow keys to rotate." hidden></div>
<button type="button" data-viewer-retry hidden>Retry</button>
<button type="button" data-viewer-reset disabled>Reset view</button>
<button type="button" data-viewer-back>Back to product</button></section></main>
<script>
window.fixtureMetrics={{posts:[],cart:0}};
const realFetch=window.fetch;
window.fetch=(url,options)=>{{
 if(String(url).includes('native-resolve'))window.fixtureMetrics.posts.push(JSON.parse(options.body));
 return realFetch(url,options);
}};
document.querySelector('#size').addEventListener('change',event=>{{
 document.querySelector('[name="variation_id"]').value=({{s:511,m:512}})[event.target.value]||0;
}});
document.querySelector('#native-cart').addEventListener('click',()=>window.fixtureMetrics.cart++);
</script><script type="module">
await import('/theme/product-glb-init.mjs');window.fixtureReady=true;
</script></html>""".encode(),
        product,
    )


@pytest.fixture
def native_server():
    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *_):
            pass

        def send_bytes(self, data, mime):
            self.send_response(200)
            self.send_header("Content-Type", mime)
            self.send_header("Content-Length", str(len(data)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(data)

        def do_GET(self):
            path = urlsplit(self.path).path
            self.server.requests.append(path)
            if path == "/":
                data, _ = fixture_html(self.server.server_port)
                self.send_bytes(data, "text/html")
            elif path.startswith("/theme/") and path[7:] in {
                "product-glb-init.mjs",
                "product-glb-viewer.mjs",
                "product-glb-three.mjs",
            }:
                self.send_bytes((JS / path[7:]).read_bytes(), "text/javascript")
            elif path.startswith("/vendor/") and path[8:] in {
                "three.module.min.js",
                "GLTFLoader.js",
                "BufferGeometryUtils.js",
            }:
                self.send_bytes((JS / "lib/three-r170" / path[8:]).read_bytes(), "text/javascript")
            elif path == "/triangle.glb":
                if self.server.asset_failure:
                    self.send_error(503)
                else:
                    self.send_bytes(glb(), "model/gltf-binary")
            elif path == "/native-product":
                self.send_bytes(b"Native synthetic product details remain available.", "text/plain")
            else:
                self.send_error(404)

        def do_POST(self):
            if urlsplit(self.path).path != "/native-resolve":
                self.send_error(404)
                return
            selection = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
            self.server.posts.append(selection)
            _, product = fixture_html(self.server.server_port)
            self.send_bytes(
                json.dumps(
                    {
                        **product,
                        "variation_id": selection["variation_id"],
                        "native_sku": (
                            "fixture-native-m"
                            if selection["variation_id"] == 512
                            else "fixture-native-s"
                        ),
                        "attributes": selection["attributes"],
                        "available": self.server.available,
                        "registry_sha256": REGISTRY,
                    }
                ).encode(),
                "application/json",
            )

    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    server.requests, server.posts = [], []
    server.available, server.asset_failure = True, False
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    yield server
    server.shutdown()
    thread.join()


@pytest.fixture(scope="module")
def chromium():
    with sync_playwright() as runtime:
        browser = runtime.chromium.launch(
            args=["--use-gl=angle", "--use-angle=swiftshader", "--enable-unsafe-swiftshader"]
        )
        yield browser
        browser.close()


def start(chromium, native_server, **options):
    origin = f"http://127.0.0.1:{native_server.server_port}"
    context = chromium.new_context(service_workers="block", **options)
    denied = []

    def restrict(route):
        if route.request.url.startswith(origin + "/"):
            route.continue_()
        else:
            denied.append(route.request.url)
            route.abort()

    context.route("**/*", restrict)
    context.tracing.start(screenshots=True, snapshots=True, sources=True)
    page = context.new_page()
    page.set_default_timeout(5000)
    page.goto(origin + "/")
    page.wait_for_function("window.fixtureReady===true")
    return context, page, denied


def state(page, expected):
    expect(page.locator("#viewer")).to_have_attribute("data-viewer-state", expected)


def choose_medium(page):
    page.get_by_label("Size", exact=True).select_option("m")
    expect(page.get_by_role("button", name="Explore in 3D")).to_be_visible()


def artifact(context, page, name, server, denied):
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    page.screenshot(path=str(EVIDENCE / f"{name}.png"), full_page=True)
    (EVIDENCE / f"{name}.html").write_text(page.content())
    receipt = {
        "scope": "REPRODUCED_LOCAL_SYNTHETIC_REAL_THEME_MODULES",
        "authentication": "NOT_APPLICABLE",
        "approval_id": "SYNTHETIC-TEST-ONLY",
        "actual_wordpress": False,
        "actual_browser_bfcache": False,
        "viewport": page.viewport_size,
        "browser_version": context.browser.version,
        "endpoint_posts": server.posts,
        "requests": server.requests,
        "blocked_external_requests": denied,
        "source_sha256": {
            str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest()
            for path in [JS / f"product-glb-{suffix}.mjs" for suffix in ["init", "viewer", "three"]]
        },
        "head": "Working tree sources; hashes identify tested bytes, not commit cleanliness",
    }
    (EVIDENCE / f"{name}.json").write_text(json.dumps(receipt, indent=2) + "\n")
    context.tracing.stop(path=str(EVIDENCE / f"{name}-trace.zip"))


@pytest.mark.parametrize("mobile", [False, True], ids=["desktop", "mobile"])
def test_native_selection_mount_keyboard_and_fresh_reopen(chromium, native_server, mobile):
    options = (
        {"viewport": {"width": 390, "height": 844}, "is_mobile": True, "has_touch": True}
        if mobile
        else {}
    )
    context, page, denied = start(chromium, native_server, **options)
    try:
        assert native_server.posts == []
        assert not any(path.startswith("/vendor/") for path in native_server.requests)
        page.get_by_label("Size", exact=True).select_option("s")
        expect(page.locator("[data-viewer-status]")).to_contain_text(
            "unavailable for this selection"
        )
        expect(page.locator("[data-viewer-open]")).to_be_hidden()
        expect(page.locator("[data-viewer-stage]")).to_be_hidden()
        assert "/triangle.glb" not in native_server.requests
        choose_medium(page)
        assert len(native_server.posts) == 2
        page.get_by_role("button", name="Explore in 3D").focus()
        page.keyboard.press("Enter")
        state(page, "ready")
        assert len(native_server.posts) == 3
        assert native_server.posts[-1] == {
            "sku": "fixture-native",
            "variation_id": 512,
            "attributes": {"attribute_pa_size": "m"},
        }
        assert page.locator("canvas").count() == 1
        assert page.locator("[data-viewer-stage]").evaluate("node=>node===document.activeElement")
        page.keyboard.press("ArrowRight")
        assert float(page.locator("[data-camera-yaw]").get_attribute("data-camera-yaw")) > 0
        page.keyboard.press("Home")
        assert page.locator("[data-camera-yaw]").get_attribute("data-camera-yaw") == "0"
        artifact(
            context,
            page,
            "theme-ready-mobile" if mobile else "theme-ready-desktop",
            native_server,
            denied,
        )
        page.keyboard.press("Escape")
        state(page, "idle")
        assert page.locator("canvas").count() == 0
        assert page.locator("[data-viewer-open]").evaluate("node=>node===document.activeElement")
        page.keyboard.press("Enter")
        state(page, "ready")
        assert len(native_server.posts) == 4
        assert page.get_by_role("link", name="Product details").is_visible()
        page.get_by_role("button", name="Add to cart fixture control").click()
        assert page.evaluate("window.fixtureMetrics.cart") == 1
        assert not denied
    finally:
        context.close()


def test_real_context_loss_retry_fresh_endpoint_and_native_unavailable(chromium, native_server):
    context, page, denied = start(chromium, native_server)
    try:
        choose_medium(page)
        page.get_by_role("button", name="Explore in 3D").click()
        state(page, "ready")
        page.locator("canvas").evaluate(
            "canvas=>canvas.getContext('webgl2').getExtension('WEBGL_lose_context').loseContext()"
        )
        state(page, "error")
        assert page.locator("canvas").count() == 0
        page.get_by_role("button", name="Retry", exact=True).click()
        state(page, "ready")
        assert len(native_server.posts) == 3
        page.get_by_role("button", name="Back to product").click()
        native_server.available = False
        page.get_by_role("button", name="Explore in 3D").click()
        state(page, "error")
        assert len(native_server.posts) == 4
        assert native_server.requests.count("/triangle.glb") == 2
        page.get_by_role("button", name="Retry", exact=True).click()
        state(page, "error")
        assert len(native_server.posts) == 5
        assert native_server.requests.count("/triangle.glb") == 2
        artifact(context, page, "theme-context-loss-native-unavailable", native_server, denied)
        page.get_by_role("link", name="Product details").click()
        expect(page.locator("body")).to_have_text(
            "Native synthetic product details remain available."
        )
        assert not denied
    finally:
        context.close()


def test_asset_failure_retry_and_native_link(chromium, native_server):
    context, page, denied = start(chromium, native_server)
    try:
        choose_medium(page)
        native_server.asset_failure = True
        page.get_by_role("button", name="Explore in 3D").click()
        state(page, "error")
        assert page.locator("canvas").count() == 0
        assert not any(path.startswith("/vendor/") for path in native_server.requests)
        native_server.asset_failure = False
        page.get_by_role("button", name="Retry", exact=True).click()
        state(page, "ready")
        assert len(native_server.posts) == 3
        assert page.locator("canvas").count() == 1
        artifact(context, page, "theme-asset-recovery", native_server, denied)
        page.get_by_role("link", name="Product details").click()
        expect(page.locator("body")).to_have_text(
            "Native synthetic product details remain available."
        )
        assert not denied
    finally:
        context.close()


def test_selection_and_dom_removal_release_parsed_resources(chromium, native_server):
    context, page, denied = start(chromium, native_server)
    try:
        page.evaluate("""async()=>{
          const THREE=await import('/vendor/three.module.min.js');
          const {GLTFLoader}=await import('/vendor/GLTFLoader.js');
          window.resources={parsed:[],disposed:[]};
          for(const type of [THREE.BufferGeometry,THREE.Material]){
            const dispose=type.prototype.dispose;
            type.prototype.dispose=function(){window.resources.disposed.push(this.uuid);return dispose.call(this);};
          }
          const parse=GLTFLoader.prototype.parseAsync;
          GLTFLoader.prototype.parseAsync=async function(...args){
            const result=await parse.apply(this,args);
            for(const scene of result.scenes)scene.traverse(object=>{
              if(object.geometry)window.resources.parsed.push(object.geometry.uuid);
              for(const material of [].concat(object.material||[]))window.resources.parsed.push(material.uuid);
            });return result;
          };
        }""")
        choose_medium(page)
        page.get_by_role("button", name="Explore in 3D").click()
        state(page, "ready")
        first = page.evaluate("window.resources.parsed")
        assert len(set(first)) == 2
        page.get_by_label("Size", exact=True).select_option("s")
        expect(page.locator("[data-viewer-status]")).to_contain_text(
            "unavailable for this selection"
        )
        assert page.locator("canvas").count() == 0
        expect(page.locator("[data-viewer-stage]")).to_be_hidden()
        assert all(page.evaluate("window.resources.disposed").count(item) == 1 for item in first)
        choose_medium(page)
        page.get_by_role("button", name="Explore in 3D").click()
        state(page, "ready")
        assert len(native_server.posts) == 5
        page.evaluate("document.querySelector('#viewer').remove()")
        page.wait_for_function("window.resources.disposed.length===4")
        assert all(
            page.evaluate("window.resources.disposed").count(item) == 1
            for item in page.evaluate("window.resources.parsed")
        )
        assert page.locator("canvas").count() == 0
        artifact(context, page, "theme-selection-removal-disposal", native_server, denied)
        assert not denied
    finally:
        context.close()


def test_page_transition_restoration_mounts_one_controller(chromium, native_server):
    context, page, denied = start(chromium, native_server)
    try:
        choose_medium(page)
        page.get_by_role("button", name="Explore in 3D").click()
        state(page, "ready")
        assert len(native_server.posts) == 2
        page.evaluate("dispatchEvent(new PageTransitionEvent('pagehide',{persisted:true}))")
        state(page, "disposed")
        assert page.locator("canvas").count() == 0
        page.evaluate("dispatchEvent(new PageTransitionEvent('pageshow',{persisted:true}))")
        state(page, "idle")
        expect(page.get_by_role("button", name="Explore in 3D")).to_be_visible()
        assert len(native_server.posts) == 3
        # A second pageshow cannot attach another controller/listener to the root.
        page.evaluate("dispatchEvent(new PageTransitionEvent('pageshow',{persisted:true}))")
        page.get_by_role("button", name="Explore in 3D").click()
        state(page, "ready")
        assert len(native_server.posts) == 4
        assert page.locator("canvas").count() == 1
        page.get_by_label("Size", exact=True).select_option("s")
        expect(page.locator("[data-viewer-status]")).to_contain_text(
            "unavailable for this selection"
        )
        assert len(native_server.posts) == 5
        assert page.locator("canvas").count() == 0
        artifact(context, page, "theme-pageshow-restoration", native_server, denied)
        assert not denied
    finally:
        context.close()


def test_removed_root_reinserted_restores_one_live_controller(chromium, native_server):
    context, page, denied = start(chromium, native_server)
    try:
        choose_medium(page)
        page.get_by_role("button", name="Explore in 3D").click()
        state(page, "ready")
        assert len(native_server.posts) == 2
        page.evaluate(
            "window.removedRoot=document.querySelector('#viewer');window.removedRoot.remove()"
        )
        page.wait_for_function("window.removedRoot.dataset.viewerState==='disposed'")
        assert page.evaluate("window.removedRoot.querySelectorAll('canvas').length") == 0
        page.evaluate(
            "document.querySelector('.summary').append(window.removedRoot);dispatchEvent(new PageTransitionEvent('pageshow',{persisted:true}))"
        )
        state(page, "idle")
        expect(page.get_by_role("button", name="Explore in 3D")).to_be_visible()
        assert len(native_server.posts) == 3
        page.evaluate("dispatchEvent(new PageTransitionEvent('pageshow',{persisted:true}))")
        page.get_by_role("button", name="Explore in 3D").click()
        state(page, "ready")
        assert len(native_server.posts) == 4
        assert page.locator("canvas").count() == 1
        page.get_by_label("Size", exact=True).select_option("s")
        expect(page.locator("[data-viewer-status]")).to_contain_text(
            "unavailable for this selection"
        )
        assert len(native_server.posts) == 5
        assert page.locator("canvas").count() == 0
        artifact(context, page, "theme-root-reinsertion", native_server, denied)
        assert not denied
    finally:
        context.close()
