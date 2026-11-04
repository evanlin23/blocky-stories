"""Writes ../story.json for ep102 "aunt peaches" (script.md, 2026-11-04). Run: python stories/ep102-aunt-peaches/generator/make_story.py

The words are in lines.json. Places are in ../layout.py (shared with set.py). A character facing -y has yaw 0, +x 90,
+y 180, -x -90. Shots use the script's chunk numbers (a shot at "L07.2" starts on chunk 2 of line L07); captions are
split to two or three words and the references are remapped.
"""
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import layout as G  # noqa: E402

OUT = HERE.parent / "story.json"
REV = 2
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
idx = next(i for i, l in enumerate(lines) if l["id"] == "L18")
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
    "me": person("#dca97c", "#f8f8f6", "#b8a77a", "#f4f4f2", hair="cap", hair_c="#15100c", hat="ballcap", hat_c="#e8493a",
                 sleeves="short", brow_w=1.9),
    "clem": person("#e8b890", "#ffd34d", "#4a6a9a", "#7a4a2a", hair="cap", hair_c="#b8b8c0", hat="bucket", hat_c="#e8cf8a",
                   extras=["apron"], extra_c="#4a6a9a", eyes="lashes", brow_w=1.9),
    "mom": person("#e6b48c", "#2fa8a0", "#4a4a5a", "#3a2a1a", hair="cap", hair_c="#1a1410", extras=["glasses"],
                  extra_c="#2a2a2a", eyes="lashes", brow_w=1.9),
    "carrier": person("#e2b088", "#8aa0c0", "#4a5a78", "#2a2a2a", hair="cap", hair_c="#d8d8d8", hat="bucket", hat_c="#d8c8a0"),
    "carrier0": person("#e2b088", "#8aa0c0", "#4a5a78", "#2a2a2a", hair="cap", hair_c="#3a2418", hat="bucket", hat_c="#d8c8a0"),
    "b1": person("#c89870", "#c04a3a", "#4a5a4a", "#3a2a1a", hair="spiky", hair_c="#3a2a1a", pattern="plaid",
                 pattern_c="#2a2a2a", extras=["backpack"], extra_c="#4a8a5a", sleeves="short"),
    "b2": person("#c89870", "#3a6aa8", "#4a5a4a", "#3a2a1a", hair="swoop", hair_c="#3a2a1a", pattern="plaid",
                 pattern_c="#1a2a3a", extras=["backpack"], extra_c="#c0543a", sleeves="short"),
    "b3": person("#c89870", "#2fa8a0", "#3a4a5a", "#2a2a2a", hair="spiky", hair_c="#3a2a1a", sleeves="short"),
    "b4": person("#c89870", "#2fa8a0", "#3a4a5a", "#2a2a2a", hair="swoop", hair_c="#3a2a1a", sleeves="short"),
}
acting = {n: [{"at": 0, "hidden": True, "pos": [0, 0]}] for n in cast}
last = {n: [0, 0] for n in cast}
visible = set()
cues = []
SH = []


def put(who, at, pos, yaw=None, **kw):
    p = list(pos)
    acting[who].append({"at": at, "pos": list(last[who])})
    k = {"at": at, "pos": p, "blend": 0.0, "hidden": False}
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


def shot(at, camera, name, step=2, hand=None, follow=None):
    SH.append((at, camera, step, hand, follow, name))


def look(at, id_, dur=0.0):
    cue(at, "look", id=id_, dur=dur)


def move(at, obj, dur=0.0, **kw):
    cue(at, "mv", obj=obj, dur=dur, **kw)


def odo(at, n, dur=0.0):
    cue(at, "odo", n=float(n), dur=dur)


def sit(who, at, on=True, z=0.7):
    cue(at, "sit", who=who, on=on, z=z)


def ride(who, at, on=True):
    cue(at, "ride", who=who, on=on)


FX, FY = G.FARM
PZ = 0.45                                # the porch deck
MX, MY = G.MAIL
GX, GY = G.GAS
RX, RY = G.ROOM
KX, KY = G.KIT
CX, CY = G.CITY
BX, BY = G.BUS
QX, QY = G.ROAD
TX, TY = GX - 11.0, GY - 1.0             # the picnic table
SWX, SWY = -5.0, 3.2                     # the porch swing
RAILP = (5.0, 1.55, 1.62)                # the rail peach
CARX, CARY = QX, 0.0                     # my car on the ridge road
DRV = (QX + 0.45, 0.45)                  # the driver's seat
MC = (QX - 1.7, 31.0)                    # Mom's open car by the fence post
MCD = (MC[0] + 0.45, MC[1] + 0.45)
POSTX = QX - 4.4

# ===================================================================== 01 the hook (L01 to L02)
look(0, "day")
odo(0, 412)
cue(0, "gold", v=0.0)
cue(0, "sill", n=0.0)
cue(0, "rock", a=0.0)
cue(0, "lane", v=0.0)
cue(0, "gone", v=0.0)
cue(0, "map", v=0.0)
move(0, "pc1", x=RAILP[0], y=RAILP[1], z=RAILP[2])
move(0, "gateleaf", yaw=80.0)
move(0, "mecar", x=CARX, y=CARY, z=0.0, yaw=0.0)
put("clem", 0, [4.5, 2.35, PZ], 0, expr="smile", arms=[0, 80])
shot(0, mv([5.35, -1.5, 2.05], [5.3, 1.6, 1.65], 40, [5.35, -0.9, 2.0], [5.3, 1.6, 1.65], 40), "peachclose")
only("L01.1", ["me"])
put("me", "L01.1", [2.2, 2.6, PZ], 0, expr="smirk", head=[-25, 0], look=[0.7, 0.0])
shot("L01.1", fr(2.2, 2.6, 1.75, 4.2, 40, dx=-0.3), "mesus")
only("L01.2", [])
move("L01.2-0.5", "gateleaf", yaw=80.0)
move("L01.2", "gateleaf", dur=0.7, yaw=0.0)
shot("L01.2", mv([3.4, -14.0, 1.4], [0.0, -8.0, 1.0], 38, [2.6, -13.0, 1.4], [0.0, -8.0, 1.0], 38), "gateshut")
# L02: keys away from the peach
only("L02", ["me"])
put("me", "L02", [5.5, 2.35, PZ], 0, expr="grin", arms=[0, 78])
move("L02", "keys", dur=0.9, x=6.2)
shot("L02", mv([5.9, -1.8, 2.1], [5.5, 1.7, 1.75], 38, [5.8, -1.2, 2.1], [5.5, 1.7, 1.75], 38), "keysaway")
only("L02.1", [])
shot("L02.1", mv([5.3, 0.1, 1.95], [5.0, 1.6, 1.6], 50, [5.1, 0.7, 1.8], [5.0, 1.6, 1.6], 50), "peachalone")

# ===================================================================== 02 the montage (L03 to L08)
# L03: the mail carrier, first delivery
look("L03", "day")
move("L03", "pc1", z=-60.0)
only("L03", ["carrier0"])
put("carrier0", "L03", [MX - 4.0, 1.5], 0, expr="grin", arms=[0, 128])
move("L03", "pc2", x=MX - 3.75, y=1.0, z=1.55)
beat("carrier0", "L03.1", expr="smile", arms=[0, 128])
shot("L03", mv([MX - 3.2, -2.6, 1.85], [MX - 4.0, 1.5, 1.6], 42, [MX - 3.4, -1.9, 1.8], [MX - 4.0, 1.5, 1.6], 42), "carbite")
go("carrier0", "L03.2-0.6", [MX - 3.8, 1.5], expr="smile", arms=[0, 0])
go("carrier0", "L03.2>", [MX + 1.0, 1.5], expr="smile", arms=[0, 0])
move("L03.2-0.6", "pc2", z=-60.0)
shot("L03.2", mv([MX - 1.0, -4.5, 1.6], [MX - 3.0, 1.5, 1.2], 36, [MX + 0.6, -4.5, 1.6], [MX - 0.8, 1.5, 1.2], 36), "carwalk")
# L04
only("L04", ["carrier"])
put("carrier", "L04", [MX + 1.0, 1.7], 0, expr="smile", arms=[0, 150])
beat("carrier", "L04+0.5", arms=[0, 120])
beat("carrier", "L04+0.9", arms=[0, 155])
shot("L04", fr(MX + 1.0, 1.7, 1.55, 4.6, 36, dx=0.4), "cargray")
go("carrier", "L04.1", [MX + 1.0, 1.7], arms=[0, 0])
go("carrier", "L04.1>", [MX - 6.0, 1.9], arms=[0, 0])
shot("L04.1", mv([MX + 1.5, -5.0, 1.7], [MX - 1.0, 1.8, 1.4], 34, [MX - 2.0, -5.0, 1.7], [MX - 4.0, 1.8, 1.4], 34), "carroute")
put("carrier", "L04.2", [MX - 6.0, 1.9], 0, expr="smile", arms=[0, 140])
beat("carrier", "L04.2+0.5", arms=[0, 165])
shot("L04.2", fr(MX - 6.0, 1.9, 1.7, 3.6, 46, dx=-0.3), "cartip")
# L05: the brothers at the pie
look("L05", "day")
only("L05", ["b1", "b2"])
put("b1", "L05", [TX - 0.95, TY, 0.0], 90, expr="smile")
put("b2", "L05", [TX + 0.95, TY, 0.0], -90, expr="smile")
sit("b1", "L05", True, 0.62)
sit("b2", "L05", True, 0.62)
shot("L05", mv([TX + 2.2, TY - 5.8, 1.7], [TX, TY, 1.25], 38, [TX + 1.8, TY - 5.0, 1.7], [TX, TY, 1.25], 38), "pie1")
beat("b1", "L05.2", expr="grin", head=[0, 12])
beat("b2", "L05.2", expr="grin", head=[0, 12])
shot("L05.2", mv([TX - 0.2, TY - 3.6, 1.85], [TX, TY, 1.25], 46, [TX - 0.1, TY - 3.1, 1.8], [TX, TY, 1.25], 46), "pie2")
# L06: the gas station
only("L06", ["b3", "b4"])
sit("b1", "L06", False)
sit("b2", "L06", False)
put("b3", "L06", [GX + 0.2, GY - 1.6], 0, expr="smile", arms=[0, 40])
put("b4", "L06", [GX - 1.6, GY - 1.6], 0, expr="grin", arms=[0, 150])
beat("b4", "L06+0.5", arms=[0, 120])
shot("L06", mv([GX - 0.3, GY - 9.0, 1.8], [GX - 0.5, GY - 1.6, 1.8], 32, [GX - 0.3, GY - 7.6, 1.8], [GX - 0.5, GY - 1.6, 1.8], 32), "gasst")
put("b3", "L06.1", [GX - 0.6, GY - 2.0], 0, expr="laugh", arms=[0, 40])
put("b4", "L06.1", [GX + 0.6, GY - 2.0], 0, expr="laugh", arms=[40, 0])
shot("L06.1", fr(GX, GY - 2.0, 1.7, 4.6, 36, dx=0.3), "gasfun")
# L07: the guest room
look("L07", "day")
only("L07", [])
move("L07", "pc2", x=RX - 1.85, y=RY + 0.8, z=1.08)
shot("L07", mv([RX - 1.6, RY - 2.2, 1.75], [RX - 1.9, RY + 0.8, 0.95], 40, [RX - 1.7, RY - 1.6, 1.65], [RX - 1.9, RY + 0.8, 0.95], 40), "bedpeach")
only("L07.1", ["clem"])
put("clem", "L07.1", [RX + 3.1, RY + 2.7, 0.0], 0, expr="warm", head=[0, 0])
shot("L07.1", fr(RX + 3.1, RY + 2.7, 1.7, 4.8, 36, dx=-0.5), "clemdoor")
only("L07.3", ["me"])
put("me", "L07.3", [RX - 0.2, RY + 1.2, 0.0], 0, expr="worried", head=[-30, 15])
beat("me", "L07.4", head=[25, 0], expr="smirk")
shot("L07.3", fr(RX - 0.2, RY + 1.2, 1.7, 4.2, 38, dx=0.3), "melook")
# L08: the sill
only("L08", ["me"])
put("me", "L08", [RX + 0.3, RY + 2.1, 0.0], 160, expr="soft", arms=[0, 0])
move("L08", "pc2", dur=0.0, x=RX - 0.2, y=RY + 2.6, z=1.1)
move("L08+0.2", "pc2", dur=0.7, x=RX - 0.45, y=RY + 3.2, z=1.07)
beat("me", "L08+0.2", arms=[0, 80])
beat("me", "L08.1", arms=[0, 0])
shot("L08", mv([RX + 3.6, RY - 1.2, 1.9], [RX + 0.2, RY + 2.5, 1.2], 36, [RX + 3.0, RY - 0.6, 1.9], [RX + 0.2, RY + 2.5, 1.2], 36), "sillset")
move("L08.2-0.1", "pc2", z=-60.0)
cue("L08.2-0.1", "sill", n=1.0)
cue("L08.2", "sill", n=12.0, dur=1.4)
shot("L08.2", mv([RX + 0.9, RY - 0.4, 1.7], [RX + 0.1, RY + 3.2, 1.1], 42, [RX + 0.4, RY + 0.4, 1.4], [RX + 0.1, RY + 3.2, 1.1], 42), "sillrow")

# ===================================================================== 03 the drive grows (L09 to L17)
look("L09", "day")
only("L09", ["me"])
cue("L09", "sit", who="me", on=True, z=0.7)
put("me", "L09", [DRV[0], DRV[1], 0.0], 0, expr="worried", arms=[0, 60])
shot("L09", mv([QX + 3.4, -5.4, 2.0], [QX + 0.5, 0.0, 1.3], 36, [QX + 3.0, -4.6, 1.9], [QX + 0.5, 0.0, 1.3], 36), "drive1")
odo("L09.1", 12, 1.0)
shot("L09.1", mv([QX + 1.4, -2.6, 1.7], [QX + 0.45, 0.45, 1.4], 52, [QX + 1.2, -2.0, 1.7], [QX + 0.45, 0.45, 1.4], 52), "odoclose")
only("L10", [])
shot("L10", mv([QX + 1.0, 36.0, 4.5], [QX, -10.0, 1.0], 30, [QX + 0.6, 24.0, 3.6], [QX, -14.0, 1.0], 30), "valleydown")
shot("L11", mv([QX + 2.0, -40.0, 3.5], [QX, 80.0, 6.0], 24, [QX + 1.5, -30.0, 3.3], [QX, 80.0, 6.0], 24), "ridge2")
odo("L11", 30)
odo("L11.1", 90)
shot("L11.1", mv([QX - 2.5, -42.0, 4.5], [QX + 4.0, 100.0, 8.0], 24, [QX - 2.0, -30.0, 4.2], [QX + 4.0, 100.0, 8.0], 24), "ridge3")
look("L12", "dusk", 0.8)
odo("L12", 240)
only("L12", ["me"])
put("me", "L12", [DRV[0], DRV[1], 0.0], 0, expr="soft", arms=[0, 0], head=[0, 0])
shot("L12", mv([QX + 3.6, -4.8, 1.8], [QX + 0.2, 0.2, 1.1], 34, [QX + 3.2, -4.2, 1.8], [QX + 0.2, 0.2, 1.1], 34), "wrappers")
beat("me", "L12.1", expr="squeeze")
acting["me"].append({"from": "L12.1", "to": "L12.1+0.8", "mouth": [0.0, 1.0]})
shot("L12.1", mv([QX + 1.6, -3.2, 1.8], [QX + 0.45, 0.45, 1.5], 52, [QX + 1.3, -2.4, 1.78], [QX + 0.45, 0.45, 1.5], 52), "yawn")
look("L13", "day", 0.8)
cue("L13", "map", v=1.0)
beat("me", "L13", expr="soft", arms=[0, 0])
shot("L13", mv([QX + 0.9, -3.6, 2.6], [QX - 0.05, -0.2, 1.1], 46, [QX + 0.6, -2.8, 2.4], [QX - 0.05, -0.2, 1.1], 46), "mapclose")
beat("me", "L13.1", expr="worried", arms=[80, 0])
shot("L13.1", mv([QX + 1.3, -3.0, 2.5], [QX + 0.0, 0.2, 1.4], 40, [QX + 1.0, -2.4, 2.3], [QX + 0.0, 0.2, 1.4], 40), "maptrace")
# L14: Mom in the city kitchen
cue("L14", "map", v=0.0)
sit("me", "L14", False)
only("L14", ["mom"])
put("mom", "L14", [KX - 2.6, KY + 2.0], 0, expr="sad-smile", head=[0, 6])
shot("L14", fr(KX - 2.6, KY + 2.0, 1.55, 4.4, 40, dx=0.4), "momsink")
put("mom", "L14.1", [KX - 2.6, KY + 2.0], 0, expr="sad-smile", arms=[0, 150], head=[-8, 0])
move("L14.1", "phone", x=KX - 2.6 + 0.4, y=KY + 1.82, z=1.72)
shot("L14.1", fr(KX - 2.6, KY + 2.0, 1.6, 3.4, 48, dx=-0.3), "momphone")
# L15: Mom misses the turn
move("L15", "phone", z=-60.0)
only("L15", ["mom"])
sit("mom", "L15", True, 0.7)
put("mom", "L15", [MCD[0], MCD[1] + 0.0, 0.0], 0, expr="worried", arms=[0, 0])
shot("L15", mv([QX + 1.5, MC[1] - 5.5, 1.9], [MC[0] + 0.3, MC[1] + 0.3, 1.45], 32, [QX + 1.2, MC[1] - 4.8, 1.9], [MC[0] + 0.3, MC[1] + 0.3, 1.45], 32), "momdrive")
only("L15.1", [])
move("L15.1-0.05", "momcar", x=QX - 1.7, y=48.0, z=0.0, yaw=0.0)
move("L15.1", "momcar", dur=1.0, lin=True, x=QX - 1.7, y=14.0)
shot("L15.1", mv([QX - 8.0, G.POST_Y - 4.0, 1.5], [POSTX, G.POST_Y, 1.1], 34, [QX - 7.0, G.POST_Y - 3.6, 1.5], [POSTX, G.POST_Y, 1.1], 34), "postpass")
move("L15.2-0.05", "momcar", x=QX - 1.7, y=48.0, z=0.0, yaw=0.0)
move("L15.2", "momcar", dur=1.0, lin=True, x=QX - 1.7, y=14.0)
shot("L15.2", mv([QX - 8.4, G.POST_Y - 4.4, 1.2], [POSTX, G.POST_Y, 1.1], 34, [QX - 7.4, G.POST_Y - 4.0, 1.3], [POSTX, G.POST_Y, 1.1], 34), "postpass2")
# L16: the old photo
move("L16-0.05", "momcar", x=QX - 1.7, y=90.0)
sit("mom", "L16", False)
only("L16", [])
shot("L16", mv([RX - 3.4, RY - 0.6, 2.1], [RX - 3.4, RY + 3.4, 2.0], 40, [RX - 3.4, RY + 0.2, 2.05], [RX - 3.4, RY + 3.4, 2.0], 40), "photo")
shot("L16+0.7", mv([RX - 3.9, RY + 1.4, 2.0], [RX - 3.9, RY + 3.4, 2.0], 70, [RX - 3.9, RY + 2.1, 2.0], [RX - 3.9, RY + 3.4, 2.0], 70), "photomom")
# L17: two days
look("L17", "morn", 0.5)
cue("L17", "sit", who="me", on=True, z=0.7)
only("L17", ["me"])
put("me", "L17", [DRV[0], DRV[1], 0.0], 0, expr="asleep", head=[0, 12])
beat("me", "L17+0.5", expr="worried", head=[0, 0])
shot("L17", mv([QX + 2.6, -3.0, 1.9], [QX + 0.45, 0.45, 1.5], 46, [QX + 2.4, -2.4, 1.85], [QX + 0.45, 0.45, 1.5], 46), "wake")
odo("L17.1", 412, 1.0)
shot("L17.1", mv([QX + 1.4, -2.4, 1.7], [QX + 0.45, 0.45, 1.4], 52, [QX + 1.2, -1.9, 1.7], [QX + 0.45, 0.45, 1.4], 52), "odo412")
look("L17.2", "dusk", 0.8)
beat("me", "L17.2", expr="soft")
shot("L17.2", mv([QX + 3.8, -6.0, 1.7], [QX + 0.4, 0.0, 1.4], 36, [QX + 3.2, -5.0, 1.7], [QX + 0.4, 0.0, 1.4], 36), "sunsetdrive")

# ===================================================================== 04 the road goes (L18 to L20)
beat("me", "P01", expr="worried")
shot("P01", mv([QX + 1.6, -4.4, 1.7], [QX, -0.9, 1.55], 80, [QX + 1.2, -3.9, 1.7], [QX, -0.9, 1.55], 80), "mirrorclose")
beat("me", "L18", expr="worried", look=[-0.8, 0.5], head=[0, 0])
shot("L18", mv([QX + 2.1, -3.0, 1.9], [QX + 0.2, 0.5, 1.5], 50, [QX + 1.8, -2.5, 1.9], [QX + 0.2, 0.5, 1.5], 50), "eyesmirror")
cue("L18.1", "gone", v=1.0, dur=1.8)
beat("me", "L18.1", expr="scared", head=[40, 0], look=[0.5, 0.0])
shot("L18.1", mv([QX + 2.2, -2.8, 1.8], [QX + 0.45, 0.45, 1.5], 50, [QX + 1.9, -2.3, 1.8], [QX + 0.45, 0.45, 1.5], 50), "turnhead")
shot("L19", mv([QX + 0.45, 0.9, 1.7], [QX + 0.2, 30.0, 0.3], 30, [QX + 0.45, 1.1, 1.7], [QX + 0.2, 30.0, 0.4], 30), "backwin")
odo("L19+0.5", 412)
odo("L19+0.7", 388, 0.25)
odo("L19+0.95", 539, 0.25)
odo("L19+1.2", 412, 0.25)
beat("me", "L19+0.5", expr="terrified")
shot("L19+0.5", mv([QX + 1.4, -2.4, 1.7], [QX + 0.45, 0.45, 1.4], 52, [QX + 1.2, -1.9, 1.7], [QX + 0.45, 0.45, 1.4], 52), "odoflick")
beat("me", "L19.1", expr="scared", head=[0, 0])
acting["me"].append({"from": "L19.1", "to": "L19.1+0.7", "mouth": [0.0, 0.9]})
shot("L19.1", mv([QX + 1.5, -2.6, 1.72], [QX + 0.45, 0.45, 1.48], 58, [QX + 1.3, -2.1, 1.72], [QX + 0.45, 0.45, 1.48], 58), "faceopen")
shot("L20", mv([QX + 1.6, 9.0, 0.7], [QX, 26.0, 0.9], 28, [QX + 1.4, 11.0, 0.8], [QX, 26.0, 0.9], 28), "grasslow")
shot("L20.1", mv([QX + 3.2, 14.0, 0.6], [QX, 17.0, 0.2], 30, [QX + 2.6, 15.0, 0.5], [QX, 17.0, 0.2], 30), "roadend")

# ===================================================================== 05 the gate (L21 to L26)
sit("me", "L21", False)
cue("L21", "lane", v=1.0)
look("L21", "dusk")
only("L21", ["clem"])
move("L21", "mecar", x=0.0, y=-12.5, z=0.0, yaw=180.0)
move("L21", "gateleaf", yaw=0.0)
move("L21", "pc3", x=0.0, y=-7.85, z=1.6)
put("clem", "L21", [-0.5, -7.1, 0.0], 0, expr="smile", arms=[0, 80])
shot("L21", mv([0.5, -12.0, 1.75], [-0.3, -7.4, 1.55], 36, [0.3, -11.0, 1.75], [-0.3, -7.4, 1.55], 36), "gateclem")
only("L21.1", ["me", "clem"])
put("me", "L21.1", [0.4, -11.0, 0.0], 180, expr="worried")
go("me", "L21.1>", [1.3, -8.9, 0.0], expr="worried", arms=[0, 0])
shot("L21.1", mv([5.2, -14.0, 1.9], [0.7, -10.0, 1.3], 36, [4.8, -13.0, 1.9], [0.7, -9.8, 1.3], 36), "stumble")
put("clem", "L21.1", [-0.5, -7.1, 0.0], 0, expr="relieved" if False else "warm", arms=[0, 80])
put("me", "L22", [1.3, -8.9, 0.0], 180, expr="worried", arms=[60, 0])
acting["me"].append({"from": "L22", "to": "L22>", "mouth": [0.2, 0.6]})
shot("L22", fr(-0.5, -7.1, 1.85, 4.2, 54, dx=0.4), "clemclose")
shot("L22.1", mv([3.0, -4.4, 1.7], [1.4, -8.5, 1.4], 40, [2.6, -4.6, 1.7], [1.4, -8.5, 1.4], 40), "grippost")
# L23: the warning's backwards
beat("clem", "L23", head=[18, 0])
beat("clem", "L23+0.35", head=[-18, 0])
beat("clem", "L23+0.7", head=[16, 0])
beat("clem", "L23.1", head=[0, 0], expr="smirk")
shot("L23", fr(-0.5, -7.1, 1.85, 4.0, 52, dx=-0.4), "clemshake")
shot("L23.1", mv([0.3, -9.7, 1.8], [0.0, -7.85, 1.62], 64, [0.2, -9.0, 1.75], [0.0, -7.85, 1.62], 64), "peachpalm")
# L24: those who eat
only("L24", [])
move("L24", "pc3", z=-60.0)
shot("L24", mv([-1.0, 3.2, 2.2], [0.0, -45.0, 1.2], 26, [-0.6, 3.0, 2.15], [0.0, -45.0, 1.2], 26), "valley")
only("L24.1", ["b3", "b4"])
put("b3", "L24.1", [GX - 1.4, GY + 7.0, 3.8], 0, expr="grin", arms=[0, 150])
put("b4", "L24.1", [GX + 1.0, GY + 7.0, 3.8], 0, expr="grin", arms=[150, 0])
beat("b3", "L24.1+0.5", arms=[0, 120])
beat("b4", "L24.1+0.5", arms=[120, 0])
shot("L24.1", mv([GX - 3.0, GY - 12.0, 3.0], [GX - 0.2, GY + 7.0, 4.6], 34, [GX - 2.4, GY - 11.0, 3.2], [GX - 0.2, GY + 7.0, 4.6], 34), "roofwave")
# L25: the reveal picture
move("L25", "gateleaf", yaw=82.0)
move("L25", "pc3", x=0.2, y=-7.9, z=1.5)
only("L25", ["clem"])
put("clem", "L25", [0.2, -7.4, 0.0], 180, expr="warm", arms=[0, 80])
shot("L25", mv([1.6, -2.4, 1.75], [0.0, -9.6, 1.45], 34, [1.3, -2.8, 1.75], [0.0, -9.6, 1.45], 34), "reveal")
# L26: forgot you more
move("L26", "pc3", z=-60.0)
only("L26", [])
cue("L26", "sill", n=12.0)
shot("L26", mv([RX + 0.9, RY - 0.4, 1.7], [RX + 0.1, RY + 3.2, 1.1], 40, [RX + 0.4, RY + 0.4, 1.4], [RX + 0.1, RY + 3.2, 1.1], 40), "sillrow2")
odo("L26.1", 12)
odo("L26.1+0.3", 30, 0.2)
odo("L26.1+0.6", 90, 0.2)
odo("L26.1+0.9", 240, 0.2)
odo("L26.1+1.2", 412, 0.2)
shot("L26.1", mv([QX + 3.0, -6.0, 2.2], [QX, 16.0, 0.8], 30, [QX + 2.4, -3.0, 2.0], [QX, 16.0, 0.8], 30), "roadgone")

# ===================================================================== 06 the proof (L27 to L33)
look("L27", "day", 0.6)
move("L27", "mecar", x=CARX, y=CARY, z=0.0, yaw=0.0)
only("L27", ["carrier"])
sit("carrier", "L27", True, 0.62)
put("carrier", "L27", [BX, BY + 1.45, 0.0], 0, expr="grin")
move("L27", "pc4", x=BX + 0.45, y=BY + 0.9, z=1.1)
shot("L27", mv([BX + 1.8, BY - 4.6, 1.5], [BX, BY + 1.5, 1.1], 36, [BX + 1.4, BY - 4.0, 1.5], [BX, BY + 1.5, 1.1], 36), "bus")
sit("carrier", "L27.2", False)
move("L27.2", "pc4", z=-60.0)
put("carrier", "L27.2", [CX - 6.0, CY - 1.0, 0.0], 90, expr="grin")
go("carrier", "L27.2>", [CX + 4.0, CY - 1.0, 0.0], expr="grin")
move("L27.2-0.05", "city1", x=CX + 20.0, y=CY - 5.0, z=0.0, yaw=90.0)
move("L27.2", "city1", dur=2.2, lin=True, x=CX - 20.0)
shot("L27.2", mv([CX - 2.0, CY - 9.0, 1.8], [CX - 3.0, CY - 1.0, 1.3], 34, [CX + 1.0, CY - 8.6, 1.8], [CX + 0.0, CY - 1.0, 1.3], 34), "busstep")
look("L28", "noon", 0.5)
only("L28", ["carrier"])
put("carrier", "L28", [MX + 2.0, 1.7], 0, expr="grin", arms=[0, 150])
beat("carrier", "L28+0.4", arms=[0, 120])
shot("L28", fr(MX + 2.0, 1.7, 1.6, 4.2, 38, dx=-0.4), "lunch")
look("L29", "day", 0.6)
only("L29", ["b3", "b4"])
move("L29", "brocar", x=GX - 8.0, y=GY - 5.5, z=0.0, yaw=90.0)
put("b3", "L29", [GX - 8.0, GY - 4.0], 90, expr="grin", arms=[0, 70])
put("b4", "L29", [GX - 6.0, GY - 4.2], 0, expr="grin", arms=[70, 0])
move("L29", "gift0", x=GX - 7.0, y=GY - 4.6, z=1.2)
move("L29", "gift1", x=GX - 8.0, y=GY - 4.4, z=1.15)
shot("L29", mv([GX - 3.0, GY - 9.5, 1.8], [GX - 7.0, GY - 4.4, 1.3], 36, [GX - 3.6, GY - 8.8, 1.8], [GX - 7.0, GY - 4.4, 1.3], 36), "gifts")
only("L29.2", [])
move("L29.2", "gift0", z=-60.0)
move("L29.2", "gift1", z=-60.0)
move("L29.2-0.05", "brocar", x=QX - 1.7, y=95.0, z=0.0, yaw=0.0)
move("L29.2", "brocar", dur=1.3, lin=True, y=-40.0)
shot("L29.2", mv([QX + 6.0, 6.0, 1.6], [QX - 1.7, 6.0, 1.0], 34, [QX + 5.5, 4.0, 1.6], [QX - 1.7, 4.0, 1.0], 34), "carrolls")
move("L30-0.05", "brocar", x=GX - 32.0, y=GY - 5.0, z=0.0, yaw=90.0)
move("L30", "brocar", dur=1.0, x=GX - 9.0, y=GY - 5.0)
only("L30", [])
put("b3", "L30+0.9", [GX - 9.0, GY - 7.4], 0, expr="laugh", arms=[165, 165])
put("b4", "L30+0.9", [GX - 7.4, GY - 7.4], 0, expr="laugh", arms=[165, 165])
shot("L30", mv([GX - 6.0, GY - 13.0, 1.7], [GX - 9.0, GY - 5.5, 1.2], 34, [GX - 6.4, GY - 11.5, 1.7], [GX - 8.4, GY - 5.8, 1.3], 34), "gasback")
look("L31", "dusk", 0.6)
only("L31", ["clem", "me"])
move("L31", "brocar", z=-60.0)
put("clem", "L31", [4.4, 2.35, PZ], 0, expr="warm", arms=[0, 80])
put("me", "L31", [3.3, 0.8, 0.0], 180, expr="soft")
move("L31", "pc5", x=4.9, y=1.6, z=1.6)
shot("L31", mv([7.0, -2.4, 1.9], [4.4, 1.6, 1.6], 34, [6.3, -2.0, 1.9], [4.4, 1.6, 1.6], 34), "offer")
shot("L31.1", mv([5.2, -0.4, 1.8], [4.9, 1.6, 1.62], 66, [5.1, 0.4, 1.75], [4.9, 1.6, 1.62], 66), "peachgold")
look("L32", "day", 0.6)
move("L32", "pc5", z=-60.0)
only("L32", [])
shot("L32", mv([RX - 3.9, RY + 1.2, 2.0], [RX - 3.9, RY + 3.4, 2.0], 70, [RX - 3.9, RY + 2.0, 2.0], [RX - 3.9, RY + 3.4, 2.0], 70), "photomom2")
only("L32.1", ["mom"])
put("mom", "L32.1", [KX + 0.2, KY + 2.4], 0, expr="sad-smile", look=[0.7, 0.3], head=[28, 0])
shot("L32.1", fr(KX + 0.2, KY + 2.4, 1.6, 4.0, 44, dx=-0.4), "momwindow")
only("L33", [])
move("L33-0.05", "momcar", x=QX - 1.7, y=52.0, z=0.0, yaw=0.0)
move("L33", "momcar", dur=1.0, lin=True, y=14.0)
shot("L33", mv([QX - 8.0, G.POST_Y - 4.0, 1.5], [POSTX, G.POST_Y, 1.1], 34, [QX - 7.0, G.POST_Y - 3.6, 1.5], [POSTX, G.POST_Y, 1.1], 34), "postagain")
move("L33.1", "momcar", y=90.0)
shot("L33.1", mv([POSTX + 2.4, G.POST_Y - 3.0, 1.1], [POSTX - 6.0, G.POST_Y, 0.4], 32, [POSTX + 2.0, G.POST_Y - 2.4, 1.1], [POSTX - 6.0, G.POST_Y, 0.4], 32), "turnunseen")

# ===================================================================== 07 I eat it (L34 to L39)
look("L34", "dusk", 0.6)
only("L34", ["me", "clem"])
cue("L34", "rock", a=7.0)
put("me", "L34", [SWX - 0.6, SWY - 0.15, 0.0], 0, expr="smile", arms=[0, 125])
sit("me", "L34", True, 1.08)
ride("me", "L34", True)
put("clem", "L34", [SWX + 0.6, SWY - 0.15, 0.0], 0, expr="warm")
sit("clem", "L34", True, 1.08)
ride("clem", "L34", True)
move("L34", "pc5", x=SWX - 0.35, y=SWY - 0.7, z=1.95)
beat("me", "L34+0.6", expr="grin", arms=[0, 125])
acting["me"].append({"from": "L34+0.4", "to": "L34+1.0", "mouth": [0.0, 0.8]})
shot("L34", mv([SWX - 0.2, -0.2, 2.2], [SWX, SWY, 1.9], 36, [SWX - 0.1, 0.4, 2.1], [SWX, SWY, 1.9], 36), "swingbite")
cue("L34.1", "gold", v=1.0)
beat("clem", "L34.1", expr="laugh")
beat("me", "L34.1", expr="grin")
shot("L34.1", mv([SWX + 1.2, -0.4, 2.0], [SWX + 0.1, SWY, 1.9], 38, [SWX + 0.8, 0.1, 1.95], [SWX + 0.1, SWY, 1.9], 38), "swinglaugh")
move("L34.2", "pc5", z=-60.0)
shot("L34.2", mv([SWX + 0.8, 1.3, 3.1], [SWX + 1.3, SWY - 0.15, 3.3], 80, [SWX + 0.9, 1.9, 3.15], [SWX + 1.3, SWY - 0.15, 3.3], 80), "lorestroke")
beat("me", "L35", expr="squeeze", arms=[0, 0])
acting["me"].append({"from": "L35", "to": "L35>", "mouth": [0.1, 0.6]})
shot("L35", mv([SWX - 1.0, 0.5, 2.1], [SWX - 0.6, SWY, 1.9], 52, [SWX - 0.9, 1.0, 2.05], [SWX - 0.6, SWY, 1.9], 52), "chew")
# L36: twelve minutes
look("L36", "morn", 0.6)
cue("L36", "rock", a=0.0)
sit("me", "L36", True, 0.7)
ride("me", "L36", False)
ride("clem", "L36", False)
cue("L36", "gone", v=0.0)
cue("L36", "lane", v=0.0)
only("L36", ["me"])
odo("L36", 12)
put("me", "L36", [DRV[0], DRV[1], 0.0], 0, expr="delighted")
shot("L36", mv([QX + 3.6, -6.0, 1.8], [QX + 0.4, 0.2, 1.4], 36, [QX + 3.0, -5.0, 1.8], [QX + 0.4, 0.2, 1.4], 36), "morndrive")
move("L36.1", "mecar", x=CX + 1.2, y=CY + 0.5, z=0.0, yaw=0.0)
put("me", "L36.1", [CX + 1.65, CY + 0.95, 0.0], 0, expr="laugh")
shot("L36.1", mv([CX + 4.4, CY - 5.2, 1.9], [CX + 1.65, CY + 0.95, 1.5], 36, [CX + 3.6, CY - 4.4, 1.8], [CX + 1.65, CY + 0.95, 1.5], 36), "citycar")
# L37: Mom's peach
look("L37", "day", 0.5)
sit("me", "L37", False)
move("L37", "mecar", x=CARX, y=CARY, z=0.0)
only("L37", ["me"])
put("me", "L37", [KX + 2.4, KY + 2.4, 0.0], 0, expr="smile", arms=[0, 78])
move("L37", "pc6", x=KX + 2.9, y=KY + 1.75, z=1.14)
shot("L37", mv([KX + 2.2, KY - 2.0, 1.9], [KX + 2.6, KY + 1.9, 1.3], 38, [KX + 2.3, KY - 1.2, 1.85], [KX + 2.6, KY + 1.9, 1.3], 38), "setpeach")
only("L37.1", ["mom"])
put("mom", "L37.1", [KX + 1.7, KY + 2.4, 0.0], 0, expr="sad-smile", arms=[75, 0])
move("L37.1", "pc6", dur=0.8, x=KX + 1.2, y=KY + 1.75, z=1.14)
shot("L37.1", fr(KX + 1.7, KY + 2.4, 1.6, 3.8, 44, dx=0.3), "momtakes")
# L38: she found the turn
only("L38", [])
move("L37.1>", "pc6", z=-60.0)
move("L38-0.05", "momcar", x=QX - 1.7, y=62.0, z=0.0, yaw=0.0)
move("L38", "momcar", dur=1.2, lin=True, y=31.0)
move("L38+1.2", "momcar", dur=0.9, x=QX - 8.0, y=G.POST_Y, yaw=-90.0)
shot("L38", mv([QX - 8.0, G.POST_Y - 6.0, 1.6], [POSTX, G.POST_Y + 6.0, 1.0], 32, [QX - 7.0, G.POST_Y - 5.0, 1.6], [POSTX - 1.0, G.POST_Y + 3.0, 1.0], 32), "turnin")
move("L38.1-0.05", "gateleaf", yaw=82.0)
only("L38.1", ["clem", "mom"])
move("L38.1", "gateleaf", yaw=82.0)
put("clem", "L38.1", [0.0, 3.0, PZ], 0, expr="laugh")
go("clem", "L38.1+0.9", [-0.4, -7.3, 0.0], expr="laugh", run=True)
put("mom", "L38.1", [-0.4, -9.6, 0.0], 180, expr="smile")
go("mom", "L38.1+0.9", [-0.4, -8.7, 0.0], expr="smile")
beat("clem", "L38.2-0.4", arms=[90, 90], yaw=0, expr="laugh")
beat("mom", "L38.2-0.4", arms=[90, 90], yaw=180, expr="sad-smile")
shot("L38.1", mv([3.2, -3.6, 1.6], [0.0, -4.0, 0.6], 34, [3.0, -5.0, 1.6], [-0.2, -6.4, 1.0], 34), "runhug")
shot("L38.2", mv([4.2, -8.0, 1.65], [-0.4, -8.0, 1.5], 34, [3.6, -8.0, 1.65], [-0.4, -8.0, 1.5], 34), "hug")
only("L38.3", ["me"])
put("me", "L38.3", [4.4, 2.35, PZ], 0, expr="grin")
shot("L38.3", fr(4.4, 2.35, 1.75, 4.4, 38, dx=0.5), "megrin")
# L39: the rule, loop
look("L39", "dusk", 0.6)
cue("L39", "rock", a=6.0)
only("L39", ["me", "mom", "clem"])
put("mom", "L39", [SWX - 1.0, SWY - 0.15, 0.0], 0, expr="laugh")
put("me", "L39", [SWX, SWY - 0.15, 0.0], 0, expr="laugh")
put("clem", "L39", [SWX + 1.0, SWY - 0.15, 0.0], 0, expr="laugh")
for w_ in ("mom", "me", "clem"):
    sit(w_, "L39", True, 1.08)
    ride(w_, "L39", True)
move("L39", "bowl", x=SWX, y=SWY - 0.75, z=1.35)
move("L39", "pc7", x=SWX - 0.08, y=SWY - 0.75, z=1.5)
move("L39", "pc8", x=SWX + 0.1, y=SWY - 0.72, z=1.48)
shot("L39", mv([SWX, -0.6, 2.2], [SWX, SWY, 1.9], 34, [SWX, -0.1, 2.15], [SWX, SWY, 1.9], 34), "threeswing")
look("L39.1", "day", 0.5)
cue("L39.1", "rock", a=0.0)
for w_ in ("mom", "me", "clem"):
    ride(w_, "L39.1", False)
only("L39.1", [])
for o in ("bowl", "pc7", "pc8"):
    move("L39.1", o, z=-60.0)
move("L39.1", "keys", x=5.4)
move("L39.1", "gateleaf", yaw=0.0)
move("L39.1", "pc1", x=RAILP[0], y=RAILP[1], z=RAILP[2])
cue("L39.1", "gold", v=0.0)
shot("L39.1", mv([5.15, -0.3, 2.0], [5.2, 1.6, 1.6], 44, [5.2, 0.05, 1.97], [5.2, 1.6, 1.6], 44), "looppeach")

# ---------------------------------------------------------------------------------------------- finish
for k_ in acting.values():
    remap_all(k_)
remap_all(cues)
# pad the numbers: remap offsets "L19+0.5" etc. stay as written
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
    {"at": "L01.2", "kind": "latch", "db": -10},
    {"at": "L34+0.5", "kind": "click", "db": -22},
]
music = {
    "root": 55, "mode": "major", "bpm": 100, "seed": 102,
    "sections": [
        {"at": 0, "voices": ["musicbox", "pad"], "energy": 0.4, "root": 55, "mode": "major"},
        {"at": "L09", "voices": ["musicbox", "drone"], "energy": 0.35, "root": 55, "mode": "major"},
        {"at": "L18", "voices": ["drone", "choir"], "energy": 0.3, "root": 55, "mode": "minor"},
        {"at": "L23", "voices": ["pad", "drone"], "energy": 0.35, "root": 52, "mode": "minor"},
        {"at": "L31", "voices": ["pad", "musicbox"], "energy": 0.45, "root": 55, "mode": "major"},
        {"at": "L34", "voices": ["musicbox", "pad", "pulse"], "energy": 0.6, "root": 55, "mode": "major"},
    ],
}
sound = {
    "floor": "grass", "steps_db": -26,
    "ambience": [{"kind": "crickets", "from": "L21", "to": "L25", "lufs": -44}],
    "sfx": sfx,
    "music_drops": [{"from": "P01", "to": "P01>"}],
    "rev": REV,
}
remap_all(sfx)
remap_all(music["sections"])
remap_all(sound["music_drops"])
remap_all(sound["ambience"])
polish = {"reveal": [remap("L25"), remap("L19")], "twist": remap("L23"),
          "quiet": [[remap("L37"), remap("L39")]],
          "hold": [names["reveal"], names["lorestroke"], names["peachclose"]]}
story = {
    "slug": "ep102-aunt-peaches",
    "title": "One Bite Here And You STAY 🍑",
    "made_for_kids": False,
    "premise": ("Everyone warns visitors never to eat a peach in my aunt's valley or every road out leads back to her "
                "gate. I have visited for twelve summers and never taken a bite, and every summer the drive there gets "
                "longer, until this year it takes two days and the road behind my car is gone."),
    "twist": ("The warning is backwards: the valley's road only remembers the people who have eaten there, so by never "
              "eating I was being forgotten a little more each year. I eat one, the drive home takes twelve minutes, "
              "and my mom, who stopped eating them when she moved away, finds the turn again."),
    "world": ("A green valley of peach orchards under a blue sky: a white farmhouse with a porch swing and a wooden "
              "gate, a gas station with a striped awning, a row of mailboxes, a winding two-lane ridge road."),
    "voice": {"voice": "am_adam", "tempo": 1.03, "rate": 1.45},
    "key_color": "#ffa86b",
    "gap": 0.15,
    "tail": 0.25,
    "fade_in": False,
    "fade_out": False,
    "rev": REV,
    "look": {"style": "closer", "fog": "#d6ecff", "fog_density": 0.003, "fog_start": 40.0, "sky": "#7ec8ff",
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
    "asr_forgive": ["i've"],
}
OUT.write_text(json.dumps(story, indent=1, ensure_ascii=False) + "\n")
print("wrote", OUT, f"({len(shots)} shots, {len(cues)} cues)")
