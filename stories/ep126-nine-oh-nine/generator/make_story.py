"""Writes ../story.json for ep126 "nine oh nine" (script.md, 2026-11-05, batch 13). Run: python stories/ep126-nine-oh-nine/generator/make_story.py

The words are in lines.json. Places are in ../layout.py (shared with set.py). A character facing -y has yaw 0,
+x 90, +y 180, -x -90. Time references use the script's chunk numbers; captions of four words or more are split in
two and the references are remapped. Everything that moves in the set (doors, shades, shutter, the dusk fade, the
clock tag, the dancers' sway, the dog) is driven by the cues here, read by set.py's animate().
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
REV = 3
orig_lines = json.loads((HERE / "lines.json").read_text())
lines, CHUNKMAP = [], {}
for ln in orig_lines:
    out, mp = [], []
    for cap, spoken in ln["chunks"]:
        cw, sw = cap.split(), spoken.split()
        n = len(cw)
        k = 1 if n <= 3 else 2
        sizes = [n // k + (1 if i < n % k else 0) for i in range(k)]
        mp.append(len(out))
        i = 0
        for sz in sizes:
            out.append([" ".join(cw[i:i + sz]), " ".join(sw[i:i + sz])])
            i += sz
    CHUNKMAP[ln["id"]] = mp
    lines.append({**ln, "chunks": out})
# the 0.6 s music drop before L21
idx = next(i for i, l in enumerate(lines) if l["id"] == "L21")
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


H = {"me": 1.0, "grandma": 0.93, "grandpa": 0.97, "baker": 1.0, "tran": 1.0}
cast = {
    "me": person("#f1c9a0", "#e24a3b", "#3a4a66", "#f4f4f2", hair="cap", hair_c="#6a4528", extras=["backpack", "hooddown"],
                 extra_c="#2f5f8f", brow_w=1.6, height=H["me"]),
    "grandma": person("#f0cfae", "#b79ce8", "#f0cf55", "#f4f4f2", hair="long", hair_c="#d9dde6", eyes="lashes",
                      brow_w=1.3, height=H["grandma"]),
    "grandpa": person("#e8bf98", "#d7b98a", "#4a4a52", "#3a2c24", hair="buzz", hair_c="#f4f4f4", brow_w=1.7,
                      height=H["grandpa"], width=1.03),
    "baker": person("#d9a47a", "#f4f1e8", "#4a4a52", "#3a2a1a", hair="cap", hair_c="#3a281a", extras=["apron"],
                    extra_c="#ff9fb2", hat="beanie", hat_c="#f4f1e8", brow_w=1.4, height=H["baker"]),
    "tran": person("#c98f64", "#4a8a5a", "#2c3a4a", "#f4f4f2", hair="spiky", hair_c="#15110f", brow_w=1.4,
                   sleeves="short", height=H["tran"]),
}
cast["me"]["face"]["freckles"] = True
acting = {n: [] for n in cast}
last = {n: [0.0, 0.0, 0.0] for n in cast}
cues = []
SH = []


def _z(p):
    """Add the roof's height to a mark on the feed store roof."""
    if len(p) == 2:
        p = p + [G.ZR if (-7 < p[0] < 7 and 0 < p[1] < 8.95) else 0.0]
    return p


def key(who, at, pos=None, **kw):
    """A key at `at`; position held from the last key unless `pos` is given (then it walks there over the gap)."""
    p = list(pos) if pos is not None else list(last[who])
    p = _z(p)
    acting[who].append({"at": at, "pos": p, **kw})
    last[who] = p


def teleport(who, at, pos, **kw):
    acting[who].append({"at": at, "pos": list(last[who]), "blend": 0.0})
    p = _z(list(pos))
    acting[who].append({"at": at, "pos": p, "blend": 0.0, **kw})
    last[who] = p


def cue(at, name, **kw):
    cues.append({"at": at, "name": name, **kw})


def cam(tx, ty, tz, d, az, lens, cz=None, lookz=None):
    """A camera d metres from (tx, ty, tz) on the side az degrees round from the south (0 = south of it, 90 = east of
    it, 180 = north of it), looking at it."""
    cx = tx + d * math.sin(az * D2R)
    cy = ty - d * math.cos(az * D2R)
    return [[0, [round(cx, 3), round(cy, 3), cz if cz is not None else tz], [tx, ty, tz if lookz is None else lookz], lens]]


def face(x, y, hz, az, width=0.30, lens=32, up=0.12):
    """A camera that fills `width` of the frame with a 0.41 m head centred at (x, y, hz), seen from azimuth az, the
    head placed `up` of the frame height above the middle."""
    d = 0.41 * lens / (13.5 * width)
    fh = d * 24.0 / lens
    return cam(x, y, hz, d, az, lens, cz=hz + 0.02 * fh, lookz=hz - up * fh)


def hz(who, z=0.0):
    return 1.57 * H[who] + z


def shot(sid, at, camera, **kw):
    SH.append((sid, at, camera, kw))


def yaw_to(frm, to):
    return math.degrees(math.atan2(to[0] - frm[0], -(to[1] - frm[1])))


BX, BY = G.BUS
KX, KY = G.KITCHEN
RX, RY = G.ROAD
ZR = G.ZR
GPA = list(G.GRANDPA)
GMA = list(G.GRANDMA)
DOOR = (-6.0, -33.0)          # the green door's foot; the door faces east


# ------------------------------------------------------------------------------------------------ the starting marks
cue(0, "look", id="dusk", dur=0)
cue(0, "time", hh=9, mm=6)
cue(0, "sit", who="me", s=1.0)
cue(0, "sit", who="grandma", s=0.0)
cue(0, "sit", who="grandpa", s=0.0)
cue(0, "dance", amp=1.0)
cue(0, "shades", s=0.0)
cue(0, "doors", on=0.0)
key("me", 0, [BX, BY], yaw=0, expr="worried", head=[0, 0], arms=[0, 0], side=[0, 0])
key("grandma", 0, GMA[:2], yaw=GMA[2], expr="smile", arms=[0.55, 0.55], side=[0, 0], hidden=False)
key("grandpa", 0, GPA[:2], yaw=GPA[2], expr="smile", arms=[0.55, 0.55], side=[0, 0], lean=0)
key("baker", 0, [-5.3, -16.6], yaw=90, expr="neutral")
key("tran", 0, [1.0, -60.0], yaw=180, expr="worried", hidden=True)

# ===== 01 the rule and its price (L01 to L05)
shot("S01a", 0, face(BX, BY, hz("me"), 0, 0.34, 34))
cue("L01", "bus", mode="gold")
shot("S01b", "L01.0+0.55", face(BX, BY, hz("me"), 0, 0.5, 34))
shot("S02", "L02", face(BX, BY, hz("me"), 5, 0.34, 34))
key("me", "L02", expr="worried", side=[0, 0])
key("me", "L02.1", expr="neutral", side=[26, 26])
key("me", "L02.1+0.5", expr="neutral", side=[0, 0])
# the baker, 9:08
cue("L03", "time", hh=9, mm=8)
teleport("me", "L03", [BX, BY], yaw=0)
key("baker", "L03", [-5.3, -16.6], yaw=90, expr="neutral", arms=[0, 0])
key("baker", "L03+0.2", arms=[150, 150])
key("baker", "L03.1+0.1", arms=[110, 110])
cue("L03", "shutter", on=1.0)
shot("S03", "L03", cam(-5.3, -16.6, hz("baker"), 3.2, 90, 32, lookz=hz("baker") - 0.3))
# Mr. Tran at a run
teleport("baker", "L04", [-9.5, -16.6], yaw=90)
teleport("tran", "L04", [1.4, -25.0], yaw=180, expr="worried", hidden=False, run=True)
key("tran", "L04+0.1", [1.4, -25.0], yaw=180, run=True)
key("tran", "L05", [1.1, -13.0], yaw=180, run=True, expr="worried")
shot("S04", "L04", [[0, [2.4, -20.2, 1.45], [1.4, -25.0, 1.4], 34], [1, [2.1, -8.0, 1.45], [1.2, -12.8, 1.4], 34]])
# every door in town shuts, one slow dusk fade
cue("L05", "time", hh=9, mm=9)
cue("L05", "look", id="night", dur=1.5)
cue("L05+0.15", "doors", on=1.0)
cue("L05", "dog", on=0.0)
teleport("tran", "L05+0.1", [1.1, -60.0], yaw=180, hidden=True)
shot("S05", "L05", [[0, [2.0, -12.5, 1.6], [-6.0, -18.0, 1.3], 26]])

# ===== 02 the narrator is the exception (L06 to L11)
cue("L06", "bus", mode="off")
teleport("me", "L06", [KX, KY], yaw=0, expr="neutral")
cue("L06", "sit", who="me", s=0.0)
shot("S06", "L06", face(KX, KY, hz("me"), 0, 0.34, 34))
key("me", "L06.2", expr="neutral", head=[0, 6])
cue("L07", "bus", mode="night")
cue("L07", "time", hh=8, mm=50)
cue("L07", "sit", who="me", s=1.0)
teleport("me", "L07", [BX, BY], yaw=0, expr="worried", head=[0, 0])
shot("S07", "L07", face(BX, BY, hz("me"), -4, 0.34, 34))
# the bus stopped on a dark road, me stepping out
cue("L08", "bus", mode="off")
cue("L08", "time", hh=8, mm=52)
cue("L08", "sit", who="me", s=0.0)
teleport("me", "L08", [RX, RY - 2.0], yaw=0, expr="worried")
key("me", "L08+0.5", [RX, RY - 2.0], yaw=0)
key("me", "L08.1", [RX + 0.3, RY - 5.0], yaw=0, expr="worried")
shot("S08", "L08", cam(RX + 0.2, RY - 3.4, 1.2, 6.2, 12, 30, cz=1.4))
# running
cue("L09", "time", hh=9, mm=1)
teleport("me", "L09", [0.6, -28.5], yaw=180, expr="scared", run=True)
key("me", "L09+0.1", [0.6, -28.5], yaw=180, run=True)
key("me", "L10", [0.6, -19.5], yaw=180, run=True, expr="scared")
shot("S09", "L09", [[0, [1.0, -23.6, 1.4], [0.6, -28.5, 1.35], 30], [1, [1.0, -14.6, 1.4], [0.6, -19.5, 1.35], 30]])
# the green door, shut; then me at it, knocking
cue("L10", "time", hh=9, mm=9)
teleport("me", "L10", [DOOR[0] + 3.0, DOOR[1] + 4.0], yaw=180, expr="scared", head=[0, 0])
shot("S10", "L10", cam(DOOR[0], DOOR[1], 1.2, 4.2, 90, 28, lookz=1.1))
teleport("me", "L11", [DOOR[0] + 0.85, DOOR[1] + 0.2], yaw=-60, expr="scared", head=[52, 0], arms=[0, 0])
key("me", "L11+0.1", arms=[78, 0])
key("me", "L11+0.4", arms=[62, 0])
key("me", "L11+0.7", arms=[78, 0])
key("me", "L11+1.0", arms=[62, 0])
shot("S11", "L11", face(DOOR[0] + 0.85, DOOR[1] + 0.2, hz("me"), -12, 0.30, 32))

# ===== 03 the shades come down, the town goes silent (L12 to L16)
cue("L12", "time", hh=9, mm=40)
cue("L12", "shades", s=1.0)
teleport("me", "L12", [0.0, -15.0], yaw=180, expr="worried", head=[0, 0], arms=[0, 0])
shot("S12a", "L12", [[0, [4.4, -16.0, 1.9], [-6.0, -19.0, 1.9], 26]])
cue("L12.1-0.1", "lastshade", on=1.0, dur=1.45)
shot("S12b", "L12.1", [[0, [2.2, -24.2, 2.0], [-6.0, -24.2, 2.0], 30]])
key("me", "L13", [0.0, -15.0], yaw=180, expr="worried")
shot("S13", "L13", cam(0.0, -15.0, 1.3, 5.5, 180, 38, cz=1.5, lookz=1.5))
key("me", "L14", yaw=180, expr="wide", head=[0, -22])
shot("S14", "L14", face(0.0, -15.0, hz("me"), 178, 0.30, 32, up=0.05))
key("me", "L15", yaw=180, expr="neutral", head=[-24, -4])
shot("S15", "L15", face(0.0, -15.0, hz("me"), 168, 0.40, 36, up=0.05))
shot("S16", "L16", [[0, [G.LADDER_X - 2.0, 15.5, 1.6], [G.LADDER_X + 0.5, 9.0, 7.2], 24]])

# ===== 04 the ladder (L17 to L20)
teleport("me", "L17", [G.LADDER_X + 0.9, 10.6], yaw=180, expr="worried", head=[0, 0])
shot("S17", "L17", [[0, [G.LADDER_X + 2.4, 12.8, 1.8], [G.LADDER_X, 9.0, 3.8], 28]])
key("me", "L18", yaw=180, expr="worried", head=[0, 6])
shot("S18", "L18", face(G.LADDER_X + 0.9, 10.6, hz("me"), 176, 0.32, 32, up=0.0))
shot("S19", "L19", [[0, [G.LADDER_X + 0.3, 10.9, 5.85], [G.LADDER_X + 0.1, 9.1, 5.62], 30], [1, [G.LADDER_X + 0.25, 10.5, 5.82], [G.LADDER_X + 0.12, 9.1, 5.65], 30]])
key("me", "L20", yaw=180, expr="neutral", head=[0, -12], lean=-4)
shot("S20", "L20", face(G.LADDER_X + 0.9, 10.6, hz("me"), 180, 0.30, 32, up=0.0))
shot("S20d", "P01", [[0, [G.LADDER_X - 0.5, 11.5, 5.0], [G.LADDER_X, 9.0, 7.0], 26]])

# ===== 05 two people on the roof (L21 to L28)
cue("L21", "time", hh=11, mm=15)
teleport("me", "P01", [G.LADDER_X, G.ROOF_FACE_Y], yaw=0, expr="wide", head=[0, 0])
shot("S21", "L21", face(GMA[0] - 0.3, GMA[1], hz("grandma", ZR), 165, 0.25, 30, up=0.04))
shot("S22", "L22", face(GMA[0] - 0.38, GMA[1], hz("grandma", ZR), 172, 0.3, 30, up=0.04))
key("grandma", "L23", expr="wide", blink=False)
shot("S23", "L23", face(GMA[0], GMA[1], hz("grandma", ZR), 168, 0.36, 30, up=0.04))
key("grandma", "L24", expr="smile", blink=True)
key("grandpa", "L24-0.05", yaw=0.0)
teleport("grandpa", "L24", GPA[:2], yaw=-170, expr="sad-smile", arms=[0.55, 0.55])
shot("S24", "L24", face(GPA[0], GPA[1], hz("grandpa", ZR), 190, 0.34, 30, up=0.04))
key("me", "L25", expr="wide")
shot("S25", "L25", face(G.LADDER_X, G.ROOF_FACE_Y, hz("me", ZR), 3, 0.32, 32, up=0.02))
shot("S26", "L26", cam(G.CANE[0], G.CANE[1], ZR + 0.95, 1.4, 20, 30, cz=ZR + 0.72))
# they stop and turn to me
cue("L27", "dance", amp=0.0, dur=0.4)
tm = yaw_to(GMA[:2], (G.LADDER_X, G.ROOF_FACE_Y))
key("grandma", "L27", GMA[:2], yaw=tm, expr="neutral", arms=[0, 0])
key("grandpa", "L27", [0.9, 5.9], yaw=yaw_to([0.9, 5.9], (G.LADDER_X, G.ROOF_FACE_Y)), expr="sad-smile", arms=[0, 0])
shot("S26b", "L26.2", cam(G.CANE[0], G.CANE[1], ZR + 0.9, 1.6, -25, 30, cz=ZR + 1.1))
shot("S27a", "L27", face(GMA[0], GMA[1], hz("grandma", ZR), tm - 8, 0.34, 30, up=0.04))
shot("S27b", "L27.1", face(G.LADDER_X, G.ROOF_FACE_Y, hz("me", ZR), 8, 0.34, 32, up=0.02))
# "You'd better SIT down."
key("grandma", "L27.1+0.3", GMA[:2], yaw=tm, expr="smile", arms=[0, 0])
key("grandma", "L28+0.2", list(G.SIT_G), yaw=180, expr="smirk", arms=[0, 0])
cue("L28+0.6", "sit", who="grandma", s=1.0, dur=0.4)
cue("L28+0.9", "pat", amp=1.0)
key("grandpa", "L27.1+0.3", [0.1, 6.2], yaw=0, expr="sad-smile")
key("grandpa", "L28+0.4", list(G.GP_STAND), yaw=0, expr="sad-smile")
cue("L28", "time", hh=2, mm=30)
teleport("me", "L28", list(G.ME_PARAPET), yaw=0, expr="neutral", head=[0, 0])
cue("L28", "sit", who="me", s=1.0)
shot("S28", "L28", face(G.SIT_G[0], G.SIT_G[1], hz("grandma", ZR), 176, 0.30, 30, up=0.02))

# ===== 06 the reveal said plainly (L29 to L39)
key("grandma", "L29", yaw=180, expr="smile")
shot("S29", "L29", face(G.SIT_G[0], G.SIT_G[1], hz("grandma", ZR), 168, 0.36, 30, up=0.04))
cue("L29", "pat", amp=0.0)
key("me", "L29", expr="wide")
shot("S30", "L30", cam(G.RADIO[0], G.RADIO[1], ZR + 0.65, 1.8, 160, 30, cz=ZR + 0.95))
key("grandma", "L31", expr="polite")
shot("S31", "L31", face(G.SIT_G[0], G.SIT_G[1], hz("grandma", ZR), 184, 0.34, 30, up=0.04))
key("grandma", "L32", expr="smile")
shot("S32", "L32", face(G.SIT_G[0], G.SIT_G[1], hz("grandma", ZR), 176, 0.46, 30, up=0.04))
key("grandma", "L33", expr="polite")
shot("S33", "L33", cam(G.SIT_G[0] + 0.1, G.SIT_G[1], hz("grandma", ZR), 3.1, 188, 30, cz=hz("grandma", ZR) + 0.1,
                       lookz=hz("grandma", ZR) - 0.3))
shot("S34", "L34", [[0, [G.BOARD[0] - 0.3, -0.6, 1.6], [G.BOARD[0], G.BOARD[1], 1.5], 28]])
shot("S35", "L35", [[0, [0.0, 0.3, ZR + 2.6], [0.0, -24.0, 1.5], 22], [1, [0.0, -1.3, ZR + 2.4], [0.0, -24.0, 1.5], 24]])
shot("S36", "L36", [[0, [1.717, 2.03, ZR + 1.3], [1.3, 5.0, ZR], 26], [1, [1.647, 2.524, ZR + 1.1], [1.3, 5.0, ZR], 26]])
key("grandpa", "L37", yaw=0, expr="warm")
shot("S37", "L37", face(G.GP_STAND[0], G.GP_STAND[1], hz("grandpa", ZR), 3, 0.34, 30, up=0.04))
# the dance, again: over my shoulder (S38)
cue("L38", "sit", who="grandma", s=0.0)
cue("L38", "pat", amp=0.0)
cue("L38", "dance", amp=1.0, dur=0.3)
teleport("grandma", "L38", GMA[:2], yaw=GMA[2], expr="smile", arms=[0.6, 0.6])
teleport("grandpa", "L38", GPA[:2], yaw=GPA[2], expr="smile", arms=[0.6, 0.6])
key("me", "L38", expr="smile")
shot("S38", "L38", [[0, [G.ME_PARAPET[0] + 1.6, 11.2, ZR + 2.3], [GMA[0] + 0.4, GMA[1], ZR + 1.2], 24]])
shot("S38b", "L38.2", face(GMA[0], GMA[1], hz("grandma", ZR), 160, 0.3, 30, up=0.04))
key("me", "L39", expr="laugh")
shot("S39", "L39", face(G.ME_PARAPET[0], G.ME_PARAPET[1], hz("me", ZR), 4, 0.32, 32, up=0.02))

# ===== 07 the promise and the warm turn (L40 to L46)
shot("S40", "L40", face(GMA[0], GMA[1], hz("grandma", ZR), 168, 0.34, 30, up=0.04))
key("grandma", "L40", expr="polite")
key("me", "L40", expr="smile")
shot("S40b", "L40.1", face(GMA[0], GMA[1], hz("grandma", ZR), 178, 0.42, 30, up=0.04))
cue("L41", "dance", amp=0.0, dur=0.4)
key("grandma", "L41", GMA[:2], yaw=180, expr="smile", arms=[0, 0])
key("grandpa", "L41", GPA[:2], yaw=0, arms=[0, 0], lean=0)
key("grandpa", "L41+0.45", [0.1, 5.5], yaw=-90, expr="smile", arms=[0, 40], lean=14)
key("grandpa", "L41+1.2", arms=[0, 44])
cue("L41+1.1", "radio", on=1.0, dur=1.0)
shot("S41", "L41+0.5", cam(G.RADIO[0] - 0.12, G.RADIO[1], ZR + 1.0, 2.3, 175, 30, cz=ZR + 0.85))
cue("L42", "time", hh=5, mm=50)
cue("L42", "dance", amp=1.0, dur=0.3)
cue("L42", "sky", id="pale")
teleport("grandma", "L42", GMA[:2], yaw=GMA[2], expr="warm", arms=[0.6, 0.6])
teleport("grandpa", "L42", GPA[:2], yaw=GPA[2], expr="smile", arms=[0.6, 0.6], lean=0)
shot("S42", "L42", face(GMA[0], GMA[1], hz("grandma", ZR), 165, 0.27, 30, up=0.04))
key("grandpa", "L43-0.05", yaw=0.0)
teleport("grandpa", "L43", GPA[:2], yaw=-170, expr="smile", arms=[0.6, 0.6])
shot("S43", "L43", face(GPA[0], GPA[1], hz("grandpa", ZR), 190, 0.2, 30, up=0.2))
cue("L44", "time", hh=9, mm=20)
cue("L44", "sky", id="night")
cue("L44", "bus", mode="night")
cue("L44", "sit", who="me", s=1.0)
teleport("me", "L44", [BX, BY], yaw=0, expr="smile", head=[0, 0])
shot("S44", "L44", face(BX, BY, hz("me"), 4, 0.34, 34))
cue("L45", "bus", mode="off")
cue("L45", "sit", who="me", s=0.0)
LX = G.LADDER_X + 0.62
teleport("me", "L45", [LX, 10.5], yaw=180, expr="warm", side=[0, 66], head=[0, 0])
shot("S45", "L45", face(LX, 10.5, hz("me"), 176, 0.34, 32, up=0.02))
cue("L46", "time", hh=9, mm=6)
cue("L46", "bus", mode="gold")
cue("L46", "sit", who="me", s=1.0)
teleport("me", "L46", [BX, BY], yaw=0, expr="worried", side=[0, 0], head=[0, 0])
shot("S46a", "L46", face(BX, BY, hz("me"), 0, 0.34, 34))
shot("S46", "L46.2", face(BX, BY, hz("me"), 0, 0.44, 34))

# ------------------------------------------------------------------------------------------------ finish
remap_all(cues)
for k_ in acting.values():
    remap_all(k_)
shots, names = [], {}
for i, (sid, at, camera, kw) in enumerate(SH):
    s = {"id": sid, "cam": camera, "step": 2}
    if i:
        s["at"] = remap(at)
    s.update(kw)
    shots.append(s)
    names[sid] = sid

sfx = [
    {"at": "L01.0+0.75", "kind": "bell", "db": -13},
    {"at": "L05+0.45", "kind": "door", "db": -17},
    {"at": "L05+0.95", "kind": "door", "db": -17},
    {"at": "L11+0.1", "kind": "knock", "db": -9, "pattern": [0, 0.3, 0.6], "tone": "hand"},
    {"at": "L12.1", "kind": "creak", "db": -22, "dur": 1.4},
    {"at": "P01>", "kind": "sting", "db": -15},
    {"at": "L41+1.1", "kind": "riser", "db": -20, "dur": 1.4},
]
music = {
    "root": 45, "mode": "minor", "bpm": 96, "seed": 126,
    "sections": [
        {"at": 0, "voices": ["pulse", "piano", "pad"], "energy": 0.55},
        {"at": "L12", "voices": ["musicbox", "drone"], "energy": 0.3},
        {"at": "L21", "voices": ["musicbox", "piano", "pad"], "energy": 0.42},
        {"at": "L29", "voices": ["piano", "pad", "musicbox"], "energy": 0.5, "mode": "major"},
        {"at": "L40", "voices": ["piano", "pulse", "pad"], "energy": 0.55, "mode": "minor"},
    ],
}
sound = {
    "floor": "concrete", "steps_db": -24,
    "ambience": [{"kind": "crickets", "from": "L06", "to": "end", "lufs": -42},
                 ],
    "hums": [{"note": "A1", "from": "L07", "to": "L08.1", "lufs": -38, "fade_in": 0.3, "fade_out": 1.4}],
    "sfx": sfx,
    "music_drops": [{"from": "P01", "to": "P01>", "keep": ["sting"]}],
    "rev": REV,
}
remap_all(sfx)
remap_all(music["sections"])
remap_all(sound["music_drops"])
remap_all(sound["ambience"])
polish = {"reveal": [remap("L32"), remap("L38")], "twist": remap("L32"),
          "emph": [remap(x) for x in ["L01.0", "L05", "L12", "L14", "L21", "L23", "L38"]],
          "quiet": [[remap("L36"), remap("L38")]],
          "hold": [], "sway": []}
story = {
    "slug": "ep126-nine-oh-nine",
    "title": "Nobody Lets You IN After 9:09",
    "made_for_kids": False,
    "premise": ("In a small town everyone is indoors by 9:09 every night and nobody lets anyone in till dawn, and "
                "nobody knows why, until I get locked out and climb the feed store ladder."),
    "twist": ("My grandma made the curfew up at seventeen so the streets would be empty for her first date with "
              "my grandpa on the feed store roof, the whole town just followed it, and they have met up there every "
              "night for sixty years."),
    "world": ("One bright block of painted brick shops ending at a red feed store with a flat roof, a ladder on its "
              "back wall, cream streetlamps, a huge moon, a little radio on a crate."),
    "voice": {"voice": "am_adam", "tempo": 1.03, "rate": 1.45},
    "key_color": "#ffd76b",
    "gap": 0.12,
    "tail": 0,
    "fade_in": False,
    "fade_out": False,
    "rev": REV,
    "look": {"style": "closer", "fog": "#9fb0d8", "fog_density": 0.003, "fog_start": 60.0, "sky": "#ffcf8a",
             "sky_strength": 1.0, "exposure": 0.1, "flash_safe": True, "polish": polish},
    "grade": {"shadows": [0.0, 0.0, 0.03], "highlights": [0.03, 0.012, -0.02], "saturation": 1.1, "contrast": 1.05,
              "vignette": 0.2, "bloom": 0.2, "grain": 0.008},
    "phonemes": {},
    "homophones": {"ninehundredandnine": "nineohnine", "ninehundredandeight": "nineoheight", "1965": "nineteensixtyfive"},
    "cast": cast,
    "lines": lines,
    "shots": shots,
    "acting": acting,
    "cues": cues,
    "fx": [],
    "music": music,
    "sound": sound,
    "set_moves": [],
    "frames_ok": ["S05", "S03", "S27a", "S28"],
    "framing_ok": ["S12b", "S25", "S41", "S40b", "S26", "S26b", "S30", "S35"],
}
OUT.write_text(json.dumps(story, indent=1, ensure_ascii=False) + "\n")
print("wrote", OUT, f"({len(shots)} shots, {len(cues)} cues)")
