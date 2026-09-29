#!/usr/bin/env python3
"""Score research sources for the Source Ledger, per references/ledger.md.

Input (stdin, or a file given with --input): one source per line, tab or pipe separated:
    name | url | tier | date | corroborations [| reuse]
where date is YYYY-MM-DD, YYYY-MM, YYYY, or "live" (a living page, counted as today),
or a JSON list of objects with the keys name, url, tier, date, corroborations, reuse.
Lines that are empty or start with "#" are ignored.

Output: ready-to-paste ledger rows (markdown), then the same rows as JSON.

Score = Tier + Recency + Corroboration + Reuse
  Tier:          authoritative/academic 40, practitioner 20, community 10
  Recency:       25 if <= 90 days old, then linear decay to 0 at --recency-days (default 540)
  Corroboration: 0 -> 0, 1 -> 10, 2+ -> 20
  Reuse:         as given, capped at 15 (default 0)

Example:
    printf 'Example paper | https://example.org/paper | academic | 2026-06-01 | 2\n' \\
        | python3 score.py --today 2026-09-29
"""
import argparse
import datetime as dt
import json
import re
import sys

TIER = {"authoritative": 40, "academic": 40, "practitioner": 20, "community": 10}


def norm(u):
    """Normalize a URL into the ledger match key."""
    u = u.strip().lower()
    u = re.sub(r"^https?://", "", u)
    u = re.sub(r"^www\.", "", u)
    return u.split("?")[0].split("#")[0].rstrip("/")


def age_days(date, today, recency_days):
    d = (date or "").strip().lower()
    if d in ("", "live", "today", "current"):
        return 0
    for fmt in ("%Y-%m-%d", "%Y-%m", "%Y"):
        try:
            return (today - dt.datetime.strptime(d, fmt).date()).days
        except ValueError:
            pass
    m = re.match(r"~?(\d{4})", d)
    # an approximate year counts from mid-year; anything unparseable counts as fully stale
    return (today - dt.date(int(m.group(1)), 6, 30)).days if m else recency_days


def recency(age, recency_days):
    if age <= 90:
        return 25
    return max(0, round(25 * (recency_days - age) / (recency_days - 90)))


def corrob(n):
    n = int(n or 0)
    return 0 if n <= 0 else 10 if n == 1 else 20


def score(row, today, recency_days):
    tier = str(row["tier"]).strip().lower()
    if tier not in TIER:
        raise ValueError(f"unknown tier {row['tier']!r} for {row.get('name')!r}; use one of {sorted(TIER)}")
    t = TIER[tier]
    r = recency(age_days(row.get("date"), today, recency_days), recency_days)
    c = corrob(row.get("corroborations", 0))
    u = min(15, int(row.get("reuse", 0) or 0))
    return {**row, "tier": tier, "url": norm(row["url"]), "tier_pts": t, "recency": r,
            "corrob": c, "reuse": u, "score": t + r + c + u}


def parse(text):
    text = text.strip()
    if text.startswith("["):
        return json.loads(text)
    rows = []
    for line in text.splitlines():
        if not line.strip() or line.strip().startswith("#"):
            continue
        parts = [p.strip() for p in re.split(r"\t|\|", line.strip().strip("|"))]
        if len(parts) < 5:
            raise ValueError(f"expected at least 5 fields, got {len(parts)}: {line!r}")
        name, url, tier, date, cor = parts[:5]
        reuse = parts[5] if len(parts) > 5 and parts[5] else 0
        rows.append({"name": name, "url": url, "tier": tier, "date": date,
                     "corroborations": cor, "reuse": reuse})
    return rows


def main():
    ap = argparse.ArgumentParser(
        description="Score research sources for the Source Ledger (see references/ledger.md).",
        epilog="Input line format: name | url | tier | date | corroborations [| reuse]",
    )
    ap.add_argument("--input", "-i", help="read sources from this file instead of stdin")
    ap.add_argument("--today", help="override today's date (YYYY-MM-DD), for reproducible scoring")
    ap.add_argument("--recency-days", type=int, default=540,
                    help="age in days at which recency reaches 0 (default 540, matches the venue map)")
    ap.add_argument("--note", default="NOTE", help="research note name for the 'Used in' column")
    args = ap.parse_args()

    today = dt.date.fromisoformat(args.today) if args.today else dt.date.today()
    text = open(args.input, encoding="utf-8").read() if args.input else sys.stdin.read()
    rows = [score(r, today, args.recency_days) for r in parse(text)]
    rows.sort(key=lambda r: r["score"], reverse=True)

    print("| # | Source | URL | Tier | Score | Tier | Recency | Corrob. | Reuse | Last verified | Used in |")
    print("|---|--------|-----|------|-------|------|---------|---------|-------|---------------|---------|")
    for i, r in enumerate(rows, 1):
        print(f"| {i} | {r['name']} | {r['url']} | {r['tier']} | **{r['score']}** | {r['tier_pts']} | "
              f"{r['recency']} | {r['corrob']} | {r['reuse']} | {today} | [[{args.note}]] |")
    print()
    print(json.dumps(rows, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
