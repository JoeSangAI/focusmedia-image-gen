from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path
from types import SimpleNamespace


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from select_media_references import select_references  # noqa: E402


def args(**overrides: object) -> SimpleNamespace:
    values: dict[str, object] = {
        "media": None,
        "tag": [],
        "scene": "any",
        "angle": "any",
        "shot_size": "any",
        "people": "any",
        "tier": "primary",
        "use_case": [],
        "max_grade": "A",
        "limit": 999,
    }
    values.update(overrides)
    return SimpleNamespace(**values)


class RemoteReferenceLibraryTest(unittest.TestCase):
    def setUp(self) -> None:
        self.manifest = json.loads(
            (ROOT / "references" / "remote-manifest.json").read_text(encoding="utf-8")
        )

    def test_graded_remote_library_and_compact_local_samples(self) -> None:
        self.assertEqual(self.manifest["schema_version"], "4.0")
        self.assertEqual(self.manifest["reference_delivery"]["remote_reference_count"], 156)
        self.assertEqual(self.manifest["reference_delivery"]["primary_reference_count"], 58)
        self.assertEqual(self.manifest["reference_delivery"]["scenario_reference_count"], 98)
        self.assertEqual(self.manifest["reference_delivery"]["excluded_reference_count"], 27)
        self.assertEqual(self.manifest["reference_delivery"]["bundled_thumbnail_count"], 16)
        references = self.manifest["references"]
        self.assertEqual(len(references), 156)
        self.assertEqual(len({item["id"] for item in references}), 156)
        self.assertEqual(sum(bool(item.get("bundled_sample")) for item in references), 16)
        self.assertEqual(sum(item["media_type"] == "LCD" for item in references), 83)
        self.assertEqual(sum(item["media_type"] == "SMART" for item in references), 21)
        self.assertEqual(sum(item["media_type"] == "POSTER" for item in references), 52)
        self.assertTrue(all(item["media_type"] != "MIXED" for item in references))
        self.assertTrue(all(item["curation_tier"] in {"primary", "scenario"} for item in references))
        self.assertTrue(all(item["recommended_for"] for item in references))

        local_samples = json.loads(
            (ROOT / "assets" / "reference-thumbnails" / "manifest.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertEqual(len(local_samples), 16)
        self.assertEqual(
            len(list((ROOT / "assets" / "reference-thumbnails").glob("*.jpg"))), 16
        )

    def test_every_remote_reference_is_publicly_addressable_without_local_paths(self) -> None:
        base_url = self.manifest["base_url"].rstrip("/") + "/"
        for item in self.manifest["references"]:
            self.assertTrue(item["url"].startswith(base_url))
            self.assertEqual(item["url"], base_url + item["path"])
            self.assertTrue(item["path"].startswith("references/library/"))
            self.assertEqual(len(item["sha256"]), 64)
            self.assertNotIn("/Users/", json.dumps(item, ensure_ascii=False))

    def test_selector_defaults_to_visual_primary_references(self) -> None:
        lcd = select_references(
            self.manifest,
            args(media="lcd", scene="elevator-hall", max_grade="A", limit=12),
        )
        self.assertTrue(lcd)
        self.assertTrue(
            all(
                item["media_type"] == "LCD"
                and item["scene"] == "elevator-hall"
                and item["paste_grade"] == "A"
                and item["curation_tier"] == "primary"
                for item in lcd
            )
        )

        smart_scenario = select_references(
            self.manifest,
            args(media="smart", tier="scenario", use_case=["wide-impact"], max_grade="C", limit=12),
        )
        self.assertTrue(smart_scenario)
        self.assertTrue(
            all(
                item["media_type"] == "SMART"
                and item["curation_tier"] == "scenario"
                and "wide-impact" in item["recommended_for"]
                for item in smart_scenario
            )
        )

        poster_array = select_references(
            self.manifest,
            args(
                media="poster",
                tier="scenario",
                use_case=["multi-frame-poster-coverage"],
                max_grade="C",
                limit=12,
            ),
        )
        self.assertTrue(poster_array)
        self.assertTrue(
            all("multi-frame-poster-coverage" in item["recommended_for"] for item in poster_array)
        )


if __name__ == "__main__":
    unittest.main()
