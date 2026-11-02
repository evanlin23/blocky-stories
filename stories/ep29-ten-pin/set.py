"""Ten Pin: a tired eight-lane bowling alley on league night, and the Spare (ep29). Built from kit.py's parts;
nothing here is shared with another story's set.

Coordinates (metres, the floor is z = 0). Lane i runs down +y at x = -PITCH * i, so our lane is lane 0 against the
right wall (x = +2.2 is the wall) and the others go off to the left (-x). The foul line is y = 0, the head pin is
at y = PIN_Y, and the deck ends in the pit under the charcoal masking unit at y = DECK_END. The approach is
y = -4.6 .. 0 (light maple), then the burgundy squiggle carpet and the mustard seats (y = SEAT_Y), a row of five.
The score screen hangs over the approach at y = SCR_Y facing -y, towards the seats. A character with yaw 0 faces -y,
so seated people (yaw 180) and a bowler look down the lanes (+y).

THE SPARE (script: "The creature"): the team's own R6 blocky body in the teal shirt with a cream side panel and the
teal-and-cream house shoes, with a second identical head stacked straight on its own, no neck. Both faces are the
same flat drawn face. The bottom eyes are always an open flat stare; the top eyes go shut, slit, half, wide. It's
built once (`build_spare`), posed per cue, never moves on screen.

Cues read here (all optional):
- spare: {"lane": 0..3, "pos": [x, y], "eyes": "shut|slit|half|wide", "bot": deg, "top": deg, "glow": 0..2,
  "gap": bool (pins 2 to 6 of our lane stand aside), "hidden": bool}  held from here
- dip: {"down": s, "hold": s, "up": s, "depth": 0.5} the lane lights ease down and back (never lower than depth)
- house: {"rise": s} the warm house lights come up to full over s seconds and stay
- pins: {"act": "up|fall|hide|drop"} our lane's pins from here
- sweep: {"act": "up"} the sweep bar rises over 1 s
- ball: {"path": [[dt, [x, y, z]], ...], "hide": bool} the one ball; it rests at the last point
- show: {"what": name, "on": bool} a prop: shoes (Mags's hands), shirt (Mags's hands), myball, myshoes (my feet),
  myshirt (my torso), nachos (the tray), strokes (always on)
- screen: {"lit5": 0/1, "dim": 0/1, "slide": 0/1, "sixth": 0/1, "dur": s, "n5": cells, "sym5": [...]} the score screen

Acting keys read here (acting.py ignores them): "sit": true bends both legs forward (the R6 sitting pose).
"""

from __future__ import annotations

import math
from pathlib import Path

import bpy
import numpy as np
from mathutils import Matrix, Vector as V
from PIL import Image, ImageDraw, ImageFilter

from blocky import faces, rig

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]

PITCH = 1.6
NL = 8
LW = 1.05
PIN_Y = 14.4
DECK_END = 16.4
SEAT_Y = -5.6
SEAT_H = 0.46
SEATS = [0.15, -0.85, -1.85, -2.85, -3.9]      # x of the five seats: Dev, Tomasz, Mags, Rosie, me
APPROACH_Y0 = -4.6
CEIL = 3.4
SCR = {"x": -1.35, "y": -3.4, "z": 2.35, "w": 1.5, "h": 1.05}
RET = {"x": -0.8, "y": -1.7}                    # our pair's ball return (hood front faces -y)
WALL_R, WALL_L = 2.2, -13.0
TEAL, CREAM, MUSTARD = "#1f8f86", "#efe6d2", "#d9a62e"
SPARE_SKIN = "#c8946c"
PIN_ROWS = [(0, 0), (-0.1525, 0.264), (0.1525, 0.264), (-0.305, 0.528), (0, 0.528), (0.305, 0.528),
            (-0.4575, 0.792), (-0.1525, 0.792), (0.1525, 0.792), (0.4575, 0.792)]


def lane_x(i):
    return -PITCH * i


def _ss(x):
    x = min(1.0, max(0.0, x))
    return x * x * (3 - 2 * x)


def _cues(tl, name):
    return [c for c in tl.get("cues", []) if c["name"] == name]


def _last(cs, t):
    cs = [c for c in cs if c["t"] <= t + 1e-9]
    return cs[-1] if cs else None


def _switch(keys, attr, t, default):
    v = default
    for k in keys:
        if attr in k and k["t"] <= t + 1e-9:
            v = k[attr]
    return v


# ------------------------------------------------------------------------------------------------ materials


def lathe(kit, name, prof, mat, parent=None, n=16):
    verts, fcs = [], []
    for j in range(n):
        a = 2 * math.pi * j / n
        for r, z in prof:
            verts.append((r * math.cos(a), r * math.sin(a), z))
    m = len(prof)
    for j in range(n):
        for i in range(m - 1):
            a, c = j * m + i, ((j + 1) % n) * m + i
            fcs.append((a, c, c + 1, a + 1))
    return kit.mesh_obj(name, verts, fcs, mat, parent, smooth=True)


def pin_mat(kit):
    m = kit._new("pin")
    nt = m.node_tree
    N, L = nt.nodes, nt.links
    b = N["Principled BSDF"]
    b.inputs["Roughness"].default_value = 0.22
    tc = N.new("ShaderNodeTexCoord")
    sep = N.new("ShaderNodeSeparateXYZ")
    L.new(tc.outputs["Object"], sep.inputs[0])

    def band(z0, z1):
        g = N.new("ShaderNodeMath")
        g.operation = "GREATER_THAN"
        g.inputs[1].default_value = z0
        L.new(sep.outputs["Z"], g.inputs[0])
        l_ = N.new("ShaderNodeMath")
        l_.operation = "LESS_THAN"
        l_.inputs[1].default_value = z1
        L.new(sep.outputs["Z"], l_.inputs[0])
        mu = N.new("ShaderNodeMath")
        mu.operation = "MULTIPLY"
        L.new(g.outputs[0], mu.inputs[0])
        L.new(l_.outputs[0], mu.inputs[1])
        return mu.outputs[0]

    a, c = band(0.255, 0.272), band(0.284, 0.301)
    ad = N.new("ShaderNodeMath")
    ad.operation = "ADD"
    ad.use_clamp = True
    L.new(a, ad.inputs[0])
    L.new(c, ad.inputs[1])
    mx = N.new("ShaderNodeMix")
    mx.data_type = "RGBA"
    mx.inputs["A"].default_value = kit.col("#efe6d2")
    mx.inputs["B"].default_value = kit.col("#1f9a8e")
    L.new(ad.outputs[0], mx.inputs["Factor"])
    L.new(mx.outputs["Result"], b.inputs["Base Color"])
    kit._fogged(m, b.outputs[0])
    return m


def squiggle(kit):
    """Burgundy carpet with our own teal and mustard squiggles (wavy bands, two layers)."""
    m = kit._new("squiggle carpet")
    nt = m.node_tree
    N, L = nt.nodes, nt.links
    b = N["Principled BSDF"]
    b.inputs["Roughness"].default_value = 0.95
    tc = N.new("ShaderNodeTexCoord")
    layers = []
    for k, (hexc, scale, ang) in enumerate((("#2a9d8f", 5.0, 0.0), ("#d9a62e", 4.0, 1.1))):
        mp = N.new("ShaderNodeMapping")
        mp.inputs["Rotation"].default_value = (0, 0, ang)
        mp.inputs["Location"].default_value = (k * 0.37, k * 0.21, 0)
        L.new(tc.outputs["Object"], mp.inputs["Vector"])
        wv = N.new("ShaderNodeTexWave")
        wv.wave_type = "BANDS"
        wv.bands_direction = "X"
        wv.inputs["Scale"].default_value = scale
        wv.inputs["Distortion"].default_value = 9.0
        wv.inputs["Detail"].default_value = 1.0
        wv.inputs["Detail Scale"].default_value = 1.5
        L.new(mp.outputs["Vector"], wv.inputs["Vector"])
        rp = N.new("ShaderNodeMapRange")
        rp.inputs["From Min"].default_value = 0.78
        rp.inputs["From Max"].default_value = 0.84
        L.new(wv.outputs["Fac"], rp.inputs["Value"])
        layers.append((rp.outputs["Result"], hexc))
    nz = N.new("ShaderNodeTexNoise")
    nz.inputs["Scale"].default_value = 60.0
    L.new(tc.outputs["Object"], nz.inputs["Vector"])
    base = N.new("ShaderNodeMix")
    base.data_type = "RGBA"
    base.inputs["A"].default_value = kit.col("#3a1838")
    base.inputs["B"].default_value = kit.col("#4b2446")
    L.new(nz.outputs["Fac"], base.inputs["Factor"])
    cur = base.outputs["Result"]
    for sock, hexc in layers:
        mx = N.new("ShaderNodeMix")
        mx.data_type = "RGBA"
        mx.inputs["B"].default_value = kit.col(hexc)
        L.new(cur, mx.inputs["A"])
        L.new(sock, mx.inputs["Factor"])
        cur = mx.outputs["Result"]
    L.new(cur, b.inputs["Base Color"])
    kit._fogged(m, b.outputs[0])
    return m


def materials(kit):
    M = {}
    M["lane"] = kit.planks("#e0a862", "#b9803f", 2.2, "Y", name="lane maple", rough=0.2)
    M["approach"] = kit.planks("#e6b87c", "#c4905a", 1.6, "Y", name="approach maple", rough=0.3)
    M["gutter"] = kit.plastic("#2b2327", 0.3, name="gutter")
    M["cap"] = kit.plastic("#2a2a31", 0.5, name="divider cap")
    M["deck"] = kit.plastic("#c99a62", 0.35, name="pin deck")
    M["arrow"] = kit.plastic("#5a381d", 0.4, name="arrow")
    M["foul"] = kit.plastic("#1d1514", 0.4, name="foul line")
    M["carpet"] = squiggle(kit)
    M["wall"] = kit.grime("#34404c", 0.7, 1.4, name="wall paint", rough=0.85)
    M["wallwood"] = kit.planks("#5b4a3a", "#3e3226", 1.0, "Z", name="wall wood", rough=0.5)
    M["ceiling"] = kit.plastic("#454350", 0.9, name="ceiling")
    M["seat"] = kit.plastic(MUSTARD, 0.5, name="seat")
    M["seatleg"] = kit.metal("#6c6f73", 0.4, name="seat leg")
    M["mask"] = kit.plastic("#1e1f24", 0.8, name="masking")
    M["black"] = kit.plastic("#08080a", 0.9, name="pit black")
    M["pin"] = pin_mat(kit)
    M["ball"] = kit.plastic("#26417f", 0.12, name="ball")
    M["ballhood"] = kit.planks("#b0763f", "#8a5a2c", 3.0, "Z", name="return hood", rough=0.5)
    M["retbody"] = kit.plastic("#3a2a24", 0.5, name="return body")
    M["rail"] = kit.metal("#9a9da0", 0.3, name="rail")
    M["teal"] = kit.emit("#2ec7b3", 0.55, name="tally teal")
    M["tealshoe"] = kit.plastic("#2a9d8f", 0.55, name="house shoe teal")
    M["creamshoe"] = kit.plastic("#efe6d2", 0.55, name="house shoe cream")
    M["cream"] = kit.plastic(CREAM, 0.6, name="cream panel")
    M["tealshirt"] = kit.plastic(TEAL, 0.8, name="teal shirt")
    M["mustard"] = kit.plastic("#cf9a28", 0.85, name="cardigan")
    M["beard"] = kit.plastic("#1f1713", 0.9, name="beard")
    M["bezel"] = kit.plastic("#15161b", 0.5, name="screen bezel")
    M["nacho"] = kit.plastic("#e3a93a", 0.7, name="nachos")
    M["tray"] = kit.plastic("#b9402f", 0.5, name="tray")
    M["table"] = kit.plastic("#4a3a44", 0.5, name="table")
    return M


# ------------------------------------------------------------------------------------------------ the room


def build_room(kit, ctx, M):
    box = kit.box
    # floors
    box("approach", (WALL_R - WALL_L, -APPROACH_Y0, 0.1), ((WALL_R + WALL_L) / 2, APPROACH_Y0 / 2, -0.05), M["approach"])
    box("carpet", (WALL_R - WALL_L, 4.4, 0.1), ((WALL_R + WALL_L) / 2, APPROACH_Y0 - 2.2, -0.05), M["carpet"])
    # shell
    yb = APPROACH_Y0 - 4.5
    box("wall.back.l", (-1.4 - WALL_L, 0.2, CEIL), ((WALL_L - 1.4) / 2, yb, CEIL / 2), M["wall"])
    box("wall.back.r", (WALL_R + 0.1, 0.2, CEIL), ((WALL_R - 0.1) / 2, yb, CEIL / 2), M["wall"])
    box("wall.back.h", (1.3, 0.2, CEIL - 2.2), (-0.75, yb, (CEIL + 2.2) / 2), M["wall"])
    box("outside", (6.0, 0.3, 3.0), (-0.75, yb - 3.0, 1.5), M["black"])
    ctx["doors"] = []
    for side, hx in ((-1, -1.4), (1, -0.1)):    # two leaves, hinged on the jambs, swinging in (+y)
        piv = kit.empty(f"door.p{side}", (hx, yb - 0.05, 0.0))
        kit.box(f"door.leaf{side}", (0.65, 0.05, 2.1), (-side * -0.0 + (0.325 if side < 0 else -0.325), 0, 1.05), M["ballhood"], piv, bevel=0.01)
        ctx["doors"].append((piv, side))
    box("wall.right", (0.2, 28.0, CEIL), (WALL_R + 0.1, 5.0, CEIL / 2), M["wall"])
    box("wall.left", (0.2, 28.0, CEIL), (WALL_L - 0.1, 5.0, CEIL / 2), M["wall"])
    box("ceiling", (WALL_R - WALL_L, 29.0, 0.1), ((WALL_R + WALL_L) / 2, 5.0, CEIL + 0.05), M["ceiling"])
    box("dado.back", (WALL_R - WALL_L, 0.06, 1.0), ((WALL_R + WALL_L) / 2, APPROACH_Y0 - 4.38, 0.5), M["wallwood"])
    box("dado.right", (0.06, 6.0, 1.0), (WALL_R - 0.03, -5.0, 0.5), M["wallwood"])
    for k in range(9):    # painted bands on the back wall, our own squares
        c = M["teal"] if k % 2 else M["mustard"]
        box(f"band{k}", (0.9, 0.04, 0.16), (-11.0 + k * 1.6, APPROACH_Y0 - 4.37, 2.4), c)
    # lanes
    arrow_mesh = [(0, 0), (-0.045, -0.3), (0.045, -0.3)]
    for i in range(NL):
        x = lane_x(i)
        box(f"gut{i}", (PITCH, DECK_END, 0.05), (x, DECK_END / 2, -0.05), M["gutter"])
        box(f"lane{i}", (LW, DECK_END - 1.5, 0.06), (x, (DECK_END - 1.5) / 2, -0.03), M["lane"])
        box(f"deck{i}", (LW + 0.1, 2.0, 0.06), (x, DECK_END - 1.0, -0.03), M["deck"])
        box(f"foul{i}", (LW, 0.04, 0.004), (x, 0.0, 0.002), M["foul"])
        for k in range(7):
            ax = x + (k - 3) * 0.14
            ay = 4.2 - 0.34 * (1 - abs(k - 3) / 3.0)
            ar = kit.mesh_obj(f"arrow{i}.{k}", [(ax + px, ay + py + 0.3, 0.003) for px, py in arrow_mesh],
                              [(0, 2, 1)], M["arrow"])
        box(f"cap{i}", (0.06, DECK_END - 1.5, 0.03), (x + PITCH / 2, (DECK_END - 1.5) / 2, 0.0), M["cap"])
        # the pit and the kickbacks at the deck
        box(f"kick{i}", (0.08, 2.4, 0.5), (x + PITCH / 2, DECK_END - 1.4, 0.2), M["mask"])
    # the pit, the masking unit above it and the back
    w = WALL_R - WALL_L
    box("pit", (w, 1.6, 1.4), ((WALL_R + WALL_L) / 2, DECK_END + 0.8, -0.2), M["black"])
    box("masking", (w, 0.5, 2.3), ((WALL_R + WALL_L) / 2, DECK_END + 0.25, 1.25 + 1.15), M["mask"])
    box("canopy", (w, 3.2, 0.2), ((WALL_R + WALL_L) / 2, DECK_END - 1.35, 3.2), M["mask"])
    box("wall.front", (w, 0.2, CEIL), ((WALL_R + WALL_L) / 2, DECK_END + 1.7, CEIL / 2), M["black"])
    # seats: moulded mustard, a row of five at the back
    for k, sx in enumerate(SEATS):
        box(f"seat{k}", (0.62, 0.5, 0.09), (sx, SEAT_Y - 0.1, SEAT_H - 0.05), M["seat"], bevel=0.03)
        box(f"seatback{k}", (0.62, 0.08, 0.5), (sx, SEAT_Y - 0.4, SEAT_H + 0.18), M["seat"], bevel=0.03)
        box(f"seatleg{k}", (0.12, 0.12, SEAT_H - 0.1), (sx, SEAT_Y - 0.25, (SEAT_H - 0.1) / 2), M["seatleg"])
    box("seatbar", (7.0, 0.1, 0.06), (-1.9, SEAT_Y - 0.25, 0.1), M["seatleg"])
    # the pins: one mesh, ten per lane
    prof = [(0, 0), (0.0485, 0), (0.0575, 0.02), (0.0605, 0.09), (0.0575, 0.15), (0.04, 0.2), (0.025, 0.25),
            (0.0235, 0.285), (0.032, 0.315), (0.0455, 0.345), (0.0455, 0.37), (0.03, 0.385), (0, 0.39)]
    proto = lathe(kit, "pin.proto", prof, M["pin"], n=14)
    mesh = proto.data
    proto.hide_render = True
    ctx["pins"] = {}
    for i in range(NL):
        g = kit.empty(f"pins{i}", (lane_x(i), PIN_Y, 0.0))
        lst = []
        for k, (dx, dy) in enumerate(PIN_ROWS):
            ob = bpy.data.objects.new(f"pin{i}.{k}", mesh)
            ob.location = (dx, dy, 0.0)
            kit.link(ob, g)
            lst.append(ob)
        ctx["pins"][i] = lst
    # the sweep bar, over our lane
    ctx["sweep"] = kit.box("sweep", (LW + 0.2, 0.12, 0.1), (0, PIN_Y - 0.35, 3.15), M["mask"])
    ctx["sweep"].hide_render = False


def build_returns(kit, ctx, M):
    """Ball returns at each pair of lanes, with a wooden hood. Ours has the five teal strokes."""
    ctx["returns"] = []
    for pair in range(4):
        x = -PITCH * (2 * pair) - PITCH / 2
        y = RET["y"]
        for sx, w in ((-1, 0.29), (1, 0.29)):      # the body is two wings round a tunnel the ball comes out of
            kit.box(f"ret{pair}.wing{sx}", (w, 0.7, 0.45), (x + sx * (0.16 + w / 2), y, 0.225), M["retbody"], bevel=0.015)
        kit.box(f"ret{pair}.floor", (0.32, 0.7, 0.12), (x, y, 0.06), M["retbody"])
        kit.box(f"ret{pair}.roof", (0.32, 0.7, 0.07), (x, y, 0.415), M["retbody"])
        kit.box(f"ret{pair}.back", (0.32, 0.04, 0.26), (x, y + 0.3, 0.25), M["black"])
        kit.box(f"ret{pair}.hood", (0.9, 0.7, 0.36), (x, y, 0.63), M["ballhood"], bevel=0.04)
        for s_ in (-1, 1):
            kit.box(f"ret{pair}.rail{s_}", (0.03, 0.9, 0.03), (x + s_ * 0.1, y - 0.78, 0.12), M["rail"])
        ctx["returns"].append((x, y))
    # five teal strokes on the hood front (the lore plant): short, upright, evenly spaced, pressed in
    x, y = RET["x"], RET["y"]
    for k in range(5):
        kit.box(f"stroke{k}", (0.026, 0.01, 0.17), (x + (k - 2) * 0.062, y - 0.352, 0.63), M["teal"], bevel=0.004)
    ball = kit.sphere("ball", 0.109, (0, -9, 0.3), M["ball"], seg=24)
    ctx["ball"] = ball
    for pair in (1, 2):    # a ball in the other racks
        x2, y2 = ctx["returns"][pair]
        kit.sphere(f"restball{pair}", 0.109, (x2, y2 - 0.6, 0.23), M["ball"], seg=16)
    # the lamp housings over each approach, with a warm bulb (its emission follows the lane lights)
    ctx["bulbs"] = []
    for i in range(4):
        lx = lane_x(i)
        kit.cyl(f"lamp{i}.housing", 0.22, 0.2, (lx, -1.4, CEIL - 0.1), M["mask"], n=16)
        bm = kit.emit("#ffcf93", 6.0, name=f"bulb{i}")
        kit.cyl(f"lamp{i}.bulb", 0.15, 0.03, (lx, -1.4, CEIL - 0.21), bm, n=16)
        ctx["bulbs"].append(bm.node_tree.nodes["Emission"].inputs["Strength"])
    # the team's bag (Mags's knee, S66)
    ctx["p_bag"] = [kit.box("bag", (0.6, 0.3, 0.32), (SEATS[2], -5.12, 0.62), M["tealshoe"], bevel=0.05),
                    kit.box("bag.flap", (0.6, 0.3, 0.05), (SEATS[2], -5.12, 0.8), M["creamshoe"], bevel=0.02, rot=(0.5, 0, 0))]


# ------------------------------------------------------------------------------------------------ the screens


def mini_face(d, x, y, s, who, k=1.0):
    skin = {"dev": (141, 90, 60), "rosie": (241, 201, 160), "mags": (232, 195, 160), "tomasz": (198, 138, 98),
            "me": (224, 180, 140)}[who]
    hair = {"dev": (30, 24, 22), "rosie": (181, 69, 31), "mags": (170, 170, 176), "tomasz": (30, 52, 100),
            "me": (74, 47, 29)}[who]
    f = lambda c: tuple(int(v * k) for v in c)
    d.rounded_rectangle([x, y, x + s, y + s], radius=s // 6, fill=f(skin))
    d.rectangle([x, y, x + s, y + s * 0.26], fill=f(hair))
    if who == "mags":
        d.ellipse([x + s * 0.35, y - s * 0.12, x + s * 0.65, y + s * 0.2], fill=f(hair))
    if who == "rosie":
        for q in range(4):
            d.ellipse([x + q * s * 0.24 - 3, y - s * 0.1, x + q * s * 0.24 + s * 0.2, y + s * 0.26], fill=f(hair))
    ink = f((20, 14, 16))
    for ex in (0.3, 0.7):
        d.ellipse([x + s * ex - s * 0.07, y + s * 0.42, x + s * ex + s * 0.07, y + s * 0.56], fill=ink)
    d.line([x + s * 0.32, y + s * 0.78, x + s * 0.68, y + s * 0.78], fill=ink, width=max(2, s // 14))
    if who == "dev":
        for ex in (0.3, 0.7):
            d.rectangle([x + s * ex - s * 0.15, y + s * 0.36, x + s * ex + s * 0.15, y + s * 0.62], outline=ink, width=2)


CELLS = {  # score cells per row: float = a bar's height, "x" a cross, "/" a slash
    0: [0.8, "/", 0.6, "x", 0.9, 0.7],
    1: [0.5, 0.7, "/", 0.8, 0.4, "/"],
    2: [0.9, "x", 0.7, "/", 0.6, 0.8],
    3: [0.6, 0.8, 0.5, "/", 0.9, "x"],
    5: [0.22, 0.12, 0.3, 0.1, 0.26, 0.18],
}
SCR_W, SCR_H = 640, 448
ROWH, ROWG, ROW0 = 66, 6, 11


def screen_image(state) -> np.ndarray:
    """The score screen for one state: six rows of a tiny face and six cells of bars, slashes and crosses. Bars and
    shapes only, no text and no digits. state: lit5, dim, slide, sixth (0..1), n5, sym5."""
    im = Image.new("RGB", (SCR_W, SCR_H), (22, 33, 58))
    d = ImageDraw.Draw(im)
    lit, dim = state["lit5"], state["dim"]
    cream, teal = (239, 230, 210), (58, 214, 192)
    who_rows = ["dev", "rosie", "mags", "tomasz"]
    for r in range(6):
        y0 = ROW0 + r * (ROWH + ROWG)
        k = 0.88 * (1 - 0.62 * dim)
        if r == 4:
            k = 0.88 + 0.12 * lit - 0.0 * dim
            if lit > 0:
                d.rectangle([8, y0 - 3, SCR_W - 8, y0 + ROWH + 3],
                            fill=tuple(int(a + (b - a) * 0.34 * lit) for a, b in zip((22, 33, 58), cream)))
        if r == 5:
            k *= (1 - state["sixth"])
        if k <= 0.01:
            continue
        f = lambda c, kk=k: tuple(int(v * kk) for v in c)
        # the face square
        if r < 4:
            mini_face(d, 20, y0 + 5, 56, who_rows[r], k)
        elif r == 4:
            d.rounded_rectangle([20, y0 + 5, 76, y0 + 61], radius=9, fill=(12, 17, 30), outline=f(cream), width=2)
        # cells
        if r == 4:
            cells = [None] * 6
            syms = state["sym5"]
            for q in range(min(6, state["n5"])):
                s = syms[q] if q < len(syms) else None
                cells[q] = s if s else (0.35 + 0.1 * ((q * 5) % 4))
        elif r == 5:
            cells = CELLS[5]
        else:
            cells = CELLS[r]
        for q, c in enumerate(cells):
            cx0 = 100 + q * 80
            d.rectangle([cx0, y0 + 4, cx0 + 74, y0 + 62], outline=f(cream), width=2)
            if c is None:
                continue
            if c == "x":
                d.line([cx0 + 12, y0 + 12, cx0 + 62, y0 + 54], fill=f(teal), width=7)
                d.line([cx0 + 62, y0 + 12, cx0 + 12, y0 + 54], fill=f(teal), width=7)
            elif c == "/":
                d.line([cx0 + 56, y0 + 10, cx0 + 18, y0 + 56], fill=f(cream), width=7)
            else:
                h = int(c * 50)
                d.rectangle([cx0 + 14, y0 + 58 - h, cx0 + 60, y0 + 58], fill=f(cream))
    # my picture: row 5's square, sliding up into row 4 (the sixth row's own square goes with it)
    u = state["slide"]
    y5, y4 = ROW0 + 5 * (ROWH + ROWG) + 5, ROW0 + 4 * (ROWH + ROWG) + 5
    kme = 0.88 * (1 - 0.62 * dim) if u < 1 else 1.0
    if state["sixth"] < 1 or u > 0:
        mini_face(d, 20, int(y5 + (y4 - y5) * u), 56, "me", max(kme, 0.7 if u > 0 else kme))
    arr = np.asarray(im, np.float32) / 255.0
    arr = np.concatenate([arr, np.ones(arr.shape[:2] + (1,), np.float32)], axis=2)
    return arr[::-1].copy()


def build_screens(kit, ctx, M):
    x, y, z, w, h = SCR["x"], SCR["y"], SCR["z"], SCR["w"], SCR["h"]
    img = bpy.data.images.new("score screen", SCR_W, SCR_H, alpha=False)
    img.colorspace_settings.name = "sRGB"
    ctx["scr_img"] = img
    ctx["scr_key"] = None
    m = kit._new("screen glow")
    nt = m.node_tree
    nt.nodes.remove(nt.nodes["Principled BSDF"])
    tex = nt.nodes.new("ShaderNodeTexImage")
    tex.image = img
    tex.interpolation = "Linear"
    em = nt.nodes.new("ShaderNodeEmission")
    em.inputs["Strength"].default_value = 0.9
    nt.links.new(tex.outputs["Color"], em.inputs["Color"])
    kit._fogged(m, em.outputs[0])
    ctx["scr_strength"] = em.inputs["Strength"]
    ctx["scr_tex"] = tex
    # static dim neighbours on their own image
    dim = bpy.data.images.new("score dim", SCR_W, SCR_H, alpha=False)
    st = {"lit5": 0, "dim": 1, "slide": 0, "sixth": 1, "n5": 0, "sym5": []}
    a = screen_image(st)
    dim.pixels.foreach_set(a.ravel())
    m2 = kit._new("screen dim")
    nt2 = m2.node_tree
    nt2.nodes.remove(nt2.nodes["Principled BSDF"])
    t2 = nt2.nodes.new("ShaderNodeTexImage")
    t2.image = dim
    e2 = nt2.nodes.new("ShaderNodeEmission")
    e2.inputs["Strength"].default_value = 0.35
    nt2.links.new(t2.outputs["Color"], e2.inputs["Color"])
    kit._fogged(m2, e2.outputs[0])
    for sx, mat in ((x, m), (x - PITCH * 1.0 - 0.0, m2), (x - PITCH * 2.0, m2)):
        kit.box(f"scr.bezel@{sx:.1f}", (w + 0.1, 0.08, h + 0.1), (sx, y, z), M["bezel"], bevel=0.02)
        # the face: a plane just in front of the bezel (towards -y), looking at -y
        fx, fy = w / 2, h / 2
        verts = [(sx - fx, y - 0.045, z - fy), (sx + fx, y - 0.045, z - fy), (sx + fx, y - 0.045, z + fy),
                 (sx - fx, y - 0.045, z + fy)]
        ob = kit.mesh_obj(f"scr.face@{sx:.1f}", verts, [(0, 1, 2, 3)], mat)
        uv = ob.data.uv_layers.new(name="UVMap")
        for poly in ob.data.polygons:
            for li, (u, v) in zip(poly.loop_indices, [(0, 0), (1, 0), (1, 1), (0, 1)]):
                uv.data[li].uv = (u, v)
        for rx in (-0.5, 0.5):
            kit.box(f"scr.rod@{sx:.1f}{rx}", (0.03, 0.03, CEIL - z - h / 2), (sx + rx, y, (CEIL + z + h / 2) / 2), M["bezel"])
    ctx["scr_state"] = None


def screen_state(tl, t):
    cs = _cues(tl, "screen")

    def ramp(key, default):
        v = default
        for c in cs:
            if key in c and c["t"] <= t + 1e-9:
                dur = c.get("dur", 0.5)
                v = v + (c[key] - v) * _ss((t - c["t"]) / dur) if dur > 0 else c[key]
        return v

    # ramps must chain from the previous value, so evaluate each in order
    out = {}
    for key, default in (("lit5", 0.0), ("dim", 0.0), ("slide", 0.0), ("sixth", 1.0)):
        v = default
        for c in cs:
            if key in c and c["t"] <= t + 1e-9:
                dur = c.get("dur", 0.5)
                u = _ss((t - c["t"]) / dur) if dur > 0 else 1.0
                v = v + (c[key] - v) * u if u < 1 else c[key]
        out[key] = round(v, 2)
    n5, sym = 0, []
    for c in cs:
        if c["t"] <= t + 1e-9:
            n5 = c.get("n5", n5)
            sym = c.get("sym5", sym)
    out["n5"], out["sym5"] = n5, sym
    return out


# ------------------------------------------------------------------------------------------------ the Spare


def spare_face(skin: str, kind: str):
    """A flat drawn face for the stacked heads: hollow black eyes with a bright pin of light in each, a straight
    mouth, and the eyes by state (shut, slit, half, wide, or the bottom head's open stare). Returns the colour image
    and an emission mask (white where the lights in the eyes are)."""
    W, H = faces.TEX_W, faces.TEX_H
    im = Image.new("RGB", (W, H), faces.hexrgb(skin))
    mk = Image.new("RGB", (W, H), (0, 0, 0))
    d, dm = ImageDraw.Draw(im), ImageDraw.Draw(mk)
    s = faces.FX1 - faces.FX0
    ink = (14, 10, 12)
    hole = (4, 3, 5)
    th = max(12, int(0.04 * s))
    ey = faces._fy(0.42)
    ry_k = {"shut": 0.0, "slit": 0.1, "half": 0.62, "wide": 1.45, "stare": 1.0}[kind]
    for side in (-1, 1):
        cx = faces._fx(0.5) + side * 0.25 * s
        rx = 0.15 * s * (1.12 if kind == "wide" else 1.0)
        if kind == "shut":
            pts = [(cx - rx * 0.9 + rx * 1.8 * i / 12, ey + 0.004 * s) for i in range(13)]
            faces._stroke(d, pts, ink, th * 1.3)
        else:
            ry = max(rx * ry_k, 0.012 * s)
            faces._ellipse(d, cx, ey, rx, ry, fill=hole, outline=ink, width=th // 2)
            gr = (0.034 if kind == "wide" else 0.026 if kind == "stare" else 0.02) * s
            gy = ey + (ry * 0.05 if kind in ("wide", "stare") else 0)
            if kind == "slit":
                faces._stroke(d, [(cx - rx * 0.7, ey), (cx + rx * 0.7, ey)], (255, 255, 255), th * 0.5)
                dm.line([(cx - rx * 0.7, ey), (cx + rx * 0.7, ey)], fill=(255, 255, 255), width=int(th * 0.5))
            else:
                faces._ellipse(d, cx, gy, gr, gr, fill=(255, 255, 255))
                faces._ellipse(dm, cx, gy, gr, gr, fill=(255, 255, 255))
        by = ey - 0.2 * s - 0.04 * s * min(1.2, ry_k)
        faces._brow(d, cx, by + 0.05 * s, 0.2 * s, -0.1, ink, th * 1.4, side)
    my = faces._fy(0.76)
    faces._stroke(d, [(faces._fx(0.5) - 0.2 * s, my), (faces._fx(0.5) + 0.2 * s, my)], ink, th * 1.2)
    return im.filter(ImageFilter.SMOOTH), mk.filter(ImageFilter.GaussianBlur(1.5))


def _emissive_head(mat, strength=0.0):
    nt = mat.node_tree
    b = nt.nodes["Principled BSDF"]
    uv = next(n for n in nt.nodes if n.type == "UVMAP")
    mt = nt.nodes.new("ShaderNodeTexImage")
    nt.links.new(uv.outputs["UV"], mt.inputs["Vector"])
    nt.links.new(mt.outputs["Color"], b.inputs["Emission Color"])
    b.inputs["Emission Strength"].default_value = strength
    return mt, b.inputs["Emission Strength"]


def build_spare(kit, ctx, M):
    wd = ROOT / "out" / "work" / "ep29-ten-pin" / "faces"
    wd.mkdir(parents=True, exist_ok=True)
    spec = {"skin": SPARE_SKIN, "shirt": TEAL, "pattern": "solid", "pants": "#26272c", "shoes": "#2a9d8f",
            "sleeves": "long", "hair": "none", "hat": "none", "width": 0.9, "height": 1.0, "face": {"eyes": "round"}}
    c = rig.Character("spare", spec, wd)
    torso = c.torso
    kit.box("spare.panel", (0.56, 1.03, 1.96), (0.74, 0, 1.0), M["cream"], torso, bevel=0.03)
    for sx in (-1, 1):   # the same house shoes as ours: a cream toe cap on teal
        leg = c.P[f"leg{sx}"]
        kit.box(f"spare.toe{sx}", (1.0, 0.42, 0.32), (0, -0.33, -1.85), M["creamshoe"], leg, bevel=0.06)
    imgs = {}

    def load(kind):
        if kind not in imgs:
            im, mk = spare_face(SPARE_SKIN, kind)
            pc, pm = wd / f"spare-{kind}.png", wd / f"spare-{kind}-mask.png"
            im.save(pc)
            mk.save(pm)
            a, b_ = bpy.data.images.load(str(pc)), bpy.data.images.load(str(pm))
            a.colorspace_settings.name = "sRGB"
            b_.colorspace_settings.name = "Non-Color"
            imgs[kind] = (a, b_)
        return imgs[kind]

    # the bottom head (c.head_mat) is always the open flat stare
    mt1, st1 = _emissive_head(c.head_mat)
    a, b_ = load("stare")
    c.face_tex.image, mt1.image = a, b_
    c.set_face = lambda *x, **k: None
    # the top head: its own pivot (so it can turn on its own), its own material and eyes
    mat2, tex2 = rig.head_material("spare.top", SPARE_SKIN)
    mt2, st2 = _emissive_head(mat2)
    pivot = kit.empty("spare.top", (0, 0, 0), c.neck)
    topg = kit.empty("spare.topg", (0, 0, faces.HEAD_H * 1.5 + 0.04), pivot)
    rig.head_mesh("spare.topm", mat2, topg)
    ctx["spare"] = {"c": c, "pivot": pivot, "load": load, "tex2": tex2, "mt2": mt2, "st1": st1, "st2": st2,
                    "state": None}
    for kind in ("shut", "slit", "half", "wide"):
        load(kind)
    # the key from below and the rim behind
    kit.light("ckey", "SPOT", (0, PIN_Y - 0.6, 0.1), 360.0, "#6fe0cf", spot=26, blend=0.6, size=0.15)
    kit.light("crim", "SPOT", (0, DECK_END + 0.1, 2.9), 300.0, "#a8f0e4", spot=32, blend=0.5, size=0.2)
    return ctx["spare"]


def pose_spare(kit, ctx, tl, t, over):
    sp = ctx["spare"]
    c = sp["c"]
    cue = _last(_cues(tl, "spare"), t)
    hide = cue is None or cue.get("hidden", False)
    for ob in [c.root] + list(c.root.children_recursive):
        ob.hide_render = hide
    # the pins' gap
    gap = bool(cue and cue.get("gap") and not hide)
    for k in (1, 2, 3, 4, 5):
        ctx["pins"][0][k].hide_render = ctx["pins"][0][k].hide_render or gap
    ck, cr = kit.LIGHTS["ckey"], kit.LIGHTS["crim"]
    if hide:
        over["ckey"] = 0.0
        over["crim"] = 0.0
        return
    over["ckey"] = over.get("ckey", 1.0) * cue.get("key", 1.0)
    over["crim"] = over.get("crim", 1.0) * cue.get("rim", 1.0)
    lane = cue.get("lane", 3)
    pos = cue.get("pos") or [lane_x(lane), 15.9 if lane else 15.2]
    x, y = pos
    bot, top = math.radians(cue.get("bot", 0)), math.radians(cue.get("top", 0))
    c.root.location = (x, y, 0.0)
    c.root.rotation_euler = (0, 0, math.radians(cue.get("yaw", 0)))
    c.neck.rotation_euler = (0, 0, bot)
    sp["pivot"].rotation_euler = (0, 0, top - bot)
    eyes = cue.get("eyes", "shut")
    if sp["state"] != eyes:
        a, m = sp["load"](eyes)
        sp["tex2"].image, sp["mt2"].image = a, m
        sp["state"] = eyes
    sp["st1"].default_value = 2.0 * cue.get("glow", 1.0)
    sp["st2"].default_value = {"shut": 0.0, "slit": 3.0, "half": 3.0, "wide": 6.0}[eyes] * cue.get("glow", 1.0)
    # the lights follow it
    ck["obj"].location = (x + 0.1, y - 1.5, 0.05)
    kit.aim(ck["obj"], (x, y, 1.95))
    cr["obj"].location = (x, y + 0.9 + (0.0 if lane else 0.6), 2.9)
    kit.aim(cr["obj"], (x, y, 1.7))


# ------------------------------------------------------------------------------------------------ lights


def build_lights(kit, ctx):
    for i in range(4):
        x = lane_x(i)
        kit.light(f"lamp{i}", "SPOT", (x, -1.4, 3.0), 560.0, "#ffb26a", spot=84, blend=0.7, size=0.25)
        kit.light(f"lanes{i}a", "AREA", (x, 5.0, 3.0), 55.0, "#ffbd78", size=1.8)
        kit.light(f"lanes{i}b", "AREA", (x, 10.5, 3.0), 45.0, "#ffbd78", size=1.8)
    for i in range(5):
        kit.light(f"strip{i}", "AREA", (lane_x(i), 15.0, 2.9), 60.0, "#a9f0e2", size=1.3, shadow=False)
    kit.light("seats", "AREA", (-1.8, SEAT_Y + 1.5, 3.2), 260.0, "#ffc58a", size=5.0, shadow=False)
    kit.light("shadowL", "SPOT", (-1.8, -9.0, 0.9), 0.0, "#ffc68a", spot=75, blend=0.25, size=0.05)
    kit.LIGHTS["shadowL"]["base"] = 3500.0
    kit.aim(kit.LIGHTS["shadowL"]["obj"], (-1.8, 6.0, 0.0))
    # the opening: a soft warm light on my face for the first seconds, so the first frame reads on a phone
    kit.light("open", "AREA", (-0.3, -3.4, 2.4), 0.0, "#ffd4a6", size=2.2, shadow=False)
    kit.LIGHTS["open"]["base"] = 130.0
    kit.aim(kit.LIGHTS["open"]["obj"], (-0.3, -1.5, 1.4))
    kit.light("fill", "AREA", (-4.0, 6.0, 3.3), 90.0, "#7c86b8", size=10.0, shadow=False)
    for k, (hx, hy) in enumerate(((0.0, -3.0), (-3.5, -3.0), (-0.8, 3.0), (-4.0, 4.0))):
        kit.light(f"house{k}", "AREA", (hx, hy, 3.3), 0.0, "#ffe2b5", size=5.0, shadow=True)
        kit.LIGHTS[f"house{k}"]["base"] = 380.0


def dip_gain(tl, t):
    g = 1.0
    for c in _cues(tl, "dip"):
        d, h, u = c.get("down", 0.6), c.get("hold", 0.3), c.get("up", 0.8)
        depth = c.get("depth", 0.5)
        a = t - c["t"]
        if a < 0 or a > d + h + u:
            continue
        if a < d:
            k = _ss(a / d)
        elif a < d + h:
            k = 1.0
        else:
            k = 1 - _ss((a - d - h) / u)
        g = min(g, 1 - (1 - depth) * k)
    return g


def house_gain(tl, t):
    c = _last(_cues(tl, "house"), t)
    return 0.0 if c is None else _ss((t - c["t"]) / c.get("rise", 1.5))


# ------------------------------------------------------------------------------------------------ props and lazy cast parts


def lazy(kit, ctx, M, story):
    """Parts that hang on the cast (built after build()): team shirts' cream panel, Mags's cardigan, Tomasz's beard,
    my house shoes and team shirt, and the props in hands."""
    if ctx.get("lazy"):
        return
    ctx["lazy"] = True
    ob = bpy.data.objects.get
    for who in ("dev", "rosie", "tomasz"):
        t_ = ob(f"{who}.torso")
        if t_ is not None:
            kit.box(f"{who}.panel", (0.56, 1.03, 1.96), (0.74, 0, 1.0), M["cream"], t_, bevel=0.03)
    t_ = ob("mags.torso")
    if t_ is not None:
        for sx in (-1, 1):
            kit.box(f"mags.cardi{sx}", (0.52, 1.05, 1.98), (sx * 0.74, 0, 1.0), M["mustard"], t_, bevel=0.05)
    h_ = ob("tomasz.headg")
    if h_ is not None:
        kit.box("tomasz.beard", (0.92, 0.2, 0.3), (0, -0.5, -0.4), M["beard"], h_, bevel=0.08)
    # my house shoes (teal, cream toe) and the team shirt over my hoodie
    shoes = []
    for sx in (-1, 1):
        leg = ob(f"me.leg{sx}")
        if leg is not None:
            shoes.append(kit.box(f"me.hs{sx}", (1.03, 1.05, 0.36), (0, 0, -1.85), M["tealshoe"], leg, bevel=0.07))
            shoes.append(kit.box(f"me.hstoe{sx}", (1.0, 0.42, 0.37), (0, -0.33, -1.85), M["creamshoe"], leg, bevel=0.06))
    ctx["p_myshoes"] = shoes
    t_ = ob("me.torso")
    ctx["p_myshirt"] = []
    if t_ is not None:
        ctx["p_myshirt"] = [kit.box("me.shirt", (2.07, 1.07, 2.02), (0, 0, 1.0), M["tealshirt"], t_, bevel=0.05),
                            kit.box("me.shirtp", (0.56, 1.09, 1.96), (0.74, 0, 1.0), M["cream"], t_, bevel=0.03)]
        ball = kit.sphere("me.holdball", 0.33, (0, -0.95, 1.0), M["ball"], t_, seg=16)
        ctx["p_myball"] = [ball]
    # Mags's hands: the shoes pair and the shirt, both parented to her right arm
    arm = ob("mags.arm1")
    ctx["p_shoes"], ctx["p_shirt"] = [], []
    if arm is not None:
        for sx in (-1, 1):
            ctx["p_shoes"].append(kit.box(f"mags.shoe{sx}", (0.48, 0.34, 0.95), (sx * 0.27, 0.0, -2.05), M["tealshoe"], arm,
                                          bevel=0.06))
            ctx["p_shoes"].append(kit.box(f"mags.shoetoe{sx}", (0.46, 0.36, 0.34), (sx * 0.27, 0.0, -2.32), M["creamshoe"],
                                          arm, bevel=0.05))
        ctx["p_shirt"].append(kit.box("mags.shirtp", (1.7, 0.3, 1.5), (0, 0, -2.5), M["tealshirt"], arm, bevel=0.06))
        ctx["p_shirt"].append(kit.box("mags.shirtc", (0.45, 0.32, 1.52), (0.5, 0, -2.5), M["cream"], arm, bevel=0.04))
    # the nachos on a small table between the seats and the lane
    tb = kit.cyl("table", 0.5, 0.05, (-2.2, -4.3, 0.55), M["table"], n=24)
    st = kit.cyl("table.stem", 0.06, 0.55, (-2.2, -4.3, 0.27), M["table"], n=10)
    tray = kit.box("tray", (0.5, 0.36, 0.05), (-2.2, -4.3, 0.6), M["tray"], bevel=0.02)
    chips = [kit.box(f"chip{k}", (0.12, 0.012, 0.1), (-2.2 + 0.12 * math.cos(k * 1.9) * (0.4 + 0.1 * (k % 3)),
                                                     -4.3 + 0.08 * math.sin(k * 2.3), 0.64 + 0.012 * (k % 4)),
                     M["nacho"], rot=(0.2 * (k % 3), 0.15 * k, 0.6 * k)) for k in range(14)]
    ctx["p_nachos"] = [tb, st, tray] + chips


def show_flag(tl, t, what):
    v = False
    for c in _cues(tl, "show"):
        if c.get("what") == what and c["t"] <= t + 1e-9:
            v = c.get("on", True)
    return v


# ------------------------------------------------------------------------------------------------ build and animate


def build(kit, story, tl):
    ctx = {}
    # objects come and go between frames (hide_render), and a kept scene lets a frame depend on the ones before it
    bpy.context.scene.render.use_persistent_data = False
    M = materials(kit)
    ctx["M"] = M
    build_room(kit, ctx, M)
    build_returns(kit, ctx, M)
    build_screens(kit, ctx, M)
    build_lights(kit, ctx)
    build_spare(kit, ctx, M)
    return ctx


def animate_pins(ctx, tl, t):
    pins = ctx["pins"][0]
    c = _last(_cues(tl, "pins"), t)
    act, t0 = (c.get("act", "up"), c["t"]) if c else ("up", 0.0)
    for k, ob in enumerate(pins):
        ob.hide_render = False
        ob.location = (PIN_ROWS[k][0], PIN_ROWS[k][1], 0.0)
        ob.rotation_euler = (0, 0, 0)
        if act == "hide":
            ob.hide_render = True
        elif act == "drop":
            u = _ss((t - t0) / 0.9)
            ob.location.z = (1 - u) * 0.9
            ob.hide_render = t < t0
        elif act == "fall":
            ts = t0 + 0.04 * ((k * 7) % 10) / 3.0
            u = _ss((t - ts) / 0.4)
            ang = (k * 2.399) % (2 * math.pi)
            dx, dy = math.cos(ang), math.sin(ang)
            if u > 0:
                ob.rotation_euler = Matrix.Rotation(u * math.pi / 2, 3, V((-dy, dx, 0))).to_euler()
                ob.location = (PIN_ROWS[k][0] + dx * 0.3 * u, PIN_ROWS[k][1] + dy * 0.3 * u, 0.06 * u)
            if t - t0 > 3.0:
                ob.hide_render = True
    sw = _last(_cues(tl, "sweep"), t)
    z = 3.15
    if sw:
        z = 3.15 - 3.07 * (1 - _ss((t - sw["t"]) / 1.0))
        if sw.get("act") == "down":
            z = 3.15 - 3.07 * _ss((t - sw["t"]) / 0.5)
    ctx["sweep"].location.z = z


def animate_ball(ctx, tl, t):
    ball = ctx["ball"]
    c = _last(_cues(tl, "ball"), t)
    if c is None or c.get("hide"):
        ball.hide_render = True
        return
    ball.hide_render = False
    path = c["path"]
    a = t - c["t"]
    pts = [(p[0], V(p[1])) for p in path]
    if a <= pts[0][0]:
        pos = pts[0][1]
    elif a >= pts[-1][0]:
        pos = pts[-1][1]
    else:
        for (t0, p0), (t1, p1) in zip(pts, pts[1:]):
            if t0 <= a <= t1:
                pos = p0.lerp(p1, (a - t0) / max(1e-6, t1 - t0))
                break
    ball.location = pos
    run = sum((q1 - q0).length for (_, q0), (_, q1) in zip(pts, pts[1:]) if _ is not None)
    done = min(1.0, max(0.0, a / max(1e-6, pts[-1][0])))
    ball.rotation_euler = (done * run / 0.109, 0, 0)


def animate(kit, story, tl, t, ctx):
    M = ctx["M"]
    lazy(kit, ctx, M, story)
    over = {}
    # the lights: a slow dip, the house coming up
    g = dip_gain(tl, t)
    for nm in kit.LIGHTS:
        if nm.startswith(("lamp", "lanes", "strip", "seats", "ckey", "crim")):
            over[nm] = g
    hg = house_gain(tl, t)
    for k in range(4):
        over[f"house{k}"] = hg
    # people sitting
    for who, keys in tl["acting"].items():
        if _switch(keys, "sit", t, False):
            for sx in (-1, 1):
                leg = bpy.data.objects.get(f"{who}.leg{sx}")
                if leg is not None:
                    leg.rotation_euler = (-math.pi / 2, 0, 0)
    animate_pins(ctx, tl, t)
    pose_spare(kit, ctx, tl, t, over)
    animate_ball(ctx, tl, t)
    over["open"] = 1.0 - _ss((t - 2.0) / 1.0)
    for st in ctx["bulbs"]:
        st.default_value = 6.0 * g
    sc = _last(_cues(tl, "shadowlight"), t)
    over["shadowL"] = 0.0 if sc is None else _ss((t - sc["t"]) / 1.0) * sc.get("on", 1.0)
    dc = _last(_cues(tl, "door"), t)
    op = 0.0 if dc is None else (_ss((t - dc["t"]) / 0.6) if dc.get("open", 0) > 0.5 else 1 - _ss((t - dc["t"]) / 0.6))
    for piv, side in ctx["doors"]:
        piv.rotation_euler = (0, 0, -side * op * math.radians(100))
    # props
    me = bpy.data.objects.get("me")
    mags = bpy.data.objects.get("mags")
    for key, who in (("myshoes", me), ("myshirt", me), ("myball", me), ("shoes", mags), ("shirt", mags)):
        on = show_flag(tl, t, key) and (who is None or not who.hide_render)
        for ob in ctx.get(f"p_{key}", []):
            ob.hide_render = not on
    for ob in ctx.get("p_bag", []):
        ob.hide_render = not show_flag(tl, t, "bag")
    ns = show_flag(tl, t, "noscreen")
    for ob in bpy.data.objects:
        if ob.name.startswith("scr."):
            ob.hide_render = ns
    on = show_flag(tl, t, "nachos")
    for ob in ctx.get("p_nachos", []):
        ob.hide_render = not on
    # the score screen
    st = screen_state(tl, t)
    key = (st["lit5"], st["dim"], st["slide"], st["sixth"], st["n5"], tuple(st["sym5"]))
    if key != ctx["scr_key"]:
        # a fresh image datablock for every state: Blender doesn't reliably re-upload a changed image between renders
        arr = screen_image(st)
        img = bpy.data.images.new("score screen", SCR_W, SCR_H, alpha=False)
        img.colorspace_settings.name = "sRGB"
        img.pixels.foreach_set(arr.ravel())
        img.update()
        old = ctx["scr_img"]
        ctx["scr_tex"].image = img
        ctx["scr_img"] = img
        if old is not None and old.users <= 1:
            bpy.data.images.remove(old)
        ctx["scr_key"] = key
    return over
