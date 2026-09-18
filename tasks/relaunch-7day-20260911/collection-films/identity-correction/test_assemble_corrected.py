"""Focused offline checks for the corrected film assembler."""

import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import assemble_corrected as assembly


class TimelineTests(unittest.TestCase):
    def test_exact_totals_and_source_ranges(self) -> None:
        expected = {
            "black-rose": [(0, 48), (48, 72), (72, 120), (120, 192)],
            "town-line-main": [(0, 24), (24, 48), (72, 120), (120, 168)],
        }
        for film in assembly.FILMS:
            self.assertEqual(sum(c.frames for c in film.cuts), film.frames)
            source = [(c.start, c.end) for c in film.cuts if c.clip == "SOURCE"]
            self.assertEqual(source, expected.get(film.id, []))
        assembly.validate_timeline()

    def test_source_mapping_crosses_discontinuous_original_intervals(self) -> None:
        cuts = assembly.expand_source(assembly.Cut("SOURCE", 60, 132))
        self.assertEqual([(c.start, c.end) for c in cuts], [(755, 767), (983, 1031), (1391, 1403)])
        self.assertEqual(sum(c.frames for c in cuts), 72)

    def test_invalid_source_ranges_fail(self) -> None:
        for start, end in [(-1, 1), (0, 193), (12, 12), (40, 12)]:
            with self.assertRaises(assembly.BuildError):
                assembly.expand_source(assembly.Cut("SOURCE", start, end))

    def test_door_and_red_reuse_do_not_reintroduce_rejected_frames(self) -> None:
        for film in assembly.FILMS:
            for cut in film.cuts:
                if cut.clip == "DOOR":
                    self.assertEqual((cut.start, cut.end), (0, 12))
            red = [c for c in film.cuts if c.clip == "KR"]
            if len(red) == 2:
                self.assertLessEqual(red[0].end, red[1].start)

    def test_source_pixels_fail_even_with_correct_frame_count(self) -> None:
        film = assembly.Film("example", "Example", 3, (assembly.Cut("SOURCE", 0, 3),))
        original = [str(i) for i in range(1561)]
        selected = original[695:698]
        self.assertEqual(assembly.verify_source_pixels(film, selected, original), 3)
        selected[1] = "changed"
        with self.assertRaises(assembly.BuildError):
            assembly.verify_source_pixels(film, selected, original)

    def test_exact_timestamps_and_forced_boundary_keyframes(self) -> None:
        frames = [
            {"best_effort_timestamp": n * 1001, "key_frame": int(n in [0, 2])} for n in range(4)
        ]
        self.assertEqual(assembly.validate_frame_records(frames, 4, {0, 2}), [0, 2])
        frames[2]["best_effort_timestamp"] += 1
        with self.assertRaises(assembly.BuildError):
            assembly.validate_frame_records(frames, 4, {0, 2})

    def test_missing_boundary_keyframe_is_rejected(self) -> None:
        frames = [{"best_effort_timestamp": n * 1001, "key_frame": int(n == 0)} for n in range(3)]
        with self.assertRaises(assembly.BuildError):
            assembly.validate_frame_records(frames, 3, {0, 2})

    def test_private_url_fields_cannot_be_serialized(self) -> None:
        for value in [
            "https://example.invalid/asset",
            "asset?_jwt=SECRET",
            "X-Amz-Signature=SECRET",
        ]:
            with self.assertRaises(assembly.BuildError):
                assembly.safe_json({"value": value})

    def test_subprocess_failure_does_not_echo_command_or_stderr(self) -> None:
        result = subprocess.CompletedProcess(["ffmpeg"], 1, stdout=b"", stderr=b"SECRET")
        with patch.object(assembly.subprocess, "run", return_value=result):
            with self.assertRaisesRegex(assembly.BuildError, "fixture failed") as raised:
                assembly.run(["ffmpeg", "SECRET"], "fixture")
        self.assertNotIn("SECRET", str(raised.exception))

    def test_zip_whitelist_and_crc(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "safe.json").write_text(assembly.safe_json({"frames": 480}))
            (root / "private-downloads.json").write_text("_jwt=SECRET")
            result = assembly.make_archive(root, ["safe.json"])
            self.assertEqual(result["crc"], "PASS")
            with assembly.zipfile.ZipFile(root / str(result["file"])) as archive:
                self.assertEqual(archive.namelist(), ["safe.json"])


@unittest.skipUnless(
    shutil.which("ffmpeg")
    and assembly.ORIGINAL.is_file()
    and (assembly.BASE / "media" / "TRAIN.mp4").is_file(),
    "Requires local FFmpeg and retained source/train inputs",
)
class TinyMediaIntegrationTests(unittest.TestCase):
    def test_half_millisecond_join_preserves_original_frames(self) -> None:
        """A one-second temporary fixture, never a final film assembly."""
        with tempfile.TemporaryDirectory(prefix="town-line-assembler-test-") as directory:
            output = Path(directory)
            (output / "work").mkdir()
            paths = assembly.Paths(assembly.ORIGINAL, assembly.BASE / "media", output)
            film = assembly.Film(
                "fixture",
                "Fixture",
                24,
                (assembly.Cut("TRAIN", 0, 12), assembly.Cut("SOURCE", 0, 12)),
            )
            cuts = {cut: assembly.make_cut(paths, cut) for cut in assembly.expanded_cuts(film)}
            master = assembly.make_master(paths, film, cuts)
            info = assembly.validate_export(master, 24, {0, 12})
            self.assertTrue(info["all_frame_timestamps_exact"])
            original = assembly.frame_hashes(assembly.ORIGINAL)
            self.assertEqual(
                assembly.verify_source_pixels(film, assembly.frame_hashes(master), original), 12
            )
            viewing = output / "fixture.mp4"
            assembly.run(
                ["ffmpeg", "-v", "error", "-nostdin", "-n", "-i", str(master), "-map", "0:v:0"]
                + assembly.encoder_args(viewing, {0, 12}, lossless=False),
                "Fixture viewing",
            )
            assembly.validate_export(viewing, 24, {0, 12})
            self.assertTrue((output / assembly.make_sheet(paths, film, viewing)).is_file())


if __name__ == "__main__":
    unittest.main()
