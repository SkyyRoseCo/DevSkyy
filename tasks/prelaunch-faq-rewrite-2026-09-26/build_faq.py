"""Render + verify the /faq/ rewrite. Fails closed (exit 1) on any unverified quote,
mis-parse, or banned claim.

Run from the repo root:
    /Users/theceo/DevSkyy/.venv/bin/python tasks/prelaunch-faq-rewrite-2026-09-26/build_faq.py

Reads policy pages from staging via the public REST API (read-only GET) and product
facts through skyyrose.core.product.get_product. Writes nothing outside this directory.
"""

from __future__ import annotations

import html
import json
import re
import sys
import time
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(REPO))

from faq_content import (  # noqa: E402
    FOUNDER_DECISIONS,
    INTRO,
    OUT_OF_SCOPE_FINDINGS,
    POLICY_CONTRADICTIONS,
    REMOVED_CLAIMS,
    SECTIONS,
)

from skyyrose.core.product import get_product  # noqa: E402

STAGING = "https://staging-7e48-skyyrose.wpcomstaging.com"
PAGE_IDS = {"9712": 9712, "10146": 10146, "10406": 10406, "10409": 10409, "9718": 9718}
ADULT_DEFAULT = "S|M|L|XL|2XL|3XL"
BANNED = [
    (r"\b\d+\s*(?:hours?|hrs?)\b", "hour count"),
    (r"respond|reply|replies|get back to you|within 1 business day", "response-time wording"),
    (r"worldwide", "worldwide"),
    (r"XS\s*(?:through|to|[-–—])\s*3XL", "XS through 3XL"),
    (r"4\s*[-–—]\s*6\s*weeks|four to six weeks", "4–6 weeks"),
    (r"fair[\s-]?trade|sustainab|responsibly|ethical", "sourcing claim"),
    (r"gender[\s-]?neutral|unisex", "gender-neutral claim"),
    (r"worldwide|every country", "worldwide"),
    (r"@skyyrose\.co", "hard-coded email"),
    (r"click here", "non-descriptive link text"),
]
# Fulfillment timelines that are allowed to contain "hour" (not reply promises).
ALLOWED_HOUR_CONTEXT = [r"48 hours before its estimated ship date"]
AUTHORITATIVE_ROUTES = {
    "/shipping-returns/",
    "/refund-policy/",
    "/returns-exchanges/",
    "/size-guide/",
    "/contact/",
    "/pre-order/",
    "/terms-of-service/",
}
# Registry-sourced answer with no authoritative page among the routes above.
LINK_EXEMPT = {"What collections does SkyyRose make?"}
MAX_SENTENCES = 3
EXPECTED_SIZE_EXCEPTIONS = {"sg-002", "sg-005", "lh-005", "sg-007"}
EXPECTED_COLLECTIONS = {"signature", "black-rose", "love-hurts", "kids-capsule"}


# ---------------------------------------------------------------- source text
def norm(text: str) -> str:
    text = re.sub(r"<(script|style)[^>]*>.*?</\1>", " ", text, flags=re.S)
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"\s+", " ", html.unescape(text)).strip()
    # A closing inline tag (</strong>, </a>) becomes a space before punctuation.
    return re.sub(r" ([.,;:)])", r"\1", text)


def fetch_page(pid: int) -> str:
    url = f"{STAGING}/?rest_route=/wp/v2/pages/{pid}&_fields=id,content&cb={int(time.time())}"
    with urllib.request.urlopen(url, timeout=30) as resp:
        return norm(json.load(resp)["content"]["rendered"])


def registry_aggregates() -> dict[str, str]:
    registry = json.loads((REPO / "logo-registry.json").read_text())
    sizes, collections = {}, set()
    for sku in sorted(registry["products"]):
        rec = get_product(sku)
        if rec["catalog"].get("published") != "1":
            continue
        sizes.setdefault(rec["catalog"]["sizes"], []).append(sku)
        collections.add(rec["collection"])
    adult = [s for k, v in sizes.items() for s in v if k not in ("2T|3T|4T|5|6|7", "One Size")]
    default = sizes.get(ADULT_DEFAULT, [])
    summary = (
        f"{len(default)} of {len(adult)} published adult sized SKUs = {ADULT_DEFAULT}; "
        + "; ".join(f"{k}: {', '.join(v)}" for k, v in sorted(sizes.items()) if k != ADULT_DEFAULT)
    )
    return {"SIZES_AGGREGATE": summary, "COLLECTIONS_AGGREGATE": ", ".join(sorted(collections))}


def registry_invariants() -> list[str]:
    """The sizing and collection answers restate these sets; fail if the registry moves."""
    registry = json.loads((REPO / "logo-registry.json").read_text())
    published = {
        sku: get_product(sku)
        for sku in registry["products"]
        if get_product(sku)["catalog"].get("published") == "1"
    }
    adult = {s: r for s, r in published.items() if r["collection"] != "kids-capsule"}
    exceptions = {s for s, r in adult.items() if r["catalog"]["sizes"] != ADULT_DEFAULT}
    default = len(adult) - len(exceptions)
    kids = {s: r["catalog"]["sizes"] for s, r in published.items() if s not in adult}
    collections = {r["collection"] for r in published.values()}
    errors = []
    if exceptions != EXPECTED_SIZE_EXCEPTIONS:
        errors.append(f"adult size exceptions changed: {sorted(exceptions)}")
    if default * 2 <= len(adult):
        errors.append(f"S–3XL is no longer most adult pieces ({default}/{len(adult)})")
    if kids != {"kids-001": "2T|3T|4T|5|6|7", "kids-002": "2T|3T|4T|5|6|7"}:
        errors.append(f"kids sizes changed: {kids}")
    if collections != EXPECTED_COLLECTIONS:
        errors.append(f"published collections changed: {sorted(collections)}")
    return errors


def registry_field(ref: str) -> str:
    match = re.fullmatch(r"products\[([a-z0-9-]+)\]\.catalog\.(\w+)", ref)
    if not match:
        raise ValueError(f"unparseable registry ref: {ref}")
    return str(get_product(match.group(1))["catalog"][match.group(2)])


def verify_sources(pages: dict[str, str], aggregates: dict[str, str]) -> list[str]:
    errors = []
    brand = (REPO / "CLAUDE.md").read_text()
    for _, items in SECTIONS:
        for question, _, sources in items:
            for source in sources:
                kind, ref = source["kind"], source["ref"]
                if kind == "policy_page":
                    if norm(source["quote"]) not in pages[ref.split()[0]]:
                        errors.append(f"[{question}] quote not on page {ref}: {source['quote']!r}")
                elif kind == "registry":
                    if source["quote"] in aggregates:
                        source["quote"] = aggregates[source["quote"]]
                        continue
                    actual = registry_field(ref)
                    if actual != source["quote"]:
                        errors.append(
                            f"[{question}] {ref} = {actual!r}, quoted {source['quote']!r}"
                        )
                elif kind == "brand_canon":
                    if source["quote"] not in brand:
                        errors.append(f"[{question}] brand quote missing: {source['quote']!r}")
                else:
                    errors.append(f"[{question}] unknown source kind {kind}")
    return errors


# ---------------------------------------------------------------- rendering
def block_markup() -> str:
    parts = [f"<!-- wp:paragraph -->\n<p>{INTRO}</p>\n<!-- /wp:paragraph -->"]
    for category, items in SECTIONS:
        parts.append(
            "<!-- wp:heading -->\n"
            f'<h2 class="wp-block-heading">{category}</h2>\n'
            "<!-- /wp:heading -->"
        )
        for question, answer, _ in items:
            parts.append(
                "<!-- wp:details -->\n"
                f'<details class="wp-block-details"><summary>{question}</summary>'
                f"<!-- wp:paragraph -->\n<p>{answer}</p>\n<!-- /wp:paragraph --></details>\n"
                "<!-- /wp:details -->"
            )
    return "\n\n".join(parts) + "\n"


def strip_tags(text: str) -> str:
    return re.sub(r"<[^>]*>", "", re.sub(r"<!--.*?-->", "", text, flags=re.S))


def seo_excerpt(text: str, length: int) -> str:
    """Mirror of skyyrose2_seo_excerpt(): wp_strip_all_tags + whitespace collapse + mb cut."""
    text = re.sub(r"\s+", " ", strip_tags(text)).strip()
    return text[: length - 1].rstrip() + "…" if len(text) > length else text


def parse_like_theme(content: str) -> tuple[str, list[dict[str, str]]]:
    details = re.findall(
        r"<details[^>]*>\s*<summary[^>]*>(.*?)</summary>(.*?)</details>", content, re.S | re.I
    )
    branch, matches = "details", details
    if not details:
        branch = "h2"
        matches = re.findall(
            r"<h2[^>]*>(.*?)</h2>\s*(?:<!--[^>]*-->\s*)*<p[^>]*>(.*?)</p>", content, re.S | re.I
        )
    entries = []
    for q, a in matches:
        q, a = seo_excerpt(q, 240), seo_excerpt(a, 1000)
        if q and a:
            entries.append({"question": q, "answer": a})
    return branch, entries


def banned_hits(text: str) -> list[str]:
    for allowed in ALLOWED_HOUR_CONTEXT:
        text = re.sub(allowed, "", text)
    return [label for pattern, label in BANNED if re.search(pattern, text, re.I)]


# ---------------------------------------------------------------- review page
def esc(text: str) -> str:
    return html.escape(text, quote=True)


def review_html(entries: list[dict]) -> str:
    rows = []
    n = 0
    for category, items in SECTIONS:
        rows.append(f"<h2>{esc(category)}</h2>")
        for question, answer, sources in items:
            n += 1
            srcs = "".join(
                f"<li><span class=k>{esc(s['kind'])}</span> <code>{esc(s['ref'])}</code>"
                f"<blockquote>{esc(s['quote'])}</blockquote></li>"
                for s in sources
            )
            rows.append(
                f"<article><h3>{n}. {esc(question)}</h3><div class=a>{answer}</div>"
                f"<details><summary>Sources ({len(sources)})</summary><ul>{srcs}</ul></details></article>"
            )
    fd = "".join(
        f"<li><strong>{esc(d['id'])} · {esc(d['topic'])}</strong><p>{esc(d['detail'])}</p></li>"
        for d in FOUNDER_DECISIONS
    )
    rc = "".join(
        f"<li><s>{esc(r['old'])}</s><p>{esc(r['reason'])}</p></li>" for r in REMOVED_CLAIMS
    )
    pc = "".join(f"<li>{esc(c)}</li>" for c in POLICY_CONTRADICTIONS)
    oos = "".join(f"<li>{esc(c)}</li>" for c in OUT_OF_SCOPE_FINDINGS)
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>FAQ Rewrite Review</title>
<style>
:root{{--bg:#fafaf8;--fg:#141414;--muted:#555;--line:#ddd;--accent:#8a4a54;--card:#fff}}
@media (prefers-color-scheme:dark){{:root:not([data-theme="light"]){{--bg:#0a0a0a;--fg:#eee;--muted:#b3b3b3;--line:#2a2a2a;--accent:#d49aa3;--card:#141414}}}}
:root[data-theme="dark"]{{--bg:#0a0a0a;--fg:#eee;--muted:#b3b3b3;--line:#2a2a2a;--accent:#d49aa3;--card:#141414}}
body{{background:var(--bg);color:var(--fg);font:16px/1.55 system-ui,sans-serif;margin:0;padding:24px 16px}}
main{{max-width:860px;margin:auto}} h1{{margin:0 0 4px}} h2{{margin-top:40px;border-bottom:1px solid var(--line);padding-bottom:6px}}
article{{background:var(--card);border:1px solid var(--line);border-radius:8px;padding:14px 16px;margin:12px 0}}
article h3{{margin:0 0 6px;font-size:1.05rem}} .a a{{color:var(--accent)}} .meta{{color:var(--muted)}}
blockquote{{margin:6px 0 10px;padding-left:10px;border-left:3px solid var(--accent);color:var(--muted);overflow-wrap:anywhere}}
code{{font-size:.85em;overflow-wrap:anywhere}} .k{{font-size:.75rem;text-transform:uppercase;letter-spacing:.06em;color:var(--accent)}}
ul{{padding-left:20px}} s{{color:var(--muted)}}
</style></head><body><main>
<h1>FAQ rewrite review: page 9711 (/faq/)</h1>
<p class=meta>Generated 2026-09-26 by build_faq.py. {len(entries)} Q/A entries, each parsed by a mirror of skyyrose2_seo_faq_entries(). Every quote below was re-checked against staging REST content or get_product() when this page was built.</p>
<p class=meta>Intro paragraph: {INTRO}</p>
{"".join(rows)}
<h2>Founder decisions</h2><ul>{fd}</ul>
<h2>Removed claims</h2><ul>{rc}</ul>
<h2>Contradictions between published sources (reported, not resolved)</h2><ul>{pc}</ul>
<h2>Out-of-scope findings</h2><ul>{oos}</ul>
</main></body></html>
"""


def main() -> int:
    pages = {key: fetch_page(pid) for key, pid in PAGE_IDS.items()}
    aggregates = registry_aggregates()
    errors = verify_sources(pages, aggregates)
    invariant_errors = registry_invariants()
    print(
        f"registry invariants (size exceptions, 'most' S–3XL, kids, collections): "
        f"{'PASS' if not invariant_errors else invariant_errors}"
    )
    errors += invariant_errors

    for _, items in SECTIONS:
        for question, answer, _ in items:
            routes = set(re.findall(r'href="([^"]+)"', answer))
            if question not in LINK_EXEMPT and not routes & AUTHORITATIVE_ROUTES:
                errors.append(f"no authoritative link: {question}")
            if routes - AUTHORITATIVE_ROUTES:
                errors.append(f"unapproved link in {question}: {routes - AUTHORITATIVE_ROUTES}")
            count = len(re.findall(r"[.?!](?:\s|$)", seo_excerpt(answer, 10_000)))
            if count > MAX_SENTENCES:
                errors.append(f"{count} sentences (max {MAX_SENTENCES}): {question}")
    print(
        f"link + length checks: every answer links an authoritative route "
        f"(exempt: {sorted(LINK_EXEMPT)}); max {MAX_SENTENCES} sentences"
    )

    markup = block_markup()
    branch, entries = parse_like_theme(markup)
    h2_matches = re.findall(
        r"<h2[^>]*>(.*?)</h2>\s*(?:<!--[^>]*-->\s*)*<p[^>]*>(.*?)</p>", markup, re.S | re.I
    )
    expected = [(q, a) for _, items in SECTIONS for q, a, _ in items]

    print(f"theme branch used: {branch}")
    print(f"parsed entries: {len(entries)} (expected {len(expected)})")
    if len(entries) != len(expected):
        errors.append("entry count mismatch")
    for i, (entry, (q, a)) in enumerate(zip(entries, expected), 1):
        want_a = seo_excerpt(a, 10_000)
        if entry["question"] != q or entry["answer"] != want_a:
            errors.append(f"mis-parse at #{i}: {entry}")
        if entry["answer"].endswith("…") or entry["question"].endswith("…"):
            errors.append(f"truncated at #{i}")
        if "<" in entry["answer"] or "-->" in entry["answer"]:
            errors.append(f"markup leaked at #{i}")
        print(f"  {i:2d}. Q: {entry['question']}")
    categories = [c for c, _ in SECTIONS]
    leaked = [e for e in entries if e["question"] in categories]
    print(f"category headings parsed as questions: {len(leaked)}")
    print(
        f"h2 fallback regex (negative test) matches: {len(h2_matches)} "
        "(branch not reached because details matched)"
    )
    if leaked:
        errors.append("category heading parsed as a question")

    print("banned-claim scan (questions + answers + intro):")
    scan_targets = [("intro", strip_tags(INTRO))] + [
        (e["question"], e["question"] + " " + e["answer"]) for e in entries
    ]
    total_hits = 0
    for label, text in scan_targets:
        hits = banned_hits(text)
        total_hits += len(hits)
        if hits:
            errors.append(f"banned claim in {label!r}: {hits}")
            print(f"  HIT {label}: {hits}")
    hour_uses = [e["question"] for e in entries if re.search(r"hour", e["answer"], re.I)]
    print(f"  hits: {total_hits}; 'hour' allowed only as fulfillment timeline in: {hour_uses}")
    print(
        f"source quotes verified: {sum(len(s) for _, it in SECTIONS for *_, s in it)}; "
        f"source errors: {len([e for e in errors if 'quote' in e or 'registry' in e])}"
    )

    if errors:
        print("FAILED:")
        for err in errors:
            print("  -", err)
        return 1

    (HERE / "faq-block-markup.html").write_text(markup)
    evidence = {
        "page_id": 9711,
        "route": "/faq/",
        "generated": "2026-09-26",
        "parse_check": {"branch": branch, "entries": len(entries), "mis_parses": 0},
        "entries": [
            {
                "category": category,
                "question": q,
                "answer_text": seo_excerpt(a, 10_000),
                "answer_html": a,
                "sources": sources,
            }
            for category, items in SECTIONS
            for q, a, sources in items
        ],
        "founder_decisions": FOUNDER_DECISIONS,
        "removed_claims": REMOVED_CLAIMS,
        "policy_contradictions": POLICY_CONTRADICTIONS,
        "out_of_scope_findings": OUT_OF_SCOPE_FINDINGS,
    }
    (HERE / "faq-evidence.json").write_text(
        json.dumps(evidence, indent=2, ensure_ascii=False) + "\n"
    )
    (HERE / "faq-review.html").write_text(review_html(entries))
    print("PASS — wrote faq-block-markup.html, faq-evidence.json, faq-review.html")
    return 0


if __name__ == "__main__":
    sys.exit(main())
