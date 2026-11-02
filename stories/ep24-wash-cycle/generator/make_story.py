"""Writes ../story.json for ep24 "wash-cycle". Run from anywhere: python stories/ep24-wash-cycle/generator/make_story.py

The words are in lines.json next to this file. Everything else is here: the cast, the shots, the acting, the cues
set.py reads, the effects, the score and the sound.

Places (set.py's coordinates, metres, shop floor z = 0): the row of six chairs is along x at y = 0 facing +y (the
dryers on the back wall); chair i is at x = -3.6 + 1.45 (i - 1). My stool at the folding table is at (-3.6, -2.45)
(the table: y -2.05 .. -1.25, x -4.6 .. 3.0). The glass door and the coat hooks are at the right end (x = 4.4, hooks at
3.2 and 3.5); the dryer that buzzed is at (-2.3, -3.0); the change machine and the soap machine are on the left
end wall; the side door beside the shop is at x = 7.2 on the street; the stair and his door are at x = -40.

Light plan (ep20 failed its flash check on lamp glows and red light at beat changes): every light change is a slow
ramp inside one held shot (S45), never across a cut. Nothing is red. The dryer windows are a steady warm glow.
"""
import json
import math
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE.parent / "story.json"
lines = json.loads((HERE / "lines.json").read_text())

CHX = [round(-3.6 + 1.45 * i, 3) for i in range(6)]
SIT_Z = -0.045
STOOL = [-3.6, -2.45, SIT_Z]
ME_CHEAT = [-3.6, -0.95, -0.64]          # close-ups only: my face a hand's width from its face
ST = (-40.0, 0.0)
TOP = 0.19 * 12
LY = ST[1] + 0.28 * 12 + 1.5
DOOR_X = 4.4
SIDE_X = 8.3
CHANGE = [-4.35, -1.45, 0.0]


def c(*keys):
    return [list(k) for k in keys]


def mv(p0, t0, l0, p1=None, t1=None, l1=None):
    if p1 is None:
        return c([0, p0, t0, l0])
    return c([0, p0, t0, l0], [1, p1, t1 if t1 is not None else t0, l1 if l1 is not None else l0])


def front(face, az, dist, dz, lens, push=0.0, aim_dz=0.0, lens2=None):
    """A camera in front of a face: az degrees round from straight on (0 = at -y of the face, 180 = at +y)."""
    a = math.radians(az)
    d = (math.sin(a), -math.cos(a))
    p0 = [round(face[0] + d[0] * dist, 3), round(face[1] + d[1] * dist, 3), round(face[2] + dz, 3)]
    tg = [face[0], face[1], round(face[2] + aim_dz, 3)]
    if not push and not lens2:
        return c([0, p0, tg, lens])
    p1 = [round(face[0] + d[0] * (dist - push), 3), round(face[1] + d[1] * (dist - push), 3), round(face[2] + dz, 3)]
    return c([0, p0, tg, lens], [1, p1, tg, lens2 or lens])


FH = 1.5                                  # a seated face's height
def F(i, dy=-0.1):                        # the Turned's face in chair i (0-based)
    return [CHX[i], dy, FH]
ME_F = [STOOL[0], STOOL[1], FH]           # my face at the table
ARTHUR_F = [CHX[5], 0.0, FH]
ROW = ([-4.4, -1.0, 1.4], [3.65, -0.1, 1.2], 20)

cast = {
    "me": {"age": "adult", "skin": "#f0c6a0", "shirt": "#2f5d43", "pattern": "solid", "collar": "#244a35",
           "pants": "#3c4660", "shoes": "#2a2420", "sleeves": "long", "hair": "swoop", "hair_c": "#2b1d14",
           "extras": ["coat"], "face": {"eyes": "round", "brows": True, "ink": "#171112"}},
    "me0": {"age": "adult", "skin": "#f0c6a0", "shirt": "#9c7418", "pattern": "solid", "collar": "#845f12",
            "pants": "#3c4660", "shoes": "#2a2420", "sleeves": "long", "hair": "swoop", "hair_c": "#2b1d14",
            "face": {"eyes": "round", "brows": True, "ink": "#171112"}},
    "arthur": {"age": "adult", "skin": "#e6bc9c", "shirt": "#8c9096", "pattern": "knit", "pattern_c": "#6a6e74",
               "pants": "#5b4331", "shoes": "#43301f", "sleeves": "long", "hair": "cap", "hair_c": "#ecebe6",
               "face": {"eyes": "tired", "brows": True, "ink": "#1a1416", "cheeks": "#eba094"}},
    "turned": {"age": "adult", "skin": "#9d8163", "shirt": "#efece4", "pattern": "solid", "pants": "#3f7fd0",
               "shoes": "#141414", "sleeves": "short", "hair": "swoop", "hair_c": "#5a3118", "width": 1.1,
               "face": {"eyes": "tired", "brows": False, "ink": "#1c0f08", "mouth": "gape", "gaze": 2.0, "pupil_scale": 0.68}},
}

# ---------------------------------------------------------------------------------------------------- shots
SH = []


def shot(at, cam, **opt):
    SH.append((at, cam, opt))


# 01 the coat (night one)
shot(0, front(ME_F, 180, 1.9, 0.0, 36, push=0.22, aim_dz=-0.34), hand=0.004)                                  # S01 me, collar up
shot("L02", mv([-2.3, -1.3, 1.1], [-2.3, -3.0, 1.0], 30, [-2.3, -1.15, 1.1], [-2.3, -3.0, 1.0], 30), hand=0.003)   # S02 the door: collar and buttons behind the glass
shot("L03", mv([1.0, -2.3, 1.55], [0.9, -5.5, 1.4], 30, [1.0, -2.4, 1.55], [0.9, -5.5, 1.4], 30), hand=0.004)          # S03 rain on glass
shot("L04", mv([-2.2, -10.2, 1.5], [1.6, -3.6, 1.2], 22), hand=0.01)                            # S04 outside
shot("L05", mv([-4.4, -0.9, 1.3], [3.5, 0.4, 1.0], 16, [-4.3, -0.9, 1.3], [3.5, 0.4, 1.0], 16), hand=0.002)            # S05 the row
shot("L06", mv([-1.6, -0.55, 1.5], [-3.5, -2.45, 1.25], 24, [-1.75, -0.55, 1.5], [-3.5, -2.45, 1.25], 25))           # S06 me at the table
shot("L07", mv([2.7, -0.6, 1.4], [4.4, -3.0, 1.3], 24, [2.9, -0.7, 1.4], [4.4, -3.0, 1.3], 26), hand=0.004)           # S07 in at the door
shot("L08", mv([-0.5, -1.0, 1.35], [3.65, 0.0, 1.2], 30, [-0.1, -1.0, 1.35], [3.65, 0.0, 1.2], 32), hand=0.003)       # S08 old man small
shot("L09", mv([2.7, 1.9, 1.5], [3.6, 0.0, 1.4], 22, [2.8, 1.8, 1.5], [3.6, 0.0, 1.4], 23), hand=0.003)   # S09 grey jumper
shot("L10", mv([2.4, 1.15, 1.5], [3.65, 0.0, 1.5], 30, [2.45, 1.1, 1.5], [3.65, 0.0, 1.5], 31), hand=0.003)   # S10 his face
shot("L11", front(ME_F, 180, 1.5, 0.0, 34, aim_dz=-0.3), hand=0.005)                                          # S11 me, cold
shot("L12", mv([-2.6, 0.2, 1.35], [-5.0, -1.1, 1.1], 24, [-2.8, 0.2, 1.35], [-5.0, -1.1, 1.1], 25), hand=0.003)   # S12 the change machine
shot("L13", mv([-4.45, -0.95, 1.5], [-0.3, -2.6, 1.15], 19, [-4.4, -0.95, 1.5], [-0.2, -2.6, 1.15], 19), hand=0.003)   # S13 wide: the end dryer buzzes, he walks back from it
shot("L14.2", mv([0.9, -1.1, 1.55], [2.8, -2.55, 1.3], 22, [1.0, -1.1, 1.55], [2.8, -2.55, 1.3], 23), hand=0.003)   # S15 him folding
shot("L15", mv([-2.0, -0.95, 1.45], [-2.3, -2.95, 0.9], 22, [-2.1, -1.0, 1.45], [-2.3, -2.95, 0.9], 22), hand=0.003)   # S16 the coat inside
shot("L16", front([-2.3, -2.2, FH], 180, 1.6, 0.0, 34), hand=0.004)                              # S17 holding it up
shot("L17", mv([-4.3, -1.15, 1.45], [2.4, -2.5, 1.25], 18, [-4.2, -1.15, 1.45], [2.4, -2.5, 1.25], 18), hand=0.003)  # S18 down the table
shot("L18", front([-2.3, -2.2, FH], 180, 1.4, 0.0, 36, push=0.2), hand=0.004)                    # S19 in the coat
# 02 the Turned (night two)
shot("L19", mv(*ROW[:2], ROW[2]), hand=0.002)                                                    # S20
shot("L20", mv([0.6, -1.7, 1.35], [2.9, 0.1, 1.15], 22, [0.8, -1.7, 1.35], [2.9, 0.1, 1.15], 23), hand=0.003)       # S21 two backs
shot("L21", mv([1.7, -1.7, 1.4], [2.2, 0.0, 1.15], 24, [1.85, -1.55, 1.4], [2.2, 0.0, 1.15], 25), hand=0.003)        # S22 the figure from behind
shot("L22", mv([2.2, -0.95, 1.12], [2.2, -0.15, 1.12], 17, [2.2, -0.85, 1.12], [2.2, -0.15, 1.12], 17), hand=0.002)  # S23 the bib on its back
shot("L23", c([0, [4.7, 1.55, 0.2], [2.95, 0.42, 0.1], 26], [1, [4.55, 1.5, 0.2], [2.95, 0.42, 0.1], 27]), hand=0.002)   # S23 low: its heels-forward shoes beside Arthur's
shot("L24", mv([2.5, -1.0, 1.0], [2.2, -0.2, 1.1], 28, [2.35, -1.5, 1.4], [2.2, -0.15, 1.5], 34))                     # S25 tilt up to the face
shot("L25", front(F(4), 0, 1.95, -0.1, 36, push=0.06), hand=0.002)                               # S26 its face
shot("L26", front(ME_F, 180, 1.6, 0.0, 34), hand=0.003)                                          # S27 me, still
shot("L27", mv([4.6, -1.5, 1.5], [3.1, -0.1, 1.45], 30, [4.5, -1.4, 1.5], [3.1, -0.1, 1.45], 31), hand=0.003)        # S28 his profile
shot("L28", mv([3.9, -14.0, 1.7], [3.9, -3.5, 1.4], 12.5), hand=0.004)   # S29 outside, the side door
shot("L29", mv([0.6, -10.8, 1.5], [2.4, -5.8, 1.35], 24), hand=0.01)   # S30 walking off
# 03 one chair nearer (night three)
shot("L30", mv(*ROW[:2], ROW[2]), hand=0.002)                                                    # S31 four
shot("L31", front(F(3), 14, 1.9, -0.1, 40, push=0.06), hand=0.002)                            # S32 its face: it doesn't blink
shot("L31b", mv([CHX[3], -0.14, 0.03], [CHX[3], -0.02, 0.41], 11), hand=0)   # S33 the tally (six strokes), held through "ten times"
shot("L32", front(F(3), 0, 1.5, -0.1, 36, push=0.08), hand=0.002)                                # S34 closer
shot("L33", front(ME_F, 180, 1.5, 0.0, 36), hand=0.004)                                          # S35 it wants the coat back
shot("L34", mv([2.5, -1.3, 1.5], [3.35, -3.3, 1.3], 18, [2.6, -1.3, 1.5], [3.35, -3.3, 1.3], 18), hand=0.003)   # S36 the hook
shot("L35", front(F(3), 0, 1.5, -0.1, 36), hand=0.002)                                           # S37 its eyes
shot("L36", mv([2.9, 1.6, 1.55], [3.65, 0.0, 1.45], 20, [3.0, 1.55, 1.55], [3.65, 0.0, 1.45], 21), hand=0.003)   # S38 he coughs
shot("L37", mv([0.4, -1.9, 1.5], [2.4, -0.8, 1.3], 20, [0.7, -1.9, 1.5], [2.7, -0.8, 1.3], 20), hand=0.004)   # S39 past his chair
shot("L38", front([3.1, -0.85, FH], 90, 1.5, 0.0, 34), hand=0.003)                               # S40 lavender
shot("L39", mv([-3.6, 1.0, 1.3], [-4.8, 1.0, 1.25], 24, [-3.5, 1.0, 1.3], [-4.8, 1.0, 1.25], 25), hand=0.002)       # S41 soap machine
shot("L40", front(ME_F, 180, 1.6, 0.1, 34, aim_dz=-0.1), hand=0.004)                             # S42 eyes down
# 04 night four
shot("L41", mv([4.6, -3.0, 1.5], [-1.0, -0.6, 1.0], 18, [4.5, -2.95, 1.5], [-1.0, -0.6, 1.0], 18), hand=0.003)      # S43 from the door
shot("L42", mv([-1.0, -1.2, 1.45], [3.65, -0.1, 1.4], 30, [-0.8, -1.2, 1.45], [3.65, -0.1, 1.4], 31), hand=0.002)    # S44 in his chair
shot("L43", mv(*ROW[:2], ROW[2]), hand=0.002)                                                    # S45 small, far
shot("L44", front(ME_F, 180, 1.5, 0.0, 34), hand=0.003)                                          # S46 breath
shot("L45", mv([-4.4, -1.0, 1.4], [3.65, -0.1, 1.2], 20), hand=0)                                # S47 the stutter, one held shot
shot("L48.3", c([0, [-3.3, -3.0, 1.3], [-3.6, -0.8, 1.2], 60], [1, [-3.35, -2.9, 1.3], [-3.6, -0.8, 1.2], 62]), hand=0.002)   # S47 its upside-down face over mine
shot("L49", c([0, [-3.6, -1.7, 1.5], [-3.6, -0.5, 1.4], 80], [1, [-3.6, -1.62, 1.5], [-3.6, -0.5, 1.4], 86]), hand=0)  # S48 its eyes
shot("L50", c([0, [-1.3, -2.6, 1.2], [-3.6, -0.95, 0.95], 55], [1, [-1.35, -2.55, 1.2], [-3.6, -0.95, 0.95], 57]), hand=0.002)   # S49 me, frozen, front three-quarter
FACE_C = lambda dx=0.0: c([0, [-3.6 + dx, -1.7, 1.5], [-3.6, -0.5, 1.4], 80], [1, [-3.6 + dx, -1.64, 1.5], [-3.6, -0.5, 1.4], 84])
COAT_C = c([0, [-2.95, -0.5, 0.88], [-3.62, -0.86, 0.84], 42], [1, [-3.0, -0.5, 0.88], [-3.62, -0.86, 0.84], 44])   # from beside it: my coat's front
CHAIR_C = c([0, [3.0, -0.95, 1.0], [3.65, 0.0, 0.7], 26], [1, [3.05, -0.9, 1.0], [3.65, 0.0, 0.7], 27])              # his empty chair, six
shot("L51", FACE_C(), hand=0.002)                              # S50 its eyes slide down
shot("L51.2", COAT_C, hand=0.002)                              # S51 the coat's buttons
shot("L51.2+0.45", FACE_C(0.12), hand=0.002)                          # S52 its eyes over to his chair
shot("L52.1+0.1", CHAIR_C, hand=0.002)                             # S53 his empty chair
shot("L52.2+0.1", FACE_C(-0.1), hand=0.002)                        # S54 and back, down
shot("L53", COAT_C, hand=0.002)                                # S55 Coat.
shot("L53.1", CHAIR_C, hand=0.002)                             # S56 Chair.
shot("L53.2", COAT_C, hand=0.002)                              # S57 Coat.
shot("L53.3", FACE_C(0.05), hand=0.002)                        # S58 counting
# 05 the coat was his
shot("L54", c([0, [-1.3, -2.6, 1.2], [-3.6, -0.95, 0.98], 60], [1, [-1.35, -2.55, 1.2], [-3.6, -0.95, 0.98], 62]), hand=0.002)   # S53 I knew: my face, its face above
shot("L55", mv([-4.4, -1.0, 1.45], [3.2, -2.5, 1.2], 17), hand=0.003)                            # S55 replay of the wide
shot("L56", mv([-5.15, -0.15, 1.5], [-2.5, -2.7, 1.2], 22, [-5.0, -0.2, 1.5], [-2.5, -2.7, 1.2], 22), hand=0.003)    # S56 the dryer, door closing
shot("L57", mv([3.0, -0.95, 1.0], [3.65, 0.0, 0.7], 26, [3.05, -0.9, 1.0], [3.65, 0.0, 0.7], 27), hand=0.002)         # S57 his empty chair
shot("L58", c([0, [-3.1, -2.5, 1.55], [-3.6, -0.7, 1.35], 48, 4], [1, [-3.15, -2.4, 1.55], [-3.6, -0.7, 1.35], 50, 4]), hand=0.002)   # S58 its face, eyes on the coat
# 06 gratitude
shot("L59", c([0, [-4.9, -2.7, 1.45], [-3.2, -0.8, 1.2], 30], [1, [-4.85, -2.65, 1.45], [-3.2, -0.8, 1.2], 31]), hand=0.002)   # S59 I stand
shot("L60", mv([3.6, 2.3, 0.85], [5.25, 3.1, 0.5], 24, [3.7, 2.35, 0.85], [5.25, 3.1, 0.5], 25), hand=0.002)   # S60 machine six
shot("L61", front([-3.6, -2.45, FH], 180, 1.9, 0.1, 30, push=0.3, aim_dz=-0.25), hand=0.003)     # S61 folding
shot("L62", mv([ST[0], 4.3, TOP + 1.75], [ST[0], 1.6, 1.5], 24, [ST[0], 4.2, TOP + 1.75], [ST[0], 2.4, 1.9], 24), hand=0.004)   # S62 up the stair
shot("L63", front([ST[0], LY + 0.25, TOP + FH], 0, 1.7, 0.1, 32), hand=0.003)   # S63 his door
shot("L64", mv([ST[0] + 0.55, LY - 3.0, TOP + 1.5], [ST[0], LY - 0.3, TOP + 1.2], 17, [ST[0] + 0.55, LY - 2.9, TOP + 1.5], [ST[0], LY - 0.3, TOP + 1.2], 17), hand=0.003)   # S64 the wash
shot("L65", front([ST[0], LY - 1.15, TOP + FH], 180, 1.5, 0.0, 36), hand=0.003)   # S65 thank you
shot("L66", front([ST[0], LY + 0.25, TOP + FH], 0, 1.6, 0.0, 34), hand=0.003)   # S66 his slippers
shot("L68", c([0, [ST[0] + 3.3, LY - 0.3, TOP + 1.45], [ST[0], LY - 0.3, TOP + 1.38], 24], [1, [ST[0] + 3.2, LY - 0.3, TOP + 1.45], [ST[0], LY - 0.3, TOP + 1.38], 25]), hand=0.002)   # S66 two-shot, both faces in profile
# 07 two coats
shot("L69", mv(*ROW[:2], ROW[2]), hand=0.002)                                                    # S68
shot("L71", mv([-1.5, -2.3, 1.2], [0.2, -1.65, 0.95], 22, [-1.4, -2.3, 1.2], [0.2, -1.65, 0.95], 23), hand=0.003)   # S69 towels
shot("L72", mv([2.3, -1.2, 1.5], [3.4, -3.3, 1.3], 16, [2.4, -1.2, 1.5], [3.4, -3.3, 1.3], 16), hand=0.003)   # S70 two coats
shot("L74", mv([-1.4, -0.7, 1.55], [1.4, -2.5, 1.25], 24, [-1.9, -0.55, 1.55], [1.5, -2.5, 1.25], 21), hand=0.003)   # S70 pull back to the table
shot("L76", mv([2.3, -1.25, 1.5], [3.35, -3.3, 1.32], 17, [2.45, -1.32, 1.5], [3.35, -3.3, 1.32], 19), hand=0.002)   # S71 the last frame: the two coats on the hook

shots, rain, step = [], [], {}
for i, (at, cam, opt) in enumerate(SH):
    sid = f"S{i + 1:02d}"
    s = {"id": sid, "cam": cam, "step": opt.get("step", 2)}
    if i:
        s["at"] = at
    if "hand" in opt:
        s["hand"] = opt["hand"]
    shots.append(s)
SID = {at: s["id"] for (at, _, _), s in zip(SH, shots)}
# the room's top light in each close-up of the creature, set to match its neighbours' exposure across the cut
DIM = {"L20": 0.6, "L21": 0.6, "L22": 0.6, "L23": 0.6, "L24": 0.6, "L48.3": 0.45, "L49": 0.8, "L50": 0.15, "L51": 1.0,
       "L51.2+0.45": 1.0, "L52.1+0.1": 0.45, "L52.2+0.1": 1.0, "L53.1": 0.45, "L53.3": 1.0,
       "L54": 0.2, "L55": 0.55, "L58": 0.5}
RAIN = [SID[k] for k in ("L03", "L04", "L28", "L29", "L34", "L72", "L76")]

# ---------------------------------------------------------------------------------------------------- acting


class Actor:
    def __init__(self, first):
        self.keys, self.last = [], first

    def jump(self, at, pos, **kw):
        self.keys.append({"at": at, "pos": self.last})
        self.keys.append({"at": at, "pos": pos, "blend": 0.0, **kw})
        self.last = pos

    def walk(self, at, pos, **kw):
        self.keys.append({"at": at, "pos": pos, **kw})
        self.last = pos

    def set(self, at, **kw):
        self.keys.append({"at": at, **kw})


SIT = dict(sit=True, yaw=180, arms=[68, 68], side=[0, 0], bend=0, lean=0)
STAND = dict(sit=False, arms=[0, 0], side=[0, 0], bend=0, lean=0)
HID = [0, 0, -9]


def P(d, **kw):
    return {**d, **kw}


def seat(i, z=SIT_Z):
    return [CHX[i], 0.0, z]


# --- me (the green coat)
me = Actor(STOOL)
me.set(0, pos=STOOL, hidden=False, expr="neutral", **P(SIT))
me.set("L01", head=[0, 6], look=[0, -0.3])
me.jump("L04", STOOL, hidden=True)
me.jump("L18", [-2.3, -2.2, 0.0], hidden=False, expr="neutral", **{**STAND, "yaw": 180})
me.set("L18", expr="shut")
me.set("L18+0.9", expr="neutral")
me.jump("L19", STOOL, **{**SIT, "arms": [68, 68]}, expr="neutral")
me.set("L25", expr="worried", head=[0, 4])
me.set("L26", expr="worried", tremble=0.0)
me.jump("L29", [3.0, -5.3, 0.0], **{**STAND, "yaw": 0}, expr="neutral")
me.walk("L29>", [1.9, -6.0, 0.0])
me.jump("L30", STOOL, **P(SIT, expr="neutral", head=[0, 0], look=[0, 0]))
me.set("L31b", head=[0, 18], look=[0, -1.0], expr="worried")
me.set("L33", head=[0, 0], look=[0, 0], expr="worried")
me.set("L34", expr="neutral")
me.jump("L37", [1.0, -0.8, 0.0], **{**STAND, "yaw": 90})
me.walk("L37>", [3.1, -0.8, 0.0], yaw=90)
me.set("L38", expr="worried", head=[-25, 0])
me.jump("L40", STOOL, **P(SIT, expr="worried", head=[0, 18], look=[0, -1.0]))
me.set("L41", expr="neutral", head=[0, 0], look=[0, 0])
me.set("L44", expr="worried")
me.set("L44+0.3", expr="neutral", tremble=0.0)
me.jump("L48.3", ME_CHEAT, **P(SIT, yaw=0, expr="terrified", tremble=1.6, head=[0, -4], look=[0, 0], arms=[6, 6]))
me.set("L50", expr="terrified", tremble=0.5)
me.set("L54", expr="wide", tremble=0.0)
me.set("L55", hidden=True)
me.jump("L58", ME_CHEAT, hidden=False, **P(SIT, yaw=0, expr="worried", tremble=0.0, head=[0, 0]))
me.jump("L59", [-2.6, -0.8, 0.0], **{**STAND, "yaw": 0}, expr="neutral", head=[0, 0])
me.jump("L60", [-2.6, -0.8, 0.0], hidden=True)

# --- me0 (the mustard hoodie: night one, the memory, the stairs)
me0 = Actor([2.2, -6.0, 0.0])
me0.set(0, pos=[2.2, -6.0, 0.0], hidden=True, expr="worried", **STAND)
me0.jump("L04", [1.6, -6.5, 0.0], hidden=False, expr="worried")
me0.walk("L04>", [4.2, -4.5, 0.0])
me0.jump("L06", STOOL, **P(SIT, expr="neutral", look=[0, 0]))
me0.jump("L07", [DOOR_X, -2.9, 0.0], **{**STAND, "yaw": 180}, expr="worried", tremble=0.6)
me0.jump("L08", STOOL, **P(SIT, expr="worried", tremble=1.0, arms=[40, 40]))
me0.set("L12", expr="worried")
me0.jump("L12", CHANGE, **{**STAND, "yaw": -90}, tremble=0.0)
me0.jump("L13", STOOL, **P(SIT, expr="wide", head=[0, 0]))
me0.jump("L16", [-2.3, -2.2, 0.0], **{**STAND, "yaw": 180, "arms": [95, 95]}, expr="wide")
me0.set("L17", head=[-22, 0], expr="worried", arms=[0, 0])
me0.jump("L18", [-2.3, -2.2, 0.0], hidden=True)
me0.jump("L55", STOOL, hidden=False, **P(SIT, expr="worried", tremble=0.8))
me0.jump("L56", CHANGE, **{**STAND, "yaw": -90}, expr="neutral", tremble=0.0)
me0.jump("L57", STOOL, **P(SIT, hidden=True))
me0.jump("L60", STOOL, hidden=False, **P(SIT, expr="neutral"))
me0.set("L61", arms=[70, 70], expr="smirk")
me0.jump("L62", [ST[0], ST[1] + 1.8, 1.15], **{**STAND, "arms": [88, 88], "yaw": 180}, expr="neutral")
me0.walk("L63", [ST[0], LY - 1.15, TOP], expr="neutral")
me0.set("L63", hidden=True)
me0.jump("L64", [ST[0], LY - 1.15, TOP], hidden=False, **{**STAND, "arms": [88, 88], "yaw": 180}, expr="neutral")
me0.set("L65", expr="soft")
me0.set("L66", hidden=True)
me0.jump("L68", [ST[0], LY - 0.85, TOP], hidden=False, **{**STAND, "arms": [88, 88], "yaw": 180}, expr="soft")
me0.jump("L69", STOOL, **P(SIT, expr="neutral"))
me0.set("L71", arms=[68, 68])
me0.jump("L74", [1.3, -2.55, 0.0], **{**STAND, "arms": [68, 68], "yaw": 180}, expr="smirk")

# --- arthur
ar = Actor(seat(5))
ar.set(0, pos=seat(5), hidden=True, expr="neutral", **P(SIT))
ar.jump("L08", seat(5), hidden=False, expr="neutral", arms=[22, 22], look=[0, -0.4])
ar.set("L10", look=[0, -0.4])
ar.jump("L12", seat(5), hidden=True)
ar.jump("L13", [-2.2, -2.45, 0.0], hidden=False, **{**STAND, "yaw": 0}, expr="neutral")
ar.walk("L13+0.45", [-2.2, -2.45, 0.0])
ar.walk("L14.2+0.9", [2.8, -2.55, 0.0], yaw=180)
ar.set("L14.2+1.4", arms=[68, 68], yaw=180)
ar.jump("L19", seat(5), **P(SIT, arms=[22, 22], look=[0, -0.4]))
ar.jump("L28", [4.9, -4.4, 0.0], **{**STAND, "yaw": 0})
ar.walk("L28>", [SIDE_X, -3.8, 0.0])
ar.jump("L29", seat(5), hidden=True)
ar.jump("L30", seat(5), hidden=False, **P(SIT, arms=[22, 22], look=[0, -0.4]))
ar.set("L36", arms=[22, 130], tremble=1.8)
ar.set("L36.1>", tremble=0.0)
ar.set("L36.2", arms=[22, 22], tremble=0.0)
ar.jump("L41", seat(5), hidden=True)
ar.jump("L55", [0.2, -2.7, 0.0], hidden=False, **{**STAND, "yaw": 180}, expr="neutral")
ar.walk("L55+1.8", [2.8, -2.55, 0.0], yaw=180)
ar.jump("L56", [-2.3, -2.5, 0.0], **{**STAND, "yaw": 0, "arms": [60, 60]})
ar.jump("L57", [-2.3, -2.5, 0.0], hidden=True)
ar.jump("L63", [ST[0], LY + 0.25, TOP], hidden=False, **{**STAND, "yaw": 0}, expr="neutral")
ar.set("L65", hidden=True)
ar.set("L66", hidden=False, head=[0, 24], expr="soft")
ar.set("L68", head=[0, 0], expr="soft")
ar.jump("L69", seat(5), hidden=False, **P(SIT, arms=[22, 22], expr="neutral"))
ar.jump("L74", [2.3, -2.55, 0.0], **{**STAND, "arms": [68, 68], "yaw": 180}, expr="soft")

ar.jump("L76", [2.3, -2.55, 0.0], hidden=True)
me0.jump("L76", [1.3, -2.55, 0.0], hidden=True)

# --- the Turned: head turned right round (so its face looks at me and the haircut faces the dryers), arms hung back
DOWN, SIDE = -1.0, 1.0                   # look keys: the face is upside down, so image-down is face-up (+x is toward chair six)
TURN = dict(yaw=180, head=[0, 0], arms=[-20, -20], side=[10, 10], expr="neutral", look=[0, 0], sit=True, bend=0,
            lean=0, tremble=0.0, blink=False)
tu = Actor(seat(4))
tu.set(0, pos=seat(4), hidden=True, **TURN)
tu.jump("L19", seat(4), hidden=False, **TURN)
tu.jump("L30", seat(3), **TURN)
tu.jump("L41", seat(3), hidden=True)
tu.jump("L42", seat(5), hidden=False, **TURN)
tu.jump("P01+0.3", seat(5), hidden=True)
tu.jump("L48.3", seat(0), hidden=False, **{**TURN, "lean": 7, "look": [0, 0.0], "head": [0, 0]})
tu.set("L49", look=[0, 0])
tu.set("L51", look=[0, DOWN])
tu.set("L51.2+0.45", look=[SIDE, 0.0])
tu.set("L52.2+0.1", look=[0, DOWN])
tu.set("L53", look=[0, DOWN])
tu.set("L53.1", look=[SIDE, 0.0])
tu.set("L53.2", look=[0, DOWN])
tu.set("L53.3", look=[0, DOWN])
tu.set("L53.3+0.6", look=[SIDE, 0.0])
tu.set("L53.3+1.0", look=[0, DOWN])
tu.jump("L55", seat(0), hidden=True)
tu.jump("L58", seat(0), hidden=False, **{**TURN, "lean": 7, "look": [0, DOWN]})
tu.jump("L59", seat(0), hidden=False, **{**TURN, "lean": 7, "head": [20, 0], "look": [0, DOWN]})
tu.jump("L60", seat(0), hidden=True)

tu.keys.append({"from": "L19", "to": "L60", "mouth": [1.0, 1.0]})
acting = {"me": me.keys, "me0": me0.keys, "arthur": ar.keys, "turned": tu.keys}

# ---------------------------------------------------------------------------------------------------- cues
cues = [
    {"at": 0, "name": "coat7", "on": True, "floor": True},
    {"at": "L14.2", "name": "d7door", "open": 1.0, "dur": 0.35},
    {"at": "L13.1", "name": "d7glow", "to": 0.03, "dur": 1.0},
    {"at": "L16", "name": "coat7", "on": False},
    {"at": "L16", "name": "held", "on": True},
    {"at": "L18", "name": "held", "on": False},
    {"at": "L34.2", "name": "hook", "a": True},
    {"at": "L40", "name": "hook", "a": False},
    {"at": "L72", "name": "hook", "a": True, "b": True},
    # the stutter: one held shot (S47), the tubes ramp down over 1.0 s, hold through P01, ramp back over 1.0 s
    {"at": "L45", "name": "tubes", "to": 0.12, "dur": 1.1},
    {"at": "P01>", "name": "tubes", "to": 1.0, "dur": 1.0},
    {"at": "L47", "name": "drums", "on": False},
    {"at": "L48.3", "name": "drums", "on": True},
    {"at": "L56", "name": "coat7", "on": False, "floor": False},
    {"at": "L56", "name": "d7door", "open": 1.0, "dur": 0.01},
    {"at": "L56+0.4", "name": "coat7", "on": True, "floor": True},
    {"at": "L56+0.5", "name": "d7door", "open": 0.0, "dur": 0.7},
    {"at": "L57", "name": "fluff", "on": True},
    {"at": "L61.1", "name": "tstack", "on": True, "pos": [-3.15, -1.65]},
    {"at": "L62", "name": "tstack", "on": False},
    {"at": "L62", "name": "stack", "on": True},
    {"at": "L63", "name": "scarf", "on": True},
    {"at": "L69", "name": "stack", "on": False},
    {"at": "L69", "name": "scarf", "on": False},
    {"at": "L71", "name": "tstack", "on": True, "pos": [-0.2, -1.65]},
    {"at": "L69", "name": "fluff", "on": False},
]

fx = [
    {"at": "L48.3", "kind": "shake", "dur": 0.35, "amp": 0.45},
]

sfx = [
    {"at": "L13.1", "kind": "buzzer", "db": -12, "dur": 0.45},
    {"at": "L13.1+0.6", "kind": "click", "db": -16},
    {"at": "L14.2", "kind": "door", "db": -26},
    {"at": "L12", "kind": "click", "db": -22},
    {"at": "L12+0.35", "kind": "click", "db": -22},
    {"at": "L12+0.6", "kind": "click", "db": -23},
    {"at": "L12+0.8", "kind": "click", "db": -22},
    {"at": "L12+1.0", "kind": "click", "db": -24},
    {"at": "L18", "kind": "whoosh", "db": -26},
    {"at": "L24", "kind": "creak", "db": -26, "dur": 0.7},
    {"at": "L31", "kind": "thud", "db": -26},
    {"at": "L35", "kind": "creak", "db": -27, "dur": 0.6},
    {"at": "L36.1>", "kind": "click", "db": -30},
    {"at": "L41", "kind": "door", "db": -22},
    {"at": "L45", "kind": "hum_sweep", "db": -13, "dur": 1.2},
    {"at": "L45+0.1", "kind": "glitch", "db": -28, "dur": 0.7},
        {"at": "L48.3", "kind": "hit", "db": -8, "keep": True},
    {"at": "L48.3+0.03", "kind": "sting", "db": -14, "dur": 2.4, "keep": True},
    {"at": "L57", "kind": "creak", "db": -34, "dur": 0.6},
    {"at": "L63", "kind": "door", "db": -22},
    {"at": "L76>-0.05", "kind": "glide", "db": -12, "dur": 1.2},
    {"at": "L76>-0.02", "kind": "bell", "db": -17},
]

sections = [
    {"at": 0, "voices": ["drone", "pad"], "energy": 0.35},
    {"at": "L05", "voices": ["drone", "pad", "pulse"], "energy": 0.4},
    {"at": "L13", "voices": ["drone", "pulse"], "energy": 0.4},
    {"at": "L15", "voices": ["drone", "pad", "pulse"], "energy": 0.4},
    {"at": "L19", "voices": ["drone", "pad", "pulse"], "energy": 0.5},
    {"at": "L30", "voices": ["drone", "pad", "pulse"], "energy": 0.55},
    {"at": "L41", "voices": ["drone", "pulse"], "energy": 0.6},
    {"at": "L45", "voices": ["drone", "pad"], "energy": 0.4},
    {"at": "L48.3", "voices": ["drone", "pad", "pulse"], "energy": 0.8},
    {"at": "L54", "voices": ["drone", "pad"], "energy": 0.5},
    {"at": "L59", "voices": ["pad", "drone"], "energy": 0.4, "mode": "major", "root": 48},
    {"at": "L69", "voices": ["pad", "drone"], "energy": 0.4, "mode": "major", "root": 48},
]

story = {
    "slug": "ep24-wash-cycle",
    "title": "The dryer nobody started had a warm coat inside",
    "made_for_kids": False,
    "premise": "My washer breaks in the first freeze, so I take my wash to an all-night laundromat and sit at the long folding table behind a row of six orange chairs. The first night a dryer I never used buzzes, and inside is a warm green wool coat in my size. From the second night a person built backwards sits in the chairs with its face on the back of its head, one chair nearer each night.",
    "twist": "The coat belongs to the quiet old man at the far end, who put it in the dryer while I was at the change machine, then sat in a jumper all week so I wouldn't ask. On night four his chair is empty, and the Turned sits in it and then leans its face to mine, its eyes counting between the coat and his chair. A stranger's coat was a neighbour looking after me.",
    "world": "A narrow all-night laundromat on a wet corner: cream wall tiles, a chequered grey floor, a wall of twelve steel front-loaders, six bolted orange plastic chairs facing six round dryer doors, a long pale wood folding table behind the chairs, a change machine and a soap machine with blank coloured buttons, long fluorescent tubes, rain on the street outside and a side door to stairs up to the flat above.",
    "key_color": "#b99cf2",
    "gap": 0.14,
    "tail": 0.25,
    "voice": {"voice": "am_adam", "tempo": 1.03, "rate": 1.45},
    "look": {"fog": "#3a4254", "fog_density": 0.02, "fog_start": 7.0, "sky": "#0d1018", "sky_strength": 1.0,
             "exposure": 0.1},
    "grade": {"shadows": [-0.02, 0.0, 0.05], "highlights": [0.03, 0.01, -0.03], "saturation": 1.0, "contrast": 1.05,
              "vignette": 0.3, "bloom": 0.25, "grain": 0.012, "red_line": 0.79, "red_lift_blue": 0.5},
    "rain_shots": RAIN,
    "lamp_shots": ["S01", SID["L44"]],
    "tally_shots": [SID["L31b"]],
    "hook_lamp_shots": [SID["L72"], SID["L76"]],
    "scare_shots": [SID[k] for k in ("L48.3", "L49", "L50", "L51", "L51.2+0.45", "L52.2+0.1", "L53.3", "L54", "L58")],
    "shoe_shots": [SID["L23"]],
    "hide_wall_shots": [SID["L68"]],
    "stair_fill_shots": [SID["L62"], SID["L65"], SID["L68"]],
    "coat_shots": [SID["L51.2"], SID["L53"], SID["L53.2"]],
    "cool_shots": [SID["L66"]],
    "phonemes": {"Arthur": "ˈɑɹθəɹ", "turned": "tˈɜɹnd", "drums": "dɹˈʌmz"},
    "creature_dim": {SID[k]: v for k, v in DIM.items()},
    "cast": cast,
    "lines": lines,
    "shots": shots,
    "acting": acting,
    "cues": cues,
    "fx": fx,
    "music": {"root": 48, "mode": "minor", "bpm": 66, "seed": 24, "sections": sections},
    "sound": {
        "floor": "stone", "steps_db": -26,
        "ambience": [
            {"kind": "hum", "from": 0, "to": "end", "lufs": -34},
            {"kind": "water", "from": 0, "to": "L45", "lufs": -40},
            {"kind": "water", "from": "L48.3", "to": "end", "lufs": -40},
            {"kind": "rain", "from": 0, "to": "end", "lufs": -40},
            {"kind": "rain", "from": "L28", "to": "L30", "lufs": -32},
            {"kind": "rain", "from": "L03", "to": "L05", "lufs": -33},
            {"kind": "room", "from": 0, "to": "end", "lufs": -42},
        ],
        "sfx": sfx,
        "music_drops": [
            {"from": "L47", "to": "L48.3", "keep": ["hit", "sting"]},
        ],
    },
}
OUT.write_text(json.dumps(story, indent=1, ensure_ascii=False))
print("wrote", OUT, len(shots), "shots")
