"""Dawn Flight (ep31): a hot-air balloon basket at sunrise over a sea of mist, a launch field, a kitchen table and
the Loose One, a person in pieces. Built from kit.py's parts; nothing here is shared with another story's set.

Coordinates: the basket's floor centre is the origin, z up. The basket is 2.3 m inside, with four corner
compartments (me SW, Dad SE, Rosa NW, the empty fourth corner NE) around a middle with two gas tanks, low dividers
and a steel burner frame over the centre. The sun is in the east (+x). The landscape (field, hedges, barns, mist, hills)
hangs from the group `L`, which sinks by `alt` metres as we rise. The envelope hangs from the group `E`. The vessel
group `V` (basket, frame, tanks, flasks, bag, the people, the creature) is what leans.

THE LOOSE ONE (RULES: the creature): a person in pieces. R6 blocks, but each limb and the torso split into short
blocks and the head cut into four square slices, a hand's width (8.5 cm) of air between every piece. Nothing joins
them. Copper torso and arms, slate-blue legs and head slices, near-black faces across every gap, two small copper
eyes (with a white highlight each) on slice two, a flat black mouth on slice four. It is one model, built once
and posed per cue.

Cues read here (all optional):
- dawn {"v": 0..1, "dur"}: the light of the day, 0 plum pre-dawn, 0.35 pink, 1 full gold
- alt {"alt": m, "dur"}: how far the landscape has sunk; field {"f": 0|1}: launch field or landing field
- tilt {"deg", "dur"}: how far the basket leans toward the fourth corner
- roar {"peak", "up", "hold", "down"}: the burner flame, its glow on the envelope, the mist and the creature
- env {"up": 0..1, "dur"}: the envelope lying on the field to standing
- cre {"pose": "hidden|scatter|off|exact", "pos": [x, y, z], "yaw": deg, "s": scatter 0..1, "head": [4 yaws],
       "arms": [l, r] forward degrees, "alpha": "roar" | number, "key": watts}
- flasks {"state": "rim|corner|end"}; bag {"state": "none|tied|grass"}; cup {"on", "y", "dur"}; phone {"on"}
- field_bg, kitchen: shots in the kitchen are marked "room": "kitchen"
- the shot spec: "frame": "basket" (the camera rides the basket, so the world leans) or "world" (the basket leans),
  "key": watts of the soft key light riding the camera, "hold": nothing
"""

from __future__ import annotations

import math

import bpy
from mathutils import Matrix, Vector as V

from blocky import faces, rig

KS = rig.S
HX = 1.15              # the basket's inside half-width
WALL = 0.12
WALL_H = 1.05
RIM_H = 0.17
RIM_TOP = WALL_H + RIM_H            # 1.22
PIVOT = V((0, 0, 3.1))              # the envelope's mouth: the basket hangs from here
BURN_Z = 2.62
ENV_H = 13.0
ENV_R = 4.8
CRUISE = 18.0                       # metres the landscape sinks while we float
KITCHEN = V((0, 0, -300))
GROUND = -0.55                      # the field is this far below the basket's floor
LAND_SHIFT = V((260, 140, 0))
G = 0.085                           # the gap between the creature's pieces
LH = 0.2
TH = 0.15
SLICE = 0.14
ORANGE = "#ff9a3c"

# ------------------------------------------------------------------------------------------------ small helpers


def _ss(x):
    x = min(1.0, max(0.0, x))
    return x * x * (3 - 2 * x)


def _cues(tl, name):
    return [c for c in tl["cues"] if c["name"] == name]


def _switch(cs, attr, t, default):
    v = default
    for c in cs:
        if attr in c and c["t"] <= t + 1e-9:
            v = c[attr]
    return v


def _ease_value(cs, attr, t, default):
    """A value that eases from one cue's setting to the next over the newer cue's dur."""
    prev, out = default, default
    for c in cs:
        if attr not in c:
            continue
        if c["t"] > t:
            break
        d = c.get("dur", 0.0)
        u = 1.0 if d <= 0 else _ss((t - c["t"]) / d)
        out = prev + (c[attr] - prev) * u
        prev = c[attr] if u >= 1 else out
    return out


def _shot(tl, t):
    for s in tl["shots"]:
        if s["start"] <= t < s["end"]:
            return s
    return tl["shots"][-1]


def _lerp3(a, b, u):
    return tuple(a[i] + (b[i] - a[i]) * u for i in range(3))


def _hex(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))


def _mixhex(a, b, u):
    a, b = _hex(a), _hex(b)
    return tuple(a[i] + (b[i] - a[i]) * u for i in range(3))


def _lin(c):
    """sRGB triple 0..1 (or a hex string) to linear."""
    if isinstance(c, str):
        c = _hex(c)
    return tuple(c[i] / 12.92 if c[i] <= 0.04045 else ((c[i] + 0.055) / 1.055) ** 2.4 for i in range(3))


# the days: [d, horizon, zenith, fog, mist, sun colour, sun power, sun elevation (degrees), sky strength, mist glow]
DAYS = [
    (0.00, "#8a6a92", "#2c2f5c", "#9d92b4", "#b7bdd3", "#c8b0d8", 0.35, -6.0, 0.85, 0.34),
    (0.35, "#f0a0a8", "#4a4f8a", "#d9b2c4", "#e2c6d0", "#ffb8a8", 1.4, -3.0, 0.85, 0.62),
    (1.00, "#ffc46b", "#86a6d6", "#ffcf98", "#f0d5ac", "#ffd9a0", 3.0, 9.0, 1.0, 0.75),
]


def day(d):
    d = min(1.0, max(0.0, d))
    for a, b in zip(DAYS, DAYS[1:]):
        if d <= b[0]:
            u = (d - a[0]) / (b[0] - a[0])
            break
    out = [d]
    for i in range(1, 6):
        out.append(_mixhex(a[i], b[i], u))
    for i in range(6, 10):
        out.append(a[i] + (b[i] - a[i]) * u)
    return out


def stretch(ob, a, b):
    """A unit cylinder (height 1 along z) stretched between two points."""
    a, b = V(a), V(b)
    d = b - a
    ob.location = (a + b) / 2
    ob.scale = (1, 1, max(1e-4, d.length))
    ob.rotation_euler = d.to_track_quat("Z", "Y").to_euler()


def hide(ob, h):
    ob.hide_render = h
    for c in ob.children_recursive:
        c.hide_render = h


def hide_tree(ob, h):
    hide(ob, h)


def sock_color(sock, rgb):
    sock.default_value = (*_lin(rgb), 1.0)


# ------------------------------------------------------------------------------------------------ materials


def emissive_glow_mat(kit, ctx, name, base_hex, rough=0.7, zscale=9.0):
    """A fabric lit by the burner from inside: an orange emission that is strongest at the mouth and fades up the
    envelope, its strength a value the animation sets (the roar)."""
    if name in kit.MATS:
        return kit.MATS[name]
    m = kit._new(name)
    nt = m.node_tree
    b = nt.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = kit.col(base_hex)
    b.inputs["Roughness"].default_value = rough
    tc = nt.nodes.new("ShaderNodeTexCoord")
    sep = nt.nodes.new("ShaderNodeSeparateXYZ")
    nt.links.new(tc.outputs["Object"], sep.inputs[0])
    mr = nt.nodes.new("ShaderNodeMapRange")
    mr.inputs["From Min"].default_value = 0.0
    mr.inputs["From Max"].default_value = zscale
    mr.inputs["To Min"].default_value = 1.0
    mr.inputs["To Max"].default_value = 0.1
    nt.links.new(sep.outputs["Z"], mr.inputs["Value"])
    val = nt.nodes.new("ShaderNodeValue")
    val.outputs[0].default_value = 0.0
    mul = nt.nodes.new("ShaderNodeMath")
    mul.operation = "MULTIPLY"
    nt.links.new(val.outputs[0], mul.inputs[0])
    nt.links.new(mr.outputs["Result"], mul.inputs[1])
    mixc = nt.nodes.new("ShaderNodeMix")
    mixc.data_type = "RGBA"
    mixc.inputs["A"].default_value = kit.col(base_hex)
    mixc.inputs["B"].default_value = kit.col(ORANGE)
    cl = nt.nodes.new("ShaderNodeMath")
    cl.operation = "MULTIPLY"
    cl.use_clamp = True
    cl.inputs[1].default_value = 1.6
    nt.links.new(mul.outputs[0], cl.inputs[0])
    nt.links.new(cl.outputs[0], mixc.inputs["Factor"])
    nt.links.new(mixc.outputs["Result"], b.inputs["Emission Color"])
    add = nt.nodes.new("ShaderNodeMath")
    add.operation = "ADD"
    add.inputs[1].default_value = 0.22            # the cloth is a little lit from within: it never goes black
    nt.links.new(mul.outputs[0], add.inputs[0])
    nt.links.new(add.outputs[0], b.inputs["Emission Strength"])
    kit._fogged(m, b.outputs[0])
    ctx["env_glow"].append(val.outputs[0])
    return m


def mist_mat(kit, ctx):
    m = kit._new("mist")
    nt = m.node_tree
    b = nt.nodes["Principled BSDF"]
    b.inputs["Roughness"].default_value = 1.0
    tc = nt.nodes.new("ShaderNodeTexCoord")
    mp = nt.nodes.new("ShaderNodeMapping")
    mp.inputs["Scale"].default_value = (0.035, 0.035, 0.035)
    nt.links.new(tc.outputs["Object"], mp.inputs["Vector"])
    nz = nt.nodes.new("ShaderNodeTexNoise")
    nz.inputs["Scale"].default_value = 1.0
    nz.inputs["Detail"].default_value = 4.0
    nt.links.new(mp.outputs["Vector"], nz.inputs["Vector"])
    mr = nt.nodes.new("ShaderNodeMapRange")
    mr.inputs["To Min"].default_value = 0.86
    mr.inputs["To Max"].default_value = 1.06
    nt.links.new(nz.outputs["Fac"], mr.inputs["Value"])
    col = nt.nodes.new("ShaderNodeRGB")                 # the mist's colour (set by the day)
    sock_color(col.outputs[0], "#b7bdd3")
    mul = nt.nodes.new("ShaderNodeMix")
    mul.data_type = "RGBA"
    mul.blend_type = "MULTIPLY"
    mul.inputs["Factor"].default_value = 1.0
    nt.links.new(col.outputs[0], mul.inputs["A"])
    cc = nt.nodes.new("ShaderNodeCombineColor")
    for k in ("Red", "Green", "Blue"):
        nt.links.new(mr.outputs["Result"], cc.inputs[k])
    nt.links.new(cc.outputs["Color"], mul.inputs["B"])
    nt.links.new(mul.outputs["Result"], b.inputs["Base Color"])
    # the mist lights itself a little (it is a lit sea of water drops) and glows orange with the burner
    eco = nt.nodes.new("ShaderNodeRGB")
    sock_color(eco.outputs[0], "#b7bdd3")
    nt.links.new(eco.outputs[0], b.inputs["Emission Color"])
    ev = nt.nodes.new("ShaderNodeValue")
    ev.outputs[0].default_value = 0.3
    nt.links.new(ev.outputs[0], b.inputs["Emission Strength"])
    kit._fogged(m, b.outputs[0])
    ctx["mist_col"], ctx["mist_emit_col"], ctx["mist_emit"] = col.outputs[0], eco.outputs[0], ev.outputs[0]
    return m


def fadeable(ctx, m):
    """Route a material through a transparency mix whose factor the animation sets (the creature fading with the glow)."""
    nt = m.node_tree
    out = next(n for n in nt.nodes if n.type == "OUTPUT_MATERIAL")
    src = out.inputs["Surface"].links[0].from_socket
    tr = nt.nodes.new("ShaderNodeBsdfTransparent")
    mix = nt.nodes.new("ShaderNodeMixShader")
    val = nt.nodes.new("ShaderNodeValue")
    val.outputs[0].default_value = 0.0
    nt.links.new(val.outputs[0], mix.inputs[0])
    nt.links.new(src, mix.inputs[1])
    nt.links.new(tr.outputs[0], mix.inputs[2])
    nt.links.new(mix.outputs[0], out.inputs["Surface"])
    ctx["fade"].append(val.outputs[0])
    return m


def new_materials(kit, ctx):
    M = {}
    M["wicker"] = kit.bricks("#b48a55", "#9a7243", "#3f2f1a", scale=7.0, name="wicker", rough=0.9, row=0.25, width=0.5,
                             grime_amt=0.25)
    M["leather"] = kit.plastic("#4a2e1e", 0.5, name="leather rim", spec=0.35)
    M["floor"] = kit.planks("#a07a48", "#80602f", scale=3.5, axis="Y", name="basket floor")
    M["steel"] = kit.metal("#6c7075", 0.4, name="steel")
    M["steel_dark"] = kit.plastic("#2a2d31", 0.5, name="steel dark")
    M["tank"] = kit.metal("#8a8f94", 0.35, name="tank")
    M["rope"] = kit.plastic("#c2a878", 0.9, name="rope")
    M["canvas"] = kit.plastic("#a89a74", 0.95, name="canvas")
    M["flask"] = kit.plastic("#3a6b73", 0.4, name="flask")
    M["flask_cap"] = kit.plastic("#d8d4c8", 0.4, name="flask cap")
    M["cup"] = kit.plastic("#d8d2c4", 0.45, name="cup")
    M["bag"] = kit.plastic("#5a4a3a", 0.9, name="satchel")
    M["tally"] = kit.plastic("#46688a", 0.55, name="tally")
    M["flame"] = kit.emit(ORANGE, 7.0, name="flame")
    M["flame_core"] = kit.emit("#ffc070", 9.0, name="flame core")
    M["pilot"] = kit.emit("#ffa04c", 6.0, name="pilot")
    M["screen"] = kit.emit("#d8e4f0", 0.8, name="phone screen")
    M["phone"] = kit.plastic("#1c1d20", 0.4, name="phone")
    M["cream"] = emissive_glow_mat(kit, ctx, "env cream", "#efe4cc")
    M["green"] = emissive_glow_mat(kit, ctx, "env green", "#2f5a3c")
    M["ground"] = kit.grime("#7a7448", 0.62, 0.5, name="stubble", rough=0.95)
    M["ground2"] = kit.grime("#87804a", 0.7, 0.4, name="stubble 2", rough=0.95)
    M["hedge"] = kit.plastic("#2f4a2c", 0.95, name="hedge")
    M["trunk"] = kit.plastic("#4a3a2a", 0.95, name="trunk")
    M["leaf"] = kit.plastic("#33502e", 0.95, name="leaf")
    M["barn"] = kit.plastic("#6b4a3c", 0.95, name="barn wall")
    M["barn_roof"] = kit.plastic("#454c58", 0.8, name="barn roof")
    M["hill"] = kit.plastic("#3a3a5c", 1.0, name="hill")
    M["trailer"] = kit.plastic("#8a8f94", 0.6, name="trailer")
    M["tyre"] = kit.plastic("#1a1a1c", 0.9, name="tyre")
    M["lampglow"] = kit.emit("#ffd9a8", 6.0, name="lamp glow")
    M["sunmat"] = kit.emit("#fff0c0", 5.0, name="sun")
    # the kitchen
    M["k_floor"] = kit.planks("#8a6a45", "#6a4e30", scale=2.0, axis="X", name="kitchen floor")
    M["k_wall"] = kit.grime("#c9b894", 0.8, 2.0, name="kitchen wall")
    M["k_wood"] = kit.plastic("#7a5a38", 0.7, name="kitchen wood")
    M["k_window"] = kit.emit("#5a4a78", 0.9, name="kitchen window")
    M["k_lamp"] = kit.emit("#ffd9a0", 6.0, name="kitchen bulb")
    M["k_mug"] = kit.plastic("#e8dcc0", 0.5, name="mug")
    M["tea"] = kit.plastic("#6a3a18", 0.3, name="tea")
    return M


# ------------------------------------------------------------------------------------------------ the sky


def build_sky(kit, ctx):
    w = bpy.context.scene.world
    nt = w.node_tree
    for n in list(nt.nodes):
        if n.type != "OUTPUT_WORLD":
            nt.nodes.remove(n)
    out = next(n for n in nt.nodes if n.type == "OUTPUT_WORLD")
    tc = nt.nodes.new("ShaderNodeTexCoord")
    mp = nt.nodes.new("ShaderNodeMapping")
    mp.vector_type = "POINT"
    nt.links.new(tc.outputs["Generated"], mp.inputs["Vector"])
    sep = nt.nodes.new("ShaderNodeSeparateXYZ")
    nt.links.new(mp.outputs["Vector"], sep.inputs[0])
    nrm = nt.nodes.new("ShaderNodeVectorMath")
    nrm.operation = "NORMALIZE"
    nt.links.new(mp.outputs["Vector"], nrm.inputs[0])
    sep2 = nt.nodes.new("ShaderNodeSeparateXYZ")
    nt.links.new(nrm.outputs["Vector"], sep2.inputs[0])
    mr = nt.nodes.new("ShaderNodeMapRange")
    mr.inputs["From Min"].default_value = -0.05
    mr.inputs["From Max"].default_value = 0.75
    nt.links.new(sep2.outputs["Z"], mr.inputs["Value"])
    ramp = nt.nodes.new("ShaderNodeValToRGB")
    nt.links.new(mr.outputs["Result"], ramp.inputs["Fac"])
    bg = nt.nodes.new("ShaderNodeBackground")
    nt.links.new(ramp.outputs["Color"], bg.inputs["Color"])
    nt.links.new(bg.outputs[0], out.inputs["Surface"])
    ctx["sky_map"], ctx["sky_ramp"], ctx["sky_bg"] = mp, ramp, bg


# ------------------------------------------------------------------------------------------------ the basket


def wbox(kit, name, lo, hi, mat, parent=None, bevel=0.0):
    sx, sy, sz = hi[0] - lo[0], hi[1] - lo[1], hi[2] - lo[2]
    return kit.box(name, (sx, sy, sz), ((lo[0] + hi[0]) / 2, (lo[1] + hi[1]) / 2, (lo[2] + hi[2]) / 2), mat, parent,
                   bevel=bevel)


def build_basket(kit, ctx, M):
    Vg = ctx["V"]
    kit.box("floor", (2 * HX + 0.02, 2 * HX + 0.02, 0.08), (0, 0, -0.04), M["floor"], Vg)
    o = HX + WALL
    for sy in (-1, 1):
        kit.box(f"wallY{sy}", (2 * o, WALL, WALL_H - GROUND), (0, sy * (HX + WALL / 2), (WALL_H + GROUND) / 2), M["wicker"], Vg)
        kit.box(f"rimY{sy}", (2 * o + 0.08, 0.2, RIM_H), (0, sy * (HX + WALL / 2), WALL_H + RIM_H / 2), M["leather"], Vg,
                bevel=0.05)
    for sx in (-1, 1):
        kit.box(f"wallX{sx}", (WALL, 2 * HX, WALL_H - GROUND), (sx * (HX + WALL / 2), 0, (WALL_H + GROUND) / 2), M["wicker"], Vg)
        kit.box(f"rimX{sx}", (0.2, 2 * HX + 0.18, RIM_H), (sx * (HX + WALL / 2), 0, WALL_H + RIM_H / 2), M["leather"], Vg,
                bevel=0.05)
    # low dividers: four corner compartments around a middle
    for sx in (-1, 1):
        kit.box(f"divX{sx}", (HX - 0.32, 0.05, 0.5), (sx * (0.32 + (HX - 0.32) / 2), 0, 0.25), M["wicker"], Vg)
    for sy in (-1, 1):
        kit.box(f"divY{sy}", (0.05, HX - 0.5, 0.5), (0, sy * (0.5 + (HX - 0.5) / 2), 0.25), M["wicker"], Vg)
    # two gas tanks in the middle
    for sy in (-1, 1):
        kit.cyl(f"tank{sy}", 0.18, 0.66, (0, sy * 0.25, 0.35), M["tank"], Vg, n=24)
        kit.cyl(f"tankcap{sy}", 0.09, 0.08, (0, sy * 0.25, 0.7), M["steel_dark"], Vg, n=16)
    # rope handles on the rim (loops on the outside)
    for sx in (-1, 1):
        for sy in (-1, 1):
            kit.box(f"hand{sx}{sy}", (0.04, 0.34, 0.04), (sx * (HX + WALL + 0.06), sy * 0.62, 0.75), M["rope"], Vg,
                    bevel=0.015)
    # the burner frame: two posts, a crossbar and the double burner
    for sx in (-1, 1):
        kit.cyl(f"post{sx}", 0.04, 1.4, (sx * (HX + 0.02), 0, 1.72), M["steel"], Vg, n=12)
    kit.box("crossbar", (2 * HX + 0.12, 0.07, 0.07), (0, 0, 2.42), M["steel"], Vg, bevel=0.015)
    for sx in (-1, 1):
        kit.box(f"burnbody{sx}", (0.14, 0.14, 0.16), (sx * 0.2, 0, 2.5), M["steel_dark"], Vg, bevel=0.03)
        kit.cyl(f"burnnoz{sx}", 0.05, 0.14, (sx * 0.2, 0, BURN_Z + 0.03), M["steel_dark"], Vg, n=12)
        kit.cyl(f"pilot{sx}", 0.012, 0.03, (sx * 0.2 + 0.07, 0, BURN_Z + 0.06), M["pilot"], Vg, n=8)
    # the flames: cones, grown by the roar
    fg = kit.empty("flames", (0, 0, BURN_Z + 0.08), Vg)
    ctx["flames"] = fg
    ctx["flame_parts"] = []
    for sx in (-1, 1):
        for nm, r0, h, mat in (("f", 0.11, 1.35, M["flame"]), ("c", 0.06, 0.8, M["flame_core"])):
            c = kit.cyl(f"flame{nm}{sx}", r0, h, (sx * 0.2, 0, h / 2), mat, fg, n=16, r2=0.015)
            ctx["flame_parts"].append((c, h))
    # the sandbag (a fat canvas bag) with its rope, the four flasks, a cup, the satchel, the phone
    bag = kit.empty("bag", (0.95, 0.93, 0.0), Vg)
    kit.box("bagm", (0.44, 0.36, 0.34), (0, 0, 0.17), M["canvas"], bag, bevel=0.1)
    kit.box("bagneck", (0.2, 0.2, 0.1), (0, 0, 0.38), M["canvas"], bag, bevel=0.05)
    kit.cyl("bagtie", 0.075, 0.04, (0, 0, 0.34), M["rope"], bag, n=12)
    ctx["bag"] = bag
    rope = kit.cyl("bagrope", 0.016, 1.0, (0, 0, 0), M["rope"], Vg, n=8)
    ctx["bagrope"] = rope
    ctx["flasks"] = []
    for k in range(4):
        fl = kit.empty(f"flask{k}", (0, 0, 0), Vg)
        kit.cyl(f"flaskb{k}", 0.048, 0.22, (0, 0, 0.11), M["flask"], fl, n=16)
        kit.cyl(f"flaskc{k}", 0.042, 0.05, (0, 0, 0.245), M["flask_cap"], fl, n=16)
        ctx["flasks"].append(fl)
    cup = kit.empty("cup", (0, 0, 0), Vg)
    kit.cyl("cupb", 0.052, 0.1, (0, 0, 0.05), M["cup"], cup, n=16, r2=0.062)
    kit.cyl("cuptea", 0.05, 0.01, (0, 0, 0.095), M["tea"], cup, n=16)
    ctx["cup"] = cup
    sat = kit.empty("satchel", (0.18, -0.75, 0.0), Vg)
    kit.box("satm", (0.5, 0.3, 0.28), (0, 0, 0.14), M["bag"], sat, bevel=0.06)
    kit.box("satflap", (0.52, 0.32, 0.03), (0, -0.0, 0.3), M["bag"], sat, rot=(0.0, 0.0, 0.0), bevel=0.01)
    ctx["satchel"] = sat
    ph = kit.empty("phone", (1.21, 0.35, RIM_TOP + 0.006), Vg)
    kit.box("phoneb", (0.075, 0.15, 0.012), (0, 0, 0), M["phone"], ph, bevel=0.01)
    kit.box("phones", (0.064, 0.136, 0.002), (0, 0, 0.007), M["screen"], ph)
    ctx["phone"] = ph
    # the lore plant: four short upright slate-blue strokes across the leather of the fourth corner's rim (S19)
    for k in range(4):
        kit.box(f"tally{k}", (0.03, 0.15, 0.005), (0.55 + (k - 1.5) * 0.075, HX + WALL / 2, RIM_TOP + 0.002), M["tally"],
                Vg)
    # the cold lamp-lit wicker on the outside of the rim: nothing written anywhere


def build_envelope(kit, ctx, M):
    E = ctx["E"]
    n_g, n_r = 16, 26

    def prof(s):
        return 1.3 * (1 - s) ** 2 + ENV_R * (math.sin(math.pi * s ** 0.9)) ** 0.7

    for g in range(n_g):
        verts, fcs = [], []
        cols = 5
        for i in range(n_r + 1):
            s = i / n_r
            r = prof(s)
            for j in range(cols + 1):
                u = j / cols
                a = 2 * math.pi * (g + u) / n_g
                rr = r * (1 + 0.035 * math.sin(math.pi * u))
                verts.append((rr * math.cos(a), rr * math.sin(a), ENV_H * s))
        for i in range(n_r):
            for j in range(cols):
                a = i * (cols + 1) + j
                fcs.append((a, a + 1, a + cols + 2, a + cols + 1))
        ob = kit.mesh_obj(f"gore{g}", verts, fcs, M["cream"] if g % 2 == 0 else M["green"], E, smooth=True)
        ob.visible_shadow = False
    # the black mouth ring
    for k in range(24):
        a = 2 * math.pi * k / 24
        kit.box(f"ring{k}", (0.36, 0.1, 0.1), (1.3 * math.cos(a), 1.3 * math.sin(a), 0.0), M["steel_dark"], E,
                rot=(0, 0, a + math.pi / 2))
    ctx["cables"] = [kit.cyl(f"cable{k}", 0.014, 1.0, (0, 0, 0), M["steel_dark"], None, n=6) for k in range(4)]
    for c in ctx["cables"]:
        c.visible_shadow = False


# ------------------------------------------------------------------------------------------------ the creature


def build_creature(kit, ctx, M):
    """The Loose One, built once. Every piece is an empty (its pivot at the piece's centre) with a block and two
    near-black caps on the faces that look across a gap."""
    cop = kit.plastic("#b8693a", 0.5, name="cre copper", spec=0.35)
    sla = kit.plastic("#46688a", 0.58, name="cre slate", spec=0.25)
    for mm, hx, st in ((cop, "#b8693a", 0.18), (sla, "#46688a", 0.55)):   # a little light of their own: slate stays blue
        b = mm.node_tree.nodes["Principled BSDF"]
        b.inputs["Emission Color"].default_value = kit.col(hx)
        b.inputs["Emission Strength"].default_value = st
    fadeable(ctx, cop)
    fadeable(ctx, sla)
    blk = fadeable(ctx, kit.plastic("#08080b", 0.9, name="cre dark", spec=0.1))
    eye = fadeable(ctx, kit.emit("#d4581a", 1.5, name="cre eye"))
    glint = fadeable(ctx, kit.emit("#fff0d8", 3.0, name="cre glint"))
    mouth = fadeable(ctx, kit.plastic("#050507", 0.9, name="cre mouth", spec=0.0))
    root = kit.empty("cre", (0, 0, 0), ctx["V"])
    ctx["cre"] = root
    pieces = []

    def piece(name, size, base, mat, group, bevel=0.012):
        e = kit.empty(f"cre.{name}", base, root)
        kit.box(f"cre.{name}.b", size, (0, 0, 0), mat, e, bevel=bevel)
        w, d, h = size
        kit.box(f"cre.{name}.cap", (w * 0.97, d * 0.97, 0.006), (0, 0, -(h / 2 + 0.0015)), blk, e)   # only the undersides
        p = {"e": e, "base": V(base), "group": group, "name": name}
        pieces.append(p)
        return e

    for sx in (-1, 1):
        for k in range(3):
            piece(f"leg{sx}{k}", (0.34, 0.34, LH), (sx * 0.17, 0, k * (LH + G) + LH / 2), sla, f"leg{sx}")
    tz0 = 3 * LH + 3 * G
    for k in range(4):
        piece(f"tor{k}", (0.68, 0.34, TH), (0, 0, tz0 + k * (TH + G) + TH / 2), cop, "torso")
    ttop = tz0 + 4 * TH + 3 * G
    for sx in (-1, 1):
        for k in range(3):
            piece(f"arm{sx}{k}", (0.34, 0.34, LH), (sx * 0.51, 0, ttop - k * (LH + G) - LH / 2), cop, f"arm{sx}")
    hz0 = ttop + G
    HW = 0.40
    for k in range(4):                      # k = 0 is the bottom slice
        e = piece(f"head{k}", (HW, HW, SLICE), (0, 0, hz0 + k * (SLICE + G) + SLICE / 2), sla, f"head{k}", bevel=0.022)
        if k == 2:                          # the second slice from the top: two small round copper eyes
            for sx in (-1, 1):
                kit.cyl(f"cre.eye{sx}", 0.026, 0.012, (sx * 0.09, -HW / 2 - 0.004, 0.0), eye, e, rot=(math.pi / 2, 0, 0),
                        n=20)
                kit.sphere(f"cre.glint{sx}", 0.0062, (sx * 0.09 + 0.008, -HW / 2 - 0.011, 0.009), glint, e, seg=8)
        if k == 0:                          # the fourth slice: a short flat black mouth line
            kit.box("cre.mouth", (0.12, 0.012, 0.018), (0, -HW / 2 - 0.002, 0.0), mouth, e)
    ctx["cre_pieces"] = pieces
    # fixed scatter for each piece (the same every time): a cloud about 4 m across, every piece at its own angle
    for i, p in enumerate(pieces):
        h = [kit.hash01(i, 1), kit.hash01(i, 2), kit.hash01(i, 3), kit.hash01(i, 4), kit.hash01(i, 5), kit.hash01(i, 6)]
        p["jp"] = V(((h[0] - 0.5) * 3.8, (h[1] - 0.5) * 3.8, (h[2] - 0.5) * 2.6 - 0.35))
        p["jr"] = V(((h[3] - 0.5) * 6.2, (h[4] - 0.5) * 6.2, (h[5] - 0.5) * 6.2))
    # slightly off: an arm block tilted, a leg block twisted, the torso blocks not quite stacked
    OFF = {"arm-11": (0, 0.28, 0.05), "arm12": (0.22, 0, 0.05), "leg-12": (0, 0, 0.42), "leg11": (0, 0, -0.3),
           "tor3": (0, 0, 0.16), "tor1": (0, 0, -0.1), "head0": (0, 0, 0.35), "head1": (0, 0, -0.22),
           "head2": (0, 0, 0.5), "head3": (0, 0, -0.3)}
    for p in pieces:
        p["off"] = V(OFF.get(p["name"], (0, 0, 0)))
    ctx["cre_off_pos"] = {"tor3": V((0.05, 0.02, 0)), "arm12": V((0.03, -0.05, 0)), "head2": V((0.025, 0, 0))}


def pose_creature(ctx, kit, c, t):
    """Place the creature for the cue `c` (already resolved at time t). Returns the root position."""
    root = ctx["cre"]
    pose = c.get("pose", "hidden")
    if pose == "hidden":
        return None
    root.parent = ctx["L"] if c.get("on") == "L" else ctx["V"]
    s = float(c.get("s", {"scatter": 1.0, "off": 0.0, "exact": 0.0}.get(pose, 0.0)))
    off = 1.0 if pose == "off" else 0.0
    pos = c.get("pos", [0, 0, 0])
    root.location = (pos[0], pos[1], pos[2])
    root.rotation_euler = (0, 0, math.radians(c.get("yaw", 0.0)))
    head = c.get("head")
    arms = c.get("arms", [0, 0])
    for p in ctx["cre_pieces"]:
        loc = V(p["base"]) + p["jp"] * s
        rot = p["jr"] * s + p["off"] * off
        if off and p["name"] in ctx["cre_off_pos"]:
            loc = loc + ctx["cre_off_pos"][p["name"]]
        g = p["group"]
        if g.startswith("head") and head:
            rot = V((rot.x, rot.y, rot.z + math.radians(head[int(g[4])])))
        if g.startswith("arm"):
            sx = -1 if g.startswith("arm-") else 1
            ang = math.radians(arms[0 if sx < 0 else 1])
            if ang:
                # swing the whole arm forward (toward -y) about the shoulder
                sh = V((sx * 0.51, 0, ctx["cre_shoulder"]))
                rel = loc - sh
                m = Matrix.Rotation(-ang, 3, "X")
                loc = sh + m @ rel
                rot = V((rot.x - ang, rot.y, rot.z))
        p["e"].location = loc
        p["e"].rotation_euler = (rot.x, rot.y, rot.z)
    return V(pos)


# ------------------------------------------------------------------------------------------------ the world


def build_landscape(kit, ctx, M):
    L = ctx["L"]
    kit.box("ground", (1500, 1500, 1.0), (0, 0, -0.5), M["ground"], L)
    kit.box("ground2", (110, 90, 1.02), (LAND_SHIFT.x, LAND_SHIFT.y, -0.5), M["ground2"], L)
    mist = kit.box("mist", (1500, 1500, 0.02), (0, 0, 0.45), mist_mat(kit, ctx), L)
    mist.visible_shadow = False
    ctx["mist"] = mist
    rnd = lambda i, a=0: kit.hash01(i, a)
    # hedges: long dark boxes, each its own height, so the mist rises over them one by one
    hedges = [((-22, -38), 0, 70, 0.8), ((30, -30), 90, 60, 1.3), ((-40, 24), 90, 80, 1.8), ((22, 38), 0, 90, 2.3),
              ((-70, -70), 0, 120, 2.7), ((60, 70), 90, 110, 3.1), ((0, 90), 0, 140, 1.6), ((95, -20), 90, 100, 2.0),
              ((LAND_SHIFT.x + 38, LAND_SHIFT.y + 0), 90, 80, 2.2), ((LAND_SHIFT.x, LAND_SHIFT.y + 44), 0, 90, 2.6),
              ((LAND_SHIFT.x - 40, LAND_SHIFT.y - 10), 90, 70, 1.2)]
    for i, (p, rot, ln, h) in enumerate(hedges):
        kit.box(f"hedge{i}", (ln, 1.3, h), (p[0], p[1], h / 2), M["hedge"], L, rot=(0, 0, math.radians(rot)), bevel=0.2)
    # barns and trees poke up through the mist like islands
    for i, (p, rot) in enumerate([((-62, 82), 20), ((88, 46), -15), ((34, -112), 70), ((-120, -30), 100),
                                  ((LAND_SHIFT.x + 70, LAND_SHIFT.y + 50), 10)]):
        b = kit.empty(f"barn{i}", (p[0], p[1], 0), L)
        b.rotation_euler = (0, 0, math.radians(rot))
        kit.box(f"barnw{i}", (14, 9, 5.2), (0, 0, 2.6), M["barn"], b, bevel=0.08)
        for sy in (-1, 1):
            kit.box(f"barnr{i}{sy}", (14.6, 5.6, 0.35), (0, sy * 2.15, 6.0), M["barn_roof"], b,
                    rot=(sy * math.radians(-32), 0, 0), bevel=0.05)
    for i in range(14):
        a = rnd(i, 7) * 2 * math.pi
        r = 30 + rnd(i, 8) * 150
        px, py = r * math.cos(a), r * math.sin(a)
        h = 6 + rnd(i, 9) * 5
        kit.box(f"trunk{i}", (0.7, 0.7, h * 0.6), (px, py, h * 0.3), M["trunk"], L)
        kit.box(f"leaf{i}", (4.6, 4.6, h * 0.55), (px, py, h * 0.75), M["leaf"], L, bevel=0.5)
    for k in range(9):                      # low hills round the valley
        a = 2 * math.pi * k / 9 + 0.3
        r = 330 + 40 * kit.hash01(k, 3)
        h = kit.sphere(f"hill{k}", 1.0, (r * math.cos(a), r * math.sin(a), 0), M["hill"], L, seg=14)
        h.scale = (95 + 30 * kit.hash01(k, 4), 70 + 30 * kit.hash01(k, 5), 42 + 12 * kit.hash01(k, 6))
    # the launch field: a lamp on a pole, a trailer, a cold-air fan
    kit.cyl("lamppole", 0.07, 3.4, (-4.6, -3.6, 1.7), M["steel"], L, n=10)
    kit.box("lamphead", (0.5, 0.3, 0.14), (-4.6, -3.6, 3.45), M["steel_dark"], L, bevel=0.03)
    kit.box("lampglow", (0.4, 0.22, 0.03), (-4.6, -3.6, 3.36), M["lampglow"], L)
    kit.box("trailer", (4.6, 2.0, 2.0), (-9.5, 6.0, 1.3), M["trailer"], L, bevel=0.08)
    for sx in (-1.6, 1.6):
        kit.cyl(f"tyre{sx}", 0.4, 0.3, (-9.5 + sx, 5.0, 0.4), M["tyre"], L, rot=(math.pi / 2, 0, 0), n=16)
    kit.cyl("fanframe", 0.6, 0.3, (4.2, -5.0, 0.75), M["steel_dark"], L, rot=(0, math.pi / 2, 0), n=20)
    kit.box("fanstand", (0.5, 0.9, 0.5), (4.2, -5.0, 0.25), M["steel_dark"], L, bevel=0.04)


def build_kitchen(kit, ctx, M):
    K = ctx["K"]
    kit.box("k_floor", (5.0, 4.4, 0.1), (0, 0, -0.05), M["k_floor"], K)
    kit.box("k_ceil", (5.0, 4.4, 0.1), (0, 0, 2.65), M["k_wall"], K)
    kit.box("k_wallN", (5.0, 0.1, 2.6), (0, 2.2, 1.3), M["k_wall"], K)
    kit.box("k_wallS", (5.0, 0.1, 2.6), (0, -2.2, 1.3), M["k_wall"], K)
    kit.box("k_wallE", (0.1, 4.4, 2.6), (2.5, 0, 1.3), M["k_wall"], K)
    kit.box("k_wallW", (0.1, 4.4, 2.6), (-2.5, 0, 1.3), M["k_wall"], K)
    kit.box("k_window", (1.1, 0.04, 0.9), (0.0, 2.14, 1.5), M["k_window"], K)
    kit.box("k_frame", (1.2, 0.05, 0.05), (0.0, 2.13, 1.97), M["k_wood"], K)
    kit.box("k_table", (0.9, 1.4, 0.06), (0, 0, 0.75), M["k_wood"], K, bevel=0.015)
    for sx in (-1, 1):
        for sy in (-1, 1):
            kit.box(f"k_leg{sx}{sy}", (0.07, 0.07, 0.72), (sx * 0.4, sy * 0.62, 0.36), M["k_wood"], K)
    for i, sx in enumerate((-1, 1)):
        kit.cyl(f"k_mug{i}", 0.05, 0.1, (sx * 0.22, 0.1 - 0.2 * sx, 0.83), M["k_mug"], K, n=16)
        kit.cyl(f"k_tea{i}", 0.045, 0.01, (sx * 0.22, 0.1 - 0.2 * sx, 0.875), M["tea"], K, n=16)
    kit.box("k_chairA", (0.42, 0.42, 0.05), (-1.5, -1.2, 0.46), M["k_wood"], K)
    kit.box("k_chairAb", (0.42, 0.05, 0.5), (-1.5, -1.0, 0.72), M["k_wood"], K)
    kit.cyl("k_cord", 0.008, 0.7, (0, 0, 2.3), M["steel_dark"], K, n=6)
    kit.sphere("k_bulb", 0.06, (0, 0, 1.92), M["k_lamp"], K, seg=10)
    kit.box("k_shelf", (1.4, 0.25, 0.04), (-1.5, 2.05, 1.5), M["k_wood"], K)
    kit.box("k_cup2", (0.12, 0.12, 0.14), (-1.5, 2.0, 1.59), M["k_mug"], K, bevel=0.02)


def build(kit, story, tl):
    ctx = {"env_glow": [], "fade": [], "tilt_cache": None}
    M = new_materials(kit, ctx)
    ctx["M"] = M
    build_sky(kit, ctx)
    ctx["V"] = kit.empty("V")
    ctx["E"] = kit.empty("E", tuple(PIVOT))
    ctx["L"] = kit.empty("L")
    ctx["K"] = kit.empty("K", tuple(KITCHEN))
    ctx["SUN"] = kit.empty("SUNRIG", tuple(PIVOT))
    build_basket(kit, ctx, M)
    build_envelope(kit, ctx, M)
    ctx["cre_shoulder"] = 3 * LH + 3 * G + 4 * TH + 3 * G
    build_creature(kit, ctx, M)
    build_landscape(kit, ctx, M)
    build_kitchen(kit, ctx, M)
    # the sun: a disc and a soft glow far east, and the light itself
    sun = ctx["SUN"]
    disc = kit.cyl("sundisc", 10.0, 0.5, (0, 0, 0), M["sunmat"], sun, n=40, rot=(math.pi / 2, 0, 0))
    ctx["sundisc"] = disc
    kit.light("sun", "SUN", (0, 0, 0), 1.0, "#ffd9a0", size=0.2, parent=sun)
    kit.LIGHTS["sun"]["light"].angle = math.radians(2.5)
    kit.light("flame", "POINT", (0, 0, BURN_Z + 0.55), 380.0, ORANGE, size=0.25, parent=ctx["V"])
    kit.light("pilot", "POINT", (0.3, 0, BURN_Z + 0.1), 5.0, ORANGE, size=0.05, parent=ctx["V"], shadow=False)
    kit.light("lamp", "POINT", (-4.6, -3.55, 3.2), 520.0, "#ffe0b0", size=0.2, parent=ctx["L"])
    kit.light("fkey", "AREA", (0, 0, 2), 40.0, "#ffe6cc", size=1.0, shadow=False)
    kit.light("ckey", "POINT", (0, 0, 2), 0.0, "#ff9a50", size=0.3)
    kit.light("crim", "POINT", (0, 0, 2), 0.0, "#8a9ad8", size=0.3)
    kit.light("cbounce", "AREA", (0, 0, 0), 0.0, "#6f95ff", size=2.0, shadow=False, rot=(math.pi, 0, 0))
    kit.light("klamp", "POINT", (0, 0, 1.85), 0.0, "#ffd29a", size=0.1, parent=ctx["K"])
    kit.light("kfill", "AREA", (0, -1.6, 2.1), 0.0, "#ffe0b8", size=2.5, parent=ctx["K"], shadow=False)
    for nm in ("fkey", "kfill"):
        kit.LIGHTS[nm]["obj"].visible_camera = False
    for ob in bpy.data.objects:
        if ob.type == "MESH" and ob.name.startswith(("post", "crossbar", "cable")):
            pass
    # the fog nodes (the day changes the haze colour)
    d = kit.FOG["density"]
    fc = tuple(kit.FOG["color"])
    ctx["fog_cols"] = [nd for m in bpy.data.materials if m.node_tree for nd in m.node_tree.nodes
                       if nd.type == "EMISSION" and all(abs(a - b) < 1e-6 for a, b in
                                                         zip(nd.inputs["Color"].default_value[:3], fc))]
    ctx["init"] = False
    return ctx


# ------------------------------------------------------------------------------------------------ animate


def tilt_matrix(deg):
    th = math.radians(deg)
    k = V((-0.7071, 0.7071, 0.0))                    # zhat x (toward the fourth corner)
    return Matrix.Translation(PIVOT) @ Matrix.Rotation(th, 4, k) @ Matrix.Translation(-PIVOT)


def cam_now(story, tl, t):
    import __main__

    shot = _shot(tl, t)
    spec = next(s for s in story["shots"] if s["id"] == shot["id"])
    if hasattr(__main__, "cam_at"):
        loc, tgt, lens, roll = __main__.cam_at(spec, shot, t, None, tl)
        return V(loc), V(tgt), spec
    return V(spec["cam"][0][1]), V(spec["cam"][0][2]), spec


def roar_at(tl, t):
    v = 0.0
    for c in _cues(tl, "roar"):
        up, hold, down, peak = c.get("up", 0.6), c.get("hold", 0.8), c.get("down", 0.9), c.get("peak", 1.0)
        x = t - c["t"]
        if x < 0:
            continue
        v = max(v, peak * _ss(x / up) * (1 - _ss((x - up - hold) / down)))
    return v


def animate(kit, story, tl, t, ctx):
    from blocky import kit as K

    over = {}
    if not ctx["init"]:
        for name in story["cast"]:
            ob = bpy.data.objects.get(name)
            if ob is not None:
                ob.parent = ctx["V"]
        ctx["init"] = True
    cam_loc, cam_tgt, spec = cam_now(story, tl, t)
    kitchen = spec.get("room") == "kitchen"
    basket_frame = spec.get("frame", "basket") == "basket"
    # ---- the day
    d = _ease_value(_cues(tl, "dawn"), "v", t, 0.0)
    (_, hor, zen, fog, mistc, suncol, sunp, sunel, skys, mglow) = day(d)
    rm = ctx["sky_ramp"].color_ramp
    rm.elements[0].color = (*_lin(hor), 1)
    rm.elements[1].color = (*_lin(zen), 1)
    ctx["sky_bg"].inputs["Strength"].default_value = skys * spec.get("amb", 1.0)
    # ---- the roar
    roar = roar_at(tl, t)
    fogc = tuple(fog[i] * (1 - 0.45 * roar) + _hex("#f2a08a")[i] * 0.45 * roar for i in range(3))
    for nd in ctx["fog_cols"]:
        nd.inputs["Color"].default_value = (*_lin(fogc), 1)
    sock_color(ctx["mist_col"], mistc)
    # ---- the lean and the frame
    deg = _ease_value(_cues(tl, "tilt"), "deg", t, 0.0)
    Mt = tilt_matrix(deg)
    MV = Matrix.Identity(4) if basket_frame else Mt
    ME = Mt.inverted() if basket_frame else Matrix.Identity(4)
    ctx["V"].matrix_basis = MV
    # ---- the envelope: lying on the field to standing
    up = _ease_value(_cues(tl, "env"), "up", t, 1.0)
    ang = math.radians(-88.0 * (1 - up))
    E = ctx["E"]
    E.matrix_basis = ME @ Matrix.Translation(PIVOT) @ Matrix.Rotation(ang, 4, "X")
    ctx["flames"].rotation_euler = (ang, 0, 0)
    # ---- the landscape
    alt = _ease_value(_cues(tl, "alt"), "alt", t, 0.0)
    fld = _switch(_cues(tl, "field"), "f", t, 0)
    shift = -LAND_SHIFT if fld else V((0, 0, 0))
    ctx["L"].matrix_basis = ME @ Matrix.Translation(V((shift.x, shift.y, GROUND - alt)))
    mh = 0.45 + 2.95 * _ss((alt - 2.0) / 10.0)
    if _switch(_cues(tl, "mist"), "h", t, None) is not None:
        mh = _ease_value(_cues(tl, "mist"), "h", t, mh)
    ctx["mist"].location.z = mh
    # ---- the sun rig and the sky
    el = math.radians(sunel)
    sun = ctx["SUN"]
    sun.matrix_basis = ME @ Matrix.Translation(PIVOT)
    dist = 420.0
    ctx["sundisc"].location = (dist * math.cos(el), 0.0, dist * math.sin(el))
    ctx["sundisc"].rotation_euler = (math.pi / 2, 0, math.pi / 2 + 0.0)
    ctx["sundisc"].hide_render = sunel < -0.5
    sl = K.LIGHTS["sun"]["obj"]
    sl.location = (dist * math.cos(el), 0.0, dist * math.sin(el))
    sl.rotation_euler = (V((-math.cos(el), 0, -math.sin(el)))).to_track_quat("-Z", "Y").to_euler()
    K.LIGHTS["sun"]["base"] = (sunp * _ss((sunel + 3.0) / 4.0)) if not kitchen else 0.0
    K.LIGHTS["sun"]["light"].color = _lin(suncol)
    mp = ctx["sky_map"]
    mp.inputs["Rotation"].default_value = (ME.to_3x3().inverted()).to_euler()
    # ---- the mist's glow
    ctx["mist_emit"].default_value = mglow * 0.55 + 0.75 * roar
    sock_color(ctx["mist_emit_col"], mistc)
    u = min(1.0, roar * 1.3)
    oc = tuple(mistc[i] * (1 - u) + _hex(ORANGE)[i] * u for i in range(3))
    ctx["mist_emit_col"].default_value = (*_lin(oc), 1)
    for s in ctx["env_glow"]:
        s.default_value = 1.35 * roar
    # ---- the flames
    for ob, h in ctx["flame_parts"]:
        ob.scale = (1.0, 1.0, max(0.001, roar))
        ob.location.z = h * max(0.001, roar) / 2
        ob.hide_render = roar < 0.015
    over["flame"] = roar
    over["pilot"] = 1.0
    ctx["flames"].hide_render = False
    # ---- the field lamp, the kitchen
    over["lamp"] = 1.0 - _ss((alt - 3.0) / 14.0)
    over["klamp"] = 0.0
    over["kfill"] = 0.0
    if kitchen:
        K.LIGHTS["klamp"]["base"] = 70.0
        over["klamp"] = 1.0
        K.LIGHTS["kfill"]["base"] = 30.0
        over["kfill"] = 1.0
    # ---- the plants: flasks, bag, rope, cup, phone
    fl = _switch(_cues(tl, "flasks"), "state", t, "corner")
    rim_x = [0.05, 0.27, 0.49, 0.71]
    for i, ob in enumerate(ctx["flasks"]):
        ob.hide_render = False
        if fl == "none":
            hide(ob, True)
            continue
        hide(ob, False)
        if i < 3 or fl == "rim":
            ob.location = (rim_x[i], -1.21, RIM_TOP)
        elif fl == "corner":
            ob.location = (0.28, 0.96, 0.0)
        else:                                   # "end": Callum's flask stands on his corner's rim
            ob.location = (1.21, 0.62, RIM_TOP)
    bs = _switch(_cues(tl, "bag"), "state", t, "tied")
    bag, rope = ctx["bag"], ctx["bagrope"]
    hide(bag, bs == "none")
    hide(rope, bs == "none")
    if bs == "tied":
        bag.location = (0.95, 0.93, 0.0)
        bag.rotation_euler = (0, 0, 0.3)
        stretch(rope, (0.95, 0.93, 0.36), (0.8, 0.64, 1.2))
        rope.parent = ctx["V"]
    elif bs == "grass":
        bag.parent = ctx["L"] if False else ctx["V"]
        bag.location = (2.1, -1.5, 0.0)
        bag.rotation_euler = (0, 0, 0.8)
        stretch(rope, (2.1, -1.5, 0.05), (2.4, -1.9, 0.03))
    if bs == "tied":
        bag.parent = ctx["V"]
    cup = ctx["cup"]
    con = _switch(_cues(tl, "cup"), "on", t, False)
    hide(cup, not con)
    cy = _ease_value(_cues(tl, "cup"), "y", t, -0.55)
    cup.location = (1.21, cy, RIM_TOP)
    ph = ctx["phone"]
    hide(ph, not _switch(_cues(tl, "phone"), "on", t, False))
    hide(ctx["satchel"], not _switch(_cues(tl, "satchel"), "on", t, False))
    # ---- the cables from the frame to the mouth ring
    posts = [V((1.2, 0, 2.42)), V((-1.2, 0, 2.42))]
    ringp = [V((1.25, 0.4, 0)), V((1.25, -0.4, 0)), V((-1.25, 0.4, 0)), V((-1.25, -0.4, 0))]
    Em = ME @ Matrix.Translation(PIVOT) @ Matrix.Rotation(ang, 4, "X")
    for i, cb in enumerate(ctx["cables"]):
        a = MV @ posts[0 if i < 2 else 1]
        b = Em @ ringp[i if i < 2 else i]
        stretch(cb, a, b)
        cb.hide_render = up < 0.02
    # ---- the creature
    cs = _cues(tl, "cre")
    cur = None
    for c in cs:
        if c["t"] <= t + 1e-9:
            cur = c
    pos = None
    cre = ctx["cre"]
    if cur and cur.get("pose", "hidden") != "hidden":
        rr = dict(cur)
        # glide between this cue's pos and the next one's (a slow approach is never seen: the cuts hide it)
        pos = pose_creature(ctx, K, rr, t)
        a = cur.get("alpha", "roar")
        alpha = min(1.0, roar * 1.7) if a == "roar" else float(a)
        if alpha < 0.012:
            hide_tree(cre, True)
        else:
            hide_tree(cre, False)
            for sck in ctx["fade"]:
                sck.default_value = 1.0 - alpha
        import os
        if os.environ.get("DAWN_DEBUG"):
            print("cre", round(t, 2), pos, alpha, "hidden" if cre.hide_render else "shown", cre.matrix_world.translation, flush=True)
        ck = cur.get("key", 380.0)
        cp = V(pos) + V((0, 0, 1.3))
        away = (cp - V((cam_loc.x, cam_loc.y, cp.z))) if cur.get("on") != "L" else V((0.7, 0.7, 0))
        away = away.normalized() if away.length > 1e-3 else V((0, 1, 0))
        K.LIGHTS["ckey"]["obj"].location = cp + away * 0.9 + V((0, 0, 1.5))
        K.LIGHTS["ckey"]["base"] = ck * max(roar, cur.get("kfloor", 0.0)) * (1.0 if alpha > 0.012 else 0.0)
        K.LIGHTS["ckey"]["obj"].parent = cre.parent
        K.LIGHTS["crim"]["obj"].location = cp + away * 1.1 + V((0, 0, 0.3))
        K.LIGHTS["crim"]["base"] = cur.get("rim", 90.0) * alpha
        K.LIGHTS["crim"]["obj"].parent = cre.parent
        cb = K.LIGHTS["cbounce"]
        cb["obj"].location = V(pos) + V((0, 0, -0.3))
        cb["obj"].parent = cre.parent
        cb["base"] = cur.get("bounce", 0.0) * alpha
        over["ckey"] = 1.0
        over["crim"] = 1.0
        over["cbounce"] = 1.0
    else:
        hide_tree(cre, True)
        over["ckey"] = 0.0
        over["crim"] = 0.0
        over["cbounce"] = 0.0
    import os
    if os.environ.get("DAWN_DEBUG") == "ray":
        dg = bpy.context.evaluated_depsgraph_get()
        dg.update()
        d = (cam_tgt - cam_loc).normalized()
        ok, loc, nrm, idx, ob, mat = bpy.context.scene.ray_cast(dg, cam_loc, d)
        print("ray", round(t, 2), tuple(round(x, 2) for x in cam_loc), ob.name if ob else None, (loc - cam_loc).length if ok else None, flush=True)
    # ---- the soft key light that rides the camera
    key = spec.get("key", 0.0)
    over["fkey"] = 0.0
    if key:
        fk = K.LIGHTS["fkey"]["obj"]
        fwd = (cam_tgt - cam_loc)
        D = max(0.6, fwd.length)
        fwd.normalize()
        right = fwd.cross(V((0, 0, 1)))
        right = right.normalized() if right.length > 1e-3 else V((1, 0, 0))
        fk.location = cam_loc + right * 0.45 + V((0, 0, 0.35)) - fwd * 0.2
        fk.rotation_euler = (cam_tgt - fk.location).to_track_quat("-Z", "Y").to_euler()
        K.LIGHTS["fkey"]["base"] = key * (min(D, 5.0) / 2.0) ** 2
        warm = _mixhex("#b8c4f0", "#ffe2bc", min(1.0, d * 1.2))
        K.LIGHTS["fkey"]["light"].color = _lin(warm)
        over["fkey"] = 1.0
        if kitchen:
            over["fkey"] = 0.6
    return over
