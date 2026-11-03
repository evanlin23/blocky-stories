"""Writes ../story.json for `rule-three` (batch 6, the Rulebook Keeper pilot, script.md 2026-11-03).

Run from anywhere: python stories/rule-three/generator/make_story.py
The words are in lines.json next to this file (made from script.md). The cast, the shots and their cameras, the acting,
the cues set.py reads, the score and the sound are all here.

Places (metres; z = 0 is the floor everywhere):
  THE HALL      the record room: x -5..5, y 0..7.5; the front wall (y 0 to -0.4) has the oak door at x = -2.6 and the
                arched window at x = 2.0. The street runs from the hall's steps down the hill toward -y.
  the lectern   (0, 5.2); Otis stands behind it at (0, 6.55) facing -y (yaw 0). Camera usually in front (y 2 to 4).
  DINER (200,0) PET SHOP (300,0) BRIDGE (400,0) MOM'S (500,0) OTIS'S KITCHEN (600,0)
Acting yaw: 0 faces -y, 90 faces +x, 180 faces +y, -90 faces -x. A character's right arm is arms[0] (the -x side).
"""
import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE.parent / "story.json"
lines = json.loads((HERE / "lines.json").read_text())
LOOP = 0.25
GAP = 0.12

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
_RR = re.compile(r"^(?P<id>[LP]\d\d)\.(?P<c>\d)(?P<rest>.*)$")


def R(ref):
    if not isinstance(ref, str):
        return ref
    m = _RR.match(ref)
    if not m or m.group("id") not in CHUNK_MAP:
        return ref
    return f"{m.group('id')}.{CHUNK_MAP[m.group('id')][int(m.group('c'))]}{m.group('rest')}"


# ---------------------------------------------------------------------------------------------------- cast
FACE = {"eyes": "round", "brows": True, "ink": "#24131f"}


def person(skin, shirt, pants, hair="cap", hair_c="#2a1d15", shoes="#2a2a30", eyes="round", **kw):
    d = {"age": "adult", "skin": skin, "shirt": shirt, "pattern": "solid", "pants": pants, "shoes": shoes,
         "sleeves": "long", "hair": hair, "hair_c": hair_c, "face": {**FACE, "eyes": eyes}}
    d.update(kw)
    return d


cast = {
    # The Buhkeeper: the channel's avatar (brand/render_brand.py KEEPER): top hat, swept brown fringe, teal knit coat,
    # mustard scarf, smirk resting face. set.py (dress_otis) adds only the ink thumb.
    "me": {"age": "adult", "skin": "#e7b48c", "shirt": "#2f6f6a", "pattern": "knit", "pattern_c": "#285e5a",
           "collar": "#f2e6c8", "pants": "#26303f", "shoes": "#1b1b20", "sleeves": "long",
           "hair": "swoop", "hair_c": "#5a3a22", "hat": "tophat", "hat_c": "#1f2b33",
           "extras": ["scarf", "coat"], "extra_c": "#e0a32a", "face": {"eyes": "dot", "brows": True}},
    "milo": person("#e6b48a", "#ff8a1f", "#8a8d96", "cap", "#c99a4e", shoes="#f2f2f2", extras=["hooddown"]),
    "milo_h": person("#e6b48a", "#ff8a1f", "#8a8d96", "none", "#d9b46a", shoes="#f2f2f2", hat="hood", hat_c="#ff8a1f"),
    "mom": person("#f0c6a4", "#b69be0", "#4a4658", "bun", "#c7cbd6", shoes="#6a4a3a", eyes="lashes", collar="#f4ecd8"),
    "cook": person("#d9a27a", "#f4f4f4", "#3a3d44", "cap", "#3a2a20", extras=["apron"], extra_c="#ffffff"),
    "mailman": person("#b88660", "#243a7a", "#243a7a", "buzz", "#1a1410", shoes="#14141a"),
    "jogger": person("#f1c9a0", "#17b3a6", "#17b3a6", "bun", "#5a3a22", shoes="#f2f2f2", eyes="lashes"),
}
TOWN = [
    ("#d9a27a", "#ffd95a", "#3a5aa6", "spiky", "#2a1d15"), ("#f1c9a0", "#ff8a6b", "#2a2d3a", "long", "#8a4a22"),
    ("#8a5a3c", "#7cc6ff", "#3a3d4a", "cap", "#1a1410"), ("#e0b48c", "#58c24a", "#d9d2c0", "bun", "#c0c0c8"),
    ("#a8704a", "#ff9ec8", "#2a3a5a", "swoop", "#3a2418"), ("#f1c9a0", "#b69be0", "#3a3d44", "cap", "#d9b86a"),
    ("#6e4a33", "#f2f2f2", "#6a3a2a", "buzz", "#1a1410"), ("#c68c5a", "#2fb5b5", "#3a3040", "long", "#2a1d15"),
]
for i, (sk, sh, pa, ha, hc) in enumerate(TOWN):
    cast[f"t{i}"] = person(sk, sh, pa, ha, hc, eyes="lashes" if i in (1, 3, 4, 7) else "round")
GUESTS = [
    ("#e0b48c", "#ff6a6a", "#2a3a5a", "swoop", "#5a3a22"), ("#8a5a3c", "#ffd95a", "#3a3d4a", "buzz", "#1a1410"),
    ("#f1c9a0", "#58c2c2", "#6a3a2a", "bun", "#2a1d15"), ("#c68c5a", "#9ad06a", "#3a3040", "cap", "#3a2418"),
]
for i, (sk, sh, pa, ha, hc) in enumerate(GUESTS):
    cast[f"g{i}"] = person(sk, sh, pa, ha, hc, eyes="lashes" if i in (0, 2) else "round")

# ---------------------------------------------------------------------------------------------------- helpers
LINE_NO = {ln["id"]: i + 1 for i, ln in enumerate(lines)}
_REF = re.compile(r"^(?P<id>[LP]\d\d)(?:\.(?P<c>\d))?(?P<tail>>)?(?P<o>[+-]\d+(?:\.\d+)?)?$")


def tkey(ref):
    """A sortable number for an anchor like "L12.1+0.4", so keys go in order without the voice timings."""
    if isinstance(ref, (int, float)):
        return float(ref)
    m = _REF.match(ref)
    base = LINE_NO[m.group("id")]
    return base * 100 + int(m.group("c") or 0) * 12 + (99 if m.group("tail") else 0) + float(m.group("o") or 0)


def fmt(a):
    return round(a, 3) if isinstance(a, (int, float)) else a


acting = {w: [] for w in cast}
cues = []
shown = {w: True for w in cast}
NEUTRAL = {"arms": [0, 0], "side": [0, 0], "head": [0, 0], "lean": 0, "tremble": 0, "blink": True}


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


def walk(who, at, pos, **kw):
    raw(who, at, pos=list(pos), **kw)


def cue(at, name, **kw):
    cues.append({"at": R(at), "name": name, **kw})


shots = []


def S(at, cam, who=None, tod=None, note="", step=2, hand=0.006, follow=None):
    """A shot. cam = (loc, tgt, lens) or (loc, tgt, lens, loc2, tgt2, lens2) for a move. who = {name: (pos, yaw, expr, kw)}."""
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
    if tod:
        cue(at, "tod", n=tod, dur=0.45)
    if len(cam) == 3:
        keys = [[0, list(cam[0]), list(cam[1]), cam[2]]]
    else:
        keys = [[0, list(cam[0]), list(cam[1]), cam[2]], [1, list(cam[3]), list(cam[4]), cam[5]]]
    shots.append({"at": R(at), "cam": keys, "step": step, "hand": hand, "note": note, "follow": follow})


def X(x, y, z=0.0):
    return [x, y, z]


# ---- zones and fixed spots
LECT = (0.0, 5.15)
OT = (0.0, 6.05)          # Otis behind the lectern
DINER, PET, BRIDGE, MOM, KIT = 200.0, 300.0, 400.0, 500.0, 600.0

# ---- the montage's people along the street (L06, L24, L25)
CROWD = [(-1.5, -12), (1.8, -11), (-4.1, -16), (4.3, -15), (0.2, -19), (-2.2, -25), (2.6, -23), (4.6, -31)]
DOWN = lambda c: c

# =========================================================================================== 01 the warning, L01 to L02
cue(0, "spread", n="stub")
cue(0, "clock", v=[9, 0])
cue(0, "stamp", mode="rest")
cue(0, "ppage", mode="pocket")
cue(0, "door", v=[0])
S(0, ((-0.03, 4.75, 3.35), (-0.03, 5.2, 1.0), 35, (-0.03, 4.78, 2.55), (-0.03, 5.2, 1.0), 35), tod="night", hand=0.0,
  note="top-down push on the stub: ragged torn edge, thumbprint, the next page marked 5")
S("L02", ((-0.05, 5.1, 1.9), (-0.06, 5.2, 1.0), 35, (-0.06, 5.12, 1.55), (-0.065, 5.2, 1.0), 35), hand=0.0,
  note="punch in to the torn edge, the thumbprint filling a third of the frame")
cue("L01.3+0.1", "sfx_hint", note="stamp thunk on OBEYS")

# =========================================================================================== 02 the rule at work, L03 to L06
S("L03", ((DINER + 0.35, -0.2, 1.45), (DINER + 0.1, 2.6, 1.35), 32, (DINER + 0.3, 0.1, 1.45), (DINER + 0.1, 2.6, 1.35), 32),
  who={"cook": (X(DINER, 2.95), 0, "neutral", {"arms": [0, 52], "head": [20, -4], "look": [0.9, 0.4]})}, tod="day",
  note="the cook reaches for the radio, eyes flicking out the window toward the hall")
S("L04", ((-2.2, -18.0, 1.4), (2.4, -13.8, 1.4), 30, (-2.0, -17.5, 1.4), (2.0, -13.8, 1.4), 30),
  who={"mailman": (X(3.6, -14.0), 0, "neutral", {"head": [-30, 0]})},
  note="the mailman mid-turn, already stepping off the curb, glancing up the hill")
walk("mailman", "L04+0.1", X(3.5, -14.0))
walk("mailman", "L04>", X(1.3, -13.7))
S("L05", ((PET + 0.1, -1.6, 1.4), (PET + 0.0, 1.6, 1.3), 40), tod="day",
  note="the parrot in the pet shop window, beak open, head cocked")
CROWD_START = {f"t{i}": (X(x, y), (i * 53) % 360 - 180, "neutral") for i, (x, y) in enumerate(CROWD)}
S("L06", ((0.0, -36.0, 0.9), (0.0, -14.0, 1.7), 24, (0.4, -33.0, 1.0), (0.0, -14.0, 1.7), 24), who=CROWD_START, tod="day",
  note="low wide up the bright high street: the whole town turns to face the hall")
for i in range(8):
    raw(f"t{i}", "L06.1+0.2", yaw=180, blend=0.5)
S("L06.2+0.25", ((0.0, -26.0, 0.5), (1.6, 0.0, 3.2), 30, (0.3, -20.0, 0.7), (1.6, 0.0, 3.6), 30), tod="dusk",
  note="the white hall and its arched window from below, push in")

# =========================================================================================== 03 me and the book, L07 to L13
OTIS_STAMP = {"arms": [60, 0]}
S("L07", ((0.55, 3.2, 1.55), (0.0, 6.0, 1.4), 40, (0.35, 3.5, 1.55), (0.0, 6.0, 1.4), 40),
  who={"me": (OT, 0, "smirk", {"arms": [50, 0]})}, tod="night", note="Otis at the lectern, the pocket page's corner showing")
S("L08+0.3", ((-2.4, 4.0, 3.15), (-5.0, 4.0, 3.15), 34), who={"me": (OT, 0, "smirk", {"arms": [50, 0]})},
  note="the brass clock at nine")
cue("L08", "clock", v=[9, 0])
S("L08.2", ((0.5, 3.4, 2.3), (-0.2, 5.6, 1.2), 34), who={"me": (OT, 0, "smirk", {"arms": [50, 0]})},
  note="the red-knobbed stamp comes down on a fresh page, ink-blue thumb")
cue("L08.2", "spread", n="fresh")
cue("L08.2-0.5", "stamp", mode="hand")
raw("me", "L08.2-0.4", arms=[112, 0], blend=0.25)
raw("me", "L08.2", arms=[92, 0], blend=0.1)
raw("me", "L08.2+0.3", arms=[112, 0], blend=0.25)
raw("me", "L08.2+0.8", arms=[50, 0], blend=0.3)
cue("L08.2+0.8", "stamp", mode="rest")
S("L09", ((-2.1, 2.3, 1.05), (-2.6, 0.1, 1.0), 34), tod="night", note="a folded slip drops through the brass slot into the basket")
cue("L09-0.2", "slip", mode="path", v=[-2.6, -0.5, 1.1, 0, 0])
cue("L09+0.2", "slip", mode="path", v=[-2.6, -0.5, 1.1, 0, 0])
cue("L09+0.7", "slip", mode="path", v=[-2.6, 0.12, 1.1, 0, 0])
cue("L09+1.1", "slip", mode="path", v=[-2.6, 0.38, 0.36, 0, 0])
cue("L09.1", "slip", mode="path", v=[-2.6, 0.4, 0.3, 0, 0])
S("L09.2", ((0.9, 3.3, 1.9), (-0.45, 5.7, 1.45), 36), who={"me": (OT, 0, "smirk", {"arms": [78, 0]})},
  note="my hand lifting one slip out")
cue("L09.2-0.1", "slip", mode="hand")
cue("L10-0.1", "slip", mode="hide")
S("L10", ((1.35, 3.0, 0.3), (0.6, 4.6, 0.38), 28, (1.2, 3.1, 0.3), (0.75, 4.6, 0.4), 28), hand=0.0,
  note="the lore shot: low on the lectern's seamless stone base against the brick, not narrated")
S("L11", ((0.2, 3.9, 1.75), (0.35, 5.1, 1.0), 42), note="last night's page: a little drawn bridge")
cue("L11-0.05", "spread", n="last")
S("L12", ((BRIDGE - 1.0, -6.0, 2.1), (BRIDGE + 0.2, 0.0, 1.3), 30), tod="day",
  who={"jogger": (X(BRIDGE - 3.8, 0.0, 0.86), 90, "fish", {})}, note="a bright morning, the stone bridge: the jogger mid-stride, lips pursed")
walk("jogger", "L12+0.05", X(BRIDGE - 3.8, 0.0, 0.86), run=True)
walk("jogger", "L12.1+0.1", X(BRIDGE + 0.5, 0.0, 0.86), run=True)
raw("jogger", "L12.1+0.1", yaw=0, expr="fish")
S("L12.2", ((BRIDGE + 2.0, -4.2, 1.6), (BRIDGE + 0.5, 0.0, 1.5), 40),
  who={"jogger": (X(BRIDGE + 0.5, 0.0, 0.86), 0, "fish", {"side": [10, 10]})},
  note="she freezes mid-whistle, then sheepish")
raw("jogger", "L12.2+0.35", expr="sad-smile", blend=0.1)
S("L13", ((-3.4, 1.5, 2.0), (-0.3, 5.3, 1.1), 24), tod="night", who={"me": ((-1.5, 5.15), 40, "smirk", {})},
  note="wide on the open book, its fat block of stamped pages, me small beside it")
S("L13.2-0.15", ((0.3, 3.3, 1.5), (0.0, 6.0, 1.42), 46), who={"me": (OT, 0, "smirk", {"arms": [40, 0]})},
  note="close on me closing the clasp")

# =========================================================================================== 04 the fight, L14 to L21
S("L14", ((-0.4, -6.2, 1.45), (-2.6, -1.4, 1.4), 32), tod="dusk",
  who={"milo": (X(-3.2, -1.7), 25, "angry", {"head": [10, 0]}), "me": (X(-1.9, -1.7), -20, "smirk", {})},
  note="the hall door at dusk: Milo and me side by side, clearly brothers")
S("L14.1", ((-3.1, -4.6, 1.55), (-3.15, -1.6, 1.5), 44),
  who={"milo": (X(-3.2, -1.7), 20, "angry", {"arms": [0, 100], "head": [-20, 0]}), "me": (X(-1.9, -1.7), -20, "smirk", {})},
  note="Milo jabbing a thumb at the hall")
S("L15", ((0.6, 3.35, 1.55), (0.78, 4.72, 1.62), 46, (0.78, 3.3, 1.55), (0.78, 4.72, 1.62), 46), tod="night", note="a framed photo of Mom on the lectern")
S("L15.1", ((2.4, 3.2, 1.85), (5.0, 3.5, 1.85), 34), note="a calendar with one date circled in red")
S("L16", ((-1.6, 3.4, 1.55), (-1.6, 1.2, 1.5), 40), who={"milo": ((-1.6, 1.2), 180, "angry", {"arms": [0, 88]})},
  note="Milo close, pointing at me: come for once")
S("L17", ((-1.6, 3.4, 1.55), (-1.6, 1.2, 1.55), 40), who={"milo": ((-1.6, 1.2), 180, "grin", {"arms": [0, 150]})},
  note="Milo grinning, one hand up like a toast")
S("L17.2-0.1", ((0.4, 3.3, 1.5), (0.0, 6.0, 1.45), 46), who={"me": (OT, 0, "worried", {})}, note="me, worried")
S("L18", ((2.8, 1.2, 1.5), (-0.2, 3.5, 1.35), 30),
  who={"me": ((0.3, 3.6), 130, "smirk", {"head": [-60, 0]}), "milo": ((-1.5, 1.7), 150, "angry", {})},
  note="I turn back to the lectern, Milo behind me in the doorway")
walk("me", "L18+0.2", (0.3, 3.6))
walk("me", "L18>", (0.0, 4.2))
S("L19", ((2.3, 4.4, 1.7), (1.0, -12.0, 1.1), 26), tod="dusk",
  who={"me": (X(2.0, 1.1), 0, "worried", {}), "milo_h": (X(0.6, -4.0), 180, "angry", {})},
  note="over my shoulder at the window: Milo walking off down the hill, hood up")
walk("milo_h", "L19+0.1", X(0.6, -4.0))
walk("milo_h", "L19>", X(0.5, -20.0))
S("L20", ((-2.6, -2.2, 1.2), (-2.6, 0.0, 1.1), 36, (-2.6, -1.7, 1.2), (-2.6, 0.0, 1.1), 36), tod="dusk", hand=0.0,
  note="the brass slot at dusk, a folded slip pushed through by an orange sleeve")
cue("L20", "sleeve", on=True)
cue("L20", "slip", mode="path", v=[-2.6, -0.34, 1.1, 0, 0])
cue("L20+0.6", "slip", mode="path", v=[-2.6, -0.34, 1.1, 0, 0])
cue("L20.2", "slip", mode="path", v=[-2.6, -0.05, 1.1, 0, 0])
cue("L20.2+0.5", "sleeve", on=False)
S("L21", ((-0.2, 3.9, 1.5), (-0.4, 5.5, 1.45), 46, (-0.3, 3.2, 1.5), (-0.4, 5.5, 1.45), 46), tod="night",
  who={"me": (OT, 0, "worried", {"arms": [80, 0]})}, note="the slip unfolded: one big scrawled pencil 3, me beyond it")
cue("L21-0.05", "slip", mode="hand")
cue("L21-0.05", "slipface", n="three")

# =========================================================================================== 05 the town turns, L22 to L29
S("L22", ((-2.4, 4.0, 3.15), (-5.0, 4.0, 3.15), 34), who={"me": (OT, 0, "smirk", {})}, note="the brass clock at eight thirty")
cue("L22", "clock", v=[8, 30])
cue("L22", "slip", mode="hide")
S("L22.2", ((0.5, 3.2, 1.55), (0.0, 6.0, 1.45), 40), who={"me": (OT, 0, "smirk", {"arms": [40, 0]})},
  note="just me and the book, warm and quiet")
S("L23", ((0.3, 3.5, 1.55), (0.0, 6.0, 1.5), 46), who={"me": (OT, 0, "worried", {"head": [25, -4]})},
  note="I look up. The street goes quiet.")
TOWN_STOP = {f"t{i}": (X(x, y), 180, "neutral", {"head": [0, -14]}) for i, (x, y) in enumerate(CROWD)}
TOWN_STOP["t4"] = (X(0.4, -9.5), 180, "neutral", {"head": [0, -14]})
S("L24", ((2.5, 3.9, 1.7), (2.0, -12.0, 1.1), 28, (2.4, 3.6, 1.7), (2.0, -12.0, 1.1), 28),
  who={"me": (X(1.25, 1.1), 0, "scared", {}), **TOWN_STOP}, tod="night", note="over my shoulder through the arched window: everyone has stopped")
NEAR = {f"t{i}": (X(x, y), 180, "neutral", {"head": [0, -24]})
        for i, (x, y) in enumerate([(0.2, -3.6), (1.6, -3.4), (3.0, -3.7), (4.3, -3.5), (-0.4, -5.6), (1.0, -5.9), (2.4, -5.7), (3.8, -6.0)])}
S("L25", ((2.0, 1.5, 2.5), (2.0, -7.0, 1.2), 20, (2.0, 0.6, 2.1), (2.0, -7.0, 1.2), 20), who=NEAR,
  note="a slow push down onto the street: eight townsfolk, every face tipped up")
S("L25.1+0.17", ((2.0, -4.2, 1.5), (2.0, 0.6, 1.75), 40), who={"me": (X(2.0, 0.85), 0, "scared", {})},
  note="the reverse: me in the window, small and lit")
GUESTS_STILL = {"g0": (X(MOM - 1.8, 2.0), 0, "neutral", {"head": [0, -14]}), "g1": (X(MOM - 0.7, 2.4), 0, "neutral", {"head": [0, -14]}),
                "g2": (X(MOM + 0.9, 2.1), 0, "neutral", {"head": [0, -14]}), "g3": (X(MOM + 1.9, 2.5), 0, "neutral", {"head": [0, -14]}),
                "mom": (X(MOM + 0.1, 1.6), 0, "neutral", {"head": [0, -30]})}
S("L26", ((MOM + 0.2, -2.6, 2.15), (MOM, 2.4, 1.3), 28, (MOM + 0.1, -2.2, 2.1), (MOM, 2.4, 1.3), 28), who=GUESTS_STILL,
  note="through Mom's lit front window: the party guests standing still, all turned uphill")
S("L26.1+0.22", ((MOM + 0.1, -1.9, 1.7), (MOM + 0.1, 1.6, 1.65), 46),
  who={"mom": (X(MOM + 0.1, 1.6), 0, "neutral", {"head": [0, -16], "arms": [0, 70]})}, note="Mom in her paper crown, face tipped up, a slice on her plate")
cue("L26.1+0.22", "plate", v=[MOM - 0.15, 1.2, 0.98])
cue("L27", "plate", v=None)
S("L27", ((0.2, 3.3, 1.5), (0.0, 6.0, 1.35), 52), tod="night", who={"me": (OT, 0, "scared", {})},
  note="me, scared, the folded page corner in my pocket")
S("L28", ((-1.0, 4.5, 1.5), (-2.8, 0.0, 1.5), 28), who={"me": (OT, 0, "scared", {})}, hand=0.004,
  note="the oak door swings open")
cue("L28", "door", v=[0])
cue("L28+0.3", "door", v=[0])
cue("L28+0.55", "door", v=[100])
S("L28.1+0.1", ((-1.0, 4.5, 1.5), (-2.7, 0.0, 1.45), 32),
  who={"me": (OT, 0, "scared", {}), "milo": (X(-2.5, -0.15), 180, "worried", {"head": [0, 4]})},
  note="Milo in the doorway, chest heaving, hood down")
S("L29", ((-2.0, 3.5, 1.6), (-2.55, 0.0, 1.5), 46), who={"milo": (X(-2.55, 0.2), 180, "worried", {})},
  note="Milo close, mid-question")

# =========================================================================================== 06 it was me, L30 to L36
MILO_AT = (-1.35, 4.2)
S("L30", ((0.45, 3.1, 1.55), (0.0, 6.0, 1.47), 48), who={"me": (OT, 0, "sheepish", {}), "milo": (MILO_AT, 180, "worried", {})},
  note="I tell him. It was me. (sheepish, meeting his eyes)")
S("L31", ((-0.45, 4.3, 1.95), (-0.2, 5.3, 1.02), 40), who={"me": (OT, 0, "sheepish", {"arms": [30, 0]}), "milo": (MILO_AT, 180, "worried", {})},
  note="the page drawn from my pocket and held up beside the stub, its torn edge matching (cover frame)")
cue("L31-0.05", "ppage", mode="world", v=[0.15, 6.3, 1.5, 0, -90])
cue("L31+0.7", "ppage", mode="world", v=[-0.36, 5.15, 1.28, 0, -90])
cue("L31", "spread", n="stub")
S("L32", ((-0.1, 3.9, 1.5), (-0.4, 5.6, 1.4), 42), who={"me": (OT, 0, "sheepish", {"arms": [85, 0]}), "milo": (MILO_AT, 180, "worried", {})},
  note="the page close: glyph rows and a half 3 at the torn top, my thumb on it")
cue("L32-0.05", "ppage", mode="hand")
S("L33", ((-0.3, 2.3, 1.55), (-1.35, 4.2, 1.5), 38), who={"me": (OT, 0, "sheepish", {}), "milo": (MILO_AT, 20, "worried", {"head": [15, 6]})},
  note="Milo looks from the page to the huge book")
S("L33.3", ((0.7, 0.9, 2.0), (-0.65, 5.2, 1.2), 20, (0.3, 1.3, 1.9), (-0.65, 5.2, 1.2), 20), who={"me": (OT, 0, "sheepish", {}), "milo": (MILO_AT, 20, "worried", {})},
  note="a wide of the hall: the two of us and the book between us")
S("L34", ((0.05, 4.2, 1.9), (0.0, 5.15, 1.2), 40), who={"me": (OT, 0, "sheepish", {}), "milo": (MILO_AT, 20, "worried", {})},
  note="the stub close (A torn page still counts)")
cue("L34", "ppage", mode="world", v=[-0.36, 5.15, 1.28, 0, -90])
S("L34.3", ((0.5, 3.1, 1.5), (0.0, 6.0, 1.4), 46), who={"me": (OT, 0, "sheepish", {"arms": [60, 0], "head": [-20, 0]}), "milo": (MILO_AT, 20, "worried", {})},
  note="me folding the page shut, glancing at Milo")
cue("L34.3", "ppage", mode="hand")
S("L35", ((0.3, 4.4, 1.9), (0.2, 5.2, 1.0), 40), who={"me": (OT, 0, "smirk", {"arms": [30, 0]}), "milo": (MILO_AT, 20, "worried", {})},
  note="my hand flicks the pages back to an old page: my first night's")
cue("L35-0.05", "ppage", mode="pocket")
cue("L35", "spread", n="old")
S("L35.2", ((0.5, 3.1, 1.5), (0.0, 6.0, 1.45), 46), who={"me": (OT, 0, "sheepish", {"side": [0, 8]}), "milo": (MILO_AT, 20, "worried", {})},
  note="me, sheepish, a small shrug")
S("L36", ((2.4, 6.6, 1.6), (-1.2, 4.2, 1.55), 40), who={"me": (OT, 0, "sheepish", {}), "milo": (MILO_AT, 125, "worried", {})},
  note="Milo close, worried softening")
raw("milo", "L36", expr="worried", yaw=125)
raw("milo", "L36+0.5", expr="neutral", blend=0.2)
S("L36.1", ((-2.4, 4.0, 3.15), (-5.0, 4.0, 3.15), 34), note="the brass clock at eight fifty")
cue("L36.1", "clock", v=[8, 50])

# =========================================================================================== 07 the loophole, L37 to L41
S("L37", ((0.8, 1.6, 1.7), (-1.1, 4.4, 1.6), 32), who={"me": (OT, 0, "smile", {}), "milo": ((-1.15, 4.4), 0, "grin", {"arms": [0, 100]})},
  note="Milo, grinning, slapping the side of the book")
raw("milo", "L37+0.3", arms=[0, 100], blend=0.1)
cue("L37", "book", mode="open")
S("L38", ((7.5, -2.0, 1.4), (-2.3, -2.0, 1.2), 22, (7.5, -2.6, 1.4), (-2.3, -2.6, 1.2), 22),
  who={"milo": (X(-2.6, -1.8), 180, "grin", {"arms": [70, 70]}), "me": (X(-2.6, -0.65), 0, "smile", {"arms": [70, 70]})},
  note="the two of us hauling the red book out of the hall door, Milo walking backward at the front")
cue("L38-0.6", "tod", n="dusk", dur=0.45)   # finish before S54 cuts in: a ramp on screen flashed (rescue r3)
cue("L38", "book", mode="carry")
walk("milo", "L38+0.1", X(-2.6, -1.8), keep_yaw=True, yaw=180)
walk("milo", "L38.2", X(-2.3, -3.6), keep_yaw=True, yaw=180)
walk("me", "L38+0.1", X(-2.6, -0.65))
walk("me", "L38.2", X(-2.3, -2.4))
cue("L38", "bookpath", v=[-2.6, -1.2, 1.05])
cue("L38.2", "bookpath", v=[-2.3, -3.0, 1.05])
LINE = {f"t{i}": (X(x, y), 90 if x < 0 else -90, "smile", {}) for i, (x, y) in enumerate(
    [(-3.4, -7), (3.4, -9), (-3.5, -12), (3.4, -14), (-3.4, -17), (3.5, -19), (-3.4, -23), (3.4, -25)])}
S("L38.2", ((3.6, -2.4, 1.9), (-1.8, -4.4, 1.25), 26, (3.55, -2.75, 1.9), (-1.6, -4.85, 1.25), 26),
  who={"milo": (X(-2.3, -3.6), 140, "grin", {"arms": [70, 70]}), "me": (X(-2.3, -2.4), 0, "smile", {"arms": [70, 70]}), **LINE},
  note="Milo walking backward at the front, face and the red book in frame, the townsfolk stepping aside and smiling")
walk("milo", "L38.2+0.1", X(-2.3, -3.6), keep_yaw=True, yaw=140)
walk("milo", "L38>", X(-0.8, -6.6), keep_yaw=True, yaw=140)
walk("me", "L38.2+0.1", X(-2.3, -2.4))
walk("me", "L38>", X(-0.8, -5.4))
cue("L38.2+0.1", "bookpath", v=[-2.3, -3.0, 1.05])
cue("L38>", "bookpath", v=[-0.8, -6.0, 1.05])
TABLE_Y = 3.6
S("L39", ((MOM - 0.9, 0.5, 1.5), (MOM - 0.1, 4.5, 1.15), 26, (MOM - 0.7, 1.0, 1.5), (MOM - 0.1, 4.5, 1.15), 26),
  who={"mom": (X(MOM, 4.9), 0, "smile", {}), "me": (X(MOM + 1.35, 3.5), -90, "smile", {"arms": [72, 0]})},
  note="Mom's bright dining room: Mom in her paper crown, the giant book across the table among cake plates; my stamp coming down")
cue("L39", "tod", n="night", dur=0.45)   # quick, inside the dining room (rescue r3: a long ramp flashed)
cue("L39-0.3", "stamp", mode="hand")
raw("me", "L39", arms=[112, 0], blend=0.2)
cue("L39", "book", mode="table")
cue("L39", "spread", n="fresh")
BK = (MOM + 0.3, 3.55)
S("L39.1+0.3", ((MOM + 0.9, 1.7, 2.0), (BK[0], BK[1], 1.2), 30, (MOM + 0.8, 1.9, 1.9), (BK[0], BK[1], 1.15), 30),
  who={"mom": (X(MOM, 4.9), 0, "smile", {}), "me": (X(MOM + 1.35, 3.5), -90, "smile", {"arms": [92, 0]})},
  note="close: the red-knobbed stamp comes down on the page, ink-blue, a soft thunk")
cue("L39.1+0.3", "stamp", mode="path")
cue("L39.1+0.3", "stamppos", v=[BK[0], BK[1], 1.3])
cue("L39.1+0.5", "stamppos", v=[BK[0], BK[1], 1.3])
cue("L39.1+0.85", "stamppos", v=[BK[0], BK[1], 1.075])
cue("L39.1+1.15", "stamppos", v=[BK[0], BK[1], 1.075])
cue("L39.2+0.5", "stamppos", v=[BK[0], BK[1], 1.3])
S("L40", ((MOM - 0.7, 2.0, 1.55), (MOM - 1.4, 4.4, 1.1), 20),
  who={"milo": (X(MOM - 1.4, 4.4, -0.3), 10, "smile", {"arms": [70, 20]})},
  note="Milo seated behind the table with a pencil and a slip, smiling")
cue("L40-0.05", "stamp", mode="rest")
cue("L40-0.05", "slip", mode="path", v=[MOM - 1.5, 4.0, 0.83, 0, 0])
cue("L40-0.05", "pencil", on=True)
cue("L40.2+0.9", "pencil", on=False)
S("L40.2", ((MOM - 0.6, 2.3, 1.5), (MOM - 1.2, 3.6, 0.85), 20),
  who={"milo": (X(MOM - 1.4, 4.4, -0.3), 10, "smile", {"arms": [70, 20]})},
  note="the slip sliding across the table between the plates")
cue("L40.2", "slip", mode="path", v=[MOM - 1.5, 4.0, 0.83, 0, 0])
cue("L40.2+0.7", "slip", mode="path", v=[MOM - 1.05, 3.15, 0.83, 0, 0])
S("L41", ((MOM - 1.1, 1.6, 1.5), (MOM - 0.3, 4.9, 1.1), 34), who={"mom": (X(MOM, 4.9), 0, "smile", {"arms": [0, 60]}), "me": (X(MOM + 1.5, 3.5), -90, "smile", {})},
  note="the last slice of cake on a plate in front, Mom smiling behind it")
cue("L41", "slip", mode="hide")
cue("L41", "spread", n="cake")
cue("L41", "cakegone")
cue("L41", "plate", v=[MOM - 1.15, 3.55, 0.84])
cue("L41.1+0.1", "plate", v=[MOM - 1.15, 3.55, 0.84])
cue("L41.1+0.9", "plate", v=[MOM - 0.2, 4.4, 0.97])

# =========================================================================================== 08 the sting, L42 to L45
S("L42", ((KIT, -1.0, 1.5), (KIT, 1.3, 1.2), 30), tod="night", who={"me": (X(KIT, 1.7), 0, "smirk", {"arms": [70, 70]})},
  note="my ink-blue thumb unfolding the torn page on the table")
cue("L42", "ppage", mode="world", v=[KIT, 0.95, 0.805, 0, -90])
cue("L42", "ppage_unfold", u=0.0)
cue("L42+0.9", "ppage_unfold", u=1.0)
cue("L42.2+0.1", "ppage_face", n="back")
S("L43", ((KIT, 0.2, 1.76), (KIT, 1.0, 0.8), 62, (KIT, 0.15, 1.72), (KIT, 1.03, 0.8), 56), who={"me": (X(KIT, 1.7), 0, "scared", {"arms": [70, 70]})},
  note="the back of the page: a big ink-blue 4, me scared beyond it. The corner tag flips to 4.")
cue("L43", "tag", v=1, dur=0.04)
S("L44", ((KIT, -1.0, 1.5), (KIT, 1.3, 1.2), 30), who={"me": (X(KIT, 1.7), 0, "scared", {"arms": [70, 70]})},
  note="my hand folding it shut fast, the 4 gone under the fold")
cue("L44", "ppage_unfold", u=1.0)
cue("L44+0.25", "ppage_unfold", u=0.0)
S("L44.2", ((KIT + 0.2, -0.2, 1.5), (KIT, 1.7, 1.28), 52), who={"me": (X(KIT, 1.7), 0, "scared", {"arms": [30, 0]})},
  note="the folded page going back into my waistcoat pocket")
cue("L44.2", "ppage", mode="pocket")
S("L45", ((KIT, -0.35, 1.52), (KIT, 1.7, 1.5), 38), who={"me": (X(KIT, 1.7), 0, "smirk", {})},
  note="me close to camera, lamp-lit, looking straight at us. Cut to frame 1.")

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
# every character starts hidden unless the first shot placed it
cues = [c for c in cues if c["name"] != "sfx_hint"]
cues.sort(key=lambda c: tkey(c["at"]))

story = {
    "slug": "rule-three",
    "title": "Rule Three Was TORN Out",
    "made_for_kids": False,
    "premise": "I keep my town's red rulebook: every night at nine I stamp one new rule picked from the slips people drop through the hall door, and by morning everyone follows it. Rule three is the only page torn out, and nobody ever asks who tore it. My little brother Milo says that if I skip Mom's birthday again he will stand up at the party and ask.",
    "twist": "I tore out rule three myself on my first night: it said that if I ever miss a night, the book goes to Milo for good. I also stamped the rule that stops anyone asking. Milo asks anyway, I tell him, and rule three's own words never said where I stamp, so we carry the book to Mom's table. At home the back of the torn page holds rule four, and I fold it shut unread.",
    "world": "a bright hill town of painted blocky houses around a sloping high street with a white clock-tower town hall at the top; inside, a mint-panelled record room with a checker floor, a brass wall clock, a pale seamless stone lectern and a door-sized red leather rulebook",
    "voice": {"voice": "am_adam", "tempo": 1.03, "rate": 1.45},
    "key_color": "#5b8cff",
    "gap": GAP,
    "tail": LOOP,
    "fade_in": False,
    "fade_out": False,
    "look": {"style": "closer", "fog": "#cfe6f5", "fog_density": 0.006, "fog_start": 14.0, "sky": "#7cc6ff", "sky_strength": 1.0,
             "exposure": 0.2, "hdri": "kloppenheim_06_puresky", "hdri_strength": 0.45, "hdri_rotation": 40, "flash_safe": True, "polish": {"emph": ["L01", "L05", "L30", "L43"], "reveal": ["L30", "L31"], "quiet": [["L38", "L41"]],
                                                                     "sway": ["S32", "S33", "S34", "S35", "S36", "S37", "S38"]}},
    "grade": {"shadows": [0.0, 0.0, 0.03], "highlights": [0.03, 0.01, -0.02], "saturation": 1.08, "contrast": 1.05,
              "vignette": 0.25, "bloom": 0.22, "grain": 0.008},
    "phonemes": {"Milo": "mˈIlO"},
    "cast": cast,
    "lines": lines,
    "shots": out_shots,
    "acting": acting,
    "cues": cues,
    "fx": [],
    "music": {"root": 40, "mode": "dorian", "bpm": 100, "seed": 6, "sections": [
        {"at": 0, "voices": ["piano", "pulse"], "energy": 0.3},
        {"at": "L03", "voices": ["piano", "pulse"], "energy": 0.42},
        {"at": "L23", "voices": ["drone", "piano"], "energy": 0.5},
        {"at": "L37", "voices": ["drone", "pad", "piano"], "energy": 0.55, "mode": "major", "root": 40},
        {"at": "L42", "voices": ["drone"], "energy": 0.45, "mode": "dorian", "root": 40}]},
    "sound": {
        "floor": "wood", "steps_db": -24, "rev": 1,
        "ambience": [{"kind": "room", "from": 0, "to": "L23", "lufs": -36},
                     {"kind": "traffic", "from": "L03", "to": "L07", "lufs": -40},
                     {"kind": "room", "from": "L23", "to": "end", "lufs": -40}],
        "sfx": [{"at": "L01.3+0.1", "kind": "thud", "db": -3},
                {"at": "L08.2", "kind": "thud", "db": -12},
                {"at": "L28+0.9", "kind": "door", "db": -14},
                {"at": "L39.1+0.85", "kind": "thud", "db": -14},
                {"at": "L42+0.3", "kind": "whoosh", "db": -30, "dur": 0.4},
                {"at": "L43", "kind": "whoosh", "db": -28, "dur": 0.4},
                {"at": "L44", "kind": "whoosh", "db": -26, "dur": 0.3}],
        "music_drops": [{"from": "P01", "to": "P01>"}],
    },
}
OUT.write_text(json.dumps(story, indent=1, ensure_ascii=False))
print(f"wrote {OUT}: {len(out_shots)} shots, {len(cues)} cues")
