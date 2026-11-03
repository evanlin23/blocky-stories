"""Writes ../story.json for ep58 "swing bridge" (script.md). Run from anywhere:

    python stories/ep58-swing-bridge/generator/make_story.py

The words are in lines.json (made by build_lines.py). Here: the cast, the shots (ids follow the script's table S01 to
S91, with a letter on the shots split to keep every cut under about 2.3 s), who stands where in each shot, the glow
levels of every pair of hands, the Reach's model per shot, the score and the sound.

Places (set.py's coordinates). The bridge: the span runs along +x from the far bank (x 0) to the pivot (x 18.3), the
cabin on the near bank (x 19 to 22.6, y 2 to 5.3), the window at x 19.5 to 20.9 and the door at x 21.5 to 22.2, both
in the y = 2 wall; the path at x 21.6 runs south. Cinema x 100, office 130, house window 160, sofa 190, street 220,
kitchen 250, bedroom 350; the new road bridge at y 120.
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
for _l in lines:
    if _l["id"] in ("L11", "L20", "L23", "L53", "L61"):
        _l["tempo"] = 0.8 if _l["id"] == "L20" else 0.9
    for _c in _l["chunks"]:      # spoken in full so Whisper hears them (captions keep the contraction)
        _c[1] = _c[1].replace("They'd bolted", "They had bolted").replace("I'd thought", "I thought").replace("sat on the", "sat on that").replace("in the fog", "in a fog")
    if False:
        pass      # slower so Whisper hears "the" and "they'd"/"I'd" (word check)

# ---------------------------------------------------------------------------------------------------- cast


def person(shirt, pants, skin, hair, hair_c, pattern="solid", pattern_c=None, shoes="#2c2622", sleeves="long",
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


LASH = {"eyes": "lashes", "brows": True, "cheeks": "#e98d7a"}
cast = {
    "me": person("#2f7f86", "#2a2f3a", "#e9c3a0", "cap", "#5a3a26", pattern="knit", pattern_c="#efe4c8", shoes="#2a2a2e"),
    "mec": person("#1f2a44", "#2a2f3a", "#e9c3a0", "cap", "#5a3a26", extras=["coat"], zip_c="#3a4666", shoes="#2a2a2e"),
    "emrys": person("#26324a", "#2f3340", "#d8ae88", "cap", "#8a8d92", collar="#b8913e", shoes="#2a2622",
                    face={"eyes": "tired", "brows": True}, flatcap="#34493b", moustache="#777a80"),
    "ada": person("#6b3a5a", "#33303a", "#e3b894", "long", "#8a3a22", extras=["coat"], zip_c="#8a5a78", face=LASH),
    "doc": person("#2f5a3e", "#2f3340", "#d9a77c", "cap", "#3a2a22", extras=["coat"], zip_c="#244a30", hat="hoodopen",
                  hat_c="#2f5a3e", face=LASH),
    "t1": person("#a8683a", "#3a3d46", "#c9946a", "spiky", "#2a1a14", extras=["coat"], zip_c="#7a4a2a"),
    "t2": person("#c9a23a", "#4a4f5c", "#f0c7a6", "bun", "#7a4a2a", extras=["coat"], zip_c="#9a7a22", face=LASH),
    "off": person("#6a6e76", "#5a5e66", "#e2b48a", "cap", "#2a2622", extras=["tie"], extra_c="#8a2a30", collar="#e8e8e8"),
    "cA": person("#d0a030", "#4a4f5c", "#d9a77c", "long", "#3a2418", face=LASH),
    "cB": person("#3a5a7a", "#3a3d46", "#e2b48a", "swoop", "#6a4a2a", pattern="stripes", pattern_c="#e8e0d0"),
    "pk": person("#6a5a4a", "#3a3d46", "#e2b48a", "cap", "#2a2622", extras=["coat"], zip_c="#4a3d30"),
    "hh": person("#d86a20", "#3a3d46", "#d0a07a", "cap", "#2a2622", hardhat=True),
}
GLOWSET = tuple(cast)

# ---------------------------------------------------------------------------------------------------- DSL
SH = []
PL = {}
EX = []
MOUTH = []
CUES = []


def hd(x, y, z=0.0, h=1.56):
    return (x, y, z + h)


def P(x, y, yaw=0, z=0.0, to=None, **kw):
    d = {"pos": [x, y, z], "yaw": yaw}
    if to:
        d["to"] = [to[0], to[1], z if len(to) < 3 else to[2]]
    d.update(kw)
    return d


def cam(*keys):
    return [list(k) for k in keys]


def mv(p0, t0, l0, p1=None, t1=None, l1=None):
    if p1 is None:
        return cam([0, list(p0), list(t0), l0])
    return cam([0, list(p0), list(t0), l0], [1, list(p1), list(t1 if t1 is not None else t0), l1 if l1 is not None else l0])


def fc(face, yaw, off, dist, lens, rise=0.12, el=0.0, push=0.0, lens2=None):
    """A camera in front of a face. yaw = the way the person faces (0 faces -y); off = degrees round from straight on;
    rise puts the face that fraction of the frame's height above the middle (out of the caption band)."""
    a = math.radians(yaw + off)
    d = (math.sin(a), -math.cos(a))
    drop = rise * dist * 24.0 / lens
    p0 = [round(face[0] + d[0] * dist, 3), round(face[1] + d[1] * dist, 3), round(face[2] + el, 3)]
    tg = [face[0], face[1], round(face[2] - drop, 3)]
    if not push and not lens2:
        return cam([0, p0, tg, lens])
    p1 = [round(face[0] + d[0] * (dist - push), 3), round(face[1] + d[1] * (dist - push), 3), round(face[2] + el, 3)]
    return cam([0, p0, tg, lens], [1, p1, tg, lens2 or lens])


def sh(sid, n, at, camera, place=None, look="day", glow=None, hand=0.004, **opt):
    c0 = camera[0][1]
    if 19.0 < c0[0] < 22.9 and 2.3 < c0[1] < 5.2:      # a camera inside the small cabin: widen the lens
        camera = [[k[0], k[1], k[2], round(k[3] * 0.7, 1)] for k in camera]
    SH.append((sid, n, at, camera, dict(opt, look=look, glow=glow or {}, hand=hand)))
    PL[sid] = place or {}


def ex(who, ref, **attrs):
    EX.append((who, ref, attrs))


def talk(who, a, b, amt=0.7):
    MOUTH.append((who, a, b, amt))


def lvl(key, ref, level, ramp=1.0):
    CUES.append({"at": ref, "name": "lvl", "key": key, "level": level, "ramp": ramp})


B, M, F, D = 1.0, 0.6, 0.2, 0.0
SIT = dict(sit=True)
ARMS0 = dict(arms=[0, 0], side=[0, 0])
CAB_SEAT = 0.02
E_POS = (21.75, 3.6)           # Emrys on his stool
ME_CRATE = (20.25, 3.55)       # me on the crate by the stove
HM = {"look": "cab_eve"}
emr = lambda yaw=-25, **kw: P(E_POS[0], E_POS[1], yaw, z=CAB_SEAT, **{**dict(sit=True, arms=[30, 30], side=[0, 0], expr="neutral"), **kw})
mecr = lambda yaw=-90, **kw: P(ME_CRATE[0], ME_CRATE[1], yaw, z=-0.09, **{**dict(sit=True, expr="neutral"), **kw})

def ins(after):
    item = SH.pop()
    i = [x[0] for x in SH].index(after)
    SH.insert(i + 1, item)


# ============================================================================================ the shots
# ---- the hook and the montage (S01 to S09)
sh("S01", 1, 0, mv([21.6, -7.4, 1.7], [21.6, -1.2, 1.75], 46, [21.6, -7.0, 1.7], [21.6, -1.2, 1.75], 46),
   {"doc": P(21.6, -0.3, 0, to=(21.6, -1.5), expr="neutral"), "t1": P(20.9, 1.0, 0, to=(20.9, -0.1), expr="neutral"),
    "t2": P(22.3, 1.2, 0, to=(22.3, 0.0), expr="neutral")}, look="day", glow={"doc": B, "t1": M, "t2": M}, hand=0.003,
   sun=(10, 25, 3.2, "#ffd9a0"), fill_k=1.5)
sh("S02", 1, "L01.2", mv([21.0, -1.7, 1.1], [21.0, 0.5, 1.12], 27, [20.95, -1.5, 1.1], [21.0, 0.5, 1.12], 27),
   {"t1": P(21.0, 0.5, 0, expr="neutral", arms=[78, 78], side=[-12, -12])}, glow={"t1": B}, hand=0.004, sun=(10, 25, 0.5, "#ffd9a0"), sky_k=0.55, fill_k=0.5)
sh("S03", 2, "L02", fc(hd(100.0, 3.0, -0.06), 0, 12, 3.1, 40), {"doc": P(100.0, 3.0, 0, z=-0.06, sit=True, expr="worried", arms=[70, 70], side=[0, 0], head=[0, 8])},
   look="cinema", glow={"doc": B})
sh("S04", 3, "L03", mv([104.0, 6.2, 2.4], [99.2, 1.6, 0.95], 28, [103.7, 6.0, 2.3], [99.2, 1.6, 0.95], 28),
   {"doc": P(100.0, 3.0, 0, z=-0.06, sit=True, arms=[70, 70], head=[0, 8], expr="worried"),
    "t1": P(98.3, 1.6, 0, z=-0.06, sit=True, head=[140, 0], expr="wide"), "t2": P(101.7, 1.6, 0, z=-0.06, sit=True, head=[-140, 0], expr="wide"),
    "cA": P(99.15, 0.2, 0, z=-0.06, sit=True, head=[150, 0], expr="wide"), "pk": P(100.85, 0.2, 0, z=-0.06, sit=True, head=[-150, 0], expr="wide")},
   look="cinema", glow={"doc": B, "t1": F, "t2": F, "cA": F, "pk": F}, hand=0.003)
sh("S05", 4, "L04", fc(hd(132.6, 4.4), 0, 14, 4.2, 38, rise=0.1), {"off": P(132.6, 4.4, 0, expr="neutral", arms=[0, 0], side=[10, 10], head=[0, 0])},
   look="office", glow={"off": B})
sh("S06", 4, "L04.2", fc((160.0, 0.05, 1.28), 0, 8, 2.5, 40, rise=0.05), {}, look="home", glow={}, hand=0.003)
sh("S07", 5, "L05", mv([190.0, -1.3, 1.65], [190.0, 3.6, 1.0], 30, [190.0, -1.0, 1.65], [190.0, 3.6, 1.0], 30),
   {"cA": P(189.0, 3.5, 0, z=-0.06, sit=True, arms=[75, 75], side=[0, 0], expr="neutral", head=[0, 0]),
    "cB": P(191.0, 3.5, 0, z=-0.06, sit=True, arms=[75, 75], side=[0, 0], expr="neutral", head=[0, 0])},
   look="sofa", glow={"cA": M, "cB": M}, hand=0.003)
sh("S08", 6, "L05.2", fc(hd(188.7, 3.5, -0.06), 0, 14, 2.6, 40, rise=0.1),
   {"cA": P(189.0, 3.5, 0, z=-0.06, sit=True, arms=[75, 75], side=[0, 0], expr="neutral", head=[-38, 0], look=[0.8, 0])},
   look="sofa", glow={"cA": M})
sh("S09", 6, "L06", fc(hd(220.0, 0.0), 0, 14, 3.1, 36, rise=0.04), {"pk": P(220.0, 0.0, 0, arms=[0, 0], side=[0, 0], expr="neutral")},
   look="street", glow={"pk": F})
lvl("pocket.pk", "L06+0.2", 0.9, 0.6)
# ---- me
STR = (21.6, -3.0)
sh("S10", 7, "L07", mv([21.6, -9.0, 1.55], [21.6, -3.0, 1.55], 30, [21.6, -8.6, 1.55], [21.6, -3.0, 1.55], 30),
   {"mec": P(STR[0], STR[1], 0, expr="neutral", arms=[0, 0], side=[0, 0])}, look="day", fill_k=1.6, sun=(14, 25, 3.0, "#ffd9a0"))
sh("S11", 8, "L08", mv([21.6, -5.6, 1.55], [21.6, -3.0, 1.3], 30), {"mec": P(STR[0], STR[1], 0, expr="neutral", arms=[95, 95], side=[-8, -8])},
   look="day", fill_k=1.6, sun=(14, 25, 3.0, "#ffd9a0"), hand=0.003)
sh("S11b", 8, "L08b", mv([24.0, -5.0, 1.7], [3.0, 0.9, 1.3], 30, [23.6, -4.8, 1.7], [3.0, 0.9, 1.3], 30), {}, look="day", reach="far",
   fd=0.03, fs=12, fogc="#d7e0e6", sun=(12, 25, 3.0, "#ffd9a0"), fill_k=1.4, hand=0.003)
ins("S11")
sh("S11c", 8, "L08b.2", mv([20.5, -2.2, 1.45], [1.4, 0.8, 1.2], 110, [20.2, -2.0, 1.45], [1.4, 0.8, 1.2], 110), {}, look="day", reach="far",
   fd=0.024, fs=10, fogc="#d7e0e6", sun=(12, 25, 3.0, "#ffd9a0"), fill_k=1.4, hand=0.003)
ins("S11b")
sh("S12", 9, "L09", mv([28.8, -3.9, 1.35], [24.6, -3.75, 1.05], 30, [28.5, -3.9, 1.35], [24.6, -3.75, 1.05], 30),
   {"ada": P(24.6, -4.25, 0, arms=[85, 85], side=[0, 0], expr="grin"), "mec": P(24.6, -3.3, 40, arms=[0, 0], side=[0, 0], expr="neutral")},
   look="day", glow={"ada": B}, crate=(24.6, -4.85, 0.95), fill_k=1.4)
sh("S13", 9, "L09.2", mv([21.4, -5.6, 1.6], [21.3, 1.0, 1.4], 30, [21.4, -5.3, 1.6], [21.3, 1.0, 1.4], 30), {"mec": P(20.4, -3.2, 0, arms=[0, 0], side=[0, 0], expr="neutral", head=[0, 6], lean=2),
   "emrys": P(22.0, 1.4, 0, expr="neutral", arms=[0, 0], side=[0, 0])},
   look="day", glow={"emrys": 0.3}, fill_k=1.6, sun=(14, 25, 3.0, "#ffd9a0"))
ex("mec", "L09.3", head=[0, -4], blend=0.3)
sh("S14", 10, "L10", mv([25.4, -2.6, 1.55], [21.2, 1.1, 1.55], 34, [25.0, -2.4, 1.55], [21.2, 1.1, 1.55], 34),
   {"emrys": P(21.1, 1.2, -20, expr="neutral", arms=[0, 0], side=[0, 0])}, look="day", glow={"emrys": 0.3}, fill_k=1.5)
sh("S15", 11, "L11", mv([14.8, 0.0, 0.5], [17.9, 0.1, 0.8], 22, [15.2, 0.0, 0.5], [17.9, 0.1, 0.8], 22),
   {"emrys": P(18.0, 0.2, 270, expr="neutral", arms=[0, 0], side=[0, 0])}, look="summer", glow={"emrys": 0.3}, hand=0.003, fill_k=2.0)
sh("S16", 11, "L11.2", mv([18.4, -5.0, 1.5], [14.5, 40.0, 6.5], 28, [18.4, -4.6, 1.5], [14.5, 40.0, 6.5], 28),
   {"emrys": P(18.6, -0.6, 0, expr="neutral", arms=[0, 0], side=[0, 0])}, look="dusk", glow={"emrys": 0.3}, hand=0.004, lk={"lamppost": 0.0}, fill_k=1.5)
sh("S17", 12, "L12", mv([250.8, -0.2, 1.5], [250.0, 3.4, 1.2], 21, [250.6, -0.1, 1.5], [250.0, 3.4, 1.2], 21),
   {"me": P(251.0, 3.4, 270, z=-0.06, sit=True, expr="neutral", arms=[40, 40]),
    "ada": P(248.9, 3.4, 90, z=-0.06, sit=True, expr="worried", arms=[70, 70])}, look="kitchen", glow={"ada": B})
sh("S18", 12, "L12.2", mv([250.7, 3.4, 1.25], [249.4, 3.4, 0.95], 17), {"ada": P(248.9, 3.4, 90, z=-0.06, sit=True, expr="worried", arms=[50, 50])},
   look="kitchen", glow={"ada": B}, hand=0.003, mug=(249.75, 3.4), glow_k=0.12)
sh("S19", 13, "L13", mv([250.0, -0.3, 1.5], [249.9, 4.0, 1.45], 22, [250.0, -0.2, 1.5], [249.9, 4.0, 1.45], 22),
   {"me": P(250.55, 4.0, 0, expr="neutral", arms=[0, 0], side=[0, 0]), "ada": P(249.3, 4.0, 90, expr="worried", arms=[0, 70], side=[0, 0])},
   look="kitchen", glow={"ada": B})
sh("S20", 14, "L14", mv([22.7, -4.0, 1.6], [21.9, 1.5, 1.5], 32, [22.5, -3.7, 1.6], [21.9, 1.5, 1.5], 32),
   {"emrys": P(21.85, 1.6, 0, expr="neutral", arms=[0, 0], side=[0, 0]), "mec": P(21.3, -1.6, 180, arms=[0, 0], side=[0, 0], expr="neutral")},
   look="day", glow={"emrys": M}, fill_k=1.6, sun=(14, 40, 3.0, "#ffd9a0"))
sh("S21", 15, "L15", mv([19.7, 4.9, 1.5], [21.6, 3.3, 1.4], 30, [19.8, 4.8, 1.5], [21.6, 3.3, 1.4], 30), {"emrys": emr(-25)}, look="cab_eve",
   glow={"emrys": M}, hand=0.003, sash=False)
sh("S22", 15, "L15.3", mv([20.7, 3.7, 1.32], [22.3, 3.7, 1.3], 30), {}, look="cab_eve", hand=0.002)
sh("S23", 16, "L16", mv([21.35, 2.95, 0.95], [21.75, 3.5, 0.8], 38), {"emrys": emr(-25)}, look="cab_eve", glow={"emrys": 0.45}, hand=0.002)
sh("S24", 16, "L16.2", mv([21.35, 2.95, 0.95], [21.75, 3.5, 0.8], 38), {"emrys": emr(-25)}, look="cab_eve", glow={"emrys": 0.3}, hand=0.002)
sh("S25", 17, "L17", mv([20.5, 2.7, 1.4], [21.75, 3.6, 1.1], 34), {"emrys": emr(-25)}, look="cab_dark", glow={"emrys": 0.2}, hand=0.002)
sh("S28", 19, "L19", mv([21.3, 3.3, 0.95], [20.2, 2.4, 0.6], 40), {}, look="cab_eve", hand=0.002, steam=True)
sh("S29", 19, "L19.2", fc(hd(21.75, 3.6, CAB_SEAT), -25, 30, 1.9, 40, rise=0.1), {"emrys": emr(0, head=[-50, 0])}, look="cab_eve", glow={"emrys": 0.45}, hand=0.003)
sh("S30", 20, "L20", mv([21.3, 4.5, 1.5], [20.1, 1.6, 1.45], 26, [21.2, 4.3, 1.5], [20.1, 1.6, 1.45], 26),
   {"emrys": P(20.2, 3.0, 0, arms=[0, 150], side=[0, 0], expr="neutral")}, look="dusk", glow={"emrys": 0.3}, sash=False, hand=0.003, sky_k=1.0,
   lk={"cab_lamp": 0.8, "cab_amb": 0.8})
sh("S31", 21, "L21", mv([21.6, -20.0, 1.55], [21.6, -12.0, 1.35], 30), {"mec": P(21.6, -12.0, 0, to=(21.6, -14.6), arms=[0, 0], side=[0, 0], expr="neutral")},
   look="dusk", glow={"mec": 0.0}, hand=0.004)
lvl("pocket.mec", "L21", 0.9, 0.5)
sh("S32", 21, "L21.2", fc((21.6, -12.0, 0.88), 0, -30, 1.35, 42, rise=0.0), {"mec": P(21.6, -12.0, 0, arms=[0, 0], side=[0, 0], expr="neutral")},
   look="dusk", hand=0.002)
# ---- the fog nights
sh("S33", 22, "L22", mv([15.4, -1.4, 1.25], [18.0, 0.8, 1.0], 38, [15.7, -1.2, 1.25], [18.0, 0.8, 1.0], 38), {}, look="nightfog", fd=0.05, hand=0.003)
sh("S34", 22, "L22.2", mv([16.4, -0.5, 1.45], [17.55, 0.8, 0.98], 45), {}, look="nightfog", prints=True, fd=0.05, hand=0.002, lk={"lamppost": 1.5})
sh("S35", 23, "L23", mv([19.2, 0.85, 1.3], [0.0, 0.8, 1.05], 60, [19.2, 0.85, 1.3], [0.0, 0.8, 1.05], 70), {}, look="fogpale", fd=0.04, hand=0.004)
sh("S36", 23, "L23.2", fc(hd(21.75, 3.6, CAB_SEAT), -25, 25, 2.0, 40, rise=0.1), {"emrys": emr(-25, head=[0, 22])}, look="cab_eve", glow={"emrys": 0.25}, hand=0.003)
sh("S37", 24, "L24", mv([21.6, -5.5, 1.6], [20.9, 2.0, 1.4], 30, [21.5, -5.2, 1.6], [20.9, 2.0, 1.4], 30), {}, look="dusk", hand=0.004, lk={"lamppost": 0.6})
sh("S38", 24, "L24.2", mv([22.8, -2.8, 1.35], [21.85, 2.0, 1.25], 34), {}, look="dusk", door=-85, hand=0.004)
sh("S39", 25, "L25", mv([21.9, 2.7, 1.3], [21.3, 3.6, 0.6], 34), {}, look="cab_dark", hand=0.003, door=-85, steam=False)
sh("S40", 26, "L26", mv([21.1, 3.2, 1.75], [22.1, 3.7, 2.05], 40), {}, look="cab_dark", hand=0.002, hangcap=True, steam=False)
sh("S41", 26, "L26.2", mv([20.5, 3.0, 0.95], [20.4, 2.3, 0.62], 40), {}, look="cab_dark", hand=0.002, steam=True)
sh("S42", 27, "L27", mv([22.0, 1.6, 1.35], [3.0, 0.85, 1.0], 55, [21.6, 1.5, 1.35], [3.0, 0.85, 1.0], 55), {}, look="fogpale", fd=0.03, lprints=True,
   nobar=True, hand=0.003)
sh("S43", 27, "L27.2", mv([21.1, 4.4, 1.45], [21.85, 2.1, 1.4], 32), {"mec": P(21.85, 2.2, 180, arms=[0, 0], side=[0, 0], expr="scared")},
   look="cab_dark", door=-85, stool2=0, hand=0.004, fill_k=0.5)
sh("S44", 28, "L28", mv([21.6, -17.0, 1.7], [21.6, -9.0, 1.35], 30), {"mec": P(21.6, -9.0, 0, arms=[0, 0], side=[0, 0], expr="worried")},
   look="nightfog", fd=0.035, torch=True, glow={"mec": F}, hand=0.005, lk={"lamppost": 0.0}, fill_k=0.0)
talk("mec", "L28", "L28.2", 0.8)
sh("S45", 28, "L28.2", fc(hd(21.6, -9.0), 0, 8, 1.1, 42, rise=0.1), {"mec": P(21.6, -9.0, 0, arms=[100, 0], side=[0, 0], expr="worried", head=[0, 16])},
   look="nightfog", fd=0.035, phone=True, hand=0.003, fill_k=0.0, lk={"lamppost": 0.0})
sh("S46", 29, "L29", mv([250.6, 5.4, 1.5], [250.0, 0.0, 1.0], 30, [250.5, 5.4, 1.5], [250.0, 0.0, 1.0], 30),
   {"emrys": P(250.0, 0.0, 180, arms=[0, 0], side=[0, 0], expr="neutral")}, look="morning", mud=True, nocap=True, glow={"emrys": 0.3}, hand=0.004,
   sky_k=1.0, fill_k=1.0, lk={"ki_amb": 1.0})
sh("S47", 30, "L30", mv([27.4, 102.0, 1.6], [27.6, 120.0, 4.6], 22, [27.4, 104.0, 1.6], [27.6, 120.0, 4.2], 22),
   {"emrys": P(26.9, 116.4, 0, expr="neutral", arms=[0, 0], side=[0, 0]), "hh": P(28.3, 116.4, 0, expr="neutral", arms=[0, 0], side=[0, 0])}, look="morning",
   glow={"emrys": 0.25, "hh": M}, hand=0.004, fill_k=1.4, sun=(25, 200, 1.0, "#f0e4d0"))
sh("S48", 31, "L31", fc(hd(28.3, 116.4), 0, 14, 2.2, 38, rise=0.1), {"hh": P(28.3, 116.4, 0, expr="neutral", arms=[0, 0], side=[0, 0], head=[0, 0])},
   look="morning", glow={"hh": M}, fill_k=1.6)
ex("hh", "L31+0.15", head=[28, 0], blend=0.3)
ex("hh", "L31+0.6", head=[-28, 0], blend=0.35)
sh("S49", 32, "L32", mv([21.4, 2.9, 0.95], [21.75, 3.6, 0.8], 38), {"emrys": emr(-25)}, look="cab_night", glow={"emrys": 0.12}, hand=0.002)
sh("S50", 33, "L33", mv([21.9, 2.6, 1.4], [20.7, 3.7, 0.9], 26, [21.8, 2.7, 1.4], [20.7, 3.7, 0.9], 26),
   {"emrys": emr(-25), "me": mecr(arms=[60, 60])}, look="cab_night", glow={"emrys": 0.12, "me": F})
# ---- Monday to Wednesday
sh("S51", 34, "L34", mv([19.7, 1.9, 1.45], [0.0, 0.9, 1.15], 52), {}, look="fogpale", reach="mon", fd=0.035, farlamp=0.9, handlamp=0.0, hand=0.003)
sh("S52", 34, "L34.2", mv([6.0, -16.0, 1.5], [0.2, 0.9, 1.4], 70), {}, look="fogpale", reach="mon", fd=0.03, hand=0.003, handlamp=0.0)
sh("S53", 35, "L35", mv([10.5, -14.0, 1.7], [3.5, 0.8, 1.2], 38), {}, look="fogpale", reach="mon", fd=0.03, hand=0.003, handlamp=0.0)
sh("S54", 36, "L36", mv([14.0, -14.0, 1.7], [4.5, 0.8, 1.3], 19), {}, look="fogpale", reach="tue", fd=0.025, hand=0.003)
sh("S55", 37, "L37", mv([22.0, -9.0, 1.7], [13.0, 0.8, 1.15], 28), {}, look="fogpale", reach="wed", fd=0.03, hand=0.003)
sh("S56", 37, "L37.3", mv([19.7, 1.95, 1.55], [17.8, 0.8, 1.0], 40), {}, look="fogpale", reach="wed", fd=0.03, hand=0.003)
sh("S57", 38, "L38", mv([18.7, -0.1, 1.4], [17.8, 0.8, 1.02], 48), {}, look="fogpale", reach="wed", fd=0.03, hand=0.002)
# ---- Thursday
sh("S58", 39, "L39", mv([19.6, 2.7, 0.8], [19.6, 4.6, 0.5], 36), {}, look="cab_night", hand=0.002)
lvl("stove", "L39", 0.1, 2.0)
lvl("lamp", "L39", 0.3, 2.0)
sh("S59", 39, "L39.3", mv([20.3, 3.3, 1.7], [21.2, 4.98, 1.5], 30), {}, look="cab_night", hand=0.002)
sh("S60", 40, "L40", mv([22.2, 5.0, 1.55], [20.5, 2.5, 1.2], 24, [22.1, 4.9, 1.55], [20.5, 2.5, 1.2], 24),
   {"emrys": emr(-25), "me": mecr()}, look="cab_low", glow={"emrys": 0.12, "me": F}, reach="stand", sash=True, stool2=180, hand=0.003)
sh("S61", 41, "L41", mv([19.95, 1.95, 1.5], [5.0, 0.8, 1.15], 45), {}, look="fogpale", reach="stand", sash=True, fd=0.03, hand=0.003)
sh("S62", 42, "L42", mv([21.2, 3.6, 1.55], [19.95, 1.4, 1.5], 34), {}, look="cab_low", reach="stand", sash=True, hand=0.003, farlamp=0.9,
   lk={"cab_stove": 1.4, "cab_lamp": 0.0})
sh("S63", 43, "L43", mv([15.3, -3.6, 1.3], [19.6, 1.3, 1.4], 24), {}, look="fogpale", reach="stand", sash=True, fd=0.022, hand=0.003)
sh("S64", 44, "L44", mv([18.9, 0.85, 1.28], [0.0, 0.8, 1.12], 30), {}, look="fogpale", reach="stand", sash=True, fd=0.03, hand=0.003)
sh("S65", 45, "L45", cam([0, [19.45, 2.72, 1.25], [20.2, 2.72, 1.2], 16]),
   {"me": P(20.25, 3.05, 0, z=-0.09, sit=True, arms=[0, 0], side=[0, 0], expr="terrified")}, look="lean_ext", reach="lean", sash=True, sill=3.5, hand=0.003,
   lk={"cab_lamp": 1.0, "cab_amb": 1.4}, fill_k=1.0)
sh("S66", 45, "L45.3", mv([21.5, 0.2, 1.4], [20.1, 3.0, 1.3], 40, [21.3, 0.3, 1.4], [20.1, 3.0, 1.3], 40),
   {"me": P(20.25, 3.05, 0, z=-0.09, sit=True, arms=[0, 0], side=[0, 0], expr="terrified"), "emrys": emr(-25)}, look="lean_ext", glow={"emrys": 0.05},
   reach="lean", sash=True, hand=0.003, sill=3.0, lk={"cab_lamp": 1.0, "cab_amb": 1.4}, fill_k=1.0)
sh("S67", 46, "L46", mv([21.4, 3.0, 0.95], [21.75, 3.5, 0.8], 38), {"emrys": emr(-25, head=[0, 20])}, look="cab_low", glow={"emrys": 0.05}, hand=0.002,
   reach="lean", sash=True)
sh("S67b", 46, "L46b", mv([20.9, 3.7, 1.45], [20.2, 2.5, 1.25], 34), {}, look="cab_low", reach="lean", sash=True, hand=0.003,
   sill=3.0, lk={"cab_amb": 1.3}, fill_k=0.8)
ins("S67")
sh("S68", 47, "L47", fc(hd(20.2, 2.95), 0, 10, 2.0, 40, rise=0.1),
   {"me": P(20.2, 2.95, 0, arms=[40, 40], side=[0, 0], expr="wide", head=[0, 24])}, look="cab_low", glow={"me": 0.4}, hand=0.003)
sh("S69", 48, "L48", mv([20.3, 4.9, 0.9], [20.0, 2.3, 1.3], 26), {"me": P(21.45, 3.3, 0, arms=[50, 50], side=[0, 0], expr="wide")},
   look="cab_low", glow={"me": 0.9}, glow_k=2.0, reach="lean", sash=True, sill=3.0, hand=0.003, lk={"cab_lamp": 0.0, "cab_amb": 0.8, "cab_stove": 0.0})
lvl("stove", "L47", 0.0, 0.5)
lvl("glow.me", "L47+0.1", 0.9, 1.0)
sh("S70", 49, "L49", fc(hd(20.2, 2.95), 0, 8, 1.4, 42, rise=0.08, el=-0.1),
   {"me": P(20.2, 2.95, 0, arms=[85, 85], side=[0, 0], expr="wide", head=[0, 6])}, look="cab_low", glow={"me": 0.5}, hand=0.002, lk={"cab_lamp": 0.0, "cab_amb": 0.3})
sh("S72", 50, "L50", fc((21.6, -12.0, 0.88), 0, -30, 1.35, 42, rise=0.0), {"mec": P(21.6, -12.0, 0, arms=[0, 0], side=[0, 0], expr="neutral")},
   look="dusk", hand=0.002)
sh("S73", 51, "L51", fc(hd(20.25, 3.55, -0.09), 0, 30, 2.0, 40, rise=0.1), {"me": mecr(arms=[0, 0], head=[35, -14], expr="soft")},
   look="cab_eve", glow={"me": F})
sh("S74", 52, "L52", mv([21.3, 3.3, 0.95], [20.2, 2.4, 0.6], 40), {}, look="cab_eve", hand=0.002, steam=True)
sh("S75", 53, "L53", mv([16.0, -6.0, 1.8], [3.0, 0.8, 1.0], 30), {}, look="fogpale", fd=0.03, hand=0.004)
sh("S76", 54, "L54", fc(hd(20.25, 3.55, -0.09), 0, -22, 1.8, 40, rise=0.1), {"me": mecr(arms=[0, 0], head=[-12, -6], expr="neutral")},
   look="cab_low", glow={"me": 0.4})
sh("S77", 55, "L55", mv([19.6, 4.9, 1.4], [21.2, 3.2, 1.35], 30, [19.7, 4.8, 1.4], [21.1, 3.2, 1.35], 30),
   {"emrys": emr(-25, head=[-40, 4]), "me": mecr(arms=[0, 0], head=[60, 0], expr="neutral")}, look="cab_low", glow={"emrys": 0.05, "me": 0.4},
   reach="lean", sash=True, hand=0.004, lk={"cab_lamp": 0.6})
talk("me", "L55", "L56>", 0.6)
sh("S78", 56, "L56", fc(hd(21.75, 3.6, CAB_SEAT), 0, 24, 1.9, 40, rise=0.1), {"emrys": emr(0, head=[-45, 0])}, look="cab_low", glow={"emrys": 0.05})
ex("emrys", "L56.2", head=[10, 0], blend=0.6)
sh("S79", 57, "L57", mv([21.4, 2.9, 0.95], [21.75, 3.5, 0.8], 38), {"emrys": emr(-25)}, look="cab_low", glow={"emrys": 0.05}, hand=0.002)
lvl("glow.emrys", "L57+0.1", 1.0, 2.5)
sh("S80", 57, "L57.2", fc(hd(21.75, 3.6, CAB_SEAT), -25, 20, 1.5, 42, rise=0.05, el=-0.2), {"emrys": emr(0, head=[0, 4], expr="soft")}, look="cab_low",
   glow={"emrys": 0.9}, hand=0.002)
sh("S81", 58, "L58", mv([20.3, 4.95, 1.6], [21.8, 3.4, 1.25], 24), {"me": P(21.0, 3.5, -90, arms=[35, 35], side=[0, 0], expr="soft"),
   "emrys": P(22.0, 3.5, 90, arms=[35, 35], side=[0, 0], expr="neutral")}, look="cab_low", glow={"me": 0.9, "emrys": 1.0}, glow_k=2.5,
   lk={"cab_lamp": 1.0, "cab_amb": 1.8, "cab_stove": 0.8}, fill_k=1.4, stool2=0)
sh("S82", 58, "L58.3", mv([20.5, 3.6, 1.5], [20.2, 2.0, 1.4], 36), {}, look="fogpale", fd=0.02, sash=False, hand=0.003)
# ---- the turn
sh("S83", 59, "L59", mv([11.0, -5.0, 1.4], [11.5, 0.0, 1.3], 32), {"mec": P(14.0, 0.0, 270, to=(8.5, 0.0), arms=[0, 0], side=[0, 0], expr="soft")},
   look="dusk", glow={"mec": 0.4}, hand=0.004, lk={"lamppost": 0.0})
sh("S84", 60, "L60", mv([17.9, -1.6, 1.55], [20.2, 2.6, 1.6], 34), {"emrys": P(20.2, 2.75, 0, arms=[0, 95], side=[0, 0], expr="neutral")},
   look="dusk", glow={"emrys": B}, hand=0.003, sky_k=1.0, lk={"cab_lamp": 0.8, "cab_amb": 0.8})
sh("S85", 61, "L61", mv([21.3, 4.95, 1.7], [20.0, 0.0, 1.5], 30, [21.3, 4.8, 1.7], [20.0, 0.0, 1.5], 30),
   {"emrys": P(20.4, 2.65, 0, expr="neutral", arms=[0, 100], side=[0, 0])}, look="dusk", glow={"emrys": B}, sash=True, hand=0.003,
   lk={"cab_lamp": 0.8, "cab_amb": 0.8})
sh("S86", 62, "L62", fc(hd(14.0, 0.0), 0, 10, 2.3, 38, rise=0.08), {"mec": P(14.0, 0.0, 0, arms=[0, 100], side=[0, 0], expr="grin")},
   look="dusk", glow={"mec": 0.6}, lk={"lamppost": 0.0}, fill_k=1.0)
sh("S87", 62, "L62.2", fc(hd(21.6, -2.0), 0, 12, 2.6, 38, rise=0.08), {"ada": P(21.6, -2.0, 0, arms=[0, 0], side=[0, 0], expr="grin")},
   look="dusk", glow={"ada": M})
sh("S88", 64, "L64", mv([349.2, -0.2, 1.9], [349.45, 2.7, 0.6], 30), {"me": P(349.45, 2.3, 0, z=0.5, lean=-90, arms=[40, 40], side=[0, 0], expr="wide"),
   "ada": P(350.55, 2.3, 0, z=0.5, lean=-90, arms=[0, 0], side=[0, 0], expr="asleep")}, look="bed", glow={"me": B}, hand=0.002, lk={"bd_amb": 1.0})
sh("S89", 64, "L64.1+0.5", mv([349.4, 0.6, 1.5], [349.4, 2.4, 0.95], 34), {"me": P(349.45, 2.3, 0, z=0.5, lean=-90, arms=[90, 90], side=[0, 0], expr="wide"),
   "ada": P(350.55, 2.3, 0, z=0.5, lean=-90, arms=[0, 0], side=[0, 0], expr="asleep")}, look="bed", glow={"me": B}, glow_k=3.0, hand=0.002, lk={"bd_amb": 1.0})
sh("S90", 65, "L65", mv([350.55, 2.9, 2.0], [350.55, 3.62, 0.72], 34), {"me": P(349.45, 2.3, 0, z=0.5, lean=-90, arms=[90, 90], side=[0, 0], expr="wide"),
   "ada": P(350.55, 2.3, 0, z=0.5, lean=-90, arms=[0, 0], side=[0, 0], expr="asleep")}, look="bed", glow={"me": B}, glow_k=4.0, hand=0.002, lk={"bd_amb": 1.5})
sh("S91", 65, "L65.3", mv([349.9, 3.6, 1.3], [349.9, 5.4, 1.2], 30), {}, look="bedout", bedreach=True, fd=0.05, hand=0.003)
sh("S92", 66, "L66", mv([351.4, 3.4, 1.5], [349.7, 3.6, 1.35], 26), {"me": P(349.45, 3.1, -90, z=0.5, sit=True, arms=[85, 85], side=[0, 0], expr="wide", head=[70, 0])},
   look="bedout", glow={"me": B}, glow_k=3.0, bedreach=True, fd=0.05, hand=0.003)


# ---- cabin face and hand shots, redone with cameras that stay inside the little room (x 19.3 to 22.3, y 2.5 to 5.0)
def cfc(face, cam_xy, lens, rise=0.1, cz=1.45):
    dx, dy = face[0] - cam_xy[0], face[1] - cam_xy[1]
    d = math.hypot(dx, dy)
    drop = rise * d * 24.0 / lens + (cz - face[2]) * 0.0
    return cam([0, [cam_xy[0], cam_xy[1], cz], [face[0], face[1], face[2] - drop], round(lens / 0.7, 1)])


def redo(sid, camera=None, place=None, **kw):
    for i, (a, b, c, d, e) in enumerate(SH):
        if a == sid:
            if camera is not None:
                d = camera
            e = dict(e, **kw)
            SH[i] = (a, b, c, d, e)
            if place is not None:
                PL[sid] = place
            return
    raise KeyError(sid)


EF = (21.75, 3.6, 1.58)
EH = (21.75, 3.5, 0.78)
redo("S24", cfc(EH, (20.7, 2.7), 30, 0.05))
redo("S25", cfc((21.75, 3.55, 1.2), (20.6, 2.8), 30, 0.05))
redo("S29", cfc(EF, (19.8, 2.75), 28), {"emrys": emr(-45, head=[-20, 0])})
redo("S36", cfc(EF, (19.8, 2.75), 28), {"emrys": emr(-25, head=[0, 22])})
redo("S78", cfc(EF, (19.8, 2.75), 28), {"emrys": emr(-70, head=[0, 0])})
redo("S80", cfc(EF, (19.8, 2.75), 26, 0.04), {"emrys": emr(-45, head=[0, 4], expr="soft")})
redo("S68", mv([20.2, 1.0, 1.15], [20.35, 2.6, 1.0], 24), glow={"me": 0.3}, look="cab_low", nosash=True, lk={"cab_amb": 1.3}, fill_k=0.6, glow_k=4.0, hand=0.002)
redo("S70", cfc((20.2, 2.95, 1.45), (21.5, 3.5), 28, 0.08), {"me": P(20.2, 2.95, 20, arms=[85, 85], side=[0, 0], expr="wide", head=[0, 6])})
redo("S73", cfc((20.25, 3.55, 1.45), (19.4, 2.7), 26), {"me": mecr(arms=[0, 0], head=[35, -14], expr="soft", yaw=-45)})
redo("S76", cfc((20.25, 3.55, 1.45), (19.4, 2.7), 26), {"me": mecr(arms=[0, 0], head=[-12, -6], expr="neutral", yaw=-45)})
redo("S07", mv([190.0, -1.3, 1.65], [190.0, 3.6, 1.0], 19, [190.0, -1.0, 1.65], [190.0, 3.6, 1.0], 19))

def insert_after(sid):
    item = SH.pop()
    i = [x[0] for x in SH].index(sid)
    SH.insert(i + 1, item)


sh("S14b", 10, "L10.2", fc(hd(21.1, 1.2), -20, 28, 3.2, 38, rise=0.08), {"emrys": P(21.1, 1.2, -20, expr="neutral", arms=[0, 0], side=[0, 0])},
   look="day", glow={"emrys": M}, fill_k=1.5, sun=(14, 40, 3.0, "#ffd9a0"))
insert_after("S14")
sh("S30b", 20, "L20.2", mv([20.6, -0.9, 1.55], [20.2, 2.6, 1.5], 34), {"emrys": P(20.2, 3.0, 0, arms=[0, 150], side=[0, 0], expr="neutral")},
   look="dusk", glow={"emrys": 0.3}, hand=0.003, sky_k=1.0, lk={"cab_lamp": 0.8, "cab_amb": 0.8, "lamppost": 0.0}, nobar=True, nosash=True)
insert_after("S30")


# ================================================================ fix round: merges (every cut 1.2 to 2.3 s) and reframes
def merge(keep, drop):
    ids = [x[0] for x in SH]
    i, j = ids.index(keep), ids.index(drop)
    if j < i:
        a, b, c, d, e = SH[i]
        SH[i] = (a, b, SH[j][2], d, e)
    del SH[j]
    PL.pop(drop, None)


for _k, _d in (("S14", "S14b"), ("S23", "S24"), ("S29", "S28"), ("S36", "S35"), ("S51", "S52"),
               ("S57", "S56"), ("S79", "S80"), ("S86", "S87")):
    merge(_k, _d)

# ---- the Reach: low three-quarter cameras, the rail as a diagonal, lighter fog behind him
RV = dict(look="fogreach", hand=0.003)
redo("S51", mv([8.4, -0.2, 1.2], [-0.6, 0.85, 1.5], 34, [7.6, -0.1, 1.2], [-0.6, 0.85, 1.5], 36), reach="mon", farlamp=0.9, handlamp=1.0, **RV)
redo("S53", mv([3.4, -3.0, 0.8], [-0.7, 0.8, 1.5], 30, [3.0, -2.8, 0.8], [-0.7, 0.8, 1.5], 30), reach="mon", farlamp=0.9, handlamp=1.0, **RV)
redo("S54", mv([10.8, -1.6, 1.7], [2.5, 0.8, 1.2], 30, [10.3, -1.5, 1.7], [2.5, 0.8, 1.2], 30), reach="tue", farlamp=0.9, handlamp=1.0, **RV)
redo("S55", mv([19.8, 0.0, 1.3], [-0.9, 0.8, 1.5], 40, [19.3, 0.05, 1.3], [-0.9, 0.8, 1.5], 40), reach="wed", **RV)
redo("S57", mv([19.3, -0.5, 1.5], [17.8, 0.8, 0.98], 36, [18.9, -0.3, 1.5], [17.8, 0.8, 0.98], 36), reach="wed", **RV)
redo("S61", mv([23.5, -0.9, 1.45], [0.5, 0.85, 1.2], 44, [23.0, -0.8, 1.45], [0.5, 0.85, 1.2], 44), reach="stand", sash=True, nobar=True, handlamp=2.5, **RV)
redo("S63", mv([27.0, -1.0, 1.45], [12.0, 1.3, 0.75], 18, [26.6, -0.9, 1.45], [12.0, 1.3, 0.75], 18), reach="stand", sash=True, nobar=True, farlamp=2.0, **RV)
redo("S64", mv([19.0, 0.8, 1.5], [0.0, 0.8, 1.15], 28, [18.7, 0.8, 1.45], [0.0, 0.8, 1.15], 28), reach="stand", sash=True, nobar=True, **RV)
# ---- dark shots, hand inserts, exposure, the rule marker
redo("S01", mv([21.6, -5.2, 1.2], [21.6, 0.3, 1.0], 36, [21.6, -4.8, 1.2], [21.6, 0.3, 1.0], 36),
     {"doc": P(21.6, -0.3, 0, expr="neutral", arms=[60, 60], side=[0, 0]), "t1": P(20.4, 0.7, 0, expr="neutral", arms=[55, 55], side=[0, 0]),
      "t2": P(22.8, 0.8, 0, expr="neutral", arms=[55, 55], side=[0, 0])},
     glow={"doc": B, "t1": B, "t2": B}, glow_k=5.0, sun=(10, 25, 0.5, "#ffd9a0"), sky_k=0.55, fill_k=0.35)
HL = dict(look="cab_eve", lk={"cab_amb": 1.3}, fill_k=1.5, glow_k=4.0, hand=0.002)
redo("S23", cfc((21.65, 3.4, 0.9), (21.65, 2.35), 10, 0.0, cz=1.0), {"emrys": emr(-25, arms=[75, 75])}, glow={"emrys": 0.8}, **HL)
redo("S49", cfc((21.65, 3.4, 0.85), (21.65, 2.35), 10, 0.0, cz=0.95), {"emrys": emr(-25)}, glow={"emrys": 0.9}, **HL)
redo("S67", cfc((21.65, 3.4, 0.85), (20.3, 2.5), 11, 0.0, cz=0.95), {"emrys": emr(-25, head=[0, 20])}, glow={"emrys": 0.7}, **HL)
redo("S79", cfc((21.65, 3.4, 0.9), (21.0, 2.4), 10, 0.0, cz=0.8), {"emrys": emr(-25, arms=[75, 75])}, glow={"emrys": 0.4}, **HL)
redo("S68", mv([20.2, 1.0, 1.15], [20.35, 2.6, 1.0], 24), glow={"me": 0.3}, look="cab_low", nosash=True, lk={"cab_amb": 1.3}, fill_k=0.6, glow_k=4.0, hand=0.002)
redo("S70", mv([19.9, 1.0, 1.35], [20.4, 2.45, 1.2], 30), glow={"me": 0.8}, look="cab_low", nosash=True, lk={"cab_lamp": 0.0, "cab_amb": 1.0}, fill_k=0.6, glow_k=4.0, hand=0.002)
redo("S32", cam([0, [22.3, -14.6, 1.2], [21.6, -12.0, 0.95], 28]), {"mec": P(21.6, -12.0, 0, arms=[0, 0], side=[0, 0], expr="neutral")},
     look="dusk", fill_k=2.2, lk={"lamppost": 1.0}, hand=0.002)
redo("S34", mv([16.9, 0.1, 1.55], [17.6, 0.8, 0.98], 36, [17.1, 0.2, 1.55], [17.6, 0.8, 0.98], 36), look="fogreach", prints=True, fd=0.012, fill_k=3.0, hand=0.002)
redo("S19", look="kitchen", fill_k=0.35, lk={"ki_amb": 0.5, "ki_win": 0.35})
redo("S18", look="kitchen", fill_k=0.4, lk={"ki_amb": 0.6, "ki_win": 0.4})
redo("S47", mv([26.6, 108.0, 1.5], [27.6, 116.4, 1.4], 30, [26.9, 110.0, 1.5], [27.6, 116.4, 1.4], 30), fill_k=0.4, sun=(25, 200, 0.5, "#f0e4d0"), sky_k=0.5, fogc="#7c8a96", fd=0.01)
redo("S57", mv([17.0, -1.5, 1.3], [18.1, 0.8, 1.0], 32, [17.4, -1.3, 1.3], [18.1, 0.8, 1.0], 32), reach="wed", handlamp=2.5, **RV)

redo("S41", fill_k=0.6)


def nudge(sid, off):
    for i, (a, b, c, d, e) in enumerate(SH):
        if a == sid:
            SH[i] = (a, b, f"{c}{off:+.2f}", d, e)
            return
    raise KeyError(sid)


for _sid, _off in (("S48", -0.35), ("S59", -0.4), ("S43", 0.3), ("S41", 0.23), ("S82", -0.25),
                   ("S76", -0.1), ("S86", -0.1), ("S11b", -0.15), ("S88", -0.3), ("S06", 0.15), ("S08", 0.13), ("S11", 0.1), ("S13", 0.07), ("S22", 0.07),
                   ("S32", 0.17), ("S34", 0.1), ("S38", -0.07), ("S69", 0.07)):
    nudge(_sid, _off)

# ================================================================================================== story
shots, ids = [], []
for sid, n, at, camera, opt in SH:
    s = {"id": sid, "n": n, "cam": camera, "step": 2}
    if ids:
        s["at"] = at
    for k, v in opt.items():
        if k not in ("glow",):
            s[k] = v
    shots.append(s)
    ids.append(sid)
REF = {s[0]: (0 if i == 0 else s[2]) for i, s in enumerate(SH)}

# glow levels: a cue at each shot's first word for every pair of hands whose level changes (cuts only, never a ramp)
cur = {w: None for w in cast}
for sid, n, at, camera, opt in SH:
    for w in cast:
        v = opt["glow"].get(w, 0.0)
        if cur[w] != v:
            CUES.append({"at": REF[sid], "name": "lvl", "key": f"glow.{w}", "level": v, "ramp": 0})
            cur[w] = v
# the pocket light leaks only where set; it is part of lvl as well
story = {
    "slug": "ep58-swing-bridge",
    "title": "In this town, your hands glow whenever somebody needs you",
    "made_for_kids": False,
    "premise": "In a river town your hands glow, soft and amber, whenever somebody needs you. The narrator's never have, and he tells himself it suits him. His wife's father Emrys swung the old iron bridge for forty-one years until it was bolted shut, and now his own hands are going dark in the bridge cabin while something with arms as long as the bridge lays its hands a little nearer the cabin each night.",
    "twist": "The narrator's hands had been glowing for months. It was Emrys who needed him: the gruff man who calls him the lodger and always has two mugs out before he arrives. He never saw it because he only looked at his hands by the stove and walked home with them in his pockets, so the first line was never a rule that left him out.",
    "world": "A river town in late autumn: a short green iron swing bridge on a stone pier, bolted shut, a small brick bridge cabin with a vertical iron wheel, a pot-bellied stove and two stools, a gravel bank path with one lamp post, river fog, and a pale new road bridge far downriver.",
    "key_color": "#b98cff",
    "gap": 0.22,
    "tail": 0.25,
    "fade_out": False,
    "voice": {"voice": "am_adam", "tempo": 1.03, "rate": 1.45},
    "look": {"flash_safe": True, "fog": "#c4dcee", "fog_density": 0.004, "fog_start": 14.0, "sky": "#9cc8ec", "sky_strength": 1.0,
             "exposure": 0.0},
    "grade": {"shadows": [0.0, 0.0, 0.03], "highlights": [0.03, 0.012, -0.02], "saturation": 1.04, "contrast": 1.04,
              "vignette": 0.25, "bloom": 0.2, "grain": 0.008},
    "cast": cast,
    "lines": lines,
    "shots": shots,
}

from blocky import timeline  # noqa: E402

vp = HERE.parent / "voice-timings.json"
if not vp.exists() or __import__("os").environ.get("DRAFT"):
    story["acting"] = {}
    story["cues"] = []
    OUT.write_text(json.dumps(story, indent=1, ensure_ascii=False) + "\n")
    print("wrote draft", OUT, f"({len(shots)} shots)")
    sys.exit(0)
voice = json.loads(vp.read_text())
draft = dict(story, name="ep58-swing-bridge")
tl0 = timeline.build(draft, voice)
at = timeline.resolver(tl0["lines"], tl0["duration"])

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
DEF = dict(arms=[0, 0], side=[0, 0], head=[0, 0], lean=0, look=[0, 0], expr="neutral", sit=False)
for i, sid in enumerate(ids):
    ref = REF[sid]
    pl = PL[sid]
    for w in cast:
        if w in pl:
            p = pl[w]
            put(w, ref, {"pos": list(prev_end[w])})
            k = {**DEF, "yaw": p["yaw"], "pos": list(p["pos"]), "blend": 0.0, "hidden": False}
            for a in ("arms", "side", "head", "lean", "look", "expr", "blink", "sit"):
                if a in p:
                    k[a] = p[a]
            put(w, ref, k)
            prev_end[w] = list(p["to"]) if p.get("to") else list(p["pos"])
            visible[w] = True
        elif visible[w]:
            put(w, ref, {"pos": list(prev_end[w]), "hidden": True, "blend": 0.0})
            visible[w] = False
for w, ref, attrs in EX:
    put(w, ref, dict(attrs))
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


fx_("L22+0.5", "click", -26)
fx_("L23+0.3", "creak", -12, dur=3.0)
fx_("L24+0.1", "door", -20)
fx_("L26+0.4", "click", -28)
fx_("L27.3", "click", -22)
fx_("L40-0.05", "sting", -12, dur=2.0, keep=True)
fx_("L43+0.05", "hit", -18, dur=1.4)
fx_("L45+0.3", "creak", -16, dur=2.0)
fx_("L48+0.0", "sting", -16, dur=1.4, keep=True)
fx_("L57+0.1", "chime", -18, dur=2.4)
fx_("L60+0.1", "whoosh", -26)
fx_("L65+0.5", "thud", -18)
fx_("L19.1", "click", -28)
fx_("L19+0.5", "click", -28)
story["music"] = {
    "root": 55, "mode": "dorian", "bpm": 76, "seed": 58,
    "sections": [
        {"at": 0, "voices": ["pluck", "pad"], "energy": 0.4},
        {"at": "L10", "voices": ["pluck", "pad"], "energy": 0.35},
        {"at": "L24", "voices": ["drone", "pluck"], "energy": 0.3},
        {"at": "L34", "voices": ["drone", "tick"], "energy": 0.3},
        {"at": "L40", "voices": ["drone"], "energy": 0.25},
        {"at": "L47", "voices": ["drone", "tick"], "energy": 0.35},
        {"at": "L51", "voices": ["drone", "pluck"], "energy": 0.4},
        {"at": "L57", "voices": ["drone", "pluck_hi", "pad"], "energy": 0.6},
        {"at": "L65", "voices": ["drone", "pluck"], "energy": 0.3},
    ]}
story["sound"] = {
    "floor": "wood", "steps_db": -26,
    "ambience": [
        {"kind": "water", "from": 0, "to": "end", "lufs": -42},
        {"kind": "hum", "from": 0, "to": "L22", "lufs": -46},
        {"kind": "wind", "from": "L22", "to": "L58", "lufs": -43},
        {"kind": "drips", "from": "L39", "to": "L47", "lufs": -44},
        {"kind": "room", "from": "L15", "to": "L21", "lufs": -44},
    ],
    "sfx": sfx,
    "music_drops": [
        {"from": "L24-0.6", "to": "L24", "keep": ["sting"]},
        {"from": "L40-0.7", "to": "L40+0.05", "keep": ["sting"]},
        {"from": "L48-0.5", "to": "L48+0.05", "keep": ["sting"]},
    ]}
story["phonemes"] = {"Emrys": "ˈɛmɹɪs"}
OUT.write_text(json.dumps(story, indent=1, ensure_ascii=False) + "\n")
print("wrote", OUT, f"({len(shots)} shots, {tl0['duration']} s)")
