"""Writes ../story.json for ep139 "future dog" (script.md, 2026-11-12, batch 15). Run: python stories/ep139-future-dog/generator/make_story.py

The words are in lines.json; places are in ../layout.py (shared with set.py). A character facing -y has yaw 0,
+x 90, +y 180, -x -90. Cues are read by set.py's animate() (its header lists them).
Three scenes: the patio (gold evening, then the same patio at sunrise), the side street at 7:40 a.m. (x 60 to 110) and
two montage spots (x 200 and x 230). Nothing here blinks or glows; the one light change is a hard cut from evening to morning.
"""
import json
import math
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
sys.path.insert(0, str(HERE.parent.parent.parent))
import layout as G  # noqa: E402
from blocky import timeline as T  # noqa: E402

OUT = HERE.parent / "story.json"
REV = 4
orig_lines = json.loads((HERE / "lines.json").read_text())
lines, CHUNKMAP = T.split_lines(orig_lines)
# the 0.5 s music drop before L28
idx = next(i for i, l in enumerate(lines) if l["id"] == "L28")
lines.insert(idx, {"id": "P28", "pause": 0.5, "chunks": [["", ""]]})


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
X = {"neutral": "neutral", "uneasy": "worried", "stunned": "wide", "nervous": "worried", "smile": "smile", "laugh": "laugh",
     "warm": "warm", "sheepish": "sad-smile"}


def person(skin, shirt, pants, shoes, hair="cap", hair_c="#2a1d15", pattern="solid", pattern_c=None, hat="none",
           hat_c="#333333", extras=(), eyes="round", sleeves="short", brow_w=1.0, extra_c=None, **kw):
    d = {"age": "adult", "skin": skin, "shirt": shirt, "pattern": pattern, "pants": pants, "shoes": shoes,
         "sleeves": sleeves, "hair": hair, "hair_c": hair_c, "hat": hat, "hat_c": hat_c,
         "face": {"eyes": eyes, "brows": True, "ink": "#1c120c"}}
    if brow_w != 1.0:
        d["face"]["brow_w"] = brow_w
    if pattern_c:
        d["pattern_c"] = pattern_c
    if extras:
        d["extras"] = list(extras)
    if extra_c:
        d["extra_c"] = extra_c
    d.update(kw)
    return d


cast = {
    "me": person("#c98f64", "#e0a826", "#8a8f98", "#2aa6a0", hair="spiky", hair_c="#4a2f1c", brow_w=1.4),
    "theo": person("#c98f64", "#3f8a4e", "#3a4a63", "#5a4030", hair="cap", hair_c="#2a1b12", pattern="plaid",
                   pattern_c="#2d6a3a", sleeves="long", brow_w=1.6, width=1.06),
    "neighbor": person("#e2b088", "#4a78b8", "#4a4a5a", "#2a2a30", hair="long", hair_c="#3a2418", eyes="lashes",
                       sleeves="long", fringe="hard"),
    "sam": person("#b98456", "#f4f4f0", "#2f3a52", "#e8e4dc", hair="cap", hair_c="#1a1410", hat="ballcap",
                  hat_c="#2f5fb0"),
    "photo_theo": person("#c98f64", "#3f8a4e", "#3a4a63", "#5a4030", hair="cap", hair_c="#2a1b12", pattern="plaid",
                         pattern_c="#2d6a3a", sleeves="long", height=0.27),
}
acting = {n: [] for n in cast}
last = {n: [0, 0] for n in cast}
cues = []
SH = []


def key(who, at, pos=None, **kw):
    p = list(pos) if pos is not None else list(last[who])
    if "expr" in kw:
        kw["expr"] = X.get(kw["expr"], kw["expr"])
    acting[who].append({"at": at, "pos": p, **kw})
    last[who] = p


def cut(who, at, pos=None, **kw):
    """A key that takes effect at once (no blend): a pose or place that changes on a cut."""
    p = list(pos) if pos is not None else list(last[who])
    acting[who].append({"at": at, "pos": list(last[who]), "blend": 0.0})
    key(who, at, p, blend=0.0, **kw)


def mouth(who, a, b, amt=0.4):
    acting[who].append({"from": a, "to": b, "mouth": [amt, amt], "flap": True})


def cue(at, name, **kw):
    cues.append({"at": at, "name": name, **kw})


DOG = dict(x=0.0, y=-80.0, z=0.0, yaw=0.0, sit=0.0, lie=0.0, up=0.0, hy=0.0, hp=0.0, tongue=0.0, wag=0.0)


def dog(at, glide=False, dur=0.0, **kw):
    """A key on Noodle's track: all fields carry on from the key before unless given."""
    DOG.update(kw)
    c = {"at": at, "name": "dog", **DOG}
    if glide:
        c["glide"] = 1
    if dur:
        c["dur"] = dur
    cues.append(c)


def C(tx, ty, tz, w, az, lens=34, cz=None, push=None, up=0.0):
    """A camera looking at (tx, ty, tz) from az degrees round from the south, showing about w metres across at the target.
    push=(w2, tz2): a second key. cz: the camera's height (default level with the target)."""
    def at_(ww, tzz, czz):
        d = ww * lens / 13.5
        cx = tx + d * math.sin(az * D2R)
        cy = ty - d * math.cos(az * D2R)
        return [round(cx, 3), round(cy, 3), czz if czz is not None else tzz], [tx, ty, tzz]
    p, t_ = at_(w, tz, cz)
    keys = [[0, p, t_, lens]]
    if push:
        p2, t2 = at_(push[0], push[1], None if cz is None else cz + (push[1] - tz))
        keys.append([1, p2, t2, lens])
    return keys


def P2(pos, tgt, lens=34):
    """A camera at an exact place."""
    return [[0, list(pos), list(tgt), lens]]


def shot(sid, at, camera, **kw):
    SH.append((sid, at, camera, kw))


ME = (G.ME_SEAT[0], G.ME_SEAT[1], -0.22)     # seated on the chair
MEX, MEY = G.ME_SEAT
PHX, PHY, PHZ = G.PHONE


def mecam(w=1.7, az=0, lens=34, dx=-0.3, tz=1.25, cz=None, push=None):
    return C(MEX + dx, MEY, tz, w, az, lens, cz=cz, push=push)


def phonecam(w=0.9, az=0, lens=34, dx=0.0, dy=0.0, cz=1.1, push=None, tz=0.8):
    return C(PHX + dx, PHY + dy, tz, w, az, lens, cz=cz, push=push)


# --------------------------------------------------------------------------------------------- the cast at rest
key("me", 0, ME, yaw=0, expr="neutral", head=[0, 0], arms=[35, 35], side=[0, 0], lean=0)
cue(0, "sit_me", s=1.0)
key("theo", 0, (G.THEO_AT[0] + G.ST * 0 + 0, G.THEO_AT[1]), yaw=0, expr="nervous", arms=[0, 0], side=[0, 0], head=[0, 0])
key("neighbor", 0, (G.NEIGH[0], G.NEIGH[1] + 2.95, 0.18), yaw=0, expr="sheepish", arms=[0, 0], side=[0, 0])
key("sam", 0, (G.SAM[0] - 0.4, G.SAM[1] + 1.0), yaw=0, expr="sheepish", arms=[10, 10], side=[0, 0])
key("photo_theo", 0, (G.PHOTO[0] - 0.14, G.PHOTO[1] - 0.035, G.TABLE_Z + 0.03), yaw=0, expr="smile", arms=[0, 0], side=[0, 0])

# the rule meter: "1" at once; the timer from L14 (05:40 at L21, 06:00 at L22); the big digit comes back as "0" at L23
cue(0, "timer", mode=0.0, s=0.0, big=1.0)
cue("L14", "timer", mode=1.0, s=0.0)
cue("L13.2", "tap", p=0.0)
cue("L13.2+0.9", "tap", p=1.0, dur=0.25)
cue("L14.2", "tap", p=0.0, dur=0.3)
for ln, sec in (("L16", 95), ("L17", 150), ("L18", 200), ("L19", 245), ("L21", 340), ("L22", 360)):
    cue(ln, "timer", mode=1.0, s=float(sec), dur=0.5)
cue("L23", "timer", mode=0.0, s=360.0, big=0.0)
cue(0, "clock", on=0.0, h=7.0, m=38.0)
cue("P28", "clock", on=1.0, h=7.0, m=38.0)
cue("L29", "clock", on=1.0, h=7.0, m=39.0)
cue("L30", "clock", on=1.0, h=7.0, m=40.0)
# the phone: home screen; rings (soft) at L01 and L13; the call screen stays through the call; home again at the click
cue(0, "phone", mode=0.0, buzz=0.0)
cue("L01.2", "phone", mode=1.0, buzz=1.0)
cue("L01.4", "phone", mode=0.0, buzz=0.0)
cue("L13", "phone", mode=1.0, buzz=1.0)
cue("L14", "phone", mode=1.0, buzz=0.0)
cue("L23", "phone", mode=0.0, buzz=0.0)
cue(0, "gate", open=0.0, latch=0.0)
cue(0, "leash", on=0.0)
cue(0, "steam", on=0.0)
cue(0, "tap", p=0.0)
for sn in ("L07", "L19.1", "L21.2", "L29.3", "L38", "L42", "L48"):
    cue(sn, "achoo")

# --------------------------------------------------------------------------------------------- 01 the rule (L01, L02)
dog(0, x=G.CHAIR2[0], y=G.CHAIR2[1], z=G.SEAT_H, yaw=0, sit=1.0, hy=30.0, tongue=0.0)
shot("S01a", 0, [[0, [-0.45, -0.1, 0.95], [-0.35, 2.4, 1.12], 34], [1, [-0.42, 0.2, 0.95], [-0.35, 2.4, 1.14], 34]])
mouth("me", 0, "L01.2", 0.35)
shot("S01b", "L01.2", [[0, [-0.35, 0.8, 0.95], [-0.2, 2.4, 1.22], 34], [1, [-0.32, 0.95, 0.97], [-0.2, 2.4, 1.25], 34]])
mouth("me", "L01.2", "L01.4", 0.35)
shot("S01c", "L01.4", C(G.CHAIR2[0] + 0.3, G.CHAIR2[1], 0.8, 1.5, 0, 34, cz=1.0))
key("me", "L02", head=[0, 10], expr="uneasy", blend=0.6)
mouth("me", "L02", "L02>", 0.35)
shot("S02", "L02", mecam(1.55, 6, 34, dx=-0.2, tz=1.25, cz=1.45, push=(1.35, 1.25)))

# --------------------------------------------------------------------------------------------- 02 the rule at work (L03 to L04)
NX, NY = G.NEIGH
shot("S03", "L03", C(NX, NY + 2.95, 1.6, 1.9, 8, 32, cz=1.7))
key("neighbor", "L03", expr="sheepish", arms=[0, 150], blend=0.5)
SX, SY = G.SAM
shot("S04a", "L04", C(SX + 0.15, SY + 1.3, 1.2, 2.5, -10, 30, cz=1.4, push=(2.1, 1.2)))
key("sam", "L04", expr="sheepish", arms=[10, 10])
cue("L04.3", "steam", on=1.0)
shot("S04b", "L04.4", C(SX + 1.7, SY + 0.9, 1.1, 3.2, -35, 30, cz=1.4))
cut("sam", "L04.4", (SX + 0.9, SY + 0.7), yaw=-35, expr="sheepish", arms=[10, 10])

# --------------------------------------------------------------------------------------------- 03 the patio, the sneeze (L05 to L11)
cut("me", "L05", ME, yaw=0, expr="neutral", head=[0, 0], arms=[35, 35])
dog("L05", x=G.NOODLE_UNDER[0], y=G.NOODLE_UNDER[1], z=0.0, yaw=0, sit=0.0, hy=0.0, tongue=0.0)
shot("S05", "L05", C(-0.2, 1.9, 1.0, 3.3, 8, 30, cz=1.55))
shot("S05b", "L05.1", mecam(1.4, 0, 34, dx=-0.25, tz=1.27, cz=1.5))
mouth("me", "L05.1", "L05>", 0.35)
shot("S07", "L07", C(G.NOODLE_UNDER[0], G.NOODLE_UNDER[1], 0.35, 1.1, 5, 34, cz=0.55))
dog("L08", sit=0.0, tongue=1.0)
shot("S08", "L08", C(G.NOODLE_UNDER[0], G.NOODLE_UNDER[1], 0.36, 1.1, 0, 34, cz=0.5, push=(0.95, 0.36)))
key("me", "L09", expr="smile", head=[0, -4])
mouth("me", "L09", "L09>", 0.35)
shot("S09", "L09", mecam(1.45, 0, 34, dx=-0.25, tz=1.27, cz=1.5))
dog("L09.2", tongue=0.0)
mouth("me", "L10", "L10>", 0.3)
shot("S10a", "L10", C(G.PHOTO[0] - 0.06, G.PHOTO[1] - 0.1, 1.12, 0.5, 0, 34, cz=1.12, push=(0.36, 1.14)))
key("me", "L10.1", expr="warm", head=[10, 12], blend=0.5)
shot("S10b", "L10.1", mecam(1.35, 0, 34, dx=-0.25, tz=1.27, cz=1.5))
shot("S11", "L11", C(G.PHOTO[0] - 0.1, G.PHOTO[1] - 0.1, 1.1, 0.7, 0, 34, cz=1.1, push=(0.45, 1.12)))
key("me", "L11", expr="warm")

# --------------------------------------------------------------------------------------------- 04 texting, the call (L12 to L15)
dog("L12.2", x=G.NOODLE_UNDER[0], y=G.NOODLE_UNDER[1], z=0.0, sit=0.0, yaw=0)
dog("L12.2+0.4", glide=True, x=-0.8, y=1.2, z=0.3, sit=0.0, yaw=-60)
dog("L13", glide=True, x=G.CHAIR2[0], y=G.CHAIR2[1], z=G.SEAT_H, sit=1.0, yaw=90, hy=0.0)
shot("S12a", "L12", phonecam(0.32, 0, 34, dx=0.0, dy=0.0, cz=0.95, tz=0.74, push=(0.26, 0.74)))
key("me", "L12.2", expr="sheepish", head=[0, 8])
shot("S12b", "L12.2", mecam(1.45, 0, 34, dx=-0.25, tz=1.27, cz=1.5))
shot("S13a", "L13", P2((0.7, 1.45, 0.95), (-0.45, 1.7, 0.76), 34))
key("me", "L13.2", expr="stunned", head=[0, 0])
shot("S13b", "L13.2", mecam(1.4, 0, 34, dx=-0.25, tz=1.27, cz=1.5))
key("me", "L14", pos=ME, arms=[35, 78], lean=14, blend=0.4)
key("me", "L14.2", arms=[35, 35], lean=0, blend=0.5)
shot("S14a", "L14", P2((-0.12, 1.15, 0.98), (-0.45, 1.72, 0.76), 34))
key("me", "L14.2", expr="neutral")
shot("S14b", "L14.2", mecam(1.4, 0, 34, dx=-0.25, tz=1.27, cz=1.5))

# --------------------------------------------------------------------------------------------- 05 Noodle and the phone (L16 to L22)
dog("L16", dur=0.5, yaw=90, hy=0.0)
shot("S16", "L16", C(-0.5, 1.5, 0.45, 2.4, 6, 32, cz=0.95))
dog("L17", hy=34.0, hp=14.0, dur=0.6)
shot("S17", "L17", C(G.CHAIR2[0] + 0.25, G.CHAIR2[1], 0.85, 1.4, 0, 34, cz=1.0, push=(1.2, 0.85)))
dog("L17.2", hy=24.0, hp=-8.0, dur=0.8)
shot("S18", "L18", P2((0.75, 1.3, 1.05), (-0.85, 1.5, 1.1), 34))
dog("L19", dur=0.5, yaw=0, hy=28.0, hp=0.0)
shot("S19", "L19", C(G.CHAIR2[0] + 0.15, G.CHAIR2[1], 1.05, 1.4, 12, 34, cz=1.05))
key("me", "L21", expr="stunned")
shot("S21a", "L21", C(G.CHAIR2[0] + 0.15, G.CHAIR2[1], 1.05, 1.4, -12, 34, cz=1.05))
shot("S21b", "L21.2", C(G.CHAIR2[0] + 0.1, G.CHAIR2[1], 1.05, 1.3, 6, 34, cz=1.05))
key("me", "L22", expr="neutral", head=[-14, 4], blend=1.0)
shot("S22", "L22", mecam(1.5, 8, 34, dx=-0.2, tz=1.25, cz=1.45, push=(1.3, 1.25)))

# --------------------------------------------------------------------------------------------- 06 the click, the gate (L23 to L27)
dog("L23", dur=0.4, yaw=90, hy=0.0, hp=4.0)
shot("S23", "L23", P2((0.6, 1.25, 1.0), (-0.9, 1.55, 1.08), 34))
key("me", "L24", expr="uneasy", head=[0, 0], blend=0.5)
mouth("me", "L24", "L24>", 0.35)
shot("S24", "L24", mecam(1.35, 0, 34, dx=-0.25, tz=1.27, cz=1.5))
dog("L25", dur=0.4, yaw=0, hy=62.0, hp=0.0)
shot("S25", "L25", C(G.CHAIR2[0] + 0.15, G.CHAIR2[1], 1.05, 1.5, 14, 34, cz=1.05))
GX, GY = G.NOODLE_LIE
dog("L26", x=2.05, y=0.9, z=0.0, yaw=90, sit=0.0, lie=0.7, hy=0.0, hp=0.0)
shot("S26", "L26", C(2.6, 0.85, 0.35, 1.5, -50, 34, cz=0.5))
dog("L27", hp=14.0, dur=0.5)
shot("S27", "L27", C(2.7, 0.9, 0.3, 1.25, -25, 34, cz=0.4))
shot("S27d", "P28", C(G.GATE_X - 0.1, 0.9, 0.7, 1.9, -78, 32, cz=1.0))

# --------------------------------------------------------------------------------------------- 07 the morning, the run (L28 to L32)
dog("L28", x=2.35, y=0.95, z=0.0, yaw=55, sit=0.0, lie=0.0, hy=0.0, hp=-6.0)
shot("S28a", "L28", C(2.55, 0.95, 0.38, 1.5, -10, 34, cz=0.7))
cut("me", "L28.1", (G.DOOR_ME[0], G.DOOR_ME[1]), yaw=0, expr="uneasy", head=[0, 6], arms=[0, 0])
cue("L28.1", "sit_me", s=0.0)
shot("S28b", "L28.1", C(G.DOOR_ME[0], G.DOOR_ME[1], 1.35, 1.6, 0, 34, cz=1.55))
dog("L29", x=2.3, y=0.68, z=0.0, yaw=90, lie=0.0, hp=-4.0, hy=0.0)
dog("L29.2", dur=0.5, hp=-30.0)
cue("L29.2", "gate", latch=0.0)
cue("L29.2+0.1", "gate", latch=1.0, dur=0.4)
shot("S29a", "L29", C(2.85, 0.62, 0.5, 0.95, -35, 34, cz=0.55))
shot("S29b", "L29.3", C(2.85, 0.6, 0.45, 1.5, -40, 34, cz=0.6))
cue("L29.3", "gate", open=1.0, latch=1.0, dur=0.9)
dog("L30", x=2.32, y=0.52, z=0.0, yaw=90, hp=-16.0, hy=0.0)
cue("L30", "leash", on=1.0, arm=60.0)
cut("me", "L30", (1.1, 0.9), yaw=90, expr="uneasy", head=[0, 0], arms=[0, 60])
cue("L30", "sit_me", s=0.0)
shot("S30a", "L30", P2((2.45, -0.95, 0.9), (2.7, 0.52, 0.5), 34))
dog("L30.1", glide=True, x=2.7, y=0.9, yaw=90, hp=0.0)
dog("L30.1+1.0", glide=True, x=5.6, y=0.9, yaw=90, hp=0.0)
shot("S30b", "L30.1", C(3.6, 0.9, 0.5, 2.8, -40, 34, cz=0.9))

# the street: me and Noodle along the sidewalk toward the van (+x), the leash out ahead
STX = G.ST
cue("L31", "leash", on=1.0, arm=75.0)
cut("me", "L31", (70.0, 0.2), yaw=90, expr="stunned", head=[0, 0], arms=[0, 70], side=[0, 0], lean=0)
cue("L31", "sit_me", s=0.0)
key("me", "L31.2", (74.5, 0.2), yaw=90, expr="stunned")
dog("L31", x=71.8, y=0.2, z=0.0, yaw=90, sit=0.0, lie=0.0, hy=0.0, hp=0.0, tongue=1.0, wag=1.0)
dog("L31.2", glide=True, x=76.3, y=0.2, yaw=90)
shot("S31a", "L31", C(72.3, 0.2, 1.25, 1.85, 90, 32, cz=1.3))
shot("S31b", "L31.2", C(75.6, 0.2, 0.75, 1.7, 62, 34, cz=0.5))
key("me", "L32", (77.0, 0.2), yaw=90)
key("me", "L32.1", (80.8, 0.2), yaw=90)
dog("L32", x=79.5, y=0.2, yaw=90)
dog("L32.1", glide=True, x=82.6, y=-0.3, yaw=90)
shot("S32", "L32", P2((72.0, -7.6, 2.4), (84.0, 1.0, 1.4), 28))

# --------------------------------------------------------------------------------------------- 08 Theo (L33 to L39)
TX, TY = G.THEO_AT
cut("theo", "L33", (TX, TY), yaw=180, expr="nervous", head=[0, 0], arms=[0, 0])
cut("me", "L33", (TX - 3.1, TY), yaw=0, expr="stunned", head=[0, 0], arms=[0, 0], side=[0, 0])
cue("L33", "leash", on=0.0)
dog("L33", x=TX - 1.6, y=TY - 0.9, z=0.0, yaw=0, sit=1.0, hy=0.0, hp=0.0, tongue=1.0, wag=0.0)
shot("S33a", "L33", P2((TX - 0.6, -5.6, 1.55), (TX + 0.5, 0.5, 1.15), 32))
key("theo", "L33.2", yaw=0, expr="stunned", blend=0.7)
shot("S33b", "L33.2", C(TX, TY, 1.3, 1.7, 0, 34, cz=1.45))
key("theo", "L34", expr="nervous")
shot("S34", "L34", C(TX, TY, 1.3, 1.45, 4, 34, cz=1.45))
shot("S35", "L35", C(TX - 3.1, TY, 1.3, 1.5, 0, 34, cz=1.45))
mouth("me", "L35", "L35>", 0.35)
key("theo", "L37", expr="sheepish", head=[-20, 4], blend=0.6)
shot("S37", "L37", C(TX, TY, 1.3, 1.45, 6, 34, cz=1.4))
shot("S38", "L38", C(TX - 0.6, TY - 0.8, 0.4, 1.1, 0, 34, cz=0.65))
dog("L38", x=TX - 0.6, y=TY - 0.8, yaw=0, sit=1.0)
key("theo", "L37.2", expr="nervous", arms=[0, 0], side=[20, 20], head=[0, 0], blend=0.6)

# --------------------------------------------------------------------------------------------- 09 the hug (L40 to L43)
# Theo kneels; Noodle hops into his arms and sits between them, Theo's arms round him from behind (all face the camera)
HUG = (TX, TY - 0.62)
cue("L40", "squat_theo", s=1.0, dur=0.6)
key("theo", "L40", (TX, TY, -0.32), yaw=0, expr="smile", arms=[34, 34], side=[0, 0], head=[0, 8], blend=0.6)
key("theo", "L40+0.8", arms=[70, 70], side=[-50, -50], expr="smile", blend=0.4)
dog("L40", glide=False, x=TX - 0.6, y=TY - 0.8, z=0.0, sit=1.0, yaw=0)
dog("L40+0.2", glide=True, x=TX - 0.3, y=TY - 0.95, z=0.4, sit=0.0, up=0.0, yaw=0, hp=-8.0)
dog("L40+0.65", glide=True, x=HUG[0], y=HUG[1], z=0.0, sit=1.0, up=0.0, yaw=0, hp=0.0, tongue=1.0, wag=1.0)
shot("S40", "L40", C(TX - 0.2, TY - 0.4, 0.85, 2.0, 0, 34, cz=1.0))
key("theo", "L41", expr="smile")
mouth("theo", "L41", "L41>", 0.25)
shot("S41", "L41", C(TX, TY - 0.2, 0.95, 1.45, 4, 34, cz=1.05))
shot("S42", "L42", C(TX - 0.1, TY - 0.5, 0.75, 1.5, -6, 34, cz=0.9))
key("theo", "L43", expr="laugh")
cut("me", "L43", (TX - 0.95, TY), yaw=0, expr="laugh", head=[0, 0], arms=[0, 0], side=[0, 0])
key("me", "L43.2", (TX - 0.95, TY), expr="laugh", side=[62, 0], blend=0.6)
shot("S43", "L43", C(TX - 0.35, TY - 0.2, 1.1, 1.9, 0, 34, cz=1.3))

# --------------------------------------------------------------------------------------------- 10 the coffee walk (L46, L48)
HX, HY = G.HOUSE
cue("L46", "squat_theo", s=0.0)
cut("theo", "L46", (HX + 0.55, G.PORCH_Y, 0.3), yaw=0, expr="smile", arms=[0, 0], side=[0, 0], head=[0, 0])
cut("me", "L46", (HX - 0.55, G.PORCH_Y, 0.3), yaw=0, expr="smile", arms=[0, 0], side=[0, 0], head=[0, 0])
dog("L46", glide=False, x=HX, y=G.PORCH_Y - 1.1, z=0.26, sit=1.0, up=0.0, yaw=0, hp=0.0, tongue=1.0, wag=1.0)
cue("L46", "leash", on=0.0)
shot("S46", "L46", C(HX, G.PORCH_Y, 1.55, 2.0, 0, 32, cz=1.55))
shot("S48", "L48", C(HX - 0.25, G.PORCH_Y - 1.1, 0.75, 1.2, 0, 34, cz=0.75))

# --------------------------------------------------------------------------------------------- 11 the reveal (L44)
cue("L44", "squat_theo", s=1.0, dur=0.1)
cut("theo", "L44", (TX, TY, -0.32), yaw=0, expr="laugh", arms=[70, 70], side=[-50, -50], head=[0, 6])
dog("L44", glide=False, x=HUG[0], y=HUG[1], z=0.0, sit=1.0, up=0.0, yaw=0, hp=0.0, tongue=1.0, wag=1.0)
cut("me", "L44", (TX - 0.95, TY), yaw=0, expr="warm", head=[0, 0], arms=[0, 0], side=[0, 0])
shot("S44a", "L44", C(TX - 0.35, TY - 0.2, 1.1, 1.9, 0, 34, cz=1.3))
cut("me", "L44.2", (TX + 0.95, TY + 0.9), yaw=0, expr="warm", head=[0, 0], arms=[0, 0], side=[0, 0])
shot("S44b", "L44.2", C(TX + 0.45, TY - 0.3, 1.1, 1.9, 0, 34, cz=1.2))
cut("me", "L44.5", (TX + 2.2, TY + 0.9), yaw=0, expr="warm", head=[0, 0], arms=[0, 0], side=[0, 0])
shot("S44c", "L44.5", C(TX + 0.2, TY - 0.7, 0.8, 1.5, 4, 34, cz=0.95))

# --------------------------------------------------------------------------------------------- 12 home (L49)
cue("L49", "sit_me", s=1.0)
cut("me", "L49", ME, yaw=0, expr="warm", head=[0, 0], arms=[35, 35], side=[0, 0], lean=0)
dog("L49", x=G.CHAIR2[0], y=G.CHAIR2[1], z=G.SEAT_H, sit=1.0, hy=30.0, wag=0.0, tongue=0.0)
shot("S49", "L49", [[0, [-0.45, -0.1, 0.95], [-0.35, 2.4, 1.12], 34], [1, [-0.42, 0.2, 0.95], [-0.35, 2.4, 1.14], 34]])

# ----------------------------------------------------------------------------------------------- finish
remap_all(cues)
for k_ in acting.values():
    remap_all(k_)
shots, names = [], {}
for i, (sid, at, camera, kw) in enumerate(SH):
    s = {"id": sid, "cam": camera, "step": 2}
    if i:
        s["at"] = remap(at)
    s.update({k: v for k, v in kw.items() if not k.startswith("_")})
    shots.append(s)

sfx = [
    {"at": "L01.2", "kind": "thud", "db": -26, "dur": 0.2},
    {"at": "L13", "kind": "thud", "db": -26, "dur": 0.2},
    {"at": "L07", "kind": "puff", "db": -22},
    {"at": "L19.1", "kind": "puff", "db": -22},
    {"at": "L21.2", "kind": "puff", "db": -22},
    {"at": "L29.3", "kind": "puff", "db": -22},
    {"at": "L38", "kind": "puff", "db": -22},
    {"at": "L42", "kind": "puff", "db": -22},
    {"at": "L48", "kind": "puff", "db": -22},
    {"at": "L23.1", "kind": "click", "db": -16},
    {"at": "L29.2+0.2", "kind": "latch", "db": -20},
    {"at": "L30+0.5", "kind": "thud", "db": -26, "dur": 0.2},
    {"at": "L33", "kind": "rattle", "db": -28},
]
music = {
    "root": 53, "mode": "major", "bpm": 104, "seed": 139,
    "sections": [
        {"at": 0, "voices": ["piano", "musicbox"], "energy": 0.42},
        {"at": "L23", "voices": ["drone"], "energy": 0.12},
        {"at": "P28", "voices": ["pulse", "piano"], "energy": 0.5},
        {"at": "L33", "voices": ["pad"], "energy": 0.16},
        {"at": "L40", "voices": ["piano", "musicbox", "pad"], "energy": 0.52},
        {"at": "L49", "voices": ["piano", "pad"], "energy": 0.3},
    ],
}
sound = {
    "floor": "concrete", "steps_db": -26,
    "sfx": sfx,
    "music_drops": [{"from": "P28", "to": "P28>", "keep": ["latch"]}],
    "ambience": [{"kind": "crickets", "from": 0, "to": "L28", "lufs": -46}],
    "rev": REV,
}
remap_all(sfx)
remap_all(music["sections"])
remap_all(sound["music_drops"])
sound["ambience"][0]["to"] = "P28"
polish = {"reveal": [remap("L44.2")], "twist": remap("L44.2"),
          "emph": [remap(x) for x in ["L01.3", "L01.5", "L13.2", "L23.1", "L30", "L34", "L44.4"]],
          "quiet": [[remap("L41"), remap("L43")]],
          "hold": ["S44b", "S01a", "S10a", "S11", "S49"], "ones": "all"}
story = {
    "slug": "ep139-future-dog",
    "title": "Future Me Only Called My DOG 🐕",
    "made_for_kids": False,
    "premise": ("On your thirtieth birthday your future self phones you once, and mine spent the whole call telling my "
                "beagle two words: Gate. Seven-forty."),
    "twist": ("Future me knew I'd overthink it for a week, so he told the one of us who never does: at 7:40 the next "
              "morning Noodle led me to my big brother Theo, back from across the ocean and too nervous to knock."),
    "world": ("A gold-lit ground-floor apartment patio with a brick wall, a low white fence and a side gate, then a leafy "
              "side street at 7:40 a.m. with a plain white moving van and a yellow house."),
    "voice": {"voice": "am_adam", "tempo": 1.03, "rate": 1.45},
    "key_color": "#ff5a4f",
    "gap": 0.15,
    "tail": 0.0,
    "fade_in": False,
    "fade_out": False,
    "rev": REV,
    "look": {"style": "closer", "fog": "#f4e8d4", "fog_density": 0.001, "fog_start": 60.0, "sky": "#ffe0b0",
             "sky_strength": 1.0, "exposure": 0.05, "flash_safe": True, "polish": polish},
    "grade": {"shadows": [0.0, 0.0, 0.02], "highlights": [0.03, 0.012, -0.02], "saturation": 1.06, "contrast": 1.03,
              "vignette": 0.12, "bloom": 0.12, "grain": 0.008},
    "hud": {"object": "tag", "at": [-0.5, 0.62], "size": 0.46},
    "phonemes": {"achoo": "ɑːtʃˈuː", "nosed": "nˈOzd"},
    "asr_forgive": ["nosed", "thirtieth", "sam's", "future me", "seven forty", "seven thirty eight", "seven thirty nine"],
    "cast": cast,
    "lines": lines,
    "shots": shots,
    "acting": acting,
    "cues": cues,
    "fx": [],
    "music": music,
    "sound": sound,
    "set_moves": [],
    "frames_ok": ["S25", "S40", "S44b"],
    "staging_ok": ["S43/me+theo touch on purpose (my hand to his shoulder)", "S44a/me+theo touch on purpose", "S46/me+theo stand close on purpose (coffee on the porch)", "S48/me+theo stand close on purpose (same pose, Noodle close-up)"],
    "framing_ok": ["S04b", "S07", "S08", "S10b", "S14b", "S17", "S31b", "S35", "S38", "S48", "S14a", "S10a"],
    "clip_ok": ["photo"],
}
OUT.write_text(json.dumps(story, indent=1, ensure_ascii=False) + "\n")
print("wrote", OUT, f"({len(shots)} shots, {len(cues)} cues)")
