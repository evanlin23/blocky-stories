"""Writes ../story.json for ep53 "Car boot" (script by the writer, 2026-11-02).

Run from anywhere: python stories/ep53-car-boot/generator/make_story.py
The words are in lines.json next to this file. Everything else is here: the cast, the shots and their cameras, the
acting, the cues set.py reads (time of day, coat colours, goods, vehicles, lamps), the score and the sound.

Places are set.py's metres. A character with yaw 0 faces -y, yaw 90 faces +x, yaw 180 faces +y. Our stall is at the
origin (table (0, 0), chairs at y = 1.45: Pip's at x = -0.65, mine at +0.65; customers stand at y = -0.7). Row A runs
along x at y = 2.4 (stalls every 4.6 m). The aisle runs down to the hedge at y = -16 with the gate at x = -16, and the
lane climbs from there along -y past the bus shelter at (-13.7, -28). Kitchen x = 100, bedroom x = 130, the coach
window x = 160, the house front x = 260.
"""
import json
import math
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE.parent / "story.json"
lines = json.loads((HERE / "lines.json").read_text())

# captions show two or three words: a longer chunk of the script is split in two, and a reference to a chunk of the
# script's numbering ("L02.2") is moved to the same words in the split lines
CHUNK_MAP = {}
for ln in lines:
    out = []
    for k, (cap, said) in enumerate(ln["chunks"]):
        cw, sw = cap.split(), said.split()
        CHUNK_MAP[(ln["id"], k)] = len(out)
        n = len(cw)
        if n <= 3:
            out.append([cap, said])
        else:
            a = (n + 1) // 2
            out.append([" ".join(cw[:a]), " ".join(sw[:a])])
            out.append([" ".join(cw[a:]), " ".join(sw[a:])])
    ln["chunks"] = out


def remap(x):
    import re
    if isinstance(x, str):
        m = re.match(r"^(L\d+)\.(\d+)(.*)$", x)
        if m and (m.group(1), int(m.group(2))) in CHUNK_MAP:
            return f"{m.group(1)}.{CHUNK_MAP[(m.group(1), int(m.group(2)))]}{m.group(3)}"
        return x
    if isinstance(x, list):
        return [remap(v) for v in x]
    if isinstance(x, dict):
        return {k: (remap(v) if k in ("at", "from", "to") else (remap(v) if isinstance(v, (dict, list)) else v)) for k, v in x.items()}
    return x


# ------------------------------------------------------------------------------------------------ pauses and holds
PAUSES = {"L26": ("P01", 0.7), "L43": ("P02", 0.6)}
HOLDS = {"L57": 0.5, "L70": 0.75}
full = []
for ln in lines:
    if ln["id"] in HOLDS:
        ln["gap"] = HOLDS[ln["id"]]
    full.append(ln)
    if ln["id"] in PAUSES:
        pid, dur = PAUSES[ln["id"]]
        full.append({"id": pid, "pause": dur, "chunks": []})
LOOP = 0.25
full.append({"id": "P03", "pause": LOOP, "chunks": []})
lines = full
SPOKEN = {}
for ln in lines:
    for k, ch in enumerate(ln.get("chunks", [])):
        if (ln["id"], k) in SPOKEN:
            ch[1] = SPOKEN[(ln["id"], k)]

# ------------------------------------------------------------------------------------------------ cast
def person(shirt, skin="#e0b48c", hair="cap", hair_c="#3a2a1e", pants="#2b3445", shoes="#1a1a1c", face=None, coat=True,
          extras=(), **kw):
    ex = (["coat"] if coat else []) + list(extras)
    d = {"age": "adult", "skin": skin, "shirt": shirt, "pattern": "solid", "pants": pants, "shoes": shoes,
         "sleeves": "long", "hair": hair, "hair_c": hair_c, "hat": "none", "extras": ex,
         "face": face or {"eyes": "round", "brows": True, "ink": "#161012"}}
    d.update(kw)
    return d


cast = {
    "me": person("#e6e3da", "#e0b48c", "cap", "#3a2a1e", extras=["hooddown"], zip_c="#b9b5a8"),
    "pip": person("#58aee0", "#f0c8a4", "long", "#b0572b", pants="#6b5a40", shoes="#6a3a2a",
                  face={"eyes": "lashes", "brows": True, "ink": "#1a1214", "bags": True}),
    "haggler": person("#4a90d9", "#d9a47c", "none", pants="#3b3a36", shoes="#2a2a2a", width=1.18,
                      face={"eyes": "round", "brows": True, "ink": "#1c1411"}),
    "sofa_a": person("#e86aa0", "#c98c64", "cap", "#2a1c14"),
    "sofa_b": person("#8456c8", "#f1c9a0", "bun", "#6a3a1e", face={"eyes": "lashes", "brows": True, "ink": "#161012"}),
    "walter": person("#7a5230", "#e3bd9c", "none", pants="#4a463e", height=0.96,
                     face={"eyes": "tired", "brows": True, "ink": "#1c1613"}),
    "buyer": person("#8658c9", "#d6a27c", "cap", "#1c1612"),
    "seller": person("#f0902b", "#e8c09c", "cap", "#5a3a22", face={"eyes": "round", "brows": True, "ink": "#161012"}),
    "white_seller": person("#e7e4db", "#e8c8a8", "none", pants="#5a5a60",
                           face={"eyes": "round", "brows": True, "ink": "#161012"}, extras=["glasses"]),
    "bg1": person("#f2c231", "#c98c64", "cap", "#2a1c14", height=1.02),
    "bg2": person("#2fb3a4", "#e8c09c", "spiky", "#7a4a2a"),
    "bg3": person("#e86aa1", "#8c5c40", "long", "#1c1612", face={"eyes": "lashes", "brows": True, "ink": "#161012"}),
    "bg4": person("#47a9d7", "#f1c9a0", "cap", "#8a6a3a", height=0.97),
    "tilted": {"age": "adult", "height": 1.7, "body_width": 0.82, "skin": "#8a7556", "shirt": "#85533a", "pattern": "solid", "pants": "#7a4a30",
               "shoes": "#2a2420", "sleeves": "long", "hair": "none", "hat": "none", "extras": [],
               "face": {"eyes": "round", "brows": False, "ink": "#0a0807", "pupil": "#050404", "mouth": "line",
                        "eye_scale": 1.35, "reflect": "#e6e3da"}},
}

# ------------------------------------------------------------------------------------------------ cameras
def c(*keys):
    return [list(k) for k in keys]


def still(loc, tgt, lens, roll=0):
    return c([0, loc, tgt, lens, roll])


def move(a, b, lens_a, lens_b=None, roll=0):
    return c([0, a[0], a[1], lens_a, roll], [1, b[0], b[1], lens_b or lens_a, roll])


def yaw_to(a, b):
    return round(math.degrees(math.atan2(b[0] - a[0], -(b[1] - a[1]))), 1)


SZ = -0.045                  # hips on a camp chair
KC = 100.0                   # kitchen x
BC = 130.0                   # bedroom x
STALL_ME = (0.65, 0.8)
CHAIR = (-0.65, 1.3)         # where Pip sits (a hair forward of the chair centre)
HAG = (-9.5, -0.65)
SHELTER_P = (-13.25, -28.3)  # Pip on the bench
LANE = -15.6

# (at, what, step, camera)
SHOTS = [
    # 01 the rule, L01 to L10 ------------------------------------------------------------------------------------
    (0, "the haggler at the lamp stall, face big, coat fading blue to orange", 2,
     move(([-10.55, 1.95, 1.72], [-9.55, -0.65, 1.55]), ([-10.4, 1.9, 1.72], [-9.55, -0.65, 1.55]), 32)),
    ("L02", "close on his sleeve finishing the fade", 2, still([-8.6, -1.5, 1.3], [-9.5, -0.65, 1.2], 32)),
    ("L02.3+0.25", "his face, sheepish, the lamp back on the table", 2, still([-10.2, 1.2, 1.7], [-9.5, -0.65, 1.56], 34)),
    ("L03", "high wide over the row: thirty boots open, flat bright coats", 4,
     move(([-8.0, -9.0, 8.5], [4.0, 3.0, 0.6]), ([-5.0, -8.0, 8.2], [5.0, 3.0, 0.6]), 24)),
    ("L04", "the green sofa: the couple sitting, coats mid-fade", 2, still([11.0, -9.0, 1.4], [11.0, -4.6, 1.15], 26)),
    ("L04.1", "the couple standing beside it, other colours, mid-fade", 2, still([13.6, -9.0, 1.5], [13.0, -4.6, 1.2], 26)),
    ("L05", "Walter behind single shoes, sun on his moustache", 2, still([8.55, -1.0, 1.55], [9.2, 0.9, 1.5], 36)),
    ("L06", "over a seller's shoulder: the buyer's coat drifting violet to pink", 2,
     still([5.05, 2.0, 1.72], [4.6, -0.7, 1.4], 30)),
    ("L07", "the white seller, same cream as mine, worried over one teapot", 2, still([-23.6, -0.9, 1.52], [-23.0, 0.9, 1.45], 34)),
    ("L08", "he picks a price and goes yellow", 2, still([-23.6, -0.9, 1.52], [-23.0, 0.9, 1.45], 34)),
    ("L09", "me behind our table, cream anorak, the estate behind", 2, still([0.15, -1.7, 1.55], [0.65, 0.8, 1.5], 30)),
    ("L10", "me to a customer across the table, smug", 2, still([1.0, -2.0, 1.62], [0.65, 0.8, 1.5], 34)),
    # 02 Pip, L11 to L24 ----------------------------------------------------------------------------------------
    ("L11", "Pip in her chair, sky-blue duffle, laughing, a teapot held up", 2, still([-0.2, -1.3, 1.5], [-0.65, 1.3, 1.4], 30)),
    ("L12", "wide: the estate, the table, the two chairs, flask and mugs", 2, still([-3.3, -4.4, 1.9], [0.0, 1.6, 0.95], 24)),
    ("L13", "kitchen: Pip with the plain envelope, coat flaring toward green", 2, still([KC + 0.9, 1.6, 1.4], [KC, -1.1, 1.2], 32)),
    ("L14", "Pip with toast, green", 2, still([KC - 0.9, 0.3, 1.25], [KC, -1.1, 1.15], 36)),
    ("L14.1", "Pip at the sink, fading to purple", 2, still([KC + 0.15, 0.1, 1.45], [KC - 1.2, 1.15, 1.3], 32)),
    ("L14.2", "Pip on her bed, fading to orange", 2, still([BC + 0.6, -1.95, 1.2], [BC - 0.6, -0.15, 1.1], 26)),
    ("L15", "Pip by the window, her coat drifting through two colours", 2,
     move(([KC + 0.0, -1.7, 1.4], [KC + 1.2, 1.2, 1.3]), ([KC + 0.4, -1.7, 1.4], [KC + 1.2, 1.2, 1.3]), 28)),
    ("L16", "Pip across the table, worried, eyes on me", 2, still([KC + 0.7, 1.0, 1.35], [KC, -1.1, 1.25], 36)),
    ("L17", "me, smiling, shrugging, mug in front", 2, still([KC - 0.9, -1.8, 1.4], [KC, 0.7, 1.35], 34)),
    ("L18", "close on my cream sleeve on the table: nothing changes", 2,
     move(([KC + 0.8, -0.7, 1.3], [KC + 0.1, 0.5, 1.0]), ([KC + 0.7, -0.6, 1.25], [KC + 0.1, 0.5, 1.0]), 32)),
    ("L19", "Pip in the doorway, coat fading to flat grey", 2, still([KC - 0.5, -0.3, 1.45], [KC - 2.5, -0.8, 1.4], 30)),
    ("L20", "unpriced junk heaped in a box", 2, still([BC + 1.8, -1.8, 1.3], [BC + 0.9, -0.6, 0.4], 26)),
    ("L20.1", "Pip sitting up in bed in the dark-blue night, the grey coat round her", 2, still([BC - 1.0, -1.5, 1.3], [BC - 0.6, 1.2, 1.1], 34)),
    ("L21", "the stall in sun: Pip far off by the hedge in grey, looking up the lane", 2,
     still([-9.0, -6.8, 1.35], [-13.8, -14.4, 1.3], 40)),
    ("L21.1", "her chair empty behind the table", 2, still([-1.9, -1.2, 1.05], [-0.65, 1.4, 0.7], 28)),
    ("L22", "overhead: every thing on the table turned toward the left chair", 2, still([0.0, 0.05, 2.75], [0.0, 0.0, 0.8], 24, 90)),
    ("L23", "the old radio, dial lamp ramping on", 2, still([-0.1, -0.95, 1.25], [-0.95, 0.1, 0.95], 38)),
    ("L24", "three mugs on the tailgate, the third cold", 2, still([1.5, 2.0, 1.45], [0.0, 2.5, 1.08], 34)),
    # 03 dawn, L25 to L42 ----------------------------------------------------------------------------------------
    ("L25", "the estate pulling away from a plain house front, tail lights steady", 2,
     still([266.0, -14.0, 1.4], [260.0, -4.0, 1.2], 30)),
    ("L26", "me at the field gate, fog thickening; down the row, our stall, both chairs empty", 2,
     still([-16.5, -15.9, 1.72], [-5.0, -4.0, 1.0], 30)),
    ("P01", "hold on the empty stall in fog", 4, still([-1.0, -5.5, 1.45], [0.0, 1.2, 0.95], 26)),
    ("L27", "Pip's duffle laid flat on the table, nobody in it", 2, still([-0.15, 0.1, 2.75], [-0.15, 0.1, 0.8], 24, 90)),
    ("L28", "close: the coat fading grey to violet and back", 2, still([-0.25, -1.2, 1.5], [-0.15, 0.0, 0.8], 34)),
    ("L29", "wide from behind me: fog over the rows, my white coat brightest", 2, still([0.9, -0.35, 1.9], [-3.5, -12.0, 1.1], 24)),
    ("L30", "the radio clicks on", 2, still([-0.1, -0.95, 1.25], [-0.95, 0.1, 0.95], 38)),
    ("L31", "low across the table: all turned to her chair, half hidden in fog", 2,
     still([1.5, -0.9, 0.98], [-0.65, 1.4, 0.8], 30)),
    ("L32", "from the hedge, long lens: a dark seated silhouette in her chair", 4, still([-12.0, -8.0, 1.3], [-0.7, 1.3, 1.3], 75)),
    ("L33", "tighter: the sideways head, the only clear thing", 4, still([-5.5, -7.0, 1.3], [-0.9, 1.3, 1.5], 70)),
    ("L34", "the same angle: the chair is empty", 4, still([-5.5, -7.0, 1.3], [-0.9, 1.3, 1.5], 70)),
    ("L35", "a strip of tarp-green canvas on the chair arm", 2, still([-1.15, 0.7, 0.75], [-0.98, 1.35, 0.42], 40)),
    ("L35.2", "I carry Pip's coat over my arm", 2, still([0.3, -1.7, 1.5], [-0.35, -0.5, 1.2], 30)),
    ("L36", "the bus shelter in fog: Pip on the bench, tired, her coat over my arm", 2,
     still([-18.2, -22.5, 1.5], [-14.0, -27.8, 1.0], 30)),
    ("L37", "Pip in her jumper, a holdall at her feet; a bus's headlamps come up behind", 2,
     still([-17.9, -30.3, 1.3], [-13.4, -28.4, 1.0], 32)),
    ("L38", "the bus pulling away up the lane without her", 2, still([-18.7, -26.0, 1.8], [-16.2, -36.5, 1.4], 28)),
    ("L39", "Pip's face, worried, looking up at me", 2, still([-16.6, -26.6, 1.5], [-13.25, -28.3, 1.1], 32)),
    ("L40", "me, worried, my coat flat and still", 2, still([-15.9, -26.0, 1.5], [-15.0, -28.3, 1.5], 34)),
    ("L41", "Pip settles back; I lay her coat on the bench", 2, still([-15.5, -26.2, 1.3], [-13.3, -28.4, 0.95], 34)),
    ("L42", "me from behind, walking down the lane into the fog", 2, still([-15.8, -31.5, 1.7], [-15.8, -24.0, 1.3], 30)),
    # 04 the Tilted, L43 to L57 ---------------------------------------------------------------------------------
    ("L43", "wide: fog thinning off the rows, gold sun coming through", 4,
     move(([-9.0, -13.0, 1.9], [2.0, -2.0, 0.9]), ([-9.0, -12.5, 1.9], [2.0, -2.0, 0.9]), 24)),
    ("P02", "me at the end of our row, stopped", 4, still([-6.3, -4.6, 1.7], [0.0, 1.2, 1.2], 26)),
    ("L44", "clearly lit: the Tilted in Pip's chair behind our stall, head on its shoulder", 2,
     still([0.3, -4.4, 0.95], [-0.95, 1.3, 1.7], 29)),
    ("L45", "full figure seated", 2, still([0.05, -2.6, 1.2], [-0.65, 1.3, 1.1], 30)),
    ("L45.1", "close on the tarp knotted at its chest, the rust overalls", 2, still([-0.2, -0.5, 1.2], [-0.65, 1.3, 1.05], 44)),
    ("L46", "close on its face: two stacked eyes, the mouth beside them", 2, still([0.05, -0.1, 1.5], [-0.95, 1.3, 1.5], 32)),
    ("L47", "its tarp in the sun, never shifting", 2, still([-2.2, -0.6, 1.4], [-0.95, 1.3, 1.4], 36)),
    ("L47.2", "my cream sleeve in the same light", 2, still([-1.9, -1.45, 1.2], [-1.25, -0.6, 1.15], 40)),
    ("L48", "me a step nearer, scared", 2, still([-2.4, -1.7, 1.5], [-0.65, -1.75, 1.5], 34)),
    ("L48.2", "its head hanging below the shoulder line, eyes still on me", 2, still([0.3, -3.1, 1.3], [-0.8, 1.3, 1.2], 36)),
    ("L49", "the tipped face, held, as Pip's at the shelter", 2, still([-0.1, -1.8, 1.25], [-0.85, 1.3, 1.25], 36)),
    ("L50", "side-on: it leans over the table, face to face with me", 2, still([-5.2, 0.3, 1.6], [-1.5, 0.3, 1.55], 18)),
    ("L51", "extreme close on its stacked eyes", 2, still([-2.3, -0.3, 1.32], [-1.82, 0.46, 1.54], 32)),
    ("L52", "my face, scared turning to worried", 2, still([0.9, 0.3, 1.55], [-1.45, -0.62, 1.5], 34)),
    ("L53", "my sleeve, still white, gold sun on it", 2, still([-1.6, -1.4, 1.25], [-1.2, -0.62, 1.2], 42)),
    ("L54", "me in the foreground, and far down the row the white seller's cream coat", 2,
     still([5.6, -1.2, 1.6], [-23.0, 0.9, 1.4], 34)),
    ("L55", "me, worried, looking down at my coat", 2, still([0.8, -0.3, 1.6], [-0.65, -0.62, 1.35], 36)),
    ("L56", "Pip at the shelter, her grey coat beside her, looking down the lane", 2,
     still([-17.0, -27.8, 1.3], [-13.25, -28.3, 1.0], 32)),
    ("L57", "me running toward the gate, the Tilted small in the background", 2, still([-16.0, -14.2, 1.45], [-6.0, -3.0, 1.2], 30)),
    # 05 go, L58 to L68 -----------------------------------------------------------------------------------------
    ("L58", "wide up the lane: a bus pulling in, headlamps coming up, Pip standing with her bag", 2,
     still([-18.4, -19.5, 1.7], [-14.2, -32.0, 1.3], 26)),
    ("L59", "me arriving, out of breath", 2, still([-14.2, -31.6, 1.6], [-15.6, -24.0, 1.3], 26)),
    ("L60-0.45", "me to Pip: Go, I'll be fine", 2, still([-16.7, -26.8, 1.55], [-14.6, -28.3, 1.45], 30)),
    ("L60.2", "Pip's face easing", 2, still([-15.7, -27.6, 1.55], [-14.0, -28.3, 1.5], 38)),
    ("L61", "my anorak fills with colour for the first time", 2,
     move(([-15.9, -25.6, 1.5], [-15.0, -28.3, 1.45]), ([-15.4, -25.9, 1.5], [-15.0, -28.3, 1.45]), 34)),
    ("L62", "Pip in her duffle: grey melts into marigold", 2, still([-17.4, -23.8, 1.6], [-14.5, -28.2, 1.2], 26)),
    ("L63", "Pip laughing, the bus pulling away behind her", 2, still([-17.0, -26.5, 1.55], [-14.4, -28.3, 1.55], 34)),
    ("L64", "the stall in full sun: Pip drops into her chair", 2, still([-2.2, -2.8, 1.3], [-0.65, 1.2, 1.0], 28)),
    ("L65", "Pip in the chair, no tarp on the arm, the goods facing every which way", 2, still([-1.9, -0.9, 1.0], [-0.75, 1.3, 0.9], 34)),
    ("L66", "the holdall in the boot, me beside it", 2, still([2.9, 2.0, 1.45], [0.2, 3.0, 1.15], 28)),
    ("L67", "the cream estate climbing the lane in morning sun", 2, still([-15.8, -13.0, 1.4], [-16.0, -46.0, 4.0], 34)),
    ("L68", "Pip at a coach window in marigold, happy tears", 2, still([160.2, -1.7, 1.3], [161.0, 0.0, 1.2], 34)),
    ("L68.2", "the coach going over the brow of the hill, small", 2, still([-16.0, -29.0, 1.8], [-16.0, -96.0, 8.0], 44)),
    # 06 one chair, L69 to L75 -----------------------------------------------------------------------------------
    ("L69", "the stall in flat light: me in blue, Pip's chair empty", 2, still([0.2, -2.4, 1.5], [0.1, 1.0, 1.1], 28)),
    ("L70", "the chair folded in the boot", 2, still([0.5, 1.7, 1.5], [-0.3, 3.2, 1.1], 32)),
    ("L70.1", "the tailgate coming down", 2, still([1.9, 1.3, 1.5], [0.0, 2.6, 1.3], 28)),
    ("L70.2", "the latch: two short upright strokes", 2, still([0.0, 1.55, 1.1], [0.0, 2.31, 1.09], 46)),
    ("L71", "wide: one chair, one table, me alone, cars along the row", 2, still([-0.4, -3.9, 1.5], [0.5, 1.0, 1.1], 22)),
    ("L72", "me looking at the shut tailgate", 2, still([2.3, 1.7, 1.5], [0.3, 1.7, 1.4], 34)),
    ("L73", "slow push on the closed boot", 2,
     move(([0.3, -1.6, 1.4], [0.0, 2.4, 1.1]), ([0.1, -0.2, 1.35], [0.0, 2.4, 1.1]), 28, 34)),
    ("L74", "mid close on me, the haggler's framing, my blue coat flat", 2, still([-0.7, 1.9, 1.7], [0.2, -0.65, 1.55], 32)),
    ("L75", "close on my face, neutral", 2, still([-0.1, 1.7, 1.58], [0.2, -0.65, 1.56], 40)),
    ("L75>", "hold on the shut tailgate", 2, still([0.0, -1.5, 1.2], [0.0, 2.4, 1.2], 30)),
]

shots = []
for i, (at, what, step, cam) in enumerate(SHOTS):
    s = {"id": f"S{i + 1:02d}", "cam": cam, "hand": 0.004 if step == 4 else 0.006, "step": step, "what": what}
    if i:
        s["at"] = at
    shots.append(s)

# ------------------------------------------------------------------------------------------------ acting
NEUTRAL = {"arms": [0, 0], "side": [0, 0], "head": [0, 0], "lean": 0, "tremble": 0, "blink": True, "sit": False}
acting = {w: [] for w in cast}


def put(who, at, pos, **kw):
    keys = acting[who]
    prev = next((k["pos"] for k in reversed(keys) if "pos" in k), None)
    if prev is not None:
        keys.append({"at": at, "pos": prev})
    keys.append({"at": at, "pos": pos, "blend": 0, "hidden": False, **NEUTRAL, "expr": "neutral", **kw})


def walk(who, at, pos, **kw):
    acting[who].append({"at": at, "pos": pos, **kw})


def key(who, at, **kw):
    acting[who].append({"at": at, **kw})


def hide(who, at):
    acting[who].append({"at": at, "hidden": True, "blend": 0})


def at_stall(who, x, y, expr="neutral", **kw):
    put(who, 0, [x, y], yaw=0, expr=expr, **kw)


for w in cast:
    hide(w, 0)

# the sellers along row A are there all film
for w, (x, y) in {"bg1": (-18.1, 0.9), "bg2": (-8.55, 0.85), "bg3": (-4.9, 0.9), "bg4": (14.1, 0.9),
                  "white_seller": (-23.0, 0.9), "walter": (9.2, 0.9), "seller": (4.2, 0.9)}.items():
    put(w, 0, [x, y], yaw=0, expr="neutral")
key("walter", 0, arms=[58, 58], side=[-28, -28], blend=0)
key("white_seller", 0, expr="worried", head=[0, 12], blend=0)
key("white_seller", "L08", expr="smirk", head=[0, 0], blend=0.3)
key("white_seller", "L09", expr="worried", head=[0, 12], blend=0)
key("bg2", 0, expr="neutral", head=[0, 6], blend=0)

# the haggler and the couple
put("haggler", 0, [HAG[0], HAG[1]], yaw=180, arms=[28, 12], head=[0, 12], expr="neutral")
key("haggler", "L02.3+0.25", expr="worried", blend=0.2)
hide("haggler", "L04")
put("sofa_a", "L04", [10.45, -4.55, 0.12], yaw=0, sit=True, expr="smirk")
put("sofa_b", "L04", [11.55, -4.55, 0.12], yaw=0, sit=True, expr="neutral")
put("sofa_a", "L04.1", [12.55, -4.7], yaw=190, expr="neutral")
put("sofa_b", "L04.1", [13.35, -4.6], yaw=170, expr="smirk")
hide("sofa_a", "L05")
hide("sofa_b", "L05")
put("buyer", "L06", [4.6, -0.7], yaw=180, head=[0, 5])
hide("buyer", "L07")
put("buyer", "L10", [-0.45, -0.75], yaw=180)
hide("buyer", "L11")

# me
put("me", "L09", list(STALL_ME), yaw=0, expr="neutral")
key("me", "L10", expr="smirk", blend=0.3)
hide("me", "L11")
put("me", "L17", [KC, 0.7], yaw=0, expr="smirk", side=[18, 18], head=[0, -3])
put("me", "L18", [KC, 0.7], yaw=0, expr="neutral", arms=[42, 42])
hide("me", "L19")
put("me", "L26", [-15.3, -14.9], yaw=yaw_to([-15.3, -14.9], [0, 0]), expr="worried", head=[0, 4])
hide("me", "L27")
put("me", "L29", [0.15, -1.2], yaw=200, expr="worried", head=[0, 6])
hide("me", "L30")
put("me", "L35.2", [-0.35, -0.55], yaw=0, expr="worried", arms=[28, 28])
hide("me", "L36")
put("me", "L36", [-15.3, -26.4], yaw=yaw_to([-15.3, -26.4], SHELTER_P), expr="worried", arms=[40, 40])
hide("me", "L37")
put("me", "L39", [-15.0, -28.3], yaw=90, expr="worried")
put("me", "L40", [-15.0, -28.3], yaw=90, expr="worried")
put("me", "L41", [-14.95, -28.5], yaw=90, expr="worried", arms=[30, 30])
put("me", "L42", [-15.7, -28.3], yaw=180, expr="worried")
walk("me", "L42+2.4", [-15.7, -19.5])
hide("me", "L43")
put("me", "P02", [-4.0, -2.4], yaw=yaw_to([-4.0, -2.4], [0, 1.3]), expr="worried")
put("me", "L48", [-0.65, -1.75], yaw=180, expr="scared", head=[0, 0])
hide("me", "L48.2")
hide("me", "L49")
put("me", "L50", [-1.45, -0.62], yaw=180, expr="scared", lean=16, head=[35, 5])
hide("me", "L51")
put("me", "L52", [-1.45, -0.62], yaw=180, expr="scared", lean=16, head=[0, 5])
key("me", "L52+0.8", expr="worried", blend=0.5)
hide("me", "L53")
put("me", "L53", [-0.65, -0.62], yaw=180, expr="worried", lean=0, arms=[10, 10])
put("me", "L54", [2.0, -0.62], yaw=-90, expr="worried")
put("me", "L55", [-0.65, -0.62], yaw=180, expr="worried", head=[0, 24])
hide("me", "L56")
put("me", "L57", [-7.0, -6.0], yaw=yaw_to([-7.0, -6.0], [-16, -15]), run=True)
walk("me", "L57+1.35", [-15.8, -14.6], run=True)
hide("me", "L58")
put("me", "L59", [-15.6, -22.0], yaw=0, expr="worried", lean=6)
walk("me", "L59+0.7", [-15.6, -26.2])
put("me", "L60-0.45", [-15.0, -28.3], yaw=90, expr="smirk", head=[0, 0])
key("me", "L61", expr="smirk")
key("me", "L62", expr="smirk")
hide("me", "L63")
put("me", "L66", [0.95, 2.1], yaw=yaw_to([0.95, 2.1], [0.0, 3.1]), expr="smirk", arms=[20, 20])
hide("me", "L67")
put("me", "L69", list(STALL_ME), yaw=0, expr="neutral")
hide("me", "L70")
put("me", "L71", [0.65, 1.3, SZ], yaw=0, sit=True, expr="neutral")
put("me", "L72", [0.35, 1.45], yaw=180, expr="worried")
hide("me", "L73")
put("me", "L74", [0.2, -0.65], yaw=180, expr="neutral")
put("me", "L75", [0.2, -0.65], yaw=180, expr="neutral")

# Pip
put("pip", "L11", [CHAIR[0], CHAIR[1], SZ], yaw=0, sit=True, expr="smirk", arms=[80, 80], head=[0, -4])
acting["pip"].append({"from": "L11", "to": "L11>", "mouth": [0.5, 0.5], "flap": True})
hide("pip", "L12")
put("pip", "L13", [KC, -1.1, SZ], yaw=180, sit=True, expr="worried", arms=[40, 40])
put("pip", "L14", [KC, -1.1, SZ], yaw=180, sit=True, expr="worried", arms=[30, 30])
put("pip", "L14.1", [KC - 1.2, 1.15], yaw=180, expr="worried", arms=[30, 30])
put("pip", "L14.2", [BC - 0.6, -0.15, -0.09], yaw=0, sit=True, expr="worried")
put("pip", "L15", [KC + 1.2, 1.15], yaw=170, expr="worried", head=[-18, 0])
put("pip", "L16", [KC, -1.1, SZ], yaw=180, sit=True, expr="worried", head=[0, 4])
put("pip", "L19", [KC - 2.4, -0.8], yaw=90, expr="worried", head=[0, 8])
hide("pip", "L20")
put("pip", "L20.1", [BC - 0.6, 1.1, -0.09], yaw=0, sit=True, expr="worried")
put("pip", "L21", [-13.8, -14.2], yaw=0, expr="worried", head=[0, -6])
hide("pip", "L22")
put("pip", "L36", [SHELTER_P[0], SHELTER_P[1], 0.03], yaw=-90, sit=True, expr="worried", head=[0, 6])
key("pip", "L41", head=[0, 14], blend=0.5)
put("pip", "L58", [-14.25, -28.0], yaw=-90, expr="worried")
put("pip", "L60-0.45", [-14.1, -28.3], yaw=-90, expr="worried")
key("pip", "L60.2", expr="neutral", blend=0.8)
put("pip", "L62", [-14.1, -28.3], yaw=-90, expr="smirk")
put("pip", "L63", [-14.4, -28.3], yaw=-90, expr="smirk")
acting["pip"].append({"from": "L63", "to": "L63>", "mouth": [0.55, 0.55], "flap": True})
put("pip", "L64", [-1.9, 0.8], yaw=60, expr="smirk")
walk("pip", "L64+0.85", [CHAIR[0], 1.45, SZ])
key("pip", "L64+0.86", sit=True, yaw=0)
key("pip", "L66", expr="smirk")
hide("pip", "L67")
put("pip", "L68", [161.05, 0.0, SZ], yaw=0, sit=True, expr="soft", side=[0, 70])

# the Tilted
put("tilted", "L32", [CHAIR[0], CHAIR[1], SZ], yaw=0, sit=True, expr="scared", blink=False, arms=[45, 45], side=[8, 8])
hide("tilted", "L34")
put("tilted", "L44", [CHAIR[0], CHAIR[1], SZ], yaw=0, sit=True, expr="scared", blink=False, arms=[14, 14], side=[6, 6])
put("tilted", "L50", [CHAIR[0], 1.0, SZ], yaw=0, sit=True, expr="scared", blink=False, arms=[-30, -30], side=[10, 10])
hide("tilted", "L56")
put("tilted", "L57", [CHAIR[0], 1.05, SZ], yaw=0, sit=True, expr="scared", blink=False, arms=[-45, -45], side=[10, 10])
hide("tilted", "L58")

# ------------------------------------------------------------------------------------------------ cues
BLUE, ORANGE = "#4a90d9", "#f0902b"
cues = [
    # time of day: every change at a cut, or a slow ramp (dur)
    {"at": 0, "name": "tod", "set": "day"},
    {"at": "L13", "name": "tod", "set": "inside"},
    {"at": "L21", "name": "tod", "set": "day"},
    {"at": "L25", "name": "tod", "set": "dawn"},
    {"at": "L26+0.05", "name": "tod", "set": "dawn"},
    {"at": "L26+0.1", "name": "tod", "set": "fog", "dur": 4.0},
    {"at": "L32", "name": "tod", "set": "sil"},
    {"at": "L34", "name": "tod", "set": "fog"},
    {"at": "L43", "name": "tod", "set": "gold", "dur": 3.0},
    {"at": "L58", "name": "tod", "set": "morn"},
    {"at": "L68", "name": "tod", "set": "morn"},
    {"at": "L69", "name": "tod", "set": "flat"},
    # coats: a colour change is always a fade of a second or more (dur 0 is only ever across a cut)
    {"at": 0, "name": "coat", "who": "haggler", "to": BLUE, "dur": 0},
    {"at": "L02.1", "name": "coat", "who": "haggler", "to": ORANGE, "dur": 1.0},
    {"at": "L04", "name": "coat", "who": "sofa_a", "to": "#2fb3a3", "dur": 1.5},
    {"at": "L04+0.1", "name": "coat", "who": "sofa_b", "to": "#f0902a", "dur": 1.4},
    {"at": "L04.1", "name": "coat", "who": "sofa_a", "to": "#f2c230", "dur": 1.3},
    {"at": "L04.1+0.1", "name": "coat", "who": "sofa_b", "to": "#e86aa0", "dur": 1.3},
    {"at": "L06", "name": "coat", "who": "buyer", "to": "#e86aa0", "dur": 1.6},
    {"at": "L08", "name": "coat", "who": "white_seller", "to": "#f2c230", "dur": 1.0},
    {"at": "L09", "name": "coat", "who": "white_seller", "to": "#e7e4db", "dur": 0},
    {"at": "L13+0.3", "name": "coat", "who": "pip", "to": "#4ea35a", "dur": 1.0},
    {"at": "L14.1", "name": "coat", "who": "pip", "to": "#8a5cc4", "dur": 1.0},
    {"at": "L14.2", "name": "coat", "who": "pip", "to": "#f08a2a", "dur": 1.0},
    {"at": "L15", "name": "coat", "who": "pip", "to": "#2fb3a3", "dur": 1.0},
    {"at": "L15+1.0", "name": "coat", "who": "pip", "to": "#e86aa0", "dur": 1.0},
    {"at": "L19+0.1", "name": "coat", "who": "pip", "to": "#8a8d90", "dur": 1.5},
    {"at": "L28", "name": "coat", "who": "pipflat", "to": "#6d5a8c", "dur": 1.0},
    {"at": "L28+1.0", "name": "coat", "who": "pipflat", "to": "#8a8d90", "dur": 1.0},
    {"at": "L36", "name": "coat", "who": "pip", "to": "#d9a62e", "dur": 0},
    {"at": "L61+0.3", "name": "coat", "who": "me", "to": "#2f5fa8", "dur": 2.0},
    {"at": "L62", "name": "coat", "who": "pip", "to": "#8a8d90", "dur": 0},
    {"at": "L62+0.3", "name": "coat", "who": "pip", "to": "#f2b233", "dur": 1.5},
    {"at": 0, "name": "nocoat", "who": "pip", "on": False},
    {"at": "L36", "name": "nocoat", "who": "pip", "on": True},
    {"at": "L62", "name": "nocoat", "who": "pip", "on": False},
    # the stall's goods, the third mug, the tarp strip
    {"at": 0, "name": "goods", "mode": "straight"},
    {"at": "L22", "name": "goods", "mode": "turned"},
    {"at": "L25", "name": "goods", "mode": "straight"},
    {"at": "L27", "name": "goods", "mode": "away"},
    {"at": "L29", "name": "goods", "mode": "straight"},
    {"at": "L31", "name": "goods", "mode": "turned"},
    {"at": "L64", "name": "goods", "mode": "chaos"},
    {"at": "L69", "name": "goods", "mode": "straight"},
    {"at": 0, "name": "mug3", "on": False},
    {"at": "L24", "name": "mug3", "on": True},
    {"at": "L25", "name": "mug3", "on": False},
    {"at": "L31", "name": "mug3", "on": True},
    {"at": "L64", "name": "mug3", "on": False},
    {"at": 0, "name": "tsil", "on": False},
    {"at": "L32", "name": "tsil", "on": True},
    {"at": "L34", "name": "tsil", "on": False},
    {"at": 0, "name": "tarp", "on": False},
    {"at": "L35", "name": "tarp", "on": True},
    {"at": "L64", "name": "tarp", "on": False},
    # Pip's coat, the holdall
    {"at": 0, "name": "pipflat", "where": "off"},
    {"at": "L27", "name": "pipflat", "where": "table", "yaw": 8},
    {"at": "L35.2", "name": "pipflat", "where": "arm"},
    {"at": "L41", "name": "pipflat", "where": "bench"},
    {"at": "L62", "name": "pipflat", "where": "off"},
    {"at": 0, "name": "bag", "where": "off"},
    {"at": "L36", "name": "bag", "where": "shelter"},
    {"at": "L64", "name": "bag", "where": "off"},
    {"at": "L66", "name": "bag", "where": "boot"},
    {"at": "L67", "name": "bag", "where": "off"},
    # lamps: the radio's dial (0.5 s ramps) and the bus headlamps (1 s)
    {"at": "L23", "name": "lamp", "to": 1.0, "dur": 0.5},
    {"at": "L25", "name": "lamp", "to": 0.0, "dur": 0.5},
    {"at": "L30", "name": "lamp", "to": 1.0, "dur": 0.5},
    {"at": "L36", "name": "lamp", "to": 0.0, "dur": 0.6},
    {"at": "L37", "name": "beam", "to": 1.0, "dur": 1.0},
    {"at": "L39", "name": "beam", "to": 0.0, "dur": 0.5},
    # extra fill inside the shelter for the L56 shot (the shelter's own lamp is always on)
    {"at": "L56-0.3", "name": "sfill", "to": 1.0, "dur": 0.3},
    {"at": "L57", "name": "sfill", "to": 0.0, "dur": 0.4},
    # a soft daylight fill on the chair arm for the L35 strip, which sits in the estate's shadow
    {"at": "L35-0.3", "name": "tfill", "to": 1.0, "dur": 0.3},
    {"at": "L35.2", "name": "tfill", "to": 0.0, "dur": 0.4},
    {"at": "L58", "name": "beam", "to": 1.0, "dur": 1.0},
    {"at": "L63+1.5", "name": "beam", "to": 0.0, "dur": 0.8},
    # vehicles: root = the rear of the car; yaw 0 faces +y, yaw 180 faces -y
    {"at": "L25", "name": "veh", "id": "estate2", "p0": [260.0, -0.5], "p1": [260.0, -26.0], "yaw": 180, "dur": 6.0},
    {"at": "L26", "name": "veh", "id": "estate2", "hide": True},
    {"at": "L37", "name": "veh", "id": "bus", "p0": [-16.2, -38.0], "p1": [-16.2, -38.0], "yaw": 0, "dur": 1.0},
    {"at": "L38", "name": "veh", "id": "bus", "p0": [-16.2, -31.0], "p1": [-16.2, -55.0], "yaw": 180, "dur": 4.5},
    {"at": "L39", "name": "veh", "id": "bus", "hide": True},
    {"at": "L58", "name": "veh", "id": "bus", "p0": [-16.2, -56.0], "p1": [-16.2, -38.0], "yaw": 0, "dur": 3.4},
    {"at": "L63", "name": "veh", "id": "bus", "p0": [-16.2, -31.0], "p1": [-16.2, -60.0], "yaw": 180, "dur": 4.0},
    {"at": "L64", "name": "veh", "id": "bus", "hide": True},
    {"at": "L67", "name": "veh", "id": "estate2", "p0": [-16.0, -19.5], "p1": [-16.0, -66.0], "yaw": 180, "dur": 3.4},
    {"at": "L68", "name": "veh", "id": "estate2", "hide": True},
    {"at": "L68.1", "name": "veh", "id": "coach", "p0": [-16.0, -62.0], "p1": [-16.0, -112.0], "yaw": 180, "dur": 3.4},
    # our tailgate comes down at L70.1 (0.9 s), the chair lies folded in the boot, the latch strokes show once
    {"at": "L70.1", "name": "hatch", "to": 0.0, "dur": 0.9},
    {"at": 0, "name": "fold", "on": False},
    {"at": "L70", "name": "fold", "on": True},
    {"at": "L70.1", "name": "fold", "on": False},
    {"at": 0, "name": "strokes", "on": False},
    {"at": "L70.2", "name": "strokes", "on": True},
    {"at": "L71", "name": "strokes", "on": False},
    # the Tilted: roll (head, degrees; -90 lies on its right shoulder), where the head sits, torso lean
    {"at": 0, "name": "tilted", "roll": -125.0, "side": 1.2, "lift": -0.45, "pitch": 8.0, "fwd": -0.55},
    {"at": "L48.2", "name": "tilted", "roll": -135.0, "lift": -0.7, "side": 1.3, "pitch": 10.0, "fwd": -0.55},
    {"at": "L50", "name": "tilted", "roll": -135.0, "lift": -0.6, "side": 1.3, "pitch": 10.0, "lean": -8.0, "fwd": -0.2, "yawh": -38.0},
    # the slow lean over the table: 19 degrees across 1.6 s, no lunge
    {"at": "L50+0.1", "name": "tilted", "roll": -135.0, "lift": -0.6, "side": 1.3, "pitch": 10.0, "lean": 24.0, "fwd": -0.2, "yawh": -38.0, "dur": 1.6},
]
# the fold only shows with the hatch up: the folded chair is "on" at L70 only, and stays in the closed boot unseen

sfx = [
    {"at": "P01+0.15", "kind": "whoosh", "db": -22, "dur": 0.6},
    {"at": "P01+0.4", "kind": "thud", "db": -26},
    {"at": "L27", "kind": "sting", "db": -15},
    {"at": "L30", "kind": "click", "db": -20},
    {"at": "L34", "kind": "click", "db": -24},
    {"at": "L23", "kind": "click", "db": -20},
    {"at": "L37+0.2", "kind": "door", "db": -26, "dur": 0.8},
    {"at": "P02+0.15", "kind": "creak", "db": -6, "dur": 1.0},
    {"at": "L44", "kind": "sting", "db": -13},
    {"at": "L50", "kind": "glide", "db": -17, "dur": 1.6},
    {"at": "L61+0.3", "kind": "bell", "db": -17, "dur": 2.0},
    {"at": "L70.1+0.8", "kind": "door", "db": -12, "dur": 1.0},
    {"at": "L75+0.5", "kind": "glide", "db": -14, "dur": 1.4},
]

story = {
    "slug": "ep53-car-boot",
    "title": "In this town, your coat changes colour when you change your mind.",
    "made_for_kids": False,
    "premise": "My sister and I run a stall off the back of our car at the Sunday car-boot sale, in a town where a coat changes colour when its wearer changes their mind. Mine has been white my whole life. When she is offered a job abroad, hers drifts through every colour for a week and sticks on grey. Everything on our stall turns to face her empty chair, and one foggy dawn her coat lies on the table without her, still changing colour by itself.",
    "twist": "A coat only changes when you change your mind, and you cannot change a mind you never made up. Mine stayed white because I never decided anything, and my sister was stuck on grey waiting on my answer. The first line first reads as a strange law I am proud to be immune to, and after the climax it reads as an accusation.",
    "world": "a sloping Sunday car-boot field of open boots and pasting tables, a hedge and a five-bar gate, a narrow lane climbing a hill past a wooden bus shelter, a small kitchen and bedroom for the week at home",
    "voice": {"voice": "am_adam", "tempo": 1.03, "rate": 1.45},
    "key_color": "#ffb627",
    "caption": {"ink": "#08090d", "stroke_add": 2, "shadow": 0.8},
    "key_stroke": 2,
    "gap": 0.12,
    "tail": 0,
    "look": {"fog": "#b8bcc0", "fog_density": 0.005, "fog_start": 3.0, "sky": "#cfd6e0", "sky_strength": 1.0,
             "exposure": 0.0, "flash_safe": True},
    "grade": {"shadows": [-0.01, 0.0, 0.04], "highlights": [0.03, 0.01, -0.02], "saturation": 1.04, "contrast": 1.05,
              "vignette": 0.3, "bloom": 0.2, "grain": 0.012},
    "phonemes": {},
    "cast": cast,
    "lines": lines,
    "shots": remap(shots),
    "acting": remap(acting),
    "cues": remap(cues),
    "fx": [],
    "music": {"root": 52, "mode": "minor", "bpm": 76, "seed": 53,
              "sections": [
                  {"at": 0, "voices": ["bubble", "pad"], "energy": 0.4},
                  {"at": "L13", "voices": ["bubble", "pad"], "energy": 0.32},
                  {"at": "L21", "voices": ["bubble", "pad"], "energy": 0.36},
                  {"at": "L25", "voices": ["pad"], "energy": 0.3},
                  {"at": "L27", "voices": ["drone", "pad"], "energy": 0.5},
                  {"at": "L36", "voices": ["drone", "pad"], "energy": 0.4},
                  {"at": "L43", "voices": ["drone", "pad"], "energy": 0.45},
                  {"at": "L52", "voices": ["drone", "pad", "choir"], "energy": 0.55},
                  {"at": "L58", "voices": ["drone", "pad"], "energy": 0.45},
                  {"at": "L60", "voices": ["drone", "pad", "piano"], "energy": 0.45, "mode": "major", "root": 52},
                  {"at": "L69", "voices": ["drone", "choir"], "energy": 0.32, "mode": "minor"},
              ]},
    "sound": {"floor": "grass", "steps_db": -22,
              "ambience": [
                  {"kind": "wind", "from": 0, "to": "end", "lufs": -38},
                  {"kind": "room", "from": 0, "to": "L13", "lufs": -40},
                  {"kind": "static", "from": "L23", "to": "L24", "lufs": -36},
                  {"kind": "static", "from": "L30", "to": "L32", "lufs": -36},
                  {"kind": "hum", "from": "L36", "to": "L39", "lufs": -40},
                  {"kind": "hum", "from": "L58", "to": "L64", "lufs": -40},
                  {"kind": "crickets", "from": "L69", "to": "L71", "lufs": -46},
              ],
              "sfx": remap(sfx),
              "music_drops": [{"from": "P01", "to": "L27", "keep": ["whoosh", "thud"]},
                              {"from": "P02-0.1", "to": "L44", "keep": ["creak"]}]},
}
OUT.write_text(json.dumps(story, indent=1, ensure_ascii=False) + "\n")
print("wrote", OUT, f"({len(shots)} shots)")
