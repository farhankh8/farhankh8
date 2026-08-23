#!/usr/bin/env python3
"""Animated certifications panel - prints like `cat certifications.log`.

Each certification row appears on a short stagger with a check mark.
Set STATIC=1 for a frozen frame.

Usage:
    python scripts/make_certifications_svg.py

Output: certifications.svg
"""
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT_SVG = ROOT / "certifications.svg"

USER = "farhan@github"
HOST = "~/certifications"

CERTS = [
    ("AWS Solutions Architecture", "Amazon Web Services", "Dec 2025", "#ff9900"),
    ("Generative AI Engineering", "IBM", "Dec 2025", "#0f62fe"),
    ("AI & ML Engineering", "Microsoft", "Dec 2025", "#00a4ef"),
    ("Data Analytics Professional", "Google", "Oct 2025", "#34a853"),
    ("IT Automation with Python", "Google", "Oct 2025", "#ea4335"),
    ("PM · Front-End · Tech Consulting", "Google · IBM · Deloitte", "2024-25", "#7ee787"),
]

BG = "#0d1117"
BAR = "#161b22"
BORDER = "#30363d"
FG = "#e6edf3"
DIM = "#8b949e"
CHECK = "#7ee787"

SCALE = 2
FONT = 13 * SCALE
LH = 24 * SCALE
PAD_X = 18 * SCALE
BAR_H = 30 * SCALE


def esc(t: str) -> str:
    return t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def build() -> str:
    static = os.environ.get("STATIC") == "1"
    w = 640 * SCALE
    h = BAR_H + PAD_X + len(CERTS) * LH + PAD_X + FONT * 2

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
    parts.append('<g clip-path="url(#round)">')
    parts.append(
        f'<clipPath id="round"><rect x="0.5" y="0.5" width="{w - 1}" '
        f'height="{h - 1}" rx="10"/></clipPath>'
    )
    parts.append(f'<rect width="{w}" height="{BAR_H}" fill="{BAR}"/>')

    dot_r = 6 * SCALE
    dot_y = BAR_H // 2
    for i, color in enumerate(("#ff5f56", "#ffbd2e", "#27c93f")):
        cx = 16 * SCALE + i * dot_r * 3
        parts.append(f'<circle cx="{cx}" cy="{dot_y}" r="{dot_r}" fill="{color}"/>')

    title_w = (len(USER) + len(HOST)) * FONT * 0.58
    parts.append(
        f'<text x="{round((w - title_w) / 2)}" y="{round(dot_y + FONT * 0.36)}" '
        f'font-size="{FONT}" fill="{DIM}">{esc(USER)} {esc(HOST)}</text>'
    )
    parts.append(f'<line x1="0" y1="{BAR_H}" x2="{w}" y2="{BAR_H}" stroke="{BORDER}"/>')

    prompt_y = BAR_H + PAD_X
    parts.append(
        f'<text class="ln" x="{PAD_X}" y="{prompt_y}" font-size="{FONT}" '
        f'fill="{DIM}">$ cat certificates/*.crt</text>'
    )

    delay = 0.25
    y = prompt_y + FONT * 1.8
    date_x = w - PAD_X - round(FONT * 0.58 * 9)
    for title, issuer, date, color in CERTS:
        anim = ""
        cls = ""
        if not static:
            cls = ' class="ln"'
            anim = f' style="animation-delay:{delay:.2}s"'
            delay += 0.14

        parts.append(f'<g{cls}{anim}>')
        parts.append(
            f'<text x="{PAD_X}" y="{y}" font-size="{FONT}" font-weight="bold" '
            f'fill="{CHECK}">[✓]</text>'
        )
        tx = PAD_X + round(FONT * 1.55)
        parts.append(
            f'<text x="{tx}" y="{y}" font-size="{FONT}" font-weight="bold" '
            f'fill="{FG}">{esc(title)}</text>'
        )
        iy = y + FONT * 1.15
        parts.append(
            f'<text x="{tx}" y="{iy}" font-size="{round(FONT * 0.78)}" '
            f'fill="{color}">■ {esc(issuer)}</text>'
        )
        parts.append(
            f'<text x="{date_x}" y="{iy}" font-size="{round(FONT * 0.78)}" '
            f'fill="{DIM}">{esc(date)}</text>'
        )
        parts.append("</g>")
        y += LH

    if not static:
        total = delay + 0.3
        parts.append(
            f'<text class="ln" style="animation-delay:{total:.2}s" '
            f'x="{PAD_X}" y="{y + FONT * 0.4}" font-size="{FONT}" '
            f'fill="{DIM}">6 verified ✔</text>'
        )

    parts.append("</g></svg>")
    return "\n".join(parts)


def main() -> None:
    OUT_SVG.write_text(build(), encoding="utf-8")
    kb = OUT_SVG.stat().st_size / 1024
    print(f"wrote {OUT_SVG.name} ({kb:.1f} KB)")


if __name__ == "__main__":
    main()
