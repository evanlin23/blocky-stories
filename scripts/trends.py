"""Weekly trend scan: which blocky / Roblox-style Shorts are rising right now, by views per day.

    python scripts/trends.py            # writes docs/trends/<date>.md and .json (needs the YouTube secrets)

YouTube search finds Shorts published in the last 14 days for each format query. Each one is ranked by views per
day since it was posted, so the list shows what's rising now, not what was big months ago. Each query's momentum
(the median views/day of its top 10) is compared with last week's scan, so a format that's cooling shows up
before our own numbers do. A second query set (QUERIES_WIDE) scans animated story Shorts outside the blocky niche,
for the port study (docs/research/port-study.md): it's kept apart so the blocky momentum stays comparable week to week,
and its channels are looked up so we can see how many new channels break in. It costs about 2,230 of the 10,000
free daily API units (22 searches at 100), and no Claude usage. The Monday /week run reads the newest file
(RULES.md → "Trends").
"""

from __future__ import annotations

import datetime as dt
import json
import os
import re
import statistics
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs" / "trends"
WINDOW_DAYS = 14

# one query per format we might make in the blocky style (the scope research's format map, plus our own lane)
QUERIES = {
    "rule premise": "in this town roblox story",
    "roblox story": "roblox story animation",
    "horror / creepy": "roblox horror story animation",
    "eerie lore": "roblox lore story animation",
    "sad / emotional": "roblox sad story animation",
    "comedy": "roblox funny story animation",
    "POV": "roblox pov animation",
    "riddle / puzzle": "roblox riddle",
    "series / part 2": "roblox story part 2",
    "blocky (no brand)": "blocky animation story",
}

# outside the niche: animated story Shorts of every kind, to find formats worth porting to the blocky style
QUERIES_WIDE = {
    "2D story animation": "2d animation story",
    "what if animation": "what if animation",
    "POV skit": "pov skit animation",
    "horror story animation": "horror story animation",
    "storytime animation": "storytime animation",
    "mystery / explainer": "mystery explained animation",
    "satisfying / sim": "satisfying simulation",
    "analog horror / fake doc": "analog horror",
    "would you rather": "would you rather",
    "riddle animation": "riddle animation",
    "life hacks": "life hacks animation",
    "if X had sound": "if they had sound animation",
}
NEW_CHANNEL_DAYS = 365


def seconds(iso: str) -> int:
    """ISO 8601 duration (PT1M5S) to seconds."""
    m = re.fullmatch(r"P(?:\d+D)?T?(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?", iso or "")
    if not m:
        return 0
    h, mi, s = (int(x) if x else 0 for x in m.groups())
    return h * 3600 + mi * 60 + s


def rate(views: int, published: str, now: dt.datetime) -> float:
    age = (now - dt.datetime.fromisoformat(published.replace("Z", "+00:00"))).total_seconds() / 86400
    return views / max(age, 0.5)


def momentum(rows: list[dict], queries: dict = QUERIES) -> dict[str, float]:
    """The median views/day of each query's 10 fastest Shorts."""
    out = {}
    for q in queries:
        r = sorted((x["per_day"] for x in rows if q in x["queries"]), reverse=True)[:10]
        out[q] = round(statistics.median(r)) if r else 0
    return out


def previous(before: str) -> dict | None:
    files = sorted(p for p in OUT.glob("*.json") if p.stem < before)
    return json.loads(files[-1].read_text()) if files else None


def report(rows: list[dict], mom: dict, prev: dict | None, day: str) -> str:
    lines = [f"# Trend scan {day}", "",
             f"Blocky / Roblox-style Shorts published in the last {WINDOW_DAYS} days, from YouTube search, ranked by "
             "views per day. Written by `scripts/trends.py` (metrics workflow). Read it as signals, not rules.", "",
             "## Format momentum (median views/day of each query's top 10)", "",
             "| Format | Views/day | vs last scan |", "|---|---|---|"]
    pm = (prev or {}).get("momentum", {})
    for q, v in sorted(mom.items(), key=lambda kv: -kv[1]):
        was = pm.get(q)
        delta = f"{(v - was) / was:+.0%}" if was else "new"
        lines.append(f"| {q} | {v:,} | {delta} |")
    chans: dict[str, list] = {}
    for x in rows:
        chans.setdefault(x["channel"], []).append(x["per_day"])
    lines += ["", "## Channels with the most rising Shorts", "", "| Channel | Shorts | Best views/day |", "|---|---|---|"]
    for c, v in sorted(chans.items(), key=lambda kv: (-len(kv[1]), -max(kv[1])))[:12]:
        lines.append(f"| {c} | {len(v)} | {round(max(v)):,} |")
    lines += ["", "## Fastest 40", "", "| Views/day | Views | Age (d) | Length | Channel | Title | Formats |",
              "|---|---|---|---|---|---|---|"]
    for x in sorted(rows, key=lambda x: -x["per_day"])[:40]:
        title = x["title"].replace("|", "/")
        lines.append(f"| {round(x['per_day']):,} | {x['views']:,} | {x['age']:.0f} | {x['seconds']} s | {x['channel']} | "
                     f"[{title}](https://youtube.com/shorts/{x['id']}) | {', '.join(x['queries'])} |")
    return "\n".join(lines) + "\n"


def youtube():
    from google.oauth2.credentials import Credentials
    from googleapiclient.discovery import build

    creds = Credentials(None, refresh_token=os.environ["YT_REFRESH_TOKEN"], client_id=os.environ["YT_CLIENT_ID"],
                        client_secret=os.environ["YT_CLIENT_SECRET"], token_uri="https://oauth2.googleapis.com/token")
    return build("youtube", "v3", credentials=creds, cache_discovery=False)


def scan(yt, now: dt.datetime, queries: dict = QUERIES) -> list[dict]:
    after = (now - dt.timedelta(days=WINDOW_DAYS)).strftime("%Y-%m-%dT%H:%M:%SZ")
    found: dict[str, set] = {}
    for name, q in queries.items():
        r = yt.search().list(part="id", q=q, type="video", videoDuration="short", order="viewCount",
                             publishedAfter=after, maxResults=25, relevanceLanguage="en").execute()
        for it in r.get("items", []):
            found.setdefault(it["id"]["videoId"], set()).add(name)
    rows, ids = [], list(found)
    for i in range(0, len(ids), 50):
        r = yt.videos().list(part="snippet,statistics,contentDetails,status", id=",".join(ids[i:i + 50])).execute()
        for v in r.get("items", []):
            secs = seconds(v["contentDetails"]["duration"])
            if not secs or secs > 180:   # Shorts only
                continue
            views = int(v["statistics"].get("viewCount", 0))
            pub = v["snippet"]["publishedAt"]
            rows.append({"id": v["id"], "title": v["snippet"]["title"], "channel": v["snippet"]["channelTitle"],
                         "views": views, "seconds": secs, "published": pub,
                         "age": (now - dt.datetime.fromisoformat(pub.replace("Z", "+00:00"))).total_seconds() / 86400,
                         "per_day": rate(views, pub, now), "queries": sorted(found[v["id"]]),
                         "channel_id": v["snippet"].get("channelId"),
                         "made_for_kids": v.get("status", {}).get("madeForKids")})
    return rows


def channels(yt, rows: list[dict], now: dt.datetime) -> None:
    """Adds each row's channel age (days) and subscriber count, one channels.list per 50 channels."""
    ids = sorted({r["channel_id"] for r in rows if r.get("channel_id")})
    info = {}
    for i in range(0, len(ids), 50):
        for c in yt.channels().list(part="snippet,statistics", id=",".join(ids[i:i + 50])).execute().get("items", []):
            st, made = c.get("statistics", {}), c["snippet"].get("publishedAt")
            info[c["id"]] = {
                "channel_age_days": round((now - dt.datetime.fromisoformat(made.replace("Z", "+00:00"))).total_seconds()
                                          / 86400) if made else None,
                "channel_subscribers": None if st.get("hiddenSubscriberCount") else
                (int(st["subscriberCount"]) if "subscriberCount" in st else None)}
    for r in rows:
        r.update(info.get(r.get("channel_id"), {"channel_age_days": None, "channel_subscribers": None}))


def wide_summary(rows: list[dict], queries: dict = QUERIES_WIDE) -> list[dict]:
    """Per format: how big a typical new Short gets, how many new channels break in, how kid-facing it is."""
    out = []
    for q in queries:
        g = [r for r in rows if q in r["queries"]]
        pd = sorted((r["per_day"] for r in g), reverse=True)
        new = [r for r in g if r.get("channel_age_days") is not None and r["channel_age_days"] < NEW_CHANNEL_DAYS]
        kids = [r for r in g if r.get("made_for_kids") is not None]
        out.append({
            "format": q, "shorts": len(g), "channels": len({r["channel"] for r in g}),
            "median_per_day": round(statistics.median(pd)) if pd else 0,
            "top10_median": round(statistics.median(pd[:10])) if pd else 0,
            "median_seconds": statistics.median([r["seconds"] for r in g]) if g else 0,
            "new_channels": len({r["channel"] for r in new}),
            "new_channels_100k_day": len({r["channel"] for r in new if r["per_day"] >= 100_000}),
            "made_for_kids": f"{sum(1 for r in kids if r['made_for_kids'])}/{len(kids)}",
        })
    return sorted(out, key=lambda x: -x["median_per_day"])


def report_wide(rows: list[dict], mom: dict, prev: dict | None) -> str:
    pm = (prev or {}).get("momentum_wide", {})
    lines = ["", "## Outside the niche: animated story Shorts of every kind (port study)", "",
             f"A separate query set, so the blocky momentum above stays comparable. \"New\" channels are under "
             f"{NEW_CHANNEL_DAYS} days old. Made for kids is the uploader's own setting.", "",
             "| Format | Shorts | Channels | Median views/day | Top-10 median | vs last scan | Length | New channels "
             "| New at 100K+/day | Made for kids |", "|---|---|---|---|---|---|---|---|---|---|"]
    for x in wide_summary(rows):
        was = pm.get(x["format"])
        delta = f"{(mom.get(x['format'], 0) - was) / was:+.0%}" if was else "new"
        lines.append(f"| {x['format']} | {x['shorts']} | {x['channels']} | {x['median_per_day']:,} | "
                     f"{x['top10_median']:,} | {delta} | {x['median_seconds']} s | {x['new_channels']} | "
                     f"{x['new_channels_100k_day']} | {x['made_for_kids']} |")
    lines += ["", "### Fastest 25 outside the niche", "",
              "| Views/day | Age (d) | Length | Channel (age d) | Title | Formats |", "|---|---|---|---|---|---|"]
    for x in sorted(rows, key=lambda x: -x["per_day"])[:25]:
        title = x["title"].replace("|", "/")
        lines.append(f"| {round(x['per_day']):,} | {x['age']:.0f} | {x['seconds']} s | {x['channel']} "
                     f"({x.get('channel_age_days', '?')}) | [{title}](https://youtube.com/shorts/{x['id']}) | "
                     f"{', '.join(x['queries'])} |")
    return "\n".join(lines) + "\n"


def main() -> None:
    now = dt.datetime.now(dt.timezone.utc)
    day = now.date().isoformat()
    yt = youtube()
    rows = scan(yt, now)
    mom = momentum(rows)
    prev = previous(day)
    md = report(rows, mom, prev, day)
    wide, mom_wide = [], {}
    try:   # the wide scan never costs us the blocky one
        wide = scan(yt, now, QUERIES_WIDE)
        channels(yt, wide, now)
        mom_wide = momentum(wide, QUERIES_WIDE)
        md += report_wide(wide, mom_wide, prev)
    except Exception as e:  # noqa: BLE001
        md += f"\n## Outside the niche\n\nThe wide scan failed: {type(e).__name__}: {e}\n"
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / f"{day}.md").write_text(md)
    (OUT / f"{day}.json").write_text(json.dumps({"momentum": mom, "rows": rows, "momentum_wide": mom_wide,
                                                 "rows_wide": wide}, indent=1) + "\n")
    print(md)


if __name__ == "__main__":
    sys.exit(main())
