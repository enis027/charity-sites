#!/usr/bin/env python3
"""Render every page of a built site at mobile, tablet and desktop widths.

Usage:
  python3 screenshots.py dist/ [--out screens] [--widths 390,768,1440] [--height 4000]

Uses an installed Chrome, Chromium or Edge in headless mode (no downloads).
Note: desktop Chrome cannot shrink its window below ~500 px in some versions,
so also check the mobile layout in a real device emulator.
"""
from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

CANDIDATES = [
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "/Applications/Chromium.app/Contents/MacOS/Chromium",
    "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
    "google-chrome", "google-chrome-stable", "chromium", "chromium-browser", "microsoft-edge", "msedge",
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
]


def find_browser() -> str | None:
    for c in CANDIDATES:
        p = shutil.which(c) or (c if Path(c).exists() else None)
        if p:
            return p
    return None


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("dist", type=Path)
    ap.add_argument("--out", type=Path, default=Path("screens"))
    ap.add_argument("--widths", default="390,768,1440")
    ap.add_argument("--height", type=int, default=4000)
    a = ap.parse_args()
    browser = find_browser()
    if not browser:
        sys.exit("No Chrome/Chromium/Edge found. Install one, or review pages in a browser manually.")
    a.out.mkdir(parents=True, exist_ok=True)
    pages = sorted(a.dist.glob("*.html"))
    for page in pages:
        for w in (int(x) for x in a.widths.split(",")):
            target = a.out / f"{page.stem}-{w}.png"
            subprocess.run([browser, "--headless=new", "--disable-gpu", "--hide-scrollbars", "--virtual-time-budget=5000",
                            f"--window-size={w},{a.height}", f"--screenshot={target.resolve()}", page.resolve().as_uri()],
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=120)
            print(target)


if __name__ == "__main__":
    main()
