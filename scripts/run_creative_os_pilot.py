#!/usr/bin/env python3
"""Reproducible local prototype assets and entry point for the adopted internal pilot."""

from __future__ import annotations

import argparse
import hashlib
import io
import json
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

from skyyrose.core.context_resolver import ResolutionRequest, SourceReference
from skyyrose.core.creative_job import JobPlan
from skyyrose.core.paths import REPO_ROOT, THEME_ROOT
from skyyrose.core.product import get_product
from skyyrose.elite_studio.creative.editorial import Direction
from skyyrose.elite_studio.creative.local_composite import AssetRef, LocalCompositeGrant, Placement
from skyyrose.elite_studio.creative.runner import run_editorial
from skyyrose.elite_studio.creative.skyyrose_adapter import SkyyRoseEditorialAdapter


def immutable_bytes(path: Path, data: bytes) -> None:
    if path.exists():
        if path.read_bytes() != data:
            raise ValueError(f"Existing input/evidence differs; preserve it: {path}")
        return
    with path.open("xb") as stream:
        stream.write(data)


def save_png(image: Image.Image, path: Path) -> None:
    stream = io.BytesIO()
    image.save(stream, format="PNG")
    immutable_bytes(path, stream.getvalue())


def ref(path: Path) -> dict:
    return {
        "path": str(path.relative_to(REPO_ROOT)),
        "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
    }


def assets(directory: Path, revision: int = 1) -> tuple[Path, list[Path]]:
    directory.mkdir(parents=True, exist_ok=True)
    # Manually authored conservative boundary; no thresholding of white garment trim.
    points = [
        (633, 142),
        (660, 146),
        (710, 164),
        (775, 163),
        (835, 145),
        (880, 128),
        (950, 141),
        (1040, 170),
        (1170, 204),
        (1300, 253),
        (1420, 300),
        (1450, 330),
        (1595, 701),
        (1565, 760),
        (1480, 850),
        (1390, 980),
        (1350, 1030),
        (1330, 1130),
        (1290, 1170),
        (1270, 1260),
        (1250, 1368),
        (1200, 1360),
        (1100, 1325),
        (900, 1320),
        (700, 1330),
        (490, 1368),
        (460, 1320),
        (425, 1250),
        (390, 1160),
        (355, 1090),
        (330, 1070),
        (240, 978),
        (155, 860),
        (87, 753),
        (72, 713),
        (72, 678),
        (123, 541),
        (178, 376),
        (195, 355),
        (280, 310),
        (380, 270),
        (490, 228),
        (580, 205),
        (615, 175),
    ]
    if revision >= 2:
        points[-4:] = [(380, 250), (490, 201), (580, 172), (630, 143)]
    mask = Image.new("L", (2000, 1800), 0)
    ImageDraw.Draw(mask).polygon(
        [(round(x * 2000 / 1663), round(y * 1800 / 1497)) for x, y in points], fill=255
    )
    if revision == 3:
        # Final conservative photographic-plate mode: preserve the ENTIRE source,
        # including all white trim and the native background. No cutout claim.
        mask = Image.new("L", (2000, 1800), 255)
    mask_path = directory / "front-mask.png"
    save_png(mask, mask_path)
    n = 1800
    y, x = np.mgrid[:n, :n]
    rng = np.random.default_rng(240924)
    noise = rng.normal(0, 1, (n, n))
    paths = []
    for k in range(3):
        if k == 0:
            base = np.array([203, 204, 192])
            texture = noise * 3 + 6 * np.sin(x / 200) + 4 * np.cos(y / 93)
        elif k == 1:
            base = np.array([211, 188, 149])
            texture = noise * 2 + 3 * np.sin(x * np.pi / 3) + 3 * np.sin(y * np.pi / 4)
        else:
            base = np.array([210, 224, 218])
            texture = noise * 1.8 + 2 * np.sin(x / 71) * np.cos(y / 44)
        light = 12 * (1 - (x + y) / (2 * n))
        arr = np.clip(base[None, None, :] + (texture + light)[:, :, None], 0, 255).astype("uint8")
        im = Image.fromarray(arr)
        d = ImageDraw.Draw(im)
        if k == 0:
            # Sunlit pavement seams, narrow planted verge and organic leaf shadow.
            d.polygon([(0, 0), (185, 0), (130, 1800), (0, 1800)], fill=(101, 117, 74))
            for a in range(190):
                px = int(rng.integers(0, 140))
                py = int(rng.integers(0, n))
                d.line(
                    [(px, py), (px + int(rng.integers(-35, 35)), py - int(rng.integers(18, 90)))],
                    fill=(125 + int(rng.integers(0, 50)), 143, 79),
                    width=2,
                )
            d.line([(180, 0), (123, 1800)], fill=(121, 125, 115), width=8)
            d.line([(150, 235), (1800, 430)], fill=(154, 155, 144), width=4)
            d.line([(135, 1520), (1800, 1640)], fill=(149, 152, 140), width=5)
            shadow = Image.new("RGBA", (n, n))
            sd = ImageDraw.Draw(shadow)
            for cx, cy, rx, ry in [
                (1500, 180, 180, 55),
                (1660, 260, 160, 45),
                (1420, 85, 120, 40),
                (1740, 410, 130, 50),
            ]:
                sd.ellipse((cx - rx, cy - ry, cx + rx, cy + ry), fill=(45, 67, 48, 50))
            im = Image.alpha_composite(
                im.convert("RGBA"), shadow.filter(ImageFilter.GaussianBlur(18))
            ).convert("RGB")
        elif k == 1:
            d.polygon([(0, 1390), (440, 1620), (700, 1800), (0, 1800)], fill=(188, 158, 113))
            d.line([(0, 1390), (440, 1620), (700, 1800)], fill=(239, 218, 176), width=10)
            d.polygon([(1500, 0), (1800, 0), (1800, 470)], fill=(233, 216, 180))
            for i in range(12):
                d.arc(
                    (1120 + i * 3, 1390 + i * 2, 1630 + i * 3, 1720 + i * 2),
                    10,
                    300,
                    fill=(137, 103, 62),
                    width=2,
                )
            for yy in range(65, 245, 28):
                d.line([(95, yy), (310, yy + 32)], fill=(177, 145, 103), width=2)
        else:
            wave = np.sin(y / 30 + np.sin(x / 63)) * np.cos(x / 38 + y / 95)
            water = np.clip(
                np.array([77, 142, 145])[None, None, :] + (wave * 17 + noise)[:, :, None], 0, 255
            ).astype("uint8")
            im.paste(Image.fromarray(water).crop((0, 0, 360, n)), (0, 0))
            d = ImageDraw.Draw(im)
            d.polygon([(320, 0), (385, 0), (290, 1800), (220, 1800)], fill=(239, 234, 212))
            d.line([(385, 0), (290, 1800)], fill=(156, 180, 170), width=10)
            for a in range(400):
                xx = int(rng.integers(430, 1800))
                yy = int(rng.integers(0, 1800))
                rr = int(rng.integers(1, 6))
                d.ellipse((xx, yy, xx + rr, yy + rr), fill=(185, 204, 194))
            d.line([(370, 220), (1800, 140)], fill=(244, 245, 226), width=18)
        path = directory / f"environment-{chr(65+k)}.png"
        save_png(im, path)
        paths.append(path)
    return mask_path, paths


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--output", type=Path, required=True)
    p.add_argument("--revision", type=int, choices=[1, 2, 3], default=1)
    p.add_argument(
        "--authorize-local",
        action="store_true",
        help="Trusted operator invocation under adopted owner handoff; no provider permission",
    )
    args = p.parse_args()
    if not args.authorize_local:
        p.error("Explicit local-action invocation required")
    output = args.output.resolve()
    if not output.is_relative_to(REPO_ROOT):
        p.error("Output must be inside this reconstructed repository")
    mask, backgrounds = assets(output / f"inputs-r{args.revision}", args.revision)
    record = get_product("br-001")
    source = THEME_ROOT / record["images"]["packshot"]["path"]
    data = json.loads((REPO_ROOT / "docs/examples/context-resolver-abstract.json").read_text())
    data.update(
        job_id="br-001-daylight-local-v1",
        objective="Three materially distinct front-source editorial prototypes",
        collection_context="black-rose",
        representation_mode="EXACT_PRODUCT",
        production_method="SOURCE_COMPOSITE",
        products=[
            {
                "sku": "br-001",
                "required_views": ["packshot"],
                "required_details": ["front_treatment", "preorder"],
            }
        ],
    )
    data["absence_reasons"].pop("collection_context")
    data["content_intent"].update(
        representation_mode="EXACT_PRODUCT", shot_role="PRODUCT_EDITORIAL"
    )
    request = ResolutionRequest.model_validate(data)
    plan = JobPlan.model_validate(
        dict(
            deliverables=["A", "B", "C"],
            experience_outcome="Relate to resilience, authorship, and emotional clarity",
            authored_meaning="Black Rose symbolism translated into daylight material experiences",
            production_method={
                "technique": "SOURCE_COMPOSITE",
                "rationale": "Protect complete photographed front; no disputed physical axis used",
                "inputs": [ref(source)],
                "feasibility_evidence": [ref(REPO_ROOT / "docs/creative-os/PILOT.md")],
            },
            success_evidence=["Visible fidelity and technical checks for each final PNG"],
            channel_requirements=["Internal 1800x1800 review only"],
            approval_requirements=["Owner review of creative direction; no publication"],
            novelty_dimensions=[
                "daylight",
                "material environment",
                "authored emotional hypothesis",
            ],
            major_initiative=False,
            accessibility_applicable=False,
            accessibility_reason="Internal still comparison with companion descriptions",
            commerce_applicable=False,
            commerce_reason="No offer, transaction, or commerce placement",
            open_issues=[],
        )
    )
    adapter = SkyyRoseEditorialAdapter(
        request,
        plan,
        "packshot",
        "front",
        SourceReference(**ref(REPO_ROOT / "docs/creative-os/source-review.json")),
    )
    hypotheses = [
        (
            "Concrete / Return",
            "Resilience reads as growth through ordinary daylight surfaces",
            "Concrete, planted verge and dappled daylight",
            "Centered front on pavement; planted margin",
            "Steadiness and renewal",
        ),
        (
            "Cloth / Continuity",
            "Authorship is tangible through making and inherited material",
            "Woven fibers, folded canvas and thread",
            "Front held within diagonal fabric folds",
            "Care, continuity and belonging",
        ),
        (
            "Tidal / Clarity",
            "Emotional release can be expressed through clear daylight rhythm",
            "Water rhythm and pale mineral surface",
            "Front on mineral platform next to water",
            "Space, release and clarity",
        ),
    ]
    directions = []
    for i, (name, hyp, env, comp, emotion) in enumerate(hypotheses):
        directions.append(
            Direction(
                chr(65 + i),
                hyp,
                name,
                env,
                comp,
                "Unaltered front-facing product anchor",
                emotion,
                "Distinct material hypothesis relative to limited staging corpus",
                "Deliberate full photographic plate; not a seamless physical placement",
                AssetRef(**ref(backgrounds[i])),
                AssetRef(**ref(mask)),
                Placement(240, 330, 0.66),
            )
        )
    grant = LocalCompositeGrant(
        request.job_id,
        ref(source)["sha256"],
        str(output),
        "Owner: start implementing; adopted revised handoff 2026-09-24; internal local composites only",
    )
    result = run_editorial(
        adapter, directions, root=REPO_ROOT, output_dir=output / f"run-{args.revision}", grant=grant
    )
    immutable_bytes(
        output / f"run-{args.revision}" / "request.json", request.model_dump_json(indent=2).encode()
    )
    immutable_bytes(
        output / f"run-{args.revision}" / "plan.json", plan.model_dump_json(indent=2).encode()
    )
    print(
        json.dumps(
            {"pilot": result["pilot"], "output": str(output / f"run-{args.revision}")}, indent=2
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
