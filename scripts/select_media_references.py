#!/usr/bin/env python3
"""Select Focus Media references from the complete public remote manifest."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


MEDIA_ALIASES = {
    "lcd": "lcd",
    "电梯电视": "lcd",
    "楼宇": "lcd",
    "楼宇lcd": "lcd",
    "smart": "smart-screen",
    "smart-screen": "smart-screen",
    "智能屏": "smart-screen",
    "poster": "poster-frame",
    "poster-frame": "poster-frame",
    "海报": "poster-frame",
    "框架": "poster-frame",
    "海报框架": "poster-frame",
    "mixed": "mixed-media",
    "mixed-media": "mixed-media",
    "混合": "mixed-media",
}
GRADE_RANK = {"A": 0, "B": 1, "C": 2}


def default_manifest() -> Path:
    return Path(__file__).resolve().parents[1] / "references" / "remote-manifest.json"


def normalize_tag(value: str | None) -> str | None:
    if not value:
        return None
    key = value.strip().lower().replace(" ", "")
    return MEDIA_ALIASES.get(key, key)


def load_manifest(path: Path) -> dict:
    return json.loads(path.expanduser().read_text(encoding="utf-8"))


def matches(item: dict, args: argparse.Namespace) -> bool:
    tags = {str(tag).lower() for tag in item.get("tags", [])}
    media = normalize_tag(args.media)
    if media and media not in tags:
        return False
    requested_tags = {normalize_tag(tag) or tag.lower() for tag in args.tag}
    if not requested_tags.issubset(tags):
        return False
    tier = str(item.get("curation_tier", "primary"))
    if args.tier != "any" and tier != args.tier:
        return False
    requested_uses = {value.strip().lower() for value in args.use_case if value.strip()}
    item_uses = {str(value).lower() for value in item.get("recommended_for", [])}
    if not requested_uses.issubset(item_uses):
        return False
    for field in ("scene", "angle", "shot_size", "people"):
        selected = getattr(args, field)
        item_value = item.get(field)
        if selected != "any" and item_value not in {selected, None} and item_value != selected:
            return False
        if selected != "any" and item_value is None and selected not in tags:
            return False
    grade = str(item.get("paste_grade", "A")).upper()
    return GRADE_RANK.get(grade, 99) <= GRADE_RANK[args.max_grade]


def sort_key(item: dict) -> tuple[int, int, str]:
    tier_rank = {"primary": 0, "scenario": 1}.get(str(item.get("curation_tier", "primary")), 99)
    return (tier_rank, GRADE_RANK.get(str(item.get("paste_grade", "A")).upper(), 99), str(item["id"]))


def select_references(manifest: dict, args: argparse.Namespace) -> list[dict]:
    references = [
        item for item in manifest.get("references", []) if matches(item, args)
    ]
    references.sort(key=sort_key)
    return references[: max(args.limit, 0)]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, default=default_manifest())
    parser.add_argument("--media", help="lcd, smart, poster, mixed, or Chinese alias")
    parser.add_argument("--tag", action="append", default=[], help="Require a tag; repeatable")
    parser.add_argument("--scene", choices=["elevator-hall", "elevator-inside", "corridor", "any"], default="any")
    parser.add_argument("--angle", choices=["front", "angle", "wide", "any"], default="any")
    parser.add_argument("--shot-size", dest="shot_size", choices=["mid", "wide", "any"], default="any")
    parser.add_argument("--people", choices=["nopeople", "people", "any"], default="any")
    parser.add_argument("--tier", choices=["primary", "scenario", "any"], default="primary")
    parser.add_argument("--use-case", action="append", default=[], help="Require a recommended use case; repeatable")
    parser.add_argument(
        "--max-grade",
        choices=["A", "B", "C"],
        default="C",
        help="Maximum source edit grade; this is not an overall visual-quality score",
    )
    parser.add_argument("--limit", type=int, default=8)
    parser.add_argument("--json", action="store_true")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    selected = select_references(load_manifest(args.manifest), args)
    if args.json:
        print(json.dumps(selected, ensure_ascii=False, indent=2))
        return
    for item in selected:
        tags = ", ".join(item.get("tags", []))
        print(f"{item['id']} | {tags} | {item['url']}")


if __name__ == "__main__":
    main()
