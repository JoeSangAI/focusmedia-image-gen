from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from fractions import Fraction
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from compose_lcd_tvc_demo import (  # noqa: E402
    DEFAULT_LOWER_BOX,
    DEFAULT_MAIN_BOX,
    DEFAULT_TEMPLATE,
    choose_audio_mode,
    choose_main_crop,
    frame_from_time,
)


class TvcWorkflowTest(unittest.TestCase):
    def test_formal_frame_is_the_default(self) -> None:
        self.assertEqual(DEFAULT_TEMPLATE.name, "lcd-32-standard.png")
        self.assertEqual(DEFAULT_MAIN_BOX, (418, 74, 1084, 610))
        self.assertEqual(DEFAULT_LOWER_BOX, (418, 802, 1084, 203))

    def test_source_variant_crop_is_validated(self) -> None:
        self.assertEqual(choose_main_crop(1920, 1440), (0, 0, 1920, 1080))
        self.assertEqual(choose_main_crop(1920, 1080), (0, 0, 1920, 1080))
        with self.assertRaisesRegex(ValueError, "expected a validated 4:3 or 16:9"):
            choose_main_crop(1000, 1000)

    def test_switch_time_must_land_on_a_whole_frame(self) -> None:
        self.assertEqual(frame_from_time("14.12", Fraction(25, 1)), 353)
        with self.assertRaisesRegex(ValueError, "whole frame"):
            frame_from_time("14.13", Fraction(25, 1))

    def test_audio_is_copied_only_when_mp4_compatible(self) -> None:
        self.assertEqual(choose_audio_mode("aac", "auto"), "copy")
        self.assertEqual(choose_audio_mode("mp3", "auto"), "aac")
        self.assertEqual(choose_audio_mode(None, "auto"), "none")
        with self.assertRaisesRegex(ValueError, "not approved"):
            choose_audio_mode("mp3", "copy")

    @unittest.skipUnless(
        shutil.which("ffmpeg") and shutil.which("ffprobe"),
        "ffmpeg is required for the integration test",
    )
    def test_short_tvc_build_preserves_frames_and_audio(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp = Path(temp_dir)
            source = temp / "source.mp4"
            tail = temp / "tail.png"
            lower = temp / "lower.png"
            template = temp / "template.png"
            output = temp / "output.mp4"
            report = temp / "report.json"
            contact = temp / "contact.png"

            Image.new("RGB", (320, 180), "#ffcc00").save(tail)
            Image.new("RGB", (320, 60), "#0066ff").save(lower)
            Image.new("RGB", (320, 180), "#eeeeee").save(template)
            subprocess.run(
                [
                    "ffmpeg",
                    "-y",
                    "-v",
                    "error",
                    "-f",
                    "lavfi",
                    "-i",
                    "testsrc2=size=320x240:rate=25:duration=0.4",
                    "-f",
                    "lavfi",
                    "-i",
                    "sine=frequency=1000:sample_rate=44100:duration=0.4",
                    "-shortest",
                    "-c:v",
                    "libx264",
                    "-pix_fmt",
                    "yuv420p",
                    "-c:a",
                    "aac",
                    str(source),
                ],
                check=True,
            )
            subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "compose_lcd_tvc_demo.py"),
                    "--source",
                    str(source),
                    "--tail",
                    str(tail),
                    "--lower",
                    str(lower),
                    "--template",
                    str(template),
                    "--main-box",
                    "20,10,160,90",
                    "--lower-box",
                    "20,140,160,30",
                    "--switch-frame",
                    "8",
                    "--preset",
                    "ultrafast",
                    "--output",
                    str(output),
                    "--report",
                    str(report),
                    "--contact-sheet",
                    str(contact),
                ],
                check=True,
            )

            payload = json.loads(report.read_text(encoding="utf-8"))
            self.assertEqual(payload["source_crop"], [0, 0, 320, 180])
            self.assertEqual(payload["switch_frame"], 8)
            self.assertEqual(payload["source_frames"], 10)
            self.assertEqual(payload["audio_preservation"], "stream_copy")
            self.assertEqual(payload["output_probe"]["width"], 320)
            self.assertEqual(payload["output_probe"]["height"], 180)
            self.assertEqual(payload["output_probe"]["frames"], 10)
            self.assertEqual(payload["output_probe"]["audio_codec"], "aac")
            self.assertTrue(output.is_file())
            self.assertTrue(contact.is_file())


if __name__ == "__main__":
    unittest.main()
