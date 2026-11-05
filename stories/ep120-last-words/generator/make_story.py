"""Writes ../story.json for ep120 "Dad's Place Still Says My Last WORDS" (script.md, 2026-11-05, batch 12).
Run: python stories/ep120-last-words/generator/make_story.py

The words are in lines.json. Places are in ../layout.py (shared with set.py). A character facing -y has yaw 0, +x 90,
+y 180, -x -90. Time references are line starts plus seconds ("L05+1.2"), so a re-chunk of a caption can't move a shot.
Captions are split to two or three words.
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
REV = 8
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
# the 0.6 s music drop before L22
idx = next(i for i, l in enumerate(lines) if l["id"] == "L22")
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


D2R = math.pi / 180
HALLX, HALLY = G.HALL
KX, KY = G.KITCHEN
LVX, LVY = G.LIVING
LX, LY = G.LOT
CBX, CBY = G.CAB
NX, NY = G.SHOP
SIX, SIY = G.SHOPIN
DX, DY = G.DAY_SHOP
AZ = G.APT_Z
RZ = G.ROOM_Z
RY = LY + G.ROOM_Y0

# ----------------------------------------------------------------------------------------------------- cast
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
    "me": person("#d9a67a", "#2f4a7a", "#3f5f8f", "#4a3a2a", hair="cap", hair_c="#120f0e", collar="#aab0bb",
                 extras=["hooddown"], extra_c="#aab0bb", brow_w=1.4),
    "dad": person("#e0b088", "#c0392b", "#3b6ea8", "#3a2a1a", hair="cap", hair_c="#8e8e98", pattern="plaid",
                  pattern_c="#7a1f18", collar="#f4f4f2", brow_w=1.6, width=1.06),
    "neighbor": person("#e8b48c", "#7fcfae", "#f1ead8", "#8a6a4a", hair="long", hair_c="#7a4a2c", eyes="lashes",
                       brow_w=1.9, pattern="knit", pattern_c="#5fb494"),
    "ray": person("#b98456", "#e8a838", "#4a4036", "#2a2a2a", hair="spiky", hair_c="#1a1410", sleeves="short"),
}
acting = {n: [{"at": 0, "hidden": True, "pos": [0, 0], "lean": 0, "arms": [0, 0], "side": [0, 0], "head": [0, 0], "yaw": 0}] for n in cast}
last = {n: [0, 0] for n in cast}
visible = set()
cues = []
SH = []

EX = {"glum": "worried", "uneasy": "worried", "sheepish": "sad-smile", "stunned": "wide", "determined": "neutral",
      "scared": "scared", "smile": "smile", "warm": "warm", "laugh": "laugh", "angry": "angry", "neutral": "neutral",
      "asleep": "asleep", "soft": "soft"}


def put(who, at, pos, yaw=None, **kw):
    p = list(pos)
    acting[who].append({"at": at, "pos": list(last[who])})
    k = {"at": at, "pos": p, "blend": 0.0, "hidden": False}
    if yaw is not None:
        k["yaw"] = yaw
    if "expr" in kw:
        kw["expr"] = EX.get(kw["expr"], kw["expr"])
    k.update(kw)
    acting[who].append(k)
    last[who] = p
    visible.add(who)


def go(who, at, pos, **kw):
    p = list(pos)
    if "expr" in kw:
        kw["expr"] = EX.get(kw["expr"], kw["expr"])
    acting[who].append({"at": at, "pos": p, **kw})
    last[who] = p


def beat(who, at, **kw):
    if "expr" in kw:
        kw["expr"] = EX.get(kw["expr"], kw["expr"])
    acting[who].append({"at": at, "pos": list(last[who]), **kw})


def only(at, names):
    for w in list(visible):
        if w not in names:
            acting[w].append({"at": at, "hidden": True})
            visible.discard(w)


def talk(who, a, b, amt=0.7):
    acting[who].append({"from": a, "to": b, "mouth": [amt, amt], "flap": True})


def cue(at, name, **kw):
    cues.append({"at": at, "name": name, **kw})


def sit(who, at, on=True, z=0.62):
    cue(at, "sit", who=who, on=on, z=z)


def rip(at, x, y, z, s=1.0, ax=1.0, yaw=0.0, k=1.0, dur=0.0):
    cue(at, "ripple", on=1.0, x=x, y=y, z=z, s=s, ax=ax, yaw=yaw, k=k, dur=dur)


def rip_off(at):
    cue(at, "ripple", on=0.0, dur=0.0)


# ---------------------------------------------------------------------------------------------------- cameras
def mv(p0, t0, l0, p1=None, t1=None, l1=None, push=0.09):
    if p1 is None:
        p1 = [p0[i] + (t0[i] - p0[i]) * push for i in range(3)]
        t1 = t0
    return [[0, list(p0), list(t0), l0], [1, list(p1), list(t1 if t1 is not None else t0), l1 or l0]]


def fc(pos, yaw, d=3.0, lens=40, aimz=1.38, side=0.0, lift=0.05, dx=0.0, push=0.09, z0=None):
    """A camera in front of a face: d metres out along where it looks (yaw), turned `side` degrees round it."""
    x, y = pos[0], pos[1]
    z = pos[2] if len(pos) > 2 else 0.0
    a = (yaw + side) * D2R
    cx, cy = x + d * math.sin(a), y - d * math.cos(a)
    perp = (math.cos(a), math.sin(a))
    cx += dx * perp[0]
    cy += dx * perp[1]
    tgt = [x + dx * perp[0], y + dx * perp[1], z + aimz]
    return mv([cx, cy, z + aimz + lift], tgt, lens, push=push)


def shot(at, camera, name, step=2, hand=None):  # noqa
    SH.append((at, camera, step, hand, name))


def F(at, who, pos, yaw, expr, name, d=3.0, lens=40, side=0.0, aimz=1.38, dx=0.0, lift=0.05, push=0.09, hand=None, **kw):
    """A shot of one character's face: places them and frames them."""
    put(who, at, pos, yaw, expr=expr, **kw)
    shot(at, fc(pos, yaw, d, lens, aimz, side, lift, dx, push), name, hand=hand)


# ================================================================================================ the film
cue(0, "days", n=731.0)
cue("L09", "days", n=0.0)
cue("L10", "days", n=731.0)
cue("L32", "days", n=0.0)
cue("L31", "lamp", v=0.0)
cue("L34", "lamp", v=0.0)
cue("L34+0.02", "lamp", v=1.0, dur=0.5)
cue("L10", "door", v=0.0, dur=0.15)
cue("L33", "door", v=1.0, dur=0.9)
cue("L60", "dust", v=0.0)
cue("L20-0.1", "roomlamp", v=0.0, dur=0.4)
cue("L06", "dog", v=1.0)
cue("L09", "lamp", v=0.45)
cue("L10", "lamp", v=1.0, dur=0.4)
cue("L09", "fill", v=0.3)
cue("L10", "fill", v=1.0, dur=0.4)

# ---------------------------------------------------------------------------------------- 01 the rule (L01..L07)
HM = (HALLX + 0.85, HALLY + 3.6)
put("me", 0, HM, 0, expr="neutral", head=[0, 0])
rip(0, HALLX + 0.2, HALLY + 2.4, 1.4, s=1.35)
shot(0, mv([HALLX + 0.55, HALLY + 0.8, 1.55], [HALLX + 0.88, HALLY + 4.4, 1.5], 30, push=0.08), "door1")
shot("L01+1.1", mv([HALLX - 0.2, HALLY - 1.6, 0.85], [HALLX + 0.2, HALLY + 4.4, 1.3], 28, push=0.1), "hallripple")
shot("L01+2.15", mv([HALLX + 0.0, HALLY + 1.0, 1.45], [HALLX + 0.85, HALLY + 4.4, 1.45], 36, push=0.1), "door2")
beat("me", "L01+2.2", expr="worried")
F("L02", "me", HM, 0, "uneasy", "meface1", d=2.8, lens=38, aimz=1.4)
rip("L02", HALLX + 0.6, HALLY + 2.6, 1.6, s=0.8)
put("neighbor", "L03", [HALLX - 0.1, HALLY + 4.0], 0, expr="smile")
go("neighbor", "L03+1.3", [HALLX - 0.2, HALLY + 2.4])
talk("neighbor", "L03", "L03>")
only("L03", ["neighbor", "me"])
rip("L03", HALLX, HALLY + 2.8, 1.4, s=1.1, ax=1.7)
shot("L03", mv([HALLX + 0.4, HALLY - 0.4, 1.45], [HALLX - 0.1, HALLY + 3.2, 1.45], 34, push=0.1), "woman")
shot("L03+0.9", mv([HALLX - 0.4, HALLY - 0.3, 1.6], [HALLX - 0.2, HALLY + 2.4, 1.55], 46, push=0.1), "woman2")
# L04: the house for sale, then its empty kitchen
only("L04", [])
rip("L04", -14.0, 7.7, 1.4, s=1.0)
shot("L04", mv([-8.8, 0.6, 1.5], [-13.6, 8.0, 1.5], 30, [-9.6, 1.4, 1.5], [-13.6, 8.0, 1.5], 30), "forsale")
rip("L04+1.1", KX, KY + 3.6, 1.35, s=1.0, ax=1.4)
shot("L04+1.1", mv([KX + 1.0, KY - 0.8, 1.35], [KX, KY + 4.0, 1.1], 30, push=0.1), "kitchen")
# L05: the woman at her door
put("neighbor", "L05", [-2.0, 6.9, 0.18], 0, expr="smile", arms=[0, 0])
go("neighbor", "L05+1.2", [-2.0, 6.7, 0.18], arms=[0, 120])
beat("neighbor", "L05+1.7", arms=[0, 60])
talk("neighbor", "L05+0.2", "L05+1.7", 0.6)
shot("L05", mv([-0.7, 1.3, 1.65], [-2.0, 6.9, 1.55], 36, [-1.0, 1.9, 1.65], [-2.0, 6.9, 1.55], 36), "woman_door")
rip_off("L05")
shot("L05+1.1", fc([-2.0, 6.7, 0.18], 0, d=3.2, lens=40, aimz=1.4, side=12), "woman_face")
only("L05", ["neighbor"])
# L06: the dog
only("L06", [])
rip("L06+0.9", LVX + 0.2, LVY + 3.0, 1.3, s=0.8, ax=1.2, k=0.6)
shot("L06", mv([LVX + 0.5, LVY + 1.0, 1.2], [LVX + 0.2, LVY + 3.8, 0.95], 34, push=0.1), "dog")
shot("L06+0.9", mv([LVX - 0.4, LVY + 2.0, 0.85], [LVX + 0.2, LVY + 3.8, 0.9], 30, push=0.1), "dogtail")
# L07: Ray at the door of his old place
put("ray", "L07", [10.0, 6.9, 0.18], 0, expr="sheepish")
talk("ray", "L07+0.2", "L07+1.6", 0.6)
only("L07", ["ray"])
rip("L07", 10.0, 7.7, 1.35, s=0.9)
shot("L07", fc([10.0, 6.9, 0.18], 0, d=3.4, lens=38, aimz=1.4, side=-10), "ray_face")
shot("L07+1.2", mv([11.6, 1.8, 1.5], [10.0, 7.2, 1.45], 34, push=0.1), "ray_ripple")
# ------------------------------------------------------------------------------ 02 two years ago (L08..L14)
only("L08", [])
shot("L08", mv([DX - 5.0, DY - 8.0, 2.6], [DX - 0.5, DY, 3.2], 24, [DX - 4.2, DY - 7.4, 2.6], [DX - 0.5, DY, 3.2], 24), "shop_day")
rip_off("L08")
put("dad", "L08+0.85", [DX - 0.4, DY - 3.6], 0, expr="smile", arms=[0, 0])
put("me", "L08+0.85", [DX + 0.4, DY - 3.6], 0, expr="smile", arms=[0, 0])
only("L08+0.85", ["dad", "me"])
cue("L08+0.85", "bezel", v=1.0)
cue("L09", "bezel", v=0.0)
shot("L08+0.85", mv([DX, DY - 6.8, 1.6], [DX, DY - 3.6, 1.5], 25, [DX, DY - 6.3, 1.6], [DX, DY - 3.6, 1.5], 25), "photo")
# L09: me at the door two years ago, Dad behind me
put("me", "L09", [NX + 0.0, NY - 0.7, AZ], 0, expr="angry", arms=[40, 40])
put("dad", "L09", [NX + 0.72, NY + 0.5, AZ], 0, expr="glum")
talk("me", "L09", "L09>", 0.9)
only("L09", ["me", "dad"])
shot("L09", mv([NX + 0.36, NY - 3.7, AZ + 1.5], [NX + 0.36, NY - 0.1, AZ + 1.5], 29, [NX + 0.36, NY - 3.3, AZ + 1.5], [NX + 0.36, NY - 0.1, AZ + 1.5], 29), "shout")
# L10: the door slams, seen from the stair
only("L10", [])
shot("L10", mv([NX - 2.0, NY - 2.6, AZ + 0.8], [NX + 0.5, NY, AZ + 1.2], 30, push=0.12), "slam")
# L11: me now, glum, in my place
F("L11", "me", [LX + 0.2, RY + 3.0, RZ], 0, "glum", "me_home", d=2.5, lens=34, aimz=1.45)
only("L11", ["me"])
# L12: the phone with no calls, then his place yelling it
only("L12", [])
shot("L12", mv([LX + 0.1, RY + 1.4, RZ + 1.5], [LX + 0.1, RY + 2.2, RZ + 0.95], 30, push=0.12), "phone")
rip("L12+1.4", NX - 2.6, NY + 0.4, AZ + 1.5, s=1.1)
shot("L12+1.4", mv([NX - 4.6, NY - 8.0, 3.4], [NX - 2.6, NY, 4.9], 28, [NX - 4.2, NY - 7.2, 3.6], [NX - 2.6, NY, 4.9], 28), "shop_yell")
# L13: driving past the shop by day
rip_off("L13")
rip_off("L13")
put("me", "L13", [DX + 0.2, 0.4 - 0.45, 0], -90, expr="glum", head=[60, 8], arms=[0, 0], lean=0)
sit("me", "L13")
only("L13", ["me"])
cue("L13", "dcar", x=DX + 1.3, dur=0.0)
cue("L13", "ride", dx=1.3, dy=0.0, on=1.0, dur=0.0)
cue("L13+0.02", "dcar", x=DX - 1.3, dur=2.6)
cue("L13+0.02", "ride", dx=-1.3, dy=0.0, on=1.0, dur=2.6)
cue("L14-0.1", "ride", dx=0.0, dy=0.0, on=0.0, dur=0.0)
shot("L13", mv([DX + 2.6, -3.7, 1.55], [DX + 1.5, 0.0, 1.4], 38, [DX + 1.7, -3.7, 1.55], [DX + 0.7, 0.0, 1.4], 38), "drive", hand=0.01)
beat("me", "L13+1.2", arms=[70, 0], head=[55, 10])
# the camera rides along the car beside me, tracking my eased drive offset (the ride cue is a 2.6 s smoothstep)
_ss = lambda x: x * x * (3 - 2 * x)
_rk = []
for _u in (0.0, 0.25, 0.5, 0.75, 1.0):
    _x = DX + 0.2 + 1.3 - 2.6 * _ss((1.18 + _u * 1.42) / 2.6)
    _rk.append([_u, [_x - 0.15, -2.3, 1.5], [_x - 0.15, -0.45, 1.38], 30])
shot("L13+1.2", _rk, "radio", hand=0.01)
# L14: Then the TRUCK started: my face at my window
sit("me", "L14-0.05", on=False)
F("L14", "me", [LX + 0.0, LY + 10.8, RZ], 0, "uneasy", "me_window", d=6.0, lens=52, aimz=1.55)
# the camera floats outside the window, three floors up
SH[-1] = (SH[-1][0], mv([LX + 0.5, LY + 4.8, RZ + 1.7], [LX, LY + 10.8, RZ + 1.55], 52, push=0.07), SH[-1][2], SH[-1][3], SH[-1][4])
only("L14", ["me"])
# ---------------------------------------------------------------------------------- 03 the truck (L15..L21)
TR = (LX - 1.2, LY + 1.2)
cue("L14", "truck", x=LX - 8.0, y=LY - 15.0, yaw=0.0, head=1.0, tail=0.0, door=0.0, shape=1.0, low=0.0)
cue("L15+0.1", "truck", x=TR[0], y=TR[1], yaw=0.0, head=1.0, dur=1.9, shape=1.0)
cue("L16", "truck", head=0.0, dur=0.0)
cue("L18+0.2", "truck", low=1.0, dur=0.9)
only("L15", [])
FROM_WIN = [LX + 0.1, LY + 10.35, RZ + 1.9]
shot("L15", mv(FROM_WIN, [LX - 1.8, LY - 2.0, 1.3], 28, [LX + 0.1, LY + 10.35, RZ + 1.9], [LX - 1.3, LY + 0.4, 1.4], 36), "arrive")
shot("L15+1.3", mv([LX - 2.0, RY + 2.9, RZ + 1.35], [LX - 1.95, RY + 4.8, RZ + 1.18], 28, push=0.1), "clock")
shot("L16", mv(FROM_WIN, [TR[0], TR[1] + 0.5, 1.4], 34, [LX - 0.1, LY + 10.35, RZ + 1.9], [TR[0], TR[1] + 0.3, 1.5], 38), "lightsoff")
shot("L17", mv(FROM_WIN, [TR[0] - 0.55, TR[1] - 0.2, 1.7], 70, [LX + 0.0, LY + 10.35, RZ + 1.9], [TR[0] - 0.4, TR[1] + 0.1, 1.55], 62), "shape1", hand=0.01)
shot("L18", mv(FROM_WIN, [TR[0] - 0.55, TR[1] - 0.2, 1.7], 70, [LX + 0.0, LY + 10.35, RZ + 1.9], [TR[0] - 0.4, TR[1] + 0.3, 1.3], 66), "shape2", hand=0.01)
cue("L19-0.05", "truck", x=TR[0], y=TR[1], yaw=180.0, head=0.0, tail=1.0, shape=0.0, low=0.0, dur=0.0)
cue("L19+0.05", "truck", x=TR[0], y=LY - 16.0, yaw=180.0, tail=1.0, dur=2.4)
shot("L19", mv(FROM_WIN, [TR[0], TR[1] - 1.0, 1.0], 30, [LX + 0.1, LY + 10.35, RZ + 1.9], [TR[0], TR[1] - 5.0, 1.0], 30), "leaves")
put("me", "L20", [LX + 0.0, LY + 10.8, RZ], 0, expr="scared")
shot("L20", mv([LX + 0.55, LY + 5.2, RZ + 1.7], [LX, LY + 10.8, RZ + 1.55], 56, push=0.07), "me_dark")
beat("me", "L21", expr="glum")
shot("L21", mv([LX + 0.3, LY + 7.6, RZ + 1.6], [LX, LY + 10.8, RZ + 1.55], 62, [LX + 0.15, LY + 7.0, RZ + 1.6], [LX, LY + 10.8, RZ + 1.55], 62), "me_dark2")
only("L20", ["me"])
shot("P01", mv([LX + 0.1, LY + 10.35, RZ + 1.9], [LX - 1.3, LY + 0.4, 1.4], 30, push=0.1), "drop")
cue("P01", "truck", x=TR[0], y=TR[1], yaw=0.0, head=0.0, tail=0.0, door=0.0, shape=1.0, low=0.0, dur=0.0)
# ---------------------------------------------------------------------------------- 04 last night (L22..L30)
only("P01", [])
shot("L22", mv(FROM_WIN, [TR[0] - 0.3, TR[1] + 0.3, 1.5], 40, [LX + 0.0, LY + 10.35, RZ + 1.9], [TR[0] - 0.3, TR[1] + 0.3, 1.5], 46), "eleven")
cue("L22+1.2", "truck", shape=0.0, dur=0.0)
cue("L22+1.2", "truck", door=1.0, dur=0.8)
shot("L23", mv([LX - 4.6, LY - 2.4, 1.6], [LX - 2.6, LY + 1.2, 0.95], 30, [LX - 4.5, LY + 3.9, 1.35], [LX - 3.1, LY + 1.4, 0.9], 34), "handle")
put("me", "L23+1.2", [LX, LY + 10.8, RZ], 0, expr="scared")
only("L23+1.2", ["me"])
shot("L23+1.2", mv([LX + 0.55, LY + 5.2, RZ + 1.7], [LX, LY + 10.8, RZ + 1.55], 52, push=0.07), "me_dark3")
only("L24", [])
shot("L24", mv([LX - 4.5, LY + 5.0, 1.8], [LX - 1.6, LY + 1.0, 1.1], 30, [LX - 4.0, LY + 4.4, 1.7], [LX - 1.6, LY + 1.0, 1.1], 30), "empty_cab")
put("me", "L25", [LX + 2.4, LY + 8.0], 0, expr="uneasy")
go("me", "L25+0.9", [LX + 2.0, LY + 4.2])
only("L25", ["me"])
shot("L25", mv([LX + 2.4, LY + 0.6, 1.6], [LX + 2.2, LY + 6.0, 1.5], 42, [LX + 2.4, LY + 0.8, 1.6], [LX + 2.0, LY + 4.6, 1.5], 44), "cross")
only("L26", [])
shot("L26", mv([CBX + 0.3, CBY + 0.55, 1.2], [CBX + 0.05, CBY - 0.1, 0.6], 30, push=0.12), "palm_seat")
shot("L27", mv([CBX + 0.9, CBY + 0.4, 1.15], [CBX + 0.4, CBY - 0.15, 0.7], 34, [CBX + 0.75, CBY + 0.3, 1.0], [CBX + 0.4, CBY - 0.15, 0.7], 34), "thermos")
shot("L27+1.1", mv([CBX + 0.5, CBY + 0.35, 0.82], [CBX + 0.4, CBY - 0.15, 0.7], 50, [CBX + 0.5, CBY + 0.2, 0.8], [CBX + 0.4, CBY - 0.15, 0.7], 50), "dent")
put("me", "L28", [CBX - 0.45, CBY - 0.2], 180, expr="stunned")
sit("me", "L28")
only("L28", ["me"])
shot("L28", mv([CBX - 0.45, CBY + 2.0, 1.7], [CBX - 0.45, CBY - 0.2, 1.5], 27, [CBX - 0.45, CBY + 1.75, 1.68], [CBX - 0.45, CBY - 0.2, 1.5], 27), "me_cab")
only("L29", [])
shot("L29", mv([CBX + 0.6, CBY + 0.3, 0.85], [CBX + 0.4, CBY - 0.15, 0.75], 55, push=0.1), "thermos2")
sit("me", "L30", on=False)
put("me", "L30", [LX + 1.0, LY + 4.6], 0, expr="uneasy", arms=[0, 90])
talk("me", "L30", "L30+1.0", 0.8)
only("L30", ["me"])
shot("L30", fc([LX + 1.0, LY + 4.6], 0, d=4.0, lens=36, aimz=1.45, side=10), "calling")
# ------------------------------------------------------------------------------- 05 Dad's place (L31..L39)
cue("L31", "mycar", x=NX + 1.0, y=NY - 11.0, yaw=0.0, head=1.0, dur=0.0)
cue("L31+0.02", "mycar", y=NY - 9.0, dur=2.2)
cue("L31", "ride", dx=0.0, dy=-2.0, on=1.0, dur=0.0)
cue("L31+0.02", "ride", dx=0.0, dy=0.0, on=1.0, dur=2.2)
cue("L32-0.1", "ride", dx=0.0, dy=0.0, on=0.0, dur=0.0)
put("me", "L31", [NX + 0.55, NY - 9.2], 180, expr="neutral")
sit("me", "L31")
only("L31", ["me"])
shot("L31", mv([NX + 1.2, NY - 5.2, 1.95], [NX + 0.55, NY - 9.2, 1.45], 38, [NX + 1.2, NY - 5.0, 1.95], [NX + 0.55, NY - 9.2, 1.45], 38), "mycar")
cue("L32", "mycar", head=0.0, dur=0.0)
sit("me", "L32", on=False)
only("L32", [])
shot("L32", mv([NX - 3.8, NY - 8.6, 2.4], [NX + 0.5, NY, 3.0], 26, [NX - 3.2, NY - 8.0, 2.5], [NX + 0.5, NY, 3.1], 26), "dark_shop")
put("me", "L33", [NX + 0.45, NY - 0.7, AZ], 0, expr="uneasy")
only("L33", ["me"])
shot("L33", fc([NX + 0.45, NY - 0.7, AZ], 0, d=3.7, lens=34, aimz=1.45, side=8), "door_opens")
only("L34", [])
shot("L34", mv([NX + 0.6, NY + 1.2, AZ + 1.5], [NX + 1.5, NY + 4.5, AZ + 0.75], 22, [NX + 0.6, NY + 1.5, AZ + 1.5], [NX + 1.5, NY + 4.5, AZ + 0.75], 22), "lamp_on")
shot("L35", mv([NX - 0.7, NY + 2.2, AZ + 1.3], [NX + 0.3, NY + 3.9, AZ + 0.7], 36, [NX - 0.5, NY + 2.5, AZ + 1.25], [NX + 0.3, NY + 3.9, AZ + 0.7], 36), "table")
put("me", "L36", [NX + 0.55, NY + 0.55, AZ], 180, expr="uneasy")
only("L36", ["me"])
rip("L36", NX + 0.1, NY + 3.4, AZ + 1.6, s=1.3, yaw=0.0)
shot("L36", mv([NX - 0.3, NY + 5.9, AZ + 1.6], [NX + 0.55, NY + 0.55, AZ + 1.45], 32, push=0.1), "doorway")
put("me", "L37", [NX + 0.5, NY + 2.2, AZ], 0, expr="stunned")
rip("L37", NX + 0.5, NY + 3.8, AZ + 1.45, s=1.3)
shot("L37", mv([NX + 0.55, NY - 1.2, AZ + 1.5], [NX + 0.5, NY + 2.6, AZ + 1.35], 25, [NX + 0.55, NY - 0.8, AZ + 1.5], [NX + 0.5, NY + 2.6, AZ + 1.35], 25), "reveal", hand=0.0)
rip("L38", NX + 0.3, NY + 4.5, AZ + 0.95, s=0.9, ax=1.3)
only("L38", [])
shot("L38", mv([NX - 0.6, NY + 2.2, AZ + 1.5], [NX + 0.3, NY + 4.6, AZ + 0.8], 34, push=0.1), "ripple_chairs")
rip_off("L39")
F("L39", "me", [NX + 0.4, NY + 3.3, AZ], 0, "stunned", "me_stunned", d=2.7, lens=36, aimz=1.45)
only("L39", ["me"])
# ----------------------------------------------------------------------------- 06 Dad's side (L40..L49)
only("L40", [])
put("dad", "L40", [NX + 0.6, NY + 0.45, AZ], 0, expr="glum", side=[0, 50], arms=[0, 0])
only("L40", ["dad"])
shot("L40", mv([NX + 0.6, NY - 1.35, AZ + 1.6], [NX + 0.6, NY + 0.45, AZ + 1.5], 24, [NX + 0.55, NY - 1.25, AZ + 1.6], [NX + 0.6, NY + 0.45, AZ + 1.5], 24), "dad_door")
put("dad", "L40+1.4", [NX + 0.3, NY - 0.7, AZ], 0, expr="glum", arms=[0, 0])
shot("L40+1.4", mv([NX + 1.4, NY - 4.3, AZ + 1.5], [NX + 0.3, NY - 0.7, AZ + 1.5], 36, [NX + 1.2, NY - 4.0, AZ + 1.5], [NX + 0.3, NY - 0.7, AZ + 1.5], 36), "dad_porch")
# L41: at the foot of the stair, face up to the camera
put("dad", "L41", [NX - 4.9, NY - 0.9, 0], 90, expr="glum", head=[0, -22])
shot("L41", mv([NX - 1.0, NY - 0.9, 3.9], [NX - 4.9, NY - 0.9, 1.5], 32, [NX - 1.3, NY - 0.9, 3.7], [NX - 4.9, NY - 0.9, 1.5], 32), "dad_stair")
# L42: asleep on the shop couch (lying on his back, face up)
put("dad", "L42", [SIX + 0.0, SIY + 4.78, 0.0], 0, expr="asleep", lean=0, head=[0, 0], arms=[0, 0])
sit("dad", "L42", z=0.5)
shot("L42", mv([SIX - 0.1, SIY + 1.2, 1.3], [SIX, SIY + 4.75, 1.25], 27, [SIX - 0.1, SIY + 1.7, 1.3], [SIX, SIY + 4.75, 1.25], 27), "dad_couch")
beat("dad", "L43", expr="glum")
shot("L43", mv([SIX - 1.0, SIY + 2.0, 1.4], [SIX, SIY + 4.75, 1.3], 30, [SIX - 0.75, SIY + 2.4, 1.4], [SIX, SIY + 4.75, 1.3], 30), "dad_couch2")
# L44: in his truck's cab, dome light
put("dad", "L44", [CBX - 0.45, CBY - 0.2], 180, expr="glum", lean=0, head=[0, 0])
sit("dad", "L44")
shot("L44", mv([CBX - 0.1, CBY + 1.5, 1.75], [CBX - 0.45, CBY - 0.2, 1.4], 26, [CBX - 0.15, CBY + 1.3, 1.7], [CBX - 0.45, CBY - 0.2, 1.4], 26), "dad_cab")
beat("dad", "L45", expr="sheepish")
talk("dad", "L45+0.1", "L45>", 0.5)
shot("L45", mv([CBX - 0.9, CBY + 1.3, 1.6], [CBX - 0.45, CBY - 0.2, 1.42], 30, [CBX - 0.8, CBY + 1.1, 1.58], [CBX - 0.45, CBY - 0.2, 1.42], 30), "dad_cab2")
sit("dad", "L46", on=False)
put("dad", "L46", [LX + 4.7, LY + 9.0], 10, expr="glum", arms=[30, 0], side=[70, 0], lean=0, head=[0, 0])
shot("L46", mv([LX + 3.4, LY + 4.6, 1.65], [LX + 5.0, LY + 9.0, 1.5], 34, [LX + 3.7, LY + 5.0, 1.65], [LX + 5.0, LY + 9.0, 1.5], 34), "dad_buzzer")
beat("dad", "L47", expr="glum", arms=[0, 0], side=[0, 0], yaw=-30)
shot("L47", mv([LX + 3.2, LY + 5.0, 1.65], [LX + 4.7, LY + 9.0, 1.55], 40, [LX + 3.6, LY + 5.4, 1.65], [LX + 4.7, LY + 9.0, 1.55], 40), "dad_turns")
cue("L46-0.05", "dadfill", v=1.0, ox=0.6, oy=-2.2, oz=2.0, dur=0.0)
cue("L50", "dadfill", v=0.0, dur=0.3)
cue("L52-0.01", "dadfill", v=1.0, ox=0.5, oy=-2.0, oz=1.9, dur=0.0)
cue("L53", "dadfill", v=1.0, ox=0.0, oy=2.0, oz=3.0, dur=0.0)
cue("L56", "dadfill", v=0.0, dur=0.3)
cue("L48", "phone", v=1.0, dur=0.3)
cue("L49", "phone", v=0.0, dur=0.3)
put("dad", "L48", [LX - 6.0, LY + 6.0], 0, expr="glum", arms=[70, 0], side=[0, 0])
shot("L48", mv([LX - 5.8, LY + 2.5, 1.5], [LX - 5.8, LY + 6.0, 1.3], 34, [LX - 5.8, LY + 2.9, 1.5], [LX - 5.8, LY + 6.0, 1.3], 34), "dad_phone")
beat("dad", "L49", expr="glum", arms=[0, 0])
shot("L49", fc([LX - 6.0, LY + 6.0], 0, d=2.9, lens=38, aimz=1.45, side=-12), "dad_face")
# ----------------------------------------------------------------------------- 07 headlights, home (L50..L62)
cue("L49+1.0", "truck2", x=NX - 8.0, y=NY - 16.0, yaw=-25.0, head=1.0, dur=0.0)
cue("L50", "truck2", x=NX - 1.0, y=NY - 9.0, yaw=0.0, head=1.0, dur=2.6)
put("me", "L50", [NX - 2.6, NY + 0.7, AZ], 0, expr="scared")
only("L50", ["me"])
shot("L50", mv([NX - 1.4, NY - 6.4, AZ + 1.5], [NX - 2.6, NY + 0.7, AZ + 1.5], 40, [NX - 1.9, NY - 6.2, AZ + 1.5], [NX - 2.6, NY + 0.7, AZ + 1.5], 40), "headlights")
cue("L51", "truck2", x=NX - 1.0, y=NY - 4.5, yaw=0.0, head=1.0, dur=1.4)
only("L51", [])
WIN = [NX - 2.6, NY + 0.5, AZ + 2.0]
shot("L51", mv(WIN, [NX - 1.0, NY - 8.0, 1.0], 30, [NX - 2.6, NY + 0.6, AZ + 1.9], [NX - 1.0, NY - 6.0, 1.2], 34), "pulls_in")
cue("L52", "truck2", head=0.0, dur=0.0)
put("dad", "L52", [NX - 3.2, NY - 5.2], 0, expr="stunned", head=[0, -6])
only("L52", ["dad"])
shot("L52", mv([NX - 3.0, NY - 8.4, 1.0], [NX - 2.9, NY, 2.3], 22, [NX - 3.0, NY - 8.0, 1.0], [NX - 2.9, NY, 2.3], 22), "dad_lot")
beat("dad", "L53", expr="sheepish", yaw=170, head=[0, -20])
shot("L53", mv([NX - 2.6, NY + 0.5, AZ + 1.95], [NX - 3.2, NY - 5.2, 1.5], 68, [NX - 2.7, NY + 0.45, AZ + 1.9], [NX - 3.2, NY - 5.2, 1.5], 72), "dad_lot2")
put("me", "L54", [NX - 2.6, NY + 0.7, AZ], 0, expr="laugh")
only("L54", ["me"])
shot("L54", mv([NX - 2.2, NY - 4.4, AZ + 1.3], [NX - 2.6, NY + 0.7, AZ + 1.55], 46, push=0.08), "me_laugh")
put("dad", "L55", [NX - 3.2, NY - 5.2], 170, expr="sheepish", head=[0, -20])
only("L55", ["dad"])
shot("L55", mv([NX - 2.6, NY + 0.5, AZ + 1.95], [NX - 3.2, NY - 5.2, 1.5], 62, [NX - 2.7, NY + 0.45, AZ + 1.9], [NX - 3.2, NY - 5.2, 1.5], 66), "dad_lot3")
put("me", "L55+1.1", [NX - 2.6, NY + 0.7, AZ], 0, expr="smile")
only("L55+1.1", ["me"])
shot("L55+1.1", mv([NX - 2.2, NY - 4.4, AZ + 1.3], [NX - 2.6, NY + 0.7, AZ + 1.55], 44, push=0.08), "me_smile")
beat("me", "L56", expr="determined")
shot("L56", mv([NX - 3.0, NY - 4.6, AZ + 1.3], [NX - 2.6, NY + 0.7, AZ + 1.55], 50, push=0.1), "me_resolve")
rip("L57", NX + 0.1, NY + 3.4, AZ + 1.6, s=1.5, ax=1.0)
only("L57", [])
shot("L57", mv([NX - 0.5, NY + 5.8, AZ + 1.6], [NX + 0.2, NY + 1.2, AZ + 1.5], 30, [NX - 0.3, NY + 5.2, AZ + 1.6], [NX + 0.2, NY + 1.2, AZ + 1.5], 30), "ripple_waver")
rip_off("L58")
put("me", "L58", [NX - 2.6, NY + 0.45, AZ], 0, expr="smile", lean=14)
talk("me", "L58+0.9", "L58>", 0.9)
only("L58", ["me"])
shot("L58", mv([NX - 2.4, NY - 4.2, AZ + 1.5], [NX - 2.6, NY + 0.5, AZ + 1.5], 40, [NX - 2.5, NY - 3.8, AZ + 1.5], [NX - 2.6, NY + 0.5, AZ + 1.5], 40), "calling_down")
rip("L59", NX + 0.1, NY + 3.4, AZ + 1.6, s=1.4, ax=0.8)
only("L59", [])
shot("L59", mv([NX - 0.3, NY + 5.7, AZ + 1.6], [NX + 0.2, NY + 1.2, AZ + 1.5], 32, [NX - 0.1, NY + 5.2, AZ + 1.6], [NX + 0.2, NY + 1.2, AZ + 1.5], 32), "ripple_shift")
put("dad", "L60", [NX - 3.6, NY - 0.9, 0.6], 90, expr="warm", head=[0, 0], side=[0, 0], arms=[0, 0])
go("dad", "L60+2.2", [NX - 1.8, NY - 0.9, 2.2], expr="warm")
only("L60", ["dad"])
rip("L60", NX - 1.2, NY - 0.9, 3.6, s=1.0, yaw=90.0)
shot("L60", mv([NX + 0.8, NY - 0.9, 4.6], [NX - 3.4, NY - 0.9, 2.4], 36, [NX + 0.8, NY - 0.9, 4.6], [NX - 1.9, NY - 0.9, 3.6], 36), "dad_climbs")
put("dad", "L61", [NX + 0.6, NY + 0.4, AZ], 0, expr="warm", head=[0, 0])
rip_off("L61")
shot("L61", mv([NX + 0.6, NY - 1.35, AZ + 1.6], [NX + 0.6, NY + 0.4, AZ + 1.5], 24, [NX + 0.55, NY - 1.25, AZ + 1.6], [NX + 0.6, NY + 0.4, AZ + 1.5], 24), "dad_door2")
put("dad", "L62", [NX + 0.6, NY + 0.5, AZ], 180, expr="warm")
shot("L62", mv([NX + 0.6, NY + 4.6, AZ + 1.6], [NX + 0.6, NY + 0.5, AZ + 1.5], 32, [NX + 0.6, NY + 4.0, AZ + 1.6], [NX + 0.6, NY + 0.5, AZ + 1.5], 32), "dad_doorway")
# ----------------------------------------------------------------------------- 08 eggs, sorry, Sundays (L63..L71)
cue("L62+0.8", "eggs", v=1.0)
put("dad", "L63", [NX - 3.2, NY + 3.6, AZ], 43, expr="smile", arms=[60, 0])
shot("L63", mv([NX - 1.2, NY + 1.2, AZ + 1.55], [NX - 3.2, NY + 3.6, AZ + 1.45], 34, [NX - 1.5, NY + 1.5, AZ + 1.5], [NX - 3.2, NY + 3.6, AZ + 1.45], 34), "dad_stove")
cue("L64+0.9", "toast", v=1.0, dur=0.12)
put("dad", "L64", [NX - 3.2, NY + 4.3, AZ], 40, expr="sheepish", arms=[0, 0])
shot("L64", mv([NX - 0.8, NY + 1.8, AZ + 1.5], [NX - 3.6, NY + 4.8, AZ + 1.25], 32, [NX - 1.0, NY + 2.0, AZ + 1.5], [NX - 3.6, NY + 4.8, AZ + 1.25], 32), "toast")
CH = [NX - 0.15, NX + 0.75]
put("me", "L65", [CH[0], NY + 4.75, AZ], 0, expr="smile")
put("dad", "L65", [CH[1], NY + 4.75, AZ], 0, expr="smile")
sit("me", "L65")
sit("dad", "L65")
only("L65", ["me", "dad"])
shot("L65", mv([NX + 0.3, NY + 0.9, AZ + 1.5], [NX + 0.3, NY + 4.75, AZ + 1.3], 30, [NX + 0.3, NY + 1.3, AZ + 1.5], [NX + 0.3, NY + 4.75, AZ + 1.3], 30), "table2")
beat("me", "L66", expr="sheepish")
beat("dad", "L66", expr="sheepish")
talk("me", "L66+0.25", "L66>", 0.9)
talk("dad", "L66+0.25", "L66>", 0.9)
for _w in ("me", "dad"):   # both open wide on "SORRY", together
    acting[_w].append({"from": "L66+0.29", "to": "L66+0.7", "mouth": [1.0, 1.0]})
    beat(_w, "L66+0.27", expr="stunned")
    beat(_w, "L66+0.72", expr="sheepish")
shot("L66", mv([NX + 0.3, NY + 0.7, AZ + 1.5], [NX + 0.3, NY + 4.75, AZ + 1.3], 22, [NX + 0.3, NY + 1.2, AZ + 1.5], [NX + 0.3, NY + 4.75, AZ + 1.3], 22), "sorry")
beat("me", "L67", expr="laugh")
beat("dad", "L67", expr="laugh")
shot("L67", mv([NX + 0.3, NY + 1.0, AZ + 1.5], [NX + 0.3, NY + 4.75, AZ + 1.3], 22, [NX + 0.3, NY + 1.5, AZ + 1.5], [NX + 0.3, NY + 4.75, AZ + 1.3], 22), "laugh2")
cue("L68", "plates", v=1.0)
cue("L68", "eggs", v=0.0)
beat("me", "L68", expr="smile")
beat("dad", "L68", expr="smile")
shot("L68", mv([NX + 0.3, NY + 0.9, AZ + 1.5], [NX + 0.3, NY + 4.75, AZ + 1.55], 28, [NX + 0.3, NY + 1.3, AZ + 1.5], [NX + 0.3, NY + 4.75, AZ + 1.5], 28), "cold_eggs")
sit("me", "L69", on=False)
sit("dad", "L69", on=False)
put("dad", "L69", [DX - 2.2, DY - 0.9, 1.8], 0, expr="smile", arms=[0, 150])
beat("dad", "L69+0.7", arms=[0, 120])
beat("dad", "L69+1.1", arms=[0, 155])
only("L69", ["dad"])
shot("L69", mv([DX - 2.4, DY - 6.2, 2.2], [DX - 2.2, DY - 0.9, 3.0], 36, [DX - 2.3, DY - 5.6, 2.3], [DX - 2.2, DY - 0.9, 3.0], 36), "wave", hand=0.0)
put("me", "L70", [DX + 0.45, DY - 0.7, AZ], 0, expr="smile")
talk("me", "L70+0.2", "L70>", 0.6)
only("L70", ["me"])
shot("L70", mv([DX + 0.5, DY - 5.4, AZ + 1.0], [DX + 0.45, DY - 0.7, AZ + 1.5], 38, [DX + 0.5, DY - 4.9, AZ + 1.1], [DX + 0.45, DY - 0.7, AZ + 1.5], 38), "me_door")
put("dad", "L71", [CH[1], NY + 4.75, AZ], 0, expr="warm")
sit("dad", "L71")
only("L71", ["dad"])
rip("L71", NX + 0.5, NY + 3.3, AZ + 1.7, s=1.0)
shot("L71", mv([NX + 0.5, NY + 1.2, AZ + 1.45], [NX + 0.5, NY + 4.75, AZ + 1.35], 34, [NX + 0.5, NY + 1.6, AZ + 1.45], [NX + 0.5, NY + 4.75, AZ + 1.35], 34), "dad_chair")
only("L71>", [])
cue("L71>", "days", n=731.0)
rip("L71>", HALLX + 0.2, HALLY + 2.4, 1.4, s=1.35)
shot("L71>", mv([HALLX + 0.1, HALLY + 1.0, 1.55], [HALLX + 0.5, HALLY + 4.4, 1.5], 30, [HALLX + 0.25, HALLY + 1.9, 1.55], [HALLX + 0.5, HALLY + 4.4, 1.5], 30), "loop_door")

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
    names[nm] = s["id"]

sfx = [
    {"at": "L01>-0.3", "kind": "thud", "db": -9},
    {"at": "L23+0.1", "kind": "creak", "db": -15, "dur": 1.2},
    {"at": "L51+0.9", "kind": "thud", "db": -19},
    {"at": "L64+0.9", "kind": "click", "db": -17},
    {"at": "L10", "kind": "door", "db": -11},
    {"at": "L22+1.3", "kind": "latch", "db": -15},
    {"at": "L33+0.05", "kind": "creak", "db": -17, "dur": 1.0},
    {"at": "L61", "kind": "knock", "db": -15},
    {"at": "L46+0.3", "kind": "knock", "db": -16},
    {"at": "L42", "kind": "creak", "db": -19, "dur": 0.8},
    {"at": "L69+0.2", "kind": "thud", "db": -16},
    {"at": "L16", "kind": "click", "db": -18},
    {"at": "L54", "kind": "thud", "db": -19},
]
music = {
    "root": 52, "mode": "minor", "bpm": 80, "seed": 120,
    "sections": [
        {"at": 0, "voices": ["piano", "pad"], "energy": 0.32},
        {"at": "L08", "voices": ["piano"], "energy": 0.26},
        {"at": "L15", "voices": ["pulse", "pad"], "energy": 0.32},
        {"at": "L22", "voices": ["drone", "pulse"], "energy": 0.46},
        {"at": "L31", "voices": ["drone", "choir"], "energy": 0.42},
        {"at": "L39", "voices": ["piano", "pad"], "energy": 0.3, "mode": "dorian"},
        {"at": "L56", "voices": ["piano", "pad", "pulse"], "energy": 0.46},
        {"at": "L58+1.2", "voices": ["piano", "pad"], "energy": 0.5, "mode": "major"},
        {"at": "L63", "voices": ["piano", "pad"], "energy": 0.42, "mode": "major"},
    ],
}
sound = {
    "floor": "wood", "steps_db": -26,
    "ambience": [{"kind": "room", "from": 0, "to": "L15", "lufs": -42},
                 {"kind": "traffic", "from": "L15", "to": "L31", "lufs": -42},
                 {"kind": "hum", "from": "L36", "to": "L39", "lufs": -38},
                 {"kind": "hum", "from": "L60", "to": "L61", "lufs": -38},
                 {"kind": "rain", "from": "L62+0.8", "to": "L64", "lufs": -46},
                 {"kind": "room", "from": "L65", "to": "end", "lufs": -42}],
    "sfx": sfx,
    "music_drops": [{"from": "P01", "to": "P01>"}],
    "rev": REV,
}
remap_all(sfx)
remap_all(music["sections"])
remap_all(sound["music_drops"])
remap_all(sound["ambience"])
polish = {"reveal": [remap("L39")], "twist": remap("L39"), "sway": [names["shape1"], names["shape2"], names["eleven"]],
          "hold": [names["photo"], names["reveal"]]}
story = {
    "slug": "ep120-last-words",
    "title": "Dad's Place Still Says My Last WORDS \U0001f50a",
    "made_for_kids": False,
    "premise": ("In a town where the last thing said in a house keeps playing out loud until somebody says something new, "
                "I've spent two years sure my dad's place over his auto shop was yelling my \"don't call me again\" at "
                "him, while a pickup parks outside my building every night with somebody in it."),
    "twist": ("The voice in Dad's place is his own, \"I'm going to go get him\": he walked out after me that night and "
              "never went back in, and the truck outside my building is him, every night, trying to knock. I call him "
              "home in my own words and we say sorry at the same time."),
    "world": ("A street of painted clapboard houses, an apartment block and its lot under one sodium streetlight, and a "
              "red-brick auto shop with an outside stair up to one room and a kitchen nook."),
    "voice": {"voice": "am_adam", "tempo": 1.03, "rate": 1.45},
    "key_color": "#49c06b",
    "gap": 0.18,
    "tail": 0.75,
    "fade_in": False,
    "fade_out": False,
    "rev": REV,
    "look": {"style": "closer", "fog": "#8fa6c8", "fog_density": 0.0, "fog_start": 30.0, "sky": "#8fd3ff",
             "sky_strength": 1.0, "exposure": 0.2, "flash_safe": True, "polish": polish},
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
    "set_moves": [],
    "clip_ok": ["ripple"],
    "framing_ok": [],
    # frames_ok reasons: S10 = an idle blink on the neighbor's big face 0.13 s in (the pose is right, the lint reads the closed eyes as a pop);
    # S18 = the door slam: the door shuts on the shot's first beat (cue door v=0, 0.15 s) and is meant; S33 = the camera climbs out from behind
    # the window ledge at the cut, so the bottom corner brightens as it clears (no light fades in).
    "frames_ok": ["S10", "S18", "S33"],
    "asr_forgive": ["eleven", "sixteen"],
}
OUT.write_text(json.dumps(story, indent=1, ensure_ascii=False) + "\n")
print("wrote", OUT, f"({len(shots)} shots, {len(cues)} cues)")
print({k: v for k, v in names.items()})
