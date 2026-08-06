#!/usr/bin/env python3
"""Validate Focus Media LCD scale against a visible elevator doorway."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


Box = tuple[float, float, float, float]


def parse_box(value: str) -> Box:
    try:
        left, top, right, bottom = (float(part) for part in value.split(","))
    except (TypeError, ValueError) as exc:
        raise argparse.ArgumentTypeError(
            "box must look like left,top,right,bottom"
        ) from exc
    if right <= left or bottom <= top:
        raise argparse.ArgumentTypeError("box must have positive width and height")
    return left, top, right, bottom


def overlaps(first: Box, second: Box) -> bool:
    return not (
        first[2] <= second[0]
        or second[2] <= first[0]
        or first[3] <= second[1]
        or second[3] <= first[1]
    )


def in_range(value: float, bounds: tuple[float, float]) -> bool:
    return bounds[0] <= value <= bounds[1]


def validate_lcd_scale(
    door: Box,
    media: Box,
    button: Box | None = None,
) -> dict[str, object]:
    door_height = door[3] - door[1]
    media_width = media[2] - media[0]
    media_height = media[3] - media[1]

    metrics = {
        "media_width_to_door_height": media_width / door_height,
        "media_height_to_door_height": media_height / door_height,
        "media_bottom_height_from_floor": (door[3] - media[3]) / door_height,
    }
    checks = {
        "media_width": in_range(metrics["media_width_to_door_height"], (0.34, 0.39)),
        "media_height": in_range(metrics["media_height_to_door_height"], (0.29, 0.34)),
        "media_bottom_height": in_range(
            metrics["media_bottom_height_from_floor"],
            (0.40, 0.52),
        ),
    }

    if button is not None:
        button_center_y = (button[1] + button[3]) / 2
        metrics["button_center_height_from_floor"] = (
            door[3] - button_center_y
        ) / door_height
        checks["button_reachable_height"] = in_range(
            metrics["button_center_height_from_floor"],
            (0.45, 0.65),
        )
        checks["media_button_do_not_overlap"] = not overlaps(media, button)

    return {
        "medium": "LCD",
        "door_box": list(door),
        "media_box": list(media),
        "button_box": list(button) if button else None,
        "metrics": {key: round(value, 4) for key, value in metrics.items()},
        "checks": checks,
        "passed": all(checks.values()),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--door-box", required=True, type=parse_box)
    parser.add_argument("--media-box", required=True, type=parse_box)
    parser.add_argument("--button-box", type=parse_box)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    report = validate_lcd_scale(args.door_box, args.media_box, args.button_box)
    payload = json.dumps(report, ensure_ascii=False, indent=2)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(payload, encoding="utf-8")
    print(payload)
    raise SystemExit(0 if report["passed"] else 2)


if __name__ == "__main__":
    main()
