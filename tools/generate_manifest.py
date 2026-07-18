#!/usr/bin/env python3
"""
Generate/refresh the image manifest for the listing.

- Scans images in images/web/ (preferred) or images/ if web/ is empty/missing
- Picks a sensible cover image (hero/cover/side/front if present; else first)
- Updates data/listing.json fields: "cover" and "images" (relative paths)

Usage:
  python3 tools/generate_manifest.py \
    [--images-dir images] [--listing data/listing.json]

Notes:
- No external deps; works on stock Python 3
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from dataclasses import dataclass
from typing import List


SUPPORTED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".avif"}


def is_image_file(filename: str) -> bool:
    _, ext = os.path.splitext(filename.lower())
    return ext in SUPPORTED_EXTENSIONS


def find_image_dir(preferred_dir: str) -> str:
    web_dir = os.path.join(preferred_dir, "web")
    if os.path.isdir(web_dir):
        # Use images/web if it contains images
        contents = [f for f in os.listdir(web_dir) if is_image_file(f)]
        if contents:
            return web_dir
    # Fallback to images/
    return preferred_dir


def list_images(image_dir: str) -> List[str]:
    try:
        entries = sorted(os.listdir(image_dir))
    except FileNotFoundError:
        return []
    return [e for e in entries if is_image_file(e)]


def score_filename_for_cover(name: str) -> int:
    n = name.lower()
    score = 0
    if any(k in n for k in ("hero", "cover")):
        score += 100
    if any(k in n for k in ("front", "side", "profile")):
        score += 50
    if any(k in n for k in ("main", "lead", "first")):
        score += 20
    # Prefer landscape by filename hints (very rough; we don't inspect pixels)
    if "landscape" in n:
        score += 5
    # De-prioritize thumbnails if any
    if any(k in n for k in ("thumb", "small", "min")):
        score -= 10
    return score


def choose_cover(images: List[str]) -> str | None:
    if not images:
        return None
    scored = sorted(images, key=lambda n: (-score_filename_for_cover(n), n))
    return scored[0]


def read_listing(path: str) -> dict:
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}


def write_listing(path: str, listing: dict) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(listing, f, ensure_ascii=False, indent=2)
        f.write("\n")


def rel_paths(images_dir: str, files: List[str]) -> List[str]:
    # Convert absolute images_dir + filename into repo-relative paths
    # Expect images_dir to be like "images" or "images/web"
    rels: List[str] = []
    prefix = images_dir.rstrip("/") + "/"
    for name in files:
        # Join then normalize relative path
        path = os.path.join(images_dir, name)
        rel = os.path.normpath(path)
        rels.append(rel.replace("\\", "/"))
    return rels


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate image manifest for listing.json")
    parser.add_argument("--images-dir", default="images", help="Directory containing images (default: images)")
    parser.add_argument("--listing", default="data/listing.json", help="Path to listing.json (default: data/listing.json)")
    args = parser.parse_args()

    images_dir = find_image_dir(args.images_dir)
    images = list_images(images_dir)

    if not images:
        print(f"No images found in {images_dir}. Nothing to update.", file=sys.stderr)
        return 0

    # Respect an existing cover set in listing.json if it matches a filename
    listing = read_listing(args.listing)
    existing_cover = (listing.get("cover") or "").strip()
    existing_basename = os.path.basename(existing_cover) if existing_cover else ""
    cover_name = existing_basename if existing_basename in images else choose_cover(images)
    # Ensure cover is first in order
    ordered: List[str] = []
    if cover_name:
        ordered.append(cover_name)
    ordered.extend([n for n in images if n != cover_name])

    rels = rel_paths(images_dir, ordered)
    cover_rel = rels[0] if rels else ""

    listing["cover"] = cover_rel
    listing["images"] = rels
    write_listing(args.listing, listing)

    print("Updated listing.json:")
    print(f"  cover:  {cover_rel}")
    print(f"  images: {len(rels)} files")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


