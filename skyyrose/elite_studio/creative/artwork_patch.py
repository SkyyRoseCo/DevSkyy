"""Local, source-bound artwork repair; no generation or publication capability.

Art masks require independent coverage review. A validated transform proves
provenance and edit boundaries, never physical correctness of fabric wrapping.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass
from pathlib import Path

import numpy as np
from PIL import Image, PngImagePlugin

from .local_composite import AssetRef, CompositeError, _path, _read


@dataclass(frozen=True)
class ArtworkPatch:
    name: str
    source: AssetRef
    crop: tuple[int, int, int, int]
    source_mask: AssetRef
    repair_mask: AssetRef
    cleanup_mask: AssetRef
    donor_offset: tuple[int, int]
    quad: tuple[tuple[float, float], ...]
    wrap_degrees: float = 0
    cleanup_mode: str = "clone"
    light_gain: float = 1
    light_contrast: float = 0
    split_donor_mask: AssetRef | None = None
    split_donor_offset: tuple[int, int] = (0, 0)
    fabric_mask: AssetRef | None = None


@dataclass(frozen=True)
class ArtworkRepair:
    job_id: str
    target: AssetRef
    patches: tuple[ArtworkPatch, ...]
    output: str


@dataclass(frozen=True)
class ArtworkGrant:
    request_sha256: str
    output_root: str
    approval_reference: str


def identity(request: ArtworkRepair) -> str:
    return hashlib.sha256(
        json.dumps(asdict(request), sort_keys=True, separators=(",", ":"), allow_nan=False).encode()
    ).hexdigest()


def _mask(root: Path, ref: AssetRef, size: tuple[int, int]) -> np.ndarray:
    im, _ = _read(root, ref)
    if im.mode != "L" or im.size != size or im.getbbox() is None:
        raise CompositeError("Nonempty L mask with exact bound dimensions required")
    return np.asarray(im, dtype=np.uint8)


def _prepare(request: ArtworkRepair, root: Path):
    # OpenCV is an optional local execution dependency, never installed here.
    import cv2

    base, metadata = _read(root, request.target)
    if metadata["icc_sha256"] is not None:
        raise CompositeError("Normalize target color profile before binding its identity")
    if base.mode != "RGB" or not request.job_id or not 1 <= len(request.patches) <= 6:
        raise CompositeError("Require RGB target and one to six named artwork patches")
    if len({p.name for p in request.patches}) != len(request.patches):
        raise CompositeError("Patch names must be unique")
    width, height = base.size
    prepared = []
    occupied = np.zeros((height, width), dtype=bool)
    for patch in request.patches:
        source, _ = _read(root, patch.source)
        left, top, right, bottom = patch.crop
        if source.mode != "RGB" or not (
            0 <= left < right <= source.width and 0 <= top < bottom <= source.height
        ):
            raise CompositeError("Source crop must fit bound RGB original")
        size = (right - left, bottom - top)
        alpha = _mask(root, patch.source_mask, size)
        region = _mask(root, patch.repair_mask, base.size)
        cleanup = _mask(root, patch.cleanup_mask, base.size)
        if np.any((region != 0) & (region != 255)):
            raise CompositeError("Repair boundary must be binary")
        inside = region == 255
        if inside.sum() > width * height * 0.015 or np.any(occupied & inside):
            raise CompositeError("Repair too broad or overlapping another repair")
        occupied |= inside
        if np.any((cleanup > 0) & ~inside):
            raise CompositeError("Cleanup escapes approved repair region")
        if patch.cleanup_mode not in {"clone", "local_interpolation", "fabric_interpolation"}:
            raise CompositeError("Unsupported fabric cleanup operation")
        if patch.cleanup_mode == "fabric_interpolation" and patch.fabric_mask is None:
            raise CompositeError("Fabric-constrained interpolation requires bound fabric domain")
        if patch.fabric_mask:
            fabric = _mask(root, patch.fabric_mask, base.size)
            if np.any((fabric != 0) & (fabric != 255)) or np.any((cleanup > 0) & (fabric == 0)):
                raise CompositeError("Cleanup escapes semantic fabric domain")
        if patch.split_donor_mask:
            if patch.cleanup_mode not in {"clone", "fabric_interpolation"}:
                raise CompositeError("Separate fabric-panel donors require compatible cleanup mode")
            split = _mask(root, patch.split_donor_mask, base.size)
            sy, sx = np.where((cleanup > 0) & (split > 0))
            ox, oy = patch.split_donor_offset
            if (
                type(ox) is not int
                or type(oy) is not int
                or np.any(sx + ox < 0)
                or np.any(sx + ox >= width)
                or np.any(sy + oy < 0)
                or np.any(sy + oy >= height)
            ):
                raise CompositeError("Separate panel donor escapes bound source")
        quad = np.asarray(patch.quad, dtype=np.float32)
        if quad.shape != (4, 2) or not np.isfinite(quad).all():
            raise CompositeError("Four finite clockwise screen corners required")
        if (
            np.any(quad[:, 0] < 0)
            or np.any(quad[:, 0] >= width)
            or np.any(quad[:, 1] < 0)
            or np.any(quad[:, 1] >= height)
        ):
            raise CompositeError("Artwork transform clips target")
        edges = np.roll(quad, -1, axis=0) - quad
        turns = (
            edges[:, 0] * np.roll(edges, -1, axis=0)[:, 1]
            - edges[:, 1] * np.roll(edges, -1, axis=0)[:, 0]
        )
        if not np.all(turns > 1) or abs(cv2.contourArea(quad)) < 4:
            raise CompositeError("Mirrored, singular or self-crossing artwork transform")
        if not np.isfinite(patch.wrap_degrees) or not 0 <= patch.wrap_degrees <= 120:
            raise CompositeError("Declared symmetric cylindrical projection must be 0..120 degrees")
        if not (0.7 <= patch.light_gain <= 1.05 and 0 <= patch.light_contrast <= 0.4):
            raise CompositeError("Lighting treatment exceeds bounded source-derived range")
        # Premultiply before every resampling operation: RGB hidden behind a
        # transparent source pixel must never bleed into artwork edges.
        rgb = np.asarray(source.crop(patch.crop), dtype=np.float32) * (
            alpha[:, :, None].astype(np.float32) / 255
        )
        alpha = alpha.astype(np.float32)
        if patch.wrap_degrees:
            # Declared geometric compression of the complete source, not a crop.
            angle = np.deg2rad(patch.wrap_degrees)
            u = np.linspace(-1, 1, size[0], dtype=np.float32)
            u = np.arcsin(u * np.sin(angle / 2)) / angle + 0.5
            map_x = np.tile(u * (size[0] - 1), (size[1], 1)).astype(np.float32)
            map_y = np.tile(np.arange(size[1], dtype=np.float32)[:, None], (1, size[0]))
            rgb = cv2.remap(rgb, map_x, map_y, cv2.INTER_CUBIC)
            alpha = cv2.remap(alpha, map_x, map_y, cv2.INTER_CUBIC)
        source_corners = np.array(
            [[0, 0], [size[0] - 1, 0], [size[0] - 1, size[1] - 1], [0, size[1] - 1]], np.float32
        )
        matrix = cv2.getPerspectiveTransform(source_corners, quad)
        if not np.isfinite(matrix).all() or abs(np.linalg.det(matrix)) < 1e-10:
            raise CompositeError("Singular artwork transform")
        # Supersample only the small target region; otherwise reducing a 1400px
        # ring into a 40px sleeve aliases its letters into disconnected specks.
        x0 = max(0, int(np.floor(quad[:, 0].min())) - 3)
        y0 = max(0, int(np.floor(quad[:, 1].min())) - 3)
        x1 = min(width, int(np.ceil(quad[:, 0].max())) + 4)
        y1 = min(height, int(np.ceil(quad[:, 1].max())) + 4)
        local_quad = (quad - np.array([x0, y0], np.float32)) * 8
        local_matrix = cv2.getPerspectiveTransform(source_corners, local_quad)
        local_size = ((x1 - x0) * 8, (y1 - y0) * 8)
        color_hi = cv2.warpPerspective(rgb, local_matrix, local_size, flags=cv2.INTER_CUBIC)
        alpha_hi = cv2.warpPerspective(alpha, local_matrix, local_size, flags=cv2.INTER_CUBIC)
        transformed = np.zeros((height, width, 3), np.float32)
        transformed_alpha = np.zeros((height, width), np.float32)
        transformed[y0:y1, x0:x1] = cv2.resize(
            color_hi, (x1 - x0, y1 - y0), interpolation=cv2.INTER_AREA
        )
        transformed_alpha[y0:y1, x0:x1] = cv2.resize(
            alpha_hi, (x1 - x0, y1 - y0), interpolation=cv2.INTER_AREA
        )
        transformed_alpha = np.clip(np.rint(transformed_alpha), 0, 255).astype(np.uint8)
        transformed = np.clip(transformed, 0, transformed_alpha[:, :, None].astype(np.float32))
        if not np.any(transformed_alpha == 255) or np.any((transformed_alpha > 0) & ~inside):
            raise CompositeError("Whole transformed artwork does not fit repair mask")
        yy, xx = np.where(cleanup > 0)
        dx, dy = patch.donor_offset
        if type(dx) is not int or type(dy) is not int or not len(xx):
            raise CompositeError("Nonempty cleanup and integer donor translation required")
        if (
            np.any(xx + dx < 0)
            or np.any(xx + dx >= width)
            or np.any(yy + dy < 0)
            or np.any(yy + dy >= height)
        ):
            raise CompositeError("Same-target donor escapes source image")
        prepared.append((patch, region, cleanup, transformed, transformed_alpha))
    return base, prepared, occupied


def _render(request: ArtworkRepair, root: Path):
    import cv2

    base, prepared, occupied = _prepare(request, root)
    original = np.asarray(base, dtype=np.uint32)
    cleaned = original.copy()
    for patch, region, cleanup, _, _ in prepared:
        yy, xx = np.where(cleanup > 0)
        dx, dy = patch.donor_offset
        weight = cleanup[yy, xx, None].astype(np.uint32)
        if patch.cleanup_mode == "fabric_interpolation":
            fabric = _mask(root, patch.fabric_mask, base.size) > 0
            ry, rx = np.where(region > 0)
            y0, y1 = max(0, int(ry.min()) - 24), min(base.height, int(ry.max()) + 25)
            x0, x1 = max(0, int(rx.min()) - 24), min(base.width, int(rx.max()) + 25)
            area = original[y0:y1, x0:x1].astype(np.uint8)
            pending = cleanup[y0:y1, x0:x1] > 0
            domain = fabric[y0:y1, x0:x1]
            panels = [np.full(domain.shape, 255, np.uint32)]
            if patch.split_donor_mask:
                split = _mask(root, patch.split_donor_mask, base.size)[y0:y1, x0:x1].astype(
                    np.uint32
                )
                panels = [255 - split, split]
            substrate = original.astype(np.uint32).copy()
            mixed = np.zeros_like(area, dtype=np.uint32)
            for coverage in panels:
                todo = pending & (coverage > 0)
                if not todo.any():
                    continue
                # Partial seam pixels receive both separately solved panels;
                # only fully owned, clean pixels can supply either solution.
                panel = coverage == 255
                good = domain & panel & ~pending
                if good.sum() < 8:
                    raise CompositeError("Insufficient same-panel fabric samples")
                # Extend ONLY known clean same-panel fabric across the temporary
                # working boundary, preventing skin/background/other-panel bleed.
                _, labels = cv2.distanceTransformWithLabels(
                    (~good).astype(np.uint8), cv2.DIST_L2, 5, labelType=cv2.DIST_LABEL_PIXEL
                )
                lookup = area[good]
                work = area.copy()
                outside = ~(domain & panel)
                work[outside] = lookup[labels[outside] - 1]
                interpolated = cv2.inpaint(work, todo.astype(np.uint8), 3, cv2.INPAINT_TELEA)
                mixed[todo] += interpolated[todo].astype(np.uint32) * coverage[todo, None]
            destination = substrate[y0:y1, x0:x1]
            destination[pending] = (mixed[pending] + 127) // 255
            donor = substrate[yy, xx]
        elif patch.cleanup_mode == "local_interpolation":
            # Deterministic neighboring-fabric interpolation, no generative model.
            substrate = cv2.inpaint(
                original.astype(np.uint8), (cleanup > 0).astype(np.uint8), 3, cv2.INPAINT_TELEA
            ).astype(np.uint32)
            donor = substrate[yy, xx]
        else:
            donor = original[yy + dy, xx + dx].copy()
            if patch.split_donor_mask:
                split = _mask(root, patch.split_donor_mask, base.size)[yy, xx, None].astype(
                    np.uint32
                )
                ox, oy = patch.split_donor_offset
                active = split[:, 0] > 0
                alternate = donor.copy()
                alternate[active] = original[yy[active] + oy, xx[active] + ox]
                donor = (donor * (255 - split) + alternate * split + 127) // 255
        cleaned[yy, xx] = (donor * weight + original[yy, xx] * (255 - weight) + 127) // 255
    result = cleaned.copy()
    for patch, _, _, rgb, alpha in prepared:
        if patch.light_gain != 1 or patch.light_contrast:
            illumination = cv2.GaussianBlur(
                cv2.cvtColor(cleaned.astype(np.uint8), cv2.COLOR_RGB2GRAY).astype(np.float32),
                (0, 0),
                2,
            )
            median = float(np.median(illumination[alpha > 0]))
            if median <= 0:
                raise CompositeError("Local fabric illumination cannot be established")
            gain = patch.light_gain * np.clip(
                1 + patch.light_contrast * (illumination / median - 1), 0.8, 1.15
            )
            rgb = rgb * gain[:, :, None]
        rgb = np.minimum(np.clip(np.rint(rgb), 0, 255), alpha[:, :, None]).astype(np.uint32)
        weight = alpha[:, :, None].astype(np.uint32)
        result = (rgb * 255 + result * (255 - weight) + 127) // 255
    if np.any(result[~occupied] != original[~occupied]):
        raise CompositeError("Pixels outside authorized artwork regions changed")
    return result.astype(np.uint8), cleaned.astype(np.uint8), occupied


def verify(request: ArtworkRepair, receipt: dict, *, root: Path, grant: ArtworkGrant) -> dict:
    expected, expected_cleaned, occupied = _render(request, root)
    path = _path(root, request.output)
    raw = path.read_bytes()
    with Image.open(path) as im:
        actual = np.asarray(im.convert("RGB"))
        technical = (
            im.format == "PNG"
            and im.mode == "RGB"
            and im.size == (expected.shape[1], expected.shape[0])
        )
    original, _ = _read(root, request.target)
    matches = actual.shape == expected.shape and np.array_equal(actual, expected)
    outside = actual.shape == expected.shape and np.array_equal(
        actual[~occupied], np.asarray(original)[~occupied]
    )
    integrity = (
        receipt.get("request_sha256") == identity(request)
        and receipt.get("sha256") == hashlib.sha256(raw).hexdigest()
        and json.dumps(receipt.get("request"), sort_keys=True)
        == json.dumps(asdict(request), sort_keys=True)
        and receipt.get("producer_sha256")
        == hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
        and receipt.get("publication_authorized") is False
        and receipt.get("provider_authorized") is False
        and receipt.get("visual_review") == "REQUIRED"
        and isinstance(grant, ArtworkGrant)
        and grant.request_sha256 == identity(request)
        and bool(grant.approval_reference.strip())
        and receipt.get("authority") == asdict(grant)
        and path.is_relative_to(_path(root, grant.output_root))
    )
    cleaned_path = _path(root, str(Path(request.output).with_suffix(".cleaned.png")))
    try:
        with Image.open(cleaned_path) as im:
            cleaned_ok = (
                im.mode == "RGB"
                and im.format == "PNG"
                and np.array_equal(np.asarray(im), expected_cleaned)
            )
        cleaned_ok = (
            cleaned_ok
            and receipt.get("cleaned_path") == str(cleaned_path.relative_to(root.resolve()))
            and receipt.get("cleaned_sha256")
            == hashlib.sha256(cleaned_path.read_bytes()).hexdigest()
        )
    except OSError:
        cleaned_ok = False
    return {
        "status": (
            "PASS" if technical and matches and outside and integrity and cleaned_ok else "FAIL"
        ),
        "technical": technical,
        "reproduced_pixels": matches,
        "outside_regions_unchanged": outside,
        "request_and_artifact_identity": integrity,
        "cleaned_intermediate": cleaned_ok,
        "limitation": "Input hashes and mask/transform preservation, not visual source-mask completeness or physical fabric conformity; independent review required.",
    }


def repair(request: ArtworkRepair, *, root: Path, grant: ArtworkGrant) -> dict:
    if (
        not isinstance(grant, ArtworkGrant)
        or grant.request_sha256 != identity(request)
        or not grant.approval_reference.strip()
    ):
        raise CompositeError("Exact request-scoped local artwork authority required")
    output = _path(root, request.output)
    if output.suffix != ".png" or not output.is_relative_to(_path(root, grant.output_root)):
        raise CompositeError("Lossless output must fit granted root")
    sidecar = output.with_suffix(".receipt.json")
    cleaned_path = output.with_suffix(".cleaned.png")
    if any(p.exists() for p in [output, sidecar, cleaned_path]):
        raise CompositeError("Immutable output already exists; use new identity")
    pixels, cleaned, _ = _render(request, root)
    output.parent.mkdir(parents=True, exist_ok=True)
    info = PngImagePlugin.PngInfo()
    info.add(b"sRGB", b"\x00")
    for path, array in [(cleaned_path, cleaned), (output, pixels)]:
        with path.open("xb") as stream:
            Image.fromarray(array).save(stream, format="PNG", pnginfo=info)
    receipt = {
        "request": asdict(request),
        "request_sha256": identity(request),
        "sha256": hashlib.sha256(output.read_bytes()).hexdigest(),
        "producer_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "authority": asdict(grant),
        "cleaned_path": str(cleaned_path.relative_to(root.resolve())),
        "cleaned_sha256": hashlib.sha256(cleaned_path.read_bytes()).hexdigest(),
        "publication_authorized": False,
        "provider_authorized": False,
        "visual_review": "REQUIRED",
    }
    with sidecar.open("x") as stream:
        json.dump(receipt, stream, indent=2)
        stream.write("\n")
    if verify(request, receipt, root=root, grant=grant)["status"] != "PASS":
        raise CompositeError("New local artwork repair verification failed")
    return receipt
