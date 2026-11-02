"""Post each uploaded story's comment (package.json "pin") as the channel, once the video is public.

    python scripts/comment.py [--dry-run]

The owner can't pin comments, and the API has no pin call, so the channel's own first comment carries the pin text.
It needs the `youtube.force-ssl` scope on the refresh token (docs/youtube-setup.md). It runs on a schedule
(comments.yml); each video gets one comment, recorded as "commented" in uploads.json.
"""

from __future__ import annotations

import argparse
import sys

from stories import uploads
from upload import record, youtube

from blocky.gate import load_package


def due(done: dict, status: dict[str, str]) -> list[str]:
    """Stories uploaded through the API, public now, and not yet commented on."""
    return [s for s, e in done.items()
            if e.get("video_id") and not e.get("commented") and status.get(e["video_id"]) == "public"]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    done = uploads()
    ids = [e["video_id"] for e in done.values() if e.get("video_id") and not e.get("commented")]
    if not ids:
        print("nothing to comment on")
        return
    yt = youtube()
    items = yt.videos().list(part="status", id=",".join(ids[:50])).execute().get("items", [])
    status = {v["id"]: v["status"]["privacyStatus"] for v in items}
    for s in due(done, status):
        pkg = load_package(s) or {}
        text = str(pkg.get("pin", "")).strip()
        vid = done[s]["video_id"]
        if not text:
            continue
        print(f"{s}: commenting on {vid}: {text!r}")
        if a.dry_run:
            continue
        yt.commentThreads().insert(part="snippet", body={"snippet": {"videoId": vid, "topLevelComment": {
            "snippet": {"textOriginal": text}}}}).execute()
        record(s, {**done[s], "commented": True})
        done = uploads()
    waiting = [s for s, e in done.items() if e.get("video_id") and not e.get("commented")]
    print(f"waiting to go public: {waiting}" if waiting else "all comments posted")


if __name__ == "__main__":
    sys.exit(main())
