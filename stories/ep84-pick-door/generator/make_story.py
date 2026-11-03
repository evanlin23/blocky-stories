"""Writes ../story.json for "Pick A Door, Comment The NUMBER" (ep84-pick-door, batch 7).

Run from anywhere: python stories/ep84-pick-door/generator/make_story.py
The words are in lines.json next to this file. Everything else is here: the cast (you, and the two copies of you
standing in the rooms behind the doors), the shots and their cameras, the acting, the cues set.py reads
(ring = the countdown ring on the camera, open = a door swinging open) and the score.

World (metres, z up, doors in the far wall y=3, camera looks +y): room n spans y 7.2n-4 .. 7.2n+3, its door wall
is at y 7.2n+3 .. 7.2n+3.2 and the next room starts right behind it. Doors at x -1.25, 0, 1.25. Door four is the
open doorway in room 0's back wall (y -4.2..-4), the hall beyond it. Acting yaw: 0 faces -y, 180 faces +y.
"""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE.parent / "story.json"
lines = json.loads((HERE / "lines.json").read_text())
LOOP = 0.25
DX = {1: -1.25, 2: 0.0, 3: 1.25}

YOU = {"age": "adult", "skin": "#f1c9a0", "shirt": "#f4ecd6", "pattern": "solid", "pants": "#2b2f3a",
       "shoes": "#fbfbf8", "sleeves": "long", "hair": "buzz", "hair_c": "#5a3a22", "extras": ["hooddown"],
       "extra_c": "#8cff3a", "face": {"eyes": "round", "brows": True, "ink": "#24131f"}}
cast = {"you": dict(YOU), "you2": dict(YOU), "you3": dict(YOU)}

acting = {k: [] for k in cast}
cues = []
shots = []


def K(who, at, pos=None, yaw=None, expr=None, **kw):
    d = {"at": at, **kw}
    if pos is not None:
        d["pos"] = pos
    if yaw is not None:
        d["yaw"] = yaw
    if expr is not None:
        d["expr"] = expr
    acting[who].append(d)


def S(at, cam, step=1, hand=0.004, note="", **kw):
    d = {"id": kw.pop("id", f"S{len(shots) + 1:02d}"), "cam": cam, "step": step, "hand": hand}
    if shots:
        d["at"] = at
    if note:
        d["note"] = note
    d.update(kw)
    shots.append(d)


def cam(p, t, lens, p2=None, t2=None, lens2=None):
    ks = [[0, list(p), list(t), lens]]
    if p2 or t2 or lens2:
        ks.append([1, list(p2 or p), list(t2 or t), lens2 or lens])
    return ks


def ring(at, num=0, f0=0.0, f1=None, spin=0.0, pop=False, big=1.0, cx=0.0, cy=0.0):
    cues.append({"at": at, "name": "ring", "num": num, "f0": f0, "f1": f0 if f1 is None else f1, "spin": spin,
                 "pop": pop, "big": big, "cx": cx, "cy": cy})


def opn(at, room, door):
    cues.append({"at": at, "name": "open", "room": room, "door": door})


# ------------------------------------------------------------------------------------------------ the ring
ring(0, 0, 0.04)
ring("L03", 0, 0.04, 1.0)
ring("L09", 3, 1.0, pop=True)
ring("L09b", 2, 0.667, pop=True)
ring("L09c", 1, 0.333, pop=True)
ring("L09c>", 0, 0.0)
ring("P10", 0, 0.0, spin=0.33)
ring("L16", 4, 1.0, big=2.3, cx=0.62, cy=-0.28)
ring("L17", 4, 1.0, big=1.0)
ring("L19", 0, 0.0, spin=0.12)
ring("L20", 0, 0.0, 1.0, spin=0.0)

# ------------------------------------------------------------------------------------------------ acting
K("you", 0, [0, 1.7], 180, "neutral", hidden=True, blend=0.0)
K("you", "L02.2", [0, 1.7], 180, "neutral", hidden=False, blend=0.0)
K("you", "L03", [0, 1.7], 180, "neutral", hidden=True, blend=0.0)
K("you", "L05", [0, 1.7], 0, "worried", arms=[0, 0], hidden=False, blend=0.0)
for i, a in enumerate((0, 40, 8, 40, 8)):
    K("you", f"L05+{0.2 + 0.22 * i:.2f}", [0, 1.7], 0, "worried", arms=[0, a], blend=0.1)
K("you", "L06", [0, 1.7], 180, "worried", arms=[0, 0], hidden=True, blend=0.0)
K("you", "L10", [0, 1.7], 180, "worried", hidden=False, blend=0.0)
K("you", "L13", [0, 1.7], 180, "scared", blend=0.0)
K("you", "L14", [0, 1.7], 0, "scared", blend=0.0)
K("you", "L15", [0, 1.7], 0, "scared", hidden=True, blend=0.0)
K("you", "L19.2", [0, 1.7], 0, "soft", hidden=False, blend=0.0)
K("you", "L20", [0, 1.7], 180, "worried", blend=0.0)
K("you2", 0, [0, 8.9], 180, "neutral")
K("you2", "L13", [0, 8.9], 180, "scared", blend=0.3)
K("you3", 0, [0, 16.1], 180, "neutral")

# ------------------------------------------------------------------------------------------------ shots
S(0, cam((0, -1.7, 1.75), (0, 3, 1.95), 17, (0, -0.4, 1.8)), id="S01", note="three doors close, push in, warm wedge on the floor")
S("L02", cam((-1.2, 0.6, 1.8), (-1.25, 3, 2.1), 24, (1.2, 0.6, 1.8), (1.25, 3, 2.1), 24), id="S02a", note="slide across the numerals")
S("L02.2", cam((0.9, -0.5, 1.15), (0, 2.4, 1.7), 24, (0.6, -0.2, 1.25), (0, 2.4, 1.7), 24), id="S02b", note="you from behind on the mat")
S("L03", cam((-1.25, 0.8, 1.9), (-1.25, 3, 1.9), 26, (-1.25, 1.5, 1.7), (-1.25, 3, 1.5), 26), id="S03", note="door one, warm glow under it")
S("L04", cam((0.6, 1.6, 1.15), (0.33, 3, 1.2), 30, (0.45, 2.1, 1.2), (0.33, 3, 1.2), 30), id="S04", note="door two knob, phone ringing", hand=0.003)
S("L05", cam((0.15, -0.3, 1.1), (0, 1.7, 1.0), 26, (0.1, 0.2, 1.1), (0, 1.7, 1.0), 26), id="S05", note="you pat the pocket", hand=0.003)
S("L06", cam((1.5, 0.3, 0.3), (1.35, 1.7, 0.05), 24, (1.5, 0.8, 0.28), (1.35, 1.7, 0.05), 24), id="S06", note="low on the worn mat")
S("L07", cam((0.5, 0.95, 2.9), (0.5, 1.6, 0), 30, (0.5, 1.3, 2.7), (0.5, 1.6, 0), 30), id="S07", note="top-down on the mat")
S("L08", cam((0, 0.4, 0.5), (0, 3, 2.0), 20, (0, 1.2, 1.0), (0, 3, 2.0), 20), id="S08", note="ring filling, doors behind")
S("L09", cam((1.25, 0.2, 1.95), (1.25, 3, 2.0), 30, (1.25, 1.0, 1.95), (1.25, 3, 2.0), 30), id="S09a", note="THREE on door three")
S("L09b", cam((0, 0.2, 1.95), (0, 3, 2.0), 30, (0, 1.0, 1.95), (0, 3, 2.0), 30), id="S09b", note="TWO")
S("L09c", cam((-1.25, 0.2, 1.95), (-1.25, 3, 2.0), 30, (-1.25, 1.0, 1.95), (-1.25, 3, 2.0), 30), id="S09c", note="ONE")
S("P10", cam((0, -0.8, 1.85), (0, 3, 2.0), 21, (0, 0.0, 1.9), (0, 3, 2.0), 21), id="S09d", note="the drop: three doors still")
S("L10", cam((3.0, 1.7, 1.6), (0, 1.7, 1.5), 30, (2.6, 1.7, 1.6), (0, 1.7, 1.5), 30), id="S10", note="you in profile, worried", hand=0.004)
S("L11", cam((-1.0, 0.0, 1.7), (-1.1, 6, 1.6), 22, (-1.0, 0.9, 1.7), (-1.1, 6, 1.6), 22), id="S11", note="door one swings open on the same room")
S("L12", cam((-1.2, 1.2, 1.7), (-1.25, 10, 1.5), 22, (-1.2, 6.2, 1.7), (-1.25, 10.4, 1.5), 22), id="S12", note="push through door one, the copy's door one opens")
S("L13", cam((0.35, 0.6, 1.7), (0, 8.6, 1.6), 22, (0.2, 1.0, 1.7), (0, 8.6, 1.6), 22), id="S13", note="door two opens, you from behind in the copy")
S("L14", cam((0, -0.5, 1.5), (0, 1.7, 1.55), 30, (0, 0.0, 1.5), (0, 1.7, 1.55), 30), id="S14", note="you scared, doors open behind", hand=0.003)
S("L15", cam((0.3, 0.3, 0.25), (0, -2.8, 0.05), 24, (0.15, -0.5, 0.2), (0, -3.0, 0.05), 24), id="S15", note="low on the floor: the warm light")
S("L16", cam((0, 0.2, 1.7), (0, 3, 1.9), 20, (0, 0.7, 1.7), (0, 3, 1.9), 20), id="S16", note="the ring, a four fades in")
S("L17", [[0, [0, 0.4, 1.6], [0, 3.4, 1.55], 22], [0.5, [0, 0.4, 1.6], [-3.0, 0.4, 1.55], 22],
          [1, [0, 0.4, 1.6], [0, -2.6, 1.5], 22]], id="S17", note="turn 180: door four behind you, open", hand=0.002)
S("L18", cam((0, -2.9, 1.45), (0, -7.5, 1.1), 22, (0, -3.6, 1.4), (0, -7.5, 1.1), 22), id="S18", note="through door four: the hall; the lime tally on the jamb")
S("L19", cam((-0.5, -4.4, 1.4), (1.35, -6.0, 1.1), 22, (0.0, -4.9, 1.35), (1.35, -6.0, 1.1), 22), id="S19a", note="the lamp, shade on")
S("L19.2", cam((3.0, 1.7, 1.6), (0, 1.7, 1.5), 30, (2.6, 1.7, 1.6), (0, 1.7, 1.5), 30), id="S19b", note="you in profile, soft")
S("L20", cam((0, -0.6, 1.6), (0, 3, 1.8), 22, (0, 0.0, 1.65), (0, 3, 1.8), 22), id="S20", note="back to the three, warm light behind you")
S("L21", cam((0, -2.6, 1.7), (0, 3, 1.95), 17, (0, -1.7, 1.75), (0, 3, 1.95), 17), id="S21", note="push in to S01's framing")

opn("L11", 0, 1)
opn("L12+0.1", 1, 1)
opn("L13", 0, 2)
opn("L14", 0, 3)

look = {"fog": "#f4f6f8", "fog_density": 0.002, "fog_start": 40.0, "sky": "#eef2f6", "exposure": 0.0,
        "flash_safe": True, "style": "closer",
        "polish": {"emph": ["L01", "L07", "L12", "L16", "L21"], "reveal": ["L11", "L16"], "twist": "L16",
                   "quiet": [["L18", "L19"]], "sway": ["S10", "S14"], "camera": True, "idle": True, "ease": True}}

story = {
    "slug": "ep84-pick-door",
    "rev": 1,
    "title": "Pick A Door, Comment The NUMBER \U0001F6AA",
    "made_for_kids": False,
    "premise": "In one bright white room there are three painted exits, each with a number and one clue, and whoever "
               "picks the wrong one lives behind it forever. You get three seconds to pick.",
    "twist": "All three open back into the room you are standing in, because you have picked one a thousand times "
             "already. The only right way out is number four, the open way you came in by, behind you, with the hall "
             "light left on, and you will still turn back to the three.",
    "world": "a clean square white room with a pale floor, three tall painted exits side by side, a worn sisal mat, "
             "and behind the viewer an open way into a warm cream hall with a mustard lamp",
    "voice": {"voice": "am_adam", "tempo": 1.03, "rate": 1.45},
    "key_color": "#8cff3a",
    "gap": 0.12,
    "tail": LOOP,
    "min_read": 0.15,
    "fade_in": False,
    "fade_out": False,
    "look": look,
    "grade": {"shadows": [-0.005, 0.0, 0.02], "highlights": [0.01, 0.005, -0.01], "saturation": 1.1, "contrast": 1.04,
              "vignette": 0.12, "bloom": 0.1, "grain": 0.006, "red_line": 0.7},
    "cast": cast,
    "lines": lines,
    "shots": shots,
    "acting": acting,
    "cues": cues,
    "music": {"root": 50, "mode": "whole", "bpm": 140, "seed": 84,
              "sections": [
                  {"at": 0, "voices": ["pulse", "pluck_hi", "bubble"], "energy": 0.6},
                  {"at": "L09", "voices": ["pulse", "pad"], "energy": 0.3},
                  {"at": "L10", "voices": ["drone", "pulse"], "energy": 0.45, "mode": "minor"},
                  {"at": "L17", "voices": ["pad", "pluck"], "energy": 0.4, "mode": "major"},
                  {"at": "L20", "voices": ["pulse", "pluck_hi", "pad"], "energy": 0.55, "mode": "whole"},
              ]},
    "sound": {
        "rev": 1, "floor": "wood", "steps_db": -24,
        "ambience": [{"kind": "room", "from": 0, "to": "end", "lufs": -44}],
        "sfx": [
            {"at": "L01>-0.3", "kind": "thud", "db": -14},
            {"at": "L04+0.1", "kind": "bell", "db": -26, "dur": 0.8},
            {"at": "L09", "kind": "click", "db": -22},
            {"at": "L09b", "kind": "click", "db": -22},
            {"at": "L09c", "kind": "click", "db": -22},
            {"at": "L11", "kind": "latch", "db": -16},
            {"at": "L11+0.12", "kind": "creak", "db": -22, "dur": 0.8},
        ],
        "music_drops": [{"from": "L09c>", "to": "P10>"}],
    },
}
OUT.write_text(json.dumps(story, indent=1, ensure_ascii=False) + "\n")
print(f"{len(shots)} shots, {len(cues)} cues")
