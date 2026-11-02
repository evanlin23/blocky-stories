"""Writes ../story.json for ep22 "The little man in the model village moves one window a day".

Run from anywhere: python stories/ep22-model-village/generator/make_story.py
The words are in lines.json next to this file. Everything else is here: the cast, the shots and their cameras,
the acting, the cues set.py reads, the score and the sound. The places are set.py's metres.
"""
import importlib.util
import json
import math
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE.parent / "story.json"
lines = json.loads((HERE / "lines.json").read_text())
_sp = importlib.util.spec_from_file_location("ep22_layout", HERE.parent / "layout.py")
LAY = importlib.util.module_from_spec(_sp)
_sp.loader.exec_module(LAY)

cast = {
    "me": {"age": "adult", "skin": "#e2b48a", "shirt": "#4f6e4b", "pattern": "solid", "collar": "#3f5a3d",
           "pants": "#6b6e72", "shoes": "#2b2a2c", "sleeves": "long", "hair": "cap", "hair_c": "#5b3b27",
           "hat": "none", "extras": ["coat"], "face": {"eyes": "round", "brows": True, "ink": "#1d1416", "bags": True}},
    "maggie": {"age": "adult", "skin": "#e6bd98", "shirt": "#27355c", "pattern": "stripes", "pattern_c": "#e8e6e0",
               "pants": "#4a4a52", "shoes": "#2e2a28", "sleeves": "long", "hair": "bun", "hair_c": "#b9b9bd",
               "hat": "none", "height": 0.94, "face": {"eyes": "round", "brows": True, "ink": "#1d1416", "cheeks": "#e59a8e"}},
    "t1": {"age": "adult", "skin": "#d9a77c", "shirt": "#cfc6b0", "pattern": "knit", "pattern_c": "#b4aa94",
           "pants": "#2c3345", "shoes": "#222222", "sleeves": "long", "hair": "buzz", "hair_c": "#7a7a7a",
           "hat": "none", "width": 1.08, "face": {"eyes": "dot", "brows": True, "ink": "#1d1416"}},
    "t2": {"age": "adult", "skin": "#c68e64", "shirt": "#2d2f36", "pattern": "solid", "collar": "#24262c",
           "pants": "#24262c", "shoes": "#1c1c1e", "sleeves": "long", "hair": "cap", "hair_c": "#1e1a18",
           "hat": "none", "height": 1.04, "extras": ["coat"], "face": {"eyes": "round", "brows": True, "ink": "#1d1416"}},
    "t3": {"age": "adult", "skin": "#eac3a0", "shirt": "#f1e24f", "pattern": "solid", "collar": "#d9c93e",
           "pants": "#3b4a63", "shoes": "#5a2f2a", "sleeves": "long", "hair": "long", "hair_c": "#8a4a2a",
           "hat": "none", "height": 0.93, "extras": ["coat"], "face": {"eyes": "lashes", "brows": True, "ink": "#1d1416"}},
    "t4": {"age": "adult", "skin": "#dcb28a", "shirt": "#6c5b4a", "pattern": "plaid", "pattern_c": "#40382e",
           "pants": "#3a3a3a", "shoes": "#2a2220", "sleeves": "long", "hair": "none", "hair_c": "#999999",
           "hat": "ballcap", "hat_c": "#3a4a5a", "height": 0.97, "face": {"eyes": "tired", "brows": True, "ink": "#1d1416"}},
    "t5": {"age": "adult", "skin": "#b98260", "shirt": "#7a3f55", "pattern": "knit", "pattern_c": "#5f2f42",
           "pants": "#2a2c34", "shoes": "#222222", "sleeves": "long", "hair": "swoop", "hair_c": "#2a1d15",
           "hat": "none", "height": 0.96, "face": {"eyes": "round", "brows": True, "ink": "#1d1416"}},
    "resident": {"age": "adult", "skin": "#e8b98f", "shirt": "#1f2e52", "pattern": "solid", "collar": "#1a2644",
                 "pants": "#1e2230", "shoes": "#14161c", "sleeves": "long", "hair": "cap", "hair_c": "#2b1d14",
                 "hat": "none", "height": 0.0257, "extras": ["coat", "scarf"], "extra_c": "#cc9a1c",
                 "face": {"eyes": "round", "brows": False, "mouth": "line", "ink": "#120d0e", "pupil": "#0a0708"}},
}

# ---------------------------------------------------------------------------------------------- holds
# the voice runs 2:11, so the picture breathes: holds go on the gaps after the lines that earn them, never in words
HOLDS = {"L09": 0.25, "L10": 0.3, "L12": 0.3, "L16": 0.3, "L17": 1.1, "L31": 0.4, "L34": 0.5, "L40": 0.3, "L44": 0.6,
         "L46": 0.2, "L48": 0.4, "L52": 0.6, "L55": 0.5, "L56": 0.4, "L62": 0.3, "L63": 0.3, "L66": 0.3, "L68": 0.5}
for ln in lines:
    if ln["id"] in HOLDS:
        ln["gap"] = HOLDS[ln["id"]]
lines = lines + [{"id": "P02", "pause": 0.4, "chunks": []}]    # the loop cut comes 0.4 s after "me", the closing sound under it

R = LAY.room
TX, CX = LAY.TX, LAY.CX
D = math.degrees


def cam(*keys):
    """Camera keys: each (u, loc, target, lens)."""
    return [[u, list(l), list(t), ln] for u, l, t, ln in keys]


def still(loc, tgt, lens):
    return cam((0, loc, tgt, lens))


def move(a, b, lens_a, lens_b=None):
    return cam((0, a[0], a[1], lens_a), (1, b[0], b[1], lens_b or lens_a))


def win(name, dist, lens=50, dx=0.0, dz=0.0, tx=0.0, tz=0.0):
    """Outside a model window, `dist` metres out, looking in (+y)."""
    r = R(name)
    return ([r["win_x"] + dx, r["front_y"] - dist, r["win_z"] + dz], [r["win_x"] + tx, r["front_y"] + 0.05, r["win_z"] + tz])


def inside(name, back, lens=24, dx=0.0, dz=0.0, tx=0.0, tz=0.0, far=1.0):
    """Inside a model room `back` metres behind the glass, looking out (-y)."""
    r = R(name)
    return ([r["win_x"] + dx, r["front_y"] + LAY.WALL + back, r["win_z"] + dz], [r["win_x"] + tx, r["front_y"] - far, r["win_z"] + tz])


def bend(room, gap=0.08, a=62, dx=0.0, dz=0.0, fz=0.015, comp=True, **extra):
    """Me (or anyone) leaning over the model with the face `gap` m from a window: feet back and low (sunk, so
    the legs are under the ground and it reads as kneeling), body a plank at `a` degrees, head pitched level."""
    r = R(room)
    ha = math.radians(a)
    head_y = r["front_y"] - gap - 0.21
    zh = r["win_z"] + fz
    d = dict(pos=[round(r["win_x"] + dx, 3), round(head_y - 1.57 * math.sin(ha), 3), round(zh - 1.57 * math.cos(ha), 3)],
             yaw=180, lean=a, head=[0, -a if comp else 0])
    d.update(extra)
    return d


def face_pt(room, gap, a=62, dx=0.0, fz=0.015):
    r = R(room)
    return [r["win_x"] + dx, r["front_y"] - gap - 0.1, r["win_z"] + fz]


def dofp(room, dy=0.0, dz=0.0, dx=0.0):
    r = R(room)
    return [r["win_x"] + dx, r["front_y"] + dy, r["win_z"] + dz]


# ---------------------------------------------------------------------------------------------- the Resident's rooms
RES = {k: LAY.stand(k, dx=(0.02 if k == "tea" else 0.0)) for k in ("bakery", "blue", "chapel", "next", "tea")}
FLOOR = {k: R(k)["floor_z"] for k in RES}

acting = {k: [] for k in cast}
last = {}


def key(who, at, **kw):
    acting[who].append({"at": at, **kw})


def put(who, at, pos, **kw):
    """Appear at `pos` at `at` (a jump: a hold key a hair before, so nothing slides across the set)."""
    if who in last:
        acting[who].append({"at": f"{at}-0.02", "pos": list(last[who])})
    acting[who].append({"at": at, "pos": list(pos), "blend": 0, "hidden": False, **kw})
    last[who] = list(pos)


def walk(who, at, pos, **kw):
    acting[who].append({"at": at, "pos": list(pos), **kw})
    last[who] = list(pos)


def gone(who, at):
    if who in last:
        acting[who].append({"at": f"{at}-0.02", "pos": list(last[who])})
    acting[who].append({"at": at, "pos": list(last.get(who, [0, 0, 0])), "hidden": True, "blend": 0})


for who in cast:
    acting[who].append({"at": 0, "pos": [0, -30, 0], "hidden": True, "yaw": 0, "lean": 0, "head": [0, 0], "arms": [0, 0],
                        "side": [0, 0], "expr": "neutral", "blend": 0})
    last[who] = [0, -30, 0]


def res(at, room, face="away", **kw):
    """The Resident in `room` at `at`: back to the glass (facing in), or facing the glass (a reverse angle)."""
    x, y, z = RES[room]
    if face == "away":
        put("resident", at, [x, y, z], yaw=180, head=[0, 0], hidden=False, expr="blank", **kw)
    elif face == "glass":
        put("resident", at, [x - 0.02, y, z], yaw=0, head=[0, 0], hidden=False, expr="blank", **kw)
    elif face == "turned":
        put("resident", at, [x, y, z], yaw=180, head=[172, 9], hidden=False, expr="blank", **kw)
    elif face == "profile":
        put("resident", at, [x, y, z], yaw=180, head=[78, 0], hidden=False, expr="blank", **kw)


# ---------------------------------------------------------------------------------------------- shots
shots = []


def shot(sid, at, cams, step=2, dof=None, hand=0.006, **kw):
    s = {"id": sid, "cam": cams, "step": step, "hand": hand}
    if at is not None:
        s["at"] = at
    if dof:
        s["dof"] = dof
    s.update(kw)
    shots.append(s)


BAK, BLU, CHA, NEX, COT, TEA = (R(k) for k in ("bakery", "blue", "chapel", "next", "cottage", "tea"))
BAKFOC = [RES["bakery"][0], RES["bakery"][1] - 0.007, FLOOR["bakery"] + 0.032]
BLUFOC = [RES["blue"][0], RES["blue"][1] - 0.007, FLOOR["blue"] + 0.032]
CHAFOC = [RES["chapel"][0], RES["chapel"][1] - 0.007, FLOOR["chapel"] + 0.032]
NEXFOC = [RES["next"][0], RES["next"][1] - 0.007, FLOOR["next"] + 0.032]
TEAFOC = [RES["tea"][0], RES["tea"][1] - 0.007, FLOOR["tea"] + 0.032]


def mac(room, d0, d1=None, lens=55, tz=-0.012, dx=0.0, tx=0.0):
    a = win(room, d0, dx=dx, tz=tz, tx=tx)
    b = win(room, d1 if d1 else d0, dx=dx, tz=tz, tx=tx)
    return cam((0, a[0], a[1], lens), (1, b[0], b[1], lens))


# 01 the sight, L01 to L17
shot("S01", None, mac("bakery", 0.14, 0.105), dof=[2.8, BAKFOC])
shot("S02", "L01.3", cam((0, [1.2, -0.9, 0.62], [2.0, 0.5, 0.42], 32), (1, [0.1, -3.2, 1.35], [1.9, -0.1, 0.62], 28)), hand=0.01)
shot("S03", "L03", cam((0, [-2.8, 0.22, 0.36], [3.0, 0.5, 0.40], 22), (1, [-2.5, 0.22, 0.36], [3.2, 0.5, 0.42], 22)), hand=0.004)
shot("S04", "L04", cam((0, [1.3, 1.0, 0.95], [-1.4, -2.3, 1.0], 30), (1, [1.3, 1.0, 0.95], [-1.1, -2.0, 1.0], 30)))
shot("S05", "L05", still([0.6, 1.0, 1.3], [0.5, -2.3, 1.1], 24))
shot("S06", "L06", cam((0, [0.1, -1.9, 1.2], [0.6, 0.5, 0.35], 40), (1, [0.3, -1.9, 1.15], [0.7, 0.5, 0.35], 40)))
shot("S07", "L07", cam((0, [1.4, -1.5, 0.75], [6.0, 0.0, 0.3], 28), (1, [1.9, -1.5, 0.75], [6.0, 0.4, 0.3], 28)), hand=0.004)
shot("S08", "L08", cam((0, [0.0, -2.0, 2.8], [0.0, 2.6, 0.3], 17), (1, [0.0, -1.7, 2.6], [0.0, 2.6, 0.3], 17)), hand=0.004)
shot("S09", "L09", still([-1.0, 1.36, 0.325], [-0.95, 1.58, 0.318], 55), dof=[3.0, [-0.95, 1.575, 0.31]])
shot("S10", "L10", mac("bakery", 0.19, 0.17, lens=45, tz=0.0), dof=[4.0, BAKFOC])
shot("S11", "L11", mac("bakery", 0.16, 0.15, lens=45, tz=0.0))
shot("S12", "L12", mac("bakery", 0.11, 0.09, lens=50, tz=0.0, dx=-0.01))
shot("S13", "L13", mac("bakery", 0.1, 0.085, lens=65, tz=-0.012, dx=-0.04, tx=0.0), dof=[2.2, [BAKFOC[0], BAKFOC[1], BAKFOC[2] + 0.008]])
shot("S14", "L14", cam((0, [2.9, -0.6, 0.62], [1.7, 0.2, 0.42], 34), (1, [2.7, -0.6, 0.6], [1.7, 0.2, 0.42], 34)))
shot("S15", "L15", still([R("bakery")["win_x"] + 1.1, R("bakery")["front_y"] - 0.5, R("bakery")["win_z"] + 0.12],
                         face_pt("bakery", 0.06), 40))
shot("S16", "L16", mac("bakery", 0.12, 0.09, lens=65), dof=[2.4, BAKFOC])
shot("S17", "L17.1", cam((0, [-1.7, -0.7, 0.5], [-2.0, 0.3, 0.16], 30), (1, [-1.9, -0.7, 0.5], [-2.0, 0.3, 0.16], 30)), hand=0.003)
# 02 the blue door, L18 to L23
shot("S18", "L18", mac("bakery", 0.17, 0.16, lens=45, tz=0.0))
shot("S19", "L19", cam((0, [0.7, 1.12, 0.62], [1.45, 1.92, 0.5], 36), (1, [0.9, 1.2, 0.58], [1.45, 1.92, 0.5], 36)))
shot("S20", "L20", mac("blue", 0.12, 0.09, lens=65), dof=[2.4, BLUFOC])
shot("S21", "L21", still([R("blue")["win_x"] + 1.1, R("blue")["front_y"] - 0.5, R("blue")["win_z"] + 0.1], face_pt("blue", 0.06), 40))
cup = [R("blue")["win_x"] - 0.03, R("blue")["front_y"] + 0.16, R("blue")["floor_z"] + 0.0345]
shot("S22", "L22", cam((0, [R("blue")["win_x"] + 0.02, R("blue")["front_y"] - 0.11, R("blue")["win_z"] + 0.012], cup, 55),
                       (1, [R("blue")["win_x"] + 0.01, R("blue")["front_y"] - 0.08, R("blue")["win_z"] + 0.006], cup, 60)),
     dof=[6.0, cup], hand=0.002)
shot("S23", "L23", cam((0, [cup[0] - 0.012, R("blue")["front_y"] - 0.02, cup[2] + 0.02], cup, 80),
                       (1, [cup[0] - 0.01, R("blue")["front_y"] - 0.02, cup[2] + 0.012], cup, 85)), dof=[5.0, cup], hand=0.001)
# 03 the chapel, L24 to L31
shot("S24", "L24", cam((0, [0.0, 3.4, 9.0], [0.0, 3.45, 0.3], 22), (1, [0.0, 3.4, 8.0], [0.0, 3.45, 0.3], 22)), hand=0.0)
shot("S25", "L25", mac("chapel", 0.12, 0.09, lens=65), dof=[2.4, CHAFOC])
shot("S26", "L26", cam((0, [0.4, 3.0, 0.95], [-1.4, 5.6, 0.55], 26), (1, [0.1, 3.4, 0.9], [-1.6, 5.8, 0.58], 26)))
shot("S27", "L27", cam((0, [-1.45, 5.15, 0.85], [-1.95, 5.82, 0.6], 34), (1, [-1.6, 5.3, 0.78], [-1.95, 5.82, 0.6], 34)))
shot("S28a", "L28", cam((0, [-1.9, 5.2, 0.5], [-1.95, 5.9, 0.82], 40), (1, [-1.9, 5.2, 0.55], [-1.95, 5.9, 0.86], 40)))
shot("S28b", "L28.1", cam((0, [-2.1, 5.4, 0.45], [-2.09, 5.82, 0.43], 50), (1, [-2.1, 5.35, 0.45], [-2.09, 5.82, 0.43], 50)), dof=[3.0, [-2.09, 5.82, 0.45]])
shot("S28c", "L28.2", mac("cottage", 0.14, 0.11, lens=55, tz=0.0), dof=[3.0, dofp("cottage", 0.02)])
shot("S29", "L29", cam((0, [-0.3, 1.0, 2.0], [-0.3, 4.6, 0.4], 28), (1, [-0.5, 2.2, 1.8], [-0.8, 5.0, 0.4], 28)))
shot("S30", "L30", still([R("chapel")["win_x"] + 1.1, R("chapel")["front_y"] - 0.5, R("chapel")["win_z"] + 0.1], face_pt("chapel", 0.01), 40))
shot("S31", "L31", mac("chapel", 0.1, 0.085, lens=70), dof=[2.2, CHAFOC])
# 04 next door, L32 to L34
shot("S32a", "L32", cam((0, [-1.55, 4.55, 0.95], [-1.55, 5.82, 0.62], 24), (1, [-1.55, 4.9, 0.8], [-1.55, 5.82, 0.62], 24)))
shot("S32b", "L32.3", mac("next", 0.12, 0.09, lens=65), dof=[2.4, NEXFOC])
shot("S33", "L33", cam((0, [CX - 0.4, -2.3, 1.5], [CX + 2.0, 0.2, 1.3], 26), (1, [CX - 0.2, -2.3, 1.5], [CX + 2.0, 0.2, 1.3], 26)))
shot("S34", "L34", cam((0, [CX - 1.3, -1.9, 1.5], [CX - 1.7, -0.9, 0.65], 30), (1, [CX - 1.5, -1.6, 1.5], [CX - 1.7, -0.9, 0.65], 30)))
# 05 the scare, L35 to L48
shot("S35", "L35", mac("cottage", 0.16, 0.13, lens=45, tz=0.0))
shot("S36", "L36", mac("cottage", 0.1, 0.085, lens=60, tz=0.0))
shot("S37", "L37", mac("next", 0.12, 0.09, lens=55, tz=0.0))
shot("S38a", "L38", cam((0, [-0.9, 5.0, 0.85], [0.15, 7.0, 0.72], 26), (1, [-0.6, 5.5, 0.85], [0.2, 7.1, 0.74], 26)))
shot("S38b", "L38.1", cam((0, [0.9, 5.4, 0.75], [0.4, 6.0, 0.75], 40), (1, [0.8, 5.9, 0.78], [0.4, 6.55, 0.78], 40)))
shot("S39", "L39", cam((0, [0.2, 6.15, 0.98], [0.3, 7.3, 0.82], 30), (1, [0.2, 6.35, 0.92], [0.3, 7.3, 0.82], 30)))
shot("S40", "L40", cam((0, [TEA["win_x"], TEA["front_y"] - 0.13, TEA["win_z"] + 0.07], [TEA["win_x"] - 0.02, TEA["front_y"] + 0.3, TEA["floor_z"] + 0.02], 40),
                       (1, [TEA["win_x"], TEA["front_y"] - 0.1, TEA["win_z"] + 0.06], [TEA["win_x"] - 0.02, TEA["front_y"] + 0.3, TEA["floor_z"] + 0.02], 40)),
     dof=[9.0, [TEA["win_x"] - 0.02, TEA["front_y"] + 0.28, TEA["floor_z"] + 0.03]])
shot("S41", "L41", still([R("tea")["win_x"] + 1.1, R("tea")["front_y"] - 0.55, R("tea")["win_z"] + 0.1], face_pt("tea", 0.05), 40))
shot("S42", "L42", cam((0, *[x for x in win("tea", 0.12, dx=0.0, tz=-0.021, tx=0.02)][:2], 60), (1, *[x for x in win("tea", 0.105, dx=0.0, tz=-0.021, tx=0.02)][:2], 62)),
     dof=[2.8, [TEAFOC[0], TEAFOC[1] - 0.0004, TEAFOC[2] + 0.008]], hand=0.0)
shot("S43", "L43", mac("tea", 0.17, 0.15, lens=45, tz=-0.012, tx=0.02), dof=[3.5, TEAFOC])
shot("S44", "L44", mac("tea", 0.20, 0.145, lens=45, tz=-0.012, tx=0.02), dof=[3.0, [TEAFOC[0], TEAFOC[1] - 0.0004, TEAFOC[2] + 0.008]], hand=0.002)
shot("S45", "L45", cam((0, [2.4, 6.72, 0.98], [1.2, 6.66, 0.8], 30), (1, [2.4, 6.72, 0.98], [1.5, 6.66, 0.78], 30)))
shot("S46", "L46", still([-0.6, 0.3, 1.62], [-0.6, -1.2, 1.57], 42), hand=0.004)
shot("S47", "L47", cam((0, [0.0, -2.0, 2.8], [0.0, 2.6, 0.3], 17), (1, [0.0, -0.4, 2.0], [0.0, 2.8, 0.3], 18)), hand=0.004)
shot("S48", "L48", cam((0, [-0.3, 2.55, 0.46], [-0.1, 4.4, 0.46], 22), (1, [0.1, 2.57, 0.44], [0.0, 4.4, 0.46], 22)), hand=0.003)
# 06 the turn, L49 to L55
shot("S49", "L49", cam((0, *inside("bakery", 0.17, lens=26, dx=0.02, dz=0.004)[:2], 26), (1, *inside("bakery", 0.16, lens=26, dx=0.02, dz=0.004)[:2], 26)),
     dof=[11.0, [BAK["win_x"], BAK["front_y"] - 0.5, BAK["win_z"]]], hand=0.002)
shot("S50", "L50", cam((0, *inside("bakery", 0.14, dx=0.016, dz=0.006)[:2], 24), (1, *inside("bakery", 0.125, dx=0.016, dz=0.006)[:2], 24)),
     dof=[2.2, [BAK["win_x"], BAK["front_y"] - 0.42, BAK["win_z"] + 0.0]], hand=0.0015)
shot("S51", "L51", cam((0, *inside("bakery", 0.125, dx=0.016, dz=0.006)[:2], 24), (1, *inside("bakery", 0.115, dx=0.016, dz=0.006)[:2], 24)),
     dof=[2.2, [BAK["win_x"], BAK["front_y"] - 0.42, BAK["win_z"]]], hand=0.0015)
shot("S52", "L52", cam((0, *inside("bakery", 0.14, dx=0.016, dz=0.006)[:2], 24), (1, *inside("bakery", 0.115, dx=0.016, dz=0.006)[:2], 26)),
     dof=[2.2, [BAK["win_x"], BAK["front_y"] - 0.42, BAK["win_z"]]], hand=0.001)
shot("S53a", "L53", cam((0, *inside("blue", 0.14, dx=0.016, dz=0.006)[:2], 24)), dof=[2.2, [BLU["win_x"], BLU["front_y"] - 0.42, BLU["win_z"]]], hand=0.0015)
shot("S53b", "L53.1", cam((0, *inside("chapel", 0.14, dx=0.016, dz=0.006)[:2], 24)), dof=[2.2, [CHA["win_x"], CHA["front_y"] - 0.42, CHA["win_z"]]], hand=0.0015)
shot("S53c", "L53.2", mac("bakery", 0.15, 0.13, lens=45, tz=0.0))
shot("S54a", "L54", cam((0, [2.3, 0.1, 0.95], [1.4, 1.9, 0.4], 28), (1, [0.4, 4.8, 1.0], [0.3, 6.8, 0.7], 28)), hand=0.004)
shot("S54b", "L54.2", mac("tea", 0.15, 0.12, lens=45, tz=-0.008, tx=0.02), dof=[3.2, TEAFOC])
shot("S55", "L55", cam((0, [0.3, 0.4, 0.75], [0.3, -1.6, 0.85], 34), (1, [0.3, 0.2, 0.75], [0.3, -1.6, 0.9], 34)), hand=0.004)
# 07 the town, L56 to L69
shot("S56", "L56", cam((0, [0.3, 0.5, 1.2], [0.3, -3.4, 1.0], 30), (1, [0.3, 0.5, 1.2], [0.3, -4.5, 1.0], 30)), hand=0.004)
shot("S57", "L57", cam((0, [TX + 1.4, -9.5, 1.5], [TX, -2.6, 1.3], 28), (1, [TX + 0.6, -6.5, 1.5], [TX, -2.4, 1.3], 28)), hand=0.004)
shot("S58", "L58", cam((0, [TX - 0.35, -2.5, 1.5], [TX, 0.8, 1.35], 26), (1, [TX - 0.25, -2.4, 1.5], [TX, 0.8, 1.35], 26)), hand=0.004)
shot("S59", "L59", cam((0, [TX - 0.3, -2.7, 1.5], [TX + 0.4, 0.8, 1.2], 30), (1, [TX - 0.2, -2.5, 1.5], [TX + 0.25, -0.4, 1.2], 32)), hand=0.004)
shot("S60", "L60", cam((0, [TX - 0.55, -2.9, 1.5], [TX + 0.2, -1.4, 1.52], 38), (1, [TX - 0.45, -2.7, 1.5], [TX + 0.2, -1.4, 1.52], 40)), hand=0.004)
shot("S61", "L61", cam((0, [TX + 0.9, -2.8, 1.52], [TX + 0.2, -1.4, 1.52], 40), (1, [TX + 0.8, -2.6, 1.52], [TX + 0.2, -1.4, 1.52], 42)), hand=0.004)
shot("S62", "L62", cam((0, [TX - 2.5, -1.8, 1.25], [TX - 2.45, -1.0, 0.8], 42), (1, [TX - 2.5, -1.7, 1.15], [TX - 2.45, -1.0, 0.8], 44)), dof=[6.0, [TX - 2.45, -1.0, 0.82]], hand=0.002)
shot("S63a", "L63", cam((0, [CX + 1.7, -0.3, 1.45], [CX + 0.6, 1.8, 1.2], 32), (1, [CX + 1.5, -0.2, 1.4], [CX + 0.6, 1.8, 1.2], 32)), hand=0.004)
shot("S63b", "L63.2", cam((0, [CX + 0.6, 1.05, 0.9], [CX + 0.6, 1.45, 0.8], 58), (1, [CX + 0.6, 1.08, 0.89], [CX + 0.6, 1.45, 0.8], 60)), dof=[2.2, [CX + 0.6, 1.45, 0.8]], hand=0.0015)
shot("S64", "L64", cam((0, [0.2, 1.3, 0.5], [0.2, -1.05, 0.42], 22), (1, [0.2, 1.1, 0.5], [0.2, -1.05, 0.42], 22)), hand=0.004)
shot("S65", "L65", cam((0, [0.2, 6.65, 1.4], [0.35, 7.45, 0.74], 28), (1, [0.35, 6.8, 1.3], [0.35, 7.45, 0.74], 30)), hand=0.002)
shot("S66a", "L66", mac("tea", 0.13, 0.11, lens=50, tz=-0.012, tx=-0.01), dof=[3.2, [TEA["win_x"] - 0.02, TEA["front_y"] + 0.07, TEA["floor_z"] + 0.02]])
shot("S66b", "L66.3", mac("tea", 0.13, 0.11, lens=50, tz=-0.012, tx=-0.01), dof=[3.2, [TEA["win_x"] - 0.02, TEA["front_y"] + 0.07, TEA["floor_z"] + 0.02]])
shot("S67", "L67", cam((0, [TEA["win_x"] - 0.045, TEA["front_y"] + 0.075, TEA["win_z"] + 0.004], [TEA["win_x"] + 0.0, TEA["front_y"] - 1.0, TEA["win_z"] + 0.008], 22),
                       (1, [TEA["win_x"] - 0.043, TEA["front_y"] + 0.073, TEA["win_z"] + 0.004], [TEA["win_x"] + 0.0, TEA["front_y"] - 1.0, TEA["win_z"] + 0.008], 22)),
     dof=[2.6, [TEA["win_x"], TEA["front_y"] - 0.4, TEA["win_z"]]], hand=0.0012)
shot("S68", "L68", cam((0, [-1.1, 5.82 - 0.2, 0.68], [-1.18, 5.82, 0.68], 40), (1, [-2.0, 5.82 - 0.2, 0.68], [-1.88, 5.82, 0.68], 40)), dof=[9.0, [-1.5, 5.82, 0.68]], hand=0.002)
shot("S69", "L69", cam((0, *win("tea", 0.11, tz=-0.012, tx=-0.012)[:2], 52), (1, *win("tea", 0.095, tz=-0.012, tx=-0.012)[:2], 54)),
     dof=[3.0, [TEA["win_x"] - 0.02, TEA["front_y"] + 0.04, TEA["floor_z"] + 0.034]], hand=0.0, step=1)

# ---------------------------------------------------------------------------------------------- acting
# me
me_expr = "worried"
put("me", "L01.3", [1.95, -0.9, -0.5], yaw=180, lean=55, head=[0, 0], hidden=False, expr="neutral", arms=[0, 0])
walk("me", "L03", [1.95, -0.9, -0.5], lean=55)
put("me", "L04", [-3.3, -3.0, 0], hidden=False, expr="neutral", lean=0, head=[0, 0], arms=[0, 0])
walk("me", "L04+1.5", [-0.2, -1.2, 0])
walk("me", "L04>", [-0.2, -1.2, 0])
put("me", "L05", [1.7, -1.6, 0], yaw=-90, expr="neutral", lean=0, head=[0, 0])
walk("me", "L06-0.03", [1.7, -1.6, 0])
put("me", "L06", [0.6, -1.05, -0.45], yaw=180, lean=50, head=[0, 0], arms=[70, 70], expr="neutral")
gone("me", "L07")
put("me", "L14", [2.45, -1.0, -0.48], yaw=180, lean=48, head=[0, 0], arms=[0, 128], expr="worried")
put("me", "L15", bend("bakery", 0.06)["pos"], **{k: v for k, v in bend("bakery", 0.06).items() if k != "pos"}, expr="worried", arms=[0, 0])
gone("me", "L16")
put("me", "L21", bend("blue", 0.06)["pos"], **{k: v for k, v in bend("blue", 0.06).items() if k != "pos"}, expr="worried", arms=[0, 0])
gone("me", "L22")
put("me", "L30", bend("chapel", 0.01)["pos"], **{k: v for k, v in bend("chapel", 0.01).items() if k != "pos"}, expr="worried", arms=[0, 0])
gone("me", "L31")
put("me", "L33", [CX + 0.9, 0.1, 0], yaw=90, expr="worried", lean=0, head=[0, 0], hidden=False)
walk("me", "L33+1.4", [CX + 1.55, 0.1, 0], yaw=90)
put("me", "L34", [CX - 0.15, -0.9, 0.7], yaw=90, lean=-90, head=[0, 0], expr="worried", hidden=False, blink=True)
gone("me", "L35")
put("me", "L41", bend("tea", 0.05)["pos"], **{k: v for k, v in bend("tea", 0.05).items() if k != "pos"}, expr="worried", arms=[0, 0])
gone("me", "L42")
put("me", "L46", [-0.6, -1.2, 0], yaw=180, expr="wide", lean=0, head=[0, 0], hidden=False, arms=[0, 0])
gone("me", "L47")
put("me", "L50", bend("bakery", 0.30, a=60, fz=-0.1)["pos"], **{k: v for k, v in bend("bakery", 0.30, a=60, fz=-0.1).items() if k != "pos"}, expr="blank", arms=[0, 0])
put("me", "L53", bend("blue", 0.30, a=60, fz=-0.1)["pos"], **{k: v for k, v in bend("blue", 0.30, a=60, fz=-0.1).items() if k != "pos"}, expr="blank", arms=[0, 0])
put("me", "L53.1", bend("chapel", 0.30, a=60, fz=-0.1)["pos"], **{k: v for k, v in bend("chapel", 0.30, a=60, fz=-0.1).items() if k != "pos"}, expr="blank", arms=[0, 0])
gone("me", "L53.2")
put("me", "L55", [0.3, -1.6, -0.5], yaw=180, lean=-12, head=[0, 8], expr="worried", hidden=False, arms=[-20, -20])
put("me", "L56", [0.3, -1.6, 0], yaw=180, lean=0, head=[0, 0], expr="neutral", hidden=False, arms=[0, 0])
walk("me", "L56+0.9", [0.3, -1.6, 0])
walk("me", "L57-0.03", [0.3, -6.0, 0])
put("me", "L57", [TX + 2.6, -10.0, 0], expr="neutral")
walk("me", "L57+1.9", [TX + 0.3, -3.3, 0])
walk("me", "L58-0.03", [TX + 0.3, -2.3, 0])
walk("me", "L58+0.8", [TX + 1.0, -2.0, 0])
put("me", "L63", [CX + 0.6, 2.15, 0], yaw=0, lean=24, head=[0, 10], expr="neutral", arms=[0, 0], hidden=False)
gone("me", "L64")
# Maggie and the townsfolk
put("t1", "L05", [-2.0, -2.9, 0], yaw=90, hidden=False, expr="neutral")
key("t1", "L05+1.2", head=[0, 0], blend=0.01)
key("t1", "L05+1.45", head=[-25, 16], blend=0.3)
key("t1", "L05+1.9", head=[0, 0], blend=0.4)
walk("t1", "L05+2.3", [2.2, -2.9, 0], yaw=90)
gone("t1", "L06")
put("t2", "L05", [-2.9, -2.1, 0], yaw=90, hidden=False, expr="neutral")
key("t2", "L05+1.5", head=[0, 0], blend=0.01)
key("t2", "L05+1.75", head=[-25, 16], blend=0.3)
key("t2", "L05+2.2", head=[0, 0], blend=0.4)
walk("t2", "L05+2.3", [1.6, -2.1, 0], yaw=90)
gone("t2", "L06")
# the tea shop, L58 on: everyone faces the door (-y), heads turned away until "quiet"
spots = {"t1": (TX - 2.4, -0.3), "t2": (TX + 2.1, -0.5), "t3": (TX - 2.6, 1.6), "t4": (TX + 2.4, 1.6), "t5": (TX - 0.4, 1.3)}
for who, (x, y) in spots.items():
    put(who, "L57", [x, y, 0], yaw=0, head=[70 if x < TX else -70, 6], hidden=False, expr="neutral")
    key(who, "L58", head=[0, 0], blend=0.55)
put("maggie", "L57", [TX + 0.8, 1.7, 0], yaw=0, head=[-60, 5], hidden=False, expr="neutral")
key("maggie", "L58", head=[0, 0], blend=0.5)
walk("maggie", "L59", [TX + 0.8, 1.7, 0], arms=[88, 88], head=[0, 8])
walk("maggie", "L59+1.6", [TX + 0.2, -1.5, 0])
key("maggie", "L59+1.7", arms=[88, 88], yaw=0)
key("maggie", "L60", yaw=0, head=[0, 4])
acting["maggie"].append({"from": "L60.1", "to": "L60.4>", "mouth": [0.8, 0.8], "flap": True})
acting["maggie"].append({"from": "L61", "to": "L61>", "mouth": [0.8, 0.8], "flap": True})
key("maggie", "L61>", arms=[88, 88])
gone("maggie", "L62")
# L64: half the town leans over the model, then (L67) leans in at the tea shop window
town = [("t4", -1.7), ("t1", -1.0), ("t2", -0.35), ("t3", 0.3), ("maggie", 0.95), ("t5", 1.6)]
for who, x in town:
    d = dict(yaw=180, lean=58, head=[0, -22], hidden=False, expr="soft", arms=[0, 0])
    put(who, "L64", [x, -1.05, -0.5], **d)
    gone(who, "L67")
tea_faces = [("t1", -0.2, 0.0, 0.5), ("maggie", 0.0, 0.05, 0.42), ("t3", 0.2, 0.0, 0.52), ("t4", -0.05, 0.16, 0.62), ("t5", 0.12, -0.12, 0.62)]
for who, dx, dz, gap in tea_faces:
    b = bend("tea", gap, a=60, dx=dx, dz=dz, expr="soft", arms=[0, 0])
    put(who, "L67", b["pos"], **{k: v for k, v in b.items() if k != "pos"}, hidden=False)
    gone(who, "L68")
# the Resident (never seen moving): found in his window after each cut
res("L01", "bakery", "away")
res("L10", "bakery", "away")
gone("resident", "L11")
res("L13", "bakery", "profile")
res("L14", "bakery", "away")
gone("resident", "L18")
res("L19", "blue", "away")
gone("resident", "L24")
res("L25", "chapel", "away")
gone("resident", "L32")
res("L32.3", "next", "away")
gone("resident", "L35")
res("L42", "tea", "turned")
res("L43", "tea", "away")
res("L44", "tea", "turned")
gone("resident", "L45")
res("L49", "bakery", "glass")
res("L53", "blue", "glass")
res("L53.1", "chapel", "glass")
gone("resident", "L53.2")
res("L54.2", "tea", "away")
gone("resident", "L55")

# ---------------------------------------------------------------------------------------------- cues
cues = [
    {"at": "L17", "name": "stone", "on": True},
    {"at": "L38", "name": "cloud", "level": 0.42, "dur": 3.2},
    {"at": "L64", "name": "cloud", "level": 1.0, "dur": 2.6},
    {"at": "L33", "name": "sky", "color": "#566079", "strength": 0.55, "sun": 0.0},
    {"at": "L35", "name": "sky", "color": "#8d959c", "strength": 1.0, "sun": 1.0},
    {"at": "L63", "name": "sky", "color": "#141824", "strength": 0.35, "sun": 0.0},
    {"at": "L64", "name": "sky", "color": "#8d959c", "strength": 1.0, "sun": 1.0},
    {"at": "L33", "name": "curtain", "level": 0.0},
    {"at": "L33.1", "name": "curtain", "level": 1.0, "dur": 1.8},
    {"at": "L34", "name": "curtain", "level": 1.0},
    {"at": "L51", "name": "mist", "level": 0.2, "dur": 2.4},
    {"at": "L53", "name": "mist", "level": 0.0},
    {"at": "L45", "name": "pot", "state": "stand", "at_xy": [1.0, 6.62], "z0": 0.7},
    {"at": "L45.2", "name": "pot", "state": "roll", "at_xy": [1.0, 6.62], "z0": 0.7},
    {"at": "L47", "name": "pot", "state": "hidden"},
    {"at": "L59", "name": "box", "where": "hands"},
    {"at": "L62", "name": "box", "where": "table"},
    {"at": "L63", "name": "box", "where": "none"},
    {"at": "L62", "name": "myfig", "where": "box", "stage": 0},
    {"at": "L63", "name": "myfig", "where": "desk", "stage": 0},
    {"at": "L63.2", "name": "myfig", "where": "desk", "stage": 1},
    {"at": "L63.3", "name": "myfig", "where": "desk", "stage": 2},
    {"at": "L63.4", "name": "myfig", "where": "desk", "stage": 3},
    {"at": "L64", "name": "myfig", "where": "none"},
    {"at": "L66.3", "name": "myfig", "where": "seat", "stage": 3},
    {"at": "L65", "name": "tearoof", "on": True},
    {"at": "L66", "name": "tearoof", "on": False},
]

# ---------------------------------------------------------------------------------------------- sound
sfx = [
    {"at": "L10", "kind": "thud", "db": -26},
    {"at": "L42", "kind": "sting", "db": -8},
    {"at": "L45.2", "kind": "thud", "db": -14},
    {"at": "L49.3", "kind": "riser", "db": -22, "dur": 1.8},
    {"at": "L50", "kind": "hit", "db": -16},
    {"at": "L51", "kind": "breath", "db": -22, "dur": 2.4},
    {"at": "L52", "kind": "thud", "db": -16},
    {"at": "L57.3", "kind": "door", "db": -20},
    {"at": "L66.3", "kind": "click", "db": -22},
    {"at": "L69.6", "kind": "glide", "db": -12, "dur": 1.8},
]

story = {
    "slug": "ep22-model-village",
    "title": "The little man in the model village moves one window a day",
    "made_for_kids": False,
    "premise": "I've taken a job repainting the knee-high model village on the front of a small seaside town. A thumb-sized man in a mustard scarf, made better than the glued painted figures, stands in a different tiny window every afternoon, one window further up the hill, toward my own model cottage.",
    "twist": "He was never coming for me. Every afternoon his window filled with my giant face, and every window I leaned into, he left. To him I was the monster, and at the end I am a tiny figure in the tea shop window myself.",
    "world": "a grey out-of-season seaside model village of painted wood houses on a sloping green ground, a low sea wall, wet slate sea, a gravel path round its front edge, and a brick town with a warm tea shop",
    "voice": {"voice": "am_adam", "tempo": 1.03, "rate": 1.45},
    "key_color": "#5ccfc0",
    "gap": 0.12,
    "tail": 0,
    "look": {"fog": "#8d959c", "fog_density": 0.012, "fog_start": 6.0, "sky": "#8d959c", "sky_strength": 1.0, "exposure": 0.45},
    "grade": {"shadows": [-0.01, 0.0, 0.03], "highlights": [0.0, 0.0, 0.0], "saturation": 0.95, "contrast": 1.06,
              "vignette": 0.3, "bloom": 0.2, "grain": 0.012},
    "phonemes": {},
    "cast": cast,
    "lines": lines,
    "shots": shots,
    "acting": acting,
    "cues": cues,
    "fx": [],
    "music": {"root": 50, "mode": "dorian", "bpm": 76, "seed": 22,
              "sections": [
                  {"at": 0, "voices": ["drone", "pulse"], "energy": 0.3},
                  {"at": "L08", "voices": ["drone", "pulse", "pad"], "energy": 0.35},
                  {"at": "L18", "voices": ["drone", "pulse", "pad"], "energy": 0.4},
                  {"at": "L26", "voices": ["drone", "pulse", "pad"], "energy": 0.5},
                  {"at": "L33", "voices": ["drone", "pad"], "energy": 0.3},
                  {"at": "L35", "voices": ["drone", "pulse", "choir"], "energy": 0.5},
                  {"at": "L41", "voices": ["drone"], "energy": 0.3},
                  {"at": "L42", "voices": ["drone", "pad", "choir"], "energy": 0.6},
                  {"at": "L46", "voices": ["drone", "pulse", "choir"], "energy": 0.6},
                  {"at": "L49", "voices": ["drone", "pad"], "energy": 0.4},
                  {"at": "L55", "voices": ["pad"], "energy": 0.25},
                  {"at": "L56", "voices": ["pad", "piano"], "energy": 0.35, "mode": "major", "root": 50},
                  {"at": "L64", "voices": ["pad", "piano", "pulse"], "energy": 0.45},
                  {"at": "L67", "voices": ["pad", "piano"], "energy": 0.4},
                  {"at": "L69", "voices": ["drone", "pad"], "energy": 0.3},
              ]},
    "sound": {"floor": "stone", "steps_db": -22,
              "ambience": [
                  {"kind": "water", "from": 0, "to": "L33", "lufs": -34},
                  {"kind": "wind", "from": 0, "to": "L33", "lufs": -38},
                  {"kind": "room", "from": "L33", "to": "L35", "lufs": -38},
                  {"kind": "water", "from": "L35", "to": "L57", "lufs": -34},
                  {"kind": "wind", "from": "L35", "to": "L57", "lufs": -38},
                  {"kind": "room", "from": "L57", "to": "L64", "lufs": -34},
                  {"kind": "water", "from": "L64", "to": "end", "lufs": -35},
                  {"kind": "wind", "from": "L64", "to": "end", "lufs": -39},
              ],
              "sfx": sfx,
              "music_drops": [{"from": "P01-0.1", "to": "L42", "keep": ["sting"]}]},
}
OUT.write_text(json.dumps(story, indent=1, ensure_ascii=False) + "\n")
print("wrote", OUT, f"({len(shots)} shots)")
