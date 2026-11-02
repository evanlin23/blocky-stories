"""Writes ../story.json for ep56 "marsh mill" (script.md). Run from anywhere:

    python stories/ep56-marsh-mill/generator/make_story.py

Words: lines.json (made by build_lines.py). Places (set.py's world, metres): the street runs along x, house fronts on
y = 6, people stand on the pavement at y = 4.6 facing +y (yaw 180). The shop where I try my key stands at (30, 25); the
track runs up +y along x = 30 to the windmill at (30, 95), its door on the -y side. Inside, positions are local to the
tower centre (MX, MY) = (30, 95); the door is at y - 3.0. The kitchen is at x = 200, the café inside at x = 150.
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

MX, MY = 30.0, 95.0
KX, KY = 200.0, 0.0      # kitchen
CX, CY = 150.0, 0.0      # café inside


def person(shirt, pants, skin, hair, hair_c, pattern="solid", pattern_c=None, shoes="#3a2f28", sleeves="long",
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


LASH = {"eyes": "lashes", "brows": True}
cast = {
    "me": person("#9a4a30", "#2c2f3a", "#e2b48a", "cap", "#4a3220", pattern="plaid", pattern_c="#2b3a5c", shoes="#2a2420",
                 extras=["apron"], extra_c="#c8bb9a", key="wheel"),
    "win": person("#2b3a5c", "#3a3c46", "#e6bf9a", "bun", "#f2efe8", collar="#c0392b", hat="beanie", hat_c="#c4bcac",
                  height=0.93, shoes="#4a3a30", key="crescent",
                  face={"eyes": "round", "brows": True}),
    "nb1": person("#e3b83a", "#5a4a3a", "#e9c3a0", "swoop", "#7a4a2a", face=LASH, key="diamond"),
    "nb2": person("#4f7fa8", "#6a5a44", "#b98a62", "spiky", "#23201c", key="cross"),
    "postman": person("#8a8d90", "#4a4d52", "#e2b48a", "none", "#555555", hat="ballcap", hat_c="#5a5d60", extras=["backpack"],
                      extra_c="#6a5a44", key="dots", collar="#6b6e72"),
    "ames": person("#8a6a4a", "#4a4036", "#d9ac84", "buzz", "#9a9a9a", pattern="knit", pattern_c="#6e533a", key="step"),
    "exwife": person("#3f7a4a", "#3a3a3a", "#e2b48a", "long", "#5a3a22", extras=["coat"], zip_c="#2a4a30", face=LASH, key="leaf"),
    "bride": person("#f1ece0", "#f1ece0", "#c9946a", "bun", "#1a1412", face=LASH, key="ring", collar="#e0d8c4"),
    "groom": person("#e6dfce", "#d8cfba", "#f0c7a6", "swoop", "#3a2a1c", extras=["tie"], extra_c="#8a4a36", key="triangle"),
    "p1": person("#c2584a", "#4a5568", "#f0c7a6", "cap", "#7a4a2a", key="bell", sleeves="short"),
    "p2": person("#7aa88c", "#6d5a48", "#c9946a", "long", "#4a2c1c", face=LASH, key="fish"),
    "p3": person("#d98a3a", "#3d4a66", "#8a5a3a", "bun", "#1a1412", face=LASH, key="wave"),
    "lifter": person("#4a2444", "#d9c9a6", "#a8774c", "cap", "#241620", shoes="#2a2220", height=1.38,
                     face={"eyes": "pin", "brows": False, "mouth": "flat", "eye_x": 0.27, "eye_scale": 1.9, "ink": "#1a1012"},
                     key=None),
}


def build_story(shots_, acting_, cues_, sound_, music_, fx_=None):
    story = {
        "slug": "ep56-marsh-mill",
        "title": "In this town, your key opens one door, and it's never your own",
        "made_for_kids": False,
        "premise": "In a marsh town everyone is born with a brass key on a cord round the neck. It opens exactly one door, never your own, and goes warm and gold only at the locked door it fits. The narrator's has never opened anything. His great-aunt Win's windmill door, open for thirty years, is locked on Monday, and each night a clean flour-free patch in the shape of two boots stands nearer behind her, in his old place by the sack hoist.",
        "twist": "The one door the narrator's key fits is Win's. He never found it because it was the only door in town never locked. She kept it open for thirty years so he'd never feel he had to come, then locked it and herself out so only his key could let her back in. The first line, a rule of exclusion, becomes the rule that someone else's door is where you are let in.",
        "world": "A small marsh town in late autumn: a sunny terraced street of painted doors, then flat reed beds and dykes under a big sky, a raised earth track, and a tarred black tower windmill with white sails, floury whitewashed rooms inside and an oak sack hoist.",
        "key_color": "#b48cff",
        "gap": 0.12,
        "tail": 0.25,
        "voice": {"voice": "am_adam", "tempo": 1.03, "rate": 1.45},
        "look": {"flash_safe": True, "fog": "#c4d2dc", "fog_density": 0.0035, "fog_start": 8.0, "sky": "#a9c8e0",
                 "sky_strength": 1.0, "exposure": 0.0},
        "grade": {"shadows": [0.0, 0.0, 0.025], "highlights": [0.03, 0.012, -0.02], "saturation": 1.04, "contrast": 1.04,
                  "vignette": 0.25, "bloom": 0.3, "grain": 0.008},
        "cast": cast,
        "lines": lines,
        "shots": shots_,
        "acting": acting_,
        "cues": cues_,
        "music": music_,
        "sound": sound_,
        "phonemes": {},
    }
    if fx_:
        story["fx"] = fx_
    return story


# ---------------------------------------------------------------------------------------------------- DSL
from blocky import timeline  # noqa: E402

voice = json.loads((HERE.parent / "voice-timings.json").read_text())
SH = []     # (id, n, at, cam, opts)
PL = {}     # id -> {who: placement}
EX = []     # (who, ref, attrs)
CUES = []
_draft = {"name": "ep56-marsh-mill", "lines": lines, "shots": [{"id": "S01", "cam": [[0, [0, 0, 1], [0, 1, 1], 30]]}],
          "cast": cast, "tail": 0.25, "gap": 0.12}
_tl0 = timeline.build(_draft, voice)
LN = {k: (v["onset"], v["end"]) for k, v in _tl0["lines"].items()}


def mid(lid, f=0.5):
    a, b = LN[lid]
    return f"{lid}+{round((b - a) * f, 2)}"


def cam(*keys):
    return [list(k) for k in keys]


def C(p, t, lens, p2=None, t2=None, lens2=None):
    if p2 is None and lens2 is None:
        return cam([0, list(p), list(t), lens])
    return cam([0, list(p), list(t), lens], [1, list(p2 or p), list(t2 or t), lens2 or lens])


def sh(sid, n, at, camera, place=None, **opt):
    SH.append((sid, n, at, camera, opt))
    PL[sid] = place or {}


def P(x, y, yaw=180, z=0.0, to=None, **kw):
    d = {"pos": [x, y, z], "yaw": yaw}
    if to:
        d["to"] = [to[0], to[1], z if len(to) < 3 else to[2]]
    d.update(kw)
    return d


def front(x, y, yaw, dist, z=1.5, off=0.0):
    """A camera spot `dist` m in front of someone at (x, y) facing yaw (0 faces -y), `off` degrees round."""
    a = math.radians(yaw + off)
    return [round(x + math.sin(a) * dist, 3), round(y - math.cos(a) * dist, 3), z]


def glow(who, ref, to=1.0, ramp=1.0):
    CUES.append({"at": ref, "name": "glow", "who": who, "to": to, "ramp": ramp})


def door(did, ref, to, ramp=0.6):
    CUES.append({"at": ref, "name": "door", "id": did, "to": to, "ramp": ramp})


def mi(x, y, z=0.0):
    return [MX + x, MY + y, z]


def through(tx, ty, tz, cz=1.55, cx=0.0, dist=1.3, lens=28):
    """From outside the mill door, through the small window at (0, -3.6, 1.55), aiming at mill-local (tx, ty, tz)."""
    return C([MX + cx, MY - 3.6 - dist, cz], [MX + tx, MY + ty, tz], lens)


MONT = {"S57": "day", "S58": "dusk"}
OPEN = 1.0

# placement shorthands
def nb(x, y=4.6, yaw=0.0, **kw):
    return P(x, y, yaw, **kw)


# ---- the street opener and the montage (S01 to S10)
sh("S01", 1, 0, C([-10.8, 0.9, 1.4], [-10.8, 4.4, 0.85], 25),
   {"nb2": P(-11.3, 4.3, 0, expr="grin", head=[0, 0]), "nb1": P(-10.3, 4.3, 0, expr="grin")}, hand=0.004)
glow("nb1", 0.3, 1.0, 1.0)
sh("S02", 1, mid("L01", 0.55), C([-10.8, 1.2, 1.3], [-10.8, 4.6, 0.95], 30, [-10.8, 1.5, 1.3], [-10.8, 4.6, 0.95], 30),
   {"nb1": P(-10.8, 4.5, 0, expr="grin")}, hand=0.004)
door("h2", mid("L01", 0.62), 1.0, 0.9)
glow("nb1", mid("L01", 0.95), 0.0, 1.0)
sh("S03", 2, "L02", C([-19.0, 0.8, 1.5], [-8.0, 4.6, 1.1], 20),
   {"p1": P(-15.5, 3.6, 40, expr="neutral"), "p2": P(-13.0, 4.4, 0), "p3": P(-10.4, 4.3, 20),
    "nb2": P(-8.2, 3.5, 330)}, hand=0.004)
glow("p3", "L02+0.15", 1.0, 1.0)
sh("S04", 2, mid("L02", 0.55), C([-5.0, 1.0, 1.1], [-5.0, 3.6, 0.5], 15),
   {"p1": P(-6.0, 3.6, 0), "p2": P(-5.0, 3.6, 0), "p3": P(-4.0, 3.6, 0)}, hand=0.003)
sh("S05", 3, "L03", C([10.8, 1.6, 1.3], [10.8, 4.6, 0.95], 26),
   {"postman": P(10.8, 4.5, 0)}, hand=0.004)
glow("postman", "L03+0.1", 1.0, 1.0)
door("cafe", "L03+0.95", 1.0, 0.8)
sh("S06", 3, mid("L03", 0.55), C([CX + 2.6, CY - 2.8, 1.5], [CX, CY + 0.3, 1.35], 26),
   {"postman": P(CX, CY + 0.8, 0, z=0.0, expr="smirk", arms=[40, 0])}, hand=0.004)
sh("S07", 4, "L04", C(front(-5.4, 4.6, 0, 2.6, 1.3), [-5.4, 4.6, 0.8], 26),
   {"ames": P(-5.4, 4.6, 0, expr="worried", arms=[25, 25])}, hand=0.004)
sh("S08", 5, "L05", C([-6.0, 0.9, 1.3], [-5.9, 4.4, 0.8], 26, [-6.0, 1.4, 1.3], [-5.9, 4.4, 0.8], 26),
   {"exwife": P(-6.2, 4.5, 15, expr="neutral")}, hand=0.004)
sh("S09", 6, "L06", C([-5.4, 0.8, 1.3], [-5.4, 4.6, 0.8], 24),
   {"ames": P(-5.9, 4.6, 0, expr="neutral"), "exwife": P(-4.9, 4.6, 0, expr="neutral")}, hand=0.004)
door("h3", "L06+0.5", 1.0, 0.9)
glow("exwife", "L06+1.8", 0.0, 1.0)
sh("S10", 7, "L07", C([5.4, 0.8, 1.3], [5.4, 4.6, 0.8], 24),
   {"bride": P(4.7, 4.4, 60, expr="grin"), "groom": P(6.2, 4.4, 300, expr="grin")}, hand=0.004)
glow("bride", "L07+0.2", 1.0, 1.0)

# ---- the narrator, then the mill (S11 to S20)
SHOP = (MX - 4.5, 24.5)
sh("S11", 8, "L08", C([MX - 2.5, 15.0, 1.6], [MX - 2.5, 60.0, 5.0], 22, [MX - 2.5, 16.0, 1.6], [MX - 2.5, 60.0, 5.0], 22),
   {"me": P(SHOP[0], 23.7, 180, arms=[0, 0], expr="neutral")}, hand=0.003)
sh("S12", 8, mid("L08", 0.55), C(front(SHOP[0], 23.7, 0, 1.2, 1.1), [SHOP[0], 23.7, 0.75], 34),
   {"me": P(SHOP[0], 23.7, 0, expr="neutral")}, hand=0.004)
sh("S13", 9, "L09", C([MX + 10, MY - 34, 2.0], [MX, MY, 6.0], 22, [MX + 8, MY - 30, 2.0], [MX, MY, 6.0], 22), {}, hand=0.003)
sh("S14", 9, mid("L09", 0.5), C(front(MX, MY - 4.2, 0, 1.7, 1.25), [MX, MY - 4.2, 0.95], 30),
   {"win": P(MX, MY - 4.2, 0, z=0.2, expr="smirk")}, hand=0.004)
sh("S15", 10, "L10", C(front(MX + 0.2, MY - 4.6, 0, 3.0, 1.35), [MX + 0.2, MY - 4.2, 1.1], 28),
   {"me": P(MX + 0.7, MY - 4.7, 0, z=0.2, expr="smirk"), "win": P(MX - 0.3, MY - 3.7, 0, expr="smirk", arms=[150, 0])}, hand=0.004)
sh("S16", 11, "L11", C([MX + 0.35, MY - 5.0, 1.0], [MX + 0.35, MY + 0.3, 0.6], 26), {}, hand=0.003)
sh("S17", 12, "L12", C([MX + 1.0, MY - 6.4, 0.9], [MX, MY - 4.4, 0.5], 30), {}, hand=0.004)
sh("S18", 13, "L13", C([MX + 0.7, MY - 5.6, 1.15], [MX + 0.35, MY - 3.47, 0.95], 36), {}, hand=0.002)
sh("S19", 13, mid("L13", 0.42), C([MX + 2.2, MY - 24, 1.6], [MX, MY - 12, 1.5], 34),
   {"me": P(MX, MY - 8.5, 0, to=(MX, MY - 17), expr="neutral", arms=[0, 0]), "win": P(MX, MY - 3.8, 0, z=0.0, expr="smirk")}, hand=0.006)
sh("S20", 14, "L14", C([MX + 5.0, MY - 30, 1.6], [MX, MY - 4, 1.5], 26, [MX + 3.0, MY - 26, 1.6], [MX, MY - 4, 1.5], 26), {}, hand=0.004)
sh("S20b", 14, mid("L14", 0.55), C([MX - 3.0, MY - 12, 1.2], [MX, MY - 4, 1.1], 28), {}, hand=0.004)

# ---- Monday to Friday (S21 to S38)
sh("S21", 15, "L15", C(front(MX + 0.3, MY - 4.4, 0, 2.7, 1.4), [MX + 0.3, MY - 4.4, 0.95], 28),
   {"me": P(MX + 0.3, MY - 4.4, 0, z=0.2, expr="worried")}, hand=0.004)
sh("S22", 15, mid("L15", 0.5), C(front(MX + 0.9, MY - 3.95, 0, 1.7, 1.2), [MX + 0.75, MY - 3.95, 1.05], 34),
   {"me": P(MX + 0.9, MY - 3.95, 0, z=0.2, expr="worried")}, hand=0.003)
sh("S23", 16, "L16", C([MX + 0.9, MY - 6.2, 0.45], [MX, MY - 4.3, 0.45], 30), {}, hand=0.005)
sh("S24", 17, "L17", C(front(MX, MY - 4.4, 0, 2.2, 1.5, 60), [MX, MY - 4.3, 1.4], 30),
   {"me": P(MX, MY - 4.4, 180, z=0.2, arms=[95, 0], expr="worried")}, hand=0.004)
sh("S25", 17, mid("L17", 0.55), through(0.0, 1.4, 1.1), {}, hand=0.003)
sh("S26", 18, "L18", through(-0.9, 0.5, 1.2, cx=0.1, dist=1.1), {"win": P(MX - 0.9, MY + 0.5, 180, arms=[40, 40], expr="neutral")}, hand=0.003)
sh("S27", 19, "L19", through(1.0, 0.3, 0.4, cz=1.95), {"win": P(MX - 0.9, MY + 0.5, 180, arms=[40, 40])}, hand=0.003)
sh("S28", 20, "L20", through(0.2, -0.1, 0.0, cz=2.25), {}, hand=0.003)
sh("S29", 21, "L21", C(mi(0.5, -1.9, 0.95), mi(0.6, -0.2, 0.75), 22), {}, hand=0.002)
sh("S30", 22, "L22", C(mi(0.3, -2.0, 1.7), mi(-0.8, 0.5, 1.4), 24),
   {"win": P(MX - 0.9, MY + 0.5, 180, arms=[40, 40])}, hand=0.004)
sh("S31", 23, "L23", through(-0.4, -0.2, 0.3, cz=2.2, cx=-0.05), {"win": P(MX - 0.9, MY + 0.5, 180, arms=[40, 40])}, hand=0.003)
sh("S32", 24, "L24", C(mi(-0.3, -1.6, 0.45), mi(-0.9, 0.0, 0.4), 30),
   {"win": P(MX - 0.9, MY + 0.5, 180, arms=[40, 40])}, hand=0.003)
sh("S33", 24, mid("L24", 0.5), C(mi(-1.0, -1.7, 1.3), mi(-0.9, 0.5, 1.2), 34),
   {"win": P(MX - 0.9, MY + 0.5, 20, arms=[40, 40], expr="smirk")}, hand=0.003)
sh("S34", 25, "L25", C([MX + 7, MY - 26, 1.8], [MX, MY, 5.5], 22), {}, hand=0.003)
sh("S35", 25, mid("L25", 0.5), C(front(MX, MY - 4.4, 0, 2.4, 1.45), [MX, MY - 4.4, 1.35], 30),
   {"me": P(MX, MY - 4.4, 0, z=0.2, expr="worried")}, hand=0.004)
sh("S36", 26, "L26", through(-0.9, 0.5, 0.5, cz=1.9), {}, hand=0.003)
sh("S37", 27, "L27", C([MX + 0.6, MY - 5.0, 1.2], [MX + 0.45, MY - 3.64, 1.1], 30), {}, hand=0.004)
sh("S38", 28, "L28", through(0.7, 0.3, 0.5, cz=1.9), {}, hand=0.003)

# ---- the torch, the kitchen, the fog, the reveal (S39 to S56)
sh("S39", 29, "L29", C([MX + 2.6, MY - 9.6, 1.7], [MX, MY - 3.8, 1.3], 28),
   {"me": P(MX + 0.4, MY - 5.8, 180, expr="worried")}, hand=0.006)
sh("S40", 30, "L30", through(0.4, 3.0, 1.6, cz=1.6, dist=1.1, lens=26), {}, hand=0.003)
sh("S41", 31, "L31", through(0.4, 3.0, 1.6, cz=1.6, dist=1.1, lens=26), {}, hand=0.003)
sh("S42", 32, "L32", through(0.4, 3.0, 2.0, cz=1.7, dist=1.2, lens=26), {}, hand=0.003)
sh("S43", 33, "L33", C([KX, KY - 1.4, 1.35], [KX, KY + 1.4, 1.15], 26),
   {"me": P(KX, KY + 1.4, 0, arms=[75, 0], expr="neutral", blink=False)}, hand=0.003)
sh("S44", 34, "L34", C([MX + 1.5, MY - 20, 1.5], [MX, MY - 3, 2.5], 22),
   {"me": P(MX, MY - 11, 180)}, hand=0.004)
sh("S45", 35, "L35", C([MX, MY - 1.9, 1.9], [MX, MY + 3.4, 2.4], 30), {}, hand=0.0)
CUES.append({"at": "L35", "name": "moon", "to": 1.0, "ramp": 2.0})
sh("S46", 35, mid("L35", 0.6), C(mi(0.0, -2.2, 1.55), mi(0.0, -4.3, 1.55), 34),
   {"me": P(MX, MY - 3.95, 180, z=0.2, expr="scared")}, hand=0.002)
LIF = (MX + 0.2, MY - 0.1)
LIF2 = (MX + 0.05, MY - 1.7)
lift_up = dict(arms=[0, 0], side=[0, 0], head=[0, -20], expr="neutral", blink=False)
sh("S47", 36, "L36", C([MX + 0.3, MY - 2.95, 1.3], [MX + 0.2, MY - 0.1, 1.55], 14), {"lifter": P(*LIF, 0, **lift_up)}, hand=0.0)
sh("S48", 37, "L37", C([MX + 1.6, MY - 2.8, 0.2], [MX + 0.2, MY - 0.1, 1.9], 16, [MX + 1.4, MY - 2.8, 0.25], [MX + 0.2, MY - 0.1, 2.1], 16),
   {"lifter": P(*LIF, 0, **lift_up)}, hand=0.0)
sh("S49", 38, "L38", C([MX + 0.3, MY - 2.9, 0.5], [MX + 0.2, MY - 0.1, 2.4], 20, [MX + 0.3, MY - 2.9, 0.6], [MX + 0.2, MY - 0.1, 2.7], 20),
   {"lifter": P(*LIF, 0, **lift_up)}, hand=0.0)
sh("S50", 39, "L39", C([MX + 0.9, MY - 2.2, 2.0], [MX - 0.3, MY - 0.1, 2.8], 32), {"lifter": P(*LIF, 0, **lift_up)}, hand=0.0)
sh("S51", 40, "L40", C([MX + 2.7, MY - 1.0, 1.0], [MX + 0.05, MY - 1.7, 1.5], 14),
   {"lifter": P(*LIF2, 0, **lift_up)}, hand=0.0)
CUES.append({"at": "L40", "name": "bend", "to": 1.0, "ramp": 1.3})
sh("S52", 40, mid("L40", 0.55), C([MX, MY - 4.7, 1.55], [MX, MY - 3.0, 1.5], 30), {"lifter": P(*LIF2, 0, **lift_up)}, hand=0.0)
sh("S53", 41, "L41", C([MX - 0.2, MY - 7.0, 1.6], [MX - 0.4, MY - 4.0, 1.55], 30),
   {"lifter": P(*LIF2, 0, **lift_up), "me": P(MX - 0.9, MY - 4.2, 60, z=0.2, expr="scared")}, hand=0.002)
sh("S54", 41, mid("L41", 0.5), C([MX + 0.5, MY - 5.0, 1.15], [MX + 0.05, MY - 2.4, 1.2], 30), {"lifter": P(*LIF2, 0, **lift_up)}, hand=0.0)
sh("S55", 42, "L42", C([MX, MY - 4.5, 1.55], [MX, MY - 3.0, 1.5], 42), {"lifter": P(*LIF2, 0, **lift_up)}, hand=0.0)
sh("S56", 43, "L43", C(front(MX, MY - 4.6, 0, 2.0, 1.4), [MX, MY - 4.6, 1.15], 30),
   {"me": P(MX, MY - 4.6, 0, expr="scared", look=[0, -0.8])}, hand=0.003)

# ---- the loophole and the turn (S57 to S68)
sh("S57", 44, "L44", C([0.0, 1.0, 1.3], [0.0, 4.5, 0.8], 24), {"nb1": P(0.0, 4.5, 0, expr="grin")}, hand=0.004)
glow("nb1", "L44+0.1", 1.0, 1.0)
sh("S58", 45, "L45", C(front(MX, MY - 4.4, 0, 2.2, 1.5, 60), [MX, MY - 4.3, 1.4], 30),
   {"me": P(MX, MY - 4.4, 180, z=0.2, arms=[95, 0], expr="worried")}, hand=0.004)
sh("S59", 46, "L46", C([MX + 5.0, MY - 30, 1.6], [MX, MY - 4, 1.5], 26, [MX + 3.0, MY - 26, 1.6], [MX, MY - 4, 1.5], 26), {}, hand=0.004)
sh("S60", 47, "L47", C(front(MX, MY - 4.6, 0, 2.1, 1.5), [MX, MY - 4.6, 1.45], 30),
   {"me": P(MX, MY - 4.6, 0, expr="wide")}, hand=0.003)
sh("S61", 48, "L48", C([MX + 0.5, MY - 7.8, 1.5], [MX + 0.5, MY - 4.0, 1.35], 22, [MX + 0.5, MY - 6.9, 1.5], [MX + 0.5, MY - 4.0, 1.4], 22),
   {"me": P(MX + 0.95, MY - 4.25, 320, z=0.2, expr="neutral"), "lifter": P(*LIF2, 0, **lift_up)}, hand=0.003)
glow("me", "L48+0.4", 1.0, 1.2)
glow("me", "L51+0.3", 0.0, 1.0)
sh("S62", 49, "L49", C([MX + 0.5, MY - 6.7, 1.5], [MX + 0.5, MY - 4.0, 1.42], 22),
   {"me": P(MX + 0.95, MY - 4.25, 320, z=0.2, expr="wide"), "lifter": P(*LIF2, 0, **lift_up)}, hand=0.003)
sh("S63", 50, "L50", C([MX + 0.6, MY - 5.3, 1.1], [MX + 0.55, MY - 3.9, 1.0], 22),
   {"me": P(MX + 0.95, MY - 4.25, 320, z=0.2)}, hand=0.002)
sh("S64", 51, "L51", C(mi(0.0, -0.4, 1.4), mi(0.0, -3.7, 1.2), 22),
   {"me": P(MX, MY - 4.0, 180, z=0.0, to=(MX + 0.1, MY - 2.2))}, hand=0.003)
door("mill", "L51", 1.0, 0.9)
sh("S65", 51, mid("L51", 0.55), C(mi(1.0, -2.1, 0.95), mi(0.2, -0.5, 0.35), 24),
   {"me": P(MX + 0.2, MY - 0.7, 180, to=(MX + 0.2, MY - 0.1))}, hand=0.003)
sh("S66", 52, "L52", C(mi(0.0, -2.9, 1.5), mi(0.2, 0.0, 1.3), 20),
   {"me": P(MX + 0.2, MY - 0.1, 0, expr="worried")}, hand=0.003)
sh("S67", 52, mid("L52", 0.5), C(mi(0.6, -1.5, 0.85), mi(0.2, -0.15, 0.25), 22),
   {"me": P(MX + 0.2, MY - 0.1, 0, expr="worried")}, hand=0.003)
sh("S68", 53, "L53", C(mi(0.9, 2.6, 1.35), mi(0.0, -3.4, 1.2), 22),
   {"me": P(MX + 0.2, MY - 0.1, 0, expr="worried")}, hand=0.003)
sh("S69", 54, "L54", C(mi(0.0, 1.6, 1.3), mi(0.0, -3.4, 1.15), 26),
   {"win": P(MX, MY - 3.45, 180, expr="smirk", arms=[0, 0])}, hand=0.003)
sh("S70", 55, "L55", C([CX + 1.0, CY - 2.8, 1.5], [CX, CY + 0.6, 1.5], 28),
   {"postman": P(CX, CY + 0.8, 0, expr="smirk", arms=[150, 0])}, hand=0.003)
sh("S71", 56, "L56", C([MX + 0.4, MY - 7.3, 1.45], [MX + 0.5, MY - 4.0, 1.25], 28),
   {"win": P(MX, MY - 3.6, 0, expr="smirk"), "me": P(MX + 1.1, MY - 4.9, 340, z=0.0, expr="neutral")}, hand=0.004)
glow("me", "L56", 1.0, 0.6)
sh("S72", 57, "L57", C(front(MX, MY - 3.6, 0, 1.9, 1.3), [MX, MY - 3.6, 1.22], 32),
   {"win": P(MX, MY - 3.6, 0, expr="smirk")}, hand=0.004)
sh("S73", 58, "L58", C([MX + 0.2, MY - 4.45, 0.98], [MX + 0.32, MY - 3.47, 0.95], 44), {}, hand=0.002)
sh("S73b", 58, mid("L58", 0.5), C(front(MX + 0.9, MY - 4.0, 0, 2.2, 1.2), [MX + 0.9, MY - 4.0, 0.85], 34),
   {"me": P(MX + 0.9, MY - 4.0, 0, z=0.2, expr="smirk")}, hand=0.002)
sh("S74", 59, "L59", C([MX - 2.5, 15.0, 1.6], [MX - 2.5, 60.0, 5.0], 22),
   {"me": P(SHOP[0], 23.7, 180, expr="neutral")}, hand=0.003)
sh("S75", 60, "L60", C([MX + 0.8, MY - 9.0, 1.2], [MX, MY - 5.5, 1.2], 28),
   {"win": P(MX, MY - 4.3, 0, z=0.2, to=(MX, MY - 12), expr="smirk")}, hand=0.004)
sh("S76", 61, "L61", C(front(MX + 0.6, MY - 4.5, 0, 3.0, 1.4), [MX + 0.6, MY - 4.5, 1.2], 26),
   {"win": P(MX + 0.05, MY - 4.45, 0, z=0.2, expr="smirk"), "me": P(MX + 1.05, MY - 4.45, 0, z=0.2, expr="smirk")}, hand=0.004)
glow("me", "L61+0.2", 0.0, 1.0)
sh("S77", 62, "L62", C(mi(0.0, -2.9, 1.55), mi(0.0, 0.5, 1.3), 20),
   {"me": P(MX + 0.95, MY + 0.15, 0, arms=[50, 50], expr="smirk"), "win": P(MX - 0.9, MY + 0.15, 0, arms=[50, 50], expr="smirk")}, hand=0.003)
sh("S78", 62, mid("L62", 0.5), C(mi(-0.9, -1.4, 1.3), mi(-0.9, 0.1, 1.2), 36),
   {"win": P(MX - 0.9, MY + 0.15, 0, arms=[50, 50], expr="smirk")}, hand=0.003)
sh("S79", 63, "L63", C([MX + 6.0, MY - 26, 1.7], [MX, MY - 4, 1.6], 26, [MX + 4.0, MY - 21, 1.7], [MX, MY - 4, 1.6], 26), {}, hand=0.004)
sh("S80", 64, "L64", C(front(MX + 0.5, MY - 4.4, 0, 2.5, 1.0), [MX + 0.5, MY - 4.4, 0.7], 30),
   {"win": P(MX + 0.05, MY - 4.4, 0, z=0.2, expr="smirk"), "me": P(MX + 0.95, MY - 4.4, 0, z=0.2, expr="smirk")}, hand=0.003)
sh("S81", 65, "L65", through(0.2, -0.1, 0.0, cz=2.25), {}, hand=0.003)
sh("S82", 65, mid("L65", 0.55), C([MX, MY - 4.95, 2.25], [MX + 0.2, MY - 0.1, 0.0], 28, [MX, MY - 4.6, 2.2], [MX + 0.2, MY - 0.1, 0.0], 28), {}, hand=0.0)

# ================================================================================================ the story
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
draft = dict(_draft, shots=shots)
tl1 = timeline.build(draft, voice)
at = timeline.resolver(tl1["lines"], tl1["duration"])

entries = {w: [] for w in cast}
seq = [0]


def put(who, ref, key):
    seq[0] += 1
    entries[who].append((at(ref), seq[0], {"at": ref, **key}))


prev_end, visible = {}, {}
for w in cast:
    put(w, 0, {"pos": [0.0, 0.0, -50.0], "hidden": True})
    prev_end[w] = [0.0, 0.0, -50.0]
    visible[w] = False
DEF = dict(arms=[0, 0], side=[0, 0], head=[0, 0], lean=0, look=[0, 0], expr="neutral")
for sid in ids:
    ref = REF[sid]
    pl = PL[sid]
    for w in cast:
        if w in pl:
            p = pl[w]
            put(w, ref, {"pos": list(prev_end[w])})
            k = {**DEF, "yaw": p["yaw"], "pos": list(p["pos"]), "blend": 0.0, "hidden": False}
            for a_ in ("arms", "side", "head", "lean", "look", "expr", "blink"):
                if a_ in p:
                    k[a_] = p[a_]
            put(w, ref, k)
            prev_end[w] = list(p["to"]) if p.get("to") else list(p["pos"])
            visible[w] = True
        elif visible[w]:
            put(w, ref, {"pos": list(prev_end[w]), "hidden": True, "blend": 0.0})
            visible[w] = False
for w in cast:
    entries[w].sort(key=lambda e: (e[0], e[1]))
acting = {w: [e[2] for e in entries[w]] for w in cast}

# ---- sound and music
sfx = []


def fx_(at_, kind, db, **kw):
    sfx.append({"at": at_, "kind": kind, "db": db, **kw})


for ref in (0.5, "L02+0.2", "L03+0.15", "L05+0.8", "L07+0.25", "L44+0.2"):
    fx_(ref, "chime", -22, dur=1.6)
fx_("L01+1.4", "door", -22)
fx_("L06+0.6", "door", -22)
fx_("L12+0.3", "latch", -22)
fx_("L16", "thud", -26)
fx_("L17+0.1", "knock", -16, pattern=[0, 0.3, 0.6], tone="hand")
fx_("L27+0.2", "creak", -28)
fx_("L28+0.8", "scrape", -26, distant=True)
fx_("L36", "sting", -12, dur=2.2, keep=True)
fx_("L40+0.4", "creak", -26)
fx_("L40+1.2", "breath", -30)
fx_("L26-0.3", "hit", -16, keep=True)
fx_("L48+0.4", "chime", -18, dur=1.8)
fx_("L50+0.5", "latch", -20)
fx_("L53+0.1", "creak", -20)
fx_("L52+1.0", "thud", -30)
fx_("L57", "chime", -26, dur=1.4)
fx_("L63", "chime", -26, dur=1.6)
fx_("L65+2.0", "sting", -24, dur=1.6)
music = {"root": 48, "mode": "harmonic", "bpm": 76, "seed": 56,
         "sections": [
             {"at": 0, "voices": ["pluck", "tick"], "energy": 0.4},
             {"at": "L15", "voices": ["pluck", "tick"], "energy": 0.35},
             {"at": "L25", "voices": ["drone", "pluck"], "energy": 0.3},
             {"at": "L34", "voices": ["drone", "tick"], "energy": 0.3},
             {"at": "L36", "voices": ["drone"], "energy": 0.25},
             {"at": "L44", "voices": ["drone", "pluck"], "energy": 0.35},
             {"at": "L53", "voices": ["drone", "pluck_hi", "pad"], "energy": 0.6},
             {"at": "L65", "voices": ["drone"], "energy": 0.2},
         ]}
sound = {
    "floor": "wood", "steps_db": -26,
    "ambience": [
        {"kind": "wind", "from": 0, "to": "L08", "lufs": -44},
        {"kind": "wind", "from": "L13", "to": "end", "lufs": -42},
        {"kind": "room", "from": "L16", "to": "L34", "lufs": -44},
        {"kind": "hum", "from": "L16", "to": "L24", "lufs": -40},
        {"kind": "drone", "from": "L25", "to": "end", "lufs": -38},
        {"kind": "hum", "from": "L62", "to": "L64", "lufs": -40},
    ],
    "sfx": sfx,
    "music_drops": [
        {"from": "L26-0.6", "to": "L26+0.1", "keep": ["hit"]},
        {"from": "L36-0.7", "to": "L36+0.2", "keep": ["sting"]},
        {"from": "L48-0.5", "to": "L48+0.35", "keep": ["chime"]},
    ]}
story = build_story(shots, acting, CUES, sound, music)
OUT.write_text(json.dumps(story, indent=1, ensure_ascii=False) + "\n")
print("wrote", OUT, f"({len(shots)} shots, {tl1['duration']} s)")
