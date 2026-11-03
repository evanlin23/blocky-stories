"""Writes ../story.json for ep55 "In this town, moss grows on you while you wait" (script.md, 2026-11-02).

Run from anywhere: python stories/ep55-caravan-park/generator/make_story.py
The words are in lines.json next to this file. Everything else is here: the cast, the shots, the acting, the cues
set.py reads, the effects, the score and the sound. Shot ids are numbered in order (S01, S02, ...).

Places (set.py's coordinates): our gate is at (0, 0) between two granite posts (x = +-0.75); the two folding chairs
sit just inside it at y = -1.6 (mine at x = -0.7, Jory's at x = +0.7), facing +y. The Kneeler kneels at
(-1.7, -2.3) facing +y. Our caravan is at y = -6.9 .. -4.5 (door at x = 0, step unit in front). The headland path
runs +y to the old bench at (3.6, 20.5). The neighbours' vans are along the row at x = -9.4, 9.4. The town is at
x = 80 (bus shelter), 120 (shop and bench), 160 (station), all facing +y. The kitchen set is at (300, -90).
"""
import json
import math
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE.parent / "story.json"
lines = json.loads((HERE / "lines.json").read_text())

FAR = [0, -200, 0]
SIT = -0.26
FACE = 1.56
CH_ME = [-0.7, -1.6]
CH_JO = [0.7, -1.6]
KN = [-1.7, -2.3]
IX, IY = 300.0, -90.0


def c(*keys):
    return [list(k) for k in keys]


def mv(p0, t0, l0, p1=None, t1=None, l1=None):
    if p1 is None:
        return c([0, p0, t0, l0])
    return c([0, p0, t0, l0], [1, p1, t1 if t1 is not None else t0, l1 if l1 is not None else l0])


def front(hd, yaw, off=0.0, dist=1.0, dz=0.0, lens=32, push=0.0, aim_dz=0.0, lens2=None):
    """A camera in front of a face: hd the face centre, yaw the way the person faces (0 = -y), off degrees round,
    dist metres away; push moves it in over the shot."""
    a = math.radians(yaw + off)
    d = (math.sin(a), -math.cos(a))
    p0 = [round(hd[0] + d[0] * dist, 3), round(hd[1] + d[1] * dist, 3), round(hd[2] + dz, 3)]
    tg = [hd[0], hd[1], round(hd[2] + aim_dz, 3)]
    if not push and not lens2:
        return c([0, p0, tg, lens])
    p1 = [round(hd[0] + d[0] * (dist - push), 3), round(hd[1] + d[1] * (dist - push), 3), round(hd[2] + dz, 3)]
    return c([0, p0, tg, lens], [1, p1, tg, lens2 or lens])


def face_of(x, y, z=0.0, sit=False):
    return [x, y, z + (FACE + SIT if sit else FACE)]


def key(face, cam, w=120.0, side=0.9, up=0.5):
    """A face light that sits beside the camera, up and to one side, aimed at the face."""
    px = cam[0] + side
    return {"face": [[round(px, 3), round(cam[1], 3), round(cam[2] + up, 3)], list(face), w]}


# ---------------------------------------------------------------------------------------------------- cast
FACE_STD = {"eyes": "round", "brows": True}


def person(skin, shirt, pants, shoes, hair, hair_c, **kw):
    d = {"age": "adult", "skin": skin, "shirt": shirt, "pants": pants, "shoes": shoes, "sleeves": "long",
         "hair": hair, "hair_c": hair_c, "hat": "none", "face": dict(FACE_STD)}
    d.update(kw)
    return d


cast = {
    "me": person("#f0c7a6", "#2c3f66", "#4a3d30", "#5a3a22", "buzz", "#a9a9ab", extras=["coat", "backpack"],
                 zip_c="#f2f0e8", extra_c="#6b4a2a"),
    "jory": person("#e6b894", "#5a7494", "#6e4f6e", "#2b221b", "cap", "#f2f2ee", pattern="knit", pattern_c="#e8dfc6",
                   hat="beanie", hat_c="#c2602a", face={"eyes": "round", "brows": True}, height=0.97),
    "neighbour": person("#f0c9a6", "#d1a031", "#3b3f4d", "#3a2a20", "bun", "#3a2a20", hat="bucket", hat_c="#c9b98a"),
    "busman": person("#d9a67e", "#7b7f86", "#3b3b40", "#2a2a2e", "cap", "#c8c8c8", extras=["coat"], zip_c="#505560"),
    "parcelman": person("#e2b48c", "#7a5434", "#3a3028", "#2a2018", "swoop", "#3a2a20", pattern="plaid",
                        pattern_c="#4f3520", extras=["coat"], zip_c="#3a2a1a"),
    "meeter1": person("#c78f68", "#2f8f8f", "#2c3038", "#22201e", "cap", "#2a1d15", extras=["coat"], zip_c="#1d6666"),
    "meeter2": person("#f0c7a6", "#8a4f3a", "#33343c", "#22201e", "cap", "#6a4a30", hat="beanie", hat_c="#d0a030"),
    "meeter3": person("#e0b08a", "#5b6a86", "#2c2c34", "#22201e", "cap", "#2a1d15", hat="ballcap", hat_c="#364055"),
    "trainwoman": person("#efc4a2", "#b04a5a", "#3a3a44", "#2a2a2e", "long", "#5a3a28", extras=["coat"], zip_c="#7a2a3a"),
    "benchman": person("#e0b28c", "#c2a074", "#4b4a52", "#3a2f26", "cap", "#d8d8d8"),
    "benchwife": person("#efc4a2", "#7a3b5e", "#33343c", "#2a2a2e", "bun", "#b8b8b8", extras=["coat"], zip_c="#4e2440"),
}

# ---------------------------------------------------------------------------------------------------- acting
keys = {k: [{"at": 0, "pos": FAR, "yaw": 0, "hidden": True, "expr": "neutral"}] for k in cast}
last = {k: FAR for k in cast}


def put(who, at, pos, yaw=None, **kw):
    """Appear (or jump) at pos on a cut."""
    keys[who].append({"at": at, "pos": last[who]})
    k = {"at": at, "pos": pos, "blend": 0.0, "hidden": False, **kw}
    if yaw is not None:
        k["yaw"] = yaw
    keys[who].append(k)
    last[who] = pos


def walk(who, at, pos, **kw):
    keys[who].append({"at": at, "pos": pos, **kw})
    last[who] = pos


def hide(who, at):
    keys[who].append({"at": at, "hidden": True})


def set_(who, at, **kw):
    keys[who].append({"at": at, **kw})


# ---- 01 the rule: the town
put("neighbour", 0, [-9.4, -3.0, 0.0], 180, expr="neutral")
set_("neighbour", "L01>", head=[0, 0])
hide("neighbour", "L02")
put("busman", "L02", [80.0, -0.3, 0.0], 180, expr="neutral")
hide("busman", "L03")
put("parcelman", "L03", [9.4, -3.0, 0.0], 180, expr="neutral", head=[25, 4])
set_("parcelman", "L03.2", head=[0, 0])
hide("parcelman", "L04")
put("meeter2", "L04", [158.2, -3.0, 0.45], 180, expr="neutral")
put("meeter3", "L04", [161.8, -3.0, 0.45], 180, expr="neutral")
put("meeter1", "L04", [160.0, -3.0, 0.45], 180, expr="neutral")
put("trainwoman", "L05", [160.0, -0.55, 0.5], 0, expr="neutral")
walk("trainwoman", "L05.2", [160.0, -1.9, 0.45])
set_("meeter1", "L05.2", expr="soft")
hide("trainwoman", "L05.2")
hide("meeter2", "L05.2")
hide("meeter3", "L05.2")
hide("meeter1", "L06")
put("benchman", "L06", [119.1, -0.3, -0.23], 180, expr="neutral", sit=True)
put("benchwife", "L06", [119.95, -0.3, -0.23], 180, expr="neutral", sit=True, arms=[0, 100])
hide("benchman", "L08")
hide("benchwife", "L08")

# ---- 02 me and Jory
put("me", "L08", [0.0, -0.9, 0.0], 40, expr="smirk")
set_("me", "L08.1", yaw=0, blend=0.6)
walk("me", "L08>", [0.0, -0.9, 0.0])
put("me", "L09", [-3.2, -2.9, 0.0], -90)
walk("me", "L09>", [-8.4, -2.9, 0.0])
put("jory", "L10", [0.5, -4.12, 0.71], 180, expr="smile", arms=[0, 0])
put("me", "L10", [-0.5, -4.12, 0.71], 180, expr="smile", arms=[0, 0])
hide("me", "L11")
put("me", "L13", [0.0, 1.0, 0.0], 180, expr="neutral")
walk("me", "L13>", [0.0, 5.2, 0.0])
put("jory", "L14", [-0.45, 6.6, 0.0], 0, expr="neutral")
put("me", "L14", [0.5, 6.6, 0.0], 0, expr="neutral")
walk("jory", "L14.2", [-0.45, 2.6, 0.0])
walk("me", "L14.2", [0.5, 2.6, 0.0])
put("jory", "L14.2", [0.35, 0.7, 0.0], 0, expr="neutral")
put("me", "L14.2", [0.0, -1.0, 0.0], 0, expr="neutral")
walk("me", "L14>", [0.0, -2.3, 0.0])
put("jory", "L15", [CH_JO[0], CH_JO[1], SIT], 180, expr="neutral", sit=True)
hide("me", "L15")
set_("jory", "L16", expr="neutral")

# ---- 03 going green
put("me", "L18", [0.0, 0.6, 0.0], 0, expr="smirk")
walk("me", "L18.1", [0.05, -0.8, 0.0])
put("jory", "L18", [CH_JO[0], CH_JO[1], 0.0], 180, expr="soft", sit=False, head=[0, 0])
walk("me", "L18>", [0.0, -0.9, 0.0])
put("me", "L19", [0.1, -1.2, 0.0], 0, expr="worried")
put("jory", "L19", [0.85, -1.2, 0.0], 0, expr="neutral")
put("jory", "L20", [CH_JO[0], CH_JO[1], SIT], 180, expr="neutral", sit=True, head=[0, 0])
hide("me", "L20")
put("me", "L21.2", [0.0, -3.9, 0.48], 180, expr="neutral")
walk("me", "L21>", [0.0, -2.0, 0.0])
hide("me", "L22")
put("jory", "L22", [CH_JO[0], CH_JO[1], SIT], 180, expr="neutral", sit=True, head=[70, 0], blend=0.0)
hide("jory", "L23")

# ---- 05 fog: I'm late; he isn't there
put("me", "L29", [0.6, 9.0, 0.0], 0, expr="worried", run=True)
walk("me", "L29>", [0.1, 3.0, 0.0], run=True)
walk("me", "L31", [0.1, 3.0, 0.0])
hide("me", "L31")
put("me", "L34", [0.0, -0.6, 0.0], 0, expr="scared")
put("me", "L35", [0.0, -0.6, 0.0], 0, expr="scared", arms=[0, 80])
set_("me", "L35.2", hidden=True)
put("me", "L37", [0.0, -0.4, 0.0], 0, expr="scared", arms=[0, 0], head=[0, -8])
set_("me", "L37.3", hidden=True)

# ---- 06 the Kneeler
put("me", "L38", [0.0, -3.9, 0.48], 180, expr="worried")
walk("me", "L38>", [0.0, -2.6, 0.0])
walk("me", "L39", [0.0, -2.6, 0.0])
hide("me", "L40")
ME_STAND = [-1.7, -0.8, 0.0]
put("me", "L47", ME_STAND, 0, expr="scared", head=[0, 0])
set_("me", "L47.2", hidden=True)
put("me", "L48", [-1.7, -1.0, 0.0], 0, expr="scared")
set_("me", "L49", expr="neutral", head=[0, 0])
set_("me", "L50", hidden=True)
put("me", "L51", ME_STAND, 0, expr="neutral")
put("me", "L52", [0.0, 0.8, 0.0], 0, expr="neutral")
walk("me", "L52.1", [0.0, -0.8, 0.0])
walk("me", "L52.2", [0.0, 1.0, 0.0])
set_("me", "L53", hidden=True)
put("me", "L55", [-0.2, -0.2, 0.0], 180, expr="neutral")
walk("me", "L55>", [0.3, 3.5, 0.0])

# ---- 07 arrived
BX, BY = 3.6, 20.35
put("jory", "L56.3", [BX - 0.45, BY, -0.23], 0, expr="smirk", sit=True)
hide("me", "L56")
put("me", "L58", [BX + 0.4, BY, -0.23], 0, expr="soft", sit=True)
set_("jory", "L58", expr="soft")
set_("jory", "L60", expr="neutral")
set_("me", "L60", expr="neutral")
set_("jory", "L61", hidden=True)
set_("jory", "L62", expr="soft", hidden=False)
hide("jory", "L63")
hide("me", "L63")

# ---- 08 patience
put("jory", "L65", [0.1, 0.8, 0.0], 180, expr="neutral", sit=False)
walk("jory", "L65>", [0.4, 6.4, 0.0])
put("me", "L66", [CH_ME[0], CH_ME[1], SIT], 180, expr="soft", sit=True)
hide("jory", "L66")
put("jory", "L67", [-0.4, 9.2, 0.0], 0, expr="neutral", sit=False)
walk("jory", "L67.3", [-0.4, 7.6, 0.0])
set_("jory", "L67.3", yaw=-85, blend=0.5)
walk("jory", "L67>", [0.0, 5.0, 0.0])
set_("me", "L68", expr="soft")
put("jory", "L69", [0.7, 2.4, 0.0], 0, expr="soft", sit=False)
walk("jory", "L69>", [0.7, -0.5, 0.0])
put("jory", "L70", [CH_JO[0], CH_JO[1], SIT], 180, expr="soft", sit=True)
put("jory", "L72", [CH_JO[0], CH_JO[1], SIT], 180, expr="neutral", sit=True, head=[75, 0])
hide("jory", "L72.4")
hide("me", "L72.4")

acting = keys

# ---------------------------------------------------------------------------------------------------- shots
# (at, camera, options). Options: step (1 = drawn on ones), hand (handheld drift), look (cue look), id
SH = []


def S(at, cam, **opt):
    SH.append((at, cam, opt))


NB_F = face_of(-9.4, -3.0)
JF = face_of(CH_JO[0], CH_JO[1], sit=True)
MF = face_of(CH_ME[0], CH_ME[1], sit=True)
KN_FACE = [KN[0], -1.75, 1.5]

# ---- 01 the rule
cam = front(NB_F, 180, -10, 3.5, 0.0, 40, push=0.25)
S(0, cam, hand=0.003)
S("L02", mv([86.0, 9.0, 1.7], [80.5, -0.5, 1.15], 30, [85.2, 8.6, 1.7], [80.5, -0.5, 1.15], 30))
PM_F = face_of(9.4, -3.0)
S("L03", front(PM_F, 180, 18, 4.4, 0.05, 36, push=0.3))
S("L03.2", front(PM_F, 180, 4, 1.5, 0.0, 38), hand=0.003)
S("L04", mv([160.0, 9.0, 1.9], [160.0, -3.0, 1.5], 34, [160.0, 8.0, 1.9], [160.0, -3.0, 1.5], 34))
S("L05", mv([161.4, -4.3, 1.7], [160.0, -1.4, 1.35], 30, [161.2, -4.2, 1.7], [160.0, -1.4, 1.35], 30))
TM_F = face_of(160.0, -3.0, 0.45)
S("L05.2", mv([160.9, 0.2, 2.15], list(TM_F), 36, [160.8, 0.3, 2.15], list(TM_F), 36))
S("L06", mv([125.0, 9.0, 2.5], [119.8, -1.0, 1.5], 28, [124.0, 8.6, 2.4], [119.8, -1.0, 1.5], 28))
BM_F = face_of(119.1, -0.3, -0.23 + 0.0, sit=False)
BM_F = [119.1, -0.3, 1.33]
S("L06.1", front(BM_F, 180, 18, 2.3, 0.0, 34, push=0.15))
BW_F = [119.95, -0.3, 1.33]
S("L07", front(BW_F, 180, -22, 2.2, 0.0, 34, push=0.15))

# ---- 02 me and Jory
ME_G = face_of(0.0, -0.9)
S("L08", front(ME_G, 0, 14, 2.6, 0.05, 34, push=0.25), look=key(ME_G, [0.6, -3.5, 1.6], 160), hand=0.003)
S("L09", mv([-4.5, 1.6, 1.5], [-6.2, -3.4, 1.15], 32, [-4.7, 1.5, 1.5], [-6.6, -3.4, 1.15], 32))
S("L10", mv([5.5, 3.0, 2.0], [0.0, -4.1, 1.75], 44, [4.2, 1.6, 1.9], [0.0, -4.1, 1.75], 50))
S("L11", mv([0.0, 3.2, 1.3], [0.0, -1.8, 0.55], 30, [0.0, 2.8, 1.25], [0.0, -1.8, 0.55], 30))
S("L12", mv([-0.5, 0.2, 0.95], [-0.7, -1.6, 0.5], 34, [-0.5, 0.0, 0.9], [-0.7, -1.6, 0.5], 34))
S("L13", mv([0.0, -0.9, 1.5], [0.1, 10.0, 1.15], 30, [0.0, -1.1, 1.5], [0.1, 10.0, 1.15], 30))
S("L14", mv([0.4, 9.8, 1.8], [0.0, 0.0, 1.2], 30, [0.2, 9.0, 1.8], [0.0, 0.0, 1.2], 30))
S("L14.2", mv([3.4, 0.8, 1.5], [0.0, -0.4, 1.25], 32))
S("L15", front(JF, 180, -26, 2.4, 0.0, 34, push=0.2), look=None)

# ---- 03 going green
S("L16", front(JF, 180, 18, 2.1, 0.0, 34, push=0.2))
S("L17.1", mv([-0.35, 0.0, 1.62], [0.25, -1.6, 1.38], 44, [-0.3, -0.1, 1.6], [0.25, -1.6, 1.38], 44), hand=0.003)
S("L18", mv([0.9, -3.5, 1.5], [0.2, -0.6, 1.3], 34, [0.8, -3.3, 1.5], [0.2, -0.6, 1.3], 34),
  look=key([0.1, -0.9, 1.56], [0.9, -3.5, 1.5], 140, side=-1.0))
S("L19", mv([0.55, -3.2, 1.55], [0.5, -1.2, 1.5], 38, [0.55, -3.0, 1.55], [0.5, -1.2, 1.5], 38),
  look=key([0.1, -1.2, 1.56], [0.55, -3.2, 1.55], 140, side=-1.0))
S("L20", front(JF, 180, 12, 2.0, 0.0, 38, push=0.1), hand=0.003)
S("L20b", front(JF, 180, 28, 1.9, -0.08, 36, push=0.15))
S("L21", mv([IX - 1.0, IY + 0.1, 1.55], [IX - 1.4, IY + 1.7, 1.0], 30, [IX - 1.1, IY + 0.2, 1.5], [IX - 1.4, IY + 1.7, 1.0], 30))
S("L21.2", mv([0.3, -0.3, 1.5], [0.0, -3.2, 1.1], 30, [0.3, -0.4, 1.5], [0.0, -3.2, 1.1], 30))
S("L22", mv([1.7, -3.2, 1.45], [0.2, -1.6, 1.15], 32, [1.6, -3.1, 1.45], [0.2, -1.6, 1.15], 32))

# lights for the Kneeler's shots: a warm side key (the kitchen window), a cold rim behind, a little fill
def kn_look(cam, aim, key_w=170.0, rim_w=420.0, fill_w=0.0, rim_from=(-3.8, -4.6, 3.2), side=None, up=0.0):
    """Side light only: a warm key from the side (the window's spill) level with the face, a cold rim from behind.
    No light from the camera's side, no fill. side = +1 / -1 picks the side (default: the camera's side of it)."""
    sg = side if side in (1, -1) else (1 if cam[0] >= aim[0] else -1)
    kp = [round(aim[0] + 2.1 * sg, 3), round(aim[1] + 0.35, 3), round(aim[2] + 0.2 + up, 3)]
    out = {"kkey": [kp, list(aim), key_w, 55, "#ffb877"],
           "krim": [list(rim_from), list(aim), rim_w, 80, "#a8c4e8"]}
    if fill_w > 0:
        out["kfill"] = [[round(cam[0], 3), round(cam[1], 3), round(cam[2] + 1.5, 3)], list(aim), fill_w]
    return out


# ---- 04 mornings
S("L23", mv([6.0, 4.0, 1.7], [0.0, -5.0, 1.2], 26, [5.6, 3.6, 1.7], [0.0, -5.0, 1.2], 26))
S("L24", mv([0.2, -1.2, 1.1], [-1.0, -3.2, 0.0], 34, [0.15, -1.25, 1.05], [-1.0, -3.2, 0.0], 34),
  look=kn_look([0.2, -1.2, 1.1], [-0.8, -3.2, 0.1], key_w=150.0, rim_w=60.0, side=-1))
S("L25", mv([-2.2, -1.2, 1.1], [-1.0, -3.2, 0.0], 34, [-2.15, -1.25, 1.05], [-1.0, -3.2, 0.0], 34),
  look=kn_look([-2.2, -1.2, 1.1], [-1.2, -3.2, 0.1], key_w=150.0, rim_w=60.0, side=1))
S("L26", mv([0.9, -2.8, 0.6], [0.0, -3.6, 0.25], 30, [0.8, -2.8, 0.55], [0.0, -3.6, 0.25], 30))
S("L26.1", mv([0.0, -2.45, 0.95], [0.0, -3.56, 0.26], 32), hand=0.0008)
S("L27", mv([2.6, -2.2, 1.5], [0.4, -4.5, 1.8], 24, [2.5, -2.3, 1.5], [0.4, -4.5, 1.8], 24))
S("L28", mv([1.3, -2.8, 1.9], [0.7, -4.4, 1.8], 36, [1.25, -2.9, 1.9], [0.7, -4.4, 1.8], 36))
S("L28.1", mv([-1.5, -1.8, 1.1], [-1.0, -3.4, 0.3], 28, [-1.4, -1.9, 1.1], [-1.0, -3.4, 0.3], 28))

# ---- 05 fog
S("L29", mv([0.0, -0.7, 1.6], [0.4, 9.0, 1.3], 30, [0.0, -0.9, 1.6], [0.3, 9.0, 1.3], 30),
  look=key([0.6, 6.0, 1.56], [0.0, -0.7, 1.6], 90, side=0.0, up=0.2))
S("L30", mv([-4.0, -2.0, 5.0], [0.0, 15.0, 0.5], 24, [-3.6, -2.0, 4.6], [0.0, 15.0, 0.5], 24))
S("L31", mv([0.0, 1.1, 1.55], [0.7, -1.6, 0.8], 30))
S("P01", mv([0.0, 1.0, 1.5], [0.7, -1.6, 0.9], 30, [0.3, -0.6, 1.3], [0.7, -1.6, 0.9], 32))
S("L32", mv([1.9, -1.0, 2.35], [0.75, 0.0, 2.3], 40, [1.8, -0.9, 2.35], [0.75, 0.0, 2.3], 40), hand=0.003)
S("L33", mv([0.7, -1.78, 2.7], [0.7, -1.6, 0.4], 30, [0.7, -1.76, 2.5], [0.7, -1.6, 0.4], 30))
S("L34", front(face_of(0.0, -0.6), 0, 12, 2.2, 0.05, 34, push=0.2), look=key(face_of(0.0, -0.6), [0.5, -2.8, 1.6], 120))
S("L35", front(face_of(0.0, -0.6), 0, -10, 1.7, 0.05, 38), look=key(face_of(0.0, -0.6), [-0.5, -2.2, 1.6], 120))
S("L35.2", mv([IX + 1.6, IY - 1.3, 1.1], [IX + 0.85, IY - 0.55, 0.78], 36, [IX + 1.5, IY - 1.2, 1.0], [IX + 0.85, IY - 0.55, 0.78], 40))
S("L36", mv([IX - 0.3, IY - 0.7, 1.5], [IX - 2.08, IY + 0.25, 1.2], 30, [IX - 0.45, IY - 0.7, 1.5], [IX - 2.08, IY + 0.25, 1.2], 30))
S("L36.3", mv([IX + 0.5, IY + 0.25, 1.45], [IX - 2.0, IY + 0.25, 0.8], 28, [IX + 0.4, IY + 0.25, 1.45], [IX - 2.0, IY + 0.25, 0.8], 28))
S("L37", front(face_of(0.0, -0.4), 0, 10, 2.0, 0.05, 36, push=0.2), look=key(face_of(0.0, -0.4), [0.6, -2.4, 1.6], 120))
S("L37.3", mv([0.0, 1.0, 1.4], [0.5, 13.0, 1.2], 28, [0.0, 1.2, 1.4], [0.5, 13.0, 1.2], 28))

# ---- 06 the Kneeler
S("L38", mv([1.7, -1.1, 1.5], [0.0, -3.4, 1.1], 30, [1.6, -1.2, 1.5], [0.0, -3.2, 1.1], 30),
  look=key([0.0, -3.6, 1.3], [1.7, -1.1, 1.5], 90, side=-0.8))
S("L39", mv([-1.2, -2.6, 1.7], [0.6, -4.4, 1.8], 28, [-1.1, -2.7, 1.7], [0.6, -4.4, 1.8], 28))
S("L40", mv([-1.0, 0.7, 0.55], [-1.5, -2.3, 0.1], 26, [-1.0, 0.5, 0.5], [-1.5, -2.3, 0.1], 26))
S("L41", mv([-2.4, -1.6, 0.4], [-2.0, -2.3, 0.0], 28, [-2.35, -1.7, 0.36], [-2.0, -2.3, 0.0], 28))
S("P02", mv([-2.4, -1.6, 0.42], [-2.0, -2.3, 0.0], 28, [-2.45, -1.65, 0.4], [-2.0, -2.3, 0.0], 28))

KH = [KN[0], -2.0, 1.2]    # the middle of the Kneeler, kneeling upright
c42 = mv([-1.9, -1.2, 0.25], [-1.7, -2.3, 0.15], 28, [-1.9, -1.3, 0.3], [-1.7, -2.3, 1.7], 28)
S("L42", c42, look=kn_look([-1.9, -1.2, 0.8], [-1.7, -2.3, 1.1]))
c42b = mv([3.6, -1.4, 1.3], [-1.7, -2.3, 1.2], 30, [3.3, -1.4, 1.3], [-1.7, -2.3, 1.2], 30)
S("L42.2", c42b, look=kn_look([3.6, -1.4, 1.3], [-1.7, -2.3, 1.2]))
c43 = mv([5.4, -1.2, 1.0], [-1.2, -1.2, 1.2], 34)
S("L43", c43, look=kn_look([4.0, -1.0, 1.3], [-1.7, -2.3, 1.2]))
S("L44", mv([-0.3, 0.4, 1.35], [-1.7, -2.3, 1.2], 40, [-0.4, 0.3, 1.35], [-1.7, -2.3, 1.2], 40),
  look=kn_look([-0.3, 0.4, 1.35], [-1.7, -2.3, 1.2]))
S("L44.2", mv([-0.9, 0.9, 1.3], [-1.9, -5.0, 1.3], 34),
  look=kn_look([-0.9, 0.9, 1.3], [-1.7, -2.3, 1.2]))
S("L45", mv([-3.6, -0.2, 1.45], [-1.0, -1.9, 1.15], 30, [-3.5, -0.2, 1.45], [-1.0, -1.9, 1.15], 30),
  look=kn_look([-3.6, -0.2, 1.45], [-1.7, -2.3, 1.2]))
S("L46", mv([-0.2, -0.9, 1.85], [-1.7, -2.2, 1.9], 40, [-0.25, -0.95, 1.85], [-1.7, -2.2, 1.9], 40),
  look=kn_look([-0.2, -0.9, 1.85], [-1.7, -2.2, 1.9]))
S("L47", mv([0.5, -0.9, 1.5], [-1.7, -0.9, 1.5], 36, [0.45, -0.95, 1.5], [-1.7, -0.9, 1.5], 36),
  look=kn_look([0.5, -0.9, 1.5], [-1.7, -1.7, 1.45]))
S("L47.2", mv([-1.7, -0.3, 1.55], [-1.7, -1.7, 1.5], 20, [-1.7, -0.4, 1.55], [-1.7, -1.7, 1.5], 20), hand=0.002,
  look=kn_look([-1.7, -0.4, 1.55], [-1.7, -1.7, 1.5], key_w=170.0, side=1))
S("L48", mv([3.2, -0.9, 1.6], [-1.7, -1.35, 1.55], 40, [1.5, -0.7, 1.6], [-1.7, -1.35, 1.55], 40), look=kn_look([3.2, -0.9, 1.6], [-1.7, -1.4, 1.55]))

# ---- 07 arrived
S("L49", mv([-0.2, -0.2, 1.6], [-1.7, -1.1, 1.55], 38, [-0.3, -0.2, 1.6], [-1.7, -1.1, 1.55], 38),
  look=kn_look([-0.2, -0.2, 1.6], [-1.7, -1.7, 1.45]))
S("L50", mv([161.6, -4.2, 1.7], [160.0, -3.0, 1.2], 32), hand=0.004)
S("L51", mv([0.5, -1.5, 1.55], [-1.7, -0.9, 1.45], 40, [0.45, -1.5, 1.55], [-1.7, -0.9, 1.45], 40),
  look=key([-1.7, -0.85, 1.5], [0.5, -1.5, 1.55], 120, side=0.8))
S("L52", mv([0.9, -3.5, 1.5], [0.2, -0.6, 1.3], 34, [0.8, -3.3, 1.5], [0.2, -0.6, 1.3], 34))
S("L53", mv([0.3, -0.3, 1.0], [-1.2, -2.0, 0.95], 30, [0.25, -0.35, 1.0], [-1.2, -2.0, 0.95], 30),
  look=kn_look([0.3, -0.3, 1.0], [-1.7, -2.3, 1.2]))
S("L54", mv([1.8, -0.6, 0.95], [0.7, -1.6, 0.6], 32, [1.7, -0.6, 0.95], [0.7, -1.6, 0.6], 32))
S("L55", mv([0.6, 9.0, 1.5], [-1.0, -2.0, 1.2], 40, [0.6, 9.0, 1.5], [-1.0, -2.0, 1.2], 40),
  look=kn_look([-0.5, 0.0, 1.5], [-1.7, -1.7, 1.45]))
S("L56", mv([3.6, 14.5, 1.3], [3.6, 20.5, 0.8], 30, [3.6, 15.5, 1.3], [3.6, 20.5, 0.8], 30))
JB_F = [BX - 0.45, BY, 1.33]
S("L56.3", front(JB_F, 0, 12, 2.0, 0.0, 34, push=0.15), look=key(JB_F, [3.8, 18.4, 1.6], 120, side=-0.8))
S("L57", mv([6.4, 19.0, 1.2], [BX - 0.45, 20.4, 1.3], 34, [6.2, 19.2, 1.2], [BX - 0.45, 20.4, 1.3], 34))
S("L58", mv([1.8, 14.5, 1.5], [3.6, 20.4, 1.15], 30, [2.0, 15.0, 1.5], [3.6, 20.4, 1.15], 30))
S("L59", mv([3.6, 24.0, 1.55], [3.6, 12.0, 0.9], 26, [3.6, 23.6, 1.55], [3.6, 12.0, 0.9], 26))
S("L60", mv([6.6, 20.4, 1.35], [BX, 20.4, 1.3], 40, [6.3, 20.4, 1.35], [BX, 20.4, 1.3], 40))
S("L60.1", mv([3.4, 14.5, 1.6], [2.0, 19.5, 2.4], 30), hand=0.005)
S("L61", front([BX + 0.4, BY, 1.33], 0, 14, 1.5, 0.0, 36, push=0.1), look=key([BX + 0.4, BY, 1.33], [BX + 1.1, BY - 1.45, 1.4], 65, side=-0.8))
S("L61.3", mv([BX - 0.8, BY - 1.5, 1.3], [BX - 0.1, BY - 0.05, 1.08], 75, [BX - 0.75, BY - 1.45, 1.3], [BX - 0.1, BY - 0.05, 1.08], 75),
  look=key([BX + 0.0, BY, 1.1], [BX - 0.8, BY - 1.5, 1.3], 110, side=0.8))
S("L62", front([BX - 0.45, BY, 1.33], 0, 10, 2.5, 0.05, 34, push=0.15), look=key([BX - 0.45, BY, 1.33], [BX + 1.0, 17.5, 1.6], 160, side=-0.8))

# ---- 08 patience
S("L63", mv([-2.8, 1.4, 1.1], [-1.0, -1.8, 0.6], 28, [-2.7, 1.3, 1.1], [-1.0, -1.8, 0.6], 28), id="RAIN1")
S("L64", mv([-2.4, -1.4, 0.45], [-2.0, -2.3, 0.0], 28, [-2.35, -1.5, 0.4], [-2.0, -2.3, 0.0], 28), id="RAIN2")
S("L65", mv([-1.8, -0.8, 1.5], [0.3, 4.5, 1.2], 30, [-1.6, -0.9, 1.5], [0.3, 4.5, 1.2], 30))
S("L66", front(MF, 180, 22, 2.1, 0.0, 34, push=0.15))
S("L67", mv([0.0, -1.4, 1.5], [-0.8, 8.6, 1.3], 70))
S("L67.3", mv([0.0, -1.4, 1.5], [-0.3, 6.2, 1.3], 60))
S("L68", mv([-0.1, 0.4, 1.35], [CH_ME[0] + 0.5, CH_ME[1], 1.14], 50), hand=0.003)
S("L68.2", front(MF, 180, -14, 1.7, 0.0, 38, push=0.1))
S("L69", mv([0.0, 3.6, 1.5], [0.0, -1.6, 0.9], 28, [0.1, 3.3, 1.5], [0.0, -1.6, 0.9], 28))
S("L70", front(MF, 180, 26, 1.9, 0.0, 36, push=0.1))
S("L71", mv([-0.1, 0.5, 1.2], [CH_ME[0] + 0.5, CH_ME[1], 1.14], 55), hand=0.002)
S("L72", front(JF, 180, 6, 1.7, 0.0, 38, push=0.1))
S("L72.4", mv([-0.1, 0.3, 0.4], [-1.4, -2.0, 0.2], 28, [-0.1, 0.2, 0.38], [-1.4, -2.0, 0.2], 28))

shots, SID = [], {}
for i, (at, cam, opt) in enumerate(SH):
    sid = opt.get("id") or f"S{i + 1:02d}"
    s = {"id": sid, "cam": cam, "step": opt.get("step", 2), "hand": opt.get("hand", 0.004)}
    if i:
        s["at"] = at
    shots.append(s)
    SID[at] = sid

# ---------------------------------------------------------------------------------------------------- cues
cues = []


def cue(at, name, **kw):
    cues.append({"at": at, "name": name, **kw})


# the light
cue(0, "env", set="day")
cue("L08", "env", set="gold", dur=0.4)
cue("L16", "env", set="gold", dur=0.4)
cue("L16.1", "env", set="dusk", dur=3.5)
cue("L18", "env", set="gold", dur=0.4)
cue("L20", "env", set="dusk", dur=6.0)
cue("L23", "env", set="morn", dur=0.4)
cue("L27-0.5", "env", set="dusk", dur=0.5)
cue("L29", "env", set="dusk", dur=0.4)
cue("L30", "env", set="fog", dur=4.0)
cue("L38", "env", set="fogdusk", dur=1.5)
cue("L56", "env", set="fog", dur=0.4)
cue("L59", "env", set="foglift", dur=4.5)
cue("L63", "env", set="grey", dur=0.4)
cue("L65", "env", set="gold2", dur=0.4)
cue("L69", "env", set="dusk2", dur=6.0)
cue("L72.4", "env", set="cold", dur=1.0)

# the porch lamp: it fades down on its own twice (1.5 s each), and is back on only across cuts
cue("L27", "lamp", v=0.0, dur=1.5)
cue("L29", "lamp", v=1.0, dur=0.5)
cue("L39", "lamp", v=0.0, dur=1.5)
cue("L65", "lamp", v=1.0, dur=0.6)

# moss
for who in ("neighbour", "busman", "parcelman", "meeter1", "meeter2", "meeter3", "benchman"):
    cue(0, "moss", who=who, v=1.0)
cue("L05.2+0.1", "moss", who="meeter1", v=0.0, dur=0.15)
cue("L50", "moss", who="meeter1", v=1.0)
cue("L50", "shower", who="meeter1")
cue("L50+0.2", "moss", who="meeter1", v=0.0, dur=0.15)
cue("L05.2+0.1", "shower", who="meeter1")
cue("L16", "moss", who="jory", v=0.2)
cue("L17", "moss", who="jory", v=0.45)
cue("L17.1", "moss", who="jory", v=0.62)
cue("L18", "moss", who="jory", v=0.66)
cue("L20", "moss", who="jory", v=0.97)
cue("L56", "moss", who="jory", v=1.18)
cue("L62.2", "moss", who="jory", v=0.0, dur=0.15)
cue("L62.2", "shower", who="jory", h=1.9)
cue("L61", "moss", who="me", v=0.25)
cue("L68", "moss", who="me", v=0.52, dur=1.2)
cue("L66", "moss", who="me", v=0.25)
cue("L63", "moss", who="me", v=0.25)

# the things
cue("L16", "seatmoss", v=0.0)
cue("L33", "seatmoss", v=1.0)
cue("L40", "seatmoss", v=0.0)
cue("P01", "cap", v=1.0)
cue("L63", "cap", v=0.0)
cue("L24", "hollows", which="step", v=1.0)
cue("L63", "hollows", which="step", v=0.0)
cue("L25", "water", which="step", v=1.0)
cue("L40", "hollows", which="chair", v=1.0)
cue("L41", "water", which="chair", v=1.0)
cue("L65", "hollows", which="chair", v=0.0)
cue("L65", "water", which="chair", v=0.0)
cue("L72.4", "hollows", which="chair", v=1.0, dur=2.0)
cue("L72.4", "water", which="chair", v=0.0)
cue("L26", "mat", v=1.0)
cue("P03", "mat", v=1.0)
cue("L35.2", "phone", v=1.0)
cue("L36", "phone", v=0.0)
cue("L04", "train", v=0.0)
cue("L05", "train", v=1.0)
cue("L05.2", "train", v=0.0)
cue(0, "train", v=0.0)
cue("L20b", "sitgull", v=1.0, pos=[0.18, -1.62, 1.2])
cue("L21", "sitgull", v=0.0)
cue("L67", "sitgull", v=1.0, pos=[-3.31, 7.09, 1.18])
cue("L68", "sitgull", v=0.0)
cue("L60.1", "gulls", v=1.0, x0=-1.0, y0=17.5, z0=2.3, dx=1.0, dy=0.22)
cue("L61", "gulls", v=0.0)

# the Kneeler: upright and side-on, then the slow bend, then leaning in
cue("L42", "kneeler", show=True, lean=0.0, pitch=0.0, yaw=0.0)
cue("L46.1", "kneeler", pitch=15.0, yaw=-30.0, dur=2.0)
cue("L47", "kneeler", pitch=0.0, yaw=0.0, dur=0.0)
cue("L47", "kneeler", lean=58.0, dur=4.2)
cue("L56", "kneeler", show=False)

# the lights for the shots the Kneeler isn't in are default (sun and sky); the shot looks come from SH
LOOK_AT = []
for (at, cam, opt), s in zip(SH, shots):
    if opt.get("look"):
        LOOK_AT.append((at, opt["look"], s))
for i, (at, look, s) in enumerate(LOOK_AT):
    idx = [a for a, _, _ in SH].index(at)
    nxt = SH[idx + 1][0] if idx + 1 < len(SH) else None
    cues.append({"at": at, "name": "shot", "look": look})
    if nxt is not None:
        cues.append({"at": nxt, "name": "shot", "look": None})

# ---------------------------------------------------------------------------------------------------- sound
sfx = [
    {"at": "L09", "kind": "click", "db": -26},
    {"at": "L18", "kind": "click", "db": -20},
    {"at": "L21", "kind": "riser", "db": -28, "dur": 1.8},
    {"at": "L05.2+0.1", "kind": "whoosh", "db": -20, "dur": 0.7},
    {"at": "L50+0.1", "kind": "whoosh", "db": -22, "dur": 0.7},
    {"at": "L62.2", "kind": "whoosh", "db": -20, "dur": 0.7},
    {"at": "L35.2", "kind": "knock", "pattern": [0.0, 0.12, 0.24, 0.36, 0.48, 0.6], "tone": "glass", "db": -16},
    {"at": "L27", "kind": "hum_sweep", "db": -26, "dur": 1.5},
    {"at": "L39", "kind": "hum_sweep", "db": -24, "dur": 1.5},
    {"at": "P01+0.2", "kind": "knock", "pattern": [0.0], "tone": "below", "db": -3, "crack": 1.5, "keep": True},
    {"at": "P02+0.15", "kind": "creak", "db": -12, "dur": 0.7, "keep": True},
    {"at": "L42.2", "kind": "sting", "db": -17, "dur": 2.2},
    {"at": "L47.2", "kind": "glide", "db": -14, "dur": 2.5},
    {"at": "L20b", "kind": "squeal", "db": -26, "dur": 0.5},
    {"at": "L60.1", "kind": "squeal", "db": -24, "dur": 0.5},
    {"at": "L60.1+0.9", "kind": "squeal", "db": -27, "dur": 0.4},
    {"at": "L67", "kind": "squeal", "db": -26, "dur": 0.5},
    {"at": "L72.4", "kind": "creak", "db": -20, "dur": 2.2},
    {"at": "L72.4", "kind": "thud", "db": -17},
]
music = {"root": 41, "mode": "lydian", "bpm": 72, "seed": 55, "sections": [
    {"at": 0, "voices": ["pad", "piano"], "energy": 0.28},
    {"at": "L16", "voices": ["pad", "piano"], "energy": 0.3},
    {"at": "L23", "voices": ["pad"], "energy": 0.28, "mode": "minor"},
    {"at": "L31", "voices": ["drone", "pad"], "energy": 0.55, "mode": "minor"},
    {"at": "L42", "voices": ["drone", "pad"], "energy": 0.7, "mode": "minor"},
    {"at": "L47", "voices": ["drone", "pad", "choir"], "energy": 0.75, "mode": "minor"},
    {"at": "L49", "voices": ["drone", "pad"], "energy": 0.5, "mode": "minor"},
    {"at": "L58", "voices": ["drone", "pad", "piano"], "energy": 0.5, "mode": "major"},
    {"at": "L70", "voices": ["drone", "pad"], "energy": 0.42, "mode": "minor"},
]}
sound = {"floor": "grass", "steps_db": -26,
         "ambience": [
             {"kind": "wind", "from": 0, "to": "end", "lufs": -36},
             {"kind": "water", "from": 0, "to": "end", "lufs": -40},
             {"kind": "wind", "from": "L30", "to": "L62", "lufs": -34},
             {"kind": "rain", "from": "L63", "to": "L65", "lufs": -32},
         ],
         "sfx": sfx,
         "music_drops": [
             {"from": "P01-0.02", "to": "P01>", "keep": ["knock"], "db": -70},
             {"from": "P02-0.02", "to": "P02>", "keep": ["creak"], "db": -70},
         ]}

fx = []

story = {
    "slug": "ep55-caravan-park",
    "title": "In this town, moss grows on you while you wait",
    "made_for_kids": False,
    "premise": "In a town where moss grows on you while you wait for someone, the narrator, an older man, has never had a speck, because he is always early and never waits. His wife Maggie is coming up green at their headland caravan park, the moss won't come off when he gets back, and every morning there are two deep knee hollows in the wet grass by the step.",
    "twist": "He came home every evening but never arrived: he put the kettle on and was out again, and never once sat in his own chair. Maggie wasn't waiting for him to come back, she was waiting for him to stop. His empty chair left the caravan's count short by one, and the Kneeler has been kneeling beside it every night, standing in his place. When he sits down and waits with her, her moss comes off and his begins.",
    "world": "A static caravan park on a grassy headland in autumn: cream caravans with coloured stripes, a picket gate between two granite posts, two folding canvas chairs, gorse and bracken, a path up to an old bench above the grey sea, and the small town below with its bus shelter, shop bench and station.",
    "voice": {"voice": "am_adam", "tempo": 1.03, "rate": 1.45},
    "key_color": "#cfd66a",
    "gap": 0.12,
    "tail": 0.25,
    "look": {"fog": "#c9d7dc", "fog_density": 0.012, "fog_start": 5.0, "sky": "#bfd3df", "sky_strength": 1.15,
             "exposure": 0.0, "flash_safe": True},
    "grade": {"shadows": [0.0, 0.0, 0.03], "highlights": [0.03, 0.015, -0.03], "saturation": 1.0,
              "contrast": 1.05, "vignette": 0.3, "bloom": 0.22, "grain": 0.012},
    "rain_shots": ["RAIN1", "RAIN2"],
    "phonemes": {},
    "cast": cast,
    "lines": lines,
    "shots": shots,
    "acting": acting,
    "cues": cues,
    "fx": fx,
    "music": music,
    "sound": sound,
}
OUT.write_text(json.dumps(story, indent=1, ensure_ascii=False) + "\n")
print("wrote", OUT, f"({len(shots)} shots)")
