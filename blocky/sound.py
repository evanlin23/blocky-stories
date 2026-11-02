"""The soundtrack for one blocky story, all synthesized (no samples, no borrowed melody):

- the narrator: the sped-up Kokoro lines (voice.py), each placed where the timeline puts it
- the score: generated per story from its `music` spec (a key, a mode, a tempo and which voices play in each
  section), with a seeded random walk over chord tones, so it's nobody's tune and no two stories share one
- ambience: wind, hum, rain, room tone, drips, crickets, water or a low drone, each between two time refs
- footsteps on every step the acting takes (acting.footsteps), on the story's floor
- one-off sounds at time refs (`sfx`): hits, risers, creaks, door slams, knocks (a "pattern" of hit times and a
  "tone": below, hand, glass, soft, glass_soft), whooshes, glitches, bells, thuds, wet clicks, bubbles (an applause
  wash, or tinybubbles), a pop, squeaks and squeals (skin on acrylic), a glide, a hum sweep, castors, and (ep17,
  opt-in) a packing-tape peel (`tape`), cardboard dragged on boards (`scrape`, "distant": through a wall) and a
  papery cardboard flex (`creak` with "tone": "cardboard"; the default creak is unchanged)
- the score can be heard through something: `music.filter` keys [{"at", "hz", "dur"}] move a low-pass over it

Balance before the master: narrator -16 LUFS over its lines, music -27 under the voice and -21 where nobody
talks, ambience at its own level. A `music_drops` hole takes everything except the voice (and any sound effect
marked `keep`, or of a kind the drop keeps) down 40 dB (or a drop's own `db`). Master: mixer.master() to -14 LUFS with the true
peak at -2.0 dBTP, so the AAC file stays at or below -1.5.
"""

from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np

from blocky import synth
from blocky.mixer import Mix, loudness, master
from blocky.synth import SR, fft_filter

from blocky import acting
from blocky.timeline import resolver

SPEECH = -16.0
DROP_DB = -40.0       # a music drop: the music, ambience, steps and sound effects fall this far (the voice doesn't)
TP_CEILING = -2.0     # the master's true peak; AAC adds about 0.3 dB, so the file lands at -1.5 dBTP or lower
MUSIC_UNDER = -27.0
MUSIC_FREE = -21.0
MODES = {"minor": [0, 2, 3, 5, 7, 8, 10], "phrygian": [0, 1, 3, 5, 7, 8, 10], "dorian": [0, 2, 3, 5, 7, 9, 10],
         "harmonic": [0, 2, 3, 5, 7, 8, 11], "locrian": [0, 1, 3, 5, 6, 8, 10], "major": [0, 2, 4, 5, 7, 9, 11],
         "whole": [0, 2, 4, 6, 8, 10]}


def load_wav(path: Path) -> np.ndarray:
    import wave

    with wave.open(str(path)) as w:
        n, ch, sw, sr = w.getnframes(), w.getnchannels(), w.getsampwidth(), w.getframerate()
        raw = w.readframes(n)
    if sw == 2:
        a = np.frombuffer(raw, "<i2").astype(np.float64) / 32768
    elif sw == 4:
        a = np.frombuffer(raw, "<i4") / 2**31
    else:
        raise ValueError(f"{path}: {sw}-byte samples")
    a = a.reshape(-1, ch).mean(axis=1)
    if sr != SR:
        m = int(round(len(a) * SR / sr))
        X = np.fft.rfft(a)
        Y = np.zeros(m // 2 + 1, complex)
        k = min(len(X), len(Y))
        Y[:k] = X[:k]
        a = np.fft.irfft(Y, m) * (m / len(a))
    return a


def lufs(x: np.ndarray, spans=None) -> float:
    if spans:
        parts = [x[max(0, int(a * SR)):int(b * SR)] for a, b in spans if b > a]
        x = np.concatenate(parts) if parts else x
    return float(loudness(x if x.ndim == 2 else np.stack([x, x], 1)))


def to_lufs(x, target, spans=None):
    l = lufs(x, spans)
    return x if not np.isfinite(l) else x * 10 ** ((target - l) / 20)


def envelope(n: int, spans, depth_db: float, attack: float = 0.05, release: float = 0.3) -> np.ndarray:
    on = np.zeros(n)
    for a, b in spans:
        on[max(0, int(a * SR)):min(n, int(b * SR))] = 1.0
    out = np.zeros(n)
    y = 0.0
    ka, kr = 1 - np.exp(-1 / (attack * SR)), 1 - np.exp(-1 / (release * SR))
    step = 240
    for i in range(0, n, step):
        tgt = on[i:i + step].max()
        k = ka if tgt > y else kr
        y = y + (tgt - y) * (1 - (1 - k) ** step)
        out[i:i + step] = y
    return 10 ** (depth_db * out / 20)


def distant(y: np.ndarray, p: dict, sr: int) -> np.ndarray:
    """The same voice heard from further off for some chunks of a line (the line's `space`: {"chunks": [k, ..],
    "lowpass": Hz, "verb": 0..1, "gain_db": dB}): darker, quieter, with a short room tail. The words and the
    voice don't change, only where they seem to come from."""
    sp = p["space"]
    out = y.copy()
    for k in sp.get("chunks", [0]):
        a, b = p["chunks"][k][:2]
        i0 = max(0, int((a - p["wav_at"] - 0.02) * sr))
        i1 = min(len(y), int((b - p["wav_at"] + 0.06) * sr))
        if i1 <= i0:
            continue
        dry = y[i0:i1]
        far = fft_filter(dry, "low", sp.get("lowpass", 2200.0)) * 10 ** (sp.get("gain_db", -4.0) / 20)
        t = np.arange(int(0.7 * sr)) / sr
        ir = np.random.default_rng(5).standard_normal(len(t)) * np.exp(-t / 0.18)
        ir /= np.sqrt(np.sum(ir ** 2))
        m = len(far) + len(ir) - 1
        tail = np.fft.irfft(np.fft.rfft(far, m) * np.fft.rfft(ir, m), m) * sp.get("verb", 0.5)
        out[i0:i1] = far
        end = min(len(out), i0 + len(tail))
        out[i0:end] += tail[: end - i0]
    return out


def narration(tl: dict, vo_dir: Path) -> tuple[np.ndarray, list]:
    n = int(round(tl["duration"] * SR))
    out = np.zeros(n)
    spans = []
    for lid in tl["order"]:
        p = tl["lines"][lid]
        if p["who"] == "pause":
            continue
        y = load_wav(vo_dir / p["wav"]) * 10 ** (p.get("gain_db", 0.0) / 20)
        if p.get("space"):
            y = distant(y, p, SR)
        i = int(round(p["wav_at"] * SR))
        j0 = max(0, -i)
        seg = y[j0:j0 + n - max(i, 0)]
        out[max(i, 0):max(i, 0) + len(seg)] += seg
        spans.append((p["onset"], p["end"]))
    return out, spans


# ------------------------------------------------------------------------------------------------ score


def _pad(f, dur, bright=0.3, seed=0):
    t = np.arange(synth.n_samples(dur)) / SR
    y = sum(synth.saw(f * (1 + d), dur, phase0=seed * 0.37 + k) for k, d in enumerate((-0.004, 0.0, 0.005)))
    y = fft_filter(y / 3, "low", 300 + 1500 * bright)
    env = np.minimum(1, t / min(1.2, dur / 3)) * np.minimum(1, (dur - t) / min(1.5, dur / 3))
    return y * env


def _musicbox(f, dur=2.0):
    return synth.fm_bell(f, dur, ratio=3.5, index=1.6, tau=0.7) * 0.6


def _piano(f, dur=1.8, seed=0):
    return synth.pluck(f, dur, brightness=0.35, decay_s=0.9, seed=seed) * 0.8


def _drone(f, dur, seed=0):
    t = np.arange(synth.n_samples(dur)) / SR
    y = synth.sine(f, dur) + 0.5 * synth.sine(f * 1.5 * 1.003, dur) + 0.3 * synth.triangle(f * 0.5, dur)
    y *= 0.7 + 0.3 * np.sin(2 * np.pi * (0.13 + 0.05 * seed) * t)
    return fft_filter(y, "low", 500) * np.minimum(1, t / 2.0)


def _pulse(dur):
    return synth.thump(min(dur, 0.35), 90.0, 40.0)


def _tick(seed=0):
    """Opt-in score voice "tick" (ep23): one soft wooden tick, like an old stage clock."""
    return synth.click(0.03, 1500.0, seed) * 0.9


def _blip(f, dur=0.16):
    """A bubbling note: a short sine that drops in pitch as it starts, like a drop into water. Not a pluck."""
    t = np.arange(synth.n_samples(dur)) / SR
    fr = f * (1 + 0.35 * np.exp(-t / 0.012))
    return synth.sine(fr, dur) * np.exp(-t / (dur * 0.35)) * np.minimum(1, t / 0.003)


def _choir(f, dur, seed=0):
    """A breathy 'aah': a pulse through two vowel formants, wobbling slightly. Synthesized, no voice."""
    t = np.arange(synth.n_samples(dur)) / SR
    vib = 1 + 0.006 * np.sin(2 * np.pi * 5.1 * t + seed)
    src = synth.pulse(f * vib, dur, duty=0.3) + 0.3 * synth.noise(dur, seed)
    y = fft_filter(src, "band", 650, 1100) * 0.7 + fft_filter(src, "band", 1000, 1500) * 0.4
    env = np.minimum(1, t / 0.8) * np.minimum(1, (dur - t) / 1.0)
    return y * env


def score(tl: dict, spec: dict) -> np.ndarray:
    """A stereo bed from the story's `music`: {"root": midi, "mode": ..., "bpm": ..., "seed": n,
    "sections": [{"at": ref, "voices": ["drone", "pad", "musicbox", "piano", "pulse", "choir", "bubble"], "energy": 0..1,
    "chord_beats": 8, "mode": a section's own mode, "root": its own root (a turn to the relative major)}]}."""
    at = resolver(tl["lines"], tl["duration"])
    rng = np.random.default_rng(spec.get("seed", 1))
    dur = tl["duration"]
    n = int(round(dur * SR))
    out = np.zeros((n, 2))
    beat = 60 / spec.get("bpm", 72)
    scale = MODES[spec.get("mode", "minor")]
    root = spec.get("root", 50)

    def deg(d, octave=0, sc=scale, rt=root):
        return rt + 12 * (octave + d // len(sc)) + sc[d % len(sc)]

    def put(sig, t0, gain, pan=0.0):
        i = int(round(t0 * SR))
        if i >= n or i + len(sig) <= 0:
            return
        j0 = max(0, -i)
        seg = sig[j0:j0 + n - max(i, 0)] * gain
        l, r = math.cos((pan + 1) * math.pi / 4), math.sin((pan + 1) * math.pi / 4)
        out[max(i, 0):max(i, 0) + len(seg), 0] += seg * l * 1.41
        out[max(i, 0):max(i, 0) + len(seg), 1] += seg * r * 1.41

    secs = spec.get("sections", [{"at": 0, "voices": ["drone", "pad"], "energy": 0.4}])
    starts = [at(s["at"]) for s in secs] + [dur]
    chord = 0
    for si, s in enumerate(secs):
        a, b = starts[si], starts[si + 1]
        if b <= a:
            continue
        voices = s.get("voices", [])
        e = s.get("energy", 0.5)
        cb = s.get("chord_beats", 8) * beat
        t = a
        while t < b - 0.05:
            seg = min(cb, b - t)
            # the chord: a random step among i, iv, v-ish degrees and a dark ii
            chord = int(rng.choice([0, 3, 4, 5, 1, 6], p=[0.3, 0.2, 0.15, 0.15, 0.1, 0.1]))
            sc, rt = MODES[s.get("mode", spec.get("mode", "minor"))], s.get("root", root)
            tones = [deg(chord, 0, sc, rt), deg(chord + 2, 0, sc, rt), deg(chord + 4, 0, sc, rt)]
            if "drone" in voices:
                put(_drone(synth.midi_hz(rt - 12), seg + 0.8, si), t, 0.35 + 0.2 * e)
            if "pad" in voices:
                for k, m in enumerate(tones):
                    put(_pad(synth.midi_hz(m), seg + 1.0, 0.2 + 0.5 * e, si * 3 + k), t, 0.12, pan=(k - 1) * 0.5)
            if "choir" in voices:
                for k, m in enumerate(tones[:2]):
                    put(_choir(synth.midi_hz(m + 12), seg + 0.6, si + k), t, 0.08, pan=(k - 0.5) * 0.8)
            steps = int(round(seg / beat))
            for q in range(steps):
                tq = t + q * beat
                if "tick" in voices:   # opt-in (ep23): a soft wooden tick on every beat
                    put(_tick(q), tq, 0.35 + 0.2 * e)
                if "pulse" in voices and (q % 2 == 0 or e > 0.7):
                    put(_pulse(beat), tq, 0.5 + 0.4 * e)
                if "musicbox" in voices and rng.random() < 0.35 + 0.5 * e:
                    m = int(rng.choice(tones)) + 24 + int(rng.choice([0, 0, 12]))
                    put(_musicbox(synth.midi_hz(m) * (1 + 0.002 * rng.standard_normal())), tq + (beat / 2 if rng.random() < 0.3 else 0),
                        0.18, pan=float(rng.uniform(-0.6, 0.6)))
                if "bubble" in voices:   # a soft bubbling arpeggio, two short drops a beat, chord tones up high
                    for h in (0.0, 0.5):
                        if rng.random() < 0.45 + 0.4 * e:
                            m = int(rng.choice(tones)) + 24 + int(rng.choice([0, 12]))
                            put(_blip(synth.midi_hz(m)), tq + h * beat + 0.02 * rng.standard_normal(), 0.1,
                                pan=float(rng.uniform(-0.7, 0.7)))
                if "piano" in voices and rng.random() < 0.3 + 0.5 * e:
                    m = int(rng.choice(tones)) + 12
                    put(_piano(synth.midi_hz(m), 2.0, q), tq, 0.25, pan=float(rng.uniform(-0.3, 0.3)))
            t += seg
    return out


def filter_track(n: int, keys: list, at, floor_hz: float = 20000.0) -> np.ndarray:
    """A low-pass cutoff (Hz) for every STFT hop of a track n samples long, from keys [{"at": ref, "hz": f,
    "dur": s}]: each key eases from the cutoff before it to its own over its dur (on a log scale)."""
    hop = 512
    t = np.arange(0, n + hop, hop) / SR
    lg = np.full(len(t), np.log(floor_hz))
    for k in sorted(keys, key=lambda k: at(k["at"])):
        t0, d = at(k["at"]), float(k.get("dur", 0.0))
        u = np.clip((t - t0) / d, 0, 1) if d > 0 else (t >= t0).astype(float)
        u = u * u * (3 - 2 * u)
        lg = lg + (np.log(float(k["hz"])) - lg) * u
    return np.exp(lg)


def lowpass_moving(x: np.ndarray, cutoff: np.ndarray, slope: float = 4.0) -> np.ndarray:
    """x (mono or stereo) through a low-pass whose cutoff moves (one value per 512-sample hop): a short-time
    Fourier mask, 1 / (1 + (f / fc)^slope), so slope 4 is 24 dB an octave. Hann windows at 75% overlap."""
    if x.ndim == 2:
        return np.stack([lowpass_moving(x[:, c], cutoff, slope) for c in range(x.shape[1])], 1)
    nfft, hop = 2048, 512
    pad = np.concatenate([np.zeros(nfft), x, np.zeros(nfft)])
    win = np.hanning(nfft)
    frames = np.lib.stride_tricks.sliding_window_view(pad, nfft)[::hop]
    X = np.fft.rfft(frames * win, axis=1)
    f = np.fft.rfftfreq(nfft, 1 / SR)
    ci = np.clip(np.arange(len(frames)) - nfft // hop, 0, len(cutoff) - 1)
    fc = cutoff[ci][:, None]
    X *= 1.0 / (1.0 + (f[None, :] / fc) ** slope)
    y = np.fft.irfft(X, nfft, axis=1) * win
    out = np.zeros(len(pad))
    norm = np.zeros(len(pad))
    for i in range(len(frames)):
        out[i * hop:i * hop + nfft] += y[i]
        norm[i * hop:i * hop + nfft] += win ** 2
    out = out / np.maximum(norm, 1e-8)
    return out[nfft:nfft + len(x)]


# ---------------------------------------------------------------------------------------------- ambience


def amb(kind: str, dur: float, seed: int = 0) -> np.ndarray:
    n = synth.n_samples(dur)
    t = np.arange(n) / SR
    if kind == "wind":
        y = fft_filter(synth.noise(dur, seed), "band", 200, 900)
        y *= 0.55 + 0.45 * synth.one_pole_smooth(np.abs(np.sin(2 * np.pi * 0.11 * t + seed)) + 0.3 * synth.noise(dur, seed + 1), 0.6)
        return y
    if kind == "hum":
        return synth.hum(dur, 60.0, seed)
    if kind == "rain":
        y = fft_filter(synth.noise(dur, seed), "band", 800, 7000) * 0.6
        drops = np.zeros(n)
        r = np.random.default_rng(seed)
        for i in r.integers(0, n - 2000, int(dur * 40)):
            drops[i:i + 400] += synth.click(400 / SR, float(r.uniform(2500, 6000)), int(i))[:400] * r.uniform(0.2, 0.8)
        return y + drops
    if kind == "room":
        return fft_filter(synth.noise(dur, seed), "band", 60, 400) * 0.6
    if kind == "drips":
        y = np.zeros(n)
        r = np.random.default_rng(seed)
        tt = 0.4
        while tt < dur - 0.3:
            i = int(tt * SR)
            f0 = float(r.uniform(900, 1600))
            d = synth.chirp(f0, f0 * 1.6, 0.05) * synth.decay(0.05, 0.015)
            y[i:i + len(d)] += d[: n - i]
            tt += float(r.uniform(0.7, 2.2))
        return y
    if kind == "crickets":
        y = np.zeros(n)
        r = np.random.default_rng(seed)
        for k in range(3):
            f0 = 4200 + 500 * k
            rate = 14 + 3 * k
            gate = (np.sin(2 * np.pi * rate * t + k) > 0.6) * (np.sin(2 * np.pi * (0.4 + 0.1 * k) * t + r.uniform(0, 6)) > 0)
            y += synth.sine(f0, dur) * synth.one_pole_smooth(gate.astype(float), 0.004) * 0.3
        return y
    if kind == "water":
        y = fft_filter(synth.noise(dur, seed), "band", 150, 1200)
        return y * (0.6 + 0.4 * synth.one_pole_smooth(np.sin(2 * np.pi * 0.3 * t) ** 2 + 0.5 * synth.noise(dur, seed + 2), 0.3))
    if kind == "drone":
        return _drone(55.0, dur, seed)
    if kind == "static":
        return fft_filter(synth.noise(dur, seed), "high", 1500) * 0.5
    raise ValueError(f"no ambience {kind!r}")


def _layer(*parts: np.ndarray) -> np.ndarray:
    """Sum sounds of different lengths, each from the start (the shorter ones are padded with silence)."""
    out = np.zeros(max(len(p) for p in parts))
    for p in parts:
        out[: len(p)] += p
    return out


def step_sound(surface: str, run: bool, seed: int) -> np.ndarray:
    r = np.random.default_rng(seed)
    if surface == "wood":
        y = _layer(synth.thump(0.12, 180, 90, seed) * 0.8, fft_filter(synth.noise(0.05, seed), "band", 400, 2000) * synth.decay(0.05, 0.012)[: synth.n_samples(0.05)] * 0.5)
    elif surface == "metal":
        y = _layer(synth.thump(0.1, 220, 120, seed) * 0.5, synth.fm_bell(float(r.uniform(700, 900)), 0.25, 2.7, 1.2, 0.06) * 0.25)
    elif surface == "grass":
        y = fft_filter(synth.noise(0.12, seed), "band", 1500, 6000) * synth.decay(0.12, 0.04)[: synth.n_samples(0.12)] * 0.6
    else:  # stone, concrete
        y = _layer(synth.thump(0.08, 140, 70, seed) * 0.6, fft_filter(synth.noise(0.06, seed), "band", 1200, 5000) * synth.decay(0.06, 0.01)[: synth.n_samples(0.06)] * 0.6)
    return y * (1.4 if run else 1.0) * float(r.uniform(0.8, 1.1))


KNOCK_TONES = ("classic", "below", "hand", "glass", "soft", "glass_soft")


def knock_hit(tone: str, seed: int = 0) -> np.ndarray:
    """One knock. below: a deep, muffled knock up through boards (wood and bone, a low body); hand: a sharper
    knuckle on planks; glass: a door with a pane in it, the glass rattling after; soft: bone on wood, close and
    quiet; glass_soft: the door again, very softly. classic: the old single thump."""
    r = np.random.default_rng(seed)
    v = float(r.uniform(0.92, 1.08))
    if tone == "classic":
        return synth.thump(0.12, 200, 100, seed)
    if tone == "below":
        body = synth.thump(0.32, 115 * v, 52, seed) * 1.1
        wood = fft_filter(synth.noise(0.09, seed), "band", 120, 700) * synth.decay(0.09, 0.022)[: synth.n_samples(0.09)]
        boom = synth.sine(68 * v, 0.4) * synth.decay(0.4, 0.11)[: synth.n_samples(0.4)] * 0.5
        return fft_filter(_layer(body, wood * 0.9, boom), "low", 900)
    if tone == "hand":
        body = synth.thump(0.12, 240 * v, 120, seed) * 0.8
        tick = fft_filter(synth.noise(0.03, seed), "band", 900, 4200) * synth.decay(0.03, 0.006)[: synth.n_samples(0.03)]
        return _layer(body, tick * 0.9, synth.click(0.008, 2600.0, seed) * 0.25)
    if tone in ("glass", "glass_soft"):
        body = synth.thump(0.16, 170 * v, 80, seed) * 0.8
        pane = synth.fm_bell(1750 * v, 0.22, ratio=2.4, index=1.1, tau=0.05) * 0.18
        y = _layer(body, pane)
        for j in range(5):          # the pane rattling in its frame after the knock
            i = int((0.03 + 0.018 * j + 0.006 * r.random()) * SR)
            c = fft_filter(synth.noise(0.012, seed + j), "band", 1800, 6000) * synth.decay(0.012, 0.003)[: synth.n_samples(0.012)]
            y[i:i + len(c)] += c[: len(y) - i] * 0.22 * (1 - j / 5)
        return y * (0.35 if tone == "glass_soft" else 1.0)
    if tone == "soft":
        body = synth.thump(0.16, 170 * v, 85, seed) * 0.55
        bone = fft_filter(synth.noise(0.02, seed), "band", 700, 2200) * synth.decay(0.02, 0.005)[: synth.n_samples(0.02)]
        return fft_filter(_layer(body, bone * 0.5), "low", 2500)
    raise ValueError(f"no knock tone {tone!r}")


def sfx(kind: str, seed: int = 0, dur: float = 1.0, opts: dict | None = None) -> np.ndarray:
    if kind == "hit":  # a low boom with a crack on top: the jump moment
        return _layer(synth.hit(1.6, seed) * 1.0, synth.thump(0.6, 70, 30, seed) * 0.8)
    if kind == "riser":
        t = np.arange(synth.n_samples(dur)) / SR
        y = fft_filter(synth.noise(dur, seed), "band", 300, 4000) * (t / dur) ** 2
        return y + synth.saw(220 * 2 ** (t / dur), dur) * 0.08 * (t / dur) ** 2
    if kind == "whoosh":
        t = np.arange(synth.n_samples(0.5)) / SR
        return fft_filter(synth.noise(0.5, seed), "band", 400, 2500) * np.sin(np.pi * t / 0.5) ** 2
    if kind == "creak" and (opts or {}).get("tone") == "cardboard":   # ep17, opt-in: a slow, low, papery flex
        return _cardboard_creak(dur, seed)
    if kind == "creak":
        t = np.arange(synth.n_samples(dur)) / SR
        f = 140 + 60 * np.sin(2 * np.pi * 0.7 * t) + 20 * synth.noise(dur, seed)
        return fft_filter(synth.pulse(f, dur, 0.1), "band", 300, 2500) * np.sin(np.pi * t / dur) * 0.5
    if kind == "door":
        return _layer(synth.thump(0.5, 110, 40, seed) * 1.0,
                      fft_filter(synth.noise(0.15, seed), "low", 900) * synth.decay(0.15, 0.04)[: synth.n_samples(0.15)])
    if kind == "knock":   # opts: pattern, gains, tone, crack (0..1, a wooden crack on top of each hit)
        o = opts or {}
        pat = o.get("pattern", (0.0, 0.28, 0.56))
        gains = o.get("gains", [1.0] * len(pat))
        y = np.zeros(synth.n_samples(max(pat) + 1.0))
        for k, (t0, g) in enumerate(zip(pat, gains)):
            tone = o.get("tone", "classic")
            s = knock_hit(tone, seed + k if tone == "classic" else seed * 31 + k) * g
            if o.get("crack"):   # a short wooden crack on top, so a deep knock still reads on a phone speaker
                c = fft_filter(synth.noise(0.035, seed * 7 + k), "band", 900, 3500) * synth.decay(0.035, 0.007)[: synth.n_samples(0.035)]
                c = _layer(c, synth.click(0.006, 1800.0, seed + k) * 0.4) * float(o["crack"]) * g
                s = s.copy()
                s[: len(c)] += c[: len(s)]
            i = int(t0 * SR)
            y[i:i + len(s)] += s[: len(y) - i]
        return y
    if kind == "glitch":
        y = fft_filter(synth.noise(dur, seed), "high", 800) * 0.6
        gate = np.repeat(np.random.default_rng(seed).random(int(dur * 40) + 1) > 0.45, SR // 40)[: len(y)]
        return y * gate + synth.pulse(97.0, dur, 0.2)[: len(y)] * gate * 0.3
    if kind == "bell":
        return synth.fm_bell(196.0, 4.0, ratio=2.76, index=2.4, tau=1.6) * 0.8
    if kind == "thud":
        return synth.thump(0.4, 90, 35, seed)
    if kind == "sting":  # a sharp dissonant cluster: the reveal
        y = sum(_pad(synth.midi_hz(m), dur, 0.8, k) for k, m in enumerate((62, 63, 69)))
        return y * synth.decay(dur, dur * 0.4)[: len(y)]
    if kind == "click":
        return synth.click(0.01, 2500.0, seed)
    if kind == "wetclick":  # a slow, sticky parting: a soft low pop, then small tacky ticks thinning out
        n = synth.n_samples(max(0.6, dur))
        y = np.zeros(n)
        pop = fft_filter(synth.noise(0.08, seed), "band", 180, 900) * synth.decay(0.08, 0.02)[: synth.n_samples(0.08)]
        y[: len(pop)] += pop * 0.9 + synth.thump(0.08, 120, 60, seed)[: len(pop)] * 0.5
        r = np.random.default_rng(seed)
        t = 0.05
        while t < len(y) / SR - 0.05:
            f0 = float(r.uniform(1400, 3200))
            tick = synth.chirp(f0, f0 * 0.6, 0.02) * synth.decay(0.02, 0.004)[: synth.n_samples(0.02)]
            i = int(t * SR)
            y[i:i + len(tick)] += tick[: n - i] * float(r.uniform(0.15, 0.45)) * (1 - t / (len(y) / SR))
            t += float(r.uniform(0.03, 0.11)) * (1 + 2 * t)
        return y
    if kind == "pop":     # one small bubble: a quick rising blip with a wet tick
        return _layer(synth.chirp(700.0, 1900.0, 0.03) * synth.decay(0.03, 0.01)[: synth.n_samples(0.03)],
                      synth.click(0.004, 3200.0, seed) * 0.3)
    if kind in ("bubbles", "tinybubbles"):   # a wash of bubbles and soft clicks: the applause (or a thin stream)
        tiny = kind == "tinybubbles"
        y = np.zeros(synth.n_samples(dur + 0.4))
        r = np.random.default_rng(seed)
        rate = 18 if tiny else 150
        for _ in range(int(rate * dur)):
            t0 = float(r.uniform(0, dur))
            f0 = float(r.uniform(900, 2600) if tiny else r.uniform(300, 2200))
            d = float(r.uniform(0.012, 0.05))
            b = synth.chirp(f0, f0 * float(r.uniform(1.4, 2.2)), d) * synth.decay(d, d * 0.3)[: synth.n_samples(d)]
            i = int(t0 * SR)
            y[i:i + len(b)] += b[: len(y) - i] * float(r.uniform(0.2, 1.0)) * (0.5 if tiny else 1.0)
        if not tiny:   # under it, the hiss of a lot of air going up
            hs = fft_filter(synth.noise(dur + 0.4, seed + 1), "band", 600, 5000)
            env = np.sin(np.pi * np.clip(np.arange(len(hs)) / SR / (dur + 0.2), 0, 1)) ** 0.7
            y += hs * env * 0.12
        return y
    if kind in ("squeak", "squeal"):   # wet skin on acrylic: a rubbery, wobbling tone (squeal: the long drag)
        d = dur if kind == "squeal" else min(dur, 0.35)
        t = np.arange(synth.n_samples(d)) / SR
        r = np.random.default_rng(seed)
        wob = synth.one_pole_smooth(synth.noise(d, seed), 0.02) * 6
        f = (520 if kind == "squeal" else 780) * (1 + 0.35 * np.sin(2 * np.pi * 0.6 * t / max(d, 0.1)) + 0.04 * wob)
        stick = (np.sin(2 * np.pi * float(r.uniform(18, 26)) * t) > -0.2).astype(float)   # stick-slip chatter
        src = synth.pulse(f, d, 0.18) * synth.one_pole_smooth(stick, 0.003)
        y = fft_filter(src, "band", 400, 3800) * 0.6 + fft_filter(synth.noise(d, seed + 3), "band", 1500, 6000) * 0.04
        env = np.minimum(1, t / 0.06) * np.minimum(1, (d - t) / 0.12)
        return y * env
    if kind == "glide":   # its glide when it comes close: a low, slow, whale-like fall in pitch
        t = np.arange(synth.n_samples(dur)) / SR
        f = 70 * (1 - 0.3 * t / dur) * (1 + 0.02 * np.sin(2 * np.pi * 3.1 * t))
        src = synth.saw(f, dur) * 0.5 + synth.sine(f * 2.01, dur) * 0.4
        y = fft_filter(src, "band", 90, 700) * np.sin(np.pi * t / dur) ** 1.5
        return y
    if kind == "hum_sweep":   # the display lights fading down: an electrical hum dropping away
        t = np.arange(synth.n_samples(dur)) / SR
        y = synth.hum(dur, 60.0, seed) * (1 - t / dur) ** 1.4
        return fft_filter(y, "band", 80, 2400)
    if kind == "castors":     # a mop bucket rolling on small wheels over concrete
        t = np.arange(synth.n_samples(dur)) / SR
        rum = fft_filter(synth.noise(dur, seed), "band", 120, 900) * (0.6 + 0.4 * np.sin(2 * np.pi * 9 * t))
        y = rum * np.sin(np.pi * t / dur) * 0.6
        for k in range(int(dur * 7)):
            i = int((k / 7 + 0.03) * SR)
            c = synth.click(0.006, 1400.0, seed + k) * 0.3
            y[i:i + len(c)] += c[: len(y) - i]
        return y
    if kind == "radio":   # opt-in (ep14): a press click, then a short band-limited static burst. No voice
        d = max(0.25, dur if dur != 1.0 else 0.45)
        n = synth.n_samples(d)
        t = np.arange(n) / SR
        y = fft_filter(synth.noise(d, seed), "band", 900, 4200)[:n] * np.minimum(1, t / 0.02) * np.exp(-t / (d * 0.5)) * 0.7
        c = synth.click(0.01, 2500.0, seed)[:n]
        y[:len(c)] += c
        return y
    if kind == "breath":  # opt-in (ep14): one slow, heavy breath of something huge: low filtered noise, swelling and fading
        n = synth.n_samples(dur)
        t = np.arange(n) / SR
        env = np.sin(np.pi * np.clip(t / dur, 0, 1)) ** 1.5
        y = fft_filter(synth.noise(dur, seed), "band", 70, 600)[:n] * env
        return y + 0.4 * fft_filter(synth.noise(dur, seed + 1), "band", 600, 1800)[:n] * env ** 3
    if kind == "tape":        # ep17: packing tape peeled off board, a sticky crackle
        return _tape_peel(dur if dur != 1.0 else 0.75, seed)
    if kind == "scrape":      # ep17: cardboard dragged on floorboards; opts "distant": heard through a wall
        return _scrape(dur, seed, bool((opts or {}).get("distant")))
    if kind == "clap":   # opt-in (ep23): one hand clap in an empty hall, a short room tail after it
        return _clap(dur, seed)
    if kind == "silence":
        return np.zeros(1)
    raise ValueError(f"no sfx {kind!r}")


def _clap(dur: float, seed: int) -> np.ndarray:
    """A single clap: three close noise bursts (the palms), then a dark room tail that keeps going for `dur`."""
    d = max(dur, 0.8)
    y = np.zeros(synth.n_samples(d))
    for k, (t0, g) in enumerate(((0.0, 1.0), (0.011, 0.7), (0.021, 0.45))):
        b = fft_filter(synth.noise(0.09, seed + k), "band", 900, 3800) * synth.decay(0.09, 0.016, 0.0006)[: synth.n_samples(0.09)]
        i = int(t0 * SR)
        y[i:i + len(b)] += b * g
    tail = fft_filter(synth.noise(d, seed + 9), "band", 300, 1800) * synth.decay(d, d / 4.5, 0.012)[: len(y)]
    y += tail * 0.22
    return y / max(1e-9, np.abs(y).max()) * 0.9


def _crackle(dur: float, seed: int, rate: float, lo: float, hi: float) -> np.ndarray:
    """Random tiny clicks at about `rate` a second, each a short band-limited tick."""
    rng = np.random.default_rng(seed)
    n = synth.n_samples(dur)
    y = np.zeros(n)
    k = int(rate * dur)
    for i in rng.integers(0, max(1, n - 64), k):
        y[i] += rng.uniform(0.3, 1.0) * rng.choice([-1, 1])
    return fft_filter(y, "band", lo, hi)


def _tape_peel(dur: float, seed: int) -> np.ndarray:
    """A strip of packing tape coming off board: a fast sticky crackle that rises as it goes, over a thin
    tearing hiss, then a little tug at the end."""
    n = synth.n_samples(dur)
    t = np.arange(n) / SR
    env = np.clip(t / (dur * 0.15), 0, 1) * (1 - np.clip((t - dur * 0.85) / (dur * 0.15), 0, 1))
    rate = 260 + 520 * (t / dur)
    crack = _crackle(dur, seed, float(rate.mean()), 1200, 7000)
    hiss = fft_filter(synth.noise(dur, seed + 1), "band", 2500, 9000) * 0.18
    y = (crack * 1.6 + hiss) * env * (0.6 + 0.4 * t / dur)
    tug = synth.thump(0.06, 260, 120, seed) * 0.25
    y[-len(tug):] += tug
    return y / (np.abs(y).max() + 1e-9)


def _scrape(dur: float, seed: int, distant: bool) -> np.ndarray:
    """A box dragged across boards: friction noise in stick-slip bursts (an uneven 7 to 13 a second), a soft
    knock where a corner catches a board seam. Distant: through a wall, so dull, lower and a little smeared."""
    rng = np.random.default_rng(seed)
    n = synth.n_samples(dur)
    t = np.arange(n) / SR
    rough = fft_filter(synth.noise(dur, seed), "band", 180, 2200)
    f = 7 + 6 * np.abs(np.sin(2 * np.pi * 0.4 * t + rng.uniform(0, 6)))
    stick = 0.35 + 0.65 * np.clip(np.sin(2 * np.pi * np.cumsum(f) / SR) * 1.4, 0, 1) ** 2
    env = np.clip(t / 0.12, 0, 1) * np.clip((dur - t) / 0.2, 0, 1)
    y = rough * stick * env
    for at in rng.uniform(0.1, max(0.11, dur - 0.2), max(1, int(dur * 1.5))):   # corners catching seams
        i = int(at * SR)
        k = synth.thump(0.09, 160, 70, int(at * 1000)) * 0.5
        y[i:i + len(k)] += k[: n - i]
    if distant:
        y = fft_filter(y, "low", 650) * 0.55
        d = int(0.023 * SR)
        y[d:] += y[:-d] * 0.35   # a little of the other room in it
    return y / (np.abs(y).max() + 1e-9)


def _cardboard_creak(dur: float, seed: int) -> np.ndarray:
    """Board flexing under weight: a slow swell of dry fibre crackle and a low papery rustle, never a wooden
    groan (a wooden creak is lookout's)."""
    n = synth.n_samples(dur)
    t = np.arange(n) / SR
    swell = np.sin(np.pi * np.clip(t / dur, 0, 1)) ** 1.5
    crack = _crackle(dur, seed, 140, 600, 4500)
    rustle = fft_filter(synth.noise(dur, seed + 3), "band", 250, 1400) * 0.35
    slow = 0.6 + 0.4 * np.sin(2 * np.pi * 1.3 * t + seed)
    y = (crack * slow + rustle) * swell
    return y / (np.abs(y).max() + 1e-9)


FILE_TP = -1.6         # the encoded file's true peak target (the gate is -1.5 dBTP on the final AAC)


def fit_file_peak(audio: np.ndarray, measure, target: float = FILE_TP, tries: int = 4) -> tuple[np.ndarray, list]:
    """Limit the mastered audio lower until its encoded file's true peak is at or under `target`. `measure(audio)`
    encodes it the way the film will be and returns the file's true peak in dBTP (ffmpeg's ebur128), because the
    AAC encode adds 0.5 to 1 dB that the master can't see. Returns the audio and each try's (ceiling, file dBTP)."""
    from blocky.mixer import limit

    log = []
    ceiling = TP_CEILING
    for _ in range(tries):
        tp = measure(audio)
        log.append((round(ceiling, 2), tp))
        if tp <= target:
            break
        ceiling -= tp - target + 0.05
        audio = limit(audio, ceiling)
    return audio, log


def drop_spec(d) -> dict:
    """A `music_drops` entry: [from, to] or {"from": ref, "to": ref, "keep": [sfx kinds that play through]}.
    Anchor both ends to line ids, so a retime can't move the hole off its words."""
    if isinstance(d, dict):
        return {"from": d["from"], "to": d["to"], "keep": list(d.get("keep", [])), "db": float(d.get("db", DROP_DB))}
    return {"from": d[0], "to": d[1], "keep": [], "db": DROP_DB}


def mix(tl: dict, st: dict, vo_dir: Path) -> tuple[np.ndarray, dict]:
    at = resolver(tl["lines"], tl["duration"])
    dur = tl["duration"]
    n = int(round(dur * SR))
    m = Mix(dur)
    voice, spans = narration(tl, vo_dir)
    voice = to_lufs(voice, SPEECH, spans)
    m.add("voice", 0.0, voice)
    snd = st.get("sound", {})
    mus = score(tl, st.get("music", {}))
    if st.get("music", {}).get("filter"):   # the score heard through water: a low-pass that moves (the reveal opens it)
        mus = lowpass_moving(mus, filter_track(len(mus), st["music"]["filter"], at))
    free = [(0, dur)] if not spans else [(a, b) for a, b in zip([0] + [e for _, e in spans], [s for s, _ in spans] + [dur]) if b - a > 0.4]
    mus = to_lufs(mus, MUSIC_FREE, free or None)
    mus *= envelope(n, spans, MUSIC_UNDER - MUSIC_FREE)[:, None]
    m.add("music", 0.0, mus)
    for k, a in enumerate(snd.get("ambience", [])):
        a0, a1 = at(a.get("from", 0)), at(a.get("to", "end"))
        if a1 <= a0:
            continue
        y = amb(a["kind"], a1 - a0, k + 3)
        y *= np.minimum(1, np.arange(len(y)) / (0.3 * SR)) * np.minimum(1, (len(y) - np.arange(len(y))) / (0.3 * SR))
        m.add("amb", a0, to_lufs(y, a.get("lufs", -32.0)), pan=a.get("pan", 0.0))
    surface = snd.get("floor", "stone")
    # opt-in: a floor per span of the film ("floor_spans": [{"from": ref, "to": ref, "floor": ...}]), over the
    # story's or the character's own
    fspans = [(at(f["from"]), at(f["to"]), f["floor"]) for f in snd.get("floor_spans", [])]
    for i, who in enumerate(st.get("cast", {})):
        for k, fs in enumerate(acting.footsteps(tl, who)):
            fl = next((f for a0, a1, f in fspans if a0 <= fs["t"] < a1), snd.get("floors", {}).get(who, surface))
            m.add("steps", fs["t"], step_sound(fl, fs["run"], i * 1000 + k),
                  gain_db=snd.get("steps_db", -20.0), pan=float(np.clip(fs["x"] * 0.1, -0.6, 0.6)))
    drops = [drop_spec(d) for d in snd.get("music_drops", [])]
    for k, e in enumerate(snd.get("sfx", [])):
        y = sfx(e["kind"], k, e.get("dur", 1.0), e)
        te = at(e["at"])
        keep = e.get("keep", False) or any(e["kind"] in d["keep"] and at(d["from"]) - 0.05 <= te < at(d["to"]) + 0.4
                                           for d in drops)
        m.add("sfx_keep" if keep else "sfx", te, y, gain_db=e.get("db", -8.0), pan=e.get("pan", 0.0))
    # the holes: everything but the voice and the kept sounds (a sting, a named hit) drops to near silence
    if drops:
        hole = np.ones(n)
        for db in sorted({d["db"] for d in drops}):   # a drop can go deeper than DROP_DB with its own "db"
            hole = np.minimum(hole, envelope(n, [(at(d["from"]), at(d["to"])) for d in drops if d["db"] == db], db,
                                             0.03, 0.4))
        hole = hole[:, None]
        for bus in ("music", "amb", "steps", "sfx"):
            if bus in m.buses:
                m.buses[bus] *= hole
    pre = m.sum()
    out, stats = master(pre, ceiling_db=TP_CEILING)
    k = min(len(out), int(0.012 * SR))   # no click where the film (or its loop) cuts off
    out[len(out) - k:] *= np.linspace(1.0, 0.0, k)[:, None]
    stats["stems_lufs"] = {k: round(float(loudness(v)), 1) for k, v in m.stems().items() if np.any(v)}
    stats["voice_lufs_over_lines"] = round(lufs(out, spans), 1) if spans else None
    return out, stats
