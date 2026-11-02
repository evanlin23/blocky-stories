"""Writes ../story.json for ep42 "barber-chair" (a town where everyone hums one note, and the third chair in my stepdad's shop).

Run from anywhere: python stories/ep42-barber-chair/generator/make_story.py
The words are in lines.json next to this file. Everything else is here: the cast, the shots, the acting, the cues set.py
reads, the effects, the score, the hums and the sound. Shots are numbered in order (S01 ...).

Places (set.py's coordinates): the high street runs along x (pavement y 0.2 to 2.0, road to the south); the shop is the
narrow room x -1.9 to 1.9, y 2.0 (window and glass door) to 11.4 (the sink). Chairs at x = -0.2: Len's y 4.4, Sid's
6.1, the third 7.8, all facing the mirror (-x). Waiting chairs by the door at x = 1.3. The cafe (60, 0), the bus (-60, 0),
Pat's flat (0, 60) and our kitchen (60, 60) are far rooms.
"""
import json
import math
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE.parent / "story.json"
lines = json.loads((HERE / "lines.json").read_text())
GAPS = {"L17": 0.6, "L20": 0.8, "L29": 0.6, "L35": 0.6, "L38": 0.6, "L40": 0.8, "L53": 0.6, "L56": 0.8, "L61": 0.5}
for ln in lines:
    if ln["id"] in GAPS:
        ln["gap"] = GAPS[ln["id"]]

FACE = 1.57                    # a standing face's height
CHX = -0.2
CY = {"len": 4.4, "sid": 6.1, "third": 7.8}
WAIT = [(1.30, 2.85), (1.30, 4.35), (1.30, 5.85)]
SINK = (0.7, 11.0)
LEN_SINK = (0.7, 10.35)
CAFE, BUS, FLAT, KIT = (60.0, 0.0), (-60.0, 0.0), (0.0, 60.0), (60.0, 60.0)


def c(*keys):
    return [list(k) for k in keys]


def C(p, t, lens=30):
    return c([0, list(p), list(t), lens])


def M(p0, t0, p1, t1, lens=30):
    """A camera move over the shot."""
    return c([0, list(p0), list(t0), lens], [1, list(p1), list(t1), lens])


def front(x, y, yaw, dist, off=0.0, dz=0.0, lens=34, push=0.0, face_z=FACE):
    """A camera in front of a face at (x, y): yaw the way they face (0 = -y), dist metres off, off degrees round."""
    a = math.radians(yaw + off)
    d = (math.sin(a), -math.cos(a))
    p0 = [round(x + d[0] * dist, 3), round(y + d[1] * dist, 3), round(face_z + dz, 3)]
    tg = [x, y, face_z]
    if not push:
        return c([0, p0, tg, lens])
    p1 = [round(x + d[0] * (dist - push), 3), round(y + d[1] * (dist - push), 3), round(face_z + dz, 3)]
    return c([0, p0, tg, lens], [1, p1, tg, lens])


# ---------------------------------------------------------------------------------------------------- the cast
def person(skin, shirt, pants, hair, hair_c, face, **kw):
    d = {"age": "adult", "skin": skin, "shirt": shirt, "pants": pants, "shoes": "#1c1612", "sleeves": "long", "hair": hair,
         "hair_c": hair_c, "hat": "none", "face": face}
    d.update(kw)
    return d


cast = {
    "me": person("#f1c9a0", "#1f2d4d", "#2a2d36", "swoop", "#2e1d12", {"eyes": "round", "brows": True},
                 extras=["coat", "scarf"], zip_c="#12192b", extra_c="#d6a62c"),
    "len": person("#e9bd9a", "#bfc1c4", "#23242a", "none", "#9a9a9c", {"eyes": "tired", "brows": True, "bags": True},
                  sleeves="short"),
    "sid": person("#f0cfb0", "#6d4a30", "#4a4338", "cap", "#f0f0ee", {"eyes": "round", "brows": True, "bags": True},
                  pattern="knit", pattern_c="#563a24", collar="#f2f0ea"),
    "mum": person("#ecc7a8", "#6a2f5a", "#2c2630", "cap", "#7a6a5c", {"eyes": "lashes", "brows": True},
                  extras=["coat"], zip_c="#3a1a30"),
    "pat": person("#f4d6b8", "#e8c54a", "#4a4658", "bun", "#8a5a2c", {"eyes": "lashes", "brows": True, "cheeks": "#e49a86"},
                  pattern="knit", pattern_c="#c9a336"),
    "ostro": person("#e0b088", "#5a3d26", "#2e2a26", "buzz", "#b8b0a6", {"eyes": "round", "brows": True, "bags": True},
                    collar="#eeeae0", height=1.06, width=1.25),
    "c1": person("#e0b088", "#2f4a3a", "#2a2d36", "cap", "#2a1d15", {"eyes": "round", "brows": True}, extras=["coat"], zip_c="#1a2a22"),
    "c2": person("#c98e66", "#6b2f33", "#241f22", "long", "#1a1a1a", {"eyes": "lashes", "brows": True}, extras=["coat"], zip_c="#3a1a1c"),
    "c3": person("#f4d6b8", "#44384f", "#2a2d36", "spiky", "#8a6a3a", {"eyes": "round", "brows": True, "freckles": True}),
    "c4": person("#8f5d3e", "#d6a62c", "#2a2d36", "buzz", "#1a1a1a", {"eyes": "button", "brows": True}, hat="beanie", hat_c="#4a4e57"),
    "c5": person("#f1c9a0", "#5a5448", "#33302c", "cap", "#6a3a22", {"eyes": "round", "brows": True, "bags": True},
                 extras=["coat"], zip_c="#2a2824"),
    "c6": person("#a87050", "#3b4a63", "#23242a", "swoop", "#1a1a1a", {"eyes": "tired", "brows": True}, extras=["scarf"], extra_c="#a83a3a"),
    "c7": person("#f0cfb0", "#7a5a3a", "#2c2f38", "bun", "#4a3020", {"eyes": "lashes", "brows": True}, extras=["coat"], zip_c="#3a2a1a"),
    "c8": person("#e9bd9a", "#8a3a4a", "#2a2d36", "long", "#8a6a3a", {"eyes": "lashes", "brows": True}, extras=["coat"], zip_c="#4a1a24"),
    "c9": person("#c98e66", "#2c2f38", "#1c1c20", "cap", "#1a1a1a", {"eyes": "round", "brows": True}, hat="ballcap", hat_c="#8a3a2a"),
    "c10": person("#f4d6b8", "#4a6a6a", "#2a2d36", "long", "#b8b0a6", {"eyes": "lashes", "brows": True, "cheeks": "#e49a86"},
                  extras=["scarf"], extra_c="#e8d8c0"),
    "c11": person("#e0b088", "#6a4a2a", "#2a2d36", "buzz", "#2a1d15", {"eyes": "round", "brows": True}, extras=["coat"], zip_c="#3a2a14"),
    "c12": person("#8f5d3e", "#8a8a96", "#2a2d36", "cap", "#1a1a1a", {"eyes": "tired", "brows": True}),
}

# ---------------------------------------------------------------------------------------------------- poses
# A pose is a dict for one character in one shot: pos [x, y] (and z), yaw, sit, expr, head [yaw, pitch], look, arms [l, r].


def at(x, y, yaw=0, **kw):
    return {"pos": [x, y], "yaw": yaw, **kw}


def sitting(x, y, yaw, z=0.04, **kw):
    return {"pos": [x, y, z], "yaw": yaw, "sit": True, "arms": [34, 34], **kw}


SH = []        # (start ref, scene, camera, who, look, options)


def shot(ref, scene, cam, who=None, look=None, **opt):
    SH.append({"at": ref, "scene": scene, "cam": cam, "who": who or {}, "look": look or {}, "opt": opt})


# ---- the hook and the rule at work, in sun (S01 to S10)
shot(0, "day", C([0.0, -2.4, 1.45], [0.0, 0.95, 1.5], 26),
     {"c10": at(-0.66, 0.5, 0, expr="neutral", head=[8, 0]), "me": at(0.0, 0.95, 0, expr="worried", head=[0, 0]),
      "c3": at(0.66, 1.4, 0, expr="neutral", head=[-8, 0])}, {"crowd": 40, "crowd_box": [-9, 9, -3.4, 1.7]}, hand=0.004, step=1)
shot("L01.4", "day", M([0, -7.0, 10.0], [0, -0.5, 1.0], [1.5, -6.0, 9.0], [0, -0.5, 1.0], 30), {}, {"crowd": 64}, hand=0.0)
shot("L02", "day", C([3.0, -0.3, 1.5], [3.0, 0.7, 1.82], 40),
     {"c2": at(3.0, 0.7, 0, expr="neutral", head=[0, 0])}, {"crowd": 30, "crowd_box": [-9, 9, -3.4, 0.0]})
shot("L02.3", "day", C([-4.6, -1.7, 0.4], [-6.6, 0.6, 1.8], 26),
     {"c4": at(-8.0, 0.6, 200, expr="neutral"), "c5": at(-7.0, 0.6, 165, expr="soft"), "c6": at(-6.0, 0.6, 150, expr="neutral"),
      "c7": at(-5.0, 0.6, 140, expr="soft")}, {"crowd": 20, "crowd_box": [-12, -2, -3.4, 0.0]})
shot("L03", "day", C([1.0, -2.0, 1.5], [3.2, 0.85, 1.6], 30),
     {"c8": at(2.3, 0.8, 0, expr="soft", head=[-40, 0]), "c9": at(4.2, 0.9, 0, expr="soft", head=[40, 0])},
     {"crowd": 40, "crowd_box": [-2, 9, -3.4, 0.0], "pair": ["c8", "c9"]})
shot("L04", "day", C([-2.6, -2.4, 1.6], [-2.6, 0.9, 1.5], 28),
     {"c5": at(-3.1, 0.9, 55, expr="soft", head=[0, 0]), "c6": at(-2.1, 0.9, -55, expr="soft"),
      "c1": at(-4.3, 0.5, 20, arms=[50, 50]), "c2": at(-0.9, 0.6, -25, arms=[50, 50]), "c11": at(-3.2, 1.7, 180, arms=[50, 50])},
     {"crowd": 24, "crowd_box": [-9, 3, -3.4, 0.0]})
shot("L05", "day", C([-20.2, -1.0, 1.55], [-20.2, 3.6, 1.5], 28),
     {"ostro": at(-20.2, 3.4, 0, expr="soft")}, {"show": ["ostro"], "buzz": 1.0})
shot("L06", "bus", M([BUS[0] - 4.2, 0.0, 1.6], [BUS[0] + 1.5, 0.0, 1.5], [BUS[0] - 3.7, 0.0, 1.6], [BUS[0] + 1.5, 0.0, 1.5], 22),
     {f"c{k}": sitting(BUS[0] - 3.2 + ((k - 1) // 2) * 1.3, BUS[1] + (1.25, -1.25)[(k - 1) % 2], 90, z=-0.03, expr="soft")
      for k in range(1, 13)}, {})
shot("L07", "flat", C([FLAT[0] - 1.3, FLAT[1] - 1.2, 1.25], [FLAT[0] + 0.5, FLAT[1] + 1.6, 1.0], 30),
     {"pat": sitting(FLAT[0] - 0.4, FLAT[1] + 1.35, 0, z=-0.07, expr="worried", head=[-20, 8], arms=[10, 10])}, {"ringlook": {"pat": [0.35, 0.3]}})
shot("L08", "day", M([0.4, -2.6, 1.55], [0.2, 0.95, 1.55], [0.3, -1.8, 1.55], [0.2, 0.95, 1.55], 34),
     {"me": at(0.2, 0.95, 0, expr="neutral", head=[0, 0])}, {"crowd": 48, "crowd_box": [-6, 6, -3.4, 1.7]})
shot("L09", "day", C([0.4, -0.5, 2.2], [0.2, 0.95, 1.93], 70),
     {"me": at(0.2, 0.95, 0, expr="neutral")}, {"crowd": 20, "crowd_box": [-4, 4, -3.4, 0.0]})
shot("L10", "cafe", C([CAFE[0] + 2.2, CAFE[1] - 3.2, 1.9], [CAFE[0] - 0.2, CAFE[1] + 0.4, 1.0], 22),
     {**{f"c{k}": sitting(CAFE[0] + tx + sx, CAFE[1] + ty + sy, yw, z=-0.025, expr="soft", head=[0, 0])
         for k, (tx, ty, sx, sy, yw) in enumerate([(-2.6, 1.6, -0.62, 0, 90), (-2.6, 1.6, 0.62, 0, -90), (0.0, 1.8, -0.62, 0, 90),
                                                   (0.0, 1.8, 0.62, 0, -90), (2.7, 1.5, -0.62, 0, 90), (-1.4, -0.8, 0.62, 0, -90),
                                                   (1.4, -1.0, -0.62, 0, 90)], 1)}}, {})
shot("L10.3", "cafe", C([CAFE[0] + 3.4, CAFE[1] - 2.9, 1.55], [CAFE[0] + 1.0, CAFE[1] - 0.6, 1.45], 28),
     {"me": sitting(CAFE[0] + 2.02, CAFE[1] - 1.0, -90, z=-0.025, expr="neutral", head=[0, 0]),
      "c6": sitting(CAFE[0] + 1.4, CAFE[1] - 1.0 + 0.62, 0, z=-0.025, expr="worried", head=[60, 0]),
      "c7": sitting(CAFE[0] + 0.0, CAFE[1] + 1.8 + 0.62, 0, z=-0.025, expr="worried", head=[45, 0]),
      "c8": sitting(CAFE[0] - 1.4, CAFE[1] - 1.42, 180, z=-0.025, expr="worried", head=[-65, 0])}, {})

# ---- Len, and the shop: Tuesday, the first creature (S11 to S24)
shot("L11", "day", C([-0.55, -0.55, 1.5], [0.15, 4.4, 1.55], 32),
     {"len": at(0.55, 4.4, -90, expr="soft", arms=[10, 10]), "c11": sitting(CHX, 4.4, -90, expr="neutral")}, {"crowd": 0})
shot("L12", "dusk", C([-0.55, -0.55, 1.5], [0.15, 4.4, 1.55], 32),
     {"len": at(0.55, 4.4, -90, expr="neutral", arms=[10, 10]), "c11": sitting(CHX, 4.4, -90, expr="neutral")}, {"crowd": 0},
     hand=0.004)
shot("L13", "dusk", M([-2.3, -1.6, 1.45], [0.6, 1.4, 1.5], [-0.2, -1.8, 1.45], [0.9, 1.4, 1.5], 28),
     {"me": [at(-1.2, 1.0, 90, expr="neutral"), {"at": "L14-0.1", "pos": [1.4, 1.0], "yaw": 90}], "len": at(0.55, 4.4, -90, expr="neutral")}, {"crowd": 10, "crowd_box": [-5, 5, -2.5, 0.0]})
shot("L14", "dusk", front(0.55, 4.4, -90, 1.6, 20, 0.12, 34, face_z=FACE),
     {"len": at(0.55, 4.4, -90, expr="tired" if False else "neutral", arms=[10, 10])}, {"k": 0.45})
shot("L15", "dusk", C([1.1, 3.1, 1.55], [0.0, 6.1, 1.5], 30),
     {"sid": at(0.55, 6.1, -90, expr="soft", arms=[40, 20]), "c12": sitting(CHX, 6.1, -90, expr="neutral"),
      "len": at(0.55, 4.4, -90, expr="neutral")}, {})
shot("L16", "dusk", C([0.0, -2.4, 1.55], [0.0, 4.5, 1.4], 24),
     {"len": at(0.55, 4.4, -90, expr="neutral"), "sid": at(0.55, 6.1, -90, expr="neutral")}, {})
shot("L16.2", "dusk", front(-0.3, 1.1, 180, 1.9, 0, 0.0, 40, face_z=FACE),
     {"me": at(-0.3, 1.1, 180, expr="shut", head=[0, 0])}, {"inside": True, "nopane": True}, step=1)
shot("L17.1", "dusk", C([-0.95, 0.3, 1.65], [0.0, 7.4, 1.3], 28),
     {"me": at(-0.6, 0.9, 180, expr="worried"), "len": at(0.55, 4.4, -90, expr="neutral"), "sid": at(0.55, 6.1, -90, expr="neutral")}, {})
shot("L18", "dusk", C([-0.8, 0.5, 1.4], [1.3, 2.85, 1.2], 32), {"len": at(0.55, 4.4, -90)}, {})
shot("L19", "dusk", C([-0.4, 0.9, 2.4], [1.3, 2.85, 0.85], 30), {"len": at(0.55, 4.4, -90)}, {})
shot("L20", "shop", C([-1.7, 2.85, 1.9], [1.3, 2.85, 0.8], 16), {}, {"rows": [0.3, 0.3, 0.3], "mf": 0.2, "sink": 0.2})
shot("L21", "dusk", C([-0.4, 3.5, 1.6], [-0.4, 1.0, 1.6], 34),
     {"me": at(-0.4, 1.0, 180, expr="worried"), "len": at(-1.15, 3.7, 90, expr="neutral")}, {"frost": False, "crowd": 14, "crowd_box": [-5, 5, -2.5, 0.0], "inside": True, "k": 0.35, "nopane": True})
shot("L22", "dusk", C([-0.9, 0.3, 1.5], [-0.2, 6.1, 1.05], 32), {"len": at(0.55, 4.4, -90)}, {})
shot("L23", "dusk", M([0.8, 6.4, 0.55], [CHX - 0.3, 7.8, 0.2], [0.8, 6.6, 0.55], [CHX - 0.3, 7.8, 0.2], 26), {}, {"broom_xy": [-0.25, 7.4]}, hand=0.004)
shot("L23.2", "dusk", C([-0.66, 7.8, 0.045], [-1.12, 7.8, 0.03], 20), {}, {"broom_xy": [-0.58, 7.42], "no_props": True}, hand=0.003)
shot("L24", "flash", C([1.3, 5.4, 1.5], [-0.1, 7.8, 1.25], 30),
     {"len": at(0.5, 7.8, -90, expr="soft", arms=[60, 0], head=[0, 0]), "mum": at(0.9, 7.0, -60, expr="soft", head=[20, 0]),
      "me": at(0.7, 8.7, -90, expr="neutral", head=[10, 0])}, {"k": 0.4})
shot("L24.5", "flash", C([1.5, 4.6, 1.55], [0.3, 7.5, 1.3], 30),
     {"len": at(0.4, 7.4, -90, expr="soft", arms=[40, 10]), "mum": at(0.9, 6.8, -60, expr="soft"), "me": at(0.9, 8.5, -100, expr="neutral")}, {"k": 0.3, "world_k": 0.35})
shot("L25", "dusk", C([1.0, 5.2, 1.5], [-0.2, 7.6, 1.2], 26),
     {"len": at(0.3, 7.4, -90, expr="neutral", arms=[34, 34])}, {"broom_xy": [-0.5, 7.4], "k": 0.55, "nopane": True})

# ---- Thursday and Friday (S31 to S53)
shot("L26", "dusk", C([-0.6, 3.4, 1.55], [-0.2, 1.1, 1.6], 30),
     {"me": at(-0.2, 1.1, 180, expr="worried"), "len": at(-1.2, 3.8, 90, expr="neutral")}, {"frost": True, "crowd": 8, "crowd_box": [-5, 5, -2.5, 0.0], "inside": True, "k": 0.35, "nopane": True})
shot("L27", "dusk", C([-0.9, 0.3, 1.45], [-0.2, 7.8, 1.0], 34), {"len": at(0.55, 4.4, -90)}, {})
shot("L28", "dusk", C([1.5, 3.2, 1.8], [-0.2, 7.8, 1.0], 30), {"len": at(0.55, 4.4, -90)}, {})
shot("L29", "shop", C([0.5, 4.6, 1.35], [-1.89, 6.9, 1.2], 32), {}, {"rows": [1, 1, 1]})
shot("L29.4", "dusk", C([-0.3, 3.4, 1.55], [-0.3, 0.9, 1.6], 32),
     {"me": [at(-0.3, 1.0, 180, expr="scared", head=[0, 0]), {"at": "L29.4+0.25", "pos": [-0.3, 1.0], "yaw": 180, "keep_yaw": True},
             {"at": "L29.4+0.85", "pos": [-0.3, 0.5], "yaw": 180}], "len": at(-1.2, 3.8, 90)}, {"inside": True, "k": 0.35})
shot("L30", "kitchen", C([KIT[0] + 1.4, KIT[1] - 1.5, 1.5], [KIT[0] - 0.1, KIT[1] + 0.3, 1.0], 28),
     {"mum": sitting(KIT[0] - 0.85, KIT[1] + 0.3, -90, z=-0.025, expr="soft", head=[0, 0]),
      "me": at(KIT[0] + 0.7, KIT[1] + 0.5, 90, expr="neutral", arms=[60, 40])}, {})
shot("L31", "dusk", C([1.1, -2.2, 1.5], [0.9, 2.0, 1.3], 30), {"me": at(1.0, 0.6, 180, expr="neutral", arms=[40, 40])},
     {"k": 0.8, "ckey": [[2.0, 0.6, 2.2], [0.6, 4.5, 1.0], 450, 70], "cfill": [[-1.0, 0.8, 2.0], [0.2, 5.0, 1.0], 250, 70]})
shot("L31.3", "shop", C([1.3, 2.6, 1.6], [-0.2, 8.0, 1.3], 24),
     {"me": at(1.0, 2.5, 180, expr="worried")}, {"rows": [1, 1, 1]}, step=1)
shot("L32", "shop", C([-0.35, 8.7, 1.5], [0.7, 10.35, 1.45], 30), {"len": at(*LEN_SINK, 180, expr="neutral", arms=[30, 30])}, {"rows": [0, 0, 1]})
shot("L33", "shop", C([0.25, 9.2, 2.0], [0.7, 10.35, 1.94], 40), {"len": at(*LEN_SINK, 180, expr="neutral", arms=[30, 30])}, {"rows": [0, 0, 1]})
shot("L34", "shop", C([-0.5, 5.7, 1.5], [1.2, 2.6, 1.5], 30), {"me": at(1.2, 2.6, 180, expr="scared", head=[40, 0])}, {"rows": [0, 0, 1]})
shot("L35", "shop", M([1.0, 3.0, 1.5], [-0.2, 8.4, 1.2], [0.4, 5.4, 1.4], [-0.2, 8.4, 1.2], 26),
     {"len": at(*LEN_SINK, 180, expr="neutral", arms=[30, 30])}, {"rows": [0, 0, 0.7], "show_creature": True})
shot("L36", "shop", C([1.35, 6.0, 2.0], [-0.2, 7.8, 1.2], 34), {"len": at(*LEN_SINK, 180, arms=[30, 30])},
     {"rows": [0, 0, 0.3], "ckey": [[1.6, 6.8, 1.8], [-0.2, 7.9, 1.0], 500, 50]})
shot("L37", "shop", C([1.65, 6.4, 1.5], [-0.2, 7.8, 1.1], 30), {"len": at(*LEN_SINK, 180, arms=[30, 30])},
     {"rows": [0, 0, 0.2], "ckey": [[1.5, 7.0, 1.7], [-0.2, 7.9, 1.0], 600, 50]})
shot("L38", "shop", C([1.7, 11.0, 1.55], [-0.2, 8.0, 1.0], 28), {"len": at(0.9, 10.35, 200, expr="neutral", arms=[30, 30])},
     {"rows": [0, 0, 0.5], "ckey": [[1.6, 9.0, 1.6], [-0.2, 8.1, 1.0], 80, 40]})
shot("L39", "shop", C([-0.3, 10.9, 0.85], [-0.2, 8.2, 1.05], 26), {},
     {"rows": [0, 0, 0.03], "sink": 0.2, "mf": 0.0, "ckey": [[1.75, 9.0, 1.5], [-0.2, 8.25, 1.0], 60, 38], "crim": [[-1.4, 9.6, 1.7], [-0.2, 8.2, 1.0], 30, 30]})
shot("L40", "shop", M([-0.2, 9.5, 1.0], [-0.2, 8.25, 0.8], [-0.2, 8.75, 0.95], [-0.2, 8.25, 0.74], 30), {},
     {"rows": [0, 0, 0.03], "sink": 0.2, "mf": 0.0, "ckey": [[1.75, 9.0, 1.5], [-0.2, 8.25, 1.0], 60, 38], "crim": [[-1.4, 9.6, 1.7], [-0.2, 8.2, 1.0], 30, 30]})
shot("L41", "shop", C([0.25, 9.2, 2.0], [0.7, 10.35, 1.94], 40), {"len": at(*LEN_SINK, 180, expr="neutral", arms=[30, 30])}, {"rows": [0, 0, 1], "sink": 0.3})
shot("L42", "shop", C([1.8, 9.0, 1.45], [0.25, 9.1, 1.2], 22), {"len": at(*LEN_SINK, 180, expr="tired" if False else "neutral", arms=[30, 30], head=[0, 25])},
     {"rows": [0, 0, 0.9], "ckey": [[1.6, 8.3, 1.6], [-0.2, 8.0, 1.0], 60, 40]})
shot("L43", "shop", C([-0.4, 5.2, 1.5], [1.1, 2.6, 1.5], 30), {"me": at(1.1, 2.7, 180, expr="scared", head=[0, 0])}, {"rows": [0, 0, 1]})
shot("L44", "shop", front(1.1, 2.7, 180, 1.5, 0, 0.0, 36, push=0.1), {"me": at(1.1, 2.7, 180, expr="shut", head=[0, 0])}, {"rows": [0, 0, 1]})
shot("L45", "shop", C([0.25, 9.2, 2.0], [0.7, 10.35, 1.94], 40), {"len": at(*LEN_SINK, 180, expr="neutral", arms=[30, 30])}, {"rows": [0, 0, 1], "sink": 0.3})
shot("L45.2", "shop", C([0.7, 3.4, 1.6], [-0.2, 6.1, 0.9], 34), {}, {"rows": [0, 0, 1]})
shot("L46.1", "shop", C([1.5, 4.0, 1.7], [0.3, 10.2, 1.2], 22), {"len": at(*LEN_SINK, 180, expr="neutral", arms=[30, 30]), "me": at(1.1, 2.7, 180, expr="shut")},
     {"rows": [0, 0, 1]})
shot("L46.4", "shop", C([1.0, 2.0, 2.2], [1.1, 2.7, 1.93], 55), {"me": at(1.1, 2.7, 180, expr="shut")}, {"rows": [0, 0, 1], "inside": True}, step=1)
shot("L47", "shop", front(1.1, 2.7, 180, 1.4, 0, 0.0, 36), {"me": at(1.1, 2.7, 180, expr="neutral", head=[0, 0])}, {"rows": [0, 0, 1]})
shot("L48", "shop", C([1.5, 2.4, 1.6], [-0.1, 8.0, 1.2], 24), {"me": at(1.1, 2.7, 180, expr="neutral")}, {"rows": [0, 0, 1]})
shot("L48.2", "shop", C([0.9, 3.2, 1.25], [-0.4, 8.4, 1.0], 20), {"me": at(1.1, 2.7, 180, expr="neutral")}, {"rows": [0, 0, 1]})
shot("L49", "shop", C([0.8, 6.8, 1.45], [-0.2, 7.8, 1.0], 34), {}, {"rows": [0, 0, 1]})
shot("L49.3", "shop", C([-0.9, 7.0, 0.5], [-1.4, 8.4, 0.2], 28), {}, {"rows": [0, 0, 1], "no_props": True})
shot("L50", "shop", front(1.1, 2.9, 180, 1.5, 15, 0.0, 34), {"me": at(1.1, 2.9, 180, expr="neutral", head=[0, -10])}, {"rows": [0, 0, 1]})
shot("L51", "shop", C([0.5, 2.6, 1.5], [-0.2, 7.8, 1.2], 30),
     {"me": [at(1.0, 3.7, 180, expr="neutral", arms=[0, 0]), {"at": "L51.3-0.05", "pos": [1.0, 5.2], "yaw": 180}]}, {"rows": [0, 0, 1]}, step=1)
shot("L51.3", "shop", C([0.5, 2.6, 1.5], [-0.2, 7.8, 1.2], 30),
     {"me": [at(0.9, 5.7, 180, expr="neutral"), {"at": "L52-0.05", "pos": [0.8, 6.9], "yaw": 180}]}, {"rows": [0, 0, 1]}, step=1)

# ---- the turn and the warm end (S54 on)
shot("L52", "shop", C([1.0, 5.6, 1.45], [-0.2, 7.8, 1.0], 28), {"me": at(0.8, 6.8, 180)}, {"rows": [0, 0, 1]})
shot("L53", "shop", C([0.9, 9.3, 1.7], [-0.3, 7.8, 0.95], 34), {"me": at(0.8, 6.8, 180)},
     {"rows": [0, 0, 1], "ckey": [[1.6, 5.6, 1.9], [-0.3, 7.8, 0.9], 500, 55]})
shot("L54", "shop", C([0.6, 6.0, 1.55], [-0.2, 7.8, 1.3], 30), {"me": sitting(CHX, 7.8, -90, z=0.04, expr="neutral", arms=[30, 30])},
     {"rows": [0, 0, 1]})
shot("L55.3", "shop", front(CHX, 7.8, -90, 1.5, 15, 0.0, 36, push=0.1, face_z=FACE + 0.04),
     {"me": sitting(CHX, 7.8, -90, z=0.04, expr="soft", head=[0, 0], arms=[30, 30])}, {"rows": [0, 0, 1]})
shot("L56", "shop", front(CHX, 7.8, -90, 1.2, 18, 0.1, 40, face_z=FACE + 0.04),
     {"me": sitting(CHX, 7.8, -90, z=0.04, expr="soft", head=[0, 0], arms=[30, 30])}, {"rows": [0, 0, 1]})
shot("L56.4", "shop", C([0.2, 7.8, 2.6], [CHX, 7.8, 1.97], 60),
     {"me": sitting(CHX, 7.8, -90, z=0.04, expr="soft", arms=[30, 30])}, {"rows": [0, 0, 1]}, step=1)
shot("L57", "shop", C([0.6, 5.0, 1.5], [-1.6, 8.6, 1.5], 24),
     {"me": sitting(CHX, 7.8, -90, z=0.04, expr="soft", arms=[30, 30]), "len": at(*LEN_SINK, 180, expr="neutral", arms=[30, 30])},
     {"rows": [0, 0, 1]})
shot("L58", "shop", C([0.0, 9.1, 2.0], [0.7, 10.35, 1.94], 40), {"len": at(*LEN_SINK, 180, expr="neutral", arms=[30, 30])}, {"rows": [0.3, 0.5, 1], "sink": 0.4})
shot("L59", "shop", front(0.7, 10.35, 0, 1.6, 15, 0.0, 34), {"len": at(0.7, 10.35, 0, expr="wide", head=[0, 0])}, {"rows": [0.6, 0.8, 1], "inside": True})
shot("L59.3", "shop", front(0.7, 10.35, 0, 1.3, -10, 0.0, 40, push=0.12), {"len": at(0.7, 10.35, 0, expr="soft", head=[0, 0])},
     {"rows": [0.8, 1, 1]})
shot("L60", "shop", C([-0.3, 7.0, 1.55], [-1.2, 9.0, 1.3], 30), {"len": at(-1.0, 8.9, -90, expr="soft", arms=[40, 0])}, {"rows": [1, 1, 1], "k": 0.6})
shot("L61", "shop", front(CHX, 7.8, -90, 1.4, 20, 0.0, 36, face_z=FACE + 0.04),
     {"me": sitting(CHX, 7.8, -90, z=0.04, expr="soft", head=[0, 0], arms=[30, 30])}, {"rows": [1, 1, 1], "oxblood": True})
shot("L61.3", "shop", C([0.5, 7.0, 1.55], [-1.6, 8.0, 1.4], 28),
     {"me": sitting(CHX, 7.8, -90, z=0.04, expr="grin", head=[0, 0], arms=[30, 30]), "len": at(0.4, 7.8, -90, expr="soft", arms=[40, 10])},
     {"rows": [1, 1, 1], "oxblood": True})
shot("L62", "shop", C([0.9, 8.6, 1.5], [-1.89, 7.5, 1.3], 28),
     {"me": sitting(CHX, 7.8, -90, z=0.04, expr="soft", arms=[30, 30]), "len": at(0.4, 7.8, -90, expr="soft", arms=[30, 30])},
     {"rows": [1, 1, 1], "oxblood": True})
shot("L63", "shopday", C([0.9, 6.6, 1.5], [-1.89, 7.4, 1.3], 28),
     {"me": sitting(CHX, 7.8, -90, z=0.04, expr="soft", arms=[30, 30]), "sid": at(0.55, 6.1, -90, expr="grin", arms=[30, 30])},
     {"rows": [1, 1, 1], "hair_short": True})
shot("L63.4", "shopday", front(0.4, 6.1, -90, 1.5, 25, 0.0, 36), {"sid": at(0.55, 6.1, -90, expr="grin", head=[0, 0]),
                                                                  "len": at(0.55, 4.4, -90, expr="soft")}, {"rows": [1, 1, 1]})
shot("L64", "shopday", C([1.18, 2.6, 1.7], [1.25, 2.2, 2.1], 36), {}, {"rows": [1, 1, 1]})
shot("L64.3", "shopday", C([1.2, 10.4, 1.7], [-0.2, 5.0, 1.3], 22),
     {"len": at(0.55, 4.4, -90, expr="soft"), "sid": at(0.55, 6.1, -90, expr="grin"), "me": sitting(CHX, 7.8, -90, z=0.04, expr="soft")},
     {"rows": [1, 1, 1]})
shot("L65", "dusk", C([-0.7, -1.4, 1.5], [-0.1, 6.0, 1.3], 22),
     {"len": at(0.55, 4.4, -90, expr="soft"), "sid": at(0.55, 6.1, -90, expr="grin"), "me": sitting(CHX, 7.8, -90, z=0.04, expr="soft")},
     {"rows": [1, 1, 1]})
shot("L66", "shop", front(CHX, 7.8, -90, 1.5, 15, 0.0, 36, face_z=FACE + 0.04),
     {"me": sitting(CHX, 7.8, -90, z=0.04, expr="soft", head=[0, 0], arms=[30, 30])},
     {"rows": [1, 1, 1], "k": 0.6})

# ---------------------------------------------------------------------------------------------------- shots, scenes, looks
shots, scenes, shotlook, crowd_cfg = [], {}, {}, {}
for i, s in enumerate(SH):
    sid = f"S{i + 1:02d}"
    sp = {"id": sid, "cam": s["cam"], "step": s["opt"].get("step", 2)}
    if i:
        sp["at"] = s["at"]
    if "hand" in s["opt"]:
        sp["hand"] = s["opt"]["hand"]
    shots.append(sp)
    scenes[sid] = s["scene"]
    lk = dict(s["look"])
    shotlook[sid] = lk
SID = {s["at"]: f"S{i + 1:02d}" for i, s in enumerate(SH)}
IDX = {f"S{i + 1:02d}": i for i in range(len(SH))}

# ---------------------------------------------------------------------------------------------------- acting
DEFAULT = {"yaw": 0, "expr": "neutral", "head": [0, 0], "look": [0, 0], "arms": [0, 0], "side": [0, 0], "sit": False, "bend": 0,
           "tremble": 0}


def build_acting():
    acting = {who: [{"at": 0, "pos": [0, 40], "hidden": True}] for who in cast}
    last = {who: {"pos": [0, 40], "hidden": True} for who in cast}
    for i, s in enumerate(SH):
        ref = s["at"]
        for who in cast:
            spec = s["who"].get(who)
            ks = acting[who]
            if spec is None:
                if not last[who]["hidden"]:
                    ks.append({"at": ref, "hidden": True})
                    last[who] = {**last[who], "hidden": True}
                continue
            moves = spec if isinstance(spec, list) else [spec]
            first = moves[0]
            pos = list(first["pos"])
            pose = {**DEFAULT, **{k: v for k, v in first.items() if k != "pos"}}
            ks.append({"at": ref, "pos": last[who]["pos"], "hidden": False, **{k: pose[k] for k in ("yaw",)}})
            ks.append({"at": ref, "pos": pos, "hidden": False, "blend": 0.0,
                       **{k: pose[k] for k in ("yaw", "expr", "head", "look", "arms", "side", "sit", "bend", "tremble")}})
            for m in moves[1:]:
                ks.append({**m})
            last[who] = {"pos": list(moves[-1].get("pos", pos)), "hidden": False}
    return acting


acting = build_acting()
# the walks that happen inside a shot
acting["me"] += [{"at": "L13", "pos": [-1.2, 1.0]}, {"at": "L14-0.1", "pos": [1.4, 1.0], "yaw": 90},
                 {"at": "L29.4", "pos": [-0.3, 1.0], "yaw": 180, "keep_yaw": True},
                 {"at": "L29.4+0.6", "pos": [-0.3, 0.45], "yaw": 180, "keep_yaw": True, "head": [0, 0]},
                 {"at": "L43", "pos": [1.1, 2.7]}, {"at": "L43+0.5", "pos": [1.1, 2.45], "yaw": 180, "keep_yaw": True},
                 {"at": "L51", "pos": [1.0, 4.4]}, {"at": "L51.3", "pos": [0.8, 6.0]}, {"at": "L52", "pos": [0.8, 7.0]},
                 {"at": "L66", "pos": [CHX, 7.8, 0.04], "yaw": -90}]     # the walk keys come after the shots' own, so end on the chair
for k, a in enumerate(acting["me"]):
    pass


def settle(who):
    """Order an actor's keys by time (set.py and acting.py want them sorted by their resolved time, which they do themselves)."""
    return acting[who]


# ---------------------------------------------------------------------------------------------------- cues
cues = [
    {"at": 0, "name": "len_em", "to": 1.0, "dur": 0.05}, {"at": 0, "name": "len_th", "to": 1.0, "dur": 0.05},
    # Len's ring thins and dims, between scenes (each change lands on a cut) and then over 1.5 s at the scare
    {"at": "L12", "name": "len_em", "to": 0.78, "dur": 0.05}, {"at": "L12", "name": "len_th", "to": 0.75, "dur": 0.05},
    {"at": "L14", "name": "len_em", "to": 0.62, "dur": 0.05}, {"at": "L14", "name": "len_th", "to": 0.62, "dur": 0.05},
    {"at": "L21", "name": "len_em", "to": 0.46, "dur": 0.05}, {"at": "L21", "name": "len_th", "to": 0.5, "dur": 0.05},
    {"at": "L26", "name": "len_em", "to": 0.33, "dur": 0.05}, {"at": "L26", "name": "len_th", "to": 0.4, "dur": 0.05},
    {"at": "L32", "name": "len_em", "to": 0.27, "dur": 0.05}, {"at": "L32", "name": "len_th", "to": 0.34, "dur": 0.05},
    {"at": "L41", "name": "len_em", "to": 0.07, "dur": 1.5}, {"at": "L41", "name": "len_th", "to": 0.2, "dur": 1.5},
    {"at": "L58", "name": "len_em", "to": 1.0, "dur": 1.5}, {"at": "L58", "name": "len_th", "to": 1.0, "dur": 1.5},
    # my ring: violet fades up over 1.2 s and starts to ripple
    {"at": "L56+0.2", "name": "violet", "to": 1.0, "dur": 1.2},
    # Sid's ring wobbles when he grins
    {"at": "L63", "name": "wobble", "to": 1.0, "dur": 0.5},
    # the shop's three light rows: one at a time, each over 1.5 s (front, then middle), the back one left on
    {"at": "L31+0.6", "name": "row0", "to": 0.0, "dur": 1.5},
    {"at": "L31+1.9", "name": "row1", "to": 0.0, "dur": 1.5},
    {"at": "L58", "name": "row0", "to": 1.0, "dur": 1.5}, {"at": "L58", "name": "row1", "to": 1.0, "dur": 1.5},
    # the creature
    {"at": "L17.1", "name": "creature", "on": False},
    {"at": "L18", "name": "creature", "on": True, "where": "wait", "mouth": False},
    {"at": "L21", "name": "creature", "on": False},
    {"at": "L22", "name": "creature", "on": True, "where": "sid", "mouth": False},
    {"at": "L23", "name": "creature", "on": False},
    {"at": "L25", "name": "creature", "on": True, "where": "sid", "mouth": False},
    {"at": "L26", "name": "creature", "on": False},
    {"at": "L27", "name": "creature", "on": True, "where": "third", "mouth": False},
    {"at": "L30", "name": "creature", "on": False},
    {"at": "L35", "name": "creature", "on": True, "where": "third", "mouth": False},
    {"at": "L39", "name": "creature", "on": True, "where": "third", "mouth": True},
    {"at": "L52", "name": "creature", "on": False},
    # the third chair turns round (L37), and turns back for the empty chair (L52)
    {"at": "L37-0.15", "name": "swivel", "to": -90.0, "dur": 1.0},
    {"at": "L52", "name": "swivel", "to": 0.0, "dur": 0.05},
    {"at": "L52", "name": "cape", "on": True},
    {"at": "L54", "name": "cape", "on": False},
    # Len sweeps (S23 to S25)
    {"at": "L23", "name": "broom", "on": True}, {"at": "L26", "name": "broom", "on": False},
    # the front door opens as I come in; the bell rings twice in the film
    {"at": "L31", "name": "door", "to": 0.0, "dur": 0.05}, {"at": "L31+0.3", "name": "door", "to": -75.0, "dur": 0.7},
    {"at": "L31.3", "name": "door", "to": 0.0, "dur": 0.05},
    {"at": "L31+0.45", "name": "bell"}, {"at": "L64", "name": "bell"},
    {"at": "L62", "name": "hair", "short": False}, {"at": "L63", "name": "hair", "short": True},
]

# each shot's own look (light and show keys read by set.py): the rows of the shop and the creature's lights per shot
fx = []

# ---------------------------------------------------------------------------------------------------- sound
sfx = [
    {"at": "L31+0.3", "kind": "door", "db": -14, "dur": 0.8},
    {"at": "L31+0.45", "kind": "bell", "db": -20},
    {"at": "L64", "kind": "bell", "db": -18},
    {"at": "L31+0.6", "kind": "click", "db": -22}, {"at": "L31+0.6", "kind": "riser", "db": -34, "dur": 1.5},
    {"at": "L31+1.9", "kind": "click", "db": -22}, {"at": "L31+1.9", "kind": "riser", "db": -34, "dur": 1.5},
    {"at": "L58", "kind": "click", "db": -24}, {"at": "L58", "kind": "riser", "db": -34, "dur": 1.5},
    {"at": "L36", "kind": "hit", "db": -13}, {"at": "L39", "kind": "sting", "db": -10, "dur": 2.4},
    {"at": "L37-0.15", "kind": "creak", "db": -22, "dur": 0.9},
    {"at": "L41", "kind": "thud", "db": -24},
    {"at": "L52", "kind": "thud", "db": -26},
    {"at": "L54", "kind": "thud", "db": -26},
    {"at": "L56+0.2", "kind": "riser", "db": -30, "dur": 1.2},
]
for k in range(6):       # the broom's swish
    sfx.append({"at": f"L23+{0.35 + 0.5 * k:.2f}", "kind": "whoosh", "db": -30})
for k in range(4):
    sfx.append({"at": f"L25+{0.1 + 0.55 * k:.2f}", "kind": "whoosh", "db": -32})


def hum(note, frm, to, lufs, levels=None, fade_in=0.6, fade_out=0.6, pan=0.0):
    h = {"note": note, "from": frm, "to": to, "lufs": lufs, "fade_in": fade_in, "fade_out": fade_out, "pan": pan}
    if levels:
        h["levels"] = levels
    return h


hums = [
    # the street's big chord: many low steady tones that never move (fifths and a sixth, all in A minor), gone from the shop
    hum("B2", 0, "L16-0.2", -44, fade_in=1.5, pan=-0.4), hum("D3", 0, "L16-0.2", -44, fade_in=1.5, pan=0.4),
    hum("A3", 0.4, "L16-0.2", -45, fade_in=1.5, pan=-0.2), hum("E4", 0.8, "L16-0.2", -46, fade_in=1.5, pan=0.2),
    hum("G4", 1.2, "L16-0.2", -47, fade_in=1.5, pan=0.0),
    hum("B2", "L21-0.3", "L26", -44, pan=-0.4), hum("D3", "L21-0.3", "L26", -44, pan=0.4), hum("A3", "L21-0.3", "L26", -45, pan=-0.2),
    hum("E4", "L21-0.3", "L26", -46, pan=0.2),
    # Mr Ostrowski's very low tone
    hum("E2", "L05", "L06", -34, fade_in=0.3, fade_out=0.4),
    # Len's A2 sinks with his ring, and comes back up at L58
    hum("A2", "L11", "end", -33, [["L11", 0], ["L12", -1], ["L14", -3], ["L21", -8], ["L26", -11], ["L32", -14], ["L41", -15],
                                   ["L41+1.5", -24], ["L46", -22], ["L57", -18], ["L58", -16], ["L58+1.5", 0], ["L64", 0]],
        fade_in=1.0, fade_out=1.8, pan=-0.25),
    # Sid's E3 on Tuesdays, and at the end
    hum("E3", "L15", "L17>+0.9", -37, fade_in=0.6, pan=0.25),
    hum("E3", "L63-0.3", "end", -33, fade_in=0.8, fade_out=1.8, pan=0.25),
    # Plant 1 (L16 to L17): all three tones sound together, at a level that is plainly heard
    hum("A2", "L16", "L17>+0.9", -28, fade_in=0.3, fade_out=0.6, pan=-0.25),
    hum("E3", "L16", "L17>+0.9", -28, fade_in=0.3, fade_out=0.6, pan=0.25),
    hum("C#4", "L16", "L17>+0.9", -28, fade_in=0.3, fade_out=0.6, pan=0.0),
    # my note, from the third chair: heard again at L34 and never as a tune, only louder as I come
    hum("C#4", "L34", "end", -31, [["L34", -12], ["L36", -5], ["L40", -4], ["L41", -9], ["L44", -3], ["L46", 0], ["L50", -3], ["L51", -7],
                                    ["L52", 2], ["L56", 0], ["L63", -2], ["L64", -2]], fade_in=0.5, fade_out=1.8),
]

story = {
    "slug": "ep42-barber-chair",
    "title": "In this town, everyone hums a note of their own",
    "made_for_kids": False,
    "premise": "In a town where everyone hums one note of their own, with a small coloured ring over every head that ripples with it, the narrator's ring is clear and silent. Their stepdad Len, a barber, has a deep amber note that fades a little more each evening, while a headless customer under a striped cape, its face drawn large on its chest, sits one chair nearer to the third barber chair Len kept for them.",
    "twist": "The narrator's note was never missing: it was in the third chair of the shop built for three, the chair Len swept every night. Sitting in it lights their ring violet on top of Len's note, the chord the first line only hinted at, and the last line says it was waiting there.",
    "world": "A frosted small-town high street in deep winter, brick shopfronts with blank painted fascias, iron lamp posts, a plain cream and maroon double-deck bus, and a narrow three-chair barbershop with a black and white checker floor, sage tiles, a long mirror, oxblood chairs and a brass sink lamp.",
    "key_color": "#c08cff",
    "gap": 0.12,
    "tail": 0.3,
    "look": {"fog": "#2b3550", "fog_density": 0.012, "fog_start": 12.0, "sky": "#10141c", "sky_strength": 1.0, "exposure": 0.0, "flash_safe": True},
    "grade": {"shadows": [0.0, 0.0, 0.05], "highlights": [0.04, 0.012, -0.03], "saturation": 1.05, "contrast": 1.06, "vignette": 0.36,
              "bloom": 0.4, "grain": 0.012, "red_line": 0.74, "red_lift_blue": 0.5},
    "shot_grades": {**{SID[r]: {"shadows": [0.06, 0.02, -0.04], "highlights": [0.08, 0.04, -0.06], "saturation": 1.18, "exposure": 1.0,
                                "vignette": 0.22, "bloom": 0.3} for r in ("L24", "L24.5")},
                    **{SID[r]: {"shadows": [0.0, 0.0, 0.05], "highlights": [0.04, 0.012, -0.03], "saturation": 1.05, "contrast": 1.06,
                                "vignette": 0.36, "bloom": 0.15, "grain": 0.012, "red_line": 0.74, "red_lift_blue": 0.5}
                       for r in ("L41", "L45", "L58")},
                    # fix round 2 (exposure only): the white shop and the close-ups were clipping
                    **{f"S{n}": {"exposure": 0.55, "bloom": 0.08} for n in (73, 74, 76, 77, 78, 79, 80)},
                    **{f"S{n}": {"bloom": 0.1} for n in (70, 71, 84)}},
    "phonemes": {"Ostrov": "ˈɑstɹɔv"},
    "cast": cast,
    "lines": lines,
    "shots": shots,
    "scenes": scenes,
    "shotlook": shotlook,
    "acting": acting,
    "cues": cues,
    "fx": fx,
    "music": {"root": 57, "mode": "minor", "bpm": 76, "seed": 42,
              "sections": [
                  {"at": 0, "voices": ["pad"], "energy": 0.3},
                  {"at": "L08", "voices": ["drone", "pad"], "energy": 0.35},
                  {"at": "L16", "voices": ["drone", "pad"], "energy": 0.4},
                  {"at": "L22", "voices": ["drone", "pad", "pulse"], "energy": 0.45},
                  {"at": "L30", "voices": ["drone", "pad"], "energy": 0.3},
                  {"at": "L36", "voices": ["drone", "choir", "pulse"], "energy": 0.6},
                  {"at": "L41", "voices": ["drone", "pad"], "energy": 0.4},
                  {"at": "L47", "voices": ["drone", "pad", "choir"], "energy": 0.45},
                  {"at": "L55", "voices": ["pad"], "energy": 0.4, "mode": "major"},
                  {"at": "L57", "voices": ["pad", "piano"], "energy": 0.5, "mode": "major"},
              ]},
    "sound": {"floor": "stone", "steps_db": -22,
              "ambience": [
                  {"kind": "wind", "from": 0, "to": "L16", "lufs": -44},
                  {"kind": "room", "from": 0, "to": "end", "lufs": -42},
                  {"kind": "water", "from": "L32", "to": "L43", "lufs": -34},
              ],
              "hums": hums,
              "sfx": sfx,
              "music_drops": [
                  {"from": "L35>", "to": "L36", "keep": ["hit"]},
                  {"from": "L38>", "to": "L39", "keep": ["sting"]},
              ]},
}
OUT.write_text(json.dumps(story, indent=1, ensure_ascii=False) + "\n")
print("wrote", OUT, f"({len(shots)} shots)")
