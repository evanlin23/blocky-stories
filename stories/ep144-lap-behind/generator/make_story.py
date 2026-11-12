"""Writes ../story.json for ep144 "The Pool Sign Says NOBODY Swims Alone" (script.md, batch 15). Run:
    python stories/ep144-lap-behind/generator/make_story.py

Words are in lines.json (the script's own slash chunks; captions are split to three words here and references
remapped). Places are in ../layout.py (shared with set.py). A character facing -y has yaw 0, +y is 180.
One pool, one sunrise, no cuts of place; the follower is foam driven by cues (see set.py). Swimmers are leaning
characters in a water slab: only head, shoulders and arms show.
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
REV = 2
D2R = math.pi / 180

orig_lines = json.loads((HERE / "lines.json").read_text())
lines, CHUNKMAP = timeline.split_lines(orig_lines)


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


def person(skin, shirt, pants, shoes, hair="none", hair_c="#2a1d15", pattern="solid", pattern_c=None, hat="none",
           hat_c="#333333", extras=(), sleeves="short", eyes="round", brow_w=1.0, **kw):
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


SKIN = "#e0a878"
LSKIN = "#e8bf98"
cast = {
    # me, 22: a red swim cap with blue goggles pushed up on it, a navy swim top, blue trunks
    "me": person(SKIN, "#1f2f5c", "#2a3a7a", SKIN, hat="beanie", hat_c="#e8433a", goggles="#2f5bea", brow_w=1.3),
    # Grandpa Lou, about 75: a white cap, a big white block moustache, a striped swim top; in the water
    "lou": person(LSKIN, "#2f5bea", "#1f2f5c", LSKIN, hat="beanie", hat_c="#f4f4f0", pattern="stripes", pattern_c="#ffffff",
                  moustache="#f2f2ee", goggles="#2f5bea", brow_w=1.2),
    # Grandpa on the deck in a towel round his shoulders
    "lout": person(LSKIN, "#2f5bea", "#1f2f5c", LSKIN, hat="beanie", hat_c="#f4f4f0", pattern="stripes", pattern_c="#ffffff",
                   moustache="#f2f2ee", brow_w=1.2, extras=["scarf"], extra_c="#2aa6a0"),
    # the lifeguard, about 30: a red visor, a white tee, a whistle
    "guard": person("#c58a5c", "#f7f7f2", "#e8433a", "#c58a5c", hat="ballcap", hat_c="#e8433a", hair="buzz", hair_c="#2a1d15"),
}
CAST = list(cast)
acting = {n: [] for n in cast}
cues = []
SH = []
last = {}

EXPR = {"neutral": "neutral", "uneasy": "worried", "scared": "scared", "stunned": "wide", "worried": "worried",
        "laugh": "laugh", "smile": "smile"}
DK = G.DECK


def put(who, at, x, y, z=0.0, yaw=0.0, expr="neutral", arms=(0, 0), side=(0, 0), head=(0, 0), lean=0.0,
        look=(0, 0), blend=0.0):
    pos = [round(x, 3), round(y, 3), round(z, 3)]
    prev = last.get(who)
    if prev and prev["pos"] != pos:
        acting[who].append({"at": at, "pos": list(prev["pos"])})
    acting[who].append({"at": at, "pos": pos, "yaw": yaw, "arms": list(arms), "side": list(side), "head": list(head),
                        "lean": lean, "expr": EXPR.get(expr, expr), "look": list(look), "hidden": False, "blink": False,
                        "blend": blend})
    last[who] = {"pos": pos, "hidden": False}


def hide(who, at):
    prev = last.get(who)
    if prev is None:
        acting[who].append({"at": 0, "pos": [0.0, -50.0, 0.0], "hidden": True, "blend": 0.0})
        last[who] = {"pos": [0.0, -50.0, 0.0], "hidden": True}
    elif not prev["hidden"]:
        acting[who].append({"at": at, "hidden": True})
        prev["hidden"] = True


def chg(who, at, blend=0.25, **kw):
    k = {"at": at, "blend": blend}
    for a, b in kw.items():
        k[a] = EXPR.get(b, b) if a == "expr" else (list(b) if isinstance(b, tuple) else b)
    acting[who].append(k)


def move(who, at, x, y, z=None, blend=0.3, **kw):
    """A swim or a climb: the character goes to (x, y) by `at`, eased; the key keeps its pose."""
    prev = last[who]
    z = prev["pos"][2] if z is None else z
    pos = [round(x, 3), round(y, 3), round(z, 3)]
    k = {"at": at, "pos": pos, "blend": blend}
    for a, b in kw.items():
        k[a] = list(b) if isinstance(b, tuple) else b
    acting[who].append(k)
    prev["pos"] = pos


def stroke(who, base, n, dt=0.6, first=0.0):
    """Alternate arm strokes (freestyle): one arm over the head, the other back."""
    for i in range(n):
        a = (165, -15) if i % 2 == 0 else (-15, 165)
        chg(who, f"{base}+{round(first + i * dt, 2)}", blend=0.5, arms=a)


def talk(who, a, b, m=0.4):
    acting[who].append({"from": a, "to": b, "mouth": [m, m], "flap": True})


def cue(at, name, **kw):
    cues.append({"at": at, "name": name, **kw})


# ---------------------------------------------------------------------------------------------- cameras
def cam(tx, ty, tz, d, lens, az=0.0, el=0.0, push=0.07, arc=2.5, to=None):
    """A camera d metres from the target at azimuth az (0 = south of it looking north, 180 = north of it looking
    south) and elevation el, pushing in by `push` while it slides `arc` degrees round."""
    def at(dd, a):
        a, e = a * D2R, el * D2R
        return [round(tx + dd * math.sin(a) * math.cos(e), 3), round(ty - dd * math.cos(a) * math.cos(e), 3),
                round(tz + dd * math.sin(e), 3)]
    tgt = [tx, ty, tz]
    t1 = list(to) if to else tgt
    push, arc = push * 2.0, arc * 3.0
    return [[0, at(d, az), tgt, lens], [1, at(d * (1 - push), az + arc), t1, lens]]


def hz(d, lens):
    return 24.0 * d / lens


def fcam(x, y, z=0.0, d=3.0, lens=30, f=0.38, dx=0.0, dz=0.0, **kw):
    """Aim so that a head at (x, y, 1.57 + z) sits f of the way down the frame."""
    h = 1.57 + z
    return cam(x + dx, y, h - (0.5 - f) * hz(d, lens) + dz, d, lens, **kw)


def ocam(x, y, z, d, lens, **kw):
    return cam(x, y, z, d, lens, **kw)


def shot(id_, at, camera, who=None, hand=0.04, step=2):
    who = who or {}
    for n in CAST:
        if n in who and who[n] is None:
            continue     # carries on from the shot before (a swim that runs across a cut)
        if n in who:
            put(n, at, **who[n])
        else:
            hide(n, at)
    SH.append((at, camera, step, hand, id_))


def ps(x, y, **kw):
    return dict(x=x, y=y, **kw)


L4, L2 = G.L4, G.L2
# the far wall seen from the deck, left of the ladder (its rails would stand in the frame from lane four's centre)
FARCAM = [[0, [-1.3, -1.5, 0.96], [-0.9, 12.6, -0.7], 55], [1, [-1.3, -1.2, 0.96], [-0.9, 12.6, -0.7], 55]]
BS = dict(z=-0.95, lean=26, head=(0, 0), arms=(75, 75), side=(25, 25), expr="neutral")   # breaststroke: head up, face to us
SW = dict(z=G.SWIM_Z, lean=66, head=(0, -22), arms=(165, -15), expr="neutral")      # a freestyle swimmer
WALL = dict(z=G.STAND_Z)                                                            # chest deep at the wall
BLOCK_TOP = G.DECK + G.BLOCK_H + 0.03
SX, SY = G.SIGN
ME_SIGN = (-1.15, -2.0)

# ============================================================================================ 01 the rule
shot("S01a", 0, fcam(*ME_SIGN, z=DK, d=4.5, lens=30, f=0.44, dx=0.5, az=180, push=0.03, arc=1.0), {
    "me": ps(*ME_SIGN, z=DK, yaw=180, expr="neutral", head=(-8, 0))})
shot("S01b", "L01.3", ocam(SX, SY, 1.78, 2.1, 24, az=178, push=0.05, arc=1.0), {})

# ============================================================================================ 02 the rule at work
LOU_S = (L2, 9.0)
shot("S03", "L03", ocam(L2 + 0.15, 6.6, 0.55, 5.0, 30, az=0, el=6, push=0.03, arc=1.5), {
    "lou": ps(*LOU_S, **BS, yaw=0)})
move("lou", "L03>", L2, 5.6, blend=0.3)
for i in range(4):
    chg("lou", f"L03+{0.3 + i * 0.7:.2f}", blend=0.35, arms=(75, 75) if i % 2 == 0 else (110, 110))
cue("L03", "f3", x=0.9, y=-0.4, v=1.0, w=1.0, s=1.3)
shot("S04", "L04", fcam(L2, 0.7, z=G.STAND_Z, d=3.8, lens=30, f=0.46, dx=0.45, az=180, push=0.04), {
    "lou": ps(L2, 0.7, **WALL, yaw=180, expr="laugh", arms=(0, 0), head=(0, 0))})
chg("lou", "L04.1", blend=0.3, arms=(150, 0))
chg("lou", "L04.1+0.5", blend=0.3, arms=(100, 0))
chg("lou", "L04.1+1.0", blend=0.3, arms=(150, 0))
cue("L04", "f3", x=0.85, y=0.7, v=1.0, w=1.0, s=1.0)
cue("L04>", "f3", v=0.0, dur=0.4)
shot("S06", "L06", fcam(L4, G.BLOCK[1], z=BLOCK_TOP, d=3.6, lens=30, f=0.46, az=48, el=8, push=0.05, arc=1.0), {
    "me": ps(L4, G.BLOCK[1], z=BLOCK_TOP, yaw=55, expr="neutral", arms=(8, 8), head=(0, 0))})

# ============================================================================================ 03 the splash
shot("S08a", "L08", ocam(L4, 4.8, 0.5, 4.0, 30, az=0, el=5, push=0.04, arc=1.5), {
    "me": ps(L4, 6.6, **BS, yaw=0)})
move("me", "L08.2", L4, 4.4, blend=0.5)
for i in range(2):
    chg("me", f"L08+{0.3 + i * 0.6:.2f}", blend=0.35, arms=(75, 75) if i % 2 == 0 else (110, 110))
shot("S08b", "L08.2", FARCAM, {})
cue("L08.2", "f0", mode="pin", x=L4 + 0.1, y=13.2, v=1.0, s=1.35)
shot("S09", "L09", ocam(G.BOARD[0], G.BOARD[1], 1.7, 3.5, 24, az=180, el=2, push=0.05, arc=1.5), {})
cue("L09", "bn", a=1, b=0)
cue("L09", "b2", v2=1.0, dur=0.4)
shot("S10", "L10", ocam(G.BOARD[0] + 0.2, G.BOARD[1], 1.6, 4.4, 24, az=192, el=3, push=0.04, arc=1.5), {})

# ============================================================================================ 04 it follows
shot("S11a", "L11", fcam(L4, 0.7, z=G.STAND_Z, d=3.0, lens=30, f=0.36, az=180, push=0.05), {
    "me": ps(L4, 0.7, **WALL, yaw=180, expr="uneasy", head=(28, 0))})
shot("S11b", "L11.2", FARCAM, {})
cue("L11.2", "f0", v=0.0, dur=0.35)
cue("L11.2", "rg", u=1.0, dur=1.2)
shot("S12", "L12", ocam(L4, 6.8, 0.0, 7.4, 28, az=0, el=52, push=0.03, arc=1.0), {
    "me": ps(L4, 6.0, **SW, yaw=180)})
move("me", "L12>", L4, 9.4, blend=0.4)
stroke("me", "L12", 3, dt=0.6)
cue("L12", "f0", mode="chase", D=2.6, v=1.0, s=0.9, dur=0.3)
cue("L12", "bn", a=2, b=1)
shot("S13", "L13", [[0, [2.6, -6.0, 3.3], [-0.9, 6.5, 0.2], 28], [1, [2.5, -5.6, 3.2], [-0.9, 6.5, 0.2], 28]], {
    "me": ps(L4, 1.4, **SW, yaw=180),
    "guard": ps(G.CHAIR[0], G.CHAIR[1], z=1.55 - 0.68, yaw=180, expr="neutral", arms=(10, 10))})
move("me", "L13>", L4, 3.0, blend=0.4)
stroke("me", "L13", 2, dt=0.6)
cue("L13", "f0", mode="chase", D=13.0, v=1.0, s=1.0)
cue("L13.1", "bn", a=4, b=3)
shot("S14", "L14", ocam(G.BOARD[0], G.BOARD[1], 1.7, 3.5, 24, az=176, el=2, push=0.05, arc=1.5), {})
cue("L14", "bn", a=6, b=5)
cue("L14.1", "bn", a=8, b=7)

# ============================================================================================ 05 the double kick
KICK = (L4, 0.95)
shot("S15", "L15", fcam(L4, 0.8, z=G.STAND_Z, d=3.4, lens=30, f=0.46, az=180, el=4, push=0.05, arc=1.0), {
    "me": ps(L4, 0.8, **WALL, yaw=180, expr="neutral", head=(0, 0), lean=0)})
chg("me", "L15.2", blend=0.4, lean=14, arms=(40, 40))
chg("me", "L15.2+0.9", blend=0.4, lean=0, arms=(0, 0))
cue("L15.2", "f1", x=L4 + 0.8, y=0.9, v=1.0, s=1.0, dur=0.12)
cue("L15.2+0.6", "f1", v=0.0, dur=0.3)
cue("L15.2+0.3", "f2", x=L4 - 0.8, y=1.0, v=1.0, s=1.0, dur=0.12)
cue("L15.2+0.9", "f2", v=0.0, dur=0.3)
shot("S16", "L16", ocam(L4, 0.9, 0.45, 3.0, 30, az=180, el=14, push=0.04, arc=1.0), {
    "me": ps(L4, 0.8, **WALL, yaw=180, expr="neutral", head=(0, 0), lean=0)})
cue("L16", "f1", x=L4 + 0.75, y=0.95, v=1.0, s=1.3, dur=0.12)
cue("L16+0.55", "f1", v=0.0, dur=0.3)
cue("L16+0.25", "f2", x=L4 - 0.75, y=1.0, v=1.0, s=1.3, dur=0.12)
cue("L16+0.75", "f2", v=0.0, dur=0.3)
shot("S17", "L17", fcam(L2, -1.4, z=DK, d=3.6, lens=30, f=0.46, dx=0.35, az=180, push=0.05), {
    "lout": ps(L2, -1.4, z=DK, yaw=190, expr="laugh", arms=(35, 0), side=(78, 0), head=(-14, 0))})
shot("S18", "L18", ocam(G.BOARD[0], G.BOARD[1], 1.7, 3.6, 24, az=184, el=2, push=0.05, arc=1.5), {})
cue("L18.1", "bn", a=12, b=11)
shot("S19", "L19", fcam(L4, 0.8, z=G.STAND_Z, d=3.4, lens=30, f=0.46, az=190, el=4, push=0.05, arc=1.0), {
    "me": ps(L4, 0.8, **WALL, yaw=180, expr="neutral", head=(0, 0), lean=0)})
chg("me", "L19.1", blend=0.4, lean=14, arms=(40, 40))
chg("me", "L19.1+0.9", blend=0.4, lean=0, arms=(0, 0))
cue("L19.1", "f1", x=L4 + 0.8, y=0.9, v=1.0, s=1.0, dur=0.12)
cue("L19.1+0.6", "f1", v=0.0, dur=0.3)
cue("L19.1+0.3", "f2", x=L4 - 0.8, y=1.0, v=1.0, s=1.0, dur=0.12)
cue("L19.1+0.9", "f2", v=0.0, dur=0.3)
shot("S20a", "L20.1", FARCAM, {})
cue("L20.2", "f1", x=L4 + 0.45, y=13.0, v=1.0, s=2.6, dur=0.12)
cue("L20.2+0.6", "f1", v=0.0, dur=0.3)
cue("L20.2+0.3", "f2", x=L4 - 0.9, y=13.2, v=1.0, s=1.8, dur=0.12)
cue("L20.2+0.9", "f2", v=0.0, dur=0.3)
shot("S20b", "L20.2+0.55", fcam(L4, 0.7, z=G.STAND_Z, d=2.9, lens=30, f=0.36, az=180, push=0.07), {
    "me": ps(L4, 0.7, **WALL, yaw=180, expr="scared", head=(14, 0))})
cue("L20.2+0.9", "f0", v=0.0, dur=0.3)
shot("SDROP", "P01", ocam(L4, 5.0, 0.7, 7.0, 30, az=0, el=7, push=0.0, arc=0.0), {})

# ============================================================================================ 06 yesterday
shot("S21", "L22", ocam(-0.3, -0.1, 1.0, 3.4, 30, az=28, el=2, push=0.04, arc=1.0), {
    "me": ps(-0.3, 0.55, z=G.STAND_Z, yaw=0, expr="uneasy", head=(0, 4))})
move("me", "L22+0.45", -0.3, 0.1, z=0.2, blend=0.45)
move("me", "L22+1.1", -0.3, -0.7, z=DK, blend=0.5)
shot("S22", "L22.2", fcam(-0.4, -1.3, z=DK, d=2.7, lens=30, f=0.38, az=180, push=0.06), {
    "me": ps(-0.4, -1.3, z=DK, yaw=180, expr="worried", head=(32, 0))})
cue("L23", "tw", v=1.0)
shot("S23a", "L23", ocam(G.BLOCK[0], G.BLOCK[1], 0.78, 2.1, 30, az=180, el=8, push=0.05, arc=2.0), {})
shot("S23b", "L23.2", ocam(G.BLOCK[0] + 0.1, G.BLOCK[1] + 0.2, 0.62, 1.05, 30, az=180, el=4, push=0.08, arc=1.0), {})

# ============================================================================================ 07 the reveal
ME25 = (-3.3, -0.7)
shot("S25a", "L25", ocam(-3.0, -0.6, 1.5, 3.5, 30, az=180, el=4, push=0.05, arc=1.0), {
    "me": ps(*ME25, z=DK, yaw=135, expr="stunned", head=(-12, 0))})
shot("S25b", "L25.2", ocam(G.BOARD[0], G.BOARD[1], 1.2, 6.8, 24, az=180, el=-3, push=0.0, arc=0.0), {})
shot("S26a", "L26", ocam(G.BLOCK[0], -1.4, 1.55, 3.0, 30, az=180, el=-6, push=0.06, arc=1.0), {
    "me": ps(G.BLOCK[0], -1.6, z=DK, yaw=180, expr="stunned")})
shot("S26b", "L26.2", fcam(L2, 0.7, z=G.STAND_Z, d=3.8, lens=30, f=0.46, dx=0.45, az=180, push=0.04), {
    "lou": ps(L2, 0.7, **WALL, yaw=180, expr="laugh", arms=(0, 0))})
cue("L26.2", "f3", x=0.8, y=0.7, v=1.0, w=1.0, s=1.5, dur=0.3)
shot("S29", "L30", ocam(G.BOARD[0], G.BOARD[1], 1.7, 3.5, 24, az=180, el=2, push=0.08, arc=1.0), {})
shot("S30a", "L31", fcam(*ME_SIGN, z=DK, d=4.5, lens=30, f=0.44, dx=0.5, az=180, push=0.03, arc=1.0), {
    "me": ps(*ME_SIGN, z=DK, yaw=180, expr="uneasy", head=(-8, 0))})
shot("S30b", "L31.1", ocam(SX, SY, 1.78, 2.1, 24, az=178, push=0.05, arc=1.0), {})

# ---------------------------------------------------------------------------------------------- finish
shots = []
for i, (at, camera, step, hand, nm) in enumerate(SH):
    s = {"id": nm, "cam": camera, "step": step, "hand": hand}
    if i:
        s["at"] = remap(at)
    shots.append(s)

lines_out = []
for ln in lines:
    if ln["id"] == "L22":
        lines_out.append({"id": "P01", "pause": 0.6, "chunks": [["", ""]]})
    lines_out.append(ln)

for items in (acting.values(), [cues]):
    for lst in items:
        remap_all(lst)

music = {
    "root": 52, "mode": "minor", "bpm": 96, "seed": 144,
    "sections": [
        {"at": 0, "voices": ["pluck", "pad"], "energy": 0.3},
        {"at": "L09", "voices": ["pluck", "pad", "drone"], "energy": 0.35},
        {"at": "L22", "voices": ["pad", "drone", "piano"], "energy": 0.3},
        {"at": "L30", "voices": ["pad", "drone", "pluck"], "energy": 0.35},
    ],
}
for sec in music["sections"]:
    sec["at"] = remap(sec["at"])
sfx = [
    {"at": "L09", "kind": "click", "db": -16},                  # the board's wood tick as the second row lights
    {"at": "L10.2", "kind": "sting", "db": -14, "dur": 0.8},     # ZERO
    {"at": "L23", "kind": "thud", "db": -18, "dur": 0.4},        # the soaked towel
    {"at": "L26.1", "kind": "hit", "db": -10},                   # the reveal
]
sound = {
    "floor": "concrete", "steps_db": -26,
    "ambience": [{"kind": "water", "from": 0, "to": "end", "lufs": -34}],
    "sfx": sfx,
    "music_drops": [{"from": "P01", "to": "P01>"}],
    "rev": REV,
}
HOLDS = ["S01b", "S09", "S10", "S14", "S18", "S25b", "S29", "S30b"]
polish = {"emph": [remap(r) for r in ("L01.3", "L08.2", "L10.2", "L11.2", "L15.2", "L20.1", "L26.1")],
          "reveal": ["L26"], "twist": "L25", "hold": HOLDS, "bed_kind": "water", "bed_drop_db": -6.0,
          "whoosh_cuts": False, "punch_rate": 0.8,
          "sway": ["S12", "S13", "S21"]}
story = {
    "slug": "ep144-lap-behind",
    "title": "The Pool Sign Says NOBODY Swims Alone \U0001F3CA",
    "made_for_kids": False,
    "premise": ("At our town pool you can't swim alone, because someone always swims with you. When I swim lane four at six "
                "A.M. something splashes one lap behind me, stops when I stop, and copies my odd double kick."),
    "twist": ("The pool sends back whoever swam your lane last. The splash one lap behind me is me from yesterday, and "
              "Grandpa's lane buddy is Grandpa."),
    "world": ("A bright outdoor town pool at sunrise: turquoise water, white lane ropes with red and blue floats, a cream "
              "changing house with a tiled roof, palm-like shade trees, a lap board on the deck."),
    "voice": {"voice": "am_adam", "tempo": 1.03, "rate": 1.45},
    "key_color": "#19c3e6",
    "gap": 0.15,
    "tail": 0,
    "fade_in": False,
    "fade_out": False,
    "rev": REV,
    "look": {"style": "closer", "fog": "#ffd8a8", "fog_density": 0.004, "fog_start": 24.0, "sky": "#ffb06f",
             "sky_strength": 1.0, "exposure": 0.0, "flash_safe": True, "polish": polish},
    "grade": {"shadows": [0.0, 0.0, 0.04], "highlights": [0.03, 0.012, -0.02], "saturation": 1.22, "contrast": 1.1,
              "vignette": 0.15, "bloom": 0.06, "grain": 0.006},
    "hud": {"object": "tag", "at": [0.5, 0.74], "size": 0.42},
    "cast": cast,
    "lines": lines_out,
    "shots": shots,
    "acting": acting,
    "cues": cues,
    "fx": [],
    "music": music,
    "sound": sound,
    "set_moves": ["S23a", "S23b"],
}
story["framing_ok"] = ["S11b", "S20a"]   # deliberate: the far wall, flat water where the splash was / is about to be
story["staging_ok"] = []
story["asr_forgive"] = ["it", "kicked"]   # Whisper hears "at seven" and "I kick"
story["clip_ok"] = ["water"]   # a swimmer's head dips under the opaque water slab on purpose
OUT.write_text(json.dumps(story, indent=1, ensure_ascii=False) + "\n")
print("wrote", OUT, f"({len(shots)} shots, {len(cues)} cues)")
