"""The Back Row: a city night bus over seven nights, the foggy stop where I get on, and the thing in the back row.

Built from kit.py's parts. The bus is one group ("bus") so it can drive past a still world in the exterior shots.
Outside, a strip of street (road, kerbs, streetlights, dark buildings with a few lit windows) repeats along y and
slides past the windows while the bus is moving. The stop (shelter, streetlamp, flag, shopfront) is its own
group that stands beside the door whenever the bus is at a stop.

Coordinates: the bus floor is z = 0, its aisle runs along y with the windscreen at y = -7.45 and the rear window
at y = 6.62. Inside it's 4.2 m wide (x = -2.1 .. 2.1, the driver on the left) and 2.75 m tall. Road level is
z = -0.4, the pavement z = -0.25. The back bench has five places at x = -1.64, -0.82, 0, 0.82, 1.64; the
middle one has the dent.

THE CREATURE is the grey passenger itself (note 18, "Uncanny beats tentacles"): the same R6 rig as every rider,
in a long grey coat with the collar up, with the pale grey blank head and its seam mouth (faces.py "line"). Its
proportions are wrong: a torso a head too long, legs that make it far too tall when it stands (bent double under
the ceiling), its own block arms stretched far too long, and big square hands. `build_creature()` makes it once;
`pose_creature()` only sets one still pose per "creature" cue (POSES), so it's the same model in every shot and
never moves on screen. The square print on the rear window is the size of its hand (HAND).

Cues read here:
- stop / go: the bus is at rest from each "stop" until the next "go" (it slows over 2.2 s before, pulls away
  over 2.5 s after); door / door_shut: the front door opens and closes
- night: {"night": "A".."G"}: the weather from here (rain on the glass, fog, the condensation on the rear window)
- leak: the front seats go wet and glossy, puddles show; drip: the drip from the roof seam
- drop: the back tubes cut out for a beat (dur); flicker_on / lights_steady: the back tubes fail / hold steady
- dim: the front of the bus sinks, so the back row is the pool of light
- creature: {"pose": name, "y": .., "head": [yaw, pitch], "hand": [side, [x, y, z]]} a still pose from here
- horror: {"on": bool} the front tubes dead, the back tube dimmed and failing, the creature's head lit from below
- underlight: {"on": bool} its head lit from below before the horror
- back: {"gain": x} the back tubes times x from here; fogwin: {"on": bool} the rear window fogged, the print on it
- swing: the back strap swings hard from here (it always sways a little)

Acting keys read here (acting.py ignores them): "sit": true bends both legs forward 90 degrees, the R6 sitting
pose, until a key says "sit": false.

Shots listed in the story's "exterior_shots" are outside: the street stands still and the bus moves through it.
"""

from __future__ import annotations

import math
from pathlib import Path

import bpy
from mathutils import Matrix, Vector

W = 2.1          # inner half width
CEIL = 2.75
YF, YB = -7.45, 6.62
ROWS = [-4.2, -3.05, -1.9, -0.75, 0.4, 1.55, 2.7, 3.85]
PLAT_Y0 = 4.65   # the raised back platform starts here
PLAT_H = 0.32
TILE = 42.0      # the street repeats every TILE metres
SPEED = 11.0     # m/s while driving
DOOR_Y = (-6.75, -5.25)
MID_DOOR = (0.98, 2.22)       # the middle door, right side (it replaces the right seat of row 5)
BENCH_X = (-1.64, -0.82, 0.0, 0.82, 1.64)
BENCH_TOP = PLAT_H + 0.47     # cushion top
WHEEL = (-1.35, -6.72, 1.06)  # the steering wheel's centre (its rim radius is WHEEL_R)
WHEEL_R = 0.27
EYE_MIRROR = (-0.78, -7.27, 2.1)   # a flat rear-view mirror over the windscreen: the driver's eyes are in it
EYE_CAM = (-0.5, -5.78, 1.78)      # ...seen from here (the mirror is angled so this camera sees his eyes)
DRIVER_EYES = (-1.35, -6.47, 1.62)
FONT = Path(__file__).resolve().parents[2] / "blocky" / "fonts" / "SchibstedGrotesk-Black.ttf"

# the square print on the rear window (its centre, world metres): where the creature's hand pressed, from inside
PRINT_X, PRINT_Z = 0.28, 1.86
HAND = 0.5              # metres: its big square block hand (the print is the same size)
# --------------------------------------------------------------------------------------------- materials


def _principled_mat(kit, name):
    m, N, L, b = kit._mat(name)
    return m, N, L, b


def rubber_floor(kit):
    """Blue-grey studded rubber, scuffed paler along the aisle."""
    m, N, L, b = _principled_mat(kit, "bus floor")
    v = kit._coords(N, L, 1.0)
    vor = N.new("ShaderNodeTexVoronoi")
    vor.inputs["Scale"].default_value = 6.0
    vor.inputs["Randomness"].default_value = 0.0
    L.new(v, vor.inputs["Vector"])
    stud = N.new("ShaderNodeMapRange")
    stud.inputs["From Min"].default_value = 0.22
    stud.inputs["From Max"].default_value = 0.3
    stud.inputs["To Min"].default_value = 1.0
    stud.inputs["To Max"].default_value = 0.0
    L.new(vor.outputs["Distance"], stud.inputs["Value"])
    nz = N.new("ShaderNodeTexNoise")
    nz.inputs["Scale"].default_value = 1.4
    nz.inputs["Detail"].default_value = 6.0
    L.new(v, nz.inputs["Vector"])
    ramp = N.new("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].position = 0.35
    ramp.color_ramp.elements[0].color = kit.col("#22272b")
    ramp.color_ramp.elements[1].position = 0.72
    ramp.color_ramp.elements[1].color = kit.col("#3e464b")
    L.new(nz.outputs["Fac"], ramp.inputs["Fac"])
    mix = N.new("ShaderNodeMix")
    mix.data_type = "RGBA"
    L.new(stud.outputs["Result"], mix.inputs["Factor"])
    L.new(ramp.outputs["Color"], mix.inputs["A"])
    mix.inputs["B"].default_value = kit.col("#5a6368")
    L.new(mix.outputs["Result"], b.inputs["Base Color"])
    rr = N.new("ShaderNodeMapRange")
    rr.inputs["To Min"].default_value = 0.78
    rr.inputs["To Max"].default_value = 0.5
    L.new(nz.outputs["Fac"], rr.inputs["Value"])
    L.new(rr.outputs["Result"], b.inputs["Roughness"])
    kit._bump(N, L, b, stud.outputs["Result"], 1.0, 0.012)
    kit._fogged(m, b.outputs[0])
    return m


def vinyl(kit, name, base, worn):
    """Worn seat vinyl with a soft sheen, paler where people sit. A Value node "wet" (0..1) darkens it and makes
    it glossy, for the leak."""
    m, N, L, b = _principled_mat(kit, name)
    v = kit._coords(N, L, 1.0)
    nz = N.new("ShaderNodeTexNoise")
    nz.inputs["Scale"].default_value = 3.5
    nz.inputs["Detail"].default_value = 8.0
    L.new(v, nz.inputs["Vector"])
    ramp = N.new("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].position = 0.42
    ramp.color_ramp.elements[0].color = kit.col(base)
    ramp.color_ramp.elements[1].position = 0.7
    ramp.color_ramp.elements[1].color = kit.col(worn)
    L.new(nz.outputs["Fac"], ramp.inputs["Fac"])
    fine = N.new("ShaderNodeTexNoise")
    fine.inputs["Scale"].default_value = 90.0
    fine.inputs["Detail"].default_value = 2.0
    L.new(v, fine.inputs["Vector"])
    wet = N.new("ShaderNodeValue")
    wet.name = wet.label = "wet"
    wet.outputs[0].default_value = 0.0
    dark = N.new("ShaderNodeMix")
    dark.data_type = "RGBA"
    dark.blend_type = "MULTIPLY"
    L.new(wet.outputs[0], dark.inputs["Factor"])
    L.new(ramp.outputs["Color"], dark.inputs["A"])
    dark.inputs["B"].default_value = (0.5, 0.52, 0.55, 1)
    L.new(dark.outputs["Result"], b.inputs["Base Color"])
    rough = N.new("ShaderNodeMapRange")
    rough.inputs["From Min"].default_value = 0.0
    rough.inputs["From Max"].default_value = 1.0
    rough.inputs["To Min"].default_value = 0.42
    rough.inputs["To Max"].default_value = 0.06
    L.new(wet.outputs[0], rough.inputs["Value"])
    L.new(rough.outputs["Result"], b.inputs["Roughness"])
    for k in ("Coat Weight",):
        if k in b.inputs:
            L.new(wet.outputs[0], b.inputs[k])
    kit._bump(N, L, b, fine.outputs["Fac"], 0.08, 0.002)
    kit._fogged(m, b.outputs[0])
    return m, wet


def rain_glass(kit, name="bus glass"):
    """Window glass with beads and runs of rain on it (a bump only, so it refracts the lights outside). A Value
    node "rain" scales how wet it is."""
    m, N, L, b = _principled_mat(kit, name)
    b.inputs["Base Color"].default_value = kit.col("#b9c8cf")
    b.inputs["Roughness"].default_value = 0.04
    b.inputs["Transmission Weight" if "Transmission Weight" in b.inputs else "Transmission"].default_value = 1.0
    b.inputs["IOR"].default_value = 1.45
    tc = N.new("ShaderNodeTexCoord")
    mp = N.new("ShaderNodeMapping")
    mp.inputs["Scale"].default_value = (1.0, 7.0, 1.0)   # runs: stretched along z in object space
    L.new(tc.outputs["Object"], mp.inputs["Vector"])
    runs = N.new("ShaderNodeTexVoronoi")
    runs.inputs["Scale"].default_value = 14.0
    L.new(mp.outputs["Vector"], runs.inputs["Vector"])
    beads = N.new("ShaderNodeTexVoronoi")
    beads.inputs["Scale"].default_value = 55.0
    L.new(tc.outputs["Object"], beads.inputs["Vector"])
    bm = N.new("ShaderNodeMapRange")
    bm.inputs["From Min"].default_value = 0.12
    bm.inputs["From Max"].default_value = 0.0
    L.new(beads.outputs["Distance"], bm.inputs["Value"])
    rm = N.new("ShaderNodeMapRange")
    rm.inputs["From Min"].default_value = 0.08
    rm.inputs["From Max"].default_value = 0.0
    L.new(runs.outputs["Distance"], rm.inputs["Value"])
    add = N.new("ShaderNodeMath")
    add.operation = "MAXIMUM"
    L.new(bm.outputs["Result"], add.inputs[0])
    L.new(rm.outputs["Result"], add.inputs[1])
    rain = N.new("ShaderNodeValue")
    rain.name = rain.label = "rain"
    rain.outputs[0].default_value = 0.6
    mul = N.new("ShaderNodeMath")
    mul.operation = "MULTIPLY"
    L.new(add.outputs[0], mul.inputs[0])
    L.new(rain.outputs[0], mul.inputs[1])
    bp = N.new("ShaderNodeBump")
    bp.inputs["Distance"].default_value = 0.004
    L.new(rain.outputs[0], bp.inputs["Strength"])
    L.new(mul.outputs[0], bp.inputs["Height"])
    L.new(bp.outputs["Normal"], b.inputs["Normal"])
    kit._fogged(m, b.outputs[0])
    return m, rain


def emissive(kit, name, hexc, strength):
    """An emission material whose strength the animation can set."""
    m = kit._new(name)
    nt = m.node_tree
    nt.nodes.remove(nt.nodes["Principled BSDF"])
    e = nt.nodes.new("ShaderNodeEmission")
    e.inputs["Color"].default_value = kit.col(hexc)
    e.inputs["Strength"].default_value = strength
    kit._fogged(m, e.outputs[0])
    try:
        m.emission_sampling = "NONE"
    except Exception:
        pass
    return m, e


def glow_cone_mat(kit, hexc, strength):
    """The fake light cone under the streetlight: thin emission that fades toward the cone's edge and bottom."""
    m = kit._new("cone glow")
    nt = m.node_tree
    N, L = nt.nodes, nt.links
    N.remove(N["Principled BSDF"])
    out = next(n for n in N if n.type == "OUTPUT_MATERIAL")
    lw = N.new("ShaderNodeLayerWeight")
    lw.inputs["Blend"].default_value = 0.35
    inv = N.new("ShaderNodeMath")
    inv.operation = "SUBTRACT"
    inv.inputs[0].default_value = 1.0
    L.new(lw.outputs["Facing"], inv.inputs[1])
    tc = N.new("ShaderNodeTexCoord")
    sep = N.new("ShaderNodeSeparateXYZ")
    L.new(tc.outputs["Generated"], sep.inputs[0])
    mul = N.new("ShaderNodeMath")
    mul.operation = "MULTIPLY"
    L.new(inv.outputs[0], mul.inputs[0])
    L.new(sep.outputs["Z"], mul.inputs[1])
    pw = N.new("ShaderNodeMath")
    pw.operation = "POWER"
    L.new(mul.outputs[0], pw.inputs[0])
    pw.inputs[1].default_value = 1.6
    e = N.new("ShaderNodeEmission")
    e.inputs["Color"].default_value = kit.col(hexc)
    e.inputs["Strength"].default_value = strength
    tr = N.new("ShaderNodeBsdfTransparent")
    add = N.new("ShaderNodeAddShader")
    sc = N.new("ShaderNodeMath")
    sc.operation = "MULTIPLY"
    L.new(pw.outputs[0], sc.inputs[0])
    sc.inputs[1].default_value = 1.0
    mixe = N.new("ShaderNodeMixShader")
    L.new(sc.outputs[0], mixe.inputs[0])
    blk = N.new("ShaderNodeEmission")
    blk.inputs["Strength"].default_value = 0.0
    L.new(blk.outputs[0], mixe.inputs[1])
    L.new(e.outputs[0], mixe.inputs[2])
    L.new(tr.outputs[0], add.inputs[0])
    L.new(mixe.outputs[0], add.inputs[1])
    L.new(add.outputs[0], out.inputs["Surface"])
    try:
        m.emission_sampling = "NONE"
        m.blend_method = "BLEND"
    except Exception:
        pass
    return m


# ------------------------------------------------------------------------------------------------- parts


def torus(kit, name, R, r, loc, mat, parent, rot=(0, 0, 0), n=28, m_=10):
    verts, faces = [], []
    for i in range(n):
        a = 2 * math.pi * i / n
        for j in range(m_):
            b = 2 * math.pi * j / m_
            verts.append(((R + r * math.cos(b)) * math.cos(a), (R + r * math.cos(b)) * math.sin(a), r * math.sin(b)))
    for i in range(n):
        for j in range(m_):
            a0, a1 = i * m_ + j, ((i + 1) % n) * m_ + j
            faces.append((a0, a1, ((i + 1) % n) * m_ + (j + 1) % m_, i * m_ + (j + 1) % m_))
    return kit.mesh_obj(name, verts, faces, mat, parent, loc, rot, smooth=True)


def rod(kit, name, p0, p1, r, mat, parent, n=14):
    """A cylinder from p0 to p1."""
    from mathutils import Vector
    a, b = Vector(p0), Vector(p1)
    d = b - a
    ob = kit.cyl(name, r, d.length, tuple((a + b) / 2), mat, parent, n=n)
    ob.rotation_euler = d.to_track_quat("Z", "Y").to_euler()
    return ob


def seat_pair(kit, M, name, x, y, parent, cushion, z0=0.0, width=1.42):
    """A forward-facing double seat: cushion, raked back, moulded shell, chrome grab rail, one leg."""
    side = 1 if x > 0 else -1
    kit.box(f"{name}.cush", (width, 0.52, 0.14), (x, y - 0.02, z0 + 0.42), cushion, parent, bevel=0.05, seg=3)
    kit.box(f"{name}.back", (width, 0.12, 0.8), (x, y + 0.28, z0 + 0.9), cushion, parent, rot=(-0.12, 0, 0),
            bevel=0.05, seg=3)
    kit.box(f"{name}.shell", (width + 0.03, 0.05, 0.86), (x, y + 0.36, z0 + 0.9), M["shell"], parent,
            rot=(-0.12, 0, 0), bevel=0.02)
    kit.box(f"{name}.pan", (width - 0.1, 0.46, 0.08), (x, y - 0.02, z0 + 0.31), M["shell"], parent, bevel=0.02)
    rod(kit, f"{name}.rail", (x - width / 2 + 0.06, y + 0.42, z0 + 1.33), (x + width / 2 - 0.06, y + 0.42, z0 + 1.33),
        0.022, M["chrome"], parent)
    for k, sx in enumerate((-1, 1)):
        rod(kit, f"{name}.post{k}", (x + sx * (width / 2 - 0.06), y + 0.4, z0 + 1.2),
            (x + sx * (width / 2 - 0.06), y + 0.42, z0 + 1.34), 0.02, M["chrome"], parent)
    lx = x - side * (width / 2 - 0.15)
    kit.box(f"{name}.leg", (0.07, 0.07, 0.28), (lx, y, z0 + 0.14), M["frame"], parent, bevel=0.01)
    kit.box(f"{name}.foot", (0.09, 0.4, 0.03), (lx, y, z0 + 0.015), M["frame"], parent, bevel=0.01)


def streetlight(kit, M, name, x, y, parent, arm_dir, z0=-0.25, h=6.4, energy=550.0, spot=False):
    rod(kit, f"{name}.pole", (x, y, z0), (x, y, z0 + h), 0.08, M["pole"], parent, n=12)
    ax = x + arm_dir * 1.5
    rod(kit, f"{name}.arm", (x, y, z0 + h - 0.1), (ax, y, z0 + h + 0.05), 0.05, M["pole"], parent, n=10)
    kit.box(f"{name}.head", (0.7, 0.32, 0.16), (ax, y, z0 + h), M["pole"], parent, bevel=0.04)
    kit.box(f"{name}.lens", (0.6, 0.26, 0.03), (ax, y, z0 + h - 0.085), M["sodium"], parent)
    if spot:
        kit.light(f"{name}.L", "SPOT", (ax, y, z0 + h - 0.2), energy, "#ffad52", spot=70, blend=0.6, size=0.25,
                  parent=parent)
    else:
        kit.light(f"{name}.L", "POINT", (ax, y, z0 + h - 0.25), energy, "#ffad52", size=0.3, parent=parent)
    return ax


def building(kit, M, name, x0, y, depth, length, height, side, parent, seed):
    """A dark block with a grid of windows, a few lit (warm or TV-blue), most dark glass."""
    xc = x0 + side * depth / 2
    kit.box(f"{name}.b", (depth, length, height), (xc, y, -0.25 + height / 2), M["facade"], parent)
    face_x = x0 - side * 0.02
    rows = int((height - 1.2) // 2.6)
    cols = int(length // 2.2)
    for r in range(rows):
        for c in range(cols):
            h = kit.hash01(seed, r, c)
            wy = y - length / 2 + 1.1 + c * (length - 2.2) / max(1, cols - 1)
            wz = 1.6 + r * 2.6
            mat = M["win_dark"]
            if h < 0.16:
                mat = M["win_warm"]
            elif h < 0.21:
                mat = M["win_blue"]
            kit.box(f"{name}.w{r}.{c}", (0.06, 1.1, 1.3), (face_x, wy, wz), mat, parent)
    # a shopfront at street level, shuttered
    kit.box(f"{name}.shut", (0.08, length * 0.7, 2.4), (face_x - side * 0.02, y, 0.95), M["shutter"], parent)



# ------------------------------------------------------------------------------------------- textures


def pil_image(name, pil):
    """A PIL image as a Blender image, packed in memory (no file next to the frames)."""
    import numpy as np

    pil = pil.convert("RGBA")
    w, h = pil.size
    img = bpy.data.images.new(name, w, h, alpha=True)
    a = np.asarray(pil, dtype=np.float32)[::-1].reshape(-1) / 255.0
    img.pixels.foreach_set(a)
    img.pack()
    return img


def text_panel(name, w_px, h_px, rows, bg, fg="#f2efe6"):
    """Made-up signage: rows of (text, px, colour or None, y) in the story's caption font."""
    from PIL import Image, ImageDraw, ImageFont

    im = Image.new("RGBA", (w_px, h_px), bg)
    d = ImageDraw.Draw(im)
    for text, px, c, y in rows:
        f = ImageFont.truetype(str(FONT), px)
        tw = d.textlength(text, font=f)
        d.text(((w_px - tw) / 2, y), text, font=f, fill=c or fg)
    return im


def blank_panel(w_px, h_px, bg, edge):
    """An empty frame: a plain panel with a slightly lighter border, no words."""
    from PIL import Image, ImageDraw

    im = Image.new("RGBA", (w_px, h_px), edge)
    ImageDraw.Draw(im).rectangle([w_px * 0.05, h_px * 0.05, w_px * 0.95, h_px * 0.95], fill=bg)
    return im


def timetable_panel(w_px, h_px, bg):
    """A timetable with no words: a header bar and rows of short pale bars, unreadable at any distance."""
    from PIL import Image, ImageDraw
    import random

    rnd = random.Random(3)
    im = Image.new("RGBA", (w_px, h_px), bg)
    d = ImageDraw.Draw(im)
    d.rectangle([40, 40, w_px - 40, 120], fill="#d9d4c4")
    for k in range(9):
        y = 170 + k * 52
        for x0, x1 in ((50, 50 + rnd.randint(90, 170)), (260, 260 + rnd.randint(60, 120)),
                       (400, 400 + rnd.randint(30, 60))):
            d.rectangle([x0, y, x1, y + 16], fill="#9fb3b8")
    return im


def image_mat(kit, name, img, emit=0.0, rough=0.5):
    m = kit._new(name)
    nt = m.node_tree
    N, L = nt.nodes, nt.links
    b = N["Principled BSDF"]
    b.inputs["Roughness"].default_value = rough
    tex = N.new("ShaderNodeTexImage")
    tex.image = img
    uv = N.new("ShaderNodeTexCoord")
    L.new(uv.outputs["UV"], tex.inputs["Vector"])
    L.new(tex.outputs["Color"], b.inputs["Base Color"])
    if emit > 0:
        L.new(tex.outputs["Color"], b.inputs["Emission Color" if "Emission Color" in b.inputs else "Emission"])
        b.inputs["Emission Strength"].default_value = emit
    kit._fogged(m, b.outputs[0])
    return m


def uv_plane(kit, name, size, loc, mat, parent, rot=(0, 0, 0)):
    """A plane with 0..1 UVs, upright text reading toward -y before rot."""
    x, z = size[0] / 2, size[1] / 2
    ob = kit.mesh_obj(name, [(-x, 0, -z), (x, 0, -z), (x, 0, z), (-x, 0, z)], [(0, 1, 2, 3)], mat, parent, loc, rot)
    uv = ob.data.uv_layers.new(name="UVMap")
    for li, (u, v) in zip(ob.data.polygons[0].loop_indices, ((0, 0), (1, 0), (1, 1), (0, 1))):
        uv.data[li].uv = (u, v)
    return ob


def handprint_image(px_per_m=600, size=(2 * W - 0.78, 1.0)):
    """The print the creature's hand leaves in the condensation: one big square, too big for a person (the same
    HAND as its block hands), pressed flat, with a few runs under it. White = fog, black = the glass wiped clear."""
    from PIL import Image, ImageDraw, ImageFilter
    import random

    W_, H_ = int(size[0] * px_per_m), int(size[1] * px_per_m)
    rnd = random.Random(7)
    im = Image.new("L", (W_, H_), 0)
    d = ImageDraw.Draw(im)
    for _ in range(1400):   # condensation: a soft uneven film, thinner near the top
        x, y, r = rnd.uniform(0, W_), rnd.uniform(0, H_), rnd.uniform(10, 45)
        d.ellipse([x - r, y - r, x + r, y + r], fill=int(150 + 80 * (y / H_) + rnd.uniform(-20, 20)))
    im = im.filter(ImageFilter.GaussianBlur(14))
    d = ImageDraw.Draw(im)
    s_ = px_per_m
    cx, cy = W_ * (0.5 + PRINT_X / size[0]), H_ * (1 - (PRINT_Z - 1.38))   # the square's centre on the glass
    half = HAND / 2 * s_
    # pressed, not cut: a few overlapping squares a little off each other, then the film creeping back in
    for k in range(6):
        jx, jy, jr = rnd.uniform(-10, 10), rnd.uniform(-10, 10), rnd.uniform(-14, 6)
        d.rounded_rectangle([cx - half + jx - jr, cy - half + jy - jr, cx + half + jx + jr, cy + half + jy + jr],
                            radius=int(0.05 * s_), fill=int(rnd.uniform(10, 40)))
    for _ in range(90):   # beads of film left on the glass inside the print
        x, y, r = rnd.uniform(cx - half, cx + half), rnd.uniform(cy - half, cy + half), rnd.uniform(3, 12)
        d.ellipse([x - r, y - r, x + r, y + r], fill=int(rnd.uniform(60, 120)))
    # a fainter second press beside it, where it touched the glass first
    o = 0.16 * s_
    d.rounded_rectangle([cx - half - o, cy - half - o * 0.6, cx + half - o, cy + half - o * 0.6],
                        radius=int(0.05 * s_), outline=110, width=10)
    im = im.filter(ImageFilter.GaussianBlur(5))
    d = ImageDraw.Draw(im)
    for k in range(6):   # runs where the wiped film beads and slides
        x = cx - half + (k + 0.5) * 2 * half / 6 + rnd.uniform(-10, 10)
        L_ = rnd.uniform(0.06, 0.24) * s_
        d.line([(x, cy + half - 4), (x + rnd.uniform(-3, 3), cy + half + L_)], fill=30, width=5)
    return im.filter(ImageFilter.GaussianBlur(2.5))


def condensation_mat(kit, img):
    """The fogged rear window: a milky film with the print wiped clear. A Value node "fog" (0..1) fades it."""
    m = kit._new("condensation")
    nt = m.node_tree
    N, L = nt.nodes, nt.links
    out = next(n for n in N if n.type == "OUTPUT_MATERIAL")
    b = N["Principled BSDF"]
    b.inputs["Base Color"].default_value = kit.col("#c9d2d4")
    b.inputs["Roughness"].default_value = 0.6
    tex = N.new("ShaderNodeTexImage")
    tex.image = img
    tex.image.colorspace_settings.name = "Non-Color"
    uv = N.new("ShaderNodeTexCoord")
    L.new(uv.outputs["UV"], tex.inputs["Vector"])
    fog = N.new("ShaderNodeValue")
    fog.name = fog.label = "fog"
    fog.outputs[0].default_value = 0.0
    mul = N.new("ShaderNodeMath")
    mul.operation = "MULTIPLY"
    L.new(tex.outputs["Color"], mul.inputs[0])
    L.new(fog.outputs[0], mul.inputs[1])
    mul2 = N.new("ShaderNodeMath")
    mul2.operation = "MULTIPLY"
    mul2.inputs[1].default_value = 0.9
    L.new(mul.outputs[0], mul2.inputs[0])
    tr = N.new("ShaderNodeBsdfTransparent")
    mix = N.new("ShaderNodeMixShader")
    L.new(mul2.outputs[0], mix.inputs[0])
    L.new(tr.outputs[0], mix.inputs[1])
    L.new(b.outputs[0], mix.inputs[2])
    L.new(mix.outputs[0], out.inputs["Surface"])
    try:
        m.blend_method = "BLEND"
    except Exception:
        pass
    return m, fog


def dent_vinyl(kit):
    """The back-row vinyl again, darker and more creased down in the hollow (object z below the cushion top), so
    the dent reads on a phone from any angle."""
    m, wet = vinyl(kit, "vinyl dent", "#3a5061", "#5b6d7a")
    N, L = m.node_tree.nodes, m.node_tree.links
    b = N["Principled BSDF"]
    src = b.inputs["Base Color"].links[0].from_socket
    tc = N.new("ShaderNodeTexCoord")
    sep = N.new("ShaderNodeSeparateXYZ")
    L.new(tc.outputs["Object"], sep.inputs[0])
    mr = N.new("ShaderNodeMapRange")
    mr.inputs["From Min"].default_value = BENCH_TOP - 0.006
    mr.inputs["From Max"].default_value = BENCH_TOP - 0.07
    L.new(sep.outputs["Z"], mr.inputs["Value"])
    crease = N.new("ShaderNodeTexWave")
    crease.inputs["Scale"].default_value = 18.0
    crease.inputs["Distortion"].default_value = 6.0
    L.new(tc.outputs["Object"], crease.inputs["Vector"])
    mix = N.new("ShaderNodeMix")
    mix.data_type = "RGBA"
    mix.blend_type = "MULTIPLY"
    L.new(mr.outputs["Result"], mix.inputs["Factor"])
    L.new(src, mix.inputs["A"])
    mix.inputs["B"].default_value = (0.32, 0.34, 0.37, 1)
    L.new(mix.outputs["Result"], b.inputs["Base Color"])
    bp = N.new("ShaderNodeBump")
    bp.inputs["Distance"].default_value = 0.004
    L.new(mr.outputs["Result"], bp.inputs["Strength"])
    L.new(crease.outputs["Fac"], bp.inputs["Height"])
    L.new(bp.outputs["Normal"], b.inputs["Normal"])
    return m


def dent_cushion(kit, name, cx, cy, top, w, d, mat, parent):
    """The middle place of the back bench: a vinyl cushion with a deep two-lobed dent in it, as if somebody
    heavy had just stood up. A grid top over a skirt, so the light rakes across the hollow."""
    nx, ny = 28, 20
    verts, faces = [], []
    def depth(u, v):
        x, y = (u - 0.5) * w, (v - 0.5) * d
        dz = 0.0
        for lx in (-0.12, 0.12):
            dz += 0.075 * math.exp(-(((x - lx) / 0.12) ** 2 + ((y + 0.03) / 0.13) ** 2))
        dz += 0.022 * math.exp(-((x / 0.24) ** 2 + ((y + 0.2) / 0.1) ** 2))   # where the thighs were
        edge = min(u, 1 - u, v, 1 - v)
        return dz * min(1.0, edge / 0.08)
    for j in range(ny + 1):
        for i in range(nx + 1):
            u, v = i / nx, j / ny
            verts.append((cx + (u - 0.5) * w, cy + (v - 0.5) * d, top - depth(u, v)))
    for j in range(ny):
        for i in range(nx):
            a = j * (nx + 1) + i
            faces.append((a, a + 1, a + nx + 2, a + nx + 1))
    # a skirt down the four sides to the cushion's base
    base = len(verts)
    ring = [j * (nx + 1) for j in range(ny + 1)][::-1] + list(range(nx + 1)) + \
           [j * (nx + 1) + nx for j in range(ny + 1)] + [ny * (nx + 1) + i for i in range(nx + 1)][::-1]
    for k in ring:
        x, y, _ = verts[k]
        verts.append((x, y, top - 0.12))
    for q in range(len(ring) - 1):
        faces.append((ring[q], ring[q + 1], base + q + 1, base + q))
    ob = kit.mesh_obj(name, verts, faces, mat, parent, smooth=True)
    return ob


# --------------------------------------------------------------------------------------------------- build


def build(kit, story, tl):
    ctx = {"lights_front": [], "lights_back": [], "street_lights": [], "drips": []}
    M = {
        "paint": kit.plastic("#c9cec9", 0.32, name="bus paint"),
        "band": kit.plastic("#2c5e66", 0.35, name="bus band"),
        "skirt": kit.plastic("#1b1d20", 0.6, name="bus skirt"),
        "wall_in": kit.grime("#a3a59c", 0.8, 2.0, name="bus wall in", rough=0.55),
        "wall_low": kit.grime("#4f5a60", 0.75, 3.0, name="bus wall low", rough=0.6),
        "ceil": kit.grime("#b3b4ab", 0.78, 1.6, name="bus ceiling", rough=0.7),
        "shell": kit.plastic("#2b3034", 0.5, name="seat shell"),
        "frame": kit.metal("#4a4d50", 0.45, name="seat frame"),
        "chrome": kit.metal("#d4d7da", 0.18, name="chrome"),
        "yellow": kit.plastic("#e0b21a", 0.45, name="grab yellow"),
        "rubber": kit.plastic("#121315", 0.8, name="rubber"),
        "dash": kit.plastic("#1b1e22", 0.55, name="dash"),
        "ad": kit.plastic("#38434c", 0.28, name="ad blank"),
        "red": kit.plastic("#b3231f", 0.4, name="stop red"),
        "mirror": kit.metal("#e8ecef", 0.015, name="convex mirror"),
        "flatmirror": kit.metal("#eef1f3", 0.0, name="flat mirror"),
        "pole": kit.metal("#3a3d40", 0.5, name="street pole"),
        "road": kit.grime("#1c1e21", 0.6, 0.35, name="asphalt wet", rough=0.2),
        "kerb": kit.concrete("#8b8a84", 1.2, 0.5, name="kerb"),
        "pave": kit.concrete("#5d5d59", 0.8, 0.5, name="pavement wet", rough=0.3),
        "facade": kit.bricks("#4a3329", "#38281f", "#262220", 1.0, name="facade bricks", grime_amt=0.5),
        "shutter": kit.metal("#4b4f52", 0.5, name="shutter"),
        "line": kit.plastic("#b9b6a8", 0.5, name="lane paint"),
        "tyre": kit.plastic("#101112", 0.85, name="tyre"),
        "stain": kit.grime("#6b6a5e", 0.5, 6.0, name="ceiling stain", rough=0.5),
        "puddle": kit.plastic("#2a3237", 0.02, name="puddle", spec=0.9),
        "shelter": kit.metal("#5d6a70", 0.4, name="shelter frame"),
        "bin": kit.plastic("#2f4a3a", 0.5, name="bin green"),
    }
    M["floor"] = rubber_floor(kit)
    M["seat"], wet_front = vinyl(kit, "vinyl front", "#3c5263", "#647684")
    M["seat_back"], _ = vinyl(kit, "vinyl back", "#3a5061", "#5b6d7a")
    M["drv_seat"] = kit.plastic("#23272c", 0.5, name="driver seat")
    M["glass"], rain = rain_glass(kit)
    M["partition"] = kit.glass("#c9d4d8", name="partition glass")
    M["water"] = kit.glass("#dfe9ef", name="drip water")
    M["tube_f"], tube_f = emissive(kit, "tube front", "#e6fbef", 7.0)
    M["tube_b"], tube_b = emissive(kit, "tube back", "#e6fbef", 7.0)
    M["sodium"], _ = emissive(kit, "sodium lens", "#ffbb6a", 22.0)
    M["win_warm"], _ = emissive(kit, "window warm", "#ffbf73", 2.2)
    M["win_blue"], _ = emissive(kit, "window blue", "#8fb2ff", 1.6)
    M["win_dark"] = kit.plastic("#0d1014", 0.15, name="window dark")
    M["head"], _ = emissive(kit, "headlight", "#fff2d8", 18.0)
    M["tail"], _ = emissive(kit, "taillight", "#ff2a1c", 6.0)
    M["instr"], _ = emissive(kit, "instruments", "#7ff0b0", 1.4)
    M["amber"], _ = emissive(kit, "amber", "#ffae3a", 3.0)
    M["lamp"], lamp_e = emissive(kit, "streetlamp lens", "#ffd9a0", 40.0)
    ctx.update(wet=wet_front, rain=rain, tube_f=tube_f, tube_b=tube_b)

    bus = kit.empty("bus")
    ctx["bus"] = bus
    L = YB - YF

    # ---- shell: floor, platform, ceiling, walls with window openings
    kit.box("floor", (2 * W, L, 0.1), (0, (YF + YB) / 2, -0.05), M["floor"], bus)
    kit.box("platform", (2 * W, YB - PLAT_Y0, PLAT_H), (0, (PLAT_Y0 + YB) / 2, PLAT_H / 2), M["floor"], bus)
    kit.box("platform.edge", (2 * W, 0.06, 0.03), (0, PLAT_Y0 + 0.03, PLAT_H + 0.005), M["yellow"], bus)
    kit.box("platform.riser", (2 * W, 0.02, PLAT_H), (0, PLAT_Y0 - 0.005, PLAT_H / 2), M["wall_low"], bus)
    kit.box("ceiling", (2 * W + 0.2, L, 0.06), (0, (YF + YB) / 2, CEIL + 0.03), M["ceil"], bus)
    kit.box("roof", (2 * W + 0.36, L + 0.25, 0.14), (0, (YF + YB) / 2, CEIL + 0.14), M["paint"], bus, bevel=0.06)
    kit.box("underskirt", (2 * W + 0.36, L + 0.25, 0.35), (0, (YF + YB) / 2, -0.22), M["skirt"], bus)

    win_lo, win_hi = 1.02, 2.12
    pillars = [-7.35, -5.25] + [r + 0.36 for r in ROWS[:-1]] + [4.55, 5.6, 6.55]
    for s in (-1, 1):
        x_in, x_out = s * (W + 0.03), s * (W + 0.13)

        def span(y0, y1, z0, z1, mat, x, t, nm):
            kit.box(nm, (t, y1 - y0, z1 - z0), (x, (y0 + y1) / 2, (z0 + z1) / 2), mat, bus)
        segs = [(YF, YB)]
        if s > 0:
            segs = [(YF, DOOR_Y[0]), (DOOR_Y[1], MID_DOOR[0]), (MID_DOOR[1], YB)]
        for k, (a, b) in enumerate(segs):
            span(a, b, 0.0, win_lo, M["wall_low"], x_in, 0.06, f"wall.low{s}.{k}")
            span(a, b, -0.05, win_lo, M["paint"], x_out, 0.1, f"skin.low{s}.{k}")
            span(a, b, 0.45, 0.62, M["band"], x_out + s * 0.055, 0.01, f"skin.band{s}.{k}")
        span(YF, YB, win_hi, CEIL, M["wall_in"], x_in, 0.06, f"wall.up{s}")
        span(YF, YB, win_hi, CEIL + 0.07, M["paint"], x_out, 0.1, f"skin.up{s}")
        pil = list(pillars)
        if s > 0:
            pil = [p for p in pil if not (MID_DOOR[0] - 0.25 < p < MID_DOOR[1] + 0.25)] + list(MID_DOOR)
        for i, py in enumerate(pil):
            if s > 0 and DOOR_Y[0] - 0.2 < py < DOOR_Y[1] + 0.2 and py != DOOR_Y[1]:
                continue
            kit.box(f"pillar{s}.{i}", (0.2, 0.14, win_hi - win_lo), (s * (W + 0.08), py, (win_lo + win_hi) / 2),
                    M["wall_in"], bus)
            kit.box(f"pstrip{s}.{i}", (0.03, 0.05, 0.85), (s * (W - 0.02), py, 1.55), M["yellow"], bus, bevel=0.01)
            kit.box(f"pillar.o{s}.{i}", (0.06, 0.16, win_hi - win_lo), (s * (W + 0.17), py, (win_lo + win_hi) / 2),
                    M["rubber"], bus)
        glass_y = [(-7.35, -5.25), (-5.25, YB - 0.07)] if s < 0 else [(-5.25, MID_DOOR[0]), (MID_DOOR[1], YB - 0.07)]
        for k, (a, b) in enumerate(glass_y):
            kit.box(f"glass{s}.{k}", (0.02, b - a, win_hi - win_lo), (s * (W + 0.1), (a + b) / 2, (win_lo + win_hi) / 2),
                    M["glass"], bus)
        if s < 0:
            kit.box("glass.drv", (0.02, 2.1, win_hi - win_lo + 0.3), (s * (W + 0.1), -6.3, (win_lo + win_hi) / 2 - 0.1),
                    M["glass"], bus)
        kit.box(f"gasket.lo{s}", (0.08, L, 0.04), (s * (W + 0.04), (YF + YB) / 2, win_lo), M["rubber"], bus)
        kit.box(f"gasket.hi{s}", (0.08, L, 0.04), (s * (W + 0.04), (YF + YB) / 2, win_hi), M["rubber"], bus)
        kit.box(f"sill{s}", (0.14, L - 2, 0.04), (s * (W - 0.05), (YF + YB) / 2 + 1, win_lo - 0.01), M["frame"], bus)
        for i in range(8):
            ay = -4.6 + i * 1.45
            kit.box(f"ad{s}.{i}", (0.03, 1.3, 0.34), (s * (W - 0.13), ay, CEIL - 0.26), M["ad"], bus,
                    rot=(0, s * 0.62, 0))
            kit.box(f"adf{s}.{i}", (0.02, 1.38, 0.42), (s * (W - 0.11), ay, CEIL - 0.25), M["frame"], bus,
                    rot=(0, s * 0.62, 0))
        for wy in (-4.6, 4.0):
            kit.box(f"wheel{s}.{wy}", (0.34, 1.0, 1.0), (s * (W + 0.05), wy, 0.1), M["tyre"], bus,
                    rot=(0, math.pi / 2, 0))
            kit.cyl(f"hub{s}.{wy}", 0.28, 0.36, (s * (W + 0.07), wy, 0.1), M["frame"], bus, rot=(0, math.pi / 2, 0), n=18)
            kit.cyl(f"tyrec{s}.{wy}", 0.5, 0.32, (s * (W + 0.06), wy, 0.1), M["tyre"], bus, rot=(0, math.pi / 2, 0), n=24)

    # ---- the middle door: two glass leaves, closed, a yellow step edge and a red stop-request bar
    for k, (a, b) in enumerate(((MID_DOOR[0], sum(MID_DOOR) / 2), (sum(MID_DOOR) / 2, MID_DOOR[1]))):
        kit.box(f"mdoor{k}.glass", (0.02, b - a - 0.05, 1.85), (W + 0.1, (a + b) / 2, 1.12), M["partition"], bus)
        kit.box(f"mdoor{k}.frame", (0.06, b - a, 0.08), (W + 0.1, (a + b) / 2, 2.08), M["rubber"], bus)
        kit.box(f"mdoor{k}.frame2", (0.06, b - a, 0.1), (W + 0.1, (a + b) / 2, 0.15), M["rubber"], bus)
        kit.box(f"mdoor{k}.edge", (0.06, 0.05, 1.95), (W + 0.1, b - 0.03 if k == 0 else a + 0.03, 1.12), M["rubber"], bus)
    kit.box("mdoor.step", (0.4, MID_DOOR[1] - MID_DOOR[0], 0.03), (W - 0.2, sum(MID_DOOR) / 2, 0.015), M["yellow"], bus)
    kit.box("mdoor.header", (0.14, MID_DOOR[1] - MID_DOOR[0] + 0.1, 0.12), (W + 0.02, sum(MID_DOOR) / 2, 2.15), M["frame"], bus)
    kit.box("mdoor.bar", (0.04, 0.5, 0.06), (W - 0.05, sum(MID_DOOR) / 2, 1.5), M["red"], bus, bevel=0.01)

    # ---- the rear: wall, window (with its condensation film), back bench of five places
    kit.box("rear.low", (2 * W + 0.2, 0.08, 1.38), (0, YB, 0.69), M["wall_low"], bus)
    kit.box("rear.up", (2 * W + 0.2, 0.08, 0.42), (0, YB, CEIL - 0.2), M["wall_in"], bus)
    for s in (-1, 1):
        kit.box(f"rear.side{s}", (0.42, 0.08, 1.0), (s * (W - 0.2), YB, 1.88), M["wall_in"], bus)
    kit.box("rear.glass", (2 * W - 0.75, 0.02, 1.0), (0, YB + 0.02, 1.88), M["glass"], bus)
    cond, fog_v = condensation_mat(kit, pil_image("handprint", handprint_image()))
    uv_plane(kit, "rear.fog", (2 * W - 0.78, 1.0), (0, YB - 0.005, 1.88), cond, bus)
    ctx["condensation"] = fog_v
    kit.box("rear.gasket", (2 * W - 0.7, 0.06, 0.04), (0, YB - 0.02, 1.38), M["rubber"], bus)
    kit.box("rear.out", (2 * W + 0.36, 0.1, 1.45), (0, YB + 0.1, 0.65), M["paint"], bus, bevel=0.05)
    for s in (-1, 1):
        kit.box(f"tail{s}", (0.22, 0.04, 0.4), (s * (W - 0.05), YB + 0.16, 0.95), M["tail"], bus)
    for k, bx in enumerate(BENCH_X):
        if k == 2:
            dent_cushion(kit, "bench.dent", bx, 5.95, BENCH_TOP, 0.8, 0.55, dent_vinyl(kit), bus)
        else:
            kit.box(f"bench.cush{k}", (0.8, 0.55, 0.14), (bx, 5.95, BENCH_TOP - 0.07), M["seat_back"], bus, bevel=0.05, seg=3)
    kit.box("bench.back", (2 * W - 0.1, 0.12, 0.86), (0, 6.33, PLAT_H + 0.88), M["seat_back"], bus, rot=(-0.1, 0, 0),
            bevel=0.05, seg=3)
    kit.box("bench.base", (2 * W - 0.1, 0.5, 0.33), (0, 6.0, PLAT_H + 0.17), M["shell"], bus, bevel=0.02)
    rod(kit, "bench.rail", (-W + 0.1, 6.42, PLAT_H + 1.38), (W - 0.1, 6.42, PLAT_H + 1.38), 0.022, M["chrome"], bus)

    # ---- seats (the right seat of row 5 is the middle door)
    for i, y in enumerate(ROWS):
        for s in (-1, 1):
            if s > 0 and i == 5:
                continue
            seat_pair(kit, M, f"seat{s}.{i}", s * 1.36, y, bus, M["seat"])
    # ---- poles, ceiling rails, straps, stop buttons
    for s in (-1, 1):
        rod(kit, f"rail{s}", (s * 0.62, -5.4, 2.42), (s * 0.62, PLAT_Y0 + 1.2, 2.42), 0.022, M["chrome"], bus)
        for k in range(6):
            yb = -5.0 + k * 2.0
            rod(kit, f"railb{s}.{k}", (s * 0.62, yb, 2.42), (s * 0.62, yb, CEIL), 0.018, M["chrome"], bus)
        for k in range(16):
            yy = -4.9 + k * 0.62
            kit.box(f"strap{s}.{k}", (0.035, 0.018, 0.22), (s * 0.62, yy, 2.31), M["rubber"], bus)
            kit.box(f"handle{s}.{k}", (0.11, 0.03, 0.035), (s * 0.62, yy, 2.19), M["yellow"], bus, bevel=0.01)
            for hx in (-1, 1):
                kit.box(f"handles{s}.{k}.{hx}", (0.025, 0.03, 0.09), (s * 0.62 + hx * 0.045, yy, 2.225), M["yellow"],
                        bus, rot=(0, hx * 0.5, 0))
    # the one strap over the back row's middle seat, on a crossbar: it swings when nothing else does
    rod(kit, "crossbar", (-0.62, 5.35, 2.42), (0.62, 5.35, 2.42), 0.02, M["chrome"], bus)
    piv = kit.empty("swing", (0.0, 5.35, 2.42), bus)
    kit.box("swing.strap", (0.035, 0.018, 0.22), (0, 0, -0.11), M["rubber"], piv)
    kit.box("swing.handle", (0.11, 0.03, 0.035), (0, 0, -0.23), M["yellow"], piv, bevel=0.01)
    for hx in (-1, 1):
        kit.box(f"swing.h{hx}", (0.025, 0.03, 0.09), (hx * 0.045, 0, -0.195), M["yellow"], piv, rot=(0, hx * 0.5, 0))
    ctx["swing"] = piv
    for i, y in enumerate(ROWS):
        if i % 2 == 0:
            for s in (-1, 1):
                rod(kit, f"pole{s}.{i}", (s * 0.6, y + 0.45, 0.0), (s * 0.6, y + 0.45, 2.42), 0.026, M["yellow"], bus)
                kit.box(f"btn{s}.{i}", (0.07, 0.07, 0.09), (s * 0.6 - s * 0.03, y + 0.45, 1.28), M["red"], bus, bevel=0.015)
    for s in (-1, 1):
        rod(kit, f"pole.back{s}", (s * 0.7, PLAT_Y0 - 0.05, 0.0), (s * 0.7, PLAT_Y0 - 0.05, 2.42), 0.026, M["yellow"], bus)

    # ---- fluorescent tubes
    for s in (-1, 1):
        for k in range(10):
            ty = -5.0 + k * 1.2
            back = ty > PLAT_Y0 - 0.3
            kit.box(f"tubeh{s}.{k}", (0.3, 1.16, 0.06), (s * 0.95, ty, CEIL - 0.03), M["frame"], bus, bevel=0.01)
            kit.box(f"tube{s}.{k}", (0.2, 1.08, 0.035), (s * 0.95, ty, CEIL - 0.07), M["tube_b" if back else "tube_f"], bus,
                    bevel=0.01)
            nm = f"tubeL{s}.{k}"
            kit.light(nm, "AREA", (s * 0.95, ty, CEIL - 0.1), 13.0 if back else 26.0, "#dff6e8", size=1.05, parent=bus)
            ld = kit.LIGHTS[nm]["light"]
            ld.shape = "RECTANGLE"
            ld.size = 1.05
            ld.size_y = 0.18
            (ctx["lights_back"] if back else ctx["lights_front"]).append(nm)
    kit.light("fill", "AREA", (0, -0.4, CEIL - 0.16), 60.0, "#8fa3b3", size=4.0, parent=bus, shadow=False)
    kit.light("bounce", "AREA", (0, -0.4, 2.15), 35.0, "#c9d6cf", size=4.0, rot=(math.pi, 0, 0), parent=bus, shadow=False)
    LDb = kit.LIGHTS["bounce"]["light"]
    LDb.shape = "RECTANGLE"
    LDb.size, LDb.size_y = 3.0, 11.5
    LDf = kit.LIGHTS["fill"]["light"]
    LDf.shape = "RECTANGLE"
    LDf.size, LDf.size_y = 3.4, 12.0

    # ---- the front: windscreen, dash, wheel, driver's seat, partition, farebox, sign box, mirrors
    kit.box("windscreen", (2 * W + 0.1, 0.03, 1.55), (0, YF - 0.02, 1.62), M["glass"], bus, rot=(0.06, 0, 0))
    kit.box("front.out", (2 * W + 0.36, 0.12, 1.1), (0, YF - 0.06, 0.32), M["paint"], bus, bevel=0.05)
    kit.box("front.band", (2 * W + 0.38, 0.02, 0.17), (0, YF - 0.13, 0.53), M["band"], bus)
    kit.box("bumper", (2 * W + 0.4, 0.22, 0.25), (0, YF - 0.15, -0.12), M["skirt"], bus, bevel=0.06)
    for s in (-1, 1):
        kit.box(f"headl{s}", (0.42, 0.04, 0.2), (s * 1.6, YF - 0.13, 0.2), M["head"], bus, bevel=0.03)
        kit.light(f"headL{s}", "SPOT", (s * 1.6, YF - 0.3, 0.2), 900.0, "#fff1d6", rot=(math.radians(84), 0, 0),
                  spot=45, blend=0.5, size=0.15, parent=bus)
    # the destination display over the windscreen, outside: amber letters, a made-up place and no route number
    # (r1 item 1: N13 was a real London night route)
    dest = text_panel("dest", 1024, 160, [("LANTERN HILL", 104, "#ffb43c", 18)], "#120d08")
    kit.box("dest.box", (2 * W - 0.4, 0.1, 0.3), (0, YF - 0.02, CEIL - 0.1), M["dash"], bus)
    uv_plane(kit, "dest.face", (2 * W - 0.5, 0.25), (0, YF - 0.075, CEIL - 0.1),
             image_mat(kit, "dest", pil_image("dest", dest), emit=3.0), bus)
    side_dest = uv_plane(kit, "dest.side", (1.4, 0.22), (W + 0.19, -4.4, 2.45),
                         kit.MATS["dest"], bus, rot=(0, 0, math.pi / 2))
    kit.box("dash", (2 * W, 0.7, 0.98), (0, YF + 0.35, 0.49), M["dash"], bus, bevel=0.06)
    kit.box("dash.hood", (1.0, 0.4, 0.14), (-1.35, YF + 0.55, 1.03), M["dash"], bus, bevel=0.05)
    for k in range(3):
        kit.box(f"gauge{k}", (0.16, 0.02, 0.1), (-1.6 + k * 0.25, YF + 0.76, 0.95), M["instr"], bus)
    kit.box("ticket.led", (0.3, 0.02, 0.06), (-0.5, YF + 0.72, 1.0), M["amber"], bus)
    wx, wy, wz = WHEEL
    rod(kit, "column", (wx, wy - 0.06, wz - 0.05), (wx, wy + 0.12, 0.6), 0.045, M["dash"], bus)
    torus(kit, "wheel", WHEEL_R, 0.028, (wx, wy, wz), M["dash"], bus, rot=(math.radians(-55), 0, 0), n=36)
    for a in (0, 2.1, 4.2):
        rod(kit, f"spoke{a}", (wx, wy, wz), (wx + WHEEL_R * math.cos(a), wy - WHEEL_R * math.sin(a) * math.sin(math.radians(35)),
            wz + WHEEL_R * math.sin(a) * math.cos(math.radians(35))), 0.015, M["dash"], bus)
    kit.box("drv.cush", (0.82, 0.6, 0.14), (-1.35, -6.25, 0.48), M["drv_seat"], bus, bevel=0.05)
    kit.box("drv.back", (0.82, 0.14, 0.95), (-1.35, -5.9, 1.02), M["drv_seat"], bus, rot=(-0.15, 0, 0), bevel=0.06)
    kit.box("drv.base", (0.4, 0.4, 0.42), (-1.35, -6.25, 0.2), M["frame"], bus, bevel=0.03)
    kit.box("partition.glass", (1.3, 0.02, 1.25), (-1.45, -5.6, 1.2), M["partition"], bus)
    kit.box("partition.frame", (1.36, 0.05, 0.06), (-1.45, -5.6, 1.85), M["frame"], bus)
    kit.box("partition.low", (1.36, 0.05, 0.6), (-1.45, -5.6, 0.3), M["wall_low"], bus)
    rod(kit, "partition.post", (-0.77, -5.6, 0.0), (-0.77, -5.6, 2.42), 0.026, M["yellow"], bus)
    kit.box("farebox", (0.3, 0.3, 1.0), (-0.55, -6.5, 0.5), M["frame"], bus, bevel=0.03)
    kit.box("farebox.top", (0.32, 0.32, 0.1), (-0.55, -6.5, 1.05), M["dash"], bus, bevel=0.02)
    kit.box("farebox.led", (0.12, 0.02, 0.05), (-0.55, -6.34, 0.95), M["amber"], bus)
    kit.box("cabtubeh", (0.3, 0.9, 0.06), (-1.1, -6.4, CEIL - 0.03), M["frame"], bus, bevel=0.01)
    kit.box("cabtube", (0.2, 0.82, 0.035), (-1.1, -6.4, CEIL - 0.07), M["tube_f"], bus, bevel=0.01)
    kit.light("cabL", "AREA", (-1.1, -6.4, CEIL - 0.1), 14.0, "#dff6e8", size=0.8, parent=bus)
    ctx["lights_front"].append("cabL")
    kit.light("dashglow", "AREA", (-1.35, -6.85, 1.08), 10.0, "#7ff0b0", size=0.5, rot=(math.radians(-150), 0, 0),
              parent=bus, shadow=False)
    kit.box("signbox", (2 * W, 0.4, 0.34), (0, YF + 0.2, CEIL - 0.17), M["dash"], bus, bevel=0.03)
    mir = kit.empty("mirror", (0.35, -7.12, 2.3), bus, rot=(math.radians(-8), 0, math.radians(-18)))
    dome = kit.sphere("mirror.dome", 0.3, (0, 0, 0), M["mirror"], mir, seg=32)
    dome.scale = (1.0, 0.28, 0.62)
    rim = torus(kit, "mirror.rim", 0.3, 0.02, (0, 0.0, 0), M["dash"], mir, rot=(math.pi / 2, 0, 0))
    rim.scale = (1.0, 0.62, 1.0)
    kit.box("mirror.back", (0.6, 0.04, 0.38), (0, -0.06, 0), M["dash"], mir, bevel=0.06)
    rod(kit, "mirror.arm", (0.35, -7.18, 2.5), (0.35, -7.2, CEIL), 0.018, M["frame"], bus)
    # the flat rear-view mirror, angled so EYE_CAM sees the driver's eyes in it
    m_, c_, e_ = Vector(EYE_MIRROR), Vector(EYE_CAM), Vector(DRIVER_EYES)
    n_ = ((c_ - m_).normalized() + (e_ - m_).normalized()).normalized()
    em = kit.empty("eyemirror", EYE_MIRROR, bus)
    em.rotation_euler = n_.to_track_quat("Z", "Y").to_euler()
    kit.box("eyemirror.glass", (0.5, 0.17, 0.012), (0, 0, 0.006), M["flatmirror"], em)
    kit.box("eyemirror.back", (0.54, 0.2, 0.04), (0, 0, -0.02), M["dash"], em, bevel=0.015)
    rod(kit, "eyemirror.arm", EYE_MIRROR, (EYE_MIRROR[0], EYE_MIRROR[1] - 0.05, CEIL), 0.014, M["frame"], bus)

    # ---- the front door
    ctx["door"] = []
    for k, (a, b) in enumerate(((DOOR_Y[0], -6.0), (-6.0, DOOR_Y[1]))):
        leaf = kit.empty(f"door{k}", (W + 0.1, (a + b) / 2, 0), bus)
        kit.box(f"door{k}.glass", (0.02, b - a - 0.06, 1.9), (0, 0, 1.15), M["partition"], leaf)
        kit.box(f"door{k}.frame", (0.06, b - a, 0.08), (0, 0, 2.12), M["rubber"], leaf)
        kit.box(f"door{k}.frame2", (0.06, b - a, 0.08), (0, 0, 0.2), M["rubber"], leaf)
        kit.box(f"door{k}.edge", (0.06, 0.05, 1.95), (0, (b - a) / 2 - 0.02, 1.15), M["rubber"], leaf)
        ctx["door"].append((leaf, -1 if k == 0 else 1))
    kit.box("door.header", (0.2, DOOR_Y[1] - DOOR_Y[0], CEIL - 2.18), (W + 0.08, -6.0, (CEIL + 2.18) / 2), M["paint"], bus)
    kit.box("door.step", (0.5, DOOR_Y[1] - DOOR_Y[0], 0.04), (W - 0.2, -6.0, 0.0), M["yellow"], bus)

    # ---- the leak
    lx, ly = -1.25, -1.9
    kit.box("seam", (0.04, 4.2, 0.01), (lx, ly, CEIL - 0.005), M["frame"], bus)
    kit.box("stain", (0.55, 0.8, 0.008), (lx, ly, CEIL - 0.012), M["stain"], bus)
    for k in range(3):
        d = kit.sphere(f"drip{k}", 0.035, (lx, ly, CEIL - 0.05), M["water"], bus, seg=10)
        d.scale = (1, 1, 1.7)
        ctx["drips"].append(d)
    ctx["puddles"] = []
    for k, (px, py, sx, sy, z) in enumerate(((-0.3, -1.7, 0.6, 0.9, 0.004), (0.25, 0.1, 0.5, 0.7, 0.004),
                                              (0.1, -3.6, 0.7, 0.5, 0.004), (-1.3, -1.93, 0.9, 0.35, 0.495),
                                              (1.35, -0.77, 0.8, 0.3, 0.495), (-1.36, 1.53, 0.8, 0.3, 0.495),
                                              (1.36, 2.68, 0.8, 0.3, 0.495), (-1.36, 3.83, 0.8, 0.3, 0.495),
                                              (1.36, 0.38, 0.8, 0.3, 0.495), (-1.36, -0.77, 0.8, 0.3, 0.495))):
        p = kit.cyl(f"puddle{k}", 0.5, 0.004, (px, py, z), M["puddle"], bus, n=24)
        ctx["puddles"].append((p, sx, sy))

    # a phone for rider 4
    kit.box("phone", (0.16, 0.3, 0.02), (0.86, -0.18, 0.98), M["dash"], bus, rot=(math.radians(-40), 0, 0), bevel=0.01)
    scr, _ = emissive(kit, "phone screen", "#9fc6ff", 1.2)
    kit.box("phone.screen", (0.13, 0.26, 0.005), (0.86, -0.175, 0.993), scr, bus, rot=(math.radians(-40), 0, 0))
    ctx["phone"] = [bpy.data.objects["phone"], bpy.data.objects["phone.screen"]]

    # ---- outside: a street that repeats along y and slides past
    street = kit.empty("street")
    ctx["street"] = street
    for c in (-1, 0, 1):
        oy = c * TILE
        kit.box(f"road{c}", (24, TILE, 0.1), (-3.0, oy, -0.45), M["road"], street)
        for k in range(6):
            kit.box(f"dash{c}.{k}", (0.14, 3.0, 0.012), (-2.75, oy - TILE / 2 + 3.5 + k * 7, -0.395), M["line"], street)
        kit.box(f"kerb{c}", (0.25, TILE, 0.2), (3.32, oy, -0.33), M["kerb"], street, bevel=0.03)
        kit.box(f"pave{c}", (6.6, TILE, 0.15), (6.75, oy, -0.33), M["pave"], street)
        kit.box(f"kerbL{c}", (0.25, TILE, 0.2), (-9.3, oy, -0.33), M["kerb"], street, bevel=0.03)
        kit.box(f"paveL{c}", (4.0, TILE, 0.15), (-11.4, oy, -0.33), M["pave"], street)
        for k in range(2):
            ly2 = oy - TILE / 4 + k * TILE / 2
            streetlight(kit, M, f"sl{c}.{k}", 3.75, ly2, street, -1)
            ctx["street_lights"].append(f"sl{c}.{k}.L")
            streetlight(kit, M, f"slL{c}.{k}", -9.6, ly2 + 10, street, 1)
            ctx["street_lights"].append(f"slL{c}.{k}.L")
        for k in range(3):
            by = oy - TILE / 2 + 7 + k * 14
            building(kit, M, f"bR{c}.{k}", 10.1, by, 8, 12.6, 9 + 4 * kit.hash01(c, k, 1), 1, street, c * 31 + k)
            building(kit, M, f"bL{c}.{k}", -13.4, by + 5, 8, 12.6, 10 + 5 * kit.hash01(c, k, 2), -1, street, c * 17 + k + 5)
    build_stop(kit, M, ctx, lamp_e)

    for nm, L_ in kit.LIGHTS.items():
        try:
            L_["obj"].visible_camera = False
        except Exception:
            pass
    # the creature's rim lights (placed every frame from its pose): cold, from behind, so black reads on black
    for k in range(2):
        kit.light(f"rim{k}", "AREA", (0, 6.4, 2.6), 0.0, "#a9c8ff", size=0.8, parent=None, shadow=True)
        kit.LIGHTS[f"rim{k}"]["obj"].visible_camera = False
    ctx["rim_energy"] = 140.0
    # a cold light low in front of the back row, for the head's close-ups (S41 to S46): lit from below
    kit.light("under", "AREA", (-0.25, 5.15, 0.75), 0.0, "#b8cce0", size=0.35, parent=None, shadow=True)
    kit.LIGHTS["under"]["base"] = UNDER_ENERGY
    kit.light("sideL", "AREA", (0, 0, 1), 0.0, "#d6e0ea", size=0.25, parent=None, shadow=True)   # a shot's raking light
    kit.LIGHTS["sideL"]["obj"].visible_camera = False
    for k in range(2):
        kit.light(f"handL{k}", "AREA", (0, 0, 1), 0.0, "#c4d2e2", size=0.3, parent=None, shadow=True)
        kit.LIGHTS[f"handL{k}"]["base"] = 5.0
        kit.LIGHTS[f"handL{k}"]["obj"].visible_camera = False
    ob = kit.LIGHTS["under"]["obj"]
    ob.rotation_euler = (Vector((0.0, 6.0, 2.05)) - Vector(ob.location)).to_track_quat("-Z", "Y").to_euler()
    kit.LIGHTS["under"]["obj"].visible_camera = False
    return ctx


def build_stop(kit, M, ctx, lamp_e):
    """The stop: a lit shelter with a timetable and a poster, the route flag, a real streetlamp whose light the
    fog catches (a volume cone that only exterior shots show), a bin, wet kerb puddles, and a lit shopfront.
    All the words are made up."""
    stop = kit.empty("stop")
    ctx["stop"] = stop
    sx0, sy = 4.4, -2.6     # the shelter's kerb-side posts
    kit.box("shel.pad", (3.2, 5.0, 0.04), (sx0 + 1.4, sy, -0.24), M["kerb"], stop)
    glassm = kit.glass("#d8e4e6", name="shelter glass")
    kit.box("shel.back", (0.02, 4.2, 2.0), (sx0 + 2.4, sy, 0.8), glassm, stop)
    kit.box("shel.side", (2.3, 0.02, 2.0), (sx0 + 1.25, sy - 2.08, 0.8), glassm, stop)
    kit.box("shel.roof", (2.8, 4.5, 0.1), (sx0 + 1.25, sy, 1.95), M["shelter"], stop, bevel=0.03)
    kit.box("shel.fascia", (0.08, 4.5, 0.22), (sx0 - 0.12, sy, 1.88), M["shelter"], stop)
    for py in (sy - 2.08, sy + 2.08):
        for px in (sx0 + 0.1, sx0 + 2.4):
            rod(kit, f"shel.post{px}.{py}", (px, py, -0.25), (px, py, 1.92), 0.045, M["shelter"], stop, n=10)
    kit.box("shel.bench", (0.42, 2.6, 0.06), (sx0 + 2.05, sy + 0.4, 0.22), M["shelter"], stop)
    # the fascia's name strip (blank), a dim empty poster frame and a timetable with no words, only unreadable
    # rows (r1 item 2: the fewer the signs, the fewer half-words in frame)
    name = text_panel("stopname", 1024, 128, [], "#1d3f49")
    uv_plane(kit, "shel.name", (2.2, 0.2), (sx0 - 0.17, sy, 1.88), image_mat(kit, "stopname", pil_image("stopname", name),
             emit=1.2), stop, rot=(0, 0, -math.pi / 2))
    poster = blank_panel(512, 900, "#2b3236", "#384147")
    uv_plane(kit, "shel.poster", (1.05, 1.75), (sx0 + 2.37, sy - 1.3, 0.95),
             image_mat(kit, "poster", pil_image("poster", poster), emit=0.35), stop, rot=(0, 0, -math.pi / 2))
    kit.box("shel.posterbox", (0.12, 1.2, 1.9), (sx0 + 2.44, sy - 1.3, 0.95), M["shelter"], stop)
    table = timetable_panel(512, 700, "#16323b")
    uv_plane(kit, "shel.table", (0.7, 0.95), (sx0 + 2.37, sy + 1.4, 1.2),
             image_mat(kit, "timetable", pil_image("timetable", table), emit=0.9), stop, rot=(0, 0, -math.pi / 2))
    kit.light("shel.L", "AREA", (sx0 + 1.3, sy, 1.86), 55.0, "#dfe9ff", size=1.6, rot=(0, 0, 0), parent=stop)
    # the route flag at the kerb
    rod(kit, "flag.pole", (3.75, -5.3, -0.25), (3.75, -5.3, 2.75), 0.04, M["pole"], stop)
    flag = text_panel("flag", 512, 700, [("LANTERN", 104, "#ffffff", 200), ("HILL", 104, "#ffffff", 330)], "#1d3f49")
    fm = image_mat(kit, "flag", pil_image("flag", flag), emit=0.6)
    for k, ry in enumerate((math.pi / 2, -math.pi / 2)):
        uv_plane(kit, f"flag.face{k}", (0.5, 0.68), (3.75 + (0.016 if k == 0 else -0.016), -5.3, 2.3), fm, stop,
                 rot=(0, 0, ry))
    kit.box("flag.edge", (0.03, 0.52, 0.7), (3.75, -5.3, 2.3), M["shelter"], stop)
    # the streetlamp: a tall pole, an arm over the kerb, a lit head, and its light caught in the fog
    lx, ly = 3.9, -9.2
    rod(kit, "lamp.pole", (lx + 0.4, ly, -0.25), (lx + 0.4, ly, 6.2), 0.09, M["pole"], stop, n=14)
    rod(kit, "lamp.arm", (lx + 0.4, ly, 6.1), (lx - 1.0, ly, 6.35), 0.05, M["pole"], stop, n=10)
    kit.box("lamp.head", (0.8, 0.36, 0.18), (lx - 1.1, ly, 6.3), M["pole"], stop, bevel=0.05)
    kit.box("lamp.lens", (0.66, 0.28, 0.03), (lx - 1.1, ly, 6.2), M["lamp"], stop)
    kit.light("lamp.L", "SPOT", (lx - 1.1, ly, 6.1), 4200.0, "#ffc887", spot=62, blend=0.45, size=0.25, parent=stop)
    kit.LIGHTS["lamp.L"]["obj"].rotation_euler = (math.radians(8), math.radians(-10), 0)
    kit.light("lamp.glow", "POINT", (lx - 1.1, ly, 5.9), 120.0, "#ffc887", size=0.6, parent=stop, shadow=False)
    halo = kit.sphere("lamp.halo", 0.9, (lx - 1.1, ly, 6.15), glow_cone_mat(kit, "#ffcf96", 0.35), stop, seg=20)
    vol = kit._new("lamp fog")
    vn = vol.node_tree.nodes
    vn.remove(vn["Principled BSDF"])
    pv = vn.new("ShaderNodeVolumePrincipled")
    pv.inputs["Density"].default_value = 0.035
    pv.inputs["Color"].default_value = kit.col("#d6dbe0")
    pv.inputs["Anisotropy"].default_value = 0.35
    vout = next(n for n in vn if n.type == "OUTPUT_MATERIAL")
    vol.node_tree.links.new(pv.outputs[0], vout.inputs["Volume"])
    fogbox = kit.box("ext.fog", (12.0, 26.0, 7.5), (4.5, -4.0, 3.4), vol, stop)
    ctx["ext_only"] = [fogbox]
    for ob in (halo,):
        for attr in ("visible_shadow", "visible_diffuse", "visible_glossy", "visible_transmission"):
            try:
                setattr(ob, attr, False)
            except Exception:
                pass
    # a bin, puddles that catch the lamp, a shopfront with a lit sign behind the shelter
    kit.cyl("bin", 0.26, 0.85, (sx0 + 0.3, sy - 2.6, 0.18), M["bin"], stop, n=18)
    kit.cyl("bin.lid", 0.28, 0.06, (sx0 + 0.3, sy - 2.6, 0.62), M["shelter"], stop, n=18)
    for k, (px, py, r) in enumerate(((3.8, -7.4, 0.9), (4.2, -3.9, 0.6), (5.3, 0.8, 0.7), (1.2, -10.5, 1.4), (0.2, -3.0, 1.1))):
        p = kit.cyl(f"spud{k}", r, 0.004, (px, py, -0.245 if px > 3.4 else -0.395), M["puddle"], stop, n=24)
        p.scale = (1.0, 1.6, 1.0)
    kit.box("shop.wall", (0.3, 9.0, 4.2), (9.95, -3.0, 1.85), M["facade"], stop)
    kit.box("shop.win", (0.05, 4.6, 1.9), (9.78, -2.6, 0.95), kit.MATS.get("window warm") or M["win_warm"], stop)
    kit.box("shop.mull", (0.06, 0.08, 1.9), (9.76, -2.6, 0.95), M["dash"], stop)
    # the shop's sign is lit but blank: it's cropped mid-word in the wide exteriors (r1 item 2)
    sign = blank_panel(1024, 200, "#16323a", "#1f4a55")
    uv_plane(kit, "shop.sign", (4.8, 0.85), (9.76, -2.6, 2.45), image_mat(kit, "shopsign", pil_image("shopsign", sign),
             emit=4.0), stop, rot=(0, 0, -math.pi / 2))
    kit.light("shop.L", "AREA", (9.4, -2.6, 1.2), 160.0, "#ffcf8f", size=3.0, rot=(0, math.radians(-90), 0), parent=stop)
    return stop


def halo_mat(kit, hexc, strength):
    """A soft glow sprite: bright where it faces the camera, gone at its rim."""
    m = kit._new(f"halo {hexc}")
    nt = m.node_tree
    N, L = nt.nodes, nt.links
    N.remove(N["Principled BSDF"])
    out = next(n for n in N if n.type == "OUTPUT_MATERIAL")
    lw = N.new("ShaderNodeLayerWeight")
    lw.inputs["Blend"].default_value = 0.5
    inv = N.new("ShaderNodeMath")
    inv.operation = "SUBTRACT"
    inv.inputs[0].default_value = 1.0
    L.new(lw.outputs["Facing"], inv.inputs[1])
    pw = N.new("ShaderNodeMath")
    pw.operation = "POWER"
    pw.inputs[1].default_value = 4.0
    L.new(inv.outputs[0], pw.inputs[0])
    e = N.new("ShaderNodeEmission")
    e.inputs["Color"].default_value = kit.col(hexc)
    e.inputs["Strength"].default_value = strength
    tr = N.new("ShaderNodeBsdfTransparent")
    mix = N.new("ShaderNodeMixShader")
    L.new(pw.outputs[0], mix.inputs[0])
    L.new(tr.outputs[0], mix.inputs[1])
    L.new(e.outputs[0], mix.inputs[2])
    add = N.new("ShaderNodeAddShader")
    L.new(mix.outputs[0], add.inputs[0])
    tr2 = N.new("ShaderNodeBsdfTransparent")
    sc = N.new("ShaderNodeMixShader")
    L.new(pw.outputs[0], sc.inputs[0])
    L.new(tr2.outputs[0], sc.inputs[1])
    blk = N.new("ShaderNodeEmission")
    blk.inputs["Strength"].default_value = 0.0
    L.new(blk.outputs[0], sc.inputs[2])
    L.new(mix.outputs[0], out.inputs["Surface"])
    try:
        m.emission_sampling = "NONE"
        m.blend_method = "BLEND"
    except Exception:
        pass
    return m


# ------------------------------------------------------------------------------------------- the creature
#
# The grey passenger itself (owner, 2026-10-30: "Grey guy only"; note 18, "Uncanny beats tentacles"). It's the
# same R6 rig as every rider, in a long grey coat with the collar up and the pale blank head with its seam. What's
# wrong with it is its proportions: a torso a head too long, legs that make it far too tall when it stands, its own
# block arms far too long, and big square hands. It never moves on screen: each "creature" cue is a new still pose
# that the story only ever reaches in the dark.

RIG_U = 0.34 * 1.25     # metres per rig unit at its height (rig.S x its "height")
TALL_TORSO = 1.15       # always: sitting, it's a head taller than anyone
ARM_U = 1.75            # rig units from the shoulder pivot to the end of the arm


def build_creature(kit, ctx):
    """The disguise and the wrong proportions, built once on the passenger rig."""
    torso = bpy.data.objects["passenger.torso"]
    coat = bpy.data.objects["passenger.torsom"].active_material
    skin = bpy.data.objects["passenger.skinarm1"].active_material
    lift = 2.0 * (TALL_TORSO - 1)            # rig units the torso grew
    for ch in list(torso.children):
        if ch.name == "passenger.torsom":
            ch.scale.z *= TALL_TORSO
            ch.location.z *= TALL_TORSO
        else:
            ch.location.z += lift
    for sx in (-1, 1):   # a long coat over the thighs
        leg = bpy.data.objects[f"passenger.leg{sx}"]
        kit.box(f"coat.skirt{sx}", (1.08, 1.1, 1.25), (0, 0, -0.6), coat, leg, bevel=0.06)
    top = 2.0 * TALL_TORSO
    kit.box("coat.collarb", (1.7, 0.2, 0.85), (0, 0.42, top + 0.3), coat, torso, rot=(-0.18, 0, 0), bevel=0.06)
    for sx in (-1, 1):
        kit.box(f"coat.collar{sx}", (0.2, 0.75, 0.62), (sx * 0.84, 0.1, top + 0.2), coat, torso, rot=(0, sx * 0.16, 0),
                bevel=0.05)
        kit.box(f"coat.lapel{sx}", (0.55, 0.1, 0.9 * TALL_TORSO), (sx * 0.42, -0.52, top - 0.6), coat, torso,
                rot=(0, sx * -0.35, 0), bevel=0.03)
    hands = {}
    for sx in (-1, 1):
        hands[sx] = kit.box(f"creature.hand{sx}", (HAND, HAND * 0.42, HAND), (0, 0, 0), skin, None, bevel=0.03)
    ctx["hands"] = hands
    m = bpy.data.materials.get("head passenger")
    if m is not None:
        b = m.node_tree.nodes.get("Principled BSDF")
        b.inputs["Roughness"].default_value = 0.42
        for k, v in (("Coat Weight", 0.18), ("Coat Roughness", 0.2), ("Specular IOR Level", 0.3)):
            if k in b.inputs:
                b.inputs[k].default_value = v
    ctx["creature"] = True


V = Vector
CEIL_Z = CEIL - 0.03

# Its standing poses. loc is where its feet are (x, y, floor z); yaw faces it (0 faces the front, -y); legs is its
# leg length against a rider's; bend tips it forward at the waist (degrees); head is (yaw, pitch) on its neck;
# arms are (left, right): a world point the hand reaches to (the arm stretches to it, up to ARM_MAX), or a hanging
# (forward degrees, length) pair. A cue can move any of them: {"name": "creature", "pose": p, "y": .., "head": ..}.
ARM_MAX = 4.6
POSES = {
    # standing at the back of the aisle, far too tall: bent double, its head pressed up under the ceiling, its arms
    # hanging past its knees
    "stand": {"loc": (0.0, 5.1, PLAT_H), "yaw": 0.0, "legs": 1.62, "bend": 34.0, "head": (0.0, 22.0),
              "arms": (("hang", 2.05), ("hang", 2.1))},
    # its arms gone long, reaching halfway down the aisle to the next poles
    "reach": {"loc": (0.0, 3.3, 0.0), "yaw": 0.0, "legs": 2.25, "bend": 76.0, "head": (0.0, -76.0),
              "arms": ((-0.6, 0.85, 1.45), (0.6, 0.85, 1.6))},
    # its hands come down the poles toward me
    "poles": {"loc": (0.0, -0.2, 0.0), "yaw": 0.0, "legs": 2.25, "bend": 78.0, "head": (0.0, -70.0),
              "arms": ((-0.6, -3.75, 1.0), (0.6, -3.75, 1.2))},
    # a pole closer: its hands on the next poles down the aisle
    "pole2": {"loc": (0.0, 1.0, 0.0), "yaw": 0.0, "legs": 2.25, "bend": 76.0, "head": (0.0, -76.0),
              "arms": ((-0.6, -1.45, 1.3), (0.6, -1.45, 1.45))},
    # one hand on the driver's mirror, the other gripping the front pole
    "mirror": {"loc": (0.15, -2.6, 0.0), "yaw": 0.0, "legs": 2.25, "bend": 78.0, "head": (0.0, -78.0),
               "arms": ((-0.6, -3.75, 1.25), (0.33, -6.98, 2.3))},
    # right behind me, folded down so its head is beside mine, a gap kept; its hands on a pole and the rail, never
    # on anyone
    "behind": {"loc": (0.3, -3.85, 0.0), "yaw": 0.0, "legs": 1.75, "bend": 108.0, "head": (0.0, -108.0), "neck": 0.55,
               "arms": ((-0.6, -3.75, 1.55), (0.6, -3.75, 1.35))},
    # the same, its hands let go: the long arms hanging still, its head low
    "behind_hang": {"loc": (0.3, -3.85, 0.0), "yaw": 0.0, "legs": 1.75, "bend": 108.0, "head": (0.0, -96.0),
                    "neck": 0.55, "arms": (("hang", 1.3), ("hang", 1.35))},
    # standing at the front, bent double, its head turned all the way round to watch me walk back
    "watch": {"loc": (0.3, -3.9, 0.0), "yaw": 0.0, "legs": 1.98, "bend": 34.0, "head": (180.0, 22.0),
              "arms": (("hang", 2.0), ("hang", 2.05))},
}


def creature_cue(tl, t):
    """The creature cue in force at t (a dict with "pose"), or the default hidden one."""
    cur = {"pose": "hidden", "t": 0.0}
    for c in sorted((c for c in tl["cues"] if c["name"] == "creature"), key=lambda c: c["t"]):
        if c["t"] <= t + 1e-9:
            cur = c
    return cur


def _aim_arm(arm, torso, target):
    """Point an arm (its local -z) at a world point and stretch it so its end lands there. Returns the stretch."""
    bpy.context.view_layer.update()
    loc = torso.matrix_world.inverted() @ V(target)
    d = loc - arm.location
    arm.rotation_euler = d.to_track_quat("-Z", "Y").to_euler()
    k = max(1.0, min(ARM_MAX, (d.length - HAND / RIG_U * 0.5) / ARM_U))
    arm.scale = (1.0, 1.0, k)
    return k


def _place_hands(ctx, pas):
    """The square hands on the ends of the arms, square to them, whatever their stretch."""
    bpy.context.view_layer.update()
    for sx, h in ctx["hands"].items():
        arm = bpy.data.objects[f"passenger.arm{sx}"]
        M = arm.matrix_world
        end = M @ V((0, 0, -ARM_U))
        down = (M.to_3x3() @ V((0, 0, -1))).normalized()
        h.location = end + down * HAND * 0.45
        h.rotation_euler = M.to_3x3().normalized().to_euler()
        h.hide_render = pas.hide_render


def pose_creature(kit, tl, t, ctx):
    pas = bpy.data.objects.get("passenger")
    if pas is None:
        return {}
    cue = creature_cue(tl, t)
    spec = POSES.get(cue.get("pose"))
    torso = bpy.data.objects["passenger.torso"]
    neck = bpy.data.objects["passenger.neck"]
    legs = [bpy.data.objects[f"passenger.leg{sx}"] for sx in (-1, 1)]
    arms = {sx: bpy.data.objects[f"passenger.arm{sx}"] for sx in (-1, 1)}
    headp = bpy.data.objects["passenger.head"]
    headp.location = (0, 0, 0)
    torso.rotation_euler = (0, 0, 0)
    for leg in legs:
        leg.scale = (1, 1, 1)
    for arm in arms.values():
        arm.scale = (1, 1, 1)
    if spec is not None and not pas.hide_render:
        spec = {**spec, **{k: cue[k] for k in ("loc", "yaw", "legs", "bend", "head", "arms", "neck") if k in cue}}
        x, y, z = spec["loc"]
        if "x" in cue:
            x = cue["x"]
        if "y" in cue:
            y = cue["y"]
        k = spec["legs"]
        pas.location = (x, y, z + (k - 1) * 2.0 * RIG_U)     # the hips rise with the long legs; the feet stay down
        pas.rotation_euler = (0, 0, math.radians(spec["yaw"]))
        for leg in legs:
            leg.rotation_euler = (0, 0, 0)
            leg.scale = (1, 1, k)
        torso.rotation_euler = (math.radians(spec["bend"]), 0, 0)
        hy, hp = spec["head"]
        neck.rotation_euler = (math.radians(hp), 0, math.radians(hy))
        headp.location = (0, 0, spec.get("neck", 0.0))     # a neck stretched too long, the head lifted off it
        for sx, a in zip((-1, 1), spec["arms"]):
            arm = arms[sx]
            if a[0] == "hang":   # straight down from the shoulder, this many metres
                bpy.context.view_layer.update()
                sh = arm.matrix_world.translation
                _aim_arm(arm, torso, (sh.x, sh.y - 0.12, sh.z - a[1]))
            else:
                _aim_arm(arm, torso, a)
    elif not pas.hide_render and "head" in cue:   # sitting: only its head is set by the cue
        hy, hp = cue["head"]
        neck.rotation_euler = (math.radians(hp), 0, math.radians(hy))
    if "hand" in cue and not pas.hide_render:      # sitting, one hand put somewhere: the window, the seat beside it
        side, target = cue["hand"]
        _aim_arm(arms[side], torso, target)
    for ob in pas.children_recursive:   # the coat parts built after the rig follow its hidden state too
        ob.hide_render = pas.hide_render
    _place_hands(ctx, pas)
    bpy.context.view_layer.update()
    head = bpy.data.objects["passenger.headm"].matrix_world.translation.copy()
    return {"visible": 0 if pas.hide_render else 1, "pose": cue.get("pose"), "head": head}

# ------------------------------------------------------------------------------------------------- animate

NIGHTS = {  # rain on the glass, fog density, condensation on the rear window
    "A": (0.55, 0.055, 0.0),   # the rule (the opening nights)
    "B": (0.3, 0.075, 0.0),    # the dent and the strap
    "C": (0.0, 0.035, 0.0),    # the long-haired guy: a dry, clear night
    "D": (0.08, 0.11, 1.0),    # the handprint: cold and misty, the back window fogged
    "E": (0.45, 0.06, 0.0),    # the night I'm the only rider
    "F": (1.0, 0.06, 0.0),     # the pour
    "G": (0.2, 0.09, 0.0),     # the next night
}


def _cue(tl, name, default=None):
    for c in tl["cues"]:
        if c["name"] == name:
            return c["t"]
    return default


def _cues(tl, name):
    return sorted((c for c in tl["cues"] if c["name"] == name), key=lambda c: c["t"])


def _shot(tl, t):
    return next((s for s in tl["shots"] if s["start"] <= t < s["end"]), tl["shots"][-1])


def _ss(x):
    x = min(1.0, max(0.0, x))
    return x * x * (3 - 2 * x)


def _switch(keys, attr, t, default):
    v = default
    for k in keys:
        if attr in k and k["t"] <= t + 1e-9:
            v = k[attr]
    return v


def stops(tl):
    st = [c["t"] for c in _cues(tl, "stop")]
    go = [c["t"] for c in _cues(tl, "go")]
    out = []
    for s in st:
        g = next((x for x in go if x > s), 1e9)
        out.append((s, g))
    return out


def speed(tl, t):
    v = SPEED
    for s, g in stops(tl):
        if s <= t < g:
            return 0.0
        if 0 <= s - t < 2.2:
            v *= _ss((s - t) / 2.2)
        if 0 <= t - g < 2.5:
            v *= _ss((t - g) / 2.5)
    return v


def offsets(tl, ctx):
    """Metres the street has slid past, at every frame (cached)."""
    if "dtab" not in ctx:
        fps, n = tl["fps"], tl["frames"] + 2
        tab, d = [], 0.0
        for f in range(n):
            tab.append(d)
            d += speed(tl, f / fps) / fps
        ctx["dtab"] = tab
    return ctx["dtab"]


def street_offset(tl, ctx, t):
    tab = offsets(tl, ctx)
    f = t * tl["fps"]
    i = min(len(tab) - 2, max(0, int(f)))
    return tab[i] + (tab[i + 1] - tab[i]) * (f - i)


def nearest_stop(tl, t):
    sts = stops(tl)
    if not sts:
        return None
    return min(sts, key=lambda sg: 0 if sg[0] <= t < sg[1] else min(abs(t - sg[0]), abs(t - sg[1])))


HORROR_BACK = 0.45    # the back tubes' share in the horror (tuned on the stills for a mean luma of 35 to 45)
HORROR_RIM = 0.55     # the rim lights on the creature in the dark
HORROR_UNDER = 3.0    # its head lit from below in the dark (UNDER_ENERGY times this)
UNDER_ENERGY = 4.0
FLICKER_LO, FLICKER_HI = 0.40, 0.65   # the failing back tube swims between these and is never off (r1 item 5)


def flicker(kit, t):
    """The failing back tube: a slow uneven swim between FLICKER_LO and FLICKER_HI, no dropouts, so no frame
    of it is a flash on its own."""
    u = 0.5 + 0.5 * kit.noise1(t, 5, 7.0)
    return FLICKER_LO + (FLICKER_HI - FLICKER_LO) * min(1.0, max(0.0, u))


def back_gain(kit, tl, t, always=False):
    """The tubes over the back row: failing while "flicker" is on (or `always`), down to a drop's `gain` (default a
    near-blackout) on every "drop", else steady."""
    for c in _cues(tl, "drop"):
        d = c.get("dur", 0.14)
        if c["t"] <= t < c["t"] + d:
            g = c.get("gain", 0.02)
            if g > 0.05:   # a dip, not a cut: eased down and back up over its length
                u = (t - c["t"]) / d
                return 1.0 - (1.0 - g) * math.sin(math.pi * u) * (flicker(kit, t) if always else 1.0)
            return g
    on = _switch(_cues(tl, "flicker"), "on", t, True)
    if on or always:
        return flicker(kit, t)
    return 1.0


def fog_nodes(ctx):
    """Every material's fog-density node (kit._fogged's MULTIPLY by -density), so the weather can change it."""
    if "fog_nodes" not in ctx:
        out = []
        for m in bpy.data.materials:
            if not m.use_nodes:
                continue
            for nd in m.node_tree.nodes:
                if nd.type == "MATH" and nd.operation == "MULTIPLY" and not nd.inputs[1].is_linked \
                        and nd.inputs[0].is_linked and nd.inputs[0].links[0].from_node.type == "MATH" \
                        and nd.inputs[0].links[0].from_node.operation == "MAXIMUM":
                    out.append(nd)
        ctx["fog_nodes"] = out
    return ctx["fog_nodes"]


def driver_grip(kit, ctx):
    """Both of the driver's hands on the wheel rim, whatever his torso and head are doing."""
    bus = ctx["bus"]
    wx, wy, wz = WHEEL
    bpy.context.view_layer.update()
    for sx in (-1, 1):
        arm = bpy.data.objects.get(f"driver.arm{sx}")
        if arm is None:
            return
        a = math.radians(-55)
        rim = V((wx + sx * WHEEL_R * 0.93, wy + 0.02, wz + 0.04))
        tgt = bus.matrix_world @ rim
        par = arm.parent
        loc = par.matrix_world.inverted() @ tgt
        d = loc - arm.location
        arm.rotation_euler = d.to_track_quat("-Z", "Y").to_euler()


def animate(kit, story, tl, t, ctx):
    if not ctx.get("creature"):
        build_creature(kit, ctx)
    shot = _shot(tl, t)["id"]
    ext = shot in set(story.get("exterior_shots", []))
    over = {}
    # ---- the bus and the street
    d = street_offset(tl, ctx, t)
    ns = nearest_stop(tl, t)
    d_stop = street_offset(tl, ctx, ns[0]) if ns else 0.0
    bus_y = 0.0
    if ext:
        if abs(d - d_stop) > 30:   # no stop near: the street stands still and the bus drives through the shot
            sh = _shot(tl, t)
            d_stop = street_offset(tl, ctx, (sh["start"] + sh["end"]) / 2)
        bus_y = -(d - d_stop)
        d = d_stop
    ctx["street"].location.y = (d + TILE / 2) % TILE - TILE / 2
    ctx["stop"].location.y = d - d_stop
    vis = abs(d - d_stop) < 45
    for ob in [ctx["stop"]] + list(ctx["stop"].children_recursive):
        ob.hide_render = not vis
    for ob in ctx["ext_only"]:
        ob.hide_render = not (ext and vis)
    v = speed(tl, t)
    sway = (0.0035 * math.sin(2 * math.pi * 0.33 * t) + 0.0015 * math.sin(2 * math.pi * 1.7 * t + 1)) * (v / SPEED)
    ctx["bus"].location.y = bus_y
    ctx["bus"].rotation_euler = (0.0, 0.0 if ext else sway, 0.0)
    # the front door
    op = 0.0
    for c in _cues(tl, "door"):
        shut = next((x["t"] for x in _cues(tl, "door_shut") if x["t"] > c["t"]), 1e9)
        if c["t"] <= t:
            op = max(op, _ss((t - c["t"]) / 0.45) * (1 - _ss((t - shut) / 0.45)))
    for leaf, side in ctx["door"]:
        leaf.location.x = W + 0.1 + 0.08 * op
        leaf.location.y = (-6.375 if side < 0 else -5.625) + side * 0.62 * op
    # people inside ride with the bus in the exterior shots
    if bus_y:
        for who in story.get("cast", {}):
            ob = bpy.data.objects.get(who)
            if ob is not None and abs(ob.location.x) < W + 0.2:
                ob.location.y += bus_y
    # sitting: both legs forward
    for who, keys in tl["acting"].items():
        if _switch(keys, "sit", t, False):
            for sx in (-1, 1):
                leg = bpy.data.objects.get(f"{who}.leg{sx}")
                if leg is not None:
                    leg.rotation_euler = (-math.pi / 2, 0, 0)
    driver_grip(kit, ctx)
    # rider 4's phone stays in his hand only while he's in his seat
    r4 = bpy.data.objects.get("rider4")
    away = r4 is None or r4.hide_render or (V((r4.location.x, r4.location.y)) - V((1.38, 0.45))).length > 0.3
    for ob in ctx["phone"]:
        ob.hide_render = away
    # ---- the weather of the night
    night = _switch(_cues(tl, "night"), "night", t, "A")
    rain, fog, cond = NIGHTS.get(night, NIGHTS["A"])
    ctx["rain"].outputs[0].default_value = rain
    for nd in fog_nodes(ctx):
        nd.inputs[1].default_value = -fog
    if _switch(_cues(tl, "fogwin"), "on", t, False):   # the print seen again (a match cut back to it)
        cond = 1.0
    ctx["condensation"].outputs[0].default_value = cond
    # the leak (the pour only), the drip
    leak = _cue(tl, "leak", 1e9)
    dry = _cue(tl, "dry", 1e9)
    w = _ss((t - leak) / 0.6) * (0.0 if t >= dry else 1.0)
    ctx["wet"].outputs[0].default_value = w
    for p, sx, sy in ctx["puddles"]:
        p.scale = (max(0.001, w * sx), max(0.001, w * sy), 1)
        p.hide_render = w < 0.01
    drip = _cue(tl, "drip", 1e9)
    for k, dr in enumerate(ctx["drips"]):
        if t < drip or t >= dry:
            dr.hide_render = True
            continue
        dr.hide_render = False
        ph = ((t - drip) / 0.7 + k / 3) % 1.0
        dr.location.z = (CEIL - 0.05) - (CEIL - 0.55) * ph ** 2
    # the strap over the middle seat: always a slow sway, a hard swing from each "swing" cue
    amp = 0.06
    for c in _cues(tl, "swing"):
        if c["t"] <= t:
            amp = max(amp, c.get("amp", 0.42) * math.exp(-(t - c["t"]) / 2.2))
    ctx["swing"].rotation_euler = (amp * math.sin(2 * math.pi * 0.62 * t), 0.0, 0.0)
    for ob in [ctx["swing"]] + list(ctx["swing"].children):   # once it's seen, the strap would crown its head
        ob.hide_render = t >= _cue(tl, "dim", 1e9)
    # ---- the tubes. Four states: normal; "dim" from the reveal (the front sinks, the back row is the pool of
    # light); "horror" (r1 M4: the front and middle tubes off, only the failing back tube, the rim lights and the
    # streetlights going by); and "undim" for the next night, back to normal
    horror = _switch(_cues(tl, "horror"), "on", t, False)
    g = back_gain(kit, tl, t, always=horror)
    g *= _switch(_cues(tl, "back"), "gain", t, 1.0)    # the back row dimmed for a beat ("Two" said back)
    reveal = _cue(tl, "dim", 1e9)
    seen = _ss((t - reveal) / 1.2) * (0.0 if t >= _cue(tl, "undim", 1e9) else 1.0)
    gb = g * (1.0 - 0.55 * seen)
    ctx["tube_b"].inputs["Strength"].default_value = 7.0 * g
    for nm in ctx["lights_back"]:
        over[nm] = gb * (HORROR_BACK if horror else 1.0)
    hum = (1.0 - 0.03 * (0.5 + 0.5 * math.sin(t * 120))) * (1.0 - 0.62 * seen)
    if horror:
        hum = 0.0
    if seen > 0 or horror:
        over["fill"] = 0.0 if horror else 1.0 - 0.55 * seen
        over["bounce"] = 0.0 if horror else 1.0 - 0.55 * seen
    ctx["tube_f"].inputs["Strength"].default_value = 7.0 * hum
    for nm in ctx["lights_front"]:
        over[nm] = hum
    under = _switch(_cues(tl, "underlight"), "on", t, False) and not ext
    over["under"] = 1.0 if under else 0.0
    # ---- the creature
    info = pose_creature(kit, tl, t, ctx)
    pas = bpy.data.objects.get("passenger")
    rim_on = info.get("visible", 0) > 0 and not ext
    for k in range(2):
        L_ = kit.LIGHTS[f"rim{k}"]
        L_["base"] = ctx["rim_energy"] * (HORROR_RIM if horror else 1.0)
        over[f"rim{k}"] = 1.0 if rim_on else 0.0
    if rim_on:
        h = V(info["head"])
        # two cold rims from behind and above its head, so the grey coat and the pale head keep an edge in the dark
        # rim 0 from behind and above its head; rim 1 from above its hands, so they read when they reach into the
        # dead front of the bus
        hands = [V(o.location) for o in ctx["hands"].values()]
        hm = (hands[0] + hands[1]) / 2
        far = (hm - h).length > 1.2
        for k, (aim, p_) in enumerate((
                (h, V((max(-W + 0.15, min(W - 0.15, h.x - 0.9)), min(YB - 0.1, h.y + 1.0), min(CEIL - 0.35, h.z + 0.15)))),
                (hm if far else h, V((max(-W + 0.15, min(W - 0.15, (hm.x if far else h.x) + 0.9)),
                                       min(YB - 0.1, (hm.y if far else h.y) + 0.9), CEIL - 0.4))))):
            ob = kit.LIGHTS[f"rim{k}"]["obj"]
            ob.location = p_
            ob.rotation_euler = (aim - p_).to_track_quat("-Z", "Y").to_euler()
        # its pale head lit from below, from in front of its face: long shadows up the coat and onto the ceiling
        ob = kit.LIGHTS["under"]["obj"]
        ob.location = (h.x, h.y - 0.5, max(0.15, h.z - 0.6))
        ob.rotation_euler = (h - V(ob.location)).to_track_quat("-Z", "Y").to_euler()
        if horror:
            over["under"] = HORROR_UNDER
        # each big square hand lit from below and in front when it's out on a pole, the sleeves left dark
        for k, hp in enumerate(hands):
            ob = kit.LIGHTS[f"handL{k}"]["obj"]
            ob.location = (hp.x, hp.y - 0.5, max(0.15, hp.z - 0.5))
            ob.rotation_euler = (hp - V(ob.location)).to_track_quat("-Z", "Y").to_euler()
            over[f"handL{k}"] = 1.0 if (hp - h).length > 1.0 else 0.0
    else:
        over["handL0"] = over["handL1"] = 0.0
    if ext:
        over["fill"] = 0.0
        over["bounce"] = 0.0
    shot_look(kit, tl, t, ctx, over, info)
    return over


def shot_look(kit, tl, t, ctx, over, info):
    """One shot's own lighting, from a "shot" cue's `look` (on at the shot's first frame, off with {"look": null}
    at its last), on top of everything else, so no other shot changes. Keys:
    back / front: the back or front tubes times this; under: the under-light on at this gain, under_size its size
    (small = a hard shadow), under_face: placed below and in front of where its face points; side: [pos, aim,
    watts] a raking light; rim1: [pos, aim, watts] the second rim put exactly here."""
    look = _switch(_cues(tl, "shot"), "look", t, None)
    ld = kit.LIGHTS["under"]["light"]
    ld.size = 0.35
    over["sideL"] = 0.0
    if not look:
        return
    if "back" in look:
        for nm in ctx["lights_back"]:
            over[nm] = over.get(nm, 1.0) * look["back"]
        ctx["tube_b"].inputs["Strength"].default_value *= look["back"]
    if "front" in look:
        for nm in ctx["lights_front"]:
            over[nm] = over.get(nm, 1.0) * look["front"]
        over["fill"] = over.get("fill", 1.0) * look["front"]
        over["bounce"] = over.get("bounce", 1.0) * look["front"]
        ctx["tube_f"].inputs["Strength"].default_value *= look["front"]
    if "under" in look and info.get("head") is not None:
        h = V(info["head"])
        ob = kit.LIGHTS["under"]["obj"]
        if look.get("under_pos"):
            ob.location = look["under_pos"]
        elif look.get("under_face"):
            f = (bpy.data.objects["passenger.headm"].matrix_world.to_3x3() @ V((0, -1, 0)))
            f.z = 0.0
            f = f.normalized() if f.length > 1e-6 else V((0, -1, 0))
            ob.location = h + f * look.get("under_out", 0.42) - V((0, 0, look.get("under_down", 0.62)))
        ob.rotation_euler = (h - V(ob.location)).to_track_quat("-Z", "Y").to_euler()
        over["under"] = look["under"]
        ld.size = look.get("under_size", 0.35)
    for key, name in (("side", "sideL"), ("rim0", "rim0"), ("rim1", "rim1")):
        if key in look:
            pos, aim, watts = look[key]
            ob = kit.LIGHTS[name]["obj"]
            ob.location = pos
            ob.rotation_euler = (V(aim) - V(pos)).to_track_quat("-Z", "Y").to_euler()
            kit.LIGHTS[name]["base"] = watts
            over[name] = 1.0
