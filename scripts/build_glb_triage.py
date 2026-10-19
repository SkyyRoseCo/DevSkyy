#!/usr/bin/env python3
"""Build the founder's GLB triage page for the web-v2 product models.

One section per ``<sku>.glb`` in the web directory: the product name from the
registry, the REAL founder photograph from ``assets/products/source-photos/``
at full resolution (the only valid QC reference — CLAUDE.md §2 "Imagery QC");
the current site image as a clearly labelled SECONDARY thumbnail (generated,
never the comparison basis); and the same "View in 3D" button + dialog the
PDP ships (``assets/js/product-3d-viewer.js`` + vendored three r170), so what
the founder judges is the production code path. Keep / Reject + note per SKU;
"Export verdicts" downloads ``glb_verdicts.json`` including which reference
file (and precedence rule) each verdict was judged against.

Reference precedence, by ``<sku>-`` filename prefix under source-photos:
``front`` (a real front photo) > ``techflat`` > ``variant`` (any other real
photo). A SKU with no source photo gets a blocking "cannot QC" notice and NO
keep/reject controls — a Keep with nothing to compare against is the
lenient-QC defect this page exists to prevent.

Paths are root-absolute so the page works served from the repo root::

    python3 -m http.server 8765        # from /Users/theceo/DevSkyy
    open http://127.0.0.1:8765/renders/3d/qc/glb-triage.html

Usage::

    python scripts/build_glb_triage.py [--web-dir renders/3d/web-v2] [--out renders/3d/qc/glb-triage.html]
"""

from __future__ import annotations

import argparse
import hashlib
import html
import json
import sys
from datetime import UTC, datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from skyyrose.core import sot_images  # noqa: E402
from skyyrose.core.product_registry import load_registry  # noqa: E402

THEME_REL = "wordpress-theme/skyyrose-flagship"
SOURCE_PHOTOS_REL = "assets/products/source-photos"
LIB_BASE = f"/{THEME_REL}/assets/js/lib/three-0.170.0/"
VIEWER_JS = f"/{THEME_REL}/assets/js/product-3d-viewer.js"
CSS_FILES = (
    f"/{THEME_REL}/assets/css/design-tokens.css",
    f"/{THEME_REL}/assets/css/single-product.css",
)
PHOTO_SUFFIXES = {".jpg", ".jpeg", ".png", ".webp"}
NO_REFERENCE_NOTICE = (
    "No real reference on file — cannot QC. Keep / Reject is disabled for this model."
)
# Founder-only question: the file is prefixed lh-002 (it resolves to lh-002 by
# rule) but its name reads like lh-006's garment. Never used as lh-006's reference.
OPEN_QUESTIONS = {
    "lh-006": (
        "Open question for the founder: assets/products/source-photos/love-hurts/"
        "lh-002-joggers-white.jpeg exists — only you can say whether it depicts this "
        "product. It is NOT shown here as the reference."
    ),
}


def sha256_of(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _rule_for(name: str) -> str | None:
    """Precedence bucket for a source-photo filename, or None if it is a back view."""
    lower = name.lower()
    if "techflat" in lower:
        return "techflat"
    if "back" in lower:
        return None
    if "front" in lower:
        return "front"
    return "variant"


def resolve_reference(sku: str, source_dir: Path) -> tuple[Path | None, str]:
    """Best real photo for ``sku`` under ``source_dir`` and the rule that matched.

    Candidates are files named ``<sku>-*`` (the source-photos naming contract).
    ``front`` beats ``techflat`` beats ``variant``; a pure back view is used only
    when nothing else exists (rule ``back``). Ties break on sorted filename so
    the choice is deterministic.
    """
    if not source_dir.is_dir():
        return None, "none"
    prefix = f"{sku}-"
    candidates = sorted(
        p
        for p in source_dir.rglob(f"{prefix}*")
        if p.is_file() and p.suffix.lower() in PHOTO_SUFFIXES
    )
    if not candidates:
        return None, "none"

    buckets: dict[str, list[Path]] = {"front": [], "techflat": [], "variant": [], "back": []}
    for path in candidates:
        buckets[_rule_for(path.name) or "back"].append(path)
    # Within techflats, a "...-front" techflat beats the composite/back sheet.
    buckets["techflat"].sort(
        key=lambda p: ("front" not in p.name.lower(), "back" in p.name.lower(), p.name)
    )
    for rule in ("front", "techflat", "variant", "back"):
        if buckets[rule]:
            return buckets[rule][0], rule
    return None, "none"


def collect_entries(web_dir: Path, repo_root: Path = REPO_ROOT) -> list[dict]:
    """One record per GLB: registry name, real reference (or none), site image, sha256.

    Fails closed: a missing web directory or a directory without GLBs raises —
    an empty triage page must never be mistaken for "all models reviewed".
    """
    if not web_dir.is_dir():
        raise FileNotFoundError(f"web GLB directory not found: {web_dir}")
    glbs = sorted(web_dir.glob("*.glb"))
    if not glbs:
        raise FileNotFoundError(f"no .glb files in {web_dir}")

    products = load_registry()["products"]
    source_dir = repo_root / SOURCE_PHOTOS_REL
    entries: list[dict] = []
    for glb in glbs:
        sku = glb.stem
        product = products.get(sku)
        name = product["catalog"].get("name", "") if product else ""

        ref_path, ref_rule = resolve_reference(sku, source_dir)

        site_rel = sot_images.resolve_image(sku, "front") if product else None
        site_path = repo_root / THEME_REL / site_rel if site_rel else None
        site_exists = bool(site_path and site_path.is_file())

        entries.append(
            {
                "sku": sku,
                "name": name,
                "in_registry": product is not None,
                "glb_path": glb.relative_to(repo_root).as_posix(),
                "glb_bytes": glb.stat().st_size,
                "glb_sha256": sha256_of(glb),
                "reference_file": ref_path.relative_to(repo_root).as_posix() if ref_path else None,
                "reference_rule": ref_rule,
                "site_image": f"/{THEME_REL}/{site_rel}" if site_exists else None,
                "open_question": OPEN_QUESTIONS.get(sku),
            }
        )
    return entries


def coverage_table(entries: list[dict]) -> str:
    """Plain-text table of which reference rule matched per SKU (printed by main)."""
    lines = [f"{'sku':<10}{'rule':<10}reference"]
    for e in entries:
        lines.append(f"{e['sku']:<10}{e['reference_rule']:<10}{e['reference_file'] or '—'}")
    counts: dict[str, int] = {}
    for e in entries:
        counts[e["reference_rule"]] = counts.get(e["reference_rule"], 0) + 1
    lines.append("totals: " + ", ".join(f"{k}={v}" for k, v in sorted(counts.items())))
    return "\n".join(lines)


def _reference_block(entry: dict, sku: str, name: str) -> tuple[str, str]:
    """The reference figure and its verdict controls — or a blocking notice and no controls."""
    if entry["reference_file"] is None:
        question = entry.get("open_question")
        question_html = f"<p>{html.escape(question)}</p>" if question else ""
        notice = (
            f'<div class="triage-ref triage-ref--missing" role="alert">'
            f"<p><strong>{html.escape(NO_REFERENCE_NOTICE)}</strong></p>{question_html}</div>"
        )
        blocked = (
            '\n      <p class="triage-blocked">QC blocked — no real reference. Add a founder photo '
            f"under assets/products/source-photos/ named <code>{sku}-…</code> and regenerate.</p>"
        )
        return notice, blocked

    ref_url = html.escape("/" + entry["reference_file"])
    ref_name = html.escape(Path(entry["reference_file"]).name)
    rule = html.escape(entry["reference_rule"])
    figure = (
        f'<figure class="triage-ref triage-ref--{rule}">'
        f'<a href="{ref_url}" target="_blank" rel="noopener" title="Open raw file">'
        f'<img src="{ref_url}" alt="Founder photo for {name or sku}: {ref_name}" loading="lazy"></a>'
        f"<figcaption><strong>REAL REFERENCE</strong> · rule: <code>{rule}</code> · "
        f"<code>{ref_name}</code></figcaption>"
        f"</figure>"
    )
    controls = f"""
      <fieldset class="triage-verdict">
        <legend>Verdict (judged against {ref_name})</legend>
        <label><input type="radio" name="verdict-{sku}" value="keep"> Keep</label>
        <label><input type="radio" name="verdict-{sku}" value="reject"> Reject</label>
        <textarea name="note-{sku}" rows="3" placeholder="Note (what is wrong, what to fix)"></textarea>
      </fieldset>"""
    return figure, controls


def _site_thumbnail(entry: dict) -> str:
    """The live-site image, labelled as generated so it is never mistaken for the reference."""
    if not entry["site_image"]:
        return ""
    return (
        f'<figure class="triage-site"><img src="{html.escape(entry["site_image"])}" alt="" '
        f'loading="lazy"><figcaption>Current site image — generated, not the reference'
        f"</figcaption></figure>"
    )


def _section(entry: dict) -> str:
    sku = html.escape(entry["sku"])
    # `name` is escaped for attribute use; `heading` keeps the RAW name because the
    # f-string below escapes it again — double-escaping printed literal &#x27; in
    # 7 of 33 product names ("The Bridge Series 'Stay Golden'", "Mint & Lavender").
    raw_name = entry["name"] or ""
    name = html.escape(raw_name)
    heading = raw_name if raw_name else f"UNKNOWN SKU {entry['sku']} — not in the registry"
    model = html.escape("/" + entry["glb_path"])
    has_reference = entry["reference_file"] is not None
    reference, controls = _reference_block(entry, sku, name)
    site = _site_thumbnail(entry)

    return f"""
<section class="triage-sku{"" if has_reference else " triage-sku--blocked"}" id="sku-{sku}" data-sku="{sku}" data-has-reference="{"1" if has_reference else "0"}">
  <header class="triage-sku__head">
    <h2>{html.escape(heading)}</h2>
    <p class="triage-sku__meta">{sku} · {entry["glb_bytes"] / 1e6:.2f} MB · sha256 {html.escape(entry["glb_sha256"][:16])}…</p>
  </header>
  <div class="triage-sku__body">
    {reference}
    <div class="triage-viewer">
      <div class="product-3d-viewer"><button type="button" class="button view-3d-model" data-model="{model}" data-product-name="{name or sku}">View in 3D</button></div>{controls}
      {site}
    </div>
  </div>
</section>"""


# Page chrome for the triage sheet. Kept out of render_page() so that function stays
# readable; the viewer itself is styled by the theme CSS linked in CSS_FILES.
_PAGE_CSS = """
  body {{ margin: 0; background: #0A0A0A; color: #FFF; font-family: 'Hanken Grotesk', 'Inter', sans-serif; }}
  .triage-top {{ position: sticky; top: 0; z-index: 5; display: flex; align-items: center; justify-content: space-between; gap: 16px; padding: 14px 24px; background: rgba(10,10,10,0.95); border-bottom: 1px solid rgba(183,110,121,0.4); }}
  .triage-top h1 {{ margin: 0; font-size: 14px; letter-spacing: 0.16em; text-transform: uppercase; }}
  .triage-top p {{ margin: 0; font-size: 12px; color: #B3B3B3; }}
  #export-verdicts {{ min-height: 44px; padding: 0 20px; border-radius: 999px; border: 1px solid #B76E79; background: #B76E79; color: #000; font: 600 12px/1 inherit; letter-spacing: 0.16em; text-transform: uppercase; cursor: pointer; }}
  .triage-sku {{ padding: 32px 24px; border-bottom: 1px solid rgba(255,255,255,0.08); }}
  .triage-sku--blocked {{ background: rgba(220,20,60,0.06); }}
  .triage-sku__head h2 {{ margin: 0 0 4px; font-size: 22px; font-weight: 600; }}
  .triage-sku__meta {{ margin: 0 0 16px; font-size: 12px; color: #B3B3B3; letter-spacing: 0.06em; }}
  .triage-sku__body {{ display: grid; grid-template-columns: minmax(0, 3fr) minmax(300px, 2fr); gap: 32px; align-items: start; }}
  .triage-ref {{ margin: 0; }}
  .triage-ref img {{ display: block; width: 100%; height: auto; border: 2px solid #B76E79; background: #111; }}
  .triage-ref figcaption {{ margin-top: 8px; font-size: 12px; color: #B3B3B3; letter-spacing: 0.06em; }}
  .triage-ref figcaption code {{ color: #FFF; }}
  .triage-ref--techflat img, .triage-ref--variant img, .triage-ref--back img {{ border-color: #D4AF37; }}
  .triage-ref--missing {{ padding: 24px; border: 2px dashed #DC143C; color: #FFF; font-size: 15px; line-height: 1.5; }}
  .triage-ref--missing p {{ margin: 0 0 12px; }}
  .triage-verdict {{ margin: 20px 0 0; padding: 16px; border: 1px solid rgba(255,255,255,0.12); border-radius: 12px; }}
  .triage-verdict legend {{ padding: 0 6px; font-size: 12px; letter-spacing: 0.1em; text-transform: uppercase; color: #B3B3B3; }}
  .triage-verdict label {{ display: inline-flex; align-items: center; gap: 6px; margin-right: 18px; font-size: 14px; }}
  .triage-verdict textarea {{ display: block; width: 100%; margin-top: 12px; padding: 10px; box-sizing: border-box; background: #111; color: #FFF; border: 1px solid rgba(255,255,255,0.12); border-radius: 8px; font: 14px/1.4 inherit; }}
  .triage-blocked {{ margin: 20px 0 0; padding: 14px 16px; border: 1px solid #DC143C; border-radius: 12px; font-size: 14px; }}
  .triage-site {{ margin: 24px 0 0; max-width: 180px; }}
  .triage-site img {{ display: block; width: 100%; height: auto; border: 1px solid rgba(255,255,255,0.12); opacity: 0.8; }}
  .triage-site figcaption {{ margin-top: 6px; font-size: 11px; color: #B3B3B3; letter-spacing: 0.06em; text-transform: uppercase; }}
  .triage-sku.is-keep {{ box-shadow: inset 4px 0 0 #B76E79; }}
  .triage-sku.is-reject {{ box-shadow: inset 4px 0 0 #DC143C; }}
  @media (max-width: 900px) {{ .triage-sku__body {{ grid-template-columns: 1fr; }} }}
  /* Triage-only: dock the (unchanged) PDP viewer dialog to the right so the
     founder photo stays visible beside the live 3D render, and keep the page
     scrollable under it (the viewer's inline overflow lock loses to !important).
     Clicking outside the docked panel closes it, as on the PDP. */
  body {{ overflow: auto !important; }}
  .sr-3d-dialog {{ position: fixed; inset: 0 0 0 auto; margin: 0; width: min(55vw, 960px); height: 100dvh; max-height: none; border-radius: 0; border-width: 0 0 0 1px; }}
  .sr-3d-dialog::backdrop {{ background: transparent; backdrop-filter: none; -webkit-backdrop-filter: none; }}
  @media (min-width: 901px) {{ .triage-sku__body {{ grid-template-columns: minmax(0, 42vw) minmax(280px, 1fr); }} }}
"""


def _export_payload(entries: list[dict]) -> str:
    """The rows the page's export button writes to glb_verdicts.json."""
    keys = ("sku", "name", "glb_path", "glb_sha256", "reference_file", "reference_rule")
    return json.dumps([{k: e[k] for k in keys} for e in entries], ensure_ascii=False)


# The triage sheet's verdict wiring (localStorage + export). A plain string, not an
# f-string fragment, so the JS braces stay readable instead of doubled.
_PAGE_SCRIPT = """
(function () {
  'use strict';
  var entries = JSON.parse(document.getElementById('triage-data').textContent);
  var STORE = 'skyyrose-glb-triage-verdicts';
  var state = {};
  try { state = JSON.parse(localStorage.getItem(STORE) || '{}'); } catch (err) { state = {}; }

  function save() { localStorage.setItem(STORE, JSON.stringify(state)); }
  function paint(section, sku) {
    var v = state[sku] || {};
    section.classList.toggle('is-keep', v.verdict === 'keep');
    section.classList.toggle('is-reject', v.verdict === 'reject');
  }

  entries.forEach(function (entry) {
    var section = document.getElementById('sku-' + entry.sku);
    if (!entry.reference_file) { return; }  // blocked: no controls, nothing to wire
    var saved = state[entry.sku] || {};
    var radios = section.querySelectorAll('input[type="radio"]');
    var note = section.querySelector('textarea');
    radios.forEach(function (radio) {
      if (saved.verdict === radio.value) { radio.checked = true; }
      radio.addEventListener('change', function () {
        state[entry.sku] = state[entry.sku] || {};
        state[entry.sku].verdict = radio.value;
        state[entry.sku].reviewed_at = new Date().toISOString();
        save(); paint(section, entry.sku);
      });
    });
    if (saved.note) { note.value = saved.note; }
    note.addEventListener('input', function () {
      state[entry.sku] = state[entry.sku] || {};
      state[entry.sku].note = note.value;
      save();
    });
    paint(section, entry.sku);
  });

  document.getElementById('export-verdicts').addEventListener('click', function () {
    var rows = entries.map(function (entry) {
      var v = entry.reference_file ? (state[entry.sku] || {}) : {};
      return {
        sku: entry.sku, name: entry.name,
        verdict: v.verdict || null, note: v.note || '',
        reviewed_at: v.reviewed_at || null,
        glb_path: entry.glb_path, glb_sha256: entry.glb_sha256,
        reference_file: entry.reference_file, reference_rule: entry.reference_rule,
        qc_blocked: !entry.reference_file
      };
    });
    var blob = new Blob([JSON.stringify(rows, null, 2)], { type: 'application/json' });
    var url = URL.createObjectURL(blob);
    var a = document.createElement('a');
    a.href = url; a.download = 'glb_verdicts.json';
    document.body.appendChild(a); a.click(); a.remove();
    setTimeout(function () { URL.revokeObjectURL(url); }, 1000);
  });
})();
"""


def render_page(entries: list[dict], generated_at: str) -> str:
    sections = "\n".join(_section(e) for e in entries)
    data = _export_payload(entries)
    config = json.dumps({"libBase": LIB_BASE, "i18n": {}})
    css_links = "\n".join(f'<link rel="stylesheet" href="{c}">' for c in CSS_FILES)
    blocked = sum(1 for e in entries if e["reference_file"] is None)
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>GLB triage — web-v2 product models</title>
{css_links}
<style>{_PAGE_CSS}</style>
</head>
<body class="single-product">
<header class="triage-top">
  <div><h1>GLB triage — web-v2</h1><p>{len(entries)} models · {blocked} blocked (no real reference) · generated {html.escape(generated_at)} · verdicts persist in this browser until exported</p></div>
  <button type="button" id="export-verdicts">Export verdicts</button>
</header>
<main class="sr-product" style="padding-top:0">
{sections}
</main>
<script id="triage-data" type="application/json">{data}</script>
<script>window.skyyRoseProduct3d = {config};</script>
<script defer src="{VIEWER_JS}"></script>
<script>{_PAGE_SCRIPT}</script>
</body>
</html>
"""


def build(web_dir: Path, out: Path, repo_root: Path = REPO_ROOT) -> list[dict]:
    entries = collect_entries(web_dir, repo_root)
    generated_at = datetime.now(UTC).isoformat(timespec="seconds")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(render_page(entries, generated_at), encoding="utf-8")
    return entries


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--web-dir", type=Path, default=REPO_ROOT / "renders/3d/web-v2")
    parser.add_argument("--out", type=Path, default=REPO_ROOT / "renders/3d/qc/glb-triage.html")
    args = parser.parse_args(argv)

    entries = build(args.web_dir, args.out)
    print(f"wrote {args.out} — {len(entries)} models")
    print(coverage_table(entries))
    blocked = [e["sku"] for e in entries if e["reference_file"] is None]
    unknown = [e["sku"] for e in entries if not e["in_registry"]]
    if blocked:
        print(f"QC BLOCKED (no real reference, no controls): {', '.join(blocked)}")
    if unknown:
        print(f"NOT in product registry: {', '.join(unknown)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
