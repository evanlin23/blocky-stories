"""Mixing and mastering: buses, panning, an EBU R128 / ITU-R BS.1770-4 loudness meter, a true-peak
meter, a lookahead limiter, and `master()` to hit -14 LUFS with true peak at or below the ceiling.

The meter is checked against ffmpeg's ebur128 filter in the tests, and the
encoder re-measures the finished MP4 with ffmpeg, so a mix can't ship off target.
"""

from __future__ import annotations

import numpy as np

from blocky.synth import SR, fft_filter

TARGET_LUFS = -14.0
TP_CEILING = -1.5  # dBTP before AAC: AAC adds up to about half a dB on transients, the gate is -1


class Mix:
    """Stereo buses of a fixed length. `add` places a mono or stereo sound at a time."""

    def __init__(self, duration: float):
        self.duration = duration
        self.n = int(round(duration * SR))
        self.buses: dict[str, np.ndarray] = {}
        self.bus_gain: dict[str, float] = {}

    def bus(self, name: str, gain_db: float = 0.0) -> np.ndarray:
        if name not in self.buses:
            self.buses[name] = np.zeros((self.n, 2))
            self.bus_gain[name] = gain_db
        return self.buses[name]

    def add(self, bus: str, t: float, sig: np.ndarray, gain_db: float = 0.0, pan: float = 0.0) -> None:
        """pan: -1 left .. +1 right (constant power)."""
        buf = self.bus(bus)
        start = int(round(t * SR))
        if start >= self.n or len(sig) == 0:
            return
        if start < 0:
            sig = sig[-start:]
            start = 0
        end = min(self.n, start + len(sig))
        g = 10 ** (gain_db / 20)
        if sig.ndim == 1:
            th = (np.clip(pan, -1, 1) + 1) * np.pi / 4
            buf[start:end, 0] += sig[: end - start] * g * np.cos(th) * np.sqrt(2)
            buf[start:end, 1] += sig[: end - start] * g * np.sin(th) * np.sqrt(2)
        else:
            buf[start:end] += sig[: end - start] * g

    def duck(self, bus: str, keys: list[str], depth_db: float = 8.0, attack: float = 0.02, release: float = 0.35,
             threshold_db: float = -50.0, knee_db: float = 12.0) -> np.ndarray:
        """Sidechain ducking: turn `bus` down by up to depth_db while any bus in `keys` is sounding.
        The keys' level (5 ms RMS, after their bus gains) sets how far: none below threshold_db, the
        full depth from threshold_db + knee_db up. The gain falls with time constant `attack` and
        recovers with `release`. Call it after every key sound has been added. Returns the gain curve
        (linear, one value per sample), which is also kept in `self.duck_gain[bus]`."""
        if bus not in self.buses:
            return np.ones(self.n)
        key = np.zeros(self.n)
        for k in keys:
            if k in self.buses:
                key += self.buses[k].mean(axis=1) * 10 ** (self.bus_gain[k] / 20)
        blk = SR // 200  # 5 ms control blocks
        nb = -(-self.n // blk)
        sq = np.pad(key**2, (0, nb * blk - self.n)).reshape(nb, blk).mean(axis=1)
        level = 10 * np.log10(np.maximum(sq, 1e-20))
        target = -depth_db * np.clip((level - threshold_db) / knee_db, 0.0, 1.0)
        a_dn = 1 - np.exp(-1 / (attack * 200))
        a_up = 1 - np.exp(-1 / (release * 200))
        g = np.empty(nb)
        cur = 0.0
        for i, tgt in enumerate(target):  # one-pole, faster down than up (200 steps a second)
            cur += (tgt - cur) * (a_dn if tgt < cur else a_up)
            g[i] = cur
        curve = 10 ** (np.interp(np.arange(self.n), np.arange(nb) * blk + blk / 2, g) / 20)
        self.buses[bus] *= curve[:, None]
        if not hasattr(self, "duck_gain"):
            self.duck_gain = {}
        self.duck_gain[bus] = curve
        return curve

    def stems(self) -> dict[str, np.ndarray]:
        return {k: v * 10 ** (self.bus_gain[k] / 20) for k, v in self.buses.items()}

    def sum(self) -> np.ndarray:
        out = np.zeros((self.n, 2))
        for v in self.stems().values():
            out += v
        return out


# ----------------------------------------------------------------------- metering

# ITU-R BS.1770-4 K-weighting at 48 kHz: a high shelf, then the RLB high-pass.
_K1 = ([1.53512485958697, -2.69169618940638, 1.19839281085285], [1.0, -1.69065929318241, 0.73248077421585])
_K2 = ([1.0, -2.0, 1.0], [1.0, -1.99004745483398, 0.99007225036621])


def _k_weight(x: np.ndarray) -> np.ndarray:
    """Apply the K filter by multiplying with its exact frequency response (zero-padded, so the
    filter's tail doesn't wrap round)."""
    if SR != 48_000:
        raise ValueError("K-weighting coefficients are for 48 kHz")
    n = len(x)
    pad = n + SR
    X = np.fft.rfft(x, n=pad, axis=0)
    z = np.exp(-1j * np.pi * np.fft.rfftfreq(pad, 1.0 / SR) / (SR / 2))
    H = np.ones_like(z)
    for b, a in (_K1, _K2):
        H *= (b[0] + b[1] * z + b[2] * z * z) / (a[0] + a[1] * z + a[2] * z * z)
    return np.fft.irfft(X * (H[:, None] if x.ndim == 2 else H), n=pad, axis=0)[:n]


def loudness(x: np.ndarray) -> float:
    """Integrated loudness in LUFS (BS.1770-4: 400 ms blocks, 75% overlap, -70 LUFS absolute gate,
    -10 LU relative gate). x is (n, 2) or mono."""
    x = x if x.ndim == 2 else x[:, None]
    y = _k_weight(x)
    block, hop = int(0.4 * SR), int(0.1 * SR)
    if len(y) < block:
        return -np.inf
    c = np.cumsum(np.concatenate([np.zeros((1, y.shape[1])), y**2]), axis=0)
    starts = np.arange(0, len(y) - block + 1, hop)
    z = (c[starts + block] - c[starts]) / block  # mean square per block per channel
    zsum = z.sum(axis=1)
    lk = -0.691 + 10 * np.log10(np.maximum(zsum, 1e-20))
    keep = lk > -70.0
    if not keep.any():
        return -np.inf
    rel = -0.691 + 10 * np.log10(zsum[keep].mean()) - 10.0
    keep &= lk > rel
    return float(-0.691 + 10 * np.log10(zsum[keep].mean()))


def momentary(x: np.ndarray, hop: float = 0.1) -> tuple[np.ndarray, np.ndarray]:
    """Momentary loudness (BS.1770, 400 ms window, no gating) every `hop` seconds, like ffmpeg's
    ebur128 'M' readings. Returns (window end times, LUFS). Silence reads -120."""
    x = x if x.ndim == 2 else x[:, None]
    y = _k_weight(x)
    block, step = int(0.4 * SR), int(hop * SR)
    c = np.cumsum(np.concatenate([np.zeros((1, y.shape[1])), y**2]), axis=0)
    ends = np.arange(step, len(y) + 1, step)
    starts = np.maximum(0, ends - block)
    z = ((c[ends] - c[starts]) / block).sum(axis=1)
    return ends / SR, np.maximum(-120.0, -0.691 + 10 * np.log10(np.maximum(z, 1e-20)))


def oversample(x: np.ndarray, k: int = 4) -> np.ndarray:
    n = len(x)
    X = np.fft.rfft(x, axis=0)
    return np.fft.irfft(X, n=n * k, axis=0) * k


def true_peak(x: np.ndarray, k: int = 4) -> float:
    """True peak in dBTP from k-times oversampling (in chunks, to bound memory)."""
    peak = 0.0
    step = SR * 5
    for i in range(0, len(x), step):
        seg = x[max(0, i - 64): i + step + 64]
        peak = max(peak, float(np.max(np.abs(oversample(seg, k)))))
    return 20 * np.log10(max(peak, 1e-12))


# ----------------------------------------------------------------------- dynamics

def _sliding_min(g: np.ndarray, w: int) -> np.ndarray:
    """Trailing minimum over w samples (van Herk / Gil-Werman, vectorised)."""
    n = len(g)
    pad = (-(n + w - 1)) % w
    a = np.concatenate([np.ones(w - 1), g, np.ones(pad)])
    blocks = a.reshape(-1, w)
    pre = np.minimum.accumulate(blocks, axis=1).ravel()
    suf = np.minimum.accumulate(blocks[:, ::-1], axis=1)[:, ::-1].ravel()
    idx = np.arange(n)
    return np.minimum(suf[idx], pre[idx + w - 1])


def _box(g: np.ndarray, w: int) -> np.ndarray:
    c = np.cumsum(np.concatenate([np.full(w, g[0]), g]))
    return (c[w:] - c[:-w]) / w


def limit(x: np.ndarray, ceiling_db: float = TP_CEILING, lookahead: float = 0.004, release: float = 0.08) -> np.ndarray:
    """Lookahead peak limiter on the 4x-oversampled peak. The output is delayed by nothing: the
    lookahead is applied to the gain curve instead, so timing stays locked to the picture."""
    ceil = 10 ** (ceiling_db / 20)
    peak = np.abs(oversample(x, 4)).reshape(len(x), 4, x.shape[1]).max(axis=(1, 2))
    need = np.minimum(1.0, ceil / np.maximum(peak, 1e-12))
    L = max(1, int(lookahead * SR))
    # Look ahead: g[n] = min(need[n .. n+L-1]), a forward minimum (a trailing one, run backwards).
    g = _sliding_min(need[::-1], L)[::-1]
    # Smooth it with a trailing L-sample average. Every term in the average at n covers need[n],
    # so the smoothed gain never lets a peak through.
    g = _box(g, L)
    # Release: hold the deepest gain for `release` and ease back, never above what's needed.
    R = max(1, int(release * SR))
    g = np.minimum(g, _box(_sliding_min(g, R), R // 2 or 1))
    return x * g[:, None]


def compress(x: np.ndarray, threshold_db: float = -18.0, ratio: float = 2.0, window: float = 0.05) -> np.ndarray:
    """Gentle RMS bus compressor (glue). Smooth gain from a 50 ms RMS window."""
    m = x.mean(axis=1)
    rms = np.sqrt(np.maximum(_box(m**2, max(1, int(window * SR))), 1e-12))
    level = 20 * np.log10(rms)
    over = np.maximum(0.0, level - threshold_db)
    gain_db = -over * (1 - 1 / ratio)
    g = 10 ** (_box(gain_db, max(1, int(0.03 * SR))) / 20)
    return x * g[:, None]


def master(x: np.ndarray, target: float = TARGET_LUFS, ceiling_db: float = TP_CEILING,
           glue: bool = True) -> tuple[np.ndarray, dict]:
    """High-pass at 25 Hz, glue compression, then iterate gain and limiting until the integrated
    loudness is within 0.05 LU of target and the true peak is at or below the ceiling."""
    y = np.stack([fft_filter(x[:, c], "high", 25.0, order=2) for c in range(2)], axis=1)
    if glue:
        y = compress(y)
    gain_db = 0.0
    for _ in range(6):
        lu = loudness(y)
        gain_db += target - lu
        y = y * 10 ** ((target - lu) / 20)
        y = limit(y, ceiling_db)
        if abs(loudness(y) - target) < 0.05 and true_peak(y) <= ceiling_db + 0.05:
            break
    lu, tp = loudness(y), true_peak(y)
    # gain_db is the static gain applied on top of the raw sum (limiting aside). Stems times this
    # gain sit on the master's scale, which is how the stats compares them.
    return y, {"lufs": round(float(lu), 2), "true_peak_dbtp": round(float(tp), 2), "gain_db": round(float(gain_db), 3)}
