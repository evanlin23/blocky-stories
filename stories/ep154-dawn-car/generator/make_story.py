"""Writes ../story.json for ep154 "Dad's Empty Car Leaves Every DAWN" (script.md, 2026-11-12, batch 15, warm lane).
Run: python stories/ep154-dawn-car/generator/make_story.py

Words are in lines.json; places in ../layout.py (shared with set.py). A character facing -y has yaw 0, +x 90,
+y 180, -x -90. Cues (read by set.py): clock, car_dad, car_mom, car_boss, ride, door_p, door_d, wheel, heater,
pseat, lock, muffin, plate, mug, crumbs, blush, sit_<who>. Nothing ever blinks or pulses: everything eases.
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
X = {"neutral": "neutral", "uneasy": "worried", "stunned": "wide", "smile": "smile", "laugh": "laugh",
     "scared": "scared", "warm": "warm", "sheepish": "polite", "sly": "smirk", "worried": "worried"}


def person(skin, shirt, pants, shoes, hair="cap", hair_c="#15151a", hat="none", eyes="round", sleeves="long",
           **kw):
    d = {"age": "adult", "skin": skin, "shirt": shirt, "pants": pants, "shoes": shoes, "sleeves": sleeves,
         "hair": hair, "hair_c": hair_c, "hat": hat, "face": {"eyes": eyes, "brows": True, "ink": "#1c120c"}}
    d.update(kw)
    return d


SKIN = "#9a6440"
cast = {
    # me: a man of 20, a big black curly top (curls in set.py), warm brown skin, a red hoodie, jeans
    "me": person(SKIN, "#d8322f", "#3a5a8a", "#f2f2f2", hair="mop", extras=["hooddown"], extra_c="#b82a28"),
    # Dad, fifties: short gray hair, a round gray beard (set.py), glasses, a blue work jacket over a plaid shirt
    "dad": person(SKIN, "#2f5fa0", "#5a5048", "#3a2a20", hair="buzz", hair_c="#505054", extras=["glasses"],
                  extra_c="#2a2a30", collar="#c8443a", width=1.05),
    # Mom, fifties: a high black bun, lashes, a pink robe
    "mom": person(SKIN, "#dc6f9a", "#dc6f9a", "#f6e6ee", hair="bun", eyes="lashes", collar="#e88ab0"),
    # the cook, about 20: very tall, a shaved head, deep brown skin, a white apron over a green T-shirt
    "cook": person("#6a3f24", "#3f9a4a", "#585c72", "#2a2a30", hair="none", sleeves="short", extras=["apron"],
                   extra_c="#ecebe4", height=1.12),
    # Mr. Fenn: a straw hat, a sunny shirt; his boss: a gray suit and a tie
    "fenn": person("#e6c19a", "#4ab8d8", "#e8dcc0", "#f2f2f2", hair="cap", hair_c="#8a5a30", hat="fedora",
                   hat_c="#e8cf7a", band_c="#c8443a", sleeves="short"),
    "boss": person("#d9b48a", "#8a8f99", "#7a7f88", "#2a2a30", hair="cap", hair_c="#3a2a20", extras=["tie"],
                   extra_c="#c8443a", collar="#f2f2f2"),
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


SEAT_OF = {}


def show(at, *names):
    for n in cast:
        if n in names and n not in vis:
            vis.add(n)
            cut(n, at, hidden=False)
        elif n not in names and n in vis:
            vis.discard(n)
            cut(n, at, hidden=True)


def pose(yaw=0, expr="neutral", **kw):
    d = dict(yaw=yaw, expr=expr, head=[0, 0], arms=[0, 0], side=[0, 0], lean=0)
    d.update(kw)
    return d


def stand(at, who, pos, yaw=0, expr="neutral", **kw):
    """Cut `who` to pos (standing) with a pose at `at`, visible."""
    if who not in vis:
        vis.add(who)
        cut(who, at, hidden=False)
    if SEAT_OF.get(who):
        cue(at, f"sit_{who}", v=0.0)
        SEAT_OF[who] = None
    cut(who, at, [pos[0], pos[1], pos[2] if len(pos) > 2 else 0.0], **pose(yaw, expr, **kw))


def sit(at, who, car, seatname, expr="neutral", sink=0.0, arms=(28, 28), inward=0.0, **kw):
    """Cut `who` into a car seat (or a kitchen chair: car=None, seatname=(x, y, yaw))."""
    h = cast[who].get("height", 1.0)
    if car is None:
        x, y, yaw = seatname
        p = (x, y, G.CHAIR_Z + 0.17 - 0.68 * h - sink)
    elif inward:
        lx, ly = G.SEATS[seatname]
        lx = lx - inward if lx > 0 else lx + inward
        p, yaw = G.to_world(car, lx, ly, G.CUSH + 0.17 - 0.68 * h - sink), (car[3] + 180) % 360
    else:
        p, yaw = G.seat(car, seatname, h, sink)
    if who not in vis:
        vis.add(who)
        cut(who, at, hidden=False)
    if not SEAT_OF.get(who):
        cue(at, f"sit_{who}", v=1.0)
    SEAT_OF[who] = True
    cut(who, at, list(p), **pose(yaw, expr, arms=list(arms), **kw))
    return list(p), yaw


def mouth(who, a, b, amt=0.4):
    acting[who].append({"from": a, "to": b, "mouth": [amt, amt], "flap": True})


def cue(at, name, **kw):
    cues.append({"at": at, "name": name, **kw})


def faceyaw(frm, to):
    return math.degrees(math.atan2(to[0] - frm[0], -(to[1] - frm[1])))


def cam(tx, ty, tz, w, az, lens, cz=None):
    """A camera looking at (tx, ty, tz) from az degrees round from the south, far enough off that the frame is w
    metres wide there."""
    d = w * 16 / 9 * lens / 24
    p = [round(tx + d * math.sin(az * D2R), 3), round(ty - d * math.cos(az * D2R), 3), cz if cz is not None else tz]
    return [[0, p, [tx, ty, tz], lens]]


def camp(pos, tgt, lens, pos2=None, tgt2=None):
    keys = [[0, list(pos), list(tgt), lens]]
    if pos2 is not None or tgt2 is not None:
        keys.append([1, list(pos2 or pos), list(tgt2 or tgt), lens])
    return keys


def ccam(car, lp, lt, lens, lp2=None, lt2=None):
    """A camera given in a car's own frame (front +y)."""
    w = lambda q: list(G.to_world(car, q[0], q[1], q[2]))
    return camp(w(lp), w(lt), lens, w(lp2) if lp2 else None, w(lt2) if lt2 else None)


def shot(sid, at, camera, **kw):
    SH.append((sid, at, camera, kw))


def car(at, name, pose_, dur=0.0):
    cue(at, f"car_{name}", x=pose_[0], y=pose_[1], yaw=pose_[3], dur=dur)


def head_at(p, yaw, h=1.0):
    return [p[0], p[1], p[2] + 1.57 * h]


for who in cast:
    key(who, 0, [0, -500, 0], yaw=0, expr="neutral", head=[0, 0], arms=[0, 0], side=[0, 0], hidden=True)
for nm, v in (("door_p", 0.0), ("door_d", 0.0), ("wheel", None), ("heater", 0.0), ("pseat", 0.0), ("lock", 0.0),
              ("crumbs", 0.0), ("blush", 0.0)):
    if v is None:
        cue(0, nm, a=0.0)
    else:
        cue(0, nm, v=v)
cue(0, "clock", s="5:40")
cue(0, "muffin", v=0.0, where="dash", drop=0.0)
cue(0, "plate", v=0.0)
cue(0, "mug", who="")
cue(0, "ride", who="")
car(0, "dad", G.CAR_HOME)
car(0, "mom", G.MOM_HOME)

HOME, WALL, DINER = G.CAR_HOME, G.CAR_WALL, G.CAR_DINER

# ===== 01 the rule (L01, L02)
ME_W = (G.CAR_HOME[0] + 1.95, G.CAR_HOME[1] - 0.1, 0.0)        # me outside Dad's driver window, facing west
stand(0, "me", ME_W, -90, "uneasy")
mouth("me", 0, "L01>", 0.35)
MEH = head_at(ME_W, -90)
# S01a: from the passenger seat, the empty driver's seat and its wheel in front, my face at the window beyond
S01_CAM = ccam(HOME, (0.85, 0.62, 1.42), (-1.25, 0.42, 1.24), 20, lp2=(0.62, 0.6, 1.42))
shot("S01a", 0, S01_CAM)
cue(0.25, "wheel", a=-9.0, dur=1.0)       # the wheel stirs by itself
cue(1.3, "wheel", a=5.0, dur=0.9)
cue("L01.3-0.1", "wheel", a=0.0, dur=0.3)
shot("S01b", "L01.3", camp([HOME[0] - 0.9, ME_W[1] - 0.35, 1.6], [MEH[0], MEH[1], MEH[2] - 0.05], 30,
                           pos2=[HOME[0] - 0.6, ME_W[1] - 0.35, 1.6]))
key("me", "L01.3", ME_W, yaw=-90, expr="stunned", head=[0, -4], blend=0.2)
# S02a: Dad on the porch, his mug on a flat palm, watching his car
show("L02", "dad")
DY = faceyaw(G.DAD_PORCH, G.CAR_HOME)
stand("L02", "dad", G.DAD_PORCH, DY, "neutral", arms=[0, 80])
cue("L02", "mug", who="dad")
DH = head_at(G.DAD_PORCH, DY)
shot("S02a", "L02", cam(DH[0], DH[1], DH[2] - 0.12, 1.5, DY + 20, 24))
# S02b: the car pulls out, nobody in it
show("L02.2")
cue("L02.2", "mug", who="")
car("L02.2", "dad", (5.0, -2.5, 0, 180), dur=1.6)
shot("S02b", "L02.2", camp([-2.6, -1.4, 1.6], [5.0, 1.0, 1.1], 30, pos2=[-2.2, -1.9, 1.55], tgt2=[5.0, -1.2, 1.1]))

# ===== 02 the rule at work (L03, L04): the noon beach
cue("L03", "clock", s="12:00")
show("L03")
shot("S03a", "L03", camp([G.BX - 5.2, -1.6, 2.9], [G.BX, 7.0, 1.55], 30, pos2=[G.BX - 4.6, -1.0, 2.85]))
show("L03.1", "fenn")
stand("L03.1", "fenn", G.FENN, 0, "sheepish", arms=[0, 0], side=[8, 8])
FH = head_at(G.FENN, 0)
shot("S03b", "L03.1", cam(FH[0], FH[1], FH[2] - 0.15, 1.3, -6, 34))
key("fenn", "L03.2", G.FENN, yaw=0, expr="sheepish", head=[-12, 4], arms=[0, 0], side=[8, 8], blend=0.35)
show("L04")
car(0, "boss", (G.BOSS_CAR[0], -8.5, 0, 0))
car("L04", "boss", G.BOSS_CAR, dur=0.7)     # it noses in right behind Fenn's, inside the shot
shot("S04a", "L04", camp([G.BX + 6.2, -7.4, 2.5], [G.BX, 1.8, 0.8], 24, pos2=[G.BX + 5.8, -6.8, 2.45]))
show("L04.1+0.2", "fenn", "boss")
stand("L04.1+0.2", "fenn", G.FENN, 4, "sheepish", side=[8, 8])
stand("L04.1+0.2", "boss", G.BOSS, -4, "sheepish", head=[-10, 0])
MID = ((G.FENN[0] + G.BOSS[0]) / 2, G.FENN[1], 1.5)
shot("S04b", "L04.1+0.2", cam(MID[0], MID[1], 1.45, 2.3, 0, 34))

# ===== 03 Mom's question (L05 to L07)
cue("L05", "clock", s="5:40")
MOMK = (G.MOM_K[0], G.MOM_K[1], 60)
DADK = (G.DAD_K[0], G.DAD_K[1], -60)
show("L05", "mom", "dad")
pm, _ = sit("L05", "mom", None, MOMK, "sly", head=[8, 0], arms=[40, 40])
pd, _ = sit("L05", "dad", None, DADK, "neutral", head=[-8, 0], arms=[40, 40])
show("L05", "mom")         # a close single of Mom: Dad is out of it till his answer
cue("L05", "plate", v=0.0)
MKH = [pm[0], pm[1], pm[2] + 1.57]
DKH = [pd[0], pd[1], pd[2] + 1.57]
shot("S05", "L05", cam(MKH[0] + 0.1, MKH[1], MKH[2] - 0.18, 1.3, 52, 24))
key("mom", "L05.1", list(pm), yaw=60, expr="sly", head=[14, 3], arms=[40, 40], blend=0.4)
show("L06", "mom", "dad")
key("dad", "L06", list(pd), yaw=-60, expr="smile", head=[-10, 0], arms=[40, 40], blend=0.3)
mouth("dad", "L06.1", "L06>", 0.45)
shot("S06", "L06", cam(DKH[0] - 0.1, DKH[1], DKH[2] - 0.18, 1.35, -45, 24))
# S07a: through the kitchen window, the car pulls out alone
show("L07")
car("L07-0.05", "dad", G.CAR_HOME)
car("L07", "dad", (5.0, -3.5, 0, 180), dur=2.0)
kp, kyaw = G.kwin_place()
shot("S07a", "L07", camp(list(G.KWIN_CAM), list(G.KWIN_TGT), 20, pos2=[G.KWIN_CAM[0] + 0.05, G.KWIN_CAM[1] - 0.12, G.KWIN_CAM[2]],
                         tgt2=[G.KWIN_TGT[0], G.KWIN_TGT[1] - 1.6, G.KWIN_TGT[2]]))
show("L07.2", "mom")
key("mom", "L07.2", list(pm), yaw=60, expr="worried", head=[20, 6], arms=[40, 40], blend=0.3)
shot("S07b", "L07.2", cam(MKH[0] + 0.1, MKH[1], MKH[2] - 0.06, 0.92, 52, 24))

# ===== 04 the clues (L08 to L11)
cue("L08", "clock", s="6:30")
show("L08")
car("L08", "dad", (5.0, -6.5, 0, 180))
car("L08+0.02", "dad", G.CAR_HOME, dur=1.4)
cue("L08", "pseat", v=1.0)
cue("L08", "heater", v=1.0)
cue("L08", "muffin", v=1.0, where="dash", drop=0.0)
shot("S08a", "L08", camp([-1.8, -5.2, 2.0], [5.0, -4.0, 1.0], 28, pos2=[-1.5, -4.8, 1.95], tgt2=[5.0, 1.8, 1.0]))
shot("S08b", "L08.2", ccam(HOME, (0.08, 0.28, 1.3), (-0.45, 0.93, 1.04), 13, lp2=(0.05, 0.36, 1.28)))
show("L08.4", "dad", "mom")
key("dad", "L08.4", list(pd), yaw=-60, expr="sheepish", head=[-2, 4], arms=[40, 40], side=[22, 22], blend=0.25)
key("dad", "L08.4+0.45", list(pd), yaw=-60, expr="sheepish", head=[2, 0], arms=[40, 40], side=[6, 6], blend=0.4)
shot("S08c", "L08.4", cam(DKH[0] - 0.08, DKH[1], DKH[2] - 0.17, 1.12, -45, 24))
# S09: the passenger seat pushed all the way back, my face at the open door
show("L09")
cue("L09", "door_p", v=1.0)
shot("S09", "L09", ccam(HOME, (2.05, -0.3, 1.3), (0.55, 0.42, 0.62), 18, lp2=(1.95, -0.2, 1.28)))
# S10: the muffin on the dash
show("L10")
cue("L10", "door_p", v=0.0)
shot("S10a", "L10", ccam(HOME, (-0.02, -0.35, 1.5), (0.3, 1.1, 1.25), 30, lp2=(0.0, -0.05, 1.45)))
shot("S10b", "L10.2", ccam(HOME, (0.2, 0.45, 1.42), (0.32, 1.13, 1.32), 34, lp2=(0.22, 0.55, 1.4)))
# S11: Dad eats it; Mom thinks he buys it
show("L11", "dad", "mom")
show("L11.3", "mom")      # S11b: Mom past Dad's plate; Dad is out of the frame
cue("L11", "muffin", v=1.0, where="plate", drop=0.0)
cue("L11", "plate", v=1.0)
cue("L11", "crumbs", v=1.0)
key("dad", "L11", list(pd), yaw=-60, expr="sheepish", head=[-14, 6], arms=[40, 40], blend=0.0)
shot("S11a", "L11", cam(DKH[0] - 0.2, DKH[1] - 0.05, DKH[2] - 0.2, 1.45, -45, 24))
key("dad", "L11.1+0.1", list(pd), yaw=-60, expr="smile", head=[-20, 2], arms=[40, 40], blend=0.4)
key("mom", "L11.3", list(pm), yaw=60, expr="sly", head=[16, 0], arms=[40, 40], blend=0.3)
# S11b: from Dad's side of the table, his muffin plate in front, Mom across it
shot("S11b", "L11.3", camp([1.5, 298.85, 1.45], [MKH[0] + 0.05, MKH[1], 1.3], 20, pos2=[1.42, 298.9, 1.44]))
cue("L12", "muffin", v=0.0, where="dash")
cue("L12", "crumbs", v=0.0)
cue("L12", "plate", v=0.0)

# ===== 05 Friday: I hide (L12, L13)
cue("L12", "clock", s="5:39")
cue("L12", "pseat", v=0.0)
cue("L12", "heater", v=0.0)
show("L12", "me")
pr, yr = sit("L12", "me", HOME, "rear_l", "sly", sink=-0.05, arms=[30, 30], head=[30, 0])
key("me", "L12.2", G.seat(HOME, "rear_l", 1.0, 0.16)[0], yaw=yr, expr="sly", arms=[30, 30], lean=6, head=[24, 0], blend=0.3)
shot("S12a", "L12", ccam(HOME, (-2.3, -0.45, 1.5), (-0.45, -1.15, 1.32), 26, lp2=(-2.15, -0.5, 1.48)))
SINK = 0.16
PME, YME = G.seat(HOME, "rear_l", 1.0, SINK)
shot("S12b", "L12.3", ccam(HOME, (-0.28, 0.85, 1.55), (-0.45, -1.15, 1.42), 26, lp2=(-0.3, 0.7, 1.52)))
mouth("me", "L12.3", "L12>", 0.3)
cue("L13", "clock", s="5:40")
show("L13", "me")
cue("L13.1", "lock", v=1.0, dur=0.18)
shot("S13a", "L13", ccam(HOME, (-2.1, -0.3, 1.32), (-1.0, -0.36, 1.22), 28, lp2=(-2.0, -0.3, 1.31)))
show("L13.2")
cue("L13.2", "wheel", a=-38.0, dur=1.3)
shot("S13b", "L13.2", ccam(HOME, (-0.05, -1.0, 1.65), (-0.72, 0.78, 1.1), 26, lp2=(-0.1, -0.85, 1.62)))

# ===== 06 the ride and the wall (L14 to L17)
cue("L14", "clock", s="5:52")
show("L14")
cue("L14", "wheel", a=0.0)
car("L14", "dad", (299.1, 34.0, 0, 180))
car("L14+0.02", "dad", (299.1, 14.0, 0, 180), dur=1.5)
shot("S14a", "L14", camp([305.0, 4.0, 1.4], [299.5, 26.0, 2.2], 38, tgt2=[299.3, 16.0, 1.6]))
car("L14.2", "dad", (299.1, 9.0, 0, 180))
car("L14.2+0.02", "dad", WALL, dur=1.3)
shot("S14b", "L14.2", camp([301.6, -8.5, 1.7], [298.6, 1.5, 1.0], 26, pos2=[301.5, -8.0, 1.7], tgt2=[298.6, 0.2, 1.0]))
# S15a: the cook by the wall, face to camera
show("L15", "cook")
CW = G.COOK_WALL
stand("L15", "cook", CW, 35, "smile", arms=[0, 0])
CH = head_at(CW, 35, 1.12)
shot("S15a", "L15", cam(CH[0], CH[1], CH[2] - 0.25, 1.5, 32, 30))
key("cook", "L15.1", CW, yaw=35, expr="smile", head=[6, -4], blend=0.4)
# S15b: me low behind the driver's seat, looking out the side window
show("L15.2", "me")
sit("L15.2", "me", WALL, "rear_l", "scared", sink=SINK, head=[-38, 0], lean=6, arms=[30, 30])
PMW, _ = G.seat(WALL, "rear_l", 1.0, SINK)
shot("S15b", "L15.2", ccam(WALL, (0.35, 0.7, 1.55), (-0.45, -1.15, 1.36), 26, lp2=(0.3, 0.55, 1.5)))
mouth("me", "L15.2", "L15>", 0.3)
# S16a: the cook drops into the passenger seat, face to camera (from the dash)
show("L16", "cook", "me")
cue("L16", "door_p", v=1.0)
PCK, YCK = G.seat(WALL, "pass", 1.12)
sit("L16", "cook", WALL, "pass", "smile", arms=[30, 30], lean=6, head=[25, 0])
key("cook", "L16+0.3", list(PCK), yaw=YCK, expr="smile", arms=[30, 30], lean=0, head=[25, 0], blend=0.3)
sit("L16", "me", WALL, "rear_l", "scared", sink=SINK + 0.1, lean=8, arms=[30, 30])
shot("S16a", "L16", ccam(WALL, (-0.6, 1.0, 1.6), (0.72, 0.1, 1.5), 20, lp2=(-0.55, 0.92, 1.58)))
# S16b: the seat slides all the way back on its rails (the tally strokes on the inner rail)
cue("L16.3", "pseat", v=1.0, dur=0.8)
PCB, _ = G.seat(WALL, "pass_back", 1.12)
key("cook", "L16.3", list(PCK), yaw=YCK, expr="smile", arms=[30, 30], keep_yaw=True)
key("cook", "L16.3+0.8", list(PCB), yaw=YCK, expr="smile", arms=[30, 30])
# a low close from the open door: the seat slides back along the outer rail and uncovers the two tally strokes;
# only the cook's knee crosses the top of the frame, never his head
shot("S16b", "L16.3", ccam(WALL, (1.4, 0.6, 0.55), (0.9, 0.05, 0.47), 14, lp2=(1.39, 0.56, 0.55)))
cue("L16>+0.1", "door_p", v=0.0, dur=0.35)
# S17a: "Morning, SIR," to the empty driver's seat
show("L17", "cook", "me")
key("cook", "L17", list(PCB), yaw=YCK, expr="smile", arms=[30, 30], head=[0, 0], blend=0.0)
key("cook", "L17.1", list(PCB), yaw=YCK, expr="smile", arms=[30, 30], head=[42, 0], blend=0.4)
mouth("cook", "L17.1", "L17.1>", 0.45)
shot("S17a", "L17", ccam(WALL, (-0.05, 0.95, 1.65), (0.72, -0.2, 1.68), 24, lp2=(0.0, 0.85, 1.63)))
# S17b: me behind the empty seat, stunned
key("me", "L17.2", list(G.seat(WALL, "rear_l", 1.0, SINK)[0]), yaw=YME, expr="stunned", head=[8, 0], lean=6, arms=[30, 30], blend=0.25)
shot("S17b", "L17.2", ccam(WALL, (-0.05, 0.75, 1.55), (-0.45, -1.15, 1.38), 26, lp2=(-0.08, 0.62, 1.52)))
# S17c: the drop: the empty driver's seat, sunrise across it, the wheel turning slowly by itself
cue("P01", "wheel", a=24.0, dur=0.9)
shot("S17c", "P01", ccam(WALL, (0.2, -0.95, 1.7), (-0.72, 0.7, 1.15), 26, lp2=(0.15, -0.8, 1.65)))

# ===== 07 the diner (L18, L19)
cue("L18", "clock", s="6:00")
show("L18")
car("L18", "dad", (G.CAR_DINER[0] + 9.0, G.CAR_DINER[1], 0, 90))
car("L18+0.02", "dad", G.CAR_DINER, dur=0.95)   # parked before S18b, whose camera rides the car
cue("L18", "wheel", a=0.0)
shot("S18a", "L18", camp([G.DX - 6.0, G.DY - 11.0, 2.0], [G.DX - 0.5, G.DY + 2.0, 1.6], 26,
                         pos2=[G.DX - 5.6, G.DY - 10.5, 1.95]))
cue("L18.2", "muffin", v=1.0, where="dash", drop=1.0)
cue("L18.2+0.02", "muffin", v=1.0, where="dash", drop=0.0, dur=0.35)
show("L18.2")
shot("S18b", "L18.2", ccam(DINER, (0.1, 0.35, 1.5), (0.32, 1.13, 1.3), 30, lp2=(0.12, 0.45, 1.47)))
# S19a: the cook at the open passenger door, leaning down, face to camera
show("L19", "cook")
cue("L19", "door_p", v=1.0)
CD = G.COOK_DINER
stand("L19", "cook", CD, 0, "warm", lean=14, head=[0, 8])
mouth("cook", "L19", "L19.1", 0.45)
shot("S19a", "L19", ccam(DINER, (-0.5, -0.1, 1.45), (2.0, -0.15, 1.6), 26, lp2=(-0.4, -0.1, 1.45)))
key("cook", "L19.2", CD, yaw=0, expr="smile", lean=12, head=[0, 6], arms=[0, 0], side=[0, 70], blend=0.3)
mouth("cook", "L19.2", "L19>", 0.45)
shot("S19b", "L19.2", ccam(DINER, (-0.1, -0.12, 1.5), (2.0, -0.15, 1.6), 30, lp2=(0.0, -0.12, 1.5)))

# ===== 08 Monday (L20 to L22)
cue("L20", "door_p", v=0.0)
cue("L20", "muffin", v=0.0)
show("L20", "me", "dad")
pme_k, _ = sit("L20", "me", None, (MOMK[0], MOMK[1], 40), "sly", head=[22, 0], arms=[40, 40])
sit("L20", "dad", None, (DADK[0], DADK[1], -40), "sheepish", head=[-22, 0], arms=[40, 40])
mouth("me", "L20", "L20.1", 0.35)
shot("S20a", "L20", cam(G.TABLE[0], G.TABLE[1] + 0.1, 1.35, 2.6, 0, 22))
cue("L20.1", "clock", s="5:40")
show("L20.1", "me")
ME_P = (-2.6, 8.4, G.PZ)
stand("L20.1", "me", ME_P, faceyaw(ME_P, (5, 3)) - 15, "sly", arms=[0, 0])
MPH = head_at(ME_P, 0)
shot("S20b", "L20.1", cam(MPH[0], MPH[1], MPH[2] - 0.15, 1.35, faceyaw(ME_P, (5, 3)) - 10, 32))
mouth("me", "L20.1", "L20.3", 0.3)
car("L20.3", "dad", HOME)
show("L20.3", "dad")
PDH, YDH = sit("L20.3", "dad", HOME, "driver", "neutral", arms=[22, 22], head=[18, 0])
# S20c: through Dad's own side window (S01a's empty seat, filled), his face turned to it
shot("S20c", "L20.3", ccam(HOME, (-2.05, 1.6, 1.62), (-0.72, 0.18, 1.5), 22, lp2=(-1.9, 1.45, 1.6)))
key("dad", "L20.4", list(PDH), yaw=YDH, expr="neutral", arms=[22, 22], head=[28, 4], blend=0.4)
# S21a: the stone wall, Monday; the cook steps to the car
cue("L21", "clock", s="5:52")
car("L21", "dad", WALL)
cue("L21", "pseat", v=1.0)
show("L21", "dad", "cook")
PDW, YDW = sit("L21", "dad", WALL, "driver", "neutral", arms=[22, 22])
stand("L21", "cook", (CW[0] - 0.2, CW[1] - 2.6, 0.0), 174, "smile")
key("cook", "L21.1", (CW[0], CW[1] - 0.6, 0.0), yaw=174, expr="smile")
key("cook", "L21.1+0.4", yaw=70, expr="smile", blend=0.35)
shot("S21a", "L21", camp([304.0, -7.8, 1.7], [297.8, 0.0, 1.3], 28, pos2=[303.7, -7.3, 1.7]))
# S21b: through the windshield from the hood: Dad and the cook side by side, the cook turning to Dad
show("L21.2", "dad", "cook")
PCI, YCI = sit("L21.2", "cook", WALL, "pass_back", "smile", arms=[30, 30], inward=0.22)
PDI, _ = sit("L21.2", "dad", WALL, "driver", "neutral", arms=[22, 22], inward=0.22)
key("cook", "L21.3", list(PCI), yaw=YCI, expr="stunned", arms=[30, 30], head=[34, 0], blend=0.35)
key("dad", "L21.3", list(PDI), yaw=YDW, expr="neutral", arms=[22, 22], head=[-6, 0], blend=0.4)
shot("S21b", "L21.2", ccam(WALL, (-0.03, 2.45, 1.7), (-0.03, -0.05, 1.6), 21, lp2=(-0.03, 2.35, 1.69)))
PCW, YCW = G.seat(WALL, "pass_back", 1.12)
# S22: "Oh. You're REAL."
show("L22", "dad", "cook")
sit("L22", "cook", WALL, "pass_back", "laugh", arms=[30, 30], head=[34, 0])
sit("L22", "dad", WALL, "driver", "neutral", arms=[22, 22], head=[-6, 0])
mouth("cook", "L22.1", "L22>", 0.5)
shot("S22", "L22", ccam(WALL, (0.05, 1.05, 1.68), (0.72, -0.2, 1.7), 24, lp2=(0.1, 0.95, 1.66)))

# ===== 09 the twist (L23) and the reveal (L24)
show("L23", "dad", "cook")
cue("L23", "blush", v=1.0, dur=0.5)
key("dad", "L23", list(PDW), yaw=YDW, expr="sheepish", arms=[22, 22], head=[-18, 6], blend=0.0)
shot("S23a", "L23", ccam(WALL, (-0.05, 1.0, 1.62), (-0.72, 0.15, 1.6), 24, lp2=(-0.1, 0.92, 1.6)))
# the remember-cut: last spring, rain; the cook walks on the verge, Dad's car passes him
cue("L23.1", "blush", v=0.0)
cue("L23.1", "pseat", v=0.0)
cue("L23.1", "ride", who="dad")
show("L23.1", "dad", "cook")
RAINCAR0 = (9.0, G.RAIN_ROAD_Y - 1.2, 0.0, 90.0)
RAINCAR1 = (1.3, G.RAIN_ROAD_Y - 1.2, 0.0, 90.0)
RAINCAR2 = (-0.5, G.RAIN_ROAD_Y - 1.2, 0.0, 90.0)
CRY = G.RAIN_ROAD_Y - 3.45          # the cook walks the road's south edge, west, the same way the car goes
car("L23.1+0.01", "dad", RAINCAR0)
car("L23.1+0.02", "dad", RAINCAR1, dur=1.5)
p1, yr0 = G.seat(RAINCAR1, "driver")
# Dad looks ahead and a little toward the verge, at the camera: he sees him, and drives on
sit("L23.1", "dad", RAINCAR1, "driver", "neutral", head=[50, 0], arms=[0, 0])
# S23b: on the verge ahead of the cook: the cook trudges toward the lens, hunched, the car comes up behind him
stand("L23.1", "cook", (1.0, CRY, 0.0), -72, "uneasy", head=[20, 10], lean=10, arms=[0, 0], side=[6, 6])
key("cook", "L23.4", (0.6, CRY, 0.0), yaw=-72, expr="uneasy", head=[20, 10], lean=10, arms=[0, 0], side=[6, 6])
shot("S23b", "L23.1", camp([-2.4, G.RAIN_ROAD_Y - 5.4, 1.7], [0.92, G.RAIN_ROAD_Y - 2.66, 1.62], 33,
                           pos2=[-2.2, G.RAIN_ROAD_Y - 5.25, 1.69], tgt2=[0.92, G.RAIN_ROAD_Y - 2.6, 1.62]))
# S23c: behind the cook as the car pulls away; Dad twists round in his seat to look back at him
car("L23.4", "dad", RAINCAR2, dur=1.3)
cut("dad", "L23.4", list(p1), yaw=-25, expr="sheepish", head=[70, 4], arms=[0, 0])
key("dad", "L23.4+0.6", list(p1), yaw=-25, expr="sheepish", head=[76, 6], arms=[0, 0], blend=0.4, keep_yaw=True)
# (set.py's ride moves Dad with the car; these keys only tell the lints where he really is)
key("dad", "L23.4+1.3", list(G.seat(RAINCAR2, "driver")[0]), yaw=-25, expr="sheepish", head=[76, 6], arms=[0, 0])
key("cook", "L23.4+0.02", (0.6, CRY, 0.0), yaw=-90, expr="uneasy", head=[-30, 4], lean=8, arms=[0, 0], side=[6, 6], blend=0.3)
key("cook", "L23>", (0.0, CRY, 0.0), yaw=-90, expr="uneasy", head=[-30, 4], lean=8, arms=[0, 0], side=[6, 6])
shot("S23c", "L23.4", camp([3.8, G.RAIN_ROAD_Y - 3.6, 1.9], [1.05, G.RAIN_ROAD_Y - 1.86, 1.55], 30,
                           tgt2=[-0.48, G.RAIN_ROAD_Y - 2.21, 1.55]))
# S24a: Friday from the dash: the empty driver's seat, the muffin, the cook talking to it
cue("L24", "ride", who="")
car("L24", "dad", WALL)
cue("L24", "pseat", v=1.0)
cue("L24", "muffin", v=1.0, where="dash", drop=0.0, lx=0.25, ly=1.0, lz=G.MUFFIN_L[2])
show("L24", "cook")
PC24, YC24 = sit("L24", "cook", WALL, "pass_back", "smile", arms=[30, 30], head=[38, 0])
mouth("cook", "L24", "L24.1>", 0.35)
cue("L24", "wheel", a=0.0)
cue("L24+0.05", "wheel", a=-16.0, dur=1.3)
# from the dash, low: the empty driver's seat in gold on the right, the cook on the left, the muffin in front of him
shot("S24a", "L24", ccam(WALL, (0.5, 2.4, 1.78), (0.1, -0.2, 1.42), 17, lp2=(0.48, 2.3, 1.77)))
# S24b: Monday: the muffin on Dad's dash at chest height, Dad and the cook side by side behind it, laughing
show("L24.2", "dad", "cook")
cue("L24.2", "muffin", v=1.0, where="dash", drop=0.0, lx=G.MUFFIN_L[0], ly=G.MUFFIN_L[1], lz=G.MUFFIN_L[2])
sit("L24.2", "dad", WALL, "driver", "laugh", arms=[22, 22], head=[-10, 0], inward=0.22)
sit("L24.2", "cook", WALL, "pass_back", "laugh", arms=[30, 30], head=[16, 0], inward=0.22)
shot("S24b", "L24.2", ccam(WALL, (-0.02, 2.55, 1.74), (-0.02, -0.05, 1.6), 20, lp2=(-0.02, 2.45, 1.73)))

# ===== 10 the button and the loop (L25, L26)
cue("L25", "clock", s="5:40")
cue("L25", "muffin", v=0.0)
cue("L25", "pseat", v=0.0)
car("L25", "dad", G.CAR_OUT)
show("L25", "mom")
MOMP = (-0.6, 8.6, G.PZ)
MY = faceyaw(MOMP, G.MOM_HOME)
stand("L25", "mom", MOMP, MY, "sly", arms=[0, 80])
cue("L25", "mug", who="mom")
MPH2 = head_at(MOMP, MY, 0.97)
shot("S25a", "L25", cam(MPH2[0], MPH2[1], MPH2[2] - 0.12, 1.45, MY + 20, 24))
show("L25.2")
cue("L25.2", "mug", who="")
car("L25.2", "mom", (G.MOM_HOME[0], -2.5, 0, 180), dur=1.5)
shot("S25b", "L25.2", camp([1.0, -3.6, 1.7], [G.MOM_HOME[0], 1.0, 1.1], 28, pos2=[1.3, -3.9, 1.65], tgt2=[G.MOM_HOME[0], -0.8, 1.1]))
# S26: my face by Dad's car window (S01a's framing), laughing; it loops into L01
car("L26", "dad", HOME)
car("L26", "mom", (G.MOM_HOME[0], -20.0, 0, 180))
show("L26", "me")
stand("L26", "me", ME_W, -90, "laugh")
mouth("me", "L26", "L26>", 0.4)
shot("S26", "L26", ccam(HOME, (0.85, 0.62, 1.42), (-1.25, 0.42, 1.24), 20, lp2=(0.55, 0.6, 1.42)))

# ----------------------------------------------------------------------------------------------- finish
remap_all(cues)
for k_ in acting.values():
    remap_all(k_)
shots = []
for i, (sid, at, camera, kw) in enumerate(SH):
    if len(camera) == 1:       # a slow dolly in on every shot whose camera was still: motion the preview can read
        _, p0_, t0_, ln = camera[0]
        camera = camera + [[1, [round(p0_[j] + 0.12 * (t0_[j] - p0_[j]), 3) for j in range(3)], list(t0_), ln]]
    s = {"id": sid, "cam": camera, "step": 2}
    if i:
        s["at"] = remap(at)
    s.update({k: v for k, v in kw.items() if not k.startswith("_")})
    shots.append(s)

sfx = [
    {"at": "L13.1", "kind": "click", "db": -16},
    {"at": "L16>+0.15", "kind": "door", "db": -20},
    {"at": "L16.3+0.75", "kind": "thud", "db": -22},
    {"at": "L18.1", "kind": "bell", "db": -24, "hz": 330.0},
]
music = {
    "root": 49, "mode": "minor", "bpm": 84, "seed": 154,
    "sections": [
        {"at": 0, "voices": ["pad", "musicbox"], "energy": 0.45},
        {"at": "L12", "voices": ["pulse", "pad"], "energy": 0.4},
        {"at": "L18", "voices": ["drone", "pad"], "energy": 0.3},
        {"at": "L23", "voices": ["pad", "choir"], "energy": 0.5},
        {"at": "L24", "mode": "major", "voices": ["musicbox", "piano", "pad"], "energy": 0.7},
        {"at": "L26", "mode": "major", "voices": ["musicbox", "pad"], "energy": 0.45},
    ],
}
sound = {
    "floor": "grass", "steps_db": -24,
    "ambience": [{"kind": "hum", "from": "L01.3", "to": "L02.3", "lufs": -40},
                 {"kind": "wind", "from": "L14", "to": "L17>", "lufs": -44},
                 {"kind": "rain", "from": "L23.1", "to": "L23>", "lufs": -36}],
    "sfx": sfx,
    "music_drops": [{"from": "P01", "to": "P01>"}],
    "rev": REV,
}
remap_all(sfx)
remap_all(music["sections"])
remap_all(sound["ambience"])
remap_all(sound["music_drops"])
polish = {"reveal": ["L22", "L24"], "twist": "L23", "emph": ["L01.3", "L02.3", "L07.2", "L17.2", "L22.2", "L24.3"],
          "ones": "all", "bed_drop_db": 0.0, "quiet": [], "hold": ["S04b", "S20a", "S21b", "S24b"], "sway": ["S13a", "S13b", "S15b", "S16a", "S17a", "S17b", "S17c"]}
polish["emph"] = [remap(x) for x in polish["emph"]]
polish["reveal"] = [remap(x) for x in polish["reveal"]]
polish["twist"] = remap(polish["twist"])
story = {
    "slug": "ep154-dawn-car",
    "title": "Dad's Empty Car Leaves Every DAWN \U0001F697",
    "made_for_kids": False,
    "premise": ("In our town your car drives itself to wherever you'd rather be and everyone can see it, and my "
                "dad's car leaves our driveway empty at 5:40 every morning and comes back with a muffin on the dash."),
    "twist": ("Last spring Dad drove past a young cook walking to work in the rain and didn't stop, and wished he "
              "had, so every morning since his car has gone to pick the cook up for him."),
    "world": ("A mint-green bungalow at the top of a hill street at sunrise, a teal hatchback in the driveway, a long "
              "hill road through green fields to a low stone wall, and a cherry-red diner."),
    "voice": {"voice": "am_adam", "tempo": 1.03, "rate": 1.45},
    "key_color": "#8f9bff",
    "gap": 0.15,
    "tail": 0.0,
    "fade_in": False,
    "fade_out": False,
    "rev": REV,
    "look": {"style": "closer", "fog": "#ffe6d2", "fog_density": 0.0, "fog_start": 200.0, "sky": "#ffd9c4",
             "sky_strength": 0.9, "exposure": 0.0, "flash_safe": True, "polish": polish},
    "grade": {"shadows": [0.0, 0.0, 0.01], "highlights": [0.025, 0.012, -0.015], "saturation": 1.05,
              "contrast": 1.03, "vignette": 0.1, "bloom": 0.12, "grain": 0.008},
    "shot_grades": {"S23b": {"saturation": 0.8, "vignette": 0.35, "bloom": 0.3},
                    "S23c": {"saturation": 0.8, "vignette": 0.35, "bloom": 0.3}},
    "rain_shots": ["S23b", "S23c"],
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
    "framing_ok": ["S02b", "S11a", "S14a", "S25b"],
    "frames_ok": ["S16a", "S18b"],
    "staging_ok": ["S21b", "S24b"],   # a seated row in the car, shoulders close (allowed)
    "clip_ok": [],
    "phonemes": {},
    "homophones": {"fenns": "fens"},
}
OUT.write_text(json.dumps(story, indent=1, ensure_ascii=False) + "\n")
print("wrote", OUT, f"({len(shots)} shots, {len(cues)} cues)")
