"""ep103 "the hungry man": one long street of pastel porches, a hollow cream house (ours) with a hall inside, Grandpa's
gray-green house across the road, two small rooms (our kitchen, Grandpa's hall and kitchen), and the rule meter: a
round cream plate tag top-left in every frame with the count of plates out tonight (42/43, 41/43, 43/43).

Everything the story moves is driven by cues in story.json (see animate): the look (sun, fill, sky, porch lights),
the plates on every step, the tag's count, our front door, the knocker, the hall clock, the blinds, the snow, Mom's
car, and what is carried on Grandpa's / my arm (basket, dish, sandwich, plate). The tag is a child of the camera.
"""
import math
import sys
from pathlib import Path

import bpy
from mathutils import Vector

sys.path.insert(0, str(Path(__file__).resolve().parent))
import layout as G  # noqa: E402

D2R = math.pi / 180.0
W = {}


def ss(x):
    x = min(1.0, max(0.0, x))
    return x * x * (3 - 2 * x)


def kit_col(h):
    h = h.lstrip("#")
    f = lambda c: (c / 12.92) if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
    return tuple(f(int(h[i:i + 2], 16) / 255) for i in (0, 2, 4))


def _L(**kw):
    base = dict(sun=3.2, sun_col="#fff0d8", el=40.0, az=120.0, fill=0.9, fill_col="#fff0e0", sky="#9fd8ff", sky_str=1.0,
                front=0.4, porch=0.0, street=0.0)
    base.update(kw)
    return base


LOOKS = {
    "morning": _L(),
    "gold": _L(sun=3.0, sun_col="#ffbf80", el=13.0, az=140.0, fill=1.0, fill_col="#ffe2c8", sky="#ffcf9e", sky_str=0.95,
               front=0.9, porch=0.5),
    "night": _L(sun=1.1, sun_col="#8aa4ff", el=38.0, az=200.0, fill=0.6, fill_col="#7f93e0", sky="#2a3a78", sky_str=0.5,
                front=0.35, porch=1.0, street=1.0),
    "snow": _L(sun=2.4, sun_col="#f2f6ff", el=34.0, az=150.0, fill=1.35, fill_col="#dfeaff", sky="#d4e3f4", sky_str=1.0,
               front=0.5, porch=0.2),
}


def look_at(tl, t):
    cues = [c for c in tl["cues"] if c["name"] == "look"]
    cur = LOOKS[cues[0]["id"]] if cues else LOOKS["gold"]
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
                else:
                    out[k] = a + (b - a) * u
            return out
    return {k: (kit_col(v) if isinstance(v, str) else v) for k, v in cur.items()}


def sample(name, tl, t, defaults):
    cues = [c for c in tl["cues"] if c["name"] == name]
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


def _hide(ob, hide):
    ob.hide_render = hide
    for c in ob.children_recursive:
        c.hide_render = hide


def noshadow(ob):
    ob.visible_shadow = False
    for c in ob.children_recursive:
        c.visible_shadow = False


PASTELS = ["#fff07a", "#9ee6c4", "#ffb48a", "#c9b3f2", "#ffd0d8", "#bfe3ff"]
ROOFS = ["#c4624a", "#6b7fa8", "#8a5a3a", "#5f8f6a"]


# ---------------------------------------------------------------------------------------------- the plates
def make_plate_objs(kit, name, x, y, z, food=None):
    """Returns (covered_or_food, stack, forks): lists of objects, each hidden at will."""
    cream = kit.plastic("#fff6e4", 0.5, spec=0.3)
    foil = kit.metal("#dfe3e8", 0.28)
    p1, p2, p3 = [], [], []
    p1.append(kit.cyl(f"{name}.pl", 0.3, 0.04, (x, y, z + 0.02), cream, n=20))
    p1.append(kit.cyl(f"{name}.plr", 0.22, 0.05, (x, y, z + 0.025), kit.plastic("#f1e2c4", 0.5), n=20))
    if food == "lasagna":
        p1.append(kit.box(f"{name}.food", (0.62, 0.5, 0.1), (x, y, z + 0.08), kit.plastic("#e8693a", 0.6), bevel=0.02))
        p1.append(kit.box(f"{name}.food2", (0.62, 0.5, 0.04), (x, y, z + 0.15), kit.plastic("#ffe08a", 0.6), bevel=0.01))
        p1.append(kit.box(f"{name}.food3", (0.62, 0.5, 0.04), (x, y, z + 0.19), kit.plastic("#c93a2c", 0.6), bevel=0.01))
    elif food == "chicken":
        ch = kit.sphere(f"{name}.food", 0.2, (x, y, z + 0.2), kit.plastic("#c8782c", 0.5, spec=0.5), seg=12)
        ch.scale = (1.2, 0.9, 0.8)
        p1.append(ch)
        for sx in (-1, 1):
            p1.append(kit.cyl(f"{name}.leg{sx}", 0.04, 0.25, (x + sx * 0.18, y - 0.08, z + 0.13), kit.plastic("#a95f20", 0.5),
                              rot=(0, sx * 1.1, 0), n=8))
            p1.append(kit.sphere(f"{name}.knob{sx}", 0.06, (x + sx * 0.3, y - 0.08, z + 0.09), kit.plastic("#f6ecd8", 0.6), seg=8))
    elif food == "cereal":
        bowl = kit.cyl(f"{name}.food", 0.15, 0.09, (x - 0.08, y, z + 0.07), kit.plastic("#7fb8e8", 0.5, spec=0.3), n=16)
        p1.append(bowl)
        p1.append(kit.cyl(f"{name}.food2", 0.125, 0.02, (x - 0.08, y, z + 0.12), kit.plastic("#e0a850", 0.7), n=16))
        for i in range(7):
            ang = i * 0.9
            p1.append(kit.sphere(f"{name}.o{i}", 0.032, (x - 0.08 + 0.07 * math.cos(ang) * (0.4 + (i % 3) * 0.3),
                                                          y + 0.07 * math.sin(ang) * (0.4 + (i % 3) * 0.3), z + 0.135),
                                 kit.plastic("#f0c070", 0.6), seg=6))
        p1.append(kit.box(f"{name}.jug", (0.1, 0.08, 0.2), (x + 0.17, y, z + 0.15), kit.plastic("#fbfbff", 0.4, spec=0.4),
                          bevel=0.015))
        p1.append(kit.box(f"{name}.jugc", (0.06, 0.05, 0.05), (x + 0.17, y, z + 0.27), kit.plastic("#3a78d9", 0.4)))
        p1.append(kit.box(f"{name}.jugs", (0.1, 0.082, 0.05), (x + 0.17, y, z + 0.14), kit.plastic("#4f90e0", 0.4), bevel=0.01))
    else:
        dome = kit.sphere(f"{name}.foil", 0.29, (x, y, z + 0.05), foil, seg=14)
        dome.scale = (1.0, 1.0, 0.5)
        p1.append(dome)
    for i in range(3):
        p2.append(kit.cyl(f"{name}.st{i}", 0.3, 0.04, (x, y, z + 0.02 + i * 0.045), cream, n=20))
        p2.append(kit.cyl(f"{name}.str{i}", 0.22, 0.05, (x, y, z + 0.025 + i * 0.045), kit.plastic("#f1e2c4", 0.5), n=20))
    p3.append(kit.cyl(f"{name}.fpl", 0.3, 0.04, (x, y, z + 0.02), cream, n=20))
    p3.append(kit.cyl(f"{name}.fplr", 0.22, 0.05, (x, y, z + 0.025), kit.plastic("#f1e2c4", 0.5), n=20))
    p3.append(kit.box(f"{name}.food", (0.2, 0.16, 0.05), (x, y, z + 0.07), kit.plastic("#f0d8a0", 0.6), bevel=0.02))
    metal = kit.metal("#cfd3d8", 0.3)
    for sx in (-1, 1):
        p3.append(kit.box(f"{name}.fk{sx}", (0.03, 0.34, 0.025), (x + sx * 0.5, y - 0.1, z + 0.02), metal))
        p3.append(kit.box(f"{name}.fkh{sx}", (0.07, 0.1, 0.025), (x + sx * 0.5, y + 0.12, z + 0.02), metal))
    return p1, p2, p3


# ---------------------------------------------------------------------------------------------- a house
def house(kit, side, k):
    name = f"h{'n' if side > 0 else 's'}{k}"
    x = k * G.SPACING
    o = -side                              # toward the street
    ours = (side, k) == G.OURS
    gp = (side, k) == G.GRANDPA
    ci = (k * 3 + (1 if side > 0 else 4)) % len(PASTELS)
    col = "#fff6e4" if ours else ("#9fb8a6" if gp else PASTELS[ci])
    wall = kit.plastic(col, 0.7, spec=0.12)
    roofm = kit.plastic("#3f6aa0" if ours else ("#55705e" if gp else ROOFS[(k + 5) % 4]), 0.6, spec=0.15)
    trim = kit.plastic("#fffaf0", 0.6)
    glass = kit.plastic("#7fa8cc", 0.2, spec=0.8)
    fy = side * G.FRONT
    cy = side * 12.0
    doorc = "#3f78d9" if ours else ("#6e4f3a" if gp else ["#d9413b", "#2f8f7a", "#e0a030", "#7a54b8"][(k + 6) % 4])
    if ours:
        pass                                  # built by hollow_house
    else:
        kit.box(f"{name}.body", (7.0, 6.0, 4.2), (x, cy, 2.1), wall)
        for sx in (-1, 1):
            kit.box(f"{name}.win{sx}", (1.3, 0.1, 1.2), (x + sx * 2.3, fy + o * 0.04, 2.2), glass)
            kit.box(f"{name}.wf{sx}", (1.6, 0.08, 1.5), (x + sx * 2.3, fy + o * 0.02, 2.2), trim)
            if gp and sx == -1:
                kit.box(f"{name}.lace", (1.2, 0.04, 1.1), (x + sx * 2.3, fy + o * 0.1, 2.2), kit.plastic("#fffaf0", 0.9))
        kit.box(f"{name}.door", (1.2, 0.12, 2.3), (x, fy + o * 0.08, 0.3 + 1.15), kit.plastic(doorc, 0.5, spec=0.3))
        kit.sphere(f"{name}.knob", 0.06, (x + 0.4, fy + o * 0.18, 1.3), kit.plastic("#e3b04b", 0.3, spec=0.6), seg=8)
    kit.box(f"{name}.roof", (7.8, 6.8, 0.4), (x, cy, 4.4), roofm)
    kit.box(f"{name}.roof2", (5.4, 4.6, 0.5), (x, cy, 4.8), roofm)
    kit.box(f"{name}.deck", (4.6, G.DECK_OUT, 0.3), (x, fy + o * G.DECK_OUT / 2, 0.15), kit.plastic("#d8b890", 0.8))
    kit.box(f"{name}.step", (1.8, 0.7, 0.15), (x, fy + o * (G.DECK_OUT + 0.35), 0.075), kit.plastic("#cbb08c", 0.8))
    kit.box(f"{name}.proof", (4.8, 2.0, 0.15), (x, fy + o * 1.0, 3.0), trim)
    for sx in (-1, 1):
        kit.cyl(f"{name}.post{sx}", 0.08, 2.7, (x + sx * 2.2, fy + o * (G.DECK_OUT - 0.1), 0.3 + 1.35), trim, n=8)
    kit.box(f"{name}.lamp", (0.2, 0.1, 0.3), (x + 1.0, fy + o * 0.1, 2.5), kit.plastic("#3a3a40", 0.5))
    kit.sphere(f"{name}.bulb", 0.13, (x + 1.0, fy + o * 0.24, 2.45), kit.emit("#ffcf73", 7.0, "bulb"), seg=8)
    px_, py_, pz_ = x + G.PLATE_DX, side * (G.FRONT - G.DECK_OUT + 0.65), G.DECK_Z
    food = None
    if (side, k) == G.FERRO:
        food = "lasagna"
    elif (side, k) == G.ABERN:
        food = "chicken"
    elif (side, k) == G.BRISCO:
        food = "cereal"
    if gp:
        px_ = x + 0.0
        py_ = side * 7.35
    return name, make_plate_objs(kit, name, px_, py_, pz_, food)


def streetlight(kit, x, y, dark, bulb):
    kit.cyl(f"sl{x}_{y}.pole", 0.07, 4.2, (x, y, 2.1), dark, n=8)
    kit.box(f"sl{x}_{y}.arm", (0.6, 0.1, 0.1), (x, y + (0.25 if y < 0 else -0.25), 4.25), dark)
    kit.sphere(f"sl{x}_{y}.bulb", 0.2, (x, y + (0.5 if y < 0 else -0.5), 4.15), bulb, seg=8)


# ---------------------------------------------------------------------------------------------- our hollow house
def hollow_house(kit):
    plastic_ = kit.plastic
    x, side = 0.0, 1
    o = -1
    wall = kit.plastic("#fff0d8", 0.7, spec=0.12)
    inner = kit.plastic("#ffe6c4", 0.8, spec=0.05)
    trim = kit.plastic("#fffaf0", 0.6)
    fy = 9.0
    T = 0.3
    yw = fy + T / 2                      # centre of the front wall
    H = 4.2
    # front wall: left of window, between window and door, right of door; above and below the window; above the door
    def fw(nm, x0, x1, z0, z1):
        kit.box(f"hn0.fw_{nm}", (x1 - x0, T, z1 - z0), ((x0 + x1) / 2, yw, (z0 + z1) / 2), wall)
    fw("a", -3.5, -2.95, 0.0, H)
    fw("b", -1.65, -0.6, 0.0, H)
    fw("c", 0.6, 3.5, 0.0, H)
    fw("sill", -2.95, -1.65, 0.0, 1.2)
    fw("head", -2.95, -1.65, 2.4, H)
    fw("lint", -0.6, 0.6, 2.6, H)
    kit.box("hn0.frame_s", (1.5, 0.12, 0.08), (-2.3, 8.97, 1.22), trim)
    kit.box("hn0.frame_h", (1.5, 0.12, 0.08), (-2.3, 8.97, 2.38), trim)
    for sx in (-1, 1):
        kit.box(f"hn0.frame{sx}", (0.08, 0.12, 1.2), (-2.3 + sx * 0.69, 8.97, 1.8), trim)
    # sides, back, floor, ceiling
    for sx in (-1, 1):
        kit.box(f"hn0.side{sx}", (T, 6.0, H), (sx * 3.35, 12.0, H / 2), wall)
    kit.box("hn0.back", (7.0, T, H), (0, 14.85, H / 2), wall)
    kit.box("hn0.floor", (6.8, 5.7, 0.08), (0, 12.0, 0.26), kit.plastic("#c9976a", 0.8))
    kit.box("hn0.ceil", (7.0, 6.0, 0.2), (0, 12.0, 3.5), inner)
    # inner skin faces (so the room is a calm cream)
    kit.box("hn0.rugr", (3.0, 2.2, 0.03), (0.6, 12.3, 0.32), kit.plastic("#d9413b", 0.9))
    # the window's blinds, inside (slats), with a slit and a plug for the slit
    bl = kit.plastic("#f2ead8", 0.7)
    W["blind_slit"] = []
    for i in range(10):
        z = 1.25 + i * 0.115
        ob = kit.box(f"hn0.slat{i}", (1.4, 0.03, 0.09), (-2.3, 9.4, z), bl)
        if i in (0, 1, 2, 3, 4, 5):
            W["blind_slit"].append(ob)
    W["slit_lit"] = []
    # the door (inward)
    hx, hy = G.FRONT_DOOR_HINGE
    door = kit.empty("hn0.door", (hx, hy, 0.3))
    W["door"] = door
    kit.box("hn0.door.leaf", (1.2, 0.1, 2.3), (0.6, 0, 1.2), kit.plastic("#3f78d9", 0.5, spec=0.3), door)
    kit.box("hn0.door.pane", (0.4, 0.115, 0.4), (0.6, 0, 1.95), kit.plastic("#cfe8ff", 0.2, spec=0.7), door)
    kit.sphere("hn0.door.knob", 0.06, (1.05, 0.12, 1.1), kit.plastic("#e3b04b", 0.3, spec=0.6), door, seg=8)
    kn = kit.empty("hn0.knocker", (0.6, -0.075, 1.5), door)
    W["knocker"] = kn
    brass = kit.plastic("#f0b93a", 0.25, spec=0.8)
    kit.cyl("hn0.kn.mount", 0.13, 0.03, (0, 0.0, 0.0), brass, kn, rot=(math.pi / 2, 0, 0), n=16)
    kit.sphere("hn0.kn.stud", 0.05, (0, -0.03, 0.0), brass, kn, seg=8)
    for i in range(12):                      # a round brass ring hanging from the stud
        a = i * 30 * D2R
        kit.box(f"hn0.kn.r{i}", (0.075, 0.06, 0.075), (math.sin(a) * 0.15, -0.045, -0.2 + math.cos(a) * 0.15), brass, kn,
                rot=(0, -a, 0))
    kit.box("hn0.kn.strike", (0.2, 0.05, 0.06), (0, -0.05, -0.44), brass, kn)
    # the long shadow of a tall man standing in the street, on our boards (1.2 cm proud of the deck)
    shm = kit.plastic("#7a4f2e", 0.95, spec=0.0)
    W["shade"] = []
    zs = 0.3 + 0.012
    for nm, sx, y0, y1, w in (("l0", -0.2, 7.2, 8.1, 0.17), ("l1", 0.2, 7.2, 8.1, 0.17), ("hip", 0.0, 8.1, 8.45, 0.62),
                              ("sh", 0.0, 8.45, 8.78, 0.95), ("arm0", -0.62, 8.2, 8.74, 0.2), ("arm1", 0.62, 8.2, 8.74, 0.2),
                              ("hd", 0.0, 8.8, 8.98, 0.4)):
        W["shade"].append(kit.box(f"hn0.shade.{nm}", (w, y1 - y0, 0.004), (0.3 + sx, (y0 + y1) / 2, zs), shm))
    # furniture: couch, TV, clock, side window, table, lamp
    cou = kit.plastic("#5f8fb8", 0.8)
    kit.box("hn0.couch.seat", (2.6, 1.0, 0.5), (1.6, 13.6, 0.55), cou, bevel=0.05)
    kit.box("hn0.couch.back", (2.6, 0.3, 0.9), (1.6, 14.2, 0.95), cou, bevel=0.05)
    for sx in (-1, 1):
        kit.box(f"hn0.couch.arm{sx}", (0.3, 1.0, 0.75), (1.6 + sx * 1.3, 13.6, 0.65), cou, bevel=0.05)
    kit.box("hn0.tv", (1.5, 0.12, 0.9), (2.25, 9.5, 1.3), kit.plastic("#2a2a30", 0.4))
    W["tvscreen"] = kit.box("hn0.tv.scr", (1.35, 0.03, 0.75), (2.25, 9.575, 1.3), kit.emit("#7fb0ff", 2.2, "tvscr"))
    kit.box("hn0.tvstand", (1.7, 0.5, 0.5), (2.25, 9.7, 0.55), kit.plastic("#8a5a3a", 0.7))
    W["tv_light"] = kit.light("tv", "POINT", (2.2, 10.6, 1.2), 90.0, "#7fb0ff", size=0.4, shadow=False)
    # hall clock on the left wall
    kit.cyl("hn0.clock.face", 0.4, 0.05, (-3.17, 11.6, 2.4), kit.plastic("#fffaf0", 0.5), rot=(0, math.pi / 2, 0), n=24)
    kit.cyl("hn0.clock.rim", 0.45, 0.04, (-3.185, 11.6, 2.4), brass, rot=(0, math.pi / 2, 0), n=24)
    inkm = kit.plastic("#2a2a30", 0.6)
    for i in range(12):
        a = i * 30 * D2R
        kit.box(f"hn0.clock.t{i}", (0.02, 0.04, 0.09), (-3.14, 11.6 + math.sin(a) * 0.32, 2.4 + math.cos(a) * 0.32), inkm,
                rot=(a, 0, 0))
    W["hand_h"] = kit.empty("hn0.clock.hh", (-3.12, 11.6, 2.4))
    kit.box("hn0.clock.hh.b", (0.015, 0.035, 0.22), (0, 0, 0.11), inkm, W["hand_h"])
    W["hand_m"] = kit.empty("hn0.clock.mh", (-3.11, 11.6, 2.4))
    kit.box("hn0.clock.mh.b", (0.012, 0.025, 0.3), (0, 0, 0.15), inkm, W["hand_m"])
    # the side window (my bedroom window) on the right wall
    kit.box("hn0.sw.frame", (0.12, 1.5, 1.5), (3.18, 12.0, 1.8), trim)
    kit.box("hn0.sw.pane", (0.06, 1.3, 1.3), (3.15, 12.0, 1.8), kit.emit("#6f8fd8", 1.6, "swpane"))
    for i in range(8):
        kit.box(f"hn0.sw.slat{i}", (0.03, 1.3, 0.08), (3.1, 12.0, 1.2 + i * 0.16), bl)
    kit.box("hn0.blanket", (1.8, 0.6, 0.12), (1.6, 12.85, 0.74), plastic_("#c8504a"), rot=(0, 0, 0.05), bevel=0.06)
    kit.box("hn0.table", (0.9, 0.5, 0.7), (-2.4, 14.3, 0.65), kit.plastic("#8a5a3a", 0.7))
    kit.box("hn0.lampb", (0.2, 0.2, 0.3), (-2.4, 14.3, 1.15), kit.plastic("#f6ecd8", 0.6))
    kit.sphere("hn0.lampshade", 0.25, (-2.4, 14.3, 1.45), kit.emit("#ffd9a0", 1.6, "lampsh"), seg=10)
    kit.light("inroom", "POINT", (0.0, 12.0, 2.9), 300.0, "#ffe2b8", size=0.6, shadow=False)
    kit.light("inroom2", "POINT", (-2.4, 14.0, 1.6), 120.0, "#ffcf90", size=0.4, shadow=False)
    W["hn0"] = True


def room(kit, cx, cy, wallc, floorc, name):
    wall = kit.plastic(wallc, 0.85, spec=0.05)
    kit.plane(f"{name}.floor", (9, 8), (cx, cy, 0.03), kit.planks(floorc, "#b78456", 1.0))
    kit.box(f"{name}.back", (9, 0.3, 3.2), (cx, cy + 3.7, 1.6), wall)
    kit.box(f"{name}.front", (9, 0.3, 3.2), (cx, cy - 3.9, 1.6), wall)
    for sx in (-1, 1):
        kit.box(f"{name}.side{sx}", (0.3, 8, 3.2), (cx + sx * 4.4, cy, 1.6), wall)
    kit.box(f"{name}.ceil", (9, 8, 0.2), (cx, cy, 3.3), wall)
    kit.box(f"{name}.base", (9, 0.1, 0.15), (cx, cy + 3.53, 0.08), kit.plastic("#fffaf0", 0.7))


# ---------------------------------------------------------------------------------------------- the build
def build(kit, story, tl):
    tl["cues"].sort(key=lambda c: c["t"])
    plastic = kit.plastic
    ground = kit.grime("#a5d08f", 0.88, 1.2, "ground", 0.95)
    road = plastic("#8d93a3", 0.85, spec=0.05)
    walk = plastic("#ece0cc", 0.9, spec=0.05)
    dark = plastic("#3a3a44", 0.6)

    sun = kit.light("sun", "SUN", (0, -30, 40), 1.0, "#fff0d8", size=0.06)
    sun.data.angle = 0.06
    fill = kit.light("fill", "SUN", (0, -30, 30), 1.0, "#cfe6ff", shadow=False)
    fill.data.angle = 0.5
    kit.aim(fill, (0, 0, 0))
    front = kit.light("front", "SUN", (-10, -30, 20), 1.0, "#ffd2ae", shadow=False)
    front.data.angle = 0.4
    kit.aim(front, (0, 0, 0))
    # warm porch pools: ours, Grandpa's, and a few neighbours
    for nm, (lx, ly) in {"p_ours": (0.0, 7.6), "p_gp": (0.0, -7.6), "p_a": (18.0, -7.6), "p_b": (18.0, 7.6),
                         "p_c": (-18.0, -7.6), "p_d": (9.0, 7.6), "p_e": (-9.0, -7.6)}.items():
        kit.light(nm, "POINT", (lx + 1.0, ly, 2.2), 160.0 if nm in ("p_ours", "p_gp") else 90.0, "#ffcf73", size=0.5,
                  shadow=False)
    kit.light("rim", "POINT", (0.0, 0.0, 2.0), 900.0, "#ffd9a8", size=0.5, shadow=False)
    kit.light("street", "POINT", (-3.0, 0.0, 4.5), 700.0, "#7fa0ff", size=1.0, shadow=False)

    kit.plane("ground", (700, 700), (0, 0, 0), ground)
    kit.plane("road", (240, 11.0), (0, 0, 0.02), road)
    kit.plane("walkn", (240, 2.0), (0, 6.2, 0.03), walk)
    kit.plane("walks", (240, 2.0), (0, -6.2, 0.03), walk)
    for i in range(-11, 12):                         # road dashes
        kit.box(f"dash{i}", (2.2, 0.18, 0.01), (i * 5.0, 0, 0.035), plastic("#ffe6a0", 0.8))
    bulb = kit.emit("#bfd4ff", 6.0, "slbulb")
    for i, xx in enumerate(range(-54, 55, 18)):
        streetlight(kit, xx + 4.5, -5.6, dark, bulb)
        if xx + 9 != -9:                      # (the pole at x = -9 would stand in front of the L71 two-shot)
            streetlight(kit, xx + 9, 5.6, dark, bulb)

    W["plates"] = {}
    for side in (1, -1):
        for k in G.KS:
            if (side, k) == G.OURS:
                continue
            nm, objs = house(kit, side, k)
            W["plates"][(side, k)] = objs
    hollow_house(kit)
    W["plates"][G.OURS] = make_plate_objs(kit, "hn0", 0 + G.PLATE_DX, 9.0 - G.DECK_OUT + 0.65, G.DECK_Z)
    # our porch pieces (the deck, step, porch roof, lamp) share house() code through a shell: build the outside bits
    _our_porch(kit)
    # bushes and trees (a few)
    for k in G.KS:
        for side in (1, -1):
            try:
                kit.prop("bush_1", (k * G.SPACING - 3.1, side * 8.4, 0), height=0.8, tint="#bfe8a8")
            except Exception:
                pass
    for k, (x, y) in enumerate([(-22, 8.0), (-4.5, -8.2), (13, 8.2), (31, -8.3), (-31, 8.2)]):
        try:
            kit.prop("commontree_1", (x, y, 0), height=6.0, tint="#cfe8c0")
        except Exception:
            pass

    # the mailbox post with two gold strokes (the lore tally)
    kit.box("mail.post", (0.14, 0.14, 1.2), (2.9, 6.4, 0.6), kit.metal("#4a4d52", 0.5))
    kit.box("mail.box", (0.5, 0.3, 0.3), (2.9, 6.4, 1.3), kit.plastic("#3f78d9", 0.5))
    for k_ in range(2):
        kit.box(f"mail.stroke{k_}", (0.025, 0.02, 0.28), (2.86 + k_ * 0.08, 6.4 - 0.08, 0.55), kit.plastic("#ffcf73", 0.5))
    # Grandpa's porch: a rocking chair and a wild flower box
    gx = 0.0
    wood = plastic("#a8744a", 0.7, spec=0.1)
    kit.box("rock.seat", (0.8, 0.8, 0.1), (gx - 1.5, -8.2, 0.75), wood)
    kit.box("rock.back", (0.8, 0.08, 0.9), (gx - 1.5, -8.6, 1.2), wood, rot=(-0.12, 0, 0))
    for sx in (-1, 1):
        kit.box(f"rock.run{sx}", (0.06, 1.1, 0.06), (gx - 1.5 + sx * 0.4, -8.2, 0.4), wood)
        kit.box(f"rock.leg{sx}", (0.06, 0.06, 0.4), (gx - 1.5 + sx * 0.4, -8.3, 0.55), wood)
    kit.box("fbox", (2.0, 0.4, 0.4), (gx + 1.7, -8.4, 0.5), plastic("#8a5a3a", 0.8))
    for i in range(7):
        kit.sphere(f"fl{i}", 0.13, (gx + 0.9 + i * 0.28, -8.4 + (i % 2) * 0.08, 0.85 + (i % 3) * 0.12),
                   plastic(["#ff7a8a", "#ffd23f", "#c9b3f2"][i % 3], 0.6), seg=8)
        kit.box(f"fls{i}", (0.04, 0.04, 0.4), (gx + 0.9 + i * 0.28, -8.4, 0.62), plastic("#4f8f3a", 0.8))
    # snow (hidden until a cue)
    W["snow"] = [kit.plane("snow.ground", (240, 40), (0, 0, 0.07), plastic("#f4f8ff", 0.9, spec=0.05))]
    snow = plastic("#f4f8ff", 0.9, spec=0.05)
    for side in (1, -1):
        for k in G.KS:
            W["snow"].append(kit.box(f"snow{side}{k}", (7.9, 6.9, 0.2), (k * G.SPACING, side * 12.0, 5.1), snow))
            W["snow"].append(kit.box(f"snowd{side}{k}", (4.4, 1.7, 0.1), (k * G.SPACING, side * 8.1, 0.36), snow))
    # Mom's car
    car = kit.empty("car", (60, -3.0, 0))
    W["car"] = car
    kit.box("car.body", (4.2, 1.8, 0.8), (0, 0, 0.7), plastic("#d9413b", 0.4, spec=0.5), car, bevel=0.1)
    kit.box("car.cab", (2.2, 1.6, 0.7), (-0.2, 0, 1.4), plastic("#d9413b", 0.4, spec=0.5), car, bevel=0.1)
    kit.box("car.win", (2.25, 1.62, 0.4), (-0.2, 0, 1.45), plastic("#9fd0f0", 0.2, spec=0.8), car)
    for sx in (-1, 1):
        for sy in (-1, 1):
            kit.cyl(f"car.w{sx}{sy}", 0.38, 0.25, (sx * 1.4, sy * 0.9, 0.38), dark, car, rot=(math.pi / 2, 0, 0), n=14)
    # --------------------------------------------------------------------- the rooms
    kx, ky = G.KITCHEN
    room(kit, kx, ky, "#ffe8c8", "#c9976a", "kit")
    kit.box("kit.cab", (4.0, 0.8, 0.95), (kx - 1.8, ky + 3.0, 0.5), plastic("#9ee6c4", 0.6))
    kit.box("kit.cabtop", (4.1, 0.9, 0.06), (kx - 1.8, ky + 3.0, 1.0), plastic("#fffaf0", 0.7))
    kit.box("kit.stove", (1.0, 0.8, 0.95), (kx + 0.8, ky + 3.0, 0.5), plastic("#e8e8ee", 0.4, spec=0.4))
    kit.cyl("kit.pan", 0.28, 0.07, (kx + 0.8, ky + 3.0, 1.04), plastic("#2a2a30", 0.4, spec=0.4), n=16)
    kit.box("kit.panh", (0.4, 0.07, 0.04), (kx + 0.8, ky + 2.55, 1.06), plastic("#2a2a30", 0.4))
    kit.box("kit.win", (1.6, 0.1, 1.2), (kx - 2.5, ky + 3.52, 1.9), kit.emit("#bfe0ff", 1.8, "kwin"))
    kit.box("kit.winf", (1.9, 0.08, 1.5), (kx - 2.5, ky + 3.5, 1.9), plastic("#fffaf0", 0.6))
    kit.box("kit.table", (1.8, 1.1, 0.12), (kx + 2.4, ky + 0.6, 0.78), wood)
    for sx in (-1, 1):
        for sy in (-1, 1):
            kit.box(f"kit.tl{sx}{sy}", (0.1, 0.1, 0.75), (kx + 2.4 + sx * 0.8, ky + 0.6 + sy * 0.45, 0.38), wood)
    for sy in (-1, 1):
        kit.box(f"kit.ch{sy}", (0.55, 0.55, 0.08), (kx + 2.4, ky + 0.6 + sy * 1.05, 0.5), wood)
        kit.box(f"kit.chb{sy}", (0.55, 0.08, 0.6), (kx + 2.4, ky + 0.6 + sy * 1.3, 0.85), wood)
    kit.cyl("kit.cplate", 0.3, 0.04, (kx - 1.8, ky + 3.0, 1.05), plastic("#fff6e4", 0.5), n=18)
    cd = kit.sphere("kit.cfoil", 0.29, (kx - 1.8, ky + 3.0, 1.09), kit.metal("#dfe3e8", 0.28), seg=12)
    cd.scale = (1.0, 1.0, 0.5)
    kit.light("kit_l", "POINT", (kx, ky + 0.5, 2.8), 350.0, "#ffe2b8", size=0.6, shadow=False)
    gx_, gy_ = G.GROOM
    room(kit, gx_, gy_, "#d8e6dc", "#b9936a", "grm")
    # photo of Grandma, on the back wall at x = gx-2.4
    pl = lambda c, r=0.9: plastic(c, r)
    px0, py0, pz0 = gx_ - 2.4, gy_ + 3.5, 1.8
    kit.box("ph.frame", (1.1, 0.08, 1.4), (px0, py0, pz0), pl("#5a3b24", 0.7))
    kit.box("ph.bg", (0.92, 0.05, 1.22), (px0, py0 - 0.05, pz0), pl("#f1e4c4"))
    kit.box("ph.body", (0.62, 0.03, 0.4), (px0, py0 - 0.09, pz0 - 0.4), pl("#d97a9a"))
    kit.box("ph.head", (0.36, 0.03, 0.38), (px0, py0 - 0.09, pz0 + 0.05), pl("#f0c8a0"))
    kit.box("ph.hair", (0.4, 0.03, 0.16), (px0, py0 - 0.10, pz0 + 0.24), pl("#d8d8e0"))
    kit.sphere("ph.bun", 0.12, (px0, py0 - 0.1, pz0 + 0.4), pl("#d8d8e0"), seg=8)
    for sx in (-1, 1):
        kit.box(f"ph.eye{sx}", (0.05, 0.03, 0.05), (px0 + sx * 0.09, py0 - 0.115, pz0 + 0.08), pl("#1c120c"))
        kit.box(f"ph.ear{sx}", (0.05, 0.03, 0.08), (px0 + sx * 0.2, py0 - 0.115, pz0 - 0.08), pl("#ffffff", 0.3))
    kit.box("ph.smile", (0.16, 0.03, 0.035), (px0, py0 - 0.115, pz0 - 0.07), pl("#b04a4a"))
    # the kitchen corner of Grandpa's room: cold stove, sink with a mug, table with a cracker
    kit.box("grm.cab", (3.2, 0.8, 0.95), (gx_ + 1.4, gy_ + 3.0, 0.5), plastic("#c8d0c8", 0.6))
    kit.box("grm.cabtop", (3.3, 0.9, 0.06), (gx_ + 1.4, gy_ + 3.0, 1.0), plastic("#eee8dc", 0.7))
    kit.box("grm.stove", (1.0, 0.8, 0.95), (gx_ + 2.8, gy_ + 3.0, 0.5), plastic("#9a9aa0", 0.5))
    kit.cyl("grm.mug", 0.1, 0.18, (gx_ + 0.8, gy_ + 2.9, 1.12), plastic("#f6ecd8", 0.6), n=12)
    kit.box("grm.table", (1.6, 1.0, 0.12), (gx_ + 0.6, gy_ + 0.4, 0.78), wood)
    for sx in (-1, 1):
        for sy in (-1, 1):
            kit.box(f"grm.tl{sx}{sy}", (0.1, 0.1, 0.75), (gx_ + 0.6 + sx * 0.7, gy_ + 0.4 + sy * 0.4, 0.38), wood)
    kit.cyl("grm.dish", 0.2, 0.03, (gx_ + 0.6, gy_ + 0.4, 0.86), plastic("#fff6e4", 0.5), n=14)
    kit.box("grm.cracker", (0.12, 0.12, 0.02), (gx_ + 0.6, gy_ + 0.4, 0.89), plastic("#e8c88a", 0.7))
    cer = kit.empty("grm.cereal", (0, 0, 0))
    kit.cyl("grm.cb", 0.17, 0.1, (gx_ + 1.0, gy_ + 0.5, 0.88), plastic("#7fb8e8", 0.5), cer, n=16)
    kit.cyl("grm.cm", 0.14, 0.02, (gx_ + 1.0, gy_ + 0.5, 0.94), plastic("#fbfbff", 0.4), cer, n=16)
    jug = kit.empty("grm.jugpour", (gx_ + 1.0, gy_ + 0.5, 1.28), cer)
    jug.rotation_euler = (0.9, 0, 0)
    kit.box("grm.jb", (0.12, 0.1, 0.24), (0, 0, 0), plastic("#fbfbff", 0.4), jug, bevel=0.015)
    kit.box("grm.jc", (0.07, 0.06, 0.05), (0, 0, 0.14), plastic("#3a78d9", 0.4), jug)
    kit.box("grm.stream", (0.03, 0.03, 0.34), (gx_ + 1.0, gy_ + 0.5, 1.1), plastic("#fbfbff", 0.4), cer)
    W["cereal"] = cer
    kit.box("grm.chair", (0.55, 0.55, 0.08), (gx_ + 0.6, gy_ - 0.55, 0.5), wood)
    kit.box("grm.chairb", (0.55, 0.08, 0.6), (gx_ + 0.6, gy_ - 0.85, 0.85), wood)
    # the hook and the long coat
    kit.box("grm.hook", (0.5, 0.08, 0.06), (gx_ + 3.4, gy_ + 3.52, 2.2), plastic("#3a3a44", 0.5))
    coatc = plastic("#2f4a3a", 0.85)
    kit.box("grm.coat", (0.8, 0.22, 1.9), (gx_ + 3.4, gy_ + 3.3, 1.2), coatc, bevel=0.05)
    kit.box("grm.coatc", (0.9, 0.26, 0.2), (gx_ + 3.4, gy_ + 3.3, 2.1), coatc, bevel=0.05)
    for sx in (-1, 1):
        kit.box(f"grm.coats{sx}", (0.2, 0.2, 1.5), (gx_ + 3.4 + sx * 0.5, gy_ + 3.3, 1.35), coatc, bevel=0.04)
    kit.box("grm.win", (1.6, 0.1, 1.2), (gx_ - 0.4, gy_ + 3.52, 1.9), kit.emit("#d8e8ff", 1.6, "gwin"))
    kit.box("grm.winf", (1.9, 0.08, 1.5), (gx_ - 0.4, gy_ + 3.5, 1.9), plastic("#fffaf0", 0.6))
    for i in range(3):
        kit.cyl(f"grm.stk{i}", 0.3, 0.04, (gx_ + 2.0, gy_ + 3.0, 1.05 + i * 0.045), plastic("#fff6e4", 0.5), n=18)
    kit.light("grm_l", "POINT", (gx_, gy_ + 0.5, 2.8), 320.0, "#ffe2b8", size=0.6, shadow=False)
    build_tag(kit)
    return {}


def _our_porch(kit):
    """Our porch outside (deck, step, porch roof, lamp, window, plaque-free)."""
    x = 0.0
    trim = kit.plastic("#fffaf0", 0.6)
    kit.box("hn0.roof", (7.8, 6.8, 0.4), (x, 12.0, 4.4), kit.plastic("#3f6aa0", 0.6, spec=0.15))
    kit.box("hn0.roof2", (5.4, 4.6, 0.5), (x, 12.0, 4.8), kit.plastic("#3f6aa0", 0.6, spec=0.15))
    kit.box("hn0.deck", (4.6, G.DECK_OUT, 0.3), (x, 9.0 - G.DECK_OUT / 2, 0.15), kit.plastic("#d8b890", 0.8))
    kit.box("hn0.step", (1.8, 0.7, 0.15), (x, 9.0 - G.DECK_OUT - 0.35, 0.075), kit.plastic("#cbb08c", 0.8))
    kit.box("hn0.proof", (4.8, 2.0, 0.15), (x, 8.0, 3.0), trim)
    for sx in (-1, 1):
        kit.cyl(f"hn0.post{sx}", 0.08, 2.7, (x + sx * 2.2, 7.3, 0.3 + 1.35), trim, n=8)
    kit.box("hn0.lamp", (0.2, 0.1, 0.3), (x + 1.0, 8.9, 2.5), kit.plastic("#3a3a40", 0.5))
    kit.sphere("hn0.bulb", 0.13, (x + 1.0, 8.76, 2.45), kit.emit("#ffcf73", 7.0, "bulb"), seg=8)


def build_tag(kit):
    """The rule meter: a round cream plate tag, top-left. A dark rim, a cream plate, a gold ring, the count of plates
    out tonight over a bar over 43 in chunky seven-segment digits."""
    cam = kit.OBJ["cam"]
    root = kit.empty("tag", (0, 0, 0), cam)
    W["tag"] = root
    cream = kit.emit("#fff6e0", 1.0, "tagcream")
    rim = kit.emit("#3a2210", 0.6, "tagrim")
    ring = kit.emit("#ffb73a", 0.9, "tagring")
    ink = kit.emit("#2a1408", 0.5, "taginkk")
    def b(name, ob):
        noshadow(ob)
        return ob
    b("rim", kit.cyl("tag.rim", 0.52, 0.004, (0, 0, 0.0), rim, root, n=40))
    b("ring", kit.cyl("tag.ring", 0.47, 0.004, (0, 0, 0.004), ring, root, n=40))
    b("plate", kit.cyl("tag.plate", 0.42, 0.004, (0, 0, 0.008), cream, root, n=40))
    # a small plate icon between the numbers (dark rim, cream well) so the tag reads as plates
    b("ip", kit.cyl("tag.ip", 0.088, 0.004, (0, 0, 0.014), ink, root, n=20))
    b("ipc", kit.cyl("tag.ipc", 0.056, 0.004, (0, 0, 0.018), cream, root, n=20))
    segs = "abcdefg"

    def digit(nm, cx, cy, w=0.21, h=0.29, t=0.08):
        out = {}
        xs0, xs1 = w / 2 - t / 2, -(w / 2 - t / 2)
        pos = {"a": (0, h / 2 - t / 2, w - t, t), "g": (0, 0, w - t, t), "d": (0, -h / 2 + t / 2, w - t, t),
               "f": (-(w / 2 - t / 2), h / 4, t, h / 2 - t / 2), "b": (w / 2 - t / 2, h / 4, t, h / 2 - t / 2),
               "e": (-(w / 2 - t / 2), -h / 4, t, h / 2 - t / 2), "c": (w / 2 - t / 2, -h / 4, t, h / 2 - t / 2)}
        for s in segs:
            dx, dz, sw, sh = pos[s]
            out[s] = b(nm, kit.box(f"tag.{nm}{s}", (sw, sh, 0.004), (cx + dx, cy + dz, 0.016), ink, root))
        # a "1" with a flag and a foot (stem centred) so it can't be read as an "i" or a bar
        out["s"] = b(nm, kit.box(f"tag.{nm}s", (t * 1.15, h, 0.004), (cx + 0.01, cy, 0.016), ink, root))
        out["l"] = b(nm, kit.box(f"tag.{nm}l", (0.1, t, 0.004), (cx - 0.05, cy + h / 2 - t * 1.2, 0.016), ink, root))
        out["z"] = b(nm, kit.box(f"tag.{nm}z", (w, t * 0.9, 0.004), (cx, cy - h / 2 + t * 0.45, 0.016), ink, root))
        return out

    W["d_t1"] = digit("t1", -0.125, 0.235)
    W["d_t2"] = digit("t2", 0.125, 0.235)
    W["d_b1"] = digit("b1", -0.125, -0.235)
    W["d_b2"] = digit("b2", 0.125, -0.235)


SEG = {"0": "abcdef", "1": "slz", "2": "abged", "3": "abgcd", "4": "fgbc", "5": "afgcd", "6": "afgedc", "7": "abc",
       "8": "abcdefg", "9": "abcdfg"}


def set_digit(d, ch):
    for s, ob in d.items():
        ob.hide_render = s not in SEG[ch]


def _first_frame(kit, story):
    # carried things, parented to the right arm hinge of Grandpa / me
    W["carry"] = {}
    ga = bpy.data.objects.get("grandpa.arm1")
    if ga is not None:
        wick = kit.plastic("#b8864e", 0.8)
        cl = kit.plastic("#d9413b", 0.8)
        c = kit.empty("carry.basket", (0, -0.15, -2.15), ga)
        kit.box("bk.body", (1.5, 1.0, 0.75), (0, 0, -0.1), wick, c, bevel=0.06)
        kit.box("bk.rim", (1.6, 1.1, 0.1), (0, 0, 0.3), wick, c)
        for sx in (-1, 1):
            kit.box(f"bk.h{sx}", (0.1, 0.1, 0.9), (sx * 0.7, 0, 0.7), wick, c)
        kit.box("bk.hb", (1.5, 0.1, 0.1), (0, 0, 1.15), wick, c)
        kit.box("bk.cloth", (1.45, 0.95, 0.06), (0, 0, 0.36), cl, c)
        for i in range(3):
            kit.box(f"bk.chk{i}", (0.34, 0.99, 0.065), (-0.5 + i * 0.5, 0, 0.365), kit.plastic("#fff6e4", 0.8), c)
        W["carry"][1] = c
        full = kit.empty("carry.full", (0, -0.15, -2.15), ga)
        for i, xo in enumerate((-0.4, 0.4)):
            kit.cyl(f"bkp{i}", 0.5, 0.12, (xo, 0, 0.5), kit.metal("#dfe3e8", 0.28), full, n=14)
        W["carry"][3] = full
        dish = kit.empty("carry.dish", (0, -0.9, -1.6), ga)
        kit.box("dish.b", (1.4, 1.0, 0.4), (0, 0, 0), kit.plastic("#d98a4a", 0.6), dish, bevel=0.05)
        kit.box("dish.f", (1.5, 1.1, 0.12), (0, 0, 0.26), kit.metal("#dfe3e8", 0.28), dish)
        W["carry"][2] = dish
        sw = kit.empty("carry.sand", (0, -0.9, -1.6), ga)
        toast = kit.plastic("#c47f32", 0.6)
        kit.box("sw.b", (1.0, 0.9, 0.18), (0, 0, 0), toast, sw, bevel=0.05)
        kit.box("sw.c", (1.1, 1.0, 0.14), (0, 0, 0.12), kit.plastic("#ffcf2a", 0.5), sw)
        kit.box("sw.d", (1.0, 0.9, 0.18), (0, 0, 0.24), toast, sw, bevel=0.05)
        kit.box("sw.e", (0.8, 0.7, 0.02), (0, 0, 0.34), kit.plastic("#e0a050", 0.6), sw)
        W["carry"][4] = sw
    me = bpy.data.objects.get("me.arm1")
    if me is not None:
        pl = kit.empty("carry.meplate", (0, -0.9, -1.6), me)
        kit.cyl("mp.pl", 0.55, 0.1, (0, 0, 0), kit.plastic("#fff6e4", 0.5), pl, n=16)
        d = kit.sphere("mp.foil", 0.52, (0, 0, 0.12), kit.metal("#dfe3e8", 0.28), pl, seg=12)
        d.scale = (1.0, 1.0, 0.5)
        W["meplate"] = pl
        ch = kit.empty("carry.chips", (0, -0.9, -1.6), me)
        kit.box("chips.bag", (0.9, 0.3, 1.0), (0, 0, 0), kit.plastic("#e8493a", 0.5), ch)
        W["chips"] = ch
    W["inited"] = True


def animate(kit, story, tl, t, ctx):
    if not W.get("inited"):
        _first_frame(kit, story)
    look = look_at(tl, t)
    gains = {}
    az, el = look["az"] * D2R, look["el"] * D2R
    d = Vector((math.sin(az) * math.cos(el), math.cos(az) * math.cos(el), math.sin(el)))
    so = kit.LIGHTS["sun"]["obj"]
    so.location = d * 60
    kit.aim(so, (0, 0, 0))
    kit.LIGHTS["sun"]["light"].color = look["sun_col"]
    kit.LIGHTS["fill"]["light"].color = look["fill_col"]
    gains["sun"], gains["fill"], gains["front"] = look["sun"], look["fill"], look["front"]
    for nm in ("p_ours", "p_gp", "p_a", "p_b", "p_c", "p_d", "p_e"):
        gains[nm] = look["porch"]
    gains["street"] = look["street"] * 0.8
    rm = sample("rim", tl, t, {"v": 0.0, "x": 0.0, "y": 0.0, "z": 2.0})
    kit.LIGHTS["rim"]["obj"].location = (rm["x"], rm["y"], rm["z"])
    gains["rim"] = rm["v"]
    sh_ = sample("shade", tl, t, {"v": 0.0})
    for ob in W["shade"]:
        ob.hide_render = sh_["v"] < 0.5
    w = bpy.context.scene.world
    bg = w.node_tree.nodes["Background"]
    bg.inputs["Color"].default_value = (*look["sky"], 1.0)
    bg.inputs["Strength"].default_value = look["sky_str"]
    # the plates
    ps = sample("plates", tl, t, {"street": 1.0, "ours": 1.0, "gp": 0.0})
    for key, (p1, p2, p3) in W["plates"].items():
        if key == G.OURS:
            st = int(round(ps["ours"]))
        elif key == G.GRANDPA:
            st = int(round(ps["gp"]))
        else:
            st = int(round(ps["street"]))
        for ob in p1:
            ob.hide_render = st != 1
        for ob in p2:
            ob.hide_render = st != 2
        for ob in p3:
            ob.hide_render = st != 3
    # the tag
    cn = sample("count", tl, t, {"n": 42.0})
    n = int(round(cn["n"]))
    set_digit(W["d_t1"], str(n // 10))
    set_digit(W["d_t2"], str(n % 10))
    set_digit(W["d_b1"], "4")
    set_digit(W["d_b2"], "3")
    lens = 40.0
    shot = next((s for s in tl["shots"] if s["start"] <= t < s["end"]), tl["shots"][-1])
    spec = next((s for s in story["shots"] if s["id"] == shot["id"]), None)
    if spec:
        keys = spec["cam"]
        u = (t - shot["start"]) / max(1e-6, shot["end"] - shot["start"])
        lens = keys[0][3]
        if len(keys) > 1:
            for a, b in zip(keys, keys[1:]):
                if u <= b[0]:
                    lens = a[3] + (b[3] - a[3]) * ss((u - a[0]) / max(1e-6, b[0] - a[0]))
                    break
            else:
                lens = keys[-1][3]
    dist = 0.3
    h2 = dist * 12.0 / lens
    w2 = h2 * 9.0 / 16.0
    tag = W["tag"]
    s = 0.46 * w2
    tag.scale = (s, s, s)
    tag.location = (-0.285 * w2, 0.62 * h2, -dist)
    # our door, knocker, clock, blinds, TV
    dr = sample("door_open", tl, t, {"v": 0.0})
    kn0 = sample("knock", tl, t, {"v": 0.0})
    W["door"].rotation_euler = (0, 0, dr["v"] * 100 * D2R + (0.004 * math.sin(t * 50) * kn0["v"]))
    kn = sample("knock", tl, t, {"v": 0.0})
    W["knocker"].rotation_euler = (kn["v"] * 0.55 * math.sin(t * 12), 0, 0)
    ck = sample("clock", tl, t, {"h": 11.0, "m": 0.0})
    W["hand_h"].rotation_euler = (-ck["h"] * 30 * D2R, 0, 0)
    W["hand_m"].rotation_euler = (-ck["m"] * 6 * D2R, 0, 0)
    bl = sample("blind", tl, t, {"v": 1.0})
    for ob in W["blind_slit"]:
        ob.hide_render = bl["v"] < 0.5
    sn = sample("snow", tl, t, {"v": 0.0})
    for ob in W["snow"]:
        ob.hide_render = sn["v"] < 0.5
    car = sample("car", tl, t, {"x": 60.0})
    W["car"].location = (car["x"], -3.0, 0.0)
    W["car"].hide_render = car["x"] > 59.0
    cr = sample("carry", tl, t, {"v": 0.0})
    for i, ob in W["carry"].items():
        _hide(ob, int(round(cr["v"])) != i and not (i == 1 and int(round(cr["v"])) == 3))
    mp = sample("meplate", tl, t, {"v": 0.0})
    if W.get("meplate") is not None:
        _hide(W["meplate"], mp["v"] < 0.5)
    ce = sample("cereal", tl, t, {"v": 0.0})
    if W.get("cereal") is not None:
        _hide(W["cereal"], ce["v"] < 0.5)
    ch = sample("chips", tl, t, {"v": 0.0})
    if W.get("chips") is not None:
        _hide(W["chips"], ch["v"] < 0.5)
    # who sits: legs straight out forward
    for c in [c for c in tl["cues"] if c["name"] == "sit" and c["t"] <= t]:
        pass
    sits = {}
    for c in tl["cues"]:
        if c["name"] == "sit" and c["t"] <= t:
            sits[c["who"]] = c
    for who, c in sits.items():
        root = bpy.data.objects.get(who)
        if c.get("on") and root is not None:
            root.location.z += c.get("z", 0.62) - 0.68
            for sx in (-1, 1):
                leg = bpy.data.objects.get(f"{who}.leg{sx}")
                if leg:
                    leg.rotation_euler = (-math.pi / 2 * 0.97, 0, 0)
    return gains
