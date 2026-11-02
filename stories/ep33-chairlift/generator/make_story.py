"""Writes ../story.json for ep33 "chairlift" (script.md, writer 2026-11-02).

Run from anywhere: python stories/ep33-chairlift/generator/make_story.py
The words are in lines.json next to this file (every line of the script, exactly). Everything else is here: the cast,
the shots and their cameras, the acting, the cues set.py reads, the effects, the score and the sound.

Places (geometry.py is shared with set.py): the line runs up +y from the bottom wheel at the origin to the top wheel at
y = 128; the up rope is at x = +1.8, the down rope at x = -1.8. A rider is keyed by where its feet-root is, so every
ride is a few `pos` keys that geometry.rider() works out. Shots that ride use "follow": "me" and their positions are
metres from my feet-root; I face +y on the up line, so my left is -x, the Four-Face's seat is 1.44 m to my left
(x - 1.44, y - 0.1) and the footrest centre is at (-0.72, +0.60, +0.17) from my feet.
"""
import json
import math
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import geometry as G  # noqa: E402

OUT = HERE.parent / "story.json"
lines = json.loads((HERE / "lines.json").read_text())

# ---------------------------------------------------------------------------------------------------- holds
# If the voice lands under 2:15 the holds are added in this order, never words: P01 up to 1.0 s, the beat after L21
# (L21's gap), L61's gap, L73's gap. A pause beat P01 is the music_drops hole (0.7 s). The loop tail is 0.3 s.
HOLDS = {"P01": 0.7}
LOOP = 0.3
out_lines = []
for ln in lines:
    out_lines.append(ln)
    if ln["id"] == "L51":
        out_lines.append({"id": "P01", "pause": HOLDS["P01"], "chunks": []})
lines = out_lines
GAPS = {}   # line id -> gap after it
TEMPO = {}  # line id -> tempo
for ln in lines:
    if ln["id"] in GAPS:
        ln["gap"] = GAPS[ln["id"]]
    if ln["id"] in TEMPO:
        ln["tempo"] = TEMPO[ln["id"]]

# ---------------------------------------------------------------------------------------------------- cast
cast = {
    "me": {"age": "adult", "skin": "#f1c9a0", "shirt": "#1f3556", "pattern": "solid", "collar": "#162843",
           "pants": "#3b404c", "shoes": "#4a392c", "sleeves": "long", "hair": "cap", "hair_c": "#5a3b22",
           "hat": "beanie", "hat_c": "#efe3c8",
           "face": {"eyes": "round", "brows": True, "cheeks": "#e98d7a", "ink": "#1b1410"}},
    "bo": {"age": "adult", "skin": "#d8a578", "shirt": "#2f5a3a", "pattern": "knit", "pattern_c": "#264a30",
           "collar": "#244a2f", "pants": "#3b3a38", "shoes": "#2b241e", "sleeves": "long", "hair": "cap",
           "hair_c": "#141414", "hat": "beanie", "hat_c": "#2b2b30", "width": 1.08,
           "face": {"eyes": "round", "brows": True, "ink": "#1a120e"}},
    "mr_halvor": {"age": "adult", "skin": "#e3b896", "shirt": "#6a4a2e", "pattern": "solid", "collar": "#583c24",
                  "pants": "#45454a", "shoes": "#7a3b2a", "sleeves": "long", "hair": "cap", "hair_c": "#f1f0ec",
                  "hat": "none", "height": 1.09,
                  "face": {"eyes": "tired", "brows": True, "ink": "#2a2420"}},
    "mrs_halvor": {"age": "adult", "skin": "#e8c4a4", "shirt": "#d6a73c", "pattern": "knit", "pattern_c": "#b58a2a",
                   "collar": "#3d5f8f", "pants": "#4a4f58", "shoes": "#2c4a35", "sleeves": "long", "hair": "bun",
                   "hair_c": "#a9a8a6", "hat": "none", "height": 0.93,
                   "face": {"eyes": "lashes", "brows": True, "cheeks": "#e49a8a", "ink": "#2a2420"}},
    "creature": {"age": "adult", "skin": "#c9b48f", "shirt": "#c97c4a", "pattern": "solid", "collar": "#b06b3d",
                 "pants": "#3a3d42", "shoes": "#7b7f84", "sleeves": "long", "hair": "none", "hat": "none",
                 "extras": ["hooddown"],
                 "face": {"eyes": "dot", "brows": False, "ink": "#0e0c0c"}},
}

# ---------------------------------------------------------------------------------------------------- helpers
HEAD = 1.57   # a head centre above the feet-root, standing or seated


def c(*keys):
    return [list(k) for k in keys]


def mv(p0, t0, l0, p1=None, t1=None, l1=None):
    if p1 is None:
        return c([0, p0, t0, l0])
    return c([0, p0, t0, l0], [1, p1, t1 if t1 is not None else t0, l1 if l1 is not None else l0])


def front(hd, yaw, off=0.0, dist=1.0, dz=0.0, lens=32, push=0.0, lens2=None, aim_dz=0.0):
    """A camera in front of a face: hd the face's centre, yaw the way the person faces (0 = -y), off degrees round
    from straight on, dist metres away; push moves it in by that much over the shot."""
    a = math.radians(yaw + off)
    d = (math.sin(a), -math.cos(a))
    p0 = [round(hd[0] + d[0] * dist, 3), round(hd[1] + d[1] * dist, 3), round(hd[2] + dz, 3)]
    tg = [hd[0], hd[1], round(hd[2] + aim_dz, 3)]
    if not push and not lens2:
        return c([0, p0, tg, lens])
    p1 = [round(hd[0] + d[0] * (dist - push), 3), round(hd[1] + d[1] * (dist - push), 3), round(hd[2] + dz, 3)]
    return c([0, p0, tg, lens], [1, p1, tg, lens2 or lens])


def hd(p, dz=HEAD):
    return [p[0], p[1], dz]


def ride_cam(dx, dy, dz, tx, ty, tz, lens, dx2=None, dy2=None, dz2=None, tx2=None, ty2=None, tz2=None, lens2=None):
    """A camera relative to my feet-root (shots with "follow": "me")."""
    k0 = [0, [dx, dy, dz], [tx, ty, tz], lens]
    if dx2 is None and tx2 is None and lens2 is None:
        return [k0]
    k1 = [1, [dx if dx2 is None else dx2, dy if dy2 is None else dy2, dz if dz2 is None else dz2],
          [tx if tx2 is None else tx2, ty if ty2 is None else ty2, tz if tz2 is None else tz2], lens2 or lens]
    return [k0, k1]


def rz(y):
    return G.rope_z(y)


def dzs(y_me, dy):
    """The extra height of a point dy up the line from where I am (the line climbs)."""
    return rz(y_me + dy) - rz(y_me)


# ---------------------------------------------------------------------------------------------------- places
BO = [-0.9, -2.5]
MR = [-2.6, -3.95]
MRS = [-1.45, -3.95]
ME0 = [1.5, -2.4]
ROPEZ = 0.0


def key(at, pos, yaw=None, **kw):
    k = {"at": at, "pos": [round(v, 3) for v in pos]}
    if yaw is not None:
        k["yaw"] = yaw
    k.update(kw)
    return k


def jump(at, frm, to, **kw):
    """A move on a cut: two keys at the same moment, so nobody walks on film."""
    return [{"at": at, "pos": frm}, {"at": at, "pos": to, "blend": 0.0, **kw}]


def seat(at, line, y, s, **kw):
    pos, yaw = G.rider(line, y, s)
    return {"at": at, "pos": pos, "yaw": round(yaw, 2), "sit": True, "seat": s, **kw}


def seat_u(at, u, s, **kw):
    pos, yaw = G.rider_u(u, s)
    return {"at": at, "pos": pos, "yaw": round(yaw, 2), "sit": True, "seat": s, **kw}


def arc(f):
    """The bottom wheel's half turn, f from 0 (the down line) to 1 (the up line)."""
    return G.BOTTOM_ARC + f * G.ARC - (G.TOT if f >= 1 else 0)


def arc_top(f):
    return G.TOP_ARC + f * G.ARC


# ---------------------------------------------------------------------------------------------------- shots
# (at, camera, options). Options: step (1 = drawn on ones), hand (handheld drift), follow (a cast name)
FL = "me"
SH = []


def shot(at, cam, **opt):
    SH.append((at, cam, opt))


# ---- 01 Monday: the bet
BOH = hd(BO)
shot(0, front(BOH, 0, 0, 5.4, 0.0, 36, push=1.5, lens2=40), hand=0.004)
shot("L02", mv((-17, -24, 15), (0, 68, 13), 20, (-15, -22, 15.5), (0, 68, 13), 20.5), hand=0.0)
shot("L03", front(hd(ME0), 180, 18, 3.0, 0.0, 34, push=0.15))
shot("L04", mv((-2.8, -5.4, 1.05), (0.4, -1.3, 1.5), 30, (-2.6, -5.2, 1.05), (0.6, -1.3, 1.5), 30), hand=0.003)
shot("L05", front(hd(ME0), 180, -14, 2.5, 0.0, 34, push=0.1))
shot("L06", mv((0.6, 0.15, 1.5), (-1.2, -3.3, 1.2), 31, (0.5, 0.15, 1.5), (-1.2, -3.3, 1.2), 31))
shot("L07", mv((-2.05, -0.4, 1.5), (-2.05, -3.95, 1.45), 30, (-2.05, -0.55, 1.5), (-2.05, -3.95, 1.45), 31))
shot("L08", mv((-2.0, -6.0, 1.8), (1.8, 16, 6.5), 28, (-2.0, -6.1, 1.8), (1.8, 20, 8.0), 28))
shot("L09", mv((-2.0, -2.0, 0.42), (-2.02, -3.95, 0.3), 22, (-2.0, -2.15, 0.4), (-2.02, -3.95, 0.3), 22), hand=0.002)
shot("L10", front(hd(BO), 0, 22, 2.6, 0.0, 32, aim_dz=0.0))
shot("L11", front(hd(MRS, 1.47), 180, -10, 2.7, 0.0, 34, push=0.1))
shot("L11.1", front(hd([1.5, -2.3]), 180, 14, 2.6, 0.0, 34))
shot("L12", mv((-0.5, -4.9, 0.55), (1.2, -1.0, 1.0), 28, (-0.3, -4.7, 0.6), (1.4, -0.9, 1.0), 28), hand=0.003)
shot("L13", mv((0.75, -1.1, 1.05), (1.15, 0.0, 0.6), 24, (0.8, -1.0, 1.0), (1.15, 0.0, 0.6), 25), hand=0.002)
shot("L14", mv((-0.9, -2.7, 1.45), (0.8, -0.1, 1.0), 26, (-0.8, -2.6, 1.45), (0.8, -0.1, 1.0), 27))
# the lore plant: top-down on the footrest between my boots, the two orange strokes centred, held the whole line
shot("L15", ride_cam(-0.72, 0.42, 1.42, -0.72, 0.60, 0.17, 24), follow=FL, hand=0.0)
shot("L16", ride_cam(0.8, 1.0, 1.3, -4.6, 1.8, 0.8, 40), follow=FL, hand=0.004)
shot("L17", ride_cam(0.1, 2.5, 1.6, 0.0, 0.0, HEAD, 34), follow=FL, hand=0.004)
Y18 = 24.0
shot("L18", ride_cam(-0.2, 0.2, 1.7, -2.6, 96.0, 34.0, 80), follow=FL, hand=0.003)
shot("L19", ride_cam(-0.2, 0.2, 1.7, -3.2, 88.0, 31.0, 150), follow=FL, hand=0.003)
shot("L20", ride_cam(-0.2, 0.2, 1.7, -3.4, 80.0, 28.0, 220), follow=FL, hand=0.002)
shot("L21", ride_cam(1.0, -3.3, 1.95, -1.5, 90.0, 24.0, 38, 1.0, -3.2, 1.95, -1.5, 90.0, 27.0, 38), follow=FL, hand=0.003)

# ---- 02 Tuesday and Wednesday
Y22, Y25 = 36.0, 60.0
shot("L22", ride_cam(0.0, 0.3, 1.7, -2.4, 30.0, 1.7 + dzs(Y22, 30.0), 55), follow=FL, hand=0.003)
shot("L23", ride_cam(0.4, 0.6, 1.7, -3.6, 21.0, 1.67 + dzs(Y22 + 8, 21), 105, tx2=-3.6, ty2=11.0, tz2=1.67 + dzs(Y22 + 12, 11)), follow=FL, hand=0.002)
shot("L23.1", ride_cam(0.5, 0.7, 1.6, -3.6, 9.0, 1.7 + dzs(Y22 + 16, 9), 110, tx2=-3.6, ty2=5.0, tz2=1.7 + dzs(Y22 + 19, 5)), follow=FL, hand=0.002)
shot("L24", ride_cam(0.3, 0.4, 1.68, -3.6, 6.0, 1.67 + dzs(Y22 + 19, 6), 140, tx2=-3.6, ty2=3.0, tz2=1.67 + dzs(Y22 + 21, 3), lens2=150), follow=FL, hand=0.002)
shot("L25", ride_cam(-0.3, 0.3, 1.8, -3.6, 4.0, 1.67 + dzs(Y22 + 21, 4), 60, tx2=-3.6, ty2=-0.6, tz2=1.67, lens2=55), follow=FL, hand=0.003)
shot("L26", ride_cam(0.9, -1.3, 1.9, -3.6, -9.0, 1.67 - dzs(Y25, 9) * 0.9 + 0.2, 70), follow=FL, hand=0.003)
shot("L27", ride_cam(0.6, -0.9, 1.8, -3.6, -13.0, 1.67 - dzs(Y25, 13) * 0.8 + 0.2, 160), follow=FL, hand=0.002)
shot("L28", front(hd(BO), 0, -18, 2.5, 0.0, 32, push=0.1))
shot("L29", front(hd([1.0, -2.3]), 180, -16, 2.5, 0.0, 34))
shot("L30", front(hd(MR, 1.62), 180, 0, 2.2, -0.15, 26, aim_dz=-0.6), hand=0.002)
# Wednesday over the lake: two chairs about to pass; footrests level; I twist round; the side face; the orbit
shot("L31", ride_cam(3.0, -5.0, 2.4, -2.7, 12.0, 0.9, 30), follow=FL, hand=0.004)
shot("L32", ride_cam(-0.3, 1.1, 0.0, -2.0, 0.6, -0.15, 40), follow=FL, hand=0.002)
shot("L33", ride_cam(0.8, 2.0, 1.75, 0.0, 0.0, HEAD, 34), follow=FL, hand=0.004)
shot("L34", ride_cam(1.0, -1.1, 1.9, -3.2, -9.0, 1.4, 90), follow=FL, hand=0.003)
shot("L35", mv((0.0, 0.0, 0.0), (0, 0, 0), 30), follow="creature", hand=0.0)   # replaced below
shot("L36", front(hd([0, 0]), 180, 0, 2.5, 0.0, 34), follow=FL)

# ---- 03 Thursday: ahead
shot("L37", ride_cam(0.9, 0.5, 1.6, -3.6, 10.0, 0.6 + dzs(70, 10), 45), follow=FL, hand=0.004)
shot("L38", ride_cam(0.0, 0.4, 1.8, -0.0, 9.0, 1.57 + dzs(72, 9), 85), follow=FL, hand=0.003)
shot("L39", ride_cam(0.0, 0.4, 1.8, -0.0, 9.0, 1.57 + dzs(80, 9), 150), follow=FL, hand=0.003)
shot("L40", ride_cam(0.0, 0.4, 1.8, -0.0, 9.0, 1.57 + dzs(88, 9), 220), follow=FL, hand=0.002)
shot("L41", ride_cam(0.9, -1.5, 1.7, 0.0, 6.0, 1.9 + dzs(96, 6) * 0.5, 36), follow=FL, hand=0.004)
shot("L42", mv((7.0, 118.0, 41.5), (0.0, 128.0, 43.0), 24, (7.0, 118.0, 41.5), (0.0, 129.0, 42.2), 25), hand=0.002)

# ---- 04 Friday: the fog
shot("L43", mv((-4.0, 36.0, 3.2), (0.0, 0.0, 3.0), 26, (-3.0, 33.0, 3.0), (0.4, 0.0, 3.0), 28), hand=0.004)
shot("L44", mv((0.9, -0.9, 1.1), (1.15, 0.0, 0.6), 24, (0.95, -0.85, 1.05), (1.15, 0.0, 0.6), 25), hand=0.002)
shot("L45", front(hd(BO), 0, 14, 2.4, 0.0, 34, push=0.1))
shot("L46", ride_cam(3.4, -4.2, 1.5, -0.6, 0.0, 1.0, 26), follow=FL, hand=0.004)
shot("L47", ride_cam(0.6, 2.2, 3.0, 0.9, 6.0, 1.5, 30), follow=FL, hand=0.003)
shot("L48", ride_cam(2.4, 4.0, 2.2, -0.7, 0.0, 1.2, 28), follow=FL, hand=0.006)
shot("L49", ride_cam(0.0, 0.2, 1.75, 0.0, 5.0, 1.75, 34), follow=FL, hand=0.006)
shot("L50", ride_cam(-0.7, 3.4, 1.15, -0.7, 0.0, 1.0, 30), follow=FL, hand=0.002)
shot("L51", ride_cam(0.5, 1.9, 1.7, -0.2, 0.0, HEAD, 34), follow=FL, hand=0.003)
shot("P01", ride_cam(0.5, 1.9, 1.7, -0.2, 0.0, HEAD, 34, lens2=36), follow=FL, hand=0.003)
shot("L52", ride_cam(-0.7, 4.0, 1.7, -0.7, 0.0, 1.5, 26), follow=FL, hand=0.003)
# the reveal: from in front, the two of us in one frame, its cube toward me, the glints the brightest thing
shot("L53", ride_cam(-0.85, 3.9, 1.62, -0.85, 0.0, 1.5, 26, lens2=29), follow=FL, hand=0.002)
shot("L54", ride_cam(-0.1, 1.7, 1.2, -0.75, 0.0, 0.95, 40), follow=FL, hand=0.002)
shot("L55", ride_cam(1.0, 0.9, 1.7, -1.44, 0.0, HEAD, 30, lens2=34), follow=FL, hand=0.002)
shot("L56", ride_cam(-0.6, 2.2, 1.7, -0.1, 0.1, HEAD, 34), follow=FL, hand=0.003)
shot("L57", ride_cam(-2.2, -1.9, 1.7, -1.44, -0.1, HEAD, 36, lens2=40), follow=FL, hand=0.002)
shot("L58", ride_cam(-3.1, 1.8, 2.4, -1.44, -0.1, 1.55, 40, lens2=48), follow=FL, hand=0.002)
shot("L59", ride_cam(0.2, 1.4, 1.65, 0.0, 0.0, HEAD, 38), follow=FL, hand=0.003)
shot("L60", mv((-3.5, 52.0, 1.6), (-0.8, 64.0, 10.0), 26), hand=0.003)
shot("L61", mv((-2.6, 112.0, 40.8), (1.6, 125.0, 40.6), 30, (-2.5, 114.0, 40.8), (1.7, 127.0, 40.8), 30), hand=0.003)
shot("L62", mv((3.6, 128.5, 41.4), (1.8, 124.0, 40.9), 26), hand=0.002)
shot("L63", mv((-3.8, 122.5, 41.6), (0.0, 129.0, 40.4), 30, (-3.6, 124.0, 41.6), (0.0, 129.0, 40.4), 30), hand=0.002)

# ---- 05 Saturday: the forfeit
shot("L64", mv((2.4, 1.0, 1.5), (-1.7, -3.7, 1.35), 26, (2.0, 0.6, 1.5), (-1.7, -3.7, 1.35), 26), hand=0.003)
shot("L65", mv((-1.9, -2.0, 0.34), (-2.0, -3.95, 0.3), 20, (-1.9, -2.2, 0.36), (-2.0, -3.95, 0.3), 20), hand=0.002)
shot("L66", mv((-0.3, 0.3, 1.45), (-0.35, -2.4, 1.45), 28))
shot("L67", front(hd([0.2, -2.3]), 180, -22, 2.2, -0.05, 32, push=0.1), hand=0.002)
shot("L68", front([MR[0], MR[1], 1.1], 180, 8, 1.55, 0.05, 28, aim_dz=0.0))
shot("L69", front(hd(MR, 1.62), 180, -14, 2.3, 0.0, 34, push=0.12))
shot("L70", mv((0.8, -5.3, 0.9), (1.6, -0.6, 1.3), 30, (0.9, -5.0, 0.9), (1.6, -0.5, 1.3), 30), hand=0.003)
shot("L71", front(hd([0.45, -1.7]), 90, 22, 2.5, 0.0, 34))
shot("L72", mv((-1.3, 1.8, 1.3), (1.8, 12.0, 5.0), 30, (-1.3, 1.8, 1.3), (1.8, 19.0, 7.0), 30), hand=0.003)
shot("L73", mv((-6.0, 12.0, 4.2), (-1.8, 12.0, 4.0), 30, (-6.0, 12.0, 4.2), (-1.8, 12.0, 4.0), 30), hand=0.003)
shot("L74", mv((1.2, 1.6, 1.55), (1.2, 3.45, 1.15), 30, (1.25, 1.65, 1.55), (1.2, 3.45, 1.15), 31), hand=0.002)
shot("L75", front(hd([1.0, 2.55]), 180, -18, 2.4, 0.0, 34, push=0.1))
shot("L76", front(hd([-0.1, 2.65]), 180, 18, 2.4, 0.0, 34))
shot("L77", front(hd([1.0, 2.55]), 180, -18, 2.4, 0.0, 34))
shot("L77.2", front(hd([-0.1, 2.65]), 180, 20, 2.4, 0.0, 34, push=0.1))
shot("L78", mv((0.0, -2.0, 1.6), (1.8, 38.0, 12.0), 120, (0.0, -2.0, 1.6), (1.8, 40.0, 12.5), 130), hand=0.002)
shot("L79", ride_cam(0.5, 5.2, 1.9, 0.0, 0.0, 1.45, 34), follow="mr_halvor", hand=0.003)
shot("L80", mv((0.5, -1.6, 1.7), (1.8, 46.0, 14.0), 34, (0.5, -1.6, 1.7), (1.8, 50.0, 15.0), 34), hand=0.002)
shot("L81", mv((-16.0, 70.0, 8.0), (1.0, 28.0, 8.0), 24, (-14.0, 70.0, 8.0), (1.0, 28.0, 8.5), 24), hand=0.002)

# ---- the orbit round the cube (L35): follow the creature, four keys
ORB = [(0, (0.0, -2.3, 1.7)), (0.34, (-2.3, 0.0, 1.7)), (0.67, (0.0, 2.3, 1.7)), (1.0, (2.3, 0.0, 1.7))]
orbit_cam = [[u, list(p), [0.0, 0.0, 1.55], 38] for u, p in ORB]
for i, (at, cam, opt) in enumerate(SH):
    if at == "L35":
        SH[i] = (at, orbit_cam, {"follow": "creature", "hand": 0.0})

shots, SID = [], {}
for i, (at, cam, opt) in enumerate(SH):
    sid = f"S{i + 1:02d}"
    s = {"id": sid, "cam": cam, "step": opt.get("step", 2)}
    if i:
        s["at"] = at
    if "hand" in opt:
        s["hand"] = opt["hand"]
    if "follow" in opt:
        s["follow"] = opt["follow"]
    shots.append(s)
    SID[at] = sid

# ---------------------------------------------------------------------------------------------------- acting
class Track:
    """One character's keys, in time order. jump=True moves them on the cut: two keys at one moment."""

    def __init__(self):
        self.keys, self.last = [], None

    def put(self, at, pos, jump=False, **kw):
        pos = [round(v, 3) for v in pos]
        if jump and self.last is not None:
            self.keys.append({"at": at, "pos": self.last})
            self.keys.append({"at": at, "pos": pos, "blend": 0.0, **kw})
        else:
            self.keys.append({"at": at, "pos": pos, **kw})
        self.last = pos
        return self

    def stand(self, at, pos, yaw, jump=False, **kw):
        return self.put(at, pos, jump, yaw=yaw, sit=False, **kw)

    def ride(self, at, line, y, s, jump=False, **kw):
        pos, yaw = G.rider(line, y, s)
        return self.put(at, pos, jump, yaw=round(yaw, 2), sit=True, seat=s, **kw)

    def ride_u(self, at, u, s, jump=False, **kw):
        pos, yaw = G.rider_u(u, s)
        return self.put(at, pos, jump, yaw=round(yaw, 2), sit=True, seat=s, **kw)

    def attr(self, at, **kw):
        self.keys.append({"at": at, **kw})
        return self

    def mouth(self, a, b, amt=0.6):
        self.keys.append({"from": a, "to": b, "mouth": [amt, amt], "flap": True})
        return self


Y22, Y25 = 36.0, 60.0
M_ = Track()
M_.stand(0, ME0, 180, expr="neutral")
M_.attr("L05", expr="smirk")
M_.stand("L06", [-0.6, -2.1], 180, jump=True)
M_.stand("L07", [1.0, -2.4], 180, jump=True)
M_.stand("L11.1", ME0, 180, jump=True, expr="grin")
M_.mouth("L11.1", "L11.2", 0.55)
# Monday: the chair swings round the wheel behind my knees and I'm in it; it stops at the loading point
M_.ride_u("L12", arc(0.62), -1, jump=True, expr="smirk")
M_.ride_u("L13", arc(0.995), -1)
M_.ride("L14>", "up", 0.0, -1)
M_.ride("L15", "up", 3.2, -1, jump=True)
M_.ride("L16", "up", 10.0, -1)
M_.ride("L17", "up", 17.0, -1, expr="worried")
M_.ride("L18", "up", 24.0, -1)
M_.ride("L21", "up", 46.0, -1)
# Tuesday
M_.ride("L22", "up", Y22, -1, jump=True, expr="neutral")
M_.ride("L25.1", "up", Y25, -1)
M_.ride("L27>", "up", Y25 + 8.0, -1)
# Wednesday at the gate, then the lake
M_.stand("L28", ME0, 180, jump=True)
M_.attr("L29", expr="smirk")
M_.ride("L31", "up", 10.0, -1, jump=True, expr="neutral")
M_.ride("L32", "up", 16.0, -1)
M_.ride("L33", "up", 20.0, -1, expr="scared", head=[110, 0])
M_.ride("L34", "up", 24.0, -1)
M_.ride("L35", "up", 28.0, -1, expr="terrified", head=[0, 0])
M_.ride("L36", "up", 32.0, -1)
# Thursday: the creature is the chair right ahead
M_.ride("L37", "up", 68.0, -1, jump=True, expr="worried")
M_.ride("L38", "up", 74.0, -1)
M_.ride("L40", "up", 90.0, -1)
M_.ride("L41", "up", 96.0, -1, expr="terrified")
M_.ride("L41>", "up", 108.0, -1)
# Friday: waiting at the loading point, then halfway up, stopped
M_.ride("L43", "up", 0.0, -1, jump=True, expr="neutral")
M_.ride("L45>", "up", 0.0, -1)
M_.ride("L46", "up", 64.0, -1, jump=True, expr="worried")
M_.ride("L51", "up", 64.0, -1, expr="terrified", look=[0.8, 0.0])
M_.ride("L52", "up", 64.0, -1, look=[0.0, 0.0])
M_.ride("L55", "up", 64.0, -1, head=[-20, 0])
M_.ride("L56", "up", 64.0, -1, head=[0, 0], lean=10)
M_.ride("L57", "up", 64.0, -1, lean=0)
M_.ride("L59", "up", 64.0, -1, expr="squeeze")
M_.ride("L60+0.8", "up", 64.0, -1, expr="terrified")
M_.ride("L60>", "up", 69.0, -1)
M_.ride("L61", "up", 117.0, -1, jump=True, expr="worried")
M_.ride("L61>", "up", 127.0, -1)
# the top deck: I stand and look at the empty seat
M_.stand("L62", [4.2, 126.0, 39.5], 90, jump=True, expr="worried")
# Saturday: the gate, the card, the coffee
M_.stand("L64", [0.25, -2.35], 180, jump=True, expr="soft")
M_.attr("L67", arms=[165, 165])
M_.attr("L68", arms=[0, 0])
M_.stand("L74", [1.0, 2.55], 180, jump=True, expr="soft")
M_.attr("L77", expr="grin")
M_.mouth("L77", "L77.1", 0.6)
M_.attr("L77.2", expr="soft")
M_.stand("L80", [0.7, 0.9], 180, jump=True, expr="soft")

B_ = Track()
B_.stand(0, BO, 0, expr="grin")
B_.attr("L10-0.05", head=[0, 0])
B_.attr("L10", head=[-38, -6])
B_.attr("L11", head=[0, 0])
B_.stand("L12", [0.1, -0.15], 90, jump=True, head=[0, 0])
B_.attr("L13", head=[0, 22])
B_.attr("L14", head=[0, 28])
B_.attr("L15", head=[0, 0])
B_.stand("L28", BO, 0, jump=True, expr="grin")
B_.stand("L43", [0.1, -0.15], 90, jump=True, expr="neutral")
B_.attr("L44", head=[0, 26])
B_.stand("L45", BO, 0, jump=True, expr="neutral", head=[0, 0])
B_.stand("L64", BO, 0, jump=True, expr="grin")
B_.attr("L66", expr="soft")
B_.stand("L71", [0.45, -1.7], 90, jump=True, expr="soft")
B_.stand("L74", [-0.1, 2.65], 180, jump=True, expr="grin")
B_.mouth("L76", "L76>", 0.6)
B_.mouth("L77.2", "L77.2>", 0.6)

MR_ = Track()
MR_.stand(0, MR, 180, expr="neutral")
MR_.attr("L30", head=[0, 38])
MR_.attr("L31", head=[0, 0])
MR_.attr("L69", expr="soft")
MR_.ride_u("L70", arc(0.55), -1, jump=True, expr="soft")
MR_.ride_u("L71", arc(0.99), -1)
MR_.ride("L71>", "up", 0.0, -1)
MR_.ride("L72", "up", 0.0, -1)
MR_.ride("L72+0.8", "up", 6.0, -1)
MR_.ride("L73", "up", 16.0, -1)
MR_.ride("L73>", "up", 24.0, -1)
MR_.ride("L78", "up", 38.0, -1)
MR_.ride("L79", "up", 42.0, -1)
MR_.ride("L80", "up", 46.0, -1)
MR_.ride("end", "up", 51.0, -1)

MRS_ = Track()
MRS_.stand(0, MRS, 180, expr="neutral")
MRS_.attr("L11", expr="grin")
MRS_.mouth("L11", "L11.1", 0.7)
MRS_.attr("L11.1", expr="neutral")
MRS_.ride_u("L70", arc(0.55), 1, jump=True, expr="soft")
MRS_.ride_u("L71", arc(0.99), 1)
MRS_.ride("L71>", "up", 0.0, 1)
MRS_.ride("L72", "up", 0.0, 1)
MRS_.ride("L72+0.8", "up", 6.0, 1)
MRS_.ride("L73", "up", 16.0, 1)
MRS_.ride("L73>", "up", 24.0, 1)
MRS_.ride("L78", "up", 38.0, 1)
MRS_.ride("L79", "up", 42.0, 1)
MRS_.ride("L80", "up", 46.0, 1)
MRS_.ride("end", "up", 51.0, 1)

# the Four-Face. Down chairs face -y; it sits on the side nearer my line (x = -1.08). It is only ever nearer.
C_ = Track()
C_.ride_u(0, arc(0.0), 1, hidden=True)          # a ghost on the wheel, so the chair swings in at L04
C_.ride_u("L04", arc(0.12), 1)
C_.ride_u("L04>", arc(0.9), 1)
C_.ride_u("L05", arc(0.9), 1)
# Monday: far up the line, coming down
C_.ride("L18", "down", 122.0, 1, jump=True, hidden=False)
C_.ride("L20.1", "down", 106.0, 1)
C_.ride("L21", "down", 104.0, 1, hidden=True)
# Tuesday: nearer, passing me below the halfway tower; level with my chair at L25.1
C_.ride("L22", "down", Y22 + 34.0, 1, jump=True, hidden=False)
C_.ride("L23", "down", Y22 + 22.0, 1)
C_.ride("L24", "down", Y22 + 10.0, 1)
C_.ride("L25", "down", Y22 + 4.0, 1)
C_.ride("L25.1", "down", Y25, 1)
C_.ride("L26", "down", Y25 - 8.0, 1)
C_.ride("L27", "down", Y25 - 14.0, 1)
C_.ride("L27>", "down", Y25 - 17.0, 1)
C_.ride("L28", "down", Y25 - 17.0, 1, hidden=True)
# Wednesday: over the lake, passing so close
C_.ride("L31", "down", 26.0, 1, jump=True, hidden=False)
C_.ride("L32", "down", 16.0, 1)
C_.ride("L33", "down", 10.0, 1)
C_.ride("L34", "down", 4.0, 1)
C_.ride("L35", "down", 2.0, 1)
C_.ride("L36", "down", 0.5, 1)
# Thursday: the chair right ahead, going up, its back to me (alone on it, on the side nearer the line)
C_.ride("L37", "up", 77.0, -1, jump=True, hidden=True)
C_.ride("L38", "up", 83.0, -1, hidden=False)
C_.ride("L40", "up", 99.0, -1)
C_.ride("L41", "up", 105.0, -1)
C_.ride("L41>", "up", 117.0, -1)
C_.ride_u("L42", G.TOP_ARC + 0.02 * G.ARC, -1, jump=True, hidden=True)
C_.ride_u("L42>", G.TOP_ARC + 0.85 * G.ARC, -1)
# Friday: beside me on the left, from L53 to L59; a ghost keeps the chair's left seat otherwise
C_.ride("L43", "up", 64.0, 1, jump=True, hidden=True)
C_.ride("L53", "up", 64.0, 1, hidden=False)
C_.ride("L59+0.5", "up", 64.0, 1)
C_.ride("L60", "up", 64.0, 1, hidden=True)
C_.ride("L60>", "up", 69.0, 1)
C_.ride("L61", "up", 117.0, 1, jump=True)
C_.ride("L61>", "up", 127.0, 1)
C_.ride_u("L62", G.TOP_ARC + 0.05 * G.ARC, 1, jump=True)
C_.ride_u("L63", G.TOP_ARC + 0.05 * G.ARC, 1)
C_.ride_u("L63>", G.TOP_ARC + 0.9 * G.ARC, 1)

acting = {"me": M_.keys, "bo": B_.keys, "mr_halvor": MR_.keys, "mrs_halvor": MRS_.keys, "creature": C_.keys}


# ---------------------------------------------------------------------------------------------------- cues
cues = [
    {"at": 0, "name": "light", "look": "pre", "ramp": 0.01},
    {"at": "L15", "name": "light", "look": "pink", "ramp": 9.0},
    {"at": "L21>", "name": "light", "look": "pre", "ramp": 0.01},
    {"at": "L24", "name": "light", "look": "pink", "ramp": 8.0},
    {"at": "L28", "name": "light", "look": "pre", "ramp": 0.01},
    {"at": "L31", "name": "light", "look": "pink", "ramp": 8.0},
    {"at": "L36>", "name": "light", "look": "pre", "ramp": 0.01},
    {"at": "L38", "name": "light", "look": "pink", "ramp": 8.0},
    {"at": "L41", "name": "light", "look": "gold", "ramp": 6.0},
    {"at": "L42>", "name": "light", "look": "pre", "ramp": 0.01},
    {"at": "L43+0.2", "name": "light", "look": "fog", "ramp": 3.0},
    {"at": "L52", "name": "light", "look": "thin", "ramp": 2.0},
    {"at": "L60", "name": "light", "look": "gold", "ramp": 7.0},
    {"at": "L63>", "name": "light", "look": "pink", "ramp": 0.3},
    {"at": "L72", "name": "light", "look": "gold", "ramp": 9.0},
    {"at": 0, "name": "card", "me": True, "mr": False},
    {"at": "L68", "name": "card", "me": False, "mr": True},
    {"at": 0, "name": "cup", "on": False},
    {"at": "L74", "name": "cup", "on": True},
    {"at": 0, "name": "sway", "amp": 1.4, "bias": 0.0, "dur": 0.1},
    {"at": "L47", "name": "sway", "amp": 3.2, "bias": 0.0, "dur": 1.2},
    {"at": "L50", "name": "sway", "amp": 1.4, "bias": -3.6, "dur": 0.9},
    {"at": "L60", "name": "sway", "amp": 1.4, "bias": 0.0, "dur": 1.2},
    {"at": 0, "name": "arm_to", "who": "bo", "to": None},
    {"at": "L13", "name": "arm_to", "who": "bo", "arm": 1, "to": [1.12, -0.02, 0.62]},
    {"at": "L15", "name": "arm_to", "who": "bo", "to": None},
    {"at": "L44", "name": "arm_to", "who": "bo", "arm": 1, "to": [1.12, -0.02, 0.62]},
    {"at": "L45", "name": "arm_to", "who": "bo", "to": None},
]
fx = [
    {"at": "L46", "kind": "shake", "dur": 0.5, "amp": 0.6},
    {"at": "L53", "kind": "punch", "dur": 0.35, "zoom": 1.07},
]

# ---------------------------------------------------------------------------------------------------- sound
sfx = []
# the chair clacks over each tower on the rides, and the wheel's hum is the ambience
for ref in ("L16", "L17+0.5", "L18+0.3", "L19+0.4", "L21", "L23", "L24+0.3", "L38", "L39+0.5", "L40+0.4", "L41+0.4",
            "L72+0.5", "L73+0.3"):
    sfx.append({"at": ref, "kind": "click", "db": -22})
sfx += [
    {"at": "L12", "kind": "whoosh", "db": -22},
    {"at": "L25.1", "kind": "whoosh", "db": -14},
    {"at": "L32", "kind": "whoosh", "db": -16},
    {"at": "L46", "kind": "thud", "db": -12},
    {"at": "L47", "kind": "creak", "db": -18, "dur": 1.6},
    {"at": "L50", "kind": "creak", "db": -14, "dur": 1.2},
    {"at": "P01+0.55", "kind": "hit", "db": -6, "keep": True},
    {"at": "L53-0.04", "kind": "sting", "db": -11, "dur": 2.2, "keep": True},
    {"at": "L60", "kind": "thud", "db": -16},
    {"at": "L72", "kind": "bell", "db": -26},
    {"at": "L81>", "kind": "door", "db": -10},
]

story = {
    "slug": "ep33-chairlift",
    "title": "I paid for both seats so I could ride the chairlift alone",
    "made_for_kids": False,
    "premise": "On a week's holiday I book the first chair of every dawn on an old lakeside chairlift, both seats, so I can ride up alone. A rider in a faded orange cagoule with a cube head and the same face on all four sides rides the lift alone too, a little nearer my chair each day, and on the foggy Friday it is in the seat beside me.",
    "twist": "The bet that I can't ride up alone has never been won. Every summer someone takes it and loses, and the forfeit seat is how an old couple has ridden the first chair for forty years without once buying a pass.",
    "world": "An old two-seat chairlift: a timber station on a plank deck at the water's edge of a still black lake, grey steel towers up a steep pine slope to a bare rocky ridge, pre-dawn blue and sunrise pink, one day of thick lake fog.",
    "voice": {"voice": "am_adam", "tempo": 1.03, "rate": 1.45},
    "key_color": "#ff8fb1",
    "gap": 0.12,
    "tail": LOOP,
    "look": {"fog": "#47597a", "fog_density": 0.010, "fog_start": 12.0, "sky": "#3d5170", "exposure": 0.6},
    "grade": {"shadows": [-0.01, 0.0, 0.05], "highlights": [0.04, 0.012, -0.03], "saturation": 1.0,
              "contrast": 1.06, "vignette": 0.3, "bloom": 0.35, "grain": 0.012},
    "phonemes": {"Halvor": "hˈælvɚ", "Halvors": "hˈælvɚz", "cagoule": "kəɡˈul", "Bo": "bˈO"},
    "cast": cast,
    "lines": lines,
    "shots": shots,
    "acting": acting,
    "cues": cues,
    "fx": fx,
    # E Phrygian at 66 bpm: a slow pad and a low pulse that matches the chair's clack. The pulse stops at L46 with the
    # motor. From L64 the pad lifts to E major at the same tempo with a soft figure (our own synthesis)
    "music": {"root": 40, "mode": "phrygian", "bpm": 66, "seed": 33,
              "sections": [
                  {"at": 0, "voices": ["drone", "pad"], "energy": 0.3},
                  {"at": "L12", "voices": ["drone", "pad", "pulse"], "energy": 0.42},
                  {"at": "L22", "voices": ["drone", "pad", "pulse"], "energy": 0.5},
                  {"at": "L37", "voices": ["drone", "pad", "pulse"], "energy": 0.58},
                  {"at": "L46", "voices": ["drone", "pad"], "energy": 0.32},
                  {"at": "L53", "voices": ["drone", "pad", "choir"], "energy": 0.55},
                  {"at": "L60", "voices": ["pad", "pulse"], "energy": 0.4},
                  {"at": "L64", "mode": "major", "voices": ["pad", "piano"], "energy": 0.5},
                  {"at": "L72", "mode": "major", "voices": ["pad", "piano", "pulse"], "energy": 0.6},
              ]},
    "sound": {"floor": "wood", "steps_db": -90,
              "ambience": [
                  {"kind": "water", "from": 0, "to": "end", "lufs": -36},
                  {"kind": "hum", "from": 0, "to": "L46", "lufs": -38},
                  {"kind": "hum", "from": "L60", "to": "end", "lufs": -38},
                  {"kind": "wind", "from": "L43", "to": "L60", "lufs": -40},
              ],
              "sfx": sfx,
              "music_drops": [{"from": "P01", "to": "L52", "keep": ["hit", "sting"]}]},
}
OUT.write_text(json.dumps(story, indent=1, ensure_ascii=False) + "\n")
print("wrote", OUT, f"({len(shots)} shots)")
