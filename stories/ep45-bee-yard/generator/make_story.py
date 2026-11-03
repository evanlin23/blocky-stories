"""Writes ../story.json for ep45 "bee yard" (script.md). Run from anywhere:

    python stories/ep45-bee-yard/generator/make_story.py

The words are in lines.json (made by build_lines.py). Here: the cast, the shots (ids follow the script's table S01 to
S81, plus the cold open S00 (S02 and S03 were cut in the 2026-11-03 opening fix), with a letter on the few shots split to keep every cut under about 2.3 s), who stands where in each shot, the dial
readings, the veils, the smoke, the score and the sound. Shot numbering "n" in each shot is the script's number, which
set.py reads for the light (look_of) and the gate.

Places (set.py's coordinates). The yard: origin at the gate, +y up the hill, the ground rises 0.12 per metre (gz).
Hives 1 to 12 in rows at y = 5.5, 9.5, 13.5, x = -4.5, -1.5, 1.5, 4.5. The shed is at x -5.6 to -3.6, y 0.9 to 3.6, its
board on the +x wall (x = -3.57) with hooks at y 1.75 and 2.75. The gate posts stand at x = +-1.45. The pier: x offset
300 (X), the quay at z 0 (y < 0), the deck at z 0.45 (y 0 to 28), the ticket hut at (293, -4), the café table at (306, -5.5).
"""
import json
import math
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT))
OUT = HERE.parent / "story.json"
lines = json.loads((HERE / "lines.json").read_text())

X = 300.0
PZ = 0.45
SLOPE = 0.12


def G(y):
    return SLOPE * y if y >= 0 else SLOPE * y - 0.02 * y * y


def gz(y):
    y0 = math.floor(y / 2.5) * 2.5
    u = (y - y0) / 2.5
    return G(y0) * (1 - u) + G(y0 + 2.5) * u


LIFT = 0.12
HUT = (X - 7.0, -4.0)
CAFE = (X + 6.0, -5.5)

# ---------------------------------------------------------------------------------------------------- cast


def person(shirt, pants, skin, hair, hair_c, pattern="solid", pattern_c=None, shoes="#3a2f28", sleeves="short",
           collar=None, hat="none", hat_c="#333333", extras=None, face=None, **kw):
    d = {"age": "adult", "skin": skin, "shirt": shirt, "pattern": pattern, "pants": pants, "shoes": shoes,
         "sleeves": sleeves, "hair": hair, "hair_c": hair_c, "hat": hat,
         "face": face or {"eyes": "round", "brows": True}}
    if pattern_c:
        d["pattern_c"] = pattern_c
    if collar:
        d["collar"] = collar
    if hat != "none":
        d["hat_c"] = hat_c
    if extras:
        d["extras"] = extras
    d.update(kw)
    return d


cast = {
    "me": person("#273550", "#3a3d46", "#e9c3a0", "cap", "#16151a", pattern="stripes", pattern_c="#f1e4c8",
                 shoes="#2a2a2e", collar="#f1e4c8"),
    "lena": person("#f1ede2", "#b59d74", "#d9a77c", "bun", "#3b2518", sleeves="long", collar="#8aa37f", dial_dz=0.1,
                   shoes="#5a4030", face={"eyes": "lashes", "brows": True, "cheeks": "#e98d7a"}),
    "hover": person("#e3a53a", "#8c8f94", "#d8b27a", "cap", "#8c8f94", sleeves="long", collar="#c48a28",
                    shoes="#6f7277", extras=["coat"], zip_c="#a87a25", dial_dz=0.0,
                    face={"eyes": "pin", "brows": False, "mouth": "flat", "ink": "#1a1416"}),
    "a1": person("#c2584a", "#4a5568", "#f0c7a6", "swoop", "#7a4a2a", sleeves="short", shoes="#3a2a20"),
    "a2": person("#4f7fa8", "#8a7a5e", "#b98a62", "long", "#2a1a14", sleeves="short", shoes="#3a2a20",
                 face={"eyes": "lashes", "brows": True}),
    "b1": person("#7a8f4a", "#6a5a44", "#e2b48a", "spiky", "#23201c", sleeves="short", extras=["backpack"], extra_c="#c9742e"),
    "b2": person("#d9b84a", "#3d4a66", "#8a5a3a", "bun", "#1a1412", sleeves="short", face={"eyes": "lashes", "brows": True}),
    "t": person("#8a8d90", "#4a4d52", "#e2b48a", "none", "#555555", sleeves="long", hat="ballcap", hat_c="#5a5d60",
                collar="#6b6e72", face={"eyes": "tired", "brows": True}),
    "d1": person("#e0705a", "#40495c", "#f0c7a6", "swoop", "#3a2a1c", sleeves="short", face={"eyes": "round", "brows": True, "cheeks": "#ee8a78"}),
    "d2": person("#7aa88c", "#6d5a48", "#c9946a", "long", "#4a2c1c", sleeves="short", face={"eyes": "lashes", "brows": True, "cheeks": "#ee8a78"}),
}
for i, (sh, hc, sk, hs) in enumerate((("#b75a8c", "#2a1c14", "#f0c7a6", "cap"), ("#5a7ab7", "#8a6a3a", "#b98a62", "swoop"),
                                      ("#d98a3a", "#1a1412", "#e2b48a", "long"), ("#5aa78a", "#3a2a1c", "#8a5a3a", "bun"),
                                      ("#a76ab7", "#6a3a1c", "#f0c7a6", "spiky"), ("#c9c25a", "#222222", "#c9946a", "cap"))):
    cast[f"c{i + 1}"] = person(sh, "#4a4f5c" if i % 2 else "#6a5a44", sk, hs, hc, sleeves="short")

# ---------------------------------------------------------------------------------------------------- DSL
SH = []          # (id, n, at, cam, opts)
PL = {}          # id -> {who: placement}
EX = []          # (who, ref, attrs) keys inside a shot
MOUTH = []       # (who, from, to, amount)
CUES = []


def hd(x, y, z=None, h=1.56):
    return (x, y, (gz(y) if z is None else z) + h)


def P(x, y, yaw, z=None, to=None, **kw):
    d = {"pos": [x, y, gz(y) if z is None else z], "yaw": yaw}
    if to:
        d["to"] = [to[0], to[1], gz(to[1]) if len(to) < 3 else to[2]]
    d.update(kw)
    return d


def cam(*keys):
    return [list(k) for k in keys]


def mv(p0, t0, l0, p1=None, t1=None, l1=None):
    if p1 is None:
        return cam([0, list(p0), list(t0), l0])
    return cam([0, list(p0), list(t0), l0], [1, list(p1), list(t1 if t1 is not None else t0), l1 if l1 is not None else l0])


def fc(face, yaw, off, dist, lens, dial=True, el=0.0, push=0.0, drop=None, lens2=None):
    """A camera in front of a face. face = (x, y, z of the face's centre), yaw = the way the person faces (0 faces -y),
    off = degrees round from straight on, dist = metres. With dial=True the aim is dropped so the face sits in the upper
    half of the frame with its dial above, clear of the caption band."""
    a = math.radians(yaw + off)
    hv = 24.0 * dist / lens
    if drop is None:
        drop = max(0.42 * hv - 0.85, -0.12) if dial else 0.05
    d = (math.sin(a), -math.cos(a))
    p0 = [round(face[0] + d[0] * dist, 3), round(face[1] + d[1] * dist, 3), round(face[2] + el, 3)]
    tg = [face[0], face[1], round(face[2] - drop, 3)]
    if not push and not lens2:
        return cam([0, p0, tg, lens])
    p1 = [round(face[0] + d[0] * (dist - push), 3), round(face[1] + d[1] * (dist - push), 3), round(face[2] + el, 3)]
    return cam([0, p0, tg, lens], [1, p1, tg, lens2 or lens])


def sh(sid, n, at, camera, place=None, **opt):
    SH.append((sid, n, at, camera, opt))
    PL[sid] = place or {}


def ex(who, ref, **attrs):
    EX.append((who, ref, attrs))


def talk(who, a, b, amt=0.7):
    MOUTH.append((who, a, b, amt))


def dial(who, ref, **kw):
    CUES.append({"at": ref, "name": "dial", "who": who, **kw})


def veil(who, ref, on):
    CUES.append({"at": ref, "name": "veil", "who": who, "on": on})


GATE_OUT = (0.0, -1.25)
GATE_IN = (0.0, 1.25)
LENA_W = (-1.5, 4.3)
ME = "me"
HIVE_Y = {1: 5.5, 2: 9.5, 3: 13.5}
HOV_WED = (3.0, 13.5)
HOV_THU = (3.0, 9.5)
HOV_FRI = (-2.2, 2.3)
HOV_GATE = (-0.7, 0.25)
BZ = gz(2.25) + 1.65          # the board's centre height (set.py: zb + 1.65)
BOARD_CAM_T = [-3.5, 2.25, BZ]
hv = lambda x, y, yaw=0, **kw: P(x, y, yaw, z=gz(y) + LIFT, arms=[0, 0], side=[0, 0], head=[0, 8], expr="neutral", blink=False, **kw)

# ============================================================================================ the shots
# ---- the warning, the pier and the montage (S00 to S11)
cx0, cx1 = X - 0.31, X + 0.31
hug = dict(arms=[26, 26], side=[0, 0], expr="soft")
H1 = {}     # the taller embrace: arms over and outside the partner's
H2 = {}     # the lower one: arms under, round the back     # chest to chest, arms round the back, closed smiles
# S00, the warning (L01): a Friday flash-forward, close and lit, on the wrong thing. The Hover by the shed (his
# Friday place), the empty air over his head where a dial should be, pushing in. Lena small behind him at row 1, her
# dial in frame (24 hours, Friday's reading). Never his boots: the gap is saved for L25. n=33 gives it Friday's light.
S00H = (-0.52, 3.6)
_gy = gz(S00H[1])
S00L = (0.52, 3.6)
# S00a (L01 to "Only"): a chest-up two-shot, centred for TV: Lena with her dial (24) and the Hover with empty air at the
# same height, both faces over 1/5 of the frame, pushing in. Bees hidden (set.py).
_cz = _gy + 1.45
sh("S00a", 33, 0, mv([0.0, S00H[1] - 3.3, _cz], [0.0, S00H[1], _gy + 1.5], 24, [0.0, S00H[1] - 3.05, _cz], [0.0, S00H[1], _gy + 1.5], 24),
   {"hover": hv(S00H[0], S00H[1], 0), "lena": P(S00L[0], S00L[1], 0, expr="soft", arms=[0, 0], side=[0, 0])}, hand=0.003)
# S00b ("Only ONE CLOCK"): a low insert at grass height on his floating boots, the sunlit strip under the soles, the shadow apart.
sh("S00b", 33, "L01.3", mv([S00H[0] + 0.7, S00H[1] - 2.4, _gy + 0.26], [S00H[0], S00H[1], _gy + 0.3], 26,
                          [S00H[0] + 0.55, S00H[1] - 1.9, _gy + 0.26], [S00H[0], S00H[1], _gy + 0.3], 26),
   {"hover": hv(S00H[0], S00H[1], 0), "lena": P(S00L[0], 9.0, 0, expr="soft", arms=[0, 0], side=[0, 0])}, hand=0.003)
sh("S01", 2, "L02", mv([X - 0.3, 4.9, 1.85], [X, 9.0, 2.0], 44, [X - 0.2, 5.4, 1.85], [X, 9.0, 2.0], 44),
   {"a1": P(cx0, 9.0, 90, z=PZ, head=[-72, 0], **hug, **H1), "a2": P(cx1, 9.0, 270, z=PZ, head=[72, 0], **hug, **H2),
    "b1": P(X - 1.7, 13.6, 0, z=PZ, to=(X - 1.7, 12.0, PZ), expr="neutral"), "b2": P(X + 1.8, 14.6, 0, z=PZ, to=(X + 1.8, 13.0, PZ), expr="neutral")}, hand=0.003)
cp = lambda x, y, yaw, who_head: P(x, y, yaw, z=PZ, arms=[26, 26], side=[0, 0], expr="soft", head=[who_head, 0])
sh("S04", 3, "L03", mv([X + 0.8, 15.5, 6.4], [X, 25.2, 1.4], 30, [X + 0.4, 16.5, 6.0], [X, 25.2, 1.4], 30),
   {"c1": cp(X - 1.7, 23.2, 90, -60), "c2": cp(X - 1.09, 23.2, 270, 60), "c3": cp(X + 1.09, 24.8, 90, -60),
    "c4": cp(X + 1.7, 24.8, 270, 60), "c5": cp(X - 0.31, 26.6, 90, -60), "c6": cp(X + 0.31, 26.6, 270, 60)}, hand=0.003)
sh("S05", 4, "L04", mv([HUT[0] + 4.7, -4.9, 1.55], [HUT[0] + 0.5, -4.0, 1.55], 38, [HUT[0] + 4.4, -4.8, 1.55], [HUT[0] + 0.5, -4.0, 1.55], 38),
   {"t": P(HUT[0] + 0.5, -4.0, 90, z=-0.25, expr="angry", arms=[0, 0], side=[0, 0], head=[0, 0])}, hand=0.003)
sh("S06", 4, "L04.2-0.2", fc((HUT[0] + 0.5, -4.0, 1.31), 90, 18, 2.3, 40),
   {"t": P(HUT[0] + 0.5, -4.0, 90, z=-0.25, expr="smirk", arms=[0, 0], side=[0, 0], head=[0, 0], look=[0, -1])}, hand=0.004)
ex("t", "L04.3", head=[0, -8], blend=0.3)
ex("t", "L04.3+0.7", head=[0, 9], look=[0, 0], blend=0.3)
tx, ty = CAFE
sh("S07", 5, "L05", mv([tx - 0.4, -10.8, 1.7], [tx, ty, 1.55], 36, [tx - 0.2, -10.5, 1.7], [tx, ty, 1.55], 36),
   {"d1": P(tx - 0.62, ty, 90, z=0.0, head=[-45, 0], look=[0, -1], expr="neutral", arms=[0, 0], side=[0, 0]),
    "d2": P(tx + 0.62, ty, 270, z=0.0, head=[45, 0], look=[0, -1], expr="neutral", arms=[0, 0], side=[0, 0])}, hand=0.004)
sh("S08", 6, "L06", mv([tx, -10.8, 2.3], [tx, ty, 2.0], 32),
   {"d1": P(tx - 0.62, ty, 90, z=0.0, head=[-45, 0], expr="neutral", arms=[0, 0], side=[0, 0]),
    "d2": P(tx + 0.62, ty, 270, z=0.0, head=[45, 0], expr="neutral", arms=[0, 0], side=[0, 0])}, hand=0.003)
sh("S09", 6, "L06.2-0.15", mv([tx + 0.1, -10.4, 1.75], [tx, ty, 1.5], 34, [tx + 0.1, -10.0, 1.75], [tx, ty, 1.5], 34),
   {"d1": P(tx - 0.62, ty, 90, z=0.0, head=[-30, 18], expr="shut", arms=[0, 0], side=[0, 0]),
    "d2": P(tx + 0.62, ty, 270, z=0.0, head=[30, 18], expr="shut", arms=[0, 0], side=[0, 0])}, hand=0.004)
STEP_Z = 0.22
sh("S10", 7, "L07", mv([X, -5.6, 1.3], [X, -0.9, 1.6], 28, [X, -5.3, 1.3], [X, -0.9, 1.6], 28),
   {"b1": P(X - 0.38, -1.1, 0, z=0.11, expr="neutral", arms=[0, 0], side=[0, 0]),
    "b2": P(X + 0.38, -0.65, 0, z=0.22, expr="neutral", arms=[0, 0], side=[0, 0])}, hand=0.003)
sh("S11", 8, "L08", mv([X, -5.0, 1.3], [X, -0.9, 1.6], 28, [X, -4.7, 1.3], [X, -0.9, 1.6], 28),
   {"b1": P(X - 0.38, -1.1, 0, z=0.11, expr="wide", head=[-42, 0], arms=[0, 0], side=[0, 0]),
    "b2": P(X + 0.38, -0.65, 0, z=0.22, expr="wide", head=[42, 0], arms=[0, 0], side=[0, 0])}, hand=0.004)
# ---- me
ME_Q = (X - 1.0, -9.0)
sh("S12", 9, "L09", fc(hd(*ME_Q, 0.0), 0, 14, 3.7, 35), {"me": P(ME_Q[0], ME_Q[1], 0, z=0.0, arms=[0, 0], side=[0, 0], expr="neutral")}, hand=0.004)
sh("S13", 10, "L10", fc(hd(*ME_Q, 0.0), 0, 8, 1.9, 45, push=0.12), {"me": P(ME_Q[0], ME_Q[1], 0, z=0.0, arms=[0, 0], side=[0, 0], expr="neutral")}, hand=0.003)
sh("S14", 11, "L11", mv([X + 0.6, -11.8, 1.6], [X, -7.2, 1.5], 30, [X + 0.3, -11.6, 1.6], [X - 0.2, -7.2, 1.5], 30),
   {"me": P(X + 2.3, -7.0, 270, z=0.0, to=(X - 2.0, -7.0, 0.0), arms=[0, 0], side=[22, 22], expr="neutral"),
    "a1": P(X - 0.31, -5.5, 90, z=0.0, head=[-72, 0], **hug), "a2": P(X + 0.31, -5.5, 270, z=0.0, head=[72, 0], **hug)}, hand=0.004)
# ---- Lena and the yard
sh("S15", 12, "L12", mv([-7.5, -14.0, gz(-14) + 4.2], [0.0, -1.0, 1.0], 30, [-6.8, -13.2, gz(-13.2) + 4.0], [0.0, -1.0, 1.0], 30),
   {"lena": P(-0.6, -6.5, 0, to=(0.1, -2.6), expr="neutral")}, hand=0.006)
sh("S16", 13, "L13", fc(hd(0.3, -1.25), 180, 22, 4.2, 35), {"me": P(0.3, -1.25, 180, arms=[0, 0], side=[0, 0], expr="neutral")}, hand=0.004)
sh("S17", 14, "L14", fc(hd(*GATE_IN), 0, 28, 2.6, 38), {"lena": P(GATE_IN[0], GATE_IN[1], 0, expr="neutral", arms=[0, 0], side=[0, 0])}, hand=0.004)
sh("S18", 15, "L15", mv([3.6, -4.6, 1.55], [0.0, 0.0, 1.5], 30, [3.4, -4.4, 1.55], [0.0, 0.0, 1.5], 30),
   {"me": P(0.0, -0.95, 180, arms=[0, 150], side=[0, 0], expr="neutral"),
    "lena": P(0.0, 0.9, 0, arms=[0, 150], side=[0, 0], expr="neutral")}, hand=0.004)
sh("S19", 16, "L16", fc(hd(0.0, -1.25), 180, 22, 3.5, 35),
   {"me": P(0.0, -1.25, 180, arms=[70, 70], side=[0, 0], expr="neutral"), "lena": P(-3.2, 2.4, 0, arms=[0, 0], side=[0, 0], expr="neutral")}, hand=0.004)
ex("me", "L16.2-0.4", arms=[0, 150], blend=0.35)
sh("S20", 16, "L16.2", fc(hd(-0.7, 1.6), 0, 22, 2.3, 40), {"lena": P(-0.7, 1.6, 0, expr="neutral", arms=[0, 0], side=[0, 0])}, hand=0.004)
sh("S21", 17, "L17", mv([3.7, -4.4, 1.55], [0.0, 0.05, 1.5], 28, [3.5, -4.2, 1.55], [0.0, 0.05, 1.5], 28),
   {"me": P(0.3, -0.95, 140, arms=[0, 0], side=[25, 25], expr="worried", head=[-30, 0]),
    "lena": P(-0.4, 0.95, 0, arms=[0, 0], side=[0, 0], expr="neutral")}, hand=0.004)
sh("S22", 18, "L18", mv([3.4, -3.0, 1.6], [-0.4, 0.4, 1.35], 28, [3.2, -2.8, 1.6], [-0.4, 0.4, 1.35], 28),
   {"me": P(1.0, -1.2, 120, arms=[0, 95], side=[0, 0], expr="neutral"),
    "lena": P(-0.3, 1.05, 330, arms=[0, 0], side=[0, 0], expr="neutral")}, hand=0.004)
sh("S22b", 18, "L18.3", fc(hd(1.0, -1.2), 140, 18, 3.0, 35), {"me": P(1.0, -1.2, 120, arms=[0, 95], side=[0, 0], expr="neutral")}, hand=0.004)
LW = (-1.5, 4.3)
sh("S23", 19, "L19", fc(hd(*LW), 0, 24, 4.6, 55), {"lena": P(LW[0], LW[1], 0, expr="neutral", arms=[0, 0], side=[0, 0])}, hand=0.004)
sh("S24", 20, "L20", fc(hd(0.3, -1.25), 160, 12, 3.3, 35),
   {"me": P(0.3, -1.25, 160, arms=[0, 0], side=[0, 0], expr="worried", head=[-40, 0])}, hand=0.004)
ex("me", "L20.1", head=[40, 0], blend=1.0)
sh("S25", 21, "L21", mv([1.6, 3.0, 1.4], [-1.5, 4.9, 1.45], 26, [1.4, 3.2, 1.4], [-1.5, 4.9, 1.45], 26),
   {"lena": P(-1.5, 4.65, 180, lean=22, arms=[55, 55], side=[0, 0], expr="neutral")}, hand=0.004)
sh("S26", 22, "L21.3", fc(hd(*LW), 0, 24, 2.6, 40), {"lena": P(LW[0], LW[1], 0, expr="neutral", arms=[0, 0], side=[0, 0])}, hand=0.004)
sh("S27", 22, "L22.1", fc(hd(*LW), 0, -24, 2.6, 40), {"lena": P(LW[0], LW[1], 0, expr="neutral", arms=[0, 0], side=[0, 0])}, hand=0.004)
# ---- Wednesday: the Hover in the last row
sh("S28", 23, "L23", mv([0.4, -0.8, 1.5], [2.4, 13.5, 1.9], 34, [0.5, -0.7, 1.5], [2.4, 13.5, 1.9], 38),
   {"hover": hv(*HOV_WED, 0), "lena": P(-1.5, 4.65, 180, lean=22, arms=[55, 55], side=[0, 0], expr="neutral")}, hand=0.004)
sh("S29", 24, "L24", mv([0.0, 8.0, gz(8.0) + 0.4], [3.0, 13.5, gz(13.5) + 0.95], 34, [0.2, 8.4, gz(8.4) + 0.4], [3.0, 13.5, gz(13.5) + 1.0], 36), {"hover": hv(*HOV_WED, 0)}, hand=0.002)
sh("S30", 25, "L25", mv([6.7, 9.7, gz(9.7) + 0.3], [3.0, 13.5, gz(13.5) + 0.62], 45, [6.4, 9.9, gz(9.9) + 0.28], [3.0, 13.5, gz(13.5) + 0.62], 45),
   {"hover": hv(*HOV_WED, 0)}, hand=0.0015)
sh("S31", 25, "L25.3", mv([4.1, 12.2, gz(12.2) + 0.1], [3.0, 13.5, gz(13.5) + 0.12], 50, [3.9, 12.3, gz(12.3) + 0.1], [3.0, 13.5, gz(13.5) + 0.12], 52),
   {"hover": hv(*HOV_WED, 0)}, hand=0.0015)
sh("S32", 26, "L26.1", mv([3.3, 11.3, gz(11.3) + 0.3], [3.0, 13.5, gz(13.5) + 0.7], 28, [3.3, 11.6, gz(11.5) + 0.4], [3.0, 13.5, gz(13.5) + 1.8], 28),
   {"hover": hv(*HOV_WED, 0)}, hand=0.002)
sh("S32b", 27, "L27", fc(hd(*HOV_WED, gz(13.5) + LIFT), 0, 14, 3.0, 36, dial=False, drop=-0.05), {"hover": hv(*HOV_WED, 0)}, hand=0.002)
sh("S33", 28, "L28", fc(hd(0.2, -1.25), 160, 10, 2.9, 38),
   {"me": P(0.2, -1.25, 160, arms=[0, 0], side=[0, 0], expr="scared", head=[-20, 0])}, hand=0.005)
talk("me", "L28", "L28.2", 0.8)
sh("S34", 28, "L28.2+0.2", mv([0.5, 0.1, 1.55], [-1.5, 4.3, 1.75], 38, [0.5, 0.3, 1.55], [-1.5, 4.3, 1.75], 40),
   {"lena": P(LW[0], LW[1], 180, expr="neutral", arms=[0, 0], side=[0, 0])}, hand=0.004)
ex("lena", "L28.2+0.3", yaw=0, blend=0.4)
sh("S35", 29, "L29", fc(hd(*LW), 0, 24, 2.6, 40), {"lena": P(LW[0], LW[1], 0, expr="neutral", arms=[0, 0], side=[0, 0])}, hand=0.004)
# ---- Thursday
sh("S36", 30, "L30", mv([0.6, 5.2, gz(5.2) + 0.4], [3.0, 9.5, gz(9.5) + 0.95], 34, [0.8, 5.5, gz(5.5) + 0.4], [3.0, 9.5, gz(9.5) + 1.0], 36), {"hover": hv(*HOV_THU, 0)}, hand=0.003)
sh("S37", 31, "L31", fc(hd(*HOV_THU, gz(9.5) + LIFT), 0, 16, 2.6, 40, dial=False, drop=0.0), {"hover": hv(*HOV_THU, 0)}, hand=0.002)
sh("S37b", 31, "L31.2", fc(hd(*HOV_THU, gz(9.5) + LIFT), 0, -12, 1.7, 45, dial=False, drop=0.0, push=0.15), {"hover": hv(*HOV_THU, 0)}, hand=0.0015)
sh("S38", 32, "L32", fc(hd(*LW), 0, -24, 2.6, 40), {"lena": P(LW[0], LW[1], 0, expr="neutral", arms=[0, 0], side=[0, 0])}, hand=0.004)
# ---- Friday: the shed, the veils
HF = hv(HOV_FRI[0], HOV_FRI[1], 40)
sh("S39", 33, "L33", mv([0.7, -1.0, 1.5], [-2.6, 2.3, 1.45], 36, [0.6, -0.9, 1.5], [-2.6, 2.3, 1.45], 36), {"hover": HF}, hand=0.003)
sh("S40", 34, "L33.3+0.2", mv([-0.6, 2.3, BZ + 0.0], BOARD_CAM_T, 28, [-0.7, 2.3, BZ + 0.0], BOARD_CAM_T, 28), {}, hand=0.003)
sh("S41", 34, "L34.2", mv([-1.5, 1.75, BZ + 0.05], [-3.5, 1.75, BZ + 0.05], 38, [-1.7, 1.75, BZ + 0.05], [-3.5, 1.75, BZ + 0.05], 40), {}, hand=0.003)
sh("S42", 35, "L35.1", mv([-1.25, 2.5, BZ + 0.0], [-3.5, 2.5, BZ - 0.02], 26), {}, hand=0.002)
sh("S43", 36, "L36", mv([0.6, -0.9, 1.55], [-2.5, 2.3, 1.7], 40, [0.5, -0.8, 1.55], [-2.5, 2.3, 1.7], 40),
   {"lena": P(-2.6, 2.6, 40, expr="neutral", arms=[0, 0], side=[0, 0])}, hand=0.004)
sh("S44", 37, "L37", mv([0.8, -0.8, gz(-0.8) + 0.9], [-2.2, 2.6, 1.3], 36), {"hover": hv(-2.2, 2.9, 40)}, hand=0.003)
sh("S44b", 37, "L37.3", mv([-0.6, 0.7, gz(0.7) + 0.3], [-2.2, 2.9, gz(2.9) + 0.2], 40), {"hover": hv(-2.2, 2.9, 40)}, hand=0.002)
# ---- night, Saturday
sh("S45", 38, "L38", fc(hd(X, -9.0, 0.0), 0, 12, 3.2, 35), {"me": P(X, -9.0, 0, z=0.0, arms=[0, 0], side=[0, 0], expr="worried", head=[0, -12])}, hand=0.004)
sh("S46", 38, "L38.3", fc(hd(-2.2, 2.25, gz(2.25) + LIFT), 40, 8, 1.8, 50, dial=False, drop=0.05), {"hover": hv(-2.2, 2.25, 40)}, hand=0.0015)
sh("S47", 39, "L39", fc(hd(0.2, -1.25), 180, 20, 4.0, 32),
   {"me": P(0.2, -1.25, 180, arms=[0, 0], side=[0, 0], expr="neutral")}, hand=0.004)
sh("S47b", 39, "L39.2", fc(hd(0.2, -1.25), 180, -28, 2.7, 38), {"me": P(0.2, -1.25, 180, arms=[0, 0], side=[0, 0], expr="neutral")}, hand=0.004)
# ---- the smoke
SMK = (-1.9, 3.9)
sh("S48", 40, "L40", mv([0.9, 0.2, 1.6], [-2.0, 3.7, 1.55], 36, [0.7, 0.3, 1.6], [-2.0, 3.7, 1.55], 38),
   {"lena": P(SMK[0], SMK[1], 320, arms=[55, 0], side=[0, 0], expr="neutral")}, hand=0.004)
sh("S49", 41, "L41", fc(hd(*SMK), 0, 38, 4.6, 50), {"lena": P(SMK[0], SMK[1], 320, arms=[55, 0], side=[0, 0], expr="neutral")}, hand=0.004)
sh("S50", 42, "L42", mv([0.0, -0.9, 1.55], [0.0, 14.0, 1.4], 30, [0.0, -0.8, 1.55], [0.0, 14.0, 1.4], 30), {}, hand=0.005)
sh("S51", 43, "L43", fc(hd(0.2, -1.0), 180, 18, 3.0, 35),
   {"me": P(0.2, -1.0, 180, arms=[0, 120], side=[0, 0], expr="worried")}, hand=0.005)
ex("me", "L43.1", arms=[0, 95], blend=0.3)
# ---- the reveal
HG = hv(HOV_GATE[0], HOV_GATE[1], 0)
sh("S52", 44, "L44", mv([0.6, -3.3, 0.85], [-0.7, 0.25, 1.4], 30, [0.5, -3.0, 0.85], [-0.7, 0.25, 1.4], 32),
   {"hover": HG, "me": P(-1.25, -0.85, 180, arms=[0, 0], side=[0, 0], expr="scared")}, hand=0.003)
sh("S53", 45, "L45", mv([0.45, -2.4, gz(-2.4) + 0.35], [-0.7, 0.3, gz(0.2) + 1.85], 30, [0.5, -2.3, gz(-2.3) + 0.4], [-0.7, 0.3, gz(0.2) + 1.85], 30),
   {"hover": HG, "me": P(-1.6, -0.9, 180, arms=[0, 0], side=[0, 0], expr="terrified", head=[0, -8])}, hand=0.003)
sh("S54", 45, "L45.2", mv([0.4, -1.3, gz(0.2) + 0.12], [-0.7, 0.25, gz(0.2) + 0.2], 40, [0.3, -1.2, gz(0.2) + 0.12], [-0.7, 0.25, gz(0.2) + 0.2], 40),
   {"hover": HG}, hand=0.0015)
sh("S55", 46, "L46", fc(hd(*HOV_GATE, gz(0.2) + LIFT), 0, 12, 2.1, 45, dial=False, drop=0.0), {"hover": HG}, hand=0.002)
LENA_S = (0.0, 6.0)
sh("S56", 47, "L47", mv([0.7, -1.4, 1.7], [0.0, 6.0, 2.0], 45, [0.6, -1.3, 1.7], [0.0, 6.0, 2.0], 48),
   {"hover": HG, "lena": P(LENA_S[0], LENA_S[1], 0, arms=[30, 30], side=[0, 0], expr="neutral")}, hand=0.004)
sh("S57", 48, "L48", fc(hd(0.0, -1.0), 180, -70, 2.3, 45), {"me": P(0.0, -1.0, 180, arms=[0, 0], side=[0, 0], expr="worried")}, hand=0.004)
sh("S58", 49, "L49", fc(hd(0.0, -1.0), 180, 14, 2.5, 40), {"me": P(0.0, -1.0, 180, arms=[0, 0], side=[0, 0], expr="blank")}, hand=0.003)
sh("S59", 49, "L49.2+0.15", fc(hd(*LENA_S), 0, 8, 5.4, 55), {"lena": P(LENA_S[0], LENA_S[1], 0, arms=[30, 30], side=[0, 0], expr="neutral")}, hand=0.004)
sh("S60", 50, "L50", mv([0.3, 0.0, 1.6], [-0.4, 6.2, 1.7], 38, [0.3, 0.2, 1.6], [-0.4, 6.2, 1.7], 40),
   {"lena": P(-0.4, 6.2, 180, arms=[40, 40], side=[0, 0], expr="neutral")}, hand=0.004)
sh("S60b", 50, "L50.2", fc(hd(-0.4, 6.2), 180 + 180, 10, 3.3, 52), {"lena": P(-0.4, 6.2, 0, arms=[40, 40], side=[0, 0], expr="neutral")}, hand=0.004)
sh("S61", 51, "L51", fc(hd(0.0, -1.0), 180, 24, 2.3, 42), {"me": P(0.0, -1.0, 180, arms=[0, 0], side=[0, 0], expr="angry")}, hand=0.004)
sh("S64", 52, "L52", mv([-4.4, -3.4, 1.4], [0.2, 0.8, 1.4], 28, [-4.0, -3.1, 1.4], [0.3, 1.4, 1.4], 28),
   {"hover": HG, "me": P(0.9, -1.7, 180, to=(1.0, 2.6), arms=[0, 0], side=[0, 0], expr="angry")}, hand=0.004)
sh("S62", 52, "L52.2", mv([-0.6, 2.3, BZ], BOARD_CAM_T, 28, [-0.7, 2.3, BZ], BOARD_CAM_T, 28), {}, hand=0.004)
sh("S63", 53, "L53", fc(hd(0.0, -1.0), 180, 18, 2.4, 40), {"me": P(0.0, -1.0, 180, arms=[0, 0], side=[0, 0], expr="angry")}, hand=0.004)
sh("S65", 54, "L54", fc(hd(*LENA_S), 0, 10, 3.0, 50), {"lena": P(LENA_S[0], LENA_S[1], 0, arms=[30, 30], side=[0, 0], expr="neutral")}, hand=0.004)
sh("S66", 55, "L55", mv([3.7, 3.6, 1.5], [0.0, 5.7, 1.5], 35, [3.5, 3.8, 1.5], [0.0, 5.7, 1.5], 35),
   {"me": P(0.0, 5.4, 180, arms=[82, 82], side=[0, 0], expr="shut"), "lena": P(0.0, 6.0, 0, arms=[82, 82], side=[0, 0], expr="grin")}, hand=0.004)
sh("S67", 56, "L56", fc(hd(*LENA_S), 0, 70, 3.2, 55, push=0.3), {"me": P(0.0, 5.4, 180, arms=[82, 82], side=[0, 0], expr="shut"),
   "lena": P(0.0, 6.0, 0, arms=[82, 82], side=[0, 0], expr="grin")}, hand=0.003)
sh("S68", 57, "L57", fc(hd(0.0, 5.4), 180, -72, 2.9, 40), {"me": P(0.0, 5.4, 180, arms=[82, 82], side=[0, 0], expr="soft"),
   "lena": P(0.0, 6.0, 0, arms=[82, 82], side=[0, 0], expr="grin")}, hand=0.003)
sh("S69", 58, "L58", fc(hd(0.0, 5.4), 180, -78, 1.8, 50), {"me": P(0.0, 5.4, 180, arms=[82, 82], side=[0, 0], expr="neutral"),
   "lena": P(0.0, 6.0, 0, arms=[82, 82], side=[0, 0], expr="grin")}, hand=0.003)
sh("S70", 59, "L59", mv([1.6, -3.2, 1.3], [-0.6, 0.3, 0.8], 30, [1.4, -2.9, 1.3], [-0.6, 0.3, 0.8], 30), {}, hand=0.004)
sh("S71", 60, "L60", fc(hd(0.0, 5.45), 0, 12, 3.4, 35), {"me": P(0.0, 5.45, 0, arms=[82, 82], side=[0, 0], expr="neutral", head=[0, 0]),
   "lena": P(-0.85, 4.9, 180, arms=[82, 82], side=[0, 0], expr="grin")}, hand=0.004)
# ---- Monday again, and the turn
sh("S72", 61, "L61", mv([3.7, -4.5, 1.55], [0.0, 0.0, 1.5], 28, [3.5, -4.3, 1.55], [0.0, 0.0, 1.5], 28),
   {"me": P(0.0, -0.95, 180, arms=[0, 0], side=[0, 0], expr="neutral"), "lena": P(0.0, 0.95, 0, arms=[0, 0], side=[0, 0], expr="neutral")}, hand=0.004)
sh("S72b", 61, "L61.2", fc(hd(0.0, 0.95), 0, 24, 2.4, 45), {"lena": P(0.0, 0.95, 0, arms=[0, 0], side=[0, 0], expr="neutral")}, hand=0.004)
sh("S73", 62, "L62", fc(hd(0.0, -0.95), 180, 26, 3.6, 35), {"me": P(0.0, -0.95, 180, arms=[0, 150], side=[0, 0], expr="neutral"),
   "lena": P(0.0, 0.95, 0, arms=[0, 150], side=[0, 0], expr="neutral")}, hand=0.004)
sh("S73b", 62, "L62.2", fc(hd(0.0, 0.95), 0, -24, 2.4, 45), {"lena": P(0.0, 0.95, 0, arms=[0, 150], side=[0, 0], expr="neutral")}, hand=0.004)
sh("S74", 63, "L63", fc(hd(0.0, 0.95), 0, 14, 1.9, 50), {"lena": P(0.0, 0.95, 0, arms=[0, 0], side=[0, 0], expr="grin")}, hand=0.003)
sh("S75", 64, "L64", fc(hd(0.0, -0.95), 180, 20, 2.1, 46), {"me": P(0.0, -0.95, 180, arms=[0, 0], side=[0, 0], expr="wide")}, hand=0.003)
sh("S76", 65, "L65", fc(hd(0.0, -0.95), 180, 10, 1.6, 50), {"me": P(0.0, -0.95, 180, arms=[0, 0], side=[0, 0], expr="neutral")}, hand=0.003)
sh("S76b", 65, "L65.2", fc(hd(0.0, -0.95), 180, -30, 2.4, 40), {"me": P(0.0, -0.95, 180, arms=[0, 0], side=[0, 0], expr="neutral", head=[0, 10])}, hand=0.003)
sh("S77", 66, "L66", fc(hd(0.0, 0.95), 0, 10, 1.6, 50), {"lena": P(0.0, 0.95, 0, arms=[0, 0], side=[0, 0], expr="grin")}, hand=0.004)
sh("S78", 67, "L67", mv([-0.6, 2.3, BZ], BOARD_CAM_T, 28, [-0.7, 2.3, BZ], BOARD_CAM_T, 28), {}, hand=0.004)
sh("S79", 68, "L68", mv([2.9, -0.4, 1.5], [0.0, 0.0, 1.5], 33, [2.6, -0.4, 1.5], [0.0, 0.0, 1.5], 33),
   {"me": P(0.0, -0.4, 180, arms=[82, 82], side=[0, 0], expr="neutral"), "lena": P(0.0, 0.25, 0, arms=[82, 82], side=[0, 0], expr="grin")}, hand=0.004)
sh("S80", 69, "L69", mv([0.0, -0.9, 1.6], [0.0, 3.0, 1.5], 30, [0.0, -0.7, 1.6], [0.0, 3.0, 1.5], 30),
   {"me": P(-0.7, 3.0, 0, arms=[0, 0], side=[0, 0], expr="neutral"), "lena": P(0.7, 3.0, 0, arms=[0, 0], side=[0, 0], expr="grin")}, hand=0.004)
_cz = gz(3) + 1.75
_pp = {"me": P(-0.55, 3.0, 0, arms=[0, 0], side=[0, 0], expr="neutral"), "lena": P(0.55, 3.0, 0, arms=[0, 0], side=[0, 0], expr="grin")}
sh("S80b", 69, "L69.3", mv([0.0, -2.9, _cz], [0.0, 3.0, _cz], 36, [0.0, -2.5, _cz], [0.0, 3.0, _cz], 36), dict(_pp), hand=0.004)
sh("S81", 70, "L70", mv([0.0, -2.5, _cz], [0.0, 3.0, _cz], 36, [0.0, -2.1, _cz], [0.0, 3.0, _cz], 38), dict(_pp), hand=0.003)

# ================================================================================================== dials
# unit pips: 1 seconds, 2 minutes, 3 hours, 4 days, 5 months, 6 years
for who in ("a1", "a2"):
    dial(who, 0, glow=1.0, vis=0.0, val="", unit=0, frac=1.0, mark="0")
    dial(who, "L03", glow=0.0, vis=1.0, val="5", unit=5, frac=1.0, ramp=1.0)
    dial(who, "L11", glow=1.0, vis=0.0, ramp=0.8, mark="0")
dial("b1", 0, val="12", unit=3, frac=0.62, glow=0.0, vis=1.0, tone="coral")
dial("b2", 0, val="3", unit=4, frac=0.4, glow=0.0, vis=1.0, tone="coral")
dial("b1", "L02.1", val="11", unit=3, frac=0.58)
dial("b1", "L07+0.2", glow=0.0)
dial("b1", "L07.1", glow=1.0, vis=0.0, ramp=0.8, mark="0")
dial("b2", "L07.1", glow=1.0, vis=0.0, ramp=0.8, mark="0")
dial("b1", "L08.2", glow=0.0, vis=1.0, ramp=1.0, val="3", unit=5, frac=1.0)
dial("b2", "L08.2", glow=0.0, vis=1.0, ramp=1.0, val="8", unit=5, frac=1.0)
for c in ("c1", "c2", "c3", "c4", "c5", "c6"):
    dial(c, 0, glow=1.0, vis=0.0, val="", unit=0, frac=1.0, mark="0")
dial("t", 0, val="9", unit=6, frac=1.0, glow=0.0, vis=1.0, tone="coral")
for d_ in ("d1", "d2"):
    dial(d_, 0, val="4", unit=3, frac=0.5, glow=0.0, vis=1.0, tone="coral")
dial("me", 0, val="", unit=0, frac=1.0, glow=0.0, vis=0.0)
dial("me", "L57.1", val="6", unit=3, frac=0.8, vis=1.0, glow=0.0, ramp=1.0, tone="coral")
dial("me", "L68", val="7", unit=3, frac=0.7)      # the later numbers are small
# Lena: months, the Monday dip, hours, minutes, seconds, zero
dial("lena", 0, val="24", unit=3, frac=0.34, glow=0.0, vis=1.0, tone="coral")     # S00 is a Friday flash-forward
dial("lena", "L02", val="4", unit=5, frac=0.92, tone="coral")
dial("lena", "L16+0.75", val="2", unit=1, frac=0.07, tone="honey", ramp=0.3)
dial("lena", "L16.2+0.9", val="1", unit=1, frac=0.04)
dial("lena", "L17", val="4", unit=5, frac=0.92, tone="coral")
dial("lena", "L19", val="72", unit=3, frac=0.95, tone="coral")
dial("lena", "L22", val="70", unit=3, frac=0.93)
dial("lena", "L22.1", val="66", unit=3, frac=0.88)
dial("lena", "L29", val="48", unit=3, frac=0.66)
dial("lena", "L32", val="24", unit=3, frac=0.34)
dial("lena", "L41", val="1", unit=2, frac=0.03, tone="honey")
dial("lena", "L47", val="20", unit=1, frac=0.33)
dial("lena", "L49.2", val="16", unit=1, frac=0.27)
dial("lena", "L50.2", val="13", unit=1, frac=0.21)
dial("lena", "L54.1", val="3", unit=1, frac=0.05)
dial("lena", "L54.1+0.4", val="2", unit=1, frac=0.03)
dial("lena", "L54.1+0.8", val="1", unit=1, frac=0.015)
dial("lena", "L55+0.55", val="0", unit=1, frac=0.0)
dial("lena", "L56.1", glow=1.0, vis=0.0, ramp=0.8, mark="0")
dial("lena", "L57.1+0.8", glow=0.0, vis=1.0, ramp=1.0, val="9", unit=3, frac=1.0, tone="coral")
dial("lena", "L61", val="1", unit=1, frac=0.05, tone="honey")
dial("lena", "L62.2", val="4", unit=5, frac=0.92, tone="coral")
dial("lena", "L68", val="5", unit=3, frac=0.8)
dial("lena", "L69", val="3", unit=3, frac=0.5)
# veils: hers goes on Saturday morning, mine for the run; the board's veils are set.py's
veil("lena", 0, False)
veil("lena", "L40", True)
veil("lena", "L61", False)
veil("lena", "L63", True)
veil("lena", "L67", False)
veil("lena", "L68", True)
veil("me", 0, False)
veil("me", "L53", True)
veil("me", "L61", False)
veil("me", "L68", True)
CUES += [{"at": "L40", "name": "smoke_in"}, {"at": "L59", "name": "smoke_out"},
         {"at": "L40+0.1", "name": "puff", "dur": 6.5}, {"at": "L52.3-0.05", "name": "veil_take"}]

# ================================================================================================== story
shots, ids = [], []
for sid, n, at, camera, opt in SH:
    s = {"id": sid, "n": n, "cam": camera, "step": opt.get("step", 2)}
    if ids:
        s["at"] = at
    if "hand" in opt:
        s["hand"] = opt["hand"]
    shots.append(s)
    ids.append(sid)
REF = {s[0]: (0 if i == 0 else s[2]) for i, s in enumerate(SH)}

story = {
    "slug": "ep45-bee-yard",
    "title": "Keep the Man With No Clock Away",
    "made_for_kids": False,
    "premise": "In a harbour town everyone has a small round dial over their head that counts down to their next hug. The narrator's has always been blank. His girlfriend Lena keeps bees in a hill yard he has never entered, and her dial starts counting hours toward noon on Saturday while a man who floats a hand above the grass stands two hives nearer each day.",
    "twist": "Lena's dial was never counting down to someone else. It was counting down to the narrator: every time he nearly hugged her goodbye at the gate it dropped to seconds, and every time he only waved it jumped back up. His own dial was blank because it was waiting for him to decide.",
    "world": "A harbour town on a sunny hill in early summer: a wooden ferry pier and quay below, and above it a dry-stone bee yard with twelve white hives, a small shed with a veil board, one wooden gate and the sea far down the slope.",
    "key_color": "#ff86b8",
    "gap": 0.12,
    "tail": 0.25,
    "fade_out": False,       # the last frame stays bright so the loop cuts straight into S00
    "fade_in": False,       # frame 1 is already the picture (opening recipe v1)
    "voice": {"voice": "am_adam", "tempo": 1.03, "rate": 1.45},
    "phonemes": {"Thursday": "θˈɜɹzdA"},
    "look": {"flash_safe": True, "polish": {"hold": ["S00a"], "quiet": [["L55", "L58"], ["L66", "L68"]]}, "fog": "#bcd6ea", "fog_density": 0.0035, "fog_start": 8.0, "sky": "#9cc8ea", "sky_strength": 1.0,
             "exposure": 0.0},
    "grade": {"shadows": [0.0, 0.0, 0.02], "highlights": [0.03, 0.015, -0.02], "saturation": 1.05, "contrast": 1.03,
              "vignette": 0.22, "bloom": 0.25, "grain": 0.008},
    "cast": cast,
    "lines": lines,
    "shots": shots,
}

# ---- acting, from each shot's placements
from blocky import timeline  # noqa: E402

voice = json.loads((HERE.parent / "voice-timings.json").read_text())
draft = dict(story, name="ep45-bee-yard")
tl0 = timeline.build(draft, voice)
at = timeline.resolver(tl0["lines"], tl0["duration"])

entries = {w: [] for w in cast}
seq = [0]


def put(who, ref, key):
    seq[0] += 1
    entries[who].append((at(ref), seq[0], {"at": ref, **key}))


prev_end, visible = {}, {}
for w in cast:
    put(w, -1.0, {"pos": [0.0, 0.0, -50.0], "hidden": True})
    prev_end[w] = [0.0, 0.0, -50.0]
    visible[w] = False
DEF = dict(arms=[0, 0], side=[0, 0], head=[0, 0], lean=0, look=[0, 0], expr="neutral")
for i, sid in enumerate(ids):
    ref = REF[sid]
    pl = PL[sid]
    for w in cast:
        if w in pl:
            p = pl[w]
            if i:
                put(w, ref, {"pos": list(prev_end[w])})     # (the first shot has nowhere to walk from)
            k = {**DEF, "yaw": p["yaw"], "pos": list(p["pos"]), "blend": 0.0, "hidden": False}
            for a in ("arms", "side", "head", "lean", "look", "expr", "blink"):
                if a in p:
                    k[a] = p[a]
            put(w, ref, k)
            prev_end[w] = list(p["to"]) if p.get("to") else list(p["pos"])
            visible[w] = True
        elif visible[w]:
            put(w, ref, {"pos": list(prev_end[w]), "hidden": True, "blend": 0.0})
            visible[w] = False
for w, ref, attrs in EX:
    k = dict(attrs)
    put(w, ref, k)
for w in cast:
    entries[w].sort(key=lambda e: (e[0], e[1]))
acting = {w: [e[2] for e in entries[w]] for w in cast}
for w, a, b, amt in MOUTH:
    acting[w].append({"from": a, "to": b, "mouth": [amt, amt], "flap": True})
    acting[w].sort(key=lambda k: at(k["from"]) if "from" in k else at(k["at"]))
story["acting"] = acting
story["cues"] = CUES

# ---- sound
sfx = []


def fx_(at_, kind, db, **kw):
    sfx.append({"at": at_, "kind": kind, "db": db, **kw})


for ref in ("L02+0.1", "L03+0.1", "L07.1", "L11+0.1", "L56.1"):
    fx_(ref, "chime", -19, dur=1.9)
# (the quiet decorative dial clicks were cut 2026-11-03: sound budget)
for ref in ("L54.1", "L54.1+0.4", "L54.1+0.8"):
    fx_(ref, "click", -17)
fx_("L13.3", "latch", -16)
fx_("L39", "latch", -18)
for k, off in enumerate((0.15, 1.2, 2.3)):
    fx_(f"L40+{off}", "puff", -17, dur=0.6)
fx_("L01.4", "sting", -8, dur=1.6, keep=True)     # the hit on "LOVE"
fx_("L44", "sting", -11, dur=2.4, keep=True)
fx_("L52.3+0.2", "whoosh", -17)
fx_("L55+0.35", "thud", -26)
# quality lift 2026-11-03: recorded latch, whoosh and thud where beats land
fx_("L15>-0.4", "latch", -20)           # the gate, each evening
fx_("L23", "thud", -30)                  # someone in the last row
fx_("L45", "thud", -28)                  # floating in the gateway
fx_("L52+0.1", "thud", -24)              # the veil comes off its hook
fx_("L68", "latch", -18)                 # at the gate now
fx_("L63", "chime", -26, dur=1.6)
sfx.sort(key=lambda e: 0)
story["music"] = {
    "root": 57, "mode": "mixolydian", "bpm": 92, "seed": 45,
    "sections": [
        {"at": 0, "voices": ["drone"], "energy": 0.3},
        {"at": "L02", "voices": ["drone", "pluck"], "energy": 0.4},
        {"at": "L12", "voices": ["drone", "pluck"], "energy": 0.35},
        {"at": "L19", "voices": ["drone", "pluck", "tick"], "energy": 0.4},
        {"at": "L23", "voices": ["drone", "tick"], "energy": 0.25},
        {"at": "L25", "voices": ["drone", "pluck", "tick"], "energy": 0.35},
        {"at": "L40", "voices": ["drone", "tick"], "energy": 0.3},
        {"at": "L44", "voices": ["drone"], "energy": 0.25},
        {"at": "L49", "voices": ["drone", "tick"], "energy": 0.35},
        {"at": "L54", "voices": ["drone", "tick"], "energy": 0.4},
        {"at": "L56", "voices": ["drone", "pluck_hi", "pad"], "energy": 0.65},
        {"at": "L60", "voices": ["drone", "pluck"], "energy": 0.4},
        {"at": "L66", "voices": ["drone", "pluck_hi", "pad"], "energy": 0.6},
    ]}
story["sound"] = {
    "floor": "grass", "steps_db": -26, "rev": 7,
    "ambience": [
        {"kind": "beehum", "from": 0, "to": "L02", "lufs": -42},
        {"kind": "gulls", "from": "L02", "to": "L15", "lufs": -41},
        {"kind": "wind", "from": "L02", "to": "L12", "lufs": -44},
        {"kind": "beehum", "from": "L15", "to": "L59", "lufs": -40},
        {"kind": "beehum", "from": "L46", "to": "L50", "lufs": -35},
        {"kind": "crickets", "from": "L38", "to": "L38.3+0.4", "lufs": -38},
        {"kind": "wind", "from": "L40", "to": "L59", "lufs": -42},
        {"kind": "beehum", "from": "L61", "to": "L66", "lufs": -42},
        {"kind": "gulls", "from": "L69", "to": "end", "lufs": -43},
    ],
    "sfx": sfx,
    "music_drops": [
        {"from": "L23-0.6", "to": "L23+0.25", "keep": ["sting"]},
        {"from": "L44-0.6", "to": "L44+0.45", "keep": ["sting"]},
        {"from": "L54-0.5", "to": "L54+0.2", "keep": ["click"]},
    ]}
story["clip_ok"] = [f"hpuff{i}" for i in range(12)] + ["lbee0", "lbee1", "lbee2"]
story["phonemes"] = {"Thursday": "θˈɜɹzdA"}
OUT.write_text(json.dumps(story, indent=1, ensure_ascii=False) + "\n")
print("wrote", OUT, f"({len(shots)} shots, {tl0['duration']} s)")
