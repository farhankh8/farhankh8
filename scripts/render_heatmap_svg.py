#!/usr/bin/env python3
"""Render data/contributions.json as an animated 53-week heatmap SVG.

Classic GitHub calendar of rounded boxes in a green ramp, revealed
diagonally line-after-line with CSS keyframes that play once and freeze.
Includes month/weekday labels, a Less->More legend, and a stats footer.

Usage:
    python scripts/render_heatmap_svg.py

Output: contrib-heatmap.svg
"""
import json
import math
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "contributions.json"
OUT = ROOT / "contrib-heatmap.svg"

PALETTE = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353", "#69f0a0"]
LIGHT_NONE = "#ebedf0"
FG = "#8b949e"
FG_LIGHT = "#57606a"

CELL, GAP, PITCH = 11.0, 3.0, 14.0
LEFT, TOP, PAD_R = 34.0, 22.0, 14.0
FOOTER = 58.0
RX = 2.5

MONTHS = ["", "Jan", "Feb", "Mar", "Apr", "May", "Jun",
          "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]


def esc(t: str) -> str:
    return t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def build_weeks(days):
    weeks, week = [], []
    first_wd = date.fromisoformat(days[0]["date"]).weekday()
    week.extend([None] * first_wd)
    for d in days:
        week.append(d)
        if len(week) == 7:
            weeks.append(week)
            week = []
    if week:
        week.extend([None] * (7 - len(week)))
        weeks.append(week)
    return weeks


def boost_level(day, p90: float) -> int:
    level = min(4, day["level"])
    if level == 4 and day["count"] >= max(p90, 1):
        return 5
    return level


def build() -> str:
    payload = json.loads(DATA.read_text(encoding="utf-8"))
    days = sorted(payload["days"], key=lambda d: d["date"])
    stats = payload["stats"]
    weeks = build_weeks(days)

    nonzero = [d["count"] for d in days if d["count"] > 0]
    p90 = float(np_percentile(nonzero, 90)) if nonzero else 1.0

    grid_w = len(weeks) * PITCH
    w = LEFT + grid_w + PAD_R
    h = TOP + 7 * PITCH + FOOTER

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w:.0f}" height="{h:.0f}" '
        f'viewBox="0 0 {w:.0f} {h:.0f}" role="img" aria-label="Contribution heatmap">',
        "<style>",
        "text{font-family:'Cascadia Code','JetBrains Mono',Consolas,Menlo,monospace}",
        ".lbl{fill:#8b949e;font-size:9px}.stat{fill:#e6edf3;font-size:12px;font-weight:bold}",
        ".wk{opacity:0;animation:drop .38s ease-out forwards}"
        "@keyframes drop{from{opacity:0;transform:translateY(-8px)}"
        "to{opacity:1;transform:none}}",
        ".end{opacity:0;animation:fade .5s ease-out forwards}"
        "@keyframes fade{to{opacity:1}}",
        ".l0{fill:#161b22}.l1{fill:#0e4429}.l2{fill:#006d32}"
        ".l3{fill:#26a641}.l4{fill:#39d353}.l5{fill:#69f0a0}",
        "@media (prefers-color-scheme:light){"
        ".l0{fill:#ebedf0}.lbl{fill:#57606a}.stat{fill:#24292f}}",
        "</style>",
    ]

    last_month = None
    last_label_col = -10
    for ci, week in enumerate(weeks):
        x = LEFT + ci * PITCH
        first_day = next((d for d in week if d), None)
        if first_day:
            m = int(first_day["date"][5:7])
            if m != last_month and ci - last_label_col >= 3:
                parts.append(
                    f'<text class="lbl" x="{x:.1f}" y="12">{MONTHS[m]}</text>'
                )
                last_month = m
                last_label_col = ci
        delay = round(ci * 0.016, 3)
        parts.append(f'<g class="wk" style="animation-delay:{delay}s">')
        for ri, dcell in enumerate(week):
            if not dcell:
                continue
            y = TOP + ri * PITCH
            lvl = boost_level(dcell, p90)
            count = dcell["count"]
            tip = esc(
                f'{count} contribution{"s" if count != 1 else ""} on {dcell["date"]}'
            )
            parts.append(
                f'<rect class="l{lvl}" x="{x:.1f}" y="{y:.1f}" width="{CELL}" '
                f'height="{CELL}" rx="{RX}"><title>{tip}</title></rect>'
            )
        parts.append("</g>")

    for label, ri in (("Mon", 1), ("Wed", 3), ("Fri", 5)):
        y = TOP + ri * PITCH + CELL - 2
        parts.append(f'<text class="lbl" x="0" y="{y:.1f}">{label}</text>')

    foot_y = TOP + 7 * PITCH + 30
    parts.append(
        f'<text class="end stat" style="animation-delay:{round(len(weeks) * 0.016 + 0.15, 2)}s" '
        f'x="{LEFT:.0f}" y="{foot_y:.0f}">'
        f'{stats["total"]:,} contributions in the last year</text>'
    )

    legend_delay = round(len(weeks) * 0.016 + 0.25, 2)
    lx = w - PAD_R - (PITCH * 5 + 46)
    parts.append(f'<g class="end" style="animation-delay:{legend_delay}s">')
    parts.append(f'<text class="lbl" x="{lx:.1f}" y="{foot_y:.0f}">Less</text>')
    for i in range(5):
        cx = lx + 26 + i * PITCH
        parts.append(
            f'<rect x="{cx:.1f}" y="{foot_y - 9:.1f}" width="{CELL}" height="{CELL}" '
            f'rx="{RX}" fill="{PALETTE[i]}"/>'
        )
    parts.append(f'<text class="lbl" x="{lx + 26 + 5 * PITCH + 3:.1f}" y="{foot_y:.0f}">More</text>')
    parts.append("</g>")

    streak_x = lx - 160
    if streak_x > 300:
        streak = f'streak {stats["current_streak"]}d · best {stats["longest_streak"]}d'
        parts.append(
            f'<text class="lbl end" style="animation-delay:{legend_delay}s" '
            f'x="{streak_x:.0f}" y="{foot_y:.0f}">{esc(streak)}</text>'
        )

    parts.append("</svg>")
    return "\n".join(parts)


def np_percentile(values, pct):
    vals = sorted(values)
    if not vals:
        return 0.0
    k = (len(vals) - 1) * pct / 100.0
    lo = math.floor(k)
    hi = math.ceil(k)
    if lo == hi:
        return vals[lo]
    return vals[lo] + (vals[hi] - vals[lo]) * (k - lo)


def main() -> None:
    if not DATA.exists():
        raise SystemExit("run scripts/fetch_contributions.py first")
    OUT.write_text(build(), encoding="utf-8")
    kb = OUT.stat().st_size / 1024
    print(f"wrote {OUT.name} ({kb:.1f} KB)")


if __name__ == "__main__":
    main()
