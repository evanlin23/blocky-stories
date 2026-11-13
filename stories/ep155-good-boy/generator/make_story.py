"""Writes ../story.json for ep155 "Lost Dogs Here Walk Home As PEOPLE" (script.md, 2026-11-12, batch 15, warm lane).
Run: python stories/ep155-good-boy/generator/make_story.py

Words are in lines.json; places in ../layout.py (shared with set.py). A character facing -y has yaw 0, +x 90, +y 180,
-x -90. Cues (read by set.py): keyb, clock, tod, door, photo, wiggle, leash, sausage, vac, mug, strap, curtain, pose, dog, thump.
Nothing ever blinks; the time of day changes only on a cut.
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
REV = 5
orig_lines = json.loads((HERE / "lines.json").read_text())
lines, CHUNKMAP = T.split_lines(orig_lines)
# the reveal picture is held 1.6 s: a silent beat after "Good BOY." and a closing beat after the last thump
i21 = next(i for i, l in enumerate(lines) if l["id"] == "L21")
lines.insert(i21 + 1, {"id": "P01", "pause": 0.8, "chunks": [["", ""]]})
lines.append({"id": "P02", "pause": 0.9, "chunks": [["", ""]]})


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
X = {"neutral": "neutral", "uneasy": "worried", "stunned": "wide", "sad": "soft", "smile": "smile",
     "laugh": "laugh", "scared": "scared", "warm": "warm", "sheepish": "polite"}


def person(skin, shirt, pants, shoes, hair="cap", hair_c="#15151a", hat="none", eyes="round", sleeves="long", **kw):
    d = {"age": "adult", "skin": skin, "shirt": shirt, "pants": pants, "shoes": shoes, "sleeves": sleeves,
         "hair": hair, "hair_c": hair_c, "hat": hat, "face": {"eyes": eyes, "brows": True, "ink": "#1c120c"}}
    d.update(kw)
    return d


cast = {
    # me (Pepper as a man, about 20): lanky, white block hair (a black streak and an ear patch are added in set.py)
    "me": person("#f1c9a0", "#c4562a", "#3d5a8a", "#f2f2f2", hair="cap", hair_c="#f6f3ec", height=1.06, width=0.97,
                 collar="#a8421c"),
    # Mr. Dale, fifties: short gray hair, round glasses, a gray moustache (set.py), a green cardigan over white
    "dale": person("#e0b890", "#5d8a4a", "#6a6a74", "#4a3a2a", hair="buzz", hair_c="#a9a9b2",
                    collar="#f8f4ea", width=1.05),
    # Rory, 16: black flat-top (set.py), a yellow T-shirt
    "rory": person("#c58e64", "#ffd23f", "#3a5a9a", "#f2f2f2", hair="buzz", hair_c="#15151a", sleeves="short",
                   age="teen"),
    # Mrs. Ortiz, sixties: silver curls, a lilac housecoat
    "ortiz": person("#e6c19a", "#b79adf", "#9a82c8", "#d8d0e8", hair="mop", hair_c="#cfcfd8", eyes="lashes",
                    collar="#f4eaff"),
    # her poodle as a man: white curly block hair and a huge curly cream fur coat (set.py adds the fur)
    "poodleman": person("#e8c8a8", "#f2ecde", "#d8d2c6", "#c8c2b6", hair="mop", hair_c="#faf6ee", extras=["coat"],
                        collar="#fffaf0", width=1.1),
    # the mail carrier, forties: navy cap, light blue shirt, navy shorts' trousers, a brown bag (no lettering)
    "mail": person("#a96f4a", "#9ac0e8", "#1d2f5a", "#2a2a30", hair="buzz", hair_c="#15151a", hat="ballcap",
                   hat_c="#1d2f5a", sleeves="short", extras=["backpack"], extra_c="#8a5a2a"),
    # the man who can't read the blank sign: a burgundy cardigan
    "walker": person("#d9b48a", "#8a3a4a", "#b9a47a", "#3a2a1a", hair="buzz", hair_c="#6a4a2a", collar="#f8f4ea"),
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


HZ = {"walker": 1.65, "me": 1.75, "mesit": 1.40, "dale": 1.70, "dalesit": 1.48, "rorysit": 1.15}   # head centre above the deck (or the ground)


def fc(x, y, hz, w, az, lens, up=0.12, push=None):
    """A camera whose frame is w metres wide at (x, y) with the head at height hz sitting `up` of the frame's height above the middle."""
    cz = round(hz - up * w * 16 / 9, 3)
    return cam(x, y, cz, w, az, lens, cz=cz, push=push)


def camp(pos, tgt, lens, pos2=None, tgt2=None):
    keys = [[0, list(pos), list(tgt), lens]]
    if pos2 is not None or tgt2 is not None:
        keys.append([1, list(pos2 or pos), list(tgt2 or tgt), lens])
    return keys


def shot(sid, at, camera, **kw):
    SH.append((sid, at, camera, kw))


for who in cast:
    key(who, 0, [0, 0, 0], yaw=0, expr="neutral", head=[0, 0], arms=[0, 0], side=[0, 0], hidden=True)

HX, FY, DECK = G.HX, G.FY, G.DECK
SM, SR, SD = G.SEAT_ME, G.SEAT_RORY, G.SEAT_DALE
FACE_Z = DECK + 1.0        # a seated head's centre, about
cue(0, "clock", s="8:00")
cue(0, "tod", v="day")
for nm in ("door", "photo", "wiggle", "sausage", "vac", "mug", "strap", "curtain", "keyb"):
    cue(0, nm, v=0.0)
cue(0, "leash", v=1.0)
cue(0, "sausage", v=1.0)
cue(0, "dog", v=0.0)


def sit(at, who, v=1.0, dur=0.0, kneel=0.0):
    cue(at, "pose", who=who, sit=v, kneel=kneel, dur=dur)


# ----------------------------------------------------------------------------------------------- 01 the rule
PEGF = (G.PEG_X - 1.05, 11.35)                  # me standing left of the peg
show(0, "me")
place(0, "me", (PEGF[0], PEGF[1], DECK), 0, "smile", head=[-25, 8])
shot("S01a", 0, cam(61.1, 11.7, DECK + 1.3, 2.3, -6, 36, cz=DECK + 1.3))
key("me", "L01.1", yaw=0, expr="smile", head=[-10, 14], blend=0.35)
shot("S01b", "L01.1+0.35", fc(PEGF[0] + 0.4, PEGF[1], DECK + HZ["me"], 2.0, -8, 36))
place("L01.3", "me", (PEGF[0], PEGF[1], DECK), 0, "smile", head=[0, 0])
shot("S01c", "L01.3", cam(PEGF[0] + 0.35, 11.4, DECK + 1.15, 2.85, -30, 26, cz=DECK + 1.15, push=(2.5, DECK + 1.15)))

# ----------------------------------------------------------------------------------------------- 02 mine
show("L02", "dale")
cue("L02", "door", v=1.0)
place("L02", "dale", (HX + 0.1, FY + 0.55, DECK), 0, "sad", arms=[0, 80])
cue("L02", "mug", v=1.0)
shot("S02a", "L02", cam(HX + 0.1, FY + 0.3, DECK + 1.2, 1.9, 0, 34, cz=DECK + 1.4))
show("L02.3", "rory")
cue("L02.3", "mug", v=0.0)
cue("L02.3", "door", v=0.0)
place("L02.3", "rory", (G.PEG_X - 0.6, 11.3, DECK), 0, "sad", head=[0, 6])
key("rory", "L02.4", yaw=0, expr="sad", head=[-14, 6], blend=0.4)
shot("S02b", "L02.3", cam(G.PEG_X - 0.6, 11.3, DECK + 1.2, 1.9, -14, 34, cz=DECK + 1.35))

# ----------------------------------------------------------------------------------------------- 03 stakes
GATEY = 5.9
show("L03", "me", "dale")
place("L03", "me", (HX - 0.9, GATEY, 0.0), 150, "uneasy", head=[0, 0])
place("L03", "dale", (HX + 0.5, GATEY, 0.0), 210, "sad")
shot("S03a", "L03", camp([HX - 0.2, 9.7, 1.55], [HX - 0.2, GATEY, 1.25], 20, pos2=[HX - 0.2, 9.3, 1.55]))
show("L03.3", "me")
place("L03.3", "me", (HX - 0.9, GATEY, 0.0), 0, "uneasy", head=[-12, 0])
shot("S03c", "L03.3", fc(HX - 0.9, GATEY, HZ["me"], 2.0, -6, 36))

# ----------------------------------------------------------------------------------------------- 04 / 05 the poodle
OX, OY = G.ORT
show("L04", "ortiz")
place("L04", "ortiz", (OX + 1.0, OY - 2.3, 0.0), 0, "smile", arms=[0, 0])
shot("S04a", "L04", cam(OX + 1.0, OY - 2.3, 1.4, 1.6, 6, 34, cz=1.5))
show("L04.2", "poodleman")
place("L04.2", "poodleman", (OX - 0.7, OY - 2.0, 0.0), 0, "sheepish", arms=[0, 0])
shot("S04b", "L04.2", cam(OX - 0.7, OY - 2.0, 1.25, 1.55, -8, 34, cz=1.3))
show("L05-0.15", "poodleman", "ortiz")
place("L05-0.15", "poodleman", (OX - 0.55, OY - 2.1, 0.0), 0, "sheepish", arms=[0, 0])
place("L05-0.15", "ortiz", (OX + 0.85, OY - 2.1, 0.0), 0, "smile", arms=[0, 0])
sit("L05-0.15", "poodleman", 0.0)
sit("L05+0.12", "poodleman", 0.55, 0.4)
shot("S05a", "L05-0.15", camp([OX + 1.8, OY - 6.2, 1.3], [OX - 0.55, OY - 2.1, 1.0], 32, pos2=[OX + 1.4, OY - 5.4, 1.25]))
key("ortiz", "L05.2", yaw=0, expr="smile", arms=[0, 70], head=[18, 0], blend=0.3)
sit("L05.2", "poodleman", 0.55)
shot("S05b", "L05.2", cam(OX + 0.15, OY - 2.1, 1.1, 2.7, 0, 32, cz=1.2))

# ----------------------------------------------------------------------------------------------- 06 dog-people
CX, CY = G.COR
show("L06", "walker")
sit("L06", "poodleman", 0.0)
place("L06", "walker", (CX - 0.45, CY - 0.5, 0.0), 0, "stunned", arms=[0, 0], head=[-40, 4])
shot("S06a", "L06", fc(CX + 0.3, CY + 0.3, HZ["walker"], 2.8, -6, 30, push=(2.65, HZ["walker"])))
place("L06.2", "walker", (CX - 0.45, CY - 0.5, 0.0), 0, "stunned", arms=[0, 0], head=[-40, 4])
key("walker", "L06.3", yaw=0, expr="wide", arms=[70, 70], head=[-30, -4], blend=0.1)
shot("S06b", "L06.2", fc(CX + 0.3, CY + 0.3, HZ["walker"], 2.7, 10, 30, push=(2.4, HZ["walker"])))

# ----------------------------------------------------------------------------------------------- 07 the fine print
sit("L07", "me", 1.0)
show("L07", "me")
place("L07", "me", (SM[0], SM[1], DECK), 0, "smile", head=[0, 4])
shot("S07", "L07", fc(SM[0], SM[1], DECK + HZ["mesit"], 2.0, -22, 36))
key("me", "L07.2", yaw=-24, expr="warm", head=[-6, 0], blend=0.4)
shot("S07b", "L07.2", fc(SM[0], SM[1], DECK + HZ["mesit"], 2.0, -22, 36))

# ----------------------------------------------------------------------------------------------- 08 the step
show("L08")
shot("S08b", "L08", cam(61.55, FY, DECK + 1.2, 1.45, 0, 32, cz=DECK + 1.2, push=(1.2, DECK + 1.2)))
show("L08.3", "me", "rory", "dale")
sit("L08.3", "rory", 1.0)
place("L08.3", "me", (SM[0], SM[1], DECK), 0, "smile", head=[0, 0])
place("L08.3", "rory", (SR[0], SR[1], DECK), 0, "smile", head=[8, 0])
place("L08.3", "dale", (HX - 0.2, FY + 0.55, DECK), 0, "smile")
cue("L08.3", "door", v=1.0)
shot("S08a", "L08.3", fc(58.3, SM[1], DECK + HZ["mesit"], 2.9, 0, 30, up=0.10))
show("L08.5", "rory")
place("L08.5", "rory", (SR[0], SR[1], DECK), 0, "laugh", head=[0, 0])
cue("L08.5", "door", v=0.0)
shot("S08c", "L08.5", fc(SR[0], SR[1], DECK + HZ["rorysit"], 2.0, 14, 36))

# ----------------------------------------------------------------------------------------------- 09 the doorbell
cue("L09", "clock", s="8:02")
cue("L09", "door", v=1.0)
cue("L09", "curtain", v=1.0, dur=0.5)
sit("L09", "me", 0.0)
show("L09", "me")
place("L09", "me", (G.WIN_X + 0.3, FY + 0.9, DECK), 70, "laugh", arms=[0, 0], head=[40, -4])
shot("S09a", "L09", camp([HX + 1.2, 15.4, DECK + 1.7], [G.WIN_X + 0.3, FY + 0.8, DECK + 1.25], 28, pos2=[HX + 0.9, 15.0, DECK + 1.7]))
show("L09.3-0.12", "rory")
place("L09.3-0.12", "rory", (HX - 0.1, FY + 0.45, DECK), 180, "stunned", arms=[0, 0])
shot("S09b", "L09.3-0.12", cam(HX - 0.1, FY + 0.45, DECK + 1.2, 1.8, 180, 34, cz=DECK + 1.3))

# ----------------------------------------------------------------------------------------------- 10 the mail carrier
cue("L10", "curtain", v=0.0)
cue("L10", "door", v=0.0)
show("L10", "mail")
place("L10", "mail", (HX, 4.5, 0.0), 180, "neutral", arms=[0, 0])
shot("S10", "L10", camp([HX - 1.6, 9.2, 1.7], [HX, 4.6, 1.35], 32, pos2=[HX - 1.4, 8.7, 1.65]))
show("L10.1", "rory")
sit("L10.1", "rory", 1.0)
place("L10.1", "rory", (SR[0], SR[1], DECK), 0, "laugh", head=[-18, 0])
shot("S10b", "L10.1", fc(SR[0], SR[1], DECK + HZ["rorysit"], 2.0, 18, 36))

# ----------------------------------------------------------------------------------------------- 11 the photo
cue("L11", "photo", v=1.0)
show("L11", "me")
sit("L11", "me", 1.0)
place("L11", "me", (SM[0], SM[1], DECK), 0, "uneasy", head=[26, 3])
shot("S11a", "L11", cam(59.45, 11.2, DECK + 1.15, 2.3, -30, 32, cz=DECK + 1.3))
show("L11.2")
shot("S11b", "L11.2", cam(HX, FY, DECK + 1.2, 1.2, 0, 32, cz=DECK + 1.25, push=(0.95, DECK + 1.2)))

# ----------------------------------------------------------------------------------------------- 12 the writing
cue("L12", "wiggle", v=0.0)
cue("L12.1", "wiggle", v=1.0, dur=0.3)
show("L12")
shot("S12a", "L12", cam(HX, FY, DECK + 1.0, 1.0, 0, 32, cz=DECK + 1.05, push=(0.8, DECK + 1.0)))
cue("L12.2", "wiggle", v=0.0, dur=0.4)
show("L12.2-0.3", "me")
place("L12.2-0.3", "me", (SM[0], SM[1], DECK), 0, "smile", head=[18, 0])
shot("S12b", "L12.2-0.3", fc(SM[0], SM[1], DECK + HZ["mesit"], 2.0, -18, 36))
show("L12.4", "rory")
place("L12.4", "rory", (SR[0], SR[1], DECK), 0, "stunned", head=[10, 0])
key("rory", "L12.4+0.5", yaw=0, expr="laugh", head=[10, 0], blend=0.2)
shot("S12c", "L12.4", fc(SR[0], SR[1], DECK + HZ["rorysit"], 2.0, 14, 36))

# ----------------------------------------------------------------------------------------------- 13 12:30
cue("L13", "clock", s="12:30")
cue("L13", "vac", v=1.0)
show("L13", "dale")
sit("L13", "me", 0.0)
place("L13", "dale", (HX + 0.1, 11.75, DECK), 0, "smile", arms=[62, 62])
shot("S13a", "L13", camp([HX + 1.9, 8.3, DECK + 1.5], [HX + 0.4, 11.0, DECK + 0.05], 30, pos2=[HX + 1.6, 8.8, DECK + 1.45]))
cue("L13.3", "vac", v=0.0)
show("L13.3", "me")
sit("L13.3", "me", 1.0)
place("L13.3", "me", (G.DECK_X0 + 0.12, 10.8, DECK + 0.95), 0, "uneasy", head=[-20, 0])
shot("S13b", "L13.3", cam(G.DECK_X0 + 0.3, 10.8, DECK + 1.9, 1.6, 22, 36, cz=DECK + 1.95))

# ----------------------------------------------------------------------------------------------- 14 6:40
cue("L14", "clock", s="6:40")
cue("L14", "tod", v="gold")
sit("L14", "me", 0.0)
show("L14")
shot("S14a", "L14", cam(61.55, 10.35, DECK + 0.3, 0.75, 32, 34, cz=DECK + 0.4, push=(0.6, DECK + 0.3)))
shot("S14b", "L14.3", cam(59.75, 10.3, DECK + 0.2, 0.7, 24, 34, cz=DECK + 0.35, push=(0.55, DECK + 0.2)))

# ----------------------------------------------------------------------------------------------- 15 the sausage
show("L15", "me")
sit("L15", "me", 1.0)
place("L15", "me", (SM[0], SM[1], DECK), 0, "sheepish", head=[-22, 8])
shot("S15a", "L15", fc(SM[0] + 0.1, SM[1], DECK + HZ["mesit"], 2.1, -20, 34))
cue("L15.1", "sausage", v=0.0)
place("L15.1+0.1", "me", (SM[0], SM[1], DECK), 0, "smile", head=[-14, 8])
mouth("me", "L15.1", "L15.1+0.5", 0.45)
shot("S15b", "L15.1+0.1", fc(SM[0] + 0.1, SM[1], DECK + HZ["mesit"], 1.8, -16, 34))

# ----------------------------------------------------------------------------------------------- 16 the long look
show("L16", "dale")
place("L16", "dale", (HX + 0.4, 11.4, DECK), 0, "neutral", arms=[0, 0])
shot("S16a", "L16", fc(HX + 0.4, 11.4, DECK + HZ["dale"], 1.9, 8, 34))
key("dale", "L16.3", yaw=0, expr="sad", head=[-8, 0], blend=0.3)
shot("S16c", "L16.2", fc(HX + 0.4, 11.4, DECK + HZ["dale"], 1.8, -6, 36))

# ----------------------------------------------------------------------------------------------- 17 9:58
cue("L17", "clock", s="9:58")
cue("L17", "tod", v="dusk")
cue("L17", "leash", v=0.0)
show("L17")
shot("S17a", "L17", cam(61.55, FY, DECK + 1.2, 1.45, 0, 32, cz=DECK + 1.2, push=(1.2, DECK + 1.2)))
show("L17.2", "dale")
sit("L17.2", "dale", 1.0)
cue("L17.2", "strap", v=1.0)
place("L17.2", "dale", (SD[0], SD[1], DECK), 0, "sad", arms=[62, 62], head=[0, 14])
shot("S17b", "L17.2", fc(SD[0], SD[1], DECK + HZ["dalesit"], 2.1, -14, 34, up=0.16))

# ----------------------------------------------------------------------------------------------- 18 where I sit
show("L18", "dale")
place("L18", "dale", (SD[0], SD[1], DECK), 0, "sad", arms=[62, 62], head=[0, 8])
shot("S18a", "L18", fc(SD[0], SD[1], DECK + HZ["dalesit"], 2.0, -10, 36))
show("L18.2", "me")
sit("L18.2", "me", 1.0)
place("L18.2", "me", (SM[0], SM[1], DECK), 0, "warm", head=[0, 0])
shot("S18b", "L18.2", fc(SM[0] + 0.4, SM[1], DECK + HZ["mesit"], 2.3, -33, 34))

# ----------------------------------------------------------------------------------------------- 19 the nudge
ME19 = (SD[0] - 0.95, SM[1])
show("L19", "me", "dale")
place("L19", "dale", (SD[0], SD[1], DECK), 0, "sad", arms=[62, 62], head=[-20, 14])
place("L19", "me", (SD[0] - 1.0, ME19[1], DECK), 0, "warm", head=[0, 0])
key("me", "L19+0.3", ME19 + (DECK,), yaw=0, expr="warm", head=[30, 14], lean=10, blend=0.7)
shot("S19a", "L19", fc((ME19[0] + SD[0]) / 2, SM[1], DECK + 1.44, 2.4, -12, 34))
key("me", "L19.2", yaw=0, expr="stunned", head=[0, 0], lean=0, blend=0.3)
show("L19.2", "me")
shot("S19b", "L19.2", fc(ME19[0], ME19[1], DECK + HZ["mesit"], 2.0, -14, 36))

# ----------------------------------------------------------------------------------------------- 20 he knelt
KY = 9.2
show("L20", "me", "dale")
place("L20", "me", (ME19[0], ME19[1], DECK), 0, "stunned", head=[0, 0])
place("L20", "dale", (ME19[0], KY, 0.30), 180, "warm", arms=[0, 0])
cue("L20", "strap", v=0.0)
cue("L20", "keyb", v=1.0, dur=0.4)
cue("L21.1", "keyb", v=0.0, dur=0.4)
cue("L20", "pose", who="dale", sit=0.0, kneel=0.0, dur=0.0)
cue("L20+0.1", "pose", who="dale", sit=0.0, kneel=1.0, dur=0.5)
shot("S20a", "L20", camp([ME19[0] - 2.9, 11.6, DECK + 1.2], [ME19[0], 9.8, DECK + 0.7], 24, pos2=[ME19[0] - 2.6, 11.3, DECK + 1.2]))
show("L20.2", "dale")
place("L20.2", "dale", (ME19[0], KY, 0.30), 180, "warm", arms=[0, 0])
cue("L20.2", "pose", who="dale", sit=0.0, kneel=1.0, dur=0.0)
mouth("dale", "L21", "L21.1", 0.4)
shot("S20b", "L20.2", camp([ME19[0] + 0.5, 11.7, DECK + 1.1], [ME19[0], KY, DECK + 1.1], 17, pos2=[ME19[0] + 0.35, 11.5, DECK + 1.1]))

# ----------------------------------------------------------------------------------------------- 21 the reveal
show("L21.1")
cue("L21.1", "dog", v=1.0, x=SM[0], y=SM[1] + 0.1, z=DECK + 0.03, yaw=0.0, sit=1.0, wag=0.6, tongue=1.0)
shot("S21b", "L21.1", camp([SM[0] - 2.1, 7.6, DECK + 0.9], [SM[0] + 0.5, 11.2, DECK + 1.0], 34, pos2=[SM[0] - 1.9, 7.8, DECK + 0.85]),
     )

# ----------------------------------------------------------------------------------------------- 22 thump thump
cue("L22", "thump")
cue("L22.1", "thump")
cue("L22", "dog", v=1.0, x=SM[0], y=SM[1] + 0.1, z=DECK + 0.03, yaw=0.0, sit=1.0, wag=0.0, tongue=1.0)
shot("S22a", "L22", cam(SM[0], SM[1] + 0.25, DECK + 0.45, 2.2, -80, 34, cz=DECK + 0.4, push=(1.9, DECK + 0.45)))
show("P02", "rory")
sit("P02", "rory", 1.0)
place("P02", "rory", (SR[0], SR[1], DECK), 0, "laugh", head=[22, 0])
cue("P02", "dog", v=1.0, x=SM[0], y=SM[1] + 0.1, z=DECK + 0.03, yaw=-40, sit=1.0, wag=1.0, tongue=1.0)
shot("S22b", "P02", cam(58.2, SM[1], DECK + 0.8, 2.3, -4, 30, cz=DECK + 0.8))

# ----------------------------------------------------------------------------------------------- finish
remap_all(cues)
for k_ in acting.values():
    remap_all(k_)
shots = []
for i, (sid, at, camera, kw) in enumerate(SH):
    if len(camera) == 1:
        _, p0, t0, ln = camera[0]
        camera = camera + [[1, [round(p0[j] + 0.17 * (t0[j] - p0[j]), 3) for j in range(3)], list(t0), ln]]
    s = {"id": sid, "cam": camera, "step": 2}
    if i:
        s["at"] = remap(at)
    s.update({k: v for k, v in kw.items() if not k.startswith("_")})
    shots.append(s)

sfx = [
    {"at": "L09.1", "kind": "bell", "db": -17},
    {"at": "L22", "kind": "thud", "db": -12},
    {"at": "L22.1", "kind": "thud", "db": -12},
]
music = {
    "root": 55, "mode": "major", "bpm": 104, "seed": 155,
    "sections": [
        {"at": 0, "voices": ["pluck_hi", "pulse", "bubble"], "energy": 0.55},
        {"at": "L17", "mode": "minor", "root": 52, "voices": ["pad", "pluck"], "energy": 0.3},
        {"at": "L21", "mode": "major", "root": 55, "voices": ["pad", "pluck_hi", "choir"], "energy": 0.55},
        {"at": "L22", "voices": ["pad", "pluck_hi"], "energy": 0.4},
    ],
}
sound = {
    "floor": "wood", "steps_db": -22,
    "ambience": [{"kind": "hum", "from": "L13.1", "to": "L13.3", "lufs": -36},
                 {"kind": "crickets", "from": "L17", "to": "end", "lufs": -42}],
    "sfx": sfx,
    "music_drops": [],
    "rev": REV,
}
remap_all(sfx)
remap_all(music["sections"])
remap_all(sound["ambience"])
polish = {"reveal": ["L21.1"], "twist": "L21", "emph": ["L01.1", "L21.1", "L05.2", "L22"],
          "quiet": [["L17", "L19>"]], "hold": ["S08b", "S11b"], "sway": []}
polish["emph"] = [remap(x) for x in polish["emph"]]
polish["reveal"] = [remap(x) for x in polish["reveal"]]
polish["twist"] = remap(polish["twist"])
polish["quiet"] = [[remap(a), remap(b)] for a, b in polish["quiet"]]
DUSK = ["S17a", "S17b", "S18a", "S18b", "S19a", "S19b", "S20a", "S20b", "S21b", "S22a", "S22b"]
story = {
    "slug": "ep155-good-boy",
    "title": "Lost Dogs Here Walk Home As PEOPLE \U0001F43E",
    "made_for_kids": False,
    "premise": ("In this town a lost dog walks home as a person, and nobody may call its name until it is home, so the "
                "man who spends the whole day on his favorite neighbors' porch waiting with them for their lost spaniel "
                "does not know he is the dog."),
    "twist": ("Mr. Dale kneels and says You're home, Pepper, good boy, and the narrator, who ate the sausage set out "
              "for Pepper and sat on the step where Pepper always waited, is the spaniel."),
    "world": ("A sunny street of pastel houses, the Dales' butter-yellow house with a wooden porch step, a blue leash "
              "on a peg and a photo taped to the front door, then golden hour, then a blue dusk with the porch light on."),
    "voice": {"voice": "am_adam", "tempo": 1.03, "rate": 1.45},
    "key_color": "#ff9a3c",
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
    "set_moves": ["S13a"],
    "shot_grades": {sid: {"highlights": [0.0, 0.0, 0.015], "shadows": [0.0, 0.01, 0.05], "saturation": 0.98} for sid in DUSK},
    "framing_ok": [],
    "frames_ok": [],
    "staging_ok": [],
    "asr_forgive": ["missus ortiz's", "eight oh two", "twelve thirty mister", "six forty", "nine fifty eight"],
    "phonemes": {"Ortiz": "ˈɔɹtɪz", "Rory": "ɹˈɔɹi"},
}
OUT.write_text(json.dumps(story, indent=1, ensure_ascii=False) + "\n")
print("wrote", OUT, f"({len(shots)} shots, {len(cues)} cues)")
