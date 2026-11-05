"""Writes ../story.json for ep112 "hide and seek" (script.md, 2026-11-04). Run: python stories/ep112-hide-and-seek/generator/make_story.py

The words are in lines.json. Places are in ../layout.py (shared with set.py). A character facing -y has yaw 0, +x 90,
+y 180, -x -90, and faces the direction (sin yaw, -cos yaw). Shots use the script's chunk numbers (a shot at "L07.2"
starts on chunk 2 of line L07); captions are split to two or three words and the references are remapped.
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
REV = 6
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
idx = next(i for i, l in enumerate(lines) if l["id"] == "L13")
lines.insert(idx, {"id": "P01", "pause": 0.4, "chunks": [["", ""]]})


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


def orb(tx, ty, tz, az, d, lens, dz=0.0, push=0.12, dtx=0.0):
    """A camera d metres from the target, on the side the heading az (degrees) faces, easing in by `push`."""
    a = math.radians(az)
    sx, sy = math.sin(a), -math.cos(a)
    p0 = [tx + sx * d, ty + sy * d, tz + dz]
    p1 = [tx + sx * d * (1 - push) + dtx, ty + sy * d * (1 - push), tz + dz * 0.95]
    return mv(p0, [tx, ty, tz], lens, p1, [tx, ty, tz], lens)


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
    "me": person("#dca97c", "#ffd23f", "#3d6fb5", "#f4f4f2", hair="cap", hair_c="#15100c", hat="ballcap", hat_c="#e8493a",
                 sleeves="short", brow_w=1.9),
    "grandma": person("#f0c8a8", "#9b6bd6", "#5a4a7a", "#e8e0d0", hair="bun", hair_c="#d6d6e2", extras=["glasses"],
                      extra_c="#2a2a2a", eyes="lashes", brow_w=1.0, height=0.93),
    "glenn": person("#e2a982", "#18b3a8", "#c8b080", "#6a4a2a", hair="cap", hair_c="#4a2e1a", sleeves="short", brow_w=1.9),
    "c1": person("#c89870", "#ff6f5e", "#3a4a6a", "#3a2a1a", hair="long", hair_c="#1c1210", eyes="lashes", sleeves="short",
                 brow_w=1.9),
    "c2": person("#f0c8a8", "#4fb86a", "#7a6a52", "#2a2a2a", hair="spiky", hair_c="#a0521c", sleeves="short"),
    "c3": person("#8a5a3c", "#ffa13d", "#2f3b5a", "#2a2a2a", hair="bun", hair_c="#1a1210", eyes="lashes", sleeves="short",
                 brow_w=1.9),
}
acting = {n: [{"at": 0, "hidden": True, "pos": [0, 0]}] for n in cast}
last = {n: [0, 0] for n in cast}
visible = set()
cues = []
SH = []


def put(who, at, pos, yaw=None, **kw):
    p = list(pos)
    acting[who].append({"at": at, "pos": list(last[who])})
    k = {"at": at, "pos": p, "blend": 0.0, "hidden": False, "lean": 0.0, "head": [0, 0], "arms": [0, 0], "side": [0, 0]}
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


def move(at, obj, dur=0.0, **kw):
    cue(at, "mv", obj=obj, dur=dur, **kw)


def sit(who, at, on=True, z=G.SEAT):
    cue(at, "sit", who=who, on=on, z=z)


TAX, TAY = G.TA
TBX, TBY = G.TB
FARA, FARB = TAY + G.FAR, TBY + G.FAR            # the far benches' y
GL = (-0.55, FARA)                                # where Mr. Glenn sits
GR = (0.85, FARA)                                 # where Grandma sits
SHX, SHY = G.SHED
GRS = (SHX - 0.7, SHY - 1.7)                      # Grandma counting at the shed (face to camera)
BOWL = (TBX + 0.8, TBY)
MEB = (TBX + 0.9, FARB)                           # where I sit at table B
ME2 = (TAX - 1.8, TAY + 0.3)                      # where I stand to say it
PHOTO_AT = (2.2, 1.7)                             # Grandma showing the photo
PHOTO_W = (PHOTO_AT[0] + 0.47, PHOTO_AT[1] - 0.49, 1.14)   # about where the photo lies, in the world
GY = -120.0
BN = (-4.4, 6.2)                                  # the bench Glenn sits on in the shed shot
BNY = -88.0

# ===================================================================== 01 the hook (L01 to L03)
cue(0, "clock", y=31.0, d=204.0)
cue(0, "eye", v=0.0)
cue(0, "photo", v=0.0)
cue(0, "gst", v=1.0)
cue(0, "mst", v=0.0)
move(0, "shedd", yaw=0.0)
move(0, "fork", z=-60.0)
move(0, "bowl", z=-60.0)
move(0, "fst", z=-60.0)
move(0, "bench", vis=0.0)
put("grandma", 0, [GRS[0], GRS[1]], 0, expr="shut", arms=[0, 150])
shot(0, orb(GRS[0], GRS[1], 1.38, 0, 3.0, 40, push=0.14), "grancount")
only("L01.2", ["grandma", "c1", "c2", "c3"])
put("c1", "L01.2", [-3.7, 1.4], 15, expr="smile")
put("c2", "L01.2", [-9.0, 2.6], 0, expr="grin")
put("c3", "L01.2", [-4.8, 1.4], -15, expr="smile")
beat("c1", "L01.2+0.3", expr="laugh")
beat("c3", "L01.2+0.3", expr="laugh")
go("c1", "L01.3-0.02", [-0.5, 6.5], run=True)
go("c3", "L01.3-0.02", [-8.0, 6.0], run=True)
shot("L01.2", mv([-4.25, -2.9, 1.45], [-4.25, 1.4, 1.2], 24, [-4.25, -2.5, 1.45], [-4.25, 1.4, 1.2], 24), "scatter")
only("L01.3", ["grandma"])
put("grandma", "L01.3", [-7.0, 6.7], 25, expr="worried", arms=[0, 0], head=[-35, 0])
move("L01.3", "shedd", dur=0.5, yaw=38.0)
shot("L01.3", orb(-6.6, 7.0, 1.2, -20, 4.2, 26, dz=0.2), "shedajar")

# L02: the old photo on Grandma's palm
cue("L02", "photo", v=1.0)
only("L02", ["grandma"])
put("grandma", "L02", [PHOTO_AT[0], PHOTO_AT[1]], 0, expr="smile", arms=[0, 62], head=[0, 14])
shot("L02", orb(PHOTO_W[0], PHOTO_W[1], PHOTO_W[2], -15, 1.9, 36, dz=1.0), "palm1")
beat("grandma", "L02.2", expr="laugh", arms=[0, 66], head=[0, 10])
shot("L02.2", orb(PHOTO_AT[0] - 0.05, PHOTO_AT[1], 1.4, 12, 2.9, 40), "granface")
shot("L03", orb(PHOTO_W[0], PHOTO_W[1], PHOTO_W[2], 0, 1.45, 50, dz=0.9, push=0.08), "photogap")

# ===================================================================== 02 the game at work (L04 to L12)
cue("L04", "photo", v=0.0)
only("L04", ["grandma"])
sit("grandma", "L04", True)
put("grandma", "L04", GR, 0, expr="wide", arms=[0, 70])
beat("grandma", "L04+0.3", arms=[0, 62])
beat("grandma", "L04+0.6", arms=[0, 72])
beat("grandma", "L04+0.9", arms=[0, 62])
shot("L04", orb(GR[0], GR[1], 1.2, 0, 3.4, 38, dz=0.15), "grantable")
beat("grandma", "L04.2", arms=[0, 72], expr="angry")
beat("grandma", "L04.2+0.3", arms=[0, 62])
beat("grandma", "L04.2+0.6", arms=[0, 72])
shot("L04.2", orb(GR[0] + 0.1, GR[1] - 0.2, 1.2, -40, 3.2, 34, dz=0.15), "tap")
# L05: the reunion today
only("L05", ["grandma", "c1", "c2", "c3"])
sit("c1", "L05", True)
sit("c3", "L05", True)
sit("c2", "L05", True)
put("grandma", "L05", GR, 0, expr="smile")
put("c2", "L05", [GL[0], FARA], 0, expr="smile")
put("c1", "L05", [TBX - 0.6, FARB], 0, expr="laugh")
put("c3", "L05", [TBX + 0.6, FARB], 0, expr="smile")
shot("L05", orb(0.15, FARA, 1.2, 0, 4.6, 26, dz=0.4, push=0.1), "reunion")
cue("L05.1", "clock", y=31.0, d=205.0)
cue("L05.1", "pulse")
beat("c1", "L05.1", head=[30, 0])
beat("c3", "L05.1", head=[-30, 0])
shot("L05.1", orb(TBX, FARB, 1.3, 25, 5.2, 30, dz=0.2), "tick")
# L06: under the porch, behind the shed
only("L06", ["c1", "c3"])
sit("c1", "L06", False)
sit("c3", "L06", False)
px, py = G.PORCH
put("c1", "L06", [px - 3.0, py - 2.0], 160, expr="worried", lean=6.0, head=[0, 8])
put("c3", "L06", [px - 1.9, py - 2.0], 200, expr="worried", lean=6.0, head=[0, 8])
beat("c1", "L06+0.5", lean=9.0, head=[-6, 12])
shot("L06", mv([px - 5.0, py + 0.9, 1.25], [px - 2.45, py - 2.0, 1.2], 28, [px - 4.8, py + 0.7, 1.25], [px - 2.45, py - 2.0, 1.2], 28), "porch")
only("L06.1+0.3", ["me"])
put("me", "L06.1+0.3", [-4.6, 10.9], 100, expr="worried", head=[-20, 8])
beat("me", "L06.1+0.7", head=[18, 4], expr="worried")
shot("L06.1+0.3", mv([-2.2, 12.6, 1.6], [-5.7, 10.4, 1.4], 26, [-2.4, 12.4, 1.6], [-5.7, 10.4, 1.4], 26), "behindshed")
# L07: Mr. Glenn at the fence
FX, FY = G.GLENN_FENCE
only("L07", ["glenn"])
put("glenn", "L07", [FX, FY], 0, expr="smile", arms=[70, 70])
beat("glenn", "L07+0.5", head=[-12, 0])
shot("L07", orb(FX, FY, 1.45, 0, 3.0, 40, push=0.12), "glennface")
beat("glenn", "L07.1", head=[-22, 0], arms=[70, 70], expr="smile")
beat("glenn", "L07.1+0.4", head=[22, 0])
beat("glenn", "L07.2", head=[0, 0], arms=[70, 70], expr="smile")
shot("L07.1", orb(FX, FY, 1.45, -38, 3.5, 34, dz=0.0), "glennscan")
# L08: Nice guy, big mustache, always sits facing the shed
only("L08", ["glenn"])
sit("glenn", "L08", True)
put("glenn", "L08", GL, GY, expr="smile")
shot("L08", orb(GL[0], GL[1], 1.32, GY, 3.0, 40, push=0.12), "glennstache")
move("L08.2-0.05", "bench", vis=1.0)
put("glenn", "L08.2", list(BN), BNY, expr="smile")
shot("L08.2", mv([-7.0, 3.9, 1.5], [-5.1, 6.5, 1.5], 22, [-6.8, 4.0, 1.5], [-5.1, 6.5, 1.5], 22), "glennshed")
move("L09-0.1", "bench", vis=0.0)
# L09: the potato salad
move("L09-0.05", "bowl", x=BOWL[0], y=BOWL[1] - 0.55, z=1.1)
only("L09", ["glenn"])
sit("glenn", "L09", False)
put("glenn", "L09", [BOWL[0], BOWL[1] - 1.1], 180, expr="smile", arms=[75, 75])
move("L09+0.15", "bowl", dur=0.45, x=BOWL[0], y=BOWL[1], z=0.815)
beat("glenn", "L09+0.55", arms=[0, 0])
shot("L09", mv([BOWL[0] + 0.3, BOWL[1] + 3.2, 1.9], [BOWL[0], BOWL[1] - 1.0, 1.2], 34, [BOWL[0] + 0.2, BOWL[1] + 2.8, 1.9], [BOWL[0], BOWL[1] - 1.0, 1.2], 34), "bringsalad")
shot("L09.1+0.35", orb(BOWL[0], BOWL[1] - 0.4, 1.2, 180, 3.3, 36, dz=0.15, push=0.1), "bowlclose")
# L10: I finally try it
only("L10", ["me", "c1", "c3"])
sit("me", "L10", True)
sit("c1", "L10", True)
sit("c3", "L10", True)
put("c1", "L10", [TBX - 0.9, FARB], 0, expr="smile")
put("c3", "L10", [TBX, FARB], 0, expr="smile")
put("me", "L10", list(MEB), 0, expr="worried", head=[0, 14])
beat("me", "L10+0.3", head=[0, 4])
beat("me", "L10.1", head=[0, 12], expr="worried")
acting["me"].append({"from": "L10.1", "to": "L10.1+0.8", "mouth": [0.0, 0.9]})
shot("L10", orb(MEB[0], MEB[1], 1.25, 0, 3.4, 38, dz=0.1), "metry")
# L11: it's Uncle Pete's famous salad
beat("me", "L11", expr="smirk", arms=[0, 0], head=[0, 8])
beat("me", "L11.1", expr="wide", head=[0, 0])
shot("L11", orb(MEB[0], MEB[1], 1.3, 14, 2.8, 42, dz=0.05, push=0.16), "mechew")
# L12: nobody else has the recipe
only("L12", ["c1", "c3"])
sit("c1", "L12", False)
sit("c3", "L12", False)
put("c1", "L12", [TBX - 0.5, TBY - 1.6], 0, expr="worried")
acting["c1"].append({"at": "L12+0.2", "pos": [TBX - 0.5, TBY - 1.6], "side": [55, 55], "expr": "worried"})
put("c3", "L12", [TBX + 0.5, TBY - 1.6], 0, expr="worried")
acting["c3"].append({"at": "L12.1", "pos": [TBX + 0.5, TBY - 1.6], "side": [55, 55], "expr": "worried"})
shot("L12", orb(TBX, TBY - 1.6, 1.4, 0, 5.2, 38), "cousinshrug")

# ===================================================================== 03 the reveal (P01, L13 to L19)
# the 0.4 s hole: me looking from the bowl to Mr. Glenn
only("P01", ["me", "glenn"])
sit("me", "P01", True)
sit("glenn", "P01", True)
put("me", "P01", list(MEB), 0, expr="worried", head=[0, 14])
put("glenn", "P01", GL, GY, expr="smile")
acting["me"].append({"at": "P01+0.15", "pos": list(MEB), "head": [34, 0]})
shot("P01", orb(MEB[0], MEB[1], 1.25, -8, 3.2, 40), "melook")
# L13: so I walked over
sit("me", "L13", False)
put("me", "L13", list(MEB), 90, expr="smirk")
go("me", "L14", list(ME2), expr="smirk")
beat("glenn", "L13+0.5", expr="worried", yaw=-65.0)
shot("L13", mv([-3.4, 0.4, 1.7], [-3.2, 4.4, 1.3], 28, [-2.6, 1.0, 1.65], [-1.3, 4.7, 1.35], 28), "walkover")
# L14: Found you, Uncle Pete
acting["me"].append({"at": "L14", "pos": list(ME2), "yaw": 55.0, "expr": "smirk"})
acting["me"].append({"at": "L14+0.25", "pos": list(ME2), "yaw": 55.0, "arms": [0, 85], "expr": "smirk"})
beat("glenn", "L14", expr="worried", yaw=-35.0)
shot("L14", orb(-1.3, 4.6, 1.35, -4, 4.6, 30, push=0.08), "point")
cue("L14.2", "eye", v=1.0)
cue("L14.2", "pulse")
beat("glenn", "L14.2", expr="wide", yaw=-12.0)
shot("L14.2", orb(GL[0], GL[1], 1.4, -12, 2.7, 44, push=0.1), "caughtface")
# L15: the mustache falls into the salad (one held shot)
beat("glenn", "L15", expr="wide", yaw=-8.0)
beat("glenn", "L15.1", expr="laugh")
cue("L15.1", "gst", v=0.0)
move("L15.1-0.05", "fst", x=GL[0], y=GL[1] - 0.3, z=1.5)
move("L15.1", "fst", dur=0.35, x=GL[0] + 0.02, y=GL[1] - 0.5, z=1.05)
move("L15.1+0.35", "fst", dur=0.3, x=GL[0] + 0.02, y=TAY + 0.3, z=0.99)
shot("L15", mv([GL[0] - 0.3, 1.5, 1.3], [GL[0], 4.7, 1.15], 30, [GL[0] - 0.2, 2.0, 1.3], [GL[0], 4.7, 1.15], 30), "reveal")
# L16: Grandma drops her fork
only("L16", ["grandma", "glenn"])
cue("L16", "gst", v=0.0)
sit("grandma", "L16", True)
put("grandma", "L16", GR, 0, expr="wide", arms=[0, 75])
beat("glenn", "L16", expr="smile", yaw=0.0)
move("L16", "fork", x=GR[0] + 0.1, y=TAY + 0.1, z=1.15, yaw=90.0)
move("L16+0.55", "fork", dur=0.2, x=GR[0] + 0.1, y=TAY + 0.15, z=0.835, yaw=90.0)
beat("grandma", "L16+0.55", arms=[0, 20])
shot("L16", mv([GR[0] - 0.1, 1.9, 1.3], [GR[0] + 0.05, 4.5, 1.08], 28, [GR[0] - 0.1, 2.3, 1.3], [GR[0] + 0.05, 4.5, 1.08], 28), "grandfork")
move("L16.1+1.0", "fork", z=-60.0)
# L17: thirty-one years, he lives next door
only("L17", ["grandma"])
put("grandma", "L17", GR, 0, expr="laugh", arms=[0, 0])
sit("grandma", "L17", True)
shot("L17", orb(GR[0], GR[1], 1.3, 0, 2.7, 42, dz=0.1), "grandlaugh")
only("L17.1", ["grandma"])
shot("L17.1", mv([0.95, 1.2, 1.2], [0.85, 9.0, 1.75], 30, [0.95, 1.7, 1.25], [0.85, 9.0, 1.75], 30), "nhouse")
# L18: nobody ever looks at the guy helping you look
only("L18", ["glenn"])
sit("glenn", "L18", True)
put("glenn", "L18", GL, 0, expr="smile")
shot("L18", orb(GL[0], GL[1], 1.35, 0, 3.0, 40, push=0.1), "petegrin")
beat("glenn", "L18.1", expr="laugh", side=[45, 45], head=[0, 0])
shot("L18.2", mv([-3.3, 7.3, 0.9], [-1.0, 4.95, 0.85], 24, [-3.1, 7.05, 0.9], [-1.0, 4.95, 0.85], 24), "tally")
beat("glenn", "L18.3", expr="smile", side=[55, 55])
shot("L18.3", orb(GL[0], GL[1], 1.2, 12, 2.8, 36, dz=0.1), "peteshrug")
# L19: so now Pete's it
cue("L19", "clock", y=0.0, d=0.0)
cue("L19", "eye", v=2.0)
cue("L19", "pulse")
sit("glenn", "L19", False)
only("L19", ["glenn"])
put("glenn", "L19", [GRS[0] + 0.2, GRS[1]], 0, expr="shut", arms=[0, 150])
shot("L19", orb(GRS[0] + 0.2, GRS[1], 1.45, 0, 3.2, 40, push=0.14), "petecount")
only("L19.1", ["glenn", "c1", "c2", "c3"])
beat("glenn", "L19.1", arms=[0, 0], expr="shut")
put("c1", "L19.1", [-4.0, 5.4], 90, expr="grin")
put("c2", "L19.1", [-5.0, 6.4], 180, expr="grin")
put("c3", "L19.1", [-6.6, 5.0], -90, expr="grin")
go("c1", "L20", [4.5, 7.6], run=True)
go("c2", "L20", [-4.0, 11.5], run=True)
go("c3", "L20", [-11.0, 2.5], run=True)
shot("L19.1", orb(GRS[0] + 0.2, GRS[1], 1.4, 35, 4.6, 30, dz=0.1, push=0.1), "scatter2")
# L20: and I'm hiding
only("L20", ["me"])
put("me", "L20", [3.0, 11.4], 15, expr="laugh", arms=[0, 0])
go("me", "L20+0.9", [3.4, 10.8], expr="laugh")
shot("L20", orb(3.1, 11.2, 1.4, 15, 3.4, 40, push=0.1), "sneak")
shot("L20+0.55", orb(3.3, 10.9, 1.4, 5, 2.5, 46, push=0.08), "sneak2")
# L21: see you at next year's reunion
only("L21", ["me"])
put("me", "L21", [SHX + 2.0, SHY + 2.0], 66, expr="smirk")
shot("L21", mv([SHX + 5.6, SHY + 0.8, 1.55], [SHX + 1.2, SHY + 1.8, 1.45], 32, [SHX + 5.2, SHY + 1.0, 1.55], [SHX + 1.2, SHY + 1.8, 1.45], 32), "behindshed2")
cue("L21.2", "mst", v=1.0)
beat("me", "L21.2", expr="smirk", arms=[0, 150], head=[0, 0])
shot("L21.2", orb(SHX + 2.0, SHY + 2.0, 1.5, 66, 2.4, 44), "mestache")
cue("L21.3", "photo", v=0.0)
only("L21.3+0.7", ["grandma"])
sit("grandma", "L21.3+0.7", False)
put("grandma", "L21.3+0.7", [GRS[0], GRS[1]], 0, expr="shut", arms=[0, 150])
shot("L21.3+0.7", orb(GRS[0], GRS[1], 1.38, 0, 3.0, 40, push=0.14), "grancount2")

# ---------------------------------------------------------------------------------------------- finish
for k_ in acting.values():
    remap_all(k_)
remap_all(cues)
# fewer, longer cuts (cuts_per_10s): drop these shots; "fwd" ones extend the shot before, "back" ones let the next shot start early
DROP_FWD = {"sneak2", "tick", "glennscan", "grandlaugh", "tap", "granface"}
DROP_BACK = {"petecount", "melook"}
_sh, _carry = [], None
for _e in SH:
    if _e[5] in DROP_FWD:
        continue
    if _e[5] in DROP_BACK:
        _carry = _e[0]
        continue
    if _carry is not None:
        _e = (_carry,) + _e[1:]
        _carry = None
    _sh.append(_e)
SH = _sh
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
    {"at": "L14.2", "kind": "sting", "db": -14},
    {"at": "L15.1+0.6", "kind": "thud", "db": -22},
    {"at": "L01.3+0.55", "kind": "thud", "db": -24},
]
music = {
    "root": 48, "mode": "major", "bpm": 126, "seed": 112,
    "sections": [
        {"at": 0, "voices": ["pulse", "pad"], "energy": 0.45, "root": 48, "mode": "major"},
        {"at": "L10", "voices": ["pad", "drone"], "energy": 0.3, "root": 48, "mode": "major"},
        {"at": "L14", "voices": ["piano", "pulse", "pad"], "energy": 0.6, "root": 48, "mode": "major"},
        {"at": "L16", "voices": ["pulse", "piano", "pad"], "energy": 0.55, "root": 48, "mode": "major"},
    ],
}
sound = {
    "floor": "grass", "steps_db": -26,
    "ambience": [{"kind": "wind", "from": 0, "to": "end", "lufs": -46}],
    "sfx": sfx,
    "music_drops": [{"from": "P01", "to": "P01>"}],
    "rev": REV,
}
remap_all(sfx)
remap_all(music["sections"])
remap_all(sound["music_drops"])
remap_all(sound["ambience"])
polish = {"reveal": [remap("L15.1"), remap("L14.2")],
          "hold": [names[n_] for n_ in ("reveal", "tally", "photogap", "palm1", "grantable", "glennface", "grandfork", "reunion", "walkover", "sneak")]}
story = {
    "slug": "ep112-hide-and-seek",
    "title": "Our Family Game Never ENDED 🫣",
    "made_for_kids": False,
    "premise": ("My family's game of hide-and-seek started thirty-one years ago and my Uncle Pete has never been found, so "
                "at every reunion Grandma and the cousins keep looking, with the help of the nice neighbor, Mr. Glenn."),
    "twist": ("Mr. Glenn is Uncle Pete in a mustache that is a little too big: he has hidden in plain sight next door for "
              "thirty-one years, helping us look for himself, until I taste his famous potato salad and say his name. "
              "Now he is it, and I am the one hiding."),
    "world": ("A bright green back yard on a summer afternoon: red-checked picnic tables, string lights, a sagging gray "
              "shed, a white fence to the neighbor's tidy yellow house, and Grandma's porch."),
    "voice": {"voice": "am_adam", "tempo": 1.03, "rate": 1.45},
    "key_color": "#e84a4a",
    "gap": 0.15,
    "tail": 0.25,
    "fade_in": False,
    "fade_out": False,
    "rev": REV,
    "look": {"style": "closer", "fog": "#d6ecff", "fog_density": 0.003, "fog_start": 40.0, "sky": "#7ec8ff",
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
    "set_moves": [names["shedajar"], names["reveal"], names["grandfork"], names["bringsalad"], names["bowlclose"]],
    "asr_forgive": ["i've"],
}
OUT.write_text(json.dumps(story, indent=1, ensure_ascii=False) + "\n")
if __import__("os").environ.get("NAMES"):
    print({v: k for k, v in names.items()})
print("wrote", OUT, f"({len(shots)} shots, {len(cues)} cues)")
