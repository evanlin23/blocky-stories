"""ep110 "bless you": a pollen-gold spring town. Small sets side by side along x (see layout.py): the park, a street,
an office, two kitchens, a dog's room, a party, a landlord's room, Grandpa's green front room (with the wall of
clippings), a bedroom. Everything the story moves is driven by cues in story.json (see animate): the look (day or the
one dark 2 a.m. scene), the TV glow, the rule meter (a cream tag on the camera: pollen glyph with five dots, the
sneeze count in seven-segment digits, map pins), the pollen in the air, the soft gold swirl a sneeze leaves, who sits,
the cups, the pill bottle.
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
GOLD = "#ffc93a"


def ss(x):
    x = min(1.0, max(0.0, x))
    return x * x * (3 - 2 * x)


def rnd(*xs):
    h = 0.0
    for i, x in enumerate(xs):
        h = math.sin(h * 12.9898 + (x + 1.7 * i) * 78.233 + 0.37) * 43758.5453
    return h - math.floor(h)


def kit_col(h):
    h = h.lstrip("#")
    f = lambda c: (c / 12.92) if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
    return tuple(f(int(h[i:i + 2], 16) / 255) for i in (0, 2, 4))


def _L(**kw):
    base = dict(sun=3.2, sun_col="#fff0d0", el=48.0, az=-20.0, fill=0.9, fill_col="#fff2dc", sky="#9fd8ff", sky_str=1.0,
                front=0.35, night=0.0)
    base.update(kw)
    return base


LOOKS = {
    "day": _L(),
    # the one dark scene: no sun, a dim cold sky, the TV and the streetlight do the work
    "night": _L(sun=0.0, fill=0.02, fill_col="#9fb4ff", sky="#0a1020", sky_str=0.06, front=0.0, night=1.0),
}


def look_at(tl, t):
    cues = [c for c in tl["cues"] if c["name"] == "look"]
    cur = LOOKS[cues[0]["id"]] if cues else LOOKS["day"]
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


def noshadow(ob):
    ob.visible_shadow = False
    for c in ob.children_recursive:
        c.visible_shadow = False


# ---------------------------------------------------------------------------------------------- set helpers
def room(kit, x0, wall, floor, name, wide=10.0, hgt=3.6):
    """Floor, back wall (y = +4), two side walls. Open on the camera side."""
    kit.plane(f"{name}.floor", (wide, 9.0), (x0, 0.5, 0.03), floor)
    kit.box(f"{name}.back", (wide, 0.3, hgt), (x0, G.WALL_Y, hgt / 2), wall)
    for sx in (-1, 1):
        kit.box(f"{name}.side{sx}", (0.3, 9.0, hgt), (x0 + sx * wide / 2, 0.5, hgt / 2), wall)


def armchair(kit, name, x, y, col, rough=0.8):
    m = kit.plastic(col, rough, spec=0.12)
    dk = kit.plastic("#1f4a33" if col == "#2f6b4a" else col, rough, spec=0.1)
    kit.box(f"{name}.seat", (1.1, 1.0, 0.24), (x, y, 0.33), m, bevel=0.07)
    kit.box(f"{name}.base", (1.1, 1.0, 0.2), (x, y, 0.1), dk, bevel=0.04)
    kit.box(f"{name}.back", (1.1, 0.24, 1.15), (x, y + 0.5, 0.78), m, bevel=0.08)
    for sx in (-1, 1):
        kit.box(f"{name}.arm{sx}", (0.3, 1.0, 0.46), (x + sx * 0.62, y, 0.44), m, bevel=0.07)


def sofa(kit, name, x, y, w, col):
    m = kit.plastic(col, 0.8, spec=0.1) if isinstance(col, str) else col
    kit.box(f"{name}.seat", (w, 1.0, 0.24), (x, y, 0.33), m, bevel=0.07)
    kit.box(f"{name}.base", (w, 1.0, 0.2), (x, y, 0.1), m, bevel=0.04)
    kit.box(f"{name}.back", (w, 0.24, 0.95), (x, y + 0.5, 0.68), m, bevel=0.08)
    for sx in (-1, 1):
        kit.box(f"{name}.arm{sx}", (0.24, 1.0, 0.5), (x + sx * (w / 2 - 0.12), y, 0.46), m, bevel=0.07)


def cup(kit, name, x, y, z, parent=None, col="#f6ecd8", r=0.055):
    c = kit.plastic(col, 0.35, spec=0.5)
    ob = kit.cyl(f"{name}.cup", r, 0.075, (x, y, z + 0.0375), c, parent, n=14, r2=r * 0.8)
    kit.box(f"{name}.handle", (0.02, 0.05, 0.04), (x + r + 0.008, y, z + 0.04), c, parent)
    return ob


def tea_tray(kit, x, y, z, name="tray", two=True):
    brass = kit.plastic("#d9a441", 0.3, spec=0.7)
    kit.box(f"{name}.tray", (0.78, 0.46, 0.03), (x, y, z + 0.015), brass, bevel=0.01)
    kit.box(f"{name}.handleL", (0.04, 0.2, 0.05), (x - 0.4, y, z + 0.05), brass)
    kit.box(f"{name}.handleR", (0.04, 0.2, 0.05), (x + 0.4, y, z + 0.05), brass)
    # three green strokes scratched low on the handle (lore plant), 1 cm proud
    sm = kit.plastic("#2fa86a", 0.5)
    for k in range(3):
        kit.box(f"{name}.stroke{k}", (0.012, 0.012, 0.05), (x + 0.4, y - 0.075 + k * 0.07, z + 0.05), sm, rot=(0, 0.35, 0))
    pot = kit.plastic("#fffaf0", 0.35, spec=0.5)
    kit.sphere(f"{name}.pot", 0.1, (x + 0.2, y + 0.04, z + 0.13), pot, seg=14)
    kit.box(f"{name}.spout", (0.04, 0.12, 0.04), (x + 0.2, y - 0.1, z + 0.14), pot, rot=(0.5, 0, 0))
    kit.cyl(f"{name}.lid", 0.04, 0.04, (x + 0.2, y + 0.04, z + 0.24), pot, n=10)
    cup(kit, f"{name}.c1", x - 0.2, y + 0.0, z + 0.03)
    cup(kit, f"{name}.c2", x - 0.05, y - 0.02, z + 0.03)
    g3 = kit.empty(f"{name}.c3g", (0, 0, 0))
    cup(kit, f"{name}.c3", x - 0.12, y + 0.14, z + 0.03, parent=g3)
    W["cup3"] = g3
    return None


def figure(kit, name, x, y, z, s, shirt, skin="#dca97c", hair="#c89a5a", bg=None, bgw=0.36, bgh=0.28):
    """A tiny flat person on a clipping (head, shoulders, hair), 0.5 cm layers toward the camera (-y)."""
    if bg:
        kit.box(f"{name}.bg", (bgw, 0.006, bgh), (x, y, z), kit.plastic(bg, 0.8))
    kit.box(f"{name}.body", (0.16 * s, 0.006, 0.12 * s), (x, y - 0.01, z - 0.07 * s), kit.plastic(shirt, 0.8))
    kit.box(f"{name}.head", (0.09 * s, 0.006, 0.1 * s), (x, y - 0.02, z + 0.02 * s), kit.plastic(skin, 0.8), bevel=0.01)
    kit.box(f"{name}.hair", (0.1 * s, 0.006, 0.04 * s), (x, y - 0.03, z + 0.065 * s), kit.plastic(hair, 0.8))


def clippings(kit, x0):
    paper_cols = ["#f6ecd0", "#efe0b8", "#f9f1dc", "#e9dcb0"]
    bgs = ["#ffd66b", "#9fdc9a", "#f4a3a3", "#c9b3ff", "#ffb87a", "#fff0b0"]
    shirts = ["#5fa8e8"] * 6                  # every clipping is the narrator in his blue hoodie
    ink = kit.plastic("#5a4a36", 0.9)
    yw = G.WALL_Y - 0.15            # the wall's inner face
    W["clip"] = {}
    for r, zc in enumerate((1.4, 2.05, 2.7)):
        for i in range(11):
            if i < 2 and r > 0:
                continue                       # the big portrait goes here
            x = x0 - 4.0 + i * 0.8 + (rnd(i, r, 1) - 0.5) * 0.08
            z = zc + (rnd(i, r, 2) - 0.5) * 0.08
            rot = (rnd(i, r, 3) - 0.5) * 0.1
            pw, ph = 0.56, 0.6
            kit.box(f"clip{i}_{r}.paper", (pw, 0.01, ph), (x, yw - 0.01, z), kit.plastic(paper_cols[(i + r) % 4], 0.9),
                    rot=(0, rot, 0))
            W["clip"][(i, r)] = (x, z)
            if (i, r) in ((3, 2), (4, 2), (5, 2)):
                continue                       # drawn by hand below
            figure(kit, f"clip{i}_{r}.f", x, yw - 0.025, z + 0.1, 1.0, shirts[(i * 2 + r) % 6], bg=bgs[(i + 2 * r) % 6],
                   bgw=0.44, bgh=0.3)
            for k in range(3):
                kit.box(f"clip{i}_{r}.ln{k}", (0.44 - 0.1 * ((i + k) % 3), 0.006, 0.025), (x - 0.04 * (k % 2), yw - 0.025,
                        z - 0.1 - k * 0.055), ink)
    # feature 1: a birth notice (a swaddled baby), 2: a bowling trophy (me at about 16), 3: me in a work shirt
    for (i, r), kind in {(3, 2): "baby", (4, 2): "bowl", (5, 2): "work"}.items():
        x, z = W["clip"][(i, r)]
        y = yw - 0.025
        if kind == "baby":
            kit.box(f"clipB.bg", (0.44, 0.006, 0.3), (x, y, z + 0.1), kit.plastic("#ffd1dc", 0.8))
            kit.box(f"clipB.blanket", (0.2, 0.006, 0.12), (x, y - 0.01, z + 0.06), kit.plastic("#fffaf0", 0.8), bevel=0.01)
            kit.box(f"clipB.head", (0.1, 0.006, 0.1), (x, y - 0.02, z + 0.15), kit.plastic("#dca97c", 0.8), bevel=0.01)
            kit.box(f"clipB.hair", (0.05, 0.006, 0.03), (x, y - 0.03, z + 0.2), kit.plastic("#c89a5a", 0.8))
        elif kind == "bowl":
            kit.box(f"clipT.bg", (0.44, 0.006, 0.3), (x, y, z + 0.1), kit.plastic("#ffd66b", 0.8))
            figure(kit, "clipT.me", x - 0.07, y - 0.01, z + 0.1, 1.0, "#5fa8e8", bg=None)
            kit.cyl("clipT.cup", 0.045, 0.1, (x + 0.1, y - 0.04, z + 0.1), kit.plastic("#ffd23f", 0.3, spec=0.7), rot=(math.pi / 2, 0, 0), n=10, r2=0.025)
            kit.box("clipT.base", (0.11, 0.01, 0.03), (x + 0.1, y - 0.04, z + 0.04), kit.plastic("#d9a441", 0.3, spec=0.6))
        else:
            kit.box(f"clipW.bg", (0.44, 0.006, 0.3), (x, y, z + 0.1), kit.plastic("#cfe6c8", 0.8))
            figure(kit, "clipW.me", x, y - 0.01, z + 0.1, 1.2, "#5fa8e8", bg=None)
        for k in range(3):
            kit.box(f"clip{kind}.ln{k}", (0.44 - 0.1 * k, 0.006, 0.025), (x, y, z - 0.1 - k * 0.055), ink)
    # the big portrait of me, a gold frame, a little proud of the clippings
    px, pz = x0 - 3.6, 2.3
    kit.box("portrait.frame", (1.34, 0.03, 1.44), (px, yw - 0.035, pz), kit.plastic("#d9a441", 0.3, spec=0.7), bevel=0.01)
    kit.box("portrait.bg", (1.18, 0.01, 1.28), (px, yw - 0.06, pz), kit.plastic("#8ec9ff", 0.8))
    kit.box("portrait.hoodie", (0.84, 0.01, 0.5), (px, yw - 0.07, pz - 0.44), kit.plastic("#5fa8e8", 0.7))
    kit.box("portrait.head", (0.46, 0.01, 0.5), (px, yw - 0.08, pz + 0.12), kit.plastic("#dca97c", 0.7), bevel=0.03)
    kit.box("portrait.hair", (0.5, 0.01, 0.16), (px, yw - 0.09, pz + 0.36), kit.plastic("#c89a5a", 0.7), bevel=0.02)
    for sx in (-1, 1):
        kit.box(f"portrait.eye{sx}", (0.06, 0.01, 0.07), (px + sx * 0.11, yw - 0.09, pz + 0.17), kit.plastic("#1c120c", 0.6))
    kit.box("portrait.smile", (0.16, 0.01, 0.035), (px, yw - 0.09, pz + 0.02), kit.plastic("#7a3a30", 0.6))


def pollen_swirl_pool(kit):
    m = kit.emit(GOLD, 1.5, "swirlgold")
    W["sw"] = []
    for i in range(96):
        ob = kit.sphere(f"swirl{i}", 0.085, (0, 0, -50), m, seg=6)
        noshadow(ob)
        W["sw"].append(ob)
    m2 = kit.emit("#ffd75a", 2.0, "specgold")
    W["sp"] = []
    for i in range(170):
        ob = kit.sphere(f"speck{i}", 0.032 + 0.02 * rnd(i, 9), (0, 0, -50), m2, seg=5)
        noshadow(ob)
        W["sp"].append(ob)


def kitchen(kit, x0, name, wall, floor, cab, stove_c, mom_house=True, ours=False):
    room(kit, x0, wall, floor, name)
    plastic = kit.plastic
    cabm = plastic(cab, 0.5, spec=0.2)
    top = plastic("#f6ecd8", 0.4, spec=0.3)
    # counter run on the back wall
    kit.box(f"{name}.cab", (6.2, 0.8, 0.88), (x0 - 1.4, 3.45, 0.44), cabm, bevel=0.02)
    kit.box(f"{name}.top", (6.3, 0.9, 0.06), (x0 - 1.4, 3.45, 0.91), top, bevel=0.015)
    for k in range(6):
        kit.box(f"{name}.door{k}", (0.9, 0.02, 0.62), (x0 - 3.95 + k * 1.03, 3.04, 0.45), plastic(cab, 0.5), bevel=0.01)
    # the stove (blue), four burners and an oven door
    sx = x0 - 2.4
    kit.box(f"{name}.stove", (1.0, 0.82, 0.94), (sx, 3.43, 0.47), plastic(stove_c, 0.35, spec=0.4), bevel=0.03)
    kit.box(f"{name}.stovetop", (1.0, 0.84, 0.05), (sx, 3.43, 0.945), plastic("#2a2f38", 0.4, spec=0.3), bevel=0.01)
    for bxx in (-0.22, 0.22):
        for byy in (-0.15, 0.17):
            kit.cyl(f"{name}.burner{bxx}{byy}", 0.14, 0.02, (sx + bxx, 3.43 + byy, 0.98), plastic("#5a5f68", 0.4), n=14)
    kit.box(f"{name}.ovenwin", (0.7, 0.02, 0.32), (sx, 3.01, 0.42), plastic("#fff0cf", 0.3, spec=0.6), bevel=0.01)
    for k in range(4):
        kit.cyl(f"{name}.knob{k}", 0.035, 0.03, (sx - 0.3 + k * 0.2, 3.01, 0.82), plastic("#f4f4f2", 0.4), rot=(math.pi / 2, 0, 0), n=10)
    # a window over the counter
    kit.box(f"{name}.winframe", (1.9, 0.06, 1.4), (x0 + 2.5, 3.84, 1.9), plastic("#fffaf0", 0.6))
    kit.box(f"{name}.win", (1.7, 0.04, 1.2), (x0 + 2.5, 3.8, 1.9), kit.emit("#cfeaff", 1.5, "kwin"))
    # a table and chairs at the right
    wood = plastic("#d9a46a", 0.6, spec=0.1)
    kit.box(f"{name}.table", (1.5, 1.2, 0.07), (x0 + 3.0, 1.5, 0.76), wood, bevel=0.02)
    for tx in (-1, 1):
        for ty in (-1, 1):
            kit.box(f"{name}.tleg{tx}{ty}", (0.08, 0.08, 0.72), (x0 + 3.0 + tx * 0.65, 1.5 + ty * 0.5, 0.36), wood)
    kit.box(f"{name}.cloth", (1.1, 0.8, 0.02), (x0 + 3.0, 1.5, 0.8), plastic("#ffd23f", 0.7))
    for sgn in (-1, 1):
        cx_ = x0 + 3.0 + sgn * 1.15
        kit.box(f"{name}.chair{sgn}", (0.5, 0.5, 0.07), (cx_, 1.5, 0.45), wood, bevel=0.02)
        kit.box(f"{name}.chairb{sgn}", (0.07, 0.5, 0.55), (cx_ + sgn * 0.22, 1.5, 0.74), wood, bevel=0.02)
        for ty in (-1, 1):
            kit.box(f"{name}.chairl{sgn}{ty}", (0.06, 0.06, 0.42), (cx_ - sgn * 0.2, 1.5 + ty * 0.2, 0.21), wood)
    # the coffee maker
    cmx = x0 + 0.2
    kit.box(f"{name}.cm", (0.3, 0.3, 0.38), (cmx, 3.5, 1.13), plastic("#2a2f38", 0.4, spec=0.4), bevel=0.02)
    kit.cyl(f"{name}.cmpot", 0.09, 0.2, (cmx, 3.34, 1.0), kit.glass("#c9a070"), n=14)
    kit.box(f"{name}.cmlight", (0.04, 0.02, 0.04), (cmx + 0.09, 3.34, 1.25), kit.emit("#ff6a4a", 1.0, "cmled"))
    if ours:
        # the pill bottle by the coffee maker, a bread box beside the stove side, an apron on a hook
        W["pillx"] = x0 + 0.62
        W["pill"] = kit.empty("pill", (x0 + 0.62, 3.2, 0.94))
        kit.cyl("pill.body", 0.05, 0.13, (0, 0, 0.065), plastic("#ffffff", 0.35, spec=0.4), W["pill"], n=14)
        kit.cyl("pill.cap", 0.056, 0.04, (0, 0, 0.15), plastic("#e8a030", 0.4), W["pill"], n=14)
        kit.cyl("pill.band", 0.052, 0.045, (0, 0, 0.06), plastic("#f4a3a3", 0.4), W["pill"], n=14)
        W["pillhome"] = (x0 + 0.62, 3.2, 0.94)
        # a second bottle on the counter left of Mom, up only for the L03.2 kitchen beat
        W["pill0"] = kit.empty("pill0", (x0 - 1.72, 3.1, 0.94))
        kit.cyl("pill0.body", 0.05, 0.13, (0, 0, 0.065), plastic("#ffffff", 0.35, spec=0.4), W["pill0"], n=14)
        kit.cyl("pill0.cap", 0.056, 0.04, (0, 0, 0.15), plastic("#e8a030", 0.4), W["pill0"], n=14)
        kit.cyl("pill0.band", 0.052, 0.045, (0, 0, 0.06), plastic("#f4a3a3", 0.4), W["pill0"], n=14)
        W["pill0"].scale = (2.0, 2.0, 2.0)   # big enough to read at phone size
        W["pillbox"] = (x0 + 1.3, 3.18, 1.02)
        bx_ = x0 + 1.3
        kit.box("breadbox.body", (0.62, 0.42, 0.34), (bx_, 3.35, 1.11), plastic("#c98a4a", 0.6), bevel=0.03)
        kit.box("breadbox.slot", (0.46, 0.02, 0.2), (bx_, 3.139, 1.1), plastic("#2a1a10", 0.9))
        kit.box("breadbox.lid", (0.66, 0.46, 0.05), (bx_, 3.35, 1.3), plastic("#b57a3a", 0.6), bevel=0.02)
        kit.box("hook", (0.06, 0.1, 0.06), (x0 - 4.3, 3.8, 1.9), plastic("#4a4d52", 0.4))
        kit.box("apron.body", (0.46, 0.03, 0.62), (x0 - 4.3, 3.78, 1.55), plastic("#ffc94a", 0.7), bevel=0.01)
        kit.box("apron.bib", (0.28, 0.03, 0.3), (x0 - 4.3, 3.77, 1.95), plastic("#ffc94a", 0.7), bevel=0.01)
        kit.box("apron.tie", (0.5, 0.02, 0.05), (x0 - 4.3, 3.77, 1.5), plastic("#e8a030", 0.7))
        # the cookies for the tray later; the cat-free fridge
        kit.prop("kitchen_fridge", (x0 - 4.35, 3.0, 0), rot=0, height=1.9, tint="#f2f2f4")
    else:
        # a plate with a sandwich already out
        kit.cyl(f"{name}.plate", 0.2, 0.02, (x0 + 0.7, 3.2, 0.96), plastic("#ffffff", 0.3, spec=0.5), n=18)
        kit.box(f"{name}.bread1", (0.22, 0.2, 0.05), (x0 + 0.7, 3.2, 0.995), plastic("#e8b878", 0.7), bevel=0.02)
        kit.box(f"{name}.fill", (0.22, 0.2, 0.03), (x0 + 0.7, 3.2, 1.03), plastic("#7fb070", 0.7))
        kit.box(f"{name}.bread2", (0.22, 0.2, 0.05), (x0 + 0.7, 3.2, 1.065), plastic("#e8b878", 0.7), bevel=0.02)


def build(kit, story, tl):
    tl["cues"].sort(key=lambda c: c["t"])
    plastic = kit.plastic
    cream = plastic("#f6ecd8", 0.8, spec=0.05)
    wood = plastic("#a8744a", 0.7, spec=0.1)

    # ------------------------------------------------------------------ the sun and the fill
    sun = kit.light("sun", "SUN", (0, -30, 40), 1.0, "#fff0d0", size=0.06)
    sun.data.angle = 0.06
    fill = kit.light("fill", "SUN", (0, -30, 30), 1.0, "#fff2dc", shadow=False)
    fill.data.angle = 0.5
    kit.aim(fill, (0, 0, 0))
    front = kit.light("front", "SUN", (-10, -30, 20), 1.0, "#ffe6c0", shadow=False)
    front.data.angle = 0.4
    kit.aim(front, (0, 0, 0))
    kit.light("lt_office", "POINT", (G.OFFICE, -0.5, 3.2), 300.0, "#fff0d8", size=0.5, shadow=False)
    for nm, x in (("lt_mkit", G.MKIT), ("lt_dog", G.DOG), ("lt_land", G.LAND), ("lt_kit", G.KIT)):
        kit.light(nm, "POINT", (x, -0.5, 3.2), 520.0, "#fff0d8", size=0.5, shadow=False)
    kit.light("lt_party", "POINT", (G.PARTY, -2.5, 3.5), 300.0, "#fff4dc", size=0.5, shadow=False)
    # Grandpa's room: day, the TV (steady), the streetlight, a cold face fill
    kit.light("gpday", "POINT", (G.GP, -0.6, 3.2), 560.0, "#fff0d8", size=0.5, shadow=False)
    kit.light("gptv", "POINT", (G.GP - 2.2, 1.3, 1.4), 450.0, "#bfd8ff", size=0.5, shadow=False)
    kit.light("gpface", "POINT", (G.GP + 0.6, -1.6, 1.9), 150.0, "#aac4ff", size=0.6, shadow=False)
    kit.light("gpkey", "POINT", (G.GP + 1.0, -0.6, 1.7), 150.0, "#ffe6cc", size=0.5, shadow=False)
    kit.light("gpstreet", "POINT", (G.GP + 4.1, 0.5, 2.3), 160.0, "#dfe8ff", size=0.5, shadow=False)
    kit.light("bedday", "POINT", (G.BED, -0.5, 3.2), 420.0, "#fff0d8", size=0.5, shadow=False)
    kit.light("bedmoon", "POINT", (G.BED + 2.4, 0.5, 2.2), 380.0, "#a8c0ff", size=0.6, shadow=False)
    kit.light("bedlamp", "POINT", (G.BED - 1.2, 2.2, 1.1), 90.0, "#ffd9a0", size=0.3, shadow=False)

    ground = kit.grime("#f0d86c", 0.9, 1.4, "pgrass", 0.95)
    kit.plane("ground", (700, 700), (0, 0, 0), ground)

    # ------------------------------------------------------------------ the park
    px = G.PARK
    kit.box("path", (3.0, 70.0, 0.04), (px, 0, 0.03), plastic("#f6e8c4", 0.9, spec=0.05))
    kit.box("pathedge1", (0.2, 70.0, 0.05), (px - 1.6, 0, 0.03), plastic("#e8d6a8", 0.9))
    kit.box("pathedge2", (0.2, 70.0, 0.05), (px + 1.6, 0, 0.03), plastic("#e8d6a8", 0.9))
    for k, (x, y, tn) in enumerate([(-9, 6, "#c9e38a"), (10, 8, "#d8e98a"), (-12, -4, "#c9e38a"), (13, -6, "#bfe08a"),
                                    (-7, 22, "#d8e98a"), (8, 26, "#c9e38a"), (-15, 14, "#bfe08a"), (16, 18, "#d8e98a"),
                                    (-6, 38, "#c9e38a"), (7, 40, "#d8e98a")]):
        kit.prop("commontree_1" if k % 2 == 0 else "commontree_2", (x, y, 0), rot=k * 37, height=6.0 + (k % 3) * 0.8, tint=tn)
    for k in range(120):
        gx = (rnd(k, 1) - 0.5) * 26
        gy = -26 + rnd(k, 2) * 62
        if abs(gx) < 2.2:
            gx += 4.4 if gx >= 0 else -4.4
        kit.prop("grass", (gx, gy, 0), rot=rnd(k, 3) * 360, height=0.7 + 0.35 * rnd(k, 4), tint="#f5d764")
    for k in range(18):
        kit.prop("flowers", (-8 + k * 1.1, -3 + 3 * rnd(k, 5), 0), rot=rnd(k, 6) * 360, height=0.5, tint="#ffe48a")
    # a bench by the path
    kit.box("bench.seat", (1.8, 0.6, 0.1), (px + 3.4, -9.0, 0.5), wood, rot=(0, 0, math.pi / 2))
    kit.box("bench.back", (0.1, 1.8, 0.7), (px + 3.85, -9.0, 0.85), wood)
    for sy in (-1, 1):
        kit.box(f"bench.leg{sy}", (0.5, 0.1, 0.5), (px + 3.4, -9.0 + sy * 0.8, 0.25), kit.metal("#4a4d52", 0.5))
    for k in range(6):
        h = 18 + k * 9
        kit.prop(["sub_building_type_a", "sub_building_type_c", "sub_building_type_f", "sub_building_type_k", "sub_building_type_p",
                  "sub_building_type_a"][k], (-30 + k * 12, 52, 0), rot=180, height=5.5 + (k % 2), tint=["#f4c8b8", "#f8e0a0", "#c8e8c8", "#c8dcf4", "#f4c8e0", "#f8d8a8"][k])

    # ------------------------------------------------------------------ the downtown street
    sx = G.STREET
    kit.plane("road", (110, 8.0), (sx, 0, 0.03), plastic("#9a9fb0", 0.9, spec=0.05))
    kit.plane("walkS", (110, 3.0), (sx, -5.5, 0.05), plastic("#f1e4cc", 0.9, spec=0.05))
    kit.plane("walkN", (110, 3.0), (sx, 5.5, 0.05), plastic("#f1e4cc", 0.9, spec=0.05))
    for k in range(9):
        x = sx - 48 + k * 12
        kit.prop(["sub_building_type_a", "sub_building_type_c", "sub_building_type_f", "sub_building_type_k", "sub_building_type_p"][k % 5],
                 (x, 12.0, 0), rot=180, height=5.4 + (k % 3) * 0.7, tint=["#f4c8b8", "#f8e0a0", "#c8e8c8", "#c8dcf4", "#f4c8e0"][(k + 2) % 5])
        if k % 2 == 0:
            kit.prop("sub_tree_large", (x + 6, 7.4, 0), height=4.2, tint="#d4eb9a")
    for k in range(4):
        kit.prop("bldg_2story", (sx - 40 + k * 28, 30.0, 0), rot=180, height=9, tint=["#f8d8a8", "#c8e8c8", "#f4c8e0", "#c8dcf4"][k])
    # a car at the kerb (S20b): body, cabin, wheels, a windshield
    cx_, cy_ = sx + 9.0, -3.2
    kit.box("car.body", (4.2, 1.8, 0.7), (cx_, cy_, 0.65), plastic("#e8493a", 0.35, spec=0.5), bevel=0.12)
    kit.box("car.cabin", (2.3, 1.7, 0.6), (cx_ - 0.2, cy_, 1.25), plastic("#e8493a", 0.35, spec=0.5), bevel=0.12)
    kit.box("car.glassF", (0.04, 1.5, 0.5), (cx_ + 0.98, cy_, 1.27), kit.glass("#cfe6ff"), rot=(0, 0.45, 0))
    kit.box("car.glassS", (2.0, 0.04, 0.46), (cx_ - 0.2, cy_ - 0.86, 1.27), kit.glass("#cfe6ff"))
    for wx in (-1.3, 1.3):
        for wy in (-1, 1):
            kit.cyl(f"car.wheel{wx}{wy}", 0.36, 0.22, (cx_ + wx, cy_ + wy * 0.88, 0.36), plastic("#2a2a30", 0.8),
                    rot=(math.pi / 2, 0, 0), n=14)
    W["carpos"] = (cx_, cy_)
    kit.box("car.pollen", (0.03, 1.5, 0.5), (cx_ + 1.0, cy_, 1.27), kit.emit("#ffd75a", 0.35, "carpollen"), rot=(0, 0.45, 0))

    # ------------------------------------------------------------------ the office: glass, a long white table
    ox = G.OFFICE
    room(kit, ox, kit.plastic("#b4c7d6", 0.35, spec=0.4), kit.plastic("#aab4c0", 0.5, spec=0.3), "office")
    for k in range(5):
        kit.box(f"office.mull{k}", (0.12, 0.1, 3.5), (ox - 4 + k * 2.0, 3.8, 1.75), plastic("#ffffff", 0.5))
    kit.box("office.rail", (10, 0.1, 0.12), (ox, 3.8, 2.2), plastic("#ffffff", 0.5))
    kit.box("office.table", (3.6, 1.3, 0.08), (ox, 1.0, 0.78), plastic("#b8c0ca", 0.4, spec=0.3), bevel=0.02)
    for tx in (-1, 1):
        kit.box(f"office.tleg{tx}", (0.1, 1.1, 0.74), (ox + tx * 1.6, 1.0, 0.37), plastic("#c9d2dc", 0.4))
    kit.box("office.laptop", (0.5, 0.35, 0.03), (ox - 0.8, 0.9, 0.84), plastic("#4a4f5a", 0.4))
    kit.box("office.screen", (0.5, 0.03, 0.34), (ox - 0.8, 1.06, 1.0), plastic("#303642", 0.4), rot=(-0.2, 0, 0))
    kit.box("office.plant", (0.22, 0.22, 0.2), (ox + 1.4, 1.0, 0.9), plastic("#e8845a", 0.6))
    kit.sphere("office.plantl", 0.2, (ox + 1.4, 1.0, 1.15), plastic("#5fae4a", 0.8), seg=8)
    kit.box("office.rug", (4.5, 3.0, 0.02), (ox, 1.2, 0.04), plastic("#8ec9ff", 0.9))

    # ------------------------------------------------------------------ the two kitchens
    kitchen(kit, G.MKIT, "mk", plastic("#c8e8c8", 0.85, spec=0.05), kit.checker("#f6ecd8", "#e8dcc0", 0.9), "#7fb070", "#e8845a", ours=False)
    kitchen(kit, G.KIT, "ok", plastic("#ffeccd", 0.85, spec=0.05), kit.planks("#d9a46a", "#c98f58", 1.0), "#f6e2c0", "#3b7fd0", ours=True)
    kit.plane("ok.tile", (6, 3), (G.KIT - 1.0, 0.3, 0.05), kit.checker("#f6ecd8", "#cfe6ff", 0.8))

    # ------------------------------------------------------------------ the dog's room
    dx = G.DOG
    room(kit, dx, plastic("#ffe0a8", 0.85, spec=0.05), kit.planks("#d9a46a", "#c98f58", 1.0), "dog")
    kit.box("dog.winframe", (2.0, 0.06, 1.5), (dx + 2.6, 3.84, 1.9), plastic("#fffaf0", 0.6))
    kit.box("dog.win", (1.8, 0.04, 1.3), (dx + 2.6, 3.8, 1.9), kit.emit("#cfeaff", 1.5, "dogwin"))
    bedm = plastic("#d9534f", 0.9)
    kit.box("dogbed.rim", (2.3, 1.6, 0.26), (dx, 1.6, 0.13), bedm, bevel=0.1)
    kit.box("dogbed.in", (1.9, 1.2, 0.3), (dx, 1.6, 0.17), plastic("#ffe9c8", 0.95), bevel=0.08)
    dm = plastic("#c98a4a", 0.8)
    dd = plastic("#8a5a2c", 0.8)
    W["dog"] = kit.empty("dog", (dx + 1.45, 1.55, 0.0))
    d_ = W["dog"]
    kit.box("dog.body", (0.55, 0.95, 0.5), (0, 0, 0.62), dm, d_, bevel=0.1)
    kit.box("dog.head", (0.4, 0.4, 0.4), (0, -0.55, 0.98), dm, d_, bevel=0.08)
    kit.box("dog.snout", (0.22, 0.2, 0.18), (0, -0.78, 0.9), dd, d_, bevel=0.05)
    kit.box("dog.nose", (0.08, 0.04, 0.06), (0, -0.89, 0.95), plastic("#1c120c", 0.5), d_)
    for sx_ in (-1, 1):
        kit.box(f"dog.ear{sx_}", (0.1, 0.18, 0.3), (sx_ * 0.24, -0.5, 1.02), dd, d_, bevel=0.04)
        kit.box(f"dog.eye{sx_}", (0.06, 0.03, 0.06), (sx_ * 0.1, -0.745, 1.03), plastic("#1c120c", 0.5), d_)
        for sy_ in (-1, 1):
            kit.box(f"dog.leg{sx_}{sy_}", (0.16, 0.16, 0.4), (sx_ * 0.19, -0.3 * -sy_ * 1.0, 0.2), dm, d_, bevel=0.04)
    W["tail"] = kit.empty("dog.tailg", (0, 0.5, 0.8), d_)
    kit.box("dog.tail", (0.1, 0.1, 0.5), (0, 0.05, 0.2), dd, W["tail"], bevel=0.04)

    # ------------------------------------------------------------------ the backyard party
    qx = G.PARTY
    kit.plane("party.lawn", (14, 11), (qx, 0.5, 0.035), plastic("#b9d86a", 0.9, spec=0.05))
    for k in range(7):
        kit.prop("sub_fence", (qx - 6.0 + k * 2.0, 4.2, 0), height=1.3, tint="#fff4e0")
    for k in range(3):
        kit.prop("commontree_1", (qx - 6 + k * 6, 8.5, 0), rot=k * 60, height=6.5, tint="#c9e38a")
    for k in range(14):
        bcol = ["#ffd23f", "#e8493a", "#8ec9ff", "#ff9fc0", "#7fd08a"][k % 5]
        kit.box(f"flag{k}", (0.22, 0.02, 0.26), (qx - 3.9 + k * 0.6, 3.6, 2.4 - 0.35 * math.sin(math.pi * k / 13)), plastic(bcol, 0.6), rot=(0, 0.3 * ((k % 2) - 0.5), 0))
    kit.box("party.table", (2.4, 0.9, 0.06), (qx + 2.8, 2.2, 0.8), plastic("#ffffff", 0.5), bevel=0.02)
    for tx in (-1, 1):
        kit.box(f"party.tleg{tx}", (0.08, 0.7, 0.78), (qx + 2.8 + tx * 1.1, 2.2, 0.39), plastic("#c9d2dc", 0.4))
    kit.cyl("party.cake", 0.22, 0.2, (qx + 2.8, 2.2, 0.93), plastic("#ffd1dc", 0.6), n=16)
    kit.cyl("party.candle", 0.015, 0.1, (qx + 2.8, 2.2, 1.08), plastic("#8ec9ff", 0.6), n=8)
    for k in range(5):
        c_ = ["#e8493a", "#ffd23f", "#8ec9ff", "#7fd08a", "#ff9fc0"][k]
        kit.cyl(f"balloon{k}.str", 0.008, 1.4, (qx - 3.2 + k * 0.45, 3.0, 0.7), plastic("#ffffff", 0.5), n=5)
        kit.sphere(f"balloon{k}", 0.3, (qx - 3.2 + k * 0.45, 3.0, 1.7 + 0.15 * (k % 2)), plastic(c_, 0.25, spec=0.6), seg=12)

    # ------------------------------------------------------------------ the landlord's living room
    lx = G.LAND
    room(kit, lx, plastic("#f2d6c0", 0.85, spec=0.05), kit.planks("#b98a5a", "#a87848", 1.0), "land")
    plaid = kit.checker("#c0543a", "#f1e4cc", 4.0, "plaid")
    sofa(kit, "land.couch", lx - 1.7, 2.6, 2.4, plaid)
    armchair(kit, "land.arm", lx + 2.0, 2.6, "#8a5a3a")
    kit.box("land.coffee", (1.0, 0.6, 0.06), (lx + 0.15, 1.7, 0.4), wood, bevel=0.02)
    for tx in (-1, 1):
        kit.box(f"land.cleg{tx}", (0.06, 0.5, 0.38), (lx + 0.15 + tx * 0.42, 1.7, 0.19), wood)
    kit.box("land.winframe", (2.0, 0.06, 1.5), (lx + 0.5, 3.84, 2.0), plastic("#fffaf0", 0.6))
    kit.box("land.win", (1.8, 0.04, 1.3), (lx + 0.5, 3.8, 2.0), kit.emit("#cfeaff", 1.5, "landwin"))
    kit.prop("houseplant_1", (lx - 4.2, 3.4, 0), height=0.9)

    # ------------------------------------------------------------------ Grandpa's front room: deep green and cream
    gx = G.GP
    room(kit, gx, plastic("#f2e6c8", 0.9, spec=0.04), kit.planks("#8a5a32", "#74482a", 1.0), "gp", wide=10.0, hgt=3.5)
    # ceiling (was open: cameras tilting up saw a black void); sits on the wall tops, reaches back past the lens
    kit.box("gp.ceiling", (10.3, 16.0, 0.1), (gx, -3.0, 3.55), plastic("#efe3c4", 0.95, spec=0.04))
    wain = plastic("#2f6b4a", 0.8, spec=0.08)
    kit.box("gp.wain", (10.0, 0.06, 0.9), (gx, G.WALL_Y - 0.17, 0.5), wain)
    kit.box("gp.wainrail", (10.0, 0.08, 0.06), (gx, G.WALL_Y - 0.17, 0.97), plastic("#e9dcb0", 0.7))
    for sx_ in (-1, 1):
        kit.box(f"gp.wains{sx_}", (0.06, 9.0, 0.9), (gx + sx_ * 4.82, 0.5, 0.5), wain)
    kit.box("gp.rug", (6.2, 3.4, 0.02), (gx + 0.2, 0.6, 0.04), plastic("#f6ecd0", 0.95))
    kit.box("gp.rugedge", (6.0, 3.2, 0.021), (gx + 0.2, 0.6, 0.06), plastic("#e9dcb0", 0.95))
    kit.box("gp.rugin", (5.7, 2.9, 0.022), (gx + 0.2, 0.6, 0.08), plastic("#f6ecd0", 0.95))
    armchair(kit, "gp.arm", gx + 1.6, 2.0, "#2f6b4a")
    sofa(kit, "gp.sofa", gx - 0.4, 2.0, 2.3, plastic("#c98a3a", 0.85, spec=0.08))
    kit.box("gp.t1top", (1.6, 0.9, 0.05), (gx + 0.1, 1.0, 0.55), wood, bevel=0.015)
    for tx in (-1, 1):
        for ty in (-1, 1):
            kit.box(f"gp.t1leg{tx}{ty}", (0.07, 0.07, 0.52), (gx + 0.1 + tx * 0.7, 1.0 + ty * 0.36, 0.26), wood)
    tea_tray(kit, gx - 0.25, 1.0, 0.575, "gp.tray")
    # cookies, then a small cake with one candle, on the table beside the tray (a cue shows one or the other)
    W["cookies"] = kit.empty("cookies", (gx + 0.45, 1.0, 0.575))
    kit.cyl("cookies.plate", 0.19, 0.02, (0, 0, 0.01), plastic("#ffffff", 0.3, spec=0.5), W["cookies"], n=16)
    for k in range(5):
        a = k * 1.256
        kit.cyl(f"cookies.c{k}", 0.055, 0.025, (0.09 * math.cos(a), 0.09 * math.sin(a), 0.035), plastic("#b9783a", 0.8), W["cookies"], n=10)
        kit.box(f"cookies.chip{k}", (0.02, 0.02, 0.01), (0.09 * math.cos(a), 0.09 * math.sin(a), 0.052), plastic("#4a2a14", 0.8), W["cookies"])
    W["cake"] = kit.empty("cake", (gx + 0.45, 1.0, 0.575))
    kit.cyl("cake.plate", 0.2, 0.02, (0, 0, 0.01), plastic("#ffffff", 0.3, spec=0.5), W["cake"], n=16)
    kit.cyl("cake.body", 0.14, 0.12, (0, 0, 0.08), plastic("#ffd1dc", 0.6), W["cake"], n=16)
    kit.cyl("cake.icing", 0.145, 0.03, (0, 0, 0.145), plastic("#fffaf0", 0.5), W["cake"], n=16)
    kit.cyl("cake.candle", 0.012, 0.09, (0, 0, 0.2), plastic("#8ec9ff", 0.6), W["cake"], n=8)
    kit.sphere("cake.flame", 0.02, (0, 0, 0.26), kit.emit("#ffcf6e", 3.0, "cakeflame"), W["cake"], seg=8)
    kit.cyl("gp.t2top", 0.35, 0.05, (gx + 2.85, 2.0, 0.62), wood, n=16)
    kit.cyl("gp.t2leg", 0.06, 0.6, (gx + 2.85, 2.0, 0.3), wood, n=10)
    # the framed photo of young Mom at a stove in a yellow apron (no text)
    fx, fy, fz = gx + 2.78, 2.0, 0.65
    zc = fz + 0.36
    P = lambda nm, size, dx, dz, dy, col, **kw: kit.box(nm, size, (fx + dx, fy - dy, zc + dz), plastic(col, 0.7), **kw)
    kit.box("frame.f", (0.58, 0.04, 0.7), (fx, fy - 0.1, zc), plastic("#d9a441", 0.3, spec=0.7), bevel=0.01)
    P("frame.bg", (0.5, 0.01, 0.62), 0, 0, 0.125, "#cfe6ff")
    P("frame.stove", (0.5, 0.01, 0.24), 0, -0.19, 0.136, "#3b7fd0")
    P("frame.stovetop", (0.5, 0.01, 0.04), 0, -0.065, 0.146, "#2a2f38")
    P("frame.oven", (0.26, 0.01, 0.1), 0, -0.2, 0.147, "#fff0cf")
    P("frame.pot", (0.12, 0.01, 0.07), -0.17, -0.025, 0.147, "#8a8f98")
    P("frame.hairback", (0.24, 0.01, 0.2), 0, 0.185, 0.14, "#9a7a45", bevel=0.01)
    P("frame.apron", (0.2, 0.01, 0.2), 0, 0.0, 0.152, "#ffc94a")
    P("frame.head", (0.15, 0.01, 0.15), 0, 0.17, 0.158, "#e6b48c", bevel=0.01)
    P("frame.fringe", (0.17, 0.01, 0.05), 0, 0.255, 0.166, "#9a7a45", bevel=0.005)
    for sx_ in (-1, 1):
        P(f"frame.eye{sx_}", (0.022, 0.01, 0.03), sx_ * 0.037, 0.18, 0.168, "#1c120c")
    P("frame.smile", (0.06, 0.01, 0.014), 0, 0.115, 0.168, "#7a3a30")
    kit.cyl("gp.lamp", 0.06, 0.3, (gx + 3.5, 2.5, 0.8), plastic("#f6ecd8", 0.5), n=10)
    kit.cyl("gp.lampshade", 0.16, 0.2, (gx + 3.5, 2.5, 1.05), plastic("#ffe6a8", 0.7), n=14, r2=0.1)
    # the TV on a cart at the west wall, facing +x; its screen is a separate plane so it can fade up
    tvx, tvy, tha = gx - 2.9, 1.7, math.radians(-38)

    def tvp(nm, size, dx, dz, mat, bev=0.0):
        c, sn = math.cos(tha), math.sin(tha)
        return kit.box(nm, size, (tvx + dx * c, tvy + dx * sn, dz), mat, rot=(0, 0, tha), bevel=bev)
    tvp("gp.cart", (0.7, 1.3, 0.6), 0, 0.3, wood, 0.02)
    tvp("gp.tv", (0.22, 1.1, 0.7), -0.05, 0.95, plastic("#22252c", 0.4, spec=0.3), 0.02)
    W["tvmat"] = kit.emit("#bfd8ff", 3.0, "tvglow")
    tvp("gp.screen", (0.02, 0.96, 0.56), 0.08, 0.95, W["tvmat"])
    # the big window (east wall): a pane that goes from sky to night
    kit.box("gp.winframe", (0.06, 2.6, 1.9), (gx + 4.84, 1.5, 1.9), plastic("#fffaf0", 0.6))
    W["winmat"] = kit.emit("#cfeaff", 1.6, "gpwin")
    kit.box("gp.win", (0.04, 2.4, 1.7), (gx + 4.8, 1.5, 1.9), W["winmat"])
    kit.box("gp.winbar", (0.05, 0.06, 1.7), (gx + 4.79, 1.5, 1.9), plastic("#fffaf0", 0.6))
    clippings(kit, gx)
    for sx_ in (-1, 1):
        kit.prop("houseplant_1", (gx + sx_ * 4.3, 3.3, 0), height=0.8)

    # ------------------------------------------------------------------ the bedroom
    bx = G.BED
    room(kit, bx, plastic("#cfe6ff", 0.85, spec=0.05), kit.planks("#d9a46a", "#c98f58", 1.0), "bed")
    kit.box("bed.frame", (1.9, 2.3, 0.3), (bx, 2.5, 0.25), wood, bevel=0.04)
    kit.box("bed.mattress", (1.8, 2.2, 0.22), (bx, 2.5, 0.5), plastic("#ffffff", 0.9), bevel=0.05)
    kit.box("bed.head", (1.9, 0.12, 1.1), (bx, 3.62, 0.75), wood, bevel=0.04)
    kit.box("bed.pillow", (0.8, 0.4, 0.14), (bx, 3.3, 0.67), plastic("#ffd23f", 0.9), bevel=0.06)
    kit.box("bed.blanket", (1.8, 1.2, 0.16), (bx, 2.0, 0.6), plastic("#8ec9ff", 0.9), bevel=0.06)
    kit.box("bed.stand", (0.6, 0.5, 0.55), (bx - 1.5, 3.4, 0.28), wood, bevel=0.03)
    # the clock: a round face at 2:00 (no numerals, just ticks), on the stand
    cl = kit.empty("clock", (bx - 1.5, 3.12, 0.95))
    kit.cyl("clock.face", 0.2, 0.05, (0, 0, 0), plastic("#fffaf0", 0.4), cl, rot=(math.pi / 2, 0, 0), n=24)
    kit.cyl("clock.rim", 0.225, 0.04, (0, 0.012, 0), plastic("#e8493a", 0.4), cl, rot=(math.pi / 2, 0, 0), n=24)
    for k in range(12):
        a = k * math.pi / 6
        kit.box(f"clock.tick{k}", (0.016, 0.01, 0.04 if k % 3 else 0.06), (0.16 * math.sin(a), -0.04, 0.16 * math.cos(a)),
                plastic("#2a2f38", 0.5), cl, rot=(0, a, 0))
    kit.box("clock.hour", (0.022, 0.012, 0.11), (0.05 * math.sin(math.pi / 3), -0.05, 0.05 * math.cos(math.pi / 3)), plastic("#2a2f38", 0.5), cl, rot=(0, math.pi / 3, 0))
    kit.box("clock.min", (0.014, 0.012, 0.16), (0, -0.06, 0.07), plastic("#2a2f38", 0.5), cl)
    kit.box("bed.winframe", (1.9, 0.06, 1.6), (bx + 2.6, 3.84, 1.9), plastic("#fffaf0", 0.6))
    kit.box("bed.win", (1.7, 0.04, 1.4), (bx + 2.6, 3.8, 1.9), kit.emit("#1c2a58", 0.8, "bedwin"))

    pollen_swirl_pool(kit)
    build_tag(kit)
    return {}


# ---------------------------------------------------------------------------------------------- the rule meter
SEG = {  # a b c d e f g
    "6": "acdefg", "3": "abcdg", "4": "bcfg", "5": "acdfg", "2": "abdeg", "0": "abcdef", "1": "bc", "7": "abc", "8": "abcdefg", "9": "abcdfg",
}


def build_tag(kit):
    """The rule meter: a cream tag on the camera. Left: a pollen glyph (a gold flower) over five lit dots. Middle: the
    sneeze count in seven-segment digits. Right: a map pin (grey, green when I've landed) and a second pin later."""
    cam = kit.OBJ["cam"]
    root = kit.empty("tag", (0, 0, 0), cam)
    W["tag"] = root
    cream = kit.emit("#fbf1d6", 0.9, "tagcream")
    edge = kit.emit("#4a2e12", 0.5, "tagedge")
    ink = kit.emit("#3a2210", 0.5, "tagink")
    gold = kit.emit("#ffbf1f", 1.0, "taggold")
    orange = kit.emit("#f08a1e", 0.9, "tagorange")

    def b(name, size, loc, mat, rot=0.0):
        ob = kit.box(name, size, loc, mat, root, rot=(0, 0, rot))
        noshadow(ob)
        return ob

    b("tag.edge", (1.0, 0.64, 0.004), (0, 0, 0.0), edge)
    b("tag.plate", (0.95, 0.58, 0.004), (0, 0, 0.004), cream)
    # pollen glyph: six petals round a core
    gxc, gyc = -0.32, 0.1
    for k in range(6):
        a = k * math.pi / 3
        ob = kit.cyl(f"tag.pet{k}", 0.055, 0.004, (gxc + 0.085 * math.cos(a), gyc + 0.085 * math.sin(a), 0.008), orange, root, rot=(0, 0, 0), n=10)
        noshadow(ob)
    ob = kit.cyl("tag.core", 0.075, 0.004, (gxc, gyc, 0.012), gold, root, n=14)
    noshadow(ob)
    for k in range(5):
        ob = kit.cyl(f"tag.dot{k}", 0.032, 0.004, (gxc - 0.12 + k * 0.06, -0.14, 0.008), gold, root, n=10)
        noshadow(ob)
    # the count: two seven-segment digits
    W["segs"] = []
    for d, dx in enumerate((-0.08, 0.1)):
        row = {}
        for s_, (sx_, sy_, hor) in {"a": (0, 0.14, 1), "g": (0, 0, 1), "d": (0, -0.14, 1), "f": (-0.055, 0.07, 0),
                                    "b": (0.055, 0.07, 0), "e": (-0.055, -0.07, 0), "c": (0.055, -0.07, 0)}.items():
            size = (0.085, 0.034, 0.004) if hor else (0.034, 0.1, 0.004)
            row[s_] = b(f"tag.d{d}{s_}", size, (dx + sx_, 0.03 + sy_, 0.008), ink)
        W["segs"].append(row)
    # pins
    W["pinmats"] = []
    W["pins"] = []
    for k, px_ in enumerate((0.33, 0.44)):
        m = kit.emit("#8a8a8a", 0.9, f"tagpin{k}")
        W["pinmats"].append(m)
        p = kit.empty(f"tag.pin{k}", (px_, 0.04, 0.008), root)
        s = kit.cyl(f"tag.pinb{k}", 0.058, 0.004, (0, 0.04, 0), m, p, n=14)
        cn = kit.box(f"tag.pinc{k}", (0.082, 0.082, 0.004), (0, -0.012, 0), m, p, rot=(0, 0, math.pi / 4))
        hole = kit.cyl(f"tag.pinh{k}", 0.022, 0.004, (0, 0.04, 0.004), cream, p, n=10)
        for o in (s, cn, hole):
            noshadow(o)
        W["pins"].append(p)


def _adopt(parent, ob):
    """A head part made after the first pose starts hidden when its head is (nobody is at the origin on frame 0)."""
    ob.hide_render = parent.hide_render
    return ob


def _first_frame(kit, story):
    from blocky import faces
    R, H = faces.HEAD_R, faces.HEAD_H
    gh = bpy.data.objects.get("grandpa.headg")
    if gh is not None:
        m = kit.plastic("#f4f4f0", 0.9)
        _adopt(gh, kit.box("grandpa.brow", (0.95, 0.07, 0.09), (0, -R - 0.03, 0.15), m, gh, bevel=0.02))
        # clear pale lenses (the stock glass mirrors the dark room and reads black): see-through, so the eyes show
        lm = kit.plastic("#dfe8ec", 0.2)
        lm.node_tree.nodes["Principled BSDF"].inputs["Alpha"].default_value = 0.22
        for sx in (-1, 1):
            lo = bpy.data.objects.get(f"grandpa.gl{sx}")
            if lo is not None:
                lo.data.materials.clear()
                lo.data.materials.append(lm)
        _adopt(gh, kit.box("grandpa.tuft", (0.28, 0.06, 0.1), (0, -R - 0.04, -0.36), m, gh, bevel=0.02))
    mh = bpy.data.objects.get("mom.headg")
    if mh is not None:
        sil = kit.plastic("#cfcfd6", 0.5, spec=0.3)
        for sx in (-1, 1):
            _adopt(mh, kit.box(f"mom.temple{sx}", (0.1, 0.46, 0.4), (sx * (R + 0.01), -0.12, H / 2 - 0.42), sil, mh, bevel=0.03))
    W["holds"] = {}
    for who, sx in (("me", 1), ("mom", 1), ("landlord", 1)):
        arm = bpy.data.objects.get(f"{who}.arm{sx}")
        if arm is None:
            continue
        c = kit.plastic("#f6ecd8" if who != "landlord" else "#e8493a", 0.35, spec=0.5)
        ob = kit.cyl(f"{who}.hcup", 0.26, 0.34, (0, -0.72, -1.78), c, arm, n=14, r2=0.21)
        h2 = kit.box(f"{who}.hcuph", (0.1, 0.2, 0.2), (0.3, -0.72, -1.78), c, arm)
        h2.parent = arm
        W["holds"][who] = [ob, h2]
    W["inited"] = True


def _hide(ob, hide):
    ob.hide_render = hide
    for c in ob.children_recursive:
        c.hide_render = hide


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
    night = look["night"]
    gains["sun"], gains["fill"], gains["front"] = look["sun"], look["fill"], look["front"]
    for nm in ("lt_office", "lt_mkit", "lt_dog", "lt_party", "lt_land", "lt_kit", "bedday"):
        gains[nm] = 1.0
    gains["gpday"] = 1.0 - night
    gains["bedday"] = 1.0 - night
    tv = sample("tv", tl, t, {"v": 0.0})["v"]
    gains["gptv"] = 0.14 * tv * night
    gains["gpkey"] = 1.2 * night * (0.55 + 0.45 * tv)
    gains["gpface"] = 0.2 * night * (0.35 + 0.65 * tv)
    gains["gpstreet"] = 0.15 * night * (0.4 + 0.6 * tv)
    gains["bedmoon"] = 0.35 * night
    gains["bedlamp"] = 0.5 * night
    if "wallobs" not in W:
        W["wallobs"] = [o for o in bpy.data.objects if o.name.startswith(("clip", "portrait"))]
    wall_on = sample("wall", tl, t, {"v": 0.0})["v"] > 0.5
    for o in W["wallobs"]:
        o.hide_render = not wall_on
    W["tvmat"].node_tree.nodes["Emission"].inputs["Strength"].default_value = 0.25 + 3.2 * tv * night
    W["winmat"].node_tree.nodes["Emission"].inputs["Strength"].default_value = 1.6 * (1 - night) + 0.5 * night
    w = bpy.context.scene.world
    bg = w.node_tree.nodes["Background"]
    bg.inputs["Color"].default_value = (*look["sky"], 1.0)
    bg.inputs["Strength"].default_value = look["sky_str"]

    # the current shot, its lens and its target (for the tag size and the pollen)
    lens, tgt = 40.0, Vector((0, 0, 1.5))
    shot = next((s for s in tl["shots"] if s["start"] <= t < s["end"]), tl["shots"][-1])
    spec = next((s for s in story["shots"] if s["id"] == shot["id"]), None)
    if spec:
        keys = spec["cam"]
        u = (t - shot["start"]) / max(1e-6, shot["end"] - shot["start"])
        lens, tgt = keys[0][3], Vector(keys[0][2])
        if len(keys) > 1:
            for a, b in zip(keys, keys[1:]):
                if u <= b[0]:
                    k = ss((u - a[0]) / max(1e-6, b[0] - a[0]))
                    lens = a[3] + (b[3] - a[3]) * k
                    tgt = Vector(a[2]).lerp(Vector(b[2]), k)
                    break
            else:
                lens, tgt = keys[-1][3], Vector(keys[-1][2])
    # the tag, in the top-left corner at a fixed angular size
    h2 = 12.0 / lens
    w2 = h2 * 9.0 / 16.0
    tag = W["tag"]
    s = 0.62 * w2
    tag.scale = (s, s, s)
    tag.location = (-0.6 * w2, 0.7 * h2, -1.0)
    # count digits
    ct = sample("count", tl, t, {"n": 63.0})
    n = int(round(ct["n"]))
    for dgt, ch in enumerate(f"{n:02d}"[-2:]):
        on = SEG[ch]
        for k, ob in W["segs"][dgt].items():
            ob.hide_render = k not in on
    # pins: the first goes green on a landing and pulses; the second appears later
    pn = sample("pin", tl, t, {"v": 0.0, "v2": 0.0})
    grey, green = kit_col("#8a8a8a"), kit_col("#2fb06a")
    pulse = 0.0
    for c in tl["cues"]:
        if c["name"] == "pin" and c["t"] <= t < c["t"] + 1.6 and c.get("v", 0) > 0.5:
            pulse = max(pulse, math.sin((t - c["t"]) * 9.0) * math.exp(-(t - c["t"]) * 1.4))
    for k, (m, p) in enumerate(zip(W["pinmats"], W["pins"])):
        v = pn["v"] if k == 0 else pn["v2"]
        e = m.node_tree.nodes["Emission"]
        e.inputs["Color"].default_value = (*[grey[i] + (green[i] - grey[i]) * v for i in range(3)], 1.0)
        p.hide_render = (k == 1 and pn["v2"] < 0.02)
        sc = 1.0 + 0.16 * pulse * (1 if k == 0 else 0)
        p.scale = (sc, sc, sc)

    # pollen in the air near whatever the shot is looking at (outdoors only), a soft drift
    outdoors = (tgt.x < 95) or (215 < tgt.x < 245)
    pl = sample("pollen", tl, t, {"level": 1.0})["level"]
    nvis = int(len(W["sp"]) * min(1.0, 0.45 * pl)) if outdoors else 0
    for i, ob in enumerate(W["sp"]):
        if i >= nvis:
            ob.location = (0, 0, -50)
            continue
        ox = (rnd(i, 1) - 0.5) * 7.0
        oy = (rnd(i, 2) - 0.35) * 8.0
        oz = (rnd(i, 3) - 0.35) * 3.6
        dr = 0.25 * math.sin(0.55 * t + rnd(i, 4) * 6.3)
        ob.location = (tgt.x + ox + dr, tgt.y + oy, max(0.1, tgt.z + oz + 0.2 * math.sin(0.4 * t + rnd(i, 5) * 6.3)))

    # the soft gold swirl a sneeze leaves (vanish or landing): dense at once, thinning over ~1 s
    allsw = [c for c in tl["cues"] if c["name"] == "swirl"]
    for ob in W["sw"]:
        ob.location = (0, 0, -50)
    for ci, sw in enumerate(allsw):
        du = sw.get("dur", 1.0)
        if not (sw["t"] <= t < sw["t"] + du):
            continue
        u = (t - sw["t"]) / du
        grp = (ci % 3) * 32
        szf = sw.get("sz", 1.4)
        for j in range(32):
            i = grp + j
            ob = W["sw"][i]
            r0 = (0.5 + 0.5 * rnd(i, 1)) * sw.get("wide", 1.0)
            ang = rnd(i, 2) * 6.283 + 4.0 * u * (1 if i % 2 else -1)
            rad = r0 * (0.8 + 1.2 * u)
            z = sw["z"] + (rnd(i, 3) - 0.5) * sw.get("tall", 1.7) + 0.6 * u
            ob.location = (sw["x"] + rad * math.cos(ang), sw["y"] + rad * math.sin(ang) * 0.6, max(0.05, z))
            k = max(0.02, (1.0 - ss(u)) ** 0.8) * (0.7 + 0.6 * rnd(i, 4)) * szf
            ob.scale = (k, k, k)

    # nothing gold floats through a face: push every particle out of any visible head
    heads = [o for o in bpy.data.objects if ".headm" in o.name and not o.hide_render and o.type == "MESH"]
    if heads:
        bpy.context.view_layer.update()
        hs = []
        for o in heads:
            pts = [o.matrix_world @ Vector(c) for c in o.bound_box]
            ctr = sum(pts, Vector()) / 8.0
            hs.append((ctr, max((p - ctr).length for p in pts) + 0.05))
        for ob in W["sw"] + W["sp"]:
            if ob.location.z < -10:
                continue
            rr = max(ob.scale.x, 1.0) * ob.dimensions.x * 0.5 if False else 0.0
            for ctr, hr in hs:
                dv = ob.location - ctr
                lim = hr + 0.2
                if dv.length < lim:
                    if dv.length < 1e-4:
                        dv = Vector((1, 0, 0))
                    ob.location = ctr + dv.normalized() * lim

    # the pill bottle slides into the bread box
    pb = sample("pillpos", tl, t, {"u": 0.0})["u"]
    if W.get("pill") is not None:
        h = Vector(W["pillhome"])
        e = Vector(W["pillbox"])
        # slide along the counter front, lift to the slot, then push in through the slot
        mid = Vector((e.x, h.y - 0.16, e.z))
        if pb < 0.55:
            loc = h.lerp(mid, ss(pb / 0.55))
        else:
            loc = mid.lerp(e, ss((pb - 0.55) / 0.45))
        W["pill"].location = loc
        _hide(W["pill"], pb >= 0.99)
    if W.get("pill0") is not None:
        _hide(W["pill0"], sample("pill0", tl, t, {"v": 0.0})["v"] < 0.5)
    # cups held on a palm
    hold = {}
    for c in tl["cues"]:
        if c["name"] == "hold" and c["t"] <= t:
            hold[c["who"]] = c.get("on", True)
    for who, obs in W.get("holds", {}).items():
        for ob in obs:
            ob.hide_render = not hold.get(who, False)
    _hide(W["cup3"], sample("cup3", tl, t, {"v": 0.0})["v"] < 0.5)
    tr = sample("treat", tl, t, {"v": 0.0})["v"]
    _hide(W["cookies"], not (0.5 < tr < 1.5))
    _hide(W["cake"], not (tr >= 1.5))
    # windshield pollen only after L20
    # who sits: legs straight out forward, hips on the seat
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
    # the dog's tail
    if W.get("tail") is not None:
        W["tail"].rotation_euler = (0, 0.5 * math.sin(t * 7.0), 0)
    return gains
