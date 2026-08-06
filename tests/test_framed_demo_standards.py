from __future__ import annotations

import json
import unittest
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
ASSET_DIR = ROOT / "assets" / "framed-demo-standards"

EXPECTED = {
    "smart-32-standard.png": ((1440, 1920), "32-inch smart screen"),
    "lcd-32-standard.png": ((1920, 1080), "32-inch building LCD"),
    "poster-frame-standard.png": ((1440, 1920), "poster frame"),
}


class FramedDemoStandardsTest(unittest.TestCase):
    def test_complete_standard_frames_are_valid_and_correctly_named(self) -> None:
        for name, (size, media_type) in EXPECTED.items():
            path = ASSET_DIR / name
            self.assertTrue(path.is_file())
            self.assertGreater(path.stat().st_size, 100_000)
            with Image.open(path) as image:
                self.assertEqual(image.format, "PNG")
                self.assertEqual(image.size, size)
                image.verify()

            manifest = json.loads((ASSET_DIR / "manifest.json").read_text(encoding="utf-8"))
            record = {item["file"]: item for item in manifest["assets"]}[name]
            self.assertIn(media_type, record["media_type"])
            self.assertNotIn("source_absolute_path", record)
            self.assertTrue(record["source_provenance"])
            self.assertEqual(record["role"], "framed_demo_standard")

    def test_manifest_covers_exactly_the_shipped_standards(self) -> None:
        manifest = json.loads((ASSET_DIR / "manifest.json").read_text(encoding="utf-8"))
        self.assertEqual(manifest["schema_version"], 1)
        records = {item["file"]: item for item in manifest["assets"]}
        self.assertEqual(set(records), set(EXPECTED))
        for record in records.values():
            forbidden = " ".join(record["forbidden_use"]).lower()
            self.assertIn("environment photo", forbidden)
            self.assertIn("flat-paste", forbidden)

    def test_skill_documents_standard_and_remote_reference_routes(self) -> None:
        skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("smart-32-standard.png", skill)
        self.assertIn("156 张已分级的远端参考图库", skill)
        self.assertIn("下载通过校验的图片", skill)
        self.assertIn("不得从环境照片裁出设备", skill)


if __name__ == "__main__":
    unittest.main()
