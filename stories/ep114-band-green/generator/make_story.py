"""Writes ../story.json for ep114 "band green" (script.md, 2026-11-04). Run: python stories/ep114-band-green/generator/make_story.py

The words are in lines.json. Places are in ../layout.py (shared with set.py). A character facing -y has yaw 0,
+x 90, +y 180, -x -90. Time references use the script's chunk numbers; captions of four words or more are split in
two and the references are remapped. The dance itself is drawn in set.py's animate(), driven by the cues here.
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


cast = {
    "me": person("#8a5a3a", "#e0a32a", "#8a8f98", "#f4f4f2", hair="spiky", hair_c="#15110f", sleeves="long",
                 extras=["hooddown"], brow_w=1.9),
    "grandpa": person("#e2b088", "#3d6ea6", "#4a4a52", "#3a2c24", hair="cap", hair_c="#f0f0f0", hat="ballcap",
                      hat_c="#8a8e96", brow_w=1.6, width=1.04),
    "bank": person("#d9a47a", "#6b7280", "#5a606c", "#1c1c20", hair="cap", hair_c="#3a281a", extras=["tie"],
                   collar="#f4f4f2", extra_c="#c0392b"),
    "mail": person("#b98456", "#2f5fa8", "#233a66", "#1c1c20", hair="bun", hair_c="#1a1410", hat="ballcap",
                   hat_c="#2f5fa8", eyes="lashes", sleeves="short"),
    "sand": person("#f0c8a0", "#c0543a", "#4a5a7a", "#2a2a2a", hair="swoop", hair_c="#a05a2a", sleeves="short"),
    "t1": person("#e8b890", "#4a8a5a", "#3a3a48", "#d8d0c8", hair="spiky", hair_c="#6a4a2a"),
    "t2": person("#c98f64", "#d96b8a", "#f0e6d6", "#3a2a1a", hair="long", hair_c="#150f0c", eyes="lashes"),
    "t3": person("#f0c8a0", "#8a5ab0", "#2a2a38", "#3a3a3a", hair="buzz", hair_c="#c89a5a"),
    "t4": person("#8a5a3a", "#f08a3a", "#3a4a5a", "#f4f4f2", hair="cap", hair_c="#15110f", hat="beanie", hat_c="#4a4a8a"),
    "t5": person("#d3a07a", "#3a8aaa", "#5a4a3a", "#2a3a2a", hair="bun", hair_c="#3a281a", eyes="lashes"),
    "t6": person("#e2b088", "#6a8a4a", "#4a4036", "#2a2a2a", hair="swoop", hair_c="#2a2a2a"),
    "t7": person("#b98456", "#e8c24a", "#2c3a4a", "#7a4a2a", hair="spiky", hair_c="#1a1410", sleeves="short"),
}
acting = {n: [] for n in cast}
last = {n: [0, 0] for n in cast}
cues = []
SH = []
D = G.DANCE
SEAT = list(G.ME_SEAT)
STAND = list(G.ME_STAND)


def key(who, at, pos=None, **kw):
    """A key at `at`; position held from the last key unless `pos` is given (then it walks there over the gap)."""
    p = list(pos) if pos is not None else list(last[who])
    acting[who].append({"at": at, "pos": p, **kw})
    last[who] = p


def teleport(who, at, pos, **kw):
    acting[who].append({"at": at, "pos": list(last[who]), "blend": 0.0})
    acting[who].append({"at": at, "pos": list(pos), "blend": 0.0, **kw})
    last[who] = list(pos)


def cue(at, name, **kw):
    cues.append({"at": at, "name": name, **kw})


def deg(v):
    return math.degrees(v)


def cam(tx, ty, tz, d, az, lens, cz=None, lookz=None):
    """A held camera d metres from (tx, ty, tz), on the side az degrees round from the south (0 = south of it, 90 =
    east of it), looking at it. Single key: the polish pack adds the slow push."""
    cx = tx + d * math.sin(az * D2R)
    cy = ty - d * math.cos(az * D2R)
    return [[0, [round(cx, 3), round(cy, 3), cz if cz is not None else tz], [tx, ty, tz if lookz is None else lookz], lens]]


def shot(at, camera, name, **kw):
    SH.append((at, camera, name, kw))


def front(name, tz=1.4, d=3.2, lens=36, off=0.0, cz=None):
    """A camera in front of a dancer's resting face."""
    x, y, yaw = D[name]
    return cam(x, y, tz, d, yaw + off, lens, cz)


MEX, MEY = SEAT
BX, BY = G.BENCH1
# ---------------------------------------------------------------------------------------------- the town at rest
for who, (x, y, yaw) in D.items():
    key(who, 0, [x, y], yaw=yaw, expr="grin", lean=0, arms=[0, 0], side=[0, 0])
key("me", 0, SEAT, yaw=90, expr="worried", head=[0, 6], lean=0, arms=[0, 0], side=[0, 0])

cue(0, "look", id="dusk", dur=0)
cue(0, "song", n=1.0)
cue(0, "feet", n=6.0)
cue(0, "dance", amp=1.0, tired=0.0)
cue(0, "face", m=0.0, tx=BX, ty=BY)
cue(0, "sit", s=1.0)
cue(0, "medance", amp=0.0)
cue(0, "band", u=1.0, play=1.0, brim=0.0, eyes=0.0, turn=0.0)
cue(0, "clock", h=12.0)
cue(0, "truck", y=-60.0)
cue(0, "sit6", s=0.0)
cue(0, "phone", where=0.0, screen=0.0)

# ===== 01 the rule (L01 to L05)
shot(0, [[0, [-3.0, -4.3, 0.3], [-4.6, -2.2, 0.38], 24], [1, [-3.15, -4.1, 0.32], [-4.6, -2.2, 0.4], 24]], "feet1")
shot("L01.1", cam(1.0, -1.0, 1.2, 8.5, 5, 28), "row")
shot("L01.2", cam(-3.2, -1.0, 1.3, 5.5, 85, 30), "dancers")
shot("L02", cam(MEX, MEY, 1.42, 3.2, 90, 40), "meglum")
cue("L02", "song", n=1.0)
shot("L02.2", [[0, [-4.4, -2.5, 0.4], [-5.65, -1.75, 0.1], 30]], "sneakers")
# L03: the wide sunset, the band shows up
shot("L03", [[0, [0.0, -9.5, 1.9], [0.0, 6.0, 2.9], 18]], "wide")
cue("L03", "song", n=2.0)
shot("L03.2", [[0, [0.6, 2.4, 1.5], [0.0, 9.0, 2.5], 30]], "bandshows")
# L04: from behind the crowd
shot("L04", [[0, [2.4, 3.6, 1.7], [0.0, 9.0, 2.4], 26]], "behindcrowd")
shot("L04.2", [[0, [-0.9, 5.4, 1.9], [-0.8, 8.8, 2.3], 38]], "jackets")
shot("L05", [[0, [0.3, 5.9, 1.3], [0.0, 8.8, 3.1], 36]], "brims")
shot("L05.2", [[0, [3.8, 6.2, 1.6], [1.4, 8.8, 3.1], 38]], "brims2")

# ===== 02 the rule at work (L06 to L10)
shot("L06", cam(D["t2"][0], D["t2"][1], 0.4, 2.4, 120, 28, cz=0.3), "feetgo")
shot("L07", front("bank", 1.3, 3.6, 34), "bank")
shot("L08", cam(D["mail"][0], D["mail"][1], 0.85, 4.2, 170, 30, cz=1.2), "mail")
shot("L09", front("grandpa", 1.35, 3.6, 34), "grandpa")
shot("L09.1", front("grandpa", 0.55, 2.2, 30, cz=0.45), "knees")
shot("L10", front("sand", 1.35, 3.6, 34), "sand")
shot("L10.2", front("sand", 1.2, 2.4, 40), "sandwich")
cue("L06", "song", n=3.0)

# ===== 03 me on the bench (L11 to L18)
shot("L11", [[0, [-8.0, -4.6, 1.4], [-5.6, -1.5, 1.2], 32]], "bench")
shot("L12", [[0, [-4.7, -3.0, 0.4], [-5.6, -1.75, 0.1], 30]], "sneakers2")
# L13: the photo of me and Benny on my phone, held on my raised hand
key("me", "L13", arms=[0, 88], head=[0, 8], expr="worried")
key("me", "L13.2", arms=[0, 88], head=[0, 8])
cue("L13", "phone", where=1.0, screen=0.0, x=MEX + 0.7, y=MEY + 0.52, z=1.7, rot=90.0, tilt=-8.0, lie=0.0)
shot("L13", [[0, [-3.3, -1.0, 1.55], [MEX + 0.7, MEY + 0.5, 1.5], 40]], "photo")
key("me", "L13.1", arms=[0, 0], head=[0, 6])
cue("L13.1", "phone", where=0.0)
cue("L13.1", "truck", y=-8.0, dur=0)
cue("L13.1+0.1", "truck", y=38.0, dur=3.6)
shot("L13.1", [[0, [10.2, -14.0, 1.6], [12.3, -2.0, 1.8], 30]], "truck")
cue("L14", "truck", y=-60.0, dur=0)
cue("L14", "band", u=0.8, play=0.0, brim=0.0, eyes=0.0, turn=0.0, dur=0)
cue("L14+0.05", "band", u=1.0, dur=1.5)
cue("L14+1.2", "band", play=1.0, dur=0.5)
shot("L14", [[0, [0.0, 3.4, 1.5], [0.0, 10.0, 1.9], 24]], "bandwalk")
cue("L15", "song", n=4.0)
shot("L15", [[0, [-5.55, -0.55, 1.5], [BX - 0.05, BY + 1.5, 0.86], 55]], "scratch")
shot("L15.3", [[0, [-6.0, -0.6, 1.2], [-2.0, 1.0, 1.3], 26]], "mypov")
key("me", "L16", head=[-25, 4], expr="worried")
shot("L16", cam(MEX, MEY, 1.42, 2.8, 115, 38), "watch")
shot("L17", [[0, [3.1, -8.5, 2.0], [-1.0, 0.5, 1.2], 22]], "songend")
cue("L17", "song", n=5.0)
shot("L18", [[0, [4.5, -6.5, 1.8], [-2.0, 0.0, 1.3], 22]], "spin")
cue("L18.1", "face", m=1.0, dur=0.5)
shot("L18.1", [[0, [-7.6, -3.4, 1.9], [-1.5, 1.0, 1.3], 24]], "allface")
key("me", "L18.3", head=[0, 4], expr="worried")
shot("L18.3", cam(MEX, MEY, 1.42, 2.8, 110, 40), "notice")
cue("L19", "face", m=0.0, dur=0.5)

# ===== 04 last Saturday (L19 to L27)
cue("L19", "look", id="night", dur=1.0)
cue("L19", "dance", amp=0.9, tired=0.15, dur=1.0)
cue("L19", "song", n=20.0, dur=0.4)
shot("L19", [[0, [0.0, -9.5, 2.3], [0.0, 2.0, 1.8], 20]], "night")
cue("L20", "song", n=36.0, dur=0.5)
cue("L20", "clock", h=12.0)
shot("L19.2+0.3", [[0, [5.6, 1.0, 6.3], [14.0, 1.0, 7.2], 24]], "clock12")
cue("L20.1", "clock", h=13.0)
cue("L20.1", "song", n=38.0, dur=0.3)
shot("L20.1", [[0, [6.4, 1.2, 6.5], [14.0, 1.0, 7.2], 26]], "clock1")
cue("L20.2", "song", n=40.0, dur=0.3)
shot("L20.2", [[0, [-1.6, -4.6, 0.32], [0.4, -1.6, 0.42], 24]], "song40")
shot("P01", [[0, [0.0, 3.4, 1.0], [0.0, 8.8, 2.7], 28]], "drop")
cue("L21", "clock", h=3.0)
cue("L21", "song", n=43.0, dur=0.3)
cue("L21", "dance", amp=0.65, tired=0.5, dur=1.0)
shot("L21", [[0, [5.6, 0.8, 6.3], [14.0, 1.0, 7.2], 24]], "clock3")
cue("L22", "dance", amp=0.5, tired=0.9, dur=0.8)
cue("L22", "song", n=44.0, dur=0.3)
shot("L22", [[0, [0.0, -9.5, 3.2], [-1.0, 1.0, 1.2], 20]], "drooping")
shot("L22.2", [[0, [-1.8, -5.0, 0.3], [0.0, -2.0, 0.4], 24]], "dragging")
for w in D:
    key(w, "L21", expr="worried")
key("grandpa", "L23", expr="worried")
shot("L23", front("grandpa", 1.4, 3.0, 38), "gtired")
shot("L23.2", front("grandpa", 0.35, 2.2, 30, cz=0.3), "gfeet")
shot("L24", [[0, [0.0, 5.4, 0.6], [0.0, 8.8, 2.8], 26]], "below")
cue("L24", "song", n=45.0, dur=0.3)
shot("L24.2", [[0, [1.0, 6.4, 1.3], [1.6, 8.6, 2.2], 40]], "bells")
# L25: the bandleader tips his brim up an inch
cue("L25.2", "band", brim=1.0, dur=0.7)
shot("L25", [[0, [0.5, 5.1, 1.2], [0.0, 8.8, 3.0], 34]], "leader")
shot("L25.2", [[0, [0.5, 6.7, 1.9], [0.0, 8.8, 2.9], 46]], "brim")
shot("L26", [[0, [1.4, 5.5, 1.2], [0.0, 8.8, 2.95], 50]], "underbrim")
cue("L26.2+0.25", "band", eyes=1.0, dur=0.3)
shot("L26.2+0.25", [[0, [1.0, 6.0, 1.5], [0.0, 8.8, 2.95], 65]], "lights")
# L27: every face turns to my bench
cue("L27", "face", m=1.0, dur=0.6)
cue("L27", "song", n=46.0, dur=0.3)
shot("L27", [[0, [-9.2, -4.6, 2.4], [0.0, 2.5, 1.4], 30]], "reveal")
shot("L27.3+0.2", [[0, [-3.4, -0.2, 1.4], [-6.2, -1.6, 1.25], 40]], "benchfaces")

# ===== 05 the twist said plainly (L28 to L34)
cue("L28", "band", brim=0.0, eyes=0.0, dur=0.6)
key("me", "L28", expr="wide", head=[0, 0])
shot("L28", cam(MEX, MEY, 1.42, 2.8, 90, 40), "stunned")
shot("L29", [[0, [-1.5, 4.0, 1.8], [0.0, 9.0, 2.5], 26]], "bandback")
shot("L30", front("grandpa", 0.35, 2.4, 30, off=40, cz=0.3), "gfeet2")
cue("L30", "song", n=47.0, dur=0.3)
key("me", "L31", expr="worried", head=[0, 4])
shot("L31", cam(MEX, MEY, 1.38, 2.6, 80, 38), "mebench")
shot("L32", [[0, [-8.3, -3.2, 1.5], [D["bank"][0], D["bank"][1], 1.3], 30]], "stepbank")
shot("L32.1", [[0, [-8.3, -3.2, 1.5], [D["mail"][0], D["mail"][1], 1.0], 30]], "stepmail")
shot("L32.2", [[0, [-8.3, -3.2, 1.5], [D["sand"][0], D["sand"][1], 1.3], 30]], "stepsand")
shot("L32.3", [[0, [-7.6, -4.2, 1.5], [D["grandpa"][0], D["grandpa"][1], 1.3], 32]], "stepgrandpa")
shot("L33", [[0, [-6.4, -4.4, 1.5], [D["grandpa"][0], D["grandpa"][1], 1.45], 36]], "gface")
shot("L34", [[0, [-3.0, -5.6, 0.7], [-5.0, -2.3, 0.45], 26]], "kneesbench")

# ===== 06 the rule's own logic (L35 to L40)
shot("L35", [[0, [-2.4, -4.0, 0.4], [-4.2, -2.4, 0.35], 24]], "feetrow")
key("me", "L36", expr="angry", head=[0, 0])
shot("L36", cam(MEX, MEY, 1.42, 2.6, 100, 40), "determined")
cue("L37", "sit", s=0.0, dur=0.55)
key("me", "L37", expr="hopeful")
key("me", "L37+0.55", STAND, expr="hopeful")
cue("L37+0.4", "feet", n=7.0, dur=0.3)
cue("L37+0.6", "medance", amp=1.0, dur=0.4)
cue("L37+0.4", "face", m=0.0, dur=1.0)
cue("L37+0.5", "dance", amp=1.0, tired=0.0, dur=1.4)
shot("L37", [[0, [-3.0, -4.8, 2.4], [-5.4, -1.0, 1.0], 24]], "standup")
key("me", "L38", expr="laugh", yaw=90)
shot("L38", cam(STAND[0], STAND[1], 1.1, 4.0, 90, 30), "terrible")
shot("L39", cam(STAND[0], STAND[1], 1.1, 4.4, 60, 26), "chair")
shot("L39.1+0.45", cam(STAND[0], STAND[1], 1.25, 3.0, 110, 34), "chair2")
cue("L40", "dance", amp=1.0)
shot("L40", [[0, [-8.0, -5.0, 2.2], [-1.0, 0.5, 1.2], 22]], "alldance")
cue("L40.2", "band", play=0.0, dur=0.8)
cue("L40.2+0.2", "dance", amp=0.0, tired=0.0, dur=0.4)
cue("L40.2+0.2", "medance", amp=0.0, dur=0.4)
shot("L40.2", [[0, [0.0, 5.0, 1.3], [0.0, 8.8, 2.6], 28]], "lower")
cue("L41", "band", turn=1.0, dur=0.5)
cue("L41+0.3", "band", u=0.55, dur=3.6)
shot("L41", [[0, [0.0, 4.6, 1.8], [0.0, 11.0, 2.2], 24]], "walkoff")

# ===== 07 the warm turn (L42 to L48)
cue("L42", "look", id="dawn", dur=1.6)
cue("L42", "band", u=0.0, turn=0.0, dur=0)
LIE = {"grandpa": 125, "bank": 0, "mail": 30, "sand": 190, "t1": 180, "t2": 150, "t3": 0, "t4": 40, "t5": 90,
       "t6": 70, "t7": 160}
for who in D:
    key(who, "L42+0.7", blend=0.7, lean=-90, yaw=LIE[who], expr="laugh", arms=[0, 0], side=[70, 70])
key("me", "L42+0.7", blend=0.7, lean=-90, yaw=0, expr="laugh", arms=[0, 0], head=[0, 0])
shot("L42", [[0, [-9.0, -6.0, 3.6], [-1.0, 0.0, 0.4], 22]], "lying")
shot("L43", [[0, [D["grandpa"][0] + 1.2, D["grandpa"][1] + 1.1, 1.9], [D["grandpa"][0] - 0.6, D["grandpa"][1] - 0.4, 0.4], 34]], "glaugh")
cx_ = STAND[0] + 0.0
cue("L44", "phone", where=1.0, lie=1.0, screen=1.0, x=STAND[0], y=STAND[1] + 1.12, z=0.43, rot=0.0)
shot("L44", [[0, [STAND[0] + 0.1, STAND[1] - 1.5, 1.7], [STAND[0], STAND[1] + 0.65, 0.35], 30]], "call")
shot("L45", [[0, [-3.0, -7.0, 0.8], [0.0, 20.0, 5.0], 22]], "sunrise")
cue("L46", "look", id="dusk", dur=0)
cue("L46", "phone", where=0.0)
cue("L46", "dance", amp=1.0, tired=0.0, dur=0)
cue("L46", "feet", n=6.0, dur=0)
cue("L46", "song", n=1.0, dur=0)
cue("L46", "face", m=0.0, tx=G.BENCH2[0], ty=G.BENCH2[1], dur=0)
cue("L46", "band", u=0.8, play=0.0, dur=0)
cue("L46+0.05", "band", u=1.0, dur=1.9)
cue("L46+1.8", "band", play=1.0, dur=0.6)
cue("L46", "sit6", s=1.0, dur=0)
for who in D:
    if who == "t6":
        teleport(who, "L46", [7.15, -1.2], lean=0, yaw=-90, expr="worried", blend=0.0, arms=[0, 0], side=[0, 0])
    else:
        teleport(who, "L46", [D[who][0], D[who][1]], lean=0, yaw=D[who][2], expr="grin", blend=0.0, arms=[0, 0], side=[0, 0])
teleport("me", "L46", [-5.7, -1.75], lean=0, yaw=90, expr="smile", blend=0.0, arms=[0, 0], head=[0, 0])
cue("L46", "sit", s=0.0, dur=0)
shot("L46", [[0, [0.0, 3.4, 1.5], [0.0, 10.0, 1.9], 24]], "bandback2")
cue("L47", "face", m=1.0, dur=1.2)
shot("L47", [[0, [2.4, -0.8, 1.45], [7.1, -1.1, 1.25], 30]], "otherman")
cue("L48", "medance", amp=1.0, dur=0.3)
shot("L48", cam(-5.7, -1.75, 1.1, 4.4, 90, 26), "first")
shot("L48.1", [[0, [-3.0, -4.3, 0.3], [-4.6, -2.2, 0.38], 24], [1, [-3.15, -4.1, 0.32], [-4.6, -2.2, 0.4], 24]], "feet2")
# ---------------------------------------------------------------------------------------------- finish
remap_all(cues)
for k_ in acting.values():
    remap_all(k_)
shots, names = [], {}
for i, (at, camera, nm, kw) in enumerate(SH):
    s = {"id": f"S{i + 1:02d}", "cam": camera, "step": 2}
    if i:
        s["at"] = remap(at)
    s.update(kw)
    shots.append(s)
    names[nm] = s["id"]

sfx = [
    {"at": "L01.3", "kind": "sting", "db": -14},
    {"at": "L01.3", "kind": "thud", "db": -9},
    {"at": "L09.1", "kind": "click", "db": -16},
    {"at": "L09.1+0.47", "kind": "click", "db": -16},
    {"at": "L40.2+0.3", "kind": "sting", "db": -10},
]
music = {
    "root": 46, "mode": "major", "bpm": 128, "seed": 114,
    "sections": [
        {"at": 0, "voices": ["pulse", "piano", "pad"], "energy": 0.62},
        {"at": "L11", "voices": ["piano", "pad"], "energy": 0.4},
        {"at": "L19", "voices": ["piano", "drone"], "energy": 0.36},
        {"at": "L21", "voices": ["drone", "choir"], "energy": 0.5, "root": 34, "mode": "minor"},
        {"at": "L28", "voices": ["drone", "pad"], "energy": 0.3, "root": 34, "mode": "minor"},
        {"at": "L37", "voices": ["pulse", "piano", "pad"], "energy": 0.78, "root": 46, "mode": "major"},
        {"at": "L41", "voices": ["pad", "drone"], "energy": 0.26},
        {"at": "L46", "voices": ["pulse", "piano", "pad"], "energy": 0.5},
    ],
}
sound = {
    "floor": "grass", "steps_db": -28,
    "ambience": [{"kind": "crickets", "from": "L19", "to": "L42", "lufs": -40},
                 {"kind": "hum", "from": "L41", "to": "L46", "lufs": -44}],
    "sfx": sfx,
    "music_drops": [{"from": "P01", "to": "P01>"}],
    "rev": REV,
}
remap_all(sfx)
remap_all(music["sections"])
remap_all(sound["music_drops"])
remap_all(sound["ambience"])
polish = {"reveal": [remap("L27")], "twist": remap("L28"),
          "emph": [remap(x) for x in ["L01.3", "L02", "L19", "L25.1", "L26.3", "L37", "L39.1"]],
          "quiet": [[remap("L43"), remap("L45")]],
          "hold": [names["scratch"], names["photo"], names["call"]]}
story = {
    "slug": "ep114-band-green",
    "title": "When the Band Plays, EVERYONE Dances",
    "made_for_kids": False,
    "premise": ("In a town where a band nobody knows plays on the green every Saturday and everyone has to dance, "
                "I'm the only one whose feet never move, since my best friend moved away."),
    "twist": ("The band plays for the saddest person in town and won't stop until they dance, so the whole town, my "
              "grandpa's sore knees included, has been dancing all summer because I wouldn't; when I finally stand up "
              "and dance, the song ends."),
    "world": ("A square town green with a white bandstand, string lights, iron benches and painted shops: a bank, a "
              "bakery, a post office, a clock tower, a moving truck on the road."),
    "voice": {"voice": "am_adam", "tempo": 1.03, "rate": 1.45},
    "key_color": "#4fc45a",
    "gap": 0.12,
    "tail": 0.25,
    "fade_in": False,
    "fade_out": False,
    "rev": REV,
    "look": {"style": "closer", "fog": "#cfd8e8", "fog_density": 0.002, "fog_start": 40.0, "sky": "#ffc89a",
             "sky_strength": 1.0, "exposure": 0.1, "flash_safe": True, "polish": polish},
    "grade": {"shadows": [0.0, 0.0, 0.03], "highlights": [0.03, 0.012, -0.02], "saturation": 1.1, "contrast": 1.05,
              "vignette": 0.2, "bloom": 0.25, "grain": 0.008},
    "phonemes": {"Benny": "bˈɛni"},
    "cast": cast,
    "lines": lines,
    "shots": shots,
    "acting": acting,
    "cues": cues,
    "fx": [],
    "music": music,
    "sound": sound,
    "set_moves": [],
}
OUT.write_text(json.dumps(story, indent=1, ensure_ascii=False) + "\n")
print("wrote", OUT, f"({len(shots)} shots, {len(cues)} cues)")
print(names)
