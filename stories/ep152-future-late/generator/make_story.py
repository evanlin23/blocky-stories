"""Writes ../story.json for ep152 "future late" (script.md, 2026-11-12, batch 15). Run: python stories/ep152-future-late/generator/make_story.py

The words are in lines.json; places are in ../layout.py (shared with set.py). A character facing -y has yaw 0,
+x 90, +y 180, -x -90. Cues are read by set.py's animate() (its header lists them).
One real set: Mom's kitchen at night (x -3.4..3.4), plus two daylight montage spots (x 60 beach towel, x 90 porch).
Nothing here blinks or glows; the clocks' hands step, the tag's numerals change on a line.
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
REV = 6
orig_lines = json.loads((HERE / "lines.json").read_text())
lines, CHUNKMAP = T.split_lines(orig_lines)
idx = next(i for i, l in enumerate(lines) if l["id"] == "L16")
lines.insert(idx, {"id": "P16", "pause": 0.5, "chunks": [["", ""]]})     # the 0.5 s music drop before the RING


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
X = {"neutral": "neutral", "uneasy": "nervous", "stunned": "shocked", "scared": "terrified", "smile": "delighted",
     "laugh": "crylaugh", "warm": "delighted", "sheepish": "nervous", "sad": "heartbroken"}


def person(skin, shirt, pants, shoes, hair, hair_c, features=(), hair_c2=None, eyes="round", sleeves="long", **kw):
    d = {"age": "adult", "skin": skin, "shirt": shirt, "pants": pants, "shoes": shoes, "sleeves": sleeves,
         "hair": hair, "hair_c": hair_c, "hat": "none", "face": {"eyes": eyes, "brows": True, "ink": "#1c120c"}}
    if features:
        d["features"] = list(features)
    if hair_c2:
        d["hair_c2"] = hair_c2
    d.update(kw)
    return d


cast = {
    # me, 30: a dark curly cloud, a short beard, glasses; an orange hoodie; height 1.08 so he reads as a grown man
    "me": person("#7a5238", "#f08a2a", "#3a4f7a", "#f2efe6", "curls", "#2a1a10", features=["beard", "glasses"],
                 hair_c2="#2a1c12", height=1.08),
    # Mom, 60: a big darker-gray bun with a gold band (the knot) and gold glasses, a teal knit cardigan
    "mom": person("#7a5238", "#2f8f8a", "#5a4a6a", "#4a3a30", "bigbun", "#8a8a9c", features=["glasses"], hair_c2="#c9a24a",
                  pattern="knit", pattern_c="#256f6b", eyes="lashes", height=0.95),
    # the cousin (beach): a loud pink swoop, sunburnt
    "cousin": person("#d4483a", "#d8d0c0", "#2f9fd0", "#e8d8b8", "swoop", "#ff4fa0", sleeves="none"),
    # the friend (porch): a green mohawk and a mustache
    "friend": person("#b98456", "#4a8a5a", "#3a4a63", "#5a4030", "mohawk", "#2a9d5c", features=["mustache"],
                     hair_c2="#d93a2a", sleeves="short"),
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


def mouth(who, a, b, amt=0.35):
    acting[who].append({"from": a, "to": b, "mouth": [amt, amt], "flap": True})


def cue(at, name, **kw):
    cues.append({"at": at, "name": name, **kw})


def C(tx, ty, tz, w, az, lens=34, cz=None, push=None):
    """A camera looking at (tx, ty, tz) from az degrees round from the south, showing about w metres across at the target.
    push=(w2, tz2): a second key. cz: the camera's height (default level with the target)."""
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


def P2(pos, tgt, lens=34, pos2=None, tgt2=None):
    k = [[0, list(pos), list(tgt), lens]]
    if pos2 or tgt2:
        k.append([1, list(pos2 or pos), list(tgt2 or tgt), lens])
    return k


def shot(sid, at, camera, **kw):
    SH.append((sid, at, camera, kw))


MX, MY = G.ME_SEAT
OX, OY = G.MOM_SEAT
ME = (MX, MY, -0.22)
MOM = (OX, OY, -0.22)
CX, CY, CZ = G.CLOCK
PX, PY, PZ = G.PHONE


def mecam(w=1.5, az=0, lens=34, dx=0.0, tz=1.3, cz=1.45, push=None):
    return C(MX + dx, MY, tz, w, az, lens, cz=cz, push=push)


def momcam(w=1.5, az=0, lens=34, dx=0.0, tz=1.3, cz=1.45, push=None):
    return C(OX + dx, OY, tz, w, az, lens, cz=cz, push=push)


def clkcam(w=1.7, tx=0.26, az=0, lens=34, tz=1.7, cz=1.5, push=None):
    """The big kitchen clock at the frame's left, my face beside it."""
    return C(tx, 3.0, tz, w, az, lens, cz=cz, push=push)


def phonecam(w=0.6, az=0, dx=0.0, cz=1.25, tz=0.8, lens=34, push=None):
    return C(PX + dx, PY, tz, w, az, lens, cz=cz, push=push)


# --------------------------------------------------------------------------------------------- the cast at rest
key("me", 0, ME, yaw=0, expr="neutral", head=[0, 0], arms=[12, 12], side=[0, 0], lean=0)
key("mom", 0, MOM, yaw=0, expr="uneasy", head=[0, 0], arms=[12, 12], side=[0, 0], lean=0)
key("cousin", 0, (G.COUSIN[0], G.COUSIN[1]), yaw=0, expr="sheepish", arms=[0, 0], side=[0, 0])
key("friend", 0, (G.FRIEND[0] - 0.3, G.FRIEND[1], 0.3), yaw=0, expr="laugh", arms=[0, 0], side=[0, 0])
cue(0, "sit", who="me", s=1.0)
cue(0, "sit", who="mom", s=1.0)
# the rule meter: "1" at once (the call still owed); the call timer from the tap; the big digit "0" when the call ends
cue(0, "timer", mode=0.0, s=0.0, big=1.0)
for ln, sec in (("L17", 0), ("L18", 9), ("L19", 20), ("L20", 31), ("L21", 41), ("L22", 49), ("L23", 57)):
    cue(ln, "timer", mode=1.0, s=float(sec), dur=0.4)
cue("L24", "timer", mode=0.0, s=57.0, big=0.0)
# the kitchen clocks (all ten minutes fast) and the tag's readout under the tag
cue(0, "clock", on=0.0, h=11.0, m=50.0)     # the tag shows only the "1" until L12; the wall clocks read 11:50 and never rewind
cue("L12", "clock", on=1.0, h=11.0, m=52.0)
cue("L13", "clock", on=1.0, h=11.0, m=55.0)
cue("L15", "clock", on=1.0, h=11.0, m=57.0)
cue("L16", "clock", on=1.0, h=11.0, m=58.0)
# the phone: dark glyph screen; buzzes at the RING; the call screen from the tap
cue(0, "phone", mode=0.0, buzz=0.0)
cue("L16.1", "phone", mode=0.0, buzz=1.0)
cue("L17", "phone", mode=1.0, buzz=0.0)
cue("L24", "phone", mode=0.0, buzz=0.0)
cue(0, "tap", p=0.0)
cue("L17+0.2", "tap", p=0.0)
cue("L17+0.7", "tap", p=1.0, dur=0.3)
cue("L17+1.2", "tap", p=0.0, dur=0.3)

# --------------------------------------------------------------------------------------------- 01 the rule (L01, L02)
S01A = ((0.3, -0.4, 1.3), (0.3, 3.0, 0.91), 20)
shot("S01a", 0, P2(*S01A, pos2=(0.3, -0.2, 1.3), tgt2=(0.3, 3.0, 0.91)))
key("me", 0, expr="uneasy", head=[0, 6])
mouth("me", 0, "L01.2", 0.35)
shot("S01b", "L01.2", P2((0.1, -0.2, 1.35), (-0.05, 1.2, 1.0), 34, pos2=(0.1, 0.0, 1.32), tgt2=(-0.05, 1.2, 1.0)))
mouth("me", "L01.2", "L01.4", 0.35)
shot("S01c", "L01.4", clkcam(1.9, tx=0.26, push=(1.7, 1.5)))
shot("S01d", "L01.5", mecam(1.35, 0, dx=-0.1, push=(1.15, 1.3)))
mouth("me", "L01.4", "L01>", 0.35)
# L03 "Tick."
shot("S03", "L03", momcam(1.45, 8, dx=0.0, push=(1.3, 1.3)))
key("mom", "L03", expr="uneasy", head=[0, 6])
key("me", "L04", expr="scared", head=[0, 0])
shot("S04", "L04", mecam(1.4, -6, dx=-0.05, push=(1.2, 1.3)))
mouth("me", "L04", "L04>", 0.35)

# --------------------------------------------------------------------------------------------- 02 the rule at work (L05, L06)
CXD, CYD = G.COUSIN
key("cousin", "L05", expr="sheepish")
shot("S05a", "L05", C(CXD, CYD, 1.35, 1.9, 8, 32, cz=1.5, push=(1.6, 1.35)))
shot("S05b", "L05.3", C(CXD + 0.05, CYD, 1.5, 0.95, 4, 34, cz=1.5))
FXD, FYD = G.FRIEND[0] - 0.3, G.FRIEND[1] + 0.0
key("friend", "L06", expr="laugh")
shot("S06a", "L06", C(FXD, FYD, 1.65, 1.9, -8, 32, cz=1.8, push=(1.6, 1.65)))
key("friend", "L06.3", arms=[0, 0], side=[0, 0])
shot("S06b", "L06.3", C(FXD + 0.4, FYD, 1.55, 1.6, -14, 34, cz=1.7))
key("friend", "L06.3+0.3", arms=[8, 55], blend=0.35, expr="laugh")
key("friend", "L06.3+0.9", arms=[0, 0], side=[0, 0], blend=0.4)

# --------------------------------------------------------------------------------------------- 03 Mom's kitchen of clocks (L07 to L10)
key("mom", "L07", expr="smile", head=[0, 0])
shot("S07a", "L07", momcam(1.55, 6, dx=0.2, push=(1.35, 1.3)))
shot("S07b", "L07.1", P2((3.2, 3.2, 1.95), (2.2, 3.7, 1.95), 24, pos2=(3.2, 3.2, 1.95), tgt2=(-1.4, 3.7, 1.95)))
key("me", "L08", expr="neutral", head=[0, -4], arms=[0, 12], side=[38, 0], blend=0.35)
shot("S08", "L08", P2((0.6, -0.8, 1.2), (0.2, 3.3, 1.2), 24, pos2=(0.5, -0.5, 1.2), tgt2=(0.2, 3.3, 1.2)))
key("me", "L09", expr="sheepish", head=[0, 6], arms=[12, 12], side=[0, 0], blend=0.35)
key("me", "L09.1", arms=[12, 62], side=[0, 22], blend=0.35)
key("me", "L09.1+0.7", arms=[12, 12], side=[0, 0], blend=0.4)
mouth("me", "L09", "L09>", 0.35)
shot("S09", "L09", mecam(1.45, -10, dx=-0.15, push=(1.25, 1.3)))
key("mom", "L10", expr="sheepish", head=[0, -3])
shot("S10", "L10", momcam(1.3, 4, dx=0.05, push=(1.1, 1.3)))
key("mom", "L11", expr="uneasy", head=[18, -14], blend=0.5)
shot("S11", "L11", momcam(1.4, -6, dx=0.2, push=(1.2, 1.3)))
key("me", "L11", expr="uneasy", head=[-6, -10], blend=0.5)

# --------------------------------------------------------------------------------------------- 04 the wait (L12 to L15)
shot("S12", "L12", clkcam(1.75, tx=0.4, push=(1.55, 1.5)))
key("me", "L12", expr="uneasy", head=[0, 0])
shot("S13", "L13", P2((1.2, -0.3, 1.9), (-0.4, 1.9, 1.25), 22, pos2=(1.1, -0.1, 1.88), tgt2=(-0.4, 1.9, 1.25)))
key("mom", "L14", expr="uneasy", head=[0, 0], arms=[12, 12], side=[0, 0])
key("me", "L14", expr="uneasy")
shot("S14a", "L14", momcam(1.7, 0, dx=0.2, push=(1.5, 1.3)))
shot("S14b", "L14.1", P2((0.04, 1.04, 1.72), (0.04, 1.5, 0.78), 24, pos2=(0.04, 1.11, 1.59), tgt2=(0.04, 1.5, 0.78)))
key("mom", "L15", expr="uneasy", blend=0.5)
key("me", "L15", expr="scared", blend=0.5)
shot("S15", "L15", mecam(1.3, 0, dx=-0.05, push=(1.1, 1.3)))
shot("S15d", "P16", P2((0.0, -1.7, 1.5), (0.0, 2.4, 2.0), 22, pos2=(0.0, -1.5, 1.5), tgt2=(0.0, 2.4, 2.0)))

# --------------------------------------------------------------------------------------------- 05 the call (L16 to L22)
shot("S16a", "L16", P2((0.0, -0.15, 1.25), (0.0, 0.7, 0.8), 30, pos2=(0.0, 0.05, 1.2), tgt2=(0.0, 0.7, 0.8)))
key("me", "L16.1+0.3", expr="stunned", head=[0, 0])
shot("S16b", "L16.1+0.3", mecam(1.3, 0, dx=-0.05, push=(1.1, 1.3)))
shot("S17", "L17", P2((0.35, -1.0, 1.25), (0.35, 2.6, 1.1), 20, pos2=(0.35, -0.8, 1.25), tgt2=(0.35, 2.6, 1.1)))
key("me", "L18", expr="stunned", head=[0, 6])
mouth("me", "L18", "L18>", 0.35)
shot("S18", "L18", P2((0.3, -0.8, 1.35), (0.4, 2.6, 1.15), 22, pos2=(0.3, -0.5, 1.35), tgt2=(0.4, 2.6, 1.15)))
key("mom", "L19", expr="stunned", head=[0, 0], arms=[12, 12], side=[0, 0])
key("mom", "L19.1", arms=[50, 12], side=[0, 0], blend=0.4)
shot("S19", "L19", momcam(1.9, 6, dx=0.1, tz=1.0, cz=1.2, push=(1.65, 1.0)))
key("me", "L20", expr="laugh", head=[0, -6])
mouth("me", "L20", "L20>", 0.4)
key("mom", "L20", arms=[12, 12], side=[0, 0], expr="smile", blend=0.5)
shot("S20", "L20", mecam(1.4, -8, dx=-0.1, push=(1.2, 1.3)))
key("me", "L21", expr="stunned", head=[0, 0], arms=[0, 12], side=[38, 0], blend=0.35)
shot("S21a", "L21", P2((1.0, -1.2, 1.2), (0.2, 3.3, 1.2), 24, pos2=(0.95, -0.9, 1.2), tgt2=(0.2, 3.3, 1.2)))
key("me", "L21.2", expr="stunned", arms=[12, 12], side=[0, 0], blend=0.3)
shot("S21b", "L21.2", mecam(1.2, 0, dx=-0.05, push=(1.0, 1.3)))
key("me", "L22", expr="laugh", head=[0, -8], blend=0.6)
mouth("me", "L22", "L22>", 0.4)
shot("S22", "L22", mecam(1.3, 6, dx=-0.1, push=(1.1, 1.3)))

# --------------------------------------------------------------------------------------------- 06 the advice and the reveal (L23 to L26)
shot("S23a", "L23", P2((1.2, -0.3, 1.9), (-0.4, 1.9, 1.25), 22, pos2=(1.1, -0.1, 1.88), tgt2=(-0.4, 1.9, 1.25)))
shot("S23b", "L23.3", momcam(1.35, 4, dx=0.1, push=(1.15, 1.3)))
key("mom", "L23.3", expr="warm", head=[0, 0])
key("me", "L24", expr="stunned", head=[0, 0], blend=0.5)
shot("S24", "L24", P2((0.9, -0.3, 1.4), (0.3, 3.3, 1.5), 22, pos2=(0.8, 0.1, 1.4), tgt2=(0.3, 3.3, 1.5)))
shot("S25", "L25", P2((1.1, -1.1, 1.5), (0.3, 3.3, 1.6), 22, pos2=(1.0, -0.8, 1.5), tgt2=(0.3, 3.3, 1.6)))
key("me", "L25.3", expr="warm", blend=0.4)
shot("S25b", "L25.3", mecam(1.2, 0, dx=-0.1, push=(1.0, 1.3)))
mouth("me", "L25.3", "L25>", 0.3)
key("me", "L26", expr="smile", head=[0, 0], blend=0.5)
shot("S26", "L26", P2((0.5, -1.9, 1.6), (0.5, 3.0, 1.4), 26, pos2=S01A[0], tgt2=S01A[1]))
cue("L26", "timer", mode=0.0, s=57.0, big=0.0)

# ----------------------------------------------------------------------------------------------- finish
remap_all(cues)
for k_ in acting.values():
    remap_all(k_)
shots, names = [], {}
for i, (sid, at, camera, kw) in enumerate(SH):
    s = {"id": sid, "cam": camera, "step": 2}
    if i:
        s["at"] = remap(at)
    s.update({k: v for k, v in kw.items() if not k.startswith("_")})
    shots.append(s)

sfx = [
    {"at": "L03", "kind": "click", "db": -22},
    {"at": "L12.1", "kind": "click", "db": -22},
    {"at": "L13.1", "kind": "click", "db": -22},
    {"at": "L15.1", "kind": "click", "db": -22},
    {"at": "L16.1", "kind": "knock", "pattern": [0, 0.12, 0.26], "tone": "soft", "db": -20},
    {"at": "L17+0.7", "kind": "click", "db": -20},
]
music = {
    "root": 50, "mode": "minor", "bpm": 92, "seed": 152,
    "sections": [
        {"at": 0, "voices": ["musicbox"], "energy": 0.3},
        {"at": "L05", "voices": ["musicbox", "pulse"], "energy": 0.36},
        {"at": "L11", "voices": ["pad"], "energy": 0.16},
        {"at": "L16", "voices": ["piano", "musicbox", "pulse"], "energy": 0.55, "mode": "major"},
        {"at": "L23", "voices": ["pad", "piano"], "energy": 0.3, "mode": "major"},
        {"at": "L26", "voices": ["musicbox"], "energy": 0.2, "mode": "major"},
    ],
}
sound = {
    "floor": "wood", "steps_db": -26,
    "sfx": sfx,
    "music_drops": [{"from": "P16", "to": "P16>", "keep": ["click"]}],
    "ambience": [{"kind": "room", "from": 0, "to": "end", "lufs": -44}],
    "rev": REV,
}
remap_all(sfx)
remap_all(music["sections"])
remap_all(sound["music_drops"])
polish = {"overlap": True, "turn_cap": 220, "punch_max": 4, "sharpen": 0.4, "bloom_thresh": 0.85, "talk": True,
          "reveal": [remap("L24"), remap("L25.3")], "twist": remap("L24"),
          "emph": [remap(x) for x in ["L01.5", "L12", "L16.1", "L21.2", "L23.3", "L25.3"]],
          "quiet": [[remap("L25"), remap("L25.2")]],
          "hold": ["S01a", "S08", "S14a", "S21a", "S25"], "music_duck_db": 11.0, "ones": "all"}
story = {
    "slug": "ep152-future-late",
    "title": "Everyone's Future Call Came By BREAKFAST 🕛",
    "made_for_kids": False,
    "premise": ("On your thirtieth birthday your future self phones you once, that day, and mine hadn't rung by 11:57 at night "
                "while my mom and I sat under her fourteen kitchen clocks."),
    "twist": ("Mom keeps every clock ten minutes fast because I'm always late, so the call came twelve minutes early by real "
              "time, and future me was calling from her kitchen, where the clocks are still set fast for me."),
    "world": ("Mom's bright yellow kitchen at night with a round table under fourteen wall clocks, then a sunny beach towel "
              "and a small blue porch for two quick jokes."),
    "voice": {"voice": "am_adam", "tempo": 1.03, "rate": 1.45},
    "key_color": "#ff6a4f",
    "gap": 0.15,
    "tail": 0.0,
    "fade_in": False,
    "fade_out": False,
    "rev": REV,
    "look": {"style": "v3", "fog": "#f4e8d4", "fog_density": 0.001, "fog_start": 60.0, "sky": "#ffe9c0",
             "sky_strength": 1.0, "exposure": 0.05, "flash_safe": True, "polish": polish},
    "grade": {"shadows": [0.0, 0.0, 0.02], "highlights": [0.03, 0.012, -0.02], "saturation": 1.06, "contrast": 1.03,
              "vignette": 0.12, "bloom": 0.12, "grain": 0.008},
    "hud": {"object": "tag", "at": [-0.5, 0.62], "size": 0.46},
    "asr_forgive": ["thirtieth", "eleven fifty-two", "eleven fifty-five", "eleven fifty-seven", "eleven fifty-eight",
                    "hadn't", "he's", "red", "his", "forty-eight", "tick", "future me", "buy", "buy the house"],
    "cast": cast,
    "lines": lines,
    "shots": shots,
    "acting": acting,
    "cues": cues,
    "fx": [],
    "music": music,
    "sound": sound,
    "set_moves": [],
    "frames_ok": ["S01b", "S11", "S15", "S16a", "S16b"],
    "staging_ok": [],
    "framing_ok": ["S07b", "S14b", "S25", "S25b"],
    "clip_ok": [],
}
OUT.write_text(json.dumps(story, indent=1, ensure_ascii=False) + "\n")
print("wrote", OUT, f"({len(shots)} shots, {len(cues)} cues)")
