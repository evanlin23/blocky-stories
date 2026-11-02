"""Writes ../story.json for ep52 "Ferry crossing" (script by the writer, 2026-11-02).

Run from anywhere: python stories/ep52-ferry-crossing/generator/make_story.py
The words are in lines.json next to this file. Everything else is here: the cast, the shots and their cameras, the
acting, the cues set.py reads, the score and the sound. Places are set.py's metres (see its docstring).
yaw 0 faces -y, yaw 90 faces +x, yaw 180 faces +y. A head yaw of +90 turns the face toward the body's left.
"""
import json
import math
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE.parent / "story.json"
lines = json.loads((HERE / "lines.json").read_text())

F, X = 1000.0, 300.0
ME_SEAT = [F + 1.7, 4.75, 3.87]
GR_SEAT = [F + 1.7, 3.25, 3.91]
SH_SEAT = [F + 1.7, 4.75, 3.87]

PAUSES = {"L26": ("P01", 0.6), "L44": ("P02", 0.7)}
HOLDS = {"L08": 0.5, "L14": 0.45, "L17": 0.45, "L20": 0.45, "L24b": 0.5, "L28": 0.45, "L33": 0.45, "L39": 0.5,
         "L43": 0.4, "L48": 0.4, "L52": 0.4, "L56": 0.4, "L59": 0.45, "L62": 0.4, "L65": 0.5, "L66": 0.45, "L31": 0.4, "L36": 0.4, "L55": 0.4}
EXTRA = {"id": "L24b", "who": "narrator", "chunks": [["Every EVENING,", "Every evening,"], ["I end up", "I end up"],
                                                      ["a little CLOSER.", "a little closer."]]}
full = []
for ln in lines:
    if ln["id"] in HOLDS:
        ln["gap"] = HOLDS[ln["id"]]
    full.append(ln)
    if ln["id"] == "L24":
        EXTRA["gap"] = HOLDS["L24b"]
        full.append(EXTRA)
    if ln["id"] in PAUSES:
        pid, dur = PAUSES[ln["id"]]
        full.append({"id": pid, "pause": dur, "chunks": []})
full.append({"id": "P03", "pause": 0.25, "chunks": []})
lines = full
TEMPO = {"L12": 1.0, "L68": 0.7, "L20": 0.9, "L13": 1.0, "L02": 0.9, "L45": 0.9}
for _l in lines:
    if _l["id"] in TEMPO:
        _l["tempo"] = TEMPO[_l["id"]]


def split_chunks(ln):
    out = []
    for cap, sp in ln["chunks"]:
        cw, sw = cap.split(" "), sp.split(" ")
        while len(cw) > 3 and len(cw) == len(sw):
            k = 3 if len(cw) >= 6 else (len(cw) + 1) // 2
            out.append([" ".join(cw[:k]), " ".join(sw[:k])])
            cw, sw = cw[k:], sw[k:]
        out.append([" ".join(cw), " ".join(sw)])
    ln["chunks"] = out


for _ln in lines:
    split_chunks(_ln)


def spoken(lid, k, text):
    for ln in lines:
        if ln["id"] == lid:
            ln["chunks"][k][1] = text


def person(skin, shirt, pants, hair, hair_c, **kw):
    d = {"age": "adult", "skin": skin, "shirt": shirt, "pattern": "solid", "collar": None, "pants": pants,
         "shoes": "#25262b", "sleeves": "long", "hair": hair, "hair_c": hair_c, "hat": "none",
         "face": {"eyes": "round", "brows": True, "ink": "#161012"}}
    d.update(kw)
    return d


cast = {
    "me": person("#e2b48f", "#2a3550", "#32384a", "swoop", "#14110f", extras=["coat", "hooddown", "scarf"],
                 extra_c="#8a8f94", zip_c="#6a6e72"),
    "gran": person("#e9c9a8", "#8a6f9a", "#5a4a62", "bun", "#f1efea", pattern="knit", pattern_c="#6e557f",
                   collar="#a58bb4", height=0.93, shoes="#3a3030"),
    "glove_woman": person("#d9a98a", "#2f8f4a", "#2a2d33", "long", "#4a3322", extras=["coat", "hooddown"],
                          face={"eyes": "lashes", "brows": True, "ink": "#161012"}),
    "umbrella_man": person("#dcb08f", "#7a5a3a", "#3a3a3a", "cap", "#6e6a64", pattern="plaid", pattern_c="#5a3f26",
                           hat="ballcap", hat_c="#6a5238", height=1.02,
                           face={"eyes": "tired", "brows": True, "ink": "#1c1613"}),
    "jumper_man": person("#d9a07c", "#9a9fa6", "#3d4a63", "spiky", "#3a2a1c"),
    "kite_woman": person("#c98e6a", "#e8c020", "#3a3f4a", "long", "#6a4a2a", extras=["coat"], height=0.97,
                         face={"eyes": "lashes", "brows": True, "ink": "#161012"}),
    "pass1": person("#e0b08c", "#4a5560", "#2e3238", "cap", "#2a2a2a", extras=["coat"]),
    "pass2": person("#b88562", "#5e6b45", "#38362e", "buzz", "#8a8a88", extras=["coat"], height=0.96),
}
CHARS = list(cast)


def c(*keys):
    return [list(k) for k in keys]


def still(loc, tgt, lens):
    return c([0, loc, tgt, lens])


def move(a, b, lens):
    return c([0, a[0], a[1], lens], [1, b[0], b[1], lens])


SHOTS = []


def shot(at, note, cam, who=None, step=2):
    SHOTS.append({"at": at, "what": note, "cam": cam, "who": who or {}, "step": step})


def P(pos, **kw):
    return {"pos": pos, **kw}


# ------------------------------------------------------------------------------------------------ 01 the rule
shot(0, "bright low wide up the slipway: glove woman and umbrella man walking to camera",
     c([0, [0.9, 2.6, 1.2], [-0.1, -3.5, 1.0], 26], [1, [0.9, 2.4, 1.2], [-0.1, -3.5, 1.0], 26]),
     {"glove_woman": P([-0.5, -3.0], walk=[("L01>", [-0.4, 0.2])]),
      "umbrella_man": P([0.9, -4.6], walk=[("L01>", [0.9, -0.6])])})
shot("L02", "low: the glove hopping up after the raincoat hem",
     c([0, [0.9, 2.9, 0.3], [-0.4, -1.0, 0.2], 30], [1, [0.9, 2.7, 0.3], [-0.4, -1.0, 0.2], 30]),
     {"glove_woman": P([-0.5, -4.6], walk=[("L02>", [-0.45, 0.2])])})
shot("L03", "side tracking: umbrella man",
     c([0, [-2.5, -3.2, 1.1], [0.4, -3.2, 1.0], 28], [1, [-2.5, 2.6, 1.1], [0.4, 2.6, 1.0], 28]),
     {"umbrella_man": P([0.4, -3.2], walk=[("L03>", [0.4, 2.6])])})
shot("L04", "inside the ticket hut: the empty shelf",
     c([0, [700.4, -1.2, 1.3], [700, 1.4, 1.2], 24], [1, [700.2, -1.0, 1.3], [700, 1.4, 1.2], 24]))
shot("L05", "the jumper man at the bin",
     still([148.6, 9.2, 1.5], [150.6, 5.8, 1.2], 26),
     {"jumper_man": P([150.95, 5.45], yaw=-140)})
shot("L05.3", "he wakes up wearing it",
     still([600.0, -1.9, 1.35], [600, 0.95, 1.15], 26),
     {"jumper_man": P([600.0, 0.95, 0.18], yaw=0, sit=True, expr="wide")})
shot("L06", "a kite tumbling over grey sand", still([900, 2, 1.2], [903, 16, 2.2], 22))
shot("L06.3", "the kite woman at her gate, the kite on the roof",
     still([798.8, -6.4, 1.4], [800, 2.5, 2.6], 22),
     {"kite_woman": P([800, -3.6], yaw=180, head=[0, -28])})
shot("L07", "the dog alone on the harbour front", still([0, -1.2, 0.85], [0, 3.5, 0.4], 30))
shot("L08", "the dog up the gangway among legs", still([-2.2, -12.6, 0.4], [0.1, -16.8, 0.4], 24),
     {"pass1": P([-0.8, -13.6, 0.0], walk=[("L08+0.5", [-0.8, -15.3, 0.0]), ("L08+1.6", [-0.8, -18.5, 0.9]),
                                          ("L08+2.6", [-0.8, -22, 0.9])]),
      "pass2": P([0.9, -13.0, 0.0], walk=[("L08+0.8", [0.9, -15.3, 0.0]), ("L08+1.9", [0.9, -18.5, 0.9]),
                                         ("L08+2.8", [0.9, -22, 0.9])])})
shot("L08.2", "the dog on an island doorstep", still([305.4, -5.2, 0.7], [308.9, -3.1, 0.5], 28))

# ------------------------------------------------------------------------------------------------ 02 the glove
shot("L09", "me among the passengers, a thing hopping behind each, nothing behind me",
     still([0.2, 2.7, 1.3], [0.3, -3.5, 0.9], 26),
     {"me": P([0.3, -0.6], yaw=180),
      "pass1": P([-1.5, -0.8], walk=[("L09>", [-1.3, -6.0])]),
      "pass2": P([2.0, -1.8], walk=[("L09>", [2.2, -7.0])]),
      "glove_woman": P([-0.9, -2.8], walk=[("L09>", [-0.8, -8.0])]),
      "umbrella_man": P([1.3, -3.6], walk=[("L09>", [1.3, -9.0])])})
shot("L10", "the bin: a glove drops in", still([152.4, 4.4, 1.5], [150, 6.6, 1.0], 26))
shot("L11", "me walking away, looking back, worried", still([148.2, 4.5, 1.4], [153.0, 5.6, 1.3], 26),
     {"me": P([151.6, 5.3], expr="worried", head=[150, 0], walk=[("L11>", [154.6, 5.3])])})
shot("L12", "the call: Gran pulling on a glove, my hat on the hook",
     still([400.1, -1.9, 1.38], [400.1, 0.4, 1.35], 28),
     {"gran": P([399.85, 0.4], yaw=0, expr="soft", arms=[0, 80])})
shot("L13", "close on the glove with the hole",
     still([400.32, -1.05, 1.1], [400.32, -0.22, 1.1], 28),
     {"gran": P([399.85, 0.4], yaw=0, expr="soft", arms=[0, 80])})
shot("L14", "me at the table, worried", still([200.0, -1.9, 1.25], [200.5, 0.1, 1.0], 26),
     {"me": P([199.9, 0.1, -0.03], yaw=90, sit=True, expr="worried")})
shot("L15", "the island across the water", still([0, -9, 1.4], [-6, -108, 9], 20))
shot("L16", "years ago: Gran and me on the window bench in summer light",
     still([F + 5.8, 4.0, 5.2], [F + 1.7, 4.0, 5.0], 20),
     {"gran": P(GR_SEAT, yaw=90, sit=True, expr="soft"), "me": P(ME_SEAT, yaw=90, sit=True, expr="soft")})
shot("L16.4", "the empty bench today", still([F - 0.2, 2.2, 5.2], [F + 1.7, 4.0, 4.9], 26))
shot("L17", "my flat window at dusk, the island a dark line",
     still([200.9, -0.1, 1.55], [200, -2.7, 1.4], 24), {"me": P([200.0, -1.75], yaw=0)})

# ------------------------------------------------------------------------------------------------ 03 the evenings
shot("L18", "the chair empty, the door ajar", still([201.6, -1.6, 1.4], [199.4, 0.9, 0.9], 22))
shot("L19", "Monday: me at the water's edge", still([-0.7, -19.7, 1.35], [0.2, -16.4, 1.3], 28),
     {"me": P([0.2, -16.4, -0.23], yaw=0, expr="worried")})
shot("L20", "high wide: the slipway and the ferry's lights", still([-2.5, 5.5, 4.8], [12, -60, 0.6], 19))
shot("L21", "Tuesday: me on the window bench, scared", still([F + 0.9, 6.9, 5.3], [F + 1.7, 4.75, 5.1], 24),
     {"me": P(ME_SEAT, yaw=90, sit=True, expr="scared", head=[80, 0])})
shot("L22", "the empty seat beside me", still([F + 3.0, 3.25, 5.0], [F + 1.7, 3.25, 4.5], 28))
shot("L23", "the cushion sinks", still([F + 3.0, 2.5, 4.7], [F + 1.7, 3.25, 4.4], 30))
shot("L23.2", "me tipping toward it", still([F + 0.9, 6.9, 5.4], [F + 1.7, 4.75, 5.0], 26),
     {"me": P(ME_SEAT, yaw=90, sit=True, expr="scared", head=[0, 10], roll=10)})
shot("L24", "Wednesday: halfway up Gran's lane", still([X + 0.9, 11.2, 1.45], [X, 20, 1.5], 24),
     {"me": P([X, 15.0], expr="worried", head=[150, 0], walk=[("L24>", [X, 16.0])])})

# ------------------------------------------------------------------------------------------------ 04 the door
shot("L25", "Thursday: me at the green door", still([X - 2.1, 32.2, 1.5], [X + 0.1, 34.0, 1.45], 22),
     {"me": P([X - 0.1, 33.6], yaw=-50, expr="scared")})
shot("L26", "the door a hand's width open", still([X, 31.6, 1.45], [X, 36.0, 1.3], 24))
shot("L27", "her glasses on the mat", still([X - 0.3, 32.9, 0.3], [X, 34.35, 0.06], 36))
shot("L28", "her bed, made", still([X + 2.2, 36.2, 1.5], [X + 3.6, 38.4, 0.7], 22))
shot("L28.2", "the empty coat hook", still([X + 0.9, 36.9, 1.4], [X - 1.1, 36.9, 1.35], 24))
shot("L29", "the glasses into my pocket", still([X - 0.5, 32.6, 1.05], [X, 33.5, 0.95], 36),
     {"me": P([X, 33.6], yaw=0)})
shot("L30", "down the hall to the back door",
     c([0, [X, 36.0, 1.5], [X, 43.3, 1.3], 22], [1, [X, 40.0, 1.5], [X, 43.3, 1.3], 22]))
shot("L31", "the room full of hooks", still([X, 43.0, 1.5], [X, 46.5, 1.35], 13))
shot("L32", "a pan along the gloves",
     c([0, [X - 2.8, 45.2, 1.5], [X - 2.8, 46.8, 1.4], 20], [1, [X + 0.4, 45.2, 1.5], [X + 0.4, 46.8, 1.4], 20]))
shot("L32.1", "key rings rattling", still([X + 1.2, 45.7, 1.65], [X + 1.2, 46.8, 1.62], 30))
shot("L33", "my bike", still([X + 1.2, 44.3, 1.0], [X + 3.4, 45.4, 0.6], 24))
shot("L34", "the striped hat, me in the doorway", still([X - 1.6, 45.5, 1.6], [X - 0.4, 43.2, 1.5], 26),
     {"me": P([X, 43.0], yaw=180, expr="scared")})

# ------------------------------------------------------------------------------------------------ 05 the call
shot("L35", "the phone buzzes among the gloves", still([X - 0.5, 43.8, 1.25], [X - 0.6, 44.6, 0.8], 36))
shot("L36", "the call: Gran squinting on a dark doorstep", still([500.0, -1.9, 1.35], [500.0, 0.4, 1.3], 28),
     {"gran": P([500.0, 0.4], yaw=0, expr="squeeze")})
shot("L37", "this morning: Gran small on the slipway", still([-3.6, -11.5, 1.3], [0.4, -5.0, 1.2], 26),
     {"gran": P([0.4, -6.2], yaw=180)})
shot("L38", "me in the back room, worried", still([X - 0.1, 43.7, 1.5], [X, 45.4, 1.4], 24),
     {"me": P([X, 45.4], yaw=0, expr="worried")})
shot("L39", "the ferry's lights far out, alone", still([3.0, 4.5, 3.8], [18, -80, 1.8], 19))
shot("L40", "Gran nods", still([500.0, -1.9, 1.35], [500.0, 0.4, 1.3], 28),
     {"gran": P([500.0, 0.4], yaw=0, expr="squeeze", head=[0, 8])})
shot("L40.3", "the glasses through my pocket", still([X - 0.4, 44.3, 0.95], [X - 0.1, 45.35, 0.9], 36),
     {"me": P([X, 45.4], yaw=0)})
shot("L41", "the late boat over: me walking aboard",
     c([0, [X - 3.0, -8.0, 1.3], [X, -11.0, 1.0], 22], [1, [X - 3.0, -11.0, 1.3], [X, -15.5, 1.2], 22]),
     {"me": P([X, -10.2, 0.0], walk=[("L41+1.0", [X, -13.3, 0.0]), ("L41+2.1", [X, -16.5, 0.9])])})
shot("L42", "the car deck: looking for her", still([F + 0.0, -6.8, 1.7], [F, -3.0, 1.5], 24),
     {"me": P([F + 0.05, -3.2, 0.9], yaw=180, expr="worried", head=[25, 0]),
      "pass1": P([F - 2.2, -2.8, 0.9], yaw=180), "pass2": P([F + 2.3, -3.4, 0.9], yaw=180)})

# ------------------------------------------------------------------------------------------------ 06 the Shrug
shot("L43", "up the stair to the lounge door", still([F - 2.3, -4.2, 1.5], [F - 2.3, 0.4, 4.6], 22))
shot("L44", "Gran at the window, an orange edge beside her",
     still([F - 1.2, 1.1, 5.5], [F + 1.7, 3.5, 5.2], 28),
     {"gran": P(GR_SEAT, yaw=90, sit=True, expr="neutral")})
shot("L45", "the Shrug in my seat, clearly lit", still([F + 4.3, 5.7, 5.4], [F + 1.7, 4.75, 5.15], 24),
     {"gran": P(GR_SEAT, yaw=90, sit=True, expr="neutral")})
shot("L46", "side-on: shoulders level with its eyes", still([F + 4.0, 7.0, 5.2], [F + 1.7, 4.75, 5.0], 24),
     {"gran": P(GR_SEAT, yaw=90, sit=True, expr="neutral")})
shot("L47", "close: the eyes between the humps", still([F + 3.3, 5.3, 5.3], [F + 1.7, 4.75, 5.3], 30),
     {"gran": P(GR_SEAT, yaw=90, sit=True, expr="neutral")})
shot("L48", "Gran squinting, looking out", still([F + 4.6, 2.8, 5.3], [F + 1.7, 3.2, 5.3], 34),
     {"gran": P(GR_SEAT, yaw=90, sit=True, expr="squeeze")})
shot("L48.2", "two-shot from the aisle", still([F + 5.6, 4.0, 5.3], [F + 1.7, 4.0, 5.1], 17),
     {"gran": P(GR_SEAT, yaw=90, sit=True, expr="squeeze")})
shot("L49", "the humps lowering", still([F + 3.6, 5.5, 5.25], [F + 1.7, 4.75, 5.05], 28),
     {"gran": P(GR_SEAT, yaw=90, sit=True, expr="squeeze")})
shot("L50", "the full face", still([F + 3.0, 5.2, 5.1], [F + 1.7, 4.75, 5.05], 30),
     {"gran": P(GR_SEAT, yaw=90, sit=True, expr="squeeze")})
shot("L51", "the head turns to Gran", still([F + 4.0, 6.2, 5.2], [F + 1.7, 4.4, 5.05], 26),
     {"gran": P(GR_SEAT, yaw=90, sit=True, expr="squeeze")})
shot("L51.2", "leaning in, side-on", still([F + 5.6, 4.0, 5.3], [F + 1.7, 4.0, 5.1], 17),
     {"gran": P(GR_SEAT, yaw=90, sit=True, expr="squeeze")})

# ------------------------------------------------------------------------------------------------ 07 where things belong
shot("L52", "me in the aisle: I get it", still([F + 2.4, 7.2, 5.3], [F - 0.3, 3.3, 5.0], 26),
     {"gran": P(GR_SEAT, yaw=90, sit=True, expr="squeeze"),
      "me": P([F - 0.3, 3.3, 3.92], yaw=150, expr="scared")})
shot("L53", "the glove on Gran's hand", still([400.32, -1.05, 1.1], [400.32, -0.22, 1.1], 28),
     {"gran": P([399.85, 0.4], yaw=0, expr="soft", arms=[0, 80])})
shot("L54", "the dog by its blue door", still([305.4, -5.2, 0.7], [308.9, -3.1, 0.5], 28))
shot("L55", "the hooks and the striped hat", still([X - 1.6, 45.5, 1.6], [X - 0.4, 43.2, 1.5], 26))
shot("L56", "the hop-dots under my feet", still([1.3, 1.0, 0.55], [0.15, -3.2, 0.05], 26),
     {"me": P([0.3, -0.6], yaw=180)})
shot("L57", "me taking a breath", still([F + 2.4, 7.2, 5.3], [F - 0.3, 3.3, 5.0], 26),
     {"gran": P(GR_SEAT, yaw=90, sit=True, expr="squeeze"),
      "me": P([F - 0.3, 3.3, 3.92], yaw=150, expr="neutral")})
shot("L58", "my feet up the aisle", still([F + 0.2, 0.9, 4.2], [F + 0.9, 3.6, 4.15], 28),
     {"gran": P(GR_SEAT, yaw=90, sit=True, expr="squeeze"),
      "me": P([F + 0.5, 2.0, 3.92], walk=[("L58+1.4", [F + 0.7, 4.0, 3.92])])})
shot("L58.2", "I sit in my old seat", still([F + 4.5, 4.0, 5.2], [F + 1.7, 4.0, 5.0], 22),
     {"gran": P(GR_SEAT, yaw=90, sit=True, expr="neutral"), "me": P(ME_SEAT, yaw=90, sit=True, expr="neutral")})
shot("L59", "the dent fading out of the cushion", still([F + 2.8, 5.6, 4.55], [F + 1.7, 5.2, 4.4], 32),
     {"gran": P(GR_SEAT, yaw=90, sit=True, expr="neutral"), "me": P(ME_SEAT, yaw=90, sit=True, expr="neutral")})

# ------------------------------------------------------------------------------------------------ 08 home
GR_ME = {"gran": P(GR_SEAT, yaw=90, sit=True, expr="neutral")}
shot("L60", "the glasses held out", still([F + 4.2, 4.2, 5.2], [F + 1.9, 4.0, 4.95], 28),
     {"gran": P(GR_SEAT, yaw=90, sit=True, expr="neutral"),
      "me": P(ME_SEAT, yaw=90, sit=True, expr="soft", arms=[75, 75], head=[-60, 0])})
shot("L61", "her whole face lights up", still([F + 4.0, 3.25, 5.35], [F + 1.7, 3.25, 5.3], 28),
     {"gran": P(GR_SEAT, yaw=90, sit=True, expr="grin"), "me": P(ME_SEAT, yaw=90, sit=True, expr="soft")})
shot("L62", "the glove held out", still([F + 4.0, 3.9, 5.1], [F + 2.1, 3.7, 4.95], 32),
     {"gran": P(GR_SEAT, yaw=90, sit=True, expr="grin", arms=[0, 60]),
      "me": P(ME_SEAT, yaw=90, sit=True, expr="soft", head=[-40, 0])})
shot("L63", "two-shot, soft, the glove on my hand", still([F + 5.6, 4.0, 5.25], [F + 1.7, 4.0, 5.0], 20),
     {"gran": P(GR_SEAT, yaw=90, sit=True, expr="soft"), "me": P(ME_SEAT, yaw=90, sit=True, expr="soft")})
shot("L64", "from outside the window, the island coming up", still([F + 6.2, 4.0, 5.3], [F + 1.7, 4.0, 5.2], 22),
     {"gran": P(GR_SEAT, yaw=90, sit=True, expr="soft"), "me": P(ME_SEAT, yaw=90, sit=True, expr="soft")})
shot("L64.1", "the armrest, two strokes", still([F + 1.4, 4.0, 5.2], [F + 1.75, 4.0, 4.6], 20),
     {"gran": P(GR_SEAT, yaw=90, sit=True, expr="soft"), "me": P(ME_SEAT, yaw=90, sit=True, expr="soft")})
shot("L65", "the wake back to the town", still([F + 3.0, -34, 16], [F, 6, 0], 22))

# ------------------------------------------------------------------------------------------------ 09 the sting
shot("L66", "the bench from inside, small and dark", still([F - 0.2, 4.0, 5.3], [F + 1.7, 4.0, 5.1], 17),
     {"gran": P(GR_SEAT, yaw=90, sit=True, expr="soft"), "me": P(ME_SEAT, yaw=90, sit=True, expr="soft")})
shot("L67", "Gran lost me", still([F + 4.6, 4.0, 5.3], [F + 1.7, 4.0, 5.2], 26),
     {"gran": P(GR_SEAT, yaw=90, sit=True, expr="soft", roll=0, walk=[("L67+1.2", [F + 1.7, 3.55, 3.91])]),
      "me": P(ME_SEAT, yaw=90, sit=True, expr="neutral")})
shot("L68", "the mat, the glove", still([X - 0.15, 32.6, 0.45], [X, 34.35, 0.1], 30))

# ------------------------------------------------------------------------------------------------ build shots and acting
NEUTRAL = {"arms": [0, 0], "side": [0, 0], "head": [0, 0], "lean": 0, "tremble": 0, "blink": True, "sit": False,
           "roll": 0}
acting = {n: [] for n in CHARS}
shots = []
state = {n: None for n in CHARS}      # None (never shown), "hidden", "shown"
for i, sh in enumerate(SHOTS):
    s = {"id": f"S{i + 1:02d}", "cam": sh["cam"], "hand": 0.004, "step": sh["step"], "what": sh["what"]}
    if i:
        s["at"] = sh["at"]
    shots.append(s)
    at = sh["at"]
    for n in CHARS:
        keys = acting[n]
        if n in sh["who"]:
            spec = dict(sh["who"][n])
            pos = spec.pop("pos")
            walk = spec.pop("walk", [])
            roll_extra = spec.pop("roll_to", None)
            prev = next((k["pos"] for k in reversed(keys) if "pos" in k), None)
            if prev is not None:
                keys.append({"at": at, "pos": prev})
            keys.append({"at": at, "pos": pos, "blend": 0, "hidden": False, **NEUTRAL, "expr": "neutral", **spec})
            for ref, p in walk:
                keys.append({"at": ref, "pos": p})
            state[n] = "shown"
        elif state[n] != "hidden":
            keys.append({"at": at, "hidden": True, "blend": 0})
            state[n] = "hidden"

# a few timed acting keys inside shots
acting["me"].append({"at": "L52>-0.4", "expr": "neutral", "blend": 0.3})
acting["gran"].append({"at": "L67+0.2", "roll": 14, "blend": 1.4})

# ------------------------------------------------------------------------------------------------ cues
cues = []


def cue(at, name, **kw):
    cues.append({"at": at, "name": name, **kw})


def tod(ref, name, dur=0.8):
    """A slow ramp that ends at the cut (it starts dur before it)."""
    cue(f"{ref}-{dur}" if ref != 0 else 0, "tod", set=name, dur=dur)


cue(0, "tod", set="day")
tod("L16", "sunny", 0.8)
cue("L16.4", "tod", set="day", dur=0.8)
tod("L17", "dusk1", 0.8)
tod("L21", "dusk2", 0.8)
tod("L24", "dusk3", 0.8)
tod("L25", "night", 0.8)
tod("L37", "day", 0.8)
cue("L38", "tod", set="night", dur=0.8)
cue(0, "sunbeam", v=0.0)
cue("L16-0.8", "sunbeam", v=1.0, dur=0.8)
cue("L16.4", "sunbeam", v=0.0, dur=0.8)
# visibility toggles
for vid, on in (("lglove_me", False),):
    pass
cue("L10", "vis", id="lglove_me", on=False)
cue("L63", "vis", id="lglove_me", on=True)
cue("L05.3", "vis", id="jumperworn", on=True)
cue("L06", "vis", id="jumperworn", on=False)
cue("L12", "vis", id="gglove", on=True)
cue("L14", "vis", id="gglove", on=False)
cue("L53", "vis", id="gglove", on=True)
cue("L54", "vis", id="gglove", on=False)
cue("L27", "vis", id="gglasses", on=False)
cue("L61", "vis", id="gglasses", on=True)
cue("L36", "vis", id="plum", on=True)
cue("L18", "vis", id="bowT", on=False)
cue("L37", "vis", id="bowT", on=True)
cue("L38", "vis", id="bowT", on=False)
cue("L41", "vis", id="bowI", on=True)
cue("L43", "vis", id="bowI", on=False)
# doors
cue("L17", "flatdoor", deg=-25, dur=1.0)
cue("L25+0.2", "cdoor", deg=8, dur=1.2)
cue("L29", "backdoor", deg=18, dur=1.0)
cue("L30+0.5", "backdoor", deg=100, dur=1.5)
# phone and bezel
cue("L12", "bezel", on=True)
cue("L14", "bezel", on=False)
cue("L36", "bezel", on=True)
cue("L37", "bezel", on=False)
cue("L40", "bezel", on=True)
cue("L40.3", "bezel", on=False)
cue("L53", "bezel", on=True)
cue("L54", "bezel", on=False)
cue("L14", "phone", on=True, pos=[200.95, 0.12, 0.77], rot=[-12, 0, -90], glow=0.7)
cue("L15", "phone", on=False)
cue("L35-0.4", "phone", on=True, pos=[X - 0.6, 44.55, 0.805], rot=[-12, 0, 0], glow=0.0)
cue("L35+0.2", "phone", on=True, pos=[X - 0.6, 44.55, 0.805], rot=[-12, 0, 0], glow=1.0, dur=1.0)
cue("L36", "phone", on=False)
# the bench
cue("L23", "dent", v=1.0, tilt=1.0, dur=1.2)
cue("L24", "dent", v=0.0, tilt=0.0, dur=1.0)
cue("L58.2", "dent", v=0.6, tilt=0.0, y=5.05)
cue("L59", "dent", v=0.0, tilt=0.0, y=5.05, dur=2.0)
cue("L23.2", "smudge", on=True)
cue("L24", "smudge", on=False)
cue("L64.1", "strokes", on=True)
cue("L65", "strokes", on=False)
cue("L32.1", "rattle", v=1.0, dur=0.5)
cue("L33", "rattle", v=0.0, dur=0.5)
cue(0, "mdots", v=0.0)
cue("L09", "mdots", v=0.45)
cue("L10", "mdots", v=0.0)
cue("L55>-0.3", "mdots", v=1.0, dur=0.3)
cue("L57", "mdots", v=0.0)

# the Shrug: never seen moving across the room. pos is the seat; u is the shoulder height.
cue(0, "shrug", hidden=True)
cue("L44", "shrug", pos=SH_SEAT, yaw=90, u=1.0, head=0, lean=0, tilt=0)
cue("L45", "shrug", pos=SH_SEAT, yaw=90, u=1.0, head=0, lean=0, tilt=0)
cue("L46", "shrug", pos=SH_SEAT, yaw=90, u=1.0, head=0, lean=0, tilt=0)
cue("L47", "shrug", pos=SH_SEAT, yaw=90, u=1.0, head=0, lean=0, tilt=0)
cue("L48", "shrug", pos=SH_SEAT, yaw=90, u=1.0, head=0, lean=0, tilt=12)
cue("L49", "shrug", pos=SH_SEAT, yaw=90, u=0.55, head=0, lean=0, tilt=0, dur=1.6)
cue("L50", "shrug", pos=SH_SEAT, yaw=90, u=0.0, head=0, lean=0, tilt=0, dur=2.4)
cue("L51", "shrug", pos=SH_SEAT, yaw=90, u=0.0, head=-90, lean=0, tilt=0, dur=2.2)
cue("L51.2", "shrug", pos=[F + 1.7, 4.75, 3.87], yaw=90, u=0.0, head=-90, lean=60, tilt=-10, dur=3.2)
cue("L51.2+3.4", "shrug", pos=[F + 1.7, 4.45, 3.87], yaw=90, u=0.0, head=-90, lean=60, tilt=-10)
cue("L58.2", "shrug", hidden=True)
# props
for pid in ("binglove", "mglove", "glasses", "kite", "jumper"):
    cue(0, "prop", id=pid, hide=True)
cue("L05", "prop", id="jumper", pos=[150, 6.6, 1.14], rot=[0, 0, 20])
cue("L05.3", "prop", id="jumper", hide=True)
cue("L06", "prop", id="kite", pos=[901.2, 8.5, 0.4], rot=[0, 0, 0])
cue("L06.3-0.05", "prop", id="kite", pos=[907, 22, 3.5], rot=[40, 30, 200])
cue("L06.3", "prop", id="kite", pos=[800.4, 6.8, 5.0], rot=[34, 0, 15], snap=True)
cue("L07", "prop", id="kite", hide=True)
cue("L10", "prop", id="binglove", hide=True)
cue("L10+0.2", "prop", id="binglove", pos=[150.35, 6.35, 1.6], rot=[20, 0, 30], snap=True)
cue("L10+0.9", "prop", id="binglove", pos=[150.0, 6.62, 1.1], rot=[60, 0, 80])
cue("L10+1.0", "prop", id="binglove", hide=True)
cue("L27", "prop", id="glasses", pos=[X - 0.05, 34.35, 0.075], rot=[0, 0, 25])
cue("L28", "prop", id="glasses", hide=True)
cue("L29", "prop", id="glasses", pos=[X - 0.17, 33.38, 0.9], rot=[90, 0, 0])
cue("L29+1.3", "prop", id="glasses", hide=True)
cue("L40.3", "prop", id="glasses", pos=[X - 0.17, 45.2, 0.9], rot=[90, 0, 0])
cue("L41", "prop", id="glasses", hide=True)
cue("L60", "prop", id="glasses", pos=[F + 2.2, 4.25, 4.95], rot=[90, 0, 90])
cue("L60>", "prop", id="glasses", pos=[F + 2.2, 3.65, 4.95], rot=[90, 0, 90])
cue("L61", "prop", id="glasses", hide=True)
cue("L62", "prop", id="mglove", pos=[F + 2.25, 3.75, 4.97], rot=[-90, 0, 0])
cue("L63", "prop", id="mglove", hide=True)
cue("L68", "prop", id="mglove", pos=[X, 34.35, 0.065], rot=[-90, 0, 0])
cue("L68.4", "prop", id="mglove", pos=[X, 34.35, 0.065], rot=[-90, 0, 0])
cue("L68.4+0.17", "prop", id="mglove", pos=[X, 34.5, 0.3], rot=[-60, 0, 0])
cue("L68.4+0.34", "prop", id="mglove", pos=[X, 34.65, 0.065], rot=[-90, 0, 0])
# the dog
cue(0, "dog", hide=True, pos=[0, 0, 0])
cue("L07", "dog", pos=[-3.6, 3.6, 0], yaw=[90], gait=1)
cue("L07>+0.5", "dog", pos=[3.6, 3.6, 0], yaw=[90], gait=1)
cue("L08", "dog", pos=[0.1, -14.3, 0], yaw=[0], gait=1)
cue("L08+0.5", "dog", pos=[0.1, -15.3, 0], yaw=[0], gait=1)
cue("L08+1.4", "dog", pos=[0.1, -18.5, 0.9], yaw=[0], gait=1)
cue("L08+2.6", "dog", pos=[0.1, -22.0, 0.9], yaw=[0], gait=1)
cue("L08.2", "dog", pos=[X + 8.55, -3.0, 0], yaw=[90], gait=0, snap=True)
cue("L09", "dog", hide=True, pos=[0, 0, 0])
cue("L54", "dog", pos=[X + 8.55, -3.0, 0], yaw=[90], gait=0)
cue("L55", "dog", hide=True, pos=[0, 0, 0])
# the lost things hopping after their owners
hoppers = [
    {"id": "hg", "kind": "glove", "color": "#2f8f4a", "owner": "glove_woman", "behind": 0.8, "side": 0.0},
    {"id": "hu", "kind": "umbrella", "color": "#16171b", "owner": "umbrella_man", "behind": 0.45, "side": 0.28},
    {"id": "hk", "kind": "keys", "color": "#9aa2a6", "owner": "pass1", "behind": 0.7, "side": 0.0},
    {"id": "hs", "kind": "scarf", "color": "#c04a3a", "owner": "pass2", "behind": 0.8, "side": 0.0},
]
for h in ("hg", "hu"):
    cue(0, "hop", id=h, on=True)
    cue("L10", "hop", id=h, on=False)
for h in ("hk", "hs"):
    cue("L09", "hop", id=h, on=True)
    cue("L10", "hop", id=h, on=False)
# the first scare's wind, the island lights etc. are in set.py

sfx = []
for r, db in (("L01+0.5", -27), ("L01+1.1", -27), ("L02+0.2", -27), ("L02+0.75", -27), ("L03+0.3", -27),
              ("L03+0.85", -27), ("L09+0.2", -28), ("L09+0.8", -28), ("L09+1.4", -28)):
    sfx.append({"at": r, "kind": "pop", "db": db})
sfx += [
    {"at": "L10+0.8", "kind": "thud", "db": -26},
    {"at": "L23+0.1", "kind": "creak", "db": -9, "dur": 1.5},
    {"at": "P01>-0.1", "kind": "thud", "db": -9},
    {"at": "L32.1+0.1", "kind": "click", "db": -26},
    {"at": "L32.1+0.35", "kind": "click", "db": -25},
    {"at": "L32.1+0.7", "kind": "click", "db": -26},
    {"at": "L35+0.3", "kind": "glitch", "db": -22, "dur": 0.4},
    {"at": "L35+0.9", "kind": "glitch", "db": -22, "dur": 0.4},
    {"at": "L41+0.4", "kind": "thud", "db": -19},
    {"at": "L43+0.8", "kind": "creak", "db": -13, "dur": 1.4},
    {"at": "P02>-0.4", "kind": "creak", "db": -8, "dur": 1.1},
    {"at": "L45+0.3", "kind": "sting", "db": -19},
    {"at": "L51.2", "kind": "glide", "db": -20, "dur": 2.4},
    {"at": "L59", "kind": "creak", "db": -22, "dur": 1.2},
    {"at": "L68.4+0.05", "kind": "pop", "db": -14},
    {"at": "L68.4+0.15", "kind": "glide", "db": -16, "dur": 0.5},
]

secs = [
    {"at": 0, "voices": ["pad", "piano"], "energy": 0.25},
    {"at": "L02", "voices": ["pad", "piano", "pulse"], "energy": 0.42},
    {"at": "L09", "voices": ["pad", "piano"], "energy": 0.3},
    {"at": "L18", "voices": ["pad", "piano"], "energy": 0.3},
    {"at": "L24", "voices": ["pad"], "energy": 0.25},
    {"at": "L27", "voices": ["drone", "pad", "piano"], "energy": 0.6},
    {"at": "L35", "voices": ["drone", "pad", "choir"], "energy": 0.6},
    {"at": "L43", "voices": ["drone", "pad"], "energy": 0.55},
    {"at": "L45", "voices": ["drone", "pad", "choir"], "energy": 0.7},
    {"at": "L52", "voices": ["drone", "pad", "piano"], "energy": 0.55},
    {"at": "L58", "voices": ["drone", "pad", "piano"], "energy": 0.5, "mode": "major", "root": 45},
    {"at": "L66", "voices": ["drone"], "energy": 0.6},
]

story = {
    "slug": "ep52-ferry-crossing",
    "title": "In this town, everything you lose finds its way back to you",
    "made_for_kids": False,
    "premise": "In a harbour town, everything you lose hops home after you, except for me. I throw a glove in a bin on purpose, and on Sunday's call Gran is pulling it on. Then my evenings go blank, and each time I come to I am further along the way to her island: the slipway, the ferry's window seat, her lane, her open door, her glasses on the mat.",
    "twist": "The rule never said to its owner. Lost things find their way to where they belong, and people count too. Everything of mine went to Gran's because I still belong there, and the blank evenings were me, a lost thing, finding my way back. On the late crossing a passenger in life jacket orange sits in my place beside her, and when I stop fighting it and sit down in my old seat, it is gone.",
    "world": "a small white car ferry with a rust-streaked hull on flat grey water between a harbour town and an island in late autumn: a concrete slipway, a rust-red ticket hut, a lounge with teal vinyl and a window bench, a stone lane between dry-stone walls, a white cottage with a green door, and a back room hung with every glove and key I ever lost",
    "voice": {"voice": "am_adam", "tempo": 1.03, "rate": 1.45},
    "key_color": "#7fe0c8",
    "caption": {"ink": "#08090d", "stroke_add": 2, "shadow": 0.8},
    "key_stroke": 2,
    "gap": 0.12,
    "tail": 0,
    "look": {"fog": "#b4babd", "fog_density": 0.010, "fog_start": 4.0, "sky": "#c4ccd0", "sky_strength": 1.0,
             "exposure": 0.0, "flash_safe": True},
    "grade": {"shadows": [-0.02, 0.0, 0.04], "highlights": [0.03, 0.01, -0.03], "saturation": 0.95, "contrast": 1.05,
              "vignette": 0.3, "bloom": 0.22, "grain": 0.012},
    "phonemes": {},
    "cast": cast,
    "hoppers": hoppers,
    "lines": lines,
    "shots": shots,
    "acting": acting,
    "cues": cues,
    "fx": [],
    "music": {"root": 45, "mode": "minor", "bpm": 76, "seed": 52, "sections": secs},
    "sound": {"floor": "stone", "steps_db": -22,
              "ambience": [
                  {"kind": "water", "from": 0, "to": "end", "lufs": -34},
                  {"kind": "wind", "from": 0, "to": "end", "lufs": -38},
                  {"kind": "hum", "from": "L21", "to": "L24", "lufs": -38},
                  {"kind": "hum", "from": "L25", "to": "L35", "lufs": -44},
                  {"kind": "hum", "from": "L42", "to": "end", "lufs": -36},
              ],
              "sfx": sfx,
              "music_drops": [{"from": "P01", "to": "P01>", "keep": ["thud"]},
                              {"from": "P02", "to": "P02>", "keep": ["creak"]}]},
}
OUT.write_text(json.dumps(story, indent=1, ensure_ascii=False) + "\n")
print("wrote", OUT, f"({len(shots)} shots)")
