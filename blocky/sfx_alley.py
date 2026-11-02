"""Sounds for ep29 (ten-pin), all synthesized here: the lane lights' buzz, a ball rolling, pins clattering, the
pinsetter's clunk and the sweep's whirr, a soft reversing beep, and the hollow wooden thunk of a ball return.
Opt-in: `sound.sfx` hands any kind starting with "alley_" to `make`, so no other story's sound changes."""

from __future__ import annotations

import numpy as np

from blocky import synth
from blocky.synth import SR


def _env(n, a=0.004, tau=0.1):
    t = np.arange(n) / SR
    return np.minimum(1.0, t / a) * np.exp(-t / tau)


def _lp(x, hz):
    from blocky.sound import fft_filter
    return fft_filter(x, "low", hz)


def _bp(x, lo, hi):
    from blocky.sound import fft_filter
    return fft_filter(x, "band", lo, hi)


def _add(y, s, t0, g=1.0):
    i = int(t0 * SR)
    if i >= len(y):
        return
    s = s[: len(y) - i]
    y[i:i + len(s)] += s * g


def make(kind: str, seed: int, dur: float, opts: dict | None = None) -> np.ndarray:
    o = opts or {}
    r = np.random.default_rng(seed + 11)
    if kind == "alley_buzz":      # a tube light that hums and crackles
        n = synth.n_samples(dur)
        t = np.arange(n) / SR
        y = synth.sine(100.0, dur)[:n] * 0.5 + synth.sine(200.0, dur)[:n] * 0.25 + synth.sine(300.0, dur)[:n] * 0.1
        crack = np.zeros(n)
        for _ in range(int(dur * 30)):
            _add(crack, synth.click(0.004, float(r.uniform(2000, 5000)), int(r.integers(1e6))), float(r.uniform(0, dur)),
                 float(r.uniform(0.1, 0.5)))
        env = np.minimum(1, t / 0.15) * np.minimum(1, (dur - t) / 0.25)
        return (y + crack) * env
    if kind == "alley_roll":      # a ball on boards: a low rumble that swells and fades, a wobble once a turn
        n = synth.n_samples(dur)
        t = np.arange(n) / SR
        y = _bp(synth.noise(dur, seed), 70, 420)[:n]
        y = y * (0.65 + 0.35 * np.sin(2 * np.pi * 5.0 * t)) * np.sin(np.pi * np.clip(t / dur, 0, 1)) ** 0.6
        return y * 1.4
    if kind == "alley_clatter":   # pins: wooden bonks, many, thinning out, with a low roll under them
        n = synth.n_samples(max(dur, 1.6))
        y = np.zeros(n)
        times = np.sort(np.concatenate([r.uniform(0, 0.35, 8), r.uniform(0.2, 1.3, 18)]))
        for k, t0 in enumerate(times):
            f = float(r.uniform(420, 1100))
            bonk = synth.sine(f, 0.12)[: synth.n_samples(0.12)] * _env(synth.n_samples(0.12), 0.001, 0.025)
            tick = _bp(synth.noise(0.04, seed + k), 800, 4500) * _env(synth.n_samples(0.04), 0.0005, 0.008)
            g = float(r.uniform(0.4, 1.0)) * (1.0 - 0.5 * t0 / 1.4)
            _add(y, bonk, float(t0), 0.5 * g)
            _add(y, tick, float(t0), 0.7 * g)
        _add(y, _bp(synth.noise(1.2, seed), 60, 300) * np.exp(-np.arange(synth.n_samples(1.2)) / SR / 0.45), 0.0, 0.9)
        return y
    if kind == "alley_clunk":     # the pinsetter: a heavy mechanical drop and a metal tick
        y = np.zeros(synth.n_samples(0.9))
        _add(y, synth.thump(0.35, 110, 40, seed), 0.0, 1.0)
        _add(y, synth.fm_bell(310.0, 0.5, 2.6, 1.0, 0.07) * 0.25, 0.02)
        _add(y, _bp(synth.noise(0.12, seed), 500, 3000) * _env(synth.n_samples(0.12), 0.001, 0.03), 0.0, 0.8)
        _add(y, synth.thump(0.2, 140, 60, seed + 1), 0.4, 0.5)
        return y
    if kind == "alley_whirr":     # the sweep rising: a motor whine climbing
        n = synth.n_samples(dur)
        t = np.arange(n) / SR
        y = synth.whirr(dur, seed, 380.0)[:n] if hasattr(synth, "whirr") else _bp(synth.noise(dur, seed), 200, 900)[:n]
        sweep = synth.saw(150 + 220 * t / dur, dur)[:n] * 0.12
        return (y * 0.7 + sweep) * np.minimum(1, t / 0.1) * np.minimum(1, (dur - t) / 0.2)
    if kind == "alley_beep":      # a soft reversing beep: two square pulses a beat apart, each a short rounded tone
        pat = o.get("pattern", [0.0])
        y = np.zeros(synth.n_samples(max(pat) + 0.5))
        for t0 in pat:
            n = synth.n_samples(0.14)
            b = _lp(synth.pulse(1000.0, 0.14, 0.5)[:n], 3200)
            _add(y, b * np.minimum(1, np.arange(n) / (0.006 * SR)) * np.minimum(1, (n - np.arange(n)) / (0.02 * SR)) * 0.45, t0)
        return y
    if kind == "alley_thunk":     # a hollow wooden thunk with a pitch fall, the ball landing in its rack
        n = synth.n_samples(0.9)
        t = np.arange(n) / SR
        body = synth.thump(0.5, 190, 62, seed) * 1.0
        knock = _bp(synth.noise(0.06, seed), 250, 1500) * _env(synth.n_samples(0.06), 0.001, 0.012)
        hollow = synth.sine(150.0 * np.exp(-t * 2.2), 0.9)[:n] * np.exp(-t / 0.22) * 0.8
        y = np.zeros(n)
        _add(y, body, 0.0, 0.9)
        _add(y, knock, 0.0, 0.9)
        y += hollow
        return _lp(y, 2600)
    raise ValueError(f"no sfx {kind!r}")
