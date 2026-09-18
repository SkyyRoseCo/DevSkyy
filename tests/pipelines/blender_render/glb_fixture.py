"""Tiny hand-built GLB fixtures (no external deps) for the Blender render tests.

``write_box_glb`` emits a valid glTF 2.0 binary containing one box mesh with a red
``pbrMetallicRoughness`` material — enough for Blender's importer, the sheen patcher and
gltfpack. Pure ``struct``/``json`` so the fixture never depends on the code under test.
"""

from __future__ import annotations

import json
import struct
from pathlib import Path

_MAGIC = b"glTF"
_JSON_CHUNK = 0x4E4F534A
_BIN_CHUNK = 0x004E4942


def _box_geometry(size: tuple[float, float, float]) -> tuple[list[float], list[int]]:
    half_x, half_y, half_z = (component / 2.0 for component in size)
    corners = [
        (-half_x, -half_y, -half_z),
        (half_x, -half_y, -half_z),
        (half_x, half_y, -half_z),
        (-half_x, half_y, -half_z),
        (-half_x, -half_y, half_z),
        (half_x, -half_y, half_z),
        (half_x, half_y, half_z),
        (-half_x, half_y, half_z),
    ]
    faces = [
        (0, 2, 1),
        (0, 3, 2),
        (4, 5, 6),
        (4, 6, 7),
        (0, 1, 5),
        (0, 5, 4),
        (1, 2, 6),
        (1, 6, 5),
        (2, 3, 7),
        (2, 7, 6),
        (3, 0, 4),
        (3, 4, 7),
    ]
    positions = [component for corner in corners for component in corner]
    indices = [index for face in faces for index in face]
    return positions, indices


def _box_document(
    size: tuple[float, float, float], position_len: int, index_len: int, index_count: int
) -> tuple[dict, dict]:
    """The glTF JSON for one box mesh, plus its primitive (so a material can be attached)."""
    half = [component / 2.0 for component in size]
    primitive: dict = {"attributes": {"POSITION": 0}, "indices": 1}
    document: dict = {
        "asset": {"version": "2.0", "generator": "devskyy-test-fixture"},
        "scene": 0,
        "scenes": [{"nodes": [0]}],
        "nodes": [{"mesh": 0, "name": "box"}],
        "meshes": [{"primitives": [primitive]}],
        "buffers": [{"byteLength": position_len + index_len}],
        "bufferViews": [
            {"buffer": 0, "byteOffset": 0, "byteLength": position_len, "target": 34962},
            {"buffer": 0, "byteOffset": position_len, "byteLength": index_len, "target": 34963},
        ],
        "accessors": [
            {
                "bufferView": 0,
                "componentType": 5126,
                "count": 8,
                "type": "VEC3",
                "min": [-half[0], -half[1], -half[2]],
                "max": half,
            },
            {"bufferView": 1, "componentType": 5123, "count": index_count, "type": "SCALAR"},
        ],
    }
    return document, primitive


def _pack_glb(document: dict, binary: bytes) -> bytes:
    """Assemble the GLB container: padded JSON chunk, BIN chunk, 12-byte header."""
    encoded = json.dumps(document, separators=(",", ":")).encode("utf-8")
    encoded += b" " * (-len(encoded) % 4)
    body = struct.pack("<II", len(encoded), _JSON_CHUNK) + encoded
    body += struct.pack("<II", len(binary), _BIN_CHUNK) + binary
    return struct.pack("<4sII", _MAGIC, 2, 12 + len(body)) + body


def build_box_glb(
    size: tuple[float, float, float] = (0.4, 0.8, 0.2),
    *,
    color: tuple[float, float, float, float] = (0.8, 0.1, 0.1, 1.0),
    with_material: bool = True,
) -> bytes:
    """Return GLB bytes for a single box mesh (optionally without any material)."""
    positions, indices = _box_geometry(size)
    position_bytes = struct.pack(f"<{len(positions)}f", *positions)
    index_bytes = struct.pack(f"<{len(indices)}H", *indices)
    index_bytes += b"\0" * (-len(index_bytes) % 4)
    document, primitive = _box_document(size, len(position_bytes), len(index_bytes), len(indices))
    if with_material:
        primitive["material"] = 0
        document["materials"] = [
            {
                "name": "fixture_red",
                "pbrMetallicRoughness": {
                    "baseColorFactor": list(color),
                    "metallicFactor": 0.0,
                    "roughnessFactor": 0.7,
                },
            }
        ]
    return _pack_glb(document, position_bytes + index_bytes)


def write_box_glb(path: Path, **kwargs) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(build_box_glb(**kwargs))
    return path
