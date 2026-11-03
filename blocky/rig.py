"""R6-style blocky characters, built by us (bpy venv). The style is the owner's reference (note 18): a box torso
2 x 2 x 1, arms and legs 1 x 2 x 1, and a soft rounded-cylinder head with a drawn face (faces.py). Hair, hats
and clothes are blocks and procedural patterns made here. No game assets, meshes, faces or decals.

A character spec (in a story's `cast`):
    {"skin": "#f1c9a0", "shirt": "#3d6ea6", "pattern": "plaid|knit|stripes|solid", "pattern_c": "#..",
     "pants": "#..", "shoes": "#..", "sleeves": "short|long", "collar": "#.." or null,
     "hair": "none|cap|spiky|swoop|long|bun|buzz", "hair_c": "#..", "fringe": "hard" (a swoop swept harder),
     "hat": "none|fedora|beanie|ballcap|hood|tophat|bucket", "hat_c": "#..",
     "extras": ["glasses", "backpack", "scarf", "tie", "apron", "coat", "hooddown"], "extra_c": "#..",
     "zip_c": "#.." (the coat's zip),
     "face": {"eyes": "round|dot|tired|lashes|button|hollow", "brows": true, "glow": null, ...},
     "height": 1.0, "width": 1.0, "body_width": 1.0, "age": "adult|teen"}
`body_width` (opt-in, default 1.0) narrows only the torso, arms and legs and leaves the head as it is, for a set
where two people have to sit side by side without their arms meeting (ep20's photo booth).

The rig's units: the torso is 2 wide. `S` scales a unit to metres, so a default character is about 1.75 m.
Front is -y. Pivots: hips at z = 2, shoulders at z = 3.75, neck at z = 4.
"""

from __future__ import annotations

import math

import bpy

from blocky import faces, kit

S = 0.34  # metres per rig unit


def _knit(m, c1, c2):
    """A knitted look: tight vertical ribs of two shades (wave texture), like the reference's sweaters."""
    nt = m.node_tree
    b = nt.nodes["Principled BSDF"]
    tc = nt.nodes.new("ShaderNodeTexCoord")
    wv = nt.nodes.new("ShaderNodeTexWave")
    wv.wave_type = "BANDS"
    wv.bands_direction = "X"
    wv.inputs["Scale"].default_value = 14.0
    wv.inputs["Distortion"].default_value = 3.0
    wv.inputs["Detail"].default_value = 1.0
    nt.links.new(tc.outputs["Object"], wv.inputs["Vector"])
    ramp = nt.nodes.new("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].color = kit.col(c2)
    ramp.color_ramp.elements[1].color = kit.col(c1)
    ramp.color_ramp.elements[0].position = 0.3
    ramp.color_ramp.elements[1].position = 0.7
    nt.links.new(wv.outputs["Fac"], ramp.inputs["Fac"])
    nt.links.new(ramp.outputs["Color"], b.inputs["Base Color"])


def _plaid(m, c1, c2, scale):
    nt = m.node_tree
    b = nt.nodes["Principled BSDF"]
    tc = nt.nodes.new("ShaderNodeTexCoord")
    sep = nt.nodes.new("ShaderNodeSeparateXYZ")
    nt.links.new(tc.outputs["Object"], sep.inputs[0])
    bands = []
    for axis in ("X", "Z"):
        mul = nt.nodes.new("ShaderNodeMath")
        mul.operation = "MULTIPLY"
        mul.inputs[1].default_value = scale
        nt.links.new(sep.outputs[axis], mul.inputs[0])
        fr = nt.nodes.new("ShaderNodeMath")
        fr.operation = "FRACT"
        nt.links.new(mul.outputs[0], fr.inputs[0])
        lt = nt.nodes.new("ShaderNodeMath")
        lt.operation = "LESS_THAN"
        lt.inputs[1].default_value = 0.42
        nt.links.new(fr.outputs[0], lt.inputs[0])
        bands.append(lt)
    add = nt.nodes.new("ShaderNodeMath")
    add.operation = "ADD"
    nt.links.new(bands[0].outputs[0], add.inputs[0])
    nt.links.new(bands[1].outputs[0], add.inputs[1])
    mx = nt.nodes.new("ShaderNodeMath")
    mx.operation = "MULTIPLY"
    mx.inputs[1].default_value = 0.5
    nt.links.new(add.outputs[0], mx.inputs[0])
    ramp = nt.nodes.new("ShaderNodeValToRGB")
    ramp.color_ramp.interpolation = "CONSTANT"
    c = kit.col(c1)
    ramp.color_ramp.elements[0].color = c
    ramp.color_ramp.elements[1].position = 0.4
    ramp.color_ramp.elements[1].color = tuple(v * 0.75 for v in kit.col(c2)[:3]) + (1,)
    e = ramp.color_ramp.elements.new(0.9)
    e.color = kit.col(c2)
    nt.links.new(mx.outputs[0], ramp.inputs["Fac"])
    nt.links.new(ramp.outputs["Color"], b.inputs["Base Color"])


def _stripes(m, c1, c2, scale):
    nt = m.node_tree
    b = nt.nodes["Principled BSDF"]
    tc = nt.nodes.new("ShaderNodeTexCoord")
    sep = nt.nodes.new("ShaderNodeSeparateXYZ")
    nt.links.new(tc.outputs["Object"], sep.inputs[0])
    mul = nt.nodes.new("ShaderNodeMath")
    mul.operation = "MULTIPLY"
    mul.inputs[1].default_value = scale
    nt.links.new(sep.outputs["Z"], mul.inputs[0])
    fr = nt.nodes.new("ShaderNodeMath")
    fr.operation = "FRACT"
    nt.links.new(mul.outputs[0], fr.inputs[0])
    ramp = nt.nodes.new("ShaderNodeValToRGB")
    ramp.color_ramp.interpolation = "CONSTANT"
    ramp.color_ramp.elements[0].color = kit.col(c1)
    ramp.color_ramp.elements[1].position = 0.5
    ramp.color_ramp.elements[1].color = kit.col(c2)
    nt.links.new(fr.outputs[0], ramp.inputs["Fac"])
    nt.links.new(ramp.outputs["Color"], b.inputs["Base Color"])


def cloth(spec, key):
    """The shirt's material, with its pattern (plaid, knit, stripes or solid)."""
    base, pat = spec[key], spec.get("pattern", "solid") if key == "shirt" else spec.get("pants_pattern", "solid")
    pc = spec.get("pattern_c", "#202020") if key == "shirt" else spec.get("pants_pattern_c", "#202020")
    name = f"cloth {base} {pat} {pc}"
    if name in kit.MATS:
        return kit.MATS[name]
    m = kit._new(name)
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = kit.col(base)
    b.inputs["Roughness"].default_value = 0.8
    if pat == "plaid":
        _plaid(m, base, pc, 1.5)
    elif pat == "knit":
        _knit(m, base, pc)
    elif pat == "stripes":
        _stripes(m, base, pc, 1.25)
    kit._fogged(m, b.outputs[0])
    return m


def head_mesh(name, mat, parent):
    """A soft rounded cylinder (vertical axis) with UVs: u once around (u = 0.5 at the front, -y), v up."""
    R, H, b = faces.HEAD_R, faces.HEAD_H, 0.16
    n, arc = 48, 5
    prof = [(0.0, 0.0)]
    for k in range(arc + 1):  # bottom rounded edge
        a = -math.pi / 2 + (math.pi / 2) * k / arc
        prof.append((R - b + b * math.cos(a), b + b * math.sin(a)))
    for k in range(arc + 1):  # top rounded edge
        a = (math.pi / 2) * k / arc
        prof.append((R - b + b * math.cos(a), H - b + b * math.sin(a)))
    prof.append((0.0, H))
    verts, uvs = [], []
    for j in range(n + 1):
        th = 2 * math.pi * j / n
        # u = 0.5 faces -y: angle measured so that j = n/2 points at -y
        ang = th - math.pi / 2 - math.pi
        for r, z in prof:
            verts.append((r * math.cos(ang), r * math.sin(ang), z - H / 2))
            uvs.append((j / n, min(1.0, max(0.0, (z - b * 0.5) / (H - b)))))
    m = len(prof)
    fcs = []
    for j in range(n):
        for i in range(m - 1):
            a, c = j * m + i, (j + 1) * m + i
            fcs.append((a, c, c + 1, a + 1))
    ob = kit.mesh_obj(name, verts, fcs, mat, parent, smooth=True)
    uv = ob.data.uv_layers.new(name="UVMap")
    for poly in ob.data.polygons:
        for li in poly.loop_indices:
            uv.data[li].uv = uvs[ob.data.loops[li].vertex_index]
    return ob


def head_material(name, skin):
    """Skin with the face texture on top; the rig swaps the image as the expression changes."""
    m = kit._new(f"head {name}")
    nt = m.node_tree
    b = nt.nodes["Principled BSDF"]
    b.inputs["Roughness"].default_value = 0.5
    tex = nt.nodes.new("ShaderNodeTexImage")
    tex.interpolation = "Linear"
    uvn = nt.nodes.new("ShaderNodeUVMap")
    nt.links.new(uvn.outputs["UV"], tex.inputs["Vector"])
    nt.links.new(tex.outputs["Color"], b.inputs["Base Color"])
    kit._fogged(m, b.outputs[0])
    return m, tex


def soften(ob, width, seg=3):
    """A bevel and smooth shading on a part kit doesn't bevel (the bucket hat's crown and brim)."""
    m = ob.modifiers.new("bevel", "BEVEL")
    m.width = width
    m.segments = seg
    m.limit_method = "ANGLE"
    for p in ob.data.polygons:
        p.use_smooth = True
    try:
        ob.modifiers.new("wn", "WEIGHTED_NORMAL").keep_sharp = True
    except Exception:
        pass
    return ob


def brim_mesh(name, r0, z0, r1, z1, th, mat, parent, n=48):
    """A brim sloping all the way round: a ring from radius r0 at height z0 out to r1 at z1, th thick."""
    verts, fcs = [], []
    for j in range(n):
        a = 2 * math.pi * j / n
        c, s_ = math.cos(a), math.sin(a)
        verts += [(r0 * c, r0 * s_, z0), (r1 * c, r1 * s_, z1), (r1 * c, r1 * s_, z1 - th), (r0 * c, r0 * s_, z0 - th)]
    for j in range(n):
        a, b = 4 * j, 4 * ((j + 1) % n)
        fcs += [(a, a + 1, b + 1, b),            # top, facing up
                (a + 1, a + 2, b + 2, b + 1),    # outer edge, facing out
                (a + 2, a + 3, b + 3, b + 2),    # underside, facing down
                (a + 3, a, b, b + 3)]            # inner edge, facing in
    return kit.mesh_obj(name, verts, fcs, mat, parent)


class Character:
    """One avatar. `pose()` sets every joint for a frame."""

    def __init__(self, name, spec, workdir):
        self.name, self.spec, self.workdir = name, spec, workdir
        self.face = spec.get("face", {})
        self.images: dict = {}
        sc = spec.get("height", 1.0) * S
        wd = spec.get("width", 1.0)
        self.root = kit.empty(name, (0, 0, 0))
        self.root.scale = (sc * wd, sc, sc)
        skin = kit.plastic(spec["skin"], 0.5)
        shirt = cloth(spec, "shirt")
        pants = cloth(spec, "pants") if "pants" in spec else kit.plastic("#2c3550", 0.7)
        shoes = kit.plastic(spec.get("shoes", spec.get("pants", "#222222")), 0.6)
        bev = 0.08
        bw = float(spec.get("body_width", 1.0))
        P = {"root": self.root}
        self.hips = kit.empty(f"{name}.hips", (0, 0, 2.0), self.root)
        for sx in (-1, 1):
            leg = kit.empty(f"{name}.leg{sx}", (sx * 0.5 * bw, 0, 2.0), self.root)
            kit.box(f"{name}.legm{sx}", (0.98 * bw, 1.0, 1.72), (0, 0, -0.86), pants, leg, bevel=bev)
            kit.box(f"{name}.shoe{sx}", (0.99 * bw, 1.01, 0.3), (0, 0, -1.85), shoes, leg, bevel=bev)
            P[f"leg{sx}"] = leg
        self.torso = kit.empty(f"{name}.torso", (0, 0, 2.0), self.root)
        kit.box(f"{name}.torsom", (2.0 * bw, 1.0, 2.0), (0, 0, 1.0), shirt, self.torso, bevel=bev)
        if spec.get("collar"):
            cm = kit.plastic(spec["collar"], 0.6)
            kit.box(f"{name}.collar", (1.2 * bw, 1.04, 0.22), (0, 0, 1.93), cm, self.torso, bevel=0.06)
        sleeve = {"short": 0.7, "long": 1.75, "none": 0.0}[spec.get("sleeves", "long")]
        for sx in (-1, 1):
            arm = kit.empty(f"{name}.arm{sx}", (sx * 1.5 * bw, 0, 1.75), self.torso)
            if sleeve > 0:
                kit.box(f"{name}.sleeve{sx}", (0.98 * bw, 1.0, sleeve), (0, 0, 0.25 - sleeve / 2), shirt, arm, bevel=bev)
            kit.box(f"{name}.skinarm{sx}", (0.96 * bw, 0.98, 2.0 - sleeve), (0, 0, 0.25 - sleeve - (2.0 - sleeve) / 2),
                    skin, arm, bevel=bev)
            P[f"arm{sx}"] = arm
        ex = spec.get("extras", [])
        self.coat = []
        if "coat" in ex:
            # a coat to mid-thigh (ep14): two skirt panels hinged at the hips like the legs, so each swings with its
            # own leg and a stride never pokes through, meeting at the front; a zip down the middle of the front
            for sx in (-1, 1):
                hinge = kit.empty(f"{name}.coat{sx}", (sx * 0.5, 0, 2.0), self.root)
                kit.box(f"{name}.coatm{sx}", (1.0, 1.08, 0.78), (sx * 0.005, 0, -0.33), shirt, hinge, bevel=bev)
                self.coat.append((hinge, sx))
            zc = kit.plastic(spec.get("zip_c", "#2a2a2e"), 0.4)
            kit.box(f"{name}.zip", (0.07, 0.03, 1.76), (0, -0.505, 0.9), zc, self.torso, bevel=0.012)   # under the collar
        if "hooddown" in ex:   # a hood lying down behind the collar, in the coat's colour (ep14)
            kit.box(f"{name}.hooddown", (1.56, 0.5, 0.44), (0, 0.66, 1.98), shirt, self.torso, bevel=0.18)
        self.neck = kit.empty(f"{name}.neck", (0, 0, 2.0), self.torso)
        self.head = kit.empty(f"{name}.head", (0, 0, 0), self.neck)
        self.head_mat, self.face_tex = head_material(name, spec["skin"])
        headg = kit.empty(f"{name}.headg", (0, 0, faces.HEAD_H / 2 + 0.02), self.head)
        head_mesh(f"{name}.headm", self.head_mat, headg)
        self._accessories(headg, spec)
        self.P = P
        self.state = {}
        self.set_face("neutral", 0.0, (0, 0), 0.0)

    def _accessories(self, hg, spec):
        n, R, H = self.name, faces.HEAD_R, faces.HEAD_H
        top = H / 2
        hair = kit.plastic(spec.get("hair_c", "#2a1d15"), 0.65)
        style = spec.get("hair", "cap")
        if style in ("cap", "long", "bun", "swoop", "spiky") and spec.get("hat") == "bucket":
            # under a bucket hat (ep14) the crown covers the top, and the back and sides stop under the brim, so no
            # block corner pokes through it
            cut = top - 0.17
            hb0 = top - H * 0.36 - H * 0.375
            kit.box(f"{n}.hback", (2 * R + 0.08, 0.32, cut - hb0), (0, R - 0.08, (cut + hb0) / 2), hair, hg, bevel=0.1)
            for sx in (-1, 1):
                kit.box(f"{n}.hside{sx}", (0.2, 0.9, cut - (top - 0.5)), (sx * (R - 0.02), 0.2, (cut + top - 0.5) / 2),
                        hair, hg, bevel=0.08)
        elif style in ("cap", "long", "bun", "swoop", "spiky"):
            kit.box(f"{n}.hcap", (2 * R + 0.08, 2 * R + 0.08, 0.3), (0, 0.02, top - 0.05), hair, hg, bevel=0.12)
            if "backscarf" in spec.get("extras", []):   # opt-in (ep22): hair right down the back of the head, so a back reads
                kit.box(f"{n}.hback", (2 * R + 0.08, 0.32, H * 0.98), (0, R - 0.08, 0.0), hair, hg, bevel=0.1)
            else:
                kit.box(f"{n}.hback", (2 * R + 0.08, 0.32, H * 0.75), (0, R - 0.08, top - H * 0.36), hair, hg, bevel=0.1)
            for sx in (-1, 1):
                kit.box(f"{n}.hside{sx}", (0.2, 0.9, 0.5), (sx * (R - 0.02), 0.2, top - 0.25), hair, hg, bevel=0.08)
        if style == "swoop":  # a big fringe swept across the brow, like the reference's ginger boy
            kit.box(f"{n}.fringe", (2 * R + 0.06, 0.5, 0.34), (0.05, -R + 0.2, top - 0.12), hair, hg,
                    rot=(0.0, 0.12, 0.0), bevel=0.12)
            kit.box(f"{n}.fringe2", (0.9, 0.5, 0.3), (-0.3, -R + 0.25, top - 0.22), hair, hg, rot=(0, 0.35, 0), bevel=0.1)
            if spec.get("fringe") == "hard":
                # swept hard to the character's right (-x, the rig's "left"): a long lock from the crown down over the
                # right brow, stopping above the eye, so which way the fringe goes reads at phone size (ep14)
                kit.box(f"{n}.fringe3", (0.82, 0.34, 0.28), (-0.27, -R + 0.13, top - 0.13), hair, hg,
                        rot=(0.0, -0.42, 0.0), bevel=0.1)
        if style == "spiky":
            for k in range(9):
                a = -math.pi * 0.9 + k * math.pi * 1.8 / 8
                x, y = 0.55 * math.cos(a + math.pi / 2), -0.55 * math.sin(a + math.pi / 2) * 0.9
                kit.box(f"{n}.spk{k}", (0.22, 0.22, 0.7), (x, y, top + 0.12), hair, hg,
                        rot=(-y * 1.1, x * 1.1, a * 0.2), bevel=0.04)
            kit.box(f"{n}.spkf", (1.0, 0.25, 0.3), (0.0, -R + 0.08, top - 0.15), hair, hg, rot=(0.0, 0.2, 0.0), bevel=0.06)
        if style == "long":
            kit.box(f"{n}.hlong", (2 * R + 0.12, 0.4, H * 1.3), (0, R - 0.1, top - H * 0.65), hair, hg, bevel=0.12)
            for sx in (-1, 1):
                kit.box(f"{n}.hlongs{sx}", (0.24, 0.8, H * 1.15), (sx * (R + 0.02), 0.1, top - H * 0.6), hair, hg, bevel=0.1)
        if style == "bun":
            kit.box(f"{n}.bun", (0.5, 0.5, 0.45), (0, 0.15, top + 0.3), hair, hg, bevel=0.18)
        if style == "buzz":
            kit.box(f"{n}.buzz", (2 * R + 0.03, 2 * R + 0.03, 0.12), (0, 0.0, top - 0.02), hair, hg, bevel=0.05)
        hat, hc = spec.get("hat", "none"), kit.plastic(spec.get("hat_c", "#333333"), 0.6)
        if hat == "fedora":
            kit.cyl(f"{n}.brim", R + 0.42, 0.07, (0, 0, top + 0.06), hc, hg, n=32)
            kit.cyl(f"{n}.crown", R + 0.05, 0.55, (0, 0, top + 0.34), hc, hg, n=32, r2=R - 0.05)
            kit.cyl(f"{n}.band", R + 0.06, 0.12, (0, 0, top + 0.15), kit.plastic(spec.get("band_c", "#151515"), 0.5),
                    hg, n=32)
        elif hat == "beanie":
            kit.box(f"{n}.beanie", (2 * R + 0.14, 2 * R + 0.14, 0.62), (0, 0.0, top + 0.08), hc, hg, bevel=0.2)
            kit.box(f"{n}.beanief", (2 * R + 0.18, 2 * R + 0.18, 0.2), (0, 0.0, top - 0.15), hc, hg, bevel=0.06)
        elif hat == "ballcap":
            kit.box(f"{n}.capc", (2 * R + 0.12, 2 * R + 0.12, 0.42), (0, 0.0, top + 0.08), hc, hg, bevel=0.18)
            kit.box(f"{n}.capb", (2 * R * 0.8, 0.6, 0.07), (0, -R - 0.22, top - 0.08), hc, hg, bevel=0.03)
        elif hat == "tophat":
            kit.cyl(f"{n}.tbrim", R + 0.3, 0.07, (0, 0, top + 0.06), hc, hg, n=32)
            kit.cyl(f"{n}.tcrown", R, 0.95, (0, 0, top + 0.55), hc, hg, n=32)
        elif hat == "bucket":
            # a bucket hat (ep14): a short round crown and a brim sloping down all the way round, plain matte cloth
            # with no band and no logo. The crown is wide enough to cover the block hair's corners under it
            bc = kit.plastic(spec.get("hat_c", "#333333"), 0.9)
            soften(kit.cyl(f"{n}.bcrown", R + 0.28, 0.46, (0, 0, top + 0.12), bc, hg, n=40, r2=R + 0.17), 0.08)
            soften(brim_mesh(f"{n}.bbrim", R + 0.24, top - 0.07, R + 0.58, top - 0.25, 0.06, bc, hg), 0.025, 2)
        elif hat == "hood":
            kit.box(f"{n}.hood", (2 * R + 0.34, 2 * R + 0.3, H + 0.3), (0, 0.12, 0.08), hc, hg, bevel=0.22)
            # the hood is open at the front: a dark recess the face sits in front of
        elif hat == "hoodopen":
            # opt-in (ep14, Floor Thirteen): a hood that is really open at the front, so the face shows from the
            # front: a back panel, two sides and a top, with a soft lip round the opening
            hw, hd, hh, hz = 2 * R + 0.34, 2 * R + 0.3, H + 0.3, 0.08
            kit.box(f"{n}.hoodb", (hw, 0.3, hh), (0, 0.12 + hd / 2 - 0.15, hz), hc, hg, bevel=0.14)
            for sx in (-1, 1):
                kit.box(f"{n}.hoods{sx}", (0.22, hd, hh), (sx * (hw / 2 - 0.11), 0.12, hz), hc, hg, bevel=0.1)
            kit.box(f"{n}.hoodt", (hw, hd, 0.24), (0, 0.12, hz + hh / 2 - 0.12), hc, hg, bevel=0.1)
            kit.box(f"{n}.hoodlip", (hw - 0.3, 0.1, 0.1), (0, 0.12 - hd / 2 + 0.03, hz + hh / 2 - 0.3), hc, hg, bevel=0.04)
        ex = spec.get("extras", [])
        ec = kit.plastic(spec.get("extra_c", "#20242c"), 0.4)
        self.hp = {"ears": [], "neck": []}
        if "headphones" in ex:
            # opt-in (ep14, Floor Thirteen): big black block over-ear headphones, in two places at once (a set's
            # animate shows one: on the ears, or round the neck). Plain black, no logo.
            hp_c = kit.plastic(spec.get("hp_c", "#0d0d10"), 0.45)
            ears = self.hp["ears"]
            ears.append(kit.box(f"{n}.hpe_band", (2 * R + 0.5, 0.22, 0.16), (0, 0.12, top + 0.46), hp_c, hg, bevel=0.06))
            for sx in (-1, 1):
                ears.append(kit.box(f"{n}.hpe_arm{sx}", (0.16, 0.2, 0.9), (sx * (R + 0.34), 0.12, top + 0.02), hp_c, hg,
                                    bevel=0.05))
                ears.append(kit.box(f"{n}.hpe_cup{sx}", (0.34, 0.74, 0.82), (sx * (R + 0.4), 0.12, -0.05), hp_c, hg,
                                    bevel=0.12))
            neck = self.hp["neck"]
            neck.append(kit.box(f"{n}.hpn_back", (1.5, 0.16, 0.16), (0, 0.5, 2.0), hp_c, self.torso, bevel=0.05))
            for sx in (-1, 1):
                neck.append(kit.box(f"{n}.hpn_side{sx}", (0.16, 1.0, 0.16), (sx * 0.72, 0.0, 2.0), hp_c, self.torso,
                                    bevel=0.05))
                neck.append(kit.box(f"{n}.hpn_cup{sx}", (0.66, 0.34, 0.74), (sx * 0.72, -0.55, 1.78), hp_c, self.torso,
                                    bevel=0.12))
            for ob in neck:
                ob.hide_render = True
        if "glasses" in ex:
            gc = kit.plastic(spec["glasses_c"], 0.4) if spec.get("glasses_c") else ec   # opt-in (ep32): frames apart from extra_c
            for sx in (-1, 1):
                kit.box(f"{n}.gl{sx}", (0.42, 0.06, 0.32), (sx * 0.24, -R - 0.03, -0.02), kit.glass("#dde6ea"), hg,
                        bevel=0.04)
                kit.box(f"{n}.glf{sx}", (0.46, 0.04, 0.05), (sx * 0.24, -R - 0.05, 0.15), gc, hg)
            kit.box(f"{n}.glb", (0.1, 0.04, 0.05), (0, -R - 0.05, 0.1), gc, hg)
        if "backpack" in ex:
            kit.box(f"{n}.pack", (1.5, 0.6, 1.6), (0, 0.78, 1.05), ec, self.torso, bevel=0.15)
        if "scarf" in ex:
            kit.box(f"{n}.scarf", (2.1, 1.12, 0.36), (0, 0, 1.85), ec, self.torso, bevel=0.1)
            kit.box(f"{n}.scarft", (0.36, 0.1, 0.9), (0.45, -0.55, 1.35), ec, self.torso, bevel=0.06)
        if "backscarf" in ex:   # opt-in (ep22): a scarf tail down the back and a coat seam, so a back reads as a back
            # no tail on the back: a yellow strip down the back read as a front scarf knot
            seam = kit.plastic(spec.get("seam_c", "#33426e"), 0.5)
            kit.box(f"{n}.seam", (0.1, 0.03, 1.5), (0.1, 0.51, 0.85), seam, self.torso, bevel=0.012)
            kit.box(f"{n}.belt", (2.02, 0.05, 0.16), (0, 0.5, 0.45), seam, self.torso, bevel=0.02)
        if "tie" in ex:
            kit.box(f"{n}.tie", (0.22, 0.06, 1.1), (0, -0.52, 1.35), ec, self.torso, bevel=0.03)
        if "apron" in ex:
            kit.box(f"{n}.apron", (1.6, 0.06, 2.4), (0, -0.53, 0.8), ec, self.torso, bevel=0.03)

    # ------------------------------------------------------------------------------------------------ pose

    def set_face(self, expr, open_, look, blink):
        key = faces.face_key(self.face, self.spec["skin"], expr, open_, look, blink)
        if self.state.get("face") == key:
            return
        img = self.images.get(key)
        if img is None:
            pil = faces.face_image(self.face, self.spec["skin"], expr, open_, look, blink)
            path = self.workdir / f"face-{self.name}-{key}.png"
            if not path.exists():
                pil.save(path)
            img = bpy.data.images.load(str(path))
            img.colorspace_settings.name = "sRGB"
            self.images[key] = img
        self.face_tex.image = img
        self.state["face"] = key

    def pose(self, x, y, z, yaw, legs=0.0, arms=(0.0, 0.0), arms_side=(0.0, 0.0), head_yaw=0.0,
             head_pitch=0.0, lean=0.0, bob=0.0, expr="neutral", mouth=0.0, look=(0, 0), blink=0.0, hidden=False):
        """legs: swing angle (rad, + = left leg forward); arms: (left, right) raise angle forward (rad);
        arms_side: (left, right) out to the side; yaw: facing (rad, 0 = facing -y)."""
        r = self.root
        r.location = (x, y, z + bob)
        r.rotation_euler = (lean, 0, yaw)
        r.hide_render = hidden
        for ob in r.children_recursive:
            ob.hide_render = hidden
        self.P["leg-1"].rotation_euler = (legs, 0, 0)
        self.P["leg1"].rotation_euler = (-legs, 0, 0)
        for hinge, sx in self.coat:   # a coat's skirt panel swings with its own leg
            hinge.rotation_euler = (legs if sx < 0 else -legs, 0, 0)
        # arms swing opposite their legs when walking, on top of the pose
        self.P["arm-1"].rotation_euler = (-arms[0] - legs * 0.9, arms_side[0], 0)
        self.P["arm1"].rotation_euler = (-arms[1] + legs * 0.9, -arms_side[1], 0)
        self.neck.rotation_euler = (head_pitch, 0, head_yaw)
        self.set_face(expr, mouth, look, blink)
