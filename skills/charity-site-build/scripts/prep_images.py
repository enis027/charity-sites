#!/usr/bin/env python3
"""Resize photos for the web without ever enlarging them.

Usage:
  python3 prep_images.py input.jpg output.jpg --max-width 1600 [--quality 80]
  python3 prep_images.py audit/images/ site/assets/photos/ --max-width 1200

Uses whatever is installed, in this order: Pillow, ImageMagick (magick/convert),
macOS sips. If none is available it copies the file unchanged and says so.
Upscaling is a separate, deliberate step (see photography.md) and is never done here.
"""
from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

EXT = {".jpg", ".jpeg", ".png", ".webp"}


def resize(src: Path, dst: Path, max_w: int, quality: int) -> str:
    dst.parent.mkdir(parents=True, exist_ok=True)
    try:
        from PIL import Image  # type: ignore
        with Image.open(src) as im:
            if im.width > max_w:
                im = im.resize((max_w, round(im.height * max_w / im.width)), Image.LANCZOS)
            if dst.suffix.lower() in (".jpg", ".jpeg") and im.mode in ("RGBA", "P"):
                im = im.convert("RGB")
            im.save(dst, quality=quality, optimize=True)
        return "pillow"
    except ImportError:
        pass
    magick = shutil.which("magick") or shutil.which("convert")
    if magick:
        subprocess.run([magick, str(src), "-resize", f"{max_w}x>", "-strip", "-quality", str(quality), str(dst)], check=True)
        return "imagemagick"
    if shutil.which("sips"):
        shutil.copy(src, dst)
        out = subprocess.run(["sips", "-g", "pixelWidth", str(dst)], capture_output=True, text=True).stdout
        width = int(out.split()[-1]) if out.split() else 0
        if width > max_w:
            subprocess.run(["sips", "--resampleWidth", str(max_w), "-s", "formatOptions", str(quality), str(dst)], check=True, capture_output=True)
        return "sips"
    shutil.copy(src, dst)
    return "copied (no resizer installed)"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("src", type=Path)
    ap.add_argument("dst", type=Path)
    ap.add_argument("--max-width", type=int, default=1600)
    ap.add_argument("--quality", type=int, default=80)
    a = ap.parse_args()
    if a.src.is_dir():
        files = [p for p in sorted(a.src.iterdir()) if p.suffix.lower() in EXT]
        for f in files:
            how = resize(f, a.dst / f.name, a.max_width, a.quality)
            print(f"{f.name}: {how}")
    elif a.src.exists():
        print(resize(a.src, a.dst, a.max_width, a.quality))
    else:
        sys.exit(f"not found: {a.src}")


if __name__ == "__main__":
    main()
