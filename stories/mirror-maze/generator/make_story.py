"""Writes ../story.json for ep15 "Your Reflection STAYS When You Walk Away" (redo, script.md and brief.md, 2026-11-02).

Run from anywhere: python stories/mirror-maze/generator/make_story.py
The words are in lines.json next to this file. Everything else is here: the cast and the strangers, the shots and
their cameras, the acting (me, Tasha, the maze guy), the cues set.py reads, the shot looks, the score and the sound.

The idea: I am the reflection a person left in a maze pane when they moved away, and Tasha visits me. So in every shot
of me I stand behind a pane; Tasha is on the near, rainy side. Every leftover (the strangers in the glass, me, and
later Tasha's reflection) carries a thin lilac rim, set.py's marker.

Places (metres, the field is z = 0): the maze's front faces -y at y = 12 with its arch at x = 3, a gallery behind it
(x 0.5 to 5.5, y 12.1 to 17.6); the duckboards run from it down to the fry van at (1, -16); the truck is at
(-4.2, 7.2). The maze's inside is built at x = 60: a glass grid, the stage pane at y = 12.8 (Tasha on its -y side, me
on its +y side), the back pane behind me, the maze's bulbs at y = 17.
Acting yaw: 0 faces -y, 90 faces +x, 180 faces +y, -90 faces -x.
"""
import json
import math
import re
from pathlib import Path

from blocky import timeline

HERE = Path(__file__).resolve().parent
OUT = HERE.parent / "story.json"
lines = json.loads((HERE / "lines.json").read_text())
# word-check pins: "But Tasha" runs together at this speed ("Batasha"), so a comma holds them apart in the voice only
for ln in lines:
    if ln["id"] == "L21":
        ln["chunks"][0][1] = "The people,"
    if ln["id"] in ("L09", "L13"):
        ln["chunks"][0][1] = ln["chunks"][0][1].replace("But Tasha", "But... Tasha")
LOOP = 0.25
GAP = 0.12

# ---------------------------------------------------------------------------------------------------- cast
cast = {
    "me": {"age": "adult", "skin": "#d9a27a", "shirt": "#b8697a", "pattern": "solid", "collar": "#8f4a5c",
           "pants": "#151518", "shoes": "#0c0c0e", "sleeves": "long", "hair": "cap", "hair_c": "#3a2a20",
           "hat": "bucket", "hat_c": "#6f9a2e", "face": {"eyes": "round", "brows": True, "ink": "#24131f"}},
    "tasha": {"age": "adult", "skin": "#b07850", "shirt": "#f0c419", "pattern": "solid", "collar": "#d8aa12",
              "pants": "#151518", "shoes": "#0c0c0e", "sleeves": "long", "hair": "swoop", "hair_c": "#5a2a48",
              "fringe": "hard", "hat": "none", "extras": ["coat", "hooddown"], "zip_c": "#3b3224",
              "face": {"eyes": "round", "brows": True, "ink": "#24131f"}},
    "guy": {"age": "adult", "skin": "#6e4a33", "shirt": "#3b3e4c", "pattern": "solid", "pants": "#3a3d42",
            "shoes": "#0c0c0e", "sleeves": "long", "hair": "none", "hat": "hood", "hat_c": "#3b3e4c", "width": 1.15,
            "face": {"eyes": "round", "brows": True, "ink": "#1a0f0a"}},
}


def person(skin, shirt, pants, hair="cap", hair_c="#2a1d15", hat=None, hat_c="#333333", pattern="solid", extras=None,
           eyes="round", pattern_c=None, **kw):
    d = {"age": "adult", "skin": skin, "shirt": shirt, "pattern": pattern, "pants": pants, "shoes": "#141416",
         "sleeves": "long", "hair": hair, "hair_c": hair_c,
         "face": {"eyes": eyes, "brows": True, "ink": "#24131f"}}
    if hat:
        d.update(hat=hat, hat_c=hat_c)
    if extras:
        d["extras"] = extras
    if pattern_c:
        d["pattern_c"] = pattern_c
    d.update(kw)
    return d


# the leftovers: ten strangers in varied coats, hats and hair (no green, no yellow: those are mine and Tasha's)
extras = {
    "x0": person("#c68c5a", "#3d6ea6", "#2a2d3a", "spiky", "#2a1d15"),
    "x1": person("#e0b48c", "#c4523a", "#2d2a30", "long", "#6b3a22"),
    "x2": person("#8a5a3c", "#e8e4ee", "#3a3d6a", "cap", "#2a1d15", hat="beanie", hat_c="#c46a3a"),
    "x3": person("#f1c9a0", "#6a3d8a", "#1c1c22", "bun", "#1a1410"),
    "x4": person("#a8704a", "#8f6a52", "#26303a", "buzz", "#1a1410", pattern="stripes", pattern_c="#e8e0d4"),
    "x5": person("#6e4a33", "#2f7f93", "#2a2630", "cap", "#1a1410", hat="fedora", hat_c="#3a3028"),
    "x6": person("#d9a27a", "#d98a3a", "#33303a", "buzz", "#3a2a20"),
    "x7": person("#b88660", "#8a8a98", "#262a36", "cap", "#2a1d15", hat="ballcap", hat_c="#a03a3a"),
    "x8": person("#f1c9a0", "#c9a0b8", "#3a3140", "swoop", "#d9b86a"),
    "x9": person("#9a6a48", "#4a5568", "#22242c", "spiky", "#e8d8b0", extras=["glasses"]),
}
OLD = ("#5c566a", "#6a6475", "#4f4a5a", "#625c70", "#575163")
for i, sh in enumerate(OLD):
    extras[f"o{i}"] = person("#aaa0ae", sh, "#3a3644", "long" if i % 2 else "cap", "#2a2630",
                             eyes="mirror", **({"hat": "beanie", "hat_c": "#4a4658"} if i == 2 else {}))
    extras[f"o{i}"]["face"]["mouth_inside"] = "#07070a"
extras["dark"] = person("#837a90", "#5f5670", "#3c3748", "long", "#26222c", eyes="mirror", height=1.12, width=0.92,
                        head_stretch=1.7)
extras["dark"]["face"]["brows"] = False       # no eyebrows: brows read as a bored man
extras["dark"]["face"]["mouth"] = "line"      # a seam, no lips
extras["dark"]["face"]["mouth_inside"] = "#07070a"
extras["dark"]["matte"] = True

# ---------------------------------------------------------------------------------------------------- time
voice = json.loads((HERE.parent / "voice-timings.json").read_text())
_tl0 = timeline.build({"name": "mirror-maze", "lines": lines, "shots": [{"id": "S0"}], "gap": GAP, "tail": LOOP,
                       "cast": cast}, voice)
AT = timeline.resolver(_tl0["lines"], _tl0["duration"])

_REF = re.compile(r"^(?P<b>[^+-]+)(?P<o>[+-]\d+(?:\.\d+)?)?$")


def fmt(a):
    ref, off = a if isinstance(a, tuple) else (a, 0.0)
    if isinstance(ref, (int, float)):
        return round(ref + off, 3)
    m_ = _REF.match(ref)
    base, o = (m_.group("b"), float(m_.group("o") or 0)) if m_ else (ref, 0.0)
    off = round(off + o, 3)
    return base if abs(off) < 1e-9 else f"{base}{off:+.3f}"


# ---------------------------------------------------------------------------------------------------- acting
NEUTRAL = {"arms": [0, 0], "side": [0, 0], "head": [0, 0], "lean": 0, "tremble": 0, "blink": True, "bow": 0}
acting = {"me": [], "tasha": [], "guy": []}
cues = []


def raw(who, at, **kw):
    acting[who].append({"at": fmt(at), **kw})


def put(who, at, pos, **kw):
    """A cut: the character is there from this instant, with everything it doesn't set back to neutral."""
    keys = acting[who]
    prev = next((k["pos"] for k in reversed(keys) if "pos" in k), None)
    if prev is not None:
        keys.append({"at": fmt(at), "pos": prev})
    base = {**NEUTRAL, "hidden": False, "expr": "neutral"}
    keys.append({"at": fmt(at), "pos": pos, "blend": 0, **base, **kw})


def hide(who, at):
    acting[who].append({"at": fmt(at), "hidden": True, "blend": 0})


def mouth(who, a, b, lo=0.0, hi=0.8, flap=True):
    acting[who].append({"from": fmt(a), "to": fmt(b), "mouth": [lo, hi], "flap": flap})


def stage(at, *ents):
    """A stage cue: who stands where from here (anyone not listed is hidden). Entries: E(...)."""
    cues.append({"at": at, "name": "stage", "put": list(ents)})


def E(who, pos, yaw=0, **kw):
    return {"who": who, "pos": list(pos), "yaw": yaw, **kw}


PS = {}


def props(at, **kw):
    """A props cue; each one restates the whole state (set.py reads only the latest), so the state is carried here."""
    for k, v in kw.items():
        if v is None:
            PS.pop(k, None)
        else:
            PS[k] = v
    cues.append({"at": at, "name": "props", **json.loads(json.dumps(PS))})


def rain(at, on=True, box=None, top=4.0):
    cues.append({"at": at, "name": "rain", "on": on, "box": box or [0, 1, 0, 1], "top": top})


# ---------------------------------------------------------------------------------------------------- shots
shots = []


def S(at, cam, step=2, look=None, dof=None, follow=None, hand=None, note="", rain2d=True):
    d = {"at": at, "cam": cam, "step": step, "look": look, "dof": dof, "follow": follow, "hand": hand, "note": note,
         "rain": rain2d}
    shots.append(d)
    return d


def one(loc, tgt, lens, roll=0):
    return [[0, list(loc), list(tgt), lens] + ([roll] if roll else [])]


def mv(a, b, lens_a, lens_b=None):
    return [[0, list(a[0]), list(a[1]), lens_a], [1, list(b[0]), list(b[1]), lens_b or lens_a]]


IX = 60.0
SY = 12.8                        # the stage pane
TP = (IX - 0.25, 12.15)          # Tasha at the pane
MP = (IX + 0.3, 13.45)           # me behind it
RAIN_IN = [IX - 2.2, IX + 2.2, 6.0, 12.45]
Z_IN = 0.04
BZ = 0.05                        # the boards
PZ = 1.08                        # the gallery floor (PLAT_Z + 0.03)

LOOK_IN = {"camfill": 0.3, "maze": 0, "inside": 0, "wash": 0, "amb": 0.4, "room": 1.0, "roomb": 1.3}
LOOK_NIGHT = {"exposure": 0.8, "camfill": 0.6, "amb": 1.0, "bulbs": 0.5,
              "rim": [[-2.5, 0.5, 6.5], [-9.0, 3.0, 1.4], 3000, 55, "#9aa6d8"],
              "rim2": [[-5.0, 6.0, 7.5], [-12.5, 9.0, 1.6], 3000, 55, "#9aa6d8"]}

# =========================================================================================== 01 the hook, L01
hide("me", 0)
hide("guy", 0)
hide("tasha", 0)
put("tasha", "L01b", [2.9, 7.0, BZ], yaw=0, expr="grin", head=[0, 0])
stage(0, *[E(w, p, 0, expr=e, rim=True) for w, p, e in (
    ("x0", (1.75, 14.3, PZ), "neutral"), ("x1", (3.0, 14.4, PZ), "grin"), ("x2", (4.2, 14.3, PZ), "neutral"))])
LOOK_HOOK = {"exposure": 1.1, "camfill": 1.5, "gal": 1.0, "inside": 1.6, "wash": 1.0}
LOOK_WARN = {"exposure": 1.0, "camfill": 1.3, "gal": 1.2, "inside": 1.6, "wash": 1.0, "amb": 1.0, "bulbs": 0.8,
             "kick": [[2.2, 9.2, 2.4], [3.0, 14.3, 1.6], 900, 40, "#dfe4ff"]}
S(0, mv(((3.0, 7.3, 1.55), (3.0, 14.3, 1.45)), ((3.0, 8.6, 1.6), (3.0, 14.3, 1.78)), 40, 44), 2, look=LOOK_WARN,
  note="the warned-of thing: one pane through the arch holds a lilac-rimmed stranger, nobody in front; pushes in")
S("L01b", mv(((3.2, 3.9, 1.45), (3.0, 11.5, 2.2)), ((3.15, 4.3, 1.5), (3.0, 11.5, 2.2)), 34), 2, look=LOOK_HOOK,
  note="Tasha lit at the maze front, the panes behind her hold a lilac-rimmed crowd on no steps")

# =========================================================================================== 02 the van and the puddle, L02 to L05
hide("tasha", "L02")
VAN = (1.0, -16.0)
stage("L02", *[E(f"x{i}", (3.5 + i * 0.55, VAN[1] + 0.8, 0.02), -90, expr="neutral", rim=True) for i in range(10)])
S("L02", mv(((0.4, -9.6, 1.5), (5.4, -15.2, 1.3)), ((1.2, -9.6, 1.5), (6.0, -15.2, 1.3)), 28), 2,
  look={"exposure": 0.6, "camfill": 0.5, "amb": 1.0},
  note="the fry van's shiny side: a long queue of lilac-rimmed people in the glass")
stage("L03", E("x0", (VAN[0] - 0.9, VAN[1] + 2.3, 0.02), 0, expr="neutral", rim=False),
      E("x1", (VAN[0] + 0.3, VAN[1] + 2.3, 0.02), 0, expr="smirk", rim=False),
      *[E(f"x{i}", (3.5 + (i - 2) * 0.55, VAN[1] + 0.8, 0.02), -90, rim=True) for i in range(2, 10)])
S("L03", one((-2.6, -11.0, 1.6), (0.5, -14.6, 1.4), 22), 2,
  look={"exposure": 1.0, "camfill": 0.8, "amb": 1.0, "rim": [[-2.2, -11.5, 3.0], [0.3, -13.8, 1.2], 900, 60, "#ffd9a0"], "van": [[0.7, -14.4, 2.0], [0.7, -13.2, 1.0], 60, 1.8, "#ffb060"]},
  note="the real hatch: two customers")
# the puddle: a man tying his boot, nobody over him
stage("L04", E("x0", (0.62, 4.5, BZ + 0.07), 180, expr="neutral", bow=60, rim=True, arms=[0, 0], lie=True, scale=0.46))
S("L04", one((0.15, 2.2, 1.45), (0.62, 4.05, 0.05), 30), 2,
  look={**LOOK_NIGHT, "camfill": 1.0}, note="a puddle on the boards holds a man tying his boot, upside down, rimmed, over empty boards")
S("L05", mv(((0.5, 2.6, 1.0), (0.62, 4.05, 0.05)), ((0.6, 3.1, 0.8), (0.62, 3.95, 0.05)), 34), 2,
  look={**LOOK_NIGHT, "camfill": 1.0}, note="he tied it in March: nobody over him")

# =========================================================================================== 03 the truck, L06 to L07
TX, TY, BEDZ = -4.2, 7.2, 1.15
props("L06", truckpanes=True)
waves = [("x0", -7.4, 0.2), ("x1", -6.4, 0.15), ("x2", -5.4, 0.2), ("x3", -4.4, 0.15), ("x4", -6.0, 0.8), ("x5", -4.9, 0.85)]
stage("L06", *[E(w, (x, TY + dy, BEDZ), 0, expr="smirk", wave=True, rim=True, scale=0.86 if dy < 0.5 else 0.7) for w, x, dy in waves])
S("L06", mv(((-2.8, 0.5, 1.7), (-5.0, 7.0, 2.2)), ((-3.8, 0.5, 1.7), (-5.4, 7.0, 2.2)), 26), 2,
  look=LOOK_NIGHT, note="the truck's glass full of waving people, each rimmed")
stage("L07", E("x3", (-4.4, TY + 0.15, BEDZ), 0, expr="smirk", wave=True, rim=True, scale=0.86))
S("L07", one((-1.5, 2.4, 1.9), (-3.3, 6.65, 2.1), 34), 2, look=LOOK_NIGHT,
  note="a brand-new pane, empty, gleaming; a little funny")

# =========================================================================================== 04 me, L08
props("L08", truckpanes=False)
rain("L08", True, RAIN_IN)
put("me", "L08", [MP[0] - 0.2, MP[1], Z_IN], yaw=-30, expr="smirk", head=[20, 0])
hide("tasha", "L08")
stage("L08", E("me", (0, 0, 0), 0, rim=True))
S("L08", one((IX + 0.6, 9.5, 1.55), (IX + 0.1, 13.5, 1.6), 38), 2, look=LOOK_IN, rain2d=False,
  note="me at a pane, side-on, nothing of me in the glass in front: the lilac rim, the bulbs behind me")
mouth("me", "L08", "L08>", 0.1, 0.7)

# =========================================================================================== 05 Tasha and me, L09 to L13
put("tasha", "L09", [TP[0], TP[1], Z_IN], yaw=180, expr="smirk", head=[0, 0])
put("me", "L09", [MP[0], MP[1], Z_IN], yaw=0, expr="neutral")
S("L09", one((IX + 0.55, 9.3, 1.55), (IX, 13.0, 1.5), 36), 2, look=LOOK_IN, rain2d=False,
  note="Tasha and me either side of the pane, rain on her side only")
raw("tasha", "L10", arms=[0, 82], expr="smirk", blend=0.3)
mouth("tasha", "L10.3", "L10>", 0.1, 0.8)
S("L10", one((IX - 0.5, 15.3, 1.65), (TP[0], TP[1], 1.6), 40), 2, look=LOOK_IN, rain2d=False,
  note="her grin through the glass, pointing at my hat")
S("L10.3", one((IX + 0.65, 9.8, 1.7), (MP[0], MP[1], 1.75), 46), 2, look=LOOK_IN, rain2d=False,
  note="my face and the green hat: what's that?")
raw("tasha", "L11", arms=[0, 0], blend=0.3)
raw("me", "L11", expr="smirk")
mouth("me", "L11", "L11>", 0.1, 0.7)
S("L11", one((IX + 0.6, 10.6, 1.7), (MP[0], MP[1], 1.72), 52), 2, look=LOOK_IN, rain2d=False, note="I say pickle")
props("L12", fries=True)
raw("tasha", "L12", arms=[75, 75], expr="smirk", blend=0.3)
mouth("tasha", "L12.2", "L12>", 0.1, 0.8)
S("L12", one((IX - 0.5, 15.3, 1.5), (TP[0], TP[1], 1.3), 38), 2, look=LOOK_IN, rain2d=False,
  note="Tasha with a tray in each hand: whoever says pickle buys the fries")
raw("tasha", "L13", expr="smirk")
raw("me", "L13.2", expr="neutral", arms=[0, 40], blend=0.4)
S("L13", one((IX + 0.55, 9.3, 1.5), (IX + 0.0, 13.0, 1.5), 32), 2, look=LOOK_IN, rain2d=False,
  note="she pays, eating from both trays; I never have")
raw("me", "L13>", arms=[0, 0], blend=0.4)

# =========================================================================================== 06 the last night, L14 to L17
props("L14", fries=False, halfpanes=True)
raw("tasha", "L14", arms=[0, 0], expr="smirk", blend=0.3)
put("guy", "L14", [IX + 2.6, 9.9, Z_IN], yaw=-90, expr="neutral", arms=[40, 40])
raw("guy", "L17>", pos=[IX - 2.6, 9.9, Z_IN])
props("L14", fries=False, halfpanes=True, carry=True, off=[-0.85, 0.0], yaw=270)
stage("L14", E("me", (0, 0, 0), 0, rim=True))
S("L14", mv(((IX + 0.2, 5.6, 1.6), (IX, 12.0, 1.5)), ((IX + 0.2, 6.6, 1.6), (IX, 12.0, 1.5)), 26), 2, look=LOOK_IN,
  rain2d=False, note="roof off, rain; the maze guy carries a pane past")
S("L15", one((0.6, -3.4, 1.5), (0.0, 0.6, 1.3), 30), 2, follow="guy", look=LOOK_IN, rain2d=False,
  note="the maze guy taking the panes down")
MINIS = lambda: [E(w, (0, 0, 0), 0, att={"side": sx, "ahead": -0.12, "up": uz, "yaw": 0}, scale=0.5, expr="neutral", rim=True)
                 for w, sx, uz in (("x0", -0.4, 0.08), ("x1", 0.4, 0.08), ("x2", -0.4, 1.18), ("x3", 0.4, 1.18))]
hide("tasha", "L16")
hide("me", "L16")
stage("L16", *MINIS())
LOOK_CARRY = {**LOOK_IN, "camfill": 0.9}
S("L16", one((0.5, 3.6, 1.55), (0.0, 0.85, 1.3), 30), 2, follow="guy", look=LOOK_CARRY, rain2d=False,
  note="every pane he carried was packed with faces")
S("L17", mv(((0.5, 3.6, 1.55), (0.0, 0.85, 1.4)), ((0.5, 3.9, 1.6), (0.0, 0.85, 1.5)), 34, 40), 2, follow="guy",
  look={**LOOK_CARRY, "camfill": 0.25, "exposure": 0.8}, rain2d=False, note="they all turned to watch me")
stage("L17.1",
      *[E(w, (0, 0, 0), 0, att={"side": sx, "ahead": -0.12, "up": uz, "yaw": 0}, scale=0.5, expr="neutral", rim=True,
          head=[-35 if sx < 0 else 35, 0]) for w, sx, uz in (("x0", -0.4, 0.08), ("x1", 0.4, 0.08), ("x2", -0.4, 1.18), ("x3", 0.4, 1.18))])

# =========================================================================================== 07 the breath, L18 to L19
props("L18", halfpanes=False, carry=False, off=None, yaw=None)
stage("L18", E("me", (0, 0, 0), 0, rim=True))
rain("L18", True, RAIN_IN)
hide("guy", "L18")
put("tasha", "L18", [TP[0], TP[1], Z_IN], yaw=180, expr="smirk", head=[0, 0])
mouth("tasha", "L18", "L18.1>", 0.3, 0.9)
put("me", "L18", [MP[0], MP[1], Z_IN], yaw=0, expr="neutral")
cues.append({"at": "L18.2", "name": "fog", "on": True, "peak": 0.4, "pos": [TP[0], SY - 0.05, 1.5]})
S("L18", one((IX - 0.7, 15.3, 1.65), (TP[0], TP[1], 1.6), 44), 2, look=LOOK_IN, rain2d=False,
  note="Tasha laughed; her side of the glass fogged up")
S("L19", one((IX + 0.55, 9.3, 1.55), (IX + 0.0, 13.0, 1.5), 36), 2, look=LOOK_IN, rain2d=False,
  note="mine never does: her fogged patch, my glass clear")
cues.append({"at": "L20", "name": "fog", "on": False, "pos": [TP[0], SY - 0.05, 1.5]})

# =========================================================================================== 08 the dark panes, L20 to L23
LOOK_DARK = {"camfill": 0.5, "maze": 0, "inside": 0, "wash": 0, "amb": 0.15, "room": 0.7, "roomb": 1.0}
OLDS = [E("o0", (IX + 0.45, 11.2, Z_IN), 0, expr="blank", rim=True), E("o1", (IX - 0.45, 9.4, Z_IN), 0, expr="blank", rim=True),
        E("o2", (IX + 0.45, 7.8, Z_IN), 0, expr="blank", rim=True), E("o3", (IX - 1.5, 10.6, Z_IN), 0, expr="blank", rim=True),
        E("o4", (IX + 1.5, 12.0, Z_IN), 0, expr="blank", rim=True)]
hide("tasha", "L20")
hide("me", "L20")
rain("L20", False)
DK = lambda y: E("dark", (IX, y, Z_IN), 0, expr="blank", rim=True)
CAM_D = ((IX, 2.0, 1.55), (IX, 12.0, 1.7), 26)
stage("L20", *OLDS, DK(12.3))
S("L20", one(*CAM_D), 2, look=LOOK_DARK, rain2d=False, note="the back panes, the oldest figures gone dark, none with a shine")
S("L21", one((IX + 0.7, 7.6, 1.6), (IX + 0.45, 11.2, 1.62), 50), 2, look=LOOK_DARK, rain2d=False, note="a face with no shine")
stage("L22", *OLDS, DK(10.3))
S("L22", one(*CAM_D), 2, look=LOOK_DARK, rain2d=False, note="nobody had come to see them in years")
stage("L23", *OLDS, DK(8.3))
S("L23", one(*CAM_D), 2, look=LOOK_DARK, rain2d=False, note="every time I looked, one was nearer")
stage("L23.2", *OLDS, DK(6.2))
S("L23.2", one(*CAM_D), 2, look=LOOK_DARK, rain2d=False, note="a pane nearer")

# =========================================================================================== 09 behind me, L24 to L26
LOOK_FACE = {"exposure": 0.0, "camfill": 0.0, "maze": 0, "inside": 0, "wash": 0, "amb": 0.05, "room": 0.06, "roomb": 0.1,
             "face": [[IX + 0.05, 12.9, 0.15], [IX - 0.1, 14.35, 2.2], 45, 0.25, "#e6ecff"],
             "kick": [[IX + 0.15, 12.7, 0.25], [IX - 0.1, 14.35, 1.4], 38, 22, "#c8c0e8"],
             "rim": [[IX + 1.4, 16.0, 2.6], [IX - 0.1, 14.3, 1.9], 120, 30, "#b8a8ff"],
             "rim2": [[IX - 1.5, 15.5, 2.6], [IX - 0.1, 14.3, 1.9], 60, 30, "#9a98c8"]}
rain("L24", True, RAIN_IN)
rain("L24.3", False)
rain("L26", True, RAIN_IN)
put("me", "L24", [MP[0] + 0.3, 13.2, Z_IN], yaw=0, expr="scared")
put("tasha", "L24", [TP[0], TP[1], Z_IN], yaw=180, expr="worried", head=[0, 0])
stage("L24", E("me", (0, 0, 0), 0, rim=True), E("dark", (IX - 0.15, 14.35, Z_IN), 0, expr="blank", rim=True, head=[0, 18]))
S("L24", mv(((IX + 0.2, 11.4, 1.55), (IX, 14.2, 1.6)), ((IX + 0.2, 11.9, 1.55), (IX, 14.2, 1.7)), 32, 36), 2, look=LOOK_FACE,
  rain2d=False, note="right behind me, in my glass: the dark one a head too tall")
props("P01", nostage=True)
S("P01", one((IX + 0.12, 12.55, 1.35), (IX - 0.1, 14.35, 2.1), 36), 1, look=LOOK_FACE, rain2d=False,
  note="the hit: its face behind my shoulder, lit from below, grey rim")
S("L25", mv(((IX + 0.12, 12.55, 1.35), (IX - 0.1, 14.35, 2.1)), ((IX + 0.05, 12.7, 1.4), (IX - 0.1, 14.35, 2.1)), 36, 40), 1,
  look=LOOK_FACE, rain2d=False, note="its eyes were black, like a window at night")
props("L26", nostage=False)
raw("tasha", "L26", expr="wide", pos=[TP[0], TP[1], Z_IN], yaw=180, keep_yaw=True)
raw("tasha", "L27-0.05", pos=[TP[0], TP[1], Z_IN], yaw=180, keep_yaw=True)
stage("L26", E("me", (0, 0, 0), 0, rim=True))
S("L26", one((IX - 0.7, 15.3, 1.65), (TP[0], TP[1], 1.65), 44), 2, rain2d=False,
  look={**LOOK_IN, "face": [[IX - 0.7, 14.9, 1.4], [TP[0], TP[1], 1.7], 40, 0.6, "#dfe4ff"]},
  note="Tasha's face lit, staring right at it")
stage("L26+0.85", E("me", (0, 0, 0), 0, rim=True), E("dark", (IX - 0.15, 14.35, Z_IN), 0, expr="blank", rim=True, head=[0, 18]))
S("L26+0.85", one((IX + 0.05, 12.7, 1.4), (IX - 0.1, 14.35, 2.1), 40), 1, look=LOOK_FACE, rain2d=False,
  note="the dark one, stopped")

# =========================================================================================== 10 lifted and tipped, L27 to P02
GUY_AT = [IX, 12.05, Z_IN]
put("guy", "L27", GUY_AT, yaw=180, expr="neutral", arms=[60, 60])
props("L27", halfpanes=True, nostage=True, carry=True, world=[IX, SY, Z_IN, 0.0])
stage("L27", E("me", (0, 0, 0), 0, att={"side": -0.5, "ahead": -0.45, "up": 0.03, "yaw": 0, "tilt": True}, rim=True))
raw("tasha", "L27", expr="worried", yaw=180, pos=[TP[0] - 0.6, TP[1] - 0.2, Z_IN])
S("L27", one((IX + 0.9, 8.0, 1.7), (IX, 12.5, 1.6), 28), 2, look={**LOOK_IN, "room": 1.2}, rain2d=False,
  note="the maze guy lifts my pane, his back to us")
cues.append({"at": "L28.1", "name": "tilt", "deg": 25, "dur": 0.6})
LC, LT = [IX + 0.2, 15.6, 1.7], [IX - 0.3, 11.0, 1.55]
S("L28", [[0, LC, LT, 30, 0], [0.3, LC, LT, 30, 0], [0.75, LC, LT, 30, 25], [1, LC, LT, 30, 25]],
  2, look={**LOOK_IN, "room": 1.2}, rain2d=False,
  note="from inside my whole maze tips about 25 degrees over 0.6 s: the camera rolls with me, the world beyond tips")
# outside, her side: Tasha level in the rain, me tipped in the carried pane
GX, GY = 0.0, 4.8
put("guy", "P02", [1.6, GY, BZ], yaw=-90, expr="neutral", arms=[0, 0], side=[10, 10])
props("P02", halfpanes=False, nostage=False, carry=True, world=None, off=[0.0, 0.95], yaw=90, wet=True)
put("tasha", "P02", [-0.9, 3.4, BZ], yaw=180, expr="smirk", head=[0, 25])
rain("P02", True, [-8.0, 4.0, 1.0, 4.6], 4.5)
S("P02", one((0.4, 0.5, 1.5), (-0.1, 5.0, 1.45), 34), 2, look={**LOOK_NIGHT, "camfill": 1.3}, rain2d=False,
  note="the tilt held from her side: Tasha level in the rain, me tipped inside the pane")

# =========================================================================================== 11 the reveal, L29 to L33
# the guy walks the carried pane west along y = 4.8 to the truck; Tasha walks beside it on the rainy side
GY = 4.8
raw("guy", "L29", pos=[1.6, GY, BZ])
raw("guy", "L33>", pos=[-3.25, GY, BZ])
raw("tasha", "L29", pos=[-0.9, 3.4, BZ], yaw=180)
raw("tasha", "L33>", pos=[-5.7, 3.4, BZ])
rain("L29", True, [-9.0, 4.0, 1.0, 4.55], 4.5)
LOOK_WALK = {**LOOK_NIGHT, "camfill": 1.4}
stage("L29", E("me", (0, 0, 0), 0, att={"side": -0.5, "ahead": -0.45, "up": 0.03, "yaw": 0, "tilt": True}, rim=True))
S("L29", one((-1.0, -3.2, 1.5), (-1.0, 0.45, 1.6), 22), 2, follow="guy", look=LOOK_WALK, rain2d=False,
  note="the reveal said plainly: me in the pane, front at last, the lilac rim and the shine")
S("L30", mv(((-0.7, -2.7, 1.35), (-1.25, 0.2, 1.5)), ((-0.9, -2.5, 1.35), (-1.25, 0.2, 1.5)), 34), 2, follow="guy", look=LOOK_WALK,
  rain2d=False, note="me alone in the pane, the empty boards in front of it: the real me looked in this pane last year")
S("L31", one((2.0, -5.5, 1.7), (-1.4, 0.2, 1.4), 24), 2, follow="guy", look=LOOK_WALK, rain2d=False,
  note="the real me looked in this pane last year, then moved away")
S("L32", one((-1.7, -0.7, 1.65), (0.0, 0.0, 1.65), 50), 2, follow="tasha", look=LOOK_WALK, rain2d=False,
  note="Tasha comes to see me anyway")
S("L33", one((-0.55, -1.35, 1.45), (-0.55, 0.45, 1.4), 46), 2, follow="guy", look=LOOK_WALK, rain2d=False,
  note="the eye close: my glint the brightest point")

# =========================================================================================== 12 the truck, L34 to L35
PANE_T = [TX, 6.55, BEDZ, 0.0]
cues.append({"at": "L34", "name": "tilt", "deg": 0, "dur": 0.6})
props("L34", world=PANE_T, off=None, yaw=None)
put("guy", "L34", [TX - 0.5, 5.2, BZ], yaw=180, expr="neutral", arms=[70, 70])
hide("guy", "L35")
put("tasha", "L34", [TX + 0.45, 3.4, BZ], yaw=180, expr="smirk", head=[0, 0])
rain("L34", True, [-9.0, 0.0, 0.5, 5.0], 4.5)
stage("L34", E("me", (0, 0, 0), 0, att={"side": -0.5, "ahead": -0.45, "up": 0.03, "yaw": 0, "tilt": True}, rim=True))
LOOK_TRUCK = {**LOOK_NIGHT, "camfill": 1.0,
              "kick": [[-1.0, 1.0, 3.2], [TX, 6.8, 2.2], 5000, 40, "#c9b8ff"]}
S("L34", one((-6.5, -2.5, 1.8), (TX, 6.8, 2.0), 28), 2, look=LOOK_TRUCK, rain2d=False,
  note="the truck at the field's edge; my pane is set on it")
raw("me", "L35", expr="worried")
S("L35", one((TX - 0.2, 3.7, 1.5), (TX - 0.2, 6.9, 2.5), 34), 2, look=LOOK_TRUCK, rain2d=False,
  note="nobody there will come to see me")

# =========================================================================================== 13 she looks at herself, L36 to L39
put("tasha", "L36", [TX + 0.45, 4.7, BZ], yaw=180, expr="smirk", head=[0, -12])
S("L36", one((TX + 1.4, 3.0, 1.7), (TX - 0.2, 6.9, 2.5), 32), 2, look=LOOK_TRUCK, rain2d=False,
  note="all week she'd only looked at me")
TR = E("tr", (0, 0, 0), 0, att={"side": 0.5, "ahead": -0.95, "up": 0.03, "yaw": 0}, expr="smirk", rim=True)
ME_T = E("me", (0, 0, 0), 0, att={"side": -0.5, "ahead": -0.45, "up": 0.03, "yaw": 0}, rim=True)
stage("L37.1", ME_T, TR)
raw("tasha", "L37", expr="smirk", head=[0, -12])
S("L37", one((TX + 1.0, 3.1, 1.6), (TX + 0.1, 6.9, 2.5), 30), 2, look=LOOK_TRUCK, rain2d=False,
  note="she looks at herself on purpose: her reflection appears beside me, rimmed")
raw("tasha", "L38", pos=[TX + 0.45, 0.6, BZ], yaw=0, expr="smirk")
S("L38", one((TX - 1.0, 5.6, 2.0), (TX + 0.45, 1.8, 1.4), 38), 2, look=LOOK_TRUCK, rain2d=False,
  note="she walks back into the rain; her reflection stays")
S("L39", mv(((TX + 0.1, 3.5, 1.9), (TX - 0.05, 6.9, 2.6)), ((TX + 0.1, 3.9, 2.0), (TX - 0.05, 6.9, 2.6)), 30, 34), 2,
  look=LOOK_TRUCK, rain2d=False, note="and her reflection stayed with me")

# =========================================================================================== 14 the joke goes on, L40 to L41
hide("tasha", "L40")
stage("L40", ME_T, E("tr", (0, 0, 0), 0, att={"side": 0.5, "ahead": -0.95, "up": 0.03, "yaw": 0}, expr="smirk", arms=[0, 82],
                     rim=True))
S("L40", one((TX + 0.3, 3.8, 2.3), (TX + 0.0, 6.9, 2.6), 36), 2, look=LOOK_TRUCK, rain2d=False,
  note="on the truck her reflection points at my hat: what's that?")
stage("L41", E("me", (0, 0, 0), 0, att={"side": -0.5, "ahead": -0.45, "up": 0.03, "yaw": 0}, expr="smirk", rim=True),
      E("tr", (0, 0, 0), 0, att={"side": 0.5, "ahead": -0.95, "up": 0.03, "yaw": 0}, expr="smirk", rim=True))
raw("me", "L41", expr="smirk")
S("L41", one((TX - 0.1, 4.6, 2.5), (TX - 0.3, 6.9, 2.7), 46), 2, look=LOOK_TRUCK, rain2d=False,
  note="I said pickle, every time: my grin")

# =========================================================================================== 15 the last turn, L42 to L43
put("tasha", "L42", [TX - 0.5, 2.4, BZ], yaw=180, expr="smirk", arms=[0, 150])
raw("tasha", "L42+0.8", arms=[0, 120], blend=0.3)
raw("tasha", "L43", arms=[0, 150], blend=0.3)
stage("L42", ME_T, E("tr", (0, 0, 0), 0, att={"side": 0.5, "ahead": -0.95, "up": 0.03, "yaw": 0}, expr="smirk", rim=True))
S("L42", one((TX - 1.4, -3.4, 1.8), (TX, 6.9, 2.2), 38), 2, look=LOOK_TRUCK, rain2d=False,
  note="the pane on the truck from outside, two of us in it; the real Tasha small on the duckboards, waving")
stage("L43", ME_T, TR,
      E("dark", (0, 0, 0), 0, att={"side": 0.0, "ahead": -1.75, "up": 0.03, "yaw": 0}, expr="blank", rim=True))
LOOK_END = {**LOOK_TRUCK, "face": [[TX + 0.2, 6.9, 1.2], [TX + 0.05, 8.0, 2.3], 50, 0.8],
            "rim2": [[TX + 1.8, 9.6, 3.6], [TX + 0.05, 8.0, 2.0], 900, 30, "#b8a8ff"]}
S("L43", mv(((TX - 0.6, 0.6, 2.2), (TX, 6.9, 2.4)), ((TX - 0.15, 3.9, 2.0), (TX + 0.0, 7.7, 2.7)), 36, 34), 2,
  look=LOOK_END, rain2d=False, note="a push into the pane: deep behind us, the dark one, a pane nearer than it should be")

# ---------------------------------------------------------------------------------------------------- assemble
out_shots, looks, dofs, rain_shots = [], {}, {}, []
for i, d in enumerate(shots):
    sid = f"S{i + 1:02d}"
    sh = {"id": sid, "cam": d["cam"], "step": d["step"], "hand": 0.0 if d["step"] == 4 else (0.006 if d["step"] == 1 else 0.01),
          "note": d["note"]}
    if i:
        sh["at"] = d["at"]
    if d["follow"]:
        sh["follow"] = d["follow"]
    out_shots.append(sh)
    if d["look"]:
        looks[sid] = d["look"]
    if d["dof"]:
        dofs[sid] = d["dof"]
    if d["rain"]:
        rain_shots.append(sid)


def key_t(k):
    return AT(k["from"]) if "from" in k else AT(k["at"])


for who in acting:
    ks = acting[who]
    order = sorted(range(len(ks)), key=lambda j: (round(key_t(ks[j]), 3), j))
    acting[who] = [ks[j] for j in order]
acting = {w: ks for w, ks in acting.items() if ks}
cues.sort(key=lambda c: AT(c["at"]))

story = {
    "slug": "ep15-mirror-maze",
    "title": "Your Reflection STAYS When You Walk Away",
    "made_for_kids": False,
    "premise": "In a town where your reflection stays behind in the glass when you walk away, I meet my best friend Tasha at the travelling fair's mirror maze every night, and on the last night the maze guy starts loading the panes onto the truck.",
    "twist": "I'm not the person, I'm the reflection the real me left in a maze pane last year before moving away. I've never left a reflection because I am one. Tasha has come every night to see me, and when my pane goes on the truck she looks at herself in it on purpose, so her reflection stays behind with mine.",
    "world": "a travelling fair packing up in the rain at night, in a town where every reflection stays where it was made: duckboards over mud, a puddle that still holds a man tying his boot, a flatbed truck of glass panes full of waving strangers, a fry van whose side holds a long queue, and a lilac-bulbed mirror maze with its roof off",
    "voice": {"voice": "am_adam", "tempo": 1.03, "rate": 1.45},
    "key_color": "#ffd23a",
    "gap": GAP,
    "tail": LOOP,
    "fade_in": False,
    "look": {"fog": "#1c1826", "fog_density": 0.055, "fog_start": 3.5, "sky": "#120f18", "exposure": 0.7, "flash_safe": True},
    "grade": {"shadows": [0.03, -0.02, 0.07], "highlights": [-0.02, 0.0, 0.03], "saturation": 0.9, "contrast": 1.1,
              "vignette": 0.5, "bloom": 0.4, "grain": 0.012, "red_line": 0.78},
    "rain_shots": rain_shots,
    "rain_gain": 1.2,
    "phonemes": {"Tasha's": "tˈɑʃəz", "too": "tˈuːː"},
    "cast": cast,
    "extras": extras,
    "lines": lines,
    "shots": out_shots,
    "acting": acting,
    "cues": cues,
    "looks": looks,
    "dof": dofs,
    "light_only": {"face": ["dark.*", "me.headm", "tasha.headm"]},
    "fx": [],
    "music": {"root": 40, "mode": "dorian", "bpm": 76, "seed": 15,
              "sections": [
                  {"at": 0, "voices": ["drone", "pad"], "energy": 0.3},
                  {"at": "L14", "voices": ["drone", "pad", "piano"], "energy": 0.4},
                  {"at": "L20", "voices": ["drone", "pad", "piano", "pulse"], "energy": 0.62},
                  {"at": "P01", "voices": ["drone"], "energy": 0.25},
                  {"at": "L27", "voices": ["drone", "pad", "piano"], "energy": 0.5},
                  {"at": "L29", "voices": ["pad", "piano"], "energy": 0.3},
                  {"at": "L39", "voices": ["piano", "pad", "drone"], "energy": 0.55, "mode": "major", "root": 40},
                  {"at": "L42", "voices": ["drone"], "energy": 0.2},
              ]},
    "sound": {"floor": "wood", "steps_db": -20,
              "ambience": [
                  {"kind": "rain", "from": 0, "to": "end", "lufs": -34},
                  {"kind": "wind", "from": "L06", "to": "L08", "lufs": -40},
                  {"kind": "hum", "from": "L09", "to": "L19", "lufs": -42},
                  {"kind": "drips", "from": "L20", "to": "L26", "lufs": -40},
              ],
              "rev": 3,
              "sfx": [
                  {"at": "L01>-0.35", "kind": "hit", "db": -9},
                  {"at": "L01>-0.35", "kind": "whoosh", "db": -20},
                  {"at": "P01", "kind": "hit", "db": -6},
                  {"at": "P01", "kind": "sting", "db": -9},
                  {"at": "L23", "kind": "riser", "db": -20, "dur": 1.8},
                  {"at": "L27.2", "kind": "whoosh", "db": -18},
                  {"at": "L34", "kind": "click", "db": -14},
                  {"at": "L37.1", "kind": "bell", "db": -22},
              ],
              "music_drops": [{"from": "L24.3", "to": "P01>", "keep": ["hit", "sting"]},
                              {"from": "L28.2", "to": "P02>"}]},
}
OUT.write_text(json.dumps(story, indent=1, ensure_ascii=False) + "\n")
print("wrote", OUT, f"({len(out_shots)} shots)")
