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

TA, TB, TC = 1.15, 2.6, 1.28          # tent half-width (x), half-depth (y), height at the middle
FX, FY = 0.02, -0.15                 # the figure's seat (hips), world
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
            verts.append((x, y, roof(x, y)))
    for i in range(ny):
        for j in range(nx):
            a_ = i * (nx + 1) + j
            fcs.append((a_, a_ + 1, a_ + nx + 2, a_ + nx + 1))
    tent_mat = P("#c0601a", 0.9, 0.02)
    try:    # the fabric glows a little from the moon behind it: a cool violet emission under the orange
        bsdf = tent_mat.node_tree.nodes["Principled BSDF"]
        bsdf.inputs["Emission Color"].default_value = (0.55, 0.27, 0.12, 1)
        bsdf.inputs["Emission Strength"].default_value = 0.22
    except Exception:
        pass
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

    # two crossing tent poles pressed on the roof, meeting at a steel hub at the top (scale, and the tally's place)
    steel = P("#2c2e36", 0.4, 0.5)
    for ang in (0.0,):
        pts_ = []
        for k in range(0, 49):
            u = -1 + 2 * k / 48
            x, y = TA * 0.97 * u * math.cos(ang), TB * 0.97 * u * math.sin(ang)
            pts_.append(V((x, y, roof(x, y) - 0.03)))
        for a_, b_ in zip(pts_, pts_[1:]):
            bar(kit, "pole", a_, b_, 0.045, 0.045, steel, bevel=0.012)
    kit.cyl("hub", 0.09, 0.07, (0, 0, roof(0, 0) - 0.07), steel, n=16)

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
    rim = kit.light("moonrim", "SPOT", (1.4, -0.45, 1.0), 450, "#7fa8ff", size=0.15, spot=55, blend=0.3, shadow=False)
    kit.aim(rim, (0.7, -0.15, 0.95))
    rim2 = kit.light("moonrim2", "SPOT", (-0.15, -0.75, 1.15), 450, "#7fa8ff", size=0.15, spot=55, blend=0.3, shadow=False)
    kit.aim(rim2, (0.05, -0.15, 1.0))
    rim3 = kit.light("moonrim3", "SPOT", (0.2, -0.9, 0.5), 200, "#7fa8ff", size=0.15, spot=60, blend=0.3, shadow=False)
    kit.aim(rim3, (0.3, -0.15, 0.8))

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


def rimify(mat, strength=14.0, blend=0.5, color=(0.30, 0.55, 1.0, 1)):
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
    hoodie = P("#e8bf2e", 0.8, 0.1)
    vest = P("#2f9a45", 0.7, 0.25)
    jeans = P("#2a3550", 0.8, 0.05)
    shoes = P("#222228", 0.6)
    for m_ in (skin, hoodie, vest, jeans, shoes):
        rimify(m_)
    TORSO = 0.82                # 1.6x the cast's torso
    NECK = 0.2 * 1.8                  # about 1.8x the neck (a short one on the cast)
    # legs folded, ordinary: thighs forward and up, shins down, feet flat
    for sx in (-1, 1):
        hip = W(sx * 0.17, 0.0, HIP + 0.12)
        knee = W(sx * 0.19, -0.36, HIP + 0.5)
        foot = W(sx * 0.19, -0.44, 0.1)
        bar(kit, "thigh", hip, knee, 0.3, 0.3, jeans)
        bar(kit, "shin", knee, foot, 0.26, 0.26, jeans)
        kit.box(nm("shoe"), (0.24, 0.4, 0.14), tuple(W(sx * 0.19, -0.56, 0.07)), shoes, None, (0, 0, 0), 0.04)
    # the torso: hoodie, with the puffer vest over it in two quilted bands (horizontal ribs)
    base = HIP + 0.04
    kit.box(nm("torso"), (0.5, 0.32, TORSO), tuple(W(0, 0, base + TORSO / 2)), hoodie, None, (0, 0, 0), 0.06)
    vh = TORSO * 0.9
    for sx in (-1, 1):                      # vest panels either side of a hoodie front
        kit.box(nm("vest"), (0.21, 0.355, vh), tuple(W(sx * 0.165, -0.005, base + vh / 2 + 0.03)), vest, None, (0, 0, 0), 0.07)
    for k in range(5):                      # quilting ribs
        z = base + 0.12 + k * (vh - 0.15) / 4
        for sx in (-1, 1):
            kit.box(nm("rib"), (0.21, 0.38, 0.035), tuple(W(sx * 0.165, -0.005, z)), P("#237a36", 0.8), None, (0, 0, 0), 0.015)
    sh_z = base + TORSO - 0.1
    # long arms: sleeves (hoodie yellow under the vest) down to the knees, hands flat on them
    for sx in (-1, 1):
        shoulder = W(sx * 0.34, 0.0, sh_z)
        elbow = W(sx * 0.38, 0.05, base + 0.25)
        wrist = W(sx * 0.27, -0.38, HIP + 0.55)
        bar(kit, "uarm", shoulder, elbow, 0.2, 0.2, hoodie, bevel=0.05)
        bar(kit, "farm", elbow, wrist, 0.17, 0.17, hoodie, bevel=0.05)
        kit.box(nm("hand"), (0.15, 0.22, 0.07), tuple(W(sx * 0.21, -0.44, HIP + 0.6)), skin, None, (0, 0, 0), 0.025)
    # the neck: blocky, in shadow: straight up, then bent over toward frame left; the head lies against the sloping roof
    n0 = W(0, 0.0, base + TORSO - 0.02)
    hc = V((n0.x + 0.62, n0.y + 0.02, n0.z + 0.0))
    attach = hc + V((-0.2, 0.0, 0.06))
    p1 = V((n0.x, n0.y + 0.02, n0.z + 0.3))
    p2 = V((n0.x + 0.22, n0.y + 0.02, n0.z + 0.28))
    neckmat = P("#8a5530", 0.6, 0.2)
    hood = P("#b8921c", 0.85, 0.05)
    rimify(neckmat, 18.0, 0.5)
    rimify(hood)
    kit.box(nm("hoodcollar"), (0.46, 0.34, 0.2), tuple(n0 + V((0, 0.02, -0.02))), hood, None, (0, 0, 0), 0.08)
    kit.box(nm("hoodbunch"), (0.46, 0.2, 0.3), tuple(n0 + V((0, -0.17, -0.03))), hood, None, (0.2, 0, 0), 0.09)
    for sx in (-1, 1):   # hunched shoulders, shrugged up toward the neck
        bar(kit, "shrug", n0 + V((sx * 0.32, 0.0, -0.1)), n0 + V((sx * 0.13, 0.04, 0.08)), 0.22, 0.3, hoodie, bevel=0.06)
    bar(kit, "neck1", n0 + V((0, 0.02, 0.05)), p1, 0.2, 0.2, neckmat, bevel=0.04)
    bar(kit, "neck2", p1 + V((0, 0, -0.1)), p2, 0.2, 0.2, neckmat, bevel=0.04)
    bar(kit, "neck3", p2, attach, 0.2, 0.2, neckmat, bevel=0.04)

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
    scale = S * 1.15
    head = kit.empty("chead", tuple(hc))
    head.scale = (scale, scale, scale)
    head.rotation_mode = "QUATERNION"
    # local top (+z) -> world -x (rolled), face (-y local) stays toward +y (the camera); a little extra tilt
    m = Matrix.Rotation(math.radians(80), 3, "Y") @ Matrix.Rotation(math.pi, 3, "Z")
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
        kit.box(nm("socket"), (0.24, 0.03, 0.13), (sx * 0.232, -R - 0.005, 0.08), sock, hg, (0, 0, 0), 0.03)
    # the lantern's own glow on the underside of the head: a narrow warm spot from the floor, aimed at the head
    k = kit.light("headkey", "SPOT", (0.1, 0.75, 0.35), 55, "#ffe3b0", size=0.12, spot=34, blend=0.9, shadow=False)
    kit.aim(k, tuple(hc))
    k2 = kit.light("mekey", "SPOT", (-0.1, 0.75, 0.3), 14, "#ffe3b0", size=0.12, spot=40, blend=0.9, shadow=False)
    kit.aim(k2, (-0.55, 0.0, 1.05))
    ctx["head"] = head


# ------------------------------------------------------------------------------------------------ per frame
def animate(kit, story, tl, t, ctx):
    ch = rig.CHARS.get("me")
    if ch is not None:
        # seated: legs straight out toward the camera (front is local -y, so the legs swing -90 degrees)
        ch.root.location.z = -0.86
        ch.P["leg-1"].rotation_euler = (-math.pi / 2, 0, 0)
        ch.P["leg1"].rotation_euler = (-math.pi / 2, 0, 0)
        ch.P["arm-1"].rotation_euler = (-0.5, 0.1, 0)
        ch.P["arm1"].rotation_euler = (-0.5, -0.1, 0)
    return {}
