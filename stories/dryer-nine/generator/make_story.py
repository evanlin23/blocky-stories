"""Writes ../story.json for "Nobody Uses Dryer NINE" (script.md, 2026-11-03).

Run from anywhere: python stories/dryer-nine/generator/make_story.py
The words are in lines.json next to this file. Everything else is here: the cast, the shots, the acting, the cues
set.py reads, the effects, the score and the sound. Shot ids are numbered in order (S01, S02, ...).

Places (set.py's coordinates): the dryer row is along the back wall, door faces at y = 3.2; dryer n is at
x = -4.05 + 0.9 (n - 1), so nine is at x = 3.15, eight at 2.25. The folding table is at (2.5, 0.3). The front windows
are at y = -4.55, the door gap at x = -4.3. The lot, Jonah's truck (x = -0.8, y = -10) and the moon are outside.
Acting yaw: 0 faces -y (toward the windows and most cameras), 180 faces +y (toward the dryers), 90 faces +x.
"""
import json
import math
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE.parent / "story.json"
lines = json.loads((HERE / "lines.json").read_text())
ids = [l["id"] for l in lines]
if "P01" not in ids:   # the 0.6 s hole before "Then nine's door went CLICK."
    lines.insert(ids.index("L26") + 1, {"id": "P01", "pause": 0.6, "chunks": []})

X9 = 3.15
FAR = [0, -200, 0]
SLOT = [X9 + 0.28, 3.147, 1.2]


def c(*keys):
    return [list(k) for k in keys]


def cam(loc, tgt, lens, loc2=None, tgt2=None, lens2=None):
    if loc2 is None and tgt2 is None and lens2 is None:
        return c([0, loc, tgt, lens])
    return c([0, loc, tgt, lens], [1, loc2 or loc, tgt2 or tgt, lens2 or lens])


def key(face, camp, w=120.0, side=0.9, up=0.5):
    px = camp[0] + side
    return {"face": [[round(px, 3), round(camp[1], 3), round(camp[2] + up, 3)], list(face), w]}


# ---------------------------------------------------------------------------------------------------- cast
FACE_STD = {"eyes": "round", "brows": True}


def person(skin, shirt, pants, shoes, hair, hair_c, **kw):
    d = {"age": "adult", "skin": skin, "shirt": shirt, "pants": pants, "shoes": shoes, "sleeves": "long",
         "hair": hair, "hair_c": hair_c, "hat": "none", "face": dict(FACE_STD)}
    d.update(kw)
    return d


cast = {
    "me": person("#f0c7a6", "#ff8a2b", "#2b3350", "#f4f4f4", "swoop", "#4a2f1d", pattern="stripes", pattern_c="#fff0d0",
                 extras=["hooddown"]),
    "jonah": person("#f0c7a6", "#3fae5a", "#4a5a7a", "#e8e8e8", "cap", "#3a2418", pattern="plaid", pattern_c="#1f6b35",
                    collar="#ffffff", height=1.07),
    "basketlady": person("#e0b08a", "#ff7fb0", "#ff5f9a", "#ffffff", "bun", "#3a2418"),
    "towelman": person("#c78f68", "#d9302b", "#3a4a6a", "#2a2a2e", "cap", "#2a2a2e", pattern="plaid", pattern_c="#7a1410",
                       hat="beanie", hat_c="#9aa0a8", width=1.1),
}

keys = {k: [{"at": 0, "pos": FAR, "yaw": 0, "hidden": True, "expr": "neutral"}] for k in cast}
last = {k: FAR for k in cast}


def put(who, at, pos, yaw=None, **kw):
    keys[who].append({"at": at, "pos": last[who]})
    k = {"at": at, "pos": pos, "blend": 0.0, "hidden": False, **kw}
    if yaw is not None:
        k["yaw"] = yaw
    keys[who].append(k)
    last[who] = pos


def walk(who, at, pos, **kw):
    keys[who].append({"at": at, "pos": pos, **kw})
    last[who] = pos


def hide(who, at):
    keys[who].append({"at": at, "hidden": True})


def set_(who, at, **kw):
    keys[who].append({"at": at, "**": 0, **kw} if False else {"at": at, **kw})


SIT_Z = -0.58

# the basket lady swerves wide of nine
put("basketlady", "L03", [1.6, 2.0], expr="neutral", arms=[75, 75])
walk("basketlady", "L03.0+0.4", [2.4, 1.3])
walk("basketlady", "L03.0+0.9", [3.5, 1.2])
walk("basketlady", "L03>", [4.4, 1.8])
hide("basketlady", "L04")
# the towel man folds on eight
put("towelman", "L04", [2.25, 2.55], 180, expr="neutral", arms=[55, 55])
hide("towelman", "L06")
# S07: me with my phone up in front of nine
put("me", "L07", [2.4, 2.3], 180, expr="neutral", arms=[78, 0])
hide("me", "L08")
# S08: the table
put("me", "L08", [0.85, 1.05], 0, expr="smile", arms=[0, 0])
put("jonah", "L08", [0.15, 1.05], 0, expr="smile")
# S09: Jonah at the front window (his truck outside)
put("jonah", "L09", [0.0, -3.4], 0, expr="soft")
hide("me", "L09")
hide("jonah", "L10")
put("me", "L11", [2.8, 2.3], 20, expr="worried")
put("me", "L12", [2.92, 2.35], 180, expr="neutral", arms=[92, 0])
hide("me", "L13")
put("me", "L14.2", [2.8, 1.4], 0, expr="smile", arms=[0, 0])
put("me", "L15", [2.92, 2.35], 180, expr="neutral", arms=[92, 0])
hide("me", "L15.3")
hide("me", "L16")
# L17: everybody else goes home, out the door
put("basketlady", "L17", [-1.8, -1.6], expr="neutral", arms=[75, 75])
walk("basketlady", "L17>", [-4.3, -4.3])
walk("basketlady", "L18", [-4.3, -7.5])
hide("basketlady", "L18+0.4")
put("towelman", "L17", [-1.2, -1.0], expr="neutral", arms=[0, 0])
walk("towelman", "L17>", [-4.2, -4.3])
walk("towelman", "L18", [-4.2, -7.5])
hide("towelman", "L18+0.4")
# L18: arm wrestling across the table
put("me", "L18", [0.4, -0.5], 180, expr="laugh", arms=[90, 0])
put("jonah", "L18", [0.4, 1.1], 0, expr="laugh", arms=[0, 90])
set_("me", "L18.1", expr="wide")
set_("jonah", "L18.1", expr="laugh")
put("jonah", "L19", [4.2, -2.2], -90, expr="laugh", arms=[60, 60])
hide("me", "L19")
hide("jonah", "L21")
# the drum fills and something dark rolls past: me facing nine, scared
put("me", "L24.1", [3.0, 1.5], 180, expr="scared")
put("jonah", "L25", [2.3, 1.5], 0, expr="neutral")
set_("jonah", "L25.0+0.4", yaw=170, blend=0.5, expr="worried")
put("me", "L25", [3.0, 1.5], 180, expr="scared")
put("jonah", "L26", [2.3, 1.5], 170, expr="worried", head=[0, -12])
put("me", "L28", [3.0, 1.5], 180, expr="worried")
hide("me", "L28+0.01")
# L29: the lights go dim; we back toward the table
put("me", "L29", [2.6, 1.7], 180, expr="scared", keep_yaw=True)
put("jonah", "L29", [1.9, 1.7], 180, expr="worried", keep_yaw=True)
walk("me", "L30", [1.6, 1.1], yaw=180)
walk("jonah", "L30", [0.9, 1.1], yaw=180)
put("me", "L31", [2.3, 0.8], 180, expr="scared")
put("jonah", "L31", [1.5, 1.0], 180, expr="worried")
set_("me", "L33", yaw=0, blend=0.45)
put("me", "L35", [2.0, 1.3], 180, expr="scared")
put("jonah", "L35", [1.2, 1.3], 180, expr="worried")
put("me", "L37", [1.55, 1.3], 180, expr="scared")
put("jonah", "L37", [0.85, 1.25], 180, expr="worried")
put("me", "L38", [3.03, 1.6], 180, expr="scared", head=[0, 0])
put("jonah", "L38", [1.9, 1.5], 180, expr="worried")
put("jonah", "L39", [1.9, 1.5], 180, expr="angry", keep_yaw=True)
walk("jonah", "L39>", [2.55, 2.15], yaw=180)
put("me", "L39", [3.03, 1.6], 180, expr="scared")
put("jonah", "L40", [2.55, 2.1], 180, expr="angry", lean=14, arms=[0, 35])
hide("me", "L40")
hide("jonah", "L41")
# L42: sitting on the floor, backs to nine's shut door; Jonah on my left
put("me", "L42", [2.77, 2.95, SIT_Z], 0, expr="soft", sit=True)
put("jonah", "L42", [3.53, 2.95, SIT_Z * 1.07], 0, expr="soft", sit=True)
set_("jonah", "L45", expr="laugh", arms=[110, 110])
set_("me", "L45.2", expr="laugh")
# L48: the sun is up, we stand
put("me", "L48", [2.6, 0.9], 0, expr="soft", sit=False, arms=[0, 0])
put("jonah", "L48", [3.3, 0.9], 0, expr="soft", sit=False, arms=[0, 0])
hide("me", "L49")
hide("jonah", "L49")
# L51: the hug by the truck, then he drives and I stand in the door
put("me", "L51", [4.2, -7.6], 90, expr="soft", arms=[62, 62])
put("jonah", "L51", [4.9, -7.6], -90, expr="soft", arms=[62, 62])
put("me", "L51.2", [-3.9, -3.6], 0, expr="soft", arms=[0, 0])
hide("jonah", "L51.2")
hide("me", "L52")
acting = keys

# ---------------------------------------------------------------------------------------------------- shots
SH = []


def S(at, camspec, **opt):
    SH.append((at, camspec, opt))


FW = [X9, 3.14, 0.78]        # nine's window and timer
TM9 = [X9, 3.15, 1.2]
LOOK_ME = {}

# ---- the hook: close on nine's round window, centred, pushing in
S(0, cam([X9, 1.25, 0.72], [X9, 3.14, 0.72], 40, [X9, 1.55, 0.72]), hand=0.002)
S("L01.3", cam([X9, 1.5, 0.7], [X9, 3.14, 0.66], 40, [X9, 1.85, 0.7]), hand=0.002)
S("L02", cam([X9 + 0.5, 2.2, 1.3], [X9 + 0.28, 3.15, 1.2], 42, [X9 + 0.38, 2.0, 1.27]), hand=0.003)
S("L03", cam([5.0, -2.2, 0.7], [3.1, 2.2, 0.95], 30, [4.9, -2.1, 0.7]))
S("L04", cam([2.7, 2.2, 3.05], [2.7, 3.4, 1.45], 36), hand=0.003)
S("L05", cam([X9, 2.15, 0.66], [X9, 3.14, 0.64], 42, [X9, 1.9, 0.66]), hand=0.002)
S("L06", cam([2.13, 2.0, 1.2], [2.13, 3.15, 1.2], 32, [X9, 2.0, 1.2], [X9, 3.15, 1.2], 32))
S("L07", cam([3.7, 1.9, 1.3], [2.95, 2.85, 1.25], 34, [3.6, 2.0, 1.3]), hand=0.003)
S("L08", cam([-1.9, -1.5, 1.45], [0.55, 1.0, 1.3], 30, [-1.7, -1.3, 1.45]))
S("L08.2", cam([-0.6, -0.4, 1.55], [0.4, 1.05, 1.5], 36, [-0.5, -0.3, 1.55]), hand=0.003)
S("L09", cam([0.6, -2.3, 1.7], [-0.6, -10.0, 2.1], 30), hand=0.003)
S("L10", cam([X9, 2.2, 1.22], [X9, 3.15, 1.2], 40, [X9, 1.85, 1.22]), hand=0.002)
S("L11", cam([2.4, 0.9, 1.55], [2.8, 2.3, 1.5], 38, [2.45, 1.05, 1.55]),
  look={"face": [[2.0, 0.6, 2.2], [2.8, 2.3, 1.5], 140.0], "key2": [[3.6, 2.8, 1.7], [2.8, 2.3, 1.5], 90.0, 60, "#ffb02e"]})
S("L12", cam([3.25, 2.1, 1.3], [X9 + 0.3, 3.1, 1.2], 38, [3.3, 2.3, 1.28]), hand=0.002)
S("L13", cam([X9, 2.1, 1.22], [X9, 3.15, 1.2], 38, [X9, 1.8, 1.22]), hand=0.002)
S("L14", cam([0.3, -1.8, 1.4], [0.3, -12.0, 3.4], 28), hand=0.003)
S("L14.2", cam([2.7, -0.2, 1.55], [2.8, 1.4, 1.5], 36, [2.7, 0.0, 1.55]),
  look={"face": [[2.0, -0.6, 2.2], [2.8, 1.4, 1.5], 120.0], "key2": [[1.2, -1.8, 1.8], [2.8, 1.4, 1.5], 80.0, 60, "#cfe0ff"]})
S("L15", cam([3.3, 1.8, 1.25], [3.3, 3.15, 1.2], 40, [3.3, 1.55, 1.25]), hand=0.002)
S("L15.3", cam([X9, 2.0, 0.66], [X9, 3.14, 0.64], 44, [X9, 1.75, 0.66]), hand=0.002)
S("L16", cam([X9 - 0.3, 2.2, 1.9], [X9 - 0.1, 3.45, 1.45], 34), hand=0.003)
S("L16.3", cam([X9, 2.0, 1.22], [X9, 3.15, 1.2], 38, [X9, 1.7, 1.22]), hand=0.002)
S("L17", cam([4.9, 2.6, 2.1], [-2.0, -2.5, 1.1], 28, [4.8, 2.6, 2.1]), hand=0.004)
S("L18", cam([-1.3, -1.3, 1.1], [0.8, 0.3, 1.2], 34, [-1.2, -1.25, 1.1]), hand=0.003)
S("L18.1", cam([2.4, 0.3, 1.5], [0.4, 0.3, 1.5], 30, [2.3, 0.3, 1.5]), hand=0.003)
S("L19", cam([5.0, -0.2, 1.6], [4.2, -2.2, 1.3], 34, [4.9, -0.3, 1.6]), hand=0.003)
# ---- the drum fills
S("L21", cam([X9, 2.1, 0.66], [X9, 3.14, 0.64], 44, [X9, 1.8, 0.66]), hand=0.002)
S("L22", cam([X9, 1.8, 0.66], [X9, 3.14, 0.64], 52, [X9, 1.6, 0.66]), hand=0.002)
S("L23", cam([X9 + 0.1, 1.9, 0.7], [X9, 3.14, 0.62], 48, [X9 + 0.05, 1.7, 0.66]), hand=0.002)
S("L24", cam([X9, 1.4, 0.64], [X9, 3.14, 0.62], 50, [X9, 1.25, 0.64]), hand=0.002)
S("L24.1", cam([X9, 3.08, 0.66], [3.0, 1.5, 1.5], 32), look={"face": [[3.4, 0.2, 2.2], [3.0, 1.5, 1.5], 130.0]})
S("L25", cam([1.2, 0.1, 1.6], [2.4, 1.5, 1.5], 38, [1.3, 0.2, 1.6]),
  look={"face": [[0.6, -0.4, 2.3], [2.4, 1.5, 1.5], 140.0]})
S("L26", cam([2.0, 0.6, 1.62], [2.3, 1.5, 1.6], 52, [2.05, 0.75, 1.62]),
  look={"face": [[1.3, 0.2, 2.2], [2.3, 1.5, 1.6], 120.0]})
S("L26.3", cam([X9, 2.1, 1.22], [X9, 3.15, 1.2], 40, [X9, 1.9, 1.22]), hand=0.002)
# ---- the door goes (after the 0.6 s drop)
S("L27", cam([3.75, 2.35, 0.72], [3.52, 3.12, 0.62], 44, [3.7, 2.45, 0.7]), hand=0.002)
S("L28", cam([X9, 1.0, 0.12], [X9, 3.0, 0.16], 28, [X9, 0.8, 0.12]), hand=0.002)
S("L29", cam([-3.8, -3.4, 2.5], [2.6, 2.0, 1.0], 24, [-3.5, -3.2, 2.4]), hand=0.003)
S("L29.1", cam([4.3, 0.2, 1.4], [2.2, 1.7, 1.3], 30, [4.2, 0.3, 1.4]),
  look={"rim": [[3.2, 3.0, 1.8], [2.6, 1.5, 1.4], 260.0, 80, "#bcd2ff"], "face": [[1.8, -0.7, 2.2], [2.6, 1.5, 1.4], 70.0]})
S("L30", cam([4.0, 0.5, 0.35], [3.2, 1.4, 0.1], 30, [3.9, 0.6, 0.33]), hand=0.002)
S("L31", cam([3.8, 0.4, 0.6], [X9, 2.6, 1.3], 32, [3.7, 0.5, 0.62]), hand=0.002,
  look={"face": [[2.4, -0.6, 2.0], [X9, 2.4, 0.9], 25.0], "key2": [[X9, 1.4, 0.1], [X9, 2.45, 0.95], 40.0, 70, "#d4e8ff"]})
S("L32", cam([3.0, 0.85, 1.0], [X9, 2.5, 1.62], 36, [3.05, 0.95, 1.02]), hand=0.002,
  look={"face": [[2.3, -0.9, 2.1], [X9, 2.4, 0.95], 30.0], "key2": [[X9, 1.2, 0.12], [X9, 2.45, 0.95], 45.0, 70, "#d4e8ff"]})
S("L33", cam([3.9, 1.0, 1.5], [2.3, 0.8, 1.5], 34, [3.8, 1.0, 1.5]),
  look={"face": [[4.0, 0.0, 2.1], [2.3, 0.8, 1.5], 120.0]})
S("L34", cam([0.8, -2.0, 1.5], [0.3, -14.0, 3.4], 26), hand=0.003)
S("L35", cam([4.3, 0.2, 0.9], [2.8, 2.4, 1.2], 28, [4.2, 0.3, 0.9]), hand=0.002,
  look={"face": [[1.0, -0.2, 2.0], [2.2, 1.4, 1.4], 80.0], "key2": [[X9, 1.3, 0.12], [X9, 2.45, 0.95], 40.0, 70, "#d4e8ff"]})
S("L36", cam([X9, 0.7, 1.3], [X9, 2.52, 1.68], 40, [X9, 0.9, 1.35]), hand=0.002,
  look={"face": [[2.6, 0.8, 1.9], [X9, 2.4, 1.0], 70.0], "key2": [[X9, 1.2, 0.12], [X9, 2.45, 0.95], 45.0, 70, "#d4e8ff"]})
S("L37", cam([0.4, -1.6, 1.5], [2.3, 1.4, 0.45], 24, [0.6, -1.5, 1.5]),
  look={"face": [[0.0, -2.0, 2.3], [2.3, 1.3, 0.5], 90.0]})
S("L38", cam([3.95, 1.05, 1.62], [3.05, 2.1, 1.5], 36, [3.9, 1.1, 1.62]), hand=0.002,
  look={"face": [[4.2, 0.2, 2.2], [3.05, 1.9, 1.5], 80.0], "rim": [[3.5, 3.0, 2.0], [3.05, 2.0, 1.5], 200.0, 70, "#bcd2ff"]})
S("L39", cam([4.4, 0.8, 1.45], [2.3, 1.8, 1.3], 24, [4.3, 0.9, 1.45]),
  look={"face": [[4.6, 0.0, 2.2], [2.5, 1.8, 1.3], 110.0]})
S("L40", cam([4.2, 1.5, 0.8], [2.6, 2.3, 0.95], 24, [4.1, 1.6, 0.82]), hand=0.002,
  look={"face": [[4.4, 0.6, 1.8], [2.5, 2.1, 1.0], 100.0]})
S("L41", cam([X9, 2.0, 0.66], [X9, 3.14, 0.64], 44, [X9, 1.85, 0.66]), hand=0.002)
# ---- held shut
S("L42", cam([X9, 0.5, 0.75], [X9, 3.0, 0.8], 22, [X9, 0.7, 0.75]), hand=0.002,
  look={"face": [[X9, -0.2, 1.8], [X9, 2.9, 0.9], 120.0]})
S("L42.1", cam([4.5, 2.2, 0.62], [3.15, 3.0, 0.62], 22, [4.4, 2.3, 0.62]), hand=0.002,
  look={"face": [[4.8, 1.2, 1.6], [3.15, 2.9, 0.7], 100.0]})
S("L43", cam([X9, 2.0, 0.55], [X9, 3.14, 1.0], 30, [X9, 1.9, 0.6]), hand=0.002)
S("L44", cam([X9, 0.7, 0.85], [X9, 3.0, 0.85], 22, [X9, 0.9, 0.85]), hand=0.002,
  look={"face": [[X9, -0.3, 1.9], [X9, 2.9, 0.9], 120.0]})
S("L45", cam([4.3, 1.6, 0.95], [3.53, 2.95, 0.95], 26, [4.2, 1.7, 0.95]), hand=0.002,
  look={"face": [[4.6, 0.8, 1.9], [3.53, 2.9, 0.95], 100.0]})
S("L45.2", cam([X9 + 0.1, 1.6, 0.8], [X9, 3.0, 0.82], 34, [X9 + 0.1, 1.7, 0.8]), hand=0.002,
  look={"face": [[X9, 0.4, 1.9], [X9, 2.9, 0.9], 110.0]})
S("L47", cam([X9, 2.0, 1.22], [X9, 3.15, 1.2], 40, [X9, 1.85, 1.22]), hand=0.002)
S("L48", cam([2.9, 2.4, 1.45], [1.6, -4.5, 1.7], 28, [2.8, 2.3, 1.45]), hand=0.002)
S("L49", cam([X9, 2.0, 0.66], [X9, 3.14, 0.64], 44, [X9, 1.85, 0.66]), hand=0.002)
S("L50", cam([X9, 2.15, 0.66], [X9, 3.14, 0.64], 42, [X9, 1.9, 0.66]), hand=0.002)
S("L51", cam([4.4, -12.0, 1.5], [4.55, -7.6, 1.3], 34, [4.4, -11.4, 1.5]), hand=0.003)
S("L51.2", cam([-2.9, -2.4, 1.5], [0.0, -9.5, 1.5], 30, [-3.0, -2.5, 1.5]), hand=0.003)
# ---- the next night, and the sting
S("L52", cam([-3.2, -2.8, 1.9], [2.2, 3.0, 0.9], 24, [-2.8, -2.4, 1.85]), hand=0.003)
S("L53", cam([X9, 1.8, 0.78], FW, 40, [X9, 1.55, 0.78]), hand=0.002)
S("L54", cam([X9, 1.5, 0.74], [X9, 3.14, 0.72], 40, [X9, 1.28, 0.74]), hand=0.002)
S("L55", cam([X9, 1.9, 0.78], FW, 40, [X9, 1.75, 0.78]), hand=0.002)

DARK_AT = {"L29.1", "L30", "L31", "L32", "L33", "L35", "L36", "L37", "L38", "L39", "L40"}
for at, camspec, opt in SH:      # in the dark scene the shot lights are small: the drum, the amber and the moon face do the work
    if at in DARK_AT and opt.get("look"):
        for nm in ("face", "rim", "key2"):
            if nm in opt["look"]:
                opt["look"][nm][2] = round(opt["look"][nm][2] * 0.5, 1)
shots, SID = [], {}
for i, (at, camspec, opt) in enumerate(SH):
    sid = f"S{i + 1:02d}"
    s = {"id": sid, "cam": camspec, "step": opt.get("step", 2), "hand": opt.get("hand", 0.004)}
    if i:
        s["at"] = at
    shots.append(s)

# ---------------------------------------------------------------------------------------------------- cues
cues = []


def cue(at, name, **kw):
    cues.append({"at": at, "name": name, **kw})


def timer(at, who, s):
    cue(at, "timer", who=who, s=s)


# the rule meter: nine's timer, and eight's ordinary one
timer(0, 9, "0:41")
timer(0, 8, "0:12")
timer("L06", 8, "0:11")
timer("L06.1", 8, "0:10")
timer("L06.2", 8, "0:09")
timer("L10.2", 9, "0:40")
timer("L13.1", 9, "0:51")
timer("L15.1", 9, "1:01")
timer("L16.3", 9, "1:31")
timer("L16.3+0.35", 9, "3:11")
timer("L16.3+0.7", 9, "5:51")
timer("L16.3+1.05", 9, "7:31")
timer("L35", 9, "7:30")
timer("L42", 9, "7:29")
timer("L45.2", 9, "2:14")
timer("L47", 9, "0:01")
timer("L47.1", 9, "0:00")
timer("L52", 9, "9:40")

# the drum and the moon turn together
cue(0, "spin", v=0.9)
cue("L49", "spin", v=0.0, dur=1.3)
cue("L52", "spin", v=0.9, dur=1.2)
cue("L53", "spin", v=0.18, dur=1.6)
cue(0, "moon", z=6.0)
cue("L14", "moon", z=7.6, dur=2.0)
cue("L30", "moon", show=False)
cue("L52", "moon", show=True)
cue("L52", "moon", z=6.0)

# the drum fills with night; things ride round in it
cue(0, "fill", v=0.0)
cue("L16", "fill", v=0.18, dur=1.0)
cue("L21", "fill", v=0.7, dur=1.4)
cue("L22", "dc", what="bulk", v=1)
cue("L23", "dc", what="bulk", v=0)
cue("L23", "dc", what="sleeve", v=1)
cue("L24", "dc", what="sleeve", v=0)
cue("L24", "dc", what="fingers", v=1)
cue("L24.1", "dc", what="fingers", v=0)
cue("L28", "fill", v=0.9, dur=0.5)
cue("L40", "dc", what="folded", v=1)
cue("L45.2", "dc", what="face", v=1)
cue("L45>", "dc", what="face", v=0)
cue("L48", "dc", what="folded", v=0)
cue("L48", "fill", v=0.0, dur=0.0)
cue("L49", "empty", v=1)
cue("L52", "empty", v=0)
cue("L52", "fill", v=0.6, dur=1.6)
cue("L53", "dc", what="hand", v=1)
cue("L54", "dc", what="face", v=1)

# the door: ajar at the click, wide at the reveal (across a cut), shut again by Jonah's shoulder
cue("L27.2", "door", v=7.0, dur=0.3)
cue("L30", "door", v=88.0, dur=0.0)
cue("L40+0.3", "door", v=0.0, dur=0.6)

# the Night half out, then leaned in toward my face (across the cut at L38), then back in the drum (L40)
cue("L30", "night", show=True)
cue("L30", "nlean", v=0.0)
cue("L38", "nlean", v=0.86, dur=0.0)
cue("L38+0.3", "nlean", v=1.0, dur=1.4)
cue("L40", "night", show=False)
cue("L28", "pool", v=0.0)
cue("L28", "pool", v=0.55, dur=1.2)
cue("L30", "pool", v=0.8, dur=1.0)
cue("L37", "pool", v=1.0, dur=0.6)
cue("L41", "pool", v=0.0, dur=1.6)

# the light: bright room, then the panels near nine dim one at a time (0.6 s ramps), then back at dawn
for n, g, off in ((5, 0.01, 0.0), (4, 0.01, 0.35), (3, 0.01, 0.7), (2, 0.02, 1.05), (1, 0.03, 1.4), (0, 0.15, 1.75)):
    cue(f"L29+{off}", "pan", n=n, v=g, dur=0.6)
    cue("L48", "pan", n=n, v=1.0, dur=0.9)
cue("L29", "amb", v=0.05, dur=1.4)
cue("L48", "amb", v=1.0, dur=1.2)
cue("L29", "dl", v=3.0, dur=0.8)
cue("L48", "dl", v=1.0, dur=1.0)
cue("L29", "am", v=1.6, dur=0.8)
cue("L48", "am", v=1.0, dur=1.0)
cue("L48", "dawn", v=1.0, dur=2.2)
cue("L52-0.2", "dawn", v=0.0, dur=0.5)
cue("L51.2", "truck", x=-0.8)
cue("L51.2", "truck", x=22.0, dur=2.6)
cue("L52", "truck", x=-0.8, dur=0.0)

# props
cue("L16", "roll", v=1)
cue("L16.3", "roll", v=0)
cue("L12+0.15", "coin", p0=[SLOT[0], 2.95, SLOT[2]], p1=[SLOT[0], 3.145, SLOT[2]], dur=0.3)
cue("L15+0.1", "coin", p0=[SLOT[0], 2.95, SLOT[2]], p1=[SLOT[0], 3.145, SLOT[2]], dur=0.3)
cue("L07", "phone", show=True, pos=[2.95, 2.85, 1.25], yaw=0.0)
cue("L08", "phone", show=False)
cue("L19", "snacks", v=1)
cue("L21", "snacks", v=0)
cue("L48", "cap", who="me", v=1)
cue("L48", "cap", who="jonah", v=0)

# each shot's own light
LOOK_AT = []
for (at, camspec, opt) in SH:
    if opt.get("look"):
        LOOK_AT.append(at)
for at, camspec, opt in SH:
    pass
for i, (at, camspec, opt) in enumerate(SH):
    if opt.get("look"):
        cues.append({"at": at, "name": "shot", "look": opt["look"]})
        if i + 1 < len(SH):
            nxt = SH[i + 1]
            if not nxt[2].get("look"):
                cues.append({"at": nxt[0], "name": "shot", "look": None})
    elif i > 0 and SH[i - 1][2].get("look"):
        pass

# ---------------------------------------------------------------------------------------------------- sound
sfx = [
    {"at": "L01.3+0.3", "kind": "hit", "db": -7},
    {"at": "L01.3+0.3", "kind": "thud", "db": -10},
    {"at": "L12+0.35", "kind": "click", "db": -16},
    {"at": "L13.1", "kind": "click", "db": -22},
    {"at": "L14", "kind": "whoosh", "db": -26, "dur": 1.4},
    {"at": "L15+0.35", "kind": "click", "db": -16},
    {"at": "L16.3", "kind": "click", "db": -18},
    {"at": "L16.3+0.35", "kind": "click", "db": -18},
    {"at": "L16.3+0.7", "kind": "click", "db": -18},
    {"at": "L16.3+1.05", "kind": "click", "db": -18},
    {"at": "L17", "kind": "door", "db": -22},
    {"at": "L21", "kind": "riser", "db": -28, "dur": 1.6},
    {"at": "L22", "kind": "thud", "db": -22},
    {"at": "L24", "kind": "thud", "db": -24},
    {"at": "L27.2", "kind": "click", "db": -9},
    {"at": "L28", "kind": "whoosh", "db": -18, "dur": 1.4},
    {"at": "L30", "kind": "thud", "db": -12},
    {"at": "L36", "kind": "sting", "db": -16, "dur": 1.6},
    {"at": "L38", "kind": "riser", "db": -26, "dur": 1.4},
    {"at": "L40+0.5", "kind": "door", "db": -12},
    {"at": "L41", "kind": "whoosh", "db": -22, "dur": 1.2},
    {"at": "L49", "kind": "bell", "db": -30},
    {"at": "L52", "kind": "thud", "db": -20},
    {"at": "L53", "kind": "click", "db": -20},
    {"at": "L54", "kind": "sting", "db": -18, "dur": 1.8},
]
music = {"root": 48, "mode": "lydian", "bpm": 112, "seed": 9, "sections": [
    {"at": 0, "voices": ["pulse", "piano"], "energy": 0.4},
    {"at": "L21", "voices": ["pulse", "piano", "pad"], "energy": 0.42},
    {"at": "L27", "voices": ["drone", "pad"], "energy": 0.6, "mode": "minor"},
    {"at": "L42", "voices": ["drone", "pad"], "energy": 0.4, "mode": "major"},
    {"at": "L48", "voices": ["pad", "piano"], "energy": 0.5, "mode": "major"},
    {"at": "L52", "voices": ["drone"], "energy": 0.45, "mode": "minor"},
]}
sound = {"floor": "stone", "steps_db": -24,
         "ambience": [
             {"kind": "hum", "from": 0, "to": "end", "lufs": -34},
             {"kind": "room", "from": 0, "to": "end", "lufs": -38},
         ],
         "sfx": sfx,
         "music_drops": [{"from": "P01-0.02", "to": "P01>", "keep": ["click"], "db": -70}]}

story = {
    "slug": "dryer-nine",
    "title": "Nobody Uses Dryer NINE",
    "made_for_kids": False,
    "premise": "At the all-night laundromat, dryer nine runs every night with nothing in it and its timer counts down to sunrise, not to dry. On my big brother Jonah's last night before he moves out, nine says forty-one minutes, and I feed it a quarter, which buys ten more minutes of night.",
    "twist": "Dryer nine dries the night itself. A quarter buys more night, and when I buy seven hours of it there is too much for the drum: a long figure of starry cloth with the moon for a face climbs out. Jonah and I hold the door shut with our backs until the timer runs out and the sun comes up. The next night something inside holds a quarter up to the glass: now it wants you to buy more night.",
    "world": "A small bright all-night laundromat on a dark parking lot: white tile floor, mint walls, a row of ten mint front-load dryers along the back, yellow washers, a folding table, sunflower chairs, a snack machine, big front windows onto a navy lot with a street light, a white box truck and a cream moon.",
    "voice": {"voice": "am_adam", "tempo": 1.03, "rate": 1.45},
    "key_color": "#ffb02e",
    "gap": 0.12,
    "tail": 0.25,
    "fade_in": False,
    "fade_out": False,
    "look": {"style": "closer", "fog": "#bcd4e8", "fog_density": 0.0, "fog_start": 6.0, "sky": "#1d2f7a", "sky_strength": 1.0,
             "hdri": "lebombo", "hdri_strength": 0.45, "hdri_rotation": 0, "hdri_visible": False,
             "exposure": 0.0, "flash_safe": True},
    "grade": {"shadows": [0.0, 0.0, 0.03], "highlights": [0.03, 0.015, -0.02], "saturation": 1.12,
              "contrast": 1.06, "vignette": 0.28, "bloom": 0.2, "grain": 0.01},
    "phonemes": {"dryer": "dɹˈIɚ"},
    "cast": cast,
    "lines": lines,
    "shots": shots,
    "acting": acting,
    "cues": cues,
    "fx": [],
    "music": music,
    "sound": sound,
}
OUT.write_text(json.dumps(story, indent=1, ensure_ascii=False) + "\n")
print("wrote", OUT, f"({len(shots)} shots)")
