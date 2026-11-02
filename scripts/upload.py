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

from stories import ROOT, UPLOADS, all_stories, film, gate_open, slug, uploads

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
        if s in done or s in skip:
            continue
        if film(s) and gate_open(s):
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


def upload(yt, mp4: Path, title: str, desc: str) -> str:
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
    subprocess.run(["git", "-C", str(ROOT), "push"], check=True)


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
        if audited and all(os.environ.get(k) for k in ("YT_CLIENT_ID", "YT_CLIENT_SECRET", "YT_REFRESH_TOKEN")):
            vid = upload(youtube(), mp4, title, desc)
            record(story, {"video_id": vid, "uploaded": today, "title": title})
            issue(f"Ready to publish: {title}",
                  f"**{s}** is uploaded to PandaNanoAdventures as **private**.\n\n"
                  f"1. Watch it: https://studio.youtube.com/video/{vid}/edit\n"
                  f"2. Set visibility to Public (or schedule it).\n"
                  f"3. Pin this comment:\n\n> {pin}\n\n"
                  f"If Studio shows it as *locked* private, the API audit isn't approved yet: download the film "
                  f"from {rel} and upload it by hand with the text below.\n\n"
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
