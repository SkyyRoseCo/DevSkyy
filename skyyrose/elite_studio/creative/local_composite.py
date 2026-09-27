"""Source-locked local composition with scoped grants and independent pixel checks.

This adapter proves preservation of the supplied mask, not correctness of source
identity, mask coverage, physical garment facts, or permission beyond local output.
The trusted caller injects a grant from its actual approval record, never a brief.
"""

from __future__ import annotations

import hashlib
import io
import json
import math
import os
import zlib
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import numpy as np
from PIL import Image, ImageCms, PngImagePlugin, __version__ as pillow_version


class CompositeError(ValueError):
    """Fail-closed input, authority, identity or preservation failure."""


@dataclass(frozen=True)
class AssetRef:
    path: str
    sha256: str


@dataclass(frozen=True)
class Placement:
    x: int
    y: int
    scale: float = 1.0

    def __post_init__(self) -> None:
        if type(self.x) is not int or type(self.y) is not int:
            raise CompositeError("Placement requires integer translation")
        if isinstance(self.scale, bool) or not math.isfinite(self.scale) or self.scale <= 0:
            raise CompositeError("Uniform scale must be finite and positive")


@dataclass(frozen=True)
class CompositeRequest:
    job_id: str
    source: AssetRef
    mask: AssetRef
    background: AssetRef
    placement: Placement
    output_path: str


@dataclass(frozen=True)
class LocalCompositeGrant:
    """Trusted caller capability; no construction from untrusted job dictionaries."""

    job_id: str
    source_sha256: str
    output_root: str
    approval_reference: str
    action: str = "local_composite"


def _digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _canonical(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()


def _path(root: Path, path: str) -> Path:
    candidate = (root / path).resolve()
    if not candidate.is_relative_to(root.resolve()):
        raise CompositeError("Asset/output path escapes allowed root")
    return candidate


def _read(root: Path, asset: AssetRef) -> tuple[Image.Image, dict]:
    data = _path(root, asset.path).read_bytes()
    if _digest(data) != asset.sha256:
        raise CompositeError(f"Source identity changed: {asset.path}")
    with Image.open(io.BytesIO(data)) as image:
        image.load()
        if getattr(image, "n_frames", 1) != 1:
            raise CompositeError("Only single-frame input assets are supported")
        orientation = image.getexif().get(274, 1)
        if orientation != 1:
            raise CompositeError("Source orientation must be normalized before binding")
        metadata = {
            "sha256": asset.sha256,
            "path": asset.path,
            "mode": image.mode,
            "dimensions": list(image.size),
            "orientation": orientation,
            "icc_sha256": (
                _digest(image.info["icc_profile"]) if image.info.get("icc_profile") else None
            ),
        }
        result = image.copy()
        if image.mode == "RGBA":
            if image.getchannel("A").getextrema() != (255, 255):
                raise CompositeError(
                    "RGBA inputs must be fully opaque; transparency is defined by the bound L mask"
                )
            result = image.convert("RGB")
        if result.mode == "RGB" and image.info.get("icc_profile"):
            result = ImageCms.profileToProfile(
                result,
                ImageCms.ImageCmsProfile(io.BytesIO(image.info["icc_profile"])),
                ImageCms.createProfile("sRGB"),
                outputMode="RGB",
            )
            metadata["color_conversion"] = "embedded ICC to sRGB"
        else:
            metadata["color_conversion"] = "none; untagged RGB interpreted as sRGB"
    return result, metadata


def _inputs(
    request: CompositeRequest, root: Path
) -> tuple[Image.Image, Image.Image, Image.Image, dict]:
    if not request.job_id.strip():
        raise CompositeError("A job identity is required")
    source, source_meta = _read(root, request.source)
    mask, mask_meta = _read(root, request.mask)
    background, background_meta = _read(root, request.background)
    if source.mode != "RGB" or background.mode != "RGB" or mask.mode != "L":
        raise CompositeError("Require RGB source/background and L mask")
    if source.size != mask.size:
        raise CompositeError("Mask dimensions must equal full source dimensions")
    if mask.getbbox() is None or mask.getextrema()[1] != 255:
        raise CompositeError("Mask must contain a nonempty opaque protected interior")
    width = round(source.width * request.placement.scale)
    height = round(source.height * request.placement.scale)
    if min(width, height) < 1:
        raise CompositeError("Scale produces empty layer")
    x, y = request.placement.x, request.placement.y
    if x < 0 or y < 0 or x + width > background.width or y + height > background.height:
        raise CompositeError("Complete source layer must fit without clipping")
    metadata = {
        "runtime": {"pillow": pillow_version, "numpy": np.__version__},
        "source": source_meta,
        "mask": mask_meta,
        "background": background_meta,
        "transform": {
            "matrix": [[request.placement.scale, 0, x], [0, request.placement.scale, y], [0, 0, 1]],
            "resized_dimensions": [width, height],
            "resampling": "Pillow BICUBIC RGB and mask; integer dimensions round",
            "allowed": ["translation", "uniform_scale"],
            "edge_processing": "only declared uniform resize of source and alpha",
        },
        "protected_region": "all mask alpha > 0; opaque interior alpha=255; boundary 0<alpha<255",
        "working_profile": "sRGB",
        "export_profile": "sRGB PNG rendering intent perceptual",
        "tolerances": {
            "interior_max_channel_error": 0,
            "boundary_max_channel_error": 0,
            "background_max_channel_error": 0,
        },
        "tolerance_rationale": "Lossless PNG and independently rounded integer alpha math permit exact equality",
    }
    return source, mask, background, metadata


def _implementation_digest() -> str:
    return _digest(Path(__file__).read_bytes())


def _request_identity(
    request: CompositeRequest, metadata: dict, implementation_digest: str | None = None
) -> str:
    return _digest(
        _canonical(
            {
                "request": asdict(request),
                "inputs": metadata,
                "implementation": implementation_digest or _implementation_digest(),
            }
        )
    )


def _require_grant(
    request: CompositeRequest, root: Path, grant: LocalCompositeGrant | None
) -> dict:
    if not isinstance(grant, LocalCompositeGrant):
        raise CompositeError("Missing trusted local_composite action grant")
    if (
        grant.action != "local_composite"
        or grant.job_id != request.job_id
        or grant.source_sha256 != request.source.sha256
    ):
        raise CompositeError("Grant does not cover action/job/source")
    if not grant.approval_reference.strip():
        raise CompositeError("Grant requires actual approval provenance")
    allowed = _path(root, grant.output_root)
    output = _path(root, request.output_path)
    if not output.is_relative_to(allowed) or output == allowed:
        raise CompositeError("Output is outside granted scope")
    return asdict(grant)


def _exact_srgb_export(data: bytes) -> bool:
    """Inspect raw chunks: Pillow can silently discard invalid competing profiles."""
    if data[:8] != b"\x89PNG\r\n\x1a\n":
        return False
    offset, srgb_count = 8, 0
    while offset + 12 <= len(data):
        length = int.from_bytes(data[offset : offset + 4], "big")
        end = offset + 12 + length
        if end > len(data):
            return False
        kind = data[offset + 4 : offset + 8]
        payload = data[offset + 8 : offset + 8 + length]
        crc = int.from_bytes(data[offset + 8 + length : end], "big")
        if zlib.crc32(kind + payload) & 0xFFFFFFFF != crc:
            return False
        # This adapter exports exactly one sRGB declaration. Even nominally
        # equivalent ancillary profiles are outside that declared export contract.
        if kind in {b"iCCP", b"gAMA", b"cHRM", b"cICP", b"mDCV", b"cLLI"}:
            return False
        if kind == b"sRGB":
            srgb_count += 1
            if payload != b"\x00" or srgb_count != 1:
                return False
        if kind == b"IEND":
            return length == 0 and end == len(data) and srgb_count == 1
        offset = end
    return False


def verify_composite(
    request: CompositeRequest,
    manifest: dict,
    *,
    root: Path,
    producer_implementation: AssetRef | None = None,
) -> dict:
    """Check actual PNG with current verifier, optionally binding a past producer.

    Historical producer bytes are hash-checked as data only, never imported or run.
    The caller supplies the reviewed producer snapshot separately from the receipt.
    """
    verifier_digest = _implementation_digest()
    producer_digest = verifier_digest
    if producer_implementation is not None:
        snapshot = _path(root, producer_implementation.path).read_bytes()
        if _digest(snapshot) != producer_implementation.sha256:
            raise CompositeError("Historical producer snapshot identity changed")
        producer_digest = producer_implementation.sha256
    implementation_evidence = {
        "producer_implementation_sha256": producer_digest,
        "verifier_implementation_sha256": verifier_digest,
        "historical_producer_reference": (
            asdict(producer_implementation) if producer_implementation else None
        ),
        "verification_mode": (
            "CURRENT_VERIFIER_HISTORICAL_PRODUCER"
            if producer_implementation
            else "CURRENT_PRODUCER_AND_VERIFIER"
        ),
    }
    source, mask, background, metadata = _inputs(request, root)
    output = _path(root, request.output_path)
    actual_bytes = output.read_bytes()
    identity_ok = (
        manifest.get("request_identity") == _request_identity(request, metadata, producer_digest)
        and manifest.get("inputs") == metadata
        and manifest.get("request") == asdict(request)
        and manifest.get("job_id") == request.job_id
        and manifest.get("output_path") == request.output_path
        and manifest.get("output_dimensions") == list(background.size)
        and manifest.get("output_format") == "PNG"
        and manifest.get("publication_authorized") is False
        and manifest.get("provider_authorized") is False
    )
    hash_ok = manifest.get("output_sha256") == _digest(actual_bytes)
    if not _exact_srgb_export(actual_bytes):
        return {
            "status": "FAIL",
            "technical": "FAIL",
            "color_profile": "FAIL",
            "reason": "PNG violates exact sRGB-only export declaration",
            "artifact_identity": "PASS" if hash_ok else "FAIL",
            **implementation_evidence,
        }
    with Image.open(io.BytesIO(actual_bytes)) as actual_image:
        actual_image.load()
        technical_ok = (
            actual_image.format == "PNG"
            and actual_image.mode == "RGB"
            and actual_image.size == background.size
            and actual_image.info.get("srgb") == 0
        )
        if not technical_ok:
            return {
                "status": "FAIL",
                "technical": "FAIL",
                "artifact_identity": "PASS" if hash_ok else "FAIL",
                **implementation_evidence,
            }
        actual = np.asarray(actual_image, dtype=np.int32)
    size = tuple(metadata["transform"]["resized_dimensions"])
    # Separate verification path: no paste/composite call is shared with producer.
    rgb = np.asarray(source.resize(size, Image.Resampling.BICUBIC), dtype=np.int32)
    alpha = np.asarray(mask.resize(size, Image.Resampling.BICUBIC), dtype=np.int32)
    expected = np.asarray(background, dtype=np.int32).copy()
    x, y = request.placement.x, request.placement.y
    area = expected[y : y + size[1], x : x + size[0]]
    expected[y : y + size[1], x : x + size[0]] = (
        rgb * alpha[:, :, None] + area * (255 - alpha[:, :, None]) + 127
    ) // 255
    all_alpha = np.zeros(expected.shape[:2], dtype=np.int32)
    all_alpha[y : y + size[1], x : x + size[0]] = alpha
    error = np.abs(expected - actual).max(axis=2)
    criteria = {}
    for name, region in (
        ("opaque_interior", all_alpha == 255),
        ("antialiased_boundary", (all_alpha > 0) & (all_alpha < 255)),
        ("unprotected_background", all_alpha == 0),
    ):
        count = int(region.sum())
        maximum = int(error[region].max()) if count else 0
        criteria[name] = {
            "applicable": bool(count),
            "reason": (
                "Pixels in declared alpha region" if count else "No pixels in this alpha class"
            ),
            "pixel_count": count,
            "max_channel_error": maximum,
            "result": "PASS" if count and maximum == 0 else "FAIL" if count else "NOT RUN",
        }
    passed = (
        identity_ok
        and hash_ok
        and all(item["max_channel_error"] == 0 for item in criteria.values())
    )
    return {
        **implementation_evidence,
        "color_profile": "PASS",
        "status": "PASS" if passed else "FAIL",
        "technical": "PASS",
        "request_identity": "PASS" if identity_ok else "FAIL",
        "artifact_identity": "PASS" if hash_ok else "FAIL",
        "criteria": criteria,
        "output_sha256": _digest(actual_bytes),
        "limitations": "Checks source-layer preservation only; source correctness and complete garment mask coverage require separate visual review.",
    }


def compose(
    request: CompositeRequest, *, root: Path, grant: LocalCompositeGrant | None = None
) -> dict:
    """Create one immutable lossless artifact or verify an identical existing run."""
    authority = _require_grant(request, root, grant)
    source, mask, background, metadata = _inputs(request, root)
    output = _path(root, request.output_path)
    if output.suffix.lower() != ".png":
        raise CompositeError("Lossless PNG review master required")
    sidecar = output.with_suffix(output.suffix + ".manifest.json")
    identity = _request_identity(request, metadata)
    if output.exists() or sidecar.exists():
        if not output.is_file() or not sidecar.is_file():
            raise CompositeError(
                "Incomplete existing artifact; preserve and use a new output identity"
            )
        prior = json.loads(sidecar.read_text())
        if prior.get("request_identity") != identity or prior.get("authority") != authority:
            raise CompositeError("Existing artifact belongs to different source/contract/grant")
        if verify_composite(request, prior, root=root)["status"] != "PASS":
            raise CompositeError("Existing artifact verification failed")
        return prior
    size = tuple(metadata["transform"]["resized_dimensions"])
    layer = source.resize(size, Image.Resampling.BICUBIC)
    alpha = mask.resize(size, Image.Resampling.BICUBIC)
    result = background.copy()
    result.paste(layer, (request.placement.x, request.placement.y), alpha)
    png_info = PngImagePlugin.PngInfo()
    png_info.add(b"sRGB", b"\x00")
    stream = io.BytesIO()
    result.save(stream, format="PNG", pnginfo=png_info, icc_profile=None)
    data = stream.getvalue()
    manifest = {
        "version": "1.0",
        "job_id": request.job_id,
        "request": asdict(request),
        "request_identity": identity,
        "inputs": metadata,
        "authority": authority,
        "output_path": request.output_path,
        "output_sha256": _digest(data),
        "output_dimensions": list(result.size),
        "output_format": "PNG",
        "publication_authorized": False,
        "provider_authorized": False,
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    # Exclusive reservation prevents accidental overwrite and concurrent re-use.
    with sidecar.open("x") as receipt:
        receipt.write(_canonical(manifest).decode())
        receipt.flush()
        os.fsync(receipt.fileno())
    with output.open("xb") as image_file:
        image_file.write(data)
        image_file.flush()
        os.fsync(image_file.fileno())
    assessment = verify_composite(request, manifest, root=root)
    if assessment["status"] != "PASS":
        raise CompositeError("New artifact failed independent pixel preservation checks")
    return manifest
