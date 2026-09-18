"""On-model lookbook generation — gpt-image-2 edit of a real garment into a scene.

Folded from the engine-comparison prototype (renders/oai/_lookbook/_prototype/):
gpt-image-2 **edit** won decisively over FASHN try-on and FLUX Kontext because it
absorbs a flat product *techflat* + a styled scene in a single pass — producing a
model who genuinely *wears* the garment in the scene, no floating. FASHN needs a
ghost-mannequin/product garment image (wrong input contract for our flat
techflats); Kontext's masked scene-drop produced blank output. Verdict + evidence:
``renders/oai/_lookbook/_prototype/NOTES.md`` (bug-141 for the FASHN dead-end).

This module reuses the canonical OAI imagery infrastructure rather than
re-implementing it:
  • garment refs  -> ``references.build_references`` (canonical SKU→techflat map,
                     hard-fails on a missing garment — no silent fallback)
  • catalog facts -> ``catalog_loader.get_product_with_dossier``
  • the edit call -> ``client.OAIImageClient`` (retry/backoff, gpt-image-2 high)
  • cost + gate   -> ``cost.CostManifest`` / ``format_manifest`` / ``SpendTracker``

CLI:
    python -m scripts.oai_render.lookbook plan     --sku lh-004 --scene <scene.png>
    python -m scripts.oai_render.lookbook generate --sku lh-004 --scene <scene.png> --yes
"""

from __future__ import annotations

import argparse
import logging
import re
import sys
from pathlib import Path

import openai

# Ensure OPENAI_API_KEY is present for config.get_api_key() — the project env
# loader (root .env + gemini/.env) may not carry it; .env.hf does. config reads
# the key LAZILY (at OAIImageClient init, in _generate_one), so loading .env.hf
# here at import — before any client is built — is sufficient. The interpreter
# reads the value; it is never logged.

_log = logging.getLogger(__name__)
try:
    from dotenv import load_dotenv

    load_dotenv(Path(__file__).resolve().parents[2] / ".env.hf", override=False)
except ImportError:  # pragma: no cover - dotenv optional if key already exported
    pass

from skyyrose.core.catalog_loader import get_product_with_dossier  # noqa: E402
from skyyrose.core.dossier_loader import DossierMissingError  # noqa: E402

from . import config, cost, references  # noqa: E402
from .client import OAIImageClient  # noqa: E402

# Per-collection scene register (the prompt's setting; the actual backdrop image
# is supplied via --scene). love-hurts = the Beauty-and-the-Beast gothic world;
# the others default to the brand's Oakland-concrete-luxury register.
# Locked 2026-06-18 by the photography-director + image-prompt-engineer
# collaboration (brand-canon settings + photographic craft, director final
# canon sign-off). Cathedral (European-house lineage, locked out) rerouted to a
# decayed Oakland Art Deco theater for canon-safe Beauty-and-the-Beast grandeur
# (founder asked for more B&B feel); Kids "mauve" → "warm neutral" (mauve = Love
# Hurts palette). Each string completes "The model stands in {scene_desc}."
COLLECTION_SCENE: dict[str, str] = {
    "love-hurts": (
        "the gilded mezzanine of a decayed Oakland Art Deco theater at midnight — "
        "peeling gold leaf on ornate columns, an enchanted rose under a glass cloche "
        "burning amber as the room's sole heart-light, candlelight pooling from "
        "flanking candelabra, crimson velvet on the balcony rail, rose petals mid-fall "
        "catching the flame, soft god-rays through faded gilt, crimson-and-gold "
        "split-tone, 85mm f/1.4 painterly bokeh"
    ),
    "black-rose": (
        "a nocturnal Oakland waterfront rose garden at low tide — rows of black and "
        "white roses silver-wet with rain, cold silver moonlight raking from "
        "camera-right, rain suspended mid-air as fine platinum threads, the Bay "
        "Bridge a distant rain-blurred ice-blue span across dark water, wet stone "
        "underfoot mirroring the subject, monochrome platinum-charcoal grade, "
        "85mm f/1.8 painterly depth"
    ),
    "signature": (
        "the rooftop of a Deep East Oakland low-rise at 4 a.m. — raw poured concrete "
        "parapet as foreground texture, the Bay Bridge strung amber across the water "
        "dissolving into marine-layer haze, warm golden key from camera-left at 45 "
        "degrees raking the model, faint lens haze from damp pre-dawn air, 85mm "
        "portrait compression, honey-gold grade cooled slightly in the shadows for "
        "contrast lift, contact shadow anchored on bare concrete"
    ),
    "kids-capsule": (
        "a sunlit East Oakland neighborhood sidewalk on a Saturday morning — "
        "rose-gold light raking painted concrete steps from camera-left at a low "
        "angle, a mural soft-focused at frame-left, warm golden fill diffused by "
        "open shade, 50mm editorial lens feel, warm rose-gold grade held in the "
        "highlights with shadows pulled to a soft warm neutral, contact shadow "
        "grounded on painted concrete underfoot, unhurried open-air atmosphere"
    ),
}
DEFAULT_SCENE = "an Oakland concrete-luxury editorial setting with dramatic directional light"


def _garment_refs(sku: str, collection: str) -> list[references.ReferenceImage]:
    """Canonical front-only references for an on-model render.

    Includes: the garment photo/techflat; the brand LOGO close-up (so the model
    reproduces the EXACT emblem rather than hallucinating one — founder-reported
    logo drift when the logo ref was excluded); and a sport patch only when the
    SKU requires it (jerseys). Front-only (``include_back=False``) avoids the
    back-view / multi-panel collage failure. Raises ``MissingReferenceError``
    when no garment source exists — never silently substitutes.
    """
    refs = references.build_references(sku, collection, include_back=False)
    needs_patch = references.requires_patch(sku)
    keep = [
        r
        for r in refs
        if r.path.exists()
        and (r.kind in ("garment", "logo") or (r.kind == "patch" and needs_patch))
    ]
    if not any(r.kind == "garment" for r in keep):
        raise references.MissingReferenceError(f"no usable garment reference for {sku}")
    return keep


def _garment_paths(sku: str, collection: str) -> list[Path]:
    """Resolved reference image paths for an on-model render (garment + logo + patch)."""
    return [r.path for r in _garment_refs(sku, collection)]


def _resolve(sku: str, collection: str | None) -> tuple[str, str, str, str]:
    """Return (name, collection, scene_desc, placement) from the canonical catalog row.

    ``get_product_with_dossier`` hard-fails (KeyError for an unknown SKU,
    DossierMissingError for an un-authored dossier) — convert both to
    MissingReferenceError so ``main`` reports a clean ABORT, never a traceback.
    """
    try:
        row = get_product_with_dossier(sku)
    except (KeyError, DossierMissingError) as exc:
        raise references.MissingReferenceError(f"{sku}: {exc}") from exc
    name = (row.get("name") or sku).strip()
    coll = (collection or row.get("collection") or "").strip()
    scene_desc = COLLECTION_SCENE.get(coll, DEFAULT_SCENE)
    from skyyrose.elite_studio.logo_registry import LogoRegistry

    placement = LogoRegistry.load().prompt_instructions(
        sku, require_sizing=references.requires_patch(sku)
    )
    return name, coll, scene_desc, placement


def build_prompt(name: str, scene_desc: str, has_logo: bool = False, placement: str = "") -> str:
    """Lookbook 'worn, not floating' prompt — garment is the protagonist."""
    logo_clause = (
        " One of the reference images is a CLOSE-UP of the exact brand logo/emblem that is "
        "printed or embroidered ON this garment — reproduce that logo faithfully (correct "
        "letterforms, exact shape and colour) in its proper place on the garment. Do NOT "
        "invent or garble the lettering, do not add extra logos, and do not render the logo "
        "as a separate floating object."
        if has_logo
        else ""
    )
    placement_clause = f" {placement}" if placement else ""
    return (
        f"Full-body editorial fashion photograph of a model wearing this exact "
        f"{name}, worn naturally with realistic drape, fit, fabric folds and grounded "
        f"contact shadows. Reproduce the garment's exact design, colors, embroidery "
        f"and lettering from the reference image — do not invent, recolor or restyle "
        f"any part of the garment.{logo_clause}{placement_clause} The model stands in {scene_desc}. "
        f"The garment is the protagonist of the frame. Cinematic, photographic, ultra-detailed, 8k."
    )


def _generate_one(sku: str, scene: Path, collection: str | None, dest: Path) -> bytes:
    """Render one on-model lookbook image. Returns PNG bytes, writes to dest.

    Internal — callers must have already passed the cost gate (enforce_cap + --yes).
    """
    if not scene.exists():
        raise FileNotFoundError(f"scene image not found: {scene}")
    name, coll, scene_desc, placement = _resolve(sku, collection)
    refs = _garment_refs(sku, coll)
    image_paths = [r.path for r in refs] + [scene]  # garment+logo lead; scene = context
    has_logo = any(r.kind == "logo" for r in refs)
    prompt = build_prompt(name, scene_desc, has_logo, placement)
    data = OAIImageClient().edit(prompt=prompt, image_paths=image_paths)
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(data)
    return data


def _manifest(skus: list[str]) -> cost.CostManifest:
    entries = []
    for sku in skus:
        name, coll, _, _ = _resolve(sku, None)
        # Count the refs actually sent to the edit call (garment + logo + any
        # required patch) so the manifest matches the real API inputs.
        ref_count = len(_garment_paths(sku, coll))
        entries.append(cost.ManifestEntry(sku=sku, name=name, n_images=1, ref_count=ref_count))
    return cost.CostManifest(entries=entries)


def _run_batch(skus: list[str], scene: Path, collection: str | None, out_dir: Path) -> int:
    """Render each SKU on-model, tracking spend against the hard cap. Returns exit code."""
    tracker = cost.SpendTracker()
    failures = 0
    for sku in skus:
        safe_sku = re.sub(r"[^a-z0-9\-]", "", sku.lower())
        dest = out_dir / f"{safe_sku}-onmodel.png"
        if not tracker.can_afford(config.EST_COST_PER_IMAGE_USD):
            _log.error("STOP: spend cap $%.2f reached before %s", tracker.cap_usd, sku)
            break
        try:
            _log.info("[%s] rendering on-model ...", sku)
            data = _generate_one(sku, scene, collection, dest)
            tracker.add(config.EST_COST_PER_IMAGE_USD)
            _log.info("[%s] [ok] %s (%d KB)", sku, dest, len(data) // 1024)
        except openai.AuthenticationError:
            # Never log str(exc) — the OpenAI SDK echoes a partial key in it.
            _log.error("[%s] [fail] AuthenticationError: check %s", sku, config.API_KEY_ENV)
            failures += 1
            break  # every subsequent call fails identically
        except (references.MissingReferenceError, FileNotFoundError) as exc:
            _log.error("[%s] [fail] %s: %s", sku, type(exc).__name__, exc)
            failures += 1
        except openai.APIError as exc:  # noqa: BLE001 — surface, continue the batch
            # Suppress str(exc): OpenAI APIError messages may echo request details.
            failures += 1
            _log.error("[%s] [fail] %s: details suppressed", sku, type(exc).__name__)
        except Exception as exc:  # noqa: BLE001 — surface, continue the batch
            failures += 1
            _log.error("[%s] [fail] %s: %s", sku, type(exc).__name__, exc)
    _log.info("\nDone. spent ~$%.2f, %d failed -> %s", tracker.spent_usd, failures, out_dir)
    return 1 if failures else 0


def main(argv: list[str] | None = None) -> int:
    # Configure module logger: INFO → stdout, WARNING+ → stderr, format = message only.
    # This keeps CLI output byte-identical to the original print() calls.
    _fmt = logging.Formatter("%(message)s")
    _stdout_h = logging.StreamHandler(sys.stdout)
    _stdout_h.setLevel(logging.DEBUG)
    _stdout_h.setFormatter(_fmt)
    _stdout_h.addFilter(lambda r: r.levelno < logging.WARNING)
    _stderr_h = logging.StreamHandler(sys.stderr)
    _stderr_h.setLevel(logging.WARNING)
    _stderr_h.setFormatter(_fmt)
    _log.addHandler(_stdout_h)
    _log.addHandler(_stderr_h)
    _log.setLevel(logging.DEBUG)
    # Prevent double-emission if a root handler is already configured.
    _log.propagate = False

    ap = argparse.ArgumentParser(description="On-model lookbook (gpt-image-2 edit)")
    ap.add_argument("mode", choices=["plan", "generate"])
    ap.add_argument("--sku", action="append", required=True, help="SKU(s) to render")
    ap.add_argument("--scene", type=Path, required=True, help="styled backdrop image")
    ap.add_argument("--collection", default=None, help="override collection (else from catalog)")
    ap.add_argument("--out", type=Path, default=config.OUTPUT_DIR / "_lookbook" / "onmodel")
    ap.add_argument("--yes", action="store_true", help="confirm the paid run (generate)")
    args = ap.parse_args(argv)

    # Anchor --out inside the canonical output dir — a traversal --out must not
    # let a write land outside renders/.
    out_dir = Path(args.out).resolve()
    if not out_dir.is_relative_to(config.OUTPUT_DIR.resolve()):
        _log.error("ABORT: --out must be inside %s", config.OUTPUT_DIR)
        return 2

    if not args.scene.exists():
        _log.error("ABORT: scene not found: %s", args.scene)
        return 2

    try:
        manifest = _manifest(args.sku)
    except references.MissingReferenceError as exc:
        _log.error("ABORT: %s", exc)
        return 2

    _log.info("%s", cost.format_manifest(manifest))
    if args.mode == "plan":
        return 0

    try:
        cost.enforce_cap(manifest)
    except cost.CostCapExceeded as exc:
        _log.error("ABORT: %s", exc)
        return 2
    if not args.yes:
        _log.error("\nRefusing to spend without --yes (STOP-AND-SHOW gate).")
        return 3
    if not config.api_key_present():
        _log.error("ABORT: %s not set (add to .env.hf)", config.API_KEY_ENV)
        return 2

    return _run_batch(args.sku, args.scene, args.collection, out_dir)


if __name__ == "__main__":
    raise SystemExit(main())
