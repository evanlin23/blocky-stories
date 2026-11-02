"""Writes ../story.json for ep44 "In this world, your moon fills while you sleep" (script.md).

Run from anywhere: python stories/ep44-sleeper-car/generator/make_story.py
The words are in lines.json next to this file. Everything else is here: the cast, the shots, the acting, the cues
set.py reads (door slides, the lamp fade, the glass blanket), the effects, the score and the sound.

Places (set.py's OX): each is its own island along +x. Coordinates below are world coordinates: a person's "pos" is
their feet (for a seated person, their hips' x, y and a z that puts the thighs on the seat), z = 0 is the floor.
"""
import json
import math
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE.parent / "story.json"
lines = json.loads((HERE / "lines.json").read_text())

OX = {"plat": 0, "intv": 60, "offc": 120, "kitch": 180, "comm": 240, "flat": 300, "text": 360, "cab": 420,
      "cor": 480, "caf": 540}
HZ = 1.57                       # a standing head's centre above the feet
SEAT_Z = lambda h: round(h - 0.51, 3)   # root z that puts the thighs on a seat of height h


def P(zone, x, y, z=0.0):
    return [round(OX[zone] + x, 3), y, z]


# ------------------------------------------------------------------------------------------------- the cast
def person(skin, shirt, pants, hair="cap", hair_c="#2a1d15", pattern="solid", pattern_c=None, bw=0.85, **kw):
    d = {"age": "adult", "skin": skin, "shirt": shirt, "pants": pants, "shoes": "#2a2420", "sleeves": "long",
         "hair": hair, "hair_c": hair_c, "body_width": bw, "face": {"eyes": "round", "brows": True}}
    if pattern != "solid":
        d["pattern"] = pattern
        d["pattern_c"] = pattern_c
    for k, v in kw.items():
        if k == "face":
            d["face"] = {**d["face"], **v}
        else:
            d[k] = v
    return d


TWIN_HAIR = dict(hair="swoop", hair_c="#3a2518")
cast = {
    "me": person("#f0c7a6", "#4a5f84", "#6b6f78", bw=0.8, extras=["hooddown"], **TWIN_HAIR,
                 face={"cheeks": "#e8a08a"}),
    "ash": person("#cdb9a6", "#c99a2e", "#6b4a2e", bw=0.8, pattern="knit", pattern_c="#a67c1a", **TWIN_HAIR,
                  face={"eyes": "tired", "bags": True}),
    "ash2": person("#f0c7a6", "#c99a2e", "#6b4a2e", bw=0.8, pattern="knit", pattern_c="#a67c1a", **TWIN_HAIR,
                   face={"eyes": "round", "cheeks": "#e98d7a"}),
    "t1": person("#e0b48a", "#7b4a8a", "#3a3a48", hair="buzz", hair_c="#1f1a17", face={"cheeks": "#d98a70"}),
    "t2": person("#f1c9a0", "#4a7a6a", "#3a4050", hair="long", hair_c="#6b3a22", face={"eyes": "tired", "bags": True}),
    "t3": person("#8d5a3b", "#c26b3a", "#2e3340", hair="none", hat="beanie", hat_c="#2a3a5a"),
    "intv": person("#e6c19c", "#8a7a5a", "#3a3a3a", pattern="plaid", pattern_c="#5a4a30", hair="cap",
                   hair_c="#8b8a86", collar="#efe6cf"),
    "cand": person("#d9a679", "#3f7a4f", "#2f3a44", hair="bun", hair_c="#241810", extras=["tie"], extra_c="#e8e2d0",
                   face={"eyes": "lashes"}),
    "napper": person("#f1c9a0", "#6a7fb0", "#3b4150", pattern="stripes", pattern_c="#e8e8f0", hair="spiky",
                     hair_c="#5a3a22", extras=["tie"], extra_c="#a83a3a", face={"cheeks": "#e98d7a"}),
    "co1": person("#7a4a2e", "#9a6a6a", "#3b3640", hair="cap", hair_c="#15110e", face={"brows": True}),
    "co2": person("#f1c9a0", "#7d8a9a", "#40434a", hair="long", hair_c="#c9b08a", face={"eyes": "lashes"}),
    "cA": person("#e8b88e", "#b02a3a", "#5a2a30", hair="swoop", hair_c="#6b3a22", sleeves="long"),
    "cB": person("#f1c9a0", "#3f6c9c", "#4a4f5a", pattern="plaid", pattern_c="#d8d0b8", hair="cap", hair_c="#241810",
                 face={"freckles": True}),
    "c1": person("#e0b48a", "#6e7a4a", "#33362e", hair="cap", hair_c="#241810", extras=["coat"], bw=0.65),
    "c2": person("#8d5a3b", "#8a4a3a", "#33302e", hair="buzz", hair_c="#15110e", extras=["coat"], bw=0.65,
                 face={"eyes": "tired", "bags": True}),
    "c3": person("#f1c9a0", "#4a5a7a", "#2e3340", hair="long", hair_c="#7a4a2a", extras=["coat"], bw=0.65,
                 face={"eyes": "lashes"}),
    "c4": person("#d9a679", "#7a6a4a", "#3a342c", hair="none", hat="beanie", hat_c="#6a3a3a", extras=["coat"], bw=0.65),
    "att": person("#e6c19c", "#f3efe6", "#2a2a30", hair="cap", hair_c="#15151a", extras=["apron"], extra_c="#6e2a2e",
                  collar="#6e2a2e", face={"brows": True}),
    "ash3": person("#f0c7a6", "#c99a2e", "#6b4a2e", bw=0.8, pattern="knit", pattern_c="#a67c1a", extras=["backpack"],
                   extra_c="#6e2a2e", **TWIN_HAIR, face={"eyes": "round", "cheeks": "#e98d7a"}),
    "glass": {"age": "adult", "offscreen": True},
}
PEOPLE = [k for k in cast if k != "glass"]


# ------------------------------------------------------------------------------------------------- cameras
def c(*keys):
    return [list(k) for k in keys]


def mv(p0, t0, l0, p1=None, t1=None, l1=None):
    if p1 is None:
        return c([0, p0, t0, l0])
    return c([0, p0, t0, l0], [1, p1, t1 if t1 is not None else t0, l1 if l1 is not None else l0])


def face_cam(hd, yaw, dist=2.4, off=0.0, lens=34, dz=0.0, push=0.0, mt=0.63, moon=True, aim=None, tilt=0.0):
    """A camera in front of a face (hd = head centre), with the moon's top just inside the frame."""
    a = math.radians(yaw + off)
    d = (math.sin(a), -math.cos(a))

    def at(dist_):
        hf = 2 * dist_ * 12 / lens
        tz = aim if aim is not None else (hd[2] + mt - 0.44 * hf if moon else hd[2] - 0.05)
        return ([round(hd[0] + d[0] * dist_, 3), round(hd[1] + d[1] * dist_, 3), round(hd[2] + dz, 3)],
                [hd[0], hd[1], round(tz + tilt, 3)])
    p0, t0 = at(dist)
    if not push:
        return mv(p0, t0, lens)
    p1, t1 = at(dist - push)
    return mv(p0, t0, lens, p1, t1, lens)


def hd(pos, z=HZ):
    return [pos[0], pos[1], pos[2] + z]


def lying_head(pos):
    """Head centre of a person lying on their back, head toward +y (lean -90, yaw 0): feet at pos."""
    return [pos[0], round(pos[1] + 1.57, 3), pos[2]]


# --------------------------------------------------------------------------------------------- places, poses
# the cabin
BOT = [OX["cab"] + 0.6, -1.3, 0.79]      # Ash lying on the bottom bunk, head to +y
TOP = [OX["cab"] + 0.6, -1.3, 2.09]      # me on the top bunk: mattress top 1.92 + 0.17
GL_TOP = [OX["cab"] + 0.27, -1.22, 1.92 + 0.36]   # the Glass One on its side in my bunk
# the corridor
CX = OX["cor"]
GL1 = [CX, 19.3, 0.0]
GL3 = [CX - 0.35, 4.4, 0.0]
DOORY = 4.4

SH = []   # (id, at, cam, opts)


_n = [0]


def shot(at, cam, sid=None, **opt):
    if sid is None:
        _n[0] += 1
        sid = f"S{_n[0]:02d}"
    SH.append((sid, at, cam, opt))
    return sid


# ---- the hook: a bright morning platform (S01 to S12)
CAB = OX["cab"]
HB = lying_head(BOT)             # Ash's head on the bottom bunk
HT = lying_head(TOP)             # my head on the top bunk
lie = lambda h, dist=1.7, lens=22, dz=0.3, push=0.0: face_cam(h, -90, dist, 0, lens, dz=dz, push=push)
shot(0, mv([0.0, -5.6, 1.45], [0.0, 0.0, 0.51], 35, [0.0, -4.7, 1.45], [0.0, 0.0, 0.51], 35), hand=0.004)       # S01
T1, T2, T3 = [-0.62, 0.8, 0.0], [0.0, -0.1, 0.0], [0.62, 0.8, 0.0]
shot("L02", face_cam(hd(T1), 0, 2.7, 4, 34, mt=0.72, push=0.1))                                         # S02
shot("L03", face_cam(hd(T2), 0, 2.5, -6, 34, push=0.1))                                                 # S03
shot("L04", mv(P("intv", 0.0, -1.0, 1.5), P("intv", 0.0, 2.9, 1.5), 26, P("intv", 0.0, -0.6, 1.5),
               P("intv", 0.0, 2.9, 1.5), 26))                                                           # S04
shot("L05", mv(P("offc", 0.0, -1.3, 1.5), P("offc", 0.0, 3.0, 1.3), 27,
               P("offc", 0.0, -0.9, 1.5), P("offc", 0.0, 3.0, 1.3), 27))                                # S05
shot("L06", mv(P("kitch", 0.0, -1.8, 1.55), P("kitch", 0.0, 1.9, 1.15), 27,
               P("kitch", 0.0, -1.5, 1.55), P("kitch", 0.0, 1.9, 1.15), 27))                            # S06
shot("L07", mv(P("comm", 0.0, -5.8, 0.9), P("comm", 1.15, -1.2, 1.5), 34,
               P("comm", 0.1, -5.4, 0.9), P("comm", 1.15, -1.2, 1.5), 34))                              # S07
ME_PL = [0.3, 0.5, 0.0]
shot("L08", face_cam(hd(ME_PL), 0, 2.4, 0, 34))                                                         # S08
shot("L09", mv(P("flat", -0.9, -2.0, 1.25), P("flat", -0.85, 3.0, 0.95), 24,
               P("flat", -0.9, -1.8, 1.25), P("flat", -0.85, 3.0, 0.95), 24))                              # S09
shot("L10", face_cam(hd(ME_PL), 0, 3.1, -8, 30, dz=-0.05, moon=True))                                   # S10
ASH_PL = [1.65, 3.55, 0.0]
ME_PL2 = [0.95, 2.8, 0.0]
shot("L11", face_cam(hd(ASH_PL), 0, 2.7, 0, 34))                                                        # S11
shot("L12", mv([0.1, -1.0, 1.5], [1.3, 3.2, 1.0], 36, [0.9, 0.6, 1.5], [1.62, 3.55, 1.25], 36))          # S12
# ---- the train, the cabin, Ash out, me up
shot("L13", mv(P("text", -3.5, -5.5, 1.3), P("text", 0.0, 5.0, 2.2), 20, P("text", -1.0, -5.5, 1.3),
               P("text", 3.0, 5.0, 2.2), 20), tod="dusk")                                                # S13
shot("L14", mv([CAB - 1.05, 0.0, 1.5], [CAB + 1.0, 0.1, 1.35], 20,
               [CAB - 1.0, 0.0, 1.5], [CAB + 1.0, 0.1, 1.35], 20), tod="dusk")                          # S14
shot("L15", lie(HB, 1.7, 22, 0.35, 0.1), tod="dusk")                                                    # S15
shot("L16", lie(HT, 1.75, 20, 0.15))                                                                    # S16
shot("L16.3", mv([CX + 0.15, 0.1, 1.55], [CX, 9.0, 1.3], 32, [CX + 0.15, 0.7, 1.55], [CX, 9.0, 1.3], 32))   # S17
shot("L17", mv([CX, 4.3, 1.55], [CX, 19.3, 1.5], 42, [CX, 4.3, 1.55], [CX, 19.3, 1.5], 46), hand=0.002)  # S18
shot("L18", mv([CX + 0.1, 10.5, 1.4], [CX, 19.3, 1.3], 50))                                              # S19
shot("L19", mv([CX + 0.12, 12.4, 1.5], [CX, 19.3, 1.4], 34, [CX + 0.1, 11.9, 1.5], [CX, 19.3, 1.4], 34), hand=0.002, dim=0.7)  # S20
shot("L20", mv([CX + 0.55, 13.0, 1.35], [CX, 19.3, 1.25], 30, [CX + 0.5, 12.5, 1.35], [CX, 19.3, 1.25], 30), dim=0.7)   # S21
shot("L21-0.4", mv([CX + 0.05, 14.6, 1.7], [CX, 19.3, 1.75], 32, [CX + 0.04, 14.3, 1.7], [CX, 19.3, 1.75], 32), dim=0.7)  # S22
shot("L21.2", mv([CX + 0.05, 15.4, 1.5], [CX, 19.3, 1.7], 38, [CX + 0.04, 15.3, 1.5], [CX, 19.3, 2.3], 38), dim=0.7)      # S23
ME_C1 = [CX, 4.4, 0.0]
shot("L22.2", face_cam(hd(ME_C1), 180, 2.6, 0, 34, dz=0.05))                                             # S24
shot("L23", lie(HT, 1.75, 20, 0.15), tod=["night", "grey"])                                              # S25
SIT_ASH = [CAB + 0.45, -0.1, SEAT_Z(0.62)]
HS = [CAB - 0.25, -0.1, 1.34]                                                                            # Ash hunched, sitting up
shot("L24", face_cam(HS, -90, 0.92, 18, 13), tod="grey")                                                  # S26
CAF = lambda x, y, z=0.0: P("caf", x, y, z)
ASH_CNT = CAF(-0.55, 12.9)
shot("L25-0.5", face_cam(hd(ASH_CNT), 180, 2.4, 0, 28), tod="grey")                                      # S27
shot("L25.2", face_cam(hd(ASH_CNT), 180, 2.0, 0, 28, push=0.1), tod="grey")                              # S28
ATT = CAF(-0.55, 14.9)
shot("L26", mv(CAF(0.3, 10.9, 1.55), CAF(-0.55, 13.9, 1.5), 26), tod="grey")                             # S29
# ---- afternoon in the cafe car, the nap
BY = 4.8
ME_BOOTH = CAF(1.3, BY - 0.62, SEAT_Z(0.42))
ASH_BOOTH = CAF(1.3, BY + 0.62, SEAT_Z(0.42))
MID_BOOTH = CAF(1.3, BY, SEAT_Z(0.42))
shot("L27", face_cam(hd(ME_BOOTH), -90, 2.6, 0, 24), tod="day")                                          # S30
shot("L28", face_cam(hd(MID_BOOTH), -90, 2.85, 0, 18), tod="day")                                         # S31
shot("L29-0.4", face_cam(hd(ASH_BOOTH), -90, 2.3, 0, 24), tod="day")                                     # S32
shot("L29.2", face_cam(hd(ASH_BOOTH), -90, 2.3, 0, 24, push=0.3), tod="day")                             # S33
# ---- night two
GL2 = [CX - 0.1, 10.4, 0.0]
shot("L30", mv([CX - 0.2, 8.6, 1.5], [CX + 0.3, 5.6, 1.45], 24), tod="night")                            # S34
shot("L31", mv([CX - 0.3, 1.0, 1.6], [CX + 1.5, 7.0, 1.5], 28))                                          # S35
shot("L32", mv([CX - 0.3, 1.0, 1.65], [CX + 1.6, 10.4, 1.6], 60))                                         # S36
shot("L33", mv([CX + 0.3, 3.2, 1.55], [CX - 0.1, 11.0, 1.3], 26))                                        # S37
shot("L34", face_cam(hd(MID_BOOTH), -90, 2.85, 0, 18), tod="grey")                                        # S38
shot("L35", face_cam(hd(ASH_BOOTH), -90, 2.5, 0, 24, push=0.3), tod="grey")                              # S39
shot("L36", face_cam(hd(ASH_BOOTH), -90, 2.2, 0, 24), tod="grey")                                        # S40
# ---- night three
ME_DOOR = [CX - 1.2, DOORY, 0.0]
shot("L37", face_cam(hd(ME_DOOR), 90, 1.8, 0, 24), tod="night")                                          # S41
shot("L38", mv([CX + 0.7, 7.4, 1.5], [CX - 0.5, 4.4, 1.2], 24))                                          # S42
shot("L39", mv([CX + 0.7, 4.4, 1.1], [CX - 0.35, 4.4, 1.0], 12))                                         # S43
shot("L39.2", mv([CX - 1.5, 4.4, 1.6], [CX - 0.35, 4.4, 1.6], 22))                                       # S44
shot("L40", face_cam(hd(ME_BOOTH), -90, 2.6, 0, 24), tod=["night", "grey"])                              # S45
# ---- night four
shot("L41-0.4", lie(HB, 1.7, 22, 0.35))                                                                  # S46
shot("L41.2", mv([CAB - 0.8, 0.27, 1.1], [CAB + 0.6, 0.27, 1.3], 30, [CAB - 0.7, 0.27, 1.1], [CAB + 0.6, 0.27, 1.3], 30))   # S47
ME_CAB_DOOR = [CAB - 1.25, -0.35, 0.0]
shot("L42", face_cam(hd(ME_CAB_DOOR), 90, 1.05, 0, 14, dz=-0.1))                                         # S48
shot("L43", mv([CX, 3.0, 1.5], [CX, 14.0, 1.5], 32, [CX, 3.2, 1.5], [CX, 14.0, 1.5], 32))                 # S49
shot("L44", mv([CX + 0.2, 1.0, 1.7], [CX, 14.0, 1.3], 30))                                                # S50
shot("L45", mv([CX + 0.2, 1.0, 1.7], [CX, 14.0, 1.3], 30))                                                # S51
shot("L46-0.2", mv([CX + 0.1, 5.0, 1.55], [CX, 14.0, 1.4], 32))                                               # S52
ME_STUB = [CAB - 2.0, 0.0, 0.0]
shot("L46.3", face_cam(hd(ME_STUB), 90, 1.8, 0, 20))                                                      # S53
shot("L47", mv([CAB - 2.7, 0.0, 1.7], [CAB + 0.3, -0.4, 2.3], 26))                                       # S54
shot("L48", mv([CAB - 0.95, -1.3, 2.9], [CAB + 0.3, -0.3, 2.0], 22, [CAB - 0.85, -1.2, 2.85], [CAB + 0.3, -0.3, 2.0], 22))                                      # S55
shot("L49", mv([CAB + 0.3, -1.55, 2.95], [CAB + 0.3, 0.3, 2.1], 16, [CAB + 0.3, -1.5, 2.85], [CAB + 0.3, 0.3, 2.1], 16))                                       # S56
shot("L50.1", mv([CAB - 1.15, 0.05, 1.1], [CAB + 0.05, 0.3, 1.68], 20, [CAB - 1.05, 0.08, 1.12], [CAB + 0.05, 0.3, 1.68], 20))                                     # S57
shot("L51", lie(HB, 1.7, 22, 0.35))                                                                      # S58
# ---- the turn
shot("L52", face_cam(hd(ME_BOOTH), -90, 2.6, 0, 24), tod="grey")                                         # S59
shot("L53", face_cam(hd(ASH_BOOTH), -90, 2.3, 0, 24), tod="grey")                                        # S60
shot("L54", face_cam(hd(ASH_BOOTH), -90, 2.4, 0, 24, push=0.2), tod="grey")                              # S61
shot("L54.3", mv([CX + 0.15, 0.1, 1.55], [CX, 9.0, 1.3], 32), sid="S61b")
shot("L55", face_cam(hd(ME_C1), 180, 2.6, 0, 34, dz=0.05))                                               # S62
shot("L55.3", mv([CAB - 2.6, 0.5, 1.6], [CAB + 0.3, 0.0, 1.6], 20))                                      # S63
shot("L56", mv([CAB - 2.6, 0.5, 1.6], [CAB - 1.25, -0.35, 2.15], 22, [CAB - 2.6, 0.5, 1.6], [CAB + 0.6, 0.27, 1.3], 22))   # S64
shot("L56.4", mv([CAB - 2.3, 0.5, 1.4], [CAB + 0.6, 0.27, 1.3], 36), sid="S64b")
shot("L57", face_cam(hd(ME_CAB_DOOR), 90, 1.05, 0, 14, dz=-0.1))                                         # S65
shot("L58", mv([CAB - 0.55, 0.0, 1.15], [CAB - 0.07, -0.05, 1.15], 50), hand=0.0015)                     # S66
shot("L59", mv([CAB - 1.15, -1.0, 2.5], [CAB + 0.6, -0.8, 1.95], 22, [CAB - 1.05, -0.95, 2.45], [CAB + 0.6, -0.8, 1.95], 22))                                                                       # S67
shot("L60", lie(HT, 1.75, 20, 0.15))                                                                     # S68
shot("L61", mv([CAB - 1.1, -1.3, 1.6], [CAB + 0.6, 0.4, 1.75], 17), tod=["night", "dawn"])                # S69
shot("L62", mv([CAB - 1.0, -0.6, 2.7], [CAB + 0.1, 0.1, 2.2], 26), tod="dawn")                           # S70
HA2 = [CAB - 0.15, 0.1, 0.45 + 1.57]
shot("L62.2", face_cam(HA2, 0, 1.5, 0, 20), tod="dawn")                                                   # S71
shot("L63", lie(HT, 1.75, 20, 0.15), tod="dawn")                                                         # S72
shot("L64", mv([1.3, -3.2, 1.5], [0.0, 1.0, 1.15], 30))                                                   # S73
shot("L65", mv([0.0, -5.0, 1.5], [-0.1, 0.0, 1.0], 32, [0.0, -4.3, 1.5], [-0.1, 0.0, 1.0], 32))             # S74
shot("L66", mv([0.0, -5.2, 1.5], [0.0, 0.0, 1.0], 32, [0.0, -4.6, 1.5], [0.0, 0.0, 1.0], 32))                                                  # S75

def plus(ref, d):
    """A time reference moved by d seconds (the ref may already carry an offset)."""
    if isinstance(ref, (int, float)):
        return ref + d
    m = re.match(r"^(.*?)([+-]\d+(?:\.\d+)?)?$", ref)
    base, off = m.group(1), float(m.group(2) or 0)
    return f"{base}{off + d:+.3f}"


AT = {sid: at for sid, at, _, _ in SH}
NX = {sid: (SH[i + 1][1] if i + 1 < len(SH) else "end") for i, (sid, _, _, _) in enumerate(SH)}

# ------------------------------------------------------------------------------------------------- acting
BASE = {"at": 0, "pos": [0, 0, -100], "hidden": True, "expr": "neutral", "yaw": 0, "lean": 0, "bend": 0, "roll": 0,
        "sit": False, "head": [0, 0], "arms": [0, 0], "side": [0, 0], "look": [0, 0], "blink": True}
act = {k: [dict(BASE)] for k in PEOPLE}
last = {k: [0, 0, -100] for k in PEOPLE}


def put(who, at, pos=None, walk=False, **kw):
    """A key for `who` on a cut: a jump to `pos` (or a walk there from the last key if walk=True)."""
    ks = act[who]
    kw.setdefault("blend", 0.0)
    if pos is not None:
        pos = list(pos) + [0.0] * (3 - len(pos))
        if not walk and last[who] != pos:
            ks.append({"at": at, "pos": last[who], "blend": 0.0})
        kw["pos"] = pos
        last[who] = pos
    ks.append({"at": at, **kw})


def gone(who, at):
    act[who].append({"at": at, "hidden": True, "blend": 0.0})


def show(who, sid, pos, until=None, **kw):
    put(who, AT[sid], pos, hidden=False, **kw)
    gone(who, NX[until or sid])


def talk(who, frm, to, amt=0.7):
    act[who].append({"from": frm, "to": to, "mouth": [amt, amt], "flap": True})


def mouth(who, frm, to, a, b):
    act[who].append({"from": frm, "to": to, "mouth": [a, b]})


SITK = dict(sit=True)
# ---- platform: S01 to S03
show("t1", "S01", P("plat", *T1), "S03", yaw=0, expr="smirk", look=[0, 0], head=[0, 0])
act["t1"].append({"at": AT["S02"], "expr": "wide", "blend": 0.0})
mouth("t1", AT["S02"], AT["S03"], 0.85, 0.85)
show("t2", "S01", P("plat", *T2), "S03", yaw=0, expr="worried", look=[0, 0.3], head=[0, 6])
show("t3", "S01", P("plat", *T3), "S02", yaw=0, expr="blank", look=[0, 0])
# ---- montage rooms: S04 to S07
show("cand", "S04", P("intv", -0.55, 2.9, SEAT_Z(0.45)), yaw=0, expr="worried", head=[0, 0], **SITK)
act["cand"].append({"at": plus(AT["S04"], 0.6), "expr": "scared", "blend": 0.0})
show("intv", "S04", P("intv", 0.55, 2.9, SEAT_Z(0.45)), yaw=0, expr="neutral", look=[0, 0], head=[-10, 0], **SITK)
act["intv"].append({"at": plus(AT["S04"], 0.45), "look": [-0.8, -0.9], "head": [-30, -10], "blend": 0.3})
show("napper", "S05", P("offc", 0, 2.9, SEAT_Z(0.45)), yaw=0, expr="soft", head=[0, -12], arms=[0, 0], **SITK)
show("co1", "S05", P("offc", -0.95, 3.6), yaw=0, expr="blank", head=[35, 0], look=[0.8, 0])
show("co2", "S05", P("offc", 0.95, 3.6), yaw=0, expr="worried", head=[-35, 0], look=[-0.8, 0])
show("cA", "S06", P("kitch", -0.62, 1.95, SEAT_Z(0.45)), yaw=0, expr="soft", head=[0, -9], **SITK)
show("cB", "S06", P("kitch", 0.62, 1.95, SEAT_Z(0.45)), yaw=0, expr="blank", head=[-32, 0], look=[-0.8, 0.1], **SITK)
for k, (cn, y) in enumerate((("c1", -2.7), ("c2", -1.8), ("c3", -0.9), ("c4", 0.0))):
    show(cn, "S07", P("comm", 1.15, y, SEAT_Z(0.45)), yaw=-90, expr="blank" if k % 2 else "worried", head=[62, 6],
         look=[0, 0.4], **SITK)
# ---- platform again: me and Ash
show("me", "S08", P("plat", *ME_PL), "S08", yaw=0, expr="smirk", head=[0, 0])
# S09: the old flat, me awake in bed, Ash asleep on the sofa (the bonus plant)
put("me", AT["S09"], P("flat", -1.1, -1.57, 0.72), hidden=False, yaw=0, lean=-90, expr="neutral", blink=False,
    head=[-28, 0], look=[0, 0], arms=[0, 0])
put("ash", AT["S09"], P("flat", 0.8, 5.1, 0.62), hidden=False, yaw=90, lean=-90, expr="asleep", head=[0, 0])
gone("me", NX["S09"])
gone("ash", NX["S09"])
put("me", AT["S10"], P("plat", *ME_PL), hidden=False, yaw=0, lean=0, expr="smirk", head=[8, 0], blink=True,
    arms=[0, 0], side=[16, 16])
gone("me", NX["S10"])
put("ash", AT["S11"], P("plat", *ASH_PL), hidden=False, yaw=0, lean=-8, expr="asleep", head=[0, 12], arms=[0, 0])
mouth("ash", AT["S11"], NX["S12"], 0.5, 0.5)
put("me", AT["S12"], P("plat", *ME_PL2), hidden=False, yaw=0, lean=0, expr="soft", head=[0, 0], side=[0, 0])
gone("me", NX["S12"])
gone("ash", NX["S12"])
# ---- the cabin: S15 Ash out, S16 me up, then the corridor
put("ash", AT["S15"], BOT, hidden=False, yaw=0, lean=-90, expr="asleep", head=[-40, 0], arms=[0, 0])
mouth("ash", AT["S15"], NX["S25"], 0.25, 0.25)
put("me", AT["S16"], TOP, hidden=False, yaw=0, lean=-90, expr="neutral", blink=False, head=[-40, 0], arms=[0, 0], side=[0, 0])
gone("me", NX["S16"])
put("me", AT["S17"], P("cor", 0.0, 2.4), hidden=False, lean=0, expr="worried", head=[0, 0], blink=True)
put("me", AT["S18"], P("cor", 0.0, 4.4), walk=True)
gone("me", AT["S18"])
put("me", AT["S24"], P("cor", 0.0, 4.4), hidden=False, yaw=180, expr="terrified", head=[0, 0], look=[0, 0.2])
gone("me", NX["S24"])
glass = []


_glast = [[0, 0, -100]]


def gput(at, pos=None, **kw):
    kw.setdefault("blend", 0.0)
    if pos is not None:
        if _glast[0] != pos:
            glass.append({"at": at, "pos": _glast[0], "blend": 0.0})
        kw["pos"] = pos
        _glast[0] = pos
    glass.append({"at": at, **kw})


glass.append({"at": 0, "pos": [0, 0, -100], "hidden": True})
gput(AT["S18"], GL1, hidden=False, yaw=180, lean=0, roll=0, arms=[0, 0], side=[0, 0], head=[0, 0])
gput(AT["S21"], yaw=205)       # 3/4: the chest (collar notch) is read through the glass beside the face
gput(AT["S22"], yaw=180)
gput(NX["S24"], hidden=True)
# S25: me awake in the top bunk (Ash still asleep below); the window goes grey
put("me", AT["S25"], TOP, hidden=False, yaw=0, lean=-90, expr="neutral", blink=False, head=[-40, 0])
gone("me", NX["S25"])
gone("ash", NX["S25"])
# S26: morning: Ash sits up, hunched, at the bunk edge
put("ash", AT["S26"], SIT_ASH, hidden=False, yaw=-90, lean=0, expr="neutral", head=[0, -46], bend=52, sit=True, arms=[0, 0])
gone("ash", NX["S26"])
# S27 to S29: the cafe counter
put("ash", AT["S27"], ASH_CNT, hidden=False, yaw=180, lean=0, bend=0, sit=False, expr="neutral", head=[0, 0], look=[0, 0.2], arms=[0, 0])
talk("ash", AT["S27"], plus(AT["S27"], 0.9), 0.6)
act["ash"].append({"at": plus(AT["S27"], 0.9), "expr": "asleep", "head": [0, 18], "blend": 0.7})
put("ash", AT["S28"], ASH_CNT, expr="asleep", head=[0, 22], blend=0.0)
act["ash"].append({"at": plus(AT["S28"], 0.45), "head": [0, 2], "blend": 0.15})
act["ash"].append({"at": plus(AT["S28"], 0.9), "head": [0, 24], "blend": 0.5})
mouth("ash", AT["S28"], NX["S28"], 0.45, 0.45)
put("ash", AT["S29"], ASH_CNT, expr="asleep", head=[0, 20])
gone("ash", NX["S29"])
show("att", "S29", ATT, yaw=0, expr="neutral", look=[0, 0.4], head=[0, 0])
act["att"].append({"at": plus(AT["S29"], 0.3), "look": [0, -0.9], "head": [0, -8], "blend": 0.3})
# S30 to S33: afternoon booth, the nap
put("me", AT["S30"], ME_BOOTH, hidden=False, yaw=-90, lean=0, expr="asleep", head=[0, -12], arms=[0, 0], blink=True, **SITK)
gone("me", NX["S30"])
put("me", AT["S31"], ME_BOOTH, hidden=False, expr="neutral", head=[0, 0], lean=0, bend=0, **SITK)
put("ash", AT["S31"], ASH_BOOTH, hidden=False, yaw=-90, lean=0, bend=0, expr="soft", head=[0, 0], arms=[160, 160], **SITK)
act["ash"].append({"at": plus(AT["S31"], 0.7), "arms": [10, 10], "blend": 0.5})
put("ash", AT["S32"], ASH_BOOTH, expr="smirk", head=[0, 0], arms=[0, 0])
gone("ash", NX["S33"])
gone("me", NX["S33"])
# S34 to S37: night two
put("me", AT["S34"], P("cor", 0.3, 5.6), hidden=False, yaw=125, lean=0, expr="worried", head=[0, 0], look=[0, 0], blink=True)
gone("me", NX["S36"])
gput(AT["S35"], GL2, hidden=False, yaw=180)
gput(NX["S37"], hidden=True)
# S38 to S40: breakfast
put("me", AT["S38"], ME_BOOTH, hidden=False, yaw=-90, expr="neutral", head=[0, 0], lean=0, bend=0, **SITK)
put("ash", AT["S38"], ASH_BOOTH, hidden=False, yaw=-90, lean=0, bend=0, expr="blank", head=[0, 6], look=[-0.4, 0.5], arms=[18, 18], **SITK)
talk("ash", AT["S38"], NX["S38"], 0.5)
act["ash"].append({"at": AT["S39"], "look": [-0.6, 0.6], "expr": "blank", "head": [0, 4], "blend": 0.0})
gone("me", NX["S40"])
gone("ash", NX["S40"])
# S41 to S44: night three, the door
put("me", AT["S41"], ME_DOOR, hidden=False, yaw=90, lean=0, expr="wide", head=[0, 0], look=[0, 0], arms=[0, 0], blink=True)
gone("me", AT["S42"])
gput(AT["S42"], GL3, hidden=False, yaw=90)
gput(NX["S44"], hidden=True)
put("me", AT["S45"], ME_BOOTH, hidden=False, yaw=-90, lean=0, bend=0, expr="neutral", head=[0, 0], blink=True, **SITK)
gone("me", NX["S45"])
# S46 to S48: night four, Ash nearly dark
put("ash", AT["S46"], BOT, hidden=False, yaw=0, lean=-90, bend=0, sit=False, expr="asleep", head=[-40, 0], arms=[0, 0])
gone("ash", AT["S48"])
put("ash", AT["S48"], BOT, hidden=False)
put("me", AT["S48"], ME_CAB_DOOR, hidden=False, yaw=90, lean=0, expr="scared", head=[0, 0], look=[0.3, 0.5], arms=[0, 0], blink=True)
gone("me", NX["S48"])
# S49 to S52: the corridor at three
put("me", AT["S49"], P("cor", 0.0, 12.0), hidden=False, yaw=0, expr="worried", head=[0, 0], look=[0, 0], blink=True)
put("me", AT["S50"], P("cor", 0.0, 7.2), walk=True)
put("me", AT["S51"], P("cor", 0.0, 6.2), walk=True)
gone("me", NX["S51"])
put("me", AT["S53"], ME_STUB, hidden=False, yaw=90, expr="worried", head=[0, 0], look=[0.3, 0.2], arms=[0, 0], blink=True)
# S54 to S58: the Glass One in my bunk
gput(AT["S54"], GL_TOP, hidden=False, yaw=0, lean=-90, roll=90, head=[-65, 0], arms=[0, 0], side=[0, 0])
gput(AT["S57"], [GL_TOP[0] - 0.12, GL_TOP[1], GL_TOP[2] - 0.04], nkm=[0, 0.7071, -0.7071, 0, 0.7071, 0.7071, 1, 0, 0])   # head hung over the bunk edge, face down at Ash
gone("me", AT["S54"])
put("ash", AT["S54"], BOT, hidden=False, expr="asleep")
gone("ash", NX["S58"])
gput(NX["S58"], hidden=True)
# S59 to S61: flash cuts
put("me", AT["S59"], ME_BOOTH, hidden=False, yaw=-90, lean=0, expr="asleep", head=[0, -12], blink=True, **SITK)
gone("me", NX["S59"])
put("ash", AT["S60"], ASH_BOOTH, hidden=False, yaw=-90, lean=0, bend=0, expr="smirk", head=[0, 0], arms=[0, 0], **SITK)
put("ash", AT["S61"], ASH_BOOTH, expr="blank", head=[0, 4], look=[-0.6, 0.6])
gone("ash", NX["S61"])
put("me", AT["S61b"], P("cor", 0.0, 2.4), hidden=False, yaw=180, lean=0, expr="worried", head=[0, 0], blink=True, sit=False, bend=0)
put("me", NX["S61b"], P("cor", 0.0, 4.0), walk=True)
# S62 to S68: the loophole
put("me", AT["S62"], P("cor", 0.0, 4.4), hidden=False, yaw=180, expr="soft", head=[0, -26], look=[0, -0.8], blink=True)
put("me", AT["S63"], ME_CAB_DOOR, hidden=False, yaw=90, expr="soft", head=[0, 0], look=[0, 0], arms=[0, 0])
put("ash", AT["S63"], BOT, hidden=False, yaw=0, lean=-90, expr="asleep", head=[-40, 0])
gone("ash", NX["S64b"])
put("me", AT["S65"], ME_CAB_DOOR, expr="crying", head=[0, 0])
act["me"].append({"at": plus(AT["S65"], 0.9), "expr": "soft", "blend": 0.0})
gone("me", NX["S65"])
# S67: the empty bunk, plain cream blanket (nobody there); I lie down in it at S68
put("me", AT["S68"], TOP, hidden=False, yaw=0, lean=-90, expr="neutral", blink=False, head=[-40, 0], arms=[0, 0])
act["me"].append({"at": plus(AT["S68"], 0.3), "expr": "soft", "blend": 0.0})
put("ash2", AT["S69"], BOT, hidden=False, yaw=0, lean=-90, expr="asleep", head=[-40, 0])
put("me", AT["S69"], TOP, expr="asleep", head=[-40, 0])
gone("ash2", AT["S70"])
put("me", AT["S70"], TOP, expr="asleep", head=[-40, 0])
put("ash2", AT["S70"], P("cab", -0.15, 0.1, 0.45), hidden=False, yaw=90, lean=0, expr="soft", head=[0, 0], arms=[130, 130])
put("ash2", AT["S71"], P("cab", -0.15, 0.1, 0.45), expr="smirk", head=[-88, 0], arms=[130, 130])
gone("ash2", NX["S71"])
put("me", AT["S72"], TOP, expr="soft", head=[-40, 0], blink=True)
gone("me", NX["S72"])
# S73 to S75: the morning platform
put("ash3", AT["S73"], P("plat", 0.0, 1.0), hidden=False, yaw=0, expr="smirk", head=[0, 0], arms=[0, 0], lean=0, bend=0)
mouth("ash3", AT["S73"], AT["S74"], 0.6, 0.6)
put("ash3", AT["S74"], P("plat", 0.4, -1.4), walk=True)
put("ash3", AT["S75"], P("plat", 0.4, -1.4), walk=True)
put("me", AT["S74"], P("plat", -0.8, 0.5), hidden=False, yaw=0, expr="soft", head=[0, 0], lean=0, bend=0, sit=False)
put("me", AT["S75"], P("plat", -0.6, -1.5), walk=True)

act["glass"] = glass

# ------------------------------------------------------------------------------------------------- cues, fx
cues = [
    {"at": "L44", "name": "lamps"},
    {"at": "L37+0.2", "name": "door_cor", "to": 1, "dur": 0.7},
    {"at": "L40", "name": "door_cor", "to": 0, "dur": 0.01},
    {"at": "L42", "name": "door_cab", "to": 1, "dur": 0.01},
    {"at": "L43", "name": "door_cab", "to": 0, "dur": 0.01},
    {"at": "L46.3+0.05", "name": "door_cab", "to": 1, "dur": 0.7},
    {"at": "L47", "name": "lump", "on": True},
    {"at": "L52", "name": "lump", "on": False},
]
fx = [
    {"at": "L50.1", "kind": "punch", "dur": 0.8, "zoom": 1.08, "fade": 0.2},
    {"at": "L19", "kind": "punch", "dur": 0.8, "zoom": 1.06, "fade": 0.2},
]
sfx = [
    {"at": "L19", "kind": "sting", "db": -17, "dur": 1.6},
    {"at": "L26+0.5", "kind": "click", "db": -16},
    {"at": "L26+0.62", "kind": "click", "db": -20},
    {"at": "L46.3+0.05", "kind": "door", "db": -14},
    {"at": "L50.1", "kind": "hit", "db": -10},
    {"at": "L35", "kind": "creak", "db": -30, "dur": 0.9},
    {"at": "L66+0.55", "kind": "glide", "db": -18, "dur": 1.0},   # the closing sound: a low fall in pitch under "while I do"
]
amb = [
    {"kind": "hum", "from": "L13", "to": "end", "lufs": -34},
    {"kind": "wind", "from": "L13", "to": "end", "lufs": -35},
    {"kind": "room", "from": 0, "to": "L13", "lufs": -42},
]
sections = [
    {"at": 0, "voices": ["pad", "drone"], "energy": 0.3},
    {"at": "L08", "voices": ["pad"], "energy": 0.3},
    {"at": "L11", "voices": ["pad", "drone"], "energy": 0.3},
    {"at": "L17", "voices": ["drone", "pulse"], "energy": 0.4},
    {"at": "L23", "voices": ["drone", "pad"], "energy": 0.3},
    {"at": "L30", "voices": ["drone"], "energy": 0.3},
    {"at": "L31", "voices": ["drone", "pulse"], "energy": 0.45},
    {"at": "L34", "voices": ["drone", "pad"], "energy": 0.3},
    {"at": "L37", "voices": ["drone", "pulse"], "energy": 0.45},
    {"at": "L43", "voices": ["drone"], "energy": 0.3},
    {"at": "L47", "voices": ["drone", "pulse"], "energy": 0.6},
    {"at": "L52", "voices": ["pad", "drone"], "energy": 0.3},
    {"at": "L58", "voices": ["drone"], "energy": 0.2},
    {"at": "L60", "voices": ["pad"], "energy": 0.4, "mode": "major", "root": 52},
    {"at": "L64", "voices": ["pad", "choir"], "energy": 0.4, "mode": "major", "root": 52},
]
drops = [
    {"from": "L17-0.6", "to": "L17+0.5"},
    {"from": "L31-0.6", "to": "L31+0.6"},
    {"from": "L47-0.6", "to": "L47+0.6"},
    {"from": "L44", "to": "L45", "keep": []},
]

shots = []
for i, (sid, at, cam, opt) in enumerate(SH):
    s = {"id": sid, "cam": cam, "step": opt.get("step", 2)}
    if i:
        s["at"] = at
    for k in ("hand", "tod", "tod_dur", "dim"):
        if k in opt:
            s[k] = opt[k]
    shots.append(s)

story = {
    "slug": "ep44-sleeper-car",
    "title": "In this world, a moon over your head fills while you sleep",
    "made_for_kids": False,
    "premise": "A little moon floats over everyone's head and fills while they sleep: full after a good night, a thin crescent after a bad one. The narrator's is always full though he hasn't slept a whole night in years. His twin Ash sleeps ten hours and his moon keeps shrinking. On a four-night sleeper train to their father's retirement party, a person of clear glass stands one step nearer their cabin door every night.",
    "twist": "Their moons are crossed: the narrator's fills while Ash sleeps, and Ash's only fills while the narrator does. Every full moon he ever had was made of Ash's sleep. The glass person was keeping the narrator's empty bunk while he walked the corridor, and it's gone once he lies down and sleeps, so the first line means whose sleep it was all along.",
    "world": "A long-distance sleeper train crossing open country at night: a walnut and cream corridor with dim amber lamps and dark windows, a two-berth cabin with a brass ladder, a cafe car with burgundy booths, and a bright morning platform under a glass canopy.",
    "key_color": "#c7b8ff",
    "gap": 0.12,
    "tail": 0.25,
    "voice": {"voice": "am_adam", "tempo": 1.03, "rate": 1.45},
    "look": {"flash_safe": True, "fog": "#141c33", "fog_density": 0.03, "fog_start": 4.0, "sky": "#141c33", "exposure": 0.0},
    "grade": {"shadows": [0.0, 0.0, 0.05], "highlights": [0.03, 0.01, -0.02], "saturation": 1.0, "contrast": 1.05,
              "vignette": 0.3, "bloom": 0.22, "grain": 0.01,
              "red_line": 0.75, "red_lift_blue": 0.35},
    "cast": cast,
    "lines": lines,
    "shots": shots,
    "acting": act,
    "cues": cues,
    "fx": fx,
    "music": {"root": 52, "mode": "dorian", "bpm": 66, "seed": 44, "sections": sections},
    "sound": {"floor": "wood", "steps_db": -26, "ambience": amb, "sfx": sfx, "music_drops": drops},
}
OUT.write_text(json.dumps(story, indent=1, ensure_ascii=False) + "\n")
print("wrote", OUT, f"({len(shots)} shots)")
