"""ep141 "The LOST Poster Has My Face": one bright, sunny, warm world. A street corner with a wooden notice board
(cream LOST posters with a red "?" glyph and a drawn picture, no letters), a mailbox, two front doors, a little blue
car, and four closed rooms: Mom's kitchen, my card room, Grandma's kitchen and the striped pie tent.

ONE sun, never changed; nothing blinks, glows or flickers. No text anywhere: the only marks are glyphs and numerals.
Cues read by animate(): sit (per character 0..1), flour (0/1), trophy (on, x, y, z), scarf (on, x, y, z), pie (on),
banner (on), gposter (on), tally (on). Extras on the cast (quiff, puff, apron, watch, flour) are built in late() on the
first animate, once the cast exists.
"""
import math
import sys
import tempfile
from pathlib import Path

import bpy
from mathutils import Vector as V

sys.path.insert(0, str(Path(__file__).resolve().parent))
import layout as G  # noqa: E402

W = {}
SIT = -math.pi / 2 * 0.97
SEATED = ("me", "bud1", "bud2")
D2R = math.pi / 180.0


def ss(x):
    x = min(1.0, max(0.0, x))
    return x * x * (3 - 2 * x)


def lerp(a, b, u):
    return a + (b - a) * u


def noshadow(ob):
    ob.visible_shadow = False
    for c in ob.children_recursive:
        c.visible_shadow = False


def hide(ob, h=True):
    ob.hide_render = h
    for c in ob.children_recursive:
        c.hide_render = h


def sample(name, tl, t, defaults):
    """The state of cue track `name` at t: numeric fields eased over a cue's own "dur"."""
    cur, prev = dict(defaults), dict(defaults)
    for c in tl["cues"]:
        if c["name"] != name:
            continue
        if c["t"] > t:
            break
        prev = dict(cur)
        cur.update({k: v for k, v in c.items() if k in defaults})
        dur = c.get("dur", 0.0)
        if dur > 0 and t < c["t"] + dur:
            u = ss((t - c["t"]) / dur)
            return {k: (prev[k] + (cur[k] - prev[k]) * u if isinstance(cur[k], (int, float)) else cur[k]) for k in cur}
    return cur


# ---------------------------------------------------------------------------------------------- the outdoors
def P(kit, hexc, rough=0.5, spec=0.35):
    return kit.plastic(hexc, rough, spec=spec)


def stage_ground(kit, c, backdrop=True, road=True):
    cx, cy = c
    pl = kit.plastic
    kit.box(f"walk.{cx}", (13.0, 12.0, 0.1), (cx, cy + 0.0, -0.05), kit.texture("concrete", 1.0, tint="#f0ece4"))
    kit.box(f"kerb.{cx}", (13.0, 0.22, 0.16), (cx, cy - 6.1, 0.0), pl("#d8d4cc", 0.8, spec=0.05))
    if road:
        kit.box(f"road.{cx}", (13.0, 8.0, 0.1), (cx, cy - 10.2, -0.05), kit.texture("asphalt", 0.5, tint="#c8c8d0"))
    if backdrop:
        kit.prop("sub_building_type_c", (cx - 5.5, cy + 14.0, 0), rot=180, height=6.5)
        kit.prop("sub_building_type_k", (cx + 5.5, cy + 15.0, 0), rot=180, height=6.5)
        kit.prop("sub_tree_large", (cx + 1.0, cy + 10.0, 0), height=6.0)


def build_ground(kit):
    kit.plane("lawn", (900, 900), (0, 0, -0.03), kit.plastic("#62c45a", 0.9, spec=0.05))
    for c in (G.CORNER, G.MAIL, G.ADOOR, G.GDOOR, G.CAR):
        stage_ground(kit, c)


# ---------------------------------------------------------------------------------------------- the notice board
def layer(kit, name, size, x, z, k, mat):
    """One flat piece of a poster's picture, k layers (1.2 cm each) proud of the board."""
    return kit.box(name, (size[0], 0.01, size[1]), (x, G.BOARD_Y - 0.05 - 0.012 * k, z), mat)


def qmark(kit, name, x, z, s, mat):
    """A big red question-mark glyph, from boxes."""
    layer(kit, f"{name}.q1", (0.26 * s, 0.07 * s), x, z + 0.20 * s, 2, mat)
    layer(kit, f"{name}.q2", (0.07 * s, 0.17 * s), x + 0.095 * s, z + 0.115 * s, 2, mat)
    layer(kit, f"{name}.q3", (0.17 * s, 0.07 * s), x + 0.045 * s, z + 0.03 * s, 2, mat)
    layer(kit, f"{name}.q4", (0.07 * s, 0.10 * s), x, z - 0.03 * s, 2, mat)
    layer(kit, f"{name}.q5", (0.08 * s, 0.08 * s), x, z - 0.15 * s, 2, mat)


def poster_sheet(kit, key, x, picture):
    pl = kit.plastic
    cream = pl("#f3e8cc", 0.8, spec=0.05)
    edge = pl("#c9b98e", 0.8, spec=0.05)
    red = pl("#d8322f", 0.6, spec=0.1)
    z = G.POSTER_Z
    kit.box(f"poster.{key}.edge", (0.9, 0.008, 1.2), (x, G.BOARD_Y - 0.043, z), edge)
    kit.box(f"poster.{key}.sheet", (0.86, 0.01, 1.16), (x, G.BOARD_Y - 0.05 - 0.012, z), cream)
    qmark(kit, f"poster.{key}", x, z + 0.43, 1.0, red)
    kit.box(f"poster.{key}.pin", (0.07, 0.03, 0.07), (x, G.BOARD_Y - 0.09, z + 0.545), pl("#3a6fd0", 0.4))
    picture(kit, key, x, z - 0.12)


def pic_umbrella(kit, key, x, z):
    pl = kit.plastic
    cols = [pl("#d8322f", 0.6), pl("#f2c230", 0.6)]
    widths = [0.66, 0.56, 0.42, 0.24]
    for i, w in enumerate(widths):
        layer(kit, f"poster.{key}.cn{i}", (w, 0.1), x, z + 0.18 + 0.09 * i, 3, cols[i % 2])
    layer(kit, f"poster.{key}.stem", (0.04, 0.44), x, z - 0.06, 3, pl("#4a3a2e", 0.6))
    layer(kit, f"poster.{key}.hook1", (0.14, 0.04), x - 0.05, z - 0.28, 3, pl("#4a3a2e", 0.6))
    layer(kit, f"poster.{key}.hook2", (0.04, 0.09), x - 0.1, z - 0.24, 3, pl("#4a3a2e", 0.6))


def pic_keys(kit, key, x, z):
    pl = kit.plastic
    gold = pl("#c99a24", 0.4, spec=0.5)
    steel = pl("#7d8794", 0.4, spec=0.5)
    ring = kit.cyl(f"poster.{key}.ring", 0.13, 0.01, (x, G.BOARD_Y - 0.05 - 0.012 * 3, z + 0.2), steel, rot=(math.pi / 2, 0, 0), n=18)
    kit.cyl(f"poster.{key}.hole", 0.08, 0.01, (x, G.BOARD_Y - 0.05 - 0.012 * 4, z + 0.2), pl("#f3e8cc", 0.8), rot=(math.pi / 2, 0, 0), n=16)
    for i, (dx, mat) in enumerate(((-0.1, gold), (0.1, steel))):
        layer(kit, f"poster.{key}.sh{i}", (0.05, 0.4), x + dx, z - 0.08, 5, mat)
        layer(kit, f"poster.{key}.bow{i}", (0.15, 0.12), x + dx, z + 0.06, 5, mat)
        layer(kit, f"poster.{key}.t{i}", (0.1, 0.05), x + dx + 0.06, z - 0.22, 5, mat)
        layer(kit, f"poster.{key}.t{i}b", (0.08, 0.04), x + dx + 0.05, z - 0.14, 5, mat)


def pic_face(kit, key, x, z, who="me"):
    pl = kit.plastic
    skin = pl("#f1c9a0", 0.6)
    ink = pl("#2a1a14", 0.7)
    layer(kit, f"poster.{key}.bg", (0.76, 0.84), x, z - 0.04, 2, pl("#7fb8e8", 0.7))
    if who == "me":
        hair = pl("#b4532c", 0.6)
        layer(kit, f"poster.{key}.shirt", (0.5, 0.16), x, z - 0.27, 3, pl("#4f86d8", 0.6))
        layer(kit, f"poster.{key}.head", (0.42, 0.46), x, z - 0.02, 3, skin)
        layer(kit, f"poster.{key}.hair", (0.46, 0.12), x, z + 0.25, 4, hair)
        layer(kit, f"poster.{key}.quiff", (0.28, 0.12), x - 0.04, z + 0.35, 4, hair)
        for i, dx in enumerate((-0.1, 0.1)):
            layer(kit, f"poster.{key}.eye{i}", (0.05, 0.06), x + dx, z + 0.04, 4, ink)
        layer(kit, f"poster.{key}.mouth", (0.16, 0.025), x, z - 0.1, 4, ink)
        layer(kit, f"poster.{key}.mouthL", (0.03, 0.04), x - 0.09, z - 0.085, 4, ink)
        layer(kit, f"poster.{key}.mouthR", (0.03, 0.04), x + 0.09, z - 0.085, 4, ink)
        for i, (dx, dz) in enumerate(((-0.13, -0.03), (-0.09, -0.05), (0.09, -0.05), (0.13, -0.03))):
            layer(kit, f"poster.{key}.fr{i}", (0.02, 0.02), x + dx, z + dz, 4, pl("#b9714a", 0.7))
    else:
        white = pl("#e8e4ee", 0.8)
        layer(kit, f"poster.{key}.shirt", (0.5, 0.16), x, z - 0.27, 3, pl("#a98ad8", 0.6))
        layer(kit, f"poster.{key}.puff", (0.6, 0.34), x, z + 0.17, 3, white)
        layer(kit, f"poster.{key}.puff2", (0.5, 0.14), x, z + 0.37, 3, white)
        layer(kit, f"poster.{key}.head", (0.38, 0.4), x, z - 0.04, 4, skin)
        layer(kit, f"poster.{key}.fringe", (0.38, 0.08), x, z + 0.16, 5, white)
        for i, dx in enumerate((-0.09, 0.09)):
            layer(kit, f"poster.{key}.gl{i}", (0.12, 0.1), x + dx, z + 0.02, 5, pl("#3a2a3a", 0.5))
            layer(kit, f"poster.{key}.eye{i}", (0.07, 0.06), x + dx, z + 0.02, 6, skin)
            layer(kit, f"poster.{key}.pupil{i}", (0.035, 0.04), x + dx, z + 0.02, 7, ink)
        layer(kit, f"poster.{key}.mouth", (0.16, 0.025), x, z - 0.11, 5, ink)
        layer(kit, f"poster.{key}.mouthL", (0.03, 0.04), x - 0.09, z - 0.095, 5, ink)
        layer(kit, f"poster.{key}.mouthR", (0.03, 0.04), x + 0.09, z - 0.095, 5, ink)


def build_board(kit):
    pl = kit.plastic
    wood = pl("#b9874f", 0.7, spec=0.1)
    dark = pl("#7a5230", 0.7, spec=0.1)
    for sx in (-2.5, 2.5):
        kit.box(f"board.post{sx}", (0.16, 0.16, 2.9), (sx, G.BOARD_Y + 0.1, 1.45), dark)
    kit.box("board.panel", (5.0, 0.08, 1.8), (0, G.BOARD_Y, 1.65), wood)
    for z in (0.74, 2.56):
        kit.box(f"board.rail{z}", (5.12, 0.1, 0.1), (0, G.BOARD_Y - 0.01, z), dark)
    for sx in (-2.55, 2.55):
        kit.box(f"board.side{sx}", (0.1, 0.1, 1.9), (sx, G.BOARD_Y - 0.01, 1.65), dark)
    kit.box("board.roof", (5.4, 0.55, 0.08), (0, G.BOARD_Y - 0.15, 2.66), dark)
    S = G.SLOT
    poster_sheet(kit, "umb", S["umb"], pic_umbrella)
    poster_sheet(kit, "keys", S["keys"], pic_keys)
    poster_sheet(kit, "me", S["me"], lambda k, key, x, z: pic_face(k, key, x, z, "me"))
    # Grandma's poster appears after a cut (the gposter cue)
    before = set(o.name for o in bpy.data.objects)
    poster_sheet(kit, "gran", S["gran"], lambda k, key, x, z: pic_face(k, key, x, z, "gran"))
    W["gposter"] = [o for o in bpy.data.objects if o.name not in before]
    # the lore tally: two short red strokes on the board's top corner (not narrated), seen in S28
    red = pl("#a01818", 0.5)
    W["tally"] = [kit.box(f"board.tally{k}", (0.05, 0.02, 0.2), (2.15 + 0.13 * k, G.BOARD_Y - 0.065, 2.38), red) for k in range(2)]
    # the sidewalk's big tree and a lamp post for depth
    kit.prop("commontree_1", (-6.5, 7.5, 0), rot=20, height=6.5, tint="#d4f0c4")
    kit.prop("bush_1", (4.2, 5.2, 0), height=1.3)
    kit.prop("bush_1", (-4.2, 5.0, 0), height=1.3)


# ---------------------------------------------------------------------------------------------- mailbox, doors, car
def build_mailbox(kit):
    cx, cy = G.MAIL
    pl = kit.plastic
    kit.box("mb.post", (0.14, 0.14, 1.2), (cx, cy + 2.2, 0.6), pl("#8a5a34", 0.7))
    kit.box("mb.body", (0.34, 0.7, 0.3), (cx, cy + 2.2, 1.3), pl("#3a6fd0", 0.4, spec=0.5), bevel=0.05)
    kit.box("mb.top", (0.36, 0.7, 0.04), (cx, cy + 2.2, 1.47), pl("#2f58a8", 0.4), bevel=0.02)
    kit.box("mb.flag", (0.04, 0.04, 0.3), (cx + 0.2, cy + 2.0, 1.45), pl("#d8322f", 0.5))
    kit.box("mb.flag2", (0.04, 0.16, 0.1), (cx + 0.2, cy + 1.95, 1.6), pl("#d8322f", 0.5))
    kit.box("mb.door", (0.3, 0.02, 0.24), (cx, cy + 1.84, 1.3), pl("#2f58a8", 0.4))
    for sx in (-1, 1):
        kit.box(f"mb.fence{sx}", (3.0, 0.1, 0.9), (cx + sx * 3.2, cy + 4.2, 0.45), pl("#f0e4cc", 0.7))
    kit.prop("bush_1", (cx + 4.5, cy + 3.2, 0), height=1.4)
    kit.prop("flowers", (cx - 3.3, cy + 2.8, 0), height=0.8)


def house_front(kit, c, wall, door, name):
    """A porch wall with a painted door, a window, a roof overhang and a step, facing south."""
    cx, cy = c
    pl = kit.plastic
    y = cy + 3.5
    kit.box(f"{name}.wall", (9.0, 0.3, 3.4), (cx, y, 1.7), pl(wall, 0.8, spec=0.05))
    kit.box(f"{name}.roof", (9.6, 1.4, 0.2), (cx, y - 0.6, 3.5), pl("#8a4a3a", 0.7))
    kit.box(f"{name}.door", (1.0, 0.1, 2.1), (cx, y - 0.2, 1.05), pl(door, 0.5, spec=0.3), bevel=0.02)
    kit.box(f"{name}.doorframe", (1.2, 0.08, 2.25), (cx, y - 0.17, 1.12), pl("#f0e8d4", 0.7))
    kit.cyl(f"{name}.knob", 0.05, 0.06, (cx + 0.35, y - 0.28, 1.0), pl("#d8a93b", 0.3, spec=0.8), rot=(math.pi / 2, 0, 0), n=10)
    for sx in (-1, 1):
        kit.box(f"{name}.win{sx}", (1.1, 0.06, 1.1), (cx + sx * 2.9, y - 0.18, 1.8), pl("#9ed4f0", 0.2, spec=0.7))
        kit.box(f"{name}.winframe{sx}", (1.3, 0.05, 1.3), (cx + sx * 2.9, y - 0.16, 1.8), pl("#f6f1e6", 0.6))
        kit.box(f"{name}.shutterL{sx}", (0.22, 0.05, 1.3), (cx + sx * 2.9 - 0.76, y - 0.2, 1.8), pl("#4a8a6a", 0.6))
        kit.box(f"{name}.shutterR{sx}", (0.22, 0.05, 1.3), (cx + sx * 2.9 + 0.76, y - 0.2, 1.8), pl("#4a8a6a", 0.6))
        kit.box(f"{name}.planter{sx}", (1.3, 0.3, 0.26), (cx + sx * 2.9, y - 0.4, 1.05), pl("#8a5a34", 0.7))
        for k in range(4):
            kit.sphere(f"{name}.fl{sx}{k}", 0.1, (cx + sx * 2.9 - 0.45 + 0.3 * k, y - 0.4, 1.28), pl("#e8587a", 0.7), seg=8)
    kit.box(f"{name}.step", (1.6, 0.6, 0.12), (cx, y - 0.6, 0.06), pl("#c8c4bc", 0.8))
    kit.box(f"{name}.mat", (0.9, 0.5, 0.02), (cx, y - 0.9, 0.01), pl("#d8322f", 0.8))


def build_car(kit):
    cx, cy = G.CAR
    pl = kit.plastic
    blue = pl("#2f7fe0", 0.3, spec=0.6)
    glass = pl("#bfe6ff", 0.15, spec=0.8)
    dark = pl("#25252b", 0.7)
    root = kit.empty("car", (cx + 0.9, cy + 3.6, 0))
    kit.box("car.body", (2.9, 1.5, 0.62), (0, 0, 0.62), blue, root, bevel=0.1)
    kit.box("car.cab", (1.6, 1.36, 0.55), (-0.15, 0, 1.2), blue, root, bevel=0.1)
    for sx in (-1, 1):
        kit.box(f"car.win{sx}", (1.3, 0.04, 0.38), (-0.15, sx * 0.69, 1.2), glass, root)
    kit.box("car.windF", (0.04, 1.2, 0.38), (0.66, 0, 1.2), glass, root)
    kit.box("car.bump1", (0.1, 1.5, 0.14), (1.47, 0, 0.42), pl("#cfd2d6", 0.3, spec=0.8), root)
    kit.box("car.bump2", (0.1, 1.5, 0.14), (-1.47, 0, 0.42), pl("#cfd2d6", 0.3, spec=0.8), root)
    for sx in (-1, 1):
        for lx in (-0.95, 0.95):
            kit.cyl(f"car.wh{sx}{lx}", 0.3, 0.2, (lx, sx * 0.72, 0.3), dark, root, rot=(math.pi / 2, 0, 0), n=14)
            kit.cyl(f"car.hub{sx}{lx}", 0.14, 0.22, (lx, sx * 0.72, 0.3), pl("#cfd2d6", 0.3, spec=0.8), root, rot=(math.pi / 2, 0, 0), n=10)
        kit.box(f"car.lamp{sx}", (0.04, 0.24, 0.16), (1.46, sx * 0.5, 0.72), pl("#fff3c8", 0.3), root)


# ---------------------------------------------------------------------------------------------- rooms
def build_room(kit, c, name, wall, floor_tint, trim="#f0e4cc", light=520):
    cx, cy = c
    H = G.ROOM_HALF
    pl = kit.plastic
    w = pl(wall, 0.85, spec=0.05)
    kit.box(f"{name}.floor", (9.4, 9.4, 0.1), (cx, cy, -0.05), kit.texture("wood", 1.0, tint=floor_tint))
    kit.box(f"{name}.ceil", (9.4, 9.4, 0.12), (cx, cy, 3.06), kit.emit("#f4e6cc", 0.55))
    kit.box(f"{name}.wallB", (9.4, 0.2, 3.0), (cx, cy + H + 0.1, 1.5), w)
    kit.box(f"{name}.wallF", (9.4, 0.2, 3.0), (cx, cy - H - 0.1, 1.5), w)
    kit.box(f"{name}.wallL", (0.2, 9.4, 3.0), (cx - H - 0.1, cy, 1.5), w)
    kit.box(f"{name}.wallR", (0.2, 9.4, 3.0), (cx + H + 0.1, cy, 1.5), w)
    tm = pl(trim, 0.7, spec=0.05)
    kit.box(f"{name}.baseB", (9.0, 0.06, 0.16), (cx, cy + H - 0.03, 0.08), tm)
    kit.box(f"{name}.baseL", (0.06, 9.0, 0.16), (cx - H + 0.03, cy, 0.08), tm)
    kit.box(f"{name}.baseR", (0.06, 9.0, 0.16), (cx + H - 0.03, cy, 0.08), tm)
    kit.box(f"{name}.crownB", (9.0, 0.08, 0.1), (cx, cy + H - 0.04, 2.95), tm)
    lt = kit.light(f"{name}.lamp", "AREA", (cx, cy, 2.8), light, "#fff1da", size=5.0, shadow=False)
    kit.aim(lt, (cx, cy, 0.0))
    lt2 = kit.light(f"{name}.lamp2", "AREA", (cx, cy + 3.0, 2.8), light * 0.6, "#fff1da", size=4.0, shadow=False)
    kit.aim(lt2, (cx, cy + 3.0, 0.0))


def window(kit, name, x, y, z, w=1.7, h=1.25, yard=True, curtain="#f08a5c", side="B"):
    """A window in the back wall (face at y), the sky and a green yard behind, white frame, open curtains."""
    pl = kit.plastic
    kit.box(f"{name}.sky", (w, 0.04, h * 0.62), (x, y - 0.03, z + h * 0.19), kit.emit("#a8dcff", 1.6))
    kit.box(f"{name}.yard", (w, 0.04, h * 0.38), (x, y - 0.03, z - h * 0.31), kit.emit("#74c860", 1.2))
    fr = pl("#f0e8d6", 0.7)
    for dz in (-h / 2 - 0.04, h / 2 + 0.04):
        kit.box(f"{name}.fh{dz}", (w + 0.16, 0.08, 0.08), (x, y - 0.05, z + dz), fr)
    for dx in (-w / 2 - 0.04, w / 2 + 0.04, 0.0):
        kit.box(f"{name}.fv{dx}", (0.08, 0.08, h + 0.16), (x + dx, y - 0.05, z), fr)
    kit.box(f"{name}.mullh", (w, 0.07, 0.06), (x, y - 0.05, z), fr)
    cur = pl(curtain, 0.9, spec=0.02)
    for sx in (-1, 1):
        kit.box(f"{name}.cur{sx}", (0.34, 0.1, h + 0.5), (x + sx * (w / 2 + 0.28), y - 0.1, z), cur, bevel=0.03)
    kit.box(f"{name}.rod", (w + 1.1, 0.06, 0.05), (x, y - 0.1, z + h / 2 + 0.28), pl("#7a5230", 0.5))


def picture_frame(kit, name, x, y, z, w, h, cols):
    pl = kit.plastic
    kit.box(f"{name}.fr", (w + 0.1, 0.05, h + 0.1), (x, y - 0.03, z), pl("#7a5230", 0.6))
    kit.box(f"{name}.a", (w, 0.03, h), (x, y - 0.06, z), pl(cols[0], 0.7))
    kit.box(f"{name}.b", (w * 0.6, 0.03, h * 0.45), (x - w * 0.1, y - 0.075, z - h * 0.2), pl(cols[1], 0.7))
    kit.sphere(f"{name}.c", min(w, h) * 0.14, (x + w * 0.22, y - 0.09, z + h * 0.22), pl(cols[2], 0.6), seg=10)


def counter_run(kit, name, x0, x1, y, z_top=0.92, body="#4fa39a", top="#d9b27a"):
    pl = kit.plastic
    w = x1 - x0
    xc = (x0 + x1) / 2
    kit.box(f"{name}.base", (w, 0.62, z_top - 0.06), (xc, y, (z_top - 0.06) / 2), pl(body, 0.5, spec=0.3), bevel=0.02)
    kit.box(f"{name}.top", (w + 0.04, 0.68, 0.06), (xc, y - 0.02, z_top - 0.03), pl(top, 0.6, spec=0.2), bevel=0.01)
    n = max(1, int(w / 0.7))
    for k in range(1, n):
        kit.box(f"{name}.seam{k}", (0.02, 0.02, z_top - 0.2), (x0 + w * k / n, y - 0.32, (z_top - 0.2) / 2 + 0.06), pl("#2a2a2e", 0.7))
    for k in range(n):
        kit.box(f"{name}.knob{k}", (0.1, 0.03, 0.03), (x0 + w * (k + 0.5) / n, y - 0.33, z_top - 0.18), pl("#d8d4cc", 0.3, spec=0.8))


def upper_cabs(kit, name, x0, x1, y, body="#f2c44c"):
    pl = kit.plastic
    w = x1 - x0
    kit.box(f"{name}.cab", (w, 0.4, 0.75), ((x0 + x1) / 2, y, 1.95), pl(body, 0.5, spec=0.3), bevel=0.02)
    n = max(1, int(w / 0.7))
    for k in range(1, n):
        kit.box(f"{name}.seam{k}", (0.02, 0.02, 0.7), (x0 + w * k / n, y - 0.21, 1.95), pl("#2a2a2e", 0.7))


def round_table(kit, name, x, y, top="#d9a050", cloth=None, r=0.8, h=0.74):
    pl = kit.plastic
    kit.cyl(f"{name}.leg", 0.1, h, (x, y, h / 2), pl("#7a5230", 0.6), n=10)
    kit.cyl(f"{name}.top", r, 0.05, (x, y, h), pl(cloth or top, 0.6, spec=0.2), n=28)
    kit.cyl(f"{name}.base", 0.34, 0.05, (x, y, 0.025), pl("#7a5230", 0.6), n=16)


def chair(kit, name, x, y, yaw=0.0, col="#d8573a"):
    pl = kit.plastic
    root = kit.empty(name, (x, y, 0), None, rot=(0, 0, yaw * D2R))
    kit.box(f"{name}.seat", (0.46, 0.46, 0.06), (0, 0, 0.43), pl(col, 0.5, spec=0.3), root, bevel=0.02)
    kit.box(f"{name}.back", (0.46, 0.06, 0.5), (0, 0.2, 0.72), pl(col, 0.5, spec=0.3), root, bevel=0.02)
    for sx in (-1, 1):
        for sy in (-1, 1):
            kit.box(f"{name}.leg{sx}{sy}", (0.05, 0.05, 0.4), (sx * 0.2, sy * 0.2, 0.2), pl("#6a4a2e", 0.6), root)


def ribbons(kit, name, x, y, z, col, col2):
    """A shelf (face at y) with six plain rosette ribbons hung under a rail: discs and two tails, no text."""
    pl = kit.plastic
    kit.box(f"{name}.board", (1.9, 0.06, 0.1), (x, y - 0.06, z + 0.5), pl("#7a5230", 0.6))
    kit.box(f"{name}.back", (1.9, 0.03, 0.9), (x, y - 0.02, z + 0.05), pl("#a8774a", 0.7))
    kit.box(f"{name}.ledge", (2.0, 0.16, 0.05), (x, y - 0.1, z - 0.42), pl("#7a5230", 0.6))
    m1, m2 = pl(col, 0.35, spec=0.6), pl(col2, 0.5, spec=0.3)
    for k in range(6):
        px = x - 0.75 + 0.3 * k
        kit.box(f"{name}.tL{k}", (0.07, 0.025, 0.3), (px - 0.05, y - 0.09, z + 0.14), m2, rot=(0, 0.2, 0))
        kit.box(f"{name}.tR{k}", (0.07, 0.025, 0.3), (px + 0.05, y - 0.09, z + 0.14), m2, rot=(0, -0.2, 0))
        kit.cyl(f"{name}.d{k}", 0.13, 0.04, (px, y - 0.12, z + 0.34), m1, rot=(math.pi / 2, 0, 0), n=14)
        kit.cyl(f"{name}.c{k}", 0.065, 0.045, (px, y - 0.15, z + 0.34), m2, rot=(math.pi / 2, 0, 0), n=10)


def pie(kit, name, x, y, z, r=0.2, crust="#d79a4a", parent=None):
    pl = kit.plastic
    kit.cyl(f"{name}.tin", r, 0.06, (x, y, z + 0.03), pl("#a9a9b0", 0.4, spec=0.6), parent, n=18)
    kit.cyl(f"{name}.crust", r * 0.9, 0.07, (x, y, z + 0.08), pl(crust, 0.7, spec=0.1), parent, n=18)
    kit.cyl(f"{name}.top", r * 0.7, 0.03, (x, y, z + 0.13), pl("#e8b866", 0.7, spec=0.1), parent, n=18)


def build_momk(kit):
    cx, cy = G.MOMK
    H = G.ROOM_HALF
    pl = kit.plastic
    build_room(kit, G.MOMK, "momk", "#f0d27c", "#e0b078")
    window(kit, "momk.win", cx - 1.6, cy + H, 1.65, 1.8, 1.3, curtain="#e8704c")
    counter_run(kit, "momk.cnt", cx + 0.6, cx + 4.3, cy + H - 0.34)
    upper_cabs(kit, "momk.up", cx + 1.4, cx + 4.3, cy + H - 0.2)
    kit.box("momk.fridge", (0.9, 0.8, 1.95), (cx - 4.0, cy + H - 0.45, 0.98), pl("#b8c8d4", 0.35, spec=0.6), bevel=0.04)
    kit.box("momk.fridge2", (0.88, 0.02, 0.04), (cx - 4.0, cy + H - 0.86, 1.3), pl("#8a96a0", 0.5))
    round_table(kit, "momk.tbl", cx - 2.8, cy + 2.4, cloth="#d9573d")
    chair(kit, "momk.ch1", cx - 3.5, cy + 2.4, 90, "#3a9aa0")
    chair(kit, "momk.ch2", cx - 2.1, cy + 2.4, -90, "#3a9aa0")
    picture_frame(kit, "momk.pic", cx + 2.9, cy + H - 0.05, 2.55, 0.8, 0.6, ("#8ac0e0", "#74c860", "#f2c230"))
    kit.cyl("momk.bowl", 0.18, 0.1, (cx + 3.0, cy + H - 0.34, 0.97), pl("#d8322f", 0.4, spec=0.5), n=14)
    for k, col in enumerate(("#f2c230", "#e8704c", "#74c860")):
        kit.sphere(f"momk.fruit{k}", 0.07, (cx + 2.95 + 0.07 * k, cy + H - 0.34, 1.06), pl(col, 0.6), seg=8)
    kit.box("momk.rug", (2.4, 1.6, 0.02), (cx + 0.2, cy + 1.5, 0.01), pl("#4a8ad0", 0.9, spec=0.02))
    kit.box("momk.rug2", (2.0, 1.2, 0.02), (cx + 0.2, cy + 1.5, 0.02), pl("#f0c050", 0.9, spec=0.02))


def build_card(kit):
    cx, cy = G.CARD
    H = G.ROOM_HALF
    pl = kit.plastic
    build_room(kit, G.CARD, "card", "#9bcfe0", "#d8a878")
    window(kit, "card.win", cx - 3.0, cy + H, 1.7, 1.6, 1.2, curtain="#f2c44c")
    ribbons(kit, "gold", cx + 2.5, cy + H - 0.02, 1.9, "#e8b830", "#d89a20")
    # the card table: green felt, chips and cards, three chairs (mine centre far side, one friend's near side)
    kit.box("card.tbl", (2.3, 1.3, 0.06), (cx - 1.5, cy + 0.8, 0.72), pl("#2f8a56", 0.9, spec=0.02), bevel=0.02)
    kit.box("card.tblrim", (2.4, 1.4, 0.05), (cx - 1.5, cy + 0.8, 0.68), pl("#7a5230", 0.6))
    for sx in (-1, 1):
        for sy in (-1, 1):
            kit.box(f"card.tleg{sx}{sy}", (0.08, 0.08, 0.7), (cx - 1.5 + sx * 1.05, cy + 0.8 + sy * 0.55, 0.35), pl("#7a5230", 0.6))
    chair(kit, "card.chMe", cx - 1.4, cy + 1.75, 180, "#d8573a")
    chair(kit, "card.chB1", cx - 2.6, cy + 1.75, 180, "#3a9aa0")
    chair(kit, "card.chB2", cx - 0.2, cy + 0.2, 90, "#f2c44c")
    chipc = ["#d8322f", "#2f6fd0", "#f2c230", "#2f8a56"]
    for k in range(10):
        kit.cyl(f"card.chip{k}", 0.05, 0.02, (cx - 1.3 + 0.12 * (k % 5), cy + 0.5 + 0.12 * (k // 5), 0.76 + 0.02 * (k % 3)), pl(chipc[k % 4], 0.4, spec=0.5), n=10)
    for k in range(5):
        kit.box(f"card.card{k}", (0.15, 0.2, 0.01), (cx - 1.9 + 0.17 * k, cy + 1.05, 0.755), pl("#e8e4da", 0.7), rot=(0, 0, 0.1 * k))
    picture_frame(kit, "card.pic", cx + 0.3, cy + H - 0.05, 2.1, 0.9, 0.7, ("#f0a0a0", "#8ac0e0", "#f2c230"))
    kit.box("card.rug", (3.4, 2.4, 0.02), (cx - 1.5, cy + 1.0, 0.01), pl("#d8573a", 0.9, spec=0.02))


def build_grank(kit):
    cx, cy = G.GRANK
    H = G.ROOM_HALF
    pl = kit.plastic
    build_room(kit, G.GRANK, "grank", "#f4b8c4", "#d8a070")
    ribbons(kit, "silver", cx - 3.0, cy + H - 0.02, 1.9, "#b8bec8", "#8a96b8")
    window(kit, "grank.win", cx + 0.6, cy + H, 1.75, 1.5, 1.1, curtain="#a98ad8")
    counter_run(kit, "grank.cnt", cx - 0.4, cx + 4.3, cy + H - 0.34, body="#a98ad8", top="#e0c898")
    upper_cabs(kit, "grank.up", cx + 2.0, cx + 4.3, cy + H - 0.2, body="#f2e0a0")
    for k in range(6):
        pie(kit, f"grank.pie{k}", cx + 0.2 + 0.6 * k, cy + H - 0.34, 0.95, 0.2, "#d79a4a")
    kit.box("grank.flour", (0.5, 0.35, 0.3), (cx + 3.8, cy + H - 0.55, 1.1), pl("#d8d2c4", 0.9, spec=0.02), bevel=0.04)
    kit.cyl("grank.pin", 0.04, 0.5, (cx + 0.2, cy + H - 0.7, 0.98), pl("#c89a5a", 0.6), rot=(0, math.pi / 2, 0), n=10)
    kit.box("grank.rug", (3.0, 1.8, 0.02), (cx + 0.6, cy + 2.2, 0.01), pl("#f2c44c", 0.9, spec=0.02))
    round_table(kit, "grank.tbl", cx - 3.4, cy + 0.6, cloth="#f2c44c", r=0.7)
    chair(kit, "grank.ch1", cx - 3.4, cy + 1.5, 180, "#a98ad8")
    picture_frame(kit, "grank.pic", cx + 3.2, cy + 0.0 + H - 0.05, 2.7, 0.7, 0.5, ("#8ac0e0", "#f2c230", "#d8322f"))


def build_tent(kit):
    cx, cy = G.TENT
    pl = kit.plastic
    red = pl("#d94a3a", 0.8, spec=0.05)
    wht = pl("#cfc8b8", 0.8, spec=0.05)
    HX, HY = 6.0, 5.0
    kit.box("tent.floor", (12.4, 10.4, 0.1), (cx, cy, -0.05), kit.texture("grass", 1.0, tint="#d8f0b0"))

    # walls: alternating strips 0.6 m wide
    for k in range(20):
        m = red if k % 2 else wht
        kit.box(f"tent.back{k}", (0.6, 0.12, 3.8), (cx - HX + 0.3 + 0.6 * k, cy + HY + 0.06, 1.9), m)
        kit.box(f"tent.front{k}", (0.6, 0.12, 3.8), (cx - HX + 0.3 + 0.6 * k, cy - HY - 0.06, 1.9), m)
    for k in range(17):
        m = red if k % 2 else wht
        kit.box(f"tent.right{k}", (0.12, 0.6, 2.8), (cx + HX + 0.06, cy - HY + 0.3 + 0.6 * k, 1.4), m)
        # the left wall has the open flap: stripes only on the far part (y > cy + 3.2) and above the opening
        if cy - HY + 0.3 + 0.6 * k > cy + 3.4 or cy - HY + 0.3 + 0.6 * k < cy - 3.4:
            kit.box(f"tent.left{k}", (0.12, 0.6, 2.8), (cx - HX - 0.06, cy - HY + 0.3 + 0.6 * k, 1.4), m)
    kit.box("tent.leftlintel", (0.12, 6.8, 0.5), (cx - HX - 0.06, cy, 2.55), red)
    # the pitched roof: two slabs with alternating stripes, the ridge along x
    ang = math.atan2(1.4, HY)
    sl = math.hypot(HY, 1.4)
    for sgn in (-1, 1):
        for k in range(20):
            m = red if k % 2 else wht
            kit.box(f"tent.roofp{sgn}{k}", (0.6, sl + 0.3, 0.1), (cx - HX + 0.3 + 0.6 * k, cy + sgn * HY / 2, 3.5),
                    m, rot=(-sgn * ang, 0, 0))
    # the lawn outside the flap, trees for depth
    kit.prop("commontree_1", (cx - 15.0, cy + 2.0, 0), rot=40, height=7.0, tint="#d4f0c4")
    kit.prop("commontree_1", (cx - 13.0, cy - 6.0, 0), rot=10, height=6.0, tint="#d4f0c4")
    kit.prop("sub_building_type_c", (cx - 24.0, cy + 10.0, 0), rot=90, height=6.0)
    # bunting along the back wall (plain triangles as small boxes)
    cols = ["#f2c230", "#3a6fd0", "#74c860", "#e8587a"]
    for k in range(14):
        kit.box(f"tent.flag{k}", (0.32, 0.03, 0.4), (cx - 5.2 + 0.8 * k, cy + HY - 0.08, 3.1 - 0.12 * math.sin(k * 0.8)), pl(cols[k % 4], 0.7),
                rot=(0, 0.785, 0))
    kit.box("tent.string", (11.0, 0.02, 0.03), (cx, cy + HY - 0.07, 3.28), pl("#4a3a2e", 0.7))
    # lights
    for i, (lx, ly) in enumerate(((0, 0), (-3.5, 2.5), (3.5, 2.5), (0, 3.5))):
        lt = kit.light(f"tent.lamp{i}", "AREA", (cx + lx, cy + ly, 3.6), 520 if i == 0 else 380, "#fff1da", size=4.5, shadow=False)
        kit.aim(lt, (cx + lx, cy + ly, 0.0))
    # the judges' long table (face at y = cy + 1.55), cloth, three pies under cloths, bell, trophy
    cloth = pl("#5d86c8", 0.9, spec=0.02)
    kit.box("tent.tbl", (6.2, 0.9, 0.82), (cx, cy + 2.0, 0.41), cloth, bevel=0.02)
    kit.box("tent.tbltop", (6.3, 1.0, 0.05), (cx, cy + 2.0, 0.845), pl("#6f96d8", 0.9, spec=0.02), bevel=0.01)
    kit.box("tent.tblskirt", (6.3, 0.05, 0.3), (cx, cy + 1.5, 0.62), pl("#f2c44c", 0.8, spec=0.02))
    doms = ["#d8c898", "#e8a8a0", "#a8d0b0"]
    for k, dx in enumerate((-2.3, -1.5, -0.7)):
        kit.sphere(f"tent.dome{k}", 0.28, (cx + dx, cy + 2.15, 0.9), pl(doms[k], 0.9, spec=0.02), seg=14)
        kit.cyl(f"tent.domebase{k}", 0.29, 0.07, (cx + dx, cy + 2.15, 0.885), pl(doms[k], 0.9, spec=0.02), n=14)
    # the bell: brass hemisphere on a base
    brass = pl("#d8a93b", 0.25, spec=0.9)
    kit.cyl("tent.bellbase", 0.15, 0.04, (cx + 0.5, cy + 2.35, 0.89), brass, n=16)
    kit.sphere("tent.bell", 0.12, (cx + 0.5, cy + 2.35, 0.9), brass, seg=14)
    kit.sphere("tent.bellknob", 0.03, (cx + 0.5, cy + 2.35, 1.03), brass, seg=8)
    # a second small table for the banner
    kit.box("tent.tbl2", (2.4, 0.9, 0.8), (cx - 3.6, cy + 2.0, 0.4), pl("#d9a050", 0.7), bevel=0.02)
    # folding chairs along the right wall
    for k in range(4):
        chair(kit, f"tent.ch{k}", cx + 5.4, cy - 2.0 + 1.1 * k, 90, "#d8d4cc" if False else "#7d9ad0")
    # the trophy: a plain gold cup, moved by cue
    gold = pl("#e8b830", 0.25, spec=0.9)
    tr = kit.empty("trophy", (cx, cy + 2.4, 0.9))
    kit.cyl("trophy.base", 0.12, 0.06, (0, 0, 0.03), gold, tr, n=14)
    kit.cyl("trophy.stem", 0.04, 0.2, (0, 0, 0.16), gold, tr, n=10)
    kit.cyl("trophy.cup", 0.12, 0.2, (0, 0, 0.36), gold, tr, n=16, r2=0.17)
    for sx in (-1, 1):
        kit.box(f"trophy.h{sx}", (0.04, 0.03, 0.12), (sx * 0.19, 0, 0.38), gold, tr)
        kit.box(f"trophy.h2{sx}", (0.1, 0.03, 0.03), (sx * 0.15, 0, 0.44), gold, tr)
    W["trophy"] = tr
    # the banner (a painted picture, no letters) hung over the front of the second table
    bn = kit.empty("banner", (cx - 3.6, cy + 1.53, 0))
    W["banner"] = bn
    kit.box("banner.cloth", (1.9, 0.02, 0.8), (0, 0, 0.4), pl("#8ac8f0", 0.9, spec=0.02), bn)
    kit.box("banner.hem", (1.94, 0.03, 0.05), (0, -0.005, 0.03), pl("#e8587a", 0.8), bn)
    kit.box("banner.hem2", (1.94, 0.03, 0.05), (0, -0.005, 0.77), pl("#e8587a", 0.8), bn)
    kit.box("banner.grass", (1.9, 0.03, 0.12), (0, -0.01, 0.1), pl("#74c860", 0.9), bn)
    # the painted Grandma holding up a cup: lavender body, face, white puff, gold cup
    kit.box("banner.body", (0.5, 0.03, 0.34), (0, -0.02, 0.28), pl("#a98ad8", 0.8), bn)
    kit.box("banner.puff", (0.52, 0.03, 0.3), (0, -0.02, 0.62), pl("#f4f0fa", 0.8), bn)
    kit.box("banner.head", (0.34, 0.03, 0.26), (0, -0.03, 0.55), pl("#f1c9a0", 0.8), bn)
    for sx in (-1, 1):
        kit.box(f"banner.eye{sx}", (0.05, 0.03, 0.06), (sx * 0.08, -0.05, 0.57), pl("#2a1a14", 0.7), bn)
        kit.box(f"banner.arm{sx}", (0.1, 0.03, 0.34), (sx * 0.34, -0.02, 0.42), pl("#a98ad8", 0.8), bn, rot=(0, sx * 0.35, 0))
        kit.box(f"banner.star{sx}", (0.16, 0.03, 0.16), (sx * 0.75, -0.02, 0.5), pl("#f2c230", 0.6), bn, rot=(0, 0.785, 0))
        kit.box(f"banner.star2{sx}", (0.1, 0.03, 0.1), (sx * 0.55, -0.02, 0.68), pl("#e8587a", 0.6), bn, rot=(0, 0.785, 0))
    kit.box("banner.mouth", (0.14, 0.03, 0.03), (0, -0.05, 0.48), pl("#2a1a14", 0.7), bn)
    kit.cyl("banner.cup", 0.07, 0.16, (0.0, -0.035, 0.74), pl("#e8b830", 0.3, spec=0.8), bn, rot=(math.pi / 2, 0, 0), n=12, r2=0.1)
    for sx in (-1, 1):
        kit.box(f"banner.rope{sx}", (0.05, 0.05, 0.1), (sx * 0.8, 0.0, 0.82), pl("#4a3a2e", 0.7), bn)
    # a pie on a plate in front of judge A (Grandma's), shown by the pie cue
    pp = kit.empty("tent.gpie", (cx - 0.9, cy + 1.85, 0.87))
    pie(kit, "tent.gpie.p", 0, 0, 0, 0.2, "#c98a3a", pp)
    kit.cyl("tent.gpie.plate", 0.27, 0.02, (0, 0, 0.0), pl("#cfd8e0", 0.3, spec=0.6), pp, n=20)
    W["gpie"] = pp
    # the scarf, a trophy and the aunt's scarf are moved by cues
    sc = kit.empty("scarf", (0, 0, -30))
    kit.box("scarf.a", (0.34, 0.2, 0.08), (0, 0, 0), pl("#d8322f", 0.9, spec=0.02), sc, bevel=0.03)
    kit.box("scarf.b", (0.34, 0.2, 0.025), (0, 0, 0.0525), pl("#f4ecd0", 0.9, spec=0.02), sc)
    kit.box("scarf.c", (0.34, 0.2, 0.025), (0, 0, -0.0525), pl("#3a6fd0", 0.9, spec=0.02), sc)
    for k in range(3):
        kit.box(f"scarf.s{k}", (0.07, 0.205, 0.095), (-0.12 + 0.12 * k, 0, 0), pl("#f4ecd0" if k % 2 else "#2f58a8", 0.9, spec=0.02), sc)
    W["scarf"] = sc


# ---------------------------------------------------------------------------------------------- the rule tag
DIGIT_SEGS = {0: "abcdef", 1: "bc", 2: "abged", 3: "abgcd", 4: "fgbc", 5: "afgcd", 6: "afgedc", 7: "abc", 8: "abcdefg",
              9: "abcdfg"}


def build_tag(kit):
    cam = kit.OBJ["cam"]
    root = kit.empty("tag", (0, 0, 0), cam)
    W["tag"] = root
    edge = kit.emit("#2b2118", 0.6, "tagedge")
    plate = kit.emit("#f2e6c8", 0.85, "tagplate")
    ink = kit.emit("#2b2118", 0.6, "tagink")
    red = kit.emit("#d8322f", 0.8, "tagred")
    white = kit.emit("#fbf6e6", 0.9, "tagwhite")

    def b(name, size, loc, mat):
        ob = kit.box(name, size, loc, mat, root)
        noshadow(ob)
        return ob

    b("tag.edge", (1.62, 0.86, 0.006), (0, 0, 0), edge)
    b("tag.plate", (1.56, 0.8, 0.006), (0, 0, 0.007), plate)
    z = 0.016
    # the poster glyph: a dark-edged sheet with a big red question mark
    b("tag.pedge", (0.58, 0.7, 0.006), (-0.44, 0.0, z), ink)
    b("tag.psheet", (0.5, 0.62, 0.006), (-0.44, 0.0, z + 0.002), white)
    z2 = z + 0.004
    b("tag.q1", (0.28, 0.08, 0.006), (-0.44, 0.21, z2), red)
    b("tag.q2", (0.09, 0.22, 0.006), (-0.34, 0.1, z2), red)
    b("tag.q3", (0.2, 0.08, 0.006), (-0.4, -0.03, z2), red)
    b("tag.q4", (0.09, 0.12, 0.006), (-0.44, -0.1, z2), red)
    b("tag.q5", (0.1, 0.1, 0.006), (-0.44, -0.24, z2), red)
    b("tag.divider", (0.015, 0.6, 0.006), (-0.05, 0.0, z), ink)
    W["digits"] = {}

    def digit_set(label, cx, cy, dw=0.15, dh=0.48, t=0.055):
        pos = {"a": (0, dh / 2 - t / 2, dw, t), "g": (0, 0, dw, t), "d": (0, -dh / 2 + t / 2, dw, t),
               "f": (-dw / 2 + t / 2, dh / 4, t, dh / 2), "b": (dw / 2 - t / 2, dh / 4, t, dh / 2),
               "e": (-dw / 2 + t / 2, -dh / 4, t, dh / 2), "c": (dw / 2 - t / 2, -dh / 4, t, dh / 2)}
        d = {}
        for k, (px, py, sw, sh) in pos.items():
            d[k] = b(f"tag.{label}{k}", (sw, sh, 0.006), (cx + px, cy + py, z), ink)
        return d

    W["digits"]["day"] = digit_set("d0", 0.45, 0.0, 0.46, 0.64, 0.12)
    W["clockrow"] = []
    p2 = b("tag.edge2", (1.62, 0.7, 0.006), (0, -0.74, 0.0), edge)
    p3 = b("tag.plate2", (1.56, 0.64, 0.006), (0, -0.74, 0.007), plate)
    W["clockrow"] += [p2, p3]
    cdig = [digit_set("c0", -0.5, -0.74, 0.22, 0.44, 0.06), digit_set("c1", -0.2, -0.74, 0.22, 0.44, 0.06),
            digit_set("c2", 0.26, -0.74, 0.22, 0.44, 0.06), digit_set("c3", 0.56, -0.74, 0.22, 0.44, 0.06)]
    dots = [b("tag.colon1", (0.08, 0.08, 0.006), (0.03, -0.66, z), ink), b("tag.colon2", (0.08, 0.08, 0.006), (0.03, -0.82, z), ink)]
    W["digits"]["clock"] = cdig
    W["clockrow"] += dots


def _digit(d, n):
    segs = DIGIT_SEGS.get(n, "") if n is not None else ""
    for k, ob in d.items():
        ob.hide_render = k not in segs


def set_tag(tl, t):
    tg = sample("tag", tl, t, {"n": 7, "clock": 0})
    n, clock = int(tg["n"]), int(tg["clock"])
    _digit(W["digits"]["day"], n)
    on = clock > 0
    for ob in W["clockrow"]:
        ob.hide_render = not on
    hh, mm = clock // 100, clock % 100
    vals = [hh // 10, hh % 10, mm // 10, mm % 10]
    for d, v in zip(W["digits"]["clock"], vals):
        _digit(d, v if on else None)


# ---------------------------------------------------------------------------------------------- build / animate
def build(kit, story, tl):
    W.clear()
    W.update(kit=kit, inited=False)
    tl["cues"].sort(key=lambda c: c["t"])
    sun = kit.light("sun", "SUN", (18, -27, 51), 1.0, "#fff1d6", size=0.06)
    sun.data.angle = 0.05
    kit.aim(sun, (0, 0, 0))
    fill = kit.light("fill", "SUN", (0, -10, 30), 1.0, "#e8f0ff", shadow=False)
    fill.data.angle = 0.5
    kit.aim(fill, (0, 0, 0))
    W["camkey"] = kit.light("camkey", "POINT", (0, 0, 5), 60, "#ffe9cc", size=0.5, shadow=False)
    W["camfill"] = kit.light("camfill", "POINT", (0, 0, 5), 40, "#fff4e4", size=0.8, shadow=False)
    for n in ("camkey", "camfill"):
        kit.LIGHTS[n]["obj"].visible_camera = False
    build_ground(kit)
    build_board(kit)
    build_mailbox(kit)
    house_front(kit, G.ADOOR, "#f2c27a", "#3a9aa0", "adoor")
    house_front(kit, G.GDOOR, "#c8a8e0", "#d8573a", "gdoor")
    build_car(kit)
    build_momk(kit)
    build_card(kit)
    build_grank(kit)
    build_tent(kit)
    build_tag(kit)
    # outdoor fills so faces toward the camera are never flat: the sun is behind the camera already
    for i, c in enumerate((G.CORNER, G.MAIL, G.ADOOR, G.GDOOR, G.CAR)):
        f = kit.light(f"outfill{i}", "AREA", (c[0], c[1] - 5.0, 4.0), 900, "#fff4e4", size=5.0, shadow=False)
        kit.aim(f, (c[0], c[1] + 1.5, 1.4))
    try:
        from blocky import polish
        W["camspecs"] = polish.cam_specs(story, tl, polish.spec(story))
    except Exception:
        W["camspecs"] = None
    W["shots"] = {s["id"]: s for s in story["shots"]}
    return {}


def late(kit):
    """Once the cast exists: my quiff, Grandma's puff, apron and watch, the flour, Mom's bob."""
    g = bpy.data.objects.get
    pl = kit.plastic
    W["flour"], W["watch"] = [], []
    for who in ("me", "me_b"):
        hg = g(f"{who}.headg")
        if hg is not None:
            hair = pl("#b4532c", 0.6)
            kit.box(f"{who}.quiff", (0.8, 0.62, 0.42), (0.02, -0.28, 0.76), hair, hg, rot=(-0.25, 0, 0), bevel=0.14)
            kit.box(f"{who}.quiff2", (0.5, 0.5, 0.3), (-0.12, -0.45, 0.88), hair, hg, rot=(-0.35, 0, 0.1), bevel=0.12)
    gh = g("grandma.headg")
    if gh is not None:
        white = pl("#ece8f2", 0.85, spec=0.05)
        kit.sphere("grandma.puff", 0.82, (0, 0.36, 0.3), white, gh, seg=14)
        for k in range(10):
            a = k * math.pi * 2 / 10
            kit.sphere(f"grandma.curl{k}", 0.2, (0.78 * math.cos(a), 0.36 + 0.5 * math.sin(a) * 0.4, 0.3 + 0.62 * math.sin(a) * 0.6 + 0.1),
                       white, gh, seg=8)
        for sx in (-1, 1):
            kit.sphere(f"grandma.sidecurl{sx}", 0.24, (sx * 0.64, 0.05, 0.1), white, gh, seg=8)
            kit.sphere(f"grandma.sidecurl2{sx}", 0.2, (sx * 0.66, -0.05, -0.12), white, gh, seg=8)
    gt = g("grandma.torso")
    if gt is not None:
        ap = pl("#f6d6e0", 0.8, spec=0.05)
        kit.box("grandma.apron", (1.5, 0.05, 1.7), (0, -0.54, 0.95), ap, gt, bevel=0.03)
        kit.box("grandma.apronb", (1.56, 0.05, 0.12), (0, -0.54, 1.86), ap, gt)
        for k, (dx, dz, col) in enumerate(((-0.4, 1.3, "#e8587a"), (0.2, 1.1, "#f2c230"), (-0.2, 0.7, "#e8587a"), (0.45, 0.55, "#f2c230"),
                                           (-0.5, 0.3, "#f2c230"), (0.05, 0.25, "#e8587a"))):
            kit.cyl(f"grandma.flower{k}", 0.1, 0.02, (dx, -0.58, dz), pl(col, 0.6), gt, rot=(math.pi / 2, 0, 0), n=8)
    for sx in (-1, 1):
        arm = g(f"grandma.arm{sx}")
        if arm is not None:
            W["flour"].append(kit.box(f"grandma.flour{sx}", (0.74, 1.06, 1.1), (0, 0, -1.25), pl("#ece6d8", 0.95, spec=0.02), arm, bevel=0.06))
    arm = g("grandma.arm1")
    if arm is not None:
        W["watch"] = [kit.box("grandma.watchband", (0.74, 1.04, 0.2), (0, 0, -1.7), pl("#8a5a34", 0.6), arm),
                      kit.box("grandma.watchface", (0.4, 0.1, 0.4), (0, -0.54, -1.7), pl("#f6f1e6", 0.4, spec=0.7), arm)]
    mh = g("mom.headg")
    if mh is not None:
        dark = pl("#2a1a1a", 0.65)
        kit.box("mom.bob", (1.62, 1.3, 0.7), (0, 0.22, 0.12), dark, mh, bevel=0.2)
        kit.box("mom.bobfringe", (1.3, 0.3, 0.3), (0, -0.55, 0.45), dark, mh, bevel=0.1)
    W["inited"] = True


def animate(kit, story, tl, t, ctx):
    if not W.get("inited"):
        late(kit)
    shot = next((s for s in tl["shots"] if s["start"] <= t < s["end"]), tl["shots"][-1])
    sd = W["shots"].get(shot["id"], {})
    try:
        from blocky import bl_story
        cl, ct, lens, _ = bl_story.cam_at(W["camspecs"][shot["id"]], shot, t, {}, tl)
    except Exception:
        k0 = sd.get("cam", [[0, [0, -3, 1.5], [0, 0, 1.5], 36]])[0]
        cl, ct, lens = k0[1], k0[2], k0[3]
    # the camera's own soft key and fill, scaled by distance, brighter indoors than out
    f = V(ct) - V(cl)
    dist = max(0.3, f.length)
    f.normalize()
    r = f.cross(V((0, 0, 1)))
    r = r.normalized() if r.length > 1e-6 else V((1, 0, 0))
    kpos = V(cl) - r * 0.7 + V((0, 0, 0.6))
    W["camkey"].location = (kpos.x, kpos.y, kpos.z)
    fpos = V(cl) + r * 0.9 + V((0, 0, 0.1))
    W["camfill"].location = (fpos.x, fpos.y, fpos.z)
    fg = min(2.2, max(0.05, (dist / 3.0) ** 2))
    indoor = cl[1] < -30
    gains = {"sun": 4.2, "fill": 1.2, "camkey": fg * (0.9 if indoor else 0.35) * sd.get("key", 1.0),
             "camfill": fg * (0.9 if indoor else 0.4) * sd.get("fill", 1.0)}
    # seated: legs level while the character sits
    sit = sample("sit", tl, t, {n: 0.0 for n in SEATED})
    for who in SEATED:
        s = sit[who]
        if s > 0.001:
            for sx in (-1, 1):
                leg = bpy.data.objects.get(f"{who}.leg{sx}")
                if leg:
                    leg.rotation_euler = (leg.rotation_euler.x * (1 - s) + SIT * s, 0, 0)
    fl = sample("flour", tl, t, {"on": 0.0})["on"] > 0.5
    for o in W.get("flour", []):
        o.hide_render = not fl
    for o in W.get("watch", []):
        o.hide_render = sample("watch", tl, t, {"on": 0.0})["on"] < 0.5
    tr = sample("trophy", tl, t, {"on": 0.0, "x": G.TENT[0], "y": G.TENT[1] + 2.4, "z": 0.9})
    W["trophy"].location = (tr["x"], tr["y"], tr["z"])
    W["trophy"].scale = (0.75, 0.75, 0.75)
    sc = sample("scarf", tl, t, {"on": 0.0, "x": 0.0, "y": 0.0, "z": -30.0})
    W["scarf"].location = (sc["x"], sc["y"], sc["z"] if sc["on"] > 0.5 else -30.0)
    hide(W["gpie"], sample("pie", tl, t, {"on": 0.0})["on"] < 0.5)
    ba = sample("banner", tl, t, {"on": 0.0})["on"] > 0.5
    W["banner"].location = (G.TENT[0] - 3.6, G.TENT[1] + 1.53, 0.0) if ba else (0, 0, -30)
    gp = sample("gposter", tl, t, {"on": 0.0})["on"] > 0.5
    for o in W["gposter"]:
        o.hide_render = not gp
    ty = sample("tally", tl, t, {"on": 0.0})["on"] > 0.5
    for o in W["tally"]:
        o.hide_render = not ty
    set_tag(tl, t)
    return gains
