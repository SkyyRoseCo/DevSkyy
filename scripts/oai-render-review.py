#!/usr/bin/env python3
"""Founder review environment for OAI product renders.

Serves an HTML review board: every render gets a hallucination checkbox,
an approve checkbox, and a comment box. Annotations persist to
renders/oai/_review/review-state.json on every change (debounced autosave).

Render PNGs are served live from renders/oai/<slug>/*.png when present.
Renders listed in the roster but missing on disk (e.g. the deleted
2026-06-08 batch) show a placeholder row so they can still be annotated
from the recovered evidence sheets displayed at the top of the page.

Usage:
    python3 scripts/oai-render-review.py            # serve on 127.0.0.1:8944
    python3 scripts/oai-render-review.py --port N
No third-party dependencies.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import tempfile
from datetime import UTC, datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
OUTPUT_DIR = PROJECT_ROOT / "renders" / "oai"
REVIEW_DIR = OUTPUT_DIR / "_review"
EVIDENCE_DIR = OUTPUT_DIR / "_evidence"
STATE_PATH = REVIEW_DIR / "review-state.json"
ROSTER_PATH = REVIEW_DIR / "roster.txt"

SAFE_SEGMENT = re.compile(r"^[a-zA-Z0-9_.-]+$")
VIEW_ORDER = {"ghost.png": 0, "ghost-back.png": 1, "on-model.png": 2}


def load_roster() -> list[str]:
    """Union of renders on disk and renders named in the roster file."""
    entries: set[str] = set()
    if OUTPUT_DIR.is_dir():
        for png in OUTPUT_DIR.glob("*/*.png"):
            if not png.parent.name.startswith("_"):
                entries.add(f"{png.parent.name}/{png.name}")
    if ROSTER_PATH.is_file():
        for line in ROSTER_PATH.read_text().splitlines():
            line = line.strip()
            if line and "/" in line and not line.startswith("_"):
                entries.add(line)
    return sorted(entries, key=lambda e: (e.split("/")[0], VIEW_ORDER.get(e.split("/")[1], 9), e))


def load_state() -> dict:
    if STATE_PATH.is_file():
        try:
            return json.loads(STATE_PATH.read_text())
        except (json.JSONDecodeError, OSError):
            backup = STATE_PATH.with_suffix(".json.corrupt")
            STATE_PATH.rename(backup)
            print(f"warning: corrupt state moved to {backup}", file=sys.stderr)
    return {}


def save_state(state: dict) -> None:
    """Atomic write so a crash mid-save never loses prior annotations."""
    REVIEW_DIR.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=REVIEW_DIR, suffix=".tmp")
    try:
        with os.fdopen(fd, "w") as f:
            json.dump(state, f, indent=2, sort_keys=True)
        os.replace(tmp, STATE_PATH)
    except OSError:
        if os.path.exists(tmp):
            os.unlink(tmp)
        raise


def evidence_files() -> list[str]:
    if not EVIDENCE_DIR.is_dir():
        return []
    return sorted(
        p.name for p in EVIDENCE_DIR.iterdir() if p.suffix.lower() in {".png", ".jpg", ".jpeg"}
    )


def render_page() -> str:
    roster = load_roster()
    products: dict[str, list[dict]] = {}
    for entry in roster:
        slug, fname = entry.split("/", 1)
        exists = (OUTPUT_DIR / slug / fname).is_file()
        products.setdefault(slug, []).append({"entry": entry, "file": fname, "exists": exists})

    sheets = "".join(
        f'<a href="/evidence/{n}" target="_blank"><img src="/evidence/{n}" loading="lazy" alt="{n}"></a>'
        for n in evidence_files()
    )

    sections = []
    for slug, rows in products.items():
        row_html = []
        for r in rows:
            eid = r["entry"]
            thumb = (
                f'<a href="/img/{eid}" target="_blank"><img class="thumb" src="/img/{eid}" loading="lazy"></a>'
                if r["exists"]
                else '<div class="thumb missing">file deleted —<br>judge from sheets above</div>'
            )
            view = r["file"].replace(".png", "")
            row_html.append(f"""
            <div class="row" data-entry="{eid}">
              {thumb}
              <div class="meta">
                <div class="view">{view}</div>
                <label class="flag"><input type="checkbox" class="cb-flag"> Hallucination / reject</label>
                <label class="ok"><input type="checkbox" class="cb-ok"> Approved</label>
                <textarea class="comment" placeholder="What's wrong (or right) with this render…"></textarea>
                <div class="saved" aria-live="polite"></div>
              </div>
            </div>""")
        sections.append(f'<section class="product"><h2>{slug}</h2>{"".join(row_html)}</section>')

    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>SkyyRose — Render Review Board</title>
<style>
  :root {{ --rose:#B76E79; --gold:#D4AF37; --crimson:#DC143C; --bg:#0A0A0A; --card:#141414; --line:#262626; }}
  * {{ box-sizing:border-box; }}
  body {{ background:var(--bg); color:#eee; font:15px/1.5 "Inter",-apple-system,sans-serif; margin:0; padding:24px; }}
  header {{ position:sticky; top:0; z-index:5; background:rgba(10,10,10,.95); backdrop-filter:blur(8px);
            border-bottom:1px solid var(--line); margin:-24px -24px 24px; padding:16px 24px; display:flex;
            align-items:baseline; gap:18px; flex-wrap:wrap; }}
  h1 {{ font-size:19px; margin:0; color:var(--rose); letter-spacing:.04em; }}
  #stats {{ color:#999; font-size:13px; }}
  #stats b {{ color:var(--gold); }} #stats b.bad {{ color:var(--crimson); }}
  .sheets {{ display:flex; gap:10px; overflow-x:auto; padding-bottom:14px; margin-bottom:28px; }}
  .sheets img {{ height:170px; border:1px solid var(--line); border-radius:6px; }}
  .note {{ background:#1c1208; border:1px solid #5c3d12; color:#e8c98a; padding:10px 14px; border-radius:8px;
           margin-bottom:22px; font-size:13.5px; }}
  .product {{ background:var(--card); border:1px solid var(--line); border-radius:10px; padding:16px 18px; margin-bottom:16px; }}
  .product h2 {{ margin:0 0 12px; font-size:15px; color:var(--gold); letter-spacing:.05em; text-transform:uppercase; }}
  .row {{ display:flex; gap:16px; padding:12px 0; border-top:1px solid var(--line); }}
  .thumb {{ width:150px; height:225px; object-fit:cover; border-radius:6px; background:#000; flex:none; }}
  .thumb.missing {{ display:flex; align-items:center; justify-content:center; text-align:center;
                    color:#666; font-size:12px; border:1px dashed #333; }}
  .meta {{ flex:1; min-width:0; }}
  .view {{ font-size:13px; color:#aaa; margin-bottom:8px; font-family:ui-monospace,monospace; }}
  label {{ display:inline-flex; align-items:center; gap:7px; margin-right:20px; cursor:pointer; font-size:14px; }}
  .flag {{ color:var(--crimson); }} .ok {{ color:#7dc77d; }}
  input[type=checkbox] {{ width:17px; height:17px; accent-color:var(--rose); }}
  textarea {{ width:100%; margin-top:10px; min-height:54px; background:#0f0f0f; color:#eee;
              border:1px solid var(--line); border-radius:6px; padding:8px 10px; font:13.5px/1.45 inherit; resize:vertical; }}
  textarea:focus {{ outline:1px solid var(--rose); }}
  .saved {{ font-size:11.5px; color:#5a8f5a; height:14px; margin-top:4px; }}
  .row.is-flagged {{ background:rgba(220,20,60,.06); border-radius:8px; padding-left:8px; padding-right:8px; }}
</style></head><body>
<header><h1>SKYYROSE RENDER REVIEW</h1><div id="stats"></div></header>
<div class="note"><b>Heads up:</b> the 79 PNGs from the 2026-06-08 batch were deleted from disk.
The strips below are recovered review sheets from the QC sweep — click any to open full size.
Mark every render that hallucinated and write what's wrong; annotations save automatically and
drive the prompt fixes before the re-render.</div>
<div class="sheets">{sheets}</div>
{"".join(sections)}
<script>
const state = {{}};
let saveTimer = null;
async function loadState() {{
  const r = await fetch('/api/state'); Object.assign(state, await r.json());
  document.querySelectorAll('.row').forEach(row => {{
    const s = state[row.dataset.entry]; if (!s) return;
    row.querySelector('.cb-flag').checked = !!s.flagged;
    row.querySelector('.cb-ok').checked = !!s.approved;
    row.querySelector('.comment').value = s.comment || '';
    row.classList.toggle('is-flagged', !!s.flagged);
  }});
  updateStats();
}}
function collect(row) {{
  state[row.dataset.entry] = {{
    flagged: row.querySelector('.cb-flag').checked,
    approved: row.querySelector('.cb-ok').checked,
    comment: row.querySelector('.comment').value,
    updated: new Date().toISOString()
  }};
  row.classList.toggle('is-flagged', state[row.dataset.entry].flagged);
}}
function scheduleSave(row) {{
  collect(row); updateStats();
  clearTimeout(saveTimer);
  saveTimer = setTimeout(async () => {{
    const r = await fetch('/api/state', {{method:'POST', headers:{{'Content-Type':'application/json'}},
                                          body: JSON.stringify(state)}});
    const ok = r.ok;
    document.querySelectorAll('.row').forEach(rw => {{
      const el = rw.querySelector('.saved');
      if (state[rw.dataset.entry]) el.textContent = ok ? 'saved' : 'SAVE FAILED — keep this tab open';
    }});
  }}, 500);
}}
function updateStats() {{
  const rows = document.querySelectorAll('.row').length;
  const vals = Object.values(state);
  const flagged = vals.filter(v => v.flagged).length;
  const approved = vals.filter(v => v.approved).length;
  document.getElementById('stats').innerHTML =
    `${{rows}} renders · <b class="bad">${{flagged}} flagged</b> · <b>${{approved}} approved</b> · ${{vals.length}} touched`;
}}
document.querySelectorAll('.row').forEach(row => {{
  row.querySelectorAll('input,textarea').forEach(el =>
    el.addEventListener('input', () => scheduleSave(row)));
}});
loadState();
</script></body></html>"""


class ReviewHandler(BaseHTTPRequestHandler):
    def _send(self, code: int, body: bytes, ctype: str) -> None:
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def _serve_file(self, base: Path, segments: list[str], ctype_map: dict) -> None:
        if not all(SAFE_SEGMENT.match(s) for s in segments):
            self._send(400, b"bad path", "text/plain")
            return
        path = base.joinpath(*segments)
        if not path.is_file():
            self._send(404, b"not found", "text/plain")
            return
        ctype = ctype_map.get(path.suffix.lower(), "application/octet-stream")
        self._send(200, path.read_bytes(), ctype)

    def do_GET(self) -> None:  # noqa: N802 - http.server API
        img_types = {".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg"}
        if self.path == "/" or self.path.startswith("/?"):
            self._send(200, render_page().encode(), "text/html; charset=utf-8")
        elif self.path == "/api/state":
            self._send(200, json.dumps(load_state()).encode(), "application/json")
        elif self.path.startswith("/img/"):
            self._serve_file(OUTPUT_DIR, self.path[5:].split("/"), img_types)
        elif self.path.startswith("/evidence/"):
            self._serve_file(EVIDENCE_DIR, self.path[10:].split("/"), img_types)
        else:
            self._send(404, b"not found", "text/plain")

    def do_POST(self) -> None:  # noqa: N802 - http.server API
        if self.path != "/api/state":
            self._send(404, b"not found", "text/plain")
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
            if length > 5_000_000:
                self._send(413, b"too large", "text/plain")
                return
            payload = json.loads(self.rfile.read(length))
            if not isinstance(payload, dict):
                raise ValueError("state must be an object")
        except (ValueError, json.JSONDecodeError) as exc:
            self._send(400, f"invalid payload: {exc}".encode(), "text/plain")
            return
        merged = load_state()
        merged.update(payload)
        save_state(merged)
        self._send(200, b'{"ok": true}', "application/json")

    def log_message(self, fmt: str, *args) -> None:  # quiet
        pass


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", type=int, default=8944)
    args = parser.parse_args()
    REVIEW_DIR.mkdir(parents=True, exist_ok=True)
    server = ThreadingHTTPServer(("127.0.0.1", args.port), ReviewHandler)
    stamp = datetime.now(UTC).strftime("%H:%M:%SZ")
    print(f"[{stamp}] review board: http://127.0.0.1:{args.port}/  (state: {STATE_PATH})")
    server.serve_forever()


if __name__ == "__main__":
    main()
