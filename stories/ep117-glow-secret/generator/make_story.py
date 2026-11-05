"""Writes ../story.json for ep117 "My Parents GLOW In The Dark" (script.md, 2026-11-05). Run: python stories/ep117-glow-secret/generator/make_story.py

The words are in lines.json. Places are in ../layout.py (shared with set.py). A character facing -y has yaw 0, +x 90,
+y 180, -x -90. Shots use the script's chunk numbers (a shot at "L07.2" starts on chunk 2 of line L07); captions are
split to two or three words and the references are remapped. Glow is only ever steady or a slow swell (flash_safe).
"""
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import layout as G  # noqa: E402

OUT = HERE.parent / "story.json"
REV = 9
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
idx = next(i for i, l in enumerate(lines) if l["id"] == "L16")
lines.insert(idx, {"id": "P01", "pause": 0.5, "chunks": [["", ""]]})


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


def fr(tx, ty, tz, d, lens, dx=0.0, dz=0.0, push=0.14, sx=0.0):
    """A camera in front of (tx, ty, tz) on the -y side, d metres away, easing in by `push`."""
    return mv([tx + dx, ty - d, tz + dz], [tx, ty, tz], lens,
              [tx + dx * 0.8 + sx, ty - d * (1 - push), tz + dz * 0.9], [tx, ty, tz], lens)


def person(skin, shirt, pants, shoes, hair="cap", hair_c="#2a1d15", pattern="solid", pattern_c=None, hat="none",
           hat_c="#333333", extras=(), eyes="round", sleeves="long", brow_w=1.0, **kw):
    d = {"age": "adult", "skin": skin, "shirt": shirt, "pattern": pattern, "pants": pants, "shoes": shoes,
         "sleeves": sleeves, "hair": hair, "hair_c": hair_c, "hat": hat, "hat_c": hat_c,
         "face": {"eyes": eyes, "brows": True, "ink": "#1c120c"}}
    if brow_w != 1.0:
        d["face"]["brow_w"] = brow_w
    if pattern_c:
        d["pattern_c"] = pattern_c
    if extras:
        d["extras"] = list(extras)
    d.update(kw)
    return d


cast = {
    "me": person("#d9a578", "#3d74d6", "#35507a", "#f2f2f0", hair="cap", hair_c="#4a2f1c", extras=["hooddown"],
                 sleeves="long", brow_w=1.9, body_width=G.BW),
    "mom": person("#e9b78f", "#e0a32a", "#4a4a5a", "#3a2a1a", hair="long", hair_c="#15110e", eyes="lashes",
                  brow_w=1.9, body_width=G.BW),
    "dad": person("#e2ad84", "#3f8a4e", "#4a4a52", "#3a2a1a", hair="buzz", hair_c="#6d6d76", pattern="plaid",
                  pattern_c="#1f4a2b", extras=["glasses"], extra_c="#2a2a2a", brow_w=1.9, body_width=G.BW),
    "roommate": person("#cf9d74", "#a8a8ae", "#3a4658", "#e8e8e8", hair="cap", hair_c="#2a1d15", hat="ballcap",
                       hat_c="#d8343a", sleeves="short", brow_w=1.9),
    "planner": person("#eab890", "#a05ad0", "#2a2a3a", "#2a2a2a", hair="bun", hair_c="#3a2418", eyes="lashes",
                      brow_w=1.9),
    "woman": person("#d8a27a", "#2fa8a0", "#4a5a78", "#2a2a2a", hair="long", hair_c="#6a3a22", eyes="lashes",
                    brow_w=1.9),
}
acting = {n: [{"at": 0, "hidden": True, "pos": [0, 0]}] for n in cast}
last = {n: [0, 0] for n in cast}
visible = set()
seated = set()
cues = []
SH = []


def cue(at, name, **kw):
    cues.append({"at": at, "name": name, **kw})


def sit(who, at, on=True, z=G.SEAT_Z):
    cue(at, "sit", who=who, on=on, z=z)
    (seated.add if on else seated.discard)(who)


def put(who, at, pos, yaw=None, seat=False, **kw):
    if who in seated and not seat:
        sit(who, at, False)
    p = list(pos)
    if at == 0:   # the first frame is already in place: no hidden key at the origin to clip at t=0
        acting[who] = [k_ for k_ in acting[who] if k_.get("at") != 0]
    else:
        acting[who].append({"at": at, "pos": list(last[who])})
    k = {"at": at, "pos": p, "blend": 0.0, "hidden": False, "arms": [0, 0], "side": [0, 0]}
    if yaw is not None:
        k["yaw"] = yaw
    k.update(kw)
    acting[who].append(k)
    last[who] = p
    visible.add(who)
    if seat:
        sit(who, at, True)


def beat(who, at, **kw):
    acting[who].append({"at": at, "pos": list(last[who]), **kw})


def go(who, at, pos, **kw):
    acting[who].append({"at": at, "pos": list(pos), **kw})
    last[who] = list(pos)


def only(at, names):
    for w in list(visible):
        if w not in names:
            acting[w].append({"at": at, "hidden": True})
            visible.discard(w)


def shot(at, camera, name, step=2, hand=None, follow=None):
    SH.append((at, camera, step, hand, follow, name))


def look(at, id_, dur=0.0):
    cue(at, "look", id=id_, dur=dur)


def glow(at, who, v, dur=0.0):
    cue(at, "g" + who, v=v, dur=dur)


def bar(at, dur=0.0, **kw):
    cue(at, "bar", dur=dur, **kw)


def move(at, obj, dur=0.0, **kw):
    cue(at, "mv", obj=obj, dur=dur, **kw)


SX, SY_ = G.ROOM
SY = G.SEAT_Y
BASE = 0.9                      # Mom's and Dad's steady glow, every shot
MX, DX_, ME_X = -0.45, 0.45, 0.0  # pair seats
TM, TD, TS = -0.68, 0.68, 0.0   # trio seats: Mom, Dad, me in the middle
GX, GY = G.GUM
LX, LY = G.LOT
CX, CY = G.CAR
BX, BY = G.BUS
PX, PY = G.PLAN
KX, KY = G.CARD
FX, FY = G.FRIDGE
TGX, TGY = G.STAGE


def seat(who, at, x, expr, **kw):
    put(who, at, [x, SY, 0.0], 0, seat=True, expr=expr, **kw)


def duo(at, em="smile", ed="smile", **kw):
    only(at, ["mom", "dad"])
    seat("mom", at, MX, em, **kw)
    seat("dad", at, DX_, ed, **kw)


def trio(at, em="smile", ed="smile", ee="smile", sp=None):
    only(at, ["mom", "dad", "me"])
    seat("mom", at, TM if sp is None else -sp, em)
    seat("dad", at, TD if sp is None else sp, ed)
    seat("me", at, TS, ee)


# initial state
cue(0, "look", id="room", dur=0.0)
glow(0, "mom", BASE)
glow(0, "dad", BASE)
glow(0, "me", 0.0)
glow(0, "oth", 0.0, 0.0)
bar(0, m=1.0, d=1.0, s=0.0)
cue(0, "shades", who="mom", v=0.0)
cue(0, "shades", who="dad", v=0.0)
cue(0, "spot", v=0.0)
cue(0, "moths", v=0.0)
cue(0, "bglow", v=0.0)
cue(0, "waiter", v=0.0)

# ===================================================================== 01 the hook (L01 to L02)
duo(0, "smile", "smile")
shot(0, mv([0.0, SY - 4.6, 1.28], [0.0, SY, 1.15], 34, [0.0, SY - 4.2, 1.28], [0.0, SY, 1.15], 34), "hook", hand=0.006)
only("L02", ["me"])
seat("me", "L02", 0.25, "smirk")
shot("L02", fr(0.25, SY, 1.15, 3.7, 34, dx=0.15), "mecross")
duo("L02.2", "sad-smile", "sad-smile")
shot("L02.2", fr(0.0, SY, 1.15, 4.5, 34, dx=-0.1, push=0.08), "sheep")

# ===================================================================== 02 the montage (L03 to L06)
look("L03", "day")
only("L03", ["woman"])
put("woman", "L03", [BX - 0.2, 2.2, 0.0], 0, expr="neutral", arms=[0, 0])
glow("L03", "oth", 0.35)
glow("L03.1", "oth", 0.95, 1.0)
shot("L03", fr(BX - 0.2, 2.2, 1.2, 4.0, 34, dx=0.3), "bus1")
beat("woman", "L03.2", expr="worried")
shot("L03.2", fr(BX - 0.2, 2.2, 1.45, 2.9, 34, dx=-0.3), "bus2")
# L04 planner behind a door
glow("L04", "oth", 1.0)
only("L04", ["planner"])
put("planner", "L04", [PX + 0.7, 3.0, 0.0], 0, expr="smirk", arms=[0, 0])
beat("planner", "L04+0.5", arms=[0, 125], side=[0, 45])
shot("L04", fr(PX + 0.65, 3.0, 1.3, 3.5, 34, dx=0.0, push=0.06), "planner")
# L05 the card table
glow("L05", "oth", 0.0)
only("L05", [])
shot("L05", mv([KX + 0.2, -1.3, 1.9], [KX, 1.9, 0.85], 32, [KX + 0.5, -0.2, 1.6], [KX, 1.9, 0.85], 32), "cards")
# L06 the roommate and the fridge
glow("L06", "oth", 0.9)
only("L06", ["roommate"])
put("roommate", "L06", [FX + 0.7, 2.1, 0.0], -12, expr="sad-smile", arms=[0, 80])
move("L06", "box", x=FX + 0.7 + 0.4, y=1.36, z=1.48)
cue("L06", "fridgeglow", v=1.0)
shot("L06", fr(FX + 0.3, 2.4, 1.25, 4.4, 28, dx=-0.1, push=0.06), "fridge1")
glow("L06.2", "oth", 1.0, 1.0)
shot("L06.2", fr(FX + 0.3, 2.4, 1.25, 4.4, 28, dx=0.3, push=0.06), "fridge2")

# ===================================================================== 03 thirty years (L07 to L10)
look("L07", "room")
move("L07-0.1", "box", z=-60.0)
cue("L07", "fridgeglow", v=0.0)
glow("L07", "oth", 0.0)
duo("L07", "warm", "warm")
shot("L07", mv([0.15, SY - 4.6, 1.3], [0.0, SY, 1.15], 34, [0.05, SY - 4.2, 1.3], [0.0, SY, 1.15], 34), "duo7")
duo("L08", "smile", "smile")
shot("L08", mv([3.0, -0.4, 1.5], [0.0, SY, 1.4], 36, [2.7, -0.2, 1.5], [0.0, SY, 1.4], 36), "side8")
trio("L09", "smile", "smile", "smile")
shot("L09", mv([0.0, SY - 5.25, 1.2], [0.0, SY, 1.25], 34, [0.0, SY - 5.0, 1.2], [0.0, SY, 1.25], 34), "wide9")
only("L10", ["mom", "dad"])
seat("mom", "L10", MX, "smile")
seat("dad", "L10", DX_, "smile")
shot("L10", mv([0.1, -0.7, 2.0], [0.0, 3.0, 1.2], 34, [0.05, -0.2, 1.95], [0.0, 3.0, 1.2], 34), "pizzaclose")
seat("mom", "L10.1", -0.45, "sad-smile", arms=[0, 70], side=[0, -6])
seat("dad", "L10.1", 0.45, "sad-smile", arms=[70, 0], side=[-6, 0])
look("L10.1", "roomdim", 0.6)
cue("L10.1", "pie", v=0.0)
move("L10.1", "slice", dur=0.5, x=-0.12, y=2.7, z=0.99)
move("L10.1+0.7", "slice", dur=0.5, x=0.12, y=2.7, z=0.99)
shot("L10.1", mv([0.0, 1.5, 1.75], [0.0, 2.8, 0.98], 30, [0.0, 1.8, 1.7], [0.0, 2.8, 0.98], 30), "nudge")

# ===================================================================== 04 the dark lot (L11 to L15)
look("L11", "lot")
cue("L11", "pie", v=1.0)
only("L11", ["mom", "dad"])
put("mom", "L11", [LX - 0.65, CY - 4.6, 0.0], 0, expr="smile")
put("dad", "L11", [LX + 0.65, CY - 4.6, 0.0], 0, expr="smile")
go("mom", "L11>", [LX - 0.65, CY - 5.3, 0.0], expr="smile")
go("dad", "L11>", [LX + 0.65, CY - 5.3, 0.0], expr="smile")
shot("L11", mv([LX, 6.9, 1.45], [LX, CY - 4.4, 1.25], 26, [LX, 7.2, 1.45], [LX, CY - 4.6, 1.25], 26), "lot11", step=1)
only("L12", ["mom", "dad"])
put("mom", "L12", [LX - 0.65, CY - 5.3, 0.0], 0, expr="warm")
put("dad", "L12", [LX + 0.65, CY - 5.3, 0.0], 0, expr="warm")
cue("L12", "moths", v=1.0, dur=0.4)
shot("L12", mv([LX, 6.9, 1.45], [LX, CY - 5.3, 1.3], 26, [LX, 7.2, 1.45], [LX, CY - 5.3, 1.3], 26), "moth12")
cue("L13-0.1", "moths", v=0.0, dur=0.3)
only("L13", ["me"])
put("me", "L13", [LX + 0.1, CY - 2.2, 0.0], 0, expr="worried")
shot("L13", fr(LX + 0.1, CY - 2.2, 1.3, 3.3, 34, dx=0.2), "meuneasy")
# L14 the joke inserts
look("L14", "room")
only("L14", ["mom"])
seat("mom", "L14", 0.0, "smile")
cue("L14", "shades", who="mom", v=1.0)
shot("L14", fr(0.0, SY, 1.15, 3.3, 34, dx=-0.15), "shadesmom")
look("L14.2", "stage")
cue("L14.2-0.1", "shades", who="mom", v=0.0)
cue("L14.2", "shades", who="dad", v=1.0)
cue("L14.2", "spot", v=1.0, dur=0.5)
only("L14.2", ["dad"])
put("dad", "L14.2", [TGX, 3.0, 0.0], 0, expr="smile")
shot("L14.2", fr(TGX, 3.0, 1.35, 3.3, 34, dx=0.2), "spotdad")
look("L15", "room")
cue("L15", "spot", v=0.0)
cue("L15", "shades", who="dad", v=0.0)
only("L15", ["me"])
seat("me", "L15", 0.2, "neutral")
shot("L15", fr(0.2, SY, 1.15, 3.3, 34, dx=-0.2), "meknow")

# ===================================================================== 05 the two asks (L16 to L20)
look("P01", "gum")
only("P01", [])
shot("P01", mv([GX - 0.4, 0.6, 1.9], [GX, GY, 1.45], 40, [GX - 0.2, 1.0, 1.85], [GX, GY, 1.45], 40), "gumdrop")
only("L16", ["mom", "me"])
put("me", "L16", [GX - 1.15, 2.45, 0.0], 0, expr="neutral")
put("mom", "L16", [GX - 0.55, 2.45, 0.0], 0, expr="sad-smile")
shot("L16", mv([GX - 0.44, 2.45 - 5.4, 1.2], [GX - 0.44, 2.45, 1.2], 34, [GX - 0.44, 2.45 - 5.2, 1.2], [GX - 0.44, 2.45, 1.2], 34), "gum16")
only("L17", ["mom"])
put("mom", "L17", [GX - 0.55, 2.45, 0.0], 0, expr="sheepish" if False else "sad-smile")
glow("L17", "mom", 1.8, 1.3)
glow("L18+0.3", "mom", BASE, 0.9)
bar("L17", dur=1.3, m=1.2)
bar("L18+0.3", dur=0.9, m=1.0)
shot("L17", fr(GX - 0.55, 2.45, 1.3, 3.2, 34, dx=0.15, dz=-0.1), "momflare")
put("mom", "L17.2+0.45", [GX - 1.65, 2.45, 0.0], 0, expr="sad-smile")
cue("L17.1", "gshadow", v=1.0, dur=0.5)
shot("L17.2+0.45", mv([GX + 0.5, -1.4, 1.3], [GX + 0.5, 3.2, 1.2], 26, [GX + 0.45, -0.9, 1.3], [GX + 0.45, 3.2, 1.2], 26), "shadows")
only("L18+0.18", ["mom"])
cue("L18+0.18", "gshadow", v=0.0)
put("mom", "L18+0.18", [GX - 0.55, 2.45, 0.0], 0, expr="sad-smile", arms=[0, 0])
beat("mom", "L18.1", arms=[0, 112], side=[0, -28])
shot("L18+0.18", fr(GX - 0.55, 2.45, 1.3, 3.2, 34, dx=-0.1, dz=-0.1), "momsh")
look("L19", "lot")
glow("L19", "mom", BASE)
only("L19", ["dad", "me"])
put("me", "L19", [LX + 0.55, CY - 4.6, 0.0], 0, expr="neutral")
put("dad", "L19", [LX - 0.55, CY - 4.6, 0.0], 0, expr="sad-smile")
shot("L19", mv([LX, 6.7, 1.3], [LX, CY - 4.6, 1.25], 30, [LX, 7.0, 1.3], [LX, CY - 4.6, 1.25], 30), "dadme19")
only("L20", ["dad"])
put("dad", "L20", [LX - 0.9, CY - 4.6, 0.0], 0, expr="sad-smile", arms=[0, 0])
glow("L20-0.1", "dad", BASE)
glow("L20", "dad", 1.7, 0.6)
glow("L20.1+0.2", "dad", BASE, 0.7)
beat("dad", "L20.1", arms=[0, 112], side=[0, -28])
shot("L20", fr(LX - 0.5, CY - 4.6, 1.3, 3.8, 30, dx=0.0, dz=-0.1), "dadflare")
only("L21", ["me"])
put("me", "L21", [LX + 0.1, CY - 2.2, 0.0], 0, expr="wide")
shot("L21", fr(LX + 0.1, CY - 2.2, 1.3, 3.2, 34, dx=-0.2), "mestun")

# ===================================================================== 06 the reveal (L22 to L27)
look("L22", "room")
only("L22", [])
shot("L22", mv([3.8, 0.2, 1.5], [2.4, 3.4, 0.9], 34, [3.5, 0.5, 1.45], [2.4, 3.4, 0.9], 34), "emptybooth")
duo("L23", "fish", "fish")
only("L23", ["mom"])
seat("mom", "L23", 0.0, "fish")
shot("L23", fr(0.0, SY, 1.3, 2.8, 34, dx=0.1), "momfish")
only("L23.1", ["dad"])
seat("dad", "L23.1", 0.0, "fish")
shot("L23.1", fr(0.0, SY, 1.3, 2.8, 34, dx=-0.1), "dadfish")
duo("L24", "polite", "polite", head=[0, 8])
shot("L24", mv([3.0, -0.2, 1.5], [0.0, SY, 1.3], 36, [2.7, 0.0, 1.5], [0.0, SY, 1.3], 36), "polite1")
duo("L24.2", "polite", "polite", head=[0, 12])
shot("L24.2", mv([0.0, SY - 5.0, 1.15], [0.0, SY, 1.15], 34, [0.0, SY - 4.6, 1.15], [0.0, SY, 1.15], 34), "reveal", hand=0.006)
only("L25", [])
shot("L25", mv([-0.35, 1.3, 1.5], [0.0, 2.8, 1.0], 36, [0.3, 1.6, 1.35], [0.0, 2.8, 1.0], 36), "pizza25")
only("L26", ["me"])
seat("me", "L26", 0.0, "laugh")
shot("L26", fr(0.0, SY, 1.15, 3.1, 34), "melaugh")
only("L27", ["mom"])
seat("mom", "L27", 0.0, "sad-smile")
shot("L27", fr(0.0, SY, 1.3, 2.9, 34, dx=0.1), "momsock")
# retry 2026-11-05: L27b, Dad's answer to Mom's sock line. His face in the booth, steady base glow (no glow cue, no change)
only("L27b", ["dad"])
seat("dad", "L27b", 0.0, "sad-smile")
shot("L27b", fr(0.0, SY, 1.3, 2.9, 34, dx=-0.1), "dadstare")

# ===================================================================== 07 the warm turn (L28 to L33)
trio("L28", "sad-smile", "sad-smile", "smile")
shot("L28", mv([0.0, SY - 5.25, 1.2], [0.0, SY, 1.25], 34, [0.0, SY - 5.0, 1.2], [0.0, SY, 1.25], 34), "trio28")
trio("L29", "smile", "smile", "neutral")
shot("L29", mv([1.6, -0.8, 1.5], [0.0, SY, 1.4], 34, [1.4, -0.5, 1.5], [0.0, SY, 1.4], 34), "side29")
only("L30", ["me"])
seat("me", "L30", 0.0, "smile")
glow("L30", "me", 1.4, 1.2)
bar("L30", dur=1.2, s=1.0)
shot("L30", fr(0.0, SY, 1.25, 2.8, 34, dx=0.1), "meglow")
trio("L31", "smile", "smile", "smile")
glow("L31", "me", 1.4)
cue("L31", "bglow", v=1.0, dur=1.0)
shot("L31", mv([0.0, SY - 5.25, 1.2], [0.0, SY, 1.25], 34, [0.0, SY - 5.0, 1.2], [0.0, SY, 1.25], 34), "trio31")
shot("L31.2", mv([-1.6, -0.8, 1.5], [0.0, SY, 1.4], 34, [-1.4, -0.5, 1.5], [0.0, SY, 1.4], 34), "side31")
trio("L32", "laugh", "laugh", "smile", sp=0.58)
cue("L32", "waiter", v=1.0, dur=0.0)
move("L32", "wa", x=2.5, y=2.35, z=1.25)
move("L32+0.1", "wa", dur=0.9, x=0.9, y=2.55, z=1.01)
shot("L32", mv([0.3, SY - 5.0, 1.2], [0.3, SY, 1.25], 34, [0.25, SY - 4.8, 1.2], [0.25, SY, 1.25], 34), "trio32")
cue("L33-0.1", "waiter", v=0.0)
only("L33", ["me"])
seat("me", "L33", 0.0, "smile")
shot("L33", fr(0.0, SY, 1.25, 2.8, 34, dx=-0.1), "mefinal")
duo("L33.1", "smile", "smile")
cue("L33.1", "bglow", v=0.0, dur=0.3)
shot("L33.1", mv([0.0, SY - 4.6, 1.28], [0.0, SY, 1.15], 34, [0.0, SY - 4.2, 1.28], [0.0, SY, 1.15], 34), "loop", hand=0.006)

# ---------------------------------------------------------------------------------------------- finish
for k_ in acting.values():
    remap_all(k_)
remap_all(cues)
shots, names = [], {}
for i, (at, camera, step, hand, follow, nm) in enumerate(SH):
    s = {"id": f"S{i + 1:02d}", "cam": camera, "step": step}
    if i:
        s["at"] = remap(at)
    if hand is not None:
        s["hand"] = hand
    if follow:
        s["follow"] = follow
    shots.append(s)
    names[nm] = s["id"]

sfx = [
    {"at": "L01.1", "kind": "bell", "db": -15},
    {"at": "L17.1-0.8", "kind": "riser", "db": -20, "dur": 0.9},
    {"at": "L30", "kind": "bell", "db": -14},
    {"at": "L10.1+0.1", "kind": "click", "db": -22},
    {"at": "L22", "kind": "thud", "db": -22},
    {"at": "L31", "kind": "bell", "db": -18},
    {"at": "L32+0.9", "kind": "thud", "db": -22},
]
music = {
    "root": 58, "mode": "major", "bpm": 132, "seed": 117,
    "sections": [
        {"at": 0, "voices": ["pad", "piano", "pulse"], "energy": 0.45},
        {"at": "L13", "voices": ["pad", "pulse"], "energy": 0.3},
        {"at": "L16", "voices": ["drone", "pulse"], "energy": 0.3},
        {"at": "L21", "voices": ["pad", "piano"], "energy": 0.35},
        {"at": "L27", "voices": ["pad", "piano", "pulse", "musicbox"], "energy": 0.6},
    ],
}
sound = {
    "floor": "wood", "steps_db": -26,
    "ambience": [{"kind": "room", "from": 0, "to": "L11", "lufs": -44},
                 {"kind": "crickets", "from": "L11", "to": "L14", "lufs": -44},
                 {"kind": "crickets", "from": "L19", "to": "L22", "lufs": -44},
                 {"kind": "room", "from": "L22", "to": "end", "lufs": -44}],
    "sfx": sfx,
    "music_drops": [{"from": "P01", "to": "P01>"}],
    "rev": REV,
}
remap_all(sfx)
remap_all(music["sections"])
remap_all(sound["music_drops"])
remap_all(sound["ambience"])
polish = {"reveal": [remap("L24.2")], "twist": remap("L21"),
          "emph": [remap("L01.1"), remap("L17.2"), remap("L24.3"), remap("L27.2"), remap("L30")],
          "hold": [names[n_] for n_ in ("reveal", "wide9", "trio28", "trio31", "trio32", "emptybooth", "lot11", "hook", "sheep", "duo7", "side8", "moth12", "gum16", "dadme19", "polite1", "side29", "side31", "loop", "nudge", "shadows", "dadflare", "momflare", "momsh", "fridge1", "fridge2", "planner")]}
story = {
    "slug": "ep117-glow-secret",
    "title": "My Parents GLOW In The Dark 💡",
    "made_for_kids": False,
    "premise": ("In my town you glow while you keep a secret, brighter every day. My parents have glowed like "
                "lighthouses for thirty years, and one Friday at our pizza booth I finally ask each of them "
                "what they are hiding."),
    "twist": ("The huge secret is tiny and the same on both sides: neither of them liked the pizza on their first "
              "date, and each has ordered it every Friday since so the other won't feel bad. I promise to keep "
              "it, so now I glow too."),
    "world": ("A bright red-and-cream pizza place on a Friday evening: a red vinyl booth by a big window, a checker "
              "floor, round pendant lamps, a gumball machine by the door, and a dusky parking lot outside."),
    "voice": {"voice": "am_adam", "tempo": 1.03, "rate": 1.45},
    "key_color": "#ff4b3a",
    "gap": 0.15,
    "tail": 0.2,
    "fade_in": False,
    "fade_out": False,
    "rev": REV,
    "look": {"style": "closer", "fog": "#d6e0ff", "fog_density": 0.002, "fog_start": 40.0, "sky": "#ffe8c8",
             "sky_strength": 1.0, "exposure": 0.1, "flash_safe": True, "polish": polish},
    "grade": {"shadows": [0.0, 0.0, 0.03], "highlights": [0.03, 0.012, -0.02], "saturation": 1.1, "contrast": 1.05,
              "vignette": 0.2, "bloom": 0.35, "grain": 0.008},
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
    "framing_ok": ["S14", "S24", "S27", "S29"],
    "frames_ok": ["S19", "S27"],
}
OUT.write_text(json.dumps(story, indent=1, ensure_ascii=False) + "\n")
print({v: k for k, v in names.items()}) if __import__("os").environ.get("NAMES") else None
print("wrote", OUT, f"({len(shots)} shots, {len(cues)} cues)")
