"""Dawn Flight (ep31, redo): a hot-air balloon basket at dawn over a sea of mist, a launch field, a kitchen, and
three small montage sets (a field gate, a cottage door, a lane by a dry-stone wall) plus the inside of Rosa's trailer.
Built from kit.py's parts; nothing here is shared with another story's set.

Coordinates: the basket's floor centre is the origin, z up. The basket is 2.3 m inside with a thick leather rim; the
people stand at its north rim (y about 0.6) with their hands on two worn patches. The sun is in the east (+x). The
landscape hangs from the group `L`, which sinks by `alt` metres as we rise. The envelope hangs from the group `E`.
`V` holds the basket, the frame and the people. The other sets sit far below the world (z = -300) in zones.

Everyone has seams (rig.py, spec "seams": true): each limb in three blocks, the torso in two, the head in four
slices. The cue `seam` {who, gap, body, head, hand, dur} sets the gaps in cm per character.

Cues read here (all optional):
- dawn {"v": 0..1, "dur"}: the light of the day, 0 plum pre-dawn, 0.35 pink, 1 full gold
- alt {"alt": m, "dur"}; field {"f": 0|1}: launch field or landing field
- roar {"peak", "up", "hold", "down"}: the burner flame and its glow on the envelope and the mist
- env {"up": 0..1, "dur"}: the envelope lying on the field to standing
- seam {"who", "gap", "body", "head", "hand", "dur"}
- the shot spec: "frame": "basket" or "world"; "room": "kitchen" | "trailer" | "mont" (outdoor montage, sun on);
  "key": watts of the soft key light riding the camera; "amb": sky strength
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



# ------------------------------------------------------------------------------------------------ new constants
ZONES = {"gate": V((40, 0, -300)), "door": V((80, 0, -300)), "lane": V((120, 0, -300)), "trailer": V((160, 0, -300))}
PATCH_X = (-0.55, 0.55)          # where Dad's hand and mine rest on the north rim
RIM_Y = HX + WALL / 2            # the north rim's centre line
MIST_BADGE = "#efe4cc"
GREEN = "#2f5a3c"


def new_materials(kit, ctx):
    M = {}
    M["wicker"] = kit.bricks("#b48a55", "#9a7243", "#3f2f1a", scale=7.0, name="wicker", rough=0.9, row=0.25, width=0.5,
                             grime_amt=0.25)
    M["leather"] = kit.plastic("#4a2e1e", 0.5, name="leather rim", spec=0.35)
    M["worn"] = kit.plastic("#7a5a42", 0.55, name="worn leather", spec=0.3)
    M["floor"] = kit.planks("#a07a48", "#80602f", scale=3.5, axis="Y", name="basket floor")
    M["steel"] = kit.metal("#6c7075", 0.4, name="steel")
    M["steel_dark"] = kit.plastic("#2a2d31", 0.5, name="steel dark")
    M["tank"] = kit.metal("#8a8f94", 0.35, name="tank")
    M["rope"] = kit.plastic("#c2a878", 0.9, name="rope")
    M["tally"] = kit.plastic("#4a6378", 0.55, name="tally")
    M["flame"] = kit.emit(ORANGE, 7.0, name="flame")
    M["flame_core"] = kit.emit("#ffc070", 9.0, name="flame core")
    M["pilot"] = kit.emit("#ffa04c", 6.0, name="pilot")
    M["cream"] = emissive_glow_mat(kit, ctx, "env cream", "#efe4cc")
    M["green"] = emissive_glow_mat(kit, ctx, "env green", GREEN)
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
    M["lampglow"] = kit.emit("#ffd9a8", 2.2, name="lamp glow")
    M["sunmat"] = kit.emit("#fff0c0", 5.0, name="sun")
    # the kitchen
    M["k_floor"] = kit.planks("#8a6a45", "#6a4e30", scale=2.0, axis="X", name="kitchen floor")
    M["k_wall"] = kit.grime("#c9b894", 0.8, 2.0, name="kitchen wall")
    M["k_wood"] = kit.plastic("#7a5a38", 0.7, name="kitchen wood")
    M["k_door"] = kit.plastic("#56604a", 0.6, name="cottage door")
    M["k_window"] = kit.emit("#e8d4d6", 1.6, name="kitchen window")
    M["k_win_dark"] = kit.plastic("#4a4a58", 0.9, name="window farm")
    M["k_lamp"] = kit.emit("#ffd9a0", 6.0, name="kitchen bulb")
    M["k_mug"] = kit.plastic("#e8dcc0", 0.5, name="mug")
    M["tea"] = kit.plastic("#6a3a18", 0.3, name="tea")
    M["outside"] = kit.emit("#f4e4d0", 2.2, name="outside daylight")
    # the montage
    M["grass"] = kit.grime("#6f8a4a", 0.7, 0.6, name="meadow", rough=0.95)
    M["gate_wood"] = kit.plastic("#8a6a44", 0.8, name="gate wood")
    M["stone"] = kit.grime("#9a968a", 0.62, 6.0, name="dry stone", rough=0.95)
    M["stone2"] = kit.grime("#857f74", 0.62, 7.0, name="dry stone 2", rough=0.95)
    M["lane"] = kit.grime("#a89a78", 0.7, 0.8, name="lane", rough=0.95)
    M["t_wall"] = kit.grime("#c8a878", 0.8, 3.0, name="trailer wall", rough=0.9)
    M["t_floor"] = kit.planks("#8a6a45", "#6a4e30", scale=2.0, axis="X", name="trailer floor")
    M["t_lamp"] = kit.emit("#ffd9a0", 6.0, name="trailer bulb")
    M["b_green"] = kit.plastic(GREEN, 0.5, name="badge green")
    M["b_cream"] = kit.plastic(MIST_BADGE, 0.5, name="badge cream")
    return M


def disc_mesh(kit, name, centres, r, y, mat, parent, n=14):
    """Many flat discs facing -y in one object (the wall of badges): one mesh, one material."""
    verts, fcs = [], []
    for (cx, cz) in centres:
        b = len(verts)
        for i in range(n):
            a = 2 * math.pi * i / n
            verts.append((cx + r * math.cos(a), y, cz + r * math.sin(a)))
        fcs.append(tuple(reversed(range(b, b + n))))      # normal toward -y
    return kit.mesh_obj(name, verts, fcs, mat, parent)


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
    for sy in (-1, 1):
        kit.cyl(f"tank{sy}", 0.18, 0.66, (-0.0, sy * 0.3, 0.35), M["tank"], Vg, n=24)
        kit.cyl(f"tankcap{sy}", 0.09, 0.08, (0, sy * 0.3, 0.7), M["steel_dark"], Vg, n=16)
    for sx in (-1, 1):
        for sy in (-1, 1):
            kit.box(f"hand{sx}{sy}", (0.04, 0.34, 0.04), (sx * (HX + WALL + 0.06), sy * 0.62, 0.75), M["rope"], Vg,
                    bevel=0.015)
    for sx in (-1, 1):
        kit.cyl(f"post{sx}", 0.04, 1.4, (sx * (HX + 0.02), 0, 1.72), M["steel"], Vg, n=12)
    kit.box("crossbar", (2 * HX + 0.12, 0.07, 0.07), (0, 0, 2.42), M["steel"], Vg, bevel=0.015)
    for sx in (-1, 1):
        kit.box(f"burnbody{sx}", (0.14, 0.14, 0.16), (sx * 0.2, 0, 2.5), M["steel_dark"], Vg, bevel=0.03)
        kit.cyl(f"burnnoz{sx}", 0.05, 0.14, (sx * 0.2, 0, BURN_Z + 0.03), M["steel_dark"], Vg, n=12)
        kit.cyl(f"pilot{sx}", 0.012, 0.03, (sx * 0.2 + 0.07, 0, BURN_Z + 0.06), M["pilot"], Vg, n=8)
    fg = kit.empty("flames", (0, 0, BURN_Z + 0.08), Vg)
    ctx["flames"] = fg
    ctx["flame_parts"] = []
    for sx in (-1, 1):
        for nm, r0, h, mat in (("f", 0.11, 1.35, M["flame"]), ("c", 0.06, 0.8, M["flame_core"])):
            c = kit.cyl(f"flame{nm}{sx}", r0, h, (sx * 0.2, 0, h / 2), mat, fg, n=16, r2=0.015)
            ctx["flame_parts"].append((c, h))
    # the two worn patches on the north rim, exactly under two hands, and the lore tally between them
    top = RIM_TOP + 0.0
    for i, px in enumerate(PATCH_X):
        kit.box(f"worn{i}", (0.3, 0.17, 0.006), (px, RIM_Y, top + 0.004), M["worn"], Vg)
    for k, px in enumerate((-0.07, 0.07)):
        kit.box(f"tally{k}", (0.034, 0.15, 0.006), (px, RIM_Y, top + 0.005), M["tally"], Vg)


def build_landscape(kit, ctx, M):
    L = ctx["L"]
    kit.box("ground", (1500, 1500, 1.0), (0, 0, -0.5), M["ground"], L)
    kit.box("ground2", (110, 90, 1.02), (LAND_SHIFT.x, LAND_SHIFT.y, -0.5), M["ground2"], L)
    mist = kit.box("mist", (1500, 1500, 0.02), (0, 0, 0.45), mist_mat(kit, ctx), L)
    mist.visible_shadow = False
    ctx["mist"] = mist
    rnd = lambda i, a=0: kit.hash01(i, a)
    hedges = [((-22, -38), 0, 70, 0.8), ((30, -30), 90, 60, 1.3), ((-40, 24), 90, 80, 1.8), ((22, 38), 0, 90, 2.3),
              ((-70, -70), 0, 120, 2.7), ((60, 70), 90, 110, 3.1), ((0, 90), 0, 140, 1.6), ((95, -20), 90, 100, 2.0),
              ((LAND_SHIFT.x + 38, LAND_SHIFT.y + 0), 90, 80, 2.2), ((LAND_SHIFT.x, LAND_SHIFT.y + 44), 0, 90, 2.6),
              ((LAND_SHIFT.x - 40, LAND_SHIFT.y - 10), 90, 70, 1.2)]
    for i, (p, rot, ln, h) in enumerate(hedges):
        kit.box(f"hedge{i}", (ln, 1.3, h), (p[0], p[1], h / 2), M["hedge"], L, rot=(0, 0, math.radians(rot)), bevel=0.2)
    for i, (p, rot) in enumerate([((-62, 82), 20), ((88, 46), -15), ((34, -112), 70), ((-120, -30), 100),
                                  ((LAND_SHIFT.x + 70, LAND_SHIFT.y + 50), 10), ((30, 52), 40), ((-52, 30), 5)]):
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
    for k in range(9):
        a = 2 * math.pi * k / 9 + 0.3
        r = 330 + 40 * kit.hash01(k, 3)
        h = kit.sphere(f"hill{k}", 1.0, (r * math.cos(a), r * math.sin(a), 0), M["hill"], L, seg=14)
        h.scale = (95 + 30 * kit.hash01(k, 4), 70 + 30 * kit.hash01(k, 5), 42 + 12 * kit.hash01(k, 6))
    # the launch field: a lamp on a pole, a trailer whose back doors stand open, a cold-air fan
    kit.cyl("lamppole", 0.07, 3.4, (-4.6, -3.6, 1.7), M["steel"], L, n=10)
    kit.box("lamphead", (0.5, 0.3, 0.14), (-4.6, -3.6, 3.45), M["steel_dark"], L, bevel=0.03)
    kit.box("lampglow", (0.4, 0.22, 0.03), (-4.6, -3.6, 3.36), M["lampglow"], L)
    kit.box("trailer", (4.6, 2.0, 2.0), (-9.5, 6.0, 1.3), M["trailer"], L, bevel=0.08)
    kit.box("trailerlit", (1.2, 0.04, 1.2), (-9.5, 4.98, 1.3), M["lampglow"], L)
    for sx in (-1.6, 1.6):
        kit.cyl(f"tyre{sx}", 0.4, 0.3, (-9.5 + sx, 5.0, 0.4), M["tyre"], L, rot=(math.pi / 2, 0, 0), n=16)
    kit.cyl("fanframe", 0.6, 0.3, (4.2, -5.0, 0.75), M["steel_dark"], L, rot=(0, math.pi / 2, 0), n=20)
    kit.box("fanstand", (0.5, 0.9, 0.5), (4.2, -5.0, 0.25), M["steel_dark"], L, bevel=0.04)


def build_kitchen(kit, ctx, M):
    K = ctx["K"]
    kit.box("k_floor", (5.0, 4.4, 0.1), (0, 0, -0.05), M["k_floor"], K)
    kit.box("k_ceil", (5.0, 4.4, 0.1), (0, 0, 2.65), M["k_wall"], K)
    kit.box("k_wallN", (5.0, 0.1, 2.6), (0, 2.2, 1.3), M["k_wall"], K)
    kit.box("k_wallE", (0.1, 4.4, 2.6), (2.5, 0, 1.3), M["k_wall"], K)
    kit.box("k_wallW", (0.1, 4.4, 2.6), (-2.5, 0, 1.3), M["k_wall"], K)
    # the south wall has a door at x = 1.5 (an opening 1.0 wide, 2.1 high) onto a bright morning
    kit.box("k_wallS1", (3.5, 0.1, 2.6), (-0.75, -2.2, 1.3), M["k_wall"], K)
    kit.box("k_wallS2", (1.0, 0.1, 2.6), (2.0, -2.2, 1.3), M["k_wall"], K)
    kit.box("k_wallS3", (1.0, 0.1, 0.5), (1.5, -2.2, 2.35), M["k_wall"], K)
    kit.box("k_doorfL", (0.08, 0.16, 2.1), (0.96, -2.2, 1.05), M["k_wood"], K)
    kit.box("k_doorfR", (0.08, 0.16, 2.1), (2.04, -2.2, 1.05), M["k_wood"], K)
    kit.box("k_doorfT", (1.16, 0.16, 0.08), (1.5, -2.2, 2.12), M["k_wood"], K)
    kit.box("k_doorleaf", (0.9, 0.06, 2.05), (0.5, -2.62, 1.03), M["k_door"], K, rot=(0, 0, math.radians(-90)))
    kit.box("k_outside", (6.0, 0.05, 3.2), (1.5, -3.6, 1.6), M["outside"], K)
    kit.box("k_step", (1.2, 0.5, 0.12), (1.5, -2.5, 0.0), M["stone"], K)
    kit.box("k_window", (1.1, 0.04, 0.9), (0.0, 2.14, 1.5), M["k_window"], K)
    kit.box("k_frame", (1.2, 0.05, 0.05), (0.0, 2.13, 1.97), M["k_wood"], K)
    kit.box("k_frameb", (1.2, 0.05, 0.05), (0.0, 2.13, 1.03), M["k_wood"], K)
    kit.box("k_framel", (0.05, 0.05, 0.98), (-0.575, 2.13, 1.5), M["k_wood"], K)
    kit.box("k_framer", (0.05, 0.05, 0.98), (0.575, 2.13, 1.5), M["k_wood"], K)
    kit.box("k_farm1", (0.5, 0.02, 0.16), (-0.25, 2.115, 1.18), M["k_win_dark"], K, bevel=0.005)
    kit.box("k_farm2", (0.12, 0.02, 0.24), (0.3, 2.115, 1.2), M["k_win_dark"], K, bevel=0.005)
    kit.box("k_table", (0.9, 1.4, 0.06), (0, 0, 0.75), M["k_wood"], K, bevel=0.015)
    for sx in (-1, 1):
        for sy in (-1, 1):
            kit.box(f"k_leg{sx}{sy}", (0.07, 0.07, 0.72), (sx * 0.4, sy * 0.62, 0.36), M["k_wood"], K)
    for i, sx in enumerate((-1, 1)):
        kit.cyl(f"k_mug{i}", 0.05, 0.1, (sx * 0.22, 0.1 - 0.2 * sx, 0.83), M["k_mug"], K, n=16)
        kit.cyl(f"k_tea{i}", 0.045, 0.01, (sx * 0.22, 0.1 - 0.2 * sx, 0.875), M["tea"], K, n=16)
    kit.cyl("k_cord", 0.008, 0.7, (0, 0, 2.3), M["steel_dark"], K, n=6)
    kit.sphere("k_bulb", 0.06, (0, 0, 1.92), M["k_lamp"], K, seg=10)
    kit.box("k_shelf", (1.4, 0.25, 0.04), (-1.5, 2.05, 1.5), M["k_wood"], K)
    kit.box("k_cup2", (0.12, 0.12, 0.14), (-1.5, 2.0, 1.59), M["k_mug"], K, bevel=0.02)


def build_montage(kit, ctx, M):
    # --- the field gate (the newlyweds): meadow, hedge behind, a five-bar gate between two posts
    Z = kit.empty("Zgate", tuple(ZONES["gate"]))
    kit.box("g_grass", (40, 40, 0.2), (0, 0, -0.1), M["grass"], Z)
    kit.box("g_hedgeL", (14, 1.4, 1.7), (-8.5, 3.0, 0.85), M["hedge"], Z, bevel=0.25)
    kit.box("g_hedgeR", (14, 1.4, 1.7), (8.5, 3.0, 0.85), M["hedge"], Z, bevel=0.25)
    for sx in (-1, 1):
        kit.box(f"g_post{sx}", (0.2, 0.2, 1.6), (sx * 1.4, 3.0, 0.8), M["gate_wood"], Z, bevel=0.03)
    for k in range(4):
        kit.box(f"g_bar{k}", (2.6, 0.07, 0.11), (0, 2.96, 0.35 + k * 0.3), M["gate_wood"], Z, bevel=0.015)
    kit.box("g_diag", (0.08, 0.06, 1.3), (0.0, 2.93, 0.75), M["gate_wood"], Z, rot=(0, math.radians(58), 0), bevel=0.015)
    for k in range(10):
        a = kit.hash01(k, 2) * 2 * math.pi
        kit.box(f"g_tree{k}", (0.5, 0.5, 2.0 + 3 * kit.hash01(k, 3)), (-16 + 3.6 * k, 9 + 4 * kit.hash01(k, 5), 1.5),
                M["leaf"], Z, bevel=0.2)
    # --- the lane by a dry-stone wall (the grandad): the wall runs along x at y = 1.2
    Z = kit.empty("Zlane", tuple(ZONES["lane"]))
    kit.box("l_ground", (60, 12, 0.2), (0, 0, -0.1), M["lane"], Z)
    kit.box("l_grassB", (60, 16, 0.2), (0, 10, -0.095), M["grass"], Z)
    for k in range(40):
        h = 0.95 + 0.12 * kit.hash01(k, 1)
        kit.box(f"l_stone{k}", (1.6, 0.55, h), (-30 + 1.5 * k, 1.2, h / 2), M["stone"] if k % 2 else M["stone2"], Z, bevel=0.08)
    for k in range(40):
        kit.box(f"l_cap{k}", (0.7, 0.62, 0.22), (-30 + 1.5 * k + 0.35, 1.2, 1.05 + 0.1 * kit.hash01(k, 4)),
                M["stone2"] if k % 2 else M["stone"], Z, bevel=0.06)
    for k in range(8):
        kit.box(f"l_tree{k}", (0.6, 0.6, 5 + 2 * kit.hash01(k, 8)), (-24 + 7 * k, 6.5 + 3 * kit.hash01(k, 6), 3), M["leaf"], Z,
                bevel=0.3)
    # --- the inside of Rosa's trailer: the back wall (y = 1.35) covered in identical balloon badges
    Z = kit.empty("Ztrailer", tuple(ZONES["trailer"]))
    ctx["T"] = Z
    kit.box("t_floor", (2.3, 3.8, 0.1), (0, -0.55, -0.05), M["t_floor"], Z)
    kit.box("t_ceil", (2.3, 3.8, 0.1), (0, -0.55, 2.55), M["t_wall"], Z)
    kit.box("t_wallB", (2.3, 0.1, 2.6), (0, 1.4, 1.25), M["t_wall"], Z)
    for sx in (-1, 1):
        kit.box(f"t_wallS{sx}", (0.1, 3.8, 2.6), (sx * 1.2, -0.55, 1.25), M["t_wall"], Z)
    kit.box("t_wallF", (2.3, 0.1, 2.6), (0, -2.5, 1.25), M["t_wall"], Z)
    kit.cyl("t_cord", 0.008, 0.5, (0, 0.0, 2.3), M["steel_dark"], Z, n=6)
    kit.sphere("t_bulb", 0.07, (0, 0.0, 2.02), M["t_lamp"], Z, seg=10)
    cs = []
    for j in range(16):
        for i in range(13):
            if (i, j) == (12, 7):          # the empty cell where today's badge goes
                continue
            cs.append((-0.9 + i * 0.15, 0.17 + j * 0.15))
    yb = 1.35 - 0.012                      # each layer 1 cm proud of the one below, so nothing shares a plane
    disc_mesh(kit, "badges_g", cs, 0.062, yb, M["b_green"], Z)
    disc_mesh(kit, "badges_c", cs, 0.046, yb - 0.012, M["b_cream"], Z)
    disc_mesh(kit, "badges_b", [(x, z + 0.01) for x, z in cs], 0.02, yb - 0.024, M["b_green"], Z, n=10)
    new = [(0.9, 0.17 + 7 * 0.15)]
    ctx["badge_new"] = [disc_mesh(kit, "badge_ng", new, 0.062, yb, M["b_green"], Z),
                        disc_mesh(kit, "badge_nc", new, 0.046, yb - 0.012, M["b_cream"], Z),
                        disc_mesh(kit, "badge_nb", [(0.9, new[0][1] + 0.01)], 0.02, yb - 0.024, M["b_green"], Z, n=10)]


def build(kit, story, tl):
    ctx = {"env_glow": [], "fade": []}
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
    build_landscape(kit, ctx, M)
    build_kitchen(kit, ctx, M)
    build_montage(kit, ctx, M)
    sun = ctx["SUN"]
    disc = kit.cyl("sundisc", 10.0, 0.5, (0, 0, 0), M["sunmat"], sun, n=40, rot=(math.pi / 2, 0, 0))
    ctx["sundisc"] = disc
    kit.light("sun", "SUN", (0, 0, 0), 1.0, "#ffd9a0", size=0.2, parent=sun)
    kit.LIGHTS["sun"]["light"].angle = math.radians(2.5)
    kit.light("flame", "POINT", (0, 0, BURN_Z + 0.55), 380.0, ORANGE, size=0.25, parent=ctx["V"])
    kit.light("pilot", "POINT", (0.3, 0, BURN_Z + 0.1), 5.0, ORANGE, size=0.05, parent=ctx["V"], shadow=False)
    kit.light("lamp", "POINT", (-4.6, -3.55, 3.2), 520.0, "#ffe0b0", size=0.2, parent=ctx["L"])
    kit.light("fkey", "AREA", (0, 0, 2), 40.0, "#ffe6cc", size=1.0, shadow=False)
    kit.light("dsun", "SUN", (0, 0, 20), 0.0, "#ffb690", size=0.2)
    kit.LIGHTS["dsun"]["light"].angle = math.radians(4.0)
    ed = math.radians(7.0)
    kit.LIGHTS["dsun"]["obj"].rotation_euler = (V((-math.cos(ed), 0.25, -math.sin(ed)))).to_track_quat("-Z", "Y").to_euler()
    kit.light("klamp", "POINT", (0, 0, 1.85), 0.0, "#ffd29a", size=0.1, parent=ctx["K"])
    kit.light("kfill", "AREA", (0, -1.6, 2.1), 0.0, "#ffe0b8", size=2.5, parent=ctx["K"], shadow=False)
    kit.light("tlamp", "POINT", (0, 0.2, 1.9), 0.0, "#ffd29a", size=0.1, parent=ctx["T"])
    kit.light("tfill", "AREA", (0, -1.2, 2.2), 0.0, "#ffe0b8", size=2.5, parent=ctx["T"], shadow=False)
    for nm in ("fkey", "kfill", "tfill"):
        kit.LIGHTS[nm]["obj"].visible_camera = False
    d = kit.FOG["density"]
    fc = tuple(kit.FOG["color"])
    ctx["fog_cols"] = [nd for m in bpy.data.materials if m.node_tree for nd in m.node_tree.nodes
                       if nd.type == "EMISSION" and all(abs(a - b) < 1e-6 for a, b in
                                                         zip(nd.inputs["Color"].default_value[:3], fc))]
    ctx["init"] = False
    return ctx


# ------------------------------------------------------------------------------------------------ animate


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
    from blocky import rig as R

    over = {}
    if not ctx["init"]:
        for name in story["cast"]:
            ob = bpy.data.objects.get(name)
            if ob is not None and name in ("me", "dad", "rosa"):
                ob.parent = ctx["V"]
        ctx["init"] = True
    cam_loc, cam_tgt, spec = cam_now(story, tl, t)
    room = spec.get("room", "")
    basket_frame = spec.get("frame", "basket") == "basket"
    d = _ease_value(_cues(tl, "dawn"), "v", t, 0.0)
    (_, hor, zen, fog, mistc, suncol, sunp, sunel, skys, mglow) = day(d)
    rm = ctx["sky_ramp"].color_ramp
    rm.elements[0].color = (*_lin(hor), 1)
    rm.elements[1].color = (*_lin(zen), 1)
    ctx["sky_bg"].inputs["Strength"].default_value = skys * spec.get("amb", 1.0)
    roar = roar_at(tl, t)
    fogc = tuple(fog[i] * (1 - 0.4 * roar) + _hex("#f4cabe")[i] * 0.4 * roar for i in range(3))
    for nd in ctx["fog_cols"]:
        nd.inputs["Color"].default_value = (*_lin(fogc), 1)
    sock_color(ctx["mist_col"], mistc)
    ctx["V"].matrix_basis = Matrix.Identity(4)
    up = _ease_value(_cues(tl, "env"), "up", t, 1.0)
    ang = math.radians(-88.0 * (1 - up))
    ctx["E"].matrix_basis = Matrix.Translation(PIVOT) @ Matrix.Rotation(ang, 4, "X")
    ctx["flames"].rotation_euler = (ang, 0, 0)
    alt = _ease_value(_cues(tl, "alt"), "alt", t, 0.0)
    fld = _switch(_cues(tl, "field"), "f", t, 0)
    shift = -LAND_SHIFT if fld else V((0, 0, 0))
    ctx["L"].matrix_basis = Matrix.Translation(V((shift.x, shift.y, GROUND - alt)))
    mh = -0.45 + 0.9 * _ss(alt / 2.5) + 2.95 * _ss((alt - 2.0) / 10.0)     # no mist over the field, it rises as we do
    ctx["mist"].location.z = mh
    el = math.radians(sunel)
    sun = ctx["SUN"]
    sun.matrix_basis = Matrix.Translation(PIVOT)
    dist = 420.0
    ctx["sundisc"].location = (dist * math.cos(el), 0.0, dist * math.sin(el))
    ctx["sundisc"].rotation_euler = (math.pi / 2, 0, math.pi / 2)
    ctx["sundisc"].hide_render = sunel < -0.5
    sl = K.LIGHTS["sun"]["obj"]
    sl.location = (dist * math.cos(el), 0.0, dist * math.sin(el))
    sl.rotation_euler = (V((-math.cos(el), 0, -math.sin(el)))).to_track_quat("-Z", "Y").to_euler()
    indoors = room in ("kitchen", "trailer")
    K.LIGHTS["sun"]["base"] = (sunp * _ss((sunel + 3.0) / 4.0)) if not indoors else 0.0
    K.LIGHTS["sun"]["light"].color = _lin(suncol)
    ctx["sky_map"].inputs["Rotation"].default_value = (0, 0, 0)
    ctx["mist_emit"].default_value = mglow * 0.55 + 0.5 * roar
    sock_color(ctx["mist_emit_col"], mistc)
    u = min(1.0, roar * 1.3)
    oc = tuple(mistc[i] * (1 - u) + _hex("#ffd2c4")[i] * u for i in range(3))
    ctx["mist_emit_col"].default_value = (*_lin(oc), 1)
    for s in ctx["env_glow"]:
        s.default_value = 1.35 * roar
    for ob, h in ctx["flame_parts"]:
        ob.scale = (1.0, 1.0, max(0.001, roar))
        ob.location.z = h * max(0.001, roar) / 2
        ob.hide_render = roar < 0.015
    over["flame"] = roar
    over["pilot"] = 1.0
    over["lamp"] = 1.0 - _ss((alt - 3.0) / 14.0)
    over["klamp"] = over["kfill"] = over["tlamp"] = over["tfill"] = 0.0
    if room == "kitchen":
        K.LIGHTS["klamp"]["base"] = 70.0
        K.LIGHTS["kfill"]["base"] = 34.0
        over["klamp"] = over["kfill"] = 1.0
    if room == "trailer":
        K.LIGHTS["tlamp"]["base"] = 60.0
        K.LIGHTS["tfill"]["base"] = 36.0
        over["tlamp"] = over["tfill"] = 1.0
    # ---- the pink dawn sun for the hook and the next dawn, the badge, the seams
    K.LIGHTS["dsun"]["base"] = spec.get("dsun", 0.0)
    over["dsun"] = 1.0
    bn = _switch(_cues(tl, "badge"), "on", t, False)
    for ob in ctx["badge_new"]:
        ob.hide_render = not bn
    # ---- the seams
    for name, ch in R.CHARS.items():
        if not ch.sm:
            continue
        cs = [c for c in _cues(tl, "seam") if c.get("who") == name]
        base = ch.spec.get("seam", 0.5)
        g = _ease_value(cs, "gap", t, base)
        amp = _switch([c for c in _cues(tl, "rattle") if c.get("who") == name], "amp", t, 0.0)
        if amp:
            g = max(0.3, g + amp * math.sin(2 * math.pi * 7.5 * t))
        ch.set_seams(g, _ease_value(cs, "body", t, base), _ease_value(cs, "head", t, base), _ease_value(cs, "hand", t, base))
    # ---- the cables from the frame to the mouth ring
    posts = [V((1.2, 0, 2.42)), V((-1.2, 0, 2.42))]
    ringp = [V((1.25, 0.4, 0)), V((1.25, -0.4, 0)), V((-1.25, 0.4, 0)), V((-1.25, -0.4, 0))]
    Em = Matrix.Translation(PIVOT) @ Matrix.Rotation(ang, 4, "X")
    for i, cb in enumerate(ctx["cables"]):
        stretch(cb, posts[0 if i < 2 else 1], Em @ ringp[i])
        cb.hide_render = up < 0.02
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
        if indoors:
            over["fkey"] = 0.6
    return over
