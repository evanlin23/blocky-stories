"""Writes ../story.json for ep93 "recipe card" (script.md, 2026-11-03). Run: python stories/ep93-recipe-card/generator/make_story.py

The words are in lines.json (every line of the script). The edit (shots, acting, cues) is in plan.py.
Coordinates: x east, y north (the window wall), z up. A character facing -y has yaw 0, +x 90, -x -90, +y 180.
"""
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
OUT = HERE.parent / "story.json"
REV = 2

orig_lines = json.loads((HERE / "lines.json").read_text())
lines, CHUNKMAP = [], {}
for ln in orig_lines:
    if "pause" in ln:
        lines.append(ln)
        continue
    out, mp = [], []
    for cap, spoken in ln["chunks"]:
        cw, sw = cap.split(), spoken.split()
        n = len(cw)
        k = 1 if n <= 3 else (2 if n <= 6 else 3)
        sizes = [n // k + (1 if i < n % k else 0) for i in range(k)]
        mp.append(len(out))
        i = 0
        for sz in sizes:
            out.append([" ".join(cw[i:i + sz]), " ".join(sw[i:i + sz])])
            i += sz
    CHUNKMAP[ln["id"]] = mp
    lines.append({**ln, "chunks": out})


def remap(ref):
    return ref   # plan.py uses the split chunk numbers of the timeline directly
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


import plan  # noqa: E402  (the edit)

cast = plan.cast
acting, cues, SH = plan.acting, plan.cues, plan.SH
for k_ in acting.values():
    remap_all(k_)
remap_all(cues)
shots = []
for i, (at, camera, hand, follow) in enumerate(SH):
    s = {"id": f"S{i + 1:03d}", "cam": camera, "step": 2}
    if i:
        s["at"] = remap(at)
    if hand is not None:
        s["hand"] = hand
    if follow:
        s["follow"] = follow
    shots.append(s)

sfx = [
    {"at": "L01.1", "kind": "click", "db": -16},             # a soft paper flick on "HANDWRITING"
    {"at": "L03", "kind": "whoosh", "db": -24},
    {"at": "L32", "kind": "creak", "db": -18, "dur": 1.2},
    {"at": "L35", "kind": "creak", "db": -20, "dur": 1.4},
    {"at": "L37", "kind": "creak", "db": -14, "dur": 0.9},   # the tin lid
    {"at": "L50.1", "kind": "click", "db": -16},             # one small drip
    {"at": "L52", "kind": "whoosh", "db": -22},
    {"at": "L46", "kind": "bell", "db": -20},
    {"at": "L34.2", "kind": "click", "db": -18},
    {"at": "L45.1", "kind": "click", "db": -18},
    {"at": "L24.3", "kind": "click", "db": -19},
    {"at": "L58", "kind": "click", "db": -19},
    {"at": "L66", "kind": "click", "db": -19},
    {"at": "L53.1", "kind": "creak", "db": -20, "dur": 0.9, "synth": True},
]
music = {
    "root": 53, "mode": "lydian", "bpm": 96, "seed": 93,
    "sections": [
        {"at": 0, "voices": ["piano", "pulse"], "energy": 0.45},
        {"at": "L32", "voices": ["piano", "pad"], "energy": 0.5},
        {"at": "L35", "voices": ["pulse"], "energy": 0.35},
        {"at": "L37", "voices": ["drone", "pulse"], "energy": 0.6},
        {"at": "L45", "voices": ["piano", "pad", "pulse"], "energy": 0.8},
        {"at": "L55", "voices": ["piano", "pad"], "energy": 0.55},
        {"at": "L67", "voices": ["piano", "pad", "pulse"], "energy": 0.5},
    ],
}
sound = {
    "floor": "wood", "steps_db": -24, "rev": REV,
    "ambience": [{"kind": "room", "from": 0, "to": "end", "lufs": -38}],
    "sfx": sfx,
    "music_drops": [{"from": "P01", "to": "P01>"}],
}
look = {"fog": "#ffd9a8", "fog_density": 0.006, "fog_start": 18.0, "sky": "#ffd2a0", "sky_strength": 0.9,
        "exposure": -0.3, "flash_safe": True, "style": "closer",
        "polish": {"emph": ["L01.3", "L12.3", "L45.1", "L62.0", "L65.1", "L68.3"], "reveal": ["L62", "L38"], "twist": "L52",
                   "quiet": [["L67", "L69"]], "hold": plan.HOLD}}
story = {
    "slug": "ep93-recipe-card",
    "title": "Grandma's Recipe Is In My HANDWRITING",
    "made_for_kids": False,
    "premise": ("In a town where the night you finally cook a recipe right its card flies off to whoever needs it most, "
                "my grandma's sixty-year-old soup card is in my handwriting, and I've never written it. So I copy it "
                "and cook it myself, all spring, until my own card starts tugging toward the window."),
    "twist": ("When I finally cook her soup right, my copy flies out the window and lands sixty years back in "
              "nineteen-year-old Grandma's soup pot, so she learned it from my card and I learned it from hers: "
              "nobody ever invented the soup."),
    "world": ("Grandma Nell's butter-yellow kitchen with robin's-egg blue cabinets, a copper pot, a bowl of lemons, "
              "a dented tin on a shelf and a framed old photo, in a pink-gold town at dusk."),
    "voice": {"voice": "am_adam", "tempo": 1.03, "rate": 1.45},
    "key_color": "#ffe14d",
    "gap": 0.12,
    "tail": 0.25,
    "fade_in": False,
    "look": look,
    "grade": {"shadows": [-0.01, 0.0, 0.03], "highlights": [0.03, 0.012, -0.02], "saturation": 1.28, "contrast": 1.05,
              "vignette": 0.15, "bloom": 0.22, "grain": 0.008, "red_line": 0.74},
    "phonemes": {},
    "cast": cast,
    "lines": lines,
    "shots": shots,
    "acting": acting,
    "cues": cues,
    "fx": [],
    "music": music,
    "sound": sound,
    "set_moves": plan.SET_MOVES,
    "clip_ok": plan.CLIP_OK,
}
remap_all(sfx)
remap_all(music["sections"])
remap_all(sound["music_drops"])
remap_all(sound["ambience"])
for key in ("emph", "reveal"):
    look["polish"][key] = [remap(x) for x in look["polish"][key]]
look["polish"]["twist"] = remap(look["polish"]["twist"])
look["polish"]["quiet"] = [[remap(a), remap(b)] for a, b in look["polish"]["quiet"]]
OUT.write_text(json.dumps(story, indent=1, ensure_ascii=False) + "\n")
print("wrote", OUT, f"({len(shots)} shots, {len(cues)} cues)")
