"""Writes ../story.json for ep41-orchard-rows ("In this town, every footprint glows until the next sunrise").

Run from anywhere: python stories/ep41-orchard-rows/generator/make_story.py
The words are in lines.json (from script.md). Everything else is here: the cast, the shots and their cameras, the
acting, the cues set.py reads (time of day, trails of prints, the Rough One, the porch lamp, the blind, the door),
the effects, the score and the sound. Places are in ../geo.py.
"""
import importlib.util
import json
import math
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE.parent / "story.json"
_g = importlib.util.spec_from_file_location("orchard_geo", HERE.parent / "geo.py")
geo = importlib.util.module_from_spec(_g)
_g.loader.exec_module(geo)
O = lambda x, y, z=None: ([x, geo.OY + y] if z is None else [x, geo.OY + y, z])
OY = geo.OY
F = geo.FLOOR

lines = json.loads((HERE / "lines.json").read_text())
LOOP = 0.25
out_lines = []
for ln in lines:
    out_lines.append(ln)
    if ln["id"] == "L64":
        out_lines.append({"id": "P64", "pause": 1.45, "chunks": []})   # the bench seat, held, not narrated
out_lines.append({"id": "P03", "pause": LOOP, "chunks": []})
lines = out_lines
# the word check: these lines a touch slower so a swallowed word comes through
TEMPO = {"L05": 0.9, "L06": 0.92, "L56": 0.88, "L11": 0.85, "L13": 0.85, "L18": 0.92, "L48": 0.9, "L65": 0.85, "L66": 0.84}
for ln in lines:
    if ln["id"] in TEMPO:
        ln["tempo"] = TEMPO[ln["id"]]

PINK, BLUE, YEL, ORG, TEAL, VIO = "#ff8ec4", "#8fb8ff", "#ffe066", "#ff9a3c", "#4fe0c8", "#b48cff"
CORAL, LIME = "#ff6b6b", "#b6e84a"

FACE = {"eyes": "round", "brows": True}
cast = {
    "me": {"age": "adult", "skin": "#e8b894", "shirt": "#b8531f", "pattern": "plaid", "pattern_c": "#6e2a12",
           "collar": "#8f3f1a", "pants": "#2d3a52", "shoes": "#5a3a22", "sleeves": "long", "hair": "swoop",
           "hair_c": "#3a2418", "hat": "none", "face": {**FACE, "ink": "#1a1210"}, "glow": PINK},
    "nan": {"age": "adult", "skin": "#efc9aa", "shirt": "#d8cbad", "pattern": "knit", "pattern_c": "#bfae88",
            "collar": "#6a3a5c", "pants": "#6a3a5c", "shoes": "#8a6f4a", "sleeves": "long", "hair": "bun",
            "hair_c": "#cfd3da", "hat": "none", "width": 0.92,
            "body_width": 0.95, "face": {**FACE, "cheeks": "#e9a090"}, "glow": BLUE},
    "woman": {"age": "adult", "skin": "#d9a06f", "shirt": "#2f7a47", "collar": "#245f38", "pants": "#3a3f4a",
              "shoes": "#2a2220", "sleeves": "long", "hair": "long", "hair_c": "#5a3420", "hat": "none",
              "extras": ["coat"], "zip_c": "#1d4a2c", "face": {**FACE}, "glow": YEL},
    "pj": {"age": "adult", "skin": "#c68d62", "shirt": "#e8e4da", "pattern": "stripes", "pattern_c": "#6a85c4",
           "collar": "#e8e4da", "pants": "#e8e4da", "pants_pattern": "stripes", "pants_pattern_c": "#6a85c4",
           "shoes": "#5a4a3a", "sleeves": "long", "hair": "buzz", "hair_c": "#2a1d15", "hat": "none",
           "face": {**FACE, "bags": True}, "glow": ORG},
    "front": {"age": "adult", "skin": "#e3b690", "shirt": "#23272f", "pants": "#1b1e24", "shoes": "#111114",
              "sleeves": "long", "hair": "cap", "hair_c": "#1b1e24", "hat": "beanie", "hat_c": "#1b1e24",
              "extras": ["coat"], "zip_c": "#3a3f4a", "face": {**FACE}, "glow": TEAL},
    "follow": {"age": "adult", "skin": "#b07a52", "shirt": "#2c2531", "pants": "#1c1b22", "shoes": "#111114",
               "sleeves": "long", "hair": "buzz", "hair_c": "#16110e", "hat": "ballcap", "hat_c": "#2c2531",
               "extras": ["coat"], "zip_c": "#3a3f4a", "width": 1.06, "face": {**FACE}, "glow": VIO},
    "pass1": {"age": "adult", "skin": "#f0cfae", "shirt": "#7a8aa0", "pattern": "knit", "pattern_c": "#65748a",
              "collar": "#7a8aa0", "pants": "#5b4a3a", "shoes": "#2a2220", "sleeves": "long", "hair": "spiky",
              "hair_c": "#8a5a2a", "hat": "none", "face": {**FACE}, "glow": CORAL},
    "pass2": {"age": "adult", "skin": "#8a5636", "shirt": "#c7b9a0", "collar": "#b3a58c", "pants": "#3b4a5f",
              "shoes": "#1d1a18", "sleeves": "short", "hair": "cap", "hair_c": "#16110e", "hat": "none",
              "face": {**FACE}, "glow": LIME},
}
WHO = list(cast)

# ------------------------------------------------------------------------------------------ shots and acting
shots, cues, fx = [], [], []
acting = {w: [] for w in WHO}
last = {w: {"pos": [0, 0, -50]} for w in WHO}        # where each was left; hidden until placed
pending_end = {w: None for w in WHO}


def plus(ref, d):
    if isinstance(ref, (int, float)):
        return round(ref + d, 3)
    return f"{ref}{'+' if d >= 0 else '-'}{abs(d)}"


def cam(*keys, hand=0.012, follow=None, step=2):
    ks = []
    n = len(keys)
    for i, k in enumerate(keys):
        u = 0.0 if n == 1 else i / (n - 1)
        ks.append([u, list(k[0]), list(k[1]), k[2]] + ([k[3]] if len(k) > 3 else []))
    d = {"cam": ks, "hand": hand, "step": step}
    if follow:
        d["follow"] = follow
    return d


SHOT_ORDER = []


def shot(sid, at, camspec, acts=None, tod=None, **extra):
    """acts: {who: {"pos": start, "end": pos at the next cut (optional), ...key extras}}. Anyone not named is hidden."""
    orch = int(sid[1:]) >= 11

    def fix_pos(p):
        p = list(p)
        if orch and p[1] < 150:
            p[1] = round(p[1] + OY, 3)
        return p

    if orch:
        camspec = {**camspec, "cam": [[k[0], fix_pos(k[1]), fix_pos(k[2])] + k[3:] for k in camspec["cam"]]}
    s = {"id": sid, **camspec, **extra}
    if at is not None and at != 0:
        s["at"] = at
    shots.append(s)
    SHOT_ORDER.append((sid, at if at is not None else 0))
    acts = acts or {}
    anchor = at if at is not None else 0
    for w in WHO:
        a = acts.get(w)
        # close the previous walk exactly at this cut
        if pending_end[w] is not None:
            acting[w].append({"at": anchor, "pos": pending_end[w]})
            last[w] = {"pos": pending_end[w]}
            pending_end[w] = None
        elif last[w]["pos"][2:3] != [-50] or True:
            if acting[w]:
                acting[w].append({"at": anchor, "pos": last[w]["pos"]})
        if a is None:
            if not acting[w] or not acting[w][-1].get("hidden"):
                acting[w].append({"at": anchor, "pos": last[w]["pos"], "hidden": True, "blend": 0, "arms": [0, 0],
                                  "side": [0, 0], "head": [0, 0], "lean": 0, "tremble": 0, "yaw": 0})
            continue
        a = dict(a)
        pos = fix_pos(a.pop("pos"))
        end = a.pop("end", None)
        end = fix_pos(end) if end is not None else None
        key = {"at": anchor, "pos": pos, "hidden": False, "blend": 0, "arms": [0, 0], "side": [0, 0], "head": [0, 0],
               "lean": 0, "tremble": 0, "expr": "neutral", "yaw": 0, **a}
        acting[w].append(key)
        last[w] = {"pos": pos}
        if end is not None:
            pending_end[w] = end
    if tod:
        cues.append({"at": anchor, "name": "tod", "set": tod})


def cue(at, name, **kw):
    cues.append({"at": at, "name": name, **kw})


def trail(at, tid, color, lines_=None, kind="glow", strength=2.4, z=0.0, walker=None, pre=None, gap=0.62, lat=0.16,
          every=1, per_print=False, boost=None, offset=None, size=None, rise=0.3):
    c = {"at": at, "name": "trail", "id": tid, "color": color, "kind": kind, "strength": strength, "z": z,
         "gap": gap, "lat": lat, "every": every, "rise": rise}
    if lines_:
        c["lines"] = lines_
    if walker:
        c["walker"] = walker
    if pre:
        c["lines"] = pre
    if per_print:
        c["per_print"] = True
    if boost:
        c["boost"] = boost
    if offset:
        c["offset"] = offset
    if size:
        c["size"] = size
    cues.append(c)


def off(at, tid, dur=0.4):
    cues.append({"at": at, "name": "trail_off", "id": tid, "dur": dur})


def strength(at, tid, value, dur=0.6):
    cues.append({"at": at, "name": "trail_str", "id": tid, "value": value, "dur": dur})


def rough(at, pos, yaw=0.0, on=True, lights=1.0):
    cues.append({"at": at, "name": "rough", "on": on, "pos": pos, "yaw": yaw, "lights": lights})


def look(x, y):
    return [x, y]


# ============================================================================== TOWN (dusk, then night)
# S01 the hook: lit golden street, my face in frame, pink soles, three townsfolk with trails of their own.
CY = -7.0
shot("S01", 0, cam(([0.2, -10.2, 1.2], [0.2, -1.0, 1.15], 34), ([0.2, -10.0, 1.2], [0.2, -1.0, 1.15], 34), hand=0.006),
     {"me": {"pos": [0.1, -3.2], "end": [0.1, -4.6], "expr": "worried"},
      "woman": {"pos": [-2.7, 1.4], "end": [-2.7, -0.4]},
      "pass1": {"pos": [2.6, 3.0], "end": [2.6, 1.0]},
      "pass2": {"pos": [-1.0, 7.0], "end": [-1.0, 4.9]}}, tod="dusk")
trail(0, "t_me", PINK, pre=[[[0.1, -3.2], [0.1, 18]]], strength=3.0)
trail(0, "t_me_w", PINK, walker="me", strength=3.0)
trail(0, "t_wo", YEL, pre=[[[-2.7, 1.4], [-2.2, 17]]], strength=3.0)
trail(0, "t_wo_w", YEL, walker="woman", strength=3.0)
trail(0, "t_p1", CORAL, pre=[[[2.6, 3.0], [3.0, 16]]], strength=3.0)
trail(0, "t_p1_w", CORAL, walker="pass1", strength=3.0)
trail(0, "t_p2", LIME, pre=[[[-1.0, 7.0], [-1.0, 18]]], strength=3.0)
trail(0, "t_p2_w", LIME, walker="pass2", strength=3.0)

# S02 low across the cobbles: four trails crossing
shot("S02", "L02", cam(([-2.9, -2.6, 0.22], [0.9, 6.0, 0.0], 30), ([-2.7, -2.4, 0.24], [0.9, 6.0, 0.0], 30)), {}, tod="dusk")
trail("L02", "c_y", YEL, [[[-3.2, 14], [-1.2, 6], [1.4, -3.8]]], strength=3.2)
trail("L02", "c_o", ORG, [[[3.2, 12], [1.6, 5], [-1.4, -3.2]]], strength=3.2)
trail("L02", "c_t", TEAL, [[[0.2, 16], [-0.6, 6], [2.9, -3.0]]], strength=3.2)
trail("L02", "c_p", PINK, [[[-2.2, 10], [0.3, 3], [1.0, -3.8]]], strength=3.2)

# S03 night: the woman in the green coat, looking about, worried
shot("S03", "L03", cam(([0.4, -1.3, 1.45], [0.3, 4.0, 1.05], 40), ([0.7, -1.2, 1.5], [0.3, 4.0, 1.05], 40)),
     {"woman": {"pos": [0.9, 4.6], "end": [-0.2, 3.3], "yaw": 180, "expr": "worried", "head": [30, 0]}}, tod="night")
for t_ in ("t_me", "t_me_w", "t_wo", "t_wo_w", "t_p1", "t_p1_w", "t_p2", "t_p2_w", "c_y", "c_o", "c_t", "c_p"):
    off("L03", t_, 0.05)
trail("L03", "y_wander", YEL, [[[2.6, 9], [0.9, 6.0], [-0.6, 4.4], [0.9, 3.3], [-0.5, 2.6]]], strength=3.6)
# S04 her yellow trail runs back to a wooden bench, plain keys on it
shot("S04", "L03.2", cam(([0.9, 0.8, 0.95], [-3.4, 8.8, 0.45], 34), ([0.9, 1.0, 0.95], [-3.4, 8.8, 0.45], 34)), {})
trail("L03.2", "y_back", YEL, [[[0.9, 3.3], [-0.9, 5.5], [-2.6, 7.7], [-3.1, 8.6]]], strength=3.6)
cue("L03.2", "vis", show=["keys"])

# S05, S06 the townsman's kitchen (30, 0)
shot("S05", "L04", cam(([30.0, -1.9, 1.5], [30.9, 3.8, 1.25], 30), ([30.1, -1.8, 1.5], [30.9, 3.8, 1.25], 30)),
     {"pj": {"pos": [30.9, 3.6], "yaw": 180, "expr": "wide"}}, tod="night")
cue("L04", "fridge", on=1.0, dur=0.6)
cue("L04", "vis", hide=["keys"])
trail("L04", "o_kit", ORG, [[[27.4, 2.0], [29.4, 2.6], [30.9, 3.3]]], strength=4.0, z=0.01)
shot("S06", "L04.3", cam(([29.4, 2.3, 4.4], [29.4, 2.45, 0.0], 32), ([29.4, 2.3, 4.2], [29.4, 2.45, 0.0], 32)),
     {"pj": {"pos": [30.9, 3.6], "yaw": 180, "expr": "wide"}})

# S07 to S09 the garden path (60, 0): the follower steps into the front one's prints
shot("S07", "L05", cam(([57.8, -2.2, 1.5], [60.0, 0.6, 0.7], 34), ([57.9, -2.0, 1.5], [60.0, 1.0, 0.7], 34)),
     {"front": {"pos": [60.0, -0.2], "end": [60.0, 1.8]}, "follow": {"pos": [60.0, -1.44], "end": [60.0, 0.56]}}, tod="night")
trail("L05", "tg", TEAL, walker="front", strength=1.1, per_print=True,
      boost={"who": "follow", "factor": 2.0, "dur": 0.6, "radius": 0.5})
cue("L05", "pairlight", to=1.0, dur=0.3)
cue("L07", "pairlight", to=0.0, dur=0.6)
shot("S08", "L06", cam(([60.4, -4.2, 1.25], [60.0, 0.8, 0.2], 34), ([60.4, -3.9, 1.25], [60.0, 1.1, 0.2], 34)),
     {"front": {"pos": [60.0, 1.8], "end": [60.0, 3.3]}, "follow": {"pos": [60.0, 0.56], "end": [60.0, 2.06]}})
shot("S09", "L06.2", cam(([60.35, -6.2, 1.2], [60.0, 6.0, 0.8], 34), ([60.35, -5.8, 1.2], [60.0, 6.0, 0.8], 34)),
     {"front": {"pos": [60.0, 3.3], "end": [60.0, 6.5]}, "follow": {"pos": [60.0, 2.06], "end": [60.0, 5.26]}})
# S10 the street at sunrise, every trail fading over 2 s
shot("S10", "L07", cam(([1.0, -13.0, 2.4], [0.0, 6.0, 0.4], 30), ([0.6, -12.0, 2.2], [0.0, 6.0, 0.4], 30)), {}, tod="sunrise")
for i_, (c_, x_) in enumerate([(YEL, -2.2), (ORG, 2.2), (TEAL, -0.6), (PINK, 0.9), (CORAL, 3.4), (LIME, -3.4)]):
    trail("L07", f"s10_{i_}", c_, [[[x_ + 0.4, -6], [x_ - 0.5, 4], [x_ + 0.3, 16]]], strength=3.4)
    off("L07+0.4", f"s10_{i_}", 2.0)

# ============================================================================== THE ORCHARD (dusk)
ORCH_OLD = []
for x_, y0_, y1_ in [(5, 6, 60), (-5, 8, 54), (9, 10, 40), (-9, 12, 62), (13, 14, 50), (-13, 20, 58)]:
    ORCH_OLD.append([O(x_, y0_), O(x_, y1_)])
for y_, x0_, x1_ in [(18, -12, 12), (26, -10, 8), (34, -8, 12), (42, -12, 6), (50, -6, 12), (58, -12, 10)]:
    ORCH_OLD.append([O(x0_, y_), O(x1_, y_)])
ORCH_OLD.append([O(0, 6), O(5, 18), O(-5, 34), O(1, 42)])
ORCH_OLD.append([O(-9, 62), O(-1, 56), O(5, 50)])
MAIN_Y0, GAP = 2.6, 0.62
yk = lambda k: round(MAIN_Y0 + GAP * k, 3)
MAIN = [[O(0, MAIN_Y0), O(0, 66.0)]]

shot("S11", "L08", cam(([0.5, 6.8, 1.45], [0.0, 10.2, 1.4], 40), ([0.5, 6.9, 1.45], [0.0, 10.2, 1.4], 40), hand=0.006),
     {"me": {"pos": O(0.0, 9.6), "yaw": 0, "expr": "worried"}}, tod="dusk")
trail("L08", "old", PINK, ORCH_OLD, strength=2.4)
trail("L08", "main", PINK, MAIN, strength=2.8)
shot("S12", "L09", cam(([1.2, 5.0, 2.55], [0.0, 0.8, 2.3], 38), ([1.1, 5.0, 2.55], [0.0, 0.8, 2.3], 38)),
     {"nan": {"pos": O(0.0, 0.8, F), "yaw": 180, "arms": [10, 140], "expr": "grin"}})
cue("L09", "lamp", to=1.0, dur=0.3)
shot("S13", "L10", cam(([0.5, 9.0, 1.3], [0.0, 14.5, 1.15], 40), ([0.5, 9.2, 1.3], [0.0, 14.5, 1.15], 40)),
     {"me": {"pos": O(0.0, 18.0), "end": O(0.0, 14.4), "expr": "neutral"}})
cue("L10", "vis", show=["bag"])
cue("L11", "vis", hide=["bag"])
shot("S14", "L11", cam(([0.0, 2.0 + OY - OY, 24.0], [0.0, 36.0, 0.0], 24), ([0.0, 5.0, 25.0], [0.0, 38.0, 0.0], 24)), {})
shot("S15", "L12", cam(([0.1, 12.0, 0.3], [-0.5, 36.0, 0.2], 28), ([0.1, 14.0, 0.3], [-0.5, 38.0, 0.2], 28)), {})
shot("S16", "L13", cam(([1.4, -1.4, F + 1.4], [-0.7, -5.8, F + 0.6], 28), ([1.2, -1.6, F + 1.4], [-0.7, -5.8, F + 0.6], 28)),
     {"nan": {"pos": [-0.3, -6.0, F], "yaw": 150, "expr": "neutral"}})
NANK = [[[3.6, -4.4], [2.6, -5.4], [0.8, -6.0], [-0.3, -5.5]], [[-0.3, -5.5], [0.5, -3.2], [0.0, -0.9]],
        [[0.0, -0.9], [0.6, -3.0], [1.7, -4.2], [1.2, -5.2], [1.6, -6.2]], [[-1.6, -5.1], [-2.3, -1.4], [-1.0, -3.4]]]
trail("L13", "nan_k", BLUE, [[[x, geo.OY + y] for x, y in ln_] for ln_ in NANK], strength=2.6, z=F + 0.012)
shot("S17", "L13.2", cam(([2.6, 5.6, 1.25], [-0.4, 10.4, 0.9], 34), ([2.4, 5.8, 1.25], [-0.4, 10.4, 0.9], 34)), {})

# ============================================================================== FIRST DAWN
SQ1 = [[O(geo.LEFT, 68.0), O(geo.LEFT, 61.4)]]
shot("S18", "L14", cam(([0.6, 1.1, 2.6], [0.0, 60.0, 1.3], 30), ([0.6, 1.3, 2.6], [0.0, 60.0, 1.3], 30)), {}, tod="dawn")
rough("L14", O(geo.LEFT, 61.5), yaw=0, lights=0.6)
cue("L14", "lamp", to=0.35, dur=0.4)
trail("L14", "sq1", "#1d2a16", SQ1, kind="dark", gap=1.3, lat=0.32)
shot("S19", "L15", cam(([0.55, 62.2, 0.5], [-0.55, 65.0, 0.0], 28), ([0.55, 62.4, 0.5], [-0.55, 65.2, 0.0], 28)), {})
shot("S20", "L16", cam(([-0.4, 65.0, 4.0], [-0.4, 65.0, 0.0], 30), ([-0.4, 64.0, 3.6], [-0.4, 64.5, 0.0], 30)), {})
shot("S21", "L17", cam(([-0.6, 53.5, 0.35], [-0.6, 66.0, 0.3], 28), ([-0.6, 55.5, 0.35], [-0.6, 66.0, 0.3], 28)), {})
shot("S22", "L18", cam(([-1.1, 54.0, 0.55], [-1.1, 66.0, 0.9], 30), ([-1.1, 58.0, 0.55], [-1.1, 66.0, 0.9], 30)), {})
shot("S23", "L18.3", cam(([0.8, 49.0, 1.2], [-1.1, 62.0, 1.3], 55), ([0.8, 49.5, 1.2], [-1.1, 62.0, 1.3], 55)), {})
shot("S24", "L19", cam(([1.8, 36.0, 1.4], [-1.1, 61.6, 1.3], 100), ([1.8, 36.6, 1.4], [-1.1, 61.6, 1.3], 100)), {})
rough("L19", O(geo.LEFT, 61.5), yaw=0, lights=0.12)
shot("S25", "L20", cam(([-0.4, 47.0, 2.1], [-1.1, 61.2, 2.1], 90), ([-0.45, 47.6, 2.1], [-1.1, 61.2, 2.1], 90), hand=0.004), {})
rough("L20", O(geo.LEFT, 61.5), yaw=0, lights=0.15)
rough("L21", O(geo.LEFT, 61.5), yaw=0, lights=0.6)
shot("S26", "L21", cam(([0.5, 50.0, 1.4], [-1.1, 61.5, 1.5], 34), ([0.6, 50.4, 1.4], [-1.1, 61.5, 1.5], 34)), {})
cue("L21", "leaves", on=True, at_xy=O(geo.LEFT, 61.5))
shot("S27", "L22", cam(([-3.2, 10.5, 1.0], [-3.8, 15.5, 1.5], 34), ([-3.1, 10.6, 1.0], [-3.8, 15.5, 1.5], 34)),
     {"nan": {"pos": O(-3.8, 15.6), "yaw": 0, "arms": [140, 150], "head": [0, 25], "expr": "neutral"}})
cue("L22", "leaves", on=False, at_xy=O(geo.LEFT, 61.5))
cue("L22", "vis", show=["basket"])
shot("S28", "L23", cam(([0.3, -2.1, F + 0.95], [-0.75, -0.7, F + 0.15], 30), ([0.25, -2.0, F + 0.9], [-0.75, -0.7, F + 0.15], 30)), {})
cue("L23", "vis", show=["boots"])
off("L23", "nan_k", 0.05)

# ============================================================================== SECOND DAWN
shot("S29", "L24", cam(([0.6, 1.2, 2.5], [-1.1, 40.0, 1.2], 40), ([0.6, 1.4, 2.5], [-1.1, 40.0, 1.2], 40)), {}, tod="dawn")
trail("L24", "sq2", "#1d2a16", [[O(geo.LEFT, 60.1), O(geo.LEFT, 39.2)]], kind="dark", gap=1.3, lat=0.32)
rough("L24", O(geo.LEFT, 61.5), on=False)
shot("S30", "L25", cam(([0.9, 30.5, 1.4], [-1.1, 38.5, 1.5], 40), ([0.9, 31.0, 1.4], [-1.1, 38.5, 1.5], 40)), {})
rough("L25", O(geo.LEFT, 38.4), yaw=0, lights=1.0)
shot("S31", "L26", cam(([8.0, 25.5, 1.9], [2.5, 35.5, 1.9], 32), ([7.8, 25.8, 1.9], [2.5, 35.5, 1.9], 32)),
     {"me": {"pos": O(5.4, 31.2, 0.9), "yaw": 90, "arms": [160, 160], "expr": "neutral"}})
cue("L26", "vis", show=["ladder"])
shot("S32", "L26.3", cam(([0.5, 27.0, 1.75], [-1.1, 38.4, 2.0], 42), ([0.5, 27.2, 1.75], [-1.1, 38.4, 2.0], 42)),
     {"me": {"pos": O(1.5, 28.6, 0.9), "yaw": 90, "arms": [160, 160], "expr": "worried"}})

# ============================================================================== THIRD DAWN
shot("S33", "L27", cam(([-0.2, -2.4, F + 1.7], [-2.6, -0.8, F + 1.5], 34), ([-0.3, -2.3, F + 1.7], [-2.6, -0.8, F + 1.5], 34)),
     {"me": {"pos": [-2.6, -1.1, F], "yaw": 150, "arms": [150, 150]}}, tod="dawn")
cue("L27", "expo", ev=-0.5)
cue("L29.3", "expo", ev=-0.7)
cue("L30", "expo", ev=0.0)
cue("L27", "blind", to=1.0, dur=1.2)
cue("L27", "daywin", to=1.0, dur=1.2)
rough("L27", O(geo.LEFT, 38.4), on=False)
shot("S34", "L28", cam(([-2.6, 4.0, 3.8], [-2.6, 1.0, 0.1], 30), ([-2.6, 3.4, 3.4], [-2.6, 1.0, 0.1], 30)), {})
trail("L28", "sq3", "#1d2a16", [[O(geo.LEFT, 37.8), O(geo.LEFT, 12.0), O(-1.6, 6.0), O(-2.6, 1.5)]], kind="dark", gap=1.3, lat=0.32)
shot("S35", "L29", cam(([-2.6, -1.5, F + 1.5], [-2.6, 1.0, F + 1.4], 34), ([-2.6, -1.4, F + 1.5], [-2.6, 1.0, F + 1.35], 34), hand=0.004), {})
rough("L29", O(-2.6, 1.15), yaw=0)
shot("S36", "L29.3", cam(([0.3, -0.4, F + 1.7], [-2.6, -1.1, F + 1.55], 40), ([0.25, -0.4, F + 1.7], [-2.6, -1.1, F + 1.55], 40)),
     {"me": {"pos": [-2.6, -1.1, F], "yaw": 120, "arms": [0, 0], "expr": "terrified", "tremble": 1}})

# ============================================================================== THE NIGHT
shot("S37", "L30", cam(([4.5, 11.0, 1.7], [0.0, 0.0, 2.8], 30), ([4.2, 10.0, 1.7], [0.0, 0.0, 2.8], 30)), {}, tod="night")
rough("L30", O(geo.LEFT, 38.4), on=False)
cue("L30", "lamp", to=1.0, dur=0.4)
cue("L30", "daywin", to=0.0, dur=0.5)
off("L30", "sq1", 0.05)
shot("S38", "L31", cam(([-4.3, -0.4, F + 1.9], [-5.0, -3.0, F + 0.9], 36), ([-4.4, -0.5, F + 1.9], [-5.0, -3.0, F + 0.9], 36)),
     {"me": {"pos": [-5.0, -3.0, F + 0.1], "yaw": 180, "sit": True, "expr": "worried"}})
shot("S39", "L31.2", cam(([2.7, -2.2, F + 2.6], [4.0, -4.4, F + 0.5], 34), ([2.8, -2.3, F + 2.6], [4.0, -4.4, F + 0.5], 34)), {})
shot("S40", "L32", cam(([1.8, -6.6, F + 2.5], [1.5, -3.0, F + 0.0], 26), ([1.6, -6.4, F + 2.5], [1.5, -3.0, F + 0.0], 26)), {})
trail("L32", "nan_n", BLUE, [[[x, geo.OY + y] for x, y in [[3.5, -4.2], [2.6, -5.3], [1.4, -5.5], [0.6, -3.6], [0.0, -1.0]]]],
      strength=3.4, z=F + 0.012)
shot("S41", "L33", cam(([0.7, -1.7, F + 1.2], [0.0, -0.7, F + 0.0], 36), ([0.6, -1.6, F + 1.1], [0.0, -0.7, F + 0.0], 36)), {})
shot("S42", "L34", cam(([0.9, 4.5, F + 1.65], [0.0, 0.0, F + 1.6], 36), ([0.8, 4.2, F + 1.65], [0.0, 0.0, F + 1.6], 36)),
     {"me": {"pos": [0.0, -0.5, F], "yaw": 180, "expr": "worried"}})
cue("L34", "door", to=1.0, dur=0.9)
cue("L35", "expo", ev=-1.1)
cue("L36", "expo", ev=0.0)
shot("S43", "L35", cam(([1.8, 3.0, F + 1.5], [0.1, 0.0, F + 1.9], 34), ([1.7, 3.0, F + 1.5], [0.1, 0.0, F + 1.9], 34)),
     {"me": {"pos": [0.0, 0.3, F], "yaw": 180, "expr": "scared"}})
cue("L35", "lamp", to=0.15, dur=1.6)
RPOS = O(geo.LEFT + 0.05, 2.7)
shot("S44", "L36", cam(([0.35, -1.5, F + 1.45], [-1.0, 2.7, 2.35], 28), ([0.3, -1.3, F + 1.45], [-1.0, 2.7, 2.35], 28), hand=0.004),
     {})
rough("L36", RPOS, yaw=0)
shot("S45", "L37", cam(([8.0, 1.2, 2.5], [-0.5, 2.0, 2.0], 44), ([7.6, 1.3, 2.5], [-0.5, 2.0, 2.0], 44), hand=0.004),
     {"me": {"pos": [-0.35, 1.25, F], "yaw": 50, "head": [-40, 0], "expr": "scared", "tremble": 0.8}})
shot("S46", "L38", cam(([-1.15, 1.7, 2.3], [-1.3, 2.28, 2.28], 50), ([-1.2, 1.55, 2.3], [-1.3, 2.28, 2.28], 50), hand=0.003), {})
shot("S47", "L39", cam(([-0.1, 1.25, F + 1.7], [0.9, 14.0, 0.7], 28), ([-0.05, 1.25, F + 1.7], [0.9, 14.5, 0.7], 28)), {})
strength("L39", "main", 4.6, 0.6)
shot("S48", "L40", cam(([0.1, 5.5, 0.28], [0.0, 16.0, 0.05], 30), ([0.1, 7.5, 0.28], [0.0, 17.0, 0.05], 30)), {})
shot("S49", "L41", cam(([0.2, 10.2, 0.55], [0.0, yk(13), 0.0], 40), ([0.15, 10.4, 0.5], [0.0, yk(13), 0.0], 40)), {})
shot("S50", "L42", cam(([0.6, 3.6, 0.35], [0.0, 5.3, 0.06], 42), ([0.65, 3.9, 0.35], [0.0, 6.2, 0.06], 42)),
     {"me": {"pos": [0.0, 2.6, 0.0], "end": [0.0, 6.6], "expr": "scared"}})
trail("L42", "step50", PINK, [[O(0, yk(1)), O(0, yk(9))]], strength=4.6, per_print=True,
      boost={"who": "me", "factor": 1.5, "dur": 0.6, "radius": 0.5})
# the chase
shot("S51", "L43", cam(([0.9, 19.3, 1.6], [0.0, 22.1, 1.55], 40), ([0.9, 19.5, 1.6], [0.0, 22.1, 1.55], 40)),
     {"me": {"pos": O(0.0, 22.0), "yaw": 150, "head": [-130, 0], "expr": "scared"}})
shot("S52", "L43.3", cam(([0.4, 22.5, 1.6], [-1.1, 14.0, 1.9], 40), ([0.4, 22.0, 1.6], [-1.1, 14.0, 1.9], 40)), {})
rough("L43.3", O(geo.LEFT, 14.2), yaw=180)
shot("S53", "L44", cam(([0.9, 43.3, 1.6], [0.0, 46.1, 1.55], 40), ([0.9, 43.5, 1.6], [0.0, 46.1, 1.55], 40)),
     {"me": {"pos": O(0.0, 46.0), "yaw": 150, "head": [-130, 0], "expr": "terrified"}})
rough("L44", O(geo.LEFT, 14.2), on=False)
shot("S54", "L44.3", cam(([0.6, 46.0, 1.6], [-1.1, 38.8, 2.0], 45), ([0.6, 45.5, 1.6], [-1.1, 38.8, 2.0], 45)), {})
rough("L44.3", O(geo.LEFT, 38.9), yaw=180)
shot("S55", "L45", cam(([-0.6, 33.0, 5.2], [-0.6, 32.0, 0.0], 30), ([-0.6, 32.0, 4.6], [-0.6, 31.0, 0.0], 30)), {})
rough("L45", O(geo.LEFT, 38.9), on=False)
shot("S56", "L46", cam(([0.4, -2.3, 1.3], [0.0, 2.0, 1.0], 34), ([0.4, -2.3, 1.3], [0.0, 2.0, 1.0], 34), follow="me"),
     {"me": {"pos": O(0.0, 50.6), "end": O(0.0, 52.9), "yaw": 180, "expr": "terrified", "run": True}})
shot("S57", "L47", cam(([0.4, 54.0, 0.4], [0.0, 69.0, 0.9], 30), ([0.4, 56.0, 0.4], [0.0, 69.0, 0.9], 30)), {})
shot("S58", "L48", cam(([2.0, 66.4, 1.3], [0.0, 69.4, 0.7], 30), ([1.95, 66.6, 1.3], [0.0, 69.4, 0.7], 30)), {})
# the bench: Nan sits, slippers in the grass
shot("S59", "L49", cam(([0.9, 66.0, 1.0], [0.1, 69.5, 0.85], 32), ([0.85, 66.2, 1.0], [0.1, 69.5, 0.85], 32)),
     {"nan": {"pos": O(0.35, BENCH := geo.BENCH_Y - 0.05), "yaw": 0, "sit": True, "expr": "neutral"}})
shot("S60", "L50", cam(([0.55, 67.2, 1.35], [0.3, 69.5, 1.3], 40), ([0.5, 67.3, 1.35], [0.3, 69.5, 1.3], 40)),
     {"nan": {"pos": O(0.35, geo.BENCH_Y - 0.05), "yaw": 0, "sit": True, "expr": "soft"}})
shot("S61", "L51", cam(([0.0, 30.0, 6.0], [0.0, 31.0, 0.0], 30), ([0.0, 31.0, 5.6], [0.0, 31.5, 0.0], 30)), {})
# a past night, silvery: I walk my old paths asleep, inside my own prints; Nan follows inside them
shot("S62", "L52", cam(([1.9, 16.2, 1.3], [0.0, yk(30), 0.9], 36), ([1.9, 16.6, 1.3], [0.0, yk(31), 0.9], 36)),
     {"me": {"pos": O(0.0, yk(27)), "end": O(0.0, yk(27) + 1.9), "yaw": 180, "expr": "shut", "arms": [0, 0]}}, tod="silver")
trail("L52", "pastpink", PINK, [[O(0, yk(28)), O(0, yk(47))]], strength=2.4, per_print=True,
      boost={"who": "me", "factor": 2.2, "dur": 0.6, "radius": 0.5})
shot("S63", "L53", cam(([1.1, yk(31) - 1.6, 0.55], [0.0, yk(31), 0.05], 40), ([1.1, yk(31) - 1.4, 0.55], [0.0, yk(32), 0.05], 40)),
     {"me": {"pos": O(0.0, yk(27) + 1.9), "end": O(0.0, yk(27) + 3.3), "yaw": 180, "expr": "shut"}})
shot("S64", "L54", cam(([0.9, 16.2, 1.5], [0.0, yk(27) + 4.2, 0.8], 30), ([0.9, 16.8, 1.5], [0.0, yk(27) + 4.6, 0.8], 30)),
     {"me": {"pos": O(0.0, yk(27) + 4.2), "end": O(0.0, yk(27) + 5.4), "yaw": 180, "expr": "shut"},
      "nan": {"pos": O(0.0, yk(27) + 1.6), "end": O(0.0, yk(27) + 2.8), "yaw": 180, "expr": "neutral"}})
shot("S65", "L54.3", cam(([1.0, 72.6, 1.45], [0.0, 55.0, 0.6], 34), ([0.9, 72.4, 1.45], [0.0, 55.0, 0.6], 34)),
     {"nan": {"pos": O(0.35, geo.BENCH_Y - 0.05), "yaw": 0, "sit": True, "expr": "soft"},
      "me": {"pos": O(0.0, 56.0), "end": O(0.0, 49.5), "yaw": 0, "expr": "shut"}})
trail("L54.3", "pastwalk", PINK, walker="me", strength=3.0, lat=0.16)
off("L55", "pastwalk", 0.05)
off("L55", "pastpink", 0.05)
# back on the bench, now
shot("S66", "L55", cam(([0.0, 66.0, 1.1], [0.0, 69.5, 0.95], 28), ([0.0, 66.1, 1.1], [0.0, 69.5, 0.95], 28)),
     {"nan": {"pos": O(0.45, geo.BENCH_Y - 0.05), "yaw": 0, "sit": True, "expr": "neutral"},
      "me": {"pos": O(-0.45, geo.BENCH_Y - 0.05), "yaw": 0, "sit": True, "expr": "worried"}}, tod="night")
shot("S67", "L56", cam(([-0.4, 68.8, 1.2], [-1.1, 50.0, 1.2], 32), ([-0.4, 68.8, 1.2], [-1.1, 48.0, 1.2], 32)), {})
shot("S68", "L57", cam(([0.65, 67.4, 1.35], [0.45, 69.5, 1.3], 40), ([0.6, 67.5, 1.35], [0.45, 69.5, 1.3], 40)),
     {"nan": {"pos": O(0.45, geo.BENCH_Y - 0.05), "yaw": 0, "sit": True, "expr": "smirk"}})
shot("S69", "L58", cam(([0.1, 62.6, 1.15], [0.0, 67.2, 0.95], 34), ([0.1, 63.0, 1.15], [0.0, 67.2, 0.95], 34)),
     {"nan": {"pos": O(0.55, 67.6), "end": O(0.55, 66.4), "yaw": 0, "arms": [0, 0], "expr": "soft"},
      "me": {"pos": O(-0.55, 67.6), "end": O(-0.55, 66.4), "yaw": 0, "expr": "soft"}})
trail("L58", "wp", PINK, walker="me", strength=5.0, lat=0.16)
trail("L58", "wb", BLUE, walker="nan", strength=5.0, lat=0.14)
cue("L58-0.4", "pairlight", to=1.0, dur=0.8)
cue("L58", "lamp", to=0.6, dur=1.5)
shot("S70", "L59", cam(([0.0, 69.5, 0.45], [0.0, 62.0, 0.1], 30), ([0.0, 68.7, 0.45], [0.0, 62.0, 0.1], 30)),
     {"nan": {"pos": O(0.55, 66.4), "end": O(0.55, 64.8), "yaw": 0}, "me": {"pos": O(-0.55, 66.4), "end": O(-0.55, 64.8), "yaw": 0}})
off("L61", "wp", 0.05)
off("L61", "wb", 0.05)
shot("S71", "L60", cam(([2.7, 0.9, 1.9], [0.0, 3.0, 1.0], 34), ([2.7, 1.2, 1.9], [0.0, 2.6, 1.0], 34)),
     {"nan": {"pos": [0.35, OY + 4.0, 0.0], "end": [0.35, OY + 1.2, F], "yaw": 180, "arms": [0, 35], "expr": "soft"},
      "me": {"pos": [-0.3, OY + 4.0, 0.0], "end": [-0.3, OY + 1.2, F], "yaw": 180, "arms": [0, 0], "side": [0, 0]}})
shot("S72", "L61", cam(([0.3, -0.4, F + 1.7], [-2.6, -1.1, F + 1.55], 40), ([0.25, -0.4, F + 1.7], [-2.6, -1.1, F + 1.55], 40)),
     {"me": {"pos": [-2.6, -1.1, F], "yaw": 120, "expr": "soft"}}, tod="sunrise")
cue("L61", "daywin", to=0.5, dur=0.5)
cue("L61", "expo", ev=-0.8)
shot("S73", "L62", cam(([0.0, 1.3, 2.7], [0.0, 60.0, 0.8], 30), ([0.0, 1.5, 2.7], [0.0, 60.0, 0.8], 30)), {})
trail("L62", "fp", PINK, [[O(-0.55, 66.4), O(-0.55, 2.8)]], strength=3.4)
trail("L62", "fb", BLUE, [[O(0.55, 66.4), O(0.55, 2.8)]], strength=3.4)
shot("S74", "L63", cam(([0.2, 9.5, 0.55], [0.0, 12.0, 0.0], 40), ([0.2, 9.8, 0.5], [0.0, 12.0, 0.0], 40)), {})
shot("S75", "L64", cam(([-0.2, 57.0, 3.2], [-0.9, 68.6, 0.4], 38), ([-0.2, 57.5, 3.0], [-0.9, 68.6, 0.4], 38)), {})
shot("S76", "L64.2", cam(([0.0, 68.5, 1.55], [0.0, 69.5, 0.5], 36), ([0.0, 68.6, 1.5], [0.0, 69.5, 0.5], 36), hand=0.003), {})
shot("S77", "L65", cam(([3.9, 1.4, 2.55], [0.0, 0.75, 2.3], 32), ([3.7, 1.45, 2.55], [0.0, 0.75, 2.3], 32)),
     {"nan": {"pos": [0.35, OY + 0.75, F], "yaw": 100, "expr": "soft", "arms": [0, 0]},
      "me": {"pos": [-0.35, OY + 0.75, F], "yaw": 80, "expr": "soft"}})
cue("L65", "vis", show=["mugs"])
shot("S78", "L66.1", cam(([4.0, 3.2, 1.3], [0.0, 1.5, 0.8], 34), ([4.0, 3.3, 1.25], [0.0, 1.9, 0.6], 34), hand=0.004),
     {"me": {"pos": [-0.3, OY + 1.05, F], "end": [-0.3, OY + 2.0, 0.3], "yaw": 180},
      "nan": {"pos": [0.35, OY + 1.05, F], "end": [0.35, OY + 2.0, 0.3], "yaw": 180}})

for w_ in WHO:
    if pending_end[w_] is not None:
        acting[w_].append({"at": "end", "pos": pending_end[w_]})

# ------------------------------------------------------------------------------------------ the score and sound
music = {"root": 43, "mode": "dorian", "bpm": 76, "seed": 41, "sections": [
    {"at": 0, "voices": ["drone", "pulse", "piano"], "energy": 0.42},
    {"at": "L08", "voices": ["drone", "pad", "piano"], "energy": 0.36},
    {"at": "L14", "voices": ["drone", "pad", "pulse"], "energy": 0.4},
    {"at": "L24", "voices": ["drone", "pad", "pulse", "piano"], "energy": 0.5},
    {"at": "L30", "voices": ["drone", "choir"], "energy": 0.55},
    {"at": "L36", "voices": ["drone", "choir"], "energy": 0.4},
    {"at": "L42", "voices": ["drone", "pulse", "choir"], "energy": 0.6},
    {"at": "L47", "voices": ["drone", "pad"], "energy": 0.4},
    {"at": "L52", "voices": ["pad", "piano"], "energy": 0.3},
    {"at": "L57", "voices": ["pad", "piano", "pulse"], "energy": 0.45, "mode": "major", "root": 43},
    {"at": "L65", "voices": ["pad", "piano"], "energy": 0.35}]}
sound = {"floor": "grass", "steps_db": -20,
         "ambience": [{"kind": "wind", "from": 0, "to": "L08", "lufs": -40},
                      {"kind": "crickets", "from": "L03", "to": "L07", "lufs": -38},
                      {"kind": "wind", "from": "L14", "to": "end", "lufs": -36},
                      {"kind": "hum", "from": "L30", "to": "L36", "lufs": -40},
                      {"kind": "hum", "from": "L36", "to": "L42", "lufs": -46}],
         "sfx": [{"at": "L04", "kind": "click", "db": -16},
                 {"at": "L22.3", "kind": "thud", "db": -24},
                 {"at": "L27", "kind": "creak", "db": -22, "dur": 1.2},
                 {"at": "L34", "kind": "door", "db": -16},
                 {"at": "L36", "kind": "sting", "db": -10},
                 {"at": "L43.3", "kind": "riser", "db": -24, "dur": 1.0},
                 {"at": "L44.3", "kind": "riser", "db": -22, "dur": 1.0},
                 {"at": "P64", "kind": "bell", "db": -24},
                 {"at": "L66.3", "kind": "glide", "db": -18, "dur": 1.0}],
         "music_drops": [{"from": "L36-0.6", "to": "L36.1", "keep": ["sting"]},
                         {"from": "L44-0.6", "to": "L44.1"}]}

story = {
    "slug": "ep41-orchard-rows",
    "title": "In this town, every footprint glows until sunrise",
    "made_for_kids": False,
    "premise": "In this town every footprint glows in its owner's colour until the next sunrise. Back in my grandmother's "
               "orchard for harvest week, my old pink paths still glow in every row, though everyone else's prints fade at "
               "dawn. Each dawn a new trail of huge square prints that do not glow runs beside my path and ends a little "
               "nearer the house, where something built from far too few blocks stands still all day.",
    "twist": "The prints that never fade are my own doing. Every night since I moved to town I have sleepwalked back to the "
             "orchard and down my old rows, stepping inside my own prints so they never go out, and Nan follows my glow and "
             "watches it home. Tonight is the first time I come out to her awake, and I still walk them every night.",
    "world": "A small farm town at harvest week: a cobbled dusk street, a townsman's kitchen, and an apple orchard of seven "
             "long rows in fog behind a whitewashed farmhouse, with a bench at the end of the far row.",
    "voice": {"voice": "am_adam", "tempo": 1.03, "rate": 1.45},
    "key_color": PINK,
    "caption": {"ink": "#10131a", "stroke_add": 2, "shadow": 0.8},
    "key_stroke": 2,
    "gap": 0.12,
    "tail": 0,
    "look": {"fog": "#8a98a6", "fog_density": 0.028, "fog_start": 6.0, "sky": "#8a98a6", "sky_strength": 0.8,
             "exposure": 0.0, "flash_safe": True},
    "grade": {"shadows": [-0.01, 0.0, 0.04], "highlights": [0.03, 0.01, -0.02], "saturation": 1.0, "contrast": 1.06,
              "vignette": 0.34, "bloom": 0.42, "grain": 0.012, "red_line": 0.78},
    "phonemes": {"Theirs": "ðˈɛɹz"},
    "cast": cast,
    "lines": lines,
    "shots": shots,
    "acting": acting,
    "cues": cues,
    "fx": fx,
    "music": music,
    "sound": sound,
}
OUT.write_text(json.dumps(story, indent=1, ensure_ascii=False))
print(f"wrote {OUT}: {len(shots)} shots, {len(lines)} lines, {len(cues)} cues")
