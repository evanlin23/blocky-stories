"""Weekly compilation: about 20 minutes of our published stories as one 16:9 long-form video.

    python scripts/compile.py [--minutes 20] [--dry-run]

It picks the uploaded stories not yet in a compilation, oldest first, until the running time reaches about 20
minutes. Each story's film plays in full, centred on a blurred copy of itself so the frame is 16:9; joined
that way, YouTube treats the result as a normal long video, not a Short. The description lists a chapter per
story. The thumbnail is the stories' own cover frames side by side. It goes up private and publishes on its own
at noon Central, separate from the daily Short (owner, 2026-11-02: once a week, and it doesn't count as the day's
upload). compilations.json records what went in, so no story repeats until every story has been used.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import subprocess
import sys
import tempfile
from pathlib import Path

from stories import ROOT, film, slug, uploads
from upload import already_on_channel, fetch, push, youtube

from blocky.gate import load_package

COMPILATIONS = ROOT / "compilations.json"
TITLE = "In This Town / In This World: Creepy Story Animation Compilation"
PUBLISH_HOUR_CENTRAL = 12


def stamp(sec: float) -> str:
    s = int(sec)
    h, m, s = s // 3600, s % 3600 // 60, s % 60
    return f"{h}:{m:02d}:{s:02d}" if h else f"{m}:{s:02d}"


def chapters(parts: list[tuple[str, float]]) -> str:
    """YouTube chapter lines: the first at 0:00, one per story."""
    out, t = [], 0.0
    for title, dur in parts:
        out.append(f"{stamp(t)} {title}")
        t += dur
    return "\n".join(out)


def pick(candidates: list[tuple[str, float]], minutes: float) -> list[str]:
    """Oldest first until the total reaches the target; at least 5 stories, or nothing."""
    chosen, total = [], 0.0
    for s, dur in candidates:
        if total >= minutes * 60:
            break
        chosen.append(s)
        total += dur
    return chosen if len(chosen) >= 5 and total >= 0.75 * minutes * 60 else []


def compiled() -> dict:
    return json.loads(COMPILATIONS.read_text()) if COMPILATIONS.exists() else {}


def duration(mp4: Path) -> float:
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(mp4)],
                       capture_output=True, text=True, check=True)
    return float(r.stdout.strip())


def widescreen(src: Path, dst: Path) -> None:
    """Vertical film → 1920x1080: the film centred at full height on a blurred, darkened copy of itself."""
    vf = ("[0:v]split[a][b];[a]scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080,"
          "boxblur=30:3,eq=brightness=-0.15[bg];[b]scale=-2:1080[fg];[bg][fg]overlay=(W-w)/2:0,setsar=1,fps=30[v]")
    subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-y", "-i", str(src), "-filter_complex", vf, "-map", "[v]",
                    "-map", "0:a", "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-c:a", "aac", "-b:a",
                    "192k", "-ar", "48000", str(dst)], check=True)


def thumbnail(covers: list[Path], dst: Path) -> None:
    """The stories' cover frames side by side, 1280x720 (5 at most, so faces still read)."""
    covers = covers[:5]
    w = 1280 // len(covers)
    args = ["ffmpeg", "-nostdin", "-v", "error", "-y"]
    for c in covers:
        args += ["-i", str(c)]
    scale = "".join(f"[{i}:v]scale={w}:720:force_original_aspect_ratio=increase,crop={w}:720[c{i}];"
                    for i in range(len(covers)))
    stack = "".join(f"[c{i}]" for i in range(len(covers))) + f"hstack=inputs={len(covers)},scale=1280:720[t]"
    if len(covers) == 1:
        stack = "[c0]scale=1280:720[t]"
    subprocess.run(args + ["-filter_complex", scale + stack, "-map", "[t]", "-frames:v", "1", str(dst)], check=True)


def cover_frame(d: Path, s: str, mp4: Path, dur: float) -> Path:
    jpg = next(d.rglob(f"{s}.cover.jpg"), None)
    if jpg:
        return jpg
    out = d / f"{s}.thumb.jpg"   # films rendered before cover frames existed: take one near the reveal
    subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-y", "-ss", f"{dur * 0.78:.2f}", "-i", str(mp4),
                    "-frames:v", "1", "-q:v", "3", str(out)], check=True)
    return out


def publish_at(now: dt.datetime | None = None) -> str:
    from zoneinfo import ZoneInfo

    tz = ZoneInfo("America/Chicago")
    now = (now or dt.datetime.now(dt.timezone.utc)).astimezone(tz)
    at = now.replace(hour=PUBLISH_HOUR_CENTRAL, minute=0, second=0, microsecond=0)
    if at < now + dt.timedelta(minutes=30):
        at = now + dt.timedelta(hours=1)
    return at.astimezone(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--minutes", type=float, default=20)
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    done, comps = uploads(), compiled()
    used = {s for c in comps.values() for s in c["stories"]}
    pool = [s for s, e in done.items() if e.get("video_id") or e.get("uploaded") or e.get("issued")]
    fresh = [s for s in pool if s not in used and film(s)]
    if sum(1 for _ in fresh) < 5:   # every story's been used: start the cycle again from the oldest
        fresh = [s for s in pool if film(s)]
    with tempfile.TemporaryDirectory() as td:
        td = Path(td)
        got: list[tuple[str, float, Path, Path, dict]] = []
        for s in fresh:
            d = td / s
            d.mkdir()
            try:
                mp4, flash = fetch(s, d)
            except (subprocess.CalledProcessError, StopIteration):
                print(f"{s}: no film to use, skipped")
                continue
            dur = duration(mp4)
            got.append((s, dur, mp4, cover_frame(d, slug(s), mp4, dur), flash))
            if sum(g[1] for g in got) >= a.minutes * 60:
                break
        chosen = pick([(g[0], g[1]) for g in got], a.minutes)
        if not chosen:
            print(f"not enough published stories for a {a.minutes:g}-minute compilation yet ({len(got)} with films)")
            return
        parts = [g for g in got if g[0] in chosen]
        titles = [(load_package(s) or {}).get("title", s) for s, *_ in parts]
        total = sum(p[1] for p in parts)
        flashing = any(p[4].get("description_line") for p in parts)
        desc = ((("Flashing lights in places.\n\n") if flashing else "")
                + f"{len(parts)} creepy blocky stories, each in a town with one strange rule. It's all made up.\n\n"
                + chapters([(t, p[1]) for t, p in zip(titles, parts)]) + "\n\nA creepy blocky story compilation, "
                "built with code and Blender.\n")
        title = f"{TITLE} ({round(total / 60)} min)"
        print(title, "\n", desc)
        if a.dry_run:
            return
        wides = []
        for s, dur, mp4, cov, _ in parts:
            w = td / f"{s}.wide.mp4"
            widescreen(mp4, w)
            wides.append(w)
        lst = td / "list.txt"
        lst.write_text("".join(f"file '{w}'\n" for w in wides))
        out = td / "compilation.mp4"
        subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(lst),
                        "-c", "copy", "-movflags", "+faststart", str(out)], check=True)
        thumb = td / "thumb.jpg"
        thumbnail([p[3] for p in parts], thumb)
        yt = youtube()
        if already_on_channel(yt, title):
            print("a compilation with this title is already on the channel; not uploading again")
            return
        from googleapiclient.http import MediaFileUpload

        when = publish_at()
        body = {"snippet": {"title": title, "description": desc, "categoryId": "24"},
                "status": {"privacyStatus": "private", "publishAt": when, "selfDeclaredMadeForKids": False,
                           "containsSyntheticMedia": False}}
        req = yt.videos().insert(part="snippet,status", body=body,
                                 media_body=MediaFileUpload(str(out), mimetype="video/mp4", chunksize=16 << 20,
                                                            resumable=True))
        resp = None
        while resp is None:
            st, resp = req.next_chunk()
            if st:
                print(f"uploaded {int(st.progress() * 100)}%", flush=True)
        vid = resp["id"]
        try:   # custom thumbnails need a phone-verified channel; carry on without one
            yt.thumbnails().set(videoId=vid, media_body=MediaFileUpload(str(thumb), mimetype="image/jpeg")).execute()
        except Exception as e:  # noqa: BLE001
            print(f"thumbnail not set: {e}")
        import playlists
        playlists.add(yt, vid, ["compilations"])   # never raises
        comps[dt.date.today().isoformat()] = {"video_id": vid, "title": title, "stories": chosen, "publish_at": when}
        COMPILATIONS.write_text(json.dumps(comps, indent=1) + "\n")
        subprocess.run(["git", "-C", str(ROOT), "add", "compilations.json"], check=True)
        if playlists.FILE.exists():
            subprocess.run(["git", "-C", str(ROOT), "add", str(playlists.FILE)], check=True)
        subprocess.run(["git", "-C", str(ROOT), "commit", "-m", f"compilation: {len(chosen)} stories"], check=True)
        push()
        print(f"compilation uploaded: https://studio.youtube.com/video/{vid}/edit (public at {when})")


if __name__ == "__main__":
    sys.exit(main())
