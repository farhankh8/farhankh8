#!/usr/bin/env python3
"""Hand-authored neofetch-style info card as an animated SVG.

Each line fades and slides in on a short stagger so the panel looks like
it is printing next to the portrait. Set STATIC=1 to emit a frozen frame
for local previews.

Usage:
    python scripts/make_info_card.py

Output: info-card.svg
"""
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT_SVG = ROOT / "info-card.svg"

USER = "farhan@github"
HOST = "~/whoami"

ROWS = [
    ("now",       "Final-year BCA @ Yenepoya College", "#7ee787"),
    ("focus",     "Full-Stack · AI/ML · Cloud Computing", "#79c0ff"),
    ("stack",     "React · Next.js · Node · Mongo · Firebase", "#d2a8ff"),
    ("ai",        "Gemini AI · LLMs · NLP · Generative AI", "#ffa657"),
    ("cloud",     "AWS · Azure · GCP · Docker · Vercel", "#7ee787"),
    ("learning",  "SAP FICO · ERP · Power BI · Tally · Excel", "#79c0ff"),
    ("building",  "SaaS models · Data & Business Analytics", "#d2a8ff"),
    ("open to",   "India · UAE · GCC opportunities", "#ffa657"),
]

SWATCHES = ["#1f6feb", "#a371f7", "#db61a2", "#f0883e",
            "#3fb950", "#39c5cf", "#e3b341", "#f85149"]

BG = "#0d1117"
BAR = "#161b22"
BORDER = "#30363d"
FG = "#e6edf3"
DIM = "#8b949e"

SCALE = 2
FONT = 13 * SCALE
LH = 25 * SCALE
PAD_X = 18 * SCALE
BAR_H = 30 * SCALE


def esc(text: str) -> str:
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def build() -> str:
    static = os.environ.get("STATIC") == "1"

    body_rows = len(ROWS)
    swatch_h = LH * 1.6
    w = 490 * SCALE
    h = BAR_H + PAD_X + body_rows * LH + swatch_h + PAD_X

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
        f'viewBox="0 0 {w} {h}">',
        "<style>text{font-family:'Cascadia Code','JetBrains Mono',Consolas,"
        "'DejaVu Sans Mono',Menlo,monospace}</style>",
    ]
    if not static:
        parts.append(
            "<style>.ln{opacity:0;animation:print .45s ease-out forwards}"
            "@keyframes print{from{opacity:0;transform:translateY(12px)}"
            "to{opacity:1;transform:none}}</style>"
        )

    parts.append(
        f'<rect x="0.5" y="0.5" width="{w - 1}" height="{h - 1}" rx="10" '
        f'fill="{BG}" stroke="{BORDER}"/>'
    )
    parts.append(
        f'<clipPath id="round"><rect x="0.5" y="0.5" width="{w - 1}" '
        f'height="{h - 1}" rx="10"/></clipPath>'
    )
    parts.append('<g clip-path="url(#round)">')
    parts.append(f'<rect width="{w}" height="{BAR_H}" fill="{BAR}"/>')

    dot_r = 6 * SCALE
    dot_y = BAR_H // 2
    for i, color in enumerate(("#ff5f56", "#ffbd2e", "#27c93f")):
        cx = 16 * SCALE + i * (dot_r * 3)
        parts.append(f'<circle cx="{cx}" cy="{dot_y}" r="{dot_r}" fill="{color}"/>')

    title_w = len(USER + HOST) * FONT * 0.58
    parts.append(
        f'<text x="{round((w - title_w) / 2)}" y="{round(dot_y + FONT * 0.36)}" '
        f'font-size="{FONT}" fill="{DIM}">{esc(USER)} {esc(HOST)}</text>'
    )
    parts.append(
        f'<line x1="0" y1="{BAR_H}" x2="{w}" y2="{BAR_H}" stroke="{BORDER}"/>'
    )

    y = BAR_H + PAD_X + FONT
    delay = 0.15
    for key, value, color in ROWS:
        anim = ""
        cls = ""
        if not static:
            cls = ' class="ln"'
            anim = f' style="animation-delay:{delay:.2}s"'
            delay += 0.12
        parts.append(f'<g{cls}{anim}>')
        parts.append(
            f'<text x="{PAD_X}" y="{y}" font-size="{FONT}" font-weight="bold" '
            f'fill="{color}">{esc(key)}</text>'
        )
        kx = PAD_X + round(FONT * 0.62 * max(len(k) for k, _, _ in ROWS)) + 14
        parts.append(
            f'<text x="{kx}" y="{y}" font-size="{FONT}" fill="{FG}">{esc(value)}</text>'
        )
        parts.append("</g>")
        y += LH

    y += round(LH * 0.35)
    size = round(LH * 0.62)
    gap = round(size * 0.55)
    anim = ""
    cls = ""
    if not static:
        cls = ' class="ln"'
        anim = f' style="animation-delay:{delay:.2}s"'
    parts.append(f'<g{cls}{anim}>')
    for i in range(16):
        color = SWATCHES[i % len(SWATCHES)]
        sx = PAD_X + i * (size + gap)
        sy = y if i < 8 else y + size + round(gap * 0.7)
        if i >= 8:
            sx = PAD_X + (i - 8) * (size + gap)
        parts.append(f'<rect x="{sx}" y="{sy}" width="{size}" height="{size}" rx="{size // 5}" fill="{color}"/>')
    parts.append("</g>")

    parts.append("</g></svg>")
    return "\n".join(parts)


def main() -> None:
    OUT_SVG.write_text(build(), encoding="utf-8")
    kb = OUT_SVG.stat().st_size / 1024
    print(f"wrote {OUT_SVG.name} ({kb:.1f} KB)")


if __name__ == "__main__":
    main()
