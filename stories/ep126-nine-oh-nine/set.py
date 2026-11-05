"""ep126 "nine oh nine": one bright block of painted brick shops ending at the red feed store, its flat moonlit roof and
the iron ladder on its back wall, plus three tiny roofed sets (the bus window, the kitchen) and a dark road.

The rule meter is a cream tag on the camera (top-left): a clock glyph and the time in seven-segment digits. Everything
the story moves is driven by cues in story.json (see animate): the dusk fade, the time, the doors, the shades, the
bakery shutter, the dancers' sway, who sits, the pat on the crate, the radio, the dog on its leash.
Batch 13 bars: nothing blinks or flickers. The streetlamps are steady point lights from frame 1, the radio has no light,
the marquee and every notice are blank or glyphs. The film's only light changes are S05's 1.5 s dusk fade and S12b's one
slow shade (1.5 s).
"""
import math
import sys
from pathlib import Path

import bpy
from mathutils import Vector

sys.path.insert(0, str(Path(__file__).resolve().parent))
import layout as G  # noqa: E402

try:
    from blocky import acting as _acting
except Exception:  # pragma: no cover
    _acting = None

D2R = math.pi / 180.0
W = {}
ZR = G.ZR


def ss(x):
    x = min(1.0, max(0.0, x))
    return x * x * (3 - 2 * x)


def kit_col(h):
    h = h.lstrip("#")
    f = lambda c: (c / 12.92) if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
    return tuple(f(int(h[i:i + 2], 16) / 255) for i in (0, 2, 4))


def _L(**kw):
    base = dict(sun=4.5, sun_col="#ffc27a", sd=(-0.85, -0.3, 0.38), fill=1.0, fill_col="#ffe2c0", sky="#ffcf8a",
                sky_str=1.0)
    base.update(kw)
    return base


LOOKS = {
    # golden hour, a little before nine in summer: low warm sun from the west
    "dusk": _L(),
    # a warm night under a huge moon: cool moonlight from the south, deep blue (never black) sky
    "night": _L(sun=2.3, sun_col="#d3dfff", sd=(-0.05, -0.94, 0.33), fill=1.0, fill_col="#8fa8ff", sky="#2a3f86",
                sky_str=1.0),
}
SKY_PALE = ("#3a4f94", 1.0)    # S42, S43: a little paler, a static colour on a cut


def look_at(tl, t):
    cues = [c for c in tl["cues"] if c["name"] == "look"]
    cur = LOOKS[cues[0]["id"]] if cues else LOOKS["dusk"]
    prev = cur
    for c in cues:
        if c["t"] > t:
            break
        prev, cur = cur, LOOKS[c["id"]]
        dur = c.get("dur", 0.0)
        dur = 0.0 if dur <= 0 else max(0.4, dur)
        if t < c["t"] + dur:
            u = ss((t - c["t"]) / dur)
            out = {}
            for k in cur:
                a, b = prev[k], cur[k]
                if isinstance(a, str):
                    ca, cb = kit_col(a), kit_col(b)
                    out[k] = tuple(ca[i] + (cb[i] - ca[i]) * u for i in range(3))
                elif isinstance(a, tuple):
                    out[k] = tuple(x + (y - x) * u for x, y in zip(a, b))
                else:
                    out[k] = a + (b - a) * u
            return out
    return {k: (kit_col(v) if isinstance(v, str) else v) for k, v in cur.items()}


def sample(name, tl, t, defaults, **match):
    """The state of cue track `name` at t (fields eased over a cue's own "dur")."""
    cues = [c for c in tl["cues"] if c["name"] == name and all(c.get(k) == v for k, v in match.items())]
    cur, prev = dict(defaults), dict(defaults)
    for c in cues:
        if c["t"] > t:
            break
        prev = dict(cur)
        cur.update({k: v for k, v in c.items() if k in defaults})
        dur = c.get("dur", 0.0)
        if dur > 0 and t < c["t"] + dur:
            u = ss((t - c["t"]) / dur)
            return {k: (prev[k] + (cur[k] - prev[k]) * u if isinstance(cur[k], (int, float)) else cur[k]) for k in cur}
    return cur


def cue_time(tl, name):
    for c in tl["cues"]:
        if c["name"] == name:
            return c["t"]
    return 1e9


def noshadow(ob):
    ob.visible_shadow = False
    for c in ob.children_recursive:
        c.visible_shadow = False


# ---------------------------------------------------------------------------------------------- the street
def make_shop(kit, name, side, y0, y1, h, tint, windows, door, awning=None, awn_col="#ffffff", glass_n=True,
              last=False, depth=7.0, special=None, win_w=1.7, door_col="#c9503a", cap="#6a3a30", poster=False):
    """A painted brick shop whose front (x = +-6) faces the street. side -1: west (front faces +x); +1: east."""
    plastic = kit.plastic
    L = y1 - y0
    ym = (y0 + y1) / 2
    fx = 6.0 * side          # the front plane
    out = -side              # direction out to the street... side=-1 (west): out = +1
    cx = fx + side * depth / 2
    wall = kit.texture("brick", 1.0, tint=tint, mat_name=f"brick{tint}")
    kit.box(f"{name}.body", (depth, L, h), (cx, ym, h / 2), wall)
    kit.box(f"{name}.cap", (depth + 0.2, L + 0.3, 0.45), (cx, ym, h + 0.2), plastic(cap, 0.7, spec=0.1))
    kit.box(f"{name}.cap2", (0.5, L + 0.3, 0.35), (fx + out * 0.2, ym, h - 0.2), plastic("#f4ecd8", 0.7, spec=0.1))
    glass = kit.emit("#ffd9a0", 1.3, "winglass")
    frame = plastic("#f6f0e2", 0.7)
    shade_m = kit.emit("#f3e4bd", 0.85, "shadecream")
    dark = plastic("#3a3f4c", 0.4, spec=0.5)
    for k, wy in enumerate(windows):
        gm = dark if poster else glass
        kit.box(f"{name}.wf{k}", (0.1, win_w + 0.25, 1.65), (fx + out * 0.04, wy, 1.6), frame)
        kit.box(f"{name}.wg{k}", (0.06, win_w, 1.4), (fx + out * 0.1, wy, 1.6), gm)
        if poster:
            continue
        # the shade: a roll at the top that comes down over the glass (scale z of the empty at the top)
        e = kit.empty(f"{name}.shade{k}", (fx + out * 0.16, wy, 2.3))
        kit.box(f"{name}.shadeb{k}", (0.05, win_w + 0.06, 1.45), (0, 0, -0.725), shade_m, e)
        e.scale = (1, 1, 0.06)
        W["shades"].append((e, last and k == 0))
    # the door, hinged on its south edge, opening out onto the sidewalk
    if door is not None:
        dm = plastic(door_col, 0.5, spec=0.3)
        kit.box(f"{name}.doorframe", (0.1, 1.35, 2.35), (fx + out * 0.03, door, 1.17), frame)
        kit.box(f"{name}.dark", (0.05, 1.05, 2.1), (fx + out * 0.05, door, 1.05), plastic("#2a2630", 0.7))
        hinge = kit.empty(f"{name}.hinge", (fx + out * 0.1, door - 0.5, 0.0))
        kit.box(f"{name}.door", (0.08, 1.0, 2.1), (0, 0.5, 1.05), dm, hinge)
        kit.box(f"{name}.knob", (0.07, 0.07, 0.07), (out * 0.06, 0.88, 1.0), plastic("#e8c050", 0.3, spec=0.8), hinge)
        W["doors"].append((hinge, side))
    if awning:
        n = int(L / 0.5)
        for i in range(n):
            col = awn_col if i % 2 else awning
            kit.box(f"{name}.awn{i}", (1.5, 0.5, 0.07), (fx + out * 0.8, y0 + 0.25 + i * 0.5, 2.75),
                    plastic(col, 0.6), rot=(0, side * 0.22 * -1.0, 0))
    if special == "bank":
        for i in range(4):
            yy = y0 + 1.2 + i * (L - 2.4) / 3
            kit.cyl(f"{name}.col{i}", 0.25, 3.4, (fx + out * 0.7, yy, 1.7), plastic("#f1ece0", 0.55), n=16)
        kit.box(f"{name}.ped", (1.4, L - 1.0, 0.45), (fx + out * 0.7, ym, 3.62), plastic("#f1ece0", 0.55))
        kit.box(f"{name}.step", (1.4, L - 1.2, 0.2), (fx + out * 0.7, ym, 0.1), plastic("#d8d2c4", 0.8))
    if special == "movie":
        kit.box(f"{name}.marq", (1.7, 5.2, 0.9), (fx + out * 0.95, ym - 0.4, 3.3), plastic("#f4ecd8", 0.55))
        kit.box(f"{name}.marqt", (1.74, 5.24, 0.12), (fx + out * 0.95, ym - 0.4, 3.78), plastic("#c04a5a", 0.6))
        kit.box(f"{name}.marqb", (1.74, 5.24, 0.12), (fx + out * 0.95, ym - 0.4, 2.82), plastic("#c04a5a", 0.6))
        for yy in (ym - 3.2, ym + 2.4):
            kit.box(f"{name}.post{yy}", (0.14, 0.14, 2.8), (fx + out * 1.7, yy, 1.4), plastic("#c04a5a", 0.6))
    if special == "hardware":
        kit.box(f"{name}.sign", (0.12, 3.6, 0.8), (fx + out * 0.1, ym, 3.05), plastic("#4f9f6a", 0.5))
        kit.box(f"{name}.crateA", (0.7, 0.7, 0.6), (fx + out * 1.1, y0 + 1.0, 0.3), plastic("#c89a5a", 0.7))
        kit.box(f"{name}.crateB", (0.6, 0.6, 0.5), (fx + out * 1.1, y0 + 1.9, 0.25), plastic("#b07c4a", 0.7))
    if special == "flowers":
        for i, c in enumerate(("#ff7aa8", "#ffd36b", "#a98cf0", "#ff9a5a")):
            kit.box(f"{name}.fl{i}", (0.5, 0.6, 0.5), (fx + out * 0.8, y0 + 0.9 + i * 0.9, 0.25), plastic("#8a5a3a", 0.7))
            kit.sphere(f"{name}.fb{i}", 0.34, (fx + out * 0.8, y0 + 0.9 + i * 0.9, 0.7), plastic(c, 0.6), seg=10)


def street_lamp(kit, k, x, y, steady):
    plastic = kit.plastic
    iron = plastic("#2e3340", 0.5, spec=0.3)
    kit.cyl(f"lamp{k}.pole", 0.07, 3.5, (x, y, 1.75), iron, n=10)
    kit.cyl(f"lamp{k}.base", 0.16, 0.5, (x, y, 0.25), iron, n=10)
    kit.box(f"lamp{k}.arm", (0.45, 0.07, 0.07), (x - 0.22 * math.copysign(1, x), y, 3.5), iron)
    bx = x - 0.45 * math.copysign(1, x)
    kit.sphere(f"lamp{k}.bulb", 0.23, (bx, y, 3.38), kit.emit("#ffe9b0", 7.0, "lampglow"), seg=12)
    kit.cyl(f"lamp{k}.hat", 0.3, 0.1, (bx, y, 3.66), iron, n=12)
    lt = kit.light(f"lamp{k}", "POINT", (bx, y, 3.3), 1.0, "#ffe9b0", size=0.3, shadow=False)
    lt.hide_render = True
    W["lamps"].append(f"lamp{k}")


def build_street(kit):
    plastic = kit.plastic
    road = kit.texture("asphalt", 0.5, tint="#8c93a6", mat_name="asphalt road")
    walk = kit.texture("concrete", 0.6, tint="#d8d2c6", mat_name="concrete walk")
    kit.box("road", (9.0, 140.0, 0.1), (0, -70.0, -0.05), road)
    for sx in (-1, 1):
        kit.box(f"walk{sx}", (1.5, 140.0, 0.16), (sx * 5.25, -70.0, 0.0), walk)
    kit.plane("ground", (500, 500), (0, -60, -0.12), kit.grime("#6f8f6a", 0.8, 2.0, "ground", 0.95))
    kit.plane("alley", (60, 30), (0, 24, -0.01), kit.grime("#8d8f98", 0.7, 3.0, "alley", 0.9))
    # dashed centre line
    for i in range(24):
        kit.box(f"dash{i}", (0.14, 1.6, 0.012), (0, -3.0 - i * 5.0, 0.005), plastic("#f1e2a8", 0.8, spec=0.05))
    # ---- the shops
    make_shop(kit, "hardware", -1, -28.5, -21.5, 5.2, "#f0d78a", [-24.2], -27.0, awning="#4f9f6a", awn_col="#f6f0e2",
              last=True, special="hardware", door_col="#2f7f8f", win_w=2.6)
    make_shop(kit, "bakery", -1, -20.5, -12.5, 5.4, "#f7b2c4", [-14.3, -17.6], -19.4, awning="#ff9fb2",
              awn_col="#fffaf0", door_col="#d9684a")
    make_shop(kit, "bank", -1, -11.5, -2.5, 6.0, "#e0d8c8", [-9.6, -4.4], -7.0, special="bank", door_col="#3a4f7a",
              cap="#8a8478")
    make_shop(kit, "house", -1, -37.0, -29.5, 4.2, "#f2e6c8", [-35.4, -31.2], -33.0, door_col="#3fa05c", cap="#8a5a48",
              depth=6.0)
    make_shop(kit, "movie", 1, -31.0, -20.0, 5.8, "#c9a8e0", [-28.8, -22.4], -25.5, special="movie", poster=True,
              door_col="#c04a5a", cap="#5a3a6a")
    make_shop(kit, "flowers", 1, -18.5, -11.0, 5.2, "#a6e0b4", [-16.7, -12.8], -14.8, awning="#ffd36b",
              awn_col="#fffaf0", special="flowers", door_col="#c0603a")
    make_shop(kit, "barber", 1, -9.5, -2.0, 5.6, "#a8cdf0", [-8.1, -3.6], -5.85, door_col="#d04a4a", cap="#3a5a8a")
    # the stoop in front of the green door
    kit.box("stoop", (0.9, 1.7, 0.18), (-5.55, -33.0, 0.09), plastic("#cfc6b4", 0.8))
    # ---- the feed store: red, flat tar roof, a parapet, an iron ladder up its back wall
    red = kit.texture("brick", 1.0, tint="#e08070", mat_name="brick feed")
    kit.box("feed.body", (14.0, 9.0, ZR - 0.4), (0, 4.5, (ZR - 0.4) / 2), red)
    kit.box("feed.roof", (14.4, 9.4, 0.4), (0, 4.5, ZR - 0.2), plastic("#8d97ab", 0.6, spec=0.2))
    wood = plastic("#a46a40", 0.7)
    kit.box("feed.door", (3.2, 0.16, 3.0), (0, -0.08, 1.5), wood)
    kit.box("feed.doorframe", (3.5, 0.12, 0.25), (0, -0.1, 3.1), plastic("#f4ecd8", 0.6))
    for i in range(4):
        kit.box(f"feed.sack{i}", (0.7, 0.5, 0.45), (-2.8 + i * 0.75, -0.6, 0.23), plastic("#d9c7a0", 0.9))
    kit.box("feed.band", (14.2, 0.1, 0.5), (0, -0.05, 4.6), plastic("#f4ecd8", 0.6))
    # parapet 0.5 high, 0.4 thick; the north side has a gap for the ladder
    pm = plastic("#9aa3b5", 0.65, spec=0.15)
    top = ZR
    kit.box("par.s", (14.4, 0.4, 0.5), (0, 0.0, top + 0.25), pm)
    kit.box("par.w", (0.4, 9.4, 0.5), (-7.0, 4.5, top + 0.25), pm)
    kit.box("par.e", (0.4, 9.4, 0.5), (7.0, 4.5, top + 0.25), pm)
    gx0, gx1 = G.LADDER_X - 0.55, G.LADDER_X + 0.55
    kit.box("par.n1", ((gx0 + 7.2), 0.4, 0.5), ((gx0 - 7.2) / 2, 8.85, top + 0.25), pm)
    kit.box("par.n2", ((7.2 - gx1), 0.4, 0.5), ((gx1 + 7.2) / 2, 8.85, top + 0.25), pm)
    # the roof's furniture
    cx, cy = G.CRATE
    kit.box("crate", (1.2, 0.62, 0.5), (cx, cy, top + 0.25 - 0.0), kit.texture("wood", 0.7, tint="#c8a070", mat_name="wood crate"))
    for sx in (-1, 1):
        kit.box(f"crate.slat{sx}", (0.06, 0.66, 0.5), (cx + sx * 0.6, cy, top + 0.25), plastic("#8a5a34", 0.7))
    build_radio(kit, top)
    # a folded plaid blanket on the east end of the crate's lid? no: on the south parapet, two tin cups on the north one
    kit.box("blanket", (0.7, 0.45, 0.1), (cx + 1.3, cy + 0.6, top + 0.05), plastic("#c0503a", 0.9))
    kit.box("blanket.s1", (0.7, 0.07, 0.115), (cx + 1.3, cy + 0.6, top + 0.05), plastic("#f2e0b0", 0.9))
    kit.box("blanket.s2", (0.07, 0.45, 0.115), (cx + 1.3, cy + 0.6, top + 0.05), plastic("#2f5a3c", 0.9))
    for k, xx in enumerate((-0.45, -0.18)):
        kit.cyl(f"cup{k}", 0.09, 0.14, (xx, 8.85, top + 0.5 + 0.07), kit.metal("#b8bfca", 0.35), n=14)
    # two pale worn patches (2 cm proud of the roof) where two people always stand
    for k, (px, py) in enumerate(((G.GRANDPA[0], G.GRANDPA[1]), (G.GRANDMA[0], G.GRANDMA[1]))):
        kit.box(f"patch{k}", (0.8, 0.55, 0.02), (px, py, top + 0.011), plastic("#cfd6e2", 0.8, spec=0.05))
    # Grandpa's cane, leaning on the north parapet
    cane = plastic("#6a4a2e", 0.5)
    ce = kit.empty("cane", (G.CANE[0], G.CANE[1] + 0.2, top + 0.5), rot=(-0.28, 0, 0))
    kit.box("cane.shaft", (0.04, 0.04, 1.0), (0, 0, 0.35), cane, ce)
    kit.box("cane.hook", (0.14, 0.04, 0.04), (0.05, 0, 0.87), cane, ce)
    # ---- the ladder
    iron = kit.metal("#4a4f5c", 0.45)
    lx = G.LADDER_X
    for sx in (-1, 1):
        kit.box(f"lad.rail{sx}", (0.07, 0.07, ZR + 1.0), (lx + sx * 0.28, 9.14, (ZR + 1.0) / 2 - 0.05), iron)
        for z in (1.5, 3.5, 5.7):
            kit.box(f"lad.bk{sx}{z}", (0.08, 0.16, 0.12), (lx + sx * 0.28, 9.06, z), iron)
    worn = kit.metal("#d4d9e2", 0.25)
    for i in range(int((ZR + 0.7) / 0.3)):
        z = 0.35 + i * 0.3
        kit.cyl(f"lad.rung{i}", 0.027, 0.56, (lx, 9.14, z), iron, rot=(0, math.pi / 2, 0), n=10)
        kit.cyl(f"lad.worn{i}", 0.031, 0.26, (lx, 9.14, z), worn, rot=(0, math.pi / 2, 0), n=10)
    # the tally: two lavender strokes scratched into the top rung bracket (1 cm proud)
    tm = kit.plastic("#b79ce8", 0.5)
    kit.box("lad.plate", (0.34, 0.03, 0.3), (lx + 0.28, 9.0, 5.7), iron)
    for k in range(2):
        kit.box(f"lad.tally{k}", (0.03, 0.012, 0.2), (lx + 0.2 + k * 0.1, 8.98, 5.7), tm)
    # ---- the town notice board under its little roof (glyph notice only)
    bx, by = G.BOARD
    wd = plastic("#8a5a34", 0.7)
    for sx in (-1, 1):
        kit.box(f"board.post{sx}", (0.12, 0.12, 2.1), (bx + sx * 0.75, by, 1.05), wd)
    kit.box("board.back", (1.6, 0.08, 1.1), (bx, by, 1.4), plastic("#d9c7a0", 0.8))
    kit.box("board.roof", (1.9, 0.6, 0.1), (bx, by + 0.15, 2.2), plastic("#c0503a", 0.6), rot=(-0.25, 0, 0))
    kit.box("board.paper", (0.62, 0.012, 0.8), (bx, by + 0.05, 1.45), plastic("#fffaf0", 0.9))
    gm = plastic("#3a4a8a", 0.6)
    for r in range(4):
        for c in range(5):
            kit.box(f"glyph{r}{c}", (0.075, 0.012, 0.03 + 0.012 * ((r * 5 + c) % 3)),
                    (bx - 0.22 + c * 0.11, by + 0.062, 1.7 - r * 0.17), gm, rot=(0, 0.5 * (-1) ** (r + c), 0))
    # a bench by the bakery, the lamps
    for k, (x, y) in enumerate([(-4.9, -8.0), (4.9, -18.0), (-4.9, -28.0), (4.9, -8.0), (-4.9, -18.0), (4.9, -28.0)]):
        street_lamp(kit, k, x, y, True)
    # far houses and the hills, so the end of the street isn't a wall of fog
    for i, (x, y, w, d, hh, c) in enumerate([(-9, -48, 7, 6, 3.2, "#7a8fb8"), (9, -52, 7, 6, 3.6, "#7a8fb8"),
                                              (-10, -66, 8, 7, 3.4, "#6f83ae"), (10, -70, 8, 7, 4.0, "#6f83ae"),
                                              (0, -96, 30, 8, 5.0, "#5f74a0")]):
        kit.box(f"far{i}", (w, d, hh), (x, y, hh / 2), plastic(c, 0.9, spec=0.05))
    # the huge moon
    W["moon"] = kit.sphere("moon", 8.0, (-5.0, -90.0, 32.0), kit.emit("#f6f3e4", 7.0, "moonglow"), seg=24)
    noshadow(W["moon"])
    W["moon"].visible_glossy = False
    # the shutter on the bakery (comes down in S03)
    sh = kit.empty("shutter", (-5.93, -16.4, 2.6))
    kit.box("shutter.b", (0.06, 6.6, 2.6), (0, 0, -1.3), plastic("#aeb6c4", 0.45, spec=0.5), sh)
    sh.scale = (1, 1, 0.02)
    W["shutter"] = sh


def build_radio(kit, top):
    rx, ry = G.RADIO
    z0 = top + 0.5
    cream = kit.plastic("#f1e6c8", 0.5, spec=0.3)
    dark = kit.plastic("#3a3a44", 0.6)
    root = kit.empty("radio", (rx, ry, z0))
    kit.box("radio.body", (0.36, 0.13, 0.23), (0, 0, 0.115), cream, root, bevel=0.015)
    for i in range(5):
        kit.box(f"radio.grille{i}", (0.2, 0.014, 0.02), (-0.05, -0.07, 0.07 + i * 0.03), dark, root)
    knob = kit.empty("radio.knobe", (0.12, -0.07, 0.17), root)
    kit.cyl("radio.knob", 0.035, 0.03, (0, 0, 0), kit.plastic("#c0503a", 0.4), knob, rot=(math.pi / 2, 0, 0), n=14)
    kit.box("radio.mark", (0.01, 0.02, 0.05), (0, -0.016, 0.0), kit.plastic("#fffaf0", 0.5), knob)
    kit.box("radio.handle", (0.28, 0.03, 0.03), (0, 0, 0.26), dark, root)
    ant = kit.empty("radio.ant", (0.15, 0.0, 0.23), root, rot=(0, 0.45, 0))
    kit.cyl("radio.antb", 0.008, 0.45, (0, 0, 0.225), kit.metal("#c7ccd6", 0.3), ant, n=6)
    W["knob"] = knob


# ---------------------------------------------------------------------------------------------- the small sets
def build_bus(kit):
    plastic = kit.plastic
    bx, by = G.BUS
    wall = plastic("#7f8fb6", 0.7, spec=0.1)
    trim = plastic("#f4f0e4", 0.6)
    kit.box("bus.floor", (11.0, 4.6, 0.1), (bx, -0.8, -0.05), plastic("#4a4f5c", 0.8))
    kit.box("bus.ceil", (11.0, 4.6, 0.15), (bx, -0.8, 2.85), plastic("#e9e4d6", 0.7))
    # the north wall with a long window (x +-2.2, z 0.95 to 2.25)
    kit.box("bus.wl", (3.4, 0.15, 2.8), (bx - 3.8, 1.2, 1.4), wall)
    kit.box("bus.wr", (3.4, 0.15, 2.8), (bx + 3.8, 1.2, 1.4), wall)
    kit.box("bus.wb", (4.4, 0.15, 0.95), (bx, 1.2, 0.475), wall)
    kit.box("bus.wt", (4.4, 0.15, 0.6), (bx, 1.2, 2.55), wall)
    for dx in (-2.2, 2.2):
        kit.box(f"bus.fr{dx}", (0.1, 0.2, 1.4), (bx + dx, 1.2, 1.6), trim)
    kit.box("bus.sill", (4.5, 0.25, 0.06), (bx, 1.15, 0.95), trim)
    kit.box("bus.lintel", (4.5, 0.2, 0.06), (bx, 1.2, 2.25), trim)
    kit.box("bus.endL", (0.15, 4.6, 2.9), (bx - 5.5, -0.8, 1.4), wall)
    kit.box("bus.endR", (0.15, 4.6, 2.9), (bx + 5.5, -0.8, 1.4), wall)
    kit.box("bus.baffle", (11.0, 0.15, 3.0), (bx, -3.2, 1.4), wall)
    # the bench along the window, and a pole
    kit.box("bus.seat", (7.5, 0.62, 0.14), (bx, 0.75, 0.43), plastic("#e0705a", 0.6))
    kit.box("bus.seatbase", (7.5, 0.5, 0.36), (bx, 0.8, 0.18), plastic("#7a3a30", 0.7))
    kit.box("bus.back", (7.5, 0.1, 0.4), (bx, 1.07, 0.7), plastic("#e0705a", 0.6))
    kit.cyl("bus.pole", 0.03, 2.8, (bx + 1.7, -0.3, 1.4), kit.metal("#cfd4dc", 0.3), n=10)
    kit.cyl("bus.rail", 0.025, 7.0, (bx, -0.3, 2.65), kit.metal("#cfd4dc", 0.3), rot=(0, math.pi / 2, 0), n=10)
    # outside the window: a golden evening or a blue night (shown per shot)
    gold = kit.emit("#ffb24a", 2.6, "busgold")
    night = kit.emit("#26397c", 1.3, "busnight")
    W["bus_gold"], W["bus_night"] = [], []
    for nm, m, grp in (("g", gold, W["bus_gold"]), ("n", night, W["bus_night"])):
        grp.append(kit.plane(f"bus.sky{nm}", (24, 6), (bx, 4.2, 1.7), m, rot=(math.pi / 2, 0, 0)))
        for i, (dx, w_, h_) in enumerate(((-3.0, 1.8, 1.2), (-0.8, 1.4, 0.9), (1.4, 2.0, 1.5), (3.2, 1.2, 0.8))):
            c = "#a2542e" if nm == "g" else "#101a3e"
            grp.append(kit.box(f"bus.hs{nm}{i}", (w_, 0.2, h_), (bx + dx, 4.0, 0.95 + h_ / 2), kit.emit(c, 0.7, f"hs{c}")))
    kit.light("busL", "POINT", (bx, 2.4, 2.0), 1.0, "#ffb866", size=0.5, shadow=False).hide_render = True


def build_kitchen(kit):
    plastic = kit.plastic
    kx, ky = G.KITCHEN
    wall = plastic("#f4dca8", 0.8, spec=0.05)
    kit.box("k.floor", (9.0, 6.0, 0.1), (kx, -0.5, -0.05), plastic("#c89a64", 0.6))
    kit.box("k.ceil", (9.0, 6.0, 0.15), (kx, -0.5, 2.85), plastic("#f4ecd8", 0.8))
    kit.box("k.wl", (3.6, 0.15, 2.8), (kx - 2.7, 1.9, 1.4), wall)
    kit.box("k.wr", (3.6, 0.15, 2.8), (kx + 2.7, 1.9, 1.4), wall)
    kit.box("k.wb", (1.8, 0.15, 1.1), (kx, 1.9, 0.55), wall)
    kit.box("k.wt", (1.8, 0.15, 0.6), (kx, 1.9, 2.5), wall)
    kit.box("k.sideL", (0.15, 6.0, 2.9), (kx - 4.5, -0.5, 1.4), wall)
    kit.box("k.sideR", (0.15, 6.0, 2.9), (kx + 4.5, -0.5, 1.4), wall)
    kit.box("k.baffle", (9.0, 0.15, 3.0), (kx, -3.5, 1.4), wall)
    frame = plastic("#fffaf0", 0.6)
    for dx in (-0.9, 0.9):
        kit.box(f"k.fr{dx}", (0.1, 0.2, 1.4), (kx + dx, 1.9, 1.8), frame)
    kit.box("k.sill", (1.9, 0.3, 0.06), (kx, 1.8, 1.1), frame)
    kit.plane("k.night", (3, 3), (kx, 2.6, 1.8), kit.emit("#2a3f86", 1.2, "knight"), rot=(math.pi / 2, 0, 0))
    kit.box("k.counterL", (2.4, 0.7, 0.9), (kx - 2.5, 1.45, 0.45), plastic("#d8a468", 0.6))
    kit.box("k.counterR", (2.4, 0.7, 0.9), (kx + 2.5, 1.45, 0.45), plastic("#d8a468", 0.6))
    kit.box("k.topL", (2.5, 0.75, 0.06), (kx - 2.5, 1.45, 0.93), plastic("#f4ecd8", 0.5))
    kit.box("k.topR", (2.5, 0.75, 0.06), (kx + 2.5, 1.45, 0.93), plastic("#f4ecd8", 0.5))
    kit.box("k.upL", (2.2, 0.4, 0.8), (kx - 2.5, 1.65, 2.0), plastic("#e8b878", 0.6))
    kit.box("k.upR", (2.2, 0.4, 0.8), (kx + 2.5, 1.65, 2.0), plastic("#e8b878", 0.6))
    kit.box("k.fridge", (0.95, 0.8, 1.9), (kx + 4.0, 1.3, 0.95), plastic("#eef3f6", 0.4, spec=0.5))
    kit.cyl("k.kettle", 0.15, 0.25, (kx - 2.1, 1.45, 1.1), kit.metal("#cfd4dc", 0.3), n=14)
    kit.cyl("k.bowl", 0.22, 0.12, (kx + 2.0, 1.45, 1.0), plastic("#e0705a", 0.5), n=16)
    kit.sphere("k.lamp", 0.3, (kx - 1.6, 0.6, 2.35), kit.emit("#ffd9a0", 4.0, "klampglow"), seg=12)
    kit.light("kitL", "POINT", (kx, 0.4, 2.3), 1.0, "#ffc980", size=0.5, shadow=False).hide_render = True


def build_road(kit):
    plastic = kit.plastic
    rx, ry = G.ROAD
    kit.box("r.road", (80.0, 8.0, 0.1), (rx, ry, -0.05), kit.texture("asphalt", 0.5, tint="#7c849a", mat_name="asphalt rd"))
    kit.plane("r.grass", (200, 80), (rx, ry, -0.1), kit.grime("#5a7a58", 0.8, 2.0, "rgrass", 0.95))
    for i in range(10):
        kit.box(f"r.dash{i}", (1.8, 0.14, 0.012), (rx - 20 + i * 4.5, ry + 0.3, 0.005), plastic("#f1e2a8", 0.8, spec=0.05))
    # the bus, pulled over, tired and dark
    body = plastic("#e8b838", 0.5, spec=0.3)
    kit.box("r.bus", (9.0, 2.5, 2.9), (rx - 2.0, ry + 0.0, 1.8), body, bevel=0.1)
    kit.box("r.busstripe", (9.05, 2.54, 0.35), (rx - 2.0, ry, 1.1), plastic("#c04a3a", 0.5))
    kit.box("r.buswin", (7.6, 0.06, 0.9), (rx - 2.0, ry - 1.27, 2.35), plastic("#3a4560", 0.25, spec=0.7))
    kit.box("r.busdoor", (1.0, 0.06, 2.2), (rx, ry - 1.27, 1.2), plastic("#252a38", 0.4))
    for dx in (-4.2, 1.8):
        kit.cyl(f"r.wh{dx}", 0.5, 0.35, (rx + dx, ry - 1.0, 0.5), plastic("#1c1c20", 0.8), rot=(math.pi / 2, 0, 0), n=16)
    kit.box("r.busstep", (1.0, 0.4, 0.3), (rx, ry - 1.5, 0.2), plastic("#6a6e7a", 0.6))


# ---------------------------------------------------------------------------------------------- the rule meter
DIGIT_SEGS = {0: "abcdef", 1: "bc", 2: "abged", 3: "abgcd", 4: "fgbc", 5: "afgcd", 6: "afgedc", 7: "abc",
              8: "abcdefg", 9: "abcdfg"}


def build_tag(kit):
    cam = kit.OBJ["cam"]
    root = kit.empty("tag", (0, 0, 0), cam)
    W["tag"] = root
    edge = kit.emit("#2b2118", 0.6, "tagedge")
    plate = kit.emit("#f6ecd0", 0.9, "tagplate")
    ink = kit.emit("#2b2118", 0.6, "tagink")
    gold = kit.emit("#d98a1c", 1.2, "taggold")

    def b(name, size, loc, mat, parent=None):
        ob = kit.box(name, size, loc, mat, parent or root)
        noshadow(ob)
        return ob

    b("tag.edge", (1.36, 0.7, 0.006), (0, 0, 0), edge)
    b("tag.plate", (1.3, 0.64, 0.006), (0, 0, 0.007), plate)
    z = 0.016
    # the clock glyph: a ring, a face, two hands, twelve-three-six-nine ticks
    ob = kit.cyl("tag.ring", 0.235, 0.006, (-0.42, 0, z), ink, root, n=24)
    noshadow(ob)
    ob = kit.cyl("tag.face", 0.2, 0.006, (-0.42, 0, z + 0.003), plate, root, n=24)
    noshadow(ob)
    for k in range(4):
        a = k * math.pi / 2
        t_ = b(f"tag.tick{k}", (0.03, 0.06, 0.006), (-0.42 + 0.165 * math.sin(a), 0.165 * math.cos(a), z + 0.006), ink)
        t_.rotation_euler = (0, 0, -a)
    hh_ = kit.empty("tag.hh", (-0.42, 0, z + 0.008), root)
    b("tag.hhb", (0.045, 0.11, 0.006), (0, 0.045, 0), gold, hh_)
    mh_ = kit.empty("tag.mh", (-0.42, 0, z + 0.011), root)
    b("tag.mhb", (0.03, 0.17, 0.006), (0, 0.07, 0), ink, mh_)
    b("tag.hub", (0.05, 0.05, 0.006), (-0.42, 0, z + 0.014), ink)
    W["hands"] = (hh_, mh_)
    # four seven-segment digits and a colon
    W["digits"] = []
    for di, cx in enumerate((-0.02, 0.15, 0.37, 0.54)):
        dw, dh, t = 0.12, 0.4, 0.052
        cy = 0.0
        pos = {"a": (0, dh / 2 - t / 2, dw, t), "g": (0, 0, dw, t), "d": (0, -dh / 2 + t / 2, dw, t),
               "f": (-dw / 2 + t / 2, dh / 4, t, dh / 2), "b": (dw / 2 - t / 2, dh / 4, t, dh / 2),
               "e": (-dw / 2 + t / 2, -dh / 4, t, dh / 2), "c": (dw / 2 - t / 2, -dh / 4, t, dh / 2)}
        d = {}
        for k, (px, py, sw, sh) in pos.items():
            d[k] = b(f"tag.d{di}{k}", (sw, sh, 0.006), (cx + px, cy + py, z), ink)
        W["digits"].append(d)
    for yy in (0.08, -0.08):
        b(f"tag.colon{yy}", (0.05, 0.05, 0.006), (0.26, yy, z), ink)


def _digit(d, n):
    segs = DIGIT_SEGS.get(n, "")
    for k, ob in d.items():
        ob.hide_render = k not in segs


# ---------------------------------------------------------------------------------------------- the dog
def build_dog(kit):
    plastic = kit.plastic
    brown = plastic("#9a5a34", 0.55)
    dk = plastic("#5a3220", 0.6)
    root = kit.empty("dog", (0, -80, 0))
    W["dog"] = root
    kit.box("dog.body", (0.2, 0.62, 0.2), (0, 0.0, 0.26), brown, root, bevel=0.06)
    kit.box("dog.head", (0.17, 0.24, 0.17), (0, -0.4, 0.34), brown, root, bevel=0.05)
    kit.box("dog.snout", (0.1, 0.16, 0.1), (0, -0.55, 0.31), dk, root, bevel=0.03)
    for sx in (-1, 1):
        kit.box(f"dog.ear{sx}", (0.04, 0.12, 0.14), (sx * 0.1, -0.35, 0.3), dk, root)
    kit.box("dog.tail", (0.05, 0.3, 0.05), (0, 0.42, 0.34), brown, root, rot=(0.6, 0, 0))
    W["dogleg"] = []
    for i, (dx, dy) in enumerate(((-0.07, -0.22), (0.07, -0.22), (-0.07, 0.22), (0.07, 0.22))):
        e = kit.empty(f"dog.leg{i}", (dx, dy, 0.18), root)
        kit.box(f"dog.legb{i}", (0.06, 0.06, 0.2), (0, 0, -0.09), dk, e)
        W["dogleg"].append(e)
    lash = kit.box("dog.leash", (1.0, 0.012, 0.012), (0, -80, 0.9), plastic("#c0303a", 0.6))
    W["leash"] = lash


# ---------------------------------------------------------------------------------------------- build
def build(kit, story, tl):
    tl["cues"].sort(key=lambda c: c["t"])
    W["shades"], W["doors"], W["lamps"] = [], [], []
    sun = kit.light("sun", "SUN", (-30, -30, 30), 1.0, "#ffc27a", size=0.06)
    sun.data.angle = 0.05
    fill = kit.light("fill", "SUN", (0, -10, 30), 1.0, "#ffe2c0", shadow=False)
    fill.data.angle = 0.5
    kit.aim(fill, (0, 0, 0))
    kit.light("key", "POINT", (0, 0, 2), 1.0, "#fff4e0", size=0.8, shadow=False)
    kit.light("warm", "POINT", (0, 0, 1), 1.0, "#ffd9a0", size=0.5, shadow=False)
    kit.light("rimL", "POINT", (0, 0, 3), 1.0, "#bcd0ff", size=0.6, shadow=False)
    for nm in ("sun", "fill", "key", "warm", "rimL"):
        kit.LIGHTS[nm]["obj"].visible_camera = False
    build_street(kit)
    build_bus(kit)
    build_kitchen(kit)
    build_road(kit)
    build_dog(kit)
    build_tag(kit)
    for nm in W["lamps"]:
        kit.LIGHTS[nm]["obj"].visible_camera = False
    for nm in ("busL", "kitL"):
        kit.LIGHTS[nm]["obj"].visible_camera = False
    return {}


# ---------------------------------------------------------------------------------------------- the cast's extras
def _first_frame(kit, story):
    ensure = bpy.data.objects.get
    gm_h, gm_t = ensure("grandma.headg"), ensure("grandma.torso")
    red = kit.plastic("#e02f45", 0.35, spec=0.5)
    W["lipU"], W["lipO"] = [], []
    if gm_h is not None:
        # lipstick: a red smile just proud of the drawn mouth, or a red O for the stunned face
        z0 = -0.27
        for k, (x, z, rot, w) in enumerate(((0.0, z0 - 0.015, 0, 0.12), (-0.065, z0 + 0.0, 0.25, 0.1), (0.065, z0 + 0.0, -0.25, 0.1),
                                            (-0.11, z0 + 0.03, 0.55, 0.07), (0.11, z0 + 0.03, -0.55, 0.07))):
            W["lipU"].append(kit.box(f"lipU{k}", (w, 0.03, 0.065), (x, -0.625, z), red, gm_h, rot=(0, rot, 0), bevel=0.01))
        for k, (x, z, w, h) in enumerate(((0.0, -0.29, 0.14, 0.04), (0.0, -0.21, 0.14, 0.04), (-0.06, -0.25, 0.04, 0.1), (0.06, -0.25, 0.04, 0.1))):
            ob = kit.box(f"lipO{k}", (w, 0.03, h), (x, -0.625, z), red, gm_h, bevel=0.01)
            ob.hide_render = True
            W["lipO"].append(ob)
    if gm_t is not None:
        sil = kit.plastic("#dfe3ec", 0.6)
        yel = kit.plastic("#f0cf55", 0.6)
        kit.box("grandma.dress", (0.95, 0.05, 1.95), (0, -0.52, 1.0), yel, gm_t, bevel=0.02)
        for k, z in enumerate((1.45, 1.0, 0.55)):
            kit.box(f"grandma.braid{k}", (0.3, 0.3, 0.48), (-0.9, -0.5, z + 0.35), sil, gm_t, bevel=0.1)
        kit.box("grandma.braidtie", (0.34, 0.34, 0.1), (-0.9, -0.5, 0.45), kit.plastic("#b79ce8", 0.5), gm_t)
    gp_t = ensure("grandpa.torso")
    if gp_t is not None:
        bt = kit.plastic("#8a2f3a", 0.5)
        kit.box("grandpa.knot", (0.18, 0.09, 0.16), (0, -0.55, 1.86), bt, gp_t, bevel=0.03)
        for sx in (-1, 1):
            kit.box(f"grandpa.bow{sx}", (0.3, 0.07, 0.24), (sx * 0.22, -0.54, 1.86), bt, gp_t, rot=(0, sx * 0.25, 0), bevel=0.03)
    for who in ("me", "grandma", "grandpa", "baker", "tran"):
        for ob in [bpy.data.objects.get(f"{who}.arm-1"), bpy.data.objects.get(f"{who}.arm1")]:
            pass
    W["inited"] = True


def _legs_sit(who, s):
    for sx in (-1, 1):
        leg = bpy.data.objects.get(f"{who}.leg{sx}")
        if leg:
            leg.rotation_euler = (leg.rotation_euler.x * (1 - s) + (-math.pi / 2 * 0.97) * s, 0, 0)


BUS_SHOTS = {"S01a", "S01b", "S02", "S07", "S44", "S46"}
KITCHEN_SHOTS = {"S06"}
# roof shots where the face is held in moon shadow (S21, S22) or lit from below (S23)
DIMFACE = {"S21": (0.35, 0.22), "S22": (0.45, 0.3), "S23": (0.5, 1.1)}
SKYOV = {"S42": SKY_PALE, "S43": SKY_PALE}


def animate(kit, story, tl, t, ctx):
    if not W.get("inited"):
        _first_frame(kit, story)
    look = look_at(tl, t)
    gains = {}
    shot = next((s for s in tl["shots"] if s["start"] <= t < s["end"]), tl["shots"][-1])
    sid = shot["id"]
    spec = next((s for s in story["shots"] if s["id"] == sid), None)
    night = look["fill"] > 0 and look["sun"] < 3.4
    so = kit.LIGHTS["sun"]["obj"]
    so.location = Vector(look["sd"]).normalized() * 60
    kit.aim(so, (0, 0, 0))
    kit.LIGHTS["sun"]["light"].color = look["sun_col"]
    kit.LIGHTS["fill"]["light"].color = look["fill_col"]
    gains["sun"], gains["fill"] = look["sun"], look["fill"]
    gains["lamp"] = 1.0
    for nm in W["lamps"]:
        gains[nm] = 330.0
    # sky
    w = bpy.context.scene.world
    bg = w.node_tree.nodes["Background"]
    skyc, skys = look["sky"], look["sky_str"]
    if sid in SKYOV and sample("sky", tl, t, {"id": "night"})["id"] == "pale":
        skyc, skys = kit_col(SKYOV[sid][0]), SKYOV[sid][1]
    inbus = sid in BUS_SHOTS
    inkit = sid in KITCHEN_SHOTS
    if inbus or inkit:
        skyc = kit_col("#26397c") if sample("bus", tl, t, {"mode": "off"})["mode"] != "gold" else kit_col("#ffb24a")
    bg.inputs["Color"].default_value = (*skyc, 1.0)
    bg.inputs["Strength"].default_value = skys
    # interiors
    bm = sample("bus", tl, t, {"mode": "off"})["mode"]
    for ob in W["bus_gold"]:
        ob.hide_render = bm != "gold"
    for ob in W["bus_night"]:
        ob.hide_render = bm != "night"
    gains["busL"] = (520.0 if bm == "gold" else 160.0) if inbus else 0.0
    gains["kitL"] = 520.0 if inkit else 0.0
    # the follow lights: a key at the camera, a warm one under it, a cool rim from behind the subject
    key_g, warm_g, rim_g = 0.0, 0.0, 0.0
    if spec:
        c0 = spec["cam"][0]
        loc, tgt = Vector(c0[1]), Vector(c0[2])
        dist = max(1.0, (loc - tgt).length)
        base = 150.0 * dist * dist / 9.0
        if inbus:
            key_g = base * (0.5 if bm == "gold" else 1.0)
        elif inkit:
            key_g = base * 0.6
        elif sid in DIMFACE:
            key_g = base * DIMFACE[sid][0]
            warm_g = base * DIMFACE[sid][1]
        else:
            key_g = base * (0.5 if look["sun"] > 3.4 else 1.0)
        right = Vector((c0[2][1] - c0[1][1], -(c0[2][0] - c0[1][0]), 0)).normalized() if (loc - tgt).length > 0.01 else Vector((1, 0, 0))
        kl = kit.LIGHTS["key"]["obj"]
        kl.location = loc + Vector((0, 0, 0.5)) - right * 0.5
        wl = kit.LIGHTS["warm"]["obj"]
        wl.location = loc + Vector((0, 0, -0.9))
        rl = kit.LIGHTS["rimL"]["obj"]
        rl.location = tgt + (tgt - loc).normalized() * 1.6 + Vector((0, 0, 0.9))
        if ZR - 0.5 < tgt.z < ZR + 3.0:
            rim_g = base * 0.25
    gains["key"], gains["warm"], gains["rimL"] = key_g, warm_g, rim_g
    # the clock tag
    tm = sample("time", tl, t, {"hh": 9, "mm": 6})
    hh, mm = int(tm["hh"]), int(tm["mm"])
    _digit(W["digits"][0], (hh // 10) if hh >= 10 else -1)
    _digit(W["digits"][1], hh % 10)
    _digit(W["digits"][2], mm // 10)
    _digit(W["digits"][3], mm % 10)
    W["hands"][0].rotation_euler = (0, 0, -((hh % 12) * 30 + mm * 0.5) * D2R)
    W["hands"][1].rotation_euler = (0, 0, -(mm * 6) * D2R)
    lens = spec["cam"][0][3] if spec else 40.0
    dist = 1.0
    h2 = dist * 24.0 / lens
    w2 = h2 * 9.0 / 16.0
    s = 0.34 * w2
    tag = W["tag"]
    tag.scale = (s, s, s)
    tag.location = (-0.5 * w2 + 0.325 * w2 + 0.10 * w2, 0.5 * h2 - 0.30 * w2, -dist)
    # the doors: open until S05, then every door in town shuts, one after the other
    dn = cue_time(tl, "doors")
    for i, (hinge, side) in enumerate(W["doors"]):
        if t < dn:
            op = 1.0 if i % 3 != 2 else 0.0
        else:
            op = (1.0 if i % 3 != 2 else 0.0) * (1.0 - ss((t - dn - 0.18 * i) / 0.45))
        hinge.rotation_euler = (0, 0, side * 1.65 * op)
    # shades: all but the last come down at L12; the last slides over 1.5 s
    sh = sample("shades", tl, t, {"s": 0.0})["s"]
    last = sample("lastshade", tl, t, {"on": 0.0})["on"]
    for e, is_last in W["shades"]:
        v = last if is_last else sh
        e.scale = (1, 1, 0.06 + 0.94 * ss(v) if is_last else 0.06 + 0.94 * v)
    # the bakery shutter
    st0 = cue_time(tl, "shutter")
    W["shutter"].scale = (1, 1, 0.02 + 0.98 * ss((t - st0 - 0.2) / 1.1) if t >= st0 else 0.02)
    # the radio knob turns while Grandpa's hand is on it
    rv = sample("radio", tl, t, {"on": 0.0})["on"]
    W["knob"].rotation_euler = (0, rv * 2.2, 0)
    # sits and the pat
    for who in ("me", "grandma", "grandpa"):
        sv = sample("sit", tl, t, {"s": 0.0}, who=who)["s"]
        if sv > 0.001:
            _legs_sit(who, sv)
    pv = sample("pat", tl, t, {"amp": 0.0})["amp"]
    ga = bpy.data.objects.get("grandma.arm-1")
    if ga is not None and pv > 0.01:
        ga.rotation_euler = (-0.12, 0.42 + 0.1 * math.sin(t * 6.0), 0)
    # the dance: both sway together, hands at waists
    da = sample("dance", tl, t, {"amp": 1.0})["amp"]
    if da > 0.01:
        ph = 2 * math.pi * t / 1.875
        sw = math.sin(ph)
        for who in ("grandma", "grandpa"):
            r = bpy.data.objects.get(who)
            if r is None:
                continue
            r.location.x += 0.11 * sw * da
            r.location.z += 0.012 * abs(math.sin(ph)) * da
            r.rotation_euler = (r.rotation_euler.x, 0, r.rotation_euler.z + 0.05 * sw * da)
            for sx, lg in ((-1, 1), (1, -1)):
                leg = bpy.data.objects.get(f"{who}.leg{sx}")
                if leg:
                    leg.rotation_euler = (0.14 * math.sin(ph) * lg * da, 0, 0)
    # the lipstick follows the face
    if _acting is not None and W.get("lipU"):
        ex = _acting.state(tl, "grandma", t)["expr"]
        wide = ex in ("wide", "scared")
        for ob in W["lipU"]:
            ob.hide_render = wide
        for ob in W["lipO"]:
            ob.hide_render = not wide
    # Mr. Tran's dog and its leash
    tr = bpy.data.objects.get("tran")
    dog, lash = W["dog"], W["leash"]
    if tr is not None and not tr.hide_render:
        yaw = tr.rotation_euler.z
        fwd = Vector((math.sin(yaw), -math.cos(yaw), 0))
        rgt = Vector((math.cos(yaw), math.sin(yaw), 0))
        base = Vector(tr.location)
        dp = base + fwd * 1.55 + rgt * 0.4
        dog.location = (dp.x, dp.y, 0)
        dog.rotation_euler = (0, 0, yaw)
        ph = t * 14.0
        for i, e in enumerate(W["dogleg"]):
            e.rotation_euler = (0.7 * math.sin(ph + (math.pi if i in (1, 2) else 0)), 0, 0)
        hand = base + fwd * 0.25 + rgt * 0.3 + Vector((0, 0, 0.8))
        end = dp + Vector((0, 0, 0.32)) - fwd * 0.25
        d = end - hand
        lash.location = (hand + end) / 2
        lash.scale = (d.length, 1, 1)
        lash.rotation_euler = (0, -math.atan2(d.z, math.hypot(d.x, d.y)), math.atan2(d.y, d.x))
    else:
        dog.location = (0, -80, 0)
        lash.location = (0, -80, 0.9)
    return gains
