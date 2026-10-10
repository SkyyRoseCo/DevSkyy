"""Assemble the corrected Town Line films from local files, without network calls.

Run --dry-run for the timeline or --check-inputs for read-only media validation.
An ordinary invocation builds into output/ only after every input passes. Source
frames are decoded directly from the original video and checked after encoding.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import logging
import subprocess
import sys
import zipfile
from dataclasses import asdict, dataclass
from fractions import Fraction
from pathlib import Path

BASE = Path(__file__).resolve().parent
ORIGINAL = Path("/Users/theceo/Downloads/Video Apr 21 2024, 11 01 18 AM.mp4")
ORIGINAL_SHA = "8b0953c5824f07f0a8f483aeac34305ec032d453c93da17a37cfa4ecd6918127"
FPS = Fraction(24000, 1001)
TIME_BASE = Fraction(1, 24000)
SOURCE_INTERVALS = ((695, 767), (983, 1031), (1391, 1463))
REUSED_HASHES = {
    "TRAIN": "95a736ed1550944b038040641d4247b07ab33d7bf3041965535e77ac67b20b02",
    "DOOR": "f071c24131d3fd4329bb1766fbf47656ca7299f382bc71c33a1f4bacabc51efe",
}
LOG = logging.getLogger("town_line")


class BuildError(RuntimeError):
    """A failed input, source-preservation, export, or packaging invariant."""


@dataclass(frozen=True, order=True)
class Cut:
    """An end-exclusive range of decoded frames."""

    clip: str
    start: int
    end: int

    @property
    def frames(self) -> int:
        return self.end - self.start


@dataclass(frozen=True)
class Film:
    """One immutable edit and its expected final length."""

    id: str
    title: str
    frames: int
    cuts: tuple[Cut, ...]


@dataclass(frozen=True)
class Paths:
    """Local inputs and a separate output directory."""

    source: Path
    media: Path
    output: Path

    def input(self, clip: str) -> Path:
        return self.source if clip == "SOURCE" else self.media / f"{clip}.mp4"


FILMS = (
    Film("signature", "The First Light", 480, (Cut("SGA", 0, 240), Cut("SGB", 0, 240))),
    Film(
        "black-rose",
        "The Night Car",
        480,
        (
            Cut("SOURCE", 0, 48),
            Cut("BRA", 0, 72),
            Cut("SOURCE", 48, 72),
            Cut("SOURCE", 72, 120),
            Cut("BRA", 72, 168),
            Cut("SOURCE", 120, 192),
            Cut("BRB", 0, 120),
        ),
    ),
    Film("love-hurts", "The Seat Beside You", 480, (Cut("LHA", 0, 240), Cut("LHB", 0, 240))),
    Film(
        "kids-capsule",
        "Your Turn",
        480,
        (
            Cut("DOOR", 0, 12),
            Cut("KR", 0, 144),
            Cut("KP", 0, 228),
            Cut("KR", 144, 240),
        ),
    ),
    Film(
        "town-line-main",
        "The Town Line",
        960,
        (
            Cut("TRAIN", 0, 48),
            Cut("SGA", 144, 192),
            Cut("SGB", 144, 240),
            Cut("SOURCE", 0, 24),
            Cut("BRA", 24, 72),
            Cut("SOURCE", 24, 48),
            Cut("SOURCE", 72, 120),
            Cut("SOURCE", 120, 168),
            Cut("BRB", 24, 120),
            Cut("LHA", 144, 240),
            Cut("LHB", 144, 240),
            Cut("DOOR", 0, 12),
            Cut("KR", 0, 120),
            Cut("KP", 24, 120),
            Cut("KR", 180, 240),
        ),
    ),
)


def run(args: list[str], label: str) -> bytes:
    """Run a local media tool; never expose its command or captured error text."""
    try:
        result = subprocess.run(args, capture_output=True, check=False)
    except OSError:
        raise BuildError(f"{label} could not start") from None
    if result.returncode:
        raise BuildError(f"{label} failed (exit {result.returncode})")
    return result.stdout


def sha256(path: Path) -> str:
    """Hash file bytes without buffering an entire movie."""
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def safe_json(value: object) -> str:
    """Serialize only delivery-safe metadata; no remote URL is ever needed."""
    serialized = json.dumps(value, indent=2, sort_keys=True)
    lowered = serialized.lower()
    if any(
        marker in lowered for marker in ("https://", "http://", "_jwt=", "x-amz-", "upload_url")
    ):
        raise BuildError("Private download data cannot enter a delivery report")
    return serialized + "\n"


def write_json(path: Path, value: object) -> None:
    """Write a checked JSON delivery artifact."""
    path.write_text(safe_json(value), encoding="utf-8")


def probe(path: Path) -> dict[str, object]:
    """Read counted video frames and only the metadata required for validation."""
    data = json.loads(
        run(
            [
                "ffprobe",
                "-v",
                "error",
                "-count_frames",
                "-show_streams",
                "-show_format",
                "-of",
                "json",
                str(path),
            ],
            f"Probe {path.name}",
        )
    )
    video = next((s for s in data["streams"] if s["codec_type"] == "video"), None)
    if video is None:
        raise BuildError(f"No video in {path.name}")
    return {
        "file": path.name,
        "frames": int(video["nb_read_frames"]),
        "fps": str(video["r_frame_rate"]),
        "average_fps": str(video["avg_frame_rate"]),
        "time_base": str(video["time_base"]),
        "width": int(video["width"]),
        "height": int(video["height"]),
        "pixel_format": str(video["pix_fmt"]),
        "duration": float(data["format"]["duration"]),
        "audio_tracks": sum(s["codec_type"] == "audio" for s in data["streams"]),
        "sha256": sha256(path),
        "bytes": path.stat().st_size,
    }


def expand_source(cut: Cut) -> tuple[Cut, ...]:
    """Map logical SOURCE-reel indices back to unchanged original video frames."""
    if cut.clip != "SOURCE":
        return (cut,)
    if not 0 <= cut.start < cut.end <= 192:
        raise BuildError("Invalid original-source selection")
    result = []
    offset = 0
    for original_start, original_end in SOURCE_INTERVALS:
        limit = offset + original_end - original_start
        start, end = max(cut.start, offset), min(cut.end, limit)
        if start < end:
            result.append(
                Cut("SOURCE", original_start + start - offset, original_start + end - offset)
            )
        offset = limit
    return tuple(result)


def expanded_cuts(film: Film) -> tuple[Cut, ...]:
    """Resolve every edit range into its actual input file's frame indices."""
    return tuple(item for cut in film.cuts for item in expand_source(cut))


def boundaries(cuts: tuple[Cut, ...]) -> set[int]:
    """Return all shot-start frame indices, including the first frame."""
    starts, offset = set(), 0
    for cut in cuts:
        starts.add(offset)
        offset += cut.frames
    return starts


def validate_timeline() -> None:
    """Reject accidental changes to exact lengths, source coverage, or reuse."""
    expected = {
        "black-rose": [(0, 48), (48, 72), (72, 120), (120, 192)],
        "town-line-main": [(0, 24), (24, 48), (72, 120), (120, 168)],
    }
    for film in FILMS:
        if sum(c.frames for c in film.cuts) != film.frames:
            raise BuildError(f"Timeline total changed: {film.id}")
        if [(c.start, c.end) for c in film.cuts if c.clip == "SOURCE"] != expected.get(film.id, []):
            raise BuildError(f"Source selections changed: {film.id}")
        for cut in film.cuts:
            if (
                cut.start < 0
                or cut.frames <= 0
                or (cut.clip == "DOOR" and (cut.start, cut.end) != (0, 12))
            ):
                raise BuildError(f"Invalid or rejected range: {film.id}")
            expand_source(cut)


def check_inputs(paths: Paths) -> dict[str, object]:
    """Inspect available local inputs and report every missing or invalid file."""
    needed: dict[str, int] = {"SOURCE": 1561}
    for film in FILMS:
        for cut in expanded_cuts(film):
            needed[cut.clip] = max(needed.get(cut.clip, 0), cut.end)
    inputs: dict[str, object] = {}
    problems = []
    for clip, count in sorted(needed.items()):
        path = paths.input(clip)
        if not path.is_file():
            problems.append(f"Missing {clip}")
            continue
        info = probe(path)
        inputs[clip] = info
        wanted_fps = FPS if clip == "SOURCE" else Fraction(24)
        if (
            Fraction(str(info["fps"])) != wanted_fps
            or Fraction(str(info["average_fps"])) != wanted_fps
        ):
            problems.append(f"Unexpected cadence: {clip}")
        if int(str(info["frames"])) < count:
            problems.append(f"Insufficient decoded frames: {clip}")
        expected_hash = ORIGINAL_SHA if clip == "SOURCE" else REUSED_HASHES.get(clip)
        if expected_hash and info["sha256"] != expected_hash:
            problems.append(f"Input identity hash mismatch: {clip}")
        if clip == "SOURCE":
            if (info["width"], info["height"], info["pixel_format"]) != (720, 1280, "yuv420p"):
                problems.append("Original-source decoded format changed")
        elif info["audio_tracks"]:
            problems.append(f"Generated input has audio; prepare a documented silent copy: {clip}")
    return {"ready": not problems, "problems": problems, "inputs": inputs}


def encoder_args(output: Path, keyframes: set[int], *, lossless: bool) -> list[str]:
    """Use exact video/movie time bases and force keyframes at every edit boundary."""
    force = "expr:" + "+".join(f"eq(n,{n})" for n in sorted(keyframes))
    # FFmpeg 8 rejects -r together with passthrough. Every input timestamp is
    # already assigned to this exact cadence; count, timestamps and source MD5
    # checks below reject any frame duplication, removal or pixel change.
    args = [
        "-an",
        "-map_metadata",
        "-1",
        "-c:v",
        "libx264",
        "-preset",
        "fast" if lossless else "slow",
        "-crf",
        "0" if lossless else "16",
        "-pix_fmt",
        "yuv420p",
        "-threads",
        "2",
        "-bf",
        "0",
        "-r",
        str(FPS),
        "-fps_mode",
        "cfr",
        "-video_track_timescale",
        "24000",
        "-movie_timescale",
        "24000",
        "-g",
        "48",
        "-sc_threshold",
        "0",
        "-force_key_frames",
        force,
        "-color_primaries",
        "bt709",
        "-color_trc",
        "bt709",
        "-colorspace",
        "bt709",
    ]
    if not lossless:
        args += ["-profile:v", "high"]
    return args + ["-movflags", "+faststart", str(output)]


def make_cut(paths: Paths, cut: Cut) -> Path:
    """Encode one exact cut; original source bypasses all image transformations."""
    output = paths.output / "work" / f"{cut.clip}-{cut.start}-{cut.end}.mp4"
    filters = f"trim=start_frame={cut.start}:end_frame={cut.end},settb=1/24000,setpts=N*1001"
    if cut.clip != "SOURCE":
        filters += ",scale=720:1280:force_original_aspect_ratio=decrease:force_divisible_by=2:flags=lanczos"
        filters += ",pad=720:1280:(ow-iw)/2:(oh-ih)/2,setsar=1"
    run(
        [
            "ffmpeg",
            "-v",
            "error",
            "-nostdin",
            "-n",
            "-threads",
            "1",
            "-noautorotate",
            "-i",
            str(paths.input(cut.clip)),
            "-map",
            "0:v:0",
            "-vf",
            filters,
        ]
        + encoder_args(output, {0}, lossless=True),
        f"Cut {cut.clip} {cut.start}:{cut.end}",
    )
    validate_export(output, cut.frames, {0})
    return output


def frame_hashes(path: Path) -> list[str]:
    """Hash every decoded YUV420P frame without cadence conversion."""
    raw = run(
        [
            "ffmpeg",
            "-v",
            "error",
            "-nostdin",
            "-threads",
            "1",
            "-noautorotate",
            "-i",
            str(path),
            "-map",
            "0:v:0",
            "-an",
            "-pix_fmt",
            "yuv420p",
            "-threads",
            "1",
            "-fps_mode",
            "passthrough",
            "-f",
            "framemd5",
            "pipe:1",
        ],
        f"Frame hashes {path.name}",
    )
    return [
        line.rsplit(",", 1)[1].strip()
        for line in raw.decode().splitlines()
        if line and not line.startswith("#")
    ]


def validate_frame_records(
    records: list[dict[str, int]], count: int, required_keys: set[int]
) -> list[int]:
    """Check every decoded frame timestamp and required shot-boundary keyframe."""
    if len(records) != count:
        raise BuildError("Decoded frame count changed")
    keys = []
    for index, frame in enumerate(records):
        if frame["best_effort_timestamp"] != index * 1001:
            raise BuildError(f"Frame timestamp discontinuity at frame {index}")
        if frame["key_frame"]:
            keys.append(index)
    if not required_keys.issubset(keys):
        raise BuildError("Missing keyframe at an edit boundary")
    return keys


def validate_export(path: Path, count: int, required_keys: set[int]) -> dict[str, object]:
    """Require exact decoded length, silence, canvas, timestamps, and keyframes."""
    info = probe(path)
    expected = (count, str(FPS), str(FPS), "1/24000", 720, 1280, "yuv420p", 0)
    fields = (
        "frames",
        "fps",
        "average_fps",
        "time_base",
        "width",
        "height",
        "pixel_format",
        "audio_tracks",
    )
    if tuple(info[field] for field in fields) != expected:
        raise BuildError(f"Export format validation failed: {path.name}")
    if abs(float(str(info["duration"])) - float(count / FPS)) > 0.001:
        raise BuildError(f"Export duration validation failed: {path.name}")
    data = json.loads(
        run(
            [
                "ffprobe",
                "-v",
                "error",
                "-select_streams",
                "v:0",
                "-show_frames",
                "-show_entries",
                "frame=best_effort_timestamp,key_frame",
                "-of",
                "json",
                str(path),
            ],
            f"Timestamp validation {path.name}",
        )
    )
    records = [
        {"best_effort_timestamp": int(f["best_effort_timestamp"]), "key_frame": int(f["key_frame"])}
        for f in data["frames"]
    ]
    keys = validate_frame_records(records, count, required_keys)
    info["all_frame_timestamps_exact"] = True
    info["keyframes"] = [{"frame": n, "pts": n * 1001} for n in keys]
    return info


def source_frame_map(film: Film, original: list[str]) -> list[dict[str, object]]:
    """Record exact original/output frame correspondence, including decoded MD5."""
    proof: list[dict[str, object]] = []
    offset = 0
    for cut in expanded_cuts(film):
        if cut.clip == "SOURCE":
            for index in range(cut.frames):
                proof.append(
                    {
                        "output_frame": offset + index,
                        "original_frame": cut.start + index,
                        "md5": original[cut.start + index],
                    }
                )
        offset += cut.frames
    return proof


def verify_source_pixels(film: Film, final: list[str], original: list[str]) -> int:
    """Fail on any selected original pixel mismatch after final lossless encoding."""
    if len(final) != film.frames:
        raise BuildError(f"Final decoded hash count changed: {film.id}")
    proof = source_frame_map(film, original)
    for item in proof:
        if final[int(str(item["output_frame"]))] != item["md5"]:
            raise BuildError(f"Original source pixels changed: {film.id}")
    return len(proof)


def make_master(paths: Paths, film: Film, cuts: dict[Cut, Path]) -> Path:
    """Losslessly concatenate frames and assign exact final rational timestamps."""
    selections = expanded_cuts(film)
    args = ["ffmpeg", "-v", "error", "-nostdin", "-n", "-filter_complex_threads", "1"]
    for cut in selections:
        args += ["-threads", "1", "-i", str(cuts[cut])]
    graph = "".join(f"[{n}:v:0]" for n in range(len(selections)))
    graph += f"concat=n={len(selections)}:v=1:a=0,settb=1/24000,setpts=N*1001[out]"
    output = paths.output / f"{film.id}-lossless.mp4"
    run(
        args
        + ["-filter_complex", graph, "-map", "[out]"]
        + encoder_args(output, boundaries(selections), lossless=True),
        f"Master {film.id}",
    )
    return output


def make_sheet(paths: Paths, film: Film, viewing: Path) -> str:
    """Include the actual final frame and frames on both sides of each join."""
    indices = {0, film.frames // 4, film.frames // 2, film.frames * 3 // 4, film.frames - 1}
    for boundary in boundaries(expanded_cuts(film)):
        indices.update({max(0, boundary - 1), boundary})
    ordered = sorted(indices)
    select = "+".join(f"eq(n\\,{n})" for n in ordered)
    rows = (len(ordered) + 4) // 5
    sheet = paths.output / f"{film.id}-sheet.jpg"
    run(
        [
            "ffmpeg",
            "-v",
            "error",
            "-nostdin",
            "-n",
            "-threads",
            "1",
            "-i",
            str(viewing),
            "-vf",
            f"select={select},scale=144:256,tile=5x{rows}",
            "-frames:v",
            "1",
            "-q:v",
            "2",
            str(sheet),
        ],
        f"Contact sheet {film.id}",
    )
    if not sheet.is_file() or not sheet.stat().st_size:
        raise BuildError(f"Contact sheet missing: {film.id}")
    write_json(
        paths.output / f"{film.id}-sheet-frames.json", {"file": sheet.name, "frames": ordered}
    )
    return sheet.name


def build_film(
    paths: Paths, film: Film, cuts: dict[Cut, Path], original: list[str]
) -> dict[str, object]:
    """Build both delivery variants and retain frame-preservation evidence."""
    master = make_master(paths, film, cuts)
    required_keys = boundaries(expanded_cuts(film))
    master_info = validate_export(master, film.frames, required_keys)
    checked = verify_source_pixels(film, frame_hashes(master), original)
    proof_name = f"{film.id}-source-frame-proof.json"
    write_json(
        paths.output / proof_name,
        {"original_sha256": ORIGINAL_SHA, "matches": source_frame_map(film, original)},
    )
    viewing = paths.output / f"{film.id}.mp4"
    run(
        [
            "ffmpeg",
            "-v",
            "error",
            "-nostdin",
            "-n",
            "-threads",
            "1",
            "-i",
            str(master),
            "-map",
            "0:v:0",
        ]
        + encoder_args(viewing, required_keys, lossless=False),
        f"Viewing copy {film.id}",
    )
    view_info = validate_export(viewing, film.frames, required_keys)
    sheet_name = make_sheet(paths, film, viewing)
    LOG.info("%s: %s frames, %s original source frames matched", film.id, film.frames, checked)
    return {
        "id": film.id,
        "title": film.title,
        "frames": film.frames,
        "master": master_info,
        "viewing": view_info,
        "source_frames_pixel_matched": checked,
        "source_proof": proof_name,
        "sheet": sheet_name,
        "segments": [asdict(c) for c in film.cuts],
    }


def make_archive(output: Path, filenames: list[str]) -> dict[str, object]:
    """Archive an explicit public-file whitelist and verify every member's CRC."""
    archive = output / "SkyyRose-Town-Line-Corrected-Films.zip"
    if len(filenames) != len(set(filenames)) or any(Path(name).name != name for name in filenames):
        raise BuildError("Invalid archive filename whitelist")
    with zipfile.ZipFile(archive, "x", compression=zipfile.ZIP_STORED) as bundle:
        for name in filenames:
            bundle.write(output / name, name)
    with zipfile.ZipFile(archive) as bundle:
        if bundle.namelist() != filenames or bundle.testzip() is not None:
            raise BuildError("Archive file-list or CRC validation failed")
    return {
        "file": archive.name,
        "sha256": sha256(archive),
        "bytes": archive.stat().st_size,
        "crc": "PASS",
    }


def assemble(paths: Paths, checked: dict[str, object]) -> dict[str, object]:
    """Build into an empty local directory and never overwrite historical work."""
    if paths.output.exists() and any(paths.output.iterdir()):
        raise BuildError(
            "Output must be empty; preserve the existing run and choose a new output directory"
        )
    paths.output.mkdir(parents=True, exist_ok=True)
    (paths.output / "work").mkdir()
    original_hashes = frame_hashes(paths.source)
    if len(original_hashes) != 1561:
        raise BuildError("Original source decoded frame count changed")
    specs = sorted({c for film in FILMS for c in expanded_cuts(film)})
    cuts = {}
    for index, cut in enumerate(specs, 1):
        LOG.info("Cut %s/%s: %s %s:%s", index, len(specs), cut.clip, cut.start, cut.end)
        cuts[cut] = make_cut(paths, cut)
    films = [build_film(paths, film, cuts, original_hashes) for film in FILMS]
    if sha256(paths.source) != ORIGINAL_SHA:
        raise BuildError("Original source file changed during assembly")
    report = {
        "schema": "skyyrose.collection-films.corrected.v1",
        "fps": str(FPS),
        "canvas": [720, 1280],
        "audio_tracks": 0,
        "inputs": checked["inputs"],
        "films": films,
        "published": False,
        "source_file_unchanged": True,
        "original_sha256": ORIGINAL_SHA,
        "source_original_intervals": SOURCE_INTERVALS,
        "source_policy": "Every selected original decoded frame matched in lossless masters; viewing copies use delivery compression.",
        "visual_review": "PENDING: technical source proof does not establish generated cast or garment continuity.",
    }
    write_json(paths.output / "verification.json", report)
    write_json(paths.output / "edit-manifest.json", timeline_report())
    script_name = "assemble_corrected.py"
    (paths.output / script_name).write_bytes(Path(__file__).read_bytes())
    filenames = ["verification.json", "edit-manifest.json", script_name]
    for film in FILMS:
        filenames.extend(
            f"{film.id}{suffix}"
            for suffix in (
                "-lossless.mp4",
                ".mp4",
                "-sheet.jpg",
                "-sheet-frames.json",
                "-source-frame-proof.json",
            )
        )
    report["archive"] = make_archive(paths.output, filenames)
    write_json(paths.output / "final-report.json", report)
    return report


def timeline_report() -> dict[str, object]:
    """Return reproducible public editorial data with no download URLs or tokens."""
    return {
        "fps": str(FPS),
        "canvas": [720, 1280],
        "requested_motion_jobs": 8,
        "requested_motion_seconds": 75,
        "source_original_intervals": SOURCE_INTERVALS,
        "films": [
            {
                "id": f.id,
                "title": f.title,
                "frames": f.frames,
                "duration": float(f.frames / FPS),
                "segments": [asdict(c) for c in f.cuts],
            }
            for f in FILMS
        ],
    }


def main() -> int:
    """Run a read-only check or, explicitly without check flags, local assembly."""
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate/print the edit without reading media or writing files",
    )
    mode.add_argument(
        "--check-inputs",
        action="store_true",
        help="Hash/probe local inputs; never assemble or write",
    )
    parser.add_argument("--source", type=Path, default=ORIGINAL)
    parser.add_argument("--media-dir", type=Path, default=BASE / "media")
    parser.add_argument("--output-dir", type=Path, default=BASE / "output")
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    try:
        validate_timeline()
        if args.dry_run:
            sys.stdout.write(safe_json(timeline_report()))
            return 0
        paths = Paths(args.source.resolve(), args.media_dir.resolve(), args.output_dir.resolve())
        if paths.source.is_relative_to(paths.output) or paths.media.is_relative_to(paths.output):
            raise BuildError("Output directory cannot contain original or downloaded inputs")
        checked = check_inputs(paths)
        if args.check_inputs or not checked["ready"]:
            sys.stdout.write(safe_json(checked))
            return 0 if checked["ready"] else 2
        report = assemble(paths, checked)
        sys.stdout.write(
            safe_json(
                {
                    "status": "TECHNICAL_VALIDATION_PASSED",
                    "archive": report["archive"],
                    "visual_review": report["visual_review"],
                }
            )
        )
        return 0
    except (BuildError, OSError, ValueError, KeyError) as exc:
        message = (
            str(exc)
            if isinstance(exc, BuildError)
            else f"Local {type(exc).__name__}; check inputs and filesystem"
        )
        LOG.error("Assembly stopped: %s", message)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
