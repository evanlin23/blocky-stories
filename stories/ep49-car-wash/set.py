"""ep49 The bell on your collar: a small automatic car wash on the edge of town, and four little places around it.

Built from kit.py's parts (nothing here is shared with another story's set). Metres, floor z = 0, a character with
yaw 0 faces -y.

THE WASH (origin): a forecourt on y < 0 with a painted queue lane at x 0 running up to the shed. The shed is a long
open-ended corrugated tunnel, x -4.2 .. 4.2, y 0 .. 16, roof at 4. The conveyor runs down the middle (x 0). The pay
booth is built into its left bay, x -3.9 .. -2.1, y 0.5 .. 2.5: a hatch window on its +x side (toward the cars), a
door on its +y side (toward the tunnel), the steel sill under the hatch (its left end, toward y 0.9, is where the keys
and the clapper lie; the tally of two strokes is scratched at the right end, y 2.0). The Stutter's line stands in the
left aisle, x -3.1, from the booth door (y 2.7) back into the tunnel at 0.7 m steps. Along the tunnel: the foam arch
at y 7, two brush pairs at y 9.3 and 11.3, the drying arch at y 13.5, drying lamps low along both walls.
Away from the wash: the kiosk (x 6 .. 9, y -14 .. -11), the sign pole (x 9, y -6), and four small sets far off:
the cafe (x 60, y 0), the wedding hall (x 60, y 30), the street (x 60, y -30), the flat (x -60, y 0) and its
kitchen (x -60, y -20).

THE STUTTER: five characters `st0` .. `st4` (the same person, one cast spec tinted greyer each time). They are posed
by the acting keys like anyone, and set.py gives each one a transparency (a fade value in its materials), driven by
the `fade` cues: the base ramp is 100, 80, 62, 44, 28 percent, and a copy's own fade takes it to 0.

Cues read here (all optional; a missing one means its default):
- tod {set}: day, sunrise, over, noon, dusk, night (the sun, the sky and the interior fills), switched at a cut
- mist {v, dur}: 0..1 haze in the tunnel, eased over dur
- dry {v, dur}: the drying lamps 0..1, eased over dur (at least 1 s)
- spin {v, dur}: brush speed in turns a second, eased over dur
- lever {v, dur}: the blue lever 0 (up) .. 1 (down)
- foot / hand {on}: the five wet footprint pairs / five handprints on the silver car
- chain {on}: the chain and disc across the lane
- bag {on} (me), carry {on} (Ruben's drum), clapper {on} (the clapper in my bell)
- car:NAME {pos, yaw, glide, on}, item:NAME {pos, glide, on}: cars, the van, the phone, the keys, the clapper
- ring {who, dur, rate, amp}, sway {who: [...], dur}, pocket {}: bell wobbles and Ruben's pocket jump
- fade {k}: the Stutter's copy k fades out over dur
- ride {who, car, off}: a character sitting in a car, moving with it
"""

from __future__ import annotations

import math
import random

import bpy
from mathutils import Vector as V

# ------------------------------------------------------------------------------------------------ palette
WET = "#8a8f94"
STEEL = "#a9b3ba"
WASH_BLUE = "#3f8fcf"
FOAM = "#e4ecf0"
GOLD = "#d9a441"
RUST = "#b5532c"
CREAM = "#efe3c8"
BRASS = "#c9a24a"
GREEN = "#355e45"
MUSTARD = "#d2a237"
MISTC = "#a8cbe4"
AMBER = "#e89a3c"

SHED_X0, SHED_X1, SHED_Y1, ROOF = -4.2, 4.2, 16.0, 4.0
OFF = {"cafe": (60, 0), "wed": (60, 30), "street": (60, -30), "flat": (-60, 0), "kitchen": (-60, -20)}

TOD = {
    "day": dict(work=1.0, yard=1.0, sun=4.2, sun_c="#fff0da", sky="#b4d0ea", sky_s=1.1, loc=(-9, -12, 14), fill=1.0, flat=1.0),
    "sunrise": dict(work=1.0, yard=1.0, sun=3.4, sun_c="#ffbe82", sky="#f4cfa6", sky_s=0.9, loc=(6, 14, 5), fill=1.0, flat=1.0),
    "over": dict(work=1.0, yard=1.0, sun=0.9, sun_c="#d8e2ee", sky="#9aa6b4", sky_s=1.0, loc=(-6, -8, 14), fill=1.0, flat=1.0),
    "noon": dict(work=1.0, yard=1.0, sun=1.4, sun_c="#e3e8ee", sky="#a4afbb", sky_s=1.05, loc=(-6, -8, 14), fill=1.0, flat=1.0),
    "dusk": dict(work=0.28, yard=0.12, sun=0.7, sun_c="#ff9a5a", sky="#37406a", sky_s=0.5, loc=(10, -4, 4), fill=0.9, flat=0.5),
    "night": dict(work=0.3, yard=0.1, sun=0.22, sun_c="#8aa6dc", sky="#0e1626", sky_s=0.3, loc=(-6, -8, 12), fill=0.9, flat=0.12),
}


def srgb(c):
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def hex_rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))


def mix_hex(a, b, u):
    ra, rb = hex_rgb(a), hex_rgb(b)
    return "#" + "".join(f"{int(round((x + (y - x) * u) * 255)):02x}" for x, y in zip(ra, rb))


def ss(x):
    x = min(1.0, max(0.0, x))
    return x * x * (3 - 2 * x)


# ------------------------------------------------------------------------------------------------ cue helpers
def _cs(tl, name):
    return sorted([c for c in tl.get("cues", []) if c["name"] == name], key=lambda c: c["t"])


def last(tl, name, t):
    cur = None
    for c in _cs(tl, name):
        if c["t"] <= t + 1e-9:
            cur = c
    return cur


def merged(tl, name, t):
    d = {}
    for c in _cs(tl, name):
        if c["t"] <= t + 1e-9:
            d.update(c)
    return d


def ramp(tl, name, t, default=0.0):
    cur = default
    for c in _cs(tl, name):
        if c["t"] > t + 1e-9:
            break
        d = c.get("dur", 0.0)
        if d <= 0 or t >= c["t"] + d:
            cur = c["v"]
        else:
            cur = cur + (c["v"] - cur) * ss((t - c["t"]) / d)
            break
    return cur


def traj(tl, name, t):
    """An entity's position: the last cue with a pos, gliding there from the one before if it says glide."""
    cs = [c for c in _cs(tl, name) if "pos" in c]
    cur, prev = None, None
    for c in cs:
        if c["t"] <= t + 1e-9:
            prev, cur = cur, c
    if cur is None:
        return None
    p = list(cur["pos"])
    if prev is not None and cur.get("glide"):
        end = cur["t"] + cur["glide"]
        u = min(1.0, max(0.0, (t - cur["t"]) / cur["glide"])) if t < end else 1.0
        pa = prev["pos"] if "dest" not in prev else prev["dest"]
        p = [a + (b - a) * u for a, b in zip(pa, cur["pos"])]
    return p, cur


def traj2(tl, name, t):
    """Piecewise-linear motion: each cue {pos}, optionally {to, move} = go to `to` over `move` seconds from its time."""
    c = last(tl, name, t)
    if c is None:
        return None
    p = list(c["pos"])
    if "to" in c:
        u = ss((t - c["t"]) / max(1e-6, c["move"]))
        p = [a + (b - a) * u for a, b in zip(c["pos"], c["to"])]
    return p, c


# ------------------------------------------------------------------------------------------------ small builders
_n = [0]


def nm(base):
    _n[0] += 1
    return f"{base}{_n[0]}"


def B(kit, name, size, loc, mat, rot=(0, 0, 0), parent=None, bevel=0.0):
    return kit.box(nm(name), size, loc, mat, parent, rot, bevel)


def Bb(kit, name, lo, hi, mat, parent=None, bevel=0.0):
    """A box from corner lo to corner hi."""
    size = tuple(h - l for l, h in zip(lo, hi))
    loc = tuple((h + l) / 2 for l, h in zip(lo, hi))
    return kit.box(nm(name), size, loc, mat, parent, (0, 0, 0), bevel)


def C(kit, name, r, h, loc, mat, rot=(0, 0, 0), parent=None, n=20, r2=None):
    return kit.cyl(nm(name), r, h, loc, mat, parent, rot, n, r2)


def emissive(kit, name, hexc, strength):
    """An emission material with its Strength node kept so a cue can drive it."""
    m = kit.emit(hexc, strength, name=name)
    return m


def set_strength(m, v):
    for n in m.node_tree.nodes:
        if n.type == "EMISSION":
            n.inputs["Strength"].default_value = v


def alpha_mat(kit, name, hexc, emit_hex=None, emit_s=0.0, rough=0.9):
    """A translucent sheet whose alpha is a value node named 'alpha' (mist, wet prints)."""
    m = kit._new(name)
    nt = m.node_tree
    for n in list(nt.nodes):
        if n.type != "OUTPUT_MATERIAL":
            nt.nodes.remove(n)
    out = next(n for n in nt.nodes if n.type == "OUTPUT_MATERIAL")
    tr = nt.nodes.new("ShaderNodeBsdfTransparent")
    if emit_hex:
        sh = nt.nodes.new("ShaderNodeEmission")
        sh.inputs["Color"].default_value = kit.col(emit_hex)
        sh.inputs["Strength"].default_value = emit_s
    else:
        sh = nt.nodes.new("ShaderNodeBsdfDiffuse")
        sh.inputs["Color"].default_value = kit.col(hexc)
    val = nt.nodes.new("ShaderNodeValue")
    val.name = "alpha"
    val.outputs[0].default_value = 0.0
    mx = nt.nodes.new("ShaderNodeMixShader")
    nt.links.new(val.outputs[0], mx.inputs[0])
    nt.links.new(tr.outputs[0], mx.inputs[1])
    nt.links.new(sh.outputs[0], mx.inputs[2])
    nt.links.new(mx.outputs[0], out.inputs["Surface"])
    return m


def set_alpha(m, v):
    m.node_tree.nodes["alpha"].outputs[0].default_value = v


def show(objs, on):
    for o in objs:
        o.hide_render = not on


# ------------------------------------------------------------------------------------------------ materials
def materials(kit):
    M = {}
    M["conc"] = kit.concrete(WET, 1.4, 0.4, name="conc")
    M["floor"] = kit.concrete("#767b80", 1.8, 0.35, name="floorc")
    M["grass"] = kit.grime("#8f8a52", 0.6, 1.2, name="fieldgrass", rough=0.95)
    M["steel"] = kit.metal(STEEL, 0.45, name="steel")
    M["wallmetal"] = kit.grime("#8d98a0", 0.7, 2.0, name="wallmetal", rough=0.5)
    M["dark"] = kit.plastic("#16181c", 0.6, name="dark")
    M["blue"] = kit.plastic(WASH_BLUE, 0.5, name="blue")
    M["white"] = kit.plastic("#dfe6ea", 0.55, name="white")
    M["foam"] = kit.plastic(FOAM, 0.95, name="foam")
    M["cream"] = kit.plastic(CREAM, 0.7, name="cream")
    M["brass"] = kit.metal(BRASS, 0.28, name="brass")
    M["stripe"] = kit.plastic("#d8d6c8", 0.8, name="stripe")
    M["gold"] = kit.plastic(GOLD, 0.8, name="leafgold")
    M["rust"] = kit.plastic(RUST, 0.8, name="leafrust")
    M["rubber"] = kit.plastic("#222428", 0.9, name="rubber")
    M["roller"] = kit.metal("#6d767d", 0.35, name="roller")
    M["booth"] = kit.plastic(WASH_BLUE, 0.45, name="boothblue")
    M["boothin"] = kit.plastic("#cfd6da", 0.8, name="boothin")
    M["stool"] = kit.plastic("#4a5058", 0.7, name="stool")
    M["dust"] = kit.plastic("#9a948a", 1.0, name="dust")
    M["lever_w"] = kit.plastic("#eceff0", 0.4, name="lever_w")
    M["lever_y"] = kit.plastic("#e8c247", 0.4, name="lever_y")
    M["lever_b"] = kit.plastic("#3f8fcf", 0.4, name="lever_b")
    M["wood"] = kit.planks("#7a5a3a", "#5a4026", 1.2, "X", name="wood")
    M["wood2"] = kit.planks("#a98757", "#8a6b43", 1.5, "Y", name="wood2")
    M["plaster"] = kit.grime("#cdbfa8", 0.85, 2.0, name="plaster", rough=0.9)
    M["plaster2"] = kit.grime("#b7c0b0", 0.85, 2.0, name="plaster2", rough=0.9)
    M["night_wall"] = kit.grime("#5f6a78", 0.8, 2.0, name="nightwall", rough=0.9)
    M["brick"] = kit.bricks("#8b4c37", "#6a3a2c", "#55504a", 1.6, name="townbrick")
    M["cobble"] = kit.cobbles("#3b3d44", "#5c5a58", "#1a1a1d", 2.4, 0.3, name="towncob")
    M["cloth"] = kit.plastic("#b26a52", 0.95, name="blanket")
    M["blanket2"] = kit.plastic("#5c7aa0", 0.95, name="blanket2")
    M["pillow"] = kit.plastic("#e8e1d4", 0.9, name="pillow")
    M["pie"] = kit.plastic("#b57a3c", 0.7, name="pie")
    M["tin"] = kit.metal("#b9bec2", 0.4, name="tin")
    M["car_silver"] = kit.plastic("#b9c2c9", 0.35, name="car_silver")
    M["car_red"] = kit.plastic("#4f86c6", 0.35, name="car_red")
    M["car_teal"] = kit.plastic("#3b8a86", 0.4, name="car_teal")
    M["car_plum"] = kit.plastic("#7d4a86", 0.4, name="car_plum")
    M["car_sand"] = kit.plastic("#c7b27e", 0.4, name="car_sand")
    M["van"] = kit.plastic(MUSTARD, 0.45, name="van")
    M["drum"] = kit.plastic("#e8e3d4", 0.6, name="drum")
    M["footp"] = alpha_mat(kit, "footprint", "#20303c", None, 0.0)
    set_alpha(M["footp"], 0.0)
    M["handp"] = alpha_mat(kit, "handprint", "#0f1c2c", None, 0.0)
    M["mist"] = alpha_mat(kit, "mist", MISTC, MISTC, 1.1)
    M["lamp"] = emissive(kit, "drylamp", AMBER, 0.0)
    M["worklight"] = emissive(kit, "worklight", "#cfe0ff", 6.0)
    M["window_n"] = emissive(kit, "windnight", "#20365a", 0.9)
    M["window_warm"] = emissive(kit, "windwarm", "#ffcf88", 2.5)
    M["lampshade"] = emissive(kit, "lampshade", "#ffd9a0", 4.0)
    M["itemdark"] = kit.plastic("#101319", 0.35, name="itemdark")
    M["phoneglow"] = emissive(kit, "phoneglow", "#a8c8ff", 1.6)
    M["lightpanel"] = emissive(kit, "lightpanel", "#fff2dc", 3.0)
    M["scratch"] = kit.plastic(WASH_BLUE, 0.4, name="scratch")
    M["glass"] = kit.plastic("#7fa3b8", 0.1, name="glasspane")
    M["pane_dark"] = kit.plastic("#26303a", 0.2, name="panedark")
    M["bell"] = M["brass"]
    return M


# ------------------------------------------------------------------------------------------------ the wash
def build_ground(kit, ctx, M):
    kit.plane(nm("field"), (260, 260), (0, 0, -0.02), M["grass"])
    kit.plane(nm("forecourt"), (24, 44), (0, -22, 0), M["conc"])
    kit.plane(nm("apron"), (11.5, 3), (0, 1.0, 0.0), M["conc"])
    # the painted queue lane: two dashed lines, plain
    for sx in (-1, 1):
        for k in range(0, 9):
            B(kit, "dash", (0.12, 1.6, 0.012), (sx * 1.9, -1.8 - k * 2.8, 0.008), M["stripe"])
    for k in range(5):
        B(kit, "bar", (3.8, 0.14, 0.012), (0, -4.0 - k * 5.4, 0.008), M["stripe"])
    rng = random.Random(49)
    leaves = []
    for i in range(46):
        x, y = rng.uniform(-9, 9), rng.uniform(-30, -1)
        m = M["gold"] if rng.random() < 0.6 else M["rust"]
        leaves.append(B(kit, "leaf", (0.16, 0.12, 0.012), (x, y, 0.012), m, (0, 0, rng.uniform(0, 3.1))))
    ctx["leaves"] = leaves


def build_shed(kit, ctx, M):
    L = SHED_Y1
    # floor inside, roof, side walls (ribbed corrugated steel), no end walls: open both ends
    B(kit, "shedfloor", (8.4, L, 0.06), (0, L / 2, 0.02), M["floor"])
    B(kit, "roof", (8.8, L + 0.4, 0.18), (0, L / 2, ROOF + 0.1), M["steel"])
    for sx in (-1, 1):
        B(kit, "wall", (0.16, L, ROOF), (sx * 4.28, L / 2, ROOF / 2), M["wallmetal"])
        for k in range(int(L / 0.55)):
            B(kit, "rib", (0.07, 0.16, ROOF - 0.2), (sx * 4.16, 0.3 + k * 0.55, ROOF / 2), M["steel"])
        # a blue trim band along the top
        B(kit, "trim", (0.2, L, 0.28), (sx * 4.22, L / 2, ROOF - 0.5), M["blue"])
    # the conveyor: a low track with rollers
    B(kit, "track", (0.9, L + 4.0, 0.1), (0, L / 2 - 1.0, 0.07), M["rubber"])
    rollers = []
    for k in range(int((L + 4.0) / 0.4)):
        rollers.append(C(kit, "roller", 0.05, 0.8, (0, -3.0 + k * 0.4, 0.15), M["roller"], rot=(0, math.pi / 2, 0), n=10))
    ctx["rollers"] = rollers
    # work lights on the roof (steady): a tube and an area light
    for k, y in enumerate((2.0, 6.0, 10.0, 14.0)):
        B(kit, "worktube", (1.6, 0.18, 0.06), (0, y, ROOF - 0.06), M["worklight"])
        kit.light(f"work{k}", "AREA", (0, y, ROOF - 0.25), 260, "#cfe0ff", (0, 0, 0), size=2.4)
    # the foam arch (y 7): pillars, a top bar, hanging foam
    for sx in (-1, 1):
        B(kit, "fpil", (0.22, 0.3, 3.4), (sx * 3.95, 7.0, 1.7), M["steel"])
    B(kit, "fbar", (8.2, 0.34, 0.3), (0, 7.0, 3.35), M["blue"])
    for k in range(-7, 8):
        r = 0.2 + 0.07 * ((k * 7) % 3)
        kit.sphere(nm("foamb"), r, (k * 0.5, 7.0 + 0.04 * (k % 2), 3.0 - 0.1 * (k % 3)), M["foam"], seg=10)
    # the brushes: two pairs, tall cores with blue and white strips
    ctx["brushes"] = []
    for y in (9.3, 11.3):
        for sx in (-1, 1):
            root = kit.empty(nm("brush"), (sx * 1.8, y, 0.1))
            C(kit, "bcore", 0.14, 2.6, (0, 0, 1.3), M["dark"], parent=root, n=12)
            for k in range(14):
                a = 2 * math.pi * k / 14
                B(kit, "strip", (0.1, 0.5, 2.3), (math.cos(a) * 0.34, math.sin(a) * 0.34, 1.3),
                  M["blue"] if k % 2 else M["white"], rot=(0, 0, a + math.pi / 2), parent=root)
            ctx["brushes"].append(root)
    # the drying arch (y 13.5)
    for sx in (-1, 1):
        B(kit, "dpil", (0.26, 0.4, 3.2), (sx * 3.9, 13.5, 1.6), M["steel"])
    B(kit, "dbar", (8.2, 0.5, 0.34), (0, 13.5, 3.15), M["steel"])
    for x in (-2.4, -0.8, 0.8, 2.4):
        B(kit, "nozzle", (0.5, 0.7, 0.3), (x, 13.45, 2.75), M["dark"], (0.5, 0, 0))
    for sx in (-1, 1):
        B(kit, "snozzle", (0.4, 0.8, 0.3), (sx * 3.4, 13.45, 1.6), M["dark"], (0, 0, sx * 0.4))
    # the drying lamps, low along both walls
    lamps = []
    for sx in (-1, 1):
        for k in range(11):
            lamps.append(B(kit, "dlamp", (0.2, 0.55, 0.16), (sx * 3.98, 3.2 + k * 1.1, 0.36), M["lamp"], bevel=0.03))
        for k, y in enumerate((4.0, 7.5, 11.0, 14.5)):
            kit.light(f"dry{'L' if sx < 0 else 'R'}{k}", "POINT", (sx * 3.5, y, 0.55), 70, AMBER, size=0.5)
    ctx["lamps"] = lamps
    # the mist: translucent sheets across the tunnel, eased in by a cue
    sheets = []
    for k in range(12):
        y = 1.0 + k * 1.2
        sheets.append(B(kit, "mist", (8.0, 0.02, 3.9), (0, y, 1.95), M["mist"]))
    ctx["mist"] = sheets
    # footprints: five pairs down the left of the conveyor, toes toward the booth (-y), each fainter
    ctx["prints"] = []
    for k in range(5):
        y = 3.0 + k * 0.7
        for sx in (-1, 1):
            p = B(kit, "foot", (0.2, 0.46, 0.008), (-0.78 + sx * 0.14, y, 0.07), M["footp"])
            ctx["prints"].append((p, k))
    ctx["print_mats"] = []
    # one material per pair so each is fainter: duplicate the sheet material
    for k in range(5):
        m = M["footp"].copy()
        m.name = f"footprint{k}"
        ctx["print_mats"].append(m)
    for p, k in ctx["prints"]:
        p.data.materials.clear()
        p.data.materials.append(ctx["print_mats"][k])
    # the chain and its blank disc, across the lane at the mouth
    chain = []
    for k in range(21):
        u = k / 20
        x = -1.8 + 3.6 * u
        z = 1.05 - 0.22 * math.sin(math.pi * u)
        chain.append(B(kit, "link", (0.14, 0.05, 0.05), (x, -0.5, z), M["steel"], (0, 0, 0)))
    chain.append(C(kit, "disc", 0.2, 0.025, (0, -0.5, 0.58), M["white"], rot=(math.pi / 2, 0, 0), n=24))
    ctx["chain"] = chain


def build_booth(kit, ctx, M):
    x0, x1, y0, y1, H = -3.9, -2.1, 0.5, 2.5, 2.9
    t = 0.1
    B(kit, "bfloor", (x1 - x0, y1 - y0, 0.08), ((x0 + x1) / 2, (y0 + y1) / 2, 0.05), M["floor"])
    B(kit, "broof", (x1 - x0 + 0.3, y1 - y0 + 0.3, 0.12), ((x0 + x1) / 2, (y0 + y1) / 2, H + 0.06), M["steel"])
    Bb(kit, "bdoorL", (x0, y1 - t, 0), (-3.5, y1, H), M["booth"])
    Bb(kit, "bdoorR", (-2.7, y1 - t, 0), (x1, y1, H), M["booth"])
    Bb(kit, "bdoorT", (-3.5, y1 - t, 2.6), (-2.7, y1, H), M["booth"])
    Bb(kit, "bdoorframe1", (-3.56, y1 + 0.0, 0), (-3.5, y1 + 0.06, 2.6), M["white"])
    Bb(kit, "bdoorframe2", (-2.7, y1 + 0.0, 0), (-2.64, y1 + 0.06, 2.6), M["white"])
    # the -y wall is plain, with the beanie hook
    Bb(kit, "bfront", (x0, y0, 0), (x1, y0 + t, H), M["booth"])
    ctx["hook"] = B(kit, "hook", (0.05, 0.12, 0.05), (-3.0, y0 + t + 0.06, 1.95), M["steel"])
    B(kit, "hookplate", (0.12, 0.03, 0.2), (-3.0, y0 + t + 0.015, 1.95), M["steel"])
    ctx["beanie"] = B(kit, "beanie_hook", (0.22, 0.2, 0.2), (-3.0, y0 + t + 0.14, 1.8), kit.plastic(MUSTARD, 0.9, name="beaniemat"), bevel=0.07)
    # the -x wall plain
    Bb(kit, "bleft", (x0, y0, 0), (x0 + t, y1, H), M["booth"])
    # the +x wall with the hatch y 1.0 .. 2.0, z 1.1 .. 1.75
    Bb(kit, "bhatchL", (x1 - t, y0, 0), (x1, 1.0, H), M["booth"])
    Bb(kit, "bhatchR", (x1 - t, 2.0, 0), (x1, y1, H), M["booth"])
    Bb(kit, "bhatchB", (x1 - t, 1.0, 0), (x1, 2.0, 1.1), M["booth"])
    Bb(kit, "bhatchT", (x1 - t, 1.0, 1.75), (x1, 2.0, H), M["booth"])
    # the sill: a steel shelf under the hatch, y 0.85 .. 2.15, left end (low y) holds keys and clapper
    ctx["sill_top"] = 1.12
    Bb(kit, "sill", (x1 - 0.02, 0.85, 1.07), (x1 + 0.22, 2.15, 1.12), M["steel"])
    # the tally: two short upright strokes scratched in wash blue at the right end (high y)
    for k, y in enumerate((1.9, 2.0)):
        Bb(kit, "tally", (x1 + 0.02, y - 0.016, 1.1195), (x1 + 0.2, y + 0.016, 1.126), M["scratch"])
    # inside: a counter under the hatch, the till, two stools (one dusty), the lever panel on the +y wall
    Bb(kit, "counter", (x1 - 0.5, 1.0, 0), (x1 - t, 2.0, 1.02), M["boothin"])
    B(kit, "till", (0.3, 0.4, 0.2), (x1 - 0.3, 1.5, 1.12), M["dark"], bevel=0.03)
    for k in range(5):
        C(kit, "coin", 0.035, 0.012, (x1 - 0.22 + 0.01 * k, 1.8 + 0.03 * k, 1.03), M["brass"], n=10)
    for y, mat in ((1.95, M["stool"]), (1.15, M["stool"])):
        C(kit, "stoolseat", 0.2, 0.06, (-3.5, y, 0.66), mat, n=16)
        C(kit, "stoolleg", 0.04, 0.62, (-3.5, y, 0.33), M["steel"], n=8)
    C(kit, "dust", 0.19, 0.012, (-3.5, 1.15, 0.7), M["dust"], n=16)
    B(kit, "panel", (0.9, 0.08, 0.6), (-3.2, y0 + t + 0.05, 1.25), M["dark"], bevel=0.02)
    ctx["levers"] = {}
    for key, x, mat in (("w", -3.45, M["lever_w"]), ("y", -3.2, M["lever_y"]), ("b", -2.95, M["lever_b"])):
        piv = kit.empty(nm("leverpiv"), (x, y0 + t + 0.12, 1.1))
        B(kit, "leverstick", (0.05, 0.05, 0.26), (0, 0, 0.13), M["steel"], parent=piv)
        kit.sphere(nm("leverknob"), 0.06, (0, 0, 0.28), mat, piv, seg=10)
        ctx["levers"][key] = piv
        piv.rotation_euler = (0.0, 0, 0)
    kit.light("booth_lamp", "POINT", (-3.0, 1.5, 2.0), 38, "#ffd9a8", size=0.3)
    # the window-sill wet ring where the keys sat (shown for one shot)
    ctx["ring"] = C(kit, "wetring", 0.07, 0.006, (x1 + 0.1, 1.0, 1.125), kit.plastic("#4a5a66", 0.2, name="wetring"), n=18)
    # items on the sill and the conveyor: phone, keys, clapper
    ctx["phone"] = B(kit, "phone", (0.24, 0.46, 0.03), (0, 0, -5), kit.plastic("#2a2e36", 0.3, name="phonebody"), bevel=0.02)
    B(kit, "phonescreen", (0.2, 0.4, 0.006), (0, 0, 0.017), M["itemdark"], parent=ctx["phone"])
    ctx["keys"] = kit.empty(nm("keys"), (0, 0, -5))
    ctx["keys"].scale = (3.0, 3.0, 3.0)
    C(kit, "keyring", 0.04, 0.008, (0, 0, 0), M["itemdark"], parent=ctx["keys"], n=16)
    for k in range(3):
        B(kit, "key", (0.025, 0.07, 0.006), (0.0, -0.06, 0.0), M["itemdark"], (0, 0, 0.5 * (k - 1)), ctx["keys"])
    ctx["clapper"] = kit.empty(nm("clapper"), (0, 0, -5))
    kit.sphere(nm("clapperb"), 0.035, (0, 0, 0.0), M["brass"], ctx["clapper"], seg=10)
    C(kit, "clapperst", 0.008, 0.07, (0, 0, 0.06), M["brass"], parent=ctx["clapper"], n=8)
    C(kit, "clapperlp", 0.02, 0.004, (0, 0, 0.1), M["brass"], rot=(math.pi / 2, 0, 0), parent=ctx["clapper"], n=12)


def build_car(kit, name, mat, M, length=4.2, hatch=False):
    root = kit.empty(nm(name))
    Bb(kit, "carbody", (-0.9, -length / 2, 0.18), (0.9, length / 2, 0.9), mat, root, bevel=0.1)
    Bb(kit, "carhood", (-0.86, length / 2 - 1.2, 0.9), (0.86, length / 2 - 0.02, 0.98), mat, root, bevel=0.06)
    if hatch:
        Bb(kit, "cabin", (-0.84, -length / 2 + 0.2, 0.9), (0.84, -0.25, 1.55), mat, root, bevel=0.1)
        Bb(kit, "glass", (-0.86, -length / 2 + 0.3, 1.05), (0.86, -0.4, 1.4), M["pane_dark"], root)
    else:
        Bb(kit, "seatback", (-0.8, -0.65, 0.9), (0.8, -0.45, 1.12), M["rubber"], root, bevel=0.05)
        Bb(kit, "windshield", (-0.84, 0.5, 0.9), (0.84, 0.58, 1.3), M["pane_dark"], root)
    for sx in (-1, 1):
        for fy in (-1, 1):
            C(kit, "wheel", 0.33, 0.22, (sx * 0.9, fy * length * 0.31, 0.33), M["rubber"], rot=(0, math.pi / 2, 0), parent=root, n=14)
    for sx in (-1, 1):
        kit.sphere(nm("headlight"), 0.1, (sx * 0.55, length / 2 - 0.02, 0.7), kit.plastic("#f3ecd0", 0.2, name="headlamp"), root, seg=8)
    return root


def build_wash_extras(kit, ctx, M):
    # sign pole with a drawn car and three drops
    C(kit, "pole", 0.1, 5.0, (9.0, -6.0, 2.5), M["steel"], n=10)
    B(kit, "signboard", (2.2, 0.14, 1.6), (9.0, -6.05, 5.2), M["blue"], bevel=0.05)
    B(kit, "carsil", (1.0, 0.04, 0.32), (8.7, -6.14, 5.1), M["white"])
    B(kit, "carsil2", (0.55, 0.04, 0.26), (8.62, -6.14, 5.34), M["white"])
    for dx in (-0.22, 0.2):
        C(kit, "carsilw", 0.1, 0.04, (8.7 + dx, -6.14, 4.92), M["white"], rot=(math.pi / 2, 0, 0), n=10)
    for k in range(3):
        kit.sphere(nm("drop"), 0.1, (9.35, -6.14, 5.0 + 0.2 * k), M["white"], seg=8)
    # kiosk: cream box, a hatch toward -x, a counter with a tray of three pies
    Bb(kit, "kiosk", (6.0, -14.0, 0), (9.0, -11.0, 2.6), M["cream"])
    Bb(kit, "kioskroof", (5.8, -14.2, 2.6), (9.2, -10.8, 2.78), M["blue"])
    Bb(kit, "kiosk_hatchframe", (5.94, -13.2, 1.0), (6.02, -11.8, 2.0), M["dark"])
    Bb(kit, "kioskcounter", (5.7, -13.3, 0), (6.0, -11.7, 1.0), M["cream"])
    B(kit, "kiosk_tray", (0.34, 1.0, 0.03), (5.85, -12.5, 1.02), M["tin"])
    for k in range(3):
        C(kit, "pie", 0.14, 0.07, (5.85, -12.8 + 0.3 * k, 1.07), M["pie"], n=14)
    B(kit, "awning", (0.9, 2.2, 0.06), (5.55, -12.5, 2.25), M["blue"], (0, 0.25, 0))
    # a few cars: the queue of three (open tops, a driver each), the silver car, the red hatchback, the van
    ctx["cars"] = {
        "q1": build_car(kit, "car_q1", M["car_teal"], M),
        "q2": build_car(kit, "car_q2", M["car_plum"], M),
        "q3": build_car(kit, "car_q3", M["car_sand"], M),
        "silver": build_car(kit, "car_silver", M["car_silver"], M),
        "red": build_car(kit, "car_red", M["car_red"], M, hatch=True),
    }
    van = kit.empty(nm("van"))
    Bb(kit, "vbody", (-0.95, -1.9, 0.3), (0.95, 1.0, 2.1), M["van"], van, bevel=0.08)
    Bb(kit, "vcab", (-0.95, 1.0, 0.3), (0.95, 2.2, 1.4), M["van"], van, bevel=0.08)
    Bb(kit, "vglass", (-0.97, 1.05, 1.0), (0.97, 2.0, 1.35), M["pane_dark"], van)
    for sx in (-1, 1):
        for fy in (-1.1, 1.5):
            C(kit, "vwheel", 0.36, 0.24, (sx * 0.95, fy, 0.36), M["rubber"], rot=(0, math.pi / 2, 0), parent=van, n=14)
    # open back: the drums stacked to the roof (3 x 3 columns), doors swung wide
    for sx in (-1, 1):
        Bb(kit, "vdoor", (sx * 1.0 - 0.04 + (0.05 if sx > 0 else -0.05), -1.9, 0.3), (sx * 1.0 + 0.04 + (0.05 if sx > 0 else -0.05), -0.95 - 0.9, 2.1), M["van"], van)
    ctx["van_drums"] = []
    for i, x in enumerate((-0.55, 0.0, 0.55)):
        for z in (0.65, 1.2, 1.75):
            ctx["van_drums"].append(C(kit, "vdrum", 0.24, 0.5, (x, -1.45, z), M["drum"], parent=van, n=14))
            ctx["van_drums"].append(C(kit, "vdrum", 0.24, 0.5, (x, -0.9, z), M["drum"], parent=van, n=14))
            for d in ctx["van_drums"][-2:]:
                kit.sphere(nm("drumdrop"), 0.06, (0, -0.1, 0.0), M["blue"], d, seg=8)
    ctx["cars"]["van"] = van
    # a few more drums by the booth wall for the carry
    # the fence: a low rail at the forecourt's far side
    for k in range(-5, 6):
        B(kit, "post", (0.08, 0.08, 0.9), (k * 1.8, -39.0, 0.45), M["steel"])
    B(kit, "rail", (20, 0.05, 0.06), (0, -39.0, 0.8), M["steel"])


# ------------------------------------------------------------------------------------------------ small far sets
def room(kit, ox, oy, w, d, h, floor, wall, ceil=None, open_front=False, door_gap=None):
    """A room: floor, three walls and a ceiling, the front (-y) wall left off so the camera can sit in the room."""
    B(kit, "rfloor", (w, d, 0.1), (ox, oy, -0.05), floor)
    B(kit, "rback", (w, 0.12, h), (ox, oy + d / 2, h / 2), wall)
    B(kit, "rleft", (0.12, d, h), (ox - w / 2, oy, h / 2), wall)
    B(kit, "rright", (0.12, d, h), (ox + w / 2, oy, h / 2), wall)
    if ceil is not None:
        B(kit, "rceil", (w, d, 0.1), (ox, oy, h + 0.05), ceil)


def build_cafe(kit, ctx, M):
    ox, oy = OFF["cafe"]
    room(kit, ox, oy, 7, 6, 3.2, M["wood2"], M["plaster"], M["plaster"])
    C(kit, "table", 0.55, 0.05, (ox, oy + 0.2, 0.74), M["wood"], n=20)
    C(kit, "tablepost", 0.07, 0.72, (ox, oy + 0.2, 0.37), M["steel"], n=10)
    for sx in (-1, 1):
        B(kit, "chair", (0.45, 0.45, 0.06), (ox + sx * 1.35, oy + 0.3, 0.45), M["wood"])
        B(kit, "chairback", (0.06, 0.45, 0.5), (ox + sx * 1.55, oy + 0.3, 0.72), M["wood"])
        C(kit, "cup", 0.06, 0.09, (ox + sx * 0.25, oy + 0.15, 0.82), M["white"], n=12)
    Bb(kit, "winframe", (ox - 1.5, oy + 2.88, 1.0), (ox + 1.5, oy + 2.94, 2.4), M["window_warm"])
    kit.light("cafe_key", "AREA", (ox, oy - 1.0, 2.9), 220, "#ffe2b8", size=3.0)
    kit.light("cafe_fill", "POINT", (ox - 2.5, oy - 1.5, 2.0), 60, "#ffd4a0", size=0.5)


def build_wed(kit, ctx, M):
    ox, oy = OFF["wed"]
    room(kit, ox, oy, 9, 12, 4.0, M["wood2"], M["cream"], M["cream"])
    # a flower arch behind the couple and a runner
    for sx in (-1, 1):
        B(kit, "archpost", (0.12, 0.12, 2.9), (ox + sx * 1.2, oy + 0.6, 1.45), M["white"])
    B(kit, "archtop", (2.6, 0.14, 0.14), (ox, oy + 0.6, 2.9), M["white"])
    for k in range(9):
        kit.sphere(nm("bloom"), 0.12, (ox - 1.0 + 0.25 * k, oy + 0.6, 2.9 + 0.08 * (k % 2)), M["rust"] if k % 2 else M["gold"], seg=8)
    B(kit, "runner", (1.2, 10, 0.01), (ox, oy, 0.01), kit.plastic("#8a2f3a", 0.9, name="runner"))
    for sx in (-1, 1):
        for k in range(4):
            B(kit, "pew", (2.2, 0.35, 0.5), (ox + sx * 2.6, oy + 3.8 + k * 1.1, 0.25), M["wood"])
    kit.light("wed_key", "AREA", (ox, oy + 1.0, 3.6), 280, "#ffe6c4", size=4.0)
    kit.light("wed_fill", "AREA", (ox, oy + 6.0, 3.6), 160, "#ffe6c4", size=4.0)


def build_street(kit, ctx, M):
    ox, oy = OFF["street"]
    kit.plane(nm("streetground"), (40, 30), (ox, oy - 4, 0), M["cobble"])
    # the facade along y = oy + 2: a brick wall with three plain doors (open, dark behind) and a lit window
    fy = oy + 2.0
    xs = [(ox - 9, ox - 3.6)]
    doors = [ox - 3.3, ox + 0.9, ox + 3.2]
    win = (ox - 1.6, ox - 0.1)
    # wall pieces between openings
    edges = [("a", ox - 10, doors[0] - 0.5), ("b", doors[0] + 0.5, win[0]), ("c", win[1], doors[1] - 0.5), ("d", doors[1] + 0.5, doors[2] - 0.5), ("e", doors[2] + 0.5, ox + 10)]
    for k, a, b in edges:
        Bb(kit, "fac" + k, (a, fy, 0), (b, fy + 0.3, 3.2), M["brick"])
    for d in doors:
        Bb(kit, "doortop", (d - 0.5, fy, 2.15), (d + 0.5, fy + 0.3, 3.2), M["brick"])
        Bb(kit, "doorbox", (d - 0.5, fy + 0.3, 0), (d + 0.5, fy + 1.4, 2.15), M["dark"])
        Bb(kit, "doorfr", (d - 0.56, fy - 0.02, 0), (d - 0.5, fy + 0.04, 2.15), M["white"])
        Bb(kit, "doorfr2", (d + 0.5, fy - 0.02, 0), (d + 0.56, fy + 0.04, 2.15), M["white"])
    Bb(kit, "winlow", (win[0], fy, 0), (win[1], fy + 0.3, 0.95), M["brick"])
    Bb(kit, "winhigh", (win[0], fy, 2.0), (win[1], fy + 0.3, 3.2), M["brick"])
    Bb(kit, "winroom", (win[0], fy + 1.3, 0.95), (win[1], fy + 1.4, 2.0), M["window_warm"])
    Bb(kit, "winframe", (win[0] - 0.04, fy - 0.02, 0.92), (win[1] + 0.04, fy + 0.02, 0.95), M["white"])
    B(kit, "roofline", (22, 0.8, 0.3), (ox, fy + 0.3, 3.35), M["steel"])
    kit.light("street_win", "POINT", (win[0] + 0.7, fy - 0.4, 1.7), 24, "#ffcf88", size=0.2)
    for d in doors:
        kit.light(f"street_door{d:.0f}", "POINT", (d, fy - 0.5, 2.4), 10, "#ffcf9a", size=0.2)
    ctx["street"] = dict(doors=doors, win=win, fy=fy)
    # the phone glow, steady (a small dim panel in front of the texter's chest)
    ctx["glow"] = B(kit, "glow", (0.1, 0.02, 0.17), (win[0] + 0.75, fy + 0.62, 1.2), M["phoneglow"])


def build_flat(kit, ctx, M):
    ox, oy = OFF["flat"]
    room(kit, ox, oy, 6.0, 6.0, 2.6, M["wood"], M["plaster2"], M["plaster2"])
    # a window on the left wall (night blue), a picture-free plain east wall (the wall between our beds)
    Bb(kit, "flatwin", (ox - 3.0 + 0.07, oy - 0.8, 1.0), (ox - 3.0 + 0.1, oy + 0.8, 2.1), M["window_n"])
    # the bed: head to the east wall, along the north wall, a mattress and a blanket
    bx, by = ox - 1.0, oy + 1.9
    Bb(kit, "bedframe", (bx - 1.1, by - 0.5, 0.0), (bx + 1.1, by + 0.5, 0.28), M["wood"])
    Bb(kit, "mattress", (bx - 1.05, by - 0.47, 0.28), (bx + 1.05, by + 0.47, 0.5), M["pillow"], bevel=0.04)
    Bb(kit, "blanket", (bx - 1.06, by - 0.5, 0.5), (bx + 0.35, by + 0.5, 0.64), M["cloth"], bevel=0.05)
    Bb(kit, "pillow", (bx + 0.45, by - 0.3, 0.5), (bx + 0.95, by + 0.3, 0.64), M["pillow"], bevel=0.06)
    ctx["bed"] = (bx, by)
    # the bedside table with the warm lamp, a chair with my overalls and their bell
    B(kit, "nightstand", (0.4, 0.4, 0.5), (bx + 1.5, by + 0.1, 0.25), M["wood"])
    kit.sphere(nm("lampbase"), 0.1, (bx + 1.5, by + 0.1, 0.58), M["lampshade"], seg=10)
    kit.light("flat_lamp", "POINT", (bx + 1.4, by - 0.1, 0.8), 14, "#ffcf90", size=0.12)
    kit.light("flat_fill", "AREA", (ox, oy, 2.5), 90, "#a9bde0", size=3.0)
    chx, chy = ox - 2.0, oy + 0.6
    B(kit, "chair", (0.5, 0.5, 0.06), (chx, chy, 0.46), M["wood"])
    B(kit, "chairback", (0.06, 0.5, 0.55), (chx - 0.22, chy, 0.75), M["wood"])
    for sx in (-1, 1):
        for sy in (-1, 1):
            B(kit, "chairleg", (0.05, 0.05, 0.43), (chx + sx * 0.2, chy + sy * 0.2, 0.22), M["wood"])
    ctx["overalls"] = B(kit, "overalls", (0.44, 0.34, 0.3), (chx, chy, 0.65), kit.plastic(GREEN, 0.9, name="overallmat"), bevel=0.05)
    B(kit, "overalls_bib", (0.4, 0.05, 0.5), (chx + 0.02, chy, 0.95), kit.plastic(GREEN, 0.9, name="overallmat"), (0, 0, 0))
    ctx["chair_bell"] = kit.empty(nm("chair_bell"), (chx + 0.04, chy - 0.04, 1.15))
    make_bell_geo(kit, ctx["chair_bell"], 0.07, M, False)
    # the kitchen
    ox, oy = OFF["kitchen"]
    room(kit, ox, oy, 5.0, 4.5, 2.6, M["wood"], M["plaster"], M["plaster"])
    Bb(kit, "kcounter", (ox - 2.5, oy + 1.5, 0), (ox + 2.5, oy + 2.2, 0.92), M["cream"])
    Bb(kit, "kcounter_top", (ox - 2.5, oy + 1.45, 0.92), (ox + 2.5, oy + 2.2, 0.96), M["wood"])
    Bb(kit, "kwin", (ox + 1.3, oy + 2.18, 1.1), (ox + 2.3, oy + 2.22, 2.1), M["window_warm"])
    C(kit, "ktable", 0.5, 0.05, (ox - 1.3, oy - 0.2, 0.74), M["wood"], n=18)
    C(kit, "ktablepost", 0.06, 0.72, (ox - 1.3, oy - 0.2, 0.36), M["steel"], n=8)
    for k in range(2):
        C(kit, "kmug", 0.05, 0.09, (ox - 1.3 + 0.2 * k, oy - 0.25, 0.8), M["white"], n=10)
    kit.light("kitchen_key", "AREA", (ox, oy - 0.5, 2.5), 230, "#ffe9c8", size=2.8)


# ------------------------------------------------------------------------------------------------ bells
def make_bell_geo(kit, pivot, r, M, with_clapper=True):
    """A small brass collar bell hanging from `pivot`: a dome, a dark slot mouth, a loop and a clapper."""
    d = kit.sphere(nm("belldome"), r, (0, 0, -r * 0.9), M["brass"], pivot, seg=14)
    d.scale = (1.0, 1.0, 0.9)
    C(kit, "bellrim", r * 0.98, r * 0.18, (0, 0, -r * 1.62), M["brass"], parent=pivot, n=16)
    m = C(kit, "bellmouth", r * 0.72, r * 0.05, (0, 0, -r * 1.74), M["dark"], parent=pivot, n=14)
    B(kit, "bellloop", (r * 0.3, r * 0.15, r * 0.5), (0, 0, r * 0.2), M["brass"], parent=pivot, bevel=r * 0.04)
    cl = None
    if with_clapper:
        cl = kit.sphere(nm("bellclapper"), r * 0.34, (0, 0, -r * 1.98), M["brass"], pivot, seg=8)
        cl.hide_render = True
    return d, cl


def attach(kit, story, ctx, M):
    """Bells on collars, Ruben's pocket, my bag, Ruben's drum: parented to each character's torso (the rig is built
    after set.build, so this runs on the first frame)."""
    ctx["bells"], ctx["clappers"] = {}, {}
    names = [n for n in story["cast"] if not n.startswith("st")]
    for who in names:
        torso = bpy.data.objects.get(f"{who}.torso")
        if torso is None:
            continue
        piv = kit.empty(nm(f"bell_{who}"), (-0.52, -0.78, 1.86), torso)
        d, cl = make_bell_geo(kit, piv, 0.25, M)
        ctx["bells"][who] = piv
        ctx["clappers"][who] = cl
    ru = bpy.data.objects.get("ruben.torso")
    if ru is not None:
        pm = kit.plastic("#2c4a37", 0.9, name="pocketmat")
        ctx["pocket"] = B(kit, "pocket", (0.78, 0.06, 0.56), (0.5, -0.62, 1.15), pm, parent=ru, bevel=0.03)
        ctx["pocket_base"] = tuple(ctx["pocket"].location)
        ctx["drum"] = C(kit, "carrydrum", 0.7, 1.9, (0, -1.5, 0.8), M["drum"], parent=ru, n=18)
        kit.sphere(nm("carrydrop"), 0.18, (0, -0.72, 0.2), M["blue"], ctx["drum"], seg=8)
        ctx["drum"].hide_render = True
        for c in ctx["drum"].children:
            c.hide_render = True
    me = bpy.data.objects.get("me.torso")
    if me is not None:
        bag = B(kit, "bag", (1.0, 0.7, 1.2), (1.35, 0.55, 0.9), kit.plastic("#5a4a3a", 0.9, name="bagmat"), parent=me, bevel=0.1)
        strap = B(kit, "bagstrap", (0.22, 1.05, 0.06), (0.85, 0.0, 1.98), kit.plastic("#5a4a3a", 0.9, name="bagmat"), parent=me)
        ctx["bag"] = [bag, strap]
        show(ctx["bag"], False)
    # shoulder straps for the overalls (cosmetic): both of us and Ruben
    for who in ("me", "ruben"):
        t = bpy.data.objects.get(f"{who}.torso")
        if t is None:
            continue
        gm = kit.plastic(GREEN, 0.8, name="strapmat")
        for sx in (-1, 1):
            B(kit, "strap", (0.28, 1.04, 0.1), (sx * 0.62, 0.0, 1.97), gm, parent=t)
            B(kit, "strapf", (0.28, 0.06, 0.45), (sx * 0.62, -0.54, 1.75), gm, parent=t)


def make_fade(kit, who, ctx):
    """Give a Stutter copy a fade: wrap every material's shader in a mix with a transparent shader."""
    vals = []
    seen = set()
    root = bpy.data.objects.get(who)
    if root is None:
        return vals
    for ob in [root] + list(root.children_recursive):
        if ob.type != "MESH":
            continue
        for slot in ob.material_slots:
            m = slot.material
            if m is None or m.name in seen:
                continue
            seen.add(m.name)
            nt = m.node_tree
            out = next(n for n in nt.nodes if n.type == "OUTPUT_MATERIAL")
            lk = out.inputs["Surface"].links
            if not lk:
                continue
            src = lk[0].from_socket
            tr = nt.nodes.new("ShaderNodeBsdfTransparent")
            val = nt.nodes.new("ShaderNodeValue")
            val.outputs[0].default_value = 1.0
            mx = nt.nodes.new("ShaderNodeMixShader")
            nt.links.new(val.outputs[0], mx.inputs[0])
            nt.links.new(tr.outputs[0], mx.inputs[1])
            nt.links.new(src, mx.inputs[2])
            nt.links.new(mx.outputs[0], out.inputs["Surface"])
            vals.append(val)
    return vals


# ------------------------------------------------------------------------------------------------ build
def build(kit, story, tl):
    ctx = {"attached": False, "fades": {}}
    sc = bpy.context.scene
    sc.cycles.transparent_max_bounces = 24
    M = materials(kit)
    ctx["M"] = M
    build_ground(kit, ctx, M)
    build_shed(kit, ctx, M)
    build_booth(kit, ctx, M)
    build_wash_extras(kit, ctx, M)
    build_cafe(kit, ctx, M)
    build_wed(kit, ctx, M)
    build_street(kit, ctx, M)
    build_flat(kit, ctx, M)
    # the sun, steady direction per time of day
    sun = kit.light("sun", "SUN", (-9, -12, 14), 1.0, "#fff0da")
    sun.data.angle = math.radians(4)
    ctx["sun"] = sun
    # the Stutter's lights: an amber key from low on the right, a cold rim behind (both ride the drying lamps)
    kit.light("skey", "SPOT", (-1.0, 2.2, 0.25), 520, AMBER, spot=70, blend=0.5, size=0.4)
    kit.aim(kit.LIGHTS["skey"]["obj"], (-3.1, 4.2, 1.2))
    kit.light("skey2", "SPOT", (-1.1, 6.5, 0.3), 380, AMBER, spot=60, blend=0.5, size=0.4)
    kit.aim(kit.LIGHTS["skey2"]["obj"], (-3.1, 4.4, 1.2))
    kit.light("skey3", "SPOT", (-3.1, 1.0, 0.1), 260, AMBER, spot=60, blend=0.5, size=0.3)
    kit.aim(kit.LIGHTS["skey3"]["obj"], (-3.1, 2.7, 1.5))
    kit.light("srim", "SPOT", (-4.0, 1.2, 2.6), 520, "#7fb0ff", spot=75, blend=0.5, size=0.3)
    kit.aim(kit.LIGHTS["srim"]["obj"], (-3.1, 4.6, 1.3))
    # soft fills so a forecourt face reads under the overcast sky
    kit.light("yard_fill", "AREA", (0, -7, 6), 380, "#f4f1ea", size=10)
    kit.aim(kit.LIGHTS["yard_fill"]["obj"], (0, -7, 0))
    kit.light("hatch_fill", "POINT", (-1.0, 0.0, 1.6), 80, "#ffe9d0", size=0.3)
    # the Stutter in the mist: a cold back light behind it, a blue rim; the lean: a low amber key from below
    kit.light("collar_lamp", "SPOT", (-3.5, 0.65, 1.9), 140, "#ffd9a8", spot=70, blend=0.6, size=0.3)
    kit.aim(kit.LIGHTS["collar_lamp"]["obj"], (-3.0, 2.0, 1.5))
    kit.light("figback", "POINT", (-3.1, 12.6, 1.7), 900, "#cfe6ff", size=0.8)
    kit.light("figrim", "SPOT", (-4.0, 12.0, 2.8), 700, "#7fb0ff", spot=60, blend=0.5, size=0.3)
    kit.aim(kit.LIGHTS["figrim"]["obj"], (-3.1, 9.8, 1.4))
    kit.light("leankey", "SPOT", (-1.9, 2.78, 0.95), 110, AMBER, spot=60, blend=0.5, size=0.25)
    kit.aim(kit.LIGHTS["leankey"]["obj"], (-2.2, 2.78, 1.75))
    kit.light("item_lamp", "SPOT", (0.5, 0.2, 1.3), 90, "#ffe2b0", spot=70, blend=0.5, size=0.3)
    kit.aim(kit.LIGHTS["item_lamp"]["obj"], (0.0, 1.6, 0.25))
    kit.light("sill_rake", "SPOT", (-1.2, 1.4, 1.5), 120, "#ffd9a0", spot=40, blend=0.5, size=0.1)
    kit.aim(kit.LIGHTS["sill_rake"]["obj"], (-2.05, 1.9, 1.1))
    ctx["lamp_rows"] = [n for n in kit.LIGHTS if n.startswith("dry")]
    return ctx


# ------------------------------------------------------------------------------------------------ animate
def place(ob, p, yaw=0.0):
    ob.location = (p[0], p[1], p[2] if len(p) > 2 else 0.0)
    ob.rotation_euler = (0, 0, math.radians(yaw))


def car_state(tl, key, t):
    r = traj2(tl, "car:" + key, t)
    if r is None:
        return None
    p, c = r
    return p, c.get("yaw", 0.0), c.get("on", True)


def bell_wobble(tl, who, t):
    amp = 0.0
    ph = 0.0
    for c in _cs(tl, "ring"):
        if c["who"] != who or c["t"] > t:
            continue
        n = int(c.get("dur", 0.0) * c.get("rate", 1.0)) + 1
        for k in range(n):
            te = c["t"] + k / c.get("rate", 1.0)
            if 0 <= t - te < 1.1:
                x = t - te
                amp += c.get("amp", 1.0) * math.exp(-x / 0.3) * math.sin(2 * math.pi * 6.5 * x)
    for c in _cs(tl, "sway"):
        if t >= c["t"] and t < c["t"] + c["dur"] and who in c["who"]:
            x = t - c["t"]
            env = min(1.0, x / 0.3) * min(1.0, (c["dur"] - x) / 0.5)
            amp += 0.9 * env * (math.sin(2 * math.pi * 1.6 * x + sum(map(ord, who)) % 7) + 0.4 * math.sin(2 * math.pi * 3.1 * x))
    return amp


def animate(kit, story, tl, t, ctx):
    M = ctx["M"]
    if not ctx["attached"]:
        ctx["attached"] = True
        attach(kit, story, ctx, M)
        for k in range(5):
            ctx["fades"][k] = make_fade(kit, f"st{k}", ctx)
            # the Stutter's arms are too long: they hang past the hip, nearly to the knee
            for sx in (-1, 1):
                arm = bpy.data.objects.get(f"st{k}.arm{sx}")
                if arm is not None:
                    arm.scale = (1.0, 1.0, 1.6)
    # ---- the time of day
    tod = (last(tl, "tod", t) or {"set": "day"})["set"]
    T = TOD[tod]
    sun = ctx["sun"]
    sun.data.color = kit.col(T["sun_c"])[:3]
    sun.location = T["loc"]
    kit.aim(sun, (0, 0, 0))
    w = bpy.context.scene.world
    bg = w.node_tree.nodes["Background"]
    bg.inputs["Color"].default_value = kit.col(T["sky"])
    bg.inputs["Strength"].default_value = T["sky_s"]
    g = {"sun": T["sun"], "flat_fill": T["flat"], "flat_lamp": 1.0, "yard_fill": T["yard"], "hatch_fill": T["yard"]}
    for k in range(4):
        g[f"work{k}"] = T["work"]
    # ---- the drying lamps and the Stutter's lights
    dry = ramp(tl, "dry", t, 0.0)
    set_strength(M["lamp"], 7.0 * dry)
    for n in ctx["lamp_rows"]:
        g[n] = dry
    for n in ("skey", "skey2", "skey3", "srim"):
        g[n] = dry
    sil = ramp(tl, "sil", t, 0.0)
    g["figback"] = sil
    g["figrim"] = sil
    g["collar_lamp"] = ramp(tl, "collarlit", t, 0.0)
    g["leankey"] = ramp(tl, "leankey", t, 0.0)
    g["booth_lamp"] = 1.0 - ramp(tl, "boothoff", t, 0.0)
    g["skey3"] = 1.0 - 0.9 * ramp(tl, "boothoff", t, 0.0) if "skey3" in g else 0.0
    # darken the Stutter's copies against the mist
    if "st_cols" not in ctx:
        ctx["st_cols"] = []
        for k in range(5):
            root = bpy.data.objects.get(f"st{k}")
            seen = set()
            for ob in [root] + list(root.children_recursive) if root else []:
                if ob.type != "MESH":
                    continue
                for slot in ob.material_slots:
                    m = slot.material
                    if m is None or m.name in seen or not m.node_tree:
                        continue
                    seen.add(m.name)
                    for n in m.node_tree.nodes:
                        if n.type == "BSDF_PRINCIPLED":
                            ctx["st_cols"].append((n.inputs["Base Color"], tuple(n.inputs["Base Color"].default_value)))
                            for lk in m.node_tree.links:
                                if lk.to_socket == n.inputs["Base Color"]:
                                    ctx.setdefault("st_links", []).append((m.node_tree, lk.from_socket, lk.to_socket))
    dark = sil > 0.5
    if dark != ctx.get("st_dark", False):
        ctx["st_dark"] = dark
        for tree, a, b in ctx.get("st_links", []):
            if dark:
                for lk in list(tree.links):
                    if lk.to_socket == b:
                        tree.links.remove(lk)
            elif not any(lk.to_socket == b for lk in tree.links):
                tree.links.new(a, b)
    for sock, c0 in ctx["st_cols"]:
        u = (1.0 if dark else 0.82 * sil)
        sock.default_value = (c0[0] * (1 - u) + 0.01 * u, c0[1] * (1 - u) + 0.02 * u, c0[2] * (1 - u) + 0.05 * u, c0[3])
    # ---- the mist, the brushes, the lever
    mist = ramp(tl, "mist", t, 0.0)
    for s in ctx["mist"]:
        s.hide_render = mist < 0.01
    set_alpha(M["mist"], 0.085 * mist)
    if "spin_table" not in ctx:
        ctx["spin_table"] = build_spin(tl)
    spin = ctx["spin_table"]
    ang = spin(t)
    for i, b in enumerate(ctx["brushes"]):
        b.rotation_euler = (0, 0, ang * (1 if i % 2 else -1) * 2 * math.pi + i)
    lv = ramp(tl, "lever", t, 0.0)
    ctx["levers"]["b"].rotation_euler = (-0.9 * lv, 0, 0)
    # ---- footprints, handprints, the chain
    fo = (last(tl, "foot", t) or {"on": False})["on"]
    for p, k in ctx["prints"]:
        p.hide_render = not fo
    for k, m in enumerate(ctx["print_mats"]):
        set_alpha(m, (0.62 - 0.12 * k) if fo else 0.0)
    ha = (last(tl, "hand", t) or {"on": False})["on"]
    if "handprints" not in ctx:
        ctx["handprints"] = make_handprints(kit, ctx, M)
    for h in ctx["handprints"]:
        h.hide_render = not ha
    for k, m in enumerate(ctx.get("hand_mats", [])):
        set_alpha(m, 0.95 - 0.15 * k)
    show(ctx["chain"], (last(tl, "chain", t) or {"on": False})["on"])
    show([ctx["ring"]], (last(tl, "ring_mark", t) or {"on": False})["on"])
    # ---- cars and the items
    for key, root in ctx["cars"].items():
        s = car_state(tl, key, t)
        if s is None:
            show([root] + list(root.children_recursive), False)
            continue
        p, yaw, on = s
        show([root] + list(root.children_recursive), on)
        place(root, p, yaw)
    for name in ("phone", "keys", "clapper"):
        ob = ctx[name]
        r = traj2(tl, "item:" + name, t)
        objs = [ob] + list(ob.children_recursive)
        if r is None or not r[1].get("on", True):
            show(objs, False)
            continue
        p, c = r
        show(objs, True)
        ob.location = tuple(p)
        ob.rotation_euler = (0, 0, math.radians(c.get("yaw", 0.0)))
    g["item_lamp"] = 1.0 if (traj2(tl, "item:phone", t) and traj2(tl, "item:phone", t)[1].get("on", True)) else 0.0
    # ---- my clapper in my bell, my bag, Ruben's drum
    cm = (last(tl, "clapper", t) or {"on": False})["on"]
    if ctx["clappers"].get("me") is not None:
        ctx["clappers"]["me"].hide_render = not cm
    show(ctx["bag"], (last(tl, "bag", t) or {"on": False})["on"])
    if "drum" in ctx:
        dr = (last(tl, "carry", t) or {"on": False})["on"]
        show([ctx["drum"]] + list(ctx["drum"].children), dr)
        # the pocket's jump: one hop
        jump = 0.0
        for c in _cs(tl, "pocket"):
            x = t - c["t"]
            if 0 <= x < 0.5:
                jump += math.sin(math.pi * x / 0.5) * 0.14
        b = ctx["pocket_base"]
        ctx["pocket"].location = (b[0], b[1] - jump * 0.5, b[2] + jump)
    # ---- the beanie on its hook: there until Ruben takes it (before L27), gone after
    show([ctx["beanie"]], (last(tl, "beanie", t) or {"on": True})["on"])
    # ---- the street phone glow, the wet ring on the sill
    # ---- bells
    for who, piv in ctx["bells"].items():
        a = bell_wobble(tl, who, t)
        piv.rotation_euler = (0.5 * a * 0.6, 0.3 * a * 0.6, 0)
    cb = ctx["chair_bell"]
    tr = 0.0
    for c in _cs(tl, "trem"):
        if c["t"] <= t < c["t"] + c["dur"]:
            x = t - c["t"]
            tr = (1 - ss((x - c["dur"] * 0.4) / (c["dur"] * 0.6))) * math.sin(2 * math.pi * 11 * x) * 0.5
    cb.rotation_euler = (tr, tr * 0.6, 0)
    # ---- riders: a character sitting in a car moves with it
    for who, rc in riders(tl, t).items():
        ob = bpy.data.objects.get(who)
        s = car_state(tl, rc["car"], t)
        if ob is None or s is None:
            continue
        p, yaw, on = s
        off = rc["off"]
        a = math.radians(yaw)
        x = p[0] + off[0] * math.cos(a) - off[1] * math.sin(a)
        y = p[1] + off[0] * math.sin(a) + off[1] * math.cos(a)
        ob.location = (x, y, off[2])
    # ---- the Stutter's fades
    base = (1.0, 0.8, 0.62, 0.44, 0.28)
    for k in range(5):
        v = base[k]
        for c in _cs(tl, "fade"):
            if c["k"] == k:
                v *= 1.0 - ss((t - c["t"]) / max(1e-6, c["dur"]))
        for val in ctx["fades"].get(k, []):
            val.outputs[0].default_value = v
    return g


def riders(tl, t):
    out = {}
    for c in _cs(tl, "ride"):
        if c["t"] <= t + 1e-9:
            if c.get("car"):
                out[c["who"]] = c
            else:
                out.pop(c["who"], None)
    return out


def build_spin(tl):
    """Brush angle in turns by time: the integral of the eased speed cues, tabulated every 0.05 s."""
    dur = tl["duration"] + 1
    n = int(dur / 0.05) + 2
    tab = [0.0] * n
    for i in range(1, n):
        tab[i] = tab[i - 1] + ramp(tl, "spin", i * 0.05, 0.0) * 0.05

    def f(t):
        x = min(max(t, 0.0) / 0.05, n - 1.001)
        i = int(x)
        return tab[i] + (tab[i + 1] - tab[i]) * (x - i)
    return f


def make_handprints(kit, ctx, M):
    car = ctx["cars"]["silver"]
    hs = []
    ctx["hand_mats"] = []
    for k in range(5):
        # a wet hand pressed on the silver car's left side (x -0.9): palm, four fingers and a thumb, five in a row
        m = M["handp"].copy()
        m.name = f"handprint{k}"
        ctx["hand_mats"].append(m)
        y0 = -1.3 + 0.62 * k
        X = -0.912
        hs.append(B(kit, "handp", (0.012, 0.2, 0.22), (X, y0, 0.55), m, parent=car))
        for j, (dy, ln) in enumerate(((-0.075, 0.13), (-0.025, 0.16), (0.025, 0.17), (0.075, 0.13))):
            hs.append(B(kit, "handf", (0.012, 0.04, ln), (X, y0 + dy, 0.66 + ln / 2), m, parent=car))
        hs.append(B(kit, "handt", (0.012, 0.13, 0.05), (X, y0 + 0.14, 0.6), m, (0.6, 0, 0), parent=car))
    return hs
