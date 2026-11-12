"""Writes ../story.json for ep145 "our dog barked once, then twice" (script.md, 2026-11-12, batch 15, interactive lane).
Run: python stories/ep145-dog-barks/generator/make_story.py

The words are in lines.json; places are in ../layout.py (shared with set.py). Yaw 0 faces -y, 90 +x, 180 +y, -90 -x.
Every character move is a `cut` on a shot boundary (nobody teleports in view) except Mia's walk into the house.
Moose is not a cast member: set.py moves him by the `moose`, `mlook`, `bark` and `badge` cue tracks.
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
    mm = re.match(r"^(L\d+b?)\.(\d+)(.*)$", ref)
    if mm and mm.group(1) in CHUNKMAP:
        return f"{mm.group(1)}.{CHUNKMAP[mm.group(1)][int(mm.group(2))]}{mm.group(3)}"
    return ref


def remap_all(items):
    for it in items:
        for key in ("at", "from", "to"):
            if key in it:
                it[key] = remap(it[key])


D2R = math.pi / 180
X = {"neutral": "neutral", "serious": "blank", "uneasy": "worried", "stunned": "wide", "sad": "worried",
     "smile": "smile", "laugh": "laugh", "scared": "scared", "worried": "worried", "grin": "grin"}


def person(skin, shirt, pants, shoes, hair="cap", hair_c="#2a1d15", hat="none", extras=(), eyes="round", brow_w=1.0,
           extra_c=None, **kw):
    d = {"age": "adult", "skin": skin, "shirt": shirt, "pants": pants, "shoes": shoes, "sleeves": "short",
         "hair": hair, "hair_c": hair_c, "hat": hat, "face": {"eyes": eyes, "brows": True, "ink": "#1c120c"}}
    if brow_w != 1.0:
        d["face"]["brow_w"] = brow_w
    if extras:
        d["extras"] = list(extras)
    if extra_c:
        d["extra_c"] = extra_c
    d.update(kw)
    return d


cast = {
    # me, 19: an orange camp shirt, brown block hair, a plain grill apron
    "me": person("#f1c9a0", "#ff8a3d", "#3a4a6a", "#f2f2f2", hair="cap", hair_c="#6b4226", extras=["apron"],
                 extra_c="#f4f1e8", brow_w=1.2),
    # Mia, 26: a lemon top, black curls in a high puff, lashes
    "mia": person("#c58e64", "#ffe066", "#f2b93a", "#f2f2f2", hair="bun", hair_c="#15151a", eyes="lashes", brow_w=0.9),
    # Grant, 28: a pale blue button shirt, neat brown hair, a short beard (set.py)
    "grant": person("#e8b88a", "#9cc7ff", "#4a4f60", "#3a2a1c", hair="swoop", hair_c="#6b4a2e", collar="#f4f8ff",
                    brow_w=1.2, sleeves="long"),
    # the mail carrier, 40s: navy cap and trousers, a light blue shirt, no badge or lettering
    "mail": person("#d9a47a", "#6f9ad8", "#1f3a6e", "#2a2a30", hair="cap", hair_c="#2a1d15", hat="ballcap",
                   hat_c="#1f3a6e", brow_w=1.3),
    # the "roof inspector", 50s: an orange vest, grey buzz hair, glasses, a clipboard (set.py)
    "inspector": person("#ecc9a0", "#ffa51f", "#4a4a52", "#2a2a30", hair="buzz", hair_c="#8a8a92", extras=["glasses"],
                        sleeves="short", brow_w=1.4),
    # Mr. Hale, a neighbour in his 60s: bald with a grey fringe, a green cardigan
    "hale": person("#e8b88a", "#6a9a6a", "#6a5a4a", "#3a2a1c", hair="none", brow_w=1.4, width=1.08, sleeves="long"),
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
    """A key that takes effect at once (no blend): a pose or place that changes on a cut."""
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


def put(who, at, pos, yaw=None, expr="neutral", **kw):
    """Stand `who` at `pos` from `at` on a cut, facing `yaw` (or toward the grill)."""
    d = dict(head=[0, 0], arms=[0, 0], side=[0, 0], lean=0.0)
    d.update(kw)
    cut(who, at, [pos[0], pos[1], 0.0], yaw=yaw if yaw is not None else 0.0, expr=expr, **d)


def mouth(who, a, b, amt=0.45):
    acting[who].append({"from": a, "to": b, "mouth": [amt, amt], "flap": True})


def cue(at, name, **kw):
    cues.append({"at": at, "name": name, **kw})


def cam(tx, ty, tz, w, az, lens, cz=None, push=None):
    """A camera looking at (tx, ty, tz) from az degrees round from the south, far enough off that the frame is w
    metres wide there. One key (the polish pack adds the slow push) or, with push=(w2, tz2), two keys."""
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


def shot(sid, at, camera, moose=False, **kw):
    """`moose`: Moose is in the shot, so the bark badge floats over his head; otherwise it rides in the corner."""
    SH.append((sid, at, camera, kw))
    cue(at, "badge", mode=1.0 if moose else 2.0)


def moose_at(at, x, y, yaw=0.0, pose=0.0, dur=0.0):
    cue(at, "moose", x=x, y=y, yaw=yaw, pose=float(pose), dur=dur)


def bark(*ats):
    for a in ats:
        cue(a, "bark")


def number(at, n, dur=0.2):
    cue(at, "badge", n=float(n), dur=dur)


GT = G.GATE
GRILL = G.GRILL
ME_G, GR_G = G.ME_G, G.GR_G
YME = G.yaw_to(ME_G, GRILL)
YGR = G.yaw_to(GR_G, GRILL)
CARRIER = (GT[0] + 0.9, GT[1] + 1.9)               # the visitor, a step inside the gate (south-west of Moose)
MOOSE_GATE = (GT[0] + 0.05, GT[1] + 3.0)           # Moose, nose to the visitor's hand
MIA_T = (2.9, 4.5)                                 # Mia at the table's west end, her back to us

# ----------------------------------------------------------------------------------------------- the cast at rest
for who in cast:
    key(who, 0, [0, 0, 0], yaw=0, expr="neutral", head=[0, 0], arms=[0, 0], side=[0, 0], hidden=True)
moose_at(0, *MOOSE_GATE, G.yaw_to(MOOSE_GATE, CARRIER))
cue(0, "badge", n=1.0, mode=1.0)
cue(0, "gate", ang=0.0)
cue(0, "door", ang=0.0)
cue(0, "ring", mode=0.0)
cue(0, "carrot", on=0.0)
cue(0, "biscuit", on=0.0)
cue(0, "clip", on=0.0)
cue(0, "spat", on=0.0)
cue(0, "rock", amp=0.0)
cue(0, "napkin", on=0.0)
cue(0, "mlook", yaw=0.0, pitch=0.0)

# ===== 01 the rule, shown at once (L01, L02): Moose's face, badge 1, a biscuit offered at the edge
show(0, "mail")
put("mail", 0, CARRIER, G.yaw_to(CARRIER, MOOSE_GATE), "smile", arms=[0, 40])
cue(0, "gate", ang=90.0)
cue(0, "biscuit", on=1.0)
# the camera stands on the lawn inside the fence, west of Moose, a metre and a bit from his face; the carrier's hand
# (the biscuit) comes in at the right edge, his body is out of frame (south of the right edge)
shot("S01a", 0, camp([-1.79, -1.73, 0.8], [-1.1, 0.2, 0.85], 22, pos2=[-1.72, -1.6, 0.8]), moose=True)
shot("S01b", "L01.1", camp([-1.72, -1.17, 1.0], [-1.2, 0.26, 1.2], 24, pos2=[-1.65, -1.05, 1.0]), moose=True)
# TWICE: the badge flips to 2 and straight back to 1 (a joke-quick demo)
shot("S02", "L02", camp([-1.72, -1.17, 1.0], [-1.2, 0.26, 1.2], 24, pos2=[-1.68, -1.1, 1.0]), moose=True)
number("L02", 2)
number("L02.1", 1)

# ===== 02 the rule at work (L03 to L06)
shot("S03", "L03", cam(-1.1, -0.1, 1.0, 2.8, -75, 30, cz=0.8, push=(2.5, 1.0)), moose=True)
bark("L03.2")
cue("L03", "biscuit", on=1.0)
# the squeaky carrot, which only family may share: Moose lies on it, chin on it, watching the visitor sideways
MX3 = (MOOSE_GATE[0] - 0.1, MOOSE_GATE[1] + 0.2)
moose_at("L03b", *MX3, G.yaw_to(MX3, CARRIER), 2, 0.0)
cue("L03b", "carrot", on=1.0, x=MX3[0] - 0.25, y=MX3[1] - 0.65, z=0.0, yaw=75.0, carry=0.0)
cue("L03b", "mlook", yaw=0.0, pitch=8.0)
shot("S04", "L03b", camp([-4.3, -0.1, 0.5], [MX3[0] - 0.1, MX3[1] - 0.3, 0.35], 36, pos2=[-4.1, -0.05, 0.5]),
     moose=True)
shot("S04b", "L03b.1", camp([-4.1, -0.3, 0.5], [MX3[0] - 0.1, MX3[1] - 0.4, 0.4], 42, pos2=[-3.9, -0.25, 0.5]),
     moose=True)
# the biscuit goes into his mouth
moose_at("L04", *MOOSE_GATE, G.yaw_to(MOOSE_GATE, CARRIER), 0, 0.0)
cue("L04", "carrot", on=0.0)
cue("L04", "mlook", yaw=0.0, pitch=-12.0)
put("mail", "L04", CARRIER, G.yaw_to(CARRIER, MOOSE_GATE), "smile", arms=[0, 48])
key("mail", "L04+0.3", yaw=G.yaw_to(CARRIER, MOOSE_GATE), arms=[0, 48], expr="smile")
key("mail", "L04.1+0.4", yaw=G.yaw_to(CARRIER, MOOSE_GATE), arms=[0, 30], expr="smile", blend=0.8)
cue("L04.2", "biscuit", on=0.0)
shot("S05", "L04", camp([-1.7, -1.2, 0.6], [-1.0, -0.1, 0.7], 20, pos2=[-1.65, -1.1, 0.62]), moose=True)
# the roof inspector: two barks, and the badge goes to 2
show("L05", "inspector")
put("inspector", "L05", CARRIER, G.yaw_to(CARRIER, MOOSE_GATE), "smile", arms=[70, 0])
cue("L05", "mlook", yaw=0.0, pitch=0.0)
cue("L05", "clip", on=1.0)
number("L05", 2)
shot("S06", "L05", cam(-1.1, -0.1, 1.05, 2.8, -75, 30, cz=0.85, push=(2.5, 1.05)), moose=True)
bark("L05.2", "L05.2+0.5")
# Mr. Hale and the clean strip where his gutter was
show("L06", "hale")
put("hale", "L06", G.HALE, G.yaw_to(G.HALE, (-4.0, 0.2)), "stunned", head=[0, 0])
cue("L06", "clip", on=0.0)
cue("L06", "gate", ang=0.0)
shot("S07", "L06", camp([-3.9, 1.5, 1.5], [-7.0, 2.6, 2.05], 28, pos2=[-4.4, 1.75, 1.5]))

# ===== 03 the town's dog, never wrong; the yard (L07, L08)
show("L07")
moose_at("L07", 3.9, -0.6, G.yaw_to((3.9, -0.6), (2.6, 1.6)), 0)
moose_at("L07+0.2", 2.6, 1.6, G.yaw_to((3.9, -0.6), (2.6, 1.6)), 0, 2.2)
number("L07", 2)
shot("S08", "L07", camp([4.6, 2.4, 1.4], [1.1, 6.8, 1.3], 34, pos2=[4.3, 2.9, 1.4], tgt2=[1.1, 6.8, 1.3]))

# ===== 04 Mia and Grant at the gate (L09 to L12b)
show("L09", "mia", "grant")
put("mia", "L09", (GT[0] - 0.8, GT[1] + 0.65), 180, "smile", arms=[0, 0])
put("grant", "L09", (GT[0] + 0.62, GT[1] + 0.65), 180, "smile", arms=[0, 0])
cue("L09", "gate", ang=90.0)
number("L09", 1, 0.01)
shot("S09", "L09", cam(GT[0] - 0.1, GT[1] + 0.65, 1.2, 3.0, 160, 30, cz=1.35, push=(2.7, 1.2)))
show("L10")
moose_at("L10", MOOSE_GATE[0] + 0.1, MOOSE_GATE[1] + 0.05, G.yaw_to(MOOSE_GATE, (GT[0], GT[1])), 0)
cue("L10", "mlook", yaw=0.0, pitch=0.0)
shot("S10", "L10", camp([-2.2, -4.7, 1.0], [-1.4, 0.15, 0.85], 48, pos2=[-2.2, -4.3, 1.0]), moose=True)
bark("L11")
# Mia's little dance, Grant beside her saying Moose's name, then the handshake
show("L12", "mia", "grant")
put("mia", "L12", (-1.9, 0.3), 180, "laugh", arms=[0, 0])
put("grant", "L12", (-0.5, 0.3), 180, "smile", arms=[0, 0])
key("mia", "L12+0.25", yaw=180, arms=[160, 160], side=[0, 0], expr="laugh", blend=0.5)
key("mia", "L12+0.9", yaw=190, arms=[40, 160], expr="laugh", blend=0.5)
key("mia", "L12.1", yaw=170, arms=[160, 40], expr="laugh", blend=0.5)
mouth("grant", "L12+0.1", "L12+0.7", 0.5)
cue("L12", "gate", ang=0.0)
shot("S11", "L12", cam(-1.2, 0.3, 1.2, 2.6, 130, 24, cz=1.35, push=(2.3, 1.2)))
show("L12b", "me", "grant")
put("me", "L12b", (0.45, 0.3), -90, "smile", arms=[0, 0])
put("grant", "L12b", (-0.45, 0.3), 90, "smile", arms=[0, 0])
key("me", "L12b+0.3", yaw=-90, arms=[0, 80], expr="smile", blend=0.4)
key("grant", "L12b+0.3", yaw=90, arms=[0, 80], expr="smile", blend=0.4)
shot("S11b", "L12b", cam(0.0, 0.3, 1.3, 2.4, -150, 30, cz=1.35, push=(2.0, 1.3)))

# ===== 05 four-fifteen: the grill, the table that rocks, Moose barks again (L13 to L15b)
show("L13", "me", "grant", "mia")
put("me", "L13", ME_G, YME, "neutral", arms=[0, 0])
put("grant", "L13", GR_G, YGR, "smile", arms=[0, 0])
put("mia", "L13", MIA_T, 180, "smile", arms=[70, 70])
key("mia", "L13+0.7", yaw=180, arms=[10, 10], expr="smile", blend=0.5)
cue("L13+0.4", "rock", amp=1.0, dur=0.3)
cue("L13+1.5", "rock", amp=0.0, dur=0.4)
number("L13", 1, 0.01)
shot("S12", "L13", cam(0.0, 3.4, 1.3, 2.2, 140, 26, cz=1.55, push=(2.0, 1.3)))
show("L14", "me", "grant")
moose_at("L14", 4.2, 0.6, G.yaw_to((4.2, 0.6), (1.3, 4.5)), 0)
moose_at("L14+0.2", 1.3, 4.5, G.yaw_to((4.2, 0.6), (1.3, 4.5)), 0, 2.2)
put("me", "L14", ME_G, YME, "neutral")
put("grant", "L14", GR_G, YGR, "smile")
shot("S13", "L14", camp([1.2, 6.0, 0.8], [2.9, 2.4, 0.5], 28, pos2=[1.3, 5.6, 0.8]), moose=True)
show("L15", "me", "grant")
moose_at("L15", 1.3, 4.5, -24.0, 0)
shot("S14", "L15", cam(1.5, 4.0, 0.75, 1.1, 20, 36, cz=0.8, push=(0.95, 0.75)), moose=True)
bark("L15", "L15.1")
number("L15.1", 2)
show("L15b", "grant")
cue("L15b", "gate", ang=88.0)
shot("S15", "L15b", camp([1.0, 5.5, 0.65], [0.75, 3.0, 0.9], 18, pos2=[1.0, 5.2, 0.65]),
     moose=True, hold=True)
# the drop: the badge says 2, still, the grill smoke drifting
shot("SD", "P01", cam(0.0, 4.2, 1.3, 1.9, 25, 32, cz=1.3, push=(1.6, 1.3)), moose=False)

# ===== 06 I watched him (L16 to L21b)
show("L16", "me")
put("me", "L16", ME_G, -30, "stunned", head=[25, 0])
mouth("me", "L16", "L16>", 0.4)
shot("S16", "L16", cam(ME_G[0], ME_G[1], 1.55, 1.1, -30, 40, cz=1.5, push=(0.95, 1.55)))
show("L17", "grant")
put("grant", "L17", GR_G, -40, "smile", arms=[0, 60])
cue("L17", "spat", on=1.0)
key("grant", "L17+0.4", yaw=-40, arms=[0, 38], expr="smile", blend=0.4)
key("grant", "L17+0.9", yaw=-40, arms=[0, 62], expr="smile", blend=0.4)
shot("S17", "L17", cam(GR_G[0], GR_G[1], 1.3, 2.2, -40, 30, cz=1.35, push=(1.9, 1.3)))
show("L18", "grant")
put("grant", "L18", GR_G, -25, "neutral", arms=[0, 0])
cue("L18", "spat", on=0.0)
mouth("grant", "L18+0.2", "L18+0.7", 0.4)
number("L18", 2, 0.01)
shot("S18", "L18", cam(GR_G[0], GR_G[1], 1.55, 1.1, -25, 40, cz=1.5, push=(0.95, 1.55)))
# 2b: Mia goes in for ketchup, and Grant lifts Grandma's ring box off the sill
show("L19", "mia")
put("mia", "L19", (-1.9, 5.3), -135, "smile")
key("mia", "L19>", [-3.0, 7.3], expr="smile")
key("mia", "L19>+0.1", [-3.0, 7.3], hidden=True)
cue("L19", "door", ang=100.0)
shot("S19", "L19", cam(-2.0, 6.0, 1.4, 4.0, -8, 26, cz=1.45, push=(3.4, 1.4)))
RGX = G.RING[0]
show("L20", "grant")
put("grant", "L20", (RGX - 0.55, 6.05), 180, "neutral", arms=[0, 0])
key("grant", "L20+0.3", yaw=180, arms=[0, 92], expr="neutral", blend=0.7)
key("grant", "L20.2", yaw=180, arms=[0, 92], expr="neutral")
key("grant", "L20.3", yaw=180, arms=[0, 10], expr="neutral", blend=0.5)
cue("L20.2", "ring", mode=1.0)
cue("L20.3+0.5", "ring", mode=2.0)
shot("S19b", "L20", camp([-0.6, 6.6, 1.4], [0.9, 6.5, 1.3], 16, pos2=[-0.5, 6.55, 1.4]))
show("L21", "me", "grant")
put("me", "L21", ME_G, 90, "worried")
put("grant", "L21", GR_G, -90, "smile")
mouth("grant", "L21", "L21>", 0.5)
shot("S20", "L21", cam(-0.15, 3.4, 1.35, 2.4, 15, 26, cz=1.4, push=(2.1, 1.35)))
show("L21b", "me")
put("me", "L21b", ME_G, 35, "worried", head=[-8, 0])
mouth("me", "L21b", "L21b>", 0.4)
shot("S21", "L21b", cam(ME_G[0], ME_G[1], 1.55, 1.1, 35, 40, cz=1.5, push=(0.95, 1.55)))

# ===== 07 the other side of it (L22 to L25b)
GRANT_FEET = (GR_G[0] + 0.1, GR_G[1] - 0.7)
show("L22", "grant")
put("grant", "L22", GR_G, YGR, "smile")
moose_at("L22", 2.6, 1.9, G.yaw_to((2.6, 1.9), (2.5, 2.2)), 0)
cue("L22", "carrot", on=1.0, carry=1.0)
MG = (GR_G[0] + 0.7, GR_G[1] - 0.9)
moose_at("L23", 2.6, 1.9, G.yaw_to((2.6, 1.9), MG), 0)
moose_at("L23+0.1", MG[0], MG[1], G.yaw_to((2.6, 1.9), MG), 0, 1.7)
cue("L23.2", "carrot", on=1.0, x=GRANT_FEET[0] + 0.1, y=GRANT_FEET[1] - 0.25, z=0.0, yaw=70.0, carry=0.0)
number("L22", 2, 0.01)
shot("S22", "L22", camp([-0.4, 2.4, 0.5], [1.75, 2.35, 0.4], 20, pos2=[-0.25, 2.4, 0.5]), moose=True)
shot("S22b", "L23.3", cam(GRANT_FEET[0] + 0.1, GRANT_FEET[1] - 0.25, 0.1, 0.9, -20, 36, cz=0.4, push=(0.75, 0.1)),
     moose=False)
cue("L23.3", "mlook", yaw=0.0, pitch=0.0)
moose_at("L24", GR_G[0] + 0.55, GR_G[1] - 1.2, 80.0, 0)
cue("L24", "mlook", yaw=0.0, pitch=-18.0)
put("grant", "L24", GR_G, G.yaw_to(GR_G, (GR_G[0] + 0.55, GR_G[1] - 1.2)), "smile")
shot("S23", "L24", cam(1.0, 2.9, 1.0, 2.6, 80, 28, cz=0.9, push=(2.3, 1.0)), moose=True)
# 1b: Grant, bent to the picnic table's short leg, a folded napkin under it
show("L25", "grant")
put("grant", "L25", (4.9, 4.45), 194, "smile", lean=0.0)
key("grant", "L25+0.2", yaw=194, lean=18, arms=[30, 30], expr="smile", blend=0.5)
key("grant", "L25+0.8", [4.9, 4.45, -0.42], yaw=194, lean=18, arms=[40, 40], expr="smile", blend=0.5)
cue("L25", "rock", amp=1.0, dur=0.1)
cue("L25.1", "napkin", on=1.0)
cue("L25.1", "rock", amp=0.0, dur=0.3)
shot("S24", "L25", camp([6.4, 6.6, 0.7], [4.85, 4.9, 0.6], 16, pos2=[6.2, 6.4, 0.7]))
# 1c: the S15 framing again, and the open gate
show("L26", "grant")
put("grant", "L26", GR_G, YGR, "neutral")
moose_at("L26", 1.3, 4.5, -24.0, 0)
cue("L26", "mlook", yaw=0.0, pitch=0.0)
bark("L26.1", "L26.1+0.5")
shot("S25", "L26", camp([1.0, 5.5, 0.65], [0.75, 3.0, 0.9], 18, pos2=[1.0, 5.2, 0.65]),
     moose=True, hold=True)
show("L28")
shot("S26", "L28", cam(GT[0] + 0.5, GT[1] + 0.2, 0.9, 2.0, 150, 28, cz=1.1, push=(1.7, 0.9)))
shot("S26b", "L28b", camp([-4.0, 0.2, 1.6], [-9.5, 2.7, 2.4], 22, pos2=[-4.6, 0.5, 1.6]))

# ===== 08 no answer (L29 to L31)
show("L29")
moose_at("L29", 0.4, 1.8, -24.0, 0)
cue("L29", "mlook", yaw=0.0, pitch=-8.0)
cue("L29", "gate", ang=88.0)
shot("S27", "L29", camp([0.69, -0.21, 0.75], [0.23, 1.42, 0.75], 22, pos2=[0.62, -0.05, 0.75]), moose=True)
show("L30", "mia", "grant")
put("mia", "L30", (1.6, 4.7), -15, "laugh", arms=[0, 75])
put("grant", "L30", (3.1, 4.7), 20, "laugh", arms=[0, 0])
key("mia", "L30+0.4", yaw=-15, arms=[0, 75], expr="laugh", blend=0.5)
number("L30", 2, 0.01)
shot("S28", "L30", cam(2.1, 4.7, 1.2, 2.2, 25, 28, cz=1.3, push=(2.0, 1.2)))
show("L31", "me")
put("me", "L31", ME_G, G.yaw_to(ME_G, (ME_G[0] - 1, ME_G[1] - 4)), "worried")
mouth("me", "L31", "L31>", 0.4)
shot("S29", "L31", cam(ME_G[0], ME_G[1], 1.55, 1.15, 5, 40, cz=1.5, push=(1.0, 1.55)), hold=True)
fx = [{"at": "L31>+0.3", "kind": "punch", "dur": 1.5, "zoom": 1.05},
      {"at": "P02+1.8", "kind": "punch", "dur": 1.5, "zoom": 1.05}]

# ----------------------------------------------------------------------------------------------- finish
remap_all(cues)
for k_ in acting.values():
    remap_all(k_)
remap_all(fx)
shots = []
for i, (sid, at, camera, kw) in enumerate(SH):
    s = {"id": sid, "cam": camera, "step": 2}
    if i:
        s["at"] = remap(at)
    s.update({k: v for k, v in kw.items() if k != "hold"})
    shots.append(s)
hold = [sid for sid, at, camera, kw in SH if kw.get("hold")]

sfx = [
    {"at": "L12b", "kind": "thud", "db": -26},
]
music = {
    "root": 55, "mode": "mixolydian", "bpm": 108, "seed": 145,
    "sections": [
        {"at": 0, "voices": ["pulse", "pad"], "energy": 0.45},
        {"at": "L09", "voices": ["pulse", "pad"], "energy": 0.55},
        {"at": "L15", "voices": ["drone", "pulse"], "energy": 0.45},
        {"at": "L19", "voices": ["drone", "pad"], "energy": 0.4},
        {"at": "P02", "voices": ["drone"], "energy": 0.25},
    ],
}
sound = {
    "floor": "grass", "steps_db": -26,
    "ambience": [{"kind": "crickets", "from": 0, "to": "end", "lufs": -44},
                 {"kind": "wind", "from": 0, "to": "end", "lufs": -46}],
    "sfx": sfx,
    "music_drops": [{"from": "P01", "to": "P01>"}],
    "rev": REV,
}
remap_all(sfx)
remap_all(music["sections"])
remap_all(sound["ambience"])
remap_all(sound["music_drops"])
polish = {"reveal": [remap("L15b"), remap("L20.2")], "twist": remap("L15b"), "emph": [remap("L02"), remap("L15b")],
          "quiet": [], "hold": sorted(set(hold + ["S29"])), "sway": [], "reframe_every": 0.8}
story = {
    "slug": "ep145-dog-barks",
    "title": "Our Dog Barked ONCE, Then Twice",
    "made_for_kids": False,
    "premise": ("In our town a dog barks once for a stranger who means well and twice for one who doesn't, and our "
                "dog barked once at my sister's fiance at the gate and twice when I was alone with him at the grill."),
    "twist": ("The trusted source contradicts itself: there are clues both ways (he knew the dog's name and pocketed "
              "Grandma's ring box, but the dog shared its toy with him and the second bark was aimed past him at the "
              "open gate), and I ask which bark to trust."),
    "world": ("Our sunny backyard on a Sunday: a green lawn, a white picket fence with a side gate, a red brick patio, "
              "a kettle grill, a picnic table with a gingham cloth, bunting, and the back of our yellow house."),
    "voice": {"voice": "am_adam", "tempo": 1.03, "rate": 1.45},
    "key_color": "#ff6a3d",
    "gap": 0.15,
    "tail": 0.0,
    "fade_in": False,
    "fade_out": False,
    "rev": REV,
    "look": {"style": "closer", "fog": "#dff1ff", "fog_density": 0.001, "fog_start": 60.0, "sky": "#8fd3ff",
             "sky_strength": 1.0, "exposure": 0.0, "flash_safe": True, "polish": polish},
    "grade": {"shadows": [0.0, 0.0, 0.015], "highlights": [0.02, 0.01, -0.01], "saturation": 1.05, "contrast": 1.03,
              "vignette": 0.12, "bloom": 0.1, "grain": 0.008},
    "hud": {"object": "tag", "at": [-0.4, 0.62], "size": 0.5},
    "cast": cast,
    "lines": lines,
    "shots": shots,
    "acting": acting,
    "cues": cues,
    "fx": fx,
    "music": music,
    "sound": sound,
    "set_moves": [],
    "framing_ok": ["S03", "S05", "S11b", "S19", "S20", "S22", "S22b"],
    "frames_ok": ["S02", "S06", "S15", "S19b", "S24", "S27", "S28"],
    "staging_ok": ["S11b/me+grant"],
    "phonemes": {},
    "homophones": {},
}
OUT.write_text(json.dumps(story, indent=1, ensure_ascii=False) + "\n")
print("wrote", OUT, f"({len(shots)} shots, {len(cues)} cues)")
