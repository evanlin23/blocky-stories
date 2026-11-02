"""ep36-ice-huts: a frozen lake, a dozen painted fishing huts, a small town on the shore, an old estate car.

Places (metres; z = 0 is the snow and the ice, x < 0 is the town side of the shore, x > 0 the lake):
  the shore line x = 0 (pines, a slipway), the lake out to x = 250
  the red hut at RED = (30, 4): door in its -x wall, window in its +y wall, two stools over one hole
  the town street along y at x = -30 (café, my flat, the hedge lane, the bus stop, the square)
  the car's cabin far away at CAR = (200, -150)

Everything that changes in time reads the story's cues (story.json): "fog" (density ramps), "flame" (where each
flame leans), "door", "lamp", "curtain", "puff" (breath), "sun". Every light change is a smooth ramp (hard rule 7),
and the flames are steady: a constant emission, a slow lean and a gentle sway.
"""
import math

import bpy
from mathutils import Quaternion, Vector

from blocky import acting
from blocky import bl_story

RED = (30.0, 4.0)
CAR = (200.0, -150.0)
HUT_W, HUT_D, HUT_H, WALL = 3.0, 3.6, 2.15, 0.1
DOOR_Y0, DOOR_Y1, DOOR_H = -1.75, -0.05, 1.62          # local to the red hut: the doorway in the -x wall
WIN_X0, WIN_X1, WIN_Z0, WIN_Z1 = -0.2, 0.7, 0.9, 1.6  # the window in the +y wall
FLAME_H = 0.22
HEAD_TOP = 1.78          # a default character's head top (m), times its height
HATS = {"me": 0.12, "grandad": 0.22, "pell": 0.08, "fisher1": 0.1, "fisher2": 0.1, "fisher3": 0.1, "fisher4": 0.1,
        "owner": 0.0, "driver": 0.0, "newcomer": 0.0, "date_w": 0.0, "date_m": 0.0}
HEIGHT = {"leaner": 1.06}
FOG_FADE = {}


def _ss(x):
    x = min(1.0, max(0.0, x))
    return x * x * (3 - 2 * x)


def _cues(tl, name):
    return [c for c in tl.get("cues", []) if c["name"] == name]


def W(p, local):
    return (p[0] + local[0], p[1] + local[1], local[2])


# ------------------------------------------------------------------------------------------ materials
def materials(kit):
    M = {}
    M["snow"] = kit.plastic("#d6e0ea", 0.92, "snow")
    M["ice"] = kit.grime("#9fb4c4", dark=0.78, scale=0.35, name="ice", rough=0.62)
    M["slush"] = kit.plastic("#aeb9c4", 0.8, "slush")
    M["path"] = kit.plastic("#c3d0dc", 0.9, "bootpath")
    M["pine"] = kit.plastic("#1f3a2c", 0.9, "pine")
    M["pinesnow"] = kit.plastic("#cfd9e2", 0.9, "pinesnow")
    M["trunk"] = kit.plastic("#3a2a20", 0.9, "trunk")
    M["tar"] = kit.grime("#1d1b19", dark=0.6, scale=4.0, name="tar", rough=0.9)
    M["iron"] = kit.metal("#2a2b2d", 0.5, "iron")
    M["iron2"] = kit.metal("#3b3c3f", 0.45, "iron2")
    M["rust"] = kit.plastic("#8e3b1f", 0.7, "scratch rust")
    M["hole"] = kit.plastic("#0c1218", 0.2, "hole")
    M["stoolwood"] = kit.planks("#7a5a3a", "#5a4028", 3.0, "X", "stool")
    M["floor"] = kit.planks("#6e5438", "#4e3a26", 1.0, "X", "hutfloor")
    M["wool"] = kit.plastic("#8a6a55", 0.95, "wool blanket")
    M["wool2"] = kit.plastic("#6c4a3c", 0.95, "wool stripe")
    M["lamp"] = kit.plastic("#d9a96a", 0.4, "lamp body")
    M["glass"] = kit.glass("#c8d8e0", "hutglass")
    M["curtain"] = kit.checker("#c8b79a", "#8e5a48", 14.0, "curtain", 0.95)
    M["stove"] = kit.metal("#1f2022", 0.55, "stove")
    M["hedge"] = kit.plastic("#27432f", 0.95, "hedge")
    M["brickA"] = kit.bricks("#7a3b2a", "#5e2c22", "#8a8680", 1.2, "brickA")
    M["brickB"] = kit.bricks("#8a5a3c", "#6a432c", "#8a8680", 1.2, "brickB")
    M["timberA"] = kit.planks("#b8a27a", "#9a845e", 1.2, "Z", "timberA")
    M["timberB"] = kit.planks("#8aa0a0", "#6c8484", 1.2, "Z", "timberB")
    M["roofA"] = kit.plastic("#4a3a3a", 0.8, "roofA")
    M["roofS"] = kit.plastic("#cfd8e2", 0.9, "roofS")
    M["trim"] = kit.plastic("#d8d2c4", 0.7, "trim")
    M["doorB"] = kit.plastic("#3d5a6a", 0.6, "doorB")
    M["doorC"] = kit.plastic("#7a3030", 0.6, "doorC")
    M["road"] = kit.plastic("#7c8794", 0.9, "road")
    M["kerb"] = kit.plastic("#aab2ba", 0.8, "kerb")
    M["warm"] = kit.emit("#ffb060", 3.2, "windowwarm")
    M["lampglow"] = kit.emit("#ffc27a", 3.2, "lampglow")
    M["bench"] = kit.plastic("#6b4a2e", 0.7, "bench")
    M["van"] = kit.plastic("#c9ccd0", 0.5, "van")
    M["vandark"] = kit.plastic("#2b2e33", 0.6, "vandark")
    M["tyre"] = kit.plastic("#16181a", 0.8, "tyre")
    M["table"] = kit.plastic("#8a6a48", 0.6, "table")
    M["cloth"] = kit.plastic("#b5c9c2", 0.9, "tablecloth")
    M["counter"] = kit.plastic("#5a3d2a", 0.6, "counter")
    M["carseat"] = kit.plastic("#8a7658", 0.95, "carseat")
    M["carbody"] = kit.plastic("#41484a", 0.75, "carbody")
    M["carwin"] = kit.emit("#070b10", 1.0, "carnight")
    M["vent"] = kit.emit("#ff9a3c", 2.4, "ventglow")
    M["paint"] = {}
    for name, hexc in (("red", "#a8322a"), ("teal", "#2f7f7a"), ("mustard", "#c9a03a"), ("sage", "#8aa37a"),
                       ("white", "#e6e2d8")):
        c = hexc.lstrip("#")
        dark = "#" + "".join(f"{int(int(c[i:i + 2], 16) * 0.82):02x}" for i in (0, 2, 4))
        M["paint"][name] = (kit.planks(hexc, dark, 1.0, "X", f"paintX {name}"), kit.planks(hexc, dark, 1.0, "Z", f"paintZ {name}"),
                            kit.plastic(hexc, 0.7, f"paint {name}"))
    return M


# ------------------------------------------------------------------------------------------ the lake, the shore
def build_ground(kit, M):
    kit.plane("ice", (900, 900), (125, 0, 0), M["ice"])
    kit.plane("land", (160, 300), (-82, 0, 0.004), M["snow"])
    kit.plane("shore slush", (3.5, 300), (0.4, 0, 0.006), M["slush"])
    # drifts on the lake and the shore
    import random
    rnd = random.Random(7)
    for i in range(70):
        x, y = rnd.uniform(-6, 110), rnd.uniform(-45, 45)
        r = rnd.uniform(0.7, 2.2)
        d = kit.sphere(f"drift{i}", r, (x, y, 0.0), M["snow"], seg=10)
        d.scale = (1.0, rnd.uniform(0.7, 1.3), 0.16)
    # boot paths from the shore to the huts (flush darker strips)
    for i, (y, x1) in enumerate(((3.35, 28.0), (-2.5, 28.0), (9.0, 28.0), (-9, 28), (3.35, 66.0))):
        kit.plane(f"path{i}", (x1 - 1.0, 0.7), ((x1 + 1.0) / 2, y, 0.012), M["path"])
    for k, (x, y0, y1) in enumerate(((12.0, -18.0, 20.0), (28.5, -14.0, 24.0))):
        kit.plane(f"rowpath{k}", (0.6, y1 - y0), (x, (y0 + y1) / 2, 0.013), M["path"])
    # pines along the shore
    for i in range(34):
        y = -46 + i * 2.75 + rnd.uniform(-0.6, 0.6)
        x = rnd.uniform(-9, -3.5)
        tree(kit, M, f"pine{i}", x, y, rnd.uniform(3.0, 5.2))
    for i in range(8):                       # a few more across the far end so the shore line reads
        tree(kit, M, f"farpine{i}", rnd.uniform(-14, -8), rnd.uniform(-40, 40), rnd.uniform(4, 6))
    # the slipway: packed snow ramp down to the ice, and a pair of posts
    kit.box("slipway", (8.0, 3.2, 0.1), (3.0, -4.0, 0.05), M["path"], rot=(0, 0, 0))
    for sy in (-2.3, -5.7):
        kit.cyl(f"slipost{sy}", 0.09, 1.0, (1.8, sy, 0.5), M["trunk"], n=8)


def tree(kit, M, name, x, y, h):
    kit.cyl(f"{name}.t", 0.12, h * 0.25, (x, y, h * 0.125), M["trunk"], n=8)
    for k in range(4):
        z = h * (0.2 + 0.2 * k)
        r = (1.25 - 0.27 * k) * h / 4.0
        kit.cyl(f"{name}.c{k}", r, h * 0.3, (x, y, z + h * 0.12), M["pine"], n=10, r2=r * 0.15)
        kit.cyl(f"{name}.s{k}", r * 0.62, h * 0.06, (x, y, z + h * 0.2), M["pinesnow"], n=10, r2=r * 0.1)


# ------------------------------------------------------------------------------------------ the huts
def hut(kit, M, name, cx, cy, paint, red=False):
    pX, pZ, pF = M["paint"][paint]
    z0 = 0.0
    T = WALL
    parts = {}
    if not red:
        kit.box(f"{name}.body", (HUT_W, HUT_D, HUT_H), (cx, cy, HUT_H / 2), pZ, bevel=0.02)
        kit.box(f"{name}.door", (0.05, 1.0, 1.4), (cx - HUT_W / 2 - 0.02, cy - 0.6, 0.7), M["stove"])
        kit.box(f"{name}.sill", (0.03, 0.7, 0.5), (cx - 0.1, cy + HUT_D / 2 + 0.01, 1.2), M["stove"])
    else:
        # the four walls round a hollow room
        kit.box(f"{name}.back", (T, HUT_D, HUT_H), (cx + HUT_W / 2 - T / 2, cy, HUT_H / 2), pX)
        kit.box(f"{name}.wy-", (HUT_W, T, HUT_H), (cx, cy - HUT_D / 2 + T / 2, HUT_H / 2), pZ)
        # the front: the wall left of the doorway (y > door's top edge), the lintel over it
        y_lo = DOOR_Y1
        kit.box(f"{name}.front", (T, HUT_D / 2 - y_lo, HUT_H), (cx - HUT_W / 2 + T / 2, cy + (y_lo + HUT_D / 2) / 2, HUT_H / 2), pX)
        kit.box(f"{name}.lintel", (T, DOOR_Y1 - DOOR_Y0, HUT_H - DOOR_H), (cx - HUT_W / 2 + T / 2, cy + (DOOR_Y0 + DOOR_Y1) / 2,
                                                                          (HUT_H + DOOR_H) / 2), pX)
        # the +y wall with its window
        yw = cy + HUT_D / 2 - T / 2
        kit.box(f"{name}.wy+b", (HUT_W, T, WIN_Z0), (cx, yw, WIN_Z0 / 2), pZ)
        kit.box(f"{name}.wy+t", (HUT_W, T, HUT_H - WIN_Z1), (cx, yw, (HUT_H + WIN_Z1) / 2), pZ)
        kit.box(f"{name}.wy+l", (WIN_X0 + HUT_W / 2, T, WIN_Z1 - WIN_Z0), (cx + (-HUT_W / 2 + WIN_X0) / 2, yw, (WIN_Z0 + WIN_Z1) / 2), pZ)
        kit.box(f"{name}.wy+r", (HUT_W / 2 - WIN_X1, T, WIN_Z1 - WIN_Z0), (cx + (HUT_W / 2 + WIN_X1) / 2, yw, (WIN_Z0 + WIN_Z1) / 2), pZ)
        # the four-pane window: glass, a cross of frame, the sill
        wx, wz = cx + (WIN_X0 + WIN_X1) / 2, (WIN_Z0 + WIN_Z1) / 2
        kit.box(f"{name}.pane", (WIN_X1 - WIN_X0, 0.012, WIN_Z1 - WIN_Z0), (wx, yw, wz), M["glass"])
        kit.box(f"{name}.mullv", (0.04, 0.05, WIN_Z1 - WIN_Z0), (wx, yw, wz), M["trim"])
        kit.box(f"{name}.mullh", (WIN_X1 - WIN_X0, 0.05, 0.04), (wx, yw, wz), M["trim"])
        kit.box(f"{name}.wsill", (WIN_X1 - WIN_X0 + 0.16, 0.14, 0.05), (wx, yw + 0.06, WIN_Z0 - 0.02), M["trim"])
        # floor boards, the hole, two stools, a stove, a shelf, a lamp on a hook
        kit.box(f"{name}.floor", (HUT_W, HUT_D, 0.05), (cx, cy, 0.0), M["floor"])
        hx, hy = cx + 0.2, cy + 0.4
        kit.cyl(f"{name}.hole", 0.22, 0.01, (hx, hy, 0.03), M["hole"], n=24)
        for k, sx in enumerate((-0.35, 0.75)):
            sx_, sy_ = cx + sx, cy + 0.4
            kit.cyl(f"{name}.stool{k}", 0.2, 0.05, (sx_, sy_, 0.42), M["stoolwood"], n=14)
            for lx, ly in ((0.12, 0.12), (-0.12, 0.12), (0.12, -0.12), (-0.12, -0.12)):
                kit.box(f"{name}.stool{k}.leg{lx}{ly}", (0.05, 0.05, 0.4), (sx_ + lx, sy_ + ly, 0.2), M["stoolwood"])
        kit.box(f"{name}.stove", (0.55, 0.45, 0.7), (cx + HUT_W / 2 - 0.4, cy - 1.0, 0.35), M["stove"], bevel=0.02)
        kit.cyl(f"{name}.stovepipe_in", 0.07, 1.5, (cx + HUT_W / 2 - 0.4, cy - 1.0, 1.45), M["stove"], n=10)
        kit.box(f"{name}.shelf", (0.25, 1.4, 0.04), (cx + HUT_W / 2 - 0.2, cy + 0.6, 1.3), M["stoolwood"])
        for k in range(3):
            kit.cyl(f"{name}.tin{k}", 0.05, 0.12, (cx + HUT_W / 2 - 0.2, cy + 0.2 + 0.35 * k, 1.38), M["iron2"], n=10)
        kit.box(f"{name}.hook", (0.03, 0.03, 0.4), (cx + 0.2, cy + 0.85, HUT_H - 0.25), M["iron"])
        lamp = kit.cyl(f"{name}.lampglass", 0.07, 0.17, (cx + 0.2, cy + 0.85, HUT_H - 0.6), M["lampglow"], n=12)
        kit.cyl(f"{name}.lampbase", 0.09, 0.05, (cx + 0.2, cy + 0.85, HUT_H - 0.7), M["lamp"], n=12)
        parts["lampglass"] = lamp
        # the blanket folded on the second stool
        kit.box(f"{name}.blanket", (0.4, 0.34, 0.1), (cx + 0.75, cy + 0.4, 0.52), M["wool"], bevel=0.04)
        kit.box(f"{name}.blanket2", (0.41, 0.1, 0.105), (cx + 0.75, cy + 0.4, 0.525), M["wool2"], bevel=0.03)
        # the curtain on the window's inside: a checked panel on a pivot that swings shut
        piv = kit.empty(f"{name}.curtpiv", (wx - 0.45, yw - 0.07, wz))
        kit.box(f"{name}.curtain", (0.9, 0.025, WIN_Z1 - WIN_Z0 + 0.06), (0.45, 0, 0), M["curtain"], piv)
        piv.scale = (0.12, 1, 1)
        parts["curtain"] = piv
        # the door on its hinge (right jamb): planks, an iron thumb latch with a scratched plate
        hinge = kit.empty(f"{name}.hinge", (cx - HUT_W / 2 + 0.03, cy + DOOR_Y0, 0.0))
        kit.box(f"{name}.leaf", (0.05, DOOR_Y1 - DOOR_Y0, DOOR_H - 0.02), (0.0, (DOOR_Y1 - DOOR_Y0) / 2, DOOR_H / 2), pX, hinge)
        lx, ly, lz = -0.04, (DOOR_Y1 - DOOR_Y0) - 0.22, 0.95
        kit.box(f"{name}.platelatch", (0.015, 0.2, 0.09), (lx, ly, lz), M["iron"], hinge, bevel=0.004)
        kit.box(f"{name}.bar", (0.02, 0.26, 0.022), (lx - 0.012, ly - 0.03, lz + 0.075), M["iron2"], hinge, rot=(0.12, 0, 0), bevel=0.006)
        kit.box(f"{name}.thumb", (0.02, 0.04, 0.07), (lx - 0.012, ly + 0.07, lz + 0.11), M["iron2"], hinge, bevel=0.006)
        for k, dy in enumerate((-0.035, 0.025)):     # lore: two short rust-red strokes scratched in the plate
            kit.box(f"{name}.scratch{k}", (0.004, 0.012, 0.062), (lx - 0.0105, ly + dy, lz - 0.003), M["rust"], hinge,
                    rot=(0, 0.35 if k else -0.2, 0))
        parts["hinge"] = hinge
    # roof, stovepipe, snow cap
    kit.box(f"{name}.roof", (HUT_W + 0.3, HUT_D + 0.3, 0.1), (cx, cy, HUT_H + 0.05), M["tar"], rot=(0, 0.04, 0))
    kit.box(f"{name}.roofsnow", (HUT_W + 0.1, HUT_D + 0.1, 0.07), (cx, cy, HUT_H + 0.14), M["snow"], rot=(0, 0.04, 0), bevel=0.03)
    kit.cyl(f"{name}.pipe", 0.07, 0.6, (cx + HUT_W / 2 - 0.4, cy - 1.0, HUT_H + 0.4), M["stove"], n=10)
    kit.cyl(f"{name}.pipecap", 0.1, 0.04, (cx + HUT_W / 2 - 0.4, cy - 1.0, HUT_H + 0.72), M["stove"], n=10)
    # snow banked at the foot
    for k, (dx, dy, sx, sy) in enumerate(((0, -HUT_D / 2 - 0.2, 1.8, 0.45), (0, HUT_D / 2 + 0.2, 1.8, 0.45),
                                          (HUT_W / 2 + 0.2, 0, 0.45, 1.5))):
        d = kit.sphere(f"{name}.bank{k}", 1.0, (cx + dx, cy + dy, 0.0), M["snow"], seg=10)
        d.scale = (sx, sy, 0.22)
    return parts


# a fishing hole with a little flagged stick
def hole(kit, M, name, x, y, flag="#d65a3a"):
    kit.cyl(f"{name}.h", 0.2, 0.02, (x, y, 0.014), M["hole"], n=16)
    kit.cyl(f"{name}.stick", 0.012, 0.9, (x + 0.35, y, 0.45), M["trunk"], n=6)
    kit.box(f"{name}.flag", (0.22, 0.01, 0.12), (x + 0.45, y, 0.84), kit.plastic(flag, 0.8, "flag " + flag))


def build_huts(kit, M):
    layout = [(13, -14, "teal"), (13, -3.2, "mustard"), (13, 3.4, "white"), (13, 14, "sage"),
              (30, -14, "white"), (30, -4, "mustard"), (30, 12.4, "teal"), (30, 22, "sage"),
              (48, -10, "teal"), (50, 2, "white"), (48, 18, "mustard"), (68, 8, "sage"), (72, -8, "mustard"),
              (90, 6, "teal")]
    for i, (x, y, p) in enumerate(layout):
        hut(kit, M, f"hut{i}", x, y, p)
    parts = hut(kit, M, "red", RED[0], RED[1], "red", red=True)
    for i, (x, y, c) in enumerate(((10.8, -3.5, "#d65a3a"), (10.8, 10.5, "#e8c04a"), (27.6, -1.6, "#4a8ad6"),
                                   (27.6, -11.5, "#d65a3a"), (46, -7.0, "#e8c04a"), (47, 5.0, "#4a8ad6"),
                                   (20, -6, "#d65a3a"), (22, 8, "#e8c04a"), (60, 2, "#d65a3a"))):
        hole(kit, M, f"hole{i}", x, y, c)
    return parts


# ------------------------------------------------------------------------------------------ the town
def house(kit, M, name, x, y, w, d, h, face, wallmat, roofmat, door_mat, windows=2, door=True, lit=True):
    """A house whose front looks toward `face` (+1: +x, -1: -x). x is the front face's x; the body sits behind it."""
    cx = x - face * d / 2
    kit.box(f"{name}.b", (d, w, h), (cx, y, h / 2), wallmat)
    # a pitched roof: two slabs and a snow cap
    for s in (-1, 1):
        kit.box(f"{name}.r{s}", (d + 0.5, w / 2 + 0.5, 0.12), (cx, y + s * w / 4, h + w * 0.1), roofmat, rot=(-s * 0.4, 0, 0))
        kit.box(f"{name}.rs{s}", (d + 0.5, w / 2 + 0.4, 0.08), (cx, y + s * w / 4, h + w * 0.1 + 0.1), M["roofS"], rot=(-s * 0.4, 0, 0), bevel=0.03)
    for k in range(windows):
        wy = y + (k - (windows - 1) / 2) * (w / (windows + 0.4))
        for z in (1.5, h - 1.5) if h > 5.5 else (1.6,):
            kit.box(f"{name}.w{k}{z}", (0.06, 1.0, 1.1), (x + face * 0.01, wy, z), M["warm"] if lit else M["glass"])
            kit.box(f"{name}.wf{k}{z}", (0.1, 1.2, 1.3), (x + face * 0.0, wy, z), M["trim"])
    if door:
        kit.box(f"{name}.door", (0.08, 1.0, 2.0), (x + face * 0.03, y - w / 2 + 1.1, 1.0), door_mat)
        kit.box(f"{name}.step", (0.7, 1.4, 0.2), (x + face * 0.4, y - w / 2 + 1.1, 0.1), M["kerb"])


def build_town(kit, M):
    kit.box("road", (5.0, 90.0, 0.02), (-30.0, 0, 0.012), M["road"])
    for s in (-1, 1):
        kit.box(f"kerb{s}", (0.22, 90.0, 0.12), (-30.0 + s * 2.6, 0, 0.06), M["kerb"])
    # west side, the square and the bus stop
    for k, y in enumerate((-30, -22, 18, 28, 36)):
        house(kit, M, f"wh{k}", -42, y, 7, 6, 6.4, 1, M["brickB"] if k % 2 else M["timberA"], M["roofA"], M["doorB"])
    # the bus stop (west pavement), the bench in the square
    kit.box("bs.roof", (1.4, 3.0, 0.1), (-34.4, 8.0, 2.4), M["tar"])
    for sy in (6.6, 9.4):
        kit.box(f"bs.post{sy}", (0.08, 0.08, 2.4), (-33.8, sy, 1.2), M["iron2"])
    kit.box("bs.back", (0.06, 3.0, 1.3), (-35.0, 8.0, 1.25), M["glass"])
    kit.box("bs.seat", (0.5, 2.2, 0.06), (-34.7, 8.0, 0.5), M["bench"])
    kit.box("bs.seatleg", (0.4, 2.0, 0.5), (-34.7, 8.0, 0.25), M["iron2"])
    kit.box("bench.seat", (0.5, 1.8, 0.06), (-37.0, -1.5, 0.48), M["bench"])
    kit.box("bench.back", (0.06, 1.8, 0.5), (-37.25, -1.5, 0.78), M["bench"])
    for sy in (-2.3, -0.7):
        kit.box(f"bench.leg{sy}", (0.4, 0.06, 0.48), (-37.0, sy, 0.24), M["iron2"])
    # east side: the hedge lane
    kit.box("hedge", (1.2, 14.0, 1.7), (-25.8, 12.0, 0.85), M["hedge"], bevel=0.25)
    kit.box("hedge.snow", (1.0, 13.6, 0.12), (-25.8, 12.0, 1.7), M["snow"], bevel=0.05)
    kit.box("hedge.end", (1.0, 0.5, 1.7), (-25.8, 4.6, 0.85), M["hedge"], bevel=0.2)
    for k, y in enumerate((10, 22)):
        house(kit, M, f"eh{k}", -19, y, 7, 6, 6.0, -1, M["timberB"], M["roofA"], M["doorC"])
    for k, y in enumerate((28, 38)):
        house(kit, M, f"ee{k}", -26, y, 7, 6, 6.4, -1, M["brickA"], M["roofA"], M["doorC"])
    # my flat, the door at (−26, −11.7)
    house(kit, M, "flat", -26, -13, 9, 7, 6.6, -1, M["brickA"], M["roofA"], M["doorC"], windows=2, lit=False)
    house(kit, M, "flat2", -26, -24, 8, 7, 6.6, -1, M["brickB"], M["roofA"], M["doorB"], windows=2, lit=True)
    # the café: a hollow room with a big window on the street, a table by the window, a counter behind
    cx0, cx1, cy0, cy1, ch = -26.0, -19.0, -8.0, 2.0, 3.2
    kit.box("cafe.back", (0.2, cy1 - cy0, ch), (cx1, (cy0 + cy1) / 2, ch / 2), M["timberA"])
    kit.box("cafe.s-", (cx1 - cx0, 0.2, ch), ((cx0 + cx1) / 2, cy0, ch / 2), M["timberA"])
    kit.box("cafe.s+", (cx1 - cx0, 0.2, ch), ((cx0 + cx1) / 2, cy1, ch / 2), M["timberA"])
    kit.box("cafe.floor", (cx1 - cx0, cy1 - cy0, 0.05), ((cx0 + cx1) / 2, (cy0 + cy1) / 2, 0.02), M["floor"])
    kit.box("cafe.roof", (cx1 - cx0 + 0.6, cy1 - cy0 + 0.6, 0.15), ((cx0 + cx1) / 2, (cy0 + cy1) / 2, ch + 0.08), M["tar"])
    kit.box("cafe.roofsnow", (cx1 - cx0 + 0.4, cy1 - cy0 + 0.4, 0.08), ((cx0 + cx1) / 2, (cy0 + cy1) / 2, ch + 0.2), M["snow"], bevel=0.03)
    # the front wall: pieces round a big window (y -5.5 .. -0.5, z 0.8 .. 2.4)
    kit.box("cafe.fl", (0.2, 2.5, ch), (cx0, cy0 + 1.25, ch / 2), M["timberA"])
    kit.box("cafe.fr", (0.2, 2.5, ch), (cx0, cy1 - 1.25, ch / 2), M["timberA"])
    kit.box("cafe.fb", (0.2, 5.0, 0.8), (cx0, -3.0, 0.4), M["timberA"])
    kit.box("cafe.ft", (0.2, 5.0, ch - 2.4), (cx0, -3.0, (ch + 2.4) / 2), M["timberA"])
    kit.box("cafe.table", (1.0, 0.8, 0.05), (-24.5, -3.0, 0.75), M["table"])
    kit.cyl("cafe.tleg", 0.05, 0.75, (-24.5, -3.0, 0.38), M["iron2"], n=8)
    for k, dy in enumerate((-0.75, 0.75)):
        kit.box(f"cafe.chair{k}", (0.42, 0.42, 0.05), (-24.5, -3.0 + dy, 0.45), M["bench"])
        kit.box(f"cafe.chairb{k}", (0.42, 0.05, 0.5), (-24.5, -3.0 + dy + (0.2 if dy > 0 else -0.2), 0.7), M["bench"])
    kit.box("cafe.counter", (0.7, 4.6, 1.0), (-21.0, -3.0, 0.5), M["counter"], bevel=0.02)
    kit.box("cafe.top", (0.9, 4.8, 0.06), (-21.0, -3.0, 1.03), M["table"])
    for k, y in enumerate((-4.5, -1.6)):
        kit.cyl(f"cafe.cup{k}", 0.05, 0.08, (-21.0, y, 1.1), M["trim"], n=10)
    kit.box("cafe.lamp", (1.5, 1.0, 0.04), (-23.0, -3.0, ch - 0.05), M["warm"])
    # a plain removal van at the kerb, east side near the flat
    vx, vy = -27.9, -12.0
    kit.box("van.body", (2.1, 5.2, 2.4), (vx, vy - 0.6, 1.5), M["van"], bevel=0.05)
    kit.box("van.cab", (2.1, 1.7, 1.7), (vx, vy + 2.7, 1.1), M["van"], bevel=0.05)
    kit.box("van.win", (2.12, 1.1, 0.7), (vx, vy + 2.9, 1.5), M["vandark"])
    kit.box("van.base", (2.1, 6.9, 0.35), (vx, vy + 0.4, 0.38), M["vandark"])
    for wy in (vy - 1.6, vy + 2.4):
        for sx in (-1, 1):
            kit.cyl(f"van.tyre{wy}{sx}", 0.38, 0.25, (vx + sx * 1.0, wy, 0.38), M["tyre"], rot=(0, math.pi / 2, 0), n=14)
    # lamp posts down the street
    for k, y in enumerate(range(-30, 32, 12)):
        kit.cyl(f"post{k}", 0.05, 3.8, (-27.6, y, 1.9), M["iron2"], n=8)
        kit.sphere(f"postl{k}", 0.15, (-27.6, y, 3.9), M["warm"], seg=8)


# ------------------------------------------------------------------------------------------ the car
def build_car(kit, M):
    cx, cy = CAR
    z_roof = 2.05
    kit.box("car.floor", (1.9, 3.6, 0.1), (cx, cy + 0.5, -0.05), M["carbody"])
    kit.box("car.roof", (1.9, 3.6, 0.1), (cx, cy + 0.5, z_roof + 0.05), M["carbody"])
    for s in (-1, 1):
        kit.box(f"car.side{s}", (0.1, 3.6, 0.9), (cx + s * 0.95, cy + 0.5, 0.45), M["carbody"])
        kit.box(f"car.win{s}", (0.04, 3.4, 0.85), (cx + s * 0.96, cy + 0.5, 1.5), M["carwin"])
        kit.box(f"car.pillar{s}", (0.1, 0.12, 0.8), (cx + s * 0.95, cy + 0.5, 1.9), M["carbody"])
    kit.box("car.rear", (1.9, 0.1, 2.0), (cx, cy + 2.3, 1.0), M["carbody"])
    kit.box("car.rearwin", (1.5, 0.04, 0.8), (cx, cy + 2.24, 1.5), M["carwin"])
    kit.box("car.front", (1.9, 0.1, 0.8), (cx, cy - 1.35, 0.4), M["carbody"])
    kit.box("car.dash", (1.8, 0.6, 0.5), (cx, cy - 1.05, 0.65), M["carbody"])
    kit.box("car.windscreen", (1.7, 0.04, 0.9), (cx, cy - 1.32, 1.55), M["carwin"])
    for k, vx in enumerate((-0.25, 0.25)):
        kit.box(f"car.vent{k}", (0.22, 0.04, 0.08), (cx + vx, cy - 0.745, 0.88), M["vent"])
    kit.cyl("car.wheel", 0.19, 0.04, (cx - 0.4, cy - 0.68, 0.98), M["tyre"], rot=(math.pi / 2.6, 0, 0), n=16)
    for k, sy in enumerate((-0.2, 1.05)):          # front seats and the back bench
        for sx in (-0.42, 0.42):
            if sy < 0.5:
                kit.box(f"car.seat{k}{sx}", (0.6, 0.55, 0.45), (cx + sx, cy + sy, 0.25), M["carseat"], bevel=0.05)
                kit.box(f"car.seatb{k}{sx}", (0.6, 0.14, 0.75), (cx + sx, cy + sy + 0.3, 0.8), M["carseat"], bevel=0.05)
        if sy > 0.5:
            kit.box("car.bench", (1.7, 0.6, 0.45), (cx, cy + sy, 0.25), M["carseat"], bevel=0.05)
            kit.box("car.benchb", (1.7, 0.14, 0.75), (cx, cy + sy + 0.35, 0.8), M["carseat"], bevel=0.05)


# ------------------------------------------------------------------------------------------ flames
def flame_mesh(kit, name, mat, scale=1.35):
    n, rings = 14, 16
    verts, faces = [], []
    for i in range(rings + 1):
        u = i / rings
        r = 0.062 * math.sin(math.pi * (u ** 0.6)) ** 0.9 * (1 - u) ** 0.4 * scale
        z = FLAME_H * u * scale
        for j in range(n):
            a = 2 * math.pi * j / n
            verts.append((r * math.cos(a), r * math.sin(a), z))
    for i in range(rings):
        for j in range(n):
            a, b = i * n + j, i * n + (j + 1) % n
            faces.append((a, b, b + n, a + n))
    return kit.mesh_obj(name, verts, faces, mat, smooth=True)


def build_flames(kit, M, cast_names):
    flames = {}
    outer = kit.emit("#ff9a26", 4.0, "flame outer")
    core = kit.emit("#ffd27a", 5.5, "flame core")
    for who in cast_names:
        root = kit.empty(f"flame.{who}")
        piv = kit.empty(f"flame.{who}.piv", (0, 0, 0), root)
        a = flame_mesh(kit, f"flame.{who}.o", outer)
        a.parent = piv
        b = flame_mesh(kit, f"flame.{who}.c", core, 0.56)
        b.parent = piv
        b.location = (0, 0, 0.012)
        strength = 7.0 if who in ("me", "grandad") else 3.0
        L = kit.light(f"flame.{who}", "POINT", (0, 0, 0.1), strength, "#ffb86a", size=0.05, parent=piv, shadow=(who in ("me", "grandad")))
        flames[who] = {"root": root, "piv": piv, "light": L, "strength": strength}
    return flames


# ------------------------------------------------------------------------------------------ lights
def build_lights(kit, ctx):
    sun = kit.light("sun", "SUN", (-50, -60, 30), 2.6, "#ffd29a", size=0.3)
    kit.aim(sun, (0, 0, 0))
    sun.data.angle = 0.03
    fill = kit.light("fill", "SUN", (40, 40, 60), 0.7, "#b8cde6")
    kit.aim(fill, (0, 0, 0))
    fill.data.angle = 0.2
    ctx["sun"], ctx["fill"] = sun, fill
    # the hut: a lamp on its hook, soft bounce from the window
    hx, hy = RED[0] + 0.2, RED[1] + 0.85
    kit.light("hutlamp", "POINT", (hx, hy, HUT_H - 0.55), 420.0, "#ffc27a", size=0.12)
    kit.light("hutbounce", "POINT", (RED[0] - 0.3, RED[1] - 0.4, 0.9), 60.0, "#ffb070", size=0.4)
    kit.light("hutfill", "POINT", (RED[0] + 0.6, RED[1] - 0.9, 1.9), 60.0, "#ffb98a", size=0.5)
    # the Leaner's cold key and rim, moved in animate to stand with it
    ctx["lkey"] = kit.light("lkey", "AREA", (0, 0, 2), 150.0, "#aac8ea", size=1.6)
    ctx["lamber"] = kit.light("lamber", "POINT", (0, 0, -20), 60.0, "#ffb060", size=0.25)
    ctx["lrim"] = kit.light("lrim", "SPOT", (0, 0, 2), 260.0, "#9cc4ee", size=0.3, spot=40, blend=0.5)
    # the car: a soft orange from the vents, a pale glow from the roof
    cx, cy = CAR
    kit.light("carvent", "POINT", (cx, cy - 0.5, 0.85), 90.0, "#ff9a3c", size=0.15)
    kit.light("carroof", "POINT", (cx, cy + 0.6, 1.9), 120.0, "#9aaed0", size=0.3)
    # the café and the flat-door fills
    kit.light("cafe", "POINT", (-23.0, -3.0, 2.8), 700.0, "#ffc890", size=0.4)
    # a pale fill at the red hut's door from the fog
    kit.light("doorfill", "AREA", (RED[0] - 3.5, RED[1] - 0.6, 1.2), 180.0, "#bcd0e6", size=1.5)
    kit.aim(bpy.data.objects["doorfill"], (RED[0] - 1.5, RED[1] - 0.6, 1.2))


# ------------------------------------------------------------------------------------------ build
def build(kit, story, tl):
    ctx = {"story": story}
    M = materials(kit)
    ctx["M"] = M
    build_ground(kit, M)
    ctx["red"] = build_huts(kit, M)
    build_town(kit, M)
    build_car(kit, M)
    names = [n for n, s in story["cast"].items() if n != "leaner"]
    ctx["flames"] = build_flames(kit, M, names)
    build_lights(kit, ctx)
    # the puff of breath: a soft white card that grows and fades (opacity animated)
    pm = bpy.data.materials.new("puff")
    pm.use_nodes = True
    nt = pm.node_tree
    for n in list(nt.nodes):
        nt.nodes.remove(n)
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    em = nt.nodes.new("ShaderNodeEmission")
    em.inputs["Color"].default_value = (0.9, 0.95, 1.0, 1)
    em.inputs["Strength"].default_value = 1.0
    tr = nt.nodes.new("ShaderNodeBsdfTransparent")
    mix = nt.nodes.new("ShaderNodeMixShader")
    mix.inputs[0].default_value = 0.0
    nt.links.new(tr.outputs[0], mix.inputs[1])
    nt.links.new(em.outputs[0], mix.inputs[2])
    nt.links.new(mix.outputs[0], out.inputs["Surface"])
    ctx["puffmix"] = mix
    ctx["puff"] = kit.sphere("puff", 0.12, (0, 0, -50), pm, seg=10)
    ctx["shotspec"] = {s["id"]: s for s in story["shots"]}
    return ctx


# ------------------------------------------------------------------------------------------ animate
def _eased(cues, key, t, default):
    """A value that eases from the previous cue's to this cue's over its "dur"."""
    v = default
    for c in cues:
        if c["t"] > t + 1e-9:
            break
        if key in c:
            u = _ss((t - c["t"]) / max(1e-6, c.get("dur", 0.0))) if c.get("dur", 0) > 0 else 1.0
            v = v + (c[key] - v) * u if u < 1.0 else c[key]
    return v


def _flame_vec(tl, cues, who, t):
    """The flame's lean as an (x, y) vector in degrees: a blend from cue to cue."""
    s = acting.state(tl, who, t)
    px, py = s["x"], s["y"]
    v = (0.0, 0.0)
    for c in cues:
        if c["t"] > t + 1e-9:
            break
        ang = c.get("ang", 40.0)
        if "spin" in c:
            ph = 2 * math.pi * (t - c["t"]) / c["spin"]
            tgt = (ang * math.cos(ph), ang * math.sin(ph))
        elif c.get("to") is None:
            tgt = (0.0, 0.0)
        else:
            tx, ty = c["to"]
            if c.get("shore"):
                tx, ty = -300.0, py
            dx, dy = tx - px, ty - py
            d = math.hypot(dx, dy) or 1.0
            tgt = (ang * dx / d, ang * dy / d)
        dur = c.get("dur", 0.9)
        u = _ss((t - c["t"]) / max(1e-6, dur))
        v = (v[0] + (tgt[0] - v[0]) * u, v[1] + (tgt[1] - v[1]) * u)
    return v


def animate_flames(kit, story, tl, t, ctx):
    gains = {}
    cs = _cues(tl, "flame")
    for who, f in ctx["flames"].items():
        s = acting.state(tl, who, t)
        hidden = s["hidden"]
        f["root"].hide_render = hidden
        for ob in f["root"].children_recursive:
            ob.hide_render = hidden
        gains[f"flame.{who}"] = 0.0 if hidden else 1.0
        if hidden:
            continue
        h = story["cast"][who].get("height", 1.0)
        top = HEAD_TOP * h + HATS.get(who, 0.0)
        ln = s["lean"]
        fx, fy = math.sin(s["yaw"]), -math.cos(s["yaw"])
        f["root"].location = (s["x"] + top * math.sin(ln) * fx, s["y"] + top * math.sin(ln) * fy,
                              s["z"] + s["bob"] + top * math.cos(ln) + 0.18)
        vx, vy = _flame_vec(tl, [c for c in cs if c["who"] == who], who, t)
        sway = math.radians(2.0) * math.sin(2 * math.pi * 0.3 * t + hash(who) % 7)
        ang = math.hypot(vx, vy)
        if ang < 1e-3:
            f["piv"].rotation_euler = (sway, 0, 0)
        else:
            q = Quaternion((-vy, vx, 0.0), math.radians(ang))
            f["piv"].rotation_euler = q.to_euler()
            f["piv"].rotation_euler.rotate_axis("X", sway)
    return gains


def init_lazy(kit, story, ctx):
    """Once the cast exists: the fog nodes (every material's, the characters' too) and the dressing."""
    if ctx.get("lazy"):
        return
    ctx["lazy"] = True
    dens0 = kit.FOG["density"]
    fc = kit.FOG["color"]
    muls, ems = [], []
    for m in bpy.data.materials:
        if not m.node_tree:
            continue
        for n in m.node_tree.nodes:
            if n.type == "MATH" and n.operation == "MULTIPLY" and abs(n.inputs[1].default_value + dens0) < 1e-9:
                muls.append(n)
            elif n.type == "EMISSION" and all(abs(n.inputs["Color"].default_value[i] - fc[i]) < 1e-6 for i in range(3)):
                ems.append(n)
    ctx["fogmuls"], ctx["fogems"], ctx["fogc0"] = muls, ems, tuple(fc)
    ctx["world_bg"] = bpy.context.scene.world.node_tree.nodes["Background"]
    dress(kit, story, ctx)


def dress(kit, story, ctx):
    """Beards, caps, leaves, a flask, a suitcase: things the rig has no part for."""
    M = ctx["M"]
    ob = bpy.data.objects
    white = kit.plastic("#f0f0ee", 0.9, "white hair")
    R, Hh = 0.62, 1.2

    def head(who):
        return ob.get(f"{who}.headg")
    hg = head("grandad")
    if hg:
        kit.box("g.beard", (0.98, 0.5, 0.42), (0, -R + 0.12, -0.38), white, hg, bevel=0.14)
        kit.box("g.mous", (0.62, 0.2, 0.12), (0, -R - 0.02, -0.14), white, hg, bevel=0.05)
        kit.sphere("g.bobble", 0.19, (0, 0.0, Hh / 2 + 0.52), kit.plastic("#d9b24a", 0.9, "bobble"), hg, seg=10)
        kit.box("g.brow", (1.0, 0.08, 0.1), (0, -R + 0.02, 0.13), white, hg, bevel=0.03)
    capc = kit.plastic("#16120f", 0.8, "flatcap")
    for who, colr in (("leaner", "#16120f"), ("pell", "#6b5a40")):
        hg2 = head(who)
        if hg2:
            cm = capc if who == "leaner" else kit.plastic(colr, 0.9, "tweed")
            kit.cyl(f"{who}.flatcap", R + 0.12, 0.22, (0, 0.0, Hh / 2 + 0.02), cm, hg2, n=24)
            kit.box(f"{who}.capbill", (0.9, 0.5, 0.06), (0, -R - 0.12, Hh / 2 - 0.1), cm, hg2, bevel=0.02)
    hp = head("pell")
    if hp:
        lv = kit.plastic("#4f7a3a", 0.9, "leaf")
        ctx["leaves"] = [kit.box(f"leaf{k}", (0.22, 0.14, 0.03), (0.2 * (k - 1), -0.1 + 0.1 * k, Hh / 2 + 0.16 + 0.02 * k), lv, hp,
                                 rot=(0.3, 0.4 * k, 0.5 * k)) for k in range(3)]
        for o in ctx["leaves"]:
            o.hide_render = True
    tm = ob.get("me.torso")
    if tm:
        fl = kit.cyl("me.flask", 0.16, 0.7, (1.3, 0.1, 0.9), kit.metal("#8e9399", 0.35, "flask"), tm, n=12)
    # the suitcase by the newcomer, the bucket by the far hole, the lap blanket
    kit.box("suitcase", (0.55, 0.22, 0.75), (-34.2, -4.2, 0.4), kit.plastic("#4a5a6a", 0.6, "case"), bevel=0.04)
    kit.box("suitcase.h", (0.25, 0.04, 0.3), (-34.2, -4.2, 0.9), M["iron2"])
    kit.cyl("bucket", 0.22, 0.4, (88.0, -4.0, 0.2), kit.metal("#6c7a82", 0.5, "bucket"), n=14, r2=0.26)
    kit.cyl("far.hole", 0.2, 0.02, (89.3, -4.0, 0.014), M["hole"], n=16)
    kit.cyl("far.stick", 0.012, 0.9, (89.65, -4.0, 0.45), M["trunk"], n=6)
    kit.box("far.flag", (0.22, 0.01, 0.12), (89.75, -4.0, 0.84), kit.plastic("#e8c04a", 0.8, "flag y"))
    kit.cyl("storm.hole", 0.2, 0.02, (63.4, 8.9, 0.014), M["hole"], n=16)
    kit.cyl("storm.stick", 0.012, 0.9, (63.75, 8.9, 0.45), M["trunk"], n=6)
    kit.box("storm.flag", (0.22, 0.01, 0.12), (63.85, 8.9, 0.84), kit.plastic("#d65a3a", 0.8, "flag r"))
    lap = kit.box("lap", (0.55, 0.45, 0.14), (RED[0] + 0.75, RED[1] + 0.0, 0.52), M["wool"], bevel=0.05)
    ctx["lap"] = lap
    lap.hide_render = True
    ctx["blanket"] = [ob["red.blanket"], ob["red.blanket2"]]


def animate_fog(kit, tl, t, ctx):
    d = _eased(_cues(tl, "fog"), "d", t, ctx["story"]["look"]["fog_density"])
    for n in ctx["fogmuls"]:
        n.inputs[1].default_value = -d
    # the dusk of the last night: the fog, the world and the window go from pale to deep blue, slowly
    k = _eased(_cues(tl, "dusk"), "v", t, 0.0)
    c0 = ctx["fogc0"]
    dusk = (0.03, 0.045, 0.1)
    col = tuple(c0[i] + (dusk[i] - c0[i]) * k for i in range(3))
    for n in ctx["fogems"]:
        n.inputs["Color"].default_value = (*col, 1.0)
    ctx["world_bg"].inputs["Color"].default_value = (*col, 1.0)
    ctx["dusk"] = k
    return d


def animate_props(kit, tl, t, ctx):
    red = ctx["red"]
    red["hinge"].rotation_euler = (0, 0, -math.radians(105) * _eased(_cues(tl, "door"), "open", t, 0.0))
    shut = _eased(_cues(tl, "curtain"), "shut", t, 0.0)
    red["curtain"].scale = (0.12 + 0.88 * shut, 1, 1)
    # the lamp: smooth levels only
    lamp = _eased(_cues(tl, "lamp"), "on", t, 1.0)
    ctx["M"]["lampglow"].node_tree.nodes["Emission"].inputs["Strength"].default_value = 3.2 * (0.25 + 0.75 * lamp)
    # puffs of breath
    pf = ctx["puff"]
    pf.location = (0, 0, -50)
    for c in _cues(tl, "puff"):
        u = (t - c["t"]) / 0.6
        if 0 <= u <= 1:
            s = acting.state(tl, c.get("who", "me"), t)
            yaw = s["yaw"] if c.get("yaw") is None else math.radians(c["yaw"])
            fx, fy = math.sin(yaw), -math.cos(yaw)
            r = 0.28 + 0.12 * u
            pf.location = (s["x"] + fx * (0.24 + 0.28 * u) + c.get("dx", 0.0), s["y"] + fy * (0.24 + 0.28 * u) + c.get("dy", 0.0),
                           s["z"] + c.get("z", 1.56) + 0.05 * u)
            pf.scale = (r * 1.2, r * 1.2, r * 0.8)
            ctx["puffmix"].inputs[0].default_value = 0.45 * (1 - _ss(u)) * _ss(u * 6)
            break
    else:
        ctx["puffmix"].inputs[0].default_value = 0.0


def current_shot(tl, t):
    return next((s for s in tl["shots"] if s["start"] <= t < s["end"]), tl["shots"][-1])


def animate_lights(kit, story, tl, t, ctx, over, d):
    shot = current_shot(tl, t)
    sid = shot["id"]
    where = story["shot_where"].get(sid, "ice")
    # sun: dims as the fog thickens (a slow follow of the fog's own ramp)
    thick = _ss((d - 0.012) / 0.08)
    over["sun"] = (1.0 - 0.8 * thick) * (1.0 - ctx.get("dusk", 0.0)) if where in ("ice", "town") else 0.0
    over["fill"] = (1.0 + 0.2 * thick) * (1.0 - 0.8 * ctx.get("dusk", 0.0)) if where in ("ice", "town") else 0.0
    inside = where == "hut"
    lamp = _eased(_cues(tl, "lamp"), "on", t, 1.0)
    over["hutlamp"] = (0.1 + 0.9 * lamp) if inside else 0.0
    over["hutfill"] = (0.3 + 0.7 * lamp) if inside else 0.0
    over["hutbounce"] = (0.12 + 0.88 * lamp) if inside else 0.0
    over["carvent"] = over["carroof"] = 1.0 if where == "car" else 0.0
    over["cafe"] = 1.0 if where == "town" else 0.0
    over["doorfill"] = 1.0 if sid in story.get("door_shots", []) else 0.0
    # the Leaner's key and rim: on in its exterior shots, set up from the camera's side
    on = sid in story.get("leaner_shots", [])
    s = acting.state(tl, "leaner", t)
    if on and not s["hidden"]:
        loc, tgt, lens, roll = bl_story.cam_at(ctx["shotspec"][sid], shot, t, {}, tl)
        lean = s["lean"]
        # the head's centre
        hx = s["x"] + 1.3 * math.sin(lean) * math.sin(-s["yaw"]) * -1 if False else s["x"]
        head = Vector((s["x"], s["y"], 1.3 * math.cos(lean)))
        fwd = Vector((math.sin(s["yaw"]), -math.cos(s["yaw"]), 0.0))
        head += fwd * 1.3 * math.sin(lean)
        cam = Vector(loc)
        toward = (head - cam)
        toward.z = 0
        toward.normalize() if toward.length > 1e-6 else None
        side = Vector((-toward.y, toward.x, 0.0))
        kit_aim = kit.aim
        kp = head - toward * 1.5 + side * 0.9
        kp.z = max(0.25, head.z - 0.7)
        ctx["lkey"].location = kp
        kit_aim(ctx["lkey"], tuple(head))
        ctx["lrim"].location = head + toward * 2.4 - side * 1.0 + Vector((0, 0, 0.8))
        kit_aim(ctx["lrim"], tuple(head))
        amber = sid in story.get("amber_shots", [])
        over["lamber"] = 1.0 if amber else 0.0
        if amber:       # the lamp's glow comes through the window and lights the tipped face amber
            ctx["lamber"].location = head + fwd * 0.7 + Vector((0, 0, 0.25))
        over["lkey"] = 0.0 if amber else story.get("leaner_key", {}).get(sid, 1.0)
        over["lrim"] = story.get("leaner_rim", {}).get(sid, 1.0)
    else:
        over["lkey"] = over["lrim"] = over["lamber"] = 0.0
    return over


def animate(kit, story, tl, t, ctx):
    dbg = __import__("os").environ.get("ICE_CAM")   # look-dev only: "x,y,z,tx,ty,tz,lens" replaces every shot's camera
    if dbg and not ctx.get("dbg"):
        v = [float(x) for x in dbg.split(",")]
        for sp in story["shots"]:
            sp["cam"] = [[0, v[0:3], v[3:6], v[6]]]
        ctx["dbg"] = True
    init_lazy(kit, story, ctx)
    sid = current_shot(tl, t)["id"]
    for o in ctx.get("leaves", []):
        o.hide_render = sid not in story.get("leaves_shots", [])
    after = int(sid[1:3]) >= 72
    bpy.data.objects["red.pane"].hide_render = sid == "S41"
    ctx["lap"].hide_render = not (after and sid in ("S73", "S74", "S75", "S76", "S77"))
    for b in ctx["blanket"]:
        b.hide_render = after
    over = animate_flames(kit, story, tl, t, ctx)
    d = animate_fog(kit, tl, t, ctx)
    animate_props(kit, tl, t, ctx)
    animate_lights(kit, story, tl, t, ctx, over, d)
    return over
