"""Writes ../story.json for ep11 "Never sit in the back row" (round 2b: the grey passenger, script 02b).

Run from anywhere: python stories/back-row/generator/make_story.py
The words are in lines.json next to this file (L01 to L19 are the drawn opening's, unchanged). Everything else, the
cast, shots, acting, cues, effects, score and sound, is here, so chunk references stay consistent. Shot ids are
numbered in order (S01, S02, ...); a shot's tags mark it as an exterior or a rain shot.
"""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE.parent / "story.json"
lines = json.loads((HERE / "lines.json").read_text())

SEAT_Z = -0.02          # root z for someone on a front seat (cushion top 0.49)
BACK_Z = 0.28           # root z on the back bench (platform 0.32, cushion top 0.79)
PASS_Z = 0.15           # the passenger is 1.25x, so its hips sit higher
ARMS_SIT = [38, 38]
ME_BACK = [-0.82, 6.0, BACK_Z]     # my place on the back bench, beside the middle seat
ME_NIGHT = [-1.38, 2.7, SEAT_Z]    # my seat on the strange nights
HEAD = [0.0, 6.0, 2.24]            # the creature's head, seated (its torso is a head too long)
TO_ME = -75                        # its head turned to me

# One voice for everyone (owner, 2026-10-30): voice A reads every line, and speech is reported by the narrator.
# No cast member has a voice of its own.
cast = {
    "me": {"age": "adult", "skin": "#e3ad84", "shirt": "#c8952a", "pattern": "knit", "pattern_c": "#9c6f1a",
           "collar": "#d8443a", "pants": "#2b3346", "shoes": "#1c1c20", "sleeves": "long",
           "hair": "spiky", "hair_c": "#3a2416", "hat": "none",
           "extras": ["backpack"], "extra_c": "#2a2f36",
           "face": {"eyes": "round", "brows": True, "bags": True}},
    "driver": {"age": "adult", "skin": "#b98059", "shirt": "#26324f", "pattern": "stripes", "pattern_c": "#3a4a6c",
               "collar": "#2f3d5e", "pants": "#1f2537", "shoes": "#111114", "sleeves": "short",
               "hair": "buzz", "hair_c": "#1a1512", "hat": "beanie", "hat_c": "#1f2a44",
               "width": 1.15, "face": {"eyes": "classic", "brows": True, "ink": "#120e10"}},
    "woman": {"age": "adult", "skin": "#efc6a2", "shirt": "#2f4d36", "pattern": "knit", "pattern_c": "#243b2a",
              "collar": "#2a4430", "pants": "#2a4430", "shoes": "#2a2220", "sleeves": "long",
              "hair": "bun", "hair_c": "#33302f", "hat": "none",
              "extras": ["scarf"], "extra_c": "#7d8084",
              "face": {"eyes": "round", "brows": True}},
    "rider3": {"age": "adult", "skin": "#8a5636", "shirt": "#7a5636", "pattern": "plaid", "pattern_c": "#c9b08a",
               "collar": "#6a4a2e", "pants": "#3b3a36", "shoes": "#1d1a18", "sleeves": "long",
               "hair": "swoop", "hair_c": "#16110e", "hat": "ballcap", "hat_c": "#5b2c26",
               "face": {"eyes": "round", "brows": True}},
    "rider4": {"age": "adult", "skin": "#f2d0b0", "shirt": "#24304a", "pattern": "stripes", "pattern_c": "#d9dde3",
               "collar": "#24304a", "pants": "#4a4f57", "shoes": "#e6e6e2", "sleeves": "short",
               "hair": "long", "hair_c": "#7a4b2a", "hat": "none",
               "face": {"eyes": "round", "brows": True}},
    "rider5": {"age": "adult", "skin": "#5c3a27", "shirt": "#6e6a63", "pattern": "knit", "pattern_c": "#57534d",
               "collar": None, "pants": "#2e2b28", "shoes": "#3b2a1f", "sleeves": "long",
               "hair": "buzz", "hair_c": "#9b9a96", "hat": "none",
               "extras": ["glasses"], "extra_c": "#1a1a1a",
               "face": {"eyes": "tired", "brows": True}},
    # the creature's disguise: a tall grey coat, collar up, a pale grey blank head with one thin line for a mouth.
    # No black arms or tentacles (note 18, "Uncanny beats tentacles"): it is the same R6 blocks as everyone else, but
    # far too tall and with its own block arms far too long. It never moves on screen and never touches anyone.
    "passenger": {"age": "adult", "skin": "#8c9095", "shirt": "#575b61", "pattern": "solid",
                  "collar": "#4b4f55", "pants": "#4b4f55", "shoes": "#1c1e21", "sleeves": "long",
                  "hair": "none", "hat": "none", "height": 1.25, "width": 0.82,
                  "face": {"eyes": "none", "mouth": "line", "brows": False, "ink": "#3b3e43"}},
}


def sit(at, pos, **kw):
    return {"at": at, "pos": pos, "yaw": kw.pop("yaw", 0), "sit": True, "arms": kw.pop("arms", ARMS_SIT), **kw}


def jump(at, frm, to, **kw):
    """A cut-away move: two keys at the same moment, so nobody walks (or clatters) on film."""
    return [{"at": at, "pos": frm}, {"at": at, "pos": to, **kw}]


# what a "creature" cue can say: pose (set.py POSES, or "seated" for the acting's place), y, loc, legs, head, hand
def cr(at, pose, **kw):
    return {"at": at, "name": "creature", "pose": pose, **kw}


acting = {
    "me": [
        {"at": 0, "pos": [3.85, -7.3, -0.25], "yaw": 160, "expr": "neutral", "sit": False, "arms": [0, 0]},
        {"at": "L03.2", "pos": [3.85, -7.3, -0.25], "yaw": 160},
        {"at": "L03>", "pos": [2.7, -6.0, -0.25]},
        {"at": "L04", "pos": [1.15, -5.9, 0.0], "yaw": -100},
        {"at": "L05", "pos": [1.15, -5.9, 0.0], "yaw": -100},
        {"at": "L05.2", "pos": [0.25, -4.0, 0.0]},
        {"at": "L05>", "pos": [-1.0, -3.0, 0.0], "yaw": 0, "keep_yaw": True},
        sit("L05>+0.25", [-1.38, -3.0, SEAT_Z]),
        {"at": "L08", "head": [0, 0], "look": [0.3, 0]},
        {"at": "L09", "head": [8, -12], "look": [0.2, -0.6], "expr": "worried"},
        {"at": "L12", "head": [55, 0], "look": [-0.8, 0], "expr": "worried"},
        {"at": "L13", "head": [0, 0], "look": [0, 0], "expr": "neutral"},
        # the strange nights: my seat further back
        *jump("L14", [-1.38, -3.0, SEAT_Z], ME_NIGHT, yaw=0),
        {"at": "L17", "head": [0, 0], "look": [0, 0], "expr": "neutral"},
        {"at": "L19", "head": [62, 0], "look": [-0.6, 0], "expr": "worried"},
        # ---- from here on, round 2b's script (ids L20 to L81)
        {"at": "L21", "head": [0, 0], "look": [0, 0], "expr": "neutral"},
        {"at": "L24", "expr": "worried", "head": [0, 4]},
        {"at": "L27", "head": [60, 0], "look": [-0.8, 0], "expr": "worried", "blend": 0.35},   # it said "Two" too
        {"at": "L28", "expr": "scared"},
        # the pour: on my feet in the aisle, holding a strap, then the back row
        {"at": "L29", "pos": ME_NIGHT, "sit": True},
        {"at": "L29", "pos": [0.45, 2.15, 0.0], "yaw": 0, "sit": False, "arms": [0, 168], "expr": "neutral",
         "head": [0, 6], "look": [0, 0.3], "blend": 0.0},
        {"at": "L32.3", "pos": [0.45, 2.15, 0.0], "yaw": 0, "arms": [0, 0], "blend": 0.2},
        {"at": "L32.4", "pos": [0.05, 4.3, 0.0]},
        {"at": "L32.4+0.35", "pos": [-0.5, 5.3, 0.32]},
        {"at": "L32.4+0.45", "pos": [-0.55, 5.35, 0.32], "yaw": 180, "blend": 0.05, "keep_yaw": True},
        sit("L32.4+0.85", ME_BACK, blend=0.35, keep_yaw=True, head=[0, 0]),
        {"at": "L33", "head": [0, -4], "look": [0, 0], "expr": "worried"},
        {"at": "L34", "head": [0, -25], "look": [0, -0.8]},
        {"at": "L35", "head": [0, 0], "look": [0, 0]},
        {"at": "L37", "head": [-12, 0], "look": [0.6, 0], "blend": 0.2},
        {"at": "L37+0.3", "head": [14, 0], "look": [-0.6, 0], "blend": 0.2},
        {"at": "L38", "head": [24, 0], "look": [-1, 0.1], "expr": "wide", "blend": 0.1},
        {"at": "L39", "head": [20, 0], "look": [-1, 0], "expr": "scared"},
        {"at": "L43", "expr": "terrified", "tremble": 1.2},
        # I run to the front, right behind the driver, and turn to face the aisle
        {"at": "L47", "pos": ME_BACK, "sit": True},
        {"at": "L47+0.1", "pos": [-0.55, 5.35, 0.32], "sit": False, "arms": [0, 0], "head": [0, 0], "look": [0, 0],
         "tremble": 0.0, "blend": 0.0},
        {"at": "L47.1", "pos": [-0.15, 4.3, 0.0], "run": True},
        {"at": "L47.3+0.3", "pos": [-0.3, -4.95, 0.0], "run": True},
        {"at": "L48", "pos": [-0.3, -4.95, 0.0], "yaw": 180, "expr": "terrified", "arms": [20, 25], "blend": 0.2},
        {"at": "L49", "tremble": 1.5},
        # I turn to the front for the mirror, so at L60 it is behind me
        {"at": "L58", "yaw": 0, "head": [0, 8], "look": [0, 0.4], "blend": 0.3},
        {"at": "L60", "head": [0, 0], "look": [0.6, 0], "tremble": 2.0, "blend": 0.1},
        {"at": "L67", "expr": "worried", "tremble": 0.0, "look": [0.4, 0]},
        # I go back and sit with it (a jump cut: the walk is seen from the back row)
        *jump("L70", [-0.3, -4.95, 0.0], [-0.15, 2.2, 0.0], yaw=180, expr="worried", arms=[0, 0], head=[0, 0]),
        {"at": "L70.2", "pos": [-0.15, 4.3, 0.0]},
        {"at": "L70.2+0.35", "pos": [-0.5, 5.3, 0.32]},
        {"at": "L70.2+0.45", "pos": [-0.55, 5.35, 0.32], "yaw": 180, "blend": 0.05, "keep_yaw": True},
        sit("L70.2+0.85", ME_BACK, blend=0.35, keep_yaw=True, head=[0, 0], expr="worried"),
        {"at": "L72", "expr": "neutral", "head": [14, 0], "look": [-0.6, 0]},
        {"at": "L73", "head": [0, -10], "look": [0, -0.6]},
        # off at my stop: out on the pavement by the back of the bus, walking away
        {"at": "L74", "pos": ME_BACK, "sit": True},
        {"at": "L74", "pos": [3.7, 3.2, -0.25], "yaw": 0, "sit": False, "arms": [0, 0], "expr": "neutral",
         "head": [-40, 0], "blend": 0.0},
        {"at": "L74>+0.3", "pos": [4.3, -0.4, -0.25]},
        # the next night, at the stop, then on board facing the back row
        *jump("L75", [4.3, -0.4, -0.25], [5.4, -2.9, -0.25], yaw=-90, expr="worried", head=[0, 0]),
        {"at": "L75.1", "pos": [5.4, -2.9, -0.25], "yaw": -90},
        {"at": "L75>+0.4", "pos": [3.0, -5.7, -0.25]},
        *jump("L76", [3.0, -5.7, -0.25], [0.1, 1.0, 0.0], yaw=180, expr="neutral"),
        {"at": "L79.1", "pos": [0.1, 1.0, 0.0], "yaw": 180},
        {"at": "L79.3", "pos": [0.05, 4.3, 0.0]},
        {"at": "L79.4", "pos": [-0.5, 5.3, 0.32]},
        {"at": "L79.4+0.1", "pos": [-0.55, 5.35, 0.32], "yaw": 180, "blend": 0.05, "keep_yaw": True},
        sit("L79.4+0.5", ME_BACK, blend=0.35, keep_yaw=True, head=[0, 0], expr="neutral"),
        {"at": "L81", "head": [10, 0], "look": [-0.4, 0]},
    ],
    "driver": [
        sit(0, [-1.35, -6.25, 0.04], arms=[62, 62], expr="blank", head=[0, 0], look=[0, 0]),
        {"at": "L06.2", "head": [10, -14], "look": [0.6, -1.0], "blend": 0.35},
        {"at": "L07", "blink": False}, {"at": "L08", "blink": True},
        {"at": "L08", "head": [0, 0], "look": [0, 0]},
        {"at": "L25.1", "head": [30, -24], "look": [0.6, -0.9], "blend": 0.35},
        {"at": "L26", "blink": False}, {"at": "L27", "blink": True},     # eyes fixed on the mirror on "Two"
        {"at": "L27", "head": [0, 0], "look": [0, 0]},
        {"at": "L35.2", "head": [10, -14], "look": [0.6, -1.0], "blend": 0.35},
        {"at": "L36", "blink": False}, {"at": "L37", "blink": True},
        {"at": "L37", "head": [0, 0], "look": [0, 0]},
        {"at": "L58", "blink": False}, {"at": "L60", "blink": True},    # he doesn't even look
        {"at": "L80", "head": [30, -24], "look": [0.6, -0.9], "blend": 0.3},
    ],
    "woman": [
        sit(0, [1.38, -3.0, SEAT_Z], expr="neutral", head=[0, 0], lean=0),
        {"at": "L12", "head": [-50, 4], "lean": 8, "look": [0.9, 0.1], "expr": "worried", "blend": 0.3},
        {"at": "L13", "head": [0, 6], "lean": 0, "look": [0, 0.3], "expr": "neutral"},
        {"at": "L24", "hidden": True},
        {"at": "L29", "hidden": False, "expr": "neutral", "head": [0, 0], "look": [0, 0]},
        {"at": "L33.2", "expr": "squeeze", "head": [0, 10]},
        {"at": "L75", "expr": "neutral", "head": [0, 22], "look": [0, 1]},
        {"at": "L78", "expr": "neutral", "head": [-20, 14], "look": [0.6, 0.8]},
    ],
    # the others ride with their eyes screwed shut through all of it
    "rider3": [sit(0, [-1.42, 0.45, SEAT_Z], expr="shut", head=[-14, 16], arms=[30, 30]),
               {"at": "L24", "hidden": True}, {"at": "L29", "hidden": False},
               {"at": "L48", "expr": "squeeze"}, {"at": "L75", "expr": "shut"}],
    "rider4": [
        sit(0, [1.38, 0.45, SEAT_Z], expr="neutral", head=[0, 22], look=[0, 1], arms=[72, 35]),
        # the long-haired guy's night: up the aisle to the back, stops, turns, and stands by the middle door
        {"at": "L17", "pos": [1.38, 0.45, SEAT_Z]},
        {"at": "L17", "pos": [0.0, -1.6, 0.0], "sit": False, "arms": [0, 0], "head": [0, 0], "look": [0, 0], "blend": 0.0},
        {"at": "L17>", "pos": [0.0, 4.15, 0.0]},
        {"at": "L18", "pos": [0.0, 4.15, 0.0], "yaw": 180, "blend": 0.1},
        {"at": "L18.1", "pos": [0.0, 4.15, 0.0], "yaw": 0, "expr": "worried", "blend": 0.12},
        *jump("L18.2", [0.0, 4.15, 0.0], [1.74, 1.62, 0.0], yaw=-90),
        {"at": "L20", "head": [-50, 0], "look": [0, 0], "expr": "scared"},
        *jump("L21", [1.74, 1.62, 0.0], [1.38, 0.45, SEAT_Z]),
        sit("L21", [1.38, 0.45, SEAT_Z], expr="neutral", head=[0, 22], look=[0, 1], arms=[72, 35]),
        {"at": "L24", "hidden": True}, {"at": "L29", "hidden": False},
        {"at": "L48", "expr": "squeeze"}, {"at": "L75", "expr": "neutral"},
    ],
    "rider5": [sit(0, [1.38, 2.75, SEAT_Z], expr="neutral", head=[-6, 6], look=[-0.3, 0.3], arms=[34, 34]),
               {"at": "L24", "hidden": True}, {"at": "L29", "hidden": False},
               {"at": "L48", "expr": "squeeze"}, {"at": "L75", "expr": "neutral"}],
    "passenger": [
        sit(0, [0.0, 6.0, PASS_Z], arms=[30, 30], expr="blank", hidden=True, head=[0, 0], lean=0),
        {"at": "L38", "hidden": False},
        # back on the seat in the dark at L71, a little closer to me
        *jump("L71.1+0.3", [0.0, 6.0, PASS_Z], [-0.12, 6.0, PASS_Z]),
        # the seam opens in the dark (L62), stays open, and moves as it asks (L66); it shuts in the next dark
        {"from": "L62.1+0.25", "to": "L62.1+1.05", "mouth": [0.0, 3.0]},
        {"from": "L62.1+1.05", "to": "L66.1", "mouth": [3.0, 3.0]},
        {"from": "L66.1", "to": "L66.1>", "mouth": [3.0, 2.2]},
        {"from": "L66.1>", "to": "L66.2>", "mouth": [2.2, 3.2]},
        {"from": "L66.2>", "to": "L71.1+0.3", "mouth": [3.2, 3.2]},
    ],
}

# shots: (at, cam keys, options). cam keys: [u, [x, y, z], [tx, ty, tz], lens]
LOOP_CAM = ([0.0, -3.6, 0.42], [0.0, 6.0, 1.05], 24)   # S01's first frame, and the last shot's last
EYE = (list((-0.5, -5.78, 1.78)), list((-0.78, -7.27, 2.1)))   # the camera that sees the driver's eyes in his mirror
POV = [-0.3, -4.5, 1.62]                                  # just in front of my eyes at the front pole


def c(*keys):
    return [list(k) for k in keys]


SH = [
    # ---- 01 the rule. S01 (r1 M6): the push ends close enough to see the dent; the last shot ends on its first frame
    (0, c([0, LOOP_CAM[0], LOOP_CAM[1], LOOP_CAM[2]], [1, [0.0, 0.2, 1.38], [0.0, 5.95, 0.78], 30]), {"hand": 0.01}),
    ("L02", c([0, [0.9, 3.0, 1.05], [-0.1, 6.3, 1.1], 30], [1, [0.7, 3.5, 1.0], [-0.1, 6.3, 1.15], 33]), {}),
    ("L03", c([0, [2.85, -13.2, 0.55], [2.6, -3.0, 1.45], 26], [1, [2.9, -12.8, 0.6], [2.9, -4.0, 1.4], 28]), {"tags": ["ext"]}),
    ("L04", c([0, [1.95, -5.35, 1.78], [-1.35, -6.3, 1.35], 30], [1, [1.8, -5.45, 1.75], [-1.35, -6.3, 1.4], 36]), {}),
    ("L05", c([0, [-0.45, -7.3, 1.45], [-1.35, -6.25, 1.55], 24], [1, [-0.5, -7.28, 1.46], [-1.35, -6.25, 1.57], 28]), {}),
    ("L06.2", c([0, [-1.05, -5.7, 1.95], [0.35, -7.12, 2.3], 42], [1, [-0.95, -5.8, 1.97], [0.35, -7.12, 2.3], 50]), {}),
    ("L07", c([0, [-0.75, -7.32, 1.12], [-1.35, -6.25, 1.62], 24]), {"hand": 0.006, "step": 1}),
    # S08 (r2 F1): one eased sweep from the front-left riders to the back-right, on ones (no whip back and forth)
    ("L08.1", c([0, [-0.55, -3.3, 1.5], [-1.4, 0.6, 1.0], 24], [1, [-0.55, -3.3, 1.5], [1.35, 2.9, 1.0], 24]), {"step": 1}),
    ("L09", c([0, [-0.55, -4.45, 1.35], [-1.38, -3.0, 1.45], 34], [1, [-0.6, -4.35, 1.35], [-1.38, -3.0, 1.45], 38]), {}),
    ("L10", c([0, [0.35, 0.6, 1.55], [0.0, 6.0, 1.15], 28], [1, [0.3, 1.4, 1.5], [0.0, 6.0, 1.15], 30]), {}),
    ("L11", c([0, [0.2, 3.6, 1.2], [0.7, 5.7, 2.6], 22], [1, [0.15, 3.9, 1.2], [0.6, 5.8, 2.6], 22]), {"step": 1}),
    ("L12", c([0, [-0.55, -3.8, 1.5], [1.38, -2.95, 1.55], 30], [1, [-0.5, -3.72, 1.5], [1.38, -2.95, 1.58], 34]), {}),
    # S13 (r1 M10): her in her seat by the middle door, the back row dark behind her
    ("L13.3", c([0, [0.3, -4.75, 1.42], [1.2, 1.2, 1.12], 24], [1, [0.32, -4.55, 1.42], [1.2, 1.2, 1.12], 25]), {}),
    # ---- 02 strange nights
    ("L14", c([0, [-0.7, 3.35, 1.6], [0.0, 6.0, 0.85], 30], [1, [-0.62, 3.6, 1.55], [0.0, 6.0, 0.82], 32]), {}),
    ("L14.3", c([0, [0.42, 5.2, 1.0], [0.0, 5.95, 0.74], 38], [1, [0.36, 5.32, 0.97], [0.0, 5.95, 0.74], 44]), {}),
    ("L16", c([0, [0.0, 3.55, 1.45], [0.0, 5.6, 1.7], 28], [1, [0.0, 3.75, 1.45], [0.0, 5.6, 1.72], 30]), {}),
    ("L17", c([0, [0.0, -4.8, 1.7], [0.0, 3.0, 1.15], 28], [1, [0.0, -4.4, 1.7], [0.0, 3.0, 1.15], 30]), {}),
    ("L18.2", c([0, [-0.6, 0.1, 1.5], [1.65, 1.6, 1.45], 34], [1, [-0.55, 0.25, 1.5], [1.65, 1.6, 1.45], 38]), {}),
    ("L19", c([0, [1.5, 1.05, 1.8], [-1.3, 2.7, 1.3], 32]), {}),
    # ---- from here on, round 2b's script (ids L20 to L81)
    ("L20", c([0, [0.95, 2.35, 1.6], [1.74, 1.62, 1.58], 36]), {"step": 1, "hand": 0.004}),
    ("L21", c([0, [0.0, 2.5, 1.55], [0.0, 6.6, 1.6], 28], [1, [0.0, 2.9, 1.55], [0.0, 6.6, 1.62], 30]), {}),
    ("L22", c([0, [0.45, 5.3, 1.9], [0.28, 6.6, 1.86], 38], [1, [0.4, 5.7, 1.88], [0.28, 6.6, 1.86], 46]), {}),
    ("L22.3", c([0, [0.2, 5.75, 1.0], [0.28, 6.62, 1.86], 26], [1, [0.2, 5.8, 1.02], [0.28, 6.62, 1.88], 28]), {"hand": 0.006}),
    # the square print, straight on: the angle the L67 match cut comes back to
    ("L23", c([0, [0.3, 5.3, 1.86], [0.28, 6.62, 1.86], 28], [1, [0.3, 5.4, 1.86], [0.28, 6.62, 1.86], 30]), {}),
    ("L24", c([0, [1.2, 5.9, 2.35], [-1.0, -1.0, 0.9], 24], [1, [1.15, 5.8, 2.3], [-1.0, -1.0, 0.95], 26]), {}),
    ("L25", c([0, EYE[0], EYE[1], 44], [1, EYE[0], EYE[1], 52]), {"hand": 0.004}),
    ("L26", c([0, [-0.75, -7.32, 1.12], [-1.35, -6.25, 1.62], 26]), {"hand": 0.006, "step": 1}),
    # "Two" said back from the back row (r1 M7): the dim back row from my seat, the dent, the strap swinging
    ("L27", c([0, [-0.8, 2.9, 1.45], [0.0, 6.0, 1.3], 26], [1, [-0.75, 3.2, 1.45], [0.0, 6.0, 1.3], 28]), {}),
    ("L28", c([0, [0.0, 4.4, 1.35], [0.0, 6.0, 0.85], 30], [1, [0.0, 4.7, 1.3], [0.0, 6.0, 0.85], 34]), {}),
    ("L28.2", c([0, [-0.62, 1.85, 1.35], [-1.38, 2.7, 1.45], 34], [1, [-0.66, 1.95, 1.35], [-1.38, 2.7, 1.45], 38]), {}),
    # ---- 03 the rain, the break
    ("L29", c([0, [7.0, -10.0, 0.6], [0.0, -2.0, 1.4], 24], [1, [7.0, -9.0, 0.7], [0.0, -1.5, 1.4], 24]), {"tags": ["ext", "rain"]}),
    ("L30", c([0, [-0.2, -2.6, 1.15], [-1.25, -1.9, 0.6], 34], [1, [-0.25, -2.5, 1.0], [-1.25, -1.9, 0.55], 40]), {"step": 1}),
    ("L31", c([0, [-0.3, 1.0, 0.9], [0.0, 6.2, 0.9], 28], [1, [-0.3, 1.9, 0.95], [0.0, 6.2, 0.88], 30]), {}),
    ("L32", c([0, [0.8, 1.1, 1.62], [0.45, 2.15, 1.5], 38], [1, [0.76, 1.2, 1.6], [0.45, 2.15, 1.52], 42]), {}),
    ("L32.3", c([0, [0.55, 1.5, 0.55], [-0.1, 5.0, 1.15], 22], [1, [0.5, 1.9, 0.55], [-0.5, 6.0, 1.1], 24]), {"step": 1}),
    ("L33", c([0, [0.15, -3.95, 1.4], [1.38, -3.0, 1.55], 36], [1, [0.2, -3.85, 1.4], [1.38, -3.0, 1.55], 42]), {}),
    ("L34", c([0, [-0.4, 4.6, 1.15], [-0.55, 5.9, 2.65], 20], [1, [-0.4, 4.6, 1.1], [-0.55, 5.9, 2.65], 20]), {"hand": 0.006, "step": 1}),
    # ---- 04 six
    ("L35", c([0, [-1.05, -5.7, 1.95], [0.35, -7.12, 2.3], 46], [1, [-0.95, -5.8, 1.97], [0.35, -7.12, 2.3], 54]), {}),
    ("L36", c([0, [-0.72, -7.1, 1.25], [-1.35, -6.25, 1.6], 40]), {"hand": 0.004, "step": 1}),
    ("L37", c([0, [-0.85, 4.95, 1.55], [-0.82, 6.0, 1.82], 34], [1, [-0.85, 5.05, 1.55], [-0.82, 6.0, 1.82], 36]), {}),
    ("L38", c([0, [-0.35, 3.3, 1.6], [-0.4, 6.0, 1.9], 24]), {"step": 1, "hand": 0.006}),
    ("L40", c([0, [0.3, 4.35, 0.85], [0.0, 6.0, 1.3], 24], [1, [0.3, 4.35, 1.0], [0.0, 6.0, 2.3], 24]), {}),
    ("L41", c([0, [0.0, 5.05, 2.3], HEAD, 30], [1, [0.0, 5.15, 2.3], HEAD, 34]), {}),
    # (r1 M5) on "That DENT was IT": from above, its weight pressing the two-lobed dent
    ("L42", c([0, [0.35, 4.7, 0.62], [0.0, 5.75, 0.75], 28], [1, [0.35, 4.75, 0.62], [0.0, 5.75, 0.75], 30]), {}),
    # the two blinks: the same two-shot each time, so the head is turned further when the light comes back
    ("L43", c([0, [-0.4, 3.9, 1.65], [-0.4, 6.0, 1.85], 26]), {"step": 1, "hand": 0.004}),
    ("L44", c([0, [-1.2, 5.0, 2.0], [0.0, 6.0, 2.1], 24], [1, [-1.18, 5.04, 2.0], [0.0, 6.0, 2.1], 25]), {"hand": 0.003}),
    ("L45", c([0, [-0.4, 3.9, 1.65], [-0.4, 6.0, 1.85], 26]), {"step": 1, "hand": 0.004}),
    ("L46", c([0, [-0.45, 7.6, 1.98], [0.0, 6.0, 2.1], 24], [1, [-0.45, 7.55, 1.98], [0.0, 6.0, 2.1], 25]), {}),
    # ---- 05 it follows me
    ("L47", c([0, [0.35, -5.7, 1.6], [0.0, 5.0, 1.4], 26]), {"step": 1, "hand": 0.006}),
    ("L48", c([0, [-0.1, -3.9, 1.55], [-0.3, -5.0, 1.55], 30]), {"step": 1, "hand": 0.004}),
    ("L49", c([0, POV, [0.0, 5.0, 2.05], 40]), {"step": 1, "hand": 0.004}),
    ("L50", c([0, [0.3, 0.2, 1.2], [0.0, 5.0, 1.75], 26], [1, [0.3, 0.45, 1.2], [0.0, 5.0, 1.78], 27]), {}),
    ("L51", c([0, POV, [0.0, 4.0, 2.0], 36]), {"step": 1, "hand": 0.004}),
    # its arms only ever in close-ups (the owner, on still 2): the big square hands on the poles near the
    # camera, the sleeves going back into the dark, never a long arm seen in full
    ("L52", c([0, [0.22, 0.1, 1.5], [0.6, 0.85, 1.6], 28], [1, [0.23, 0.15, 1.5], [0.6, 0.85, 1.6], 30]), {}),
    ("L53", c([0, [0.5, 0.3, 1.3], [0.6, 0.85, 1.6], 26], [1, [0.5, 0.33, 1.3], [0.6, 0.85, 1.6], 28]), {}),
    ("L54", c([0, [-0.2, -1.6, 1.5], [0.0, 0.85, 1.55], 26]), {"hand": 0.004}),
    ("L55", c([0, [0.0, -2.6, 1.4], [0.0, -1.45, 1.35], 28]), {"step": 1, "hand": 0.006}),
    ("L56", c([0, [0.3, -5.25, 1.75], [-0.6, -3.75, 1.25], 28]), {"step": 1, "hand": 0.006}),
    ("L57", c([0, [0.2, -4.9, 1.5], [-0.6, -3.75, 1.3], 26], [1, [0.19, -4.86, 1.5], [-0.6, -3.75, 1.3], 27]), {}),
    # (r1 M10) close on the mirror, the square hand on the glass for the tap
    ("L58", c([0, [-0.12, -4.2, 1.85], [0.3, -7.0, 2.2], 26]), {"step": 1, "hand": 0.003}),
    ("L59", c([0, EYE[0], EYE[1], 50]), {"hand": 0.003}),
    ("L60", c([0, [0.05, -6.85, 1.6], [0.0, -4.9, 1.6], 26]), {"step": 1, "hand": 0.004}),
    ("L61", c([0, [0.12, -6.3, 1.58], [0.0, -4.9, 1.6], 30], [1, [0.12, -6.2, 1.58], [0.0, -4.9, 1.6], 32]), {}),
    ("L63.1", c([0, [0.45, -5.9, 1.62], [0.3, -4.9, 1.62], 34]), {"step": 1, "hand": 0.003}),
    ("L64", c([0, [0.32, -5.55, 1.55], [0.3, -4.9, 1.52], 34], [1, [0.32, -5.5, 1.55], [0.3, -4.9, 1.52], 38]), {}),
    ("L65", c([0, [-0.3, -5.75, 1.58], [-0.3, -4.95, 1.55], 34]), {"hand": 0.003}),
    ("L66", c([0, [-0.2, -5.6, 1.55], [0.3, -4.9, 1.62], 32], [1, [-0.18, -5.55, 1.55], [0.3, -4.9, 1.62], 34]), {}),
    # ---- 06 lonely. The match cut back to the print, at L23's angle
    ("L67", c([0, [0.3, 5.3, 1.86], [0.28, 6.62, 1.86], 28], [1, [0.3, 5.4, 1.86], [0.28, 6.62, 1.86], 30]), {}),
    ("L68", c([0, [0.3, -1.6, 1.7], [0.1, -4.8, 1.5], 26], [1, [0.3, -1.8, 1.7], [0.1, -4.8, 1.5], 27]), {}),
    ("L69", c([0, [0.75, -3.2, 1.45], [0.25, -4.6, 1.65], 30], [1, [0.72, -3.3, 1.45], [0.25, -4.6, 1.65], 32]), {}),
    ("L70", c([0, [0.45, 5.6, 1.7], [0.0, -2.5, 1.3], 26]), {}),
    ("L71", c([0, [-0.4, 3.9, 1.65], [-0.4, 6.0, 1.85], 26]), {"hand": 0.004}),
    ("L72.2", c([0, [-0.45, 4.7, 1.9], [-0.45, 6.0, 1.95], 30], [1, [-0.45, 4.8, 1.9], [-0.45, 6.0, 1.95], 32]), {}),
    ("L73", c([0, [-0.85, 4.95, 1.55], [-0.82, 6.0, 1.82], 34], [1, [-0.85, 5.05, 1.55], [-0.82, 6.0, 1.82], 36]), {}),
    # the wave, seen from the middle door as I step off
    ("L74", c([0, [0.75, 2.05, 1.75], [0.15, 5.7, 2.15], 30], [1, [0.74, 2.12, 1.75], [0.15, 5.7, 2.15], 32]), {}),
    # ---- 07 the next night
    # S76 (r2 item 2): pulled back and round so the board reads "LANTERN HILL" whole
    ("L75", c([0, [-1.2, -17.5, 1.6], [1.1, -5.0, 2.0], 22], [1, [-1.1, -17.2, 1.6], [1.1, -5.0, 2.0], 23]), {"tags": ["ext"]}),
    ("L75.1", c([0, [4.3, -7.6, 1.15], [2.2, -6.0, 1.25], 30], [1, [4.25, -7.45, 1.15], [2.2, -6.0, 1.25], 33]), {"tags": ["ext"]}),
    # (r1 M10) from above, its long arm across the empty seat like a bar
    ("L76", c([0, [-0.95, 4.9, 2.3], [-0.95, 5.95, 0.85], 24], [1, [-0.95, 4.95, 2.3], [-0.95, 5.95, 0.85], 25]), {}),
    ("L77", c([0, [-1.55, 5.1, 1.25], [-0.8, 5.9, 0.95], 26]), {}),
    ("L78", c([0, [0.15, -3.95, 1.4], [1.38, -3.0, 1.55], 36], [1, [0.2, -3.85, 1.42], [1.38, -3.0, 1.55], 40]), {}),
    # (r1 M9) me walking back to sit beside it, held through "The driver says SIX"
    ("L79", c([0, [0.0, -0.5, 1.75], [0.0, 5.5, 1.2], 26], [1, [0.0, 0.6, 1.75], [0.0, 5.5, 1.25], 28]), {}),
    # the aisle wide that ends on S01's first frame, so the loop cuts straight back to the empty bus
    ("L81", c([0, [0.0, -3.2, 0.46], LOOP_CAM[1], 25], [1, LOOP_CAM[0], LOOP_CAM[1], LOOP_CAM[2]]), {"hand": 0.01}),
]

shots, ext, rainy = [], [], []
for i, (at, cam, opt) in enumerate(SH):
    sid = f"S{i + 1:02d}"
    s = {"id": sid, "cam": cam, "step": opt.get("step", 2)}
    if i:
        s["at"] = at
    if "hand" in opt:
        s["hand"] = opt["hand"]
    shots.append(s)
    if "ext" in opt.get("tags", []):
        ext.append(sid)
    if "rain" in opt.get("tags", []):
        rainy.append(sid)

# Every dark beat: (time, the light-drop length, the post's black). Each one is where it changes pose, so it's
# never seen moving. At least 0.5 s apart (standards' flash bar), and "OUT" cuts in the beat after the word.
DARK = [
    ("L43.1+0.05", 0.2, 0.9), ("L45.0+0.3", 0.2, 0.9),
    ("L48.2+0.2", 0.6, 1.0),                               # every light on the bus went out
    ("L51.0+0.15", 0.25, 0.9), ("L55.0>", 0.25, 0.9), ("L56.0>", 0.25, 0.9), ("L60.0>", 0.25, 0.9),
    ("L62.1", 1.2, 1.0),                                   # the wet click, heard in the dark
    ("L71.1", 0.9, 1.0),                                   # the seat beside me creaks, in the dark
]
cues = [
    {"at": 0, "name": "night", "night": "A"},
    {"at": 0, "name": "creature", "pose": "seated"},
    {"at": 0, "name": "flicker", "on": True},
    # S01 (r1 M6): the strap sways on its own, and the back-row tubes dip once on "BACK ROW"
    {"at": 0, "name": "swing", "amp": 0.2},
    {"at": "L01.4+0.25", "name": "drop", "dur": 0.4, "gain": 0.08},
    {"at": "L03.2", "name": "stop"}, {"at": "L03.2+0.05", "name": "door"}, {"at": "L06", "name": "door_shut"},
    {"at": "L08", "name": "go"},
    {"at": "L14", "name": "night", "night": "B"},
    {"at": "L16", "name": "swing"},
    {"at": "L17", "name": "night", "night": "C"},
    {"at": "L21", "name": "night", "night": "D"},
    {"at": "L24", "name": "night", "night": "E"},
    # "Two" comes back from the back row: its tube sinks, the strap swings over the empty seat
    {"at": "L27", "name": "back", "gain": 0.4}, {"at": "L27", "name": "swing", "amp": 0.3},
    {"at": "L29", "name": "back", "gain": 1.0},
    {"at": "L29", "name": "night", "night": "F"},
    {"at": "L30", "name": "drip"}, {"at": "L30.1", "name": "leak"},
    # the two L34 drops, on "flickered ONCE" and "TWICE", more than 0.5 s apart (r1 item 5)
    {"at": "L34.2", "name": "drop", "dur": 0.13}, {"at": "L34.3", "name": "drop", "dur": 0.13},
    {"at": "L34.5", "name": "flicker", "on": False},
    {"at": "L35.1", "name": "stop"}, {"at": "L38>+0.6", "name": "go"},
    {"at": "L38", "name": "dim"},
    # its head, after each blink
    cr("L43.1+0.15", "seated", head=[TO_ME, 4]),
    cr("L45.0+0.4", "seated", head=[-150, 6]),
    # horror lighting (r1 M4) from the blackout until the warm turn (L67, a cut away from it)
    {"at": "L48.2+0.3", "name": "horror", "on": True}, {"at": "L67", "name": "horror", "on": False},   # it warms
    cr("L48.2+0.3", "stand"),                                              # up, far too tall, at the back
    cr("L51.0+0.25", "reach", y=3.3),                                     # a row closer, its arms down the aisle
    cr("L55.0>+0.12", "pole2"),                                            # its hands on the next poles
    cr("L56.0>+0.12", "mirror"),                                           # down the poles to me, a hand on the mirror
    cr("L60.0>+0.12", "behind"),                                           # right behind me
    cr("L67", "behind_hang"),                                              # (at the cut away to the window)
    cr("L70", "watch"),                                                    # (at the cut to the back row)
    cr("L71.1+0.3", "seated"),                                             # back beside me, in the dark
    {"at": "L67", "name": "fogwin", "on": True}, {"at": "L68", "name": "fogwin", "on": False},
    {"at": "L73", "name": "stop"}, {"at": "L74", "name": "door"}, {"at": "L74>+0.3", "name": "door_shut"},
    {"at": "L74>+0.6", "name": "go"},
    cr("L74", "seated", hand=[1, [0.7, 5.7, 2.45]]),                     # the wave, its hand at the window
    {"at": "L75", "name": "night", "night": "G"}, {"at": "L75", "name": "dry"}, {"at": "L75", "name": "undim"},
    {"at": "L75", "name": "flicker", "on": True},
    {"at": "L75", "name": "stop"}, {"at": "L75.1-0.15", "name": "door"}, {"at": "L76", "name": "door_shut"},
    {"at": "L76+0.3", "name": "go"},
    cr("L75", "seated", hand=[-1, [-1.6, 5.9, 1.05]]),                    # its long arm across my seat
    cr("L78", "seated"),                                                   # (at the cut to her)
]
for at, dur, _ in DARK:
    cues.append({"at": at, "name": "drop", "dur": dur})

# Six shots' own light (round 2b fixes), on for exactly their frames: "shot" cues switch at half a frame before each
# shot's first frame and its next shot's first frame (set.py shot_look). Nothing else changes.
HEAD_LOOK = {"back": 0.05, "front": 0.3, "under": 6.0, "under_size": 0.08, "under_face": True, "under_out": 0.6,
             "under_down": 0.35}
POLE_HAND = [-0.6, -3.75, 1.25]
SHOT_LOOKS = [
    ("L42", "L43", {"back": 0.6, "side": [[0.95, 5.2, 0.62], [0.0, 5.8, 0.8], 30.0]}),              # S44 the dent
    ("L44", "L45", {**HEAD_LOOK, "rim0": [[0.8, 6.45, 2.45], HEAD, 15.0], "rim1": [[-0.2, 6.5, 2.6], HEAD, 10.0]}),                           # S46 the head
    ("L46", "L47", {**HEAD_LOOK, "under": 3.0, "under_pos": [-0.35, 6.5, 1.8], "rim0": [[0.9, 5.3, 2.45], HEAD, 15.0],
                    "rim1": [[0.6, 6.5, 1.6], HEAD, 10.0]}),                            # S48 the head
    ("L56", "L57", {"back": 0.5, "rim1": [[-0.9, -3.2, 1.9], POLE_HAND, 25.0]}),                     # S58 the poles
    ("L57", "L58", {"back": 0.5, "rim1": [[-0.9, -3.2, 1.9], POLE_HAND, 25.0]}),                     # S59 the hand
    ("L58", "L59", {"back": 0.5, "rim1": [[0.75, -6.6, 2.6], [0.33, -6.98, 2.3], 40.0],
                    "side": [[-0.9, -6.1, 2.55], [-1.35, -6.47, 1.7], 25.0]}),                       # S60 the mirror
]
for a, b, look in SHOT_LOOKS:
    cues.append({"at": f"{a}-0.017", "name": "shot", "look": look})
    cues.append({"at": f"{b}-0.017", "name": "shot", "look": None})

fx = [
    {"at": "L04.1", "kind": "punch", "dur": 0.9, "zoom": 1.12, "fade": 0.1},
    {"at": "L07", "kind": "punch", "dur": 0.5, "zoom": 1.1, "fade": 0.1},
    {"at": "L22.1", "kind": "punch", "dur": 0.7, "zoom": 1.08, "fade": 0.2},
    {"at": "L26", "kind": "punch", "dur": 0.45, "zoom": 1.1, "fade": 0.1},
    {"at": "L34.2", "kind": "black", "dur": 0.1, "amp": 0.6},
    {"at": "L34.3", "kind": "black", "dur": 0.1, "amp": 0.6},
    {"at": "L36", "kind": "punch", "dur": 0.5, "zoom": 1.1, "fade": 0.1},
    {"at": "L38", "kind": "punch", "dur": 0.6, "zoom": 1.14, "fade": 0.15},
    {"at": "L38", "kind": "shake", "dur": 0.4, "amp": 0.6},
    {"at": "L55.0>+0.25", "kind": "shake", "dur": 0.3, "amp": 0.45},
    {"at": "L56.0>+0.25", "kind": "shake", "dur": 0.3, "amp": 0.5},
    {"at": "L60.0>+0.25", "kind": "shake", "dur": 0.35, "amp": 0.6},
]
for at, dur, amp in DARK:
    fx.append({"at": at, "kind": "black", "dur": dur, "amp": amp, "fade": 0.06})

sfx = [
    {"at": "L03.1", "kind": "bell", "db": -14},
    {"at": "L03.2", "kind": "whoosh", "db": -12},
    {"at": "L11.2", "kind": "glitch", "db": -24, "dur": 0.25},
    {"at": "L16", "kind": "creak", "db": -22, "dur": 1.2},
    {"at": "L20.1", "kind": "thud", "db": -16},
    {"at": "L21.2", "kind": "riser", "db": -22, "dur": 1.6},
    {"at": "L22.1", "kind": "thud", "db": -10},
    {"at": "L26", "kind": "sting", "db": -16, "dur": 1.5},
    {"at": "L28", "kind": "sting", "db": -20, "dur": 1.4},
    {"at": "L29", "kind": "hit", "db": -16},
    {"at": "L30.1", "kind": "click", "db": -10},
    {"at": "L32.4+0.9", "kind": "creak", "db": -14, "dur": 0.6},
    {"at": "L34.2", "kind": "glitch", "db": -20, "dur": 0.12},
    {"at": "L34.3", "kind": "glitch", "db": -20, "dur": 0.12},
    {"at": "L34.5", "kind": "sting", "db": -14, "dur": 2.0},
    {"at": "L35.1", "kind": "bell", "db": -16},
    {"at": "L38", "kind": "hit", "db": -7, "keep": True},            # the reveal lands at the end of the hole
    {"at": "L38+0.05", "kind": "sting", "db": -12, "dur": 2.4, "keep": True},
    {"at": "L48.2+0.2", "kind": "hit", "db": -9, "keep": True},
    {"at": "L49.1", "kind": "sting", "db": -14, "dur": 2.0},
    {"at": "L51.0+0.15", "kind": "hit", "db": -11},
    {"at": "L55.0>", "kind": "hit", "db": -11},
    {"at": "L56.0>", "kind": "hit", "db": -11},
    {"at": "L58.1", "kind": "click", "db": -8},                      # a soft tap on the glass, twice
    {"at": "L58.1+0.22", "kind": "click", "db": -10},
    {"at": "L60.0>", "kind": "hit", "db": -9},
    {"at": "L62.3-0.1", "kind": "wetclick", "db": -9, "dur": 1.2, "keep": True},
    {"at": "L71.3", "kind": "creak", "db": -12, "dur": 1.0, "keep": True},
    {"at": "L73", "kind": "bell", "db": -10},
    {"at": "L75.1", "kind": "whoosh", "db": -9},
]
for at, _, _ in DARK:   # the tubes' buzz crackle on every drop
    sfx.append({"at": at, "kind": "glitch", "db": -17, "dur": 0.2})

# L28's "Two." heard from the back of the bus: the same voice, darker and further off
for ln in lines:
    if ln["id"] == "L28":
        ln["space"] = {"chunks": [0], "lowpass": 2000, "verb": 0.55, "gain_db": -4}

story = {
    "slug": "ep11-back-row",
    "title": "Never sit in the back row",
    "made_for_kids": False,
    "premise": "A night-shift worker rides the last bus home every night after a nine-hour shift. At each stop the silent driver checks his mirror and says six, but the worker only ever counts five riders, and nobody sits in the flickering back row.",
    "twist": "The count was right all along. A grey passenger built like everyone else, but far too tall, with arms far too long and a pale seamed head that turns too far, has sat in the back row for years. When the worker sits there it follows them up the bus in the dark, then asks in their own voice for company. It was only lonely, and now the worker sits with it every night.",
    "world": "The inside of a city night bus over seven nights: worn vinyl seats, chrome poles, a studded rubber floor, cold fluorescent tubes that flicker over the back row, and one foggy concrete bus stop.",
    "voice": {"voice": "am_adam", "tempo": 1.03, "rate": 1.45},
    "key_color": "#c8ff5a",
    "gap": 0.1,
    "tail": 0,          # no black at the end (r1 T5): the last shot cuts straight back to the first
    "look": {"fog": "#10161d", "fog_density": 0.055, "fog_start": 7.5, "sky": "#070a0e", "sky_strength": 1.0,
             "exposure": 0.25},
    "grade": {"shadows": [-0.04, 0.02, 0.07], "highlights": [-0.01, 0.03, -0.02], "saturation": 0.82,
              "contrast": 1.08, "vignette": 0.42, "bloom": 0.42, "grain": 0.014},
    "exterior_shots": ext,
    "rain_shots": rainy,
    "rain_gain": 1.6,
    "phonemes": {"collar": "kˈɑlɚ"},
    "cast": cast,
    "lines": lines,
    "shots": shots,
    "acting": acting,
    "cues": cues,
    "fx": fx,
    "music": {"root": 45, "mode": "phrygian", "bpm": 66, "seed": 11,
              "sections": [   # no music box anywhere (r1 item 4)
                  {"at": 0, "voices": ["drone", "pad"], "energy": 0.3},
                  {"at": "L12", "voices": ["drone", "pad", "piano"], "energy": 0.35},
                  {"at": "L14", "voices": ["drone", "pad", "piano"], "energy": 0.3},
                  {"at": "L21", "voices": ["drone", "pad", "piano"], "energy": 0.4},
                  {"at": "L24", "voices": ["drone"], "energy": 0.2},
                  {"at": "L27", "voices": ["drone"], "energy": 0.15},
                  {"at": "L29", "voices": ["drone", "pad", "pulse"], "energy": 0.45},
                  {"at": "L32", "voices": ["drone", "pad", "piano", "pulse"], "energy": 0.55},
                  {"at": "L35", "voices": ["drone", "pad", "pulse"], "energy": 0.7},
                  {"at": "L39", "voices": ["drone", "choir"], "energy": 0.4},
                  {"at": "L43", "voices": ["drone", "choir", "pad"], "energy": 0.5},
                  {"at": "L47", "voices": ["drone", "pulse", "choir"], "energy": 0.75},
                  {"at": "L51", "voices": ["drone", "pad", "pulse", "choir"], "energy": 0.9},
                  {"at": "L55", "voices": ["drone", "pad", "pulse", "choir"], "energy": 1.0},
                  {"at": "L61", "voices": ["drone"], "energy": 0.3},
                  {"at": "L67", "voices": ["pad", "piano"], "energy": 0.35},      # it warms: no choir, the piano in
                  {"at": "L73", "voices": ["drone", "pad", "piano"], "energy": 0.35},
                  {"at": "L75", "voices": ["pad", "piano"], "energy": 0.4},
                  {"at": "L79", "voices": ["pad", "piano"], "energy": 0.45},
              ]},
    "sound": {"floor": "stone", "steps_db": -24,
              "ambience": [
                  {"kind": "hum", "from": 0, "to": "end", "lufs": -31},
                  {"kind": "room", "from": 0, "to": "end", "lufs": -37},
                  {"kind": "rain", "from": 0, "to": "L14", "lufs": -35},
                  {"kind": "rain", "from": "L14", "to": "L17", "lufs": -38},
                  {"kind": "wind", "from": "L21", "to": "L24", "lufs": -36},
                  {"kind": "rain", "from": "L24", "to": "L29", "lufs": -36},
                  {"kind": "rain", "from": "L29", "to": "L75", "lufs": -29},
                  {"kind": "drips", "from": "L30", "to": "L33", "lufs": -34},
                  {"kind": "static", "from": "L49", "to": "L62", "lufs": -40},
                  {"kind": "rain", "from": "L75", "to": "end", "lufs": -38},
                  {"kind": "wind", "from": "L75", "to": "L76", "lufs": -37},
              ],
              "sfx": sfx,
              # real holes (r1 E3): everything but the voice and the kept sounds drops 40 dB, anchored to lines
              "music_drops": [{"from": "L36", "to": "L38"}, {"from": "L48.2", "to": "L49"},
                              {"from": "L62", "to": "L63"}, {"from": "L65", "to": "L66>"},
                              {"from": "L71", "to": "L72"}]},
}
OUT.write_text(json.dumps(story, indent=1, ensure_ascii=False) + "\n")
print("wrote", OUT, f"({len(shots)} shots)")
