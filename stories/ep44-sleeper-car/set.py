"""Sleeper car (ep44): a night train, its corridor, cabin and cafe car, the bright hook platform, four montage rooms,
and the Glass One. Built from kit.py's parts. Nothing here is shared with another story's set.

Layout: every place is its own island along +x (OX below), lit only by its own lights (named "<zone>:<what>"), and
animate() switches the other islands' lights off. Front is -y (yaw 0). z = 0 is the floor.

THE MOON (the marker): a flat disc 0.2 m across, 0.22 m above the top of every head, always turned to the camera. The
lit part is cream, the unlit part a faint slate, so the whole disc always reads. A phase is a texture; Ash's follows the
shot (ASH_PHASE below), every other moon is fixed.

THE GLASS ONE: a full R6-shaped person of clear glass blocks with thick bottle-green edges, built once (build_glass)
and posed per frame from the "glass" acting keys. Its face is on the BACK of its head: two eye glints and a dark
mouth slot. No moon, no clothes, no hair. It is never moving on camera; only nearer in the next shot.

LIGHT: the corridor's amber lamps are constant except for one slow fade (the "lamps" cue: down over 1.5 s, hold, up over
1.5 s). Windows never show anything passing: the landscape is a still, low-contrast backdrop sliding by very slowly.
Window light only changes through the slow TOD fades (shot "tod": [from, to], over 2 s).
"""

import math

import bpy
import numpy as np
from mathutils import Vector as V
from PIL import Image, ImageDraw

OX = {"plat": 0, "intv": 60, "offc": 120, "kitch": 180, "comm": 240, "flat": 300, "text": 360, "cab": 420,
      "cor": 480, "caf": 540}
S = 0.34
DOOR_Y = [2.2 + 2.2 * i for i in range(8)]       # corridor cabin doors (y); ours is index 1
OUR = 1
LAMP_Y = [1.1 + 2.2 * i for i in range(9)]

# ---------------------------------------------------------------------------------------- the time of day
TODS = {
    "night": dict(world="#141c33", ws=0.30, fog="#141c33", fd=0.03, ground="#1d283c", ground2="#222f46",
                  hill="#26334c", win="#7f95c0", winE=1.0),
    "grey": dict(world="#6c7a90", ws=0.5, fog="#4a566c", fd=0.02, ground="#3b4658", ground2="#465266",
                 hill="#505d72", win="#aab4c6", winE=3.2),
    "day": dict(world="#cfdcee", ws=1.1, fog="#cfdcee", fd=0.006, ground="#7d8a63", ground2="#8d9a70",
                hill="#8fa19a", win="#fff1dc", winE=7.0),
    "dawn": dict(world="#e3b08c", ws=0.7, fog="#8a7a80", fd=0.02, ground="#4e5058", ground2="#5a5a60",
                 hill="#7a6a70", win="#ffc690", winE=4.0),
    "plat": dict(world="#f2c9a2", ws=1.5, fog="#f2d9bd", fd=0.005, ground="#7d8a63", ground2="#8d9a70",
                 hill="#8fa19a", win="#fff1dc", winE=1.0),
    "room": dict(world="#c9c1b2", ws=0.6, fog="#c9c1b2", fd=0.004, ground="#7d8a63", ground2="#8d9a70",
                 hill="#8fa19a", win="#fff1dc", winE=1.0),
    "flat": dict(world="#1a2448", ws=0.4, fog="#0f1530", fd=0.02, ground="#1d283c", ground2="#222f46",
                 hill="#26334c", win="#7f95c0", winE=1.0),
    "dusk": dict(world="#3c466a", ws=0.8, fog="#34405e", fd=0.012, ground="#2a3350", ground2="#323c5a",
                 hill="#3a4466", win="#ffb070", winE=1.0),
}
ZONE_TOD = {"plat": "plat", "intv": "room", "offc": "room", "kitch": "room", "comm": "room", "flat": "flat",
            "text": "dusk", "cab": "night", "cor": "night", "caf": "night"}


def hx(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))


def lin(h):
    from blocky import kit

    return kit.col(h)[:3]


def _mix(a, b, u):
    return tuple(x + (y - x) * u for x, y in zip(a, b))


# ----------------------------------------------------------------------------------------------- helpers
def E(kit, ox, name, x0, x1, y0, y1, z0, z1, mat, parent=None, bevel=0.0, rot=(0, 0, 0)):
    """A box by its extents (zone-local x, y, z)."""
    return kit.box(name, (x1 - x0, y1 - y0, z1 - z0), (ox + (x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2), mat,
                   parent, rot=rot, bevel=bevel)


def torus(kit, name, R, r, loc, mat, parent, n=40, m=8):
    verts, faces = [], []
    for i in range(n):
        a = 2 * math.pi * i / n
        for j in range(m):
            b = 2 * math.pi * j / m
            rr = R + r * math.cos(b)
            verts.append((rr * math.cos(a), rr * math.sin(a), r * math.sin(b)))
    for i in range(n):
        for j in range(m):
            a0, a1 = i * m + j, ((i + 1) % n) * m + j
            faces.append((a0, a1, a1 - j + (j + 1) % m, a0 - j + (j + 1) % m))
    return kit.mesh_obj(name, verts, faces, mat, parent, loc, smooth=True)


def materials(kit):
    M = {}
    M["walnut"] = kit.planks("#5b3a24", "#3f2817", 1.0, "Y", name="ep44 walnut", rough=0.55)
    M["walnut_d"] = kit.plastic("#3a2416", 0.6, name="ep44 walnut dark")
    M["cream"] = kit.plastic("#efe6cf", 0.8, name="ep44 cream")
    M["cream_d"] = kit.plastic("#bdb39b", 0.85, name="ep44 cream dark")
    M["brass"] = kit.metal("#c8963c", 0.3, name="ep44 brass")
    M["burg"] = kit.plastic("#6e2a2e", 0.65, name="ep44 burgundy")
    M["carpet"] = kit.checker("#2b3552", "#6a3745", 7.0, name="ep44 carpet", rough=0.9)
    M["navy"] = kit.plastic("#18203a", 0.8, name="ep44 navy")
    M["stone"] = kit.checker("#dcd5c5", "#cfc8b6", 0.85, name="ep44 stone", rough=0.8)
    M["stone_w"] = kit.plastic("#d8d2c4", 0.9, name="ep44 stone wall")
    M["iron"] = kit.metal("#343a40", 0.5, name="ep44 iron")
    M["cup"] = kit.plastic("#f4f1ea", 0.4, name="ep44 cup")
    M["frost"] = kit.emit("#e3a35c", 0.12, name="ep44 frost")
    M["blanket"] = kit.checker("#efe6cf", "#d3c6a6", 9.0, name="ep44 blanket", rough=0.95)
    M["dark"] = kit.plastic("#0d1018", 0.9, name="ep44 dark")
    M["wall_n"] = kit.plastic("#6f7a8e", 0.9, name="ep44 wall night")
    M["plant"] = kit.plastic("#4d7a4a", 0.8, name="ep44 plant")
    M["wood_l"] = kit.planks("#a97c50", "#8b6238", 1.0, "X", name="ep44 wood light", rough=0.6)
    M["paper"] = kit.plastic("#f2efe6", 0.9, name="ep44 paper")
    M["screen"] = kit.emit("#9fc7e8", 0.6, name="ep44 screen")
    M["sofa"] = kit.plastic("#58627a", 0.9, name="ep44 sofa")
    M["bed"] = kit.plastic("#8d9bb8", 0.9, name="ep44 bedding")
    M["seat_c"] = kit.plastic("#8c5a3a", 0.8, name="ep44 commuter seat")
    M["floor_g"] = kit.plastic("#6a6e75", 0.85, name="ep44 grey floor")
    M["win_warm"] = kit.emit("#e3a35c", 2.2, name="ep44 warm window")
    M["body_navy"] = kit.plastic("#1d2b4d", 0.5, name="ep44 carriage navy")
    M["lamp"] = kit.emit("#e3a35c", 1.0, name="ep44 lamp shade")
    M["corlamp"] = kit.emit("#e3a35c", 1.6, name="ep44 corridor lamp shade")
    return M


def glass_pane(kit, name="ep44 pane", refl=0.2):
    """A window pane: mostly clear, a faint mirror (the reflection in S35/S36)."""
    if name in kit.MATS:
        return kit.MATS[name]
    m = kit._new(name)
    nt = m.node_tree
    nt.nodes.remove(nt.nodes["Principled BSDF"])
    out = next(n for n in nt.nodes if n.type == "OUTPUT_MATERIAL")
    tr = nt.nodes.new("ShaderNodeBsdfTransparent")
    gl = nt.nodes.new("ShaderNodeBsdfGlossy")
    gl.inputs["Roughness"].default_value = 0.03
    gl.inputs["Color"].default_value = (0.85, 0.9, 1.0, 1)
    mix = nt.nodes.new("ShaderNodeMixShader")
    mix.inputs[0].default_value = refl
    nt.links.new(tr.outputs[0], mix.inputs[1])
    nt.links.new(gl.outputs[0], mix.inputs[2])
    nt.links.new(mix.outputs[0], out.inputs["Surface"])
    return m


# ------------------------------------------------------------------------------------------------- moons
LEVELS = [0.015, 0.025, 0.03, 0.04, 0.06, 0.08, 0.1, 0.12, 0.15, 0.2, 0.3, 0.4, 0.5, 0.7, 0.85, 1.0]


def moon_image(f, px=256):
    yy, xx = np.mgrid[0:px, 0:px].astype(np.float32)
    # 3x supersample for a clean edge
    ss = 3
    ys = (np.arange(px * ss) + 0.5) / (px * ss) * 2 - 1
    yv, xv = np.meshgrid(ys, ys, indexing="ij")
    inside = (xv ** 2 + yv ** 2) <= 0.96
    k = 1 - 2 * f
    lit = inside & (xv >= k * np.sqrt(np.clip(0.96 - yv ** 2, 0, 1)))
    ins = inside.reshape(px, ss, px, ss).mean(axis=(1, 3))
    lt = lit.reshape(px, ss, px, ss).mean(axis=(1, 3))
    img = np.zeros((px, px, 4), np.float32)
    cream = np.array(hx("#f3ecd2"))
    slate = np.array(hx("#3b4560"))
    img[..., :3] = slate
    img[..., 3] = ins * 0.35
    a = lt[..., None]
    img[..., :3] = img[..., :3] * (1 - a) + cream * a
    img[..., 3] = np.maximum(ins * 0.35, lt)
    return (img * 255).astype(np.uint8)


def moon_mats(kit):
    out = {}
    for f in LEVELS:
        a = moon_image(f)
        img = bpy.data.images.new(f"moon{f}", a.shape[1], a.shape[0], alpha=True)
        img.pixels.foreach_set((a[::-1].astype(np.float32) / 255).ravel())
        img.pack()
        m = bpy.data.materials.new(f"moon {f}")
        m.use_nodes = True
        nt = m.node_tree
        for n in list(nt.nodes):
            if n.type != "OUTPUT_MATERIAL":
                nt.nodes.remove(n)
        outn = next(n for n in nt.nodes if n.type == "OUTPUT_MATERIAL")
        tx = nt.nodes.new("ShaderNodeTexImage")
        tx.image = img
        tx.interpolation = "Linear"
        tx.extension = "CLIP"
        tc = nt.nodes.new("ShaderNodeTexCoord")
        nt.links.new(tc.outputs["Generated"], tx.inputs["Vector"])
        em = nt.nodes.new("ShaderNodeEmission")
        em.inputs["Strength"].default_value = 0.85
        tr = nt.nodes.new("ShaderNodeBsdfTransparent")
        mx = nt.nodes.new("ShaderNodeMixShader")
        nt.links.new(tx.outputs["Color"], em.inputs["Color"])
        nt.links.new(tx.outputs["Alpha"], mx.inputs[0])
        nt.links.new(tr.outputs[0], mx.inputs[1])
        nt.links.new(em.outputs[0], mx.inputs[2])
        nt.links.new(mx.outputs[0], outn.inputs["Surface"])
        try:
            m.emission_sampling = "NONE"
        except Exception:
            pass
        out[f] = m
    return out


def near_level(f):
    return min(LEVELS, key=lambda x: abs(x - f))


FIXED_MOON = {"me": 1.0, "t1": 1.0, "t2": 0.3, "t3": 0.5, "cand": 0.2, "napper": 1.0, "co1": 0.15, "co2": 0.2,
              "cA": 1.0, "cB": 0.15, "c1": 0.2, "c2": 0.15, "c3": 0.3, "c4": 0.2, "att": 0.7, "intv": 0.85,
              "ash2": 1.0}
MOON_SCALE = {"napper": 1.5, "t1": 1.4, "ash": 1.25}
# Ash's moon by shot: (from, to), a change over the shot's own length (at least 1 s in every ramp)
ASH_PHASE = {}


def _ash_table():
    """Ash's moon in clear steps: 0.15 (a crescent) -> eyelash 0.10 (S26) -> a nap makes it fuller (S33 ramps
    0.08 -> 0.3) -> thread 0.05 (S40) -> barely there 0.03 (S47) -> one line 0.015 (S58)."""
    def put(a, b, v):
        for i in range(a, b + 1):
            ASH_PHASE[f"S{i:02d}"] = v
    put(1, 25, (0.15, 0.15))
    put(26, 32, (0.1, 0.1))
    ASH_PHASE["S33"] = (0.1, 0.3)
    put(34, 37, (0.06, 0.06))
    put(38, 45, (0.04, 0.04))
    put(46, 57, (0.025, 0.025))
    ASH_PHASE["S58"] = (0.015, 0.015)
    ASH_PHASE["S59"] = (0.025, 0.025)
    ASH_PHASE["S64b"] = (0.015, 0.015)
    ASH_PHASE["S60"] = (0.2, 0.2)
    ASH_PHASE["S61"] = (0.06, 0.06)
    put(62, 68, (0.015, 0.015))
    put(69, 75, (1.0, 1.0))


_ash_table()


# --------------------------------------------------------------------------------------------- the Glass One
EDGE = 0.15   # rig units: thick bottle-green edges where the blocks meet


def glass_mats(kit):
    if "g_glass" in kit.MATS:
        return kit.MATS["g_glass"], kit.MATS["g_edge"]
    m = kit._new("g_glass")
    nt = m.node_tree
    nt.nodes.remove(nt.nodes["Principled BSDF"])
    out = next(n for n in nt.nodes if n.type == "OUTPUT_MATERIAL")
    tr = nt.nodes.new("ShaderNodeBsdfTransparent")
    tr.inputs["Color"].default_value = (0.78, 0.93, 0.86, 1)
    gl = nt.nodes.new("ShaderNodeBsdfGlossy")
    gl.inputs["Roughness"].default_value = 0.06
    gl.inputs["Color"].default_value = (0.8, 1.0, 0.9, 1)
    lw = nt.nodes.new("ShaderNodeLayerWeight")
    lw.inputs["Blend"].default_value = 0.35
    add = nt.nodes.new("ShaderNodeMath")
    add.operation = "ADD"
    add.inputs[1].default_value = 0.12
    cl = nt.nodes.new("ShaderNodeMath")
    cl.operation = "MINIMUM"
    cl.inputs[1].default_value = 0.85
    mix = nt.nodes.new("ShaderNodeMixShader")
    nt.links.new(lw.outputs["Fresnel"], add.inputs[0])
    nt.links.new(add.outputs[0], cl.inputs[0])
    nt.links.new(cl.outputs[0], mix.inputs[0])
    # a faint cool veil on the pane (never a glow): a clear sheet still reads as a sheet of glass
    veil = nt.nodes.new("ShaderNodeEmission")
    veil.inputs["Color"].default_value = (0.55, 0.8, 0.7, 1)
    veil.inputs["Strength"].default_value = 0.0
    # a faint fresnel: the veil is strongest toward the glancing edges (a rim), faint face-on; it never glows
    fz = nt.nodes.new("ShaderNodeLayerWeight")
    fz.inputs["Blend"].default_value = 0.5
    fs = nt.nodes.new("ShaderNodeMath")
    fs.operation = "MULTIPLY"
    fs.inputs[1].default_value = 0.9
    fa = nt.nodes.new("ShaderNodeMath")
    fa.operation = "ADD"
    fa.inputs[1].default_value = 0.09
    nt.links.new(fz.outputs["Fresnel"], fs.inputs[0])
    nt.links.new(fs.outputs[0], fa.inputs[0])
    nt.links.new(fa.outputs[0], veil.inputs["Strength"])
    tm = nt.nodes.new("ShaderNodeMixShader")
    tm.inputs[0].default_value = 0.5
    nt.links.new(tr.outputs[0], tm.inputs[1])
    nt.links.new(veil.outputs[0], tm.inputs[2])
    nt.links.new(tm.outputs[0], mix.inputs[1])
    nt.links.new(gl.outputs[0], mix.inputs[2])
    nt.links.new(mix.outputs[0], out.inputs["Surface"])
    e = kit._new("g_edge")
    b = e.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = kit.col("#1b6044")
    b.inputs["Roughness"].default_value = 0.14
    b.inputs["Emission Color"].default_value = kit.col("#1f6b4a")
    b.inputs["Emission Strength"].default_value = 0.3
    e.diffuse_color = kit.col("#1f6b4a")
    return m, e


def glass_part(kit, name, size, center, parent, gm, em):
    """One glass block: a clear box and twelve thick green edge bars."""
    sx, sy, sz = size
    kit.box(f"{name}.pane", size, center, gm, parent)
    t = EDGE
    cx, cy, cz = center
    for ax in (-1, 1):
        for ay in (-1, 1):
            kit.box(f"{name}.ez{ax}{ay}", (t, t, sz + t), (cx + ax * sx / 2, cy + ay * sy / 2, cz), em, parent)
            kit.box(f"{name}.ex{ax}{ay}", (sx + t, t, t), (cx, cy + ay * sy / 2, cz + ax * sz / 2), em, parent)
            kit.box(f"{name}.ey{ax}{ay}", (t, sy + t, t), (cx + ax * sx / 2, cy, cz + ay * sz / 2), em, parent)


def build_glass(kit, ctx):
    gm, em = glass_mats(kit)
    glint = kit.emit("#fff1c4", 2.6, name="g_glint")
    dark = kit.plastic("#050607", 0.9, name="g_mouth")
    root = kit.empty("glass", (0, 0, -100))
    root.scale = (S, S, S)
    G = {"root": root}
    for sx in (-1, 1):
        leg = kit.empty(f"glass.leg{sx}", (sx * 0.5, 0, 2.0), root)
        glass_part(kit, f"glass.leg{sx}", (1.0, 1.0, 2.0), (0, 0, -1.0), leg, gm, em)
        G[f"leg{sx}"] = leg
    torso = kit.empty("glass.torso", (0, 0, 2.0), root)
    glass_part(kit, "glass.torso", (2.0, 1.0, 2.0), (0, 0, 1.0), torso, gm, em)
    # the chest cue (the FRONT is -y): a thick bottle-green V collar notch and a centre seam, so you can tell which
    # way the body faces while the face is on the back of the head
    T = EDGE * 1.9
    for sx in (-1, 1):
        kit.box(f"glass.collar{sx}", (1.0, T, T), (sx * 0.5, -0.5, 1.62), em, torso,
                rot=(0, sx * math.radians(-32), 0))
    kit.box("glass.seam", (T * 0.8, T * 0.8, 1.0), (0, -0.5, 0.78), em, torso)
    kit.box("glass.belt", (2.0, T * 0.7, T * 0.7), (0, -0.5, 0.2), em, torso)
    G["torso"] = torso
    for sx in (-1, 1):
        arm = kit.empty(f"glass.arm{sx}", (sx * 1.5, 0, 1.75), torso)
        glass_part(kit, f"glass.arm{sx}", (1.0, 1.0, 2.0), (0, 0, -0.75), arm, gm, em)
        G[f"arm{sx}"] = arm
    neck = kit.empty("glass.neck", (0, 0, 2.0), torso)
    head = kit.empty("glass.head", (0, 0, 0.62), neck)
    R, H = 0.62, 1.2
    kit.cyl("glass.headm", R, H, (0, 0, 0), gm, head, n=40)
    for z in (-H / 2, H / 2):
        torus(kit, f"glass.ring{z}", R, EDGE / 2, (0, 0, z), em, head)
    for k in range(4):
        a = math.radians(45 + 90 * k)
        kit.box(f"glass.hbar{k}", (EDGE, EDGE, H + EDGE), (R * math.cos(a), R * math.sin(a), 0), em, head,
                rot=(0, 0, a))
    # the face is on the BACK of the head (+y): two glints and a short dark mouth slot, set into the glass
    for sx in (-1, 1):
        g = kit.sphere(f"glass.glint{sx}", 0.068, (sx * 0.23, R - 0.02, 0.12), glint, head, seg=10)
        g.scale = (1.0, 0.5, 1.15)
    kit.box("glass.mouth", (0.34, 0.07, 0.045), (0, R - 0.0, -0.2), dark, head)
    G["neck"], G["head"] = neck, head
    ctx["G"] = G


def pose_glass(tl, t, ctx):
    from blocky import acting as ac

    keys = tl["acting"].get("glass", [])
    G = ctx["G"]
    if not keys:
        G["root"].location = (0, 0, -100)
        return None
    s = ac.state(tl, "glass", t)
    hide = s["hidden"]
    roll = math.radians(ac._held(keys, "roll", t, 0.0))
    G["root"].location = (s["x"], s["y"], s["z"] if not hide else -100)
    G["root"].rotation_euler = (s["lean"], roll, s["yaw"])
    G["leg-1"].rotation_euler = (0, 0, 0)
    G["leg1"].rotation_euler = (0, 0, 0)
    G["arm-1"].rotation_euler = (-s["arms"][0], s["arms_side"][0], 0)
    G["arm1"].rotation_euler = (-s["arms"][1], -s["arms_side"][1], 0)
    G["neck"].rotation_euler = (s["head_pitch"], 0, s["head_yaw"])
    nks = [k for k in keys if "nk" in k or "nkm" in k]
    if nks and t >= nks[0]["t"] and not hide:   # a direct neck pose (degrees x, y, z), for the head hung over the bunk edge
        from mathutils import Matrix

        nm = ac._held(keys, "nkm", t, None)
        if nm is not None:   # a full rotation matrix (row-major), when angles are awkward
            G["neck"].rotation_euler = Matrix([nm[0:3], nm[3:6], nm[6:9]]).to_euler()
            return V((G["root"].location.x, G["root"].location.y, G["root"].location.z + 1.75))
        nk = ac._held(keys, "nk", t, [0.0, 0.0, 0.0])
        a, b, c = (math.radians(v) for v in nk)
        G["neck"].rotation_euler = (Matrix.Rotation(a, 3, "X") @ Matrix.Rotation(b, 3, "Y")
                                    @ Matrix.Rotation(c, 3, "Z")).to_euler()
    pr = G["root"].location
    return V((pr.x, pr.y, pr.z + 1.75))


# ------------------------------------------------------------------------------------------ landscape
def landscape(kit, ctx, ox, side, name, r=0.4):
    """The still, dark view from the train windows: ground, a few low hills, sliding by very slowly. Emission only,
    so no light of its own can pass a window. `side` +1 is the +x side of the car, -1 the -x side."""
    grp = kit.empty(f"land.{name}", (ox, 0, 0))
    gm = kit._new(f"land ground {name}")
    nt = gm.node_tree
    nt.nodes.remove(nt.nodes["Principled BSDF"])
    out = next(n for n in nt.nodes if n.type == "OUTPUT_MATERIAL")
    tc = nt.nodes.new("ShaderNodeTexCoord")
    nz = nt.nodes.new("ShaderNodeTexNoise")
    nz.inputs["Scale"].default_value = 0.35
    nz.inputs["Detail"].default_value = 4.0
    nt.links.new(tc.outputs["Object"], nz.inputs["Vector"])
    ramp = nt.nodes.new("ShaderNodeValToRGB")
    em = nt.nodes.new("ShaderNodeEmission")
    em.inputs["Strength"].default_value = 1.0
    nt.links.new(nz.outputs["Fac"], ramp.inputs["Fac"])
    nt.links.new(ramp.outputs["Color"], em.inputs["Color"])
    nt.links.new(em.outputs[0], out.inputs["Surface"])
    hm = kit._new(f"land hill {name}")
    nt2 = hm.node_tree
    nt2.nodes.remove(nt2.nodes["Principled BSDF"])
    out2 = next(n for n in nt2.nodes if n.type == "OUTPUT_MATERIAL")
    em2 = nt2.nodes.new("ShaderNodeEmission")
    nt2.links.new(em2.outputs[0], out2.inputs["Surface"])
    for m in (gm, hm):
        try:
            m.emission_sampling = "NONE"
        except Exception:
            pass
    kit.box(f"land.ground.{name}", (140 * r, 260 * r, 0.2), (side * 75 * r, 0, -1.3), gm, grp)
    for i, (hx_, hy, sx, sy, sz) in enumerate([(40, -30, 16, 26, 3.6), (52, 10, 20, 30, 5.0), (36, 55, 14, 22, 3.0),
                                                 (60, -70, 22, 34, 5.5), (46, 90, 18, 28, 4.0), (44, -110, 16, 24, 3.4)]):
        h = kit.sphere(f"land.hill{i}.{name}", 1.0, (side * hx_ * r, hy * r, -1.2), hm, grp, seg=14)
        h.scale = (sx * r, sy * r, sz * r)
    ctx.setdefault("land", []).append({"grp": grp, "ramp": ramp, "hill": em2, "ox": ox})


# ----------------------------------------------------------------------------------------------- corridor
def build_corridor(kit, ctx, M):
    ox = OX["cor"]
    W0, W1, Y0, Y1, H = -0.75, 0.75, -1.6, 20.6, 2.4
    E(kit, ox, "cor.floor", W0, W1, Y0, Y1, -0.1, 0.0, M["walnut_d"])
    E(kit, ox, "cor.carpet", -0.45, 0.45, Y0, Y1, 0.0, 0.012, M["carpet"])
    E(kit, ox, "cor.ceil", W0, W1, Y0, Y1, H, H + 0.1, M["cream_d"])
    # cabin side: walnut wall with doors
    oy0, oy1 = DOOR_Y[OUR] - 0.62, DOOR_Y[OUR] + 0.62
    E(kit, ox, "cor.wallA1", W0 - 0.1, W0, Y0, oy0, 0, H, M["walnut"])
    E(kit, ox, "cor.wallA2", W0 - 0.1, W0, oy1, Y1, 0, H, M["walnut"])
    E(kit, ox, "cor.wallA3", W0 - 0.1, W0, oy0, oy1, 2.1, H, M["walnut"])
    # behind our door: a dark corner of the cabin, so a person can stand in the doorway
    E(kit, ox, "cor.alc_floor", -2.5, W0, oy0 - 0.5, oy1 + 0.5, -0.1, 0, M["walnut_d"])
    E(kit, ox, "cor.alc_back", -2.6, -2.5, oy0 - 0.5, oy1 + 0.5, 0, H, M["walnut"])
    E(kit, ox, "cor.alc_l", -2.6, W0, oy0 - 0.6, oy0 - 0.5, 0, H, M["walnut"])
    E(kit, ox, "cor.alc_r", -2.6, W0, oy1 + 0.5, oy1 + 0.6, 0, H, M["walnut"])
    E(kit, ox, "cor.alc_ceil", -2.5, W0, oy0 - 0.5, oy1 + 0.5, H, H + 0.1, M["cream_d"])
    kit.light("cor:alcove", "POINT", (ox - 1.7, DOOR_Y[OUR], 2.1), 3.5, "#e3a35c", size=0.06)
    E(kit, ox, "cor.skirt", W0, W0 + 0.03, Y0, Y1, 0, 0.12, M["walnut_d"])
    E(kit, ox, "cor.rail", W0, W0 + 0.04, Y0, Y1, 0.95, 1.0, M["brass"])
    ctx["cor_doors"] = []
    for i, y in enumerate(DOOR_Y):
        d = kit.empty(f"cor.door{i}", (ox, y, 0))
        kit.box(f"cor.door{i}.slab", (0.05, 1.2, 2.05), (W0 + 0.025, 0, 1.025), M["walnut_d"], d, bevel=0.01)
        kit.box(f"cor.door{i}.frost", (0.02, 0.8, 0.75), (W0 + 0.06, 0, 1.45), M["frost"], d)
        kit.box(f"cor.door{i}.handle", (0.04, 0.16, 0.035), (W0 + 0.07, 0.48, 1.0), M["brass"], d)
        kit.box(f"cor.door{i}.plate", (0.012, 0.16, 0.1), (W0 + 0.056, -0.45, 1.85), M["brass"], d)
        for k in range(i + 1):
            kit.cyl(f"cor.door{i}.dot{k}", 0.009, 0.006, (W0 + 0.064, -0.45 - 0.06 + (k % 4) * 0.04,
                    1.85 + 0.025 - (k // 4) * 0.04), M["dark"], d, rot=(0, math.pi / 2, 0), n=10)
        ctx["cor_doors"].append(d)
        E(kit, ox, f"cor.frame{i}a", W0, W0 + 0.06, y - 0.64, y - 0.6, 0, 2.1, M["walnut"])
        E(kit, ox, f"cor.frame{i}b", W0, W0 + 0.06, y + 0.6, y + 0.64, 0, 2.1, M["walnut"])
    # window side: pillars and panes
    pane = glass_pane(kit, "ep44 pane", 0.5)
    E(kit, ox, "cor.wallB_low", W1, W1 + 0.1, Y0, Y1, 0, 0.85, M["walnut"])
    E(kit, ox, "cor.wallB_high", W1, W1 + 0.1, Y0, Y1, 2.05, H, M["walnut_d"])
    for i in range(10):
        yc = 0.0 + 2.2 * i + 1.1 - 1.1
        E(kit, ox, f"cor.pillar{i}", W1 - 0.03, W1 + 0.1, yc - 0.1, yc + 0.1, 0.85, 2.05, M["walnut"])
        E(kit, ox, f"cor.sill{i}", W1 - 0.05, W1 + 0.0, yc + 0.1, yc + 2.1, 0.83, 0.88, M["brass"])
    kit.plane("cor.pane", (22.0, 1.2), (ox + W1, 9.5, 1.45), pane, rot=(math.pi / 2, 0, math.pi / 2))
    # the far end: the connecting door with its round window
    E(kit, ox, "cor.end", W0, W1, Y1 - 0.1, Y1, 0, H, M["walnut"])
    E(kit, ox, "cor.endframe", -0.7, 0.7, Y1 - 0.12, Y1 - 0.1, 0, 2.15, M["walnut_d"])
    kit.cyl("cor.endwin", 0.14, 0.03, (ox, Y1 - 0.14, 1.55), kit.emit("#2c3a52", 0.6, name="ep44 endwin"), None,
            rot=(math.pi / 2, 0, 0), n=24)
    torus(kit, "cor.endring", 0.15, 0.015, (ox, Y1 - 0.14, 1.55), M["brass"], None, n=28, m=6).rotation_euler = (
        math.pi / 2, 0, 0)
    # near end, so a reverse shot isn't open to the void
    E(kit, ox, "cor.start", W0, W1, Y0, Y0 + 0.1, 0, H, M["walnut"])
    # lamps on the cabin side, between the doors
    ctx["lamp_em"] = []
    for i, y in enumerate(LAMP_Y):
        kit.box(f"cor.lamp{i}", (0.06, 0.16, 0.2), (ox + W0 + 0.05, y, 2.0), M["corlamp"], None, bevel=0.02)
        kit.light(f"cor:lamp{i}", "POINT", (ox + W0 + 0.28, y, 1.95), 7.0, "#e3a35c", size=0.05)
    kit.light("cor:fill", "AREA", (ox, 9.5, 2.3), 55.0, "#e3a35c", size=2.0)
    kit.aim(kit.LIGHTS["cor:fill"]["obj"], (ox, 9.5, 0))
    kit.LIGHTS["cor:fill"]["obj"].scale = (0.25, 5.0, 1.0)
    for i, y in enumerate([2.0, 7.0, 12.0, 17.0]):
        kit.light(f"cor:win{i}", "AREA", (ox + 2.0, y, 1.7), 90.0, "#7f95c0", size=1.4)
        kit.aim(kit.LIGHTS[f"cor:win{i}"]["obj"], (ox + 0.3, y - 0.2, 1.3))
    landscape(kit, ctx, ox, +1, "cor")


def build_stub(kit, ctx, M):
    """Outside our cabin door, seen from inside the cabin (S53, S54): a bit of the same corridor."""
    ox = OX["cab"] - 1.2
    pane = glass_pane(kit, "ep44 pane2")
    E(kit, ox, "stub.floor", -1.6, 0, -4, 4, -0.1, 0, M["walnut_d"])
    E(kit, ox, "stub.carpet", -1.3, -0.3, -4, 4, 0.0, 0.012, M["carpet"])
    E(kit, ox, "stub.ceil", -1.6, 0, -4, 4, 3.2, 3.3, M["cream_d"])
    E(kit, ox, "stub.wall", -1.7, -1.6, -4, 4, 0, 3.2, M["walnut"])
    kit.plane("stub.pane", (8, 1.2), (ox - 1.6, 0, 1.45), pane, rot=(math.pi / 2, 0, math.pi / 2))
    E(kit, ox, "stub.low", -1.6, -1.5, -4, 4, 0, 0.85, M["walnut"])
    E(kit, ox, "stub.high", -1.6, -1.5, -4, 4, 2.05, 3.2, M["walnut_d"])
    E(kit, ox, "stub.end1", -1.6, 0, 3.9, 4.0, 0, 3.2, M["walnut"])
    E(kit, ox, "stub.end2", -1.6, 0, -4.0, -3.9, 0, 3.2, M["walnut"])
    kit.box("stub.lamp", (0.16, 0.06, 0.2), (OX["cab"] - 1.38, 0.9, 2.0), M["lamp"], None, bevel=0.02)
    kit.light("cab:stub", "POINT", (OX["cab"] - 1.8, 0.9, 1.9), 7.0, "#e3a35c", size=0.05)
    kit.light("cab:stub2", "POINT", (OX["cab"] - 1.8, -1.5, 1.9), 4.0, "#e3a35c", size=0.05)
    landscape(kit, ctx, OX["cab"] - 4.0, -1, "stub")
    kit.OBJ["stub_land"] = True


# --------------------------------------------------------------------------------------------------- cabin
def build_cabin(kit, ctx, M):
    ox = OX["cab"]
    CH = 3.0                       # a tall cabin, so a moon fits over the top bunk
    ZH = 1.55                      # the top bunk's frame (Ash sits up under it, hunched)
    pane = glass_pane(kit, "ep44 pane3", 0.12)
    E(kit, ox, "cab.floor", -1.2, 1.2, -1.6, 1.6, -0.1, 0.0, M["walnut_d"])
    E(kit, ox, "cab.rug", -0.95, -0.1, -1.2, 1.2, 0.0, 0.012, M["carpet"])
    E(kit, ox, "cab.ceil", -1.2, 1.2, -1.6, 1.6, CH, CH + 0.1, M["cream_d"])
    E(kit, ox, "cab.wallR", 1.2, 1.3, -1.6, 1.6, 0, CH, M["walnut"])
    E(kit, ox, "cab.wallN", -1.2, 1.2, -1.7, -1.6, 0, CH, M["walnut"])
    # the window wall (+y) with its opening, and the corridor wall (-x) with the door opening
    E(kit, ox, "cab.wallS_lo", -1.2, 1.2, 1.6, 1.7, 0, 1.3, M["walnut"])
    E(kit, ox, "cab.wallS_hi", -1.2, 1.2, 1.6, 1.7, 2.5, CH, M["walnut"])
    E(kit, ox, "cab.wallS_l", -1.2, -0.6, 1.6, 1.7, 1.3, 2.5, M["walnut"])
    E(kit, ox, "cab.wallS_r", 0.6, 1.2, 1.6, 1.7, 1.3, 2.5, M["walnut"])
    kit.plane("cab.pane", (1.2, 1.2), (ox, 1.6, 1.9), pane, rot=(math.pi / 2, 0, 0))
    for nm, x0, x1, z0, z1 in (("a", -0.62, -0.58, 1.28, 2.52), ("b", 0.58, 0.62, 1.28, 2.52),
                               ("c", -0.62, 0.62, 1.28, 1.32), ("d", -0.62, 0.62, 2.48, 2.52)):
        E(kit, ox, f"cab.wf{nm}", x0, x1, 1.58, 1.62, z0, z1, M["brass"])
    E(kit, ox, "cab.wallW_a", -1.3, -1.2, -1.6, -0.6, 0, CH, M["walnut"])
    E(kit, ox, "cab.wallW_b", -1.3, -1.2, 0.6, 1.6, 0, CH, M["walnut"])
    E(kit, ox, "cab.wallW_c", -1.3, -1.2, -0.6, 0.6, 2.1, CH, M["walnut"])
    # the sliding door, on the cabin side of its wall, slides toward +y
    d = kit.empty("cab.door", (ox, 0, 0))
    kit.box("cab.door.slab", (0.05, 1.24, 2.12), (-1.17, 0, 1.06), M["walnut_d"], d, bevel=0.01)
    kit.box("cab.door.frost", (0.02, 0.8, 0.75), (-1.2, 0, 1.5), M["frost"], d)
    kit.box("cab.door.handle", (0.04, 0.16, 0.035), (-1.13, -0.28, 1.0), M["brass"], d)
    ctx["cab_door"] = d
    # bunks along +x: bottom and top, heads toward +y
    for nm, z0 in (("lo", 0.25), ("hi", ZH)):
        E(kit, ox, f"cab.bunk_{nm}", 0.0, 1.2, -1.5, 0.5, z0, z0 + 0.25, M["walnut"], bevel=0.02)
        E(kit, ox, f"cab.mat_{nm}", 0.02, 1.18, -1.48, 0.48, z0 + 0.25, z0 + 0.37, M["bed"], bevel=0.04)
        E(kit, ox, f"cab.pillow_{nm}", 0.2, 1.0, 0.08, 0.46, z0 + 0.37, z0 + 0.47, M["cream"], bevel=0.05)
        E(kit, ox, f"cab.rail_{nm}", 0.0, 0.04, -1.5, 0.5, z0 + 0.25, z0 + 0.34, M["walnut_d"])
    for py in (-1.46, 0.46):
        E(kit, ox, f"cab.post{py}", 0.0, 0.05, py - 0.03, py + 0.03, 0.0, ZH + 0.5, M["brass"])
    # the brass ladder on the corridor side of the bunks: rungs at 0.4, 0.75, 1.1 (the third), 1.45, 1.8
    for ry in (-0.05, 0.35):
        E(kit, ox, f"cab.ladder{ry}", -0.07, -0.03, ry - 0.02, ry + 0.02, 0.05, ZH + 0.15, M["brass"])
    for k, rz in enumerate((0.4, 0.75, 1.1, 1.45)):
        kit.cyl(f"cab.rung{k}", 0.014, 0.4, (ox - 0.05, 0.15, rz), M["brass"], None, rot=(math.pi / 2, 0, 0), n=10)
    tm = kit.emit("#2fae78", 0.5, name="ep44 tally")
    ctx["tally"] = [E(kit, ox, f"cab.tally{i}", -0.0735, -0.0705, -0.064 + i * 0.03, -0.056 + i * 0.03, 1.12, 1.2, tm)
                    for i in range(2)]
    # the folding table under the window, the blankets
    E(kit, ox, "cab.table", -0.55, 0.5, 1.2, 1.6, 0.72, 0.76, M["walnut"], bevel=0.01)
    for tx in (-0.5, 0.45):
        E(kit, ox, f"cab.tleg{tx}", tx - 0.015, tx + 0.015, 1.5, 1.56, 0.0, 0.72, M["brass"])
    ctx["blank_lo"] = E(kit, ox, "cab.blanket_lo", 0.05, 1.15, -1.45, -0.35, 0.62, 0.68, M["blanket"], bevel=0.03)
    ctx["blank_hi"] = E(kit, ox, "cab.blanket_hi", 0.05, 1.15, -1.45, -0.15, ZH + 0.37, ZH + 0.46, M["blanket"], bevel=0.03)
    ctx["blank_lump"] = E(kit, ox, "cab.blanket_lump", -0.05, 0.62, -1.45, -0.04, ZH + 0.37, ZH + 1.14, M["blanket"], bevel=0.15)
    # a rounded bump at the shoulder, so the lump reads as a body (and a head on the pillow beyond it)
    ctx["blank_lump2"] = E(kit, ox, "cab.blanket_lump2", -0.05, 0.56, -0.5, -0.04, ZH + 0.37, ZH + 1.2, M["blanket"], bevel=0.17)
    # the reading lamp (dim amber, lit only before sleep), a ceiling fill, the moonlit window, the stub's amber
    E(kit, ox, "cab.readlamp", -0.06, -0.02, 0.05, 0.2, 1.3, 1.4, M["brass"], bevel=0.01)
    kit.light("cab:read", "POINT", (ox - 0.15, 0.1, 1.5), 9.0, "#e3a35c", size=0.06)
    kit.light("cab:ladder", "POINT", (ox - 0.55, 0.1, 1.2), 12.0, "#e3a35c", size=0.08)
    kit.light("cab:fill", "AREA", (ox - 0.2, 0.0, CH - 0.05), 75.0, "#9db0d4", size=1.6)
    kit.aim(kit.LIGHTS["cab:fill"]["obj"], (ox, 0, 0))
    kit.light("cab:win", "AREA", (ox, 2.4, 2.0), 120.0, "#7f95c0", size=1.1)
    kit.aim(kit.LIGHTS["cab:win"]["obj"], (ox, 0.2, 1.2))
    kit.light("cab:win2", "AREA", (ox + 0.4, -1.55, 2.9), 26.0, "#9db0d4", size=0.9)
    kit.aim(kit.LIGHTS["cab:win2"]["obj"], (ox + 0.5, 0.3, 1.2))
    kit.light("cab:glow", "POINT", (ox - 0.9, 0.25, 1.75), 4.0, "#8fe0b8", size=0.15)
    landscape(kit, ctx, ox, +1, "cab")
    ctx["land"][-1]["grp"].rotation_euler = (0, 0, math.pi / 2)   # the window looks along +y
    ctx["land"][-1]["grp"].location = (ox, 2.0, 0)
    ctx["land"][-1]["rot"] = True


# ----------------------------------------------------------------------------------------------------- cafe
CAFE_Y = [1.6, 4.8, 8.0, 11.2]


def build_cafe(kit, ctx, M):
    ox = OX["caf"]
    pane = glass_pane(kit, "ep44 pane4", 0.12)
    E(kit, ox, "caf.floor", -1.7, 1.8, -1, 16, -0.1, 0.0, M["walnut_d"])
    E(kit, ox, "caf.runner", -0.7, 0.2, -1, 16, 0.0, 0.012, M["carpet"])
    E(kit, ox, "caf.ceil", -1.7, 1.8, -1, 16, 2.5, 2.6, M["cream_d"])
    E(kit, ox, "caf.wallL", -1.8, -1.7, -1, 16, 0, 2.5, M["walnut"])
    E(kit, ox, "caf.wallN", -1.8, 1.8, -1.1, -1.0, 0, 2.5, M["walnut"])
    E(kit, ox, "caf.wallF", -1.8, 1.8, 16, 16.1, 0, 2.5, M["walnut"])
    E(kit, ox, "caf.wallR_lo", 1.7, 1.8, -1, 16, 0, 0.9, M["walnut"])
    E(kit, ox, "caf.wallR_hi", 1.7, 1.8, -1, 16, 2.0, 2.5, M["walnut_d"])
    for i in range(5):
        yc = 0.0 + 3.2 * i
        E(kit, ox, f"caf.pillar{i}", 1.65, 1.8, yc - 0.1, yc + 0.1, 0.9, 2.0, M["walnut"])
    kit.plane("caf.pane", (17, 1.1), (ox + 1.7, 7.5, 1.45), pane, rot=(math.pi / 2, 0, math.pi / 2))
    for k, yc in enumerate(CAFE_Y):
        E(kit, ox, f"caf.seat{k}", 1.0, 1.7, yc - 1.5, yc + 1.5, 0.0, 0.42, M["burg"], bevel=0.03)
        E(kit, ox, f"caf.back{k}", 1.5, 1.68, yc - 1.5, yc + 1.5, 0.42, 1.0, M["burg"], bevel=0.06)
        E(kit, ox, f"caf.table{k}", 0.35, 0.95, yc - 1.1, yc + 1.1, 0.84, 0.88, M["walnut"], bevel=0.01)
        kit.cyl(f"caf.ped{k}", 0.05, 0.84, (ox + 0.33, yc, 0.42), M["brass"], None, n=12)
        for cy in (yc - 0.5, yc + 0.5):
            kit.cyl(f"caf.cup{k}{cy}", 0.045, 0.08, (ox + 0.65, cy, 0.92), M["cup"], None, n=14)
    # the counter and what's behind it
    E(kit, ox, "caf.counter", -1.7, 0.5, 13.6, 14.4, 0, 1.05, M["walnut"], bevel=0.02)
    E(kit, ox, "caf.countertop", -1.72, 0.52, 13.58, 14.42, 1.05, 1.1, M["brass"], bevel=0.01)
    E(kit, ox, "caf.shelf", -1.7, 0.5, 15.7, 16.0, 1.3, 1.36, M["walnut"])
    E(kit, ox, "caf.urn", -1.3, -0.8, 15.2, 15.7, 1.05, 1.9, M["brass"], bevel=0.1)
    kit.cyl("caf.cupc", 0.045, 0.08, (ox - 0.35, 13.9, 1.14), M["cup"], None, n=14)
    # the blank menu board, our own dot glyphs
    E(kit, ox, "caf.board", -1.0, 0.3, 15.9, 15.95, 1.55, 2.3, M["dark"])
    for r in range(3):
        for c in range(1 + r):
            kit.cyl(f"caf.dot{r}{c}", 0.04, 0.01, (ox - 0.7 + c * 0.12, 15.88, 2.15 - r * 0.2), M["cream"], None,
                    rot=(math.pi / 2, 0, 0), n=12)
    for i, y in enumerate((1.6, 4.8, 8.0, 11.2)):
        E(kit, ox, f"caf.lampbox{i}", -0.1, 0.1, y - 0.08, y + 0.08, 2.4, 2.5, M["lamp"], bevel=0.02)
        kit.light(f"caf:lamp{i}", "POINT", (ox, y, 2.25), 14.0, "#e3a35c", size=0.08)
        kit.light(f"caf:win{i}", "AREA", (ox + 2.8, y, 1.7), 110.0, "#7f95c0", size=1.6)
        kit.aim(kit.LIGHTS[f"caf:win{i}"]["obj"], (ox + 0.8, y - 0.3, 1.0))
    kit.light("caf:cntr", "POINT", (ox - 0.6, 12.6, 2.2), 12.0, "#e3a35c", size=0.08)
    kit.light("caf:cntr2", "POINT", (ox - 0.6, 14.9, 2.2), 12.0, "#e3a35c", size=0.08)
    landscape(kit, ctx, ox, +1, "caf")


# ----------------------------------------------------------------------------------------------- platform
def build_platform(kit, ctx, M):
    ox = OX["plat"]
    E(kit, ox, "plat.floor", -16, 16, -16, 12, -0.5, 0.0, M["stone"])
    E(kit, ox, "plat.back", -16, 16, 12, 12.4, 0, 9, M["stone_w"])
    E(kit, ox, "plat.base", -16, 16, 11.8, 12, 0, 0.5, M["cream_d"])
    for i, x in enumerate((-6.0, -2.0, 2.0, 6.0)):
        E(kit, ox, f"plat.board{i}", x - 0.8, x + 0.8, 11.75, 11.8, 2.4, 3.4, M["dark"])
        E(kit, ox, f"plat.boardf{i}", x - 0.86, x + 0.86, 11.72, 11.76, 2.34, 3.46, M["brass"])
        for k in range(3):
            kit.cyl(f"plat.bdot{i}{k}", 0.07, 0.01, (ox + x - 0.35 + k * 0.35, 11.7, 2.9), M["cream"], None,
                    rot=(math.pi / 2, 0, 0), n=12)
    for i, y in enumerate((-9.0, -3.0, 3.0, 9.0)):
        for sx in (-1, 1):
            E(kit, ox, f"plat.col{i}{sx}", sx * 4.0 - 0.17, sx * 4.0 + 0.17, y - 0.17, y + 0.17, 0, 5.6, M["iron"],
              bevel=0.03)
            E(kit, ox, f"plat.colbase{i}{sx}", sx * 4.0 - 0.26, sx * 4.0 + 0.26, y - 0.26, y + 0.26, 0, 0.35,
              M["iron"], bevel=0.04)
        E(kit, ox, f"plat.beam{i}", -4.2, 4.2, y - 0.1, y + 0.1, 5.5, 5.75, M["iron"])
    E(kit, ox, "plat.roof", -4.3, 4.3, -10, 10, 5.78, 5.84, kit.emit("#f6e8d2", 0.9, name="ep44 skylight"))
    # an extra column to lean on, near the middle (S11)
    E(kit, ox, "plat.colM", 1.33, 1.67, 3.83, 4.17, 0, 5.6, M["iron"], bevel=0.03)
    E(kit, ox, "plat.bag", 0.55, 1.1, 3.2, 3.65, 0, 0.42, M["burg"], bevel=0.06)
    kit.light("plat:sun", "AREA", (ox - 3.0, -7.0, 7.5), 900.0, "#ffe2bb", size=6.0)
    kit.aim(kit.LIGHTS["plat:sun"]["obj"], (ox, 1.0, 0.8))
    kit.light("plat:fill", "AREA", (ox + 1.0, -9.0, 3.2), 520.0, "#f3e6dc", size=6.0)
    kit.aim(kit.LIGHTS["plat:fill"]["obj"], (ox, 0.0, 1.4))


# ------------------------------------------------------------------------------------------ montage rooms
def room(kit, name, ox, M, wall, floor, w=5.0, d=4.5, h=2.8, back=True):
    E(kit, ox, f"{name}.floor", -w / 2, w / 2, -d, d, -0.1, 0.0, floor)
    if back:
        E(kit, ox, f"{name}.back", -w / 2, w / 2, d, d + 0.1, 0, h, wall)
    E(kit, ox, f"{name}.left", -w / 2 - 0.1, -w / 2, -d, d + 0.1, 0, h, wall)
    E(kit, ox, f"{name}.right", w / 2, w / 2 + 0.1, -d, d + 0.1, 0, h, wall)
    E(kit, ox, f"{name}.ceil", -w / 2, w / 2, -d, d, h, h + 0.1, M["cream_d"])
    E(kit, ox, f"{name}.skirt", -w / 2, w / 2, d - 0.03, d, 0, 0.12, M["walnut_d"])


def chair(kit, name, ox, x, y, mat, face=-1, seat=0.45):
    E(kit, ox, f"{name}.s", x - 0.3, x + 0.3, y - 0.3, y + 0.3, seat - 0.05, seat, mat, bevel=0.02)
    E(kit, ox, f"{name}.b", x - 0.3, x + 0.3, y - face * 0.3 - 0.04 * (-face), y - face * 0.3 + 0.04 * face, seat,
      seat + 0.5, mat, bevel=0.02)
    for lx in (-0.26, 0.26):
        for ly in (-0.26, 0.26):
            E(kit, ox, f"{name}.l{lx}{ly}", x + lx - 0.02, x + lx + 0.02, y + ly - 0.02, y + ly + 0.02, 0, seat - 0.05,
              mat)


def build_rooms(kit, ctx, M):
    # --- interview room (S04)
    ox = OX["intv"]
    room(kit, "intv", ox, M, M["stone_w"], M["wood_l"])
    E(kit, ox, "intv.desk", -1.1, 1.1, 1.3, 2.0, 0, 0.88, M["walnut"], bevel=0.02)
    E(kit, ox, "intv.deskt", -1.15, 1.15, 1.25, 2.05, 0.88, 0.92, M["walnut_d"])
    E(kit, ox, "intv.win", -1.0, 1.0, 4.45, 4.5, 1.1, 2.3, kit.emit("#fff1dc", 0.8, name="ep44 intv window"))
    E(kit, ox, "intv.plant", 1.9, 2.3, 3.7, 4.1, 0, 0.9, M["plant"], bevel=0.12)
    chair(kit, "intv.c1", ox, -0.5, 0.35, M["walnut_d"], face=1)
    chair(kit, "intv.c2", ox, 0.55, 2.9, M["walnut_d"], face=-1)
    kit.light("intv:key", "AREA", (ox, -1.5, 2.6), 330.0, "#fff0dc", size=3.0)
    kit.aim(kit.LIGHTS["intv:key"]["obj"], (ox, 1.5, 1.0))
    # --- open-plan office (S05)
    ox = OX["offc"]
    room(kit, "offc", ox, M, M["stone_w"], M["floor_g"], w=7.0)
    E(kit, ox, "offc.table", -2.2, 2.2, 1.2, 2.1, 0, 0.88, M["walnut"], bevel=0.02)
    E(kit, ox, "offc.tablet", -2.25, 2.25, 1.15, 2.15, 0.88, 0.92, M["walnut_d"])
    for k, x in enumerate((-1.4, 0.0, 1.4)):
        E(kit, ox, f"offc.mon{k}", x - 0.3, x + 0.3, 1.5, 1.55, 1.0, 1.4, M["screen"])
    E(kit, ox, "offc.board", -2.5, 2.5, 4.45, 4.5, 1.2, 2.4, M["cream"])
    for k in range(4):
        E(kit, ox, f"offc.desk{k}", -3.2 + k * 2.1, -2.2 + k * 2.1, 3.3, 4.1, 0, 0.74, M["walnut"])
    chair(kit, "offc.c1", ox, 0.0, 2.9, M["walnut_d"], face=-1)
    kit.light("offc:key", "AREA", (ox, -1.5, 2.7), 420.0, "#fff4e6", size=4.0)
    kit.aim(kit.LIGHTS["offc:key"]["obj"], (ox, 1.5, 1.0))
    # --- kitchen table (S06)
    ox = OX["kitch"]
    room(kit, "kitch", ox, M, kit.plastic("#d8c8a0", 0.9, name="ep44 kitchen wall"), M["wood_l"], w=5.0)
    E(kit, ox, "kitch.table", -1.1, 1.1, 0.4, 1.3, 0.84, 0.88, M["walnut"], bevel=0.02)
    for lx in (-1.0, 1.0):
        E(kit, ox, f"kitch.tl{lx}", lx - 0.04, lx + 0.04, 0.5, 0.58, 0, 0.84, M["walnut_d"])
        E(kit, ox, f"kitch.tl2{lx}", lx - 0.04, lx + 0.04, 1.15, 1.23, 0, 0.84, M["walnut_d"])
    for k, x in enumerate((-0.5, 0.5)):
        kit.cyl(f"kitch.mug{k}", 0.05, 0.1, (ox + x, 0.85, 0.93), M["cup"], None, n=14)
    E(kit, ox, "kitch.win", -0.9, 0.9, 4.45, 4.5, 1.1, 2.3, kit.emit("#fff1dc", 0.8, name="ep44 kitchen window"))
    E(kit, ox, "kitch.counter", 0.9, 2.4, 3.7, 4.45, 0, 0.92, M["cream"], bevel=0.02)
    chair(kit, "kitch.c1", ox, -0.62, 1.95, M["walnut_d"], face=-1)
    chair(kit, "kitch.c2", ox, 0.62, 1.95, M["walnut_d"], face=-1)
    kit.light("kitch:key", "AREA", (ox, -1.4, 2.6), 300.0, "#fff0d8", size=3.0)
    kit.aim(kit.LIGHTS["kitch:key"]["obj"], (ox, 1.0, 1.0))
    # --- commuter carriage (S07): a long bench down the row
    ox = OX["comm"]
    room(kit, "comm", ox, M, kit.plastic("#8a95a8", 0.9, name="ep44 commuter wall"), M["floor_g"], w=3.0, d=7.0)
    E(kit, ox, "comm.bench", 0.6, 1.5, -5.4, 4.0, 0, 0.45, M["seat_c"], bevel=0.04)
    E(kit, ox, "comm.back", 1.35, 1.5, -5.4, 4.0, 0.45, 1.0, M["seat_c"], bevel=0.04)
    E(kit, ox, "comm.window", 1.5, 1.55, -5.0, 3.6, 1.0, 1.9, kit.emit("#cfd9e8", 1.0, name="ep44 commuter window"))
    E(kit, ox, "comm.bench2", -1.5, -0.6, -5.4, 4.0, 0, 0.45, M["seat_c"], bevel=0.04)
    for k in range(5):
        E(kit, ox, f"comm.pole{k}", 0.02, 0.07, -5.0 + 2.4 * k, -4.95 + 2.4 * k, 0, 2.8, M["brass"])
    kit.light("comm:key", "AREA", (ox, -0.5, 2.7), 380.0, "#f4f0e8", size=3.5)
    kit.aim(kit.LIGHTS["comm:key"]["obj"], (ox + 0.5, -0.5, 0.9))
    kit.light("comm:key2", "AREA", (ox, -4.5, 2.7), 260.0, "#f4f0e8", size=3.5)
    kit.aim(kit.LIGHTS["comm:key2"]["obj"], (ox + 0.5, -2.5, 0.9))


# ------------------------------------------------------------------------------------- flat, train outside
def build_flat(kit, ctx, M):
    ox = OX["flat"]
    room(kit, "flat", ox, M, M["wall_n"], M["walnut_d"], w=4.0, d=2.2, h=2.6, back=False)
    # the doorway in the +y wall is just a lower wall + a dark lintel, and the living room beyond
    E(kit, ox, "flat.back_c", -0.5, 0.5, 2.1, 2.3, 2.1, 2.6, M["wall_n"])
    E(kit, ox, "flat.lr_floor", -2.0, 2.0, 2.3, 6.2, -0.1, 0.0, M["walnut_d"])
    E(kit, ox, "flat.lr_back", -2.0, 2.0, 6.2, 6.3, 0, 2.6, M["wall_n"])
    E(kit, ox, "flat.lr_l", -2.1, -2.0, 2.3, 6.3, 0, 2.6, M["wall_n"])
    E(kit, ox, "flat.lr_r", 2.0, 2.1, 2.3, 6.3, 0, 2.6, M["wall_n"])
    E(kit, ox, "flat.lr_ceil", -2.0, 2.0, 2.3, 6.2, 2.6, 2.7, M["cream_d"])
    # the doorway: cut by building the back wall in pieces
    E(kit, ox, "flat.dw_l", -2.0, -0.5, 2.1, 2.3, 0, 2.1, M["wall_n"])
    E(kit, ox, "flat.dw_r", 0.5, 2.0, 2.1, 2.3, 0, 2.1, M["wall_n"])
    E(kit, ox, "flat.bed", -1.9, -0.3, -1.9, 0.5, 0.0, 0.42, M["walnut"], bevel=0.03)
    E(kit, ox, "flat.bedmat", -1.88, -0.32, -1.88, 0.48, 0.42, 0.55, M["bed"], bevel=0.05)
    E(kit, ox, "flat.bedpil", -1.7, -0.5, 0.0, 0.42, 0.55, 0.65, M["cream"], bevel=0.06)
    E(kit, ox, "flat.sofa", -1.0, 0.9, 4.6, 5.6, 0.0, 0.45, M["sofa"], bevel=0.05)
    E(kit, ox, "flat.sofab", -1.0, 0.9, 5.5, 5.75, 0.45, 0.95, M["sofa"], bevel=0.06)
    E(kit, ox, "flat.win", 1.99, 2.0, -1.0, 0.4, 1.0, 2.0, kit.emit("#6a80b0", 0.7, name="ep44 flat window"))
    kit.light("flat:moon", "AREA", (ox + 2.8, -0.3, 1.9), 220.0, "#7f95c0", size=1.3)
    kit.aim(kit.LIGHTS["flat:moon"]["obj"], (ox - 0.6, -0.2, 0.6))
    kit.light("flat:fill", "AREA", (ox, -1.0, 2.5), 140.0, "#8aa0cc", size=2.5)
    kit.aim(kit.LIGHTS["flat:fill"]["obj"], (ox - 0.4, 0.5, 0.4))
    kit.light("flat:lr", "AREA", (ox + 0.2, 4.8, 2.5), 90.0, "#8aa0cc", size=2.0)
    kit.aim(kit.LIGHTS["flat:lr"]["obj"], (ox, 5.0, 0.4))


def build_text(kit, ctx, M):
    """The train at the platform in the evening (S13): a long walnut and navy carriage with warm windows."""
    ox = OX["text"]
    E(kit, ox, "text.floor", -14, 14, -9, 10, -0.5, 0.0, M["stone"])
    E(kit, ox, "text.pit", -14, 14, 3.2, 10, -1.0, -0.4, M["dark"])
    E(kit, ox, "text.body", -9.0, 9.0, 4.6, 6.2, 0.7, 3.8, M["body_navy"], bevel=0.08)
    E(kit, ox, "text.band", -9.01, 9.01, 4.55, 6.25, 1.2, 1.55, M["walnut"], bevel=0.02)
    E(kit, ox, "text.roof", -9.0, 9.0, 4.8, 6.0, 3.8, 4.0, M["navy"], bevel=0.2)
    E(kit, ox, "text.skirt", -9.0, 9.0, 4.7, 6.1, 0.35, 0.7, M["iron"])
    for i in range(10):
        x = -8.0 + i * 1.78
        E(kit, ox, f"text.win{i}", x - 0.6, x + 0.6, 4.52, 4.6, 2.0, 3.2, M["win_warm"])
        E(kit, ox, f"text.winf{i}", x - 0.66, x + 0.66, 4.5, 4.55, 1.95, 3.25, M["brass"])
    for i in range(4):
        E(kit, ox, f"text.wheel{i}", -7 + i * 4.5 - 0.5, -7 + i * 4.5 + 0.5, 4.8, 6.0, 0.05, 0.65, M["iron"])
    kit.light("text:key", "AREA", (ox - 3.0, -2.0, 4.8), 500.0, "#ffc58a", size=4.0)
    kit.aim(kit.LIGHTS["text:key"]["obj"], (ox, 4.6, 1.8))
    kit.light("text:fill", "AREA", (ox + 4.0, -3.0, 3.5), 260.0, "#8aa0d0", size=5.0)
    kit.aim(kit.LIGHTS["text:fill"]["obj"], (ox, 4.6, 1.8))
    kit.light("text:glow", "AREA", (ox, 3.2, 2.6), 160.0, "#e3a35c", size=7.0)
    kit.aim(kit.LIGHTS["text:glow"]["obj"], (ox, 0.0, 0.2))


# ------------------------------------------------------------------------------------------------- build
def build(kit, story, tl):
    ctx = {}
    M = materials(kit)
    ctx["M"] = M
    build_platform(kit, ctx, M)
    build_rooms(kit, ctx, M)
    build_flat(kit, ctx, M)
    build_text(kit, ctx, M)
    build_cabin(kit, ctx, M)
    build_stub(kit, ctx, M)
    build_corridor(kit, ctx, M)
    build_cafe(kit, ctx, M)
    build_glass(kit, ctx)
    # the moons: one disc per person
    mm = moon_mats(kit)
    ctx["moon_mats"] = mm
    ctx["moons"] = {}
    for name, spec in story.get("cast", {}).items():
        if spec.get("offscreen"):
            continue
        m = kit.plane(f"moon.{name}", (1, 1), (0, 0, -200), mm[1.0])
        ctx["moons"][name] = m
    ctx["spec"] = {s["id"]: s for s in story["shots"]}
    ctx["ladder_objs"] = [o for o in bpy.data.objects if o.name.startswith("cab.ladder") or o.name.startswith("cab.rung")]
    ctx["start"] = {s["id"]: s["start"] for s in tl["shots"]}
    ctx["lamp_node"] = [n for n in kit.MATS["ep44 corridor lamp shade"].node_tree.nodes if n.type == "EMISSION"][0]
    ctx["lamp_node"].inputs["Strength"].default_value = 1.6
    return ctx


# ----------------------------------------------------------------------------------------------- animate
def _ss(x):
    x = min(1.0, max(0.0, x))
    return x * x * (3 - 2 * x)


def _cues(tl, name):
    return [c for c in tl["cues"] if c["name"] == name]


def _shot(tl, t):
    for s in tl["shots"]:
        if s["start"] <= t < s["end"]:
            return s
    return tl["shots"][-1]


def cam_now(story, tl, t):
    import __main__

    shot = _shot(tl, t)
    spec = next(s for s in story["shots"] if s["id"] == shot["id"])
    if hasattr(__main__, "cam_at"):
        return V(__main__.cam_at(spec, shot, t, None, tl)[0])
    return V(spec["cam"][0][1])


def _fog_nodes(ctx):
    if "fog_nodes" not in ctx:
        from blocky import kit as _k

        d = _k.FOG["density"]
        ctx["fog_nodes"] = [nd for m in bpy.data.materials if m.node_tree for nd in m.node_tree.nodes
                            if nd.type == "MATH" and nd.operation == "MULTIPLY" and d > 0
                            and abs(nd.inputs[1].default_value + d) < 1e-6]
        fc = tuple(_k.FOG["color"])
        ctx["fog_cols"] = [nd for m in bpy.data.materials if m.node_tree for nd in m.node_tree.nodes
                           if nd.type == "EMISSION" and all(abs(a - b) < 1e-6 for a, b in
                                                             zip(nd.inputs["Color"].default_value[:3], fc))]
    return ctx["fog_nodes"]


def _tod_values(a, b, u):
    A, B = TODS[a], TODS[b]
    out = {}
    for k in ("world", "fog", "ground", "ground2", "hill", "win"):
        out[k] = _mix(lin(A[k]), lin(B[k]), u)
    for k in ("ws", "fd", "winE"):
        out[k] = A[k] + (B[k] - A[k]) * u
    return out


def apply_tod(kit, ctx, a, b, u):
    v = _tod_values(a, b, u)
    w = bpy.context.scene.world.node_tree.nodes["Background"]
    w.inputs["Color"].default_value = (*v["world"], 1)
    w.inputs["Strength"].default_value = v["ws"]
    _fog_nodes(ctx)
    for nd in ctx["fog_nodes"]:
        nd.inputs[1].default_value = -v["fd"]
    for nd in ctx["fog_cols"]:
        nd.inputs["Color"].default_value = (*v["fog"], 1)
    for L in ctx["land"]:
        L["ramp"].color_ramp.elements[0].color = (*v["ground"], 1)
        L["ramp"].color_ramp.elements[1].color = (*v["ground2"], 1)
        L["hill"].inputs["Color"].default_value = (*v["hill"], 1)
    return v


def _open_amt(cs, t):
    """0..1 from the door cues ({"to": 0|1, "dur"}): eases over each cue's own length."""
    prev, out = 0.0, 0.0
    for c in cs:
        if c["t"] > t:
            break
        d = c.get("dur", 0.7)
        u = 1.0 if d <= 0 else _ss((t - c["t"]) / d)
        out = prev + (c["to"] - prev) * u
        prev = c["to"] if u >= 1 else out
    return out


def lamp_gain(tl, t):
    """The corridor lamps' one fade: down over 1.5 s to 0.1, hold 1 s, back up over 1.5 s."""
    g = 1.0
    for c in _cues(tl, "lamps"):
        u = t - c["t"]
        if u < 0:
            continue
        if u < 1.5:
            g = 1.0 - 0.9 * _ss(u / 1.5)
        elif u < 2.5:
            g = 0.1
        elif u < 4.0:
            g = 0.1 + 0.9 * _ss((u - 2.5) / 1.5)
    return g


def animate(kit, story, tl, t, ctx):
    from blocky import acting as ac
    from blocky import kit as K

    shot = _shot(tl, t)
    spec = ctx["spec"][shot["id"]]
    cam = cam_now(story, tl, t)
    zone = min(OX, key=lambda k: abs(OX[k] - cam.x))
    tod = spec.get("tod", ZONE_TOD[zone])
    if isinstance(tod, str):
        a = b = tod
        u = 0.0
    else:
        a, b = tod
        u = _ss((t - shot["start"]) / spec.get("tod_dur", 2.0))
    v = apply_tod(K, ctx, a, b, u)
    over = {}
    lg = lamp_gain(tl, t)
    for name, L in K.LIGHTS.items():
        z = name.split(":")[0]
        g = 1.0 if z == zone else 0.0
        if g and ":win" in name:
            L["light"].color = v["win"]
            g = v["winE"]
        if g and name.startswith("cor:") and ("lamp" in name or "fill" in name):
            g *= lg
        if name == "cab:ladder":
            g *= 1.0 if shot["id"] == "S66" else 0.0
        if name == "cab:read":
            sid = shot["id"]
            g *= (1.0 if sid == "S14" else (1.0 - _ss((t - (shot["end"] - 0.4)) / 0.4)) if sid == "S15" else 0.0)
        if name == "cab:glow":
            t0 = ctx["start"].get("S54", 1e9)
            g *= _ss((t - t0) / 0.5) if t >= t0 else 0.0
        if name.startswith("cor:") and spec.get("dim"):
            g *= spec["dim"]
        if name.startswith("cab:stub"):
            g *= 0.5 + 0.5 * _open_amt(_cues(tl, "door_cab"), t)
        over[name] = g
    ctx["lamp_node"].inputs["Strength"].default_value = 1.6 * lg * (spec.get("dim") or 1.0)
    # the view outside slides by very slowly (no light moves; only soft shapes)
    for L in ctx["land"]:
        g = L["grp"]
        if L.get("rot"):
            g.location = (L["ox"] + 0.22 * t, 2.0, 0)
        elif L["ox"] == OX["cab"] - 4.0:
            g.location = (L["ox"], 0.22 * t, 0)
        else:
            g.location = (L["ox"], -0.22 * t, 0)
    # doors and the blankets
    for i, d in enumerate(ctx["cor_doors"]):
        amt = _open_amt(_cues(tl, "door_cor"), t) if i == OUR else 0.0
        d.location = (OX["cor"], DOOR_Y[i] + 1.3 * amt, 0)
    ctx["cab_door"].location = (OX["cab"], 1.3 * _open_amt(_cues(tl, "door_cab"), t), 0)
    ls = [c for c in _cues(tl, "lump") if c["t"] <= t]
    lump = bool(ls and ls[-1]["on"])
    ctx["blank_lump"].hide_render = not lump
    ctx["blank_lump2"].hide_render = not lump
    for o in ctx["ladder_objs"]:
        o.hide_render = shot["id"] == "S57"
    for o in ctx["tally"]:
        o.hide_render = shot["id"] != "S66"
    # people: sitting, bending; then their moons
    bpy.context.view_layer.update()
    for who, spec_c in story["cast"].items():
        if spec_c.get("offscreen"):
            continue
        keys = tl["acting"].get(who, [])
        if not keys:
            continue
        for sx in (-1, 1):
            leg = bpy.data.objects.get(f"{who}.leg{sx}")
            if leg is not None and ac._switch(keys, "sit", t, False):
                leg.rotation_euler = (-math.pi / 2, 0, 0)
        tor = bpy.data.objects.get(f"{who}.torso")
        if tor is not None:
            tor.rotation_euler = (math.radians(ac._held(keys, "bend", t, 0.0)), 0, 0)
    bpy.context.view_layer.update()
    pose_glass(tl, t, ctx)
    ash = ASH_PHASE.get(shot["id"], (0.15, 0.15))
    for who, mo in ctx["moons"].items():
        root = bpy.data.objects.get(who)
        hg = bpy.data.objects.get(f"{who}.headg")
        s = ac.state(tl, who, t)
        if root is None or hg is None or s["hidden"] or s["z"] < -50:
            mo.location = (0, 0, -200)
            continue
        if who == "ash":
            f = ash[0] + (ash[1] - ash[0]) * _ss((t - shot["start"]) / max(0.1, shot["end"] - shot["start"]))
        else:
            f = FIXED_MOON.get(who, 1.0)
        mo.data.materials[0] = ctx["moon_mats"][near_level(f)]
        hp = hg.matrix_world.translation
        sc = story["cast"][who].get("height", 1.0)
        pos = V((hp.x, hp.y, hp.z + 0.21 * sc + 0.22 + 0.1 * MOON_SCALE.get(who, 1.0)))
        mo.location = pos
        k = 0.2 * MOON_SCALE.get(who, 1.0)
        mo.scale = (k, k, k)
        mo.rotation_euler = (cam - pos).to_track_quat("Z", "Y").to_euler()
    return over
