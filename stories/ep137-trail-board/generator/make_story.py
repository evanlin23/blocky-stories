"""Writes ../story.json for "The Trail Board Painted at DUSK" (ep137-trail-board, batch 15a, interactive lane).

Run from anywhere: python stories/ep137-trail-board/generator/make_story.py
The words are in lines.json (captions already in 2 to 3 word chunks; L01.3 means chunk 3). Everything else is here.

World (metres, z up, characters face the camera at yaw 0, i.e. toward -y): the board at the origin facing -y (2.4 m wide,
panel z 0.9 to 2.5), the pine bench at (5, 1.2), the warden's hut at (-5.5, 6.5) with its door on y 5.5, the creek at
x 8.2 to 12.2, the creek path at x 6.5 to 7.5 running +y, the fence on y 9.5, the sun low behind the board (+y).
Cameras are placed by the width of frame they show at the target (C): lens 45 shows 2.0 m at 6.7 m.
"""
import json
import math
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[2]))
OUT = HERE.parent / "story.json"
lines = json.loads((HERE / "lines.json").read_text())

# ---------------------------------------------------------------------------------------------------- cast
FACE = {"eyes": "round", "brows": True, "ink": "#24131f"}
LASH = {"eyes": "lashes", "brows": True, "ink": "#24131f"}
cast = {
    "me": {"age": "adult", "skin": "#f1c9a0", "shirt": "#2a3e6a", "pattern": "solid", "pants": "#b59f78",
           "shoes": "#5a3b22", "sleeves": "long", "hair": "swoop", "hair_c": "#c9a46a", "face": dict(FACE)},
    "june": {"age": "adult", "skin": "#f1c9a0", "shirt": "#ffd23a", "pattern": "solid", "pants": "#4a4258",
             "shoes": "#6a4a2a", "sleeves": "long", "hair": "long", "hair_c": "#7a2a1a", "face": dict(LASH)},
    "dot": {"age": "adult", "skin": "#e8b891", "shirt": "#f3e9d0", "pattern": "solid", "pants": "#6b6a4a",
            "shoes": "#4a3a2a", "sleeves": "long", "hair": "bun", "hair_c": "#f2f2f2", "height": 0.92,
            "extras": ["apron"], "extra_c": "#2f7a45",
            "face": {**LASH, "bags": True}},
    "marcus": {"age": "adult", "skin": "#c98f62", "shirt": "#b8322a", "pattern": "plaid", "pattern_c": "#2a2a2a",
               "pants": "#3a4a6a", "shoes": "#3a2a1a", "sleeves": "long", "hair": "buzz", "hair_c": "#3a2616",
               "hat": "beanie", "hat_c": "#2a2a30", "face": dict(FACE)},
}

NEUTRAL = {"arms": [0, 0], "side": [0, 0], "head": [0, 0], "lean": 0, "tremble": 0, "blink": True}
acting = {k: [] for k in cast}
cues = []
shots = []


def raw(who, at, **kw):
    acting[who].append({"at": at, **kw})


def put(who, at, pos, yaw=0, expr="neutral", **kw):
    """The character is there from this instant (a cut); everything it doesn't set goes back to neutral."""
    keys = acting[who]
    prev = next((k["pos"] for k in reversed(keys) if "pos" in k), None)
    if prev is not None:
        keys.append({"at": at, "pos": prev})
    keys.append({"at": at, "pos": list(pos), "blend": 0, "yaw": yaw, "expr": expr, "hidden": False, **NEUTRAL, **kw})


def gone(who, at):
    acting[who].append({"at": at, "hidden": True, "blend": 0})


def cue(at, name, **kw):
    cues.append({"at": at, "name": name, **kw})


def talk(who, frm, to, amt=0.55):
    acting[who].append({"from": frm, "to": to, "mouth": [amt, amt], "flap": True})


for k in acting:
    acting[k].append({"at": 0, "pos": [0, 30, 0], "hidden": True, "blend": 0, **NEUTRAL})


# ---------------------------------------------------------------------------------------------------- cameras
def pos_of(tg, d, az, el):
    a, e = math.radians(az), math.radians(el)
    return [round(tg[0] + d * math.sin(a) * math.cos(e), 3), round(tg[1] - d * math.cos(a) * math.cos(e), 3),
            round(tg[2] + d * math.sin(e), 3)]


def C(tgt, w, az=0, el=3, lens=45, w2=None, tgt2=None, az2=None):
    """A camera aimed at tgt, standing so the frame shows w metres across at the target (lens 45: 2 m at 6.7 m).
    With w2 / tgt2 / az2 it moves there over the shot."""
    k0 = [0, pos_of(tgt, w * lens / 13.5, az, el), list(tgt), lens]
    if w2 is None and tgt2 is None and az2 is None:
        return [k0]
    t2 = tgt2 or tgt
    return [k0, [1, pos_of(t2, (w2 or w) * lens / 13.5, az if az2 is None else az2, el), list(t2), lens]]


def X(loc, tgt, lens, loc2=None, tgt2=None, lens2=None):
    ks = [[0, list(loc), list(tgt), lens]]
    if loc2 or tgt2 or lens2:
        ks.append([1, list(loc2 or loc), list(tgt2 or tgt), lens2 or lens])
    return ks


def S(at, cam, look, hand=0.004, dof=None, fill=1.0, step=2, note="", **kw):
    d = {"id": "", "cam": cam, "step": step, "hand": hand, "look": look}
    if shots:
        d["at"] = at
    if dof:
        d["dof"] = dof
    if fill != 1.0:
        d["fill"] = fill
    d.update(kw)
    if note:
        d["note"] = note
    shots.append(d)
    return d


def name(*ids):
    pass


# places
THEO = (-0.35, -0.9)
BOARDW = (0.0, 0.0, 1.7)
BENCH_Z = -0.19
BEN = (5.0, 1.15)
DOT_HUT = (-5.5, 4.2)
DOT_LOT = (-3.5, -1.6)
M_, D_ = "m", "d"

# =========================================================================================== L01 to L07 the rule, working
cue(0, "board", g="one0")
put("me", 0, THEO, 0, "neutral")
S(0, C((0.12, 0, 1.45), 2.0, az=0, el=2, lens=45, w2=1.9), M_, note="S01a frame 1: my face on the left, the board's one glyph line right")
gone("me", "L01.3")
cue("L01.3", "board", g="one0")
S("L01.3", C((0.1, 0, 1.7), 1.7, el=2, w2=1.45), M_, note="S01b punch in on the glyph line on HAVE")
S("L02", C((0.3, 2, 1.9), 4.3, az=-10, el=4, lens=30, w2=3.9), M_, sun2=[0.5, 70.0, 20.0, 3.5], note="S02 wide: the trailhead, the board in the middle")
cue("L03", "board", g="one1")
S("L03", C((0, 0, 1.7), 2.9, el=2, lens=40, w2=2.6), M_, note="S03 the board, one glyph line, fills the frame")
put("dot", "L04", DOT_LOT, 0, "laugh", arms=[45, 45])
cue("L04", "mush", on=True, pos=[DOT_LOT[0], DOT_LOT[1] - 0.7, 0.42], scale=1.5)
S("L04", C((DOT_LOT[0], DOT_LOT[1], 1.2), 2.2, az=12, el=3, w2=2.0), M_, note="S04a Dot alone on the gravel with the giant mushroom")
S("L04.3", C((DOT_LOT[0], DOT_LOT[1], 1.5), 1.5, az=12, el=3, w2=1.3), M_, note="S04b punch in on her face")
gone("dot", "L05")
cue("L05", "mush", on=False)
cue("L05", "board", g="one2")
S("L05", C((0, 0, 1.7), 2.9, el=2, lens=40, w2=2.6, az2=-6), M_, note="S05 the board, a different single glyph line")
put("marcus", "L06", BEN and (BEN[0], BEN[1]), 0, "neutral")
acting["marcus"][-1]["pos"] = [BEN[0], BEN[1], BENCH_Z]
acting["marcus"][-2]["pos"] = [BEN[0], BEN[1], BENCH_Z]
acting["marcus"][-1]["arms"] = [30, 30]
S("L06", C((5.0, 1.15, 1.25), 2.1, az=0, el=3, w2=1.9), M_, note="S06a Marcus on the bench")
cue("L06.2", "canoe", on=True, **{"from": [9.9, 3.7], "to": [9.1, 2.5], "dur": 2.4, "yaw0": 6, "yaw1": -8})
S("L06.2", C((9.6, 2.9, 0.4), 3.5, az=-28, el=14, lens=35, w2=3.1), M_, note="S06b the red canoe drifts to the bank by the bench")
raw("marcus", "L06.5", expr="wide", blend=0.3)
raw("marcus", "L06.5+1.0", expr="laugh", blend=0.3)
S("L06.5", C((5.0, 1.15, 1.25), 1.5, az=0, el=3, w2=1.35), M_, note="S06c Marcus stunned, then laughs")
gone("marcus", "L07")
cue("L07", "canoe", on=False)
cue("L07", "board", g="one3")
S("L07", C((0, 0, 1.7), 3.0, el=2, lens=40, w2=2.4), M_, note="S07 the board's one line, slow push in")

# =========================================================================================== L08 to L10 my turn
put("me", "L08", (0.1, -0.9), 0, "smile")
cue("L08", "board", g="one0")
S("L08", C((-0.2, 0, 1.45), 2.0, el=2, w2=1.9), M_, tally=True, note="S08 my face, smile; the post foot with its tally at the frame bottom")
gone("me", "L09")
put("june", "L09", BEN, 0, "delighted", arms=[30, 30])
acting["june"][-1]["pos"] = [BEN[0], BEN[1], BENCH_Z]
acting["june"][-2]["pos"] = [BEN[0], BEN[1], BENCH_Z]
cue("L09", "gear", on=True)
talk("june", "L09", "L09>", 0.45)
S("L09", C((5.0, 1.15, 1.3), 2.1, el=3, w2=1.9), M_, note="S09 June on the bench, smile, talking (same gold, Saturday)")
gone("june", "L10")
cue("L10", "gear", on=False)
put("me", "L10", THEO, 0, "worried")
S("L10", C((0.12, 0, 1.45), 2.0, el=2, w2=1.9), M_, note="S10 my face, uneasy")

# =========================================================================================== L11 to L14 dusk
gone("me", "L11")
cue("L11", "board", g="one4")
S("L11", X((0.3, -5.0, 0.9), (0.0, 0.0, 3.3), 24, (0.3, -4.4, 0.9), (0.0, 0.0, 3.4), 24), D_,
  note="S11 the board under a huge low orange sun in a pink-orange sky")
S("L12", C((0, 0, 1.7), 2.1, el=2, lens=45, w2=1.8), D_, note="S12 close on the new glyph line in the orange light")
put("me", "L13", THEO, 0, "wide")
S("L13", C((0.12, 0, 1.45), 2.0, el=2, w2=1.9), D_, note="S13 my face, stunned, lit orange")
gone("me", "L14")
put("dot", "L14", DOT_HUT, 0, "worried")
S("L14", C((DOT_HUT[0], DOT_HUT[1], 1.2), 1.7, az=0, el=3, w2=1.5), D_, fill=2.2, note="S14a Dot alone at the hut's white door, orange light")
put("dot", "L14.4", (-0.45, -1.0), 0, "angry")
talk("dot", "L14.4", "L14>", 0.5)
S("L14.4", C((-0.2, 0, 1.5), 1.5, az=0, el=2, w2=1.35), D_, fill=1.5, note="S14b Dot's face, angry, the board behind her in orange light")
gone("dot", "L15")

# =========================================================================================== L15 the fade, L16 the path
cue("L15", "board", g="one4")
S("L15", X((1.0, -5.0, 1.6), (9.0, 14.0, 3.2), 24, (1.2, -4.4, 1.6), (9.0, 14.0, 3.4), 24), D_, fade=[D_, M_],
  note="S15 held wide of the pines and creek bank, board out of frame: dusk fades to sunrise over the whole shot")
cue("L16", "path", on=True)
cue("L16", "board", g="full")
S("L16", X((9.6, -5.0, 3.0), (7.0, 8.0, 0.7), 24, (9.2, -4.4, 2.8), (7.0, 8.5, 0.7), 24), M_,
  note="S16a the creek bank: a clear earth path now runs along the creek into the trees")
S("L16.2", X((7.2, -3.0, 1.3), (7.0, 14.0, 1.1), 30, (7.1, 2.0, 1.25), (7.0, 16.0, 1.1), 30), M_,
  note="S16b a slow push down the path")

# =========================================================================================== L17 to L22 sunrise, the board
put("june", "L17", BEN, 0, "delighted", arms=[30, 30])
acting["june"][-1]["pos"] = [BEN[0], BEN[1], BENCH_Z]
acting["june"][-2]["pos"] = [BEN[0], BEN[1], BENCH_Z]
raw("june", "L17+0.3", lean=40, arms=[25, 25], head=[0, 25], blend=0.8)
cue("L17", "gear", on=True)
S("L17", C((4.6, 1.15, 0.15), 2.5, el=3, w2=2.3), M_, note="S17 June on the bench, lacing her boots, the pack beside her")
raw("june", "L18", lean=0, arms=[30, 30], head=[0, 0], blend=0.5)
S("L18", C((5.0, 1.15, 1.3), 1.4, el=3, w2=1.25), M_, note="S18 June's face, smile")
gone("june", "L19")
cue("L19", "gear", on=False)
cue("L19", "board", g="full")
S("L19", C((0, 0, 1.7), 2.9, el=2, lens=40, w2=2.55), M_, note="S19 the board filled with four lines of glyphs")
S("L19.3", C((0, 0, 1.85), 2.6, el=2, lens=40, w2=2.2), M_, note="S19b push on the four lines as the message is read")
put("me", "L20", THEO, 0, "scared")
S("L20", C((0.12, 0, 1.45), 2.0, el=2, w2=1.9), M_, note="S20 my face, scared")
gone("me", "L21")
S("L21", C((0, 0, 2.05), 1.9, el=2, lens=45, w2=1.6), M_, note="S21 the top two lines, punch in on WHY")
S("L22", C((0, 0, 1.7), 3.2, el=2, lens=40, w2=2.9), M_, note="S22 wide: the whole board, four full lines")

# =========================================================================================== L23 to L27 no answer
put("dot", "L23", (6.9, 0.7), 70, "worried", side=[0, 0])
S("L23", X((9.8, -4.4, 1.5), (6.4, 1.4, 1.15), 36, (9.4, -4.0, 1.5), (6.4, 1.6, 1.15), 36), M_, note="S23a the new path, Dot alone at its mouth, back to us")
put("dot", "L23.3", (6.6, 0.4), 0, "scared", head=[-62, 0])
talk("dot", "L23.3", "L23>", 0.45)
S("L23.3", C((6.6, 0.4, 1.3), 1.5, az=-20, el=2, w2=1.3), M_, note="S23b Dot's face, scared, on OURS; the path behind")
gone("dot", "L24")
put("june", "L24", BEN, 0, "laugh", arms=[30, 30])
acting["june"][-1]["pos"] = [BEN[0], BEN[1], BENCH_Z]
acting["june"][-2]["pos"] = [BEN[0], BEN[1], BENCH_Z]
raw("june", "L24", side=[0, 105], blend=0.4)
raw("june", "L24+0.4", side=[0, 135], blend=0.35)
raw("june", "L24+0.8", side=[0, 105], blend=0.35)
raw("june", "L24+1.2", side=[0, 135], blend=0.35)
put("me", "L24", (3.55, -1.2), 180, "neutral")
S("L24", X((4.1, -3.0, 1.3), (5.0, 1.2, 1.25), 38, (4.2, -2.8, 1.3), None, 38), M_, dof=[4.3, 2.4],
  note="S24 June at the bench, laughing, waving; my shoulder soft 3 m in front of her")
gone("me", "L25")
gone("june", "L25")
S("L25", C((0, 0, 1.7), 2.9, el=2, lens=40, w2=2.5), M_, note="S25 the four-line board")
put("me", "L26", THEO, 0, "worried")
S("L26", C((0.12, 0, 1.45), 2.0, el=2, w2=1.9), M_, note="S26 my face, uneasy, the board's edge behind me")
put("me", "L27", THEO, 0, "scared")
S("L27", C((0.12, 0, 1.45), 2.0, el=2, w2=1.9), M_, note="S27 my face, scared, to camera: S01a's framing for the loop")

# shot ids in order
for i, s in enumerate(shots):
    s["id"] = ""
IDS = ["S01a", "S01b", "S02", "S03", "S04a", "S04b", "S05", "S06a", "S06b", "S06c", "S07", "S08", "S09", "S10", "S11",
       "S12", "S13", "S14a", "S14b", "S15", "S16a", "S16b", "S17", "S18", "S19", "S19b", "S20", "S21", "S22", "S23a",
       "S23b", "S24", "S25", "S26", "S27"]
assert len(IDS) == len(shots), (len(IDS), len(shots))
for s, i in zip(shots, IDS):
    s["id"] = i

# ---------------------------------------------------------------------------------------------------- story
look = {"fog": "#fff2cf", "fog_density": 0.002, "fog_start": 28.0, "sky": "#ffe79a", "exposure": 0.0,
        "flash_safe": True, "style": "closer",
        "polish": {"hold": ["S02", "S11", "S15", "S22"], "ones": "walk"}}
story = {
    "slug": "ep137-trail-board",
    "title": "The Trail Board Painted at DUSK \U0001F332",
    "made_for_kids": False,
    "premise": "Every sunrise the trail board at our trailhead paints one short rule for the day, and obeying it pays off. "
               "This weekend it painted at dusk, which it never does, telling me not to walk a creek path that is on no map, "
               "and at sunrise it repainted itself in four lines to say the opposite: walk it with my sister June so she comes home.",
    "twist": "Nothing is explained. The path is there, June has already seen it, the warden says it isn't theirs and the "
             "board has written two rules for the same morning, so the viewer has to pick which board to trust.",
    "world": "a green trailhead at the edge of town: a gravel lot where a street ends, a white picket fence, a forest-green "
             "board on two posts, a small green warden's hut, a pine bench, tall pines and a shallow blue creek",
    "voice": {"voice": "am_adam", "tempo": 1.03, "rate": 1.45},
    "key_color": "#7dff6a",
    "gap": 0.15,
    "tail": 0.25,
    "fade_in": False,
    "fade_out": False,
    "look": look,
    "grade": {"shadows": [-0.01, 0.0, 0.03], "highlights": [0.03, 0.01, -0.02], "saturation": 1.1, "contrast": 1.05,
              "vignette": 0.15, "bloom": 0.2, "grain": 0.008, "red_line": 0.7, "red_lift_blue": 0.42},
    "cast": cast,
    "lines": lines,
    "shots": shots,
    "acting": acting,
    "cues": cues,
    "set_moves": ["S06b", "S15"],
    "framing_ok": ["S02", "S07", "S15", "S22", "S25", "S23a"],
    "music": {"root": 45, "mode": "dorian", "bpm": 104, "seed": 137,
              "sections": [
                  {"at": 0, "voices": ["bubble", "pulse", "pluck_hi"], "energy": 0.5},
                  {"at": "L11", "voices": ["pad", "pluck"], "energy": 0.25},
                  {"at": "L16", "voices": ["drone", "pad", "pluck"], "energy": 0.4},
              ]},
    "sound": {
        "rev": 1, "floor": "gravel", "steps_db": -22,
        "ambience": [{"kind": "water", "from": 0, "to": "end", "lufs": -42},
                     {"kind": "wind", "from": "L11", "to": "L15", "lufs": -44}],
        "sfx": [{"at": "L06.5-0.15", "kind": "knock", "db": -18, "pattern": [0], "tone": "hand"}],
        "music_drops": [["P1", "P1>"]],
    },
}
from blocky import timeline

vf = HERE.parent / "voice-timings.json"


def key(e):
    return e.get("at", e.get("from"))


if vf.exists():
    voice = json.loads(vf.read_text())
    _tl0 = timeline.build({"name": "ep137-trail-board", "lines": lines, "shots": [{"id": "S0"}], "gap": 0.15, "tail": 0.25,
                           "cast": cast}, voice)
    AT = timeline.resolver(_tl0["lines"], _tl0["duration"])
    for k in acting:
        acting[k].sort(key=lambda e: AT(key(e)))
    cues.sort(key=lambda e: AT(e["at"]))
story["rev"] = 2
OUT.write_text(json.dumps(story, indent=1, ensure_ascii=False) + "\n")
print(f"{len(shots)} shots, {len(cues)} cues")
