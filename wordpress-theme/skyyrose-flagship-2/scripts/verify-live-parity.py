#!/usr/bin/env python3
"""Prove the live site serves this theme's repo bytes. Read-only.

Usage:
  python3 scripts/verify-live-parity.py [--pages / /shop/ ...] [--json out.json]
  python3 scripts/verify-live-parity.py --rea-cdp http://127.0.0.1:9333   # + runtime evidence

Closes the repo -> live evidence gap (CLAUDE.md §2, bug-287): a repo fact is not a
live fact. Each page is fetched at its bare URL — the response visitors get from the
edge cache — without following redirects, and checked four ways:
  * every distinct theme script/style URL in the HTML: served bytes == the repo file at
    that path, and for hash-sized assets the ?ver= carries the content hash
    (functions.php skyyrose2_asset_version) of the served bytes;
  * Jetpack Boost /_jb_static/ CSS bundles: repo .min.css files are matched exactly,
    after reproducing Boost's url() rewrite; theme CSS left unmatched is drift;
  * homepage inline blocks (critical CSS, hero controller) == their repo sources;
  * brand font policy: no font-CDN stylesheet, no cut family declared in any CSS.
With --rea-cdp, each page is also opened in that loopback CDP browser and captured by
REA (`rea-agents analyze-web-bundle`); every theme script that executed must match the
repo file at its own path.

Fails closed (bug-230): exit 0 PASS, 1 FAIL (drift or policy finding), 2 INCOMPLETE —
a non-200 or redirected page, a page with no theme assets, a missing required inline
block, a REA error or exception, or a capture with no theme scripts is never parity.
"""

from __future__ import annotations

import argparse
import hashlib
import http.client
import json
import re
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from collections.abc import Callable
from pathlib import Path

UA = "Mozilla/5.0 (compatible; SkyyRoseLiveParity/1.0; read-only)"
REA = ["npx", "--yes", "rea-agents@6.4.0"]
HASHED_MAX_BYTES = 262144  # skyyrose2_asset_version() hashes files at or below this size
FONT_CDNS = ("fonts.googleapis.com", "fonts-api.wp.com", "fonts.bunny.net", "use.typekit.net")
CUT_FONTS = ("playfair display", "cormorant garamond", "bebas neue", "yellowtail")
DEFAULT_PAGES = ["/", "/shop/", "/collections/black-rose/", "/product/br-001/"]
# inc/critical-rendering.php prints these verbatim on the front page (no URL to fetch).
HOME_INLINE = {
    "/": [
        ("style", "skyyrose2-critical-home", "assets/css/critical/home.min.css"),
        ("script", "skyyrose2-visual-recovery-early", "assets/js/visual-recovery.min.js"),
    ]
}

Fetch = Callable[[str], "tuple[int, bytes]"]
ReaRunner = Callable[[str], dict]
Inline = dict[str, list[tuple[str, str, str]]]


class _NoRedirect(urllib.request.HTTPRedirectHandler):
    """Surface 3xx as the status: a redirected page must not be verified as its target."""

    def redirect_request(self, *args, **kwargs):  # noqa: ANN002, ANN003
        return None


OPENER = urllib.request.build_opener(_NoRedirect)


def fetch(url: str) -> tuple[int, bytes]:
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    try:
        with OPENER.open(req, timeout=30) as resp:
            return resp.status, resp.read()
    except urllib.error.HTTPError as err:  # includes unfollowed 3xx
        return err.code, b""
    except (http.client.HTTPException, OSError):
        return 0, b""  # unreachable, reset or truncated: INCOMPLETE, never PASS


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def theme_refs(html: str, host: str, folder: str) -> list[tuple[str, str]]:
    """Every distinct (theme-relative path, query) the page references."""
    html = html.replace("\\/", "/")
    pat = re.compile(
        re.escape(f"{host}/wp-content/themes/{folder}/")
        + r"([^\"'\s?#)]+\.(?:js|mjs|css))(\?[^\"'\s#)]*)?"
    )
    return sorted({(rel, query or "") for rel, query in pat.findall(html)})


def concat_bundles(html: str, host: str) -> list[tuple[str, str]]:
    """Jetpack Boost bundles as (url, kind): a <link> loads CSS, a <script> loads JS."""
    bundle = re.escape(host) + r"/_jb_static/\?\?[0-9a-f]+"
    found = {(url, "css") for url in re.findall(rf"<link\b[^>]*\bhref=['\"]({bundle})['\"]", html)}
    found |= {(url, "js") for url in re.findall(rf"<script\b[^>]*\bsrc=['\"]({bundle})['\"]", html)}
    return sorted(found)


def cdn_font_findings(html: str) -> list[dict]:
    findings = []
    for href in re.findall(r"<link[^>]+href=['\"]([^'\"]+)['\"]", html):
        if any(cdn in href for cdn in FONT_CDNS):
            findings.append(
                {"kind": "font-cdn", "detail": f"font stylesheet from a CDN: {href[:120]}"}
            )
            findings += cut_font_findings(urllib.parse.unquote_plus(href), href[:80])
    return findings


def cut_font_findings(css: str, where: str) -> list[dict]:
    """Cut brand families named in font-family declarations or a font-CDN family list."""
    text = css.lower()
    declared = re.findall(r"([^{};]{0,60})\{[^}]*?font-family\s*:([^;}]*)", text)
    findings = []
    for cut in CUT_FONTS:
        selectors = [sel.strip() for sel, family in declared if cut in family]
        if selectors:
            context = f" (selector {selectors[0][-50:]!r})"
        elif not declared and cut in text:
            context = ""  # a font-CDN family list, not a stylesheet
        else:
            continue
        findings.append(
            {"kind": "cut-font", "detail": f"cut brand font '{cut}' in {where}{context}"}
        )
    return findings


def boost_rewrite(text: str, rel: str, folder: str) -> str:
    """Reproduce Jetpack Boost's url() rewrite: relative targets made root-relative, unquoted."""
    base = f"/wp-content/themes/{folder}/{Path(rel).parent.as_posix()}/"

    def swap(match: re.Match) -> str:
        target = match.group(2)
        if re.match(r"(?:[a-z]+:|/|#)", target, re.I):
            return match.group(0)
        return f"url({base}{target})"

    return re.sub(r"url\(\s*(['\"]?)([^'\")]+)\1\s*\)", swap, text)


def bundle_contents(bundle: str, repo: Path, folder: str, kind: str) -> tuple[dict[str, str], str]:
    """Repo .min.css/.min.js files the bundle contains -> method, plus the unmatched remainder."""
    found, rest = {}, bundle
    for asset in sorted((repo / f"assets/{kind}").glob(f"*.min.{kind}")):
        text = asset.read_text(encoding="utf-8", errors="replace").strip()
        if not text:
            continue
        rel = str(asset.relative_to(repo))
        variants = [(text, "concat-exact")]
        if kind == "css":
            variants.append((boost_rewrite(text, rel, folder), "concat-boost-url"))
        for variant, method in variants:
            if variant in rest:
                found[rel] = method
                rest = rest.replace(variant, "")
                break
    return found, rest


def unmatched_theme_code(rest: str, folder: str) -> str | None:
    """A theme fingerprint left after removing every matched repo file is stale theme code."""
    marker = re.search(rf"[.#]sr2-|--sr2-|/themes/{re.escape(folder)}/", rest)
    if not marker:
        return None
    return re.sub(r"\s+", " ", rest[max(0, marker.start() - 60) : marker.start() + 80])


def check_ref(rel: str, query: str, served: bytes, repo: Path) -> str | None:
    """Return a drift description, or None when the served asset is the repo's."""
    local = repo / rel
    if not local.is_file():
        return f"{rel}: served live but not in repo"
    if sha256(served) != sha256(local.read_bytes()):
        return f"{rel}: served bytes differ from repo ({sha256(served)[:12]} vs {sha256(local.read_bytes())[:12]})"
    ver = urllib.parse.parse_qs(query.lstrip("?")).get("ver", [None])[0]
    if ver is None or len(served) > HASHED_MAX_BYTES:
        return None  # Jetpack ?m= rewrites and large mtime-keyed files: bytes already proven
    hashed = re.fullmatch(r"[^-]+-([0-9a-f]{12})", ver)
    if not hashed:
        return f"{rel}: ?ver={ver} has no content hash (pre-hash cache key)"
    if not sha256(served).startswith(hashed.group(1)):
        return (
            f"{rel}: ?ver= hash {hashed.group(1)} does not match served bytes (stale cached HTML)"
        )
    return None


def inline_check(
    html: str, path: str, required: Inline, repo: Path, host: str, folder: str
) -> dict:
    out: dict = {"verified": [], "findings": [], "incomplete": []}
    assets = f"{host}/wp-content/themes/{folder}/assets"
    for tag, block_id, rel in required.get(path, []):
        found = re.search(
            rf"<{tag}\b[^>]*\bid=[\"']{re.escape(block_id)}[\"'][^>]*>(.*?)</{tag}>", html, re.S
        )
        if not found:
            out["incomplete"].append(f"{path}: required inline block #{block_id} absent")
            continue
        local = repo / rel
        expected = (
            local.read_text(encoding="utf-8").strip().replace("__SKYYROSE2_ASSETS__", assets)
            if local.is_file()
            else None
        )
        if found.group(1).strip() == expected:
            out["verified"].append({"page": path, "asset": rel, "method": "inline-exact"})
        else:
            out["findings"].append(
                {"kind": "inline-drift", "page": path, "detail": f"#{block_id} != {rel}"}
            )
    return out


def rea_capture(cdp: str) -> ReaRunner:
    """Open the URL in a new tab of the loopback CDP browser and capture it with REA."""

    def run(url: str) -> dict:
        req = urllib.request.Request(f"{cdp}/json/new?{url}", method="PUT")
        with urllib.request.urlopen(req, timeout=30) as resp:
            target = json.load(resp)["id"]
        try:
            time.sleep(8)  # let the page settle before the bounded observation window
            origin = urllib.parse.urlsplit(url)._replace(path="", query="").geturl()
            out = subprocess.run(
                [*REA, "analyze-web-bundle", cdp, target, "--allowed-origins", origin,
                 "--observation-ms", "4000", "--format", "json"],
                capture_output=True, text=True, timeout=300, check=False,
            )  # fmt: skip
            try:
                return json.loads(out.stdout)
            except json.JSONDecodeError:
                return {"error": f"REA exit {out.returncode}: {out.stderr[-300:]}"}
        finally:
            urllib.request.urlopen(f"{cdp}/json/close/{target}", timeout=10).close()

    return run


def runtime_check(
    evidence: dict, repo: Path, folder: str
) -> tuple[list[dict], list[dict], str | None]:
    """Every executed theme script must equal the repo file at its own path."""
    result = evidence.get("normalized_result")
    if not result or result.get("completeness", {}).get("status") != "complete":
        return [], [], f"REA capture failed or incomplete: {str(evidence.get('error', ''))[:200]}"
    verified, findings = [], []
    for node in result["observations"]["chunks"]["nodes"]:
        if f"/themes/{folder}/" not in node.get("url", ""):
            continue
        rel = node["url"].split(f"/themes/{folder}/", 1)[1].split("?", 1)[0]
        local = repo / rel
        if local.is_file() and sha256(local.read_bytes()) == node.get("artifact_sha256"):
            verified.append({"asset": rel, "method": "rea-runtime"})
        else:
            findings.append(
                {"kind": "runtime-drift", "detail": f"{rel}: executed bytes differ from repo"}
            )
    if not verified and not findings:
        return [], [], "REA saw no executed theme scripts"
    return verified, findings, None


def _merge(report: dict, part: dict) -> None:
    for key in ("verified", "findings", "incomplete"):
        report[key] += part.get(key, [])


def _check_assets(html: str, path: str, host: str, folder: str, repo: Path, get: Fetch) -> dict:
    out: dict = {"verified": [], "findings": [], "incomplete": []}
    for rel, query in theme_refs(html, host, folder):
        code, served = get(f"{host}/wp-content/themes/{folder}/{rel}{query}")
        drift = f"{rel}: HTTP {code}" if code != 200 else check_ref(rel, query, served, repo)
        if drift:
            out["findings"].append({"kind": "drift", "page": path, "detail": drift})
        else:
            out["verified"].append({"page": path, "asset": rel, "method": "http-bytes"})
            if rel.endswith(".css"):
                out["findings"] += [
                    {**f, "page": path}
                    for f in cut_font_findings(served.decode("utf-8", "replace"), rel)
                ]
    for bundle, kind in concat_bundles(html, host):
        code, blob = get(bundle)
        if code != 200:
            out["incomplete"].append(f"{path}: bundle {bundle} HTTP {code}")
            continue
        text = blob.decode("utf-8", "replace")
        found, rest = bundle_contents(text, repo, folder, kind)
        out["verified"] += [{"page": path, "asset": rel, "method": m} for rel, m in found.items()]
        stale = unmatched_theme_code(rest, folder)
        if stale:
            out["findings"].append(
                {"kind": f"unmatched-theme-{kind}", "page": path, "detail": f"{bundle}: …{stale}…"}
            )
        if kind == "css":
            out["findings"] += [{**f, "page": path} for f in cut_font_findings(text, bundle)]
    return out


def _check_runtime(url: str, path: str, repo: Path, folder: str, runner: ReaRunner) -> dict:
    try:
        evidence = runner(url)
    except Exception as err:  # noqa: BLE001 — any runner failure is INCOMPLETE, never a traceback
        return {"incomplete": [f"{path}: REA runner failed: {err}"]}
    ok, bad, problem = runtime_check(evidence, repo, folder)
    return {
        "verified": [{**v, "page": path} for v in ok],
        "findings": [{**f, "page": path} for f in bad],
        "incomplete": [f"{path}: {problem}"] if problem else [],
    }


def verify(host: str, pages: list[str], repo: Path, folder: str, get: Fetch,rea_runner: ReaRunner | None = None, inline_required: Inline | None = None) -> dict:  # fmt: skip
    report: dict = {"verified": [], "findings": [], "incomplete": []}
    for path in pages:
        url = f"{host}{path}"
        status, body = get(url)  # bare URL: what the edge cache serves visitors
        if status != 200:
            kind = "redirect" if 300 <= status < 400 else "HTTP"
            report["incomplete"].append(f"{path}: {kind} {status}")
            continue
        html = body.decode("utf-8", "replace")
        if not theme_refs(html, host, folder) and not concat_bundles(html, host):
            report["incomplete"].append(f"{path}: no theme assets referenced")
            continue
        _merge(report, _check_assets(html, path, host, folder, repo, get))
        _merge(report, inline_check(html, path, inline_required or {}, repo, host, folder))
        report["findings"] += [{**f, "page": path} for f in cdn_font_findings(html)]
        for block in re.findall(r"<style\b[^>]*>(.*?)</style>", html, re.S):
            report["findings"] += [
                {**f, "page": path} for f in cut_font_findings(block, "inline <style>")
            ]
        if rea_runner is not None:
            _merge(report, _check_runtime(url, path, repo, folder, rea_runner))
    status = "FAIL" if report["findings"] else "INCOMPLETE" if report["incomplete"] else "PASS"
    return {"status": status, **report}


def main() -> int:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    ap.add_argument("--host", default="https://skyyrose.co")
    ap.add_argument("--pages", nargs="+", default=DEFAULT_PAGES)
    ap.add_argument("--folder", default="skyyrose-flagship-2", help="live theme folder name")
    ap.add_argument("--rea-cdp", help="loopback CDP endpoint, e.g. http://127.0.0.1:9333")
    ap.add_argument("--json", type=Path, help="write the full report here")
    args = ap.parse_args()
    if args.rea_cdp and urllib.parse.urlsplit(args.rea_cdp).hostname not in (
        "127.0.0.1",
        "localhost",
    ):
        ap.error("--rea-cdp must be a loopback endpoint")
    repo = Path(__file__).resolve().parent.parent
    runner = rea_capture(args.rea_cdp) if args.rea_cdp else None
    report = verify(
        args.host.rstrip("/"), args.pages, repo, args.folder, fetch, runner, HOME_INLINE
    )
    if args.json:
        args.json.write_text(json.dumps(report, indent=1) + "\n", encoding="utf-8")
    for item in report["findings"]:
        print(f"FINDING [{item['kind']}] {item.get('page', '')} {item['detail']}")
    for item in report["incomplete"]:
        print(f"INCOMPLETE {item}")
    print(f"{report['status']}: {len(report['verified'])} asset checks verified, "
          f"{len(report['findings'])} findings, {len(report['incomplete'])} incomplete")  # fmt: skip
    return {"PASS": 0, "FAIL": 1}.get(report["status"], 2)


if __name__ == "__main__":
    sys.exit(main())
