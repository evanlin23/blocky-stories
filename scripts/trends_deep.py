"""Deep pass on the week's trend scan: what the 40 fastest Shorts say about themselves, and what their viewers say.

    python scripts/trends_deep.py [date]   # reads docs/trends/<date>.json (default: the newest scan)
                                           # writes docs/trends/deep/<date>.json and .md (needs the YouTube secrets)

For each of the scan's 40 fastest Shorts (by views per day) it saves the description and tags, the channel's
subscriber count and creation date, the publish hour (UTC), the like/view and comment/view ratios, and the top 20
comments (order=relevance, text only: no usernames, @handles masked). It runs right after scripts/trends.py in the
metrics workflow (continue-on-error), and costs about 45 of the 10,000 free daily API units (the scan before it about 2,230). Every call is counted
against a cap, so a bug can never spend the day's quota (the daily upload needs about 1,600).

Public repo: descriptions and comments are other people's words, so both are cut short (DESC_CHARS, COMMENT_CHARS)
and only a few appear in the .md. Read them for themes; quote nothing long anywhere.
"""

from __future__ import annotations

import collections
import datetime as dt
import json
import re
import statistics
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TRENDS = ROOT / "docs" / "trends"
OUT = TRENDS / "deep"
TOP = 40
COMMENTS = 20
DESC_CHARS = 400
COMMENT_CHARS = 240
CAP = 300   # units this script may spend; it needs ~45

# YouTube Data API v3 quota costs (https://developers.google.com/youtube/v3/determine_quota_cost)
COST = {"search.list": 100, "videos.list": 1, "channels.list": 1, "commentThreads.list": 1}

STOP = set("""a an and are as at be but by for from has have he her his i if in is it its just me my no not of on or
so that the their them they this to was we were what when who why will with you your yall im its dont thats like
u ur lol bro he's she's it's i'm don't that's you're can cant can't did do get got one all out up how would there
she him then than been only more very really even about also our because still into over too oh yes yeah""".split())


class Budget:
    """Counts API units and refuses any call that would go past the cap."""

    def __init__(self, cap: int = CAP):
        self.cap, self.used, self.calls = cap, 0, collections.Counter()

    def spend(self, method: str) -> bool:
        c = COST[method]
        if self.used + c > self.cap:
            return False
        self.used += c
        self.calls[method] += 1
        return True


def scan_cost(n_videos: int, n_queries: int) -> int:
    """What scripts/trends.py spent: one search per query, one videos.list per 50 ids."""
    return n_queries * COST["search.list"] + -(-n_videos // 50) * COST["videos.list"]


def clean(text: str, limit: int) -> str:
    """One line, @handles masked, links shortened, cut to `limit` characters."""
    t = re.sub(r"@[\w.\-]+", "@user", text or "")
    t = re.sub(r"https?://\S+", "<link>", t)
    t = re.sub(r"\s+", " ", t).strip()
    return t if len(t) <= limit else t[: limit - 1].rstrip() + "…"


def ratio(a, b) -> float | None:
    try:
        return round(int(a) / int(b), 5) if int(b) else None
    except (TypeError, ValueError):
        return None


def latest(day: str | None) -> Path:
    files = sorted(TRENDS.glob("????-??-??.json"))
    if day:
        return TRENDS / f"{day}.json"
    if not files:
        raise SystemExit("no trend scan yet: run scripts/trends.py first")
    return files[-1]


def fastest(rows: list[dict], n: int = TOP) -> list[dict]:
    return sorted(rows, key=lambda r: -r["per_day"])[:n]


def comments(yt, vid: str, budget: Budget) -> tuple[list[str], str | None]:
    if not budget.spend("commentThreads.list"):
        return [], "skipped: unit cap"
    try:
        r = yt.commentThreads().list(part="snippet", videoId=vid, order="relevance", maxResults=COMMENTS,
                                     textFormat="plainText").execute()
    except Exception as e:  # comments off, video gone, ...: keep going
        return [], f"unavailable: {type(e).__name__}"
    out = []
    for it in r.get("items", []):
        top = it.get("snippet", {}).get("topLevelComment", {}).get("snippet", {})
        txt = clean(top.get("textOriginal") or top.get("textDisplay") or "", COMMENT_CHARS)
        if txt:
            out.append(txt)
    return out, None


def deep(yt, rows: list[dict], now: dt.datetime, budget: Budget) -> list[dict]:
    pick = fastest(rows)
    ids = [r["id"] for r in pick]
    vids: dict[str, dict] = {}
    for i in range(0, len(ids), 50):
        if budget.spend("videos.list"):
            for v in yt.videos().list(part="snippet,statistics,contentDetails", id=",".join(ids[i:i + 50])
                                      ).execute().get("items", []):
                vids[v["id"]] = v
    chan_ids = sorted({v["snippet"]["channelId"] for v in vids.values()})
    chans: dict[str, dict] = {}
    for i in range(0, len(chan_ids), 50):
        if budget.spend("channels.list"):
            for c in yt.channels().list(part="snippet,statistics", id=",".join(chan_ids[i:i + 50])
                                        ).execute().get("items", []):
                chans[c["id"]] = c
    out = []
    for rank, r in enumerate(pick, 1):
        v = vids.get(r["id"])
        if not v:
            continue
        sn, st = v["snippet"], v.get("statistics", {})
        ch = chans.get(sn["channelId"], {})
        cst = ch.get("statistics", {})
        pub = dt.datetime.fromisoformat(sn["publishedAt"].replace("Z", "+00:00"))
        cpub = ch.get("snippet", {}).get("publishedAt")
        cdate = dt.datetime.fromisoformat(cpub.replace("Z", "+00:00")) if cpub else None
        views = int(st.get("viewCount", r["views"]))
        text, note = comments(yt, r["id"], budget)
        desc = sn.get("description", "")
        out.append({
            "rank": rank, "id": r["id"], "title": sn["title"], "channel": sn["channelTitle"],
            "seconds": r["seconds"], "views": views, "per_day": round(r["per_day"]), "queries": r["queries"],
            "published": sn["publishedAt"], "hour_utc": pub.hour, "weekday": pub.strftime("%a"),
            "description": clean(desc, DESC_CHARS),
            "description_first_line": clean(desc.strip().splitlines()[0] if desc.strip() else "", 160),
            "tags": sn.get("tags", []),
            "likes": int(st["likeCount"]) if "likeCount" in st else None,
            "comments": int(st["commentCount"]) if "commentCount" in st else None,
            "like_per_view": ratio(st.get("likeCount"), views),
            "comment_per_view": ratio(st.get("commentCount"), views),
            "channel_subscribers": None if cst.get("hiddenSubscriberCount") else
            (int(cst["subscriberCount"]) if "subscriberCount" in cst else None),
            "channel_videos": int(cst["videoCount"]) if "videoCount" in cst else None,
            "channel_created": cpub,
            "channel_age_days": round((now - cdate).total_seconds() / 86400) if cdate else None,
            "top_comments": text, "comments_note": note,
        })
    return out


def words(texts: list[str], n: int = 25) -> list[tuple[str, int]]:
    c = collections.Counter()
    for t in texts:
        c.update({w for w in re.findall(r"[a-z']{3,}", t.lower()) if w not in STOP})   # once per comment
    return c.most_common(n)


def med(xs):
    xs = [x for x in xs if x is not None]
    return statistics.median(xs) if xs else None


def pct(x):
    return "n/a" if x is None else f"{x:.2%}"


def report(items: list[dict], day: str, units: dict) -> str:
    L = [f"# Deep trend data {day}", "",
         f"The {len(items)} fastest Shorts from `docs/trends/{day}.md`, looked up one by one by "
         "`scripts/trends_deep.py`. Descriptions and comments are cut short and @handles masked; the full (still "
         f"trimmed) text is in `{day}.json`. Read for themes, quote nothing long.", "",
         f"API units today: scan ≈{units['scan']}, deep {units['deep']}, total ≈{units['scan'] + units['deep']} "
         f"of 10,000 ({units['calls']}).", "",
         "## Medians", "",
         f"- Length {med([x['seconds'] for x in items])} s · like/view {pct(med([x['like_per_view'] for x in items]))}"
         f" · comment/view {pct(med([x['comment_per_view'] for x in items]))}",
         f"- Channel subscribers {med([x['channel_subscribers'] for x in items]) or 0:,.0f} · channel age "
         f"{med([x['channel_age_days'] for x in items]) or 0:,.0f} days · tags per video "
         f"{med([len(x['tags']) for x in items])}", ""]
    hours = collections.Counter(x["hour_utc"] for x in items)
    L += ["## Publish hour (UTC; Central is UTC-6 in winter)", "",
          " · ".join(f"{h:02d}h: {n}" for h, n in sorted(hours.items())), ""]
    L += ["## What commenters say most (words, counted once per comment)", "",
          ", ".join(f"{w} {n}" for w, n in words([c for x in items for c in x["top_comments"]])), ""]
    L += ["## The 40", "", "| # | Views/day | Len | Hour | Subs | Ch. age (d) | Like/view | Cmt/view | Tags | Title |",
          "|---|---|---|---|---|---|---|---|---|---|"]
    for x in items:
        subs = "hidden" if x["channel_subscribers"] is None else f"{x['channel_subscribers']:,}"
        title = x["title"].replace("|", "/")
        L.append(f"| {x['rank']} | {x['per_day']:,} | {x['seconds']} s | {x['hour_utc']:02d} | {subs} | "
                 f"{x['channel_age_days'] if x['channel_age_days'] is not None else '?'} | "
                 f"{pct(x['like_per_view'])} | {pct(x['comment_per_view'])} | {len(x['tags'])} | "
                 f"[{title}](https://youtube.com/shorts/{x['id']}) |")
    L += ["", "## Each one: description opening and three top comments", ""]
    for x in items:
        L.append(f"**{x['rank']}. {x['title']}** ({x['channel']})")
        if x["description_first_line"]:
            L.append(f"- Description opens: {clean(x['description_first_line'], 100)}")
        if x["tags"]:
            L.append(f"- Tags: {', '.join(x['tags'][:8])}")
        for c in x["top_comments"][:3]:
            L.append(f"- Comment: {clean(c, 100)}")
        if x["comments_note"]:
            L.append(f"- Comments {x['comments_note']}")
        L.append("")
    return "\n".join(L)


def main(argv: list[str]) -> None:
    sys.path.insert(0, str(Path(__file__).parent))
    from trends import QUERIES, QUERIES_WIDE, youtube

    src = latest(argv[1] if len(argv) > 1 else None)
    scan = json.loads(src.read_text())
    day = src.stem
    budget = Budget()
    items = deep(youtube(), scan["rows"], dt.datetime.now(dt.timezone.utc), budget)
    wide = scan.get("rows_wide", [])
    units = {"scan": scan_cost(len(scan["rows"]) + len(wide), len(QUERIES) + len(QUERIES_WIDE))
             + -(-len({r.get("channel_id") for r in wide}) // 50), "deep": budget.used,
             "calls": ", ".join(f"{k} ×{v}" for k, v in sorted(budget.calls.items()))}
    OUT.mkdir(parents=True, exist_ok=True)
    md = report(items, day, units)
    (OUT / f"{day}.md").write_text(md)
    (OUT / f"{day}.json").write_text(json.dumps({"day": day, "units": units, "videos": items}, indent=1,
                                                ensure_ascii=False) + "\n")
    print(md)


if __name__ == "__main__":
    sys.exit(main(sys.argv))
