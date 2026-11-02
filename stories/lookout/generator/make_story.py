"""Writes ../story.json for ep14 "Lookout" (brief 02-brief.md, script 02b-script.md, 2026-10-31).

Run from anywhere: python stories/lookout/generator/make_story.py
The words are in lines.json next to this file (every line of the script, exactly). Everything else is here: the
cast, the shots, the acting, the cues set.py reads, the effects, the score and the sound. Shot ids are numbered in
order (S01, S02, ...), and every shot starts on a line reference, never a rounded time.

Places (set.py's coordinates): the tower stands on (0, 0) and the ground at its foot is z = 0. The cab is 4 x 4 m
(x, y in -2 .. 2) with its floor's top at CAB_Z = 19.6; the catwalk runs 1 m round it, its rail on the outer edge
(the south rail's line is y = -2.96). The 112 stairs climb a square switchback inside the legs (corners at +-1.45)
and come up through a hatch at the cab's south-west corner. The fence and its gate are 6.2 m south of the tower,
and the fire road runs from the gate down the slope to the shelf at (44, -266), about 50 m lower, over the valley.
A character facing -y has yaw 0, facing +x has yaw 90, facing -x yaw -90 and facing +y yaw 180.
"""
import json
import math
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE.parent / "story.json"
lines = json.loads((HERE / "lines.json").read_text())

CAB_Z = 19.6
A = 1.45                                  # the stairs' square
RISE = CAB_Z / 112
STAIR_W = 0.6                             # a flight's width (set.py)
ROAD = ((0.0, -6.2), (0.0, -16.0), (3.0, -32.0), (-2.0, -52.0), (6.0, -80.0), (18.0, -120.0), (30.0, -170.0),
        (38.0, -220.0), (42.0, -258.0))
SHELF = (44.0, -266.0)


def ground(x, y):
    """set.py's terrain_z without its small bumps (they're smoothed to nothing on the plateau, the road and the
    shelf, which is everywhere I stand)."""
    z = -0.2 * max(0.0, -y - 20.0) - 0.05 * max(0.0, abs(x) - 24.0)
    z += 0.16 * max(0.0, y - 110.0) - 0.0006 * max(0.0, y - 260.0) ** 2
    if y < -272.0:
        z = max(-175.0, z - 1.6 * (-272.0 - y))
    return 0.0 if math.hypot(x, y) < 22 else round(z, 3)


def road(u, side=0.0):
    """A point on the road (u 0..1 along it), `side` metres to the right of its middle, on the ground."""
    segs = [math.hypot(b[0] - a[0], b[1] - a[1]) for a, b in zip(ROAD, ROAD[1:])]
    d = u * sum(segs)
    for (a, b), L in zip(zip(ROAD, ROAD[1:]), segs):
        if d <= L or (a, b) == (ROAD[-2], ROAD[-1]):
            k = min(1.0, d / L)
            dx, dy = (b[0] - a[0]) / L, (b[1] - a[1]) / L
            x, y = a[0] + (b[0] - a[0]) * k - dy * side, a[1] + (b[1] - a[1]) * k + dx * side
            return [round(x, 3), round(y, 3), ground(x, y)]
        d -= L


def gpose(at, u, stride):
    """The giant held in one pose at road position u, its front down the road, its head on my lamp."""
    a, b = road(u), road(u + 0.002)
    return {"at": at, "name": "giant", "pos": [a[0], a[1], 0.0], "yaw": round(math.degrees(math.atan2(b[0] - a[0], -(b[1] - a[1]))), 1),
            "pitch": 3.0, "stride": stride, "look_lamp": True, "pines": True}


def c(*keys):
    return [list(k) for k in keys]


def mv(p0, t0, l0, p1=None, t1=None, l1=None, roll=0.0):
    """A camera: one key, or a move from the first key to the second over the shot."""
    if p1 is None:
        return c([0, p0, t0, l0, roll])
    return c([0, p0, t0, l0, roll], [1, p1, t1 if t1 is not None else t0, l1 if l1 is not None else l0, roll])


def at_floor(p, z=CAB_Z):
    return [p[0], p[1], z]


# ---------------------------------------------------------------------------------------------------- the cast
# Me, alone (brief): cobalt and black plaid flannel, the hood up in every shot, black cap hair under it, charcoal
# canvas pants, honey-tan boots, warm tan skin, round eyes, thick black brows. No age is said or shown.
cast = {
    "me": {"age": "adult", "skin": "#b5794e", "shirt": "#2a56c6", "pattern": "plaid", "pattern_c": "#141821",
           "collar": "#101216", "pants": "#2e2924", "shoes": "#a8733a", "sleeves": "long", "hair": "cap",
           "hair_c": "#121214", "hat": "hood", "hat_c": "#4b4e57",
           "face": {"eyes": "round", "brows": True, "ink": "#16100c"}},
}

# ---------------------------------------------------------------------------------------------------- places
GLASS_S = at_floor([0.4, -1.55])          # at the cab's south glass
# (the probe keeps me clear of the cot along the east wall, the table and radio shelf at the north wall, the stairs'
# hatch at the south-west corner and the door: my arms make me 1.36 m wide)
GLASS_E = at_floor([1.45, -1.25])         # at the east glass, south of the cot (the burn's smudge)
GLASS_N = at_floor([-0.8, 1.0])           # at the north glass, clear of the table (the far ridge)
GLASS_W = at_floor([-1.25, -0.8])         # by the west glass, clear of the hatch (03: the shoulders behind me)
RADIO_AT = at_floor([0.8, 1.0])           # at the radio shelf, my left hand over the radio
COT = [1.52, 0.3, CAB_Z - 0.03]           # sitting on the cot (my thighs on its top)
RADIO_UP = at_floor([0.4, -1.15])         # L18 to L20: the radio held up to the dark, short of the glass
DOOR_IN = at_floor([-1.3, 0.3])           # (clear of the open door, which stays open from L35 on)
DOOR_OUT = at_floor([-2.45, 0.0])         # just out of the door, in the middle of the catwalk
CORNER_SW = at_floor([-2.5, -2.45])
RAIL = at_floor([0.74, -2.42])            # at the south rail, the creature test's place
EAST_WIN = at_floor([0.45, -0.2])         # across the cab with the lamp to the far (east) window, short of the cot
AT_COT = at_floor([0.73, -0.2])           # a step closer: my right hand at 67 degrees sets the lamp on the cot's top
LAMP_SET = [1.278, -0.71, CAB_Z + 0.48]   # ... here (that hand's end, minus the bail's 0.56 m)
CORNER_NW = at_floor([-1.35, 0.35])       # backed against the west wall by the door, clear of the table
LAMP_COT = [1.5, -0.55, CAB_Z + 0.48]     # the lamp set down on the cot
LAMP_TABLE = [-0.5, 1.5, CAB_Z + 0.76]    # on the table at night
LAMP_HAND = {"hand": "me.arm-1", "offset": [0.0, 0.0, -0.56]}   # its bail hanging from my right hand


def stair_corner(k):
    """The stairs' corners going down from the hatch: k = 0 is the top landing (19.6 m), k = 8 the ground."""
    order = [(-A, -A), (-A, A), (A, A), (A, -A)]
    x, y = order[k % 4]
    return [x, y, round(CAB_Z - k * 14 * RISE, 3)]


def flight(k, u, inward=0.1, lift=0.3):
    """A point u (0..1) down the flight from corner k to corner k + 1, on the treads (set.py build_stairs: a 0.6 m
    landing in each corner, then 14 treads over the 2.3 m between them, 47 degrees), `lift` over the line through
    the treads' middles (a boot spans a tread and the back of the next one up) and `inward` toward the stairwell's
    middle (my outer arm clears the handrail on the flight's outer side)."""
    a, b = stair_corner(k), stair_corner(k + 1)
    d = 2 * A * u                          # along the flight from the top corner
    run, top = 2 * A - STAIR_W, CAB_Z - k * 14 * RISE
    c0 = STAIR_W / 2 + run / 28            # the top tread's middle; the bottom tread's is 2A - c0
    if d <= c0:
        z = top
    elif d >= 2 * A - c0:
        z = top - 13 * RISE
    else:
        z = top - (d - c0) * (13 * RISE) / (2 * A - 2 * c0)
    p = [a[0] + (b[0] - a[0]) * u, a[1] + (b[1] - a[1]) * u, z + lift]
    if abs(a[0] - b[0]) > abs(a[1] - b[1]):    # it runs along x, at y = +-A: in toward y = 0
        p[1] -= math.copysign(inward, p[1])
    else:
        p[0] -= math.copysign(inward, p[0])
    return [round(v, 3) for v in p]


GATE_IN, GATE_OUT = [-2.25, -1.4, 0.0], [-2.25, -3.05, 0.0]   # the stairs' foot, then through the gate (set.py GATE_X)
ON_SHELF = [43.0, -270.0, ground(44.0, -266.0) + 0.05]       # on the shelf's slab (its top is 5 cm over the ground)
U_ME = {"L64": (0.050, 0.062), "L65": (0.062, 0.078), "L66": (0.078, 0.090), "L67": (0.210, 0.225)}
LAG = 0.03                                # its lag behind me down the road (7.7 m)

# the giant's places (set.py CLEAR keeps the forest off them)
FAR = [-25.0, 57.0, 0.0]                  # L01, far back behind the cab in fog
WALK_UP = ([-31.5, -11.0], [-16.0, 1.0])  # 03: up the ridge toward the tower (the scale wide at L30)
LEAN = [5.6, -7.6, -2.6]                  # L37 to L41: low, its right stone on the frame below the cab
FEAR = [2.45, -8.0, 0.0]                  # L42 on: its hollow 1.3 m past the south rail

# ---------------------------------------------------------------------------------------------------- shots
# (at, camera, options). step 1 = drawn on ones (the lights rising, its foot in my lamp's pool); hand = handheld drift.
FEAR_CAM = mv([-0.12, -1.72, 21.95], [2.41, -5.16, 20.4], 15)        # critic pass 2: 20 deg down, 5 deg left
SCALE_CAM = mv([-82.5, -85.8, 12.0], [-18.0, -5.0, 15.0], 38, [-81.0, -84.5, 12.0], [-18.0, -5.0, 15.2], 38)
REVEAL_34 = mv([-10.2, 3.2, 21.3], [0.7, -5.6, 18.8], 18, roll=2.5)
WINDOW_CLOSE = mv([0.25, 0.0, 21.4], [0.25, -6.0, 20.6], 17, roll=-3.0)
SH = [
    # ---- 01 the question. The lit cab from outside on a pearl-fog morning, me at the glass; far back in the fog a
    # dark mass with two faint points (never mentioned). Slow push in
    (0, mv([10.5, -14.0, 19.8], [0.0, 0.0, 21.2], 30, [8.2, -11.0, 20.2], [0.0, 0.0, 21.4], 32), {"hand": 0.004}),
    ("L02", mv([1.65, 1.6, 21.1], [0.2, -0.7, 20.6], 22), {}),
    ("L03", mv([4.6, -7.6, 1.3], [0.0, 0.0, 5.0], 16, [4.6, -7.6, 1.3], [0.0, 0.0, 19.0], 16), {}),
    ("L04", mv([0.15, 1.05, 20.78], [0.3, 1.78, 20.66], 40), {"hand": 0.002}),
    ("L05", mv([-1.2, -0.6, 21.6], [520.0, -36.0, 2.0], 26, [-1.0, -0.62, 21.6], [520.0, -36.0, 2.0], 28), {}),
    ("L06", mv([0.5, -2.62, 21.1], [20.0, -880.0, -120.0], 30, [0.5, -2.62, 21.0], [20.0, -880.0, -122.0], 34), {}),
    ("L06.2", mv([0.5, -2.62, 21.0], [-20.0, -880.0, -146.0], 90, [0.5, -2.62, 21.0], [-45.0, -880.0, -147.0], 105), {}),
    ("L07", mv([0.42, -2.75, 21.18], [0.4, -1.55, 21.16], 30), {"hand": 0.003}),
    # ---- 02 seen, heard. Binocular POV on the far ridge, the snapped line, my face behind the binoculars
    ("L08", mv([-0.8, 1.75, 21.2], [-62.0, 282.0, 33.0], 140, [-0.8, 1.75, 21.2], [-72.0, 296.0, 34.5], 140), {}),
    ("L09", mv([-0.8, 1.75, 21.2], [-100.0, 330.0, 38.0], 140, [-0.8, 1.75, 21.2], [-40.0, 240.0, 31.0], 140), {}),
    ("L10", mv([-0.8, 2.7, 21.15], [-0.8, 1.0, 21.15], 30), {}),
    ("L11", mv([0.3, -1.6, 21.7], [-40.0, 240.0, 30.0], 30, [0.25, -1.6, 21.7], [-20.0, 180.0, 26.0], 30), {}),
    ("L12", mv([0.9, 3.1, 21.3], [0.55, 1.2, 20.9], 28), {}),
    ("L13", mv([-0.3, 1.2, 20.95], [0.3, 1.77, 20.66], 35), {"hand": 0.002}),
    ("L14", mv([17.0, -13.0, 24.0], [0.0, 0.0, 21.0], 28, [15.6, -12.0, 23.8], [0.0, 0.0, 21.0], 30), {}),
    ("L15", mv([-0.6, -0.8, 20.9], [1.5, 0.3, 20.75], 26), {}),
    ("L16", mv([-0.2, 1.2, 21.2], [0.0, -12.0, 20.5], 22, [-0.2, 1.0, 21.2], [0.0, -12.0, 20.5], 22), {}),
    ("L18", mv([1.0, -4.5, 21.3], [0.4, -1.15, 21.15], 28), {"hand": 0.004}),
    ("L19", mv([1.1, -2.75, 21.1], [0.9, -1.8, 21.0], 40), {"hand": 0.003}),
    ("L20", mv([0.4, -2.8, 21.0], [0.75, -1.6, 20.95], 30), {"hand": 0.003}),
    # ---- 03 traces, moving. The stairs, the prints, the catwalk at dusk, the pines parting, the scale wide
    ("L21", mv([8.0, 6.0, 22.0], [1.2, 0.2, 15.0], 24), {}),
    ("L22", mv([7.5, -8.5, 4.5], [2.6, -13.6, 0.0], 24), {}),
    ("L23", mv([2.6, -7.4, 11.0], [2.5, -13.2, 0.0], 30), {}),
    ("L24", mv([4.6, -14.2, 2.1], [2.5, -16.2, 0.0], 24, [4.2, -14.6, 1.6], [2.5, -16.4, 0.0], 26), {}),
    ("L26", mv([1.0, -8.0, 2.0], [2.0, -30.0, -2.0], 24, [2.0, -9.0, 9.0], [2.0, -40.0, -5.0], 24), {}),
    ("L27", mv([0.2, -1.4, 21.7], [-30.0, -40.0, 10.0], 24), {}),
    ("L28", mv([-1.2, -2.6, 21.3], [-34.0, -24.0, 9.0], 40, [-1.2, -2.6, 21.3], [-30.0, -18.0, 9.5], 40), {}),
    ("P02", mv([0.6, -3.6, 20.3], [0.05, -2.6, 20.0], 35), {"hand": 0.004}),
    ("L30", SCALE_CAM, {"hand": 0.0}),
    ("L31", mv([-55.0, -45.0, 21.0], [-25.0, -6.0, 20.0], 70, [-54.0, -44.0, 21.0], [-23.0, -4.5, 20.0], 70), {}),
    ("L33", mv([0.7, -1.4, 21.3], [-6.0, -0.8, 20.0], 24), {}),
    # ---- 04 close, felt (the scare). The fog top under the catwalk, the tower's foot, the catwalk, the lean, the
    # lights rising on ones, the fear close, the 3/4, the window, the radio
    ("L34", mv([20.0, -10.0, 21.0], [0.0, 0.0, 21.0], 28, [18.0, -9.0, 21.0], [0.0, 0.0, 21.0], 30), {}),
    ("L35", mv([3.0, -7.0, 1.0], [0.0, 0.0, 6.0], 18), {}),
    ("L36", mv([-2.5, -2.6, 21.3], [-2.0, 0.0, 20.9], 20), {}),
    ("L37", mv([1.3, -1.6, 21.75], [-1.5, -9.0, 20.2], 22), {"hand": 0.004}),
    ("L38", mv([-5.0, 4.0, 5.0], [0.0, 0.0, 14.0], 20), {}),
    ("L39", mv([-24.0, -3.0, 12.0], [0.0, -1.0, 14.0], 26), {}),
    ("L40", mv([15.0, -16.0, 4.0], [1.0, -3.0, 13.5], 20, [14.0, -15.0, 4.5], [1.0, -3.0, 14.0], 20, roll=5.0), {}),
    ("L41", mv([1.6, -3.5, 20.7], [0.75, -2.8, 20.4], 30), {"hand": 0.003}),
    ("L42", mv([0.95, -1.6, 21.55], [2.45, -6.5, 19.6], 24), {"step": 1, "hand": 0.003}),
    ("L43", FEAR_CAM, {"hand": 0.002}),
    ("L44", mv([1.6, -2.8, 21.35], [2.3, -6.0, 21.3], 20), {"hand": 0.002}),
    ("L45", mv([10.0, -4.0, 23.0], [2.4, -7.0, 18.0], 24), {"hand": 0.003}),
    ("L46", mv([0.4, 1.7, 21.3], [0.8, -6.0, 20.8], 18), {"hand": 0.002}),
    ("L47", mv([1.4, -2.6, 21.2], [2.35, -6.2, 21.35], 26), {"hand": 0.002}),
    ("L49", mv([0.62, -3.35, 21.15], [0.74, -2.42, 21.15], 30), {"hand": 0.003}),
    ("L50", mv([1.2, -3.9, 21.1], [1.1, -3.0, 21.1], 40), {"hand": 0.003}),
    ("L51", mv([-0.3, -3.7, 21.2], [0.8, -2.5, 21.15], 28), {"hand": 0.003}),
    # ---- 05 the lamp test, inside the cab at night
    ("L52", mv([1.7, 1.6, 21.3], [-0.3, -2.6, 20.8], 18), {}),
    # (the giant faces the tower, so its lights are seen from the north: the lit cab, the lamp moving along the
    # glass, the two warm points beyond it, level with the lamp's line)
    ("L53", mv([-5.0, 8.0, 21.4], [0.0, -0.7, 21.0], 36), {}),
    ("L54", mv([-1.6, -1.6, 21.4], [1.0, -0.3, 20.3], 20), {}),
    # (L55: from behind the cot, the lamp low and the lights through the south glass above and beyond it)
    ("L55", mv([0.6, 0.9, 20.8], [2.05, -3.9, 20.5], 30), {}),
    ("L56", mv([1.5, 0.6, 21.2], [500.0, -700.0, -110.0], 26), {}),
    ("L58", mv([-0.3, -0.3, 21.2], [-1.35, 0.35, 21.15], 30), {}),
    ("L59", mv([0.2, 1.0, 20.8], [2.15, -3.7, 20.5], 22, [0.55, 0.9, 20.8], [2.1, -3.9, 20.5], 24), {}),
    # ---- 06 the walk. The stairs, the gate, the road low wide, its foot in my pool (on ones), the shelf at first light
    ("L61", mv([3.0, -1.8, 21.0], [0.8, -0.4, 20.9], 24), {}),
    ("L62", mv([-6.0, 5.0, 13.0], [1.5, -6.0, 11.0], 22), {}),
    ("L63", mv([-2.0, 0.6, 1.7], [-1.8, -8.0, 0.6], 22), {}),
    # it's never seen walking: each shot holds one pose of it, and it steps between the cuts (RULES, the creature)
    ("L64", mv([0.6, -40.0, -3.2], [0.0, -16.0, 8.0], 18, [0.6, -39.0, -3.0], [0.0, -16.0, 8.5], 18), {"hand": 0.004}),
    ("L64.1", mv([-2.5, -42.0, -3.3], [0.0, -13.0, 13.0], 28), {"hand": 0.003}),
    ("L64b", mv([2.8, -46.0, -4.0], [0.3, -14.0, 12.0], 34), {"hand": 0.003}),
    ("L65", mv([6.2, -26.5, -0.4], [2.6, -23.5, -0.5], 24), {"step": 1, "hand": 0.003}),
    ("L65.2", mv([-3.5, -33.0, -0.2], [2.5, -23.5, -0.5], 34), {"step": 1, "hand": 0.003}),
    ("L66", mv([3.6, -35.5, -1.7], [3.2, -31.5, -0.3], 30), {"hand": 0.003}),
    ("L67", mv([-6.0, -76.0, -8.0], [0.5, -53.0, 3.5], 22), {}),
    ("L67.1", mv([5.0, -100.0, 2.0], [1.0, -58.0, 3.0], 34), {}),
    ("L68", mv([62.0, -300.0, -40.0], [43.0, -268.0, -52.0], 22), {}),
    ("L69", mv([41.0, -262.0, -46.0], [55.0, -880.0, -150.0], 34), {}),
    ("L70", mv([34.0, -240.0, -26.0], [52.0, -880.0, -150.0], 36), {}),
    # it's seen in poses, cut by cut: behind me, past me, then down the slope into the trees
    ("L71", mv([46.0, -281.0, -47.5], [46.0, -256.0, -34.0], 20), {}),
    ("L71.1", mv([30.0, -258.0, -46.0], [57.0, -268.0, -38.0], 22), {}),
    ("L71.2", mv([45.2, -272.7, -48.6], [43.0, -270.0, -48.7], 40), {}),
    ("L72", mv([47.0, -270.0, -37.5], [82.0, -258.0, -36.0], 24), {}),
    ("L72.2", mv([47.0, -270.0, -37.5], [108.0, -250.0, -33.0], 30), {}),
    ("L72.3", mv([47.0, -270.0, -37.5], [134.0, -244.0, -34.0], 40), {}),
    # ---- 07 spring: low on the road, a small pine in a print, a slow tilt up the line of them to the tower's gate
    ("L73", mv([1.2, -38.0, -2.3], [-0.5, -34.0, -2.4], 26, [1.2, -38.0, -2.1], [-1.0, -2.0, 3.0], 26), {}),
    ("L73.3", mv([0.3, -24.0, 1.3], [0.0, -4.0, 3.0], 26), {}),
]
shots = []
for i, (at, cam, opt) in enumerate(SH):
    s = {"id": f"S{i + 1:02d}", "cam": cam, "step": opt.get("step", 2)}
    if i:
        s["at"] = at
    if "hand" in opt:
        s["hand"] = opt["hand"]
    shots.append(s)

# ---------------------------------------------------------------------------------------------------- acting


def jump(at, frm, to, **kw):
    """A move on a cut: two keys at the same moment, so nobody walks on film."""
    return [{"at": at, "pos": frm}, {"at": at, "pos": to, "blend": 0.0, **kw}]


HOLD = dict(arms=[20, 0])                 # the lamp at my side on its bail
HIGH = dict(arms=[155, 0])                # the lamp held high
RAILS = dict(arms=[82, 82])               # both hands resting on the rail's top (at 0.54 m from it)
BINO = dict(arms=[102, 102])              # binoculars up to my eyes
me = [
    # 01
    {"at": 0, "pos": GLASS_S, "yaw": 0, "expr": "neutral", "arms": [0, 0], "head": [0, 4]},
    *jump("L02", GLASS_S, [0.25, -0.65, CAB_Z], yaw=160, expr="neutral", head=[0, -2], **HOLD),
    *jump("L05", [0.25, -0.65, CAB_Z], GLASS_E, yaw=90, expr="neutral", head=[0, 2], arms=[0, 0]),
    *jump("L06", GLASS_E, GLASS_S, yaw=0, expr="neutral", head=[0, -6]),
    {"at": "L07", "pos": GLASS_S, "yaw": 0, "expr": "neutral", "head": [0, 0]},
    # 02
    *jump("L08", GLASS_S, GLASS_N, yaw=180, expr="neutral", head=[0, 2], **BINO),
    {"at": "L10", "pos": GLASS_N, "expr": "worried"},
    {"at": "L11", "pos": GLASS_N},
    *jump("L12", GLASS_N, RADIO_AT, yaw=180, expr="worried", arms=[0, 72], head=[0, -8]),
    *jump("L14", RADIO_AT, COT, yaw=-90, sit=True, expr="neutral", arms=[0, 0], head=[0, 0]),
    {"at": "L15", "pos": COT, "expr": "worried", "head": [-10, 6]},
    # (back from the glass: the radio held up toward the dark stops short of it)
    *jump("L18", COT, RADIO_UP, yaw=0, sit=False, expr="worried", arms=[0, 85], head=[0, 4]),
    {"at": "L20", "pos": RADIO_UP, "expr": "scared", "arms": [0, 85]},
    {"at": "L20.1", "pos": RADIO_UP, "expr": "scared", "arms": [0, 30]},
    # 03: down the stairs in the morning, the prints, then back up on the catwalk at dusk
    # (a flight below the top one: the top flight runs under the cab floor)
    # (the third flight down: higher up, the tower's braced faces come in close to the stairs)
    *jump("L21", RADIO_UP, flight(2, 0.16), yaw=0, expr="neutral", arms=[0, 0], head=[0, -20]),
    {"at": "L21>", "pos": flight(2, 0.5)},
    *jump("L22", flight(2, 0.5), [5.0, -11.5, 0.0], yaw=-130, expr="worried", head=[0, -14]),
    *jump("L23", [5.0, -11.5, 0.0], [2.5, -13.2, 0.1], yaw=0, expr="worried", head=[0, -30]),
    *jump("L26", [2.5, -13.2, 0.1], [3.8, -9.5, 0.0], yaw=10, expr="worried", head=[0, -6]),
    *jump("L27", [3.8, -9.5, 0.0], at_floor([-0.6, -2.45]), yaw=-35, expr="neutral", **RAILS, head=[0, -14]),
    {"at": "L28", "pos": at_floor([-0.6, -2.45]), "expr": "worried"},
    *jump("P02", at_floor([-0.6, -2.45]), at_floor([0.55, -2.4]), yaw=0, expr="scared", **HOLD, head=[0, -10]),
    *jump("L33", at_floor([0.55, -2.4]), GLASS_W, yaw=95, expr="scared", arms=[0, 0], head=[0, 0]),
    # 04: the cab at night, out the door onto the catwalk with the lamp, the lean, the lights
    *jump("L34", GLASS_W, at_floor([0.4, -1.3]), yaw=0, expr="terrified", **HOLD, head=[0, -4]),
    # out of the door onto the catwalk (the shot cuts before I'd walk along it: it's 1 m wide and I'm 1.36)
    # (I start outside the door's swing, 1.6 m round its hinge, and reach it as it finishes opening)
    *jump("L36", at_floor([0.4, -1.3]), at_floor([0.3, 0.35]), yaw=-90, expr="scared", **HOLD),
    {"at": "L36>", "pos": DOOR_OUT},
    # the lamp held up high at the rail (inside its line: lowered from out over the rail it would cross it)
    *jump("L37", DOOR_OUT, RAIL, yaw=0, expr="scared", arms=[160, 0], head=[0, -4]),
    # on the cut: my left hand grips the rail; the lamp hangs from my right at my side, swinging clear of the toe
    # board (both keys carry arms, so nothing blends across L37 to L41)
    {"at": "L41", "pos": RAIL, "arms": [160, 0]},
    {"at": "L41", "pos": RAIL, "blend": 0.0, "yaw": 0, "expr": "terrified", "arms": [20, 82], "head": [0, -6]},
    {"at": "L43", "pos": RAIL, "yaw": -57, "arms": [64, 84], "head": [-56, 4], "look": [0.95, -0.05],
     "expr": "terrified", "blink": False, "tremble": 1.2},
    # hold the fear close's pose to its cut, then both hands on the rail (the lamp set down at my side)
    {"at": "L44", "pos": RAIL, "yaw": -57, "arms": [64, 84], "head": [-56, 4], "look": [0.95, -0.05]},
    {"at": "L44", "pos": RAIL, "blend": 0.0, "yaw": 0, **RAILS, "head": [0, 2], "look": [0, 0]},
    {"at": "L49", "pos": RAIL, "yaw": 0, "head": [8, 0], "expr": "terrified", "tremble": 2.0},
    # the radio off my belt as it clicks (L50), up to my mouth, my eyes on the lights
    {"at": "L50", "pos": RAIL, "tremble": 0.6, "arms": [82, 82]},
    {"at": "L50+0.4", "pos": RAIL, "arms": [82, 115]},
    {"at": "L51", "pos": RAIL, "yaw": 0, "arms": [82, 115], "head": [0, 2], "expr": "terrified", "blink": True},
    # 05: back inside, the lamp to the far window, onto the cot, me into the corner
    *jump("L52", RAIL, DOOR_IN, yaw=90, expr="scared", **HOLD, head=[0, 0]),
    {"at": "L52.2", "pos": EAST_WIN, "yaw": 90},
    # the lamp onto the cot: up over its edge first (the lamp hangs 0.56 m under my hand and the cot is 0.48 m
    # high), a step in, then down onto it; then I back away into the corner
    {"at": "L54", "pos": EAST_WIN, "yaw": 90, "arms": [20, 0]},
    {"at": "L54+0.3", "pos": EAST_WIN, "yaw": 90, "arms": [74, 0]},
    {"at": "L54+0.6", "pos": AT_COT, "yaw": 90, "arms": [74, 0]},
    {"at": "L54.1", "pos": AT_COT, "yaw": 90, "arms": [67, 0]},
    {"at": "L54.1+0.3", "pos": AT_COT, "yaw": 90, "arms": [30, 0]},
    {"at": "L54>", "pos": CORNER_NW, "arms": [0, 0], "yaw": 60, "expr": "scared"},
    {"at": "L58", "pos": CORNER_NW, "yaw": 60, "expr": "wide", "head": [0, 0]},
    {"at": "L59", "pos": CORNER_NW, "expr": "worried"},
    # 06: the lamp held high, down the stairs, out the gate, down the road all night, the shelf at first light
    # its reverse: my hand on the lamp at the cot, then up (it clears the cot's top above 67 degrees) and back a step
    *jump("L61", CORNER_NW, AT_COT, yaw=90, expr="neutral", arms=[67, 0], head=[0, -10]),
    {"at": "L61.1", "pos": AT_COT, "yaw": 90, "arms": [67, 0], "keep_yaw": True},   # (stepping back, still facing it)
    {"at": "L61.1+0.5", "pos": EAST_WIN, "yaw": 90, **HIGH, "head": [0, 6]},
    *jump("L62", EAST_WIN, flight(3, 0.18), yaw=-90, expr="neutral", **HIGH, head=[0, 0]),
    {"at": "L62>", "pos": flight(3, 0.6)},
    # the gate at the stairs' foot: off the last flight, I turn south through it
    *jump("L63", flight(3, 0.6), GATE_IN, yaw=0, **HIGH, expr="neutral"),
    {"at": "L63.1", "pos": GATE_IN}, {"at": "L63>", "pos": GATE_OUT},
    # down the road at a walk (about 2 m/s), it 7.7 m behind me (road u 0.03), so its toes stay 3 m behind my heels
    *jump("L64", GATE_OUT, road(U_ME["L64"][0], 1.2), yaw=0, **HIGH, expr="neutral"),
    {"at": "L64>", "pos": road(U_ME["L64"][1], 1.2)},
    {"at": "L65>", "pos": road(U_ME["L65"][1], 1.2)},
    {"at": "L66", "pos": road(U_ME["L66"][0], 1.2), "expr": "neutral"},
    {"at": "L66>", "pos": road(U_ME["L66"][1], 1.2)},
    *jump("L67", road(U_ME["L66"][1], 1.2), road(U_ME["L67"][0], 1.2), **HIGH),
    {"at": "L67>", "pos": road(U_ME["L67"][1], 1.2)},
    *jump("L68", road(U_ME["L67"][1], 1.2), ON_SHELF, yaw=0, **HOLD, expr="neutral", head=[0, -16]),
    {"at": "L71", "pos": ON_SHELF, "yaw": 40, "expr": "neutral", "head": [10, -6]},
    {"at": "L71.1", "pos": ON_SHELF, "expr": "soft"},
    # 07: not in frame
    {"at": "L73", "pos": ON_SHELF, "hidden": True},
]
acting = {"me": me}

# ---------------------------------------------------------------------------------------------------- cues
LIGHTS_ON = "L04.2"
cues = [
    # the whole light (set.py LOOKS)
    {"at": 0, "name": "look", "id": "dayfar"}, {"at": "L02", "name": "look", "id": "day"},
    {"at": "L06", "name": "look", "id": "clear"},
    {"at": "L07", "name": "look", "id": "day"}, {"at": "L08", "name": "look", "id": "bino"},
    {"at": "L10", "name": "look", "id": "day"}, {"at": "L11", "name": "look", "id": "bino"},
    {"at": "L12", "name": "look", "id": "day"}, {"at": "L14", "name": "look", "id": "night"},
    {"at": "L21", "name": "look", "id": "day"}, {"at": "L27", "name": "look", "id": "dusk"},
    {"at": "L34", "name": "look", "id": "nighthigh"}, {"at": "L40", "name": "look", "id": "nightlean"},
    {"at": "L41", "name": "look", "id": "nighthigh"}, {"at": "P03", "name": "look", "id": "night"},
    {"at": "L56", "name": "look", "id": "nightvalley"}, {"at": "L58", "name": "look", "id": "night"},
    {"at": "L63", "name": "look", "id": "nightroad"}, {"at": "L67.1", "name": "look", "id": "nightroadhi"},
    {"at": "L68", "name": "look", "id": "dawn"},
    {"at": "L73", "name": "look", "id": "spring"},
    # the lantern: in my hand, set down, held high (it never flickers or goes out)
    {"at": 0, "name": "lamp", "pos": [0.9, -1.3, CAB_Z]},
    {"at": "L02", "name": "lamp", **LAMP_HAND},
    {"at": "L05", "name": "lamp", "pos": [0.9, -1.3, CAB_Z]},
    {"at": "L14", "name": "lamp", "pos": LAMP_TABLE},
    {"at": "L21", "name": "lamp", "pos": LAMP_COT},
    {"at": "P02", "name": "lamp", **LAMP_HAND, "swing": 6.0, "decay": 1.0},
    {"at": "L33", "name": "lamp", "pos": LAMP_TABLE},
    {"at": "L34", "name": "lamp", **LAMP_HAND},
    {"at": "L41", "name": "lamp", "hand": "me.arm-1", "offset": [0.0, 0.0, -0.56], "swing": 12.0, "decay": 1.4},
    {"at": "L43", "name": "lamp", **LAMP_HAND},
    # set down on the catwalk at my right side, inside the toe board: it rakes the bark from behind me (L44)
    {"at": "L44", "name": "lamp", "pos": [0.05, -2.62, CAB_Z]},
    {"at": "L52", "name": "lamp", **LAMP_HAND},
    {"at": "L54.1", "name": "lamp", "pos": LAMP_SET},
    {"at": "L61.1", "name": "lamp", **LAMP_HAND},
    {"at": "L62", "name": "lamp", **LAMP_HAND, "swing": 5.0, "decay": 1.5},
    {"at": "L68", "name": "lamp", **LAMP_HAND},
    {"at": "L73", "name": "lamp", "pos": LAMP_COT},
    {"at": "L67.1", "name": "lampglow", "k": 18.0}, {"at": "L68", "name": "lampglow", "k": 1.0},
    # the radio's green light while she transmits (none of her audio plays), and the radio in my hand at L18 to L20
    {"at": 0, "name": "radio", "on": False},
    {"at": LIGHTS_ON, "name": "radio", "on": True}, {"at": "L04>+0.2", "name": "radio", "on": False},
    {"at": "L13.1", "name": "radio", "on": True}, {"at": "L13>+0.35", "name": "radio", "on": False},
    {"at": "L19.1", "name": "radio", "on": True}, {"at": "L19>+0.2", "name": "radio", "on": False},
    {"at": "L50", "name": "radio", "on": True}, {"at": "P04+0.6", "name": "radio", "on": False},
    {"at": "L18", "name": "radio", "hand": "me.arm1"}, {"at": "L21", "name": "radio", "hand": None},
    {"at": "L50", "name": "radio", "hand": "me.arm1"}, {"at": "L52", "name": "radio", "hand": None},
    {"at": "L08", "name": "binos", "hand": "me.arm-1"}, {"at": "L12", "name": "binos", "hand": None},
    # the door onto the catwalk, the gate onto the road, the tower's lean
    {"at": 0, "name": "door", "open": 0.0}, {"at": "L35>", "name": "door", "open": 1.0, "dur": 0.4},
    {"at": 0, "name": "gate", "open": 0.0}, {"at": "L63", "name": "gate", "open": 1.0, "dur": 0.7},
    {"at": "L73", "name": "gate", "open": 0.0},
    {"at": 0, "name": "lean", "deg": 0.0}, {"at": "L39", "name": "lean", "deg": 2.4, "dur": 0.7},
    {"at": "L41", "name": "lean", "deg": 0.0, "dur": 1.0},
    # its breaths: the lights swell about 15% (L47, P04); the first ones are heard only
    {"at": "L47", "name": "breath"}, {"at": "P04", "name": "breath"},
    # the giant (set.py giant_state). Its walks put a footfall on every beat of the score's pulse (40 bpm, from the
    # section's start), so the score walks with it
    {"at": 0, "name": "giant", "pos": FAR, "yaw": 22.6, "pitch": 3.0, "lights": 0.7},
    {"at": "L02", "name": "giant", "pos": FAR, "hidden": True},
    {"at": "L28", "name": "giant", "hidden": True,
     "walk": {"from": [-80.0, -50.0], "to": [-36.0, -15.0], "until": "P02", "beat0": "P02", "stride": -12.0}},
    {"at": "P02", "name": "giant",
     "walk": {"from": WALK_UP[0], "to": WALK_UP[1], "until": "L34", "beat0": "P02", "stride": -14.0}},
    {"at": "L34", "name": "giant", "pos": FEAR, "hidden": True},
    {"at": "L37", "name": "giant", "pos": LEAN, "yaw": 205.0, "pitch": 10.0, "head": -20.0, "lights": 0.0},
    {"at": "L42", "name": "giant", "pos": FEAR, "yaw": 180.0, "pitch": 7.0, "head": 12.0, "rise": {"from": -4.0, "dur": 1.8},
     "fade": 1.3},
    {"at": "L43", "name": "giant", "pos": FEAR, "yaw": 180.0, "pitch": 7.0, "head": 12.0},
    {"at": "L52", "name": "giant", "pos": FEAR, "yaw": 180.0, "pitch": 7.0, "look_lamp": True},
    {"at": "L62", "name": "giant", "pos": [2.0, -13.0, -6.0], "yaw": 180.0, "pitch": 7.0, "look_lamp": True,
     "rise": {"from": 6.0, "dur": 1.6}},
    {"at": "L63", "name": "giant", "pos": [0.0, -2.0, 0.0], "hidden": True},
    # down the road, one held pose per shot (it steps between the cuts, never on screen), about 8 m behind me, on
    # the road's middle (I walk 1.2 m to its side, so its left foot comes down in my path, where my light just was)
    gpose("L64", 0.019, 6.0), gpose("L64.1", 0.0245, -6.0), gpose("L64b", 0.031, 6.0), gpose("L65", 0.036, 6.0),
    gpose("L65.2", 0.043, -6.0), gpose("L66", 0.051, 6.0), gpose("L67", 0.179, -6.0), gpose("L67.1", 0.187, 6.0),
    {"at": "L68", "name": "giant", "pos": [40.5, -254.0, 0.0], "yaw": 190.0, "pitch": 3.0, "head": 0.0},
    # behind me, past me (9 m clear of me at the nearest), then down the slope into the trees, a pose to a shot
    {"at": "L71", "name": "giant", "pos": [46.0, -256.0, 0.0], "yaw": 0.0, "pitch": 3.0, "stride": -6.0, "pines": True},
    {"at": "L71.1", "name": "giant", "pos": [57.0, -268.0, 0.0], "yaw": 35.0, "pitch": 3.0, "stride": 6.0, "pines": True},
    {"at": "L71.2", "name": "giant", "pos": [64.0, -278.0, 0.0], "yaw": 45.0, "pitch": 3.0, "stride": -6.0, "pines": True},
    {"at": "L72", "name": "giant", "pos": [82.0, -258.0, 0.0], "yaw": 90.0, "pitch": 3.0, "stride": 6.0, "pines": True},
    {"at": "L72.2", "name": "giant", "pos": [108.0, -250.0, -4.0], "yaw": 90.0, "pitch": 3.0, "stride": -6.0, "pines": True},
    {"at": "L72.3", "name": "giant", "pos": [134.0, -244.0, -9.0], "yaw": 90.0, "pitch": 3.0, "stride": 6.0, "pines": True},
    {"at": "L73", "name": "giant", "pos": [134.0, -244.0, 0.0], "hidden": True},
]

fx = [{"at": "L39", "kind": "shake", "dur": 0.8, "amp": 0.45}]

# ---------------------------------------------------------------------------------------------------- sound
BEAT = 1.5                                # 40 bpm


def beats(start, until_s, every=BEAT):
    """Footfall references every beat from a line reference, for `until_s` seconds."""
    return [f"{start}+{k * every:.2f}" for k in range(int(until_s / every) + 1)]


steps1 = beats("P02", 9.0)                # the walk up the ridge, P02 to L35 (heard only from L34)
steps2 = beats("L64.1", 6.4)              # down the road (L64.1 to L68)
steps3 = beats("L71", 4.4)                # past me and down the slope, fading
sfx = [
    # the radio: a click, a static burst, the green light (none of the ranger's audio plays)
    *[{"at": a, "kind": "radio", "db": -15} for a in (LIGHTS_ON, "L13.1", "L19.1", "L50")],
    {"at": "L04>+0.15", "kind": "click", "db": -14}, {"at": "L13>+0.3", "kind": "click", "db": -13},
    {"at": "P04+0.6", "kind": "click", "db": -14},
    {"at": "L12", "kind": "click", "db": -14}, {"at": "L18", "kind": "click", "db": -14},
    {"at": "L20", "kind": "click", "db": -12},
    # its breath, slow and heavy, ending in a trunk's creak
    {"at": "L15.1", "kind": "breath", "db": -15, "dur": 2.6}, {"at": "L17.1", "kind": "creak", "db": -16, "dur": 0.9},
    {"at": "P01", "kind": "breath", "db": -13, "dur": 2.2}, {"at": "P01+0.55", "kind": "creak", "db": -15, "dur": 0.9},
    {"at": "L47", "kind": "breath", "db": -10, "dur": 2.4}, {"at": "L48", "kind": "creak", "db": -12, "dur": 1.0},
    {"at": "P04", "kind": "breath", "db": -11, "dur": 2.0}, {"at": "P04+0.5", "kind": "creak", "db": -13, "dur": 0.9},
    # its footfalls: a deep thud, a timber creak and a rustle, on the pulse
    *[{"at": a, "kind": "thud", "db": -6 if k == 0 else -10} for k, a in enumerate(steps1)],
    *[{"at": a, "kind": "creak", "db": -18, "dur": 0.5} for a in steps1],
    *[{"at": a, "kind": "whoosh", "db": -24} for a in steps1],
    {"at": "L35.2", "kind": "thud", "db": -5},
    *[{"at": a, "kind": "thud", "db": -6 if k == 0 else -9} for k, a in enumerate(steps2)],
    *[{"at": a, "kind": "creak", "db": -18, "dur": 0.5} for a in steps2],
    *[{"at": a, "kind": "thud", "db": -12 - 2 * k} for k, a in enumerate(steps3)],
    # the scare: the door, the tower's long groan, the lean, the lamp's bail, the hole, the sting
    {"at": "L35>", "kind": "door", "db": -16},
    {"at": "L38", "kind": "creak", "db": -9, "dur": 2.2}, {"at": "L39", "kind": "creak", "db": -10, "dur": 1.4},
    {"at": "L41.1", "kind": "creak", "db": -20, "dur": 0.5},
    {"at": "P03", "kind": "creak", "db": -12, "dur": 1.6, "keep": True},
    {"at": "L42-0.04", "kind": "sting", "db": -11, "dur": 2.4, "keep": True},
    {"at": "L63", "kind": "door", "db": -16},
]
story = {
    "slug": "ep16-lookout",
    "title": "Every pine on the far ridge snapped at the same height",
    "made_for_kids": False,
    "premise": "Alone in a fire lookout's glass cab above an autumn forest, with a lamp, binoculars and a radio, I watch a giant made of the forest walk the ridges in thick fog, and each sign of it is nearer than the last: seen, heard, traces, moving, close, felt.",
    "twist": "It isn't hunting me. It steers by the river, the smoke has hidden the river, and my lamp is the only light that keeps still. I carry the lamp down the fire road at first light until it can see the river again.",
    "world": "A fire lookout tower: a 4 m glass cab on braced steel legs 19.6 m up, a plank catwalk and rail, an autumn forest of dark pines and gold larch in fog, a fire road down to a rocky shelf over a smoky valley.",
    "voice": {"voice": "am_adam", "tempo": 1.03, "rate": 1.45},
    "key_color": "#ffb22e",
    "gap": 0.12,
    "tail": 0.25,
    "look": {"fog": "#2a3238", "fog_density": 0.034, "fog_start": 3.0, "sky": "#2a3238", "exposure": 1.6},
    "grade": {"shadows": [-0.02, 0.01, 0.02], "highlights": [0.04, 0.015, -0.03], "saturation": 0.9,
              "contrast": 1.08, "vignette": 0.35, "bloom": 0.45, "grain": 0.014, "red_line": 0.79},
    "phonemes": {},
    "cast": cast,
    "lines": lines,
    "shots": shots,
    "acting": acting,
    "cues": cues,
    "fx": fx,
    # dorian on E2, 40 bpm (brief). The pulse plays only while it walks, so its sections are its walks and their
    # footfalls are the pulse's beats. Piano only on the walk down; the low choir once, at first light. No music box
    "music": {"root": 40, "mode": "dorian", "bpm": 40, "seed": 14,
              "sections": [
                  {"at": 0, "voices": ["drone", "pad"], "energy": 0.25},
                  {"at": "L14", "voices": ["drone", "pad"], "energy": 0.32},
                  {"at": "L21", "voices": ["drone", "pad"], "energy": 0.28},
                  {"at": "P02", "voices": ["drone", "pad", "pulse"], "energy": 0.75},
                  {"at": "L35.2", "voices": ["drone", "pad"], "energy": 0.3},
                  {"at": "L42", "voices": ["drone", "pad"], "energy": 0.4},
                  {"at": "L52", "voices": ["drone", "pad"], "energy": 0.3},
                  {"at": "L64.1", "voices": ["drone", "pad", "pulse", "piano"], "energy": 0.75},
                  {"at": "L68", "voices": ["pad", "piano"], "energy": 0.4},
                  {"at": "P06", "voices": ["pad", "choir"], "energy": 0.45},
                  {"at": "L71", "voices": ["pad", "pulse", "piano"], "energy": 0.72},
                  {"at": "L73", "voices": ["pad"], "energy": 0.3},
              ]},
    "sound": {"floor": "wood", "steps_db": -22,
              # opt-in (sound.py): soft dirt on the road and at the tower's foot, wood in the tower
              "floor_spans": [{"from": "L22", "to": "L27", "floor": "grass"}, {"from": "L63", "to": "L73", "floor": "grass"}],
              "ambience": [
                  {"kind": "wind", "from": 0, "to": "L14", "lufs": -36},
                  {"kind": "static", "from": "L14", "to": "L21", "lufs": -44},
                  {"kind": "drips", "from": "L14", "to": "L21", "lufs": -40},
                  {"kind": "wind", "from": "L21", "to": "L34", "lufs": -37},
                  {"kind": "wind", "from": "L34", "to": "L63", "lufs": -40},
                  {"kind": "drone", "from": "L38", "to": "P04", "lufs": -38},
                  {"kind": "static", "from": "L50", "to": "P05", "lufs": -45},
                  {"kind": "drips", "from": "L52", "to": "L61", "lufs": -42},
                  {"kind": "wind", "from": "L63", "to": "L68", "lufs": -38},
                  {"kind": "water", "from": "L68", "to": "L73", "lufs": -40},
                  {"kind": "wind", "from": "L73", "to": "end", "lufs": -42},
              ],
              "sfx": sfx,
              # the one hole (brief): 0.6 s at -40 dB before the lights rise, keeping the creak and the sting
              "music_drops": [{"from": "P03", "to": "L42", "keep": ["creak", "sting"]}]},
}
OUT.write_text(json.dumps(story, indent=1, ensure_ascii=False) + "\n")
print("wrote", OUT, f"({len(shots)} shots)")
