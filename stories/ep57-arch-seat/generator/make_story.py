"""Writes ../story.json for ep57 "In this town, every favour you owe sits on your head as a gold block".

Run from anywhere: python stories/ep57-arch-seat/generator/make_story.py
The words are in linetext.py (cut into lines.json). Everything else is here: the cast, the shots and their cameras,
the staging, the gold-block stacks, the light grades, the score and the sound. set.py reads the cues (see its header).

Placement: a character is put at a spot by the `place` acting key (so a cut never walks it across the square and never
makes footsteps); only real walking is a `pos` move. Characters not staged in a shot are hidden at its cut.
"""
import json
import math
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import linetext  # noqa: E402

OUT = HERE.parent / "story.json"
lines = linetext.lines()
(HERE / "lines.json").write_text(json.dumps(lines, indent=1, ensure_ascii=False))

# holds if the voice lands short of the floor: L09, L24, L36, L52, L57 get a beat
HOLDS = {"L14": 0.7, "L46": 0.0, "L47": 0.0, "L09": 0.3, "L24": 0.3, "L36": 0.3, "L52": 0.4, "L57": 0.4, "L72": 0.0}
for ln in lines:
    if ln["id"] in HOLDS:
        ln["gap"] = HOLDS[ln["id"]]
LOOP = 0.12
TEMPO = {"L37": 0.93, "L46": 0.97, "L61": 0.92, "L62": 0.93, "L68": 0.97}
for ln in lines:
    if ln["id"] in TEMPO:
        ln["tempo"] = TEMPO[ln["id"]]

# ---------------------------------------------------------------------------------------------------- cast
FACE = {"eyes": "round", "brows": True, "ink": "#1b1410"}


def person(skin, shirt, pants, hair="cap", hair_c="#3a2a1e", sleeves="long", pattern="solid", pattern_c=None,
           shoes=None, stack=0, height=1.0, extras=None, hat=None, hat_c=None, eyes="round", **kw):
    d = {"age": "adult", "skin": skin, "shirt": shirt, "pattern": pattern, "pants": pants, "shoes": shoes or "#3a3633",
         "sleeves": sleeves, "hair": hair, "hair_c": hair_c, "hat": hat or "none",
         "face": {"eyes": eyes, "brows": True, "ink": "#1b1410"}}
    if pattern_c:
        d["pattern_c"] = pattern_c
    if hat_c:
        d["hat_c"] = hat_c
    if extras:
        d["extras"] = extras
    if height != 1.0:
        d["height"] = height
    if stack:
        d["stack_cap"] = stack
    d.update(kw)
    return d


cast = {
    "me": person("#e0ac80", "#d9a627", "#3f5e3a", "cap", "#5b3d28", extras=["hooddown"], stack=24),
    "ilan": person("#d8a27a", "#7fb7e6", "#c8aa7a", "cap", "#15110f", sleeves="short", pattern="stripes",
                   pattern_c="#a6cdf0", hat="ballcap", hat_c="#d0473c", stack=24),
    "varga": person("#e8bc98", "#6b3f6b", "#4a3a4a", "bun", "#b9b5b0", extras=["apron"], extra_c="#f4f1ea", height=0.95,
                    stack=3),
    "ode": person("#c99468", "#3f6b3a", "#3b5a36", "none", "#222222", extras=["glasses"], stack=3),
    "landlady": person("#e3b894", "#b9a2d6", "#8d86a0", "bun", "#eeeeee", height=0.93, stack=2),
    "span": {"age": "adult", "skin": "#c9a07e", "shirt": "#c98d8f", "pattern": "knit", "pattern_c": "#b4797c",
             "pants": "#e8dcc4", "shoes": "#e8dcc4", "sleeves": "long", "hair": "cap", "hair_c": "#5a463a",
             "hat": "none", "face": {"eyes": "pin", "brows": False, "mouth": "flat", "ink": "#2a1d15"}},
    "dwoman": person("#e5b48c", "#c96a6a", "#5b4a6b", "long", "#4a2f22", stack=3),
    "dman": person("#cf9a72", "#4a6a9a", "#3a3a40", "cap", "#2a1d15", stack=6),
    "pass1": person("#e0b090", "#8aa86a", "#6b5a45", "cap", "#7a5a3a", stack=2),
    "pass2": person("#c99470", "#c9a05a", "#44505e", "swoop", "#2a2420", stack=3),
    "mover": person("#d8a27a", "#8a6a3a", "#3d4a5c", "cap", "#4a3828", stack=14),
    "neigh1": person("#e3b894", "#7a9ab8", "#6b6358", "cap", "#8a8a8a", stack=4, height=0.97),
    "neigh2": person("#c99470", "#b87a5a", "#4a4a52", "buzz", "#2a2420", stack=4),
    "best": person("#e0ac80", "#2a2f45", "#2a2f45", "cap", "#3a2a1e", extras=["tie"], extra_c="#c9a05a", stack=20),
    "wed1": person("#e5b48c", "#f2ece0", "#d8cfc0", "long", "#5a3a28", stack=2),
    "wed2": person("#cf9a72", "#5c6a8a", "#3a3a40", "cap", "#1d1612", stack=3),
    "wed3": person("#e3b894", "#9a5a6a", "#4a3a44", "bun", "#8a8a8a", stack=1),
    "wed4": person("#c99470", "#4a5a4a", "#34383a", "buzz", "#2a2420", stack=4),
}
FOLK = [("#e0ac80", "#b0556a", "#46404a", "long", "#2a1d15", 1), ("#cf9a72", "#5a8aa0", "#4b4338", "cap", "#3a2a1e", 2),
        ("#e5b48c", "#a0a050", "#55453a", "swoop", "#6a4a2a", 0), ("#c99470", "#8a5a9a", "#3a4a58", "cap", "#1d1612", 3),
        ("#d8a27a", "#d0884a", "#3f4a3a", "buzz", "#5a4a3a", 1), ("#e3b894", "#5a9a7a", "#4a3a3a", "bun", "#9a8a7a", 2),
        ("#cf9a72", "#a85a4a", "#34405a", "cap", "#2a2420", 4), ("#e0ac80", "#6a7ab0", "#5a5048", "long", "#8a5a3a", 0)]
for i, (sk, sh, pn, hr, hc, st) in enumerate(FOLK, 1):
    cast[f"folk{i}"] = person(sk, sh, pn, hr, hc, stack=max(st, 1))

# ---------------------------------------------------------------------------------------------------- DSL
DEG = math.degrees


def yaw_to(a, b):
    return round(DEG(math.atan2(b[0] - a[0], -(b[1] - a[1]))), 1)


def still(loc, tgt, lens):
    return [[0, list(loc), list(tgt), lens]]


def move(a, b, lens_a, lens_b=None):
    return [[0, list(a[0]), list(a[1]), lens_a], [1, list(b[0]), list(b[1]), lens_b or lens_a]]


def around(tgt, d, az, h, lens, tz=None):
    """A camera d metres from tgt on the bearing az (0: south of it looking north, 90: west of it looking east)."""
    loc = [tgt[0] + d * math.sin(math.radians(az)), tgt[1] - d * math.cos(math.radians(az)), h]
    return still(loc, [tgt[0], tgt[1], tgt[2] if len(tgt) > 2 else (tz or 1.5)], lens)


shots = []     # {id, ref, cam, stage: [...], step, hand}
cues = []
sfx = []
cnt = {}       # stack counts as the cues are laid down in time order


def plus(ref, dt):
    if isinstance(ref, (int, float)):
        return round(ref + dt, 3)
    if "+" in ref:
        base, off = ref.split("+")
        return f"{base}+{float(off) + dt:.3f}"
    return f"{ref}+{dt:.3f}"


def shot(sid, ref, cam, *stage, step=2, hand=0.012, env=None, **kw):
    shots.append({"id": sid, "ref": ref, "cam": cam, "stage": list(stage), "step": step, "hand": hand, **kw})
    if env:
        cues.append({"at": ref, "name": "env", "state": env[0], "dur": max(0.3, env[1]), **({"wet": True} if len(env) > 2 else {})})


def A(who, x, y, yaw=0.0, expr="neutral", z=0.0, **kw):
    return {"who": who, "p": [x, y, z], "yaw": yaw, "expr": expr, **kw}


def face(a, b):
    return yaw_to(a, b)


def stack(who, n, ref, mode=None, **kw):
    cnt[who] = n
    cues.append({"at": ref, "name": "stack", "who": who, "n": n, **({"mode": mode} if mode else {}), **kw})


def arc(frm, to, ref, dur=0.6):
    si, di = cnt[frm] - 1, cnt[to]
    cues.append({"at": ref, "name": "arc", "from": frm, "to": to, "si": si, "di": di, "dur": dur})
    stack(frm, cnt[frm] - 1, ref, "set")
    stack(to, cnt[to] + 1, plus(ref, dur), "arcin")


def sf(at, kind, db, **kw):
    sfx.append({"at": at, "kind": kind, "db": db, **kw})


def cue(at, name, **kw):
    cues.append({"at": at, "name": name, **kw})


SIT = -0.23   # a seated character's z (the seat is 0.45 m, the hips 0.68 m up)
SEATY = 16.7  # hips when seated normally
IL = -0.62    # Ilan's half
ME = 0.62     # mine

# ================================================================================================== THE SHOTS
def fc(x, y, az, d, lens, head=1.62, hp=0.38, off=(0.0, 0.0)):
    """A still camera d metres from (x, y) on bearing az (0: south of it looking north; 90: east of it looking west), the
    lens in mm. The head height `head` sits hp of the way down the frame (0.38: above the caption band)."""
    fh = d * 24.0 / lens
    tz = head - fh * (0.5 - hp)
    loc = [x + d * math.sin(math.radians(az)) + off[0], y - d * math.cos(math.radians(az)) + off[1], tz + 0.12]
    return still(loc, [x + off[0], y + off[1], tz], lens)


def fm(a, b):
    """A camera move from one fc(...) to another (both keyword dicts)."""
    ca, cb = fc(**a), fc(**b)
    return [[0, ca[0][1], ca[0][2], ca[0][3]], [1, cb[0][1], cb[0][2], cb[0][3]]]


def pair(a, b, d, lens, az=None, head=1.62, hp=0.38):
    mid = ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2)
    if az is None:
        az = (DEG(math.atan2(b[0] - a[0], b[1] - a[1])) + 90) % 360
    return fc(mid[0], mid[1], az, d, lens, head, hp)


# ---- 1  the rule, the montage (L01 to L08)
shot("S01", 0, fc(-9.9, 4.7, 90, 3.0, 26),
     A("dwoman", -10.35, 5.1, 35, "grin", head=[-10, 0]),
     A("dman", -9.8, 4.3, 140, "grin", flap=(0.15, 1.4), head=[10, 0]),
     A("pass1", -8.9, 8.2, 0, "neutral"), A("pass2", -8.0, 6.8, 20, "smirk"), env=("day", 0.3), step=2)
stack("dman", 3, 0)
stack("dwoman", 3, 0)
stack("pass1", 1, 0)
stack("pass2", 2, 0)
stack("dman", 4, 1.6, "land")
cue(0, "door", open=1, init=True)
sf(1.6, "click", -12)
sf(0.0, "chime", -19)

WIDE = still([3.0, -3.4, 2.1], [-1.0, 8.0, 3.0], 17)
crowd = [A("folk1", -4.5, 4.6, 40, "grin"), A("folk2", -1.5, 6.0, 200, "neutral"), A("folk3", 1.5, 3.4, 150, "smirk"),
         A("folk4", 3.5, 6.6, 250, "grin"), A("folk5", -6.0, 7.5, 120, "neutral"), A("folk6", 0.5, 9.2, 180, "grin"),
         A("folk7", 6.0, 4.2, 100, "neutral"), A("folk8", -3.2, 9.6, 220, "smirk"),
         A("pass1", -7.2, 3.6, 90, "neutral"), A("pass2", 5.2, 8.4, 230, "grin"), A("dman", 2.0, 1.2, 180, "grin"),
         A("dwoman", -2.0, 2.2, 140, "grin")]
shot("S02", "L01.3", WIDE, *crowd)
for i in range(1, 9):
    stack(f"folk{i}", [1, 2, 1, 3, 1, 2, 4, 1][i - 1], 0)

shot("S03", "L02", fc(-9.6, 4.6, 5, 2.6, 30, head=1.6),
     A("dwoman", -9.6, 4.6, 5, "grin", arms=[0, 100], side=[0, 40]), A("dman", -8.6, 6.4, 180, "neutral"))
shot("S04", "L02.2", fc(-9.9, 4.15, 90, 2.5, 34, head=1.75, hp=0.5),
     A("dman", -9.9, 4.15, 180, "grin"), A("dwoman", -9.9, 5.25, 0, "grin"))
stack("dman", 3, "L02.2-0.01", "set")
stack("dman", 4, "L02.2+0.2", "land")
sf("L02.2+0.2", "click", -12)
shot("S05", "L03", fc(-9.9, 4.15, 120, 2.3, 34, head=1.62),
     A("dman", -9.9, 4.15, 150, "worried", head=[0, -12], flap=(0.05, 0.7)), A("dwoman", -9.9, 5.25, 0, "smile"))
shot("S06", "L04", fc(-9.7, 4.3, 90, 3.8, 26),
     A("dwoman", -9.9, 4.9, 180, "grin"), A("dman", -9.4, 3.7, 270, "grin", arms=[0, 78]))
stack("dman", 4, "L04-0.01", "set")
stack("dman", 3, "L04.3-0.1", "drop")
sf("L04.3-0.1", "click", -20)
shot("S06b", "L04.4", fc(-9.9, 4.7, 90, 3.0, 26),
     A("dwoman", -10.35, 5.1, 35, "smile", head=[-10, 0]), A("dman", -9.8, 4.3, 140, "grin", head=[10, 0]))
cue("L05", "door", open=0)
shot("S07", "L05", fm(dict(x=0.4, y=3.6, az=0, d=5.5, lens=22, head=1.75, hp=0.5), dict(x=2.0, y=3.6, az=0, d=5.5, lens=22, head=1.75, hp=0.5)),
     A("mover", 0.2, 3.6, 90, "grin", walk=(2.2, 3.6), arms=[50, 50]), A("folk1", 3.8, 2.6, 160, "grin", arms=[0, 130]),
     A("folk4", 5.5, 4.4, 220, "smirk", arms=[0, 140]))
stack("mover", 14, 0)
shot("S08", "L06", fc(7.4, -0.4, 35, 4.0, 22, head=1.5, hp=0.5),
     A("mover", 6.2, -0.4, 90, "worried", walk=(7.9, -0.4), bend=48, head=[0, 18], stackfollow=1.0),
     A("folk2", 5.0, 2.4, 180, "grin"))
shot("S09", "L07", fc(-4.7, 9.3, 0, 4.2, 26),
     A("neigh1", -5.5, 9.3, 90, "smirk"), A("neigh2", -3.9, 9.3, 270, "smirk"))
stack("neigh1", 3, 0)
stack("neigh2", 2, 0)
shot("S10", "L07.3", fc(-4.7, 9.3, 330, 4.2, 26),
     A("neigh1", -5.5, 9.3, 90, "grin"), A("neigh2", -3.9, 9.3, 270, "grin"))
arc("neigh1", "neigh2", "L07.0", 0.6)
arc("neigh2", "neigh1", "L07.4", 0.6)
sf("L07.0+0.6", "click", -14)
sf("L07.4+0.6", "click", -14)
shot("S11", "L08", still([5.5, 7.6, 1.5], [5.5, 12.4, 1.4], 28),
     A("best", 5.5, 12.6, 0, "smile", z=0.34), A("wed1", 4.3, 12.4, 10, "grin", z=0.34),
     A("wed2", 6.7, 12.4, 350, "grin", z=0.34), A("wed3", 3.3, 12.1, 15, "smile", z=0.34),
     A("wed4", 7.7, 12.1, 345, "smile", z=0.34))
stack("best", 20, 0)
for w, n in (("wed1", 2), ("wed2", 3), ("wed3", 1), ("wed4", 4)):
    stack(w, n, 0)
# ---- 2  me (L09 to L11)
shot("S12", "L09", fc(-0.6, 5.0, 10, 4.6, 26, head=1.2, hp=0.62),
     A("me", -1.35, 5.0, 10, "neutral"), A("ilan", 0.15, 5.0, 350, "grin", head=[0, 5]),
     A("folk1", -3.4, 7.4, 0, "grin"), A("folk4", 2.4, 6.8, 350, "smirk"))
stack("me", 0, 0)
stack("ilan", 12, 0)
shot("S13", "L10", fc(-0.2, 4.0, 350, 2.2, 34, head=1.7, hp=0.45), A("me", -0.5, 4.0, 350, "neutral"),
     A("ilan", 0.75, 4.2, 340, "grin", head=[0, 5]), A("folk2", 3.2, 6.5, 0, "grin"))
shot("S14", "L11", fc(9.8, 2.0, 0, 3.0, 26),
     A("me", 9.8, 2.0, 0, "neutral", arms=[40, 60]))
# ---- 3  Ilan, the seat, the whispers (L12 to L20)
shot("S15", "L12", move(([-2.0, 0.6, 1.3], [-2.0, 3.9, 1.5]), ([-2.0, 0.6, 1.3], [-2.0, 3.9, 3.6]), 24),
     A("ilan", -2.0, 3.9, 355, "grin"), A("folk2", -3.7, 7.4, 160, "neutral"), A("folk1", -1.6, 7.8, 190, "grin"),
     A("folk3", 0.3, 7.2, 170, "neutral"))
cue("L13", "prop", item="bag", on=True)
shot("S16", "L13", move(([0.9, 10.4, 1.7], [-0.2, 16.4, 1.3]), ([0.5, 12.3, 1.6], [-0.2, 16.4, 1.45]), 24),
     A("ilan", IL, SEATY, 0, "grin", z=SIT, sit=True, cap=True))
cue(0, "strokes", on=False)
cue("L14", "strokes", on=True)
cue("L15", "strokes", on=False)
shot("S17", "L14", still([0.15, 14.55, 0.5], [0.0, 15.62, 0.4], 36))
shot("S18", "L15", fm(dict(x=-4.5, y=8.5, az=0, d=5.0, lens=22), dict(x=-1.0, y=8.5, az=0, d=5.0, lens=22)),
     A("me", -4.5, 8.5, 90, "neutral", walk=(-1.0, 8.5), head=[-20, 0]), A("folk1", -5.0, 10.5, 90, "grin"))
shot("S19", "L16", fc(8.8, 5.2, 270, 3.4, 22, head=1.32, hp=0.4),
     A("folk6", 8.8, 4.5, 180, "worried", z=SIT, sit=True), A("folk3", 8.8, 5.9, 0, "worried", z=SIT, sit=True))
shot("S20", "L17", still([6.0, 5.6, 0.7], [9.6, 6.8, 2.7], 24),
     A("ilan", 10.1, 7.8, 270, "grin"))
shot("S21", "L18", fm(dict(x=-9.0, y=6.8, az=20, d=5.2, lens=24, head=1.6, hp=0.5), dict(x=-9.0, y=5.4, az=20, d=5.2, lens=24, head=1.6, hp=0.5)),
     A("ilan", -9.0, 6.8, 0, "grin", walk=(-9.0, 5.4)), env=("day", 0.3))
stack("ilan", 16, "L18", "set")
shot("S22", "L19", fc(-2.5, 4.0, 0, 3.6, 20, head=1.62, hp=0.5),
     A("ilan", -2.5, 4.0, 0, "worried", head=[0, 10]))
shot("S23", "L19.2", still([-2.0, 0.6, 3.2], [-2.0, 5.0, 0.0], 26),
     A("ilan", -3.2, 4.0, 90, "grin", walk=(-1.2, 4.0)))
shot("S24", "L20", fc(0.0, 4.6, 0, 6.5, 22, head=1.62, hp=0.5),
     A("ilan", 0.0, 4.3, 0, "grin"), A("folk1", -2.0, 5.2, 300, "neutral", walk=(-2.8, 4.6)),
     A("folk2", 2.3, 4.7, 60, "neutral", walk=(2.9, 3.6)), A("folk4", -0.4, 6.8, 180, "worried"))
# ---- 4  the shadow (L21 to L25)
shot("S25", "L21", fm(dict(x=1.0, y=11.2, az=0, d=5.0, lens=22), dict(x=-0.6, y=11.2, az=0, d=5.0, lens=22)),
     A("me", 1.4, 11.2, 270, "neutral", walk=(-1.0, 11.2)))
shot("S26", "L22", fc(0.3, 12.0, 8, 2.0, 34), A("me", 0.3, 12.0, 8, "worried", look=[0, -0.6], head=[0, 14]))
shot("S27", "L23", still([0.0, 8.4, 1.5], [0.0, 12.7, 0.0], 24), step=2)
cue("L23-0.4", "shadow", kind="floor", y=14.0, yaw=180, stretch=1.7)
shot("S28", "L23.3", move(([-1.7, 10.6, 1.1], [-1.1, 13.0, 0.0]), ([1.7, 10.6, 1.1], [1.1, 13.0, 0.0]), 22))
shot("S29", "L24", still([0.5, 10.3, 1.5], [0.0, 16.0, 0.6], 22),
     A("ilan", IL, SEATY - 0.1, 0, "worried", z=SIT, sit=True, head=[0, 12]))
shot("S30", "L25", still([1.2, 11.0, 1.8], [-2.6, 4.6, 1.2], 22),
     A("me", -1.2, 8.0, 200, "worried", walk=(-4.4, 2.6)))
cue("L25", "shadow", kind="none")
# ---- 5  my luck (L26 to L29)
shot("S31", "L26", fc(-10.05, 3.0, 0, 3.4, 30, head=1.5, hp=0.42),
     A("varga", -10.75, 3.0, 90, "grin", arms=[40, 40]), A("me", -9.4, 3.0, 270, "smile"))
cue("L26", "prop", item="loaf", on=True, loc=[-10.1, 3.0, 1.12])
shot("S32", "L26.2", fc(-9.6, 3.0, 0, 3.8, 26, head=1.5, hp=0.42),
     A("varga", -10.75, 3.0, 90, "grin"), A("me", -9.4, 3.0, 270, "smile"),
     A("ilan", -8.55, 3.0, 270, "smile", flap=(0.1, 0.9)))
stack("ilan", 17, "L26.2+0.5", "land")
sf("L26.2+0.5", "click", -12)
shot("S33", "L27", fc(-7.8, 0.4, 0, 4.2, 22, head=1.55, hp=0.45),
     A("ode", -9.0, -0.3, 70, "grin", arms=[0, 90]), A("me", -8.2, 0.8, 250, "smile"),
     A("ilan", -6.8, 2.4, 200, "smile", flap=(0.2, 1.0)))
cue("L27", "prop", item="loaf", on=False)
stack("ilan", 18, "L27+0.9", "land")
sf("L27+0.9", "click", -12)
shot("S34", "L28", fc(-9.8, 9.6, 0, 3.4, 26),
     A("landlady", -10.4, 9.6, 90, "smile", arms=[0, 60]), A("me", -9.0, 9.6, 270, "smile"))
shot("S35", "L29", fc(-2.8, 4.4, 0, 3.3, 24, head=1.74), A("me", -2.8, 4.4, 0, "grin", z=0.12))
# ---- 6  Saturday 2: the empty seat, the phone, dusk (L30 to L38)
shot("S36", "L30", fc(-1.0, 5.0, 10, 3.6, 20, head=1.62, hp=0.62), A("ilan", -1.0, 5.0, 10, "grin"), env=("day", 0.3))
stack("ilan", 19, "L30", "set")
shot("S37", "L30.2", fc(3.0, 8.5, 25, 2.6, 30), A("me", 3.0, 8.5, 25, "angry"))
shot("S38", "L31", still([0.0, 9.2, 1.0], [0.0, 16.6, 1.05], 30))
shot("S39", "L32", still([0.0, 13.8, 1.15], [0.0, 16.2, 0.55], 26))
cue("L32", "prop", item="cap", on=True)
cue("L32", "prop", item="bag", on=True)
shot("S40", "L33", still([0.0, 9.2, 1.0], [0.0, 16.6, 1.05], 30))
cue("L33", "shadow", kind="wall")
shot("S41", "L34", fc(8.3, 4.9, 270, 3.0, 26), A("me", 8.3, 4.1, 100, "worried", walk=(8.3, 5.7)))
cue("L34", "shadow", kind="none")
shot("S42", "L34.2", fm(dict(x=0.3, y=3.5, az=0, d=5.0, lens=22), dict(x=0.3, y=8.0, az=0, d=5.0, lens=22)),
     A("me", 0.3, 3.0, 0, "worried", walk=(0.3, 8.5)))
shot("S43", "L35", still([0.4, 15.0, 0.95], [-0.4, 16.15, 0.5], 36))
cue("L35", "prop", item="phone", on=True)
for k in range(3):
    sf(f"L35+{0.05 + 0.25 * k:.2f}", "click", -24)
shot("S44", "L36", fc(-0.5, 7.0, 15, 2.4, 32), A("me", -0.5, 7.0, 15, "worried", arms=[0, 110], head=[0, -8]),
     env=("dusk", 2.0))
shot("S45", "L37", fc(3.0, 5.0, 20, 3.2, 24), A("ilan", 3.0, 5.0, 20, "worried", head=[0, 6]))
stack("ilan", 20, "L37-0.05", "set")
shot("S46", "L38", fm(dict(x=3.0, y=5.0, az=20, d=4.2, lens=20, head=2.2, hp=0.5), dict(x=3.0, y=5.0, az=20, d=4.2, lens=20, head=4.2, hp=0.5)),
     A("ilan", 3.0, 5.0, 20, "worried", head=[0, 6]))
# ---- 7  Saturday 3: rain, the Span (L39 to L48)
shot("S47", "L39", still([2.5, 1.5, 1.7], [-1.0, 9.0, 1.9], 22), A("folk2", 5.5, 4.0, 180, "neutral"),
     env=("rain", 0.3))
cue("L39", "prop", item="cap", on=False)
cue("L39", "prop", item="bag", on=False)
cue("L39", "prop", item="phone", on=False)
ARCHCAM = still([0.1, 10.2, 1.05], [0.0, 16.6, 1.2], 38)
WIDECAM = still([0.0, 7.0, 1.45], [0.0, 16.6, 1.15], 30)      # the whole arch mouth, wall to wall, from the square
LIT = dict(rim=1000, key=800, front=0, face=320)
SEATED_ILAN = dict(z=SIT, sit=True, bend=62, head=[0, 22], cap=False)
cue("L40", "env", state="raindim", dur=1.0)
shot("S48", "L40", ARCHCAM, A("ilan", IL, 16.05, 0, "worried", **SEATED_ILAN), step=2)
stack("ilan", 22, "L39", "set")
shot("S49", "L41", WIDECAM, A("ilan", IL, 16.05, 0, "worried", **SEATED_ILAN),
     A("span", 0.0, 16.95, 0, "neutral", side=[8, 8], z=SIT, sit=True), step=1)
cue("L41", "spanlight", on=True, rim=0, key=0, front=0, face=0)
cue("L41", "wallglow", e=3.6, dur=0.3, dim=0.88)
shot("S50", "L41.3", fc(0.7, 10.6, 30, 2.8, 28),
     A("me", 0.7, 10.6, 30, "wide"), A("ilan", IL, 16.05, 0, "worried", **SEATED_ILAN),
     A("span", 0.0, 16.95, 0, "neutral", side=[8, 8], z=SIT, sit=True))
shot("S51", "L42", still([1.3, 14.2, 0.8], [-0.1, 16.95, 1.0], 18),
     A("ilan", IL, 16.05, 0, "worried", **SEATED_ILAN),
     A("span", 0.0, 16.95, 0, "neutral", side=[8, 8], z=SIT, sit=True), step=1)
cue("L42", "spanlight", on=True, rim=900, key=600, front=0, face=240)
cue("L42", "wallglow", e=1.5, dur=0.5, dim=0.35)
cue("L43", "spanlight", on=True, **LIT)
shot("S52", "L43", WIDECAM, A("ilan", IL, 16.05, 0, "worried", **SEATED_ILAN),
     A("span", 0.0, 16.95, 0, "neutral", side=[8, 8], z=SIT, sit=True), step=1)
shot("S53", "L44", still([0.2, 14.0, 1.2], [0.0, 16.95, 1.45], 38),
     A("ilan", IL, 16.05, 0, "worried", **SEATED_ILAN),
     A("span", 0.0, 16.95, 0, "neutral", side=[8, 8], z=SIT, sit=True, head=[-18, 0]), step=1)
shot("S54", "L44.2", still([-1.2, 14.2, 1.7], [IL, 16.0, 1.0], 36),
     A("ilan", IL, 16.05, 0, "worried", **SEATED_ILAN),
     A("span", 0.0, 16.95, 0, "neutral", side=[8, 8], z=SIT, sit=True, head=[-18, 0]), step=1)
shot("S55", "L45", still([0.1, 14.6, 0.35], [0.0, 16.9, 1.9], 24),
     A("span", 0.0, 16.95, 0, "neutral", side=[8, 8], z=SIT, sit=True), step=1)
shot("S56", "L46", fc(0.3, 10.5, 0, 1.7, 40), A("me", 0.3, 10.5, 0, "worried", head=[55, 0]))
shot("S57", "L46.2", WIDECAM,
     A("ilan", IL, 16.05, 0, "worried", **SEATED_ILAN),
     A("span", -0.15, 15.2, 180, "neutral", side=[8, 8]), step=1)
cue("L46.2", "spanlight", on=True, **LIT)
shot("S58", "L47", still([0.0, 11.4, 1.2], [-0.15, 15.6, 1.3], 34),
     A("ilan", IL, 16.05, 0, "worried", **SEATED_ILAN),
     A("span", -0.15, 15.2, 180, "neutral", side=[8, 8], bend=32, head=[0, 25]), step=1)
shot("S59", "L47.3", still([0.3, 13.0, 3.0], [-0.62, 15.9, 0.9], 26),
     A("ilan", IL, 16.05, 0, "worried", **SEATED_ILAN),
     A("span", -0.15, 15.2, 180, "neutral", side=[8, 8], bend=32, head=[0, 25]), step=1)
# ---- 8  the reading of it (L48 to L55)
shot("S60", "L48", still([1.3, 16.1, 1.0], [-0.62, 16.0, 0.85], 36),
     A("ilan", IL, 16.05, 0, "squeeze", mouth=(0.0, 1.6), **SEATED_ILAN))
cue("L48", "spanlight", on=False)
cue("L48", "seatfill", e=200)
cue("L56", "seatfill", e=0)
cue("L48", "ilanlight", on=True)
cue("L49", "ilanlight", on=False)
cue("L46.2", "ilanlight", on=True)
stack("ilan", 17, "L49", "set")
stack("ilan", 18, "L50", "set")
stack("ilan", 22, "L51", "set")
shot("S61", "L49", fc(-9.6, 3.0, 0, 3.8, 26, head=1.5, hp=0.42),
     A("varga", -10.75, 3.0, 90, "grin"), A("me", -9.4, 3.0, 270, "smile"), A("ilan", -8.55, 3.0, 270, "smile", flap=(0.0, 0.9)),
     env=("day", 0.5))
shot("S62", "L50", fc(-7.8, 0.4, 0, 4.2, 22, head=1.55, hp=0.45),
     A("ode", -9.0, -0.3, 70, "grin", arms=[0, 90]), A("me", -8.2, 0.8, 250, "smile"),
     A("ilan", -6.8, 2.2, 230, "smile", flap=(0.0, 1.0)))
shot("S63", "L51", fc(0.5, 11.0, 10, 2.4, 30), A("me", 0.5, 11.0, 10, "wide"), env=("rain", 1.0))
shot("S64", "L52", fc(0.5, 11.0, 0, 1.7, 34, head=1.65), A("me", 0.5, 11.0, 0, "worried"))
shot("S65", "L53", move(([1.8, 12.5, 0.6], [IL, 16.2, 1.4]), ([1.4, 12.8, 1.2], [IL, 16.2, 3.8]), 22),
     A("ilan", IL, 16.05, 0, "worried", **SEATED_ILAN))
cue("L53", "mem", on=True)
cue("L54", "mem", on=False)
cue("L54", "door", open=1)
stack("dman", 3, "L54-0.01", "set")
stack("dman", 4, "L54+0.2", "land")
sf("L54+0.2", "click", -12)
shot("S66", "L54", fc(-9.9, 4.15, 90, 2.5, 34, head=1.75, hp=0.5), A("dman", -9.9, 4.15, 180, "grin"),
     A("dwoman", -9.9, 5.25, 0, "grin"), env=("rain", 0.3))
cue("L55", "door", open=0)
shot("S67", "L55", still([0.4, 8.6, 0.5], [0.4, 11.6, 0.35], 28), A("me", 0.4, 12.4, 0, "worried", head=[0, 25]))
# ---- 9  the turn (L56 to L66)
shot("S68", "L56", still([2.6, 9.2, 1.6], [0.2, 15.4, 1.1], 24),
     A("me", 0.4, 11.2, 0, "worried", walk=(ME, 15.6)), A("ilan", IL, 16.05, 0, "worried", **SEATED_ILAN), step=2)
shot("S69", "L57", still([1.4, 14.4, 1.1], [0.2, 17.0, 1.1], 28),
     A("me", ME, SEATY, 0, "worried", z=SIT, sit=True),
     A("ilan", IL, SEATY, 0, "worried", z=SIT, sit=True, bend=40, head=[0, 22], cap=False))
shot("S70", "L58", still([-1.0, 11.5, 1.3], [0.3, 16.6, 1.9], 26),
     A("me", ME, 16.5, 0, "grin", z=0.45),
     A("ilan", IL, SEATY, 0, "worried", z=SIT, sit=True, bend=40, head=[0, 22], cap=False))
stack("me", 0, 0)
BG = [A("varga", -3.2, 11.0, 180, "grin"), A("ode", 3.0, 11.6, 180, "grin"), A("landlady", 0.2, 9.4, 180, "smile"),
      A("folk1", -5.0, 9.0, 180, "wide"), A("folk4", 4.8, 9.2, 180, "grin"), A("folk6", -1.8, 8.0, 180, "wide")]
shot("S71", "L59", still([0.0, 3.2, 1.9], [0.0, 15.8, 2.5], 24),
     A("me", ME, 16.5, 0, "grin", z=0.45), A("ilan", IL, SEATY, 0, "worried", z=SIT, sit=True, bend=20, head=[0, 10], cap=False),
     *BG, env=("rain", 0.3))
arc("ilan", "me", "L59.3", 0.6)
shot("S72", "L59.4", fc(ME, 16.5, 0, 4.2, 30, head=1.75 + 0.45, hp=0.5),
     A("me", ME, 16.5, 0, "wide", z=0.45), A("ilan", IL, SEATY, 0, "worried", z=SIT, sit=True, bend=20, head=[0, 10], cap=False))
shot("S73", "L60", still([0.5, 14.9, 1.6], [2.8, 11.8, 1.5], 30),
     A("ode", 2.8, 11.8, 215, "grin"), A("folk4", 4.2, 10.4, 200, "grin"))
arc("ilan", "me", "L60.2", 0.6)
sf("L60.2+0.6", "click", -12)
shot("S74", "L61", still([-0.3, 14.9, 1.6], [-2.6, 10.8, 1.5], 30),
     A("landlady", -2.6, 10.8, 151, "smile"), A("folk1", -4.0, 11.6, 140, "wide"))
arc("ilan", "me", "L61.1", 0.6)
sf("L61.1+0.6", "click", -12)
shot("S75", "L62", still([0.0, 3.2, 1.9], [0.0, 15.8, 2.5], 24),
     A("me", ME, 16.5, 0, "grin", z=0.45), A("ilan", IL, SEATY, 0, "worried", z=SIT, sit=True, bend=10, head=[0, 5], cap=False),
     *BG)
cue("L62", "doors", open=1)
for i, ref in enumerate(("L62", "L62+0.2", "L62+0.4", "L62+0.6", "L62+0.8", "L62+1.0", "L62+1.2", "L62+1.4")):
    arc("ilan", "me", ref, 0.55)
shot("S76", "L63", fc(IL, SEATY, 12, 3.6, 28, head=1.32, hp=0.4),
     A("ilan", IL, SEATY, 0, "smile", z=SIT, sit=True, head=[0, 0], cap=False))
stack("ilan", 2, "L63", "set")
stack("me", 12, "L63", "set")
stack("ilan", 1, "L63.1", "drop")
stack("ilan", 0, "L63.2", "drop")
shot("S77", "L64", fc(IL, SEATY, 12, 2.2, 34, head=1.32, hp=0.42), A("ilan", IL, SEATY, 0, "laugh", z=SIT, sit=True, head=[0, 0], cap=False))
shot("S78", "L65", still([0.4, 12.2, 1.2], [ME, 16.6, 2.6], 20),
     A("me", ME, SEATY, 0, "grin", z=SIT, sit=True), A("ilan", IL, SEATY, 0, "grin", z=SIT, sit=True, cap=False))
stack("me", 18, "L65", "set")
shot("S79", "L66", move(([1.9, 10.0, 1.6], [0.0, 16.4, 1.4]), ([1.2, 11.2, 1.5], [0.0, 16.4, 1.9]), 24),
     A("me", ME, SEATY, 0, "smile", z=SIT, sit=True), A("ilan", IL, SEATY, 0, "smile", z=SIT, sit=True, cap=False),
     env=("lowsun", 3.0, True))
# ---- 10  later, bright (L67 to L72)
shot("S80", "L67", fc(0.0, 16.7, 15, 5.5, 26, head=1.32, hp=0.4),
     A("me", ME, SEATY, 0, "smile", z=SIT, sit=True), A("ilan", IL, SEATY, 0, "laugh", z=SIT, sit=True, cap=True),
     env=("day", 0.4))
stack("me", 6, "L67", "set")
stack("ilan", 5, "L67", "set")
shot("S81", "L68", fm(dict(x=0.0, y=14.0, az=0, d=5.0, lens=22), dict(x=0.0, y=12.0, az=0, d=5.0, lens=22)),
     A("me", -0.55, 15.0, 0, "laugh", walk=(-0.55, 11.6), bend=22), A("ilan", 0.55, 15.1, 0, "laugh", walk=(0.55, 11.7), bend=22))
sf("L68+0.4", "thud", -14)
shot("S82", "L69", fc(-9.8, 4.2, 90, 3.8, 26),
     A("me", -9.4, 3.7, 270, "smile", arms=[0, 78]), A("varga", -9.9, 4.9, 180, "grin"))
stack("varga", 3, 0)
stack("me", 5, "L69+0.3", "drop")
cue("L69", "door", open=1)
cue("L70", "door", open=0)
shot("S83", "L69.2", fc(-9.3, 0.2, 90, 3.8, 24),
     A("ilan", -9.3, 0.9, 250, "grin", arms=[40, 40]), A("ode", -9.3, -0.5, 290, "laugh"))
stack("ode", 2, "L69.2+0.7", "land")
sf("L69.2+0.7", "click", -12)
shot("S84", "L70", still([2.5, -3.8, 2.2], [0.0, 8.0, 3.0], 17),
     A("me", -1.0, 4.5, 20, "smile"), A("ilan", 0.4, 4.4, 340, "smile"), A("folk1", -4.5, 4.6, 40, "grin"),
     A("folk2", -1.5, 7.0, 200, "neutral"), A("folk4", 3.5, 6.6, 250, "grin"), A("folk7", 5.5, 3.6, 100, "neutral"),
     A("folk6", 1.0, 9.2, 180, "grin"), A("dman", 4.4, 1.0, 180, "grin"))
cue("L70.2", "ilanlight", on=True)
cue("L71", "ilanlight", on=False)
cue("L70.2", "seatfill", e=250)
shot("S85", "L70.2", ARCHCAM, A("ilan", IL, 16.05, 0, "worried", **SEATED_ILAN), env=("raindim", 0.5))
stack("ilan", 22, "L70.2", "set")
cue("L71", "env", state="cold", dur=2.5)
cue("L71", "seatfill", e=300)
shot("S86", "L71", still([0.0, 14.4, 0.8], [0.0, 16.6, 0.45], 26))
shot("S87", "L72", still([0.62, 13.4, 0.35], [0.62, 15.4, 0.05], 24))
shot("S88", "L72.1", still([0.0, 9.0, 1.3], [0.0, 16.6, 1.0], 28))

# ================================================================================================== BUILD
refs = [s["ref"] for s in shots]
acting = {w: [] for w in cast}
staged_by = {}
for i, s in enumerate(shots):
    nxt = refs[i + 1] if i + 1 < len(refs) else "end"
    for a in s["stage"]:
        staged_by.setdefault(a["who"], {})[i] = (a, nxt)

world = {w: [0.0, 0.0, 0.0] for w in cast}     # where the character is now
curpos = {w: [0.0, 0.0, 0.0] for w in cast}    # the acting `pos`
visible = {w: False for w in cast}
for w in cast:
    acting[w].append({"at": 0, "hidden": True, "pos": [0, 0, 0], "blend": 0})
for i, s in enumerate(shots):
    ref = refs[i]
    nxt = refs[i + 1] if i + 1 < len(refs) else "end"
    names = {a["who"] for a in s["stage"]}
    for w in cast:
        if w not in names and visible[w]:
            acting[w].append({"at": ref, "hidden": True, "blend": 0})
            visible[w] = False
    for a in s["stage"]:
        w = a["who"]
        cur = curpos[w]
        pl = [a["p"][k] - cur[k] for k in range(3)]
        key = {"at": ref, "pos": list(cur), "place": pl, "yaw": a["yaw"], "expr": a["expr"], "hidden": False, "blend": 0,
               "sit": bool(a.get("sit", False)), "bend": a.get("bend", 0), "head": a.get("head", [0, 0]),
               "arms": a.get("arms", [0, 0]), "side": a.get("side", [0, 0]), "stackfollow": a.get("stackfollow", 0.0)}
        if w == "ilan":
            key["cap"] = a.get("cap", not ("S47" <= shots[i]["id"] <= "S79"))
        acting[w].append(key)
        visible[w] = True
        world[w] = list(a["p"])
        if a.get("walk"):
            tx, ty = a["walk"]
            dx, dy = tx - world[w][0], ty - world[w][1]
            curpos[w] = [cur[0] + dx, cur[1] + dy, cur[2]]
            acting[w].append({"at": nxt, "pos": list(curpos[w])})
            world[w] = [tx, ty, a["p"][2]]
        if a.get("flap"):
            f0, f1 = a["flap"]
            acting[w].append({"from": plus(ref, f0), "to": plus(ref, f1), "mouth": [0.7, 0.7], "flap": True})
        if a.get("mouth"):
            f0, f1 = a["mouth"]
            acting[w].append({"from": plus(ref, f0), "to": plus(ref, f1), "mouth": [0.5, 0.5], "flap": True})

shots_out = []
for s in shots:
    d = {"id": s["id"], "cam": s["cam"], "hand": s["hand"], "step": s["step"]}
    if s["ref"] != 0:
        d["at"] = s["ref"]
    shots_out.append(d)

# initial state of every stack the montage does not set (set before the first shot's time 0)
for w, spec in cast.items():
    if spec.get("stack_cap") and not any(c["name"] == "stack" and c["who"] == w and c["at"] == 0 for c in cues):
        cues.append({"at": 0, "name": "stack", "who": w, "n": 0, "mode": "set"})
cues.sort(key=lambda c: 0 if c["at"] == 0 else 1)

# ---------------------------------------------------------------------------------------------------- sound
for at in ("L02.2+0.2",):
    pass
sf("L06", "thud", -26)
ambience = [
    {"kind": "water", "from": 0, "to": "L39", "lufs": -42},
    {"kind": "rain", "from": "L39", "to": "L66", "lufs": -30},
    {"kind": "drone", "from": "L31", "to": "end", "lufs": -36},
    {"kind": "wind", "from": "L66", "to": "L67", "lufs": -44},
    {"kind": "crickets", "from": "L80" if False else "L67", "to": "L69", "lufs": -46},
]

story = {
    "slug": "ep57-arch-seat",
    "title": "In this town, every favour you owe sits on your head as a gold block",
    "made_for_kids": False,
    "premise": "In a hill town every favour you owe sits on your head as a small gold block that lands the moment you say thanks and drops when you do a favour back. My head is bare because I never say thanks, my cousin Ilan carries the tallest stack in town, and every Saturday something sits in my half of the stone seat under the clock arch: a figure with one ordinary head and shoulders as wide as the whole seat.",
    "twist": "Every block on Ilan's head was a favour done for me: all summer the town quietly helped me, and because I never said thanks, Ilan went round after me and said it for me, so each block landed on him. The same rule undoes it, since a block lands on whoever says thanks, so when I say thanks myself the blocks arc from his head to mine, and the thing in my seat is gone the moment I sit.",
    "world": "a small hill town square in high summer: honey cobbles, a round stone fountain, a bakery with a mint and cream awning, a cafe, a bike repair stand, a bus shelter, painted house fronts, and a stone clock arch with a deep stone seat cut into its back wall, seen in sun, dusk and steady rain",
    "voice": {"voice": "am_adam", "tempo": 1.03, "rate": 1.45},
    "key_color": "#b48cff",
    "caption": {"ink": "#08090d", "stroke_add": 2, "shadow": 0.8},
    "key_stroke": 2,
    "gap": 0.12,
    "tail": LOOP,
    "look": {"fog": "#c8d4e0", "fog_density": 0.004, "fog_start": 14.0, "sky": "#9fcaf0", "sky_strength": 1.0,
             "exposure": 0.2, "flash_safe": True},
    "grade": {"shadows": [-0.02, 0.0, 0.03], "highlights": [0.03, 0.01, -0.02], "saturation": 1.05, "contrast": 1.05,
              "vignette": 0.28, "bloom": 0.2, "grain": 0.01},
    "rain_shots": [s["id"] for s in shots if ("S47" <= s["id"] <= "S79" and s["id"] not in ("S61", "S62")) or s["id"] == "S85"],
    "rain_gain": 0.8,
    "phonemes": {"Ilan": "ˈilɑn", "Varga": "vˈɑɹɡə"},
    "cast": cast,
    "lines": lines,
    "shots": shots_out,
    "acting": acting,
    "cues": cues,
    "fx": [],
    "music": {"root": 43, "mode": "lydian", "bpm": 104, "seed": 57,
              "sections": [
                  {"at": 0, "voices": ["piano", "pulse"], "energy": 0.55},
                  {"at": "L22", "voices": ["piano"], "energy": 0.3},
                  {"at": "L31", "voices": ["drone", "pad", "pulse"], "energy": 0.35},
                  {"at": "L39", "voices": ["drone", "pad"], "energy": 0.4},
                  {"at": "L48", "voices": ["drone", "pad", "pulse"], "energy": 0.5},
                  {"at": "L59", "voices": ["drone", "pulse", "piano"], "energy": 0.6},
                  {"at": "L64", "voices": ["drone", "piano", "pulse"], "energy": 0.5},
                  {"at": "L70", "voices": ["drone", "pad"], "energy": 0.3},
                  {"at": "L72", "voices": ["drone"], "energy": 0.2},
              ]},
    "sound": {"floor": "stone", "steps_db": -22, "ambience": ambience, "sfx": sfx,
              "music_drops": [["L22.3", "L23.1"], ["L42.3", "L43.1"], ["L47>-0.4", "L48"]]},
}
OUT.write_text(json.dumps(story, indent=1, ensure_ascii=False) + "\n")
print("wrote", OUT, f"({len(shots)} shots)")
