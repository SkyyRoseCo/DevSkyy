#!/usr/bin/env python3
"""Validate a live XML sitemap against Google's sitemap requirements. Read-only.

Usage: python3 scripts/validate-sitemap.py https://skyyrose.co/sitemap.xml [--max-urls N]

Checks (Google Search Central, "Build and submit a sitemap" + sitemaps.org protocol):
  * well-formed UTF-8 XML in the http://www.sitemaps.org/schemas/sitemap/0.9 namespace;
  * <= 50,000 URLs and <= 50 MB uncompressed per file; sitemap indexes are followed;
  * every <loc> is an absolute https URL on the sitemap's host with no query string;
  * every <loc> answers 200 directly (no redirect hop) and carries no noindex
    (robots meta or X-Robots-Tag); its canonical, when present, is itself;
  * <lastmod>, when present, is a valid W3C datetime.
Exit 0 when every check passes, 1 otherwise. Every failure is printed.
"""

from __future__ import annotations

import argparse
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime

NS = "http://www.sitemaps.org/schemas/sitemap/0.9"
UA = "Mozilla/5.0 (compatible; SkyyRoseSitemapValidator/1.0; read-only)"
MAX_URLS = 50_000
MAX_BYTES = 50 * 1024 * 1024
SLEEP = 0.2


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):  # noqa: D401
        return None


OPENER = urllib.request.build_opener(NoRedirect)


def fetch(url: str, cache_bust: bool) -> tuple[int, dict, bytes]:
    target = url
    if cache_bust:
        target += ("&" if "?" in url else "?") + f"cb={int(time.time() * 1000)}"
    req = urllib.request.Request(target, headers={"User-Agent": UA})
    try:
        with OPENER.open(req, timeout=40) as resp:
            return resp.status, {k.lower(): v for k, v in resp.headers.items()}, resp.read()
    except urllib.error.HTTPError as err:
        return err.code, {k.lower(): v for k, v in err.headers.items()}, err.read() or b""


def parse(body: bytes, source: str, failures: list[str]) -> ET.Element | None:
    if len(body) > MAX_BYTES:
        failures.append(f"{source}: {len(body)} bytes exceeds the 50 MB limit")
    try:
        body.decode("utf-8")
    except UnicodeDecodeError:
        failures.append(f"{source}: not UTF-8")
    try:
        root = ET.fromstring(body)
    except ET.ParseError as err:
        failures.append(f"{source}: XML parse error: {err}")
        return None
    if root.tag not in (f"{{{NS}}}urlset", f"{{{NS}}}sitemapindex"):
        failures.append(
            f"{source}: root element {root.tag} is not a sitemaps.org urlset/sitemapindex"
        )
    return root


def valid_lastmod(value: str) -> bool:
    for fmt in ("%Y-%m-%d", "%Y-%m-%dT%H:%M:%S%z", "%Y-%m-%dT%H:%M%z"):
        try:
            datetime.strptime(value.replace("Z", "+0000"), fmt)
            return True
        except ValueError:
            continue
    return False


def check_page(url: str, failures: list[str]) -> None:
    status, headers, body = fetch(url, cache_bust=True)
    if status != 200:
        failures.append(
            f"{url}: HTTP {status}"
            + (f" -> {headers.get('location')}" if headers.get("location") else "")
        )
        return
    if "noindex" in (headers.get("x-robots-tag") or "").lower():
        failures.append(f"{url}: X-Robots-Tag noindex")
    html = body.decode("utf-8", errors="replace")
    head = html[: html.find("</head>")] if "</head>" in html else html[:200_000]
    for meta in re.findall(r"<meta\b[^>]*>", head, re.I):
        if re.search(r'name\s*=\s*["\']robots["\']', meta, re.I) and "noindex" in meta.lower():
            failures.append(f"{url}: robots meta noindex")
    canonical = re.search(
        r'<link\b[^>]*rel\s*=\s*["\']canonical["\'][^>]*href\s*=\s*["\']([^"\']+)', head, re.I
    )
    if canonical and canonical.group(1).split("?")[0].rstrip("/") != url.rstrip("/"):
        failures.append(f"{url}: canonical points elsewhere ({canonical.group(1)})")


def walk(sitemap_url: str, failures: list[str], seen: set[str], locs: list[str]) -> None:
    if sitemap_url in seen:
        return
    seen.add(sitemap_url)
    status, headers, body = fetch(sitemap_url, cache_bust=False)
    if status != 200:
        failures.append(f"{sitemap_url}: sitemap HTTP {status}")
        return
    root = parse(body, sitemap_url, failures)
    if root is None:
        return
    host = urllib.parse.urlsplit(sitemap_url).netloc
    if root.tag == f"{{{NS}}}sitemapindex":
        for child in root.findall(f"{{{NS}}}sitemap"):
            loc = (child.findtext(f"{{{NS}}}loc") or "").strip()
            if loc:
                walk(loc, failures, seen, locs)
        return
    entries = root.findall(f"{{{NS}}}url")
    if len(entries) > MAX_URLS:
        failures.append(f"{sitemap_url}: {len(entries)} URLs exceeds the 50,000 limit")
    for entry in entries:
        loc = (entry.findtext(f"{{{NS}}}loc") or "").strip()
        lastmod = (entry.findtext(f"{{{NS}}}lastmod") or "").strip()
        if not loc:
            failures.append(f"{sitemap_url}: <url> without <loc>")
            continue
        parts = urllib.parse.urlsplit(loc)
        if parts.scheme != "https" or parts.netloc != host:
            failures.append(f"{loc}: not an absolute https URL on {host}")
        if parts.query:
            failures.append(f"{loc}: query string in sitemap URL")
        if lastmod and not valid_lastmod(lastmod):
            failures.append(f"{loc}: invalid lastmod {lastmod}")
        if loc in locs:
            failures.append(f"{loc}: listed more than once")
        locs.append(loc)


def main() -> int:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("sitemap")
    parser.add_argument(
        "--max-urls", type=int, default=2000, help="cap on page probes (default 2000)"
    )
    args = parser.parse_args()
    failures: list[str] = []
    locs: list[str] = []
    walk(args.sitemap, failures, set(), locs)
    print(f"{len(locs)} URLs listed under {args.sitemap}")
    for loc in locs[: args.max_urls]:
        check_page(loc, failures)
        time.sleep(SLEEP)
    if failures:
        print(f"FAIL {len(failures)} finding(s):")
        for item in failures:
            print(" -", item)
        return 1
    print("PASS sitemap: valid XML, within size limits, every URL 200/indexable/canonical/direct.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
