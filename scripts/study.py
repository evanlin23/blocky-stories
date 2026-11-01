"""Study other people's Shorts and Reels, so the writer learns from what works: `python scripts/study.py <url or mp4> ...`

For each video it writes out/study/<id>/ (gitignored, deleted with --clean):
- hook.png       the first 3 seconds, 4 frames a second, with timestamps (what makes people stay)
- sheet-N.png    the rest at 1 frame a second, 30 to a sheet
- report.json    title, channel, views, likes, comments count, length, upload date, the top comments by likes,
                 a timestamped transcript with words a minute, the shot cuts and cuts a second, loudness and
                 silences (music drops)

An analyst subagent then reads the sheets and the report (see .claude/agents/analyst.md). Only its written notes
go in the repo (docs/research/). Never commit anyone else's video or frames: this repo is public.

Downloads use yt-dlp. YouTube and Instagram usually want a signed-in session: put a Netscape cookies.txt from a
throwaway account in $YTDLP_COOKIES (a path), or base64 of it in $YTDLP_COOKIES_B64.
"""

from __future__ import annotations

import argparse
import base64
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "out" / "study"


def cookies() -> list[str]:
    if os.environ.get("YTDLP_COOKIES") and Path(os.environ["YTDLP_COOKIES"]).exists():
        return ["--cookies", os.environ["YTDLP_COOKIES"]]
    if os.environ.get("YTDLP_COOKIES_B64"):
        f = Path(tempfile.gettempdir()) / "ytdlp-cookies.txt"
        f.write_bytes(base64.b64decode(os.environ["YTDLP_COOKIES_B64"]))
        f.chmod(0o600)
        return ["--cookies", str(f)]
    return []


def fetch(url: str, d: Path) -> tuple[Path, dict]:
    """Download one video (720p at most) with its info and top comments."""
    d.mkdir(parents=True, exist_ok=True)
    cmd = ["yt-dlp", "-q", "--no-warnings", *cookies(), "-f", "bv*[height<=720]+ba/b[height<=720]/b",
           "--merge-output-format", "mp4", "--write-info-json", "--write-comments",
           "--extractor-args", "youtube:max_comments=40,all,0;comment_sort=top", "-o", str(d / "video.%(ext)s"), url]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(r.stderr.strip().splitlines()[-1] if r.stderr.strip() else "yt-dlp failed")
    info = json.loads((d / "video.info.json").read_text())
    return d / "video.mp4", info


def frames(mp4: Path, times: list[float], w: int = 216) -> list[Image.Image]:
    out = []
    for t in times:
        png = subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-ss", f"{t:.2f}", "-i", str(mp4), "-frames:v", "1",
                              "-vf", f"scale={w}:-2", "-f", "image2pipe", "-vcodec", "png", "-"],
                             capture_output=True).stdout
        if png:
            from io import BytesIO

            out.append((t, Image.open(BytesIO(png)).convert("RGB")))
    return out


def sheet(shots, cols: int, path: Path, title: str) -> None:
    if not shots:
        return
    tw, th = shots[0][1].size
    rows = (len(shots) + cols - 1) // cols
    img = Image.new("RGB", (cols * (tw + 6) + 6, rows * (th + 24) + 34), (20, 20, 24))
    dr = ImageDraw.Draw(img)
    dr.text((8, 8), title[:120], fill=(240, 240, 240))
    for i, (t, im) in enumerate(shots):
        x, y = 6 + (i % cols) * (tw + 6), 30 + (i // cols) * (th + 24)
        img.paste(im, (x, y + 18))
        dr.text((x + 2, y + 3), f"{t:5.2f}s", fill=(255, 220, 90))
    img.save(path)


def duration(mp4: Path) -> float:
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(mp4)],
                       capture_output=True, text=True)
    return float(r.stdout.strip() or 0)


def cuts(mp4: Path) -> list[float]:
    r = subprocess.run(["ffmpeg", "-nostdin", "-i", str(mp4), "-vf", "select='gt(scene,0.3)',showinfo", "-an",
                        "-f", "null", "-"], capture_output=True, text=True)
    return [round(float(m), 2) for m in re.findall(r"pts_time:([\d.]+)", r.stderr)]


def audio(mp4: Path) -> dict:
    r = subprocess.run(["ffmpeg", "-nostdin", "-i", str(mp4), "-af", "silencedetect=n=-38dB:d=0.35,ebur128",
                        "-f", "null", "-"], capture_output=True, text=True)
    sil = [round(float(x), 2) for x in re.findall(r"silence_start: ([\d.]+)", r.stderr)]
    lufs = re.findall(r"I:\s+(-?[\d.]+) LUFS", r.stderr)
    return {"silences_at_s": sil, "lufs": float(lufs[-1]) if lufs else None}


def transcript(mp4: Path) -> dict:
    from faster_whisper import WhisperModel

    model = WhisperModel(os.environ.get("STUDY_WHISPER", "small"), device="cpu", compute_type="int8")
    import numpy as np

    raw = subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-i", str(mp4), "-ac", "1", "-ar", "16000", "-f", "f32le", "-"],
                         capture_output=True).stdout   # ffmpeg decodes, so PyAV versions don't matter
    segs, _ = model.transcribe(np.frombuffer(raw, np.float32), word_timestamps=True, vad_filter=True)
    lines, words = [], 0
    first = last = None
    for s in segs:
        lines.append({"t": round(s.start, 2), "end": round(s.end, 2), "text": s.text.strip()})
        for w in s.words or []:
            words += 1
            first = w.start if first is None else first
            last = w.end
    speaking = (last - first) if first is not None else 0
    return {"lines": lines, "words": words, "wpm_speaking": round(words / speaking * 60) if speaking else 0,
            "first_word_at_s": round(first, 2) if first is not None else None}


def study(src: str, clean_video: bool) -> Path:
    local = Path(src).exists()
    vid = Path(src).stem if local else re.sub(r"[^A-Za-z0-9_-]", "", src.rstrip("/").split("/")[-1].split("?")[0])[-20:]
    d = OUT / vid
    if local:
        d.mkdir(parents=True, exist_ok=True)
        mp4, info = Path(src), {"title": Path(src).name}
    else:
        mp4, info = fetch(src, d)
    L = duration(mp4)
    title = f"{info.get('title', '')} ({info.get('channel') or info.get('uploader') or ''})"
    sheet(frames(mp4, [i / 4 for i in range(12)]), 6, d / "hook.png", "HOOK 0-3 s: " + title)
    rest = [float(t) for t in range(3, int(L) + 1)]
    for k in range(0, len(rest), 30):
        sheet(frames(mp4, rest[k:k + 30]), 6, d / f"sheet-{k // 30 + 1}.png", f"{title}  [{k + 3}s on]")
    c = cuts(mp4)
    top = sorted(info.get("comments") or [], key=lambda x: -(x.get("like_count") or 0))[:20]
    rep = {
        "source": src, "title": info.get("title"), "channel": info.get("channel") or info.get("uploader"),
        "channel_followers": info.get("channel_follower_count"), "views": info.get("view_count"),
        "likes": info.get("like_count"), "comment_count": info.get("comment_count"),
        "uploaded": info.get("upload_date"), "length_s": round(L, 2), "description": (info.get("description") or "")[:600],
        "cuts_at_s": c, "cuts_per_s": round(len(c) / L, 2) if L else None, "audio": audio(mp4),
        "transcript": transcript(mp4),
        "top_comments": [{"likes": x.get("like_count"), "text": (x.get("text") or "")[:300]} for x in top],
        "sheets": sorted(p.name for p in d.glob("*.png")),
    }
    (d / "report.json").write_text(json.dumps(rep, indent=1, ensure_ascii=False))
    if clean_video and not local:
        for f in d.glob("video.*"):
            f.unlink()
    print(f"{d}: {rep['title']!r}, {rep['length_s']} s, {rep['transcript']['wpm_speaking']} wpm, "
          f"{rep['cuts_per_s']} cuts/s, {len(rep['sheets'])} sheets")
    return d


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("src", nargs="+", help="URLs (YouTube, Instagram, anything yt-dlp reads) or local mp4 files")
    ap.add_argument("--keep-video", action="store_true", help="keep the downloaded mp4 (default: delete it)")
    ap.add_argument("--clean", action="store_true", help="delete out/study/ and stop")
    a = ap.parse_args()
    if a.clean:
        shutil.rmtree(OUT, ignore_errors=True)
        return
    bad = 0
    for s in a.src:
        try:
            study(s, not a.keep_video)
        except Exception as e:
            bad += 1
            print(f"FAILED {s}: {e}", file=sys.stderr)
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
