"""The v3 faces (`look.style: "v3"`): flat, drawn on, and pushed hard. PIL only, like faces.py.

What changes from v2 (faces.py): the face is a decal on the flat front of a rounded block head, not a wrap round a
cylinder, so it can be drawn big. Eyes are tall ovals that squash and stretch with the mood (each eye on its own,
so a face can be lopsided), brows are thick bars that fly up or knit hard, mouths open wide onto a dark inside with
teeth and a tongue, and cartoon accents (tear streams, sweat drops, an anger cross, gloom lines, sparkles) sit on
top. Everything is drawn from shapes here: no shading, no gradients (viewers called a shaded close-up face
"creepy", docs/research/2026-11-12-purplehat-study.md), nothing traced from any game's or channel's faces.

The texture covers the head's front: x left to right as the viewer sees it, y top to bottom, transparent where
there's no ink so the skin shows through. The rig maps it onto the front of the head (rig.head_mesh_v3).
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field, replace

from PIL import Image, ImageDraw

from .faces import hexrgb

# the v3 head in rig units (rig.py builds the same): wider than tall, a rounded block
HEAD3_W, HEAD3_H, HEAD3_D = 2.8, 2.3, 2.1
# where the eyes sit and how big they are, as fractions of the face texture (hair3's glasses fit round them)
EYE_RX, EYE_RY, EYE_GAP, EYE_Y = 0.145, 0.185, 0.4, 0.5
TEX3_W = 1024
TEX3_H = int(round(TEX3_W * HEAD3_H / HEAD3_W))
HAIRLINE = 0.13   # the top of the face box a fringe may cover: nothing is drawn above it
SS = 2   # drawn at twice the size, then halved: smooth edges without any blur or shading

WHITE = (252, 252, 248)
INSIDE = (70, 18, 32)       # an open mouth's inside
TONGUE = (236, 96, 120)
TEAR = (110, 200, 255)
TEAR_INK = (40, 110, 190)
SWEAT = (150, 220, 255)
ANGER = (230, 40, 50)
GLOOM = (92, 80, 160)


@dataclass(frozen=True)
class Eye:
    shape: str = "oval"      # oval | happy (^ arc) | shut (flat line) | squeeze (> <) | x | spiral | star | heart
    sx: float = 1.0          # squash and stretch: width and height scale on the base eye
    sy: float = 1.0
    lid: float = 0.0         # 0..1, a flat lid down from the top (squint, bored)
    lid_tilt: float = 0.0    # + tilts the lid's inner end down (angry), - raises it (sad)
    lower: float = 0.0       # 0..1, a lid up from the bottom (smiling cheeks, suspicion)
    pupil: float = 1.0       # pupil size; small is shock, big is soft
    dy: float = 0.0          # move the eye up (-) or down (+), in face heights


@dataclass(frozen=True)
class Brow:
    dy: float = 0.0          # up (-) or down (+) from rest, in face heights
    tilt: float = 0.0        # + raises the inner end (worry), - drops it (anger)
    bend: float = 0.0        # + arches up in the middle, - sags
    w: float = 1.0
    hide: bool = False


@dataclass(frozen=True)
class Mouth:
    shape: str = "smile"     # smile | flat | frown | grin | o | scream | wail | wobble | smirk | teeth | blep | cat
    w: float = 1.0
    h: float = 1.0
    tilt: float = 0.0        # lopsided: + lifts the viewer's right corner
    dx: float = 0.0


@dataclass(frozen=True)
class Face3:
    eyes: tuple = (Eye(), Eye())         # (viewer's left, viewer's right)
    brows: tuple = (Brow(), Brow())
    mouth: Mouth = Mouth()
    accents: tuple = ()                  # tears | stream | sweat | anger | gloom | blush | sparkle | shake


E, B, M = Eye, Brow, Mouth
FACES3: dict[str, Face3] = {
    "neutral": Face3(mouth=M("smile", 0.55, 0.5)),
    "shocked": Face3((E(sx=1.08, sy=1.28, pupil=0.5), E(sx=1.08, sy=1.28, pupil=0.5)),
                     (B(-0.12, 0.1, 0.4), B(-0.12, 0.1, 0.4)), M("o", 1.0, 1.75)),
    "delighted": Face3((E("happy", 1.05, 1.0), E("happy", 1.05, 1.0)), (B(-0.08, 0.0, 0.5), B(-0.08, 0.0, 0.5)),
                       M("grin", 1.35, 1.25), ("blush", "sparkle")),
    "smug": Face3((E(lid=0.52, lower=0.1, pupil=0.85),
                   E(lid=0.4, lower=0.1, pupil=0.85)),
                  (B(0.02, -0.25, 0.1), B(-0.09, 0.15, 0.55)), M("smirk", 0.95, 0.9, tilt=0.6, dx=0.08)),
    "terrified": Face3((E(sx=1.12, sy=1.42, pupil=0.32, dy=-0.02), E(sx=1.12, sy=1.42, pupil=0.32, dy=-0.02)),
                       (B(-0.16, 0.9, -0.2), B(-0.16, 0.9, -0.2)), M("scream", 1.0, 1.3), ("sweat", "shake")),
    "crylaugh": Face3((E("squeeze", 1.1, 1.0), E("squeeze", 1.1, 1.0)), (B(-0.1, 0.55, 0.2), B(-0.1, 0.55, 0.2)),
                      M("grin", 1.5, 1.45), ("tears", "blush")),
    "suspicious": Face3((E(lid=0.58, lower=0.2, pupil=0.8), E(sx=1.05, sy=1.15, pupil=0.55)),
                        (B(0.03, -0.55, 0.0), B(-0.1, 0.2, 0.5)), M("flat", 0.6, 1.0, tilt=-0.35, dx=-0.06)),
    "heartbroken": Face3((E(sy=0.95, lid=0.25, lid_tilt=-0.5, pupil=1.25), E(sy=0.95, lid=0.25, lid_tilt=-0.5, pupil=1.25)),
                         (B(-0.07, 1.0, -0.3), B(-0.07, 1.0, -0.3)), M("wail", 1.1, 1.1), ("stream", "gloom")),
    "determined": Face3((E(sy=0.9, lid=0.32, lid_tilt=0.55, pupil=0.85), E(sy=0.9, lid=0.32, lid_tilt=0.55, pupil=0.85)),
                        (B(0.04, -0.75, 0.0, 1.1), B(0.04, -0.75, 0.0, 1.1)), M("teeth", 1.0, 1.25)),
    "furious": Face3((E(sy=0.85, lid=0.42, lid_tilt=0.9, pupil=0.45), E(sy=0.85, lid=0.42, lid_tilt=0.9, pupil=0.45)),
                     (B(0.06, -1.1, 0.0, 1.15), B(0.06, -1.1, 0.0, 1.15)), M("scream", 1.25, 1.0), ("anger",)),
    "nervous": Face3((E(sy=1.05, pupil=0.6), E(sy=1.05, pupil=0.6)), (B(-0.05, 0.7, 0.0), B(-0.05, 0.7, 0.0)),
                     M("wobble", 1.0, 1.0), ("sweat",)),
    "disgusted": Face3((E(lid=0.55, lower=0.35, pupil=0.75), E("squeeze", 0.95, 0.85)),
                       (B(0.05, -0.4, 0.0), B(0.07, -0.6, 0.0)), M("blep", 1.0, 1.0, tilt=-0.4), ("gloom",)),
    "deadpan": Face3((E(lid=0.5, pupil=0.6), E(lid=0.5, pupil=0.6)), (B(0.03, 0.0, 0.0), B(0.03, 0.0, 0.0)),
                     M("flat", 0.75, 1.0)),
    "awe": Face3((E("star", 1.15, 1.2), E("star", 1.15, 1.2)), (B(-0.13, 0.25, 0.5), B(-0.13, 0.25, 0.5)),
                 M("o", 0.55, 0.85), ("blush", "sparkle")),
    "lovestruck": Face3((E("heart", 1.1, 1.1), E("heart", 1.1, 1.1)), (B(-0.09, 0.35, 0.4), B(-0.09, 0.35, 0.4)),
                        M("cat", 0.9, 1.0), ("blush",)),
    "scheming": Face3((E(lid=0.45, lid_tilt=0.5, lower=0.15, pupil=0.6), E(lid=0.45, lid_tilt=0.5, lower=0.15, pupil=0.6)),
                      (B(0.0, -0.8, 0.3), B(0.0, -0.8, 0.3)), M("grin", 1.25, 0.6, tilt=0.15)),
}
EXPRESSIONS3 = tuple(FACES3)
# a story's v2 expression names still work under v3: each maps to its nearest v3 face
ALIASES3 = {"worried": "nervous", "scared": "terrified", "crying": "heartbroken", "angry": "furious",
            "smirk": "smug", "blank": "deadpan", "wide": "shocked", "shut": "delighted", "grin": "delighted",
            "squeeze": "terrified", "soft": "delighted", "asleep": "deadpan", "fish": "suspicious", "laugh": "crylaugh",
            "smile": "neutral", "hopeful": "awe", "polite": "neutral", "sad-smile": "heartbroken", "warm": "delighted"}


def resolve(expr: str) -> str:
    return expr if expr in FACES3 else ALIASES3.get(expr, "neutral")


# ------------------------------------------------------------------------------------------------ drawing

class _Pen:
    def __init__(self, ink, scale=1.0):
        self.W, self.H = TEX3_W * SS, TEX3_H * SS
        self.im = Image.new("RGBA", (self.W, self.H), (0, 0, 0, 0))
        self.d = ImageDraw.Draw(self.im)
        self.ink = ink + (255,)
        self.th = 0.03 * self.W * scale     # the ink line: thick, like a marker

    def X(self, u):    # u from -1 (left edge) to 1 (right edge) of the face
        return self.W / 2 + u * self.W / 2

    def Y(self, v):    # v from 0 (top) to 1 (bottom)
        return v * self.H

    def poly(self, pts, fill, outline=True, th=None):
        th = self.th if th is None else th
        self.d.polygon(pts, fill=fill + (255,) if len(fill) == 3 else fill)
        if outline:
            self.line(pts + [pts[0]], th)

    def line(self, pts, th=None, col=None):
        th = self.th if th is None else th
        col = self.ink if col is None else (col + (255,) if len(col) == 3 else col)
        self.d.line(pts, fill=col, width=max(1, int(th)), joint="curve")
        for x, y in (pts[0], pts[-1]):
            self.d.ellipse([x - th / 2, y - th / 2, x + th / 2, y + th / 2], fill=col)

    def ellipse(self, cx, cy, rx, ry, fill, outline=True, th=None):
        th = self.th if th is None else th
        if outline:
            self.d.ellipse([cx - rx - th / 2, cy - ry - th / 2, cx + rx + th / 2, cy + ry + th / 2], fill=self.ink)
        self.d.ellipse([cx - rx + (th / 2 if outline else 0), cy - ry + (th / 2 if outline else 0),
                        cx + rx - (th / 2 if outline else 0), cy + ry - (th / 2 if outline else 0)],
                       fill=fill + (255,) if len(fill) == 3 else fill)


def _oval_pts(cx, cy, rx, ry, n=48):
    return [(cx + rx * math.cos(2 * math.pi * i / n), cy + ry * math.sin(2 * math.pi * i / n)) for i in range(n)]


def _arc(cx, cy, w, bend, n=20, tilt=0.0):
    """A curve of width w through (cx, cy): bend > 0 dips down in the middle (a smile), < 0 humps up."""
    return [(cx - w / 2 + w * i / n, cy + bend * (1 - (2 * i / n - 1) ** 2) - tilt * (2 * i / n - 1) * w * 0.25)
            for i in range(n + 1)]


def _eye(p: _Pen, e: Eye, cx, cy, side, look, blink, pupil_c, base_rx, base_ry, skin):
    rx, ry = base_rx * e.sx, base_ry * e.sy
    cy += e.dy * p.H
    shape = "shut" if blink > 0.5 and e.shape in ("oval", "star", "heart") else e.shape
    if shape == "happy":
        p.line(_arc(cx, cy + ry * 0.1, rx * 1.9, -ry * 0.75), p.th * 1.15)
        return
    if shape == "shut":
        p.line(_arc(cx, cy + ry * 0.15, rx * 1.8, ry * 0.18), p.th * 1.1)
        return
    if shape == "squeeze":   # > <, pointing at the nose
        tip = cx - side * rx * 0.75
        p.line([(cx + side * rx * 0.85, cy - ry * 0.55), (tip, cy), (cx + side * rx * 0.85, cy + ry * 0.55)], p.th * 1.15)
        return
    if shape == "x":
        for s_ in (-1, 1):
            p.line([(cx - rx * 0.7, cy - s_ * ry * 0.6), (cx + rx * 0.7, cy + s_ * ry * 0.6)], p.th * 1.1)
        return
    # the eye is drawn on its own layer, then the lids cut it (no skin-coloured patches over the face)
    q = _Pen.__new__(_Pen)
    q.W, q.H, q.ink, q.th = p.W, p.H, p.ink, p.th
    q.im = Image.new("RGBA", (p.W, p.H), (0, 0, 0, 0))
    q.d = ImageDraw.Draw(q.im)
    q.ellipse(cx, cy, rx, ry, WHITE)
    lx, ly = look
    pr = rx * 0.5 * e.pupil
    px, py = cx + lx * (rx - pr) * 0.75, cy + ly * (ry - pr) * 0.6 + ry * 0.05
    if shape == "star":
        st = [(px + (pr * 1.5 if k % 2 == 0 else pr * 0.6) * math.cos(-math.pi / 2 + k * math.pi / 5),
               py + (pr * 1.5 if k % 2 == 0 else pr * 0.6) * math.sin(-math.pi / 2 + k * math.pi / 5)) for k in range(10)]
        q.poly(st, (255, 206, 60), th=p.th * 0.55)
    elif shape == "heart":
        hr = pr * 1.25
        ht = [(px + hr * math.sin(t) ** 3, py - hr * (13 * math.cos(t) - 5 * math.cos(2 * t) - 2 * math.cos(3 * t)
               - math.cos(4 * t)) / 16) for t in [2 * math.pi * i / 40 for i in range(40)]]
        q.poly(ht, (236, 60, 100), th=p.th * 0.55)
    else:
        q.ellipse(px, py, pr, pr, pupil_c, outline=False)
        if pr > rx * 0.2:   # two flat highlights: no gradient
            q.ellipse(px - pr * 0.35, py - pr * 0.4, pr * 0.32, pr * 0.32, WHITE, outline=False)
            q.ellipse(px + pr * 0.38, py + pr * 0.35, pr * 0.14, pr * 0.14, WHITE, outline=False)
        else:               # a pin pupil keeps one pin of light
            q.ellipse(px - pr * 0.2, py - pr * 0.25, max(3, pr * 0.35), max(3, pr * 0.35), WHITE, outline=False)
    mask = Image.new("L", (p.W, p.H), 255)
    md = ImageDraw.Draw(mask)
    lines = []
    big = rx + p.th * 2
    if e.lid > 0:
        yi = cy - ry + 2 * ry * e.lid + e.lid_tilt * ry * 0.5      # inner end (toward the nose)
        yo = cy - ry + 2 * ry * e.lid - e.lid_tilt * ry * 0.5
        xi, xo = cx - side * big, cx + side * big
        md.polygon([(xi, cy - ry * 3), (xo, cy - ry * 3), (xo, yo + (yo - yi) * 0.0), (xi, yi)], fill=0)
        lines.append(_clip_line(cx, cy, rx, ry, (xi, yi), (xo, yo)))
    if e.lower > 0:
        yb = cy + ry - 2 * ry * e.lower
        arc = _arc(cx, yb + ry * 0.12, big * 2, -ry * 0.25)
        md.polygon(arc + [(cx + big, cy + ry * 3), (cx - big, cy + ry * 3)], fill=0)
        lines.append([pt for pt in arc if ((pt[0] - cx) / rx) ** 2 + ((pt[1] - cy) / ry) ** 2 <= 1.0])
    p.im.alpha_composite(Image.composite(q.im, Image.new("RGBA", q.im.size, (0, 0, 0, 0)), mask))
    for ln in lines:
        if len(ln) > 1:
            p.line(ln, p.th * 1.1)


def _clip_line(cx, cy, rx, ry, a, b, n=40):
    """The part of the straight line a-b inside the eye's oval (where a lid's edge shows)."""
    pts = [(a[0] + (b[0] - a[0]) * i / n, a[1] + (b[1] - a[1]) * i / n) for i in range(n + 1)]
    pts = [pt for pt in pts if ((pt[0] - cx) / (rx * 1.04)) ** 2 + ((pt[1] - cy) / (ry * 1.04)) ** 2 <= 1.0]
    return sorted(pts)


def _brow(p: _Pen, b: Brow, cx, cy, side, w):
    if b.hide:
        return
    w *= b.w
    cy = max(p.Y(HAIRLINE) + p.th, cy + b.dy * p.H * 0.6)
    inner, outer = cx - side * w / 2, cx + side * w / 2
    yi, yo = cy - b.tilt * w * 0.32, cy + b.tilt * w * 0.12
    n = 12
    pts = []
    for i in range(n + 1):
        t = i / n
        x = outer + (inner - outer) * t
        y = yo + (yi - yo) * t - b.bend * w * 0.22 * (1 - (2 * t - 1) ** 2)
        pts.append((x, y))
    lift = p.Y(HAIRLINE) + p.th * 1.1 - min(y for _, y in pts)   # brows that fly up stop under the fringe
    if lift > 0:
        pts = [(x, y + lift) for x, y in pts]
    # a thick bar that tapers at the outer end
    for i in range(n):
        th = p.th * (1.35 + 0.55 * (i / n))
        p.line([pts[i], pts[i + 1]], th)


def _mouth(p: _Pen, m: Mouth, open_: float, cx, cy):
    W = p.W * 0.36 * m.w
    cx += m.dx * p.W / 2
    sh = m.shape
    talk = open_ > 0.05
    if talk and sh in ("smile", "flat", "smirk", "wobble", "cat"):   # talking opens a closed mouth into its open cousin
        sh = {"smile": "grin", "flat": "o", "smirk": "grin", "wobble": "scream", "cat": "grin"}[sh]
        m = replace(m, h=0.35 + 0.65 * open_)
    elif talk:
        m = replace(m, h=m.h * (0.75 + 0.4 * open_))
    H = p.H * 0.13 * m.h
    if sh == "smile":
        p.line(_arc(cx, cy, W, H * 0.55, tilt=m.tilt), p.th * 1.1)
    elif sh == "flat":
        p.line(_arc(cx, cy, W, 0.0, tilt=m.tilt), p.th * 1.1)
    elif sh == "frown":
        p.line(_arc(cx, cy + H * 0.3, W, -H * 0.5, tilt=m.tilt), p.th * 1.1)
    elif sh == "smirk":   # flat on one side, hooked up on the other
        pts = [(cx - W / 2 + W * i / 20, cy + (H * 0.35 * (i / 20) ** 3) - m.tilt * H * 0.9 * max(0, (i / 20 - 0.55) / 0.45) ** 2)
               for i in range(21)]
        p.line(pts, p.th * 1.4)
        p.line([pts[-1], (pts[-1][0] + W * 0.06, pts[-1][1] - H * 0.3)], p.th * 1.1)
    elif sh == "wobble":
        pts = [(cx - W / 2 + W * i / 40, cy + H * 0.16 * math.sin(i / 40 * math.pi * 5)) for i in range(41)]
        p.line(pts, p.th)
    elif sh == "cat":   # a w-shaped closed smile
        pts = [(cx - W / 2 + W * i / 40, cy + H * 0.45 * abs(math.sin(i / 40 * math.pi * 2))) for i in range(41)]
        p.line(pts, p.th)
    elif sh in ("grin", "o", "scream", "wail", "teeth", "blep"):
        if sh == "grin":    # a D: flat top, big round bottom
            top = [(cx - W / 2 + W * i / 20, cy - H * 0.35 - m.tilt * (2 * i / 20 - 1) * H * 0.3) for i in range(21)]
            bot = [(cx + W / 2 - W * i / 30, cy - H * 0.35 + H * 1.25 * math.sin(math.pi * i / 30) ** 0.9) for i in range(31)]
            pts = top + bot
        elif sh == "o":
            pts = _oval_pts(cx, cy + H * 0.1, W * 0.32, H * 0.62)
        elif sh == "scream":   # a tall rounded box, wider at the bottom
            pts = []
            for i in range(48):
                a = 2 * math.pi * i / 48
                x, y = math.cos(a), math.sin(a)
                k = 0.85 + 0.15 * y
                pts.append((cx + W * 0.42 * k * (abs(x) ** 0.6) * (1 if x >= 0 else -1), cy + H * 0.1 + H * 0.85 * (abs(y) ** 0.75) * (1 if y >= 0 else -1)))
        elif sh == "wail":     # an upside-down D, lopsided wobble on top
            top = [(cx - W / 2 + W * i / 30, cy + H * 0.55 - H * 1.0 * math.sin(math.pi * i / 30) ** 0.9) for i in range(31)]
            pts = top + [(cx + W / 2 - W * i / 10, cy + H * 0.55) for i in range(11)]
        elif sh == "teeth":    # gritted: a wide rounded bar of teeth
            x0, x1, y0, y1 = cx - W / 2, cx + W / 2, cy - H * 0.38, cy + H * 0.38
            p.d.rounded_rectangle([x0 - p.th / 2, y0 - p.th / 2, x1 + p.th / 2, y1 + p.th / 2], radius=H * 0.4, fill=p.ink)
            p.d.rounded_rectangle([x0 + p.th / 2, y0 + p.th / 2, x1 - p.th / 2, y1 - p.th / 2], radius=H * 0.3, fill=WHITE + (255,))
            p.line([(x0 + p.th, cy), (x1 - p.th, cy)], p.th * 0.6)
            for k in range(1, 5):
                x = x0 + (x1 - x0) * k / 5
                p.line([(x, y0 + p.th * 0.6), (x, y1 - p.th * 0.6)], p.th * 0.55)
            return
        else:                  # blep: a crooked flat line with the tongue out of one side
            pts_l = [(cx - W / 2 + W * i / 20, cy - m.tilt * (2 * i / 20 - 1) * H * 0.3 + H * 0.12 * math.sin(i / 20 * math.pi * 3)) for i in range(21)]
            tx, ty = cx + W * 0.18, cy + H * 0.05
            p.poly(_oval_pts(tx, ty + H * 0.45, W * 0.15, H * 0.5)[0:25] + [(tx - W * 0.15, ty)], TONGUE, th=p.th * 0.8)
            p.line(pts_l, p.th * 1.1)
            return
        p.poly(pts, INSIDE, th=p.th * 1.05)
        # teeth along the top and a tongue at the bottom, clipped to the mouth by drawing into a mask
        mask = Image.new("L", (p.W, p.H), 0)
        md = ImageDraw.Draw(mask)
        md.polygon(pts, fill=255)
        layer = Image.new("RGBA", (p.W, p.H), (0, 0, 0, 0))
        ld = ImageDraw.Draw(layer)
        ys = [y for _, y in pts]
        ytop, ybot = min(ys), max(ys)
        hh = ybot - ytop
        if sh in ("grin", "scream", "wail") and hh > H * 0.5:
            ld.rectangle([cx - W, ytop - 2, cx + W, ytop + hh * 0.2], fill=WHITE + (255,))
            ld.ellipse([cx - W * 0.3, ybot - hh * 0.32, cx + W * 0.3, ybot + hh * 0.3], fill=TONGUE + (255,))
        elif sh == "o" and hh > H * 0.6:
            ld.ellipse([cx - W * 0.2, ybot - hh * 0.3, cx + W * 0.2, ybot + hh * 0.25], fill=TONGUE + (255,))
        p.im.paste(layer, (0, 0), Image.composite(layer, Image.new("RGBA", layer.size, (0, 0, 0, 0)), mask).split()[3])
        p.line(pts + [pts[0]], p.th * 1.05)


def _accents(p: _Pen, f: Face3, ex, ey, rx, ry):
    a = set(f.accents)
    if "blush" in a:
        for side in (-1, 1):
            for k in (-1, 0, 1):   # three slanted hatch lines: flat, not a soft gradient
                x = p.X(side * 0.56) + k * p.W * 0.03
                p.line([(x + p.W * 0.012, p.Y(0.6)), (x - p.W * 0.012, p.Y(0.67))], p.th * 0.6, (236, 90, 110))
    if "tears" in a:   # big drops flying off the outer corners
        for side in (-1, 1):
            x, y = ex(side) + side * rx * 1.25, ey - ry * 0.1
            for k, sc in enumerate((1.0, 0.6)):
                xx, yy = x + side * k * p.W * 0.07, y - k * p.H * 0.05
                r = p.W * 0.035 * sc
                drop = [(xx + r * math.cos(t), yy + r * math.sin(t)) for t in [math.pi * (0.0 + i / 12) for i in range(13)]]
                drop += [(xx - side * r * 1.6, yy - r * 1.5)]
                p.poly(drop, TEAR, th=p.th * 0.55)
    if "stream" in a:  # waterfalls down the cheeks
        for side in (-1, 1):
            x = ex(side)
            y0 = ey + ry * 0.75
            w = rx * 0.55
            pts = [(x - w / 2, y0), (x + w / 2, y0)]
            pts += [(x + w / 2 + p.W * 0.012 * math.sin(k), y0 + (p.H - y0) * k / 6) for k in range(1, 7)]
            pts += [(x - w / 2 + p.W * 0.012 * math.sin(k), y0 + (p.H - y0) * k / 6) for k in range(6, 0, -1)]
            p.poly(pts, TEAR, th=p.th * 0.55)
    if "sweat" in a:   # one fat drop on the viewer's right temple
        x, y, r = p.X(0.74), p.Y(0.3), p.W * 0.045
        drop = [(x + r * math.cos(t), y + r * math.sin(t)) for t in [math.pi * (-0.15 + 1.3 * i / 16) for i in range(17)]]
        drop += [(x, y - r * 2.2)]
        p.poly(drop, SWEAT, th=p.th * 0.6)
        p.ellipse(x - r * 0.3, y - r * 0.1, r * 0.22, r * 0.3, WHITE, outline=False)
    if "anger" in a:   # the cross-vein, flat red
        x, y, r = p.X(-0.7), p.Y(0.24), p.W * 0.055
        for sx, sy in ((-1, -1), (1, -1), (-1, 1), (1, 1)):
            p.line(_arc(x + sx * r * 0.55, y + sy * r * 0.55, r * 0.9, sy * r * 0.35 * -1), p.th * 0.85, ANGER)
    if "gloom" in a:   # flat vertical lines down from the top
        for k in range(7):
            x = p.X(-0.5 + k / 6)
            p.line([(x, p.Y(HAIRLINE + 0.03)), (x, p.Y(HAIRLINE + 0.12 + 0.04 * (k % 2)))], p.th * 0.5, GLOOM)
    if "sparkle" in a:
        for x, y, r in ((p.X(-0.8), p.Y(0.26), p.W * 0.04), (p.X(0.82), p.Y(0.36), p.W * 0.03)):
            st = [(x + (r if k % 2 == 0 else r * 0.3) * math.cos(k * math.pi / 4), y + (r if k % 2 == 0 else r * 0.3) * math.sin(k * math.pi / 4)) for k in range(8)]
            p.d.polygon(st, fill=(255, 220, 90, 255))
    if "shake" in a:   # tremble marks beside the eyes
        for side in (-1, 1):
            x = p.X(side * 0.86)
            for k in (-1, 1):
                p.line([(x - p.W * 0.015, p.Y(0.42 + k * 0.06)), (x + p.W * 0.015, p.Y(0.42 + k * 0.06) - p.H * 0.02)], p.th * 0.55)


def face3_image(face: dict, skin: str, expr: str = "neutral", open_: float = 0.0, look=(0.0, 0.0),
                blink: float = 0.0, pop: float = 0.0) -> Image.Image:
    """The v3 face for one expression as an RGBA image (transparent where the skin shows). `pop` (0..1) is the
    snap at the start of a new expression: the eyes and brows stretch past their pose by up to 15%, then settle."""
    f = FACES3[resolve(expr)]
    p = _Pen(hexrgb(face.get("ink", "#17121a")), float(face.get("line", 1.0)))
    skin_c = hexrgb(skin)
    pupil_c = hexrgb(face.get("pupil", "#17121a"))
    es = float(face.get("eye_scale", 1.0)) * (1 + 0.15 * pop)
    rx, ry = p.W * EYE_RX * es, p.H * EYE_RY * es
    gap = float(face.get("eye_gap", 1.0))
    ey = p.Y(EYE_Y + float(face.get("eye_y", 0.0)))
    ex = lambda side: p.X(side * EYE_GAP * gap)
    look = (max(-1.0, min(1.0, look[0])), max(-1.0, min(1.0, look[1])))
    for i, side in enumerate((-1, 1)):
        e = f.eyes[i]
        _eye(p, e, ex(side), ey, side, look, blink, pupil_c, rx, ry, skin_c)
        bry = max(p.Y(HAIRLINE), ey - ry * e.sy - p.H * (0.075 + 0.03 * pop) + (e.dy * p.H))
        if face.get("brows", True):
            _brow(p, f.brows[i], ex(side), bry, side, rx * 2.1 * float(face.get("brow_w", 1.0)))
    if face.get("freckles"):
        for side in (-1, 1):
            for fx, fy in ((0.5, 0.64), (0.58, 0.62), (0.54, 0.7)):
                p.ellipse(p.X(side * fx), p.Y(fy), p.W * 0.009, p.W * 0.009, tuple(int(c * 0.7) for c in skin_c), outline=False)
    stache = face.get("mustache")
    _mouth(p, f.mouth, open_, p.X(0), p.Y(0.8 + (0.05 if face.get("mouth_low") or stache else 0.0)))
    if stache:   # a drawn mustache over the mouth (a modelled one lives on the head: rig hair "mustache")
        sc = hexrgb(stache)
        for side in (-1, 1):
            pts = [(p.X(0), p.Y(0.68)), (p.X(side * 0.34), p.Y(0.64)), (p.X(side * 0.52), p.Y(0.58)),
                   (p.X(side * 0.46), p.Y(0.72)), (p.X(0), p.Y(0.76))]
            p.poly(pts, sc, th=p.th * 0.8)
    _accents(p, f, ex, ey, rx, ry)
    return p.im.resize((TEX3_W, TEX3_H), Image.BOX)


def face3_key(face: dict, skin: str, expr: str, open_: float, look, blink: float, pop: float = 0.0) -> str:
    q = lambda x, n: round(x * n) / n
    style = "".join(f"{k}{face[k]}-" for k in ("eye_scale", "eye_gap", "eye_y", "brow_w", "line", "ink", "pupil", "mustache", "freckles", "mouth_low")
                    if k in face).replace("#", "")
    return f"v3-{style}{resolve(expr)}-{q(open_, 3)}-{q(look[0], 2)}-{q(look[1], 2)}-{int(blink > 0.5)}-{q(pop, 3)}"


def check_original3(face: dict) -> list[str]:
    """v3 faces are drawn bigger than any catalogue face and always have whites, brows and a lopsided range, so
    the classic default (two plain black ovals over a curved smile) can't come out of it; the one thing to refuse
    is turning the brows off and the eyes down to dots."""
    if not face.get("brows", True) and float(face.get("eye_scale", 1.0)) < 0.6:
        return ["a v3 face without brows and with tiny eyes reads as a stock face: keep the brows"]
    return []


POP_IN, POP_OUT = 0.05, 0.25   # seconds: the snap past the pose, then the settle back


def pop_at(dt: float) -> float:
    """The snap on a new v3 expression, dt seconds after its key: up to 1 in two frames, then eased back to 0, so
    the key line lands hard and holds (the driver sets Character.pop from it)."""
    if dt < 0:
        return 0.0
    if dt < POP_IN:
        return dt / POP_IN
    u = min(1.0, (dt - POP_IN) / POP_OUT)
    return (1 - u) ** 2
