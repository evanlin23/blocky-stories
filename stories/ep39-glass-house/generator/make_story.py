"""Writes ../story.json for ep39 "In this town, everyone has a cloud that rains when they're sad".

Run from anywhere: python stories/ep39-glass-house/generator/make_story.py
The words are in lines.json next to this file. Everything else is here: the shots and their cameras, the acting, the
cues set.py reads (time of day, lamps, the Long Neck's pose, clouds and rain, plants), the score and the sound.
Places are set.py's: street (x -40..40), kitchen (x 100 + ...), garden and glasshouse (x 200 + ...), cinema (x 300 + ...).
Light changes are slow ramps and always happen out of shot or on a cut (flash_safe).
"""
import json
import math
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from cast import cast, clouds, umbrellas  # noqa: E402

OUT = HERE.parent / "story.json"
lines = json.loads((HERE / "lines.json").read_text())

# the word check: slow a line down where a word was swallowed (filled in after the first asr run)
TEMPO = {"L28": 0.62}
for ln in lines:
    if ln["id"] in TEMPO:
        ln["tempo"] = TEMPO[ln["id"]]

GX, KX, CX = 200.0, 100.0, 300.0


def G(x, y, z):
    return [GX + x, y, z]


def K(x, y, z):
    return [KX + x, y, z]


def Cn(x, y, z):
    return [CX + x, y, z]


def c(*keys):
    return [list(k) for k in keys]


def still(loc, tgt, lens):
    return c([0, loc, tgt, lens])


def move(a, b, lens_a, lens_b=None):
    return c([0, a[0], a[1], lens_a], [1, b[0], b[1], lens_b or lens_a])


# ---------------------------------------------------------------------------------------------------- shots
# (id, at, room, what, step, camera)
SHOTS = []


def shot(sid, at, room, what, cam, step=2, hand=0.006):
    SHOTS.append((sid, at, room, what, step, cam, hand))


# street, day. The street camera looks along the pavement from the west, so the people at the gates line up in depth.
ALONG = still([-3.4, -0.6, 1.45], [1.8, 1.0, 1.9], 28)
shot("S01", 0, "street", "me at our gate, my big cloud; Mr Pell's drizzle and two neighbours behind", ALONG)
shot("S02a", "L02", "street", "Mr Pell at his gate, mug, drizzle on his cap", still([4.0, -3.0, 1.45], [4.0, 0.8, 1.7], 34))
shot("S02b", "L02.2", "street", "low angle up through the drizzle", still([3.9, -0.7, 0.45], [4.0, 0.9, 2.0], 26))
shot("S03", "L03", "street", "over the fences: his lawn green, the rest straw",
     move(([-3.4, -0.4, 2.8], [4.5, 2.8, 0.3]), ([-3.0, -0.4, 2.8], [4.5, 2.8, 0.3]), 22))
shot("S04", "L04", "street", "the cafe couple in raincoats, both clouds raining on the cups",
     still([-22.0, -1.3, 1.6], [-22.0, 2.6, 1.7], 26))
shot("S05a", "L05", "cinema", "the front row from the screen, faces lit blue", still(Cn(0.1, -0.9, 1.15), Cn(0.1, 3.0, 1.1), 26))
shot("S05b", "L05.2", "cinema", "the same row, umbrellas up, clouds raining on them", still(Cn(0.1, -0.9, 1.3), Cn(0.1, 3.0, 1.6), 26))
shot("S06a", "L06", "street", "the wedding couple under bunting",
     move(([22.0, -9.2, 1.3], [22.0, -4.0, 2.0]), ([22.0, -8.6, 1.3], [22.0, -4.0, 2.0]), 28))
shot("S06b", "L06.2", "street", "a guest covered in freckles, grinning", still([20.5, -6.4, 1.7], [20.2, -3.3, 1.6], 36))
shot("S07", "L07", "street", "me on our step, low, my cloud huge against the sky", still([0.7, 0.4, 0.5], [0.0, 3.9, 2.3], 20))
shot("S08", "L08", "street", "close on my dry cloud, push in",
     move(([0.4, 1.3, 2.3], [0.0, 3.9, 2.4]), ([0.2, 2.2, 2.35], [0.0, 3.9, 2.4]), 26))
shot("S09", "L09", "street", "me waving to a neighbour, both grinning", still([-1.9, -3.4, 1.65], [-1.9, 0.8, 1.9], 30))
shot("S10", "L10", "kitchen", "the hall hook: three patched umbrellas and mine in its wrapper",
     c([0, K(2.88, 2.1, 1.05), K(2.88, 3.74, 1.05), 30], [1, K(2.9, 2.3, 1.05), K(2.9, 3.74, 1.05), 30]))
shot("S11a", "L11", "garden", "Lou's framed photo on Mum's bench", still(G(-0.7, 17.2, 1.0), G(-1.93, 18.0, 0.92), 40))
shot("S11b", "L11.2", "garden", "the sea postcard on the potting table", still(G(0.2, 20.4, 1.25), G(0.32, 21.45, 0.97), 40))
shot("S12a", "L12", "garden", "daytime wide down the garden to the glasshouse",
     move((G(0.4, 1.4, 1.75), G(0.2, 19.0, 1.3)), (G(0.4, 3.0, 1.75), G(0.2, 19.0, 1.3)), 22))
shot("S12b", "L12.2", "garden", "the door's iron hinge: two short strokes, held", still(G(-0.25, 14.95, 1.57), G(-0.25, 16.0, 1.55), 28), 4, 0)
shot("S13a", "L13", "kitchen", "Mum at the sink, her cloud dark and low", still(K(1.9, 3.1, 1.5), K(-0.9, 3.45, 1.55), 30))
shot("S13b", "L13.2", "kitchen", "close on the cloud, heavy, dry underneath", still(K(0.9, 2.6, 1.5), K(-0.9, 3.45, 1.85), 40))
shot("S14", "L14", "kitchen", "her tired face looking up at it", still(K(-0.5, 1.5, 1.55), K(-0.85, 3.4, 1.5), 36))
shot("S15a", "L15", "garden", "Mum in the wicker chair at dusk, a blanket, beside Lou's bench", still(G(-0.4, 16.5, 1.35), G(0.9, 19.5, 1.1), 30))
shot("S15b", "L15.3", "garden", "over her shoulder down Lou's bench, crowded pots", still(G(0.9, 20.7, 1.55), G(2.0, 17.2, 0.95), 28))
shot("S16", "L16", "garden", "a big Lou leaf, brown and curling", still(G(1.2, 17.8, 1.2), G(1.925, 18.35, 1.15), 36))
shot("S17", "L17", "kitchen", "Monday: Mum, cloud a hand above her head", still(K(1.0, 0.1, 1.45), K(1.0, 2.75, 1.5), 30))
shot("S18", "L18", "kitchen", "Tuesday: the cloud at her hairline", still(K(1.0, 0.1, 1.45), K(1.0, 2.75, 1.5), 30))
shot("S19a", "L19", "kitchen", "Wednesday: over her eyes", still(K(1.0, 0.1, 1.45), K(1.0, 2.75, 1.5), 30))
shot("S19b", "L19.3", "kitchen", "tea into the sugar bowl", still(K(1.9, 0.7, 1.4), K(1.1, 1.95, 0.95), 30), 2, 0)
shot("S20a", "L20", "kitchen", "me across the table, asking", still(K(2.25, 3.5, 1.55), K(1.0, 1.05, 1.45), 30))
shot("S20b", "L20.2", "kitchen", "Mum's smile under the cloud's edge", still(K(1.75, 0.8, 1.5), K(1.0, 2.75, 1.45), 34))
shot("S21", "L21", "kitchen", "the cloud over her nose", still(K(1.75, 0.8, 1.5), K(1.0, 2.75, 1.45), 34))
shot("S22", "L22", "garden", "night, from the back step: the glasshouse glowing, a head over the far hedge",
     still(G(1.6, 10.5, 1.5), G(3.7, 25.0, 3.5), 40))
shot("S23", "L23", "garden", "closer: the head against the stars", c([0, G(2.0, 14.0, 1.5), G(3.7, 25.0, 3.8), 38], [1, G(2.4, 16.0, 1.5), G(3.7, 25.0, 3.8), 38]))
shot("S24", "L24", "garden", "tilt down the stacked blocks into the hedge",
     c([0, G(2.4, 16.5, 1.5), G(3.7, 25.0, 4.0), 40], [1, G(2.4, 16.5, 1.5), G(3.7, 25.0, 2.2), 40]))
shot("S25", "L25", "garden", "night two, from the path: the head just above the door", still(G(-0.4, 9.4, 1.45), G(1.0, 15.8, 3.0), 30))
shot("S26a", "L26", "garden", "me, close, looking away to the house", still(G(-0.3, 8.4, 1.6), G(-0.3, 10.8, 1.65), 30))
shot("S26b", "L26.2", "garden", "back to the door: the head, same spot, hold", still(G(-0.4, 9.4, 1.45), G(1.0, 15.8, 3.0), 30), 4, 0)
shot("S27", "L27", "garden", "night three, inside, looking up: the face on a roof pane", still(G(0.0, 18.2, 1.3), G(1.25, 19.5, 2.5), 28))
shot("S28", "L28", "garden", "high: Mum asleep, her cloud low", still(G(0.2, 20.7, 2.5), G(0.85, 19.4, 1.0), 28))
shot("S29", "L29", "garden", "the face through the glass", still(G(0.1, 18.9, 1.2), G(1.27, 19.5, 2.55), 38))
shot("S30a", "L30", "kitchen", "breakfast, me telling Mum", still(K(2.9, -0.4, 1.5), K(1.0, 1.9, 1.3), 24))
shot("S30b", "L30.2", "kitchen", "Mum, cloud over her eyes, smiling", still(K(1.75, 0.8, 1.5), K(1.0, 2.75, 1.45), 34))
shot("S31", "L31", "garden", "Friday dusk: me on the path with a mug toward the glowing glasshouse", still(G(-0.7, 7.6, 1.6), G(0.1, 16.0, 1.4), 26))
shot("S32", "L32", "garden", "inside: the lamps fading slowly down", still(G(-0.3, 16.5, 1.4), G(0.2, 19.0, 2.35), 26))
shot("S33a", "L33", "garden", "Mum asleep, cloud over her whole face", still(G(0.55, 17.2, 1.25), G(0.85, 19.5, 1.25), 34))
shot("S33b", "L33.3", "garden", "close: her chin and the blanket below the grey", still(G(0.75, 18.4, 0.95), G(0.85, 19.5, 0.95), 40))
shot("S34", "L34", "garden", "Lou's bench beside her, empty slats, brown plants", still(G(0.9, 17.0, 1.1), G(2.0, 19.0, 0.8), 30))
shot("S35", "L35", "garden", "up at the roof: the vent propped open", still(G(0.3, 18.2, 1.3), G(1.9, 19.45, 2.2), 28))
shot("S36", "L36", "garden", "the reveal: the head hanging through the vent beside Lou's bench", still(G(-0.1, 15.3, 1.3), G(1.1, 19.5, 1.6), 34), 1, 0.004)
shot("S37a", "L37", "garden", "outside, low: its body dark against the glasshouse wall", still(G(5.6, 16.4, 0.55), G(2.75, 19.5, 1.5), 28), 1)
shot("S37b", "L37.2", "garden", "the neck over the roof and in through the vent", still(G(4.9, 17.0, 2.2), G(2.1, 19.5, 2.0), 30), 1)
shot("S38", "L38", "garden", "its face beside Lou's bench, a hand from Mum's cloud", still(G(0.4, 16.4, 1.5), G(1.2, 19.5, 1.5), 34), 1)
shot("S39", "L39", "garden", "its eyes on me, hold", still(G(1.0, 17.1, 1.4), G(1.58, 19.5, 1.4), 38), 1, 0)
shot("S40a", "L40", "garden", "me backing toward the potting table", still(G(-0.1, 16.2, 1.5), G(-0.3, 20.0, 1.35), 24), 1)
shot("S40b", "L40.2", "garden", "the dry leaves rustling", still(G(0.9, 21.0, 1.25), G(-0.35, 21.45, 0.9), 28), 1)
shot("S41", "L41", "garden", "the lamps fade to dark: only the eye glints", still(G(-0.1, 15.3, 1.3), G(1.1, 19.5, 1.6), 34), 1, 0)
shot("S42", "L42", "garden", "the lamps fade up slowly: the head lower", still(G(-0.1, 15.3, 1.3), G(1.3, 19.5, 1.35), 34), 1, 0)
shot("S43", "L43", "garden", "its chin on the slats of Lou's bench", still(G(0.35, 18.0, 1.15), G(1.95, 19.5, 1.0), 36), 1)
shot("S44", "L44", "garden", "Mum's chair: only a slate cloud and the blanket's hem", still(G(0.6, 17.6, 1.1), G(0.85, 19.5, 0.95), 34))
shot("S45", "L45", "garden", "me turning to the glass: Mr Pell's lawn glowing green", still(G(0.4, 20.3, 1.5), G(-12.0, 13.5, 1.3), 30))
shot("S46a", "L46", "garden", "close on me, thinking", still(G(-0.3, 16.6, 1.55), G(-0.3, 18.2, 1.6), 36))
shot("S46b", "L46.2", "street", "the cafe couple, laughing in the rain", still([-22.0, -1.3, 1.45], [-22.0, 2.6, 1.3], 30))
shot("S47", "L47", "garden", "Mum's slate cloud, huge and low", still(G(0.55, 17.6, 1.1), G(0.85, 19.5, 1.2), 32))
shot("S48a", "L48", "garden", "Mum asleep under it", still(G(0.2, 17.5, 1.3), G(0.85, 19.5, 1.2), 36))
shot("S48b", "L48.2", "garden", "me, my big white cloud", still(G(-0.4, 16.6, 1.5), G(0.0, 18.5, 1.9), 28))
shot("S49", "L49", "garden", "close on my cloud's grey underside", still(G(-0.7, 17.5, 1.0), G(0.0, 18.6, 2.3), 28))
shot("S50a", "L50", "garden", "me beside her chair, saying her name", still(G(-0.9, 17.2, 1.5), G(0.5, 19.1, 1.4), 28))
shot("S50b", "L50.3", "garden", "her cloud lifts a little off her face as she wakes", still(G(0.55, 17.4, 1.3), G(0.85, 19.5, 1.35), 36))
shot("S51", "L51", "garden", "me, close, eyes wet", still(G(0.0, 16.7, 1.6), G(0.0, 18.5, 1.6), 38))
shot("S52", "L52", "garden", "my cloud going grey", still(G(-0.8, 16.9, 1.4), G(0.0, 18.5, 2.2), 26))
shot("S53", "L53", "garden", "the first drops from my cloud onto my face", still(G(0.0, 16.6, 1.75), G(0.0, 18.5, 1.85), 34))
shot("S54a", "L54", "garden", "Mum looking up at my rain", still(G(0.55, 17.4, 1.3), G(0.85, 19.5, 1.45), 34))
shot("S54b", "L54.3", "garden", "her face crumples; her cloud starts to rain", still(G(0.55, 17.4, 1.3), G(0.85, 19.5, 1.45), 34))
shot("S55", "L55", "garden", "high: two clouds raining over Lou's bench, the head resting behind", still(G(-0.5, 17.0, 2.5), G(1.2, 19.3, 1.0), 26))
shot("S56", "L56", "garden", "Mum laughing and crying, me the same", still(G(0.6, 16.6, 1.5), G(0.5, 19.0, 1.5), 24))
shot("S57a", "L57", "garden", "the wrapper torn off, on the floor", still(G(0.5, 16.9, 1.0), G(0.2, 18.0, 0.1), 30))
shot("S57b", "L57.3", "garden", "the umbrella up, rain falling under it", still(G(0.3, 15.9, 1.75), G(0.15, 18.4, 1.6), 20))
shot("S58a", "L58", "garden", "I sit on Lou's bench where the head was", still(G(0.4, 17.4, 1.2), G(1.95, 19.5, 1.1), 30))
shot("S58b", "L58.3", "garden", "up at the roof vent: empty, open, rain on its sill", still(G(0.3, 18.5, 1.4), G(1.9, 19.45, 2.2), 28))
shot("S59", "L59", "garden", "morning: two light white clouds over two benches", still(G(0.0, 16.1, 1.4), G(0.0, 19.5, 0.95), 8))
shot("S60", "L60", "garden", "Lou's plants standing up green, wet leaves in soft sun", still(G(0.9, 17.3, 1.2), G(2.0, 18.6, 0.95), 34))
shot("S61", "L61", "garden", "Mr Pell over the hedge, raising his mug, under his drizzle", still(G(-3.2, 14.0, 1.6), G(-7.2, 14.0, 1.75), 32))
shot("S62", "L62", "street", "the sunny street again: me at the gate, a light rain, Mum beside me", ALONG)
shot("S62b", "L62.4", "street", "far down the street: a long head over a hedge beside a neighbour's heavy dry cloud",
     still([25.0, -2.6, 1.5], [35.5, 1.5, 3.0], 40), 1, 0)
shot("S63", "L63", "street", "close on me, grinning in my own drizzle", still([-1.6, -0.2, 1.7], [0.0, 0.9, 1.75], 38))

shots = []
for i, (sid, at, room, what, step, cam, hand) in enumerate(SHOTS):
    s = {"id": sid, "cam": cam, "hand": hand, "step": step, "room": room, "what": what}
    if i:
        s["at"] = at
    shots.append(s)

# ---------------------------------------------------------------------------------------------------- acting
# Everyone starts far away (x -100: out of every room, and their clouds too) and is placed on a cut by put(): a put()
# writes a zero-length step (no walk) and a key with blend 0, so nothing glides in a shot. walk() is a move in a shot.
NEUTRAL = {"arms": [0, 0], "side": [0, 0], "head": [0, 0], "lean": 0, "tremble": 0, "sit": False, "blink": True}
acting = {w: [{"at": 0, "pos": [-100.0, -50.0 - 2 * i], "yaw": 0}] for i, w in enumerate(cast)}


def put(who, at, pos, yaw=0, expr="neutral", **kw):
    keys = acting[who]
    prev = next((k["pos"] for k in reversed(keys) if "pos" in k), None)
    if prev is not None:
        keys.append({"at": at, "pos": prev})
    keys.append({"at": at, "pos": pos, "yaw": yaw, "blend": 0, "expr": expr, **NEUTRAL, **kw})


def walk(who, at, pos, **kw):
    acting[who].append({"at": at, "pos": pos, **kw})


def key(who, at, **kw):
    acting[who].append({"at": at, **kw})


def away(who, at):
    put(who, at, [-100.0, -50.0])


def face_to(a, b):
    """The yaw that faces from a toward b (yaw 0 faces -y, 90 faces +x)."""
    return round(math.degrees(math.atan2(b[0] - a[0], -(b[1] - a[1]))), 1)


# --- the street, day (L01 to L10)
put("me", 0, [0.0, 0.85], yaw=-90, expr="neutral", arms=[0, 0], head=[0, 0])      # leaning on our gate
put("pell", 0, [4.0, 0.85], yaw=-90, expr="angry", arms=[0, 62], head=[0, 0])     # Mr Pell at his gate, mug up
put("nb1", 0, [8.0, 0.85], yaw=-90, expr="smirk")
put("nb2", 0, [12.0, 0.85], yaw=-90, expr="neutral")
put("nb3", 0, [-100.0, -60.0])
# the cafe (L04): a couple in raincoats at the table, facing each other, sitting
put("cf1", "L03", [-22.6, 2.6, -0.23], yaw=90, expr="crying", sit=True, head=[0, 8], arms=[8, 8])
put("cf2", "L03", [-21.4, 2.6, -0.23], yaw=-90, expr="crying", sit=True, head=[0, 8], arms=[8, 8])
# the cinema row (L05): two seats and a third at the edge, sitting, facing the screen
put("cn1", "L04.2", [CX - 0.62, 3.0, -0.23], yaw=0, expr="worried", sit=True)
put("cn2", "L04.2", [CX + 0.62, 3.0, -0.23], yaw=0, expr="crying", sit=True)
put("cn3", "L04.2", [CX + 1.86, 3.0, -0.23], yaw=0, expr="worried", sit=True)
# the wedding (L06)
put("wd1", "L05.2", [21.3, -4.1], yaw=0, expr="grin", arms=[0, 0])
put("wd2", "L05.2", [22.7, -4.1], yaw=0, expr="grin")
put("gs1", "L05.2", [20.0, -3.4], yaw=0, expr="grin")
put("gs2", "L05.2", [24.0, -3.4], yaw=0, expr="grin")
# me on our step (L07 to L08): my cloud against the sky
put("me", "L06.3", [0.0, 3.9, 0.15], yaw=0, expr="grin", head=[0, -6])
put("me", "L08", [0.0, 3.9, 0.15], yaw=0, expr="neutral", head=[0, -14])
# L09: waving to a neighbour, both grinning (facing each other along the pavement)
put("me", "L08.2", [-1.3, 0.85], yaw=-90, expr="grin", arms=[0, 150], head=[0, 0])
put("nb3", "L08.2", [-2.55, 0.85], yaw=90, expr="grin", arms=[0, 40])
# L10: nothing on screen but the hook (the kitchen)
# --- Mum, in time order: the sink (L13), her face (L14), the glasshouse at dusk (L15 to L16), the kitchen mornings
# (L17 to L21), the glasshouse nights (L22 on), breakfast (L30), the glasshouse again (L31 on)
put("mum", "L12.2", [KX - 0.9, 3.45], yaw=180, expr="neutral", arms=[40, 40], head=[0, 14])
put("mum", "L14", [KX - 0.9, 3.4], yaw=0, expr="worried", arms=[30, 30], head=[0, -22])           # looking up at her cloud
put("mum", "L15-0.1", [GX + 0.85, 19.5, -0.23], yaw=0, expr="asleep", sit=True, arms=[30, 30], head=[0, 14])
put("mum", "L17-0.1", [KX + 1.0, 2.75, -0.23], yaw=0, expr="neutral", sit=True, arms=[30, 30], head=[0, 8])
put("mum", "L19.2", [KX + 1.0, 2.75, -0.23], yaw=0, expr="neutral", sit=True, arms=[68, 20], head=[0, 24])  # the pot, already tipped
put("mum", "L20.2", [KX + 1.0, 2.75, -0.23], yaw=0, expr="soft", sit=True, arms=[20, 20], head=[0, 4])
put("mum", "L22-0.1", [GX + 0.85, 19.5, -0.23], yaw=0, expr="asleep", sit=True, arms=[30, 30], head=[0, 14])
put("mum", "L30-0.1", [KX + 1.0, 2.75, -0.23], yaw=0, expr="soft", sit=True, arms=[20, 20], head=[0, 4])
put("mum", "L31-0.1", [GX + 0.85, 19.5, -0.23], yaw=0, expr="asleep", sit=True, arms=[30, 30], head=[0, 14])
put("me", "L20-0.1", [KX + 1.0, 1.05, -0.23], yaw=180, expr="worried", sit=True, arms=[25, 25], head=[0, 4])
# --- night one to three (L22 to L29): me in the garden, Mum asleep
put("me", "L26-0.1", [GX - 0.3, 10.8], yaw=0, expr="worried", head=[-30, 0])                  # looking away to the house
key("me", "L26.2-0.01", yaw=0)
put("me", "L26.2+3", [-100.0, -50.0])
# breakfast (L30): me and Mum at the table
put("me", "L30-0.1", [KX + 1.0, 1.05, -0.23], yaw=180, expr="worried", sit=True, arms=[25, 25], head=[0, 4])
# Friday dusk (L31): me walking out with a mug; Mum asleep in the chair
put("me", "L31-0.1", [GX - 0.05, 6.2], yaw=180, expr="neutral", arms=[0, 68], head=[0, 0])
walk("me", "L32-0.3", [GX + 0.0, 15.2], arms=[0, 68])
# the scare: me comes into the glasshouse door and stands there (the camera is at the door)
put("me", "L32", [GX - 0.1, 16.5], yaw=180, expr="worried", arms=[0, 68], head=[0, 0])
put("me", "L33", [GX - 0.2, 17.2], yaw=180, expr="scared", arms=[0, 0], head=[0, 0])
put("me", "L40-0.1", [GX - 0.15, 18.0], yaw=0, expr="terrified", tremble=2.0, head=[0, 0])
walk("me", "L40.1", [GX - 0.15, 18.0], yaw=0, expr="terrified", tremble=2.0, keep_yaw=True)
walk("me", "L40.2", [GX - 0.3, 20.75], yaw=0, expr="terrified", tremble=2.0, keep_yaw=True)
key("me", "L40.2", yaw=0)
put("me", "L41", [GX - 0.3, 20.75], yaw=0, expr="terrified", tremble=2.0)
put("me", "L45-0.1", [GX - 1.3, 18.0], yaw=-90, expr="worried", head=[0, 0])                 # turning to the west glass
put("me", "L46", [GX - 0.3, 18.2], yaw=0, expr="worried", head=[0, 0])                       # thinking
put("me", "L48.2", [GX + 0.0, 18.6], yaw=0, expr="neutral", head=[0, 0])
put("me", "L50", [GX + 0.25, 18.7], yaw=60, expr="worried", head=[0, 0], arms=[0, 0])
put("me", "L51", [GX + 0.0, 18.5], yaw=0, expr="crying", head=[0, 0])
key("me", "L53", head=[0, -14], expr="crying", blend=0.5)
put("me", "L55", [GX + 0.0, 18.5], yaw=0, expr="crying", head=[0, 0])
key("me", "L56", expr="crying")
put("me", "L57.3", [GX + 0.0, 18.5], yaw=0, expr="crying", head=[0, 0], arms=[0, 0])
# me on Lou's bench (L58): seated where its head was; Mum back on her own bench (L59)
put("me", "L58", [GX + 1.95, 19.5, 0.08], yaw=-90, expr="soft", sit=True, arms=[10, 10])
put("me", "L59", [GX + 1.95, 19.5, 0.08], yaw=-90, expr="soft", sit=True, arms=[10, 10])
# Mum: wakes (L50.2), looks up (L54), crumples (L54.2), laughs and cries (L56)
put("mum", "L50.1", [GX + 0.85, 19.5, -0.23], yaw=0, expr="asleep", sit=True, arms=[30, 30], head=[0, 14])
key("mum", "L50.3+0.1", expr="worried", head=[0, 4], blend=0.5)
key("mum", "L51", expr="worried", head=[0, 4])
key("mum", "L53", expr="worried", head=[0, -24], blend=0.6)
key("mum", "L54.2", expr="crying", head=[0, 6])
key("mum", "L56", expr="crying", head=[0, 4], arms=[60, 60])
put("mum", "L59", [GX - 1.95, 19.5, 0.08], yaw=90, expr="soft", sit=True, arms=[10, 10], head=[0, 0])
# morning in the garden (L60 to L61): Mr Pell over the hedge, me and Mum on their benches
put("pell2", "L61-0.1", [GX - 7.2, 14.0], yaw=90, expr="smirk", arms=[0, 100], head=[0, 0])
# L61 street ending (L62 to L63)
put("me", "L62-0.1", [0.0, 0.95], yaw=-90, expr="grin", head=[0, 0])
put("mum", "L62-0.1", [1.5, 0.35], yaw=-90, expr="grin")
put("pell", "L62-0.1", [4.0, 0.85], yaw=-90, expr="smirk", arms=[0, 62])
put("nb1", "L62-0.1", [8.0, 0.85], yaw=-90, expr="smirk")
put("nb2", "L62-0.1", [12.0, 0.85], yaw=-90, expr="neutral")
put("nb3", "L62-0.1", [33.0, 0.85], yaw=-90, expr="neutral")
put("me", "L63", [0.0, 0.95], yaw=-90, expr="grin", head=[0, 0])
# the cafe couple laughing in the rain (L46b): same table, new faces
put("cf1", "L46.1", [-22.6, 2.6, -0.23], yaw=90, expr="grin", sit=True, head=[0, 4], arms=[8, 8])
put("cf2", "L46.1", [-21.4, 2.6, -0.23], yaw=-90, expr="grin", sit=True, head=[0, 4], arms=[8, 8])

# ---------------------------------------------------------------------------------------------------- cues
NECK_BODY = {
    # night 1: behind the far hedge, the neck straight up, the head about 4.3 m high, facing the house
    "n1": {"body": [3.7, 25.6], "yaw": 0, "pts": [[3.7, 25.6, 1.34], [3.7, 25.6, 3.74]], "look": [0.6, 4.0, 3.6], "rim": [-1.2, -2.0, 0.6], "rim_w": 260.0},
    # night 2: against the glasshouse's front gable beside the door, the neck straight up
    "n2": {"body": [1.15, 15.35], "yaw": 0, "pts": [[1.15, 15.35, 1.34], [1.15, 15.35, 3.74]], "look": [-0.4, 8.4, 2.9], "rim": [-1.0, -2.0, 0.6], "rim_w": 260.0},
    # night 3: the body at the east wall, the neck over the eave and along the roof, the head down on one pane
    "n3": {"body": [2.75, 19.5], "yaw": -90,
           "pts": [[2.75, 19.5, 1.34], [2.75, 19.5, 2.05], [2.3, 19.5, 1.9], [1.45, 19.5, 2.42]], "look": [0.85, 19.5, 1.3]},
    # night 3, close: the head hangs face-on over one pane, looking down through the glass
    "n3f": {"body": [2.75, 19.5], "yaw": -90,
            "pts": [[2.75, 19.5, 1.34], [2.75, 19.5, 3.0], [0.4, 19.5, 3.9], [1.1, 19.5, 2.62]],
            "look": [0.1, 18.9, 1.2], "rim": [-0.1, -1.0, -1.3], "rim_w": 320.0},
    # the scare: the neck in through the open vent, the head hanging beside Lou's bench at Mum's height
    "scare": {"body": [2.75, 19.5], "yaw": -90,
              "pts": [[2.75, 19.5, 1.34], [2.75, 19.5, 2.05], [1.62, 19.5, 2.05], [1.58, 19.5, 1.55]],
              "look": [-0.1, 15.3, 1.3], "roll": 9},
    # after the fade: one more block of neck, the chin on the slats of Lou's bench
    "low": {"body": [2.75, 19.5], "yaw": -90,
            "pts": [[2.75, 19.5, 1.34], [2.75, 19.5, 2.05], [1.95, 19.5, 2.05], [1.95, 19.5, 1.2]],
            "look": [0.3, 18.0, 1.1], "roll": 6},
}


def neck(at, name, **over):
    d = dict(NECK_BODY[name])
    d.update(over)
    return {"at": at, "name": "neck", "on": True, **d}


cues = [
    # ---- the garden's light: set out of shot (a ramp of 0.3 s ending on the cut)
    {"at": 0, "name": "tod", "mode": "day", "dur": 0.3},
    {"at": "L15-0.4", "name": "tod", "mode": "dusk", "dur": 0.3},
    {"at": "L22-0.4", "name": "tod", "mode": "night", "dur": 0.3},
    {"at": "L31-0.4", "name": "tod", "mode": "dusk", "dur": 0.3},
    {"at": "L32", "name": "tod", "mode": "night", "dur": 3.0},
    {"at": "L59-0.3", "name": "tod", "mode": "morning", "dur": 0.3},
    # ---- the lamps (every change is a slow ramp)
    {"at": 0, "name": "lamps", "to": 1.0, "dur": 0.3},
    {"at": "L32", "name": "lamps", "to": 0.5, "dur": 1.5},
    {"at": "L36-0.5", "name": "lamps", "to": 0.32, "dur": 0.4},
    {"at": "L41", "name": "lamps", "to": 0.0, "dur": 1.2},
    {"at": "L42", "name": "lamps", "to": 0.32, "dur": 1.5},
    {"at": "L45-0.4", "name": "lamps", "to": 0.55, "dur": 0.3},
    {"at": "L59-0.5", "name": "lamps", "to": 0.0, "dur": 0.4},
    # ---- the roof vent, the door
    {"at": "L35", "name": "vent", "to": 1.0, "dur": 0.7},
    {"at": "L59-0.4", "name": "vent", "to": 0.0, "dur": 0.3},
    {"at": "L22-0.4", "name": "door", "to": 0.0, "dur": 0.3},
    {"at": "L31-0.4", "name": "door", "to": 1.0, "dur": 0.3},
    # ---- the plants: green and standing, then going brown, then standing again
    {"at": 0, "name": "plants", "to": 0.0, "dur": 0.3},
    {"at": "L15-0.4", "name": "plants", "to": 0.55, "dur": 0.3},
    {"at": "L16", "name": "plants", "to": 0.8, "dur": 1.6},
    {"at": "L21", "name": "plants", "to": 1.0, "dur": 0.4},
    {"at": "L60", "name": "plants", "to": 0.0, "dur": 1.4},
    # ---- the Long Neck: never seen moving, only nearer
    {"at": 0, "name": "neck", "on": False},
    neck("L22", "n1"),
    neck("L25", "n2"),
    neck("L27", "n3"),
    neck("L29", "n3f"),
    {"at": "L30", "name": "neck", "on": False},
    neck("L36", "scare"),
    neck("L39", "scare", look=[1.0, 17.1, 1.4]),
    neck("L42-0.2", "low"),
    {"at": "L58", "name": "neck", "on": False},
    {"at": "L62.4", "name": "neck", "on": True, "room": "street", "abs": True, "body": [36.6, 3.0], "yaw": 0,
     "pts": [[36.6 - GX, 3.0, 1.34], [36.6 - GX, 3.0, 4.2]], "look": [28.0 - GX, -2.6, 3.0]},
    {"at": "L63", "name": "neck", "on": False},
    {"at": "L40.2", "name": "rustle", "on": True},
    {"at": "L41", "name": "rustle", "on": False},
    # ---- the tea
    {"at": "L19.2", "name": "pour", "on": True},
    {"at": "L19.3+1.8", "name": "pour", "on": False},
    # ---- the mug in my hand on the path, Mr Pell's mug
    {"at": "L31-0.1", "name": "mug", "who": "me", "on": True, "raise": 68},
    {"at": "L33", "name": "mug", "who": "me", "on": False},
    {"at": 0, "name": "mug", "who": "pell", "on": True, "raise": 62},
    {"at": "L61-0.1", "name": "mug", "who": "pell2", "on": True, "raise": 100},
    {"at": "L62-0.1", "name": "mug", "who": "pell", "on": True, "raise": 62},
    # ---- the wrapper on the floor, the umbrellas
    {"at": 0, "name": "wrapper", "on": False},
    {"at": "L57", "name": "wrapper", "on": True},
    {"at": "L05.2", "name": "umbrella", "who": "cn1", "on": True},
    {"at": "L05.2", "name": "umbrella", "who": "cn2", "on": True},
    {"at": "L05.2", "name": "umbrella", "who": "cn3", "on": True},
    {"at": "L06", "name": "umbrella", "who": "cn1", "on": False},
    {"at": "L06", "name": "umbrella", "who": "cn2", "on": False},
    {"at": "L06", "name": "umbrella", "who": "cn3", "on": False},
    {"at": "L57.3", "name": "umbrella", "who": "me", "on": True},
    {"at": "L58", "name": "umbrella", "who": "me", "on": False},
    # ---- rain through the open vent (the sill) after the head is gone
    {"at": 0, "name": "ventrain", "on": False},
    {"at": "L58", "name": "ventrain", "on": True},
    {"at": "L59-0.4", "name": "ventrain", "on": False},
    # ---- clouds: Pell's drizzle all the way, the cafe and cinema rain, then mine, then Mum's
    {"at": 0, "name": "cloud", "who": "pell", "rain": 0.55, "dur": 0.3},
    {"at": "L61-0.1", "name": "cloud", "who": "pell2", "rain": 0.55, "dur": 0.3},
    {"at": "L03.2", "name": "cloud", "who": "cf1", "rain": 1.0, "size": 1.35, "tone": 0.55, "dur": 0.3},
    {"at": "L03.2", "name": "cloud", "who": "cf2", "rain": 1.0, "size": 1.35, "tone": 0.55, "dur": 0.3},
    {"at": "L05.2", "name": "cloud", "who": "cn1", "rain": 0.8, "dur": 0.3},
    {"at": "L05.2", "name": "cloud", "who": "cn2", "rain": 0.8, "dur": 0.3},
    {"at": "L05.2", "name": "cloud", "who": "cn3", "rain": 0.8, "dur": 0.3},
    {"at": "L46.1", "name": "cloud", "who": "cf1", "rain": 0.8, "dur": 0.3},
    {"at": "L46.1", "name": "cloud", "who": "cf2", "rain": 0.8, "dur": 0.3},
    {"at": "L06", "name": "cloud", "who": "cn1", "rain": 0.0, "dur": 0.1},
    {"at": "L06", "name": "cloud", "who": "cn2", "rain": 0.0, "dur": 0.1},
    {"at": "L06", "name": "cloud", "who": "cn3", "rain": 0.0, "dur": 0.1},
    {"at": "L13-0.3", "name": "cloud", "who": "cf1", "rain": 0.0, "dur": 0.1},
    {"at": "L13-0.3", "name": "cloud", "who": "cf2", "rain": 0.0, "dur": 0.1},
    # Mum's cloud: heavy and dark, sinking day by day, never raining until L54.2
    {"at": 0, "name": "cloud", "who": "mum", "gap": 0.14, "size": 1.3, "dur": 0.05},
    {"at": "L17", "name": "cloud", "who": "mum", "gap": 0.14, "dur": 0.05},
    {"at": "L18", "name": "cloud", "who": "mum", "gap": -0.04, "dur": 0.05},
    {"at": "L19", "name": "cloud", "who": "mum", "gap": -0.3, "dur": 0.05},
    {"at": "L21", "name": "cloud", "who": "mum", "gap": -0.4, "dur": 0.05},
    {"at": "L22", "name": "cloud", "who": "mum", "gap": -0.46, "dur": 0.05},
    {"at": "L33", "name": "cloud", "who": "mum", "gap": -0.55, "size": 2.1, "dur": 0.05},
    {"at": "L44", "name": "cloud", "who": "mum", "gap": -0.55, "size": 2.1, "dur": 0.05},
    {"at": "L47", "name": "cloud", "who": "mum", "gap": -0.55, "size": 2.1, "dur": 0.05},
    {"at": "L50.3+0.1", "name": "cloud", "who": "mum", "gap": -0.2, "size": 1.5, "dur": 0.9},
    {"at": "L53", "name": "cloud", "who": "mum", "gap": 0.1, "size": 1.4, "dur": 1.0},
    {"at": "L54.3", "name": "cloud", "who": "mum", "rain": 0.85, "dur": 0.8},
    {"at": "L55", "name": "cloud", "who": "mum", "white": 1.0, "dur": 3.5},
    {"at": "L59", "name": "cloud", "who": "mum", "gap": 0.14, "size": 1.0, "rain": 0.0, "white": 1.0, "dur": 0.05},
    {"at": "L62-0.1", "name": "cloud", "who": "nb3", "size": 3.0, "gap": 0.0, "tone": 1.0, "rain": 0.0, "dur": 0.05},
    {"at": "L62", "name": "cloud", "who": "mum", "gap": 0.14, "size": 1.0, "rain": 0.25, "white": 1.0, "dur": 0.05},
    # mine: the biggest, whitest cloud in town, never rained; it goes grey at L52 and rains from L53
    {"at": 0, "name": "cloud", "who": "me", "size": 2.0, "rain": 0.0, "dur": 0.05},
    {"at": "L52-0.15", "name": "cloud", "who": "me", "tone": 1.0, "dur": 0.9},
    {"at": "L53", "name": "cloud", "who": "me", "rain": 0.7, "dur": 0.8},
    {"at": "L59", "name": "cloud", "who": "me", "tone": 0.0, "size": 1.4, "rain": 0.0, "gap": 0.14, "dur": 0.05},
    {"at": "L62", "name": "cloud", "who": "me", "tone": 0.0, "size": 1.7, "rain": 0.3, "dur": 0.05},
    {"at": "L57.3", "name": "cloud", "who": "me", "gap": 0.45, "dur": 0.05},
    {"at": "L58", "name": "cloud", "who": "me", "gap": 0.14, "dur": 0.05},
]

# ---------------------------------------------------------------------------------------------------- sound
sfx = [
    {"at": "L22", "name": "x", "kind": "riser", "db": -26, "dur": 1.6},
    {"at": "L27", "kind": "creak", "db": -20, "dur": 1.1},                    # a glass pane taking weight
    {"at": "L35.1", "kind": "creak", "db": -22, "dur": 1.0},                  # the vent propped open
    {"at": "L36", "kind": "sting", "db": -10},
    {"at": "L40.2", "kind": "whoosh", "db": -26, "dur": 1.0},                  # dry leaves
    {"at": "L42", "kind": "thud", "db": -24},
    {"at": "L52", "kind": "bell", "db": -20},                                 # one soft note as the cloud turns grey
    {"at": "L58", "kind": "click", "db": -22},
    {"at": "L62.4", "kind": "sting", "db": -14},                                # far down the street, a head over a hedge
    {"at": "L63+0.6", "kind": "thud", "db": -16},                               # the last sound
]
for s_ in sfx:
    s_.pop("name", None)

story = {
    "slug": "ep39-glass-house",
    "title": "In this town, everyone has a cloud that rains when they're sad",
    "made_for_kids": False,
    "premise": "In our town everyone has a small white cloud over their head that rains when they're sad. Mine is the biggest in town and has never rained once, so everyone calls me the happy one. Since Mum's sister Lou moved across the sea, Mum's cloud has gone dark and low and never rains, and she sleeps in the glasshouse at the end of the garden among Lou's dying plants. Each night a head on a long neck of stacked blocks is nearer the glasshouse.",
    "twist": "The Long Neck took Lou's place on her empty bench, patient until someone sat there; a cloud that never rains only gets heavier, so Mum and I had each been holding ours in for the other, and when mine finally rained the thing was gone and the plants stood up.",
    "world": "a dry late-summer terraced street under a sunny sky, a small kitchen, and a back garden of straw-coloured grass with a Victorian glasshouse at the end of it, white frame, small panes, two benches facing each other",
    "voice": {"voice": "am_adam", "tempo": 1.03, "rate": 1.45},
    "key_color": "#6fb6ff",
    "gap": 0.12,
    "tail": 0.3,
    "min_read": 0.22,
    "look": {"fog": "#2a3446", "fog_density": 0.003, "fog_start": 12.0, "sky": "#9cc4ee", "sky_strength": 1.0,
             "exposure": 0.0, "flash_safe": True},
    "exposure": {"street": 0.0, "kitchen": 0.2, "cinema": 0.3},
    "grade": {"shadows": [-0.01, 0.0, 0.035], "highlights": [0.02, 0.008, -0.01], "saturation": 1.05, "contrast": 1.06,
              "vignette": 0.32, "bloom": 0.2, "grain": 0.011},
    "phonemes": {"Mum": "mˈʌm"},
    "cast": cast,
    "clouds": clouds,
    "umbrellas": umbrellas,
    "lines": lines,
    "shots": shots,
    "acting": acting,
    "cues": cues,
    "fx": [],
    "music": {"root": 50, "mode": "dorian", "bpm": 76, "seed": 39,
              "sections": [
                  {"at": 0, "voices": ["pad", "piano", "pulse"], "energy": 0.4},
                  {"at": "L07", "voices": ["pad", "piano", "pulse"], "energy": 0.45},
                  {"at": "L11", "voices": ["pad", "piano"], "energy": 0.32},
                  {"at": "L17", "voices": ["pad", "piano", "pulse"], "energy": 0.4},
                  {"at": "L22", "voices": ["drone", "piano"], "energy": 0.34},
                  {"at": "L30", "voices": ["pad", "piano"], "energy": 0.3},
                  {"at": "L31", "voices": ["drone", "pad", "piano"], "energy": 0.38},
                  {"at": "L36", "voices": ["drone", "choir"], "energy": 0.4},
                  {"at": "L41", "voices": ["drone"], "energy": 0.25},
                  {"at": "L42", "voices": ["drone", "choir"], "energy": 0.36},
                  {"at": "L45", "voices": ["drone", "pad", "piano"], "energy": 0.4},
                  {"at": "L49", "voices": ["pad", "piano"], "energy": 0.3},
                  {"at": "L53", "voices": ["pad", "piano", "pulse"], "energy": 0.5, "mode": "major", "root": 50},
                  {"at": "L59", "voices": ["pad", "piano", "pulse"], "energy": 0.45, "mode": "major", "root": 50},
                  {"at": "L63", "voices": ["pad", "piano"], "energy": 0.3},
              ]},
    "sound": {"floor": "stone", "steps_db": -22,
              "ambience": [
                  {"kind": "crickets", "from": 0, "to": "L22", "lufs": -40},
                  {"kind": "rain", "from": "L02", "to": "L04", "lufs": -46},
                  {"kind": "rain", "from": "L04", "to": "L06", "lufs": -40},
                  {"kind": "room", "from": "L13", "to": "L22", "lufs": -38},
                  {"kind": "crickets", "from": "L22", "to": "L30", "lufs": -34},
                  {"kind": "crickets", "from": "L31", "to": "L53", "lufs": -34},
                  {"kind": "wind", "from": "L22", "to": "L53", "lufs": -44},
                  {"kind": "rain", "from": "L53", "to": "L59", "lufs": -32},
                  {"kind": "wind", "from": "L59", "to": "end", "lufs": -44},
                  {"kind": "rain", "from": "L62", "to": "end", "lufs": -46},
              ],
              "sfx": sfx,
              "music_drops": [{"from": "L36-0.6", "to": "L36.1", "keep": ["sting"]},
                              {"from": "L42-0.6", "to": "L42.1"}]},
}
OUT.write_text(json.dumps(story, indent=1, ensure_ascii=False) + "\n")
print("wrote", OUT, f"({len(shots)} shots)")
