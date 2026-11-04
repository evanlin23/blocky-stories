"""Writes ../story.json for ep89 "sister-diary" (batch 8, script.md 2026-11-03).

Run from anywhere: python stories/ep89-sister-diary/generator/make_story.py
The words are in lines.json next to this file (made from script.md). The cast, the shots, the acting, the cues set.py
reads, the score and the sound are all here.

Places (metres, floor z = 0; yaw 0 faces -y, 90 faces +x, 180 faces +y, -90 faces -x):
  THE UPSTAIRS  hall y -2.2..0 (x -4.4..4.4); my room (sky blue) x -4.4..-0.1, y 0..4.4; Nina's room (lilac)
                x 0.1..4.4, y 0..4.4; one shared wall at x = 0. Doors in the hall wall at x = -1.6 (mine) and +1.6 (hers).
  my desk       against the shared wall, top x -0.76..-0.14, y 0.8..2.2; I sit at (-1.25, 1.5) facing +x (yaw 90)
  Nina's desk   the same, mirrored: she sits at (1.25, 1.5) facing -x (yaw -90). The two desks are back to back.
  far rooms     GIFT (30, 0)  CAR (60, 0)  WORK (90, 0)  PAIR (120, 0)
Cues set.py reads: ink / inkclear / answer / place / open / pen / mydoor / ndoor / drawer / lamp / hud2 / ribbon / glint /
clock / photo (see set.py's docstring).
"""
import json
import math
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE.parent / "story.json"
lines = json.loads((HERE / "lines.json").read_text())
LOOP = 0.25
GAP = 0.12

# the 0.6 s music drop before L21 and the one beat before the reveal (L49) are pause beats
_i = next(i for i, l in enumerate(lines) if l["id"] == "L21")
lines.insert(_i, {"id": "P01", "pause": 0.6, "chunks": []})
_i = next(i for i, l in enumerate(lines) if l["id"] == "L49")
lines.insert(_i, {"id": "P02", "pause": 0.5, "chunks": []})

# captions show 2 or 3 words at a time: split any longer chunk in two, and remap the anchors ("L12.2") to the new indices
CHUNK_MAP = {}
for _ln in lines:
    if "pause" in _ln:
        continue
    _new, _m = [], {}
    for _k, (_cap, _sp) in enumerate(_ln["chunks"]):
        _m[_k] = len(_new)
        _cw, _sw = _cap.split(" "), _sp.split(" ")
        if len(_sw) > 3 and len(_cw) == len(_sw):
            _h = (len(_sw) + 1) // 2
            _new.append([" ".join(_cw[:_h]), " ".join(_sw[:_h])])
            _new.append([" ".join(_cw[_h:]), " ".join(_sw[_h:])])
        else:
            _new.append([_cap, _sp])
    _ln["chunks"] = _new
    CHUNK_MAP[_ln["id"]] = _m
_RR = re.compile(r"^(?P<id>[LP]\d\d[a-c]?)\.(?P<c>\d)(?P<rest>.*)$")


def R(ref):
    if not isinstance(ref, str):
        return ref
    m = _RR.match(ref)
    if not m or m.group("id") not in CHUNK_MAP:
        return ref
    return f"{m.group('id')}.{CHUNK_MAP[m.group('id')][int(m.group('c'))]}{m.group('rest')}"


# ---------------------------------------------------------------------------------------------------- cast
def person(skin, shirt, pants, hair, hair_c, eyes="round", shoes="#f4f4f4", **kw):
    d = {"age": "adult", "skin": skin, "shirt": shirt, "pattern": "solid", "pants": pants, "shoes": shoes,
         "sleeves": "long", "hair": hair, "hair_c": hair_c, "hat": "none", "face": {"eyes": eyes, "brows": True}}
    d.update(kw)
    return d


cast = {
    # me (17, Leo): short brown hair, sky-blue hoodie, jeans, white socks
    "me": person("#f1c9a0", "#4fa9ff", "#34507f", "swoop", "#5a3a22", age="teen", extras=["hooddown"], extra_c="#4fa9ff"),
    # Nina (19): long dark hair, lilac sweater (a work lanyard is added in set.py), lashes
    "nina": person("#e8b998", "#c7a6ff", "#3a3550", "long", "#2a1a22", eyes="lashes", pattern="knit", pattern_c="#b48cf2",
                   collar="#f4ecf8"),
    # Mom: seen once
    "mom": person("#f0c6a4", "#f2a98a", "#4a4658", "bun", "#8a5a3a", eyes="lashes", shoes="#6a4a3a", collar="#fff1e0"),
}

# ---------------------------------------------------------------------------------------------------- helpers
LINE_NO = {ln["id"]: i + 1 for i, ln in enumerate(lines)}
_REF = re.compile(r"^(?P<id>[LP]\d\d[a-c]?)(?:\.(?P<c>\d))?(?P<tail>>)?(?P<o>[+-]\d+(?:\.\d+)?)?$")


def tkey(ref):
    """A sortable number for an anchor like "L12.1+0.4"."""
    if isinstance(ref, (int, float)):
        return float(ref)
    m = _REF.match(ref)
    base = LINE_NO[m.group("id")]
    return base * 100 + int(m.group("c") or 0) * 12 + (99 if m.group("tail") else 0) + float(m.group("o") or 0)


def fmt(a):
    return round(a, 3) if isinstance(a, (int, float)) else a


acting = {w: [{"at": 0, "hidden": True, "blend": 0, "pos": [0, 40]}] for w in cast}
cues = []
shown = {w: False for w in cast}
NEUTRAL = {"arms": [0, 0], "side": [0, 0], "head": [0, 0], "lean": 0, "tremble": 0, "blink": True, "look": [0, 0],
           "sit": False, "bend": 0}


def raw(who, at, **kw):
    acting[who].append({"at": fmt(R(at)), **kw})


def put(who, at, pos, yaw=0, expr="neutral", **kw):
    at = R(at)
    keys = acting[who]
    prev = next((k["pos"] for k in reversed(keys) if "pos" in k), None)
    if prev is not None:
        keys.append({"at": fmt(at), "pos": prev})
    keys.append({"at": fmt(at), "pos": list(pos), "blend": 0, **NEUTRAL, "hidden": False, "yaw": yaw, "expr": expr, **kw})
    shown[who] = True


def hide(who, at):
    at = R(at)
    if shown[who]:
        acting[who].append({"at": fmt(at), "hidden": True, "blend": 0})
        shown[who] = False


def cue(at, name, **kw):
    cues.append({"at": R(at), "name": name, **kw})


shots = []
SHOTLOOK = {}


def S(at, cam, who=None, note="", step=2, hand=0.006, look=None, follow=None):
    """A shot. cam = (loc, tgt, lens) or (loc, tgt, lens, loc2, tgt2, lens2). who = {name: (pos, yaw, expr, kw)}."""
    who = who or {}
    for name in cast:
        if name in who:
            spec = who[name]
            pos, yaw = spec[0], spec[1]
            expr = spec[2] if len(spec) > 2 else "neutral"
            kw = spec[3] if len(spec) > 3 else {}
            put(name, at, pos, yaw, expr, **kw)
        else:
            hide(name, at)
    if len(cam) == 3:
        keys = [[0, list(cam[0]), list(cam[1]), cam[2]]]
    else:
        keys = [[0, list(cam[0]), list(cam[1]), cam[2]], [1, list(cam[3]), list(cam[4]), cam[5]]]
    sid = f"S{len(shots) + 1:02d}"
    if look:
        SHOTLOOK[sid] = look
    shots.append({"at": R(at), "cam": keys, "step": step, "hand": hand, "note": note, "follow": follow})
    return sid


def X(x, y, z=0.0):
    return [x, y, z]


# ---- fixed spots
ME_D = (-1.25, 1.5)        # my desk chair
NI_D = (1.25, 1.5)         # Nina's desk chair
SEATZ = -0.2               # root height of a sitter
BD_M = (-0.46, 1.5, 0.78)  # the diary on my desk
BD_N = (0.46, 1.5, 0.78)   # the diary on Nina's desk
D_ME, D_NI = (-1.6, -0.45), (1.6, -0.45)   # standing in the hall at each door
GIFT, CAR, WORK, PAIR = 30.0, 60.0, 90.0, 120.0


def sit_me(expr="neutral", **kw):
    return (X(ME_D[0], ME_D[1], SEATZ), 90, expr, {"sit": True, "arms": [66, 66], **kw})


def sit_ni(expr="neutral", **kw):
    return (X(NI_D[0], NI_D[1], SEATZ), -90, expr, {"sit": True, "arms": [66, 66], **kw})


def C3(p, t, lens=32):
    return (p, t, lens)


def MV(p0, t0, p1, t1, lens=32, lens1=None):
    return (p0, t0, lens, p1, t1, lens if lens1 is None else lens1)


# ---- ink helpers: the pages' rows. Each cue: {d: page, row, c: ink colour, to, dur, size, shake, hard}
ROWS = 6
_next_row = {"blue": 0, "lilac": 0}
_row_of = {"blue": {}, "lilac": {}}   # tag -> row


def clear(d, at):
    cue(at, "inkclear", d=d)
    _next_row[d] = 0


def write(d, at, c, dur=1.2, to=1.0, tag=None, row=None, size=1.0, shake=0.0, hard=False):
    """Write (or continue) a row on page d: ink colour c ('lilac'/'blue'/'green'), crawling to `to` over dur."""
    if tag is not None and tag in _row_of[d]:
        r = _row_of[d][tag]
    else:
        r = row if row is not None else _next_row[d]
        if r >= ROWS:
            clear(d, at)
            r = 0
        _next_row[d] = r + 1
        if tag is not None:
            _row_of[d][tag] = r
    kw = {"d": d, "row": r, "c": c, "to": to, "dur": dur}
    if size != 1.0:
        kw["size"] = size
    if shake:
        kw["shake"] = shake
    if hard:
        kw["hard"] = True
    cue(at, "ink", **kw)
    return r


def fillrows(d, at, c, n):
    for _ in range(n):
        write(d, at, c, dur=0.05)


def place(d, at, to, dur=0.0, **kw):
    cue(at, "place", d=d, to=to, dur=dur, **kw)


def openb(d, at, to, dur=0.5):
    cue(at, "open", d=d, to=to, dur=dur)


# ===================================================================================================== 01 the hook, L01 to L02
# the blue diary: open on my desk, lilac ink already crawling (rows 0-1 written, row 2 writing now)
place("blue", 0, "desk")
place("lilac", 0, "nshelf")
openb("blue", 0, 1.0, 0.01)
cue(0, "hud2", to=0, dur=0.01)
cue(0, "clock", h=11, m=47)
fillrows("blue", 0, "lilac", 2)
for _r in (0, 1):
    cue(0, "ink", d="blue", row=_r, c="lilac", to=1.0, dur=0.05, size=1.3)
write("blue", 0.05, "lilac", dur=2.6, to=1.0, size=1.3)
write("blue", "L02", "lilac", dur=2.2, to=1.0)

S(0, MV((-1.1, 2.15, 1.2), (-0.4, 1.5, 0.8), (-0.62, 1.8, 1.0), (-0.38, 1.5, 0.8), 26), hand=0.0, look={"cutwall": True},
  note="a real book: the open blue diary on the desk, cover rim, brass caps and clasp tab, the lamp, lilac ink crawling; push in")
S("L02", MV((0.8, 2.0, 1.5), (-1.25, 1.5, 1.33), (0.5, 1.8, 1.45), (-1.25, 1.5, 1.33), 26),
  who={"me": sit_me("worried", head=[0, 6])}, look={"cutwall": True},
  note="me at the desk, guilty, glancing at the camera as if caught")

# ===================================================================================================== 02 the pair, L03 to L06a
cue("L03", "ribbon", on=1)
place("blue", "L03", "gift")
place("lilac", "L03", "gift")
openb("blue", "L03", 0.0, 0.01)
S("L03", MV((GIFT + 0.05, -0.95, 1.22), (GIFT, 0.0, 0.84), (GIFT + 0.02, -0.7, 1.12), (GIFT, 0.0, 0.84), 34),
  note="two wrapped diaries on a bright gift table, lilac and blue, side by side")
cue("L04", "ribbon", on=0)
S("L04", MV((GIFT + 0.12, -0.34, 0.99), (GIFT - 0.14, 0.0, 0.8), (GIFT + 0.0, -0.3, 0.97), (GIFT - 0.14, 0.0, 0.8), 40),
  note="Nina's is LILAC: the lilac diary, its clasp catching the light")
S("L04.1", MV((GIFT - 0.0, -0.34, 0.99), (GIFT + 0.14, 0.0, 0.8), (GIFT + 0.13, -0.3, 0.97), (GIFT + 0.14, 0.0, 0.8), 40),
  note="Mine is BLUE: the blue diary")
place("blue", "L05", "touch", dur=0.5)
place("lilac", "L05", "touch", dur=0.5)
cue("L05.1+0.2", "glint", dur=0.6)
S("L05", MV((GIFT - 0.02, -0.28, 0.94), (GIFT, 0.0, 0.83), (GIFT, -0.2, 0.9), (GIFT, 0.0, 0.83), 45),
  note="the two clasps touching, a tiny glint between them")
place("blue", "L06", "drawer")
place("lilac", "L06", "ndeskdust")
cue("L06", "drawer", to=1.0, dur=1.0)
S("L06", MV((-3.3, 3.0, 1.45), (-3.3, 4.05, 0.66), (-3.3, 3.25, 1.2), (-3.3, 3.8, 0.66), 34),
  look={"cutwall": False},
  note="my drawer sliding open, the blue diary inside, dust on it; a framed bookshelf photo on the wall above")
S("L06a", MV((0.95, 2.25, 1.2), (0.46, 1.58, 0.78), (0.72, 1.95, 0.98), (0.46, 1.58, 0.78), 34),
  note="Neither of us: the lilac diary dusty on Nina's desk")
S("L06a.1", MV((-3.3, 3.35, 1.1), (-3.3, 3.78, 0.66), (-3.3, 3.5, 0.95), (-3.3, 3.78, 0.66), 44),
  note="ever WROTE in them: the blue one in my drawer, dusty")

# ===================================================================================================== 03 Nina, the hall, L07 to L09a
cue("L07", "ndoor", to=75, dur=0.4)
cue("L07", "mydoor", to=75, dur=0.4)
S("L07", MV((0.1, -1.15, 1.55), (1.6, -0.45, 1.5), (0.4, -1.1, 1.55), (1.6, -0.45, 1.5), 30),
  who={"nina": (X(*D_NI), -50, "angry", {"arms": [20, 20]})},
  note="across the hall: Nina in her lilac sweater, annoyed, at her door")
S("L07.2", MV((-0.3, -1.15, 1.55), (-1.6, -0.45, 1.5), (-0.6, -1.1, 1.55), (-1.6, -0.45, 1.5), 30),
  who={"me": (X(*D_ME), 55, "angry", {})},
  note="I'm her BROTHER: me at my door")
S("L08", MV((0.0, -1.95, 1.55), (0.0, -0.5, 1.5), (0.0, -1.8, 1.55), (0.0, -0.5, 1.5), 20),
  who={"me": (X(-0.5, -0.5), 90, "angry", {}), "nina": (X(0.5, -0.5), -90, "angry", {})},
  note="the hall between us")
cue("L09+0.4", "ndoor", to=0, dur=0.14)
S("L09", MV((1.25, -1.35, 1.6), (1.6, 0.9, 1.5), (1.4, -1.1, 1.6), (1.6, 0.9, 1.5), 28),
  who={"nina": (X(1.65, 1.0), 0, "angry", {"arms": [20, 20]})},
  note="her door slamming: Nina's angry face in the gap as it shuts")
S("L09.1", MV((0.3, -1.45, 1.2), (0.0, -2.0, 0.9), (0.2, -1.5, 1.15), (0.0, -2.0, 0.9), 40),
  note="car keys on the hall table")
S("L09.2", MV((0.0, -1.0, 1.3), (0.0, -2.0, 0.95), (0.0, -1.2, 1.2), (0.0, -2.0, 0.95), 34),
  who={"me": (X(-0.5, -1.65), 0, "angry", {"arms": [80, 80]}), "nina": (X(0.5, -1.65), 0, "angry", {"arms": [80, 80]})},
  note="two hands reaching for the keys (cut before any grip)")
cue("L09a", "ndoor", to=0, dur=0.01)
S("L09a", MV((0.8, 2.0, 1.5), (-1.25, 1.5, 1.33), (0.5, 1.8, 1.45), (-1.25, 1.5, 1.33), 26),
  who={"me": sit_me("angry", head=[0, 6])},
  look={"cutwall": True},
  note="me on my bed, ear near the wall, annoyed, her keyboard tapping through it")

# ===================================================================================================== 04 the ink, L10 to L15
clear("blue", "L10")
openb("blue", "L10", 0.0, 0.01)
place("blue", "L10", "desk")
openb("blue", "L10+0.3", 1.0, 0.7)
write("blue", "L10.2", "lilac", dur=1.2, to=1.0, tag="a")
S("L10", MV((-0.95, 2.25, 1.35), (-0.46, 1.5, 0.8), (-0.78, 2.1, 1.2), (-0.46, 1.5, 0.8), 30),
  who={"me": sit_me("worried")}, look={"cutwall": False},
  note="the blue diary on my desk, falling open by itself, a line of lilac ink appearing")
S("L10.2", MV((-0.905, 1.43, 1.2), (-0.365, 1.43, 0.79), (-0.755, 1.43, 1.0), (-0.365, 1.43, 0.79), 36), hand=0.0,
  note="the line of ink appearing, close")
write("blue", "L11", "lilac", dur=1.4, to=1.0)
S("L11", MV((-0.855, 1.43, 0.98), (-0.365, 1.43, 0.79), (-0.685, 1.43, 0.92), (-0.365, 1.43, 0.79), 36), hand=0.0,
  note="close: lilac ink in my own blocky scribble style")
write("blue", "L12", "lilac", dur=1.6, to=1.0)
S("L12", MV((-0.82, 1.62, 1.0), (-0.4, 1.43, 0.79), (-0.66, 1.48, 0.9), (-0.37, 1.43, 0.79), 50), hand=0.0,
  note="the ink moving, letter by letter")
write("blue", "L13", "lilac", dur=2.0, to=1.0)
S("L13", MV((-0.66, 1.45, 0.9), (-0.37, 1.43, 0.79), (-0.55, 1.43, 0.85), (-0.34, 1.43, 0.79), 60), hand=0.0,
  note="extreme close on the ink crawling")
S("L14", MV((WORK - 1.2, -1.6, 1.3), (WORK, 0.2, 1.3), (WORK - 0.9, -1.5, 1.3), (WORK, 0.2, 1.3), 30),
  who={"nina": (X(WORK, 0.2), 0, "neutral", {"arms": [30, 30], "head": [0, 8]})},
  note="Tuesday. She hates her JOB: Nina at work, tired, at a counter")
S("L15", MV((CAR - 1.0, -2.1, 0.75), (CAR, 0.0, 0.7), (CAR - 0.7, -1.9, 0.78), (CAR, 0.0, 0.7), 34),
  note="the family car's dented door")
S("L15.1", C3((CAR - 0.4, -2.3, 1.45), (CAR - 0.05, -1.6, 1.4), 28),
  who={"me": (X(CAR - 0.05, -1.6), 0, "wide", {}), },
  note="me stunned, then trying not to laugh")
raw("me", "L15.1+0.9", expr="grin")

# ===================================================================================================== 05 I write back, L16 to L24
S("L16", MV((0.8, 1.5, 1.55), (-1.25, 1.5, 1.3), (0.5, 1.5, 1.5), (-1.25, 1.5, 1.3), 26),
  who={"me": sit_me("worried", head=[0, 8])}, look={"cutwall": True},
  note="me, guilty, hand on the cover")
cue("L17", "pageturn")
S("L17", MV((-0.9, 2.05, 1.2), (-0.365, 1.5, 0.79), (-0.72, 1.95, 1.05), (-0.365, 1.5, 0.79), 36),
  who={"me": sit_me("worried", head=[0, 18])},
  note="me turning the page anyway")
cue("L18", "pen", d="blue", on=1)
S("L18", MV((-0.45, 0.8, 0.98), (-0.365, 1.43, 0.79), (-0.42, 0.9, 0.9), (-0.365, 1.43, 0.79), 36), hand=0.0,
  note="my blue pen over the page")
write("blue", "L19", "blue", dur=1.5, to=1.0, tag="mine1")
S("L19", MV((-0.45, 0.85, 0.95), (-0.365, 1.43, 0.79), (-0.4, 0.95, 0.88), (-0.365, 1.43, 0.79), 36), hand=0.0,
  note="my blue line appearing under hers")
cue("L20", "pen", d="blue", on=0)
S("L20", MV((-0.42, 0.9, 0.9), (-0.365, 1.43, 0.79), (-0.38, 0.98, 0.86), (-0.365, 1.43, 0.79), 40), hand=0.0,
  note="close on my short blue line")
# P01: the 0.6 s drop; the page, nothing moving
S("P01", MV((-0.705, 1.43, 1.05), (-0.365, 1.43, 0.79), (-0.605, 1.43, 0.98), (-0.365, 1.43, 0.79), 36), hand=0.0,
  note="the drop: the page, nothing moving")
S("L21", MV((-0.805, 1.43, 1.2), (-0.365, 1.43, 0.79), (-0.625, 1.43, 1.0), (-0.365, 1.43, 0.79), 36), hand=0.0,
  note="The ink STOPPED: the page, still")
cue("L22", "answer")
write("blue", "L22.1", "lilac", dur=2.2, to=0.55, tag="ans1")
S("L22", MV((-0.705, 1.33, 1.0), (-0.365, 1.43, 0.79), (-0.525, 1.35, 0.9), (-0.365, 1.43, 0.79), 36), hand=0.0,
  note="lilac ink starting again under my line, slower")
write("blue", "L23", "lilac", dur=0.5, to=0.62, tag="ans1")
S("L23", MV((-0.605, 1.43, 0.92), (-0.365, 1.43, 0.79), (-0.525, 1.43, 0.88), (-0.365, 1.43, 0.79), 36), hand=0.0,
  note="close on her short line")
S("L23+0.55", MV((0.7, 1.5, 1.45), (-1.25, 1.5, 1.3), (0.45, 1.5, 1.42), (-1.25, 1.5, 1.3), 26),
  who={"me": sit_me("scared", head=[0, 6])}, look={"cutwall": True},
  note="Who are YOU? me, scared")
openb("blue", "L24", 0.0, 0.2)
S("L24", MV((-0.805, 2.15, 1.2), (-0.365, 1.43, 0.79), (-0.705, 2.0, 1.05), (-0.365, 1.43, 0.79), 36),
  who={"me": sit_me("scared", arms=[80, 80])},
  note="I shut it: snapping it shut")
S("L24.1", MV((-2.5, 2.2, 1.7), (-1.2, 3.8, 0.85), (-2.2, 2.4, 1.6), (-1.2, 3.8, 0.85), 30),
  who={"me": (X(-2.05, 3.8, 0.83), -90, "wide", {"lean": -90, "blink": False})},
  note="I didn't SLEEP: lying awake")

# ===================================================================================================== 06 every night, L25 to L31
cue("L25", "clock", h=0, m=20)
for k, (t, dx) in enumerate((("L25", 0), ("L25.1", 0), ("L25.2", 0))):
    pass
openb("blue", "L25", 1.0, 0.3)
S("L25", MV((-0.905, 2.2, 1.25), (-0.365, 1.43, 0.79), (-0.805, 2.05, 1.1), (-0.365, 1.43, 0.79), 34),
  who={"me": sit_me("worried", head=[0, 14])},
  note="night after night: the diary opening on my desk, lamp-lit insert")
write("blue", "L25.1", "lilac", dur=1.4, to=1.0)
S("L25.1", MV((-0.7, 2.0, 1.1), (-0.365, 1.5, 0.79), (-0.55, 1.95, 1.0), (-0.365, 1.5, 0.79), 36), hand=0.0,
  note="insert two")
write("blue", "L25.2", "lilac", dur=1.0, to=1.0)
S("L25.2", MV((0.7, 1.9, 1.2), (-1.2, 1.5, 1.2), (0.5, 1.8, 1.2), (-1.2, 1.5, 1.2), 30),
  who={"me": sit_me("worried", head=[0, 10])}, look={"cutwall": True},
  note="insert three")
cue("L26", "answer")
write("blue", "L26", "lilac", dur=1.4, to=1.0)
S("L26", MV((-0.655, 1.43, 0.96), (-0.365, 1.43, 0.79), (-0.505, 1.43, 0.9), (-0.365, 1.43, 0.79), 36), hand=0.0,
  note="it kept ANSWERING: the page, the tally ticks up")
cue("L27", "answer")
write("blue", "L27", "lilac", dur=0.9, to=1.0)
S("L27", MV((0.7, 1.9, 1.45), (-1.25, 1.5, 1.3), (0.45, 1.7, 1.4), (-1.25, 1.5, 1.3), 26),
  who={"me": sit_me("neutral", head=[0, 12])}, look={"cutwall": True},
  note="lilac ink filling a line fast. Me curious")
S("L27.1", MV((-0.685, 1.48, 0.95), (-0.365, 1.43, 0.79), (-0.525, 1.45, 0.88), (-0.365, 1.43, 0.79), 36), hand=0.0,
  note="only FAMILY would know: the line")
cue("L28", "mydoor", to=110, dur=0.5)
place("blue", "L28", "nightstand")
S("L28", MV((-2.0, 2.3, 1.75), (-2.05, 3.8, 1.55), (-2.05, 2.4, 1.7), (-2.05, 3.8, 1.55), 30),
  who={"me": (X(-2.05, 3.8, 0.1), 0, "squeeze", {"sit": True, "arms": [20, 20], "blink": False}),
       "mom": (X(-1.5, -0.55), 180, "soft", {})},
  look={"cutwall": False},
  note="me in bed, eyes shut tight, Mom's face lit in the doorway, then she leaves")
cue("L28.1+0.2", "mydoor", to=0, dur=0.6)
S("L28.1", MV((-1.6, 1.6, 1.4), (-1.5, -0.55, 1.35), (-1.6, 1.3, 1.4), (-1.5, -0.55, 1.35), 28),
  who={"mom": (X(-1.5, -0.55), 180, "soft", {})},
  note="Mom checks, face lit")
place("blue", "L29", "desk")
S("L29", MV((0.7, 1.9, 1.5), (-1.25, 1.5, 1.3), (0.4, 1.7, 1.45), (-1.25, 1.5, 1.3), 26),
  who={"me": sit_me("worried", head=[0, 12])}, look={"cutwall": True},
  note="me humming at my desk, worried")
write("blue", "L30", "lilac", dur=1.2, to=1.0, size=1.5)
S("L30", MV((-0.705, 1.43, 0.98), (-0.365, 1.43, 0.79), (-0.545, 1.43, 0.9), (-0.365, 1.43, 0.79), 36), hand=0.0,
  note="Thursday: lilac ink, bigger letters")
cue("L31", "pen", d="blue", on=1)
write("blue", "L31.1", "blue", dur=0.7, to=1.0, size=1.2)
S("L31", MV((-0.45, 0.85, 0.95), (-0.365, 1.43, 0.79), (-0.4, 0.95, 0.88), (-0.365, 1.43, 0.79), 36), hand=0.0,
  note="my blue line, fast")
cue("L31>", "pen", d="blue", on=0)

# ===================================================================================================== 07 the scare, L32 to L38
cue("L32", "answer")
write("blue", "L32.1", "lilac", dur=0.8, to=0.7, tag="hear")
S("L32", MV((0.65, 1.9, 1.5), (-1.25, 1.5, 1.3), (0.35, 1.8, 1.45), (-1.25, 1.5, 1.3), 26),
  who={"me": sit_me("scared", head=[40, 6])}, look={"cutwall": True},
  note="lilac ink, one short line. Me scared, looking at my wall")
S("L33", MV((0.45, 1.5, 1.5), (-1.25, 1.5, 1.36), (0.2, 1.5, 1.45), (-1.25, 1.5, 1.38), 26),
  who={"me": sit_me("squeeze")}, look={"cutwall": True},
  note="my mouth shut tight")
cue("L34", "answer")
write("blue", "L34.1", "lilac", dur=1.3, to=1.0)
S("L34", MV((0.6, 1.9, 1.45), (-1.25, 1.5, 1.3), (0.3, 1.7, 1.4), (-1.25, 1.5, 1.3), 26),
  who={"me": sit_me("worried", head=[0, 6])}, look={"cutwall": True},
  note="me whispering, and the lilac ink writing at the same time")
write("blue", "L34.3", "lilac", dur=1.0, to=1.0, shake=0.002)
S("L34.2", MV((-0.685, 1.43, 0.97), (-0.365, 1.43, 0.79), (-0.525, 1.43, 0.9), (-0.365, 1.43, 0.79), 36), hand=0.0,
  note="out LOUD, it wrote it DOWN")
cue("L35", "answer")
write("blue", "L35", "lilac", dur=1.4, to=1.0, hard=True, size=1.25)
S("L35", MV((-0.645, 1.43, 0.95), (-0.365, 1.43, 0.79), (-0.505, 1.43, 0.88), (-0.365, 1.43, 0.79), 36), hand=0.0,
  note="lilac ink, pressed hard into the page")
cue("L36", "answer")
write("blue", "L36", "lilac", dur=1.5, to=1.0, shake=0.003)
S("L36", MV((-0.645, 1.43, 0.95), (-0.365, 1.43, 0.79), (-0.505, 1.43, 0.88), (-0.365, 1.43, 0.79), 36), hand=0.0,
  note="lilac ink, shaky")
cue("L37", "answer")
cue("L37", "clock", h=0, m=0)
write("blue", "L37.1", "lilac", dur=0.8, to=1.0, shake=0.003)
write("blue", "L37.3", "lilac", dur=0.8, to=1.0, shake=0.004)
S("L37", MV((-0.5, 1.9, 0.82), (-0.31, 2.72, 0.6), (-0.45, 2.0, 0.78), (-0.31, 2.72, 0.6), 40),
  look={"cutwall": False},
  note="the clock glyph on my nightstand at 12:00")
S("L37.2", MV((-0.705, 1.43, 1.0), (-0.365, 1.43, 0.79), (-0.525, 1.43, 0.9), (-0.365, 1.43, 0.79), 36), hand=0.0,
  note="lilac ink racing across the page")
cue("L38", "mydoor", to=60, dur=0.5)
cue("L38", "lamp", n="n1", to=1.0, dur=0.4)
S("L38", MV((-0.9, -1.6, 0.5), (1.6, -0.1, 0.1), (-0.5, -1.5, 0.42), (1.6, -0.1, 0.1), 26),
  look={"cutwall": False},
  note="my door ajar: down the hall, a warm lamp clicking on under Nina's door")

# ===================================================================================================== 08 Nina's room, L39 to L48
place("blue", "L39", "held")
openb("blue", "L39", 0.0, 0.05)
S("L39", MV((-1.0, -1.0, 1.5), (-1.4, 0.9, 1.3), (-1.1, -0.7, 1.45), (-1.4, 0.9, 1.3), 28),
  who={"me": (X(-1.4, 0.9), 0, "scared", {"arms": [70, 70]})},
  note="me holding the blue diary to my chest, scared")
cue("L40", "mydoor", to=80, dur=0.4)
S("L40", MV((-2.9, -1.7, 1.2), (0.0, -0.5, 1.0), (-2.2, -1.7, 1.2), (0.6, -0.5, 1.0), 32),
  who={"me": (X(-1.1, -0.85), 0, "scared", {"arms": [70, 70]})},
  note="me crossing the hall in socks")
raw("me", "L40+0.3", pos=[1.0, -0.6], yaw=90, arms=[70, 70])
cue("L41", "ndoor", to=40, dur=0.3)
S("L41", MV((1.0, -0.8, 1.4), (1.5, 1.5, 1.2), (1.0, -0.6, 1.4), (1.5, 1.5, 1.2), 30),
  who={"me": (X(1.0, -0.6), 90, "scared", {"arms": [70, 70]})},
  look={"cutwall": False},
  note="her door open an inch, lamplight in the gap")
cue("L42", "lamp", n="n2", to=1.0, dur=0.4)
place("lilac", "L42", "ndesk")
openb("lilac", "L42", 1.0, 0.05)
cue("L42", "pen", d="lilac", on=1)
write("lilac", "L42", "lilac", dur=2.5, to=1.0)
S("L42", MV((1.22, -0.45, 1.5), (1.25, 1.5, 1.4), (1.22, -0.15, 1.5), (1.25, 1.5, 1.4), 30),
  who={"nina": (X(NI_D[0], NI_D[1], SEATZ), -70, "terrified", {"sit": True, "arms": [66, 66], "head": [0, 14]})},
  note="through the gap: Nina at her desk, the lilac diary open")
cue("L43", "lamp", n="n3", to=1.0, dur=0.4)
S("L43", MV((3.8, 0.4, 1.8), (1.2, 1.9, 1.0), (3.6, 0.5, 1.75), (1.2, 1.9, 1.0), 26),
  who={"nina": sit_ni("terrified", head=[0, 14])},
  note="her room: every lamp on, three of them")
S("L44", MV((-0.8, 1.5, 1.5), (1.25, 1.5, 1.28), (-0.6, 1.5, 1.45), (1.25, 1.5, 1.3), 30),
  who={"nina": sit_ni("terrified", head=[0, 14])}, look={"cutwall": True},
  note="Nina close, terrified, writing. Cover frame")
S("L45", MV((2.6, 1.2, 1.65), (0.55, 2.8, 0.95), (2.2, 1.6, 1.55), (0.55, 2.8, 0.95), 26),
  who={"nina": (X(0.95, 2.75), -75, "terrified", {"arms": [80, 80]})},
  note="her dresser shoved against our shared wall")
S("L46", MV((1.1, 2.6, 1.9), (0.45, 1.55, 0.8), (0.85, 2.2, 1.55), (0.45, 1.55, 0.8), 28),
  who={"nina": (X(NI_D[0], NI_D[1], SEATZ), -75, "terrified", {"sit": True, "arms": [66, 66], "head": [0, 24]})},
  note="over her shoulder: her pen moving")
write("lilac", "L47", "lilac", dur=1.3, to=1.0, tag="who")
S("L47", MV((0.7, 2.1, 1.2), (0.37, 1.57, 0.79), (0.5, 1.9, 1.0), (0.37, 1.57, 0.79), 36), hand=0.0,
  note="her lilac line close")
write("blue", "L48", "lilac", dur=1.3, to=1.0, tag="who")
cue("L48", "hud2", to=1, dur=0.5)
cue("L48+1.3", "pen", d="lilac", on=0)
S("L48", MV((-0.6, 2.0, 1.45), (-1.6, 0.1, 1.65), (-0.7, 1.8, 1.45), (-1.6, 0.1, 1.65), 28),
  who={"me": (X(-1.6, 0.1), 180, "wide", {"arms": [70, 70]})},
  look={"cutwall": False},
  note="the blue diary in my hands, the same line crawling across it. Both insets now")

# ===================================================================================================== 09 the reveal, L49 to L57
place("blue", "P02>", "pair")
place("lilac", "P02>", "pair")
openb("blue", "P02>", 1.0, 0.05)
openb("lilac", "P02>", 1.0, 0.05)
S("P02", MV((PAIR, -0.5, 1.35), (PAIR, 0.0, 0.8), (PAIR, -0.35, 1.15), (PAIR, 0.0, 0.8), 36), hand=0.0,
  note="the beat: everything stops, the two diaries side by side")
S("L49", MV((PAIR, -0.5, 1.2), (PAIR, 0.0, 0.8), (PAIR, -0.34, 1.0), (PAIR, 0.0, 0.8), 38), hand=0.0,
  note="Our diaries were never HAUNTED: identical lines")
openb("blue", "L50-0.2", 0.0, 0.3)
openb("lilac", "L50-0.2", 0.0, 0.3)
place("blue", "L50-0.2", "touch", dur=0.4)
place("lilac", "L50-0.2", "touch", dur=0.4)
cue("L50.1", "glint", dur=0.7)
S("L50", MV((GIFT - 0.02, -0.28, 0.94), (GIFT, 0.0, 0.83), (GIFT, -0.2, 0.9), (GIFT, 0.0, 0.83), 45),
  note="the two clasps glinting together (S05's framing); two lilac strokes scratched in Nina's clasp")
place("blue", "L51", "pair")
place("lilac", "L51", "pair")
openb("blue", "L51", 1.0, 0.05)
openb("lilac", "L51", 1.0, 0.05)
clear("blue", "L51")
clear("lilac", "L51")
write("blue", "L51.1", "blue", dur=0.8, to=0.5, tag="w1")
write("lilac", "L51.1", "blue", dur=0.8, to=0.5, tag="w1")
S("L51", MV((PAIR, -0.45, 1.15), (PAIR, 0.0, 0.8), (PAIR, -0.32, 1.0), (PAIR, 0.0, 0.8), 38), hand=0.0,
  note="split screen: a word in one, the same word in the other")
write("blue", "L51.2", "blue", dur=1.0, to=1.0, tag="w2")
write("lilac", "L51.2", "blue", dur=1.0, to=1.0, tag="w2")
S("L51.2", MV((PAIR - 0.14, -0.25, 0.98), (PAIR - 0.14, 0.0, 0.8), (PAIR + 0.14, -0.25, 0.98), (PAIR + 0.14, 0.0, 0.8), 55), hand=0.0,
  note="in the READER'S own handwriting: my blocky scribble on the blue page, her loopy scribble on the lilac")
S("L51b", C3((0.6, 1.5, 1.6), (-1.25, 1.5, 1.3), 26),
  who={"me": sit_me("scared", head=[0, 8])}, look={"cutwall": True},
  note="me earlier, staring at my own scribble style")
S("L51b.1", C3((-0.6, 1.5, 1.55), (1.25, 1.5, 1.38), 28),
  who={"nina": sit_ni("scared", head=[0, 8])}, look={"cutwall": True},
  note="Nina earlier, staring at hers")
place("lilac", "L51c", "ndeskdust")
openb("lilac", "L51c", 0.0, 0.01)
cue("L51c+0.5", "blow")
S("L51c", MV((-0.5, 1.75, 1.12), (1.05, 1.5, 1.2), (-0.25, 1.7, 1.08), (1.05, 1.5, 1.2), 30), look={"cutwall": True},
  who={"nina": (X(NI_D[0], NI_D[1], SEATZ), -90, "fish", {"sit": True, "arms": [66, 66], "head": [0, 22], "lean": 10, "blink": False})},
  note="Nina last week, opening the lilac diary for the first time, blowing dust off it")
S("L52", MV((0.7, 1.7, 1.45), (-1.25, 1.5, 1.3), (0.4, 1.6, 1.4), (-1.25, 1.5, 1.3), 26),
  who={"me": sit_me("neutral", head=[0, 12])}, look={"cutwall": True},
  note="me, earlier, at my desk reading (S27's framing)")
S("L53", MV((-0.7, 1.7, 1.45), (1.25, 1.5, 1.3), (-0.4, 1.6, 1.4), (1.25, 1.5, 1.3), 28),
  who={"nina": sit_ni("scared", head=[0, 12])}, look={"cutwall": True},
  note="Nina, earlier, at her desk reading, scared")
cue("L54", "pen", d="blue", on=1)
cue("L54", "pen", d="lilac", on=1)
write("blue", "L54", "blue", dur=1.2, to=1.0, tag="w3")
write("lilac", "L54", "blue", dur=1.2, to=1.0, tag="w3")
S("L54", MV((PAIR, -0.6, 1.2), (PAIR, 0.0, 0.79), (PAIR, -0.45, 1.05), (PAIR, 0.0, 0.79), 34), hand=0.0,
  note="split: my blue pen, her lilac pen, writing at the same moment")
cue("L55-0.1", "pen", d="blue", on=0)
cue("L55-0.1", "pen", d="lilac", on=0)
cue("L55-0.3", "ndoor", to=80, dur=0.3)
S("L55", MV((1.4, -2.1, 1.6), (1.4, -0.9, 1.6), (1.4, -1.9, 1.6), (1.4, -0.9, 1.6), 21),
  who={"me": (X(1.15, -0.9), 90, "wide", {}), "nina": (X(1.65, -0.9), -90, "wide", {})},
  look={"cutwall": False},
  note="me and Nina face to face in her doorway, both stunned")
cue("L56", "ndoor", to=0, dur=0.3)
cue("L56", "mydoor", to=0, dur=0.3)
S("L56", MV((0.0, 1.5, 9.0), (0.0, 1.5, 0.0), (0.0, 1.5, 7.6), (0.0, 1.5, 0.0), 40),
  look={"noceil": True, "plan": True},
  note="top-down floor plan: her desk and mine on either side of one wall")
S("L56.2", MV((0.8, 2.0, 1.5), (-1.25, 1.5, 1.33), (0.5, 1.8, 1.45), (-1.25, 1.5, 1.33), 26),
  who={"me": sit_me("worried", head=[0, 0])}, look={"cutwall": True},
  note="She COULD, through our WALL")
S("L57", MV((0.0, -2.1, 1.6), (0.0, -0.9, 1.6), (0.0, -1.95, 1.6), (0.0, -0.9, 1.6), 21),
  who={"me": (X(-0.28, -0.9), 90, "worried", {}), "nina": (X(0.28, -0.9), -90, "worried", {})},
  look={"cutwall": False},
  note="both of us in the hall, the night before, at our own doors")

# ===================================================================================================== 10 make up, L58 to L67
cue("L58", "keys", to="floor") if False else None
place("blue", "L58", "held")
openb("blue", "L58", 0.0, 0.05)
S("L58", MV((3.0, 0.9, 1.6), (1.55, 1.2, 1.5), (2.8, 1.0, 1.6), (1.55, 1.2, 1.5), 26),
  who={"me": (X(1.9, 0.8), 180, "worried", {"arms": [70, 70]}), "nina": (X(1.3, 1.6), 0, "wide", {})},
  look={"cutwall": False},
  note="then she saw the blue diary in my hands")
S("L59", MV((1.0, 0.3, 1.6), (1.3, 1.6, 1.6), (1.15, 0.6, 1.6), (1.3, 1.6, 1.6), 28),
  who={"me": (X(1.9, 0.8), 180, "worried", {"arms": [70, 70]}), "nina": (X(1.3, 1.6), 0, "soft", {})},
  look={"cutwall": False},
  note="she reads it")
place("blue", "L60", "pair")
openb("blue", "L60", 1.0, 0.05)
clear("blue", "L60")
write("blue", "L60", "blue", dur=1.3, to=1.0, tag="miss")
S("L60", MV((PAIR - 0.1, -0.4, 1.0), (PAIR - 0.08, 0.1, 0.79), (PAIR - 0.08, -0.28, 0.93), (PAIR - 0.08, 0.1, 0.79), 38), hand=0.0,
  note="my blue line close")
S("L61", MV((0.3, 0.4, 1.6), (1.3, 1.6, 1.6), (0.5, 0.6, 1.6), (1.3, 1.6, 1.6), 28),
  who={"nina": (X(1.3, 1.6), 0, "laugh", {})}, look={"cutwall": True},
  note="Nina laughs")
place("lilac", "L62", "ndesk")
place("lilac", "L62+0.3", "toyou", dur=1.0)
S("L62", MV((1.6, 0.8, 1.3), (0.5, 1.5, 0.8), (1.3, 0.9, 1.2), (0.5, 1.5, 0.8), 30), hand=0.0,
  note="the lilac diary sliding across her desk to me")
place("lilac", "L63", "pair")
openb("lilac", "L63", 1.0, 0.05)
clear("lilac", "L63")
write("lilac", "L63", "lilac", dur=1.3, to=1.0, tag="miss")
S("L63", MV((PAIR + 0.2, -0.4, 1.0), (PAIR + 0.22, 0.1, 0.79), (PAIR + 0.22, -0.28, 0.93), (PAIR + 0.22, 0.1, 0.79), 38), hand=0.0,
  note="her last line close")
S("L63.1", MV((2.9, 1.0, 1.6), (1.9, 0.8, 1.6), (2.7, 1.0, 1.6), (1.9, 0.8, 1.6), 26),
  who={"me": (X(1.9, 0.8), 180, "soft", {"arms": [70, 70]})}, look={"cutwall": False},
  note="Me soft")
S("L64", MV((1.5, 2.7, 1.6), (1.5, 0.9, 1.55), (1.5, 2.45, 1.6), (1.5, 0.9, 1.55), 21),
  who={"nina": (X(1.22, 0.9), 90, "soft", {}), "me": (X(1.78, 0.9), -90, "soft", {})}, look={"cutwall": False},
  note="Nina soft, shrugging at the wastebasket")
S("L65", MV((0.6, 0.5, 1.6), (1.9, 1.3, 1.6), (0.9, 0.6, 1.6), (1.9, 1.3, 1.6), 28),
  who={"me": (X(1.9, 1.3), -90, "laugh", {})}, look={"cutwall": True},
  note="me nodding, laugh")
cue("L66", "clock", h=3, m=0)
cue("L66", "keys", to="floor")
S("L66", MV((3.9, 2.15, 1.6), (1.4, 2.15, 1.0), (3.5, 2.15, 1.5), (1.4, 2.15, 1.0), 21),
  who={"me": (X(2.2, 2.45, -0.5), 0, "laugh", {"sit": True, "arms": [20, 20]}),
       "nina": (X(2.2, 1.85, -0.5), 180, "laugh", {"sit": True, "arms": [20, 20]})},
  note="both of us on her floor, lamps on, talking, the clock glyph at 3:00")
S("L67", MV((3.6, 2.15, 1.45), (2.2, 2.15, 1.0), (3.1, 2.15, 1.35), (2.2, 2.15, 1.0), 21),
  who={"me": (X(2.2, 2.45, -0.5), 0, "grin", {"sit": True, "arms": [20, 20]}),
       "nina": (X(2.2, 1.85, -0.5), 180, "laugh", {"sit": True, "arms": [20, 20]})},
  note="both laughing, the car keys between us")
S("L67.1", MV((2.8, 2.1, 0.8), (2.2, 2.15, 0.1), (2.6, 2.1, 0.6), (2.2, 2.15, 0.1), 34), hand=0.0,
  note="the car keys on the floor between us")

# ===================================================================================================== 11 the sting, L68 to L73
cue("L68", "clock", h=10, m=10)
place("blue", "L68", "desk")
place("lilac", "L68", "ndesk")
clear("blue", "L68")
write("blue", "L68.1", "lilac", dur=1.4, to=1.0, tag="d1")
S("L68", MV((WORK - 1.2, -1.5, 1.3), (WORK, 0.2, 1.3), (WORK - 0.9, -1.4, 1.3), (WORK, 0.2, 1.3), 30),
  who={"nina": (X(WORK, 0.2), 0, "smile", {"arms": [30, 30], "head": [0, 6]})},
  note="day: Nina at work with the lilac diary")
S("L68.1", MV((0.7, 1.9, 1.45), (-1.25, 1.5, 1.3), (0.4, 1.7, 1.4), (-1.25, 1.5, 1.3), 26),
  who={"me": sit_me("smile", head=[0, 10])}, look={"cutwall": True},
  note="me at my desk with the blue, a doodle crawling across mine")
cue("L69", "clock", h=2, m=40)
clear("blue", "L69")
write("blue", "L69", "lilac", dur=0.6, to=1.0)
write("blue", "L69", "blue", dur=0.6, to=1.0)
S("L69", MV((-0.805, 1.43, 1.2), (-0.365, 1.43, 0.79), (-0.605, 1.43, 1.0), (-0.365, 1.43, 0.79), 38), hand=0.0,
  note="night: the blue diary, both our lines on the page")
write("blue", "L70", "green", dur=2.2, to=1.0, tag="third")
write("lilac", "L70", "green", dur=2.2, to=1.0, tag="third")
S("L70", MV((-0.705, 1.43, 1.05), (-0.365, 1.43, 0.79), (-0.525, 1.43, 0.92), (-0.365, 1.43, 0.79), 36), hand=0.0,
  note="under them, sea-green ink crawling. Both insets show it")
S("L71", MV((-3.2, 3.45, 1.55), (-3.2, 4.38, 1.58), (-3.25, 4.0, 1.6), (-3.25, 4.38, 1.6), 40, 75), hand=0.0,
  look={"cutwall": False},
  note="the framed bookshelf photo on my wall, a sea-green spine among the books")
S("L72", MV((0.9, 1.1, 1.65), (-1.3, 1.15, 1.55), (0.7, 1.1, 1.65), (-1.3, 1.15, 1.55), 22),
  who={"me": (X(-1.3, 1.6), 90, "worried", {}), "nina": (X(-1.3, 0.75), 90, "worried", {})},
  look={"cutwall": True},
  note="me and Nina side by side at my desk, worried")
write("blue", "L73", "green", dur=1.0, to=1.0, tag="third2")
S("L73", MV((-0.805, 1.43, 1.15), (-0.365, 1.43, 0.79), (-0.655, 1.43, 0.97), (-0.365, 1.43, 0.79), 36), hand=0.0,
  note="push in on the sea-green ink, then (loop) the blue diary close, S01's framing")

# ---------------------------------------------------------------------------------------------------- assemble
out_shots = []
for i, d in enumerate(shots):
    sh = {"id": f"S{i + 1:02d}", "cam": d["cam"], "step": d["step"], "hand": d["hand"], "note": d["note"]}
    if i:
        sh["at"] = d["at"]
    if d["follow"]:
        sh["follow"] = d["follow"]
    out_shots.append(sh)


def key_t(k):
    return tkey(k["from"]) if "from" in k else tkey(k["at"])


for who in acting:
    ks = acting[who]
    order = sorted(range(len(ks)), key=lambda j: (key_t(ks[j]), j))
    acting[who] = [ks[j] for j in order]
acting = {w: ks for w, ks in acting.items() if ks}
cues.sort(key=lambda c: tkey(c["at"]))

story = {
    "slug": "ep89-sister-diary",
    "title": "My Sister's Diary ANSWERS Me",
    "made_for_kids": False,
    "premise": "Years ago Grandma gave my big sister Nina and me matching diaries, lilac and blue, and said they only work as a set. Last week my blank diary started filling with Nina's words as she wrote, crawling across the page in my own handwriting. I wrote back under her line, and it answered.",
    "twist": "Grandma's diaries are a pair: whatever you write in one shows up in the other, in the reader's own hand. For a week I thought my sister's diary was answering me and she thought hers was answering her; each of us was the other's ghost. We talk again, and last night a third hand, in sea-green ink, wrote under both our lines.",
    "world": "a bright upstairs of two bedrooms across a short hall: my sky-blue room and my sister's lilac room, desks back to back on one shared wall, warm desk lamps, a navy night sky in the windows",
    "voice": {"voice": "am_adam", "tempo": 1.03, "rate": 1.45},
    "key_color": "#a678ff",
    "gap": GAP,
    "tail": LOOP,
    "fade_in": False,
    "fade_out": False,
    "look": {"style": "closer", "fog": "#2a3a6a", "fog_density": 0.004, "fog_start": 12.0, "sky": "#1f2f5c", "sky_strength": 0.6,
             "exposure": 0.2, "flash_safe": True, "polish": {"emph": ["L01", "L19", "L32", "L50", "L55"], "reveal": ["L38", "L44", "L55"],
                                                        "sway": []}},
    "grade": {"shadows": [0.0, 0.0, 0.04], "highlights": [0.03, 0.01, -0.02], "saturation": 1.1, "contrast": 1.05,
              "vignette": 0.22, "bloom": 0.25, "grain": 0.008},
    "phonemes": {"Nina": "nˈinə"},
    "cast": cast,
    "lines": lines,
    "shots": out_shots,
    "acting": acting,
    "cues": cues,
    "shotlook": SHOTLOOK,
    "fx": [],
    "rev": 9,
    "music": {"root": 51, "mode": "major", "bpm": 100, "seed": 89, "sections": [
        {"at": 0, "voices": ["musicbox", "pulse"], "energy": 0.35},
        {"at": "L21", "voices": ["piano", "drone"], "energy": 0.4, "mode": "minor"},
        {"at": "L25", "voices": ["piano", "drone", "pulse"], "energy": 0.5, "mode": "minor"},
        {"at": "L32", "voices": ["drone", "pulse", "choir"], "energy": 0.62, "mode": "minor"},
        {"at": "L39", "voices": ["drone", "pad"], "energy": 0.45, "mode": "minor"},
        {"at": "L49", "voices": ["pad", "piano", "musicbox"], "energy": 0.55, "mode": "major"},
        {"at": "L69", "voices": ["drone"], "energy": 0.4, "mode": "minor"}]},
    "sound": {
        "floor": "wood", "steps_db": -26, "rev": 9,
        "ambience": [{"kind": "room", "from": 0, "to": "end", "lufs": -40},
                     {"kind": "crickets", "from": "L21", "to": "L48", "lufs": -46}],
        "sfx": [{"at": "L01.4+0.05", "kind": "hit", "db": -7},
                {"at": "L09+0.4", "kind": "door", "db": -13},
                {"at": "L38.2", "kind": "click", "db": -9},
                {"at": "L61+0.1", "kind": "bell", "db": -16},
                {"at": "L70", "kind": "sting", "db": -12}] + [
            {"at": a, "kind": "scrape", "db": -25, "dur": d} for a, d in (
                ("L10.2", 0.7), ("L12+0.2", 0.8), ("L19+0.1", 0.8), ("L22.1", 0.8), ("L31+0.1", 0.5), ("L36", 0.8),
                ("L42+0.3", 0.9), ("L47", 0.8), ("L54+0.1", 0.8), ("L60+0.1", 0.8), ("L63", 0.8))],
        "music_drops": [{"from": "P01", "to": "P01>"}, {"from": "P02", "to": "P02>"}],
    },
}
OUT.write_text(json.dumps(story, indent=1, ensure_ascii=False))
print(f"wrote {OUT}: {len(out_shots)} shots, {len(cues)} cues")
