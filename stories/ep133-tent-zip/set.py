"""ep133-tent-zip: the tangerine dome tent at night, the lantern, and the figure (Dev's face on a body too tall).

PHASE 1 (creature test still): the tent interior, the red door stripe, the lantern, the moon fill, `me` seated at
frame right (a rig character, posed seated in animate()) and THE FIGURE, built here from kit parts so its neck
(about 1.8x) and torso (about 1.6x) can be stretched on their own: a seated body whose head lies sideways, bent flat
against the tent roof. Dev's face is the rig's own head mesh and face texture; the beanie, vest and hoodie are boxes.
Everything is built in build(). World (metres, z up): the camera sits at the back wall (+y) looking toward -y; the
figure and I face the camera. The figure is at x +0.5 (frame left), me at x -0.6 (frame right), door flap behind me.
"""

from __future__ import annotations

import math
import tempfile
from pathlib import Path

import bpy
from mathutils import Matrix, Vector as V

from blocky import faces, rig

TMP = Path(tempfile.mkdtemp(prefix="tentzip-"))
_n = [0]

TA, TB, TC = 1.25, 2.6, 1.95          # tent half-width (x), half-depth (y), height at the middle
FX, FY = 0.12, -0.15
HC = (FX + 0.15, FY + 0.2 + 0.03, 0.06 + 0.04 + 1.65 + 0.2)      # the head's centre (see build_figure)
HDIR = (0.94, 0.0, 0.34)                                         # its top, tilted into the roof


def dent(x, y):
    """The fabric pushed out and draped over the head and beanie: the roof is what stops it."""
    best = 0.0
    for off, r in ((0.0, 0.8), (0.5, 0.65)):
        cx, cz = HC[0] + HDIR[0] * off, HC[2] + HDIR[2] * off - 0.1
        d2 = (x - cx) ** 2 + (y - HC[1]) ** 2
        if d2 < r * r:
            best = max(best, cz + math.sqrt(r * r - d2) - 0.0)
    return best


def roofd(x, y):
    z = roof(x, y)
    return max(z, dent(x, y)) if z > 0 else 0.0                 # the figure's seat (hips), world
HIP = 0.06                            # the seat height
S = 0.34                              # rig metres per unit


def nm(p):
    _n[0] += 1
    return f"{p}.{_n[0]}"


def roof(x, y):
    """The tent's roof height at (x, y): a flattened dome with steep walls."""
    ry = max(0.0, (abs(y) - 1.9) / (TB - 1.9))
    r = math.sqrt((x / TA) ** 2 + ry ** 2)
    if r >= 1:
        return 0.0
    return TC * (1 - r ** 2.4) ** 0.5


def surf(x, y):
    """A point on the roof and its inward normal (toward the inside)."""
    z = roof(x, y)
    e = 0.01
    dx = (roof(x + e, y) - roof(x - e, y)) / (2 * e)
    dy = (roof(x, y + e) - roof(x, y - e)) / (2 * e)
    n = V((dx, dy, -1)).normalized() * -1
    n = V((-dx, -dy, 1)).normalized()      # outward
    return V((x, y, z)), -n


def orient(box_z_to):
    return V((0, 0, 1)).rotation_difference(V(box_z_to).normalized()).to_euler()


def bar(kit, name, p0, p1, tx, ty, mat, parent=None, bevel=0.03):
    """A box from p0 to p1, tx by ty across."""
    a, b = V(p0), V(p1)
    d = b - a
    return kit.box(nm(name), (tx, ty, d.length), tuple((a + b) / 2), mat, parent, tuple(orient(d)), bevel)


def build(kit, story, tl):
    ctx = {}
    P = lambda c, r=0.55, s=0.35: kit.plastic(c, r, spec=s)
    sc = bpy.context.scene

    # ---- the tent shell: a heightfield dome, tangerine, seen from inside
    nx, ny = 40, 60
    verts, fcs = [], []
    for i in range(ny + 1):
        y = -TB + 2 * TB * i / ny
        for j in range(nx + 1):
            x = -TA + 2 * TA * (0.5 - 0.5 * math.cos(math.pi * j / nx))
            verts.append((x, y, roofd(x, y)))
    for i in range(ny):
        for j in range(nx):
            a_ = i * (nx + 1) + j
            fcs.append((a_, a_ + 1, a_ + nx + 2, a_ + nx + 1))
    tent_mat = P("#b8561a", 0.9, 0.02)
    try:    # the full moon outside shines blue through the fabric: emission rises with height and toward the back
        nt = tent_mat.node_tree
        bsdf = nt.nodes["Principled BSDF"]
        geo = nt.nodes.new("ShaderNodeNewGeometry")
        sep = nt.nodes.new("ShaderNodeSeparateXYZ")
        nt.links.new(geo.outputs["Position"], sep.inputs[0])
        dist = nt.nodes.new("ShaderNodeVectorMath")
        dist.operation = "DISTANCE"
        dist.inputs[1].default_value = (HC[0] + 0.1, HC[1], 1.55)
        nt.links.new(geo.outputs["Position"], dist.inputs[0])
        ramp = nt.nodes.new("ShaderNodeMapRange")
        ramp.inputs["From Min"].default_value = 0.4
        ramp.inputs["From Max"].default_value = 2.2
        ramp.inputs["To Min"].default_value = 1.05
        ramp.inputs["To Max"].default_value = 0.08
        nt.links.new(dist.outputs["Value"], ramp.inputs["Value"])
        bsdf.inputs["Emission Color"].default_value = (0.1, 0.3, 1.0, 1)
        nt.links.new(ramp.outputs["Result"], bsdf.inputs["Emission Strength"])
    except Exception as e:
        print("tent mat failed", e)
    shell = kit.mesh_obj("tentshell", verts, fcs, tent_mat, None, smooth=True)
    ctx["shell"] = shell
    # the groundsheet and the two sleeping bags
    kit.box("floor", (2 * TA, 2 * TB, 0.04), (0, 0, -0.02), P("#5b3a22", 0.9, 0.05), None, (0, 0, 0), 0.0)
    kit.box("mat1", (1.0, 1.7, 0.05), (-0.62, 0.15, 0.025), P("#3a4658", 0.9, 0.03), None, (0, 0, 0), 0.02)  # my bag, open
    kit.box("mat1b", (0.9, 0.5, 0.12), (-0.62, 0.95, 0.06), P("#323c4c", 0.9, 0.03), None, (0, 0, 0), 0.05)   # rumple
    # the rolled, tied bag the figure sits on (along x), and its straps
    kit.cyl("roll", 0.08, 0.62, (FX, FY, 0.08), P("#6a4e8a", 0.85, 0.05), None, (0, math.pi / 2, 0), n=24)
    for dx in (-0.2, 0.2):
        kit.cyl(nm("strap"), 0.088, 0.04, (FX + dx, FY, 0.08), P("#e7d9a8", 0.8, 0.05), None, (0, math.pi / 2, 0), n=24)

    # panel seams running front to back along the roof (stitched dark lines): they show the fabric is a roof
    seam = P("#3a4f86", 0.8, 0.05)
    for sx_ in (-0.85, -0.45, 0.0, 0.95):
        pts_ = [V((sx_, y_, roofd(sx_, y_) - 0.015)) for y_ in [-2.4 + 0.1 * k for k in range(49)] if roof(sx_, y_) > 0.05]
        for a_, b_ in zip(pts_, pts_[1:]):
            bar(kit, "seam", a_, b_, 0.02, 0.008, seam, bevel=0.0)

    # stress creases in the fabric, fanning out from the pressed head
    for k in range(9):
        ang_ = math.radians(-70 + k * 20)
        pts_ = []
        for rr in [0.45 + 0.08 * i for i in range(10)]:
            x_, y_ = HC[0] + 0.25 + rr * math.cos(ang_), HC[1] + rr * math.sin(ang_) * 0.8
            if roof(x_, y_) > 0.05:
                pts_.append(V((x_, y_, roofd(x_, y_) - 0.012)))
        for a_, b_ in zip(pts_, pts_[1:]):
            bar(kit, "crease", a_, b_, 0.018, 0.008, seam, bevel=0.0)

    # ---- the door flap on the right wall, with the fat red stripe across it
    dp, dn = surf(-0.35, -1.5)
    ang = math.atan2(dn.x, dn.z) if False else 0
    flap_rot = tuple(V((0, 0, 1)).rotation_difference(-dn).to_euler())
    off = -dn * 0.0
    dc = dp + (-dn) * 0.02                       # 2 cm proud of the fabric: no z-fight
    flap = kit.box("flap", (0.95, 1.25, 0.02), tuple(dc), P("#ffa247", 0.7, 0.1), None, flap_rot, 0.01)
    # stripe: slightly further proud, a fat red band across the flap (local x across)
    sp = dp + (-dn) * 0.04
    kit.box("stripe", (0.95, 0.20, 0.02), tuple(sp + V((0, 0, 0.0))), P("#e2302a", 0.6, 0.1), None, flap_rot, 0.008)
    ctx["flap"] = flap

    # ---- the lantern: steady, cream, on the floor between the bags toward the camera
    LX, LY = 0.12, 0.42
    kit.cyl("lantbase", 0.1, 0.05, (LX, LY, 0.025), P("#2c2a2e", 0.5), n=24)
    glow = kit.emit("#fff0c8", 6.0, name="lantglow")
    kit.cyl("lantern", 0.075, 0.22, (LX, LY, 0.16), glow, n=24)
    kit.cyl("lanttop", 0.09, 0.04, (LX, LY, 0.29), P("#2c2a2e", 0.5), n=24)
    kit.light("lantern", "POINT", (LX, LY - 0.02, 0.22), 90, "#ffe7b4", size=0.1)
    kit.light("lanthalo", "POINT", (LX, LY, 0.9), 3, "#ffe2a8", size=0.3, shadow=False)   # the fabric's glow
    ctx["lights_late"] = True
    # ---- the moon through the fabric: cool blue fill from above-behind, rim from behind the figure
    kit.light("moonfill", "AREA", (0.0, 0.5, 1.2), 25, "#7fa8ff", size=1.8, rot=(0, 0, 0), shadow=False)
    rim = kit.light("moonrim", "SPOT", (1.5, -0.6, 1.6), 700, "#7fa8ff", size=0.15, spot=55, blend=0.3, shadow=False)
    kit.aim(rim, (0.5, -0.15, 1.4))
    rim2 = kit.light("moonrim2", "SPOT", (-0.5, -1.0, 1.9), 700, "#7fa8ff", size=0.15, spot=55, blend=0.3, shadow=False)
    kit.aim(rim2, (0.2, -0.15, 1.4))
    rim3 = kit.light("moonrim3", "SPOT", (0.3, -1.0, 1.2), 400, "#7fa8ff", size=0.15, spot=60, blend=0.3, shadow=False)
    kit.aim(rim3, (0.3, -0.15, 1.3))

    build_figure(kit, ctx)
    return ctx


# ------------------------------------------------------------------------------------------------ the figure
def W(lx, ly, lz):
    """Figure-local (front = -y, centred on its seat) to world: the figure faces the camera (+y)."""
    return V((FX - lx, FY - ly, lz))


def tube(kit, name, pts, radii, mat, sides=14):
    """A smooth round tube along pts (the path lies roughly in one x-z plane)."""
    verts, fcs = [], []
    side = V((0, 1, 0))
    for k, p in enumerate(pts):
        a = pts[max(0, k - 1)]
        b = pts[min(len(pts) - 1, k + 1)]
        T = (b - a).normalized()
        u = T.cross(side).normalized()
        v = T.cross(u).normalized()
        for m in range(sides):
            ph = 2 * math.pi * m / sides
            verts.append(tuple(p + (u * math.cos(ph) + v * math.sin(ph)) * radii[k]))
    for k in range(len(pts) - 1):
        for m in range(sides):
            a_, b_ = k * sides + m, k * sides + (m + 1) % sides
            fcs.append((a_, b_, b_ + sides, a_ + sides))
    fcs.append(tuple(reversed(range(sides))))
    fcs.append(tuple(range((len(pts) - 1) * sides, len(pts) * sides)))
    return kit.mesh_obj(nm(name), verts, fcs, mat, None, smooth=True)


def rimify(mat, strength=40.0, blend=0.5, color=(0.30, 0.55, 1.0, 1)):
    """A hard cool-blue moon rim on a material's silhouette edges (a Layer Weight fresnel into the emission)."""
    try:
        nt = mat.node_tree
        bsdf = nt.nodes["Principled BSDF"]
        lw = nt.nodes.new("ShaderNodeLayerWeight")
        lw.inputs["Blend"].default_value = blend
        mul = nt.nodes.new("ShaderNodeMath")
        mul.operation = "MULTIPLY"
        mul.inputs[1].default_value = strength
        pw = nt.nodes.new("ShaderNodeMath")
        pw.operation = "POWER"
        pw.inputs[1].default_value = 4.0
        nt.links.new(lw.outputs["Fresnel"], pw.inputs[0])
        nt.links.new(pw.outputs[0], mul.inputs[0])
        mix = nt.nodes.new("ShaderNodeMixRGB")
        mix.blend_type = "MULTIPLY"
        mix.inputs["Fac"].default_value = 1.0
        mix.inputs["Color2"].default_value = color
        nt.links.new(mul.outputs[0], mix.inputs["Color1"])
        nt.links.new(mix.outputs["Color"], bsdf.inputs["Emission Color"])
        bsdf.inputs["Emission Strength"].default_value = 1.0
    except Exception as e:
        print("rimify failed", e)


def build_figure(kit, ctx):
    R, H = faces.HEAD_R, faces.HEAD_H
    P = lambda c, r=0.6, s=0.25: kit.plastic(c, r, spec=s)
    skin = P("#b0713f", 0.55, 0.3)
    hoodie = P("#c9a22a", 0.8, 0.1)
    vest = P("#2f9a45", 0.7, 0.25)
    jeans = P("#2a3550", 0.8, 0.05)
    shoes = P("#222228", 0.6)
    for m_ in (skin, hoodie, vest, jeans, shoes):
        rimify(m_)
    TORSO = 1.65                # about 1.6x the cast's torso, and broad
    LEAN = 0.2                 # hunched: the shoulders roll forward toward the camera
    # legs folded, ordinary: thighs forward and up, shins down, feet flat
    for sx in (-1, 1):
        hip = W(sx * 0.2, 0.0, HIP + 0.12)
        knee = W(sx * 0.22, -0.4, HIP + 0.5)
        foot = W(sx * 0.22, -0.48, 0.1)
        bar(kit, "thigh", hip, knee, 0.32, 0.32, jeans)
        bar(kit, "shin", knee, foot, 0.28, 0.28, jeans)
        kit.box(nm("shoe"), (0.26, 0.42, 0.14), tuple(W(sx * 0.22, -0.6, 0.07)), shoes, None, (0, 0, 0), 0.04)
    base = HIP + 0.04
    # the torso leans toward the camera: built as bars from the hips to the shoulders
    hipc = W(0, 0.0, base)
    shc = W(0, -LEAN, base + TORSO)
    bar(kit, "torso", hipc, shc, 0.56, 0.36, hoodie, bevel=0.07)
    vh = TORSO * 0.9
    for sx in (-1, 1):                      # vest panels either side of a hoodie front
        a_ = W(sx * 0.2, -0.02, base + 0.03)
        b_ = W(sx * 0.2, -LEAN * 0.9 - 0.02, base + vh)
        bar(kit, "vest", a_, b_, 0.25, 0.4, vest, bevel=0.07)
        for k in range(6):                  # quilting ribs
            u = 0.1 + k * 0.15
            c = a_ + (b_ - a_) * u
            kit.box(nm("rib"), (0.25, 0.43, 0.035), tuple(c), P("#237a36", 0.8), None, (0, 0, 0), 0.015)
    sh_z = base + TORSO - 0.12
    # long arms: sleeves down to the knees, hands flat on them
    for sx in (-1, 1):
        shoulder = W(sx * 0.4, -LEAN, sh_z)
        elbow = W(sx * 0.46, -LEAN * 0.2, base + 0.3)
        wrist = W(sx * 0.3, -0.4, HIP + 0.56)
        bar(kit, "uarm", shoulder, elbow, 0.22, 0.22, hoodie, bevel=0.05)
        bar(kit, "farm", elbow, wrist, 0.18, 0.18, hoodie, bevel=0.05)
        kit.box(nm("hand"), (0.17, 0.24, 0.07), tuple(W(sx * 0.24, -0.46, HIP + 0.62)), skin, None, (0, 0, 0), 0.025)
    # the neck: a short dark stub between two raised shoulders; the head is jammed sideways into the roof
    n0 = W(0, -LEAN, base + TORSO)
    hc = V(HC)
    neckmat = P("#2a1a12", 0.6, 0.2)
    hood = P("#b8921c", 0.85, 0.05)
    rimify(neckmat, 18.0, 0.5)
    rimify(hood)
    kit.box(nm("hoodcollar"), (0.5, 0.36, 0.16), tuple(n0 + V((0, 0.0, -0.04))), hood, None, (0, 0, 0), 0.07)
    for sx in (-1, 1):   # shoulders shrugged up to the ears
        bar(kit, "shrug", n0 + V((sx * 0.38, 0.0, -0.18)), n0 + V((sx * 0.2, 0.0, 0.08)), 0.26, 0.34, hoodie, bevel=0.07)
    bar(kit, "neck", n0 + V((0, 0.0, -0.04)), n0 + V((0.12, 0.0, 0.2)), 0.2, 0.2, neckmat, bevel=0.04)

    # head: Dev's face on the rig's head mesh, scaled to the cast's head, then rolled sideways
    face = {"eyes": "hollow", "brows": True, "mouth": "none", "ink": "#2a1a14", "eye_scale": 0.55}
    pil = faces.face_image(face, "#b0713f", "neutral", 0.0, (0, 0), 0.0)
    path = TMP / "dev-face.png"
    pil.save(path)
    img = bpy.data.images.load(str(path))
    img.colorspace_settings.name = "sRGB"
    mat, tex = rig.head_material("figure", "#b0713f")
    tex.image = img
    rimify(mat)
    scale = S * 1.45
    head = kit.empty("chead", tuple(hc))
    head.scale = (scale, scale, scale)
    head.rotation_mode = "QUATERNION"
    # local top (+z) -> world -x (rolled), face (-y local) stays toward +y (the camera); a little extra tilt
    m = Matrix.Rotation(math.radians(76), 3, "Y") @ Matrix.Rotation(math.pi, 3, "Z")
    m = Matrix.Rotation(math.radians(-10), 3, "X") @ m
    head.rotation_quaternion = m.to_quaternion()
    hg = kit.empty("cheadg", (0, 0, 0), head)
    rig.head_mesh("cheadm", mat, hg)
    top = H / 2
    bean = P("#ff7a1a", 0.7, 0.2)
    rimify(bean)
    kit.box("cbeanie", (2 * R + 0.14, 2 * R + 0.14, 0.62), (0, 0, top + 0.08), bean, hg, (0, 0, 0), 0.2)
    kit.box("cbeaniefold", (2 * R + 0.18, 2 * R + 0.18, 0.2), (0, 0, top - 0.15), bean, hg, (0, 0, 0), 0.06)
    # curly hair at the sides under the beanie
    hair = P("#17110d", 0.8, 0.05)
    for sx in (-1, 1):
        kit.box(nm("chair"), (0.16, 0.5, 0.3), (sx * (R + 0.04), 0.1, top - 0.35), hair, hg, (0, 0, 0), 0.06)
    # a nose line (a small lit ridge) and two small glints in the hollow eyes, the brightest things on the head
    kit.box("cnose", (0.07, 0.12, 0.3), (0, -R + 0.02, -0.05), P("#a46b3e", 0.5, 0.35), hg, (0, 0, 0), 0.03)
    glint = kit.emit("#fff6dc", 14.0, name="glint")
    for sx in (-1, 1):
        d = kit.cyl(nm("glint"), 0.03, 0.02, (sx * 0.232, -R - 0.03, 0.075), glint, hg, rot=(math.pi / 2, 0, 0), n=16)
        try:
            d.visible_shadow = False
        except Exception:
            pass
    # two dark sockets over the hollow eyes (the glints sit in them), so the face is half in shadow
    sock = kit.plastic("#120b08", 0.9, spec=0.02)
    for sx in (-1, 1):
        kit.box(nm("socket"), (0.19, 0.03, 0.1), (sx * 0.232, -R - 0.005, 0.08), sock, hg, (0, 0, 0), 0.03)
    # the lantern's own glow on the underside of the head: a narrow warm spot from the floor, aimed at the head
    k = kit.light("headkey", "SPOT", (0.1, 0.75, 0.35), 180, "#ffe3b0", size=0.12, spot=34, blend=0.9, shadow=False)
    kit.aim(k, tuple(hc))
    k2 = kit.light("mekey", "SPOT", (-0.1, 0.75, 0.3), 40, "#ffe3b0", size=0.12, spot=40, blend=0.9, shadow=False)
    kit.aim(k2, (-0.45, 0.0, 0.8))
    ctx["head"] = head


# ------------------------------------------------------------------------------------------------ per frame
def animate(kit, story, tl, t, ctx):
    ch = rig.CHARS.get("me")
    if ch is not None:
        # seated: legs straight out toward the camera (front is local -y, so the legs swing -90 degrees)
        ch.root.location.z = -0.92
        ch.P["leg-1"].rotation_euler = (-math.pi / 2, 0, 0)
        ch.P["leg1"].rotation_euler = (-math.pi / 2, 0, 0)
        ch.P["arm-1"].rotation_euler = (-0.5, 0.1, 0)
        ch.P["arm1"].rotation_euler = (-0.5, -0.1, 0)
    return {}
