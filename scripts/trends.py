"""Weekly trend scan: which blocky / Roblox-style Shorts are rising right now, by views per day.

    python scripts/trends.py            # writes docs/trends/<date>.md and .json (needs the YouTube secrets)

YouTube search finds Shorts published in the last 14 days for each format query. Each one is ranked by views per
day since it was posted, so the list shows what's rising now, not what was big months ago. Each query's momentum
(the median views/day of its top 10) is compared with last week's scan, so a format that's cooling shows up
before our own numbers do. It costs about 1,000 of the 10,000 free daily API units, and no Claude usage. The
Monday /week run reads the newest file (RULES.md → "Trends").
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


def momentum(rows: list[dict]) -> dict[str, float]:
    """The median views/day of each query's 10 fastest Shorts."""
    out = {}
    for q in QUERIES:
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


def scan(yt, now: dt.datetime) -> list[dict]:
    after = (now - dt.timedelta(days=WINDOW_DAYS)).strftime("%Y-%m-%dT%H:%M:%SZ")
    found: dict[str, set] = {}
    for name, q in QUERIES.items():
        r = yt.search().list(part="id", q=q, type="video", videoDuration="short", order="viewCount",
                             publishedAfter=after, maxResults=25, relevanceLanguage="en").execute()
        for it in r.get("items", []):
            found.setdefault(it["id"]["videoId"], set()).add(name)
    rows, ids = [], list(found)
    for i in range(0, len(ids), 50):
        r = yt.videos().list(part="snippet,statistics,contentDetails", id=",".join(ids[i:i + 50])).execute()
        for v in r.get("items", []):
            secs = seconds(v["contentDetails"]["duration"])
            if not secs or secs > 180:   # Shorts only
                continue
            views = int(v["statistics"].get("viewCount", 0))
            pub = v["snippet"]["publishedAt"]
            rows.append({"id": v["id"], "title": v["snippet"]["title"], "channel": v["snippet"]["channelTitle"],
                         "views": views, "seconds": secs, "published": pub,
                         "age": (now - dt.datetime.fromisoformat(pub.replace("Z", "+00:00"))).total_seconds() / 86400,
                         "per_day": rate(views, pub, now), "queries": sorted(found[v["id"]])})
    return rows


def main() -> None:
    now = dt.datetime.now(dt.timezone.utc)
    day = now.date().isoformat()
    rows = scan(youtube(), now)
    mom = momentum(rows)
    OUT.mkdir(parents=True, exist_ok=True)
    md = report(rows, mom, previous(day), day)
    (OUT / f"{day}.md").write_text(md)
    (OUT / f"{day}.json").write_text(json.dumps({"momentum": mom, "rows": rows}, indent=1) + "\n")
    print(md)


if __name__ == "__main__":
    sys.exit(main())
