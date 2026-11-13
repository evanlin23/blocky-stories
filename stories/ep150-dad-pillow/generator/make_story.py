"""Writes ../story.json for ep150 "My Stepdad's Pillow Dreams Of Someone KNOCKING" (script.md, 2026-11-12, batch 15, warm lane).
Run: python stories/ep150-dad-pillow/generator/make_story.py

Words are in lines.json (chunk numbers below are the ORIGINAL chunks; `remap` turns them into the split captions);
places are in ../layout.py (shared with set.py). A character facing -y has yaw 0, +x 90, +y 180, -x -90.
Cues (read by set.py): night (the tag's moon count, 4 = sun), mode (wake | dream | dusk: which lights and gold),
door (1 open, 0 shut), pillow (1: held on my forearms), bed (1: I lie in bed under the quilt), seat (Dad's seat on the
third stair), ear (the dog's ear twitch), spat (1 in Dad's hand, 2 dropped). Nothing ever blinks or pulses.
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
REV = 7
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
     "laugh": "laugh", "scared": "scared", "warm": "warm", "sheepish": "polite", "sleep": "soft"}


def person(skin, shirt, pants, shoes, hair="cap", hair_c="#15151a", hat="none", eyes="round", sleeves="long", **kw):
    d = {"age": "adult", "skin": skin, "shirt": shirt, "pants": pants, "shoes": shoes, "sleeves": sleeves,
         "hair": hair, "hair_c": hair_c, "hat": hat, "face": {"eyes": eyes, "brows": True, "ink": "#1c120c"}}
    d.update(kw)
    return d


SKIN = "#a97a52"
cast = {
    # me, 26: a short twisty dark crop, deep tan skin, a maroon sweatshirt, gray joggers, socks
    "me": person(SKIN, "#8a2a3a", "#8a8d96", "#efeae0", hair="cap", collar="#6a1c2a"),
    # me at sixteen: the same face and skin, a hoodie, a little smaller
    "teen": person(SKIN, "#3a5a8a", "#3a3a48", "#f2f2f2", hair="cap", extras=["hooddown"], extra_c="#3a5a8a", collar="#2a4468",
                   age="teen", height=0.93),
    # Dad, 58: a gray flat-top, the same skin as mine (set.py adds the big gray mustache), a blue cardigan over a white tee
    "dad": person("#a97a52", "#2f4e9e", "#4a5a7a", "#8a5a3a", hair="buzz", hair_c="#a9a9b2", collar="#f4f0e8", width=1.04),
    # Dad in the memory: a younger, darker mustache and dark hair
    "dadm": person("#a97a52", "#2f4e9e", "#4a5a7a", "#8a5a3a", hair="buzz", hair_c="#2a2420", collar="#f4f0e8", width=1.04),
    "cousin": person("#c58e64", "#6aa8d8", "#5a5a6a", "#f2f2f2", hair="swoop", hair_c="#3a2418"),
    "buddy": person("#d9b48a", "#e8a838", "#3a3a48", "#f2f2f2", hair="spiky", hair_c="#7a4a22", sleeves="short"),
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
    d = dict(yaw=yaw, expr=expr, head=[0, 0], arms=[0, 0], side=[0, 0], lean=0, blink=True, look=[0, 0], tremble=0)
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
cue(0, "night", n=0)
cue(0, "mode", m="wake")
cue(0, "frontdoor", v=1.0)
cue(0, "pillow", v=0.0)
cue(0, "bed", v=0.0)
cue(0, "seat", v=0.0)
cue(0, "ear", v=0.0)
cue(0, "spat", v=0.0)

HX = G.HX
# ------------------------------------------------------------------------------------------------ the places
LY = (G.BX, G.LY_ROOT[0], G.LY_ROOT[1])
HEAD = (G.BX, 3.1, 0.85)


def lying(at, expr="sleep"):
    place(at, "me", LY, 0, expr, lean=-84, head=[90, 0], blink=False)


def me_guest(at, expr, arms=(0, 0), **kw):
    place(at, "me", (G.ME_G[0], G.ME_G[1], 0.0), 0, expr, arms=list(arms), **kw)


# ===== 01 the rule (L01, L02)
show(0, "me")
cue(0, "bed", v=1.0)
lying(0)
shot("S01a", 0, cam(*HEAD, 1.4, 90, 36, cz=1.05))
shot("S01b", "L01.3", cam(*HEAD, 1.0, 82, 36, cz=1.0))
# S02: stakes, Dad's pillow held flat on my forearms
cue("L02", "bed", v=0.0)
cue("L02", "pillow", v=1.0)
me_guest("L02", "sheepish", arms=(72, 72))
mouth("me", "L02", "L02>", 0.3)
shot("S02", "L02", cam(G.ME_G[0], G.ME_G[1], 1.2, 1.7, 0, 30, cz=1.3))

# ===== 02 the rule at work (L03, L04)
cue("L03", "pillow", v=0.0)
show("L03", "cousin")
place("L03", "cousin", (G.CX, 2.35, -0.2), 0, "stunned", arms=[0, 0])
key("cousin", "L03.1", (G.CX, 2.35, -0.2), yaw=0, expr="stunned", head=[-22, 6], blend=0.35)
key("cousin", "L03.2", (G.CX, 2.35, -0.2), yaw=0, expr="stunned", head=[20, -4], blend=0.35)
key("cousin", "L03.3", (G.CX, 2.35, -0.2), yaw=0, expr="stunned", head=[-8, 8], blend=0.35)
shot("S03", "L03", cam(G.CX - 0.12, 2.35, 1.3, 1.25, -35, 32, cz=1.4))
show("L04", "buddy")
place("L04", "buddy", (G.BDX - 0.5, G.BDY + 0.8, -0.55), 0, "sheepish", arms=[0, 0])
shot("S04a", "L04", cam(G.BDX - 0.2, G.BDY + 0.8, 1.05, 2.5, 0, 30, cz=1.2))
cue("L04.2", "ear", v=1.0)
shot("S04b", "L04.2", camp([G.BDX + 0.95, G.BDY - 1.75, 0.85], [G.BDX + 0.45, G.BDY + 0.1, 0.45], 30,
                            pos2=[G.BDX + 0.9, G.BDY - 1.55, 0.83], tgt2=[G.BDX + 0.45, G.BDY + 0.1, 0.45]))
cue("L04>", "ear", v=0.0)

# ===== 03 the silly habit (L06, L07)
cue("L06", "night", n=1)
show("L06", "me")
PME = (HX - 0.05, 5.75, 0.0)          # on the porch, the doorway's east jamb by my raised hand
place("L06", "me", (PME[0], 6.3, 0.0), 0, "smile", arms=[0, 0])
key("me", "L06.2", PME, yaw=0, expr="smile", arms=[0, 0])
shot("S06a", "L06", cam(HX + 0.05, 5.9, 1.3, 2.6, 0, 30, cz=1.45))
# the knocks: the door-side arm up, knuckles on the jamb, two taps (cut in raised)
cut("me", "L06.3", PME, yaw=0, expr="smile", arms=[0, 62], side=[0, 0])
key("me", "L06.3+0.05", PME, yaw=0, expr="smile", arms=[0, 72], side=[0, 0], blend=0.05)
key("me", "L06.3+0.2", PME, yaw=0, expr="smile", arms=[0, 62], side=[0, 0], blend=0.1)
key("me", "L06.3+0.35", PME, yaw=0, expr="smile", arms=[0, 72], side=[0, 0], blend=0.1)
key("me", "L06.4", PME, yaw=0, expr="laugh", arms=[0, 0], side=[0, 0], blend=0.3)
mouth("me", "L06.4", "L06.5", 0.6)
shot("S06b", "L06.3", cam(HX + 0.2, 5.6, 1.25, 1.6, 12, 30, cz=1.35))
shot("S06c", "L06.4", cam(PME[0], PME[1], 1.5, 1.3, 0, 34, cz=1.55))
# S06d: the wide-open door on the sunny porch, me already in (out of frame)
show("L06.5")
shot("S06d", "L06.5", camp([HX, 0.6, 1.0], [HX, 5.0, 1.75], 22, pos2=[HX + 0.2, 1.65, 1.05], tgt2=[HX, 5.0, 1.75]))
# S07: Dad in the hall, shaking his head, smiling
show("L07", "dad")
place("L07", "dad", (HX, 2.4, 0.0), 0, "smile", arms=[0, 0])
key("dad", "L07.1", (HX, 2.4, 0.0), yaw=0, expr="smile", head=[18, 0], blend=0.3)
key("dad", "L07.1+0.35", (HX, 2.4, 0.0), yaw=0, expr="smile", head=[-18, 0], blend=0.3)
key("dad", "L07.2", (HX, 2.4, 0.0), yaw=0, expr="smile", head=[0, 0], blend=0.3)
shot("S07", "L07", cam(HX, 2.4, 1.3, 1.7, 0, 24, cz=1.45))

# ===== 04 the dream (L08 to L12)
cue("L08", "mode", m="dream")
cue("L08", "frontdoor", v=0.0)
show("L08", "me")
place("L08", "me", (G.ME_H[0], G.ME_H[1], 0.0), 0, "worried", arms=[0, 0])
# looking round the dream hall: left, then right
key("me", "L08.1", (G.ME_H[0], G.ME_H[1], 0.0), yaw=0, expr="worried", head=[-38, 0], blend=0.35)
key("me", "L08.2", (G.ME_H[0], G.ME_H[1], 0.0), yaw=0, expr="worried", head=[34, 0], blend=0.4)
shot("S08a", "L08", camp([HX, -1.14, 1.4], [HX, 3.1, 1.3], 22, pos2=[HX - 0.15, -0.45, 1.4], tgt2=[HX, 3.1, 1.32]))
place("L08.3", "me", (HX + 0.35, 3.8, 0.0), 0, "worried", arms=[0, 0])
shot("S08b", "L08.3", cam(HX - 0.1, 5.0, 1.4, 2.2, 0, 28, cz=1.4))
place("L09", "me", (G.ME_H[0], 3.2, 0.0), 0, "worried", arms=[0, 0])
mouth("me", "L09", "L09>", 0.3)
shot("S09", "L09", cam(HX, 3.2, 1.5, 1.0, 0, 36, cz=1.5))
# Dad on the third stair, sitting still, smiling
cue("L10", "seat", v=1.0)
SEAT_Z = -0.14
show("L10", "dad")
place("L10", "dad", (G.DAD_X, G.DAD_Y, SEAT_Z), 0, "smile", arms=[0, 0])
shot("S10a", "L10", cam(G.DAD_X, G.DAD_Y, 1.0, 1.9, 0, 20, cz=1.25))
shot("S10b", "L10.3", cam(G.DAD_X, G.DAD_Y, 1.4, 0.9, 0, 34, cz=1.4))
show("L12", "me", "dad")
place("L12", "me", (G.ME_H[0], 3.2, 0.0), 0, "worried", arms=[0, 0])
key("me", "L12", (G.ME_H[0], 3.2, 0.0), yaw=0, expr="worried", head=[0, 0], blend=0.3)
key("me", "L12.0+0.2", (G.ME_H[0], 3.2, 0.0), yaw=0, expr="worried", head=[-50, 0], blend=0.6)
mouth("me", "L12", "L12>", 0.25)
# S12: the wide: Dad smiling on the stair, me glancing at him, the shut door right there
shot("S12", "L12", camp([59.0, -1.3, 1.45], [58.95, 2.6, 1.3], 18, pos2=[59.0, -1.05, 1.45], tgt2=[58.95, 2.6, 1.32]))

# ===== 05 the second and third night (L14 to L19)
cue("L14", "night", n=2)
# night two: I've come down the hall toward Dad on the stair; he doesn't move
MS14 = (59.1, 0.5, 0.0)
place("L14", "me", (60.2, 2.6, 0.0), -23, "worried", arms=[0, 0])
key("me", "L14.2", MS14, yaw=-23, expr="worried", arms=[0, 0])
key("me", "L14.2+0.45", MS14, yaw=-148, expr="worried", arms=[0, 0], blend=0.4)
shot("S14a", "L14", camp([58.0, -1.2, 1.5], [58.95, 1.62, 1.3], 18, pos2=[58.05, -0.95, 1.5], tgt2=[58.97, 1.62, 1.3]))
# S14b: over my right shoulder, Dad on the stair, eyes shut, smiling, still
shot("S14b", "L14.4", camp([61.5, -0.3, 1.75], [58.4, 1.35, 1.2], 34, pos2=[61.4, -0.22, 1.73], tgt2=[58.4, 1.37, 1.2]))
cue("L17", "night", n=3)
# night three: I walk from by the stair to the door myself, glancing back
place("L17", "me", (59.7, 1.8, 0.0), 173, "worried", arms=[0, 0], head=[-50, 0])
key("me", "L17.1", (59.7, 1.8, 0.0), yaw=173, expr="worried", head=[-50, 0])
key("me", "L17>", (59.95, 3.9, 0.0), yaw=173, expr="worried", head=[-50, 0])
mouth("me", "L17", "L17>", 0.3)
shot("S17", "L17", camp([62.3, 1.0, 1.45], [60.0, 1.9, 1.35], 20, pos2=[62.22, 1.12, 1.45], tgt2=[60.1, 4.1, 1.4]))
place("L18", "dad", (G.DAD_X, G.DAD_Y, SEAT_Z), 0, "warm", arms=[0, 0])
mouth("dad", "L18.2", "L18.4", 0.45)
key("dad", "L18.4", (G.DAD_X, G.DAD_Y, SEAT_Z), yaw=0, expr="warm", arms=[0, 0], blend=0.2)
shot("S18a", "L18", cam(G.DAD_X, G.DAD_Y, 1.3, 1.2, 0, 30, cz=1.35))
shot("S18b", "L18.3", cam(G.DAD_X, G.DAD_Y, 1.4, 0.85, 0, 34, cz=1.4))
place("L19", "me", (HX + 0.25, 4.1, 0.0), 90, "stunned", arms=[0, 0])
mouth("me", "L19", "L19>", 0.3)
shot("S19", "L19", camp([61.5, 3.4, 1.5], [60.34, 4.45, 1.45], 16, pos2=[61.42, 3.47, 1.5], tgt2=[60.34, 4.47, 1.45]))
# S19c: the knock comes through; the wide: Dad smiling on the stair, me with my ear at his door
shot("S19c", "L19.2", camp([59.0, -1.3, 1.5], [59.0, 2.8, 1.4], 18, pos2=[59.0, -1.0, 1.5], tgt2=[59.0, 2.8, 1.42]))
# the drop: the door's gold edges, my face at the frame's edge
cut("me", "P01", (HX + 0.45, 3.9, 0.0), yaw=0, expr="stunned")
shot("S19b", "P01", cam(HX + 0.1, 5.0, 1.45, 2.4, 0, 30, cz=1.45))

# ===== 06 the voice (L20 to L24)
place("L20", "me", (HX, 3.9, 0.0), 0, "stunned", arms=[0, 0])
key("me", "L20.1", (HX, 3.9, 0.0), yaw=0, expr="stunned", head=[-14, 8], blend=0.4)
mouth("me", "L20", "L20>", 0.3)
shot("S20", "L20", cam(HX, 3.9, 1.5, 0.85, 0, 36, cz=1.5))
key("me", "L21.1", (HX, 3.9, 0.0), yaw=0, expr="stunned", head=[12, -6], blend=0.35)
mouth("me", "L21", "L21>", 0.35)
shot("S21", "L21", cam(HX, 3.9, 1.45, 0.82, 0, 38, cz=1.47))
# S22: the memory, me at sixteen on the porch, evening
show("L22", "teen")
place("L22", "teen", (G.MX, G.MY - 1.2, 0.0), 40, "sheepish", arms=[0, 0], side=[12, 12], head=[0, -8])
mouth("teen", "L22", "L22>", 0.3)
cut("teen", "L22.2", (G.MX, G.MY - 1.2, 0.0), yaw=0, expr="sheepish", arms=[0, 0], side=[0, 0], head=[0, 0])
shot("S22a", "L22", cam(G.MX - 0.3, G.MY - 1.1, 1.4, 2.1, 70, 30, cz=1.15))
shot("S22b", "L22.2", cam(G.MX, G.MY - 1.2, 1.4, 0.85, 0, 36, cz=1.4))
show("L23", "dadm")
place("L23", "dadm", (G.MX + 1.17, G.MY + 0.9, 0.0), 0, "neutral", arms=[0, 0])
mouth("dadm", "L23", "L23>", 0.15)
shot("S23", "L23", cam(G.MX + 1.05, G.MY + 0.9, 1.55, 1.1, 0, 34, cz=1.55))
show("L24", "teen")
TP = (G.MX - 0.37, G.MY - 0.71, 0.0)   # the door-side arm reaches the panel
place("L24", "teen", TP, 180, "worried", arms=[74, 0])
key("teen", "L24+0.3", TP, yaw=180, expr="worried", arms=[86, 0], blend=0.06)
key("teen", "L24+0.45", TP, yaw=180, expr="worried", arms=[74, 0], blend=0.1)
key("teen", "L24+0.6", TP, yaw=180, expr="worried", arms=[86, 0], blend=0.1)
shot("S24a", "L24", cam(G.MX - 0.1, G.MY - 0.55, 1.2, 1.9, 30, 30, cz=1.3))
place("L24.2", "teen", (G.MX, G.MY - 1.0, 0.0), 0, "worried", arms=[0, 0])
mouth("teen", "L24.2", "L24>", 0.7)
shot("S24b", "L24.2", cam(G.MX, G.MY - 1.0, 1.45, 0.95, 25, 34, cz=1.12))

# ===== 07 the reveal (L25)
cue("L25", "mode", m="dream")
show("L25", "me", "dad")
place("L25", "me", (HX + 0.7, 3.0, 0.0), 0, "warm", arms=[0, 0])
place("L25", "dad", (G.DAD_X, G.DAD_Y, SEAT_Z), 0, "sleep", arms=[0, 0], blink=False)
shot("S25", "L25", camp([HX - 0.7, -1.3, 1.3], [HX - 0.7, 2.6, 1.6], 15, pos2=[HX - 0.7, -1.3, 1.62], tgt2=[HX - 0.7, 2.6, 1.72]))
# my small smile toward Dad as the line lands
key("me", "L25.2", (HX + 0.7, 3.0, 0.0), yaw=0, expr="warm", head=[-14, 6], blend=0.6)

# ===== 08 the kitchen (L27)
cue("L27", "mode", m="wake")
cue("L27", "frontdoor", v=1.0)
cue("L27", "seat", v=0.0)
cue("L27", "night", n=4)
KX = G.KX
show("L27", "me")
KP = (KX + 0.15, -0.5, 0.0)    # in the corridor, knuckles on the doorway's jamb
place("L27", "me", KP, 180, "laugh", arms=[0, 0])
key("me", "L27.3", KP, yaw=180, expr="laugh", arms=[0, 66], side=[0, 8], blend=0.25)
key("me", "L27.3+0.05", KP, yaw=180, expr="laugh", arms=[0, 76], side=[0, 8], blend=0.05)
key("me", "L27.3+0.2", KP, yaw=180, expr="laugh", arms=[0, 66], side=[0, 8], blend=0.1)
key("me", "L27.3+0.35", KP, yaw=180, expr="laugh", arms=[0, 76], side=[0, 8], blend=0.1)
key("me", "L27.4", KP, yaw=180, expr="laugh", arms=[0, 0], side=[0, 0], blend=0.3)
mouth("me", "L27", "L27>", 0.35)
shot("S27a", "L27", camp([KX + 0.05, 3.48, 1.45], [KX + 0.05, -0.3, 1.3], 30, pos2=[KX - 0.1, 2.8, 1.43], tgt2=[KX + 0.05, -0.3, 1.32]))
cue("L27>", "spat", v=1.0)
cue("L27>+0.35", "spat", v=2.0)
show("L27>", "dad")
place("L27>", "dad", (KX, 3.55, 0.0), 0, "laugh", arms=[0, 62])
key("dad", "L27>+0.3", (KX, 3.55, 0.0), yaw=0, expr="laugh", arms=[0, 0], blend=0.2)
shot("S27b", "L27>", cam(KX + 0.1, 3.55, 1.1, 1.8, 25, 22, cz=1.3))

# ===== 09 the loop line (L32)
cue("L32", "mode", m="dusk")
cue("L32", "night", n=0)
cue("L32", "spat", v=0.0)
show("L32", "me")
cue("L32", "pillow", v=1.0)
me_guest("L32", "smile", arms=(72, 72))
shot("S32a", "L32", cam(G.ME_G[0], G.ME_G[1], 1.2, 1.7, 0, 30, cz=1.3))
cue("L32.2", "pillow", v=0.0)
cue("L32.2", "bed", v=1.0)
lying("L32.2")
shot("S32b", "L32.2", cam(*HEAD, 1.4, 90, 36, cz=1.05, push=(1.0, 0.85)))

# ----------------------------------------------------------------------------------------------- finish
remap_all(cues)
for k_ in acting.values():
    remap_all(k_)
shots = []
for i, (sid, at, camera, kw) in enumerate(SH):
    if len(camera) == 1:       # a slow dolly in on every shot whose camera was still
        _, p0, t0, ln = camera[0]
        camera = camera + [[1, [round(p0[j] + 0.12 * (t0[j] - p0[j]), 3) for j in range(3)], list(t0), ln]]
    s = {"id": sid, "cam": camera, "step": 2}
    if i:
        s["at"] = remap(at)
    s.update({k: v for k, v in kw.items() if not k.startswith("_")})
    shots.append(s)

sfx = [
    {"at": "L06.3+0.05", "kind": "knock", "pattern": [0, 0.3], "tone": "soft", "db": -14},
    {"at": "L08.3+0.05", "kind": "knock", "pattern": [0, 0.3], "tone": "soft", "db": -14},
    {"at": "L14.2+0.05", "kind": "knock", "pattern": [0, 0.3], "tone": "soft", "db": -14},
    {"at": "L19.2+0.05", "kind": "knock", "pattern": [0, 0.3], "tone": "soft", "db": -14},
    {"at": "L24+0.3", "kind": "knock", "pattern": [0, 0.3], "tone": "soft", "db": -14},
    {"at": "L27.3+0.05", "kind": "knock", "pattern": [0, 0.3], "tone": "soft", "db": -14},
    {"at": "L27>+0.75", "kind": "knock", "pattern": [0, 0.09, 0.16], "tone": "glass", "db": -24},
]
music = {
    "root": 48, "mode": "minor", "bpm": 88, "seed": 150,
    "sections": [
        {"at": 0, "voices": ["piano", "pad"], "energy": 0.45},
        {"at": "L08", "voices": ["pad", "musicbox"], "energy": 0.35},
        {"at": "L17", "voices": ["pad", "drone"], "energy": 0.4},
        {"at": "L20", "voices": ["drone", "pad"], "energy": 0.3},
        {"at": "L25", "mode": "major", "voices": ["piano", "pad", "choir"], "energy": 0.7},
        {"at": "L27", "mode": "major", "voices": ["piano", "musicbox", "pad"], "energy": 0.5},
        {"at": "L32", "mode": "major", "voices": ["piano", "pad"], "energy": 0.35},
    ],
}
sound = {
    "floor": "wood", "steps_db": -22,
    "ambience": [{"kind": "room", "from": 0, "to": "L06", "lufs": -40},
                 {"kind": "crickets", "from": "L06.5", "to": "L06>", "lufs": -44}],
    "sfx": sfx,
    "music_drops": [{"from": "P01", "to": "P01>"}],
    "rev": REV,
}
remap_all(sfx)
remap_all(music["sections"])
remap_all(sound["ambience"])
remap_all(sound["music_drops"])
polish = {"reveal": ["L20", "L25"], "emph": ["L01.3", "L02.1", "L18.4", "L25.3"],
          "quiet": [], "hold": ["S06d", "S19", "S25"], "sway": [], "punch_cap": {"S25": 0.0}}
polish["emph"] = [remap(x) for x in polish["emph"]]
story = {
    "slug": "ep150-dad-pillow",
    "title": "My Stepdad's Pillow Dreams Of Someone KNOCKING \U0001F6CF️",
    "made_for_kids": False,
    "premise": ("In our town, if you sleep on someone else's pillow you dream their dream, and my stepdad's pillow "
                "dreams the same thing every night: two knocks at his front door, and a voice yelling Dad."),
    "twist": ("The voice is mine at sixteen, locked out my first week in his house, the first time I ever called him "
              "Dad, and he never opens the door because the dream ends when he does."),
    "world": ("A bright guest room with a striped quilt, my stepdad's sunny front hall and kitchen, and the same hall "
              "in his dream, warm sunset gold, with a staircase and a white front door."),
    "voice": {"voice": "am_adam", "tempo": 1.03, "rate": 1.45},
    "key_color": "#ffc66a",
    "gap": 0.15,
    "tail": 0.0,
    "fade_in": False,
    "fade_out": False,
    "rev": REV,
    "look": {"style": "closer", "fog": "#e8f3ff", "fog_density": 0.0008, "fog_start": 80.0, "sky": "#8fd0ff",
             "sky_strength": 1.0, "exposure": 0.0, "flash_safe": True, "polish": polish},
    "grade": {"shadows": [0.0, 0.0, 0.01], "highlights": [0.025, 0.012, -0.015], "saturation": 1.05,
              "contrast": 1.03, "vignette": 0.1, "bloom": 0.1, "grain": 0.008},
    "hud": {"object": "tag", "at": [-0.4, 0.62], "size": 0.58},
    "cast": cast,
    "lines": lines,
    "shots": shots,
    "acting": acting,
    "cues": cues,
    "fx": [],
    "music": music,
    "sound": sound,
    "set_moves": [],
    "clip_ok": ["pillow"],
    "framing_ok": [],
    "frames_ok": [],
    "staging_ok": ["S24b/yaw"],
}
OUT.write_text(json.dumps(story, indent=1, ensure_ascii=False) + "\n")
print("wrote", OUT, f"({len(shots)} shots, {len(cues)} cues)")
