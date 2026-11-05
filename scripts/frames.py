"""Frame lint: what a preview's drawn frames show that no review should have to find. Report only.

    python scripts/frames.py --story stories/<name> [--frames out/work/<name>/frames-preview] [--film f.mp4]
                             [--timeline t.json] [--json out.json]

Three mechanical misses that dropped stories at the review or the proof (docs/audit/lessons-log.md 39 and 40):
  blank    a near-uniform frame: the camera inside a wall, a set that didn't build, nothing drawn
           (ep105 S85 and S139; ep120 S67, nine blank frames). Most of the frame within a few levels of one
           colour. An fx "black" or "flash" and the fades at either end are meant, so they're skipped.
  pop      a shot's first drawing differs sharply from its next one while the rest of the shot moves smoothly:
           a character posed a frame late, popping in (ep116 S01, Grandpa missing on frame 0). Measured cell by
           cell (an 8 x 8 grid), so one character appearing counts even when the rest of the frame holds.
  dark     a shot opens dark and brightens over its first ~0.3 s, then holds: a fill light fading in after the
           cut (ep120 S62, S68, S69). The first drawing's mean brightness is 15% or more under the brightness
           0.3 to 0.5 s in, and the rise doesn't fall back (a flicker is the flash check's job).
It reads the frames the preview wrote (out/work/<story>/frames-preview/fNNNNN.png: the raw renders, every 4th
frame from each shot's first), or the proof's or the final's (frames-proof/, frames/), or a film (--film, decoded
by ffmpeg, captions and all). Shot times come from the story's timeline, as framing.py reads them. A shot in
story.json "frames_ok": ["S12"] is skipped: a deliberate blank, pop or slow light-up. It needs no Blender.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
HERE = Path(__file__).resolve().parent
for _p in (str(ROOT), str(HERE)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import measure  # noqa: E402

W, H = 54, 96          # frames are read at this size: enough for a mean, a spread and an 8 x 8 grid
BLANK_TOL = 0.04       # a pixel within this (0..1) of the frame's median colour counts as the same colour...
BLANK_SHARE = 0.95     # ...and a frame this uniform is blank
GRID = 8               # the pop check's grid, GRID x GRID cells
POP_MIN = 0.12         # a cell changing this much (mean abs, 0..1) from the first drawing to the next...
POP_K = 3.0            # ...and this many times the shot's usual change between drawings, is a pop
DARK_RISE = 0.15       # the first drawing this much darker than the shot 0.3 to 0.5 s in...
DARK_AT = (0.3, 0.5)
DARK_HOLD = 0.95       # ...which holds at least this much of that brightness until 0.8 s
DARK_MIN = 0.08        # (a shot darker than this all through is a night shot, not a fade)
EDGE = 4               # frames this close to the film's start or end are its fade in and out (when it has them)


def luma(img: np.ndarray) -> np.ndarray:
    """0..1 brightness of an RGB frame (any dtype)."""
    f = img.astype(np.float32)
    if f.max() > 1.5:
        f /= 255.0
    return 0.2126 * f[..., 0] + 0.7152 * f[..., 1] + 0.0722 * f[..., 2]


def small(img: np.ndarray) -> np.ndarray:
    """An RGB frame (H, W, 3, 0..1) at W x H, by block means (no resampling library needed)."""
    f = img[..., :3].astype(np.float32)
    if f.max() > 1.5:
        f /= 255.0
    h, w = f.shape[:2]
    ys = np.linspace(0, h, H + 1).astype(int)
    xs = np.linspace(0, w, W + 1).astype(int)
    rows = np.add.reduceat(f, ys[:-1], axis=0) / np.diff(ys)[:, None, None]
    return np.add.reduceat(rows, xs[:-1], axis=1) / np.diff(xs)[None, :, None]


def blank(img: np.ndarray) -> tuple[bool, float]:
    """(is it near-uniform, the share of it within BLANK_TOL of its median colour)."""
    med = np.median(img.reshape(-1, 3), axis=0)
    share = float((np.abs(img - med).max(axis=-1) <= BLANK_TOL).mean())
    return share >= BLANK_SHARE, share


def cells(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    """Mean absolute luma change in each GRID x GRID cell between two frames."""
    d = np.abs(luma(a) - luma(b))
    ys = np.linspace(0, d.shape[0], GRID + 1).astype(int)
    xs = np.linspace(0, d.shape[1], GRID + 1).astype(int)
    return np.array([[d[ys[i]:ys[i + 1], xs[j]:xs[j + 1]].mean() for j in range(GRID)] for i in range(GRID)])


def meant(tl: dict, f: int) -> bool:
    """A frame an fx means to be dark, white or noise, or one in the fades at either end."""
    t = f / tl["fps"]
    if (f < EDGE and tl.get("fade_in", True)) or (f >= tl["frames"] - EDGE and tl.get("fade_out", True)):
        return True
    for fx in tl.get("fx", []):
        t0 = fx.get("t", fx.get("start", 0.0))
        if fx.get("kind") in ("black", "flash", "static") and t0 - 0.05 <= t <= t0 + fx.get("dur", 0.4) + 0.05:
            return True
    return False


def lint(frames: dict[int, np.ndarray], tl: dict, ok: set | None = None) -> list[dict]:
    """frames: frame number -> RGB image (any size). Rows as framing.py writes them."""
    ok = ok or set()
    fps = tl["fps"]
    rows = []
    sm = {f: small(im) for f, im in frames.items()}
    for shot in tl["shots"]:
        sid = shot["id"]
        fs = sorted(f for f in sm if shot["f0"] <= f < shot["f1"])
        if sid in ok or not fs:
            continue
        # blank frames, as one row per run
        bl = [f for f in fs if not meant(tl, f) and blank(sm[f])[0]]
        if bl:
            run = [bl[0]]
            for f in bl[1:] + [None]:
                if f is not None and fs.index(f) == fs.index(run[-1]) + 1:
                    run.append(f)
                    continue
                n = len(run)
                rows.append(row(sid, run[0] / fps, (run[-1] + 1) / fps, "blank", f"{n} drawn frame{'s' * (n > 1)} "
                                f"near-uniform (f{run[0]}-f{run[-1]}, {blank(sm[run[0]])[1]:.0%} one colour)"))
                if f is not None:
                    run = [f]
        # a dark opening: the first drawing against 0.3 to 0.5 s in, held to 0.8 s
        dark = False
        mean = {f: float(luma(sm[f]).mean()) for f in fs}
        later = [mean[f] for f in fs if DARK_AT[0] <= (f - shot["f0"]) / fps <= DARK_AT[1]]
        hold = [mean[f] for f in fs if DARK_AT[1] < (f - shot["f0"]) / fps <= 0.8]
        if later and not meant(tl, fs[0]):
            lo, hi = mean[fs[0]], float(np.mean(later))
            if hi >= DARK_MIN and lo <= (1 - DARK_RISE) * hi and all(h >= DARK_HOLD * hi for h in hold):
                dark = True
                rows.append(row(sid, fs[0] / fps, shot["f0"] / fps + DARK_AT[1], "dark",
                                f"opens at {lo:.2f} brightness and rises to {hi:.2f} by {DARK_AT[1]} s: "
                                f"a light fading in after the cut"))
        if len(fs) >= 3 and not dark and not meant(tl, fs[0]):   # (a dark opening pops too: said once)
            # a pop: the first drawing to the next, against the shot's usual change between drawings
            first = cells(sm[fs[0]], sm[fs[1]])
            rest = [cells(sm[a], sm[b]).max() for a, b in zip(fs[1:], fs[2:])]
            usual = float(np.median(rest)) if rest else 0.0
            big = float(first.max())
            if big >= POP_MIN and big >= POP_K * max(usual, 0.01):
                rows.append(row(sid, fs[0] / fps, fs[1] / fps, "pop", f"frame {fs[0] - shot['f0']} to the next drawing: "
                                f"a cell changes {big:.2f} (the shot's usual {usual:.2f}): something pops in"))
    rows.sort(key=lambda r: (r["t0"], r["check"]))
    return rows


def row(shot, a, b, check, detail):
    return {"shot": shot, "t0": round(a, 2), "t1": round(b, 2), "check": check, "detail": detail}


def read_dir(d: Path) -> dict[int, np.ndarray]:
    from PIL import Image
    out = {}
    for p in sorted(d.glob("f*.png")):
        m = re.fullmatch(r"f(\d+)\.png", p.name)
        if m:
            with Image.open(p) as im:
                out[int(m.group(1))] = small(np.asarray(im.convert("RGB")))
    return out


def read_film(path: Path) -> dict[int, np.ndarray]:
    """Every frame of a film at W x H, through ffmpeg (numbered from 0)."""
    raw = subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-i", str(path), "-vf", f"scale={W}:{H}",
                          "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], capture_output=True, check=True).stdout
    a = np.frombuffer(raw, np.uint8).reshape(-1, H, W, 3)
    return {i: a[i].astype(np.float32) / 255.0 for i in range(len(a))}


def table(rows: list[dict]) -> str:
    out = ["| shot | seconds | check | detail |", "|---|---|---|---|"]
    out += [f"| {r['shot']} | {r['t0']:.2f}-{r['t1']:.2f} | {r['check']} | {r['detail']} |" for r in rows]
    return "\n".join(out)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--story", type=Path, required=True)
    ap.add_argument("--frames", type=Path, help="a folder of fNNNNN.png (default: the preview's, then the proof's)")
    ap.add_argument("--film", type=Path, help="read a film instead of a frames folder")
    ap.add_argument("--timeline", type=Path)
    ap.add_argument("--json", type=Path)
    a = ap.parse_args(argv)
    st, tl = measure.load_timeline(a.story, a.timeline)
    work = ROOT / "out" / "work" / a.story.name
    if tl is None and (work / "timeline.json").exists():
        tl = json.loads((work / "timeline.json").read_text())
    if tl is None:
        print(f"{a.story}: no voice-timings.json, no timeline: nothing to check")
        return 0
    if a.film:
        frames, src = read_film(a.film), str(a.film)
    else:
        d = a.frames or next((work / n for n in ("frames-preview", "frames-proof", "frames") if (work / n).is_dir()),
                             None)
        if d is None or not d.is_dir():
            print(f"{a.story}: no frames under {work} (render the preview first): nothing to check")
            return 0
        frames, src = read_dir(d), str(d)
    rows = lint(frames, tl, set(st.get("frames_ok", [])))
    c = {}
    for r in rows:
        c[r["check"]] = c.get(r["check"], 0) + 1
    print(f"# frames: {st.get('name', a.story.name)}: {len(frames)} frames from {src}, {len(rows)} findings {c}")
    if rows:
        print(table(rows))
    if a.json:
        a.json.write_text(json.dumps({"story": st.get("name"), "source": src, "findings": rows, "counts": c},
                                     indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
