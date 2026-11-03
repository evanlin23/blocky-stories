"""Writes ../story.json for ep26 "last-skate" / "Skip Ahead" (script.md, writer, revival 2026-11-03).

Run from anywhere: python stories/ep26-last-skate/generator/make_story.py
The words are in lines.json next to this file (made from script.md). Everything else is here: the cast, the shots
and their cameras, the acting, the cues set.py reads (the room's dim, the spotlight's sweeps, the Skater's folds, the
twelve song lights, the clock, the buttons, the ribbons), the score and the sound. Places are set.py's: the rink
floor is x +-7, y +-4.4; the south rail is y -4.15, people lean on it at y -3.75; the snack bar is west on the
concourse, the hire counter east, the booth on the north wall. A character with yaw 0 faces -y; yaw 90 faces +x;
yaw 180 faces +y (north, the floor from the concourse).
"""
import json
import math
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE.parent / "story.json"
lines = json.loads((HERE / "lines.json").read_text())

# the word check: a comma in the spoken text only where Whisper swallowed a word
TEMPO = {"L04": 0.9, "L15": 0.9, "L30": 0.9, "L24": 0.93}
# and a comma in the spoken text only (the captions don't change) where Whisper swallowed the "ed" of a word
SPOKEN = {("L24", 0): "That's where skipped,"}
for ln in lines:
    for k, ch in enumerate(ln.get("chunks", [])):
        if (ln["id"], k) in SPOKEN:
            ch[1] = SPOKEN[(ln["id"], k)]
for ln in lines:
    if ln["id"] in TEMPO:
        ln["tempo"] = TEMPO[ln["id"]]

# ---------------------------------------------------------------------------------------------------- cast
FACE = {"eyes": "round", "brows": True, "ink": "#16100f"}
cast = {
    "me": {"age": "adult", "skin": "#c98e66", "shirt": "#2a8d88", "pattern": "solid", "collar": "#237873",
           "pants": "#33384f", "shoes": "#d8d3c6", "sleeves": "short", "hair": "cap", "hair_c": "#1a1412",
           "hat": "none", "face": dict(FACE)},
    # Gus, my best friend: the old "pop" model re-dressed (brown block hair, orange shirt, navy shorts, a gold crown)
    "gus": {"age": "adult", "skin": "#e4ae88", "shirt": "#e8782a", "pattern": "solid", "collar": "#cf6620",
            "pants": "#26304f", "shoes": "#e8dcc2", "sleeves": "short", "hair": "cap", "hair_c": "#4a2f1d",
            "hat": "none", "width": 1.12, "face": dict(FACE)},
    # the lady from Gus's work: the old "nan" model re-dressed (dark-brown bob, mint cardigan, round glasses, a soda)
    "coworker": {"age": "adult", "skin": "#ecc29c", "shirt": "#8fd0b0", "pattern": "solid", "collar": "#a7dfc3",
                 "pants": "#d6d1e2", "shoes": "#f1efe9", "sleeves": "short", "hair": "long", "hair_c": "#3a2416",
                 "hat": "none", "height": 0.96, "width": 0.92, "extras": ["glasses"], "extra_c": "#2a2224",
                 "face": {"eyes": "lashes", "brows": True, "ink": "#1b1214"}},
    "lenny": {"age": "adult", "skin": "#d49a74", "shirt": "#b0293b", "pattern": "solid", "collar": "#b0293b",
              "pants": "#2c2b33", "shoes": "#222222", "sleeves": "short", "hair": "buzz", "hair_c": "#2a1d17",
              "hat": "none", "extras": ["headphones"], "hp_c": "#26262c", "face": dict(FACE)},
    "c1a": {"age": "adult", "skin": "#e0a67e", "shirt": "#3a5f9a", "pattern": "solid", "pants": "#2e3045",
            "shoes": "#e8dcc2", "sleeves": "short", "hair": "swoop", "hair_c": "#3a2a1c", "hat": "none",
            "face": dict(FACE)},
    "c1b": {"age": "adult", "skin": "#8d5a3f", "shirt": "#d0a43a", "pattern": "solid", "pants": "#4a3b33",
            "shoes": "#e8dcc2", "sleeves": "short", "hair": "long", "hair_c": "#18110e", "hat": "none",
            "face": {"eyes": "lashes", "brows": True, "ink": "#18100e"}},
    "c2a": {"age": "adult", "skin": "#f0c8a4", "shirt": "#5a8a56", "pattern": "stripes", "pattern_c": "#dfe4d2",
            "pants": "#3d4150", "shoes": "#e8dcc2", "sleeves": "short", "hair": "spiky", "hair_c": "#7a4a2a",
            "hat": "none", "face": dict(FACE)},
    "c2b": {"age": "adult", "skin": "#b87850", "shirt": "#7d4f8e", "pattern": "solid", "pants": "#2c3040",
            "shoes": "#e8dcc2", "sleeves": "short", "hair": "bun", "hair_c": "#241812", "hat": "none",
            "face": {"eyes": "round", "brows": True, "ink": "#1c1210", "bags": False}},
    "c3a": {"age": "adult", "skin": "#c68a62", "shirt": "#a8505e", "pattern": "solid", "pants": "#30343f", "shoes": "#e8dcc2",
            "sleeves": "short", "hair": "cap", "hair_c": "#20150f", "hat": "none", "face": dict(FACE)},
    "c3b": {"age": "adult", "skin": "#e8b894", "shirt": "#4a7f9a", "pattern": "solid", "pants": "#3a3a4c", "shoes": "#e8dcc2",
            "sleeves": "short", "hair": "long", "hair_c": "#6a4020", "hat": "none",
            "face": {"eyes": "lashes", "brows": True, "ink": "#18100e"}},
    "s1": {"age": "adult", "skin": "#d9a27a", "shirt": "#6a7f9c", "pattern": "solid", "pants": "#35384a", "shoes": "#e8dcc2",
           "sleeves": "short", "hair": "buzz", "hair_c": "#2a1d17", "hat": "none", "face": dict(FACE)},
    "s2": {"age": "adult", "skin": "#a8704c", "shirt": "#c9a24a", "pattern": "solid", "pants": "#3a3a46", "shoes": "#e8dcc2",
           "sleeves": "short", "hair": "bun", "hair_c": "#1c130f", "hat": "none",
           "face": {"eyes": "lashes", "brows": True, "ink": "#18100e"}},
    "s3": {"age": "adult", "skin": "#f0c8a4", "shirt": "#7a9c6a", "pattern": "stripes", "pattern_c": "#dfe4d2", "pants": "#2f3342",
           "shoes": "#e8dcc2", "sleeves": "short", "hair": "swoop", "hair_c": "#5a3a22", "hat": "none", "face": dict(FACE)},
}


def c(*keys):
    return [list(k) for k in keys]


def still(loc, tgt, lens, roll=0):
    return c([0, loc, tgt, lens, roll])


def move(a, b, lens_a, lens_b=None):
    return c([0, a[0], a[1], lens_a], [1, b[0], b[1], lens_b or lens_a])


def yaw_to(a, b):
    return round(math.degrees(math.atan2(b[0] - a[0], -(b[1] - a[1]))), 1)


def C(loc, tgt, h, roll=0):
    """A still camera: h is the height in metres the frame shows at the target (portrait, sensor height 24 mm)."""
    d = math.dist(loc, tgt)
    return still(loc, tgt, round(24.0 * d / h, 1), roll)


def face(p, yaw, dist=1.5, h=1.0, z=1.5, side=0.0, dz=0.05):
    """A camera in front of a character at p (facing yaw), looking at their face height z."""
    fx, fy = math.sin(math.radians(yaw)), -math.cos(math.radians(yaw))
    rx, ry = -fy, fx
    loc = [round(p[0] + fx * dist + rx * side, 2), round(p[1] + fy * dist + ry * side, 2), z + dz]
    return C(loc, [p[0], p[1], z], h)


# ---------------------------------------------------------------------------------------------------- places
MEST = (-5.0, -6.7)        # my stool
CWST = (-3.8, -6.7)        # the lady's stool
RAILY = -3.75
ME_RAIL = (3.0, RAILY)     # where I lean on the south rail
SK_POST = (4.3, RAILY)     # the Skater one post from me
SK_BESIDE = (3.8, RAILY)   # right beside me
FAR = (-2.5, 3.7)          # the far (north) rail
MID = (0.5, 0.2)           # the middle of the floor
GUS_BOOTH = (1.05, 5.1)
LENNY = (-0.35, 5.25)
FLOOR_SIT = -0.51          # a character sits on the boards with its origin this far down

HIGH = still([-5.8, -7.9, 3.9], [1.0, 0.5, 0.6], 20)
BOOTH_BAR = lambda x, h: C([x, 3.3, 3.9], [x, 4.5, 3.85], h)         # the song lights, close
LEN_FACE = C([-0.35, 2.9, 3.25], [-0.35, 5.2, 3.3], 2.0)
CLOCK = C([-4.3, -5.2, 2.9], [-4.3, -8.95, 3.3], 1.7)
SKATER_LOW = C([6.2, -1.3, 0.9], [3.9, RAILY, 0.9], 2.6)                # the Skater at the rail from the floor

SHOTS = [
    # 01 the rule
    (0, "Lenny close, grin, his flat hand coming down on the skip button, the song lights above him, one bulb cherry", 2,
     move(([-0.7, 2.6, 3.0], [-0.7, 5.2, 2.95]), ([-0.7, 3.1, 3.0], [-0.7, 5.2, 2.95]), 17, 20)),
    ("L02", "the song lights close, the next bulb glowing gold", 2, BOOTH_BAR(0.17, 1.0)),
    ("L02.1", "low on the honey floor, wheels gliding past", 2, C([-2.8, -3.0, 0.2], [1.0, -1.2, 0.15], 1.0)),
    # 02 skip one: the wipeout
    ("L03", "Gus in his paper crown in a hug of friends at the hire counter", 2, C([3.4, -4.6, 1.55], [3.4, -6.4, 1.5], 2.1)),
    ("L03.1", "me alone at the hire counter, skates in front of me", 2, C([5.3, -4.6, 1.55], [5.3, -6.3, 1.45], 2.1)),
    ("L03.2", "the lore shot: the end cubby, the far-too-long cherry skates, the tally on the near heel", 2,
     move(([6.5, -5.3, 1.3], [6.5, -8.05, 1.12]), ([6.5, -6.0, 1.15], [6.5, -8.05, 1.12]), 34, 55)),
    ("L04", "me wobbling onto the floor, arms out", 2, C([-3.0, -3.2, 1.3], [0.6, -3.0, 1.1], 3.6)),
    ("L04.1", "me tipping backward, Gus already tipping beside me, laughing", 2, C([1.6, -0.2, 0.9], [1.7, -2.7, 1.0], 2.8)),
    ("L04.2", "Gus's friends at the rail turning to look", 2, C([-2.8, -1.2, 1.4], [-3.0, RAILY, 1.4], 2.4)),
    ("L05", "me on the boards, worried, looking up toward the booth", 2, C([1.5, 0.0, 0.7], [1.5, -2.6, 0.6], 1.9)),
    ("L05.1", "Lenny's two flat hands over the cherry skip and the cream back buttons", 2, C([-0.35, 2.8, 3.15], [-0.35, 5.2, 3.0], 2.7)),
    ("L06", "the button under his flat hand, the next song light turning cherry", 2, C([-0.6, 3.4, 3.2], [-0.6, 4.6, 3.1], 2.0)),
    ("L06.2", "me on a chrome stool at the snack bar, fries in front of me; the spotlight sweeps the far rail behind", 2,
     C([-6.0, -7.7, 1.55], [-1.0, 2.5, 1.35], 5.2)),
    ("L07", "the snack-bar clock, its minute hand settled further on", 2, CLOCK),
    ("L07.1", "a paper boat of fries on the ledge, a fry drooping", 2, C([-4.9, -5.1, 1.55], [-4.9, -5.98, 1.2], 0.75)),
    ("L07.2", "my face, wide", 2, face((-5.0, -6.7), 180, 1.8, 1.25, 1.5)),
    ("L08", "high wide: the soft pool sliding along the far rail onto the Skater, the song lights in frame", 2, HIGH),
    ("L08.2", "medium on the Skater, face toward the floor, the painted smile", 2, C([-3.0, -0.2, 1.4], [FAR[0], FAR[1], 1.2], 3.0)),
    ("L09", "side view of its left leg: two bends, a hard shadow under each", 2, C([-6.2, 3.6, 0.7], [FAR[0], FAR[1], 0.55], 1.4)),
    ("L09.1", "its right leg beside it, straight and too long", 2, C([-2.0, 0.6, 0.5], [FAR[0], FAR[1], 0.8], 2.0)),
    # 03 skip two: small talk
    ("L10", "the lady from Gus's work sliding onto the next stool", 2, C([-4.4, -4.7, 1.6], [-4.4, -6.7, 1.3], 2.8)),
    ("L10.1", "my face, worried, calling up at the booth", 2, face((-5.0, -6.7), 180, 1.8, 1.25, 1.5)),
    ("L10.2", "Lenny's hand on the skip button, a light turning cherry", 2, C([-0.6, 3.4, 3.2], [-0.6, 4.6, 3.1], 2.0)),
    ("L13", "high wide: the pool on the Skater dead centre, Gus's friends skating round it", 2, HIGH),
    ("L13.2", "close on both legs, each folded twice", 2, C([-1.2, -1.6, 0.5], [MID[0], MID[1], 0.4], 1.3)),
    ("L14", "two cherry song lights, close", 2, BOOTH_BAR(0.34, 1.0)),
    ("L14.1", "from my stool, the Skater's face turned toward me across the floor", 2, C([-4.8, -6.0, 1.5], [MID[0], MID[1], 1.2], 3.4)),
    # 04 skip three: the couples skate
    ("L15", "Lenny at his mic", 2, C([-0.2, 2.8, 3.15], [-0.3, 5.2, 3.1], 2.4)),
    ("L15.1", "the room easing down a little, the waltz in", 2, HIGH),
    ("L16", "Gus's friends gliding past in pairs, each pair joined by a cherry ribbon loop", 2, C([0.5, -6.3, 1.4], [0.5, -2.0, 1.3], 3.0)),
    ("L16.1", "me at the rail, bare wrists, worried", 2, C([3.0, -2.0, 1.55], [3.0, RAILY, 1.45], 1.5)),
    ("L17", "wide along the rail: me, a cream post, then the Skater, body facing me", 2, C([6.4, -1.4, 1.4], [3.6, RAILY, 1.25], 3.4)),
    ("L17.2", "my face, terrified", 2, face(ME_RAIL, 180, 1.5, 1.2, 1.5)),
    ("L18", "close on its right arm folded flat on its stripes", 2, C([2.2, -3.0, 1.2], [4.3, RAILY, 1.0], 1.5)),
    ("L18.2", "its face, the eye highlights the brightest thing, key from below", 2, C([3.2, -3.4, 0.55], [4.3, RAILY, 1.2], 0.95)),
    # 05 skip four: the speech
    ("L19", "Gus in the booth beside Lenny, crown on, at the mic", 2, C([1.05, 2.9, 3.1], [1.05, 5.1, 3.2], 2.0)),
    ("L19.1", "Gus looking out over the booth, right at camera", 2, C([1.05, 3.3, 3.2], [1.05, 5.1, 3.3], 1.4)),
    ("L19.2", "me at the rail, wide, calling up", 2, C([3.0, -2.0, 1.55], [3.0, RAILY, 1.5], 1.6)),
    ("P01", "the drop: the rail in the spotlight, still, the room dim", 2, C([6.0, -2.2, 1.3], [3.0, RAILY, 1.3], 2.8)),
    ("L20", "the pool widens on me, and the Skater is in it at my shoulder", 2, C([6.4, -1.5, 1.3], [3.4, RAILY, 1.2], 3.2)),
    ("L20.2", "my face, terrified, its stripes at the frame edge", 2, C([2.3, -2.7, 1.55], [3.0, RAILY, 1.5], 1.35)),
    ("L21", "side on, the two of us at the rail, its head level with my shoulder", 2, C([3.6, -0.7, 1.2], [3.4, RAILY, 1.1], 3.0)),
    ("L21.2", "close on its folded knees", 2, C([4.6, -2.6, 0.5], [3.9, RAILY, 0.4], 1.1)),
    ("L22", "THE TEST STILL: its arm held out to me, two bends, a hand's width from mine, cherry rim", 1,
     C([3.9, -1.3, 0.85], [3.65, -3.7, 1.3], 3.4)),
    ("P02", "the second drop: hold on the two hands, my hand pulled back to my chest", 2, C([3.4, -2.3, 1.1], [3.4, RAILY, 1.1], 1.3)),
    # 06 the reveal
    ("L23", "my eyes going from the song lights to its joints", 2, face(ME_RAIL, 180, 1.5, 1.2, 1.5)),
    ("L23.1", "the four cherry song lights in a row", 2, BOOTH_BAR(0.85, 2.4)),
    ("L23.2", "the Skater's four folded joints, one quick push-in", 2,
     move(([2.6, -2.2, 1.0], [3.8, RAILY, 1.0]), ([3.0, -2.6, 1.0], [3.8, RAILY, 1.0]), 22, 34)),
    ("L24", "the snack-bar clock, its hands", 2, CLOCK),
    ("L24.1", "the far rail, empty", 2, C([-2.5, 0.0, 1.5], [FAR[0], FAR[1], 1.0], 3.0)),
    ("L24.2", "the middle of the floor, empty", 2, C([-1.5, -3.0, 1.2], [MID[0], MID[1], 0.2], 3.0)),
    ("L24.2+0.33", "the post one away, empty", 2, C([6.2, -2.2, 1.3], [SK_POST[0], SK_POST[1], 1.0], 2.2)),
    ("L24.3", "the Skater's smile, close", 2, C([3.0, -3.0, 1.2], [3.8, RAILY, 1.1], 0.9)),
    ("L25", "its hand a hand's width from my sleeve", 2, C([3.4, -2.4, 1.1], [3.4, RAILY, 1.1], 1.15)),
    ("L25+0.45", "the gap closing a finger", 2, C([3.45, -2.3, 1.1], [3.4, RAILY, 1.1], 1.1)),
    ("L25.1", "my own arm held tight against my side, terrified face above it", 2, C([2.8, -2.5, 1.3], [3.0, RAILY, 1.2], 1.25)),
    ("L25.2", "my face, the spotlight hot on it", 2, face(ME_RAIL, 180, 1.4, 1.1, 1.5)),
    ("L25b", "the Skater's painted smile, close", 2, C([3.0, -3.0, 1.2], [3.8, RAILY, 1.1], 0.9)),
    ("L25b+0.7", "my face in the same framing, terrified", 2, C([2.5, -2.9, 1.4], [3.0, RAILY, 1.5], 0.9)),
    # 07 taking them back
    ("L26", "me at the rail, calling up, worried", 2, face(ME_RAIL, 180, 1.5, 1.3, 1.5)),
    ("L26.1", "Lenny's flat hand coming down on the cream back button", 2, C([-0.1, 3.0, 3.2], [-0.1, 4.65, 2.9], 2.0)),
    ("L26.2", "the first cherry light, close, the rewind swell", 2, BOOTH_BAR(0.17, 1.0)),
    ("L27", "me tipping backward on the floor", 2, C([1.6, -0.2, 0.9], [1.7, -2.7, 1.0], 2.8)),
    ("L27.1", "Gus beside me going down too, laughing, on purpose", 2, C([2.8, -1.0, 1.2], [2.1, -2.7, 1.1], 1.9)),
    ("L27.2", "the two of us sitting on the boards, laughing", 2, C([1.7, -0.1, 0.9], [1.7, -2.7, 0.5], 2.3)),
    ("L28", "the Skater at the rail, its left knee open", 2, SKATER_LOW),
    ("L28.1", "the first light turning cream", 2, BOOTH_BAR(0.17, 1.0)),
    ("L29", "the lady from Gus's work and me at the snack bar, both laughing", 2, C([-4.4, -4.7, 1.6], [-4.4, -6.7, 1.3], 2.8)),
    ("L29.2", "the Skater, both legs straight now, a little taller", 2, SKATER_LOW),
    ("L30", "Gus and me side by side on the floor, a cherry ribbon at our near wrists, wobbling", 2, C([1.5, 2.4, 1.45], [1.45, -0.4, 1.2], 3.4)),
    ("L30.2", "the pair of us almost going down, laughing", 2, C([1.4, 1.2, 1.1], [1.45, -0.4, 1.0], 2.1)),
    ("L31", "its right arm open and straight, the third light turning cream", 2, SKATER_LOW),
    ("L31b", "Lenny's hand on the back button", 2, C([-0.1, 3.0, 3.2], [-0.1, 4.65, 2.9], 2.0)),
    ("L31b.1", "Gus at the booth mic, crown on, the room bright", 2, C([1.05, 2.9, 3.1], [1.05, 5.1, 3.2], 2.0)),
    ("L32", "Gus at the mic, soft, pointing out at the floor", 2, C([1.05, 3.1, 3.15], [1.05, 5.1, 3.25], 1.6)),
    ("L32.1", "Gus's friends at the rail turning to me, grinning", 2, C([-2.8, -1.2, 1.4], [-3.0, RAILY, 1.4], 2.4)),
    ("L32.3", "my face, soft", 2, face(ME_RAIL, 180, 1.5, 1.2, 1.5)),
    ("L33", "its left arm unfolded to straight, the fourth light cream", 2, SKATER_LOW),
    # 08 straight, and the sting
    ("L34", "low wide along the rail: the Skater straight, a head above every guest, smiling down at me", 2,
     C([0.4, -2.9, 0.45], [4.4, RAILY, 1.4], 3.6)),
    ("L34.1", "its face from below, the smile unchanged", 2, C([3.0, -3.3, 0.4], [3.9, RAILY, 2.0], 1.1)),
    ("L35", "the spotlight sliding off it", 2, C([6.2, -1.3, 1.0], [3.9, RAILY, 1.3], 3.4)),
    ("L35.1", "the pool comes back round to an empty post", 2, SKATER_LOW),
    ("L35.2", "the song lights, all cream", 2, C([0.0, 0.5, 3.3], [0.0, 4.5, 3.7], 6.4)),
    ("L36", "a guest at the foot of the booth calling up for a skip", 2, C([0.2, 4.2, 2.7], [-0.6, 3.3, 1.5], 1.9)),
    ("L36.1", "Lenny's hand over the button", 2, C([-0.6, 3.4, 3.2], [-0.6, 4.6, 3.1], 2.0)),
    ("L36.2", "wide across the floor: at the far rail, small and lit, a striped shape with one leg bent twice", 2, HIGH),
    ("L36.3", "my face, worried, turning toward the guy", 2, face(ME_RAIL, 180, 1.5, 1.3, 1.5)),
    ("L38", "me pushing off the rail toward the booth", 2, C([3.0, -5.6, 1.6], [2.8, 0.2, 1.3], 3.8)),
]

shots = []
for i, (at, what, step, cam) in enumerate(SHOTS):
    s = {"id": f"S{i + 1:02d}", "cam": cam, "hand": 0.0 if step == 1 else 0.004, "step": step, "what": what}
    if i:
        s["at"] = at
    shots.append(s)

shots[0]["expo"] = 0.45
for sh in shots:
    if sh["what"].startswith("THE TEST STILL"):
        sh["skboost"] = 0.4
        sh["expo"] = 0.8

# ---------------------------------------------------------------------------------------------------- acting
NEUTRAL = {"arms": [0, 0], "side": [0, 0], "head": [0, 0], "lean": 0, "tremble": 0, "blink": True, "sit": False,
           "skate": False, "wobble": 0, "hidden": False}
acting = {w: [] for w in cast}


def put(who, at, pos, **kw):
    keys = acting[who]
    prev = next((k["pos"] for k in reversed(keys) if "pos" in k), None)
    if prev is not None:
        keys.append({"at": at, "pos": prev})
    keys.append({"at": at, "pos": pos, "blend": 0, **NEUTRAL, "expr": "neutral", **kw})


def walk(who, at, pos, **kw):
    acting[who].append({"at": at, "pos": pos, **kw})


def key(who, at, **kw):
    acting[who].append({"at": at, **kw})


def hide(who, at):
    acting[who].append({"at": at, "hidden": True, "blend": 0})


def seat(who, at, x, **kw):
    put(who, at, [x, -6.7, 0.19], yaw=180, sit=True, arms=[66, 66], **kw)


def floor_sit(who, at, pos, **kw):
    put(who, at, [pos[0], pos[1], FLOOR_SIT], yaw=180, sit=True, arms=[30, 30], **kw)


for w in cast:
    hide(w, 0)

# ---- me
put("me", "L03.1", [5.3, -6.3], yaw=180, skate=True, expr="neutral")
put("me", "L04", [-1.4, -3.5], yaw=90, skate=True, wobble=6, side=[70, 70], expr="worried")
walk("me", "L04.1", [0.9, -3.0], skate=True, wobble=6, side=[70, 70])
put("me", "L04.1", [1.3, -2.7], yaw=180, skate=True, wobble=0, side=[60, 60], expr="wide")
key("me", "L04.1", lean=0)
key("me", "L04.1+0.5", lean=-34, blend=0.5)
floor_sit("me", "L05", [1.5, -2.6], expr="worried", head=[0, -20])
seat("me", "L06.2", MEST[0], expr="wide")
key("me", "L07.2", arms=[66, 66], expr="wide")
key("me", "L10.1", arms=[150, 150], expr="worried", blend=0.4)
key("me", "L10.2", arms=[66, 66], blend=0.2)
seat("me", "L13", MEST[0], expr="worried")
put("me", "L16.1", list(ME_RAIL), yaw=180, skate=True, arms=[25, 25], expr="worried")
key("me", "L17.2", expr="terrified", blend=0.2)
key("me", "L19.2", arms=[150, 150], expr="wide", blend=0.3)
key("me", "L20", arms=[20, 20], expr="terrified", blend=0.2)
key("me", "L22", side=[0, 60], expr="terrified", blend=0.3)
key("me", "P02", side=[0, 20], arms=[20, 80], blend=0.3)
key("me", "L26", arms=[150, 150], side=[0, 0], expr="worried", blend=0.4)
put("me", "L27", [1.3, -2.7], yaw=180, skate=True, side=[60, 60], expr="wide")
key("me", "L27", lean=0)
key("me", "L27+0.6", lean=-34, blend=0.5)
floor_sit("me", "L27.2", [1.45, -2.6], expr="laugh")
hide("me", "L28")
seat("me", "L29", MEST[0], expr="laugh")
put("me", "L30", [1.1, -0.4], yaw=180, skate=True, expr="grin", side=[25, 25], wobble=5)
key("me", "L30.2", lean=-12, wobble=8, expr="laugh", blend=0.4)
hide("me", "L31")
put("me", "L32.1", list(ME_RAIL), yaw=180, skate=True, arms=[25, 25], expr="soft")
put("me", "L34", [2.9, RAILY], yaw=90, skate=True, arms=[25, 25], expr="wide", head=[0, 0])
put("me", "L36.3", list(ME_RAIL), yaw=180, skate=True, arms=[25, 25], expr="worried")
walk("me", "L38", [2.5, -2.0], skate=True)

# ---- Gus
put("gus", "L03", [3.4, -6.3], yaw=180, skate=True, expr="grin", arms=[40, 40])
hide("gus", "L03.1")
put("gus", "L04.1", [2.2, -2.7], yaw=180, skate=True, side=[60, 60], expr="laugh")
key("gus", "L04.1", lean=0)
key("gus", "L04.1+0.4", lean=-30, blend=0.5)
hide("gus", "L05")
put("gus", "L19", list(GUS_BOOTH) + [1.74], yaw=0, expr="soft", arms=[0, 70])
hide("gus", "L26")
put("gus", "L27.1", [2.2, -2.7], yaw=180, skate=True, side=[60, 60], expr="laugh")
key("gus", "L27.1", lean=0)
key("gus", "L27.1+0.4", lean=-30, blend=0.5)
floor_sit("gus", "L27.2", [2.3, -2.6], expr="laugh")
hide("gus", "L28")
put("gus", "L30", [2.0, -0.4], yaw=180, skate=True, expr="grin", side=[25, 25], wobble=6)
key("gus", "L30.2", lean=-12, wobble=8, expr="laugh", blend=0.4)
hide("gus", "L31")
put("gus", "L31b.1", list(GUS_BOOTH) + [1.74], yaw=0, expr="soft", arms=[0, 0])
key("gus", "L32", arms=[0, 90], expr="soft", blend=0.4)
hide("gus", "L32.1")

# ---- the lady from Gus's work
put("coworker", "L10", [-2.3, -5.2], yaw=-90, skate=True, expr="grin")
walk("coworker", "L10+0.5", [-3.7, -5.2], skate=True)
seat("coworker", "L10+0.9", CWST[0], expr="grin")
hide("coworker", "L10.2")
seat("coworker", "L29", CWST[0], expr="laugh")
hide("coworker", "L29.2")

# ---- Lenny at the booth: the skip button is under his left hand (the -x one), the back button under his right
SKIPX, BACKX = -0.9, 0.2
put("lenny", 0, list(LENNY) + [1.74], yaw=0, expr="grin", arms=[30, 0])
key("lenny", "L01.1", arms=[50, 0], blend=0.4)
key("lenny", "L01.2", arms=[66, 0], blend=0.25)
key("lenny", "L02", arms=[0, 0], blend=0.4)
key("lenny", "L05.1", arms=[48, 48], blend=0.4)
key("lenny", "L06", arms=[48, 0], blend=0.3)
key("lenny", "L06.1", arms=[66, 0], blend=0.2)
key("lenny", "L06.2", arms=[0, 0], blend=0.4)
key("lenny", "L10.1", arms=[48, 0], blend=0.3)
key("lenny", "L10.2", arms=[66, 0], blend=0.25)
key("lenny", "L10>", arms=[0, 0], blend=0.4)
key("lenny", "L15", arms=[0, 70], expr="grin", blend=0.5)
key("lenny", "L15.1", arms=[0, 0], blend=0.4)
key("lenny", "L26.1-0.5", arms=[0, 48], expr="neutral", blend=0.3)
key("lenny", "L26.1+0.3", arms=[0, 66], blend=0.25)
key("lenny", "L27", arms=[0, 0], blend=0.4)
key("lenny", "L31b-0.4", arms=[0, 48], blend=0.3)
key("lenny", "L31b", arms=[0, 66], blend=0.25)
key("lenny", "L31b.1", arms=[0, 0], blend=0.4)
key("lenny", "L36", expr="grin", arms=[0, 0])
key("lenny", "L36.1", arms=[48, 0], blend=0.3)

# ---- the guy who asks for a skip
put("s1", "L36", [-0.6, 3.3], yaw=180, skate=True, expr="grin", arms=[150, 150], head=[0, -20])
hide("s1", "L36.2")

# ---- Gus's friends: singles at the rail and the hug, then couples orbiting the floor
A_, B_, CY = 5.0, 2.0, 0.8
OMEGA = 0.4


def ell(theta, off):
    x, y = A_ * math.cos(theta), B_ * math.sin(theta)
    nx, ny = math.cos(theta) * B_, math.sin(theta) * A_
    n = math.hypot(nx, ny)
    return [round(x + off * nx / n, 3), round(y + CY + off * ny / n, 3)]


def orbit(anchor, secs, th0, a, b, off=0.45, step=0.8):
    ref = (lambda dt: f"{anchor}+{dt:.1f}") if isinstance(anchor, str) else (lambda dt: round(anchor + dt, 2))
    for who, o in ((a, -off), (b, off)):
        put(who, anchor, ell(th0, o), yaw=0, skate=True, expr="grin", arms=[18, 18], side=[8, 8])
        n = int(secs / step)
        for k in range(1, n + 1):
            walk(who, ref(k * step), ell(th0 + OMEGA * k * step, o), skate=True, arms=[18, 18], side=[8, 8])
        hide(who, ref(secs + 0.1))


# the hug at the counter (L03), the singles at the rail (L04.2)
put("s1", "L03", [2.3, -6.2], yaw=180, skate=True, expr="grin", arms=[40, 40])
put("s2", "L03", [4.5, -6.2], yaw=180, skate=True, expr="grin", arms=[40, 40])
put("s3", "L03", [3.4, -5.4], yaw=180, skate=True, expr="grin", arms=[40, 40])
put("s1", "L04.2", [-3.4, RAILY], yaw=180, skate=True, expr="wide")
put("s2", "L04.2", [-2.6, RAILY], yaw=180, skate=True, expr="wide")
put("s3", "L04.2", [-4.2, RAILY], yaw=180, skate=True, expr="wide")
hide("s1", "L05")
hide("s2", "L05")
hide("s3", "L05")
put("s1", "L32.1", [-3.4, RAILY], yaw=180, skate=True, expr="grin")
put("s2", "L32.1", [-2.6, RAILY], yaw=180, skate=True, expr="grin")
put("s3", "L32.1", [-4.2, RAILY], yaw=180, skate=True, expr="grin")
hide("s2", "L32.3")
hide("s3", "L32.3")
put("s1", "L34", [1.7, RAILY], yaw=180, skate=True, expr="wide")
hide("s1", "L35")
# the couples (their hug is L03): three pairs skating the floor from the first lap to the end
LAST = 105.0
orbit(0, 5.0, 0.6, "c1a", "c1b")      # the earliest low shot (L02.1) wants wheels: they skate in from the start
orbit(0, 5.0, 2.7, "c2a", "c2b")
orbit(0, 5.0, 4.8, "c3a", "c3b")
orbit("L04", LAST, 0.6, "c1a", "c1b")
orbit("L04", LAST, 2.7, "c2a", "c2b")
orbit("L04", LAST, 4.8, "c3a", "c3b")

# ---------------------------------------------------------------------------------------------------- cues
cues = [{"at": 0, "name": "skates", "who": w, "on": True} for w in cast if w != "lenny"]


def sweep(at, start, mid, end, size=40, gain=0.9):
    """The spotlight slides in from the edge (never pops), crosses, and settles. Cues are sequential."""
    return [
        {"at": at, "name": "spot", "to": list(start), "gain": 0.0, "size": size, "dur": 0.02},
        {"at": f"{at}+0.1" if isinstance(at, str) else at + 0.1, "name": "spot", "to": list(mid), "gain": gain, "dur": 1.8},
        {"at": f"{at}+2.0" if isinstance(at, str) else at + 2.0, "name": "spot", "to": list(end), "dur": 2.2},
    ]


cues += [
    {"at": "L19.3", "name": "dim", "level": 0.3, "dur": 1.5},
    {"at": "L26", "name": "dim", "level": 1.0, "dur": 1.5},
]
cues += sweep("L02", (-7.5, 1.0), (-4.5, 1.0), (-1.0, 0.6), 44, 0.55)
cues += sweep("L06.2", (-7.6, 3.7), (-6.0, 3.7), (FAR[0], FAR[1]), 38, 0.9)
cues += [{"at": "L10>", "name": "spot", "gain": 0.0, "dur": 0.6}]
cues += sweep("L13", (-7.6, 0.2), (-4.0, 0.2), (MID[0], MID[1]), 40, 0.9)
cues += [{"at": "L15", "name": "spot", "gain": 0.0, "dur": 0.6}]
cues += sweep("L16", (7.4, -2.6), (6.0, -2.6), (2.0, 1.4), 44, 0.6)
cues += [{"at": "L16.1", "name": "spot", "to": [3.6, -3.4], "gain": 0.8, "dur": 2.4}]
cues += [{"at": "L19.1", "name": "spot", "to": [ME_RAIL[0] + 0.4, RAILY + 0.2], "dur": 2.0, "size": 44, "gain": 1.0}]
cues += [{"at": "L25", "name": "spot", "to": [ME_RAIL[0] + 0.6, RAILY + 0.2], "dur": 1.5}]
cues += [{"at": "L26.1", "name": "spot", "gain": 0.0, "dur": 0.8}]
cues += sweep("L28", (8.0, -1.0), (6.0, RAILY), (SK_BESIDE[0], RAILY + 0.1), 40, 0.9)
cues += [{"at": "L29.1", "name": "spot", "gain": 0.0, "dur": 0.6}]
cues += sweep("L31", (8.0, -1.0), (6.0, RAILY), (SK_BESIDE[0], RAILY + 0.1), 40, 0.9)
cues += [{"at": "L31b-0.1", "name": "spot", "gain": 0.0, "dur": 0.6}]
cues += sweep("L33", (8.0, -1.0), (6.0, RAILY), (SK_BESIDE[0], RAILY + 0.1), 40, 0.9)
cues += [
    {"at": "L35", "name": "spot", "to": [-1.0, -1.6], "dur": 1.9},
    {"at": "L35.1+0.2", "name": "spot", "to": [SK_BESIDE[0], RAILY + 0.1], "dur": 1.6},
    {"at": "L35.2", "name": "spot", "gain": 0.0, "dur": 1.0},
]
cues += sweep("L36.2", (-7.6, 3.7), (-6.0, 3.7), (FAR[0], FAR[1]), 38, 0.9)

# the Skater: placed where it already stands when a beat starts, never seen moving. fold = [left knee, right knee,
# left elbow, right elbow], 1 = folded (bent twice), 0 = open (straight)


def sk(at, fold, pos, yaw, pose="rest", head=(0, 0), reach_side=-1):
    cues.append({"at": at, "name": "skater", "pos": list(pos), "yaw": yaw, "pose": pose, "fold": list(fold),
                 "head": list(head), "hidden": False, "reach_side": reach_side})


def sk_hide(at):
    cues.append({"at": at, "name": "skater", "hidden": True})


sk("L06.2", [1, 0, 0, 0], FAR, 0, head=(0, 8))                       # skip 1: the far rail
sk_hide("L10.2")
sk("L13", [1, 1, 0, 0], MID, yaw_to(MID, MEST), head=(0, 0))        # skip 2: the middle, face toward me
sk_hide("L15")
sk("L17", [1, 1, 0, 1], SK_POST, -90)                                # skip 3: one post away, facing me
sk_hide("L19.3")
sk("L20", [1, 1, 1, 1], SK_BESIDE, -90)                              # skip 4: right beside me, folded tight
sk("L22", [1, 1, 1, 1], SK_BESIDE, -75, pose="reach", reach_side=-1, head=(-55, 0))  # its left arm held out to me, bent twice
sk_hide("L24.1")
sk("L24.3", [1, 1, 1, 1], SK_BESIDE, -90, pose="reach", reach_side=-1)
sk("L27.2+0.4", [1, 1, 1, 1], SK_BESIDE, -90)
sk("L28", [0, 1, 1, 1], SK_BESIDE, -90)                              # take back the wipeout: the left knee opens
sk("L29.2", [0, 0, 1, 1], SK_BESIDE, -90)                            # the question: the other knee
sk("L31", [0, 0, 1, 0], SK_BESIDE, -90)                              # the couples skate: the right elbow
sk("L33", [0, 0, 0, 0], SK_BESIDE, -90, pose="straight")             # the speech: the last elbow
sk("L34", [0, 0, 0, 0], SK_BESIDE, -90, pose="straight", head=(0, 8))
sk_hide("L35.1")
sk("L36.2", [1, 0, 0, 0], FAR, 0, head=(0, 8))                       # the sting: something folded once

# ribbons: the couples while the waltz plays, Gus and me for the couples skate
cues += [
    {"at": "L15.1", "name": "ribbon", "group": "couples", "on": True},
    {"at": "L19.3", "name": "ribbon", "group": "couples", "on": False},
    {"at": "L30", "name": "ribbon", "group": "gus", "on": True},
    {"at": "L30.2+0.8", "name": "ribbon", "group": "gus", "on": False},
]

# the twelve song lights (the rule meter): cream = played, gold = playing now, cherry = skipped. Bulb 5 starts cherry
# (the loop's guy) and cools to cream; 4 skips light 6, 7, 9, 10 cherry; each take-back turns one cream.


def bulb(at, i, state, dur=0.4):
    cues.append({"at": at, "name": "song", "i": i, "state": state, "dur": dur})


bulb("L02", 5, "cream", 0.6)
bulb("L06.1", 6, "cherry")
bulb("L06.1", 7, "gold", 0.6)
bulb("L10.2", 7, "cherry")
bulb("L10.2", 8, "gold", 0.6)
bulb("L15", 8, "cream", 0.6)
bulb("L15", 9, "gold", 0.6)
bulb("L16.2", 9, "cherry")
bulb("L16.2", 10, "gold", 0.6)
bulb("L19.3", 10, "cherry")
bulb("L19.3", 11, "gold", 0.6)
bulb("L28.1", 6, "cream", 0.6)
bulb("L29.2", 7, "cream", 0.6)
bulb("L31", 9, "cream", 0.6)
bulb("L33", 10, "cream", 0.6)
bulb("L35.2", 11, "cream", 0.6)
bulb("L36.1+0.5", 11, "cherry")

# the clock: minutes since 3:00. Each skip jumps it four minutes; the take-backs wind it home
clock = [("L02", 10), ("L06.1", 14), ("L10.2", 18), ("L16.2", 22), ("L19.3", 26), ("L35.2", 10)]
for at, m in clock:
    cues.append({"at": at, "name": "clock", "min": m, "dur": 0.35})
# the button presses
for at, btn in (("L01.2", "skip"), ("L06.1", "skip"), ("L10.2", "skip"), ("L26.1+0.3", "back"), ("L31b", "back"),
                ("L36.1+0.5", "skip")):
    cues.append({"at": at, "name": "press", "btn": btn})

# ---------------------------------------------------------------------------------------------------- sound
sfx = [
    {"at": "L01.2", "kind": "hit", "db": -8},
    {"at": "L01.2", "kind": "glitch", "db": -25},
    {"at": "L06.1", "kind": "click", "db": -10},
    {"at": "L06.1+0.05", "kind": "glitch", "db": -25},
    {"at": "L10.2", "kind": "glitch", "db": -25},
    {"at": "L16.2", "kind": "glitch", "db": -25},
    {"at": "L19.3", "kind": "glitch", "db": -25},
    {"at": "P01+0.4", "kind": "hit", "db": -6},
    {"at": "P02+0.3", "kind": "hit", "db": -6},
    {"at": "L26.1+0.3", "kind": "click", "db": -12},
    {"at": "L36.2", "kind": "sting", "db": -16},
]

story = {
    "slug": "ep26-last-skate",
    "title": "Ask For A Skip, Get SKIPPED",
    "made_for_kids": False,
    "premise": "At my best friend Gus's birthday skate at a roller rink, I know nobody else. The DJ will skip any song you ask, but he skips you: you land at the start of the next song somewhere else, your fries cold. I skip everything awkward, and each time the spotlight sweeps in, a Skater in faded cherry-and-cream stripes stands nearer, one more of its limbs bent twice like a folding chair.",
    "twist": "Skipped time doesn't vanish. It folds up into the Skater, one fold for every song skipped, and comes after you. When it reaches you, every skipped minute lands in the same second and folds you up like it. The only way out is the back button: I live each skipped song again, one at a time, and every joint straightens.",
    "world": "a bright roller rink on a Saturday afternoon: a honey maple floor, a cherry padded rail with cream posts, cherry-and-cream stripes on every wall, a snack bar with chrome stools and a clock with hands only, a hire counter with a wall of cubbies, and a raised DJ booth with twelve song lights, a cherry skip button and a cream back button",
    "voice": {"voice": "am_adam", "tempo": 1.03, "rate": 1.45},
    "key_color": "#ff5f7e",
    "caption": {"ink": "#0a0809", "stroke_add": 2, "shadow": 0.8},
    "key_stroke": 2,
    "gap": 0.12,
    "tail": 0,
    "fade_in": False,
    "look": {"fog": "#d7e8f2", "fog_density": 0.004, "fog_start": 12.0, "sky": "#8cc6ee", "sky_strength": 1.0,
             "exposure": 0.3, "flash_safe": True, "polish": True},
    "grade": {"shadows": [0.0, 0.0, 0.01], "highlights": [0.02, 0.01, -0.01], "saturation": 1.05, "red_line": 0.78,
              "contrast": 1.04, "vignette": 0.25, "bloom": 0.25, "grain": 0.01},
    "phonemes": {"lap": "lˈæp", "skipped": "skˈɪpt"},
    "cast": cast,
    "lines": lines,
    "shots": shots,
    "acting": acting,
    "cues": cues,
    "fx": [],
    # the fast songs: a bright rink organ in D major; the waltz: F lydian, soft; the drone enters at L13 and thickens at
    # each skip, lifts a step at each take-back and is gone by L34
    "music": {"root": 50, "mode": "major", "bpm": 132, "seed": 26,
              "sections": [
                  {"at": 0, "voices": ["pad", "pulse", "piano"], "energy": 0.55, "mode": "major", "root": 50},
                  {"at": "L13", "voices": ["pad", "pulse", "piano", "drone"], "energy": 0.55, "mode": "major", "root": 50},
                  {"at": "L16", "voices": ["pad", "piano", "drone"], "energy": 0.35, "mode": "lydian", "root": 53},
                  {"at": "L19.3", "voices": ["pad", "drone", "choir"], "energy": 0.5, "mode": "minor", "root": 50},
                  {"at": "L26", "voices": ["pad", "piano", "drone"], "energy": 0.4, "mode": "major", "root": 50},
                  {"at": "L32", "voices": ["pad", "piano"], "energy": 0.35, "mode": "major", "root": 50},
                  {"at": "L34", "voices": ["pad", "pulse", "piano"], "energy": 0.55, "mode": "major", "root": 50},
                  {"at": "L36.1", "voices": ["pad", "drone", "piano"], "energy": 0.4, "mode": "minor", "root": 50},
              ]},
    "sound": {"floor": "wood", "steps_db": -26,
              "ambience": [
                  {"kind": "room", "from": 0, "to": "end", "lufs": -34},
                  {"kind": "hum", "from": 0, "to": "end", "lufs": -42},
              ],
              "sfx": sfx,
              "music_drops": [{"from": "P01-0.1", "to": "L20", "keep": ["hit", "sting"]},
                              {"from": "P02-0.1", "to": "L23", "keep": ["hit"]}]},
}
# the caption chunks are split to 2 or 3 words (lines.json): every "Lxx.k" above means the k-th chunk of the script's
# own phrasing, so it is moved to the first piece of that phrase
import re
STARTS = json.loads((HERE / "chunk_starts.json").read_text())
REF = re.compile(r"^([LP]\w+?)\.(\d+)(>?)(.*)$")


def remap(ref):
    m = REF.match(ref)
    if not m or m.group(1) not in STARTS:
        return ref
    lid, k, tail, rest = m.group(1), int(m.group(2)), m.group(3), m.group(4)
    return f"{lid}.{STARTS[lid][k]}{tail}{rest}"


def walk_refs(o):
    if isinstance(o, dict):
        for k, v in o.items():
            if k in ("at", "from", "to") and isinstance(v, str):
                o[k] = remap(v)
            else:
                walk_refs(v)
    elif isinstance(o, list):
        for v in o:
            walk_refs(v)


for k in ("shots", "acting", "cues", "fx"):
    walk_refs(story[k])
walk_refs(story["music"])
walk_refs(story["sound"])
lines_out = story["lines"] + [{"id": "P03", "pause": 0.25, "chunks": []}] if not any(l["id"] == "P03" for l in story["lines"]) else story["lines"]
story["lines"] = lines_out
# keep any rev already in story.json (the generator drops it) and bump it so the changed story is drawn again
try:
    old = json.loads(OUT.read_text())
    rev = old.get("sound", {}).get("rev", 0)
except Exception:
    rev = 0
story["sound"]["rev"] = rev + 1
OUT.write_text(json.dumps(story, indent=1, ensure_ascii=False) + "\n")
print("wrote", OUT, f"({len(shots)} shots)")
