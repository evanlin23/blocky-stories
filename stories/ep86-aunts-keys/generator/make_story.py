"""Writes ../story.json for "Aunt Lou Has A Key To YOURS" (ep86-aunts-keys, batch 8).

Run from anywhere: python stories/ep86-aunts-keys/generator/make_story.py
The words are in lines.json next to this file. Everything else is here: the cast (me, Aunt Lou, Mr. Park, Mrs. Haddad),
the shots and their cameras, the acting, the cues set.py reads (ring, tags, clock, room, door<k>, hand, box, phone, ...)
and the score.

World (metres, z up): a horseshoe court of twelve houses on a ring of radius 11 round a fountain at the origin, open
toward -y. House k stands at angle A0 + (k-1)*DA (from +y toward +x) and its door faces the fountain. house-local
coordinates (hw): origin at the door's foot, x along the facade, y out of the wall toward the fountain's side is -y.
The interior is one room at (40, 0) re-dressed by the "room" cue; a pocket close-up is at (60, 0).
Acting yaw: 0 faces -y, 180 faces +y, 90 faces +x, -90 faces -x.
"""
import json
import math
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[2]))
OUT = HERE.parent / "story.json"
lines = json.loads((HERE / "lines.json").read_text())
LOOP = 0.25

R, A0, DA = 11.0, -125.0, 250.0 / 11
RX, RY = 40.0, 0.0           # the interior
MX, MY = 60.0, 0.0           # the pocket close-up
BRASS = "#d8a93b"

# ---------------------------------------------------------------------------------------------------- cast
FACE = {"eyes": "round", "brows": True, "ink": "#24131f"}
cast = {
    "me": {"age": "adult", "skin": "#e8b88a", "shirt": "#2f7a4a", "pattern": "solid", "pants": "#8a8d96", "shoes": "#f4f4f2",
           "sleeves": "long", "hair": "spiky", "hair_c": "#16131a", "extras": ["hooddown"], "extra_c": "#256a3e",
           "face": dict(FACE)},
    "lou": {"age": "adult", "skin": "#f1c9a0", "shirt": "#ffc23a", "pattern": "solid", "pants": "#6b4a2a", "shoes": "#6b3d1e",
            "sleeves": "long", "hair": "long", "hair_c": "#f6f4ee", "extras": ["coat", "glasses"], "extra_c": "#3a3a46",
            "zip_c": "#d8a93b", "height": 0.94, "width": 1.0,
            "face": {"eyes": "lashes", "brows": True, "ink": "#24131f"}},
    "park": {"age": "adult", "skin": "#d9a27a", "shirt": "#5f78b5", "pattern": "stripes", "pattern_c": "#eef0f8",
             "pants": "#4a5a8a", "shoes": "#6b3d1e", "sleeves": "long", "hair": "buzz", "hair_c": "#a4a9b3",
             "extras": ["tie"], "extra_c": "#eef0f8", "width": 1.1, "face": dict(FACE)},
    "haddad": {"age": "adult", "skin": "#b88a62", "shirt": "#2fb5a8", "pattern": "knit", "pattern_c": "#259b90",
               "pants": "#3a3a4a", "shoes": "#f4f4f2", "sleeves": "long", "hair": "bun", "hair_c": "#2a1c18", "height": 0.96,
               "face": {"eyes": "lashes", "brows": True, "ink": "#24131f"}},
}

# ---------------------------------------------------------------------------------------------------- state
NEUTRAL = {"arms": [0, 0], "side": [0, 0], "head": [0, 0], "lean": 0, "tremble": 0, "blink": True}
acting = {k: [] for k in cast}
cues = []
shots = []


def raw(who, at, **kw):
    acting[who].append({"at": at, **kw})


def put(who, at, pos, yaw=0, expr="neutral", **kw):
    """The character is there from this instant (a cut); everything it doesn't set goes back to neutral."""
    keys = acting[who]
    prev = next((k["pos"] for k in reversed(keys) if "pos" in k), None)
    if prev is not None:
        keys.append({"at": at, "pos": prev})
    keys.append({"at": at, "pos": list(pos), "blend": 0, "yaw": yaw, "expr": expr, "hidden": False, **NEUTRAL, **kw})


def walk(who, at0, pos0, at1, pos1, yaw=None, expr="neutral", **kw):
    put(who, at0, pos0, yaw if yaw is not None else 0, expr, **kw)
    raw(who, at1, pos=list(pos1))


def gone(who, at):
    acting[who].append({"at": at, "hidden": True, "blend": 0})


def cue(at, name, **kw):
    cues.append({"at": at, "name": name, **kw})


# ---------------------------------------------------------------------------------------------------- geometry
def ang(k):
    return A0 + (k - 1) * DA


def hw(k, lx, ly, z):
    """House-local (lx along the facade, ly out of the wall: negative is toward the fountain) to world."""
    a = math.radians(ang(k))
    ox, oy, rz = R * math.sin(a), R * math.cos(a), -a
    c, s = math.cos(rz), math.sin(rz)
    return [round(ox + lx * c - ly * s, 3), round(oy + lx * s + ly * c, 3), z]


def front(k, d, lx=0.0, z=0.0):
    return hw(k, lx, -d, z)


def yawf(k):
    return 180 - ang(k)          # facing the house


def yawc(k):
    return -ang(k)               # facing the fountain


def yaw_to(p, q):
    return math.degrees(math.atan2(q[0] - p[0], -(q[1] - p[1])))


def K_(pos, tgt, lens, pos2=None, tgt2=None, lens2=None):
    ks = [[0, list(pos), list(tgt), lens]]
    if pos2 or tgt2 or lens2:
        ks.append([1, list(pos2 or pos), list(tgt2 or tgt), lens2 or lens])
    return ks


def HC(k, lp, lt, lens, lp2=None, lt2=None, lens2=None):
    """A camera given in house-local coordinates."""
    def sc(a, t):   # a camera close to a keyhole stands 2.2 times further off (the ring is small)
        if a is not None and abs(t[0] - 0.38) < 0.01 and -0.22 < t[1] < -0.1 and t[2] < 0.9:
            return tuple(t[i] + (a[i] - t[i]) * 2.2 for i in range(3))
        return a
    lp, lp2 = sc(lp, lt), sc(lp2, lt2 or lt) if lp2 else None
    return K_(hw(k, *lp), hw(k, *lt), lens, hw(k, *lp2) if lp2 else None, hw(k, *lt2) if lt2 else None, lens2)


def FC(p, yaw, d, off=15, el=4, lens=40, h=1.5, th=None, d2=None, lens2=None, off2=None, h2=None):
    """A camera in front of a character at p facing yaw: distance d, `off` degrees round from straight on."""
    th = h if th is None else th

    def pos(dd, of, hh):
        a = math.radians(yaw + of)
        return [round(p[0] + dd * math.sin(a), 3), round(p[1] - dd * math.cos(a), 3), round(hh + dd * math.sin(math.radians(el)), 3)]

    tgt = [p[0], p[1], th]
    if d2 is None and lens2 is None and off2 is None and h2 is None:
        return [[0, pos(d, off, h), tgt, lens]]
    return [[0, pos(d, off, h), tgt, lens],
            [1, pos(d2 or d, off if off2 is None else off2, h if h2 is None else h2), [p[0], p[1], th if h2 is None else h2], lens2 or lens]]


def W(p, d, az, el, lens, h=1.0, d2=None, lens2=None, az2=None):
    """A camera at distance d from point p, azimuth az (0: camera on the -y side), elevation el."""
    def pos(dd, a_):
        a = math.radians(a_)
        e = math.radians(el)
        return [round(p[0] + dd * math.sin(a) * math.cos(e), 3), round(p[1] - dd * math.cos(a) * math.cos(e), 3), round(h + dd * math.sin(e), 3)]

    tgt = [p[0], p[1], h]
    ks = [[0, pos(d, az), tgt, lens]]
    if d2 or lens2 or az2 is not None:
        ks.append([1, pos(d2 or d, az if az2 is None else az2), tgt, lens2 or lens])
    return ks


def S(at, cam, look="day", hand=0.006, fill=1.0, exp=0.0, step=2, note="", dof=None, rkey=1.0, tag=None, face=False):
    d = {"id": f"S{len(shots) + 1:02d}", "cam": cam, "step": step, "hand": hand, "look": look}
    if len(shots):
        d["at"] = at
    for k, v, dflt in (("fill", fill, 1.0), ("exp", exp, 0.0), ("rkey", rkey, 1.0)):
        if v != dflt:
            d[k] = v
    if face:
        d["face"] = True
    if dof:
        d["dof"] = dof
    if note:
        d["note"] = note
    shots.append(d)
    return d


# ---------------------------------------------------------------------------------------------------- cue helpers
GLOW = []          # the tags lit now


def tags(at, glow):
    GLOW[:] = sorted(glow)
    cue(at, "tags", glow=list(GLOW), big=False)


def tags_big(at, glow):
    cue(at, "tags", glow=list(glow), big=True)


def clock(at, text=None, day=None):
    cue(at, "clock", text=text, day=day)


def ring(at, k=None, pos=None, yaw=0, turn=(0, 0), dur=1.0, hand=True, tilt=0, on=True, lx=0.38, lz=0.78, scale=1.0):
    if k is not None:
        pos = hw(k, lx, -0.145, lz)
        yaw = -ang(k)
    if not on:
        cue(at, "ring", on=False)
        return
    cue(at, "ring", on=True, pos=list(pos), yaw=yaw, turn=list(turn), dur=dur, hand=hand, tilt=tilt, scale=scale)


def RK(k, lx, ly, z, dx=0.0):
    """A world point given relative to house k's keyhole (so a camera can sit right by the key)."""
    return hw(k, 0.38 + lx, -0.145 + ly, 0.78 + z)


def door(at, k, a0, a1, dur=0.8):
    cue(at, f"door{k}", a0=a0, a1=a1, dur=dur)


def room(at, show, **kw):
    cue(at, "room", show=list(show), **kw)


def hand(at, k=None, pos=None, yaw=0, shake=0.0, on=True, dur=1.0, a0=0, a1=0, lx=0.38, lz=1.0, ly=-0.19):
    if not on:
        cue(at, "hand", on=False)
        return
    if k is not None:
        pos = hw(k, lx, ly, lz)
        yaw = -ang(k)
    cue(at, "hand", on=True, pos=list(pos), yaw=yaw, shake=shake, dur=dur, a0=a0, a1=a1)


# ---------------------------------------------------------------------------------------------------- places
ME, LOU, PARK, HAD = "me", "lou", "park", "haddad"
PORCH = hw(7, -0.9, -0.75, 3.0)
FOOT_T = [0.0, 0.0, 1.0]


def footage(lens=13, tgt=(0.0, 0.0, 1.0)):
    return K_(PORCH, list(tgt), lens)


def ARC(k, d=1.0, lx=0.0):
    return front(k, d, lx)


# ================================================================================================== S01 - S26: the montage
# --- S01/S02: Lou at a stranger's red door at dusk, her key already in the deadbolt, her face in frame from frame 1
LOCK4 = hw(4, 0.38, -0.155, 1.3)
LOU_AT = hw(4, 0.95, -0.4, 0.0)
_LOOKAT = hw(4, 0.3, -0.15, 0.0)
_CAM0 = hw(4, -0.1, -2.1, 1.5)
LOU_YAW = yaw_to(LOU_AT, _LOOKAT)
_hy = (yaw_to(LOU_AT, _CAM0) - LOU_YAW + 180) % 360 - 180
LOU_HEAD = [round(_hy * 0.85, 1), 0]
ring(0, k=4, lz=1.3, turn=(0, 0), dur=1.0, hand=False, scale=2.3)
put(LOU, 0, LOU_AT, LOU_YAW, "brisk", arms=[72, 72], head=LOU_HEAD)
S(0, HC(4, (-0.1, -2.1, 1.45), (0.72, -0.3, 1.3), 28, (0.05, -1.8, 1.42), (0.68, -0.3, 1.3), 32), "dusk", fill=1.6, hand=0.003, note="Lou's face, the ring in her hands, a key in a red door's lock")
ring("L02", k=4, lz=1.3, turn=(0, 80), dur=0.5, hand=False, scale=2.3)
S("L02", HC(4, (0.05, -0.95, 1.5), (0.4, -0.15, 1.32), 38, (0.15, -0.75, 1.46), (0.4, -0.15, 1.32), 44), "dusk", fill=1.6, hand=0.003, note="the key turning")
ring("L02.2", k=4, turn=(80, 80), dur=1.0, on=False)
gone(LOU, "L02.2")
clock("L02.2", None)
clock("L56", None)
clock("L57", "05:52")
clock("L59", None)
# --- S03: the court by day from above; S04: at midnight
S("L02.1", K_([0, -27, 16], [0, 3, 1.5], 14, [2, -24, 13], [0, 3, 1.5], 14.5), "day", hand=0.0, note="twelve houses round a fountain")
S("L03.1", K_([7, -25, 9], [-1, 2, 1.8], 17, [5, -22, 8], [-1, 2, 1.8], 18), "day", hand=0.0, note="closer on the fountain")
S("L04", K_([-5, -21, 7.0], [0, 1, 2.0], 15, [-3, -19, 6.0], [0, 1, 2.2], 15), "night", hand=0.0, note="midnight, four lamps on")
S("L04.2", HC(5, (-0.3, -2.8, 1.0), (0.1, 0.0, 1.6), 20, (-0.1, -2.2, 1.1), (0.1, 0.0, 1.5), 20), "night", note="you can hear it from every door")
# --- S05: three keys turning in three locks
ring("L05", k=2, turn=(0, 70), dur=0.5)
S("L05", HC(2, (0.05, -0.55, 0.9), (0.38, -0.13, 0.78), 40, (0.15, -0.42, 0.86), (0.38, -0.13, 0.78), 46), "night", fill=1.4, hand=0.003, note="CLICK one")
ring("L05.1", k=8, turn=(0, 70), dur=0.5)
S("L05.1", HC(8, (0.6, -0.5, 0.7), (0.38, -0.13, 0.78), 40, (0.52, -0.4, 0.74), (0.38, -0.13, 0.78), 46), "night", fill=1.4, hand=0.003, note="click two")
ring("L05.2", k=11, turn=(0, 70), dur=0.5)
S("L05.2", HC(11, (0.25, -0.5, 1.0), (0.38, -0.13, 0.78), 40, (0.3, -0.4, 0.92), (0.38, -0.13, 0.78), 46), "night", fill=1.4, hand=0.003, note="CLICK three")
# --- S06: before sunrise she unlocks them all again
ring("L06", k=5, turn=(70, 0), dur=0.6)
S("L06", HC(5, (0.62, -0.6, 0.7), (0.38, -0.13, 0.78), 38, (0.52, -0.46, 0.76), (0.38, -0.13, 0.78), 44), "dawn", fill=1.3, hand=0.003, note="the key turning back")
ring("L06.1", k=9, turn=(70, 0), dur=0.5)
S("L06.1", HC(9, (0.1, -0.55, 0.9), (0.38, -0.13, 0.78), 40, (0.2, -0.42, 0.86), (0.38, -0.13, 0.78), 46), "dawn", fill=1.3, hand=0.003, note="click, click")
ring("L06.2", on=False)
put(LOU, "L06.2", front(9, 1.6, -3.0), yawf(9) + 70, "neutral")
raw(LOU, "L06>", pos=front(10, 1.6, 1.0), run=True)
S("L06.2", K_([-3, -9.5, 1.4], [3, 3, 1.4], 18, [-2, -9.5, 1.4], [4, 3, 1.4], 20), "dawn", note="she unlocks them all again")
# --- S07 Mr. Park asleep in his armchair facing his door
room("L07", ["armchair", "door_a"], chair_yaw=180)
put(PARK, "L07", [RX + 0.0, RY + 1.0, 0.3], 180, "shut", lean=-28, head=[0, -8])
S("L07", FC([RX + 0.45, RY + 1.0], 180, 1.9, -20, 4, 28, 1.55, 1.6, d2=1.6), "int", hand=0.004, rkey=1.0, note="Mr. Park asleep, face")
S("L07.2", K_([RX + 0.9, RY - 2.4, 1.9], [RX + 0.1, RY + 1.6, 1.35], 15, [RX + 0.6, RY - 2.0, 1.8], [RX + 0.1, RY + 1.6, 1.35], 17), "int", hand=0.004, rkey=0.6, note="facing his door")
# --- S08 Mrs. Haddad with the new lock
cue("L08", "padlock", on=True, pos=front(9, 1.0, 0.0, 1.2))
put(HAD, "L08", front(9, 1.1, 0.0), yawf(9) + 180, "angry", arms=[75, 75], head=[0, 5])
gone(PARK, "L08")
S("L08", FC(front(9, 1.1), yawf(9) + 180, 2.0, 20, 4, 40, 1.45, 1.4, d2=1.7), "day", note="Mrs. Haddad, a new shiny lock")
# --- S09 Lou threads a new key
cue("L09", "padlock", on=False)
put(LOU, "L09", front(1, 1.0, -1.25), yawf(1) + 180, "neutral", arms=[60, 0])
ring("L09", pos=[front(1, 1.0, -1.25)[0] + 0.05, front(1, 1.0, -1.25)[1] - 0.12, 1.15], yaw=yawf(1) + 180 - 180 + 0, turn=(0, 0), dur=1.0, hand=False)
S("L09", FC(front(1, 1.0, -1.25), yawf(1) + 180, 1.9, 28, 4, 38, 1.35, 1.2, d2=1.45), "day", note="Lou threading a new key onto her ring")
# --- S10 the shop window of blank keys
ring("L10", on=False)
gone(LOU, "L10")
S("L10", HC(1, (-1.2, -1.9, 1.55), (-1.25, 0, 1.55), 26, (-1.2, -1.2, 1.55), (-1.25, 0, 1.55), 28), "day", note="the shop window of hanging blank keys")
# --- S11 Lou on her porch
put(LOU, "L11", front(1, 1.2, 0.0), yawf(1) + 180, "neutral", arms=[70, 0])
ring("L11", pos=[front(1, 1.2, 0.0)[0], front(1, 1.2, 0.0)[1], 1.2], yaw=yawf(1) + 180, hand=False)
S("L11", FC(front(1, 1.2), yawf(1) + 180, 2.2, -22, 4, 36, 1.4, 1.35, d2=1.7), "day", note="my aunt Lou, number one, ring in hand")
ring("L11.2", on=False)
S("L11.2", HC(1, (0.0, -2.6, 1.8), (0.0, 0.0, 2.3), 28, (0.0, -2.0, 1.8), (0.0, 0.0, 2.2), 30), "day", note="number ONE: a plain latch, no lock")
# --- S12 me moving into number seven
gone(LOU, "L12")
cue("L12", "box", on=True)
put(ME, "L12", front(7, 1.4, 0.0), yawf(7) + 180, "smile", arms=[70, 70])
S("L12", FC(front(7, 1.4), yawf(7) + 180, 2.4, 15, 4, 38, 1.55, 1.6, d2=1.9), "day", note="me with a box at number seven")
S("L12.3", HC(7, (1.9, -2.4, 1.6), (0.0, 0.0, 2.2), 28, (1.6, -1.9, 1.7), (0.0, 0.0, 2.1), 30), "day", note="number SEVEN, my new doormat")
S("L12.4", FC(front(7, 1.4), yawf(7) + 180, 1.5, -18, 3, 40, 1.58, 1.58), "day", note="my first place")
# --- S13 my one key into my pocket
cue("L13", "box", on=False)
gone(ME, "L13")
cue("L13", "pocket", on=True, dur=1.0)
S("L13", K_([MX + 0.05, MY - 2.6, 1.3], [MX + 0.05, MY, 0.7], 30, [MX + 0.05, MY - 2.1, 1.1], [MX + 0.05, MY, 0.65], 32), "day", fill=1.3, note="my one key into my pocket")
# --- S14 close on her ring: the tag with 7
cue("L14", "pocket", on=False)
RP = [-8.0, -5.8, 1.15]
ring("L14", pos=RP, yaw=-ang(1) + 0, hand=True)
S("L14", K_([RP[0] + 0.0, RP[1] + (-0.0) - 0.3, RP[2] - 0.2], [RP[0], RP[1] - 0.08, RP[2] - 0.2], 40), "day", fill=1.3, hand=0.002, note="the ring: a tag with 7")
# --- S15 the court at midnight from my window, tags glowing one by one
ring("L15", on=False)
tags("L15", [])
for i, n in enumerate([2, 3, 4, 5, 6, 8, 9, 10, 11, 12]):
    tags(f"L15+{0.05 + i * 0.14:.2f}", [2, 3, 4, 5, 6, 8, 9, 10, 11, 12][:i + 1])
S("L15", K_(hw(7, -0.95, -0.8, 4.3), [0, 0, 1.6], 11, hw(7, -0.95, -1.0, 4.35), [0, 0, 1.6], 11.5), "night", hand=0.003, note="from my window, the tags glow")
# --- S16 my door from inside, the lock still open, tag 7 dark
room("L16", ["door_b"])
S("L16", K_([RX + 0.9, RY + 0.7, 1.15], [RX + 0.6, RY + 2.85, 1.0], 30, [RX + 0.85, RY + 1.2, 1.1], [RX + 0.6, RY + 2.85, 0.95], 34), "intn", hand=0.004, rkey=0.8, note="my door from inside, still open")
# --- S17 morning: waking in bed in wet sneakers, grass on the floor
tags("L17", [])
room("L17", ["bed", "grass"], bed_yaw=0)
put(ME, "L17", [RX + 1.9, RY + 0.3, 0.7], 0, "shut", lean=-90, head=[0, 0])
raw(ME, "L17.1", expr="worried")
S("L17", K_([RX + 0.2, RY - 1.4, 2.6], [RX + 1.9, RY + 1.6, 0.6], 26, [RX + 0.5, RY - 1.2, 2.3], [RX + 1.9, RY + 1.5, 0.6], 28), "int", note="waking in bed")
S("L17.2", K_([RX + 1.9, RY - 0.1, 0.95], [RX + 1.9, RY + 0.8, 0.52], 34, [RX + 1.7, RY - 0.0, 0.85], [RX + 1.9, RY + 0.8, 0.5], 38), "int", note="the sneakers, wet")
S("L17.3", K_([RX + 1.0, RY - 0.4, 0.9], [RX + 1.7, RY + 0.6, 0.0], 30, [RX + 1.0, RY - 0.3, 0.8], [RX + 1.6, RY + 0.6, 0.0], 32), "int", note="grass on the floorboards")
# --- S18/S19 the neighbours
room("L18", [])
gone(ME, "L18")
put(PARK, "L18", [2.2, -2.8, 0.0], 235, "neutral", head=[-35, 0])
put(HAD, "L18", [0.4, -3.3, 0.0], 100, "neutral", head=[30, 0])
S("L18", W([1.4, -3.1], 3.0, 10, 4, 36, h=1.4, d2=2.2), "day", note="two neighbours whispering at the fountain")
put(PARK, "L19", [1.6, -2.6, 0.0], 200, "angry", head=[0, 10])
raw(PARK, "L19.2", head=[0, -6])
gone(HAD, "L19")
S("L19", FC([1.6, -2.6], 200, 1.6, 12, 3, 40, 1.55, 1.55, d2=1.2), "day", note="the night landlady")
# --- S20 me embarrassed; S21 Lou and me on her step; S22 palm out; S23 Lou soft
gone(PARK, "L20")
put(ME, "L20", front(1, 2.4, 0.9), yawf(1) + 180 - 20, "sad-smile", head=[0, 8])
S("L20", FC(front(1, 2.4, 0.9), yawf(1) + 160, 1.5, 15, 3, 40, 1.58, 1.58, d2=1.2), "day", note="me, embarrassed")
put(ME, "L21", front(1, 2.0, 1.2), yawf(1) + 180 - 90, "angry")
put(LOU, "L21", front(1, 1.2, 0.0), yawf(1) + 180 + 40, "neutral")
S("L21", W(front(1, 1.6, 0.4), 4.4, 20, 5, 30, h=1.1, d2=3.6), "day", note="Lou and me on her step")
put(ME, "L22", front(1, 2.0, 1.2), yawf(1) + 180 - 90, "angry", arms=[85, 85])
S("L22", FC(front(1, 2.0, 1.2), yawf(1) + 180 - 90, 1.9, 35, 4, 36, 1.4, 1.3, d2=1.5), "day", note="palm out for the ring")
gone(ME, "L23")
put(LOU, "L23", front(1, 1.2, 0.0), yawf(1) + 180 + 40, "soft", head=[0, 5])
ring("L23", pos=[front(1, 1.2, 0.0)[0] + 0.15, front(1, 1.2, 0.0)[1] + 0.1, 1.0], yaw=yawf(1) + 180 + 40, hand=False)
S("L23", FC(front(1, 1.2, 0.0), yawf(1) + 180 + 40, 2.4, 25, 3, 36, 1.35, 1.35, d2=2.0), "day", fill=1.0, face=True, note="Lou, soft, not handing it over")
ring("L24", on=False)
gone(LOU, "L24")
# --- S24 I leave my door open on purpose; S25 the camera; S26 its view
put(ME, "L24", front(7, 1.0, -0.8), yawf(7) + 180 + 70, "angry")
S("L24", FC(front(7, 1.0, -0.8), yawf(7) + 250, 2.0, 25, 4, 34, 1.5, 1.4, d2=1.5), "dusk", fill=1.2, note="at my door that night")
S("L24.1", HC(7, (0.2, -0.6, 1.0), (0.38, -0.13, 0.8), 42, (0.3, -0.45, 0.96), (0.38, -0.13, 0.8), 48), "dusk", fill=1.3, note="on PURPOSE")
gone(ME, "L25")
S("L25", HC(7, (-0.4, -1.4, 3.3), (-0.9, -0.5, 3.0), 38, (-0.55, -1.0, 3.2), (-0.9, -0.5, 3.0), 44), "dusk", note="the little camera on its bracket")
S("L25.2", HC(7, (-1.5, -1.0, 3.0), (-1.0, -1.8, 2.9), 30, (-1.3, -0.9, 3.0), (0.0, -6, 1.6), 22), "dusk", note="facing the court")
S("L25.3", K_(PORCH, [0, 0, 1.0], 12, [PORCH[0] - 0.1, PORCH[1] - 0.1, PORCH[2]], [0, 0, 1.0], 13), "dusk", note="what it sees")
S("L26", K_(PORCH, [0, 0, 1.0], 14), "day", hand=0.0, note="the camera's view by day")
clock("P01", "12:00")
tags("P01", [])
S("P01", K_(PORCH, [0, 0, 1.0], 13, [PORCH[0] - 0.1, PORCH[1] - 0.1, PORCH[2]], [0, 0, 1.0], 13), "night", hand=0.0, fill=1.2, note="the footage, still, 12:00")

# ================================================================================================== S27 - S39: the footage, 12:01 to 12:04
clock("L27", "12:01")
S("L27", K_(PORCH, [0, 0, 1.0], 15), "night", hand=0.0, fill=1.2, note="12:01")
put(LOU, "L28", front(1, 1.1, 0.0), yawf(1) + 180, "neutral")
walk(LOU, "L28", front(1, 1.1, 0.0), "L28.1", front(1, 3.0, 0.8), yaw=yawc(1) + 20)
S("L28", K_(PORCH, [-2, -1, 1.0], 12), "night", hand=0.0, fill=1.2, note="Aunt Lou comes in from number one")
S("L28.1", K_(PORCH, [-6.0, -3.5, 1.1], 22, PORCH, [-5.2, -4.6, 1.1], 26), "night", hand=0.0, fill=1.3, note="in her yellow raincoat")
# the race: door to door, 2, 3, 4, 5, 6 then 8..12 (skipping 7), each key turns and the tags glow
tags("L29", [2])
RACE1 = [2, 3, 4, 5, 6]
put(LOU, "L29", front(2, 2.6, 0.0), yawf(2) + 180, "neutral", run=True)
tL = {}
S("L29", K_(PORCH, [-7.5, 1.0, 1.0], 19, PORCH, [-6.0, 4.0, 1.0], 22), "night", hand=0.0, fill=1.3, note="door to door, fast")
raw(LOU, "L29.2", pos=front(3, 1.1, 0.0), run=True)
raw(LOU, "L29.3", pos=front(4, 1.1, 0.0), run=True)
raw(LOU, "L29.4", pos=front(5, 1.1, 0.0), run=True)
raw(LOU, "L29>", pos=front(6, 1.1, 0.0), run=True)
tags("L29.2", [2, 3])
tags("L29.3", [2, 3, 4])
tags("L29.4", [2, 3, 4, 5])
ring("L29.2", k=3, turn=(0, 70), dur=0.5, hand=True)
S("L29.2", HC(3, (0.1, -0.55, 0.9), (0.38, -0.13, 0.78), 40, (0.2, -0.42, 0.86), (0.38, -0.13, 0.78), 46), "night", fill=1.4, hand=0.003, note="a key turning, fast")
ring("L29.4", on=False)
S("L29.3", K_(PORCH, [2.0, 7.0, 1.0], 20, PORCH, [3.5, 6.0, 1.0], 22), "night", hand=0.0, fill=1.3, note="Lou across the court")
tags("L29>", [2, 3, 4, 5, 6])
# --- S30: close on Lou's face, worried, glancing at my door
put(LOU, "L30", front(6, 1.3, 0.2), yawf(6) + 180 + 25, "worried", head=[40, 0], look=[0.8, 0])
gone(LOU, "L32+0.8")
S("L30", FC(front(6, 1.3, 0.2), yawf(6) + 180 + 25, 2.3, 10, 3, 36, 1.35, 1.35, d2=1.95), "night", fill=2.0, note="her face, worried")
walk(LOU, "L31", front(6, 1.3, 0.2), "L31>", front(8, 1.3, 0.0), yaw=None, expr="worried", run=True)
S("L31", K_(PORCH, [3.5, 8.0, 1.0], 21, PORCH, [2.6, 8.6, 1.0], 24), "night", hand=0.0, fill=1.3, note="she passes number seven")
# L32: she steps inside number one, leaving her door open
put(LOU, "L32", front(1, 1.5, 0.45), yawf(1) + 180, "neutral")
raw(LOU, "L32.1", pos=front(1, 0.95, 0.45))
door("L32", 1, 0, 85, 0.5)
S("L32", HC(1, (0.9, -4.6, 1.6), (0.0, 0.0, 1.2), 22, (0.7, -4.0, 1.6), (0.0, 0.0, 1.2), 24), "night", fill=1.3, note="she skips her own door")
gone(LOU, "L33")
clock("L33", "12:04")
clock("L67", None)
tags("L33", [2, 3, 4, 5, 6, 8, 9, 10, 11, 12])
S("L33", K_(PORCH, [0, 0, 1.0], 14, PORCH, [0.3, 0.2, 1.0], 16), "night", hand=0.0, fill=1.2, note="12:04")
# --- the hush before it: my door, closed, a held breath
S("P02", HC(7, (-1.5, -4.6, 1.9), (0.0, 0.0, 1.2), 20, (-1.1, -3.9, 1.8), (0.0, 0.0, 1.2), 22), "night", hand=0.002, fill=1.2, note="my door, closed, still")
# --- S34: my door opens from inside
door("L34", 7, 0, 80, 0.9)
S("L34", HC(7, (-1.0, -3.4, 1.9), (0.0, 0.0, 1.2), 24, (-0.7, -2.8, 1.8), (0.0, 0.0, 1.2), 26), "night", hand=0.002, fill=1.2, note="my door swings open")
# --- S35: from behind and far, someone walks out slow, arms a little out
walk(ME, "L35", front(7, 0.5, 0.0), "L36", [1.4, 3.8, 0.0], yaw=None, expr="shut", arms=[22, 22], head=[0, 0])
S("L35", K_(hw(7, 0.9, -3.8, 2.6), [1.2, 5.6, 0.9], 19, hw(7, 0.9, -3.4, 2.5), [1.2, 5.3, 1.0], 22), "night", hand=0.002, fill=1.0, note="from behind and far, arms out")
S("L35.2", K_(PORCH, [1.8, 5.2, 0.9], 20, PORCH, [1.6, 4.2, 0.9], 21), "night", hand=0.0, fill=1.0, note="slow, walking away")
# --- S36: three quick inserts: a hand on three handles, rattling
hand("L36", k=6, shake=1.0, lx=0.38, lz=1.0)
S("L36", HC(6, (0.7, -0.7, 1.2), (0.38, -0.15, 1.0), 40, (0.6, -0.55, 1.15), (0.38, -0.15, 1.0), 46), "night", fill=1.4, hand=0.003, note="a hand on a handle, rattling")
hand("L36.1", k=8, shake=1.0)
S("L36.1", HC(8, (0.0, -0.7, 1.3), (0.38, -0.15, 1.0), 40, (0.1, -0.55, 1.2), (0.38, -0.15, 1.0), 46), "night", fill=1.4, hand=0.003, note="another")
hand("L36.2", k=3, shake=1.0)
S("L36.2", HC(3, (0.9, -0.6, 1.1), (0.38, -0.15, 1.0), 40, (0.75, -0.5, 1.1), (0.38, -0.15, 1.0), 46), "night", fill=1.4, hand=0.003, note="and another")
# --- S37: every one holds shut
hand("L37", on=False)
walk(ME, "L37", front(5, 1.6, 0.2), "L37.1", front(5, 1.4, 0.2), yaw=yawf(5) + 180, expr="shut", arms=[22, 22])
S("L37", K_(PORCH, [-1.2, 6.8, 1.0], 20, PORCH, [-1.6, 7.4, 1.0], 22), "night", hand=0.0, fill=1.3, note="trying every door")
hand("L37.1", k=5, shake=0.6)
S("L37.1", HC(5, (-0.1, -0.6, 1.2), (0.38, -0.12, 1.0), 42, (0.0, -0.5, 1.1), (0.38, -0.12, 1.0), 48), "night", fill=1.4, hand=0.003, note="holds shut")
hand("L38", on=False)
# --- S38: it turns toward the camera under my porch lamp
put(ME, "L38", [1.6, 5.2, 0.0], yaw_to([1.6, 5.2], [1.2, 3.0]) + 0, "shut", arms=[22, 22])
raw(ME, "L38", yaw=yaw_to([1.6, 5.2], [1.2, 3.0]), blend=0)
raw(ME, "L38.1", yaw=yaw_to([1.6, 5.2], PORCH), blend=0.9)
S("L38", K_(PORCH, [1.5, 4.8, 1.2], 17, PORCH, [1.7, 5.4, 1.4], 22), "night", hand=0.0, fill=1.3, note="it turns to the camera")
# --- S39: my face, eyes shut. S43 uses the same face.
FACE_P = front(7, 2.4, 0.0)
put(ME, "L39", FACE_P, yawf(7), "asleep", arms=[22, 22])
S("L39", FC(FACE_P, yawf(7), 1.5, 6, 4, 40, 1.6, 1.6, d2=1.2), "night", hand=0.0, fill=0.3, exp=0.1, face=True, note="my face, eyes shut: it's ME")
# --- S40: me now, watching on my phone at the kitchen table
S("L40", FC(FACE_P, yawf(7), 1.3, -8, 3, 40, 1.6, 1.6, d2=1.1), "night", hand=0.0, fill=0.3, exp=0.1, face=True, note="eyes shut, fast asleep")
room("L41", ["kitchen"])
cue("L41", "phone", on=True)
put(ME, "L41", [RX - 0.3, RY - 0.4, 0.0], 150, "scared", arms=[75, 75], head=[0, 14])
S("L41", FC([RX - 0.3, RY - 0.4], 150, 1.8, 18, 3, 36, 1.5, 1.4, d2=1.4), "int", note="me now, watching, scared")
# --- S41 - S43: I walked straight at the camera, closer, and closer, until my sleeping face filled the screen
cue("L41.1", "phone", on=False)
a_end = front(7, 3.4, 0.0)
walk(ME, "L41.1", front(7, 7.5, 0.0), "L43", a_end, yaw=yawf(7), expr="asleep", arms=[22, 22])
S("L41.1", K_(PORCH, [0.6, 3.2, 1.2], 16, PORCH, [1.0, 4.0, 1.3], 18), "night", hand=0.0, fill=1.3, note="walking straight at the camera")
S("L41.2", K_(PORCH, [1.2, 5.6, 1.4], 22, PORCH, [1.4, 6.4, 1.5], 26), "night", hand=0.0, fill=1.3, note="straight at the CAMERA")
S("L42", K_(PORCH, [1.5, 7.2, 1.5], 30, PORCH, [1.7, 7.9, 1.55], 36), "night", hand=0.0, fill=1.3, note="closer")
S("L42.1", K_(PORCH, [1.7, 8.4, 1.55], 44, PORCH, [1.8, 8.8, 1.58], 52), "night", hand=0.0, fill=1.3, note="and CLOSER")
S("L43", FC(a_end, yawf(7), 1.9, 3, 4, 38, 1.6, 1.6, d2=1.15, lens2=42), "night", hand=0.0, fill=0.3, exp=0.1, face=True, note="my sleeping face fills the screen")
S("L43.2", FC(a_end, yawf(7), 1.25, 0, 3, 44, 1.6, 1.6, d2=0.95), "night", hand=0.0, fill=0.3, exp=0.1, face=True, note="eyes shut, lit warm")

# ================================================================================================== S44 - S72 (continued in the next section)
# ================================================================================================== S44 - S71
# --- S44 the court at midnight, me small at the fountain, arms out; the tally low at the rim
gone(ME, "L44")
walk(ME, "L44", [-3.6, 1.6, 0.0], "L45", [3.4, 2.2, 0.0], yaw=90, expr="asleep", arms=[22, 22])
S("L44", K_(PORCH, [0.0, 0.0, 0.9], 13, [PORCH[0] - 0.2, PORCH[1] - 0.3, PORCH[2] - 0.2], [0, 0, 0.9], 14), "night", hand=0.0, fill=1.0, note="me small at the fountain, arms out")
S("L44.1", K_([0.8, -4.8, 0.32], [0.0, -2.3, 0.3], 20, [0.4, -3.9, 0.34], [0.0, -2.3, 0.3], 22), "night", hand=0.0, fill=0.6, note="two brass strokes, low at the rim (never narrated)")
S("L44.3", K_(PORCH, [0.0, 0.0, 0.9], 15, PORCH, [0.4, 0.0, 0.9], 16), "night", hand=0.0, fill=1.0, note="at MIDNIGHT")
# --- S45 number one's lit window
door("L45", 1, 0, 85, 0.5)
put(LOU, "L45", front(1, 0.9, 0.0), yawc(1), "worried", arms=[0, 0])
S("L45", K_([-3, -14, 2.4], [-8.4, -5.6, 2.7], 15, [-4, -12.5, 2.6], [-8.4, -5.6, 2.8], 16), "night", hand=0.0, note="her door, my old room's lit window")
S("L45.2", HC(1, (0.5, -3.4, 1.4), (0.0, 0, 1.0), 26, (0.3, -2.9, 1.4), (0.0, 0, 1.05), 28), "night", fill=1.4, note="Lou in her doorway, the window lit above")
S("L45.3", K_(PORCH, [-2.0, 3.0, 0.9], 20, PORCH, [-3.5, 3.0, 0.9], 22), "night", hand=0.0, fill=1.0, note="sleepwalking home")
# --- S46 trying door after door
walk(ME, "L46", front(8, 3.0, 0.0), "L46.1", front(8, 1.4, 0.0), yaw=yawf(8), expr="asleep", arms=[22, 22])
raw(ME, "L46.2", pos=front(9, 1.4, 0.0), yaw=yawf(9))
raw(ME, "L47-0.2", pos=front(10, 1.0, 0.0), yaw=yawf(10))
S("L46", K_(PORCH, [5.0, 1.0, 1.0], 19, PORCH, [6.5, 2.0, 1.0], 22), "night", hand=0.0, fill=1.2, note="trying every door")
hand("L46.1", k=9, shake=0.7)
S("L46.1", HC(9, (0.8, -0.6, 1.2), (0.38, -0.15, 1.0), 40, (0.65, -0.5, 1.1), (0.38, -0.15, 1.0), 46), "night", fill=1.4, hand=0.003, note="a handle")
hand("L46.2", on=False)
S("L46.2", K_(PORCH, [7.0, -1.0, 1.0], 22, PORCH, [8.0, -1.8, 1.0], 24), "night", hand=0.0, fill=1.2, note="to find my old ROOM")
# --- S47 Lou at her window watching the clock; she races
door("L47", 1, 85, 0, 0.4)
clock("L47", None)
gone(ME, "L47")
room("L47", ["window", "clock", "lamp"])
put(LOU, "L47", [RX - 2.4, RY + 0.8, 0.0], 300, "worried", head=[40, 0])
S("L47", FC([RX - 2.4, RY + 0.8], 300, 3.2, 60, 4, 36, 1.4, 1.4, d2=2.8), "intn", hand=0.004, rkey=0.5, fill=1.0, note="Aunt Lou at her window, watching the clock")
clock("L47.1", "12:04")
put(LOU, "L47.1", front(2, 2.6, 0.0), yawf(2) + 180, "worried", run=True)
raw(LOU, "L48-0.2", pos=front(5, 1.2, 0.0), run=True)
put(ME, "L47.1", [0.2, 2.5, 0.0], 90, "asleep", arms=[22, 22])
raw(ME, "L48", pos=[1.2, 2.3, 0.0])
S("L47.1", K_(PORCH, [-3, 1, 1.0], 18, PORCH, [-1.5, 3.5, 1.0], 20), "night", hand=0.0, fill=1.3, note="Aunt Lou races me")
# --- S48 ten locks, ten glowing tags
ring("L48", k=5, turn=(0, 70), dur=0.5)
S("L48", HC(5, (0.15, -0.55, 0.9), (0.38, -0.13, 0.78), 40, (0.25, -0.42, 0.86), (0.38, -0.13, 0.78), 46), "night", fill=1.4, hand=0.003, note="she locks")
ring("L48.1", on=False)
tags_big("L48.1", [2, 3, 4, 5, 6, 8, 9, 10, 11, 12])
S("L48.1", K_(PORCH, [0, 0, 1.0], 12, [PORCH[0] - 0.2, PORCH[1] - 0.2, PORCH[2]], [0, 0, 1.0], 12.5), "night", hand=0.0, fill=1.2, note="TEN tags glowing, big")
tags("L48.2", [2, 3, 4, 5, 6, 8, 9, 10, 11, 12])
ring("L48.2", k=11, turn=(0, 70), dur=0.5)
S("L48.2", HC(11, (0.6, -0.5, 0.9), (0.38, -0.13, 0.78), 40, (0.5, -0.4, 0.84), (0.38, -0.13, 0.78), 46), "night", fill=1.4, hand=0.003, note="with their own keys")
# --- S49 her door, open a crack, warm light
ring("L49", on=False)
door("L49", 1, 0, 14, 0.5)
walk(ME, "L49", front(1, 6.0, 0.0), "L49.3", front(1, 2.0, 0.0), yaw=yawf(1), expr="asleep", arms=[22, 22])
S("L49", K_(PORCH, [-4, -1, 1.0], 18, PORCH, [-6, -4, 1.0], 22), "night", hand=0.0, fill=1.2, note="the only one I can open")
S("L49.3", HC(1, (0.5, -1.6, 1.3), (0.2, 0, 1.1), 30, (0.35, -1.2, 1.3), (0.15, 0, 1.1), 36), "night", fill=0.8, note="is hers, a crack, warm light")
# --- S49a my own door from inside: my sleeping hand on the brass thumb-turn, turning it open
THUMB = [RX + 0.7, RY + 2.805, 1.1]
room("L49a", ["door_b"])
put(ME, "L49a", [RX - 0.3, RY + 1.0, 0.0], 180, "asleep", arms=[0, 70])
S("L49a", FC([RX - 0.3, RY + 1.0], 180, 2.9, -55, 4, 36, 1.45, 1.45, d2=2.5), "intn", hand=0.002, fill=1.3, rkey=1.0, note="me, asleep, at my own door")
hand("L49a.2", pos=THUMB, yaw=0, a0=0, a1=0, dur=0.5)
S("L49a.2", K_([RX + 1.7, RY + 1.5, 1.4], [RX + 0.7, RY + 2.75, 1.1], 40, [RX + 1.5, RY + 1.7, 1.35], [RX + 0.7, RY + 2.75, 1.1], 44), "intn", hand=0.002, fill=1.2, rkey=1.0, note="my hand on the brass thumb-turn")
hand("L49a.5", pos=THUMB, yaw=0, a0=0, a1=90, dur=0.9)
S("L49a.5", K_([RX + 1.6, RY + 1.9, 1.3], [RX + 0.7, RY + 2.75, 1.1], 44, [RX + 1.4, RY + 2.1, 1.25], [RX + 0.7, RY + 2.75, 1.1], 50), "intn", hand=0.002, fill=1.2, rkey=1.0, note="I just TURN it")
# --- S50 Thursday
hand("L50", on=False)
door("L50", 1, 14, 0, 0.5)
clock("L50", "12:04", 4)
gone(ME, "L50")
gone(LOU, "L50")
S("L50", K_(PORCH, [0, 0, 1.0], 13), "night", hand=0.0, fill=1.2, note="Thursday, 12:04")
S("L50.1", K_(PORCH, [-2, 0, 1.0], 17, PORCH, [-3, 0, 1.0], 18), "night", hand=0.0, fill=1.2, note="the worst")
# --- S51 Lou's knee
put(LOU, "L51", front(2, 3.0, 0.0), yawc(2) + 40, "worried", lean=10, arms=[0, 0])
S("L51", FC(front(2, 3.0, 0.0), yawc(2) + 40, 3.6, 25, 4, 30, 1.1, 1.1, d2=3.1), "night", fill=1.8, note="her knee, slow")
S("L51.2", FC(front(2, 3.0, 0.0), yawc(2) + 40, 2.9, 20, 4, 36, 1.3, 1.3, d2=2.5), "night", fill=2.0, note="she was slow")
# --- S52 me at Mr. Park's door first
put(ME, "L52", front(3, 3.0, 0.0), yawf(3), "asleep", arms=[22, 22])
raw(ME, "L52.1", pos=front(3, 1.4, 0.0))
S("L52", FC(front(3, 2.2, 0.0), yawf(3), 3.4, 60, 4, 36, 1.4, 1.4, d2=3.1), "night", fill=1.4, note="me first")
S("L52.1", FC(front(3, 1.6, 0.0), yawf(3), 3.4, 80, 4, 36, 1.4, 1.4, d2=3.0), "night", fill=1.4, note="at Mr. Park's door")
S("L52.3", FC(front(3, 1.4, 0.0), yawf(3), 3.2, -75, 4, 36, 1.4, 1.4, d2=2.8), "night", fill=1.4, note="first")
# --- S53 his handle starts to turn
S("L53", FC(front(3, 1.4, 0.0), yawf(3), 2.2, 160, 6, 30, 1.2, 1.3, d2=1.8), "night", fill=1.5, note="I watched myself")
hand("L53.1", k=3, shake=0.0, a0=0, a1=35, dur=0.8)
S("L53.1", HC(3, (0.8, -0.6, 1.2), (0.38, -0.15, 1.0), 40, (0.65, -0.5, 1.1), (0.38, -0.15, 1.0), 46), "night", fill=1.4, hand=0.003, note="the handle starts to turn")
# --- S54 her key turns with a second to spare
hand("L54", on=False)
ring("L54", k=3, turn=(0, 75), dur=0.5)
S("L54", HC(3, (0.1, -0.55, 0.9), (0.38, -0.13, 0.78), 40, (0.2, -0.42, 0.86), (0.38, -0.13, 0.78), 46), "night", fill=1.4, hand=0.003, note="she turns the key")
ring("L54.2", on=False)
hand("L54.2", k=3, shake=0.0, a0=35, a1=0, dur=0.3)
S("L54.2", HC(3, (0.8, -0.6, 1.2), (0.38, -0.15, 1.0), 40, (0.65, -0.5, 1.1), (0.38, -0.15, 1.0), 46), "night", fill=1.4, hand=0.003, note="the handle stops")
hand("L54.3", on=False)
put(LOU, "L54.3", front(3, 2.0, 1.0), yawf(3), "worried", lean=8)
S("L54.3", W(front(3, 1.2, 0.5), 4.2, 35, 6, 28, h=1.2, d2=3.4), "night", fill=1.3, note="one second to spare")
# --- S55 her door opens for me
put(ME, "L55", front(1, 2.0, 0.4), yawf(1), "asleep", arms=[22, 22])
gone(LOU, "L55")
S("L55", K_(PORCH, [-5.0, -2.0, 1.0], 16, PORCH, [-6.0, -3.0, 1.0], 18), "night", hand=0.0, fill=1.3, note="on the video")
raw(ME, "L55.1", pos=front(1, 1.4, 0.4))
hand("L55.1", k=1, shake=0.3, lz=1.0)
S("L55.1", HC(1, (0.8, -0.6, 1.2), (0.38, -0.17, 1.0), 40, (0.65, -0.5, 1.1), (0.38, -0.17, 1.0), 46), "night", fill=1.4, hand=0.003, note="I try her handle")
hand("L55.3", on=False)
door("L55.3", 1, 0, 75, 0.6)
S("L55.3", HC(1, (0.9, -2.6, 1.5), (0.0, 0.0, 1.2), 24, (0.7, -2.0, 1.4), (0.0, 0.0, 1.2), 26), "night", fill=1.0, note="it OPENS")
# --- S56 inside number one, Lou with a blanket
gone(ME, "L56")
door("L56", 1, 75, 75, 0.1)
room("L56", ["lamp", "window"])
cue("L56", "blanket", on=True)
put(LOU, "L56", [RX + 1.4, RY + 0.4, 0.0], 270, "soft", arms=[40, 40])
S("L56", K_([RX - 0.7, RY - 1.1, 1.6], [RX + 1.4, RY + 0.4, 1.4], 28, [RX - 0.4, RY - 0.8, 1.55], [RX + 1.4, RY + 0.4, 1.4], 30), "intn", hand=0.004, rkey=0.8, note="Lou waiting with a blanket")
S("L56.1", FC([RX + 1.4, RY + 0.4], 270, 3.0, 25, 3, 36, 1.3, 1.3, d2=2.6), "intn", hand=0.004, rkey=0.9, note="a blanket")
# --- S57 dawn: she walks me back
cue("L57", "blanket", on=False)
door("L57", 1, 0, 0, 0.1)
_m0, _m1 = front(1, 2.5, 0.0), front(7, 1.6, 0.0)
walk(ME, "L57", _m0, "L58", _m1, yaw=None, expr="asleep", arms=[22, 22])
walk(LOU, "L57", [_m0[0] + 0.9, _m0[1] + 0.5, 0.0], "L58", [_m1[0] + 0.9, _m1[1] + 0.1, 0.0], yaw=None, expr="soft", arms=[0, 80])
S("L57", K_([0.2, 2.9, 1.55], [0.55, 0.2, 1.3], 15, [0.2, 2.6, 1.5], [0.55, 0.2, 1.3], 16), "dawn", note="before sunrise, she walks me back")["follow"] = "me"
S("L57.1", K_([0.0, 2.5, 1.5], [0.55, 0.2, 1.3], 15, [0.1, 2.2, 1.45], [0.55, 0.2, 1.3], 16), "dawn", note="her arm round my shoulders")["follow"] = "me"
S("L57.3", K_([0.1, 1.9, 1.5], [0.55, 0.15, 1.3], 14, [0.2, 1.7, 1.45], [0.55, 0.15, 1.3], 15), "dawn", note="to number SEVEN")["follow"] = "me"
# --- S58 my door locks with her key; tag 7 glows
door("L58", 7, 80, 0, 0.7)
gone(ME, "L58")
put(LOU, "L58", front(7, 1.0, 0.7), yawf(7), "soft", arms=[0, 0])
S("L58", HC(7, (1.6, -2.6, 1.6), (0.0, 0.0, 1.2), 26, (1.2, -2.1, 1.5), (0.0, 0.0, 1.2), 28), "dawn", note="and locks my door behind me")
ring("L58.3", k=7, turn=(0, 75), dur=0.5)
tags("L58.3", [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12])
S("L58.3", HC(7, (0.1, -0.55, 0.9), (0.38, -0.13, 0.78), 40, (0.2, -0.42, 0.86), (0.38, -0.13, 0.78), 46), "dawn", fill=1.3, hand=0.003, note="with HER key, tag 7 glows")
# --- S58a then she unlocks the other ten, the tags fade
ring("L58a", on=False)
walk(LOU, "L58a", front(6, 2.6, 0.0), "L58a.1", front(5, 2.6, 0.0), yaw=yawf(6), expr="neutral", run=True)
raw(LOU, "L58a.3", pos=front(4, 1.2, 0.0), run=True)
raw(LOU, "L59-0.3", pos=front(3, 1.2, 0.0), run=True)
S("L58a", K_(PORCH, [0, 0, 1.0], 13, [PORCH[0] - 0.2, PORCH[1], PORCH[2]], [0, 0, 1.0], 14), "dawn", hand=0.0, fill=1.0, note="she goes round again")
ring("L58a.1", k=5, turn=(70, 0), dur=0.5)
for i, n in enumerate([12, 11, 10, 9, 8, 7, 6, 5, 4, 3]):
    tags(f"L58a+{0.35 + i * 0.28:.2f}", [x for x in range(2, 13) if x not in [12, 11, 10, 9, 8, 7, 6, 5, 4, 3][:i + 1]])
S("L58a.1", HC(5, (0.15, -0.55, 0.9), (0.38, -0.13, 0.78), 40, (0.25, -0.42, 0.86), (0.38, -0.13, 0.78), 46), "dawn", fill=1.3, hand=0.003, note="unlocking the other ten")
ring("L58a.3", on=False)
S("L58a.3", K_([2, -12, 3.0], [-1, 2, 1.5], 16, [1, -11, 2.5], [-1, 2, 1.5], 18), "dawn", hand=0.0, note="before anyone wakes")
tags("L59", [])
# --- S59 the ring's tag 7
gone(LOU, "L59")
ring("L59", pos=RP, yaw=-ang(1), hand=True)
S("L59", K_([RP[0], RP[1] - 0.3, RP[2] - 0.2], [RP[0], RP[1] - 0.08, RP[2] - 0.2], 40, [RP[0], RP[1] - 0.22, RP[2] - 0.2], [RP[0], RP[1] - 0.08, RP[2] - 0.2], 40), "dawn", fill=1.3, hand=0.002, note="that's why she has one")
# --- S60 Lou at her kitchen table at dawn
ring("L60", pos=[RX - 0.2, RY + 0.1, 0.78], yaw=0, tilt=90, hand=False)
room("L60", ["kitchen", "window"])
put(LOU, "L60", [RX - 0.2, RY + 0.95, 0.0], 0, "worried", head=[0, 10])
S("L60", FC([RX - 0.2, RY + 0.95], 0, 2.2, 15, 4, 34, 1.3, 1.3, d2=1.7), "int", hand=0.004, note="Aunt Lou, tired, a mug, the ring")
ring("L60.2", pos=[RX - 0.2, RY + 0.1, 0.8], yaw=0, tilt=90, hand=False)
S("L60.2", K_([RX - 0.2, RY - 0.9, 1.5], [RX - 0.2, RY + 0.1, 0.8], 36, [RX - 0.2, RY - 0.6, 1.3], [RX - 0.2, RY + 0.1, 0.8], 40), "int", hand=0.003, note="the ring beside it")
ring("L60.3", on=False)
S("L60.3", FC([RX - 0.2, RY + 0.95], 0, 1.5, -20, 3, 40, 1.4, 1.35, d2=1.2), "int", note="she didn't want me scared")
gone(LOU, "L60.4")
put(ME, "L60.4", front(7, 2.8, 0.0), yawc(7), "worried")
S("L60.4", FC(front(7, 2.8, 0.0), yawc(7), 2.4, 15, 4, 34, 1.5, 1.5, d2=1.9), "dawn", note="in my own place")
# --- S61 me at my table, phone down, soft
gone(ME, "L61")
put(ME, "L61", [RX - 0.3, RY - 0.4, 0.0], 150, "soft", arms=[0, 0], head=[0, 5])
room("L61", ["kitchen"])
S("L61", FC([RX - 0.3, RY - 0.4], 150, 2.0, 18, 3, 36, 1.5, 1.45, d2=1.5), "int", note="me at my table, phone down")
S("L61.3", FC([RX - 0.3, RY - 0.4], 150, 1.4, -10, 3, 40, 1.55, 1.55, d2=1.1), "int", note="what I was looking for")
# --- S62 her spare room: my old lamp and bed
gone(ME, "L62")
room("L62", ["bed", "lamp", "window"], bed_yaw=0)
S("L62", K_([RX + 0.2, RY - 2.4, 1.7], [RX + 2.3, RY + 1.6, 0.8], 24, [RX + 0.6, RY - 2.0, 1.6], [RX + 2.4, RY + 1.6, 0.8], 26), "int", note="my old room")
# --- S63 Sunday: carrying the bed across the court
room("L63", [])
cue("L63", "bed", on=True, pos=[-3.0, -6.0, 0.9], to=[1.2, -4.0, 0.9], yaw=90, dur=2.0)
walk(ME, "L63", [-4.5, -6.0, 0.0], "L64", [-0.3, -4.0, 0.0], yaw=None, expr="neutral", arms=[40, 40])
walk(LOU, "L63", [-1.7, -6.0, 0.0], "L64", [2.5, -4.0, 0.0], yaw=None, expr="neutral", arms=[40, 40])
S("L63", W([-1.5, -5.6], 6.0, 100, 6, 28, h=1.2, d2=5.0), "day", note="Sunday, we carry it")
S("L63.1", W([0.2, -4.7], 4.6, 105, 5, 28, h=1.2, d2=3.9), "day", note="we carried it")
S("L63.2", W([1.4, -4.1], 4.4, 100, 5, 28, h=1.25, d2=3.7), "day", note="across the COURT, past the fountain")
# --- S64 my old lamp, my squeaky bed
cue("L64", "bed", on=False)
gone(LOU, "L64")
gone(ME, "L64")
room("L64", ["lamp", "bed", "window"], bed_yaw=0)
S("L64", K_([RX + 0.5, RY - 0.8, 1.5], [RX + 2.9, RY + 2.3, 0.9], 30, [RX + 0.9, RY - 0.4, 1.4], [RX + 2.9, RY + 2.3, 0.9], 34), "int", rkey=0.7, note="my old lamp")
put(ME, "L64.1", [RX + 1.9, RY + 1.0, 0.45], 0, "smile")
raw(ME, "L64.1", pos=[RX + 1.9, RY + 1.0, 0.45])
raw(ME, "L65", pos=[RX + 1.9, RY + 1.0, 0.4])
S("L64.1", K_([RX + 0.3, RY - 2.5, 1.7], [RX + 1.9, RY + 1.0, 1.15], 25, [RX + 0.7, RY - 2.2, 1.65], [RX + 1.9, RY + 1.0, 1.2], 27), "int", note="my squeaky old bed")
# --- S65 - S67 that night, on a camera on my shelf
clock("L65", "12:04")
put(ME, "L65", [RX + 1.9, RY + 0.3, 0.7], 0, "asleep", lean=-90)
raw(ME, "L65.2", lean=-20, blend=0.9)
S("L65", K_([RX - 0.6, RY - 1.2, 2.3], [RX + 1.9, RY + 1.3, 0.6], 22, [RX - 0.3, RY - 1.0, 2.2], [RX + 1.9, RY + 1.3, 0.6], 24), "intn", hand=0.0, rkey=0.8, note="that night, on my shelf camera")
S("L65.2", K_([RX - 0.2, RY - 2.2, 2.4], [RX + 1.9, RY + 1.2, 1.25], 24, [RX + 0.1, RY - 2.0, 2.3], [RX + 1.9, RY + 1.2, 1.3], 26), "intn", hand=0.0, rkey=0.8, note="I sit up at twelve oh-four")
raw(ME, "L66", head=[60, 0], blend=0.7)
raw(ME, "L66.1", lean=-90, head=[0, 0], blend=0.9)
S("L66", FC([RX + 1.9, RY + 0.85], 0, 2.6, 30, 12, 30, 1.2, 1.1, d2=2.0), "intn", hand=0.0, rkey=0.8, note="look around")
S("L66.1", K_([RX + 0.9, RY - 1.2, 1.9], [RX + 1.9, RY + 1.3, 0.6], 26, [RX + 1.2, RY - 1.0, 1.8], [RX + 1.9, RY + 1.3, 0.6], 28), "intn", hand=0.0, rkey=0.8, note="and lie back down")
S("L67", K_([RX + 0.6, RY + 0.4, 1.7], [RX + 1.5, RY + 1.65, 1.0], 24, [RX + 0.8, RY + 0.5, 1.6], [RX + 1.5, RY + 1.65, 1.0], 26), "intn", hand=0.002, rkey=0.8, note="already HOME: my sleeping face, calm")
# --- S68 11:58, the court locks its own doors
clock("L68", "11:58")
gone(ME, "L68")
room("L68", [])
put(PARK, "L68", front(3, 1.0, 0.7), yawc(3), "neutral")
door("L68", 3, 80, 0, 0.5)
S("L68", FC(front(3, 1.0, 0.7), yawc(3), 2.3, 20, 4, 34, 1.5, 1.5, d2=1.8), "night", fill=1.3, note="Mr. Park, his own door")
put(HAD, "L68.1", front(9, 1.0, 0.0), yawc(9), "neutral", arms=[40, 0])
ring("L68.1", k=9, turn=(0, 75), dur=0.5, hand=False)
S("L68.1", FC(front(9, 1.0, 0.0), yawc(9), 2.0, -25, 4, 34, 1.45, 1.4, d2=1.6), "night", fill=1.3, note="Mrs. Haddad, her own key")
ring("L68.3", on=False)
clock("L68.3", None)
S("L68.3", K_([-3, -14, 4.5], [1, 3, 1.5], 14, [-2, -13, 4.0], [1, 3, 1.5], 15), "night", hand=0.0, note="the whole court")
# --- S69 the neighbours wave at her window
put(PARK, "L69", front(1, 5.0, 0.0), yawc(1), "smile", arms=[0, 150])
put(HAD, "L69", front(1, 4.6, -0.9), yawc(1), "smile", arms=[0, 150])
S("L69", HC(1, (-0.2, -7.4, 1.2), (-0.2, -4.5, 2.3), 23, (-0.2, -7.0, 1.2), (-0.2, -4.5, 2.3), 25), "dawn", note="and waves at her lit window")
room("L69.1", ["window", "lamp"])
put(LOU, "L69.1", [RX - 2.4, RY + 0.8, 0.0], 300, "laugh", head=[40, 0])
S("L69.1", FC([RX - 2.4, RY + 0.8], 300, 3.0, 60, 4, 34, 1.45, 1.45, d2=2.6), "int", fill=1.2, note="at her window, laughing")
gone(PARK, "L69.1")
gone(HAD, "L69.1")
# --- S70 she still does her rounds
walk(LOU, "L70", front(5, 1.2, -0.6), "L70.1", front(5, 3.2, 0.2), yaw=None, expr="soft")
put(LOU, "L70.2", front(6, 1.4, 0.0), yawc(6) + 20, "soft")
tags("L70", [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12])
S("L70", HC(5, (0.2, -6.8, 1.5), (0.0, -1.0, 1.2), 30, (0.2, -6.2, 1.5), (0.0, -1.2, 1.2), 32), "dusk", fill=1.4, note="she still does her rounds")
S("L70.1", HC(5, (1.6, -6.2, 1.4), (0.3, -2.6, 1.2), 32, (1.2, -5.6, 1.4), (0.3, -2.6, 1.2), 34), "dusk", fill=1.4, note="old habit")
S("L70.2", FC(front(6, 1.4, 0.0), yawc(6) + 20, 2.4, 15, 4, 36, 1.35, 1.35, d2=2.0), "dusk", fill=1.5, note="her face, soft")
# --- S71 me on my step, then the ring close: the loop
tags("L71", [])
gone(LOU, "L71")
put(ME, "L71", front(7, 1.2, 0.0), yawc(7), "smile")
S("L71", FC(front(7, 1.2, 0.0), yawc(7), 2.3, 18, 4, 34, 1.55, 1.55, d2=1.8), "dusk", note="me on my step")
S("L71.2", FC(front(7, 1.2, 0.0), yawc(7), 1.5, -15, 3, 40, 1.58, 1.58, d2=1.2), "dusk", note="I tell them")
gone(ME, "L71.3")
ring("L71.3", k=4, lz=1.3, turn=(0, 0), dur=1.0, hand=False, scale=2.3)
put(LOU, "L71.3", LOU_AT, LOU_YAW, "brisk", arms=[72, 72], head=LOU_HEAD)
S("L71.3", HC(4, (-0.1, -2.1, 1.45), (0.58, -0.3, 1.3), 28, (0.05, -1.8, 1.42), (0.56, -0.3, 1.3), 32), "dusk", fill=1.6, hand=0.003, note="the hook again: Lou, the ring, the key")


# ---------------------------------------------------------------------------------------------------- story
look = {"fog": "#bcd8ee", "fog_density": 0.0, "fog_start": 40.0, "sky": "#8fd0ff", "exposure": 0.0, "flash_safe": True,
        "style": "closer",
        "polish": {"emph": ["L01", "L05", "L19", "L39", "L43", "L45", "L67"], "reveal": ["L39", "L43"], "twist": "L39",
                   "quiet": [["L60", "L61"]], "sway": [], "camera": True, "idle": True, "ease": True, "hold": []}}
story = {
    "slug": "ep86-aunts-keys",
    "title": "Aunt Lou Has A Key To YOURS \U0001F511",
    "made_for_kids": False,
    "premise": "My aunt Lou, the locksmith of our court of twelve houses, has a key to every one of them. For a month every "
               "door has clicked at midnight and again before sunrise, and the neighbors think she lets herself in. I "
               "moved into number seven last month and never gave her a key. She has one anyway, and my sneakers are "
               "wet every morning, so I put a camera on my porch.",
    "twist": "The thing that walks the court at midnight trying every handle is me, asleep, sleepwalking back to my old "
             "room at Aunt Lou's. She locks ten doors every night so the only handle I can open is hers, then walks me "
             "home and locks my door behind me. We carry my old bed and lamp across the court, and I stop walking.",
    "world": "a closed court of twelve narrow red-brick houses in a horseshoe round a teal-lit stone fountain, ivy, iron "
             "lamps, brass handles and numeral plates, a locksmith's key shop window, and a porch camera's night footage",
    "voice": {"voice": "am_adam", "tempo": 1.03, "rate": 1.45},
    "asr_forgive": ["twelve oh one", "twelve oh four", "in", "eyes", "walked"],
    "key_color": BRASS,
    "phonemes": {"walked": "wˈɔkt", "Eyes": "ˈIz", "eyes": "ˈIz", "their": "ðˈɛɹ"},
    "gap": 0.15,
    "tail": LOOP,
    "min_read": 0.15,
    "fade_in": False,
    "fade_out": False,
    "look": look,
    "grade": {"shadows": [-0.01, 0.0, 0.04], "highlights": [0.03, 0.01, -0.02], "saturation": 1.12, "contrast": 1.05,
              "vignette": 0.18, "bloom": 0.2, "grain": 0.008, "red_line": 0.7},
    "cast": cast,
    "lines": lines,
    "shots": shots,
    "acting": acting,
    "cues": cues,
    "rev": 3,
    "music": {"root": 48, "mode": "minor", "bpm": 104, "seed": 86,
              "sections": [
                  {"at": 0, "voices": ["pluck", "pulse", "pad"], "energy": 0.5},
                  {"at": "L27", "voices": ["pluck", "pulse", "pad"], "energy": 0.8},
                  {"at": "L33", "voices": ["drone", "pad"], "energy": 0.55},
                  {"at": "L55", "voices": ["pad", "drone"], "energy": 0.4, "mode": "major"},
                  {"at": "L61", "voices": ["pluck", "pad", "pulse"], "energy": 0.45, "mode": "major"},
                  {"at": "L70", "voices": ["pad", "pluck"], "energy": 0.25, "mode": "major"},
              ]},
    "sound": {
        "rev": 3, "floor": "stone", "steps_db": -22,
        "ambience": [{"kind": "crickets", "from": "L27", "to": "L55", "lufs": -40},
                     {"kind": "water", "from": "L44", "to": "L59", "lufs": -44}],
        "sfx": [
            {"at": "L01.4", "kind": "hit", "db": -9},
            {"at": "L05", "kind": "click", "db": -20},
            {"at": "L34+0.2", "kind": "creak", "db": -16, "dur": 1.0},
            {"at": "L36.1", "kind": "knock", "db": -24, "pattern": [0, 0.12], "tone": "soft"},
            {"at": "L54.2+0.4", "kind": "click", "db": -14},
            {"at": "L33", "kind": "riser", "db": -16, "dur": 0.8},
        ],
        "music_drops": [{"from": "L26>", "to": "P01>", "db": -60}, {"from": "L33>", "to": "P02>", "db": -60}],
    },
}
from blocky import timeline

try:
    voice = json.loads((HERE.parent / "voice-timings.json").read_text())
    _tl0 = timeline.build({"name": "ep86-aunts-keys", "lines": lines, "shots": [{"id": "S0"}], "gap": 0.15, "tail": LOOP,
                           "min_read": 0.15, "cast": cast}, voice)
    AT = timeline.resolver(_tl0["lines"], _tl0["duration"])
    for k in acting:
        acting[k].sort(key=lambda e: AT(e["at"]))
    cues.sort(key=lambda e: AT(e["at"]))
except (SystemExit, FileNotFoundError, KeyError) as e:
    print("sort skipped (voice timings stale):", e)
OUT.write_text(json.dumps(story, indent=1, ensure_ascii=False) + "\n")
print(f"{len(shots)} shots, {len(cues)} cues")
