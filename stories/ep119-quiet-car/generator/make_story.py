"""Writes ../story.json for ep119 "quiet car" (script.md, 2026-11-05). Run: python stories/ep119-quiet-car/generator/make_story.py

The words are in lines.json. Places are in ../layout.py (shared with set.py). A character facing -y has yaw 0, +x 90,
+y 180, -x -90. Time references use the script's chunk numbers; captions are split to two or three words and the
references are remapped.
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
REV = 18
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
# the music drops: 0.6 s before L19, 0.5 s before L46
for before, pid, dur in (("L19", "P01", 0.6), ("L46", "P02", 0.5), ("L48", "P03", 0.45)):
    idx = next(i for i, l in enumerate(lines) if l["id"] == before)
    lines.insert(idx, {"id": pid, "pause": dur, "chunks": [["", ""]]})


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
    # me: a gray wool coat over a mustard sweater (its collar), round black glasses
    "me": person("#dca97c", "#8e939c", "#3a3f4a", "#2a2a30", hair="cap", hair_c="#5a3d26", collar="#e0a32a",
                 extras=["coat"], extra_c="#15151a", zip_c="#6b7078", brow_w=1.6,
                 body_width=0.88),
    # Teddy: curly red hair, freckled, an orange vest over a blue shirt (blue collar and sleeves)
    "teddy": person("#f0c8a0", "#ff7a2e", "#2f4a8a", "#e8e0d0", hair="mop", hair_c="#c8461e", collar="#3f6fd0",
                    brow_w=1.6, body_width=0.88),
    "beard": person("#e2b088", "#8a6a48", "#4a4036", "#3a2a1a", hair="cap", hair_c="#c4c7ce", pattern="plaid",
                    pattern_c="#5a4630", hat="ballcap", hat_c="#7a5230", brow_w=1.4),
    "wife": person("#f0c8a0", "#2f9a62", "#e8e0d0", "#6a4a32", hair="bun", hair_c="#f2f2f2", eyes="lashes",
                   extras=["coat"], brow_w=1.2),
    "conductor": person("#d3a07a", "#22306a", "#22306a", "#15151a", hair="cap", hair_c="#8d9096", hat="ballcap",
                        hat_c="#22306a", collar="#ffffff", extras=["tie"], extra_c="#e0a32a", brow_w=1.4),
    "c1": person("#b98456", "#2fa8a0", "#4a4036", "#2a2a2a", hair="buzz", hair_c="#1a1410", sleeves="short"),
    "c2": person("#f0c8a0", "#8a5ab0", "#2a2a38", "#d8d0c8", hair="long", hair_c="#7a4a2c", eyes="lashes"),
}
acting = {n: [{"at": 0, "hidden": n != "me", "pos": list(G.ME) if n == "me" else [0, 0]}] for n in cast}
last = {n: (list(G.ME) if n == "me" else [0, 0]) for n in cast}
visible = set()
cues = []
SH = []


def put(who, at, pos, yaw=None, **kw):
    p = list(pos)
    acting[who].append({"at": at, "pos": list(last[who])})
    k = {"at": at, "pos": p, "blend": 0.0, "hidden": False, "lean": 0}
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


def shot(at, camera, name, step=1, follow=None):
    SH.append((at, camera, step, follow, name))


def K(T, az, d, lens, el=3.0, off=0.0, up=0.0):
    d = d * 1.3
    if up:
        T = (T[0], T[1], T[2] - up * 24.0 / lens * d)     # aim lower: the subject rides up in the frame (above a caption)
    a, e = math.radians(az), math.radians(el)
    pos = [T[0] + d * math.cos(a) * math.cos(e), T[1] + d * math.sin(a) * math.cos(e), T[2] + d * math.sin(e)]
    tgt = list(T)
    if off:
        sh = off * (9 / 16 * 24 / lens * d)
        rx, ry = -math.sin(a), math.cos(a)
        pos[0] -= rx * sh
        pos[1] -= ry * sh
        tgt[0] -= rx * sh
        tgt[1] -= ry * sh
    return [[0, [round(v, 3) for v in pos], [round(v, 3) for v in tgt], lens]]


def K2(T0, az0, d0, T1, az1, d1, lens, el=3.0, lens1=None, off=0.0, up=0.0):
    a = K(T0, az0, d0, lens, el, off, up)[0]
    b = K(T1, az1, d1, lens1 or lens, el, off, up)[0]
    return [a, [1, b[1], b[2], b[3]]]


def P(pos, tgt, lens):
    return [[0, list(pos), list(tgt), lens]]


def P2(p0, t0, p1, t1, lens, lens1=None):
    return [[0, list(p0), list(t0), lens], [1, list(p1), list(t1), lens1 or lens]]


# ---------------------------------------------------------------------------------------------- places
def AIS(d, lens, cx=0.0, z=1.55):
    """A camera in the aisle, d m in front of me where I stand (facing +y), looking back at my face: no seat back
    between us."""
    return [[0, [round(cx, 3), round(G.row_y(3) + d, 3), z], [0.0, G.row_y(3), 1.55], lens]]



ry = G.row_y
MEX, MEY = G.ME
TEX, TEY = G.TED
MEH = (MEX + 0.1, MEY + 0.17, 1.42)   # my head, seated (it sits forward of the hip along my facing)
TEH = (TEX - 0.1, TEY + 0.17, 1.42)
S9X, S9Y = G.SEAT9
D0, D1 = G.DOOR
DY = (D0 + D1) / 2
SIT = G.HIP
HALF_ = G.HALF


def sit(who, at, on=True):
    cue(at, "sit", who=who, on=on, z=SIT)


def seat_me(at, expr="neutral", **kw):
    put("me", at, [MEX, MEY], 150, expr=expr, arms=[35, 35], **kw)
    sit("me", at)


def seat_ted(at, expr="smile", **kw):
    put("teddy", at, [TEX, TEY], 210, expr=expr, arms=[35, 35], **kw)
    sit("teddy", at)


def env(at, **kw):
    cue(at, "env", **kw)


def move(at, v):
    cue(at, "move", v=float(v))


# ------------------------------------------------------------------------------------------------- 01 the rule
cue(0, "count", n=1512)
cue(0, "door", u=0.6)
cue(0, "move", v=1.0)
cue(0, "look", id="day")
# S01a: my face close, lips shut, the empty seats behind me
seat_me(0, "neutral")
shot(0, K(MEH, 78, 3.0, 50, 4, 0.05, up=0.13), "face1")
# S01b: the sliding door closes, the hush glyph on it
only("L01.1", ["me"])
env("L01.1", plat=1.0)
move("L01.1", 0)
cue("L01.1", "door", u=0.6)
cue("L01.1+0.1", "door", u=0.0, dur=0.8)
shot("L01.1", P([-1.5, 0.35, 1.5], [HALF_, DY, 1.3], 30), "doorclose")
# S02: my face, eyes sliding to the empty seats
env("L02", plat=0.0)
move("L02", 1)
beat("me", "L02", expr="worried", look=[0.0, 0.0])
beat("me", "L02.1", expr="worried", look=[0.8, 0.0], head=[25, 0])
shot("L02", K(MEH, 78, 2.5, 50, 3, 0.05, up=0.13), "face2")
# S03a: the empty car from the end door; S03b: the train sliding along
beat("me", "L02.1+0.3", expr="worried", look=[0.0, 0.0], head=[0, 0])
only("L03", [])
shot("L03", P([0.0, 0.45, 1.45], [0.0, 14.0, 1.3], 24), "emptycar")
shot("L03.1", P2([-9.0, 21.0, 5.8], [-2.2, 14.0, 1.4], [-9.0, 16.0, 5.8], [-2.2, 14.0, 1.4], 15), "exterior")
# S04: seat nine, a flat cap on it; the sneeze
shot("L04", K((S9X + 0.2, S9Y - 0.5, 1.25), 245, 2.0, 45, 8), "cap")
shot("L04.2", K((S9X + 0.2, S9Y - 0.5, 1.15), 205, 3.3, 40, 12), "seat9")
# S05: his wife sets the lunch bag on seat nine, on a flat palm
cue("L05", "lunch", v=1.0)
cue("L05", "lift", u=1.0)
cue("L05.2", "lift", u=0.0, dur=0.7)
only("L05", ["wife"])
put("wife", "L05", [0.0, S9Y - 0.1], 90, expr="warm", arms=[70, 70])
beat("wife", "L05.2", expr="smile", arms=[60, 60], head=[0, 8])
shot("L05", K((0.0, S9Y - 0.1, 1.5), 2, 2.4, 32, 6, 0.05), "wife")
shot("L05.2", K((0.45, S9Y - 0.1, 0.95), 5, 2.5, 34, 6), "wife2")
# S06: that evening the bag is crumbs; my face
only("L06", [])
cue("L06", "lunch", v=2.0)
shot("L06", K((S9X, S9Y, 0.55), 215, 1.6, 40, 40), "crumbs")
only("L06.1", ["me"])
seat_me("L06.1", "worried")
shot("L06.1", K(MEH, 78, 2.6, 50, 3, 0.05, up=0.13), "face3")
# S07: two commuters step the long way round the open door
only("L07", ["c1", "c2"])
cue("L07", "lunch", v=0.0)
env("L07", plat=1.0)
move("L07", 0)
cue("L07", "door", u=1.0)
put("c1", "L07", [3.3, 6.5], 0, expr="polite")
go("c1", "L07+0.5", [3.3, 3.4])
go("c1", "L07+0.9", [5.0, 1.5])
go("c1", "L07>", [3.3, -2.0])
put("c2", "L07.1", [3.5, 7.0], 0, expr="neutral")
go("c2", "L07.1+0.5", [3.5, 3.4])
go("c2", "L07.1+0.9", [5.2, 1.4])
go("c2", "L07.2>", [3.5, -2.5])
shot("L07", P2([9.0, -3.2, 1.6], [3.9, 3.6, 1.2], [8.8, -2.4, 1.6], [3.9, 2.6, 1.2], 22), "commuters")
shot("L07.2", P([9.0, -3.0, 1.6], [4.3, 0.2, 1.2], 22), "commuters2")
# S08: I step into the quiet car (door open), face to camera
only("L08", ["me"])
cue("L08", "sit", who="me", on=False, z=SIT)
put("me", "L08", [2.2, DY], -90, expr="neutral")
go("me", "L08+0.6", [0.3, DY])
shot("L08", P([-1.6, 1.3, 1.55], [1.2, DY, 1.4], 36), "enter")
# S09: in my seat, morning light; the stone door frame, held
env("L09", plat=0.0)
move("L09", 1)
cue("L09", "door", u=0.0)
seat_me("L09", "neutral")
shot("L09", K(MEH, 100, 3.2, 40, 4, 0.06), "inseat")
only("L09.1", [])
shot("L09.1", P2([-0.9, 4.2, 1.5], [HALF_, D1 + 0.6, 1.3], [-0.9, 4.0, 1.5], [HALF_, D1 + 0.6, 1.3], 36), "stone")
# S10: my face, close, neutral
only("L10", ["me"])
seat_me("L10", "neutral")
shot("L10", K(MEH, 78, 2.4, 55, 3, 0.05, up=0.13), "face4")
# S11: Teddy at a party; me beside him
PX, PY = G.PARTY
only("L11", ["teddy", "me"])
cue("L11", "sit", who="me", on=False, z=SIT)
put("teddy", "L11", [PX - 0.9, PY + 2.0], 0, expr="laugh", arms=[60, 20])
beat("teddy", "L11+0.6", expr="laugh", arms=[20, 80])
beat("teddy", "L11+1.2", expr="smile", arms=[80, 20])
put("me", "L11", [PX + 0.9, PY + 2.0], 0, expr="smile")
shot("L11", K((PX - 0.9, PY + 2.0, 1.55), 270, 3.2, 40, 2, 0.0), "party1")
shot("L11.2", K((PX - 0.5, PY + 2.0, 1.55), 265, 3.3, 30, 2, 0.0), "party2")
# S12: Teddy's smile; a smiley in the fog on a bus window
only("L12", ["teddy"])
put("teddy", "L12", [PX, PY + 2.0], 0, expr="smile", arms=[0, 40])
shot("L12", K((PX, PY + 2.0, 1.55), 268, 2.8, 48, 2, 0.0), "tedsmile")
shot("L12.1", P([G.BUS[0], G.BUS[1] - 0.9, 1.75], [G.BUS[0], G.BUS[1] + 1.94, 1.75], 20), "bussmile")
# S13: a spring morning through the train window
only("L13", [])
cue("L13", "season", s=0.0)
shot("L13", P2([0.2, 14.5, 1.9], [-6.0, 14.8, 1.2], [0.2, 14.5, 1.9], [-6.0, 15.1, 1.1], 30), "spring")
# S14: Teddy jumps in as the doors close
only("L14", ["teddy"])
cue("L14", "door", u=1.0)
cue("L14+0.2", "door", u=0.0, dur=0.8)
put("teddy", "L14", [4.6, DY], -90, expr="smile")
go("teddy", "L14+0.9", [0.4, DY])
acting["teddy"][-1]["sfx"] = "door"
shot("L14", P([-1.6, 1.0, 1.5], [1.6, DY, 1.4], 36), "jump")
# S15: Teddy slides into the seat across the aisle
put("teddy", "L15", [0.25, ry(2)], 0, expr="smile")
go("teddy", "L15+0.9", [0.25, TEY - 0.2])
acting["teddy"][-1]["yaw"] = 180
put("teddy", "L15>", [TEX, TEY], 210, expr="smile", arms=[35, 35])
sit("teddy", "L15>")
only("L15", ["teddy", "me"])
seat_me("L15", "neutral")
shot("L15", K2((0.0, ry(2.5), 1.4), 100, 3.8, (0.4, ry(3.9), 1.4), 115, 3.2, 38), "slideseat")
# S16: Teddy lights up at me, then says it
beat("teddy", "L16", expr="smile", head=[-20, 0])
shot("L16", K(TEH, 118, 2.9, 50, 3, 0.05), "tedlit")
beat("teddy", "L16.2", expr="smile", head=[-20, 0])
acting["teddy"].append({"from": "L16.2", "to": "L16.2>", "mouth": [0.3, 0.9], "flap": True})
shot("L16.2", K(TEH, 125, 2.3, 55, 3, 0.05), "tedmouth")
# S17: I freeze (Teddy out of the frame: hidden for this one shot, back at L18)
only("L17", ["me"])
beat("me", "L17", expr="scared", head=[0, 0])
shot("L17", K(MEH, 78, 2.6, 55, 3, 0.05, up=0.13), "freeze")
# S18: two-shot, Teddy's smile fading, the tag at 1513
cue("L16", "count", n=1513)
seat_ted("L18", "neutral", head=[-20, 0])
beat("me", "L18", expr="scared")
shot("L18", P2([0.05, 20.6, 2.0], [0.0, 11.2, 1.4], [0.05, 19.4, 1.95], [0.0, 11.2, 1.4], 44), "twoshot")
# the drop: the train goes into the tunnel
env("P01", tunnel=1.0)
cue("P01", "look", id="tunnel")
shot("P01", P2([-0.3, 15.2, 1.35], [0.8, 12.4, 1.75], [-0.3, 14.6, 1.35], [0.8, 12.4, 1.75], 26), "tunnelin")
# the count climbs a morning at a time: 1,560 by L32, 1,600 by L42
for at_, n_, d_ in (("L22", 1522, 1.0), ("L25", 1534, 0.8), ("L28", 1546, 0.8), ("L31", 1560, 0.8), ("L34", 1572, 0.8),
                    ("L36", 1583, 0.8), ("L39", 1592, 0.8), ("L41", 1600, 0.8), ("L43", 1608, 0.8)):
    cue(at_, "count", n=n_, dur=d_)
# S19: the car in the tunnel
shot("L19", P2([0.0, 15.2, 1.75], [-0.5, 10.3, 1.4], [0.0, 14.4, 1.75], [-0.5, 10.3, 1.45], 26), "tunnel")
# S20: out of the tunnel, Teddy's seat empty
env("L20-0.35", tunnel=0.0)
cue("L20", "look", id="day")
only("L20", ["me"])
cue("L20", "cup", v=1.0)
cue("L20", "warm1", a=1.0, dur=0.6)
shot("L20", K((TEX, TEY, 0.9), 290, 2.9, 40, 22), "emptyseat")
# S21: close, his coffee still steaming
shot("L21", K((TEX + 0.1, TEY + 0.1, 0.8), 215, 1.7, 40, 22, 0.0), "coffee")
# S22: my face, the empty seat across the aisle
beat("me", "L22", expr="wide")
shot("L22", K2(MEH, 60, 3.0, MEH, 70, 2.5, 50, 3, 0.1), "face5")
# S23: my palm flat on his warm seat
cue("L23", "sit", who="me", on=False, z=SIT)
only("L23", [])
cue("L23", "hand", v=1.0)
cue("L24", "hand", v=0.0)
shot("L23", P2([TEX - 0.1, TEY + 1.0, 1.4], [TEX - 0.1, TEY - 0.02, 0.55], [TEX - 0.1, TEY + 0.85, 1.25], [TEX - 0.1, TEY - 0.02, 0.55], 30), "palm")
# S24: close, his window, a small patch of fog
only("L24", [])
cue("L24", "patch", a=1.0, dur=0.6)
shot("L24", P([-0.2, TEY, 1.6], [HALF_, TEY, 1.5], 22), "patchfog")
# S25: the empty car, a heat shimmer over every seat
cue("L25", "warm", a=1.0, dur=0.6)
shot("L25", P2([0.0, 5.0, 1.9], [0.0, 13.0, 1.0], [0.0, 5.8, 1.9], [0.0, 13.0, 1.0], 26), "shimmer")
# S26: a smiley draws itself in the fog from the inside
cue("L26", "smiley", p=0.0)
cue("L26+0.4", "smiley", p=6.0, dur=1.3)
shot("L26", P2([-0.2, TEY, 1.6], [HALF_, TEY, 1.5], [0.0, TEY, 1.58], [HALF_, TEY, 1.5], 22, 26), "smiley")
# S27: my small smile
beat("me", "L27", expr="smile")
put("me", "L27", [MEX, MEY], 150, expr="smile", arms=[35, 35])
sit("me", "L27")
shot("L27", K(MEH, 78, 2.6, 52, 3, 0.05, up=0.13), "face6")
# S28: I set a second coffee on his seat with a flat palm
cue("L28", "cup2", v=1.0)
cue("L28", "sit", who="me", on=False, z=SIT)
put("me", "L28", [0.05, TEY - 1.1], 0, expr="smile", side=[0, 80])
beat("me", "L28.1", expr="smile", side=[0, 82], head=[-10, 0])
cue("L28.2", "cup2", v=0.0)
shot("L28", K((0.05, TEY - 1.1, 1.45), 270, 3.0, 40, 3), "cupset")
# S29: the cup is always empty; the car at the end of the line
cue("L29", "cup", v=2.0)
shot("L29", K((TEX + 0.1, TEY + 0.1, 0.75), 200, 1.5, 45, 35), "emptycup")
# S30: my face lit by my phone
seat_me("L30", "worried")
shot("L30", K(MEH, 78, 2.5, 55, 3, 0.05, up=0.13), "face7")
# S31: his phone buzzing on an empty seat
cue("L31", "phone", v=2.0)
only("L31", [])
shot("L31", K((TEX - 0.2, TEY - 0.1, 0.55), 240, 1.2, 45, 20), "buzz")
# S32: a hat on the rack, nobody under it
only("L32", [])
cue("L32.1", "hat", v=1.0)
cue("L32", "phone", v=0.0)
shot("L32", P([0.9, ry(7.4), 1.2], [-1.9, ry(8) + 0.0, 2.1], 34), "rack")
shot("L32.3", P2([0.2, ry(7.5), 2.0], [-1.7, ry(8), 2.1], [0.2, ry(7.5), 1.2], [-1.7, ry(8), 0.7], 34), "rackdown")
# S33: a cake with candles on seat twelve, then out
cue("L33", "cake", v=1.0)
shot("L33", P([-0.3, ry(6) + 1.0, 1.3], [-1.6, ry(6) + 0.05, 0.7], 36), "cake")
cue("L33.3", "cake", v=2.0)
shot("L33.3", P2([-0.3, ry(6) + 1.0, 1.3], [-1.6, ry(6) + 0.05, 0.7], [-0.4, ry(6) + 0.9, 1.2], [-1.6, ry(6) + 0.05, 0.8], 36), "cakeout")
# S34: the maze in my puzzle book, half traced in green; my face
cue("L34", "maze", p=0.0)
cue("L34.1", "maze", p=3.0, dur=1.0)
shot("L34", K((-1.62, MEY + 0.05, 0.58), 120, 1.1, 40, 62), "maze")
seat_me("L34.3", "wide")
shot("L34.3", K(MEH, 78, 2.6, 52, 3, 0.05, up=0.13), "face8")
beat("me", "L34.3+0.5", expr="smile")
# S35, S36: my face, tight and scared
beat("me", "L35", expr="worried")
shot("L35", K(MEH, 78, 2.3, 55, 2, 0.05, up=0.13), "face9")
beat("me", "L36", expr="scared")
shot("L36", K(MEH, 78, 2.15, 56, 2, -0.04, up=0.13), "face10")
# S37: Teddy's empty seat, the smiley in the fog
cue("L37", "smiley", p=6.0)
shot("L37", P2([-0.3, TEY - 1.0, 1.6], [HALF_, TEY + 0.05, 1.5], [-0.3, TEY - 0.7, 1.58], [HALF_, TEY + 0.05, 1.5], 24), "emptyseat2")
# S38: me alone in the car, small
beat("me", "L38", expr="worried")
shot("L38", P2([0.55, TEY + 0.2, 2.3], [-0.8, MEY - 0.1, 0.95], [0.5, TEY - 0.2, 2.2], [-0.8, MEY - 0.1, 0.95], 24), "alone")
# S39: the empty car from the end door
only("L39", [])
shot("L39", P2([0.0, 0.5, 1.5], [0.0, 14.0, 1.3], [0.0, 1.3, 1.5], [0.0, 14.0, 1.3], 24), "emptycar2")
# S40: the conductor walks past our car's door window without stopping
only("L40", ["conductor"])
put("conductor", "L40", [0.0, -0.55], 180, expr="neutral", head=[60, 0])
beat("conductor", "L40+0.9", expr="neutral", head=[-60, 0])
shot("L40", P([0.0, 2.6, 1.62], [0.0, -0.55, 1.62], 50), "conductor1")
only("L40.3", [])
shot("L40.3", K2((0.0, ry(4.4), 1.45), 280, 2.3, (0.0, ry(4.4), 1.45), 262, 2.0, 40, 4), "tickets")
# S41: Teddy's empty seat, the steaming coffee, my face soft behind it
seat_me("L41", "worried")
cue("L41", "cup", v=1.0)
shot("L41", P([TEX + 0.45, TEY - 0.9, 0.78], [MEX, MEY, 1.4], 40), "cupface")
# S42: me at my bathroom mirror at night, mouthing a word
BX, BY = G.BATH
only("L42", ["me"])
cue("L42", "sit", who="me", on=False, z=SIT)
cue("L42", "look", id="night")
env("L42", plat=0.0)
put("me", "L42", [BX, BY + 1.3], 0, expr="worried")
acting["me"].append({"from": "L42.1", "to": "L42.2>", "mouth": [0.0, 0.7], "flap": True})
shot("L42", K((BX, BY + 1.3, 1.45), 270, 2.7, 46, 2), "mirror")
# S43: back in my seat, morning, glum, mouth shut
cue("L43", "look", id="day")
seat_me("L43", "worried")
shot("L43", K(MEH, 78, 2.5, 52, 3, 0.05, up=0.13), "face11")
# S44: seasons through the window; my face beside his fogged window
cue("L44", "season", s=1.0)
cue("L44", "count", n=1700, dur=1.6)
shot("L44", P2([0.2, 14.5, 1.9], [-6.0, 14.8, 1.2], [0.2, 14.5, 1.9], [-6.0, 15.1, 1.1], 30), "summer")
cue("L44.1", "season", s=2.0)
shot("L44.1", P2([0.2, 14.5, 1.9], [-6.0, 15.1, 1.1], [0.2, 14.5, 1.9], [-6.0, 15.4, 1.2], 30), "fall")
shot("L44.2", K(MEH, 78, 2.7, 46, 4, -0.05, up=0.13), "face12")
# S45: determined, mouth opening, the tag at 1724
cue("L45", "count", n=1724, dur=0.4)
beat("me", "L45", expr="neutral", head=[0, 0])
acting["me"].append({"from": "L45.2", "to": "L45.2>", "mouth": [0.1, 0.8]})
shot("L45", K(MEH, 78, 2.2, 55, 2, 0.05, up=0.13), "face13")
# the drop: the still car
shot("P02", P([0.2, ry(2.4), 1.6], [0.0, ry(6), 1.3], 28), "stillcar")
# S46: every window fogs, front to back
cue("L46", "fog", p=0.0)
cue("L46+0.1", "fog", p=1.0, dur=1.2)
shot("L46", P([MEX + 0.05, MEY + 0.5, 1.5], [0.0, ry(8), 1.4], 24), "fogsweep")
# S47: the reveal: me standing in the aisle, mouth open, every window fogged
cue("L47", "sit", who="me", on=False, z=SIT)
put("me", "L47", [0.15, MEY], 218, expr="wide", head=[0, 0])
acting["me"].append({"from": "L47", "to": "L47.1>", "mouth": [0.2, 0.9]})
shot("L47", P2([-1.35, MEY + 1.8, 1.45], [0.5, MEY - 0.6, 1.5], [-1.35, MEY + 1.5, 1.45], [0.5, MEY - 0.6, 1.5], 17), "reveal")
# S48: handprints press into the fog
cue("L48", "fogmax", m=0.36, dur=0.6)
cue("L52+0.5", "fogmax", m=0.88, dur=1.2)
cue("L48", "prints", p=1.0, dur=0.2)
shot("L48", P([-0.5, ry(6) + 0.15, 1.6], [HALF_, ry(6) + 0.15, 1.5], 24), "prints1")
cue("L48.1", "prints", p=4.0, dur=0.5)
shot("L48.1", P([0.5, ry(5) + 0.15, 1.6], [-HALF_, ry(5) + 0.15, 1.5], 24), "prints2")
# S49: my face, stunned
put("me", "L49", [0.0, MEY], 180, expr="wide")
shot("L49", AIS(3.3, 38, 0.12), "face14")
# S50: every seat cushion dipped
cue("L50", "dip", u=0.0)
cue("L50+0.1", "dip", u=1.0, dur=0.7)
cue("L50", "prints", p=8.0)
shot("L50", P2([0.0, 5.0, 1.8], [0.0, 13.0, 0.8], [0.0, 6.0, 1.8], [0.0, 13.0, 0.8], 26), "dipped")
# S51: fogged windows, one after another
shot("L51", P2([-0.9, ry(3.6), 1.6], [HALF_ - 0.04, ry(4.6), 1.5], [-0.9, ry(3.9), 1.6], [HALF_ - 0.04, ry(4.9), 1.5], 46), "fogpan")
# S52: Teddy's seat, the smiley in the fog
shot("L52", P2([-0.3, TEY + 1.0, 1.6], [HALF_, TEY - 0.05, 1.5], [-0.3, TEY + 0.7, 1.58], [HALF_, TEY - 0.05, 1.5], 24), "emptyseat3")
# S53: my face, uneasy
put("me", "L53", [0.0, MEY], 180, expr="worried")
shot("L53", AIS(3.1, 38, -0.12), "face15")
# S54: me alone in the aisle
shot("L54", K2((0.0, ry(4.8), 1.2), 95, 4.8, (0.0, ry(4.8), 1.2), 100, 4.2, 28, 6), "aisle")
# S55: the fogged windows from low, as if leaning in; my face in the foreground
shot("L55", P2([0.35, MEY + 2.4, 0.95], [-0.2, MEY - 3.0, 1.95], [0.3, MEY + 2.1, 0.95], [-0.15, MEY - 3.0, 2.0], 26), "leaning")
# S56: the tag, close, and me looking at it
put("me", "L56", [0.0, MEY], 180, expr="worried", head=[-30, -10])
shot("L56", AIS(3.2, 38, 0.1), "face16")
# S57: determined, a small nod
beat("me", "L57", expr="neutral", head=[0, 0])
beat("me", "L57.1", expr="neutral", head=[0, 12])
shot("L57", AIS(3.0, 38, -0.1), "face17")
# S58: I stand tall in the aisle
put("me", "L58", [0.0, MEY], 180, expr="neutral", head=[0, 0])
shot("L58", P2([0.1, MEY + 4.2, 1.45], [0.0, MEY, 1.45], [-0.05, MEY + 3.2, 1.55], [0.0, MEY, 1.55], 32), "standup")
# S59: I say good morning to everybody; the tag stops, its glyph opens
cue("L59", "glyph", u=0.0)
cue("L59+0.2", "glyph", u=1.0, dur=0.5)
beat("me", "L59", expr="laugh")
acting["me"].append({"from": "L59", "to": "L59.2>", "mouth": [0.8, 0.8]})
shot("L59", AIS(3.0, 40, 0.0), "say")
# S60: for one second, nothing
beat("me", "L60", expr="wide")
shot("L60", P2([0.0, MEY + 3.6, 1.5], [0.0, MEY - 2.5, 1.35], [0.0, MEY + 3.3, 1.5], [0.0, MEY - 2.5, 1.35], 22), "silent")
# S61: the fog swells once; my hair lifted by the breath of it
cue("L61", "swell", s=0.0)
cue("L61+0.1", "swell", s=1.0, dur=0.6)
cue("L61+0.8", "swell", s=0.0, dur=0.6)
shot("L61", P2([0.3, MEY + 2.6, 1.1], [-0.1, MEY - 3.0, 1.85], [0.25, MEY + 2.3, 1.1], [-0.1, MEY - 3.0, 1.85], 22), "swell")
beat("me", "L61.1", expr="wide", head=[0, -6])
shot("L61.1", AIS(3.0, 40, 0.1), "face18")
# S62: the windows clear one by one
cue("L62", "clear", q=0.0)
cue("L62+0.1", "clear", q=1.0, dur=3.4)
shot("L62", P2([0.0, ry(5.2), 1.7], [-0.45 * HALF_, ry(1.6), 1.4], [0.0, ry(4.8), 1.7], [0.45 * HALF_, ry(1.2), 1.4], 28), "clearing")
# S63: my face, laughing
beat("me", "L63", expr="laugh")
move("L63>", 0)
shot("L63", AIS(3.2, 38, -0.1), "face19")
# S64: the doors slide open onto the sunny platform
env("L64", plat=1.0)
move("L64", 0)
cue("L64", "fog", p=0.0)
cue("L64", "door", u=0.0)
cue("L64+0.2", "door", u=1.0, dur=1.0)
put("me", "L64", [-0.4, DY], 90, expr="smile")
shot("L64", P([-1.5, 1.5, 1.55], [3.6, DY, 1.4], 30), "doorsopen")
# S65: long sunny shadows of many people stepping out; only me in the door
cue("L65", "shadows", t0=0.0)
put("me", "L65", [HALF_ - 0.3, DY + 0.4], 90, expr="smile")
shot("L65", P([8.0, DY - 3.4, 1.7], [2.8, DY, 0.9], 30), "shadows")
# S66: the bearded man steps off with his lunch
only("L66", ["beard"])
put("beard", "L66", [2.4, DY - 0.4], 90, expr="smile", arms=[0, 72])
go("beard", "L66+1.6", [3.2, DY - 0.4])
shot("L66", K((2.9, DY - 0.4, 1.4), 28, 3.0, 40, 9), "beard")
# S67: Teddy steps out into the sun
only("L67", ["teddy", "me"])
put("teddy", "L67", [2.2, DY], 90, expr="laugh")
go("teddy", "L67+1.4", [4.2, DY])
put("me", "L67", [1.0, DY], 90, expr="smile")
shot("L67", K((3.0, DY, 1.55), 35, 3.2, 42, 4), "teddyout")
# S68: Teddy hugs me so hard my glasses fog
put("me", "L68", [5.0, DY + 0.3], 120, expr="laugh")
put("teddy", "L68", [4.2, DY - 0.4], 60, expr="laugh", arms=[85, 85])
cue("L68.1", "glass", a=1.0, s=0.0, dur=0.6)
shot("L68", K((4.6, DY, 1.5), 10, 3.2, 40, 4), "hug")
# S69: a smiley drawn on my fogged glasses
put("teddy", "L69", [6.2, DY + 0.05], 0, expr="laugh", side=[0, 80], head=[-35, 0])
put("me", "L69", [5.0, DY + 0.1], 0, expr="smile")
cue("L69.1", "glass", a=1.0, s=0.0)
cue("L69.1+0.2", "glass", a=1.0, s=6.0, dur=1.0)
shot("L69", P([5.6, DY - 2.9, 1.58], [5.6, DY + 0.1, 1.55], 22), "glasses")
# S70: Teddy talks with his hands
put("teddy", "L70", [4.2, DY - 0.5], 0, expr="laugh", arms=[60, 20])
beat("teddy", "L70+0.5", expr="laugh", arms=[20, 80])
beat("teddy", "L70+1.0", expr="smile", arms=[85, 25])
beat("teddy", "L70+1.2", expr="laugh", arms=[30, 70])
put("me", "L70", [5.2, DY - 0.5], 0, expr="smile")
cue("L70", "glass", a=0.0, s=0.0, dur=0.5)
shot("L70", K((4.6, DY - 0.5, 1.55), 262, 3.4, 40, 2), "talk")
# S71: Teddy and me in the busy bright car; the quiet car's door behind us
LY = G.LOUD_Y0 + G.CAR_L
env("L71", plat=0.0)
move("L71", 1)
cue("L71", "door", u=0.0)
cue("L71", "glass", a=0.0, s=0.0)
only("L71", ["teddy", "me", "c1"])
put("teddy", "L71", [-0.5, LY - 3.5], 0, expr="laugh", arms=[70, 20])
put("me", "L71", [0.7, LY - 3.5], 0, expr="smile")
put("c1", "L71", [-0.1, LY - 9.5], 180, expr="smile")
beat("teddy", "L71+0.7", expr="laugh", arms=[20, 75])
shot("L71", K((0.1, LY - 3.5, 1.55), 262 - 172, 3.4, 40, 2), "loudcar")
# S72: the conductor at the quiet car's door, face to camera
only("L72", ["conductor"])
put("conductor", "L72", [0.0, 0.5], 0, expr="neutral", head=[0, 0])
shot("L72", P([0.0, -3.4, 1.6], [0.0, 0.5, 1.55], 40), "cond2")
# S73: his finger to his lips
beat("conductor", "L73", expr="neutral")
cue("L73", "cfing", v=1.0)
shot("L73", P([0.0, -2.6, 1.6], [0.1, 0.5, 1.55], 52), "cond3")
# S74: a wink, then my face back in my seat (S01a's framing): the loop
beat("conductor", "L74", expr="polite")
cue("L74", "wink", v=1.0)
shot("L74", P([0.0, -2.8, 1.6], [0.0, 0.5, 1.58], 55), "cond4")
cue("L74>", "wink", v=0.0)
cue("L74>", "cfing", v=0.0)
only("L74>", ["me"])
seat_me("L74>", "neutral")
shot("L74>", K(MEH, 78, 2.7, 50, 4, 0.05), "loop")

# ---------------------------------------------------------------------------------------------- finish
cue(0, "fog", p=0.0)
cue(0, "clear", q=0.0)
cue(0, "swell", s=0.0)
cue(0, "patch", a=0.0)
cue(0, "smiley", p=0.0)
cue(0, "prints", p=0.0)
cue(0, "warm", a=0.0)
cue(0, "dip", u=0.0)
cue(0, "cup", v=0.0)
cue(0, "phone", v=0.0)
cue(0, "hat", v=0.0)
cue(0, "cake", v=0.0)
cue(0, "lunch", v=0.0)
cue(0, "lift", u=0.0)
cue(0, "maze", p=0.0)
cue(0, "season", s=0.0)
cue(0, "glyph", u=0.0)
cue(0, "glass", a=0.0, s=0.0)
cue(0, "hand", v=0.0)
cue(0, "cfing", v=0.0)
cue(0, "wink", v=0.0)
cue(0, "fogmax", m=0.88)
cue(0, "env", tunnel=0.0, plat=0.0)
for k_ in acting.values():
    remap_all(k_)
remap_all(cues)
# cues and keys landing exactly on a cut can miss the cut's first drawing: apply them a frame early (frames.py pops)
EARLY = {remap(x) for x in ("L09", "L48", "L48.1", "L71")}
for k_ in list(acting.values()) + [cues]:
    for it in k_:
        if it.get("at") in EARLY and it["at"] == it.get("at"):
            it["at"] = f"{it['at']}-0.2" if ("blend" in it or "pos" not in it) else f"{it['at']}-0.22"
cues.sort(key=lambda c: (0 if c["at"] == 0 else 1))
shots, names = [], {}
for i, (at, camera, step, follow, nm) in enumerate(SH):
    s = {"id": f"S{i + 1:02d}", "cam": camera, "step": step}
    if i:
        s["at"] = remap(at)
    if follow:
        s["follow"] = follow
    shots.append(s)
    names[nm] = s["id"]

sfx = [
    {"at": "L01.1+0.4", "kind": "thud", "db": -8},
    {"at": "L01.1+0.4", "kind": "bell", "db": -17, "dur": 0.9},
    {"at": "L16.2", "kind": "thud", "db": -16},
    {"at": "P01", "kind": "whoosh", "db": -14, "dur": 1.4, "keep": True},
    {"at": "P02", "kind": "whoosh", "db": -20, "dur": 1.1, "keep": True},
    {"at": "L74+0.2", "kind": "bell", "db": -16, "dur": 0.9},
]
music = {
    "root": 57, "mode": "minor", "bpm": 88, "seed": 119,
    "sections": [
        {"at": 0, "voices": ["piano", "pulse", "pad"], "energy": 0.32},
        {"at": "L19", "voices": ["pulse", "drone"], "energy": 0.4},
        {"at": "L35", "voices": ["pulse", "drone", "pad"], "energy": 0.5},
        {"at": "L46", "voices": ["drone", "pad"], "energy": 0.62},
        {"at": "L56", "voices": ["pad"], "energy": 0.45},
        {"at": "L61", "voices": ["choir", "pad", "piano"], "energy": 0.7, "mode": "major"},
        {"at": "L62", "voices": ["piano", "pulse", "pad"], "energy": 0.62, "mode": "major"},
    ],
}
sound = {
    "floor": "metal", "steps_db": -26,
    "ambience": [{"kind": "hum", "from": 0, "to": "end", "lufs": -42},
                 {"kind": "room", "from": 0, "to": "end", "lufs": -44}],
    "sfx": sfx,
    "music_drops": [{"from": "P01", "to": "P01>", "db": -16}, {"from": "P02", "to": "P02>", "db": -16}],
    "rev": REV,
}
remap_all(sfx)
remap_all(music["sections"])
remap_all(sound["music_drops"])
polish = {"bed_drop_db": -3.0, "hold": [names["reveal"], names["clearing"], names["dipped"]], "reveal": [remap("L47")], "twist": remap("L49"),
          "emph": [remap(x) for x in ["L01.1", "L16.2", "L47", "L59.1", "L61.1", "L64"]],
          "quiet": [[remap("L67"), remap("L70")]],
          "sway": [names["freeze"], names["face10"], names["face15"]]}
story = {
    "slug": "ep119-quiet-car",
    "title": "Nobody Talks In The QUIET Car 🚆",
    "made_for_kids": False,
    "premise": ("On a sunny commuter train, anyone who says a word in the quiet car rides on out of sight until "
                "somebody answers them, and the shy narrator froze when his cousin Teddy said hey, so Teddy has "
                "been stuck aboard all year."),
    "twist": ("The empty car is full of forty people who each said one word and never got an answer, all leaning in "
              "every morning hoping the quiet one will talk, so he says good morning to all of them at once and they "
              "all answer at once."),
    "world": ("A bright silver and sea-green commuter train on an elevated line over pastel roofs: the quiet car is "
              "cream with ten rows of high-backed seat pairs, big windows and steel luggage racks, with a sunlit "
              "platform under a green canopy."),
    "voice": {"voice": "am_adam", "tempo": 1.03, "rate": 1.45},
    "key_color": "#b48cff",
    "gap": 0.15,
    "tail": 0.6,
    "fade_in": False,
    "fade_out": False,
    "rev": REV,
    "look": {"style": "closer", "fog": "#cfe6f5", "fog_density": 0.003, "fog_start": 30.0, "sky": "#8fd3ff",
             "sky_strength": 1.0, "exposure": 0.25, "flash_safe": True, "polish": polish},
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
    "framing_ok": [names["exterior"], names["bussmile"], names["emptyseat2"], names["swell"], names["loudcar"]],
    "frames_ok": [],
    "clip_ok": [],
    "asr_forgive": ["nineteen eighty seven", "walk the", "walked a", "1987"],
}
OUT.write_text(json.dumps(story, indent=1, ensure_ascii=False) + "\n")
print("wrote", OUT, f"({len(shots)} shots, {len(cues)} cues)")
print({k: v for k, v in names.items()})
