"""Writes ../story.json for ep132 "bus stop" (script.md, 2026-11-06, batch 14). Run: python stories/ep132-bus-stop/generator/make_story.py

The words are in lines.json; places are in ../layout.py (shared with set.py). A character facing -y has yaw 0,
+x 90, +y 180, -x -90; a camera `az` degrees round from the south looks at a character who faces it with yaw = az.
Time references use the script's chunk numbers (remapped through timeline.split_lines).
Batch 14: one sunny morning, no light change at all; no set moves (the depot door is shut, then up after a cut; the
bus is placed by cues on cuts and never drives); no text anywhere but the chalk numerals.
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
X = {"neutral": "neutral", "bored": "blank", "uneasy": "worried", "stunned": "wide", "sad": "worried",
     "smile": "smile", "laugh": "laugh", "warm": "warm", "sheepish": "sad-smile"}


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
    # me: short wavy brown hair, pale skin, a blue work shirt
    "me": person("#f0cfb0", "#5f8fd0", "#3d4660", "#3a2a20", hair="cap", hair_c="#6a4228", brow_w=1.3),
    # Mr. Tolley: round glasses, a neat brown mustache (built in set.py), a gray cardigan over a pale blue shirt
    "driver": person("#e2b088", "#9a9aa2", "#4a4a50", "#2f2a26", hair="cap", hair_c="#4a3626", pattern="knit",
                     pattern_c="#8a8a94", collar="#bcd8f0", extras=["glasses"], extra_c="#3a2a1a", brow_w=1.3),
    # the same man in his uniform (a navy jacket and tie) from the reveal on
    "driver_b": person("#e2b088", "#26386a", "#2a2f44", "#2f2a26", hair="cap", hair_c="#4a3626", collar="#bcd8f0",
                       extras=["glasses", "tie"], extra_c="#3a2a1a", brow_w=1.3),
    # the woman in the sun hat
    "wa": person("#d9a47a", "#e8806a", "#3a4a5a", "#6a4a32", hair="long", hair_c="#5a3a2a", hat="bucket",
                 hat_c="#f2e6b0", eyes="lashes"),
    # the man in the scarf
    "ma": person("#a8744c", "#5a7a5a", "#2f3a52", "#3a2a1a", hair="buzz", hair_c="#1a1410", extras=["scarf"],
                 extra_c="#d65a3a", brow_w=1.4),
    # a new commuter: a woman with a red scarf
    "nc": person("#c98f64", "#3a9a9a", "#2a2a38", "#3a2a1a", hair="bun", hair_c="#2a1a1a", eyes="lashes",
                 extras=["scarf"], extra_c="#d8473a"),
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


def wpos(st, local):
    bx, by, yaw = st
    th = yaw * D2R
    x, y = local
    return (round(bx + x * math.cos(th) - y * math.sin(th), 3), round(by + x * math.sin(th) + y * math.cos(th), 3))


def seat(who, at, pos, **kw):
    """Seated on the bench (or the bus) from `at`, at once."""
    cut(who, at, [pos[0], pos[1], G.SIT_Z if len(pos) == 2 else pos[2]], **kw)


SIT_ALL = ("me", "driver", "driver_b", "wa", "ma", "nc")
ME, TOL, WOM, MAN, NC = G.ME, G.TOL, G.WOM, G.MAN, G.NC
DRV_STOP, FRONT_STOP = wpos(G.BUS_STOP, G.BUS_DRV), wpos(G.BUS_STOP, G.BUS_FRONT)
DRV_MOUTH = wpos(G.BUS_MOUTH, G.BUS_DRV)

# ----------------------------------------------------------------------------------------------- the cast at rest
key("me", 0, [*ME, G.SIT_Z], yaw=0, expr="neutral", head=[0, 0], arms=[0, 0], side=[0, 0], lean=0)
key("driver", 0, [*TOL, G.SIT_Z], yaw=0, expr="neutral", head=[0, 0], arms=[0, 0], side=[0, 0])
key("wa", 0, [*WOM, G.SIT_Z], yaw=0, expr="neutral", head=[0, 14], arms=[0, 0], side=[0, 0])
key("ma", 0, [*MAN, G.SIT_Z], yaw=0, expr="sad", head=[0, 0], arms=[0, 0], side=[0, 0])
key("nc", 0, [*NC, G.SIT_Z], yaw=0, expr="uneasy", hidden=True, head=[0, 0], arms=[0, 0], side=[0, 0])
key("driver_b", 0, [*DRV_MOUTH, G.BUS_SEAT_Z], yaw=180, expr="laugh", hidden=True, arms=[0, 0], side=[0, 0])
cue(0, "sit", me=1.0, driver=1.0, wa=1.0, ma=1.0, nc=0.0, driver_b=0.0)
cue(0, "door", up=0.0)
cue(0, "chalk", two=0.0)
cue(0, "bus", x=G.BUS_HIDE[0], y=G.BUS_HIDE[1], yaw=G.BUS_HIDE[2])

# ===== 01 the rule (L01, L02)
shot("S01a", 0, cam(2.0, 1.3, 1.3, 2.2, 0, 36, cz=1.35, push=(1.9, 1.3)))
shot("S01b", "L01.2", cam(2.0, 1.3, 1.3, 1.9, 0, 36, cz=1.35, push=(1.8, 1.3)))
shot("S02", "L02", cam(WOM[0], 1.1, 1.3, 1.25, 0, 36, cz=1.35, push=(1.05, 1.3)))
key("wa", "L02.1", head=[0, 6])

# ===== 02 the rule at work (L03 to L07)
# S03: shoe height, three pairs of shoes filling the frame, the bench's steel foot with the lore strokes at the edge
shot("S03", "L03", camp([-0.45, -3.0, 0.5], [-0.45, 0.55, -0.68], 20, pos2=[-0.45, -2.7, 0.5], tgt2=[-0.45, 0.55, -0.62]))
shot("S04", "L04", cam(2.52, 1.5, 1.6, 1.5, 5, 36, cz=1.55, push=(1.2, 1.6)))
cut("wa", "L05", hidden=True)       # the man alone in S05 (the woman's hat would be cut; the old driver is not in the scene)
cut("driver", "L05", hidden=True)
shot("S05", "L05", cam(MAN[0], 1.1, 1.3, 1.5, -8, 36, cz=1.35, push=(1.15, 1.3)))
shot("S06", "L06", camp([-0.6, -4.2, 1.6], [0, G.DEPOT_Y, 2.3], 17, pos2=[0.6, -5.6, 1.6]))
# S07: she and I stand and walk toward the camera (both faces to camera, the chalk count beside us, he is out)
cut("driver", "L07", hidden=True)
cut("wa", "L07", [0.85, 1.1, G.SIT_Z], yaw=0, expr="bored", head=[0, 0], hidden=False)
cut("me", "L07", [1.7, 1.1, G.SIT_Z], yaw=0, expr="bored", head=[0, 0])
cue("L07", "sit", wa=0.0, me=0.0, dur=0.3)
key("wa", "L07.1", [0.85, 1.1, 0.0], yaw=0)
key("wa", "L07.2", [0.85, 0.2, 0.0], yaw=0)
key("me", "L07.1", [1.7, 1.1, 0.0], yaw=0)
key("me", "L07.2", [1.7, 0.2, 0.0], yaw=0)
shot("S07", "L07", cam(1.7, 0.6, 1.2, 2.7, 0, 36, cz=1.3, push=(2.55, 1.2)))

# ===== 03 day forty-two (L08 to L11)
cut("driver", "L08", [*G.TOL8, G.SIT_Z], yaw=0, expr="neutral", head=[0, 0], hidden=False, arms=[0, 0])
cut("me", "L08", [*G.ME8, G.SIT_Z], yaw=0, expr="neutral", head=[0, 0])
cut("wa", "L08", [*WOM, G.SIT_Z], hidden=True)
cut("ma", "L08", [*MAN, G.SIT_Z], hidden=True)
cue("L08", "sit", me=1.0, driver=1.0)
shot("S08a", "L08", cam(1.96, 1.1, 1.3, 2.18, 0, 36, cz=1.35, push=(2.12, 1.3)))
key("driver", "L08.3", expr="sad", head=[0, -9])
key("driver", "L09", expr="neutral", head=[0, 4])
shot("S08b", "L08.3", cam(1.96, 1.1, 1.3, 2.15, -6, 36, cz=1.35, push=(2.1, 1.3)))
key("me", "L09", expr="uneasy")
key("me", "L09.1", expr="smile")
mouth("me", "L09.1", "L09>", 0.5)
shot("S09", "L09", cam(1.9, 1.1, 1.3, 1.2, 6, 36, cz=1.35, push=(1.05, 1.3)))
key("driver", "L10", expr="stunned", head=[0, 0])
shot("S10a", "L10", cam(0.95, 1.1, 1.3, 1.3, 0, 36, cz=1.35, push=(1.1, 1.3)))
key("driver", "L10.2", expr="smile")
shot("S10b", "L10.2", cam(0.9, 1.1, 1.3, 1.3, -8, 36, cz=1.35, push=(1.15, 1.3)))
key("driver", "L11", expr="smile")
mouth("driver", "L11.1", "L11>", 0.5)
shot("S11", "L11", cam(0.9, 1.1, 1.3, 1.3, 7, 36, cz=1.35, push=(1.0, 1.3)))

# ===== 04 he stands, crosses, the door is up (L12 to L14)
cue("L12", "sit", driver=0.0, dur=0.35)
key("driver", "L12", [*G.TOL8, 0.0], yaw=0, expr="smile", head=[0, 0])
shot("S12", "L12", cam(0.95, 1.1, 1.5, 1.3, 0, 36, cz=1.5, push=(1.2, 1.55)))
cut("driver", "L13", [0.8, -1.8, 0.0], yaw=0, expr="smile")
key("driver", "L13.1", [0.8, -3.6, 0.0], yaw=0)
cut("me", "L13", hidden=True)       # out of the S13a picture (the camera stands where I sit)
shot("S13a", "L13", camp([0.8, 1.6, 1.7], [0.8, -2.4, 0.9], 16, pos2=[0.8, 1.6, 1.7], tgt2=[0.8, -3.2, 0.9]))
cut("driver", "L13.1", [0.75, -6.0, 0.0], hidden=True)
cue("L13.1", "door", up=1.0)
cue("L13.1", "bus", x=G.BUS_IN[0], y=G.BUS_IN[1], yaw=G.BUS_IN[2])
shot("S13b", "L13.1", camp([0.3, -5.3, 1.7], [0, G.DEPOT_Y, 1.9], 24, pos2=[0.1, -7.3, 1.7]))
cut("me", "L14", [*ME, G.SIT_Z], yaw=0, expr="stunned", head=[0, 0], hidden=False)
cue("L14", "sit", me=1.0)
shot("S14", "L14", cam(1.5, 1.1, 1.3, 1.5, 0, 36, cz=1.35, push=(1.25, 1.3)))

# ===== 05 the reveal (L15, L16)
cut("driver_b", "L15", [*DRV_MOUTH, G.BUS_SEAT_Z], yaw=180, expr="laugh", hidden=False, arms=[0, 40], head=[0, 0])
cue("L15", "sit", driver_b=1.0)
cue("L15", "bus", x=G.BUS_MOUTH[0], y=G.BUS_MOUTH[1], yaw=G.BUS_MOUTH[2])
for i, a in enumerate((60, 30, 60)):
    key("driver_b", f"L15+{0.3 * (i + 1):.2f}", arms=[0, a])
shot("S15a", "L15", camp([-0.4, -6.2, 1.9], [-0.45, -12.9, 1.75], 40, pos2=[-0.5, -8.0, 1.9]))
key("driver_b", "L15.2", arms=[0, 40])
for i, a in enumerate((60, 30, 60, 30, 60, 30)):
    key("driver_b", f"L15.2+{0.28 * (i + 1):.2f}", arms=[0, a])
shot("S15b", "L15.2", camp([DRV_MOUTH[0], -8.8, 2.0], [DRV_MOUTH[0], DRV_MOUTH[1], 1.95], 40,
                           pos2=[DRV_MOUTH[0], -10.0, 2.0]))
key("driver_b", "L16", expr="sheepish", head=[0, 8], arms=[0, 0])
shot("S16", "L16", camp([DRV_MOUTH[0], -10.2, 2.0], [DRV_MOUTH[0], DRV_MOUTH[1], 1.95], 40,
                        pos2=[DRV_MOUTH[0], -9.0, 2.0]))

# ===== 06 the bus at the stop (L17 to L19)
cue("L17", "bus", x=G.BUS_STOP[0], y=G.BUS_STOP[1], yaw=G.BUS_STOP[2])
cut("driver_b", "L17", [*DRV_STOP, G.BUS_SEAT_Z], yaw=-40, expr="smile", head=[0, 0], arms=[0, 40])
cut("me", "L17", [*FRONT_STOP, G.BUS_SEAT_Z], yaw=-40, expr="smile", head=[0, 0])
shot("S17", "L17", camp([2.0, -14.5, 11.0], [2.3, -1.0, 2.4], 26, pos2=[2.1, -13.0, 10.2]))
cut("driver_b", "L18", [*DRV_STOP, G.BUS_SEAT_Z], yaw=-85, expr="smile", head=[0, 0], arms=[0, 40])
cut("me", "L18", [*FRONT_STOP, G.BUS_SEAT_Z], yaw=-85, expr="smile", head=[0, 0])
shot("S18a", "L18", camp([-4.2, -3.45, 1.9], [0.3, -3.45, 1.55], 30, pos2=[-3.9, -3.45, 1.9]))
key("me", "L18.2", expr="smile", head=[0, 0])
shot("S18b", "L18.2", camp([-4.1, -3.45, 1.9], [0.3, -3.45, 1.55], 30, pos2=[-3.8, -3.45, 1.9]))
cut("driver_b", "L19", [*DRV_STOP, G.BUS_SEAT_Z], yaw=-90, expr="laugh", head=[0, 0], arms=[0, 40])
mouth("driver_b", "L19", "L19>", 0.45)
shot("S19", "L19", camp([-4.9, -4.1, 1.95], [0.3, -4.1, 1.9], 36, pos2=[-3.7, -4.1, 1.95]))

# ===== 07 somebody new, so I go first (L20 to L22)
cut("driver_b", "L20", [*DRV_STOP, G.BUS_SEAT_Z], hidden=True)
cut("me", "L20", [*TOL, G.SIT_Z], yaw=0, expr="neutral", hidden=True)
cut("nc", "L20", [*NC, G.SIT_Z], yaw=0, expr="uneasy", hidden=False, head=[0, 0])
cue("L20", "sit", nc=1.0, me=1.0)
cue("L20", "chalk", two=1.0)
cue("L20", "bus", x=G.BUS_HIDE[0], y=G.BUS_HIDE[1], yaw=G.BUS_HIDE[2])
shot("S20a", "L20", cam(2.0, 1.3, 1.3, 2.2, 0, 36, cz=1.35))
key("nc", "L20.2", expr="uneasy", head=[0, 6])
shot("S20b", "L20.2", cam(2.0, 1.3, 1.3, 1.9, -8, 36, cz=1.35, push=(1.85, 1.3)))
cut("me", "L21", [*G.ME_NC, G.SIT_Z], yaw=0, expr="smile", hidden=False, head=[0, 0])
mouth("me", "L21", "L21>", 0.5)
key("nc", "L21", expr="uneasy", head=[0, 0])
key("nc", "L21+0.9", expr="smile")
shot("S21", "L21", [cam(1.9, 1.1, 1.3, 2.35, 3, 36, cz=1.35)[0], [1, *cam(1.9, 1.1, 1.3, 2.3, 3, 36, cz=1.35)[0][1:]]])
cut("nc", "L22", [*NC, G.SIT_Z], hidden=True)
cut("me", "L22", [*ME, G.SIT_Z], yaw=0, expr="smile", hidden=False, head=[0, 0])
key("me", "L22.2", expr="neutral")
shot("S22a", "L22", cam(2.0, 1.3, 1.3, 2.2, 0, 36, cz=1.35))
shot("S22b", "L22.2", cam(2.0, 1.3, 1.3, 1.9, 0, 36, cz=1.35, push=(1.7, 1.3)))

# ----------------------------------------------------------------------------------------------- finish
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

sfx = [
    {"at": "L01.2", "kind": "bell", "db": -18},          # the soft coin-like clink on "TALKING"
    {"at": "L08.3", "kind": "breath", "db": -13, "dur": 0.7},   # the sigh
    {"at": "L13.1", "kind": "door", "db": -15},           # a low rumble off screen over the cut to the open door
    {"at": "L17.1", "kind": "whoosh", "db": -26},         # a gentle brake hiss
]
music = {
    "root": 53, "mode": "major", "bpm": 120, "seed": 132,
    "sections": [
        {"at": 0, "voices": ["piano", "pad"], "energy": 0.3},
        {"at": "L09", "voices": ["piano", "pad"], "energy": 0.42},
        {"at": "L12", "voices": ["piano", "pad", "pulse"], "energy": 0.5},
        {"at": "L17", "voices": ["piano", "pad", "pulse"], "energy": 0.62},
    ],
}
sound = {
    "floor": "concrete", "steps_db": -24,
    "ambience": [{"kind": "traffic", "from": 0, "to": "end", "lufs": -40},
                 {"kind": "hum", "from": "L17", "to": "L18>", "lufs": -40}],
    "sfx": sfx,
    "rev": REV,
}
remap_all(sfx)
remap_all(music["sections"])
remap_all(sound["ambience"])
polish = {"reveal": ["L14", "L15"], "twist": "L14", "emph": ["L01.2", "L02.1", "L14"],
          "quiet": [["L18", "L19>"]], "hold": ["S06", "S07", "S08a", "S13b", "S17", "S21"]}
polish["emph"] = [remap(x) for x in polish["emph"]]
story = {
    "slug": "ep132-bus-stop",
    "title": "The Bus Hasn't Come In 41 DAYS",
    "made_for_kids": False,
    "premise": ("At our bus stop the fare is two strangers talking, and the bus hasn't come in forty-one days because "
                "nobody here goes first."),
    "twist": ("The quiet man on the bench every morning is the new driver, too shy to speak first; when I finally say "
              "'nice day' he crosses the street, opens the depot and drives the bus out, and now I go first for every "
              "new face on the bench."),
    "world": ("A sunny small-town corner: a red glass bus shelter with a pale yellow side wall and a slate chalk board, "
              "a long wooden bench, a cherry tree, and across the street a brick bus depot with a big blue roll-up door."),
    "voice": {"voice": "am_adam", "tempo": 1.03, "rate": 1.45},
    "key_color": "#ff5a4a",
    "gap": 0.15,
    "tail": 0.25,
    "fade_in": False,
    "fade_out": False,
    "rev": REV,
    "look": {"style": "closer", "fog": "#dfe8f4", "fog_density": 0.001, "fog_start": 60.0, "sky": "#8fd6ff",
             "sky_strength": 1.0, "exposure": 0.05, "flash_safe": True, "polish": polish},
    "grade": {"shadows": [0.0, 0.0, 0.02], "highlights": [0.03, 0.012, -0.02], "saturation": 1.08, "contrast": 1.04,
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
    "framing_ok": [],
    "frames_ok": ["S07", "S12"],
}
OUT.write_text(json.dumps(story, indent=1, ensure_ascii=False) + "\n")
print("wrote", OUT, f"({len(shots)} shots, {len(cues)} cues)")
