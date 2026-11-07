"""Writes ../story.json for ep136 "one answer" (script.md, 2026-11-06, batch 15a, interactive lane). Run:
python stories/ep136-one-answer/generator/make_story.py

The words are in lines.json; places are in ../layout.py (shared with set.py). A character facing -y has yaw 0,
+x 90, +y 180, -x -90. Time references use the script's chunk numbers (remapped through timeline.split_lines).
Lane staging: one slow light change (cue "dusk", 1.5 s, on the held wide S23a); nothing blinks; at most one face in any
shot; every sit/stand/turn is eased over 0.4 s or more, or on a cut; the rule marker (the post) is in the scene and
is moved only on cuts.
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
REV = 3
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
X = {"neutral": "neutral", "uneasy": "worried", "stunned": "wide", "scared": "scared", "smile": "smile",
     "laugh": "laugh", "shout": "neutral"}


def person(skin, shirt, pants, shoes, hair="cap", hair_c="#2a1d15", pattern="solid", pattern_c=None, hat="none",
           hat_c="#333333", extras=(), eyes="round", sleeves="long", brow_w=1.0, extra_c=None, **kw):
    d = {"age": "adult", "body_width": 0.6, "skin": skin, "shirt": shirt, "pattern": pattern, "pants": pants, "shoes": shoes,
         "sleeves": sleeves, "hair": hair, "hair_c": hair_c, "hat": hat, "hat_c": hat_c,
         "face": {"eyes": eyes, "brows": True, "ink": "#1c120c"}}
    if brow_w != 1.0:
        d["face"]["brow_w"] = brow_w
    if pattern_c:
        d["pattern_c"] = pattern_c
    if extras:
        d["extras"] = list(extras)
    if extra_c:
        d["extra_c"] = extra_c
    d.update(kw)
    return d


cast = {
    # Eli: short black curly hair, brown skin, a mustard work shirt over a white tee, jeans
    "me": person("#9a6a44", "#e0b23a", "#3d5a8c", "#3a2a20", hair="cap", hair_c="#15100c", collar="#fafaf5",
                 brow_w=1.3),
    # Mrs. Ruiz: a flour-dusted white apron over a red dress, dark hair in a bun
    "ruiz": person("#d9a47a", "#c8302a", "#7a2a2a", "#4a2a1a", hair="bun", hair_c="#2a1a14", eyes="lashes",
                   extras=["apron"], extra_c="#f4f0e6"),
    # Kofi: a green hoodie, short hair
    "kofi": person("#7a5232", "#4a9a5a", "#34405a", "#2a2a2e", hair="buzz", hair_c="#15100c", extras=["hooddown"],
                   extra_c="#3a7a4a", brow_w=1.3),
    # Mr. Bell: white hair, a brown cardigan
    "bell": person("#e2b088", "#8a5a34", "#4a4a50", "#2f2a26", hair="cap", hair_c="#f2f2f0", pattern="knit",
                   pattern_c="#6a4222", collar="#e8e4d8", brow_w=1.3),
}
acting = {n: [] for n in cast}
last = {n: [0, 0] for n in cast}
cues = []
SH = []


def key(who, at, pos=None, **kw):
    p = list(pos) if pos is not None else list(last[who])
    if "expr" in kw:
        kw["expr"] = X.get(kw["expr"], kw["expr"])
    acting[who].append({"at": at, "pos": p, **kw})
    last[who] = p


def cut(who, at, pos=None, **kw):
    """A key that takes effect at once (no blend): a pose or place that changes on a cut."""
    p = list(pos) if pos is not None else list(last[who])
    acting[who].append({"at": at, "pos": list(last[who]), "blend": 0.0})
    key(who, at, p, blend=0.0, **kw)


def mouth(who, a, b, amt=0.5, flap=True):
    k = {"from": a, "to": b, "mouth": [amt, amt]}
    if flap:
        k["flap"] = True
    acting[who].append(k)


def cue(at, name, **kw):
    cues.append({"at": at, "name": name, **kw})


def cam(tx, ty, tz, w, az, lens, cz=None, push=None):
    """A camera looking at (tx, ty, tz) from az degrees round from the south, far enough off that the frame is w
    metres wide there (the frame is w = d * 13.5 / lens wide at distance d). One key or, with push=(w2, tz2), two."""
    def at_(ww, tzz, czz):
        d = ww * lens / 13.5
        return [round(tx + d * math.sin(az * D2R), 3), round(ty - d * math.cos(az * D2R), 3),
                czz if czz is not None else tzz], [tx, ty, tzz]
    p, t_ = at_(w, tz, cz)
    keys = [[0, p, t_, lens]]
    if push:
        p2, t2 = at_(push[0], push[1], None if cz is None else cz + (push[1] - tz))
        keys.append([1, p2, t2, lens])
    return keys


def camp(pos, tgt, lens, pos2=None, tgt2=None):
    keys = [[0, list(pos), list(tgt), lens]]
    if pos2 is not None or tgt2 is not None:
        keys.append([1, list(pos2 or pos), list(tgt2 or tgt), lens])
    return keys


def shot(sid, at, camera, **kw):
    SH.append((sid, at, camera, kw))


ST = G.ST
SX = G.SEAT
ROCKS = G.ROCK_X
ZR = G.ROCK_Z


def rock_cam(n, w=11.0, push=True):
    """Looks south at rock n from over the lot, framing it w metres wide."""
    x = ROCKS[n - 1]
    tgt = (x, G.WALL_Y, ZR - 2.6)
    lens = 36
    d = w * lens / 13.5
    pos = (x, G.WALL_Y + d, 1.6)
    return camp(pos, tgt, lens, pos2=(x, G.WALL_Y + d * 0.86, 1.8) if push else None)


BELL_CAM = ([2.6, 6.4, 1.5], [-0.4, 1.35, 1.58], 32, [2.4, 6.0, 1.5])


def hidden_all(at, but=()):
    for n in ("me", "ruiz", "kofi", "bell"):
        if n not in but:
            cut(n, at, ST, hidden=True)


# ------------------------------------------------------------------------------------------------ the cast at rest
key("me", 0, [*ST, 0], yaw=0, expr="neutral", head=[0, 0], arms=[0, 0], side=[0, 0], lean=0)
for n in ("ruiz", "kofi", "bell"):
    key(n, 0, [*ST, 0], yaw=0, expr="neutral", head=[0, 0], arms=[0, 0], side=[0, 0], hidden=True)
cue(0, "sit", me=0.0)
cue(0, "post", x=G.POST_RAIL[0], y=G.POST_RAIL[1])
cue(0, "dusk", v=0.0)
cue(0, "show", car=0.0, loaf=0.0, pane=0.0, rim=0.0)
cue(0, "shout", me=0.0, ruiz=0.0, kofi=0.0, bell=0.0)

# ===== 01 the rule (L01, L02)
shot("S01a", 0, cam(0.47, ST[1], 1.62, 1.75, 0, 36, cz=1.62, push=(1.6, 1.62)))
key("me", 0.62, head=[0, 0])
key("me", 0.95, head=[-10, 0], blend=0.3)
shot("S01a2", 0.62, cam(0.4, ST[1], 1.62, 1.4, -15, 36, cz=1.62, push=(1.25, 1.62)))
shot("S01b", "L01.2", cam(G.POST_RAIL[0], G.POST_RAIL[1], 1.6, 1.7, 0, 36, cz=1.6, push=(1.45, 1.6)))
key("me", "L01.2", expr="neutral")
shot("S02", "L02", camp([-4.0, 4.5, 2.4], [0, G.WALL_Y, 6.5], 24, pos2=[-1.5, 4.5, 2.6], tgt2=[0, G.WALL_Y, 7.0]))
shot("S03a", "L03", cam(0.38, ST[1], 1.62, 1.9, 0, 36, cz=1.62, push=(1.7, 1.62)))
cue("L03", "shout", me=1.0)
cue("L03.3", "shout", me=0.0)
key("me", "L03", expr="shout")
shot("S03b", "L03.3", camp([0.0, 5.5, 4.4], [0, G.WALL_Y, 5.0], 20, pos2=[-1.5, 5.0, 4.0]))
shot("S03c", "L03.3+0.7", camp([6.0, 4.0, 2.4], [-1.0, G.WALL_Y, 5.2], 24, pos2=[3.5, 3.6, 2.8]))
key("me", "L03.3", expr="neutral")

# ===== 02 the rule at work (L04 to L12): three people, each alone at the railing


# Mrs. Ruiz
cut("me", "L04", ST, hidden=True)
cut("ruiz", "L04", ST, yaw=0, expr="shout", hidden=False, head=[0, 0])
cue("L04", "shout", ruiz=1.0)
cue("L05", "shout", ruiz=0.0)
shot("S04", "L04", cam(0.0, ST[1], 1.6, 1.75, 4, 36, cz=1.62, push=(1.6, 1.62)))
key("ruiz", "L05", expr="neutral")
shot("S05a", "L05", rock_cam(1))
shot("S05b", "L05.1", rock_cam(2))
shot("S05c", "L05.2", rock_cam(3))
shot("S05d", "L05.2+0.45", rock_cam(3, 9.0))
key("ruiz", "L05b", expr="laugh")
shot("S05e", "L05b", cam(0.0, ST[1], 1.6, 1.6, -5, 36, cz=1.62, push=(1.5, 1.62)))
key("ruiz", "L05b+0.4", head=[0, 0])
key("ruiz", "L05b+0.75", head=[12, 4], blend=0.35)
shot("S05f", "L05b+0.7", cam(0.0, ST[1], 1.6, 1.4, 16, 36, cz=1.55, push=(1.25, 1.6)))
cue("L06", "show", loaf=1.0)
key("ruiz", "L06", expr="laugh", arms=[62, 62])
shot("S06", "L06", cam(0.0, ST[1], 1.35, 1.9, 5, 36, cz=1.4, push=(1.7, 1.4)))
cue("L07", "show", loaf=0.0)
# Kofi
cut("ruiz", "L07", ST, hidden=True, arms=[0, 0])
cut("kofi", "L07", ST, yaw=0, expr="shout", hidden=False, head=[0, 0])
cue("L07", "shout", kofi=1.0)
cue("L08", "shout", kofi=0.0)
shot("S07", "L07", cam(0.0, ST[1], 1.6, 1.75, -4, 36, cz=1.62, push=(1.6, 1.62)))
key("kofi", "L07+0.8", head=[0, 0])
key("kofi", "L07+1.3", head=[-14, 3], blend=0.5)
shot("S07b", "L07+0.92", cam(0.0, ST[1], 1.62, 1.45, 17, 36, cz=1.5, push=(1.3, 1.62)))
key("kofi", "L08", expr="neutral")
shot("S08a", "L08", rock_cam(1))
shot("S08b", "L08.1", rock_cam(2))
shot("S08c", "L08.2", rock_cam(3))
shot("S08d", "L08.2+0.45", rock_cam(3, 9.0))
key("kofi", "L08b", expr="smile")
shot("S08e", "L08b", cam(0.0, ST[1], 1.6, 1.6, 4, 36, cz=1.62, push=(1.45, 1.62)))
key("kofi", "L09", expr="smile", head=[0, 9])
key("kofi", "L09.1", head=[0, -4], blend=0.5)
shot("S09", "L09", cam(0.0, ST[1], 1.6, 1.7, -3, 36, cz=1.62, push=(1.55, 1.62)))
shot("S09b", "L09+0.78", cam(0.0, ST[1], 1.6, 1.45, 16, 36, cz=1.7, push=(1.3, 1.6)))
# Mr. Bell
cut("kofi", "L10", ST, hidden=True)
cut("bell", "L10", ST, yaw=0, expr="shout", hidden=False, head=[0, 0])
cue("L10", "shout", bell=1.0)
cue("L11", "shout", bell=0.0)
shot("S10", "L10", cam(0.0, ST[1], 1.6, 1.75, 3, 36, cz=1.62, push=(1.6, 1.62)))
key("bell", "L11", expr="neutral")
shot("S11a", "L11", rock_cam(1))
shot("S11b", "L11.1", rock_cam(2))
shot("S11c", "L11.2", rock_cam(3))
shot("S11d", "L11.2+0.45", rock_cam(3, 9.0))
# the cut to the lot side: his face, stunned, as "WALTER." lands (camera on the canyon side, the red car behind him),
# then he turns (0.5 s, eased) to the car, and a CUT to the reverse angle from beyond the car: his face, laughing
cut("bell", "L11b", ST, yaw=0, expr="wide", head=[0, 0])
cue("L11b", "show", car=1.0)
cue("L11b", "post", x=-3.0, y=G.POST_RAIL[1])      # the post steps out of the frame, on the cut
key("bell", "L11b+0.66", ST, yaw=180, expr="wide", head=[0, 0], blend=0.5)     # the turn: 22.45 to 22.95, eased
key("bell", "L11b+0.68", expr="laugh", blend=0.0)
shot("S11e", "L11b", camp([0.4, -3.6, 1.05], [0.0, 1.5, 1.58], 30, pos2=[0.3, -3.25, 1.1], tgt2=[0.0, 1.5, 1.58]))
shot("S11f", "L11b+0.68", camp(BELL_CAM[0], BELL_CAM[1], BELL_CAM[2], pos2=BELL_CAM[3]))
cue("L12", "show", car=0.0)
cue("L12", "post", x=G.POST_RAIL[0], y=G.POST_RAIL[1])
shot("S12", "L12", rock_cam(3, 8.0))
x3 = ROCKS[2]
shot("S12b", "L12.2", camp([x3 + 5.0, G.WALL_Y + 19.0, 1.4], [x3, G.WALL_Y, ZR - 2.6], 36,
                           pos2=[x3 + 3.2, G.WALL_Y + 17.0, 1.9]))

# ===== 03 my turn (L13 to L22)
cut("bell", "L12", ST, hidden=True)
cut("me", "L13", ST, yaw=0, expr="smile", hidden=False, head=[0, 0])
shot("S13", "L13", cam(0.47, ST[1], 1.62, 1.75, 0, 36, cz=1.62, push=(1.65, 1.62)))
key("me", "L14", expr="neutral")
shot("S14", "L14", cam(0.72, ST[1], 1.5, 2.2, 0, 36, cz=1.6, push=(2.05, 1.55)))
shot("S14b", "L14+0.95", cam(0.6, ST[1], 1.5, 1.9, -15, 36, cz=1.45, push=(1.7, 1.55)))
key("me", "L15", expr="uneasy")
shot("S15", "L15", cam(0.32, ST[1], 1.62, 1.5, 6, 36, cz=1.62, push=(1.35, 1.62)))
key("me", "L16", expr="uneasy")
key("me", "L16.2", expr="stunned")
shot("S16", "L16", cam(0.32, ST[1], 1.62, 1.5, 3, 36, cz=1.62, push=(1.35, 1.62)))
key("me", "L17", expr="shout")
cue("L17", "shout", me=1.0)
cue("L18", "shout", me=0.0)
shot("S17", "L17", cam(0.47, ST[1], 1.62, 1.75, 0, 36, cz=1.62, push=(1.65, 1.62)))
key("me", "L18", expr="neutral")
shot("S18", "L18", rock_cam(1, 11.0))
key("me", "L19", expr="shout")
cue("L19", "shout", me=1.0)
cue("L20", "shout", me=0.0)
shot("S19", "L19", cam(0.0, ST[1], 1.3, 1.1, 0, 36, cz=1.3, push=(1.0, 1.3)))
shot("S19c", "L19+0.8", cam(0.0, ST[1], 1.3, 1.25, 17, 36, cz=1.25, push=(1.1, 1.3)))
shot("S19b", "P1", camp([-2.6, 3.5, 2.4], [0, G.WALL_Y, 6.0], 24, pos2=[-1.6, 2.0, 2.5]))
key("me", "L20", expr="scared")
shot("S20", "L20", cam(0.0, ST[1], 1.62, 1.3, 0, 36, cz=1.62, push=(1.15, 1.62)))
shot("S21", "L21", camp([-1.5, 6.0, 3.0], [0, G.WALL_Y, 7.0], 18, pos2=[-1.0, 3.0, 2.8], tgt2=[0, G.WALL_Y, 7.0]))
cut("me", "L21", ST, hidden=True)
cut("me", "L22", ST, yaw=0, expr="uneasy", hidden=False, head=[0, 0])
shot("S22", "L22", cam(0.32, ST[1], 1.62, 1.5, 2, 36, cz=1.62, push=(1.35, 1.62)))

# ===== 04 the truck (L23 to L26): I have walked to the truck on the cut; dusk comes in over 1.5 s on the wide
cut("me", "L23", [SX[0], SX[1], SX[2]], yaw=0, expr="uneasy", head=[0, 0])
cue("L23", "sit", me=1.0)
cue("L23", "dusk", v=1.0, dur=1.5)
shot("S23a", "L23", camp([-2.2, -2.6, 3.2], [G.XT - 0.9, 4.6, 1.2], 20, pos2=[-1.9, -2.0, 3.1]))
key("me", "L23.1", expr="uneasy")
cue("L23.1", "post", x=G.POST_BEHIND[0], y=G.POST_BEHIND[1])
shot("S23b", "L23.1", cam(G.XT - 0.2, G.YT, 1.2, 2.0, 0, 36, cz=1.6, push=(1.85, 1.25)))
key("me", "L24", expr="scared")
mouth("me", "L24", "L24>", 0.35)
shot("S24", "L24", cam(SX[0], G.YT, 1.35, 1.15, 0, 36, cz=1.6, push=(1.05, 1.4)))
# three rocks at dusk, seen from the cab
def cab_rock(n):
    x = ROCKS[n - 1]
    return camp([G.XT + 0.35, SX[1] + 0.4, 1.75], [x, G.WALL_Y, ZR - 1.6], 50)


def win_cue(at, n, lens=50, d=0.7):
    """The window edge for rock n's cab shot: a bar down the left side and a lip along the bottom, d metres ahead of
    the camera's first key (world objects, placed just inside the truck window)."""
    p, t_ = cab_rock(n)[0][1], cab_rock(n)[0][2]
    f = [t_[i] - p[i] for i in range(3)]
    ln = math.sqrt(sum(c * c for c in f))
    f = [c / ln for c in f]
    right = [f[1], -f[0], 0.0]
    rn = math.hypot(right[0], right[1])
    right = [c / rn for c in right]
    up = [right[1] * f[2] - right[2] * f[1], right[2] * f[0] - right[0] * f[2], right[0] * f[1] - right[1] * f[0]]
    hw = d * 13.5 / lens / 2
    hh = hw * 16 / 9
    pc = [p[i] + f[i] * d - right[i] * (hw - 0.0075) + up[i] * 0.0 for i in range(3)]
    qc = [p[i] + f[i] * d - up[i] * (hh - 0.012) for i in range(3)]
    cue(at, "win", on=1.0, px=round(pc[0], 3), py=round(pc[1], 3), pz=round(pc[2], 3), qx=round(qc[0], 3),
        qy=round(qc[1], 3), qz=round(qc[2], 3), fx=round(f[0], 4), fy=round(f[1], 4), fz=round(f[2], 4))



cue("L25", "rocks", r1=1.0, r2=0.0, r3=0.0)
cue("L25.1", "rocks", r1=0.0, r2=1.0, r3=0.0)
cue("L25.2", "rocks", r1=0.0, r2=0.0, r3=1.0)
cue("L26", "rocks", r1=1.0, r2=1.0, r3=1.0)
win_cue("L25", 1)
win_cue("L25.1", 2)
win_cue("L25.2", 3)
cue("L26", "win", on=0.0)
shot("S25a", "L25", cab_rock(1))
shot("S25b", "L25.1", cab_rock(2))
shot("S25c", "L25.2", cab_rock(3))
key("me", "L26", expr="stunned")
shot("S26", "L26", cam(G.XT - 0.1, G.YT, 1.35, 1.45, 0, 36, cz=1.65, push=(1.35, 1.4)))
shot("S26b", "L26+0.8", cam(G.XT - 0.1, G.YT, 1.35, 1.45, 16, 36, cz=1.5, push=(1.3, 1.4)))

# ===== 05 no answer (L27 to L32)
cue("L27", "post", x=G.POST_AHEAD[0], y=G.POST_AHEAD[1])
cue("L27", "show", rim=1.0)
cut("me", "L27", [*SX], hidden=True)       # out of the cab view (the camera sits where I sit)
shot("S27", "L27", camp([SX[0] + 0.4, SX[1] + 0.6, 1.62], [G.POST_AHEAD[0], G.POST_AHEAD[1], 1.9], 36,
                        pos2=[SX[0] + 0.4, SX[1] - 0.2, 1.64]))
shot("S28", "L28", camp([G.POST_AHEAD[0] + 0.1, G.POST_AHEAD[1] + 4.6, 2.15], [G.POST_AHEAD[0], G.POST_AHEAD[1], 1.95],
                        36, pos2=[G.POST_AHEAD[0] + 0.1, G.POST_AHEAD[1] + 4.2, 2.15]))
shot("S28b", "L28+0.6", camp([G.POST_AHEAD[0] + 0.8, G.POST_AHEAD[1] + 3.7, 1.6],
                             [G.POST_AHEAD[0], G.POST_AHEAD[1], 1.9], 36,
                             pos2=[G.POST_AHEAD[0] + 0.4, G.POST_AHEAD[1] + 3.3, 1.75]))
cue("L29", "show", pane=1.0)
shot("S29", "L29", camp([G.XT + 0.8, G.YT - 0.1, 1.5], [G.XT - 1.0, G.YT - 0.1, 1.5], 11,
                        pos2=[G.XT + 0.7, G.YT - 0.1, 1.5]))
shot("S29b", "L29+0.9", camp([G.XT + 0.7, G.YT + 0.45, 1.45], [G.XT - 1.0, G.YT - 0.1, 1.6], 14,
                             pos2=[G.XT + 0.6, G.YT + 0.3, 1.5]))
cue("L30", "panepos", x=-1.0, y=0.5, rz=-90.0, s=0.7)
cut("me", "L30", [*SX], yaw=0, expr="scared", head=[0, 0], hidden=False)
key("me", "L30.0+0.2", expr="scared", head=[-62, 0], blend=0.6)
shot("S30", "L30", cam(SX[0] - 0.4, G.YT, 1.4, 1.55, 0, 36, cz=1.55, push=(1.45, 1.42)))
cue("L31", "show", pane=0.0)
cue("L31", "post", x=G.POST_AHEAD[0], y=G.POST_AHEAD[1])
cut("me", "L31", [*SX], hidden=True)
shot("S31a", "L31", rock_cam(1, 11.0))
shot("S31b", "L31.1", camp([SX[0] + 0.4, SX[1] + 0.6, 1.62], [G.POST_AHEAD[0], G.POST_AHEAD[1], 1.9], 36,
                           pos2=[SX[0] + 0.4, SX[1] + 0.1, 1.64]))
cue("L32", "post", x=G.POST_BEHIND[0], y=G.POST_BEHIND[1])
cue("L32", "show", rim=0.0)
cut("me", "L32", [*SX], yaw=0, expr="scared", head=[0, 0], hidden=False)
shot("S32", "L32", cam(G.XT - 0.1, G.YT, 1.35, 1.45, 0, 36, cz=1.65, push=(1.35, 1.4)))

# ------------------------------------------------------------------------------------------------ finish
remap_all(cues)
for k_ in acting.values():
    remap_all(k_)
shots = []
for i, (sid, at, camera, kw) in enumerate(SH):
    s = {"id": sid, "cam": camera, "step": 2}
    if i:
        s["at"] = remap(at)
    s.update({k: v for k, v in kw.items() if not k.startswith("_")})
    shots.append(s)

music = {
    "root": 50, "mode": "minor", "bpm": 96, "seed": 136,
    "sections": [
        {"at": 0, "voices": ["pluck", "pulse"], "energy": 0.35},
        {"at": "L13", "voices": ["pluck", "pulse", "pad"], "energy": 0.4},
        {"at": "L18", "voices": ["drone", "pad"], "energy": 0.45},
        {"at": "L23", "voices": ["drone", "pad", "pulse"], "energy": 0.5},
    ],
}
sound = {
    "floor": "gravel", "steps_db": -26,
    "ambience": [{"kind": "wind", "from": 0, "to": "end", "lufs": -42}],
    "sfx": [{"at": "L29.1", "kind": "knock", "pattern": [0, 0.45, 0.9], "tone": "glass_soft", "db": -14},
            {"at": "L01.2", "kind": "hit", "db": -14}, {"at": "L12.2", "kind": "hit", "db": -14},
            {"at": "L23.1", "kind": "door", "db": -16}, {"at": "L31.1", "kind": "hit", "db": -14}, {"at": "L26", "kind": "hit", "db": -14},
            {"at": "L16.2", "kind": "thud", "db": -16}],
    "music_drops": [["L19>", "L20"]],
    "rev": REV,
}
remap_all(sound["sfx"])
remap_all(sound["ambience"])
remap_all(music["sections"])
sound["music_drops"] = [[remap(a), remap(b)] for a, b in sound["music_drops"]]
polish = {"emph": ["L01.2", "L12.2", "L16.2", "L28.1", "L31.1", "L32.1"], "reveal": ["L19"],
          "twist": "L20", "sway": ["S03a", "S04", "S07", "S10", "S13", "S14", "S15", "S16", "S17", "S19", "S20", "S22", "S24", "S26", "S30", "S32", "S02", "S05a", "S05b", "S05c", "S05d", "S08a", "S08b", "S08c", "S08d", "S11a", "S11b", "S11c", "S11d", "S12", "S18", "S21", "S31a"], "hold": ["S11e", "S11f", "S23a", "S29", "S28", "S25a", "S25b", "S25c"]}
polish["emph"] = [remap(x) for x in polish["emph"]]
polish["reveal"] = [remap(x) for x in polish["reveal"]]
polish["twist"] = remap(polish["twist"])
story = {
    "slug": "ep136-one-answer",
    "title": "My Echo Answered TWICE",
    "made_for_kids": False,
    "premise": ("At a canyon overlook your echo answers one question, on three, starting with your name; I ask who is "
                "coming with my brother, who lives alone but said we, and it answers twice."),
    "twist": ("The first answer came too fast and without my name, saying don't open the door; the second kept the "
              "rule's timing and my name, which should not happen, saying open it because Nate is scared; someone is "
              "knocking, saying my name. The ending leaves it open: which echo do I trust?"),
    "world": ("A red-gold canyon overlook: a wooden railing, a thick post painted with a huge cream numeral one, a far "
              "wall in bands with three painted rocks marked with one, two and three dots, and a dirt lot with a teal "
              "pickup."),
    "voice": {"voice": "am_adam", "tempo": 1.03, "rate": 1.45},
    "key_color": "#ffc93a",
    "gap": 0.15,
    "asr_ignore_tail_repeat": True,
    "homophones": {"opened": "open"},
    "tail": 0.25,
    "fade_in": False,
    "fade_out": False,
    "rev": REV + 1,
    "look": {"style": "closer", "fog": "#e8d8c0", "fog_density": 0.0008, "fog_start": 60.0, "sky": "#c8dcf0",
             "sky_strength": 1.0, "exposure": 0.05, "flash_safe": True, "polish": polish},
    "grade": {"shadows": [0.0, 0.0, 0.02], "highlights": [0.03, 0.012, -0.02], "saturation": 1.06, "contrast": 1.04,
              "vignette": 0.15, "bloom": 0.15, "grain": 0.008},
    "cast": cast,
    "lines": lines,
    "shots": shots,
    "acting": acting,
    "cues": cues,
    "fx": [],
    "music": music,
    "sound": sound,
    "set_moves": [],
    "framing_ok": ["S02", "S05a", "S05b", "S05c", "S05d", "S08a", "S08b", "S08c", "S08d", "S11a", "S11b", "S11c", "S11d", "S12", "S18", "S21", "S25a", "S25b", "S25c", "S28", "S29", "S31a"],   # the clue rocks and the far wall: no person on purpose
}
OUT.write_text(json.dumps(story, indent=1, ensure_ascii=False) + "\n")
print("wrote", OUT, f"({len(shots)} shots, {len(cues)} cues)")
