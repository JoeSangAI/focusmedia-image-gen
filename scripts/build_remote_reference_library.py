#!/usr/bin/env python3
"""Build a compact public Focus Media reference library and its manifest."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
from pathlib import Path

from PIL import Image, ImageOps


MEDIA_TAGS = {
    "LCD": "lcd",
    "SMART": "smart-screen",
    "POSTER": "poster-frame",
    "MIXED": "mixed-media",
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")


def load_rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def load_curated(path: Path | None) -> tuple[dict[str, dict[str, object]], set[str], str]:
    if path is None:
        return {}, set(), "primary"
    document = json.loads(path.read_text(encoding="utf-8"))
    items = document.get("references", []) if isinstance(document, dict) else document
    if not isinstance(items, list):
        raise ValueError("curated manifest must contain a references array")

    excluded_items = document.get("excluded_sources", []) if isinstance(document, dict) else []
    if not isinstance(excluded_items, list) or not all(isinstance(item, str) for item in excluded_items):
        raise ValueError("excluded_sources must be an array of relative source paths")
    excluded = set(excluded_items)
    unlisted_tier = str(document.get("unlisted_tier", "primary")) if isinstance(document, dict) else "primary"
    if unlisted_tier not in {"primary", "scenario"}:
        raise ValueError("unlisted_tier must be primary or scenario")

    curated: dict[str, dict[str, object]] = {}
    for item in items:
        if not isinstance(item, dict) or not item.get("relative_source"):
            raise ValueError("each curated reference requires relative_source")
        key = str(item["relative_source"])
        if key in curated:
            raise ValueError(f"duplicate curated source: {key}")
        tier = str(item.get("tier", "primary"))
        if tier == "backup":
            tier = "scenario"
            item = {**item, "tier": tier}
        if tier not in {"primary", "scenario"}:
            raise ValueError(f"invalid curated tier for {key}: {tier}")
        curated[key] = item
    overlap = set(curated) & excluded
    if overlap:
        raise ValueError("source cannot be both curated and excluded: " + ", ".join(sorted(overlap)))
    return curated, excluded, unlisted_tier


def resize_jpeg(source: Path, destination: Path, max_dimension: int, quality: int) -> tuple[int, int]:
    destination.parent.mkdir(parents=True, exist_ok=True)
    with Image.open(source) as opened:
        image = ImageOps.exif_transpose(opened).convert("RGB")
        image.thumbnail((max_dimension, max_dimension), Image.Resampling.LANCZOS)
        image.save(destination, "JPEG", quality=quality, optimize=True, progressive=True)
        return image.size


def recommended_for(row: dict[str, str], tier: str) -> list[str]:
    uses: list[str] = []
    if tier == "primary":
        uses.extend(["default-generation", "premium-hardware-presentation"])
    else:
        uses.append("scenario-specific-generation")
    if row["shot_size"] == "wide":
        uses.extend(["wide-impact", "spatial-scale"])
    if row["people"] == "people":
        uses.append("people-scale")
    if row["scene"] == "elevator-inside":
        uses.append("elevator-interior")
    if row["scene"] == "corridor":
        uses.append("corridor-depth")
    if row["angle"] != "front":
        uses.append("alternate-perspective")
    if row["media_type"] == "POSTER" and row["shot_size"] == "wide":
        uses.append("multi-frame-poster-coverage")
    if row["media_type"] == "LCD" and row["shot_size"] == "mid" and row["angle"] == "front":
        uses.append("lcd-hardware-accuracy")
    if row["media_type"] == "SMART" and row["shot_size"] == "mid" and row["angle"] == "front":
        uses.append("smart-screen-hardware-accuracy")
    if row["media_type"] == "POSTER" and row["shot_size"] == "mid" and row["angle"] == "front":
        uses.append("poster-frame-hardware-accuracy")
    return list(dict.fromkeys(uses))


def reference_tags(row: dict[str, str], tier: str, extra_tags: object = None) -> list[str]:
    media = MEDIA_TAGS[row["media_type"]]
    tags = [
        media,
        row["scene"],
        row["angle"],
        row["shot_size"],
        row["people"],
        f"grade-{row['paste_grade'].lower()}",
    ]
    tags.extend(["reference-library", f"tier-{tier}"])
    tags.extend(recommended_for(row, tier))
    if isinstance(extra_tags, list):
        tags.extend(str(tag) for tag in extra_tags if str(tag))
    return list(dict.fromkeys(tags))


def load_demos(path: Path | None) -> list[dict[str, object]]:
    if path is None or not path.exists():
        return []
    return list(json.loads(path.read_text(encoding="utf-8")).get("demos", []))


def build(args: argparse.Namespace) -> dict[str, object]:
    rows = load_rows(args.library_manifest)
    curated, excluded_sources, unlisted_tier = load_curated(args.curated_manifest)
    output_root = args.output_root.resolve()
    output_root.mkdir(parents=True, exist_ok=True)
    references: list[dict[str, object]] = []
    seen_ids: set[str] = set()
    seen_curated: set[str] = set()

    for row in rows:
        relative_source = f"assets/media-library/{row['category_dir']}/{row['new_filename']}"
        if relative_source in excluded_sources:
            continue
        sample = curated.get(relative_source)
        tier = str(sample.get("tier", "primary")) if sample else unlisted_tier
        source = args.library_root / row["category_dir"] / row["new_filename"]
        if not source.is_file():
            raise FileNotFoundError(f"missing library image: {source}")

        if sample:
            seen_curated.add(relative_source)
        reference_id = str(sample["id"]) if sample and sample.get("id") else slug(source.stem)
        if reference_id in seen_ids:
            raise ValueError(f"duplicate reference id: {reference_id}")
        seen_ids.add(reference_id)

        relative_output = Path("references") / "library" / row["category_dir"] / row["new_filename"]
        destination = output_root / relative_output
        width, height = resize_jpeg(source, destination, args.max_dimension, args.quality)
        path = relative_output.as_posix()
        record: dict[str, object] = {
            "id": reference_id,
            "tags": reference_tags(row, tier, sample.get("curation_tags") if sample else None),
            "media_type": row["media_type"],
            "scene": row["scene"],
            "angle": row["angle"],
            "shot_size": row["shot_size"],
            "people": row["people"],
            "paste_grade": row["paste_grade"],
            "source_edit_grade": row["paste_grade"],
            "quality_tier": "premium" if tier == "primary" else "scenario",
            "recommended_for": recommended_for(row, tier),
            "source_width": int(row["width"]),
            "source_height": int(row["height"]),
            "path": path,
            "url": f"{args.base_url.rstrip('/')}/{path}",
            "width": width,
            "height": height,
            "bytes": destination.stat().st_size,
            "sha256": sha256(destination),
        }
        record["curation_tier"] = tier
        if sample and sample.get("thumbnail"):
            record["bundled_sample"] = True
            record["local_thumbnail"] = str(sample["thumbnail"])
        references.append(record)

    missing_curated = set(curated) - seen_curated
    if missing_curated:
        raise ValueError(
            "curated sources missing from library manifest: "
            + ", ".join(sorted(missing_curated))
        )

    references.sort(key=lambda item: str(item["id"]))
    manifest = {
        "schema_version": "4.0",
        "name": "focusmedia-image-gen-remote-assets",
        "base_url": args.base_url.rstrip("/"),
        "generated_for": "focusmedia-image-gen skill curated public reference library",
        "security_model": "public read-only static assets; no upload or delete endpoint",
        "reference_delivery": {
            "remote_reference_count": len(references),
            "primary_reference_count": sum(item["curation_tier"] == "primary" for item in references),
            "scenario_reference_count": sum(item["curation_tier"] == "scenario" for item in references),
            "excluded_reference_count": len(excluded_sources),
            "bundled_thumbnail_count": sum(1 for item in references if item.get("bundled_sample")),
            "remote_max_dimension": args.max_dimension,
            "remote_jpeg_quality": args.quality,
        },
        "selection_policy": {
            "default_tier": "primary",
            "primary_rule": "Premium, clean, hardware-focused references for default generation.",
            "scenario_rule": "Purpose-specific references for wide impact, spatial scale, people, multi-frame poster coverage, interiors, corridors, and alternate perspectives.",
            "source_edit_grade_rule": "A/B/C records direct display-replacement confidence, not whether a photo is visually acceptable for a scene.",
        },
        "demos": load_demos(args.existing_manifest),
        "references": references,
    }
    manifest_path = output_root / "manifests" / "remote-manifest.json"
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return {
        "manifest": str(manifest_path),
        "reference_count": len(references),
        "bundled_sample_count": manifest["reference_delivery"]["bundled_thumbnail_count"],
        "total_bytes": sum(int(item["bytes"]) for item in references),
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Build remote-ready Focus Media reference images and manifest."
    )
    parser.add_argument("--library-root", required=True, type=Path)
    parser.add_argument("--library-manifest", required=True, type=Path)
    parser.add_argument("--output-root", required=True, type=Path)
    parser.add_argument("--base-url", required=True)
    parser.add_argument("--curated-manifest", type=Path)
    parser.add_argument("--existing-manifest", type=Path)
    parser.add_argument("--max-dimension", type=int, default=1200)
    parser.add_argument("--quality", type=int, default=86)
    args = parser.parse_args()
    if args.max_dimension < 256:
        raise SystemExit("--max-dimension must be at least 256")
    if not 1 <= args.quality <= 100:
        raise SystemExit("--quality must be between 1 and 100")

    report = build(args)
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
