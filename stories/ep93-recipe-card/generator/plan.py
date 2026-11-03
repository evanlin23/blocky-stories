"""The edit for ep93: cast, acting, cues and shots.

Chunk refs ("L05.2") are the split caption chunks of the timeline (see lines.json after make_story's split).
Kitchen: x -3.5..3.5, y -3..3 (window north at y 3), stove west, fridge east, table at (0.3, -0.9).
Booths: x 100 (Ito), 120 (fire station), 140 (doorway), 160 (flat). The town street is at x 60 (houses at y -4).
"""


def person(skin, shirt, pants, shoes, hair="cap", hair_c="#2a1d15", pattern="solid", pattern_c=None, hat="none",
           hat_c="#333333", extras=(), eyes="round", sleeves="long", height=1.0, **kw):
    d = {"age": "adult", "skin": skin, "shirt": shirt, "pattern": pattern, "pants": pants, "shoes": shoes,
         "sleeves": sleeves, "hair": hair, "hair_c": hair_c, "hat": hat, "hat_c": hat_c, "height": height,
         "face": {"eyes": eyes, "brows": True, "ink": "#24131f"}}
    if pattern_c:
        d["pattern_c"] = pattern_c
    if extras:
        d["extras"] = list(extras)
    d.update(kw)
    return d


cast = {
    "me": person("#efc08f", "#e0a82a", "#3b5a8c", "#f4f4f2", hair="swoop", hair_c="#6a4426", pattern="knit",
                 pattern_c="#c98f1a", height=1.0),
    "nell": person("#f1cfae", "#d8334a", "#7a4a5a", "#6a3a3a", hair="bun", hair_c="#f4f4f6", extras=["glasses", "apron"],
                   extra_c="#f6ecda", eyes="lashes", height=0.93, glasses_c="#6a4a2a"),
    "mom": person("#e8b890", "#3f9a5a", "#4a4036", "#3a2a1a", hair="cap", hair_c="#a0522d", eyes="lashes", height=0.97),
    "dad": person("#e0ac80", "#c0602a", "#3a4a6a", "#4a3a2a", hair="buzz", hair_c="#9a9a9a", pattern="plaid",
                  pattern_c="#6a3a1a", height=1.04, width=1.08),
    "ito": person("#c8946a", "#2a7ab0", "#3a3a44", "#2a2a2a", hair="buzz", hair_c="#555555", pattern="stripes",
                  pattern_c="#e8f0f4", extras=["apron"], extra_c="#fff4dc", height=1.0),
    "ff": person("#e8b890", "#e8c02a", "#3a3a44", "#2a2a2a", hair="buzz", hair_c="#3a2a1a", hat="bucket",
                 hat_c="#d8334a", height=1.02),
    "nw": person("#c98f66", "#e07ab0", "#4a5a8a", "#f4f4f2", hair="long", hair_c="#2a1a14", eyes="lashes", height=0.97),
    "gy": person("#f0c8a0", "#8a8fa0", "#4a5a8a", "#d8d0c0", hair="spiky", hair_c="#5a3a22", height=1.0),
}

acting = {n: [{"at": 0, "hidden": True, "pos": [0, 0]}] for n in cast}
last = {n: [0, 0] for n in cast}
cues = []
SH = []
HOLD = []
SET_MOVES = []
CLIP_OK = []


def put(who, at, pos, yaw=0, **kw):
    """Appear (or jump) to pos on `at`."""
    acting[who].append({"at": at, "pos": list(last[who])})
    k = {"at": at, "pos": list(pos), "blend": 0.0, "hidden": False, "yaw": yaw}
    k.update(kw)
    acting[who].append(k)
    last[who] = list(pos)


def hold(who, at, **kw):
    acting[who].append({"at": at, "pos": list(last[who]), **kw})


def hide(*whos, at):
    for w in whos:
        acting[w].append({"at": at, "hidden": True})


def cue(at, name, **kw):
    cues.append({"at": at, "name": name, **kw})


def obj(oid, at, pos=None, rot=(0, 0, 0), dur=0.0, hide=False, flutter=0.0):
    c = {"at": at, "name": "obj", "id": oid}
    if hide:
        c["hide"] = True
    else:
        c.update(pos=list(pos), rot=list(rot))
        if dur:
            c["dur"] = dur
        if flutter:
            c["flutter"] = flutter
    cues.append(c)


def hold_obj(oid, at, who, arm=1, off=(0, -0.1, 0), rot=(0, 0, 0), flutter=0.0):
    c = {"at": at, "name": "hold", "id": oid, "who": who, "arm": arm, "off": list(off), "rot": list(rot)}
    if flutter:
        c["flutter"] = flutter
    cues.append(c)


def fly(oid, at, p0, p1, dur, r0=(0, 0, 0), r1=(0, 0, 0), flutter=10.0):
    obj(oid, at, p0, r0)
    obj(oid, f"{at}+0.03", p1, r1, dur=dur, flutter=flutter)


def sit(who, at, on=True, z=0.45):
    cue(at, "sit", who=who, on=on, z=z)


def look(at, id_, dur=0.8):
    cue(at, "look", id=id_, dur=dur)


def _width(L):
    """The size class (the old 'lens' number) as a frame width in metres at the target."""
    if L < 0:
        return -L
    if L <= 30:
        return 2.8 + (30 - L) * 0.5
    if L <= 42:
        return 2.6 - (L - 30) * 0.07
    return max(0.5, 1.1 * (42.0 / L) ** 1.4)


def _lens(frm, to, L):
    d = sum((a - b) ** 2 for a, b in zip(frm, to)) ** 0.5
    return round(min(80.0, max(14.0, 13.5 * d / _width(L))), 1)


def S(at, frm, to, lens=32, frm2=None, to2=None, hand=None):
    keys = [[0, list(frm), list(to), _lens(frm, to, lens)]]
    if frm2 is not None:
        t2 = list(to2 if to2 is not None else to)
        keys.append([1, list(frm2), t2, _lens(frm2, t2, lens)])
    SH.append((at, keys, hand, None))


# ================================================================================================ the cues that run all film
look(0, "gold")
cue(0, "tin", open=0.0)
for t_, k in [(0, "old"), ("L23", "old0"), ("L25", "new0"), ("L27", "new1"), ("L28", "new9"), ("L29", "new20"),
              ("L31", "new39"), ("L36", "new40"), ("L41", "new41"), ("L51", "new41s")]:
    cue(t_, "inset", state=k)
cue("L53", "inset_fly", **{"from": "new41s"})
cue("L38", "tex", id="card_old", tex="card_old_wet")
cue("L59", "tex", id="card_old", tex="card_old")
cue("L48.3", "tex", id="card_new", tex="card_new_line")
cue("L51", "tex", id="card_new", tex="card_new_stain")

# ================================================================================================ 01 the hook (L01 to L02)
# Grandma holds the card up to the camera over the table; my list lies on the table
put("nell", 0, [0.3, 0.8], 0, expr="smile", arms=[0, 80])
obj("card_old", 0, [0.5, 0.38, 1.25], (0, 0, 0), flutter=2)
obj("list", 0, [0.0, 0.02, 0.795], [-90, 0, 8])
S(0, [0.4, -0.75, 1.5], [0.35, 0.3, 1.02], 44)                                          # S001 the card, close
S("L01.3", [0.5, -0.3, 1.3], [0.5, 0.38, 1.22], 62, [0.5, -0.1, 1.28], [0.5, 0.38, 1.22])    # S002 the matching loops
hide("nell", at="L02")
obj("card_old", "L02", hide=True)
obj("list", "L02", hide=True)
put("me", "L02", [0.3, 0.9], 0, expr="worried", arms=[0, 70], head=[0, 10])
hold_obj("pen", "L02", "me", arm=1, off=(0, -0.1, 0.0), rot=(60, 0, 0))
S("L02", [0.7, -0.8, 1.55], [0.3, 0.9, 1.45], 36)                                         # S003 me uneasy

# ================================================================================================ 02 the town (L03 to L08)
hide("me", at="L03")
obj("pen", "L03", hide=True)
fly("card_m1", "L03", [57.1, -1.75, 1.9], [57.6, 0.8, 7.0], 1.9, (0, 0, 0), (25, 10, 40), 14)
S("L03", [56.0, 9.0, 2.2], [57.2, -2.0, 3.4], -7.0)                                          # S004 a card lifts from a window
for i in range(6):
    x0 = 50 + i * 4.0
    fly(f"fl{i}", "L03.1", [x0, -1.6, 2.2], [x0 + 3 - i * 0.6, 1.5 - (i % 3), 6.0 + (i % 3) * 1.0], 1.9,
        (0, 0, 0), (30, 15, 90 + i * 30), 16)
S("L03.2", [58.0, 9.0, 3.2], [60.0, -3.0, 6.0], -10.0, [58.6, 9.0, 3.4], [60.2, -3.0, 6.2])    # S005 cards over the roofs
obj("card_m1", "L04", hide=True)
for i in range(6):
    obj(f"fl{i}", "L04", hide=True)
fly("card_m5", "L04", [52.0, 4.2, 2.0], [60.0, 4.4, 1.6], 1.0, (0, 0, 10), (10, 0, -20), 10)
obj("card_m5", "L04.2", [60.0, 4.4, 1.6], (10, 0, -20))
obj("card_m5", "L04.2+0.02", [64.5, 6.4, 2.6], (20, 10, -70), dur=1.1, flutter=10)
S("L04", [57.0, 9.0, 2.0], [58.0, 4.0, 1.8], -5.0, [57.0, 9.0, 2.0], [60.0, 4.2, 1.7])       # S006 a card glides down the street
S("L04.2", [61.0, 8.0, 3.0], [64.0, 5.0, 2.2], -5.0)                                         # S007 and turns the corner
obj("card_m5", "L05", hide=True)

# L05 Mr. Ito (booth 1), the fire station (booth 2)
put("ito", "L05", [100.2, -1.55], 180, expr="grin", arms=[50, 50])
S("L05", [101.2, 1.6, 1.5], [100.2, -1.2, 1.3], 30)                                         # S008 Ito at his island
obj("card_m6", "L05.2", [99.9, -0.85, 1.0], (0, 0, 0))
obj("card_m6", "L05.2+0.02", [100.4, -0.5, 2.6], (15, 0, 40), dur=0.8, flutter=14)
S("L05.2", [99.2, 0.9, 1.5], [100.0, -0.8, 1.6], 32)                                        # S009 the card leaps
obj("card_m6", "L05.4", hide=True)
hide("ito", at="L05.4")
put("ff", "L05.4", [120.4, -1.5], 180, expr="delighted", arms=[110, 110])
fly("card_m2", "L05.4", [117.6, 0.8, 2.4], [120.3, -1.0, 1.7], 0.7, (0, 0, 20), (0, 0, 0), 10)
S("L05.4", [121.6, 2.0, 1.6], [120.0, -1.0, 1.6], 30)                                        # S010 the firefighter catches it
S("L05.6", [120.9, 0.4, 1.7], [120.4, -1.3, 1.6], 38)                                        # S011 ...close

# L06 Mrs. Bell's pie card, the newlywed's doorstep (booth 3)
hide("ff", at="L06")
obj("card_m2", "L06", hide=True)
put("nw", "L06", [140.0, -1.1], 180, expr="neutral", arms=[0, 0])
S("L06", [141.2, 1.5, 1.5], [140.0, -1.5, 1.2], 30)                                          # S012 doorway full of boxes
fly("card_m3", "L06.1", [139.2, -1.0, 2.6], [140.0, -1.75, 0.07], 0.8, (0, 0, 30), (-90, 0, 0), 8)
S("L06.2", [140.6, 0.6, 1.3], [140.0, -1.7, 0.4], 30)                                        # S013 the card lands on her mat
hold("nw", "L06.3", expr="delighted", arms=[60, 60])
S("L06.3", [140.5, 0.9, 1.5], [140.0, -1.1, 1.4], 34)                                        # S014 delighted

# L07 the guy over his sink (booth 4)
hide("nw", at="L07")
obj("card_m3", "L07", hide=True)
put("gy", "L07", [160.0, -1.35], 90, expr="neutral", arms=[0, 90])
obj("cereal", "L07", [160.15, -1.75, 1.0], (0, 0, 0))
S("L07", [158.2, 0.8, 1.5], [160.0, -1.7, 1.2], 30)                                          # S015 a guy alone with cereal
S("L07.2", [158.6, -0.8, 1.35], [160.0, -2.0, 1.0], 34)                                      # S016 over his sink
fly("card_m4", "L07.3", [160.0, -2.3, 1.9], [160.0, -2.3, 1.7], 0.5, (0, 0, 0), (0, 0, 8), 8)
obj("card_m4", "L07.3+0.6", [160.1, -2.3, 1.7], (0, 0, 4), flutter=10)
S("L07.3", [159.0, -0.6, 1.7], [160.0, -2.4, 1.7], 34)                                       # S017 something at the window
S("L07.5", [160.0, -1.0, 1.7], [160.05, -2.4, 1.7], 40)                                      # S018 the card taps the glass

# L08 inserts: under a jar, under a magnet, shut in a tin (booth 1)
hide("gy", at="L08")
obj("cereal", "L08", hide=True)
obj("card_m4", "L08", hide=True)
obj("card_i1", "L08", [99.0, -1.98, 0.95], (0, 0, 0))
obj("card_i2", "L08", [101.74, -2.0, 1.2], (0, 0, -90))
obj("card_i3", "L08", [100.6, -1.9, 1.35], (0, 0, 0))
S("L08", [99.0, -0.2, 1.3], [99.0, -2.0, 1.1], 40)                                           # S019 under a jar
S("L08.1", [100.8, -0.6, 1.4], [101.8, -2.0, 1.3], 40)                                       # S020 under a magnet
S("L08.2", [100.6, -0.4, 1.3], [100.6, -2.0, 1.15], 40)                                      # S021 shut in a tin

# ================================================================================================ 03 Grandma's kitchen (L09 to L22)
obj("card_i1", "L09", hide=True)
obj("card_i2", "L09", hide=True)
obj("card_i3", "L09", hide=True)
put("nell", "L09", [-2.45, 0.4], -90, expr="smile", arms=[45, 55], head=[70, 0])
hold_obj("spoon", "L09", "nell", arm=1, off=(0.0, -0.12, -0.05), rot=(0, 0, 0))
S("L09", [-1.4,-1.5,1.5], [-2.45, 0.4, 1.35], 34)                                           # S022 Nell at her stove
S("L09.1", [1.2, 1.0, 1.3], [2.2, 2.6, 1.1], 34, [1.6, 1.2, 1.3], [2.2, 2.6, 1.15])         # S023 the bowl of lemons
S("L09.3", [-1.9,-1.9,1.55], [-2.45, 0.4, 1.35], 38)                                          # S024 stirring, from memory
obj("spoon", "L10", hide=True)
put("nell", "L10", [-2.6, -1.55], -90, expr="smile", arms=[0, 70])
cue("L10", "tin", open=1.0, dur=0.6)
obj("card_old", "L10", [-3.27, -1.5, 1.88], (0, 0, 90))
S("L10", [-1.4, -0.4, 1.7], [-3.3, -1.5, 1.6], 34)                                           # S025 the tin on the shelf, opened
S("L10.1", [-2.1, -1.5, 1.8], [-3.3, -1.5, 1.8], 42)                                         # S026 the card in the tin
S("L10.2", [0.2, -0.2, 1.6], [-3.2, -1.5, 1.4], 28)                                          # S027 the shelf, wide
put("nell", "L11", [-1.5, -1.3], 15, expr="smile", arms=[0, 85])
obj("card_old", "L11", [-1.38, -1.75, 1.2], (0, 0, 15))
cue("L11", "tin", open=0.0, dur=0.6)
S("L11", [-1.2, -2.9, 1.35], [-1.4, -1.5, 1.2], 40)                                          # S028 Grandma holds the card up
S("L11.2", [-1.2, -2.7, 1.25], [-1.38, -1.75, 1.2], 56)                                       # S029 close on the writing: mine
S("L12", [-1.3, -2.7, 1.3], [-1.38, -1.75, 1.22], 66, [-1.3, -2.4, 1.15], [-1.38, -1.75, 1.1])  # S030 a seven with a bar
obj("list", "L12.2", [-1.9, -2.0, 1.1], (0, 0, 15))
S("L12.2", [-1.7, -2.9, 1.2], [-1.9, -2.0, 1.1], 60)                                       # S031 my list: the same seven
S("L12.3", [-1.0, -2.9, 1.25], [-1.6, -1.9, 1.15], 48)                                        # S032 both
obj("list", "L13", hide=True)
obj("card_old", "L13", [-3.27, -1.5, 1.88], (0, 0, 90))
put("nell", "L13", [-2.6, -1.55], -90, expr="smile", arms=[0, 70])
cue("L13.1", "tin", open=0.0, dur=0.5)
S("L13", [-1.8, -1.0, 1.85], [-3.3, -1.5, 1.7], 44)                                          # S033 the tin's worn paint
S("L13.1", [-2.0, -1.8, 1.5], [-3.3, -1.5, 1.6], 40)                                         # S034 her hand sets it back

# L14 Sunday dinner
hide("nell", at="L14")
obj("card_old", "L14", hide=True)
put("nell", "L14", [1.6, -0.9], -90, expr="grin", arms=[0, 70])
sit("nell", "L14")
put("dad", "L14", [-1.0, -0.9], 90, expr="smile", arms=[0, 0])
sit("dad", "L14")
put("mom", "L14", [0.3, -2.2], 180, expr="smile", arms=[0, 0])
sit("mom", "L14")
put("me", "L14", [0.3, 0.4], 0, expr="sad-smile", arms=[0, 0])
sit("me", "L14")
hold_obj("spoon", "L14", "nell", arm=1, off=(0.0, -0.15, 0.0), rot=(-70, 0, 0))
S("L14", [-0.8, 1.6, 1.9], [0.3, -0.9, 0.9], 28)                                            # S035 Sunday dinner
S("L14.2", [2.5, -2.6, 1.55], [1.6, -0.9, 1.25], 32)                                         # S036 Grandma points her spoon at me
hold_obj("wedge", "L14.4", "me", arm=1, off=(0.0, -0.2, 0.1))
hold("me", "L14.4", arms=[0, 75], expr="polite")
S("L14.4", [-0.1, -0.9, 1.7], [0.3, 0.4, 1.2], 34)                                          # S037 I squeeze lemon on my bowl
hold("mom", "L15", expr="laugh")
hold("dad", "L15", expr="laugh")
S("L15", [1.0, 0.4, 1.8], [-0.4, -1.6, 1.15], 30)                                            # S038 Mom and Dad laugh
obj("wedge", "L16", hide=True)
S("L16", [0.3, 0.7, 1.7], [0.3, -2.2, 1.3], 36)                                              # S039 Mom waves it off
hold("me", "L16.3", arms=[0, 0], expr="sad-smile")
S("L16.3", [0.9, -2.1, 1.7], [0.3, 0.4, 1.2], 36)                                           # S040 me, embarrassed

# L17 to L22 the card, the stain, the secret
hold("nell", "L17", arms=[0, 82], expr="smile")
obj("tbowl0", "L17", hide=True)
obj("tbowl0", "L20", [1.1, -0.9, 0.78], (0, 0, 0))
obj("card_old", "L17", [1.15, -0.9, 1.22], (0, 0, -90))
obj("spoon", "L17", hide=True)
S("L17", [-0.1, -0.9, 1.45], [1.15, -0.9, 1.2], 44)                                            # S041 the soft edge of the card
S("L17.2", [0.1, -0.9, 1.4], [1.15, -0.9, 1.2], 54)                                        # S042 older than I am
S("L18", [0.2, -0.8, 1.25], [1.15, -0.9, 1.1], 58)                                            # S043 the bottom, the stain
S("L18.2", [0.3, -0.85, 1.15], [1.15, -0.85, 1.1], 70, [0.5, -0.85, 1.12], [1.15, -0.85, 1.1])   # S044 old brown stain
S("L19", [0.55, -0.82, 1.12], [1.15, -0.82, 1.1], 90)                                            # S045 punch in on the boot
S("L19.1", [0.7, -0.8, 1.14], [1.15, -0.78, 1.13], 100)                                        # S046 a little boot
hide("dad", "mom", at="L20")
put("me", "L20", [0.3, 1.7], 0, expr="worried", arms=[0, 82], head=[0, 8])
sit("me", "L20", False)
sit("dad", "L20", False)
sit("mom", "L20", False)
sit("nell", "L20", False)
obj("card_old", "L20", [0.3, 1.25, 1.25], (0, 0, 0))
S("L20", [0.7, -0.9, 1.55], [0.3, 1.5, 1.35], 40)                                            # S047 me squinting at it against the window
S("L20.1", [-0.1, -0.5, 1.5], [0.3, 1.5, 1.35], 46)                                         # S048 the secret step
put("nell", "L21", [0.6, 0.3], 0, expr="smirk", arms=[0, 0])
obj("card_old", "L21", hide=True)
hide("me", at="L21")
S("L21", [0.9, -1.4, 1.35], [0.6, 0.3, 1.3], 34)                                            # S049 Grandma zips her lips
S("L21.1", [0.2, -1.2, 1.3], [0.6, 0.3, 1.35], 40)                                           # S050 won't tell me
hold("nell", "L22", arms=[0, 82], expr="smirk")
obj("card_old", "L22", [0.6, -0.15, 1.22], (0, 0, 0), flutter=4)
S("L22", [0.2, -1.2, 1.4], [0.6, 0.3, 1.3], 34)                                              # S051 she taps the card
S("L22.2", [0.5, -0.6, 1.3], [0.6, 0.3, 1.2], 48)                                            # S052 it's on the card

# ================================================================================================ 04 I try (L23 to L31)
hide("nell", at="L23")
obj("card_old", "L23", hide=True)
put("me", "L23", [-2.45, 0.4], -90, expr="worried", arms=[45, 55], head=[70, 0])
hold_obj("spoon", "L23", "me", arm=1, off=(0.0, -0.12, -0.05))
put("nell", "L23", [1.6, -0.9], -90, expr="smile", arms=[0, 0])
sit("nell", "L23")
S("L23", [0.4, 2.0, 1.9], [-1.2, -0.3, 1.2], 26)                                            # S053 me at her stove, Grandma watching
S("L23.2", [-1.5,-1.5,1.5], [-2.45, 0.4, 1.35], 34)                                          # S054 making it myself
obj("spoon", "L24", hide=True)
hide("me", "nell", at="L24")
sit("me", "L24", False)
sit("nell", "L24", False)
put("me", "L24", [0.3, 0.4], 0, expr="worried", arms=[0, 70], head=[0, 25])
sit("me", "L24")
obj("tbowl2", "L24", hide=True)
obj("tbowl3", "L24", hide=True)
obj("tbowl2", "L27", [0.3, -1.55, 0.78], (0, 0, 0))
obj("tbowl3", "L27", [0.3, -0.25, 0.78], (0, 0, 0))
hold_obj("pen", "L24", "me", arm=1, off=(0, -0.1, -0.02), rot=(70, 0, 0))
obj("card_old2", "L24", [0.05, 0.0, 0.795], (-90, 0, 0))
obj("card_new", "L24", [0.55, 0.0, 0.795], (-90, 0, 0))
S("L24", [0.3, -0.5, 1.7], [0.3, 0.0, 0.8], 36)                                              # S055 my hand writing
S("L24.3", [0.4, -0.6, 1.5], [0.5, 0.0, 0.8], 40)                                            # S056 onto a fresh one
S("L25", [0.3, -0.35, 1.45], [0.3, 0.0, 0.8], 36)                                            # S057 the two cards side by side
S("L25.2", [0.3, -0.2, 1.1], [0.3, 0.0, 0.8], 44)                                            # S058 exactly like hers
S("L26", [0.32, -0.15, 1.0], [0.3, 0.0, 0.8], 60)                                            # S059 every loop
# tasting
obj("pen", "L27", hide=True)
obj("card_new", "L27", hide=True)
obj("card_old2", "L27", hide=True)
sit("me", "L27", False)
put("me", "L27", [-2.45, 0.4], -90, expr="squeeze", arms=[60, 75], head=[70, 0])
hold_obj("spoon", "L27", "me", arm=1, off=(0.0, -0.1, 0.05), rot=(-40, 0, 0))
S("L27", [-1.4,-1.5,1.5], [-2.45, 0.4, 1.35], 34)                                           # S060 me tasting, grimace
S("L27.1", [-2.0,-1.9,1.55], [-2.45, 0.4, 1.35], 38)                                          # S061 too thin
hide("me", at="L28")
obj("spoon", "L28", hide=True)
put("dad", "L28", [-1.3, 1.3], 20, expr="fish", arms=[0, 75])
hold_obj("spoon", "L28", "dad", arm=1, off=(0.0, -0.1, 0.05), rot=(-40, 0, 0))
S("L28", [-0.1, -0.3, 1.5], [-1.3, 1.3, 1.45], 34)                                          # S062 Dad tasting, pucker
S("L28.1", [0.1, 0.4, 1.55], [-1.3, 1.3, 1.5], 38)                                           # S063 too salty
hide("dad", at="L29")
obj("spoon", "L29", hide=True)
for i in range(10):
    obj(f"cbowl{i}", "L29", [-1.6 + (i % 5) * 0.4, 2.5 - (i // 5) * 0.32, 0.95], (0, 0, 0))
S("L29", [-0.4, 0.4, 1.4], [-0.2, 2.5, 1.0], 34)                                            # S064 the counter crowded with bowls
put("mom", "L29.1", [0.3, 1.4], 0, expr="hopeful", arms=[65, 65])
S("L29.1", [0.6, -0.5, 1.6], [0.3, 1.4, 1.45], 34)                                           # S065 Mom, pleading
hide("mom", at="L30")
for i in range(10):
    obj(f"cbowl{i}", "L30", hide=True)
put("nell", "L30", [-1.0, 0.5], 50, expr="neutral", arms=[0, 75])
hold_obj("spoon", "L30", "nell", arm=1, off=(0.0, -0.1, 0.05), rot=(-40, 0, 0))
S("L30", [0.8, -0.8, 1.5], [-1.0, 0.5, 1.3], 34)                                             # S066 Grandma tasting
hold("nell", "L30.2", arms=[0, 60], expr="smirk")
obj("spoon", "L30.2", hide=True)
S("L30.2", [0.5, -0.6, 1.4], [-1.0, 0.5, 1.3], 40)                                          # S067 almost together
S("L30.3", [-0.1, -0.8, 1.45], [-1.0, 0.5, 1.4], 44)                                         # S068 CLOSE
hide("nell", at="L31")
put("me", "L31", [-2.45, 0.4], -90, expr="worried", arms=[45, 55], head=[70, 0])
hold_obj("spoon", "L31", "me", arm=1, off=(0.0, -0.12, -0.05))
S("L31", [-1.3,-1.4,1.5], [-2.45, 0.4, 1.35], 34, [-1.8,-1.8,1.5], [-2.45, 0.4, 1.35])     # S069 thirty-nine, stirring

# ================================================================================================ 05 the card tugs (L32 to L41)
look("L32", "blue", 1.4)
obj("spoon", "L32", hide=True)
put("me", "L32", [0.0, 1.85], 180, expr="worried", arms=[0, 75])
obj("card_new", "L32", [0.0, 2.3, 1.4], (-12, 0, 180), flutter=8)
S("L32", [1.3, 1.2, 1.5], [0.0, 2.2, 1.4], 36)                                              # S070 my card tugging in my hand
S("L32.2", [-1.3, 1.0, 1.5], [0.0, 2.3, 1.4], 38)                                           # S071 toward the window
hold("me", "L33", expr="scared", arms=[0, 90])
obj("card_new", "L33", [0.0, 2.5, 1.5], (-25, 0, 180), dur=0.4, flutter=12)
S("L33", [0.0, 3.8, 1.6], [0.0, 1.9, 1.5], 34)                                              # S072 straining toward the window
S("L33.1", [-0.2, 3.6, 1.6], [0.0, 2.1, 1.5], 38)                                            # S073 like a kite
hide("me", at="L34")
put("me", "L34", [2.15, 1.55], 90, expr="worried", arms=[0, 95])
obj("card_new", "L34", [2.69, 1.95, 1.55], (0, 0, -90), flutter=7)
S("L34", [1.0, 0.2, 1.55], [2.6, 1.8, 1.45], 32)                                             # S074 stuck to the fridge
S("L34.2", [1.9, 0.9, 1.5], [2.69, 1.95, 1.5], 46)                                           # S075 with a magnet
hide("me", at="L35")
S("L35", [1.2, 0.6, 1.5], [2.6, 1.9, 1.4], 34)                                               # S076 it tugged all night
S("L35.3", [1.8, 0.7, 1.5], [2.69, 1.95, 1.5], 50, [2.0, 0.9, 1.5], [2.69, 1.95, 1.5])      # S077 the magnet slides
S("L35.4", [1.5, 1.2, 1.35], [2.69, 1.95, 1.45], 40)                                         # S078 where it was going
put("nell", "L36", [-1.3, -0.1], -95, expr="neutral", arms=[0, 0], look=[-0.8, 0.2])
S("L36", [-0.1, -0.2, 1.5], [-1.3, -0.1, 1.4], 36)                                           # S079 Grandma's eyes go to the tin
S("P01", [-2.0, -1.0, 1.75], [-3.3, -1.5, 1.7], 38)                                          # S080 the tin, steam drifting
# L37 I open the tin
hide("nell", at="L37")
cue("L37", "tin", open=1.0, dur=0.9)
obj("card_old", "L37", [-3.27, -1.5, 1.88], (0, 0, 90))
S("L37", [-2.0, -0.6, 1.85], [-3.3, -1.5, 1.8], 38)                                          # S081 the tin lid lifting
S("L37.1", [-2.2, -1.3, 2.0], [-3.45, -1.5, 1.95], 50)                                       # S082 the tally in the lid
S("L38", [-2.0, -1.4, 1.85], [-3.27, -1.5, 1.85], 54)                                        # S083 the stain, wet
obj("drop", "L38.3", [-3.25, -1.43, 1.78], (0, 0, 0))
obj("drop", "L38.3+0.03", [-3.25, -1.43, 1.62], (0, 0, 0), dur=0.9)
S("L38.3", [-2.0, -1.2, 1.8], [-3.26, -1.45, 1.78], 60)                                      # S084 a bead of soup runs
S("L38.5", [-1.7, -0.9, 1.9], [-3.27, -1.5, 1.8], 48)                                        # S085 just spilled
obj("drop", "L39", hide=True)
cue("L39", "tin", open=0.0, dur=0.5)
obj("card_old", "L39", hide=True)
put("me", "L39", [0.55, 1.7], 180, expr="scared", arms=[0, 60])
put("nell", "L39", [-0.38, 1.7], 180, expr="soft", arms=[65, 0])
S("L39", [0.9,-0.4,1.5], [0.4, 2.1, 1.0], 30)                                              # S086 Grandma's hand on mine
S("L39.1", [2.0,0.9,1.4], [0.4, 2.1, 1.0], 32)                                             # S087 my hand
put("nell", "L40", [-0.2, 0.2], 10, expr="soft", arms=[0, 0])
hide("me", at="L40")
S("L40", [-0.1, -1.6, 1.4], [-0.2, 0.2, 1.3], 34)                                            # S088 Grandma, close
S("L40.1", [0.3, -1.4, 1.35], [-0.2, 0.2, 1.3], 40)                                          # S089 it's tonight
hide("nell", at="L41")
put("me", "L41", [-2.45, 0.4], -90, expr="worried", arms=[45, 55], head=[70, 0])
hold_obj("spoon", "L41", "me", arm=1, off=(0.0, -0.12, -0.05))
S("L41", [-1.5,-1.6,1.5], [-2.45, 0.4, 1.35], 34)                                            # S090 forty-one

# ================================================================================================ 06 the lemon (L42 to L51)
look("L42", "gold", 1.0)
hold("me", "L42", arms=[60, 70], expr="neutral")
hold_obj("spoon", "L42", "me", arm=1, off=(0.0, -0.1, 0.05), rot=(-40, 0, 0))
S("L42", [-2.0,-1.9,1.55], [-2.45, 0.4, 1.35], 38)                                             # S091 I taste it
S("L42.1", [-1.7,-1.0,1.8], [-3.1, 0.4, 1.15], 46)                                          # S092 over the pot
hold("me", "L43", expr="neutral", head=[0, -10])
S("L43", [-1.3,-1.4,1.5], [-2.45, 0.4, 1.35], 38)                                           # S093 it needed something
S("L43.1", [-1.9,-1.9,1.5], [-2.45, 0.4, 1.35], 40)                                           # S094 just a little
S("L44", [1.0, 0.8, 1.35], [2.2, 2.6, 1.15], 38, [1.5, 1.2, 1.4], [2.2, 2.6, 1.15])         # S095 the bowl of lemons
S("L44.2", [1.0, 1.3, 1.4], [2.2, 2.6, 1.15], 44)                                            # S096 to everything
hold("me", "L45", arms=[60, 85], expr="grin")
obj("spoon", "L45", hide=True)
hold_obj("lemon_hand", "L45", "me", arm=1, off=(0.0, -0.1, 0.12))
obj("drop2", "L45.1", [-3.12, 0.4, 1.4], (0, 0, 0))
obj("drop2", "L45.1+0.03", [-3.12, 0.4, 1.26], (0, 0, 0), dur=0.5)
S("L45", [-1.4,-1.6,1.6], [-2.8, 0.4, 1.3], 40)                                            # S097 a squeeze of lemon
S("L45.1", [-1.9,-0.9,1.9], [-3.1, 0.4, 1.3], 50)                                          # S098 one bright drop
obj("drop2", "L46", hide=True)
obj("lemon_hand", "L46", hide=True)
hold("me", "L46", arms=[60, 75], expr="wide")
hold_obj("spoon", "L46", "me", arm=1, off=(0.0, -0.1, 0.05), rot=(-40, 0, 0))
S("L46", [-1.5,-1.5,1.5], [-2.45, 0.4, 1.35], 36)                                         # S099 eyes wide
put("nell", "L47", [-1.5, -0.1], 35, expr="soft", arms=[0, 0])
S("L47", [-0.7, -1.2, 1.5], [-1.7, -0.1, 1.4], 34)                                           # S100 Grandma tastes from my spoon
obj("spoon", "L48", hide=True)
hide("nell", at="L48")
put("me", "L48", [2.15, 1.55], 90, expr="neutral", arms=[0, 95])
obj("card_new", "L48", [2.69, 1.95, 1.55], (0, 0, -90))
obj("card_new", "L48+0.1", [2.55, 1.6, 1.3], (0, 0, 90), dur=0.5)
S("L48", [1.0, 0.2, 1.55], [2.6, 1.8, 1.45], 32)                                             # S101 my card off the magnet
put("me", "L48.1", [2.05, 1.8], 180, expr="neutral", arms=[0, 62])
obj("card_new", "L48.1", [1.4, 2.5, 0.955], (-90, 0, 0))
hold_obj("pen", "L48.1", "me", arm=1, off=(0, -0.08, -0.02), rot=(75, 0, 0))
S("L48.1", [0.9,1.5,1.5], [1.4, 2.5, 0.95], 38)                                            # S102 a pen
S("L48.3", [0.8,1.6,1.4], [1.4, 2.5, 0.95], 44)                                            # S103 writing
S("L48.4", [0.9,1.9,1.25], [1.4, 2.5, 0.95], 52)                                            # S104 the last line
S("L49", [1.0,1.95,1.15], [1.4, 2.5, 0.95], 62)                                             # S105 the fresh line
S("L49.1", [1.1,1.9,1.3], [1.4, 2.5, 0.95], 56)                                            # S106 lemon at the end
obj("pen", "L50", hide=True)
hold_obj("spoon", "L50", "me", arm=1, off=(0.0, -0.1, 0.05), rot=(-50, 0, 0))
obj("drop", "L50.2", [1.5, 2.45, 1.25], (0, 0, 0))
obj("drop", "L50.2+0.03", [1.5, 2.45, 0.97], (0, 0, 0), dur=0.5)
S("L50", [0.8,1.5,1.5], [1.45, 2.45, 1.0], 38)                                             # S107 a drip falls off my spoon
S("L50.3", [1.0,1.8,1.3], [1.45, 2.5, 0.96], 56)                                           # S108 right on top
obj("drop", "L51", hide=True)
S("L51", [1.1,1.9,1.25], [1.4, 2.5, 0.96], 64)                                            # S109 a little boot
S("L51.1", [1.0,2.1,1.05], [1.4, 2.5, 0.96], 80)                                           # S110 the fresh stain

# ================================================================================================ 07 it flies (L52 to L61)
look("L53", "dusk", 1.0)
obj("spoon", "L52", hide=True)
obj("card_new", "L52", [1.4, 2.5, 0.97], (-90, 0, 0))
obj("card_new", "L52+0.03", [1.2, 2.4, 1.5], (-30, 10, 20), dur=1.0, flutter=10)
hold("me", "L52", arms=[0, 0])
S("L52", [0.6,1.5,1.4], [1.3, 2.4, 1.15], 38)                                              # S111 the card lifts off my palm
obj("card_new", "L52.1", [1.2, 2.4, 1.5], (-30, 10, 20), flutter=10)
obj("card_new", "L52.1+0.03", [0.2, 2.9, 1.7], (0, 0, 10), dur=0.9, flutter=10)
S("L52.1", [0.3,1.3,1.6], [0.6, 2.8, 1.6], 34)                                             # S112 it leaves my hand
obj("card_new", "L53", [0.2, 2.9, 1.7], (0, 0, 10), flutter=8)
obj("card_new", "L53+0.03", [-1.0, 12.0, 6.0], (10, 0, 60), dur=3.5, flutter=10)
S("L53", [0.0, 0.8, 1.6], [0.0, 3.0, 1.7], 30)                                               # S113 straight out the window
S("L53.2", [0.0, 1.4, 1.7], [-0.6, 12.0, 6.0], 24, [0.0, 1.4, 1.7], [-1.0, 12.0, 6.0])    # S114 small over the roofs
hide("me", at="L54")
put("nell", "L54", [0.0, 1.8], 180, expr="soft", arms=[0, 0])
S("L54", [0.0, 4.6, 1.5], [0.0, 1.8, 1.4], 30)                                               # S115 Grandma at the window
S("L54.1", [0.5, 4.4, 1.5], [0.0, 1.8, 1.4], 38)                                             # S116 she watches it go
obj("card_new", "L55", hide=True)
look("L55", "gold", 1.2)
hide("nell", at="L55")
S("L55", [1.9, -0.9, 1.55], [3.4, -0.9, 1.55], 32)                                           # S117 the framed photo
S("L55.1", [2.3, -0.9, 1.55], [3.43, -0.9, 1.55], 40)                                        # S118 sixty years ago
S("L55.3", [2.6, -0.9, 1.5], [3.43, -0.94, 1.52], 52)                                        # S119 a card fell out of the air
S("L55.5", [2.5, -0.5, 1.45], [3.43, -0.85, 1.35], 50)                                       # S120 into her soup pot
S("L56", [2.6, -0.9, 1.65], [3.43, -0.9, 1.7], 56)                                           # S121 nineteen, laughing
S("L56.1", [2.7, -0.8, 1.6], [3.43, -0.95, 1.65], 62)                                        # S122 just married
S("L56.2", [2.4, -1.0, 1.55], [3.43, -0.85, 1.5], 46)                                        # S123 and couldn't boil water
S("L57", [2.5, -0.5, 1.4], [3.43, -0.8, 1.3], 52)                                            # S124 she cooked it that night
S("L57.1", [2.5, -0.7, 1.5], [3.43, -0.85, 1.4], 40)                                         # S125 and never stopped
put("nell", "L58", [2.95, -0.1], -80, expr="soft", arms=[0, 98])
obj("card_old", "L58", [2.51, -0.18, 1.25], (0, 0, -80))
S("L58", [1.5, -0.8, 1.45], [2.85, -0.2, 1.35], 40)                                          # S126 the old card, my loops
S("L58.1", [1.7, -0.9, 1.4], [2.65, -0.25, 1.3], 54)                                         # S127 in MY handwriting
S("L59", [1.6, -0.6, 1.3], [2.65, -0.25, 1.25], 66)                                          # S128 the stain, dry again
S("L59.2", [1.8, -0.7, 1.3], [2.65, -0.25, 1.25], 56)                                        # S129 over the last line
obj("card_old", "L60", hide=True)
hold("nell", "L60", arms=[0, 95], expr="smirk")
hold_obj("lemon_hand", "L60", "nell", arm=1, off=(0.0, -0.1, 0.12))
S("L60", [1.4, -1.4, 1.5], [2.95, -0.1, 1.4], 34)                                            # S130 Grandma smirks, a lemon up
S("L60.2", [1.8, -1.5, 1.45], [2.95, -0.1, 1.4], 40)                                         # S131 find the last step herself
put("me", "L61", [2.0, -1.6], 40, expr="laugh", arms=[0, 0])
obj("lemon_hand", "L61", hide=True)
S("L61", [3.0, -2.4, 1.5], [2.0, -1.6, 1.4], 34)                                             # S132 me, a soft laugh
# L62 the reveal picture: Grandma, the card, the photo, one frame
hide("me", at="L62")
hold("nell", "L62", arms=[0, 98], expr="soft")
obj("lemon_hand", "L62", hide=True)
obj("card_old", "L62", [2.51, -0.18, 1.25], (0, 0, -80))
S("L62", [0.7, -1.6, 1.5], [3.2, -0.6, 1.5], 30, [0.9, -1.55, 1.5], [3.2, -0.6, 1.5])      # S133 the same card, sixty years apart
S("L63", [2.4, -1.0, 1.6], [3.43, -0.944, 1.512], 70)                                        # S134 the card in the photo
S("L64", [1.9, -0.7, 1.45], [2.65, -0.25, 1.3], 70)                                          # S135 the card in her hand
S("L65", [1.6, -1.2, 1.5], [3.0, -0.5, 1.45], 44, [1.9, -1.0, 1.5], [3.0, -0.5, 1.45])     # S136 both boot stains
S("L65.1", [1.9, -0.8, 1.5], [3.2, -0.6, 1.5], 50)                                           # S137 the same card
S("L66", [1.2, 0.2, 1.45], [2.7, -0.25, 1.3], 46, [1.6, -1.0, 1.45], [2.7, -0.25, 1.3])     # S138 circling the card
S("L66.1", [2.2, -1.4, 1.4], [2.7, -0.25, 1.3], 52, [3.1, -1.0, 1.4], [2.7, -0.25, 1.3])    # S139 around and around

# ================================================================================================ 08 the loop (L67 to L72)
obj("card_old", "L67", hide=True)
hide("nell", at="L67")
look("L69", "dusk", 1.5)
put("nell", "L67", [1.6, -0.9], -90, expr="soft", arms=[0, 70])
sit("nell", "L67")
put("dad", "L67", [-1.0, -0.9], 90, expr="smile", arms=[0, 0])
sit("dad", "L67")
put("mom", "L67", [0.3, -2.2], 180, expr="smile", arms=[0, 0])
sit("mom", "L67")
put("me", "L67", [0.3, 0.4], 0, expr="soft", arms=[0, 0])
sit("me", "L67")
hold_obj("spoon", "L67", "nell", arm=1, off=(0.0, -0.12, 0.0), rot=(-50, 0, 0))
S("L67", [-0.2, 1.4, 1.9], [0.7, -0.9, 0.95], 28)                                            # S140 Grandma tastes my soup
S("L68", [2.6, -2.2, 1.45], [1.6, -0.9, 1.2], 34)                                            # S141 Grandma, close, soft
hold("nell", "L68.2", expr="soft")
S("L68.3", [-0.1, -0.9, 1.7], [0.3, 0.4, 1.2], 34)                                           # S142 me, soft
obj("spoon", "L69", hide=True)
sit("me", "L69", False)
put("me", "L69", [-2.45, 0.4], -90, expr="soft", arms=[45, 55], head=[70, 0])
hold("nell", "L69", expr="laugh")
hold("mom", "L69", expr="laugh")
hold("dad", "L69", expr="laugh")
S("L69", [1.4, 0.8, 1.7], [-1.0, -0.4, 1.2], 26)                                             # S143 I make it every Sunday
cue("L69.2", "tin", open=0.0)
S("L69.2", [-2.0, -0.8, 1.8], [-3.3, -1.5, 1.65], 40)                                        # S144 the tin shut on the shelf
S("L69.3", [-1.4,-1.5,1.5], [-2.45, 0.4, 1.35], 34)                                       # S145 from memory
hide("me", "nell", "mom", "dad", at="L70")
sit("nell", "L70", False)
sit("mom", "L70", False)
sit("dad", "L70", False)
fly("fl0", "L70", [-1.5, 12.0, 3.4], [-4.0, 16.0, 4.6], 3.0, (0, 0, 0), (20, 10, 60), 10)
S("L70", [0.0, 1.2, 1.6], [0.0, 16.0, 4.5], 26)                                              # S146 one small card far off
S("L70.1", [0.8, 1.2, 1.7], [-3.0, 18.0, 6.5], 24)                                           # S147 the dusk sky
obj("fl0", "L71", hide=True)
S("L71", [2.5, -0.9, 1.6], [3.43, -0.9, 1.6], 34)                                            # S148 the framed photo
S("L71.2", [2.5, -0.9, 1.55], [3.43, -0.944, 1.512], 56)                                     # S149 a card just landed
# L72 loop: back to S001's framing, the card in Grandma's hand
put("nell", "L72", [0.3, 0.8], 0, expr="smile", arms=[0, 80])
obj("card_old", "L72", [0.5, 0.38, 1.25], (0, 0, 0), flutter=2)
obj("list", "L72", [0.0, 0.02, 0.795], (-90, 0, 8))
cue("L72", "tin", open=0.0)
S("L72", [0.4, -0.75, 1.5], [0.35, 0.3, 1.02], 44)                                             # S150 close on the card: loop
