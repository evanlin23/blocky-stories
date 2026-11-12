"""Writes ../story.json for ep146 "My Cousin's Phone Is ALWAYS At 1%" (script.md, batch 15). Run:
    python stories/ep146-one-percent/generator/make_story.py

The words are in lines.json (the script's own slash chunks; captions are split to three words here and the
references remapped). Places are in ../layout.py (shared with set.py). A character facing -y has yaw 0, +y is 180.
Daylight, nothing flickers; the phones' and the tag's states change by shot (set.py's tables).
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
REV = 1
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


def person(skin, shirt, pants, shoes, hair="buzz", hair_c="#2a1d15", collar=None, hat="none", hat_c="#333333",
           eyes="round", sleeves="long", pattern="solid", pattern_c=None, extras=(), brow_w=1.0, **kw):
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
    # me, 31: a short ginger buzz cut, light freckled skin, a gray hoodie (hood down), jeans, white sneakers
    "me": person("#f1c9a0", "#8a8f99", "#4a5a8a", "#f2efe6", hair="buzz", hair_c="#c8642a", extras=["hooddown"],
                 extra_c="#7a808a", freckles="#b9703c", brow_w=1.3),
    # Dex, 32: a big black curly top, warm brown skin, a yellow windbreaker over a white tee, rubber boots
    "dex": person("#b9794a", "#f2c230", "#3b4a5e", "#2f6a4a", hair="mop", hair_c="#15100c", collar="#ffffff",
                  curls="#15100c", brow_w=1.3),
    # Grandma, 80: white hair in a bun, a blue knit cardigan, lashes
    "grandma": person("#f0c8a0", "#4a78c8", "#6a5a8a", "#6a4a30", hair="bun", hair_c="#f0f0f2", pattern="knit",
                      pattern_c="#6f98e0", eyes="lashes", height=0.93),
    # Grandpa, 82: a white captain's cap (no badge), a big gray moustache, a red cardigan
    "grandpa": person("#e8b890", "#c0392b", "#4a4a5a", "#3a3028", hair="none", hat="ballcap", hat_c="#f4f1ea",
                      pattern="knit", pattern_c="#d9594b", stache="#b9b9c0", height=0.97),
}
CAST = list(cast)
acting = {n: [] for n in cast}
cues = []
SH = []
last = {}

EXPR = {"neutral": "neutral", "uneasy": "worried", "scared": "scared", "stunned": "wide", "sad": "worried",
        "smile": "smile", "laugh": "laugh", "warm": "warm", "sly": "smirk", "sheepish": "sad-smile",
        "determined": "neutral", "soft": "soft"}


def put(who, at, pos, yaw=0.0, expr="neutral", arms=(0, 0), side=(0, 0), head=(0, 0), lean=0.0, look=(0, 0)):
    pos = [round(pos[0], 3), round(pos[1], 3), round(pos[2] if len(pos) > 2 else 0.0, 3)]
    prev = last.get(who)
    if prev and prev["pos"] != pos:
        acting[who].append({"at": at, "pos": list(prev["pos"])})   # stand where we were, then jump (same time: no steps)
    acting[who].append({"at": at, "pos": pos, "yaw": yaw, "arms": list(arms), "side": list(side), "head": list(head),
                        "lean": lean, "expr": EXPR.get(expr, expr), "look": list(look), "hidden": False, "blink": False,
                        "blend": 0.0})
    last[who] = {"pos": pos, "hidden": False}


def hide(who, at):
    prev = last.get(who)
    if prev is None:
        acting[who].append({"at": 0, "pos": [0.0, -50.0, 0.0], "hidden": True, "blend": 0.0})
        last[who] = {"pos": [0.0, -50.0, 0.0], "hidden": True}
    elif not prev["hidden"]:
        acting[who].append({"at": at, "hidden": True})
        prev["hidden"] = True


def chg(who, at, blend=0.3, **kw):
    k = {"at": at, "blend": blend}
    for a, b in kw.items():
        k[a] = EXPR.get(b, b) if a == "expr" else (list(b) if isinstance(b, tuple) else b)
    acting[who].append(k)


def walk(who, at, pos, yaw=None):
    """Walk to pos (the previous key stays where it was; the walk faces where it goes)."""
    k = {"at": at, "pos": [round(pos[0], 3), round(pos[1], 3), round(pos[2] if len(pos) > 2 else 0.0, 3)]}
    if yaw is not None:
        k["yaw"] = yaw
    acting[who].append(k)
    last[who]["pos"] = k["pos"]


# ---------------------------------------------------------------------------------------------- cameras
def cam(tx, ty, tz, d, lens, az=0.0, el=0.0, push=0.07, arc=2.5, to=None):
    """A camera d metres from the target at azimuth az (0: south of it looking north, 180: north of it) and elevation
    el, pushing in by `push` while it slides `arc` degrees round."""
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


def fcam(pos, d=3.0, lens=30, f=0.38, dx=0.0, dz=0.0, z0=1.57, **kw):
    """Aim so that a head at pos (eyes z0 above its feet) sits f of the way down the frame."""
    h = pos[2] + z0 + dz
    return cam(pos[0] + dx, pos[1], h - (0.5 - f) * hz(d, lens), d, lens, **kw)


def shot(id_, at, camera, who=None, hand=0.04, step=2):
    who = who or {}
    for n in CAST:
        if n in who:
            kw = dict(who[n])
            put(n, at, kw.pop("pos"), **kw)
        else:
            hide(n, at)
    SH.append((at, camera, step, hand, id_))


ME, DEX = G.ME, G.DEX
HOLD = dict(arms=(58, 58), side=(-8, -8))          # a flat palm, chest height, in front
LOWHOLD = dict(arms=(8, 80), side=(4, -4))         # the phone held up beside the head, in a flat palm
DOWN = dict(arms=(8, 8), side=(4, 4))
MEF = 180.0                                        # I face north, toward the boat and the camera


def me(expr="neutral", pos=ME, **kw):
    return {"me": dict(pos=pos, yaw=MEF, expr=expr, **kw)}


def dex(expr="neutral", pos=DEX, **kw):
    return {"dex": dict(pos=pos, yaw=0.0, expr=expr, **kw)}


# ============================================================================================ 01 the rule
shot("S01a", 0, cam(0.2, G.RAIL_Y, 1.8, 2.0, 28, push=0.05, arc=1.5),
     dex("neutral", head=(0, 10), look=(0.3, -0.4), **DOWN))
shot("S01a2", "L01.1", cam(0.45, G.RAIL_Y, 1.84, 1.15, 28, push=0.08, arc=2), dex("neutral", head=(0, 10), **DOWN))
shot("S01b", "L01.2", cam(ME[0], ME[1], 1.28, 2.6, 28, az=MEF, push=0.04, arc=1.5), me("neutral", **LOWHOLD))
shot("S01c", "L01.3", fcam(DEX, d=2.8, lens=30, f=0.38, push=0.05), dex("neutral", head=(0, 6), **DOWN))

# ============================================================================================ 02 the cost
shot("S02", "L02", cam(DEX[0], DEX[1], 1.78, 2.1, 28, push=0.06, arc=2), dex("neutral", **HOLD))

# ============================================================================================ 03 stakes
shot("S03a", "L03", fcam(DEX, d=3.0, lens=30, f=0.38, push=0.05), dex("neutral", head=(0, 4), **DOWN))
shot("S03b", "L03.2", fcam(DEX, d=2.1, lens=30, f=0.36, push=0.08), dex("neutral", **HOLD))

# ============================================================================================ 04 the example
GM = G.GRANDMA
shot("S04a", "L04", cam(G.ROOM[0], GM[1], 1.2, 3.8, 28, push=0.04, arc=1.5), {
    "grandma": dict(pos=(GM[0], GM[1], 0.0), yaw=0.0, expr="sly", arms=(30, 30), side=(-6, -6))})
shot("S04b", "L04.2", cam(GM[0] - 0.15, GM[1], 1.3, 2.5, 28, push=0.08, arc=2), {
    "grandma": dict(pos=(GM[0], GM[1], 0.0), yaw=0.0, expr="sly", arms=(30, 30), side=(-6, -6))})

# ============================================================================================ 05 the duck
shot("S05", "L05", fcam(ME, d=2.6, lens=30, f=0.36, az=MEF, push=0.05), me("smile", **LOWHOLD))
shot("S06", "L06", cam(DEX[0], DEX[1] - 0.2, 1.75, 1.7, 30, push=0.06, arc=2), dex("neutral", head=(0, 8), **HOLD))
shot("S07a", "L07", fcam(DEX, d=2.5, lens=30, f=0.36, push=0.05), dex("sad", head=(0, 10), **HOLD))
shot("S07b", "L07.2", fcam(DEX, d=2.0, lens=30, f=0.38, push=0.08), dex("sad", arms=(80, 80), side=(28, 28)))

# ============================================================================================ 06 the walk
shot("S08a", "L08", cam(ME[0], -0.1, 1.4, 3.4, 28, az=MEF, push=0.02, arc=1.0, to=[0, 0.2, 1.4]),
     {"me": dict(pos=(0.0, -1.5, 0.0), yaw=MEF, expr="determined", arms=(10, 10))})
walk("me", "L08.2", (0.0, ME[1], 0.0))
shot("S08b", "L08.2", fcam(ME, d=2.3, lens=30, f=0.38, az=MEF, push=0.06), me("determined", **DOWN))
shot("S09", "L09", cam(0.3, 1.3, 0.5, 2.8, 28, az=22, el=5, push=0.05, arc=2), me("uneasy", **DOWN))
G_FL = [G.FLASH_ME, G.FLASH_DEX, G.FLASH_GPA]
shot("S10", "L10", cam(0.0, 5.7, 1.55, 6.2, 28, push=0.04, arc=2), {
    "me": dict(pos=G.FLASH_ME, yaw=0.0, expr="sly", arms=(30, 30), side=(-60, -8), head=(-18, 0)),
    "dex": dict(pos=G.FLASH_DEX, yaw=0.0, expr="sly", arms=(30, 30), side=(-8, -60), head=(18, 0)),
    "grandpa": dict(pos=G.FLASH_GPA, yaw=0.0, expr="soft", arms=(8, 8), side=(4, 4))})
shot("S11", "L11", fcam(ME, d=2.6, lens=30, f=0.36, az=MEF, push=0.05), me("sheepish", **LOWHOLD))
shot("S12", "L12", fcam(ME, d=2.4, lens=30, f=0.38, az=MEF, push=0.06), me("uneasy", **DOWN))
chg("me", "L12.2", blend=0.4, expr="soft")
shot("S13a", "L13", fcam(ME, d=2.4, lens=30, f=0.36, az=MEF, push=0.05), me("neutral", **LOWHOLD))
shot("S13b", "L13.1", fcam(ME, d=2.2, lens=30, f=0.38, az=MEF, push=0.06), me("determined", **HOLD))
# the drop: nobody speaks; the water between us and the boat beyond
shot("S13c", "P01", cam(0.0, 2.2, 1.7, 7.0, 30, push=0.03, arc=1.0), {**me("determined", **HOLD), **dex("neutral", **DOWN)})

# ============================================================================================ 07 the call
shot("S14a", "L14", cam(DEX[0], DEX[1] - 0.2, 1.75, 1.7, 30, push=0.06, arc=2), dex("neutral", head=(0, 8), **HOLD))
shot("S14b", "L14.0+0.8", fcam(DEX, d=2.2, lens=30, f=0.38, push=0.06), dex("stunned", **HOLD))
shot("S15", "L15.2", cam(DEX[0], DEX[1] - 0.3, 1.8, 1.9, 30, push=0.05, arc=2), dex("stunned", head=(0, 8), **HOLD))
shot("S16", "L16", cam(ME[0], ME[1] - 0.05, 1.45, 2.0, 30, az=MEF, push=0.05, arc=2), me("stunned", **HOLD))

# ============================================================================================ 08 the reveal
shot("S17", "L17", cam(ME[0], ME[1] + 0.2, 1.3, 1.5, 30, az=MEF, push=0.03, arc=1.0), me("stunned", **HOLD))
shot("S18", "L18", cam(ME[0], ME[1] + 0.2, 1.4, 2.3, 30, az=MEF, push=0.06, arc=1.0), me("stunned", arms=(62, 62), side=(-6, -6)))
shot("S19a", "L19", fcam(ME, d=2.4, lens=30, f=0.38, az=MEF, push=0.06), me("sheepish", **DOWN))
shot("S19b", "L19.2", fcam(DEX, d=2.6, lens=30, f=0.38, push=0.06), dex("stunned", **DOWN))
chg("dex", "L19.3", blend=0.5, expr="warm")
shot("S20", "L20", fcam(DEX, d=2.5, lens=30, f=0.3, push=0.06), dex("laugh", **HOLD))
shot("S21", "L21", fcam(ME, d=2.6, lens=30, f=0.36, az=MEF, push=0.08, arc=1.5), me("warm", **LOWHOLD))

# ---------------------------------------------------------------------------------------------- finish
shots = []
for i, (at, camera, step, hand, nm) in enumerate(SH):
    s = {"id": nm, "cam": camera, "step": step, "hand": hand}
    if i:
        s["at"] = remap(at)
    shots.append(s)

lines_out = []
for ln in lines:
    if ln["id"] == "L14":
        lines_out.append({"id": "P01", "pause": 0.5, "chunks": [["", ""]]})
    lines_out.append(ln)

for items in (acting.values(), [cues]):
    for lst in items:
        remap_all(lst)

sfx = [
    {"at": "L06", "kind": "ding", "db": -13, "dur": 0.32, "pitch": 330, "fall": 0.4, "lp": 2800},     # the duck
    {"at": "L14", "kind": "ding", "db": -13, "dur": 0.32, "pitch": 330, "fall": 0.4, "lp": 2800},
    {"at": "L15.3", "kind": "ding", "db": -17, "dur": 0.45, "pitch": 520, "fall": 0.5, "lp": 2400},   # a phone runs out
    {"at": "L16.1", "kind": "ding", "db": -17, "dur": 0.45, "pitch": 440, "fall": 0.5, "lp": 2400},
]
for s_ in sfx:
    s_["at"] = remap(s_["at"])
music = {
    "root": 47, "mode": "minor", "bpm": 100, "seed": 146,
    "sections": [
        {"at": 0, "voices": ["pluck", "pad"], "energy": 0.35, "mode": "minor", "root": 47},
        {"at": "L08", "voices": ["piano", "pad"], "energy": 0.25, "mode": "minor", "root": 47},
        {"at": "L14", "voices": ["drone", "pad"], "energy": 0.2, "mode": "minor", "root": 47},
        {"at": "L17", "voices": ["pad"], "energy": 0.1, "mode": "minor", "root": 47},
        {"at": "L20", "voices": ["pluck", "pad", "piano"], "energy": 0.5, "mode": "major", "root": 47},
    ],
}
for sec in music["sections"]:
    sec["at"] = remap(sec["at"])
sound = {"floor": "wood", "steps_db": -24, "ambience": [], "sfx": sfx,
         "music_drops": [{"from": "P01", "to": "P01>"}], "rev": REV}
polish = {"emph": [remap(r) for r in ("L01.1", "L03.2", "L11.1", "L13.1", "L15.3", "L18.1", "L19.1")],
          "reveal": ["L19"], "twist": "L19", "quiet": [["L20", "L21"]], "whoosh_cuts": False,
          "hold": ["S09", "S18"], "set_moves": []}
polish.pop("set_moves")
story = {
    "slug": "ep146-one-percent",
    "title": "My Cousin's Phone Is ALWAYS At 1% \U0001F50B",
    "made_for_kids": False,
    "premise": ("In our town your phone can't run out while you're waiting for someone to call, but it never charges "
                "past one percent. My cousin Dex's phone has said 1% for three years, waiting on a call from someone "
                "he won't name."),
    "twist": ("The someone is me, and my own phone has said 1% for the same three years because I have been waiting on "
              "him. When I finally call, the waiting is over, and both phones run out mid-hello."),
    "world": ("A sunny marina on a blue afternoon: a white jetty, small boats, green hills across the water, and "
              "Grandpa's teal-and-white houseboat with a covered deck, plus Grandma's yellow living room."),
    "voice": {"voice": "am_adam", "tempo": 1.03, "rate": 1.45},
    "key_color": "#ff5a4f",
    "gap": 0.15,
    "tail": 0,
    "fade_in": False,
    "fade_out": False,
    "rev": REV,
    "look": {"style": "closer", "fog": "#dff0ff", "fog_density": 0.002, "fog_start": 60.0, "sky": "#8fd0ff",
             "sky_strength": 1.0, "exposure": 0.2, "flash_safe": True, "polish": polish},
    "grade": {"shadows": [0.0, 0.0, 0.03], "highlights": [0.03, 0.012, -0.02], "saturation": 1.06, "contrast": 1.04,
              "vignette": 0.15, "bloom": 0.08, "grain": 0.006},
    "phonemes": {"Dex": "dˈɛks"},
    "hud": {"object": "tag", "at": [-0.37, 0.6], "size": 0.56},
    "cast": cast,
    "lines": lines_out,
    "shots": shots,
    "acting": acting,
    "cues": cues,
    "fx": [],
    "music": music,
    "sound": sound,
    "framing_ok": ["S09"],   # sneakers close-up at the plank: the line is about my feet, my head is cut on purpose
    "staging_ok": [],
    "asr_forgive": ["hel", "percent", "percent it's"],
}
OUT.write_text(json.dumps(story, indent=1, ensure_ascii=False) + "\n")
print("wrote", OUT, f"({len(shots)} shots)")
