#!/usr/bin/env python3
"""Convert a prepped photo into a self-typing monochrome ASCII SVG.

Reads data/source-prepped.png (see prep_photo.py). If missing, falls back
to your GitHub avatar so the pipeline works out of the box.

Each row prints via a horizontal SMIL clip wipe with a riding cursor
block, staggered top-to-bottom. Plays once and freezes.

Usage:
    python scripts/make_ascii_svg.py

Output: avi-ascii.svg -> farhan-ascii.svg at repo root
"""
import os
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageOps

ROOT = Path(__file__).resolve().parent.parent
PREPPED = ROOT / "data" / "source-prepped.png"
AVATAR_URL = "https://avatars.githubusercontent.com/farhankh8"
OUT_SVG = ROOT / "farhan-ascii.svg"

RAMP = " .`:-=+*cs#%@"
FILL = "#c9d1d9"
BG = "#0d1117"
BORDER = "#30363d"

FONT_SIZE = float(os.environ.get("ASCII_FONT", "10"))
COLS = int(os.environ.get("ASCII_COLS", "100"))
CW = FONT_SIZE * 0.6
LH = FONT_SIZE * 1.16
PAD = 14

STEP = 0.055
DUR = 0.3


def get_source() -> Image.Image:
    if PREPPED.exists():
        print(f"using {PREPPED}")
        return Image.open(PREPPED)
    print("no source-prepped.png found - falling back to GitHub avatar")
    print("for a better portrait run: python scripts/prep_photo.py your-photo.jpg")
    import requests

    resp = requests.get(AVATAR_URL, timeout=30)
    resp.raise_for_status()
    img = Image.open(__import__("io").BytesIO(resp.content)).convert("L")
    img = ImageOps.autocontrast(img, cutoff=1)
    PREPPED.parent.mkdir(parents=True, exist_ok=True)
    img.save(PREPPED)
    return img


def to_grid(img: Image.Image):
    aspect = img.width / img.height
    rows = max(20, min(80, round(COLS * CW / (aspect * LH))))
    small = img.resize((COLS, rows), Image.LANCZOS)
    vals = np.asarray(small, dtype=np.float32)

    lo, hi = np.percentile(vals, 2), np.percentile(vals, 98)
    if hi - lo < 1:
        hi = lo + 1
    norm = np.clip((vals - lo) / (hi - lo), 0.0, 1.0)
    darkness = (1.0 - norm) ** 1.15

    glyphs = []
    n = len(RAMP)
    for r in range(rows):
        line = []
        for c in range(COLS):
            d = float(darkness[r, c])
            idx = int(d * (n - 1))
            line.append(RAMP[idx] if idx > 0 else " ")
        glyphs.append("".join(line))
    top_blank = sum(1 for line in glyphs if not line.strip())
    while glyphs and not glyphs[0].strip():
        glyphs.pop(0)
    while glyphs and not glyphs[-1].strip():
        glyphs.pop()
    print(f"grid {COLS}x{len(glyphs)} ({top_blank} blank rows trimmed)")
    return glyphs


def esc(text: str) -> str:
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def build_svg(grid) -> str:
    rows = len(grid)
    inner_w = COLS * CW
    inner_h = rows * LH
    w = round(inner_w + PAD * 2)
    h = round(inner_h + PAD * 2)

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
        f'viewBox="0 0 {w} {h}">',
        "<style>text{font-family:'Cascadia Code','JetBrains Mono',Consolas,"
        "'DejaVu Sans Mono',Menlo,monospace;white-space:pre}</style>",
        f'<rect x="0.5" y="0.5" width="{w - 1}" height="{h - 1}" rx="10" '
        f'fill="{BG}" stroke="{BORDER}"/>',
        f'<g fill="{FILL}" font-size="{FONT_SIZE:g}">',
    ]

    for i, line in enumerate(grid):
        rid = f"r{i}"
        y_top = round(PAD + i * LH)
        baseline = round(y_top + FONT_SIZE)
        begin = round(i * STEP, 3)
        dur = DUR

        parts.append(
            f'<clipPath id="{rid}"><rect x="{PAD}" y="{y_top}" height="{round(LH)}" width="0">'
            f'<animate attributeName="width" to="{round(inner_w)}" dur="{dur}s" '
            f'begin="{begin}s" fill="freeze"/></rect></clipPath>'
        )
        parts.append(f'<g clip-path="url(#{rid})">')
        parts.append(
            f'<text x="{PAD}" y="{baseline}" xml:space="preserve" '
            f'textLength="{round(inner_w)}" lengthAdjust="spacing">{esc(line)}</text>'
        )
        parts.append("</g>")

        cx_to = round(PAD + inner_w - CW)
        parts.append(
            f'<rect x="{PAD}" y="{y_top + 1}" width="{round(CW)}" '
            f'height="{round(FONT_SIZE)}" fill="#58a6ff">'
            f'<animate attributeName="x" to="{cx_to}" dur="{dur}s" begin="{begin}s" fill="freeze"/>'
            f'<animate attributeName="opacity" values="0;1;1;0" '
            f'keyTimes="0;0.02;0.86;1" dur="{dur}s" begin="{begin}s" fill="freeze"/>'
            "</rect>"
        )

    total = round((rows - 1) * STEP + DUR + 0.4, 2)
    parts.append(
        f'<rect x="{PAD}" y="{round(PAD + rows * LH) - 2}" width="{round(CW)}" '
        f'height="{round(FONT_SIZE)}" fill="{FILL}" opacity="0">'
        f'<set attributeName="opacity" to="1" begin="{total}s" fill="freeze"/>'
        '<animate attributeName="opacity" values="1;0;1" dur="1.2s" '
        f'begin="{total + 0.6}s" repeatCount="indefinite"/>'
        "</rect>"
    )

    parts.append("</g></svg>")
    return "\n".join(parts)


def main() -> None:
    grid = to_grid(get_source())
    svg = build_svg(grid)
    OUT_SVG.write_text(svg, encoding="utf-8")
    kb = OUT_SVG.stat().st_size / 1024
    print(f"wrote {OUT_SVG.name} ({kb:.1f} KB)")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        sys.exit(f"error: {exc}")
