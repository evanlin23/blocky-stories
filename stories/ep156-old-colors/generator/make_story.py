"""Writes ../story.json for ep156 "Miss Your Old House And You Turn Its COLORS" (script.md, 2026-11-12, batch 15, warm).
Run: python stories/ep156-old-colors/generator/make_story.py

Words are in lines.json; places in ../layout.py (shared with set.py). A character facing -y has yaw 0, +x 90, +y 180,
-x -90. Cues (read by set.py): day (n: the calendar page), prints (the fridge fingerprints), curtain, print (the checked
print on the bench), rub (the blue rubbed on Mom's cardigan). Colour changes on people are stepped through cast
variants of one body (same acting keys), 0.2 s apart, so nothing ever blinks: Leo goes meb -> mf1 -> mf2 -> sw
over 0.6 s on the hug, the plaid man goes man1 -> man2 -> man3.
"""
import json
import math
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
sys.path.insert(0, str(HERE.parent.parent.parent))
import layout as G  # noqa: E402
from blocky import timeline as T  # noqa: E402

OUT = HERE.parent / "story.json"
REV = 2
orig_lines = json.loads((HERE / "lines.json").read_text())
lines, CHUNKMAP = T.split_lines(orig_lines)


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


D2R = math.pi / 180
X = {"neutral": "neutral", "uneasy": "worried", "stunned": "wide", "sad": "worried", "smile": "smile",
     "laugh": "laugh", "warm": "warm", "sheepish": "polite", "sly": "smirk"}

SKIN = "#c98f62"
BLUE_SKIN = "#86c4ee"


def mixc(a, b, u):
    ca = [int(a[i:i + 2], 16) for i in (1, 3, 5)]
    cb = [int(b[i:i + 2], 16) for i in (1, 3, 5)]
    return "#%02x%02x%02x" % tuple(int(round(ca[i] + (cb[i] - ca[i]) * u)) for i in range(3))


def person(skin, shirt, pants, shoes, hair="cap", hair_c="#15151a", hat="none", eyes="round", sleeves="long", **kw):
    d = {"age": "adult", "skin": skin, "shirt": shirt, "pants": pants, "shoes": shoes, "sleeves": sleeves,
         "hair": hair, "hair_c": hair_c, "hat": hat, "face": {"eyes": eyes, "brows": True, "ink": "#1c120c"}}
    d.update(kw)
    return d


def leo(skin, **kw):
    return person(skin, "#8a4fa3", "#3a4a6a", "#f2f2f2", hair="cap", hair_c="#5a3a22", age="teen", height=1.04,
                  extras=["hooddown"], collar="#6e3a86", **kw)


cast = {
    # Leo, 17: a tall brown block quiff (set.py), light brown skin, a plum hoodie; from L13 three sweaters (plum over
    # orange over oat: bands at the collar, hem and cuffs, set.py) in a bulkier body. The blue ones are the reveal.
    "me": leo(SKIN),
    "sw": leo(SKIN, width=1.08, body_width=1.1),
    "mf2": leo(mixc(SKIN, BLUE_SKIN, 0.33), width=1.08, body_width=1.1),
    "mf1": leo(mixc(SKIN, BLUE_SKIN, 0.66), width=1.08, body_width=1.1),
    "meb": leo(BLUE_SKIN, width=1.08, body_width=1.1),
    # Mom (Nell), forties: a big curly black bun (set.py), the same skin, a coral cardigan over a navy shirt (set.py)
    "mom": person(SKIN, "#f08a74", "#46506a", "#f2f2f2", hair="cap", eyes="lashes", collar="#2e3f73", height=0.95),
    # Mr. Pratt, sixties: bald, a white mustache (set.py), teal all over, a waterline and portholes (set.py)
    "pratt": person("#1fa5b8", "#1b97aa", "#17828f", "#2e3f73", hair="none", sleeves="long", width=1.04),
    # the bench woman: terracotta and white checks all over, a big scarf
    "woman": person("#e0b08a", "#c96f4a", "#c96f4a", "#fffaf0", hair="long", hair_c="#5a3a22", eyes="lashes",
                    collar="#fffaf0", pattern="plaid", pattern_c="#fffaf0", pants_pattern="plaid",
                    pants_pattern_c="#fffaf0", height=0.95),
    # the plaid man (three washes) and his grown daughter
    "man1": person("#d9b48a", "#3f9a5a", "#3f9a5a", "#f2f2f2", hair="buzz", hair_c="#a9a9b2", pattern="plaid",
                   pattern_c="#f2f2c0", pants_pattern="plaid", pants_pattern_c="#f2f2c0", height=1.02),
    "man2": person("#d9b48a", "#8bbf94", "#8bbf94", "#f2f2f2", hair="buzz", hair_c="#a9a9b2", pattern="plaid",
                   pattern_c="#e8ecd8", pants_pattern="plaid", pants_pattern_c="#e8ecd8", height=1.02),
    "man3": person("#d9b48a", "#d9d2b0", "#6a6050", "#f2f2f2", hair="buzz", hair_c="#a9a9b2", height=1.02),
    "girl": person("#c58e64", "#c01e2a", "#3a4a6a", "#f2f2f2", hair="long", hair_c="#2a1d15", eyes="lashes",
                   height=0.97),
}
LEOS = ["me", "sw", "mf2", "mf1", "meb"]
MAN = ["man1", "man2", "man3"]
acting = {n: [] for n in cast}
last = {n: [0, 0, 0] for n in cast}
vis = set()
cues = []
SH = []


def key(who, at, pos=None, **kw):
    p = list(pos) if pos is not None else list(last[who])
    if len(p) == 2:
        p.append(0.0)
    if "expr" in kw:
        kw["expr"] = X.get(kw["expr"], kw["expr"])
    acting[who].append({"at": at, "pos": p, **kw})
    last[who] = p


def cut(who, at, pos=None, **kw):
    """A key that takes effect at once: a pose or place that changes on a cut."""
    p = list(pos) if pos is not None else list(last[who])
    if len(p) == 2:
        p.append(0.0)
    acting[who].append({"at": at, "pos": list(last[who]), "blend": 0.0})
    key(who, at, p, blend=0.0, **kw)


def show(at, *names):
    for n in cast:
        if n in names and n not in vis:
            vis.add(n)
            cut(n, at, hidden=False)
        elif n not in names and n in vis:
            vis.discard(n)
            cut(n, at, hidden=True)


def pose(yaw=0, expr="neutral", **kw):
    d = dict(yaw=yaw, expr=expr, head=[0, 0], arms=[0, 0], side=[0, 0])
    d.update(kw)
    return d


def place(at, who, pos, yaw=0, expr="neutral", **kw):
    """Cut `who` to pos with a pose at `at`, visible."""
    if who not in vis:
        vis.add(who)
        cut(who, at, hidden=False)
    cut(who, at, [pos[0], pos[1], pos[2] if len(pos) > 2 else 0.0], **pose(yaw, expr, **kw))


def mouth(who, a, b, amt=0.4):
    acting[who].append({"from": a, "to": b, "mouth": [amt, amt], "flap": True})


def cue(at, name, **kw):
    cues.append({"at": at, "name": name, **kw})


def cam(tx, ty, tz, w, az, lens, cz=None, push=None):
    """A camera looking at (tx, ty, tz) from az degrees round from the south, far enough off that the frame is w
    metres wide there."""
    def at_(ww, tzz, czz):
        d = ww * 16 / 9 * lens / 24
        return [round(tx + d * math.sin(az * D2R), 3), round(ty - d * math.cos(az * D2R), 3),
                czz if czz is not None else tzz], [tx, ty, tzz]
    p, t_ = at_(w, tz, cz)
    keys = [[0, p, t_, lens]]
    if push:
        w2 = w - (w - push[0]) * 2.2
        p2, t2 = at_(w2, push[1], None if cz is None else cz + (push[1] - tz))
        keys.append([1, p2, t2, lens])
    return keys


def camp(pos, tgt, lens, pos2=None, tgt2=None):
    keys = [[0, list(pos), list(tgt), lens]]
    if pos2 is not None or tgt2 is not None:
        keys.append([1, list(pos2 or pos), list(tgt2 or tgt), lens])
    return keys


def shot(sid, at, camera, **kw):
    SH.append((sid, at, camera, kw))


for who in cast:
    key(who, 0, [0, 0, 0], yaw=0, expr="neutral", head=[0, 0], arms=[0, 0], side=[0, 0], hidden=True)
cue(0, "day", n=1)
cue(0, "prints", v=0.0)
cue(0, "curtain", v=0.0)
cue(0, "print", v=0.0)
cue(0, "rub", v=0.0)

# ----------------------------------------------------------------------------------------------- the places
LX, LY = -0.72, 0.35           # me at the table (facing east)
MX, MY = 0.72, 0.35            # Mom at the table (facing west)
LEO_P, MOM_P = (LX, LY), (MX, MY)


def leo_at(at, who="me", pos=LEO_P, yaw=90, expr="neutral", **kw):
    place(at, who, pos, yaw, expr, **kw)


def mom_at(at, pos=MOM_P, yaw=-90, expr="neutral", **kw):
    place(at, "mom", pos, yaw, expr, **kw)


TABLE_HANDS = [36, 36]


def face_tz(face_z, w):
    """Where to aim so the face sits about 35% down the frame (clear of the caption band)."""
    return round(face_z - 0.15 * w * 16 / 9, 3)


def shot_mom_win(sid, at, w=1.7):
    tz = face_tz(1.5, w)
    shot(sid, at, cam(-3.3, 0.5, tz, w, 80, 34, cz=tz))


def shot_leo(sid, at, w=1.8, az=45, lens=34, fz=1.62, **kw):
    tz = face_tz(fz, w)
    shot(sid, at, cam(LX, LY, tz, w, az, lens, cz=tz), **kw)


def shot_mom(sid, at, w=1.8, az=-45, lens=34, fz=1.5, **kw):
    tz = face_tz(fz, w)
    shot(sid, at, cam(MX, MY, tz, w, az, lens, cz=tz), **kw)


# ===== helpers for the table views
TABLE_SIDE = [10, 10]


def mom_hands(at, expr="neutral", **kw):
    mom_at(at, expr=expr, arms=TABLE_HANDS, side=TABLE_SIDE, **kw)


def shot_hands(sid, at, w=1.5, az=50, tz=1.3, cz=1.0, lens=28, tx=0.0, ty=0.35, push=None, **kw):
    """Low 3/4 from Mom's side: her flat palms on the bare table in the lower third, Leo's whole head beside them."""
    c = cam(tx, ty, tz, w, az, lens, cz=cz)
    if push:
        c = c + [[1, [round(c[0][1][0] + push[0], 3), round(c[0][1][1] + push[1], 3), c[0][1][2]], c[0][2], lens]]
    shot(sid, at, c, **kw)


# ===== 01 the rule (L01): Mom's hands palms up on the table, my face beside them, checking
show(0, "me", "mom")
leo_at(0, "me", expr="uneasy", head=[0, 22], arms=[0, 0])
mom_hands(0, expr="neutral")
shot_hands("S01a", 0, w=1.7, az=25, tx=-0.15)
# S01b: I look at my own hands by the fridge: the real "1" page and the pencil tally at my waist
show("L01.2", "me")
place("L01.2", "me", (1.35, 2.0), 10, "neutral", arms=[40, 40], head=[0, 28])
shot("S01b", "L01.2", cam(2.0, 2.5, 1.25, 1.8, -20, 28, cz=1.25))

# ===== 02 mine (L02): Mom at the window, waist up
show("L02", "mom")
place("L02", "mom", (-3.3, 0.5), 60, "sad", arms=[0, 0])
shot("S02a", "L02", cam(-3.3, 0.5, face_tz(1.5, 1.5), 1.5, 100, 28, cz=face_tz(1.5, 1.5)))
shot("S02b", "L02.2", cam(-3.3, 0.5, face_tz(1.5, 1.1), 1.1, 60, 34, cz=face_tz(1.5, 1.1)))

# ===== 03 the stakes (L03): the photo from above, my morning check
cue("L03", "photo", v=1.0)
cue("L03.3", "photo", v=0.0)
show("L03")
shot("S03a", "L03", camp([0.0, -1.72, 2.5], [0.0, -0.2, 0.8], 28, pos2=[0.0, -1.5, 2.2], tgt2=[0.0, -0.2, 0.8]), hold_=True)
show("L03.3", "me", "mom")
leo_at("L03.3", "me", expr="uneasy", head=[0, 24])
mom_hands("L03.3", expr="neutral")
shot_hands("S03b", "L03.3", w=2.6, az=-25, tz=1.2, cz=0.95, tx=-0.1)

# ===== 04, 05 Mr. Pratt (L04, L05)
PRATT_P = (G.PRATT[0] + 0.4, 3.35, 0.3)
show("L04", "pratt")
place("L04", "pratt", PRATT_P, 0, "smile", arms=[0, 120])
key("pratt", "L04+0.5", PRATT_P, yaw=0, expr="smile", arms=[0, 145], blend=0.3)
key("pratt", "L04+1.0", PRATT_P, yaw=0, expr="smile", arms=[0, 115], blend=0.3)
shot("S04", "L04", cam(60.4, 3.35, 0.95, 2.9, 0, 28, cz=1.9, push=(2.6, 0.95)))
place("L05", "pratt", PRATT_P, 0, "laugh", arms=[0, 0], head=[0, 18])
key("pratt", "L05+0.5", PRATT_P, yaw=0, expr="laugh", arms=[0, 62], head=[0, 28], blend=0.3)
key("pratt", "L05.1", PRATT_P, yaw=0, expr="laugh", arms=[0, 0], side=[30, 30], head=[0, 0], blend=0.3)
shot("S05", "L05", cam(60.4, 3.35, 0.95, 2.7, 0, 28, cz=1.7))

# ===== 06 it rubs off (L06): the bench woman and the big checked print she leaves on the bench back
WOMAN_P = (1.35, 62.9, 0.0)
show("L06", "woman")
place("L06", "woman", WOMAN_P, 0, "smile", arms=[0, 0])
key("woman", "L06+0.3", WOMAN_P, yaw=0, expr="smile", arms=[0, 38], blend=0.4)
cue("L06+0.5", "print", v=1.0)
shot("S06a", "L06", camp([0.7, 58.9, 2.3], [0.7, 63.1, 0.9], 28, pos2=[0.7, 59.6, 2.1], tgt2=[0.75, 63.1, 1.0]))
shot("S06b", "L06.2", cam(WOMAN_P[0], 62.7, face_tz(1.5, 1.7), 1.7, 8, 34, cz=face_tz(1.5, 1.7)))
place("L06.2", "woman", WOMAN_P, 0, "smile", arms=[0, 0], head=[0, 0])

# ===== 07 a hug washes it out (L07): the plaid man and his grown daughter, both faces front 3/4
show("L07", "man1", "girl")
for m_ in MAN:
    cut(m_, "L07", (13.3, 62.0), **pose(60, "smile", arms=[0, 0], keep_yaw=True))
    key(m_, "L07+0.45", (14.25, 62.5), yaw=50, expr="smile", arms=[0, 0], blend=0.45)
    key(m_, "L07+0.5", (14.25, 62.5), yaw=50, expr="laugh", arms=[70, 70], side=[22, 22], blend=0.3)
place("L07", "girl", (15.2, 62.5), -80, "smile", arms=[0, 0])
key("girl", "L07+0.1", (15.2, 62.5), yaw=-50, expr="smile", arms=[78, 78], side=[28, 28], blend=0.45)
key("girl", "L07+0.5", (15.2, 62.5), yaw=-50, expr="laugh", arms=[70, 70], side=[22, 22], blend=0.3)
# the plaid steps down to plain over 0.6 s, a third at a time, 0.3 s apart
cut("man2", "L07+0.6", hidden=True)
cut("man3", "L07+0.6", hidden=True)
cut("man2", "L07+0.75", hidden=False)
cut("man1", "L07+0.75", hidden=True)
cut("man3", "L07+1.05", hidden=False)
cut("man2", "L07+1.05", hidden=True)
shot("S07", "L07", cam(14.7, 62.5, face_tz(1.55, 1.9), 1.9, 0, 28, cz=face_tz(1.55, 1.9)))

# ===== 08 day 3: the first dodge (L08)
cue("L08", "day", n=3)
show("L08", "mom")
mom_at("L08", expr="smile", arms=[0, 0])
key("mom", "L08+0.45", MOM_P, yaw=-90, expr="smile", arms=[82, 82], side=[30, 30], blend=0.5)
shot_mom("S08a", "L08", w=1.9)
show("L08.2", "me")
leo_at("L08.2", "me", expr="neutral", arms=[0, 0], keep_yaw=True)
key("me", "L08.2+0.8", (LX - 0.55, LY), yaw=90, expr="sheepish", arms=[0, 0], head=[0, 8], blend=0.4)
shot("S08b", "L08.2", cam(LX - 0.35, LY, face_tz(1.62, 2.0), 2.0, 45, 34, cz=face_tz(1.62, 2.0)))

# ===== 09 day 9: the swing (L09)
cue("L09", "day", n=9)
SWX, SWY = G.PORCH[0], G.PORCH[1] - 0.3
show("L09", "me")
place("L09", "me", (SWX + 0.62, SWY - 0.8), 0, "smile", arms=[0, 0])
shot("S09a", "L09", cam(SWX + 0.26, SWY, 1.65, 2.6, 0, 28, cz=1.9))
show("L09.2-0.27", "mom")
place("L09.2-0.27", "mom", (4.0, G.DOOR_Y), -90, "smile", arms=[0, 0])
shot("S09b", "L09.2-0.27", cam(4.0, G.DOOR_Y, face_tz(1.5, 1.9), 1.9, -95, 34, cz=face_tz(1.5, 1.9)))

# ===== 10 day 16: the fingerprints (L10)
cue("L10", "day", n=16)
cue("L10", "prints", v=1.0)
show("L10", "me")
place("L10", "me", (1.35, 2.05), 100, "stunned", arms=[0, 0], head=[-30, 4])
shot("S10a", "L10", cam(1.5, 2.45, 1.35, 1.7, 12, 28, cz=1.35))
show("L10.3-0.43", "me", "mom")
leo_at("L10.3-0.43", "me", expr="sheepish", head=[0, 22])
mom_hands("L10.3-0.43", expr="neutral")
shot_hands("S10b", "L10.3-0.43", w=2.3, az=-25, tz=1.15, cz=0.95, tx=-0.1)
shot("S10c", "L10.4", cam(LX, LY, face_tz(1.62, 1.2), 1.2, 45, 34, cz=face_tz(1.62, 1.2)))

# ===== 11 day 23: the curtains (L11), then one dodge
cue("L11", "day", n=23)
cue("L11", "curtain", v=1.0)
show("L11", "me")
place("L11", "me", (-3.15, 0.1), 80, "smile", arms=[0, 0])
shot("S11a", "L11", camp([-1.9, -2.4, 1.2], [-3.4, 0.2, 1.3], 28, pos2=[-1.9, -2.4, 1.2], tgt2=[-3.4, 0.2, 2.0]))
show("L11.2", "me", "mom")
leo_at("L11.2", "me", expr="neutral", arms=[0, 0], keep_yaw=True)
mom_at("L11.2", expr="warm", arms=[0, 0])
key("mom", "L11.2+0.3", MOM_P, yaw=-90, expr="warm", arms=[82, 82], side=[30, 30], blend=0.5)
key("me", "L11.2+0.85", (LX - 0.55, LY), yaw=90, expr="sheepish", arms=[0, 0], blend=0.4)
shot("S11b", "L11.2", cam(LX - 0.2, LY, face_tz(1.62, 2.2), 2.2, 45, 34, cz=face_tz(1.62, 2.2)))

# ===== 12 day 31: the pillowcase (L12)
cue("L12", "day", n=31)
RX, RY = G.ROOM
show("L12", "me")
place("L12", "me", (RX + 1.15, RY + 2.7), -50, "uneasy", arms=[0, 0], head=[0, 14])
W12 = 2.0
shot("S12a", "L12", cam(RX + 0.32 + 0.2 * W12 + 0.02, RY + 3.05, 0.95, W12, -30, 28, cz=1.25))
key("me", "L12.3", (RX + 1.15, RY + 2.7), yaw=-50, expr="sly", arms=[0, 0], head=[0, 6], blend=0.3)
shot("S12b", "L12.3", cam(RX + 1.2, RY + 2.7, face_tz(1.62, 1.8), 1.8, -42, 34, cz=face_tz(1.62, 1.8)))

# ===== 13 day 40: three sweaters (L13)
cue("L13", "day", n=40)
show("L13", "sw", "mom")
leo_at("L13", "sw", expr="uneasy", arms=TABLE_HANDS)
mom_at("L13", expr="neutral", arms=[0, 0])
acting["sw"].append({"from": "L13", "to": "L13>", "tremble": 2.0})
shot("S13a", "L13", cam(LX, LY, 1.2, 1.5, 10, 28, cz=1.2))
shot("S13b", "L13.2", cam(LX, LY, 1.2, 1.3, 20, 28, cz=1.2))

# ===== 14 Mr. Pratt asks (L14)
show("L14", "pratt")
place("L14", "pratt", PRATT_P, 0, "smile", arms=[0, 0], head=[0, 0])
key("pratt", "L14+0.5", PRATT_P, yaw=0, expr="smile", arms=[0, 100], blend=0.4)
shot("S14a", "L14", cam(60.4, 3.35, face_tz(1.62, 2.0), 2.0, 0, 28, cz=1.7))
show("L14.2-0.27", "sw")
place("L14.2-0.27", "sw", (60.0, -0.1), 180, "neutral", arms=[0, 0])
shot("S14b", "L14.2-0.27", camp([60.4, 3.9, 2.0], [60.0, -0.1, 1.3], 28, pos2=[60.3, 3.4, 2.0]))

# ===== 15 day 41: nothing (L15)
cue("L15", "day", n=41)
show("L15", "sw", "mom")
leo_at("L15", "sw", expr="neutral", arms=[0, 0])
mom_at("L15", expr="neutral", arms=[0, 0])
shot_leo("S15a", "L15", w=2.0)
show("L15.4", "mom")
mom_at("L15.4", expr="warm", arms=[0, 0])
shot_mom("S15b", "L15.4", w=1.7)

# ===== 16 the hands (L16): closer in, hands meet over the table
LX2, MX2 = -0.5, 0.5
show("L16", "sw", "mom")
cut("sw", "L16", (LX2, LY), **pose(90, "uneasy", arms=[0, 0]))
cut("mom", "L16", (MX2, MY), **pose(-90, "warm", arms=[0, 0]))
key("sw", "L16+0.2", (LX2, LY), yaw=90, expr="uneasy", arms=[58, 58], blend=0.5)
key("mom", "L16+0.7", (MX2, MY), yaw=-90, expr="warm", arms=[26, 26], blend=0.2)
key("mom", "L16+1.0", (MX2, MY), yaw=-90, expr="warm", arms=[56, 56], blend=0.66)
shot("S16a", "L16", camp([0.0, 0.1, 2.75], [0.0, 0.35, 0.8], 16, pos2=[0.0, 0.1, 2.5], tgt2=[0.0, 0.35, 0.8]))

# ===== 17 the reveal (L17): Mom's face alone, then the picture from her eyes
show("L16.3-0.1", "mom")
mouth("mom", "L17", "L17.1", 0.35)
shot_mom("S17a", "L16.3-0.1", w=1.7)
show("L17.1", "meb")
place("L17.1", "meb", (LX2, LY), 90, "wide", arms=[58, 58])
key("meb", "L17.1+0.2", (LX2, LY), yaw=90, expr="wide", arms=[58, 58], head=[0, -4], blend=0.5)
shot("S17b", "L17.1", camp([MX2 + 1.4, MY - 0.8, 1.6], [LX2, LY - 0.12, 1.3], 24, pos2=[MX2 + 1.1, MY - 0.7, 1.6]))

# ===== 18 the hug washes it out (L18): one shot, both faces, the blue goes out in three steps 0.3 s apart
cue("L18", "day", n=41)
HUG_L, HUG_M = (1.2, 1.7), (1.8, 1.7)
S18 = "L18.1+0.15"
show(S18, "meb", "mom")
cut("meb", S18, HUG_L, **pose(55, "smile", arms=[75, 75], side=[25, 25]))
cut("mom", S18, HUG_M, **pose(-55, "laugh", arms=[75, 75], side=[25, 25]))
for new, old, dt in (("mf1", "meb", 0.45), ("mf2", "mf1", 0.75), ("sw", "mf2", 1.05)):
    place(f"L18.1+{dt}", new, HUG_L, 55, "laugh", arms=[75, 75], side=[25, 25])
    cut(old, f"L18.1+{dt}", hidden=True)
    vis.discard(old)
cue("L18.1+0.55", "rub", v=1.0)
shot("S18", S18, camp([1.5, -1.3, 1.5], [1.5, 1.7, 1.42], 28, pos2=[1.5, -0.9, 1.5], tgt2=[1.5, 1.7, 1.42]))

# ----------------------------------------------------------------------------------------------- finish
remap_all(cues)
for k_ in acting.values():
    remap_all(k_)
shots = []
HOLD = []
for i, (sid, at, camera, kw) in enumerate(SH):
    if kw.pop("hold_", False):
        HOLD.append(sid)
    if len(camera) == 1:       # a slow dolly in on every shot whose camera was still: motion the preview can read
        _, p0, t0, ln = camera[0]
        camera = camera + [[1, [round(p0[j] + 0.12 * (t0[j] - p0[j]), 3) for j in range(3)], list(t0), ln]]
    s = {"id": sid, "cam": camera, "step": 2}
    if i:
        s["at"] = remap(at)
    s.update({k: v for k, v in kw.items() if not k.startswith("_")})
    shots.append(s)

sfx = [
    {"at": "L01.1", "kind": "whoosh", "db": -22},                        # the brush stroke on COLORS
    {"at": "L08.3", "kind": "whoosh", "db": -22},                        # the first dodge
    {"at": "L10.1", "kind": "thud", "db": -16},                          # the fridge door
    {"at": "L11.3", "kind": "whoosh", "db": -22},                        # the second dodge
    {"at": "L18.1", "kind": "riser", "db": -22, "dur": 0.9},          # the colours rinse out
]
music = {
    "root": 56, "mode": "major", "bpm": 132, "seed": 156,
    "sections": [
        {"at": 0, "voices": ["piano", "pad"], "energy": 0.45},
        {"at": "L08", "voices": ["piano", "pulse", "pad"], "energy": 0.5},
        {"at": "L15", "voices": ["piano"], "energy": 0.3},
        {"at": "L17", "voices": ["pad"], "energy": 0.2},
        {"at": "L18", "voices": ["piano", "pad", "musicbox"], "energy": 0.6},
    ],
}
sound = {
    "floor": "wood", "steps_db": -22,
    "ambience": [],
    "sfx": sfx,
    "music_drops": [{"from": "L17", "to": "L17>"}],
    "rev": REV,
}
remap_all(sfx)
remap_all(music["sections"])
remap_all(sound["music_drops"])
polish = {"reveal": ["L17.1"], "twist": "L17", "emph": ["L01.1", "L05.1", "L10.1", "L12.1", "L15.2", "L17.1", "L18.1"],
          "quiet": [["L18", "L18>"]], "hold": HOLD + ["S17b"], "sway": ["S13a", "S13b"]}
polish["emph"] = [remap(x) for x in polish["emph"]]
polish["reveal"] = [remap(x) for x in polish["reveal"]]
polish["twist"] = remap(polish["twist"])
polish["quiet"] = [[remap(a), remap(b)] for a, b in polish["quiet"]]
story = {
    "slug": "ep156-old-colors",
    "title": "Miss Your Old House And You Turn Its COLORS \U0001F3E0",
    "made_for_kids": False,
    "premise": ("In our town, if you miss your old house you slowly turn its colors and never see it on yourself, "
                "so after a move a seventeen-year-old checks his mom's hands every morning and puts the old house "
                "back for her."),
    "twist": ("The one going sky blue with yellow stripes is me, the teen who dodges every hug, and a hug from "
              "home is what washes it out."),
    "world": ("Mom's sunny new kitchen across town, a back porch with the old house's sky-blue swing, the neighbor's "
              "porch over a white fence, and a street where people turn their old houses' colors."),
    "voice": {"voice": "am_adam", "tempo": 1.03, "rate": 1.45},
    "key_color": "#b06ad8",
    "gap": 0.15,
    "tail": 0.9,
    "fade_in": False,
    "fade_out": False,
    "rev": REV,
    "look": {"style": "closer", "fog": "#e8f3ff", "fog_density": 0.0008, "fog_start": 80.0, "sky": "#8fd0ff",
             "sky_strength": 0.7, "exposure": 0.0, "flash_safe": True, "polish": polish},
    "grade": {"shadows": [0.0, 0.0, 0.01], "highlights": [0.025, 0.012, -0.015], "saturation": 1.05,
              "contrast": 1.03, "vignette": 0.1, "bloom": 0.12, "grain": 0.008},
    "hud": {"object": "tag", "at": [-0.42, 0.62], "size": 0.5},
    "cast": cast,
    "lines": lines,
    "shots": shots,
    "acting": acting,
    "cues": cues,
    "fx": [],
    "music": music,
    "sound": sound,
    "set_moves": [],
    "framing_ok": ["S03a", "S08b", "S11b", "S15a", "S16a"],
    "frames_ok": [],
    "staging_ok": ["S07/close", "S16a/close", "S18/close"],
    "phonemes": {"Nell": "nˈɛl"},
    "homophones": {"stripey": "stripy"},
}
OUT.write_text(json.dumps(story, indent=1, ensure_ascii=False) + "\n")
print("wrote", OUT, f"({len(shots)} shots, {len(cues)} cues)")
