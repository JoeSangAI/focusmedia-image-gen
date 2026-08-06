#!/usr/bin/env python3
"""Normalize a supplied media creative without non-uniform stretching."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from PIL import Image, ImageFilter


def parse_size(value: str) -> tuple[int, int]:
    try:
        width_str, height_str = value.lower().split("x", 1)
        width, height = int(width_str), int(height_str)
    except (ValueError, TypeError) as exc:
        raise argparse.ArgumentTypeError("size must look like 1920x360") from exc
    if width <= 0 or height <= 0:
        raise argparse.ArgumentTypeError("size values must be positive")
    return width, height


def parse_crop(value: str) -> tuple[int, int, int, int]:
    try:
        left, top, right, bottom = (int(part) for part in value.split(","))
    except (ValueError, TypeError) as exc:
        raise argparse.ArgumentTypeError("crop must look like left,top,right,bottom") from exc
    if right <= left or bottom <= top:
        raise argparse.ArgumentTypeError("crop must have positive width and height")
    return left, top, right, bottom


def center_crop_to_ratio(image: Image.Image, ratio: float) -> Image.Image:
    current = image.width / image.height
    if current > ratio:
        width = round(image.height * ratio)
        left = (image.width - width) // 2
        return image.crop((left, 0, left + width, image.height))
    height = round(image.width / ratio)
    top = (image.height - height) // 2
    return image.crop((0, top, image.width, top + height))


def contain_blur(image: Image.Image, size: tuple[int, int]) -> Image.Image:
    width, height = size
    background_scale = max(width / image.width, height / image.height)
    background = image.resize(
        (
            round(image.width * background_scale),
            round(image.height * background_scale),
        ),
        Image.Resampling.LANCZOS,
    )
    background = center_crop_to_ratio(background, width / height)
    background = background.resize(size, Image.Resampling.LANCZOS)
    background = background.filter(ImageFilter.GaussianBlur(radius=max(8, min(size) // 18)))

    foreground_scale = min(width / image.width, height / image.height)
    foreground = image.resize(
        (
            round(image.width * foreground_scale),
            round(image.height * foreground_scale),
        ),
        Image.Resampling.LANCZOS,
    )
    x = (width - foreground.width) // 2
    y = (height - foreground.height) // 2
    background.paste(foreground, (x, y))
    return background


def normalize(
    image: Image.Image,
    size: tuple[int, int],
    mode: str,
) -> Image.Image:
    image = image.convert("RGB")
    ratio = size[0] / size[1]
    if mode in {"safe-band", "cover"}:
        return center_crop_to_ratio(image, ratio).resize(size, Image.Resampling.LANCZOS)
    if mode == "contain-blur":
        return contain_blur(image, size)
    raise ValueError(f"unsupported mode: {mode}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--size", required=True, type=parse_size)
    parser.add_argument(
        "--mode",
        choices=["safe-band", "contain-blur", "cover"],
        required=True,
        help=(
            "safe-band: crop a deliberately protected center band; "
            "contain-blur: preserve every source pixel; "
            "cover: crop edges only when they are known to be expendable"
        ),
    )
    parser.add_argument("--crop", type=parse_crop)
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()

    source = Image.open(args.input).convert("RGB")
    working = source.crop(args.crop) if args.crop else source
    result = normalize(working, args.size, args.mode)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    result.save(args.output, quality=96)

    if args.report:
        report = {
            "input": str(args.input),
            "input_size": list(source.size),
            "crop": list(args.crop) if args.crop else None,
            "working_size": list(working.size),
            "mode": args.mode,
            "output": str(args.output),
            "output_size": list(result.size),
            "target_ratio": args.size[0] / args.size[1],
            "non_uniform_stretch": False,
            "source_pixels_preserved": args.mode == "contain-blur",
        }
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(
            json.dumps(report, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )


if __name__ == "__main__":
    main()
