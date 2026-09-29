"""In-test GLB builders — a real, spec-valid one-triangle GLB and JSON-only variants.

Kept stdlib-only so the web-pipeline tests never depend on the fixture tooling
they are testing.
"""

from __future__ import annotations

import json
import struct
from typing import Any

_JSON_CHUNK = 0x4E4F534A
_BIN_CHUNK = 0x004E4942


def _pad(data: bytes, fill: bytes) -> bytes:
    return data + fill * (-len(data) % 4)


def pack_glb(document: dict[str, Any], binary: bytes | None) -> bytes:
    """Assemble a GLB container from a glTF JSON document and optional BIN payload."""
    json_bytes = _pad(json.dumps(document, indent=2).encode("utf-8"), b" ")
    body = struct.pack("<II", len(json_bytes), _JSON_CHUNK) + json_bytes
    if binary is not None:
        bin_bytes = _pad(binary, b"\x00")
        body += struct.pack("<II", len(bin_bytes), _BIN_CHUNK) + bin_bytes
    return struct.pack("<4sII", b"glTF", 2, 12 + len(body)) + body


def triangle_document(binary_length: int, *, materials: int = 1) -> dict[str, Any]:
    """glTF JSON for one triangle whose positions live in the BIN chunk."""
    return {
        "asset": {"version": "2.0", "generator": "skyyrose-test-fixture"},
        "scene": 0,
        "scenes": [{"nodes": [0]}],
        "nodes": [{"mesh": 0}],
        "meshes": [{"primitives": [{"attributes": {"POSITION": 0}, "material": 0}]}],
        "materials": [
            {"name": f"fabric-{i}", "pbrMetallicRoughness": {"roughnessFactor": 0.9}}
            for i in range(materials)
        ],
        "buffers": [{"byteLength": binary_length}],
        "bufferViews": [{"buffer": 0, "byteOffset": 0, "byteLength": binary_length}],
        "accessors": [
            {
                "bufferView": 0,
                "componentType": 5126,
                "count": 3,
                "type": "VEC3",
                "min": [0.0, 0.0, 0.0],
                "max": [1.0, 1.0, 0.0],
            }
        ],
    }


def build_triangle_glb(*, materials: int = 1) -> bytes:
    """A complete, loadable GLB: one triangle, `materials` PBR materials."""
    positions = struct.pack("<9f", 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 1.0, 0.0)
    return pack_glb(triangle_document(len(positions), materials=materials), positions)


def web_ready_document(
    *,
    sheen: bool = True,
    mime: str = "image/ktx2",
    required: bool = True,
    compressed_view: bool = True,
) -> dict[str, Any]:
    """JSON shaped like real gltfpack `-cc -tc` output, for gate tests (no real payload).

    Mirrors what the binary actually emits (verified against renders/3d/web-v2/br-006.glb):
    meshopt/quantization/basisu in BOTH extensionsUsed and extensionsRequired, and a
    bufferView carrying EXT_meshopt_compression. `required=False` / `compressed_view=False`
    produce the "declares compression it never applied" shapes the gate must reject.
    """
    material: dict[str, Any] = {"pbrMetallicRoughness": {"baseColorTexture": {"index": 0}}}
    if sheen:
        material["extensions"] = {
            "KHR_materials_sheen": {
                "sheenColorFactor": [0.2, 0.2, 0.2],
                "sheenRoughnessFactor": 0.8,
            },
        }
    web = ["EXT_meshopt_compression", "KHR_texture_basisu", "KHR_mesh_quantization"]
    used = [*web, "KHR_materials_sheen"] if sheen else list(web)
    view: dict[str, Any] = {"buffer": 0, "byteLength": 4}
    if compressed_view:
        view["extensions"] = {
            "EXT_meshopt_compression": {
                "buffer": 0,
                "byteLength": 4,
                "count": 3,
                "mode": "ATTRIBUTES",
            }
        }
    document: dict[str, Any] = {
        "asset": {"version": "2.0", "generator": "gltfpack 1.2"},
        "extensionsUsed": used,
        "materials": [material],
        "textures": [{"extensions": {"KHR_texture_basisu": {"source": 0}}}],
        "images": [{"bufferView": 0, "mimeType": mime}],
        "buffers": [{"byteLength": 4}],
        "bufferViews": [view],
    }
    if required:
        document["extensionsRequired"] = list(web)
    return document
