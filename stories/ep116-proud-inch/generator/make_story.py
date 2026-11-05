"""Writes ../story.json for ep116 "Grandpa Is Nine Feet TALL" (script.md, 2026-11-05). Run:
python stories/ep116-proud-inch/generator/make_story.py

The words are in lines.json. Places are in ../layout.py (shared with set.py). A character facing -y has yaw 0, +x 90,
+y 180, -x -90. Time references use the script's chunk numbers (L01.3 is the fourth chunk); captions are split to two or
three words and the references are remapped.
"""
import json
import math
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import layout as G  # noqa: E402

OUT = HERE.parent / "story.json"
REV = 1
orig_lines = json.loads((HERE / "lines.json").read_text())
lines, CHUNKMAP = [], {}
for ln in orig_lines:
    out, mp = [], []
    for cap, spoken in ln["chunks"]:
        cw, sw = cap.split(), spoken.split()
        n = len(cw)
        k = 1 if n <= 3 else (2 if n <= 6 else 3)
        sizes = [n // k + (1 if i < n % k else 0) for i in range(k)]
        mp.append(len(out))
        i = 0
        for sz in sizes:
            out.append([" ".join(cw[i:i + sz]), " ".join(sw[i:i + sz])])
            i += sz
    CHUNKMAP[ln["id"]] = mp
    lines.append({**ln, "chunks": out})
# the 0.6 s music drop before L20
idx = next(i for i, l in enumerate(lines) if l["id"] == "L20")
lines.insert(idx, {"id": "P01", "pause": 0.6, "chunks": [["", ""]]})


def remap(ref):
    if not isinstance(ref, str):
        return ref
    mm = re.match(r"^(L\d+)\.(\d+)(.*)$", ref)
    if mm and mm.group(1) in CHUNKMAP:
        return f"{mm.group(1)}.{CHUNKMAP[mm.group(1)][int(mm.group(2))]}{mm.group(3)}"
    return ref


def remap_all(items):
    for it in items:
        for key in ("at", "from", "to"):
            if key in it:
                it[key] = remap(it[key])


def person(skin, shirt, pants, shoes, hair="cap", hair_c="#2a1d15", pattern="solid", pattern_c=None, collar=None,
           hat="none", hat_c="#333333", extras=(), eyes="round", sleeves="long", brow_w=1.0, **kw):
    d = {"age": "adult", "skin": skin, "shirt": shirt, "pattern": pattern, "pants": pants, "shoes": shoes,
         "sleeves": sleeves, "hair": hair, "hair_c": hair_c, "hat": hat, "hat_c": hat_c,
         "face": {"eyes": eyes, "brows": True, "ink": "#1c120c"}}
    if brow_w != 1.0:
        d["face"]["brow_w"] = brow_w
    if pattern_c:
        d["pattern_c"] = pattern_c
    if collar:
        d["collar"] = collar
    if extras:
        d["extras"] = list(extras)
    d.update(kw)
    return d


cast = {
    "me": person("#dca97c", "#8c93a0", "#3c5a8c", "#3a2a1e", hair="cap", hair_c="#15110e", sleeves="short",
                 extras=["apron"], extra_c="#e8493a", brow_w=1.6),
    "grandpa": person("#e8b890", "#c98f45", "#7a5434", "#3a2a1e", hair="buzz", hair_c="#f4f4f6", brow_w=2.6,
                      height=1.6, collar="#f0e2c4", eyes="round"),
    "bloom": person("#f0c8a0", "#ffd23f", "#4a5a7a", "#6a4a32", hair="long", hair_c="#b9bdc8", eyes="lashes",
                    brow_w=1.4, extras=["coat"]),
    "cust": person("#b98456", "#5a8ad0", "#4a4036", "#2a2a2a", hair="buzz", hair_c="#1a1410"),
    "dad1": person("#e2b088", "#4aa86a", "#4a5a7a", "#3a2a1a", hair="spiky", hair_c="#7a4a2a", sleeves="short",
                   height=1.22),
    "mail": person("#d3a07a", "#3a6fd0", "#2c3a5a", "#2a2a2a", hair="bun", hair_c="#2a1a12", eyes="lashes",
                   extras=["backpack"], extra_c="#e8b830", height=1.25),
    "bridedad": person("#e8b890", "#8a909c", "#6a707c", "#2a2a2a", hair="cap", hair_c="#b4b4ba", collar="#fffaf0",
                       extras=["tie"], extra_c="#d9443a", height=1.2),
}
acting = {n: [{"at": 0, "hidden": True, "pos": [0, 0]}] for n in cast}
last = {n: [0, 0] for n in cast}
visible = set()
cues = []
SH = []


def put(who, at, pos, yaw=None, **kw):
    p = list(pos)
    acting[who].append({"at": at, "pos": list(last[who])})
    k = {"at": at, "pos": p, "blend": 0.0, "hidden": False, "lean": 0, "head": [0, 0], "arms": [0, 0], "side": [0, 0]}
    if yaw is not None:
        k["yaw"] = yaw
    k.update(kw)
    acting[who].append(k)
    last[who] = p
    visible.add(who)


def go(who, at, pos, **kw):
    p = list(pos)
    acting[who].append({"at": at, "pos": p, **kw})
    last[who] = p


def beat(who, at, **kw):
    acting[who].append({"at": at, "pos": list(last[who]), **kw})


def only(at, names):
    for w in list(visible):
        if w not in names:
            acting[w].append({"at": at, "hidden": True})
            visible.discard(w)


def cue(at, name, **kw):
    cues.append({"at": at, "name": name, **kw})


def shot(at, camera, name, step=2, hand=None):
    SH.append((at, camera, step, hand, name))


def mv(p0, t0, l0, p1=None, t1=None, l1=None):
    if p1 is None:
        return [[0, list(p0), list(t0), l0]]
    return [[0, list(p0), list(t0), l0], [1, list(p1), list(t1 if t1 is not None else t0), l1 or l0]]


def fc(h, fw, lens=36, fx=0.5, fy=0.46, ccx=0.0, ccz=0.0, push=0.1, tdx=0.0):
    """A camera that frames the head centre `h` at fraction (fx, fy) of a frame `fw` metres wide, looking along +y,
    ccx / ccz move the camera sideways / up (a three-quarter or low angle), the second key pushes in by `push`."""
    d = fw * lens / 13.5
    hh = fw * 24.0 / 13.5
    tx = h[0] + (0.5 - fx) * fw + tdx
    tz = h[2] - (0.5 - fy) * hh
    a = [tx + ccx, h[1] - d, tz + ccz]
    b = [tx + ccx * 0.7, h[1] - d * (1 - push), tz + ccz * 0.7]
    return mv(a, [tx, h[1], tz], lens, b, [tx, h[1], tz], lens)


GX, GY = G.G_POS
GHD = (GX, GY, G.G_HEAD)
MEX, MEY = G.ME_POS
FX, FY = G.ME_FRONT
HM = G.ME_HEAD
GP = [GX, GY]


def grandpa_sit(at, on=True):
    cue(at, "sit", who="grandpa", on=on, z=G.G_HIP)


# ---------------------------------------------------------------------------------------------- opening cues
cue(0, "look", id="day", dur=0)
cue(0, "tag", g=0.0, m=9.0)
grandpa_sit(0)
cue(0, "tile", u=0.0)
cue(0, "hat", u=0.0)
cue(0, "bdoor", u=0.0)
cue(0, "fdoor", u=0.0)
cue(0, "newmark", v=0.0)
cue(0, "item", key=0.0, hinge=0.0, tomato=0.0, faucet=0.0)

# ===== 01 the rule (L01 to L05)
put("grandpa", 0, GP, 0, expr="neutral")
put("me", 0, [MEX, MEY], 0, expr="neutral")
shot(0, fc(GHD, 1.9, 34, fx=0.35, fy=0.5, push=0.06), "face1")
shot("L01.3", fc(GHD, 1.1, 40, fx=0.5, fy=0.48, push=0.22), "face1b")
# L02: me beside him, a sideways look
put("me", "L02", [FX, FY], 0, expr="neutral", head=[-35, 0])
beat("grandpa", "L02", expr="neutral")
beat("grandpa", "L02.2", expr="polite", head=[18, 0])
shot("L02", fc((2.4, 0.8, 1.85), 2.1, 34, fx=0.5, fy=0.5, push=0.1), "two")
shot("L02.2", fc((FX, FY, HM), 1.1, 40, fx=0.5, fy=0.45, push=0.15), "mefix")
# L03: the dad at the cafe door
only("L03", ["dad1"])
cx0, cy0 = G.CAFE
put("dad1", "L03", [cx0, cy0 - 0.9], 0, expr="grin", lean=26, head=[0, 8], arms=[0, 40])
beat("dad1", "L03.1", expr="smile", lean=34, head=[0, 14])
shot("L03", fc((cx0, cy0 - 1.2, 1.62), 1.8, 34, fx=0.55, fy=0.5, push=0.12), "dad")
shot("L03.1", fc((cx0, cy0 - 1.2, 1.55), 1.5, 40, fx=0.55, fy=0.5, push=0.12, ccx=0.5), "dad2")
# L04: the mail carrier and her tomatoes
only("L04", ["mail"])
gx, gy = G.GARDEN
put("mail", "L04", [gx, gy + 1.0], 0, expr="smile", arms=[0, 0])
shot("L04", fc((gx, gy + 1.0, 1.97), 2.5, 34, fx=0.52, fy=0.4, push=0.1, ccz=-0.7), "mail")
beat("mail", "L04.1-0.2", expr="smile", arms=[0, 92])
cue("L04.1-0.2", "item", tomato=1.0)
shot("L04.1", fc((gx, gy + 1.0, 1.97), 1.7, 40, fx=0.3, fy=0.4, push=0.1), "tomato")
beat("mail", "L04.2", expr="smile", arms=[0, 0])
cue("L04.2", "item", tomato=0.0)
shot("L04.2", fc((gx, gy + 1.0, 1.97), 2.1, 30, fx=0.5, fy=0.36, push=0.1, ccz=-0.9), "mail2")
# L05: the bride's dad dances on his knees
only("L05", ["bridedad"])
wx, wy = G.WEDDING
put("bridedad", "L05", [wx, wy, -0.74], 0, expr="smile", arms=[70, 70])
beat("bridedad", "L05.1", expr="grin", arms=[20, 120], head=[10, 0], lean=-6)
go("bridedad", "L05>", [wx + 0.2, wy, -0.74])
shot("L05", fc((wx, wy, 0.5 + 0.95), 1.9, 34, fx=0.55, fy=0.46, push=0.1), "bride")
shot("L05.1", fc((wx, wy, 1.4), 1.5, 42, fx=0.5, fy=0.46, push=0.15, ccx=-0.4), "bride2")

# ===== 02 Grandpa (L06 to L15)
only("L06", ["grandpa"])
put("grandpa", "L06", GP, 0, expr="neutral")
shot("L06", fc(GHD, 1.7, 36, fx=0.5, fy=0.48, push=0.1), "gpa")
only("L06.1", ["grandpa", "me"])
put("grandpa", "L06.1", GP, 0, expr="neutral")
put("me", "L06.1", [MEX, MEY], 0, expr="neutral")
shot("L06.1", mv([2.0, -5.0, 1.9], [2.3, 1.2, 1.7], 28, [2.2, -4.3, 1.9], [2.4, 1.2, 1.7], 28), "shopwide")
# L07: from low and to the side, under the hat shelf (the cover frame)
only("L07", ["grandpa"])
put("grandpa", "L07", GP, 0, expr="neutral", head=[-12, 0])
shot("L07", mv([1.4, -1.8, 1.1], [3.4, 1.0, 2.25], 30, [1.7, -1.5, 1.2], [3.4, 1.0, 2.3], 30), "low")
shot("L07+0.9", fc(GHD, 1.5, 36, fx=0.45, fy=0.5, push=0.12, ccx=-1.0, ccz=-0.4), "low2")
# L08: the crate, then his face across the counter
beat("grandpa", "L08", expr="neutral", head=[0, 0])
shot("L08", mv([3.2, -2.6, 1.5], [3.1, 1.0, 1.75], 26, [3.2, -2.3, 1.55], [3.1, 1.0, 1.77], 26), "crate")
put("cust", "L08.1", [2.1, -1.1], 180, expr="neutral", lean=0)
beat("grandpa", "L08.1", expr="smile")
shot("L08.1", mv([2.2, -1.9, 1.75], [3.15, 1.0, 2.0], 40, [2.4, -1.7, 1.78], [3.15, 1.0, 2.0], 40), "cust")
only("L09", ["grandpa"])
beat("grandpa", "L09", expr="neutral")
beat("grandpa", "L09.1", head=[0, 12])
beat("grandpa", "L09.1+0.35", head=[0, -2])
shot("L09", fc(GHD, 1.1, 42, fx=0.5, fy=0.48, push=0.12), "nod")
# L10: me, glum, Grandpa soft behind
only("L10", ["me", "grandpa"])
put("me", "L10", [FX, FY], 0, expr="worried", head=[0, 6])
put("grandpa", "L10", GP, 0, expr="neutral")
shot("L10", fc((2.4, 0.8, 1.85), 2.1, 34, fx=0.5, fy=0.5, push=0.12, ccx=-0.7), "meglum")
# L11: Saturdays at his counter; the key machine's vise
put("me", "L11", [FX, FY], 0, expr="neutral", arms=[0, 92], head=[-20, 0])
cue("L11", "item", key=1.0)
shot("L11", fc((2.4, 0.8, 1.85), 2.1, 34, fx=0.5, fy=0.5, push=0.12, ccx=0.4), "keyslide")
cue("L11.2", "item", key=0.0)
only("L11.1", [])
shot("L11.1", mv([-1.94, -1.05, 1.5], [-1.9, -0.3, 1.45], 50, [-1.94, -0.85, 1.5], [-1.9, -0.3, 1.45], 50), "vise")
put("me", "L11.2", [MEX, MEY], 0, expr="neutral")
shot("L11.2", mv([0.4, -2.6, 1.7], [0.3, 0.6, 1.5], 30, [0.7, -2.2, 1.7], [0.5, 0.6, 1.5], 30), "counter")
# L12: my face
only("L12", ["me"])
put("me", "L12", [MEX, MEY], 0, expr="sad-smile", head=[0, 8])
shot("L12", fc((MEX, MEY, HM), 1.1, 40, fx=0.55, fy=0.5, push=0.14), "meface")
# L13: both of us, me looking up at him
only("L13", ["me", "grandpa"])
put("me", "L13", [FX, FY], 0, expr="sad-smile", head=[-30, -18])
put("grandpa", "L13", GP, 0, expr="neutral", head=[20, 8])
shot("L13", fc((2.4, 0.8, 1.85), 2.1, 34, fx=0.5, fy=0.5, push=0.1), "look-up")
# L14: the hems
only("L14", ["grandpa"])
put("grandpa", "L14", GP, 0, expr="neutral")
shot("L14", mv([1.85, -0.35, 0.8], [2.85, 0.32, 0.62], 28, [1.95, -0.1, 0.75], [2.85, 0.32, 0.62], 28), "hems")
beat("grandpa", "L14.1", expr="polite")
shot("L14.1", fc(GHD, 1.1, 42, fx=0.5, fy=0.48, push=0.12), "sheepish")
# L15: the hat comes down; the broken hinge waits on the counter
cue("L15", "item", hinge=1.0)
beat("grandpa", "L15", expr="neutral", side=[0, 170], blend=0.2)
cue("L15+0.3", "hat", u=1.0, dur=0.9)
beat("grandpa", "L15+0.4", side=[0, 40], blend=0.8)
shot("L15", fc((GX, GY, 2.0), 3.0, 34, fx=0.8, fy=0.5, push=0.1), "hat")

# ===== 03 the dark shop (L16 to L20)
only("L16", ["me"])
cue("L16", "look", id="dark", dur=0)
cue("L16", "item", hinge=0.0)
cue("L16", "hat", u=0.0)
cue("L16", "fdoor", u=0.0)
cue("L16+0.1", "fdoor", u=1.0, dur=0.6)
put("me", "L16", [G.FDOOR_X, G.FRONT_Y - 0.5], 180, expr="neutral")
go("me", "L16+0.7", [G.FDOOR_X, G.FRONT_Y - 0.5])
shot("L16", mv([-4.6, -2.0, 1.55], [G.FDOOR_X, G.FRONT_Y, 1.5], 32, [-4.9, -2.4, 1.55], [G.FDOOR_X, G.FRONT_Y, 1.5], 32), "door")
put("me", "L16.1", [-4.9, -3.6], 180, expr="neutral")
go("me", "L16>", [-4.9, -2.7])
shot("L16.1", mv([-4.9, -0.8, 1.6], [-4.9, -3.2, 1.45], 34, [-4.9, -1.2, 1.6], [-4.9, -3.2, 1.45], 34), "enter")
only("L17", [])
shot("L17", mv([-6.2, -4.6, 1.5], [-1.0, 2.0, 1.4], 26, [-5.6, -4.2, 1.5], [-0.6, 2.0, 1.4], 26), "darkshop")
put("me", "L18", [-1.0, -2.2], 0, expr="worried", head=[0, 6])
shot("L18", fc((-1.0, -2.2, HM), 1.1, 40, fx=0.5, fy=0.46, push=0.15), "listen")
beat("me", "L18.1", expr="worried", head=[28, 4])
only("L18.2", [])
shot("L18.2", mv([-3.5, -2.6, 1.3], [0.0, 0.5, 1.2], 30, [-3.1, -2.4, 1.3], [0.4, 0.5, 1.2], 30), "murmur")
shot("L19", mv([2.2, -0.9, 0.9], [3.1, 1.0, 3.3], 28, [2.5, -0.6, 0.9], [3.1, 1.0, 3.35], 28), "ceiling")
cue("L19", "tile", u=0.04, dur=0.6)
cue("L19+0.9", "tile", u=0.0, dur=0.3)
shot("P01", mv([1.4, -0.4, 0.8], [3.1, 1.0, 3.35], 30, [1.6, -0.2, 0.8], [3.1, 1.0, 3.38], 30), "ceiling2")
shot("L20", mv([2.9, -0.2, 1.0], [3.1, 1.0, 3.3], 34, [3.0, 0.2, 1.1], [3.1, 1.0, 3.35], 34), "tile")
cue("L20+0.1", "tile", u=0.15, dur=0.8)

# ===== 04 the lights, Mrs. Bloom (L21 to L28)
only("L21", ["bloom"])
cue("L21", "look", id="day", dur=0.5)
put("bloom", "L21", [FX, FY], 0, expr="smile")
grandpa_sit("L21")
shot("L21", fc((FX, FY, HM), 1.2, 40, fx=0.5, fy=0.46, push=0.12), "bloom")
put("grandpa", "L21.2", GP, 0, expr="neutral")
put("bloom", "L21.2", [FX, FY], 0, expr="smile")
beat("grandpa", "L21.2+0.5", expr="warm")
shot("L21.2", fc((2.4, 0.8, 1.85), 2.1, 34, fx=0.5, fy=0.5, push=0.1), "bloomgpa")
only("L22", ["bloom"])
put("bloom", "L22", [FX, FY], 0, expr="smile", arms=[0, 92])
cue("L22", "item", faucet=1.0)
shot("L22", fc((FX, FY, HM), 1.6, 38, fx=0.32, fy=0.46, push=0.15), "faucet")
beat("bloom", "L23", expr="warm", arms=[0, 92])
shot("L23", fc((FX, FY, HM), 1.1, 40, fx=0.5, fy=0.45, push=0.14), "bloom2")
cue("L24", "item", faucet=0.0)
only("L24", ["grandpa"])
put("grandpa", "L24", GP, 0, expr="warm", head=[-12, 0])
cue("L24+0.6", "tag", g=1.0)
shot("L24", fc(GHD, 1.5, 36, fx=0.52, fy=0.5, push=0.12), "gpatag")
only("L25", ["grandpa"])
beat("grandpa", "L25", expr="warm", head=[0, 10])
beat("grandpa", "L25.1", head=[0, -2])
shot("L25", fc(GHD, 1.1, 42, fx=0.5, fy=0.47, push=0.14), "gpanod")
beat("grandpa", "L26", expr="smile", head=[10, 0])
shot("L26", fc(GHD, 3.0, 30, fx=0.76, fy=0.5, push=0.08), "gpacounter")
only("L27", ["grandpa"])
beat("grandpa", "L27", expr="smile", head=[-25, 0])
beat("grandpa", "L27.1", head=[-10, 5])
shot("L27", fc(GHD, 1.2, 40, fx=0.5, fy=0.47, push=0.14), "gpasmile")
only("L28", ["bloom", "grandpa"])
put("bloom", "L28", [FX, FY], 0, expr="warm", head=[22, 0])
put("grandpa", "L28", GP, 0, expr="neutral")
shot("L28", fc((FX, FY, HM), 1.2, 40, fx=0.4, fy=0.46, push=0.12, ccx=-0.4), "bloomnod")

# ===== 05 the marked frame (L29 to L36)
only("L29", [])
shot("L29", mv([1.9, 0.6, 1.9], [1.85, 4.4, 2.05], 24, [1.9, 1.0, 2.0], [1.85, 4.4, 2.1], 24), "marks")
shot("L29.1", mv([1.75, 2.6, 1.5], [1.8, 4.4, 1.6], 34, [1.75, 2.8, 2.5], [1.8, 4.4, 2.7], 34), "tilt")
shot("L30", mv([1.95, 3.0, 2.25], [1.8, 4.4, 2.3], 50, [1.95, 3.25, 2.3], [1.8, 4.4, 2.3], 50), "onemark")
put("me", "L31", [2.55, 4.0], 0, expr="smile", head=[20, 0])
shot("L31", fc((2.55, 4.0, HM), 1.9, 32, fx=0.64, fy=0.58, push=0.1), "meframe")
only("L32", [])
shot("L32", mv([1.95, 3.2, 2.3], [1.85, 4.4, 2.31], 55, [1.95, 3.5, 2.3], [1.85, 4.4, 2.31], 55), "bike")
shot("L32.1", mv([2.0, 3.2, 2.45], [1.9, 4.4, 2.43], 55, [2.0, 3.5, 2.45], [1.9, 4.4, 2.43], 55), "roof")
only("L33", ["grandpa"])
put("grandpa", "L33", GP, 0, expr="warm")
shot("L33", fc(GHD, 2.2, 34, fx=0.72, fy=0.55, push=0.05, ccx=0.0), "reveal")
only("L34", ["bloom"])
put("bloom", "L34", [FX, FY], 0, expr="smile", arms=[0, 92])
cue("L34", "item", faucet=1.0)
cue("L35", "item", faucet=0.0)
shot("L34", fc((FX, FY, HM), 1.3, 38, fx=0.3, fy=0.46, push=0.12), "bloom3")
only("L35", ["me"])
put("me", "L35", [FX, FY], 0, expr="sad-smile", head=[0, 6])
shot("L35", fc((FX, FY, HM), 1.1, 40, fx=0.55, fy=0.46, push=0.14), "meglum2")
only("L36", ["grandpa", "me"])
put("grandpa", "L36", GP, 0, expr="neutral")
put("me", "L36", [FX, FY], 0, expr="neutral", arms=[0, 92])
cue("L36", "item", key=1.0)
shot("L36", fc((2.4, GY, G.G_HEAD), 2.4, 34, fx=0.5, fy=0.5, push=0.1), "gpahand")

# ===== 06 the fix (L37 to L45)
cue("L37", "item", key=0.0)
only("L37", ["me"])
put("me", "L37", [2.3, 3.9], 0, expr="smirk", lean=6)
cue("L37+0.4", "bdoor", u=0.0)
cue("L37+0.5", "bdoor", u=0.025, dur=0.2)
cue("L37+0.8", "bdoor", u=0.0, dur=0.2)
cue("L37+1.1", "bdoor", u=0.03, dur=0.2)
cue("L37+1.4", "bdoor", u=0.0, dur=0.2)
shot("L37", fc((2.5, 3.9, HM), 2.0, 32, fx=0.52, fy=0.5, push=0.12), "stuck")
cue("L38-0.2", "bdoor", u=1.0, dur=0.5)
only("L38", [])
shot("L38", mv([2.75, 1.4, 1.35], [2.75, 4.5, 1.3], 28, [2.75, 1.8, 1.4], [2.75, 4.5, 1.3], 28), "swing")
only("L38.1", ["me"])
put("me", "L38.1", [MEX, MEY], 0, expr="smile")
shot("L38.1", fc((MEX, MEY, HM), 1.1, 40, fx=0.52, fy=0.46, push=0.14), "mefix2")
only("L39", ["grandpa"])
put("grandpa", "L39", GP, 0, expr="neutral", head=[-10, 0])
shot("L39", fc(GHD, 1.1, 42, fx=0.5, fy=0.48, push=0.14), "long")
cue("L39.1", "look", id="day", dur=0)
beat("grandpa", "L40", expr="warm", head=[-12, 0])
shot("L40", fc(GHD, 1.3, 40, fx=0.5, fy=0.47, push=0.12), "said")
only("L40.2", ["me"])
put("me", "L40.2", [FX, FY], 0, expr="smile", head=[-25, -10])
shot("L40.2", fc((FX, FY, HM), 1.1, 42, fx=0.5, fy=0.46, push=0.14), "meface2")
only("L41", [])
cue("L41", "tile", u=0.15)
cue("L41+0.1", "tile", u=1.0, dur=0.7)
cue("L41+0.1", "dust", dur=1.1)
shot("L41", mv([2.3, -0.2, 0.9], [3.1, 1.0, 3.2], 28, [2.5, 0.1, 1.0], [3.1, 1.0, 3.4], 28), "pop")
only("L41.1", ["grandpa"])
put("grandpa", "L41.1", GP, 0, expr="smile", head=[0, -8])
cue("L41.1", "tag", g=2.0)
shot("L41.1", fc(GHD, 1.5, 34, fx=0.5, fy=0.56, push=0.1), "gpaunder")
only("L42", ["grandpa", "me"])
put("grandpa", "L42", GP, 0, expr="warm", head=[18, 8])
put("me", "L42", [FX, FY], 0, expr="smile", head=[-25, -15])
shot("L42", fc((2.4, 0.8, 1.85), 2.1, 34, fx=0.5, fy=0.5, push=0.1), "sayback")
only("L43", ["me"])
put("me", "L43", [FX, FY], 0, expr="smile")
cue("L43+0.15", "tag", m=10.0)
shot("L43", fc((FX, FY, HM), 1.1, 40, fx=0.55, fy=0.46, push=0.1), "mytag")
beat("me", "L43.1", expr="laugh", head=[0, -6])
shot("L43.1", fc((FX, FY, HM), 1.0, 44, fx=0.5, fy=0.46, push=0.16), "mylaugh")
# L44: Grandpa stooped through the back doorway, me beside him, the new mark
only("L44", ["grandpa", "me"])
grandpa_sit("L44", False)
put("grandpa", "L44", [2.85, 3.9], 0, expr="smile", lean=24, head=[0, -6])
put("me", "L44", [1.6, 3.75], 0, expr="smile")
cue("L44+0.3", "newmark", v=1.0)
shot("L44", fc((2.5, 3.7, 2.0), 3.0, 30, fx=0.55, fy=0.5, push=0.1), "doorway")
only("L45", ["me"])
put("me", "L45", [MEX, MEY], 0, expr="smile")
shot("L45", fc((MEX, MEY, HM), 1.1, 40, fx=0.5, fy=0.46, push=0.12), "mylast")
only("L45.1", ["grandpa"])
grandpa_sit("L45.1")
put("grandpa", "L45.1", GP, 0, expr="neutral")
shot("L45.1", fc(GHD, 1.9, 34, fx=0.35, fy=0.5, push=0.06), "face1")

# ---------------------------------------------------------------------------------------------- finish
for k_ in acting.values():
    remap_all(k_)
remap_all(cues)
shots, names = [], {}
for i, (at, camera, step, hand, nm) in enumerate(SH):
    s = {"id": f"S{i + 1:02d}", "cam": camera, "step": step}
    if i:
        s["at"] = remap(at)
    if hand is not None:
        s["hand"] = hand
    shots.append(s)
    names.setdefault(nm, s["id"])

sfx = [
    {"at": "L01>-0.35", "kind": "thud", "db": -8},
    {"at": "L01>-0.3", "kind": "creak", "db": -16, "dur": 0.6},
    {"at": "L19", "kind": "creak", "db": -14, "dur": 1.6},
    {"at": "L20+0.5", "kind": "creak", "db": -18, "dur": 0.8},
    {"at": "L24+0.6", "kind": "click", "db": -22},
    {"at": "L38+0.1", "kind": "door", "db": -12},
    {"at": "L41+0.15", "kind": "click", "db": -14},
    {"at": "L43+0.15", "kind": "click", "db": -22},
]
music = {
    "root": 53, "mode": "major", "bpm": 96, "seed": 116,
    "sections": [
        {"at": 0, "voices": ["piano", "pulse"], "energy": 0.4, "root": 53, "mode": "major"},
        {"at": "L16", "voices": ["drone"], "energy": 0.25, "root": 41, "mode": "minor"},
        {"at": "L20", "voices": ["drone", "pad"], "energy": 0.3, "root": 41, "mode": "minor"},
        {"at": "L23", "voices": ["piano", "pad"], "energy": 0.45, "root": 53, "mode": "major"},
        {"at": "L33", "voices": ["pad"], "energy": 0.4, "root": 53, "mode": "major"},
        {"at": "L37", "voices": ["piano", "pad", "pulse"], "energy": 0.65, "root": 53, "mode": "major"},
    ],
}
sound = {
    "floor": "wood", "steps_db": -26,
    "ambience": [{"kind": "hum", "from": "L21", "to": "L22", "lufs": -40}],
    "sfx": sfx,
    "music_drops": [{"from": "P01", "to": "P01>"}],
    "rev": REV,
}
remap_all(sfx)
remap_all(music["sections"])
remap_all(sound["music_drops"])
remap_all(sound["ambience"])
polish = {"reveal": [remap("L33.0"), remap("L41")], "emph": [remap(x) for x in ["L01.3", "L04.2", "L07", "L08", "L19", "L33.0", "L38.1", "L43"]],
          "twist": remap("L33.0")}
story = {
    "slug": "ep116-proud-inch",
    "title": "Grandpa Is Nine Feet TALL 📏",
    "made_for_kids": False,
    "premise": ("In a town where saying you're proud of someone makes you grow an inch, my quiet hardware-store grandpa "
                "is nine feet tall and has never said it to me."),
    "twist": ("He says it to anyone in town who fixes something with their own hands, one pencil mark per inch on his "
              "door frame, and I've never fixed a thing myself, so I fix the stuck back door, he says it to my face, "
              "and I say it back and grow my first inch."),
    "world": ("A bright little hardware store on a sunny main street: mint shelves of bins, a honey-wood counter, a key "
              "machine, an upturned crate behind the counter, a front window full of sun and a back doorway whose "
              "cream frame is covered in pencil marks."),
    "voice": {"voice": "am_adam", "tempo": 1.03, "rate": 1.45},
    "key_color": "#ffcf3a",
    "gap": 0.12,
    "tail": 0.25,
    "fade_in": False,
    "fade_out": False,
    "rev": REV,
    "look": {"style": "closer", "fog": "#e8f2ff", "fog_density": 0.0015, "fog_start": 40.0, "sky": "#9fd8ff",
             "sky_strength": 1.0, "exposure": 0.0, "flash_safe": True, "polish": polish},
    "grade": {"shadows": [0.0, 0.0, 0.03], "highlights": [0.03, 0.012, -0.02], "saturation": 1.1, "contrast": 1.05,
              "vignette": 0.2, "bloom": 0.2, "grain": 0.008},
    "phonemes": {},
    "cast": cast,
    "lines": lines,
    "shots": shots,
    "acting": acting,
    "cues": cues,
    "fx": [],
    "music": music,
    "sound": sound,
    "set_moves": [names["tile"], names["pop"], names["swing"], names["door"]],
    "clip_ok": [],
    "asr_forgive": ["dads duck", "mail", "he's", "said"],
}
OUT.write_text(json.dumps(story, indent=1, ensure_ascii=False) + "\n")
print("wrote", OUT, f"({len(shots)} shots, {len(cues)} cues)")
