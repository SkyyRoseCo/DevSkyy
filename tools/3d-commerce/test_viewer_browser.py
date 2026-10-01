"""Loopback Chromium/Three r170; fixture acceptance is never written to a product registry."""

import hashlib
import json
import struct
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlsplit

import pytest
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
VENDOR = ROOT / "wordpress-theme/skyyrose-flagship-2/assets/js/lib/three-r170"
REGISTRY = "a" * 64
EVIDENCE = ROOT / "tasks/3d-commerce-20261001/evidence"


def glb(uri=False):
    binary = struct.pack("<9f", -1, -1, 0, 1, -1, 0, 0, 1, 0)
    doc = {
        "asset": {"version": "2.0"},
        "buffers": [{"byteLength": len(binary)}],
        "bufferViews": [{"buffer": 0, "byteOffset": 0, "byteLength": len(binary)}],
        "accessors": [
            {
                "bufferView": 0,
                "componentType": 5126,
                "count": 3,
                "type": "VEC3",
                "min": [-1, -1, 0],
                "max": [1, 1, 0],
            }
        ],
        "meshes": [{"primitives": [{"attributes": {"POSITION": 0}, "material": 0}]}],
        "materials": [
            {"doubleSided": True, "pbrMetallicRoughness": {"baseColorFactor": [0.8, 0.2, 0.3, 1]}}
        ],
        "nodes": [{"mesh": 0}],
        "scenes": [{"nodes": [0]}],
        "scene": 0,
    }
    if uri:
        doc["buffers"][0]["uri"] = "https://example.invalid/unbound.bin"
    raw = json.dumps(doc, separators=(",", ":")).encode()
    raw += b" " * (-len(raw) % 4)
    return (
        struct.pack("<III", 0x46546C67, 2, 28 + len(raw) + len(binary))
        + struct.pack("<II", len(raw), 0x4E4F534A)
        + raw
        + struct.pack("<II", len(binary), 0x004E4942)
        + binary
    )


def fixture(mode, port):
    payload = glb(mode == "uri")
    products = [
        {
            "sku": sku,
            "native_sku": sku,
            "product_id": i + 1,
            "variation_id": 0,
            "attributes": {},
            "url": f"http://127.0.0.1:{port}/product/{sku}",
            "name": "Synthetic triangle",
        }
        for i, sku in enumerate(["fixture-a", "fixture-b"])
    ]
    entries = [
        {
            **p,
            "asset_url": f"/asset.glb?mode={mode}",
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
        for p in products
    ]
    manifest = {
        "schema": "skyyrose.accepted-glb-runtime.v1",
        "registry_sha256": REGISTRY,
        "publication_authorized": True,
        "entries": entries,
    }
    if mode == "stale":
        manifest["registry_sha256"] = "b" * 64
    if mode == "unaccepted":
        entries[0]["creative_approval"] = "BLOCKED"
    if mode == "variation":
        entries[0]["variation_id"] = 99
    if mode == "duplicate":
        entries.append(entries[0])
    if mode == "unknown":
        entries.append({**entries[0], "sku": "unknown"})
    return f"""<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Local synthetic viewer fixture</title>
<style>body{{font:18px system-ui;margin:16px;color:#111;background:#fafafa}}button,a{{display:inline-block;padding:12px;min-height:24px}}button:focus-visible,a:focus-visible,[tabindex]:focus-visible{{outline:3px solid #124faa;outline-offset:2px}}[data-viewer-stage]{{height:360px;width:100%;touch-action:none}}[data-viewer-stage]>div{{height:100%;width:100%}}canvas{{display:block;width:100%;height:100%}}[hidden]{{display:none!important}}</style>
<main id="viewer"><h1>Synthetic asset fixture</h1><p>This triangle tests local behavior only.</p><ul aria-label="Product details"><li><a href="/product/fixture-a">Product A details</a><button data-viewer-open="fixture-a">View A in 3D</button></li><li><a href="/product/fixture-b">Product B details</a><button data-viewer-open="fixture-b">View B in 3D</button></li></ul>
<p data-viewer-status role="status" aria-live="polite">Product details available.</p><div data-viewer-stage tabindex="0" role="group" aria-label="3D product view; use arrow keys to rotate" hidden></div><button data-viewer-retry hidden>Retry 3D view</button><button data-viewer-reset disabled>Reset view</button><button data-viewer-back hidden>Back to products</button></main>
<script type="module">
import {{createViewer}} from '/viewer.mjs'; import {{createThreeRenderer}} from '/three-renderer.mjs';
const mode={json.dumps(mode)}; const products={json.dumps(products)}; const manifest={json.dumps(manifest)};
window.metrics={{created:0,disposed:0,resolved:0}};
window.products=products;
window.resolveProduct=async p=>{{window.metrics.resolved++; if(mode==='selection-delay')await new Promise(r=>setTimeout(r,300)); return {{...p,registry_sha256:'{REGISTRY}',available:mode!=='unavailable',...(mode==='native-stale'?{{variation_id:5}}:{{}})}};}};
const factory=async args=>{{
 if(mode==='webgl-failure'){{const original=HTMLCanvasElement.prototype.getContext; HTMLCanvasElement.prototype.getContext=function(type,...rest){{return type.startsWith('webgl')?null:original.call(this,type,...rest);}};}}
 const renderer=await createThreeRenderer(args,new URL('/vendor/',location.href)); window.metrics.created++;
 const dispose=renderer.dispose; renderer.dispose=()=>{{window.metrics.disposed++;dispose();}};
 if(mode==='late-renderer' && window.metrics.created===1)await new Promise(r=>setTimeout(r,350));
 return renderer;
}};
try{{window.viewer=createViewer(document.querySelector('#viewer'),{{products,manifest,registrySha:'{REGISTRY}',resolveProduct:p=>window.resolveProduct(p),rendererFactory:factory,timeoutMs:mode==='timeout'?1:3000}});}}catch(error){{document.querySelector('#viewer').dataset.viewerState='error';document.querySelector('[data-viewer-status]').textContent='3D view unavailable. Product details remain available.';window.initError=String(error);}}
window.fixtureReady=true;
</script></html>""".encode()


@pytest.fixture(scope="module")
def server():
    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *_):
            pass

        def do_GET(self):
            request = urlsplit(self.path)
            mode = parse_qs(request.query).get("mode", ["ready"])[0]
            if request.path == "/":
                data, mime = fixture(mode, self.server.server_port), "text/html"
            elif request.path in {"/viewer.mjs", "/three-renderer.mjs"}:
                data, mime = (HERE / request.path[1:]).read_bytes(), "text/javascript"
            elif request.path.startswith("/vendor/") and request.path[8:] in {
                "three.module.min.js",
                "GLTFLoader.js",
                "BufferGeometryUtils.js",
            }:
                data, mime = (VENDOR / request.path[8:]).read_bytes(), "text/javascript"
            elif request.path == "/asset.glb":
                self.server.asset_requests += 1
                data, mime = glb(mode == "uri"), "model/gltf-binary"
                if mode == "byte-swap":
                    data = data[:-1] + bytes([data[-1] ^ 1])
                if mode == "network-error":
                    self.send_error(503)
                    return
            elif request.path.startswith("/product/"):
                data, mime = b"Native product fallback fixture", "text/plain"
            else:
                self.send_error(404)
                return
            self.send_response(200)
            self.send_header("Content-Type", mime)
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)

    instance = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    instance.asset_requests = 0
    thread = threading.Thread(target=instance.serve_forever, daemon=True)
    thread.start()
    yield instance
    instance.shutdown()
    thread.join()


@pytest.fixture(scope="module")
def browser():
    with sync_playwright() as runtime:
        app = runtime.chromium.launch(
            args=["--use-gl=angle", "--use-angle=swiftshader", "--enable-unsafe-swiftshader"]
        )
        yield app
        app.close()


def start(browser, server, mode="ready", **options):
    context = browser.new_context(service_workers="block", **options)
    denied = []
    origin = f"http://127.0.0.1:{server.server_port}"

    def restrict(route):
        if route.request.url.startswith(origin + "/") or route.request.url.startswith(
            "blob:" + origin + "/"
        ):
            route.continue_()
        else:
            denied.append(route.request.url)
            route.abort()

    context.route("**/*", restrict)
    page = context.new_page()
    page.set_default_timeout(5000)
    page.set_default_navigation_timeout(10000)
    page.goto(origin + "/?mode=" + mode)
    if options.get("java_script_enabled", True):
        page.wait_for_function("window.fixtureReady===true")
    return context, page, denied


def state(page, expected):
    page.wait_for_function(
        "value=>document.querySelector('#viewer').dataset.viewerState===value",
        arg=expected,
        timeout=5000,
    )


def fallback(page):
    assert page.get_by_role("link", name="Product A details").is_visible()
    assert page.get_by_role("link", name="Product B details").is_visible()


@pytest.mark.parametrize(
    "mode",
    [
        "stale",
        "unaccepted",
        "variation",
        "duplicate",
        "unknown",
        "unavailable",
        "native-stale",
        "byte-swap",
        "uri",
        "network-error",
        "webgl-failure",
        "timeout",
    ],
)
def test_failures_keep_native_fallback(browser, server, mode):
    context, page, denied = start(browser, server, mode)
    try:
        if mode != "unknown":
            page.get_by_role("button", name="View A in 3D").click()
        state(page, "error")
        fallback(page)
        assert page.locator("canvas").count() == 0
        page.get_by_role("link", name="Product A details").click()
        assert page.locator("body").inner_text() == "Native product fallback fixture"
        assert not denied
    finally:
        context.close()


def test_ready_keyboard_reset_back_and_disposal(browser, server):
    context, page, denied = start(browser, server, reduced_motion="reduce")
    try:
        page.get_by_role("button", name="View A in 3D").focus()
        page.keyboard.press("Enter")
        state(page, "ready")
        fallback(page)
        assert page.locator("canvas").count() == 1
        stage = page.locator("[data-viewer-stage]")
        assert stage.evaluate("node=>node===document.activeElement")
        page.keyboard.press("ArrowRight")
        assert float(page.locator("[data-camera-yaw]").get_attribute("data-camera-yaw")) > 0
        page.keyboard.press("Home")
        assert page.locator("[data-camera-yaw]").get_attribute("data-camera-yaw") == "0"
        page.screenshot(path=str(EVIDENCE / "viewer-desktop.png"))
        page.keyboard.press("Escape")
        state(page, "idle")
        assert page.get_by_role("button", name="View A in 3D").evaluate(
            "node=>node===document.activeElement"
        )
        assert page.evaluate("window.metrics.disposed") == 1
        page.evaluate("window.viewer.dispose();window.viewer.dispose()")
        assert page.evaluate("window.metrics.disposed") == 1
        assert not denied
    finally:
        context.close()


def test_real_context_loss_retry_revalidates(browser, server):
    context, page, denied = start(browser, server)
    try:
        page.get_by_role("button", name="View A in 3D").click()
        state(page, "ready")
        page.locator("canvas").evaluate(
            "canvas=>canvas.getContext('webgl2').getExtension('WEBGL_lose_context').loseContext()"
        )
        state(page, "error")
        fallback(page)
        page.get_by_role("button", name="Retry 3D view").click()
        state(page, "ready")
        assert page.evaluate("window.metrics.resolved") == 2
        assert page.evaluate("window.metrics.disposed") == 1
        page.evaluate("window.viewer.dispose()")
        assert page.evaluate("window.metrics.disposed") == 2
        assert not denied
    finally:
        context.close()


def test_late_renderer_is_disposed_without_replacing_selection(browser, server):
    context, page, denied = start(browser, server, "late-renderer")
    try:
        page.get_by_role("button", name="View A in 3D").click()
        page.wait_for_function("window.metrics.created===1")
        page.get_by_role("button", name="View B in 3D").click()
        state(page, "ready")
        page.wait_for_function("window.metrics.disposed===1")
        assert page.locator("canvas").count() == 1
        assert page.evaluate("window.metrics.created") == 2
        assert not denied
    finally:
        context.close()


def test_back_cancels_loading_and_dispose_cancels_late_resolution(browser, server):
    context, page, denied = start(browser, server, "selection-delay")
    try:
        page.get_by_role("button", name="View A in 3D").click()
        state(page, "loading")
        fallback(page)
        page.get_by_role("button", name="Back to products").click()
        state(page, "idle")
        page.evaluate("window.viewer.open('fixture-b');window.viewer.dispose()")
        page.wait_for_timeout(400)
        state(page, "disposed")
        assert page.locator("canvas").count() == 0
        assert page.evaluate("window.metrics.created") == 0
        assert not denied
    finally:
        context.close()


def test_mobile_touch_and_error_retry_stale_selection(browser, server):
    context, page, denied = start(
        browser, server, viewport={"width": 390, "height": 844}, is_mobile=True, has_touch=True
    )
    try:
        page.get_by_role("button", name="View A in 3D").tap()
        state(page, "ready")
        rect = page.locator("[data-viewer-stage]").bounding_box()
        x = rect["x"] + 70
        y = rect["y"] + 70
        session = context.new_cdp_session(page)
        session.send(
            "Input.dispatchTouchEvent", {"type": "touchStart", "touchPoints": [{"x": x, "y": y}]}
        )
        session.send(
            "Input.dispatchTouchEvent",
            {"type": "touchMove", "touchPoints": [{"x": x + 50, "y": y + 20}]},
        )
        session.send("Input.dispatchTouchEvent", {"type": "touchEnd", "touchPoints": []})
        assert float(page.locator("[data-camera-yaw]").get_attribute("data-camera-yaw")) > 0
        page.get_by_role("button", name="Reset view").tap()
        assert page.locator("[data-camera-yaw]").get_attribute("data-camera-yaw") == "0"
        page.screenshot(path=str(EVIDENCE / "viewer-mobile.png"))
        page.locator("canvas").evaluate(
            "canvas=>canvas.getContext('webgl2').getExtension('WEBGL_lose_context').loseContext()"
        )
        state(page, "error")
        page.evaluate("window.resolveProduct=async p=>({...p,available:false})")
        page.get_by_role("button", name="Retry 3D view").tap()
        state(page, "error")
        fallback(page)
        assert page.evaluate("window.metrics.created") == 1
        assert not denied
    finally:
        context.close()


def test_no_javascript_native_links(browser, server):
    context, page, denied = start(browser, server, java_script_enabled=False)
    try:
        fallback(page)
        page.get_by_role("link", name="Product B details").click()
        assert page.locator("body").inner_text() == "Native product fallback fixture"
        assert not denied
    finally:
        context.close()
