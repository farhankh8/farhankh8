#!/usr/bin/env python3
"""Infinite dual-direction skills ticker as an SVG.

Two rows of technology pills scroll opposite ways forever - keeps the
profile feeling alive after the one-shot animations settle.

Usage:
    python scripts/make_skills_ticker.py

Output: skills-ticker.svg
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT_SVG = ROOT / "skills-ticker.svg"

ROW1 = ["React.js", "Next.js", "TypeScript", "JavaScript", "Node.js", "Express.js",
        "MongoDB", "PostgreSQL", "Firebase", "Python", "SQL", "Tailwind CSS"]
ROW2 = ["AWS", "Azure", "GCP", "Docker", "Vercel", "Git",
        "Gemini AI", "LLM Integration", "NLP", "Power BI", "SAP FICO", "Advanced Excel"]

COLORS = ["#7ee787", "#79c0ff", "#d2a8ff", "#ffa657", "#39c5cf", "#f778ba"]

W, H = 1720, 168
PAD = 18
FONT = 24
CHAR_W = 13
PILL_H = 46
PILL_PAD = 26
GAP = 16
BORDER = "#30363d"
BG = "#0d1117"


def esc(t: str) -> str:
    return t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def build_row(chips, y, color_offset):
    seq = []
    x = 0.0
    i = 0
    while x < W:
        label = chips[i % len(chips)]
        color = COLORS[(i + color_offset) % len(COLORS)]
        pw = round(len(label) * CHAR_W + PILL_PAD * 2)
        seq.append(
            f'<rect x="{x:.0f}" y="{y}" width="{pw}" height="{PILL_H}" '
            f'rx="{PILL_H // 2}" fill="none" stroke="{color}" stroke-width="2"/>'
            f'<text x="{x + pw / 2:.0f}" y="{y + PILL_H / 2 + FONT * 0.36:.0f}" '
            f'font-size="{FONT}" fill="{color}" text-anchor="middle">{esc(label)}</text>'
        )
        x += pw + GAP
        i += 1
    seq_w = x - GAP
    return "\n".join(seq), seq_w


def wrap_group(seq_xml, seq_w, cls):
    parts = [f'<g class="{cls}">']
    for dx in (0.0, seq_w + GAP):
        parts.append(f'<g transform="translate({dx:.0f},0)">')
        parts.append(seq_xml)
        parts.append("</g>")
    parts.append("</g>")
    return "\n".join(parts)


def main() -> None:
    row1, w1 = build_row(ROW1, PAD, 0)
    row2, w2 = build_row(ROW2, PAD + PILL_H + GAP, 3)

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
<style>
text{{font-family:'Cascadia Code','JetBrains Mono',Consolas,Menlo,monospace}}
.r1{{animation:left {round(w1 / 90)}s linear infinite}}
.r2{{animation:right {round(w2 / 110)}s linear infinite}}
@keyframes left{{from{{transform:translateX(0)}}to{{transform:translateX(-{w1 + GAP:.0f}px)}}}}
@keyframes right{{from{{transform:translateX(-{w2 + GAP:.0f}px)}}to{{transform:translateX(0)}}}}
</style>
<clipPath id="clip"><rect x="0" y="0" width="{W}" height="{H}" rx="14"/></clipPath>
<rect x="0.5" y="0.5" width="{W - 1}" height="{H - 1}" rx="14" fill="{BG}" stroke="{BORDER}"/>
<g clip-path="url(#clip)">
{wrap_group(row1, w1, 'r1')}
{wrap_group(row2, w2, 'r2')}
</g>
</svg>'''

    OUT_SVG.write_text(svg, encoding="utf-8")
    kb = OUT_SVG.stat().st_size / 1024
    print(f"wrote {OUT_SVG.name} ({kb:.1f} KB)")


if __name__ == "__main__":
    main()
