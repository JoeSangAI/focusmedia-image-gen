#!/usr/bin/env python3
"""Download selected Focus Media remote references into a local checksum cache."""

from __future__ import annotations

import argparse
import hashlib
import sys
import urllib.request
from pathlib import Path

from select_media_references import build_parser, load_manifest, select_references


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def download(item: dict, output_dir: Path, force: bool = False) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    target = output_dir / Path(item["path"]).name
    if target.exists() and not force:
        if item.get("sha256") and sha256(target) != item["sha256"]:
            raise RuntimeError(f"cached file failed checksum: {target}")
        return target

    request = urllib.request.Request(item["url"], headers={"User-Agent": "focusmedia-image-gen/2.0"})
    with urllib.request.urlopen(request, timeout=30) as response:
        data = response.read()
    target.write_bytes(data)

    if item.get("sha256") and sha256(target) != item["sha256"]:
        target.unlink(missing_ok=True)
        raise RuntimeError(f"downloaded file failed checksum: {target}")
    return target


def build_fetch_parser() -> argparse.ArgumentParser:
    selection = build_parser()
    parser = argparse.ArgumentParser(parents=[selection], add_help=False)
    parser.add_argument("--id", action="append", default=[], help="Reference id; repeatable")
    parser.add_argument("--output", type=Path, default=Path(".focusmedia-cache/references"))
    parser.add_argument("--force", action="store_true")
    return parser


def main() -> None:
    args = build_fetch_parser().parse_args()
    manifest = load_manifest(args.manifest)
    if args.id:
        wanted = set(args.id)
        selected = [item for item in manifest.get("references", []) if item.get("id") in wanted]
        missing = wanted - {str(item["id"]) for item in selected}
        if missing:
            raise SystemExit(f"Unknown reference ids: {', '.join(sorted(missing))}")
    else:
        selected = select_references(manifest, args)
    if not selected:
        print("No matching references found.", file=sys.stderr)
        raise SystemExit(1)

    for item in selected:
        path = download(item, args.output.expanduser(), args.force)
        print(f"{item['id']} -> {path}")


if __name__ == "__main__":
    main()
