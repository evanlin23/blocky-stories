"""Writes ../story.json for ep33 "chairlift" (script.md, redo, writer 2026-11-02).

Run from anywhere: python stories/ep33-chairlift/generator/make_story.py
The words are in lines.json next to this file (every line of the script, exactly). Everything else is here: the cast,
the shots and their cameras, the acting, the cues set.py reads, the effects, the score and the sound.

Places (geometry.py is shared with set.py): the line runs up +y from the bottom wheel at the origin to the top wheel at
y = 128; the up rope is at x = +1.8, the down rope at x = -1.8. A rider is keyed by where its feet-root is, so every
ride is a few `pos` keys that geometry.rider() works out. Shots that ride use "follow" and their positions are metres
from that rider's feet-root. The ridge top is z = 39.5; the long bench is at y = 137 facing the sunrise (+y); its left
end (x < -2) has no backrest, and that's where Gran sits facing the town (yaw 0 faces -y).
"""
import json
import math
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import geometry as G  # noqa: E402

OUT = HERE.parent / "story.json"
PKG = json.loads((HERE.parent / "package.json").read_text())
lines = json.loads((HERE / "lines.json").read_text())

# ---------------------------------------------------------------------------------------------------- gaps
# line id -> seconds of air after it. P01 (0.7 s) is the music_drops hole before the scare. The loop tail is 0.5 s
# so the bull wheel's clack lands 0.25 s after "SPRING." and still clears the cut.
GAPS = {"L12": 0.2, "L20": 0.1, "L21": 0.35, "L32": 0.3, "L36": 0.25}
LOOP = 0.5
for ln in lines:
    if ln["id"] in GAPS:
        ln["gap"] = GAPS[ln["id"]]

# ---------------------------------------------------------------------------------------------------- cast
cast = {
    "me": {"age": "adult", "skin": "#f1c9a0", "shirt": "#1f3556", "pattern": "solid", "collar": "#162843",
           "pants": "#3b404c", "shoes": "#4a392c", "sleeves": "long", "hair": "cap", "hair_c": "#5a3b22",
           "hat": "beanie", "hat_c": "#efe3c8",
           "face": {"eyes": "round", "brows": True, "cheeks": "#e98d7a", "ink": "#1b1410"}},
    "bo": {"age": "adult", "skin": "#d8a578", "shirt": "#2f5a3a", "pattern": "knit", "pattern_c": "#264a30",
           "collar": "#244a2f", "pants": "#3b3a38", "shoes": "#2b241e", "sleeves": "long", "hair": "none",
           "hair_c": "#141414", "hat": "beanie", "hat_c": "#2b2b30", "width": 1.08,
           "face": {"eyes": "round", "brows": True, "ink": "#1a120e"}},
    "mr_pell": {"age": "adult", "skin": "#e3b896", "shirt": "#6a4a2e", "pattern": "solid", "collar": "#583c24",
                "pants": "#45454a", "shoes": "#7a3b2a", "sleeves": "long", "hair": "cap", "hair_c": "#f1f0ec",
                "hat": "none", "height": 1.09, "extras": ["scarf"], "extra_c": "#8a3a34",
                "face": {"eyes": "tired", "brows": True, "ink": "#2a2420"}},
    "gran": {"age": "adult", "skin": "#e8c4a4", "shirt": "#d6a73c", "pattern": "knit", "pattern_c": "#c99a2e",
             "collar": "#3d5f8f", "pants": "#4a4f58", "shoes": "#2c4a35", "sleeves": "long", "hair": "cap",
             "hair_c": "#a9a8a6", "hat": "beanie", "hat_c": "#4a5a66", "height": 0.93,
             "face": {"eyes": "lashes", "brows": True, "cheeks": "#e49a8a", "ink": "#2a2420"}},
    "laugher": {"age": "adult", "skin": "#e0b08a", "shirt": "#e8c13a", "pattern": "solid", "collar": "#c9a02a",
                "pants": "#3a3f4c", "shoes": "#2b241e", "sleeves": "long", "hair": "long", "hair_c": "#3a2616",
                "hat": "none", "extras": ["scarf"], "extra_c": "#c23b3b",
                "face": {"eyes": "lashes", "brows": True, "cheeks": "#e98d7a", "ink": "#1b1410"}},
    "ext1": {"age": "adult", "skin": "#c68e68", "shirt": "#d98c4c", "pattern": "solid", "collar": "#b87038",
             "pants": "#3b404c", "shoes": "#2b241e", "sleeves": "short", "hair": "spiky", "hair_c": "#1c1410",
             "hat": "none", "face": {"eyes": "round", "brows": True, "ink": "#1b1410"}},
    "ext2": {"age": "adult", "skin": "#f1c9a0", "shirt": "#5d8fb0", "pattern": "stripes", "pattern_c": "#7fa8c4",
             "collar": "#46708f", "pants": "#4a4f58", "shoes": "#2b241e", "sleeves": "short", "hair": "swoop",
             "hair_c": "#8a6a3a", "hat": "none", "face": {"eyes": "round", "brows": True, "ink": "#1b1410"}},
    "ext3": {"age": "adult", "skin": "#8a5a3c", "shirt": "#8a5db0", "pattern": "solid", "collar": "#6e4890",
             "pants": "#3b3a38", "shoes": "#2b241e", "sleeves": "short", "hair": "buzz", "hair_c": "#141010",
             "hat": "none", "face": {"eyes": "round", "brows": True, "ink": "#1b1410"}},
}

# ---------------------------------------------------------------------------------------------------- helpers
HEAD = 1.57   # a head centre above the feet-root, standing or seated
Z0 = 39.5     # the ridge top
SEATZ = Z0 - 0.05   # a bench sitter's feet-root


def c(*keys):
    return [list(k) for k in keys]


def mv(p0, t0, l0, p1=None, t1=None, l1=None):
    if p1 is None:
        return c([0, p0, t0, l0])
    return c([0, p0, t0, l0], [1, p1, t1 if t1 is not None else t0, l1 if l1 is not None else l0])


def front(hd, yaw, off=0.0, dist=1.0, dz=0.0, lens=32, push=0.0, lens2=None, aim_dz=0.0):
    """A camera in front of a face: hd the face's centre, yaw the way the person faces (0 = -y), off degrees round
    from straight on, dist metres away; push moves it in by that much over the shot."""
    a = math.radians(yaw + off)
    d = (math.sin(a), -math.cos(a))
    p0 = [round(hd[0] + d[0] * dist, 3), round(hd[1] + d[1] * dist, 3), round(hd[2] + dz, 3)]
    tg = [hd[0], hd[1], round(hd[2] + aim_dz, 3)]
    if not push and not lens2:
        return c([0, p0, tg, lens])
    p1 = [round(hd[0] + d[0] * (dist - push), 3), round(hd[1] + d[1] * (dist - push), 3), round(hd[2] + dz, 3)]
    return c([0, p0, tg, lens], [1, p1, tg, lens2 or lens])


def hd(p, dz=HEAD):
    return [p[0], p[1], dz]


def ride_cam(dx, dy, dz, tx, ty, tz, lens, dx2=None, dy2=None, dz2=None, tx2=None, ty2=None, tz2=None, lens2=None):
    """A camera relative to a rider's feet-root (shots with "follow")."""
    k0 = [0, [dx, dy, dz], [tx, ty, tz], lens]
    if dx2 is None and tx2 is None and lens2 is None:
        return [k0]
    k1 = [1, [dx if dx2 is None else dx2, dy if dy2 is None else dy2, dz if dz2 is None else dz2],
          [tx if tx2 is None else tx2, ty if ty2 is None else ty2, tz if tz2 is None else tz2], lens2 or lens]
    return [k0, k1]


# ---------------------------------------------------------------------------------------------------- places
BO = [1.25, -2.6]
ME = [0.3, -2.6]
VIEW = [-5.5, 1.8]        # where you stand at the viewer
BENCH_Y = 137.0
LA, E1, E2, E3 = [4.6, BENCH_Y], [3.2, BENCH_Y], [1.8, BENCH_Y], [0.4, BENCH_Y]
GB, MB = [-4.3, BENCH_Y], [-2.9, BENCH_Y]       # Gran and me at the open end of the bench
STAND = [-5.3, 135.4]                         # me, standing in front of Gran
TABLE = [-3.3, -8.0]

# ---------------------------------------------------------------------------------------------------- shots
SH = []


def shot(at, cam, **opt):
    SH.append((at, cam, opt))


# ---- the rule and the montage
shot(0, mv((8.0, 139.0, 40.3), (4.3, 137.0, 41.7), 40, (7.5, 138.7, 40.35), (4.3, 137.0, 41.8), 36), hand=0.002)
shot("L01.3", mv((10.5, -8.0, 1.3), (1.0, 24.0, 9.0), 30, (10.5, -8.0, 1.35), (1.0, 24.0, 9.4), 30), hand=0.002)
# the ridge is hidden from the deck by the slope, so the long lens looks from the hillside: the row of still figures
shot("L02", mv((-7.5, 116.0, 42.0), (2.6, 137.0, 40.9), 40, (-7.5, 116.5, 42.0), (2.6, 137.0, 40.95), 42), hand=0.002)
shot("L03", mv((-0.5, -6.4, 1.4), (-1.6, -2.3, 1.4), 30, (-0.5, -6.2, 1.4), (-1.5, -2.5, 1.4), 30), hand=0.002)
shot("L03.3", front(hd([-1.5, -3.5], 1.7), 0, 0, 2.4, 0.0, 34, push=0.15))
shot("L04", ride_cam(1.4, 5.0, 0.5, 0, 0, 1.2, 30), follow="bo", hand=0.003)
# ---- me and Gran
shot("L05", front(hd(ME), 0, 12, 2.6, 0.0, 32, push=0.1))
shot("L06", front(hd([-1.0, 1.2]), 180, -38, 3.4, 0.0, 32))
shot("L07", front(hd([-1.2, -2.6], 1.46), 90, -48, 2.4, 0.0, 32, push=0.1))
shot("L08", mv((-0.15, -4.4, 1.9), (-0.15, -2.6, 1.7), 40, (-0.15, -4.2, 1.9), (-0.15, -2.6, 1.7), 40), hand=0.002)
shot("L08.2", mv((-0.5, -5.0, 1.3), (-0.55, -2.6, 1.1), 30, (-0.5, -4.8, 1.3), (-0.55, -2.6, 1.1), 31), hand=0.002)
shot("L09", ride_cam(-1.0, 5.5, 1.0, 0, 0, 1.0, 32, dx2=-1.0, dy2=5.0), follow="gran", hand=0.003)
shot("L10", mv((-5.6, -12.0, 1.5), (-2.4, -4.0, 1.2), 27, (-5.4, -11.8, 1.5), (-2.4, -4.0, 1.2), 27), hand=0.002)
shot("L11", mv((-1.3, -11.8, 1.5), (-1.3, -8.0, 1.5), 32), hand=0.002)
shot("L12", front(hd(ME), 0, -10, 2.6, 0.0, 32))
shot("L12.3", mv((-3.4, -5.4, 1.7), (-3.8, -8.8, 0.95), 30, (-3.4, -5.6, 1.7), (-3.8, -8.8, 0.95), 31), hand=0.002)
# ---- the ridge, through the viewer
shot("L13", mv((-3.0, 0.6, 1.5), (-5.5, 2.0, 1.4), 32, (-3.1, 0.7, 1.5), (-5.5, 2.0, 1.4), 33), hand=0.002)
shot("L14", mv((2.4, 121.5, 41.6), (1.8, 137.0, 41.3), 52), hand=0.002, scope=True)
shot("L15", mv((-3.4, 123.0, 41.2), (-4.3, 137.0, 41.2), 130), hand=0.001, scope=True)
shot("L16", mv((-3.4, 123.4, 41.2), (-4.3, 137.0, 41.4), 150), hand=0.001, scope=True)
shot("L17", mv((-3.4, 123.4, 41.2), (-4.3, 137.0, 41.4), 150), hand=0.001, scope=True)
shot("L18", front(hd(BO), 0, 14, 2.5, 0.0, 32, push=0.1))
shot("L19", mv((-3.4, -5.4, 1.7), (-3.8, -8.8, 0.8), 28, (-3.5, -5.6, 1.7), (-3.8, -8.8, 0.8), 28), hand=0.002)
shot("L20", mv((-2.4, -5.5, 1.7), (-1.8, 10.0, 1.1), 35, (-2.4, -5.5, 1.7), (-1.8, 10.0, 1.15), 34), hand=0.002)
shot("L20.2", mv((-2.0, -3.5, 1.4), (-4.5, 0.5, 1.2), 30), hand=0.003)
shot("P01", mv((-3.4, 0.6, 1.5), (-5.5, 1.9, 1.4), 34), hand=0.001)
shot("L21", mv((-3.0, 132.0, 41.1), (-4.3, 137.0, 41.1), 75), hand=0.0, scope=True, cfill=1.3)
shot("L21.3", mv((-3.3, 5.0, 2.0), (-5.5, 1.8, 1.45), 36), hand=0.002)
# ---- the ride and the reveal
shot("L22", ride_cam(-0.5, 1.25, 1.35, -0.45, 0.45, 0.15, 24), follow="me", hand=0.0)
shot("L23", ride_cam(0.9, -0.8, 1.1, 1.6, 12.0, -0.2, 30), follow="me", hand=0.003, cfill=0.3)
shot("L24", ride_cam(0.6, 0.4, 1.7, -2.0, -55.0, -13.0, 50), follow="me", hand=0.003, cfill=0.3)
shot("L25", mv((-3.4, 133.5, 41.2), (-4.3, 137.0, 41.3), 45), hand=0.001)
shot("L26", mv((-4.0, 131.8, 41.3), (-4.8, 136.2, 41.1), 34), hand=0.001)
shot("L27", mv((-2.6, 140.4, 42.1), (-5.3, 135.4, 41.2), 40), hand=0.001)
shot("L28", mv((-4.3, 132.0, 41.1), (-4.3, 137.0, 41.1), 48), hand=0.001)
shot("L29", mv((-6.0, 112.0, 52.0), (-5.0, -35.0, 3.0), 40), hand=0.001)
shot("L30", mv((-4.3, 141.0, 43.4), (-4.3, 120.0, 38.0), 22), hand=0.001, cfill=0.05)
shot("L31", mv((-2.9, 126.0, 41.2), (-2.9, 137.0, 40.75), 72), hand=0.001)
shot("L32", mv((-4.2, 132.3, 41.2), (-4.4, 137.0, 41.2), 40), hand=0.001)
# ---- the turn and the sting
shot("L33", mv((-3.6, 131.6, 41.3), (-3.6, 137.0, 41.0), 34), hand=0.001)
shot("L34", mv((-3.6, 133.2, 41.9), (-3.6, 136.6, 40.6), 40), hand=0.001)
shot("L35", mv((-1.0, 30.0, 70.0), (0.4, -2.6, 0.0), 38), hand=0.001)
shot("L36", mv((-3.6, 130.6, 41.9), (-3.6, 137.0, 40.3), 30), hand=0.001)
# from the hillside again (the slope hides the ridge from the lake), nobody in front of the lens
shot("L37", mv((-14.0, 68.0, 46.0), (-3.4, 137.0, 41.0), 125, (-14.0, 68.0, 46.0), (-3.4, 137.0, 41.05), 128), hand=0.001, cfill=0.1)

shots, SID = [], {}
for i, (at, cam, opt) in enumerate(SH):
    sid = f"S{i + 1:02d}"
    s = {"id": sid, "cam": cam, "step": opt.get("step", 2)}
    if i:
        s["at"] = at
    for k_ in ("hand", "follow", "scope", "cfill"):
        if k_ in opt:
            s[k_] = opt[k_]
    shots.append(s)
    SID[at] = sid


# ---------------------------------------------------------------------------------------------------- acting
class Track:
    """One character's keys, in time order. jump=True moves them on the cut: two keys at one moment."""

    def __init__(self):
        self.keys, self.last = [], None

    def put(self, at, pos, jump=False, **kw):
        pos = [round(v, 3) for v in pos]
        if jump and self.last is not None:
            self.keys.append({"at": at, "pos": self.last})
            self.keys.append({"at": at, "pos": pos, "blend": 0.0, **kw})
        else:
            self.keys.append({"at": at, "pos": pos, **kw})
        self.last = pos
        return self

    def stand(self, at, pos, yaw, jump=False, **kw):
        return self.put(at, pos, jump, yaw=yaw, sit=False, perch=False, **kw)

    def perch(self, at, pos, yaw, jump=True, z=SEATZ, **kw):
        return self.put(at, [pos[0], pos[1], z], jump, yaw=yaw, sit=False, perch=True, **kw)

    def ride(self, at, line, y, s, jump=False, **kw):
        pos, yaw = G.rider(line, y, s)
        return self.put(at, pos, jump, yaw=round(yaw, 2), sit=True, perch=False, seat=s, **kw)

    def attr(self, at, **kw):
        self.keys.append({"at": at, **kw})
        return self

    def mouth(self, a, b, amt=0.6):
        self.keys.append({"from": a, "to": b, "mouth": [amt, amt], "flap": True})
        return self


NOWHERE = [0, -30]

# me: the far end of the bench at the start, the deck, the viewer, the ride, the ridge
M_ = Track()
M_.perch(0, MB, 0, jump=False, expr="neutral", head=[0, 0], arms=[0, 0], lean=0, look=[0, 0])
M_.stand("L02+0.5", ME, 0, jump=True, expr="neutral")
M_.attr("L05", expr="smirk", arms=[75, 75])
M_.stand("L06", [-1.0, 1.2], 180, jump=True, expr="neutral", arms=[0, 0])
M_.stand("L07", [0.3, -2.6], -90, jump=True)
M_.stand("L08", [0.25, -2.6], -90, jump=True)
M_.stand("L10", [-0.75, -8.0], -90, jump=True)
M_.attr("L11", expr="smirk", look=[0.9, 0.7])
M_.stand("L12", ME, 0, jump=True, expr="neutral", look=[0, 0])
M_.stand("L13", VIEW, 180, jump=True, expr="neutral", lean=18)
M_.attr("L19", expr="worried")
M_.stand("L20.2", [-2.8, -0.6], 180, jump=True, lean=0, expr="worried")
M_.put("L20.2>", [VIEW[0], VIEW[1]], yaw=180, sit=False, perch=False, run=True)
M_.attr("P01", lean=24)
M_.attr("L21.3", expr="terrified")
M_.ride("L22", "up", 3.2, -1, jump=True, expr="scared", lean=0)
M_.ride("L23", "up", 16.0, -1)
M_.ride("L24", "up", 38.0, -1, expr="worried")
M_.ride("L24>", "up", 52.0, -1)
M_.stand("L25", STAND, 180, jump=True, expr="worried")
M_.attr("L26", head=[-35, 0])
M_.attr("L27", expr="soft", head=[0, 0])
M_.perch("L31", MB, 0, jump=True, expr="soft")
M_.perch("L33", MB, 0, jump=True, expr="soft")

B_ = Track()
B_.stand(0, BO, 180, expr="grin", head=[0, -18], arms=[0, 0])
B_.ride("L04", "up", 4.0, -1, jump=True, expr="grin", arms=[0, 160])
B_.ride("L04>", "up", 9.0, -1)
B_.stand("L05", [-6.8, -6.0], 0, jump=True, expr="neutral", head=[0, 0], arms=[0, 0])
B_.stand("L18", BO, 0, jump=True, expr="neutral", side=[35, 35])
B_.stand("L19", [-6.8, -6.0], 0, jump=True, side=[0, 0])
B_.stand("L24", BO, 0, jump=True, expr="neutral")
B_.stand("L37", BO, 0, jump=True, expr="neutral")

PE = Track()
PE.stand(0, [0, -30], 0, hidden=True, expr="scared")
PE.ride("L03", "down", 2.6, 1, jump=True, hidden=False)
PE.ride("L03+0.5", "down", 0.8, 1)
PE.stand("L03+0.5", [-1.8, -1.2], 0, jump=True)
PE.put("L03.3", [-1.5, -3.5], yaw=0, sit=False)
PE.attr("L04", hidden=True)

G_ = Track()
G_.perch(0, GB, 0, jump=False, expr="neutral", head=[0, 0], arms=[0, 0])
G_.stand("L07", [-1.2, -2.6], 90, jump=True, expr="smile")
G_.stand("L08", [-0.55, -2.6], 90, jump=True, arms=[135, 135])
G_.stand("L08.2", [-0.55, -2.6], 0, jump=True, arms=[75, 75], expr="smile")
G_.ride("L09", "up", 2.4, -1, jump=True, arms=[0, 0])
G_.ride("L09>", "up", 14.0, -1)
G_.ride("L10", "down", 3.0, 1, jump=True)
G_.ride("L10+0.9", "down", 0.9, 1)
G_.stand("L10+0.9", [-1.8, -1.0], 0, jump=True)
G_.put("L10>", [-1.9, -5.6], yaw=0, sit=False)
G_.stand("L11", [-1.9, -8.0], 90, jump=True, expr="soft", arms=[105, 105])
G_.perch("L12.3", [-3.8, -8.78], 180, jump=True, z=-0.04, expr="smile", arms=[0, 0])
G_.perch("L13", GB, 0, jump=True, expr="neutral")
G_.attr("L15", blink=False)
G_.attr("L20", expr="asleep", blink=True)
G_.attr("L25.1", expr="neutral")
G_.attr("L26", expr="smile")
G_.attr("L28", expr="soft")
G_.attr("L32", expr="smile", head=[0, 14])

LA_ = Track()
LA_.perch(0, LA, 180, jump=False, expr="laugh", head=[0, 0], arms=[0, 0])
LA_.attr("L02", head=[0, 0])

E1_ = Track()
E1_.perch(0, E1, 180, jump=False, expr="smile", head=[0, 0], arms=[0, 0])
E1_.stand("L03", [1.4, -5.0], 0, jump=True, expr="smile")
E1_.perch("L03.3", E1, 180, jump=True, expr="smile")
E2_ = Track()
E2_.perch(0, E2, 180, jump=False, expr="neutral", head=[0, 0], arms=[0, 0])
E2_.stand("L03", [2.9, -4.4], 0, jump=True, expr="smile")
E2_.perch("L03.3", E2, 180, jump=True, expr="neutral")
E3_ = Track()
E3_.perch(0, E3, 180, jump=False, expr="neutral", head=[0, 0], arms=[0, 0])

acting = {"me": M_.keys, "gran": G_.keys, "bo": B_.keys, "mr_pell": PE.keys, "laugher": LA_.keys,
          "ext1": E1_.keys, "ext2": E2_.keys, "ext3": E3_.keys}

# ---------------------------------------------------------------------------------------------------- cues
cues = [
    {"at": 0, "name": "light", "look": "gold", "sky": "#5f93c0", "sky_s": 1.0, "ramp": 0.01},
    {"at": "L01.3", "name": "light", "look": "gold", "ramp": 1.2},
    {"at": "L13", "name": "light", "look": "pink", "ramp": 6.0},
    {"at": "L21", "name": "light", "look": "flat", "ramp": 0.4},
    {"at": "L22", "name": "light", "look": "gold", "ramp": 1.0},
    {"at": "L23", "name": "light", "look": "fog", "ramp": 2.5},
    {"at": "L25", "name": "light", "look": "gold", "ramp": 3.0},
    {"at": "L28", "name": "light", "look": "pink", "ramp": 6.0},
    {"at": "L30", "name": "light", "look": "pink", "sun_e": 0.8, "sky_s": 0.75, "cam": 0.2, "ramp": 0.5},
    {"at": "L31", "name": "light", "look": "pink", "ramp": 0.6},
    {"at": "L32", "name": "light", "look": "gold", "ramp": 4.0},
    {"at": "L36", "name": "light", "look": "base", "ramp": 2.0},
    # the time-lapse sky: smooth, slow, one direction; the light level never cycles
    {"at": 0, "name": "sunsweep", "az0": -25, "az1": 25, "dur": 3.0},
    {"at": "L24", "name": "sunsweep", "az0": 8, "az1": 150, "dur": 3.4},
    {"at": "L25", "name": "sunsweep", "az0": 150, "az1": 8, "dur": 0.3},
    {"at": "L35", "name": "sunsweep", "az0": 8, "az1": 110, "dur": 3.2},
    {"at": "L36", "name": "sunsweep", "az0": -20, "az1": 20, "dur": 3.0},
    {"at": 0, "name": "clouds", "on": True, "speed": 40.0},
    {"at": "L02>", "name": "clouds", "on": False},
    {"at": "L17", "name": "clouds", "on": True, "speed": 14.0},
    {"at": "L18", "name": "clouds", "on": False},
    {"at": "L23", "name": "clouds", "on": True, "speed": 40.0},
    {"at": "L25", "name": "clouds", "on": False},
    {"at": "L27", "name": "clouds", "on": True, "speed": 40.0},
    {"at": "L28", "name": "clouds", "on": False},
    {"at": "L30", "name": "clouds", "on": True, "speed": 40.0},
    {"at": "L31", "name": "clouds", "on": False},
    {"at": "L36", "name": "clouds", "on": True, "speed": 40.0},
    {"at": 0, "name": "mist", "on": False},
    {"at": "L23", "name": "mist", "on": True, "speed": 7.0},
    {"at": "L25", "name": "mist", "on": False},
    {"at": 0, "name": "upchairs", "on": False},
    {"at": "L02", "name": "upchairs", "on": True},
    {"at": "L03", "name": "upchairs", "on": False},
    {"at": "L06", "name": "upchairs", "on": True},
    {"at": "L07", "name": "upchairs", "on": False},
    {"at": "L37", "name": "upchairs", "on": True},
    {"at": 0, "name": "bunch", "on": False},
    {"at": "L20", "name": "bunch", "on": True},
    {"at": "L20.2", "name": "bunch", "on": False},
    {"at": 0, "name": "toproof", "on": True},
    {"at": "L02", "name": "toproof", "on": False},
    {"at": "L03", "name": "toproof", "on": True},
    {"at": "L20", "name": "phase", "u": 257.65, "when": 0.8},
    {"at": "L20.2", "name": "phase", "off": True},
    {"at": 0, "name": "sway", "amp": 1.4, "bias": 0.0, "dur": 0.1},
    {"at": 0, "name": "blanket", "on": False},
    {"at": "L08.2", "name": "blanket", "on": True, "who": "gran", "local": [0, -0.5, 1.12], "size": [1.05, 0.45, 0.2]},
    {"at": "L09", "name": "blanket", "on": True, "who": "gran", "local": [1.44, -0.05, 0.62], "size": [0.95, 0.55, 0.18]},
    {"at": "L10", "name": "blanket", "on": False},
    {"at": "L34", "name": "blanket", "on": True, "pos": [-3.6, 136.35, Z0 + 0.865], "size": [2.4, 0.8, 0.1]},
    {"at": 0, "name": "gull", "mode": "off"},
    {"at": "L16", "name": "gull", "mode": "hat"},
    {"at": "L25.1", "name": "gull", "mode": "fly", "dur": 1.4, "to": [2.5, 4.0, 3.0]},
    {"at": "L26", "name": "gull", "mode": "off"},
    {"at": "L37", "name": "summer"},
    {"at": "L21", "name": "open", "from": 0.9, "dur": 0.4},
]
fx = [
    {"at": "L21", "kind": "punch", "dur": 0.35, "zoom": 1.06},
]

# ---------------------------------------------------------------------------------------------------- sound
sfx = []
for ref in ("L22+0.7", "L23+0.5", "L23+1.9", "L24+0.6", "L24+1.9"):   # the chair clacks over each tower
    sfx.append({"at": ref, "kind": "click", "db": -20})
sfx += [
    {"at": "L09", "kind": "whoosh", "db": -24},
    {"at": "L21", "kind": "hit", "db": -6, "keep": True},
    {"at": "L22", "kind": "whoosh", "db": -20},
    {"at": "L24", "kind": "riser", "db": -26, "dur": 2.6},
    {"at": "L25.1", "kind": "whoosh", "db": -22},
    {"at": "L32", "kind": "bell", "db": -22},
    {"at": "L37>+0.25", "kind": "thud", "db": -16},
]

story = {
    "slug": "ep33-chairlift",
    "title": PKG["title"],
    "made_for_kids": False,
    "premise": ("In a lake town, one day at the top of the chairlift costs a year down at the lake, so people ride up to "
                "skip the things they don't want to sit through, and from the deck you can see them on the ridge, still "
                "as posts. I have never been up, because I don't want to miss a day. Gran goes up every morning with a "
                "blanket big enough for two, comes down for Sunday dinner, and every Sunday says I look older. Through "
                "the deck's old viewer she's the one person on the ridge facing away from the sunrise, and one Sunday "
                "she doesn't come down."),
    "twist": ("Gran isn't riding up the ridge to skip my life: she's the oldest in the valley, and a day at the top costs "
              "a year below, so she lives up there to stretch her last few years across the whole of mine, and every "
              "Sunday she said I looked older she meant it. I turn the rule once more and spend my own weeks beside her."),
    "world": ("An old two-seat chairlift by a still lake in spring: a timber station on a plank deck at the water's edge "
              "with a fixed sightseeing viewer at the rail, grey steel towers up a green pine slope to a bare ridge with "
              "a long wooden bench facing the sunrise, a town of small houses behind the deck, clear gold dawns and one "
              "morning of lake fog."),
    "voice": {"voice": "am_adam", "tempo": 1.03, "rate": 1.45},
    "key_color": "#ff8fb1",
    "gap": 0.12,
    "tail": LOOP,
    "look": {"fog": "#d9c2a8", "fog_density": 0.004, "fog_start": 12.0, "sky": "#9ec1d6", "exposure": 0.0,
             "flash_safe": True},
    "grade": {"shadows": [-0.005, 0.0, 0.04], "highlights": [0.035, 0.012, -0.02], "saturation": 1.04,
              "contrast": 1.05, "vignette": 0.25, "bloom": 0.3, "grain": 0.012},
    "phonemes": {"Gran": "ɡɹˈæn", "mum": "mˈʌm", "Bo": "bˈO", "Pell": "pˈɛl"},
    "cast": cast,
    "lines": lines,
    "shots": shots,
    "acting": acting,
    "cues": cues,
    "fx": fx,
    # A Aeolian at 72 bpm: a thin pad and a dry tick on every beat, like a clock. The heavy drone enters at L19 and holds.
    # On the ride the tick stops (it never reaches the top). From L32 the pad lifts to A major with a soft plucked bell
    # figure and the drone kept low under it.
    "music": {"root": 45, "mode": "minor", "bpm": 72, "seed": 33,
              "sections": [
                  {"at": 0, "voices": ["pad", "tick"], "energy": 0.3},
                  {"at": "L13", "voices": ["pad", "tick"], "energy": 0.4},
                  {"at": "L19", "voices": ["drone", "pad", "tick"], "energy": 0.5},
                  {"at": "L22", "voices": ["drone", "pad"], "energy": 0.5},
                  {"at": "L25", "voices": ["drone", "pad"], "energy": 0.35},
                  {"at": "L32", "mode": "major", "voices": ["drone", "pad", "pluck_hi"], "energy": 0.3},
              ]},
    "sound": {"floor": "wood", "steps_db": -90,
              "ambience": [
                  {"kind": "water", "from": 0, "to": "end", "lufs": -36},
                  {"kind": "hum", "from": 0, "to": "end", "lufs": -40},
                  {"kind": "gulls", "from": 0, "to": "end", "lufs": -42},
              ],
              "sfx": sfx,
              "music_drops": [{"from": "P01", "to": "L21", "keep": ["hit"]}]},
}
OUT.write_text(json.dumps(story, indent=1, ensure_ascii=False) + "\n")
print("wrote", OUT, f"({len(shots)} shots)")
