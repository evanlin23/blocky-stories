"""Writes ../story.json for ep14 "Our building doesn't have a thirteenth floor" (script, brief + amendment 1, 2026-10-31;
rebuilt in this repo 2026-11-02).

Run from anywhere: python stories/floor-thirteen/generator/make_story.py
The words are in lines.json next to this file. Everything else is here: the cast, the shots and their cameras, the
acting, the cues set.py reads (lights, doors, indicator, panel, the Attendant's pose and lit buttons, the finger,
the hour on the balcony, props, the headphones), the score and the sound.

Places (set.py's metres). The lift car: x -1.05 .. 1.05, y -0.95 (the doors) .. 0.95, floor z = 0, facing the doors
is yaw 0 (-y). The floor panel is on the front wall at x = -0.75; "left" as you face the doors is +x. Past the doors
(y < -1.27) one of three places shows: 13's hall, the 12 landing (3.9 m long, our two doors on the end wall at
y = -5.17: mine at x +0.55, his at x -0.55) or the lobby (8.6 m, the street doors at y = -9.9). The balconies are
30 m east: the divider wall at x = 30, mine on the west (x < 30), his pots on the east, the outer rail at y = 0.
"""
import json
import math
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE.parent / "story.json"
lines = json.loads((HERE / "lines.json").read_text())

BX = 30.0
DOOR_W = 1.1
LOOP = 0.3            # the last word ends 0.3 s before the cut back to the DING
HOLDS = {"L08": 0.55, "L27": 0.35, "L34": 0.2, "L50": 0.35, "L58": 0.3, "L66": 0.5, "L71": 0.4, "L78": 0.5,
         "L80": 0.55, "L82": 0.45, "L86": 0.25, "L89": 0.4, "L94": 0.0, "L52": 0.3, "L92": 0.3}
for ln in lines:
    if ln["id"] in HOLDS and "pause" not in ln:
        ln["gap"] = HOLDS[ln["id"]]

# "Mr." is read as "mister" (the word check hears it so); Okafor is oh-KAH-for
SPOKEN = {}
for ln in lines:
    for k, ch in enumerate(ln.get("chunks", [])):
        if (ln["id"], k) in SPOKEN:
            ch[1] = SPOKEN[(ln["id"], k)]

# ------------------------------------------------------------------------------------------------------ cast
cast = {
    "me": {"age": "adult", "skin": "#d7a17a", "shirt": "#6a5c94", "pattern": "solid", "collar": "#6a5c94",
           "pants": "#8f8566", "shoes": "#e0782a", "sleeves": "long", "hair": "swoop", "hair_c": "#141213",
           "hat": "hoodopen", "hat_c": "#6a5c94", "extras": ["headphones"],
           "face": {"eyes": "round", "brows": True, "ink": "#161012"}},
    "okafor": {"age": "adult", "skin": "#5b3a28", "shirt": "#8a9a6b", "pattern": "solid", "collar": "#8a9a6b",
               "pants": "#5a4632", "shoes": "#2a1c14", "sleeves": "long", "hair": "cap", "hair_c": "#1c1716",
               "hat": "none", "extras": ["tie"], "extra_c": "#b8322a",
               "face": {"eyes": "round", "brows": True, "ink": "#161012", "bags": True}},
}


def C(*keys):
    return [list(k) for k in keys]


def still(loc, tgt, lens):
    return C([0, loc, tgt, lens])


def move(a, b, lens_a, lens_b=None):
    return C([0, a[0], a[1], lens_a], [1, b[0], b[1], lens_b or lens_a])


# ----------------------------------------------------------------------------------------------------- cameras
# Inside the car, looking out through the doors from its back (the POV: I'm the camera, so I'm out of frame)
BACK_WIDE = still([0.0, 1.4, 1.45], [0.0, -1.9, 1.5], 22)
BACK_WIDE_B = still([-0.1, 1.05, 1.5], [0.0, -1.9, 1.5], 22)
BACK_WIDE_C = move([0.1, 1.4, 1.4], [0.05, 1.1, 1.42], 22) and C([0, [0.1, 1.4, 1.4], [0.0, -1.9, 1.5], 22],
                                                                [1, [0.05, 1.15, 1.42], [0.0, -1.9, 1.5], 22])
FIRST = still([0.12, 1.1, 1.6], [0.0, -1.9, 1.55], 22)           # over my shoulder, the doors parting
# the panel inserts (the floor panel: x -0.75, buttons z 0.7 .. 1.5; lobby star at z 0.884, close at z 0.81)
PANEL_LOW = still([-0.74, -0.33, 0.95], [-0.745, -0.94, 0.95], 40)
PANEL_TOP = still([-0.74, -0.33, 1.3], [-0.745, -0.94, 1.3], 40)
PANEL_BTN = still([-0.76, 0.0, 1.44], [-0.77, -0.94, 1.47], 34)   # the top button (z 1.49) with the tomato at its face, centred
INDICATOR = still([0.0, 0.0, 2.2], [0.0, -0.94, 2.3], 30)
# faces: from the doors looking back into the car
FACE_ME = still([0.32, -0.86, 1.52], [-0.1, 0.6, 1.5], 24)
FACE_HIM = still([-0.3, -0.86, 1.52], [0.5, 0.55, 1.5], 24)
# the creature close (its panel at z about 2.0): the aim sits low so the panel rides high in the frame
HEAD_CLOSE = still([0.2, 0.35, 1.7], [0.0, -1.7, 1.9], 38)
HEAD_CLOSE_L = still([0.35, 0.4, 1.65], [0.46, -1.7, 1.9], 40)
HEAD_CLOSE_R = still([-0.3, 0.4, 1.65], [-0.46, -1.7, 1.9], 40)
HEAD_CLOSE_B = still([0.2, 0.35, 1.7], [0.0, -1.7, 1.45], 30)   # the bowed head: the panel rides high, the eye above the caption band
HELD = still([0.05, 0.95, 1.1], [0.0, -1.9, 1.8], 18)             # the pass-3 reveal frame, locked off
PUSH = C([0, [0.05, 0.95, 1.1], [0.0, -1.9, 1.8], 18], [1, [0.03, 0.5, 1.25], [0.0, -1.9, 1.85], 22])
EDGE_R = still([0.2, 0.1, 1.25], [0.46, -1.15, 1.25], 30)       # the right leaf's edge against its sleeve
EDGE_L = still([-0.2, 0.1, 1.25], [-0.46, -1.15, 1.25], 30)
LOOM = C([0, [0.0, 0.45, 1.05], [0.0, -1.9, 2.0], 24], [1, [0.0, 0.2, 1.2], [0.0, -1.9, 1.95], 24])
LOOM_CLOSE = C([0, [0.0, 0.35, 1.4], [0.0, -1.9, 1.6], 30], [1, [0.0, 0.1, 1.45], [0.0, -1.9, 1.6], 30])
FACES_FEAR = still([0.3, -0.86, 1.2], [-0.35, 0.15, 1.55], 26)

# ------------------------------------------------------------------------------------------------------ shots
# (at, label, step, camera). step 1 on the scare's cut and the doors, 2 elsewhere
SH = []


def shot(at, label, cam, step=2, hand=0.01, key=None):
    SH.append({"at": at, "label": label, "cam": cam, "step": step, "hand": hand, "key": key})


def lamp(cam, aim, w=1.0, up=0.45, c="#e8e4dc", size=0.7, side=0.0):
    """A face key by the camera: where the (first) camera key is, a little up and to the side, aimed at `aim`."""
    x, y, z = cam[0][1]
    return {"at": [round(x + side, 3), round(y, 3), round(z + up, 3)], "aim": list(aim), "w": round(w * 0.55, 3), "c": c, "size": size}


# 01 going up
shot(0, "first frame: over my shoulder, the doors parting on the DING, 13 above, one cold light in the gap", FIRST, 1, 0.006)
shot("L01", "insert: my finger on the star", PANEL_LOW, 2)
shot("L01.1", "its lit face in the gap: one button on me (a face in frame by 2 s)", HEAD_CLOSE_L, 2)
shot("L02", "insert: the indicator reading 13", INDICATOR, 2)
shot("L03", "my face, worried, hood up, headphones on", FACE_ME, 2)
shot("L04", "wide: it stands just left of the gap, one button on me", BACK_WIDE, 2)
shot("L05", "closer on the black jacket and its brass", still([0.1, 0.55, 1.45], [0.4, -1.7, 1.35], 32), 2)
shot("L06", "close on its head: the 3x3 panel", HEAD_CLOSE_L, 2)
shot("L07", "the panel: one lit, toward me", still([-0.05, 0.3, 1.5], [0.46, -1.7, 1.88], 44), 2)
shot("L07.3", "my face", FACE_ME, 2)
shot("L08", "the doors close by themselves, its light on me through the gap", BACK_WIDE_B, 2)
shot("L08.2", "the indicator going 13 to 12", INDICATOR, 2)
# 02 next door
shot("L09", "the 12 landing from the car: pale walls, two doors on the end wall", still([0.0, 0.5, 1.5], [0.0, -4.5, 1.4], 22), 2)
shot("L10", "we pass at our doors: he looks at his keys, I look at the lift", still([0.0, -1.5, 1.5], [0.0, -4.6, 1.4], 24), 2)
shot("L10.1", "we walk to the lift, nobody nods", still([0.0, -1.5, 1.5], [0.0, -3.4, 1.4], 24), 2)
L11C = still([BX + 0.2, -4.6, 1.6], [BX, 1.2, 1.3], 20)
shot("L11", "blue hour: the two balconies side by side", L11C, 2, key=lamp(L11C, [BX, 0.9, 1.2], 2.0, up=0.1, c="#bcd0ff", size=2.0))
L12C = still([BX + 1.2, -1.5, 1.75], [BX + 1.45, 0.6, 1.3], 30)
shot("L12", "him bent over his pots, his mouth going", L12C, 2, key=lamp(L12C, [BX + 1.45, 0.6, 1.3], 0.9, up=0.1, c="#bcd0ff"))
L13C = still([BX + 1.9, -0.8, 1.7], [BX + 1.7, 0.6, 1.2], 30)
shot("L13", "closer on him talking to a vine", L13C, 2, key=lamp(L13C, [BX + 1.7, 0.6, 1.2], 0.9, up=0.1, c="#bcd0ff"))
L131C = still([BX - 1.0, -1.7, 1.75], [BX - 1.2, 0.8, 1.4], 26)
shot("L13.1", "me on my side, pretending not to hear", L131C, 2, key=lamp(L131C, [BX - 1.2, 0.8, 1.4], 0.9, up=0.1, c="#bcd0ff"))
L14C = still([BX + 1.0, -1.3, 1.5], [BX + 1.0, 0.6, 1.7], 26)
shot("L14", "his open hand toward the sky", L14C, 2, key=lamp(L14C, [BX + 1.0, 0.6, 1.5], 0.9, up=0.1, c="#bcd0ff"))
shot("L15", "Wednesday: the phone on my open palm, on speaker", FACE_ME, 2, key=lamp(FACE_ME, [-0.1, 0.6, 1.5], 0.8, up=0.3))
shot("L16", "the down triangle lit under the 12", INDICATOR, 2)
shot("L17", "the doors open on the lobby, I walk out, still arguing", still([0.0, 0.8, 1.5], [0.0, -6.0, 1.3], 22), 2)
# 03 Thursday and Saturday
shot("L18", "insert: the star pressed again", PANEL_LOW, 2)
shot("L19", "insert: the up triangle", INDICATOR, 2)
shot("P02", "the doors part on 13, the ceiling dims, it stands just right", BACK_WIDE, 1)
shot("L20", "wide: just right of the gap, a step from the sill", BACK_WIDE_B, 2)
shot("L21", "through the gap: the hall runs back", still([0.0, 0.7, 1.55], [0.0, -9.0, 1.45], 26), 2)
shot("L22", "the one cold light far down the hall", still([0.0, 0.4, 1.7], [0.3, -11.0, 1.9], 55), 2)
shot("L23", "hold on the open gap", BACK_WIDE_C, 2, 0.003)
shot("L24", "insert: my finger on the close button, one click", PANEL_LOW, 2)
shot("L25", "close on its panel: the light steps down to the corner", HEAD_CLOSE_R, 2)
shot("L26", "over my hand on the close button, the lit corner soft behind", still([-0.62, -0.1, 1.0], [-0.3, -1.7, 1.55], 34), 2)
shot("L27", "press two", PANEL_LOW, 2)
shot("L27.1", "press three, and the doors start to close", PANEL_LOW, 2)
shot("L28", "from the car: the gap narrowing, its light still on me", BACK_WIDE, 2)
shot("L29", "Saturday: the up triangle", INDICATOR, 2)
shot("P03", "the doors part, the ceiling dims: it stands in front", BACK_WIDE, 1)
shot("L30", "wide: straight in front of the gap", BACK_WIDE_B, 2)
shot("L31", "a low shot, its waist down", still([0.25, 0.9, 0.5], [0.0, -1.7, 0.75], 30), 2)
shot("L32", "the black sleeve running down to the glove", still([0.0, 0.7, 0.95], [0.28, -1.68, 0.95], 38), 2)
shot("L33", "the folded gloves hang from the black sleeves, its jacket above and its knees below", still([0.05, 0.95, 0.85], [0.0, -1.7, 1.0], 30), 2)
shot("L34", "a fast run of presses on close", PANEL_LOW, 2)
shot("L35", "the doors finally close on it", BACK_WIDE, 2)
shot("L36", "wide: me small in the steady car light", still([0.0, -0.88, 1.6], [0.0, 0.9, 1.25], 15), 2)
shot("L37", "my bare balcony, his pots beyond the low wall", still([BX - 2.6, 1.3, 1.5], [BX + 0.3, 0.5, 1.0], 22), 2)
# 04 next Monday
shot("L38", "the 12 landing, both front doors open together", still([0.0, -1.5, 1.45], [0.0, -5.2, 1.3], 22), 2)
shot("L39", "one wall apart", still([0.0, -3.3, 1.25], [0.0, -5.15, 1.45], 26), 2)
L40C = still([0.0, -1.85, 1.5], [0.0, -3.7, 1.4], 15)
shot("L40", "waiting for the lift without a word", L40C, 2, key=lamp(L40C, [0.0, -3.7, 1.4], 0.9, up=0.3))
shot("L41", "he goes to the back", still([-0.5, -0.86, 1.5], [0.55, 0.55, 1.4], 22), 2)
L412 = still([0.3, 0.3, 1.5], [-0.55, -0.45, 1.5], 17)
shot("L41.2", "I stay by the buttons, my face to him", L412, 2, key=lamp(L412, [-0.55, -0.45, 1.5], 0.1, up=0.3, side=0.3))
shot("L42", "insert: the star", PANEL_LOW, 2)
shot("L43", "the up triangle", INDICATOR, 2)
shot("L44", "his face goes stiff", FACE_HIM, 2, key=lamp(FACE_HIM, [0.5, 0.55, 1.5], 0.8, up=0.3))
shot("L45", "his eyes on the indicator: 13", INDICATOR, 2)
L46C = still([0.3, 0.3, 1.5], [-0.62, -0.5, 1.5], 18)
shot("L46", "me looking at him, then away", L46C, 2, key=lamp(L46C, [-0.5, -0.45, 1.5], 0.55, up=0.3, side=0.3))
L47C = still([0.9, -0.86, 1.7], [-0.2, 0.3, 1.3], 15)
shot("L47", "the lift slows: both of us in the car", L47C, 2, key=lamp(L47C, [0.0, 0.1, 1.4], 0.8, up=0.2))
shot("P04", "the doors part, the ceiling dims, it fills the gap", still([0.1, 1.4, 1.45], [0.0, -1.9, 1.5], 22), 1)
shot("L48", "it fills the whole gap", BACK_WIDE, 2)
shot("L49", "its panel, the one light toward him", HEAD_CLOSE, 2)
shot("L50", "the light steps across to me", HEAD_CLOSE, 2, 0.003)
shot("L51", "hold: the doors open and nothing moving", BACK_WIDE_C, 2, 0.003)
# 05 the doors
shot("L52", "me at the panel pressing close", still([0.6, 0.9, 1.45], [-0.3, -0.6, 1.3], 22), 2)
shot("L52.1", "insert: close, one click, the doors don't move", PANEL_LOW, 2)
shot("L53", "insert: the second click", PANEL_LOW, 2)
shot("L54", "wide from the back: I step back, the leaves slide in", still([0.0, 1.4, 1.5], [0.0, -1.8, 1.5], 20), 2, 0.003)
shot("P06", "THE BUMP: the held centre-line frame, locked off: the leaves hit its shoulders", HELD, 1, 0)
shot("L55", "it is in the doorway: a slow push on the held frame", PUSH, 1, 0)
shot("L56", "close on the right leaf's edge against its sleeve", EDGE_R, 1, 0.004)
shot("L56.2", "its head tips down: looming from below", LOOM, 1, 0.004)
shot("L57", "closer: the lit face looms over my shoulder", still([0.12, 0.65, 0.62], [0.0, -1.9, 1.95], 17), 1, 0.004)
shot("L58", "back to the held frame: the leaves bounce off its shoulders", HELD, 1, 0)
shot("L59", "our faces in fear, lit cold from beyond the doors", FACES_FEAR, 1, 0.004,
     key=lamp(FACES_FEAR, [-0.35, 0.15, 1.55], 0.5, up=0.1, c="#bcd0ff", side=0.2))
shot("L60", "the leaves roll back: the held frame", HELD, 1, 0)
shot("L60.1", "the left leaf's edge comes in against its sleeve again", EDGE_L, 1, 0.004)
shot("P07", "THUMP: the face fills the doorway", LOOM_CLOSE, 1, 0.004)
L61C = still([0.0, 1.35, 1.7], [0.0, 0.15, 1.25], 17)
shot("L61", "his hand finds my sleeve", L61C, 2, key=lamp(L61C, [0.0, 0.15, 1.3], 3.5, up=0.2))
shot("L61.2", "my face lit cold from below", still([0.3, -0.86, 1.2], [-0.35, 0.15, 1.55], 26), 2)
# 06 nine lights
shot("L62", "Wednesday: me mid-rant, the phone on my palm", FACE_ME, 2, key=lamp(FACE_ME, [-0.1, 0.6, 1.5], 0.8, up=0.3))
shot("L64", "back on 13: my face, working it out", still([0.3, -0.86, 1.2], [-0.35, 0.2, 1.55], 26), 2)
shot("L65", "over his shoulder, my mouth going, its panel beyond", still([0.45, 1.25, 1.5], [-0.45, -1.4, 1.65], 21), 1)
shot("L66", "insert: the panel with one corner dark", HEAD_CLOSE_B, 2)
shot("L67", "his face, his eyes on the dark button", still([0.0, -0.86, 1.52], [0.58, 0.3, 1.52], 26), 2)
shot("L68", "he asks what", HELD, 1, 0)
shot("L69", "I say anything", still([0.3, -0.86, 1.52], [-0.4, 0.3, 1.52], 26), 2)
shot("L70", "I don't talk to people", HELD, 1, 0)
shot("L71", "insert: five lit and four dark", HEAD_CLOSE_B, 2)
shot("L72", "you talk to your tomatoes: his brows go up", still([-0.1, -0.86, 1.52], [0.55, 0.3, 1.52], 24), 2)
shot("L73", "they listen", HELD, 1, 0)
shot("L74", "he looked at his shoes", still([-0.3, -0.7, 1.45], [0.55, 0.3, 1.2], 26), 2)
shot("L75", "I don't know anyone in this city", still([0.3, -0.86, 1.52], [-0.4, 0.3, 1.52], 26), 2)
shot("L76", "he looked up", still([-0.1, -0.86, 1.52], [0.55, 0.3, 1.52], 24), 2)
shot("L77", "the tomatoes were my wife's", still([-0.2, -0.86, 1.5], [0.5, 0.3, 1.5], 30), 2)
shot("L78", "insert: only the middle lit, on me", HEAD_CLOSE_B, 2)
shot("L79", "come and try one", still([-0.1, -0.86, 1.52], [0.55, 0.3, 1.52], 26), 2)
shot("L80", "the doorway is empty, the doors slide shut", BACK_WIDE, 2, 0.003)
shot("L81", "the indicator going 13 to 12", INDICATOR, 2)
L82C = still([0.0, -0.88, 1.55], [0.0, 0.5, 1.5], 12)
shot("L82", "our two faces in the steady car light", L82C, 2, 0.004, key=lamp(L82C, [0.0, 0.3, 1.5], 0.6, up=0.3))
# 07 up to twenty
L83C = still([0.0, -3.1, 1.5], [0.0, -0.8, 1.5], 24)
shot("L83", "the doors open on daylight: the two of us in the car, lit by it", L83C, 1, key=lamp(L83C, [0.0, -0.4, 1.5], 0.5, up=0.2, c="#fff0d8"))
L84C = still([0.0, -9.5, 1.5], [0.0, -1.5, 1.35], 20)
shot("L84", "we walk out side by side", L84C, 2, key=lamp(L84C, [0.0, -5.0, 1.4], 0.6, up=0.2, c="#fff0d8", size=1.0))
shot("L85", "evening, low sun: a tomato on the wall", still([BX - 1.0, 1.25, 1.3], [BX + 0.0, 0.5, 1.1], 30), 2)
shot("L86", "a second tomato", still([BX - 0.9, 1.2, 1.3], [BX + 0.0, 0.8, 1.12], 34), 2)
L87C = still([BX - 1.1, 1.15, 1.35], [BX + 0.45, 0.6, 1.35], 28)
shot("L87", "his whole head, still talking", L87C, 2, key=lamp(L87C, [BX + 0.45, 0.62, 1.35], 0.9, up=0.2, c="#ffe0b0"))
L88C = still([BX, 1.62, 1.5], [BX, 0.7, 1.4], 10)
shot("L88", "the two-shot: he introduces me to every plant, our faces to the sunset", L88C, 2, key=lamp(L88C, [BX, 0.6, 1.4], 0.9, up=0.2, c="#ffe0b0"))
shot("L89", "the same two-shot, the sun lower", L88C, 2, key=lamp(L88C, [BX, 0.6, 1.4], 0.8, up=0.2, c="#ffd0a0"))
L90C = still([0.0, -0.88, 1.5], [0.0, 0.5, 1.5], 12)
shot("L90", "the next morning, both of us talking", L90C, 2, key=lamp(L90C, [0.0, 0.3, 1.5], 0.6, up=0.3))
L91C = still([0.0, -0.86, 1.5], [0.42, 0.2, 1.35], 15)
shot("L91", "a tomato on his open palm", L91C, 2, key=lamp(L91C, [0.3, 0.3, 1.4], 0.6, up=0.3))
shot("L92", "insert: the tomato meets the top button", PANEL_BTN, 2)
shot("L93", "insert: my finger on the star", PANEL_LOW, 2)
shot("L94", "the indicator runs up to twenty and back down, one shot (no cut inside the count)", INDICATOR, 2)
shot("L94.3", "the two-shot, both still talking", L90C, 2, key=lamp(L90C, [0.0, 0.3, 1.5], 0.6, up=0.3))

shots = []
for k, s in enumerate(SH):
    d = {"id": f"S{k + 1:02d}", "cam": s["cam"], "step": s["step"], "hand": s["hand"]}
    if s.get("key"):
        d["key"] = s["key"]
    if k:
        d["at"] = s["at"]
    shots.append(d)

# ------------------------------------------------------------------------------------------------------ acting
NEUTRAL = {"arms": [0, 0], "side": [0, 0], "head": [0, 0], "lean": 0, "tremble": 0, "blink": True}
acting = {"me": [], "okafor": []}


def put(who, at, pos, **kw):
    keys = acting[who]
    prev = next((k["pos"] for k in reversed(keys) if "pos" in k), None)
    if prev is not None:
        keys.append({"at": at, "pos": prev})
    keys.append({"at": at, "pos": pos, "blend": 0, "hidden": False, **NEUTRAL,
                 "expr": "worried" if who == "me" else "neutral", **kw})


def walk(who, at, pos, **kw):
    acting[who].append({"at": at, "pos": pos, **kw})


def key(who, at, **kw):
    acting[who].append({"at": at, **kw})


def hide(who, at):
    acting[who].append({"at": at, "hidden": True, "blend": 0})


def talk(who, a, b, amount=0.6):
    acting[who].append({"from": a, "to": b, "mouth": [amount, amount], "flap": True})


# The car. Facing the doors is yaw 0. "Left" is +x.
AT_PANEL = [-0.22, -0.1]
ME_BACK = [-0.1, 0.6]
# placed for the held centre-line shot (the pass-3 reveal) and the nine lights
ME_HELD = dict(pos=[-0.58, 0.12], yaw=80, head=[65, 0])
HIM_HELD = dict(pos=[0.60, 0.15], yaw=-80, head=[-60, 0])

# --- section 01: going up (me alone)
put("me", 0, [-0.55, 0.45], yaw=0, head=[0, 4])                       # over my shoulder at the back of the car
hide("me", "L01")
put("me", "L03", ME_BACK, yaw=0, head=[0, 3], expr="worried")
hide("me", "L04")
put("me", "L07.3", ME_BACK, yaw=0, expr="wide")
hide("me", "L08")
hide("okafor", 0)
# --- section 02
put("me", "L10", [0.55, -4.75], yaw=0, expr="neutral", head=[0, 0])
put("okafor", "L10", [-0.55, -4.75], yaw=0, expr="neutral", head=[0, 24])
walk("me", "L10>", [0.38, -2.3], head=[0, 0])
walk("okafor", "L10>", [-0.4, -2.4], head=[0, 24])
put("okafor", "L11", [BX + 1.5, 0.82], yaw=0, lean=8, arms=[4, 4], head=[0, 14], expr="neutral")
talk("okafor", "L12", "L14>")
key("okafor", "L12", lean=10, blend=0.4)
put("me", "L11", [BX - 1.2, 0.95], yaw=-50, head=[-30, 0], expr="neutral")
put("okafor", "L13", [BX + 1.35, 0.82], yaw=-8, lean=8, arms=[2, 2], head=[-20, 16])
put("okafor", "L13.1", [BX + 1.5, 0.82], yaw=0, lean=8, arms=[4, 4], head=[0, 14])
put("me", "L13.1", [BX - 1.2, 0.95], yaw=-30, head=[-25, 4], expr="neutral")
put("okafor", "L14", [BX + 0.96, 0.7], yaw=0, lean=0, arms=[0, 100], head=[0, -25])
hide("me", "L14")
put("me", "L15", ME_BACK, yaw=0, arms=[0, 78], head=[0, 8], expr="angry")   # mid-rant, the phone on my palm
acting["me"].append({"from": "L15", "to": "L17>", "mouth": [0.65, 0.65], "flap": True})
hide("okafor", "L15")
hide("me", "L16")
put("me", "L17", [0.1, 0.0], yaw=180 + 180, arms=[0, 78], expr="angry")
walk("me", "L17>", [0.0, -6.2], arms=[0, 78])
# --- section 03: Thursday and Saturday (me alone)
hide("me", "L18")
hide("me", "L36-0.01")
put("me", "L36", [0.0, 0.5], yaw=0, head=[0, 6], expr="worried")
hide("me", "L37")
# --- section 04: next Monday
put("me", "L38", [0.55, -4.95], yaw=0, expr="neutral")
put("okafor", "L38", [-0.55, -4.95], yaw=0, expr="neutral")
put("me", "L39", [0.55, -4.95], yaw=0, expr="neutral")
put("okafor", "L39", [-0.55, -4.95], yaw=0, expr="neutral")
put("me", "L40", [0.7, -3.7], yaw=180, expr="neutral")
put("okafor", "L40", [-0.7, -3.7], yaw=180, expr="neutral")
put("okafor", "L41", [0.28, 0.55], yaw=0, expr="neutral")
put("me", "L41", [-0.32, -0.15], yaw=0, expr="neutral")
put("me", "L41.2", [-0.32, -0.15], yaw=130, expr="neutral")
put("okafor", "L41.2", [0.28, 0.55], yaw=0, expr="neutral")
hide("me", "L42")
hide("okafor", "L42")
put("okafor", "L44", [0.28, 0.4], yaw=-30, expr="scared", head=[0, 0])
hide("me", "L44")
hide("okafor", "L45")
put("me", "L46", [-0.32, -0.15], yaw=130, head=[0, 0], expr="worried")
key("me", "L46.2", head=[-55, 0], blend=0.4)
put("okafor", "L46", [0.28, 0.55], yaw=0, expr="scared")
put("me", "L47", [-0.32, -0.15], yaw=0, expr="worried")
put("okafor", "L47", [0.28, 0.55], yaw=0, expr="scared")
put("me", "P04", [-0.6, 0.1], yaw=80, head=[65, 0], expr="wide")
put("okafor", "P04", [0.6, 0.1], yaw=-80, head=[-60, 0], expr="scared")
hide("okafor", "L49")
hide("me", "L49")
# --- section 05: the doors
put("me", "L52", AT_PANEL, yaw=0, arms=[75, 0], expr="worried")
hide("okafor", "L52")
hide("me", "L52.1")
put("me", "L54", AT_PANEL, yaw=0, arms=[75, 0], expr="worried")
walk("me", "L54.2+0.2", ME_HELD["pos"], yaw=80, arms=[0, 0], head=[65, 0], keep_yaw=True)
put("okafor", "L54", HIM_HELD["pos"], yaw=-80, expr="scared", head=[-60, 0])
put("me", "P06", ME_HELD["pos"], yaw=ME_HELD["yaw"], head=ME_HELD["head"], expr="terrified")
put("okafor", "P06", HIM_HELD["pos"], yaw=HIM_HELD["yaw"], head=HIM_HELD["head"], expr="scared")
# L57: a closer insert over my shoulder, then back to the held places
put("me", "L57", ME_HELD["pos"], yaw=ME_HELD["yaw"], head=ME_HELD["head"], expr="terrified")
put("okafor", "L57", HIM_HELD["pos"], yaw=HIM_HELD["yaw"], head=HIM_HELD["head"], expr="scared")
for _id in ("L55", "L56", "L56.2"):
    put("me", _id, ME_HELD["pos"], yaw=ME_HELD["yaw"], head=ME_HELD["head"], expr="terrified")
    put("okafor", _id, HIM_HELD["pos"], yaw=HIM_HELD["yaw"], head=HIM_HELD["head"], expr="scared")
put("me", "L58", ME_HELD["pos"], yaw=ME_HELD["yaw"], head=ME_HELD["head"], expr="terrified")
put("okafor", "L58", HIM_HELD["pos"], yaw=HIM_HELD["yaw"], head=HIM_HELD["head"], expr="scared")
put("me", "L59", [-0.35, 0.2], yaw=0, head=[0, -6], expr="terrified")
hide("okafor", "L59")
for _id in ("L60", "L60.1", "P07"):
    put("me", _id, ME_HELD["pos"], yaw=ME_HELD["yaw"], head=ME_HELD["head"], expr="terrified")
    put("okafor", _id, HIM_HELD["pos"], yaw=HIM_HELD["yaw"], head=HIM_HELD["head"], expr="scared")
put("me", "L61", [-0.35, 0.15], yaw=80, head=[0, 0], expr="terrified")
put("okafor", "L61", [0.33, 0.15], yaw=-80, arms=[0, 92], head=[0, 0], expr="scared")
for k in range(6):   # a small tremble in his hand
    key("okafor", f"L61.1+{0.08 * k:.2f}", arms=[0, 92 + (3 if k % 2 else -3)], blend=0.07)
put("me", "L61.2", [-0.35, 0.2], yaw=0, head=[0, -6], expr="terrified")
hide("okafor", "L61.2")
# --- section 06: nine lights
put("me", "L62", ME_BACK, yaw=0, arms=[0, 78], head=[0, 8], expr="angry")
acting["me"].append({"from": "L62", "to": "L63>", "mouth": [0.65, 0.65], "flap": True})
put("me", "L64", [-0.35, 0.2], yaw=0, head=[0, -6], expr="worried")
put("me", "L65", [-0.55, 0.15], yaw=35, head=[0, 0], expr="worried")
put("okafor", "L65", [0.6, 0.6], yaw=-150, head=[0, 0], expr="scared")
acting["me"].append({"from": "L65.1", "to": "L65>", "mouth": [0.7, 0.7], "flap": True})
hide("me", "L66")
hide("okafor", "L66")
put("okafor", "L67", [0.58, 0.3], yaw=0, expr="scared", head=[0, 8])
hide("me", "L67")
put("me", "L68", ME_HELD["pos"], yaw=ME_HELD["yaw"], head=ME_HELD["head"], expr="worried")
put("okafor", "L68", HIM_HELD["pos"], yaw=HIM_HELD["yaw"], head=HIM_HELD["head"], expr="scared")
acting["okafor"].append({"from": "L68.1", "to": "L68>", "mouth": [0.6, 0.6], "flap": True})
put("me", "L69", [-0.4, 0.3], yaw=0, head=[0, 0], expr="worried")
acting["me"].append({"from": "L69.1", "to": "L69>", "mouth": [0.7, 0.7], "flap": True})
hide("okafor", "L69")
put("me", "L70", ME_HELD["pos"], yaw=ME_HELD["yaw"], head=ME_HELD["head"], expr="worried")
put("okafor", "L70", HIM_HELD["pos"], yaw=HIM_HELD["yaw"], head=HIM_HELD["head"], expr="scared")
acting["okafor"].append({"from": "L70.1", "to": "L70>", "mouth": [0.6, 0.6], "flap": True})
hide("me", "L71")
hide("okafor", "L71")
put("okafor", "L72", [0.55, 0.3], yaw=0, expr="scared", head=[0, 0])
key("okafor", "L72.2", expr="wide", blend=0.2)
hide("me", "L72")
put("me", "L73", ME_HELD["pos"], yaw=ME_HELD["yaw"], head=ME_HELD["head"], expr="worried")
put("okafor", "L73", HIM_HELD["pos"], yaw=HIM_HELD["yaw"], head=HIM_HELD["head"], expr="neutral")
acting["okafor"].append({"from": "L73", "to": "L73.0>", "mouth": [0.6, 0.6], "flap": True})
put("okafor", "L74", [0.55, 0.3], yaw=0, expr="neutral", head=[0, 28])
hide("me", "L74")
put("me", "L75", [-0.4, 0.3], yaw=0, head=[0, 0], expr="worried")
acting["me"].append({"from": "L75.1", "to": "L75>", "mouth": [0.7, 0.7], "flap": True})
hide("okafor", "L75")
put("okafor", "L76", [0.55, 0.3], yaw=0, expr="neutral", head=[0, -4])
hide("me", "L76")
put("okafor", "L77", [0.5, 0.3], yaw=0, expr="soft", head=[0, 2])
acting["okafor"].append({"from": "L77.1", "to": "L77>", "mouth": [0.5, 0.5], "flap": True})
hide("okafor", "L78")
put("okafor", "L79", [0.55, 0.3], yaw=0, expr="soft", head=[0, 0])
acting["okafor"].append({"from": "L79.1", "to": "L79>", "mouth": [0.5, 0.5], "flap": True})
hide("okafor", "L80")
put("me", "L82", [-0.26, 0.05], yaw=12, head=[0, 0], expr="soft")
put("okafor", "L82", [0.25, 0.6], yaw=-12, head=[0, 0], expr="soft")
put("okafor", "L83", [0.25, 0.15], yaw=0, expr="soft")
put("me", "L83", [-0.26, -0.4], yaw=0, expr="soft")
# --- section 07: up to twenty
put("me", "L84", [0.7, -4.4], yaw=0, expr="soft")
put("okafor", "L84", [-0.7, -4.4], yaw=0, expr="soft")
walk("me", "L84>+0.1", [0.7, -8.0], expr="soft", keep_yaw=False)
walk("okafor", "L84>+0.1", [-0.7, -8.0], expr="soft")
hide("me", "L85")
hide("okafor", "L85")
put("okafor", "L87", [BX + 0.4, 0.75, -0.8], yaw=-90, expr="soft", head=[0, 0])
key("okafor", "L87", pos=[BX + 0.4, 0.75, -0.8])
walk("okafor", "L87.1", [BX + 0.4, 0.75, 0.0])
acting["okafor"].append({"from": "L87", "to": "L87>", "mouth": [0.6, 0.6], "flap": True})
hide("me", "L87")
put("okafor", "L88", [BX + 0.4, 0.75], yaw=-90, expr="grin", arms=[0, 0], head=[-70, 0])
put("me", "L88", [BX - 0.4, 0.75], yaw=90, expr="grin", arms=[0, 0], side=[0, 0], head=[70, 0])
key("okafor", "L88.1", arms=[0, 30], blend=0.3)
key("okafor", "L88.2", arms=[0, 10], blend=0.4)
acting["okafor"].append({"from": "L88", "to": "L89>", "mouth": [0.55, 0.55], "flap": True})
put("me", "L89", [BX - 0.4, 0.75], yaw=90, expr="grin")
put("okafor", "L89", [BX + 0.4, 0.75], yaw=-90, expr="grin", arms=[0, 10])
put("me", "L90", [-0.26, 0.05], yaw=10, expr="grin", head=[0, 0])
put("okafor", "L90", [0.25, 0.6], yaw=-10, expr="grin", head=[0, 0])
acting["me"].append({"from": "L90", "to": "L90>", "mouth": [0.6, 0.6], "flap": True})
acting["okafor"].append({"from": "L90", "to": "L91>", "mouth": [0.6, 0.6], "flap": True})
put("okafor", "L91", [0.25, 0.6], yaw=-12, expr="grin", arms=[0, 86], head=[0, 0])
key("okafor", "L91.1", arms=[0, 100], blend=0.4)
key("okafor", "L91.2", arms=[0, 74], blend=0.4)
hide("me", "L91")
hide("me", "L92")
hide("okafor", "L92")
put("me", "L94.3", [-0.26, 0.05], yaw=10, expr="grin")
put("okafor", "L94.3", [0.25, 0.6], yaw=-10, expr="grin")
acting["me"].append({"from": "L94.3", "to": "L94>", "mouth": [0.6, 0.6], "flap": True})
acting["okafor"].append({"from": "L94.3", "to": "L94>", "mouth": [0.6, 0.6], "flap": True})

# -------------------------------------------------------------------------------------------------------- cues
cues = []


def cue(at, name, **kw):
    if name in ("lights", "attendant"):
        kw["dur"] = max(kw.get("dur", 0.3), 0.3)   # flash-safe: every light switch ramps over at least 0.3 s
    cues.append({"at": at, "name": name, **kw})


# the lights: thirteen is the dimmed car with 13's cold light; the dim is a ramp (never a cut), the doors too
def thirteen(at, dur=1.0, **kw):
    cue(at, "lights", state="thirteen", cast_dark=True, cast_rim=kw.pop("rim", 0.7), fill=kw.pop("fill", 0.0),
        dur=dur, **kw)


# 01: the first frame already stands in 13's light, the panel at 40% and dimming to 5%
cue(0, "lights", state="thirteen", cast_dark=True, cast_rim=0.7, fill=1.0, ceiling=0.8)
cue("L04", "lights", state="thirteen", cast_dark=True, cast_rim=0.7, fill=1.0, ceiling=0.05, dur=1.2)
cue("L08.1", "lights", state="on", dur=1.0)
cue("L09", "lights", state="land")
cue("L11", "lights", state="balc_blue")
cue("L15", "lights", state="on")
cue("L17", "lights", state="lobby")
cue("L18", "lights", state="on")
cue("P02", "lights", state="thirteen", cast_dark=True, cast_rim=0.7, fill=1.0, dur=1.4)
cue("L28>", "lights", state="on", dur=1.0)
cue("P03", "lights", state="thirteen", cast_dark=True, cast_rim=0.7, fill=1.0, dur=1.4)
cue("L35+0.3", "lights", state="on", dur=1.0)
cue("L37", "lights", state="balc_blue")
cue("L38", "lights", state="land")
cue("L41", "lights", state="on")
cue("P04", "lights", state="thirteen", cast_dark=True, cast_rim=0.7, fill=0.8, dur=1.4)
cue("P06", "lights", state="thirteen", cast_dark=True, cast_rim=0.7, fill=0.0)
cue("L57", "lights", state="thirteen", cast_dark=True, cast_rim=0.8, fill=0.0)
cue("L58", "lights", state="thirteen", cast_dark=True, cast_rim=0.7, fill=0.0)
cue("L59", "lights", state="thirteen", cast_dark=True, cast_rim=0.5, fill=1.1)
cue("L60", "lights", state="thirteen", cast_dark=True, cast_rim=0.7, fill=0.0)
cue("L61", "lights", state="thirteen", cast_dark=True, cast_rim=1.6, fill=0.0)
cue("L61.2", "lights", state="thirteen", cast_dark=True, cast_rim=0.5, fill=1.1)
cue("L62", "lights", state="on")
cue("L64", "lights", state="thirteen", cast_dark=True, cast_rim=0.5, fill=1.1)
cue("L67", "lights", state="thirteen", cast_dark=True, cast_rim=0.5, fill=1.1)
cue("L68", "lights", state="thirteen", cast_dark=True, cast_rim=0.7, fill=0.0)
cue("L69", "lights", state="thirteen", cast_dark=True, cast_rim=0.5, fill=1.1)
cue("L70", "lights", state="thirteen", cast_dark=True, cast_rim=0.7, fill=0.0)
cue("L71", "lights", state="thirteen", cast_dark=True, cast_rim=0.5, fill=0.0)
cue("L72", "lights", state="thirteen", cast_dark=True, cast_rim=0.5, fill=1.1)
cue("L73", "lights", state="thirteen", cast_dark=True, cast_rim=0.7, fill=0.0)
cue("L74", "lights", state="thirteen", cast_dark=True, cast_rim=0.5, fill=1.1)
cue("L80", "lights", state="on", dur=1.5)
cue("L83", "lights", state="lobby")
cue("L85", "lights", state="balc_gold")
cue("L90", "lights", state="on")

# the doors: gap in metres between the leaves (1.1 open). The hall's own doors stay open.
cue(0, "doors", gap=0.14, hall=1.0)
cue(0.04, "doors", gap=DOOR_W, hall=1.0, dur=0.55)
cue("L08.1", "doors", gap=0.0, hall=1.0, dur=1.3)
cue("L09", "doors", gap=DOOR_W, hall=1.0)
cue("L15", "doors", gap=0.0, hall=1.0)
cue("L17", "doors", gap=DOOR_W, hall=1.0)
cue("L18", "doors", gap=0.0, hall=1.0)
cue("P02", "doors", gap=DOOR_W, hall=1.0, dur=0.6)
cue("L27.1+0.25", "doors", gap=0.0, hall=1.0, dur=1.7)
cue("P03", "doors", gap=DOOR_W, hall=1.0, dur=0.6)
cue("L35+0.2", "doors", gap=0.0, hall=1.0, dur=1.4)
cue("L38", "doors", gap=0.0, hall=1.0)
cue("L41", "doors", gap=0.0, hall=1.0)
cue("P04", "doors", gap=DOOR_W, hall=1.0, dur=0.6)
cue("L54.2", "doors", gap=0.8, hall=1.0, dur=1.25)       # the leaves land on its shoulders as the THUMP does
cue("P06", "doors", gap=0.8, hall=1.0, recoil=0.05)
cue("L58.1", "doors", gap=0.8, hall=1.0, recoil=0.06)     # BOUNCED
cue("L60", "doors", gap=DOOR_W, hall=1.0, dur=0.7)         # rolled back
cue("L60.1+0.15", "doors", gap=0.8, hall=1.0, dur=0.75)    # and tried again: lands on the THUMP
cue("P07", "doors", gap=0.8, hall=1.0, recoil=0.05)
cue("L61", "doors", gap=DOOR_W, hall=1.0, dur=0.5)
cue("L62", "doors", gap=0.0, hall=1.0)
cue("L64", "doors", gap=DOOR_W, hall=1.0)
cue("L80", "doors", gap=0.0, hall=1.0, dur=1.5)
cue("L83.1", "doors", gap=DOOR_W, hall=1.0, dur=0.9)
cue("L90", "doors", gap=0.0, hall=1.0)

# the landing's two front doors (open together on Monday)
cue("L38", "land_doors", open=0.0)
cue("L38.3", "land_doors", open=1.0, dur=0.7)
cue("L40", "land_doors", open=1.0)

# the floor indicator
cue(0, "indicator", floor="13", arrow=None)
cue("L01.1", "indicator", floor="12", arrow="up")
cue("L02", "indicator", floor="13", arrow=None)
cue("L08.2", "indicator", floor="12", arrow="down")
cue("L15", "indicator", floor="12", arrow="down")
cue("L18", "indicator", floor="12", arrow="up")
cue("P02", "indicator", floor="13", arrow=None)
cue("L28>", "indicator", floor="12", arrow="down")
cue("L29", "indicator", floor="12", arrow="up")
cue("P03", "indicator", floor="13", arrow=None)
cue("L35+1.6", "indicator", floor="12", arrow="down")
cue("L43", "indicator", floor="12", arrow="up")
cue("L45", "indicator", floor="13", arrow=None)
cue("P04", "indicator", floor="13", arrow=None)
cue("L81", "indicator", floor="12", arrow="down")
cue("L82", "indicator", floor="12", arrow=None)
cue("L83", "indicator", floor="12", arrow=None)
cue("L90", "indicator", floor="12", arrow=None)
cue("L93+0.3", "indicator", floor="12", arrow="up")
# 12, 14 ... 20 and back, never 13; two a second or slower, or jumping across the cuts
for at, fl, ar in (("L94", "12", "up"), ("L94.1", "16", "up"), ("L94.1+0.4", "20", "up"), ("L94.2+0.25", "17", "down"),
                   ("L94.3", "12", None)):
    cue(at, "indicator", floor=fl, arrow=ar)

# the floor panel's lit buttons (0 is the lobby's star; 21 is close)
cue(0, "panel", lit=[])
cue("L01", "panel", lit=[0])
cue("L02", "panel", lit=[])
cue("L18", "panel", lit=[0])
cue("L19", "panel", lit=[0])
cue("P02", "panel", lit=[])
cue("L24", "panel", lit=[21])
cue("L24+0.4", "panel", lit=[])
cue("L27", "panel", lit=[21])
cue("L27+0.4", "panel", lit=[])
cue("L27.1", "panel", lit=[21])
cue("L27.1+0.4", "panel", lit=[])
cue("L34", "panel", lit=[21])
cue("L35", "panel", lit=[])
cue("L42", "panel", lit=[0])
cue("L44", "panel", lit=[0])
cue("L52.1", "panel", lit=[21])
cue("L52.1+0.4", "panel", lit=[])
cue("L53", "panel", lit=[21])
cue("L53+0.4", "panel", lit=[])
cue("L80", "panel", lit=[])
cue("L92.2", "panel", lit=[19])      # lit on BUTTON
cue("L93", "panel", lit=[19, 0])
cue("L94", "panel", lit=[19, 0])

# my finger (presses: press goes 0 to 1 and back)
cue(0, "finger", on=False)
cue("L01", "finger", on=True, button=0, press=0.0)
cue("L01+0.25", "finger", on=True, button=0, press=1.0, dur=0.1)
cue("L01+0.6", "finger", on=True, button=0, press=0.0, dur=0.1)
cue("L01.1", "finger", on=False)
cue("L18", "finger", on=True, button=0, press=0.0)
cue("L18+0.3", "finger", on=True, button=0, press=1.0, dur=0.1)
cue("L19", "finger", on=False)
cue("L24", "finger", on=True, button=21, press=0.0)
cue("L24+0.15", "finger", on=True, button=21, press=1.0, dur=0.1)
cue("L24+0.5", "finger", on=False)
cue("L26", "finger", on=True, button=21, press=0.2)
cue("L27", "finger", on=True, button=21, press=0.0)
cue("L27+0.15", "finger", on=True, button=21, press=1.0, dur=0.1)
cue("L27+0.45", "finger", on=False)
cue("L27.1", "finger", on=True, button=21, press=0.0)
cue("L27.1+0.15", "finger", on=True, button=21, press=1.0, dur=0.1)
cue("L27.1+0.45", "finger", on=False)
cue("L34", "finger", on=True, button=21, press=0.0)
for k in range(9):
    cue(f"L34+{0.07 + 0.2 * k:.2f}", "finger", on=True, button=21, press=1.0, dur=0.06)
    cue(f"L34+{0.17 + 0.2 * k:.2f}", "finger", on=True, button=21, press=0.0, dur=0.06)
cue("L35", "finger", on=False)
cue("L42", "finger", on=True, button=0, press=0.0)
cue("L42+0.25", "finger", on=True, button=0, press=1.0, dur=0.1)
cue("L43", "finger", on=False)
cue("L52.1", "finger", on=True, button=21, press=0.0)
cue("L52.1+0.15", "finger", on=True, button=21, press=1.0, dur=0.1)
cue("L52.1+0.55", "finger", on=False)
cue("L53", "finger", on=True, button=21, press=0.0)
cue("L53+0.15", "finger", on=True, button=21, press=1.0, dur=0.1)
cue("L53+0.6", "finger", on=True, button=21, press=1.0)
cue("L54", "finger", on=False)
cue("L92", "finger", on=True, button=19, press=0.0, tomato=True)
cue("L92.2-0.1", "finger", on=True, button=19, press=1.0, dur=0.1, tomato=True)
cue("L93", "finger", on=True, button=0, press=0.0)
cue("L93+0.25", "finger", on=True, button=0, press=1.0, dur=0.1)
cue("L94", "finger", on=False)

# the Attendant: where it stands (found there when a shot starts, never seen moving), which buttons are lit.
# viewed from the car: left is +x, so its panel's left column (3 6 0 side) faces him at the back left and the
# right column (5 8 2) faces me at the panel. Index 3 = toward him, 4 = the middle, 5 = toward me, 8 = the bottom
# corner nearest the car's panel.
cue(0, "attendant", pose="left", lit=[5], glow=3.0, wash=3.0)
cue("L04", "attendant", pose="left", lit=[5], glow=1.5)
cue("L09", "attendant", hidden=True)
cue("P02", "attendant", pose="right", lit=[5], glow=1.5)
cue("L25.1", "attendant", pose="right", lit=[8], glow=1.5, dur=0.25)
cue("L28", "attendant", pose="right", lit=[5], glow=1.5, dur=0.25)
cue("P03", "attendant", pose="centre", lit=[5], glow=1.5)
cue("L36", "attendant", hidden=True)
cue("P04", "attendant", pose="centre", lit=[5], glow=1.5)
cue("L49", "attendant", pose="centre", lit=[3], glow=1.5, dur=0.2)
cue("L50", "attendant", pose="centre", lit=[4], glow=1.5, dur=0.2)
cue("L50+0.45", "attendant", pose="centre", lit=[5], glow=1.5, dur=0.2)
BUMP = dict(pose="bump", bend=44, head=[-16, 0, 0], glow=0.75, eye=1.9, peak=0.0, key=0.3, wash=0.55)
cue("P06", "attendant", lit="all", **BUMP)
cue("L56.2", "attendant", lit="all", **{**BUMP, "head": [14, 0, 0]})    # its head tips down at us (on the cut)
for at, n in (("L65.2", 8), ("L68>-0.3", 7), ("L69.2", 6), ("L70.2", 5), ("L72.2", 4), ("L73.0>-0.2", 3), ("L75.3", 2),
              ("L77.4", 1), ("L79.2+0.3", 0)):
    cue(at, "attendant", lit=n, dur=0.18, **BUMP)
cue("L80", "attendant", hidden=True)

# balconies: the hour, the tomatoes on the wall, the props, the headphones
cue(0, "sky", hour=None)
cue("L11", "sky", hour="blue")
cue("L15", "sky", hour=None)
cue("L37", "sky", hour="blue")
cue("L38", "sky", hour=None)
cue("L85", "sky", hour="gold")
cue("L90", "sky", hour=None)
cue(0, "tomatoes", n=0)
cue("L85", "tomatoes", n=1)
cue("L86", "tomatoes", n=2)
cue("L87", "tomatoes", n=2)
cue("L89", "tomatoes", n=4)
cue(0, "props", phone=False, tomato=False)
cue("L15", "props", phone=True, tomato=False)
cue("L18", "props", phone=False, tomato=False)
cue("L62", "props", phone=True, tomato=False)
cue("L64", "props", phone=False, tomato=False)
cue("L91", "props", phone=False, tomato=True)
cue("L92", "props", phone=False, tomato=False)
cue(0, "headphones", where="ears")
cue("L65", "headphones", where="neck")

# ---------------------------------------------------------------------------------------------------- sound
sfx = []


def sf(at, kind, db, **kw):
    sfx.append({"at": at, "kind": kind, "db": db, **kw})


for at in ("P01", "P02", "P03", "P04"):
    sf(at, "bell", -15)
sf("P08", "bell", -15)
sf("L08.2", "click", -22)
for at in ("L01+0.25", "L18+0.3", "L24+0.15", "L27+0.15", "L27.1+0.15", "L42+0.25", "L52.1+0.15", "L53+0.15", "L93+0.25"):
    sf(at, "click", -12)
for k in range(9):
    sf(f"L34+{0.07 + 0.2 * k:.2f}", "click", -15)
sf("L92.2", "thud", -22)
sf("L58.1", "thud", -16)
sf("P06", "hit", -6, keep=True)
sf("P06", "thud", -9, keep=True)
sf("L60+0.1", "whoosh", -28, dur=0.5)
sf("L54.2", "whoosh", -26, dur=1.6, keep=True)
sf("P07", "thud", -10)
sf("L58", "whoosh", -28, dur=0.5)
sf("L80", "whoosh", -26, dur=1.2)
sf("L08.1", "whoosh", -26, dur=1.0)
sf("L83.1", "whoosh", -28, dur=0.8)
sf("L28>-1.5", "whoosh", -28, dur=1.0)
sf("L35+0.2", "whoosh", -26, dur=1.2)
sf("L44", "sting", -20)
sf("L85", "creak", -30, dur=0.5)

story = {
    "slug": "ep14-floor-thirteen",
    "title": "Our building doesn't have a thirteenth floor",
    "made_for_kids": False,
    "premise": "A tenant on the twelfth floor of an older apartment tower presses LOBBY and the lift goes up, to a thirteenth floor the building doesn't have, where something in a brass-and-black lift attendant's uniform with a panel of nine lift buttons for a face is stood too close to the doors, a different place each visit.",
    "twist": "The lift only comes to the floor that isn't there when nobody inside is talking, and two silent neighbours count as alone: talking is what darkens its buttons, and the narrator and the man next door, who only ever talked to his tomatoes, ride up to twenty and back chatting without noticing.",
    "world": "an older apartment tower in an unnamed city: a walnut-and-brass lift car, a long umber hall on the floor that isn't there, a beige twelfth-floor landing, a daylight lobby, and two side-by-side concrete balconies with a low wall and a crowd of terracotta pots",
    "voice": {"voice": "am_adam", "tempo": 1.03, "rate": 1.45},
    "key_color": "#ffbf3f",
    "caption": {"ink": "#08090d", "stroke_add": 2, "shadow": 0.8},
    "key_stroke": 2,
    "gap": 0.12,
    "tail": LOOP,
    "look": {"fog": "#0d1015", "fog_density": 0.02, "fog_start": 1.5, "sky": "#0b0d11", "sky_strength": 1.0,
             "exposure": 1.0, "flash_safe": True},
    "grade": {"shadows": [-0.02, 0.0, 0.04], "highlights": [0.0, 0.005, 0.01], "saturation": 0.85, "contrast": 1.1,
              "vignette": 0.42, "bloom": 0.22, "grain": 0.014, "red_line": 0.79},
    "phonemes": {"Okafor": "ˌOkˈɑfɔɹ"},
    "cast": cast,
    "lines": lines,
    "shots": shots,
    "acting": acting,
    "cues": cues,
    "fx": [],
    # G locrian at 76: every DING (the bell is G3) lands on the unstable tonic; the warm turn goes to G dorian at the
    # lobby, and the piano is the first warm voice
    "music": {"root": 43, "mode": "locrian", "bpm": 76, "seed": 14,
              "sections": [
                  {"at": 0, "voices": ["drone", "pad"], "energy": 0.4},
                  {"at": "L08.1", "voices": ["drone", "pad", "pulse"], "energy": 0.4},
                  {"at": "L09", "voices": ["drone", "pad"], "energy": 0.3},
                  {"at": "L15", "voices": ["drone", "pad", "pulse"], "energy": 0.38},
                  {"at": "P02", "voices": ["pad"], "energy": 0.3},
                  {"at": "L28>", "voices": ["drone", "pad", "pulse"], "energy": 0.4},
                  {"at": "P03", "voices": ["pad", "drone"], "energy": 0.45},
                  {"at": "L35+0.2", "voices": ["drone", "pad", "pulse"], "energy": 0.4},
                  {"at": "L38", "voices": ["drone", "pad"], "energy": 0.3},
                  {"at": "L41", "voices": ["drone", "pad", "pulse"], "energy": 0.42},
                  {"at": "L47", "voices": ["drone", "pad"], "energy": 0.4},
                  {"at": "P04", "voices": ["pad", "drone"], "energy": 0.5},
                  {"at": "L52", "voices": ["pad", "drone"], "energy": 0.55},
                  {"at": "P07>", "voices": ["drone", "pad", "choir"], "energy": 0.5},
                  {"at": "L77", "voices": ["pad", "drone"], "energy": 0.3},
                  {"at": "L80", "voices": ["drone", "pad", "pulse"], "energy": 0.32},
                  {"at": "P08", "voices": ["piano", "pad", "drone"], "energy": 0.4, "mode": "dorian", "root": 43},
                  {"at": "L90", "voices": ["piano", "pad", "drone", "pulse"], "energy": 0.5, "mode": "dorian"},
              ]},
    "sound": {"floor": "wood", "steps_db": -22,
              "ambience": [
                  {"kind": "hum", "from": 0, "to": "L09", "lufs": -38},
                  {"kind": "drone", "from": 0, "to": "L08.1", "lufs": -38},
                  {"kind": "room", "from": "L09", "to": "L11", "lufs": -40},
                  {"kind": "wind", "from": "L11", "to": "L15", "lufs": -40},
                  {"kind": "hum", "from": "L15", "to": "L18", "lufs": -38},
                  {"kind": "hum", "from": "L18", "to": "P02", "lufs": -38},
                  {"kind": "drone", "from": "P02", "to": "L28>", "lufs": -38},
                  {"kind": "hum", "from": "L28>", "to": "P03", "lufs": -38},
                  {"kind": "drone", "from": "P03", "to": "L35+0.2", "lufs": -38},
                  {"kind": "wind", "from": "L36", "to": "L38", "lufs": -40},
                  {"kind": "room", "from": "L38", "to": "L41", "lufs": -40},
                  {"kind": "hum", "from": "L41", "to": "P04", "lufs": -38},
                  {"kind": "drone", "from": "P04", "to": "L80", "lufs": -38},
                  {"kind": "hum", "from": "L80", "to": "P08", "lufs": -38},
                  {"kind": "room", "from": "P08", "to": "L85", "lufs": -40},
                  {"kind": "wind", "from": "L85", "to": "L90", "lufs": -40},
                  {"kind": "hum", "from": "L90", "to": "end", "lufs": -38},
              ],
              "sfx": sfx,
              # the one deep hole: from the second click to the hit on the bump
              "music_drops": [{"from": "L53+0.35", "to": "P06", "db": -45.0, "keep": ["hit", "thud", "whoosh"]}]},
}
OUT.write_text(json.dumps(story, indent=1, ensure_ascii=False) + "\n")
print("wrote", OUT, f"({len(shots)} shots)")
