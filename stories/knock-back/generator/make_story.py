"""Writes ../story.json for ep12 "When the floor knocks, knock back" (script 02b, revised 2026-10-30 for note 18).

Run from anywhere: python stories/knock-back/generator/make_story.py
The words are in lines.json next to this file. Everything else is here: the cast, the shots, the acting, the cues
set.py reads, the effects, the score and the sound. Shot ids are numbered in order (S01, S02, ...). A shot's tags
mark it as outside (fog, the yard) or drawn on ones.

Places (set.py's coordinates): the kitchen floor is z = 0; the front door is at x = -1.25 on the front wall
(y = -3.2); the cellar door is x -0.6..1.2, y -0.15..0.95; the worn pale board runs along y at x = -0.7, dished
at y = -0.25; the one wide gap is at x = -1.025; the bulb hangs at (-0.35, -0.1, 1.98); the stove is against the
left wall at (-2.3, -1.55); the table is at (-1.75, 0.3). Outside, the porch is the front wall's side, the yard
0.62 m below the floor.
"""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE.parent / "story.json"
lines = json.loads((HERE / "lines.json").read_text())

import math

YARD = -0.62
SIT_Z, KNEEL_Z = -0.04, -0.5
ME_KNEEL = [-0.51, -0.69, KNEEL_Z]       # kneeling facing +y: my right knee and right fist land on the pale board
ME_CHAIR = [-1.75, 1.3, SIT_Z]           # the far end of the table, facing -y
RAY_CHAIR = [-1.05, -0.3, SIT_Z]         # beside the pale board, facing +y
ME_STOVE = [-1.82, -1.55, 0.0]           # pressed against the stove, facing the room (+x)
ME_KNEEL2 = [-1.75, -1.42, KNEEL_Z]      # kneeling by the stove, facing +x (P09)
DIP = [-0.72, -0.25, 0.03]               # the dished middle of the pale board, where the knuckles go
FACE_Z = -0.53                           # its head under the boards: the face just under the joists
DOOR = [-1.25, -3.2]
PORCH = -5.1
H_STAND, H_SIT, H_KNEEL = 1.56, 1.5, 1.05   # face heights


def front(hd, yaw, off=0.0, dist=1.0, dz=0.0, lens=32, push=0.0, lens2=None, aim_dz=0.0):
    """A camera in front of a face: hd the face's centre, yaw the way the person faces (0 = -y), off degrees
    round from straight on, dist metres away; push moves it in by that much over the shot."""
    a = math.radians(yaw + off)
    d = (math.sin(a), -math.cos(a))
    p0 = [round(hd[0] + d[0] * dist, 3), round(hd[1] + d[1] * dist, 3), round(hd[2] + dz, 3)]
    tg = [hd[0], hd[1], round(hd[2] + aim_dz, 3)]
    if not push and not lens2:
        return c([0, p0, tg, lens])
    p1 = [round(hd[0] + d[0] * (dist - push), 3), round(hd[1] + d[1] * (dist - push), 3), round(hd[2] + dz, 3)]
    return c([0, p0, tg, lens], [1, p1, tg, lens2 or lens])


# One voice for everyone (owner, 2026-10-30): voice A reads every line, and Ray's words are reported by the
# narrator. Nobody has a voice of their own.
cast = {
    "me": {"age": "adult", "skin": "#f0c7a6", "shirt": "#c2582a", "pattern": "plaid", "pattern_c": "#efe2c6",
           "collar": "#a8471f", "pants": "#5d7aa0", "shoes": "#5a3a22", "sleeves": "short",
           "hair": "swoop", "hair_c": "#d7b46a", "hat": "none",
           "face": {"eyes": "round", "brows": True, "cheeks": "#e98d7a"}},
    "ray": {"age": "adult", "skin": "#7a4a2e", "shirt": "#3f6c9c", "pattern": "solid", "collar": "#36608c",
            "pants": "#b39a72", "shoes": "#3a281a", "sleeves": "short", "hair": "cap", "hair_c": "#8b8a86",
            "hat": "fedora", "hat_c": "#e2cf98", "band_c": "#6b4a2a", "width": 1.2,
            "face": {"eyes": "round", "brows": True, "ink": "#141010"}},
}


def c(*keys):
    return [list(k) for k in keys]


def mv(p0, t0, l0, p1=None, t1=None, l1=None):
    """A camera: one key, or a move from the first key to the second over the shot."""
    if p1 is None:
        return c([0, p0, t0, l0])
    return c([0, p0, t0, l0], [1, p1, t1 if t1 is not None else t0, l1 if l1 is not None else l0])


# ---------------------------------------------------------------------------------------------------- shots
# (at, camera, options). Options: step (1 = drawn on ones), hand (handheld drift), tags ["ext"] (outside: fog)
ME_K = [-0.51, -0.6, H_KNEEL]            # my face, kneeling upright on the pale board
ME_T = [-1.75, 1.3, H_SIT]               # my face at the table
RAY_T = [-1.05, -0.3, H_SIT]             # Ray's face at his chair
ME_S = [-1.82, -1.55, H_STAND]           # my face against the stove
RAY_D = [-1.25, -2.55, H_STAND]          # Ray at the front door, keys in hand
ME_D = [-0.1, -1.4, H_STAND]             # me by the table, watching him go
RAY_R = [-2.6, -6.9, YARD + H_STAND]     # Ray raking the trail at dawn
# cameras used by the shot list below (round 1)
GAP_X = -1.039                           # the wide gap's centre (9 cm across)
G1 = [GAP_X, -1.25]
G2 = [GAP_X, -1.25]
EYE_CAM = mv([GAP_X + 0.005, -1.42, 0.3], [GAP_X, -1.38, -0.3], 44, [GAP_X + 0.005, -1.41, 0.27], [GAP_X, -1.38, -0.3], 50)
EYE_CAM2 = mv([GAP_X + 0.06, -1.5, 0.36], [GAP_X + 0.01, -1.33, -0.3], 30, [GAP_X + 0.06, -1.49, 0.33], [GAP_X + 0.01, -1.33, -0.3], 33)
EYE_CAM3 = mv([GAP_X + 0.005, -0.9, 0.36], [GAP_X, -0.88, -0.3], 36, [GAP_X + 0.005, -0.895, 0.34], [GAP_X, -0.88, -0.3], 40)
BOARD_CAM = mv([-0.7, 0.75, 0.05], [-0.72, -0.4, 0.12], 22)
BOARD_CAM2 = mv([-0.95, 0.55, 0.06], [-0.66, -0.5, 0.1], 20)
CRAB_CAM = mv([0.3, -1.75, 1.5], [0.3, -1.15, 0.05], 16, [0.3, -1.72, 1.46], [0.3, -1.18, 0.05], 16)   # r3: eyes clear the caption
CRAB_CAM2 = mv([0.3, -2.05, 0.16], [0.3, -0.8, 0.2], 15, [0.3, -2.0, 0.16], [0.3, -0.8, 0.2], 15)
FACE_CAM = mv([0.3, -2.25, 0.9], [0.3, -1.35, 0.18], 26, [0.3, -2.18, 0.88], [0.3, -1.35, 0.18], 28)   # r3: the neck stump in on top
PAST_CAM = mv([0.6, -0.4, 1.7], [-1.15, -2.0, -0.05], 22)   # round 3: tilted down, my face out of frame (R6, audience)
DOOR_CAM = mv([-1.25, -1.15, 1.25], [-1.25, -3.2, 0.95], 22, [-1.25, -1.3, 1.25], [-1.25, -3.2, 0.98], 24)   # r3: eyes clear
# round 3: the hook on the pale board; the hand's knuckles on the board by my boot (board level); my fist meeting the
# boards with its hand clear; its face sinking into the cellar opening, looking up at the lens
HOOK_CAM = mv([-0.42, 0.95, 0.26], [-0.72, -0.4, 0.5], 17, [-0.43, 0.88, 0.26], [-0.72, -0.4, 0.52], 17)
HAND_CAM = mv([-1.22, -2.65, 0.32], [-1.6, -1.55, 0.0], 30)
KNOCK_CAM = mv([0.25, -0.05, 0.55], [-1.05, -0.9, 0.0], 20)
SINK_CAM = mv([0.3, -0.6, 1.8], [0.3, -0.55, -0.4], 22, [0.3, -0.43, 1.52], [0.3, -0.36, -0.45], 23)
RAY_WARM_CAM = mv([0.6, -0.95, 0.3], [-0.75, -0.62, 0.72], 30, [0.57, -0.94, 0.3], [-0.75, -0.62, 0.72], 32)
SH = [
    # ---- 01 the rule. The hook (round 1, P7): floor level on the pale board, the bulb swinging at the top of the
    # frame, the board jumping on "KNOCKS". Nobody in it. Then me, knocking back
    (0, HOOK_CAM, {"hand": 0.004}),
    ("P01", mv([-0.25, 1.0, 0.14], [-0.6, -0.55, 0.78], 15, [-0.27, 0.92, 0.14], [-0.6, -0.55, 0.8], 16), {"hand": 0.006}),
    ("L02", mv([-0.74, 0.05, 0.8], [-0.72, -0.32, 0.0], 26, [-0.74, 0.02, 0.72], [-0.72, -0.32, 0.0], 29), {}),
    ("L03", mv([-0.15, -2.6, 0.18], [0.3, 0.4, 0.05], 22, [0.0, -1.8, 0.2], [0.3, 0.4, 0.05], 22), {}),
    # the bolt, seen from below through the crack
    ("L04", mv([0.12, 0.3, -0.28], [0.4, -0.07, -0.075], 24, [0.14, 0.27, -0.27], [0.4, -0.07, -0.075], 27), {}),
    ("L05", mv([0.45, -0.55, 2.1], [0.3, 0.4, 0.0], 24, [0.45, -0.35, 1.8], [0.3, 0.4, 0.0], 26), {}),
    # summer days in the yard; Ray to camera, talking
    ("L06", mv([8.8, -16.5, 1.3], [1.5, -6.0, 1.0], 24, [8.2, -16.0, 1.3], [1.5, -6.0, 1.0], 25), {"tags": ["ext"]}),
    ("L07", front([3.8, -8.4, YARD + H_STAND], 0, 0, 1.45, -0.05, 32, push=0.1), {"tags": ["ext"]}),
    # the worn pale board, then close on its dip (a pale knuckle shows in the gap for a few frames: the rewatch clue)
    ("L09", mv([0.05, -1.7, 0.65], [-0.7, -0.2, 0.0], 24, [-0.2, -1.35, 0.5], [-0.7, -0.2, 0.0], 26), {}),
    ("L10", mv([-0.42, -0.72, 0.2], [-0.72, -0.25, 0.0], 30, [-0.45, -0.68, 0.15], [-0.72, -0.25, 0.0], 34), {}),
    ("L11", front(ME_T, 0, 15, 1.3, -0.02, 34, push=0.08), {}),
    ("L12", front(RAY_T, 180, -20, 1.3, -0.04, 32, push=0.08), {}),
    # ---- 02 summer nights. The house in fog, its warm window, the crickets loud
    ("L15", mv([-8.6, 7.5, 0.6], [-2.8, 2.2, 1.0], 26, [-8.2, 7.0, 0.6], [-2.8, 2.2, 1.0], 27), {"tags": ["ext"]}),
    ("L16", mv([0.45, 1.95, 1.95], [-1.5, 0.3, 0.8], 22, [0.4, 1.85, 1.9], [-1.5, 0.3, 0.8], 23), {}),
    ("L18", mv([-0.6, -0.9, 1.55], [-0.35, -0.1, 2.0], 34), {"hand": 0.002}),
    ("P02", mv([-0.4, -1.5, 0.12], [-0.4, 0.2, 1.4], 18), {"step": 1}),
    ("L19", front(RAY_T, 180, -30, 1.25, 0.2, 30, aim_dz=-0.3), {}),
    # Ray's hand hanging off his chair onto the pale board, at table height, his plate in frame (P8)
    ("P03", front(RAY_T, 180, -70, 1.9, -0.75, 22, aim_dz=-0.7), {"step": 1}),
    ("L20", mv([-6.0, 4.6, 0.5], [-2.8, 2.2, 1.3], 28, [-5.7, 4.3, 0.5], [-2.8, 2.2, 1.3], 30), {"tags": ["ext"]}),
    ("L21", mv([0.9, -1.6, 0.55], [-1.2, 0.4, 0.75], 20, [0.8, -1.5, 0.53], [-1.2, 0.4, 0.75], 21), {}),
    ("L24", front(RAY_T, 180, 35, 1.3, -0.5, 24, aim_dz=-0.45), {}),
    # dawn: the drag trail overhead (the main trail shot), low along it, its end under the window; Ray's rake
    ("L25", mv([-0.5, -12.6, 7.6], [1.2, -7.1, -0.6], 20, [-0.4, -12.3, 7.3], [1.2, -7.1, -0.6], 21),
     {"tags": ["ext"], "fog": 0.12}),
    ("L26.1", mv([0.6, -8.6, 0.6], [6.0, -6.9, -0.62], 22, [0.8, -8.5, 0.56], [6.4, -6.9, -0.62], 22),
     {"tags": ["ext"], "fog": 0.3}),
    ("L28", mv([-6.2, 0.6, -0.2], [-2.9, 2.2, 0.4], 24, [-6.0, 0.8, -0.2], [-2.9, 2.2, 0.6], 25), {"tags": ["ext"], "fog": 0.3}),
    ("L29", mv([-1.2, -8.5, 0.95], [-2.6, -6.9, 0.4], 26, [-1.3, -8.4, 0.95], [-2.6, -6.9, 0.4], 28), {"tags": ["ext"], "fog": 0.3}),
    ("L30.1", front(RAY_R, 90, -25, 1.35, -0.03, 34), {"tags": ["ext"], "hand": 0.003}),
    ("L31", front([-0.75, -4.85, H_STAND], 0, 10, 1.3, -0.03, 34, push=0.06), {"tags": ["ext"]}),
    # late night: down for water, the gap, red going past under it, then the eye (high in the frame, clear of the
    # caption)
    ("L32", mv([0.9, -2.5, 1.6], [-0.8, 0.0, 0.8], 22), {}),
    ("L33", mv([-0.35, -2.35, 1.55], [GAP_X, -1.25, 0.0], 26, [-0.4, -2.25, 1.45], [GAP_X, -1.25, 0.0], 29), {}),
    ("L34", mv([GAP_X + 0.01, -1.42, 0.4], [GAP_X, -1.22, -0.5], 32), {"hand": 0.002, "step": 1}),
    ("L35", EYE_CAM, {"hand": 0.0015, "step": 1}),
    # ---- 03 Ray leaves
    ("L37", mv([0.55, -3.0, 1.45], [-0.7, -2.0, 1.3], 22, [0.45, -2.95, 1.45], [-0.7, -2.0, 1.3], 23), {}),
    ("L39", front(ME_D, -45, 0, 1.25, -0.02, 34), {}),
    ("L40", front(RAY_D, 135, 10, 1.25, -0.03, 34, push=0.1), {}),
    ("L42", mv([-0.9, -4.6, 1.35], [5.2, -15.0, 0.4], 26), {"tags": ["ext"]}),
    ("L43", mv([2.2, 2.6, 2.1], [-0.4, -1.2, 0.5], 18, [2.1, 2.5, 2.05], [-0.4, -1.2, 0.5], 19), {}),
    # ---- 04 the knock I can't answer
    ("L45", mv([-0.1, 2.35, 1.8], [-0.1, 3.2, 1.85], 34, [-0.1, 2.45, 1.82], [-0.1, 3.2, 1.85], 40), {}),
    ("P04", mv([0.5, -1.4, 0.14], [-0.3, -0.1, 1.3], 18), {"step": 1}),
    ("L46", mv([0.2, 0.75, 1.35], [-0.55, -0.6, 0.6], 22, [0.15, 0.65, 1.3], [-0.55, -0.6, 0.6], 23), {}),
    ("P05", mv([-0.3, -0.02, 0.25], [-0.72, -0.27, 0.05], 28), {"step": 1}),
    ("L47", front(ME_K, 180, 0, 1.15, 0.0, 32), {}),
    ("P06", mv([0.5, -1.8, 0.2], [-0.5, 0.0, 1.2], 17), {"step": 1, "hand": 0.01}),
    # floor level on the pale board: dust jumping out of the gaps on each knock (P8)
    ("P06+0.8", BOARD_CAM, {"step": 1, "hand": 0.008}),
    ("L48", front(ME_K, 180, 20, 1.1, 0.0, 34), {"step": 1, "hand": 0.006}),
    ("L49", mv([0.4, -0.6, 1.3], [-0.35, -0.1, 2.1], 22), {"step": 1, "hand": 0.006}),
    ("L50", BOARD_CAM2, {"step": 1, "hand": 0.006}),
    ("L51", mv([0.35, 0.25, 1.2], [-0.6, -0.55, 1.25], 18), {"hand": 0.004}),
    ("L52", front(ME_K, 180, -15, 1.15, 0.0, 36, push=0.12, lens2=40), {}),
    ("L53", mv([1.9, 2.4, 2.0], [-0.6, -1.0, 0.4], 18), {}),
    ("L54", mv([-1.1, -0.3, 1.35], [-1.25, -3.2, 1.25], 24, [-1.15, -1.5, 1.35], [-1.25, -3.2, 1.35], 30), {}),
    # over my shoulder toward the front door (P8: not the same face as L48 and L52)
    ("L56", mv([0.05, 0.3, 1.65], [-1.25, -3.2, 1.1], 30, [0.0, 0.2, 1.64], [-1.25, -3.2, 1.1], 32), {}),
    ("L57", mv([-1.15, -1.95, 1.45], [-1.25, -3.2, 1.45], 26, [-1.15, -2.05, 1.45], [-1.25, -3.2, 1.45], 28), {}),
    ("L59", EYE_CAM2, {"step": 1, "hand": 0.002}),
    # ---- 05 it comes up
    ("L60", mv([0.12, 0.3, -0.28], [0.45, -0.07, -0.075], 25, [0.14, 0.27, -0.27], [0.45, -0.07, -0.075], 28), {}),
    ("L61", mv([0.85, -1.25, 0.16], [0.95, -0.12, 0.12], 34, [0.86, -1.15, 0.16], [0.95, -0.12, 0.14], 38), {}),
    ("L62", mv([0.3, -0.85, 2.2], [0.3, -0.729, 1.207], 17, [0.3, -0.83, 2.1], [0.3, -0.6, 1.1], 21), {"step": 1}),
    # the crab, restaged (P2): floor level a metre in front as it crawls at the lens, limbs past both edges; then
    # low from the side for "far too wide and flat"
    ("L63", CRAB_CAM, {"hand": 0.003}),
    ("L64.2", CRAB_CAM2, {"hand": 0.003}),
    ("L66", FACE_CAM, {}),
    ("L68", front(ME_S, 90, 0, 1.15, -0.02, 34, push=0.12, lens2=38), {"hand": 0.004}),
    # from the far side at floor level (P2): my boots, the clear floor between us and all of it in one frame
    ("L69", PAST_CAM, {"step": 1}),
    ("L70", mv([-0.2, -0.9, 1.2], [-1.25, -3.0, 0.9], 22, [-0.3, -1.0, 1.25], [-1.25, -3.1, 1.1], 22), {"step": 1}),
    ("L71", DOOR_CAM, {}),
    ("L74", front(ME_S, 90, 15, 1.15, -0.02, 34), {}),
    ("L74.2", mv([-0.6, -1.4, 1.2], [-1.25, -3.0, 0.8], 24), {"step": 1}),
    ("L75", HAND_CAM, {}),
    ("L76", front(ME_S, 90, -10, 1.1, -0.02, 36), {}),
    ("L77", KNOCK_CAM, {"step": 1}),
    ("L78", SINK_CAM, {}),
    ("L79", mv([0.12, 0.3, -0.28], [0.42, -0.07, -0.075], 27), {}),
    # ---- 06 morning, and the last night. The trail up the steps carries "FRONT DOOR" (L83's shot is gone)
    ("L80", mv([5.5, -13.5, 1.0], [0.0, -5.0, 0.6], 24, [5.2, -13.0, 1.0], [0.0, -5.0, 0.6], 25), {"tags": ["ext"]}),
    ("L81", mv([0.2, -9.6, 3.6], [-1.25, -5.4, -0.3], 22, [0.0, -9.0, 3.4], [-1.25, -5.2, -0.2], 22),
     {"tags": ["ext"], "fog": 0.3}),
    ("L84", mv([-0.9, 1.0, 1.55], [-1.95, 2.35, 1.5], 30, [-0.95, 1.05, 1.55], [-1.95, 2.35, 1.5], 33), {}),
    # Ray's smirk under the brim (P5): a low camera in front of his face
    ("L86a", RAY_WARM_CAM, {}),
    # the warm turn shown (P5): that night, me at the board under the bulb, knocking first; then S34's floor-gap
    # camera, and its eye, still, looking up at me in warm light
    ("L86c", mv([0.9, 1.6, 1.3], [-0.65, -0.45, 0.45], 24, [0.86, 1.55, 1.27], [-0.65, -0.45, 0.45], 25), {}),
    ("L86c.2", EYE_CAM3, {"hand": 0.0015}),
    ("L87", mv([1.9, 2.4, 2.0], [-0.6, -1.0, 0.4], 18, [1.8, 2.3, 1.95], [-0.6, -1.0, 0.4], 19), {}),
    ("L88", mv([-0.3, -0.02, 0.25], [-0.72, -0.27, 0.05], 28), {}),
    ("L89", mv([-1.0, -0.4, 1.35], [-1.25, -3.2, 1.45], 24, [-1.15, -1.9, 1.4], [-1.25, -3.2, 1.45], 30), {}),
]

shots, ext, fog_gain = [], [], {}
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
    if "fog" in opt:
        fog_gain[sid] = opt["fog"]
SID = {at: s["id"] for (at, _, _), s in zip(SH, shots)}

# ---------------------------------------------------------------------------------------------------- acting


def jump(at, frm, to, **kw):
    """A move on a cut: two keys at the same moment, so nobody walks (or clatters) on film."""
    return [{"at": at, "pos": frm}, {"at": at, "pos": to, "blend": 0.0, **kw}]


def kneel(at, pos, **kw):
    return {"at": at, "pos": pos, "kneel": True, "sit": False, **kw}


def sit(at, pos, **kw):
    return {"at": at, "pos": pos, "sit": True, "kneel": False, **kw}


def talk(who_keys, frm, to, amt=0.7):
    who_keys.append({"from": frm, "to": to, "mouth": [amt, amt], "flap": True})


UP = dict(bend=10, arms=[6, 10], side=[0, 0])                 # kneeling upright, hands on my thighs
KNOCK = dict(bend=48, arms=[6, 48], side=[0, -30])            # bent to the board, my right fist over the dip


def knocks(at, back):
    """Bend to the board for a knock and come back up after it."""
    return [{"at": f"{at}-0.35", **UP, "blend": 0.0}, {"at": at, **KNOCK, "blend": 0.3},
            {"at": back, **KNOCK, "blend": 0.0}, {"at": f"{back}+0.35", **UP, "blend": 0.35}]


me = [
    # the hook is the empty floor: I'm not in it, and come in on the cut to P01
    kneel(0, ME_KNEEL, yaw=180, lean=0, expr="neutral", head=[0, -18], look=[0, -0.6], blend=0.0, tremble=0.0,
          hidden=True, **UP),
    {"at": "P01", "hidden": False},
    *knocks("P01", "P01>"),
    {"at": "L02", "pos": ME_KNEEL},
    # summer days: in the yard with Ray
    *jump("L06", ME_KNEEL, [4.4, -9.0, YARD], yaw=-20, kneel=False, arms=[0, 0], side=[0, 0], bend=0, head=[0, 0],
          look=[0, 0]),
    {"at": "L06>", "pos": [4.4, -9.0, YARD], "yaw": -20},
    # supper: at the far end of the table
    *jump("L09", [4.4, -9.0, YARD], ME_CHAIR, yaw=0, sit=True, arms=[42, 42], expr="neutral"),
    {"at": "L11", "expr": "worried", "head": [10, -4], "look": [0.3, -0.1]},
    {"at": "L12", "expr": "neutral", "head": [0, 0], "look": [0, 0]},
    {"at": "L16.3", "expr": "worried", "look": [0, -0.4]},
    {"at": "L20", "expr": "neutral", "look": [0, 0]},
    {"at": "L21", "expr": "worried", "head": [0, -14], "look": [0, -0.8]},
    {"at": "L24", "expr": "neutral", "head": [0, 0], "look": [0, 0]},
    # dawn on the porch, not buying it
    *jump("L25", ME_CHAIR, [-0.75, -4.85, 0.0], yaw=0, sit=False, arms=[0, 0], expr="neutral", head=[0, 0]),
    {"at": "L31", "pos": [-0.75, -4.85, 0.0], "expr": "smirk", "yaw": 0, "look": [0, 0]},
    # late one night, down for water, and stopping by the gap
    *jump("L32", [-0.75, -4.85, 0.0], [1.9, 0.6, 0.0], expr="neutral", look=[0, 0]),
    {"at": "L32.2", "pos": [0.4, -0.7, 0.0]},
    {"at": "L33", "pos": [-1.35, -1.7, 0.0]},
    {"at": "L33.1", "pos": [-1.35, -1.7, 0.0], "yaw": 144, "head": [0, -30], "look": [0, -1], "expr": "worried"},
    {"at": "L35", "expr": "wide"},
    {"at": "L36", "expr": "scared"},
    # August: Ray at the door, me by the table
    *jump("L37", [-1.35, -1.7, 0.0], [-0.1, -1.4, 0.0], yaw=-45, expr="neutral", head=[0, 0], look=[0, 0]),
    {"at": "L40", "expr": "worried"},
    *jump("L42", [-0.1, -1.4, 0.0], [0.2, -4.75, 0.0], yaw=160, expr="worried"),
    *jump("L43", [0.2, -4.75, 0.0], [-0.4, -1.2, 0.0], yaw=200, expr="worried"),
    # midnight: kneeling on the pale board
    *jump("L45", [-0.4, -1.2, 0.0], ME_KNEEL, kneel=True, yaw=180, head=[0, -12], look=[0, -0.4], expr="worried", **UP),
    *knocks("P05", "P05>"),
    {"at": "L47", "expr": "scared", "head": [0, 0], "look": [0, 0]},
    {"at": "L48", "expr": "terrified", "tremble": 1.4},
    {"at": "L51", "bend": 22, "arms": [6, 120], "side": [0, -12], "blend": 0.35},       # my fist up, frozen
    {"at": "L53", "tremble": 0.0, **UP, "blend": 0.5},
    {"at": "L54", "head": [-35, 0], "look": [-0.7, 0], "expr": "terrified", "blend": 0.4},
    {"at": "L59", "head": [0, -25], "look": [0, -0.9], "tremble": 1.0},
    # it comes up: I'm against the stove (moved on the cut to the bolt)
    *jump("L60", ME_KNEEL, ME_STOVE, kneel=False, yaw=90, arms=[0, 0], side=[0, 0], bend=0, head=[0, 0],
          look=[0.2, 0], expr="terrified", tremble=1.2),
    {"at": "L68", "expr": "squeeze", "tremble": 1.8, "head": [-15, 8]},
    {"at": "L74", "expr": "terrified", "tremble": 0.6, "head": [-30, 0], "look": [-0.6, 0]},
    {"at": "L75", "head": [0, -30], "look": [0, -1]},
    *jump("L77", ME_STOVE, ME_KNEEL2, kneel=True, yaw=90, head=[0, -20], look=[0, -0.6], expr="worried", tremble=0.0,
          **UP),
    *knocks("P09", "P09>"),
    {"at": "L78", "head": [20, -6], "look": [0.5, -0.2]},
    # morning: on the porch with Ray, then at the table
    *jump("L80", ME_KNEEL2, [-0.5, -4.6, 0.0], kneel=False, yaw=-30, arms=[0, 0], side=[0, 0], bend=0, head=[0, 0],
          look=[0, 0], expr="worried"),
    *jump("L84", [-0.5, -4.6, 0.0], ME_CHAIR, sit=True, yaw=0, arms=[42, 42], expr="neutral"),
    # that night: I knock first, at the pale board, and look down at the gap for its answer
    *jump("L86c", ME_CHAIR, ME_KNEEL, sit=False, kneel=True, yaw=180, head=[0, -18], look=[0, -0.6], expr="neutral",
          **UP),
    *knocks("L86c.1", "L86c.1>"),
    {"at": "L86c.2", "head": [-30, -30], "look": [-0.7, -0.8], "expr": "smirk", "blend": 0.4},
    {"at": "L87", "head": [0, -18], "look": [0, -0.6], "expr": "neutral", "blend": 0.0},
    *knocks("L88", "L88>"),
    {"at": "L89", "head": [-40, 0], "look": [-0.8, 0], "expr": "worried", "blend": 0.5},
]
# Ray: warm (smirk), attentive (neutral) or worried. The grin only where the words say it: L24 "with a GRIN",
# and before L40 "he stopped GRINNING" (standards' advisory, round 1)
ray = [
    sit(0, RAY_CHAIR, yaw=180, arms=[38, 30], side=[0, 0], bend=0, lean=0, tremble=0.0, expr="smirk", head=[0, -10],
        look=[0, -0.3], hidden=True),
    # the yard: by the truck, talking to me (to camera)
    *jump("L06", RAY_CHAIR, [3.8, -8.4, YARD], hidden=False, sit=False, yaw=0, arms=[0, 0], head=[0, 0], expr="smirk"),
    *jump("L09", [3.8, -8.4, YARD], RAY_CHAIR, sit=True, yaw=180, arms=[38, 30], expr="smirk", head=[0, 0]),
    {"at": "L12", "expr": "smirk", "head": [-25, 0], "look": [-0.4, 0.1]},
    {"at": "L12.3", "expr": "neutral", "head": [-20, 0], "look": [-0.4, 0.1]},
    {"at": "L15", "head": [0, -16], "look": [0, -0.6], "expr": "neutral"},
    {"at": "L24", "expr": "grin"},
    {"at": "L25", "expr": "neutral"},
    # dawn: raking the trail over
    *jump("L25", RAY_CHAIR, [-2.6, -6.9, YARD], sit=False, yaw=90, arms=[0, 0], head=[0, -20], expr="neutral"),
    {"at": "L30", "head": [-20, 0], "look": [0, 0], "expr": "blank"},
    {"at": "L31", "head": [0, 0]},
    # off till sunrise
    *jump("L32", [-2.6, -6.9, YARD], [-2.6, -6.9, YARD], hidden=True),
    *jump("L37", [-2.6, -6.9, YARD], [-1.25, -2.55, 0.0], hidden=False, yaw=135, expr="grin", head=[0, 0],
          look=[0, 0], arms=[0, 25]),
    {"at": "L40.1", "expr": "worried", "arms": [0, 0]},
    *jump("L42", [-1.25, -2.55, 0.0], [-1.25, -2.55, 0.0], hidden=True),
    # sunrise: on the porch, looking down at the trail up the steps
    *jump("L80", [-1.25, -2.55, 0.0], [-1.45, -4.9, 0.0], hidden=False, yaw=0, expr="worried", head=[0, -26],
          look=[0, -0.8], arms=[0, 0]),
    # the kitchen: by the window, then softer, his hands on the worn board, his face up to me
    *jump("L84", [-1.45, -4.9, 0.0], [-1.95, 2.35, 0.0], yaw=11, expr="worried", head=[0, 0], look=[0, 0]),
    *jump("L86a", [-1.95, 2.35, 0.0], [-1.1, -0.62, KNEEL_Z], kneel=True, yaw=90, arms=[44, 44], side=[-18, -18],
          bend=42, expr="smirk", head=[0, 22], look=[0.4, 0.2]),
    *jump("L86c", [-1.1, -0.62, KNEEL_Z], [-1.1, -0.62, KNEEL_Z], hidden=True),
]
# Ray's mouth moves under the words the narrator reports
talk(ray, "L07.1", "L07.1>")
talk(ray, "L12.1", "L12.4>")
talk(ray, "L30.1", "L30.1>")
talk(ray, "L41.1", "L41.4>")
talk(ray, "L84.1", "L84.3>")
talk(ray, "L85", "L86>")
talk(ray, "L86a", "L86b>", 0.5)
acting = {"me": me, "ray": ray}

# ---------------------------------------------------------------------------------------------------- cues


def kp(at, pose, **kw):
    return {"at": at, "name": "keeper", "pose": pose, **kw}


KNOCK2 = [0.0, 0.2]                      # knock-knock
NIGHT2 = [0.0, 0.62, 0.84]               # knock... knock-knock (night two, and the front door at P07)
FAST = [0.0, 0.14, 0.28, 0.52, 0.76, 0.9, 1.04, 1.18, 1.42, 1.56]   # knock-knock-knock, knock, knock x4, knock-knock
CLUE_HEAD = [GAP_X + 0.47, -0.45 + 1.333, FACE_Z]   # under the floor, so its right hand reaches up into the gap
BOLT_HAND = [0.47, -0.07, -0.16]            # its fingers on the bolt's knob, from below
PASS_END, PASS_H, PASS_ARM, PASS_LEG = [-0.45, -2.65], 10, 30, 110   # the crawl past me (round 3, R6)
HAND_AT, HAND, HAND_BACK = [-0.1, -1.7], [-1.525, -1.53, 0.07], [-0.5, -2.3, 0.04]   # by my boot (round 3)
SINK_END = [0.25, -0.2]   # S69 (round 3): it sinks only to just under the lip, its face still on the lens
HOOK_JUMP = 0.045
HOOK_LOOK = {"bulb": 0.2, "fill": 0.05, "bounce": 0.15, "night": 1.6,
             "key": [[-0.45, 0.75, 0.55], [-0.7, -0.3, 0.0], 16.0, 28]}
DOOR_FOOT = {"start": PASS_END, "heading": PASS_H, "arm": PASS_ARM, "leg": PASS_LEG}

cues = [
    {"at": 0, "name": "time", "time": "night"},
    {"at": 0, "name": "clock", "h": 8, "m": 40},
    {"at": 0, "name": "keeper", "pose": "hidden"},
    {"at": 0, "name": "trail", "a": False, "b": False},
    {"at": 0, "name": "hat", "on": "ray"},
    # the hook: the bulb already swinging, two knocks from below under "KNOCKS", the board jumps; then my fist
    {"at": 0, "name": "swing", "amp": 0.16, "tau": 4.0},
    # round 3 (critic 5): a big jump on "KNOCKS", a few cm and held a beat, with dust kicking out of its gaps
    {"at": "L01.3", "name": "knock_below", "pattern": KNOCK2, "amp": 0.12, "board": True, "jump": HOOK_JUMP,
     "fall": 0.2},
    {"at": "L01.3", "name": "dust", "dur": 1.2},
    {"at": "L01.3", "name": "puff", "dur": 1.1, "height": 0.16},
    # the hook's own light: the room behind cooler and darker, a low key on the pale board
    {"at": 0, "name": "shot", "look": HOOK_LOOK},
    {"at": "P01-0.017", "name": "shot", "look": None},
    {"at": "P01+0.1", "name": "fist", "pattern": KNOCK2},
    {"at": "L06", "name": "time", "time": "day"}, {"at": "L06", "name": "truck", "state": "parked"},
    {"at": "L09", "name": "time", "time": "night"},
    # the rewatch clue: a pale knuckle in the gap for a few frames, on "KNUCKLES"
    kp("L09.3-0.05", "under", head_at=CLUE_HEAD, heading=90, face=[CLUE_HEAD[0], CLUE_HEAD[1], 1.0],
       hand_r=[GAP_X, -0.45, -0.03]),
    kp("L09.3+0.17", "hidden"),
    {"at": "L15", "name": "supper", "on": True},
    {"at": "P02", "name": "knock_below", "pattern": KNOCK2, "amp": 0.16, "board": True},
    {"at": "L21", "name": "supper", "on": False},
    {"at": "P03-0.4", "name": "arm_to", "who": "ray", "arm": -1, "to": [-0.72, -0.27, 0.02], "pattern": KNOCK2,
     "knock_at": 0.5},
    {"at": "L20", "name": "arm_to", "who": "ray", "to": None},
    {"at": "L24", "name": "arm_to", "who": "ray", "arm": -1, "to": [-0.72, -0.27, 0.02], "pattern": NIGHT2,
     "knock_at": 0.05},
    {"at": "L25", "name": "arm_to", "who": "ray", "to": None},
    {"at": "L23", "name": "knock_below", "pattern": [0.0], "amp": 0.1, "board": True},
    {"at": "L23.1", "name": "knock_below", "pattern": KNOCK2, "amp": 0.1, "board": True},
    {"at": "L25", "name": "time", "time": "dawn"}, {"at": "L25", "name": "trail", "a": True},
    {"at": "L29+0.6", "name": "rake", "on": True}, {"at": "L32", "name": "rake", "on": False},
    {"at": "L30", "name": "trail", "a": False},
    {"at": "L32", "name": "time", "time": "night"}, {"at": "L32", "name": "clock", "h": 1, "m": 20},
    # the glimpse: red sliding past under the gap, then its face under it, one eye in the gap
    kp("L34", "under", head_at=[G1[0], 1.2, FACE_Z], face="cam"),
    kp("L34>", "under", head_at=[G1[0], -2.6, FACE_Z], face="cam", glide=True),
    kp("L35", "under", head_at=[GAP_X + 0.06, G1[1], FACE_Z], face=[GAP_X, G1[1], 1.0]),
    kp("L36+0.25", "hidden"),
    {"at": "L37", "name": "time", "time": "dusk"}, {"at": "L37", "name": "clock", "h": 7, "m": 15},
    {"at": "L42", "name": "time", "time": "night"}, {"at": "L42", "name": "truck", "state": "go"},
    {"at": "L42", "name": "hat", "on": "hook"},
    {"at": "L43", "name": "truck", "state": "gone"},
    # midnight: the minute hand ticks onto twelve, on the word
    {"at": "L45", "name": "clock", "h": 11, "m": 59},
    {"at": "L45.0+0.35", "name": "clock", "h": 0, "m": 0},
    {"at": "P04", "name": "knock_below", "pattern": KNOCK2, "amp": 0.16, "board": True},
    {"at": "P05+0.1", "name": "fist", "pattern": KNOCK2},
    {"at": "P06", "name": "knock_below", "pattern": FAST, "amp": 0.11, "board": True},   # calmed for the flash bar (Q2)
    {"at": "P06", "name": "dust", "dur": 3.6},
    {"at": "L49", "name": "swing", "amp": 0.6, "tau": 1.6},   # still hits the beam; calmed for the flash bar (Q2)
    {"at": "L50", "name": "dust", "dur": 3.0},
    {"at": "L50.2", "name": "knock_below", "pattern": [0.0, 0.3], "amp": 0.1, "board": True},
    # the visitor: the soft shadow on the frosted glass, crossing in about 1.5 s, feeling for the handle
    {"at": "L57", "name": "shadow", "on": True, "x": 1.1, "dur": 0.0},
    {"at": "L57.1", "name": "shadow", "x": 0.0, "dur": 1.5},
    {"at": "L58.2", "name": "shadow", "x": 0.42, "dur": 0.8},
    {"at": "L59", "name": "shadow", "on": False},
    kp("L59", "under", head_at=[GAP_X + 0.06, G2[1], FACE_Z], face=[GAP_X, G2[1], 1.0]),
    # it comes up: the bolt from below (its fingers on it), the door on its knuckles, the reveal, the crawl, the door
    kp("L60", "rise", neck=[0.42, -0.62], slope=50, face=[0.3, -0.2, 0.0], hand_r=BOLT_HAND,
       hand_l=[0.0, 0.3, -0.9]),
    {"at": "L60.1", "name": "bolt", "open": True, "dur": 0.45},
    kp("L61", "rise", neck=[0.1, -0.35], slope=50, face="cam", hand_l=[0.95, -0.1, 0.14], hand_r=[-0.3, 0.2, -0.3]),
    {"at": "L61.1", "name": "trapdoor", "open": 0.2, "dur": 0.7},
    kp("L62", "rise", neck=[0.12, -0.32], slope=48, face="cam", up=[0.25, -1, 0], arm=-30),
    kp("L62>", "rise", neck=[-0.22, 0.34], slope=42, face="cam", up=[0.25, -1, 0], arm=-30, glide=True),
    {"at": "L62", "name": "trapdoor", "open": 1.0, "dur": 0.9},
    kp("L63", "crawl", where=[0.3, -0.5], heading=0, height=0.48, face="cam"),
    kp("L64>", "crawl", where=[0.3, -0.78], heading=0, height=0.48, face="cam", glide=True),
    kp("L66", "crawl", where=[0.3, -0.8], heading=0, height=0.48, face="cam"),
    kp("L68", "crawl", where=[0.3, -0.82], heading=0, height=0.48, face="me", glide=True),
    # round 3, R6: the crawl past me keeps clear floor between us. Its limbs tuck in (PASS_ARM, PASS_LEG) and it
    # ends at the door's foot further out from my boots, where the climb starts (S62) and ends (S65)
    kp("L69", "crawl", where=[0.3, -0.82], heading=-28, height=0.48, face="me", arm=PASS_ARM, leg=PASS_LEG),
    kp("L69>", "crawl", where=PASS_END, heading=PASS_H, height=0.48, face="me", arm=PASS_ARM, leg=PASS_LEG,
       glide=True),
    kp("L70", "door", climb=0.0, face="me", **DOOR_FOOT),
    kp("L70>", "door", climb=1.0, face="me", glide=True, **DOOR_FOOT),
    {"at": "L71", "name": "shadow", "on": True, "x": 0.15, "dur": 0.0},
    {"at": "L73.1", "name": "shadow", "x": 1.25, "dur": 1.5},
    {"at": "L74", "name": "shadow", "on": False},
    kp("L74.2", "door", climb=1.0, face="me", **DOOR_FOOT),
    kp("L75", "door", climb=0.0, face="me", glide=True, **DOOR_FOOT),
    # round 3 (critic 2, R6): its hand comes down steep, so the end with the four knuckles meets the board a few cm
    # from my boot and never my trouser leg; on my knock (S68) it draws the hand back off me
    kp("L75", "crawl", where=HAND_AT, heading=180, height=0.58, face="me", hand_l=HAND, lift=0.3),
    kp("L75.2", "crawl", where=HAND_AT, heading=180, height=0.58, face="me", hand_l=HAND, lift=0.0, glide=True),
    kp("L77", "crawl", where=[0.3, -1.8], heading=180, height=0.45, face="me", hand_l=HAND_BACK),
    {"at": "P08", "name": "keeper_knock", "pattern": KNOCK2, "side": 0},
    {"at": "P09+0.1", "name": "fist", "pattern": KNOCK2},
    kp("L78", "rise", neck=[-0.22, 0.34], slope=42, face="cam", arm=-30),   # r3: its face on the lens as it sinks
    kp("L79", "rise", neck=SINK_END, slope=46, face="me", arm=-30, glide=True),   # r3: sinks only to the lip
    {"at": "L78.3", "name": "trapdoor", "open": 0.0, "dur": 1.1},
    kp("L79", "rise", neck=[0.42, -0.62], slope=50, face=[0.3, -0.2, 0.0], hand_r=BOLT_HAND,
       hand_l=[0.0, 0.3, -0.9]),
    {"at": "L79.1", "name": "bolt", "open": False, "dur": 0.35},
    kp("L79>+0.2", "hidden"),
    {"at": "L79", "name": "settle"},
    # morning
    {"at": "L80", "name": "time", "time": "dawn"}, {"at": "L80", "name": "truck", "state": "parked"},
    {"at": "L80", "name": "trail", "b": True}, {"at": "L80", "name": "hat", "on": "ray"},
    {"at": "L84", "name": "time", "time": "day"}, {"at": "L84", "name": "trail", "b": False},
    # that night: my knock first, its soft answer, its eye in the gap looking up at me
    {"at": "L86c", "name": "time", "time": "night"}, {"at": "L86c", "name": "hat", "on": "hook"},
    {"at": "L86c.1", "name": "fist", "pattern": KNOCK2},
    {"at": "L86c.2-0.4", "name": "knock_below", "pattern": KNOCK2, "amp": 0.04},
    kp("L86c", "under", head_at=[GAP_X + 0.06, -0.79, FACE_Z], face=[GAP_X, -0.79, 1.0]),
    kp("L87", "hidden"),
    {"at": "L87>+0.5", "name": "knock_below", "pattern": KNOCK2, "amp": 0.12, "board": True},
    {"at": "L88+0.1", "name": "fist", "pattern": KNOCK2},
]

# each shot's own light (set.py shot_look): on for exactly that shot's frames. The keeper's keys are a cool
# near-white (round 1, P3), so its crimson reads red and its skin pale, not yellow
COOL = "#f0f2f8"
UNDER_EYE = {"bulb": 0.6, "under": [[GAP_X + 0.12, -1.38, -0.2], "face", 3.0, 50, COOL]}
BOLT_LIGHT = {"under": [[0.62, 0.12, -0.3], [0.42, -0.07, -0.1], 26.0, 60]}   # warm, faint, under the floor
LOOKS = {
    "L04": {"under": [[0.62, 0.12, -0.24], [0.4, -0.07, -0.08], 4.0, 60]},
    "L45": {"key": [[0.25, 2.35, 1.45], [-0.1, 3.17, 1.85], 7.0, 22]},
    "L42": {"moon": 3.5},
    "P06+0.8": {"key": [[-0.4, 0.2, 0.6], [-0.72, -0.4, 0.05], 8.0, 40]},
    "L50": {"key": [[-0.4, 0.2, 0.6], [-0.72, -0.5, 0.05], 8.0, 40]},
    "L34": {"under": [[GAP_X + 0.2, -1.4, -0.2], [GAP_X, -1.25, -0.6], 5.0, 70, COOL]},
    "L35": UNDER_EYE,
    "L57": {"porch": 140.0, "bulb": 0.75},
    "L59": {"bulb": 0.6, "under": [[GAP_X + 0.12, -1.42, -0.2], "face", 3.0, 50, COOL]},
    "L60": BOLT_LIGHT,
    "L61": {"bulb": 0.7, "key": [[0.6, -1.0, 0.35], [0.95, -0.1, 0.1], 10.0, 30, COOL]},
    "L62": {"bulb": 0.22, "fill": 0.12, "key": [[0.05, -1.3, 0.9], "face", 9.0, 22, COOL]},
    "L63": {"bulb": 0.3, "fill": 0.25, "key": [[0.3, -1.9, 0.35], [0.3, -0.75, 0.3], 9.0, 70, COOL]},
    "L64.2": {"bulb": 0.3, "fill": 0.25, "key": [[0.9, -2.2, 0.15], [0.3, -0.8, 0.4], 9.0, 70, COOL]},
    "L66": {"bulb": 0.15, "fill": 0.1, "key": [[-0.35, -1.95, 0.08], "face", 3.5, 22, COOL]},
    "L69": {"bulb": 0.6, "key": [[0.5, -2.4, 0.9], "face", 8.0, 55, COOL]},
    "L70": {"bulb": 0.6, "key": [[-0.6, -1.4, 1.2], "face", 7.0, 40, COOL]},
    "L71": {"bulb": 0.18, "fill": 0.12, "porch": 140.0, "key": [[-0.95, -1.9, 0.35], "face", 4.0, 18, COOL]},
    "L74.2": {"key": [[-0.7, -1.5, 1.3], "face", 12.0, 30, COOL]},
    "L75": {"key": [[-1.2, -2.3, 0.45], [-1.52, -1.6, 0.06], 7.0, 30, COOL]},   # r3: on the knuckle side
    "L77": {"key": [[-0.9, -0.8, 0.8], [-1.4, -1.3, 0.1], 6.0, 40, COOL]},
    "L78": {"bulb": 0.15, "fill": 0.1, "key": [[0.3, -0.95, 0.75], "face", 3.0, 22, COOL]},   # r3: S53's low key
    "L79": BOLT_LIGHT,
    "L86c.2": {"under": [[GAP_X + 0.12, -0.92, -0.2], "face", 2.2, 50, "#ffd9b0"]},
}
def early(ref, d=0.017):
    """A time reference moved d seconds earlier (half a frame before a cut)."""
    import re as _re

    m = _re.match(r"^(.*?)([+-]\d+(?:\.\d+)?)?$", str(ref))
    base, off = m.group(1), float(m.group(2) or 0)
    off -= d
    return f"{base}{off:+.3f}"


for at, look in LOOKS.items():
    i = [a for a, _, _ in SH].index(at)
    nxt = SH[i + 1][0]
    cues.append({"at": early(at), "name": "shot", "look": look})
    cues.append({"at": early(nxt), "name": "shot", "look": None})

fx = [
    {"at": "L04.1", "kind": "punch", "dur": 0.9, "zoom": 1.1, "fade": 0.1},
    {"at": "L35", "kind": "punch", "dur": 0.8, "zoom": 1.12, "fade": 0.15},
    {"at": "P06", "kind": "shake", "dur": 1.5, "amp": 0.55},
    {"at": "L49.3", "kind": "shake", "dur": 0.35, "amp": 0.5},
    {"at": "L59.2", "kind": "punch", "dur": 0.9, "zoom": 1.1, "fade": 0.2},
    {"at": "L62.1", "kind": "punch", "dur": 0.7, "zoom": 1.08, "fade": 0.2},
    {"at": "L89>-0.18", "kind": "black", "dur": 60.0, "amp": 1.0},      # cut to black on "too"
]

CRACK = 1.5     # a short wooden crack on every knock from below, so it reads on a phone speaker (Q1)
sfx = [
    # the knocks, as the script's table writes them (sound.knock_hit tones)
    {"at": "L01.3", "kind": "knock", "pattern": KNOCK2, "tone": "below", "db": -4, "crack": 3.0},
    {"at": "P01+0.1", "kind": "knock", "pattern": KNOCK2, "tone": "hand", "db": -6},
    {"at": "P02", "kind": "knock", "pattern": KNOCK2, "tone": "below", "db": -4, "crack": CRACK},
    {"at": "P03+0.1", "kind": "knock", "pattern": KNOCK2, "tone": "hand", "db": -7},
    {"at": "L23", "kind": "knock", "pattern": [0.0], "tone": "below", "db": -7, "crack": CRACK},
    {"at": "L23.1", "kind": "knock", "pattern": KNOCK2, "tone": "below", "db": -7, "crack": CRACK},
    {"at": "L24+0.05", "kind": "knock", "pattern": NIGHT2, "tone": "hand", "db": -12},
    {"at": "P04", "kind": "knock", "pattern": KNOCK2, "tone": "below", "db": -4, "crack": CRACK},
    {"at": "P05+0.1", "kind": "knock", "pattern": KNOCK2, "tone": "hand", "db": -6},
    {"at": "P06", "kind": "knock", "pattern": FAST, "tone": "below", "db": -2, "crack": CRACK,
     "gains": [1, 0.8, 0.9, 1.1, 1, 0.85, 0.95, 1.1, 1, 0.9]},
    {"at": "P06", "kind": "hit", "db": -11},       # the music slams in under the fast knocks (P4)
    {"at": "L50.2", "kind": "knock", "pattern": [0.0, 0.3], "tone": "below", "db": -10, "crack": CRACK},
    {"at": "P07", "kind": "knock", "pattern": NIGHT2, "tone": "glass", "db": -4},
    {"at": "P08", "kind": "knock", "pattern": KNOCK2, "tone": "soft", "db": -5},
    {"at": "P09+0.1", "kind": "knock", "pattern": KNOCK2, "tone": "hand", "db": -9},
    {"at": "L86c.1", "kind": "knock", "pattern": KNOCK2, "tone": "hand", "db": -11},
    {"at": "L86c.2-0.4", "kind": "knock", "pattern": KNOCK2, "tone": "soft", "db": -9},
    {"at": "L87>+0.5", "kind": "knock", "pattern": KNOCK2, "tone": "below", "db": -6, "crack": CRACK},
    {"at": "L88+0.1", "kind": "knock", "pattern": KNOCK2, "tone": "hand", "db": -8},
    {"at": "L89>-0.3", "kind": "knock", "pattern": [0.0], "tone": "glass_soft", "db": -4},
    {"at": "P10+0.2", "kind": "knock", "pattern": [0.0], "tone": "glass_soft", "db": -4},
    # the bulb's cord creaks when it swings; it bumps the beam
    {"at": "0.3", "kind": "creak", "db": -30, "dur": 0.8},
    {"at": "P02+0.3", "kind": "creak", "db": -26, "dur": 0.8},
    {"at": "P04+0.3", "kind": "creak", "db": -26, "dur": 0.8},
    {"at": "P06+0.3", "kind": "creak", "db": -22, "dur": 1.2},
    {"at": "L49.3", "kind": "thud", "db": -12},
    {"at": "L49.3+0.02", "kind": "click", "db": -14},
    # the truck, the bolt, the cellar door, the keeper
    {"at": "L42", "kind": "whoosh", "db": -18},
    {"at": "L04.1", "kind": "click", "db": -16},
    {"at": "L60.1", "kind": "click", "db": -6, "keep": True},
    {"at": "L60.1+0.05", "kind": "creak", "db": -16, "dur": 0.45, "keep": True},
    {"at": "L61", "kind": "riser", "db": -16, "dur": 2.2},
    {"at": "L61.1", "kind": "creak", "db": -12, "dur": 1.1},
    {"at": "L62", "kind": "door", "db": -12},
    {"at": "L62.1", "kind": "sting", "db": -11, "dur": 2.6},
    {"at": "L63", "kind": "creak", "db": -16, "dur": 0.9},
    {"at": "L64.2", "kind": "creak", "db": -18, "dur": 0.8},
    {"at": "L69", "kind": "creak", "db": -14, "dur": 1.0},
    {"at": "L69.2", "kind": "creak", "db": -15, "dur": 0.9},
    {"at": "L70", "kind": "creak", "db": -13, "dur": 1.2},
    {"at": "L71", "kind": "thud", "db": -16},
    {"at": "L74.2", "kind": "creak", "db": -16, "dur": 1.2},
    {"at": "L78.1", "kind": "creak", "db": -15, "dur": 1.0},
    {"at": "L78.3", "kind": "door", "db": -12},
    {"at": "L79.1", "kind": "click", "db": -6},
    {"at": "L79.1+0.05", "kind": "creak", "db": -18, "dur": 0.35},
    {"at": "L80", "kind": "door", "db": -26},
]

story = {
    "slug": "ep12-knock-back",
    "title": "When the floor knocks, knock back",
    "made_for_kids": False,
    "premise": "A 19-year-old spends a summer helping talkative Uncle Ray on his farm. Some nights the kitchen floor knocks from below, and Ray always knocks back the same rhythm right away and laughs it off. The cellar door's bolt is on the cellar side.",
    "twist": "The thing under the floor is the house's guard and the knock is its warning. When the narrator can't answer, something outside knocks the rhythm it has been learning, and the keeper, a too-wide person crawling belly up with its face upside down, comes up and holds the front door shut. It knocks to check the family is still there. One night the narrator knocks first and it answers softly. The last night the floor knocks first again, and when the narrator answers, something outside knocks back too.",
    "world": "A farmhouse kitchen on a dry summer night: wide plank floor with gaps, a cellar door in the floor, one swinging tungsten bulb, a cast-iron stove, a front door with frosted glass, and a dusty yard in low fog under a big moon.",
    "key_color": "#ff4a3d",
    "key_stroke": 4,      # a thicker dark outline on the red key words over bright wood (round 1, P8)
    "gap": 0.12,
    "tail": 0,       # it cuts to black on "too", one more soft knock on black, then straight back to S01 (the knock loops into the opening knock)
    "look": {"fog": "#262b45", "fog_density": 0.06, "fog_start": 5.0, "sky": "#0a0c1c", "sky_strength": 1.0,
             "exposure": 0.55},
    "grade": {"shadows": [0.02, -0.01, -0.03], "highlights": [0.05, 0.02, -0.05], "saturation": 1.05,
              "contrast": 1.1, "vignette": 0.45, "bloom": 0.38, "grain": 0.012,
              "red_line": 0.79, "red_lift_blue": 0.5},   # under WCAG's saturated red (0.8): the warm grade would flash red on every cut
    # Whisper heard "copied" as "copped" and "one eye" as "when I": these spellings are heard right (and "One" with
    # a capital only matches L35's spoken text, so no other "one" changes)
    "phonemes": {"copied": "kˈɑpid", "One": "wˈʌn"},
    "exterior_shots": ext,
    "fog_gain": fog_gain,
    "cast": cast,
    "lines": lines,
    "shots": shots,
    "acting": acting,
    "cues": cues,
    "fx": fx,
    "music": {"root": 38, "mode": "harmonic", "bpm": 58, "seed": 12,
              "sections": [   # no piano, no music box
                  {"at": 0, "voices": ["drone", "pad"], "energy": 0.3},
                  {"at": "L06", "voices": ["pad"], "energy": 0.3},
                  {"at": "L09", "voices": ["drone", "pad"], "energy": 0.3},
                  {"at": "L25", "voices": ["pad"], "energy": 0.25},
                  {"at": "L32", "voices": ["drone"], "energy": 0.3},
                  {"at": "L37", "voices": ["drone", "pad"], "energy": 0.35},
                  {"at": "L45", "voices": ["drone", "pulse"], "energy": 0.5},
                  {"at": "L47", "voices": ["drone", "pad", "pulse"], "energy": 0.85},
                  # after the silence, held low through "from the FRONT DOOR, three KNOCKS" (P4)
                  {"at": "L53", "voices": ["drone"], "energy": 0.15},
                  {"at": "L56", "voices": ["drone", "pulse"], "energy": 0.55},
                  {"at": "L60", "voices": ["drone", "pad", "pulse"], "energy": 0.7},
                  {"at": "L62", "voices": ["drone", "choir", "pad"], "energy": 0.6},
                  {"at": "L68", "voices": ["drone", "choir", "pulse"], "energy": 0.75},
                  {"at": "L72", "voices": ["drone", "pad"], "energy": 0.4},
                  {"at": "L75", "voices": ["drone"], "energy": 0.2},
                  {"at": "L78", "voices": ["drone", "pad"], "energy": 0.35},
                  {"at": "L80", "voices": ["pad"], "energy": 0.3},
                  # the warm turn: the pad opens to the relative major, then back to the minor for the last night
                  {"at": "L86a", "voices": ["pad"], "energy": 0.35, "mode": "major", "root": 41},
                  {"at": "L87", "voices": ["drone", "pad"], "energy": 0.3},
              ]},
    "sound": {"floor": "wood", "steps_db": -24, "floors": {},
              "ambience": [
                  {"kind": "room", "from": 0, "to": "end", "lufs": -40},
                  # the crickets are the clock: loud, then gone before a knock, back after it's answered
                  {"kind": "crickets", "from": 0, "to": "L06", "lufs": -32},
                  {"kind": "wind", "from": "L06", "to": "L09", "lufs": -38},
                  {"kind": "crickets", "from": "L09", "to": "L16.3", "lufs": -31},
                  {"kind": "crickets", "from": "L20.1", "to": "L25", "lufs": -31},
                  {"kind": "wind", "from": "L25", "to": "L32", "lufs": -37},
                  {"kind": "crickets", "from": "L32", "to": "L34", "lufs": -36},
                  {"kind": "crickets", "from": "L37", "to": "L42", "lufs": -40},
                  {"kind": "crickets", "from": "L42", "to": "L45.2", "lufs": -28},
                  {"kind": "drone", "from": "L42", "to": "L43", "lufs": -34},
                  {"kind": "drone", "from": "L62", "to": "L79", "lufs": -36},       # its low hum while it's up
                  {"kind": "crickets", "from": "L74.2", "to": "L80", "lufs": -38},  # one by one
                  {"kind": "crickets", "from": "L74.3", "to": "L80", "lufs": -35},
                  {"kind": "crickets", "from": "P09>", "to": "L80", "lufs": -32},
                  {"kind": "wind", "from": "L80", "to": "L84", "lufs": -37},
                  {"kind": "crickets", "from": "L86c", "to": "end", "lufs": -30},
              ],
              "sfx": sfx,
              # every knock from below lands in silence: the music, the crickets and the rest drop half a beat
              # before it, and the knock plays through
              "music_drops": [
                  {"from": "L01.3-0.3", "to": "L01.3+0.45", "keep": ["knock"]},
                  {"from": "P02-0.3", "to": "P02>+0.1", "keep": ["knock"]},
                  {"from": "L23-0.3", "to": "L23>+0.1", "keep": ["knock"]},
                  {"from": "P04-0.56", "to": "P04>+0.1", "keep": ["knock"], "db": -70},
                  # P06 breaks the pattern: the hole lands before its first knock, then the run plays over the
                  # pulse with a hit under it, no drops between the fast knocks (P4)
                  {"from": "P06-0.56", "to": "P06-0.02", "keep": ["knock"], "db": -70},
                  # "Then, QUIET.": everything goes, pulse and crickets included, from the end of L52
                  {"from": "L52>-0.04", "to": "L53>+0.15", "db": -70},
                  # the front door's knock... knock-knock lands alone
                  {"from": "P07-0.46", "to": "P07>", "keep": ["knock"], "db": -70},
                  {"from": "L75", "to": "P09>", "keep": ["knock"]},
                  {"from": "L87>-0.04", "to": "L88", "keep": ["knock"], "db": -70},
                  {"from": "L89>-0.35", "to": "end", "keep": ["knock"]},
              ]},
}
OUT.write_text(json.dumps(story, indent=1, ensure_ascii=False) + "\n")
print("wrote", OUT, f"({len(shots)} shots)")
