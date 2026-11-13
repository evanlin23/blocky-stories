"""Writes ../story.json for ep147 "Room Six Came With a Man in the CLOSET" (script.md, 2026-11-12, batch 15, eerie lane).
Run: python stories/ep147-motel-reviews/generator/make_story.py

Words are in lines.json; places in ../layout.py (shared with set.py). A character facing -y has yaw 0, +x 90,
+y 180, -x -90. Style v3 (the pilot). Cues (read by set.py): stars (the rule card's filled stars, 1..5), card (the card
a hand holds: mode none | hand | desk, who, kind ours | old | mine | last), pen, key (mode none | desk), shirts, shirt
(mode none | hand), drawer, closet (the doors, 0 shut .. 1 open), win (the window: 1 day, 0 night, 0.55 dawn).
Nothing ever blinks or pulses: every light rises over at least 0.3 s.
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
REV = 15
orig_lines = json.loads((HERE / "lines.json").read_text())
lines, CHUNKMAP = T.split_lines(orig_lines)


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


def person(skin, shirt, pants, shoes, hair, hair_c, features=(), hair_c2=None, eyes="round", sleeves="short", **kw):
    d = {"age": "adult", "skin": skin, "shirt": shirt, "pants": pants, "shoes": shoes, "sleeves": sleeves,
         "hair": hair, "hair_c": hair_c, "hat": "none", "face": {"eyes": eyes, "brows": True, "ink": "#1c120c"}}
    if features:
        d["features"] = list(features)
    if hair_c2:
        d["hair_c2"] = hair_c2
    d.update(kw)
    return d


cast = {
    # me, 21: a tall brown quiff (the loud silhouette), a teal road-trip T-shirt
    "me": person("#e3b088", "#2ec4b6", "#6b5b46", "#f2f2f2", "quiff", "#6b3f22", features=["beard"], height=1.08),
    # Dad, about 52: a wide gray-brown flat-top and a giant walrus mustache, a pineapple-yellow aloha shirt
    "dad": person("#c98f63", "#ffb02e", "#e8dcc0", "#8a6a48", "shag", "#6e6458", features=["dadstache", "shades"],
                  hair_c2="#1a1a22", pattern="stripes", pattern_c="#ff7a2e", head_scale=1.04, width=1.04),
    # the closet man, looks about 40: very neat black hair with a side part, ears and a nape (set.py swaps the "buzz"
    # silhouette for it in this story), a charcoal suit, gray tie
    "man": person("#e8c8a8", "#5b6170", "#4b505e", "#15151a", "buzz", "#0f0e16", hair_c2="#e8c8a8", sleeves="long",
                  extras=["tie"], extra_c="#8d93a3", collar="#f4f4f4", body_width=0.94),
    # the clerk, about 60: bald, big red reading-glasses frames, a mint motel shirt
    "clerk": person("#e8c4a0", "#7fe0c4", "#8a7c66", "#8a6a48", "bald", "#e8573a", features=["glasses"],
                    hair_c2="#e8573a"),
}
acting = {n: [] for n in cast}
last = {n: [0, 0, 0] for n in cast}
vis = set()
cues = []
SH = []


def key(who, at, pos=None, **kw):
    p = list(pos) if pos is not None else list(last[who])
    if len(p) == 2:
        p.append(0.0)
    acting[who].append({"at": at, "pos": p, **kw})
    last[who] = p


def cut(who, at, pos=None, **kw):
    """A key that takes effect at once: a pose or place that changes on a cut."""
    p = list(pos) if pos is not None else list(last[who])
    if len(p) == 2:
        p.append(0.0)
    acting[who].append({"at": at, "pos": list(last[who]), "blend": 0.0})
    key(who, at, p, blend=0.0, **kw)


def show(at, *names):
    for n in cast:
        if n in names and n not in vis:
            vis.add(n)
            cut(n, at, hidden=False)
        elif n not in names and n in vis:
            vis.discard(n)
            cut(n, at, hidden=True)


def pose(yaw=0, expr="neutral", **kw):
    d = dict(yaw=yaw, expr=expr, head=[0, 0], arms=[0, 0], side=[0, 0])
    d.update(kw)
    return d


def place(at, who, pos, yaw=0, expr="neutral", **kw):
    if who not in vis:
        vis.add(who)
        cut(who, at, hidden=False)
    cut(who, at, [pos[0], pos[1], pos[2] if len(pos) > 2 else 0.0], **pose(yaw, expr, **kw))


def mouth(who, a, b, amt=0.4):
    acting[who].append({"from": a, "to": b, "mouth": [amt, amt], "flap": True})


def cue(at, name, **kw):
    cues.append({"at": at, "name": name, **kw})


def cam(tx, ty, tz, w, az, lens, cz=None, push=None):
    """A camera looking at (tx, ty, tz) from az degrees round from the south, far enough off that the frame is w
    metres wide there."""
    def at_(ww, tzz, czz):
        d = ww * 16 / 9 * lens / 24
        return [round(tx + d * math.sin(az * D2R), 3), round(ty - d * math.cos(az * D2R), 3),
                czz if czz is not None else tzz], [tx, ty, tzz]
    p, t_ = at_(w, tz, cz)
    keys = [[0, p, t_, lens]]
    if push:
        w2 = w - (w - push[0]) * 2.2
        p2, t2 = at_(w2, push[1], None if cz is None else cz + (push[1] - tz))
        keys.append([1, p2, t2, lens])
    return keys


def camp(pos, tgt, lens, pos2=None, tgt2=None):
    keys = [[0, list(pos), list(tgt), lens]]
    if pos2 is not None or tgt2 is not None:
        keys.append([1, list(pos2 or pos), list(tgt2 or tgt), lens])
    return keys


def shot(sid, at, camera, **kw):
    SH.append((sid, at, camera, kw))


for who in cast:
    key(who, 0, [0, 0, 0], yaw=0, expr="neutral", head=[0, 0], arms=[0, 0], side=[0, 0], hidden=True)

# initial prop state
cue(0, "stars", n=5)
cue(0, "card", mode="none", who="me", kind="ours")
cue(0, "pen", mode="none", who="me")
cue(0, "key", mode="none")
cue(0, "shirts", v=0.0)
cue(0, "shirt", mode="none", who="dad")
cue(0, "drawer", v=0.0)
cue(0, "closet", v=0.0)
cue(0, "win", v=1.0)

MX, MY = G.ME_C
CLX = G.CLX
MAN0 = (G.MAN[0], G.MAN[1], 0.0)
ME_FACE = (MX + 0.3, MY, 1.55)       # target for a card + face shot of me


def me_c(at, expr="neutral", arms=(0, 86), yaw=0, **kw):
    place(at, "me", (MX, MY, 0.0), yaw, expr, arms=list(arms), **kw)
    if isinstance(at, str) and "head" not in kw:   # a small head turn and nod through the shot (the card shots were still)
        for dt, hd in ((0.4, [7, -3]), (0.85, [-5, 2])):
            key("me", f"{at}+{dt}", [MX, MY, 0.0], yaw=yaw, expr=expr, arms=list(arms), head=hd, blend=0.4)


# ===== 01 the rule (L01, L02)
show(0, "me")
me_c(0, "neutral")
cue(0, "card", mode="hand", who="me", kind="ours")
mouth("me", 0, "L01>", 0.35)
shot("S01a", 0, cam(*ME_FACE, 2.2, 0, 30, cz=1.55))
# S05 on "Room SIX": the two of us at the door, then back to the card
SOFF = 2.0
cue("L01.2", "card", mode="none", who="me", kind="ours")
show("L01.2", "me", "dad")
place("L01.2", "me", (G.EX - 0.72, G.EXT_WALK_Y, 0.0), 0, "delighted", arms=[0, 0])
place("L01.2", "dad", (G.EX + 0.72, G.EXT_WALK_Y, 0.0), 0, "delighted", arms=[0, 0])
shot("S05", "L01.2", cam(G.EX, G.EXT_WALK_Y, 1.5, 2.6, 0, 30, cz=1.45))
show("L01.3", "me")
me_c("L01.3", "neutral")
cue("L01.3", "card", mode="hand", who="me", kind="ours")
shot("S01b", "L01.3", cam(MX + 0.15, MY, 1.7, 2.4, 8, 30, cz=1.7))
# S02: the drawer of cards, pulled open
show("L02")
cue("L02", "drawer", v=1.0, dur=0.4)
cue("L02", "card", mode="none", who="me", kind="ours")
shot("S02", "L02", cam(G.DESK[0], 1.75, 0.9, 1.0, -8, 36, cz=2.4))

# ===== 02 the bucket joke (L04)
cue("L04", "drawer", v=0.0, dur=0.1)
show("L04")
shot("S04a", "L04", cam(*G.EXT_POOL, 0.5, 1.5, 8, 30, cz=0.7))
show("L04.2", "dad")
place("L04.2", "dad", (G.EXT_POOL[0] - 0.55, G.EXT_POOL[1] - 0.2, 0.0), 0, "crylaugh", arms=[0, 0], head=[0, 18])
shot("S04b", "L04.2", cam(G.EXT_POOL[0] - 0.4, G.EXT_POOL[1] - 0.2, 1.2, 3.2, -8, 28, cz=1.4))

# ===== 03 our card, the closet (L06, L07, L08)
cue("L06", "stars", n=5)
show("L06", "me")
me_c("L06", "nervous")
cue("L06", "card", mode="hand", who="me", kind="ours")
mouth("me", "L06", "L06>", 0.35)
shot("S06", "L06", cam(*ME_FACE, 2.2, -8, 30, cz=1.55))
cue("L06.2", "card", mode="none", who="me", kind="ours")
show("L06.2", "dad")
place("L06.2", "dad", (MX - 0.2, MY, 0.0), 0, "crylaugh", arms=[0, 0], head=[0, 6])
key("dad", "L06.2+0.5", [MX - 0.2, MY, 0.0], yaw=0, expr="crylaugh", arms=[0, 0], head=[-8, -6], blend=0.4)
shot("S06b", "L06.2", cam(MX - 0.2, MY, 1.7, 2.3, 10, 30, cz=1.7))
cue("L07", "card", mode="none", who="me", kind="ours")
cue("L07.1", "closet", v=1.0, dur=0.8)
show("L07", "dad")
place("L07", "dad", (0.55, 0.75, 0.0), 120, "crylaugh", arms=[0, 0], head=[-40, 0])
key("dad", "L07.2", [1.4, 1.4, 0.0], yaw=160, expr="crylaugh", arms=[0, 0], head=[-50, 0], blend=0.35)
key("dad", "L07.2+0.45", [1.4, 1.4, 0.0], yaw=160, expr="crylaugh", arms=[0, 52], head=[-50, 0], blend=0.35)
shot("S07", "L07", cam(1.4, 1.9, 1.5, 2.9, 28, 30, cz=1.5))
show("L08", "man")
place("L08", "man", MAN0, 180, "deadpan", arms=[0, 0])
shot("S08", "L08", cam(CLX, 3.1, 1.5, 2.6, 0, 30, cz=1.5, push=(2.1, 1.55)))
shot("S08b", "L08.2", cam(CLX, 3.1, 1.95, 1.9, 6, 34, cz=1.95))

# ===== 04 the clerk (L10)
show("L10", "clerk")
place("L10", "clerk", (G.CLERK[0] + 1.1, G.CLERK[1], 0.0), 0, "suspicious", arms=[0, 70])
shot("S10a", "L10", cam(G.OX + 0.3, 1.6, 1.4, 3.0, 0, 30, cz=1.4))
place("L10.2", "clerk", (G.OX + 1.1, G.CLERK[1], 0.0), 0, "suspicious", arms=[0, 70])
shot("S10b", "L10.2", cam(G.OX + 1.6, 1.6, 1.5, 2.7, 0, 32, cz=1.5))

# ===== 05 the morning (L13, L15)
cue("L13", "shirts", v=1.0)
show("L13")
shot("S13a", "L13", cam(G.DESK[0], 2.15, 0.9, 0.95, 6, 36, cz=2.9))
shot("S13b", "L13.3", cam(G.DESK[0] - 0.25, 2.2, 0.95, 0.7, 6, 40, cz=2.6))
show("L15", "man")
place("L15", "man", MAN0, 180, "deadpan", arms=[0, 0])
shot("S15", "L15", cam(CLX, 3.1, 1.35, 2.6, -14, 30, cz=1.35))

# ===== 06 the old card (L16, L17, L19)
cue("L16", "win", v=0.0, dur=0.4)
cue("L16", "drawer", v=1.0, dur=0.1)
show("L16", "me")
place("L16", "me", (-0.05, 1.3, 0.0), -35, "nervous", arms=[0, 74], head=[0, 14])
cue("L16", "card", mode="hand", who="me", kind="old")
mouth("me", "L16", "L16>", 0.35)
shot("S16", "L16", cam(0.1, 1.8, 1.55, 2.2, -20, 30, cz=1.55))
cue("L17", "drawer", v=0.0, dur=0.1)
me_c("L17", "nervous")
shot("S17a", "L17", cam(MX + 0.15, MY, 1.7, 2.4, 8, 30, cz=1.7))
me_c("L17.2", "terrified")
mouth("me", "L17.2", "L17>", 0.4)
shot("S17b", "L17.2", cam(MX + 0.15, MY, 1.65, 2.4, -8, 30, cz=1.65))
show("L19", "me")
me_c("L19", "shocked", yaw=0, head=[-30, 0])
shot("S19a", "L19", cam(MX + 0.05, MY, 1.55, 2.6, 6, 30, cz=1.55))
show("L19.1", "man")
place("L19.1", "man", MAN0, 180, "deadpan", arms=[0, 0])
shot("S19b", "L19.1", cam(CLX, 3.1, 1.4, 2.5, 22, 30, cz=1.4))

# ===== 07 the new card (L20, L21)
cue("L20", "closet", v=0.0, dur=0.0)
show("L20", "me")
me_c("L20", "determined", arms=[70, 86])
cue("L20", "card", mode="hand", who="me", kind="mine")
cue("L20", "pen", mode="hand", who="me")
mouth("me", "L20", "L20>", 0.35)
shot("S20", "L20", cam(MX + 0.15, MY, 1.55, 2.3, -6, 28, cz=1.55))
cue("L21", "pen", mode="none", who="me")
cue("L21", "pen", mode="hand", who="me")
place("L21", "me", (MX, MY, 0.0), 0, "determined", arms=[70, 86])
for k_, dt in enumerate((0.25, 0.5, 0.75, 1.0, 1.25, 1.5, 1.75, 2.0)):
    key("me", f"L21+{dt}", [MX, MY, 0.0], yaw=0, expr="determined", arms=[70, 86],
        head=[10, 4 if k_ % 2 else -4], blend=0.3)
shot("S21", "L21", cam(MX + 0.25, MY - 0.1, 1.2, 1.9, -8, 32, cz=1.2))

# ===== 08 the doors open (L22, L23, L24)
cue("L22", "win", v=0.55, dur=0.4)
cue("L22", "card", mode="none", who="me", kind="mine")
cue("L22", "pen", mode="none", who="me")
show("L22")
shot("S22", "L22", cam(CLX, 3.1, 1.4, 2.6, 24, 30, cz=1.4))
cue("L22.2", "closet", v=1.0, dur=0.8)
show("L22.2", "man")
place("L22.2", "man", MAN0, 180, "hollow", arms=[0, 0])
# L23: he steps out toward us, along the closet front, to the desk
S23 = [G.MAN[0], 1.5, 0.0]
key("man", "L23", S23, yaw=0, expr="hollow", arms=[0, 0], blend=0.25)
key("man", "L23.1", [G.MAN_DESK[0] - 0.2, 1.5, 0.0], yaw=-90, expr="hollow", arms=[0, 0], blend=0.4)
key("man", "L23.2", [G.MAN_DESK[0] - 0.2, 1.55, 0.0], yaw=180, expr="hollow", arms=[80, 80], blend=0.45)
shot("S23a", "L23", camp((0.2, -4.0, 1.4), (0.2, 1.9, 1.4), 30, (-0.8, -4.0, 1.4), (-0.8, 1.9, 1.4)))
cue("L23.2", "key", mode="desk", dur=0.1)
shot("S23b", "L23.2", cam(-0.2, 1.9, 1.15, 2.0, 0, 34, cz=1.15))
# L24: he turns, nods, walks to the door
MD = [G.MAN_DESK[0] - 0.2, 1.55, 0.0]
key("man", "L24-0.3", MD, yaw=180, expr="hollow", arms=[0, 0], blend=0.2)
key("man", "L24+0.4", MD, yaw=0, expr="hollow", arms=[0, 0], head=[0, 0], blend=0.7)
key("man", "L24.1-0.2", MD, yaw=0, expr="hollow", arms=[0, 0], head=[0, 22], blend=0.25)
key("man", "L24.1+0.2", MD, yaw=0, expr="hollow", arms=[0, 0], head=[0, 0], blend=0.25)
key("man", "P01-0.1", [1.5, 1.5, 0.0], yaw=90, expr="hollow", arms=[0, 0], blend=0.75)
shot("S24a", "L24", cam(MD[0], 1.55, 1.5, 1.8, 0, 34, cz=1.5))
show("L24.2", "me", "dad", "man")
place("L24.2", "me", (0.65, 0.2, 0.0), 0, "shocked", arms=[0, 0])
place("L24.2", "dad", (-0.85, 0.2, 0.0), 0, "awe", arms=[0, 0])
shot("S24b", "L24.2", cam(-0.1, 0.2, 1.55, 3.0, 0, 30, cz=1.5))
# the drop: the empty closet
show("P01")
cue("P01", "closet", v=1.0)
shot("S25", "P01", cam(CLX, 3.1, 1.35, 2.6, -10, 30, cz=1.35))

# ===== 09 the last card (L26, L28, L29)
cue("L26", "card", mode="hand", who="me", kind="last")
cue("L26", "key", mode="desk")
show("L26", "me")
place("L26", "me", (-1.3, 1.15, 0.0), 15, "nervous", arms=[0, 86])
shot("S26", "L26", cam(-0.65, 1.5, 1.45, 3.0, 4, 30, cz=1.45))
cue("L28", "stars", n=1)
show("L28", "me")
me_c("L28", "nervous")
cue("L28", "card", mode="hand", who="me", kind="last")
cue("L28", "key", mode="desk")
shot("S28a", "L28", cam(MX + 0.15, MY, 1.7, 2.4, 6, 30, cz=1.7))
me_c("L29", "terrified", arms=[0, 86])
mouth("me", "L29", "L29>", 0.4)
shot("S28b", "L29", cam(*ME_FACE, 2.2, -6, 30, cz=1.55))

# ===== 10 the loop line (L33)
cue("L33", "card", mode="none", who="me", kind="last")
cue("L33", "shirts", v=0.0)
cue("L33", "shirt", mode="hand", who="dad", f=0.0)
cue("L33.1", "shirt", f=1.0, dur=0.6)
cue("L33.2", "shirt", f=2.0, dur=0.6)
show("L33", "dad")
place("L33", "dad", (MX - 0.1, MY, 0.0), 0, "neutral", arms=[62, 62], head=[0, 0])
key("dad", "L33.1", [MX - 0.1, MY, 0.0], yaw=0, expr="neutral", arms=[50, 70], head=[8, 0], blend=0.3)
key("dad", "L33.1+0.4", [MX - 0.1, MY, 0.0], yaw=0, expr="neutral", arms=[62, 62], head=[8, 0], blend=0.3)
key("dad", "L33.2", [MX - 0.1, MY, 0.0], yaw=0, expr="neutral", arms=[70, 50], head=[8, 0], blend=0.3)
key("dad", "L33.2+0.4", [MX - 0.1, MY, 0.0], yaw=0, expr="neutral", arms=[62, 62], head=[8, 0], blend=0.3)
shot("S32", "L33", cam(MX - 0.1, MY, 1.5, 2.1, 0, 28, cz=1.5))
cue("L33.3", "shirt", mode="desk", who="dad", f=2.0)
cue("L33.3", "key", mode="none")
shot("S33", "L33.3", cam(G.DESK[0] + 0.15, 1.95, 1.0, 1.1, 0, 32, cz=1.0))

# ----------------------------------------------------------------------------------------------- finish
remap_all(cues)
for k_ in acting.values():
    remap_all(k_)
shots = []
for i, (sid, at, camera, kw) in enumerate(SH):
    if len(camera) == 1:       # a slow dolly in on every shot whose camera was still
        _, p0, t0, ln = camera[0]
        camera = camera + [[1, [round(p0[j] + 0.1 * (t0[j] - p0[j]), 3) for j in range(3)], list(t0), ln]]
    s = {"id": sid, "cam": camera, "step": 2}
    if i:
        s["at"] = remap(at)
    s.update({k: v for k, v in kw.items() if not k.startswith("_")})
    shots.append(s)

sfx = [
    {"at": "L10", "kind": "bell", "db": -12},
    {"at": "L22.3", "kind": "click", "db": -14},
    {"at": "P01", "kind": "door", "db": -16},
]
music = {
    "root": 69, "mode": "minor", "bpm": 88, "seed": 147,
    "sections": [
        {"at": 0, "voices": ["bass", "vibes"], "energy": 0.4},
        {"at": "L08", "voices": ["bass", "vibes", "drone"], "energy": 0.45},
        {"at": "L16", "voices": ["drone", "pad"], "energy": 0.4},
        {"at": "L22", "voices": ["bass", "drone", "vibes"], "energy": 0.55},
        {"at": "L26", "voices": ["drone", "pad"], "energy": 0.4},
    ],
}
sound = {
    "floor": "wood", "steps_db": -22,
    "ambience": [{"kind": "hum", "from": "L01", "to": "L33>", "lufs": -44}],
    "sfx": sfx,
    "music_drops": [{"from": "P01", "to": "P01>"}],
    "rev": REV,
}
remap_all(sfx)
remap_all(music["sections"])
remap_all(sound["ambience"])
remap_all(sound["music_drops"])
polish = {"overlap": True, "turn_cap": 220, "punch_max": 4, "sharpen": 0.4, "bloom_thresh": 0.85,
          "reveal": [remap("L08"), remap("L22.2")], "twist": remap("L28"),
          "emph": [remap(x) for x in ("L01.2", "L08", "L17.2", "L29")],
          "hold": ["S05", "S10a", "S24b"], "cam_push": 0.11}
story = {
    "slug": "ep147-motel-reviews",
    "title": "Room Six Came With a Polite STRANGER \U0001F6CE️",
    "made_for_kids": False,
    "premise": ("At this motel every review card comes true, and you get whatever the last guest wrote: our card "
                "says the man in the closet is very polite."),
    "twist": ("The man was the last guest, kept in Room Six by a card that said he never left; when I write him out, "
              "the card he leaves behind is about my dad and me."),
    "world": ("A bright roadside motel in the desert sun: mint doors, a pink office, a bucket for a pool, and Room "
              "Six with two orange beds, a desk with a drawer of review cards and a louvered closet."),
    "voice": {"voice": "am_adam", "tempo": 1.03, "rate": 1.45},
    "key_color": "#ff5fa2",
    "gap": 0.15,
    "tail": 0.25,
    "fade_in": False,
    "fade_out": False,
    "rev": REV,
    "look": {"style": "v3", "fog": "#e8f3ff", "fog_density": 0.0006, "fog_start": 90.0, "sky": "#7fd0ff",
             "sky_strength": 1.0, "exposure": 0.0, "flash_safe": True, "polish": polish},
    "grade": {"shadows": [0.0, 0.0, 0.01], "highlights": [0.025, 0.012, -0.015], "saturation": 1.05,
              "contrast": 1.03, "vignette": 0.1, "bloom": 0.12, "grain": 0.008},
    "hud": {"object": "tag", "at": [-0.44, 0.74], "size": 0.5},
    "cast": cast,
    "lines": lines,
    "shots": shots,
    "acting": acting,
    "cues": cues,
    "fx": [],
    "music": music,
    "sound": sound,
    "set_moves": ["S02", "S22"],
    "framing_ok": ["S08", "S08b", "S15", "S19b"],  # the closet man faces the wall on purpose (the script: back only until L22)
    "frames_ok": [],
    "staging_ok": [],
    "phonemes": {},
    "homophones": {"ay": "i", "em": "am"},
}
OUT.write_text(json.dumps(story, indent=1, ensure_ascii=False) + "\n")
print("wrote", OUT, f"({len(shots)} shots, {len(cues)} cues)")
