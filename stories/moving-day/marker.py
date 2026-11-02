"""Moving Day: the Boxes' marker faces, and the marker marks on the other boxes. PIL and numpy only, so the
repo's Python, the tests and Blender's Python can all draw them.

Every drawing is one fat chisel marker on brown board, the same weight every time (LINE). The hand wobbles a
little, the ink pools where a stroke starts and stops, goes darker where two strokes cross and bleeds a little
into the fibres. Filled parts (pupils, the open mouth) are scribbled in, so specks of board show near their
edges. Nothing is a clean vector shape, and nothing comes from a game's face catalogue: these are our own
drawings, made of circles, arcs and scribbles.

An image is one face of a box, RGBA: the ink's colour, with alpha for how much ink is on the board. x runs left
to right as you look at the face, y top to bottom. `face(kind)` is the head box's front, `face_side(kind)` its
side faces (only "many_eyes" spills round the corner), `mark(kind)` a mark on another box.
"""

from __future__ import annotations

import math

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

FACES = ("none", "frown", "stare", "sideways", "many_eyes", "wide", "smile")
MARKS = ("none", "arrows", "cross", "eye", "squiggle", "eyes", "tally")
LINE = 0.036          # the marker's width, as a fraction of the head box's front width (about 1.8 cm): every face
INK = (17, 15, 19)    # near black, a little violet, like a fresh permanent marker
LAY = 0.9             # how much ink one pass lays down (two passes, where strokes cross: 0.99)


class Pen:
    """One marker on one face of a box. Strokes are stamped as overlapping round nibs along a wobbling path."""

    def __init__(self, w: int, h: int, seed: int, line_px: float):
        self.w, self.h = w, h
        self.r = np.random.default_rng(seed)
        self.lw = line_px
        self.acc = np.zeros((h, w), np.float32)

    # ---- paths
    @staticmethod
    def _spline(pts, n=24):
        """Catmull-Rom through the points (ends held), n samples a span."""
        p = [pts[0]] + list(pts) + [pts[-1]]
        out = []
        for i in range(1, len(p) - 2):
            p0, p1, p2, p3 = (np.array(p[k], float) for k in (i - 1, i, i + 1, i + 2))
            for k in range(n):
                t = k / n
                t2, t3 = t * t, t * t * t
                out.append(0.5 * ((2 * p1) + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t2
                                  + (-p0 + 3 * p1 - 3 * p2 + p3) * t3))
        out.append(np.array(p[-2], float))
        return np.array(out)

    def _wobble(self, path, amp=0.13, ds=2.0):
        """Resample every ds px and push the line sideways by a slow, smooth hand wobble."""
        path = np.asarray(path, float)
        seg = np.hypot(*np.diff(path, axis=0).T)
        s = np.concatenate([[0], np.cumsum(seg)])
        if s[-1] < 1e-6:
            return path, np.ones(len(path))
        ss = np.arange(0, s[-1] + ds, ds)
        x = np.interp(ss, s, path[:, 0])
        y = np.interp(ss, s, path[:, 1])
        dx, dy = np.gradient(x), np.gradient(y)
        nrm = np.hypot(dx, dy) + 1e-9
        nx, ny = -dy / nrm, dx / nrm
        ph = self.r.uniform(0, 2 * math.pi, 3)
        f = 2 * math.pi / (self.lw * self.r.uniform(3.5, 5.5))
        wob = (np.sin(ss * f + ph[0]) * 0.6 + np.sin(ss * f * 2.3 + ph[1]) * 0.3
               + np.sin(ss * f * 5.1 + ph[2]) * 0.1) * amp * self.lw
        width = 1.0 + 0.07 * np.sin(ss * f * 0.7 + ph[1] * 1.7)
        return np.stack([x + nx * wob, y + ny * wob], 1), width

    def stroke(self, pts, smooth=True, amp=0.13, lay=LAY, pool=True):
        """One pass of the marker through the control points (pixel coordinates)."""
        # straight segments are resampled too, so they wobble like the curves
        path = self._spline(pts) if smooth and len(pts) > 2 else np.asarray(pts, float)
        path, width = self._wobble(path, amp)
        im = Image.new("L", (self.w, self.h), 0)
        d = ImageDraw.Draw(im)
        for (x, y), k in zip(path, width):
            r = self.lw * 0.5 * k
            d.ellipse([x - r, y - r, x + r, y + r], fill=255)
        if pool:   # the nib rests a moment where a stroke starts and stops: a slightly fatter, darker blot
            for (x, y) in (path[0], path[-1]):
                r = self.lw * 0.58
                d.ellipse([x - r, y - r, x + r, y + r], fill=255)
        a = np.asarray(im, np.float32) / 255
        self.acc = 1 - (1 - self.acc) * (1 - a * lay)
        if pool:
            im2 = Image.new("L", (self.w, self.h), 0)
            d2 = ImageDraw.Draw(im2)
            for (x, y) in (path[0], path[-1]):
                r = self.lw * 0.42
                d2.ellipse([x - r, y - r, x + r, y + r], fill=255)
            a2 = np.asarray(im2.filter(ImageFilter.GaussianBlur(self.lw * 0.15)), np.float32) / 255
            self.acc = 1 - (1 - self.acc) * (1 - a2 * 0.6)

    # ---- shapes
    def circle(self, cx, cy, r, over=None, passes=1, squash=1.0):
        """A hand-drawn loop: it starts anywhere, runs a little past where it began and never quite closes on
        itself, and isn't a perfect circle. passes > 1 goes round again, pressing harder (the wide face)."""
        for k in range(passes):
            a0 = self.r.uniform(0, 2 * math.pi)
            ov = math.radians(over if over is not None else self.r.uniform(14, 30))
            n = max(24, int(r * 0.5))
            ph = self.r.uniform(0, 2 * math.pi)
            pts = []
            for i in range(n + 1):
                a = a0 + (2 * math.pi + ov) * i / n
                rr = r * (1 + 0.035 * math.sin(2 * a + ph)) * (1 - 0.035 * i / n) * (1 + 0.02 * k)
                pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a) * squash))
            self.stroke(pts, smooth=False, amp=0.09)

    def loop(self, cx, cy, rx, ry, laps=3, drift=0.0):
        """One continuous stroke round an oval several times, the centre drifting a little each lap, so the lines
        cross instead of thickening (the same marker width, gone over in a hurry)."""
        a0 = self.r.uniform(0, 2 * math.pi)
        n = max(40, int((rx + ry) * 0.6)) * laps
        dxy = self.r.uniform(-1, 1, (laps + 1, 2)) * drift
        pts = []
        for i in range(n + 1):
            u = i / n * laps
            k = int(u)
            f = u - k
            ox = dxy[k][0] * (1 - f) + dxy[min(k + 1, laps)][0] * f
            oy = dxy[k][1] * (1 - f) + dxy[min(k + 1, laps)][1] * f
            a = a0 + 2 * math.pi * u
            wob = 1 + 0.04 * math.sin(3 * a + k)
            pts.append((cx + ox + rx * wob * math.cos(a), cy + oy + ry * wob * math.sin(a)))
        self.stroke(pts, smooth=False, amp=0.08, pool=False)

    def dot(self, cx, cy, r):
        """A filled dot, scribbled round and round from the edge in."""
        step = self.lw * 0.55
        rr = r - self.lw * 0.45
        pts = []
        a = self.r.uniform(0, 2 * math.pi)
        while rr > 0:
            for i in range(28):
                a += 2 * math.pi / 28
                pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
                rr -= step / 28
        pts.append((cx, cy))
        if len(pts) > 2:
            self.stroke(pts, smooth=False, amp=0.05, pool=False)
        self.circle(cx, cy, max(r - self.lw * 0.45, self.lw * 0.3), over=8)

    def line(self, pts, **kw):
        self.stroke(pts, **kw)

    def fill(self, poly, angle=22.0, gaps=0.07):
        """Scribble a shape solid: tight zigzags across it, kept inside the outline (which is drawn over the
        edge afterwards), with the odd speck of board left where the hand didn't quite reach."""
        mask = Image.new("L", (self.w, self.h), 0)
        ImageDraw.Draw(mask).polygon([tuple(p) for p in poly], fill=255)
        m = np.asarray(mask, np.float32) / 255
        xs, ys = np.array([p[0] for p in poly]), np.array([p[1] for p in poly])
        cx, cy = xs.mean(), ys.mean()
        rad = max(xs.max() - xs.min(), ys.max() - ys.min())
        th = math.radians(angle)
        ux, uy = math.cos(th), math.sin(th)          # along the zigzag
        vx, vy = -uy, ux                              # across
        step = self.lw * 0.62
        pts = []
        k = -rad
        side = 1
        while k <= rad:
            pts.append((cx + vx * k + ux * side * rad, cy + vy * k + uy * side * rad))
            k += step
            side = -side
        sc = Pen(self.w, self.h, int(self.r.integers(1 << 30)), self.lw)
        sc.stroke(pts, smooth=False, amp=0.25, pool=False)
        # specks: the scribble misses a few spots, mostly near the edge
        edge = np.asarray(mask.filter(ImageFilter.GaussianBlur(self.lw * 0.9)), np.float32) / 255
        rough = self._noise(self.lw * 0.45)
        miss = (rough > 1 - gaps * (1.6 - edge)) & (edge < 0.97)
        a = sc.acc * m * np.where(miss, 0.25, 1.0)
        self.acc = 1 - (1 - self.acc) * (1 - a)

    def solid(self, poly, shrink=0.0, lay=0.985):
        """Ink a shape solid (a marker gone over and over), set in from its outline by shrink px so the
        outline stroke and the scribble own the ragged edge."""
        mask = Image.new("L", (self.w, self.h), 0)
        ImageDraw.Draw(mask).polygon([tuple(p) for p in poly], fill=255)
        if shrink > 0:
            k = int(shrink) * 2 + 1
            mask = mask.filter(ImageFilter.MinFilter(k if k % 2 else k + 1))
        a = np.asarray(mask, np.float32) / 255
        self.acc = 1 - (1 - self.acc) * (1 - a * lay)

    def _noise(self, scale):
        n = self.r.random((max(2, int(self.h / scale)), max(2, int(self.w / scale)))).astype(np.float32)
        im = Image.fromarray((n * 255).astype(np.uint8)).resize((self.w, self.h), Image.BICUBIC)
        return np.asarray(im, np.float32) / 255

    def image(self) -> Image.Image:
        """The ink as RGBA: a little bleed into the board round every stroke, and a dry, uneven lay."""
        a = self.acc
        if a.max() <= 0:
            return Image.new("RGBA", (self.w, self.h), INK + (0,))
        im = Image.fromarray((np.clip(a, 0, 1) * 255).astype(np.uint8))
        halo = np.asarray(im.filter(ImageFilter.GaussianBlur(self.lw * 0.16)), np.float32) / 255
        bleed = halo * (0.5 + 0.5 * self._noise(self.lw * 0.2)) * 0.45
        out = np.maximum(a, bleed)
        # the marker lays unevenly on board where it's gone over once; where it's gone over and over it's solid
        out = np.where(out > 0.97, 1.0, out * (0.9 + 0.1 * self._noise(self.lw * 0.12)))
        rgba = np.zeros((self.h, self.w, 4), np.uint8)
        rgba[..., :3] = INK
        rgba[..., 3] = (np.clip(out, 0, 1) * 255).astype(np.uint8)
        return Image.fromarray(rgba, "RGBA")


def _pen(w, h, seed, line_w=None):
    return Pen(w, h, seed, LINE * (line_w or w))


def face(kind: str, w: int = 1024, h: int = 940, seed: int = 17, gaze=(-0.55, 0.85)) -> Image.Image:
    """The head box's front, as it reads to the viewer (set.py turns it 180 degrees on a box that hangs upside
    down). w x h is the face's aspect. gaze is where the wide face's pupils slide, -1..1 each way as you look at
    it (+y down): toward Mum, down and to the left from her door."""
    if kind not in FACES:
        raise ValueError(f"face {kind!r} isn't one of {FACES}")
    p = _pen(w, h, seed + FACES.index(kind) * 101)
    X = lambda u: u * w
    Y = lambda v: v * h
    if kind == "frown":
        # two small dots set a little too far apart and too low, and a heavy downturned mouth
        p.dot(X(0.31), Y(0.43), X(0.05))
        p.dot(X(0.685), Y(0.445), X(0.044))
        p.line([(X(0.27), Y(0.80)), (X(0.36), Y(0.70)), (X(0.5), Y(0.665)), (X(0.635), Y(0.695)), (X(0.73), Y(0.79))])
    elif kind == "stare":
        # two big rings with pin pupils dead centre, and no mouth at all
        for cx, r in ((0.30, 0.135), (0.70, 0.128)):
            p.circle(X(cx), Y(0.43), X(r))
            p.dot(X(cx), Y(0.43), X(0.024))
    elif kind == "many_eyes":
        for (u, v, r, shape) in _many(seed, w / h, 0.07):
            _eye(p, X(u), Y(v), X(r), shape)
    elif kind == "sideways":
        # two rings with their pupils slid hard to one side (toward Mum's door), and no mouth
        for cx, r in ((0.30, 0.13), (0.70, 0.124)):
            p.circle(X(cx), Y(0.42), X(r))
            p.dot(X(cx + r * 0.62), Y(0.43), X(0.03))
    elif kind == "wide":
        # drawn wide open, as it reads from the door: two tall eyes, one bigger and set higher, each gone round once;
        # small solid pupils slid to the lower edge toward Mum (gaze, as you look at the face); and a tall gape whose
        # top pushes up between the eyes and whose bottom runs off the box's edge, so it never closes. It leans a
        # little, sits a little off centre and its edge is ragged where the marker shook
        gn = math.hypot(*gaze) or 1.0
        gx, gy = gaze[0] / gn, gaze[1] / gn
        for cx, cy, r in ((0.235, 0.30, 0.095), (0.765, 0.24, 0.125)):
            sq = 1.95
            p.circle(X(cx), Y(cy), X(r), squash=sq, over=22)
            k = 0.62   # how far toward the rim the pupil has slid
            p.dot(X(cx) + gx * k * X(r), Y(cy) + gy * k * X(r) * sq, X(0.028))
        # the mouth is a hole, not an expression: widest across its top third (about half the box), narrowing a
        # little as it runs off the bottom edge, solid black under the scribble so the board shows only in a
        # ragged rim at its edge. It leans 7 degrees and sits a touch off centre
        rr = np.random.default_rng(seed + 401)
        ph = rr.uniform(0, 2 * math.pi, 4)
        # its top edge pushes up a little left of centre, between the eyes, where the marker went over twice
        # a tall narrow slit between the eyes, not a round beard: pointed at the top, widest a third of the way down
        key = [(0.49, 0.18), (0.535, 0.30), (0.585, 0.50), (0.60, 0.72), (0.585, 0.95), (0.57, 1.14), (0.43, 1.14),
               (0.415, 0.95), (0.40, 0.72), (0.425, 0.50), (0.46, 0.30)]
        outline = []
        for (x0, y0), (x1, y1) in zip(key, key[1:] + key[:1]):
            for k in range(12):
                u = k / 12
                outline.append((x0 + (x1 - x0) * u, y0 + (y1 - y0) * u))
        cx_, cy_ = 0.50, 0.66
        tilt = math.radians(7)
        mouth = []
        for i, (x, y) in enumerate(outline):
            a = 2 * math.pi * i / len(outline)
            n = 1 + 0.10 * (0.5 * math.sin(5 * a + ph[0]) + 0.3 * math.sin(9 * a + ph[1]) + 0.2 * math.sin(13 * a + ph[2])) * 0.35
            dx, dy = (x - cx_) * n, (y - cy_) * n
            dx, dy = dx * math.cos(tilt) - dy * math.sin(tilt), dx * math.sin(tilt) + dy * math.cos(tilt)
            if y < 0.53:   # the top edge ragged where the hand shook: short, uneven teeth, never a clean arc
                dy -= (0.53 - y) / 0.11 * (0.009 * math.sin(41 * x + ph[3]) + 0.006 * math.sin(97 * x + ph[1])
                                           + 0.004 * math.sin(173 * x + ph[2]))
            mouth.append((X(cx_ + 0.012 + dx), Y(cy_ + dy)))
        p.solid(mouth, shrink=p.lw * 0.35)
        p.fill(mouth, angle=14, gaps=0.05)
        p.fill(mouth, angle=-42, gaps=0.03)
        p.stroke(mouth + mouth[:3], smooth=False, amp=0.25)
    elif kind == "smile":
        # eyes shut in two soft arcs, and a small smile a little to one side
        for cx in (0.32, 0.68):
            p.line([(X(cx - 0.085), Y(0.45)), (X(cx), Y(0.395)), (X(cx + 0.085), Y(0.45))])
        p.line([(X(0.36), Y(0.66)), (X(0.45), Y(0.725)), (X(0.56), Y(0.73)), (X(0.645), Y(0.665))])
    return p.image()


def face_side(kind: str, w: int = 1024, h: int = 940, seed: int = 17, side: int = 1, front_w: int | None = None):
    """A side face of the head box (side -1 is the box's own right, +1 its left). Only "many_eyes" spills onto
    it: four eyes crowding round the corner from the front. Same marker width as the front."""
    p = _pen(w, h, seed + 7 + side, front_w or w)
    if kind == "many_eyes":
        r = np.random.default_rng(seed + 31 + side)
        for (u, v, rr, shape) in _many(seed + 50 + side, w / h, 0.09, n=5, rmax=0.085):
            # crowd them toward the edge they share with the front
            u2 = u * 0.55 + (0.45 if side < 0 else 0.0)
            _eye(p, u2 * w, v * h, rr * (front_w or w), shape)
        del r
    return p.image()


def _many(seed, aspect, margin, n=17, rmax=0.11):
    """Where the eyes go: a seeded scatter, big and small, never touching (u, v in 0..1 of the face)."""
    r = np.random.default_rng(seed)
    out = []
    tries = 0
    while len(out) < n and tries < 6000:
        tries += 1
        rad = float(r.uniform(0.035, rmax) if len(out) > 2 else r.uniform(0.07, rmax))
        u = float(r.uniform(margin + rad, 1 - margin - rad))
        v = float(r.uniform(margin + rad * aspect, 1 - margin - rad * aspect))
        ok = all(math.hypot(u - a, (v - b) / aspect) > rad + rb + LINE * 1.6 for a, b, rb, _ in out)
        if ok:
            out.append((u, v, rad, "almond" if r.random() < 0.3 else "ring"))
    return out


def _eye(p: Pen, cx, cy, r, shape):
    if shape == "almond":
        top = [(cx - r * 1.25, cy), (cx - r * 0.5, cy - r * 0.62), (cx + r * 0.5, cy - r * 0.62), (cx + r * 1.25, cy)]
        bot = [(cx - r * 1.25, cy), (cx - r * 0.5, cy + r * 0.55), (cx + r * 0.5, cy + r * 0.55), (cx + r * 1.25, cy)]
        p.line(top)
        p.line(bot)
        p.dot(cx, cy, max(p.lw * 0.62, r * 0.34))
    else:
        p.circle(cx, cy, r)
        p.dot(cx, cy, max(p.lw * 0.6, r * 0.3))


def mark(kind: str, w: int = 1024, h: int = 768, seed: int = 5, line_w: int = 1024) -> Image.Image:
    """A mark on another box (the stacks): plain drawings, never words. line_w is the head box front's width
    in the same pixels-per-metre, so the marker is the same width on every box."""
    if kind not in MARKS:
        raise ValueError(f"mark {kind!r} isn't one of {MARKS}")
    p = _pen(w, h, seed + MARKS.index(kind) * 13, line_w)
    if kind == "arrows":   # the "this side up" picture: two arrows on a bar, drawn, no text
        for cx in (0.40, 0.60):
            p.line([(cx * w, 0.66 * h), (cx * w, 0.30 * h)], smooth=False)
            p.line([((cx - 0.06) * w, 0.40 * h), (cx * w, 0.29 * h), ((cx + 0.06) * w, 0.40 * h)], smooth=False)
        p.line([(0.32 * w, 0.72 * h), (0.68 * w, 0.72 * h)], smooth=False)
    elif kind == "cross":
        p.line([(0.3 * w, 0.3 * h), (0.7 * w, 0.7 * h)], smooth=False)
        p.line([(0.68 * w, 0.28 * h), (0.32 * w, 0.72 * h)], smooth=False)
    elif kind == "eye":
        _eye(p, 0.5 * w, 0.5 * h, 0.12 * line_w, "ring")
    elif kind == "eyes":
        # two dry rings with their pupils slid hard to the left and a little up as you look at the box: on a box
        # facing into the front room, that's toward Mum's door across the hall. The same marker as the face box
        for cx, cy, r in ((0.32, 0.46, 0.125), (0.68, 0.45, 0.118)):
            p.circle(cx * w, cy * h, r * w)
            p.dot(cx * w - r * w * 0.58, cy * h - r * w * 0.22, w * 0.034)
    elif kind == "tally":
        # four strokes and a slash through them, small, low on the left of a tall box face: the hidden mark
        x0, y0, y1 = 0.10 * w, 0.47 * h, 0.54 * h
        for k in range(4):
            xk = x0 + k * 0.075 * w
            p.line([(xk + 0.003 * w * k, y0), (xk - 0.004 * w, y1)], smooth=False)
        p.line([(x0 - 0.04 * w, y1 - 0.006 * h), (x0 + 0.29 * w, y0 + 0.004 * h)], smooth=False)
    elif kind == "squiggle":
        p.line([(0.25 * w + k * 0.05 * w, 0.5 * h + (0.06 if k % 2 else -0.06) * h) for k in range(11)])
    return p.image()


def board_preview(img: Image.Image, board=(165, 122, 78)) -> Image.Image:
    """The drawing on plain board, for looking at it outside Blender."""
    bg = Image.new("RGBA", img.size, board + (255,))
    bg.alpha_composite(img)
    return bg.convert("RGB")


if __name__ == "__main__":   # python marker.py <out dir>: every face and mark on board, side by side
    import sys
    from pathlib import Path

    out = Path(sys.argv[1] if len(sys.argv) > 1 else ".")
    out.mkdir(parents=True, exist_ok=True)
    tiles = [board_preview(face(k, 512, 470)) for k in FACES[1:]]
    tiles += [board_preview(face_side("many_eyes", 470, 470, side=s, front_w=512)) for s in (-1, 1)]
    sheet = Image.new("RGB", (sum(t.width for t in tiles) + 10 * len(tiles), 480), (30, 28, 32))
    x = 0
    for t in tiles:
        sheet.paste(t, (x, 5))
        x += t.width + 10
    sheet.save(out / "faces.png")
    ms = [board_preview(mark(k, 400, 300, line_w=512)) for k in MARKS[1:]]
    sh2 = Image.new("RGB", (410 * len(ms), 310), (30, 28, 32))
    for i, t in enumerate(ms):
        sh2.paste(t, (i * 410, 5))
    sh2.save(out / "marks.png")
    print(out / "faces.png")
