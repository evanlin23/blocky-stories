"""Writes ../story.json for ep13 "Closing Time" (script 02b, revised 2026-10-30 for note 18 and ep12's carry-over).

Run from anywhere: python stories/closing-time/generator/make_story.py
The words are in lines.json next to this file. Everything else is here: the cast, the shots, the acting, the cues
set.py reads, the effects, the score and the sound. Shot ids are numbered in order (S01, S02, ...).

Places (set.py's coordinates): the hall's floor is z = 0 and the acrylic's inside face is y = 0, the hall behind it
(+y) and the tank in front (-y, the acrylic's tank face at y = -0.3, the sand at z = -1.2). The handrail is at
y = 0.45. Facing the glass is yaw 0. The corridor door is in the back wall (y = 6) at x = 5; the light switch is
just left of it at x = 4.05. The ceiling hatch is over (-2.2, 1.2). The Regular is 6 m wide; at the peak it's
pressed flat on the glass at x = -1.6, its eyes at z 2.0 .. 3.9.
"""
import json
import math
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE.parent / "story.json"
lines = json.loads((HERE / "lines.json").read_text())

GF = -0.3            # the acrylic's tank face
H_ME, H_ROSA, H_DEV = 1.55, 1.55, 1.71   # face heights


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


# One voice for everyone (owner, 2026-10-30): voice A reads every line, and Rosa's and Dev's words are reported by
# the narrator. Nobody has a voice of their own. All three wear the same plain charcoal tabard (set.py adds its
# back), no logo or text.
TAB = {"extras": ["apron"], "extra_c": "#34373d"}
cast = {
    "me": {"age": "adult", "skin": "#f2cfb2", "shirt": "#e6d9bf", "pattern": "knit", "pattern_c": "#c9b994",
           "collar": "#f6f4ee", "pants": "#1d1e22", "shoes": "#e9ecea", "sleeves": "long", "hair": "cap",
           "hair_c": "#9c3f1f", "hat": "none", **TAB,
           "face": {"eyes": "round", "brows": True, "ink": "#2b1810", "freckles": True}},
    "rosa": {"age": "adult", "skin": "#c39a6e", "shirt": "#6a2f55", "pattern": "knit", "pattern_c": "#4f2242",
             "collar": "#f2f0ea", "pants": "#6c6d71", "shoes": "#2a2a2c", "sleeves": "long", "hair": "spiky",
             "hair_c": "#c9ccd2", "hat": "none", "width": 1.1, **TAB,
             "face": {"eyes": "round", "brows": True, "ink": "#1a1416", "bags": True}},
    "dev": {"age": "adult", "skin": "#8a5a3a", "shirt": "#c41e24", "pattern": "solid", "collar": "#a8181d",
            "pants": "#3a3b40", "shoes": "#f0f0ee", "sleeves": "short", "hair": "buzz", "hair_c": "#e8d9a0",
            "hat": "none", "height": 1.1, **TAB,
            "face": {"eyes": "round", "brows": True, "ink": "#141010"}},
}

# ---------------------------------------------------------------------------------------------------- places
LINE = {"rosa": [-1.25, 1.05], "me": [0.0, 1.05], "dev": [1.3, 1.05]}           # the wave, at the rail
PEAK = {"rosa": [0.55, 1.2], "me": [-0.9, 1.15], "dev": [2.3, 2.5]}            # the show goes on
# lined up, and seen from the water. Round 2 (P3): a metre further right than round 1, so from the water the three
# sit clear of the Regular's back, which stays where it was pressed (x -1.6) and falls to the frame's left third
BOW = {"rosa": [1.6, 1.0], "me": [2.8, 1.0], "dev": [4.0, 1.0]}
# round 3 (standards R5): in the L71 bow shot only (S58) the line-up stands 0.35 m further back from the rail, so
# the 52-degree bow clears the rail tube and the heads stop short of the acrylic. It steps there on the cut into S58
# and back on the cut out of it, so no other shot changes
BOW_BACK = {k: [v[0], round(v[1] + 0.35, 3)] for k, v in BOW.items()}
REG_FAR = [0.6, -22.0, 2.5]
REG_MID = [0.2, -12.0, 2.6]
REG_NEAR = [-0.4, -9.0, 2.7]
REG_GLASS = [-1.6, -1.0, 2.95]                 # right up to it (not pressed)
REG_PRESS = [-1.6, -0.68, 2.95]                 # pressed flat: covering half the glass
REG_DRAG = [-1.6, -0.68, 2.5]                   # its whole front dragged down the glass
ME_AT_RAIL = [1.2, 0.95]                        # section 06: me alone at the rail
PUP_GLASS = [1.2, GF - 0.16, 1.6]
# section 06: the parent hangs behind and to the left of its pup, a little higher, so the pup has its own outline
# against the parent's bare right wing (no rows or mouth line behind it, P4)
REG_BEHIND = [-0.7, -1.75, 2.6]
# round 3 (critic, D1): after L84 both glide off into the blue. The parent goes further and out past the frame's left
# edge, so it fades first; the pup goes out and away as S69's camera turns after it, so it comes whole into the frame
# from the left edge (whole from about 1 s into L85) and its lit rows, still turned to me, are the last thing to go
REG_AWAY = [-8.0, -10.0, 3.4]                  # out of the frame's left edge into the blue by the cut
PUP_AWAY = [-4.5, -2.8, 2.2]
# S69's camera: key 1 at the end of L84 (S69_HOLD is where L84 ends in the shot: 132.445 s of 130.833 to 134.7 s; a
# retime has to move it), then a slow turn of PAN degrees into the tank by the cut
S69_HOLD = 0.417
PAN = 12.0
_f = (1.2 - 2.92, 0.1 - 0.58)
_a = math.radians(PAN)
S69_TURN = [round(2.92 + _f[0] * math.cos(_a) - _f[1] * math.sin(_a), 3),
            round(0.58 + _f[0] * math.sin(_a) + _f[1] * math.cos(_a), 3), 1.53]


def hd(p, h=H_ME):
    return [p[0], p[1], h]


def waist(p, h, bearing, dist=2.2, lens=38, dz=-0.1, aim_dz=-0.05, push=0.0):
    """Round 2 (P8): a waist-up shot from the hall side, the camera `bearing` degrees round from straight back
    into the hall (0 = +y), so the glass and the tank fill the frame behind whoever it's on."""
    a = math.radians(bearing)
    d = (math.sin(a), math.cos(a))
    p0 = [round(p[0] + d[0] * dist, 3), round(p[1] + d[1] * dist, 3), round(h + dz, 3)]
    tg = [p[0], p[1], round(h + aim_dz, 3)]
    if not push:
        return c([0, p0, tg, lens])
    p1 = [round(p[0] + d[0] * (dist - push), 3), round(p[1] + d[1] * (dist - push), 3), round(h + dz, 3)]
    return c([0, p0, tg, lens], [1, p1, tg, lens])


def facing(bearing, turn=0.0):
    """The yaw that faces a camera at `bearing` (waist()), turned `turn` degrees away from it."""
    return round(180.0 - bearing + turn, 1)


# ---------------------------------------------------------------------------------------------------- shots
# (at, camera, options). Options: step (1 = drawn on ones), hand (handheld drift), tank_fog / reg_fog / eye_fog /
# hall_fog (this shot's blue: thinner for far looks and the reveal; eye_fog keeps the rows out of the blue the
# outline sinks into), crowd_n / crowd_clear (fewer fish, none near the lens), dof [focus m, f-stop]
EYES_C = [-1.6, -0.55, 2.95]           # the middle of its eye rows at the peak
EYES_D = [-1.6, -0.55, 2.5]            # after the drag
# the rows whole, my head's edge in the foreground (P2: L50 to L51 and L73 to L74 share it)
ROWS_CAM = ([-1.25, 2.75, 2.05], [-1.62, -0.6, 2.62], 24)
REVEAL = {"tank_fog": 0.045, "reg_fog": 0.06, "hall_fog": 0.02, "crowd_n": 70, "crowd_clear": 7.0}
SH = [
    # ---- 01 the rule. The hook (P6): low behind the three of us, our raised hands in silhouette, a slow push and
    # zoom so the Regular grows out there, its shut rows lit a touch
    (0, c([0, [0.35, 0.55, 2.2], [0.5, -7.5, 2.45], 28], [1, [0.4, -0.15, 2.28], [0.5, -7.5, 2.5], 40]),
     {"hand": 0.003, "tank_fog": 0.045, "reg_fog": 0.04, "eye_fog": 0.02, "crowd_n": 80}),
    # the reverse, through the glass: my face, lit by the caustics
    ("L02", front(hd(LINE["me"]), 0, 8, 1.6, 0.0, 26, push=0.12), {"tank_fog": 0.05}),
    ("L03", mv([-6.4, 5.6, 4.3], [0.8, 0.7, 0.6], 15, [-6.2, 5.5, 4.2], [1.0, 0.7, 0.6], 15), {}),
    # low along the glass, then into the blue
    ("L04", mv([5.6, 0.95, 0.45], [-3.0, -0.6, 2.3], 17, [4.7, 0.95, 0.45], [-3.8, -0.6, 2.3], 17), {}),
    ("L04.2", mv([0.6, 1.3, 1.65], [0.2, -20.0, 2.2], 24, [0.6, 0.85, 1.65], [0.2, -20.0, 2.2], 26), {}),
    ("L07", front(hd(LINE["rosa"], H_ROSA), 0, -6, 1.7, 0.25, 24, push=0.1, aim_dz=0.2), {"tank_fog": 0.05}),
    ("L08", front(hd(LINE["dev"], H_DEV), 0, 10, 1.7, 0.0, 24, aim_dz=0.1), {"tank_fog": 0.05}),
    # the fish don't swim: the crowd hanging still, all pointed at us
    ("L09", mv([2.4, -1.2, 1.3], [-1.0, -8.0, 2.6], 22, [1.0, -1.4, 1.35], [-1.6, -8.0, 2.6], 22), {"tank_fog": 0.1}),
    # way out in the blue: a slow push past the crowd into the fog, to the rows hanging in the dark (P1 wide)
    ("L12", mv([0.3, -1.0, 2.0], [0.6, -22.0, 2.5], 30, [0.4, -4.5, 2.2], [0.6, -22.0, 2.5], 34),
     {"tank_fog": 0.11, "reg_fog": 0.08, "eye_fog": 0.03}),
    ("L14", front(hd(LINE["rosa"], H_ROSA), 0, 25, 1.35, 0.0, 30), {}),
    # ---- 02 night shifts. Looking down into the tank: over my shoulder at the rail, then low through the glass to
    # the benches, bigger and lit (P9)
    ("L17", mv([1.15, 1.35, 1.95], [-0.2, -4.5, -0.9], 24, [1.05, 1.25, 1.9], [-0.2, -4.5, -0.9], 26), {}),
    ("L18", mv([-0.55, 0.25, 0.42], [-1.9, -5.6, -0.7], 44, [-0.5, 0.22, 0.42], [-1.9, -5.6, -0.72], 50),
     {"tank_fog": 0.06}),
    ("L19.1", mv([-1.5, 2.0, 0.95], [-3.0, 3.1, 0.5], 24, [-1.6, 2.05, 0.92], [-3.0, 3.1, 0.5], 25), {}),
    ("L19.2", mv([-0.1, -9.6, -0.45], [-1.5, -5.6, -0.65], 34, [-0.1, -9.3, -0.45], [-1.5, -5.6, -0.65], 34),
     {"tank_fog": 0.05}),
    # who puts benches in a tank: waist-up, turned back to the room, the glass and the tank behind me (P8)
    ("L20", waist([0.3, 0.8], H_ME, 28, 2.8, 34, dz=-0.05, aim_dz=-0.2), {}),
    # the hatch: a tilt up to the ceiling, then close on it from below
    ("L21", mv([-1.4, 3.0, 1.55], [-2.2, 1.2, 2.4], 22, [-1.6, 2.4, 1.8], [-2.2, 1.2, 5.0], 26), {}),
    ("L23", mv([0.9, 3.2, 1.7], [-1.3, 1.0, 1.4], 24), {}),
    # Rosa turns from the rail to answer me: waist-up over my shoulder, the tank behind her (P8)
    ("L24", waist([-1.5, 0.8], H_ROSA, 22, 2.6, 34, dz=-0.05, aim_dz=-0.2), {}),
    # the morning wave, more crowded; then the Regular gliding closer, seen moving
    ("L26", mv([0.3, 5.0, 1.75], [0.0, -8.0, 2.1], 21, [0.3, 4.7, 1.75], [0.0, -8.0, 2.1], 21), {}),
    ("L27", mv([0.5, 1.25, 1.7], [0.3, -14.0, 2.6], 30), {"tank_fog": 0.1, "reg_fog": 0.06}),
    # close enough to see the slits: a long lens at the glass; then the close look at the shut lids
    ("L28", mv([0.4, 0.3, 2.3], [0.2, -12.0, 2.6], 70), {"tank_fog": 0.1, "reg_fog": 0.06}),
    ("L29", mv([0.4, 0.25, 2.5], [0.5, -11.8, 2.9], 150, [0.4, 0.25, 2.5], [0.5, -11.8, 2.75], 165),
     {"tank_fog": 0.08, "reg_fog": 0.03, "hand": 0.002}),
    # she never turned her back on that tank: Rosa wiping the rail, from behind her, the Regular out there
    ("L32", mv([-1.0, 3.8, 1.6], [-0.6, -6.0, 2.2], 22, [-1.0, 3.6, 1.6], [-0.6, -6.0, 2.2], 22), {"reg_fog": 0.08}),
    # ---- 03 Dev doesn't wave
    ("L33", mv([0.2, 4.6, 1.75], [0.0, -6.0, 2.0], 21), {"reg_fog": 0.08}),
    # his hand dropping, from behind him, the Regular out there (P8)
    ("L34", mv([1.75, 2.55, 1.95], [0.6, -7.0, 2.1], 28), {"reg_fog": 0.08}),
    # he turns his back on the tank to laugh at us: waist-up, the tank behind him (P8)
    ("L35", waist(LINE["dev"], H_DEV, -18, 2.7, 34, dz=-0.1, aim_dz=-0.25), {}),
    # the corridor: the caged light up a stop, the porthole door glowing (P9). One shot for L36 now
    ("L36", mv([-3.2, 1.7, 2.2], [4.8, 6.0, 1.2], 20, [-3.0, 1.9, 2.2], [5.0, 6.0, 1.2], 20), {}),
    # Rosa kept waving: from behind her, her hand up against the tank and the Regular in it (P8)
    ("L38", mv([-0.85, 2.45, 2.0], [-1.0, -7.0, 2.3], 28, [-0.85, 2.3, 2.0], [-1.0, -7.0, 2.3], 28), {"reg_fog": 0.07}),
    # her smirk was gone: the one full face, head and shoulders, wide enough for her silver crop (P8)
    ("L39", front(hd(LINE["rosa"], H_ROSA), 0, 0, 1.3, 0.04, 32, aim_dz=-0.08), {}),
    # behind the glass it glides right up to it (seen moving), past Rosa's shoulder
    ("L40", mv([-0.6, 2.4, 1.75], [-1.2, -4.0, 2.7], 22), {"reg_fog": 0.06}),
    # the crack insert (P2): tight on the two lids that crack, centred, one above the caption and one below
    ("L41", mv([-2.15, 0.8, 2.9], [-2.15, -0.75, 2.9], 27), {"hand": 0.002, "step": 1}),
    ("L42", mv([2.6, 4.2, 1.2], [-1.2, -0.5, 2.4], 18), {}),
    # ---- 04 the show goes on. Dev comes in down the corridor (clocking in, P9), too much light through the porthole
    ("L43", mv([5.0, 13.9, 1.6], [5.0, 6.1, 1.5], 26, [5.0, 13.3, 1.6], [5.0, 6.1, 1.5], 26), {}),
    ("L44", mv([6.2, 5.6, 4.4], [-1.0, 0.0, 1.0], 15), {}),
    ("L45", mv([2.9, 5.3, 1.65], [4.05, 6.0, 1.35], 28), {}),
    # the glass packed edge to edge (P1 wide: the outline into the blue, the rows the brightest shape)
    ("L46", mv([3.2, 4.6, 1.5], [0.4, -2.5, 2.4], 17, [3.0, 4.4, 1.5], [0.2, -2.5, 2.4], 17),
     {"reg_fog": 0.32, "eye_fog": 0.05}),
    # pressed flat: a low wide, the three of us small in front of it
    ("L48", mv([1.5, 5.4, 0.6], [-1.2, -0.4, 2.6], 16), {"reg_fog": 0.3, "eye_fog": 0.04}),
    ("L49", mv([1.6, 1.9, 2.4], [-4.6, -0.4, 2.9], 20, [1.6, 1.9, 2.4], [1.4, -0.4, 2.9], 20), {"glass_ior": 1.08}),
    # the lids opening one after another down both rows, whole in frame, my head's edge in the foreground (P2)
    ("L50", mv(*ROWS_CAM), {"hand": 0.002}),
    ("L52", mv([0.35, 0.95, 2.4], [-1.45, -0.4, 2.55], 24), {"glass_ior": 1.1}),
    # the creature test's frame: over my head, every eye on me
    ("L53", mv([-0.55, 3.15, 2.55], [-1.48, -0.4, 2.6], 18, [-0.55, 3.0, 2.55], [-1.48, -0.4, 2.6], 18), {}),
    # real ones: two eyes fill the frame
    ("L54", mv([-2.15, 0.6, 2.95], [-2.15, -0.6, 2.72], 21), {"hand": 0.0015}),
    # right at ME (P2): my eye line, every eye straight down the lens. It replaces my face shot, from "And they"
    ("L55", mv([-1.6, 1.7, 1.62], [-1.6, -0.55, 3.0], 16, [-1.6, 1.55, 1.62], [-1.6, -0.55, 3.0], 17),
     {"hand": 0.0025}),
    ("L56", front(hd(PEAK["dev"], H_DEV), 0, 20, 2.3, -0.25, 30, aim_dz=-0.45), {}),
    # its whole front dragging down the glass: a slow track along it
    ("L57", mv([0.3, 3.2, 2.4], [-1.7, -0.5, 2.15], 20, [0.25, 3.1, 2.2], [-1.7, -0.5, 1.7], 20), {}),
    # Rosa didn't flinch: waist-up from the side, the dragged-down rows beyond her (P8)
    ("L58", mv([2.35, 0.15, 1.65], [0.55, 1.2, 1.55], 28), {}),
    ("L59", mv([1.6, 2.6, 1.75], [-0.4, -0.4, 2.3], 22, [1.5, 2.4, 1.75], [-0.4, -0.4, 2.3], 22), {}),
    # ---- 05 curtain call. Push into the glass and through it, right of where it presses, and turn round
    ("L60", c([0, [3.9, 3.0, 1.9], [3.9, -6.0, 2.0], 22], [0.6, [3.9, -1.0, 2.2], [3.0, -9.0, 2.4], 22],
               [1, [3.6, -4.6, 2.6], [10.0, -5.0, 2.6], 22]), {"tank_fog": 0.06, "hall_fog": 0.0}),
    # the reveal (P3): from out in the blue, the box about 70% of the frame, the three lit in the middle of it and
    # the Regular's dark back at the left third; fewer, softer fish and none near the lens
    ("L60.3", mv([9.0, -15.4, 3.6], [1.3, 0.0, 2.3], 15.5, [8.7, -14.7, 3.5], [1.3, 0.0, 2.3], 15.5), dict(REVEAL)),
    ("L62", mv([-0.2, -9.6, -0.55], [1.9, 0.0, 1.4], 18, [0.0, -9.3, -0.5], [1.9, 0.0, 1.5], 18),
     {**REVEAL, "crowd_clear": 4.5}),
    # the hatch on the roof, its hinge and wheel rim-lit
    ("L63", mv([-3.4, -2.4, 7.6], [-2.2, 1.2, 5.5], 26, [-3.3, -2.3, 7.5], [-2.2, 1.2, 5.5], 28),
     {**REVEAL, "crowd_clear": 3.0}),
    ("L64", mv([3.6, -6.6, 2.0], [2.8, 1.0, 1.3], 30, [3.6, -6.2, 2.0], [2.8, 1.0, 1.3], 32),
     {**REVEAL, "crowd_clear": 3.5, "hall_fog": 0.015}),
    # the turn-round view held (2.0 s), the same framing as the reveal, drifting back
    ("P03", mv([8.8, -15.0, 3.6], [1.3, 0.0, 2.3], 15.5, [9.2, -15.8, 3.7], [1.3, 0.0, 2.3], 15.5), dict(REVEAL)),
    # WE were the EXHIBIT: the audience's view, from behind their benches (P3), held to the curtain call
    ("L65", mv([3.3, -8.6, -0.45], [2.6, 0.5, 1.1], 20, [3.2, -7.8, -0.4], [2.6, 0.5, 1.1], 21),
     {**REVEAL, "crowd_clear": 3.0}),
    # back inside, the filter closes: Rosa lines us up
    ("L68", mv([2.8, 4.6, 1.8], [2.8, -1.0, 1.6], 22), {}),
    # Dev, not grinning now: waist-up in the line-up, turned to Rosa, the tank behind him (P8)
    ("L69", waist(BOW["dev"], H_DEV, -40, 2.6, 34, dz=-0.1, aim_dz=-0.25), {}),
    # Rosa: wave, then bow. Waist-up, turned to us, the glass behind her (P8)
    ("L70", waist(BOW["rosa"], H_ROSA, 38, 2.6, 34, dz=-0.05, aim_dz=-0.2), {}),
    # the bow from the audience's seat (P9): from inside the tank through the glass, past the Regular's dark rim
    ("L71", mv([1.3, -3.6, 1.7], [2.9, 1.0, 1.15], 26, [1.35, -3.45, 1.7], [2.9, 1.0, 1.1], 26),
     {"tank_fog": 0.05, "reg_fog": 0.05, "hall_fog": 0.0, "crowd_n": 0, "dof": [4.9, 2.8]}),
    # the applause rolling along the glass from one end to the other
    ("P04", mv([5.9, 3.8, 1.5], [-3.0, -0.4, 2.0], 17), {}),
    # its eyes closing down the rows, whole in frame, the last one on me (P2: L73 to L74 in one framing)
    ("L73", mv([ROWS_CAM[0][0], ROWS_CAM[0][1], ROWS_CAM[0][2] - 0.4], [-1.62, -0.6, 2.2], 24), {"hand": 0.002}),
    ("L75", mv([1.7, 3.0, 1.7], [-1.6, -6.0, 2.4], 20), {"reg_fog": 0.08}),
    ("L76", mv([6.0, 5.6, 4.0], [-1.0, 0.0, 1.2], 15), {}),
    # ---- 06 closing time. Dev already at the glass, waving first (shown, not said, P9: clear enough to see)
    ("L78", mv([6.0, 4.4, 1.8], [2.6, -6.0, 1.8], 22, [5.9, 4.2, 1.8], [2.6, -6.0, 1.8], 23), {"reg_fog": 0.07}),
    ("L79", mv([1.3, 0.3, 1.8], [1.0, -6.0, 2.0], 30), {"reg_fog": 0.07, "tank_fog": 0.08}),
    ("L80", mv([-1.0, 2.2, 1.5], [1.2, -0.8, 1.8], 22, [-0.9, 2.0, 1.5], [1.2, -0.8, 1.8], 22), {}),
    # right up against my face (P4): over my shoulder, my head big in the foreground, the pup small at the glass
    # with its own outline, the parent behind it soft and dark
    ("L82", mv([1.72, 1.95, 1.72], [1.1, GF - 0.16, 1.58], 30), {"dof": [2.45, 2.2]}),
    ("L83", mv([1.62, 1.75, 1.66], [1.15, GF - 0.16, 1.6], 34), {"hand": 0.0015, "dof": [2.25, 2.2]}),
    # the hold ends on the cut to my face going soft: a chest-up two-shot, the pup's open eyes in frame (P4)
    ("L83c-0.5", mv([2.8, -1.3, 1.55], [1.05, 0.7, 1.5], 28, [2.75, -1.2, 1.55], [1.05, 0.7, 1.5], 28),
     {"tank_fog": 0.04, "crowd_n": 0, "dof": [2.75, 2.8]}),
    # the side view to the end (P4): me at the rail, the pup at the glass, the tiny bubbles between us; its eyes
    # follow my hand, then one small slow bow at its height
    # round 3 (D1): the side framing held to the end of L84 (S69_HOLD of the shot), then it turns slowly into the tank
    # after the pup as the two of them glide off, so the pup comes whole into the frame and stays clear of my head
    ("L84", c([0, [3.0, 0.58, 1.35], [1.2, 0.1, 1.55], 22], [S69_HOLD, [2.92, 0.58, 1.35], [1.2, 0.1, 1.53], 22],
              [1, [2.92, 0.58, 1.35], S69_TURN, 22]),
     {"glass_ior": 1.04, "reg_fog": 0.22, "eye_fog": 0.1}),
]

shots, LOOKS = [], {}
per_shot = {k: {} for k in ("tank_fog", "reg_fog", "eye_fog", "hall_fog", "crowd_n", "crowd_clear", "dof", "glass_ior")}
for i, (at, cam, opt) in enumerate(SH):
    sid = f"S{i + 1:02d}"
    s = {"id": sid, "cam": cam, "step": opt.get("step", 2)}
    if i:
        s["at"] = at
    if "hand" in opt:
        s["hand"] = opt["hand"]
    shots.append(s)
    for k, d in per_shot.items():
        if k in opt:
            d[sid] = opt[k]
SID = {at: s["id"] for (at, _, _), s in zip(SH, shots)}

# ---------------------------------------------------------------------------------------------------- acting


def jump(at, frm, to, **kw):
    """A move on a cut: two keys at the same moment, so nobody walks (or clatters) on film."""
    return [{"at": at, "pos": frm}, {"at": at, "pos": to, "blend": 0.0, **kw}]


def talk(keys, frm, to, amt=0.7):
    keys.append({"from": frm, "to": to, "mouth": [amt, amt], "flap": True})


WAVE_ME = dict(arms=[0, 150], side=[0, -8], wave=[0, 22])
WAVE_ROSA = dict(arms=[0, 165], side=[0, -4], wave=[0, 30])
WAVE_DEV = dict(arms=[0, 105], side=[0, -20], wave=[0, 9])
DOWN = dict(arms=[0, 0], side=[0, 0], wave=[0, 0])
BOWED = dict(bow=46, arms=[8, 8], side=[0, 0], wave=[0, 0])
UP = dict(bow=0)
MOPPING = dict(arms=[38, 42], side=[0, 0], mop=True)

me = [
    {"at": 0, "pos": LINE["me"], "yaw": 0, "expr": "neutral", "head": [0, 6], "bow": 0, "wipe": 0.0, **WAVE_ME},
    {"at": "L02", "pos": LINE["me"], "expr": "neutral"},
    {"at": "L03", "pos": LINE["me"], **DOWN, "blend": 0.5},
    {"at": "L04.2", "head": [0, 4]},
    {"at": "L10", "expr": "worried", "head": [0, 6]},
    # 02: my first week, at the rail looking down into the tank
    *jump("L17", LINE["me"], [0.3, 0.8], yaw=0, head=[0, -32], arms=[18, 18], expr="neutral"),
    # who puts benches in a tank: turned back to the room (to Rosa, behind the camera)
    {"at": "L20", "pos": [0.3, 0.8], "yaw": facing(28, 12), "expr": "worried", "head": [0, -4], "arms": [0, 0],
     "blend": 0.0},
    *jump("L21", [0.3, 0.8], [-0.8, 1.6], yaw=-150, head=[0, 30], expr="worried"),
    {"at": "L23", "pos": [-0.8, 1.6], "yaw": -110, "head": [0, 0], "expr": "neutral"},
    *jump("L26", [-0.8, 1.6], LINE["me"], yaw=0, expr="neutral", head=[0, 6], **WAVE_ME),
    {"at": "L27", **DOWN, "blend": 0.5, "expr": "worried"},
    {"at": "L32", "pos": LINE["me"]},
    *jump("L32", LINE["me"], [0.6, 2.5], yaw=-20, **MOPPING, expr="worried", head=[0, -15]),
    {"at": "L32.2", "pos": [0.9, 2.45]}, {"at": "L32>", "pos": [0.7, 2.4]},
    # 03: the Friday wave
    *jump("L33", [0.7, 2.4], LINE["me"], yaw=0, mop=False, expr="neutral", head=[0, 6], **WAVE_ME),
    {"at": "L35", "head": [35, 0], "expr": "worried"},
    {"at": "L36", "head": [55, 0]},
    {"at": "L38", "head": [-20, 0], "expr": "worried", **DOWN, "blend": 0.6},
    {"at": "L40", "head": [0, 6], "expr": "scared"},
    {"at": "L41", "expr": "wide"},
    {"at": "L42", "pos": LINE["me"]},
    # 04: Saturday
    *jump("L43", LINE["me"], PEAK["me"], yaw=0, expr="scared", head=[0, 12], **DOWN),
    {"at": "L44", "head": [20, 18]},
    {"at": "L46", "head": [0, 10], "expr": "scared"},
    {"at": "L50", "head": [0, 22], "expr": "wide", "blink": False},
    {"at": "L53", "head": [0, 24], "expr": "wide"},
    {"at": "L55", "head": [0, 20], "expr": "terrified", "tremble": 1.6},
    {"at": "L56", "head": [-30, 12]},
    {"at": "L57", "head": [0, 16], "tremble": 0.0, "expr": "terrified"},
    {"at": "L59", "head": [-35, 6], "blink": True, "expr": "scared"},
    # 05: seen from the water, lined up at the rail; the bow
    *jump("L60", PEAK["me"], BOW["me"], yaw=0, head=[0, 10], expr="scared"),
    {"at": "L68", "pos": BOW["me"], "head": [-30, 0]},
    {"at": "L70", "head": [-25, 0]},
    *jump("L71", BOW["me"], BOW_BACK["me"]),
    {"at": "L71", "head": [0, 6], **WAVE_ME, "expr": "scared"},
    {"at": "L71.1", **DOWN, **BOWED, "expr": "shut", "blend": 0.7},
    *jump("P04", BOW_BACK["me"], BOW["me"]),
    {"at": "P04+0.4", **UP, "blend": 0.9},
    {"at": "L72", "expr": "worried", "head": [0, 10]},
    {"at": "L74", "expr": "wide"},
    {"at": "L76", "expr": "worried"},
    {"at": "L76>", "pos": BOW["me"]},
    # 06: the next night: me alone at the rail with Dev waving beside
    *jump("L78", BOW["me"], ME_AT_RAIL, yaw=0, expr="neutral", head=[0, 6], **DOWN),
    {"at": "L82", "expr": "worried", "head": [0, 2]},
    {"at": "L83", "expr": "scared", "blink": False},
    # the cut to my face (P4): wide, then going soft, turned a little to the camera so the face reads
    {"at": "L83c-0.5", "expr": "wide", "head": [30, -4], "blend": 0.0},
    {"at": "L83c-0.12", "expr": "soft", "blink": True, "head": [28, -6], "blend": 0.5},
    # I waved, slowly, and its eyes followed my hand; then one small slow bow at its height (plainer than L71's)
    {"at": "L84", "head": [0, 0], "arms": [0, 140], "side": [0, -10], "wave": [0, 26], "wave_hz": 0.75,
     "expr": "soft", "blend": 0.35},
    {"at": "L84.2>", **DOWN, "blend": 0.6},
    # round 3 (critic): the last line is the creature's. I don't bow or wave back: I stand at the rail and my head
    # follows it out into the blue
    {"at": "L85", "head": [-18, 3], "expr": "soft", "blend": 1.6},
]

rosa = [
    {"at": 0, "pos": LINE["rosa"], "yaw": 0, "expr": "smirk", "head": [0, 8], "bow": 0, "wipe": 0.0, **WAVE_ROSA},
    {"at": "L02", "pos": LINE["rosa"]},
    {"at": "L08", **DOWN, "blend": 0.6},
    {"at": "L14", "head": [20, 0], "expr": "smirk"},
    *jump("L17", LINE["rosa"], [-1.5, 0.8], yaw=0, expr="smirk", head=[0, 0], **DOWN),
    {"at": "L23", "pos": [-1.5, 0.8], "arms": [45, 45], "wipe": 1.0, "blend": 0.3},
    # she turns from the rail to answer me (P8: the waist-up with the tank behind her)
    {"at": "L24", "pos": [-1.5, 0.8], "yaw": facing(22, -10), "arms": [0, 0], "wipe": 0.0, "head": [0, 0],
     "blend": 0.0},
    *jump("L26", [-1.5, 0.8], LINE["rosa"], yaw=0, head=[0, 8], wipe=0.0, **WAVE_ROSA),
    {"at": "L27", **DOWN, "blend": 0.6},
    *jump("L32", LINE["rosa"], [-1.4, 0.75], yaw=0, arms=[45, 45], wipe=1.0, head=[0, 0]),
    {"at": "L32>", "pos": [-1.4, 0.75]},
    *jump("L33", [-1.4, 0.75], LINE["rosa"], yaw=0, wipe=0.0, head=[0, 8], **WAVE_ROSA),
    {"at": "L35", "head": [40, 0], "expr": "neutral"},
    {"at": "L36.2", "head": [0, 8], "expr": "neutral"},
    # her smirk was gone: a flat straight mouth (P8), not the wavy worried one
    {"at": "L39", "expr": "blank"},
    {"at": "L42", **DOWN, "blend": 0.7, "expr": "worried"},
    # 04: the switch, then beside me at the glass
    *jump("L43", LINE["rosa"], [4.05, 5.45], yaw=180, expr="worried", head=[0, -4], **DOWN),
    {"at": "L45.1", "arms": [60, 75], "side": [0, 0]},
    {"at": "L45.2", "arms": [0, 0]},
    *jump("L46", [4.05, 5.45], PEAK["rosa"], yaw=0, expr="worried", head=[0, 12]),
    {"at": "L56", "head": [0, 12]},
    {"at": "L58", "expr": "blank", "head": [0, 14]},
    {"at": "L59", "expr": "blank"},
    *jump("L60", PEAK["rosa"], BOW["rosa"], yaw=0, expr="blank"),
    {"at": "L68", "pos": BOW["rosa"], "yaw": 30, "arms": [40, 40], "side": [0, 30]},
    {"at": "L69", "yaw": 0, "arms": [0, 0], "side": [0, 0]},
    # wave, then bow: turned to Dev and me (P8)
    {"at": "L70", "yaw": facing(38, -12), "blend": 0.0, "expr": "blank"},
    *jump("L71", BOW["rosa"], BOW_BACK["rosa"]),
    {"at": "L71", "yaw": 0, **WAVE_ROSA, "blend": 0.0},
    {"at": "L71.1", **DOWN, **BOWED, "blend": 0.7},
    *jump("P04", BOW_BACK["rosa"], BOW["rosa"]),
    {"at": "P04+0.4", **UP, "blend": 0.9},
    {"at": "L76>", "pos": BOW["rosa"]},
    {"at": "L78", "hidden": True},
]
talk(rosa, "L24.1", "L24.2>")
talk(rosa, "L59", "L59.1>")
talk(rosa, "L59.3", "L59.4>")
talk(rosa, "L70.1", "L70.2>")

dev = [
    {"at": 0, "pos": LINE["dev"], "yaw": 0, "expr": "grin", "head": [0, 8], "bow": 0, "wipe": 0.0, **WAVE_DEV},
    {"at": "L02", "pos": LINE["dev"]},
    {"at": "L09", **DOWN, "blend": 0.6},
    {"at": "L17", "hidden": True},
    {"at": "L26", "pos": LINE["dev"], "hidden": False, "yaw": 0, "expr": "grin", **WAVE_DEV},
    {"at": "L27", **DOWN, "blend": 0.6},
    {"at": "L32", "hidden": True},
    {"at": "L33", "pos": LINE["dev"], "hidden": False, "yaw": 0, "expr": "grin", **WAVE_DEV},
    {"at": "L34", **DOWN, "blend": 0.35},
    # he turns his back on the tank to laugh at us (P8)
    {"at": "L35", "pos": LINE["dev"], "yaw": facing(-18, 8), "expr": "grin", "head": [0, 4], "blend": 0.0},
    {"at": "L36", "pos": LINE["dev"]},
    {"at": "L36.1", "pos": [3.6, 4.0]},
    {"at": "L36.2", "pos": [5.0, 5.95]},
    {"at": "L36>", "pos": [5.0, 7.6]},
    {"at": "L38", "hidden": True},
    # 04: Saturday, clocking in: down the corridor to the hall door (P9), then back, frozen, holding a mop
    {"at": "L43", "pos": [4.8, 10.6], "hidden": False, "yaw": 0, "expr": "neutral", "head": [0, 0], **DOWN},
    {"at": "L43>", "pos": [4.9, 7.4]},
    {"at": "L44", "hidden": True},
    {"at": "L46", "pos": PEAK["dev"], "hidden": False, "yaw": 0, "expr": "scared", "head": [0, 14], **MOPPING,
     "arms": [30, 34]},
    {"at": "L56", "expr": "terrified", "tremble": 1.2},
    {"at": "L58", "tremble": 0.0},
    *jump("L60", PEAK["dev"], BOW["dev"], yaw=0, mop=False, arms=[0, 0], expr="scared"),
    # not grinning now: turned to Rosa as she lines us up (P8)
    {"at": "L69", "yaw": facing(-40, 10), "head": [0, 2], "expr": "scared", "blend": 0.0},
    {"at": "L70", "yaw": 0, "head": [-20, 0], "blend": 0.0},
    *jump("L71", BOW["dev"], BOW_BACK["dev"]),
    {"at": "L71", **WAVE_DEV, "arms": [0, 140], "wave": [0, 20], "head": [0, 4]},
    {"at": "L71.1", **DOWN, **BOWED, "blend": 0.7, "expr": "shut"},
    *jump("P04", BOW_BACK["dev"], BOW["dev"]),
    {"at": "P04+0.4", **UP, "blend": 0.9, "expr": "scared"},
    {"at": "L76>", "pos": BOW["dev"]},
    # 06: already at the glass, waving first (shown, never said)
    *jump("L78", BOW["dev"], [4.5, 0.95], yaw=0, expr="neutral", head=[0, 6], arms=[0, 150], wave=[0, 24]),
    {"at": "L80", **DOWN, "blend": 0.6, "yaw": -40},
    {"at": "L85>", "pos": [4.5, 0.95]},
]
talk(dev, "L35.1", "L35.4>")
acting = {"me": me, "rosa": rosa, "dev": dev}

# ---------------------------------------------------------------------------------------------------- cues
ROWS = "rows"
cues = [
    {"at": 0, "name": "lights", "state": "rest"},
    {"at": 0, "name": "crowd", "n": 55},
    {"at": 0, "name": "eyes", "state": "shut", "look": "me"},
    {"at": "L26", "name": "crowd", "n": 110},
    {"at": "L33", "name": "crowd", "n": 135},
    {"at": "L46", "name": "crowd", "n": 260},
    {"at": "L60", "name": "crowd", "n": 150},       # out in the water: the packed ones are behind us
    {"at": "L68", "name": "crowd", "n": 260},
    {"at": "L75.1", "name": "crowd", "n": 150},
    {"at": "L78", "name": "crowd", "n": 70},
    # the corridor door: Dev through it, then it swings shut
    {"at": "L36.1", "name": "door", "open": 1.0, "dur": 0.5},
    {"at": "L36.3", "name": "door", "open": 0.0, "dur": 0.3},
    # Saturday: Dev opens it coming in
    {"at": "L43.2", "name": "door", "open": 0.6, "dur": 0.5},
    {"at": "L44", "name": "door", "open": 0.0},
    # the lids: two crack open for a second as Dev goes (one above the caption, one below: P2); then all open, one
    # after another, top to bottom
    {"at": "L41.1", "name": "eyes", "state": "crack", "order": [1, 3], "every": 0.12, "hold": 0.9, "amount": 0.85,
     "blink": False},
    {"at": "L50.1", "name": "eyes", "state": "open", "order": ROWS, "every": 0.17, "open_dur": 0.3, "look": "me",
     "blink": True},
    # right at ME: straight down the lens from my eye line (P2)
    {"at": "L55", "name": "eyes", "state": "open", "order": [], "look": "cam"},
    {"at": "L56", "name": "eyes", "state": "open", "order": [], "look": "dev"},
    {"at": "L56.2", "name": "eyes", "state": "open", "order": [], "look": "me"},
    {"at": "L59", "name": "eyes", "state": "open", "order": [], "look": "rosa"},
    {"at": "L60", "name": "eyes", "state": "open", "order": [], "look": "me"},
    # at the bow they close one after another, the last one on me
    {"at": "L73", "name": "eyes", "state": "shut", "order": [9, 4, 8, 3, 6, 1, 5, 0, 7, 2], "every": 0.2,
     "open_dur": 0.3},
    {"at": "L74.1", "name": "eyes", "state": "shut", "order": [], "look": "me"},
    {"at": "L75", "name": "eyes", "state": "shut", "order": list(range(10)), "every": 0.0},
    # the fog bloom where it presses, and the bubbles
    {"at": "L52.3", "name": "fogbloom", "amount": 0.3, "dur": 1.2},
    {"at": "L54", "name": "fogbloom", "amount": 0.1, "dur": 1.2},      # the breath fog thins, so the stare reads
    {"at": "L75", "name": "fogbloom", "amount": 0.0, "dur": 1.5},
    {"at": "P04", "name": "bubbles", "kind": "applause", "dur": 1.7},
    # the tiny stream rises between us through the side shot (P4)
    {"at": "L84", "name": "bubbles", "kind": "tiny", "dur": 2.6, "x0": 0.7, "x1": 1.8, "z0": 1.1, "z1": 1.8},
    # the hall's lights: dim, stuck bright, down like a stage, then the next night
    {"at": "L43", "name": "lights", "state": "stuck", "dur": 0.4},
    {"at": "L76.1", "name": "lights", "state": "dark", "dur": 1.8},
    {"at": "L78", "name": "lights", "state": "rest", "dur": 0.5},
    # the pup's eyes
    {"at": 0, "name": "pup_eyes", "state": "shut", "look": "me"},
    {"at": "L83.1", "name": "pup_eyes", "state": "open", "order": [0, 5, 1, 6, 2, 7, 3, 8, 4, 9], "every": 0.12,
     "open_dur": 0.22, "look": "me", "blink": False},
    # its eyes follow my hand; its own one-eye-at-a-time blink plays as acting under that, not as a reply
    {"at": "L84.1", "name": "pup_eyes", "state": "open", "order": [], "look": "hand:me"},
    {"at": "L84.2", "name": "pup_eyes", "state": "blinkwave", "order": [0, 5, 1, 6, 2, 7, 3, 8, 4, 9], "every": 0.14},
    {"at": "L85", "name": "pup_eyes", "state": "open", "order": [], "look": "me", "blink": True},
]


# the Regular's path: every time it comes closer it's seen gliding closer, in real time
REG = [
    {"at": 0, "where": [0.5, -13.0, 2.5], "ripple": 0.22, "roll": -3},
    {"at": "L02", "where": REG_FAR, "glide": True, "roll": 3},
    {"at": "L12", "where": REG_FAR, "ripple": 0.07, "roll": 3},
    {"at": "L12.5", "where": [0.7, -21.6, 2.5], "glide": True, "ripple": 0.2, "roll": 4},
    {"at": "L14", "where": [0.7, -21.6, 2.5], "glide": True, "roll": 4},
    {"at": "L26", "where": [0.7, -21.6, 2.5], "roll": 4},
    {"at": "L27", "where": [0.5, -19.0, 2.55], "glide": True},
    {"at": "L28", "where": REG_MID, "glide": True, "roll": -3},
    {"at": "L30>", "where": REG_MID, "glide": True},
    {"at": "L32", "where": [0.0, -10.5, 2.65], "glide": True},
    {"at": "L33", "where": REG_NEAR, "glide": True},
    {"at": "L40", "where": REG_NEAR},
    {"at": "L40>", "where": REG_GLASS, "glide": True, "yaw": 0},
    {"at": "L46", "where": REG_GLASS},
    {"at": "L48", "where": REG_PRESS, "glide": True, "press": 1.0},
    {"at": "L57.2", "where": REG_PRESS, "press": 1.0},
    {"at": "P02>", "where": REG_DRAG, "glide": True, "press": 1.0},
    {"at": "L60", "where": REG_DRAG, "press": 1.0},
    {"at": "L75", "where": REG_DRAG, "press": 1.0},
    {"at": "L75>", "where": [-1.4, -4.5, 2.8], "glide": True, "press": 0.0, "roll": 6},
    {"at": "L76", "where": [-1.0, -9.0, 2.7], "glide": True, "press": 0.0},
    # the next night: back out of the blue with the pup, nudging it up to the glass
    {"at": "L78", "where": [1.8, -17.0, 2.4], "hidden": False},
    {"at": "L79", "where": [1.4, -7.0, 2.2], "glide": True},
    {"at": "L80", "where": [1.3, -2.4, 2.0], "glide": True},
    {"at": "L80.3", "where": [0.2, -2.0, 2.35], "glide": True},
    {"at": "L82", "where": REG_BEHIND, "glide": True},
    {"at": "L84>", "where": REG_BEHIND, "glide": True},
    {"at": "L85>", "where": REG_AWAY, "glide": True, "yaw": -20},
]
PUP = [
    {"at": 0, "hidden": True, "where": [1.4, -18.0, 1.5]},
    {"at": "L78", "where": [2.6, -16.0, 1.4], "hidden": False},
    {"at": "L79", "where": [1.6, -6.0, 1.5], "glide": True},
    {"at": "L80", "where": [1.3, -1.5, 1.58], "glide": True},
    {"at": "L80.3", "where": [1.2, -0.52, 1.6], "glide": True, "press": 0.6},
    {"at": "L82", "where": PUP_GLASS, "glide": True, "press": 1.0},
    # it turns a little toward the side of the hall as its eyes open, so the two-shot and the side view see them
    {"at": "L83c-0.5", "where": PUP_GLASS, "glide": True, "press": 1.0, "yaw": -24},
    {"at": "L84>", "where": PUP_GLASS, "glide": True, "press": 1.0, "yaw": -24},
    # it drifts off still turned to me, so its lit rows face me (and the camera, a little to my side) to the cut
    {"at": "L85>", "where": PUP_AWAY, "glide": True, "press": 0.0, "yaw": -66},
]
for name, keys in (("regular", REG), ("pup", PUP)):
    for k in keys:
        cue = {"at": k["at"], "name": name, "pos": k["where"]}
        for kk in ("glide", "press", "ripple", "roll", "yaw", "hidden"):
            if kk in k:
                cue[kk] = k[kk]
        cues.append(cue)


# each shot's own light (set.py shot_look), on for exactly its frames. Round 2 (P1): the hall's ceiling lights no
# longer reach the Regular (set.py); it's keyed from below by the underkey strip, and the close shots add a low
# side key. FACE: 35% caustics on every face-dominant shot (standards R1, Q1)
COOL = "#e8f2f6"
WARM = "#ffd8b4"
ROSA_KEY = "#f6dcc6"                            # a touch warmer on Rosa's skin (standards A)
FACE = {"caustic": 0.35}
REV = {"disp": 4.5, "hallfill": 4.0}          # the reveal: the hall a lit box seen from out in the water
ROWS_KEY = [[-0.4, 0.6, 1.0], [-1.6, -0.6, 2.8], 160.0, 55, COOL]   # low from the right: sockets fall into shadow
LOOKS = {
    # the hook: its shut rows lit a touch out there (a narrow spot from below, in the water)
    0: {"regularkey": 0.25, "key2": [[0.6, -14.5, 0.0], [0.6, -22.4, 2.6], 2200.0, 30, "#bfe0ee"]},
    "L12": {"regularkey": 0.25, "key2": [[0.6, -15.0, 0.2], [0.6, -21.8, 2.6], 1400.0, 30, "#bfe0ee"]},
    "L14": dict(FACE),
    "L18": {"key2": [[-1.4, -3.4, 1.4], [-1.95, -5.6, -0.75], 260.0, 35, "#cfe9f0"]},
    "L19.2": {"key2": [[-0.6, -7.2, 1.6], [-1.6, -5.6, -0.7], 260.0, 40, "#cfe9f0"]},
    "L20": {**FACE, "key": [[0.9, 2.2, 2.0], [0.3, 0.8, 1.5], 30.0, 45, COOL]},
    "L21": {"key": [[-1.6, 2.4, 1.2], [-2.2, 1.2, 5.0], 110.0, 40, COOL]},
    "L24": {**FACE, "key": [[-1.1, 2.1, 2.1], [-1.5, 0.8, 1.55], 30.0, 45, ROSA_KEY]},
    "L34": dict(FACE),
    "L35": {**FACE, "key": [[1.0, 2.6, 2.1], [1.3, 1.05, 1.7], 30.0, 45, COOL]},
    "L36": {"corridor": 2.0, "key": [[3.8, 4.4, 2.6], [5.0, 6.05, 1.5], 120.0, 40]},
    "L38": dict(FACE),
    "L39": {**FACE, "key": [[-1.0, -0.4, 1.9], [-1.25, 1.05, 1.55], 26.0, 40, ROSA_KEY]},
    "L40": {"underkey": 0.8},
    "L41": {"regularkey": 0.0, "underkey": 0.4, "key": [[-1.4, 0.7, 1.9], [-2.15, -0.6, 2.9], 70.0, 40, COOL]},
    "L43": {"corridor": 2.0},
    "L45": {"key": [[3.3, 5.0, 2.4], [4.05, 6.0, 1.35], 60.0, 40]},
    "L46": {"underkey": 0.7, "regularkey": 0.2},
    "L48": {"regularkey": 0.0, "stage": 1.0, "underkey": 0.7},
    "L49": {"regularkey": 0.0, "stage": 1.0, "underkey": 2.0},
    "L50": {"regularkey": 0.0, "stage": 1.0, "underkey": 0.7, "key": ROWS_KEY},
    "L52": {"regularkey": 0.0, "stage": 1.0, "disp": 1.0, "underkey": 2.0, "key": [[1.2, 0.6, 1.2], [-0.6, -0.3, 2.6], 60.0, 45, COOL]},
    "L53": {"regularkey": 0.0, "stage": 1.0, "underkey": 0.8},
    "L54": {"regularkey": 0.0, "stage": 1.0, "underkey": 0.4, "key": [[-1.4, 1.0, 1.9], [-2.15, -0.6, 2.95], 50.0, 30, COOL]},
    "L55": {"regularkey": 0.0, **FACE, "underkey": 0.7, "key": ROWS_KEY},
    "L56": dict(FACE),
    "L57": {"regularkey": 0.0, "stage": 1.0, "underkey": 0.8},
    "L58": {**FACE, "key": [[1.5, 0.3, 2.0], [0.55, 1.2, 1.55], 30.0, 45, ROSA_KEY]},
    "L59": {"regularkey": 0.0, "stage": 1.0, "underkey": 0.8},
    "L60.3": REV, "L62": REV,
    "L63": {**REV, "key": [[-2.6, -1.0, 8.5], [-2.2, 1.2, 5.5], 400.0, 35, COOL],
            "key2": [[-0.6, 2.3, 6.0], [-2.2, 1.6, 5.55], 260.0, 30, "#cfe9f0"]},
    "L64": REV, "P03": REV, "L65": REV,
    "L69": {**FACE, "key": [[3.3, 2.3, 2.1], [4.0, 1.0, 1.7], 30.0, 45, COOL]},
    "L70": {**FACE, "key": [[2.3, 2.3, 2.1], [1.6, 1.0, 1.6], 30.0, 45, ROSA_KEY]},
    "L71": {"regularkey": 0.0, "stage": 1.0, "underkey": 0.6},
    "P04": {"stage": 1.0},
    "L73": {"regularkey": 0.0, "stage": 1.0, "underkey": 0.7, "key": [ROWS_KEY[0], [-1.6, -0.6, 2.4]] + ROWS_KEY[2:]},
    "L82": {**FACE, "underkey": 0.25, "key": [[1.75, 0.85, 1.0], [1.2, GF - 0.16, 1.6], 22.0, 22]},
    "L83": {**FACE, "underkey": 0.25, "key": [[1.7, 0.8, 1.0], [1.2, GF - 0.16, 1.6], 22.0, 22]},
    # the warm turn: my face keyed warm as the filter opens
    "L83c-0.5": {**FACE, "underkey": 0.3, "key": [[1.75, 0.35, 1.9], [1.2, 0.95, 1.55], 32.0, 40, WARM],
                 "key2": [[2.0, -1.3, 2.3], [1.2, GF - 0.2, 1.6], 30.0, 30, "#cfe9f0"]},
    "L84": {**FACE, "underkey": 1.0, "key": [[2.4, 1.4, 2.2], [1.2, 0.6, 1.3], 45.0, 50, WARM],
            "key2": [[2.1, 0.5, 1.1], [1.2, GF - 0.16, 1.6], 45.0, 35]},
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
    if at == 0:
        cues.append({"at": 0, "name": "shot", "look": look})
    else:
        cues.append({"at": early(at), "name": "shot", "look": look})
    if i + 1 < len(SH):
        cues.append({"at": early(SH[i + 1][0]), "name": "shot", "look": None})

fx = [
    {"at": "L53.2", "kind": "punch", "dur": 1.6, "zoom": 1.07, "fade": 0.4},
    {"at": "P02", "kind": "shake", "dur": 1.3, "amp": 0.3},
]

# ---------------------------------------------------------------------------------------------------- sound
EYE_OPEN = [f"L50.1+{0.17 * j:.2f}" for j in range(10)]
sfx = [
    {"at": "L01>", "kind": "sting", "db": -12, "dur": 1.6},
    {"at": "L12.3", "kind": "glide", "db": -24, "dur": 2.6},
    {"at": "L27", "kind": "glide", "db": -20, "dur": 2.4},
    {"at": "L36.1", "kind": "door", "db": -18},
    {"at": "L36.3+0.25", "kind": "door", "db": -9},
    {"at": "L43.2", "kind": "door", "db": -20},
    {"at": "L40", "kind": "glide", "db": -15, "dur": 2.6},
    {"at": "L41.1", "kind": "wetclick", "db": -13, "dur": 0.6},
    {"at": "L41.1+0.12", "kind": "wetclick", "db": -14, "dur": 0.6},
    {"at": "L45.1+0.1", "kind": "click", "db": -6},
    {"at": "L45.2", "kind": "click", "db": -6},
    {"at": "L48.3", "kind": "squeak", "db": -15, "dur": 0.35},
    {"at": "L50.1", "kind": "sting", "db": -13, "dur": 2.6},
    *[{"at": a, "kind": "wetclick", "db": -15 - (j % 3), "dur": 0.5, "pan": (-0.35 if j % 2 == 0 else 0.35)}
      for j, a in enumerate(EYE_OPEN)],
    {"at": "L52.1", "kind": "squeak", "db": -11, "dur": 0.35},
    {"at": "L57.2", "kind": "squeal", "db": -9, "dur": 2.4, "keep": True},
    {"at": "L60", "kind": "riser", "db": -15, "dur": 1.2},
    {"at": "L60.2", "kind": "whoosh", "db": -16},
    *[{"at": f"P04+{0.28 * j:.2f}", "kind": "bubbles", "db": -12, "dur": 0.55, "pan": round(-0.8 + 0.32 * j, 2)}
      for j in range(6)],
    {"at": "L72", "kind": "bubbles", "db": -20, "dur": 1.2, "pan": 0.6},
    *[{"at": f"L73+{0.2 * j:.2f}", "kind": "wetclick", "db": -22, "dur": 0.4} for j in range(10)],
    {"at": "L75.1", "kind": "glide", "db": -20, "dur": 2.4},
    {"at": "L76.1", "kind": "hum_sweep", "db": -20, "dur": 1.9},
    {"at": "L78", "kind": "glide", "db": -21, "dur": 2.6},
    {"at": "L80.4", "kind": "squeak", "db": -24, "dur": 0.3},
    *[{"at": f"L83.1+{0.12 * j:.2f}", "kind": "wetclick", "db": -25, "dur": 0.3} for j in range(10)],
    {"at": "L84", "kind": "tinybubbles", "db": -14, "dur": 2.6, "pan": 0.2},
    # round 3: the two of them gliding off into the blue under L85
    {"at": "L84>", "kind": "glide", "db": -23, "dur": 2.3},
    # the one bubble pop, under the last 0.3 s as they go; then it cuts straight to S01 (note 17)
    {"at": "end-0.3", "kind": "pop", "db": -14},
]

story = {
    "slug": "ep13-closing-time",
    "title": "Closing Time",
    "made_for_kids": False,
    "premise": "A 19-year-old new night cleaner at a city aquarium works a three-person shift in a long dark hall facing a huge acrylic wall of endless blue. Before the shift goes home, everybody stands at the big tank and waves goodbye. The fish never swim, they hang facing the hall, and far back a huge pale diamond hangs in the blue and comes a little closer every night.",
    "twist": "The hall is the exhibit and the water side is the audience: benches on the tank floor face us, the hatch in our ceiling is the keepers' access on the box's roof, and the wave is the curtain call. When a co-worker skips it the show doesn't end, until all three bow. The next night the big one brings its pup to see the people who bowed, and the pup drifts back into the blue still watching me.",
    "world": "A city aquarium's night hall: polished concrete, white tile, a 12 m wall of thick acrylic lit by crawling caustics, a steel hatch in the ceiling, a cream-tiled service corridor with a porthole door, and on the far side a blue tank with blocky rock, sand, benches and a dim crowd.",
    "key_color": "#3fe0d0",
    "key_stroke": 3,
    # round 2 (P7): over the teal tank every caption gets a thicker dark navy outline and a darker drop shadow
    "caption": {"ink": "#04101a", "stroke_add": 3, "shadow": 0.85},
    "gap": 0.12,
    # the decision's caption floor (P7): a chunk on screen under 0.3 s joins the next one in its line
    "min_read": 0.3,
    # round 2: the acrylic reflects a little less (IOR 1.25, from 1.49), so the darker Regular isn't lost behind a
    # mirror of the hall; the steepest looks through it go lower per shot (glass_ior)
    "glass_ior_default": 1.25,
    "tail": 0,
    "look": {"fog": "#0a2a3a", "fog_density": 0.0, "fog_start": 3.0, "sky": "#0f4254", "sky_strength": 1.0,
             "exposure": 0.35, "flash_safe": True},
    "grade": {"shadows": [-0.04, -0.01, 0.07], "highlights": [-0.04, 0.03, 0.02], "saturation": 0.95,
              "contrast": 1.08, "vignette": 0.4, "bloom": 0.3, "grain": 0.01},
    "shot_grades": {"S01": {"exposure": 1.7, "saturation": 1.12, "shadows": [-0.02, 0.0, 0.05]}},
    **per_shot,
    "phonemes": {},
    "cast": cast,
    "lines": lines,
    "shots": shots,
    "acting": acting,
    "cues": cues,
    "fx": fx,
    # whole-tone on A1, very slow; no piano, no music box. Heard through water (a low-pass, 400 Hz in the hall); it
    # opens all the way as the camera crosses the glass, closes as we come back in, and opens to 4 kHz with a small
    # pad lift on the cut to my soft face (P5)
    "music": {"root": 33, "mode": "whole", "bpm": 50, "seed": 31,
              "sections": [
                  {"at": 0, "voices": ["drone", "pad"], "energy": 0.3},
                  {"at": "L17", "voices": ["drone", "pad", "bubble"], "energy": 0.3},
                  {"at": "L33", "voices": ["drone", "pad", "bubble"], "energy": 0.4},
                  {"at": "L43", "voices": ["drone", "pad", "bubble"], "energy": 0.55},
                  {"at": "L50", "voices": ["drone", "pad", "choir"], "energy": 0.7},
                  {"at": "L58", "voices": ["drone", "pad"], "energy": 0.5},
                  {"at": "L60", "voices": ["drone", "pad", "bubble"], "energy": 0.65},
                  {"at": "L68", "voices": ["drone", "pad"], "energy": 0.45},
                  {"at": "L76", "voices": ["drone"], "energy": 0.25},
                  {"at": "L78", "voices": ["drone", "pad", "bubble"], "energy": 0.3},
                  {"at": "L83", "voices": ["drone", "pad"], "energy": 0.22},
                  {"at": "L83c-0.5", "voices": ["pad", "bubble"], "energy": 0.42},
              ],
              "filter": [
                  {"at": 0, "hz": 400},
                  {"at": "L60.2", "hz": 16000, "dur": 0.3},
                  {"at": "L68", "hz": 400, "dur": 0.4},
                  {"at": "L83c-0.5", "hz": 4000, "dur": 0.9},
              ]},
    "sound": {"floor": "stone", "steps_db": -23,
              "ambience": [
                  {"kind": "water", "from": 0, "to": "end", "lufs": -36},
                  {"kind": "hum", "from": 0, "to": "L43", "lufs": -44},
                  {"kind": "hum", "from": "L43", "to": "L76.1", "lufs": -39},
                  {"kind": "room", "from": 0, "to": "L60.2", "lufs": -40},
                  {"kind": "drips", "from": "L36.1", "to": "L38", "lufs": -34},
                  {"kind": "drips", "from": "L43", "to": "L44", "lufs": -32},
                  {"kind": "water", "from": "L60.2", "to": "L68", "lufs": -29},
                  {"kind": "room", "from": "L68", "to": "end", "lufs": -40},
                  {"kind": "drone", "from": "L46", "to": "L60", "lufs": -38},
              ],
              "sfx": sfx,
              # three holes (P5), and one 10 dB duck (round 3): the music and ambience to -40 dB (1) from the end of L49 to the first lid
              # click, so the sting comes out of near-silence; (2) 0.4 s after "NOTHING."; (3) 0.4 s before L83
              "music_drops": [{"from": "L49>", "to": "L50.1", "keep": ["sting", "wetclick"]},
                              {"from": "L45>", "to": "L46"},
                              {"from": "L82>", "to": "L83"},
                              # round 3 (critic, D1): a 10 dB duck of the bed under the pup's eye hold, L83 to the cut
                              # to my face
                              {"from": "L83>", "to": "L83c-0.5", "db": -10.0, "keep": ["wetclick"]}]},
}
OUT.write_text(json.dumps(story, indent=1, ensure_ascii=False) + "\n")
print("wrote", OUT, f"({len(shots)} shots)")
