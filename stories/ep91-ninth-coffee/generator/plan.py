# The shot plan for ep91-ninth-coffee: cast, shots, acting, cues, score and sound. exec'd by make_story.py.
#
# World (metres, z up): my desk at (0, 0) and Kai's at (2.6, 0) in the front row, standing desks 1.0 m high, people stand
# at y -0.85 facing +y (yaw 180). Rows at y 0, 4.2 and 8.4. The front lane (y -3.2) is clear for the ten-cuppers. The
# island with the coffee machine is at (4.4, -4.0), the elevator on the right wall at y 2, the clock on the back wall,
# the lunch table at (7.2, 7.5). Acting yaw: 0 faces -y, 180 faces +y, 90 faces +x, -90 faces -x. A camera at azimuth az
# stands at -y for az 0; a character faces the camera when its yaw equals az.
import math

MX, MY = 4.4, -4.0
FY = MY + 0.05 - 0.3          # the machine's front face
DZ = 1.005                    # desk top
SPOUT = (MX - 0.2, FY - 0.17)  # the left (coffee) spout
TRAYZ = 1.015

FACE = {"eyes": "round", "brows": True, "ink": "#24131f"}
FACEL = {"eyes": "lashes", "brows": True, "ink": "#24131f"}
GLOW = {"eyes": "classic", "brows": False, "mouth": "none", "ink": "#24131f", "pupil": "#05070a", "glow": "#22e6ff"}


def tcast(skin, shirt, pants, hair, hair_c, face=None, **kw):
    d = {"age": "adult", "skin": skin, "shirt": shirt, "pattern": "solid", "pants": pants, "shoes": "#2a2a30",
         "sleeves": "long", "hair": hair, "hair_c": hair_c, "height": 1.15, "width": 0.94, "face": dict(face or GLOW)}
    d.update(kw)
    return d


cast = {
    "me": {"age": "adult", "skin": "#f1c9a0", "shirt": "#f7f7f2", "pattern": "solid", "pants": "#8a8d96", "shoes": "#5a3a24",
           "sleeves": "short", "hair": "cap", "hair_c": "#d4452c", "extras": ["tie"], "extra_c": "#e7b53b", "face": dict(FACE)},
    "kai": {"age": "adult", "skin": "#c68b5e", "shirt": "#2fa59a", "pattern": "knit", "pattern_c": "#27877e", "pants": "#2b2f3a",
            "shoes": "#1c1c22", "sleeves": "long", "hair": "swoop", "hair_c": "#161416", "extras": ["glasses"],
            "extra_c": "#1a1a1f", "face": dict(FACE)},
    "boss": {"age": "adult", "skin": "#e7b999", "shirt": "#1d2f5c", "pattern": "solid", "pants": "#1d2f5c", "shoes": "#14142a",
             "sleeves": "long", "collar": "#ffffff", "hair": "long", "hair_c": "#aeb4be", "face": dict(FACEL)},
    "cw1": {"age": "adult", "skin": "#8a5a3c", "shirt": "#ff7a45", "pattern": "solid", "pants": "#3b4a6b", "shoes": "#2a2a30",
            "sleeves": "short", "hair": "buzz", "hair_c": "#1c1410", "face": dict(FACE)},
    "cw2": {"age": "adult", "skin": "#f1c9a0", "shirt": "#7a5ad6", "pattern": "stripes", "pattern_c": "#9a82ea", "pants": "#4a4f5c",
            "shoes": "#2a2a30", "sleeves": "long", "hair": "bun", "hair_c": "#6a4426", "face": dict(FACEL)},
    "cw3": {"age": "adult", "skin": "#d9a27a", "shirt": "#5fbf5a", "pattern": "solid", "pants": "#6b5a46", "shoes": "#2a2a30",
            "sleeves": "short", "hair": "spiky", "hair_c": "#2a1d15", "face": dict(FACE)},
    "tc1": tcast("#e0b08a", "#e6edf5", "#2b3550", "buzz", "#1c1410"),
    "tc2": tcast("#f1c9a0", "#d3deea", "#2b3550", "bun", "#2a1d15", extras=[], face=dict(GLOW)),
    "tc3": tcast("#a56e4a", "#f0f3f7", "#2b3550", "spiky", "#1c1410"),
    "tc4": tcast("#f1c9a0", "#dbe4ee", "#2b3550", "long", "#1c1410"),
    "tc5": tcast("#d9a27a", "#e9eef3", "#2b3550", "cap", "#6a4426"),
}

# ---------------------------------------------------------------------------------------------------- state
NEUTRAL = {"arms": [0, 0], "side": [0, 0], "head": [0, 0], "lean": 0, "tremble": 0, "blink": True, "look": [0, 0]}
acting = {k: [] for k in cast}
cues = []
shots = []
VIS = set()
CUPS = {}
STK = {}
MET = {"e": 9, "ticks": 9}
TYP = []


def cue(at, name, **kw):
    cues.append({"at": at, "name": name, **kw})


def raw(who, at, **kw):
    acting[who].append({"at": at, **kw})


def put(who, at, pos, yaw=0, expr="neutral", **kw):
    keys = acting[who]
    prev = next((k["pos"] for k in reversed(keys) if "pos" in k), None)
    if prev is not None:
        keys.append({"at": at, "pos": prev})
    keys.append({"at": at, "pos": list(pos), "blend": 0, "yaw": yaw, "expr": expr, "hidden": False, **NEUTRAL, **kw})
    VIS.add(who)


def gone(who, at):
    acting[who].append({"at": at, "hidden": True, "blend": 0})
    VIS.discard(who)


def scene(at, **chars):
    """Everyone named is there from `at` (a cut); everyone else is gone."""
    for w in list(VIS):
        if w not in chars:
            gone(w, at)
    for w, c in chars.items():
        c = dict(c)
        pos = c.pop("pos")
        put(w, at, pos, c.pop("yaw", 0), c.pop("expr", "neutral"), **c)


def meter(at, e=None, ticks=None, other=None, oe=10, oticks=None):
    if e is not None:
        MET["e"] = e
    if ticks is not None:
        MET["ticks"] = ticks
    d = {"e": MET["e"], "ticks": MET["ticks"]}
    if other:
        d.update(other=other, oe=oe, oticks=oe if oticks is None else oticks)
    cue(at, "meter", **d)


def cups(at, **kw):
    for k, v in kw.items():
        if v is None:
            CUPS.pop(k, None)
        else:
            CUPS[k] = list(v)
    cue(at, "cups", **{k: list(v) for k, v in CUPS.items()})


def streaks(at, **kw):
    for k, v in kw.items():
        if v is None:
            STK.pop(k, None)
        else:
            STK[k] = v
    cue(at, "streaks", **dict(STK))


def typing(at, *who):
    cue(at, "typing", who=list(who))


# ---------------------------------------------------------------------------------------------------- cameras
def pos_of(tg, d, az, el):
    a, e = math.radians(az), math.radians(el)
    return [round(tg[0] + d * math.sin(a) * math.cos(e), 3), round(tg[1] - d * math.cos(a) * math.cos(e), 3),
            round(tg[2] + d * math.sin(e), 3)]


def C(tgt, d, az=0, el=6, lens=28, d2=None, tgt2=None, lens2=None, az2=None, el2=None):
    k0 = [0, pos_of(tgt, d, az, el), list(tgt), lens]
    if d2 is None and tgt2 is None and lens2 is None and az2 is None and el2 is None:
        return [k0]
    t2 = tgt2 or tgt
    return [k0, [1, pos_of(t2, d2 if d2 is not None else d, az if az2 is None else az2, el if el2 is None else el2),
                 list(t2), lens2 or lens]]


def X(loc, tgt, lens, loc2=None, tgt2=None, lens2=None):
    ks = [[0, list(loc), list(tgt), lens]]
    if loc2 or tgt2 or lens2:
        ks.append([1, list(loc2 or loc), list(tgt2 or tgt), lens2 or lens])
    return ks


def S(at, cam, look="day", hand=0.004, fill=1.0, exp=0.0, step=2, note=""):
    d = {"id": f"S{len(shots) + 1:02d}", "cam": cam, "step": step, "hand": hand}
    if len(shots):
        d["at"] = at
    if look != "day":
        d["look"] = look
    if fill != 1.0:
        d["fill"] = fill
    if exp:
        d["exp"] = exp
    if note:
        d["note"] = note
    shots.append(d)
    return d


ME = (0.0, -0.85)
KAI_D = (2.6, -0.85)
FOCUS = {"eyes": "round"}

for k in acting:
    acting[k].append({"at": 0, "pos": [0, 20, 0], "hidden": True, "blend": 0, **NEUTRAL})

# =========================================================================================== 01 the hook, L01 to L02
meter(0, 9, 9)
cue(0, "screen", pic="blocks0")
cue(0, "clock_main", h=3.0, s=0.0)
cue(0, "elev", open=1.0)
cups(0, c8=[0.0, -0.2, DZ, True])
S(0, C((0.0, -0.2, 1.14), 0.8, 0, 5, 30, d2=0.58), fill=1.3, note="frame 1: the ninth cup, steam frozen, meter x512")
cups("L01>-0.25", c8=None, c9=[SPOUT[0], SPOUT[1] - 0.0, TRAYZ, False])
S("L01>-0.25", C((MX, -4.4, 1.36), 2.3, 0, 6, 26, d2=1.9), note="the machine's two spouts, a tenth cup under the left one")
S("L02.1", C((SPOUT[0], SPOUT[1], 1.22), 0.95, 18, 8, 30, d2=0.7), note="the tenth cup close")
S("L02.3", C((MX - 0.1, -4.4, 1.35), 1.5, -22, 10, 28, d2=1.2), note="from TEN: both spouts again")

# =========================================================================================== 02 the montage, L03 to L06a
cups("L03", c9=None)
meter("L03", 1, 1)
scene("L03", me=dict(pos=ME, yaw=180, expr="grin", arms=[68, 68]))
typing("L03", "me")
S("L03", C((0.0, -0.2, 1.12), 1.35, -35, 22, 30, d2=1.05), fill=1.2, note="my hands at the end of my sleeves, typing in a blur")
typing("L04", )
meter("L04", 2, 2)
scene("L04", cw3=dict(pos=(8.9, 2.0), yaw=90, expr="neutral"))
cue("L04", "elev", open=1.0)
cue("L04+0.3", "elev", open=0.0)
cue("L04+0.75", "elev", open=1.0)
S("L04", C((9.85, 2.0, 1.3), 3.7, -90, 4, 26, d2=3.2), note="the elevator doors close and open in one beat")
meter("L05", 4, 4)
scene("L05", cw1=dict(pos=(-2.6, -0.85), yaw=12, expr="neutral"))
acting["cw1"].append({"from": "L05", "to": "L05.2", "mouth": [0.2, 0.95]})
acting["cw1"].append({"from": "L05.2", "to": "L05>", "mouth": [0.95, 0.5]})
S("L05", C((-2.6, -0.85, 1.6), 2.5, 12, 4, 30, d2=2.1), note="a coworker talking, mouth slow and wide")
meter("L06", 2, 2)
scene("L06", cw1=dict(pos=(-3.9, 5.05), yaw=0, expr="soft"), cw2=dict(pos=(-1.3, 5.05), yaw=0, expr="soft"),
      cw3=dict(pos=(1.3, 5.05), yaw=0, expr="soft"))
cups("L06", c0=[-4.1, 4.0, DZ], c1=[-3.7, 4.0, DZ], c2=[-1.5, 4.0, DZ], c3=[-1.1, 4.0, DZ], c4=[1.1, 4.0, DZ], c5=[1.5, 4.0, DZ])
S("L06", X((-3.9, 1.6, 1.5), (-3.9, 5.0, 1.45), 22, (1.3, 1.6, 1.5), (1.3, 5.0, 1.45), 22), note="a row of people with two cups each")
cups("L06a", c0=None, c1=None, c2=None, c3=None, c4=None, c5=None)
meter("L06a", 1, 1)
scene("L06a", cw2=dict(pos=(5.5, 2.0), yaw=90, expr="neutral"))
raw("cw2", "L06a>", pos=[8.0, 2.0])
S("L06a", C((7.0, 2.0, 1.45), 3.8, -90, 4, 26, d2=2.9), look="eve", note="evening: a coworker leaves, his one old cup still lit")

# =========================================================================================== 03 Kai, L07 to L12
meter("L07", 0, 0)
cue("L07", "screen", pic="blocks0")
scene("L07")
S("L07", C((2.45, -1.2, 1.05), 2.6, -12, 10, 28, d2=2.2), note="Kai's desk, his teal jacket on the chair, the photo of us")
scene("L07.2", me=dict(pos=ME, yaw=180, expr="neutral", arms=[68, 68]))
typing("L07.2", "me")
S("L07.2", C((1.3, -0.3, 1.2), 4.6, 0, 8, 22, d2=3.9), note="my desk, then his, side by side: one desk over")
typing("L08")
scene("L08")
cups("L08", c0=[2.0, -0.14, DZ], c1=[2.28, -0.14, DZ])
S("L08", C((2.05, 0.16, 1.14), 0.85, 8, 4, 30, d2=0.62), note="the photo close: Kai and me with two cups, laughing")
S("L08.1", C((2.2, -0.1, 1.1), 1.2, -30, 12, 28, d2=0.95), note="two cups on his desk, our morning coffee")
cups("L09", c0=None, c1=None)
scene("L09", me=dict(pos=ME, yaw=24, expr="worried", head=[-0.4, 0.05], look=[0.7, 0]))
S("L09", C((0.0, -0.85, 1.6), 2.6, 24, 4, 30, d2=2.2), note="me looking at his empty chair, tired")
scene("L09.2")
S("L09.2", C((0.0, 0.16, 1.38), 0.95, -14, 3, 30, d2=0.7), note="the scorched sticky notes on my monitor, in his handwriting")
scene("L10")
cue("L10", "jacket", dx=0.0)
S("L10", C((2.6, -1.4, 0.95), 2.5, 18, 10, 28, d2=2.1), note="morning: his chair empty")
cue("L10.1", "jacket", dx=0.035)
scene("L10.1")
S("L10.1", C((2.6, -1.4, 0.95), 2.5, 18, 10, 28, d2=2.1), look="eve", note="evening: still empty, the jacket moved an inch")
S("L11", C((2.6, 0.0, 1.0), 1.6, 0, 82, 26, d2=1.25), note="top-down on his desk, perfectly neat, pens in a line")
S("L12", X((7.6, -0.4, 2.2), (-1.0, 0.0, 1.1), 22, (7.2, -0.6, 2.0), (-1.0, 0.0, 1.1), 22), note="the office at eight, every in-tray stacked")
S("L12.1", C((3.2, -0.08, 1.12), 0.9, -22, 18, 30, d2=0.65), note="a finished stack")
S("L12.2", C((0.58, -0.08, 1.12), 0.8, -18, 38, 30, d2=0.6), note="the top sheet, his scribbles and a star")

# =========================================================================================== 04 the deadline, L13 to L18
cue("L13", "screen", pic="deadline")
S("L13", C((0.1, 0.2, 1.4), 1.9, -12, 4, 30, d2=1.5), note="the deadline glyph on my screen")
cue("L13.2", "clock_main", h=3.0, s=0.0)
S("L13.2", C((0.0, 11.9, 2.55), 2.0, 0, 3, 28, d2=1.6), note="the wall clock at three")
cue("L14", "screen", pic="blank")
S("L14", C((0.1, 0.2, 1.4), 1.7, 8, 3, 30, d2=1.3), note="my blank screen")
scene("L14.2", me=dict(pos=ME, yaw=-14, expr="scared", tremble=2))
S("L14.2", C((0.0, -0.85, 1.6), 2.5, -14, 5, 30, d2=2.0), note="me, panicked")
# the pours
meter("L15", 1, 1)
scene("L15")
cue("L15", "pour", on=True, to=TRAYZ + 0.12)
cups("L15", c0=[SPOUT[0], SPOUT[1], TRAYZ])
S("L15", C((SPOUT[0], SPOUT[1], 1.2), 1.0, 20, 8, 30, d2=0.8), note="pour one")
meter("L15+0.35", 2, 2)
cups("L15+0.35", c0=[MX - 0.8, -4.4, 0.975], c1=[SPOUT[0], SPOUT[1], TRAYZ])
S("L15+0.35", C((MX - 0.4, -4.4, 1.2), 1.7, -30, 8, 28, d2=1.4), note="pour two, the first cup lined up")
meter("L15+0.7", 3, 3)
cups("L15+0.7", c0=[MX - 0.8, -4.4, 0.975], c1=[MX - 0.95, -4.4, 0.975], c2=[SPOUT[0], SPOUT[1], TRAYZ])
S("L15+0.7", C((MX - 0.6, -4.4, 1.15), 1.9, 30, 10, 28, d2=1.5), note="pour three, cups lining up")
cue("L16", "pour", on=False)
meter("L16", 5, 5)
cups("L16", c0=[-0.55, -0.28, DZ], c1=[-0.35, -0.28, DZ], c2=[-0.15, -0.28, DZ], c3=[0.05, -0.28, DZ], c4=[0.25, -0.28, DZ])
S("L16", C((0.0, -0.28, 1.1), 1.9, -16, 26, 26, d2=1.5), note="five cups on my desk")
scene("L16.1", me=dict(pos=ME, yaw=10, expr="grin", tremble=3))
S("L16.1", C((0.0, -0.85, 1.6), 2.3, 10, 4, 30, d2=1.9), note="thirty-two times fast, wired")
cue("L16.2", "clock_main", h=3.0, s=0.0)
cue("L16.2+1.0", "clock_main", h=3.0, s=1.4)
scene("L16.2")
S("L16.2", C((0.0, 11.9, 2.55), 1.7, 0, 2, 30, d2=1.3), note="the clock hands crawl")
meter("L17", 7, 7)
cups("L17", c0=[-0.55, -0.28, DZ], c1=[-0.35, -0.28, DZ], c2=[-0.15, -0.28, DZ], c3=[0.05, -0.28, DZ], c4=[0.25, -0.28, DZ],
     c5=[0.45, -0.28, DZ], c6=[-0.65, -0.1, DZ])
scene("L17", boss=dict(pos=(0.0, 2.1), yaw=40, expr="wide", head=[0, 0.3], arms=[95, 95]))
S("L17", C((0.0, 2.1, 1.55), 2.9, 40, 4, 28, d2=2.4), note="my boss frozen mid-sneeze")
cue("L17", "sneeze", on=True)
S("L17.3", C((0.0, 2.1, 1.5), 1.5, 40, 3, 30, d2=1.2), note="the cloud hanging")
cue("L18", "sneeze", on=False)
meter("L18", 9, 9)
cups("L18", c0=None, c1=None, c2=None, c3=None, c4=None, c5=None, c6=None, c8=[0.0, -1.52, 1.24, True])
scene("L18", me=dict(pos=ME, yaw=0, expr="grin", arms=[100, 0]))
S("L18", C((0.0, -0.85, 1.5), 2.2, 0, 4, 30, d2=1.8), note="the ninth cup, cut before the lip")

# the drop: the frozen office, silent
scene("P01", boss=dict(pos=(0.0, 2.1), yaw=40, expr="wide", head=[0, 0.3], arms=[95, 95]), cw1=dict(pos=(-2.6, -0.85), yaw=180, arms=[68, 68]),
      cw3=dict(pos=(1.3, 5.05), yaw=0, expr="soft"))
cue("P01", "sneeze", on=True)
cue("P01", "paper", pos=[1.2, 1.2, 1.9])
cups("P01", c8=[0.0, -0.2, DZ, True])
S("P01", X((0.0, -2.4, 1.9), (0.3, 3.5, 1.3), 17, (0.0, -2.2, 1.8), (0.3, 3.5, 1.3), 17), note="the drop: the frozen office, silent")

# =========================================================================================== 05 the frozen office, L19 to L25
cue("L19", "screen", pic="blocks0")
scene("L19", me=dict(pos=ME, yaw=8, expr="grin", tremble=2))
S("L19", C((0.0, -0.85, 1.6), 2.6, 8, 4, 30, d2=1.9), note="x512: wired, the meter at its top")
scene("L20", me=dict(pos=(-1.4, -2.5), yaw=0, expr="wide"), cw1=dict(pos=(-2.6, -0.85), yaw=180, arms=[68, 68]),
      boss=dict(pos=(0.0, 2.1), yaw=40, expr="wide", head=[0, 0.3], arms=[95, 95]), cw3=dict(pos=(1.3, 5.05), yaw=0, expr="soft"),
      cw2=dict(pos=(-1.3, 5.05), yaw=0, expr="soft"))
cue("L20", "paper", pos=[0.5, 1.8, 2.0])
cups("L20", c8=None)
S("L20", C((0.0, 3.4, 1.4), 6.0, 0, 6, 18, d2=5.2), note="the whole office stopped, a paper hanging mid-air")
S("L20.1", C((0.5, 1.8, 1.9), 2.6, -22, -3, 28, d2=2.0), note="the paper, the boss behind it")
scene("L21", me=dict(pos=(0.5, -2.4), yaw=20, expr="scared", tremble=3), cw1=dict(pos=(-2.6, -0.85), yaw=180, arms=[68, 68]),
      boss=dict(pos=(0.0, 2.1), yaw=40, expr="wide", head=[0, 0.3], arms=[95, 95]))
S("L21", C((0.5, -2.4, 1.45), 3.2, 20, 5, 26, d2=2.5), note="I stood up, scared, the only one moving")
scene("L22", tc1=dict(pos=(-0.2, -3.2), yaw=90, expr="blank", arms=[40, 70]))
raw("tc1", "L22>", pos=[0.9, -3.2])
streaks("L22", tc1=4.0)
S("L22", C((-0.8, -3.2, 1.1), 3.7, 0, 5, 15, d2=3.2), note="between the desks: a long frozen cyan streak")
scene("L22.1", tc1=dict(pos=(0.2, -3.2), yaw=90, expr="blank", arms=[40, 70]))
raw("tc1", "L22>", pos=[0.7, -3.2])
S("L22.1", C((0.4, -3.2, 1.45), 2.6, 34, 4, 26, d2=2.1), note="a person at the head of it, mid-stride")
scene("L23", tc1=dict(pos=(0.1, -3.2), yaw=90, expr="blank", arms=[40, 70]), tc5=dict(pos=(-4.6, -2.2), yaw=90, expr="blank", arms=[30, 80]))
raw("tc1", "L23>", pos=[0.9, -3.2])
raw("tc5", "L23>", pos=[-4.0, -2.2])
streaks("L23", tc1=4.5, tc5=5.0)
S("L23", C((-1.0, -2.8, 1.2), 4.4, 20, 6, 17, d2=3.8), note="even faster than me: long streaks of colour")
S("L23.1", C((-2.0, -3.0, 1.2), 3.6, -30, 8, 16, d2=3.1), note="the other way: trails across the floor")
S("L23.2", C((0.7, -3.2, 1.65), 2.1, 55, 3, 28, d2=1.7), note="the face at the head, hollow eyes glowing")
# the work: filing, typing, straightening
scene("L24", tc2=dict(pos=(-8.8, 3.0), yaw=-90, expr="blank", arms=[88, 8]))
streaks("L24", tc1=None, tc5=None, tc2=3.6)
S("L24", C((-8.4, 3.0, 1.35), 4.4, 12, 5, 20, d2=3.8), note="FILING: a streak at the cabinet")
scene("L24+0.3", tc3=dict(pos=(-2.6, -0.85), yaw=180, expr="blank", arms=[70, 70]))
streaks("L24+0.3", tc2=None, tc3=3.2)
typing("L24+0.3", "tc3")
S("L24+0.3", C((-2.6, -1.4, 1.3), 3.4, 90, 6, 20, d2=2.9), note="Typing: a streak at a keyboard")
scene("L24+0.7", tc4=dict(pos=(-5.2, -0.85), yaw=180, expr="blank", arms=[78, 70]))
streaks("L24+0.7", tc3=None, tc4=3.2)
typing("L24+0.7")
S("L24+0.7", C((-5.2, -1.4, 1.3), 3.4, -90, 6, 20, d2=2.9), note="squaring a stack on every desk")
scene("L24+1.25", tc5=dict(pos=(5.6, 2.2), yaw=-90, expr="blank", arms=[75, 75]))
streaks("L24+1.25", tc4=None, tc5=3.4)
S("L24+1.25", C((5.6, 0.9, 1.35), 3.0, -20, 6, 20, d2=2.6), note="straightening every desk, another one")
scene("L25", tc1=dict(pos=(3.0, 2.2), yaw=90, expr="blank", arms=[40, 70]), tc2=dict(pos=(-1.0, 6.3), yaw=-90, expr="blank", arms=[60, 60]),
      tc3=dict(pos=(-2.6, -0.85), yaw=180, expr="blank", arms=[70, 70]), tc4=dict(pos=(-5.2, -0.85), yaw=180, expr="blank", arms=[78, 70]),
      tc5=dict(pos=(-6.5, -3.2), yaw=90, expr="blank", arms=[30, 80]))
streaks("L25", tc1=7.0, tc2=7.0, tc3=3.5, tc4=3.5, tc5=5.5)
S("L25", X((-7.4, -6.3, 3.1), (0.5, 3.0, 1.0), 16, (-6.4, -6.2, 3.0), (0.5, 3.0, 1.0), 16), note="the whole floor crossed by cyan streaks, like light trails")
S("L25+0.45", X((8.0, -6.0, 3.2), (-1.0, 3.0, 1.0), 16, (7.2, -6.0, 3.1), (-1.0, 3.0, 1.0), 16), note="the same, from the other corner (cover frame)")

# =========================================================================================== 06 the reveal, L26 to L29
streaks("L26", tc1=None, tc2=None, tc3=None, tc4=None, tc5=None)
scene("L26")
S("L26", C((3.2, -0.08, 1.12), 1.1, 24, 16, 28, d2=0.85), note="the finished in-trays")
S("L26.2", X((7.0, -1.2, 1.4), (1.0, 0.0, 1.1), 22, (6.4, -1.2, 1.3), (1.0, 0.0, 1.1), 22), note="every desk, done")
cups("L27", c9=[SPOUT[0], SPOUT[1], TRAYZ, False])
meter("L27", 9, 9, other="ten", oe=10, oticks=10)
S("L27", C((SPOUT[0], SPOUT[1], 1.25), 1.5, -20, 6, 28, d2=1.2), note="the left spout, ten cup ticks glowing on a streak's meter")
cups("L28", c9=None)
scene("L28", tc2=dict(pos=(-2.0, -3.2), yaw=58, expr="blank", head=[0, 0.12], arms=[70, 40], lean=6))
streaks("L28", tc2=4.5)
S("L28", C((-2.0, -3.2, 1.95), 3.2, 18, -12, 22, d2=2.6), note="a ten-cupper's face, focused, at the head of its streak")
scene("L28.2", tc4=dict(pos=(-2.0, -3.4), yaw=-50, expr="blank", arms=[60, 80], lean=5))
streaks("L28.2", tc2=None, tc4=5.0)
S("L28.2", C((-2.0, -3.4, 1.0), 4.0, -20, 4, 20, d2=3.4), note="the whole figure, taller than us")
cue("L29", "mess", on=True)
scene("L29")
streaks("L29", tc4=None)
S("L29", C((-2.6, 0.0, 1.12), 1.9, -12, 24, 28, d2=1.5), note="a messy desk")
cue("L29.1", "mess", on=False)
S("L29.1", C((-2.6, 0.0, 1.12), 1.9, -12, 24, 28, d2=1.5), note="a cut later: neat")
S("L29.2", X((-5.6, -1.4, 1.5), (0.0, 0.5, 1.1), 20, (-5.0, -1.4, 1.4), (0.0, 0.5, 1.1), 20), note="what they leave: a floor of finished desks")

# =========================================================================================== 07 Kai, L30 to L36
scene("L30", me=dict(pos=ME, yaw=90, expr="wide"), kai=dict(pos=(1.4, -0.85), yaw=-90, expr="worried"))
streaks("L30", kai=5.0)
S("L30", C((0.7, -0.85, 1.35), 4.2, 0, 5, 18, d2=3.5), note="a streak stopping at my desk")
S("L30.2", C((1.4, -0.85, 1.5), 2.3, -34, 4, 26, d2=1.9), note="its head, in profile")
scene("L31", kai=dict(pos=(1.4, -0.85), yaw=-26, expr="worried", head=[0.0, 0.05]))
streaks("L31", kai=5.0)
meter("L31", 9, 9)
S("L31", C((1.4, -0.85, 1.55), 2.4, -26, 3, 28, d2=1.95), note="Kai, clear at the head, pleading")
cue("L32", "jacket", dx=0.0)
meter("L32", 9, 9)
streaks("L32", kai=None)
scene("L32", kai=dict(pos=KAI_D, yaw=180, expr="worried", arms=[70, 70]))
typing("L32", "kai")
cups("L32", **{f"c{i}": [1.98 + 0.14 * i, -0.2, DZ] for i in range(10)})
S("L32", C((2.6, -0.5, 1.2), 3.2, -22, 14, 26, d2=2.7), look="year", note="a year ago, ten cups lined up on his desk")
S("L32.1", C((2.65, -0.2, 1.1), 1.5, -38, 10, 28, d2=1.1), look="year", note="ten cups")
scene("L32.2", kai=dict(pos=KAI_D, yaw=-10, expr="worried"))
S("L32.2", C((2.6, -0.85, 1.55), 2.4, -10, 3, 28, d2=1.9), look="year", note="to make a deadline")
cups("L33", **{f"c{i}": None for i in range(10)})
typing("L33")
scene("L33")
S("L33", C((2.4, -1.5, 1.05), 2.7, -14, 12, 26, d2=2.2), note="his jacket on the chair, the photo of us")
scene("L33.1", kai=dict(pos=KAI_D, yaw=180, expr="neutral", arms=[70, 70]))
streaks("L33.1", kai=3.2)
typing("L33.1", "kai")
S("L33.1", C((2.6, -1.4, 1.25), 3.6, 74, 5, 22, d2=3.0), note="every second since: Kai at his desk, a smear behind him")
S("L33.2", C((2.6, -0.85, 1.45), 2.3, 82, 4, 28, d2=1.8), note="too fast")
streaks("L33.3", kai=None)
scene("L33.3")
S("L33.3", C((2.6, -0.6, 1.1), 2.5, 10, 12, 26, d2=2.0), note="to see: his desk, empty")
scene("L34", kai=dict(pos=KAI_D, yaw=180, expr="worried", arms=[70, 70]))
streaks("L34", kai=3.0)
typing("L34", "kai")
S("L34", C((2.6, -1.0, 1.4), 2.8, 70, 5, 28, d2=2.2), note="never too busy for me")
typing("L34.2")
scene("L34.2")
streaks("L34.2", kai=None)
S("L34.2", C((0.58, -0.08, 1.12), 0.9, -20, 38, 30, d2=0.65), note="my in-tray, finished in his handwriting")
scene("L34.3", me=dict(pos=ME, yaw=-12, expr="wide", tremble=1))
S("L34.3", C((0.0, -0.85, 1.6), 2.4, -12, 4, 30, d2=1.9), note="me, stunned")
cue("L35", "note", on=True, smoke=True)
scene("L35")
S("L35", C((0.25, 0.14, 1.5), 1.2, -10, 3, 30, d2=0.85), note="a sticky note appears on my monitor, its edge smoking")
S("L35.2", C((0.34, 0.14, 1.55), 0.7, 14, 6, 30, d2=0.5), note="so fast it smoked")
S("L36", C((0.32, 0.14, 1.5), 0.55, 0, 0, 30, d2=0.4), note="Get me down: the arrow")

# =========================================================================================== 08 the loophole, L37 to L45a
cue("L37", "note", on=False)
S("L37", C((MX + 0.35, FY - 0.37, 1.02), 0.55, -14, 8, 30, d2=0.42), note="two cyan scratches on the drip tray (the lore plant)")
S("L37.2", C((MX, -4.4, 1.38), 2.2, 0, 6, 26, d2=1.8), note="every coffee: the machine, both spouts")
S("L38", C((MX + 0.2, FY - 0.15, 1.55), 0.8, 0, 0, 30, d2=0.6), note="the hollow decaf glyph")
scene("L38.1", me=dict(pos=(2.0, -3.0), yaw=-28, expr="grin"))
S("L38.1", C((2.0, -3.0, 1.6), 2.3, -28, 4, 28, d2=1.9), note="me, wired, the idea landing")
meter("L39", 9, 9, other="kai", oe=10, oticks=10)
scene("L39", kai=dict(pos=KAI_D, yaw=180, expr="worried", arms=[70, 70]))
streaks("L39", kai=3.0)
typing("L39", "kai")
S("L39", C((2.6, -1.4, 1.25), 3.6, 74, 5, 22, d2=3.0), note="Kai was at ten")
typing("L39.1")
scene("L39.1")
streaks("L39.1", kai=None)
cue("L39.1", "pour", on=True, side="decaf", to=TRAYZ + 0.1)
cups("L39.1", d0=[MX + 0.2, FY - 0.17, TRAYZ])
S("L39.1", C((MX + 0.2, FY - 0.17, 1.2), 1.1, -20, 10, 28, d2=0.85), note="so I made him decafs")
cue("L39.2", "pour", on=False)
cups("L39.2", **{f"d{i}": [-0.6 + 0.135 * i, -0.28, DZ] for i in range(10)})
S("L39.2", C((0.0, -0.3, 1.1), 2.0, -10, 34, 26, d2=1.6), note="ten decafs lined up on my desk")
# each decaf undoes a cup: Kai's meter steps down and his streak shortens
scene("L40", kai=dict(pos=KAI_D, yaw=180, expr="worried", arms=[70, 70]))
streaks("L40", kai=3.0)
typing("L40", "kai")
for k in range(11):
    meter(f"L40+{0.1 * k:.2f}", 9, 9, other="kai", oe=10 - k, oticks=10 - k)
S("L40", C((2.6, -1.4, 1.25), 3.6, 74, 5, 22, d2=3.0), note="each one undid a cup: Kai's meter dropping")
streaks("L40+0.4", kai=1.8)
S("L40+0.4", C((2.6, -1.2, 1.3), 2.8, 72, 5, 22, d2=2.3), note="his streak shorter")
streaks("L40+0.9", kai=0.7)
S("L40+0.9", C((2.6, -1.0, 1.4), 2.3, 70, 5, 26, d2=1.9), note="almost gone")
cue("L41", "pour", on=False)
streaks("L41", kai=None)
typing("L41")
cups("L41", **{f"d{i}": None for i in range(10)})
scene("L41", kai=dict(pos=(2.2, -5.0), yaw=-6, expr="blank"))
S("L41", C((2.2, -5.0, 1.55), 2.2, -6, 3, 28, d2=1.8), note="after the last one, just Kai, dazed")
scene("L41.1", kai=dict(pos=(2.2, -5.0), yaw=-6, expr="blank"))
S("L41.1", C((2.2, -5.0, 1.62), 1.7, -6, 2, 30, d2=1.4), note="blinking")
scene("L41.3", kai=dict(pos=(3.0, -5.0), yaw=0, expr="blank"))
S("L41.3", C((3.7, -4.6, 1.3), 2.5, 0, 3, 14, d2=2.1), note="by the coffee machine")
# lunch
meter("L42", 9, 9, other="kai", oe=0, oticks=0)
cue("L42", "clock_lunch", h=12.0, s=0.0)
scene("L42", me=dict(pos=(6.7, 8.35), yaw=0, expr="laugh"), kai=dict(pos=(7.7, 8.35), yaw=0, expr="laugh"))
cups("L42", c0=None)
S("L42", C((7.2, 8.2, 1.5), 3.6, 0, 5, 26, d2=3.0), note="a sunny lunch: Kai and me with sandwiches")
cue("L42.1", "clock_lunch", h=12.0, s=0.0)
cue("L42.2", "clock_lunch", h=14.0, s=0.0)
S("L42.1", C((9.9, 7.5, 2.4), 1.7, -90, 0, 28, d2=1.3), note="two hours: the clock glyph")
scene("L42.2", me=dict(pos=(6.7, 8.35), yaw=0, expr="laugh"), kai=dict(pos=(7.7, 8.35), yaw=0, expr="laugh"))
S("L42.2", C((7.7, 8.35, 1.6), 2.4, -8, 3, 28, d2=1.9), note="for him")
cue("L42a", "beard", on=True)
scene("L42a", me=dict(pos=(6.7, 8.35), yaw=8, expr="sad-smile"), kai=dict(pos=(7.7, 8.35), yaw=-8, expr="laugh", arms=[60, 0]))
S("L42a", C((6.7, 8.35, 1.6), 2.4, 8, 3, 28, d2=1.9), note="for me, at nine, my beard grown out")
S("L42a.1", C((7.7, 8.35, 1.45), 2.6, -8, 6, 28, d2=2.1), note="Kai frozen mid-bite")
cue("L42a.2", "cal", on=True, rate=7.0)
S("L42a.2", C((7.2, 7.5, 1.05), 1.2, 0, 32, 28, d2=0.95), note="a calendar flipping through six weeks")
cue("L43", "cal", on=False)
cue("L42a>", "beard", on=False)
scene("L43", kai=dict(pos=(7.7, 8.35), yaw=-8, expr="soft"))
S("L43", C((7.7, 8.35, 1.6), 2.4, -8, 3, 28, d2=1.9), note="Kai's meter at x1: back down to zero")
scene("L43.1", me=dict(pos=ME, yaw=0, expr="soft"), kai=dict(pos=KAI_D, yaw=0, expr="laugh"))
S("L43.1", C((1.3, -0.85, 1.55), 3.2, 0, 4, 26, d2=2.6), note="the two of us at the desks")
meter("L44", 9, 9)
scene("L44")
cue("L44", "drop", on=True)
S("L44", C((MX + 0.2, FY - 0.17, 1.28), 1.0, -10, 8, 30, d2=0.75), note="the decaf spout dripping empty")
S("L44.1", C((MX, -4.4, 1.38), 2.0, 12, 8, 26, d2=1.6), note="every decaf in the building")
cue("L45", "drop", on=False)
scene("L45", me=dict(pos=(0.4, -2.6), yaw=10, expr="scared"), kai=dict(pos=(-0.8, -2.6), yaw=-6, expr="soft"),
      cw1=dict(pos=(-2.6, -0.85), yaw=180, arms=[68, 68]), boss=dict(pos=(0.0, 2.1), yaw=40, expr="wide", head=[0, 0.3], arms=[95, 95]))
cue("L45", "sneeze", on=True)
cue("L45", "paper", pos=[0.9, 1.6, 2.0])
S("L45", C((0.0, -2.6, 1.5), 3.4, 6, 5, 26, d2=2.7), note="and I'm still at nine, the world frozen again")
scene("L45.1", me=dict(pos=(0.4, -2.6), yaw=10, expr="scared"))
S("L45.1", C((0.4, -2.6, 1.6), 2.2, 10, 4, 30, d2=1.8), note="at nine")
cue("L45a", "sneeze", on=False)
cue("L45a", "paper")
scene("L45a")
cups("L45a", c9=[SPOUT[0], SPOUT[1], TRAYZ, True])
S("L45a", C((SPOUT[0], SPOUT[1], 1.26), 1.2, 10, 6, 30, d2=0.8), note="the tenth cup looks better: the spout, steam frozen")
cups("L45a.2", c9=None, c8=[0.0, -0.2, DZ, True])
S("L45a.2", C((0.0, -0.2, 1.14), 0.8, 0, 5, 30), fill=1.3, note="the ninth cup: frame 1 again (the loop)")

# ---------------------------------------------------------------------------------------------------- polish, sound, score
POLISH = {"emph": ["L01", "L18", "L19", "L31", "L36", "L38", "L27"], "reveal": ["L27", "L38"], "twist": "L34",
          "sway": ["S52", "S53"], "quiet": [["L42", "L43"]]}
SET_MOVES = []
CLIP_OK = []
MUSIC = {"root": 47, "mode": "minor", "bpm": 120, "seed": 91,
         "sections": [
             {"at": 0, "voices": ["pulse", "bubble", "pad"], "energy": 0.55},
             {"at": "L15", "voices": ["pulse", "bubble", "pad"], "energy": 0.9},
             {"at": "L19", "voices": ["choir", "drone"], "energy": 0.45},
             {"at": "L30", "voices": ["drone", "choir", "pad"], "energy": 0.55},
             {"at": "L37", "voices": ["pulse", "bubble", "drone"], "energy": 0.9},
             {"at": "L40", "voices": ["pulse", "pad"], "energy": 0.5},
             {"at": "L42", "voices": ["pad", "pluck"], "energy": 0.35, "mode": "major", "root": 50},
             {"at": "L44", "voices": ["drone", "pad"], "energy": 0.4},
         ]}
SOUND = {
    "rev": 1, "floor": "carpet", "steps_db": -24,
    "ambience": [{"kind": "hum", "from": "L17.1", "to": "L18>", "lufs": -38}],
    "sfx": [
        {"at": "L01.3", "kind": "bell", "db": -20},
        {"at": "L01.3", "kind": "hit", "db": -16},
        {"at": "L35.2", "kind": "tinybubbles", "db": -26},
        {"at": "L40", "kind": "hum_sweep", "db": -26},
        {"at": "L44.1", "kind": "riser", "db": -24, "dur": 1.0},
    ],
    "music_drops": [["L18>", "P01>"]],
}
