"""Writes ../story.json for ep127 "thousand tellings" (script.md, batch 13). Run: python stories/ep127-thousand-tellings/generator/make_story.py

The words are in lines.json. Places are in ../layout.py (shared with set.py). A character facing -y has yaw 0, +y is 180.
Shots and acting use the script's original chunk numbers ("L10.2"); the captions are split to three words and the
references are remapped.
"""
import json
import math
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE.parent))
sys.path.insert(0, str(ROOT))
import layout as G  # noqa: E402
from blocky import timeline  # noqa: E402

OUT = HERE.parent / "story.json"
REV = 3
orig_lines = json.loads((HERE / "lines.json").read_text())
lines, CHUNKMAP = timeline.split_lines(orig_lines)


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


def mv(p0, t0, l0, p1=None, t1=None, l1=None):
    if p1 is None:
        return [[0, list(p0), list(t0), l0]]
    return [[0, list(p0), list(t0), l0], [1, list(p1), list(t1 if t1 is not None else t0), l1 or l0]]


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
    # me: 27, short black hair, light skin, a mustard rain jacket, jeans
    "me": person("#f1c9a0", "#e0a32a", "#3d5a8a", "#f4f4f2", hair="cap", hair_c="#16120f", extras=["coat"],
                 brow_w=1.9, zip_c="#7a5a14"),
    # Grandpa Otto: white beard (set.py), green vest over plaid, a canvas bucket hat
    "grandpa": person("#e8bd98", "#7a9a52", "#6b5a48", "#4a3626", hair="cap", hair_c="#f2f2ea", pattern="plaid",
                      pattern_c="#33502a", hat="bucket", hat_c="#c9b98a", extras=["apron"], extra_c="#5f7f3f",
                      brow_w=1.6, width=1.04),
    "ortiz": person("#c98f65", "#ff8fb0", "#6a4a8a", "#3a2a1a", hair="long", hair_c="#4a2f1c", pattern="knit",
                    pattern_c="#e86a90", eyes="lashes", brow_w=1.9),
    "husband": person("#d3a07a", "#3a8aaa", "#4a4036", "#2a2a2a", hair="cap", hair_c="#2a1d15", pattern="plaid",
                      pattern_c="#1f5a74", extras=["glasses"], extra_c="#3a3a3e", width=1.04),
    "pike": person("#f0c8a0", "#8a5a3a", "#4a5a3a", "#3a2a1a", hair="cap", hair_c="#b4b4ba", pattern="knit",
                   pattern_c="#6a4228", hat="ballcap", hat_c="#c0543a", width=1.04),
    "pikewife": person("#e6b48c", "#8a5ab0", "#3a3a4a", "#3a2a1a", hair="bun", hair_c="#3a2a1a", eyes="lashes",
                       brow_w=1.9),
}
acting = {n: [{"at": 0, "hidden": True, "pos": [0, 0]}] for n in cast}
last = {n: [0, 0] for n in cast}
ST = {}
visible = set()
cues = []
SH = []


def put(who, at, pos, yaw=0, hz=1.57, **kw):
    p = list(pos)
    acting[who].append({"at": at, "pos": list(last[who])})
    k = {"at": at, "pos": p, "blend": 0.0, "hidden": False, "yaw": yaw, "blink": False}
    k.update(kw)
    acting[who].append(k)
    last[who] = p
    visible.add(who)
    ST[who] = {"x": p[0], "y": p[1], "hz": hz + (p[2] if len(p) > 2 else 0.0), "side": -1 if yaw == 0 else 1}


def go(who, at, pos, **kw):
    p = list(pos)
    acting[who].append({"at": at, "pos": p, **kw})
    last[who] = p
    ST[who]["x"], ST[who]["y"] = p[0], p[1]


def beat(who, at, **kw):
    acting[who].append({"at": at, "pos": list(last[who]), **kw})


def only(at, names):
    for w in list(visible):
        if w not in names:
            acting[w].append({"at": at, "hidden": True})
            visible.discard(w)


def cue(at, name, **kw):
    cues.append({"at": at, "name": name, **kw})


def seat(who, at, z=0.47, dur=0.0):
    cue(at, "sit", who=who, on=True, z=z, dur=dur)
    ST[who]["hz"] = 1.57 - (0.68 - z) + (last[who][2] if len(last[who]) > 2 else 0.0)


def stand(who, at, dur=0.0):
    cue(at, "sit", who=who, on=False, z=0.47, dur=dur)
    ST[who]["hz"] = 1.57


def talk(who, a, b, lo=0.05, hi=0.5):
    acting[who].append({"from": a, "to": b, "flap": True, "mouth": [lo, hi]})


def look(at, lid):
    cue(at, "look", id=lid, dur=0)


def count(at, s, dur=0.0):
    cue(at, "count", s=s, dur=dur)


def shot(at, camera, name, step=2, **extra):
    SH.append((at, camera, step, name, extra))


def face(who, d=3.7, lens=40, dx=0.0, dzc=0.0, tz=0.28, push=0.07, tx=0.0, side=None, dlens=0, dy=0.0):
    s = ST[who]
    if who == "grandpa":   # eye height: a camera above him sees only the hat brim (framing pre-check)
        tz, dzc = min(tz, 0.2), min(dzc, 0.1)
    if who == "grandpa" and lens >= 50:
        tz, dzc = min(tz, 0.02), min(dzc, 0.3)
    sd = side or s["side"]
    x, y, hz = s["x"], s["y"] + dy, s["hz"]
    tgt = [x + tx, y, hz - tz]
    return mv([x + dx, y + sd * d, hz + dzc], tgt, lens,
              [x + dx * 0.75, y + sd * d * (1 - push), hz + dzc * 0.85], tgt, lens + dlens)


def slate_cam(dx=0.0, d0=3.1, d1=2.7, lens=30, dz=0.0):
    """The whole slate (frame and digits) with margin: 1.2 to 1.4 m of wall across the frame."""
    cx = sx + dx
    return mv([cx, sy - d0, sz + dz], [sx, 1.7, sz], lens, [cx, sy - d1, sz + dz], [sx, 1.7, sz], lens)


# --- standard setups
GX, GY = G.GCH
MX, MY = G.MCH
GP = (GX, GY - 0.22)      # where Grandpa sits (a little forward, so his hat clears the chair back)
MP = (MX, MY + 0.22)
BX, BY = G.BEHIND
NIGHT_TELL = dict(d=3.9, lens=40, dx=-0.5, dzc=0.45)


def grandpa_chair(at, expr="shut"):
    put("grandpa", at, list(GP), 0, expr=expr)
    seat("grandpa", at)


def grandpa_counter(at, expr="smile", **kw):
    stand("grandpa", at)
    put("grandpa", at, [BX, BY], 0, expr=expr, **kw)


def me_outside(at, expr, x=G.DOOR_X, y=-7.2, **kw):
    put("me", at, [x, y], 180, expr=expr, **kw)


def me_chair(at, expr):
    put("me", at, list(MP), 180, expr=expr)
    seat("me", at)


def me_inside(at, expr, **kw):
    put("me", at, [1.5, -3.4], 180, expr=expr, **kw)


def door_cam(who="me", d=3.0, lens=36, dx=0.0, push=0.12, dzc=0.0, tz=0.28):
    return face(who, d=d, lens=lens, dx=dx, dzc=dzc, push=push, tz=tz)


# ============================================================================================ 01 the rule (L01 to L08)
look(0, "night")
count(0, "997")
cue(0, "rods", at_door=False, box=False)
cue(0, "car", mode="fix", x=G.LOT[0], y=G.LOT[1], yaw=0.0)
cue(0, "bag", on=False)
cue(0, "door", a=0.0)
cue(0, "hook", u=0.0)
grandpa_chair(0)
talk("grandpa", 0, "L01>")
shot(0, face("grandpa", **NIGHT_TELL), "open1")
shot("L01.1", face("grandpa", d=3.9, lens=48, dx=0.35, dzc=0.45), "open2")
# L02: the number on the slate, then his face again
sx, sy, sz = G.SLATE
shot("L02", slate_cam(-0.1, 3.3, 2.9, 30), "slate1")
shot("L02.1", face("grandpa", d=3.9, lens=52, dx=0.8, dzc=0.4, tz=0.25), "open3")
shot("L02.2", slate_cam(0.05, 2.9, 2.6, 28), "slate2")
# L03 to L07: the montage, one face each (day)
look("L03", "day")
only("L03", ["ortiz"])
px, py = G.PORCH
put("ortiz", "L03", [px - 0.2, py + 0.9], 0, expr="smile")
seat("ortiz", "L03", z=0.5)
talk("ortiz", "L03", "L03>")
shot("L03", face("ortiz", d=3.4, lens=36, dzc=0.15, tz=0.3), "ortiz1")
shot("L03.2", face("ortiz", d=3.4, lens=44, dx=0.8, dzc=0.15, tz=0.3), "ortiz2")
only("L04", ["husband"])
put("husband", "L04", [px + 1.4, py + 1.0], 0, expr="delighted")
shot("L04", face("husband", d=3.6, lens=36, dx=-0.3), "husband1")
shot("L04.1", face("husband", d=3.6, lens=46, dx=0.4, push=0.2), "husband2")
yx, yy = G.YARD
only("L05", ["pike"])
put("pike", "L05", [yx, yy + 1.0], 0, expr="smile")
talk("pike", "L05", "L05>")
shot("L05", face("pike", d=3.6, lens=36, dx=-0.3), "pike1")
shot("L05.2", face("pike", d=3.6, lens=46, dx=0.5), "pike2")
only("L06", [])
stx, sty = G.STREET
shot("L06", mv([stx - 5.0, sty - 1.6, 1.6], [stx + 8.0, sty + 0.4, 3.2], 28, [stx - 3.6, sty - 1.4, 1.7], [stx + 8.0, sty + 0.4, 3.3], 28), "street1")
shot("L06.2", mv([stx + 4.0, sty - 5.6, 1.5], [stx + 0.5, sty + 3.0, 3.3], 30, [stx + 3.2, sty - 5.2, 1.6], [stx + 0.5, sty + 3.0, 3.4], 30), "street2")
only("L07", ["pikewife"])
put("pikewife", "L07", [yx - 2.2, yy + 1.0], 0, expr="neutral")
shot("L07", face("pikewife", d=3.4, lens=36, dx=0.3), "wife1")
shot("L07.2", face("pikewife", d=3.4, lens=46, dx=-0.4), "wife2")
only("L08", ["me"])
me_outside("L08", "neutral")
shot("L08", face("me", d=3.4, lens=36, dx=0.0), "door1")
shot("L08.2", face("me", d=3.4, lens=46, dx=0.5), "door2")

# ============================================================================================ 02 who I am (L09 to L14)
only("L09", ["grandpa"])
grandpa_counter("L09", "smile")
shot("L09", face("grandpa", d=3.4, lens=36, dzc=0.1), "gp_counter1")
shot("L09.2", face("grandpa", d=3.4, lens=46, dx=0.5), "gp_counter2")
only("L10", ["me"])
put("me", "L10", [BX, BY], 0, expr="smile")
shot("L10", face("me", d=3.4, lens=34, dzc=0.1, push=0.1), "me_counter")
# the car pulling away (day): the car follows me
put("me", "L10.2", [G.LOT[0] + G.CAR_DX, G.LOT[1] + G.CAR_DY], 0, expr="smile")
seat("me", "L10.2", z=0.62)
cue("L10.2", "car", mode="me", z=0.0)
go("me", "L10.3+0.6", [G.LOT[0] + G.CAR_DX, G.LOT[1] + G.CAR_DY - 22.0])
shot("L10.2", mv([7.5, 8.5, 1.5], [0.0, 0.0, 0.9], 34, [6.0, 6.8, 1.6], [0.0, 0.0, 0.9], 34), "carleave1", follow="me")
only("L11", [])
stand("me", "L11")
shot("L11", mv([MX + 1.9, MY + 2.4, 1.35], [MX - 0.1, MY, 0.31], 30, [MX + 1.7, MY + 2.2, 1.35], [MX - 0.1, MY, 0.31], 30), "chair_day")
# L12: the call
kx, ky = G.KITCHEN
shot("L12", mv([kx + 1.7, ky + 1.4, 1.7], [kx + 1.6, ky + 2.5, 0.96], 40, [kx + 1.65, ky + 1.7, 1.5], [kx + 1.6, ky + 2.5, 0.96], 40), "phone1")
shot("L12.1", mv([kx + 1.2, ky + 1.4, 1.2], [kx + 1.6, ky + 2.5, 0.97], 55, [kx + 1.3, ky + 1.8, 1.1], [kx + 1.6, ky + 2.5, 0.97], 55), "phone2")
only("L12.2", ["grandpa"])
grandpa_counter("L12.2", "neutral", arms=[55, 55])
shot("L12.2", face("grandpa", d=3.4, lens=36, dx=-0.3, dzc=0.1), "gp_call1")
shot("L12.3", face("grandpa", d=3.4, lens=46, dx=0.4, dzc=0.1), "gp_call2")
# L13: the drive
only("L13", ["me"])
rx, ry = G.ROAD
cue("L13", "car", mode="me", z=0.0)
put("me", "L13", [rx + G.CAR_DX, ry + G.CAR_DY], 0, expr="neutral")
seat("me", "L13", z=0.62)
shot("L13", face("me", d=4.4, lens=40, dx=-0.2, dzc=0.05, tz=0.2), "drive1")
shot("L13.1", face("me", d=4.4, lens=50, dx=0.8, dzc=0.1, tz=0.2), "drive2")
# L14: the dry ceiling
cx_, cy_ = G.CEIL
only("L14", [])
shot("L14", mv([cx_, cy_ - 1.2, 1.3], [cx_, cy_ + 1.5, 3.2], 26, [cx_, cy_ - 0.6, 1.3], [cx_, cy_ + 1.8, 3.2], 26), "ceiling")
only("L14.1", ["grandpa"])
stand("me", "L14.1")
stand("grandpa", "L14.1")
put("grandpa", "L14.1", [cx_, cy_ + 1.4], 0, expr="smile")
shot("L14.1", mv([cx_ - 0.2, cy_ - 2.0, 1.4], [cx_, cy_ + 1.4, 1.2], 32, [cx_ - 0.1, cy_ - 1.5, 1.4], [cx_, cy_ + 1.4, 1.25], 32), "gp_ceiling")

# ============================================================================================ 03 the window (L15 to L24)
look("L15", "night")
only("L15", ["me"])
cue("L15", "car", mode="fix", x=G.LOT[0], y=G.LOT[1], yaw=0.0)
stand("me", "L15")
put("me", "L15", [G.DOOR_X, -13.0], 180, expr="neutral")
go("me", "L15.2", [G.DOOR_X, -9.4])
shot("L15", mv([G.DOOR_X, -6.6, 1.5], [G.DOOR_X, -13.0, 1.4], 38, [G.DOOR_X, -6.6, 1.5], [G.DOOR_X, -11.0, 1.4], 38), "walkup1")
beat("me", "L15.2+0.2", expr="neutral")
shot("L15.2", mv([G.DOOR_X + 0.4, -6.6, 1.6], [G.DOOR_X, -9.4, 1.35], 34, [G.DOOR_X + 0.2, -6.6, 1.6], [G.DOOR_X, -9.4, 1.35], 34), "walkup2")
# L16: through the window
only("L16", ["grandpa"])
grandpa_chair("L16", "shut")
talk("grandpa", "L16.1", "L18>")
wx = G.WIN_X
shot("L16", mv([wx + 0.05, -7.8, 1.6], [wx, GY, 0.96], 40, [wx + 0.05, -7.3, 1.6], [wx, GY, 0.96], 40), "window1", winframe=True)
shot("L16.1", mv([wx + 0.55, -7.8, 1.6], [wx, GY, 0.96], 42, [wx + 0.4, -7.4, 1.6], [wx, GY, 0.96], 42), "window2", winframe=True)
shot("L17", mv([wx - 0.45, -7.6, 1.6], [wx, GY, 0.98], 44, [wx - 0.3, -7.1, 1.6], [wx, GY, 0.98], 44), "tell1", winframe=True)
# L18, L19: the empty chair
shot("L18", mv([MX + 1.5, GY + 0.5, 2.3], [MX, MY, 0.6], 28, [MX + 1.4, GY + 0.5, 2.25], [MX, MY, 0.6], 28), "emptychair1")
shot("L18.1", mv([MX - 1.5, MY + 1.8, 1.6], [MX, MY, 0.62], 25, [MX - 1.3, MY + 1.6, 1.55], [MX, MY, 0.62], 25), "emptychair2")
shot("L19", mv([MX - 1.5, MY + 1.5, 1.15], [MX - 0.7, MY - 0.05, 0.62], 30, [MX - 1.3, MY + 1.3, 1.1], [MX - 0.7, MY - 0.05, 0.62], 30), "chairarm")
shot("L20", face("grandpa", d=3.9, lens=56, dx=-0.3, dzc=0.45, tz=0.25), "eyes_shut")
shot("L21", slate_cam(-0.3, 3.3, 2.9, 30), "slate_night1")
shot("L21.2", slate_cam(0.0, 2.8, 2.6, 28), "slate_night2")
# L22: me at the window
only("L22", ["me"])
me_outside("L22", "worried", x=wx, y=-7.1)
shot("L22", mv([wx + 0.2, -4.9, 1.55], [wx, -7.1, 1.3], 30, [wx + 0.1, -5.0, 1.55], [wx, -7.1, 1.3], 30), "mewin")
# L23: the lock and sitting down
only("L23", [])
cue("L23.1", "hook", u=1.0, dur=0.45)
shot("L23", mv([G.DOOR_X - 0.7, -4.0, 1.62], [G.DOOR_X - 0.75, -5.75, 1.6], 42, [G.DOOR_X - 0.7, -4.2, 1.62], [G.DOOR_X - 0.75, -5.75, 1.6], 42), "hook")
only("L23.2", ["grandpa"])
stand("grandpa", "L23.2")
put("grandpa", "L23.2", list(GP), 0, expr="neutral")
seat("grandpa", "L23.2+0.1", dur=0.5)
shot("L23.2", face("grandpa", d=3.9, lens=40, dx=0.4, dzc=0.45), "sitdown")
# L24: the shop from outside
only("L24", [])
shot("L24", mv([0.2, -15.0, 1.7], [wx + 0.2, -6.0, 1.45], 30, [-0.1, -13.0, 1.75], [wx + 0.2, -6.0, 1.45], 30), "outside_night")

# ============================================================================================ 04 the telling (L25 to L36)
only("L25", ["me"])
me_outside("L25", "worried")
beat("me", "L25.1", head=[8, 4])
shot("L25", door_cam(d=3.2, lens=34, dx=0.0), "listen1")
shot("L25.2", door_cam(d=3.2, lens=44, dx=0.4), "listen2")
only("L26", ["grandpa"])
grandpa_chair("L26", "shut")
talk("grandpa", "L26", "L29>")
shot("L26", face("grandpa", d=3.9, lens=40, dx=0.5, dzc=0.45), "tell2")
shot("L26.1", face("grandpa", d=3.9, lens=48, dx=-0.5, dzc=0.45), "tell3")
only("L27", ["me"])
me_outside("L27", "scared")
shot("L27", door_cam(d=3.2, lens=36, dx=-0.3), "scared1")
shot("L28", door_cam(d=2.8, lens=44, dx=0.3), "scared2")
cue("L28.2", "car", mode="fix", x=G.LOT[0], y=G.LOT[1], yaw=0.0)
only("L28.2", [])
shot("L28.2", mv([G.LOT[0] + 4.0, G.LOT[1] + 3.4, 1.4], [G.LOT[0], G.LOT[1], 0.9], 36, [G.LOT[0] + 3.4, G.LOT[1] + 3.0, 1.5], [G.LOT[0], G.LOT[1], 0.9], 36), "mycar")
only("L29", ["grandpa"])
grandpa_chair("L29", "shut")
talk("grandpa", "L29", "L30.1>")
beat("grandpa", "L29.2", expr="soft")
shot("L29", face("grandpa", d=3.9, lens=44, dx=-0.4, dzc=0.45), "smile1")
shot("L29.2", face("grandpa", d=3.9, lens=56, dx=0.3, dzc=0.45, tz=0.25), "smile2")
beat("grandpa", "L30.2", expr="shut")
shot("L30", face("grandpa", d=3.9, lens=40, dx=0.5, dzc=0.45), "mid1")
shot("L30.2", face("grandpa", d=3.9, lens=52, dx=-0.3, dzc=0.45, tz=0.25), "stopped")
shot("L31", face("grandpa", d=3.9, lens=58, dx=0.4, dzc=0.45, tz=0.25), "waiting")
shot("L32", face("grandpa", d=3.9, lens=44, dx=-0.6, dzc=0.45), "never1")
only("L32.2", ["me"])
me_outside("L32.2", "worried", x=wx, y=-7.1)
shot("L32.2", mv([wx + 0.2, -4.9, 1.55], [wx, -7.1, 1.3], 30, [wx + 0.1, -5.0, 1.55], [wx, -7.1, 1.3], 30), "uneasy_win")
count("L33.1", "998", dur=0.6)
cue("L33.1", "chalkfx")
shot("L33", slate_cam(-0.1, 3.2, 2.8, 30), "chalk998")
shot("L33.1", slate_cam(0.1, 2.9, 2.6, 28), "chalk998b")
only("L34", ["me"])
me_outside("L34", "scared", x=wx, y=-7.1)
shot("L34", mv([wx - 0.2, -4.9, 1.55], [wx, -7.1, 1.3], 30, [wx - 0.1, -5.0, 1.55], [wx, -7.1, 1.3], 30), "scared_win")
me_outside("L35", "scared")
shot("L35", door_cam(d=2.7, lens=40, dx=-0.3), "scared3")
me_outside("L36", "scared", x=wx, y=-7.1)
shot("L36", mv([wx + 0.3, -4.8, 1.6], [wx, -7.1, 1.3], 36, [wx + 0.2, -5.0, 1.6], [wx, -7.1, 1.3], 36), "lamp_on_me")
only("P01", [])
shot("P01", mv([0.0, -9.0, 1.3], [-6.0, -60.0, 0.8], 34, [0.0, -8.6, 1.4], [-6.0, -60.0, 1.0], 34), "river_drop")

# ============================================================================================ 05 the turn (L37 to L46)
look("L37", "day")
only("L37", ["grandpa"])
grandpa_counter("L37", "neutral")
shot("L37", face("grandpa", d=3.4, lens=36, dx=-0.3, dzc=0.1), "morning1")
shot("L37.2", face("grandpa", d=3.4, lens=46, dx=0.4, dzc=0.1), "morning2")
beat("grandpa", "L38", expr="worried", head=[34, -20], look=[0.4, 0.9])
shot("L38", face("grandpa", d=3.4, lens=40, dx=0.3, dzc=0.1, tz=0.3), "eyes_down1")
shot("L38.1+0.35", face("grandpa", d=3.4, lens=50, dx=-0.4, dzc=0.1, tz=0.3), "eyes_down2")
look("L39", "night")
count("L39", "999", dur=0.3)
only("L39", [])
shot("L39", slate_cam(-0.1, 3.2, 2.8, 30), "chalk999")
only("L39.1", ["grandpa"])
grandpa_chair("L39.1", "shut")
talk("grandpa", "L39.1", "L40>")
shot("L39.1+0.35", face("grandpa", d=3.9, lens=44, dx=0.4, dzc=0.45), "tell4")
shot("L40", face("grandpa", d=3.9, lens=40, dx=-0.5, dzc=0.45), "tell5")
beat("grandpa", "L40.1", expr="soft")
shot("L40.1", face("grandpa", d=3.9, lens=52, dx=0.3, dzc=0.45, tz=0.25), "tell6")
beat("grandpa", "L41", expr="shut")
shot("L41", face("grandpa", d=3.9, lens=46, dx=-0.4, dzc=0.45), "stopped2")
shot("L41.1", face("grandpa", d=3.9, lens=58, dx=0.3, dzc=0.45, tz=0.25), "stopped3")
only("L42", ["me"])
me_outside("L42", "angry")
shot("L42", door_cam(d=3.2, lens=36, dx=-0.3), "angry1")
shot("L42.2", door_cam(d=2.8, lens=46, dx=0.3), "angry2")
# L43: the car is packed
only("L43", [])
cue("L43", "car", mode="fix", x=G.LOT[0], y=G.LOT[1], yaw=0.0)
cue("L43", "bag", on=True)
shot("L43", mv([G.LOT[0] + 3.6, G.LOT[1] + 2.4, 1.5], [G.LOT[0], G.LOT[1] + 1.2, 0.9], 38, [G.LOT[0] + 3.0, G.LOT[1] + 2.0, 1.5], [G.LOT[0], G.LOT[1] + 1.2, 0.9], 38), "packed")
# L44, L45: the bridge
bx_, by_ = G.BRIDGE
only("L44", ["me"])
cue("L44", "car", mode="me", z=0.12)
cue("L44", "bag", on=False)
put("me", "L44", [bx_ + G.CAR_DX, by_ + G.CAR_DY, 0.12], 0, expr="worried")
seat("me", "L44", z=0.62)
shot("L44", face("me", d=4.4, lens=40, dx=-0.2, dzc=0.05, tz=0.2), "bridge1")
shot("L44.1", face("me", d=4.4, lens=50, dx=0.8, dzc=0.1, tz=0.2), "bridge2")
beat("me", "L45", expr="warm", head=[0, 4])
shot("L45", face("me", d=4.2, lens=44, dx=0.0, dzc=0.05, tz=0.2, push=0.2), "bridge3")
only("L45.1", ["grandpa"])
stand("me", "L45.1")
grandpa_chair("L45.1", "worried")
beat("grandpa", "L45.1+0.1", head=[0, -18])
shot("L45.1", face("grandpa", d=3.9, lens=48, dx=0.3, dzc=0.45), "hisface")
only("L45.2", ["me"])
cue("L45.2", "car", mode="me", z=0.12)
put("me", "L45.2", [bx_ + G.CAR_DX, by_ + G.CAR_DY, 0.12], 0, expr="warm")
seat("me", "L45.2", z=0.62)
shot("L45.2", face("me", d=4.0, lens=48, dx=-0.5, dzc=0.05, tz=0.2), "bridge4")
# L46: I go in
look("L46", "night")
cue("L47", "door", a=0.0)
only("L46", ["me"])
stand("me", "L46")
cue("L46", "car", mode="fix", x=G.LOT[0], y=G.LOT[1], yaw=0.0)
put("me", "L46", [G.DOOR_X, -7.4], 180, expr="neutral")
cue("L46.1", "door", a=-75.0, dur=0.7)
go("me", "L46.1", [G.DOOR_X, -7.4])
go("me", "L46.2", [G.DOOR_X, -4.4])
acting["me"][-2]["sfx"] = "door"
shot("L46", door_cam(d=3.2, lens=36, dx=0.0, push=0.05, tz=0.3), "enter1")
shot("L46.1", mv([G.DOOR_X + 0.3, -1.4, 1.55], [G.DOOR_X, -5.2, 1.4], 38, [G.DOOR_X + 0.3, -1.4, 1.55], [G.DOOR_X, -4.6, 1.4], 38), "enter2")

# ============================================================================================ 06 the reveal (L47 to L54)
only("L47", ["grandpa"])
grandpa_chair("L47", "neutral")
shot("L47", face("grandpa", d=3.9, lens=40, dx=-0.5, dzc=0.45), "reveal_open1")
shot("L47.1", face("grandpa", d=3.9, lens=50, dx=0.4, dzc=0.45), "reveal_open2")
beat("grandpa", "L48", expr="warm")
shot("L48", face("grandpa", d=3.9, lens=46, dx=-0.3, dzc=0.45, tz=0.25), "warm1")
beat("grandpa", "L49", expr="warm", head=[0, 0])
beat("grandpa", "L49+0.35", head=[0, 16])
beat("grandpa", "L49+0.85", head=[0, 0])
beat("grandpa", "L49.1+0.1", head=[0, 14])
beat("grandpa", "L49.1+0.6", head=[0, 0])
cue("L49", "wall", off=True)
cue("L49", "slatex", x=0.15, z=-0.25)
shot("L49", mv([0.0, -12.5, 4.6], [-0.4, -1.0, 0.41], 74, [-0.1, -12.3, 4.55], [-0.4, -1.0, 0.41], 74), "twist", fill_at=[-0.6, -3.0, 0.9])
cue("L49.2", "wall", off=False)
cue("L49.2", "slatex", x=G.SLATE[0], z=0.0)
shot("L49.2", mv([MX - 1.8, MY - 1.5, 2.3], [MX, MY, 0.6], 26, [MX - 1.6, MY - 1.4, 2.25], [MX, MY, 0.6], 26), "mine")
beat("grandpa", "L50", expr="warm", head=[0, 0])
shot("L50", face("grandpa", d=3.9, lens=42, dx=0.5, dzc=0.45), "tellers1")
shot("L50.2", face("grandpa", d=3.9, lens=54, dx=-0.3, dzc=0.45, tz=0.25), "tellers2")
only("L51", ["me"])
me_inside("L51", "wide")
shot("L51", mv([1.55, -0.1, 1.75], [1.5, -3.4, 1.25], 38, [1.5, -0.3, 1.75], [1.5, -3.4, 1.25], 38), "stunned1")
only("L52", ["grandpa"])
beat("grandpa", "L52", expr="smile")
put("grandpa", "L52", list(GP), 0, expr="smile")
seat("grandpa", "L52")
shot("L52", face("grandpa", d=4.2, lens=42, dx=-0.3, dzc=0.5), "saving1")
shot("L52.1", face("grandpa", d=4.2, lens=54, dx=0.4, dzc=0.5, tz=0.25), "saving2")
only("L53", ["me"])
me_inside("L53", "sad-smile")
shot("L53", mv([1.55, -0.1, 1.75], [1.5, -3.4, 1.25], 46, [1.5, -0.3, 1.75], [1.5, -3.4, 1.25], 46), "stunned2")
shot("L53.1", mv([1.7, 0.0, 1.8], [1.5, -3.4, 1.25], 56, [1.6, -0.2, 1.8], [1.5, -3.4, 1.25], 56), "stunned3")
only("L54", [])
shot("L54", slate_cam(-0.1, 3.2, 2.8, 30), "chalk999b")
only("L54.1", ["me"])
me_inside("L54.1", "neutral")
shot("L54.1", mv([1.55, -0.1, 1.75], [1.5, -3.4, 1.25], 44, [1.5, -0.3, 1.75], [1.5, -3.4, 1.25], 44), "resolve")

# ============================================================================================ 07 my ending (L55 to L63)
only("L55", ["me"])
put("me", "L55", list(MP), 180, expr="warm")
cue("L55", "sit", who="me", on=True, z=0.47, dur=0.6)
ST["me"]["hz"] = 1.57 - (0.68 - 0.47)
talk("me", "L56", "L56>")
shot("L55", face("me", d=5.0, lens=34, dx=-0.6, dzc=0.5, tz=0.3), "sat1")
beat("me", "L56", expr="neutral")
shot("L56", face("me", d=4.1, lens=46, dx=0.5, dzc=0.5, tz=0.3), "told1")
shot("L56.1", face("me", d=4.5, lens=36, dx=-0.7, dzc=0.6, tz=0.35), "told2")
beat("me", "L57", expr="smile")
shot("L57", face("me", d=4.1, lens=42, dx=0.6, dzc=0.5, tz=0.3), "told3")
shot("L57.1", face("me", d=4.1, lens=50, dx=-0.6, dzc=0.5, tz=0.3), "told4")
shot("L57.2", face("me", d=4.4, lens=34, dx=0.7, dzc=0.55, tz=0.32), "told5")
# L58: Grandpa listening, then back to me for "the end"
only("L58", ["grandpa"])
put("grandpa", "L58", list(GP), 0, expr="warm")
seat("grandpa", "L58")
shot("L58", face("grandpa", d=3.9, lens=46, dx=-0.4, dzc=0.45, tz=0.25), "gp_listens")
only("L58.1", ["me"])
put("me", "L58.1", list(MP), 180, expr="warm", head=[0, 8])
seat("me", "L58.1")
shot("L58.1", face("me", d=4.1, lens=52, dx=-0.3, dzc=0.5, tz=0.27, push=0.18, tx=-0.1), "breath")
beat("me", "L59", expr="smile", head=[0, 0])
shot("L59", face("me", d=4.1, lens=44, dx=0.6, dzc=0.5, tz=0.3, push=0.2), "end1")
shot("L59.1", face("me", d=4.6, lens=34, dx=-0.5, dzc=0.55, tz=0.3), "end2")
beat("me", "L60", expr="warm")
shot("L60", face("me", d=4.1, lens=46, dx=0.4, dzc=0.5, tz=0.3, push=0.2), "end3")
shot("L60.2", face("me", d=4.1, lens=56, dx=-0.3, dzc=0.5, tz=0.27), "end4")
only("L61", ["grandpa"])
put("grandpa", "L61", list(GP), 0, expr="shut")
seat("grandpa", "L61")
beat("grandpa", "L61.1", expr="warm")
shot("L61", face("grandpa", d=3.9, lens=44, dx=-0.4, dzc=0.45), "opens1")
shot("L61.1", face("grandpa", d=3.9, lens=56, dx=0.3, dzc=0.45, tz=0.25), "opens2")
only("L62", [])
count("L62", "1,000", dur=0.4)
shot("L62", slate_cam(-0.1, 3.3, 2.9, 28), "chalk1000")
shot("L62.1", slate_cam(0.1, 3.0, 2.7, 26), "chalk1000b")
shot("L63", mv([wx - 0.3, -4.9, 1.5], [wx - 6.0, -60.0, 0.8], 36, [wx - 0.2, -5.0, 1.55], [wx - 6.0, -60.0, 0.9], 36), "river_window")
only("L63.2", ["grandpa"])
put("grandpa", "L63.2", list(GP), 0, expr="warm")
seat("grandpa", "L63.2")
shot("L63.2", face("grandpa", d=3.9, lens=42, dx=0.5, dzc=0.45), "listening")
only("L63.3", ["me"])
put("me", "L63.3", list(MP), 180, expr="warm")
seat("me", "L63.3")
shot("L63.3", face("me", d=4.1, lens=46, dx=-0.5, dzc=0.5, tz=0.3), "listening_me")

# ============================================================================================ 08 Sundays (L64 to L70)
look("L64", "day")
only("L64", ["me"])
stand("me", "L64")
kx, ky = G.KITCHEN
put("me", "L64", [kx - 1.0, ky + 2.4], 0, expr="worried")
beat("me", "L64", arms=[12, 12])
cue("L64", "halfon", on=True)
cue("L65", "halfon", on=False)
shot("L64", mv([kx - 0.65, ky - 0.4, 1.3], [kx - 0.65, ky + 2.4, 1.15], 27, [kx - 0.65, ky - 0.1, 1.3], [kx - 0.65, ky + 2.4, 1.15], 27), "doorway")
shot("L64+0.35", mv([kx + 0.75, ky + 1.4, 2.0], [kx + 0.55, ky + 2.55, 0.99], 34, [kx + 0.7, ky + 1.6, 1.85], [kx + 0.55, ky + 2.55, 0.99], 34), "keys")
shot("L64.1+0.2", mv([kx - 1.0, ky - 0.2, 1.3], [kx - 1.0, ky + 2.4, 1.2], 34, [kx - 1.0, ky + 0.1, 1.3], [kx - 1.0, ky + 2.4, 1.2], 34), "doorway2")
cue("L65", "car", mode="me", z=0.0)
put("me", "L65", [rx + G.CAR_DX, ry + G.CAR_DY], 0, expr="wide")
seat("me", "L65", z=0.62)
shot("L65", face("me", d=4.4, lens=40, dx=-0.3, dzc=0.05, tz=0.2), "auto1")
beat("me", "L65.2", expr="laugh")
shot("L65.2", face("me", d=4.2, lens=52, dx=0.5, dzc=0.1, tz=0.2), "auto3")
only("L66", ["grandpa"])
stand("me", "L66")
cue("L66", "car", mode="fix", x=G.LOT[0], y=G.LOT[1], yaw=0.0)
cue("L66", "rods", at_door=True, box=False)
cue("L66", "door", a=-85.0)
put("grandpa", "L66", [G.DOOR_X, -6.7], 0, expr="smile", arms=[0, 0])
stand("grandpa", "L66")
shot("L66", mv([G.DOOR_X, -9.9, 1.5], [G.DOOR_X, -6.7, 1.3], 36, [G.DOOR_X, -9.4, 1.5], [G.DOOR_X, -6.7, 1.3], 36), "doorway_gp")
shot("L66.1", mv([G.DOOR_X + 0.55, -10.4, 1.5], [G.DOOR_X + 0.55, -6.7, 1.2], 22, [G.DOOR_X + 0.5, -9.9, 1.5], [G.DOOR_X + 0.5, -6.7, 1.2], 22), "rods_ready")
look("L67", "night")
cue("L67", "rods", at_door=True, box=False)
cue("L67", "door", a=0.0)
only("L67", ["grandpa"])
grandpa_chair("L67", "shut")
talk("grandpa", "L67", "L68>")
beat("grandpa", "L67", expr="soft")
shot("L67", face("grandpa", d=3.9, lens=40, dx=-0.5, dzc=0.45), "new1")
shot("L67.1", face("grandpa", d=3.9, lens=50, dx=0.5, dzc=0.45), "new2")
beat("grandpa", "L68", expr="shut")
shot("L68", face("grandpa", d=3.9, lens=44, dx=-0.3, dzc=0.45), "oldman1")
shot("L68.2", face("grandpa", d=3.9, lens=54, dx=0.4, dzc=0.45, tz=0.25), "oldman2")
count("L69", "9", dur=0.5)
only("L69", [])
shot("L69", slate_cam(-0.1, 3.2, 2.8, 30), "chalk9")
only("L70", ["grandpa"])
grandpa_chair("L70", "shut")
talk("grandpa", "L70", "L70.2")
shot("L70", face("grandpa", **NIGHT_TELL), "loop")

# ---------------------------------------------------------------------------------------------- finish
for k_ in acting.values():
    remap_all(k_)
remap_all(cues)
cues[:] = [c for c in cues if c["name"] != "chalkfx"]
# keep the cues in time order for the engine's readers
shots, names = [], {}
for i, (at, camera, step, nm, extra) in enumerate(SH):
    s = {"id": f"S{i + 1:02d}", "cam": camera, "step": step, **extra}
    if i:
        s["at"] = remap(at)
    shots.append(s)
    names[nm] = s["id"]

sfx = [
    {"at": "L01.1", "kind": "click", "db": -12},
    {"at": "L23.1+0.4", "kind": "latch", "db": -14},
    {"at": "L33.1+0.3", "kind": "click", "db": -20},
    {"at": "L39+0.3", "kind": "click", "db": -20},
    {"at": "L61", "kind": "click", "db": -22},
    {"at": "L62+0.2", "kind": "click", "db": -20},
]
for s_ in sfx:
    s_["at"] = remap(s_["at"])
music = {
    "root": 59, "mode": "minor", "bpm": 80, "seed": 127,
    "sections": [
        {"at": 0, "voices": ["piano", "pad"], "energy": 0.35, "root": 59, "mode": "minor"},
        {"at": "L16", "voices": ["piano", "pad", "pulse"], "energy": 0.45, "root": 59, "mode": "minor"},
        {"at": "L33", "voices": ["piano", "pad", "pulse", "drone"], "energy": 0.55, "root": 59, "mode": "minor"},
        {"at": "L37", "voices": ["drone"], "energy": 0.3, "root": 47, "mode": "minor"},
        {"at": "L44", "voices": ["drone", "pulse"], "energy": 0.4, "root": 47, "mode": "minor"},
        {"at": "L47", "voices": ["pad", "drone"], "energy": 0.35, "root": 59, "mode": "minor"},
        {"at": "L55", "voices": ["piano", "pad"], "energy": 0.5, "root": 59, "mode": "major"},
        {"at": "L64", "voices": ["piano", "pad", "pulse"], "energy": 0.55, "root": 59, "mode": "major"},
    ],
}
remap_all(music["sections"])
sound = {
    "floor": "wood", "steps_db": -26,
    "ambience": [
        {"kind": "water", "from": 0, "to": "end", "lufs": -44},
        {"kind": "wind", "from": "L06", "to": "L07", "lufs": -40},
        {"kind": "crickets", "from": "L15", "to": "L36>", "lufs": -44},
        {"kind": "crickets", "from": "L39", "to": "L63>", "lufs": -44},
        {"kind": "crickets", "from": "L67", "to": "end", "lufs": -44},
    ],
    "sfx": sfx,
    "music_drops": [{"from": "P01", "to": "P01>"}],
    "rev": REV,
}
remap_all(sound["ambience"])
remap_all(sound["music_drops"])
polish = {
    "reveal": [remap("L49.2")],
    "twist": remap("L49"),
    "emph": [remap(x) for x in ["L01.1", "L02.1", "L22", "L32.2", "L49.2", "L53", "L59", "L62.1"]],
    "quiet": [[remap("L63"), remap("L64")]],
    "hold": [names["me_counter"], names["twist"], names["doorway"], names["auto1"]],
}
story = {
    "slug": "ep127-thousand-tellings",
    "title": "Grandpa Has Told This Story 998 TIMES",
    "made_for_kids": False,
    "premise": ("In a river town where any story told a thousand times happens exactly the way its thousandth telling "
                "ends, I find my grandpa telling a story about me to my empty chair every night, eyes shut, and "
                "stopping in the middle every time."),
    "twist": ("Grandpa has never finished the story because the end, and the thousandth telling, are mine to tell. "
              "I sit in my chair and tell it with my own ending: I drive home every Sunday to fish with him."),
    "world": ("A green tackle shop by a wide river: a long pine counter, a wall of bright lures, a wood stove, two "
              "worn red armchairs facing each other, one low amber lamp and a chalk slate by the till."),
    "voice": {"voice": "am_adam", "tempo": 1.03, "rate": 1.45},
    "key_color": "#3fd0ff",
    "gap": 0.12,
    "tail": 0.25,
    "fade_in": False,
    "fade_out": False,
    "rev": REV,
    "look": {"style": "closer", "fog": "#cfe6f5", "fog_density": 0.003, "fog_start": 40.0, "sky": "#8fd3ff",
             "sky_strength": 1.0, "exposure": 0.2, "flash_safe": True, "polish": polish},
    "grade": {"shadows": [0.0, 0.0, 0.03], "highlights": [0.015, 0.006, -0.01], "saturation": 1.1, "contrast": 1.05,
              "vignette": 0.2, "bloom": 0.15, "grain": 0.008},
    "phonemes": {},
    "cast": cast,
    "lines": lines,
    "shots": shots,
    "acting": acting,
    "cues": cues,
    "fx": [],
    "music": music,
    "sound": sound,
    "set_moves": [names["street1"], names["street2"], names["hook"], names["enter1"], names["enter2"],
                  names["chalk998"], names["chalk998b"], names["chalk999"], names["chalk1000"], names["chalk1000b"],
                  names["chalk9"]],
    "framing_ok": [names[k] for k in ("street1", "ceiling", "emptychair1", "emptychair2", "hook", "outside_night")],
    "framing_props": {"hook": [G.DOOR_X - 0.8, -5.7, 1.6]},
    # cuts that land inside a short telling shot, where the next framing is tighter (no light changes in any shot)
    "frames_ok": ["S72", "S74", "S86", "S94", "S103", "S106", "S108"],
    "clip_ok": [],
    "asr_forgive": ["missus", "mister", "nine hundred ninety seven", "nine ninety eight", "nine ninety nine",
                    "nine hundred ninety nine", "one thousand", "he'd", "he's"],
}
OUT.write_text(json.dumps(story, indent=1, ensure_ascii=False) + "\n")
print("wrote", OUT, f"({len(shots)} shots, {len(cues)} cues)")
