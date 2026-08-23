#!/usr/bin/env python3
"""Fetch the public contribution calendar - no token needed.

GitHub serves the same fragment the profile page uses at
https://github.com/users/<username>/contributions. This script fetches it
with requests, parses the day cells with BeautifulSoup, and writes
data/contributions.json with raw days plus derived stats.

Usage:
    python scripts/fetch_contributions.py
"""
import json
import os
import re
from datetime import date, timedelta
from pathlib import Path

import requests
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "data" / "contributions.json"
USERNAME = os.environ.get("GH_USERNAME", "farhankh8")
URL = f"https://github.com/users/{USERNAME}/contributions"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) profile-art/1.0",
    "Accept": "text/html",
}


def parse_days(html: str):
    soup = BeautifulSoup(html, "html.parser")

    tips = {}
    for tip in soup.find_all("tool-tip"):
        ref = tip.get("for")
        if ref:
            tips[ref] = tip.get_text(" ", strip=True)

    days = []
    for cell in soup.find_all(attrs={"data-date": True}):
        d = cell["data-date"]
        raw = cell.get("data-count")
        if raw is not None:
            count = int(raw)
        else:
            label = tips.get(cell.get("id", ""), "") or cell.get("aria-label", "") or ""
            m = re.search(r"(\d+)\s+contributions?", label)
            count = int(m.group(1)) if m else 0
        level_raw = cell.get("data-level")
        if level_raw is not None:
            level = int(level_raw)
        else:
            level = 0 if count == 0 else min(4, 1 + count // 3)
        days.append({"date": d, "count": count, "level": level})
    return days


def _to_date(s: str) -> date:
    return date.fromisoformat(s)


def longest_streak(active_dates) -> int:
    if not active_dates:
        return 0
    best = run = 1
    for prev, cur in zip(active_dates, active_dates[1:]):
        run = run + 1 if (cur - prev).days == 1 else 1
        best = max(best, run)
    return best


def current_streak(days) -> int:
    by_date = {d["date"]: d["count"] for d in days}
    today = date.today()
    cursor = today if by_date.get(today.isoformat(), 0) > 0 else today - timedelta(days=1)
    streak = 0
    while by_date.get(cursor.isoformat(), 0) > 0:
        streak += 1
        cursor -= timedelta(days=1)
    return streak


def derive_stats(days) -> dict:
    active = sorted(_to_date(d["date"]) for d in days if d["count"] > 0)
    best = max(days, key=lambda d: d["count"], default=None)
    monthly = {}
    for d in days:
        key = d["date"][:7]
        monthly[key] = monthly.get(key, 0) + d["count"]
    return {
        "total": sum(d["count"] for d in days),
        "active_days": len(active),
        "best_day": {"date": best["date"], "count": best["count"]} if best else None,
        "current_streak": current_streak(days),
        "longest_streak": longest_streak(active),
        "monthly": dict(sorted(monthly.items())),
    }


def main() -> None:
    resp = requests.get(URL, headers=HEADERS, timeout=30)
    resp.raise_for_status()
    days = parse_days(resp.text)
    if not days:
        raise SystemExit("no contribution cells found - GitHub markup may have changed")

    seen = {}
    for d in sorted(days, key=lambda x: x["date"]):
        seen[d["date"]] = d
    days = list(seen.values())

    payload = {
        "username": USERNAME,
        "fetched_at": date.today().isoformat(),
        "days": days,
        "stats": derive_stats(days),
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    s = payload["stats"]
    print(
        f"{USERNAME}: {s['total']} contributions across {len(days)} days "
        f"(streak {s['current_streak']}d, longest {s['longest_streak']}d)"
    )
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
