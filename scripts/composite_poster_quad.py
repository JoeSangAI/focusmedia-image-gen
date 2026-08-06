#!/usr/bin/env python3
"""Composite a poster into a four-corner media surface."""

from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter


def parse_quad(value: str) -> list[tuple[float, float]]:
    parts = value.replace(";", " ").split()
    points = []
    for part in parts:
        x_str, y_str = part.split(",", 1)
        points.append((float(x_str), float(y_str)))
    if len(points) != 4:
        raise argparse.ArgumentTypeError("quad must contain four x,y points")
    return points


def perspective_coefficients(src: list[tuple[float, float]], dst: list[tuple[float, float]]) -> list[float]:
    # Solve coefficients mapping output points back to input points.
    import numpy as np

    matrix = []
    vector = []
    for (x, y), (u, v) in zip(dst, src):
        matrix.append([x, y, 1, 0, 0, 0, -u * x, -u * y])
        matrix.append([0, 0, 0, x, y, 1, -v * x, -v * y])
        vector.extend([u, v])
    return np.linalg.solve(np.array(matrix), np.array(vector)).tolist()


def fit_poster(poster: Image.Image, width: int, height: int, mode: str, background: str) -> Image.Image:
    poster = poster.convert("RGB")
    src_ratio = poster.width / poster.height
    dst_ratio = width / height

    if mode == "cover":
        if src_ratio > dst_ratio:
            new_h = height
            new_w = round(height * src_ratio)
        else:
            new_w = width
            new_h = round(width / src_ratio)
        resized = poster.resize((new_w, new_h), Image.Resampling.LANCZOS)
        left = (new_w - width) // 2
        top = (new_h - height) // 2
        return resized.crop((left, top, left + width, top + height))

    resized = poster.copy()
    resized.thumbnail((width, height), Image.Resampling.LANCZOS)
    canvas = Image.new("RGB", (width, height), background)
    x = (width - resized.width) // 2
    y = (height - resized.height) // 2
    canvas.paste(resized, (x, y))
    return canvas


def add_glass_effect(surface: Image.Image, strength: float) -> Image.Image:
    if strength <= 0:
        return surface
    overlay = Image.new("RGBA", surface.size, (255, 255, 255, 0))
    draw = ImageDraw.Draw(overlay)
    w, h = surface.size
    alpha = int(75 * strength)
    draw.polygon([(0, 0), (w * 0.36, 0), (0, h * 0.58)], fill=(255, 255, 255, alpha))
    draw.polygon([(w * 0.55, 0), (w * 0.73, 0), (0, h)], fill=(255, 255, 255, int(alpha * 0.55)))
    draw.rectangle((0, 0, w, h), outline=(255, 255, 255, int(alpha * 0.35)), width=max(1, round(w * 0.006)))
    return Image.alpha_composite(surface.convert("RGBA"), overlay).convert("RGB")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--poster", required=True, type=Path)
    parser.add_argument("--background", required=True, type=Path)
    parser.add_argument("--quad", required=True, type=parse_quad, help="top-left top-right bottom-right bottom-left, e.g. '100,80 500,90 520,700 90,690'")
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--fit", choices=["cover", "contain"], default="cover")
    parser.add_argument("--surface-width", type=int, default=1200)
    parser.add_argument("--surface-height", type=int, default=1800)
    parser.add_argument("--background-fill", default="white")
    parser.add_argument("--glass", type=float, default=0.0, help="0 to 1")
    parser.add_argument("--shadow", type=float, default=0.0, help="0 to 1")
    args = parser.parse_args()

    background = Image.open(args.background).convert("RGB")
    poster = Image.open(args.poster)
    surface = fit_poster(poster, args.surface_width, args.surface_height, args.fit, args.background_fill)
    surface = add_glass_effect(surface, max(0.0, min(args.glass, 1.0))).convert("RGBA")

    src = [(0, 0), (surface.width, 0), (surface.width, surface.height), (0, surface.height)]
    coeffs = perspective_coefficients(src, args.quad)
    warped = surface.transform(background.size, Image.Transform.PERSPECTIVE, coeffs, Image.Resampling.BICUBIC)

    mask = Image.new("L", surface.size, 255)
    warped_mask = mask.transform(background.size, Image.Transform.PERSPECTIVE, coeffs, Image.Resampling.BICUBIC)

    if args.shadow > 0:
        shadow = Image.new("RGBA", background.size, (0, 0, 0, 0))
        shadow_mask = warped_mask.filter(ImageFilter.GaussianBlur(radius=8))
        shadow_alpha = shadow_mask.point(lambda p: int(p * max(0.0, min(args.shadow, 1.0)) * 0.45))
        shadow.putalpha(shadow_alpha)
        background = Image.alpha_composite(background.convert("RGBA"), shadow).convert("RGB")

    composed = Image.composite(warped.convert("RGB"), background, warped_mask)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    composed.save(args.output, quality=94)


if __name__ == "__main__":
    main()
