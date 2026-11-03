"""Craft metrics for one of our films: the numbers behind "does it look and sound high quality".

    python scripts/measure.py out/ep38-drive-in.mp4 --story stories/ep38-drive-in [--mix mix.json] [--json o.json]
    python scripts/measure.py --story stories/back-row            # no film: the spec metrics only

The methods are in docs/research/craft-metrics.md, and the targets are in TARGETS below (warnings for now). Free
tools only: ffmpeg and numpy. OpenCV is used for optical flow when it's installed and skipped when it isn't.

What it reads:
- the film (picture and sound), decoded by ffmpeg at 108 x 192 for the picture and 48 kHz mono for the sound;
- the story (`story.json` + `voice-timings.json`, or a `timeline.json`): the shots, captions, effects, sound
  effects, acting and camera keys, so cuts, face size and character motion come from the edit itself;
- the mix report (`mix.json` from the film artifact) for the stems' loudness, when it's there.
It prints a markdown table, and `--json` writes every number.
"""

from __future__ import annotations

import argparse
import json
import math
import re
import shutil
import subprocess
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

PW, PH = 108, 192          # the picture is measured at 1/10 size (9:16)
SR = 48000

# Provisional targets: (low, high), either end None. From back-row (our one hit) against ep20, ep38 and knock-back
# (our flops), plus the hit channels' published numbers (docs/research/craft-metrics.md -> "Targets"). They warn
# until the browser study of 20 fast-rising Shorts confirms them; then the confirmed ones block.
TARGETS = {
    # the picture (macro)
    "macro.picture_changes_per_10s": (11, 16),       # skylox study 11-15; ours 6.7-10.4
    "spec.cuts_per_10s": (5.5, 8.0),                 # back-row 5.9; the flops 4.7-5.3
    "spec.shots_over_2s_share": (None, 0.25),        # back-row 0.22; the flops 0.27-0.59
    "spec.shot_p90_s": (None, 2.5),
    "macro.longest_still_s": (None, 1.5),            # the polish pack's own bar
    "macro.motion_energy_mean": (1.5, None),
    "spec.camera_move_share": (0.65, None),          # back-row 0.71; the flops 0.32-0.66
    "spec.punch_per_10s": (0.4, None),               # back-row 0.44; the flops 0.15-0.29
    "macro.brightness_mean": (0.25, None),
    "macro.brightness_first_3s": (0.30, None),       # knock-back 0.10, ep20 0.18: frame 1 is lit
    "macro.dark_frame_share": (None, 0.15),
    "macro.saturation_mean": (0.35, None),
    "macro.contrast_mean": (0.15, None),
    "spec.face_big_share": (0.40, None),             # back-row 0.45; the flops 0.33-0.47
    "spec.caption_share": (0.90, None),
    "spec.caption_words_median": (None, 3),
    # the acting (micro)
    "macro.held_frame_share": (None, 0.15),          # drawn on twos: 34-56% of our frames repeat
    "micro.character_motion_shot_share": (0.50, None),
    "micro.walk_dead_end_share": (None, 0.25),       # every walk starts and stops dead today
    "micro.idle_window_share": (None, 0.30),
    "micro.caption_sync_p90_ms": (None, 120),
    # the sound (micro)
    "spec.sound_events_per_10s": (4.0, None),        # back-row 3.4, the flops 1.2-3.3; the polish pack adds about 4
    "sound.silence_share": (None, 0.005),
    "sound.voice_bed_gap_db": (8.0, 14.0),
    "sound.lufs": (-15.0, -13.0),
    "sound.true_peak_dbtp": (None, -1.0),
    "sound.hf_share_max_5s": (None, 0.08),
    "sound.hf_jump_max": (None, 0.04),
}


# ---------- reading ----------

def probe(path: Path) -> dict:
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "stream=codec_type,width,height,r_frame_rate:"
                          "format=duration", "-of", "json", str(path)], capture_output=True, text=True, check=True)
    d = json.loads(out.stdout)
    v = next((s for s in d["streams"] if s["codec_type"] == "video"), None)
    a, b = (v["r_frame_rate"].split("/") if v else ("30", "1"))
    return {"duration": float(d["format"]["duration"]), "fps": float(a) / float(b),
            "width": v and v["width"], "height": v and v["height"],
            "audio": any(s["codec_type"] == "audio" for s in d["streams"])}


def read_frames(path: Path) -> np.ndarray:
    """Every frame at PW x PH, RGB in 0..1 (float32). About 250 KB a frame, so a 2:30 film is about 1 GB."""
    raw = subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-i", str(path), "-vf", f"scale={PW}:{PH}:flags=area",
                          "-pix_fmt", "rgb24", "-f", "rawvideo", "-"], capture_output=True, check=True).stdout
    a = np.frombuffer(raw, np.uint8).reshape(-1, PH, PW, 3)
    return a


def read_audio(path: Path) -> np.ndarray:
    raw = subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-i", str(path), "-vn", "-ac", "1", "-ar", str(SR),
                          "-f", "f32le", "-"], capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.float32).copy()


def ebur128(path: Path) -> dict:
    p = subprocess.run(["ffmpeg", "-nostdin", "-hide_banner", "-i", str(path), "-vn", "-af", "ebur128=peak=true",
                        "-f", "null", "-"], capture_output=True, text=True)
    s = p.stderr[p.stderr.rfind("Summary:"):]
    get = lambda k: (lambda m: float(m.group(1)) if m else None)(re.search(k + r":\s*(-?[\d.]+|-inf)", s))
    return {"lufs": get("I"), "lra": get("LRA"), "true_peak_dbtp": get("Peak")}


def load_timeline(story: Path | None, timeline: Path | None) -> tuple[dict | None, dict | None]:
    st = tl = None
    if story:
        st = json.loads((story / "story.json").read_text())
        st.setdefault("name", story.name)
    if timeline:
        tl = json.loads(timeline.read_text())
    elif story and (story / "voice-timings.json").exists():
        from blocky import timeline as T
        tl = T.build(st, json.loads((story / "voice-timings.json").read_text()))
    return st, tl


# ---------- picture ----------

def luma(f: np.ndarray) -> np.ndarray:
    f = f.astype(np.float32) / 255.0
    return f[..., 0] * 0.2126 + f[..., 1] * 0.7152 + f[..., 2] * 0.0722


def phase_shift(a: np.ndarray, b: np.ndarray) -> tuple[float, float]:
    """The global translation from a to b in pixels (phase correlation), with a Hann window."""
    w = np.outer(np.hanning(a.shape[0]), np.hanning(a.shape[1]))
    A, B = np.fft.fft2((a - a.mean()) * w), np.fft.fft2((b - b.mean()) * w)
    r = A * np.conj(B)
    r /= np.abs(r) + 1e-9
    c = np.fft.ifft2(r).real
    y, x = np.unravel_index(np.argmax(c), c.shape)
    if y > a.shape[0] // 2:
        y -= a.shape[0]
    if x > a.shape[1] // 2:
        x -= a.shape[1]
    # a parabola through the peak's neighbours for sub-pixel precision
    def sub(m, p0, n):
        l, r_ = m[(p0 - 1) % n], m[(p0 + 1) % n]
        d = l - 2 * m[p0 % n] + r_
        return 0.0 if abs(d) < 1e-12 else 0.5 * (l - r_) / d
    yy, xx = np.unravel_index(np.argmax(c), c.shape)
    return float(x + sub(c[yy], xx, c.shape[1])), float(y + sub(c[:, xx], yy, c.shape[0]))


def runs(mask: np.ndarray) -> list[tuple[int, int]]:
    """(start, length) of each run of True."""
    out, i, n = [], 0, len(mask)
    while i < n:
        if mask[i]:
            j = i
            while j < n and mask[j]:
                j += 1
            out.append((i, j - i))
            i = j
        else:
            i += 1
    return out


def picture(frames: np.ndarray, fps: float) -> dict:
    n = len(frames)
    Y = np.stack([luma(f) for f in frames])
    dur = n / fps
    d1 = np.r_[0, np.abs(np.diff(Y, axis=0)).mean(axis=(1, 2))]            # frame-to-frame change
    d2 = np.r_[0, 0, np.abs(Y[2:] - Y[:-2]).mean(axis=(1, 2))]             # over two frames (our 15 fps shots)
    hist = np.stack([np.histogram(y, 32, (0, 1))[0] / y.size for y in Y])
    dh = np.r_[0, np.abs(np.diff(hist, axis=0)).sum(axis=1)]
    # a cut: a big jump against the frames around it. Flashes and dips to black count once, as a transition.
    local = np.array([np.median(d1[max(0, i - 8):i + 8]) for i in range(n)])
    cut = (d1 > np.maximum(0.045, 4 * local)) & (dh > 0.25)
    cut[:int(0.2 * fps)] = False          # the fade up and the last frames aren't cuts
    cut[n - int(0.2 * fps):] = False
    for i in np.nonzero(cut)[0]:          # one cut per 4 frames at most
        cut[i + 1:i + 4] = False
    cuts = np.nonzero(cut)[0]
    shots = np.diff(np.r_[0, cuts, n]) / fps

    # the browser protocol's picture change: samples 0.5 s apart on a 18 x 32 grid, mean change over 4%
    g = _grid(Y)
    step = max(1, int(round(fps * 0.5)))
    idx = np.arange(0, n, step)
    ch = np.abs(np.diff(g[idx], axis=0)).mean(axis=(1, 2)) > 0.04
    changes_10s = float(ch.sum() / max(1e-9, (len(idx) - 1) * 0.5) * 10)
    step4 = max(1, int(round(fps * 0.25)))
    idx4 = np.arange(0, n, step4)
    dq = np.abs(np.diff(g[idx4], axis=0)).mean(axis=(1, 2))
    ch4 = dq > 0.04
    still_q = max([l for _, l in runs(dq < 0.006)], default=0) * step4 / fps

    # camera motion: the global shift between frames two apart (skips the repeated frames of a 15 fps shot)
    shift = np.zeros(n)
    for i in range(2, n, 2):
        if cut[i - 1] or cut[i]:
            continue
        dx, dy = phase_shift(Y[i - 2], Y[i])
        shift[i] = shift[i - 1] = math.hypot(dx, dy) / 2       # pixels per frame at 108 wide
    flow = None
    try:
        import cv2
        mags = []
        for i in range(3, n, 3):
            if cut[i - 2:i + 1].any():
                continue
            f = cv2.calcOpticalFlowFarneback((Y[i - 2] * 255).astype(np.uint8), (Y[i] * 255).astype(np.uint8),
                                             None, 0.5, 2, 9, 2, 5, 1.1, 0)
            mags.append(float(np.linalg.norm(f, axis=2).mean() / 2))
        flow = float(np.mean(mags)) * 10 if mags else 0.0   # px per frame at full width (1080)
    except ImportError:
        pass
    moving = shift > 0.04            # 0.4 px per frame at 1080 wide: anything a viewer reads as a move
    # motion energy: the mean frame change (percent of full scale), per second
    sec = int(dur)
    energy = np.array([d2[int(s * fps):int((s + 1) * fps)].mean() for s in range(max(1, sec))]) * 100
    # still: under 0.35% change over two frames, no global shift, no cut
    still = (d2 < 0.0035) & ~moving & ~cut
    longest_still = max([l for _, l in runs(still)], default=0) / fps
    held = (d1 < 0.0015) & ~cut
    # colour
    sat, con, bri = [], [], []
    for f, y in zip(frames[::3], Y[::3]):
        x = f.astype(np.float32) / 255
        mx, mn = x.max(axis=2), x.min(axis=2)
        lit = mx > 0.04
        sat.append(float(((mx - mn)[lit] / mx[lit]).mean()) if lit.any() else 0.0)
        con.append(float(y.std()))
        bri.append(float(y.mean()))
    bri = np.array(bri)
    black = Y.mean(axis=(1, 2)) < 0.03
    dips = [r for r in runs(black) if r[0] > 0 and r[0] + r[1] < n]
    return {
        "duration_s": round(dur, 2),
        "cuts": int(len(cuts)),
        "cuts_per_10s": round(len(cuts) / dur * 10, 2),
        "shot_median_s": round(float(np.median(shots)), 2),
        "shot_p90_s": round(float(np.percentile(shots, 90)), 2),
        "shot_max_s": round(float(shots.max()), 2),
        "cut_times": [round(i / fps, 2) for i in cuts],
        "picture_changes_per_10s": round(changes_10s, 1),
        "picture_changes_per_10s_q": round(float(ch4.sum() / max(1e-9, (len(idx4) - 1) * 0.25) * 10), 1),
        "motion_energy_q": round(float(dq.mean()) * 100, 2),
        "longest_still_q_s": round(still_q, 2),
        "camera_motion_share": round(float(moving.mean()), 3),
        "camera_shift_px_per_frame": round(float(np.median(shift[moving])) * 10, 2) if moving.any() else 0.0,
        "flow_mean_px_per_frame": None if flow is None else round(flow, 2),
        "motion_energy_mean": round(float(energy.mean()), 2),
        "motion_energy_p10": round(float(np.percentile(energy, 10)), 2),
        "motion_energy_per_s": [round(float(e), 2) for e in energy],
        "longest_still_s": round(longest_still, 2),
        "stills_over_2s": int(sum(1 for _, l in runs(still) if l / fps > 2)),
        "held_frame_share": round(float(held.mean()), 3),
        "brightness_mean": round(float(bri.mean()), 3),
        "brightness_first_3s": round(float(Y[:int(3 * fps)].mean()), 3),
        "dark_frame_share": round(float((bri < 0.12).mean()), 3),
        "saturation_mean": round(float(np.mean(sat)), 3),
        "contrast_mean": round(float(np.mean(con)), 3),
        "black_dips": len(dips),
    }


def _grid(Y: np.ndarray) -> np.ndarray:
    """Each frame as an 18 x 32 grid (rows x columns of a portrait frame: 32 tall, 18 wide)."""
    n, h, w = Y.shape
    gh, gw = 32, 18
    hh, ww = h // gh * gh, w // gw * gw
    return Y[:, :hh, :ww].reshape(n, gh, hh // gh, gw, ww // gw).mean(axis=(2, 4))


# ---------- sound ----------

def _stft_mag(x: np.ndarray, win: int = 1024, hop: int = 512) -> np.ndarray:
    if len(x) < win:
        x = np.pad(x, (0, win - len(x)))
    n = 1 + (len(x) - win) // hop
    idx = np.arange(win)[None, :] + hop * np.arange(n)[:, None]
    return np.abs(np.fft.rfft(x[idx] * np.hanning(win), axis=1))


def onsets(x: np.ndarray) -> np.ndarray:
    """Onset times (s): peaks in the log spectral flux over a moving median, at least 80 ms apart."""
    hop = 512
    M = np.log1p(_stft_mag(x, 1024, hop) * 10)
    flux = np.r_[0, np.maximum(0, np.diff(M, axis=0)).sum(axis=1)]
    fr = SR / hop
    w = int(fr)               # a 2 s window for the threshold
    out = []
    last = -1e9
    for i in range(1, len(flux) - 1):
        if flux[i] < flux[i - 1] or flux[i] < flux[i + 1]:
            continue
        seg = flux[max(0, i - w):i + w]
        med = np.median(seg)
        mad = np.median(np.abs(seg - med)) + 1e-9
        if flux[i] > med + 6 * mad and i / fr - last >= 0.08:
            out.append(i / fr)
            last = i / fr
    return np.array(out)


def rms_db(x: np.ndarray, win: float) -> np.ndarray:
    n = int(SR * win)
    m = len(x) // n
    if m == 0:
        return np.array([-120.0])
    r = np.sqrt((x[:m * n].reshape(m, n) ** 2).mean(axis=1))
    return 20 * np.log10(r + 1e-10)


def sound(x: np.ndarray, tl: dict | None, mix: dict | None, loud: dict) -> dict:
    dur = len(x) / SR
    out = dict(loud)
    db50 = rms_db(x, 0.05)
    sil = db50 < -60
    out["silence_share"] = round(float(sil.mean()), 4)
    out["longest_silence_s"] = round(max([l for _, l in runs(sil)], default=0) * 0.05, 2)
    # high frequencies: share of energy above 4 kHz in 5 s windows
    M = _stft_mag(x, 2048, 1024) ** 2
    freqs = np.fft.rfftfreq(2048, 1 / SR)
    hi = M[:, freqs >= 4000].sum(axis=1)
    tot = M.sum(axis=1) + 1e-12
    per = int(5 * SR / 1024)
    wins = [hi[i:i + per].sum() / tot[i:i + per].sum() for i in range(0, len(hi) - per // 2, per)]
    out["hf_share"] = round(float(hi.sum() / tot.sum()), 4)
    out["hf_share_max_5s"] = round(float(max(wins)), 4) if wins else 0.0
    out["hf_jump_max"] = round(float(np.max(np.abs(np.diff(wins)))), 4) if len(wins) > 1 else 0.0
    on = onsets(x)
    out["onsets_per_10s"] = round(len(on) / dur * 10, 2)
    if tl:
        spans = [(p["onset"] - 0.06, p["end"] + 0.06) for p in tl["lines"].values() if p.get("who") != "pause"]
        inv = lambda t: any(a <= t <= b for a, b in spans)
        free = [t for t in on if not inv(t)]
        voice_time = sum(min(b, dur) - max(a, 0) for a, b in spans)
        out["sfx_onsets_per_10s"] = round(len(free) / max(1e-9, dur) * 10, 2)
        out["sfx_onsets_per_10s_unvoiced"] = round(len(free) / max(1e-9, dur - voice_time) * 10, 2)
        # voice to bed: 50 ms windows inside lines against those in the gaps (0.15 s in from each edge)
        t50 = (np.arange(len(db50)) + 0.5) * 0.05
        voice = np.array([inv(t) for t in t50])
        gaps = []
        for (a0, b0), (a1, b1) in zip(sorted(spans), sorted(spans)[1:]):
            if a1 - b0 > 0.3:
                gaps.append((b0 + 0.15, a1 - 0.15))
        gap = np.array([any(a <= t <= b for a, b in gaps) for t in t50])
        if voice.any() and gap.any():
            out["voice_bed_gap_audio_db"] = round(float(np.percentile(db50[voice], 75) - np.median(db50[gap & ~sil])), 1) \
                if (gap & ~sil).any() else None
        out["caption_sync"] = sync(x, tl)
    else:
        out["sfx_onsets_per_10s"] = out["onsets_per_10s"]
    if mix and mix.get("stems_lufs"):
        s = mix["stems_lufs"]
        bed = [s[k] for k in ("music", "amb") if s.get(k) is not None]
        if bed and s.get("voice") is not None:
            out["voice_bed_gap_stems_db"] = round(s["voice"] - 10 * math.log10(sum(10 ** (b / 10) for b in bed)), 1)
    # the stems' number when there's a mix report (exact); else the film's lines against its gaps (rougher)
    out["voice_bed_gap_db"] = out.get("voice_bed_gap_stems_db", out.get("voice_bed_gap_audio_db"))
    return out


def sync(x: np.ndarray, tl: dict) -> dict:
    """How far each caption (and each mouth flap) lands from the voice's real onset under it, in ms."""
    env = rms_db(x, 0.005)
    def onset_near(t):
        i0, i1 = int((t - 0.15) / 0.005), int((t + 0.25) / 0.005)
        if i0 < 20 or i1 >= len(env):
            return None
        floor = np.percentile(env[max(0, i0 - 40):i0 + 1], 20)
        seg = env[i0:i1]
        k = np.nonzero(seg > floor + 12)[0]
        return None if not len(k) else (i0 + k[0]) * 0.005
    offs, flap = [], []
    firsts = {p["chunks"][0][0] for p in tl["lines"].values() if p.get("who") != "pause" and p["chunks"]}
    for c in tl["captions"]:
        # only a line's first caption: it starts after a gap, so the voice onset under it is clean to find
        if c.get("big") or not any(abs(c["start"] + 0.04 - f) < 1e-3 for f in firsts):
            continue
        o = onset_near(c["start"] + 0.04)
        if o is not None:
            offs.append((o - (c["start"] + 0.04)) * 1000)
    for who, fl in tl.get("talk", {}).items():
        for a, _ in fl:
            o = onset_near(a)
            if o is not None:
                flap.append((o - a) * 1000)
    q = lambda v, p: round(float(np.percentile(np.abs(v), p)), 0) if v else None
    return {"captions": len(offs), "caption_median_ms": round(float(np.median(offs)), 0) if offs else None,
            "caption_p90_ms": q(offs, 90), "flaps": len(flap),
            "flap_median_ms": round(float(np.median(flap)), 0) if flap else None, "flap_p90_ms": q(flap, 90)}


# ---------- the edit (story.json + timeline) ----------

def _ease(u):
    u = min(1.0, max(0.0, u))
    return u * u * (3 - 2 * u)


def cam_at(spec: dict, shot: dict, t: float, tl: dict):
    """The camera at t as bl_story.cam_at places it, without the handheld drift (a steady reading)."""
    from blocky import acting
    keys = spec["cam"]
    u = (t - shot["start"]) / max(1e-6, shot["end"] - shot["start"])
    lerp = lambda a, b, v: tuple(x + (y - x) * v for x, y in zip(a, b))
    if u <= keys[0][0] or len(keys) == 1:
        k = keys[0]
        loc, tgt, lens = tuple(k[1]), tuple(k[2]), k[3]
    else:
        loc = None
        for a, b in zip(keys, keys[1:]):
            if u <= b[0]:
                v = _ease((u - a[0]) / max(1e-6, b[0] - a[0]))
                loc, tgt, lens = lerp(a[1], b[1], v), lerp(a[2], b[2], v), a[3] + (b[3] - a[3]) * v
                break
        if loc is None:
            k = keys[-1]
            loc, tgt, lens = tuple(k[1]), tuple(k[2]), k[3]
    if spec.get("follow") and spec["follow"] in tl["acting"]:
        s = acting.state(tl, spec["follow"], t)
        loc = (loc[0] + s["x"], loc[1] + s["y"], loc[2] + s["z"])
        tgt = (tgt[0] + s["x"], tgt[1] + s["y"], tgt[2] + s["z"])
    return np.array(loc, float), np.array(tgt, float), float(lens)


def project(loc, tgt, lens, p, zoom=1.0):
    """(x, y, width-per-metre) of point p in the frame, -1..1 across; None behind the camera. Blender's camera:
    vertical sensor fit, 24 mm tall, 1080 x 1920."""
    f = tgt - loc
    f /= np.linalg.norm(f) + 1e-9
    r = np.cross(f, [0, 0, 1.0])
    if np.linalg.norm(r) < 1e-6:
        r = np.array([1.0, 0, 0])
    r /= np.linalg.norm(r)
    u = np.cross(r, f)
    d = p - loc
    z = float(d @ f)
    if z <= 0.05:
        return None
    half_h = z * 12.0 / lens / zoom
    half_w = half_h * 1080 / 1920
    return float(d @ r) / half_w, float(d @ u) / half_h, 1.0 / (2 * half_w)


def edit(st: dict, tl: dict) -> dict:
    from blocky import acting
    fps, dur = tl["fps"], tl["duration"]
    shots = tl["shots"]
    lens_ = np.array([s["end"] - s["start"] for s in shots])
    specs = {s["id"]: s for s in st["shots"]}
    out = {"duration_s": round(dur, 2), "shots": len(shots), "cuts_per_10s": round((len(shots) - 1) / dur * 10, 2),
           "shot_median_s": round(float(np.median(lens_)), 2), "shot_p90_s": round(float(np.percentile(lens_, 90)), 2),
           "shot_max_s": round(float(lens_.max()), 2),
           "shots_over_2s_share": round(float((lens_ > 2.0).mean()), 3),
           "time_in_shots_over_2s_share": round(float(lens_[lens_ > 2.0].sum() / dur), 3),
           "step2_frame_share": round(sum((s["f1"] - s["f0"]) for s in shots if s["step"] >= 2) / tl["frames"], 3)}
    # transitions: hard cuts plus each effect kind, and the fades
    kinds = {}
    for f in tl["fx"]:
        kinds[f["kind"]] = kinds.get(f["kind"], 0) + 1
    out["transitions"] = {"cut": len(shots) - 1, **kinds, "fade_in": bool(tl.get("fade_in", True)),
                          "fade_out": bool(tl.get("fade_out", True)) and tl.get("tail", 0.9) > 0}
    from blocky import polish, timeline as T
    at = T.resolver(tl["lines"], dur)
    pol = polish.spec(st)
    emph, pev = [], []
    if pol:
        emph = polish.emph_times(tl, pol, at)
        pev = polish.sound_events(tl, st, pol, at)
        out["transitions"]["polish_punch"] = len(emph)
        out["transitions"]["polish_whoosh"] = sum(1 for e in pev if "whoosh" in e["kind"])
    out["polish"] = bool(pol)
    out["punch_per_10s"] = round((kinds.get("punch", 0) + len(emph)) / dur * 10, 2)
    # captions
    caps = [c for c in tl["captions"]]
    iv = sorted((c["start"], c["end"]) for c in caps)
    cover, cur = 0.0, None
    for a, b in iv:
        if cur is None or a > cur[1]:
            if cur:
                cover += cur[1] - cur[0]
            cur = [a, b]
        else:
            cur[1] = max(cur[1], b)
    if cur:
        cover += cur[1] - cur[0]
    words = [len(c["text"].split()) for c in caps if not c.get("big")]
    out["caption_share"] = round(cover / dur, 3)
    out["captions"] = len(caps)
    out["caption_words_mean"] = round(float(np.mean(words)), 2) if words else 0
    out["caption_words_median"] = float(np.median(words)) if words else 0
    out["caption_words_max"] = int(max(words, default=0))
    try:
        from blocky import post
        hs = [post.caption_image(c["text"], False)[0].size[1] for c in caps[:60] if not c.get("big")]
        b = post.font(post.CAP_PX).getbbox("H")
        out["caption_px"] = post.CAP_PX
        out["caption_letter_share"] = round((b[3] - b[1]) / post.H, 3)      # a capital's height / frame height
        out["caption_block_share"] = round(float(np.median(hs)) / post.H, 3) if hs else None
    except Exception:    # no PIL or fonts: the size is skipped
        pass
    out["sfx"] = len(st.get("sound", {}).get("sfx", [])) + len(pev)
    out["polish_sounds"] = len(pev)
    out["sfx_per_10s"] = round(out["sfx"] / dur * 10, 2)
    cast = {k: v for k, v in st.get("cast", {}).items() if not v.get("offscreen")}
    steps = sum(len(acting.footsteps(tl, w)) for w in cast)
    out["footsteps_per_10s"] = round(steps / dur * 10, 2)
    # a walk's footsteps are one event to the ear: a burst per walk of 2 steps or more
    bursts = 0
    for w in cast:
        fs = [f["t"] for f in acting.footsteps(tl, w)]
        bursts += sum(1 for i, t in enumerate(fs) if i + 1 < len(fs) and (i == 0 or t - fs[i - 1] > 0.8))
    out["sound_events_per_10s"] = round((out["sfx"] + bursts) / dur * 10, 2)
    out["ambience_beds"] = len(st.get("sound", {}).get("ambience", []))
    out["music_drops"] = len(st.get("sound", {}).get("music_drops", []))

    # camera, faces and characters, sampled at 10 per second
    try:
        from blocky import post
        fxz = lambda t: post.fx_at(tl, t)["punch"]
    except Exception:
        fxz = lambda t: 1.0

    def zoom_at(t):   # the effects' punch-in times the polish pack's crop move (zoom, plus its slide as zoom-equivalent)
        if not pol:
            return fxz(t)
        z, dx, dy = polish.motion(tl, st, pol, t, emph)
        return fxz(t) * z + abs(dx) + abs(dy)
    dt = 0.1
    ts = np.arange(0, dur, dt)
    face_big, cam_move, idle, any_vis = [], [], [], []
    shot_moves = {s["id"]: False for s in shots}
    prev = {}
    prev_cam = None
    last_shot = None
    for t in ts:
        shot = next((s for s in shots if s["start"] <= t < s["end"]), shots[-1])
        spec = specs.get(shot["id"], {})
        if "cam" not in spec:
            continue
        loc, tgt, lens = cam_at(spec, shot, t, tl)
        z = zoom_at(t)
        if prev_cam is not None and last_shot == shot["id"]:
            pl, pt, plen, pz = prev_cam
            fwd0, fwd1 = pt - pl, tgt - loc
            ang = math.degrees(math.acos(np.clip(fwd0 @ fwd1 / (np.linalg.norm(fwd0) * np.linalg.norm(fwd1) + 1e-9),
                                                 -1, 1)))
            mv = np.linalg.norm(loc - pl) / dt > 0.03 or ang / dt > 1.0 or abs(lens - plen) / dt > 0.3 \
                or abs(z - pz) / dt > 0.02
            cam_move.append(bool(mv))
        prev_cam, last_shot = (loc, tgt, lens, z), shot["id"]
        big, vis, still = False, False, True
        for name, spec_c in cast.items():
            s = acting.state(tl, name, t)
            if s["hidden"]:
                continue
            h = spec_c.get("height", 1.0)
            p = project(loc, tgt, lens, np.array([s["x"], s["y"], s["z"] + 1.5 * h]), z)
            if p is None or abs(p[0]) > 1.05 or abs(p[1]) > 1.05:
                prev.pop(name, None)
                continue
            vis = True
            if 2 * 0.21 * h * p[2] >= 0.2:
                big = True
            pose = np.array([s["x"], s["y"], s["z"], s["yaw"], *s["arms"], *s["arms_side"], s["head_yaw"],
                             s["head_pitch"], s["lean"], s["legs"], s["mouth"]])
            if name in prev and np.abs(pose - prev[name]).max() > 0.01:
                still = False
                shot_moves[shot["id"]] = True
            prev[name] = pose
        face_big.append(big)
        any_vis.append(vis)
        idle.append(vis and still)
    out["face_big_share"] = round(float(np.mean(face_big)), 3) if face_big else 0.0
    out["face_big_first_3s"] = bool(any(face_big[:30]))
    out["camera_move_share"] = round(float(np.mean(cam_move)), 3) if cam_move else 0.0
    vis_shots = [s["id"] for s in shots]
    out["character_motion_shot_share"] = round(sum(shot_moves.values()) / max(1, len(vis_shots)), 3)
    # idle: 1 s windows where someone is on screen and nobody moves at all (blinks don't count)
    idle = np.array(idle)
    w = int(1 / dt)
    wins = [idle[i:i + w].all() for i in range(0, len(idle) - w + 1, w) if np.array(any_vis[i:i + w]).any()]
    out["idle_window_share"] = round(float(np.mean(wins)), 3) if wins else 0.0

    # easing: acting.position moves at a constant speed between two pos keys, so a walk that doesn't continue
    # from a key moving the same way starts or stops dead in one frame (an acceleration spike). Count those.
    jerks, walk_s, walks = 0, 0.0, 0
    for name in cast:
        keys = [k for k in tl["acting"].get(name, []) if "pos" in k]
        vel = []
        for a, b in zip(keys, keys[1:]):
            d = np.subtract(b["pos"][:2], a["pos"][:2])
            dur_ = b["t"] - a["t"]
            vel.append((a["t"], b["t"], d / dur_ if dur_ > 1e-6 else None))
        for i, (t0, t1, v) in enumerate(vel):
            if v is None or np.linalg.norm(v) < 0.3 or np.linalg.norm(v) * (t1 - t0) < 0.05 or t1 - t0 > 600:
                continue
            walk_s += t1 - t0
            walks += 1
            for j in (i - 1, i + 1):
                w = vel[j][2] if 0 <= j < len(vel) else np.zeros(2)
                if w is None:
                    w = np.zeros(2)
                if np.linalg.norm(v - w) > 0.5:      # a change over 0.5 m/s in one frame: about 15 m/s2
                    jerks += 1
    out["walk_s"] = round(walk_s, 1)
    out["walks"] = walks
    out["walk_dead_ends"] = jerks
    out["walk_dead_end_share"] = round(jerks / (2 * walks), 3) if walks else 0.0
    # camera stops inside a shot: a key between two moving segments (smoothstep stops dead at every key)
    stops = 0
    for s in st["shots"]:
        k = s["cam"]
        for a, b, c in zip(k, k[1:], k[2:]):
            m1 = np.linalg.norm(np.subtract(b[1], a[1])) > 0.02 or np.linalg.norm(np.subtract(b[2], a[2])) > 0.02
            m2 = np.linalg.norm(np.subtract(c[1], b[1])) > 0.02 or np.linalg.norm(np.subtract(c[2], b[2])) > 0.02
            stops += bool(m1 and m2)
    out["camera_midshot_stops"] = stops
    # secondary motion: pose keys that aren't a walk (head, arms, lean, tremble, look) per minute of film
    sec = sum(1 for keys in st.get("acting", {}).values() for k in keys
              if any(a in k for a in ("head", "arms", "side", "lean", "tremble", "look")))
    out["secondary_keys_per_min"] = round(sec / dur * 60, 1)
    out["talk_flaps"] = sum(len(v) for v in tl.get("talk", {}).values())
    return out


# ---------- the report ----------

def measure(film: Path | None, story: Path | None = None, timeline: Path | None = None,
            mix: Path | None = None) -> dict:
    st, tl = load_timeline(story, timeline)
    res = {"film": str(film) if film else None, "story": st and st.get("name")}
    mixd = json.loads(mix.read_text()) if mix and mix.exists() else None
    if film:
        info = probe(film)
        res["probe"] = info
        res["macro"] = picture(read_frames(film), info["fps"])
        if info["audio"]:
            res["sound"] = sound(read_audio(film), tl, mixd, ebur128(film))
    if st and tl:
        res["spec"] = edit(st, tl)
        if film and abs(res["spec"]["duration_s"] - res["probe"]["duration"]) > 0.25:
            res["warning"] = (f"the story's timeline runs {res['spec']['duration_s']} s but the film runs "
                              f"{res['probe']['duration']:.2f} s: the spec has changed since this film was drawn")
    res["micro"] = micro(res)
    res["checks"] = check(res)
    return res


def micro(res: dict) -> dict:
    sp, so = res.get("spec", {}), res.get("sound", {})
    m = {k: sp[k] for k in ("character_motion_shot_share", "walk_dead_end_share", "camera_midshot_stops",
                            "secondary_keys_per_min", "idle_window_share", "talk_flaps") if k in sp}
    cs = so.get("caption_sync") or {}
    if cs.get("caption_p90_ms") is not None:
        m["caption_sync_p90_ms"] = cs["caption_p90_ms"]
    if cs.get("flap_p90_ms") is not None:
        m["flap_sync_p90_ms"] = cs["flap_p90_ms"]
    return m


def value(res: dict, key: str):
    sect, k = key.split(".", 1)
    v = res.get(sect, {}).get(k)
    if v is None and sect == "macro":          # no film: the edit's own number stands in where there is one
        v = res.get("spec", {}).get({"camera_motion_share": "camera_move_share"}.get(k, k))
    return v


def check(res: dict) -> list[dict]:
    out = []
    for key, (lo, hi) in TARGETS.items():
        v = value(res, key)
        if v is None:
            continue
        ok = (lo is None or v >= lo) and (hi is None or v <= hi)
        out.append({"metric": key, "value": v, "low": lo, "high": hi, "status": "ok" if ok else "warn"})
    return out


def table(res: dict) -> str:
    rows = [f"**{res.get('story') or res.get('film')}**" + (f"  ⚠ {res['warning']}" if res.get("warning") else ""),
            "", "| metric | value | target | |", "|---|---|---|---|"]
    for c in res["checks"]:
        rng = f"{'' if c['low'] is None else c['low']}–{'' if c['high'] is None else c['high']}"
        rows.append(f"| {c['metric']} | {c['value']} | {rng} | {'ok' if c['status'] == 'ok' else '**warn**'} |")
    warns = sum(c["status"] != "ok" for c in res["checks"])
    rows.append(f"\n{warns} of {len(res['checks'])} outside the provisional targets (warnings, not blocks).")
    return "\n".join(rows)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("film", nargs="?", type=Path, help="the mp4 (omit for the spec metrics only)")
    ap.add_argument("--story", type=Path, help="stories/<name> (story.json + voice-timings.json)")
    ap.add_argument("--timeline", type=Path, help="a timeline.json, instead of building one from --story")
    ap.add_argument("--mix", type=Path, help="mix.json from the film artifact (stem loudness)")
    ap.add_argument("--json", type=Path, help="write every number here")
    a = ap.parse_args(argv)
    if not a.film and not a.story:
        ap.error("give a film, a story, or both")
    if a.film and not shutil.which("ffmpeg"):
        ap.error("ffmpeg isn't installed")
    res = measure(a.film, a.story, a.timeline, a.mix)
    if a.json:
        a.json.parent.mkdir(parents=True, exist_ok=True)
        a.json.write_text(json.dumps(res, indent=1))
    print(table(res))
    return 0


if __name__ == "__main__":
    sys.exit(main())
