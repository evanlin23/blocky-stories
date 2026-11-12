"""Channel playlists, and the newest compilation for a Short's related video (owner, 2026-11-08).

Every story upload joins "all"; an interactive-lane story (package.json "lane": "interactive") also joins
"interactive"; each weekly compilation joins "compilations". The playlists are made on first use and their ids kept in
playlists.json (committed with the upload record). A playlist problem never fails an upload: `add` reports what it
couldn't do, and the upload issue tells the owner to do that by hand.

A Short's related-video link can't be set through the API (only in Studio: Content, the Short, Details, Related video),
so the upload issue names the newest compilation to link it to (`latest_compilation`).
"""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FILE = ROOT / "playlists.json"
COMPILATIONS = ROOT / "compilations.json"
RETRY_S = 10   # wait before the one retry of a playlist add

PLAYLISTS = {
    "all": ("Every Buhtown Story", "Every creepy blocky story from Buhtown, in the order they came out."),
    "interactive": ("Who Do You Trust? Comment 1 or 2",
                    "Two messages, one choice. Every story leaves clues for both sides. Which one would you trust?"),
    "compilations": ("Buhtown Story Compilations", "About 20 minutes of creepy blocky stories in one sitting."),
}


def load() -> dict:
    return json.loads(FILE.read_text()) if FILE.exists() else {}


def keys_for(pkg: dict | None) -> list[str]:
    """The playlists a story upload joins."""
    return ["all"] + (["interactive"] if (pkg or {}).get("lane") == "interactive" else [])


def ensure(yt, key: str) -> str:
    """The playlist id for `key`, making the playlist (public) the first time and recording it in playlists.json."""
    ids = load()
    if ids.get(key):
        return ids[key]
    title, desc = PLAYLISTS[key]
    r = yt.playlists().insert(part="snippet,status", body={
        "snippet": {"title": title, "description": desc}, "status": {"privacyStatus": "public"}}).execute()
    ids[key] = r["id"]
    FILE.write_text(json.dumps(ids, indent=1) + "\n")
    return r["id"]


def add(yt, video_id: str, keys: list[str]) -> list[str]:
    """Add the video to each playlist; returns the keys that failed. Never raises: a playlist mustn't stop an upload."""
    import time

    failed = []
    for k in keys:
        for attempt in range(2):   # a playlist made a moment ago can refuse its first item (ep48, 2026-11-09)
            try:
                yt.playlistItems().insert(part="snippet", body={"snippet": {
                    "playlistId": ensure(yt, k), "resourceId": {"kind": "youtube#video", "videoId": video_id}}}).execute()
                break
            except Exception as e:  # noqa: BLE001
                print(f"playlist {k}: not added on try {attempt + 1} ({type(e).__name__}: {e})")
                if attempt:
                    failed.append(k)
                else:
                    time.sleep(RETRY_S)
    return failed


def latest_compilation() -> str | None:
    """The newest compilation's watch link, for a Short's related video (None before the first one)."""
    comps = json.loads(COMPILATIONS.read_text()) if COMPILATIONS.exists() else {}
    for day in sorted(comps, reverse=True):
        vid = (comps[day] or {}).get("video_id")
        if vid:
            return f"https://www.youtube.com/watch?v={vid}"
    return None


def owner_steps(failed: list[str]) -> str:
    """Lines for the upload issue: the related-video link to set by hand, and any playlist the API couldn't add."""
    out = []
    comp = latest_compilation()
    if comp:
        out.append(f"Set its **related video** to the newest compilation (Studio: Content, this Short, Details, "
                   f"Related video): {comp}")
    for k in failed:
        out.append(f"Add it to the playlist **{PLAYLISTS[k][0]}** (the API couldn't).")
    return "".join(f"- {x}\n" for x in out)
