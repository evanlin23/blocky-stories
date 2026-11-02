"""The photo-booth prints (PIL only): every frame of every strip is drawn here, then set.py puts them on planes.

A print is the booth's camera looking at the bench from the front: the plum velvet with its centre seam behind, Wren
at the left and me at the right, and (in strips 1 to 4) the Third's faded sepia print behind us. The Third never
moves: its right hand is on the seam at z = 1.5 in every frame of every strip. Only how much of it shows changes,
and that only because Wren and I sit further apart each time (`sep`, metres from the middle to each head).
"""
from __future__ import annotations

import math
import random

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

from blocky import faces

PPM = 400                                  # pixels per metre in a frame
HALF_X, Z_TOP, Z_BOT = 1.1, 2.33, 0.41     # the frame's field: x from -1.1 to 1.1, z from 0.41 to 2.33
FW, FH = int(2 * HALF_X * PPM), int(round((Z_TOP - Z_BOT) * PPM))
PAD = 44
SW, SH = FW + 2 * PAD, 4 * FH + 5 * PAD
PAPER = (236, 230, 216)

VELVET, VELVET_D = (84, 34, 66), (46, 18, 38)
SUIT, SUIT2, SKIN3, SHIRT3, INK3 = (84, 60, 40), (112, 82, 56), (150, 118, 84), (150, 128, 98), (18, 12, 9)

WREN = {"skin": "#e9bd9a", "dress": (47, 107, 70), "hair": (128, 62, 38), "face": {"eyes": "classic", "brows": True}}
ME = {"skin": "#f1c9a0", "dress": (38, 50, 79), "hair": (46, 31, 22), "face": {"eyes": "round", "brows": True}}

# per strip: (sep, level of the Third that shows: 1 hand, 2 arm and shoulder, 3 the whole body, 4 as 3), wide smile
STRIPS = {1: (0.62, 1, False), 2: (0.70, 2, False), 3: (0.79, 3, False), 4: (0.87, 3, True), 5: (0.50, 0, False)}
# the jitter inside a strip (a few cm: people shift between pictures) and the faces in each frame
JIT = [(0.0, 0.0), (0.012, -0.008), (-0.008, 0.01), (0.015, 0.012)]
EXPR = {1: [("angry", "worried"), ("neutral", "worried"), ("angry", "neutral"), ("neutral", "worried")],
        2: [("angry", "worried"), ("worried", "neutral"), ("neutral", "worried"), ("angry", "scared")],
        3: [("neutral", "worried"), ("angry", "neutral"), ("worried", "worried"), ("scared", "scared")],
        4: [("blank", "blank"), ("worried", "scared"), ("scared", "worried"), ("terrified", "terrified")],
        5: [("smirk", "smirk"), ("fish", "smirk"), ("squeeze", "fish"), ("squeeze", "squeeze")]}


def P(x, z):
    return ((x + HALF_X) * PPM, (Z_TOP - z) * PPM)


def R(d, x0, z0, x1, z1, fill, r=0.0):
    a, b = P(x0, z1), P(x1, z0)
    if r:
        d.rounded_rectangle([a[0], a[1], b[0], b[1]], radius=r * PPM, fill=fill)
    else:
        d.rectangle([a[0], a[1], b[0], b[1]], fill=fill)


def poly(d, pts, fill):
    d.polygon([P(x, z) for x, z in pts], fill=fill)


def limb(d, a, b, w, fill):
    """A thick line between two points (metres)."""
    ax, az = a
    bx, bz = b
    L = math.hypot(bx - ax, bz - az) or 1.0
    nx, nz = -(bz - az) / L * w / 2, (bx - ax) / L * w / 2
    poly(d, [(ax + nx, az + nz), (bx + nx, bz + nz), (bx - nx, bz - nz), (ax - nx, az - nz)], fill)


def velvet(rng):
    base = np.zeros((FH, FW, 3), np.float32)
    base[:] = VELVET
    ys, xs = np.mgrid[0:FH, 0:FW]
    # soft vertical folds and a pool of light from above
    folds = 0.07 * np.sin(xs / 31.0 + 2 * np.sin(xs / 97.0)) + 0.04 * np.sin(xs / 13.0)
    pool = 1.0 - 0.45 * np.clip(((xs - FW / 2) / (FW * 0.62)) ** 2 + ((ys - FH * 0.42) / (FH * 0.8)) ** 2, 0, 1)
    k = (1.0 + folds) * pool
    base *= k[..., None]
    base += rng.normal(0, 3.0, base.shape)
    im = Image.fromarray(np.clip(base, 0, 255).astype(np.uint8))
    d = ImageDraw.Draw(im)
    sx = P(0, 0)[0]
    d.rectangle([sx - 4, 0, sx + 3, FH], fill=VELVET_D)                      # the seam
    d.rectangle([sx - 7, 0, sx - 5, FH], fill=tuple(int(c * 0.78) for c in VELVET))
    return im


def third(level, wide, rng):
    """The Third as a sepia print on a transparent layer. Its right hand is at the same place whatever the level."""
    lay = Image.new("RGBA", (FW, FH), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    if level >= 3:
        for x0, x1 in ((-0.27, -0.03), (0.03, 0.27)):
            R(d, x0, 0.30, x1, 1.2, SUIT)
        R(d, -0.31, 1.12, 0.31, 2.1, SUIT, 0.03)                              # torso
        poly(d, [(-0.31, 2.1), (-0.36, 1.98), (-0.05, 2.17), (0.05, 2.17), (0.36, 1.98), (0.31, 2.1)], SUIT)
        R(d, -0.13, 1.14, 0.13, 2.08, SUIT2)                                  # the waistcoat
        poly(d, [(-0.06, 2.1), (0.06, 2.1), (0.0, 1.84)], SHIRT3)
        R(d, -0.018, 1.45, 0.018, 1.95, INK3)                                 # the tie
        R(d, 0.31, 0.88, 0.48, 2.0, SUIT, 0.03)                               # the left arm, straight down
        R(d, 0.32, 0.72, 0.47, 0.9, SKIN3, 0.03)
        R(d, -0.075, 2.08, 0.075, 2.2, SKIN3)                                 # neck
        # the lower face: a jaw, and the slot smile that opens onto black
        R(d, -0.22, 2.14, 0.22, 2.4, SKIN3, 0.04)
        sm = 0.30 if wide else 0.20
        th = 0.034 if wide else 0.02
        pts = [P(-sm + 2 * sm * i / 24, 2.27 - (0.045 if wide else 0.02) * (2 * (i / 24 - 0.5)) ** 2) for i in range(25)]
        d.line(pts, fill=(5, 3, 3), width=int(th * PPM), joint="curve")
        if wide:
            for ex in (-1, 1):
                x, y = pts[0] if ex < 0 else pts[-1]
                d.ellipse([x - th * PPM * 0.5, y - th * PPM * 0.5, x + th * PPM * 0.5, y + th * PPM * 0.5], fill=(5, 3, 3))
    if level >= 2:
        poly(d, [(-0.31, 1.82), (-0.31, 2.1), (-0.05, 2.17), (0.0, 2.1), (0.0, 1.82)], SUIT)   # one shoulder
        limb(d, (-0.62, 1.50), (-0.31, 1.98), 0.2, SUIT)                       # the upper arm
        R(d, -0.72, 1.40, -0.5, 1.6, SUIT, 0.06)                              # the elbow
        R(d, -0.62, 1.405, -0.17, 1.595, SUIT)                                # the forearm
    # the hand and its cuff: the same pixels in every frame of every strip
    R(d, -0.17, 1.408, -0.10, 1.592, SHIRT3)
    R(d, -0.10, 1.40, 0.07, 1.60, SKIN3, 0.02)
    for z, ln in ((1.585, 0.19), (1.527, 0.235), (1.469, 0.215), (1.413, 0.16)):
        R(d, 0.06, z - 0.021, 0.07 + ln, z + 0.021, SKIN3, 0.02)
    poly(d, [(-0.07, 1.6), (-0.01, 1.6), (0.02, 1.71), (-0.04, 1.73)], SKIN3)  # the thumb
    arr = np.asarray(lay).astype(np.float32)
    g = rng.normal(0, 9.0, arr.shape[:2])[..., None]
    arr[..., :3] = np.clip(arr[..., :3] + g, 0, 255)
    arr[..., 3] = np.where(arr[..., 3] > 0, 250, 0)
    return Image.fromarray(arr.astype(np.uint8))


def face_crop(face, skin, expr, width_px):
    im = faces.face_image(face, skin, expr).crop((faces.FX0, faces.FY0, faces.FX1, faces.FY1))
    return im.resize((int(width_px), int(width_px * im.height / im.width)), Image.LANCZOS)


def sitter(img, spec, cx, expr, wren):
    d = ImageDraw.Draw(img)
    dress = spec["dress"]
    shade = tuple(int(c * 0.8) for c in dress)
    R(d, cx - 0.476, 0.55, cx + 0.476, 1.34, shade, 0.04)                      # the arms
    R(d, cx - 0.238, 0.55, cx + 0.238, 1.38, dress, 0.03)                       # the torso
    skin = tuple(int(spec["skin"][i:i + 2], 16) for i in (1, 3, 5))
    R(d, cx - 0.476, 0.53, cx - 0.25, 0.7, skin, 0.03)                         # hands
    R(d, cx + 0.25, 0.53, cx + 0.476, 0.7, skin, 0.03)
    pants = dress if wren else (30, 36, 56)
    R(d, cx - 0.238, 0.5, cx + 0.238, 0.86, pants, 0.03)                        # the thighs, coming at the lens
    R(d, cx - 0.238, 0.43, cx + 0.238, 0.56, (30, 24, 24), 0.03)
    if wren:
        R(d, cx - 0.05, 1.34, cx + 0.05, 1.4, skin)
    else:
        poly(d, [(cx - 0.08, 1.38), (cx + 0.08, 1.38), (cx, 1.12)], (236, 232, 220))   # the white shirt
        R(d, cx - 0.025, 0.92, cx + 0.025, 1.3, (200, 150, 40))                          # the mustard tie
    hair = spec["hair"]
    hw = 0.37
    if wren:
        R(d, cx - 0.21, 1.2, cx + 0.21, 1.86, hair, 0.05)                    # the bob behind
    R(d, cx - hw / 2, 1.38, cx + hw / 2, 1.78, skin, 0.07)                    # the head
    fc = face_crop(spec["face"], spec["skin"], expr, hw * PPM * 0.9)
    x, y = P(cx, 1.58)
    img.paste(fc, (int(x - fc.width / 2), int(y - fc.height / 2)))
    d = ImageDraw.Draw(img)
    R(d, cx - 0.2, 1.72, cx + 0.2, 1.85, hair, 0.05)                          # the cap of hair
    if wren:
        R(d, cx - 0.21, 1.46, cx - 0.17, 1.8, hair, 0.02)
        R(d, cx + 0.17, 1.46, cx + 0.21, 1.8, hair, 0.02)
        R(d, cx + 0.1, 1.78, cx + 0.15, 1.82, (200, 150, 60))               # the brass clip
    else:
        R(d, cx - 0.16, 1.69, cx + 0.05, 1.77, hair, 0.03)                    # the swept fringe


def frame(strip, k, rng):
    """Frame k (0..3) of strip 1..5."""
    sep, level, wide = STRIPS[strip]
    jw, jm = JIT[k]
    im = velvet(rng).convert("RGBA")
    if level:
        fig = third(level, wide or (strip == 3 and k == 3), rng)   # strip 3's fourth picture: the smile is wider
        im.alpha_composite(fig)
    im = im.convert("RGB")
    e_w, e_m = EXPR[strip][k]
    sitter(im, WREN, -(sep + jw), e_w, True)
    sitter(im, ME, sep + jm, e_m, False)
    a = np.asarray(im).astype(np.float32)
    ys, xs = np.mgrid[0:FH, 0:FW]
    vig = 1.0 - 0.38 * (((xs - FW / 2) / (FW / 2)) ** 2 * 0.6 + ((ys - FH / 2) / (FH / 2)) ** 2 * 0.6)
    a *= vig[..., None]
    a += rng.normal(0, 4.0, a.shape)
    a[..., 0] *= 1.04
    a[..., 2] *= 0.93                                                         # an old print's warmth
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(0.7))


def strip(n, frames=(0, 1, 2, 3)):
    """Strip n (1..5): up to four frames on white paper, top to bottom."""
    rng = np.random.default_rng(100 + n)
    out = Image.new("RGB", (SW, len(frames) * FH + (len(frames) + 1) * PAD), PAPER)
    for i, k in enumerate(frames):
        out.paste(frame(n, k, rng), (PAD, PAD + i * (FH + PAD)))
    a = np.asarray(out).astype(np.float32)
    a += rng.normal(0, 3.0, a.shape)
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))


def back(tally=False, size=(SW, 2 * FH + 3 * PAD)):
    """The paper side of a half strip: plain, or with the tally (three short upright strokes in faded brown)."""
    rng = np.random.default_rng(7)
    im = Image.new("RGB", size, (196, 188, 168))
    if tally:
        d = ImageDraw.Draw(im)
        cx, cy = size[0] // 2, int(size[1] * 0.46)
        for i in (-1, 0, 1):
            x = cx + i * 120 + rng.integers(-6, 6)
            d.line([(x, cy - 170), (x + int(rng.integers(-8, 8)), cy + 170)], fill=(112, 74, 46), width=46)
            d.ellipse([x - 23, cy - 193, x + 23, cy - 147], fill=(139, 96, 62))
            d.ellipse([x - 23, cy + 147, x + 23, cy + 193], fill=(139, 96, 62))
    a = np.asarray(im).astype(np.float32) + rng.normal(0, 4, (size[1], size[0], 3))
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(1.2 if tally else 0.5))


if __name__ == "__main__":
    import sys
    out = sys.argv[1]
    for n in range(1, 6):
        strip(n).resize((SW // 4, SH // 4)).save(f"{out}/strip{n}.png")
