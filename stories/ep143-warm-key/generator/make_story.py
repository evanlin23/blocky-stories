"""Writes ../story.json for ep143 "My Old House Key Went WARM" (script.md, 2026-11-12, batch 15, warm lane).
Run: python stories/ep143-warm-key/generator/make_story.py

Words are in lines.json; places in ../layout.py (shared with set.py). A character facing -y has yaw 0, +x 90,
+y 180, -x -90. Cues (read by set.py): pips (the tag's lit pips, 1..5), heat (the key's warmth, 0..5), key (where the
key and its dinosaur are: mode hang | hand | lock | hook2 | none, who, anchor), mitt, boxes, door, sticker, curtain,
swing, phone. Nothing ever blinks or pulses: every light rises over at least 0.3 s.
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
REV = 11
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
     "laugh": "laugh", "scared": "scared", "warm": "warm", "sheepish": "polite", "sly": "smirk"}


def person(skin, shirt, pants, shoes, hair="cap", hair_c="#15151a", hat="none", eyes="round", sleeves="long",
           **kw):
    d = {"age": "adult", "skin": skin, "shirt": shirt, "pants": pants, "shoes": shoes, "sleeves": sleeves,
         "hair": hair, "hair_c": hair_c, "hat": hat, "face": {"eyes": eyes, "brows": True, "ink": "#1c120c"}}
    d.update(kw)
    return d


SKIN = "#d9b48a"
cast = {
    # me: a man of 27, short spiky black crop, light olive skin, navy windbreaker, khakis
    "me": person(SKIN, "#26386a", "#c9b58a", "#f2f2f2", hair="spiky", collar="#1c2a52"),
    # Jess, 31: long black hair (a ponytail in set.py), the same skin, a red sweater, round earrings (set.py)
    "jess": person(SKIN, "#d8322f", "#3a4a6a", "#f2f2f2", hair="long", eyes="lashes", collar="#f4e6dc"),
    # Mom: short gray hair, a yellow cardigan
    "mom": person("#e6c19a", "#f2c84a", "#6a5a8a", "#f2f2f2", hair="cap", hair_c="#b9b9c2", eyes="lashes",
                  collar="#fff6d8"),
    # Dad: a gray beard (set.py), a green polo
    "dad": person("#d9b48a", "#3f9a5a", "#b9a47a", "#f2f2f2", hair="buzz", hair_c="#a9a9b2", sleeves="short",
                  collar="#2f7a46", width=1.05),
    "pizza": person("#c58e64", "#7a1f2e", "#2a2a34", "#2a2a30", hair="cap", hat="ballcap", hat_c="#d8322f",
                    sleeves="short"),
    "buddy": person("#a96f4a", "#8a8f99", "#3a3a48", "#f2f2f2", hair="buzz", hair_c="#15151a", sleeves="none"),
}
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


def faceyaw(frm, to):
    return math.degrees(math.atan2(to[0] - frm[0], -(to[1] - frm[1])))


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


def keycue(at, mode, who="me", dur=0.0, **kw):
    cue(at, "key", mode=mode, who=who, **kw)


for who in cast:
    key(who, 0, [0, 0, 0], yaw=0, expr="neutral", head=[0, 0], arms=[0, 0], side=[0, 0], hidden=True)
cue(0, "pips", n=1)
cue(0, "heat", v=1.6)
cue(0, "key", mode="hang", who="me")
cue(0, "door", v=0.0)
cue(0, "sticker", v=0.0)
cue(0, "mitt", v=0.0)
cue(0, "boxes", v=0.0)
cue(0, "phone", v=0.0)
cue(0, "curtain", v=0.0)
cue(0, "swing", v=0.0)
cue(0, "lock", v=0.0)

# ----------------------------------------------------------------------------------------------- the stages
ZP = G.ZP
ZH = G.ZH
HX, HY = G.HOUSE
ME_A = G.ME_A
# the face + key frame used at S01a and again at S32
APT_TGT = (0.0, 2.7, 1.5)


def me_a(at, expr="neutral", arms=(0, 0), yaw=0, **kw):
    place(at, "me", (ME_A[0], ME_A[1], 0.0), yaw, expr, arms=list(arms), **kw)


def hill_cam_down(ty, tx=60.0, tz=1.5, w=2.0, lens=30, cx=60.0, cy=None):
    pass


# ===== 01 the rule (L01, L02)
show(0, "me")
me_a(0, "neutral")
mouth("me", 0, "L01>", 0.35)
shot("S01a", 0, cam(*APT_TGT, 1.7, 0, 36, cz=1.5))
shot("S01b", "L01.2", cam(0.0, 2.7, 1.5, 1.5, 8, 36, cz=1.5))
# S02: stakes, the key in my flat palm
me_a("L02", "wide", arms=(0, 86))
cue("L02", "key", mode="hand", who="me")
cue("L02", "heat", v=1.1, dur=0.5)
mouth("me", "L02", "L02>", 0.35)
shot("S02", "L02", cam(0.55, 2.35, 1.5, 1.5, 0, 36, cz=1.5))

# ===== 02 the rule at work (L03 to L06)
show("L03", "pizza")
place("L03", "pizza", (-60.0, 2.7, 0.0), 0, "smile", arms=[88, 88])
cue("L03", "boxes", v=1.0)
shot("S03", "L03", cam(-59.85, 2.7, 1.1, 1.5, 0, 30, cz=1.4))
cue("L04", "boxes", v=0.0)
show("L04", "buddy")
place("L04", "buddy", (-60.8, 31.9, 0.0), 0, "worried", arms=[0, 0])
shot("S04a", "L04", cam(-60.6, 31.9, 1.3, 1.5, 0, 30, cz=1.45))
show("L04.2")
shot("S04b", "L04.2", camp([-60.1, 30.6, 1.2], [-60.25, 33.3, 1.15], 34))
# S05: the dinosaur swinging under the key (back in the apartment)
show("L05", "me")
me_a("L05", "smile")
cue("L05", "key", mode="hang", who="me")
cue("L05", "swing", v=1.0)
mouth("me", "L05", "L05>", 0.35)
shot("S05", "L05", cam(-0.6, 3.3, 1.3, 1.05, -20, 36, cz=1.3))
cue("L06", "swing", v=0.0)
shot("S06a", "L06", camp([-1.55, 1.9, 1.5], [-1.55, 3.45, 1.45], 30))
me_a("L06.1", "smile")
mouth("me", "L06.1", "L06>", 0.4)
shot("S06b", "L06.1", cam(0.3, 2.6, 1.55, 1.0, 0, 36, cz=1.5))

# ===== 03 the old house (L07 to L09)
show("L07")
shot("S07", "L07", camp([60.0, 8.0, 0.07 * 8 + 1.7], [60.0, 36.0, ZP + 2.6], 24, pos2=[60.0, 10.0, 0.07 * 10 + 1.7]))
show("L08", "me")
me_a("L08", "warm")
mouth("me", "L08", "L08>", 0.3)
shot("S08", "L08", cam(0.3, 2.6, 1.5, 1.05, -12, 36, cz=1.5))
show("L09")
shot("S09a", "L09", camp([61.6, 23.5, ZH + 1.6], [59.6, 35.0, ZP + 1.4], 24, pos2=[61.2, 24.5, ZH + 1.6]))
show("L09.2", "me")
me_a("L09.2", "worried")
mouth("me", "L09.2", "L09>", 0.4)
shot("S09b", "L09.2", cam(0.3, 2.5, 1.55, 1.0, 8, 36, cz=1.5))

# ===== 04 Monday, Tuesday, Wednesday (L10 to L13)
cue("L10", "pips", n=2)
cue("L10", "heat", v=2.2, dur=0.6)
me_a("L10", "worried", arms=(0, 86))
cue("L10", "key", mode="hand", who="me")
shot("S10a", "L10", cam(0.55, 2.35, 1.5, 1.5, 0, 36, cz=1.5))
mouth("me", "L10.2", "L10>", 0.4)
shot("S10b", "L10.2", cam(0.3, 2.5, 1.55, 1.0, -8, 36, cz=1.5))
cue("L11", "phone", v=1.0)
show("L11")
cue("L11", "key", mode="hang", who="me")
shot("S11a", "L11", camp([1.75, 0.9, 1.1], [1.75, 2.8, 0.85], 36, pos2=[1.75, 1.3, 1.05]))
place("L11.2", "me", (G.ME_T[0], G.ME_T[1], 0.0), 0, "polite", arms=[0, 0])
key("me", "L11.2+0.01", yaw=0, expr="polite", head=[28, 0], blend=0.35)
key("me", "L11.2+0.25", yaw=0, expr="polite", head=[-28, 0], blend=0.25)
key("me", "L11.2+0.5", yaw=0, expr="polite", head=[22, 0], blend=0.25)
key("me", "L11.2+0.7", yaw=0, expr="polite", head=[0, 0], blend=0.2)
mouth("me", "L11.2", "L11>", 0.4)
shot("S11b", "L11.2", cam(1.75, 3.05, 1.5, 1.0, 0, 36, cz=1.5))
cue("L12", "pips", n=4)
cue("L12", "heat", v=3.8, dur=0.6)
me_a("L12", "polite", arms=(0, 86))
cue("L12", "key", mode="hand", who="me")
shot("S12a", "L12", cam(0.55, 2.35, 1.5, 1.5, 0, 36, cz=1.5))
place("L12.2", "me", (G.ME_T[0], G.ME_T[1], 0.0), 0, "polite", arms=[0, 0])
cue("L12.2", "key", mode="hang", who="me")
mouth("me", "L12.2", "L12>", 0.35)
shot("S12b", "L12.2", cam(1.75, 3.0, 1.35, 1.3, 0, 36, cz=1.4))
cue("L13", "pips", n=5)
cue("L13", "heat", v=5.0, dur=0.6)
cue("L13", "mitt", v=1.0)
cue("L13", "key", mode="hand", who="me")
me_a("L13", "wide", arms=(0, 86))
mouth("me", "L13", "L13>", 0.4)
shot("S13", "L13", cam(0.55, 2.35, 1.5, 1.5, 0, 36, cz=1.5))
cue("L14", "mitt", v=0.0)

# ===== 05 the hill (L14 to L19)
show("L14", "me")
place("L14", "me", (60.15, 17.6, 0.07 * 17.6), 180, "worried", arms=[0, 86])
key("me", "L14>", [60.15, 20.4, 0.07 * 20.4], yaw=180, expr="worried", arms=[0, 86], blend=0.25)
shot("S14", "L14", camp([60.2, 25.6, 0.07 * 25.6 + 1.6], [60.15, 19.0, 0.07 * 19 + 1.25], 36))
show("L15")
cue("L15", "key", mode="none", who="me")
shot("S15a", "L15", camp([58.4, 25.0, ZH + 1.6], [60.0, 36.0, ZP + 2.3], 26, pos2=[58.8, 26.0, ZH + 1.6]))
cue("L15.2", "curtain", v=1.0, dur=0.6)
shot("S15b", "L15.2", camp([60.0, 22.5, ZH + 1.6], [60.0, 36.0, ZP + 3.9], 40, pos2=[60.0, 23.5, ZH + 1.7]))
cue("L16", "curtain", v=0.0, dur=0.6)
show("L16", "me")
place("L16", "me", (60.3, 30.4, ZH), 0, "scared", arms=[0, 0])
cue("L16", "key", mode="hand", who="me")
key("me", "L16", yaw=0, expr="scared", arms=[0, 86])
mouth("me", "L16", "L16>", 0.35)
shot("S16", "L16", cam(60.3, 30.4, ZH + 1.45, 1.4, 0, 34, cz=ZH + 1.2))
# S17: on the porch, 1 m from the door, the door at the frame's left
P17 = (HX - 0.95, HY - 0.8, ZP)
place("L17", "me", P17, 0, "worried", arms=[0, 0])
cue("L17", "sticker", v=1.0)
mouth("me", "L17", "L17>", 0.3)
shot("S17", "L17", cam(HX - 0.4, HY, ZP + 1.35, 2.5, -10, 34, cz=ZP + 1.4, push=(2.2, ZP + 1.35)))
# S18: the sticker at chest height, my face beside it
P18 = (HX - 0.95, HY - 0.6, ZP)
place("L18", "me", P18, 0, "worried", arms=[0, 0])
mouth("me", "L18", "L18>", 0.35)
shot("S18", "L18", cam(HX - 0.4, HY, ZP + 1.35, 2.3, 6, 34, cz=ZP + 1.4, push=(2.1, ZP + 1.35)))
# S19: the keychain dinosaur beside the sticker
P19 = (HX - 0.9, HY - 0.6, ZP)
place("L19", "me", P19, 0, "wide", arms=[0, 90])
cue("L19", "key", mode="hand", who="me")
mouth("me", "L19", "L19>", 0.35)
shot("S19", "L19", cam(HX - 0.4, HY, ZP + 1.35, 2.4, -6, 34, cz=ZP + 1.4, push=(2.2, ZP + 1.35)))
# the drop: the door, gold light on it, my face at the edge
key("me", "P01", P19, yaw=0, expr="scared", arms=[0, 0])
shot("S19b", "P01", cam(HX - 0.4, HY, ZP + 1.3, 2.4, -8, 32, cz=ZP + 1.35, push=(2.2, ZP + 1.3)))

# ===== 06 the lock (L20 to L22)
INS = G.INS
show("L20")
cue("L20", "lock", v=1.0)
cue("L20", "key", mode="lock", who="me")
shot("S20", "L20", camp([INS[0] - 1.2, INS[1] - 2.1, 1.5], [INS[0] + 0.35, INS[1], 1.3], 34,
                        pos2=[INS[0] - 1.0, INS[1] - 1.8, 1.45]))
cue("L21", "lock", v=0.0)
show("L21", "me")
place("L21", "me", (HX - 0.2, HY - 0.9, ZP), 0, "wide", arms=[0, 0])
cue("L21", "key", mode="hand", who="me")
mouth("me", "L21", "L21.2", 0.35)
shot("S21a", "L21", cam(HX - 0.2, HY - 0.9, ZP + 1.5, 0.9, 0, 40, cz=ZP + 1.45))
key("me", "L21.2", yaw=0, expr="scared", arms=[0, 86], head=[0, 4], blend=0.4)
mouth("me", "L21.2", "L21>", 0.3)
shot("S21b", "L21.2", cam(HX - 0.2, HY - 0.9, ZP + 1.5, 0.85, 6, 40, cz=ZP + 1.45))
cue("L22", "door", v=1.0, dur=0.5)
cue("L22", "key", mode="none", who="me")
show("L22")
shot("S22", "L22", camp([HX + 0.9, HY - 2.9, ZP + 1.5], [HX + 0.2, HY + 1.5, ZP + 1.3], 28, pos2=[HX + 0.6, HY - 2.3, ZP + 1.5]))

# ===== 07 the reveal (L23 to L27)
MOM, DAD = (HX + 0.5, 38.5, ZP), (HX - 0.7, 39.0, ZP)
show("L23", "mom", "dad")
place("L23", "mom", MOM, 0, "laugh", arms=[0, 0])
place("L23", "dad", DAD, 0, "laugh", arms=[0, 0])
shot("S23a", "L23", camp([HX - 0.05, HY - 2.3, ZP + 1.45], [HX - 0.05, 38.7, ZP + 1.25], 33))
JESS_F = (HX + 0.45, 37.2, ZP)
show("L23.2", "jess")
place("L23.2", "jess", JESS_F, 0, "laugh", arms=[0, 0])
shot("S23b", "L23.2", cam(HX - 0.05, 37.2, ZP + 1.05, 1.7, 0, 34, cz=ZP + 1.1))
show("L24", "me")
place("L24", "me", (HX - 0.2, HY - 1.0, ZP), 0, "wide", arms=[0, 0])
mouth("me", "L24", "L24>", 0.3)
shot("S24", "L24", cam(HX - 0.2, HY - 1.0, ZP + 1.5, 0.95, 4, 36, cz=ZP + 1.45))
show("L25", "jess")
place("L25", "jess", (HX + 0.0, HY + 0.7, ZP), 0, "sly", arms=[0, 0])
mouth("jess", "L25", "L25>", 0.35)
shot("S25", "L25", cam(HX + 0.0, HY + 0.7, ZP + 1.5, 1.0, -6, 34, cz=ZP + 1.45))
# S26: the reveal picture
show("L26", "jess", "mom", "dad")
place("L26", "jess", (HX + 0.0, HY + 0.7, ZP), 0, "laugh", arms=[0, 86])
place("L26", "mom", (HX + 0.5, 38.6, ZP), 0, "laugh", arms=[0, 0])
place("L26", "dad", (HX - 0.95, 39.0, ZP), 0, "laugh", arms=[0, 0])
cue("L26", "key", mode="jess", who="jess")
shot("S26", "L26", cam(HX + 0.22, HY + 0.7, ZP + 1.4, 1.45, 0, 34, cz=ZP + 1.4))
show("L27", "jess")
place("L27", "jess", (HX + 0.0, HY + 0.7, ZP), 0, "laugh", arms=[0, 0])
cue("L27", "key", mode="none", who="me")
mouth("jess", "L27", "L27>", 0.5)
shot("S27", "L27", cam(HX + 0.0, HY + 0.7, ZP + 1.6, 0.8, 8, 40, cz=ZP + 1.55))

# ===== 08 why it worked (L28 to L32)
cue("L28", "lock", v=1.0)
cue("L28", "key", mode="lock", who="me")
show("L28")
shot("S28a", "L28", camp([INS[0] + 1.3, INS[1] - 2.8, 1.2], [INS[0] + 0.38, INS[1], 1.05], 36,
                         pos2=[INS[0] + 1.0, INS[1] - 2.4, 1.15]))
cue("L28.2", "lock", v=0.0)
show("L28.2", "jess")
place("L28.2", "jess", (HX + 0.0, HY + 0.7, ZP), 0, "warm", arms=[0, 0])
mouth("jess", "L28.2", "L28>", 0.35)
shot("S28b", "L28.2", cam(HX + 0.0, HY + 0.7, ZP + 1.55, 0.9, -6, 38, cz=ZP + 1.5))
cue("L29", "key", mode="none", who="me")
show("L29", "jess", "me")
JH, MH = (HX - 0.45, HY + 2.0, ZP), (HX + 0.45, HY + 2.0, ZP)
place("L29", "me", MH, 0, "laugh", arms=[0, 0])
place("L29", "jess", (HX - 1.1, HY + 2.0, ZP), 0, "laugh", arms=[0, 0])
key("jess", "L29+0.2", list(JH), yaw=0, expr="laugh", arms=[0, 75], side=[0, 0], blend=0.4)
key("me", "L29+0.2", list(MH), yaw=0, expr="laugh", arms=[75, 0], side=[0, 0], blend=0.4)
shot("S29", "L29", cam(HX + 0.0, HY + 2.0, ZP + 1.4, 2.0, 0, 34, cz=ZP + 1.4))
show("L30", "jess")
place("L30", "jess", (HX + 0.0, HY + 1.5, ZP), 0, "sly", arms=[0, 0])
mouth("jess", "L30", "L30.3", 0.35)
shot("S30a", "L30", cam(HX + 0.0, HY + 1.5, ZP + 1.55, 0.9, 6, 38, cz=ZP + 1.5))
show("L30.3", "me")
place("L30.3", "me", (HX + 0.0, HY + 1.5, ZP), 0, "polite", arms=[0, 0])
key("me", "L30.5", yaw=0, expr="warm", blend=0.4)
mouth("me", "L30.3", "L30>", 0.35)
shot("S30b", "L30.3", cam(HX + 0.0, HY + 1.5, ZP + 1.55, 0.9, -8, 38, cz=ZP + 1.5))
show("L31")
cue("L31", "key", mode="hook2", who="me", drop=1.0)
cue("L31+0.3", "key", mode="hook2", who="me", drop=0.0, dur=0.7)
cue("L31", "heat", v=5.0)
shot("S31", "L31", camp([HX + 0.2, HY + 4.0, ZP + 1.6], [HX + 1.0, HY + 0.4, ZP + 1.4], 30, pos2=[HX + 0.5, HY + 3.2, ZP + 1.6]))
show("L32", "me")
place("L32", "me", (HX + 0.7, HY + 0.9, ZP), 180, "warm", arms=[0, 0])
mouth("me", "L32", "L32>", 0.35)
shot("S32", "L32", cam(HX + 0.95, HY + 0.9, ZP + 1.45, 1.55, 180, 28, cz=ZP + 1.5))

# ----------------------------------------------------------------------------------------------- finish
remap_all(cues)
for k_ in acting.values():
    remap_all(k_)
shots = []
for i, (sid, at, camera, kw) in enumerate(SH):
    if len(camera) == 1:       # a slow dolly in on every shot whose camera was still: motion the preview can read
        _, p0, t0, ln = camera[0]
        camera = camera + [[1, [round(p0[j] + 0.17 * (t0[j] - p0[j]), 3) for j in range(3)], list(t0), ln]]
    s = {"id": sid, "cam": camera, "step": 2}
    if i:
        s["at"] = remap(at)
    s.update({k: v for k, v in kw.items() if not k.startswith("_")})
    shots.append(s)
for s in shots:
    pass

sfx = [
    {"at": "L11", "kind": "knock", "pattern": [0, 0.14], "tone": "soft", "db": -22},     # the phone, a soft buzz
    {"at": "L12.2", "kind": "knock", "pattern": [0, 0.14], "tone": "soft", "db": -22},
    {"at": "L22+0.05", "kind": "click", "db": -16},
    {"at": "L22+0.3", "kind": "creak", "db": -22, "dur": 0.8},
]
music = {
    "root": 55, "mode": "minor", "bpm": 96, "seed": 143,
    "sections": [
        {"at": 0, "voices": ["musicbox", "pad"], "energy": 0.45},
        {"at": "L14", "voices": ["pulse", "drone"], "energy": 0.35},
        {"at": "L16", "voices": ["drone"], "energy": 0.25},
        {"at": "L20", "voices": ["drone", "pad", "choir"], "energy": 0.45},
        {"at": "L23", "mode": "major", "voices": ["musicbox", "piano", "pad", "choir"], "energy": 0.75},
        {"at": "L32", "mode": "major", "voices": ["musicbox", "pad"], "energy": 0.4},
    ],
}
sound = {
    "floor": "wood", "steps_db": -22,
    "ambience": [{"kind": "hum", "from": "L01.1", "to": "L01>", "lufs": -38},
                 {"kind": "wind", "from": "L07", "to": "L07>", "lufs": -44},
                 {"kind": "wind", "from": "L14", "to": "L19>", "lufs": -42}],
    "sfx": sfx,
    "music_drops": [{"from": "P01", "to": "P01>"}],
    "rev": REV,
}
remap_all(sfx)
remap_all(music["sections"])
remap_all(sound["ambience"])
remap_all(sound["music_drops"])
SWAY = ["S15a", "S15b", "S16", "S17", "S18", "S19", "S19b", "S21a", "S21b"]
polish = {"reveal": ["L22", "L24"], "twist": "L23", "emph": ["L01.2", "L02.2", "L23.3", "L24.1", "L26.2"],
          "quiet": [], "hold": ["S17", "S18", "S19", "S19b"], "sway": True}
polish["emph"] = [remap(x) for x in polish["emph"]]
polish["reveal"] = [remap(x) for x in polish["reveal"]]
polish["twist"] = remap(polish["twist"])
story = {
    "slug": "ep143-warm-key",
    "title": "My Old House Key Went WARM \U0001F511",
    "made_for_kids": False,
    "premise": ("In our town a key goes warm when someone is waiting for you behind its door, and my key to the "
                "blue house on the hill we sold nine years ago went warm."),
    "twist": ("My big sister Jess bought the house back and had been inside since Monday waiting for me to notice, "
              "and she never changed the lock."),
    "world": ("A sunny hill street of small painted houses, an old blue house with a white porch and a warm front "
              "hall, and my bright apartment entry with a row of key hooks."),
    "voice": {"voice": "am_adam", "tempo": 1.03, "rate": 1.45},
    "key_color": "#ff9a3a",
    "gap": 0.15,
    "tail": 0.0,
    "fade_in": False,
    "fade_out": False,
    "rev": REV,
    "look": {"style": "closer", "fog": "#e8f3ff", "fog_density": 0.0008, "fog_start": 80.0, "sky": "#8fd0ff",
             "sky_strength": 1.0, "exposure": 0.0, "flash_safe": True, "polish": polish},
    "grade": {"shadows": [0.0, 0.0, 0.01], "highlights": [0.025, 0.012, -0.015], "saturation": 1.05,
              "contrast": 1.03, "vignette": 0.1, "bloom": 0.12, "grain": 0.008},
    "hud": {"object": "tag", "at": [-0.4, 0.62], "size": 0.58},
    "cast": cast,
    "lines": lines,
    "shots": shots,
    "acting": acting,
    "cues": cues,
    "fx": [],
    "music": music,
    "sound": sound,
    "set_moves": ["S05", "S15b", "S22", "S31"],
    "framing_ok": ["S04b", "S23b"],
    "frames_ok": ["S29"],
    "staging_ok": ["S29/hug"],
    "phonemes": {"Jess": "ʤˈɛs", "jess": "ʤˈɛs"},
    "homophones": {"just": "jess"},
}
OUT.write_text(json.dumps(story, indent=1, ensure_ascii=False) + "\n")
print("wrote", OUT, f"({len(shots)} shots, {len(cues)} cues)")
