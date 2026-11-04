"""ep89 "sister-diary": two bedrooms across a short hall, and two diaries whose ink crawls by itself.

Places (metres, floor z = 0): hall y -2.2..0; my room (sky blue) x -4.4..-0.1, y 0..4.4; Nina's room (lilac) x 0.1..4.4;
one shared wall at x = 0. Desks back to back on it (mine x -0.76..-0.14, hers 0.14..0.76, y 0.8..2.2). Far rooms:
GIFT (30, 0), CAR (60, 0), WORK (90, 0), PAIR (120, 0).

THE INK: each diary page ("blue", "lilac") has 6 rows of 11 glyph blocks (scribbles, never words). Cues:
  ink {d, row, c: lilac|blue|green, to, dur, size, shake, hard}   a row crawls to `to` (0..1) over dur
  inkclear {d}                                                     every row of that page empties
  answer                                                           one more tally stroke in the marker
  place {d, to, dur}  open {d, to, dur}  pen {d, on}               where a diary is, how open, the writing hand
  mydoor / ndoor {to, dur} (degrees)  drawer {to, dur}  lamp {n, to, dur}  hud2 {to, dur}  ribbon {on}  glint {dur}
  clock {h, m}        Story key "shotlook": {shot: {cutwall, noceil, plan}}.
THE MARKER (the rule meter): the open blue diary as an inset parented to the camera, top right, with the same lilac
ink crawling and a pen glyph with a tally; the lilac diary joins it from L48 (cue hud2).
"""

from __future__ import annotations

import math
import random
import sys
from pathlib import Path

import bpy
from mathutils import Euler, Matrix, Vector as V

from blocky import acting as ac

W, H = 0.14, 0.19                # one page
PAGE_TOP = 0.0185
ROWS, COLS = 6, 11
INK = {"lilac": "#6a2af0", "blue": "#1448d0", "green": "#12b088", "dark": "#4a1fc0"}
GIFT, CAR, WORK, PAIR = 30.0, 60.0, 90.0, 120.0


def _ss(x):
    x = min(1.0, max(0.0, x))
    return x * x * (3 - 2 * x)


def _cues(tl, name):
    return [c for c in tl["cues"] if c["name"] == name]


def _level(tl, name, t, default, **match):
    v0, v = default, default
    for c in _cues(tl, name):
        if any(c.get(k) != x for k, x in match.items()):
            continue
        if c["t"] > t + 1e-9:
            break
        d = max(1e-6, c.get("dur", 0.3))
        v0, v = v, c["to"]
        if t < c["t"] + d:
            return v0 + (v - v0) * _ss((t - c["t"]) / d)
    return v


def _shot(tl, t):
    for s in tl["shots"]:
        if s["start"] <= t < s["end"]:
            return s
    return tl["shots"][-1]


def box(kit, name, lo, hi, mat, parent=None, bevel=0.0):
    c = tuple((a + b) / 2 for a, b in zip(lo, hi))
    s = tuple(b - a for a, b in zip(lo, hi))
    return kit.box(name, s, c, mat, parent, bevel=bevel)


# --------------------------------------------------------------------------------------------------- materials
def materials(kit):
    M = {}
    P = kit.plastic
    M["floor"] = kit.planks("#e2c394", "#cfa970", 1.0, "X", "floor", 0.6)
    M["hallfloor"] = kit.planks("#e8cfa6", "#d6b684", 1.0, "X", "hall floor", 0.6)
    M["wall_b"] = P("#9fd8ff", 0.9, "wall blue", 0.1)
    M["wall_l"] = P("#d4bcff", 0.9, "wall lilac", 0.1)
    M["wall_h"] = P("#fff0d8", 0.9, "wall hall", 0.1)
    M["ceil"] = P("#fff6e6", 0.9, "ceiling", 0.05)
    M["trim"] = P("#ffffff", 0.6, "trim", 0.2)
    M["desk"] = P("#b98a58", 0.6, "desk wood", 0.3)
    M["wood2"] = P("#b98450", 0.6, "dark wood", 0.3)
    M["white"] = P("#fbfbff", 0.5, "white", 0.3)
    M["chair_b"] = P("#5fb4ff", 0.5, "chair blue", 0.3)
    M["chair_l"] = P("#b894ff", 0.5, "chair lilac", 0.3)
    M["bed_b"] = P("#6fbaff", 0.7, "duvet blue", 0.1)
    M["bed_l"] = P("#c7a6ff", 0.7, "duvet lilac", 0.1)
    M["sheet"] = P("#fff9ee", 0.8, "sheet", 0.1)
    M["rug_b"] = P("#3f8fe0", 0.95, "rug blue", 0.0)
    M["rug_l"] = P("#9a72e8", 0.95, "rug lilac", 0.0)
    M["rug_h"] = P("#ff8f6b", 0.95, "rug hall", 0.0)
    M["brass"] = kit.metal("#e8b43c", 0.28, "brass")
    M["cover_b"] = P("#3f8fff", 0.5, "cover blue", 0.35)
    M["cover_l"] = P("#b48cf2", 0.5, "cover lilac", 0.35)
    M["page"] = P("#f0e2c4", 0.85, "page", 0.05)
    M["ribbon"] = P("#ff7a8a", 0.5, "ribbon", 0.2)
    M["dust"] = P("#cfc8b8", 0.95, "dust", 0.0)
    M["navy"] = kit.emit("#1f2f5c", 1.3, "night")
    M["star"] = kit.emit("#fff6d0", 4.0, "star")
    M["moon"] = kit.emit("#fff1c0", 2.5, "moon")
    M["black"] = P("#1b1b22", 0.5, "black", 0.3)
    M["skin"] = P("#e8b998", 0.5, "skin", 0.2)
    M["keyring"] = kit.metal("#cfd3d8", 0.25, "keys")
    M["tag"] = P("#ff4f5a", 0.5, "key tag", 0.3)
    M["shade"] = kit.emit("#ffc470", 2.2, "shade")
    M["yellow"] = P("#ffd95a", 0.6, "cloth yellow", 0.1)
    M["mint"] = P("#a8f0d0", 0.9, "mint wall", 0.1)
    M["car"] = P("#ff5a4a", 0.35, "car red", 0.5)
    M["carglass"] = P("#6b8fb8", 0.1, "car glass", 0.6)
    M["tyre"] = P("#25252b", 0.8, "tyre", 0.1)
    M["dent"] = P("#d9453a", 0.5, "dent", 0.4)
    M["curtain_b"] = P("#ffffff", 0.9, "curtain", 0.0)
    M["clockface"] = kit.emit("#fff7e0", 1.0, "clock face")
    M["hand"] = P("#2a2a40", 0.5, "clock hand", 0.1)
    M["glint"] = kit.emit("#ffffff", 5.0, "glint")
    M["bulb_n"] = kit.emit("#ffd9a0", 3.0, "bulb")
    M["strip"] = kit.emit("#ffcc7a", 2.0, "door strip")
    M["glow"] = kit.emit("#ffd08a", 0.9, "floor glow")
    # HUD (self-lit, so it reads the same in every shot)
    M["h_plate"] = kit.emit("#16224d", 1.0, "hud plate")
    M["h_edge"] = kit.emit("#f4f6ff", 1.2, "hud edge")
    M["h_page"] = kit.emit("#fff6df", 0.95, "hud page")
    M["h_cb"] = kit.emit("#2f7fe8", 1.0, "hud cover b")
    M["h_cl"] = kit.emit("#9a6ff0", 1.0, "hud cover l")
    M["h_gold"] = kit.emit("#ffd35a", 1.6, "hud gold")
    M["h_pedge"] = kit.emit("#d8c08e", 0.9, "hud page edge")
    M["h_spb"] = kit.emit("#1a4fb0", 1.0, "hud spine b")
    M["h_spl"] = kit.emit("#6a3fc8", 1.0, "hud spine l")
    M["h_shadow"] = kit.emit("#101a3c", 0.9, "hud shadow")
    M["h_pen"] = kit.emit("#ffffff", 1.0, "hud pen")
    for k, h in INK.items():
        M[f"ink_{k}"] = kit.emit(h, 1.0, f"ink {k}")
        M[f"hink_{k}"] = kit.emit(h, 1.25, f"hud ink {k}")
    return M


# --------------------------------------------------------------------------------------------------- the ink
class Ink:
    """A page of scribble glyphs: ROWS rows of COLS blocks. Style 'block' (my hand) or 'loop' (hers)."""

    def __init__(self, kit, name, parent, style, M, ztop, pitch, gscale, stroke, prefix="ink_", rowpitch=0.0235):
        self.kit, self.M, self.prefix = kit, M, prefix
        self.glyphs = []          # [row][col] -> (empty, [objs])
        self.cur = {}
        self.ztop = ztop
        x0 = 0.016
        ytop = H - 0.026
        for r in range(ROWS):
            row = []
            for c in range(COLS):
                if c in (3, 7) and style == "block" or c in (4, 8) and style == "loop":
                    row.append(None)
                    continue
                rnd = random.Random(r * 101 + c * 7 + 3)
                e = kit.empty(f"{name}.g{r}_{c}", (x0 + c * pitch, ytop - r * rowpitch, ztop), parent)
                e.scale = (gscale, gscale, gscale)
                objs = []
                p = rnd.randrange(4)
                h = (0.011 + 0.006 * rnd.random())
                sw = 0.0026 * stroke
                mat = M[prefix + "lilac"]

                def B(nm, sx, sy, x, y, rz=0.0):
                    o = kit.box(f"{name}.g{r}_{c}.{nm}", (sx, sy, 0.0024), (x, y, 0.0), mat, e, rot=(0, 0, rz))
                    o.hide_render = True
                    objs.append(o)
                if style == "block":
                    if p == 0:
                        B("a", sw, h, 0, h / 2); B("b", 0.006, sw, 0.0025, sw / 2)
                    elif p == 1:
                        B("a", sw, h, 0, h / 2); B("b", sw, h, 0.0055, h / 2); B("c", 0.0085, sw, 0.00275, h)
                    elif p == 2:
                        B("a", sw, h + 0.004, 0, (h + 0.004) / 2); B("b", 0.004, 0.004, 0.0045, h * 0.7)
                    else:
                        B("a", sw, h * 0.8, 0, h * 0.4); B("b", 0.0065, sw, 0.003, h * 0.8); B("c", sw, h * 0.5, 0.0065, h * 0.55)
                else:
                    if p == 0:
                        B("a", sw, h + 0.003, 0, (h + 0.003) / 2, -0.28)
                        o = kit.cyl(f"{name}.g{r}_{c}.o", 0.0034 * stroke ** 0.5, 0.0024, (0.0042, h * 0.35, 0.0), mat, e, n=10)
                        o.hide_render = True; objs.append(o)
                    elif p == 1:
                        B("a", sw, h, 0, h / 2, -0.35); B("b", sw, h, 0.0065, h / 2, 0.35)
                    elif p == 2:
                        B("a", 0.0045, sw, 0.0, h * 0.3, 0.5); B("b", 0.0045, sw, 0.0045, h * 0.55, -0.5); B("c", 0.0045, sw, 0.0085, h * 0.3, 0.5)
                    else:
                        B("a", sw, h + 0.005, 0, (h + 0.005) / 2 - 0.002, -0.4); B("b", 0.006, sw, 0.003, h * 0.6, 0.15)
                row.append((e, objs))
            self.glyphs.append(row)

    def set_row(self, r, prog, col, size, shake, t):
        n = sum(1 for g in self.glyphs[r] if g)
        shown = prog * n
        k = 0
        key = (r, col)
        for c, g in enumerate(self.glyphs[r]):
            if g is None:
                continue
            e, objs = g
            f = min(1.0, max(0.0, shown - k))
            k += 1
            vis = f > 0.02
            if vis:
                if self.cur.get((r, c)) != col:
                    for o in objs:
                        o.data.materials.clear()
                        o.data.materials.append(self.M[self.prefix + col])
                    self.cur[(r, c)] = col
                s = max(0.05, f)
                base = e.get("g0", None)
                if base is None:
                    base = e.scale[0]
                    e["g0"] = base
                e.scale = (base * size * s, base * size * s, base * size)
                if shake:
                    e.location = (e.location[0], e.location[1], self.ztop)
                    e.rotation_euler = (0, 0, shake * 25 * math.sin(t * 38 + c * 2.3 + r))
                else:
                    e.rotation_euler = (0, 0, 0)
            for o in objs:
                o.hide_render = not vis


def row_segments(tl):
    """Per page and row: [(t0, t1, p0, p1, colour, size, shake)] from the ink cues."""
    seg = {"blue": [[] for _ in range(ROWS)], "lilac": [[] for _ in range(ROWS)]}

    def val(d, r, T):
        v, col, size, shake = 0.0, "lilac", 1.0, 0.0
        for (t0, t1, p0, p1, c, s, sh) in seg[d][r]:
            if t0 <= T + 1e-9:
                v = p0 + (p1 - p0) * _ss((T - t0) / max(1e-6, t1 - t0)) if T < t1 else p1
                col, size, shake = c, s, sh
        return v

    for c in tl["cues"]:
        if c["name"] == "inkclear":
            for r in range(ROWS):
                seg[c["d"]][r].append((c["t"], c["t"], 0.0, 0.0, "lilac", 1.0, 0.0))
        elif c["name"] == "ink":
            d, r = c["d"], c["row"]
            if r >= ROWS:
                continue
            p0 = val(d, r, c["t"])
            col = "dark" if c.get("hard") else c.get("c", "lilac")
            seg[d][r].append((c["t"], c["t"] + max(0.02, c.get("dur", 1.0)), p0, c.get("to", 1.0), col,
                              c.get("size", 1.0) * (1.15 if c.get("hard") else 1.0), c.get("shake", 0.0)))
    return seg, val


def row_state(seg, d, r, T):
    v, col, size, shake = 0.0, "lilac", 1.0, 0.0
    for (t0, t1, p0, p1, c, s, sh) in seg[d][r]:
        if t0 <= T + 1e-9:
            v = p0 + (p1 - p0) * _ss((T - t0) / max(1e-6, t1 - t0)) if T < t1 else p1
            col, size, shake = c, s, sh
    return v, col, size, shake


# --------------------------------------------------------------------------------------------------- the diary
def build_diary(kit, M, name, cover, lilac):
    root = kit.empty(name, (0, 0, 0))
    mc = M["cover_l" if lilac else "cover_b"]
    box(kit, f"{name}.back", (-0.006, -0.008, 0.0), (W + 0.008, H + 0.008, 0.006), mc, root, bevel=0.002)
    for sy in (0, 1):      # brass corner caps and the clasp tab on the back cover, seen when the book lies open
        y = (-0.008 if not sy else H + 0.008 - 0.02)
        box(kit, f"{name}.bcap{sy}", (W + 0.008 - 0.02, y, 0.006), (W + 0.008, y + 0.02, 0.0085), M["brass"], root)
    box(kit, f"{name}.btab", (W + 0.008, H / 2 - 0.012, 0.0), (W + 0.022, H / 2 + 0.012, 0.0075), M["brass"], root, bevel=0.002)
    kit.cyl(f"{name}.bdot", 0.006, 0.0035, (W + 0.016, H / 2, 0.0095), M["brass"], root, n=14)
    box(kit, f"{name}.rpages", (0.0, 0.003, 0.006), (W - 0.003, H - 0.003, PAGE_TOP), M["page"], root)
    front = kit.empty(f"{name}.front", (0, 0, PAGE_TOP), root)
    box(kit, f"{name}.lpages", (0.0, 0.003, 0.0), (W - 0.003, H - 0.003, 0.0125), M["page"], front)
    box(kit, f"{name}.fcover", (-0.006, -0.008, 0.0125), (W + 0.008, H + 0.008, 0.0185), mc, front, bevel=0.002)
    for sy in (0, 1):
        for sx in (0, 1):
            x = (-0.006 if not sx else W + 0.008 - 0.018)
            y = (-0.008 if not sy else H + 0.008 - 0.018)
            box(kit, f"{name}.cap{sx}{sy}", (x, y, 0.0185), (x + 0.018, y + 0.018, 0.0205), M["brass"], front)
    kit.cyl(f"{name}.clasp", 0.0125, 0.0035, (W - 0.014, H / 2, 0.0205 + 0.00175), M["brass"], front, n=18)
    box(kit, f"{name}.clasptab", (W - 0.004, H / 2 - 0.008, 0.0185), (W + 0.007, H / 2 + 0.008, 0.0205), M["brass"], front)
    if lilac:       # the lore tally: two lilac strokes scratched in Nina's clasp
        for dx in (-0.004, 0.004):
            box(kit, f"{name}.tally{dx}", (W - 0.014 + dx - 0.0009, H / 2 - 0.006, 0.0240),
                (W - 0.014 + dx + 0.0009, H / 2 + 0.006, 0.0248), M["ink_lilac"], front)
    # ribbon band (gift)
    rib = []
    rib.append(box(kit, f"{name}.rib1", (W / 2 - 0.007, -0.006, 0.0205), (W / 2 + 0.007, H + 0.006, 0.0235), M["ribbon"], front))
    rib.append(box(kit, f"{name}.rib2", (-0.004, H / 2 - 0.007, 0.0205), (W + 0.004, H / 2 + 0.007, 0.0225), M["ribbon"], front))
    # dust
    dust = []
    rnd = random.Random(5 if lilac else 9)
    for k in range(6):
        x, y = rnd.uniform(0.01, W - 0.02), rnd.uniform(0.01, H - 0.02)
        dust.append(box(kit, f"{name}.dust{k}", (x, y, 0.0195), (x + rnd.uniform(0.02, 0.05), y + rnd.uniform(0.012, 0.03), 0.0225),
                        M["dust"], front))
    ink = Ink(kit, name + ".ink", root, "loop" if lilac else "block", M, PAGE_TOP, 0.0105, 1.15, 1.5)
    return {"root": root, "front": front, "ink": ink, "rib": rib, "dust": dust}


# --------------------------------------------------------------------------------------------------- the pen hand
def build_penhand(kit, M, name, sleeve_hex, inkc):
    r = kit.empty(name, (0, 0, -9))
    pen = kit.cyl(f"{name}.pen", 0.0055, 0.15, (0, -0.045, 0.075 + 0.0), M["black"], r, n=10)
    pen.rotation_euler = (0.55, 0, 0)       # leans back toward the reader (-y)
    kit.cyl(f"{name}.tip", 0.0055, 0.012, (0, -0.0035, 0.004), kit.plastic(inkc, 0.4), r, n=10).rotation_euler = (0.55, 0, 0)
    box(kit, f"{name}.hand", (-0.03, -0.12, 0.085), (0.03, -0.05, 0.12), M["skin"], r, bevel=0.01)
    s = kit.plastic(sleeve_hex, 0.8)
    box(kit, f"{name}.sleeve", (-0.034, -0.24, 0.095), (0.034, -0.11, 0.17), s, r, bevel=0.012)
    objs = [r] + list(r.children_recursive)
    return {"root": r, "all": objs}


# --------------------------------------------------------------------------------------------------- the marker
class Hud:
    """The marker: a small open book (coloured cover with brass caps and a clasp, a dark spine, a stack of page edges,
    cream pages with the ink) tilted a few degrees, over a soft dark shadow, so it reads as a book, not a screen."""

    def __init__(self, kit, M, name, lilac):
        self.kit, self.M = kit, M
        self.grp = kit.empty(name, (0, 0, -0.12), kit.OBJ["cam"])
        g = self.grp
        bk = kit.empty(f"{name}.bk", (0, 0.02, 0), g)
        bk.rotation_euler = (0, 0, math.radians(-7))
        mc = M["h_cl" if lilac else "h_cb"]
        sp = M["h_spl" if lilac else "h_spb"]
        box(kit, f"{name}.shadow", (-0.19, -0.13, -0.003), (0.2, 0.15, -0.0005), M["h_shadow"], bk, bevel=0.01)
        box(kit, f"{name}.cover", (-0.17, -0.098, 0.0), (0.17, 0.14, 0.004), mc, bk, bevel=0.006)
        box(kit, f"{name}.pstack", (-0.152, -0.088, 0.0035), (0.152, 0.12, 0.0075), M["h_pedge"], bk)
        box(kit, f"{name}.lp", (-0.148, -0.068, 0.0075), (-0.006, 0.118, 0.0105), M["h_page"], bk)
        box(kit, f"{name}.rp", (0.006, -0.068, 0.0075), (0.148, 0.118, 0.0105), M["h_page"], bk)
        box(kit, f"{name}.spine", (-0.008, -0.1, 0.0075), (0.008, 0.142, 0.0125), sp, bk)
        for sx in (-1, 1):
            for sy in (-1, 1):
                cx, cy = sx * 0.158, 0.021 + sy * 0.112
                box(kit, f"{name}.cap{sx}{sy}", (cx - 0.018, cy - 0.018, 0.004), (cx + 0.018, cy + 0.018, 0.0065), M["h_gold"], bk)
        box(kit, f"{name}.clasp", (0.165, -0.02, 0.0), (0.196, 0.062, 0.0055), M["h_gold"], bk, bevel=0.004)
        rootp = kit.empty(f"{name}.page", (0.0, -0.068, 0.0105 - PAGE_TOP), bk)
        # the page's ink: bigger, thicker glyphs on the right page
        self.ink = Ink(kit, name + ".ink", rootp, "loop" if lilac else "block", M, PAGE_TOP + 0.0, 0.0124, 1.35, 2.0, "hink_", 0.0235)
        # the pen glyph and the tally
        pen = kit.box(f"{name}.pen", (0.07, 0.014, 0.004), (-0.135, -0.17, 0.008), M["h_pen"], g, rot=(0, 0, 0.6))
        kit.box(f"{name}.pent", (0.016, 0.014, 0.004), (-0.158, -0.193, 0.008), M["hink_dark" if lilac else "hink_blue"], g, rot=(0, 0, 0.6))
        self.tally = []
        for i in range(10):
            t = kit.box(f"{name}.tal{i}", (0.013, 0.05, 0.004), (-0.07 + i * 0.026, -0.17, 0.008), M["h_gold"], g)
            t.hide_render = True
            self.tally.append(t)
        self.lilac = lilac
        self.objs = [g] + list(g.children_recursive)


def build_hud(kit, M, ctx):
    ctx["hud1"] = Hud(kit, M, "hud1", False)
    ctx["hud2"] = Hud(kit, M, "hud2", True)


def place_hud(ctx, lens, shown2):
    d = 0.12
    wf, hf = 2 * d * 6.75 / lens, 2 * d * 12.0 / lens
    s = 0.25 * wf / 0.372
    for key, u in (("hud1", 0.55), ("hud2", 0.0)):
        h = ctx[key]
        off = ctx.get("hudoff", (0.0, 0.0))
        h.grp.location = (u * wf / 2 + off[0] * wf, 0.69 * hf / 2 + off[1] * hf, -d)
        h.grp.scale = (s, s, s)


# --------------------------------------------------------------------------------------------------- the world
def build_home(kit, ctx, M):
    G = []

    def b(name, lo, hi, mat, bevel=0.0):
        o = box(kit, name, lo, hi, mat, None, bevel)
        G.append(o)
        return o
    b("floor", (-4.5, -2.3, -0.1), (4.5, 4.5, 0.0), M["floor"])
    b("hall floor", (-4.4, -2.2, 0.0), (4.4, 0.0, 0.004), M["hallfloor"])
    # outer walls (with windows left and right), back wall, hall walls
    for sx, wm in ((-1, "wall_b"), (1, "wall_l")):
        x0, x1 = (-4.5, -4.4) if sx < 0 else (4.4, 4.5)
        b(f"ow{sx}a", (x0, 0, 0), (x1, 4.5, 0.95), M[wm])
        b(f"ow{sx}b", (x0, 0, 2.05), (x1, 4.5, 2.7), M[wm])
        b(f"ow{sx}c", (x0, 0, 0.95), (x1, 0.8, 2.05), M[wm])
        b(f"ow{sx}d", (x0, 2.2, 0.95), (x1, 4.5, 2.05), M[wm])
        # window frame + night + stars + moon
        xi = x1 if sx < 0 else x0
        fx0, fx1 = (xi - 0.02, xi + 0.06) if sx < 0 else (xi - 0.06, xi + 0.02)
        for nm, lo, hi in (("t", (0.76, 2.05), (2.24, 2.12)), ("bt", (0.76, 0.88), (2.24, 0.95)),
                           ("l", (0.76, 0.88), (0.84, 2.12)), ("r", (2.16, 0.88), (2.24, 2.12)), ("m", (1.48, 0.95), (1.52, 2.05))):
            b(f"wf{sx}{nm}", (fx0, lo[0], lo[1]), (fx1, hi[0], hi[1]), M["trim"])
        nx = 4.62 * sx
        b(f"night{sx}", (nx - 0.02, -1.0, -0.5), (nx + 0.02, 5.5, 3.5), M["navy"])
        rnd = random.Random(sx + 3)
        for k in range(22):
            y, z = rnd.uniform(0.9, 2.1), rnd.uniform(1.02, 2.0)
            s = rnd.uniform(0.012, 0.03)
            b(f"star{sx}{k}", (nx - sx * 0.03 - 0.005, y, z), (nx - sx * 0.03 + 0.005, y + s, z + s), M["star"])
        kit.cyl(f"moon{sx}", 0.1, 0.02, (nx - sx * 0.04, 1.75, 1.65), M["moon"], None, rot=(0, math.pi / 2, 0), n=24)
        # curtains
        for yy in (0.62, 2.38):
            b(f"cur{sx}{yy}", (x1 - 0.12 if sx < 0 else x0 + 0.02, yy - 0.12, 0.7), (x1 - 0.02 if sx < 0 else x0 + 0.12, yy + 0.12, 2.3),
              M["curtain_b"], 0.02)
    b("back b", (-4.5, 4.4, 0), (0, 4.5, 2.7), M["wall_b"])
    b("back l", (0, 4.4, 0), (4.5, 4.5, 2.7), M["wall_l"])
    for sx in (-1, 1):
        b(f"hw{sx}", (4.4 * sx if sx > 0 else -4.5, -2.3, 0), (4.5 if sx > 0 else -4.4, 0, 2.7), M["wall_h"])
    b("hall back", (-4.5, -2.3, 0), (4.5, -2.2, 2.7), M["wall_h"])
    # the shared wall: blue face and lilac face (camera-hideable)
    ctx["sharedwall"] = [b("shared b", (-0.1, 0, 0), (0.0, 4.4, 2.7), M["wall_b"]), b("shared l", (0.0, 0, 0), (0.1, 4.4, 2.7), M["wall_l"])]
    # the hall wall with two door openings
    for sy_, lo, hi in ((1, (-4.5, -0.1, 0), (-2.05, 0.0, 2.7)), (2, (-1.15, -0.1, 0), (1.15, 0.0, 2.7)), (3, (2.05, -0.1, 0), (4.5, 0.0, 2.7))):
        b(f"hallwall{sy_}", lo, hi, M["wall_h"])
        lo2 = (lo[0], 0.0, lo[2]); hi2 = (hi[0], 0.1, hi[2])
        b(f"frontwall{sy_}", lo2, hi2, M["wall_b"] if sy_ == 1 else (M["wall_l"] if sy_ == 3 else M["wall_h"]))
    for x0, x1, nm, wm in ((-2.05, -1.15, "m", "wall_b"), (1.15, 2.05, "n", "wall_l")):
        b(f"lintel{nm}", (x0, -0.1, 2.1), (x1, 0.0, 2.7), M["wall_h"])
        b(f"lintel2{nm}", (x0, 0.0, 2.1), (x1, 0.1, 2.7), M[wm])
        for xx in (x0 - 0.05, x1):
            b(f"jamb{nm}{xx}", (xx, -0.12, 0), (xx + 0.05, 0.12, 2.1), M["trim"])
        b(f"head{nm}", (x0 - 0.05, -0.12, 2.1), (x1 + 0.05, 0.12, 2.15), M["trim"])
    # ceilings
    ctx["ceil"] = [b("ceil m", (-4.5, 0, 2.7), (0, 4.5, 2.78), M["ceil"]), b("ceil n", (0, 0, 2.7), (4.5, 4.5, 2.78), M["ceil"]),
                   b("ceil h", (-4.5, -2.3, 2.7), (4.5, 0, 2.78), M["ceil"])]
    # baseboards
    for nm, lo, hi in (("bb1", (-4.4, 4.3, 0), (4.4, 4.4, 0.1)), ("bb2", (-4.4, 0.1, 0), (-4.3, 4.4, 0.1)), ("bb3", (4.3, 0.1, 0), (4.4, 4.4, 0.1))):
        b(nm, lo, hi, M["trim"])
    # doors (hinged)
    for key, hx, sgn, mat in (("mydoor", -2.05, 1, "desk"), ("ndoor", 2.05, -1, "chair_l")):
        h = kit.empty(key, (hx, 0.0, 0.0))
        box(kit, f"{key}.panel", (0 if sgn > 0 else -0.9, -0.02, 0.0), (0.9 if sgn > 0 else 0, 0.02, 2.06), M["trim"] if key == "mydoor" else M["wall_l"], h, bevel=0.01)
        kit.cyl(f"{key}.knob", 0.03, 0.05, (0.8 * sgn, 0.0, 1.0), M["brass"], h, rot=(math.pi / 2, 0, 0), n=14)
        ctx[key] = h
    # hall: table with the keys, runner rug, frames
    b("hall table", (-0.4, -2.2, 0.72), (0.4, -1.8, 0.76), M["desk"], 0.01)
    for sx in (-1, 1):
        for sy in (-2.17, -1.83):
            b(f"htl{sx}{sy}", (0.34 * sx - 0.03, sy - 0.03, 0.0), (0.34 * sx + 0.03, sy + 0.03, 0.72), M["wood2"])
    b("runner", (-3.6, -1.6, 0.004), (3.6, -0.6, 0.016), M["rug_h"])
    keys = kit.empty("keys", (0.0, -2.0, 0.76))
    kr = kit.cyl("keyring", 0.035, 0.006, (0, 0, 0.006), M["keyring"], keys, n=24)
    for k in range(3):
        a = k * 0.5 - 0.5
        box(kit, f"key{k}", (0.03 + 0.0 * k, -0.01, 0.0), (0.095, 0.01, 0.006), M["keyring"], keys).rotation_euler = (0, 0, a)
    box(kit, "keytag", (-0.075, -0.02, 0.0), (-0.035, 0.02, 0.01), M["tag"], keys, bevel=0.004)
    ctx["keys"] = keys
    for k, (x, c) in enumerate(((-3.0, "h_cb"), (-2.7, "cover_l"), (3.0, "car"), (2.7, "yellow"))):
        mm = M[c] if c in M else M["white"]
        b(f"frame{k}", (x - 0.2, -2.2, 1.3), (x + 0.2, -2.17, 1.7), M["trim"])
        b(f"art{k}", (x - 0.16, -2.17, 1.34), (x + 0.16, -2.15, 1.66), mm)
    ctx["G"] = G


def build_rooms(kit, ctx, M):
    G = ctx["G"]

    def b(name, lo, hi, mat, bevel=0.0):
        o = box(kit, name, lo, hi, mat, None, bevel)
        G.append(o)
        return o
    for sx, desk_m, chair_m, rug, duvet in ((-1, "desk", "chair_b", "rug_b", "bed_b"), (1, "desk", "chair_l", "rug_l", "bed_l")):
        s = sx
        x = lambda v: s * v      # mirror helper
        def bx(name, xa, xb, ya, yb, za, zb, mat, bev=0.0):
            lo, hi = sorted((x(xa), x(xb)))
            return b(f"{name}{s}", (lo, ya, za), (hi, yb, zb), mat, bev)
        # desk against the shared wall
        bx("desktop", 0.14, 0.76, 0.8, 2.2, 0.72, 0.76, M[desk_m], 0.008)
        for yy in (0.84, 2.16):
            for xx in (0.18, 0.72):
                bx(f"dleg{xx}{yy}", xx - 0.025, xx + 0.025, yy - 0.025, yy + 0.025, 0.0, 0.72, M["white"])
        # chair
        bx("seat", 1.04, 1.46, 1.29, 1.71, 0.26, 0.30, M[chair_m], 0.01)
        bx("chback", 1.44, 1.48, 1.29, 1.71, 0.30, 0.75, M[chair_m], 0.01)
        for xx in (1.08, 1.42):
            for yy in (1.33, 1.67):
                bx(f"chleg{xx}{yy}", xx - 0.02, xx + 0.02, yy - 0.02, yy + 0.02, 0.0, 0.26, M["white"])
        # bed along the back wall, head at the shared wall
        bx("bedframe", 0.1, 2.2, 3.35, 4.35, 0.12, 0.34, M["wood2"], 0.01)
        bx("mattress", 0.12, 2.18, 3.37, 4.33, 0.34, 0.50, M["sheet"], 0.02)
        bx("duvet", 1.1, 2.18, 3.36, 4.34, 0.50, 0.55, M[duvet], 0.02)
        bx("pillow", 0.14, 0.52, 3.55, 4.15, 0.50, 0.54, M["white"], 0.02)
        # rug
        kit.cyl(f"rug{s}", 1.0, 0.012, (s * 2.5, 2.0, 0.006), M[rug], None, n=32)
        # desk lamp (spot aimed at the diary) at the door-side corner of the desk
        lx, ly = x(0.3), 0.98
        kit.cyl(f"lampbase{s}", 0.06, 0.02, (lx, ly, 0.77), M["black"], None)
        kit.cyl(f"lamparm{s}", 0.012, 0.34, (lx, ly, 0.94), M["black"], None)
        kit.cyl(f"lampshade{s}", 0.1, 0.12, (lx, ly, 1.14), M["shade"], None, r2=0.045)
        G.append(None)
    G[:] = [g for g in G if g is not None]
    # my room: dresser with the sliding drawer, the framed photo, the nightstand + clock
    for nm, lo, hi in (("dsl", (-3.8, 3.9, 0.0), (-3.75, 4.4, 0.9)), ("dsr", (-2.65, 3.9, 0.0), (-2.6, 4.4, 0.9)),
                       ("dback", (-3.8, 4.37, 0.0), (-2.6, 4.4, 0.9)), ("dbot", (-3.8, 3.9, 0.0), (-2.6, 4.4, 0.58)),
                       ("dtop", (-3.82, 3.88, 0.84), (-2.58, 4.4, 0.9)), ("dbar", (-3.8, 3.9, 0.82), (-2.6, 3.93, 0.84)),
                       ("dmid", (-3.8, 3.9, 0.58), (-2.6, 3.93, 0.62))):
        b(nm, lo, hi, M["white"] if nm not in ("dtop",) else M["desk"])
    for k, z in enumerate((0.1, 0.34)):
        b(f"dfront{k}", (-3.78, 3.88, z), (-2.62, 3.92, z + 0.2), M["chair_b"], 0.01)
        kit.cyl(f"dknob{k}", 0.02, 0.03, (-3.2, 3.86, z + 0.1), M["brass"], None, rot=(math.pi / 2, 0, 0), n=12)
    dr = kit.empty("drawer", (0, 0, 0))
    box(kit, "dr.front", (-3.76, 3.86, 0.62), (-2.64, 3.9, 0.82), M["chair_b"], dr, bevel=0.01)
    kit.cyl("dr.knob", 0.02, 0.03, (-3.2, 3.84, 0.72), M["brass"], dr, rot=(math.pi / 2, 0, 0), n=12)
    box(kit, "dr.bot", (-3.74, 3.9, 0.62), (-2.66, 4.36, 0.635), M["wood2"], dr)
    box(kit, "dr.l", (-3.74, 3.9, 0.62), (-3.72, 4.36, 0.78), M["wood2"], dr)
    box(kit, "dr.r", (-2.68, 3.9, 0.62), (-2.66, 4.36, 0.78), M["wood2"], dr)
    box(kit, "dr.b", (-3.74, 4.34, 0.62), (-2.66, 4.36, 0.78), M["wood2"], dr)
    ctx["drawer"] = dr
    # the framed bookshelf photo (a photo of shelves, no people): the sea-green spine is the plant
    fx, fz = -3.2, 1.5
    b("pframe", (fx - 0.34, 4.36, fz - 0.26), (fx + 0.34, 4.4, fz + 0.26), M["trim"])
    b("pbg", (fx - 0.3, 4.34, fz - 0.22), (fx + 0.3, 4.36, fz + 0.22), M["page"])
    kit_cols = ["#e8605a", "#f2b84a", "#5aa0e8", "#f28a4a", "#c06adf", "#e86aa0", "#d8c8a0", "#9a5a3a"]
    rnd = random.Random(11)
    for row, zb in enumerate((fz - 0.2, fz + 0.02)):
        b(f"pshelf{row}", (fx - 0.3, 4.325, zb - 0.012), (fx + 0.3, 4.34, zb), M["wood2"])
        x = fx - 0.28
        k = 0
        while x < fx + 0.25:
            w = rnd.uniform(0.022, 0.036)
            h = rnd.uniform(0.11, 0.17)
            c = kit_cols[(k + row * 3) % len(kit_cols)]
            if row == 1 and k in (3, 4):
                c = "#b48cf2" if k == 3 else "#3f8fff"; h = 0.15
            if row == 1 and k == 6:
                c = "#10c090"; h = 0.17; w = 0.045     # the third diary: sea green, the only teal spine, with a brass clasp
                b("pclasp", (x + 0.012, 4.3, zb + 0.07), (x + w - 0.012, 4.32, zb + 0.1), M["brass"])
                b("pband1", (x, 4.31, zb + 0.015), (x + w, 4.32, zb + 0.022), M["brass"])
                b("pband2", (x, 4.31, zb + h - 0.022), (x + w, 4.32, zb + h - 0.015), M["brass"])
            b(f"pbook{row}{k}", (x, 4.32, zb), (x + w, 4.34, zb + h), kit.plastic(c, 0.6, f"pb{c}", 0.2))
            x += w + 0.004
            k += 1
    # nightstand + clock
    b("nstand", (-0.5, 2.7, 0.0), (-0.12, 3.2, 0.5), M["white"], 0.01)
    ck = kit.empty("clock", (-0.31, 2.72, 0.56))
    kit.cyl("clock.face", 0.075, 0.02, (0, 0, 0), M["clockface"], ck, rot=(math.pi / 2, 0, 0), n=28)
    kit.cyl("clock.rim", 0.085, 0.012, (0, 0.006, 0), M["brass"], ck, rot=(math.pi / 2, 0, 0), n=28)
    ck.location = (-0.31, 2.72, 0.595)
    ctx["clockh"] = box(kit, "clock.h", (-0.004, -0.02, -0.003), (0.004, -0.0, 0.035), M["hand"], ck)
    ctx["clockm"] = box(kit, "clock.m", (-0.003, -0.02, -0.003), (0.003, -0.0, 0.058), M["hand"], ck)
    for p in (ctx["clockh"], ctx["clockm"]):
        p.location = (0, -0.012, 0)
    ctx["clockg"] = ck
    ck2 = kit.empty("clock2", (0.13, 2.2, 1.55))
    ck2.rotation_euler = (0, 0, math.radians(90))
    kit.cyl("clock2.face", 0.15, 0.02, (0, 0, 0), M["clockface"], ck2, rot=(math.pi / 2, 0, 0), n=28)
    kit.cyl("clock2.rim", 0.17, 0.012, (0, 0.006, 0), M["brass"], ck2, rot=(math.pi / 2, 0, 0), n=28)
    ctx["clockh2"] = box(kit, "clock2.h", (-0.008, -0.04, -0.006), (0.008, 0.0, 0.07), M["hand"], ck2)
    ctx["clockm2"] = box(kit, "clock2.m", (-0.006, -0.04, -0.006), (0.006, 0.0, 0.115), M["hand"], ck2)
    for p in (ctx["clockh2"], ctx["clockm2"]):
        p.location = (0, -0.02, 0)
    for k in range(12):
        a = k * math.pi / 6
        o = box(kit, f"clock2.t{k}", (-0.006, -0.03, 0.112), (0.006, -0.026, 0.14), M["hand"], ck2)
        o.location = (0, 0, 0)
        o.rotation_euler = (0, a, 0)
        o.location = (0, 0, 0)
    for k in range(12):      # hour ticks (glyphs, not numbers)
        a = k * math.pi / 6
        o = box(kit, f"clock.t{k}", (-0.003, -0.016, 0.058), (0.003, -0.013, 0.07), M["hand"], ck)
        o.location = (0, 0, 0)
    for o in ck.children:
        pass
    # Nina's room: shelf, dresser shoved to the wall, lamps 2 and 3
    sx0, sx1 = 2.9, 4.1
    for nm, lo, hi in (("nsl", (sx0, 4.0, 0), (sx0 + 0.04, 4.4, 1.8)), ("nsr", (sx1 - 0.04, 4.0, 0), (sx1, 4.4, 1.8))):
        b(nm, lo, hi, M["white"])
    for k, z in enumerate((0.04, 0.55, 0.95, 1.4, 1.78)):
        b(f"nsh{k}", (sx0, 4.0, z - 0.02), (sx1, 4.4, z + 0.02), M["white"])
    ncols = ["#ff9ac8", "#ffd95a", "#7ac6ff", "#8ae0a0", "#ff8f6b"]
    rnd = random.Random(21)
    for z in (0.06, 1.0, 1.42):
        x = sx0 + 0.06
        k = 0
        while x < sx1 - 0.1:
            w = rnd.uniform(0.03, 0.05)
            b(f"nbook{z}{k}", (x, 4.1, z), (x + w, 4.36, z + rnd.uniform(0.18, 0.32)), kit.plastic(ncols[k % 5], 0.6, f"nb{k % 5}", 0.2))
            x += w + 0.004
            k += 1
    b("ndresser", (0.12, 2.3, 0.0), (0.62, 3.2, 0.8), M["chair_l"], 0.015)
    for k in range(3):
        b(f"ndrw{k}", (0.62, 2.35, 0.1 + k * 0.23), (0.64, 3.15, 0.3 + k * 0.23), M["white"])
    kit.cyl("scuff", 0.01, 0.002, (1.2, 2.75, 0.014), M["dust"], None)
    # lamps 2 (floor, by the door) and 3 (on the dresser)
    kit.cyl("fl.pole", 0.015, 1.4, (3.9, 0.5, 0.7), M["black"], None)
    kit.cyl("fl.base", 0.12, 0.02, (3.9, 0.5, 0.01), M["black"], None)
    ctx["n2em"] = kit.cyl("fl.shade", 0.16, 0.22, (3.9, 0.5, 1.5), kit.emit("#ffc470", 0.01, "shade n2"), None, r2=0.1)
    ctx["n3em"] = kit.cyl("dl.shade", 0.09, 0.12, (0.37, 2.75, 0.92), kit.emit("#ffc470", 0.01, "shade n3"), None, r2=0.045)
    kit.cyl("dl.base", 0.05, 0.02, (0.37, 2.75, 0.81), M["black"], None)
    # Nina's desk lamp shade gets its own emission so lamp 1 can come on
    n1 = bpy.data.objects.get("lampshade1")
    n1.data.materials.clear()
    ctx["m_n1"] = kit.emit("#ffc470", 0.01, "shade n1")
    n1.data.materials.append(ctx["m_n1"])
    # the strip of light under Nina's door and the glow it throws on the hall floor
    ctx["strip"] = box(kit, "doorstrip", (1.17, -0.1, 0.004), (2.03, 0.1, 0.03), M["strip"])
    ctx["glow"] = box(kit, "doorglow", (1.15, -0.8, 0.018), (2.05, -0.05, 0.022), kit.emit("#ffd08a", 0.01, "glow n"))
    # a wastebasket
    kit.cyl("waste", 0.14, 0.34, (0.9, 1.0, 0.17), M["white"], None, n=16)
    b("deskpad", (-0.7, 1.0, 0.76), (-0.58, 1.1, 0.762), M["page"])


def build_zones(kit, ctx, M):
    G = ctx["G"]

    def b(name, lo, hi, mat, bevel=0.0):
        return box(kit, name, lo, hi, mat, None, bevel)
    # GIFT: a bright party table
    b("gift floor", (GIFT - 3, -3, -0.1), (GIFT + 3, 3, 0), M["hallfloor"])
    b("gift wall", (GIFT - 3, 1.6, 0), (GIFT + 3, 1.7, 3), M["mint"])
    b("gift table", (GIFT - 0.8, -0.45, 0.72), (GIFT + 0.8, 0.45, 0.76), M["yellow"], 0.01)
    for sx in (-1, 1):
        for sy in (-1, 1):
            b(f"gl{sx}{sy}", (GIFT + 0.74 * sx - 0.03, 0.4 * sy - 0.03, 0.0), (GIFT + 0.74 * sx + 0.03, 0.4 * sy + 0.03, 0.72), M["wood2"])
    for k, c in enumerate(("#ff6a8a", "#5ac8ff", "#ffd95a", "#b48cf2", "#7ae0a0")):
        x = GIFT - 0.9 + 0.45 * k
        kit.sphere(f"balloon{k}", 0.17, (x, 1.1, 1.7 + 0.12 * (k % 2)), kit.plastic(c, 0.2, f"bal{c}", 0.7))
        kit.cyl(f"bstr{k}", 0.003, 1.0, (x, 1.1, 0.95 + 0.06 * (k % 2)), M["white"], None, n=6)
    rnd = random.Random(2)
    for k in range(18):
        c = ("#ff6a8a", "#5ac8ff", "#ffd95a", "#b48cf2")[k % 4]
        x, y = GIFT + rnd.uniform(-0.7, 0.7), rnd.uniform(-0.38, 0.38)
        b(f"conf{k}", (x, y, 0.76), (x + 0.025, y + 0.012, 0.764), kit.plastic(c, 0.6, f"cf{c}", 0.1))
    # CAR: the dented door
    b("car floor", (CAR - 4, -4, -0.1), (CAR + 4, 1, 0), kit.concrete("#b8bcc4", 1.5, 0.2, "drive"))
    b("car sky wall", (CAR - 4, 1, 0), (CAR + 4, 1.2, 4), M["mint"])
    b("car body", (CAR - 2.1, -0.9, 0.38), (CAR + 2.1, 0.9, 1.0), M["car"], 0.12)
    b("car cabin", (CAR - 1.1, -0.82, 1.0), (CAR + 0.9, 0.82, 1.5), M["car"], 0.12)
    b("car glass", (CAR - 1.0, -0.86, 1.05), (CAR + 0.8, -0.8, 1.42), M["carglass"], 0.03)
    for sx in (-1, 1):
        kit.cyl(f"wheel{sx}", 0.36, 0.2, (CAR + 1.2 * sx, -0.9, 0.36), M["tyre"], None, rot=(math.pi / 2, 0, 0), n=20)
    # the dented door panel: a sunken patch with fold lines and a scraped scuff
    b("door seam a", (CAR - 0.6, -0.915, 0.4), (CAR - 0.585, -0.9, 0.98), M["tyre"])
    b("door seam b", (CAR + 0.5, -0.915, 0.4), (CAR + 0.515, -0.9, 0.98), M["tyre"])
    b("dent", (CAR - 0.36, -0.88, 0.46), (CAR + 0.3, -0.86, 0.84), M["dent"], 0.05)
    for k, (dx, dz, rz) in enumerate(((-0.1, 0.65, 0.5), (0.05, 0.6, -0.4), (-0.02, 0.52, 0.1))):
        o = kit.box(f"fold{k}", (0.34, 0.03, 0.02), (CAR + dx, -0.935, dz), kit.plastic("#8a1f1a", 0.5, "fold", 0.2), None, rot=(0, rz, 0))
    kit.box("scuff2", (0.22, 0.02, 0.05), (CAR + 0.1, -0.94, 0.5), kit.plastic("#f4e8d8", 0.7, "scuff", 0.0), None, rot=(0, -0.3, 0))
    # WORK: a counter with a till and a stack of bags
    b("work floor", (WORK - 3, -3, -0.1), (WORK + 3, 3, 0), M["floor"])
    b("work wall", (WORK - 3, 1.2, 0), (WORK + 3, 1.3, 3), M["wall_h"])
    b("counter", (WORK - 1.0, 0.45, 0.0), (WORK + 1.0, 0.95, 1.0), M["chair_b"], 0.02)
    b("counter top", (WORK - 1.05, 0.4, 1.0), (WORK + 1.05, 1.0, 1.05), M["white"], 0.01)
    b("till", (WORK + 0.3, 0.55, 1.05), (WORK + 0.7, 0.85, 1.25), M["black"], 0.02)
    b("till screen", (WORK + 0.34, 0.52, 1.12), (WORK + 0.66, 0.55, 1.22), M["clockface"])
    for k in range(4):
        b(f"bag{k}", (WORK - 0.8 + 0.05 * k, 0.55, 1.05 + 0.1 * k), (WORK - 0.45 + 0.05 * k, 0.85, 1.15 + 0.1 * k), kit.plastic("#ffd95a", 0.8, "bag", 0.1), 0.02)
    for k in range(5):
        b(f"shelfbox{k}", (WORK - 1.4 + 0.5 * k, 1.1, 1.3), (WORK - 1.1 + 0.5 * k, 1.2, 1.7), kit.plastic(("#ff9ac8", "#7ac6ff", "#ffd95a", "#8ae0a0", "#ff8f6b")[k], 0.6, f"sb{k}", 0.1))
    # PAIR: a table to lay both diaries open
    b("pair floor", (PAIR - 3, -3, -0.1), (PAIR + 3, 3, 0), M["floor"])
    b("pair wall", (PAIR - 3, 1.2, 0), (PAIR + 3, 1.3, 3), M["wall_b"])
    b("pair table", (PAIR - 0.8, -0.45, 0.72), (PAIR + 0.8, 0.45, 0.76), M["desk"], 0.008)
    for sx in (-1, 1):
        b(f"pl{sx}", (PAIR + 0.74 * sx - 0.03, -0.4, 0.0), (PAIR + 0.74 * sx + 0.03, -0.34, 0.72), M["wood2"])


def build_lights(kit, ctx):
    L = kit.light
    L("mfill", "AREA", (-2.3, 2.2, 2.55), 70, "#fff0dc", size=3.6)
    L("nfill", "AREA", (2.3, 2.2, 2.55), 70, "#fff0f6", size=3.6)
    L("hfill", "AREA", (0.0, -1.1, 2.55), 90, "#fff4e4", size=3.0)
    sp = L("mlamp", "SPOT", (-0.3, 1.0, 1.1), 1.0, "#ffcc7a", size=0.1, spot=70, blend=0.8)
    kit.aim(sp, (-0.46, 1.5, 0.78))
    sp = L("nlamp1", "SPOT", (0.3, 1.0, 1.1), 1.0, "#ffcc7a", size=0.1, spot=70, blend=0.8)
    kit.aim(sp, (0.46, 1.5, 0.78))
    L("nlamp2", "POINT", (3.8, 0.7, 1.5), 20, "#ffcc7a", size=0.2)
    L("nlamp3", "POINT", (0.37, 2.75, 1.1), 10, "#ffcc7a", size=0.1)
    L("strip", "AREA", (1.6, -0.4, 0.3), 15, "#ffcc7a", size=0.8)
    sp = L("mom", "SPOT", (-1.6, 1.5, 1.9), 3, "#ffe8d0", size=0.2, spot=50, blend=0.6)
    kit.aim(sp, (-1.5, -0.55, 1.5))
    L("gift", "AREA", (GIFT, -0.5, 2.4), 110, "#fff4e0", size=3.0)
    L("giftkey", "SPOT", (GIFT + 0.3, -1.4, 1.8), 10, "#ffe0b0", size=0.2, spot=50, blend=0.6)
    L("car", "AREA", (CAR, -2.5, 3.0), 300, "#fff8ee", size=4.0)
    L("work", "AREA", (WORK, -1.0, 2.6), 120, "#fff6ea", size=3.0)
    L("pair", "AREA", (PAIR, -0.5, 2.4), 40, "#fff2e0", size=3.0)
    sp = L("pairlamp", "SPOT", (PAIR, -0.3, 1.2), 1.5, "#ffcc7a", size=0.1, spot=80, blend=0.8)
    kit.aim(sp, (PAIR, 0.0, 0.78))
    # soft fill for the standing figures in the rooms
    L("mface", "AREA", (-1.8, 0.6, 2.2), 40, "#fff0e0", size=2.0)
    L("nface", "AREA", (1.8, 0.6, 2.2), 40, "#fff0f4", size=2.0)


# placements: name -> (centre, yaw degrees)
PLACE = {
    "desk": ((-0.46, 1.5, 0.76), -90.0),
    "ndesk": ((0.46, 1.5, 0.76), 90.0),
    "gift": {"blue": ((GIFT + 0.14, 0.0, 0.76), 170.0), "lilac": ((GIFT - 0.14, 0.0, 0.76), 8.0)},
    "touch": {"blue": ((GIFT + 0.071, 0.0, 0.76), 180.0), "lilac": ((GIFT - 0.071, 0.0, 0.76), 0.0)},
    "pair": {"blue": ((PAIR - 0.15, 0.0, 0.76), 0.0), "lilac": ((PAIR + 0.15, 0.0, 0.76), 0.0)},
    "nshelf": ((3.42, 4.12, 0.57), 0.0),
    "ndeskdust": ((0.46, 1.5, 0.76), 90.0),
    "nightstand": ((-0.33, 2.95, 0.5), 20.0),
    "edge": ((0.72, 1.1, 0.76), 90.0),
    "toyou": ((0.7, 1.2, 0.76), 90.0),
}


def _held(tl, who, t, openv):
    s = ac.state(tl, who, t, 0)
    yaw = s["yaw"]
    c, sn = math.cos(yaw), math.sin(yaw)
    # character front is local -y: world offset of (0, -0.3) rotated by yaw
    fx, fy = 0.3 * sn, -0.3 * c
    return (s["x"] + fx, s["y"] + fy, s["z"] + 1.0), math.degrees(yaw)


def diary_pose(tl, ctx, d, t):
    """(centre, rotation Euler, open) of diary d at t, interpolating the last 'place' cue's dur."""
    cs = [c for c in _cues(tl, "place") if c["d"] == d and c["t"] <= t + 1e-9]

    def at(c, tt):
        to = c["to"]
        if to == "held":
            who = c.get("who", "me")
            pos, yaw = _held(tl, who, tt, 0)
            return pos, Euler((math.radians(78), 0, math.radians(yaw)))
        if to == "drawer":
            slide = _level(tl, "drawer", tt, 0.0)
            return (-3.2 + 0.0, 4.12 - 0.36 * slide, 0.66 + 0.0), Euler((0, 0, math.radians(90)))
        p = PLACE[to]
        if isinstance(p, dict):
            p = p[d]
        return p[0], Euler((0, 0, math.radians(p[1])))
    if not cs:
        return at({"to": "desk"}, t)
    c = cs[-1]
    cur = at(c, t)
    if c.get("dur", 0) > 0 and len(cs) > 1 and t < c["t"] + c["dur"]:
        prev = at(cs[-2], t)
        u = _ss((t - c["t"]) / c["dur"])
        pos = tuple(a + (b - a) * u for a, b in zip(prev[0], cur[0]))
        ea = prev[1].to_quaternion().slerp(cur[1].to_quaternion(), u).to_euler()
        return pos, ea
    return cur


def build(kit, story, tl):
    ctx = {}
    M = materials(kit)
    ctx["M"] = M
    build_home(kit, ctx, M)
    build_rooms(kit, ctx, M)
    build_zones(kit, ctx, M)
    build_lights(kit, ctx)
    ctx["blue"] = build_diary(kit, M, "diary_blue", "blue", False)
    ctx["lilac"] = build_diary(kit, M, "diary_lilac", "lilac", True)
    ctx["pen_blue"] = build_penhand(kit, M, "pen_blue", "#4fa9ff", "#2f7cff")
    ctx["pen_lilac"] = build_penhand(kit, M, "pen_lilac", "#c7a6ff", "#a678ff")
    ctx["seg"], _ = row_segments(tl)
    # glints (clasp sparkles)
    gl = kit.empty("glint", (0, 0, -9))
    for k, a in enumerate((0.0, math.pi / 2)):
        o = box(kit, f"glint{k}", (-0.02, -0.002, -0.002), (0.02, 0.002, 0.002), M["glint"], gl)
        o.rotation_euler = (0, a, 0)
    ctx["glint"] = gl
    # Nina's lanyard and ponytail
    try:
        from blocky import rig
        ch = rig.CHARS.get("nina")
    except Exception:
        ch = None
    ctx["nina_acc"] = False
    build_hud(kit, M, ctx)
    ctx["hudobjs"] = ctx["hud1"].objs + ctx["hud2"].objs
    # the marker follows the camera: re-place it whenever the camera is placed (the lens sets its size)
    orig = kit.place_camera

    def place_camera(loc, target, lens, roll=0.0):
        orig(loc, target, lens, roll)
        place_hud(ctx, lens, True)
    kit.place_camera = place_camera
    return ctx


_acc_done = set()


def _accessories(kit, ctx):
    """Nina's lanyard and low ponytail, once her rig exists."""
    if "nina" in _acc_done:
        return
    tor = bpy.data.objects.get("nina.torso")
    if tor is None:
        return
    _acc_done.add("nina")
    M = ctx["M"]
    teal = kit.plastic("#1fb8a8", 0.6, "lanyard", 0.1)
    for sx in (-1, 1):
        o = kit.box(f"nina.lan{sx}", (0.1, 0.06, 1.3), (sx * 0.35, -0.53, 1.35), teal, tor, rot=(0, sx * 0.25, 0))
    kit.box("nina.badge", (0.45, 0.04, 0.6), (0, -0.55, 0.75), kit.plastic("#ffffff", 0.5, "badge", 0.1), tor, bevel=0.02)
    kit.box("nina.badgeline", (0.3, 0.02, 0.06), (0, -0.58, 0.85), kit.plastic("#7a7a90", 0.5, "badge ln", 0.1), tor)
    head = next((o for o in bpy.data.objects if o.name.startswith("nina.") and "head" in o.name and o.type == "EMPTY"), None)
    hair = kit.plastic("#2a1a22", 0.65, "pony", 0.1)
    par = head or tor
    z = 1.0 if head is None else -0.25
    kit.box("nina.pony", (0.32, 0.32, 0.9), (0, 0.78, z), hair, par, bevel=0.1)
    kit.box("nina.band", (0.38, 0.38, 0.1), (0, 0.78, z + 0.35), kit.plastic("#c7a6ff", 0.5, "band", 0.1), par, bevel=0.03)


def _set_wall_cam_vis(ob, vis):
    try:
        ob.visible_camera = vis
    except Exception:
        ob.hide_render = not vis


def animate(kit, story, tl, t, ctx):
    from blocky import kit as K
    M = ctx["M"]
    _accessories(kit, ctx)
    shot = _shot(tl, t)
    look = (story.get("shotlook") or {}).get(shot["id"], {})
    for o in ctx["sharedwall"]:
        _set_wall_cam_vis(o, not look.get("cutwall", False))
    for o in ctx["ceil"]:
        o.hide_render = bool(look.get("noceil", False))
    ctx["hudoff"] = tuple(look.get("hud", (0.0, 0.0)))
    # doors, drawer, clock
    ctx["mydoor"].rotation_euler = (0, 0, math.radians(_level(tl, "mydoor", t, 0.0)))
    ctx["ndoor"].rotation_euler = (0, 0, -math.radians(_level(tl, "ndoor", t, 0.0)))
    dslide = _level(tl, "drawer", t, 0.0)
    ctx["drawer"].location = (0, -0.36 * dslide, 0)
    ck = [c for c in _cues(tl, "clock") if c["t"] <= t + 1e-9]
    h, m = (ck[-1]["h"], ck[-1]["m"]) if ck else (12, 0)
    ctx["clockh"].rotation_euler = (0, 0, 0)
    ang_h = -(h % 12 + m / 60) * math.pi / 6
    ang_m = -m * math.pi / 30
    # hands lie in the clock's local XZ plane (face looks along -y): rotate about y
    ctx["clockh"].rotation_euler = (0, -ang_h, 0)
    ctx["clockm"].rotation_euler = (0, -ang_m, 0)
    ctx["clockh2"].rotation_euler = (0, -ang_h, 0)
    ctx["clockm2"].rotation_euler = (0, -ang_m, 0)
    # lamps: Nina's come on in turn (each ramps over 0.4 s)
    g1 = _level(tl, "lamp", t, 0.0, n="n1")
    g2 = _level(tl, "lamp", t, 0.0, n="n2")
    g3 = _level(tl, "lamp", t, 0.0, n="n3")
    ctx["m_n1"].node_tree.nodes["Emission"].inputs["Strength"].default_value = 0.2 + 2.2 * g1
    ctx["n2em"].data.materials[0].node_tree.nodes["Emission"].inputs["Strength"].default_value = 0.2 + 2.2 * g2
    ctx["n3em"].data.materials[0].node_tree.nodes["Emission"].inputs["Strength"].default_value = 0.2 + 2.2 * g3
    ctx["strip"].data.materials[0].node_tree.nodes["Emission"].inputs["Strength"].default_value = 7.0 * g1
    ctx["glow"].data.materials[0].node_tree.nodes["Emission"].inputs["Strength"].default_value = 2.2 * g1
    over = {"nlamp1": g1, "nlamp2": g2, "nlamp3": g3, "strip": g1 * (1 - _level(tl, "ndoor", t, 0.0) / 80.0 * 0 ),
            "nfill": 0.55 + 0.45 * max(g1, g2, g3), "mom": 1.0 if "mom" in tl["acting"] else 0.0}
    # who is lit where: far rooms only light when they are on screen (cheaper, cleaner)
    # the keys
    kc = [c for c in _cues(tl, "keys") if c["t"] <= t + 1e-9]
    ctx["keys"].location = (0.0, -2.0, 0.76) if not kc or kc[-1]["to"] == "table" else (2.2, 2.15, 0.012)
    # diaries
    for d in ("blue", "lilac"):
        D = ctx[d]
        pos, rot = diary_pose(tl, ctx, d, t)
        op = _level(tl, "open", t, 0.0, d=d)
        mat = rot.to_matrix()
        shift = (1 - op) * W / 2
        off = mat @ V((shift, 0, 0))
        D["root"].location = (pos[0] - off.x, pos[1] - off.y, pos[2] - off.z)
        D["root"].rotation_euler = rot
        D["front"].rotation_euler = (0, -math.pi * op, 0)
        place = [c for c in _cues(tl, "place") if c["d"] == d and c["t"] <= t + 1e-9]
        to = place[-1]["to"] if place else "desk"
        for o in D["rib"]:
            o.hide_render = not (_switch(tl, "ribbon", "on", t, 0) and to == "gift")
        for o in D["dust"]:
            o.hide_render = to not in ("drawer", "nshelf", "ndeskdust")
            if to == "ndeskdust":    # Nina blows the dust off: the specks lift and fade
                u = _ss((t - _blow_t(tl)) / 1.2) if _blow_t(tl) < 1e8 else 0.0
                for k_, o in enumerate(D["dust"]):
                    if "b0" not in o:
                        o["b0"] = tuple(o.location)
                    b0 = o["b0"]
                    o.location = (b0[0] + 0.05 * u * (k_ - 2), b0[1], b0[2] + 0.07 * u * (1 + k_ % 3))
                    o.scale = (max(0.001, 1 - u),) * 3
                    if u >= 0.98:
                        o.hide_render = True
        D["ink"].root_visible = op > 0.55
        for r in range(ROWS):
            p, col, size, shake = row_state(ctx["seg"], d, r, t)
            if op < 0.55:
                p = 0.0
            D["ink"].set_row(r, p, col, size, shake, t)
        # the marker's page mirrors this diary's state
        H_ = ctx["hud1" if d == "blue" else "hud2"]
        for r in range(ROWS):
            p, col, size, shake = row_state(ctx["seg"], d, r, t)
            H_.ink.set_row(r, p, col, size, shake, t)
    # the marker: second inset, tally
    h2 = _level(tl, "hud2", t, 0.0)
    for o in ctx["hud2"].objs:
        o.hide_render = h2 < 0.5
    n_ans = sum(1 for c in _cues(tl, "answer") if c["t"] <= t + 1e-9)
    last = max([c["t"] for c in _cues(tl, "answer") if c["t"] <= t + 1e-9], default=-9)
    for hk in ("hud1", "hud2"):
        for i, tal in enumerate(ctx[hk].tally):
            vis = i < min(10, n_ans)
            tal.hide_render = not vis or (hk == "hud2" and h2 < 0.5)
            if vis:
                pulse = 1.0 + 0.9 * max(0.0, 1 - (t - last) / 0.5) if i == n_ans - 1 else 1.0
                tal.scale = (pulse, pulse, 1)
    # pens
    for d in ("blue", "lilac"):
        pe = ctx[f"pen_{d}"]
        on = _switch_d(tl, "pen", d, t)
        D = ctx[d]
        if not on:
            pe["root"].location = (0, 0, -9)
            continue
        fr = _frontier(ctx["seg"], tl, d, t)
        x0, ytop = 0.016, H - 0.026
        row, prog = fr
        lp = V((x0 + prog * (COLS - 1) * 0.0105 + 0.004, ytop - row * 0.0235 + 0.004, PAGE_TOP + 0.003))
        mw = D["root"].matrix_world if False else Matrix.LocRotScale(D["root"].location, D["root"].rotation_euler, None)
        wp = mw @ lp
        pe["root"].location = wp
        pe["root"].rotation_euler = D["root"].rotation_euler
    # glint
    gc = [c for c in _cues(tl, "glint") if c["t"] <= t + 1e-9 and t < c["t"] + c.get("dur", 0.6)]
    if gc:
        c = gc[-1]
        u = (t - c["t"]) / c.get("dur", 0.6)
        s = math.sin(math.pi * u) ** 2
        place = [x for x in _cues(tl, "place") if x["d"] == "lilac" and x["t"] <= t + 1e-9]
        ctx["glint"].location = (GIFT, 0.0, 0.79) if t < 60 or True else (0, 0, -9)
        ctx["glint"].scale = (s, s, s)
        ctx["glint"].rotation_euler = (0, 0, 0)
        ctx["glint"].hide_render = s < 0.02
    else:
        ctx["glint"].location = (0, 0, -9)
    return over


def _blow_t(tl):
    cs = _cues(tl, "blow")
    return cs[0]["t"] if cs else 1e9


def _switch(tl, name, key, t, default):
    v = default
    for c in _cues(tl, name):
        if c["t"] <= t + 1e-9 and key in c:
            v = c[key]
    return v


def _switch_d(tl, name, d, t):
    v = 0
    for c in _cues(tl, name):
        if c["t"] <= t + 1e-9 and c.get("d") == d:
            v = c.get("on", 0)
    return v


def _frontier(seg, tl, d, t):
    """(row, progress) where this page's pen is: the row being written, else the next row to write."""
    best = None
    for r in range(ROWS):
        for (t0, t1, p0, p1, c, s, sh) in seg[d][r]:
            if t1 > t0 and t0 - 0.6 <= t <= t1 + 0.2:
                if best is None or t0 > best[0]:
                    p = p0 + (p1 - p0) * _ss((t - t0) / (t1 - t0)) if t >= t0 else 0.0
                    best = (t0, r, min(1.0, max(0.0, p)))
    if best:
        return best[1], best[2]
    last = None
    for r in range(ROWS):
        for (t0, t1, p0, p1, c, s, sh) in seg[d][r]:
            if t1 > t0 and t0 <= t and (last is None or t0 > last[0]):
                last = (t0, r)
    return (min(ROWS - 1, (last[1] + 1) if last else 0), 0.0)
