"""Writes ../story.json for ep31 "Dawn Flight" (script 2026-11-02).

Run from anywhere: python stories/ep31-dawn-flight/generator/make_story.py
The words are in lines.json next to this file. Everything else is here: the cast, the shots and their cameras, the
acting, the cues set.py reads (the day, the lean, the roars, the creature, the plants), the score and the sound.
Shot ids are numbered in order (S01, S02 ...). Places are set.py's metres: the basket's floor centre is the origin, the
sun is east (+x), a character with yaw 0 faces -y and yaw 90 faces +x.

Corners (inside half-width 1.15): me SW, Dad SE (against the east rim, watching the sunrise), Rosa NW, the empty
fourth corner NE (the sandbag, the fourth flask, the four tally strokes on its rim, and the Loose One).
"""
import json
import math
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE.parent / "story.json"
lines = json.loads((HERE / "lines.json").read_text())

# ---------------------------------------------------------------------------------------------------- lines
PAUSES = {"L49": {"id": "P01", "pause": 0.7, "chunks": []}, "L58": {"id": "P02", "pause": 0.8, "chunks": []}}
out_lines = []
for ln in lines:
    out_lines.append(ln)
    if ln["id"] in PAUSES:
        out_lines.append(PAUSES[ln["id"]])
lines = out_lines

# ---------------------------------------------------------------------------------------------------- cast
cast = {
    "me": {"age": "adult", "skin": "#d9a77f", "shirt": "#d9a21b", "pattern": "knit", "pattern_c": "#b8860f",
           "collar": "#caa020", "pants": "#26282e", "shoes": "#3a3a3c", "sleeves": "long", "hair": "cap",
           "hair_c": "#1e1714", "hat": "beanie", "hat_c": "#8a8d92", "extras": ["apron"], "extra_c": "#1f2c4a",
           "width": 0.86, "face": {"eyes": "round", "brows": True, "ink": "#161012"}},
    "dad": {"age": "adult", "skin": "#e8bf99", "shirt": "#2c4a38", "pattern": "solid", "collar": "#243d2e",
            "pants": "#3a3630", "shoes": "#2a2420", "sleeves": "long", "hair": "buzz", "hair_c": "#9a9a9c",
            "hat": "none", "extras": ["glasses", "scarf"], "extra_c": "#d6c49a", "width": 0.86, "height": 0.97,
            "face": {"eyes": "round", "brows": True, "ink": "#1a1214", "bags": True}},
    "rosa": {"age": "adult", "skin": "#8a5a44", "shirt": "#e6dcc4", "pattern": "knit", "pattern_c": "#cfc4a8",
             "collar": "#d4c8ac", "pants": "#2b2d33", "shoes": "#1c1c1e", "sleeves": "long", "hair": "bun",
             "hair_c": "#1a1210", "hat": "beanie", "hat_c": "#7a2434", "width": 0.86, "height": 0.95,
             "face": {"eyes": "round", "brows": True, "ink": "#140e0e"}},
    "callum": {"age": "adult", "skin": "#d9a77f", "shirt": "#1f3d2a", "pattern": "solid", "collar": "#1a3323",
               "pants": "#2c2e36", "shoes": "#d8d2c4", "sleeves": "long", "hair": "cap", "hair_c": "#3a2a20",
               "hat": "beanie", "hat_c": "#1f2c4a", "width": 0.86,
               "face": {"eyes": "round", "brows": True, "ink": "#161012", "bags": True}},
}


def c(*keys):
    return [list(k) for k in keys]


def still(loc, tgt, lens):
    return c([0, loc, tgt, lens])


def move(a, b, la, lb=None):
    return c([0, a[0], a[1], la], [1, b[0], b[1], lb or la])


def r3(v):
    return [round(x, 3) for x in v]


def fwd(yaw):
    return (math.sin(math.radians(yaw)), -math.cos(math.radians(yaw)))


def face_cam(pos, yaw, dist, ang, lens, h=1.55, dz=0.0, hz=1.5, z0=0.0, sway=None):
    """A camera in front of a face: dist metres out along (yaw + ang), looking at the head."""
    fx, fy = fwd(yaw + ang)
    loc = [pos[0] + fx * dist, pos[1] + fy * dist, z0 + h + dz]
    tgt = [pos[0], pos[1], z0 + hz]
    if sway:
        loc2 = [loc[0] + sway[0], loc[1] + sway[1], loc[2] + sway[2]]
        return c([0, loc, tgt, lens], [1, loc2, tgt, lens])
    return still(loc, tgt, lens)


def yaw_to(a, b):
    return round(math.degrees(math.atan2(b[0] - a[0], -(b[1] - a[1]))), 1)


# ---------------------------------------------------------------------------------------------------- places
ME = (-0.62, -0.62)
DAD = (0.9, -0.35)
ROSA = (-0.58, 0.6)
D4 = (0.52, 0.55)              # the fourth corner: the Loose One stands here
FIELD_DAD = (-2.2, -2.6)
K0 = -300.0                    # the kitchen's floor
KITCHEN_ME = (-0.95, 0.0)
KITCHEN_DAD = (0.95, 0.0)
SC1 = [39.0, 39.0, -13.2]      # the scatter, a field away, hung in the mist
FAR = [28.0, 28.0, -0.7]       # one hedge off, at basket height
NEAR = [5.7, 5.7, -0.1]        # a rope's length off


def c2w(root, yaw, loc):
    """A point in the creature's own frame to world (root position, yaw degrees)."""
    a = math.radians(yaw)
    x = loc[0] * math.cos(a) - loc[1] * math.sin(a)
    y = loc[0] * math.sin(a) + loc[1] * math.cos(a)
    return [root[0] + x, root[1] + y, root[2] + loc[2]]


CAM_UP = [0.0, -0.9, 1.3]
FLAME = still(CAM_UP, [0.0, 0.0, 3.0], 22)
SIDE = still([-14.0, -22.0, 0.6], [0.0, 0.0, 2.4], 24)
ME_EYE = [0.5, 0.5, 1.75]       # inside the basket, over the fourth corner's rim, looking out
ROOT_FAR = FAR
YAW_FAR = -45.0
YAW_NEAR = -45.0

# ---------------------------------------------------------------------------------------------------- shots
# (at, what, camera, step, extras)
SHOTS = [
    # 01 the tilt
    (0, "the hook: a wide from outside, the envelope still, the basket leaning",
     c([0, [-3, -36, 8.8], [0, 0, 7.6], 22], [1, [-2.2, -33.5, 8.7], [0, 0, 7.6], 22]), 2, {"frame": "world"}),
    ("L03", "a close on the still envelope", still([-9, -15, 4.0], [0.5, 0, 10.5], 30), 2, {"frame": "world"}),
    ("L04", "low on the fourth corner, the floor tipping", still([-0.35, -0.25, 0.6], [0.62, 0.66, 0.2], 20), 2,
     {"key": 14}),
    ("L05", "the burner roaring overhead", FLAME, 2, {"key": 0}),
    ("L05.1", "the mist below, the scatter far off", still([0.5, 0.5, 1.8], [35.0, 35.0, -12.0], 38), 2, {"key": 0}),
    # 02 before
    ("L06", "Dad on the launch field, grinning", face_cam((FIELD_DAD[0], FIELD_DAD[1]), 0, 1.9, 22, 30, h=1.5), 2,
     {"key": 40, "frame": "world"}),
    ("L07", "the kitchen table at night", still([0.2, -2.3, K0 + 1.55], [0, 0, K0 + 1.1], 22), 2,
     {"room": "kitchen", "frame": "world"}),
    ("L08", "me looking down at my tea", face_cam(KITCHEN_ME, 90, 1.5, -35, 32, h=1.5, z0=K0), 2,
     {"room": "kitchen", "frame": "world", "key": 20}),
    ("L09", "Dad nodding", face_cam(KITCHEN_DAD, -90, 1.5, 35, 32, h=1.48, z0=K0), 2,
     {"room": "kitchen", "frame": "world", "key": 20}),
    ("L10", "the launch field in the dark, our breath in the lamp light",
     c([0, [4.2, -7.2, 1.3], [-1.4, 0.0, 1.9], 20], [1, [3.6, -6.8, 1.35], [-1.4, 0.0, 1.9], 20]), 2,
     {"frame": "world", "key": 12}),
    ("L11", "the first flame into the mouth", still([1.6, -2.4, 1.2], [-0.2, 0.0, 3.0], 24), 2, {"frame": "world"}),
    ("L12", "the envelope standing up off the grass", still([-8.5, -12.0, 1.0], [-1.0, 0.0, 8.0], 17), 2,
     {"frame": "world"}),
    ("L13", "top-down on the four-corner basket", still([0.0, -1.7, 3.0], [0.0, 0.0, 0.2], 15), 2, {"key": 20}),
    ("L14", "Dad's bag open and FOUR flasks along the rim of his corner",
     still([-0.2, 0.15, 1.95], [1.1, -0.55, 1.15], 27), 2, {"key": 28}),
    ("L15", "my face", face_cam(ME, 135, 1.5, -40, 32), 2, {"key": 34}),
    ("L16", "Dad's sleeve and the fourth flask on the empty corner's floor",
     still([-0.4, -0.12, 1.3], [0.62, 0.55, 0.55], 24), 2, {"key": 32}),
    ("L17", "Rosa looking at the empty corner", face_cam(ROSA, 90, 1.5, -50, 32, h=1.5), 2, {"key": 34}),
    ("L18", "the sandbag, tied by its rope into the fourth corner, Rosa's sleeve at the end",
     still([-0.45, 0.2, 1.4], [0.85, 0.8, 0.8], 24), 2, {"key": 34}),
    ("L19", "the lore close: four slate-blue strokes on the leather rim",
     still([0.55, 0.15, 2.8], [0.55, 1.48, 0.11], 28), 2, {"key": 30}),
    ("L20", "the ground lets go of us", c([0, [-7.5, -10, 2.2], [0, 0, 3.6], 20], [1, [-7.5, -10, 2.2], [0, 0, 4.4], 20]),
     2, {"frame": "world"}),
    # 03 up
    ("L21", "the fields sinking under the mist", c([0, [0.4, 0.4, 1.7], [4.5, 6.5, -4.0], 24],
                                                  [1, [0.4, 0.4, 1.7], [4.5, 6.5, -12.0], 24]), 2, {"key": 0}),
    ("L22", "Rosa looking up", face_cam(ROSA, 45, 1.5, 25, 32, h=1.35, dz=0.0), 2, {"key": 32}),
    ("L23", "Dad's cup sliding along the rim", still([-0.4, -1.0, 1.75], [1.21, 0.1, 1.2], 30), 2, {"key": 22}),
    ("L24", "the cup stopping at the fourth corner", still([0.3, 0.1, 1.7], [1.21, 0.78, 1.25], 32), 2, {"key": 22}),
    ("L25", "Rosa frowning", face_cam(ROSA, 45, 1.5, 30, 32, h=1.5), 2, {"key": 34}),
    ("L25.1", "the flame overhead, roar one", FLAME, 2, {"key": 0}),
    ("L26", "the mist lit orange under us", still([0.5, 0.5, 1.8], [7.0, 9.0, -12.0], 26), 2, {"key": 0}),
    ("L27", "a long lens across the mist: the scatter a field away", still(ME_EYE, SC1, 70), 4, {"key": 0}),
    ("L28", "a closer long lens on the scatter", still(ME_EYE, [SC1[0], SC1[1], SC1[2] + 0.2], 105), 4, {"key": 0}),
    ("L29", "the parts of somebody", still(ME_EYE, [SC1[0], SC1[1], SC1[2] + 0.2], 125), 4, {"key": 0}),
    ("L30", "the roar stops and they are gone", still(ME_EYE, [SC1[0], SC1[1], SC1[2] + 0.2], 70), 4, {"key": 0}),
    ("L31", "a side wide: the lean a little steeper", SIDE, 2, {"frame": "world"}),
    # 04 nearer
    ("L32", "Dad delighted, barn roofs behind him", face_cam(DAD, 90, 1.5, -5, 30, h=1.55), 2, {"key": 32}),
    ("L33", "the flame, roar two", FLAME, 2, {"key": 0}),
    ("L34", "one hedge off", still(ME_EYE, [FAR[0], FAR[1], 0.9], 85), 4, {"key": 0}),
    ("L35", "they've come together, almost", still(ME_EYE, [FAR[0], FAR[1], 1.1], 140), 4, {"key": 0}),
    ("L36", "legs, body, arms, head in slices",
     c([0, ME_EYE, [FAR[0], FAR[1], 0.0], 150], [1, ME_EYE, [FAR[0], FAR[1], 2.1], 150]), 4, {"key": 0}),
    ("L37", "a gap between two arm blocks with mist behind",
     still(ME_EYE, c2w(FAR, YAW_FAR, [0.5, 0, 1.43]), 330), 4, {"key": 0}),
    ("L38", "far taller than a person",
     c([0, ME_EYE, [FAR[0], FAR[1], 2.2], 130], [1, ME_EYE, [FAR[0], FAR[1], 0.6], 130]), 4, {"key": 0}),
    ("L39", "Rosa never saw it", face_cam(ROSA, 45, 1.5, 25, 32, h=1.5), 2, {"key": 32}),
    ("L39.2", "my eyeline across the basket: three people standing still",
     still([-0.85, -0.85, 1.6], [0.5, 0.1, 1.4], 22), 2, {"key": 26}),
    ("L40", "the sandbag rope, taut", still([0.35, 0.35, 0.95], [1.02, 1.0, 0.7], 36), 2, {"key": 22}),
    ("L41", "the flame, roar three", FLAME, 2, {"key": 0}),
    ("L42", "a rope's length from the basket", still(ME_EYE, [NEAR[0], NEAR[1], 1.25], 60), 4, {"key": 0}),
    ("L43", "every piece in the right place", still(ME_EYE, [NEAR[0], NEAR[1], 1.3], 80), 4, {"key": 0}),
    ("L44", "its face in slices", still(ME_EYE, [NEAR[0], NEAR[1], 2.3], 170), 4, {"key": 0}),
    ("L45", "the eyes on one, the mouth two gaps below",
     c([0, ME_EYE, [NEAR[0], NEAR[1], 2.4], 210], [1, ME_EYE, [NEAR[0], NEAR[1], 2.05], 210]), 4, {"key": 0}),
    ("L46", "pink mist through the gaps", still(ME_EYE, [NEAR[0], NEAR[1], 1.35], 150), 4, {"key": 0}),
    ("L47", "the glow fading, and it with it", still(ME_EYE, [NEAR[0], NEAR[1], 1.25], 60), 4, {"key": 0}),
    # 05 the fourth corner
    ("L48", "the basket tipping hard toward the fourth corner", SIDE, 2, {"frame": "world"}),
    ("L49", "Rosa: HOLD ON", face_cam(ROSA, 45, 1.5, 25, 30, h=1.5), 2, {"key": 28}),
    ("P01", "the flame ramping up, long", FLAME, 1, {"key": 0}),
    ("L50", "the reveal from my corner across the basket", still([-1.4, -1.4, 1.6], [0.5, 0.5, 1.45], 17), 1,
     {"key": 0, "amb": 0.45}),
    ("L51", "in the fourth corner beside the sandbag", still([-0.3, -0.45, 0.55], [0.62, 0.7, 0.6], 24), 1, {"key": 0}),
    ("L52", "a low angle up its pieces into the burner glow", still([-0.4, 0.12, 0.5], [0.52, 0.55, 2.3], 22), 1,
     {"key": 0}),
    ("L53", "a copper arm block a hand's width from Dad's shoulder",
     still([0.1, -0.05, 1.52], [0.95, 0.3, 1.45], 42), 1, {"key": 0}),
    ("L54", "its sliced face turned to Dad, three-quarter view", c([0, [-0.55, -0.3, 2.0], [0.52, 0.55, 2.15], 24, 6.0]), 1,
     {"key": 0, "amb": 0.45}),
    ("L55", "Dad looking out at the brightening horizon",
     c([0, [2.25, -0.38, 1.6], [0.9, -0.35, 1.5], 30], [1, [2.2, -0.38, 1.6], [0.9, -0.35, 1.5], 30]), 1, {"key": 30}),
    ("L56", "a short roar overhead", FLAME, 1, {"key": 0}),
    ("L57", "from my eyeline: its top slice has turned to me", still([-0.62, -0.62, 1.95], [0.52, 0.55, 2.15], 28), 1,
     {"key": 0}),
    ("L58", "the rest of it still faces Dad", still([-1.12, -1.12, 1.7], [0.45, 0.45, 1.6], 18), 1, {"key": 0}),
    ("P02", "hold on my face", face_cam(ME, 135, 1.45, -35, 34), 1, {"key": 30}),
    # 06 the truth
    ("L59", "over my shoulder: me, the fourth corner, it, Dad beside it", still([-0.95, -0.9, 1.65], [0.6, 0.4, 1.55], 20), 2,
     {"key": 12}),
    ("L60", "a side wide of the lean", SIDE, 2, {"frame": "world"}),
    ("L61", "my face, ashamed", face_cam(ME, 135, 1.5, -40, 32), 2, {"key": 34}),
    ("L62", "Dad's back, the sunrise beyond", still([-0.15, -0.3, 1.62], [3.0, -0.3, 1.45], 26), 2, {"key": 14}),
    ("L63", "my face", face_cam(ME, 135, 1.35, -45, 36), 2, {"key": 34}),
    ("L64", "the sun breaking out of the mist, all gold", still([0.0, 0.1, 1.7], [60.0, -3.0, 1.2], 22), 2, {"key": 0}),
    ("L65", "me turned to Dad, my mouth moving, Dad turning to me", still([0.15, -2.5, 1.65], [0.15, -0.4, 1.5], 16), 2,
     {"key": 30}),
    ("L66", "Dad quiet under a short roar", face_cam(DAD, yaw_to(DAD, ME), 1.5, 5, 32, h=1.5), 2, {"key": 30}),
    ("L67", "Dad laughing", face_cam(DAD, yaw_to(DAD, ME), 1.5, -8, 32, h=1.5), 2, {"key": 30}),
    ("L67.2", "Rosa startled at the burner", face_cam(ROSA, 45, 1.5, 25, 32, h=1.5), 2, {"key": 30}),
    ("L68", "Dad's face", face_cam(DAD, yaw_to(DAD, ME), 1.3, 12, 36, h=1.5), 2, {"key": 30}),
    ("L69", "Dad nodding at the fourth flask in its corner", still([-0.3, -0.15, 1.5], [0.8, 0.2, 1.2], 24), 2,
     {"key": 22}),
    ("L70", "a bright wide down the sunlit valley: the lean, the creature in its corner",
     still([15.0, -13.0, 2.4], [0.0, 0.0, 2.3], 27), 2, {"frame": "world"}),
    # 07 landing
    ("L71", "the basket settling upright in a stubble field", still([-9.0, -8.0, 1.2], [0.0, 0.0, 1.9], 22), 2,
     {"frame": "world"}),
    ("L72", "the phone on the rim, Dad bent toward it", still([-0.25, 0.35, 1.55], [1.21, -0.05, 1.25], 30), 2,
     {"key": 24}),
    ("L73", "a close on the phone", still([0.9, -0.05, 1.62], [1.21, -0.05, 1.23], 42), 2, {"key": 18}),
    ("L74", "Dad's mouth", face_cam(DAD, yaw_to(DAD, ME), 1.3, 12, 36, h=1.5), 2, {"key": 30}),
    ("L75", "Dad and me laughing", still([0.15, -2.5, 1.65], [0.15, -0.4, 1.5], 16), 2, {"key": 30}),
    ("L76", "me looking across the basket", face_cam(ME, 135, 1.45, -35, 34), 2, {"key": 30}),
    ("L77", "the fourth corner in bright morning light: the sandbag and the flask",
     still([-0.25, 0.0, 1.45], [0.62, 0.72, 0.4], 22), 2, {"key": 12}),
    # 08 four
    ("L78", "the launch field the next dawn: four of us in the basket", still([-3.6, -4.0, 2.7], [0.0, 0.0, 1.35], 22), 2,
     {"frame": "world", "key": 10}),
    ("L79", "Rosa's sleeve and the sandbag on the grass", still([0.7, -3.0, 0.95], [2.1, -1.3, 0.35], 28), 2,
     {"frame": "world", "key": 12}),
    ("L80", "Callum's flask on his corner's rim", still([-0.3, 0.1, 1.75], [1.21, 0.6, 1.3], 34), 2, {"key": 24}),
    ("L81", "a wide from outside: the basket level against a flat gold horizon",
     c([0, [-3, -36, 8.8], [0, 0, 7.6], 22], [1, [-2.2, -33.5, 8.7], [0, 0, 7.6], 22]), 2, {"frame": "world"}),
]

shots = []
for i, (at, what, cam, step, extra) in enumerate(SHOTS):
    s = {"id": f"S{i + 1:02d}", "cam": cam, "hand": 0.0 if step == 4 else 0.005, "step": step, "what": what}
    if i:
        s["at"] = at
    s.update(extra)
    shots.append(s)

# ---------------------------------------------------------------------------------------------------- acting
NEUTRAL = {"arms": [0, 0], "side": [0, 0], "head": [0, 0], "lean": 0, "tremble": 0, "blink": True}
acting = {"me": [], "dad": [], "rosa": [], "callum": []}


def put(who, at, pos, **kw):
    keys = acting[who]
    prev = next((k["pos"] for k in reversed(keys) if "pos" in k), None)
    if prev is not None:
        keys.append({"at": at, "pos": prev})
    keys.append({"at": at, "pos": pos, "blend": 0, "hidden": False, **NEUTRAL, **kw})


def key(who, at, **kw):
    acting[who].append({"at": at, **kw})


def hide(who, at):
    acting[who].append({"at": at, "hidden": True, "blend": 0})


def talk(who, a, b):
    acting[who].append({"from": a, "to": b, "mouth": [0.55, 0.55], "flap": True})


def p3(xy, z=0.0):
    return [xy[0], xy[1], z]


# me: the flight stance, then the field, the kitchen, the flight again
put("me", 0, p3(ME), yaw=135, expr="worried", head=[0, 6])
hide("me", "L06")
put("me", "L07", p3(KITCHEN_ME, K0), yaw=90, expr="neutral", head=[0, 6])
key("me", "L08", head=[0, 30], expr="worried", blend=0.4)
put("me", "L10", [-1.3, -1.9, 0], yaw=30, expr="worried")
put("me", "L13", p3(ME), yaw=135, expr="worried", head=[0, 6])
key("me", "L15", expr="worried")
talk("me", "L15.1", "L15>")
key("me", "L19", expr="worried")
key("me", "L25", expr="worried")
hide("me", "L39.2")
put("me", "L40", p3(ME), yaw=135, expr="worried", head=[0, 6])
key("me", "L46", expr="scared", blend=0.3)
key("me", "L48", expr="scared", head=[0, 4])
hide("me", "L50")                                  # I'm the camera across the basket
put("me", "P02", p3(ME), yaw=135, expr="terrified", head=[0, 4])
put("me", "L61", p3(ME), yaw=135, expr="shut", head=[0, 20])
key("me", "L63", expr="shut", head=[0, 22], blend=0.4)
key("me", "L65", yaw=yaw_to(ME, DAD), expr="worried", head=[0, 0], blend=0.3)
talk("me", "L65", "L65>")
key("me", "L67", expr="soft", blend=0.5)
key("me", "L75", expr="grin", blend=0.3)
key("me", "L76", yaw=135, expr="soft", head=[0, 4], blend=0.4)
put("me", "L78", p3(ME), yaw=135, expr="grin")

# Dad: grinning on the field, hopeful at the table, in his corner watching the east
put("dad", 0, p3(DAD), yaw=90, expr="soft")
put("dad", "L06", p3(FIELD_DAD), yaw=0, expr="grin")
put("dad", "L07", p3(KITCHEN_DAD, K0), yaw=-90, expr="worried", head=[0, 4])
key("dad", "L09", expr="soft", head=[0, 16], blend=0.3)
key("dad", "L09+0.55", head=[0, -6], blend=0.25)
key("dad", "L09+1.0", head=[0, 14], blend=0.3)
put("dad", "L10", [-2.3, -2.4, 0], yaw=30, expr="soft")
put("dad", "L13", p3(DAD), yaw=90, expr="grin")
put("dad", "L16", p3(DAD), yaw=180, arms=[0, 82], expr="grin")
talk("dad", "L16.1", "L16.2")
key("dad", "L17", yaw=90, arms=[0, 0], blend=0.4)
key("dad", "L21", expr="grin")
key("dad", "L32", expr="grin", arms=[0, 78], blend=0.3)
talk("dad", "L32.3", "L32>")
key("dad", "L33", arms=[0, 0], blend=0.4)
key("dad", "L50", expr="soft")
key("dad", "L55", expr="soft", yaw=90)
key("dad", "L59", expr="soft")
key("dad", "L65", yaw=yaw_to(DAD, ME), expr="neutral", blend=0.5)
key("dad", "L67", expr="grin", blend=0.3)
talk("dad", "L67.1", "L67>")
key("dad", "L68", expr="grin", yaw=yaw_to(DAD, ME))
talk("dad", "L68.1", "L68>")
key("dad", "L69", yaw=90, head=[80, 10], expr="soft", blend=0.5)
key("dad", "L70", head=[0, 0], blend=0.4)
key("dad", "L72", head=[40, 34], yaw=70, blend=0.5)
key("dad", "L74", head=[0, 0], yaw=yaw_to(DAD, ME), expr="grin", blend=0.4)
talk("dad", "L74", "L74>")
key("dad", "L75", expr="squeeze")
put("dad", "L78", p3(DAD), yaw=90, expr="grin")

# Rosa: by the fan, at the burner frame, in her corner
put("rosa", 0, p3(ROSA), yaw=45, expr="neutral")
hide("rosa", "L06")
put("rosa", "L10", [2.9, -3.8, 0], yaw=-60)
put("rosa", "L11", [0.4, -1.9, 0], yaw=180, arms=[40, 40], head=[0, 10])
put("rosa", "L13", p3(ROSA), yaw=45)
key("rosa", "L17", yaw=90, expr="worried", blend=0.4)
put("rosa", "L18", [0.4, 1.0, 0], yaw=90, arms=[85, 0], expr="neutral")
talk("rosa", "L18.3", "L18>")
put("rosa", "L20", p3(ROSA), yaw=45)
key("rosa", "L22", head=[0, -30], blend=0.5)
talk("rosa", "L22.2", "L22>")
key("rosa", "L23", head=[0, 0], blend=0.4)
key("rosa", "L25", expr="worried")
key("rosa", "L39", expr="neutral", yaw=45)
talk("rosa", "L39.2", "L39.3")
key("rosa", "L48", expr="wide", blend=0.3)
talk("rosa", "L49.1", "L49.2")
key("rosa", "L50", expr="neutral", blend=0.4)
key("rosa", "L67", expr="wide", blend=0.1)
key("rosa", "L68", expr="neutral", blend=0.4)
put("rosa", "L79", [2.0, -0.9, 0], yaw=200, arms=[55, 55], expr="neutral")
put("rosa", "L81", p3(ROSA), yaw=45)

# Callum: only in section 08
hide("callum", 0)
put("callum", "L78", p3(D4), yaw=90, expr="grin")
key("callum", "L80", expr="soft")

# ---------------------------------------------------------------------------------------------------- cues
cues = []


def cue(at, name, **kw):
    cues.append({"at": at, "name": name, **kw})


# the day: plum pre-dawn, a brightening horizon at L55, then the sun in one 3.4 s ramp from L64, a bright next dawn
cue(0, "dawn", v=0.0)
cue("L55", "dawn", v=0.26, dur=2.0)
cue("L62", "dawn", v=0.34, dur=2.0)
cue("L64-0.2", "dawn", v=1.0, dur=3.6)
cue("L78", "dawn", v=0.86, dur=0)
# the lean (degrees toward the fourth corner)
cue(0, "tilt", deg=6.0)
cue("L06", "tilt", deg=0.0, dur=0)
cue("L22.2", "tilt", deg=4.0, dur=1.2)
cue("L24", "tilt", deg=5.5, dur=1.2)
cue("L31", "tilt", deg=7.5, dur=1.6)
cue("L48", "tilt", deg=12.0, dur=1.2)
cue("L59", "tilt", deg=9.0, dur=2.0)
cue("L70+0.3", "tilt", deg=0.0, dur=1.7)
cue("L81", "tilt", deg=0.0, dur=0)
# the ground: up at L20, down at L70, the landing field at L71, the launch field again at L78, up again for the wide
cue(0, "alt", alt=18.0)
cue("L06", "alt", alt=0.0, dur=0)
cue("L20", "alt", alt=0.0, dur=0)
cue("L20+0.4", "alt", alt=18.0, dur=9.0)
cue("L70+0.4", "alt", alt=0.0, dur=2.3)
cue("L78", "alt", alt=0.0, dur=0)
cue("L81", "alt", alt=18.0, dur=0)
cue("L71", "field", f=1)
cue("L78", "field", f=0)
cue("L81", "field", f=0)
# the envelope lies on the field until Rosa fills it
cue(0, "env", up=1.0)
cue("L06", "env", up=0.0, dur=0)
cue("L11+0.3", "env", up=1.0, dur=3.4)
cue("L78", "env", up=1.0, dur=0)
# the burner: ramps up over 0.6 s, holds, shrinks over 0.9 s; never two roars inside 3 s
cue("L05", "roar", peak=1.0, up=0.6, hold=1.6, down=0.9)
cue("L11+0.4", "roar", peak=0.8, up=1.0, hold=2.4, down=1.0)
cue("L25.1", "roar", peak=1.0, up=0.6, hold=8.4, down=1.0)
cue("L33", "roar", peak=1.0, up=0.6, hold=9.0, down=1.0)
cue("L41", "roar", peak=1.0, up=0.6, hold=8.7, down=1.0)
cue("L49.3", "roar", peak=1.0, up=0.8, hold=9.3, down=0.8)
cue("L56", "roar", peak=0.9, up=0.5, hold=0.6, down=1.0)
cue("L66", "roar", peak=0.8, up=0.5, hold=0.8, down=0.8)
cue("end-1.2", "roar", peak=0.45, up=0.3, hold=0.1, down=0.75)
# the Loose One
cue(0, "cre", pose="hidden")
cue("L05.1", "cre", pose="scatter", pos=SC1, yaw=-45, s=1.0, alpha="roar", key=1500)
cue("L06", "cre", pose="hidden")
cue("L27", "cre", pose="scatter", pos=SC1, yaw=-45, s=1.0, alpha="roar", key=1500)
cue("L31", "cre", pose="hidden")
cue("L34", "cre", pose="scatter", pos=FAR, yaw=YAW_FAR, s=0.5, alpha="roar", key=900)
cue("L35", "cre", pose="off", pos=FAR, yaw=YAW_FAR, s=0.04, alpha="roar", key=900)
cue("L40", "cre", pose="hidden")
cue("L42", "cre", pose="exact", pos=NEAR, yaw=YAW_NEAR, alpha="roar", key=240)
cue("L48", "cre", pose="hidden")
cue("L50", "cre", pose="exact", pos=p3(D4), yaw=0, alpha=1.0, key=30, kfloor=0.5, rim=110, bounce=260,
    head=[0, 0, 0, 0], arms=[0, 0])
cue("L57", "cre", pose="exact", pos=p3(D4), yaw=0, alpha=1.0, key=30, kfloor=0.5, rim=110, bounce=260,
    head=[0, 0, 0, -44], arms=[0, 0])
cue("L71", "cre", pose="hidden")
# the plants
cue(0, "flasks", state="corner")
cue("L13", "flasks", state="none")
cue("L14", "flasks", state="rim")
cue("L16", "flasks", state="corner")
cue("L78", "flasks", state="end")
cue(0, "bag", state="tied")
cue("L13", "bag", state="none")
cue("L18", "bag", state="tied")
cue("L79", "bag", state="grass")
cue("L81", "bag", state="none")
cue(0, "satchel", on=False)
cue("L14", "satchel", on=True)
cue("L78", "satchel", on=False)
cue(0, "cup", on=False)
cue("L23", "cup", on=True, y=-0.12)
cue("L23+0.3", "cup", y=0.8, dur=1.7)
cue("L26", "cup", on=False)
cue(0, "phone", on=False)
cue("L72", "phone", on=True)
cue("L77", "phone", on=False)

# ---------------------------------------------------------------------------------------------------- sound
sfx = [
    {"at": "L05", "kind": "burner", "db": -13, "dur": 3.0, "seed": 1},
    {"at": "L11+0.4", "kind": "burner", "db": -17, "dur": 4.4},
    {"at": "L25.1", "kind": "burner", "db": -15, "dur": 10.0},
    {"at": "L33", "kind": "burner", "db": -15, "dur": 11.0},
    {"at": "L41", "kind": "burner", "db": -15, "dur": 10.6},
    {"at": "L49.3", "kind": "burner", "db": -9, "dur": 10.4, "keep": True},
    {"at": "L56", "kind": "burner", "db": -13, "dur": 2.2},
    {"at": "L66", "kind": "burner", "db": -16, "dur": 2.2},
    {"at": "end-1.15", "kind": "burner", "db": -18, "dur": 1.05, "fall": 7.0},
    {"at": "L04", "kind": "creak", "db": -22, "dur": 1.2},
    {"at": "L16", "kind": "creak", "db": -26, "dur": 0.8},
    {"at": "L23+0.2", "kind": "creak", "db": -24, "dur": 1.4},
    {"at": "L40", "kind": "creak", "db": -12, "dur": 1.0, "keep": True},
    {"at": "L48", "kind": "creak", "db": -16, "dur": 1.6},
    {"at": "L50", "kind": "sting", "db": -10, "keep": True},
    {"at": "L64", "kind": "bell", "db": -26},
]
story = {
    "slug": "ep31-dawn-flight",
    "title": "The pilot said there was zero wind, so why was our balloon basket tilting?",
    "made_for_kids": False,
    "premise": "On Dad's sixtieth birthday we fly a hot-air balloon at dawn over a sea of mist. The pilot says the wind is zero, but the basket keeps leaning toward its empty fourth corner, and each time the burner roars a figure made of loose copper and slate-blue blocks is nearer and more put together.",
    "twist": "I told Dad my brother couldn't come but never asked him. The basket was built for four and I left a corner empty on purpose, so the figure was the corner's Keeper standing in the gap I made. When I confess and my brother comes the next dawn, the basket flies level.",
    "world": "a hot-air balloon basket at sunrise over a valley of thick white mist, a cold dark launch field before it, a kitchen table the night before",
    "voice": {"voice": "am_adam", "tempo": 1.03, "rate": 1.45},
    "key_color": "#ff7e6b",
    "gap": 0.12,
    "tail": 0.9,
    "look": {"fog": "#9d92b4", "fog_density": 0.0055, "fog_start": 14.0, "sky": "#8a6a92", "exposure": 0.0},
    "grade": {"shadows": [-0.01, 0.0, 0.05], "highlights": [0.03, 0.01, -0.03], "saturation": 1.0, "contrast": 1.04,
              "vignette": 0.3, "bloom": 0.28, "grain": 0.011},
    "phonemes": {},
    "cast": cast,
    "lines": lines,
    "shots": shots,
    "acting": acting,
    "cues": cues,
    "fx": [],
    "music": {"root": 50, "mode": "major", "bpm": 70, "seed": 31,
              "sections": [
                  {"at": 0, "voices": ["pad", "pulse"], "energy": 0.3},
                  {"at": "L25", "voices": ["pad", "drone"], "energy": 0.4, "mode": "minor"},
                  {"at": "L48", "voices": ["drone", "choir"], "energy": 0.55, "mode": "minor"},
                  {"at": "L59", "voices": ["pad", "drone"], "energy": 0.3, "mode": "minor"},
                  {"at": "L64", "voices": ["pad", "piano", "pulse"], "energy": 0.45, "mode": "major"},
                  {"at": "L78", "voices": ["pad", "piano"], "energy": 0.4, "mode": "major"},
              ]},
    "sound": {"floor": "wood", "steps_db": -24,
              "ambience": [
                  {"kind": "room", "from": 0, "to": "end", "lufs": -38},
                  {"kind": "wind", "from": "L06", "to": "L20", "lufs": -44},
              ],
              "sfx": sfx,
              "music_drops": [{"from": "P01", "to": "L50", "keep": ["sting", "burner"]},
                              {"from": "P02-0.1", "to": "L59", "keep": ["burner"]}]},
}
OUT.write_text(json.dumps(story, indent=1, ensure_ascii=False) + "\n")
print("wrote", OUT, f"({len(shots)} shots)")
