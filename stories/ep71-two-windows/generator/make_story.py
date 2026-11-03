"""Writes ../story.json for ep71 "Two windows" (script by the writer, 2026-11-03).

Run from anywhere: python stories/ep71-two-windows/generator/make_story.py
Words are in lines.json. Places are set.py's metres (see its docstring). yaw 0 faces -y, yaw 90 faces +x.
Cars: ours rides the lane at y = 2.65 heading +x (car yaw 0) or the back lane y = 10.6 heading -x (car yaw 180).
Cal sits on the car's left (local +y), me on the right. Riders get acting keys generated from the car's path.
"""
import json
import math
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE.parent / "story.json"
lines = json.loads((HERE / "lines.json").read_text())
for _l in lines:
    for _c in _l["chunks"]:
        _c[1] = _c[1].replace("drive thru", "drive through")
        _c[0] = _c[0].replace("Delivery vans TAPE", "Delivery vans COVER").replace("And every lap", "Every lap")
        _c[0] = _c[0].replace("and comes out", "and ends up").replace("before it can ASK", "before it ASKS")
        _c[1] = _c[1].replace("and comes out", "and ends up").replace("before it can ask", "before it asks")
        _c[0] = _c[0].replace("past Mr. Dale's", "by Mr. Dale's")
        _c[1] = _c[1].replace("past mister Dale's", "by mister Dale's")
        if _c[0] == "OURS.":
            _c[0], _c[1] = "are US.", "are us."
        _c[1] = _c[1].replace("delivery vans tape", "delivery vans cover").replace("and every lap", "every lap")
TIM = HERE.parent / "voice-timings.json"
timings = json.loads(TIM.read_text())["lines"] if TIM.exists() else {}

PAUSES = {"L29": ("P01", 0.7), "L50": ("P02", 0.6)}
HOLDS = {"L02": 0.1}
full = []
for ln in lines:
    if ln["id"] in HOLDS:
        ln["gap"] = HOLDS[ln["id"]]
    full.append(ln)
    if ln["id"] in PAUSES:
        pid, dur = PAUSES[ln["id"]]
        full.append({"id": pid, "pause": dur, "chunks": []})
full.append({"id": "P03", "pause": 0.25, "chunks": []})
lines = full


def split_chunks(ln):
    out = []
    for cap, sp in ln["chunks"]:
        cw, sw = cap.split(" "), sp.split(" ")
        while len(cw) > 3 and len(cw) == len(sw):
            k = 3 if len(cw) >= 6 else (len(cw) + 1) // 2
            out.append([" ".join(cw[:k]), " ".join(sw[:k])])
            cw, sw = cw[k:], sw[k:]
        out.append([" ".join(cw), " ".join(sw)])
    ln["chunks"] = out


for _ln in lines:
    _ln["ncap"] = len(_ln["chunks"])
    split_chunks(_ln)

# ---- approximate times (only for ordering and for splitting a line into shots)
EST = {}
_t = 0.25
for ln in lines:
    lid = ln["id"]
    if "pause" in ln:
        d = ln["pause"]
        EST[lid] = (_t, d)
    elif lid in timings:
        d = timings[lid]["end"] - timings[lid]["onset"]
        EST[lid] = (_t, d)
        d = timings[lid]["dur"]
    else:
        words = sum(len(c[1].split()) for c in ln["chunks"])
        d = words * 0.21 + 0.1
        EST[lid] = (_t, d)
    _t += d + ln.get("gap", 0.12)
TOTAL = _t


def approx(ref):
    if isinstance(ref, (int, float)):
        return float(ref)
    m = re.match(r"^(?P<b>[LP]\d+\w*?|end)(?:\.(?P<c>\d+))?(?P<g>>)?(?P<o>[+-]\d+(?:\.\d+)?)?$", str(ref))
    base, off = m.group("b"), float(m.group("o") or 0)
    if base == "end":
        return TOTAL + off
    s, d = EST[base]
    nch = len(next(l for l in lines if l["id"] == base)["chunks"]) or 1
    if m.group("c") is not None:
        s += d * int(m.group("c")) / nch
    if m.group("g"):
        s += d
    return s + off


def span(lid):
    return EST[lid]


def person(skin, shirt, pants, hair, hair_c, **kw):
    d = {"age": "adult", "skin": skin, "shirt": shirt, "pattern": "solid", "collar": None, "pants": pants,
         "shoes": "#25262b", "sleeves": "long", "hair": hair, "hair_c": hair_c, "hat": "none",
         "face": {"eyes": "round", "brows": True, "ink": "#161012"}}
    d.update(kw)
    return d


SKIN = "#e8b88f"
cal_spec = person(SKIN, "#e0a92e", "#3a4258", "cap", "#3b2a20")
me_spec = person(SKIN, "#8ec9f5", "#2f3a52", "swoop", "#3b2a20", extras=["hooddown"], extra_c="#8ec9f5")
cast = {
    "me": me_spec, "cal": cal_spec,
    "cal2": dict(cal_spec), "me2": dict(me_spec),
    "lady": person("#d9a98a", "#7fe0c4", "#2f3a52", "bun", "#6a4a35", hat="ballcap", hat_c="#ffb38a",
                   face={"eyes": "lashes", "brows": True, "ink": "#161012"}),
    "dale": person("#dcb08f", "#6aa0c8", "#4a4a52", "buzz", "#b9b9b9", pattern="plaid", pattern_c="#3d5f80"),
    "driver1": person("#b88562", "#444a58", "#2e3238", "cap", "#2a2a2a"),
}

# ------------------------------------------------------------------------------------------------ acting / cues
acting = {k: [] for k in cast}
cues = []


def A(who, at, **kw):
    acting[who].append({"at": at, **kw})


def cue(at, name, **kw):
    cues.append({"at": at, "name": name, **kw})


LY = 2.65          # lane y
BY = 10.6          # back lane y
SEAT_Z = -0.16


def rider_xy(x, y, yaw, lx, ly):
    a = math.radians(yaw)
    return [round(x + lx * math.cos(a) - ly * math.sin(a), 3), round(y + lx * math.sin(a) + ly * math.cos(a), 3), SEAT_Z]


def drive(cid, riders, pts):
    """pts: (ref, x, y, yaw, flag) with flag in '', 'snap', 'hide'. riders: {name: (lx, ly)}."""
    prev = None
    for ref, x, y, yaw, *fl in pts:
        flag = fl[0] if fl else ""
        if flag == "hide":
            cue(ref, "car", id=cid, hide=True, pos=[0, 0], yaw=0)
            for who in riders:
                A(who, ref, hidden=True)
            prev = None
            continue
        cue(ref, "car", id=cid, pos=[x, y], yaw=yaw, **({"snap": True} if flag == "snap" else {}))
        for who, (lx, ly) in riders.items():
            p = rider_xy(x, y, yaw, lx, ly)
            if flag == "snap" and prev is not None:
                A(who, ref, pos=rider_xy(prev[0], prev[1], prev[2], lx, ly), yaw=prev[2] + 90, blend=0)
            kw = dict(pos=p, yaw=yaw + 90, blend=0, hidden=False)
            A(who, ref, **kw)
        prev = (x, y, yaw)


CALP = {"cal": (-0.3, 0.45), "me": (-0.3, -0.45)}
CXS, CX1, CX2 = -12.3, 0.3, 10.4          # car centre x at the speaker, window 1, window 2
CP = {"cal2": (-0.3, 0.45), "me2": (-0.3, -0.45)}

# sit + base poses
for w in ("cal", "me", "cal2", "me2", "driver1"):
    A(w, 0, sit=True, hidden=True, arms=[70, 70] if w != "me" else [0, 0], side=[0, 0], head=[0, 0], lean=0, roll=0)
A("cal", "L08", arms=[70, 70], expr="smile", blend=0, sfx="door")
A("me", "L08", arms=[0, 0], expr="neutral", blend=0)

# ---- cars at rest
for i in range(8):
    cue(0, "car", id=f"truck{i}", pos=[15 - 4.1 * i, 12.9], yaw=180)
for cid in ("ours", "copyA", "copyB", "copyC", "copyD", "lime", "van"):
    cue(0, "car", id=cid, hide=True, pos=[0, 0], yaw=0)
cue(0, "server", lv=0, on=True)
cue(0, "scr", n=41)
cue(0, "vis", id="tix", n=0)
cue(0, "h2", v=0.0)

# lime car and van pass (L03, L04)
drive("lime", {"driver1": (-0.3, 0.45)}, [("L03-0.2", 2, LY, 0, "snap"), ("L03>+0.2", 22, LY, 0), ("L03>+0.4", 0, 0, 0, "hide")])
drive("van", {}, [("L04-0.2", 2, LY, 0, "snap"), ("L04>+0.2", 24, LY, 0), ("L04>+0.4", 0, 0, 0, "hide")])
A("driver1", "L03-0.2", hidden=False, expr="blank", arms=[70, 70], blend=0)

# lady and Dale
A("lady", 0, pos=[0, 5.2], yaw=0, expr="smile", arms=[0, 0])
A("lady", "L17", arms=[80, 0], blend=0.3)
A("lady", "L18", arms=[0, 0], blend=0.3)
A("dale", 0, pos=[300, 2.7], yaw=0, expr="smile", arms=[0, 0])
A("dale", "L07", arms=[75, 0], blend=0.3)

# ---- ours: lap 1
O = "ours"
drive(O, CALP, [("L08-0.5", -33, LY, 0, "snap"), ("L13", -22, LY, 0), ("L14>", CXS, LY, 0), ("L16>", CXS, LY, 0),
                ("L16>+0.3", CX1, LY, 0, "snap"), ("L18>", CX1, LY, 0), ("L19>", 5.0, LY, 0), ("L22>", 5.0, LY, 0),
                ("L23>", CX2, LY, 0), ("L26>", CX2, LY, 0), ("L27", 18, BY, 180, "snap"), ("L29", -30, BY, 180),
                ("L29>", -24, LY, 0, "snap"), ("P01", CXS, LY, 0), ("L34>", CXS, LY, 0),
                ("L34>+0.1", 5.5, LY, 0, "snap"), ("L36", CX2, LY, 0), ("L39>", CX2, LY, 0),
                ("L40", 18, BY, 180, "snap"), ("L41>", 0, BY, 180), ("L42-0.2", -24, LY, 0, "snap"),
                ("L42", CXS, LY, 0), ("L42>", CXS, LY, 0), ("L42>+0.1", 5.5, LY, 0, "snap"), ("L43", CX2, LY, 0),
                ("L46>", CX2, LY, 0), ("L47", -31.5, BY, 180, "snap"), ("L50", -33.5, BY, 180),
                ("L50>", CX2, LY, 0, "snap"), ("L58>", CX2, LY, 0),
                ("L58>+0.1", -24, LY, 0, "snap"), ("L59>", CXS, LY, 0), ("L64>", CXS, LY, 0),
                ("L64>+0.1", 2.5, LY, 0, "snap"), ("L65>", 8.0, LY, 0), ("L66-0.1", 572, -1.75, 0, "snap"),
                ("L67+3", 585, -1.75, 0), ("L68>", 592, -1.75, 0), ("L69-0.2", -24, LY, 0, "snap"),
                ("L69", CXS, LY, 0), ("L69>", CXS, LY, 0), ("L69>+0.1", 0, 0, 0, "hide")])
# seated poses over time
A("me", "L09", arms=[75, 75], side=[-25, -25], expr="worried")
A("me", "L10", arms=[0, 0], side=[0, 0], expr="neutral")
A("me", "L12", expr="neutral", head=[0, 0])
A("me", "L13", expr="angry", head=[50, 0])
A("me", "L14", expr="angry", head=[0, 0])
A("me", "L15", expr="neutral")
A("me", "L22", expr="scared", head=[40, 0])
A("me", "L23", expr="angry", head=[55, 0])
A("me", "L25", expr="scared", head=[-70, 0])
A("me", "L26", expr="scared", head=[0, 0])
A("me", "L30", expr="wide")
A("me", "L34", expr="scared", lean=12)
A("me", "L35", expr="scared", lean=0)
A("me", "L41", expr="angry", head=[55, 0])
A("me", "L43", expr="scared", head=[0, 0])
A("me", "L48", expr="scared", head=[140, 0])
A("me", "L51", expr="terrified", head=[40, 0])
A("me", "L56", expr="neutral", head=[0, 0])
A("me", "L57", expr="neutral", arms=[75, 75], side=[-25, -25])
A("me", "L57+0.45", expr="worried", arms=[0, 0], side=[0, 0], lean=18)
A("me", "L57+0.9", expr="angry", head=[55, 0], lean=0)
A("me", "L57+1.35", expr="scared", head=[140, 0])
A("me", "L58", expr="neutral", head=[0, 0])
A("me", "L59", expr="angry", head=[50, 0], roll=-38, arms=[40, 30])
A("me", "L61", expr="neutral", head=[50, 0], roll=-38)
A("me", "L62", expr="neutral", head=[0, 0], roll=0, arms=[0, 0])
A("me", "L64", expr="smile")
A("me", "L68", expr="smile")
A("cal", "L11", expr="smile")
A("cal", "L14", expr="laugh")
A("cal", "L15", expr="wide")
A("cal", "L15.2", expr="smile")
A("cal", "L26", expr="grin")
A("cal", "L34.3", expr="neutral")
A("cal", "L36", expr="smile", head=[-0, 0])
A("cal", "L37", expr="smile", head=[40, 0])
A("cal", "L38", expr="smile", head=[0, 0])
A("cal", "L56", expr="grin")
A("cal", "L61", expr="wide")
A("cal", "L64", expr="wide")
A("cal", "L64.0+0.8", expr="smile")
A("cal", "L67", expr="angry")
A("cal", "L68", expr="smile")
A("cal", "L69", expr="smile", head=[-60, 0], sfx="door")

# ---- the copies: A waits at the back wall from L38, B from L46, C from L49 (all facing -x)
drive("copyA", CP, [("L38-0.1", -17.8, 12.9, 180, "snap"), ("L70>", -17.8, 12.9, 180), ("L71-0.1", 3, LY, 0, "snap"),
                    ("L71>", 7.5, LY, 0)])
drive("copyB", {}, [("L46-0.1", -21.9, 12.9, 180, "snap")])
drive("copyC", {}, [("L49-0.1", -26.0, 12.9, 180, "snap")])
drive("copyD", {}, [("L54-0.1", -30.1, 12.9, 180, "snap")])
A("cal2", "L38", expr="grin", arms=[70, 70], blend=0)
A("me2", "L38", expr="scared", head=[130, 0], blend=0)

# ---- scene cues
cue("L18", "vis", id="tix", n=1)
cue("L33", "vis", id="tix", n=2)
cue("L40", "vis", id="tix", n=3)
cue("L47", "vis", id="tix", n=4)
cue("L63+0.3", "vis", id="tix", n=42)
cue("L63+0.3", "scr", n=42)
cue("L02", "vis", id="sillticket", on=False)
cue("L17+0.3", "vis", id="sillticket", on=True)
cue("L18", "vis", id="sillticket", on=False)
cue("L24", "bagcar", on=True)
cue("L26>", "bagcar", on=False)
cue("L68", "vis", id="cup", on=True)
cue("L69", "vis", id="cup", on=False)
# the Server: level 0 arm only, 1 face in the hatch, 2 shoulders, 3 waist
cue("L35", "server", lv=0, on=True)
cue("L35+0.3", "server", lv=1, dur=0.5)
cue("L39>", "server", lv=1)
cue("L40", "server", lv=0)
cue("L43", "server", lv=2, dur=0.6)
cue("L46>", "server", lv=2)
cue("L47", "server", lv=1, dur=0.3)
cue("P02>", "server", lv=3, dur=0.6)
cue("L55", "server", lv=3)
cue("L56", "server", lv=1, dur=0.4)
cue("L65", "server", lv=0, on=False)
cue("L65", "vis", id="wallB", on=False)
cue("L70", "vis", id="wallB", on=True)
cue("L70", "server", lv=0, on=True)
cue("L20", "h2", v=0.1, dur=0.5)
cue("L35", "h2", v=0.4, dur=0.8)
cue("L43", "h2", v=0.7, dur=0.8)
cue("L51", "h2", v=1.0, dur=0.8)
cue("L66", "h2", v=0.0, dur=0.8)
cue("P02", "dim", v=1.0, dur=0.6)
cue("P02>+0.1", "dim", v=0.0, dur=0.8)

# ------------------------------------------------------------------------------------------------ shots
SHOTS = []


def c(*keys):
    return [list(k) for k in keys]


def still(loc, tgt, lens, roll=0):
    return c([0, loc, tgt, lens, roll])


def move(l0, t0, l1, t1, lens0, lens1=None):
    return c([0, l0, t0, lens0], [1, l1, t1, lens1 if lens1 is not None else lens0])


def shot(at, note, cam, follow=None, hand=0.012, step=2):
    mm = re.match(r"^(L\d+)\.(\d+)$", str(at))
    if mm:   # "Lxx.k" in this file means the k-th caption chunk of the script's line, placed by proportion
        lid, k = mm.group(1), int(mm.group(2))
        ln = next(l for l in lines if l["id"] == lid)
        at = f"{lid}+{round(span(lid)[1] * k / ln['ncap'], 2)}"
    s = {"id": f"S{len(SHOTS) + 1:03d}", "at": at, "what": note, "cam": cam, "hand": hand, "step": step}
    if follow:
        s["follow"] = follow
    SHOTS.append(s)


def seq(lid, items):
    """Several shots inside one line, evenly spaced. items: (note, cam, follow or None)."""
    s, d = span(lid)
    n = len(items)
    for i, it in enumerate(items):
        at = lid if i == 0 else f"{lid}+{round(d * i / n, 2)}"
        note, cam = it[0], it[1]
        fol = it[2] if len(it) > 2 else None
        shot(at, note, cam, fol)


def rel(xyz):
    return list(xyz)


# camera frames, relative to a rider when "follow" is set (cal feet = car centre + (-0.3, +0.45) heading +x)
CAL_FRAME = still([2.8, 1.0, 1.75], [-0.25, -0.5, 1.5], 30)
ME_CLOSE = still([2.6, -1.0, 1.75], [0, 0, 1.5], 36)
TWO = still([3.0, -0.45, 1.75], [0, -0.45, 1.5], 24)
WIND = move([-0.5, -0.45, 1.75], [8, -0.45, 1.45], [-0.5, -0.45, 1.75], [8, -0.45, 1.45], 30)
MIRROR = still([-0.3, -0.45, 1.75], [0.98, -0.35, 1.58], 45)
MIRROR_CLOSE = still([-0.2, -0.35, 1.7], [0.98, -0.3, 1.58], 70)
BACK_WALL_VIEW = lambda x0: still([x0, 9.6, 0.9], [-12, 12.9, 1.0], 26)

# ---- 01 the rule
shot(0, "S01 both windows: the real one with the lady near, the lit second hatch beyond with the sleeve and bag on its sill, pushing in", move([5.05, -6.5, 2.8], [5.05, 5.0, 1.2], [5.05, -4.5, 2.6], [5.05, 5.0, 1.3], 12.5, 15), hand=0)
shot("L02", "S02 pushing toward the second hatch", move([6.2, 0.0, 1.65], [10.1, 5.0, 1.6], [8.6, 1.4, 1.65], [10.1, 5.0, 1.6], 28, 36), hand=0)
shot("L03", "S03 a car rolls past the second window", still([8.5, -0.6, 0.7], [10.5, 3.0, 1.1], 28))
shot("L04", "S04 a van with a taped window", still([9.0, -0.4, 0.8], [11.0, 3.0, 1.2], 26))
shot("L05", "S05 Mr. Dale at his door", still([300, -1.7, 1.55], [300, 3, 1.5], 36))
shot("L06", "S06 first red truck, big", still([10.5, 10.9, 0.65], [15, 12.9, 0.95], 30))
shot("L06.1", "S07 tracking along all eight", move([17, 9.8, 0.95], [13, 12.9, 0.95], [-8, 9.8, 0.95], [-14, 12.9, 0.95], 30), hand=0)
shot("L07", "S08 Dale raises the mug", still([300.3, -0.6, 1.6], [300, 3, 1.6], 45))
shot("L07.2", "S09 the soup, number nine", still([-13.73, 0.8, 1.4], [-13.73, 4.1, 1.35], 45))
# ---- 02 Cal
seq("L08", [("S10 me with the bun sign", still([2.6, -1.0, 1.75], [0, 0, 1.5], 36), "me"),
            ("S11 the lane through the windshield", WIND, "cal")])
shot("L09", "S12 me, a mock sulk", ME_CLOSE, "me")
shot("L10", "S13 the two brothers", TWO, "cal")
shot("L11", "S14 the number four", still([-15.87, 0.8, 2.05], [-15.87, 4.1, 2.05], 45))
shot("L11.1", "S15 the pickle slice", still([-14.8, 0.8, 2.05], [-14.8, 4.1, 2.05], 45))
shot("L12", "S16 me deadpan", still([2.4, -0.7, 1.75], [0, 0, 1.5], 36), "me")
shot("L13", "S17 me turned to Cal", still([1.8, -1.3, 1.75], [0, 0, 1.5], 36), "me")
shot("L13.2", "S18 Cal smiles", CAL_FRAME, "cal")
shot("L14", "S19 Cal laughing", still([2.4, 0.9, 1.75], [0, 0, 1.5], 36), "cal")
shot("L14.1", "S20 the cracked headlight", still([3.5, 0.1, 0.95], [2.23, 0.17, 0.96], 40), "cal")
shot("L14.3", "S21 pulling up beside the speaker", still([-16.5, -0.6, 1.2], [-12.3, 3.0, 1.1], 30))
shot("L15", "S22 the grille", still([-12.0, 1.9, 1.45], [-12.0, 3.8, 1.5], 50))
shot("L15.1", "S23 Cal's mouth opens", still([2.4, 0.9, 1.75], [0, 0, 1.5], 36), "cal")
shot("L16", "S24 Cal grins", CAL_FRAME, "cal")
# ---- 03 the second window
seq("L17", [("S25 the lady at the window", still([2.5, 0.6, 2.5], [0, 5.0, 1.5], 28)),
            ("S26 the ticket", still([0.5, 3.4, 1.4], [-0.2, 4.4, 1.2], 50)),
            ("S27 the sill and its one stroke", still([-0.35, 3.2, 1.6], [-0.35, 4.2, 1.14], 70))])
shot("L18", "S28 the mirror, first ticket", MIRROR, "cal")
shot("L19", "S29 the wall running on", WIND, "cal")
shot("L19.1", "S30 the end of the wall", still([3.6, 0.5, 1.3], [8, 4, 1.4], 28))
shot("L20", "S31 the second hatch is lit", still([6.5, 2.5, 1.55], [10.1, 5.0, 1.65], 35))
shot("L21", "S32 hand, bag, ticket 41", still([9.0, 2.7, 1.5], [10.1, 4.0, 1.3], 50))
shot("L22", "S33 Cal says the fries are better", still([2.6, 1.0, 1.75], [0, 0, 1.5], 36), "cal")
shot("L22.2", "S34 me scared", still([2.0, -1.2, 1.75], [0, 0, 1.5], 36), "me")
shot("L23+0.35", "S35 me says no", still([1.8, -1.3, 1.75], [0, 0, 1.5], 36), "me")
shot("L23.1", "S36 rolling up to the second window", still([6.0, -0.5, 1.0], [10, 3.0, 1.2], 30))
seq("L24", [("S37 the bag in my lap", still([1.3, -0.6, 1.9], [0.25, 0.0, 0.85], 28), "me"),
            ("S38 two buns, no pickles", still([1.0, -0.4, 1.7], [0.2, 0.0, 0.95], 30), "me")])
shot("L25", "S39 me looking back at the hatch", still([2.3, -0.8, 1.75], [0, 0, 1.5], 36), "me")
shot("L26", "S40 Cal eats a fry", still([2.4, 0.9, 1.75], [0, 0, 1.5], 36), "cal")
shot("L26.1", "S41 the exit arrow", still([13.0, 0.8, 0.9], [15.3, 2.65, 0.05], 35))
# ---- 04 lap two
shot("L27", "S42 turning along the back wall from behind", still([23, 10.6, 1.5], [10, 10.6, 0.9], 30))
shot("L28", "S43 the trucks slide past my window", still([0.1, -0.9, 1.7], [0.1, 3, 1.3], 32), "me")
shot("L29", "S44 the menu board and speaker again", WIND, "cal")
shot("P01", "S45 tight on the grille", still([-12.0, 2.0, 1.45], [-12.0, 3.8, 1.5], 60))
shot("L30", "S46 me wide", still([2.0, -1.2, 1.75], [0, 0, 1.5], 36), "me")
shot("L31", "S47 Cal grins, same frame", CAL_FRAME, "cal")
shot("L32", "S48a same grin", CAL_FRAME, "cal")
shot("L32.1", "S48b same words", CAL_FRAME, "cal", hand=0.0)
shot("L33", "S49 two tickets", MIRROR, "cal")
shot("L33.2", "S50 close on the two", MIRROR_CLOSE, "cal")
shot("L34", "S51 me leaning", still([2.0, -1.2, 1.75], [0, 0, 1.5], 36), "me")
shot("L34.2", "S52 Cal shrugs", still([2.6, 1.0, 1.75], [0, 0, 1.5], 36), "cal")
shot("L35", "S53 the hatch coming up", still([6.5, 0.0, 2.8], [10.1, 5.0, 1.65], 30))
shot("L36", "S54 the Server's face fills the hatch", move([10.1, -0.2, 2.7], [10.1, 4.9, 1.75], [10.1, 0.4, 2.7], [10.1, 4.9, 1.75], 36, 40), hand=0.006)
shot("L37", "S56 Cal pulls up", CAL_FRAME, "cal")
shot("L38", "S57 the back wall, one more car", still([-27.5, 9.6, 0.85], [-12, 12.9, 1.0], 28))
shot("L38.1", "S58 closer", still([-25.0, 10.5, 0.9], [-19.5, 12.9, 0.95], 34))
shot("L39", "S59 the cracked headlight", still([-23.0, 11.2, 0.7], [-19.73, 12.28, 0.8], 50))
# ---- 05 lap three
shot("L40", "S60 three tickets", MIRROR, "cal")
shot("L41", "S61 I shout at Cal", still([1.2, -1.2, 1.75], [0, 0, 1.5], 36), "me")
shot("L41.1", "S62 Cal drives past the trucks", still([-1.5, 1.8, 1.4], [0, 0, 1.5], 38), "cal")
shot("L42", "S63 the speaker screen", still([-12.0, 2.1, 1.62], [-12.0, 3.75, 1.62], 60))
shot("L42.1", "S64 Cal, same grin", CAL_FRAME, "cal")
shot("L43", "S65 out to its shoulders", still([14.5, 3.6, 1.7], [10.1, 4.0, 1.5], 35))
shot("L44", "S66 the bag at Cal's door", still([11.6, 2.4, 1.6], [10.1, 3.7, 1.3], 45))
shot("L45", "S67 along the smile", move([9.45, 0.4, 2.7], [9.45, 4.07, 1.62], [10.75, 0.4, 2.7], [10.75, 4.07, 1.62], 55, 55), hand=0.006)
shot("L46", "S68 two of us by the back wall", still([-34, 10.0, 0.9], [-20, 12.9, 1.0], 28))
shot("L46.2", "S69 two cracked headlights", still([-30, 10.6, 0.8], [-22.5, 12.3, 0.85], 40))
# ---- 06 lap four
shot("L47", "S70 four tickets", MIRROR, "cal")
shot("L48", "S71 I turn in my seat", still([0.1, 0.1, 1.9], [0, 0, 1.5], 36), "me")
shot("L49", "S72 over my shoulder, the back wall", still([0.5, 0.0, 1.75], [10, 1.8, 1.0], 30), "me")
shot("L49.2", "S73 the three, tighter", still([0.5, 0.0, 1.75], [8, 1.8, 1.0], 50), "me")
shot("L50", "S74 through the nearest copy", still([-21.0, 11.3, 3.2], [-17.6, 12.9, 1.4], 38))
shot("L50.1", "S75 me scared", still([2.0, -1.2, 1.75], [0, 0, 1.5], 36), "me")
shot("P02", "S76a dim, the hatch", still([6.0, 0.2, 2.3], [10.0, 4.0, 1.9], 24))
shot("L51", "S76 out to its waist", still([6.0, 0.2, 2.3], [10.0, 4.0, 1.9], 24))
shot("L52", "S77 its face a hand from Cal's", still([12.5, 2.0, 1.9], [10.3, 3.4, 1.9], 40))
BOTH = lambda z0, z1: move([5.05, -6.5, 2.8], [5.05, 5.0, 1.2], [5.05, -6.5 + z1 * 2, 2.7], [5.05, 5.0, 1.2], 12.5, 14)
shot("L53", "S78 both hatches, same framing, one window (the lit one empty)", BOTH(16, 0.0), hand=0)
shot("L54", "S79 the two windows, push", BOTH(16, 0.6), hand=0)
shot("L54.2", "S80 the second window is the first one again", still([5.05, -6.5, 2.8], [5.05, 5.0, 1.2], 12.5), hand=0)
shot("L55", "S81 down the back wall", move([22, 9.4, 1.1], [-5, 12.9, 1.0], [10, 9.4, 1.1], [-30, 12.9, 1.0], 22, 22), hand=0)
# ---- 07 the order
for k in range(3):
    shot(f"L56+{round(0.5 * k, 2)}", f"S82 Cal's grin {k}", CAL_FRAME, "cal", hand=0)
for k in range(3):
    shot(f"L57+{round(0.6 * k, 2)}", f"S83 me, pose {k}", still([2.2, -1.1, 1.75], [0, 0, 1.5], 36), "me", hand=0)
shot("L58", "S84 the bag on the sill", still([7.6, 3.4, 1.9], [10.1, 4.0, 1.3], 35))
shot("L58.2", "S85 four tickets", MIRROR, "cal")
shot("L59", "S86 the speaker post coming up", still([-14.5, 0.5, 1.4], [-12, 3.8, 1.5], 38))
shot("L59.1", "S87 I lean across Cal", still([2.2, 0.4, 1.9], [0, 0, 1.6], 45), "cal")
shot("L60", "S88 me at the grille", still([-10.2, 0.4, 1.6], [-12.6, 2.9, 1.5], 55))
shot("L61", "S89 number seven", still([-15.87, 0.8, 1.35], [-15.87, 4.1, 1.35], 45))
shot("L61.1", "S90 Cal wide", still([2.4, 0.9, 1.75], [0, 0, 1.5], 36), "cal")
shot("L61.2", "S91 the pickle slice", still([-14.8, 0.8, 2.05], [-14.8, 4.1, 2.05], 45))
shot("L62", "S92 the grille, no crackle", still([-12.0, 2.0, 1.45], [-12.0, 3.8, 1.5], 60))
shot("L63", "S93 forty-two", still([-12.0, 2.1, 1.62], [-12.0, 3.75, 1.62], 60))
shot("L64", "S94 Cal stares", still([2.4, 0.9, 1.75], [0, 0, 1.5], 36), "cal")
shot("L65", "S95 the wall just ends", WIND, "cal")
shot("L66", "S96 out onto the open road", still([590, -9.5, 1.5], [600, -1.7, 1.0], 28), hand=0)
shot("L67", "S97 Cal eats a pickle", still([2.4, 0.9, 1.75], [0, 0, 1.5], 36), "cal")
shot("L67.1", "S98 me smiles", still([2.2, -1.2, 1.75], [0, 0, 1.5], 36), "me")
shot("L68", "S99 the empty cup and ticket 42", still([-0.2, -0.9, 1.9], [1.12, -0.65, 1.24], 36), "cal")
shot("L69", "S100 a new Friday, Cal waits", TWO, "cal")
shot("L69.2", "S101 me at the grille", still([2.4, -1.2, 1.75], [0, 0, 1.5], 36), "me")
shot("L70", "S102 the back wall, our three laps", still([0.5, 0.0, 1.75], [10, 1.8, 1.0], 30), "me")
shot("L71", "S103 the front one rolls up to the hatch", move([10.1, 0.2, 1.7], [10.1, 5.0, 1.62], [10.1, 0.2, 1.7], [10.1, 5.0, 1.62], 24, 32), hand=0)
# keep captions legible: no shot is longer than a line's worth

# order the acting keys by approximate time
for who in acting:
    acting[who].sort(key=lambda k: approx(k["at"]))
cues.sort(key=lambda k: approx(k["at"]))

sfx = [
    {"at": "L01.2+0.1", "kind": "hit", "db": -9, "dur": 1.0},
    {"at": "L01.2+0.25", "kind": "click", "db": -16},
    {"at": "L02+0.3", "kind": "click", "db": -22},
    {"at": "L03", "kind": "whoosh", "db": -26, "dur": 0.9},
    {"at": "L04", "kind": "whoosh", "db": -27, "dur": 0.9},
    {"at": "L15.1", "kind": "click", "db": -24},
    {"at": "L21", "kind": "click", "db": -22},
    {"at": "L36", "kind": "click", "db": -20},
    {"at": "P01>-0.1", "kind": "glitch", "db": -22, "dur": 0.4},
    {"at": "L43", "kind": "creak", "db": -16, "dur": 1.0},
    {"at": "P02>", "kind": "thud", "db": -12},
    {"at": "P02>+0.05", "kind": "whoosh", "db": -18, "dur": 0.8},
    {"at": "L63+0.3", "kind": "click", "db": -16},
    {"at": "L65+0.6", "kind": "whoosh", "db": -22, "dur": 1.0},
    {"at": "L71>-0.2", "kind": "sting", "db": -22},
]
secs = [
    {"at": 0, "voices": ["pulse", "piano"], "energy": 0.4, "mode": "mixolydian", "root": 50},
    {"at": "L08", "voices": ["pulse", "piano", "pad"], "energy": 0.5},
    {"at": "P01>", "voices": ["drone", "pad", "pulse"], "energy": 0.6, "mode": "minor"},
    {"at": "L43", "voices": ["drone", "pad", "choir"], "energy": 0.7},
    {"at": "L62", "voices": ["drone", "pulse", "piano"], "energy": 0.5, "mode": "major"},
    {"at": "L70", "voices": ["drone"], "energy": 0.5, "mode": "minor"},
]

# ---- keep every shot under 2.0 s: split the long ones with a punch-in on the same subject
import copy


def _punch(cam, k):
    cam = copy.deepcopy(cam)
    for key in cam:
        key[3] = round(key[3] * k, 1)
        if len(key) > 4 and key is not cam[0] and False:
            pass
    return cam


def _at(at, dt):
    if at == 0:
        return round(dt, 2)
    m = re.match(r"^(L\d+)(?:\+(-?[\d.]+))?$", str(at))
    return f"{m.group(1)}+{round(float(m.group(2) or 0) + dt, 2)}"


SPLITS = {"S01 both": [(1.3, 1.2)], "S13 ": [(1.0, 1.3)], "S16 ": [(1.0, 1.3)], "S23 ": [(1.1, 1.3)], "S53 ": [(1.0, 1.25)],
          "S54 ": [(1.0, 1.25)], "S67 ": [(1.0, 1.3)], "S81 ": [(1.0, 1.25)], "S88 ": [(1.0, 1.3)], "S102 ": [(1.1, 1.3)],
          "S103 ": [(1.3, 1.3), (2.5, 1.5)]}
out = []
for s_ in SHOTS:
    out.append(s_)
    for pre, lst in SPLITS.items():
        if s_["what"].startswith(pre):
            for dt, k in lst:
                n = dict(s_)
                n["at"] = _at(s_["at"], dt)
                n["cam"] = _punch(s_["cam"], k)
                n["what"] = s_["what"] + " (punch-in)"
                n["hand"] = 0
                out.append(n)
SHOTS[:] = out
for i, s_ in enumerate(SHOTS):
    s_["id"] = f"S{i + 1:03d}"
_sw = ("S41 ", "S58 ", "S76 ", "S77 ", "S78 ")
SWAY = [s_["id"] for s_ in SHOTS if s_["what"].startswith(_sw) and "punch" not in s_["what"]]
shots = SHOTS
story = {
    "slug": "ep71-two-windows",
    "title": "This Drive-Thru Has TWO Windows",
    "made_for_kids": False,
    "premise": "A roadside drive-thru has one window, but some evenings a second one is lit past the end of the wall, and the rule is never to pull up to it. My big brother Cal has ordered for both of us every Friday for eleven years. Tonight I want to order my own, he laughs and pulls up to the second window, and the exit brings us back to the speaker, which asks for our order before he speaks.",
    "twist": "There was only ever one window. The second window is the first one a lap later, and every lap you go round waits by the back wall. The window can only hand you what you got last time, so a new order, from the only thing in the car that changes, breaks the lap.",
    "world": "a bright golden-evening roadside drive-thru with a mint building, a peach awning, a drawn menu board and a speaker post, and a brick back wall where cars wait nose to tail",
    "voice": {"voice": "am_adam", "tempo": 1.03, "rate": 1.45},
    "key_color": "#6fd13a",
    "gap": 0.12,
    "tail": 0,
    "fade_in": False,
    "look": {"fog": "#ffe2bd", "fog_density": 0.006, "fog_start": 25.0, "sky": "#f7c690", "sky_strength": 1.1,
             "hdri": "industrial_sunset_puresky", "hdri_strength": 0.7, "hdri_rotation": 0, "hdri_visible": False,
             "exposure": 0.0, "flash_safe": True, "polish": {"emph": ["L01", "L07"], "reveal": ["L50", "L51"], "quiet": [["L67", "L69"]],
                                                         "sway": SWAY}},
    "grade": {"shadows": [0.0, 0.0, 0.03], "highlights": [0.04, 0.01, -0.03], "saturation": 1.12, "contrast": 1.05,
              "vignette": 0.22, "bloom": 0.25, "grain": 0.008},
    "phonemes": {"tape": "tˈAp"},
    "cast": cast,
    "lines": lines,
    "shots": shots,
    "acting": acting,
    "cues": cues,
    "fx": [],
    "music": {"root": 50, "mode": "mixolydian", "bpm": 100, "seed": 71, "sections": secs},
    "sound": {"floor": "concrete", "steps_db": -24, "rev": 2,
              "ambience": [{"kind": "hum", "from": 0, "to": "end", "lufs": -40},
                           {"kind": "traffic", "from": 0, "to": "end", "lufs": -38}],
              "sfx": sfx,
              "music_drops": [{"from": "P01", "to": "P01>"}, {"from": "P02", "to": "P02>", "keep": ["thud"]}]},
}
OUT.write_text(json.dumps(story, indent=1, ensure_ascii=False) + "\n")
print("wrote", OUT, f"({len(shots)} shots, est {TOTAL:.0f}s)")
