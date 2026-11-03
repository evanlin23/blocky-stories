"""Daily upload: the next ready story goes to PandaNanoAdventures as a PRIVATE video, and an issue tells the owner.

    python scripts/upload.py [--story NAME] [--dry-run]

Ready means: not in uploads.json, the gate is open, and the render workflow's film artifact has a passing flash
report. The oldest episode number goes first. One story per run (the workflow runs once a day).

With the YouTube secrets set (YT_CLIENT_ID, YT_CLIENT_SECRET, YT_REFRESH_TOKEN; docs/youtube-setup.md) and the
repo variable YT_AUDITED=true (after the API audit is approved), the film is uploaded with the package's title and description, made for kids: No. Without them, the issue carries the
download link and the text to paste, for an upload by hand. Either way the owner publishes it.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

from stories import ROOT, UPLOADS, all_stories, changed_since, film, gate_open, slug, uploads

from blocky.gate import load_package

REPO = os.environ.get("GITHUB_REPOSITORY", "evanlin23/blocky-stories")


def queue() -> list[str]:
    """queue.txt: story folders to upload first, in order (blank lines and # comments ignored)."""
    q = ROOT / "queue.txt"
    names = [ln.strip() for ln in q.read_text().splitlines()] if q.exists() else []
    return [n for n in names if n and not n.startswith("#") and (ROOT / "stories" / n / "story.json").exists()]


def shape(story: str) -> str:
    """package.json's optional `shape`: a short tag for the twist's shape (e.g. "stand-in")."""
    try:
        pkg = load_package(story) or {}
    except FileNotFoundError:   # an uploaded story whose folder is gone
        pkg = {}
    return str(pkg.get("shape", "")).strip().lower()


def next_story(done: dict, skip: frozenset = frozenset()) -> str | None:
    """The oldest ready story, skipping past one whose twist shape matches the last upload's, so two in a row
    never end the same way (a story is only held back while another ready one can go first)."""
    last = shape(next(reversed(done))) if done else ""
    held = None
    for s in queue() + [x for x in all_stories() if x not in queue()]:
        if s in done or s in skip or (load_package(s) or {}).get("hold"):   # held for a redo (RULES → Packaging)
            continue
        f = film(s)
        if f and f.get("created_at") and changed_since(s, f["created_at"]):   # its film predates a fix: wait for the re-render
            continue
        if f and gate_open(s):
            if not last or shape(s) != last:
                return s
            held = held or s
    return held


def cover(d: Path, s: str) -> tuple[str, str] | None:
    """Commit the film's cover frame to covers/<slug>.jpg so the issue can show it; returns (url, m:ss)."""
    jpg = next(d.rglob(f"{s}.cover.jpg"), None)
    if jpg is None:
        return None
    txt = next(d.rglob(f"{s}.cover.txt"), None)
    t = float(txt.read_text().strip()) if txt else 0.0
    dst = ROOT / "covers" / f"{s}.jpg"
    dst.parent.mkdir(exist_ok=True)
    dst.write_bytes(jpg.read_bytes())
    subprocess.run(["git", "-C", str(ROOT), "add", str(dst)], check=True)
    return f"https://raw.githubusercontent.com/{REPO}/main/covers/{s}.jpg", f"{int(t) // 60}:{int(t) % 60:02d}"


def fetch(story: str, d: Path) -> tuple[Path, dict]:
    f = film(story)
    if f and f.get("legacy"):   # an approved final from the content repo: its description already has the flash line
        return Path(f["legacy"]), {"house_bar": {"pass": True}, "description_line": None}
    subprocess.run(["gh", "run", "download", str(f["run_id"]), "--repo", REPO, "-n", f"film-{story}", "-D", str(d)],
                   check=True)
    s = slug(story)
    mp4 = next(d.rglob(f"{s}.mp4"))
    return mp4, json.loads(next(d.rglob(f"{s}.flash.json")).read_text())


def description(pkg: dict, flash: dict) -> str:
    """The package's description, opening with the measured flashing line when the film has one."""
    text = pkg["description"].strip()
    line = flash.get("description_line")
    if line and not text.startswith("Flashing"):
        text = f"{line}\n\n{text}"
    return text + "\n"


def youtube():
    from google.oauth2.credentials import Credentials
    from googleapiclient.discovery import build

    creds = Credentials(None, refresh_token=os.environ["YT_REFRESH_TOKEN"], client_id=os.environ["YT_CLIENT_ID"],
                        client_secret=os.environ["YT_CLIENT_SECRET"], token_uri="https://oauth2.googleapis.com/token")
    # no scopes here: the refresh token carries whatever it was granted (upload, readonly, analytics)
    return build("youtube", "v3", credentials=creds, cache_discovery=False)


PUBLISH_AT_CENTRAL = 16   # 4:00 PM Central: after school for the Shorts audience, and a window for the owner to stop one


def publish_at(now: dt.datetime | None = None) -> str | None:
    """When the upload goes public on its own (YouTube's scheduled publish), as RFC 3339 UTC: today at 4:00 PM
    Central, or an hour from now if that's already past. None when YT_AUTOPUBLISH=false (stays private)."""
    if os.environ.get("YT_AUTOPUBLISH", "true").strip().lower() == "false":
        return None
    from zoneinfo import ZoneInfo

    tz = ZoneInfo("America/Chicago")
    now = (now or dt.datetime.now(dt.timezone.utc)).astimezone(tz)
    at = now.replace(hour=PUBLISH_AT_CENTRAL, minute=0, second=0, microsecond=0)
    if at < now + dt.timedelta(minutes=30):
        at = now + dt.timedelta(hours=1)
    return at.astimezone(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def already_on_channel(yt, title: str) -> str | None:
    """The video id if the channel's last 50 uploads already hold this exact title (a run that uploaded but
    crashed before recording it), so it's never uploaded twice."""
    ch = yt.channels().list(part="contentDetails", mine=True).execute().get("items", [])
    if not ch:
        return None
    pl = ch[0]["contentDetails"]["relatedPlaylists"]["uploads"]
    items = yt.playlistItems().list(part="snippet", playlistId=pl, maxResults=50).execute().get("items", [])
    pulled = json.loads((ROOT / "pulled.json").read_text()) if (ROOT / "pulled.json").exists() else {}
    for it in items:   # pulled.json: videos taken down for a fix, so the fixed film may go up again
        vid = it["snippet"]["resourceId"]["videoId"]
        if it["snippet"]["title"].strip() == title.strip() and vid not in pulled:
            return vid
    return None


def upload(yt, mp4: Path, title: str, desc: str, when: str | None = None) -> str:
    from googleapiclient.http import MediaFileUpload

    want = os.environ.get("YT_CHANNEL_ID", "").strip()
    if want:   # never upload to the wrong channel
        me = yt.channels().list(part="snippet", mine=True).execute().get("items", [])
        ids = [c["id"] for c in me]
        if want not in ids:
            sys.exit(f"the token belongs to {ids}, not YT_CHANNEL_ID {want}; refusing to upload")
    body = {
        "snippet": {"title": title, "description": desc, "categoryId": "24"},   # Entertainment
        "status": {"privacyStatus": "private", "selfDeclaredMadeForKids": False, "containsSyntheticMedia": False},
    }
    if when:   # YouTube makes it public at this time on its own
        body["status"]["publishAt"] = when
    req = yt.videos().insert(part="snippet,status", body=body,
                             media_body=MediaFileUpload(str(mp4), mimetype="video/mp4", chunksize=16 << 20,
                                                        resumable=True))
    resp = None
    while resp is None:
        status, resp = req.next_chunk()
        if status:
            print(f"uploaded {int(status.progress() * 100)}%", flush=True)
    return resp["id"]


def issue(title: str, body: str) -> None:
    subprocess.run(["gh", "issue", "create", "--repo", REPO, "--title", title, "--body", body], check=True)


def record(story: str, entry: dict) -> None:
    done = uploads()
    done[story] = entry
    UPLOADS.write_text(json.dumps(done, indent=1) + "\n")
    subprocess.run(["git", "-C", str(ROOT), "add", "uploads.json"], check=True)
    subprocess.run(["git", "-C", str(ROOT), "commit", "-m", f"uploads: {story}"], check=True)
    push()


def push(tries: int = 6) -> None:
    """Push the uploads.json commit. main moves often (story PRs merge all day), so rebase onto it and retry: a
    lost record would upload the same story again tomorrow."""
    import time

    for i in range(tries):
        if subprocess.run(["git", "-C", str(ROOT), "push", "origin", "HEAD:main"]).returncode == 0:
            return
        time.sleep(2 * (i + 1))
        subprocess.run(["git", "-C", str(ROOT), "pull", "--rebase", "origin", "main"], check=True)
    sys.exit("could not push uploads.json after several tries: record the upload by hand")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--story", default="")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    done = uploads()
    today = dt.date.today().isoformat()
    if not a.story and any(today in (e.get("uploaded"), e.get("issued")) for e in done.values()):
        print("already posted one today")   # the backup run found the first one worked
        return
    failed: set[str] = set()
    while True:   # a film that fails the flash bar never blocks the day: take the next one
        story = a.story or next_story(done, frozenset(failed))
        if not story:
            print("nothing ready to upload today" + (f" (flash fails: {sorted(failed)})" if failed else ""))
            return
        td_obj = tempfile.TemporaryDirectory()
        mp4, flash = fetch(story, Path(td_obj.name))
        if flash.get("house_bar", {}).get("pass"):
            break
        print(f"{story}: the film fails the flash bar; skipping it (redraw the shots its flash report names)")
        td_obj.cleanup()
        if a.story:
            sys.exit(1)
        failed.add(story)
    pkg = load_package(story)
    s = slug(story)
    rel = film(story)["url"] + " (the `film-" + story + "` artifact, at the bottom of the run page)"
    with td_obj as td:
        desc = description(pkg, flash)
        title = pkg["title"]
        print(f"{story}: {title!r} ({mp4.stat().st_size / 1e6:.0f} MB)")
        if a.dry_run:
            print(desc)
            return
        pin = pkg.get("pin", "")
        # API uploads only once the audit is approved (repo variable YT_AUDITED=true): before that, YouTube locks
        # every API upload as private for good, so the owner uploads by hand from the issue instead
        audited = os.environ.get("YT_AUDITED", "").strip().lower() == "true"
        have = {k: bool(os.environ.get(k)) for k in ("YT_CLIENT_ID", "YT_CLIENT_SECRET", "YT_REFRESH_TOKEN")}
        print(f"API upload: YT_AUDITED={'true' if audited else 'not true'}, secrets present: {have}")   # no values
        if audited and all(os.environ.get(k) for k in ("YT_CLIENT_ID", "YT_CLIENT_SECRET", "YT_REFRESH_TOKEN")):
            when = publish_at()
            yt = youtube()
            dup = already_on_channel(yt, title)
            if dup:   # uploaded before but never recorded: record it, don't upload again
                record(story, {"video_id": dup, "uploaded": today, "title": title, "note": "found on the channel"})
                print(f"{story}: already on the channel as {dup}; recorded it, no new upload")
                return
            vid = upload(yt, mp4, title, desc, when)
            record(story, {"video_id": vid, "uploaded": today, "title": title, "publish_at": when})
            from zoneinfo import ZoneInfo
            local = (dt.datetime.strptime(when, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=dt.timezone.utc)
                     .astimezone(ZoneInfo("America/Chicago")).strftime("%-I:%M %p Central") if when else "")
            steps = (f"It goes **public on its own at {local}**. To stop it, set it to Private in Studio before then.\n\n"
                     f"1. Watch it if you like: https://studio.youtube.com/video/{vid}/edit\n"
                     f"2. Once it's public, post and pin this comment:\n\n> {pin}\n\n" if when else
                     f"1. Watch it: https://studio.youtube.com/video/{vid}/edit\n"
                     f"2. Set visibility to Public (or schedule it).\n"
                     f"3. Pin this comment:\n\n> {pin}\n\n")
            issue(f"{'Going public' if when else 'Ready to publish'}: {title}",
                  f"**{s}** is uploaded to PandaNanoAdventures.\n\n" + steps +
                  f"If Studio shows it as *locked* private, API uploads aren't allowed after all: download the film "
                  f"from {rel}, upload it by hand with the text below, and tell Claude.\n\n"
                  f"<details><summary>Title and description</summary>\n\n```\n{title}\n\n{desc}```\n</details>\n\n"
                  f"Close this issue once it's public.")
        else:
            cv = cover(Path(td), s)
            record(story, {"manual": True, "issued": today, "title": title})
            shot = (f"**Cover** (pick the {cv[1]} moment as the Short's thumbnail):\n\n![cover]({cv[0]})\n\n" if cv else "")
            issue(f"Upload by hand: {title}",
                  f"**{s}** is ready for PandaNanoAdventures.\n\n"
                  f"**Video:** open {film(story)['url']} and tap **film-{story}** under Artifacts "
                  f"(a zip with `{s}.mp4`).\n\n"
                  f"**Title**\n```\n{title}\n```\n**Description**\n```\n{desc}```\n"
                  f"**Pinned comment** (post it as your own first comment)\n```\n{pin}\n```\n"
                  f"**Settings:** Made for kids: **No**. Altered or synthetic content: **No**.\n\n"
                  f"{shot}Close this issue once it's public.")


if __name__ == "__main__":
    main()
