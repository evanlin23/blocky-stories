"""Writes ../story.json for "The Fortune Machine Said SATURDAY" (ep135-fortune-dodge, batch 14).
Run: python stories/ep135-fortune-dodge/generator/make_story.py

The words are in lines.json (the script's narration). A character facing -y has yaw 0, +x 90, +y 180, -x -90.
Time references use the script's own chunk numbers (L24.1 is the second slash-chunk of L24): timeline.split_lines
cuts long captions to two or three words and the references are remapped.

Three stages: the midway (0, 0), our house (60, 0), the porch (120, 0). Looks: day / late / dusk / eve / dawn. A look
change is a 0.4 s ramp over the end of the shot before the cut; the one slow change is the 1.5 s dawn at L46.
Nothing in the set moves or blinks; cues only show and hide still objects (set.py).
"""
import json
import math
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT))
from blocky import timeline as T  # noqa: E402

OUT = HERE.parent / "story.json"
REV = 23
orig_lines = json.loads((HERE / "lines.json").read_text())
lines, CHUNKMAP = T.split_lines(orig_lines)
idx = next(i for i, l in enumerate(lines) if l["id"] == "L32")
lines.insert(idx, {"id": "P01", "pause": 0.6, "chunks": [["", ""]]})     # the 0.6 s music drop before L32


def remap(ref):
    if not isinstance(ref, str):
        return ref
    mm = re.match(r"^(L\d+)\.(\d+)(.*)$", ref)
    if mm and mm.group(1) in CHUNKMAP:
        return f"{mm.group(1)}.{CHUNKMAP[mm.group(1)][int(mm.group(2))]}{mm.group(3)}"
    return ref


def remap_all(items):
    for it in items:
        for key in ("at", "from", "to"):
            if key in it:
                it[key] = remap(it[key])


MID, ROOM, PORCH = (0.0, 0.0), (60.0, 0.0), (120.0, 0.0)
MACH, CART, PIE, POSTER, DUNK, LEMON = (4.0, 4.0), (-2.5, 4.0), (-9.5, 6.0), (-13.5, 6.0), (-18.5, 6.0), (11.5, 5.5)
RX, RY = ROOM
PX, PY = PORCH
CX, CY = CART
TX, TY = RX - 4.5, RY + 1.9      # the kitchen table


def yaw_to(p, q):
    return math.degrees(math.atan2(q[0] - p[0], -(q[1] - p[1])))


# ---------------------------------------------------------------------------------------------------- cast
def person(skin, shirt, pants, shoes, hair="cap", hair_c="#2a1d15", extras=(), eyes="round", sleeves="long", height=1.0,
           width=1.0, cheeks=None, **kw):
    d = {"age": "adult", "skin": skin, "shirt": shirt, "pattern": "solid", "pants": pants, "shoes": shoes, "sleeves": sleeves,
         "hair": hair, "hair_c": hair_c, "hat": "none", "face": {"eyes": eyes, "brows": True, "ink": "#24131f"}}
    if cheeks:
        d["face"]["cheeks"] = cheeks
    if extras:
        d["extras"] = list(extras)
    if height != 1.0:
        d["height"] = height
    if width != 1.0:
        d["width"] = width
    d.update(kw)
    return d


BROWN = "#b07a50"
cast = {
    "me": person(BROWN, "#e3b232", "#3a5a8a", "#f6f6f6", hair="cap", hair_c="#2a1d15", sleeves="short", hat="ballcap",
                 hat_c="#d8302a"),
    "ray": person(BROWN, "#d8302a", "#4a4a52", "#3a2c24", hair="cap", hair_c="#eeeeee", extras=["apron"], extra_c="#fbfaf6",
                  height=0.97, width=1.16, pattern="stripes", pattern_c="#fbfaf6"),
    "mom": person(BROWN, "#c9a6ee", "#3f4f7a", "#3a2c24", hair="long", hair_c="#8a3a1e", eyes="lashes", height=0.95),
    "dunk_man": person("#f1c9a0", "#2f78c8", "#e2463a", "#3a2c24", hair="buzz", hair_c="#5a3a22", sleeves="short"),
    "pie_woman": person("#e9b98f", "#ff8fa8", "#3a3a4a", "#f4f4f2", hair="bun", hair_c="#7a3b1e", eyes="lashes",
                        cheeks="#e89078", height=0.95, extras=["apron"], extra_c="#fbfaf6"),
}
H_OF = {n: c.get("height", 1.0) for n, c in cast.items()}
acting = {n: [] for n in cast}
last = {n: None for n in cast}
cues = []
SH = []


def K(who, at, pos=None, **kw):
    p = list(pos) if pos is not None else list(last[who])
    acting[who].append({"at": at, "pos": p, **kw})
    last[who] = p


def TP(who, at, pos, yaw, expr="neutral", **kw):
    """The character is there from this instant (a cut); everything it doesn't set goes back to neutral."""
    if last[who] is not None:
        acting[who].append({"at": at, "pos": list(last[who]), "blend": 0.0})
    st = {"hidden": False, "arms": [0, 0], "side": [0, 0], "head": [0, 0], "lean": 0}
    st.update(kw)
    acting[who].append({"at": at, "pos": list(pos), "blend": 0.0, "yaw": yaw, "expr": expr, **st})
    last[who] = list(pos)


def HIDE(who, at):
    acting[who].append({"at": at, "hidden": True, "blend": 0.0})


def cue(at, name, **kw):
    cues.append({"at": at, "name": name, **kw})


# expressions the script names, in the faces we have
EX = {"uneasy": "sad-smile", "sheepish": "polite", "determined": "smirk", "stunned": "wide", "sad": "worried",
      "proud": "smile"}


def X(e):
    return EX.get(e, e)


# ---------------------------------------------------------------------------------------------------- cameras
FS = 1.28


def _unit(a, b):
    d = [b[0] - a[0], b[1] - a[1]]
    n = math.hypot(*d) or 1.0
    return d[0] / n, d[1] / n


def cam_face(p, yaw, who, d=3.0, off=10.0, lens=34, shift=0.10, hdz=-0.10, tdz=-0.30, d2=None, lens2=None):
    """A camera in front of a standing character at p facing yaw: d metres off (x FS), `off` degrees round, the face a
    little right of centre (shift, m) and in the top third (tdz is where it looks, from the head centre)."""
    hz = p[2] + 1.57 * H_OF[who]
    d = d * FS
    d2 = d2 * FS if d2 else d2

    def at(dd, ll):
        a = math.radians(yaw + off)
        cam = [round(p[0] + dd * math.sin(a), 3), round(p[1] - dd * math.cos(a), 3), round(hz + hdz, 3)]
        fx, fy = _unit(cam, p)
        rx, ry = fy, -fx
        tgt = [round(p[0] - rx * shift, 3), round(p[1] - ry * shift, 3), round(hz + tdz, 3)]
        return [cam, tgt, ll]

    ks = [[0, *at(d, lens)]]
    if d2 or lens2:
        ks.append([1, *at(d2 or d, lens2 or lens)])
    return ks


def cam_at(pos, tgt, lens, pos2=None, tgt2=None, lens2=None):
    ks = [[0, [round(v, 3) for v in pos], [round(v, 3) for v in tgt], lens]]
    if pos2 or tgt2 or lens2:
        ks.append([1, [round(v, 3) for v in (pos2 or pos)], [round(v, 3) for v in (tgt2 or tgt)], lens2 or lens])
    return ks


def push(cam, f=0.1):
    k = cam[0]
    p2 = [round(a + (b - a) * f, 3) for a, b in zip(k[1], k[2])]
    return [k, [1, p2, k[2], k[3]]]


def shot(sid, at, camera, look, **kw):
    SH.append((sid, at, camera, look, kw))


FAR = [0.0, -60.0, 0.0]
for w_ in cast:
    TP(w_, 0, FAR, 0, hidden=True)

# places
ME_MACH = [3.1, 2.3, 0.0]
RAYC = [CX - 0.2, CY + 0.95, 0.0]                 # Ray behind the counter
RAY2 = [CX - 0.8, CY + 0.95, 0.05]                 # Ray in a two-shot
ME2 = [CX + 0.8, CY + 0.95, 0.0]                 # me in a two-shot
cue(0, "apron2", where="hook")

# ===== S01 the hook (L01)
TP("me", 0, ME_MACH, 0, X("uneasy"))
shot("S01a", 0, cam_at([3.55, -1.3, 1.5], [3.55, 3.0, 1.75], 24, [3.55, -0.8, 1.55], [3.55, 3.0, 1.75], 24), "day")
shot("S01b", "L01.2", cam_at([3.3, -0.3, 1.5], [3.3, 3.0, 1.7], 27, [3.25, 0.3, 1.55], [3.3, 3.0, 1.7], 27), "day")
# ===== S02 the machine, low
HIDE("me", "L02")
shot("S02", "L02", cam_at([4.0, -0.4, 0.35], [4.0, 4.0, 2.0], 24, [4.0, 0.6, 0.45], [4.0, 4.0, 2.05], 24), "day", face=False)
# ===== S03 the dunk tank
DK = [DUNK[0], DUNK[1] + 0.2, 2.4]
TP("dunk_man", "L03", DK, 0, "smile")
shot("S03a", "L03", cam_face(DK, 0, "dunk_man", 2.9, 8, 34, d2=2.6), "day")
cue("L03.2", "splash", on=True)
cue("L04", "splash", on=False)
TP("dunk_man", "L03.2", [DUNK[0], DUNK[1] + 0.05, 0.42], 0, X("stunned"))
shot("S03b", "L03.2", cam_face([DUNK[0], DUNK[1] + 0.05, 0.42], 0, "dunk_man", 3.0, 10, 34, tdz=-0.34), "day")
# ===== S04 the pie stand
HIDE("dunk_man", "L04")
PW = [PIE[0], PIE[1] + 0.8, 0.0]
TP("pie_woman", "L04", PW, 0, X("stunned"))
shot("S04", "L04", cam_face(PW, 0, "pie_woman", 3.0, 10, 34, shift=0.22, hdz=-0.12, d2=2.7), "day")
shot("S04b", "L04.2", cam_face(PW, 0, "pie_woman", 2.5, -14, 34, shift=0.2, hdz=-0.12, d2=2.2), "day")
# ===== S06 nobody argues
HIDE("pie_woman", "L06")
M6 = [2.5, 2.4, 0.0]
TP("me", "L06", M6, 8, "neutral")
shot("S06", "L06", cam_at([1.5, -1.3, 1.6], [2.9, 2.8, 1.65], 30, [1.7, -0.9, 1.6], [2.9, 2.8, 1.65], 30), "day")
# ===== S07 Ray at the cart
HIDE("me", "L07")
TP("ray", "L07", RAYC, 0, "smile")
shot("S07a", "L07", cam_face(RAYC, 0, "ray", 3.0, 10, 34, shift=0.12, d2=2.7), "day")
shot("S07b", "L07.3", cam_at([CX + 0.4, CY - 4.0, 1.55], [CX - 0.1, CY + 1.0, 1.6], 30, [CX + 0.2, CY - 3.5, 1.55],
                              [CX - 0.15, CY + 1.0, 1.6], 30), "day")
shot("S07c", "L07.4", cam_face(RAYC, 0, "ray", 2.4, -12, 34, shift=0.12, d2=2.1), "day")
# ===== S09 to S12 the rule
TP("ray", "L09", RAYC, 0, "neutral")
shot("S09", "L09", cam_face(RAYC, 0, "ray", 2.9, 6, 34, shift=0.1, d2=2.3), "day")
TP("ray", "L10", RAYC, 0, "smile")
shot("S10", "L10", cam_face(RAYC, 0, "ray", 2.9, -10, 34, shift=0.12, d2=2.6), "day")
shot("S10b", "L10.2", cam_face(RAYC, 0, "ray", 2.3, 16, 34, d2=2.0), "day")
RAYK = [CX - 2.05, CY - 0.4, -0.2]
KNEEL_CAM = cam_at([RAYK[0] + 0.4, RAYK[1] - 2.8, 1.3], [RAYK[0] + 0.3, RAYK[1], 0.85], 28,
                   [RAYK[0] + 0.4, RAYK[1] - 2.5, 1.3], [RAYK[0] + 0.3, RAYK[1], 0.85], 28)
cue("L11", "kneel", on=True)
cue("L13", "kneel", on=False)
TP("ray", "L11", RAYK, 75, "neutral", arms=[0, 55], side=[0, 0], head=[-55, 15])
shot("S11", "L11", KNEEL_CAM, "dawn")
# ===== S13 my card
HIDE("ray", "L13")
M13 = [3.35, 2.7, 0.0]
cue("L13.1", "mcard", on=True)
cue("L14", "mcard", on=False)
TP("me", "L13", M13, yaw_to(M13, [3.6, 0.0]), "neutral")
shot("S13", "L13", cam_at([4.15, -0.6, 1.2], [3.6, 3.5, 0.85], 24, [4.1, -0.2, 1.2], [3.6, 3.5, 0.85], 24), "day")
# ===== S14
TP("me", "L14", ME_MACH, 0, "scared")
shot("S14a", "L14", cam_face(ME_MACH, 0, "me", 2.8, 10, 34, d2=2.4), "day")
cue("L14.1", "card", on=True)
HIDE("me", "L14.1")
shot("S14b", "L14.1", cam_at([CX + 0.7, CY - 1.0, 1.7], [CX + 0.62, CY - 0.1, 1.08], 38, [CX + 0.65, CY - 0.8, 1.55],
                              [CX + 0.62, CY - 0.1, 1.08], 38), "day", face=False)
# ===== S15 to S17 the plan
M15 = [-0.2, 2.0, 0.0]
TP("me", "L15", M15, 0, X("determined"))
shot("S15", "L15", cam_face(M15, 0, "me", 2.9, 12, 34, d2=2.5), "day")
TP("ray", "L17", [CX + 0.4, CY + 0.95, 0.0], 0, "neutral")
TP("me", "L17", [-0.3, -0.29, 0.0], 27, "neutral")
K("me", "L17", [-0.3, -0.29, 0.0])
K("me", "L17>", [-0.1, -0.75, 0.0])
shot("S17", "L17", cam_at([1.5, -3.2, 1.55], [-2.2, 4.3, 1.3], 28, [1.4, -3.0, 1.55], [-2.2, 4.3, 1.3], 28), "day")
# ===== S18 to S21 Ray asks
HIDE("me", "L18")
TP("ray", "L18", RAYC, 0, "smile", side=[0, 30])
shot("S18", "L18", cam_face(RAYC, 0, "ray", 3.2, 14, 34, d2=2.8), "day")
shot("S18b", "L18.2", cam_face(RAYC, 0, "ray", 2.5, -16, 34, d2=2.2), "day")
TP("ray", "L19", RAYC, 0, "smile")
shot("S19", "L19", cam_face(RAYC, 0, "ray", 2.7, -12, 34, d2=2.4), "day")
HIDE("ray", "L21")
MOM = [TX, TY + 1.0, 0.0]
TP("mom", "L21", MOM, 0, "neutral")
shot("S21a", "L21", cam_face(MOM, 0, "mom", 3.0, 10, 34, d2=2.7), "day")
MEK = [TX - 0.9, TY - 0.7, 0.0]
HIDE("mom", "L21.2")
TP("me", "L21.2", MEK, 0, X("sheepish"))
shot("S21b", "L21.2", cam_face(MEK, 0, "me", 2.9, -10, 34, d2=2.5), "day")
# ===== S22 to S24 behind the lemonade stand
POST = [LEMON[0] - 1.6, LEMON[1] - 2.3]
MEPOST = [POST[0] + 0.42, POST[1] + 0.5, -0.5]
RAYL = [POST[0] + 1.0, LEMON[1] + 1.0, 0.0]
HIDE("me", "L22")
TP("me", "L22", MEPOST, 0, "scared", lean=8)
TP("ray", "L22", RAYL, 0, "smile")
shot("S22", "L22", cam_face(MEPOST, 0, "me", 2.7, -8, 34, d2=2.4), "day")
shot("S22b", "L22.2", cam_face(MEPOST, 0, "me", 2.3, 12, 34, d2=2.05), "day")
HIDE("me", "L23")
RAYC2 = [LEMON[0] - 0.8, LEMON[1] - 1.0, 0.0]
TP("ray", "L23", RAYC2, 0, "smile")
shot("S23", "L23", cam_face(RAYC2, 0, "ray", 3.5, 8, 34, shift=-0.35, d2=3.1), "day")
TP("me", "L24", MEPOST, 0, "scared", lean=8)
TP("ray", "L24", [POST[0] + 0.95, LEMON[1] + 0.9, 0.0], 0, "smile")
shot("S24", "L24", cam_face(MEPOST, 0, "me", 3.0, 8, 34, shift=-0.28, d2=2.7), "day")
# ===== S25 to S28 home
HIDE("ray", "L25")
CB = [RX + 3.0, RY + 3.5, -0.38]
TP("me", "L25", CB, 0, X("uneasy"))
shot("S25", "L25", cam_face(CB, 0, "me", 3.2, 8, 34, d2=2.8), "day")
cue("L27", "patch", i=0)
TP("me", "L27", CB, 0, "neutral")
shot("S27", "L27", cam_face(CB, 0, "me", 3.4, 14, 30, d2=3.0), "day")
# ===== S29 to S31 Saturday night
MOM2 = [TX, TY + 1.0, 0.0]
HIDE("me", "L29")
TP("mom", "L29", MOM2, 0, "crying")
shot("S29", "L29", cam_face(MOM2, 0, "mom", 2.9, 12, 34, d2=2.6, shift=0.16), "eve")
shot("S30", "L30", cam_face(MOM2, 0, "mom", 2.5, -10, 34, d2=2.2, shift=0.16), "eve")
HIDE("mom", "L31")
M31 = [TX + 0.1, TY - 0.8, 0.0]
TP("me", "L31", M31, 0, X("stunned"))
shot("S31", "L31", cam_face(M31, 0, "me", 2.8, 8, 34, d2=2.5), "eve")
# ===== the drop: the shut cart at dusk
HIDE("me", "P01")
cue("P01", "card", on=True)
shot("S31b", "P01", cam_at([0.9, -5.5, 1.8], [0.9, 4.0, 1.6], 28, [0.9, -4.8, 1.8], [0.9, 4.0, 1.6], 28), "dusk", face=False)
# ===== S32 to S40 the reveal
RAYD = [CX + 0.35, CY + 0.95, 0.0]
TP("ray", "L32", RAYD, 0, "neutral")
shot("S32", "L32", cam_face(RAYD, 0, "ray", 3.2, 10, 34, shift=-0.1, d2=2.9), "dusk")
shot("S32b", "L32.3", cam_face(RAYD, 0, "ray", 2.6, -12, 34, shift=-0.12, d2=2.3), "dusk")
HIDE("ray", "L33")
cue("L33", "grillhot", on=True)
cue("L34", "grillhot", on=False)
shot("S33", "L33", cam_at([CX - 2.1 - 0.75, CY - 3.35, 3.0], [CX - 0.75, CY - 0.05, 1.45], 22, [CX - 2.0 - 0.75, CY - 3.2, 3.0], [CX - 0.75, CY - 0.05, 1.45], 22),
     "dusk", face=False, key=3.0, exp=-0.3)
TP("ray", "L34", RAYC, 0, X("sad"))
shot("S34", "L34", cam_face(RAYC, 0, "ray", 2.8, 8, 34, d2=2.5), "dusk")
HIDE("ray", "L35")
cue("L35", "apron2", where="counter")
shot("S35", "L35", cam_at([CX + 0.33, CY - 2.4, 1.9], [CX + 0.33, CY - 0.05, 1.1], 32, [CX + 0.33, CY - 2.0, 1.8], [CX + 0.33, CY - 0.05, 1.1], 32),
     "dusk", face=False)
shot("S35b", "L35.2", cam_at([CX + 0.9, CY - 1.5, 2.1], [CX + 0.1, CY - 0.05, 1.1], 34, [CX + 0.75, CY - 1.3, 2.0], [CX + 0.1, CY - 0.05, 1.1], 34),
     "dusk", face=False)
shot("S36", "L36", cam_at([CX - 0.9, CY - 1.7, 1.5], [CX + 0.15, CY + 0.1, 1.1], 34, [CX - 0.7, CY - 1.4, 1.45], [CX + 0.15, CY + 0.1, 1.1], 34),
     "dusk", face=False)
shot("S38", "L38", cam_at([MACH[0], -0.4, 0.5], [MACH[0], 4.0, 2.0], 24, [MACH[0], 0.6, 0.6], [MACH[0], 4.0, 2.05], 24), "dusk", face=False)
M39 = [MACH[0] - 1.2, 2.2, 0.0]
TP("me", "L39", M39, 0, X("sad"))
shot("S39", "L39", cam_face(M39, 0, "me", 2.8, -10, 34, d2=2.5), "dusk")
M40 = [CX + 0.5, CY + 0.95, 0.0]
TP("me", "L40", M40, 0, "crying")
shot("S40", "L40", cam_at([CX + 0.55, CY - 1.8, 2.1], [CX + 0.55, CY + 0.35, 1.3], 26, [CX + 0.55, CY - 1.65, 2.1], [CX + 0.55, CY + 0.35, 1.3], 26),
     "dusk", cover=True)
# ===== S41 to S45 the night
CBN = CB
TP("me", "L42", CBN, 0, X("stunned"))
shot("S42", "L42", cam_face(CBN, 0, "me", 2.9, -14, 34, d2=2.5), "eve")
HIDE("me", "L43")
TP("ray", "L43", RAYC, 0, "smile")
cue("L43", "apron2", where="hook")
shot("S43", "L43", cam_face(RAYC, 0, "ray", 2.9, -10, 34, shift=0.12, d2=2.6), "day")
shot("S43b", "L43.2", cam_face(RAYC, 0, "ray", 2.3, 14, 34, d2=2.0), "day")
HIDE("ray", "L44")
shot("S44", "L44", cam_at([CX + 0.7, CY - 1.0, 1.7], [CX + 0.62, CY - 0.1, 1.08], 38, [CX + 0.65, CY - 0.8, 1.55], [CX + 0.62, CY - 0.1, 1.08], 38),
     "dusk", face=False)
TP("me", "L45", CBN, 0, X("determined"))
shot("S45", "L45", cam_face(CBN, 0, "me", 2.8, 10, 34, d2=2.4), "eve")
# ===== S46 to S50 dawn
cue("L46", "apron2", where="none")
K46 = [RX - 2.25, RY + 2.9, 0.0]
HIDE("me", "L46")
TP("me", "L46", K46, 0, X("determined"))
shot("S46", "L46", cam_at([RX - 2.35, RY + 0.2, 1.7], [RX - 2.35, RY + 4.4, 1.55], 28, [RX - 2.35, RY + 0.7, 1.7], [RX - 2.35, RY + 4.4, 1.55], 28),
     "dawn", fade=True)
HIDE("me", "L47")
shot("S47", "L47", cam_at([RX + 10.5, RY + 0.4, 1.35], [RX + 10.5, RY + 4.6, 1.2], 28, [RX + 10.5, RY + 1.0, 1.35], [RX + 10.5, RY + 4.6, 1.2], 28),
     "dawn", face=False)
cue("L50", "apron2", where="porch")
RAYP = [PX - 2.95, PY + 4.6, 0.45]
TP("ray", "L48", RAYP, 0, "neutral")
shot("S48", "L48", cam_face(RAYP, 0, "ray", 3.0, 10, 34, shift=-0.1, d2=2.7), "dawn")
shot("S48b", "L48.2", cam_face(RAYP, 0, "ray", 2.3, -14, 34, shift=-0.1, d2=2.05), "dawn")
TP("ray", "L49", RAYP, 0, "warm")
shot("S49", "L49", cam_face(RAYP, 0, "ray", 3.0, -18, 34, shift=-0.1, d2=2.6), "dawn")
shot("S49b", "L49.2", cam_face(RAYP, 0, "ray", 2.3, 16, 34, shift=-0.1, d2=2.05), "dawn")
HIDE("ray", "L50")
shot("S50", "L50", cam_at([PX - 1.9, PY + 1.2, 2.0], [PX - 1.9, PY + 3.5, 1.35], 36, [PX - 1.9, PY + 1.7, 1.95], [PX - 1.9, PY + 3.5, 1.35], 36),
     "dawn", face=False)
cue("L51", "apron2", where="none")
cue("L51", "meapron", on=True)
MEP = [PX + 0.3, PY + 4.6, 0.45]
TP("me", "L51", MEP, 0, X("uneasy"), arms=[22, 22])
shot("S51", "L51", cam_face(MEP, 0, "me", 2.9, 10, 34, d2=2.5), "dawn")
# ===== S52 to S55 the steps
RAYS = [PX - 0.8, PY + 2.25, -0.38]
MES = [PX + 0.8, PY + 2.25, -0.38]
TP("ray", "L53", RAYS, 0, "neutral")
TP("me", "L53", MES, 0, X("sad"))
shot("S53", "L53", cam_face(MES, 0, "me", 2.6, -8, 34, d2=2.3, shift=0.1), "dawn")
TP("ray", "L54", RAYS, 0, "smile")
shot("S54", "L54", cam_face(RAYS, 0, "ray", 2.6, 8, 34, d2=2.3, shift=-0.25), "dawn")
TP("ray", "L55", RAYS, 0, "laugh")
shot("S55", "L55", cam_face(RAYS, 0, "ray", 2.4, -10, 34, d2=2.1), "dawn")
# ===== S56 to S65 the cart is mine
cue("L56", "spatula", on=True)
cue("L57", "spatula", on=False)
HIDE("me", "L56")
TP("ray", "L56", [CX - 0.25, CY + 0.55, 0.05], 0, "smile", arms=[0, 85], side=[0, 0])
shot("S56", "L56", cam_at([CX + 0.0, CY - 2.7, 1.75], [CX + 0.0, CY + 0.5, 1.25], 26, [CX + 0.0, CY - 2.4, 1.75], [CX + 0.0, CY + 0.5, 1.25], 26), "day")
TP("ray", "L57", RAY2, 0, "laugh")
TP("me", "L57", ME2, 0, "laugh")
shot("S57", "L57", cam_at([CX, CY - 4.6, 1.62], [CX, CY + 0.95, 1.55], 26, [CX, CY - 4.2, 1.62], [CX, CY + 0.95, 1.55], 26), "day")
HIDE("ray", "L58")
TP("me", "L58", [CX + 0.1, CY + 0.95, 0.0], 0, "warm")
shot("S58", "L58", cam_face([CX + 0.1, CY + 0.95, 0.0], 0, "me", 2.7, -10, 34, d2=2.4), "day")
HIDE("me", "L61")
RAYK2 = RAYK
cue("L61", "kneel", on=True)
cue("L62", "kneel", on=False)
TP("ray", "L61", RAYK2, 75, "smile", arms=[0, 55], side=[0, 0], head=[-55, 15])
shot("S61", "L61", KNEEL_CAM, "day")
HIDE("ray", "L62")
cue("L62.2", "mcard", on=True)
cue("L63", "mcard", on=False)
M62 = [3.35, 2.7, 0.0]
TP("me", "L62", M62, yaw_to(M62, [3.6, 0.0]), X("uneasy"))
shot("S62", "L62", cam_at([4.15, -0.6, 1.2], [3.6, 3.5, 0.85], 24, [4.1, -0.2, 1.2], [3.6, 3.5, 0.85], 24), "day")
HIDE("me", "L63")
cue("L63", "card2", on=True)
shot("S63", "L63", cam_at([CX + 0.25, CY - 2.2, 2.3], [CX + 0.25, CY - 0.15, 0.95], 36, [CX + 0.25, CY - 2.0, 2.2], [CX + 0.25, CY - 0.15, 0.95], 36),
     "day", face=False)
M64 = [CX + 1.0, CY - 1.4, 0.0]
TP("me", "L64", M64, 0, "smile")
shot("S64", "L64", cam_face(M64, 0, "me", 2.8, 10, 34, d2=2.5), "day")
TP("me", "L65", ME_MACH, 0, "warm")
shot("S65", "L65", cam_at([3.55, -1.3, 1.5], [3.55, 3.0, 1.75], 24, [3.55, -0.4, 1.55], [3.55, 3.0, 1.75], 24), "day")

# ---------------------------------------------------------------------------------------------------- finish
remap_all(cues)
for ks in acting.values():
    remap_all(ks)

shots, names = [], {}
prev_look = None
for i, (sid, at, camera, look, kw) in enumerate(SH):
    s = {"id": sid, "cam": camera, "step": 2, "hand": 0.004}
    kw = dict(kw)
    fade = kw.pop("fade", False)
    kw.pop("cover", None)
    if i:
        s["at"] = remap(at)
    if look != prev_look and prev_look is not None and not fade:
        # the light ramps over the last 0.4 s of the shot before the cut
        cues.append({"at": remap(f"{at}-0.4") if isinstance(at, str) else max(0.0, at - 0.4), "name": "look", "id": look, "dur": 0.4})
    s.update(kw)
    if look and prev_look is None:
        cues.append({"at": 0, "name": "look", "id": look, "dur": 0.0})
    if fade:
        cues.append({"at": remap(at), "name": "look", "id": look, "dur": 2.0})
    prev_look = look
    shots.append(s)
    names[sid] = sid

sfx = [
    {"at": remap("L01.2"), "kind": "thud", "db": -12},
    {"at": remap("L03.3"), "kind": "whoosh", "db": -15},
    {"at": remap("L11.2"), "kind": "click", "db": -16},
    {"at": remap("L47.1"), "kind": "knock", "pattern": [0, 0.3, 0.6], "tone": "hand", "db": -8},
    {"at": remap("L13.1"), "kind": "click", "db": -17},
    {"at": remap("L14.1"), "kind": "thud", "db": -16},
    {"at": remap("L21"), "kind": "click", "db": -18},
    {"at": remap("L27"), "kind": "thud", "db": -16},
    {"at": remap("L35"), "kind": "thud", "db": -17},
    {"at": remap("L44"), "kind": "click", "db": -18},
    {"at": remap("L48"), "kind": "latch", "db": -16},
    {"at": remap("L50"), "kind": "thud", "db": -17},
    {"at": remap("L56"), "kind": "click", "db": -17},
    {"at": remap("L61"), "kind": "click", "db": -16},
    {"at": remap("L62.2"), "kind": "click", "db": -17},
    {"at": remap("L63"), "kind": "thud", "db": -16},
]
music = {
    "root": 43, "mode": "major", "bpm": 108, "seed": 135,
    "sections": [
        {"at": 0, "voices": ["pulse", "piano"], "energy": 0.55},
        {"at": remap("L15"), "voices": ["pulse", "pad"], "energy": 0.38},
        {"at": remap("L27"), "voices": ["pad"], "energy": 0.28, "mode": "minor", "root": 40},
        {"at": remap("L32"), "voices": ["drone", "pad"], "energy": 0.3},
        {"at": remap("L42"), "voices": ["pulse", "pad"], "energy": 0.4},
        {"at": remap("L46"), "voices": ["piano", "pad"], "energy": 0.38, "mode": "major", "root": 43},
        {"at": remap("L55"), "voices": ["pulse", "piano", "pad"], "energy": 0.62},
    ],
}
sound = {
    "floor": "grass", "steps_db": -26,
    "ambience": [],
    "sfx": sfx,
    "music_drops": [{"from": "P01", "to": "P01>"}],
    "rev": REV,
}
remap_all(sound["music_drops"])
remap_all(music["sections"])
polish = {"reveal": [remap("L30"), remap("L38"), remap("L40")], "twist": remap("L38"),
          "hold": ["S11", "S61", "S40", "S63"],
          "sway": ["S22", "S24", "S29", "S30", "S31", "S34", "S39", "S42", "S45", "S53"]}
story = {
    "slug": "ep135-fortune-dodge",
    "title": "The Fortune Machine Said SATURDAY",
    "made_for_kids": False,
    "premise": ("The county fair's fortune machine is never wrong, and my card says I'll break my Uncle Ray's heart on "
                "Saturday, so I dodge him all week."),
    "twist": ("Saturday was the day Ray meant to hand me his hot dog cart, so my hiding is what broke his heart; his own "
              "rule, nothing broken stays broken past breakfast, brings him to my door on Sunday at dawn with two egg "
              "sandwiches and the second apron."),
    "world": ("A bright county fair midway with striped tents, a stopped big wheel, Uncle Ray's red and white hot dog cart "
              "with a striped umbrella, a tall teal fortune machine with a painted gold star, and our house with its porch."),
    "voice": {"voice": "am_adam", "tempo": 1.03, "rate": 1.45},
    "key_color": "#ffcf3a",
    "gap": 0.15,
    "tail": 0.2,
    "fade_in": False,
    "fade_out": False,
    "rev": REV,
    "look": {"style": "closer", "fog": "#bfe6ff", "fog_density": 0.001, "fog_start": 40.0, "sky": "#8fd6ff", "sky_strength": 0.9,
             "exposure": 0.0, "flash_safe": True, "polish": polish},
    "grade": {"shadows": [0.0, 0.0, 0.03], "highlights": [0.03, 0.015, -0.02], "saturation": 1.08, "contrast": 1.05,
              "vignette": 0.2, "bloom": 0.2, "grain": 0.008},
    "homophones": {"5am": "fiveam"},
    "cast": cast,
    "lines": lines,
    "shots": shots,
    "acting": acting,
    "cues": cues,
    "fx": [],
    "music": music,
    "sound": sound,
    "set_moves": [],
    "framing_ok": ["S56"],
}
OUT.write_text(json.dumps(story, indent=1, ensure_ascii=False) + "\n")
print("wrote", OUT, f"({len(shots)} shots, {len(cues)} cues)")
