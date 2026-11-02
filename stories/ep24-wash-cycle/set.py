"""Wash Cycle: an all-night laundromat on a wet corner, and the Turned (ep24; nothing here is shared with another
story's set).

Coordinates (metres, the shop floor is z = 0):
- The shop runs x = -5.4 .. 5.4 (a long room), y = -3.4 (the glass front, the street beyond) .. 3.6 (the back wall).
- Six orange chairs, bolted in a row along x at y = 0, facing +y (the dryers on the back wall). Chair one (x = -3.6) is
  nearest the left end, where I sit at the folding table behind them; chair six (x = 3.65) is the old man's.
  The chairs are 1.45 m apart: two seated avatars are 1.36 m wide, so the Turned in chair five clears Arthur in six.
- The folding table runs along x at y = -2.05 .. -1.25 (top 0.9 m); my stool is at (-3.6, -2.45).
- Twelve front-loaders (two rows of six) fill the right end wall; one more dryer stands against the front wall
  (x = -2.3) behind my stool: the dryer that buzzed. The coat hook panel is beside the glass door (x = -1.25).
- The change machine and the soap machine stand on the left end wall. The side door and its lit stair are on the
  facade at x = -7.5; the stairwell (with his door at the top) is a separate little set at x = -40.

THE TURNED is a cast member (a rig.Character, so it is the same blocks as everyone else), dressed here: laundry-blue
overalls whose bib and two buttons are on its BACK, a white T-shirt, its face drawn on the back of its head (the head
is turned all the way round, so the neat brown haircut faces the dryers), its feet on backwards (the toe caps point
back toward the chair), its arms hung back. Sitting, it faces the dryers like anyone else. It is drawn once and only
placed per shot, so it is the same thing in every shot.

Cues read here (all optional): tubes {"to": 0..1, "dur": s} (the tube lights ramp inside one held shot), drums
{"on": bool}, d7glow {"on"}, d7door {"open": 0..1, "dur"}, coat7 {"on"} (the coat in the end dryer), hook {"a", "b"}
(his green coat, my navy one), stack {"on", "who"} (the wash I carry), tstack {"on", "pos"} (towels on the table),
scarf {"on"}, steam {"on"}.
"""

from __future__ import annotations

import math

import bpy
from mathutils import Vector as V

from blocky import acting as AC
from blocky import faces, rig

S = rig.S
XL, XR, YF, YB, CEIL = -5.4, 6.2, -3.4, 3.6, 2.8
CHX = [round(-3.6 + 1.45 * i, 3) for i in range(6)]
SEAT = 0.465
SIT_Z = -0.045
TB_Y0, TB_Y1, TB_Z = -2.05, -1.25, 0.9
ST = (-40.0, 0.0)
BLUE, ORANGE, GREEN = "#3f7fd0", "#e2742b", "#2f5d43"
TUBE_STRENGTH = 3.0
TUBE_W = 62.0
EYE_GLOW = 3.2


def _ss(x):
    x = min(1.0, max(0.0, x))
    return x * x * (3 - 2 * x)


def _cues(tl, name):
    return [c for c in tl["cues"] if c["name"] == name]


def _switch(cs, attr, t, default):
    v = default
    for c in cs:
        if attr in c and c["t"] <= t + 1e-9:
            v = c[attr]
    return v


def _shot(tl, t):
    for s in tl["shots"]:
        if s["start"] <= t < s["end"]:
            return s
    return tl["shots"][-1]


def _ramp(cs, t, default=1.0):
    """A value that ramps (smoothly) to each cue's "to" over its "dur" seconds, from the value before."""
    v = default
    for c in sorted(cs, key=lambda c: c["t"]):
        d = c.get("dur", 1.0)
        if t >= c["t"] + d:
            v = c["to"]
        elif t > c["t"]:
            v = v + (c["to"] - v) * _ss((t - c["t"]) / d)
            return v
        else:
            break
    return v


# ------------------------------------------------------------------------------------------------ build


def B(kit, name, size, loc, mat, parent=None, bevel=0.0, rot=(0, 0, 0)):
    return kit.box(name, size, loc, mat, parent, rot=rot, bevel=bevel)


def materials(kit):
    M = {}
    M["floor"] = kit.checker("#8c8e93", "#666870", 2.5, "wc floor", 0.28)
    M["tile"] = kit.checker("#d9d6ca", "#cfccc0", 5.0, "wc tile", 0.35)
    M["ceil"] = kit.plastic("#c4c8cc", 0.9, "wc ceiling")
    M["steel"] = kit.metal("#a3a9ae", 0.32, "wc steel")
    M["steel2"] = kit.metal("#7e848a", 0.4, "wc steel dark")
    M["dryer"] = kit.plastic("#c7cbcf", 0.34, "wc dryer body")
    M["orange"] = kit.plastic(ORANGE, 0.38, "wc orange")
    M["table"] = kit.planks("#dcc190", "#b99a66", 1.0, "X", "wc table")
    M["tealout"] = kit.plastic("#2d4650", 0.8, "wc facade")
    M["trim"] = kit.plastic("#d8d2c0", 0.7, "wc trim")
    M["tube"] = kit.emit("#f4eedb", TUBE_STRENGTH, "wc tube")
    M["warm"] = kit.emit("#d79a52", 1.7, "wc dryer glow")
    M["warm2"] = kit.emit("#ffcf90", 2.2, "wc warm plane")
    M["warm3"] = kit.emit("#ffcf90", 0.9, "wc warm room")
    M["washglass"] = kit.emit("#3d5f86", 0.5, "wc wash glass")
    M["lamp"] = kit.emit("#bcd0ff", 6.0, "wc street lamp")
    M["bokeh"] = kit.emit("#a9bfe8", 2.2, "wc bokeh")
    M["bokeh2"] = kit.emit("#e8b27a", 2.2, "wc bokeh warm")
    M["panel"] = kit.emit("#c9e6cf", 1.1, "wc change panel")
    M["black"] = kit.plastic("#0d0f13", 0.6, "wc black")
    M["blue"] = kit.emit(BLUE, 1.6, "wc tally blue")
    M["wet"] = kit.plastic("#171b21", 0.22, "wc wet road")
    M["walk"] = kit.plastic("#3a3f47", 0.3, "wc sidewalk")
    M["brick"] = kit.bricks("#5e3a30", "#4a2c26", "#3a3532", 1.0, "wc brick")
    M["wood"] = kit.plastic("#7a5a3c", 0.7, "wc stair wood")
    M["plaster"] = kit.plastic("#c9bfa6", 0.9, "wc plaster")
    M["btn_l"] = kit.plastic("#b99cf2", 0.4, "wc btn lav")
    M["btn_b"] = kit.plastic("#5a86d6", 0.4, "wc btn blue")
    M["btn_c"] = kit.plastic("#e9e4d0", 0.4, "wc btn cream")
    M["towel_g"] = kit.plastic("#8a8f98", 0.95, "wc towel grey")
    M["towel_w"] = kit.plastic("#d8d6ce", 0.95, "wc towel white")
    M["coat"] = kit.plastic(GREEN, 0.9, "wc coat green")
    M["navy"] = kit.plastic("#26334f", 0.9, "wc coat navy")
    M["lump1"] = kit.plastic("#7c5a46", 0.95, "wc lump1")
    M["lump2"] = kit.plastic("#486a58", 0.95, "wc lump2")
    M["lump3"] = kit.plastic("#8a8f98", 0.95, "wc lump3")
    M["lump4"] = kit.plastic("#6f87a8", 0.95, "wc lump4")
    return M


def build_room(kit, ctx, M):
    # floor, ceiling, walls
    B(kit, "floor", (XR - XL + 6, YB - YF, 0.1), ((XL + XR) / 2, (YF + YB) / 2, -0.05), M["floor"])
    B(kit, "ceiling", (XR - XL, YB - YF, 0.1), ((XL + XR) / 2, (YF + YB) / 2, CEIL + 0.05), M["ceil"])
    B(kit, "wall left", (0.1, YB - YF, CEIL), (XL - 0.05, (YF + YB) / 2, CEIL / 2), M["tile"])
    B(kit, "wall right", (0.1, YB - YF, CEIL), (XR + 0.05, (YF + YB) / 2, CEIL / 2), M["tile"])
    B(kit, "wall back", (XR - XL, 0.1, CEIL), ((XL + XR) / 2, YB + 0.05, CEIL / 2), M["tile"])
    B(kit, "skirt back", (XR - XL, 0.04, 0.12), ((XL + XR) / 2, YB - 0.02, 0.06), M["steel2"])
    # the front: a sill, a header, pillars, a hook panel, a glass door's frame (no glass: the street shows through)
    W = XR - XL
    for nm, z0, z1 in (("sill", 0.0, 0.7), ("header", 2.4, CEIL)):
        B(kit, f"front {nm} out", (W + 0.2, 0.1, z1 - z0), ((XL + XR) / 2, YF - 0.15, (z0 + z1) / 2), M["tealout"])
        B(kit, f"front {nm} in", (W, 0.1, z1 - z0), ((XL + XR) / 2, YF - 0.05, (z0 + z1) / 2), M["tile"])
    for k, x in enumerate((-5.3, -3.0, -0.8, 1.6, 5.3, 6.1)):
        B(kit, f"pillar{k}", (0.2, 0.3, CEIL), (x, YF - 0.1, CEIL / 2), M["steel2"])
    B(kit, "hook panel out", (0.7, 0.1, CEIL), (3.35, YF - 0.15, CEIL / 2), M["tealout"])
    B(kit, "hook panel", (0.7, 0.1, CEIL), (3.35, YF - 0.05, CEIL / 2), M["tile"])
    for k, x in enumerate((3.9, 4.9)):
        B(kit, f"door frame{k}", (0.08, 0.3, CEIL), (x, YF - 0.1, CEIL / 2), M["steel"])
    B(kit, "door push bar", (0.7, 0.05, 0.05), (4.4, YF + 0.12, 1.0), M["steel"])
    # coat hooks and the two coats
    for k, x in enumerate((3.2, 3.5)):
        kit.cyl(f"hook{k}", 0.018, 0.12, (x, YF + 0.06, 1.7), M["steel"], rot=(math.pi / 2, 0, 0), n=10)
        kit.sphere(f"hookb{k}", 0.03, (x, YF + 0.12, 1.7), M["steel"])
    ctx["coat_a"] = coat_prop(kit, "coat_a", M["coat"], (3.2, YF + 0.16, 1.66))
    ctx["coat_b"] = coat_prop(kit, "coat_b", M["navy"], (3.5, YF + 0.16, 1.66))
    # tubes over the room (emissive bars, plus the area lights that really light it)
    for k, x in enumerate((-4.0, -1.35, 1.35, 4.0)):
        for y in (-1.5, 1.4):
            B(kit, f"tube {k}{y}", (1.6, 0.12, 0.06), (x, y, CEIL - 0.05), M["tube"])
            B(kit, f"tube cap {k}{y}", (1.7, 0.2, 0.03), (x, y, CEIL - 0.01), M["steel"])
        kit.light(f"tube{k}", "AREA", (x, -0.1, CEIL - 0.12), TUBE_W, "#e8eef6", size=2.4)
    for k in range(4):
        kit.LIGHTS[f"tube{k}"]["obj"].scale = (1.0, 1.5, 1.0)
    # a soft fill from the table side, so a face turned toward the table is never black
    kit.light("table lamp", "AREA", (-1.0, -2.8, 2.2), 9.0, "#efe6d0", size=3.0)
    kit.aim(kit.LIGHTS["table lamp"]["obj"], (0.0, 0.0, 0.8))
    # the dryers' warm glow (steady), low in front of the dryer wall
    for k, x in enumerate((-2.2, 1.2, 4.0)):
        kit.light(f"dryer glow{k}", "AREA", (x, 2.35, 0.65), 12.0, "#e8a45a", size=1.6)
        kit.aim(kit.LIGHTS[f"dryer glow{k}"]["obj"], (x, -0.5, 0.9))
    kit.light("end glow", "AREA", (-2.3, -2.6, 1.0), 10.0, "#e8a45a", size=0.7)
    kit.aim(kit.LIGHTS["end glow"]["obj"], (-2.3, -1.2, 1.0))
    ctx["tube_mat"] = M["tube"]


def coat_prop(kit, name, mat, loc):
    root = kit.empty(name, loc)
    B(kit, f"{name}.body", (0.46, 0.13, 0.82), (0, 0, -0.45), mat, root, bevel=0.04)
    for sx in (-1, 1):
        B(kit, f"{name}.sl{sx}", (0.14, 0.13, 0.7), (sx * 0.285, 0.0, -0.46), mat, root, bevel=0.02)
    B(kit, f"{name}.col", (0.5, 0.16, 0.1), (0, 0, -0.04), mat, root, bevel=0.04)
    return root


def build_seats(kit, ctx, M):
    # a bolted rail under the chairs, and six orange plastic chairs
    B(kit, "chair rail", (CHX[-1] - CHX[0] + 1.0, 0.06, 0.05), ((CHX[0] + CHX[-1]) / 2, 0.2, 0.2), M["steel2"])
    ctx["chairs"] = []
    for i, x in enumerate(CHX):
        r = kit.empty(f"chair{i + 1}", (x, 0, 0))
        B(kit, f"c{i}.seat", (0.56, 0.5, 0.05), (0, 0.03, 0.44), M["orange"], r, bevel=0.015)
        B(kit, f"c{i}.back", (0.52, 0.05, 0.4), (0, -0.28, 0.72), M["orange"], r, bevel=0.015, rot=(-0.12, 0, 0))
        for sx in (-1, 1):
            for yy in (-0.15, 0.21):
                B(kit, f"c{i}.leg{sx}{yy}", (0.04, 0.04, 0.42), (sx * 0.24, yy, 0.21), M["steel2"], r)
        ctx["chairs"].append(r)
    # the Keeper's tally under chair four: six short upright strokes in laundry blue, one per chair
    for k in range(6):
        B(kit, f"tally{k}", (0.03, 0.21, 0.012), (CHX[3] - 0.175 + 0.07 * k, 0.0, 0.405), M["blue"])
    # my stool
    kit.cyl("stool", 0.2, 0.05, (-3.6, -2.45, 0.46), M["steel"], n=20)
    kit.cyl("stool leg", 0.03, 0.44, (-3.6, -2.45, 0.22), M["steel2"], n=10)
    # the folding table
    B(kit, "table top", (7.6, TB_Y1 - TB_Y0, 0.06), (-0.8, (TB_Y0 + TB_Y1) / 2, TB_Z - 0.03), M["table"], bevel=0.01)
    for lx in (-4.5, 2.9):
        for sy in (TB_Y0 + 0.08, TB_Y1 - 0.08):
            B(kit, f"table leg{lx}{sy}", (0.06, 0.06, TB_Z - 0.06), (lx, sy, (TB_Z - 0.06) / 2), M["steel2"])
    # a plain open book on my end of the table (blank pages), and the jumper fluff on chair six
    B(kit, "book l", (0.2, 0.26, 0.025), (-3.72, -1.6, TB_Z + 0.012), kit.plastic("#e8dfc8", 0.8, "wc page"), bevel=0.006)
    B(kit, "book r", (0.2, 0.26, 0.025), (-3.5, -1.6, TB_Z + 0.012), kit.plastic("#e8dfc8", 0.8, "wc page"), bevel=0.006)
    B(kit, "book cover", (0.44, 0.28, 0.012), (-3.61, -1.6, TB_Z + 0.002), kit.plastic("#4a3a52", 0.6, "wc cover"), bevel=0.006)
    fl = kit.empty("fluff", (CHX[5], 0.0, SEAT))
    gm = kit.plastic("#8b8d93", 0.98, "wc fluff")
    for k, (dx, dy, sz) in enumerate(((-0.1, 0.0, 0.14), (0.05, 0.08, 0.1), (0.12, -0.06, 0.08))):
        B(kit, f"fluff{k}", (sz, sz, sz * 0.5), (dx, dy, sz * 0.25), gm, fl, bevel=0.03, rot=(0, 0, dx * 5))
    ctx["fluff"] = fl
    hc = kit.empty("held coat", (0, 0, -9))
    B(kit, "held body", (0.5, 0.1, 0.8), (0, 0, 0), kit.plastic(GREEN, 0.9, "wc coat green"), hc, bevel=0.04)
    for sx in (-1, 1):
        B(kit, f"held sl{sx}", (0.14, 0.12, 0.6), (sx * 0.32, 0, -0.1), kit.plastic(GREEN, 0.9, "wc coat green"), hc, bevel=0.04)
    ctx["held"] = hc


def build_machines(kit, ctx, M):
    rot_ = {"load": [], "d7": None}
    # six dryers on the back wall
    ctx["dryer_lumps"] = []
    for i, x in enumerate(CHX):
        B(kit, f"dryer{i}", (1.3, 0.9, 1.85), (x, 3.15, 0.925), M["dryer"], bevel=0.02)
        kit.cyl(f"dryer ring{i}", 0.4, 0.08, (x, 2.66, 1.0), M["steel"], rot=(math.pi / 2, 0, 0), n=32)
        kit.cyl(f"dryer glass{i}", 0.31, 0.04, (x, 2.615, 1.0), M["warm"], rot=(math.pi / 2, 0, 0), n=32)
        B(kit, f"dryer panel{i}", (0.9, 0.04, 0.2), (x, 2.68, 1.62), M["steel2"])
        e = kit.empty(f"dryer load{i}", (x, 2.58, 1.0))
        for j, (lm, rr, a) in enumerate((("lump1", 0.17, 0.0), ("lump2", 0.2, 2.1), ("lump3", 0.12, 4.2))):
            B(kit, f"dl{i}{j}", (0.13, 0.04, 0.1), (rr * math.cos(a), 0, rr * math.sin(a)), M[lm], e, bevel=0.015,
              rot=(0, a, 0))
        ctx["dryer_lumps"].append(e)
    # the dryer that buzzed: against the front wall, behind my stool, its door toward the room
    x7, y7 = -2.3, -3.0
    B(kit, "dryer7", (1.3, 0.9, 1.85), (x7, y7 - 0.1, 0.925), kit.plastic("#9ea3a8", 0.34, "wc dryer7 body"), bevel=0.02)
    B(kit, "dryer7 panel", (0.9, 0.04, 0.2), (x7, y7 + 0.37, 1.62), M["steel2"])
    ctx["d7_hinge"] = kit.empty("d7 hinge", (x7 - 0.4, y7 + 0.36, 1.0))
    kit.cyl("d7 ring", 0.4, 0.08, (0.4, 0.0, 0), M["steel"], ctx["d7_hinge"], rot=(math.pi / 2, 0, 0), n=32)
    ctx["d7_glass_mat"] = kit.emit("#d79a52", 1.7, "wc d7 glass")
    kit.cyl("d7 glass", 0.31, 0.04, (0.4, 0.045, 0), ctx["d7_glass_mat"], ctx["d7_hinge"], rot=(math.pi / 2, 0, 0), n=32)
    kit.cyl("d7 drum", 0.31, 0.5, (x7, y7 + 0.1, 1.0), M["black"], rot=(math.pi / 2, 0, 0), n=32)
    ctx["d7_coat"] = kit.empty("d7 coat", (x7, y7 + 0.41, 1.0))
    kit.cyl("d7 hole", 0.33, 0.01, (x7, y7 + 0.355, 1.0), M["black"], rot=(math.pi / 2, 0, 0), n=32)
    B(kit, "d7 coat a", (0.5, 0.1, 0.34), (0, 0, 0), M["coat"], ctx["d7_coat"], bevel=0.04)
    B(kit, "d7 coat b", (0.18, 0.1, 0.36), (0.1, 0, 0.12), M["coat"], ctx["d7_coat"], bevel=0.04, rot=(0, 0.7, 0))
    ctx["d7_loadfloor"] = kit.empty("d7 floor coat", (x7, y7 + 0.45, 0.8))
    B(kit, "d7 fcoat", (0.5, 0.36, 0.1), (0, 0, 0), M["coat"], ctx["d7_loadfloor"], bevel=0.04)
    B(kit, "d7 fcoat2", (0.4, 0.3, 0.08), (0, 0, 0.08), M["coat"], ctx["d7_loadfloor"], bevel=0.04)
    kit.light("d7 inner", "POINT", (x7, y7 + 0.7, 1.0), 14.0, "#e8a45a", size=0.1)
    # twelve front-loaders on the right end wall: two rows of six, each a drum with a load
    ctx["wash"] = []
    for r_ in range(2):
        for c_ in range(6):
            y = -1.9 + 1.0 * c_
            z0 = r_ * 0.98
            B(kit, f"wash{r_}{c_}", (0.9, 0.96, 0.95), (XR - 0.45, y, z0 + 0.475), M["dryer"], bevel=0.02)
            kit.cyl(f"wash ring{r_}{c_}", 0.33, 0.07, (XR - 0.93, y, z0 + 0.5), M["steel"], rot=(0, math.pi / 2, 0), n=28)
            kit.cyl(f"wash glass{r_}{c_}", 0.26, 0.04, (XR - 0.975, y, z0 + 0.5), M["washglass"], rot=(0, math.pi / 2, 0), n=28)
            e = kit.empty(f"wash load{r_}{c_}", (XR - 1.0, y, z0 + 0.5))
            still = r_ == 0 and c_ == 5
            sets = (("lump3", 0.11, 0.0), ("lump4", 0.15, 2.4), ("lump3", 0.08, 4.4)) if still else \
                   (("lump1", 0.1, 0.0), ("lump2", 0.15, 2.2), ("lump4", 0.1, 4.3))
            for j, (lm, rr, a) in enumerate(sets):
                sz = (0.2, 0.05, 0.14) if still else (0.12, 0.04, 0.1)
                B(kit, f"wl{r_}{c_}{j}", (sz[1], sz[0], sz[2]), (0, rr * math.cos(a), rr * math.sin(a)), M[lm], e,
                  bevel=0.02, rot=(a, 0, 0))
            ctx["wash"].append((e, still))
    # the change machine and the soap machine (blank panels, steady light) on the left end wall
    B(kit, "change machine", (0.55, 0.8, 1.55), (XL + 0.28, -0.9, 0.78), M["steel2"], bevel=0.02)
    B(kit, "change panel", (0.03, 0.5, 0.3), (XL + 0.57, -0.9, 1.25), M["panel"])
    B(kit, "change slot", (0.03, 0.3, 0.05), (XL + 0.57, -0.9, 0.95), M["black"])
    B(kit, "change tray", (0.1, 0.3, 0.1), (XL + 0.6, -0.9, 0.55), M["black"])
    kit.light("change glow", "POINT", (XL + 0.9, -0.9, 1.3), 6.0, "#c9e6cf", size=0.1)
    B(kit, "soap machine", (0.6, 0.9, 1.6), (XL + 0.3, 1.0, 0.8), M["steel"], bevel=0.02)
    for r_ in range(3):
        for c_ in range(4):
            m = ("btn_l", "btn_b", "btn_c", "btn_l")[(r_ + c_) % 4]
            B(kit, f"btn{r_}{c_}", (0.03, 0.12, 0.12), (XL + 0.62, 0.72 + 0.19 * c_, 1.3 - 0.2 * r_), M[m], bevel=0.02)
    B(kit, "soap window", (0.03, 0.5, 0.25), (XL + 0.62, 1.0, 0.62), M["panel"])


def build_outside(kit, ctx, M):
    # the facade (to the left, with the side door and its lit stair), the sidewalk, the wet road, a street lamp
    SD = 8.3
    for nm, x0, x1 in (("a", 6.3, 7.8), ("b", 8.8, 11.4)):
        B(kit, f"facade {nm}", (x1 - x0, 0.3, 3.6), ((x0 + x1) / 2, YF - 0.2, 1.8), M["tealout"])
    B(kit, "facade lintel", (1.0, 0.3, 1.5), (SD, YF - 0.2, 2.85), M["tealout"])
    B(kit, "facade left", (3.0, 0.3, 3.6), (-7.0, YF - 0.2, 1.8), M["tealout"])
    B(kit, "roof", (22, 3, 0.3), (0.5, YF + 1.0, 3.7), M["tealout"])
    B(kit, "door recess", (1.0, 0.04, 2.1), (SD, YF + 0.45, 1.05), M["warm2"])
    for k in range(4):
        B(kit, f"outer step{k}", (0.9, 0.3, 0.19 * (k + 1)), (SD, YF + 0.0 + 0.3 * k, 0.095 * (k + 1)), M["wood"])
    B(kit, "side door step", (1.2, 0.5, 0.08), (SD, YF - 0.6, 0.04), M["walk"])
    kit.light("stair glow", "POINT", (SD, YF + 0.1, 1.9), 55.0, "#ffcf90", size=0.2)
    B(kit, "sidewalk", (40, 3.6, 0.1), (0, YF - 1.8 - 0.35, -0.05), M["walk"])
    B(kit, "road", (60, 30, 0.1), (0, YF - 3.6 - 15, -0.2), M["wet"])
    # a street lamp and cold light across the street
    B(kit, "lamp pole", (0.12, 0.12, 4.4), (-3.6, -7.2, 2.2), M["steel2"])
    B(kit, "lamp head", (0.5, 0.3, 0.12), (-3.4, -7.2, 4.45), M["lamp"])
    kit.light("street", "POINT", (-3.2, -7.2, 4.2), 1100.0, "#9db4ff", size=0.3)
    B(kit, "lamp pole2", (0.12, 0.12, 4.4), (7.0, -7.2, 2.2), M["steel2"])
    B(kit, "lamp head2", (0.5, 0.3, 0.12), (6.8, -7.2, 4.45), M["lamp"])
    kit.light("street2", "POINT", (6.6, -7.2, 4.2), 900.0, "#9db4ff", size=0.3)
    # blurs of cold light in the rain, across the street
    for k, (x, y, z, r, m) in enumerate(((1.4, -11.0, 2.2, 0.3, "bokeh"), (-1.0, -13.0, 3.0, 0.45, "bokeh2"), (3.2, -9.0, 1.2, 0.2, "bokeh2"),
                                         (0.2, -15.5, 1.6, 0.55, "bokeh"), (2.6, -12.0, 3.4, 0.35, "bokeh"))):
        kit.sphere(f"bokeh{k}", r, (x, y, z), M[m])
    # far windows across the street (a blur of cold light from inside the shop)
    for k, (x, z, w) in enumerate(((-9, 3.2, 0.9), (-5, 2.2, 0.7), (1, 3.6, 1.1), (6, 2.6, 0.8), (10, 3.0, 0.9))):
        B(kit, f"far win{k}", (w, 0.05, w * 1.3), (x, -16.0, z), M["lamp"] if k % 2 else M["warm2"])
    B(kit, "far wall", (50, 0.5, 9), (0, -16.5, 4.5), M["black"])


def build_stairs(kit, ctx, M):
    """The side stair up to his door: 12 treads rising along +y from (x0, y0), a warm bulb, a landing, and his door
    (a frame, no leaf) onto a warm room."""
    x0, y0 = ST
    for k in range(12):
        B(kit, f"stair{k}", (1.3, 0.28, 0.19 * (k + 1)), (x0, y0 + 0.14 + 0.28 * k, 0.095 * (k + 1)), M["wood"])
    top = 0.19 * 12
    ly = y0 + 0.28 * 12 + 1.5
    B(kit, "landing", (1.3, 1.5, 0.1), (x0, y0 + 0.28 * 12 + 0.75, top - 0.05), M["wood"])
    for sx in (-1, 1):
        B(kit, f"stair wall{sx}", (0.12, 12.0, 6.0), (x0 + sx * 0.72, y0 + 3.0, 3.0), M["plaster"])
    B(kit, "stair ceiling", (1.6, 12.0, 0.1), (x0, y0 + 3.0, 5.0), M["plaster"])
    B(kit, "stair back (street)", (1.6, 0.12, 5.2), (x0, y0 - 1.5, 2.6), M["plaster"])
    # his door: a frame (two posts and a lintel) and the warm room behind it
    for sx in (-1, 1):
        B(kit, f"door post{sx}", (0.12, 0.2, 2.2), (x0 + sx * 0.6, ly, top + 1.1), M["wood"])
    B(kit, "door lintel", (1.32, 0.2, 0.12), (x0, ly, top + 2.2), M["wood"])
    B(kit, "door wall top", (1.6, 0.14, 0.9), (x0, ly, top + 2.7), M["plaster"])
    B(kit, "flat floor", (1.6, 2.8, 0.1), (x0, ly + 1.4, top - 0.05), M["wood"])
    B(kit, "flat back", (1.6, 0.1, 3.0), (x0, ly + 2.8, top + 1.5), M["warm3"])
    B(kit, "bulb", (0.12, 0.12, 0.14), (x0, y0 + 2.4, 3.9), M["warm2"])
    kit.light("stair bulb", "POINT", (x0, y0 + 2.4, 3.7), 110.0, "#ffd0a0", size=0.1)
    kit.light("flat light", "POINT", (x0, ly + 1.6, top + 2.0), 55.0, "#ffd0a0", size=0.2)
    kit.light("landing fill", "AREA", (x0, ly - 1.2, top + 3.2), 60.0, "#e8d8c0", size=1.4)
    ctx["stair_top"] = (x0, ly - 0.6, top)


def build_props(kit, ctx, M):
    # the wash I carry: grey towels with the green coat folded on top (placed by animate)
    st = kit.empty("stack", (0, 0, -9))
    B(kit, "stack towels", (0.5, 0.36, 0.22), (0, 0, 0.0), M["towel_g"], st, bevel=0.03)
    B(kit, "stack towels2", (0.48, 0.34, 0.1), (0, 0, 0.16), M["towel_w"], st, bevel=0.03)
    B(kit, "stack coat", (0.5, 0.36, 0.1), (0, 0, 0.26), M["coat"], st, bevel=0.03)
    ctx["stack"] = st
    ts = kit.empty("tstack", (0, 0, -9))
    for k in range(5):
        B(kit, f"ts{k}", (0.46, 0.34, 0.07), (0, 0, 0.035 + 0.075 * k), M["towel_g" if k % 2 else "towel_w"], ts, bevel=0.025)
    ctx["tstack"] = ts


def build(kit, story, tl):
    ctx = {}
    M = materials(kit)
    ctx["M"] = M
    build_room(kit, ctx, M)
    build_seats(kit, ctx, M)
    build_machines(kit, ctx, M)
    build_outside(kit, ctx, M)
    build_stairs(kit, ctx, M)
    build_props(kit, ctx, M)
    # the Turned's own light (placed by animate on whichever chair it's in): a cool rim from the dryer glass, behind
    # its head, and a low warm key from the table side, below
    # lights that serve one shot only (so its brightness matches its neighbours across the cut)
    kit.light("me lamp", "AREA", (-2.5, -0.9, 2.0), 45.0, "#e8e2d4", size=1.2)
    kit.aim(kit.LIGHTS["me lamp"]["obj"], (-3.6, -2.3, 1.4))
    kit.light("hook lamp", "AREA", (2.8, -1.6, 2.4), 45.0, "#e8e2d4", size=1.0)
    kit.aim(kit.LIGHTS["hook lamp"]["obj"], (3.35, -3.3, 1.3))
    kit.light("stair fill", "AREA", (ST[0], 1.0, 4.3), 90.0, "#ffd8b0", size=1.4)
    kit.aim(kit.LIGHTS["stair fill"]["obj"], (ST[0], 2.6, 1.8))
    kit.light("t rim", "SPOT", (0, 2.2, 1.6), 150.0, "#9fc4ff", size=0.15, spot=38, blend=0.7)
    kit.light("t key", "SPOT", (0, -1.2, 0.35), 260.0, "#d79a52", size=0.12, spot=34, blend=0.7)
    return ctx


# ------------------------------------------------------------------------------------------------ people

SITTERS = ("me", "me0", "arthur", "turned")


def dress(kit, ctx, story):
    """Things added to the rig's people once: the Turned's overalls (bib and buttons on its BACK), toe caps and
    shins for anyone who sits, my collar, Arthur's moustache and scarf, and the Turned's eye light."""
    M = ctx["M"]
    ctx["dressed"] = True
    ctx["shins"] = {}
    ctx["scarf"] = []
    cast = story.get("cast", {})
    for who in SITTERS:
        if who not in cast:
            continue
        spec = cast[who]
        root = bpy.data.objects[who]
        pants = rig.cloth(spec, "pants")
        shoes = kit.plastic(spec.get("shoes", spec.get("pants", "#222222")), 0.6)
        back = who == "turned"
        sh = []
        for sx in (-1, 1):
            shin = B(kit, f"{who}.shin{sx}", (0.98, 1.0, 1.07), (sx * 0.5, -0.8, 0.965), pants, root, bevel=0.08)
            shoe = B(kit, f"{who}.sshoe{sx}", (0.99, 1.01, 0.3), (sx * 0.5, -0.8, 0.28), shoes, root, bevel=0.08)
            toe_y = -0.8 + (0.78 if back else -0.78)       # the Turned's toes point back toward the chair
            toe = B(kit, f"{who}.toe{sx}", (0.9, 0.58, 0.27), (sx * 0.5, toe_y, 0.27), shoes, root, bevel=0.08)
            sh += [shin, shoe, toe]
        ctx["shins"][who] = sh
    if "turned" in cast:
        tor = bpy.data.objects["turned.torso"]
        blue = kit.plastic(BLUE, 0.6, "wc overalls")
        cream = kit.plastic("#e9e0c8", 0.45, "wc overall button")
        B(kit, "t.band", (2.05, 1.05, 0.85), (0, 0, 0.42), blue, tor, bevel=0.06)
        B(kit, "t.bib", (1.34, 0.07, 1.15), (0, 0.54, 1.38), blue, tor, bevel=0.04)
        for sx in (-1, 1):
            B(kit, f"t.strap{sx}", (0.26, 1.08, 0.08), (sx * 0.5, 0, 1.99), blue, tor, bevel=0.03)
            B(kit, f"t.strapf{sx}", (0.26, 0.06, 0.55), (sx * 0.5, -0.53, 1.74), blue, tor, bevel=0.03)
            B(kit, f"t.strapb{sx}", (0.26, 0.06, 0.4), (sx * 0.5, 0.53, 1.78), blue, tor, bevel=0.03)
            kit.cyl(f"t.btn{sx}", 0.11, 0.05, (sx * 0.5, 0.6, 1.72), cream, tor, rot=(math.pi / 2, 0, 0), n=16)
        # a pocket on the bib
        B(kit, "t.pocket", (0.6, 0.05, 0.4), (0, 0.585, 1.2), kit.plastic("#356fb8", 0.6, "wc pocket"), tor, bevel=0.02)
        # the eye whites hold a little light of their own: the brightest thing on it
        hm = kit.MATS["head turned"]
        nt = hm.node_tree
        bsdf = nt.nodes["Principled BSDF"]
        tex = next(n for n in nt.nodes if n.type == "TEX_IMAGE")
        bw = nt.nodes.new("ShaderNodeRGBToBW")
        nt.links.new(tex.outputs["Color"], bw.inputs["Color"])
        ramp = nt.nodes.new("ShaderNodeValToRGB")
        ramp.color_ramp.elements[0].position = 0.86
        ramp.color_ramp.elements[0].color = (0, 0, 0, 1)
        ramp.color_ramp.elements[1].position = 0.93
        ramp.color_ramp.elements[1].color = (1.0, 0.96, 0.88, 1)
        nt.links.new(bw.outputs["Val"], ramp.inputs["Fac"])
        nt.links.new(ramp.outputs["Color"], bsdf.inputs["Emission Color"])
        bsdf.inputs["Emission Strength"].default_value = EYE_GLOW
        bpy.data.objects["turned.head"].scale = (1.0, 1.0, 1.24)
    if "me" in cast:
        tor = bpy.data.objects["me.torso"]
        g = kit.plastic(cast["me"]["shirt"], 0.9)
        B(kit, "me.collar up", (1.5, 0.28, 0.55), (0, 0.42, 2.12), g, tor, bevel=0.1)
        for sx in (-1, 1):
            B(kit, f"me.collar side{sx}", (0.26, 0.85, 0.5), (sx * 0.66, 0.05, 2.1), g, tor, bevel=0.1)
    if "arthur" in cast:
        hd = bpy.data.objects["arthur.headg"]
        white = kit.plastic("#f2f0ea", 0.8)
        B(kit, "arthur.mous", (0.95, 0.16, 0.2), (0, -faces.HEAD_R - 0.01, -0.24), white, hd, bevel=0.07)
        tor = bpy.data.objects["arthur.torso"]
        sc = rig.cloth({"shirt": "#9c3b2e", "pattern": "plaid", "pattern_c": "#e8d9b0"}, "shirt")
        ctx["scarf"] = [B(kit, "arthur.scarf", (2.15, 1.14, 0.4), (0, 0, 1.86), sc, tor, bevel=0.1),
                        B(kit, "arthur.scarft", (0.4, 0.1, 1.0), (0.5, -0.58, 1.3), sc, tor, bevel=0.05)]


def _state(tl, who, t):
    return AC.state(tl, who, t)


def people(kit, ctx, story, tl, t):
    """Sit the sitters (legs out along the seat, shins and shoes down to the floor), and carry the wash."""
    keys_of = tl["acting"]
    for who in SITTERS:
        if who not in story.get("cast", {}) or who not in keys_of:
            continue
        keys = keys_of[who]
        s = AC.state(tl, who, t)
        sit = bool(_switch(keys, "sit", t, False)) and not s["hidden"]
        for ob in ctx["shins"].get(who, []):
            ob.hide_render = not sit
        tor = bpy.data.objects.get(f"{who}.torso")
        if tor is not None:
            tor.rotation_euler = (math.radians(AC._held(keys, "bend", t, 0.0)), 0, 0)
        for sx in (-1, 1):
            leg = bpy.data.objects.get(f"{who}.leg{sx}")
            shoe = bpy.data.objects.get(f"{who}.shoe{sx}")
            if sit:
                leg.rotation_euler = (-math.pi / 2, 0, 0)
                leg.scale = (1.0, 1.0, 1.3 / 1.72)
                if shoe is not None:
                    shoe.hide_render = True
            else:
                leg.scale = (1.0, 1.0, 1.0)
    if "arthur" in story.get("cast", {}):
        on = _switch(_cues(tl, "scarf"), "on", t, False)
        s = AC.state(tl, "arthur", t)
        for ob in ctx["scarf"]:
            ob.hide_render = (not on) or s["hidden"]


def lights_follow_turned(kit, tl, t, over):
    s = AC.state(tl, "turned", t) if "turned" in tl["acting"] else None
    k, r = kit.LIGHTS["t key"]["obj"], kit.LIGHTS["t rim"]["obj"]
    if s is None or s["hidden"]:
        over["t key"] = 0.0
        over["t rim"] = 0.0
        return
    x, y = s["x"], s["y"]
    k.location = (x + 0.35, y - 1.15, 0.42)
    kit.aim(k, (x, y - 0.4, 1.35))
    r.location = (x - 0.2, y + 1.6, 1.9)
    kit.aim(r, (x, y - 0.15, 1.35))
    g = float(_ramp(_cues(tl, "tubes"), t, 1.0))
    over["t key"] = 0.12 + 0.88 * g
    over["t rim"] = 0.12 + 0.88 * g


def animate(kit, story, tl, t, ctx):
    over = {}
    if not ctx.get("dressed"):
        dress(kit, ctx, story)
    people(kit, ctx, story, tl, t)
    # the tubes (a ramp inside one held shot: never across a cut)
    g = float(_ramp(_cues(tl, "tubes"), t, 1.0))
    for k in range(4):
        over[f"tube{k}"] = g
    for n in ctx["tube_mat"].node_tree.nodes:
        if n.type == "EMISSION":
            n.inputs["Strength"].default_value = TUBE_STRENGTH * (0.12 + 0.88 * g)
    over["table lamp"] = 0.4 + 0.6 * g
    sid = _shot(tl, t)["id"]
    over["me lamp"] = 1.0 if sid in story.get("lamp_shots", []) else 0.0
    over["hook lamp"] = 1.0 if sid in story.get("hook_lamp_shots", []) else 0.0
    over["stair fill"] = 1.0 if sid in story.get("stair_fill_shots", []) else 0.0
    lights_follow_turned(kit, tl, t, over)
    # drums: turn while "on" (washers, and the dryers)
    ang, last, on = 0.0, 0.0, True
    for c in sorted(_cues(tl, "drums"), key=lambda c: c["t"]):
        if c["t"] >= t:
            break
        if on:
            ang += c["t"] - last
        last, on = c["t"], bool(c.get("on"))
    if on:
        ang += t - last
    for i, e in enumerate(ctx["dryer_lumps"]):
        e.rotation_euler = (0, 0, 0)
        e.rotation_euler.y = ang * 1.3 + i
    for k, (e, still) in enumerate(ctx["wash"]):
        e.rotation_euler = (0 if still else ang * 1.7 + k, 0, 0)
    # the end dryer: its coat, its door, its glow
    d7 = float(_ramp(_cues(tl, "d7glow"), t, 1.0))
    for n in ctx["d7_glass_mat"].node_tree.nodes:
        if n.type == "EMISSION":
            n.inputs["Strength"].default_value = 0.05 + 1.65 * d7
    over["d7 inner"] = d7
    ctx["d7_coat"].rotation_euler = (0, ang * 0.7, 0)
    op = _ramp([{"t": c["t"], "to": float(c.get("open", 0.0)), "dur": c.get("dur", 0.5)} for c in _cues(tl, "d7door")], t, 0.0)
    ctx["d7_hinge"].rotation_euler = (0, 0, -math.radians(100) * op)
    coat7 = _switch(_cues(tl, "coat7"), "on", t, False)
    ctx["d7_coat"].hide_render = not coat7 or op > 0.2
    for ob in ctx["d7_coat"].children:
        ob.hide_render = ctx["d7_coat"].hide_render
    fl = coat7 and op > 0.2 and _switch(_cues(tl, "coat7"), "floor", t, True)
    ctx["d7_loadfloor"].hide_render = not fl
    for ob in ctx["d7_loadfloor"].children:
        ob.hide_render = not fl
    # the coats on the hook
    for nm, key in (("coat_a", "a"), ("coat_b", "b")):
        on = _switch(_cues(tl, "hook"), key, t, False)
        ctx[nm].hide_render = not on
        for ob in ctx[nm].children:
            ob.hide_render = not on
    # the wash I carry, and the towels on the table
    sk = _switch(_cues(tl, "stack"), "on", t, False)
    if sk:
        s = AC.state(tl, "me0", t)
        fx, fy = math.sin(s["yaw"]), -math.cos(s["yaw"])
        ctx["stack"].location = (s["x"] + fx * 0.58, s["y"] + fy * 0.58, s["z"] + 1.0 + s["bob"])
        ctx["stack"].rotation_euler = (0, 0, s["yaw"])
    else:
        ctx["stack"].location = (0, 0, -9)
    hd = _switch(_cues(tl, "held"), "on", t, False)
    if hd:
        s = AC.state(tl, "me0", t)
        fx, fy = math.sin(s["yaw"]), -math.cos(s["yaw"])
        ctx["held"].location = (s["x"] + fx * 0.36, s["y"] + fy * 0.36, s["z"] + 0.98)
        ctx["held"].rotation_euler = (0, 0, s["yaw"])
    else:
        ctx["held"].location = (0, 0, -9)
    fo = _switch(_cues(tl, "fluff"), "on", t, False)
    ctx["fluff"].location = (CHX[5], 0.0, SEAT if fo else -9)
    ts = _switch(_cues(tl, "tstack"), "on", t, False)
    if ts:
        p = _switch(_cues(tl, "tstack"), "pos", t, [-3.2, -1.65])
        ctx["tstack"].location = (p[0], p[1], TB_Z)
    else:
        ctx["tstack"].location = (0, 0, -9)
    return over
