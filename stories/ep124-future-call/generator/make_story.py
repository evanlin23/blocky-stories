"""Writes ../story.json for ep124 "future call" (script.md, 2026-11-05, batch 13). Run: python stories/ep124-future-call/generator/make_story.py

The words are in lines.json; places are in ../layout.py (shared with set.py). A character facing -y has yaw 0,
+x 90, +y 180, -x -90; a camera `az` degrees round from the south looks at a character who faces it with yaw = az.
Time references use the script's chunk numbers; set.py reads the cues (timer, button, Dad's stool).
Batch 13: one sunny noon, no light change at all, nothing blinks or glows, the phone never leaves the wall.
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
# the 0.5 s music drop before L26
idx = next(i for i, l in enumerate(lines) if l["id"] == "L26")
lines.insert(idx, {"id": "P01", "pause": 0.5, "chunks": [["", ""]]})
# breath pauses on the phone line: a clear 0.45 s after these lines, with a breath sitting in each
for lid in ("L35", "L24", "L22", "L15", "L14", "L13", "L12"):
    i_ = next(i for i, l in enumerate(lines) if l["id"] == lid)
    lines.insert(i_ + 1, {"id": "P" + lid[1:], "pause": 0.45, "chunks": [["", ""]]})


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
X = {"neutral": "neutral", "uneasy": "worried", "stunned": "wide", "sad": "worried", "cry": "crying",
     "smile": "smile", "laugh": "laugh", "warm": "warm", "det": "hopeful", "sheepish": "sad-smile"}


def person(skin, shirt, pants, shoes, hair="cap", hair_c="#2a1d15", pattern="solid", pattern_c=None, hat="none",
           hat_c="#333333", extras=(), eyes="round", sleeves="long", brow_w=1.0, extra_c=None, **kw):
    d = {"age": "adult", "skin": skin, "shirt": shirt, "pattern": pattern, "pants": pants, "shoes": shoes,
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
    "me": person("#c48a5e", "#2f8f8a", "#3d5a85", "#6a4a32", hair="cap", hair_c="#15110f", pattern="plaid",
                 pattern_c="#1d5f5c", brow_w=1.5),
    "dad": person("#c48a5e", "#26386a", "#7a6a50", "#4a3626", hair="cap", hair_c="#b8b8b8", hat="ballcap",
                  hat_c="#c8202f", sleeves="short", brow_w=1.7, width=1.04),
    "mom": person("#e2b088", "#f2c230", "#4a4a5a", "#2a2a30", hair="long", hair_c="#6a4a3a", eyes="lashes",
                  extras=["hooddown"], extra_c="#f2c230"),
    "uncle": person("#d9a47a", "#e07a30", "#3a4a5a", "#5a4a3a", hair="cap", hair_c="#7a5a3a", hat="bucket",
                    hat_c="#e8d080", brow_w=1.4),
    "friend": person("#b98456", "#c0392b", "#2f3a52", "#e8e4dc", hair="spiky", hair_c="#1a1410", sleeves="short"),
    "sister": person("#c98f64", "#8a5ab0", "#2a2a38", "#3a2a1a", hair="long", hair_c="#150f0c", eyes="lashes",
                     sleeves="short"),
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


def mouth(who, a, b, amt=0.5):
    acting[who].append({"from": a, "to": b, "mouth": [amt, amt], "flap": True})


def cue(at, name, **kw):
    cues.append({"at": at, "name": name, **kw})


def cam(tx, ty, tz, d, az, lens, cz=None, push=None):
    """A camera d metres from (tx, ty, tz), az degrees round from the south, looking at it. One key (the polish pack
    adds the slow push) or, with push=(d2, tz2), two keys."""
    def at_(dd, tzz, czz):
        cx = tx + dd * math.sin(az * D2R)
        cy = ty - dd * math.cos(az * D2R)
        return [round(cx, 3), round(cy, 3), czz if czz is not None else tzz], [tx, ty, tzz]
    p, t_ = at_(d, tz, cz)
    keys = [[0, p, t_, lens]]
    if push:
        p2, t2 = at_(push[0], push[1], None if cz is None else cz + (push[1] - tz))
        keys.append([1, p2, t2, lens])
    return keys


FAR = 1.6


def shot(sid, at, camera, **kw):
    if sid not in ("S25b", "S27", "S36"):   # the first pass framed far too tight: back every camera off its target
        for k in camera:
            p, t_ = k[1], k[2]
            k[1] = [round(t_[i] + (p[i] - t_[i]) * FAR, 3) for i in range(3)]
    SH.append((sid, at, camera, kw))


ME, PH, DAD = G.ME, G.PHONE, G.DAD
FZ = 1.55


def mecam(d=2.2, az=0, lens=36, tx=-0.55, tz=1.27, push=None, ty=None):
    """A portrait of me: head near the top third, the phone off to the left when tx is left of me."""
    return cam(tx, ME[1] if ty is None else ty, tz, d, az, lens, push=push)


def dadcam(d=2.4, az=0, lens=36, tz=1.27, tx=1.35, push=None):
    return cam(tx, DAD[1], tz, d, az, lens, push=push)


# ----------------------------------------------------------------------------------------------- the cast at rest
key("me", 0, ME, yaw=0, expr="neutral", head=[0, 0], arms=[0, 0], side=[0, 0], lean=0)
key("dad", 0, DAD, yaw=0, expr="smile", head=[0, 0], arms=[56, 56], side=[0, 0], lean=0)
key("mom", 0, (G.MOM_ROOM[0], G.MOM_ROOM[1] + 1.05), yaw=0, expr="smile", arms=[55, 55], side=[0, 0])
key("uncle", 0, (G.UNCLE_ROOM[0], G.UNCLE_ROOM[1] + 0.15, 0.12), yaw=0, expr="sheepish", arms=[10, 10], side=[0, 0])
key("friend", 0, (G.KITCHEN[0] - 0.75, G.KITCHEN[1] + 1.15), yaw=0, expr="laugh", arms=[40, 40], side=[0, 0])
key("sister", 0, (G.KITCHEN[0] + 0.75, G.KITCHEN[1] + 1.15), yaw=0, expr="laugh", arms=[40, 40], side=[0, 0])

# the timer: the tag shows "1" (mode 0) until L10, then a call timer (mode 1) that steps on each line to 09:12 at L38
cue(0, "timer", mode=0.0, s=0.0)
TIMED = [f"L{n:02d}" for n in range(10, 39)]
for i, ln in enumerate(TIMED):
    cue(ln, "timer", mode=1.0, s=float(round(552 * i / (len(TIMED) - 1))))
cue(0, "btn", p=0.0)
cue(0, "dsit", s=0.0)

# ===== 01 the rule (L01, L02)
shot("S01a", 0, cam(-0.65, ME[1], 1.27, 2.2, 0, 36))
shot("S01b", "L01.3", cam(-0.55, ME[1], 1.32, 1.7, 0, 36))
key("me", "L02", head=[0, 9], expr="neutral")
key("me", "L02.1", head=[0, 0])
shot("S02", "L02", mecam(2.1, 14, 38))

# ===== 02 the rule at work (L03 to L06)
MX, MY = G.MOM_ROOM
shot("S03", "L03", cam(MX + 0.3, MY + 1.0, 1.85, 3.7, 0, 34, cz=1.5))
UX, UY = G.UNCLE_ROOM
shot("S04a", "L04", cam(UX, UY + 0.15, 1.15, 3.0, 8, 34, cz=1.3))
shot("S04b", "L04.4", cam(UX + 0.1, UY - 0.1, 0.15, 1.5, 15, 30, cz=1.25))
KX, KY = G.KITCHEN
shot("S05", "L05", cam(KX, KY + 1.15, 1.25, 3.0, 0, 30, cz=1.45))
shot("S05b", "L05.3", cam(KX, KY + 1.15, 1.3, 3.25, 0, 27, cz=1.4))   # 3.25 m (was 2.6): the 1.50 m spread cut both faces at 2.6
key("me", "L06", expr="smile", head=[0, 0])
shot("S06", "L06", cam(-0.6, ME[1], 1.27, 2.2, 0, 36))

# ===== 03 the birthday (L07 to L09)
shot("S07", "L07", cam(3.0, 2.6, 0.86, 1.7, 8, 34, cz=1.35))
key("dad", "L08", expr="smile")
mouth("dad", "L08", "L08>", 0.12)
shot("S08", "L08", dadcam(2.5, 4, 36, push=(2.15, 1.3)))
key("me", "L09", expr="neutral")
shot("S09", "L09", cam(PH[0], PH[1], PH[2], 1.3, -6, 38, cz=1.35))

# ===== 04 the call (L10 to L17)
cue("L10", "btn", p=1.0, dur=0.12)
cut("me", "L10", (-0.27, 3.1), yaw=-90, expr="smile", arms=[0, 96], head=[0, 0])
shot("S10a", "L10", cam(PH[0] + 0.65, PH[1], 1.3, 3.2, 0, 38, cz=1.3))
cut("me", "L10.1", ME, yaw=0, expr="smile", arms=[0, 0], head=[0, 0])
mouth("me", "L10.1", "L10.1>", 0.5)
shot("S10b", "L10.1", mecam(2.2, 0, 36, tx=-0.6))
key("me", "L11", expr="neutral")
shot("S11", "L11", mecam(2.1, 10, 36, tx=-0.55))
shot("S12", "L12", cam(PH[0] - 0.12, PH[1], 1.28, 1.15, -28, 46, cz=1.3, push=(0.95, 1.28)))
key("me", "L13", expr="uneasy")
shot("S13", "L13", mecam(2.0, -8, 36, push=(1.8, 1.27)))
shot("S14", "L14", mecam(1.7, 8, 36, push=(1.5, 1.27)))
shot("S15", "L15", mecam(1.45, -5, 36, push=(1.25, 1.27)))
cut("me", "L16", ME, yaw=0, expr="neutral", head=[-28, 0])
shot("S16", "L16", mecam(1.7, 12, 36, tx=-0.35))
cue("L17", "btn", p=1.0)
shot("S17", "L17", cam(PH[0], PH[1], 1.25, 1.0, -12, 38, cz=1.3))

# ===== 05 Dad's joke (L18 to L25)
cut("me", "L18", ME, yaw=0, expr="uneasy", head=[0, 0])
key("dad", "L18", expr="smile")
mouth("dad", "L18", "L19>", 0.3)
shot("S18", "L18", dadcam(2.4, 0, 36, push=(2.0, 1.3)))
key("dad", "L19", expr="smile", arms=[56, 56])
shot("S19", "L19", cam(1.55, DAD[1], 1.2, 2.2, 14, 32, cz=1.0))
key("dad", "L20", expr="laugh", head=[0, -5], lean=0)
shot("S20", "L20", dadcam(2.1, -8, 36))
key("dad", "L21", expr="laugh", head=[0, -3])
shot("S21", "L21", dadcam(1.8, 6, 36, tz=1.3))
cut("me", "L22", ME, yaw=18, expr="stunned", head=[0, 0])
shot("S22", "L22", cam(-0.55, ME[1], 1.27, 2.0, 18, 36, push=(1.7, 1.27)))
key("dad", "L23", expr="laugh", head=[0, -4])
shot("S23", "L23", dadcam(2.0, -18, 36))
shot("S24", "L24", cam(PH[0], PH[1], 1.25, 1.1, -30, 38, cz=1.3, push=(0.9, 1.25)))
cut("me", "L25", ME, yaw=0, expr="cry", head=[0, 6])
shot("S25", "L25", mecam(1.8, 0, 36))
shot("S25b", "P01", cam(0.4, 0.0, 1.3, 3.0, 180, 26, cz=1.3), _drop=True)

# ===== 06 the reveal (L26 to L29)
key("dad", "L26", expr="laugh", head=[0, -2])
cut("me", "L26", ME, yaw=0, expr="stunned", head=[0, 0])
shot("S26", "L26", mecam(1.5, 0, 36))
# S27: the camera sits west of me, so Dad is at the bench behind and to the right of me
key("dad", "L27", yaw=-45, expr="laugh", blend=0.0)
cut("me", "L27", ME, yaw=-25, expr="stunned", head=[0, 0])
shot("S27", "L27", [[0, [-1.8, 1.9, 1.45], [0.35, 3.5, 1.4], 19], [1, [-1.65, 2.05, 1.45], [0.35, 3.5, 1.4], 19]])
cut("dad", "L28", DAD, yaw=0, expr="laugh", head=[0, -5], arms=[56, 56])
shot("S28", "L28", dadcam(2.3, -4, 36, tz=1.3))
cut("me", "L29", ME, yaw=0, expr="sad", head=[0, 10])
shot("S29", "L29", mecam(1.7, 0, 36))

# ===== 07 the plan (L30 to L37)
key("me", "L30", expr="det", head=[0, 0])
shot("S30", "L30", mecam(1.9, -6, 36, push=(1.6, 1.27)))
cut("me", "L31", ME, yaw=90, expr="smile", head=[-70, 0])
ME_OLD = list(G.ME_NEAR_DAD)  # S36/S37 keep the old place
ME_NEAR = [0.30, 3.35]  # S31-S34: 1.45 m from Dad
DAD_N = [1.75, 3.35]
cut("dad", "L31", DAD_N, yaw=0, expr="smile", head=[0, 0], arms=[56, 56])
key("me", "L31.1", ME_NEAR, yaw=90, head=[-70, 0])
key("me", "L31.2", ME_NEAR, yaw=0, head=[0, 0], blend=0.4)
shot("S31", "L31", cam(1.03, 3.35, 1.25, 3.0, 2, 27, cz=1.4))
key("dad", "L32", expr="laugh", head=[0, -3])
mouth("dad", "L32", "L32>", 0.4)
shot("S32", "L32", dadcam(2.3, 6, 36, tx=1.6))
key("dad", "L33", expr="laugh")
mouth("dad", "L33", "L33.2", 0.4)
shot("S33a", "L33", cam(1.6, DAD[1], 1.05, 2.4, 6, 32, cz=1.25))
key("me", "L33.2", expr="laugh")
shot("S33b", "L33.2", cam(ME_NEAR[0] + 0.1, DAD[1], 1.1, 2.0, -6, 32, cz=1.25))
key("dad", "L34", expr="laugh", head=[0, -4])
cue("L34.1", "dsit", s=1.0, dur=0.25)
key("dad", "L34.1", list(DAD_N) + [-0.34], expr="laugh", head=[0, -4], arms=[56, 56])
shot("S34", "L34", cam(DAD_N[0] - 0.1, DAD[1] + 0.1, 1.15, 2.6, 4, 34, cz=1.5))
shot("S35", "L35", cam(PH[0], PH[1], 1.25, 1.15, -8, 38, cz=1.3, push=(0.95, 1.25)))
cut("dad", "L36", [DAD[0] + 0.75, DAD[1], 0], yaw=0, expr="laugh", head=[0, -2], arms=[56, 56])
cue("L36", "dsit", s=0.0, dur=0.0)
cut("me", "L36", [ME_OLD[0] + 0.4, ME_OLD[1]], yaw=0, expr="laugh", head=[0, -2])
shot("S36", "L36", cam(1.6, 3.35, 1.45, 6.2, 0, 38, cz=1.5, push=(5.7, 1.45)))
shot("S37", "L37", mecam(1.8, 6, 36, tx=ME_OLD[0] + 0.55, ty=ME_OLD[1]))

# ===== 08 the click (L38 to L44)
cue("L38", "btn", p=0.0, dur=0.1)
cut("me", "L38", [0.4, ME[1]], yaw=0, expr="neutral", head=[0, 0])
cut("dad", "L38", DAD, yaw=0, expr="smile", head=[0, 0], arms=[56, 56])
shot("S38", "L38", cam(PH[0], PH[1], 1.25, 1.2, -4, 38, cz=1.3))
key("dad", "L39", expr="smile")
mouth("dad", "L39", "L39>", 0.14)
shot("S39", "L39", dadcam(2.2, -6, 36))
cut("me", "L39.1", ME, yaw=0, expr="neutral", head=[0, 0])
key("me", "L40", expr="warm")
shot("S40", "L40", mecam(1.9, 8, 36))
key("dad", "L41", expr="laugh", head=[0, -3])
mouth("dad", "L41", "L41.1", 0.3)
shot("S41", "L41", dadcam(2.0, 12, 36, tz=1.3))
key("me", "L42", expr="smile")
shot("S42", "L42", mecam(1.8, -10, 36))
shot("S43", "L43", cam(PH[0] - 0.15, PH[1], 1.28, 1.7, -14, 36, cz=1.4))
cut("me", "L44", ME, yaw=0, expr="neutral", head=[0, 0])
shot("S44", "L44", cam(-0.65, ME[1], 1.27, 2.5, 0, 36, push=(1.9, 1.3)))

# ----------------------------------------------------------------------------------------------- finish
remap_all(cues)
for k_ in acting.values():
    remap_all(k_)
shots, names = [], {}
for i, (sid, at, camera, kw) in enumerate(SH):
    s = {"id": sid, "cam": camera, "step": 2}
    if i:
        s["at"] = remap(at)
    kw = {k: v for k, v in kw.items() if not k.startswith("_")}
    s.update(kw)
    shots.append(s)

sfx = [
    {"at": "L01.3", "kind": "bell", "db": -17},
    {"at": "L09.2", "kind": "bell", "db": -17},
    {"at": "L10", "kind": "click", "db": -15},
    {"at": "L38.2", "kind": "click", "db": -14},
    {"at": "L34", "kind": "creak", "db": -22, "dur": 0.35},
    {"at": "L34.1", "kind": "thud", "db": -20},
    {"at": "L17", "kind": "click", "db": -17},
    # soft breaths on the line (low band noise, nothing above 4 kHz): slow in L12 to L15, held while I talk (L16, L17),
    # a shaky pair at L22, a fading one at L24 and L25, a laugh-like triple at L35, gone after the click
    {"at": "P12", "kind": "breath", "db": -11, "dur": 0.42},
    {"at": "P13", "kind": "breath", "db": -11, "dur": 0.42},
    {"at": "P14", "kind": "breath", "db": -11, "dur": 0.42},
    {"at": "P15", "kind": "breath", "db": -11, "dur": 0.42},
    {"at": "P22", "kind": "breath", "db": -11, "dur": 0.4},
    {"at": "P24", "kind": "breath", "db": -11, "dur": 0.42},
    {"at": "P01", "kind": "breath", "db": -11, "dur": 0.45},
    {"at": "P35", "kind": "breath", "db": -11, "dur": 0.4},
]
music = {
    "root": 52, "mode": "minor", "bpm": 84, "seed": 124,
    "sections": [
        {"at": 0, "voices": ["piano", "pad"], "energy": 0.34},
        {"at": "L11", "voices": ["pad"], "energy": 0.14},
        {"at": "L18", "voices": ["pad", "pulse"], "energy": 0.3},
        {"at": "L26", "voices": ["drone"], "energy": 0.2},
        {"at": "L30", "voices": ["piano", "pad"], "energy": 0.55, "mode": "major"},
        {"at": "L38", "voices": ["pad"], "energy": 0.16},
        {"at": "L39", "voices": ["piano", "pad"], "energy": 0.3},
    ],
}
sound = {
    "floor": "concrete", "steps_db": -26,
    "sfx": sfx,
    "music_drops": [{"from": "L12", "to": "P15>", "keep": ["breath"]}, {"from": "P01", "to": "P01>", "keep": ["breath"]},
                    {"from": "P22", "to": "P22>", "keep": ["breath"]}, {"from": "P24", "to": "P24>", "keep": ["breath"]},
                    {"from": "P35", "to": "P35>", "keep": ["breath"]}],
    "rev": REV,
}
remap_all(sfx)
remap_all(music["sections"])
remap_all(sound["music_drops"])
polish = {"reveal": [remap("L27")], "twist": remap("L26"),
          "emph": [remap(x) for x in ["L01.3", "L09.2", "L20", "L21.2", "L26.1", "L36.2"]],
          "quiet": [[remap("L39"), remap("L42")]],
          "hold": ["S01a", "S36", "S44"]}
story = {
    "slug": "ep124-future-call",
    "title": "Future Me Called And Said NOTHING",
    "made_for_kids": False,
    "premise": ("On your thirtieth birthday your future self phones you once with advice, but mine only breathes "
                "on the line and goes quiet whenever I talk."),
    "twist": ("He kept quiet on purpose: future me called just to hear Dad laugh in his garage one more time, so I "
              "stop talking and get Dad telling every bad joke for the whole call, and now I save up his laughs for "
              "the call I'll make myself one day."),
    "world": ("Dad's sunny two-car garage on a Saturday noon: an open roll-up door, a red pickup, a long maple bench "
              "with a pegboard of outlined tools, and a cream wall speakerphone."),
    "voice": {"voice": "am_adam", "tempo": 1.03, "rate": 1.45},
    "key_color": "#3fd0c0",
    "gap": 0.12,
    "tail": 0.25,
    "fade_in": False,
    "fade_out": False,
    "rev": REV,
    "look": {"style": "closer", "fog": "#dfe8f4", "fog_density": 0.001, "fog_start": 60.0, "sky": "#8fd0ff",
             "sky_strength": 1.0, "exposure": 0.05, "flash_safe": True, "polish": polish},
    "grade": {"shadows": [0.0, 0.0, 0.02], "highlights": [0.03, 0.012, -0.02], "saturation": 1.08, "contrast": 1.04,
              "vignette": 0.15, "bloom": 0.15, "grain": 0.008},
    "rain_shots": ["S03"],
    "phonemes": {"laughs": "lˈæfs"},
    "cast": cast,
    "lines": lines,
    "shots": shots,
    "acting": acting,
    "cues": cues,
    "fx": [],
    "music": music,
    "sound": sound,
    "set_moves": [],
    "frames_ok": ["S31"],
    # S36 (1.30 m) and S39 (1.10 m): checked on the final by the QA desk 2026-11-06, the arms read apart
    "staging_ok": ["S36/me+dad", "S39/me+dad"],
    "framing_ok": ["S26", "S35", "S42"],
}
OUT.write_text(json.dumps(story, indent=1, ensure_ascii=False) + "\n")
print("wrote", OUT, f"({len(shots)} shots, {len(cues)} cues)")
