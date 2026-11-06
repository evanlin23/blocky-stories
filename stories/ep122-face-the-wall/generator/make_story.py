"""Writes ../story.json and ../meta.json for ep122 "face the wall" (script.md, 2026-11-05). Run:
python stories/ep122-face-the-wall/generator/make_story.py

The words are in lines.json. Places are in ../layout.py (shared with set.py). meta.json tells set.py each shot's look
and what to hide. A character facing -y has yaw 0, +x 90, +y 180, -x -90. A lying body is root (x, 1.58, 0.69) with
lean -84 (head toward +y), its face turned by head yaw: -90 faces the west wall, +90 the room (east); Dad's bed is the
mirror (+90 faces his east wall, -90 the room). Nothing blinks: every acting key holds the eyes open.
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
REV = 14
orig = json.loads((HERE / "lines.json").read_text())
lines, CM = T.split_lines(orig)
idx = next(i for i, l in enumerate(lines) if l["id"] == "L34")
lines.insert(idx, {"id": "P01", "pause": 0.6, "chunks": [["", ""]]})


class Raw(str):
    """A time reference already in split-caption coordinates."""


def remap(ref):
    if not isinstance(ref, str) or isinstance(ref, Raw):
        return ref
    mm = re.match(r"^(L\d+)\.(\d+)(.*)$", ref)
    if mm and mm.group(1) in CM:
        return f"{mm.group(1)}.{CM[mm.group(1)][int(mm.group(2))]}{mm.group(3)}"
    return ref


def remap_all(items):
    for it in items:
        for key in ("at", "from", "to"):
            if key in it:
                it[key] = remap(it[key])


def person(skin, shirt, pants, shoes, hair="cap", hair_c="#2a1d15", pattern="solid", pattern_c=None, hat="none",
           hat_c="#333333", extras=(), eyes="round", sleeves="long", brow_w=1.0, **kw):
    d = {"age": "adult", "skin": skin, "shirt": shirt, "pattern": pattern, "pants": pants, "shoes": shoes,
         "sleeves": sleeves, "hair": hair, "hair_c": hair_c, "hat": hat, "hat_c": hat_c,
         "face": {"eyes": eyes, "brows": True, "ink": "#1c120c"}}
    if brow_w != 1.0:
        d["face"]["brow_w"] = brow_w
    if pattern_c:
        d["pattern_c"] = pattern_c
    if extras:
        d["extras"] = list(extras)
    d.update(kw)
    return d


cast = {
    "me": person("#8a5a3a", "#3fa66a", "#8d93a0", "#f2eadb", hair="spiky", hair_c="#17100c", extras=["hooddown"], brow_w=1.5),
    "dad": person("#855536", "#c8473a", "#3a4560", "#2a2a30", hair="cap", hair_c="#7c7c86", pattern="plaid",
                  pattern_c="#6e1c18", brow_w=1.7, width=1.04),
    "grandma": person("#9a6a48", "#f4ecf6", "#f4ecf6", "#7fd8b8", hair="cap", hair_c="#fbfbff", extras=["glasses"],
                      glasses_c="#e6c050", eyes="lashes", height=0.72),
    "ro": person("#e0a877", "#2f8f9a", "#3a4560", "#4a3a30", hair="long", hair_c="#5a3322", hat="beanie", hat_c="#d2343a",
                 pattern="knit", pattern_c="#256f78", eyes="lashes"),
    "ezra": person("#c98f64", "#2f8f4f", "#3a4560", "#f2eadb", hair="spiky", hair_c="#2a1a10", pattern="stripes",
                   pattern_c="#e8f5ea", sleeves="short"),
}
acting = {n: [] for n in cast}
last = {n: {"pos": [0.0, 0.0, 0.0]} for n in cast}
cues, SH, META = [], [], {}


def cue(at, name, **kw):
    cues.append({"at": at, "name": name, **kw})


def A(who, at, **kw):
    """One acting key at `at`. A moved character jumps (a zero-length key pair) unless it's `walk`."""
    k = {"at": at, **kw}
    if "pos" in kw and not kw.get("walk"):
        acting[who].append({"at": at, "pos": list(last[who]["pos"]), "blend": 0.0})
        k["blend"] = kw.get("blend", 0.0)
    k.pop("walk", None)
    acting[who].append(k)
    if "pos" in kw:
        last[who]["pos"] = list(kw["pos"])


def stand(pos, yaw=0.0, expr="neutral", z=0.0, **kw):
    return {"pos": [pos[0], pos[1], z], "yaw": yaw, "expr": expr, "lean": 0.0, "head": [0, 0], "arms": [0, 0],
            "side": [0, 0], "blink": False, "look": [0, 0], **kw}


def lying(who, head, expr="neutral", bed="me", **kw):
    """Lying on my bed (bed 'me') or Dad's. head: -90 west, +90 east."""
    x = G.BX if bed == "me" else G.DX
    h = cast[who].get("height", 1.0)
    y0 = G.HEAD_Y - 1.571 * h
    z = 0.52 + 0.17 * h + 0.0 if h < 1 else G.LY_ROOT[1]
    if h < 1:
        z = 0.80 - 0.118
    return {"pos": [x, y0, z], "yaw": 0.0, "expr": expr, "lean": -84.0, "head": [head, 0], "arms": [0, 0], "side": [0, 0],
            "blink": False, "look": [0, 0], **kw}


def sit(pos, yaw, expr="neutral", z=0.0, **kw):
    return stand(pos, yaw, expr, z, **kw)


def grandma_in_bed():
    """Grandma on her own bed (centre line GBX, head to the pillow at y 8.95), head turned to the east wall."""
    h = cast["grandma"].get("height", 1.0)
    return {"pos": [G.GBX, 8.95 - 1.571 * h, 0.70], "yaw": 0.0, "expr": "neutral", "lean": -84.0, "head": [90, 0], "arms": [0, 0],
            "side": [0, 0], "blink": False, "look": [0, 0]}


def shot(at, camera, name, look="N", cast_=None, step=2, **meta):
    SH.append({"at": at, "cam": camera, "name": name, "look": look, "cast": cast_ or {}, "step": step, "meta": meta})


def fc(head, h, az, f=0.42, lens=35, dz=0.0, up=0.12, right=0.0):
    """A camera on a head so the head is `f` of the frame's width (head centre `up` of the frame height above centre)."""
    d = 0.0311 * h * lens / f
    dz = dz + (0.5 if az == 348 else 0.0)
    H = 24.0 * d / lens
    W_ = H * 9.0 / 16.0
    ra = math.radians(az)   # slide the camera sideways so the head sits `right` of the frame's width right of centre
    tgt = (head[0] + right * W_ * math.sin(ra), head[1] - right * W_ * math.cos(ra), head[2] - up * H)
    return G.orbit(tgt, d, az, dz, lens)


def lens_to(k, lens):
    c = [list(x) for x in k]
    c[0][3] = lens
    return c


HS, HD = G.HS, G.HD
KX, EX, SX, RX = G.KX, G.EX, G.SX, G.RX
HIDE_SPW = ["w_sp_W", "fl_N"]
NIGHT = "N"

# ---------------------------------------------------------------------------------------------- 01 the rule (L01, L02)
shot(0, fc(HS, 1.0, 180, 0.46, 30, up=0.0), "S01a face", "N", {"me": lying("me", -90)}, hide=HIDE_SPW)
shot(Raw(f"L01.{CM['L01'][0] + 1}"), fc(HS, 1.0, 180, 0.62, 42, up=0.0), "S01b eyes", "N", {"me": lying("me", -90)}, hide=HIDE_SPW)
shot("L02", G.orbit((-3.2, 2.3, 0.75), 2.6, 215, 0.25, 28), "S02 edge", "N", {"me": lying("me", -90)}, hide=HIDE_SPW)
# ---------------------------------------------------------------------------------------------- 02 the rule at work (L03 to L08)
shot("L03", [[0, [RX, -5.5, 0.5], [RX, 1.5, 1.0], 22]], "S03 three beds", "B", {}, step=2)
shot("L04", G.orbit((-3.5, 2.9, 0.7), 2.8, 180, 0.5, 26), "S04 bed", "D", {}, hide=HIDE_SPW, quilt="flat")
shot("L05", fc((EX, 5.1, 1.571), 1.0, 270, 0.36, 33), "S05a Ro", "E", {"ro": stand((EX, 5.1), 0, "worried")}, duffel=True)
shot("L05.2", G.orbit((-3.7, 3.15, 0.85), 2.0, 348, 0.9, 30, tz=0.8), "S05b Ro bed", "N",
     {"ro": lying("ro", -90)}, quilt="lump")
shot("L06", G.orbit((-3.7, 2.2, 0.6), 2.7, 20, 1.0, 30), "S06 tucked", "D", {}, quilt="flat")
shot("L07", G.orbit((-2.55, 1.0, 0.05), 1.5, 60, 0.7, 30), "S07 pennant", "D", {}, quilt="flat", pennant=True)
shot("L08", fc((KX + 3.0, 3.95, 1.35), 1.0, 270, 0.4, 35), "S08 Ezra", "K",
     {"ezra": sit((KX + 3.0, 3.95), 0, "wide", z=-0.22)}, sit={"ezra": 85}, cake0=False)
# ---------------------------------------------------------------------------------------------- 03 me (L09 to L16)
shot("L09", [[0, [EX - 1.0, 0.8, 2.3], [EX, 5.6, 2.6], 24]], "S09a snow", "E", {}, flakes=True)
shot("L09.1", [[0, [G.BX + 0.25, 2.55, 1.05], [G.BX + 0.48, 3.54, 0.98], 55]], "S09b tally", "D", {}, quilt="flat", tagd=0.3)
shot("L10", fc(HS, 1.0, 348, 0.4, 35, up=0.1), "S10 face day", "D", {"me": lying("me", 90)}, quilt="lump")
shot("L11", G.orbit((EX + 3.4, 1.0, 1.0), 6.5, 235, 0.7, 28), "S11a car", "E", {}, cargo=True)
shot("L11.1", G.orbit((EX + 3.4 - 0.45, 0.7, 1.0), 2.7, 270, 0.3, 38), "S11b windshield", "E",
     {"me": sit((EX + 3.4 - 0.45, 0.7), 0, "worried", z=-0.32)}, sit={"me": 85}, cargo=True)
shot("L12", fc((-2.2, 1.0, 1.571), 1.0, 180, 0.4, 35, dz=0.0), "S12 sad boxes", "D",
     {"me": stand((-2.2, 1.0), -90, "worried")}, hide=HIDE_SPW, door_sp=80)
shot("L13", fc((KX + 1.4, 4.05, 1.131), 0.72, 270, 0.4, 35), "S13a Grandma stove", "K",
     {"grandma": stand((KX + 1.4, 4.05), 0, "smile")}, glasses=True, card=True)
shot("L13.2", fc((KX + 3.0, 3.95, 1.35), 1.0, 270, 0.4, 35), "S13b me", "K",
     {"me": sit((KX + 3.0, 3.95), 0, "sad-smile", z=-0.22)}, sit={"me": 85})
shot("L14", fc((0.7, G.DOOR_Y, 1.571), 1.0, 180, 0.36, 26, up=0.0), "S14 Dad", "D",
     {"dad": stand((0.7, G.DOOR_Y), -90, "smile")}, hide=["w_sp_E", "w_sp_W"], door_sp=85, door_dd=88)
shot("L15", fc(HS, 1.0, 348, 0.42, 35, up=0.1), "S15 boxes", "N", {"me": lying("me", 90)}, quilt="lump")
# L16: I roll over to face the wall; the tag ticks to 1
shot("L16", fc(HS, 1.0, 180, 0.44, 35, up=0.1), "S16a roll", "N", {"me": lying("me", 90, "worried")}, hide=HIDE_SPW, roll=True)
shot("L16.1", fc(HS, 1.0, 180, 0.5, 38, up=-0.05), "S16b tick", "N", {"me": lying("me", -90, "worried", blend=0.5)}, hide=HIDE_SPW)
# ---------------------------------------------------------------------------------------------- night one (L17 to L22)
CLK = (-2.95, 3.35, 0.68)
shot("L17", G.orbit(CLK, 1.0, 180, 0.0, 38), "S17a clock", "N", {}, quilt="lump")
shot("L17.1", fc(HS, 1.0, 180, 0.48, 35, up=0.1), "S17b dip", "N", {"me": lying("me", -90, "shut")}, hide=HIDE_SPW, snap=True)
shot("L18", [[0, [-3.45, 0.55, 0.62], [-3.5, 2.2, 0.72], 26]], "S18 foot", "N", {"me": lying("me", -90)}, quilt="foot", rim=0)
shot("L19", fc(HS, 1.0, 180, 0.44, 35, up=0.1), "S19 scared", "N", {"me": lying("me", -90, "scared")}, hide=HIDE_SPW)
shot("L20", fc(HS, 1.0, 180, 0.6, 40, up=0.02), "S20 wide", "N", {"me": lying("me", -90, "wide")}, hide=HIDE_SPW)
shot("L21", [[0, [-5.7, 2.7, 1.0], [-2.2, 3.8, 0.6], 22]], "S21 dawn", "N", {"me": lying("me", -90, "wide")}, hide=HIDE_SPW, dawn=True)
shot("L22", [[0, [-2.4, 0.8, 1.35], [-3.7, 2.35, 0.85], 30]], "S22 tucked me", "D", {"me": lying("me", 90)}, quilt="lump")
shot("L23", fc((KX + 3.0, 4.25, 1.131), 0.72, 270, 0.36, 35), "S23 pancake", "K",
     {"grandma": stand((KX + 3.0, 4.25), 0, "smile")}, glasses=True, card=True, cake0=True)
shot("L24", fc((KX + 3.0, 3.95, 1.35), 1.0, 270, 0.4, 35), "S24 me pancake", "K",
     {"me": sit((KX + 3.0, 3.95), 0, "wide", z=-0.22)}, sit={"me": 85}, cake0=True)
shot("L25", [[0, [G.SX + 1.15, -0.1, 0.62], [G.SX, 0.42, 0.62], 30]], "S25a slippers", "SD",
     {"grandma": stand((G.SX, 0.42), 180, "neutral", z=0.38)}, card=True, glasses=True, hide=["s_E"], noskirt=True)
shot("L25.1", fc((G.SX, 1.0, G.STEP_RISE * 4 + 1.131), 0.72, 270, 0.4, 35, up=0.05), "S25b Grandma stair", "SD",
     {"grandma": stand((G.SX, 1.0), 0, "worried", z=G.STEP_RISE * 4)}, card=True, glasses=True)
# ---------------------------------------------------------------------------------------------- night two (L26 to L30)
shot("L26", fc(HS, 1.0, 180, 0.44, 35, up=0.1), "S26 roll", "N", {"me": lying("me", 90, "worried")}, hide=HIDE_SPW, roll=True)
shot("L26.1", fc(HS, 1.0, 180, 0.5, 38, up=-0.05), "S26b tick", "N", {"me": lying("me", -90, "worried", blend=0.5)}, hide=HIDE_SPW)
shot("L27", G.orbit(CLK, 1.0, 180, 0.0, 38), "S27a clock", "N", {}, quilt="lump")
shot("L27.1", [[0, [-3.45, 0.55, 0.62], [-3.5, 2.3, 0.72], 26]], "S27b knees", "N", {"me": lying("me", -90)}, quilt="knee")
shot("L28", fc((HS[0], 3.0, 0.8), 1.0, 180, 0.42, 35, up=0.12), "S28 shoulder", "N", {"me": lying("me", -90, "scared")}, hide=HIDE_SPW, quilt="shoulder")
shot("L29", [[0, [-1.8, 2.0, 1.55], [-3.6, 2.7, 1.0], 36]], "S29 dent", "N", {"me": lying("me", -90)}, quilt="shoulder", fill=0.2, gmul=0.45, wmul=0.5)
shot("L30", [[0, [-5.7, 2.7, 1.0], [-2.2, 3.8, 0.6], 22]], "S30 dawn", "N", {"me": lying("me", -90, "wide")}, hide=HIDE_SPW, dawn=True)
# ---------------------------------------------------------------------------------------------- night three (L31 to L38)
shot("L31", fc(HS, 1.0, 180, 0.44, 35, up=0.1), "S31 pillow", "N", {"me": lying("me", -90, "worried")}, hide=HIDE_SPW, pillow="dent")
shot("L32", fc(HS, 1.0, 180, 0.6, 40, up=0.02), "S32 breathing", "N", {"me": lying("me", -90, "scared")}, hide=HIDE_SPW, pillow="dent")
shot("L33", fc(HS, 1.0, 180, 0.44, 35, up=0.1), "S33 turn", "N", {"me": lying("me", -90, "scared")}, hide=HIDE_SPW, pillow="dent", turn=True)
shot("P01", [[0, [-2.0, 1.1, 1.0], [-3.2, 3.0, 0.7], 28]], "drop", "N", {"me": lying("me", 90, blend=0.8)}, quilt="lump", pillow="dent")
GRAN = (-3.35, 3.1)
SCARE_RIM, SCARE_FILL, SCARE_G = 1500, 1.8, 0.1
shot("L34", G.orbit((GRAN[0], GRAN[1], 1.28), 1.6, 180, 0.0, 32, tz=1.02), "S34 face", "N",
     {"grandma": stand(GRAN, -90, "blank", z=0.06, lean=8)}, hide=HIDE_SPW, rim=SCARE_RIM, fill=SCARE_FILL, gmul=SCARE_G, wmul=0.25, sit={"grandma": 90})
shot("L35", G.orbit((GRAN[0], GRAN[1], 1.3), 1.5, 180, 0.0, 36, tz=1.05), "S35 closer", "N",
     {"grandma": stand(GRAN, -90, "blank", z=0.06, lean=8)}, hide=HIDE_SPW, rim=SCARE_RIM, fill=SCARE_FILL, gmul=SCARE_G, wmul=0.25, sit={"grandma": 90})
shot("L36", fc(HS, 1.0, 348, 0.44, 35, up=0.1), "S36 squeeze", "N", {"me": lying("me", 90, "squeeze")}, quilt="lump")
shot("L37", [[0, [-2.2, 1.5, 1.75], [-3.5, 2.5, 1.1], 34]], "S37 pat", "N",
     {"me": lying("me", 90, "squeeze")}, quilt="lump", hand=True)
shot("L38", [[0, [-2.4, 2.2, 0.2], [-1.1, 2.62, -0.1], 30]], "S38 stripe", "N",
     {}, quilt="lump", door_sp=14, shadow=True, hide=[], fill=0.5)
shot("L39", [[0, [-0.2, 2.2, 0.8], [-0.21, 3.4, 0.05], 36], [1.0, [-0.2, 2.75, 0.6], [-0.21, 3.4, 0.05], 36]], "S39 slippers", "D", {}, slippers=True, door_sp=85, hide=[])
shot("L40", fc((KX + 3.0, 3.95, 1.35), 1.0, 270, 0.4, 35), "S40 me pancake", "K",
     {"me": sit((KX + 3.0, 3.95), 0, "worried", z=-0.22)}, sit={"me": 85}, cake0=True)
# ---------------------------------------------------------------------------------------------- night four (L41 to L50)
shot("L41", fc(HS, 1.0, 348, 0.42, 35, up=0.1), "S41 awake", "N", {"me": lying("me", 90, "worried")}, quilt="lump")
shot("L42", [[0, [-3.3, 3.0, 1.05], [0.7, 2.6, 0.95], 24]], "S42 across", "NDAD", {}, quilt="lump", door_sp=60, hide=[])
shot("L43", [[0, [1.4, 1.9, 1.5], [3.7, 3.0, 0.85], 28]], "S43 Dad back", "NDAD", {"dad": lying("dad", 90, bed="dad")}, door_dd=85)
GD = (2.9, 2.3)
shot("L44", [[0, [1.0, 2.5, 1.5], [3.3, 2.55, 0.95], 24]], "S44 buttons", "NDAD",
     {"dad": lying("dad", 90, bed="dad"), "grandma": stand(GD, -90, "neutral", z=0.04)}, card=True, sit={"grandma": 80}, door_dd=90, lampg=90, hide=["w_dd_W", "w_dd_N"])
shot("L45", [[0, [1.2, 2.3, 1.3], [3.2, 2.5, 1.05], 28]], "S45 reveal", "NDAD",
     {"dad": lying("dad", 90, bed="dad"), "grandma": stand(GD, -90, "warm", z=0.04)}, card=True, sit={"grandma": 80}, door_dd=90, lampg=90, hide=["w_dd_W", "w_dd_N"])
shot("L46", fc((GD[0], GD[1], 1.15), 0.72, 180, 0.5, 35, up=0.1, right=0.08), "S46 face", "NDAD",
     {"dad": lying("dad", 90, bed="dad"), "grandma": stand(GD, -90, "warm", z=0.04)}, card=True, sit={"grandma": 80}, door_dd=90)
shot("L47", fc((-1.1, G.DOOR_Y, 1.571), 1.0, 0, 0.44, 28), "S47 me doorway", "NDAD",
     {"me": stand((-1.1, G.DOOR_Y), 90, "wide")}, hide=["w_sp_E"], door_sp=85, door_dd=88)
shot("L48-0.16", fc((EX, 5.1, 1.571), 1.0, 270, 0.42, 33), "S48a Ro", "E", {"ro": stand((EX, 5.1), 0, "worried")})
shot("L48.1-0.08", fc((KX + 3.0, 3.95, 1.35), 1.0, 270, 0.42, 35), "S48b Ezra", "K",
     {"ezra": sit((KX + 3.0, 3.95), 0, "worried", z=-0.22)}, sit={"ezra": 85})
shot("L48.2+0.18", fc((-1.1, G.DOOR_Y, 1.571), 1.0, 0, 0.44, 28), "S48c me", "NDAD",
     {"me": stand((-1.1, G.DOOR_Y), 90, "worried")}, hide=["w_sp_E"], door_sp=85, door_dd=88)
shot("L49+0.12", fc((GD[0], GD[1], 1.1), 0.72, 180, 0.42, 35, up=0.14), "S49 hand", "NDAD",
     {"dad": lying("dad", 90, bed="dad"), "grandma": stand(GD, -90, "warm", z=0.04, arms=[0, 62])}, card=True, sit={"grandma": 80}, door_dd=90)
shot("L50", fc((GD[0], GD[1], 1.15), 0.72, 190, 0.4, 35, up=0.1), "S50 sits", "NDAD",
     {"dad": lying("dad", 90, bed="dad"), "grandma": stand(GD, -90, "warm", z=0.04, look=[0.8, 0.0])}, card=True, sit={"grandma": 80}, door_dd=90)
shot("L51", G.orbit((EX + 3.4, 1.0, 0.9), 6.0, 215, 0.8, 28), "S51 car prints", "E", {}, cargo=True)
shot("L52", [[0, [G.SX + 0.16, 2.2, 2.2], [G.SX + 0.16, 0.5, 1.05], 30]], "S52 stair", "SN",
     {"grandma": stand((G.SX, 0.5), 180, "worried", z=G.STEP_RISE * 2 - 0.04, arms=[0, 20])}, card=True, sit={"grandma": 80}, door_dd=90)
shot("L53", [[0, [1.4, 1.9, 1.5], [3.7, 3.0, 0.85], 28]], "S53 Dad wall", "NDAD", {"dad": lying("dad", 90, bed="dad")}, door_dd=85)
shot("L54", fc(HS, 1.0, 348, 0.42, 35, up=0.1), "S54 me", "N", {"me": lying("me", 90, "neutral")}, quilt="lump")
shot("L55", fc((-1.1, G.DOOR_Y, 1.571), 1.0, 0, 0.42, 28, up=0.12, right=0.17), "S55 me", "NDAD", {"me": stand((-1.1, G.DOOR_Y), 90, "hopeful")},
     hide=["w_sp_E"], door_sp=85, door_dd=88)
shot("L56", [[0, [0.0, 1.0, 0.22], [0.0, 2.6, 0.08], 30]], "S56 socks", "N",
     {"me": stand((0.35, 2.55), 90, "neutral")}, door_sp=85, hide=[])
shot("L57", fc((GD[0], GD[1], 1.571 - 0.35), 1.0, 180, 0.34, 32, up=0.0), "S57 me on bed", "NDAD",
     {"dad": lying("dad", 90, bed="dad"), "me": stand(GD, -90, "warm", z=-0.1)}, sit={"me": 80}, door_dd=90, tagd=0.22)
shot("L58", fc((GD[0], GD[1], 1.571 - 0.35), 1.0, 175, 0.4, 35, up=0.0), "S58 me", "NDAD",
     {"dad": lying("dad", 90, bed="dad"), "me": stand(GD, -90, "neutral", z=-0.1)}, sit={"me": 80}, door_dd=90, tagd=0.22)
shot("L59", fc(HD, 1.0, 0, 0.44, 35, up=0.1, right=0.12), "S59 Dad", "NDAD", {"dad": lying("dad", 90, "worried", bed="dad")},
   hide=["w_dd_E"], quilt="lump")
shot("L60", fc(HD, 1.0, 180, 0.44, 35, up=0.1, right=0.12), "S60 Dad turns", "NDAD", {"dad": lying("dad", 90, "worried", bed="dad")}, turn_dad=True)
shot("L61", fc((KX + 3.0, 3.95, 1.4), 1.0, 270, 0.4, 35, up=0.12, right=0.1), "S61 Dad pancake", "K",
     {"dad": sit((KX + 3.0, 3.95), 0, "smile", z=-0.22), "me": stand((KX + 4.2, 3.4), -90, "smile", arms=[0, 52])},
     sit={"dad": 85}, cake0=True)
shot("L62", fc((KX + 1.4, 4.05, 1.571), 1.0, 270, 0.4, 35), "S62 me stove", "K",
     {"me": stand((KX + 1.4, 4.05), 0, "smile")})
shot("L63", fc((KX + 3.0, 3.95, 1.1), 0.72, 270, 0.38, 35, up=0.0), "S63 wink", "K",
     {"grandma": sit((KX + 3.0, 3.95), 0, "smile", z=-0.04)}, sit={"grandma": 85}, glasses=True, card=True, wink=True)
shot("L64", G.orbit((EX + 3.4, 1.0, 0.9), 6.0, 235, 0.8, 28), "S64 car", "E", {}, cargo=False)
shot("L65", [[0, [0.0, 0.9, 1.15], [0.0, 6.55, 1.1], 30]], "S65 door", "N", {}, door_gr=20, door_sp=85, hide=[], crack=True)
shot("L66", fc((1.2, 8.95, 0.9), 0.72, 180, 0.34, 35, dz=0.6, up=0.05, right=0.12), "S66 Grandma wall", "N",
     {"grandma": grandma_in_bed()}, door_gr=20, hide=[], gbed=True)
shot("L67", fc((0.0, 5.3, 1.571), 1.0, 270, 0.42, 33, up=-0.06, dz=0.3), "S67 hall me", "N", {"me": stand((0.0, 5.3), 0, "warm")}, door_gr=20, hide=[], crack=True)
shot("L68", fc(HS, 1.0, 180, 0.46, 30, up=0.0), "S68 loop", "N", {"me": lying("me", -90)}, hide=HIDE_SPW)

# ---------------------------------------------------------------------------------------------- camera arcs
# Every shot over 1.2 s whose camera would hold still gets its own slow arc round its target (the fraction-of-the-shot
# key time 1.0), alternating sides, so the picture itself moves (craft meter: changes per 0.25 s) and the pack's push
# is replaced rather than stacked. Not near a hall wall, a door look or a prop that the tag sits against.
try:
    _dur = {s_["id"]: s_["end"] - s_["start"] for s_ in json.loads((HERE.parent.parent.parent / "out" / "work" /
                                                                   "ep122-face-the-wall" / "timeline.json").read_text())["shots"]}
except Exception:   # noqa: BLE001 - first run, no timeline yet
    _dur = {}
_side = 1
for i, s_ in enumerate(SH):
    d_ = _dur.get(f"S{i + 1:02d}", 0.0)
    m_ = s_["meta"]
    if len(s_["cam"]) != 1 or d_ < 1.2 or any(k in m_ for k in ("tagd", "shadow", "crack", "hand", "roll", "flakes")):
        continue
    if s_["look"] == "NDAD" and "dad" in s_["cast"] or s_["name"].startswith(("S43", "S53")):
        continue   # Dad's blue checker quilt in a moving camera read 6 flashes a second on the flash meter (82.8 s)
    if s_["name"].startswith("S55"):   # hall doorway: the arc ends against the hall wall; keep the side alternation
        _side = -_side
        continue
    c0 = s_["cam"][0]
    px, py, pz = c0[1]
    tx, ty, tz = c0[2]
    if -0.9 < px < 0.9 and 0.0 < py < 6.7 or -0.9 < tx < 0.9 and 0.0 < ty < 6.7:   # the hall: too narrow to swing in
        continue
    th = math.radians(min(18.0, 7.0 * d_)) * _side
    _side = -_side
    dx, dy = px - tx, py - ty
    nx = tx + dx * math.cos(th) - dy * math.sin(th)
    ny = ty + dx * math.sin(th) + dy * math.cos(th)
    k = 0.95   # and a slight push-in
    if 119.0 < px < 121.0:   # the stair: its walls stand at x 119.35 / 120.65, so the camera stays inside them
        nx = tx + (nx - tx) * k
        nx = min(120.42, max(119.58, nx))
        ny = ty + (ny - ty) * k
        s_["cam"] = [c0, [1.0, [round(nx, 3), round(ny, 3), round(pz, 3)], c0[2], c0[3]]]
        continue
    s_["cam"] = [c0, [1.0, [round(tx + (nx - tx) * k, 3), round(ty + (ny - ty) * k, 3), round(pz, 3)], c0[2], c0[3]]]

# ---------------------------------------------------------------------------------------------- finish: ids, acting, cues
shots, meta_out = [], {}
for i, s in enumerate(SH):
    sid = f"S{i + 1:02d}"
    d = {"id": sid, "cam": s["cam"], "step": s["step"]}
    if i:
        d["at"] = remap(s["at"])
    shots.append(d)
    m = {"look": s["look"], "name": s["name"]}
    m.update(s["meta"])
    if "grandma" in s["cast"]:
        m["has_grandma"] = True
    meta_out[sid] = m
    s["id"] = sid

# a character is on screen only in the shots that name them; everyone else is hidden at the shot's start
for i, s in enumerate(SH):
    at = s["at"] if i else 0
    at = remap(at)
    for who in cast:
        if who in s["cast"]:
            spec = dict(s["cast"][who])
            A(who, at, hidden=False, **spec)
        else:
            A(who, at, hidden=True)

# motion inside a shot: rolls, snaps, turns, pats, steps
def sid_of(prefix):
    return next(s["id"] for s in SH if s["name"].startswith(prefix))


def sh(prefix):
    return next(s for s in SH if s["name"].startswith(prefix))


def kk(who, at, **kw):
    acting[who].append({"at": remap(at), **kw})


# L16: roll to the wall (I face the room, then the wall) over the line's first words
# L17: eyes snap open as the bed dips
kk("me", "L17.1+0.35", expr="scared", blend=0.0)
# L33: I turn over, away from the wall, in 0.8 s
# L60: Dad turns from his wall to the room
kk("dad", "L60.2", head=[-90, 0], blend=1.0)
# L25: Grandma climbs one step
# L37: two pats with a flat palm (the right arm raised forward, then down, twice)
# L38: the stripe shot shows only a shadow crossing it (set.py); Grandma is hidden, so she has no walk key
# L56: I cross the hall
kk("me", "L56>", pos=[0.35, 2.55, 0.0], yaw=90, walk=True)
# the rule meter: my nights facing the wall, and the second row
cue(0, "tag", n=0.0, h=0.0)
cue("L16.1", "tag", n=1.0)
cue("L26.1", "tag", n=2.0)
cue("L31", "tag", n=3.0)
cue("L56", "tag", h=1.0)
cue("L66", "tag", h=2.0)
cue("L21", "dawn", u=0.0)
cue("L21", "dawn", u=1.0, dur=1.5)
cue("L30", "dawn", u=0.0)
cue("L30", "dawn", u=1.0, dur=1.5)

LINE_ORDER = {l["id"]: i for i, l in enumerate(lines)}


def sortkey(ref):
    if not isinstance(ref, str):
        return (-1, 0, float(ref))
    mm = re.match(r"^(L\d+|P\d+)(?:\.(\d+))?(?:([+-][\d.]+))?(>?)$", ref)
    if not mm:
        return (999, 0, 0.0)
    li, ch, off, end = mm.groups()
    return (LINE_ORDER[li], 99 if end else int(ch or 0), float(off or 0.0))


for who in acting:   # the engine wants each character's keys in time order (stable: a jump's two keys stay in order)
    acting[who].sort(key=lambda k: sortkey(k["at"]))
remap_all(cues)

sfx = [
    {"at": Raw(f"L01.{CM['L01'][0] + 1}"), "kind": "thud", "db": -9},
    {"at": "L16.1", "kind": "thud", "db": -17},
    {"at": "L17.1", "kind": "thud", "db": -16},
    {"at": "L26.1", "kind": "thud", "db": -17},
    {"at": "L27.1", "kind": "thud", "db": -16},
    {"at": "L31", "kind": "thud", "db": -16},
    {"at": "L38.0+0.9", "kind": "creak", "db": -14},
    {"at": "L42", "kind": "creak", "db": -14},
    {"at": "L63.0+0.2", "kind": "click", "db": -20},
    {"at": "L28.1", "kind": "thud", "db": -19},
    {"at": "L36", "kind": "thud", "db": -18},
    {"at": "L57.1", "kind": "thud", "db": -19},
    {"at": "L60.2", "kind": "creak", "db": -20},
    {"at": "L65.1", "kind": "creak", "db": -21},
]
remap_all(sfx)
music = {
    "root": 50, "mode": "minor", "bpm": 72, "seed": 122,
    "sections": [
        {"at": 0, "voices": ["pad", "piano"], "energy": 0.3},
        {"at": "L17", "voices": ["drone", "pad", "pulse"], "energy": 0.36},
        {"at": "L26", "voices": ["drone", "pad", "pulse", "piano"], "energy": 0.42},
        {"at": "L31", "voices": ["drone", "pad", "pulse", "piano"], "energy": 0.5},
        {"at": "L34", "voices": ["drone"], "energy": 0.3},
        {"at": "L42", "voices": ["drone", "piano"], "energy": 0.34},
        {"at": "L46", "voices": ["pad", "piano"], "energy": 0.46, "root": 50, "mode": "major"},
        {"at": "L64", "voices": ["pad"], "energy": 0.22},
        {"at": "L67", "voices": ["pad", "piano"], "energy": 0.36, "root": 50, "mode": "major"},
    ],
}
remap_all(music["sections"])
sound = {
    "floor": "wood", "steps_db": -26,
    "ambience": [{"kind": "wind", "from": 0, "to": "end", "lufs": -45}],
    "sfx": sfx,
    "music_drops": [{"from": "P01", "to": "P01>"}],
    "rev": REV,
}
remap_all(sound["music_drops"])
polish = {"reveal": [remap("L45")], "twist": remap("L34"),
          "emph": [remap(x) for x in ["L01.1", "L02", "L19", "L34", "L38", "L45", "L55"]],
          "quiet": [[remap("L46"), remap("L50")]],
          "hold": [sid_of("S45")], "reframe_every": 0.5, "reframe_min": 1.0, "reframe_zoom": 1.18, "max_zoom": 1.2, "push": 0.14, "punch": 0.08, "punch_rate": 1.3, "punch_gap": 1.3, "drift": 0.05}
story = {
    "slug": "ep122-face-the-wall",
    "title": "Never Face The WALL At Grandma's",
    "made_for_kids": False,
    "premise": ("At Grandma's, nobody sleeps facing the wall or something sits on your bed. After losing my job I "
                "face it three nights running and something small sits behind me."),
    "twist": ("The something is Grandma, who sits with whoever faces the wall because in our family that means "
              "they're sad; when her knees can't make the stairs, I sit on Dad's bed for her, then on hers."),
    "world": ("A small white clapboard house in winter: a lilac spare room with an iron bed against the wall, a sky-blue "
              "room across the hall, a butter-yellow kitchen with a mint table, a steep wooden stair."),
    "voice": {"voice": "am_adam", "tempo": 1.03, "rate": 1.32},
    "key_color": "#7fb6ff",
    "gap": 0.14,
    "tail": 0.25,
    "fade_in": False,
    "fade_out": False,
    "rev": REV,
    "look": {"style": "closer", "fog": "#cfd0f0", "fog_density": 0.002, "fog_start": 40.0, "sky": "#5b64c0",
             "sky_strength": 1.2, "exposure": 0.2, "flash_safe": True, "polish": polish},
    "grade": {"shadows": [0.01, 0.0, 0.04], "highlights": [0.03, 0.015, -0.01], "saturation": 1.12, "contrast": 1.04,
              "vignette": 0.15, "bloom": 0.2, "grain": 0.006},
    "phonemes": {"Ro": "ɹˈO", "Ezra": "ˈɛzɹə", "Elsie": "ˈɛlsi"},
    "homophones": {"row": "ro", "at": "it", "asked": "asks", "grandma": "grandmas"},
    "cast": cast,
    "lines": lines,
    "shots": shots,
    "acting": acting,
    "cues": cues,
    "fx": [],
    "music": music,
    "sound": sound,
    "set_moves": [],
    "framing_ok": ["S54", "S55", "S66", "S70", "S72", "S73", "S60", "S79"],
}
OUT.write_text(json.dumps(story, indent=1, ensure_ascii=False) + "\n")
(HERE.parent / "meta.json").write_text(json.dumps(meta_out, indent=1) + "\n")
print("wrote", OUT, f"({len(shots)} shots, {len(cues)} cues)")
