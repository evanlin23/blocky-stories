"""Sound synthesis in numpy. No samples: every sound is built from oscillators and noise here.

All functions return mono float64 arrays at SR. Times are in seconds, frequencies in Hz.
Building blocks: oscillators (band-limited with polyBLEP), envelopes, zero-phase FFT filters, and a
set of instruments an episode can combine (pluck, bell, chirp, thump, click, hum, sizzle).
"""

from __future__ import annotations

import numpy as np

SR = 48_000


def n_samples(dur: float) -> int:
    return max(1, int(round(dur * SR)))


def midi_hz(m):
    return 440.0 * 2.0 ** ((np.asarray(m, dtype=float) - 69.0) / 12.0)


def _freq_array(freq, n: int) -> np.ndarray:
    f = np.asarray(freq, dtype=float)
    return np.full(n, float(f)) if f.ndim == 0 else np.interp(np.arange(n), np.linspace(0, n - 1, len(f)), f)


def _phase(freq, n: int, phase0: float = 0.0) -> np.ndarray:
    """Phase in cycles (not radians), starting at phase0."""
    f = _freq_array(freq, n)
    return phase0 + np.concatenate([[0.0], np.cumsum(f[:-1])]) / SR


# ----------------------------------------------------------------------- oscillators

def sine(freq, dur: float, phase0: float = 0.0) -> np.ndarray:
    n = n_samples(dur)
    return np.sin(2 * np.pi * _phase(freq, n, phase0))


def _polyblep(t: np.ndarray, dt: np.ndarray) -> np.ndarray:
    """polyBLEP residual for a unit step at phase 0, for phase t in [0, 1) and increment dt."""
    out = np.zeros_like(t)
    a = t < dt
    x = t[a] / dt[a]
    out[a] = x + x - x * x - 1.0
    b = t > 1.0 - dt
    x = (t[b] - 1.0) / dt[b]
    out[b] = x * x + x + x + 1.0
    return out


def saw(freq, dur: float, phase0: float = 0.0) -> np.ndarray:
    n = n_samples(dur)
    f = _freq_array(freq, n)
    ph = _phase(f, n, phase0) % 1.0
    dt = np.clip(f / SR, 1e-9, 0.5)
    return 2.0 * ph - 1.0 - _polyblep(ph, dt)


def pulse(freq, dur: float, duty: float = 0.5, phase0: float = 0.0) -> np.ndarray:
    """Band-limited pulse wave (the chiptune square at duty 0.5, thinner at 0.25 or 0.125)."""
    n = n_samples(dur)
    f = _freq_array(freq, n)
    ph = _phase(f, n, phase0) % 1.0
    dt = np.clip(f / SR, 1e-9, 0.5)
    a = 2.0 * ph - 1.0 - _polyblep(ph, dt)
    ph2 = (ph + 1.0 - duty) % 1.0
    b = 2.0 * ph2 - 1.0 - _polyblep(ph2, dt)
    return a - b  # zero mean, peak to peak 2 (+-1 at duty 0.5)


def triangle(freq, dur: float, phase0: float = 0.0) -> np.ndarray:
    n = n_samples(dur)
    ph = _phase(freq, n, phase0 + 0.25) % 1.0
    return 4.0 * np.abs(ph - 0.5) - 1.0


def noise(dur: float, seed: int = 0) -> np.ndarray:
    return np.random.default_rng(seed).standard_normal(n_samples(dur))


# ----------------------------------------------------------------------- envelopes

def adsr(dur: float, a: float = 0.005, d: float = 0.08, s: float = 0.6, r: float = 0.1) -> np.ndarray:
    """Attack, decay, sustain, release over `dur` seconds (release included at the end)."""
    n = n_samples(dur)
    t = np.arange(n) / SR
    rel_start = max(dur - r, a + d)
    env = np.where(t < a, t / max(a, 1e-6),
                   np.where(t < a + d, 1.0 - (1.0 - s) * (t - a) / max(d, 1e-6), s))
    tail = t >= rel_start
    env[tail] *= np.clip(1.0 - (t[tail] - rel_start) / max(r, 1e-6), 0.0, 1.0)
    return env


def decay(dur: float, tau: float, attack: float = 0.002) -> np.ndarray:
    n = n_samples(dur)
    t = np.arange(n) / SR
    return np.minimum(1.0, t / max(attack, 1e-6)) * np.exp(-t / tau)


def fade(x: np.ndarray, fin: float = 0.005, fout: float = 0.005) -> np.ndarray:
    y = x.copy()
    a, b = min(len(y), n_samples(fin)), min(len(y), n_samples(fout))
    y[:a] *= np.linspace(0, 1, a)
    y[len(y) - b:] *= np.linspace(1, 0, b)
    return y


# ----------------------------------------------------------------------- filters

def fft_filter(x: np.ndarray, kind: str, f0: float, f1: float | None = None, order: int = 2) -> np.ndarray:
    """Zero-phase Butterworth-shaped filter applied in the frequency domain.
    kind: 'low', 'high' or 'band' (f0..f1)."""
    n = len(x)
    pad = n + SR // 4
    X = np.fft.rfft(x, n=pad)
    f = np.fft.rfftfreq(pad, 1.0 / SR)
    f = np.maximum(f, 1e-3)
    if kind == "low":
        H = 1.0 / np.sqrt(1.0 + (f / f0) ** (2 * order))
    elif kind == "high":
        H = 1.0 / np.sqrt(1.0 + (f0 / f) ** (2 * order))
    elif kind == "band":
        H = (1.0 / np.sqrt(1.0 + (f0 / f) ** (2 * order))) / np.sqrt(1.0 + (f / f1) ** (2 * order))
    else:
        raise ValueError(kind)
    return np.fft.irfft(X * H, n=pad)[:n]


def one_pole_smooth(x: np.ndarray, seconds: float) -> np.ndarray:
    """Moving-average smoothing (for control signals), same length."""
    k = max(1, int(seconds * SR))
    c = np.cumsum(np.concatenate([np.zeros(k), x]))
    return (c[k:] - c[:-k]) / k


# ----------------------------------------------------------------------- instruments

def pluck(freq: float, dur: float, brightness: float = 0.5, decay_s: float = 0.6, seed: int = 0) -> np.ndarray:
    """Karplus-Strong plucked string, vectorised one period at a time."""
    n = n_samples(dur)
    L = max(2, int(round(SR / freq)))
    rng = np.random.default_rng(seed)
    burst = rng.uniform(-1, 1, L)
    burst = fft_filter(np.tile(burst, 3), "low", 800 + 6000 * brightness)[L:2 * L]
    per_period = np.exp(-L / (decay_s * SR))
    out = np.empty(n + L)
    out[:L] = burst
    prev_last = 0.0
    i = L
    while i < n + L:
        prev = out[i - L:i]
        shifted = np.concatenate([[prev_last], prev[:-1]])
        blk = per_period * 0.5 * (prev + shifted)
        take = min(L, n + L - i)
        out[i:i + take] = blk[:take]
        prev_last = prev[-1]
        i += L
    y = out[:n]
    return fade(y / (np.max(np.abs(y)) + 1e-12), 0.001, 0.02)


def fm_bell(freq: float, dur: float = 2.5, ratio: float = 3.5, index: float = 2.2, tau: float = 0.9) -> np.ndarray:
    """A bell from two-operator FM. An inharmonic ratio gives the metallic ring."""
    n = n_samples(dur)
    t = np.arange(n) / SR
    env = np.exp(-t / tau) * np.minimum(1, t / 0.002)
    ienv = index * np.exp(-t / (tau * 0.35))
    mod = np.sin(2 * np.pi * freq * ratio * t)
    y = np.sin(2 * np.pi * freq * t + ienv * mod)
    y += 0.35 * np.sin(2 * np.pi * freq * 2.76 * t) * np.exp(-t / (tau * 0.5))
    return y * env / 1.35


def chirp(f0: float, f1: float, dur: float, shape: str = "exp") -> np.ndarray:
    n = n_samples(dur)
    u = np.linspace(0, 1, n)
    f = f0 * (f1 / f0) ** u if shape == "exp" else f0 + (f1 - f0) * u
    return sine(f, dur)


def thump(dur: float = 0.25, f0: float = 140.0, f1: float = 45.0, seed: int = 0) -> np.ndarray:
    """A soft low hit: a falling sine plus a little filtered noise."""
    body = chirp(f0, f1, dur) * decay(dur, dur / 4, 0.001)
    grit = fft_filter(noise(dur, seed), "low", 900) * decay(dur, 0.02, 0.0005) * 0.4
    return body + grit


def click(dur: float = 0.006, freq: float = 3500.0, seed: int = 0) -> np.ndarray:
    return fft_filter(noise(dur, seed), "band", freq * 0.6, freq * 1.6) * decay(dur, dur / 3, 0.0002)


def beep(freq: float = 2093.0, dur: float = 0.09) -> np.ndarray:
    """An appliance keypad beep: a soft square with a quick envelope."""
    return pulse(freq, dur, 0.5) * adsr(dur, 0.002, 0.02, 0.8, 0.02) * 0.6


def hum(dur: float, mains: float = 60.0, seed: int = 0, low: float = 1.0) -> np.ndarray:
    """A transformer and fan hum: mains harmonics with a slow wobble, plus filtered air noise.
    low scales the first three harmonics (under 200 Hz), e.g. 0.3 for a mix that has to read on phones."""
    n = n_samples(dur)
    t = np.arange(n) / SR
    rng = np.random.default_rng(seed)
    y = np.zeros(n)
    for k, amp in ((1, 0.25 * low), (2, 1.0 * low), (3, 0.35 * low), (4, 0.3), (6, 0.12), (8, 0.06)):
        wob = 1 + 0.002 * np.sin(2 * np.pi * (0.3 + 0.1 * k) * t + rng.uniform(0, 6))
        y += amp * np.sin(2 * np.pi * mains * k * t * wob + rng.uniform(0, 6))
    air = fft_filter(noise(dur, seed + 1), "band", 180, 2200) * 0.35
    am = 1 + 0.15 * np.sin(2 * np.pi * 2.0 * mains * t)
    return (y * 0.55 + air) * am / 2.0


def sizzle(dur: float, density: float = 400.0, seed: int = 0) -> np.ndarray:
    """Fat crackling: sparse random pops over a hiss, high-passed."""
    n = n_samples(dur)
    rng = np.random.default_rng(seed)
    pops = np.zeros(n)
    k = rng.poisson(density * dur)
    pos = rng.integers(0, n, k)
    pops[pos] = rng.uniform(-1, 1, k) * rng.uniform(0.3, 1.0, k) ** 2
    pops = fft_filter(pops, "band", 1500, 9000) * 6.0
    hiss = fft_filter(noise(dur, seed + 7), "band", 3000, 12000) * 0.25
    return pops + hiss


def whirr(dur: float, seed: int = 0, whine: float = 420.0) -> np.ndarray:
    """A small motor turning something (a turntable, a fan): a gear whine with a slow wobble and a
    rotation flutter, over filtered air. Mostly above 200 Hz, so it carries on phone speakers."""
    n = n_samples(dur)
    t = np.arange(n) / SR
    rng = np.random.default_rng(seed)
    wob = 1 + 0.01 * np.sin(2 * np.pi * 0.7 * t + rng.uniform(0, 6))
    y = 0.6 * np.sin(2 * np.pi * whine * t * wob) + 0.25 * np.sin(2 * np.pi * 2 * whine * t * wob + 1.0)
    y += 0.12 * np.sin(2 * np.pi * 3.02 * whine * t)
    flutter = 0.75 + 0.25 * np.sin(2 * np.pi * 6.0 * t) ** 2
    air = fft_filter(noise(dur, seed + 1), "band", 500, 3500) * 0.35
    return fade((y * flutter + air) / 1.2, 0.03, 0.06)


def hit(dur: float = 1.2, seed: int = 0, tail: float = 0.09) -> np.ndarray:
    """A broadband impact for a payoff: a noise burst across the spectrum, a short low body and a
    bright ring. `tail` is the burst's decay time; longer reads louder over a 400 ms window."""
    burst = noise(dur, seed) * decay(dur, tail, 0.0008)
    burst = fft_filter(burst, "high", 120) * 0.9
    body = chirp(240, 70, dur) * decay(dur, 0.12, 0.001) * 0.8
    ring = (sine(1760, dur) + 0.6 * sine(2637, dur)) * decay(dur, 0.35, 0.002) * 0.25
    y = burst + body + ring
    return y / (np.max(np.abs(y)) + 1e-12)


def blip(freq: float, dur: float = 0.12, duty: float = 0.25) -> np.ndarray:
    """A short chiptune note."""
    return pulse(freq, dur, duty) * decay(dur, dur / 3, 0.002)
