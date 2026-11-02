"""Writes ../story.json for ep20 "photo-strip" (the Third, in the old photo booth at a wedding).

Run from anywhere: python stories/ep20-photo-strip/generator/make_story.py
The words are in lines.json next to this file. Everything else is here: the cast, the shots, the acting, the cues
set.py reads, the effects, the score and the sound. Shot ids are numbered in order (S01 ...).

Places (set.py's coordinates): the hall runs along x (the ballroom door at x = 19, Wren's end is x = 3, mine x = 15), the
booth is in the +y wall's alcove, centred on x = 9 (BX). Its curtain is at y = 3.2, the bench's top is z = 0.5 and the
back velvet (with the one seam, x = 9) is at y = 4.76. People sit at y = 4.6 facing -y; Wren at the left (x < 9), me at
the right. Wren and I sit further apart every visit (SEP) and together on the last: that's the whole twist, and the
Third never moves.
"""
import json
import math
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE.parent / "story.json"
lines = json.loads((HERE / "lines.json").read_text())

BX = 9.0
SEP = {1: 0.62, 2: 0.70, 3: 0.79, 4: 0.87, 5: 0.50}      # from the middle to each person: visit 1 to 4, then together
SEAT_Y, SEAT_Z = 4.60, -0.01
FACE_Z = 1.56                                           # a face's height, seated or standing
TX, TY = BX, -2.0 + 0.55                                # the side table under the middle lamp
SX = 40.0                                               # the black table the insert shots are laid on (set.py's STAGE)

# the prints (prints.py): a strip is 0.2 m wide; frame k's centre is c(k) from the strip's middle
PW, PAD, FW, FH = 968, 44, 880, 768
SH_STRIP = 4 * FH + 5 * PAD
STRIP_H = 0.2 * SH_STRIP / PW
FRAME_H = FH / SH_STRIP * STRIP_H
FRAME_W = FW / PW * 0.2
HALF_H = 0.2 * (2 * FH + 3 * PAD) / PW


def c(*keys):
    return [list(k) for k in keys]


def mv(p0, t0, l0, p1=None, t1=None, l1=None):
    """A camera: one key, or a move from the first key to the second over the shot."""
    if p1 is None:
        return c([0, p0, t0, l0])
    return c([0, p0, t0, l0], [1, p1, t1 if t1 is not None else t0, l1 if l1 is not None else l0])


def front(hd, yaw, off=0.0, dist=1.0, dz=0.0, lens=32, push=0.0, aim_dz=0.0):
    """A camera in front of a face: hd the face's centre, yaw the way the person faces (0 = -y), off degrees round
    from straight on, dist metres away; push moves it in by that much over the shot."""
    a = math.radians(yaw + off)
    d = (math.sin(a), -math.cos(a))
    p0 = [round(hd[0] + d[0] * dist, 3), round(hd[1] + d[1] * dist, 3), round(hd[2] + dz, 3)]
    tg = [hd[0], hd[1], round(hd[2] + aim_dz, 3)]
    if not push:
        return c([0, p0, tg, lens])
    p1 = [round(hd[0] + d[0] * (dist - push), 3), round(hd[1] + d[1] * (dist - push), 3), round(hd[2] + dz, 3)]
    return c([0, p0, tg, lens], [1, p1, tg, lens])


def fy(k, sh=STRIP_H):
    """The y of frame k's centre on a strip lying with its middle at y = 0 (frame 0 at the top, +y)."""
    return sh / 2 - (PAD + FH / 2 + k * (FH + PAD)) / SH_STRIP * sh


def over(x, y, h, lens=34, y2=None, h2=None, dy=-0.16):
    """A camera over the insert table: aimed straight down at (x, y), h metres up, pulled back toward -y by dy so it
    keeps the print's top at the top of the picture. y2/h2 push to a second place."""
    if y2 is None:
        return mv([SX + x, y + dy * h / 0.6, h], [SX + x, y, 0.0], lens)
    return mv([SX + x, y + dy * h / 0.6, h], [SX + x, y, 0.0], lens, [SX + x, y2 + dy * h2 / 0.6, h2], [SX + x, y2, 0.0], lens)


# ---------------------------------------------------------------------------------------------------- the cast
# One voice for everyone: the narrator reads every line, and what Wren and Mum say is reported in it.
cast = {
    "me": {"age": "adult", "skin": "#f1c9a0", "shirt": "#26324f", "pants": "#1d2540", "shoes": "#1a1512", "collar": "#e8e4da",
           "sleeves": "long", "hair": "swoop", "hair_c": "#3a2618", "hat": "none", "extras": ["tie"], "extra_c": "#c8962c",
           "body_width": 0.7, "face": {"eyes": "round", "brows": True}},
    "wren": {"age": "adult", "skin": "#e9bd9a", "shirt": "#2f6b46", "pattern": "knit", "pattern_c": "#245538",
             "pants": "#2f6b46", "pants_pattern": "knit", "pants_pattern_c": "#245538", "shoes": "#2a1c14",
             "sleeves": "long", "hair": "cap", "hair_c": "#7e3a22", "hat": "none", "body_width": 0.7,
             "face": {"eyes": "classic", "brows": True, "cheeks": "#e49a86"}},
    "mum": {"age": "adult", "skin": "#ecc7a8", "shirt": "#b9a3d6", "pants": "#4a4658", "shoes": "#2a2430", "sleeves": "long",
            "hair": "cap", "hair_c": "#a9a9ae", "hat": "none", "extras": ["glasses"], "extra_c": "#6d5a46",
            "body_width": 0.7, "face": {"eyes": "round", "brows": True, "bags": True}},
}


def seat(side, visit, z=SEAT_Z):
    return [round(BX + side * SEP[visit], 3), SEAT_Y, z]


def face_at(side, visit):
    return [round(BX + side * SEP[visit], 3), SEAT_Y, FACE_Z]


# ---------------------------------------------------------------------------------------------------- shots
# (at, camera, options). Options: step (1 = every frame drawn), hand (handheld drift), hide (groups the camera looks
# through), stage (strips laid on the insert table: [id, x, y, rot])
HALL_Y = -1.45
W1, M1, W2, M2, W3, M3, W4, M4, W5, M5 = (face_at(-1, 1), face_at(1, 1), face_at(-1, 2), face_at(1, 2), face_at(-1, 3),
                                           face_at(1, 3), face_at(-1, 4), face_at(1, 4), face_at(-1, 5), face_at(1, 5))
LENS_HIDE = ["front", "curtain"]
HAND_Y = 0.0108                       # the hand's height above a frame's centre on a print
S1 = [("s1", 0, 0, 0)]
SH = [
    # ---- the hook: a strip on the bench between our knees, from above; then Wren, then the hall
    (0, mv([BX, 3.95, 0.82], [BX + 0.0065, 4.102, 0.506], 40, [BX, 3.99, 0.74], [BX + 0.0065, 4.102, 0.506], 40), {}),
    ("L02", front(W1, 0, 40, 1.6, -0.02, 34, push=0.1), {}),
    ("L03", mv([0.1, -1.6, 1.45], [12.0, 1.2, 1.15], 17), {"hand": 0.004}),
    ("L04", over(0, fy(0) + HAND_Y, 0.55, 40, None, None), {"stage": S1}),
    ("L05", mv([9.0, -1.9, 1.45], [9.0, 0.4, 1.4], 15), {}),
    ("L06", front([9.8, 0.4, FACE_Z], 0, -12, 1.9, 0.0, 32, push=0.15), {}),
    ("L07", mv([9.0, -1.8, 1.35], [9.0, 0.6, 1.3], 17, [9.0, -1.65, 1.35], [9.0, 0.6, 1.3], 17), {}),
    ("L08", front([9.0, 0.45, FACE_Z], 0, 8, 1.8, 0.0, 32, push=0.1), {}),
    # into the booth past the curtain, the empty bench and the velvet with its seam
    ("L09", mv([BX + 0.8, 2.4, 1.5], [BX, 4.7, 1.3], 22, [BX + 0.5, 2.7, 1.5], [BX, 4.7, 1.3], 22), {}),
    ("L10", mv([BX, 0.4, 1.55], [BX, 4.7, 1.45], 24), {"hide": LENS_HIDE}),
    ("L11", mv([BX + 0.2, -1.2, 1.4], [BX, 3.2, 1.3], 15), {"step": 1}),
    ("L11.4", mv([BX + 1.55, 1.9, 1.05], [BX + 1.55, 3.0, 0.92], 30, [BX + 1.55, 2.0, 1.0], [BX + 1.55, 3.0, 0.92], 34), {}),
    # the strip: the hand between our heads; then the same hand, close; then the real, empty velvet
    ("L12", over(0, fy(1), 0.62, 40), {"stage": S1}),
    ("L13", over(0, fy(1) + HAND_Y, 0.22, 40), {"stage": S1}),
    ("L14", mv([BX + 0.22, 3.55, 1.5], [BX, 4.76, 1.5], 30, [BX + 0.2, 3.7, 1.5], [BX, 4.76, 1.5], 30), {}),
    ("L15", mv([BX - 1.95, 2.45, 1.25], [BX - 1.7, 4.85, 1.05], 22, [BX - 1.95, 2.55, 1.25], [BX - 1.7, 4.85, 1.05], 22), {}),
    ("L16", front([9.0, 0.45, FACE_Z], 0, -10, 1.8, 0.0, 32, push=0.1), {}),
    ("L17", mv([BX, 0.4, 1.55], [BX, 4.7, 1.45], 24), {"hide": LENS_HIDE}),
    # strip two, the arm and the shoulder; the hand again; Wren's small voice
    ("L18", over(0, fy(1), 0.62, 40), {"stage": [("s2", 0, 0, 0)]}),
    ("L19", over(0, fy(2) + HAND_Y, 0.24, 40), {"stage": [("s2", 0, 0, 0)]}),
    ("L20", front(W2, 0, 25, 1.5, 0.0, 34, push=0.08), {}),
    # the cake in the hall, then my elbow past the curtain
    ("L21", mv([13.0, -1.5, 1.35], [18.2, 0.2, 1.1], 22, [13.6, -1.5, 1.35], [18.2, 0.2, 1.1], 22), {}),
    ("L22", mv([BX + 1.1, 1.5, 1.35], [BX + 1.1, 3.2, 1.2], 30, [BX + 1.1, 1.9, 1.35], [BX + 1.1, 3.2, 1.2], 32), {}),
    # strip three: the whole body, cut at the mouth, the slot smile, the smile wider
    ("L23", over(0, fy(0) - 0.02, 0.6, 38), {"stage": [("s3", 0, 0, 0)]}),
    ("L24", over(0, fy(1) + 0.03, 0.42, 38), {"stage": [("s3", 0, 0, 0)]}),
    ("L25", over(0, fy(1) + 0.0742, 0.2, 40), {"stage": [("s3", 0, 0, 0)]}),
    ("L26", over(0, fy(3) + 0.02, 0.5, 38, None, None), {"stage": [("s3", 0, 0, 0)]}),
    ("L27", mv([9.0, -1.55, 1.5], [9.0, 0.3, 1.4], 17, [9.0, -1.4, 1.5], [9.0, 0.3, 1.4], 17), {}),
    ("L28", mv([BX + 0.2, -1.1, 1.4], [BX, 3.2, 1.3], 24), {}),
    ("L28.2", mv([BX + 1.55, 1.2, 1.7], [BX + 1.55, 3.1, 1.52], 32, [BX + 1.55, 1.7, 1.66], [BX + 1.55, 3.1, 1.52], 36), {}),
    ("L29", front(W4, 0, 28, 1.5, 0.0, 34, push=0.08), {}),
    ("L30", mv([BX, 0.4, 1.55], [BX, 4.7, 1.45], 24), {"hide": LENS_HIDE}),
    # ---- the scare: out, black, the sound, the second glow, it
    ("L31", mv([BX, 0.4, 1.55], [BX, 4.7, 1.45], 24), {"hide": LENS_HIDE, "step": 1}),
    ("L32", front(W4, 0, 20, 1.5, 0.0, 34), {"step": 1}),
    ("L33", mv([BX + 0.3, 3.6, 1.0], [BX, 4.7, 1.2], 30), {"step": 1}),
    ("L34", mv([BX + 0.4, 3.5, 0.55], [BX, 4.7, 1.0], 26, [BX + 0.4, 3.55, 0.6], [BX, 4.7, 1.05], 26), {"step": 1}),
    ("L35", mv([BX + 0.45, 3.4, 1.1], [BX - 0.05, 4.75, 1.75], 14, [BX + 0.4, 3.45, 1.1], [BX - 0.05, 4.75, 1.77], 14),
     {"step": 1, "hand": 0.003}),
    ("L36", mv([BX + 0.45, 3.85, 1.55], [BX + 0.02, 4.74, 1.5], 38), {"step": 1}),
    ("L37", mv([BX + 0.55, 3.8, 0.75], [BX, 4.74, 2.35], 18, [BX + 0.5, 3.9, 0.8], [BX, 4.74, 2.37], 20), {"step": 1}),
    ("L38", front(M4, 0, -28, 1.5, 0.0, 34), {"step": 1}),
    ("L39", mv([BX - 2.0, 4.742, 2.3], [BX, 4.742, 1.5], 17), {"step": 1, "hide": ["wall_l"]}),
    ("L40", mv([BX + 0.1, -0.2, 1.45], [BX, 3.2, 1.3], 24), {"step": 1}),
    ("L41", mv([9.0, -1.6, 1.8], [9.0, 0.5, 1.2], 14), {"hand": 0.006}),
    # ---- the table, the four strips, what they say
    ("L42", mv([TX - 0.25, TY + 0.95, 1.85], [TX, TY, 0.82], 30), {}),
    ("L43", front([TX + 0.95, TY + 0.2, FACE_Z], -90, 0, 1.3, 0.0, 32), {}),
    ("L44", mv([SX - 0.2, fy(1) - 0.08, 0.95], [SX - 0.2, fy(1) + HAND_Y, 0.0], 40,
               [SX + 0.2, fy(1) - 0.08, 0.95], [SX + 0.2, fy(1) + HAND_Y, 0.0], 40),
     {"stage": [("s1", -0.315, 0, 0), ("s2", -0.105, 0, 0), ("s3", 0.105, 0, 0), ("s4", 0.315, 0, 0)]}),
    ("L45", over(0, 0, 0.95, 32), {"stage": [("s1", -0.11, -fy(0), 0), ("s4", 0.11, -fy(3), 0)]}),
    ("L46", over(0, 0, 0.8, 34, None, None), {"stage": [("s1", -0.11, -fy(1), 0), ("s4", 0.11, -fy(1), 0)]}),
    ("L47", over(0, fy(0) - 0.03, 0.5, 36, None, 0.28), {"stage": [("s3", 0, 0, 0)]}),
    # ---- the hall: me at one end, Wren at the other, and between us, the Third
    ("L48", mv([17.2, -0.2, 2.05], [4.0, -0.3, 1.2], 17), {}),
    ("L49", mv([13.6, -0.55, 1.45], [9.0, 0.0, 1.45], 26, [13.2, -0.55, 1.45], [9.0, 0.0, 1.45], 26), {"step": 1}),
    ("L50", mv([4.9, -0.6, 1.5], [3.6, -1.0, 1.5], 30), {}),
    ("L51", front([14.0, -0.95, FACE_Z], -90, -35, 1.7, 0.0, 32), {}),
    ("L52", mv([16.2, 0.2, 1.9], [5.0, -0.5, 1.3], 15), {"step": 1}),
    ("L53", mv([9.0, 0.7, 1.55], [9.0, -1.0, 1.5], 24), {}),
    ("L54", mv([9.3, -1.75, 1.62], [8.45, -1.0, FACE_Z], 28), {}),
    ("L54.4", mv([8.7, -1.75, 1.62], [9.55, -1.0, FACE_Z], 28), {}),
    ("L55", mv([BX, 0.4, 1.55], [BX, 4.7, 1.4], 28), {"hide": LENS_HIDE}),
    ("L56", front(W5, 0, 22, 1.5, 0.0, 34, push=0.08), {}),
    ("L57", front(M5, 0, -22, 1.5, 0.0, 34), {}),
    ("L57.2", front(W5, 0, 22, 1.5, 0.0, 34, push=0.06), {}),
    ("L58", over(0, fy(2) + 0.04, 0.78, 36), {"stage": [("s5", 0, 0, 0)]}),
    ("L59", mv([9.1, TY + 0.5, 1.3], [9.1, TY + 0.0, 0.8], 30), {}),
    ("L59.5", front([9.8, -0.62, 1.3], 0, 10, 1.3, 0.0, 34), {}),
    ("L60", mv([16.8, -0.7, 1.55], [11.5, -0.7, 1.5], 24, [16.2, -0.7, 1.55], [11.5, -0.7, 1.5], 24), {"hand": 0.004}),
]
shots, hides, stages = [], {}, {}
for i, (at, cam, opt) in enumerate(SH):
    sid = f"S{i + 1:02d}"
    s = {"id": sid, "cam": cam, "step": opt.get("step", 2)}
    if i:
        s["at"] = at
    if "hand" in opt:
        s["hand"] = opt["hand"]
    shots.append(s)
    if "hide" in opt:
        hides[sid] = opt["hide"]
    if "stage" in opt:
        stages[sid] = [list(e) for e in opt["stage"]]
SID = {at: s["id"] for (at, _, _), s in zip(SH, shots)}

# ---------------------------------------------------------------------------------------------------- acting


def jump(at, frm, to, **kw):
    """A move on a cut: two keys at the same moment, so nobody walks on film."""
    return [{"at": at, "pos": frm}, {"at": at, "pos": to, "blend": 0.0, **kw}]


def sit(at, pos, **kw):
    return {"at": at, "pos": pos, "sit": True, "yaw": 0, "arms": [34, 34], **kw}


def stand(at, pos, **kw):
    return {"at": at, "pos": pos, "sit": False, **kw}


def sitjump(at, frm, to, **kw):
    return [{"at": at, "pos": frm}, {**sit(at, to, **kw), "blend": 0.0}]


ME_HALL = [9.7, 0.4, 0.0]
WREN_HALL = [8.3, 0.4, 0.0]
MUM_HALL = [9.0, 0.4, 0.0]
ROAM = [9.0, 1.2, 0.0]
WREN_END, ME_END = [3.4, -0.95, 0.0], [14.6, -0.95, 0.0]

me = [
    sit(0, seat(1, 1), expr="worried", head=[-8, 0], look=[-0.3, 0]),
    {"at": "L02", "head": [-38, 0], "look": [-0.8, 0], "expr": "worried", "blend": 0.3},
    # the hall, before: a metre of floor between us, both looking away
    *jump("L05", seat(1, 1), ME_HALL, sit=False, yaw=0, arms=[0, 0], head=[55, 0], look=[0.8, 0], expr="neutral"),
    {"at": "L06", "expr": "angry", "head": [10, 0], "look": [0, 0]},
    {"at": "L07", "expr": "neutral", "head": [0, 0]},
    *jump("L07", ME_HALL, [9.95, 0.4, 0.0]),
    # the booth, the first visit, ends of the bench
    *sitjump("L10", [9.95, 0.4, 0.0], seat(1, 1), expr="worried", head=[0, 0], look=[0, 0]),
    {"at": "L14", "hidden": True},
    {"at": "L15", "hidden": False},
    *jump("L16", seat(1, 1), [10.0, 0.4, 0.0], sit=False, arms=[0, 0], expr="neutral", head=[40, 0]),
    # second visit: Wren to the edge, so me to mine
    *sitjump("L17", [10.0, 0.4, 0.0], seat(1, 1), expr="worried"),
    {"at": "L17.3", "pos": seat(1, 1)},
    {"at": "L17.4", "pos": seat(1, 2)},
    {"at": "L20", "expr": "worried", "head": [-30, 0], "look": [-0.7, 0]},
    # third visit, my elbow out past the curtain
    *jump("L22", seat(1, 2), seat(1, 3), side=[0, 24], head=[0, 0], look=[0, 0]),
    {"at": "L26", "expr": "scared", "side": [0, 0]},
    *jump("L27", seat(1, 3), [9.95, 0.3, 0.0], sit=False, arms=[0, 0], side=[0, 0], yaw=-60, expr="angry", head=[0, 0]),
    {"at": "L27.3", "expr": "worried"},
    *sitjump("L28", [9.95, 0.3, 0.0], seat(1, 4), expr="neutral", head=[0, 0], look=[0, 0]),
    {"at": "L30", "head": [0, 0], "look": [0, 0]},
    {"at": "L33", "expr": "scared", "look": [-0.4, 0]},
    {"at": "L35", "expr": "terrified", "tremble": 1.2, "head": [-14, 0], "look": [-0.7, 0]},
    {"at": "L37", "head": [-8, 0], "look": [-0.8, 0]},
    {"at": "L38", "bend": 20, "head": [-28, 0], "blend": 0.3},
    {"at": "L39", "bend": 0.0, "head": [0, 0], "tremble": 0.0, "blend": 0.4},
    # out, to the other end of the hall, then the table
    *jump("L41", seat(1, 4), [BX + 0.7, 2.7, 0.0], sit=False, arms=[0, 0], bend=0, expr="terrified", tremble=1.0,
          yaw=0, head=[0, 0], look=[0, 0], run=True),
    {"at": "L41>", "pos": [BX + 5.4, -1.0, 0.0]},
    *jump("L42", [BX + 5.4, -1.0, 0.0], [TX + 0.95, TY + 0.2, 0.0], yaw=-90, expr="worried", tremble=0.0, head=[0, 18]),
    {"at": "L43", "expr": "scared"},
    {"at": "L44", "expr": "worried"},
    # the hall again: the length of it between us
    *jump("L48", [TX + 0.95, TY + 0.2, 0.0], ME_END, yaw=-90, expr="worried", head=[0, 0], look=[0, 0]),
    {"at": "L49", "expr": "scared"},
    {"at": "L51", "pos": ME_END},
    {"at": "L51.1", "pos": [14.0, -0.95, 0.0]},
    {"at": "L52", "pos": [14.0, -0.95, 0.0]},
    {"at": "L53", "pos": [11.4, -0.95, 0.0]},
    {"at": "L53.4", "pos": [9.55, -1.0, 0.0], "yaw": -90},
    {"at": "L54", "yaw": -40, "expr": "soft", "head": [0, 0]},
    # the last visit: in the middle, squashed
    *sitjump("L55", [9.55, -1.0, 0.0], seat(1, 5), expr="smirk", head=[-30, 0], look=[-0.6, 0], yaw=0),
    {"at": "L56.1", "expr": "smirk"},
    {"at": "L57", "expr": "fish"},
    {"at": "L57.2", "expr": "squeeze"},
    {"at": "L58", "expr": "soft", "head": [-12, 0]},
    *jump("L59", seat(1, 5), [9.62, -0.62, 0.0], sit=False, arms=[0, 0], yaw=-30, expr="soft", head=[0, 0], look=[0, 0]),
    {"at": "L59.5", "yaw": 0, "head": [0, 0]},
    *jump("L60", [9.62, -0.62, 0.0], [11.5, -1.0, 0.0], yaw=90),
    {"at": "L60>", "pos": [14.6, -1.0, 0.0], "expr": "soft", "head": [-35, 0]},
]
wren = [
    sit(0, seat(-1, 1), expr="neutral", head=[8, 0], look=[0.3, 0]),
    {"at": "L02", "head": [34, 0], "look": [0.6, 0], "expr": "angry", "blend": 0.3},
    *jump("L05", seat(-1, 1), WREN_HALL, sit=False, yaw=0, arms=[0, 0], head=[-55, 0], look=[-0.8, 0], expr="angry"),
    {"at": "L07", "expr": "neutral", "head": [0, 0]},
    *jump("L07", WREN_HALL, [8.05, 0.4, 0.0]),
    *sitjump("L10", [8.05, 0.4, 0.0], seat(-1, 1), expr="neutral", head=[0, 0], look=[0, 0]),
    {"at": "L14", "hidden": True},
    {"at": "L15", "hidden": False},
    *jump("L16", seat(-1, 1), [8.0, 0.4, 0.0], sit=False, arms=[0, 0], expr="angry", head=[-40, 0]),
    *sitjump("L17", [8.0, 0.4, 0.0], seat(-1, 1), expr="angry"),
    {"at": "L17.1", "pos": seat(-1, 2)},
    {"at": "L20", "expr": "worried", "head": [0, 14], "look": [0, -0.8]},
    *jump("L22", seat(-1, 2), seat(-1, 3), expr="angry", head=[0, 0], look=[0, 0]),
    *jump("L27", seat(-1, 3), [8.05, 0.3, 0.0], sit=False, arms=[0, 0], yaw=60, expr="angry", head=[0, 0]),
    *sitjump("L28", [8.05, 0.3, 0.0], seat(-1, 4), expr="neutral", head=[-20, 0], look=[-0.6, 0], yaw=0),
    {"at": "L30", "head": [-25, 0], "look": [-0.7, 0]},
    {"at": "L32", "expr": "worried", "head": [-10, 0]},
    {"at": "L35", "expr": "terrified", "tremble": 1.0, "head": [-4, 0], "look": [0, 0]},
    *jump("L41", seat(-1, 4), [BX - 0.7, 2.7, 0.0], sit=False, arms=[0, 0], expr="terrified", tremble=1.0, yaw=0,
          head=[0, 0], look=[0, 0], run=True),
    {"at": "L41>", "pos": [BX - 5.6, -1.0, 0.0]},
    *jump("L48", [BX - 5.6, -1.0, 0.0], WREN_END, yaw=90, expr="worried", tremble=0.0, head=[0, 0]),
    {"at": "L49", "expr": "scared"},
    {"at": "L50.1", "pos": WREN_END},
    {"at": "L50.3", "pos": [4.05, -0.95, 0.0]},
    {"at": "L52", "pos": [4.05, -0.95, 0.0]},
    {"at": "L53", "pos": [6.6, -0.95, 0.0]},
    {"at": "L53.4", "pos": [8.45, -1.0, 0.0], "yaw": 90},
    {"at": "L54", "yaw": 40, "expr": "soft", "head": [0, 0]},
    *sitjump("L55", [8.45, -1.0, 0.0], seat(-1, 5), expr="smirk", head=[35, 0], look=[0.6, 0], yaw=0, arms=[34, 52]),
    {"at": "L56.1", "expr": "fish"},
    {"at": "L57", "expr": "smirk"},
    {"at": "L57.2", "expr": "squeeze"},
    {"at": "L58", "expr": "soft", "head": [12, 0]},
    *jump("L59", seat(-1, 5), [8.45, -0.62, 0.0], sit=False, arms=[0, 0], yaw=30, expr="soft", head=[0, 0], look=[0, 0]),
    {"at": "L59.5", "yaw": 0},
    *jump("L60", [8.45, -0.62, 0.0], [11.5, -0.3, 0.0], yaw=90),
    {"at": "L60>", "pos": [14.6, -0.55, 0.0], "expr": "soft"},
    {"at": "L60.3", "head": [20, 0], "arms": [0, 0]},
]
mum = [
    {"at": 0, "pos": MUM_HALL, "yaw": 0, "hidden": True, "expr": "soft", "arms": [0, 0]},
    {"at": "L07", "hidden": False, "pos": MUM_HALL, "expr": "soft", "head": [0, 0]},
    {"at": "L08", "expr": "soft"},
    {"at": "L09", "hidden": True},
    {"at": "L16", "hidden": False, "pos": MUM_HALL, "expr": "worried", "head": [0, 12]},
    {"at": "L17", "hidden": True},
]
# Wren's and Mum's mouths move under the words the narrator reports
acting = {"me": me, "wren": wren, "mum": mum}
for who, a, b in (("mum", "L08", "L08.1>"), ("mum", "L08.3", "L08.3>"), ("mum", "L16.3", "L16>"), ("wren", "L20.3", "L20>"),
                  ("wren", "L29", "L29.0>"), ("wren", "L27.4", "L27>"), ("me", "L27.1", "L27.2>")):
    acting[who].append({"from": a, "to": b, "mouth": [0.6, 0.6], "flap": True})
acting["wren"].append({"from": "L57.2", "to": "L57>", "mouth": [0.8, 0.8], "flap": True})

# ---------------------------------------------------------------------------------------------------- cues
LAMP_REST, GLOW = 0.4, 0.7


def glow(ref, off, dur_up=0.3, dur_down=0.35, lo=LAMP_REST, hi=GLOW):
    """One soft glow: a ramp up to about 70% and back (never white)."""
    return [{"at": f"{ref}+{off:.2f}", "name": "lamp", "to": hi, "dur": dur_up},
            {"at": f"{ref}+{off + dur_up + 0.02:.2f}", "name": "lamp", "to": lo, "dur": dur_down}]


cues = [
    {"at": 0, "name": "third", "on": False, "mode": "booth", "arm": "seam", "smile": "normal", "head": 0, "roll": 0},
    {"at": 0, "name": "strip", "id": "s1", "on": True, "pos": [BX, 4.34, 0.505], "rot": 0},
    {"at": "L02+0.9", "name": "strip", "id": "s1", "on": False, "pos": [0, 0, 0]},
    {"at": 0, "name": "curtain", "to": [0.0, 0.0], "dur": 0.0},
    {"at": "L09", "name": "curtain", "to": [0.95, 0.95], "dur": 0.0},
    {"at": "L10", "name": "curtain", "to": [0.0, 0.0], "dur": 0.0},
    {"at": "L12", "name": "curtain", "to": [0.95, 0.95], "dur": 0.0},
    {"at": "L10", "name": "pocket", "on": False},
    # visit one: the lamp glows four times behind the curtain, and the strip slides out
    *[c_ for k in range(4) for c_ in glow("L11", 0.05 + 0.8 * k, dur_down=0.45, lo=0.42, hi=0.55)],
    {"at": "L12", "name": "lamp", "to": LAMP_REST, "dur": 1.5},
    {"at": "L11.4", "name": "strip", "id": "s1", "on": True, "from": [BX + 1.55, 3.12, 0.99], "pos": [BX + 1.55, 2.9, 0.97],
     "tilt": -78, "dur": 0.7},
    {"at": "L12", "name": "strip", "id": "s1", "on": False, "pos": [0, 0, 0]},
    # visit two
    {"at": "L17", "name": "curtain", "to": [0.95, 0.95], "dur": 0.0},
    {"at": "L18", "name": "curtain", "to": [0.0, 0.0], "dur": 0.0},
    # visit three: the curtain's right half held back a little, so my elbow shows at its edge
    {"at": "L22", "name": "curtain", "to": [0.0, 0.0], "mid_r": 0.72, "dur": 0.0},
    {"at": "L23", "name": "curtain", "to": [0.0, 0.0], "dur": 0.0},
    {"at": "L21", "name": "cake", "from": [17.0, -1.5], "to": [17.0, 1.5], "dur": 2.4},
    # the last coin
    {"at": "L27", "name": "curtain", "to": [0.95, 0.95], "dur": 0.0},
    {"at": "L28", "name": "curtain", "to": [0.95, 0.95], "dur": 0.0},
    {"at": "L28+0.25", "name": "curtain", "to": [0.0, 0.0], "dur": 0.35},
    {"at": "L29+0.3", "name": "curtain", "to": [0.95, 0.95], "dur": 0.0},      # S30 looks in through where the curtain is
    # L31: one glow, then out. L34: the second glow, held. L40: dark again.
    {"at": "L31.1", "name": "lamp", "to": GLOW, "dur": 0.3},
    {"at": "L31.1+0.34", "name": "lamp", "to": 0.0, "dur": 0.5},
    {"at": "L34", "name": "lamp", "to": GLOW, "dur": 0.45},
    {"at": "L40", "name": "lamp", "to": 0.0, "dur": 0.5},
    {"at": "L34", "name": "third", "on": True, "mode": "booth", "arm": "seam", "smile": "normal", "head": 0, "roll": 0},
    {"at": "L37", "name": "third", "head": 12, "pitch": 40, "roll": -5, "smile": "wide"},
    {"at": "L40", "name": "third", "on": False},
    {"at": "L31.1", "name": "curtain", "to": [0.0, 0.0], "dur": 0.0},
    {"at": "P06+0.12", "name": "curtain", "to": [1.0, 1.0], "dur": 0.16},
    {"at": "L41", "name": "lamp", "to": LAMP_REST, "dur": 0.4},
    # the table, the four strips laid in a row
    *[{"at": "L42", "name": "strip", "id": f"s{k + 1}", "on": True, "pos": [round(TX + (k - 1.5) * 0.215, 3), TY, 0.805], "rot": 0}
      for k in range(4)],
    {"at": "L44", "name": "curtain", "to": [0.95, 0.95], "dur": 0.0},
    # the hall: the middle lamp goes out, the Third stands in the dark, the pools of light close in, it fades
    {"at": "L47+0.4", "name": "midlamp", "to": 0.0, "dur": 0.3},
    {"at": "L47+0.4", "name": "pools", "on": True},
    {"at": "L47+0.4", "name": "nearlamp", "to": 0.35, "dur": 0.3},
    {"at": "L47+0.4", "name": "farlamp", "to": 0.35, "dur": 0.3},
    {"at": "L49", "name": "third", "on": True, "mode": "hall", "x": 9.0, "y": 0.0, "yaw": 90, "arm": "down", "smile": "normal",
     "head": 0, "roll": 0},
    {"at": "L53", "name": "third", "on": False},
    {"at": "L53", "name": "midlamp", "to": 1.0, "dur": 0.4},
    {"at": "L53", "name": "pools", "on": False},
    {"at": "L53", "name": "nearlamp", "to": 1.0, "dur": 0.4},
    {"at": "L53", "name": "farlamp", "to": 1.0, "dur": 0.4},
    # the last strip
    {"at": "L55", "name": "curtain", "to": [0.95, 0.95], "dur": 0.0},
    {"at": "L57", "name": "strip", "id": "s5", "on": True, "pos": [0, 0, 0]},
    *[{"at": "L59", "name": "strip", "id": f"s{k}", "on": False, "pos": [0, 0, 0]} for k in range(1, 5)],
    {"at": "L59", "name": "strip", "id": "s5a", "on": True, "pos": [round(TX - 0.2, 3), TY + 0.04, 0.804], "rot": -9, "flip": True},
    {"at": "L59", "name": "strip", "id": "s5b", "on": True, "pos": [9.06, -1.47, 0.804], "rot": 11, "flip": True},
    {"at": "L59.5", "name": "pocket", "on": True},
    {"at": "L59.5", "name": "strip", "id": "s5a", "on": False, "pos": [0, 0, 0]},
]
# the dark pool: the strips in `stage` shots are placed by set.py; `s5` is only ever an insert


def early(ref, d=0.017):
    """A time reference moved d seconds earlier (half a frame before a cut)."""
    import re as _re

    m = _re.match(r"^(.*?)([+-]\d+(?:\.\d+)?)?$", str(ref))
    base, off = m.group(1), float(m.group(2) or 0)
    off -= d
    return f"{base}{off:+.3f}"


# each shot's own light (set.py shot_look): on for exactly that shot's frames
WARM, COOL = "#ffb070", "#a9c0ff"
DARK = {"hall": 0.0, "fill": 0.0, "door": 0.0}
LOOKS = {
    "L15": {"key": [[BX - 2.0, 2.3, 2.2], [BX - 1.7, 4.6, 1.0], 70.0, 75, WARM]},
    "L31": {"hall": 0.1, "fill": 0.1, "door": 0.1},
    "L32": {**DARK, "key": [[BX - 1.2, 3.4, 1.9], [BX - 0.84, 4.6, 1.6], 4.0, 30, COOL]},
    "L33": {**DARK, "key": [[BX + 0.3, 3.5, 0.8], [BX, 4.7, 0.5], 1.2, 40, COOL]},
    "L34": {**DARK, "under": [[BX + 0.3, 3.4, 0.2], "hand", 18.0, 60, WARM]},
    "L35": {**DARK, "dome": 0.5, "under": [[BX + 0.35, 3.4, 0.25], "head", 4.0, 62, WARM],
            "third_rim": [[BX - 1.1, 3.6, 2.4], "head", 40.0, 45, COOL]},
    "L36": {**DARK, "under": [[BX + 0.35, 3.5, 0.9], "hand", 30.0, 38, WARM]},
    "L37": {**DARK, "under": [[BX + 0.3, 3.5, 0.5], "head", 16.0, 55, WARM],
            "third_rim": [[BX - 1.0, 3.6, 2.7], "head", 70.0, 40, COOL]},
    "L38": {**DARK, "under": [[BX - 0.1, 3.3, 0.3], [BX + 0.84, 4.6, 1.5], 14.0, 60, WARM]},
    "L39": {**DARK, "under": [[BX - 1.0, 3.7, 0.3], [BX, 4.742, 1.4], 10.0, 70, WARM],
            "key": [[BX - 1.6, 3.5, 2.3], [BX + 1.0, 4.3, 1.2], 45.0, 70, WARM],
            "key2": [[BX - 2.0, 4.0, 2.6], [BX - 0.87, 4.6, 1.4], 40.0, 50, WARM]},
    "L22": {"key": [[BX + 2.0, 2.3, 1.6], [BX + 1.25, 4.2, 1.2], 30.0, 50, WARM]},
    "L59": {"hall": 0.4},
    "L59.5": {"hall": 0.55},
    "L40": {"hall": 1.0, "fill": 1.0},
    "L47": {},
    "L49": {"third_rim": [[12.2, -1.0, 2.4], [9.0, 0.0, 1.7], 140.0, 24, COOL], "hall": 1.0,
            },
    "L50": {"third_rim": [[7.0, -1.0, 2.4], [9.0, 0.0, 1.7], 100.0, 26, COOL]},
    "L51": {"third_rim": [[11.0, -1.0, 2.4], [9.0, 0.0, 1.7], 70.0, 26, COOL]},
    "L52": {"third_rim": [[12.2, -1.0, 2.4], [9.0, 0.0, 1.7], 30.0, 24, COOL]},
}
for at, look in LOOKS.items():
    i = [a for a, _, _ in SH].index(at)
    nxt = SH[i + 1][0]
    cues.append({"at": early(at), "name": "shot", "look": look})
    cues.append({"at": early(nxt), "name": "shot", "look": None})

# the fx: a flash is never white and never a hard cut (the booth lamp is the flash risk)
fx = [
    {"at": "L35", "kind": "punch", "dur": 0.7, "zoom": 1.1, "fade": 0.15},
    {"at": "L37", "kind": "punch", "dur": 0.7, "zoom": 1.08, "fade": 0.15},
    {"at": "P06+0.12", "kind": "shake", "dur": 0.4, "amp": 0.4},
]

sfx = [
    # the lamp's glow: a soft electric hum and a rising whine for each of the four
    *[{"at": f"L11+{0.05 + 0.8 * k:.2f}", "kind": "riser", "db": -24, "dur": 0.7} for k in range(4)],
    {"at": "L11.4", "kind": "whoosh", "db": -22},
    {"at": "L11.4+0.1", "kind": "click", "db": -16},
    {"at": "L02+0.1", "kind": "whoosh", "db": -26},
    {"at": "L28+0.25", "kind": "creak", "db": -16, "dur": 0.5},
    {"at": "L28.2", "kind": "click", "db": -9},
    {"at": "L28.2+0.25", "kind": "click", "db": -9},
    {"at": "L31.1", "kind": "riser", "db": -20, "dur": 0.7},
    {"at": "L33", "kind": "whoosh", "db": -14, "dur": 0.25},
    {"at": "L34", "kind": "riser", "db": -16, "dur": 0.9},
    {"at": "L35", "kind": "sting", "db": -9, "dur": 2.4},
    {"at": "L37", "kind": "hit", "db": -14},
    {"at": "L40", "kind": "thud", "db": -14},
    {"at": "P06+0.12", "kind": "whoosh", "db": -14},
    {"at": "L47+0.4", "kind": "thud", "db": -16},
    {"at": "L49", "kind": "sting", "db": -13, "dur": 2.0},
    {"at": "L21", "kind": "whoosh", "db": -26},
    {"at": "L60>-0.1", "kind": "whoosh", "db": -15, "dur": 0.4},
]
for k in range(1, 3):
    sfx.append({"at": f"L{57}.{k}", "kind": "click", "db": -40})
sfx = [s for s in sfx if s["db"] > -39]

story = {
    "slug": "ep20-photo-strip",
    "title": "Who keeps standing between us in our photos?",
    "made_for_kids": False,
    "premise": "At a cousin's hotel wedding, two adult sisters who haven't spoken in two years are asked by their mum for one photo of the two of them from the old coin booth in the hall, sitting in the middle, together. They sit at opposite ends of the bench every time, and every strip that comes out has a faded brown hand on the velvet between their heads.",
    "twist": "The figure behind them never moved: its hand is on the same seam, at the same height, in every frame. The sisters were sliding further apart each strip, and every inch they gave it showed more of it. The opening line, 'It's getting closer', first reads as the thing coming for them and, after the last line, as the sister saying it about the two of them, warmly.",
    "world": "A long hotel hall on a wedding night with bottle-green walls, a dark patterned carpet, three brass lamps, a muffled waltz behind a closed ballroom door, and in an alcove an old wooden coin photo booth with a plum velvet curtain, a long bench and one seam down the back velvet.",
    "key_color": "#ffc04a",
    "gap": 0.12,
    "tail": 0.28,
    "look": {"fog": "#1c1a24", "fog_density": 0.02, "fog_start": 8.0, "sky": "#0a0a10", "sky_strength": 1.0, "exposure": 0.9},
    "grade": {"shadows": [0.03, -0.01, 0.03], "highlights": [0.05, 0.015, -0.04], "saturation": 1.0, "contrast": 1.08,
              "vignette": 0.42, "bloom": 0.3, "grain": 0.014, "red_line": 0.79, "red_lift_blue": 0.5},
    "phonemes": {"But": "bˈʌt"},
    "cast": cast,
    "lines": lines,
    "shots": shots,
    "hide": hides,
    "stage": stages,
    "acting": acting,
    "cues": cues,
    "fx": fx,
    "music": {"root": 50, "mode": "major", "bpm": 72, "seed": 20,
              "sections": [
                  {"at": 0, "voices": ["pad"], "energy": 0.3},
                  {"at": "L05", "voices": ["pad", "piano"], "energy": 0.35},
                  {"at": "L12", "voices": ["drone", "pad"], "energy": 0.35, "mode": "dorian"},
                  {"at": "L18", "voices": ["drone", "pad", "piano"], "energy": 0.4, "mode": "dorian"},
                  {"at": "L23", "voices": ["drone", "pad", "pulse"], "energy": 0.55, "mode": "minor"},
                  {"at": "L28", "voices": ["drone", "pad"], "energy": 0.3, "mode": "minor"},
                  {"at": "L31", "voices": ["drone"], "energy": 0.2, "mode": "minor"},
                  {"at": "L35+0.5", "voices": ["drone", "choir", "pulse"], "energy": 0.7, "mode": "minor"},
                  {"at": "L41", "voices": ["drone", "pad"], "energy": 0.4, "mode": "minor"},
                  {"at": "L44", "voices": ["drone", "pad", "piano"], "energy": 0.5, "mode": "dorian"},
                  {"at": "L49", "voices": ["drone", "choir"], "energy": 0.55, "mode": "minor"},
                  # from L55 the waltz comes back clean and brighter, the drone gone
                  {"at": "L53", "voices": ["pad", "piano"], "energy": 0.45, "mode": "major"},
                  {"at": "L55", "voices": ["pad", "piano", "pulse"], "energy": 0.6, "mode": "major"},
              ]},
    "sound": {"floor": "wood", "steps_db": -22,
              "ambience": [
                  {"kind": "room", "from": 0, "to": "end", "lufs": -38},
                  {"kind": "hum", "from": 0, "to": "L31", "lufs": -40},
                  {"kind": "hum", "from": "L34", "to": "L40", "lufs": -30},
                  {"kind": "drone", "from": "L49", "to": "L53", "lufs": -34},
              ],
              "sfx": sfx,
              # the music, the room and the steps drop before each scare, and the sting lands in the hole
              "music_drops": [
                  {"from": "L30>-0.1", "to": "L31.1"},
                  {"from": "L35-0.62", "to": "L35", "keep": ["sting"]},
                  {"from": "L49-0.62", "to": "L49", "keep": ["sting"]},
              ]},
}
OUT.write_text(json.dumps(story, indent=1, ensure_ascii=False) + "\n")
print("wrote", OUT, f"({len(shots)} shots)")
