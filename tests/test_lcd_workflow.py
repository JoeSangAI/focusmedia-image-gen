from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from composite_lcd_screens import (  # noqa: E402
    DEFAULT_LOWER_QUAD,
    DEFAULT_MAIN_QUAD,
    DEFAULT_TEMPLATE,
    quad_bounds,
    render,
)
from normalize_media_creative import normalize  # noqa: E402
from prepare_lcd_lower_band import (  # noqa: E402
    build_edit_mask,
    build_geometry,
    crop_exact_band,
    validate_band_box,
)
from validate_media_scale import validate_lcd_scale  # noqa: E402


class LcdWorkflowTest(unittest.TestCase):
    def test_standard_template_has_official_screen_geometry(self) -> None:
        self.assertEqual(DEFAULT_TEMPLATE.name, "lcd-32-standard.png")
        main = quad_bounds(DEFAULT_MAIN_QUAD)
        lower = quad_bounds(DEFAULT_LOWER_QUAD)
        self.assertAlmostEqual((main[2] - main[0]) / (main[3] - main[1]), 16 / 9, delta=0.04)
        self.assertAlmostEqual((lower[2] - lower[0]) / (lower[3] - lower[1]), 16 / 3, delta=0.12)

    def test_normalizers_keep_official_output_size(self) -> None:
        source = Image.new("RGB", (1672, 941), "#1b5ec7")
        self.assertEqual(normalize(source, (1920, 360), "safe-band").size, (1920, 360))
        self.assertEqual(normalize(source, (1920, 360), "contain-blur").size, (1920, 360))

    def test_double_protected_band_is_exact_and_has_safe_inner_area(self) -> None:
        geometry = build_geometry((1536, 1024))
        left, top, right, bottom = geometry.extraction_box
        self.assertEqual((right - left, bottom - top), (1536, 288))
        self.assertEqual((right - left) / (bottom - top), 16 / 3)
        self.assertGreater(geometry.content_safe_box[0], left)
        self.assertLess(geometry.content_safe_box[2], right)
        mask = build_edit_mask(geometry)
        self.assertEqual(mask.getpixel((10, 10))[3], 255)
        self.assertEqual(mask.getpixel((768, 512))[3], 0)

    def test_nearby_but_wrong_lower_band_is_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "not 16:3"):
            validate_band_box((1672, 941), (0, 313, 1672, 675))
        report = validate_band_box((1672, 941), (4, 314, 1668, 626))
        self.assertTrue(report["passed"])
        self.assertEqual(report["band_size"], [1664, 312])

    def test_crop_returns_exact_official_lower_strip(self) -> None:
        output, report = crop_exact_band(Image.new("RGB", (1672, 941), "#ffd926"))
        self.assertEqual(output.size, (1920, 360))
        self.assertEqual(report["crop_box"], [4, 314, 1668, 626])
        self.assertFalse(report["non_uniform_stretch"])

    def test_composite_changes_only_approved_lcd_surfaces(self) -> None:
        before = Image.open(DEFAULT_TEMPLATE).convert("RGB")
        with tempfile.TemporaryDirectory() as temp_dir:
            temp = Path(temp_dir)
            main_path = temp / "main.png"
            lower_path = temp / "lower.png"
            Image.new("RGB", (1920, 1080), "#0066ff").save(main_path)
            Image.new("RGB", (1920, 360), "#ff6600").save(lower_path)
            after = render(DEFAULT_TEMPLATE, main_path, lower_path, DEFAULT_MAIN_QUAD, DEFAULT_LOWER_QUAD, 0.0)

        diff = ImageChops.difference(before, after)
        allowed = Image.new("L", before.size, 0)
        draw = ImageDraw.Draw(allowed)
        for quad in (DEFAULT_MAIN_QUAD, DEFAULT_LOWER_QUAD):
            left, top, right, bottom = quad_bounds(quad)
            draw.rectangle((left - 2, top - 2, right + 2, bottom + 2), fill=255)
        outside = ImageChops.multiply(diff.convert("L"), allowed.point(lambda value: 255 - value))
        self.assertIsNone(outside.getbbox())

    def test_scale_gate_rejects_oversized_lcd_and_accepts_corrected_one(self) -> None:
        rejected = validate_lcd_scale(
            door=(284, 145, 558, 997),
            media=(620, 236, 1137, 670),
            button=(840, 707, 872, 787),
        )
        self.assertFalse(rejected["passed"])
        accepted = validate_lcd_scale(
            door=(284, 145, 558, 997),
            media=(704, 315, 1016, 583),
            button=(1067, 467, 1101, 545),
        )
        self.assertTrue(accepted["passed"])


if __name__ == "__main__":
    unittest.main()
