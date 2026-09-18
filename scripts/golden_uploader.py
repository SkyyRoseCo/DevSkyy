"""Local single-file FastAPI app for uploading replacement SKU golden photos.

Use case: the SKU-to-golden alignment audit flagged mismatched goldens
(e.g. lh-005 catalog says bomber jacket, but the on-disk golden is a fanny
pack). Use this app to drag-and-drop the correct product photo for each
mismatched SKU; it overwrites
``skyyrose/elite_studio/assets/golden/{sku}/front.jpg`` and backs up the
prior file as ``front.jpg.bak.<unix-ts>``.

Run:
    .venv/bin/python scripts/golden_uploader.py
    open http://127.0.0.1:8765

Stop with Ctrl-C. No external services; pure local FastAPI.
"""

from __future__ import annotations

import logging
import re
import shutil
import sys
import time
from io import BytesIO
from pathlib import Path

# Bootstrap project root onto sys.path so this standalone script can import
# from skyyrose.core.* — only needed because uploader runs via
# `.venv/bin/python scripts/golden_uploader.py`, not as `python -m`.
_REPO_ROOT = Path(__file__).resolve().parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from fastapi import FastAPI, File, Form, HTTPException, Response, UploadFile  # noqa: E402
from fastapi.responses import HTMLResponse, JSONResponse  # noqa: E402
from PIL import Image  # noqa: E402

from skyyrose.core.paths import (
    CATALOG_CSV,
)
from skyyrose.core.paths import DOSSIERS_DIR as DOSSIER_ROOT  # noqa: E402
from skyyrose.core.paths import GOLDEN_DIR as GOLDEN_ROOT
from skyyrose.core.paths import PRODUCT_REFERENCES, golden_path

logger = logging.getLogger(__name__)

REPO_ROOT = _REPO_ROOT

ALLOWED_EXT = {".jpg", ".jpeg", ".png", ".webp"}
ALLOWED_PIL_FORMATS = {"JPEG", "PNG", "WEBP"}
PORT = 8765

PRODUCT_REFERENCES_DIR = PRODUCT_REFERENCES
TECHFLAT_REVIEW_JSON = PRODUCT_REFERENCES_DIR / "techflat-review.json"
# Layout codes the founder assigns per techflat in the review tab.
TECHFLAT_LAYOUTS = {
    "single": "Single garment, one view (front only — no split)",
    "lr": "Front (left) + Back (right), side by side",
    "tb": "Front (top) + Back (bottom), stacked",
    "grid": "2x2 set grid (multiple garments x front/back)",
    "wrong": "WRONG product / mislabeled — flag for re-upload",
    "unset": "Not yet reviewed",
}

# Canonical golden angles the pipeline consumes. Mirrors
# skyyrose.elite_studio.quality.visual_regression.CANONICAL_ANGLES plus the
# single-shot 'reference' baseline used by the SSIM comparator.
CANONICAL_ANGLES: tuple[str, ...] = (
    "front",
    "back",
    "three-quarter",
    "detail-1",
    "detail-2",
    "reference",
)
DEFAULT_ANGLE = "front"

app = FastAPI(title="SkyyRose Golden Uploader", version="1.0.0")


def _list_skus() -> list[str]:
    """Return sorted list of SKU folder names under the golden root."""
    if not GOLDEN_ROOT.is_dir():
        return []
    return sorted(p.name for p in GOLDEN_ROOT.iterdir() if p.is_dir())


def _load_catalog() -> list[dict[str, str]]:
    """Return the full catalog as a list of ``{sku, name, collection, dossier_slug}`` dicts.

    Uses csv module to handle quoted name fields with embedded commas.
    Returns rows in catalog order so the UI mirrors the source file.
    """
    from skyyrose.core.catalog_loader import read_catalog_rows

    return [
        {
            key: row.get(key, "").strip()
            for key in ("sku", "name", "collection", "dossier_slug", "is_preorder")
        }
        for row in read_catalog_rows(CATALOG_CSV)
    ]


def _set_preorder(sku: str, value: bool) -> None:
    """Flip the ``is_preorder`` column for one SKU in the canonical CSV.

    Rewrites the whole CSV preserving column order and every other field —
    only the target SKU's ``is_preorder`` cell changes. The catalog-drift
    guard hook fires on this write and announces the canonical touch.
    """
    from skyyrose.core.catalog_loader import CATALOG_CSV as canonical_csv
    from skyyrose.core.product_registry import update_catalog_fields

    if CATALOG_CSV.resolve() == canonical_csv.resolve():
        update_catalog_fields(
            sku, {"is_preorder": "1" if value else "0", "badge": "Pre-Order" if value else ""}
        )
        return

    import csv

    if not CATALOG_CSV.is_file():
        raise HTTPException(500, "catalog CSV missing")
    with CATALOG_CSV.open("r", encoding="utf-8", newline="") as fh:
        reader = csv.DictReader(fh)
        fieldnames = list(reader.fieldnames or [])
        rows = list(reader)
    if "is_preorder" not in fieldnames:
        raise HTTPException(500, "is_preorder column not present in catalog")
    found = False
    for r in rows:
        if (r.get("sku") or "").strip() == sku:
            r["is_preorder"] = "1" if value else "0"
            found = True
            break
    if not found:
        raise HTTPException(404, f"sku not in catalog: {sku}")
    with CATALOG_CSV.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames, quoting=csv.QUOTE_MINIMAL)
        writer.writeheader()
        writer.writerows(rows)


def _current_angle_path(sku: str, angle: str) -> Path | None:
    """Return the on-disk path for a SKU's angle image if present."""
    try:
        candidate = golden_path(sku, angle)
    except ValueError:
        return None
    return candidate if candidate.is_file() else None


def _angles_present(sku: str) -> list[str]:
    """Return the canonical angles that have an image on disk for this SKU."""
    return [a for a in CANONICAL_ANGLES if _current_angle_path(sku, a) is not None]


def _validate_angle(angle: str) -> str:
    """Validate an angle against the canonical allowlist."""
    if angle not in CANONICAL_ANGLES:
        raise HTTPException(
            400,
            f"invalid angle {angle!r} (allowed: {', '.join(CANONICAL_ANGLES)})",
        )
    return angle


def _safe_target_path(sku: str, angle: str) -> Path:
    """Validate SKU + angle and return the canonical ``{angle}.jpg`` path.

    Defense-in-depth: ``golden_path()`` rejects traversal payloads (``..``,
    ``/``, ``\\``); the extra alphanumeric check below also rejects empty
    strings and stray punctuation. ``angle`` is validated against the
    canonical allowlist. Creates the per-SKU directory as a side effect.
    """
    if not sku or not sku.replace("-", "").isalnum():
        raise HTTPException(400, f"invalid sku id: {sku!r}")
    _validate_angle(angle)
    try:
        target = golden_path(sku, angle)
    except ValueError as exc:
        raise HTTPException(400, f"invalid sku id: {sku!r}") from exc
    target.parent.mkdir(parents=True, exist_ok=True)
    return target


def _backup_existing(path: Path) -> Path | None:
    """Move existing file to .bak.<ts>; return the backup path."""
    if not path.is_file():
        return None
    ts = int(time.time())
    backup = path.with_suffix(f".jpg.bak.{ts}")
    shutil.copy2(path, backup)
    return backup


def _save_as_jpeg(image_bytes: bytes, dest: Path) -> tuple[int, int]:
    """Decode upload, save as JPEG at dest. Returns (width, height).

    PIL's detected ``image.format`` is checked against ``ALLOWED_PIL_FORMATS``
    before re-encode to defeat polyglot uploads (e.g., a renamed binary that
    extension-matches but PIL identifies as something else).
    """
    image = Image.open(BytesIO(image_bytes))
    if image.format not in ALLOWED_PIL_FORMATS:
        raise ValueError(
            f"image format {image.format!r} not in allowlist {sorted(ALLOWED_PIL_FORMATS)}"
        )
    if image.mode != "RGB":
        image = image.convert("RGB")
    image.save(dest, format="JPEG", quality=95, optimize=True)
    return image.size


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------


@app.get("/api/skus")
def list_skus_with_catalog() -> JSONResponse:
    """Return every catalog SKU with name, collection, golden state, and dossier.

    Iterates the catalog (authoritative source) so SKUs without a
    ``golden/{sku}/`` directory still surface as upload-target tiles.
    """
    rows = []
    for entry in _load_catalog():
        sku = entry["sku"]
        angles = _angles_present(sku)
        rows.append(
            {
                "sku": sku,
                "name": entry["name"],
                "collection": entry["collection"],
                "dossier_slug": entry["dossier_slug"],
                "has_front": "front" in angles,
                "angles": angles,
                "all_angles": list(CANONICAL_ANGLES),
                "is_preorder": entry["is_preorder"] == "1",
                "has_dossier": (
                    (DOSSIER_ROOT / f"{entry['dossier_slug']}.md").is_file()
                    if entry["dossier_slug"]
                    else False
                ),
            }
        )
    return JSONResponse(rows)


_SKU_TOKEN_RE = re.compile(r"(?:br|lh|sg|kids)-\d+")


def _infer_skus_from_filename(filename: str) -> list[str]:
    """Pull every SKU-like token from a techflat filename, de-duplicated in order.

    e.g. ``sg-001-and-sg-003-bridge-shorts-techflat.jpeg`` -> [sg-001, sg-003].
    """
    seen: list[str] = []
    for token in _SKU_TOKEN_RE.findall(filename):
        if token not in seen:
            seen.append(token)
    return seen


def _list_techflat_files() -> list[Path]:
    """Return every ``*-techflat.*`` file in product-references, sorted."""
    if not PRODUCT_REFERENCES_DIR.is_dir():
        return []
    return sorted(PRODUCT_REFERENCES_DIR.glob("*-techflat.*"))


def _load_techflat_review() -> dict:
    """Load the founder's techflat review state (or empty)."""
    if not TECHFLAT_REVIEW_JSON.is_file():
        return {}
    try:
        import json

        return json.loads(TECHFLAT_REVIEW_JSON.read_text(encoding="utf-8"))
    except Exception:
        return {}


def _save_techflat_review(state: dict) -> None:
    import json

    TECHFLAT_REVIEW_JSON.write_text(json.dumps(state, indent=2, sort_keys=True), encoding="utf-8")


@app.get("/api/techflats")
def list_techflats() -> JSONResponse:
    """Return every techflat file with inferred SKUs, catalog names, review state."""
    catalog = {e["sku"]: e for e in _load_catalog()}
    review = _load_techflat_review()
    rows = []
    for path in _list_techflat_files():
        fn = path.name
        skus = _infer_skus_from_filename(fn)
        names = [catalog[s]["name"] for s in skus if s in catalog]
        saved = review.get(fn, {})
        try:
            with Image.open(path) as im:
                w, h = im.size
        except Exception:
            w = h = 0
        rows.append(
            {
                "filename": fn,
                "skus": skus,
                "names": names,
                "width": w,
                "height": h,
                "aspect": round(w / h, 2) if h else 0,
                "layout": saved.get("layout", "unset"),
                "note": saved.get("note", ""),
            }
        )
    return JSONResponse({"layouts": TECHFLAT_LAYOUTS, "rows": rows})


@app.get("/api/techflat-image/{filename}")
def techflat_image(filename: str) -> Response:
    """Serve a techflat image by filename (validated against the known set)."""
    valid = {p.name for p in _list_techflat_files()}
    if filename not in valid:
        raise HTTPException(404, f"no techflat named {filename!r}")
    path = PRODUCT_REFERENCES_DIR / filename
    return Response(content=path.read_bytes(), media_type="image/jpeg")


@app.post("/api/techflat-review")
def save_techflat_review(
    filename: str = Form(...),
    layout: str = Form(...),
    note: str = Form(""),
) -> JSONResponse:
    """Persist the founder's layout/mismatch call for one techflat."""
    valid = {p.name for p in _list_techflat_files()}
    if filename not in valid:
        raise HTTPException(404, f"no techflat named {filename!r}")
    if layout not in TECHFLAT_LAYOUTS:
        raise HTTPException(400, f"invalid layout {layout!r} (allowed: {list(TECHFLAT_LAYOUTS)})")
    state = _load_techflat_review()
    state[filename] = {"layout": layout, "note": note.strip()}
    _save_techflat_review(state)
    return JSONResponse({"ok": True, "filename": filename, "layout": layout})


@app.post("/api/preorder")
def set_preorder(sku: str = Form(...), is_preorder: int = Form(...)) -> JSONResponse:
    """Set the pre-order flag for a SKU in the canonical catalog CSV."""
    if not sku or not sku.replace("-", "").isalnum():
        raise HTTPException(400, f"invalid sku id: {sku!r}")
    _set_preorder(sku, bool(is_preorder))
    return JSONResponse({"ok": True, "sku": sku, "is_preorder": bool(is_preorder)})


@app.get("/api/dossier/{sku}")
def dossier(sku: str) -> Response:
    """Return the markdown body of the dossier for a SKU (or 404)."""
    for entry in _load_catalog():
        if entry["sku"] == sku and entry["dossier_slug"]:
            path = DOSSIER_ROOT / f"{entry['dossier_slug']}.md"
            if path.is_file():
                return Response(content=path.read_bytes(), media_type="text/markdown")
            break
    raise HTTPException(404, f"no dossier for {sku}")


@app.get("/api/preview/{sku}/{angle}")
def preview(sku: str, angle: str) -> Response:
    """Return the current image for a SKU's angle (or 404)."""
    _validate_angle(angle)
    path = _current_angle_path(sku, angle)
    if path is None:
        raise HTTPException(404, f"no {angle}.jpg for {sku}")
    return Response(content=path.read_bytes(), media_type="image/jpeg")


@app.post("/api/upload")
async def upload(
    sku: str = Form(...),
    file: UploadFile = File(...),
    angle: str = Form(DEFAULT_ANGLE),
) -> JSONResponse:
    """Write the uploaded image to ``golden/{sku}/{angle}.jpg``.

    ``angle`` defaults to ``front`` and must be one of the canonical angles.
    The existing file is moved to ``{angle}.jpg.bak.<unix-ts>`` so the prior
    state is recoverable. The upload is normalized to JPEG (quality 95).
    """
    _validate_angle(angle)
    ext = Path(file.filename or "").suffix.lower()
    if ext and ext not in ALLOWED_EXT:
        raise HTTPException(415, f"unsupported file type: {ext} (allowed: {sorted(ALLOWED_EXT)})")

    body = await file.read()
    if not body:
        raise HTTPException(400, "empty file")
    if len(body) > 25 * 1024 * 1024:
        raise HTTPException(413, "file > 25 MB")

    dest = _safe_target_path(sku, angle)
    backup = _backup_existing(dest)
    try:
        width, height = _save_as_jpeg(body, dest)
    except Exception as exc:
        if backup is not None:
            shutil.copy2(backup, dest)
        raise HTTPException(400, f"could not decode image: {exc}") from exc

    return JSONResponse(
        {
            "ok": True,
            "sku": sku,
            "angle": angle,
            "dest": str(dest.relative_to(REPO_ROOT)),
            "backup": str(backup.relative_to(REPO_ROOT)) if backup else None,
            "size_bytes": dest.stat().st_size,
            "dimensions": [width, height],
        }
    )


# ---------------------------------------------------------------------------
# HTML UI
# ---------------------------------------------------------------------------


_INDEX_HTML = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8" />
<title>SkyyRose Golden Uploader</title>
<style>
  :root {
    --bg: #0a0a0a;
    --panel: #141414;
    --border: #2a2a2a;
    --text: #f5f5f5;
    --muted: #999;
    --accent: #B76E79; /* rose gold */
    --ok: #6fcf97;
    --bad: #eb5757;
  }
  * { box-sizing: border-box; }
  body {
    background: var(--bg); color: var(--text); margin: 0;
    font-family: -apple-system, BlinkMacSystemFont, system-ui, sans-serif;
  }
  header { padding: 24px 32px; border-bottom: 1px solid var(--border); }
  h1 { margin: 0; font-weight: 500; letter-spacing: 0.02em; }
  .subtitle { color: var(--muted); font-size: 13px; margin-top: 6px; }
  main { padding: 24px 32px; max-width: 1200px; margin: 0 auto; }
  .grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
    gap: 16px;
  }
  .card {
    background: var(--panel);
    border: 1px solid var(--border);
    border-radius: 8px;
    overflow: hidden;
    display: flex;
    flex-direction: column;
  }
  .card-img {
    aspect-ratio: 1;
    background: #1a1a1a no-repeat center / contain;
    border-bottom: 1px solid var(--border);
    position: relative;
  }
  .card-img.empty::before {
    content: "no golden on disk — upload";
    position: absolute; inset: 0;
    display: grid; place-items: center;
    color: var(--muted); font-size: 12px;
  }
  .card-img.empty { background-color: #1f1313; }
  .card-body { padding: 12px 14px; flex: 1; display: flex; flex-direction: column; }
  .sku-row { display: flex; justify-content: space-between; align-items: center; gap: 8px; }
  .sku { color: var(--accent); font-family: ui-monospace, monospace; font-size: 13px; }
  .badge {
    font-size: 10px; padding: 2px 6px; border-radius: 3px;
    background: var(--border); color: var(--muted); text-transform: uppercase;
    letter-spacing: 0.04em;
  }
  .badge.black-rose { background: #2a1218; color: #d4a8b4; }
  .badge.love-hurts { background: #2a1212; color: #e89090; }
  .badge.signature { background: #2a2618; color: #e8c890; }
  .badge.kids { background: #18222a; color: #90b4d4; }
  .dossier-link {
    margin-top: 6px; font-size: 11px; color: var(--muted);
    text-decoration: none; display: inline-block;
  }
  .dossier-link:hover { color: var(--accent); }
  .dossier-link.missing { color: var(--bad); cursor: default; pointer-events: none; }
  .name { font-size: 13px; margin-top: 4px; color: var(--text); min-height: 32px; }
  .filter-bar {
    margin-bottom: 16px; display: flex; gap: 8px; flex-wrap: wrap;
    font-size: 12px;
  }
  .filter-btn {
    padding: 6px 12px; background: var(--panel); border: 1px solid var(--border);
    color: var(--muted); border-radius: 16px; cursor: pointer;
    font: inherit;
  }
  .filter-btn.active { background: var(--accent); color: #fff; border-color: var(--accent); }
  .drop {
    margin-top: 10px;
    border: 1px dashed var(--border);
    border-radius: 6px;
    padding: 10px;
    text-align: center;
    font-size: 12px;
    color: var(--muted);
    cursor: pointer;
    transition: border-color .15s, color .15s;
  }
  .drop:hover, .drop.dragging { border-color: var(--accent); color: var(--accent); }
  .drop input { display: none; }
  .status { margin-top: 8px; font-size: 11px; min-height: 14px; }
  .status.ok { color: var(--ok); }
  .status.bad { color: var(--bad); }
  .angles {
    margin-top: 10px; display: flex; gap: 4px; flex-wrap: wrap;
  }
  .angle-btn {
    position: relative;
    flex: 1 1 auto; min-width: 34px;
    padding: 5px 4px; font: inherit; font-size: 10px;
    background: var(--bg); border: 1px solid var(--border);
    color: var(--muted); border-radius: 4px; cursor: pointer;
    text-align: center; letter-spacing: 0.02em;
    transition: border-color .12s, color .12s, background .12s;
  }
  .angle-btn:hover { border-color: var(--accent); color: var(--text); }
  .angle-btn.active { border-color: var(--accent); color: #fff; background: #2a1a1e; }
  /* coverage dot: filled = on disk, hollow = missing */
  .angle-btn::after {
    content: ""; display: block; width: 5px; height: 5px;
    border-radius: 50%; margin: 3px auto 0;
    border: 1px solid var(--muted); background: transparent;
  }
  .angle-btn.has::after { background: var(--ok); border-color: var(--ok); }
  .angles-label { font-size: 10px; color: var(--muted); margin-top: 10px; text-transform: uppercase; letter-spacing: 0.05em; }
  .preorder {
    display: flex; align-items: center; gap: 7px; margin-top: 10px;
    font-size: 12px; color: var(--muted); cursor: pointer; user-select: none;
  }
  .preorder input { width: 15px; height: 15px; accent-color: var(--accent); cursor: pointer; margin: 0; }
  .preorder.on { color: var(--accent); }
  .badge.preorder-badge { background: #2a2014; color: #e8c890; }
  .view-toggle { margin-top: 14px; display: flex; gap: 8px; }
  .view-btn {
    padding: 7px 16px; background: var(--panel); border: 1px solid var(--border);
    color: var(--muted); border-radius: 6px; cursor: pointer; font: inherit; font-size: 13px;
  }
  .view-btn.active { background: var(--accent); color: #fff; border-color: var(--accent); }
  .tf-img {
    width: 100%; aspect-ratio: 4/3; object-fit: contain;
    background: #1a1a1a; border-bottom: 1px solid var(--border); display: block;
  }
  .tf-meta { padding: 12px 14px; }
  .tf-file { font-family: ui-monospace, monospace; font-size: 11px; color: var(--muted); word-break: break-all; }
  .tf-skus { margin-top: 6px; }
  .tf-skus .sku { font-size: 12px; }
  .tf-name { font-size: 12px; color: var(--text); margin-top: 4px; }
  .tf-dims { font-size: 10px; color: var(--muted); margin-top: 4px; }
  .tf-layout { margin-top: 10px; width: 100%; padding: 7px; font: inherit; font-size: 12px;
    background: var(--bg); color: var(--text); border: 1px solid var(--border); border-radius: 5px; }
  .tf-layout.reviewed { border-color: var(--ok); }
  .tf-layout.wrong { border-color: var(--bad); color: var(--bad); }
  .tf-note { margin-top: 6px; width: 100%; padding: 6px; font: inherit; font-size: 11px;
    background: var(--bg); color: var(--text); border: 1px solid var(--border); border-radius: 5px; resize: vertical; min-height: 30px; }
  .tf-status { font-size: 10px; min-height: 12px; margin-top: 4px; }
  .tf-status.ok { color: var(--ok); }
  .tf-status.bad { color: var(--bad); }
</style>
</head>
<body>
<header>
  <h1>SkyyRose Golden Uploader</h1>
  <div class="subtitle">
    Pick an angle, then drop a photo to write <code>golden/&lt;sku&gt;/&lt;angle&gt;.jpg</code>.
    Filled dot = on disk. Prior file is backed up to <code>&lt;angle&gt;.jpg.bak.&lt;ts&gt;</code>.
  </div>
  <div class="view-toggle">
    <button class="view-btn active" id="view-goldens">Goldens</button>
    <button class="view-btn" id="view-techflats">Techflats (layout review)</button>
  </div>
</header>
<main>
  <div id="goldens-view">
    <div class="filter-bar" id="filter-bar"></div>
    <div id="grid" class="grid"></div>
  </div>
  <div id="techflats-view" style="display:none;">
    <div class="subtitle" style="margin-bottom:16px;">
      Mark each techflat's layout so the splitter knows how to crop it.
      Flag <strong>WRONG product</strong> if the image doesn't match the SKU — that one gets a re-upload, not a split.
    </div>
    <div id="tf-grid" class="grid"></div>
  </div>
</main>
<script>
const grid = document.getElementById('grid');
const filterBar = document.getElementById('filter-bar');
let allRows = [];
let currentFilter = 'all';

const FILTERS = [
  { id: 'all',        label: 'All' },
  { id: 'no-golden',  label: 'Missing front' },
  { id: 'incomplete', label: 'Incomplete angles' },
  { id: 'preorder',   label: 'Pre-order' },
  { id: 'black-rose', label: 'Black Rose' },
  { id: 'love-hurts', label: 'Love Hurts' },
  { id: 'signature',  label: 'Signature' },
  { id: 'kids-capsule', label: 'Kids' },
];

// Short labels for the angle picker buttons.
const ANGLE_LABELS = {
  'front': 'F', 'back': 'B', 'three-quarter': '¾',
  'detail-1': 'D1', 'detail-2': 'D2', 'reference': 'Ref',
};

function applyFilter() {
  let rows = allRows;
  if (currentFilter === 'no-golden') {
    rows = rows.filter((r) => !r.has_front);
  } else if (currentFilter === 'incomplete') {
    rows = rows.filter((r) => (r.angles || []).length < (r.all_angles || []).length);
  } else if (currentFilter === 'preorder') {
    rows = rows.filter((r) => r.is_preorder);
  } else if (currentFilter !== 'all') {
    rows = rows.filter((r) => r.collection === currentFilter);
  }
  grid.innerHTML = '';
  rows.forEach(renderTile);
}

function renderFilterBar() {
  filterBar.innerHTML = '';
  FILTERS.forEach((f) => {
    const btn = document.createElement('button');
    btn.className = 'filter-btn' + (f.id === currentFilter ? ' active' : '');
    btn.textContent = f.label;
    btn.onclick = () => { currentFilter = f.id; renderFilterBar(); applyFilter(); };
    filterBar.appendChild(btn);
  });
}

async function load() {
  const r = await fetch('/api/skus');
  allRows = await r.json();
  renderFilterBar();
  applyFilter();
}

function renderTile(row) {
  const card = document.createElement('div');
  card.className = 'card';

  // Per-tile selected angle + the live set of angles present on disk.
  let selectedAngle = 'front';
  const present = new Set(row.angles || []);

  const img = document.createElement('div');
  const refreshPreview = () => {
    if (present.has(selectedAngle)) {
      img.classList.remove('empty');
      img.style.backgroundImage =
        `url('/api/preview/${row.sku}/${selectedAngle}?t=${Date.now()}')`;
    } else {
      img.classList.add('empty');
      img.style.backgroundImage = '';
    }
  };
  img.className = 'card-img';
  card.appendChild(img);

  const body = document.createElement('div');
  body.className = 'card-body';

  const collShort = (row.collection || '').replace('kids-capsule', 'kids');
  const collBadge = row.collection
    ? `<span class="badge ${row.collection.replace('-capsule','')}">${collShort}</span>`
    : '';
  const dossierClass = row.has_dossier ? '' : ' missing';
  const dossierHref = row.has_dossier ? `/api/dossier/${row.sku}` : '#';
  const dossierLabel = row.has_dossier
    ? `dossier: ${row.dossier_slug}`
    : 'no dossier';
  const angleCount = (row.angles || []).length;
  const totalAngles = (row.all_angles || []).length;

  body.innerHTML =
    `<div class="sku-row"><div class="sku">${row.sku}</div>${collBadge}</div>` +
    `<div class="name">${row.name}</div>` +
    `<a class="dossier-link${dossierClass}" href="${dossierHref}" target="_blank" rel="noopener">${dossierLabel}</a>` +
    `<div class="angles-label">angles ${angleCount}/${totalAngles}</div>`;

  // Angle picker — one button per canonical angle, dot shows coverage.
  const angles = document.createElement('div');
  angles.className = 'angles';
  const angleButtons = {};
  (row.all_angles || []).forEach((angle) => {
    const btn = document.createElement('button');
    btn.className = 'angle-btn'
      + (angle === selectedAngle ? ' active' : '')
      + (present.has(angle) ? ' has' : '');
    btn.textContent = ANGLE_LABELS[angle] || angle;
    btn.title = angle + (present.has(angle) ? ' (on disk)' : ' (missing)');
    btn.onclick = () => {
      selectedAngle = angle;
      Object.values(angleButtons).forEach((b) => b.classList.remove('active'));
      btn.classList.add('active');
      refreshPreview();
      drop.textContent = `drop image or click → ${angle}`;
      status.textContent = '';
      status.className = 'status';
    };
    angleButtons[angle] = btn;
    angles.appendChild(btn);
  });

  const drop = document.createElement('label');
  drop.className = 'drop';
  drop.textContent = 'drop image or click → front';
  const input = document.createElement('input');
  input.type = 'file';
  input.accept = 'image/*';
  drop.appendChild(input);

  const status = document.createElement('div');
  status.className = 'status';

  const upload = async (file) => {
    if (!file) return;
    status.textContent = `uploading ${selectedAngle}…`;
    status.className = 'status';
    const fd = new FormData();
    fd.append('sku', row.sku);
    fd.append('angle', selectedAngle);
    fd.append('file', file);
    try {
      const resp = await fetch('/api/upload', { method: 'POST', body: fd });
      const data = await resp.json();
      if (!resp.ok) {
        status.textContent = data.detail || 'upload failed';
        status.className = 'status bad';
        return;
      }
      status.textContent =
        `${data.angle} saved (${data.dimensions[0]}×${data.dimensions[1]}, ${(data.size_bytes/1024).toFixed(0)}KB)`;
      status.className = 'status ok';
      present.add(selectedAngle);
      if (angleButtons[selectedAngle]) angleButtons[selectedAngle].classList.add('has');
      const lbl = body.querySelector('.angles-label');
      if (lbl) lbl.textContent = `angles ${present.size}/${totalAngles}`;
      refreshPreview();
    } catch (e) {
      status.textContent = 'network error';
      status.className = 'status bad';
    }
  };

  input.addEventListener('change', () => upload(input.files[0]));

  ['dragenter', 'dragover'].forEach((evt) =>
    drop.addEventListener(evt, (e) => {
      e.preventDefault();
      drop.classList.add('dragging');
    })
  );
  ['dragleave', 'drop'].forEach((evt) =>
    drop.addEventListener(evt, (e) => {
      e.preventDefault();
      drop.classList.remove('dragging');
    })
  );
  drop.addEventListener('drop', (e) => upload(e.dataTransfer.files[0]));

  // Pre-order toggle — writes is_preorder back to the canonical catalog CSV.
  const pre = document.createElement('label');
  pre.className = 'preorder' + (row.is_preorder ? ' on' : '');
  const cb = document.createElement('input');
  cb.type = 'checkbox';
  cb.checked = !!row.is_preorder;
  const preTxt = document.createElement('span');
  preTxt.textContent = 'Pre-order';
  pre.appendChild(cb);
  pre.appendChild(preTxt);
  cb.addEventListener('change', async () => {
    const fd = new FormData();
    fd.append('sku', row.sku);
    fd.append('is_preorder', cb.checked ? '1' : '0');
    try {
      const resp = await fetch('/api/preorder', { method: 'POST', body: fd });
      const data = await resp.json();
      if (!resp.ok) {
        cb.checked = !cb.checked;
        status.textContent = data.detail || 'pre-order save failed';
        status.className = 'status bad';
        return;
      }
      row.is_preorder = cb.checked;
      pre.classList.toggle('on', cb.checked);
      status.textContent = cb.checked ? 'marked pre-order' : 'pre-order cleared';
      status.className = 'status ok';
    } catch (e) {
      cb.checked = !cb.checked;
      status.textContent = 'network error';
      status.className = 'status bad';
    }
  });

  body.appendChild(angles);
  body.appendChild(pre);
  body.appendChild(drop);
  body.appendChild(status);
  card.appendChild(body);
  grid.appendChild(card);

  refreshPreview();
}

// ── Techflat layout-review view ──────────────────────────────────────
const tfGrid = document.getElementById('tf-grid');
let tfLayouts = {};
let tfLoaded = false;

async function loadTechflats() {
  const r = await fetch('/api/techflats');
  const data = await r.json();
  tfLayouts = data.layouts;
  tfGrid.innerHTML = '';
  data.rows.forEach(renderTechflatTile);
  tfLoaded = true;
}

function renderTechflatTile(row) {
  const card = document.createElement('div');
  card.className = 'card';

  const img = document.createElement('img');
  img.className = 'tf-img';
  img.loading = 'lazy';
  img.src = `/api/techflat-image/${encodeURIComponent(row.filename)}`;
  card.appendChild(img);

  const meta = document.createElement('div');
  meta.className = 'tf-meta';

  const skuHtml = (row.skus || [])
    .map((s) => `<span class="sku">${s}</span>`)
    .join(' ');
  const namesHtml = (row.names || []).join(' · ') || '<span style="color:var(--bad)">no catalog match</span>';

  meta.innerHTML =
    `<div class="tf-file">${row.filename}</div>` +
    `<div class="tf-skus">${skuHtml || '<span style="color:var(--bad)">no SKU in filename</span>'}</div>` +
    `<div class="tf-name">${namesHtml}</div>` +
    `<div class="tf-dims">${row.width}×${row.height} · ar ${row.aspect}</div>`;

  const sel = document.createElement('select');
  sel.className = 'tf-layout';
  Object.entries(tfLayouts).forEach(([code, label]) => {
    const opt = document.createElement('option');
    opt.value = code;
    opt.textContent = label;
    if (code === row.layout) opt.selected = true;
    sel.appendChild(opt);
  });
  const applyClass = () => {
    sel.classList.toggle('reviewed', sel.value !== 'unset' && sel.value !== 'wrong');
    sel.classList.toggle('wrong', sel.value === 'wrong');
  };
  applyClass();

  const note = document.createElement('textarea');
  note.className = 'tf-note';
  note.placeholder = 'note (optional) — e.g. "shows shorts not the bomber"';
  note.value = row.note || '';

  const tfStatus = document.createElement('div');
  tfStatus.className = 'tf-status';

  const save = async () => {
    const fd = new FormData();
    fd.append('filename', row.filename);
    fd.append('layout', sel.value);
    fd.append('note', note.value);
    try {
      const resp = await fetch('/api/techflat-review', { method: 'POST', body: fd });
      const data = await resp.json();
      if (!resp.ok) {
        tfStatus.textContent = data.detail || 'save failed';
        tfStatus.className = 'tf-status bad';
        return;
      }
      applyClass();
      tfStatus.textContent = 'saved';
      tfStatus.className = 'tf-status ok';
    } catch (e) {
      tfStatus.textContent = 'network error';
      tfStatus.className = 'tf-status bad';
    }
  };
  sel.addEventListener('change', save);
  note.addEventListener('blur', save);

  meta.appendChild(sel);
  meta.appendChild(note);
  meta.appendChild(tfStatus);
  card.appendChild(meta);
  tfGrid.appendChild(card);
}

// View switching
const goldensView = document.getElementById('goldens-view');
const techflatsView = document.getElementById('techflats-view');
const btnGoldens = document.getElementById('view-goldens');
const btnTechflats = document.getElementById('view-techflats');

btnGoldens.onclick = () => {
  goldensView.style.display = '';
  techflatsView.style.display = 'none';
  btnGoldens.classList.add('active');
  btnTechflats.classList.remove('active');
};
btnTechflats.onclick = () => {
  goldensView.style.display = 'none';
  techflatsView.style.display = '';
  btnTechflats.classList.add('active');
  btnGoldens.classList.remove('active');
  if (!tfLoaded) loadTechflats();
};

load();
</script>
</body>
</html>
"""


@app.get("/", response_class=HTMLResponse)
def index() -> HTMLResponse:
    return HTMLResponse(_INDEX_HTML)


def main() -> None:
    import uvicorn

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(name)s %(levelname)s %(message)s",
    )
    print(f"SkyyRose Golden Uploader → http://127.0.0.1:{PORT}")
    print(f"Writing to: {GOLDEN_ROOT}")
    uvicorn.run(app, host="127.0.0.1", port=PORT, log_level="warning")


if __name__ == "__main__":
    main()
