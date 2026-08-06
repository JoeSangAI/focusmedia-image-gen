#!/usr/bin/env python3
"""Replace both screens in the formal 32-inch LCD framed-demo standard."""

from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image, ImageDraw

from composite_poster_quad import add_glass_effect, parse_quad, perspective_coefficients


SCRIPT_DIR = Path(__file__).resolve().parent
DEFAULT_TEMPLATE = (
    SCRIPT_DIR.parent
    / "assets"
    / "framed-demo-standards"
    / "lcd-32-standard.png"
)

# Clockwise: top-left, top-right, bottom-right, bottom-left.
# These coordinates are calibrated against lcd-32-standard.png. The point spans
# are near-exact 16:9 and 16:3; inclusive image bounds add one antialiased edge.
DEFAULT_MAIN_QUAD = [
    (418.0, 74.0),
    (1501.0, 74.0),
    (1501.0, 683.0),
    (418.0, 683.0),
]
DEFAULT_LOWER_QUAD = [
    (418.0, 802.0),
    (1501.0, 802.0),
    (1501.0, 1005.0),
    (418.0, 1005.0),
]


def quad_bounds(quad: list[tuple[float, float]]) -> tuple[int, int, int, int]:
    xs = [point[0] for point in quad]
    ys = [point[1] for point in quad]
    return int(min(xs)), int(min(ys)), int(max(xs)) + 1, int(max(ys)) + 1


def paste_quad(
    background: Image.Image,
    creative: Image.Image,
    quad: list[tuple[float, float]],
    glass: float,
) -> Image.Image:
    surface = add_glass_effect(creative.convert("RGB"), glass).convert("RGBA")
    source = [
        (0.0, 0.0),
        (float(surface.width), 0.0),
        (float(surface.width), float(surface.height)),
        (0.0, float(surface.height)),
    ]
    coeffs = perspective_coefficients(source, quad)
    warped = surface.transform(
        background.size,
        Image.Transform.PERSPECTIVE,
        coeffs,
        Image.Resampling.BICUBIC,
    )
    mask = Image.new("L", surface.size, 255)
    warped_mask = mask.transform(
        background.size,
        Image.Transform.PERSPECTIVE,
        coeffs,
        Image.Resampling.BICUBIC,
    )
    return Image.composite(warped.convert("RGB"), background.convert("RGB"), warped_mask)


def validate_creative(path: Path, expected_ratio: float, label: str) -> Image.Image:
    image = Image.open(path).convert("RGB")
    ratio = image.width / image.height
    if abs(ratio - expected_ratio) > 0.01:
        raise ValueError(
            f"{label} must already match its official aspect ratio; "
            f"got {image.width}x{image.height}"
        )
    return image


def render(
    template: Path,
    main_path: Path,
    lower_path: Path,
    main_quad: list[tuple[float, float]],
    lower_quad: list[tuple[float, float]],
    glass: float,
) -> Image.Image:
    background = Image.open(template).convert("RGB")
    main = validate_creative(main_path, 16 / 9, "LCD main creative")
    lower = validate_creative(lower_path, 16 / 3, "LCD lower-screen creative")
    result = paste_quad(background, main, main_quad, glass)
    return paste_quad(result, lower, lower_quad, glass)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--main", required=True, type=Path)
    parser.add_argument("--lower", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--template", type=Path, default=DEFAULT_TEMPLATE)
    parser.add_argument("--main-quad", type=parse_quad)
    parser.add_argument("--lower-quad", type=parse_quad)
    parser.add_argument("--glass", type=float, default=0.12)
    args = parser.parse_args()

    result = render(
        args.template,
        args.main,
        args.lower,
        args.main_quad or DEFAULT_MAIN_QUAD,
        args.lower_quad or DEFAULT_LOWER_QUAD,
        max(0.0, min(args.glass, 1.0)),
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    result.save(args.output, quality=96)


if __name__ == "__main__":
    main()
