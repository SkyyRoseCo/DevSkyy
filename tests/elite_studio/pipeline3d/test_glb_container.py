"""GLB container: JSON-chunk rewrite must leave the BIN chunk byte-identical."""

from __future__ import annotations

import json
import struct

import pytest

from skyyrose.elite_studio.pipeline3d.glb_container import (
    GlbFormatError,
    read_glb,
    write_glb,
)
from tests.elite_studio.pipeline3d.glb_fixture import (
    build_triangle_glb,
    pack_glb,
    triangle_document,
)


def _chunks(data: bytes) -> list[tuple[int, bytes]]:
    offset, chunks = 12, []
    while offset < len(data):
        length, kind = struct.unpack_from("<II", data, offset)
        chunks.append((kind, data[offset + 8 : offset + 8 + length]))
        offset += 8 + length
    return chunks


def test_read_returns_document_and_untouched_tail():
    data = build_triangle_glb()
    container = read_glb(data)
    assert container.document["asset"]["version"] == "2.0"
    assert container.tail == data[12 + 8 + struct.unpack_from("<I", data, 12)[0] :]


def test_rewrite_keeps_bin_chunk_byte_identical():
    data = build_triangle_glb()
    container = read_glb(data)
    changed = {**container.document, "extras": {"note": "x" * 7}}
    out = write_glb(changed, container.tail)
    assert _chunks(out)[1] == _chunks(data)[1]
    assert read_glb(out).document["extras"] == {"note": "xxxxxxx"}


def test_written_header_and_json_padding_are_spec_valid():
    container = read_glb(build_triangle_glb())
    out = write_glb({**container.document, "extras": {"k": "odd"}}, container.tail)
    magic, version, length = struct.unpack_from("<4sII", out, 0)
    json_length = struct.unpack_from("<I", out, 12)[0]
    assert (magic, version, length) == (b"glTF", 2, len(out))
    assert json_length % 4 == 0
    assert out[20 + json_length - 1 : 20 + json_length] in (b" ", b"}")


def test_json_only_glb_round_trips_without_tail():
    data = pack_glb({"asset": {"version": "2.0"}}, None)
    container = read_glb(data)
    assert container.tail == b""
    assert read_glb(write_glb(container.document, b"")).document == container.document


@pytest.mark.parametrize(
    "mutate",
    [
        lambda d: b"gLTF" + d[4:],
        lambda d: d[:4] + struct.pack("<I", 1) + d[8:],
        lambda d: d[:8] + struct.pack("<I", len(d) + 4) + d[12:],
        lambda d: d[:12] + struct.pack("<I", len(d)) + d[16:],
        lambda d: d[:16] + struct.pack("<I", 0x004E4942) + d[20:],
        lambda d: d[:11],
    ],
    ids=["magic", "version", "total-length", "json-overrun", "first-not-json", "truncated"],
)
def test_malformed_containers_fail_closed(mutate):
    with pytest.raises(GlbFormatError):
        read_glb(mutate(build_triangle_glb()))


def test_non_object_json_fails_closed():
    data = pack_glb({"asset": {"version": "2.0"}}, None)
    json_length = struct.unpack_from("<I", data, 12)[0]
    bad = data[:20] + b"[]".ljust(json_length, b" ") + data[20 + json_length :]
    with pytest.raises(GlbFormatError):
        read_glb(bad)


def _relength(data: bytes, total: int) -> bytes:
    """Rewrite the 12-byte header's total-length field, keeping it self-consistent."""
    return data[:8] + struct.pack("<I", total) + data[12:]


def test_rejects_bin_chunk_that_overruns_the_file():
    data = build_triangle_glb()
    bin_header = data.index(b"BIN\x00") - 4
    corrupted = data[:bin_header] + struct.pack("<I", 100_000) + data[bin_header + 4 :]
    with pytest.raises(GlbFormatError, match="declares 100000 bytes"):
        read_glb(corrupted)


def test_rejects_trailing_bytes_after_the_last_chunk():
    data = build_triangle_glb()
    junk = data + b"\x00\x00\x00"
    with pytest.raises(GlbFormatError, match="truncated"):
        read_glb(_relength(junk, len(junk)))


def test_rejects_unpadded_json_chunk_length():
    data = build_triangle_glb()
    json_length = struct.unpack_from("<I", data, 12)[0]
    corrupted = data[:12] + struct.pack("<I", json_length - 3) + data[16:]
    with pytest.raises(GlbFormatError, match="unpadded length"):
        read_glb(corrupted)


@pytest.mark.parametrize("literal", ["NaN", "Infinity", "-Infinity"])
def test_rejects_json_literals_a_browser_cannot_parse(literal):
    document = triangle_document(12)
    raw = json.dumps(document).replace('"version": "2.0"', f'"version": {literal}')
    body = raw.encode("utf-8")
    body += b" " * (-len(body) % 4)
    chunk = struct.pack("<II", len(body), 0x4E4F534A) + body
    glb = struct.pack("<4sII", b"glTF", 2, 12 + len(chunk)) + chunk
    with pytest.raises(GlbFormatError, match="non-standard literal"):
        read_glb(glb)


def test_rejects_a_second_bin_chunk():
    data = build_triangle_glb()
    extra = struct.pack("<II", 4, 0x004E4942) + b"\x00\x00\x00\x00"
    doubled = data + extra
    with pytest.raises(GlbFormatError, match="BIN chunks"):
        read_glb(_relength(doubled, len(doubled)))


def test_write_glb_rejects_a_document_it_cannot_encode():
    with pytest.raises(GlbFormatError, match="not serialisable"):
        write_glb({"asset": {"generator": "\ud800"}}, b"")
