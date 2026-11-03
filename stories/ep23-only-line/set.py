"""Only Line (ep23, redo): a sunny town street corner, the playhouse stage door at dusk, and the playhouse stage in
rehearsal week, where the people who faded all the way stand in the wings. Built from kit.py's parts; nothing here is
shared with another story's set (the fade mechanism is patterned on ep49-car-wash's make_fade, copied).

Coordinates (metres, z up, the stage floor is z = 0). The stage runs x -9 .. 9 from the lip (y = 0) to the brick
back wall (y = 7.2). The proscenium is at y = -0.2 with its opening x -4.2 .. 4.2. A character with yaw 0 faces
-y, which is the house: the seats start at y = -2.6 and step back and up. Stage left is +x: four bottle-green curtain
legs hang there (inner edge x = 3.7). The town street is a little set at x = -40 (a brick terrace along y = 4.5) and the
stage door at x = +40 (a brick wall along y = 3.2); nothing in common with the stage.

Cues read here:
- mood: {"set": a MOODS name, "dur": s} the light, eased from the mood before (every change is a ramp)
- fade: {"who": key, "a": 0..1, "dur": s} a character's transparency, eased from its last value (ep49's pattern).
  Face strokes stay stronger than the body: the head's alpha is min(1, 1.6 x the body's). The tin crown never fades.
- costume: {"who": "walt", "beard": b, "crown": b, "robe": b} or {"who": "me", "cloak": b, "ears": b, "palm": b}
- throne: {"on": bool}   - audience: {"on": bool}
Acting keys read here (acting.py ignores them): "sit": true (R6 sitting, the legs straight out).
"""

from __future__ import annotations

import math

import bpy

TX, SDX = -40.0, 40.0
ROWS = 10
ROW_Y0, ROW_DY, ROW_Z0, ROW_DZ = -2.6, 0.95, -0.65, 0.12
THRONE = (0.0, 2.5)
FADERS = ("walt", "stopman", "mime", "busker", "f1", "f2", "f3", "f4")
FADED = ("f1", "f2", "f3", "f4")


def row_y(r):
    return ROW_Y0 - ROW_DY * r


def row_z(r):
    return ROW_Z0 + ROW_DZ * r


def seat_xs():
    return [round(-4.06 + 0.58 * k, 2) for k in range(15) if not (-2.7 < -4.06 + 0.58 * k < -2.0)]


# ------------------------------------------------------------------------------------------------ helpers


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


def _show(ob, on):
    for o in [ob] + list(ob.children_recursive):
        o.hide_render = not on


def pleated(kit, name, x0, x1, y, z0, z1, mat, folds=8, amp=0.07):
    """A curtain leg: a velvet sheet hanging in folds."""
    n = folds * 5
    verts, faces = [], []
    for i in range(n + 1):
        u = i / n
        verts += [(x0 + (x1 - x0) * u, y + amp * math.sin(u * folds * 2 * math.pi), z0),
                  (x0 + (x1 - x0) * u, y + amp * math.sin(u * folds * 2 * math.pi), z1)]
    for i in range(n):
        a = 2 * i
        faces.append((a, a + 2, a + 3, a + 1))
    return kit.mesh_obj(name, verts, faces, mat, None, smooth=True)


def light_only(kit, coll, light_name, objs):
    col = bpy.data.collections.get(coll) or bpy.data.collections.new(coll)
    for ob in objs:
        if ob.name not in col.objects:
            col.objects.link(ob)
    for co in col.collection_objects:
        co.light_linking.link_state = "INCLUDE"
    kit.LIGHTS[light_name]["obj"].light_linking.receiver_collection = col


def lamp(kit, name, kind, loc, energy, hexc, aim=None, size=0.2, spot=None, blend=0.4):
    ob = kit.light(name, kind, loc, energy, hexc, size=size, spot=spot, blend=blend)
    ob.visible_camera = False
    if aim is not None:
        kit.aim(ob, aim)
    return ob


# ------------------------------------------------------------------------------------------------ materials


def materials(kit):
    M = {}
    M["wood"] = kit.planks("#4a3626", "#2a1e15", scale=1.4, axis="Y", name="stage boards", rough=0.7)
    M["brick"] = kit.bricks("#5a4b4a", "#443837", mortar="#262223", scale=1.0, name="cold brick", grime_amt=0.5)
    M["black"] = kit.plastic("#08080a", 0.7, name="black")
    M["gilt_dull"] = kit.plastic("#7d6428", 0.5, name="gilt dull")
    M["velvet"] = kit.plastic("#1a4a35", 0.97, name="velvet")
    M["seat"] = kit.plastic("#4b4049", 0.92, name="seat plum")
    M["carpet"] = kit.grime("#2a1f27", 0.5, 2.0, name="carpet", rough=0.95)
    M["tape_w"] = kit.plastic("#cfc8b2", 0.85, name="tape white")
    M["tape_y"] = kit.plastic("#e3b81f", 0.85, name="tape yellow")
    M["steel"] = kit.metal("#6c7075", 0.45, name="steel")
    M["crown_tin"] = kit.plastic("#9ba2a8", 0.4, name="crown tin", spec=0.8)
    M["tin"] = kit.plastic("#9ba2a8", 0.4, name="tin", spec=0.8)
    M["white"] = kit.plastic("#e9e9e4", 0.9, name="beard white")
    M["robe"] = kit.plastic("#2c3b5c", 0.9, name="robe")
    M["robe_trim"] = kit.plastic("#b8913a", 0.5, name="robe trim")
    M["cloak"] = kit.plastic("#2b2d33", 0.95, name="cloak")
    M["wood_dark"] = kit.plastic("#3a2a1e", 0.7, name="chair wood")
    M["paper"] = kit.plastic("#d9d4c6", 0.9, name="paper")
    M["bulb"] = kit.emit("#ffe3b0", 6.0, name="bulb")
    M["head_dark"] = kit.plastic("#7a6a66", 0.9, name="aud head")
    M["body_dark"] = kit.plastic("#3c3a52", 0.9, name="aud body")
    M["roll"] = kit.plastic("#e6dcc2", 0.85, name="script roll")
    M["roll_end"] = kit.plastic("#b9ad92", 0.9, name="script roll end")
    M["glint"] = kit.emit("#ffb35c", 9.0, name="eye glint")
    return M


def town_materials(kit, M):
    """The sunny street: light fog so the far wall stays warm and bright."""
    old = dict(kit.FOG)
    kit.set_fog("#f1e3c4", 0.01, 14.0)
    M["t_brick"] = kit.bricks("#b0603f", "#94503a", mortar="#7d6f62", scale=1.0, name="warm brick", grime_amt=0.25)
    M["t_cobble"] = kit.cobbles("#6f6c66", "#a39e93", "#3c3a38", scale=2.2, wet=0.1, name="sunny cobbles")
    M["t_pave"] = kit.plastic("#b9b3a6", 0.9, name="pavement")
    M["t_teal"] = kit.plastic("#1f8a86", 0.5, name="door teal")
    M["t_cherry"] = kit.plastic("#b8223a", 0.5, name="door cherry")
    M["t_navy"] = kit.plastic("#233f7a", 0.5, name="door navy")
    M["t_frame"] = kit.plastic("#ece6d8", 0.6, name="door frame")
    M["t_step"] = kit.plastic("#a39b8e", 0.9, name="door step")
    M["t_glass"] = kit.plastic("#34495e", 0.2, name="window glass")
    M["t_green"] = kit.plastic("#3f7d47", 0.65, name="shelter green")
    M["t_iron"] = kit.plastic("#26292d", 0.5, name="lamp iron")
    M["t_brass"] = kit.plastic("#c59a3a", 0.3, name="brass", spec=0.8)
    M["t_wood"] = kit.plastic("#7a5636", 0.7, name="bench wood")
    kit.set_fog("#4a3940", 0.016, 6.0)
    M["d_brick"] = kit.bricks("#a15a42", "#80452f", mortar="#d9c9ae", scale=1.0, name="door brick", grime_amt=0.45)
    M["d_cobble"] = kit.cobbles("#4a4845", "#7b766d", "#252424", scale=2.2, wet=0.2, name="dusk cobbles")
    M["d_green"] = kit.plastic("#2f6a4a", 0.5, name="stage door green")
    M["d_lintel"] = kit.plastic("#5b5148", 0.9, name="lintel")
    kit.FOG.update(old)


# ------------------------------------------------------------------------------------------------ the street


def build_street(kit, ctx, M):
    B = kit.box
    B("street", (36, 22, 0.2), (TX, -6.0, -0.1), M["t_cobble"])
    B("pavement", (36, 4.2, 0.02), (TX, 2.4, 0.011), M["t_pave"])
    B("terrace wall", (36, 0.5, 7.0), (TX, 4.75, 3.5), M["t_brick"])
    B("terrace eaves", (36, 0.6, 0.3), (TX, 4.5, 7.05), M["t_step"])
    # windows, two floors, with a white frame standing 1 cm proud of the glass
    for k, x in enumerate((-10.5, -3.4, 5.0, 11.2)):
        for z in (1.5, 4.2) if k not in (1,) else (4.2,):
            B(f"win frame {k} {z}", (1.1, 0.06, 1.5), (TX + x, 4.47, z), M["t_frame"])
            B(f"win glass {k} {z}", (0.9, 0.04, 1.3), (TX + x, 4.435, z), M["t_glass"])
    # three painted doors; the cherry one is number nine
    doors = {"teal": (-6.5, M["t_teal"]), "navy": (1.6, M["t_navy"]), "cherry": (7.5, M["t_cherry"])}
    for nm, (x, mat) in doors.items():
        B(f"frame {nm}", (1.4, 0.06, 2.45), (TX + x, 4.47, 1.22), M["t_frame"])
        B(f"door {nm}", (1.1, 0.08, 2.2), (TX + x, 4.42, 1.1), mat)
        B(f"knob {nm}", (0.09, 0.05, 0.09), (TX + x + 0.38, 4.365, 1.05), M["t_brass"])
        B(f"step {nm}", (1.7 if nm != "cherry" else 2.6, 0.8, 0.18), (TX + x, 4.0, 0.09), M["t_step"])
    nx, nz, th = TX + 7.5, 1.75, 0.07
    segs = [("top", (0.34, 0.03, th), (0, 0.27)), ("tl", (th, 0.03, 0.28), (-0.135, 0.135)),
            ("tr", (th, 0.03, 0.28), (0.135, 0.135)), ("mid", (0.34, 0.03, th), (0, 0.0)),
            ("br", (th, 0.03, 0.28), (0.135, -0.135)), ("bot", (0.34, 0.03, th), (0, -0.27))]
    for nm, size, (dx, dz) in segs:
        B(f"nine {nm}", size, (nx + dx, 4.385, nz + dz), M["t_brass"])
    # the green wooden bus shelter (no text): roof, four posts, a bench, a low back board by the bench
    B("shelter roof", (4.0, 1.7, 0.12), (TX + 1.4, 2.55, 2.72), M["t_green"])
    B("shelter fascia", (4.04, 0.08, 0.3), (TX + 1.4, 1.72, 2.62), M["t_green"])
    for sx in (-0.5, 3.3):
        for sy in (1.8, 3.2):
            B(f"shelter post {sx} {sy}", (0.12, 0.12, 2.7), (TX + sx, sy, 1.35), M["t_green"])
    B("shelter bench", (1.3, 0.45, 0.08), (TX + 2.65, 3.0, 0.46), M["t_wood"])
    B("shelter bench back", (1.3, 0.05, 0.4), (TX + 2.65, 3.22, 0.78), M["t_green"])
    # the iron lamp post
    gx, gy = TX + 1.35, 3.52      # behind the bus-stop man in S01, so the street shows through his chest
    kit.cyl("lamp post", 0.06, 4.0, (gx, gy, 2.0), M["t_iron"], n=12)
    kit.cyl("lamp post base", 0.14, 0.5, (gx, gy, 0.25), M["t_iron"], n=12, r2=0.09)
    B("lamp head", (0.36, 0.36, 0.5), (gx, gy, 4.25), M["t_iron"], bevel=0.03)
    B("lamp cap", (0.5, 0.5, 0.08), (gx, gy, 4.55), M["t_iron"])
    B("lamp glass", (0.28, 0.28, 0.4), (gx, gy, 4.25), kit.plastic("#d8d2b8", 0.2, name="lamp glass"))


def build_door(kit, ctx, M):
    B = kit.box
    B("sd ground", (30, 20, 0.2), (SDX, -6.0, -0.1), M["d_cobble"])
    B("sd wall", (24, 0.5, 7.0), (SDX, 3.45, 3.5), M["d_brick"])
    B("sd lintel", (1.7, 0.2, 0.2), (SDX, 3.12, 2.4), M["d_lintel"])
    B("sd frame", (1.5, 0.05, 2.35), (SDX, 3.17, 1.17), M["d_lintel"])
    B("sd door", (1.2, 0.08, 2.2), (SDX, 3.12, 1.1), M["d_green"])
    B("sd handle", (0.1, 0.06, 0.18), (SDX + 0.45, 3.06, 1.05), M["t_brass"])
    B("sd step", (1.9, 0.8, 0.16), (SDX, 2.75, 0.08), M["d_lintel"])
    gx, gy, gz = SDX + 1.6, 3.0, 2.35
    B("sd lamp arm", (0.05, 0.3, 0.05), (gx, gy + 0.1, gz), M["t_iron"])
    B("sd lamp glass", (0.2, 0.2, 0.26), (gx, gy - 0.1, gz), M["bulb"])
    B("sd lamp cap", (0.28, 0.28, 0.05), (gx, gy - 0.1, gz + 0.16), M["t_iron"])


# ------------------------------------------------------------------------------------------------ the playhouse


def build_stage(kit, ctx, M):
    kit.box("stage floor", (18, 7.4, 0.2), (0, 3.7, -0.1), M["wood"])
    kit.box("stage lip", (18, 0.06, 0.8), (0, -0.03, -0.4), M["black"])
    kit.box("pit floor", (18, 2.5, 0.2), (0, -1.35, -0.75), M["carpet"])
    kit.box("back wall", (18, 0.3, 9.0), (0, 7.35, 4.5), M["brick"])
    for sx in (-1, 1):
        kit.box(f"side wall {sx}", (0.3, 7.6, 9.0), (sx * 9.0, 3.6, 4.5), M["brick"])
    for sx in (-1, 1):
        kit.box(f"pros col {sx}", (1.0, 0.6, 5.9), (sx * 4.7, -0.2, 2.25), M["black"])
        kit.box(f"pros trim {sx}", (0.07, 0.64, 4.6), (sx * 4.18, -0.2, 2.3), M["gilt_dull"])
        kit.box(f"pros foot {sx}", (1.04, 0.64, 0.12), (sx * 4.7, -0.2, -0.3), M["gilt_dull"])
    kit.box("pros beam", (10.4, 0.6, 1.3), (0, -0.2, 5.25), M["black"])
    kit.box("pros trim top", (8.5, 0.64, 0.07), (0, -0.2, 4.58), M["gilt_dull"])
    for k in range(9):
        kit.box(f"pros tile {k}", (0.5, 0.64, 0.14), (-3.6 + 0.9 * k, -0.2, 5.0), M["gilt_dull"], bevel=0.02)
    legy = ctx["places"]["legy"]
    for sx in (-1, 1):
        for k, y in enumerate(legy):
            x0, x1 = (3.7, 5.3) if sx > 0 else (-5.3, -3.7)
            pleated(kit, f"leg {sx} {k}", x0, x1, y, 0.04, 4.6, M["velvet"])
    for k, (x, y) in enumerate(ctx["places"]["marks"]):
        m = M["tape_y"] if k == 5 else M["tape_w"]
        rot = (0, 0, math.radians(((k * 37) % 11) - 5))
        kit.box(f"mark a {k}", (0.5, 0.07, 0.008), (x, y, 0.004), m, rot=rot)
        kit.box(f"mark b {k}", (0.07, 0.5, 0.008), (x, y, 0.004), m, rot=rot)
    kit.box("king mark", (0.45, 0.07, 0.008), (0.0, ctx["places"]["king"][1], 0.004), M["tape_w"])
    for k, x in enumerate((-0.05, 0.9)):
        kit.cyl(f"cup {k}", 0.04, 0.1, (x, 0.18, 0.05), M["paper"], n=14, r2=0.03)
    gx, gy = ctx["places"]["ghost"]
    kit.cyl("ghost base", 0.22, 0.04, (gx, gy, 0.02), M["steel"])
    kit.cyl("ghost pole", 0.022, 1.7, (gx, gy, 0.87), M["steel"], n=10)
    kit.sphere("ghost bulb", 0.075, (gx, gy, 1.78), M["bulb"], seg=10)
    for k in range(4):
        a = k * math.pi / 2
        kit.box(f"ghost cage {k}", (0.012, 0.012, 0.3), (gx + 0.12 * math.cos(a), gy + 0.12 * math.sin(a), 1.78), M["steel"])
    kit.cyl("ghost cap", 0.13, 0.02, (gx, gy, 1.94), M["steel"], n=14)
    # the tall wooden throne (shown for Thursday): a high back, arms, a gilt crest
    root = kit.empty("throne", (THRONE[0], THRONE[1], 0))
    kit.box("throne seat", (0.7, 0.62, 0.08), (0, 0, 0.47), M["wood_dark"], root, bevel=0.015)
    kit.box("throne back", (0.74, 0.1, 1.9), (0, 0.34, 1.0), M["wood_dark"], root, bevel=0.02)
    kit.box("throne crest", (0.94, 0.12, 0.2), (0, 0.34, 2.02), M["robe_trim"], root, bevel=0.03)
    for sx in (-1, 1):
        kit.box(f"throne arm {sx}", (0.1, 0.6, 0.08), (sx * 0.39, 0.0, 0.78), M["wood_dark"], root, bevel=0.015)
        kit.box(f"throne arm post {sx}", (0.1, 0.1, 0.4), (sx * 0.39, -0.22, 0.62), M["wood_dark"], root)
        for sy in (-1, 1):
            kit.box(f"throne leg {sx} {sy}", (0.08, 0.08, 0.45), (sx * 0.3, sy * 0.25, 0.225), M["wood_dark"], root)
    root.hide_render = True
    ctx["throne"] = root


def build_house(kit, ctx, M):
    xs = seat_xs()
    for r in range(ROWS):
        y, z = row_y(r), row_z(r)
        kit.box(f"row {r}", (10.0, ROW_DY + 0.02, z + 1.1), (0, y, (z - 1.1) / 2 + 0.0), M["carpet"])
        for x in xs:
            kit.box(f"seat {r} {x}", (0.5, 0.5, 0.1), (x, y, z + 0.42), M["seat"], bevel=0.03)
            kit.box(f"back {r} {x}", (0.5, 0.1, 0.62), (x, y - 0.27, z + 0.78), M["seat"], bevel=0.04)
            kit.box(f"rest {r} {x}", (0.1, 0.42, 0.06), (x + 0.3, y, z + 0.6), M["black"])
    aud = []
    for r in range(1, ROWS):
        for i, x in enumerate(xs):
            if kit.hash01(r, i, 5) < 0.12 or (r == 2 and abs(x + 0.58) < 0.1) or (r == 1 and abs(x) < 0.7 and abs(x - 0.58) > 0.1):
                continue
            h = 0.02 * kit.hash01(r, i, 9)
            hd = kit.sphere(f"aud head {r} {i}", 0.12, (x, row_y(r) - 0.12, row_z(r) + 1.4 + h), M["head_dark"], seg=8)
            bd = kit.box(f"aud body {r} {i}", (0.48, 0.26, 0.5), (x, row_y(r) - 0.12, row_z(r) + 1.1), M["body_dark"], bevel=0.05)
            aud += [hd, bd]
            hd.hide_render = bd.hide_render = True
    ctx["aud"] = aud


# ------------------------------------------------------------------------------------------------ the light

WASH_NAMES = ("wash_l", "wash_r", "wash_top", "wash_back")
_WARM = {"wash_l": 1.0, "wash_r": 1.0, "wash_top": 1.0, "wash_back": 1.0, "run1": 1.0, "run2": 0.5, "run3": 1.0,
         "ghost": 0.4, "marion_lamp": 1.0, "wing_fill": 1.0}
MOODS = {
    # the town in the sun, the stage door at dusk
    "sun": {"gains": {"sun": 1.0, "town_fill": 1.0, "town_fill2": 1.0}, "wash": "#ffb868", "exp": 0.0},
    "dusk": {"gains": {"door_lamp": 1.0, "door_fill": 1.0, "door_rim": 1.0}, "wash": "#ffb868", "exp": 0.0},
    # the ghost light is the key, the wash at about 6%; the faded ones are lit by their own little lights
    "ghost": {"gains": {"wash_l": 0.06, "wash_r": 0.06, "wash_top": 0.06, "wash_back": 0.2, "ghost": 1.0,
                        "ghost_fill": 0.5, "run1": 0.7, "run2": 0.4, "run3": 0.7, "wing_fill": 0.4, "fkey": 0.5,
                        "frim": 0.8, "mkey": 1.0, "marion_lamp": 0.4},
              "wash": "#ffb868", "exp": 0.9},
    "work": {"gains": {"work_l": 1.0, "work_r": 1.0, "work_house": 1.0, "run1": 0.12, "run3": 0.12, "ghost": 0.2},
             "wash": "#ffb868", "exp": 0.0},
    "warm": {"gains": dict(_WARM), "wash": "#ffb868", "exp": 0.0},
    "open": {"gains": {"wash_l": 1.0, "wash_r": 1.0, "wash_top": 1.0, "wash_back": 1.0, "run1": 1.8, "run2": 1.6,
                       "run3": 1.8, "ghost": 0.3, "aud": 1.0, "aud_back": 1.0, "wing_fill": 2.0, "wing_fill2": 4.0},
             "wash": "#ffb868", "exp": 0.0},
}


def build_lights(kit, ctx):
    gx, gy = ctx["places"]["ghost"]
    lamp(kit, "ghost", "POINT", (gx, gy, 1.78), 700.0, "#ffd7a0", size=0.08)
    lamp(kit, "ghost_fill", "AREA", (3.3, -1.6, 2.2), 160.0, "#ffd0a0", aim=(3.4, 2.8, 1.2), size=1.6)
    lamp(kit, "wash_l", "SPOT", (-3.5, -4.0, 5.4), 2600.0, "#ffb868", aim=(-0.5, 2.3, 1.0), spot=44, blend=0.5, size=0.3)
    lamp(kit, "wash_r", "SPOT", (3.5, -4.0, 5.4), 2600.0, "#ffb868", aim=(1.0, 2.3, 1.0), spot=44, blend=0.5, size=0.3)
    lamp(kit, "wash_top", "AREA", (0, 2.4, 5.6), 900.0, "#ffb868", aim=(0, 2.4, 0), size=5.0)
    lamp(kit, "wash_back", "AREA", (0, 6.3, 3.2), 500.0, "#ff9a58", aim=(0, 7.2, 1.2), size=3.0)
    lamp(kit, "work_l", "AREA", (-2.5, 2.5, 5.4), 1500.0, "#d9e5ff", aim=(-0.5, 2.5, 0), size=4.0)
    lamp(kit, "work_r", "AREA", (2.5, 2.5, 5.4), 1500.0, "#d9e5ff", aim=(1.0, 2.5, 0), size=4.0)
    lamp(kit, "work_house", "AREA", (0, -4.2, 3.9), 900.0, "#cfdcff", aim=(0, -5.5, 0), size=6.0)
    lamp(kit, "run1", "POINT", (4.6, 3.75, 0.45), 90.0, "#3f66ff", size=0.1)
    lamp(kit, "run2", "POINT", (5.3, 6.3, 0.9), 14.0, "#6d86d8", size=0.1)
    lamp(kit, "run3", "POINT", (4.5, 2.6, 0.4), 70.0, "#3f66ff", size=0.1)
    lamp(kit, "wing_fill", "POINT", (4.3, 2.2, 2.8), 110.0, "#8da0e0", size=0.2)
    lamp(kit, "wing_fill2", "POINT", (4.2, 4.8, 2.4), 90.0, "#8da0e0", size=0.2)
    lamp(kit, "marion_lamp", "SPOT", (0.2, -3.0, 2.0), 600.0, "#ffc890", aim=(-0.58, -4.5, 0.95), spot=40, blend=0.5, size=0.15)
    lamp(kit, "aud_back", "AREA", (0, -12.5, 4.6), 900.0, "#6d82b4", aim=(0, -6.0, 0.6), size=8.0)
    lamp(kit, "aud", "AREA", (0, -2.0, 4.2), 1300.0, "#6d82b4", aim=(0, -8.0, 0.4), size=8.0)
    # the faded ones' own lights (linked to them in animate): a warm key low from the ghost light's side, a thin cool
    # rim from the wings; and one for my face
    lamp(kit, "fkey", "AREA", (1.6, -0.9, 1.5), 190.0, "#ffc27a", aim=(0.0, 2.6, 1.3), size=1.2)
    lamp(kit, "frim", "AREA", (4.0, 4.2, 2.6), 500.0, "#8fb2ff", aim=(0.0, 2.4, 1.2), size=1.0)
    lamp(kit, "mkey", "AREA", (1.0, -1.2, 1.9), 110.0, "#ffd8a8", aim=(2.3, 2.9, 1.5), size=1.0)
    # the sun, the street fill, the stage door's lamp
    sun = kit.light("sun", "SUN", (TX - 8, -12, 14), 8.0, "#ffe2b0")
    sun.data.angle = math.radians(2.5)
    kit.aim(sun, (TX, 2, 0))
    lamp(kit, "town_fill", "AREA", (TX + 1, -9.0, 5.0), 2200.0, "#cfe0ff", aim=(TX + 1, 2.0, 1.0), size=9.0)
    lamp(kit, "town_fill2", "AREA", (TX - 6, -6.0, 3.5), 900.0, "#fff0d8", aim=(TX + 2, 2.0, 1.2), size=5.0)
    lamp(kit, "door_lamp", "POINT", (SDX + 1.6, 2.7, 2.35), 700.0, "#ffb866", size=0.15)
    lamp(kit, "door_fill", "AREA", (SDX + 1.0, -5.5, 4.0), 900.0, "#9fb0e6", aim=(SDX, 1.5, 1.2), size=7.0)
    lamp(kit, "door_rim", "AREA", (SDX - 3.0, 0.5, 3.0), 400.0, "#ffcf9a", aim=(SDX, 1.5, 1.2), size=2.0)


def _mood_state(tl, t):
    cs = [c for c in _cues(tl, "mood") if c["t"] <= t + 1e-9]
    cur = cs[-1]["set"] if cs else "ghost"
    prev = cs[-2]["set"] if len(cs) > 1 else cur
    u = 1.0
    if cs and float(cs[-1].get("dur", 0)) > 0:
        u = _ss((t - cs[-1]["t"]) / float(cs[-1]["dur"]))
    return MOODS[prev], MOODS[cur], u


def _hex(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))


# ------------------------------------------------------------------------------------------------ build


def build(kit, story, tl):
    ctx = {"story": story, "places": story["places"], "attached": False, "fades": {}, "linked": False}
    bpy.context.scene.cycles.transparent_max_bounces = 16
    M = materials(kit)
    town_materials(kit, M)
    ctx["M"] = M
    build_street(kit, ctx, M)
    build_door(kit, ctx, M)
    build_stage(kit, ctx, M)
    build_house(kit, ctx, M)
    build_lights(kit, ctx)
    return ctx


# ------------------------------------------------------------------------------------------------ props and costumes


def make_fade(kit, who, skip):
    """ep49's pattern: wrap every material's shader in a mix with a transparent shader, one value per material.
    Returns [(value node, is_head)]."""
    vals, seen = [], set()
    root = bpy.data.objects.get(who)
    if root is None:
        return vals
    for ob in [root] + list(root.children_recursive):
        if ob.type != "MESH" or ob in skip or "glint" in ob.name:
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
            vals.append((val, m.name.startswith("head ")))
    return vals


def attach_costumes(kit, ctx):
    M = ctx["M"]
    R, H = 0.62, 1.2
    wh = bpy.data.objects.get("walt.headg")
    if wh is None:
        return
    ctx["cost"] = {"walt": {}, "me": {}}
    W = ctx["cost"]["walt"]
    W["beard"] = [kit.box("walt beard", (0.95, 0.4, 0.34), (0, -R + 0.02, -0.5), M["white"], wh, bevel=0.1),
                  kit.box("walt mustache", (0.7, 0.14, 0.1), (0, -R - 0.02, -0.2), M["white"], wh, bevel=0.04)]
    crown = kit.empty("walt crown", (0, 0, H / 2 + 0.12), wh, rot=(0, 0.16, 0.05))
    kit.cyl("crown ring", R + 0.05, 0.22, (0, 0, 0), M["crown_tin"], crown, n=24)
    for k in range(7):
        a = 2 * math.pi * k / 7
        kit.box(f"crown spike {k}", (0.14, 0.08, 0.2), ((R + 0.02) * math.cos(a), (R + 0.02) * math.sin(a), 0.22),
                M["crown_tin"], crown, rot=(0, 0, a))
    W["crown"] = [crown]
    tor = bpy.data.objects["walt.torso"]
    robe = [kit.box("walt robe top", (2.18, 1.14, 2.14), (0, 0, 1.0), M["robe"], tor, bevel=0.12),
            kit.box("walt robe trim", (0.34, 1.16, 2.16), (0, -0.01, 1.0), M["robe_trim"], tor, bevel=0.05),
            kit.box("walt robe skirt", (2.3, 1.2, 1.9), (0, 0, -0.95), M["robe"], tor, bevel=0.14),
            kit.box("walt robe hem", (2.34, 1.24, 0.2), (0, 0, -1.8), M["robe_trim"], tor, bevel=0.05),
            kit.box("walt robe sash", (2.2, 1.18, 0.22), (0, 0, 0.1), M["robe_trim"], tor, bevel=0.05)]
    for sx in (-1, 1):
        arm = bpy.data.objects[f"walt.arm{sx}"]
        robe.append(kit.box(f"walt robe sleeve {sx}", (1.04, 1.06, 1.1), (0, 0, -0.3), M["robe"], arm, bevel=0.1))
    W["robe"] = robe
    mt = bpy.data.objects["me.torso"]
    mh = bpy.data.objects["me.headg"]
    C = ctx["cost"]["me"]
    C["cloak"] = [kit.box("me cloak back", (2.5, 0.34, 3.6), (0, 0.66, 0.2), M["cloak"], mt, bevel=0.1),
                  kit.box("me cloak cape", (2.4, 1.3, 0.7), (0, 0, 1.78), M["cloak"], mt, bevel=0.14),
                  kit.box("me cloak sideL", (0.3, 1.3, 2.4), (-1.05, 0.0, 0.85), M["cloak"], mt, bevel=0.08),
                  kit.box("me cloak sideR", (0.3, 1.3, 2.4), (1.05, 0.0, 0.85), M["cloak"], mt, bevel=0.08)]
    # my script roll: a plain cream rolled-up script, no text. Under my arm (in front of the torso, at the hip, never
    # gripped) or across my lap; both are children of the torso. The dropped one is a loose object (see animate).
    def roll(name, loc, rot, parent):
        r = kit.empty(name, loc, parent, rot=rot)
        kit.cyl(name + " body", 0.17, 1.6, (0, 0, 0), M["roll"], r, n=16)
        for e in (-1, 1):
            kit.cyl(f"{name} end {e}", 0.11, 0.03, (0, 0, e * 0.815), M["roll_end"], r, n=12)
        return r
    C["roll_arm"] = [roll("me roll arm", (1.0, -0.86, -0.1), (0.0, math.radians(18), 0.0), mt)]
    C["roll_lap"] = [roll("me roll lap", (0.25, -1.0, -1.3), (0.0, math.radians(90), math.radians(8)), mt)]
    drop = roll("script roll drop", (0, 0, -50), (0, 0, 0), None)
    drop.scale = (0.34, 0.34, 0.34)
    drop.hide_render = True
    ctx["drop"] = drop
    # Marion's glasses: the lenses out (they render black), full frames in
    for ob in list(bpy.data.objects):
        if ob.name in ("marion.gl-1", "marion.gl1", "marion.glf-1", "marion.glf1", "marion.glb"):
            ob.hide_render = True
    mah = bpy.data.objects.get("marion.headg")
    if mah is not None:
        for sx in (-1, 1):
            for nm, size, loc in (("t", (0.5, 0.03, 0.035), (sx * 0.24, -R - 0.05, 0.15)),
                                  ("b", (0.5, 0.03, 0.035), (sx * 0.24, -R - 0.05, -0.19)),
                                  ("s0", (0.035, 0.03, 0.36), (sx * 0.24 - 0.23, -R - 0.05, -0.02)),
                                  ("s1", (0.035, 0.03, 0.36), (sx * 0.24 + 0.23, -R - 0.05, -0.02))):
                kit.box(f"marion frame {nm}{sx}", size, loc, M["tin"], mah)
    # the new cast's props, always on (they hide with their wearer)
    def P(who):
        return {k: bpy.data.objects.get(f"{who}.{k}") for k in ("headg", "torso")}
    sm = P("stopman")
    if sm["headg"] is not None:     # a flat cap in olive
        cap = kit.plastic("#6b6b3a", 0.85, name="stopman cap")
        kit.box("stopman capc", (2 * R + 0.16, 2 * R + 0.1, 0.34), (0, -0.02, H / 2 + 0.0), cap, sm["headg"], bevel=0.12)
        kit.box("stopman capb", (1.0, 0.6, 0.06), (0, -R - 0.22, H / 2 - 0.12), cap, sm["headg"], bevel=0.02)
    mi = P("mime")
    if mi["headg"] is not None:     # a black beret, a little off to one side
        bm = kit.plastic("#0e0e12", 0.9, name="mime beret")
        kit.cyl("mime beret", R + 0.2, 0.2, (0.12, -0.02, H / 2 + 0.04), bm, mi["headg"], n=28, rot=(0.0, 0.14, 0.0))
        kit.cyl("mime beret stalk", 0.05, 0.1, (0.12, -0.02, H / 2 + 0.2), bm, mi["headg"], n=8)
    hb = P("husband9")
    if hb["torso"] is not None:     # braces
        bc = kit.plastic("#d9d2c0", 0.7, name="braces")
        for sx in (-1, 1):
            kit.box(f"husband9 brace {sx}", (0.14, 0.04, 2.0), (sx * 0.55, -0.52, 1.0), bc, hb["torso"])
    bu = P("busker")
    if bu["torso"] is not None:     # a box guitar on a strap
        gw = kit.plastic("#a8743c", 0.55, name="guitar wood")
        gd = kit.plastic("#1a120c", 0.8, name="guitar dark")
        g = kit.empty("busker guitar", (0.35, -0.75, 0.5), bu["torso"], rot=(0, math.radians(-28), 0))
        kit.box("guitar body", (1.5, 0.45, 1.6), (0, 0, 0.0), gw, g, bevel=0.1)
        kit.box("guitar hole", (0.6, 0.05, 0.6), (0, -0.25, 0.1), gd, g)
        kit.box("guitar neck", (0.3, 0.3, 1.9), (0, -0.05, 1.7), gd, g, bevel=0.04)
        kit.box("guitar strap", (0.14, 1.06, 0.1), (-0.2, 0.2, 1.05), gd, bu["torso"], rot=(0, math.radians(-30), 0))
    # the faded ones' eye glints: two small warm lights at the eyes, the brightest thing in the frame
    for who in FADED:
        hg = bpy.data.objects.get(f"{who}.headg")
        if hg is not None:
            for sx in (-1, 1):
                kit.sphere(f"{who} glint {sx}", 0.04, (sx * 0.19, -R - 0.005, 0.1), M["glint"], hg, seg=8)
    ctx["attached"] = True


def attach_fades(kit, ctx):
    skip = set()
    crown = bpy.data.objects.get("walt crown")
    if crown is not None:
        skip = {crown, *crown.children_recursive}
    for who in FADERS:
        ctx["fades"][who] = make_fade(kit, who, skip if who == "walt" else set())


def link_lights(kit, ctx):
    objs = []
    for who in FADED + ("walt", "stopman"):
        r = bpy.data.objects.get(who)
        if r is not None:
            objs += [o for o in [r] + list(r.children_recursive) if o.type == "MESH"]
    light_only(kit, "faded only", "fkey", objs)
    light_only(kit, "faded only", "frim", objs)
    me = bpy.data.objects.get("me")
    if me is not None:
        light_only(kit, "me only", "mkey", [o for o in [me] + list(me.children_recursive) if o.type == "MESH"])
    ctx["linked"] = True


def fade_value(tl, who, t):
    v = 1.0
    for c in sorted((c for c in _cues(tl, "fade") if c["who"] == who), key=lambda c: c["t"]):
        if c["t"] > t + 1e-9:
            break
        d = float(c.get("dur", 0))
        u = 1.0 if d <= 0 else _ss((t - c["t"]) / d)
        v = v + (c["a"] - v) * u
    return v


def head_value(tl, who, t, body):
    """The head's own alpha when a headfade cue sets one (a = -1 hands the head back to 1.3 x the body)."""
    prev = None
    for c in sorted((c for c in _cues(tl, "headfade") if c["who"] == who), key=lambda c: c["t"]):
        if c["t"] > t + 1e-9:
            break
        d = float(c.get("dur", 0))
        u = 1.0 if d <= 0 else _ss((t - c["t"]) / d)
        tgt = None if c["a"] < 0 else c["a"]
        if prev is None and tgt is None:
            continue
        base = prev if prev is not None else min(1.0, body * 1.3)
        goal = tgt if tgt is not None else min(1.0, body * 1.3)
        prev = base + (goal - base) * u if u < 1.0 else tgt
        if u >= 1.0 and tgt is None:
            prev = None
    return prev if prev is not None else min(1.0, body * 1.3)


def animate(kit, story, tl, t, ctx):
    if not ctx["attached"] and bpy.data.objects.get("walt.headg") is not None:
        attach_costumes(kit, ctx)
        attach_fades(kit, ctx)
        link_lights(kit, ctx)
    A = tl.get("acting", {})
    for who, keys in A.items():
        if _switch(keys, "sit", t, False):
            for sx in (-1, 1):
                leg = bpy.data.objects.get(f"{who}.leg{sx}")
                if leg is not None:
                    leg.rotation_euler = (math.radians(-90), 0, 0)
    for who, parts in ctx.get("cost", {}).items():
        c = _last([c for c in _cues(tl, "costume") if c.get("who") == who], t) or {}
        root = bpy.data.objects.get(who)
        shown = root is not None and not root.hide_render
        for name, objs in parts.items():
            on = bool(c.get(name, False)) and shown
            for o in objs:
                _show(o, on)
    # the dropped script roll: falls from under my arm, lands, then rolls to the yellow cross (a rigid tween)
    drop = ctx.get("drop")
    if drop is not None:
        rc = _last(_cues(tl, "roll"), t)
        on = bool(rc and rc.get("mode") == "drop")
        _show(drop, False)
        if on:
            u0 = t - rc["t"] - float(rc.get("t0", 0))
            if u0 >= 0:
                _show(drop, True)
                sx, sy, sz = rc["start"]
                lx, ly = rc["land"]
                tx, ty = rc["to"]
                fall = float(rc.get("fall", 0.5))
                dur = float(rc.get("dur", 2.4))
                r = 0.17 * 0.34
                if u0 < fall:
                    k = u0 / fall
                    pos = (sx + (lx - sx) * k, sy + (ly - sy) * k, sz + (r + 0.005 - sz) * k * k)
                    dist = 0.0
                else:
                    k = min(1.0, (u0 - fall) / dur)
                    e = 1 - (1 - k) ** 2
                    pos = (lx + (tx - lx) * e, ly + (ty - ly) * e, r + 0.005)
                    dist = math.hypot(tx - lx, ty - ly) * e
                drop.location = pos
                import mathutils
                d = mathutils.Vector((tx - lx, ty - ly, 0.0))
                d.normalize()
                ax = mathutils.Vector((-d.y, d.x, 0.0))
                q0 = mathutils.Vector((0, 0, 1)).rotation_difference(ax)
                q1 = mathutils.Quaternion(ax, -dist / (r + 0.005) if dist else 0.0)
                drop.rotation_mode = "QUATERNION"
                drop.rotation_quaternion = q1 @ q0
    # glints belong to the faded ones: they follow their wearer's hide (children of the head group, set by pose())
    tc = _last(_cues(tl, "throne"), t)
    _show(ctx["throne"], bool(tc and tc.get("on")))
    ac = _last(_cues(tl, "audience"), t)
    for o in ctx["aud"]:
        o.hide_render = not bool(ac and ac.get("on"))
    # the fades
    for who, vals in ctx["fades"].items():
        a = fade_value(tl, who, t)
        for val, is_head in vals:
            val.outputs[0].default_value = head_value(tl, who, t, a) if is_head else a
    # the faded ones' lights follow the shot: {"key": [x,y,z], "rim": [x,y,z], "aim": [x,y,z], "kg", "rg"}
    fl = _last(_cues(tl, "flight"), t) or {}
    kit.LIGHTS["fkey"]["obj"].location = tuple(fl.get("key", (1.6, -0.9, 1.5)))
    kit.LIGHTS["frim"]["obj"].location = tuple(fl.get("rim", (4.0, 4.2, 2.6)))
    kit.aim(kit.LIGHTS["fkey"]["obj"], tuple(fl.get("aim", (0.0, 2.6, 1.3))))
    kit.aim(kit.LIGHTS["frim"]["obj"], tuple(fl.get("aim", (0.0, 2.6, 1.3))))
    # the light: the mood, eased from the one before
    over = {}
    a, b, u = _mood_state(tl, t)
    for name in kit.LIGHTS:
        over[name] = a["gains"].get(name, 0.0) * (1 - u) + b["gains"].get(name, 0.0) * u
    over["fkey"] *= float(fl.get("kg", 1.0))
    over["frim"] *= float(fl.get("rg", 1.0))
    ca, cb = _hex(a["wash"]), _hex(b["wash"])
    wc = tuple(ca[i] + (cb[i] - ca[i]) * u for i in range(3))
    for nm in WASH_NAMES:
        kit.LIGHTS[nm]["light"].color = tuple(kit.srgb(v) for v in wc)
    bpy.context.scene.view_settings.exposure = a["exp"] * (1 - u) + b["exp"] * u
    return over
