"""Writes ../story.json for ep138 "the gym where you see tomorrow" (script.md, 2026-11-06, batch 15a, interactive lane).
Run: python stories/ep138-tomorrow-mirror/generator/make_story.py

The words are in lines.json; places are in ../layout.py (shared with set.py). A character facing -y has yaw 0,
+x 90, +y 180, -x -90. Two kinds of shot: REAL (a camera in the room) and GLASS (a camera standing at the mirror,
looking west out into the same gym, with a chrome pillar and a faint cool pane in front of it, set in the scene by the
`glass` cue). The real me and tomorrow-me (`me2`) are never in one shot. No light ever changes.
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
X = {"neutral": "neutral", "serious": "blank", "uneasy": "worried", "stunned": "wide", "sad": "worried",
     "smile": "smile", "laugh": "laugh", "scared": "scared"}


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


SAM = dict(skin="#c58e64", shirt="#8a8f99", pants="#1c1c22", shoes="#f2f2f2", hair="cap", hair_c="#15151a",
           brow_w=1.3, collar="#f4f4f4")
cast = {
    # Sam: short black hair, light brown skin, a gray tank over a white tee, dark bottoms
    "me": person(**SAM),
    # tomorrow-me: the same model, his own shots
    "me2": person(**SAM),
    # Dre: broad, short twists, a red hoodie
    "dre": person("#7a4a2e", "#d83a3a", "#2a2a30", "#f2f2f2", hair="spiky", hair_c="#111114", extras=["hooddown"],
                  brow_w=1.3, width=1.12, sleeves="long"),
    # Big Wendell: about 60, bald, a gray mustache (built in set.py), a black polo
    "wendell": person("#c99870", "#1c1c20", "#4a4a52", "#2a2a30", hair="none", brow_w=1.4, width=1.1, sleeves="short"),
    # Mr. Kim: neat black hair, a blue tracksuit
    "kim": person("#ecc9a0", "#2a5fb0", "#24508f", "#f2f2f2", hair="swoop", hair_c="#15151a", sleeves="long",
                  collar="#e8eefc"),
    # Lena: short purple hair, a white tee
    "lena": person("#d9a47a", "#f4f4f4", "#3a4a6a", "#f2f2f2", hair="cap", hair_c="#8a4ad0", eyes="lashes"),
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
    """Only these characters are on screen from `at` (a cut)."""
    for n in cast:
        if n in names and n not in vis:
            vis.add(n)
            cut(n, at, hidden=False)
        elif n not in names and n in vis:
            vis.discard(n)
            cut(n, at, hidden=True)


def mouth(who, a, b, amt=0.5):
    acting[who].append({"from": a, "to": b, "mouth": [amt, amt], "flap": True})


def big_mouth(who, at, n, step=0.4):
    """Slow, big mouth shapes: open and shut over `step` seconds, n times (a mouthed sentence)."""
    for i in range(n):
        a = f"{at}+{i * step:.2f}"
        b = f"{at}+{(i + 1) * step:.2f}"
        lo, hi = (0.05, 0.85) if i % 2 == 0 else (0.85, 0.05)
        acting[who].append({"from": a, "to": b, "mouth": [lo, hi]})


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


GLASS_ON = [False]
GL = {}


def shot(sid, at, camera, glass=None, **kw):
    """`glass`: a dict(lens, pos, tgt, dist) when the camera is the mirror's: the chrome pillar and the cool pane go in
    front of it by cue, on the cut; every real shot turns them off."""
    SH.append((sid, at, camera, kw))
    GL[sid] = glass
    glass_cue(at, glass)


def glass_cue(at, glass):
    """Turn the chrome pillar and the pane on in front of a glass camera (or off again after one) on the cut."""
    if glass:
        pos, tgt, lens = glass["pos"], glass["tgt"], glass["lens"]
        fx, fy = tgt[0] - pos[0], tgt[1] - pos[1]
        n = math.hypot(fx, fy)
        fx, fy = fx / n, fy / n
        dp = glass.get("dist", 1.0)
        hw = 6.75 * dp / lens
        pw = max(0.5, 2.0 * hw)
        lat = glass.get("fr", 0.45) * hw + pw / 2
        rx, ry = fy, -fx
        cue(at, "glass", on=1.0, px=round(pos[0] + fx * dp + rx * lat, 3), py=round(pos[1] + fy * dp + ry * lat, 3),
            pz=pos[2], yaw=round(math.atan2(fy, fx), 4), qx=round(pos[0] + fx * 0.45, 3),
            qy=round(pos[1] + fy * 0.45, 3), pw=round(pw, 3))
        GLASS_ON[0] = True
    elif GLASS_ON[0]:
        cue(at, "glass", on=0.0)
        GLASS_ON[0] = False


def glass_cam(tgt, lens, push=0.28, dy=0.0, cz=1.5, **kw):
    """The mirror's camera at (GCAM.x, GCAM.y + dy) looking at tgt, pushed in `push` m over the shot."""
    pos = [G.GCAM[0], G.GCAM[1] + dy, cz]
    keys = [[0, pos, list(tgt), lens]]
    glass = dict(pos=pos, tgt=tgt, lens=lens, **kw)
    if push:
        fx, fy = tgt[0] - pos[0], tgt[1] - pos[1]
        n = math.hypot(fx, fy)
        pos2 = [round(pos[0] + fx / n * push, 3), round(pos[1] + fy / n * push, 3), cz]
        keys.append([1, pos2, list(tgt), lens])
    return keys, glass


def gshot(sid, at, tgt, lens, push=0.28, dy=0.0, cz=1.5, hold=False, **kw):
    keys, glass = glass_cam(tgt, lens, push, dy, cz, **kw)
    shot(sid, at, keys, glass=glass, hold=hold)


ME = G.M
TX, TY = G.T
BX, BY = G.BENCH
K = (3.5, -0.9)                  # Mr. Kim facing the mirror (S04a)

# ----------------------------------------------------------------------------------------------- the cast at rest
for who in cast:
    if who == "me":
        continue
    key(who, 0, [0, 0, 0], yaw=0, expr="neutral", head=[0, 0], arms=[0, 0], side=[0, 0], hidden=True)
last["me"] = [ME[0], ME[1], 0.0]
cue(0, "board", v=0.0, flip=0.0)
cue(0, "glass", on=0.0)
cue(0, "sit", dre=1.0)
cue(0, "props", paint=0.0, bar=0.0, key=0.0)
SIT_Z = G.SIT_Z


def _pose(yaw, expr, kw):
    d = dict(yaw=yaw, expr=expr, head=[0, 0], arms=[0, 0], side=[0, 0])
    d.update(kw)
    return d


def me_at(at, who="me", yaw=-90, expr="neutral", **kw):
    cut(who, at, [ME[0], ME[1], 0.0], **_pose(yaw, expr, kw))


def glass_at(at, who, yaw=90, expr="neutral", pos=None, **kw):
    cut(who, at, [*(pos or (TX, TY)), 0.0], **_pose(yaw, expr, kw))


def dre_at(at, yaw, expr="neutral", **kw):
    cut("dre", at, [BX - 0.05, BY, SIT_Z], **_pose(yaw, expr, kw))


# ===== 01 the rule (L01 to L03)
show(0, "me")
me_at(0)
mouth("me", 0, "L01.1", 0.35)
shot("S01a", 0, cam(ME[0], ME[1], 1.3, 1.5, -90, 36, cz=1.35, push=(1.35, 1.3)))
show("L01.2", "me2")
glass_at("L01.2", "me2")
gshot("S01b", "L01.2", [TX, TY, 1.35], 26)
show("L02", "me2")
key("me2", "L02", [TX, TY, 0], yaw=90, arms=[12, 12])
key("me2", "L02+0.25", yaw=90, arms=[88, 88], blend=0.9)
cue("L02", "props", bar=1.0, bar_who="me2")
gshot("S02", "L02", [TX, TY, 1.1], 21, push=0.28)
show("L03", "wendell")
cut("wendell", "L03", [*G.WEN, 0.0], yaw=90, expr="smile", head=[0, 0], arms=[0, 0], side=[0, 0])
cue("L03", "props", bar=0.0)
cue("L03", "board", v=13.0, flip=1.0)
shot("S03", "L03", camp([3.0, -1.4, 1.55], [-4.6, 0.6, 1.4], 24, pos2=[2.6, -1.3, 1.55]))
key("wendell", "L03.2", yaw=90, expr="smile", head=[0, 5])

# ===== 02 the rule at work (L04 to L08)
cue("L04", "board", v=0.0, flip=0.0)
show("L04", "kim")
cut("kim", "L04", [K[0], K[1], 0.0], yaw=90, expr="neutral", head=[0, 0], arms=[0, 0], side=[0, 0])
shot("S04a", "L04", camp([0.7, -0.6, 1.6], [4.9, -1.0, 1.5], 28, pos2=[1.0, -0.65, 1.6]))
show("L04.1", "kim")
glass_at("L04.1", "kim", expr="laugh", arms=[82, 6])
cue("L04.1", "props", key=1.0, key_who="kim")
gshot("S04b", "L04.1", [TX, TY + 0.3, 1.3], 24, fr=0.7)
show("L05", "kim")
me_at("L05", "kim", yaw=-90, expr="stunned")
cue("L05", "props", key=0.0)
shot("S05", "L05", cam(ME[0], ME[1], 1.3, 1.5, -88, 36, cz=1.35, push=(1.3, 1.3)))
key("kim", "L05.1", expr="smile")
show("L06", "lena")
glass_at("L06", "lena", expr="smile")
cue("L06", "props", paint=1.0)
gshot("S06", "L06", [TX, TY, 1.3], 26, dy=0.1)
show("L07", "lena")
me_at("L07", "lena", yaw=-90, expr="smile")
cue("L07", "props", paint=0.0)
shot("S07", "L07", cam(ME[0], ME[1], 1.3, 1.5, -92, 36, cz=1.35, push=(1.3, 1.3)))
show("L08")
shot("S08", "L08", camp([2.0, 1.3, 0.95], [4.7, 0.0, 0.7], 24, pos2=[2.4, 1.1, 0.9], tgt2=[4.7, 0.0, 0.65]))

# ===== 03 my turn (L09 to L12)
show("L09", "me")
me_at("L09", "me", yaw=-90, expr="smile")
mouth("me", "L09", "L09>", 0.45)
shot("S09", "L09", cam(ME[0], ME[1], 1.3, 1.5, -90, 36, cz=1.35, push=(1.3, 1.3)))
show("L10", "dre")
dre_at("L10", -90, "smile")
cue("L10", "sit", dre=1.0)
shot("S10", "L10", cam(BX, BY, 0.95, 1.6, -90, 33, cz=1.25, push=(1.45, 0.95)))
show("L11", "me")
me_at("L11", "me", yaw=-90, expr="uneasy")
mouth("me", "L11", "L11>", 0.4)
shot("S11", "L11", cam(ME[0], ME[1], 1.3, 1.4, -94, 36, cz=1.35, push=(1.2, 1.3)))
show("L12", "me", "dre")
cut("me", "L12", [3.0, -1.0, 0.0], yaw=-90, expr="neutral", head=[0, 0], arms=[0, 0], side=[0, 0])
dre_at("L12", 90, "smile")
shot("S12a", "L12", camp([4.7, -1.2, 1.6], [BX, -1.5, 1.05], 22, pos2=[4.5, -1.2, 1.6]))
show("L12.1", "dre")
dre_at("L12.1", -90, "serious")
shot("S12b", "L12.1", cam(BX, BY, 1.0, 1.7, -90, 33, cz=1.2, push=(1.5, 1.0)))

# ===== 04 the first message (L13 to L20)
show("L13", "me")
me_at("L13", "me", yaw=-90, expr="neutral")
key("me", "L13", [ME[0], ME[1], 0.0], yaw=-90, head=[0, 0])
key("me", "L13.1", [ME[0], ME[1], 0.0], yaw=-35, head=[-25, 0], blend=0.55)
shot("S13", "L13", cam(ME[0], ME[1], 1.3, 1.5, -90, 36, cz=1.35, push=(1.35, 1.3)))
show("L14", "me2")
glass_at("L14", "me2", expr="neutral")
gshot("S14", "L14", [TX, TY, 1.35], 26, dy=-0.05)
show("P01", "me2")
show("L15", "me2")
key("me2", "L15", [TX, TY, 0], yaw=90, expr="serious", head=[0, 0])
key("me2", "L15.1", yaw=90, head=[0, -9], blend=0.6)
gshot("S15", "L15", [TX, TY, 1.4], 26, dy=0.05, push=0.28)
key("me2", "L16", yaw=90, head=[0, 0], expr="serious", blend=0.4)
big_mouth("me2", "L16.1", 5, 0.42)
gshot("S16a", "L16", [TX, TY, 1.38], 26, push=0.28)
shot_t = "L16.3"
gshot("S16b", shot_t, [TX, TY, 1.4], 36, push=0.28, dy=0.04)
glass_at("L17", "me2", expr="serious", pos=(3.2, G.GY - 1.4))
gshot("S17", "L17", [BX, G.GY - 0.9, 1.0], 11, push=0.0, dy=-0.9, hold=True, fr=0.93)
show("L18", "dre")
dre_at("L18", 90, "neutral")
shot("S18", "L18", camp([4.4, G.GY, 1.5], [BX, BY, 1.05], 30, pos2=[4.2, G.GY, 1.5]), hold=True)
show("L19", "none")
cue("L19", "board", v=14.0, flip=0.0)
gshot("S19", "L19", [-4.9, G.BOARD[1] + 0.35, 1.1], 44, push=0.0, dy=0.0, cz=1.75, dist=1.2, hold=True, fr=0.9)
show("L20", "me")
cue("L20", "board", v=0.0, flip=0.0)
me_at("L20", "me", yaw=-90, expr="stunned")
mouth("me", "L20", "L20>", 0.4)
shot("S20", "L20", cam(ME[0], ME[1], 1.3, 1.5, -88, 36, cz=1.35, push=(1.3, 1.3)))

# ===== 05 the second message (L21 to L26)
show("L21", "me")
cut("me", "L21", [4.0, G.GY, 0.0], yaw=90, expr="neutral", head=[0, 0], arms=[0, 0], side=[0, 0])
shot("S21", "L21", camp([-2.6, G.GY, 1.7], [4.0, G.GY, 1.35], 20, pos2=[-2.1, G.GY, 1.7]))
show("L22", "me2")
glass_at("L22", "me2", expr="neutral")
gshot("S22", "L22", [TX, TY, 1.35], 26, dy=-0.08)
key("me2", "L23", [TX, TY, 0], yaw=90, expr="sad", head=[0, 0], blend=0.5)
big_mouth("me2", "L23", 4, 0.4)
gshot("S23a", "L23", [TX, TY, 1.38], 26, push=0.28)
big_mouth("me2", "L23.1", 6, 0.4)
gshot("S23b", "L23.1", [TX, TY, 1.4], 36, push=0.28, dy=0.04)
key("me2", "L24", yaw=90, expr="sad", head=[0, 0])
big_mouth("me2", "L24", 2, 0.4)
gshot("S24", "L24", [TX, TY, 1.38], 30, push=0.28, dy=0.06)
cue("L25", "board", v=12.0, flip=0.0)
show("L25", "none")
gshot("S25", "L25", [-4.9, G.BOARD[1] + 0.35, 1.1], 44, push=0.0, dy=0.0, cz=1.75, dist=1.2, hold=True, fr=0.9)
show("L26", "me")
cue("L26", "board", v=0.0, flip=0.0)
me_at("L26", "me", yaw=-90, expr="scared", blink=False)
mouth("me", "L26", "L26>", 0.4)
shot("S26", "L26", cam(ME[0], ME[1], 1.3, 1.45, -92, 36, cz=1.35, push=(1.25, 1.3)))

# ===== 06 no answer (L27 to L31)
show("L27", "me")
cut("me", "L27", [2.6, -0.6, 0.0], **_pose(165, "uneasy", {"blink": False}))
mouth("me", "L27", "L27>", 0.4)
shot("S27", "L27", camp([3.4, 2.3, 1.45], [1.81, -1.37, 1.0], 20, pos2=[3.3, 2.1, 1.45]))
me_at("L28", "me", yaw=-90, expr="uneasy")
key("me", "L28.1", [ME[0], ME[1], 0.0], yaw=-90, expr="uneasy", head=[0, 4])
mouth("me", "L28", "L28>", 0.4)
shot("S28", "L28", cam(ME[0], ME[1], 1.3, 1.25, -90, 36, cz=1.35, push=(1.1, 1.3)))
show("L29", "me2")
glass_at("L29", "me2", expr="neutral", blink=False)
gshot("S29", "L29", [TX, TY, 1.35], 26, dy=0.08)
show("L30", "me")
me_at("L30", "me", yaw=-90, expr="scared")
mouth("me", "L30", "L30>", 0.4)
shot("S30", "L30", cam(ME[0], ME[1], 1.3, 1.5, -90, 36, cz=1.35, push=(1.3, 1.3)))
mouth("me", "L31", "L31>", 0.4)
shot("S31", "L31", cam(ME[0], ME[1], 1.3, 1.5, -90, 36, cz=1.35, push=(1.35, 1.3)))
key("me", "L31", [ME[0], ME[1], 0.0], yaw=-90, expr="scared")

# ----------------------------------------------------------------------------------------------- angle cuts
# A second angle of the same moment, from the middle of a shot: a real camera swings 10 degrees round its target, the
# mirror's camera slides 0.18 m along the glass (its pillar and pane are placed again for the new camera).
SPLITS = {"S01a": "L01.1", "S02": "L02.1", "S03": "L03.2", "S04b": "L04.2", "S05": "L05.1", "S06": "L06.1",
          "S07": "L07.1", "S09": "L09.2", "S10": "L10.1", "S11": "L11.1", "S12b": "L12.2", "S14": "P01",
          "S15": "L15.1", "S16a": "L16.2", "S20": "L20.1", "S21": "L21.1", "S26": "L26.1", "S27": "L27.1",
          "S28": "L28.2", "S30": "L30.1"}


def variant(sid, sign):
    sid0, at0, cam0, kw0 = next(x for x in SH if x[0] == sid)
    g = GL.get(sid)
    if g:
        dy = sign * 0.18
        pos = [g["pos"][0], round(g["pos"][1] + dy, 3), g["pos"][2]]
        tgt = [g["tgt"][0], g["tgt"][1], g["tgt"][2]]
        keys = [[0, pos, tgt, g["lens"]]]
        if len(cam0) > 1:
            fx, fy = tgt[0] - pos[0], tgt[1] - pos[1]
            n = math.hypot(fx, fy)
            keys.append([1, [round(pos[0] + fx / n * 0.28, 3), round(pos[1] + fy / n * 0.28, 3), pos[2]], tgt, g["lens"]])
        return keys, dict(g, pos=pos)
    out = []
    for k in cam0:
        t_ = k[2]
        a = sign * 10 * D2R
        dx_, dy_ = k[1][0] - t_[0], k[1][1] - t_[1]
        out.append([k[0], [round(t_[0] + dx_ * math.cos(a) - dy_ * math.sin(a), 3),
                           round(t_[1] + dx_ * math.sin(a) + dy_ * math.cos(a), 3), k[1][2]], t_, k[3]])
    return out, None


new_sh, flip = [], 1
for sid, at, camera, kw in SH:
    new_sh.append((sid, at, camera, kw))
    if sid in SPLITS:
        keys, g = variant(sid, flip)
        flip = -flip
        new_sh.append((sid + "b", SPLITS[sid], keys, {k: v for k, v in kw.items() if k != "hold"}))
        if g:
            glass_cue(SPLITS[sid], g)
SH[:] = new_sh

# ----------------------------------------------------------------------------------------------- finish
remap_all(cues)
for k_ in acting.values():
    remap_all(k_)
shots = []
for i, (sid, at, camera, kw) in enumerate(SH):
    s = {"id": sid, "cam": camera, "step": 2}
    if i:
        s["at"] = remap(at)
    s.update({k: v for k, v in kw.items() if not k.startswith("_") and k != "hold"})
    shots.append(s)
hold = [sid for sid, at, camera, kw in SH if kw.get("hold")] + ["S19", "S25"]

sfx = [
    {"at": "L04.1", "kind": "thud", "db": -24},          # a soft clank of plates
    {"at": "L06", "kind": "thud", "db": -24},
]
music = {
    "root": 52, "mode": "minor", "bpm": 112, "seed": 138,
    "sections": [
        {"at": 0, "voices": ["pulse", "pad"], "energy": 0.5},
        {"at": "L09", "voices": ["pulse", "pad"], "energy": 0.55},
        {"at": "L13", "voices": ["pulse"], "energy": 0.4},
        {"at": "L15", "voices": ["drone", "pad"], "energy": 0.4},
        {"at": "L21", "voices": ["drone", "pad"], "energy": 0.35},
    ],
}
sound = {
    "floor": "wood", "steps_db": -24,
    "ambience": [{"kind": "room", "from": 0, "to": "L20>", "lufs": -40},
                 {"kind": "hum", "from": "L15", "to": "L16>", "lufs": -38},
                 {"kind": "hum", "from": "L22", "to": "L24>", "lufs": -38}],
    "sfx": sfx,
    "music_drops": [{"from": "P01", "to": "P01>"}],
    "rev": REV,
}
remap_all(sfx)
remap_all(music["sections"])
remap_all(sound["ambience"])
remap_all(sound["music_drops"])
polish = {"reveal": ["L17.2", "L19", "L25"], "twist": "L25", "emph": ["L01.2", "L17.2", "L19.2", "L25"],
          "quiet": [], "hold": sorted(set(hold)), "sway": [x["id"] for x in shots if x["id"] not in set(hold)], "sway_amp": 0.005, "idle_scale": 2.0,
          "reframe_every": 0.5, "reframe_min": 0.9}
polish["emph"] = [remap(x) for x in polish["emph"]]
polish["reveal"] = [remap(x) for x in polish["reveal"]]
polish["twist"] = remap(polish["twist"])
story = {
    "slug": "ep138-tomorrow-mirror",
    "title": "The Gym Where You See TOMORROW",
    "made_for_kids": False,
    "premise": ("The gym mirror shows you tomorrow, so when my best friend asks for my savings tonight, tomorrow-me "
                "mouths 'don't say yes', and later, 'say yes tonight'."),
    "twist": ("Each warning's glass shows a date that isn't tomorrow, one two days ahead and one today, so I can't "
              "tell which day the mirror was really showing or which me to trust."),
    "world": ("One small bright gym: teal walls, an orange rubber floor, black racks and benches, a wall-to-wall mirror "
              "with a thick chrome edge, and a white flip-number date board on the back wall."),
    "voice": {"voice": "am_adam", "tempo": 1.03, "rate": 1.45},
    "key_color": "#3ff0e0",
    "gap": 0.15,
    "tail": 0.0,
    "fade_in": False,
    "fade_out": False,
    "rev": REV,
    "look": {"style": "closer", "fog": "#e4eef4", "fog_density": 0.001, "fog_start": 60.0, "sky": "#cfe6f2",
             "sky_strength": 1.0, "exposure": 0.0, "flash_safe": True, "polish": polish},
    "grade": {"shadows": [0.0, 0.0, 0.015], "highlights": [0.02, 0.01, -0.01], "saturation": 1.05, "contrast": 1.03,
              "vignette": 0.12, "bloom": 0.1, "grain": 0.008},
    "cast": cast,
    "lines": lines,
    "shots": shots,
    "acting": acting,
    "cues": cues,
    "fx": [],
    "music": music,
    "sound": sound,
    "set_moves": [],
    "framing_ok": ["S12a", "S03", "S03b"],
    "frames_ok": [],
    "staging_ok": [],
    "phonemes": {"Dre": "dɹˈA"},
    "homophones": {"12th": "twelfth"},
}
OUT.write_text(json.dumps(story, indent=1, ensure_ascii=False) + "\n")
print("wrote", OUT, f"({len(shots)} shots, {len(cues)} cues)")
