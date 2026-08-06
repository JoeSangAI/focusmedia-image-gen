#!/usr/bin/env python3
"""Compose a frame-exact Focus Media LCD TVC demo with a static lower strip."""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
from dataclasses import dataclass
from decimal import Decimal
from fractions import Fraction
from pathlib import Path

from PIL import Image


SCRIPT_DIR = Path(__file__).resolve().parent
DEFAULT_TEMPLATE = (
    SCRIPT_DIR.parent / "assets" / "framed-demo-standards" / "lcd-32-standard.png"
)
DEFAULT_MAIN_BOX = (418, 74, 1084, 610)
DEFAULT_LOWER_BOX = (418, 802, 1084, 203)


def parse_box(value: str) -> tuple[int, int, int, int]:
    try:
        x, y, width, height = (int(part) for part in value.split(","))
    except (AttributeError, TypeError, ValueError) as exc:
        raise argparse.ArgumentTypeError("box must look like x,y,width,height") from exc
    if min(x, y) < 0 or width <= 0 or height <= 0:
        raise argparse.ArgumentTypeError("box values must be non-negative and non-empty")
    return x, y, width, height


def run(command: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, check=True, text=True, capture_output=True)


def probe_media(path: Path) -> dict[str, object]:
    result = run(
        [
            "ffprobe",
            "-v",
            "error",
            "-show_streams",
            "-show_format",
            "-of",
            "json",
            str(path),
        ]
    )
    return json.loads(result.stdout)


def video_stream(probe: dict[str, object]) -> dict[str, object]:
    for stream in probe.get("streams", []):
        if stream.get("codec_type") == "video":
            return stream
    raise ValueError("source has no video stream")


def audio_stream(probe: dict[str, object]) -> dict[str, object] | None:
    for stream in probe.get("streams", []):
        if stream.get("codec_type") == "audio":
            return stream
    return None


def fps_fraction(stream: dict[str, object]) -> Fraction:
    value = str(stream.get("avg_frame_rate") or stream.get("r_frame_rate") or "0/1")
    fps = Fraction(value)
    if fps <= 0:
        raise ValueError(f"invalid source frame rate: {value}")
    return fps


def frame_count(stream: dict[str, object], probe: dict[str, object]) -> int:
    raw = stream.get("nb_frames")
    if raw not in (None, "N/A"):
        return int(str(raw))
    duration = stream.get("duration") or probe.get("format", {}).get("duration")
    if duration in (None, "N/A"):
        raise ValueError("source frame count and duration are both unavailable")
    return round(Decimal(str(duration)) * Decimal(fps_fraction(stream).numerator) / Decimal(fps_fraction(stream).denominator))


def frame_from_time(value: str, fps: Fraction) -> int:
    frames = Fraction(Decimal(value)) * fps
    if frames.denominator != 1:
        raise ValueError(
            f"switch time {value}s does not land on a whole frame at {fps} fps"
        )
    return frames.numerator


def choose_main_crop(
    width: int,
    height: int,
    source_layout: str = "auto",
) -> tuple[int, int, int, int]:
    ratio = width / height
    if source_layout == "auto":
        if abs(ratio - 4 / 3) <= 0.03:
            source_layout = "4:3"
        elif abs(ratio - 16 / 9) <= 0.03:
            source_layout = "16:9"
        else:
            raise ValueError(
                f"source is {width}x{height}; expected a validated 4:3 or 16:9 variant"
            )
    expected = 4 / 3 if source_layout == "4:3" else 16 / 9
    if abs(ratio - expected) > 0.03:
        raise ValueError(
            f"source layout is declared {source_layout}, but file is {width}x{height}"
        )
    if source_layout == "16:9":
        return 0, 0, width, height

    crop_height = round(width * 9 / 16)
    crop_height -= crop_height % 2
    if crop_height > height:
        raise ValueError("4:3 source is too short for a top-aligned 16:9 crop")
    return 0, 0, width - (width % 2), crop_height


def choose_audio_mode(codec: str | None, requested: str) -> str:
    if codec is None:
        return "none"
    if requested == "copy":
        if codec not in {"aac", "alac", "ac3"}:
            raise ValueError(
                f"audio codec {codec} is not approved for MP4 stream copy; use auto or aac"
            )
        return "copy"
    if requested == "aac":
        return "aac"
    return "copy" if codec in {"aac", "alac", "ac3"} else "aac"


def validate_still(path: Path, ratio: float, label: str, tolerance: float = 0.01) -> None:
    with Image.open(path) as image:
        actual = image.width / image.height
        if abs(actual - ratio) > tolerance:
            raise ValueError(
                f"{label} must already match {ratio:.4f}:1; got {image.width}x{image.height}"
            )


def validate_boxes(
    template: Path,
    main_box: tuple[int, int, int, int],
    lower_box: tuple[int, int, int, int],
) -> tuple[int, int]:
    with Image.open(template) as image:
        size = image.size
    for label, (x, y, width, height) in (
        ("main", main_box),
        ("lower", lower_box),
    ):
        if x + width > size[0] or y + height > size[1]:
            raise ValueError(f"{label} box extends outside the template")
    return size


def scale_crop(width: int, height: int) -> str:
    return (
        f"scale={width}:{height}:force_original_aspect_ratio=increase,"
        f"crop={width}:{height},setsar=1"
    )


@dataclass(frozen=True)
class Composition:
    source_probe: dict[str, object]
    fps: Fraction
    frames: int
    switch_frame: int
    crop: tuple[int, int, int, int]
    audio_codec: str | None
    audio_mode: str
    template_size: tuple[int, int]


def prepare_composition(args: argparse.Namespace) -> Composition:
    if shutil.which("ffmpeg") is None or shutil.which("ffprobe") is None:
        raise RuntimeError("ffmpeg and ffprobe are required")
    validate_still(args.tail, 16 / 9, "tail image")
    validate_still(args.lower, 16 / 3, "lower-strip image")
    template_size = validate_boxes(args.template, args.main_box, args.lower_box)

    source_probe = probe_media(args.source)
    stream = video_stream(source_probe)
    width, height = int(stream["width"]), int(stream["height"])
    fps = fps_fraction(stream)
    frames = frame_count(stream, source_probe)
    switch_frame = (
        args.switch_frame
        if args.switch_frame is not None
        else frame_from_time(args.switch_time, fps)
    )
    if switch_frame < 0 or switch_frame >= frames:
        raise ValueError(f"switch frame must be between 0 and {frames - 1}")
    crop = choose_main_crop(width, height, args.source_layout)

    source_audio = audio_stream(source_probe)
    codec = str(source_audio["codec_name"]) if source_audio else None
    mode = choose_audio_mode(codec, args.audio_mode)
    return Composition(
        source_probe,
        fps,
        frames,
        switch_frame,
        crop,
        codec,
        mode,
        template_size,
    )


def render(args: argparse.Namespace, composition: Composition) -> None:
    fps_text = f"{composition.fps.numerator}/{composition.fps.denominator}"
    crop_x, crop_y, crop_width, crop_height = composition.crop
    main_x, main_y, main_width, main_height = args.main_box
    lower_x, lower_y, lower_width, lower_height = args.lower_box

    filters = ";".join(
        [
            (
                f"[0:v]crop={crop_width}:{crop_height}:{crop_x}:{crop_y},"
                f"{scale_crop(main_width, main_height)},fps={fps_text},"
                "setpts=PTS-STARTPTS[program]"
            ),
            (
                f"[1:v]{scale_crop(main_width, main_height)},"
                "setpts=PTS-STARTPTS[tail]"
            ),
            (
                f"[program][tail]overlay=0:0:enable='gte(n,{composition.switch_frame})':"
                "shortest=1[main]"
            ),
            f"[2:v]{scale_crop(lower_width, lower_height)},setpts=PTS-STARTPTS[lower]",
            "[3:v]setpts=PTS-STARTPTS[frame]",
            (
                f"[frame][main]overlay={main_x}:{main_y}:shortest=1[with_main]"
            ),
            (
                f"[with_main][lower]overlay={lower_x}:{lower_y}:shortest=1,"
                "format=yuv420p[out]"
            ),
        ]
    )

    command = [
        "ffmpeg",
        "-y",
        "-v",
        "error",
        "-i",
        str(args.source),
        "-loop",
        "1",
        "-framerate",
        fps_text,
        "-i",
        str(args.tail),
        "-loop",
        "1",
        "-framerate",
        fps_text,
        "-i",
        str(args.lower),
        "-loop",
        "1",
        "-framerate",
        fps_text,
        "-i",
        str(args.template),
        "-filter_complex",
        filters,
        "-map",
        "[out]",
    ]
    if composition.audio_mode != "none":
        command.extend(["-map", "0:a:0"])
    command.extend(
        [
            "-c:v",
            "libx264",
            "-preset",
            args.preset,
            "-crf",
            str(args.crf),
            "-frames:v",
            str(composition.frames),
        ]
    )
    if composition.audio_mode == "copy":
        command.extend(["-c:a", "copy"])
    elif composition.audio_mode == "aac":
        command.extend(["-c:a", "aac", "-b:a", args.audio_bitrate])
    command.extend(["-movflags", "+faststart", str(args.output)])

    args.output.parent.mkdir(parents=True, exist_ok=True)
    run(command)


def make_contact_sheet(
    video: Path,
    output: Path,
    frames: int,
    switch_frame: int,
) -> list[int]:
    candidates = [
        0,
        frames // 2,
        max(0, switch_frame - 1),
        switch_frame,
        min(frames - 1, switch_frame + 1),
        frames - 1,
    ]
    selected = list(dict.fromkeys(candidates))
    expression = "+".join(f"eq(n\\,{frame})" for frame in selected)
    output.parent.mkdir(parents=True, exist_ok=True)
    run(
        [
            "ffmpeg",
            "-y",
            "-v",
            "error",
            "-i",
            str(video),
            "-vf",
            f"select='{expression}',scale=640:-1,tile=3x2:padding=8:margin=8",
            "-vsync",
            "0",
            "-frames:v",
            "1",
            str(output),
        ]
    )
    return selected


def output_summary(probe: dict[str, object]) -> dict[str, object]:
    video = video_stream(probe)
    audio = audio_stream(probe)
    return {
        "width": int(video["width"]),
        "height": int(video["height"]),
        "fps": str(video.get("avg_frame_rate")),
        "frames": int(video["nb_frames"]) if video.get("nb_frames") not in (None, "N/A") else None,
        "video_codec": video.get("codec_name"),
        "audio_codec": audio.get("codec_name") if audio else None,
        "duration": probe.get("format", {}).get("duration"),
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Build a static-lower, frame-exact 32-inch LCD TVC demo."
    )
    parser.add_argument("--source", required=True, type=Path)
    parser.add_argument("--tail", required=True, type=Path)
    parser.add_argument("--lower", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--template", type=Path, default=DEFAULT_TEMPLATE)
    parser.add_argument("--main-box", type=parse_box, default=DEFAULT_MAIN_BOX)
    parser.add_argument("--lower-box", type=parse_box, default=DEFAULT_LOWER_BOX)
    parser.add_argument("--source-layout", choices=["auto", "4:3", "16:9"], default="auto")
    switch = parser.add_mutually_exclusive_group(required=True)
    switch.add_argument("--switch-frame", type=int)
    switch.add_argument("--switch-time")
    parser.add_argument("--audio-mode", choices=["auto", "copy", "aac"], default="auto")
    parser.add_argument("--audio-bitrate", default="192k")
    parser.add_argument("--preset", default="medium")
    parser.add_argument("--crf", type=int, default=18)
    parser.add_argument("--contact-sheet", type=Path)
    parser.add_argument("--report", type=Path)
    return parser


def main() -> None:
    args = build_parser().parse_args()
    composition = prepare_composition(args)
    render(args, composition)
    sheet_frames: list[int] | None = None
    if args.contact_sheet:
        sheet_frames = make_contact_sheet(
            args.output,
            args.contact_sheet,
            composition.frames,
            composition.switch_frame,
        )

    output_probe = probe_media(args.output)
    report = {
        "source": str(args.source),
        "tail": str(args.tail),
        "lower": str(args.lower),
        "template": str(args.template),
        "output": str(args.output),
        "source_layout": args.source_layout,
        "source_crop": list(composition.crop),
        "source_fps": str(composition.fps),
        "source_frames": composition.frames,
        "switch_frame": composition.switch_frame,
        "switch_time_seconds": float(Fraction(composition.switch_frame, 1) / composition.fps),
        "main_box": list(args.main_box),
        "lower_box": list(args.lower_box),
        "source_audio_codec": composition.audio_codec,
        "audio_mode": composition.audio_mode,
        "audio_preservation": (
            "stream_copy"
            if composition.audio_mode == "copy"
            else "single_controlled_aac_transcode"
            if composition.audio_mode == "aac"
            else "no_source_audio"
        ),
        "contact_sheet": str(args.contact_sheet) if args.contact_sheet else None,
        "contact_sheet_frames": sheet_frames,
        "output_probe": output_summary(output_probe),
    }
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(
            json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8"
        )
    else:
        print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
