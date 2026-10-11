#!/usr/bin/env python3
"""Prove the live site serves this theme's repo bytes. Read-only.

Usage:
  python3 scripts/verify-live-parity.py [--pages / /shop/ ...] [--json out.json]
  python3 scripts/verify-live-parity.py --rea-cdp http://127.0.0.1:9333   # + runtime evidence

Closes the repo -> live evidence gap (CLAUDE.md §2, bug-287): a repo fact is not a
live fact. For every page it checks, three ways:
  * each theme script/style the HTML references: served bytes == repo bytes, and the
    ?ver= content hash (functions.php skyyrose2_asset_version) matches the served bytes;
  * Jetpack Boost /_jb_static/ CSS bundles: which repo .min.css files they contain,
    byte-exact or after url() normalisation (Boost rewrites relative url() paths);
  * brand font policy: no font-CDN stylesheet, no cut family (CLAUDE.md §6).
With --rea-cdp, each page is also opened in that loopback CDP browser and captured by
REA (`rea-agents analyze-web-bundle`); every theme script that actually executed must
match a repo file by sha256. REA rejects cache-busted URLs, so the capture sees what
the edge cache serves visitors — which is the point.

Fails closed (bug-230): exit 0 PASS, 1 FAIL (drift or policy finding), 2 INCOMPLETE —
a non-200 page, a page with no theme assets, a REA error, or a capture with no theme
scripts is never reported as parity.
"""

from __future__ import annotations

import argparse
import hashlib
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

Fetch = Callable[[str], "tuple[int, bytes]"]
ReaRunner = Callable[[str], dict]


def fetch(url: str) -> tuple[int, bytes]:
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return resp.status, resp.read()
    except urllib.error.HTTPError as err:
        return err.code, b""
    except (urllib.error.URLError, TimeoutError):
        return 0, b""  # unreachable counts as non-200: INCOMPLETE, never PASS


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def theme_refs(html: str, host: str, folder: str) -> dict[str, str]:
    """Map theme-relative .js/.mjs/.css paths referenced by the page to their query."""
    html = html.replace("\\/", "/")
    pat = re.compile(
        re.escape(f"{host}/wp-content/themes/{folder}/")
        + r"([^\"'\s?#)]+\.(?:js|mjs|css))(\?[^\"'\s#)]*)?"
    )
    return {rel: (query or "") for rel, query in pat.findall(html)}


def concat_bundles(html: str, host: str) -> list[str]:
    return sorted(set(re.findall(re.escape(host) + r"/_jb_static/\?\?[0-9a-f]+", html)))


def font_findings(html: str) -> list[dict]:
    findings = []
    for href in re.findall(r"<link[^>]+href=['\"]([^'\"]+)['\"]", html):
        if not any(cdn in href for cdn in FONT_CDNS):
            continue
        findings.append({"kind": "font-cdn", "detail": f"font stylesheet from a CDN: {href[:120]}"})
        family = urllib.parse.unquote_plus(href).lower()
        findings += [
            {"kind": "cut-font", "detail": f"cut brand font '{cut}' loaded via {href[:80]}"}
            for cut in CUT_FONTS
            if cut in family
        ]
    return findings


def _normalise_css(text: str) -> str:
    return re.sub(r"url\([^)]*\)", "url()", text).strip()


def css_in_bundle(bundle: str, repo: Path) -> dict[str, str]:
    """Repo .min.css files contained in a concatenated bundle -> verification method."""
    found, normalised = {}, _normalise_css(bundle)
    for css in sorted((repo / "assets/css").glob("*.min.css")):
        text = css.read_text(encoding="utf-8", errors="replace").strip()
        if not text:
            continue
        rel = str(css.relative_to(repo))
        if text in bundle:
            found[rel] = "concat-exact"
        elif _normalise_css(text) in normalised:
            found[rel] = "concat-url-normalized"
    return found


def check_ref(rel: str, query: str, served: bytes, repo: Path) -> str | None:
    """Return a drift description, or None when the served asset is the repo's."""
    local = repo / rel
    if not local.is_file():
        return f"{rel}: served live but not in repo"
    if sha256(served) != sha256(local.read_bytes()):
        return f"{rel}: served bytes differ from repo ({sha256(served)[:12]} vs {sha256(local.read_bytes())[:12]})"
    ver = re.search(r"ver=[^&-]+-([0-9a-f]{12})", query)
    if ver and len(served) <= HASHED_MAX_BYTES and not sha256(served).startswith(ver.group(1)):
        return f"{rel}: ?ver= hash {ver.group(1)} does not match served bytes (stale cached HTML)"
    return None


def rea_capture(cdp: str) -> ReaRunner:
    """Open the URL in a new tab of the loopback CDP browser and capture it with REA."""

    def run(url: str) -> dict:
        req = urllib.request.Request(f"{cdp}/json/new?{url}", method="PUT")
        with urllib.request.urlopen(req, timeout=30) as resp:
            target = json.load(resp)["id"]
        try:
            time.sleep(8)  # let the page settle before the bounded observation window
            out = subprocess.run(
                [
                    *REA,
                    "analyze-web-bundle",
                    cdp,
                    target,
                    "--allowed-origins",
                    urllib.parse.urlsplit(url)._replace(path="", query="").geturl(),
                    "--observation-ms",
                    "4000",
                    "--format",
                    "json",
                ],
                capture_output=True,
                text=True,
                timeout=300,
                check=False,
            )
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
    """Match every executed theme script in REA evidence to repo bytes."""
    result = evidence.get("normalized_result")
    if not result or result.get("completeness", {}).get("status") != "complete":
        return [], [], f"REA capture failed or incomplete: {str(evidence.get('error', ''))[:200]}"
    index = {
        sha256(p.read_bytes()): str(p.relative_to(repo))
        for p in repo.rglob("*")
        if p.suffix in (".js", ".mjs") and p.is_file() and "node_modules" not in p.parts
    }
    verified, findings = [], []
    for node in result["observations"]["chunks"]["nodes"]:
        if f"/themes/{folder}/" not in node.get("url", ""):
            continue
        rel = node["url"].split(f"/themes/{folder}/", 1)[1].split("?", 1)[0]
        hit = index.get(node.get("artifact_sha256", ""))
        if hit:
            verified.append({"asset": hit, "method": "rea-runtime"})
        else:
            findings.append(
                {"kind": "runtime-drift", "detail": f"{rel}: executed bytes match no repo file"}
            )
    if not verified and not findings:
        return [], [], "REA saw no executed theme scripts"
    return verified, findings, None


def verify(
    host: str,
    pages: list[str],
    repo: Path,
    folder: str,
    get: Fetch,
    rea_runner: ReaRunner | None = None,
) -> dict:
    verified: list[dict] = []
    findings: list[dict] = []
    incomplete: list[str] = []
    for path in pages:
        url = f"{host}{path}"
        status, body = get(f"{url}?cb={int(time.time())}")
        if status != 200:
            incomplete.append(f"{path}: HTTP {status}")
            continue
        html = body.decode("utf-8", "replace")
        refs = theme_refs(html, host, folder)
        bundles = concat_bundles(html, host)
        if not refs and not bundles:
            incomplete.append(f"{path}: no theme assets referenced")
            continue
        for rel, query in sorted(refs.items()):
            code, served = get(f"{host}/wp-content/themes/{folder}/{rel}{query}")
            drift = f"{rel}: HTTP {code}" if code != 200 else check_ref(rel, query, served, repo)
            if drift:
                findings.append({"kind": "drift", "page": path, "detail": drift})
            else:
                verified.append({"page": path, "asset": rel, "method": "http-bytes"})
        for bundle in bundles:
            code, blob = get(bundle)
            if code != 200:
                incomplete.append(f"{path}: bundle {bundle} HTTP {code}")
                continue
            for rel, method in css_in_bundle(blob.decode("utf-8", "replace"), repo).items():
                verified.append({"page": path, "asset": rel, "method": method})
        findings += [{**f, "page": path} for f in font_findings(html)]
        if rea_runner is not None:
            ok, bad, problem = runtime_check(rea_runner(url), repo, folder)
            verified += [{**v, "page": path} for v in ok]
            findings += [{**f, "page": path} for f in bad]
            if problem:
                incomplete.append(f"{path}: {problem}")
    status = "FAIL" if findings else "INCOMPLETE" if incomplete else "PASS"
    return {"status": status, "verified": verified, "findings": findings, "incomplete": incomplete}


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
    report = verify(args.host.rstrip("/"), args.pages, repo, args.folder, fetch, runner)
    if args.json:
        args.json.write_text(json.dumps(report, indent=1) + "\n", encoding="utf-8")
    for item in report["findings"]:
        print(f"FINDING [{item['kind']}] {item.get('page', '')} {item['detail']}")
    for item in report["incomplete"]:
        print(f"INCOMPLETE {item}")
    print(
        f"{report['status']}: {len(report['verified'])} asset checks verified, "
        f"{len(report['findings'])} findings, {len(report['incomplete'])} incomplete"
    )
    return {"PASS": 0, "FAIL": 1}.get(report["status"], 2)


if __name__ == "__main__":
    sys.exit(main())
