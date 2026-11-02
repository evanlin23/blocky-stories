"""Writes ../story.json for ep30 "Who was standing upside down on the ceiling above my climb?" (script.md, 2026-11-02).

Run from anywhere: python stories/ep30-top-rope/generator/make_story.py
The words are in lines.json next to this file. Everything else is here: the cast, the shots and their cameras, the
acting, the cues set.py reads (the lamps, the Headstander's pose, the rope, the tag), the effects, the score and the
sound. Places are set.py's: the wall is the plane y = 0 (the room is at -y, so the camera mostly looks toward +y), the
top hold is at z 8.35, the roof (the "ceiling") at z 9.8, the anchor at x -0.45 and the auto-belay box at x +0.4.
"""
import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE.parent / "story.json"
lines = json.loads((HERE / "lines.json").read_text())

# a closing hold: nothing added beyond the script's 0.25 s loop tail. Whisper-safe readings (see script: mishear watch)
TEMPO = {"L04": 0.97, "L46": 0.92, "L07": 0.95, "L16": 0.95, "L19": 0.95, "L67": 0.95}
for ln in lines:
    if ln["id"] in TEMPO:
        ln["tempo"] = TEMPO[ln["id"]]

LILAC = "#b9a3d9"
cast = {
    "me": {"age": "adult", "skin": "#f1c9a0", "shirt": "#b9622f", "pattern": "stripes", "pattern_c": "#e3d6b2",
           "collar": "#a2542a", "pants": "#4a5560", "shoes": "#e8dcc0", "sleeves": "short", "hair": "cap",
           "hair_c": "#2a1c14", "hat": "none", "face": {"eyes": "round", "brows": True, "ink": "#161012"}},
    "sam": {"age": "adult", "skin": "#c68f6e", "shirt": "#2f5a3e", "pattern": "solid", "collar": "#294f37",
            "pants": "#6a6e72", "shoes": "#2a2a2a", "sleeves": "long", "hair": "bun", "hair_c": "#a9acb2", "hat": "none",
            "face": {"eyes": "round", "brows": True, "ink": "#161012"}},
}
creature = {"age": "adult", "skin": LILAC, "shirt": LILAC, "pattern": "solid", "pants": "#a692c9", "shoes": "#a692c9",
            "sleeves": "long", "hair": "buzz", "hair_c": "#a692c9", "hat": "none", "height": 1.15,
            "face": {"eyes": "hollow", "brows": False, "ink": "#1c1224", "glow": "#fffdf0"}}


def c(*keys):
    return [list(k) for k in keys]


def still(loc, tgt, lens):
    return c([0, list(loc), list(tgt), lens])


def move(a, b):
    """(loc, tgt, lens) at the start to (loc, tgt, lens) at the end."""
    return c([0, list(a[0]), list(a[1]), a[2]], [1, list(b[0]), list(b[1]), b[2]])


# ---------------------------------------------------------------------------------------------------- shots
# (id, at, camera, step)
SH = []


def shot(sid, at, cam, step=2, **kw):
    SH.append({"id": sid, "at": at, "cam": cam, "step": step, **kw})


shot("S01", 0, move(((0.6, -3.4, 0.9), (-0.1, 0, 7.2), 22), ((0.5, -3.4, 0.9), (-0.1, 0, 7.0), 25)))
shot("S02", "L02", still((0.8, -4.2, 7.2), (0, -0.3, 6.7), 30))
shot("S03", "L03", move(((0.5, -0.7, 9.4), (0, -1.6, 0.3), 26), ((0.3, -0.8, 9.4), (0, -1.6, 0.3), 30)))
shot("S04", "L04", move(((0, -14.2, 2.2), (0, 0, 6.8), 20), ((0, -14.2, 2.4), (0, 0, 6.8), 22)))
shot("S05", "L05", move(((0.4, -4.6, 1.0), (0, 0, 2.0), 22), ((0.4, -4.6, 1.4), (0, -1.0, 9.0), 22)))
shot("S06", "L06", move(((0.8, -1.7, 7.6), (0, -1.5, 9.8), 24), ((0.8, -1.7, 7.6), (0.2, -2.0, 9.8), 28)))
shot("S07", "L07", still((1.2, -4.2, 1.9), (0, -1.3, 1.3), 24))
shot("S08", "L08", still((0.1, -2.4, 8.5), (0.1, -0.2, 8.85), 36))
shot("S09", "L09", move(((0.8, -4.0, 3.0), (0, -0.3, 2.8), 30), ((0.8, -4.0, 3.2), (0, -0.3, 3.0), 30)))
shot("S10", "L10", still((1.5, -3.3, 6.5), (0, -0.3, 6.9), 30), look="memory")
shot("S11", "L11", still((1.5, -2.2, 2.6), (1.9, -3.5, 0.3), 30), look="memory")
shot("S12", "L12", still((2.6, -3.4, 1.3), (0, -1.3, 1.4), 32), look="memory")
shot("S13", "L13", still((4.4, -6.3, 1.5), (4.4, -3.6, 1.3), 36))
shot("S14", "L14", still((-1.2, -4.4, 1.5), (-1.8, -0.5, 1.2), 28))
shot("S15", "L15", still((-2.0, -7.8, 1.6), (-2.0, -4.3, 1.4), 30))
shot("S16", "L16", still((-0.5, -6.0, 1.6), (-0.5, -3.0, 1.35), 34))
shot("S17", "L17", still((0.0, -5.5, 1.5), (0, -3.0, 1.55), 40))
shot("S18", "L18", still((0.5, -1.9, 7.9), (0, -0.2, 8.6), 30))
shot("S19", "L19", still((-0.45, -2.9, 8.58), (-0.45, 0, 8.58), 34))   # the lore plant: held for all of L19
shot("S20", "L20", still((-1.6, -1.0, 7.75), (0, -0.3, 7.95), 40))
shot("S21", "L21", still((-0.2, -0.6, 8.0), (0.15, -2.55, 8.9), 28))
shot("S22", "L22", still((5.4, -2.5, 8.7), (0.15, -2.55, 8.9), 28))
shot("S23", "L23", still((0.4, -0.9, 8.3), (0.15, -2.55, 8.7), 40))
shot("S24", "L24", still((1.8, -1.2, 8.6), (0.15, -2.55, 9.0), 32))
shot("S25", "L25", still((0.15, -0.9, 7.7), (0.15, -2.55, 8.05), 50))
shot("S26", "L26", still((0.15, -0.9, 7.7), (0.15, -2.55, 8.05), 70))
shot("S27", "L27", still((0, -7.5, 5.5), (0, 0, 5.8), 20))
shot("S28", "L28", still((1.8, -4.0, 4.6), (0, -0.3, 4.4), 30))
shot("S29", "L29", still((1.2, -3.6, 1.5), (-0.4, -2.2, 0.4), 28))
shot("S30", "L30", still((1.6, -4.4, 1.6), (0.2, -2.0, 0.9), 22))
shot("S31", "L31", still((0.3, -2.2, 7.6), (0.2, -0.2, 8.8), 34))
shot("S32", "L32", still((0.9, -5.4, 1.6), (0.5, -1.8, 1.3), 28))
shot("S33", "L33", still((-0.2, -0.6, 8.0), (0.15, -1.75, 9.0), 16))
shot("S34", "L34", still((5.4, -1.75, 8.7), (0.15, -1.75, 8.9), 28))
shot("S35", "L35", still((4.2, -7.0, 1.5), (4.4, -4.1, 1.3), 34))
shot("S36", "L36", still((0.0, -7.4, 1.6), (-0.5, -3.5, 1.45), 34))
shot("S37", "L37", still((1.2, -4.2, 1.9), (0, -1.3, 1.3), 24))
shot("S38", "L38", still((-0.3, -5.6, 1.5), (-0.9, -3.3, 1.55), 40))
shot("S38b", "L38.1", still((-0.9, -3.3, 1.6), (0.3, -0.3, 8.8), 60))
shot("S39", "L39", still((-0.9, -5.9, 1.5), (-0.9, -3.3, 1.6), 45))
shot("S40", "L40", still((5.4, -1.05, 8.7), (0.15, -1.05, 8.9), 28))
shot("S41", "L41", still((0.0, -3.6, 0.8), (0.15, -1.0, 9.0), 20))
shot("S42", "L42", still((1.3, -3.0, 4.5), (0, -0.3, 4.9), 30))
shot("S43", "L43", still((-1.6, -3.0, 5.0), (0, -0.3, 4.9), 30))
shot("S44", "L44", still((-0.9, -2.2, 6.2), (-0.5, -0.2, 7.7), 30))
shot("S45", "L45", still((0, -8.0, 9.5), (3.5, -5.2, 11.8), 24))
shot("S46", "L46", still((1.5, -3.8, 2.8), (0, -0.3, 2.5), 30))
shot("S47", "L47", move(((1.5, -1.4, 4.0), (0, -0.3, 4.6), 36), ((1.5, -1.4, 5.0), (0, -0.3, 5.4), 36)))
shot("S48", "L48", still((0.4, -1.9, 7.8), (0, -0.2, 8.8), 34))
shot("S49", "L49", still((0, -12.0, 1.0), (0, -4.0, 8.5), 20))
shot("S49b", "P01", still((0.3, -12.5, 2.5), (0, -2.0, 6.5), 20))
shot("S50", "L50", still((4.8, -5.0, 7.6), (0, -0.3, 7.6), 24))
shot("S51", "L51", still((1.6, -1.6, 7.95), (0, -0.3, 7.95), 45))
shot("S52", "L52", move(((1.6, -1.6, 7.95), (0, -0.3, 7.95), 45), ((1.4, -1.4, 7.95), (0, -0.3, 8.0), 52)))
shot("S53", "L53", still((0, -12.0, 1.0), (0, -4.0, 8.5), 20))
shot("S54", "L54", still((0.35, -3.2, 8.0), (0.35, 0, 8.0), 24), step=1)
shot("S55", "L55", still((-1.0, -1.0, 8.0), (0.64, -0.45, 8.02), 24), step=1)
shot("S56", "L56", still((-1.0, -1.0, 8.0), (0.64, -0.45, 8.02), 34), step=1)
shot("S57", "L57", still((-0.1, -0.75, 8.05), (0.62, -0.45, 8.05), 44), step=1)
shot("S58", "L58", still((-3.2, -0.9, 7.2), (0, -0.3, 7.2), 30))
shot("S59", "L59", still((0.8, -4.2, 7.2), (0, -0.3, 6.7), 30))
shot("S60", "L60", still((-1.5, -2.8, 7.0), (-0.4, -0.3, 7.8), 30))
shot("S61", "L61", still((1.0, -3.0, 6.5), (0, -0.3, 6.7), 32))
shot("S62", "L62", still((0, -7.5, 5.6), (0, -0.3, 6.2), 20))
shot("S63", "L63", still((-1.9, -1.3, 6.3), (0, -0.4, 6.4), 36))
shot("S64", "L64", move(((-1.3, -1.8, 7.4), (-0.1, -0.2, 8.2), 20), ((-0.9, -1.4, 8.6), (0.0, -0.6, 9.4), 20)))
shot("S65", "L65", still((-0.4, -3.4, 8.8), (0.1, -0.5, 9.6), 24))
shot("S66", "L66", still((-0.3, -1.7, 8.5), (0.62, -0.4, 8.8), 36), step=1)
shot("S67", "L67", still((-3.0, -3.0, 7.7), (0.2, -0.4, 7.9), 20))
shot("S68", "L68", still((0, -8.5, 5.0), (0, -0.5, 5.5), 18))
shot("S69", "L69", still((-1.0, -5.2, 1.5), (-1.5, -2.0, 1.5), 34))
shot("S70", "L70", still((-1.2, -3.8, 1.9), (-1.7, -2.4, 1.45), 42))
shot("S71", "L71", still((-1.5, -5.0, 1.5), (-1.5, -2.0, 1.6), 40))
shot("S72", "L72", still((-1.2, -5.0, 1.5), (-1.5, -2.0, 1.6), 40))
shot("S73", "L73", still((-0.4, -4.3, 1.6), (-0.2, -2.0, 1.25), 38))
shot("S74", "L74", move(((-1.2, -3.5, 1.2), (-0.45, -1.0, 1.5), 28), ((-1.2, -3.5, 5.5), (-0.45, -0.4, 8.0), 28)))
shot("S74b", "P03", still((0, -6.0, 3.0), (0.4, -0.5, 8.8), 22))
shot("S75", "L75", still((-0.8, -3.5, 3.8), (0.5, -0.5, 8.9), 22))
shot("S76", "L76", still((3.2, -3.4, 1.7), (-0.1, -2.0, 1.7), 28))
shot("S77", "L77", still((0.4, -4.6, 1.6), (0.2, -2.2, 1.2), 36))
shot("S78", "L78", still((-1.0, -5.2, 1.7), (-1.0, -2.9, 1.4), 34))
shot("S79", "L79", still((0.4, -5.2, 1.5), (-0.3, -2.2, 1.2), 32))
shot("S80", "L80", still((1.8, -4.2, 4.0), (0, -0.3, 3.8), 28))
shot("S81", "L81", still((-2.0, -1.0, 7.3), (0, -0.3, 7.9), 34))
shot("S82", "L82", still((0.3, -1.3, 8.1), (0.3, -1.8, 9.8), 22))
shot("S83", "L83", still((0, -8.5, 9.0), (2.0, -5.5, 12.0), 22))
shot("S84", "L84", still((-0.4, -0.7, 3.6), (-0.9, -3.2, 1.5), 30))
shot("S85", "L85", still((-3.1, -0.9, 7.2), (0, -0.3, 7.2), 30))
shot("S86", "L86", still((-0.9, -6.0, 1.6), (-0.9, -3.1, 2.4), 26))
shot("S87", "L87", still((-2.6, -1.2, 6.6), (0, -0.3, 6.9), 32))
shot("S88", "L88", still((1.6, -5.8, 0.6), (-0.5, -1.2, 3.5), 24))
shot("S89", "L89", still((0.8, -4.4, 3.0), (0, -0.4, 3.0), 26))
shot("S90", "L90", still((0.3, -6.7, 1.3), (-0.3, -1.8, 1.3), 24))

# ---------------------------------------------------------------------------------------------------- acting
acting = {"me": [], "sam": []}
OFF = re.compile(r"^(?P<base>[LP]\d+(?:\.\d+)?>?)(?P<off>[+-]\d+(?:\.\d+)?)?$")


def minus(ref, d=0.03):
    m = OFF.match(ref)
    base, off = m.group("base"), float(m.group("off") or 0)
    off -= d
    return f"{base}{off:+.2f}"


def seq(who, items):
    """items: (ref, dict), in time order. A dict with 'pos' holds that spot until just before the next item that
    has a different pos (no drift across a cut); 'glide': True lets it walk or lower to the next pos instead."""
    out, pos = [], None
    for i, (ref, kw) in enumerate(items):
        kw = dict(kw)
        glide = kw.pop("glide", False)
        kw.setdefault("blend", 0.06)
        if "pos" in kw:
            pos = kw["pos"]
        out.append({"at": ref, **kw})
        nxt = next(((r2, k2) for r2, k2 in items[i + 1:] if "pos" in k2), None)
        if "pos" in kw and nxt and nxt[1]["pos"] != kw["pos"] and not glide:
            out.append({"at": minus(nxt[0]), "pos": kw["pos"], "blend": 0.06})
    acting[who] = out


UP = [165, 165]
me = [
    ("L01", dict(pos=[0, -0.3, 6.1], yaw=180, arms=[15, 15], side=[35, 35], expr="scared")),
    ("L02", dict(arms=[5, 5], side=[85, 85])),
    ("L07", dict(pos=[0, -1.3, 0.3], arms=[40, 40], side=[0, 0], expr="neutral")),
    ("L09", dict(pos=[0, -0.3, 1.6], arms=[165, 150])),
    ("L10", dict(pos=[0, -0.3, 6.2], arms=UP, expr="worried")),
    ("L12", dict(pos=[0, -1.3, 1.0], arms=[110, 110], side=[10, 10], expr="wide")),
    ("L13", dict(pos=[4.4, -3.6, 0], yaw=0, arms=[70, 70], side=[0, 0], head=[0, 38], expr="worried")),
    ("L14", dict(pos=[-1.8, -0.5, 0.3], yaw=180, arms=[90, 90], head=[0, 10], expr="neutral")),
    ("L15", dict(pos=[0.5, -3.0, 0.3], yaw=0, arms=[0, 0], head=[0, 0])),
    ("L16", dict(pos=[0.5, -3.0, 0.3], yaw=-90, arms=[20, 20])),
    ("L17", dict(pos=[0.0, -3.0, 0.3], yaw=0, arms=[0, 0], head=[0, 0])),
    ("L17.1", dict(head=[28, 0], expr="worried")),
    ("L17.1+0.35", dict(head=[-28, 0])),
    ("L18", dict(pos=[0, -0.3, 6.4], yaw=180, arms=UP, head=[0, 0], expr="worried")),
    ("L19", dict(arms=[165, 178])),
    ("L20", dict(arms=UP, head=[75, -35])),
    ("L27", dict(pos=[0, -0.3, 6.4], arms=UP, head=[0, 0], glide=True)),
    ("L28", dict(pos=[0, -0.3, 3.9], expr="neutral", glide=True)),
    ("L29-0.03", dict(pos=[0, -0.3, 3.7])),
    ("L29", dict(pos=[0.35, -1.7, 0.3], arms=[10, 10])),
    ("L32", dict(pos=[0.8, -2.6, 0.3], glide=True)),
    ("L33-0.03", dict(pos=[0.2, -0.9, 0.3])),
    ("L33", dict(pos=[0, -0.3, 6.4], arms=UP, expr="worried")),
    ("L37", dict(pos=[0, -1.3, 0.3], arms=[40, 40], head=[-40, 0])),
    ("L40", dict(pos=[0, -0.3, 6.4], arms=UP, head=[0, 0])),
    ("L42", dict(pos=[0, -0.3, 3.4], arms=[165, 150], head=[-30, 0], glide=True)),
    ("L43", dict(pos=[0, -0.3, 3.6], arms=[175, 150], glide=True)),
    ("L44", dict(pos=[0, -0.3, 5.0], arms=UP, head=[0, 0])),
    ("L46", dict(pos=[0, -0.3, 1.0], arms=[165, 140], glide=True)),
    ("L47", dict(pos=[0, -0.3, 3.9], arms=[140, 165], head=[-45, 0], glide=True)),
    ("L48", dict(pos=[0, -0.3, 6.4], arms=UP, head=[0, 0])),
    ("L50", dict(expr="worried")),
    ("L51", dict(head=[-70, 0], expr="scared")),
    ("L52", dict(head=[-70, -25])),
    ("L54", dict(arms=[15, 175], head=[-75, 0], expr="terrified")),
    ("L58", dict(arms=[5, 5], side=[60, 60], head=[-30, 0], expr="scared")),
    ("L59", dict(side=[85, 85], head=[0, 0])),
    ("L60", dict(pos=[0, -0.3, 6.4], glide=True)),
    ("L61-0.1", dict(pos=[0, -0.3, 6.1])),
    ("L62", dict(yaw=180, head=[0, 0], expr="wide")),
    ("L63", dict(yaw=140, blend=1.6, head=[0, -35])),
    ("L68", dict(pos=[0, -0.3, 6.1], yaw=180, blend=0.4, head=[0, 0], side=[0, 0], arms=[20, 20], glide=True)),
    ("L69-0.03", dict(pos=[0, -0.9, 0.3])),
    ("L69", dict(pos=[0.1, -2.2, 0.3], yaw=0, arms=[0, 0], expr="neutral")),
    ("L73", dict(arms=[35, 0], expr="worried")),
    ("L76", dict(pos=[0.5, -2.0, 0.3], yaw=180, arms=[0, 0], head=[0, -35])),
    ("L77", dict(pos=[0.2, -2.2, 0.3], yaw=0, head=[0, 0], expr="neutral")),
    ("L80", dict(pos=[0, -0.3, 2.0], yaw=180, arms=[165, 150], glide=True)),
    ("L81-0.03", dict(pos=[0, -0.3, 4.4])),
    ("L81", dict(pos=[0, -0.3, 6.4], arms=UP, head=[75, -30])),
    ("L85", dict(arms=[5, 5], side=[65, 65], head=[60, 0], expr="soft")),
    ("L87", dict(pos=[0, -0.3, 6.0], head=[60, 0], expr="soft")),
    ("L88", dict(pos=[0, -0.3, 6.0], head=[0, 0], glide=True)),
    ("L89", dict(pos=[0, -0.4, 2.4], yaw=40, arms=[10, 10], side=[30, 30], expr="soft", glide=True)),
    ("L90", dict(pos=[0.35, -1.8, 0.7], yaw=0, arms=[0, 0], side=[0, 0], glide=True)),
    ("L90>", dict(pos=[0.35, -1.8, 0.3])),
]
seq("me", me)

sam = [
    ("L15", dict(pos=[-2.0, -4.3, 0.3], yaw=0, arms=[0, 0], expr="neutral")),
    ("L16", dict(pos=[-1.4, -3.0, 0.3], yaw=90, arms=[75, 75])),
    ("L17", dict(arms=[10, 10])),
    ("L35", dict(pos=[4.4, -4.1, 0], yaw=0, arms=[65, 65], head=[0, 35])),
    ("L36", dict(pos=[-0.5, -3.5, 0.3], arms=[0, 0], head=[0, -30])),
    ("L38", dict(pos=[-0.9, -3.3, 0.3], head=[0, -40])),
    ("L39", dict(head=[0, 0])),
    ("L69", dict(pos=[-1.5, -2.0, 0.3], head=[0, -30])),
    ("L70", dict(arms=[80, 0], head=[0, 12])),
    ("L72.1", dict(head=[0, -35])),
    ("L75", dict(arms=[0, 0], head=[0, 0])),
    ("L76", dict(pos=[-0.5, -2.0, 0.3], yaw=180, head=[0, -35])),
    ("L77", dict(pos=[-1.0, -2.9, 0.3], yaw=0, head=[0, 0])),
    ("L78", dict(arms=[60, 60])),
    ("L79", dict(pos=[-0.7, -2.2, 0.3], yaw=90, lean=20, head=[0, 25], arms=[30, 30])),
    ("L80", dict(pos=[-0.9, -3.2, 0.3], yaw=180, lean=0, head=[0, -30], arms=[50, 50])),
    ("L84", dict(lean=-16)),
    ("L84.1", dict(head=[0, 8])),
    ("L84.1+0.35", dict(head=[0, -30])),
    ("L88", dict(pos=[-1.0, -3.0, 0.3], lean=-15, head=[0, -30])),
    ("L90", dict(pos=[-1.0, -1.8, 0.3], yaw=0, lean=0, head=[0, 0], arms=[0, 0], expr="neutral")),
]
seq("sam", sam)

# ---------------------------------------------------------------------------------------------------- cues
cues = [
    {"at": 0, "name": "lamps", "to": 0.15, "dur": 0.01},
    {"at": "L04", "name": "lamps", "to": 1.0, "dur": 0.01},
    {"at": "L49.1", "name": "lamps", "to": 0.15, "dur": 0.7},       # the lamps go out: a slow ramp, never black
    {"at": "L53", "name": "lamps", "to": 1.0, "dur": 0.6},          # and come back, landing on the cut to the face
    {"at": 0, "name": "flood", "to": 0.5, "dur": 0.01},
    {"at": "L04", "name": "flood", "to": 1.0, "dur": 0.01},
    {"at": "L49.1", "name": "flood", "to": 0.35, "dur": 0.7},
    {"at": "L53", "name": "flood", "to": 1.0, "dur": 0.6},
    {"at": "L21", "name": "head", "pose": "t1"},
    {"at": "L33", "name": "head", "pose": "t2"},
    {"at": "L40", "name": "head", "pose": "t3"},
    {"at": "L46", "name": "head", "hidden": True},
    {"at": "L54", "name": "head", "pose": "lip"},
    {"at": "L66", "name": "head", "pose": "belay"},
    {"at": "L77", "name": "head", "hidden": True},
    {"at": 0, "name": "rope", "mode": "me"},
    {"at": "L64.3", "name": "rope", "mode": "creature"},
    {"at": "L73", "name": "rope", "mode": "creature"},
    {"at": "L74", "name": "rope", "mode": "end_up", "dur": 1.9},
    {"at": "P03", "name": "rope", "mode": "gathered"},
    {"at": "L77", "name": "rope", "mode": "sam"},
    {"at": "L29", "name": "coil", "on": True},
    {"at": "L31", "name": "coil", "on": False},
    {"at": "L31", "name": "tag", "swing": 12},
    {"at": "L32", "name": "tag", "swing": 3},
    {"at": "L70", "name": "tag2", "on": True},
    {"at": "L75", "name": "tag2", "on": False},
    {"at": "L77", "name": "knot", "on": True},
    {"at": "L77", "name": "warm", "to": 1.0, "dur": 0.5},
]

# per-shot lights. The creature's close shots: the front lamps dead, a key from below, a cold blue rim (set.py places them)
DARK = {"lamps": 0.02, "flood": 0.15, "fill": 0.35}
WIDE_C = {"ckey_g": 0.5, "crim_g": 0.6}
looks = {}
for sid in ("S21", "S22", "S23", "S24", "S25", "S26", "S33", "S34", "S40", "S41", "S54", "S55", "S56", "S57", "S66", "S67", "S75"):
    looks[sid] = dict(DARK)
for sid in ("S27", "S62", "S68"):
    looks[sid] = dict(WIDE_C)
looks["S27"].update({"lamps": 0.7})
for sid in ("S10", "S11", "S12"):      # memory: soft and dim
    looks[sid] = {"lamps": 0.35, "flood": 0.35, "fill": 1.0}
looks["S82"] = {"glow": [[0.3, -1.4, 9.0], 260.0]}

# ---------------------------------------------------------------------------------------------------- sound
sfx = [
    {"at": "L01", "kind": "creak", "db": -22, "dur": 1.2},
    {"at": "L43.1", "kind": "creak", "db": -24, "dur": 0.9},
    {"at": "L44", "kind": "creak", "db": -22, "dur": 1.2},
    {"at": "L49.1", "kind": "hum_sweep", "db": -20, "dur": 0.8},
    {"at": "P01+0.15", "kind": "click", "db": -26},
    {"at": "P01+0.6", "kind": "click", "db": -26},
    {"at": "L52", "kind": "creak", "db": -20, "dur": 1.3},
    {"at": "L54", "kind": "hit", "db": -8},
    {"at": "L60", "kind": "whoosh", "db": -22, "dur": 0.4},
    {"at": "L61", "kind": "thud", "db": -16},
    {"at": "P02", "kind": "creak", "db": -20, "dur": 0.9},
    {"at": "L74", "kind": "whoosh", "db": -22, "dur": 1.6},
    {"at": "L87", "kind": "thud", "db": -22},
    {"at": "L90>-0.04", "kind": "thud", "db": -12},
    {"at": "L90>-0.02", "kind": "bell", "db": -22, "dur": 0.5},
]
story = {
    "slug": "ep30-top-rope",
    "title": "Who was standing upside down on the ceiling above my climb?",
    "made_for_kids": False,
    "premise": "I climb alone on the auto-belay in a brick mill, and since a slip last year I won't let anyone hold my rope. Each Thursday, from the top hold, someone is standing upside down on the overhang ceiling, one hold nearer.",
    "twist": "The auto-belay has been broken for weeks: the upside-down figure is my belayer, my rope tied round its waist, and the thing that held me when I let go was the other end of a climb that needs two.",
    "world": "a tall old brick mill turned climbing gym: soot brick, iron lamps on chains, a grey-green wall with a roof of holds, blue crash mats, deep evening windows",
    "voice": {"voice": "am_adam", "tempo": 1.03, "rate": 1.45},
    "key_color": "#3ee0c8",
    "caption": {"ink": "#08090d", "stroke_add": 2, "shadow": 0.8},
    "key_stroke": 2,
    "gap": 0.12,
    "tail": 0.25,
    "look": {"fog": "#10141c", "fog_density": 0.012, "fog_start": 6.0, "sky": "#080a10", "sky_strength": 1.0,
             "exposure": 0.6},
    "grade": {"shadows": [-0.02, 0.0, 0.05], "highlights": [0.03, 0.01, -0.02], "saturation": 0.95, "contrast": 1.08,
              "vignette": 0.38, "bloom": 0.28, "grain": 0.013, "red_line": 0.79},
    "phonemes": {"route": "ɹˈaʊt"},
    "cast": cast,
    "creature": creature,
    "looks": looks,
    "lines": lines,
    "shots": SH,
    "acting": acting,
    "cues": cues,
    "fx": [{"at": "L54", "kind": "punch", "dur": 0.35, "zoom": 1.1, "fade": 0.2}],
    "music": {"root": 40, "mode": "phrygian", "bpm": 74, "seed": 30,
              "sections": [
                  {"at": 0, "voices": ["drone", "pad"], "energy": 0.4},
                  {"at": "L04", "voices": ["drone", "pad"], "energy": 0.3},
                  {"at": "L18", "voices": ["drone", "pad", "pulse"], "energy": 0.4},
                  {"at": "L33", "voices": ["drone", "pad", "pulse"], "energy": 0.5},
                  {"at": "L46", "voices": ["drone", "pad", "choir"], "energy": 0.55},
                  {"at": "L49", "voices": ["drone", "pad"], "energy": 0.3},
                  {"at": "L54", "voices": ["drone", "pad", "choir"], "energy": 0.6},
                  {"at": "L62", "voices": ["pad"], "energy": 0.3},
                  {"at": "L77", "voices": ["piano", "pad"], "energy": 0.4, "mode": "major", "root": 40},
              ]},
    "sound": {"floor": "wood", "steps_db": -22,
              "ambience": [
                  {"kind": "room", "from": 0, "to": "end", "lufs": -33},
                  {"kind": "hum", "from": "L49", "to": "L53", "lufs": -40},
              ],
              "sfx": sfx,
              "music_drops": [{"from": "L54-0.7", "to": "L54.1", "keep": ["hit"]}]},
}
OUT.write_text(json.dumps(story, indent=1, ensure_ascii=False) + "\n")
print("wrote", OUT, f"({len(SH)} shots)")
