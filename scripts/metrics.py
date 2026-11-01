"""Weekly numbers for every blocky story on the channel: `python scripts/metrics.py`.

Reads the channel's uploads (YouTube Data API), matches them to stories by title, pulls each one's totals,
retention curve and traffic sources (YouTube Analytics API), and writes:
- metrics/videos.json   everything, for anyone who wants to dig
- metrics/summary.md    one page that /week reads before the writer starts

Needs the YT_* secrets, with a refresh token granted `yt-analytics.readonly` as well as `youtube.readonly`.
YouTube's analytics run about 2 to 3 days behind. "Viewed vs swiped away" isn't in the API (Studio only).
"""

from __future__ import annotations

import datetime as dt
import json
import os
import re
import sys
from pathlib import Path

from stories import ROOT, all_stories, uploads

OUT = ROOT / "metrics"
SINCE = "2026-10-30"   # the first blocky story; older videos on the channel are another kind of content
TOTALS = ["views", "engagedViews", "estimatedMinutesWatched", "averageViewDuration", "averageViewPercentage",
          "likes", "comments", "shares", "subscribersGained"]


def clients():
    from google.oauth2.credentials import Credentials
    from googleapiclient.discovery import build

    creds = Credentials(None, refresh_token=os.environ["YT_REFRESH_TOKEN"], client_id=os.environ["YT_CLIENT_ID"],
                        client_secret=os.environ["YT_CLIENT_SECRET"], token_uri="https://oauth2.googleapis.com/token")
    return (build("youtube", "v3", credentials=creds, cache_discovery=False),
            build("youtubeAnalytics", "v2", credentials=creds, cache_discovery=False))


def norm(t: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", t.lower()).strip()


def story_titles() -> dict[str, str]:
    """normalised title -> story, from package.json, uploads.json and story.json."""
    out = {}
    up = uploads()
    for s in all_stories():
        d = ROOT / "stories" / s
        for t in [up.get(s, {}).get("title", "")] + [json.loads(f.read_text()).get("title", "")
                                                       for f in (d / "package.json", d / "story.json") if f.exists()]:
            if t:
                out[norm(t)] = s
    return out


def channel_videos(yt) -> list[dict]:
    ch = yt.channels().list(part="contentDetails,snippet", mine=True).execute()["items"][0]
    want = os.environ.get("YT_CHANNEL_ID", "").strip()
    if want and ch["id"] != want:
        sys.exit(f"the token belongs to {ch['id']}, not {want}")
    pl = ch["contentDetails"]["relatedPlaylists"]["uploads"]
    vids, tok = [], None
    while True:
        r = yt.playlistItems().list(part="contentDetails,snippet", playlistId=pl, maxResults=50, pageToken=tok).execute()
        for it in r["items"]:
            published = it["contentDetails"].get("videoPublishedAt") or it["snippet"]["publishedAt"]
            vids.append({"id": it["contentDetails"]["videoId"], "title": it["snippet"]["title"],
                         "published": published[:10]})
        tok = r.get("nextPageToken")
        if not tok or vids[-1]["published"] < SINCE:
            break
    vids = [v for v in vids if v["published"] >= SINCE]
    if vids:   # privacy and length
        info = yt.videos().list(part="contentDetails,status", id=",".join(v["id"] for v in vids)).execute()["items"]
        by = {i["id"]: i for i in info}
        for v in vids:
            i = by.get(v["id"], {})
            v["privacy"] = i.get("status", {}).get("privacyStatus")
            m = re.match(r"PT(?:(\d+)M)?(?:(\d+)S)?", i.get("contentDetails", {}).get("duration", ""))
            v["length_s"] = int(m.group(1) or 0) * 60 + int(m.group(2) or 0) if m else None
    return vids


def query(ya, **kw) -> list[dict]:
    r = ya.reports().query(ids="channel==MINE", **kw).execute()
    cols = [h["name"] for h in r.get("columnHeaders", [])]
    return [dict(zip(cols, row)) for row in r.get("rows", [])]


def totals(ya, v: dict, end: str) -> dict:
    metrics = list(TOTALS)
    while metrics:
        try:
            rows = query(ya, startDate=v["published"], endDate=end, metrics=",".join(metrics), filters=f"video=={v['id']}")
            return rows[0] if rows else {}
        except Exception as e:   # a metric this channel or API version doesn't serve: drop it and retry
            bad = next((m for m in metrics if m in str(e)), None)
            if bad is None:
                print(f"{v['id']}: totals failed: {e}", file=sys.stderr)
                return {}
            metrics.remove(bad)
    return {}


def retention(ya, v: dict, end: str) -> dict:
    try:
        rows = query(ya, startDate=v["published"], endDate=end, dimensions="elapsedVideoTimeRatio",
                     metrics="audienceWatchRatio,relativeRetentionPerformance", filters=f"video=={v['id']}")
    except Exception as e:
        print(f"{v['id']}: retention failed: {e}", file=sys.stderr)
        return {}
    if not rows:
        return {}
    pts = [(float(r["elapsedVideoTimeRatio"]), float(r["audienceWatchRatio"]), float(r.get("relativeRetentionPerformance", 0)))
           for r in rows]
    L = v.get("length_s") or 0

    def at(x):
        return min(pts, key=lambda p: abs(p[0] - x))[1]

    drops = sorted(((pts[i - 1][1] - pts[i][1], pts[i][0]) for i in range(2, len(pts))), reverse=True)[:3]
    return {"curve": pts, "at": {f"{int(x * 100)}%": round(at(x), 3) for x in (0.05, 0.25, 0.5, 0.75, 0.95)},
            "biggest_drops": [{"at_s": round(r * L, 1), "at_ratio": round(r, 2), "drop": round(d, 3)} for d, r in drops],
            "relative_mid": round(min(pts, key=lambda p: abs(p[0] - 0.5))[2], 2)}


def traffic(ya, v: dict, end: str) -> dict:
    try:
        rows = query(ya, startDate=v["published"], endDate=end, dimensions="insightTrafficSourceType", metrics="views",
                     filters=f"video=={v['id']}")
    except Exception as e:
        print(f"{v['id']}: traffic failed: {e}", file=sys.stderr)
        return {}
    total = sum(float(r["views"]) for r in rows) or 1
    return {r["insightTrafficSourceType"]: round(float(r["views"]) / total, 3) for r in rows}


def fmt(x, pct=False):
    if x in (None, ""):
        return "?"
    x = float(x)
    return f"{x:.0f}%" if pct else f"{x:,.0f}"


def status(r: dict) -> str:
    """Views, or why there are none: not public yet, or public but Analytics hasn't caught up (2 to 3 days)."""
    if r.get("privacy") != "public":
        return f"not public ({r.get('privacy') or 'unknown'})"
    views = (r.get("totals") or {}).get("views")
    return f"{float(views):,.0f} views" if views not in (None, "") else "no data yet (Analytics runs 2 to 3 days behind)"


def summary(rows: list[dict], end: str) -> str:
    out = [f"# Channel numbers (through {end})", "",
           "YouTube's analytics run 2 to 3 days behind. Viewed vs swiped away is Studio-only: paste it here by hand if you have it.", "",
           "| Story | Published | Length | Views | Engaged | Avg viewed | Likes | Comments | Shares | Subs | Shorts feed |",
           "|---|---|---|---|---|---|---|---|---|---|---|"]
    for r in rows:
        t, tr = r.get("totals", {}), r.get("traffic", {})
        if not t:   # nothing back yet: say why instead of a row of question marks
            out.append(f"| {r['story'] or r['title'][:40]} | {r['published']} | {r.get('length_s') or '?'} s | "
                       f"{status(r)} |||||||| ")
            continue
        out.append(f"| {r['story'] or r['title'][:40]} | {r['published']} | {r.get('length_s') or '?'} s | {fmt(t.get('views'))} | "
                   f"{fmt(t.get('engagedViews'))} | {fmt(t.get('averageViewPercentage'), True)} | {fmt(t.get('likes'))} | "
                   f"{fmt(t.get('comments'))} | {fmt(t.get('shares'))} | {fmt(t.get('subscribersGained'))} | "
                   f"{fmt(100 * tr.get('SHORTS', 0), True) if tr else '?'} |")
    out += ["", "## Retention", ""]
    for r in rows:
        ret = r.get("retention") or {}
        if not ret:
            continue
        at = ", ".join(f"{k} {v:.0%}" for k, v in ret["at"].items())
        drops = "; ".join(f"{d['at_s']} s (-{d['drop']:.0%})" for d in ret["biggest_drops"])
        out.append(f"- **{r['story'] or r['title'][:40]}**: still watching at {at}. Biggest drops at {drops}. "
                   f"Mid-video vs similar Shorts: {ret['relative_mid']} (0.5 is average).")
    return "\n".join(out) + "\n"


def main() -> None:
    yt, ya = clients()
    end = dt.date.today().isoformat()
    titles = story_titles()
    rows = []
    for v in channel_videos(yt):
        r = {**v, "story": titles.get(norm(v["title"]))}
        if v.get("privacy") == "public":
            r["totals"], r["retention"], r["traffic"] = totals(ya, v, end), retention(ya, v, end), traffic(ya, v, end)
        rows.append(r)
        print(f"{v['published']} {v['id']} {r['story'] or '-'}: {status(r)}")
    OUT.mkdir(exist_ok=True)
    (OUT / "videos.json").write_text(json.dumps({"through": end, "videos": rows}, indent=1) + "\n")
    (OUT / "summary.md").write_text(summary(rows, end))
    print((OUT / "summary.md").read_text())


if __name__ == "__main__":
    main()
