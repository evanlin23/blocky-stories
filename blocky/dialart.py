"""Ep45's dials: the little round clocks over every head. PIL and numpy only (the repo's Python, the tests and
Blender's Python can all draw them). Every dial is our own design: a cream face, a coloured arc ring round the edge
that empties as the time runs down (coral at long times, honey gold under an hour), a centre readout in blocky
segment digits drawn here from rounded bars (not a font), and a row of small pips under the digits for the unit
(1 seconds, 2 minutes, 3 hours, 4 days, 5 months, 6 years). Never letters. At zero the face glows soft gold.

`dial(val, unit, frac, glow, vis, tone)` returns an (N, N, 3) float array, row 0 at the top.
"""

from __future__ import annotations

import math
from functools import lru_cache

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

CREAM = (243, 234, 214)
TRACK = (226, 214, 187)
CORAL = (255, 127, 106)
HONEY = (227, 165, 58)
BRASS = (184, 145, 62)
INK = (58, 46, 36)
GOLD = (255, 178, 52)
GOLD_HI = (255, 214, 110)
SEGS = {
    "0": "abcdef", "1": "bc", "2": "abged", "3": "abgcd", "4": "fgbc", "5": "afgcd",
    "6": "afgedc", "7": "abc", "8": "abcdefg", "9": "abcdfg",
}


def _mix(a, b, u):
    return tuple(int(round(x + (y - x) * u)) for x, y in zip(a, b))


def _digit(d: ImageDraw.ImageDraw, ch: str, x: float, y: float, w: float, h: float, t: float, fill) -> None:
    """One blocky seven-segment digit, its top-left at (x, y): rounded bars with small gaps at the corners."""
    g = t * 0.22
    r = t * 0.45
    xs0, xs1 = x + t * 0.5 + g, x + w - t * 0.5 - g
    ym, y0, y1 = y + h / 2, y + t * 0.5, y + h - t * 0.5
    bars = {
        "a": (xs0, y0 - t / 2, xs1, y0 + t / 2), "g": (xs0, ym - t / 2, xs1, ym + t / 2),
        "d": (xs0, y1 - t / 2, xs1, y1 + t / 2),
        "f": (x, y + g, x + t, ym - g), "b": (x + w - t, y + g, x + w, ym - g),
        "e": (x, ym + g, x + t, y + h - g), "c": (x + w - t, ym + g, x + w, y + h - g),
    }
    for s in SEGS.get(ch, ""):
        d.rounded_rectangle(bars[s], radius=r, fill=fill)


@lru_cache(maxsize=512)
def dial(val: str = "", unit: int = 0, frac: float = 1.0, glow: float = 0.0, vis: float = 1.0,
         tone: str = "coral", n: int = 512, mark: str = "") -> np.ndarray:
    k = 2                                   # supersample
    N = n * k
    c = N / 2
    R = N / 2
    im = Image.new("RGB", (N, N), CREAM)
    d = ImageDraw.Draw(im)
    ink_a = max(0.0, vis) * (1.0 - glow)    # how much of the readout shows
    if ink_a > 0.01:
        arc_c = HONEY if tone == "honey" else CORAL
        box = [c - 0.88 * R, c - 0.88 * R, c + 0.88 * R, c + 0.88 * R]
        wd = int(0.13 * R)
        d.ellipse(box, outline=_mix(CREAM, TRACK, ink_a), width=wd)
        if frac > 0.004:
            a0, a1 = -90, -90 + 360 * min(1.0, frac)
            col = _mix(CREAM, arc_c, ink_a)
            d.arc(box, a0, a1, fill=col, width=wd)
            for ang in (a0, a1) if frac < 0.999 else (a0,):
                px, py = c + 0.88 * R * math.cos(math.radians(ang)), c + 0.88 * R * math.sin(math.radians(ang))
                d.ellipse([px - wd / 2, py - wd / 2, px + wd / 2, py + wd / 2], fill=col)
        val = str(val)
        if val:
            nd = len(val)
            h = 0.5 * R * (1.0 if nd <= 2 else 0.8)
            w = 0.27 * R * (1.0 if nd <= 2 else 0.8)
            t = 0.085 * R * (1.0 if nd <= 2 else 0.85)
            gap = 0.1 * R
            tot = nd * w + (nd - 1) * gap
            x0, y0 = c - tot / 2, c - 0.5 * h - 0.04 * R
            col = _mix(CREAM, INK, ink_a)
            for i, ch in enumerate(val):
                _digit(d, ch, x0 + i * (w + gap), y0, w, h, t, col)
        if unit:
            pr = 0.052 * R
            sp = 0.14 * R
            x0 = c - (unit - 1) * sp / 2
            py = c + 0.5 * R
            col = _mix(CREAM, BRASS, ink_a)
            for i in range(unit):
                px = x0 + i * sp
                d.ellipse([px - pr, py - pr, px + pr, py + pr], fill=col)
    arr = np.asarray(im.resize((n, n), Image.LANCZOS), dtype=np.float32) / 255.0
    if glow > 0.01:                          # a soft warm gold glow, brightest in the middle
        yy, xx = np.mgrid[0:n, 0:n].astype(np.float32)
        rr = np.hypot(xx - n / 2, yy - n / 2) / (n / 2)
        g = np.clip(1.0 - rr * 0.75, 0, 1) ** 1.3
        gold = np.array(GOLD, np.float32) / 255.0
        hi = np.array(GOLD_HI, np.float32) / 255.0
        tgt = gold[None, None, :] * (1 - g[..., None]) + hi[None, None, :] * g[..., None]
        arr = arr * (1 - glow) + tgt * glow
        if mark:                             # opt-in: a deep amber digit on the glow, so a zero reads as a zero
            m = Image.new("L", (n * 2, n * 2), 0)
            md = ImageDraw.Draw(m)
            R2 = n
            nd = len(mark)
            h, w, t = 1.0 * R2, 0.6 * R2, 0.15 * R2
            gp = 0.16 * R2
            tot = nd * w + (nd - 1) * gp
            for i, ch in enumerate(mark):
                _digit(md, ch, R2 - tot / 2 + i * (w + gp), R2 - h / 2, w, h, t, 255)
            ma = np.asarray(m.resize((n, n), Image.LANCZOS), dtype=np.float32)[..., None] / 255.0 * min(1.0, glow * 1.2)
            arr = arr * (1 - ma) + (np.array((120, 62, 6), np.float32) / 255.0)[None, None, :] * ma
    return np.clip(arr, 0, 1)
