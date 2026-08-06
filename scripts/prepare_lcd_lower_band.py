#!/usr/bin/env python3
"""Build and enforce the double protected-band workflow for LCD lower strips."""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from pathlib import Path

from PIL import Image, ImageDraw


TARGET_RATIO = 16 / 3
DEFAULT_CANVAS = (1536, 1024)
DEFAULT_OUTPUT = (1920, 360)


def parse_size(value: str) -> tuple[int, int]:
    try:
        width_text, height_text = value.lower().split("x", 1)
        width, height = int(width_text), int(height_text)
    except (AttributeError, TypeError, ValueError) as exc:
        raise argparse.ArgumentTypeError("size must look like 1920x360") from exc
    if width <= 0 or height <= 0:
        raise argparse.ArgumentTypeError("size values must be positive")
    return width, height


def parse_box(value: str) -> tuple[int, int, int, int]:
    try:
        left, top, right, bottom = (int(part) for part in value.split(","))
    except (AttributeError, TypeError, ValueError) as exc:
        raise argparse.ArgumentTypeError(
            "box must look like left,top,right,bottom"
        ) from exc
    if right <= left or bottom <= top:
        raise argparse.ArgumentTypeError("box must have positive width and height")
    return left, top, right, bottom


def exact_center_band_box(size: tuple[int, int]) -> tuple[int, int, int, int]:
    """Return the largest centered integer rectangle with an exact 16:3 ratio."""
    width, height = size
    unit = min(width // 16, height // 3)
    if unit < 1:
        raise ValueError(f"canvas is too small for a 16:3 band: {width}x{height}")
    band_width, band_height = unit * 16, unit * 3
    left = (width - band_width) // 2
    top = (height - band_height) // 2
    return left, top, left + band_width, top + band_height


@dataclass(frozen=True)
class BandGeometry:
    canvas_size: tuple[int, int]
    extraction_box: tuple[int, int, int, int]
    content_safe_box: tuple[int, int, int, int]
    target_ratio: str = "16:3"


def build_geometry(
    size: tuple[int, int],
    safe_horizontal: float = 0.04,
    safe_vertical: float = 0.125,
) -> BandGeometry:
    if not 0 <= safe_horizontal < 0.5 or not 0 <= safe_vertical < 0.5:
        raise ValueError("safe insets must be between 0 and 0.5")
    left, top, right, bottom = exact_center_band_box(size)
    band_width, band_height = right - left, bottom - top
    inset_x = round(band_width * safe_horizontal)
    inset_y = round(band_height * safe_vertical)
    safe_box = (
        left + inset_x,
        top + inset_y,
        right - inset_x,
        bottom - inset_y,
    )
    return BandGeometry(size, (left, top, right, bottom), safe_box)


def build_guide(geometry: BandGeometry) -> Image.Image:
    """Create a visual guide: striped blocked area, exact band, and inner safe box."""
    width, height = geometry.canvas_size
    guide = Image.new("RGB", geometry.canvas_size, "#202224")
    draw = ImageDraw.Draw(guide)
    stripe = max(18, width // 36)
    for start in range(-height, width + height, stripe * 3):
        draw.line(
            (start, height, start + height, 0),
            fill="#542629",
            width=stripe,
        )

    left, top, right, bottom = geometry.extraction_box
    draw.rectangle((left, top, right - 1, bottom - 1), fill="#ffd926")

    safe_left, safe_top, safe_right, safe_bottom = geometry.content_safe_box
    line_width = max(3, width // 512)
    draw.rectangle(
        (safe_left, safe_top, safe_right - 1, safe_bottom - 1),
        outline="#fff7bf",
        width=line_width,
    )
    return guide


def build_edit_mask(geometry: BandGeometry) -> Image.Image:
    """Create an RGBA mask: opaque outside, transparent inside the exact band."""
    mask = Image.new("RGBA", geometry.canvas_size, (255, 255, 255, 255))
    alpha = Image.new("L", geometry.canvas_size, 255)
    draw = ImageDraw.Draw(alpha)
    left, top, right, bottom = geometry.extraction_box
    draw.rectangle((left, top, right - 1, bottom - 1), fill=0)
    mask.putalpha(alpha)
    return mask


def validate_band_box(
    image_size: tuple[int, int],
    band_box: tuple[int, int, int, int],
    tolerance: float = 0.02,
) -> dict[str, object]:
    image_width, image_height = image_size
    left, top, right, bottom = band_box
    if left < 0 or top < 0 or right > image_width or bottom > image_height:
        raise ValueError("band box extends outside the returned image")
    width, height = right - left, bottom - top
    ratio = width / height
    difference = abs(ratio - TARGET_RATIO)
    report = {
        "image_size": list(image_size),
        "band_box": list(band_box),
        "band_size": [width, height],
        "ratio": ratio,
        "target_ratio": TARGET_RATIO,
        "ratio_difference": difference,
        "passed": difference <= tolerance,
    }
    if not report["passed"]:
        raise ValueError(
            f"returned protected band is {width}x{height} ({ratio:.4f}:1), "
            f"not 16:3; maximum ratio difference is {tolerance}"
        )
    return report


def crop_exact_band(
    image: Image.Image,
    output_size: tuple[int, int] = DEFAULT_OUTPUT,
) -> tuple[Image.Image, dict[str, object]]:
    if output_size[0] / output_size[1] != TARGET_RATIO:
        raise ValueError("LCD lower-strip output must use the exact 16:3 ratio")
    crop_box = exact_center_band_box(image.size)
    cropped = image.convert("RGB").crop(crop_box)
    output = cropped.resize(output_size, Image.Resampling.LANCZOS)
    report = {
        "input_size": list(image.size),
        "crop_box": list(crop_box),
        "crop_size": list(cropped.size),
        "output_size": list(output_size),
        "target_ratio": "16:3",
        "non_uniform_stretch": False,
    }
    return output, report


def write_json(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def template_command(args: argparse.Namespace) -> None:
    geometry = build_geometry(args.canvas, args.safe_horizontal, args.safe_vertical)
    args.guide.parent.mkdir(parents=True, exist_ok=True)
    args.mask.parent.mkdir(parents=True, exist_ok=True)
    build_guide(geometry).save(args.guide)
    build_edit_mask(geometry).save(args.mask)
    if args.manifest:
        payload = asdict(geometry)
        payload["safe_horizontal"] = args.safe_horizontal
        payload["safe_vertical"] = args.safe_vertical
        payload["guide"] = str(args.guide)
        payload["mask"] = str(args.mask)
        write_json(args.manifest, payload)


def crop_command(args: argparse.Namespace) -> None:
    source = Image.open(args.input)
    output, report = crop_exact_band(source, args.size)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    output.save(args.output, quality=96)
    report.update({"input": str(args.input), "output": str(args.output)})
    if args.report:
        write_json(args.report, report)


def validate_command(args: argparse.Namespace) -> None:
    with Image.open(args.input) as source:
        report = validate_band_box(source.size, args.band_box, args.tolerance)
    report["input"] = str(args.input)
    if args.report:
        write_json(args.report, report)
    print(json.dumps(report, ensure_ascii=False, indent=2))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Prepare and enforce the LCD 16:3 double protected-band workflow."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    template = subparsers.add_parser("template")
    template.add_argument("--canvas", type=parse_size, default=DEFAULT_CANVAS)
    template.add_argument("--guide", required=True, type=Path)
    template.add_argument("--mask", required=True, type=Path)
    template.add_argument("--manifest", type=Path)
    template.add_argument("--safe-horizontal", type=float, default=0.04)
    template.add_argument("--safe-vertical", type=float, default=0.125)
    template.set_defaults(handler=template_command)

    crop = subparsers.add_parser("crop")
    crop.add_argument("--input", required=True, type=Path)
    crop.add_argument("--output", required=True, type=Path)
    crop.add_argument("--size", type=parse_size, default=DEFAULT_OUTPUT)
    crop.add_argument("--report", type=Path)
    crop.set_defaults(handler=crop_command)

    validate = subparsers.add_parser("validate-band")
    validate.add_argument("--input", required=True, type=Path)
    validate.add_argument("--band-box", required=True, type=parse_box)
    validate.add_argument("--tolerance", type=float, default=0.02)
    validate.add_argument("--report", type=Path)
    validate.set_defaults(handler=validate_command)
    return parser


def main() -> None:
    args = build_parser().parse_args()
    args.handler(args)


if __name__ == "__main__":
    main()
