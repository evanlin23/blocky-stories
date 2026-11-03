"""Writes ../story.json for ep49 "The bell on your collar" (script.md, 2026-11-02).

Run from anywhere: python stories/ep49-car-wash/generator/make_story.py
The words are in lines.json next to this file. Everything else is here: the cast, the shots and their cameras, who
stands where in each shot, the cues set.py reads, the sound and the score.

Places (set.py's metres): the wash at the origin (forecourt y < 0, the tunnel along +y from 0 to 16, the booth in its
left bay at x -3.9 .. -2.1, y 0.5 .. 2.5 with its door on the +y side and its hatch on the +x side), the cafe at
(60, 0), the wedding hall at (60, 30), the street at (60, -30), the flat at (-60, 0), its kitchen at (-60, -20).
A character with yaw 0 faces -y, yaw 180 faces +y, yaw 90 faces +x, yaw -90 faces -x.
"""
import json
import math
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE.parent / "story.json"
lines = json.loads((HERE / "lines.json").read_text())

LOOP = 0.25
for _l in lines:
    if _l["id"] == "L01":
        _l["tempo"] = 1.2
    if _l["id"] == "L03":
        _l["tempo"] = 0.9
lines = lines + [{"id": "P04", "pause": LOOP, "chunks": []}]

# ---------------------------------------------------------------------------------------------------- cast
AUBURN, BLACK = "#7a3a22", "#17161a"


def person(skin, shirt, pants, hair, hair_c, **kw):
    d = {"age": "adult", "skin": skin, "shirt": shirt, "pattern": "solid", "pants": pants, "shoes": "#2a2a2e",
         "sleeves": "long", "hair": hair, "hair_c": hair_c, "hat": "none",
         "face": {"eyes": "round", "brows": True, "ink": "#161012"}}
    d.update(kw)
    return d


GREEN = "#355e45"
cast = {
    "me": person("#e8b88f", "#efe3c8", GREEN, "cap", AUBURN, extras=["apron"], extra_c=GREEN, collar=GREEN,
                 face={"eyes": "round", "brows": True, "ink": "#161012", "freckles": True}),
    "ruben": person("#d9a47a", "#cfc8b6", GREEN, "cap", BLACK, extras=["apron"], extra_c=GREEN, collar=GREEN,
                    hat="beanie", hat_c="#d2a237", height=1.06,
                    face={"eyes": "round", "brows": True, "ink": "#161012"}),
}
# the Stutter: one person five times, each copy a shade greyer
BASE = dict(skin="#d4c1af", shirt="#aebccc", pants="#3f8fcf", hair_c="#1a1b22", extra_c="#3f8fcf")


def tint(h, u):
    r = [int(h[i:i + 2], 16) for i in (1, 3, 5)]
    g = (128, 136, 146)
    return "#" + "".join(f"{int(round(a + (b - a) * u)):02x}" for a, b in zip(r, g))


for k in range(5):
    u = 0.09 * k
    cast[f"st{k}"] = person(tint(BASE["skin"], u), tint(BASE["shirt"], u), tint(BASE["pants"], u), "cap",
                            tint(BASE["hair_c"], u), extras=["apron"], extra_c=tint(BASE["extra_c"], u),
                            shoes=tint("#2a3a52", u), height=1.3, width=0.92, collar=tint("#3f8fcf", u),
                            face={"eyes": "round", "brows": False, "ink": "#0e1116", "pupil": "#050507"})
cast["pie_man"] = person("#d9a47a", "#6b4a30", "#3a3a40", "cap", "#4a3a2a", hat="ballcap", hat_c="#8a8070", width=1.12)
cast["date_a"] = person("#c98f68", "#e4572e", "#2f3140", "long", "#3a2418", pattern="knit", pattern_c="#c9441f")
cast["date_b"] = person("#e0b48e", "#3a9ad9", "#2f3140", "cap", "#2a2a30", pattern="knit", pattern_c="#2f84c0")
cast["bride"] = person("#e8b88f", "#f4eee0", "#f4eee0", "long", "#5a3a28")
cast["groom"] = person("#c98f68", "#7d838c", "#3a3d46", "cap", BLACK, extras=["tie"], extra_c="#8a2f3a")
for i, (sk, sh, hc) in enumerate((("#e0b48e", "#8aa05a", "#3a2a1a"), ("#c98f68", "#a0507a", "#1c1c20"),
                                  ("#d9a47a", "#5a7aa0", "#5a4a3a"), ("#e8b88f", "#d9a441", "#2a2a2a")), 1):
    cast[f"guest{i}"] = person(sk, sh, "#33353c", "cap" if i % 2 else "long", hc)
cast["texter"] = person("#d9a47a", "#9bb7d4", "#9bb7d4", "cap", "#3a2a22", pattern="stripes", pattern_c="#e8eef4")
for i, (sh, hc, ht) in enumerate((("#b5532c", "#2a1c14", "ballcap"), ("#3b6f8f", "#8a6a40", "none"),
                                  ("#7d4a86", "#1a1a1e", "none")), 1):
    cast[f"drv{i}"] = person("#d9a47a" if i != 2 else "#c98f68", sh, "#33353c", "cap", hc, hat=ht,
                             hat_c="#333c4a")
for i, sh in enumerate(("#8a4b6a", "#4a6a8a", "#6a8a4a"), 1):
    cast[f"nb{i}"] = person("#d9a47a", sh, "#40424a", "cap" if i != 2 else "long", "#4a3a2a")
STUT = ["st0", "st1", "st2", "st3", "st4"]
EXTRAS = [n for n in cast if n not in ("me", "ruben") and n not in STUT]


def c(*keys):
    return [list(k) for k in keys]


def still(loc, tgt, lens):
    """A slow drift (3% toward the target, lens +1.5) so no shot sits dead still (quality lift, 2026-11-03)."""
    loc2 = [round(a + (b - a) * 0.03, 3) for a, b in zip(loc, tgt)]
    return c([0, loc, tgt, lens], [1, loc2, tgt, lens + 1.5])


def move(a, b, lens_a, lens_b=None):
    return c([0, a[0], a[1], lens_a], [1, b[0], b[1], lens_b or lens_a])


# ---------------------------------------------------------------------------------------------------- locations
BOOTH_IN = (-3.1, 1.5)
LINE = [(-3.1 + 0.06 * k, 2.7 + 0.7 * k) for k in range(5)]   # the Stutter's line, front at the booth door, facing -y
CAFE, WED, STREET, FLAT, KIT = (60, 0), (60, 30), (60, -30), (-60, 0), (-60, -20)
BED = (-61.0, 1.9)     # the bed's centre; I sit up in it at BED_SEAT
SEAT = (-60.55, 1.9, -0.2)
DRIVER = (-0.45, 0.1, -0.38)    # seat offset in a car

# ---------------------------------------------------------------------------------------------------- shots
# (at, tod, who, cam, step). who: name -> dict(pos, yaw, expr, arms, side, head, lean, then=[(ref, {...}), ...])
SH = []


def shot(at, tod, who, cam, note="", step=2):
    SH.append(dict(at=at, tod=tod, who=who, cam=cam, note=note, step=step))


def P(x, y, yaw=0, expr="neutral", **kw):
    return dict(pos=[x, y], yaw=yaw, expr=expr, **kw)


# ---- 01 the bells
# opening recipe v1 (2026-11-03): frame 1 looks straight at a bell mid-ring with a face, pushing in, no wide before L03
PM = (7.4, -14.9)      # in front of the kiosk's cream front wall, facing -y into the sun, camera at -y
shot(0, "day", {"pie_man": P(PM[0], PM[1], 0, "worried")},
     c([0, [PM[0], PM[1] - 3.4, 1.25], [PM[0], PM[1], 1.25], 30], [1.8, [PM[0], PM[1] - 2.7, 1.25], [PM[0], PM[1], 1.25], 30]),
     "the whole head and the bell, the bell swinging, cream kiosk and blue sky behind, pushing in")
shot("L01.4", "day", {"pie_man": P(PM[0], PM[1], 0, "terrified")},
     c([0, [PM[0], PM[1] - 3.0, 1.25], [PM[0], PM[1], 1.25], 32], [1, [PM[0], PM[1] - 2.6, 1.25], [PM[0], PM[1], 1.25], 33]),
     "punch in on the bell under his chin as it RINGS, big, above the caption band")
shot("L02.2", "day", {"pie_man": P(PM[0], PM[1], 0, "terrified")},
     c([0, [PM[0], PM[1] - 2.9, 1.25], [PM[0], PM[1], 1.25], 33], [1, [PM[0], PM[1] - 2.5, 1.25], [PM[0], PM[1], 1.25], 34]),
     "the ding on UP, the bell swinging hard, his face above")
shot("L03", "day", {"date_a": dict(pos=[CAFE[0] - 0.85, CAFE[1] + 0.1], yaw=55, expr="worried", lean=6),
                    "date_b": dict(pos=[CAFE[0] + 0.85, CAFE[1] + 0.1], yaw=-55, expr="worried", lean=6)},
     still([CAFE[0], CAFE[1] - 2.9, 1.4], [CAFE[0], CAFE[1] + 0.1, 1.2], 28), "cafe date")
shot("L04", "day", {"bride": P(WED[0] + 0.45, WED[1] + 1.5, 0, "grin"), "groom": P(WED[0] - 0.45, WED[1] + 1.5, 0, "grin"),
                    "guest1": dict(pos=[WED[0] - 1.6, WED[1] + 4.2], yaw=0, expr="neutral", lean=13),
                    "guest2": dict(pos=[WED[0] - 0.55, WED[1] + 4.6], yaw=0, expr="neutral", lean=13),
                    "guest3": dict(pos=[WED[0] + 0.55, WED[1] + 4.2], yaw=0, expr="neutral", lean=13),
                    "guest4": dict(pos=[WED[0] + 1.6, WED[1] + 4.6], yaw=0, expr="neutral", lean=13)},
     still([WED[0], WED[1] - 1.7, 1.5], [WED[0], WED[1] + 3.2, 1.3], 24), "wedding lean-in")
shot("L05", "night", {"texter": P(STREET[0] - 0.85, STREET[1] + 2.75, 0, "terrified")},
     still([STREET[0] - 0.85, STREET[1] - 0.1, 1.4], [STREET[0] - 0.85, STREET[1] + 2.75, 1.3], 28), "texter at the window")
shot("L05.3", "night", {"nb1": dict(pos=[STREET[0] - 3.3, STREET[1] + 2.0], yaw=0, expr="angry", lean=10),
                        "nb2": dict(pos=[STREET[0] + 0.9, STREET[1] + 2.0], yaw=0, expr="angry", lean=10),
                        "nb3": dict(pos=[STREET[0] + 3.2, STREET[1] + 2.0], yaw=0, expr="angry", lean=10),
                        "texter": P(STREET[0] - 0.85, STREET[1] + 2.75, 0, "terrified")},
     still([STREET[0] - 0.3, STREET[1] - 7.5, 1.5], [STREET[0] - 0.2, STREET[1] + 2.0, 1.3], 20), "street wakes")
shot("L06", "day", {"drv1": P(0, -6, -90, "grin"), "drv2": P(0, -10.8, -90, "worried"), "drv3": P(0, -15.6, -90, "worried")},
     still([-3.8, -4.0, 1.4], [0.2, -9.5, 0.95], 22), "he guns it, the queue winces")
shot("L07", "day", {"me": P(1.4, -3.6, 152, "neutral"), "drv2": P(0, -10.8, -90, "worried"), "drv3": P(0, -15.6, -90, "neutral"),
                    "ruben": P(-1.2, -1.6, 90, "grin")},
     still([2.9, -0.8, 1.45], [-0.3, -8.0, 1.05], 22), "wind: every bell sways but mine")
# ---- 02 Ruben
shot("L08", "day", {"ruben": P(-0.8, -1.0, 0, "grin", arms=[165, 0], side=[0, 0],
                               then=[("L08+0.45", dict(arms=[120, 0])), ("L08+0.9", dict(arms=[165, 0])),
                                     ("L08+1.35", dict(arms=[120, 0]))])},
     still([-0.8, -3.6, 1.5], [-0.8, -1.0, 1.45], 30), "Ruben waves")
shot("L08.2", "day", {}, still([14.0, -17.0, 5.0], [-1.0, 3.0, 1.8], 22), "establishing wash")
shot("L09", "day", {}, still([-0.6, 1.5, 1.4], [-3.2, 1.5, 1.0], 32), "two stools")
shot("L10", "day", {"me": P(2.5, -4.6, 0, "worried", then=[("L10+1.8", dict(pos=[2.5, -8.4]))]),
                    "ruben": P(-0.9, -0.9, 0, "neutral")},
     still([2.5, -13.5, 1.45], [2.3, -4.0, 1.3], 28), "I walk away with a bag")
shot("L11", "day", {"ruben": P(-0.6, -1.0, 0, "worried")}, still([-0.6, -2.6, 1.5], [-0.6, -1.0, 1.5], 40), "his bell")
shot("L12", "day", {"ruben": P(-1.7, -1.0, 55, "grin", arms=[150, 0], then=[("L12.1", dict(expr="worried"))])},
     still([-4.2, -3.5, 1.45], [-1.0, 0.0, 1.1], 26), "waving a car in")
shot("L13", "day", {"ruben": P(-3.1, 1.5, 90, "grin", then=[("L13.1", dict(expr="worried"))])},
     still([-0.5, 1.0, 1.45], [-3.1, 1.6, 1.3], 30), "the till")
shot("L14", "night", {"me": dict(pos=list(SEAT[:2]) + [SEAT[2]], yaw=-40, expr="worried", head=[55, 0], blink=False)},
     still([FLAT[0] - 2.2, FLAT[1] - 0.2, 1.2], [SEAT[0], SEAT[1], 0.95], 26), "night, I look at the wall")
shot("L15", "day", {"ruben": dict(pos=[KIT[0], KIT[1] + 0.2], yaw=0, expr="smirk", arms=[78, 0], side=[-30, 0])},
     still([KIT[0], KIT[1] - 3.0, 1.45], [KIT[0], KIT[1] + 0.2, 1.3], 30), "pats his pocket")
shot("L15.4", "day", {"ruben": dict(pos=[KIT[0] + 0.9, KIT[1] + 0.2], yaw=0, expr="grin", arms=[165, 0]),
                      "me": P(KIT[0] - 0.8, KIT[1] - 1.1, 25, "worried")},
     still([KIT[0] - 0.2, KIT[1] - 3.6, 1.5], [KIT[0] + 0.3, KIT[1] - 0.2, 1.4], 28), "thumbs up")
# ---- 03 Monday
shot("L16", "sunrise", {"me": P(-1.0, -9.0, 0, "neutral")}, still([-1.0, -12.4, 1.5], [-1.0, -9.0, 1.4], 30), "my old overalls")
shot("L17", "day", {"ruben": P(-0.6, -1.0, 0, "grin")}, still([-0.6, -3.0, 1.55], [-0.6, -1.0, 1.55], 40), "he grins")
shot("L18", "day", {"me": P(-3.2, 1.25, -20, "worried", arms=[60, 0])},
     still([-1.0, 1.9, 1.45], [-3.2, 1.0, 1.3], 28), "booth, my sleeve on the lever")
shot("L18.3", "day", {}, still([-2.95, 1.4, 1.35], [-2.95, 0.65, 1.2], 40), "the blue lever drops")
shot("L19", "day", {}, still([0.3, -1.2, 1.2], [0.0, 10.0, 1.4], 24), "brushes with no car")
shot("L20", "day", {"me": P(-1.0, -4.0, 0, "neutral")}, still([-1.0, -4.55, 1.38], [-1.0, -4.0, 1.34], 48), "my bell")
shot("L21", "day", {"ruben": P(3.4, -3.0, 0, "worried", then=[("L21.1", dict(yaw=-50))]), "me": P(-1.4, -9.0, 0, "worried")},
     still([-0.6, -9.2, 1.5], [3.4, -2.5, 1.25], 32), "across the yard his pocket rings")
shot("L22", "day", {}, still([0.9, -1.0, 1.7], [0.0, 10.0, 1.4], 22), "the brushes stop")
shot("L22.1", "day", {}, still([-0.7, 1.2, 3.1], [-0.7, 4.0, 0.0], 24), "five pairs of footprints")
shot("L23", "day", {}, still([-0.7, 0.9, 0.3], [-0.7, 4.0, 0.05], 30), "each fainter")
shot("L24", "day", {}, still([0.0, 7.5, 1.4], [0.0, 13.5, 1.9], 28), "the dryer whistles")
shot("L24.2", "day", {"me": P(-0.5, -1.0, 0, "worried"), "ruben": dict(pos=[0.7, 0.7], yaw=0, expr="smirk", side=[40, 40])},
     still([-0.5, -3.2, 1.5], [-0.3, -0.3, 1.4], 28), "I listen, he shrugs")
shot("L25", "night", {"me": dict(pos=list(SEAT), yaw=-20, expr="neutral", head=[20, 12], blink=False)},
     still([FLAT[0] - 1.6, FLAT[1] - 0.2, 1.25], [SEAT[0], SEAT[1], 1.0], 34), "phone glow on my face")
shot("L26", "night", {}, still([FLAT[0] + 0.5, FLAT[1] + 0.4, 1.3], [FLAT[0] + 3.0, FLAT[1] + 0.6, 1.2], 30), "through the wall")
shot("L26.1", "night", {"me": dict(pos=list(SEAT), yaw=-40, expr="worried", head=[60, 0], blink=False)},
     still([FLAT[0] - 2.2, FLAT[1] - 0.1, 1.2], [SEAT[0], SEAT[1], 0.95], 26), "I look at the wall")
# ---- 04 Tuesday
shot("L27", "over", {"me": P(1.2, -6.5, 0, "worried")}, still([1.0, -11.5, 1.5], [1.2, -6.5, 1.35], 26), "empty opening")
shot("L27.1", "over", {}, still([-3.1, -3.0, 1.45], [-3.1, 1.2, 1.2], 28), "the booth, the stool, the empty hook")
shot("L28", "over", {}, still([0.0, -4.0, 1.5], [0.0, 10.0, 1.5], 22), "mist and slow brushes")
shot("P01", "over", {}, still([0.0, 0.1, 0.78], [0.0, 3.4, 0.2], 30), "empty conveyor, then phone and keys ride out")
shot("L29.2", "over", {"me": P(-0.6, -1.9, 0, "scared")}, still([-0.6, -4.4, 1.5], [-0.6, -1.9, 1.45], 30), "I call")
shot("L30", "over", {"me": P(-0.5, -3.6, 180, "scared", mouth=True)},
     still([0.2, 2.6, 1.5], [-0.5, -3.6, 1.45], 30), "calling down the tunnel")
shot("L31", "over", {}, still([0.0, 7.0, 1.5], [0.0, 13.5, 1.9], 28), "the dryer says it back")
shot("L32", "over", {"me": P(*BOOTH_IN, 90, "worried", arms=[100, 0])},
     still([0.4, 0.3, 1.5], [-2.9, 1.6, 1.3], 30), "alone in the booth")
shot("L33", "over", {}, still([0.2, 23.0, 1.25], [0.0, 14.0, 1.0], 30), "a clean car")
shot("L33.2", "over", {}, still([-3.3, 13.6, 1.0], [-0.9, 17.4, 0.7], 28), "five handprints")
shot("L34", "over", {"st0": P(-3.1, 9.8, 0, "blank")}, still([0.2, -0.6, 1.5], [-3.1, 9.8, 1.6], 50), "a figure at the far end")
shot("L35", "over", {"st0": P(-3.1, 7.0, 0, "blank")}, still([1.0, -1.0, 1.5], [-3.1, 9.0, 1.45], 50), "nearer, under the foam")
shot("L36", "over", {"st0": P(-3.1, 7.0, 0, "blank"), "st1": P(-3.1, 7.7, 0, "blank")},
     still([1.0, -1.0, 1.5], [-3.1, 9.0, 1.45], 50), "and one behind")
shot("L37", "over", {}, still([0.0, -4.6, 1.35], [0.0, 0.0, 0.95], 26), "the chain and its blank disc")
shot("L37.2", "over", {"me": P(*BOOTH_IN, 90, "scared")}, still([-0.4, 1.6, 1.45], [-3.1, 1.6, 1.4], 36), "I stop sending cars in")
# ---- 05 Noon
shot("L38", "noon", {}, still([-3.2, -4.0, 1.4], [2.0, -9.5, 1.0], 24), "the van pulls in")
shot("L38.2", "noon", {}, still([3.2, -12.5, 1.5], [3.2, -8.0, 1.1], 30), "the back full of wax")
shot("L39", "noon", {"ruben": P(4.4, -5.5, 0, "worried", then=[("L39+1.2", dict(expr="grin"))])},
     still([4.4, -8.8, 1.5], [4.4, -5.5, 1.5], 34), "he gets down")
shot("L39.3", "noon", {"me": P(2.2, -5.6, 0, "worried", then=[("L39.3+0.8", dict(expr="smirk"))])},
     still([2.2, -8.8, 1.5], [2.2, -5.6, 1.5], 34), "I realise")
shot("L40", "noon", {}, still([-0.9, 0.8, 1.32], [-2.0, 1.05, 1.1], 46), "the wet ring on the sill")
shot("L41", "noon", {"ruben": P(-2.9, -3.2, 0, "neutral", arms=[78, 78], then=[("L41+0.2", dict(pos=[-0.6, -3.2]))])},
     still([0.8, -6.2, 1.5], [-1.6, -1.8, 1.2], 24), "he carries a drum")
shot("L42", "noon", {"me": P(-1.0, -4.0, 0, "neutral")}, still([-1.0, -4.5, 1.05], [-1.0, -4.0, 1.34], 48), "my bell is still")
# ---- 06 the Stutter
shot("L43", "dusk", {}, still([0.0, -12.0, 1.5], [0.0, 6.0, 1.7], 20), "lamps warm up")
LINE_ALL = {f"st{k}": P(LINE[k][0], LINE[k][1], 0, "blank") for k in range(5)}
shot("L44", "dusk", dict(LINE_ALL), still([1.0, 1.2, 1.55], [-3.0, 4.8, 1.5], 22), "five of them, in a line")
shot("L45", "dusk", dict(LINE_ALL), still([-3.2, 1.15, 1.95], [-3.0, 5.0, 1.75], 26), "down the line, from the booth")
shot("L45.2", "dusk", dict(LINE_ALL), still([-3.1, 1.2, 1.7], [-3.1, 2.7, 1.98], 30), "the front one's face, from the booth")
shot("L46", "dusk", {**LINE_ALL, "ruben": P(-2.62, 1.75, 0, "worried")}, still([-3.1, 0.66, 1.5], [-3.1, 2.7, 0.7], 18), "its bare collar, Ruben's bell in frame")
shot("L47", "dusk", dict(LINE_ALL), still([-0.5, 3.2, 1.75], [-3.1, 2.75, 1.7], 28), "in the booth door")
shot("L48", "dusk", {**LINE_ALL, "me": P(-1.5, 1.0, 180, "scared"), "ruben": P(-0.7, 1.0, 180, "scared")},
     still([-0.3, 4.3, 1.55], [-1.1, 1.0, 1.4], 26), "I stand where I used to")
shot("P02", "dusk", dict(LINE_ALL), still([-0.9, 3.0, 1.45], [-3.0, 4.5, 1.3], 20), "hold")
HEADS = [88, 77, 58, 45, 36]      # each head turns toward me at (-1.3, 3.0)
shot("L49", "dusk", dict(LINE_ALL), still([-0.5, 3.6, 1.45], [-3.1, 3.6, 1.4], 18), "TEST: the heads turn")
shot("L49.2+0.3", "dusk", dict(LINE_ALL), still([-0.5, 5.4, 1.45], [-3.1, 5.4, 1.4], 18), "the last three")
ME_FACE = (-1.45, 2.7)
LEAN0 = {**LINE_ALL, "st0": P(LINE[0][0], LINE[0][1], 90, "blank", lean=5,
                              then=[("L50+0.3", dict(lean=10, blend=0.6))])}
LEAN1 = {**LINE_ALL, "st0": P(LINE[0][0], LINE[0][1], 90, "blank", lean=10,
                              then=[("L50.2+0.1", dict(lean=28, blend=1.9))])}
shot("L50", "dusk", {**LEAN0},
     move([-0.9, 3.55, 1.6], [-1.15, 3.4, 1.58], 30, 30) if False else c([0, [-1.0, 2.8, 1.75], [-2.5, 2.75, 1.8], 26], [1, [-1.2, 2.78, 1.68], [-2.2, 2.78, 1.65], 22]),
     "it turns and leans in, over my shoulder")
shot("L50.2", "dusk", LEAN1,
     c([0, [-1.3, 2.78, 1.66], [-2.0, 2.78, 1.62], 20], [1, [-1.3, 2.78, 1.66], [-2.0, 2.78, 1.62], 20]),
     "its leaning face level with mine, lit from below")
# ---- 07 the clapper
shot("L51", "dusk", {**LINE_ALL, "me": P(ME_FACE[0], ME_FACE[1], -90, "scared", then=[("L51+0.2", dict(pos=[-1.35, 1.4], keep_yaw=True))])},
     still([-1.35, 0.3, 0.3], [-1.35, 2.7, 0.2], 34), "my boots back away")
shot("L52", "dusk", {"ruben": P(-1.0, 0.4, 0, "smirk")}, still([-1.0, -1.8, 1.4], [-1.0, 0.4, 1.35], 34), "his pocket rings")
shot("L53", "dusk", {}, still([-0.9, 0.7, 1.35], [-2.0, 1.0, 1.1], 44), "onto the sill")
shot("L54", "dusk", {}, still([-1.5, 0.95, 1.24], [-2.0, 1.02, 1.13], 70), "the clapper")
shot("L54.1+0.3", "dusk", {"me": P(-1.55, 1.5, -90, "worried")}, still([-3.0, 1.5, 1.3], [-1.7, 1.5, 1.2], 42), "my bell's empty mouth")
shot("L55", "dusk", {"ruben": P(-1.4, 1.2, -90, "smirk")}, still([-3.0, 1.7, 1.45], [-1.5, 1.2, 1.45], 38), "he carried it")
shot("L55.2", "dusk", {"me": P(-1.4, 1.5, -90, "worried")}, still([-3.0, 1.4, 1.45], [-1.5, 1.5, 1.45], 38), "me, softening")
shot("L56", "dusk", {"me": P(-1.45, 1.0, 180, "worried"), "ruben": P(-0.4, 1.0, 180, "smirk")},
     still([-0.95, 4.3, 1.5], [-0.95, 1.0, 1.5], 30), "my face, worried softening, Ruben beside me, nothing in front")
shot("L57", "dusk", {**{f"st{k}": P(LINE[k][0], LINE[k][1], 0, "blank") for k in range(5)},
                    "me": P(-1.0, 1.0, 20, "neutral", head=[0, 30], then=[("L57+1.3", dict(yaw=-35, head=[0, -4], blend=0.7))])},
     still([0.3, -0.2, 1.5], [-1.5, 1.8, 1.5], 28), "every ring was mine: my eyes go from the clapper up to the line of five")
shot("L58", "dusk", {"ruben": P(-1.0, 0.6, 0, "neutral")}, still([-1.0, -0.1, 1.38], [-1.0, 0.6, 1.33], 48), "his still bell")
shot("L59", "dusk", {"me": P(-1.2, 1.2, 0, "smirk")}, still([-1.2, -0.7, 1.55], [-1.2, 1.2, 1.5], 36), "a quiet bell means go")
shot("L60", "dusk", {"me": P(-1.0, 0.6, 0, "smirk")}, still([-1.0, -1.0, 1.36], [-1.0, 0.6, 1.2], 40), "the clapper goes home")
shot("L61", "dusk", {"ruben": P(-0.8, 0.8, 0, "grin", then=[("L61.1", dict(head=[0, 12])), ("L61.2", dict(head=[0, -4]))])},
     still([-0.8, -1.0, 1.5], [-0.8, 0.8, 1.5], 34), "partner?")
shot("L62", "dusk", {**{f"st{k}": P(LINE[k][0], LINE[k][1], 0, "blank") for k in range(1, 5)},
                     "me": P(-0.2, 3.0, -90, "neutral", then=[("L62+0.2", dict(pos=[-1.8, 3.0])), ("L62+1.4", dict(pos=[-1.8, 3.0], yaw=-90))])},
     still([1.6, 5.6, 1.5], [-1.4, 3.3, 1.4], 24), "side-on, I walk toward the line; the front copy is gone")
shot("L63", "dusk", {"me": P(-3.1, 2.5, 0, "smirk")}, still([-3.1, 0.8, 1.36], [-3.1, 2.5, 1.2], 40), "my bell stays quiet")
shot("P03", "dusk", {}, still([-1.6, 1.1, 1.55], [-2.0, 1.95, 1.12], 34), "the lore shot: two strokes")
shot("L64", "dusk", {**{f"st{k}": P(LINE[k][0], LINE[k][1], 0, "blank") for k in range(1, 5)}},
     still([-0.8, 3.0, 1.45], [-3.1, 4.4, 1.3], 20), "they fade, front to back")
# ---- 08 partners
shot("L65", "sunrise", {"me": P(*BOOTH_IN, 90, "smirk")}, still([-0.9, 1.5, 1.45], [-3.1, 1.5, 1.35], 32), "I'm in the booth at seven")
shot("L66", "sunrise", {"me": P(*BOOTH_IN, 90, "grin", arms=[160, 0])}, still([2.8, -2.8, 1.4], [-1.6, 0.8, 1.2], 24), "I wave the first car in")
shot("L67", "sunrise", {}, still([-0.7, 1.2, 3.1], [-0.7, 4.0, 0.0], 24), "S28's angle down the conveyor at sunrise: no footprints")
shot("L68", "sunrise", {"me": P(-1.5, 18.2, 180, "smirk"), "ruben": P(1.5, 18.2, 180, "grin")},
     still([0.0, 23.0, 1.5], [0.0, 16.5, 1.3], 24), "side by side, the car comes out shining")
shot("L69", "sunrise", {"me": P(-0.45, 18.5, 180, "smirk"), "ruben": P(0.45, 18.5, 180, "smirk")},
     still([0.0, 21.8, 1.25], [0.0, 18.5, 1.1], 21), "two bells, two collars")
shot("L70", "dusk", {f"st{k}": P(LINE[k][0], LINE[k][1], 0, "blank", head=[HEADS[k], 0]) for k in range(5)}, still([1.0, 5.4, 1.55], [-2.6, 3.4, 1.5], 24), "a cold cut back: the front copy in the booth door under the lamps")
shot("L71", "sunrise", {"me": P(*BOOTH_IN, 90, "neutral")},
     still([-2.4, 1.0, 1.04], [-3.1, 1.45, 1.29], 48), "my collar bell, the clapper inside")
shot("L72", "sunrise", {"me": P(*BOOTH_IN, 90, "neutral", arms=[15, 0], then=[("L72+0.3", dict(arms=[50, 0], blend=0.8, yaw=90)), ("L72>", dict(expr="worried", yaw=90))])},
     still([-0.9, 1.5, 1.45], [-3.1, 1.5, 1.35], 32), "my bell rings and my hand stops short")

# ---------------------------------------------------------------------------------------------------- build shots + acting
shots = []
for i, s in enumerate(SH):
    d = {"id": f"S{i + 1:02d}", "cam": s["cam"], "hand": 0.01, "step": s["step"], "what": s["note"]}
    if i:
        d["at"] = s["at"]
    shots.append(d)

NEUTRAL = {"arms": [0, 0], "side": [0, 0], "head": [0, 0], "lean": 0, "tremble": 0, "blink": True}
acting = {n: [] for n in cast}
visible = {n: None for n in cast}


def put(who, at, pos, **kw):
    keys = acting[who]
    prev = next((k["pos"] for k in reversed(keys) if "pos" in k), None)
    if prev is not None:
        keys.append({"at": at, "pos": prev})
    keys.append({"at": at, "pos": pos, "blend": 0, "hidden": False, **NEUTRAL, **kw})


def hide(who, at):
    acting[who].append({"at": at, "hidden": True, "blend": 0})


for i, s in enumerate(SH):
    ref = s["at"]
    for n in cast:
        if n in s["who"]:
            w = dict(s["who"][n])
            then = w.pop("then", [])
            pos = w.pop("pos")
            w.pop("pos3", None)
            talk = w.pop("mouth", False)
            if n.startswith("drv"):
                pos = [pos[0] + DRIVER[0], pos[1] + DRIVER[1]] if False else pos
            if n.startswith("drv") or (n == "drv2" and False):
                pass
            put(n, ref, pos, **w)
            visible[n] = True
            for r, kw in then:
                k = {"at": r, **kw}
                acting[n].append(k)
            if talk:
                acting[n].append({"from": ref, "to": f"{ref}+1.6", "mouth": [0.5, 0.5], "flap": True})
        elif visible[n] is not False:
            hide(n, ref)
            visible[n] = False

# the Stutter's heads turn to me one after another (L49), the front one leans in (L50) and goes (L62)
for k in range(5):
    acting[f"st{k}"].append({"at": f"L49+{1.0 + 0.5 * k:.2f}", "head": [HEADS[k] * 1.0, 0], "blend": 1.0})
# (heads were held at their turn through to L62; the front copy is hidden by the L62 shot's cast)

# ---------------------------------------------------------------------------------------------------- cues
cues = []
last_tod = None
for s in SH:
    if s["tod"] != last_tod:
        cues.append({"at": s["at"], "name": "tod", "set": s["tod"]})
        last_tod = s["tod"]


def cue(at, name, **kw):
    cues.append({"at": at, "name": name, **kw})


def ring(who, at, dur=0.0, rate=3.0, amp=1.0):
    cue(at, "ring", who=who, dur=dur, rate=rate, amp=amp)


# riders and the queue
for who, carkey, pos in (("drv1", "q1", (0, -6)), ("drv2", "q2", (0, -10.8)), ("drv3", "q3", (0, -15.6))):
    cue(0, "ride", who=who, car=carkey, off=list(DRIVER))
    cue(0, "car:" + carkey, pos=[pos[0], pos[1]], yaw=0, on=True)
cue("L08", "car:q1", pos=[0, -6], yaw=0, on=False)
cue("L08", "car:q2", pos=[0, -6], yaw=0, on=False)
cue("L08", "car:q3", pos=[0, -6], yaw=0, on=False)
# L06: the driver guns it into the lane
cue("L06", "car:q1", pos=[0, -6], to=[0, 2.0], move=1.6, yaw=0, on=True)
cue("L07", "car:q1", pos=[0, -6], yaw=0, on=True)
# L12: a car waved into the tunnel
cue("L12", "car:q1", pos=[0, -5.0], to=[0, 3.0], move=2.6, yaw=0, on=True)
cue("L13", "car:q1", pos=[0, 3.0], yaw=0, on=False)
cue("L12", "ride", who="drv1", car=None)
# Tuesday: a car to the hatch at L32 (no driver), the silver car out at L33, handprints
cue("L32", "car:q2", pos=[0, -5.0], to=[0, -2.0], move=1.8, yaw=0, on=True)
cue("L33", "car:q2", pos=[0, -2.0], yaw=0, on=False)
cue("L33", "car:silver", pos=[0, 10.0], to=[0, 17.5], move=2.6, yaw=0, on=True)
cue("L33.2", "car:silver", pos=[0, 17.5], yaw=0, on=True)
cue("L33.2", "hand", on=True)
cue("L34", "car:silver", pos=[0, 17.5], yaw=0, on=False)
cue("L34", "hand", on=False)
cue("L35", "car:silver", pos=[0, 5.0], to=[0, 11.0], move=1.2, yaw=0, on=True)
cue("L35+1.2", "car:silver", pos=[0, 11.0], yaw=0, on=False)
cue(0, "car:silver", pos=[0, 0], yaw=0, on=False)
# the van at noon
cue("L38", "car:van", pos=[3.0, -14.0], to=[3.0, -6.0], move=2.4, yaw=0, on=True)
cue("L38.2", "car:van", pos=[3.0, -6.0], yaw=0, on=True)
cue("L40", "car:van", pos=[3.0, -6.0], yaw=0, on=False)
cue("L41", "car:van", pos=[3.0, -6.0], yaw=0, on=False)
# the red hatchback rolls into the lane at L66, then out of the tunnel at L68
cue("L66", "car:red", pos=[0, -6.0], to=[0, 0.5], move=2.0, yaw=0, on=True)
cue("L67", "car:red", pos=[0, 0.5], yaw=0, on=False)
cue("L68", "car:red", pos=[0, 10.5], to=[0, 14.8], move=3.4, yaw=0, on=True)
cue("L69", "car:red", pos=[0, 14.8], yaw=0, on=True)
cue("L70", "car:red", pos=[0, 14.8], yaw=0, on=False)
# the beanie leaves its hook, the chain, the tell-tale marks
cue("L27", "beanie", on=False)
cue("L33.2", "sil", v=1.0, dur=1.5)
cue("L33.2", "mist", v=0.12, dur=1.5)
cue("L37", "sil", v=0.0, dur=0.6)
cue("L37", "mist", v=1.0, dur=1.0)
cue("L37", "chain", on=True)
cue("L65", "chain", on=False)
cue("L22", "foot", on=True)
cue("L27", "foot", on=False)
cue("L40", "ring_mark", on=True)
cue("L41", "ring_mark", on=False)
cue("L10", "bag", on=True)
cue("L11", "bag", on=False)
cue("L41", "carry", on=True)
cue("L42", "carry", on=False)
# phone and keys ride out of the mist, then Ruben takes them back
cue("L29", "item:phone", pos=[0.16, 3.6, 0.35], to=[0.16, -0.2, 0.35], move=1.5, yaw=10)
cue("L33", "item:phone", pos=[0.16, -0.2, 0.35], yaw=10, on=False)
cue("L29", "item:keys", pos=[-0.2, 3.9, 0.3], to=[-0.2, 0.1, 0.3], move=1.5, yaw=0)
cue("L33", "item:keys", pos=[-0.2, 0.1, 0.3], yaw=0, on=False)
cue("L53+0.2", "item:clapper", pos=[-2.0, 1.0, 1.3], to=[-2.0, 1.0, 1.158], move=0.22)
cue("L53+0.6", "item:clapper", pos=[-2.0, 1.0, 1.158])
cue("L60", "item:clapper", pos=[-2.0, 1.0, 1.158], on=False)
cue("L60", "clapper", on=True)
# light and weather: slow ramps only
cue("L27", "mist", v=1.0, dur=3.2)
cue("L28>", "mist", v=0.4, dur=0.9)
cue("L38", "mist", v=0.25, dur=1.2)
cue("L43", "mist", v=0.12, dur=1.2)
cue("L65", "mist", v=0.0, dur=1.5)
cue("L43", "dry", v=1.0, dur=1.2)
cue("L45", "boothoff", v=1.0, dur=1.0)
cue("L47", "boothoff", v=0.0, dur=0.6)
cue("L46-0.4", "collarlit", v=1.0, dur=0.4)
cue("L46>", "collarlit", v=0.0, dur=0.4)
cue("L49.2", "leankey", v=1.0, dur=0.6)
cue("L51+0.6", "leankey", v=0.0, dur=0.6)
cue("L19", "spin", v=0.7, dur=1.5)
cue("L22", "spin", v=0.0, dur=1.5)
cue("L27", "spin", v=0.2, dur=1.0)
cue("L38", "spin", v=0.0, dur=1.5)
cue("L18.3", "lever", v=1.0, dur=0.9)
cue("L19", "lever", v=1.0, dur=0.1)
cue("L22", "lever", v=0.0, dur=1.0)
# bells: rings and the wind
cue(0, "sway", who=["drv1", "drv2", "drv3", "ruben", "pie_man"], dur=0.01)
ring("pie_man", 0, dur=2.4, rate=2.6, amp=1.7)
ring("pie_man", "L01.4", amp=1.4)
ring("pie_man", "L02.2+0.3", amp=1.6)
ring("date_a", "L03", dur=2.0, rate=3.2)
ring("date_b", "L03+0.1", dur=2.0, rate=3.6)
ring("texter", "L05", dur=2.4, rate=4.2, amp=1.2)
ring("drv1", "L06.0", amp=1.4)
cue("L07", "sway", who=["drv2", "drv3", "ruben", "date_a"], dur=2.2)
ring("drv1", "L06+0.3", dur=0.8, rate=3.0)
ring("me", "L72>")
cue("L21.1", "pocket")
cue("L52", "pocket")
# the Stutter: heads and lean live in acting; the fades are here
for k in range(1, 5):
    cue(f"L64+{0.6 * (k - 1):.2f}", "fade", k=k, dur=0.6)

# ---------------------------------------------------------------------------------------------------- sound
def ding(at, db=-16, pitch=2200, lp=None, **kw):
    d = {"at": at, "kind": "ding", "db": db, "pitch": pitch, "dur": 0.9}
    if lp:
        d["lp"] = lp
    d.update(kw)
    return d


sfx = [
    ding(0.15, -24, 2050),
    ding(0.75, -24, 2050),
    ding("L01.4", -12, 2050),
    ding("L02.2+0.3", -8, 2050),
    *[ding(f"L03+{0.3 * k:.1f}", -19, 2100 + 130 * (k % 3)) for k in range(3)],
    *[ding(f"L05+{0.4 * k:.2f}", -17, 2400 - 80 * (k % 4)) for k in range(4)],
    ding("L06+0.1", -14, 2150),
    {"at": "L06+0.3", "kind": "whirr", "db": -22, "dur": 1.4},
    ding("L11.1", -19, 2200, lp=1400),
    ding("L12.1", -17, 2200, lp=1400),
    ding("L13.1", -17, 2200, lp=1400),
    ding("L14.2", -20, 2200, lp=900),
    {"at": "L19+0.1", "kind": "whirr", "db": -16, "dur": 2.4},
    {"at": "L18.3+0.3", "kind": "click", "db": -14},
    ding("L21.1", -17, 2200, lp=1400),
    {"at": "L24", "kind": "whistle", "db": -22, "dur": 2.4, "pitch": 740},
    ding("L26+0.15", -20, 2200, lp=900),
    {"at": "P01+0.15", "kind": "clank", "db": -18},
    {"at": "P01+0.55", "kind": "clank", "db": -18},
    {"at": "L29", "kind": "hit", "db": -9},
    {"at": "L31", "kind": "whistle", "db": -18, "dur": 1.8, "pitch": 700, "name": True},
    {"at": "L34", "kind": "riser", "db": -26, "dur": 2.0},
    {"at": "L43", "kind": "riser", "db": -24, "dur": 1.4},
    {"at": "L49+0.1", "kind": "hit", "db": -13, "keep": True},
    ding("L52", -18, 2200, lp=1400),
    {"at": "L53+0.35", "kind": "click", "db": -10},
    {"at": "L60", "kind": "ding", "db": -20, "pitch": 1950, "dur": 0.9},
    ding("L72>", -18, 1900, fall=0.35),
    # recorded impacts where beats land (quality lift, 2026-11-03)
    {"at": "L19+0.2", "kind": "thud", "db": -18},
    {"at": "L27", "kind": "door", "db": -18},
    {"at": "L29+0.3", "kind": "thud", "db": -14},
    {"at": "L34", "kind": "thud", "db": -20},
    {"at": "L38", "kind": "door", "db": -20},
    {"at": "L47", "kind": "door", "db": -16},
    {"at": "L49+0.9", "kind": "thud", "db": -18},
    {"at": "L53", "kind": "latch", "db": -16},
    {"at": "L62+0.3", "kind": "door", "db": -18},
]

story = {
    "slug": "ep49-car-wash",
    "title": "In this town, the bell on your collar rings before every mistake",
    "made_for_kids": False,
    "premise": "In a town where a small brass bell on every collar rings just before its wearer makes a mistake, my bell has never rung. My older brother Ruben runs the car wash on the edge of town alone since I quit the pay booth, and his bell rings all day and all night. When I go back to help, the wash runs with nobody in it, five sets of wet footprints line up in the tunnel, and one morning Ruben is gone from opening, just his phone and keys riding the conveyor out.",
    "twist": "My bell never rang because it couldn't: Ruben has carried my bell's clapper in his pocket since we were teenagers so I'd stop being scared to try things, and every ring I blamed on him was mine. The five faint copies in a line are not keeping my place. They are the ring I never heard the day I quit, still echoing, each a step behind and fainter. When I take the clapper back and walk toward them as his partner, the quitting is undone and the echo dies away front to back.",
    "world": "a small automatic car wash on the edge of a town, autumn weekdays: a concrete forecourt with a painted queue lane, a corrugated tunnel with brushes, a foam arch and a drying arch, and a blue pay booth in its left bay",
    "voice": {"voice": "am_adam", "tempo": 1.03, "rate": 1.45},
    "key_color": "#f0c75e",
    "caption": {"ink": "#08090d", "stroke_add": 2, "shadow": 0.8},
    "key_stroke": 2,
    "gap": 0.12,
    "tail": 0,
    "clip_ok": ["S53/vbody476", "S63/ruben", "S67/bdoorR352", "S67/bdoorframe2355", "S67/st0", "S68/bdoorR352", "S68/bhatchR362", "S85/st3", "S90/ruben", "mist305", "mist307", "mist308", "mist309", "mist310"],
    "look": {"polish": {"quiet": [["L60", "L68"]]}, "fog": "#9aa6b4", "fog_density": 0.012, "fog_start": 14.0, "sky": "#b4d0ea", "sky_strength": 1.1,
             "exposure": 0.0, "flash_safe": True},
    "grade": {"shadows": [-0.02, 0.0, 0.05], "highlights": [0.03, 0.01, -0.02], "saturation": 0.95, "contrast": 1.08,
              "vignette": 0.35, "bloom": 0.22, "grain": 0.012},
    "phonemes": {},
    "cast": cast,
    "lines": lines,
    "shots": shots,
    "acting": acting,
    "cues": cues,
    "fx": [],
    # G dorian at 96 bpm on G2 (midi 43): thin pluck and a short air pad until P01; the heavy low drone enters at the
    # first taking (L29) and holds to the end; a soft major pad lifts over it for the warm turn
    "music": {"root": 43, "mode": "dorian", "bpm": 96, "seed": 49,
              "sections": [
                  {"at": 0, "voices": ["pulse", "pad"], "energy": 0.28},
                  {"at": "L08", "voices": ["pulse", "pad"], "energy": 0.3},
                  {"at": "L16", "voices": ["pulse", "pad"], "energy": 0.34},
                  {"at": "L22", "voices": ["pulse", "pad", "drone"], "energy": 0.32},
                  {"at": "L27", "voices": ["pulse", "pad", "drone"], "energy": 0.38},
                  {"at": "L29", "voices": ["drone", "pad", "pulse"], "energy": 0.55},
                  {"at": "L38", "voices": ["drone", "pad", "pulse"], "energy": 0.45},
                  {"at": "L43", "voices": ["drone", "pad", "choir"], "energy": 0.58},
                  {"at": "L49", "voices": ["drone", "choir", "pad"], "energy": 0.68},
                  {"at": "L57", "voices": ["drone", "pad"], "energy": 0.45},
                  {"at": "L59", "voices": ["drone", "pad", "piano"], "energy": 0.5, "mode": "major"},
                  {"at": "L69", "voices": ["drone"], "energy": 0.4, "mode": "dorian"},
              ]},
    "sound": {"rev": 9, "floor": "metal", "steps_db": -22,
              "ambience": [
                  {"kind": "wind", "from": 0, "to": "L14", "lufs": -38},
                  {"kind": "room", "from": "L14", "to": "L15", "lufs": -38},
                  {"kind": "wind", "from": "L15", "to": "L25", "lufs": -38},
                  {"kind": "room", "from": "L25", "to": "L27", "lufs": -38},
                  {"kind": "wind", "from": "L27", "to": "L43", "lufs": -38},
                  {"kind": "hum", "from": "L43", "to": "L65", "lufs": -38},
                  {"kind": "wind", "from": "L65", "to": "end", "lufs": -40},
              ],
              "sfx": sfx,
              "music_drops": [["P01", "L29"], {"from": "P02", "to": "L49+0.6", "keep": ["hit"]}]},
}
OUT.write_text(json.dumps(story, indent=1, ensure_ascii=False) + "\n")
print("wrote", OUT, f"({len(shots)} shots)")
