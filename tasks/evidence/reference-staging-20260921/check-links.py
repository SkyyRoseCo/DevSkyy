import json
import re
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

html = Path("/tmp/skyyrose-home.html").read_text(errors="ignore")
base = "https://staging-7e48-skyyrose.wpcomstaging.com"
urls = []
for attr in ("href", "src"):
    for x in re.findall(attr + r'="([^"]+)"', html):
        x = x.replace("&#038;", "&")
        if x.startswith(("mailto:", "tel:", "javascript:", "#", "data:")):
            continue
        u = urllib.parse.urljoin(base, x)
        if u not in urls:
            urls.append(u)


def check(u):
    req = urllib.request.Request(
        u, method="HEAD", headers={"User-Agent": "SkyyRose-launch-evidence/1.0"}
    )
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            return {
                "url": u,
                "status": r.status,
                "final": r.geturl(),
                "location": r.headers.get("location"),
                "kind": "asset" if "/wp-content/" in u else "link",
            }
    except Exception as e:
        # HEAD unsupported; GET small range, still record redirects
        try:
            req = urllib.request.Request(
                u, headers={"User-Agent": "SkyyRose-launch-evidence/1.0", "Range": "bytes=0-1023"}
            )
            with urllib.request.urlopen(req, timeout=20) as r:
                return {
                    "url": u,
                    "status": r.status,
                    "final": r.geturl(),
                    "location": r.headers.get("location"),
                    "kind": "asset" if "/wp-content/" in u else "link",
                    "head_error": str(e),
                }
        except Exception as e2:
            return {
                "url": u,
                "status": None,
                "final": None,
                "location": None,
                "kind": "asset" if "/wp-content/" in u else "link",
                "error": repr(e2),
            }


with ThreadPoolExecutor(max_workers=12) as ex:
    out = list(ex.map(check, urls))
summary = {
    "source": "https://staging-7e48-skyyrose.wpcomstaging.com/",
    "count": len(out),
    "links": [x for x in out if x["kind"] == "link"],
    "assets": [x for x in out if x["kind"] == "asset"],
}
Path(
    "/Users/theceo/DevSkyy/tasks/evidence/reference-staging-20260921/links-commerce.json"
).write_text(json.dumps(summary, indent=2) + "\n")
from collections import Counter

print("count", len(out), "status", Counter(x["status"] for x in out))
for x in out:
    if x["status"] not in (200, 301, 302, 303, 307, 308):
        print("BAD", x)
for x in out:
    if x.get("final") and any(k in x["final"] for k in ("wp-login", "my-account", "login")):
        print("REDIRECT", x)
