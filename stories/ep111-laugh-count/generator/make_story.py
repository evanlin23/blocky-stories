"""Writes ../story.json for "Aunt Bev Hasn't LAUGHED in 492 Days" (ep111-laugh-count, batch 11).

Run from anywhere: python stories/ep111-laugh-count/generator/make_story.py
Words are in lines.json. Metres, z up, cameras look +y at az 0; az 180 puts the camera on the lane side looking back
at the foyer (people facing +y, yaw 180, face it). Yaw 0 faces -y, 90 faces +x. Lying on the back = lean -90.

Places: the foyer y -3..-9 (shoe counter x -6, snack bar x +6), the approach y -1.5..1.5, five lanes (centres
x -5.2, -2.6, 0, 2.6, 5.2) from y 1.5 to 19, pins at y 17.5..19. Our lane is x 0.
Cues set.py reads: n_<who> {v: "492"} the number over that head, gray {g: 0..1} Bev's sleeves, ball {...}, shoe {...},
pins {dur}, lore.
"""
import json
import sys
import math
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[2]))
OUT = HERE.parent / "story.json"
lines = json.loads((HERE / "lines.json").read_text())
LOOP = 0.25

FACE = {"eyes": "round", "brows": True, "ink": "#24131f"}
cast = {
    "me": {"age": "adult", "skin": "#f1c9a0", "shirt": "#2fb8b0", "pattern": "stripes", "pattern_c": "#ffffff",
           "pants": "#3f5f9a", "shoes": "#e0443a", "sleeves": "short", "hair": "spiky", "hair_c": "#16120f",
           "face": dict(FACE)},
    "bev": {"age": "adult", "skin": "#e8b48c", "shirt": "#ff6f61", "pattern": "stripes", "pattern_c": "#ffffff",
            "pants": "#7a4fa3", "shoes": "#f4f4f2", "sleeves": "long", "hair": "mop", "hair_c": "#ff5a3c",
            "extras": ["glasses"], "extra_c": "#ff5fa2", "face": {"eyes": "lashes", "brows": True, "ink": "#24131f"}},
    "earl": {"age": "adult", "skin": "#d9a679", "shirt": "#f1ead8", "pants": "#6b7078", "shoes": "#2a2d3a",
             "sleeves": "long", "vest": "#d94a3d", "hair": "buzz", "hair_c": "#8d9096", "seams": False,
             "face": dict(FACE)},
    "lanefour": {"age": "adult", "skin": "#b4b4b4", "shirt": "#9d9d9d", "pants": "#858585", "shoes": "#767676",
                 "sleeves": "short", "hair": "cap", "hair_c": "#8a8a8a", "face": {"eyes": "round", "brows": True,
                                                                                    "ink": "#3a3a3a"}},
    "wait": {"age": "adult", "skin": "#c98e62", "shirt": "#ff9ccf", "pattern": "stripes", "pattern_c": "#ffffff",
             "pants": "#2a2d3a", "shoes": "#f4f4f2", "sleeves": "short", "hair": "bun", "hair_c": "#2a1d15",
             "face": {"eyes": "lashes", "brows": True, "ink": "#24131f"}},
    "b1": {"age": "adult", "skin": "#f1c9a0", "shirt": "#ffd21a", "pattern": "stripes", "pattern_c": "#ffffff",
           "pants": "#2f6f5f", "shoes": "#f4f4f2", "sleeves": "short", "hair": "swoop", "hair_c": "#5a3a1f",
           "face": dict(FACE)},
    "b2": {"age": "adult", "skin": "#8d5a3a", "shirt": "#7fd16a", "pattern": "stripes", "pattern_c": "#ffffff",
           "pants": "#33405e", "shoes": "#f4f4f2", "sleeves": "short", "hair": "buzz", "hair_c": "#14110e",
           "face": dict(FACE)},
}
cast["earl"].pop("seams", None)

NEUTRAL = {"arms": [0, 0], "side": [0, 0], "head": [0, 0], "lean": 0, "tremble": 0, "blink": True}
acting = {k: [] for k in cast}
cues, shots, VIS = [], [], set()


def put(who, at, pos, yaw=0, expr="neutral", **kw):
    keys = acting[who]
    prev = next((k["pos"] for k in reversed(keys) if "pos" in k), None)
    if prev is not None:
        keys.append({"at": at, "pos": prev})
    keys.append({"at": at, "pos": list(pos), "blend": kw.pop("blend", 0), "yaw": yaw, "expr": expr, "hidden": False,
                 **NEUTRAL, **kw})


def raw(who, at, **kw):
    acting[who].append({"at": at, **kw})


def scene(at, **chars):
    """Exactly these characters are on stage from `at`."""
    for who in cast:
        if who in chars:
            c = dict(chars[who])
            put(who, at, c.pop("pos"), c.pop("yaw", 180), c.pop("expr", "neutral"), **c)
            VIS.add(who)
        elif who in VIS:
            acting[who].append({"at": at, "hidden": True, "blend": 0})
            VIS.discard(who)


def cue(at, name, **kw):
    cues.append({"at": at, "name": name, **kw})


def num(at, who, v):
    cue(at, f"n_{who}", v=str(v))


def count(who, t0, dur, v0, v1, steps):
    for i in range(steps + 1):
        v = round(v0 + (v1 - v0) * i / steps)
        cue(f"{t0}+{dur * i / steps:.2f}", f"n_{who}", v=str(v))


def pos_of(tg, d, az, el):
    a, e = math.radians(az), math.radians(el)
    return [round(tg[0] + d * math.sin(a) * math.cos(e), 3), round(tg[1] - d * math.cos(a) * math.cos(e), 3),
            round(tg[2] + d * math.sin(e), 3)]


def C(tgt, w, az=180, el=5, lens=28, w2=None, tgt2=None, az2=None, el2=None, lift=0.07):
    """Camera aimed at tgt (the subject sits a little above centre) so the frame is w metres wide at the subject."""
    def one(u, tg, ww, a, e):
        if tg[2] >= 1.7:
            ww = max(ww, 1.35)      # head and number both in frame
        d = ww * lens / 13.5
        tg = [tg[0], tg[1], tg[2] - 0.27 * ww - 0.1]
        return [u, pos_of(tg, d, a, e), tg, lens]
    k0 = one(0, tgt, w, az, el)
    if w2 is None and tgt2 is None and az2 is None and el2 is None:
        return [k0]
    return [k0, one(1, tgt2 or tgt, w2 or w, az if az2 is None else az2, el if el2 is None else el2)]


def S(at, cam, hand=0.006, step=2, note="", **kw):
    d = {"id": f"S{len(shots) + 1:02d}", "cam": cam, "step": step, "hand": hand}
    if len(shots):
        d["at"] = at
    if note:
        d["note"] = note
    d.update(kw)
    shots.append(d)


def H(x, y, z=1.5):
    return (x, y, z)


for k in acting:
    acting[k].append({"at": 0, "pos": [0, -30, 0], "hidden": True, "blend": 0, **NEUTRAL})

# places
BEV_D = (-3.0, -3.7)           # Bev at the scoring desk
EARL = (-5.5, -8.4)
GRAY0 = 0.12

# ---------------------------------------------------------------------------- opening: close on Bev, no wide
num(0, "bev", 492)
cue(0, "gray", g=GRAY0)
cue(0, "tagbev", on=True)
scene(0, bev=dict(pos=(*BEV_D, 0), yaw=180, expr="laugh", tremble=3, arms=[8, 8]),
      b1=dict(pos=(-0.7, -2.6, 0), yaw=180, expr="grin"), b2=dict(pos=(0.8, -2.8, 0), yaw=180, expr="laugh"))
num(0, "b1", 17)
num(0, "b2", 3)
bh = H(BEV_D[0], BEV_D[1])
S(0, C((bh[0], bh[1], 1.85), 1.15, 180, 4), note="S01a Bev mid-laugh with 492 over her head, close")
S("L01.2", C((bh[0] + 0.1, bh[1], 2.0), 0.95, 168, 6, w2=0.85), note="S01b her number, close, punch in")
S("L02", C((-0.0, -2.7, 1.9), 2.2, 180, 4, w2=2.0), note="S02a two bowlers' heads, numbers over each")
S("L02.2", C((bh[0], bh[1], 1.9), 1.2, 195, 5, w2=1.05), note="S02b Bev again, laughing, number over her")
S("L02.3", C((bh[0] - 0.1, bh[1], 1.9), 1.0, 150, 4), note="S02c Bev, profile, laughing")

# ---------------------------------------------------------------------------- the rule at work (L03 to L10)
scene("L03", me=dict(pos=(-0.6, -0.5, 0), yaw=180, expr="blank"), bev=dict(pos=(0.9, -0.7, 0), yaw=180, expr="laugh",
      tremble=3), b1=dict(pos=(-2.6, -0.6, 0), yaw=180, expr="grin"), b2=dict(pos=(2.6, -0.4, 0), yaw=180,
                                                                              expr="laugh"),
      lanefour=dict(pos=(5.2, -0.5, 0), yaw=180, expr="laugh"))
num("L03", "me", 0)
num("L03", "bev", 492)
num("L03", "b1", 17)
num("L03", "b2", 3)
num("L03", "lanefour", "9,000")
S("L03", [[0, [0.0, -6.6, 2.5], [0, 9.0, 1.4], 26], [1, [0.0, -5.4, 2.3], [0, 9.0, 1.4], 26]], hand=0.004,
  note="S03 wide: the alley, neon on, league night, everyone's numbers glowing")
S("L03.2", [[0, [-1.2, -1.6, 1.7], [-0.5, 6.0, 1.3], 26], [1, [-0.6, -1.2, 1.7], [0.2, 6.0, 1.3], 26]],
  note="S03b low behind the bowlers toward the lanes")
scene("L04", me=dict(pos=(0.0, -2.6, 0), yaw=180, expr="blank", head=[0, 6]), b1=dict(pos=(-1.8, -5.0, 0), yaw=180,
      expr="grin"), b2=dict(pos=(1.6, -5.4, 0), yaw=180, expr="laugh"))
num("L04", "me", 0)
S("L04", C((0.0, -2.6, 1.9), 1.2, 180, 3), note="S04 me squinting at the numbers, deadpan")
scene("L05", earl=dict(pos=(*EARL, 0), yaw=180, expr="angry", arms=[0, 72]), b1=dict(pos=(-3.9, -6.2, 0), yaw=150,
      expr="laugh", tremble=3))
num("L05", "earl", 0)
num("L05", "b1", 17)
cue("L05", "spray", on=True)
S("L05", C((EARL[0], EARL[1], 1.8), 1.3, 180, 4), note="S05 Earl at shoe rental, scowl, spraying a shoe")
S("L05.1", C((EARL[0] + 0.1, EARL[1], 1.85), 1.0, 160, 4, w2=0.9), note="S05b Earl scowl closer")
S("L06", C((EARL[0] - 0.2, EARL[1], 2.0), 1.3, 205, 5, w2=1.1), note="S06 his number: 0; a bowler laughing")
scene("L07", lanefour=dict(pos=(2.6, 0.2, 0), yaw=180, expr="smile"))
num("L07", "lanefour", "9,000")
cue("L07", "spray", on=False)
S("L07", C((2.6, 0.2, 1.8), 1.8, 180, 4, w2=1.6), note="S07a the man in lane four telling a joke to nobody")
raw("lanefour", "L07.1", expr="laugh", tremble=4, blend=0.1)
S("L07.1", C((2.6, 0.2, 1.7), 1.1, 175, 3, w2=1.0), note="S07b him laughing at it, guffaw")
S("L08", C((2.6, 0.2, 2.15), 0.9, 180, 5, w2=0.8), note="S08 his number: 9,000")
S("L09", C((2.6, 0.2, 2.0), 1.3, 180, 5, tgt2=(2.6, 0.2, 0.55), w2=1.5), note="S09 tilt down him: gray everywhere")
scene("L10", bev=dict(pos=(-1.0, -1.8, 0), yaw=180, expr="grin", side=[0, 55]))
cue("L10", "gray", g=0.18)
num("L10", "bev", 492)
S("L10", C((-1.0, -1.8, 1.7), 1.4, 180, 4, w2=1.3), note="S10 Bev's sleeve, the coral starting to go gray at the cuff")
S("L10.2", C((-1.0, -1.8, 1.7), 1.1, 180, 4, w2=1.3), note="S10b past five hundred your color goes")
# ---------------------------------------------------------------------------- me (L11 to L12)
scene("L11", me=dict(pos=(0.0, -2.6, 0), yaw=180, expr="blank"))
num("L11", "me", 0)
S("L11", C((0.0, -2.6, 1.9), 1.05, 180, 4), note="S11 my number over my head: 0")
scene("L12", me=dict(pos=(0.0, 0.6, 0), yaw=180, expr="worried", lean=14, arms=[10, 25], blend=0.3))
num("L12", "me", 0)
S("L12", C((0.0, 0.6, 1.7), 1.5, 180, 5, w2=1.4), note="S12a me tripping on the approach, wince")
cue("L12.2", "shoe", dur=0.9, x0=0.15, y0=0.9, z0=0.1, x1=0.9, y1=3.2, z1=0.1, lift=1.6)
S("L12.2", C((0.3, 1.8, 1.0), 2.6, 160, 12), note="S12b my shoe flying off")
# ---------------------------------------------------------------------------- Bev (L13 to L18)
scene("L13", bev=dict(pos=(0.8, -1.2, 0), yaw=180, expr="grin", arms=[20, 8], tremble=1.5), me=dict(pos=(-0.8, -1.2, 0),
      yaw=180, expr="blank"))
num("L13", "bev", 492)
num("L13", "me", 0)
S("L13", C((0.8, -1.2, 1.7), 1.5, 185, 4, w2=1.35), note="S13 Bev mid-joke at our lane, grin")
raw("bev", "L14", arms=[85, 85], side=[-18, -18], expr="grin", blend=0.2)
S("L14", C((0.8, -1.2, 1.6), 1.2, 175, 5), note="S14 Bev pointing at herself")
scene("L15", bev=dict(pos=(5.4, -6.6, 0), yaw=0, expr="grin", arms=[0, 30]), wait=dict(pos=(5.4, -8.2, 0), yaw=180,
      expr="smile"))
num("L15", "bev", 492)
num("L15", "wait", 8)
S("L15", C((5.4, -7.4, 1.7), 3.0, 90, 4, w2=2.7), note="S15 Bev leaning on the snack bar, telling the waitress a joke")
scene("L16", bev=dict(pos=(5.6, -5.4, 0), yaw=180, expr="laugh", tremble=4))
num("L16", "bev", 492)
S("L16", C((5.6, -5.4, 1.85), 1.1, 180, 4), note="S16a Bev howling, cackle")
raw("bev", "L16+1.1", pos=[5.6, -5.4, -0.2], blend=0.15)
cue("L16+1.1", "stool", on=True)
S("L16+1.1", C((5.6, -5.4, 1.3), 1.5, 178, 4, w2=1.4), note="S16b Bev sitting down hard on a stool")
S("L17", C((5.6, -5.4, 1.65), 1.0, 180, 4), note="S17 her number, close: unchanged")
cue("L18", "gray", g=0.62)
scene("L18", bev=dict(pos=(5.6, -5.4, -0.2), yaw=180, expr="laugh", tremble=2.5, side=[0, 40]))
num("L18", "bev", 492)
S("L18", C((5.2, -5.4, 1.3), 1.0, 165, 4, w2=0.9), note="S18 her sleeves, gray creeping past the elbow")
cue("L19", "stool", on=False)
# ---------------------------------------------------------------------------- the slip (L19 to L22)
scene("L19", me=dict(pos=(0.0, 0.4, 0), yaw=180, expr="blank", arms=[75, 75]), bev=dict(pos=(0.9, -1.3, 0), yaw=180,
      expr="grin", tremble=2))
num("L19", "me", 0)
num("L19", "bev", 492)
cue("L19", "ball", mode="hold", who="me", y=0.55)
S("L19", C((0.0, 0.45, 1.3), 1.7, 180, 6, w2=1.5), note="S19 me on the approach with a ball")
raw("me", "L20", pos=[0.0, 0.9, 0.0], lean=-30, expr="wide", blend=0.15, arms=[30, 30])
cue("L20", "ball", mode="roll", dur=2.4, x0=0.0, y0=0.9, x1=0.0, y1=9.0)
cue("L21", "ball", mode="off")
S("L20", C((0.0, 1.0, 1.7), 1.5, 180, 8), note="S20a slipping")
put("me", "L20.1", (0.0, 3.6, 0.23), 180, "worried", lean=-90, blend=0.1, blink=False)
S("L20.1", C((0.0, 2.5, 0.5), 1.8, 180, 52, w2=1.6), note="S20b flat on my back on the lane")
scene("L21", me=dict(pos=(0.0, 3.6, 0.23), yaw=180, expr="worried", lean=-90, blink=False),
      bev=dict(pos=(0.15, 0.7, 0), yaw=180, expr="laugh", tremble=4, lean=22, arms=[12, 12]))
num("L21", "me", 0)
num("L21", "bev", 492)
S("L21", C((0.15, 0.8, 1.7), 1.5, 180, 8, w2=1.4), note="S21 Bev above me, snorting with laughter")
S("L22", C((0.0, 2.3, 0.4), 1.4, 180, 55), note="S22a over my head the 0")
num("L22.1", "me", 1)
num("L22.2", "me", 0)
cue("L22.1", "tick", t=0)
S("L22.2", C((0.0, 2.3, 0.4), 1.3, 175, 55, w2=1.2), note="S22b and back to 0")
# ---------------------------------------------------------------------------- the reveal (P01, L23, L24)
S("P01", C((0.0, 2.3, 0.4), 1.4, 178, 55, w2=1.25), note="the drop: my face on the lane, staring up at my number")
scene("L23", me=dict(pos=(0.0, 3.6, 0.23), yaw=180, expr="wide", lean=-90, blink=False),
      bev=dict(pos=(0.2, 0.7, 0), yaw=180, expr="laugh", tremble=4, lean=12, arms=[12, 12], head=[0, -8]))
S("L23", C((0.0, 2.3, 0.4), 1.2, 180, 56, w2=1.1), note="S23a my face, stunned")
S("L23+0.9", C((0.2, 0.7, 1.7), 1.5, 195, 8), note="S23b Bev's number unmoved as she laughs")
S("L24", C((0.1, 1.5, 0.78), 2.1, 180, 33, w2=1.95), hold=True, note="S24 the reveal: me flat, 0 glowing, Bev doubled over, 492")
S("L24.2", C((0.2, 0.7, 1.7), 1.5, 200, 8, w2=1.4), note="S24b Bev, ELSE")
# ---------------------------------------------------------------------------- the rule read right (L25 to L31)
scene("L25", earl=dict(pos=(*EARL, 0), yaw=180, expr="angry"), b1=dict(pos=(-5.2, -6.2, 0), yaw=0, expr="laugh",
      tremble=4), b2=dict(pos=(-6.1, -5.4, 0), yaw=0, expr="laugh", tremble=4), wait=dict(pos=(-4.4, -5.0, 0), yaw=0,
      expr="laugh", tremble=4))
num("L25", "earl", 0)
num("L25", "b1", 140)
num("L25", "b2", 77)
num("L25", "wait", 8)
S("L25", C((-5.4, -7.0, 1.9), 3.0, 192, 5, w2=2.6), note="S25 Earl at the counter, a line of bowlers laughing")
scene("L26", lanefour=dict(pos=(2.6, 0.2, 0), yaw=180, expr="laugh", tremble=3), b1=dict(pos=(1.3, -1.6, 0), yaw=180,
      expr="blank"), b2=dict(pos=(3.9, -1.6, 0), yaw=180, expr="blank"))
num("L26", "lanefour", "9,000")
num("L26", "b1", 61)
num("L26", "b2", 140)
S("L26", C((2.6, -0.7, 1.9), 3.0, 180, 4, w2=2.7), note="S26 lane four's man telling a joke, his whole lane silent")
scene("L27", bev=dict(pos=(0.0, -2.4, 0), yaw=180, expr="grin"))
num("L27", "bev", 492)
S("L27", C((0.0, -2.4, 1.85), 1.1, 180, 4), note="S27 Bev close, grin")
S("L28", C((0.1, -2.4, 1.9), 1.4, 175, 5, w2=1.25), note="S28 her number, close")
scene("L29", me=dict(pos=(0.0, -2.4, 0), yaw=180, expr="smirk", head=[0, 8]))
num("L29", "me", 0)
S("L29", C((0.0, -2.4, 1.85), 1.1, 180, 4), note="S29 me, sheepish, my old too-cool face")
scene("L30", me=dict(pos=(0.0, -2.4, 0), yaw=180, expr="grin", tremble=3), bev=dict(pos=(1.2, -2.4, 0), yaw=200,
      expr="grin"))
num("L30", "me", 0)
num("L30", "bev", 492)
S("L30", C((0.0, -2.4, 1.85), 1.1, 180, 4), note="S30 me laughing loud (a fake laugh)")
S("L31", C((0.75, -2.4, 1.9), 1.5, 175, 5, w2=1.35), note="S31 her number, unmoved")
# ---------------------------------------------------------------------------- the week (L32 to L38)
scene("L32", bev=dict(pos=(0.0, -2.4, 0), yaw=180, expr="smirk"))
num("L32", "bev", 492)
S("L32", C((0.0, -2.4, 1.85), 1.15, 180, 4), note="S32a Bev looking at me, determined")
raw("bev", "L32.2", expr="angry", arms=[75, 75], side=[-25, -25], blend=0.2)
S("L32.2", C((0.0, -2.4, 1.5), 1.5, 180, 4, w2=1.35), note="S32b cracking her knuckles")
scene("L33", bev=dict(pos=(-0.8, -2.0, 0), yaw=150, expr="grin", arms=[30, 20], tremble=1.5),
      me=dict(pos=(0.8, -2.0, 0), yaw=210, expr="blank"))
num("L33", "bev", 495)
num("L33", "me", 0)
cue("L33", "gray", g=0.8)
S("L33", C((0.0, -2.0, 1.75), 2.1, 180, 4, w2=1.9), note="S33 next Thursday: Bev telling a joke, me straight-faced")
scene("L34", bev=dict(pos=(0.0, -2.2, 0), yaw=180, expr="grin", side=[40, 40], tremble=2), me=dict(pos=(1.4, -2.2, 0),
      yaw=205, expr="blank"))
num("L34", "bev", 496)
num("L34", "me", 0)
S("L34", C((0.0, -2.2, 1.6), 1.5, 180, 5), note="S34a the duck")
raw("bev", "L34.1", arms=[90, 0], side=[0, 0], expr="smirk", head=[0, 12], blend=0.15)
S("L34.1", C((0.0, -2.2, 1.7), 1.4, 160, 4, w2=1.25), note="S34b the dentist")
raw("bev", "L34.2", arms=[10, 10], side=[0, 0], expr="grin", head=[0, 0], lean=8, blend=0.15)
S("L34.2", C((0.0, -2.2, 1.7), 1.35, 200, 6, w2=1.2), note="S34c the pickle one again")
scene("L35", bev=dict(pos=(0.0, -2.4, 0), yaw=180, expr="worried"))
num("L35", "bev", 498)
cue("L35", "gray", g=1.0)
S("L35", C((0.0, -2.4, 1.75), 1.5, 180, 4, w2=1.35), note="S35 her number 498, gray up to her shoulders")
num("L36", "bev", 499)
S("L36", C((0.0, -2.4, 1.9), 1.0, 180, 4, w2=0.85), note="S36 the tag: 499")
scene("L37", bev=dict(pos=(0.0, -2.4, 0), yaw=180, expr="worried", head=[0, 16], lean=4))
num("L37", "bev", 499)
S("L37", C((0.0, -2.4, 1.75), 1.4, 180, 5), note="S37 Bev, deflated, out of jokes")
scene("L38", bev=dict(pos=(0.75, -1.1, 0), yaw=180, expr="worried", arms=[72, 72], head=[0, 8]))
num("L38", "bev", 499)
cue("L38", "ball", mode="hold", who="bev", y=0.55, dx=0.0)
S("L38", C((0.75, -0.8, 1.2), 1.5, 180, 8, w2=1.35), note="S38 Bev picking up her ball, sighing")
# ---------------------------------------------------------------------------- the slip (L39 to L42)
raw("bev", "L39", pos=[0.4, 0.9, 0], lean=-28, expr="wide", blend=0.15, arms=[40, 40])
cue("L39+0.1", "ball", mode="roll", dur=3.4, x0=0.3, y0=1.0, x1=0.0, y1=18.2)
S("L39", C((0.4, 1.0, 1.1), 1.9, 180, 8), note="S39a Bev slipping")
put("bev", "L39.1", (0.0, 1.9, 0.23), 180, "wide", lean=-90, blend=0.1, blink=False)
S("L39.1", C((0.0, 0.8, 0.4), 1.7, 180, 55, w2=1.6), note="S39b flat on her back, exactly like me")
scene("L40", me=dict(pos=(-0.5, 1.0, 0), yaw=180, expr="laugh", tremble=5, lean=24, arms=[10, 10]),
      bev=dict(pos=(0.0, 1.9, 0.23), yaw=180, expr="wide", lean=-90, blink=False))
num("L40", "me", 0)
num("L40", "bev", 499)
cue("L40", "lore", on=True)
S("L40", C((-0.85, 1.0, 1.5), 1.75, 180, 2, w2=1.6), hold=True, note="S40 me laughing so hard, bent over; the ball return behind me")
cue("L41", "gray", g=0.0, dur=2.2)
count("bev", "L41", 2.0, 499, 0, 14)
raw("bev", "L41", expr="laugh", blend=0.1, tremble=4)
S("L41", C((0.0, 0.8, 0.4), 1.6, 180, 55), note="S41a her number rolling down 499, 300, 50, 0")
S("L41.2", [[0, [0.35, 7.0, 0.55], [0.0, 18.4, 0.4], 26], [1, [0.2, 10.0, 0.5], [0.0, 18.4, 0.4], 26]],
  note="S41b her ball rolling slowly down the lane; color flooding back into her sleeves")
cue("L42", "pins", dur=0.9)
S("L42", [[0, [0.4, 14.6, 0.9], [0.0, 18.4, 0.3], 24], [1, [0.4, 15.0, 1.0], [0.0, 18.4, 0.3], 24]], note="S42a the pins all falling")
scene("L42.0+0.4", bev=dict(pos=(0.0, 1.9, 0.23), yaw=180, expr="laugh", tremble=4, lean=-90, blink=False),
      me=dict(pos=(-1.1, 0.7, 0), yaw=180, expr="laugh", tremble=5, lean=24))
num("L42.0+0.4", "bev", 0)
num("L42.0+0.4", "me", 0)
S("L42.0+0.4", C((0.0, 0.8, 0.4), 1.7, 180, 55), note="S42b Bev on the floor, joy")
# ---------------------------------------------------------------------------- warm turn and loop
cue("L43", "ball", mode="off")
scene("L43", bev=dict(pos=(0.8, 3.6, 0.23), yaw=180, expr="laugh", tremble=4, lean=-90, blink=False),
      me=dict(pos=(-0.75, 3.6, 0.23), yaw=180, expr="laugh", tremble=4, lean=-90, blink=False))
num("L43", "bev", 0)
num("L43", "me", 0)
S("L43", C((0.0, 1.55, 0.4), 2.9, 180, 58, w2=2.7), note="S43 Bev and me both on our backs on the lane, laughing")
scene("L44", bev=dict(pos=(-0.7, -2.0, 0), yaw=150, expr="grin", arms=[75, 75]), me=dict(pos=(0.7, -2.0, 0), yaw=210,
      expr="smile"))
num("L44", "bev", 0)
num("L44", "me", 0)
cue("L44", "shoes", on=True)
S("L44", C((0.0, -1.7, 1.75), 2.3, 180, 6, w2=2.1), note="S44 Bev handing me bowling shoes on flat palms")
cue("L45", "shoes", on=False)
scene("L45", me=dict(pos=(0.0, -2.0, 0), yaw=180, expr="smile"))
put("me", "L45+0.1", (0.0, -1.9, 0), 180, "smile")
put("me", "L45>", (0.0, 0.6, 0), 180, "smile", blend=0.2)
num("L45", "me", 3)
S("L45", C((0.0, -0.6, 1.5), 2.0, 180, 5, w2=1.7), note="S45 me walking the approach, steady, proud")
scene("L46", me=dict(pos=(0.0, -2.0, 0), yaw=180, expr="smile", head=[0, -4]))
num("L46", "me", 3)
S("L46", C((0.0, -2.0, 1.9), 1.05, 180, 5), note="S46a my number: 3")
scene("L46.1", bev=dict(pos=(*BEV_D, 0), yaw=180, expr="laugh", tremble=3, arms=[8, 8]))
cue("L46.1", "gray", g=GRAY0, dur=0.1)
num("L46.1", "bev", 492)
S("L46.1", C((bh[0], bh[1], 1.85), 1.15, 180, 4, w2=1.05), note="S46b push in on Bev mid-laugh (S01a framing). Loop")

look = {"fog": "#dff4ff", "fog_density": 0.0, "fog_start": 40.0, "sky": "#dff4ff", "sky_strength": 1.0,
        "exposure": 0.0, "flash_safe": True, "style": "closer",
        "polish": {"reveal": ["L24"], "twist": "L23", "quiet": [["L43", "L45"]], "hold": ["S03", "S24", "S40"],
                   "camera": True, "idle": True, "ease": True}}
story = {
    "slug": "ep111-laugh-count",
    "title": "Aunt Bev Hasn't LAUGHED in 492 Days \U0001F602",
    "made_for_kids": False,
    "premise": "In this town a number floats over everyone's head and everyone says it counts the days since you last "
               "laughed. Past 500, your color starts to go. My aunt Bev, the funniest person in our family, laughs all "
               "night at league night, and hers says 492.",
    "twist": "It counts the days since you made somebody else laugh. Bev's last real laugh was from me, 492 days ago, "
             "the day I decided I was too cool for her jokes. A fake laugh doesn't count; what finally gets me is her "
             "slipping on the lane like I always do, and her counter rolls to 0 on a strike.",
    "world": "a bright bowling alley on league night with glossy maple lanes, teal and pink neon, a glyph scoreboard, "
             "a snack bar and a shoe-rental counter",
    "voice": {"voice": "am_adam", "tempo": 1.03, "rate": 1.45},
    "key_color": "#ff5fa2",
    "gap": 0.12,
    "tail": LOOP,
    "min_read": 0.15,
    "fade_in": False,
    "fade_out": False,
    "look": look,
    "grade": {"shadows": [0.0, 0.0, 0.03], "highlights": [0.03, 0.015, -0.02], "saturation": 1.25, "contrast": 1.05,
              "vignette": 0.15, "bloom": 0.3, "grain": 0.008, "red_line": 0.7},
    "cast": cast,
    "lines": lines,
    "shots": shots,
    "acting": acting,
    "cues": cues,
    "asr_forgive": ["hers", "his", "four", "four's", "mine has", "bowl", "sighed", "then", "thousand", "four ninety two", "four ninety eight", "four ninety nine"],
    "set_moves": [],
    "clip_ok": ["rim", "S01", "S29"],
    "music": {"root": 53, "mode": "major", "bpm": 120, "seed": 111,
              "sections": [
                  {"at": 0, "voices": ["bubble", "pulse", "pluck_hi"], "energy": 0.6},
                  {"at": "L11", "voices": ["bubble", "pad", "pluck"], "energy": 0.45},
                  {"at": "L23", "voices": ["drone", "pad"], "energy": 0.4, "mode": "minor"},
                  {"at": "L32", "voices": ["pad", "pulse", "pluck"], "energy": 0.55, "mode": "major"},
                  {"at": "L39", "voices": ["pad", "pulse"], "energy": 0.4},
                  {"at": "L42", "voices": ["bubble", "pluck_hi", "pad", "pulse"], "energy": 0.65},
              ]},
    "sound": {
        "rev": 1, "floor": "wood", "steps_db": -22,
        "ambience": [{"kind": "room", "from": 0, "to": "end", "lufs": -40}],
        "sfx": [
            {"at": "L01.3", "kind": "thud", "db": -14},
            {"at": "L20.1", "kind": "thud", "db": -18},
            {"at": "L39.1", "kind": "thud", "db": -18},
            {"at": "L42", "kind": "hit", "db": -18},
        ],
        "music_drops": [{"from": "L22>", "to": "P01>"}],
    },
}

vt = HERE.parent / "voice-timings.json"
if vt.exists():
    from blocky import timeline
    voice = json.loads(vt.read_text())
    _tl0 = timeline.build({"name": "ep111-laugh-count", "lines": lines, "shots": [{"id": "S0"}], "gap": 0.12,
                           "tail": LOOP, "min_read": 0.15, "cast": cast}, voice)
    AT = timeline.resolver(_tl0["lines"], _tl0["duration"])
    for k in acting:
        acting[k].sort(key=lambda e: AT(e["at"]))
    cues.sort(key=lambda e: AT(e["at"]))
story["rev"] = 1
OUT.write_text(json.dumps(story, indent=1, ensure_ascii=False) + "\n")
print(f"{len(shots)} shots, {len(cues)} cues")
