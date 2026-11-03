"""ep93 "recipe card": Grandma Nell's butter-yellow kitchen, a pink-gold town at dusk, and four little booths for the
montage (Mr. Ito's island, the fire station table, a doorway full of boxes, a bare flat's sink).

Everything the story moves is a cue in story.json (see animate): "look" (the evening light and the window's sky,
always eased 0.35 s or more), "obj" (props and cards: position, rotation, glides, hide), "hold" (a prop riding a
character's hand), "tex" (a card's picture changes), "inset" (the rule marker in the corner), "tin" (the lid),
"sit", "flock" (cards over the roofs). The rule marker is a card plane parented to the camera, so it is in
every shot at the same place. Nothing has real lettering: the cards are drawn scribble loops and numerals.
"""
import math
import os
import sys
import tempfile
from pathlib import Path

import bpy
from mathutils import Vector

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import cards as C  # noqa: E402

D2R = math.pi / 180.0
W = {"objs": {}, "inited": False}


def ss(x):
    x = min(1.0, max(0.0, x))
    return x * x * (3 - 2 * x)


# ---------------------------------------------------------------------------------------------- looks
def _L(**kw):
    base = dict(sun=1.7, sun_col="#ffc878", el=14.0, sky="#ffd2a0", sky_str=0.9, win="#ffb96e", win_str=2.4,
                itn=1.0, cool=0.0, fill=1.0)
    base.update(kw)
    return base


LOOKS = {
    "gold": _L(),
    "blue": _L(sun=0.0, sky="#2a3c8c", sky_str=0.5, win="#2640a0", win_str=1.6, itn=0.85, cool=1.0, fill=0.9),
    "bright": _L(sun=3.8, sky="#ffe0b0", win="#ffc98a", itn=1.15),
    "dusk": _L(sun=3.0, sun_col="#ff9e78", el=10, sky="#ffb0a0", sky_str=0.9, win="#ff9a80"),
}


def _col(h):
    h = h.lstrip("#")
    f = lambda c: (c / 12.92) if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
    return tuple(f(int(h[i:i + 2], 16) / 255) for i in (0, 2, 4))


def look_at(tl, t):
    cues = [c for c in tl["cues"] if c["name"] == "look"]
    cur = LOOKS[cues[0]["id"]] if cues else LOOKS["gold"]
    prev = cur
    for c in cues:
        if c["t"] > t:
            break
        prev, cur = cur, LOOKS[c["id"]]
        dur = max(0.35, c.get("dur", 0.5))
        if t < c["t"] + dur:
            u = ss((t - c["t"]) / dur)
            return {k: (_mix(prev[k], cur[k], u)) for k in cur}
    return dict(cur)


def _mix(a, b, u):
    if isinstance(a, str):
        ca, cb = _col(a), _col(b)
        return "#" + "".join("%02x" % int(round(255 * (min(1, max(0, (x + (y - x) * u))) ** (1 / 2.2)))) for x, y in zip(ca, cb))
    return a + (b - a) * u


# ---------------------------------------------------------------------------------------------- materials
def img_mat(kit, name, path, emit=0.0, rough=0.85, alpha=False, fog=True):
    """A picture on a plane. emit > 0 glows (the inset marker, so it reads in any light)."""
    m = kit._new(name)
    nt = m.node_tree
    b = nt.nodes["Principled BSDF"]
    tx = nt.nodes.new("ShaderNodeTexImage")
    tx.image = bpy.data.images.load(str(path), check_existing=True)
    tx.image.colorspace_settings.name = "sRGB"
    tx.interpolation = "Linear"
    tc = nt.nodes.new("ShaderNodeTexCoord")           # our planes have no UVs: use the generated 0..1 box coordinates
    nt.links.new(tc.outputs["Generated"], tx.inputs["Vector"])
    if alpha:
        nt.nodes.remove(b)
        em = nt.nodes.new("ShaderNodeEmission")
        em.inputs["Strength"].default_value = emit
        nt.links.new(tx.outputs["Color"], em.inputs["Color"])
        tr = nt.nodes.new("ShaderNodeBsdfTransparent")
        mx = nt.nodes.new("ShaderNodeMixShader")
        nt.links.new(tx.outputs["Alpha"], mx.inputs[0])
        nt.links.new(tr.outputs[0], mx.inputs[1])
        nt.links.new(em.outputs[0], mx.inputs[2])
        out = next(n for n in nt.nodes if n.type == "OUTPUT_MATERIAL")
        nt.links.new(mx.outputs[0], out.inputs["Surface"])
        try:
            m.emission_sampling = "NONE"
        except Exception:
            pass
        return m, tx
    nt.links.new(tx.outputs["Color"], b.inputs["Base Color"])
    b.inputs["Roughness"].default_value = rough
    if emit:
        nt.links.new(tx.outputs["Color"], b.inputs["Emission Color"])
        b.inputs["Emission Strength"].default_value = emit
    if fog:
        kit._fogged(m, b.outputs[0])
    return m, tx


def P(kit, hexc, rough=0.5):
    return kit.plastic(hexc, rough)


# ---------------------------------------------------------------------------------------------- small builders
def reg(oid, ob, hidden=False):
    W["objs"][oid] = {"ob": ob, "home": (tuple(ob.location), tuple(ob.rotation_euler)), "hidden": hidden}
    if hidden:
        ob.location = (0, 0, -50)
    return ob


def noshadow(ob):
    ob.visible_shadow = False
    for c in ob.children_recursive:
        c.visible_shadow = False


def make_card(kit, oid, tex, size=(0.42, 0.25), hidden=False):
    """A recipe card: a holder empty with a picture plane (normal -y, upright) and a cream back."""
    h = kit.empty(f"card.{oid}", (0, 0, 0))
    m, tx = img_mat(kit, f"cardmat.{oid}", W["tex"][tex], emit=0.35)
    pl = kit.plane(f"card.{oid}.face", size, (0, -0.002, 0), m, h, rot=(math.pi / 2, 0, 0))
    bk = kit.plane(f"card.{oid}.back", size, (0, 0.002, 0), kit.plastic("#f3e9cc", 0.8), h, rot=(-math.pi / 2, 0, 0))
    W.setdefault("cardtex", {})[oid] = tx
    reg(oid, h, hidden)
    return h


def gable(kit, name, w, d, h, rh, mat, roof_mat, loc):
    """A house: a box with a gable roof (ridge along x)."""
    kit.box(name + ".body", (w, d, h), (loc[0], loc[1], loc[2] + h / 2), mat, bevel=0.05)
    v = [(-w / 2 - 0.25, -d / 2 - 0.25, 0), (w / 2 + 0.25, -d / 2 - 0.25, 0), (w / 2 + 0.25, d / 2 + 0.25, 0),
         (-w / 2 - 0.25, d / 2 + 0.25, 0), (-w / 2 - 0.25, 0, rh), (w / 2 + 0.25, 0, rh)]
    f = [(0, 1, 5, 4), (2, 3, 4, 5), (0, 4, 3), (1, 2, 5), (3, 2, 1, 0)]
    kit.mesh_obj(name + ".roof", v, f, roof_mat, None, (loc[0], loc[1], loc[2] + h))


def booth(kit, name, ox, wall, floor, w=6.4, d=5.0, light=230.0):
    kit.box(name + ".floor", (w, d, 0.1), (ox, 0, -0.05), P(kit, floor, 0.6))
    kit.box(name + ".back", (w, 0.2, 2.8), (ox, -d / 2, 1.4), P(kit, wall, 0.7))
    kit.box(name + ".front", (w, 0.2, 2.8), (ox, d / 2, 1.4), P(kit, wall, 0.7))
    for sx in (-1, 1):
        kit.box(f"{name}.side{sx}", (0.2, d, 2.8), (ox + sx * w / 2, 0, 1.4), P(kit, wall, 0.7))
    kit.box(name + ".ceil", (w, d, 0.1), (ox, 0, 2.85), kit.emit("#ffeccb", 0.9, name="ceil"))
    kit.light(name + "_light", "AREA", (ox, 0.3, 2.7), 1.0, "#fff0d4", rot=(0, 0, 0), size=3.2)
    W.setdefault("booth_lights", {})[name + "_light"] = light


# ---------------------------------------------------------------------------------------------- the build
def build(kit, story, tl):
    from blocky import polish

    cdir = Path(tempfile.gettempdir()) / f"ep93cards-{os.getpid()}"
    W["tex"] = C.build_all(cdir)
    W["shots"] = polish.cam_specs(story, tl, polish.spec(story))
    P_ = lambda h, r=0.5: kit.plastic(h, r)

    # ===== the kitchen (origin): x -3.5..3.5, y -3..3, window on the north wall
    wall = kit.plastic("#ffe08a", 0.8)
    blue = kit.plastic("#8fd8e8", 0.45)
    cream = kit.plastic("#f7f3ea", 0.4)
    kit.box("k.floor", (7.2, 6.2, 0.1), (0, 0, -0.05), kit.checker("#fff0c8", "#ffd98a", 0.9, rough=0.5))
    kit.box("k.ceil", (7.2, 6.2, 0.1), (0, 0, 2.85), kit.emit("#ffeccb", 0.9, name="ceil"))
    kit.box("k.south", (7.2, 0.2, 2.8), (0, -3.1, 1.4), wall)
    kit.box("k.west", (0.2, 6.2, 2.8), (-3.6, 0, 1.4), wall)
    kit.box("k.east", (0.2, 6.2, 2.8), (3.6, 0, 1.4), wall)
    # north wall with the window hole x -1.0..1.0, z 1.1..2.2
    kit.box("k.n_l", (2.6, 0.2, 2.8), (-2.3, 3.1, 1.4), wall)
    kit.box("k.n_r", (2.6, 0.2, 2.8), (2.3, 3.1, 1.4), wall)
    kit.box("k.n_lo", (2.0, 0.2, 1.1), (0, 3.1, 0.55), wall)
    kit.box("k.n_hi", (2.0, 0.2, 0.6), (0, 3.1, 2.5), wall)
    for nm, sz, lc in (("t", (2.2, 0.12, 0.08), (0, 3.04, 2.2)), ("b", (2.2, 0.3, 0.08), (0, 3.0, 1.1)),
                       ("l", (0.08, 0.12, 1.1), (-1.0, 3.04, 1.65)), ("r", (0.08, 0.12, 1.1), (1.0, 3.04, 1.65)),
                       ("m", (0.06, 0.1, 1.1), (0, 3.04, 1.65))):
        kit.box("k.wf" + nm, sz, lc, cream, bevel=0.02)
    # outside: sky, garden, rooftops
    W["winmat"] = kit.emit("#ffb96e", 2.4, name="winsky")
    kit.plane("k.sky", (60, 30), (0, 26, 8), W["winmat"], rot=(math.pi / 2, 0, 0))
    kit.box("k.garden", (40, 24, 0.1), (0, 14, -0.45), P_("#8ed06a", 0.9))
    for i, (x, y, w, h, c) in enumerate([(-7, 11, 3.0, 2.6, "#c9728a"), (-2, 14, 3.4, 3.4, "#7a9ad0"), (4, 12, 3.0, 2.2, "#e8a05a"),
                                         (9, 15, 3.4, 3.0, "#a77ad0"), (-12, 14, 3.2, 3.0, "#d0a070")]):
        gable(kit, f"k.house{i}", w, 2.6, h, 1.3, P_(c, 0.7), P_("#7a3a3a", 0.7), (x, y, -0.4))
    for i, (x, y) in enumerate([(-3.5, 5.5), (3.5, 6.5), (0.5, 8.5)]):
        kit.cyl(f"k.trunk{i}", 0.16, 1.4, (x, y, 0.3), P_("#8a5a32"))
        kit.sphere(f"k.crown{i}", 1.0, (x, y, 1.6), P_("#4fb060", 0.8))
    # counters along the north wall, sink under the window
    kit.box("k.ctr_n", (7.0, 0.7, 0.88), (0, 2.65, 0.44), blue, bevel=0.03)
    kit.box("k.top_n", (7.0, 0.76, 0.06), (0, 2.65, 0.91), cream, bevel=0.02)
    kit.box("k.sink", (0.95, 0.5, 0.05), (0, 2.68, 0.955), kit.metal("#c8d0d6"), bevel=0.02)
    kit.cyl("k.tap_p", 0.03, 0.34, (0, 2.9, 1.1), kit.metal("#c8d0d6"))
    kit.box("k.tap_h", (0.05, 0.28, 0.05), (0, 2.78, 1.27), kit.metal("#c8d0d6"))
    for i in range(3):
        kit.box(f"k.up{i}", (1.1, 0.4, 0.7), (-2.7 + 0.0 + i * 0.0, 2.8, 2.15), blue, bevel=0.03) if False else None
    # west wall: the stove between two cabinets, the shelf with the tin
    kit.box("k.ctr_w1", (0.7, 1.7, 0.88), (-3.2, -1.2, 0.44), blue, bevel=0.03)
    kit.box("k.top_w1", (0.76, 1.7, 0.06), (-3.18, -1.2, 0.91), cream, bevel=0.02)
    kit.box("k.stove", (0.8, 0.95, 0.9), (-3.15, 0.4, 0.45), cream, bevel=0.04)
    kit.box("k.stovetop", (0.84, 0.99, 0.04), (-3.15, 0.4, 0.92), P_("#3a3a40", 0.4), bevel=0.01)
    for i, (dx, dy) in enumerate([(-0.18, -0.22), (0.18, -0.22), (-0.18, 0.22), (0.18, 0.22)]):
        kit.cyl(f"k.ring{i}", 0.13, 0.02, (-3.15 + dx, 0.4 + dy, 0.945), P_("#222228", 0.3))
    for i in range(3):
        kit.cyl(f"k.knob{i}", 0.035, 0.05, (-2.74, 0.12 + i * 0.28, 0.7), P_("#d8334a"), rot=(0, math.pi / 2, 0))
    kit.box("k.ctr_w2", (0.7, 1.5, 0.88), (-3.2, 1.85, 0.44), blue, bevel=0.03)
    kit.box("k.top_w2", (0.76, 1.5, 0.06), (-3.18, 1.85, 0.91), cream, bevel=0.02)
    # the pot, copper, with handles
    pot = kit.empty("pot", (-3.12, 0.4, 0.94))
    cop = kit.plastic("#c8743a", 0.3, spec=0.7)
    kit.cyl("pot.body", 0.25, 0.3, (0, 0, 0.15), cop, pot, n=28)
    kit.cyl("pot.soup", 0.23, 0.02, (0, 0, 0.29), P_("#f0b040", 0.35), pot, n=28)
    for sy in (-1, 1):
        kit.box(f"pot.h{sy}", (0.1, 0.07, 0.04), (0, sy * 0.3, 0.24), cop, pot, bevel=0.015)
    W["pot"] = pot
    # steam: a few soft white puffs rising
    steam_m = kit.emit("#ffffff", 0.9, name="steam")
    W["steam"] = []
    for i in range(6):
        s = kit.sphere(f"steam{i}", 0.07, (-3.12, 0.4, 1.3), steam_m, seg=8)
        noshadow(s)
        s.visible_diffuse = s.visible_glossy = False
        W["steam"].append(s)
    # shelf and tin (dented robin's-egg blue)
    kit.box("k.shelf", (0.34, 1.5, 0.05), (-3.42, -1.5, 1.55), P_("#b98a4e", 0.6), bevel=0.01)
    for sy in (-1, 1):
        kit.box(f"k.shelfb{sy}", (0.05, 0.05, 0.2), (-3.45, -1.5 + sy * 0.6, 1.45), P_("#b98a4e", 0.6))
    tin = kit.empty("tin", (-3.3, -1.5, 1.575))
    kit.box("tin.body", (0.34, 0.42, 0.24), (0, 0, 0.12), blue, tin, bevel=0.03)
    kit.box("tin.dent", (0.04, 0.12, 0.1), (0.17, 0.08, 0.12), P_("#6fb8cc", 0.5), tin, rot=(0.2, 0, 0.3))
    hinge = kit.empty("tin.hinge", (-0.17, 0, 0.24), tin)
    kit.box("tin.lid", (0.36, 0.44, 0.04), (0.18, 0, 0.02), blue, hinge, bevel=0.015)
    cop2 = kit.plastic("#d8843a", 0.3, spec=0.7)
    for sy in (-0.07, 0.07):          # the lore plant: two copper tally strokes inside the lid
        kit.box(f"tin.tally{int(sy * 100)}", (0.025, 0.012, 0.18), (0.18, sy, -0.008), cop2, hinge, rot=(0, 0, 0.06))
    W["tin_hinge"] = hinge
    # east wall: the fridge with magnets, the framed photo
    kit.box("k.fridge", (0.8, 0.9, 1.9), (3.1, 1.7, 0.95), cream, bevel=0.05)
    kit.box("k.fridge_line", (0.02, 0.88, 0.03), (2.69, 1.7, 1.3), P_("#cfc8b8"), bevel=0.0)
    kit.box("k.fridge_h", (0.05, 0.05, 0.5), (2.66, 1.4, 1.05), kit.metal("#b8c0c6"), bevel=0.01)
    for i, (hc, yy, zz) in enumerate([("#e8506a", 2.0, 1.55), ("#4a90e0", 1.45, 1.6), ("#f0c030", 1.95, 1.0), ("#5ac078", 1.5, 0.9)]):
        kit.cyl(f"k.mag{i}", 0.05, 0.03, (2.672, yy, zz), P_(hc, 0.4), rot=(0, math.pi / 2, 0))
    frame = kit.box("k.frame", (0.06, 0.62, 0.78), (3.47, -0.9, 1.55), P_("#a0703a", 0.5), bevel=0.02)
    pm, _ = img_mat(kit, "photo", W["tex"]["photo"], emit=0.3)
    kit.plane("k.photo", (0.5, 0.64), (3.43, -0.9, 1.55), pm, rot=(math.pi / 2, 0, -math.pi / 2))
    # table, chairs, bowls
    tm = P_("#c8905a", 0.5)
    kit.cyl("k.table", 0.95, 0.06, (0.3, -0.9, 0.75), tm, n=36)
    kit.cyl("k.tleg", 0.12, 0.72, (0.3, -0.9, 0.36), tm)
    kit.cyl("k.tbase", 0.38, 0.04, (0.3, -0.9, 0.02), tm)
    kit.cyl("k.cloth", 0.97, 0.01, (0.3, -0.9, 0.785), P_("#d8334a", 0.8), n=36) if False else None
    for i, (cx, cy, yaw) in enumerate([(1.6, -0.9, -90), (-1.0, -0.9, 90), (0.3, -2.2, 180), (0.3, 0.4, 0)]):
        ch = kit.empty(f"k.chair{i}", (cx, cy, 0), rot=(0, 0, yaw * D2R))
        kit.box(f"k.chs{i}", (0.5, 0.5, 0.06), (0, 0, 0.42), P_("#e8a050", 0.5), ch, bevel=0.02)
        for sx in (-1, 1):
            for sy in (-1, 1):
                kit.box(f"k.chl{i}{sx}{sy}", (0.05, 0.05, 0.4), (sx * 0.21, sy * 0.21, 0.2), P_("#c8905a"), ch)
        kit.box(f"k.chb{i}", (0.5, 0.05, 0.5), (0, 0.23, 0.72), P_("#e8a050", 0.5), ch, bevel=0.02)
    bowl_m, soup_m = kit.plastic("#fbfaf4", 0.3), P_("#f2a840", 0.35)

    def bowl(oid, loc, hidden=False):
        b = kit.empty("bowl." + oid, loc)
        kit.cyl("bowl." + oid + ".b", 0.13, 0.08, (0, 0, 0.04), bowl_m, b, r2=0.16)
        kit.cyl("bowl." + oid + ".s", 0.14, 0.01, (0, 0, 0.075), soup_m, b)
        reg(oid, b, hidden)
        return b

    for i, (bx, by) in enumerate([(1.1, -0.9), (-0.5, -0.9), (0.3, -1.55), (0.3, -0.25)]):
        bowl(f"tbowl{i}", (bx, by, 0.78))
    # a counter crowded with bowls (L29), hidden until then
    for i in range(10):
        bowl(f"cbowl{i}", (-1.6 + (i % 5) * 0.34, 2.5 - (i // 5) * 0.3, 0.94), hidden=True)
    # the bowl of lemons
    kit.cyl("k.lbowl", 0.26, 0.14, (2.2, 2.6, 1.0), P_("#fbfaf4", 0.3), r2=0.3)
    lm = P_("#ffe14d", 0.35)
    for i in range(9):
        a = i * 2.4
        r = 0.1 if i < 6 else 0.0
        s = kit.sphere(f"lemon{i}", 0.09, (2.2 + r * math.cos(a), 2.6 + r * math.sin(a), 1.12 + (i // 6) * 0.1), lm, seg=12)
        s.scale = (1.0, 1.0, 0.8)
    # props that move: a lemon in hand, a lemon wedge, a drop, a spoon, a pen, the lists
    lemon = kit.sphere("lemon_hand", 0.09, (0, 0, -50), lm, seg=12)
    lemon.scale = (1.0, 1.0, 0.82)
    reg("lemon_hand", lemon, True)
    wedge = kit.sphere("wedge", 0.06, (0, 0, -50), lm, seg=8)
    wedge.scale = (1.0, 0.7, 0.5)
    reg("wedge", wedge, True)
    drop = kit.sphere("drop", 0.04, (0, 0, -50), P_("#d8a030", 0.2), seg=10)
    reg("drop", drop, True)
    drop2 = kit.sphere("drop2", 0.035, (0, 0, -50), P_("#fff04a", 0.2), seg=10)
    reg("drop2", drop2, True)
    spoon = kit.empty("spoon", (0, 0, -50))
    kit.cyl("spoon.h", 0.018, 0.5, (0, 0, 0.0), kit.metal("#d8dadc"), spoon, rot=(0, 0, 0))
    sb = kit.sphere("spoon.b", 0.06, (0, 0, -0.27), kit.metal("#d8dadc"), spoon, seg=10)
    sb.scale = (1.0, 0.8, 0.5)
    reg("spoon", spoon, True)
    pen = kit.empty("pen", (0, 0, -50))
    kit.cyl("pen.b", 0.014, 0.22, (0, 0, 0), P_("#2a3a6a"), pen)
    reg("pen", pen, True)
    make_card(kit, "list", "list", size=(0.3, 0.18), hidden=True)
    make_card(kit, "card_old", "card_old", hidden=True)       # Grandma's card, in her hand
    make_card(kit, "card_new", "card_new", hidden=True)       # my card
    make_card(kit, "card_old2", "card_old", hidden=True)      # a second old card (the match cut / the photo close)
    for i in range(8):
        make_card(kit, f"fl{i}", "card_old" if i % 2 else "card_new", size=(1.5, 0.9), hidden=True)
    make_card(kit, "card_m1", "card_old", size=(1.6, 0.96), hidden=True)    # montage cards: big, for the street shots
    make_card(kit, "card_m6", "card_old", size=(0.34, 0.2), hidden=True)
    make_card(kit, "card_m2", "card_old", size=(0.34, 0.2), hidden=True)
    make_card(kit, "card_m3", "card_new", size=(0.34, 0.2), hidden=True)
    make_card(kit, "card_m4", "card_old", size=(0.34, 0.2), hidden=True)
    make_card(kit, "card_m5", "card_new", size=(1.5, 0.9), hidden=True)
    make_card(kit, "card_i1", "card_old", size=(0.34, 0.2), hidden=True)    # inserts
    make_card(kit, "card_i2", "card_new", size=(0.34, 0.2), hidden=True)
    make_card(kit, "card_i3", "card_old", size=(0.34, 0.2), hidden=True)

    # ===== the town at dusk (x = 60)
    ox = 60
    kit.box("t.ground", (120, 60, 0.1), (ox, 0, -0.05), P_("#9ad46a", 0.9))
    kit.box("t.road", (120, 5.0, 0.12), (ox, 4.5, -0.04), P_("#8a8c9c", 0.8))
    kit.box("t.kerb", (120, 0.3, 0.2), (ox, 2.0, 0.0), P_("#e8e0d0"))
    for i, (x, c, h) in enumerate([(-15, "#ef8fa0", 3.0), (-9, "#8fc8f0", 3.6), (-3, "#ffd070", 3.0), (3, "#a0e0a0", 3.8),
                                    (9, "#c8a0f0", 3.2), (15, "#ffb080", 3.6)]):
        gable(kit, f"t.h{i}", 5.0, 4.0, h, 1.6, P_(c, 0.6), P_("#b04a50", 0.7), (ox + x, -4.0, 0.0))
        kit.box(f"t.door{i}", (0.9, 0.08, 1.8), (ox + x + 1.2, -1.95, 0.9), P_("#d8334a", 0.5))
        for wx in (-1.3, 0.1):
            kit.box(f"t.win{i}{wx}", (0.9, 0.06, 0.9), (ox + x + wx, -1.97, 1.9), kit.emit("#ffd070", 2.2, name="twin"))
        kit.box(f"t.fence{i}", (5.0, 0.06, 0.5), (ox + x, 0.4, 0.25), P_("#fbfaf4", 0.5))
    for i, x in enumerate([-12, -6, 0, 6, 12, 18]):
        kit.cyl(f"t.trunk{i}", 0.2, 1.8, (ox + x, 1.2, 0.9), P_("#8a5a32"))
        kit.sphere(f"t.crown{i}", 1.2, (ox + x, 1.2, 2.4), P_("#58b868", 0.8))
    kit.box("t.hill", (120, 4, 8), (ox, -26, 3.0), P_("#8ac0a0", 0.9))

    # ===== the booths
    booth(kit, "b1", 100, "#ffb8a0", "#ffe8b0")          # Mr. Ito's island + the inserts
    kit.box("b1.island", (3.0, 0.9, 0.9), (100, -0.7, 0.45), P_("#8fd8e8", 0.45), bevel=0.03)
    kit.box("b1.itop", (3.1, 1.0, 0.06), (100, -0.7, 0.93), P_("#f7f3ea", 0.4), bevel=0.02)
    cop = kit.plastic("#c8743a", 0.3, spec=0.7)
    kit.cyl("b1.pot", 0.28, 0.32, (99.4, -0.7, 1.12), cop, n=28)
    kit.cyl("b1.soup", 0.26, 0.02, (99.4, -0.7, 1.27), P_("#d84a30", 0.35), n=28)
    kit.box("b1.back_ctr", (5.0, 0.7, 0.9), (100, -2.0, 0.45), P_("#8fd8e8", 0.45), bevel=0.03)
    kit.box("b1.back_top", (5.0, 0.76, 0.06), (100, -2.0, 0.93), P_("#f7f3ea", 0.4))
    # inserts (S08): a card under a jar, one under a fridge magnet, one shut in a tin
    jar = kit.cyl("b1.jar", 0.17, 0.3, (99.0, -2.0, 1.11), kit.glass("#e8f4f8"), n=24)
    kit.box("b1.slab", (0.1, 0.9, 1.5), (101.8, -2.0, 1.2), P_("#f7f3ea", 0.4), bevel=0.03)
    kit.cyl("b1.mag", 0.06, 0.04, (101.72, -2.0, 1.3), P_("#e8506a", 0.4), rot=(0, math.pi / 2, 0))
    kit.box("b1.tin", (0.36, 0.3, 0.24), (100.6, -2.0, 1.05), P_("#e8b0d0", 0.4), bevel=0.03)
    kit.box("b1.tinlid", (0.4, 0.34, 0.05), (100.6, -2.0, 1.2), P_("#e8b0d0", 0.4), bevel=0.02)
    booth(kit, "b2", 120, "#ff9a8a", "#d8c8a8")          # the fire station table
    kit.box("b2.table", (4.6, 1.1, 0.08), (120, -0.4, 0.78), P_("#c8905a", 0.5), bevel=0.02)
    for sx in (-1.9, 1.9):
        kit.box(f"b2.tl{sx}", (0.12, 0.9, 0.76), (120 + sx, -0.4, 0.38), P_("#a0703a"))
    kit.box("b2.stove", (1.6, 0.8, 0.9), (121.2, -2.0, 0.45), P_("#f7f3ea", 0.4), bevel=0.03)
    kit.cyl("b2.pot", 0.32, 0.4, (121.2, -2.0, 1.1), cop, n=28)
    kit.box("b2.rack", (2.0, 0.3, 1.2), (118.2, -2.3, 1.2), P_("#d8334a", 0.5), bevel=0.04)
    kit.box("b2.bench", (4.4, 0.4, 0.45), (120, 0.6, 0.25), P_("#e8a050", 0.5))
    booth(kit, "b3", 140, "#a8d8f0", "#e0d0b0")          # a doorway full of moving boxes
    for sx, wd in ((-1, 1.1), (1, 1.1)):
        kit.box(f"b3.jamb{sx}", (0.15, 0.3, 2.2), (140 + sx * 0.85, -2.35, 1.1), P_("#fbfaf4", 0.5))
    kit.box("b3.lintel", (1.9, 0.3, 0.15), (140, -2.35, 2.25), P_("#fbfaf4", 0.5))
    kit.box("b3.dark", (1.6, 0.1, 2.2), (140, -2.55, 1.1), kit.emit("#ffe8b8", 1.2, name="b3out"))
    kit.box("b3.mat", (1.1, 0.7, 0.04), (140, -1.8, 0.02), P_("#d8334a", 0.8), bevel=0.01)
    for i, (bx, by, bz, bs) in enumerate([(138.4, -1.9, 0.0, 0.8), (137.5, -2.0, 0.0, 0.7), (138.1, -1.9, 0.8, 0.6),
                                           (142.0, -1.8, 0.0, 0.8), (142.9, -1.6, 0.0, 0.7), (142.4, -1.7, 0.8, 0.7)]):
        kit.box(f"b3.box{i}", (bs, bs, bs * 0.9), (bx, by, bz + bs * 0.45), P_("#d8a870", 0.8), bevel=0.02)
    booth(kit, "b4", 160, "#ffe8a0", "#e8e0d0")          # a bare flat's sink
    kit.box("b4.ctr", (2.6, 0.7, 0.9), (160, -2.05, 0.45), P_("#f7f3ea", 0.5), bevel=0.03)
    kit.box("b4.sink", (0.8, 0.5, 0.05), (160, -2.05, 0.93), kit.metal("#c8d0d6"))
    kit.box("b4.winf", (1.5, 0.08, 1.2), (160, -2.46, 1.7), P_("#fbfaf4", 0.5))
    kit.box("b4.sky", (1.3, 0.05, 1.0), (160, -2.4, 1.7), kit.emit("#ff9e78", 2.0, name="b4sky"))
    bowl("cereal", (159.4, -2.05, 0.96), True)
    # ---- the montage guests' cards stay hidden until a cue places them

    # ===== lights
    kit.light("sun", "SUN", (0, 60, 14), 1.0, "#ffc878", size=0.06)
    kit.aim(kit.LIGHTS["sun"]["obj"], (0, 0, 0))
    kit.light("kint", "AREA", (0.0, 0.0, 2.7), 1.0, "#fff0d0", size=4.0)
    kit.light("kint2", "AREA", (-1.8, 0.3, 2.6), 1.0, "#ffe8c0", size=2.0)
    kit.light("kcool", "AREA", (0.0, 5.0, 2.0), 1.0, "#6a8cff", rot=(math.pi / 2 + 0.2, 0, math.pi), size=3.0)
    kit.light("kfS", "AREA", (0.0, -2.9, 1.9), 1.0, "#fff2dc", rot=(math.pi / 2, 0, 0), size=5.0)
    kit.light("kfN", "AREA", (0.0, 2.5, 2.5), 1.0, "#fff2dc", rot=(-math.pi / 2, 0, 0), size=4.0)
    kit.light("kfE", "AREA", (3.2, 0.0, 2.3), 1.0, "#fff2dc", rot=(0, math.pi / 2, 0), size=4.0)
    kit.light("kfW", "AREA", (-3.2, -1.0, 2.3), 1.0, "#fff2dc", rot=(0, -math.pi / 2, 0), size=4.0)
    kit.light("tfill", "AREA", (60, 8, 8), 1.0, "#ffe0c8", rot=(0, 0, 0), size=14.0)
    W["inited"] = False
    ctx = {}
    # the rule marker, parented to the camera
    cam = kit.OBJ["cam"]
    W["inset"] = {}
    for k in ("old", "old0", "new0", "new1", "new9", "new20", "new39", "new40", "new41", "new41s"):
        m, _ = img_mat(kit, "inset." + k, W["tex"]["inset_" + k], emit=1.0, alpha=True)
        pl = kit.plane("inset." + k, (1.0, 1.0), (0, 0, -0.2), m, cam)
        pl.visible_shadow = pl.visible_diffuse = pl.visible_glossy = False
        W["inset"][k] = pl
    return ctx


# ---------------------------------------------------------------------------------------------- animate
def _hand(who, arm, off):
    from blocky import rig
    ch = rig.CHARS.get(who)
    if ch is None:
        return None
    a = ch.P[f"arm{arm}"]
    p = a.matrix_world @ Vector((0, -0.45, -1.55))
    root = ch.root
    o = root.matrix_world.to_3x3() @ Vector(off)
    # matrix_world includes the root's scale: normalise the offset to metres
    sc = root.matrix_world.to_scale()[1]
    return p + o / max(sc, 1e-6), root.rotation_euler.z


def _first(kit, story, tl):
    W["inited"] = True
    W["objs"]["__"] = None
    del W["objs"]["__"]


def animate(kit, story, tl, t, ctx):
    from blocky import bl_story

    look = look_at(tl, t)
    gains = {}
    so = kit.LIGHTS["sun"]["obj"]
    el = look["el"] * D2R
    so.location = Vector((0, math.cos(el), math.sin(el))) * 60
    kit.aim(so, (0, 0, 0))
    kit.LIGHTS["sun"]["light"].color = _col(look["sun_col"])
    gains["sun"] = look["sun"]
    gains["kint"] = look["itn"] * 190.0
    gains["kint2"] = look["itn"] * 100.0
    for nm in ("kfS", "kfN", "kfE", "kfW"):
        gains[nm] = look["itn"] * look["fill"] * 105.0
    gains["kcool"] = look["cool"] * 260.0
    gains["tfill"] = 650.0
    for nm, w in W["booth_lights"].items():
        gains[nm] = w
    bg = bpy.context.scene.world.node_tree.nodes["Background"]
    bg.inputs["Color"].default_value = (*_col(look["sky"]), 1.0)
    bg.inputs["Strength"].default_value = look["sky_str"]
    for n in W["winmat"].node_tree.nodes:
        if n.type == "EMISSION":
            n.inputs["Color"].default_value = (*_col(look["win"]), 1.0)
            n.inputs["Strength"].default_value = look["win_str"]
    # steam
    for i, s in enumerate(W["steam"]):
        u = (t * 0.28 + i / len(W["steam"])) % 1.0
        s.location = (-3.12 + 0.07 * math.sin(t * 1.3 + i * 2), 0.4 + 0.07 * math.cos(t * 1.1 + i), 1.25 + u * 0.8)
        k = 1.0 + u * 1.2
        s.scale = (k, k, k)
    # the tin lid
    tc = [c for c in tl["cues"] if c["name"] == "tin"]
    v, _ = _sample(tc, t, ["open"], {"open": 0.0})
    W["tin_hinge"].rotation_euler = (0, -v["open"] * 105 * D2R, 0)
    bpy.context.view_layer.update()
    # objects
    tracks = {}
    for c in tl["cues"]:
        if c["name"] in ("obj", "hold"):
            tracks.setdefault(c["id"], []).append(c)
    for oid, cs in tracks.items():
        ent = W["objs"].get(oid)
        if ent is None:
            continue
        ob = ent["ob"]
        cs = sorted(cs, key=lambda c: c["t"])
        last = None
        for c in cs:
            if c["t"] <= t:
                last = c
        if last is None:
            continue
        if last["name"] == "hold":
            hp = _hand(last["who"], last.get("arm", 1), last.get("off", [0, 0, 0]))
            if hp is not None:
                ob.location = hp[0]
                r = last.get("rot", [0, 0, 0])
                fl = last.get("flutter", 0.0)
                if fl:
                    r = [r[0] + fl * math.sin(t * 9.0), r[1] + fl * 0.6 * math.sin(t * 7.0 + 1), r[2] + fl * 0.5 * math.sin(t * 5.0)]
                ob.rotation_euler = (r[0] * D2R, r[1] * D2R, hp[1] + r[2] * D2R)
            continue
        if last.get("hide"):
            ob.location = (0, 0, -50)
            continue
        objs_ = [c for c in cs if c["name"] == "obj" and not c.get("hide")]
        v, c = _sample(objs_, t, ["pos", "rot", "scale"], {"pos": [0, 0, -50], "rot": [0, 0, 0], "scale": 1.0})
        ob.location = tuple(v["pos"])
        r = v["rot"]
        fl = last.get("flutter", 0.0)
        if fl:
            r = [r[0] + fl * math.sin(t * 9.0), r[1] + fl * 0.6 * math.sin(t * 7.0 + 1), r[2] + fl * 0.5 * math.sin(t * 5.0)]
        ob.rotation_euler = (r[0] * D2R, r[1] * D2R, r[2] * D2R)
        s = v["scale"]
        ob.scale = (s, s, s)
    if os.environ.get('EP93DBG') and t < 0.6:
        for k in ('card_old', 'list'):
            o = W['objs'][k]['ob']
            print('OBJ', k, tuple(o.location), tuple(o.rotation_euler), [tuple(c.matrix_world.translation) for c in o.children], flush=True)
        print('CAM', tuple(kit.OBJ['cam'].location), flush=True)
    bpy.context.view_layer.update()
    # card pictures
    imgs = {}
    for c in tl["cues"]:
        if c["name"] == "tex" and c["t"] <= t:
            imgs[c["id"]] = c["tex"]
    for oid, tx in W.get("cardtex", {}).items():
        key = imgs.get(oid)
        if key:
            tx.image = bpy.data.images.load(str(W["tex"][key]), check_existing=True)
    # who sits
    for who in {c["who"] for c in tl["cues"] if c["name"] == "sit"}:
        cs = [c for c in tl["cues"] if c["name"] == "sit" and c["who"] == who and c["t"] <= t]
        root = bpy.data.objects.get(who)
        if cs and cs[-1].get("on") and root is not None:
            root.location.z += cs[-1].get("z", 0.45) - 0.68
            for sx in (-1, 1):
                leg = bpy.data.objects.get(f"{who}.leg{sx}")
                if leg:
                    leg.rotation_euler = (-math.pi / 2 * 0.97, 0, 0)
    # the rule marker
    _inset(kit, tl, t, bl_story)
    return gains


def _sample(cues, t, fields, defaults):
    cur = dict(defaults)
    prev = dict(defaults)
    last = None
    for c in cues:
        if c["t"] > t:
            break
        prev = dict(cur)
        for f in fields:
            if f in c:
                cur[f] = c[f]
        last = c
        dur = c.get("dur", 0.0)
        if dur > 0 and t < c["t"] + dur:
            u = ss((t - c["t"]) / dur)
            res = {}
            for f in fields:
                a, b = prev[f], cur[f]
                if isinstance(a, (list, tuple)):
                    n = max(len(a), len(b))
                    a = list(a) + [0] * (n - len(a))
                    b = list(b) + [0] * (n - len(b))
                    res[f] = [a[i] + (b[i] - a[i]) * u for i in range(n)]
                else:
                    res[f] = a + (b - a) * u
            return res, c
    return cur, last


# the marker: NDC centre and size (fractions of the half frame), kept inside the safe 80% of the frame
INS_U, INS_V, INS_W = -0.46, 0.72, 0.70


def _inset(kit, tl, t, bl_story):
    shot = next((s for s in tl["shots"] if s["start"] <= t < s["end"]), tl["shots"][-1])
    spec = W["shots"][shot["id"]]
    _, _, lens, _ = bl_story.cam_at(spec, shot, t, None, tl)
    d = 0.2
    kx, ky = d * 6.75 / lens, d * 12.0 / lens             # metres per NDC unit at depth d (sensor 24 mm tall)
    state = "old"
    st_t = 0.0
    for c in tl["cues"]:
        if c["name"] == "inset" and c["t"] <= t:
            state, st_t = c["state"], c["t"]
    fly = next((c for c in tl["cues"] if c["name"] == "inset_fly"), None)
    wd = INS_W
    # plate height in NDC-y units: width in pixels is wd * 270, so height px = that * 420/640; NDC-y per px = 1/480
    ht = (wd * 270.0 * (420 / 640)) / 480.0
    for k, pl in W["inset"].items():
        pl.hide_render = True
    du = dv = 0.0
    sk = state
    rot = -5.0 * D2R
    show = [(state, 0.0, 0.0, 1.0)]
    if fly is not None and t >= fly["t"]:
        u = ss((t - fly["t"]) / 0.8)
        u2 = ss((t - fly["t"] - 0.45) / 0.7)
        show = []
        if u < 1.0:
            show.append((fly.get("from", "new41s"), 1.3 * u, 1.2 * u, 1.0))
        if u2 > 0:
            show.append(("old", -1.3 * (1 - u2), 0.0, 1.0))
        if t >= fly["t"] + 1.15:
            show = [("old", 0.0, 0.0, 1.0)]
    for key, ou, ov, _ in show:
        pl = W["inset"][key]
        pl.hide_render = False
        pl.parent = kit.OBJ["cam"]
        u_, v_ = INS_U + ou, INS_V + ov
        pl.location = (u_ * kx, v_ * ky, -d)
        pl.rotation_euler = (0, 0, rot)
        pl.scale = (wd * kx, ht * ky, 1.0)
        if os.environ.get('EP93DBG'):
            print('INSET', key, tuple(pl.location), tuple(pl.scale), lens, pl.parent.name if pl.parent else None, flush=True)
