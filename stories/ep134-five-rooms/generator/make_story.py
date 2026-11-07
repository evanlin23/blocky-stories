"""Writes ../story.json for ep134 "five rooms" (script.md, 2026-11-06). Run: python stories/ep134-five-rooms/generator/make_story.py

The words are in lines.json. Places are in ../layout.py (shared with set.py). A character facing -y has yaw 0, +x 90,
+y 180, -x -90. Captions are split by timeline.split_lines and the chunk references are remapped.

Batch 14: nothing moves in the set and no light changes, so there are no light cues. The hall is built seven times, one
still state each (which doors are open), and a shot picks the state it needs. Night and morning are separate halls.
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
REV = 18
orig_lines = json.loads((HERE / "lines.json").read_text())
lines, CHUNKMAP = timeline.split_lines(orig_lines)
idx = next(i for i, l in enumerate(lines) if l["id"] == "L28")
lines.insert(idx, {"id": "P01", "pause": 0.6, "chunks": [["", ""]]})     # the 0.6 s music drop before L28


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


def mv(p0, t0, l0, p1=None, t1=None, l1=None):
    if p1 is None:
        return [[0, list(p0), list(t0), l0]]
    return [[0, list(p0), list(t0), l0], [1, list(p1), list(t1 if t1 is not None else t0), l1 or l0]]


def A(O, x, y, z=0.0):
    return [O[0] + x, O[1] + y, z]


def fc(O, tx, ty, tz, d, lens, dx=0.0, dz=0.0, push=0.28, az=0.0, lens2=None):
    """A camera d metres from the target, on the side az degrees round from -y, with a slow push in."""
    a = az * D2R
    tgt = [O[0] + tx, O[1] + ty, tz]
    p0 = [tgt[0] + dx + d * math.sin(a), tgt[1] - d * math.cos(a), tz + dz]
    p1 = [tgt[0] + dx * (1 - push) + d * (1 - push) * math.sin(a), tgt[1] - d * (1 - push) * math.cos(a), tz + dz]
    return mv(p0, tgt, lens, p1, tgt, lens2 or lens)


def person(skin, shirt, pants, shoes, hair="cap", hair_c="#2a1d15", pattern="solid", pattern_c=None, collar=None,
           hat="none", extras=(), eyes="round", sleeves="long", brow_w=1.0, **kw):
    d = {"age": "adult", "skin": skin, "shirt": shirt, "pattern": pattern, "pants": pants, "shoes": shoes,
         "sleeves": sleeves, "hair": hair, "hair_c": hair_c, "hat": hat,
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
    "me": person("#d9ac84", "#2a3a6a", "#8b9098", "#f4f4f2", hair="cap", hair_c="#5a3a22", extras=["hooddown"],
                 extra_c="#2a3a6a", brow_w=1.7),
    "mom": person("#e0b48a", "#c4a6e6", "#c4a6e6", "#f2a6c8", hair="long", hair_c="#cdbb92", eyes="lashes",
                  extras=["coat"], extra_c="#c4a6e6", brow_w=1.5),
    "dad": person("#e6bf98", "#8a9a5a", "#4a4a52", "#3a2a1a", hair="none", pattern="knit", pattern_c="#6a7a3c",
                  extras=["glasses"], extra_c="#3a3a3e", brow_w=1.4),
    "june": person("#d9ac84", "#1fa39a", "#3a4f78", "#f4f4f2", hair="long", hair_c="#15110f", eyes="lashes",
                   sleeves="short", brow_w=1.4),
    "bride": person("#e0b48a", "#ffffff", "#f6f0ff", "#f2a6c8", hair="bun", hair_c="#7a4a2a", eyes="lashes",
                    collar="#ffd1e8", brow_w=1.3),
    "groom": person("#c58c60", "#3a4f78", "#2a3248", "#2a2a2a", hair="cap", hair_c="#2a1d15", pattern="stripes",
                    pattern_c="#4a6498", extras=["tie"], extra_c="#e8584a", brow_w=1.5),
    "theo": person("#c58c60", "#ff9a2e", "#2f3b57", "#f4f4f2", hair="spiky", hair_c="#1c140e", extras=["glasses"],
                   extra_c="#222222", brow_w=1.4),
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


def beat(who, at, **kw):
    acting[who].append({"at": at, "pos": list(last[who]), **kw})


def only(at, names):
    for w in list(visible):
        if w not in names:
            acting[w].append({"at": at, "hidden": True})
            visible.discard(w)


def cue(at, name, **kw):
    cues.append({"at": at, "name": name, **kw})


def shot(at, camera, name, step=2, hand=None):
    SH.append((at, camera, step, hand, name))


def sit(who, at, on=True, z=0.62):
    cue(at, "sit", who=who, on=on, z=z)


HO = G.HALL_O


def hall_face(K, ref, who, x, y, az, expr, name, d=1.9, lens=24, tz=1.55, ty=0.0, tx=0.0, push=0.35, **kw):
    """Someone in hall K facing the camera, which stands d metres off at azimuth az (90: looking at the left wall)."""
    O = HO[K]
    only(ref, [who])
    put(who, ref, A(O, x, y), az, expr=expr, **kw)
    shot(ref, fc(O, x + tx, y + ty, tz, d, lens, az=az, push=push), name)
    if isinstance(ref, str) and "+" in ref:
        base, off = ref.rsplit("+", 1)
        gref = f"{base}+{float(off) + 0.55:.2f}"
    else:
        gref = f"{ref}+0.55"
    beat(who, gref, head=[14, 4])      # a glance, so the face isn't a held picture


def knock(K, ref, who, door_y, expr, name, theta=45.0, f=30.0, s=80.0, d=2.3, lens=19, push=0.16, closer=0.0, pan=0.3):
    """Someone with the flat left hand (the one toward the wall) on a left-wall door at chest height, face to camera."""
    O = HO[K]
    L = 0.62
    th = theta * D2R
    lx = -0.51 - L * math.cos(f * D2R) * math.sin(s * D2R)
    ly = -L * math.sin(f * D2R)
    ox = lx * math.cos(th) - ly * math.sin(th)
    oy = lx * math.sin(th) + ly * math.cos(th)
    tipx = G.LX - 0.01
    rx, ry = tipx - ox, door_y - 0.05 - oy
    rx += closer * math.cos(th) * 0 - closer * 1.0   # nearer the wall (-x)
    only(ref, [who])
    put(who, ref, A(O, rx, ry), theta, expr=expr, side=[s, 0], arms=[f, 0], head=[0, 0])
    # the camera looks a little toward the door so the hand and the numeral share the frame
    shot(ref, fc(O, rx - pan * math.cos(th), ry - pan * math.sin(th), 1.45, d, lens, az=theta, push=push), name)
    return rx, ry


# ===== 01 the hook, the rule, the montage (L01 to L06)
HA = HO["A"]
only(0, ["me"])
put("me", 0, A(HA, -0.6, 6.12), 90, expr="neutral")
shot(0, fc(HA, -0.6, 6.45, 1.55, 1.9, 18, push=0.2, az=90), "hook")
hall_face("A", "L01.1", "me", -0.3, 6.4, 40, "neutral", "hook2", d=2.3)
only("L02", ["me"])
put("me", "L02", A(HA, -0.3, 3.4), 30, expr="neutral")
shot("L02", mv(A(HA, 1.4, 0.7, 1.55), A(HA, -1.6, 7.0, 1.4), 24, A(HA, 1.4, 1.1, 1.55), A(HA, -1.6, 7.4, 1.4), 24), "wide")
hall_face("A", "L02.2", "me", -0.55, 8.4, 55, "worried", "lived", d=1.9, lens=26)
only("L03", ["bride", "groom"])
put("bride", "L03", A(G.HOUSE, -0.75, 0.8), 0, expr="smile")
put("groom", "L03", A(G.HOUSE, 0.75, 0.8), 0, expr="smile")
shot("L03", fc(G.HOUSE, 0.0, 0.8, 1.4, 5.0, 24, push=0.08), "newlyweds")
only("L04", [])
shot("L04", mv(A(G.BOARD, -16, 1.0, 2.7), A(G.BOARD, 3, 7.45, 4.3), 18, A(G.BOARD, -13, 1.0, 2.7), A(G.BOARD, 5, 7.45, 4.3), 18), "board")
shot("L04+1.0", mv(A(G.BOARD, 16, 1.0, 2.7), A(G.BOARD, -3, 7.45, 4.3), 18, A(G.BOARD, 13, 1.0, 2.7), A(G.BOARD, -5, 7.45, 4.3), 18), "board2")
only("L05", ["theo"])
put("theo", "L05", A(G.THEO, -0.35, 2.9), 0, expr="wide")
shot("L05", fc(G.THEO, 0.35, 2.9, 1.35, 3.6, 22, push=0.08), "theo")
shot("L05+1.2", fc(G.THEO, 0.45, 2.9, 1.4, 3.6, 20, az=8, push=0.06), "theo2")
only("L06", ["mom"])
put("mom", "L06", A(HA, 0.0, 1.6), 180, expr="smile")
shot("L06", fc(HA, 0.0, 1.6, 1.5, 2.6, 32, az=180, push=0.28), "momstairs")
only("L06.2", ["june"])
put("june", "L06.2", A(G.KIT, 0.0, 2.78), 0, expr="smile")
sit("june", "L06.2", True, 0.65)
shot("L06.2", fc(G.KIT, 0.0, 2.78, 1.3, 2.7, 34, dz=0.1, push=0.28), "june")
only("L06.3", ["me"])
put("me", "L06.3", A(HA, -0.6, 6.12), 90, expr="neutral")
shot("L06.3", fc(HA, -0.6, 6.45, 1.55, 1.9, 18, push=0.2, az=90), "andme")

# ===== 02 the rooms we know (L07 to L14)
only("L07", [])
shot("L07", mv(A(HA, -1.4, 1.0, 1.5), A(HA, 1.7, 7.5, 1.4), 24, A(HA, -1.4, 1.5, 1.5), A(HA, 1.7, 8.0, 1.4), 24), "open4")
only("L08", [])
shot("L08", mv(A(HA, 1.4, 0.8, 1.5), A(HA, -1.7, 7.0, 1.4), 22, A(HA, 1.4, 1.2, 1.5), A(HA, -1.7, 7.5, 1.4), 22), "shut5")
knock("A", "L09", "mom", G.DOORY[6], "warm", "momknock", closer=0.25, pan=0.45)
beat("mom", "L09.1", side=[84, 0])
beat("mom", "L09.1+0.5", side=[80, 0])
only("L10", ["dad"])
put("dad", "L10", A(G.LIV, 0.0, 2.15), 0, expr="smile")
sit("dad", "L10", True, 0.62)
shot("L10", fc(G.LIV, 0.0, 2.15, 1.3, 2.7, 34, dz=0.1, push=0.28), "dad")
hall_face("A", "L11", "me", -0.7, 2.4, 50, "worried", "whose", d=1.9, lens=26)
only("L12", ["me"])
put("me", "L12", A(G.PORCH, 0.0, 0.7), 0, expr="sad-smile")
sit("me", "L12", False)
shot("L12", fc(G.PORCH, 0.3, 0.7, 1.05, 4.6, 26, push=0.1), "porch")
shot("L12+0.9", fc(G.PORCH, 0.3, 0.7, 1.2, 3.6, 26, az=-28, push=0.1), "porch2")
only("L13", ["mom"])
put("mom", "L13", A(G.PORCH, 0.0, 2.7), 0, expr="smile")
shot("L13", fc(G.PORCH, 0.0, 2.7, 1.45, 2.5, 34, push=0.28), "momdoor")
shot("L13+0.9", fc(G.PORCH, 0.0, 2.7, 1.5, 1.9, 34, az=22, push=0.28), "momdoor2")
only("L14", ["me"])
put("me", "L14", A(HA, 0.75, 10.6), -90, expr="neutral")
shot("L14", fc(HA, 0.75, 10.6, 1.55, 1.7, 22, az=-90, push=0.28), "room4")

# ===== 03 the nights (L15 to L27)
only("L15", [])
shot("L15", mv(A(HO["B"], 0.9, 3.7, 1.4), A(HO["B"], -1.7, 6.7, 1.3), 20, A(HO["B"], 0.9, 4.1, 1.4), A(HO["B"], -1.7, 6.7, 1.3), 20), "ajar")
shot("L15+1.0", mv(A(HO["B"], 0.2, 4.7, 1.4), A(HO["B"], -1.7, 6.7, 1.3), 24, A(HO["B"], 0.3, 4.95, 1.4), A(HO["B"], -1.7, 6.7, 1.3), 24), "ajar2")
hall_face("B", "L16", "me", -0.5, 5.6, 125, "worried", "inch", d=1.9, lens=16, ty=1.0, arms=[0, 0], side=[0, 0])
only("L17", ["me"])
put("me", "L17", A(HO["B"], -0.85, 5.63), -40, expr="worried", arms=[0, 0], side=[0, 0], head=[40, 0])
beat("me", "L17+0.3", arms=[0, 0], side=[75, 0], head=[40, 0])
shot("L17", fc(HO["B"], -1.55, 6.1, 1.4, 2.9, 16, az=24, push=0.08), "push")
only("L18", [])
shot("L18", mv(A(HO["C"], -1.78, 6.4, 1.55), A(HO["C"], -4.85, 6.4, 1.6), 20, A(HO["C"], -2.1, 6.4, 1.55), A(HO["C"], -4.85, 6.4, 1.6), 20), "portrait")
shot("L19", mv(A(HO["C"], -1.9, 6.4, 1.4), A(HO["C"], -4.85, 6.4, 1.45), 26, A(HO["C"], -2.3, 6.4, 1.4), A(HO["C"], -4.85, 6.4, 1.45), 26), "portrait2")
hall_face("C", "L20", "me", -0.6, 5.7, 90, "scared", "meat23", d=1.9, lens=18, ty=0.25, arms=[0, 0], side=[0, 0])
beat("me", "L20.1", expr="wide")
only("L21", [])
shot("L21", mv(A(HO["D"], -1.78, 2.4, 1.55), A(HO["D"], -4.4, 2.4, 1.3), 20, A(HO["D"], -2.0, 2.4, 1.55), A(HO["D"], -4.4, 2.4, 1.3), 20), "five")
shot("L22", mv(A(HO["D"], -0.8, 2.95, 1.2), A(HO["D"], -2.8, 2.68, 1.0), 18, A(HO["D"], -1.0, 2.9, 1.2), A(HO["D"], -2.8, 2.68, 1.0), 18), "guitar")
hall_face("D", "L23", "me", -0.6, 1.9, 90, "wide", "meat19", d=1.9, lens=18, ty=0.25)
only("L24", [])
shot("L24", mv(A(HO["E"], -1.78, 8.4, 1.5), A(HO["E"], -4.4, 8.4, 1.2), 20, A(HO["E"], -2.0, 8.4, 1.5), A(HO["E"], -4.4, 8.4, 1.2), 20), "eight")
shot("L25", mv(A(HO["E"], -0.6, 8.0, 1.2), A(HO["E"], -2.9, 8.6, 0.8), 18, A(HO["E"], -0.8, 8.1, 1.2), A(HO["E"], -2.9, 8.6, 0.8), 18), "boxes")
hall_face("E", "L25+1.0", "me", -0.6, 8.4, 90, "wide", "boxes2", d=1.9, lens=18, ty=0.25)
shot("L26", mv(A(HO["F"], 0.8, 3.2, 1.5), A(HO["F"], -1.7, 4.6, 1.5), 18, A(HO["F"], 0.8, 3.45, 1.5), A(HO["F"], -1.7, 4.6, 1.5), 18), "six")
shot("L26+0.5", mv(A(HO["F"], 0.8, 9.2, 1.5), A(HO["F"], -1.7, 10.6, 1.5), 18, A(HO["F"], 0.8, 9.45, 1.5), A(HO["F"], -1.7, 10.6, 1.5), 18), "nine")
hall_face("F", "L27", "me", -0.2, 6.4, 50, "wide", "allmine", d=1.9, lens=24)
only("P01", [])
shot("P01", mv(A(HO["F"], 0.9, 0.8, 1.5), A(HO["F"], -0.5, 10.0, 1.4), 20, A(HO["F"], 0.9, 1.4, 1.5), A(HO["F"], -0.5, 10.0, 1.4), 20), "drop")

# ===== 04 the reveal (L28 to L31)
hall_face("F", "L28", "me", -0.2, 6.4, 38, "wide", "newone", d=1.55, lens=28, push=0.12)
only("L29", [])
shot("L29", mv(A(HO["F"], -2.2, 3.1, 1.6), A(HO["F"], -2.21, 1.89, 1.62), 28, A(HO["F"], -2.2, 2.9, 1.6), A(HO["F"], -2.21, 1.89, 1.62), 28), "num5")
shot("L29.2", mv(A(HO["F"], -2.2, 11.1, 1.6), A(HO["F"], -2.21, 9.89, 1.62), 28, A(HO["F"], -2.2, 10.9, 1.6), A(HO["F"], -2.21, 9.89, 1.62), 28), "num9")
only("L30", ["me"])
put("me", "L30", A(HO["F"], 0.15, 4.2), 0, expr="wide", arms=[0, 0], side=[0, 0], head=[0, 0])
shot("L30", mv(A(HO["F"], -0.4, 0.9, 1.1), A(HO["F"], -0.3, 6.5, 1.3), 15, A(HO["F"], -0.35, 1.15, 1.1), A(HO["F"], -0.3, 6.5, 1.3), 15), "reveal")
hall_face("F", "L31", "me", -0.5, 7.0, 70, "sad-smile", "knew", d=1.9, lens=26)
beat("me", "L31.1", expr="warm")

# ===== 05 the warm turn (L32 to L36)
only("L32", ["mom"])
put("mom", "L32", A(HO["F"], 0.0, 1.5), 180, expr="smile")
shot("L32", fc(HO["F"], 0.0, 1.5, 1.5, 2.6, 30, az=180, push=0.28), "momstairs2")
hall_face("F", "L33", "me", -0.4, 9.0, 60, "worried", "asked", d=1.9, lens=26)
only("L34", ["mom"])
put("mom", "L34", A(HO["F"], 0.1, 1.5), 180, expr="warm")
shot("L34", fc(HO["F"], 0.1, 1.5, 1.52, 1.9, 26, az=175, push=0.28), "momwarm")
only("L35", ["mom"])
put("mom", "L35", A(HO["F"], -0.1, 1.5), 180, expr="laugh")
shot("L35", fc(HO["F"], -0.1, 1.5, 1.52, 1.9, 26, az=185, push=0.28), "momlaugh")
hall_face("F", "L36", "me", -0.3, 4.2, 55, "laugh", "melaugh", d=1.9, lens=26)

# ===== 06 the tenth door (L37 to L42)
only("L37", [])
shot("L37", mv(A(HO["M"], 0.9, 7.5, 1.5), A(HO["M"], -0.7, 13.2, 1.4), 17, A(HO["M"], 0.9, 8.0, 1.5), A(HO["M"], -0.7, 13.2, 1.4), 17), "tenth")
hall_face("M", "L38", "me", -0.6, 11.98, 90, "wide", "sixth", d=1.9, lens=18, ty=0.2)
only("L39", [])
shot("L39", mv(A(HO["M"], 1.2, 11.3, 1.4), A(HO["M"], -1.7, 12.4, 1.3), 20, A(HO["M"], 0.2, 12.0, 1.4), A(HO["M"], -1.7, 12.4, 1.3), 20), "tenth2")
hall_face("M", "L40", "mom", -0.6, 11.98, 90, "smile", "likes", d=1.9, lens=18, ty=0.2)
knock("M", "L41", "mom", G.DOORY[10], "smile", "knocked", closer=0.25)
beat("mom", "L41.1", side=[84, 0])
beat("mom", "L41.1+0.5", side=[80, 0])
only("L42", ["me"])
put("me", "L42", A(HA, -0.6, 6.12), 90, expr="neutral")
shot("L42", mv(A(HA, -0.6 + 2.2, 6.45, 1.55), A(HA, -0.6, 6.45, 1.55), 18, A(HA, -0.6 + 1.9, 6.45, 1.55), A(HA, -0.6, 6.45, 1.55), 18), "loop")

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
    {"at": "L01+0.9", "kind": "creak", "db": -18, "dur": 0.9},
    {"at": "L15", "kind": "creak", "db": -18, "dur": 0.9},
    {"at": "L17+0.3", "kind": "creak", "db": -17, "dur": 1.0},
    {"at": "L21", "kind": "creak", "db": -18, "dur": 0.9},
    {"at": "L24", "kind": "creak", "db": -18, "dur": 0.9},
    {"at": "L09.1", "kind": "knock", "db": -18, "pattern": [0, 0.3], "tone": "hand"},
    {"at": "L41.1", "kind": "knock", "db": -18, "pattern": [0, 0.3], "tone": "hand"},
    {"at": "L33", "kind": "thud", "db": -26, "dur": 0.4},
]
music = {
    "root": 48, "mode": "major", "bpm": 100, "seed": 134,
    "sections": [
        {"at": 0, "voices": ["piano", "pad"], "energy": 0.35, "root": 48, "mode": "major"},
        {"at": "L06", "voices": ["piano", "pad", "drone"], "energy": 0.4, "root": 45, "mode": "minor"},
        {"at": "L15", "voices": ["pulse", "pad", "drone"], "energy": 0.55, "root": 45, "mode": "minor"},
        {"at": "L28", "voices": ["pad", "drone"], "energy": 0.3, "root": 45, "mode": "minor"},
        {"at": "L33", "voices": ["piano", "pad", "pulse"], "energy": 0.5, "root": 48, "mode": "major"},
    ],
}
sound = {
    "floor": "wood", "steps_db": -26,
    "ambience": [{"kind": "room", "from": 0, "to": "P01", "lufs": -44}, {"kind": "room", "from": "P01>", "to": "end", "lufs": -44}],
    "sfx": sfx,
    "music_drops": [{"from": "P01", "to": "P01>"}],
    "rev": REV,
}
remap_all(sfx)
remap_all(music["sections"])
remap_all(sound["music_drops"])
remap_all(sound["ambience"])
polish = {"reveal": [remap("L30")],
          "emph": [remap(x) for x in ["L01.0", "L02.2", "L12", "L18", "L20", "L27", "L35", "L37", "L42"]],
          "max_zoom": 1.16, "sway": True, "drift": 0.05, "cam_push": 0.12, "cam_arc": 6.0, "punch": 0.08, "punch_rate": 1.0,
          "hold": [names[n] for n in ["open4", "shut5", "reveal", "tenth"]]}
story = {
    "slug": "ep134-five-rooms",
    "title": "Our House Has Nine Rooms For FOUR \U0001f5dd️",
    "made_for_kids": False,
    "premise": ("In a town where a house builds a room for everyone who has ever lived in it, mine has nine rooms for a "
                "family of four, and Mom keeps five of them shut and knocks on each every night."),
    "twist": ("All five extra rooms are mine: each time I moved back home I'd become somebody new, so the house built "
              "a room for each of me, Mom kept every one, and now a tenth door waits for whoever I turn into next."),
    "world": ("Mom's long upstairs hall in peach and cream with a runner rug, ten white doors with big teal numerals, a "
              "warm steady ceiling glow, a stair head at one end and a window at the other, and a bright still room "
              "in its own colour behind each door."),
    "voice": {"voice": "am_adam", "tempo": 1.03, "rate": 1.45},
    "key_color": "#2fd6c6",
    "gap": 0.15,
    "tail": 0.25,
    "fade_in": False,
    "fade_out": False,
    "rev": REV,
    "look": {"style": "closer", "fog": "#f4e6d6", "fog_density": 0.004, "fog_start": 24.0, "sky": "#cfe6ff",
             "sky_strength": 1.0, "exposure": 0.25, "flash_safe": True, "polish": polish},
    "grade": {"shadows": [0.0, 0.0, 0.03], "highlights": [0.03, 0.012, -0.02], "saturation": 1.1, "contrast": 1.05,
              "vignette": 0.2, "bloom": 0.15, "grain": 0.008},
    "phonemes": {},
    "homophones": {"for": "four", "10th": "tenth"},
    "cast": cast,
    "lines": lines,
    "shots": shots,
    "acting": acting,
    "cues": cues,
    "fx": [],
    "music": music,
    "sound": sound,
    "framing_ok": [names["june"]],
    "asr_forgive": ["theo", "june", "i've", "he'd", "she'd"],
}
OUT.write_text(json.dumps(story, indent=1, ensure_ascii=False) + "\n")
print("wrote", OUT, f"({len(shots)} shots, {len(cues)} cues)")
print({k: v for k, v in names.items()})
