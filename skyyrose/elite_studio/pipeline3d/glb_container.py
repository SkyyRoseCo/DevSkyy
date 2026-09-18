"""Lossless GLB container I/O — rewrite the glTF JSON chunk, never touch the payload.

Material-level edits (sheen, anisotropy) are JSON-only changes. Re-exporting through a
DCC tool re-encodes textures and re-splits seam vertices (bug-297), so the web pipeline
edits the container directly: the JSON chunk is re-serialised and every byte after it
(BIN chunk and any further chunks) is carried over verbatim.

Layout (glTF 2.0 §4.4): 12-byte header ``magic | version | length`` followed by chunks of
``length | type | data``; the first chunk must be JSON, padded with spaces to 4 bytes.

``read_glb`` walks every chunk, not just the JSON one, because it is the only structural check
in front of the web gate: ``--prepacked-dir`` feeds it legacy files nobody in this pipeline
produced. A declared BIN length that overruns the file, trailing junk, or an unpadded chunk all
make a container that browsers reject, so they fail closed here rather than reaching the CDN.
"""

from __future__ import annotations

import json
import struct
from dataclasses import dataclass
from typing import Any

_MAGIC = b"glTF"
_VERSION = 2
_HEADER = struct.Struct("<4sII")
_CHUNK_HEADER = struct.Struct("<II")
_JSON_CHUNK = 0x4E4F534A
_BIN_CHUNK = 0x004E4942


class GlbFormatError(ValueError):
    """The bytes are not a well-formed glTF 2.0 binary container."""


@dataclass(frozen=True)
class GlbContainer:
    """Parsed GLB: the glTF JSON document and the untouched bytes that follow it."""

    document: dict[str, Any]
    tail: bytes


def _check_header(data: bytes) -> None:
    if len(data) < _HEADER.size + _CHUNK_HEADER.size:
        raise GlbFormatError(f"too short for a GLB container ({len(data)} bytes)")
    magic, version, length = _HEADER.unpack_from(data, 0)
    if magic != _MAGIC:
        raise GlbFormatError(f"bad magic {magic!r}")
    if version != _VERSION:
        raise GlbFormatError(f"unsupported glTF container version {version}")
    if length != len(data):
        raise GlbFormatError(f"header length {length} != actual {len(data)}")


def _reject_constant(literal: str) -> Any:
    """json.loads hook: NaN/Infinity parse in Python but not in a browser's JSON.parse."""
    raise GlbFormatError(f"JSON chunk contains the non-standard literal {literal}")


def _walk_chunks(data: bytes) -> list[tuple[int, int, int]]:
    """Return ``(type, data_offset, length)`` per chunk, or raise on any layout violation."""
    chunks: list[tuple[int, int, int]] = []
    cursor = _HEADER.size
    while cursor < len(data):
        if cursor + _CHUNK_HEADER.size > len(data):
            raise GlbFormatError(f"chunk header at {cursor} is truncated")
        length, chunk_type = _CHUNK_HEADER.unpack_from(data, cursor)
        if length % 4 != 0:
            raise GlbFormatError(f"chunk at {cursor} has unpadded length {length}")
        start = cursor + _CHUNK_HEADER.size
        if start + length > len(data):
            raise GlbFormatError(
                f"chunk at {cursor} declares {length} bytes, only {len(data) - start} remain"
            )
        chunks.append((chunk_type, start, length))
        cursor = start + length
    if not chunks:
        raise GlbFormatError("container holds no chunks")
    if chunks[0][0] != _JSON_CHUNK:
        raise GlbFormatError("first chunk is not JSON")
    binary = [index for index, chunk in enumerate(chunks) if chunk[0] == _BIN_CHUNK]
    if len(binary) > 1:
        raise GlbFormatError(f"{len(binary)} BIN chunks, glTF 2.0 allows one")
    if binary and binary[0] != 1:
        raise GlbFormatError(f"BIN chunk is at index {binary[0]}, must directly follow JSON")
    return chunks


def read_glb(data: bytes) -> GlbContainer:
    """Parse a GLB; raise ``GlbFormatError`` on anything malformed (fail closed)."""
    _check_header(data)
    chunks = _walk_chunks(data)
    _, json_start, json_length = chunks[0]
    try:
        document = json.loads(
            data[json_start : json_start + json_length].decode("utf-8"),
            parse_constant=_reject_constant,
        )
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise GlbFormatError(f"JSON chunk is not valid UTF-8 JSON: {exc}") from exc
    if not isinstance(document, dict):
        raise GlbFormatError("JSON chunk is not a glTF object")
    return GlbContainer(document=document, tail=data[json_start + json_length :])


def write_glb(document: dict[str, Any], tail: bytes) -> bytes:
    """Serialise ``document`` into a JSON chunk and re-attach ``tail`` byte-for-byte."""
    try:
        encoded = json.dumps(document, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    except (UnicodeEncodeError, ValueError) as exc:
        raise GlbFormatError(f"glTF document is not serialisable to a JSON chunk: {exc}") from exc
    padded = encoded + b" " * (-len(encoded) % 4)
    body = _CHUNK_HEADER.pack(len(padded), _JSON_CHUNK) + padded + tail
    return _HEADER.pack(_MAGIC, _VERSION, _HEADER.size + len(body)) + body
