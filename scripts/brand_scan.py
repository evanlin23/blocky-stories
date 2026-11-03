"""Branding scan: how the fast-growing story channels present themselves, and whether our candidate names are taken.

    python scripts/brand_scan.py "Name One" "Name Two" ...   # needs the YouTube secrets (brand.yml)

Channels studied: every channel behind the newest deep scan's 40 fastest blocky Shorts, plus the wide scan's channels
under 365 days old with a Short at 100K+/day. For each it saves the title, handle, description (trimmed), country,
creation date, subscribers, whether it has a banner, and its playlists (count and titles). For each candidate name
it runs one channel search and saves the closest matches with their subscriber counts.

Writes docs/research/brand-scan/<date>.json and .md. Avatars and banners are other people's images: they go to
out/brand-scan/ as one numbered contact sheet for the run artifact, and are never committed.

Units: channels.list 1 per 50, playlists.list 1 per channel (~50), search.list 100 per candidate. Capped at CAP.
"""

from __future__ import annotations

import datetime as dt
import io
import json
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TRENDS = ROOT / "docs" / "trends"
OUT = ROOT / "docs" / "research" / "brand-scan"
ART = ROOT / "out" / "brand-scan"
CAP = 2500
COST = {"channels.list": 1, "playlists.list": 1, "search.list": 100}


class Budget:
    def __init__(self, cap=CAP):
        self.cap, self.used = cap, 0

    def spend(self, m):
        if self.used + COST[m] > self.cap:
            return False
        self.used += COST[m]
        return True


def trim(t, n):
    t = " ".join((t or "").split())
    return t if len(t) <= n else t[: n - 1] + "…"


def pick_channels(scan: dict, deep: dict) -> list[str]:
    by_title = {r["channel"]: r.get("channel_id") for r in scan.get("rows", [])}
    ids = [by_title.get(v["channel"]) for v in deep.get("videos", [])]
    ids += [r.get("channel_id") for r in scan.get("rows_wide", [])
            if (r.get("channel_age_days") or 9999) < 365 and r["per_day"] >= 100_000]
    out = []
    for i in ids:
        if i and i not in out:
            out.append(i)
    return out


def channel_rows(yt, ids, now, budget):
    rows = []
    for i in range(0, len(ids), 50):
        if not budget.spend("channels.list"):
            break
        r = yt.channels().list(part="snippet,statistics,brandingSettings", id=",".join(ids[i:i + 50])).execute()
        for c in r.get("items", []):
            sn, st, br = c["snippet"], c.get("statistics", {}), c.get("brandingSettings", {})
            made = sn.get("publishedAt")
            rows.append({
                "id": c["id"], "title": sn.get("title", ""), "handle": sn.get("customUrl"),
                "description": trim(sn.get("description"), 300), "country": sn.get("country"),
                "created": made,
                "age_days": round((now - dt.datetime.fromisoformat(made.replace("Z", "+00:00"))).days) if made else None,
                "subscribers": None if st.get("hiddenSubscriberCount") else int(st.get("subscriberCount", 0)),
                "videos": int(st.get("videoCount", 0)),
                "banner": bool(br.get("image", {}).get("bannerExternalUrl")),
                "keywords": trim(br.get("channel", {}).get("keywords"), 200),
                "avatar_url": sn.get("thumbnails", {}).get("high", {}).get("url"),
                "banner_url": br.get("image", {}).get("bannerExternalUrl"),
            })
    return rows


def playlists(yt, cid, budget):
    if not budget.spend("playlists.list"):
        return None
    try:
        r = yt.playlists().list(part="snippet,contentDetails", channelId=cid, maxResults=50).execute()
    except Exception:  # noqa: BLE001
        return None
    return [{"title": trim(p["snippet"]["title"], 80), "items": p.get("contentDetails", {}).get("itemCount")}
            for p in r.get("items", [])]


def name_check(yt, name, budget):
    if not budget.spend("search.list"):
        return None
    r = yt.search().list(part="snippet", q=name, type="channel", maxResults=10).execute()
    hits = [{"id": it["id"]["channelId"], "title": it["snippet"]["channelTitle"]} for it in r.get("items", [])]
    if hits and budget.spend("channels.list"):
        subs = {c["id"]: c for c in yt.channels().list(part="statistics,snippet", id=",".join(h["id"] for h in hits)
                                                         ).execute().get("items", [])}
        for h in hits:
            c = subs.get(h["id"], {})
            st = c.get("statistics", {})
            h["subscribers"] = None if st.get("hiddenSubscriberCount") else int(st.get("subscriberCount", 0) or 0)
            h["handle"] = c.get("snippet", {}).get("customUrl")
    norm = lambda s: "".join(ch for ch in s.lower() if ch.isalnum())  # noqa: E731
    exact = [h for h in hits if norm(h["title"]) == norm(name) or norm(h.get("handle") or "") == "@" + norm(name)
             or norm(h.get("handle") or "") == norm(name)]
    return {"name": name, "exact": exact, "top": hits[:5]}


def sheet(rows, path):
    """Numbered contact sheet of avatars (for the run artifact only)."""
    from PIL import Image, ImageDraw
    n, size = len(rows), 160
    cols = 8
    img = Image.new("RGB", (cols * size, ((n + cols - 1) // cols) * (size + 20)), "white")
    d = ImageDraw.Draw(img)
    for k, r in enumerate(rows):
        x, y = (k % cols) * size, (k // cols) * (size + 20)
        try:
            raw = urllib.request.urlopen(r["avatar_url"], timeout=10).read()
            img.paste(Image.open(io.BytesIO(raw)).convert("RGB").resize((size - 4, size - 4)), (x + 2, y + 2))
        except Exception:  # noqa: BLE001
            pass
        d.text((x + 4, y + size), f"{k + 1}", fill="black")
    path.parent.mkdir(parents=True, exist_ok=True)
    img.save(path)


def report(rows, names, day, units):
    L = [f"# Brand scan {day}", "", f"{len(rows)} fast-growing story channels (from the deep and wide trend scans), and "
         f"{len(names)} candidate names checked by channel search. Written by `scripts/brand_scan.py`. "
         f"API units: {units}.", "",
         "| # | Channel | Handle | Words | Age (d) | Subs | Banner | Playlists | Description starts |", "|---|---|---|---|---|---|---|---|---|"]
    for k, r in enumerate(rows, 1):
        pl = r.get("playlists")
        L.append(f"| {k} | {r['title']} | {r['handle'] or ''} | {len(r['title'].split())} | {r['age_days']} | "
                 f"{r['subscribers'] if r['subscribers'] is not None else 'hidden'} | {'yes' if r['banner'] else 'no'} | "
                 f"{'?' if pl is None else len(pl)} | {trim(r['description'], 70).replace('|', '/')} |")
    L += ["", "## Candidate names", "", "| Name | Exact matches (subs) | Closest results |", "|---|---|---|"]
    for c in names:
        if c is None:
            continue
        ex = ", ".join(f"{h['title']} ({h.get('subscribers')})" for h in c["exact"]) or "none"
        top = ", ".join(f"{h['title']} ({h.get('subscribers')})" for h in c["top"])
        L.append(f"| {c['name']} | {ex} | {top} |")
    return "\n".join(L) + "\n"


def main(argv):
    sys.path.insert(0, str(Path(__file__).parent))
    from trends import youtube

    scan = json.loads(sorted(TRENDS.glob("????-??-??.json"))[-1].read_text())
    deep_files = sorted((TRENDS / "deep").glob("*.json"))
    deep = json.loads(deep_files[-1].read_text()) if deep_files else {}
    now = dt.datetime.now(dt.timezone.utc)
    yt, budget = youtube(), Budget()
    rows = channel_rows(yt, pick_channels(scan, deep), now, budget)
    for r in rows:
        r["playlists"] = playlists(yt, r["id"], budget)
    import os
    cands = argv[1:] or [n.strip() for n in os.environ.get("BRAND_NAMES", "").split(";") if n.strip()]
    names = [name_check(yt, n, budget) for n in cands]
    try:
        sheet(rows, ART / "avatars.png")
    except Exception as e:  # noqa: BLE001
        print("contact sheet failed:", e)
    day = now.date().isoformat()
    OUT.mkdir(parents=True, exist_ok=True)
    public = [{k: v for k, v in r.items() if k not in ("avatar_url", "banner_url")} for r in rows]
    (OUT / f"{day}.json").write_text(json.dumps({"channels": public, "names": names, "units": budget.used},
                                                indent=1, ensure_ascii=False) + "\n")
    md = report(rows, [n for n in names if n], day, budget.used)
    (OUT / f"{day}.md").write_text(md)
    print(md)


if __name__ == "__main__":
    sys.exit(main(sys.argv))
