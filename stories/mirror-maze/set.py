"""Mirror Maze (ep15, redo 2026-11-02): a travelling fair packing up in the rain, in a town where your reflection stays
in the glass when you walk away. The narrator is a leftover reflection in a maze pane; Tasha visits.
Built from kit.py's parts. Nothing in the set has text: no lettering, logos, signs, numbers or badges.

The set (kept from the first build): the rainy field with its duckboards and puddles, the crew's worklight, the maze
front with its lilac bulbs, the flatbed truck, the fry van, the far tarps and the dark wheel, and the maze's inside
(built at x = 60: a glass grid, the roof off).

What this redo adds:
- THE RIM: every leftover reflection (and the narrator) carries a thin lilac glow outline, our own marker. It is an
  inverted-hull shell per mesh (a copy pushed out along its normals and drawn only where it faces away), so it is a
  true outline that is never coplanar with anything. Old leftovers and the dark one carry a dull grey one.
- EXTRAS: a pool of strangers (story "extras") placed per shot by the "stage" cue: {"put": [{"who", "pos", "yaw",
  "expr", "arms", "head", "bow", "scale", "wave", "rim", "att"}]}. "att" pins one to the carried pane. "me" and "tr"
  (Tasha's reflection, the old copy model with normal eyes) take the same entries.
- THE DARK ONE ("dark"): a stranger in faded grey-violet, a head too tall, mirror-black eyes with no shine, a flat
  mouth, its rim dull grey. Built like the others, taller, with its head stretched.
- RAIN on Tasha's side only: 3D streaks inside the cue "rain" {"on", "box": [x0, x1, y0, y1]}; shots with me in them
  leave the 2D rain off.
- BREATH: a soft fog patch just in front of the stage pane on Tasha's side (cue "fog").
- THE TIP: cue "tilt" {"deg", "dur"} tips the carried pane's inside (its floor and me) about the pane's own axis.
Nothing is coplanar: shells, the fog patch, rain and panes are all offset from every other face.
"""

from __future__ import annotations

import copy as _copy
import math
import tempfile
from pathlib import Path

import bpy
import numpy as np
from mathutils import Matrix, Vector as V

from blocky import acting, rig, timeline

# ------------------------------------------------------------------------------------------------ the layout
BOARD_Z = 0.05                # the duckboards' top (everyone on the boards stands at this z)
MAZE_Y = 12.0                 # the maze's front face
MAZE_X0, MAZE_X1 = -3.5, 9.5  # the trailer's ends
MAZE_D = 7.0                  # the trailer's depth (+y from the front)
PLAT_Z = 1.05                 # the trailer's floor and the deck in front of the arch
FACADE_H = 4.3                # the facade's height above the platform
ARCH_X = 3.0                  # the arch's centre line
ARCH_R = 1.5                  # the arch: half its width, and the radius of its round top
ARCH_SIDE = 1.9               # the arch's straight sides, above the platform
DECK_D = 1.8                  # the deck in front of the arch (the steps come down off it)
WORK = (2.05, 3.55)           # the crew's worklight, near the rink
GX0, GX1, GY0, GY1 = 0.5, 5.5, 12.1, 17.6   # the gallery behind the arch
GZ = PLAT_Z + 3.6
LILAC = "#a066ff"             # the leftover rim: a cooler lilac than the bulbs
GREYRIM = "#7a7484"           # the dark one's, and the old leftovers'

VIOLET = "#5d4a72"            # the facade's faded violet
SILVER = "#a4a2b0"            # and its silver
BULB = "#efe6ff"              # the lilac-white bulbs
GLOW = "#c9b8ff"              # their light


def kit_ss(x):
    x = min(1.0, max(0.0, x))
    return x * x * (3 - 2 * x)


def cue_at(tl, name, t):
    """The latest cue of this name at or before t (its dict), or {}."""
    out = {}
    for c in tl.get("cues", []):
        if c["name"] == name and c["t"] <= t + 1e-9:
            out = c
    return out


def _shot(tl, t):
    for s in tl["shots"]:
        if s["start"] <= t < s["end"]:
            return s
    return tl["shots"][-1]


# ------------------------------------------------------------------------------------------------ materials


def pbr(kit, name, hexc, rough=0.5, metal=0.0, coat=0.0, spec=0.5, noise=None):
    """A Principled material through kit's fog. noise = (scale, dark factor, rough variation) mottles the colour and
    the wetness, for mud and wet boards."""
    if name in kit.MATS:
        return kit.MATS[name]
    m = kit._new(name)
    N, L = m.node_tree.nodes, m.node_tree.links
    b = N["Principled BSDF"]
    b.inputs["Base Color"].default_value = kit.col(hexc)
    b.inputs["Roughness"].default_value = rough
    b.inputs["Metallic"].default_value = metal
    for k in ("Specular IOR Level", "Specular"):
        if k in b.inputs:
            b.inputs[k].default_value = spec
            break
    if coat:
        b.inputs["Coat Weight"].default_value = coat
        b.inputs["Coat Roughness"].default_value = 0.08
    if noise:
        tc = N.new("ShaderNodeTexCoord")
        nz = N.new("ShaderNodeTexNoise")
        nz.inputs["Scale"].default_value = noise[0]
        nz.inputs["Detail"].default_value = 5.0
        L.new(tc.outputs["Object"], nz.inputs["Vector"])
        ramp = N.new("ShaderNodeValToRGB")
        c = kit.col(hexc)
        ramp.color_ramp.elements[0].position = 0.3
        ramp.color_ramp.elements[0].color = (c[0] * noise[1], c[1] * noise[1], c[2] * noise[1], 1)
        ramp.color_ramp.elements[1].position = 0.7
        ramp.color_ramp.elements[1].color = c
        L.new(nz.outputs["Fac"], ramp.inputs["Fac"])
        L.new(ramp.outputs["Color"], b.inputs["Base Color"])
        rr = N.new("ShaderNodeMapRange")   # the darker patches are the wetter ones
        rr.inputs["To Min"].default_value = max(0.02, rough - noise[2])
        rr.inputs["To Max"].default_value = min(1.0, rough + noise[2])
        L.new(nz.outputs["Fac"], rr.inputs["Value"])
        L.new(rr.outputs["Result"], b.inputs["Roughness"])
    m.diffuse_color = kit.col(hexc)
    kit._fogged(m, b.outputs[0])
    return m


def materials(kit):
    M = {}
    M["mud"] = pbr(kit, "mud", "#2a2127", 0.42, spec=0.5, noise=(1.3, 0.55, 0.3))
    M["boards"] = kit.planks("#4d3c33", "#2c221d", 1.0, "Y", name="duckboards wet", rough=0.3)
    M["batten"] = pbr(kit, "batten", "#231b17", 0.6)
    M["puddle"] = pbr(kit, "puddle", "#060509", 0.03, spec=0.8)
    M["trailer"] = pbr(kit, "trailer", "#26202e", 0.55)
    M["skirt"] = pbr(kit, "skirt", "#141118", 0.7)
    M["violet"] = pbr(kit, "violet", VIOLET, 0.5, coat=0.3)
    M["violet_d"] = pbr(kit, "violet dark", "#3a2e4a", 0.55)
    M["silver"] = kit.metal(SILVER, 0.32)
    M["steel"] = kit.metal("#6c6a74", 0.4)
    M["steel_d"] = kit.metal("#3a3940", 0.5)
    M["bulb"] = kit.emit(BULB, 7.0, name="bulb")
    M["socket"] = pbr(kit, "socket", "#1a1820", 0.5, metal=0.6)
    M["inside"] = pbr(kit, "maze inside", "#120f17", 0.8)
    M["ply"] = kit.planks("#3f3229", "#2a211b", 0.7, "X", name="maze floor", rough=0.55)
    M["glass"] = glass(kit, "pane")
    M["lamp_body"] = pbr(kit, "lamp body", "#2b2a2e", 0.45, metal=0.5)
    M["lamp_lens"] = kit.emit("#e6ecff", 6.0, name="lamp lens")
    M["cage"] = kit.metal("#222125", 0.5)
    return M


def glass(kit, name):
    """A tall clear pane: almost all see-through, a little reflection on top (the maze's panes are windows, not
    mirrors, with the mirrored corridor built behind them)."""
    if name in kit.MATS:
        return kit.MATS[name]
    m = kit._new(name)
    N, L = m.node_tree.nodes, m.node_tree.links
    N.remove(N["Principled BSDF"])
    tr = N.new("ShaderNodeBsdfTransparent")
    tr.inputs["Color"].default_value = (0.93, 0.92, 0.97, 1)
    gl = N.new("ShaderNodeBsdfGlossy")
    gl.inputs["Roughness"].default_value = 0.02
    gl.inputs["Color"].default_value = (0.9, 0.9, 0.95, 1)
    fr = N.new("ShaderNodeFresnel")
    fr.inputs["IOR"].default_value = 1.45
    mix = N.new("ShaderNodeMixShader")
    L.new(fr.outputs[0], mix.inputs[0])
    L.new(tr.outputs[0], mix.inputs[1])
    L.new(gl.outputs[0], mix.inputs[2])
    kit._fogged(m, mix.outputs[0])
    return m


# ------------------------------------------------------------------------------------------------ the field


def blob(kit, name, cx, cy, r, mat, seed, z, n=40, wob=0.28):
    """A puddle: a flat disc with a lumpy edge."""
    rng = np.random.default_rng(seed)
    ph = rng.uniform(0, 2 * math.pi, 3)
    verts = [(cx, cy, z)]
    for j in range(n):
        a = 2 * math.pi * j / n
        k = 1 + wob * (0.5 * math.sin(2 * a + ph[0]) + 0.3 * math.sin(3 * a + ph[1]) + 0.2 * math.sin(5 * a + ph[2]))
        verts.append((cx + r * k * math.cos(a), cy + r * k * 0.8 * math.sin(a), z))
    fcs = [(0, 1 + j, 1 + (j + 1) % n) for j in range(n)]
    ob = kit.mesh_obj(name, verts, fcs, mat)
    ob.visible_shadow = False
    return ob


def duckboard(kit, M, name, cx, cy, yaw, w=1.22, l=2.44):
    """A plywood duckboard on two battens, its top at BOARD_Z."""
    top = kit.empty(name, (cx, cy, 0.0), rot=(0, 0, math.radians(yaw)))
    kit.box(f"{name}.ply", (w, l, 0.03), (0, 0, BOARD_Z - 0.015), M["boards"], top, bevel=0.008)
    for sx in (-1, 1):
        kit.box(f"{name}.bat{sx}", (0.07, l - 0.1, 0.03), (sx * (w / 2 - 0.12), 0, 0.012), M["batten"], top)
    return top


def build_field(kit, ctx, M):
    kit.plane("field", (120, 120), (0, 10, 0), M["mud"])
    # the walkway: two lanes of boards from the maze's steps out across the field, a little crooked, as a crew lays
    # them. The scare's spot is on the boards near the worklight
    rng = np.random.default_rng(14)
    k = 0
    for lane, x in ((0, -0.2), (1, 1.04)):
        y = -3.0
        while y < MAZE_Y - DECK_D - 0.6:
            duckboard(kit, M, f"duck{k}", x + rng.uniform(-0.05, 0.05), y + 1.22, rng.uniform(-2.2, 2.2))
            y += 2.48 + rng.uniform(0.0, 0.06)
            k += 1
    # big still puddles on the boards and in the mud: they mirror the maze (the puddle-side plant)
    pz = BOARD_Z + 0.002
    for i, (x, y, r, z) in enumerate(((0.62, 4.05, 0.42, pz), (0.2, 6.3, 0.55, pz), (1.3, 1.2, 0.35, pz),
                                     (-1.6, 5.2, 1.0, 0.004), (2.6, 7.4, 1.3, 0.004), (-2.4, 9.0, 0.9, 0.004))):
        blob(kit, f"puddle{i}", x, y, r, M["puddle"], 40 + i, z)


def build_worklight(kit, ctx, M):
    """The crew's caged worklight on a low tripod, left on. Steady, never flickers: the scare's light from below."""
    x, y = WORK
    root = kit.empty("worklight", (x, y, BOARD_Z))
    for k in range(3):
        a = 2 * math.pi * k / 3 + 0.4
        dx, dy = 0.32 * math.cos(a), 0.32 * math.sin(a)
        leg = kit.cyl(f"wl.leg{k}", 0.014, 0.64, (dx / 2, dy / 2, 0.275), M["steel_d"], root, n=8)
        leg.rotation_euler = V((-dx, -dy, 0.55)).to_track_quat("Z", "Y").to_euler()   # foot out, top at the mast
    kit.cyl("wl.mast", 0.02, 0.18, (0, 0, 0.6), M["steel_d"], root, n=10)
    head = kit.empty("wl.head", (0, 0, 0.72), root)
    kit.box("wl.body", (0.3, 0.16, 0.24), (0, 0.02, 0), M["lamp_body"], head, bevel=0.02)
    kit.box("wl.lens", (0.24, 0.02, 0.18), (0, -0.065, 0), M["lamp_lens"], head)
    for k in range(5):   # the cage's bars across the front
        kit.box(f"wl.bar{k}", (0.012, 0.012, 0.26), (-0.12 + k * 0.06, -0.09, 0), M["cage"], head)
    kit.box("wl.barh", (0.3, 0.012, 0.012), (0, -0.09, 0.0), M["cage"], head)
    ctx["work_head"] = head
    ctx["work_root"] = root


# ------------------------------------------------------------------------------------------------ the maze front


def arch_outline(off, n_arc=24):
    """Points (x, z) round the arch's opening, `off` outside its edge: up the left side, over the round top, down the
    right side."""
    r = ARCH_R + off
    zc = PLAT_Z + ARCH_SIDE
    pts = [(ARCH_X - r, PLAT_Z + 0.12 + (zc - PLAT_Z - 0.12) * i / 6) for i in range(6)]
    pts += [(ARCH_X - r * math.cos(math.pi * i / n_arc), zc + r * math.sin(math.pi * i / n_arc)) for i in range(n_arc + 1)]
    pts += [(ARCH_X + r, zc - (zc - PLAT_Z - 0.12) * i / 6) for i in range(1, 7)]
    return pts


def _resample(pts, step):
    """Points every `step` metres along a polyline."""
    out, carry = [pts[0]], 0.0
    for (x0, z0), (x1, z1) in zip(pts, pts[1:]):
        seg = math.hypot(x1 - x0, z1 - z0)
        d = step - carry
        while d <= seg:
            u = d / seg
            out.append((x0 + (x1 - x0) * u, z0 + (z1 - z0) * u))
            d += step
        carry = seg - (d - step)
    return out


def spandrel(kit, name, mat, y, z_top):
    """The facade above and beside the arch's round top: a sheet from the round edge out to a rectangle."""
    zc = PLAT_Z + ARCH_SIDE
    x0, x1 = ARCH_X - ARCH_R, ARCH_X + ARCH_R
    corners = [math.atan2(z_top - zc, x1 - ARCH_X), math.atan2(z_top - zc, x0 - ARCH_X)]
    angs = sorted(set([math.pi * i / 32 for i in range(33)] + corners))
    verts, fcs = [], []
    for a in angs:
        ca, sa = math.cos(a), math.sin(a)
        verts.append((ARCH_X + ARCH_R * ca, y, zc + ARCH_R * sa))
        # out along the same direction to the rectangle's edge
        tx = (ARCH_R / abs(ca)) if abs(ca) > 1e-6 else 1e9
        tz = (z_top - zc) / sa if sa > 1e-6 else 1e9
        tt = min(tx, tz)
        verts.append((ARCH_X + tt * ca, y, zc + tt * sa))
    for i in range(len(angs) - 1):
        a, b = 2 * i, 2 * (i + 1)
        fcs.append((a, b, b + 1, a + 1))
    return kit.mesh_obj(name, verts, fcs, mat)


def build_maze(kit, ctx, M):
    y0 = MAZE_Y
    top = PLAT_Z + FACADE_H
    # the trailer: its body behind the facade, a dark skirt down to the mud, the deck and the steps
    # the trailer's body, hollow behind the arch: a gallery x GX0..GX1, y GY0..GY1, up to GZ
    top_ = PLAT_Z + FACADE_H + 0.2
    kit.box("maze.bodyL", (GX0 - MAZE_X0, MAZE_D, FACADE_H + 0.2), ((MAZE_X0 + GX0) / 2, y0 + MAZE_D / 2 + 0.05, PLAT_Z + FACADE_H / 2), M["trailer"])
    kit.box("maze.bodyR", (MAZE_X1 - GX1, MAZE_D, FACADE_H + 0.2), ((MAZE_X1 + GX1) / 2, y0 + MAZE_D / 2 + 0.05, PLAT_Z + FACADE_H / 2), M["trailer"])
    kit.box("maze.bodyT", (GX1 - GX0, MAZE_D, top_ - GZ), ((GX0 + GX1) / 2, y0 + MAZE_D / 2 + 0.05, (top_ + GZ) / 2), M["trailer"])
    kit.box("maze.bodyB", (GX1 - GX0, y0 + MAZE_D + 0.1 - GY1, FACADE_H + 0.2), ((GX0 + GX1) / 2, (GY1 + y0 + MAZE_D + 0.1) / 2, PLAT_Z + FACADE_H / 2), M["inside"])
    kit.box("maze.skirt", (MAZE_X1 - MAZE_X0, MAZE_D, PLAT_Z), ((MAZE_X0 + MAZE_X1) / 2, y0 + MAZE_D / 2, PLAT_Z / 2),
            M["skirt"])
    kit.box("maze.deck", (5.0, DECK_D, 0.12), (ARCH_X, y0 - DECK_D / 2, PLAT_Z - 0.06), M["ply"], bevel=0.01)
    kit.box("maze.deckskirt", (5.0, DECK_D - 0.1, PLAT_Z - 0.12), (ARCH_X, y0 - DECK_D / 2 + 0.05, (PLAT_Z - 0.12) / 2),
            M["skirt"])
    n_steps = 5
    for k in range(n_steps):
        h = PLAT_Z * (k + 1) / (n_steps + 1)
        kit.box(f"maze.step{k}", (1.8, 0.3, 0.06), (ARCH_X, y0 - DECK_D - 0.3 * (n_steps - k) + 0.15, h), M["steel"],
                bevel=0.01)
    for sx in (-1, 1):   # the deck's rails
        x = ARCH_X + sx * 2.45
        for k in range(3):
            kit.cyl(f"maze.post{sx}{k}", 0.025, 1.0, (x, y0 - 0.1 - k * 0.8, PLAT_Z + 0.5), M["steel"], n=8)
        kit.box(f"maze.rail{sx}", (0.05, DECK_D, 0.05), (x, y0 - DECK_D / 2, PLAT_Z + 1.0), M["steel"], bevel=0.01)
    # the facade: plain geometric panels (stripes along the top, diamonds on the wings), no faces, eyes or words
    fy = y0 - 0.03
    xl, xr = ARCH_X - ARCH_R, ARCH_X + ARCH_R
    kit.box("maze.wingL", (xl - MAZE_X0, 0.06, FACADE_H), ((MAZE_X0 + xl) / 2, fy, PLAT_Z + FACADE_H / 2),
            M["violet_d"])
    kit.box("maze.wingR", (MAZE_X1 - xr, 0.06, FACADE_H), ((MAZE_X1 + xr) / 2, fy, PLAT_Z + FACADE_H / 2),
            M["violet_d"])
    spandrel(kit, "maze.spandrel", M["violet_d"], fy - 0.031, top)
    # stripes: a frieze of upright violet and silver bands above the arch, under the roofline
    k = 0
    x = MAZE_X0 + 0.1
    while x < MAZE_X1 - 0.3:
        kit.box(f"maze.stripe{k}", (0.32, 0.04, 0.55), (x + 0.16, fy - 0.05, top - 0.42),
                M["silver" if k % 2 else "violet"], bevel=0.01)
        x += 0.4
        k += 1
    # diamonds on the wings, two rows
    for wing, (a, b) in (("L", (MAZE_X0 + 0.5, xl - 0.9)), ("R", (xr + 0.9, MAZE_X1 - 0.5))):
        n = max(1, int((b - a) / 0.95))
        for i in range(n + 1):
            x = a + (b - a) * i / max(1, n)
            for j, z in enumerate((PLAT_Z + 1.2, PLAT_Z + 2.35)):
                kit.box(f"maze.dia{wing}{i}{j}", (0.5, 0.04, 0.5), (x, fy - 0.05, z), M["silver" if (i + j) % 2 else "violet"],
                        rot=(0, math.radians(45), 0), bevel=0.01)
    # the arch's own frame, a silver band round the opening
    pts = arch_outline(0.04, 32)
    for i, ((x0, z0), (x1, z1)) in enumerate(zip(pts, pts[1:])):
        seg = math.hypot(x1 - x0, z1 - z0)
        kit.box(f"maze.archf{i}", (seg + 0.02, 0.08, 0.08), ((x0 + x1) / 2, fy - 0.06, (z0 + z1) / 2), M["silver"],
                rot=(0, -math.atan2(z1 - z0, x1 - x0), 0))
    # the bulbs: two rows round the arch and one along the roofline. Steady, never chasing
    bulbs = []
    for row, off, step in (("a", 0.2, 0.26), ("b", 0.44, 0.28)):
        for i, (x, z) in enumerate(_resample(arch_outline(off, 48), step)):
            bulbs.append((f"bulb{row}{i}", x, z))
    for i in range(int((MAZE_X1 - MAZE_X0 - 0.4) / 0.32) + 1):
        bulbs.append((f"bulbr{i}", MAZE_X0 + 0.2 + i * 0.32, top - 0.05))
    for nm, x, z in bulbs:
        kit.sphere(nm, 0.055, (x, fy - 0.11, z), M["bulb"], seg=12)
        kit.cyl(f"{nm}.s", 0.035, 0.05, (x, fy - 0.07, z), M["socket"], rot=(math.radians(90), 0, 0), n=8)
    ctx["bulbs"] = len(bulbs)
    # the gallery behind the arch: a ply floor and a row of panes on stands (build_gallery adds the leftovers' panes)
    kit.box("maze.innerfloor", (GX1 - GX0, GY1 - GY0, 0.04), ((GX0 + GX1) / 2, (GY0 + GY1) / 2, PLAT_Z + 0.02), M["ply"])



def make_pane(kit, M, name, loc, yaw=0.0, w=1.1, h=2.3, frame="steel", bulbs=0, parent=None):
    """A clear pane in a steel frame, standing on loc. The frame is deeper than the glass, so nothing is coplanar."""
    p = kit.empty(name, loc, parent, rot=(0, 0, math.radians(yaw)))
    kit.box(f"{name}.g", (w, 0.012, h), (0, 0, h / 2 + 0.05), M["glass"], p)
    for sx in (-1, 1):
        kit.box(f"{name}.f{sx}", (0.05, 0.05, h + 0.15), (sx * (w / 2 + 0.025), 0, h / 2 + 0.07), M[frame], p)
    kit.box(f"{name}.top", (w + 0.1, 0.05, 0.05), (0, 0, h + 0.1), M[frame], p)
    kit.box(f"{name}.bot", (w + 0.1, 0.05, 0.05), (0, 0, 0.03), M[frame], p)
    for k in range(bulbs):
        kit.sphere(f"{name}.b{k}", 0.04, (-w * 0.38 + k * w * 0.76 / max(1, bulbs - 1), -0.045, h + 0.18), M["bulb"], p, seg=10)
    return p


# ------------------------------------------------------------------------------------------------ the rim


def rim_mat(kit, name, hexc, strength):
    """Only the faces that face away from the camera glow, so a copy of a mesh pushed out a little shows as an outline
    round the silhouette and is invisible where the real mesh is in front of it."""
    if name in kit.MATS:
        return kit.MATS[name]
    m = kit._new(name)
    N, L = m.node_tree.nodes, m.node_tree.links
    N.remove(N["Principled BSDF"])
    geo = N.new("ShaderNodeNewGeometry")
    tr = N.new("ShaderNodeBsdfTransparent")
    em = N.new("ShaderNodeEmission")
    em.inputs["Color"].default_value = kit.col(hexc)
    em.inputs["Strength"].default_value = strength
    mix = N.new("ShaderNodeMixShader")
    L.new(geo.outputs["Backfacing"], mix.inputs[0])
    L.new(tr.outputs[0], mix.inputs[1])
    L.new(em.outputs[0], mix.inputs[2])
    out = next(n for n in N if n.type == "OUTPUT_MATERIAL")
    L.new(mix.outputs[0], out.inputs["Surface"])
    try:
        m.emission_sampling = "NONE"
    except Exception:
        pass
    return m


def add_rim(kit, root, mat, grow):
    """A shell for every mesh under `root`: parented to it with an identity transform, so it follows every pose."""
    shells = []
    for ob in list(root.children_recursive):
        if ob.type != "MESH" or ob.name.endswith(".rim"):
            continue
        me = ob.data.copy()
        me.materials.clear()
        me.materials.append(mat)
        for p in me.polygons:
            p.material_index = 0
        sh = bpy.data.objects.new(ob.name + ".rim", me)
        kit.link(sh, ob)
        sh.visible_shadow = False
        md = sh.modifiers.new("grow", "DISPLACE")
        md.strength, md.mid_level, md.direction = grow, 0.0, "NORMAL"
        shells.append(sh)
    return shells


def show_rim(shells, on):
    for s in shells:
        s.hide_render = not on


# ------------------------------------------------------------------------------------------------ the gallery (the hook)


def build_gallery(kit, ctx, M):
    """Behind the arch: a row of panes on stands. The strangers (stage cue) stand behind them in two rows."""
    for i, x in enumerate((1.8, 3.0, 4.2)):
        make_pane(kit, M, f"gal{i}", (x, 13.3, PLAT_Z + 0.02), 0, 1.1, 2.3, "silver", 0, None)
    kit.light("gal", "AREA", (ARCH_X, 14.2, PLAT_Z + 3.4), 600.0, "#d8d0ff", size=4.0)
    kit.LIGHTS["gal"]["obj"].rotation_euler = (0, 0, 0)
    kit.LIGHTS["gal"]["obj"].visible_camera = False


# ------------------------------------------------------------------------------------------------ the truck
TRUCK = (-4.2, 7.2)           # the flatbed's middle; it runs along x, its near side faces -y
TRUCK_L, TRUCK_W, BED_Z = 7.2, 2.4, 1.15


def build_truck(kit, ctx, M):
    """The crew's flatbed: no badge, no plate, no lettering. Its bed carries five panes standing in a row (four hold
    leftovers, one is brand new and empty) and is bare otherwise: the last pane of the night is set down on it."""
    x0, y0 = TRUCK
    paint = pbr(kit, "truck paint", "#2c2f38", 0.45, coat=0.3)
    rubber = pbr(kit, "tyre", "#111113", 0.8)
    win = pbr(kit, "cab glass", "#0c0d12", 0.05, spec=0.6)
    kit.box("truck.chassis", (TRUCK_L, 1.0, 0.35), (x0, y0, 0.75), M["steel_d"], bevel=0.03)
    kit.box("truck.bed", (TRUCK_L - 2.2, TRUCK_W, 0.14), (x0 - 1.1, y0, BED_Z - 0.07), M["steel"], bevel=0.02)
    kit.box("truck.cab", (2.0, TRUCK_W, 1.9), (x0 + TRUCK_L / 2 - 1.0, y0, 1.6), paint, bevel=0.12)
    kit.box("truck.wind", (0.06, TRUCK_W - 0.4, 0.7), (x0 + TRUCK_L / 2 + 0.01, y0, 2.05), win)
    for sy in (-1, 1):
        kit.box(f"truck.side{sy}", (0.9, 0.05, 0.6), (x0 + TRUCK_L / 2 - 1.0, y0 + sy * (TRUCK_W / 2 + 0.005), 2.05), win)
    for i, wx in enumerate((x0 + TRUCK_L / 2 - 1.2, x0 - 0.9, x0 - 2.3)):
        for sy in (-1, 1):
            kit.cyl(f"truck.wheel{i}{sy}", 0.5, 0.36, (wx, y0 + sy * (TRUCK_W / 2 - 0.18), 0.5), rubber,
                    rot=(math.radians(90), 0, 0), n=24)
    # a low headboard behind the cab, so the bed reads as a bed
    kit.box("truck.head", (0.12, TRUCK_W, 0.5), (x0 + 1.5, y0, BED_Z + 0.25), M["steel_d"], bevel=0.02)
    ctx["truckpanes"] = []
    for i in range(5):
        p = make_pane(kit, M, f"tp{i}", (x0 - 3.2 + i * 1.0, y0 - 0.55, BED_Z), 0, 0.9, 2.0, "steel", 0, None)
        ctx["truckpanes"].append(p)
    ctx["truck"] = TRUCK


# ------------------------------------------------------------------------------------------------ the rest of the fair
VAN = (1.0, -16.0)            # the fry van, far down the walkway (its hatch faces +y, toward the maze)
IX = 60.0                     # the maze's inside is built here, out in the dark (its own lights), cut to on the action
PANE_Y1 = 12.8                # the stage pane: Tasha on the -y side, me on the +y side


def tarp_mat(kit):
    return pbr(kit, "tarp", "#34364a", 0.7, noise=(3.0, 0.6, 0.1))


def build_far(kit, ctx, M):
    tarp = tarp_mat(kit)
    for i, (x, y, w, d, h) in enumerate(((-9.0, 3.0, 4.0, 3.0, 2.2), (-12.5, 9.0, 3.5, 5.0, 3.0), (11.0, -1.0, 4.5, 3.0, 2.6),
                                         (13.5, 14.0, 5.0, 5.0, 3.4), (-7.5, -6.0, 3.0, 3.0, 1.8), (8.0, -9.0, 3.5, 3.0, 2.0))):
        kit.box(f"ride{i}", (w, d, h), (x, y, h / 2), tarp, bevel=0.35)
        kit.box(f"ride{i}.top", (w * 0.6, d * 0.6, h * 0.5), (x, y, h + h * 0.18), tarp, bevel=0.3)
    wx, wy, wz, R = -12.0, 21.0, 6.5, 5.0
    for k in range(40):
        a = 2 * math.pi * k / 40
        kit.box(f"wheel.rim{k}", (0.22, 0.22, 2 * math.pi * R / 40 + 0.05), (wx, wy, wz), M["steel_d"],
                rot=(0, 0, 0)).location = (wx + R * math.cos(a), wy, wz + R * math.sin(a))
    for k in range(40):
        a = 2 * math.pi * k / 40
        bpy.data.objects[f"wheel.rim{k}"].rotation_euler = (0, -a, 0)
    for k in range(10):
        a = math.pi * k / 10
        kit.box(f"wheel.spoke{k}", (0.1, 0.1, 2 * R), (wx, wy, wz), M["steel_d"], rot=(0, math.pi / 2 - a, 0))
    kit.box("wheel.legL", (0.4, 0.4, wz + 0.3), (wx - 2.5, wy, (wz) / 2), M["steel_d"], rot=(0, math.radians(-22), 0))
    kit.box("wheel.legR", (0.4, 0.4, wz + 0.3), (wx + 2.5, wy, (wz) / 2), M["steel_d"], rot=(0, math.radians(22), 0))
    for k in (1, 4, 6, 9, 13, 16, 22, 29, 34):
        a = 2 * math.pi * k / 40
        kit.box(f"wheel.car{k}", (1.0, 0.8, 0.8), (wx + R * math.cos(a), wy, wz + R * math.sin(a) - 0.5), M["trailer"], bevel=0.1)

    # the fry van: boxy, a lit hatch with a steel counter; beside it a long steel-framed glass side with the queue behind
    vx, vy = VAN
    vpaint = pbr(kit, "van paint", "#3a2f34", 0.5, coat=0.2)
    kit.box("van.body", (4.0, 2.2, 2.5), (vx + 0.5, vy - 0.0, 1.25 + 0.3), vpaint, bevel=0.1)
    for sx in (-1, 1):
        kit.cyl(f"van.wheel{sx}", 0.4, 0.3, (vx + 0.5 + sx * 1.3, vy + 1.1, 0.4), pbr(kit, "tyre2", "#111113", 0.8),
                rot=(0, math.radians(90), 0), n=20)
    kit.box("van.hatch", (1.6, 0.04, 0.8), (vx - 0.3, vy + 1.12, 1.55), kit.emit("#ffb35c", 0.45, name="van glow"))
    kit.box("van.counter", (1.9, 0.5, 0.06), (vx - 0.3, vy + 1.38, 1.1), M["steel"], bevel=0.01)
    kit.box("van.awning", (2.1, 0.7, 0.05), (vx - 0.3, vy + 1.4, 2.12), vpaint, rot=(math.radians(-8), 0, 0))
    polished = kit.metal("#c9ccd4", 0.07, name="polished steel")
    kit.box("van.skirt", (5.4, 0.06, 0.5), (vx + 5.6, vy + 1.3, 0.3), polished)
    for i in range(5):
        make_pane(kit, M, f"qp{i}", (vx + 3.3 + i * 1.12, vy + 1.3, 0.05), 0, 1.0, 2.2, "steel", 0, None)

    # the pane the maze guy carries: steel frame, glass, and a shallow floor behind it that tips with me
    pn = kit.empty("carried pane", (0, 0, -20))
    kit.box("carried.g", (2.2, 0.014, 2.3), (0, 0, 1.2), M["glass"], pn)
    for sx in (-1, 1):
        kit.box(f"carried.f{sx}", (0.09, 0.09, 2.45), (sx * 1.145, 0, 1.22), M["silver"], pn)
    kit.box("carried.top", (2.4, 0.09, 0.09), (0, 0, 2.44), M["silver"], pn)
    kit.box("carried.bot", (2.4, 0.09, 0.09), (0, 0, -0.01), M["silver"], pn)
    fl = kit.empty("carried floor", (0, 0.45, 0.0), pn)
    kit.box("carried.floorm", (2.0, 0.9, 0.05), (0, 0, 0.0), M["ply"], fl)
    ctx["carried"] = pn
    ctx["carried_floor"] = fl


# ------------------------------------------------------------------------------------------------ the maze's inside


def build_inside(kit, ctx, M):
    cy = 7.0
    kit.box("in.floor", (16.0, 24.0, 0.04), (IX, cy + 3.0, 0.0), M["ply"])
    ceil = kit.box("in.ceiling", (16.0, 24.0, 0.05), (IX, cy + 3.0, 3.25), tarp_mat(kit))
    ctx["ceiling"] = ceil
    k = 0
    ctx["ip"] = []
    for wx in (-3.75, -2.25, -0.75, 0.75, 2.25, 3.75):
        for j in range(12):
            y = 0.6 + j * 1.15
            p = kit.empty(f"ip{k}", (IX + wx, y, 0.04), rot=(0, 0, math.radians(90)))
            kit.box(f"ip{k}.g", (1.1, 0.012, 2.3), (0, 0, 1.2), M["glass"], p)
            for sx in (-1, 1):
                kit.box(f"ip{k}.f{sx}", (0.05, 0.05, 2.45), (sx * 0.575, 0, 1.22), M["steel"], p)
            kit.box(f"ip{k}.top", (1.2, 0.05, 0.05), (0, 0, 2.44), M["steel"], p)
            if abs(wx) < 3:
                for b in range(3):
                    kit.sphere(f"ip{k}.b{b}", 0.04, (-0.35 + b * 0.35, 0.0, 2.52), M["bulb"], p, seg=8)
            ctx["ip"].append((p, wx, j))
            k += 1
    # the stage pane (Tasha on its -y side, me on its +y side), and the back pane behind me
    ctx["stage"] = make_pane(kit, M, "stage", (IX, PANE_Y1, 0.04), 0, 1.4, 2.3, "silver", 0, None)
    make_pane(kit, M, "backpane", (IX, 16.6, 0.04), 0, 1.4, 2.3, "steel", 0, None)
    rng = np.random.default_rng(5)
    for i in range(16):   # the maze's bulbs behind me, so my rim reads as their light
        kit.sphere(f"backbulb{i}", 0.055, (IX + rng.uniform(-1.5, 1.5), 17.1 + rng.uniform(0, 0.4), rng.uniform(0.4, 2.7)), M["bulb"], seg=10)
    # its lights: two soft lilac-white panels over the corridor
    kit.light("room", "AREA", (IX, 3.5, 3.0), 900.0, "#d8d0ff", size=3.0)
    kit.LIGHTS["room"]["obj"].rotation_euler = (0, 0, 0)
    kit.light("roomb", "AREA", (IX, 10.0, 3.0), 900.0, "#d8d0ff", size=3.0)
    kit.LIGHTS["roomb"]["obj"].rotation_euler = (0, 0, 0)
    kit.light("camfill", "POINT", (0, 0, 3), 420.0, "#a8a2d8", size=0.7, shadow=False)
    kit.light("amb", "AREA", (3.0, 0.0, 12.0), 2200.0, "#8d84b8", size=22.0)
    kit.LIGHTS["amb"]["obj"].rotation_euler = (0, 0, 0)
    kit.light("van", "AREA", (VAN[0] - 0.3, VAN[1] + 1.5, 2.0), 0.0, "#ffb060", size=1.4)
    for nm in ("room", "roomb", "amb", "van"):
        kit.LIGHTS[nm]["obj"].visible_camera = False



def matte_eyes(kit, ch):
    """No glint, glow or reflection in the copy's eyes: wherever its face texture is the eyes' near-black (darker than
    any ink), the head's surface is fully rough and has no specular, so a light can't catch in them."""
    nt = ch.head_mat.node_tree
    N, L = nt.nodes, nt.links
    b = N["Principled BSDF"]
    g = N.new("ShaderNodeGamma")   # back to display values, where the eyes' 10/255 and the ink's 34/255 are apart
    g.inputs["Gamma"].default_value = 1 / 2.2
    L.new(ch.face_tex.outputs["Color"], g.inputs["Color"])
    sep = N.new("ShaderNodeSeparateColor")
    L.new(g.outputs[0], sep.inputs[0])
    m1 = N.new("ShaderNodeMath")
    m1.operation = "MAXIMUM"
    L.new(sep.outputs[0], m1.inputs[0])
    L.new(sep.outputs[1], m1.inputs[1])
    m2 = N.new("ShaderNodeMath")
    m2.operation = "MAXIMUM"
    L.new(m1.outputs[0], m2.inputs[0])
    L.new(sep.outputs[2], m2.inputs[1])
    mask = N.new("ShaderNodeMapRange")   # 1 inside the eyes, 0 elsewhere
    mask.inputs["From Min"].default_value = 0.06
    mask.inputs["From Max"].default_value = 0.085
    mask.inputs["To Min"].default_value = 1.0
    mask.inputs["To Max"].default_value = 0.0
    L.new(m2.outputs[0], mask.inputs["Value"])
    rough = N.new("ShaderNodeMapRange")
    rough.inputs["To Min"].default_value = b.inputs["Roughness"].default_value
    rough.inputs["To Max"].default_value = 1.0
    L.new(mask.outputs["Result"], rough.inputs["Value"])
    L.new(rough.outputs["Result"], b.inputs["Roughness"])
    key = "Specular IOR Level" if "Specular IOR Level" in b.inputs else "Specular"
    spec = N.new("ShaderNodeMapRange")
    spec.inputs["To Min"].default_value = b.inputs[key].default_value
    spec.inputs["To Max"].default_value = 0.0
    L.new(mask.outputs["Result"], spec.inputs["Value"])
    L.new(spec.outputs["Result"], b.inputs[key])

# ------------------------------------------------------------------------------------------------ lights

SHOT_LIGHTS = ("work", "rim", "rim2", "bounce", "kick", "face", "hair", "van")
GAINS = {"gal": 0.0, "camfill": 0.6, "maze": 1.0, "inside": 1.0, "wash": 1.0, "amb": 1.0, "room": 0.0, "roomb": 0.0}


def build_lights(kit, ctx):
    # the maze's own glow: a broad soft lilac light off the facade and its bulbs, and one from inside the arch
    kit.light("maze", "AREA", (ARCH_X + 1.0, MAZE_Y - 0.6, PLAT_Z + 2.4), 1500.0, GLOW, size=8.0)
    kit.LIGHTS["maze"]["light"].shape = "RECTANGLE"
    kit.LIGHTS["maze"]["light"].size_y = 4.0
    kit.LIGHTS["maze"]["obj"].rotation_euler = (math.radians(-90), 0, 0)
    kit.light("inside", "POINT", (ARCH_X, MAZE_Y + 1.8, PLAT_Z + 2.6), 120.0, BULB, size=0.6)
    # the bulbs' own glow on the facade round them (they're emitters that light nothing themselves)
    kit.light("wash", "AREA", (ARCH_X, MAZE_Y - 0.9, PLAT_Z + 2.4), 260.0, BULB, size=5.0)
    kit.LIGHTS["wash"]["light"].shape = "RECTANGLE"
    kit.LIGHTS["wash"]["light"].size_y = 4.5
    kit.LIGHTS["wash"]["obj"].rotation_euler = (math.radians(90), 0, 0)
    # the worklight (its lens sits on its stand; a shot may cheat the beam's aim and strength)
    x, y = WORK
    kit.light("work", "SPOT", (x, y - 0.1, BOARD_Z + 0.72), 0.0, "#e4eaff", size=0.1, spot=70, blend=0.5)
    # a shot's own rims and the bounce off the wet boards
    kit.light("rim", "SPOT", (0, 0, 3), 0.0, GLOW, size=0.3, spot=30, blend=0.5)
    kit.light("rim2", "SPOT", (0, 0, 3), 0.0, GLOW, size=0.3, spot=30, blend=0.5)
    kit.light("kick", "SPOT", (0, 0, 3), 0.0, "#d8e0ff", size=0.2, spot=25, blend=0.5)
    kit.light("bounce", "AREA", (0, 0, 0.1), 0.0, "#d6dcf6", size=1.0)
    # the worklight's beam bounced up off the wet boards onto a face: a low soft light that a story's "light_only"
    # keeps on the heads alone, so the coat below them never outshines the face. It casts no shadow: a head turned
    # over a side-on shoulder would otherwise lose half its face to the shoulder's shadow, and nothing else sees it
    kit.light("face", "AREA", (0, 0, 0.1), 0.0, "#dfe4ff", size=0.6, shadow=False)
    kit.light("hair", "AREA", (0, 0, 0.1), 0.0, "#dfe4ff", size=0.4, shadow=False)   # the same bounce, on hair only
    for nm, L in kit.LIGHTS.items():
        L["obj"].visible_camera = False
        L["obj"].visible_glossy = nm in ("work",)


def shot_look(kit, story, tl, t, ctx):
    from blocky import kit as K

    over = {nm: 0.0 for nm in SHOT_LIGHTS}
    look = story.get("looks", {}).get(_shot(tl, t)["id"], {})
    wl = "work" in look   # the worklight's stand only shows in the shots that use it
    for o in [ctx["work_root"]] + list(ctx["work_root"].children_recursive):
        o.hide_render = not wl
    fade = cue_at(tl, "fade", t)
    fg = 1.0
    if fade and not fade.get("reset"):
        fg = 1.0 - kit_ss((t - fade["t"]) / float(fade.get("dur", 3.0)))
    for nm, dflt in GAINS.items():
        over[nm] = float(look.get(nm, dflt)) * (fg if nm in ("maze", "inside", "wash") else 1.0)
    for nm in SHOT_LIGHTS:
        if nm not in look:
            continue
        pos, aim, watts = look[nm][:3]
        ob = K.LIGHTS[nm]["obj"]
        if nm != "work":
            ob.location = pos
        ob.rotation_euler = (V(aim) - ob.location).to_track_quat("-Z", "Y").to_euler()
        K.LIGHTS[nm]["base"] = watts
        L = K.LIGHTS[nm]["light"]
        if len(look[nm]) > 3:
            if L.type == "SPOT":
                L.spot_size = math.radians(look[nm][3])
            elif L.type == "AREA":
                L.size = look[nm][3]
        if len(look[nm]) > 4:
            L.color = K.col(look[nm][4])[:3]
        over[nm] = 1.0
    # the lamp's head turns to where the beam is aimed
    d = K.LIGHTS["work"]["obj"].rotation_euler.to_matrix() @ V((0, 0, -1))
    ctx["work_head"].rotation_euler = (-math.atan2(d.z, math.hypot(d.x, d.y)), 0, math.atan2(d.x, -d.y))
    bpy.context.scene.view_settings.exposure = float(look.get("exposure", story.get("look", {}).get("exposure", 0.0)))
    from blocky import bl_story

    sh = _shot(tl, t)
    spec = next(x for x in story["shots"] if x["id"] == sh["id"])
    cl = bl_story.cam_at(spec, sh, t, None, tl)[0]
    K.LIGHTS["camfill"]["obj"].location = (cl[0], cl[1], cl[2] + 0.25)
    g = float(look.get("bulbs", 1.0)) * fg
    e = K.MATS["bulb"].node_tree.nodes.get("Emission")
    if e is not None:
        e.inputs["Strength"].default_value = 7.0 * g
    return over



# ------------------------------------------------------------------------------------------------ the strangers


def build_extras(kit, story, ctx):
    d = Path(bpy.app.tempdir or tempfile.gettempdir()) / "extras-faces"
    d.mkdir(parents=True, exist_ok=True)
    lil = rim_mat(kit, "rim lilac", LILAC, 1.8)
    gry = rim_mat(kit, "rim grey", GREYRIM, 0.25)
    ctx["x"], ctx["base"], ctx["rims"] = {}, {}, {}
    for nm, spec in story.get("extras", {}).items():
        spec = _copy.deepcopy(spec)
        stretch = spec.pop("head_stretch", 1.0)
        ch = rig.Character(nm, spec, d)
        if stretch != 1.0:
            ch.head.scale = (1.0, 1.0, stretch)
        if spec.get("face", {}).get("eyes") in ("mirror", "hollow"):
            matte_eyes(kit, ch)
        old = nm.startswith("o") or nm == "dark"
        ctx["rims"][nm] = add_rim(kit, ch.root, gry if old else lil, 0.07 if nm != "dark" else 0.08)
        ctx["x"][nm] = ch
        ctx["base"][nm] = tuple(ch.root.scale)
        ch.pose(0, 0, 0, 0, hidden=True)
        show_rim(ctx["rims"][nm], False)
    # Tasha's reflection: the old copy model, her own spec mirrored left to right, normal eyes and glint, lilac rim
    tasha = story.get("cast", {}).get("tasha")
    if tasha:
        ch = rig.Character("tr", _copy.deepcopy(tasha), d)
        ch.root.scale = (-ch.root.scale[0], ch.root.scale[1], ch.root.scale[2])
        ctx["rims"]["tr"] = add_rim(kit, ch.root, lil, 0.07)
        ctx["x"]["tr"] = ch
        ctx["base"]["tr"] = tuple(ch.root.scale)
        ch.pose(0, 0, 0, 0, hidden=True)
        show_rim(ctx["rims"]["tr"], False)


def rad(a):
    return math.radians(a)


def set_bow(name, deg):
    torso = bpy.data.objects.get(f"{name}.torso")
    if torso is None:
        return
    b = rad(deg)
    torso.rotation_euler = (b, 0, 0)
    for sx in (-1, 1):
        arm = bpy.data.objects.get(f"{name}.arm{sx}")
        if arm is not None:
            e = arm.rotation_euler
            arm.rotation_euler = (e[0] - b, e[1], e[2])


def tilt_deg(tl, t):
    """The pane's inside, tipped about the pane's own axis: eased between the "tilt" cues' angles."""
    prev, out = 0.0, 0.0
    for c in tl.get("cues", []):
        if c["name"] != "tilt":
            continue
        u = kit_ss((t - c["t"]) / max(0.05, float(c.get("dur", 0.6))))
        out = prev + (float(c["deg"]) - prev) * u
        if t >= c["t"]:
            prev = float(c["deg"]) if u >= 1.0 else out
        else:
            out = prev
            break
    return out


def place(ctx, tl, name, root, e, t, ch=None, rims=None, base=None):
    """Put one character where a stage entry says (None hides it). A cast member (me) was already posed from its
    acting; only its attachment and rim are applied."""
    shells = rims if rims is not None else ctx["rims"].get(name, [])
    if e is None:
        if ch is not None:
            ch.pose(0, 0, 0, 0, hidden=True)
        show_rim(shells, False)
        return
    x, y, z = (list(e.get("pos", [0, 0, 0])) + [0, 0, 0])[:3] if "pos" in e else (None, None, None)
    yaw = rad(e.get("yaw", 0.0))
    roll = 0.0
    att = e.get("att")
    if att and ctx.get("carry"):
        cx, cy, cz, cyaw = ctx["carry"]
        side, ahead, up = att.get("side", 0.0), att.get("ahead", -0.1), att.get("up", 0.0)
        x = cx + ahead * math.sin(cyaw) + side * math.cos(cyaw)
        y = cy - ahead * math.cos(cyaw) + side * math.sin(cyaw)
        z = cz + up
        yaw = cyaw + rad(att.get("yaw", 0.0))
        if att.get("tilt"):
            roll = rad(ctx["tilt"])
    if ch is not None:
        arms = e.get("arms", [0, 0])
        r_arm = arms[1]
        if e.get("wave"):
            ph = (sum(map(ord, name)) % 7) * 0.9
            r_arm = 150 + 28 * math.sin(2 * math.pi * 1.5 * t + ph)
        hd = e.get("head", [0, 0])
        side_ = e.get("side", [0, 0])
        ch.pose(x, y, z, yaw, rad(e.get("legs", 0)), (rad(arms[0]), rad(r_arm)), (rad(side_[0]), rad(side_[1])),
                rad(hd[0]), rad(hd[1]), 0.0, 0.0, e.get("expr", "neutral"), e.get("mouth", 0.0), (0, 0), 0.0, False)
        k = float(e.get("scale", 1.0))
        b = ctx["base"][name]
        ch.root.scale = (b[0] * k, b[1] * k, b[2] * k)
        set_bow(name, e.get("bow", 0.0))
    elif x is not None:
        root.location = (x, y, z)
    if roll and x is not None:
        R = Matrix.Rotation(yaw, 3, "Z") @ Matrix.Rotation(roll, 3, "Y")
        # tip about the pane's axis: rotate the whole body, then yaw is already in R
        R = Matrix.Rotation(ctx["carry"][3], 3, "Z") @ Matrix.Rotation(roll, 3, "Y") @ Matrix.Rotation(yaw - ctx["carry"][3], 3, "Z")
        root.rotation_euler = R.to_euler()
    elif ch is None and att:
        root.rotation_euler = (0, 0, yaw)
    hidden = root.hide_render
    show_rim(shells, bool(e.get("rim", True)) and not hidden)


def pose_stage(story, tl, t, ctx):
    ents = {e["who"]: e for e in cue_at(tl, "stage", t).get("put", [])}
    for nm, ch in ctx["x"].items():
        place(ctx, tl, nm, ch.root, ents.get(nm), t, ch=ch)
    # me: posed from the acting already; the stage may pin me inside the carried pane and tip me, and my rim is on
    me = bpy.data.objects.get("me")
    if me is not None:
        if "me_rims" not in ctx:
            ctx["me_rims"] = add_rim(ctx["kit"], me, ctx["M_rim"], 0.07)
        e = ents.get("me") or {}
        if e.get("att"):
            place(ctx, tl, "me", me, e, t, ch=None, rims=ctx["me_rims"])
        else:
            show_rim(ctx["me_rims"], bool(e.get("rim", True)) and not me.hide_render)


# ------------------------------------------------------------------------------------------------ rain and breath


def build_rain(kit, ctx, M):
    m = kit.emit("#c4ccff", 0.7, name="rain streak")
    ctx["rain"] = []
    rng = np.random.default_rng(15)
    for i in range(170):
        ob = kit.box(f"rain{i}", (0.008, 0.008, 0.4), (0, 0, -50), m)
        ob.visible_shadow = False
        ob.rotation_euler = (0, 0.09, 0)
        ctx["rain"].append((ob, rng.random(3)))


def pose_rain(story, tl, t, ctx):
    c = cue_at(tl, "rain", t)
    on = bool(c.get("on"))
    x0, x1, y0, y1 = c.get("box", [0, 1, 0, 1])
    top = float(c.get("top", 4.0))
    for ob, (u, v, w) in ctx["rain"]:
        ob.hide_render = not on
        if on:
            ob.location = (x0 + u * (x1 - x0), y0 + v * (y1 - y0), top - ((w * top + t * 9.5) % top))


def build_breath(kit, ctx):
    m = kit._new("breath")
    N, L = m.node_tree.nodes, m.node_tree.links
    N.remove(N["Principled BSDF"])
    tc = N.new("ShaderNodeTexCoord")
    sep = N.new("ShaderNodeSeparateXYZ")
    L.new(tc.outputs["Generated"], sep.inputs[0])
    com = N.new("ShaderNodeCombineXYZ")
    L.new(sep.outputs[0], com.inputs[0])
    L.new(sep.outputs[1], com.inputs[1])
    ds = N.new("ShaderNodeVectorMath")
    ds.operation = "DISTANCE"
    L.new(com.outputs[0], ds.inputs[0])
    ds.inputs[1].default_value = (0.5, 0.5, 0.0)
    mr = N.new("ShaderNodeMapRange")
    mr.inputs["From Min"].default_value = 0.5
    mr.inputs["From Max"].default_value = 0.12
    mr.inputs["To Min"].default_value = 0.0
    mr.inputs["To Max"].default_value = 1.0
    L.new(ds.outputs["Value"], mr.inputs["Value"])
    val = N.new("ShaderNodeValue")
    val.outputs[0].default_value = 0.0
    mul = N.new("ShaderNodeMath")
    mul.operation = "MULTIPLY"
    L.new(mr.outputs["Result"], mul.inputs[0])
    L.new(val.outputs[0], mul.inputs[1])
    tr = N.new("ShaderNodeBsdfTransparent")
    em = N.new("ShaderNodeEmission")
    em.inputs["Color"].default_value = (0.78, 0.8, 0.9, 1)
    em.inputs["Strength"].default_value = 0.6
    mix = N.new("ShaderNodeMixShader")
    L.new(mul.outputs[0], mix.inputs[0])
    L.new(tr.outputs[0], mix.inputs[1])
    L.new(em.outputs[0], mix.inputs[2])
    out = next(n for n in N if n.type == "OUTPUT_MATERIAL")
    L.new(mix.outputs[0], out.inputs["Surface"])
    ob = kit.plane("breath", (0.62, 0.5), (0, 0, -50), m, rot=(math.radians(90), 0, 0))
    ob.visible_shadow = False
    ctx["breath"] = (ob, val)


def pose_breath(story, tl, t, ctx):
    c = cue_at(tl, "fog", t)
    ob, val = ctx["breath"]
    a = 0.0
    if c:
        u = kit_ss((t - c["t"]) / (0.7 if c.get("on") else 0.9))
        a = float(c.get("peak", 0.6)) * (u if c.get("on") else 1.0 - u)
    ob.hide_render = a < 0.01
    val.outputs[0].default_value = a
    if c:
        px, py, pz = c.get("pos", [IX, PANE_Y1 - 0.04, 1.5])
        ob.location = (px, py, pz)


# ------------------------------------------------------------------------------------------------ build / animate


def wet_coat(kit, story):
    """Tasha's satin rain mac: a satin sheen, not a glossy slicker."""
    tasha = story.get("cast", {}).get("tasha")
    if not tasha:
        return
    m = rig.cloth(tasha, "shirt")
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Roughness"].default_value = 0.42
    b.inputs["Coat Weight"].default_value = 0.18
    b.inputs["Coat Roughness"].default_value = 0.2
    if "Sheen Weight" in b.inputs:
        b.inputs["Sheen Weight"].default_value = 0.25


def set_wet(story, wet):
    tasha = story.get("cast", {}).get("tasha")
    if not tasha:
        return
    b = rig.cloth(tasha, "shirt").node_tree.nodes["Principled BSDF"]
    base = kit_col(tasha["shirt"])
    k = 0.55 if wet else 1.0
    b.inputs["Base Color"].default_value = (base[0] * k, base[1] * k, base[2] * k, 1.0)
    b.inputs["Roughness"].default_value = 0.25 if wet else 0.42


def kit_box(*a, **k):
    from blocky import kit as K

    return K.box(*a, **k)


def kit_col(h):
    from blocky import kit as K

    return K.col(h)


def link_lights(kit, story, ctx):
    """Once, on the first frame (the cast exists by then): story "light_only": {light: [object names]} makes that
    light reach only those objects (Blender's light linking)."""
    if ctx.get("linked"):
        return
    ctx["linked"] = True
    for nm, names in story.get("light_only", {}).items():
        col = bpy.data.collections.new(f"{nm} only")
        for on in names:
            obs = ([o for o in bpy.data.objects if o.type == "MESH" and o.name.startswith(on[:-1])] if on.endswith("*")
                   else [bpy.data.objects.get(on)])
            for ob in obs:
                if ob is not None and ob.name not in col.objects:
                    col.objects.link(ob)
        for co in col.collection_objects:
            co.light_linking.link_state = "INCLUDE"
        kit.LIGHTS[nm]["obj"].light_linking.receiver_collection = col


def set_props(story, tl, t, ctx):
    """Cue "props": {truckpanes: bool, carry: bool, world: [x, y, z, yaw deg], off: [side, ahead], yaw: deg, wet: bool}."""
    pr = cue_at(tl, "props", t)
    ctx["ceiling"].hide_render = True   # the roof is off the whole film
    half = pr.get("halfpanes", False)
    for ob, wx, j in ctx["ip"]:
        gone = half and (j % 2 == 1 or (abs(wx) < 3 and j in (4, 8)))
        for o in [ob] + list(ob.children_recursive):
            o.hide_render = gone
    for o in [ctx["stage"]] + list(ctx["stage"].children_recursive):
        o.hide_render = bool(pr.get("nostage", False))
    tasha_t = bpy.data.objects.get("tasha.torso")
    if tasha_t is not None:
        if "fries" not in ctx:
            ctx["fries"] = []
            tray = ctx["M_tray"]
            for sx in (-1, 1):
                a = kit_box(f"fries.tray{sx}", (0.9, 0.9, 0.12), (sx * 1.35, -1.9, 1.25), tray, tasha_t)
                b = kit_box(f"fries.stick{sx}", (0.7, 0.7, 0.34), (sx * 1.35, -1.9, 1.48), ctx["M_fry"], tasha_t)
                ctx["fries"] += [a, b]
        for o in ctx["fries"]:
            o.hide_render = not pr.get("fries", False)
    set_wet(story, pr.get("wet", False))
    for p in ctx["truckpanes"]:
        for o in [p] + list(p.children_recursive):
            o.hide_render = not pr.get("truckpanes", False)
    ctx["carry"] = None
    pn = ctx["carried"]
    on = pr.get("carry", False)
    for o in [pn] + list(pn.children_recursive):
        o.hide_render = not on
    ctx["tilt"] = tilt_deg(tl, t)
    if on:
        if "world" in pr:
            wx_, wy_, wz_, wyaw = pr["world"]
            pn.location = (wx_, wy_, wz_)
            pn.rotation_euler = (0, 0, rad(wyaw))
            ctx["carry"] = (wx_, wy_, wz_, rad(wyaw))
        elif "guy" in story.get("cast", {}):
            cast = list(story["cast"])
            g = acting.state(tl, "guy", t, cast.index("guy"))
            side, ahead = pr.get("off", [0.0, 0.9])
            c, sn = math.cos(g["yaw"]), math.sin(g["yaw"])
            wx_, wy_ = g["x"] + ahead * sn + side * c, g["y"] - ahead * c + side * sn
            pn.location = (wx_, wy_, g["z"])
            pn.rotation_euler = (0, 0, g["yaw"] + rad(pr.get("yaw", 40)))
            ctx["carry"] = (wx_, wy_, g["z"], g["yaw"] + rad(pr.get("yaw", 40)))
        ctx["carried_floor"].rotation_euler = (0, rad(ctx["tilt"]) if pr.get("tipfloor", True) else 0.0, 0)


def build(kit, story, tl):
    ctx = {"story": story, "kit": kit}
    M = materials(kit)
    ctx["M"] = M
    ctx["M_rim"] = rim_mat(kit, "rim lilac", LILAC, 1.8)
    ctx["M_tray"] = pbr(kit, "tray", "#b99a6a", 0.7)
    ctx["M_fry"] = pbr(kit, "fries", "#e3b13c", 0.6)
    build_field(kit, ctx, M)
    build_worklight(kit, ctx, M)
    build_maze(kit, ctx, M)
    build_gallery(kit, ctx, M)
    build_truck(kit, ctx, M)
    build_far(kit, ctx, M)
    build_inside(kit, ctx, M)
    bpy.context.scene.cycles.transparent_max_bounces = 32   # panes in rows, and the rim shells' clear fronts
    build_extras(kit, story, ctx)
    build_rain(kit, ctx, M)
    build_breath(kit, ctx)
    wet_coat(kit, story)
    build_lights(kit, ctx)
    return ctx


def animate(kit, story, tl, t, ctx):
    link_lights(kit, story, ctx)
    set_props(story, tl, t, ctx)
    pose_stage(story, tl, t, ctx)
    pose_rain(story, tl, t, ctx)
    pose_breath(story, tl, t, ctx)
    for who in story.get("cast", {}):
        apply_bow(tl, t, who)
    shot = _shot(tl, t)
    cam = kit.OBJ["cam"]
    d = story.get("dof", {}).get(shot["id"])
    cam.data.dof.use_dof = bool(d)
    if d:
        cam.data.dof.focus_distance = float(d[0])
        cam.data.dof.aperture_fstop = float(d[1])
    return shot_look(kit, story, tl, t, ctx)


def apply_bow(tl, t, who):
    """Acting key "bow": degrees the torso bends forward at the hips; the arms keep hanging."""
    keys = tl["acting"].get(who)
    if not keys:
        return
    set_bow(who, acting._held(keys, "bow", t, 0.0))
