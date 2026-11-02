"""Lamp Room (ep28): an old whitewashed lighthouse let as a cottage, on a grassy cliff top in a February storm. Built
from kit.py's parts; nothing here is shared with another story's set. No text anywhere: no signs, numbers or lettering.

Coordinates: the tower's axis is x = y = 0 and the slate floor is z = 0. Azimuth 0 is +x and runs counter-clockwise
(90 is +y). The sea is to the north (+y). A character faces -y at yaw 0.

THE STAIR. A spiral of 12 treads a turn, 7 turns, each turn RISE = 2.2 m high, counter-clockwise going up. Tread i
sits at azimuth 30*i degrees, top surface z = i * RISE / 12. So every full turn the stair is back at azimuth 0, and
the landings the script names (turn n) are all at azimuth 0, z = 2.2 n: the wall features behind me at the rail are
on the wall at azimuth 0 (turn 7 the lamp-room door and its brass bolt plate, turn 6 a small round window, turn 5
a coil of rope on a hook, turn 4 Ines's blue door with a warm wall lamp beside it). The well is open (radius
WELL = 1.2) with an iron rail on its edge. The storm door is at the bottom at azimuth 90 (it opens onto the sea).
The lamp room (round, glass all round, the dead lens in the middle, the camp bed) sits on top at z = LF. The
kitchen and the vestibule beside it are a separate little room at KITCHEN, far from the tower.

THE UPWARD (the creature). One model, built once in build() and posed by animate(): an ordinary-sized blocky
person in a worn oilskin-yellow long coat and rust trousers and boots, wrong in one way. Its head is a plain tan
cylinder whose front is smooth and blank, and its face (two big round white eyes, a round mouth that opens onto
darkness) is on the flat crown, staring straight up. It is only ever seen from above. It is never seen moving.

Cues read here (all optional; the last one at or before t holds; "dur" ramps the change):
- mode: {"set": night|dawn|day|gold|memory|kitchen|kday, "dur": s}  the light of the scene (slow ramps only)
- up: {"pos": [x, y, z], "face": degrees (the way the top of its face's picture points), "mouth": 0..3, "hidden": bool}
- torch: {"on": 0..1, "from": [x, y, z], "aim": [x, y, z], "dur": s}  the torch cone
- phone: {"on": 0..1, "at": [x, y, z], "dur": s}  the phone's glow (a small light, cold white-green)
- clear: {"az": degrees, "z0": m, "z1": m}  hides the treads near azimuth az between z0 and z1 (a view down the
  well); {"az": null} shows them all
- sand: 0..3 sand on my socks.  coat: {"where": "off|worn|feet", "pos": [..]}.  blanket: "none|arm|wrap".
- bolt: {"open": 0..1, "dur": s}.  door: {"open": degrees, "glow": 0..1}  Ines's blue door.
- sun: gain on the dawn light (a mode already does it; this overrides only the sun spot's elevation)
"""

from __future__ import annotations

import math
from pathlib import Path

import bpy
from mathutils import Matrix, Vector as V

from blocky import faces, rig

S = rig.S
RISE = 2.2
PER = 12
STEP = RISE / PER
TURNS = 7
WELL = 1.2          # the open well's radius, and the rail's
STAIR_OUT = 2.4     # the treads' outer radius
WALL_R0, WALL_R1 = 2.75, 2.45   # the tower wall's radius at the bottom and at the lamp room floor
LF = TURNS * RISE + 2.4         # the lamp room floor (above the stair's top landing and its ceiling)
LAMP_H = 3.0
KITCHEN = (40.0, 0.0)


def wall_r(z):
    return WALL_R0 + (WALL_R1 - WALL_R0) * max(0.0, min(1.0, z / LF))


def pol(r, az, z):
    a = math.radians(az)
    return (r * math.cos(a), r * math.sin(a), z)


def ss(x):
    x = min(1.0, max(0.0, x))
    return x * x * (3 - 2 * x)


# ------------------------------------------------------------------------------------------------ materials


def pbr(kit, name, hexc, rough=0.6, metal=0.0, spec=0.4, noise=None, emit=None):
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
    if noise:
        tc = N.new("ShaderNodeTexCoord")
        nz = N.new("ShaderNodeTexNoise")
        nz.inputs["Scale"].default_value = noise[0]
        nz.inputs["Detail"].default_value = 4.0
        L.new(tc.outputs["Object"], nz.inputs["Vector"])
        ramp = N.new("ShaderNodeValToRGB")
        c = kit.col(hexc)
        ramp.color_ramp.elements[0].position = 0.3
        ramp.color_ramp.elements[0].color = (c[0] * noise[1], c[1] * noise[1], c[2] * noise[1], 1)
        ramp.color_ramp.elements[1].position = 0.7
        ramp.color_ramp.elements[1].color = c
        L.new(nz.outputs["Fac"], ramp.inputs["Fac"])
        L.new(ramp.outputs["Color"], b.inputs["Base Color"])
    m.diffuse_color = kit.col(hexc)
    kit._fogged(m, b.outputs[0])
    return m


def unfog(m):
    """Route the BSDF straight to the output (the far beach and sea shouldn't vanish into the distance fog)."""
    nt = m.node_tree
    out = next(n for n in nt.nodes if n.type == "OUTPUT_MATERIAL")
    nt.links.new(nt.nodes["Principled BSDF"].outputs[0], out.inputs["Surface"])


def materials(kit):
    M = {}
    M["white"] = pbr(kit, "whitewash", "#e6e1d6", 0.85, noise=(2.5, 0.8))
    M["stone"] = pbr(kit, "stair stone", "#8a949c", 0.8, noise=(5.0, 0.62))
    M["slate"] = pbr(kit, "slate", "#56626e", 0.7, noise=(3.0, 0.75))
    M["iron"] = pbr(kit, "iron", "#2c3036", 0.5, metal=0.6)
    M["brass"] = pbr(kit, "brass", "#b08d57", 0.35, metal=1.0)
    M["oak"] = kit.planks("#6b4a2e", "#4a3220", 1.5, "Z", name="oak door")
    M["storm"] = kit.planks("#3d3226", "#2a2119", 1.2, "Z", name="storm door")
    M["boards"] = kit.planks("#d8d1c0", "#bdb5a2", 1.0, "X", name="white boards", rough=0.8)
    M["blue"] = pbr(kit, "sea blue door", "#2c6a9a", 0.5)
    M["sand"] = pbr(kit, "sand", "#8f7a50", 0.95, noise=(9.0, 0.7))
    M["scratch"] = pbr(kit, "oilskin scratch", "#f0bd30", 0.35)
    M["grass"] = pbr(kit, "grass", "#3a4a2e", 0.95, noise=(1.2, 0.6))
    M["rock"] = pbr(kit, "cliff rock", "#4a4540", 0.95, noise=(0.5, 0.6))
    M["beach"] = pbr(kit, "beach", "#c2b48c", 0.95)
    M["sea"] = pbr(kit, "sea", "#3c5a70", 0.35)
    unfog(M["beach"])
    unfog(M["sea"])
    M["dark"] = pbr(kit, "dark room", "#07090c", 0.9)
    M["rope"] = pbr(kit, "rope", "#b59a6a", 0.9, noise=(30.0, 0.6))
    M["wool"] = pbr(kit, "cot blanket", "#5c6b5a", 0.9, noise=(15.0, 0.7))
    M["cotf"] = pbr(kit, "cot frame", "#3a3f46", 0.5, metal=0.5)
    M["lens"] = pbr(kit, "lens glass", "#a9bfbd", 0.15, spec=0.7)
    M["camel"] = pbr(kit, "camel coat", "#b5865a", 0.8, noise=(20.0, 0.8))
    M["wood"] = kit.planks("#7a5a3a", "#5a4028", 1.2, "X", name="kitchen wood")
    M["plate"] = pbr(kit, "plate", "#d9d6cf", 0.4)
    M["toast"] = pbr(kit, "toast", "#b98a4e", 0.8)
    M["mug"] = pbr(kit, "mug", "#c9674a", 0.4)
    M["bag"] = pbr(kit, "bag", "#4e5a3c", 0.8)
    M["bag2"] = pbr(kit, "bag two", "#6a3a32", 0.8)
    M["roof"] = pbr(kit, "lamp roof", "#26303a", 0.6)
    M["chair"] = pbr(kit, "chair", "#8a6a48", 0.7)
    M["sock"] = pbr(kit, "cream sock", "#f4ecd8", 0.95)
    # the Upward
    M["oil"] = pbr(kit, "oilskin", "#d9a92a", 0.5, spec=0.5, noise=(14.0, 0.82))
    M["rust"] = pbr(kit, "rust trousers", "#7a3f22", 0.7)
    M["tan"] = pbr(kit, "tan head", "#a9825c", 0.6)
    # windows: one emissive material for every pane; animate() sets its colour and strength
    m = kit._new("pane")
    nt = m.node_tree
    nt.nodes.remove(nt.nodes["Principled BSDF"])
    e = nt.nodes.new("ShaderNodeEmission")
    e.inputs["Color"].default_value = kit.col("#223044")
    e.inputs["Strength"].default_value = 0.3
    kit._fogged(m, e.outputs[0])
    M["pane"] = m
    M["pane_node"] = e
    # Ines's room, seen through her door: one warm emissive card
    m2 = kit._new("room glow")
    nt2 = m2.node_tree
    nt2.nodes.remove(nt2.nodes["Principled BSDF"])
    e2 = nt2.nodes.new("ShaderNodeEmission")
    e2.inputs["Color"].default_value = kit.col("#ffb56a")
    e2.inputs["Strength"].default_value = 0.0
    kit._fogged(m2, e2.outputs[0])
    M["roomglow"] = m2
    M["roomglow_node"] = e2
    M["warmpane"] = kit.emit("#ffb060", 1.6, name="warm pane")
    M["shade"] = kit.emit("#ffc88a", 1.4, name="lampshade")
    M["sunsea"] = kit.emit("#aab4b8", 0.9, name="grey sea window")
    return M


# ------------------------------------------------------------------------------------------------ helpers


def wedge(kit, name, r0, r1, a0, a1, z0, z1, mat, parent=None):
    """A stair tread: radii r0..r1, azimuths a0..a1 (degrees), z0..z1."""
    pts = []
    for z in (z0, z1):
        for a, r in ((a0, r0), (a0, r1), (a1, r1), (a1, r0)):
            pts.append(pol(r, a, z))
    return kit.mesh_obj(name, pts, kit.BOX_FACES, mat, parent)


def beam(kit, name, a, b, w, mat, parent=None):
    a, b = V(a), V(b)
    d = b - a
    ob = kit.box(name, (w, w, d.length), tuple((a + b) / 2), mat, parent)
    ob.rotation_euler = d.to_track_quat("Z", "Y").to_euler()
    return ob


def ring_wall(kit, name, r0, r1, z0, z1, mat, n=48, parent=None):
    """An open tube wall, radius r0 at z0 and r1 at z1, drawn from both sides."""
    verts, faces_ = [], []
    for i in range(n):
        a = 2 * math.pi * i / n
        verts.append((r0 * math.cos(a), r0 * math.sin(a), z0))
        verts.append((r1 * math.cos(a), r1 * math.sin(a), z1))
    for i in range(n):
        j = (i + 1) % n
        faces_.append((2 * i, 2 * j, 2 * j + 1, 2 * i + 1))
    ob = kit.mesh_obj(name, verts, faces_, mat, parent, smooth=True)
    return ob


def disc(kit, name, r, z, mat, n=48, parent=None, r_in=0.0):
    verts, faces_ = [], []
    for i in range(n):
        a = 2 * math.pi * i / n
        verts.append((r * math.cos(a), r * math.sin(a), z))
        if r_in:
            verts.append((r_in * math.cos(a), r_in * math.sin(a), z))
    if r_in:
        for i in range(n):
            j = (i + 1) % n
            faces_.append((2 * i, 2 * j, 2 * j + 1, 2 * i + 1))
    else:
        faces_.append(tuple(range(n)))
    return kit.mesh_obj(name, verts, faces_, mat, parent)


def torus(kit, name, R, r, mat, parent, loc, rot=(0, 0, 0), n=28, m=8):
    verts, faces_ = [], []
    for i in range(n):
        a = 2 * math.pi * i / n
        for j in range(m):
            b = 2 * math.pi * j / m
            verts.append(((R + r * math.cos(b)) * math.cos(a), (R + r * math.cos(b)) * math.sin(a), r * math.sin(b)))
    for i in range(n):
        for j in range(m):
            a0, a1 = i * m + j, ((i + 1) % n) * m + j
            faces_.append((a0, a1, a1 + (1 if j < m - 1 else 1 - m), a0 + (1 if j < m - 1 else 1 - m)))
    return kit.mesh_obj(name, verts, faces_, mat, parent, loc, rot, smooth=True)


def feature(kit, name, az, z):
    """An empty on the tower wall at azimuth az, height z; its +x points out of the wall, +y along it, +z up."""
    r = wall_r(z) - 0.02
    return kit.empty(name, pol(r, az, z), None, (0, 0, math.radians(az)))


def window(kit, M, name, az, z, w=0.5, h=0.9, round_=False, pane="pane"):
    f = feature(kit, name, az, z)
    if round_:
        pane = kit.cyl(f"{name}.pane", 0.28, 0.02, (0.0, 0, 0), M[pane], f, rot=(0, math.pi / 2, 0), n=24)
        torus(kit, f"{name}.ring", 0.3, 0.035, M["brass"], f, (-0.02, 0, 0), rot=(0, math.pi / 2, 0))
        return f
    kit.box(f"{name}.pane", (0.02, w, h), (0.0, 0, 0), M[pane], f)
    t = 0.07
    kit.box(f"{name}.top", (0.16, w + 2 * t, t), (-0.05, 0, h / 2 + t / 2), M["stone"], f)
    kit.box(f"{name}.sill", (0.2, w + 2 * t, t), (-0.07, 0, -h / 2 - t / 2), M["stone"], f)
    for s in (-1, 1):
        kit.box(f"{name}.jamb{s}", (0.16, t, h), (-0.05, s * (w / 2 + t / 2), 0), M["stone"], f)
    kit.box(f"{name}.bar", (0.04, 0.025, h), (-0.01, 0, 0), M["iron"], f)
    kit.box(f"{name}.bar2", (0.04, w, 0.025), (-0.01, 0, 0.05), M["iron"], f)
    return f


# ------------------------------------------------------------------------------------------------ the tower


def build_tower(kit, ctx, M):
    # the wall: one tapered shell seen from both sides, a floor, the plinth and the top of the stair shaft
    ring_wall(kit, "wall", WALL_R0, WALL_R1, 0.0, LF, M["white"])
    kit.cyl("slate floor", WALL_R0, 0.2, (0, 0, -0.1), M["slate"], None, n=48)
    disc(kit, "stair ceiling", WALL_R1, LF - 0.01, M["white"])
    ring_wall(kit, "plinth", WALL_R0 + 0.35, WALL_R0 + 0.15, 0.0, 1.1, M["stone"])
    disc(kit, "plinth cap", WALL_R0 + 0.35, 1.1, M["stone"], r_in=WALL_R0 + 0.1)
    # a dark band round the middle so the tower isn't one white tube
    ring_wall(kit, "band", wall_r(7.0) + 0.04, wall_r(9.0) + 0.04, 7.0, 9.0, pbr(kit, "band", "#3a4652", 0.8))
    # treads, rail and balusters
    ctx["treads"] = []
    ctx["rails"] = []
    top = TURNS * PER
    for i in range(top + 4):
        zt = min(i, top) * STEP
        az = 30.0 * i
        if i > top:
            az = 30.0 * top + 30.0 * (i - top)   # the flat landing continues past the last step
        ob = wedge(kit, f"tread{i}", WELL, wall_r(zt) + 0.03, az - 15.2, az + 15.2, zt - 0.34, zt, M["stone"])
        ctx["treads"].append((ob, az % 360.0, zt))
    pts = []
    for i in range(top + 4):
        zt = min(i, top) * STEP
        az = 30.0 * i
        p = pol(WELL + 0.02, az, zt)
        pts.append((p[0], p[1], zt))
        ctx["rails"].append((beam(kit, f"bal{i}", (p[0], p[1], zt), (p[0], p[1], zt + 0.92), 0.035, M["iron"]), (30.0 * i) % 360.0, zt))
    for i in range(len(pts) - 1):
        a, b = pts[i], pts[i + 1]
        ctx["rails"].append((beam(kit, f"rail{i}", (a[0], a[1], a[2] + 0.94), (b[0], b[1], b[2] + 0.94), 0.05, M["iron"]), (30.0 * i + 15) % 360.0, a[2]))
    # windows: two a turn, with a light just inside each (animate() switches them)
    ctx["wins"] = []
    for k in range(TURNS):
        for az, idx in ((150.0, 5), (330.0, 11)):
            z = (PER * k + idx) * STEP + 1.55
            window(kit, M, f"win{k}_{int(az)}", az, z)
            ctx["wins"].append((az, z))
    window(kit, M, "ines window", 270.0, 4 * RISE + 1.5, w=0.6, h=1.0, pane="warmpane")
    # wall features at azimuth 0
    build_door(kit, ctx, M)
    window(kit, M, "round window", 0.0, 6 * RISE + 2.05, round_=True)
    build_rope(kit, ctx, M)
    build_ines_door(kit, ctx, M)
    build_foot(kit, ctx, M)
    build_lamp_room(kit, ctx, M)


def build_door(kit, ctx, M):
    """The lamp-room door at the top landing (turn 7), azimuth 0, with its brass bolt plate and the two scratches."""
    z0 = TURNS * RISE
    f = feature(kit, "lamp door", 0.0, z0)
    kit.box("lamp door.frame.top", (0.18, 1.2, 0.12), (-0.05, 0, 2.12), M["stone"], f)
    for s in (-1, 1):
        kit.box(f"lamp door.frame{s}", (0.18, 0.12, 2.1), (-0.05, s * 0.58, 1.05), M["stone"], f)
    kit.box("lamp door.leaf", (0.07, 1.04, 2.04), (-0.06, 0, 1.02), M["oak"], f, bevel=0.01)
    # the plate on the latch side (+y), at about 1.05 m
    pl = kit.empty("bolt plate", (-0.105, 0.34, 1.05), f)
    kit.box("bolt plate.plate", (0.012, 0.2, 0.36), (0, 0, 0), M["brass"], pl, bevel=0.003)
    for s in (-1, 1):   # two short upright strokes scratched in oilskin yellow
        kit.box(f"bolt plate.stroke{s}", (0.004, 0.018, 0.13), (-0.008, s * 0.045, -0.03), M["scratch"], pl)
    for s in (-1, 1):
        kit.cyl(f"bolt plate.guide{s}", 0.014, 0.05, (-0.014, 0, 0.12 + s * 0.06), M["brass"], pl, rot=(0, math.pi / 2, 0), n=10)
    # the bolt: a bar that slides along y (open = drawn back toward the hinge side)
    bolt = kit.empty("bolt", (-0.02, 0, 0), pl)
    kit.box("bolt.bar", (0.02, 0.5, 0.032), (0, 0, 0.14), M["brass"], bolt, bevel=0.006)
    kit.cyl("bolt.knob", 0.02, 0.04, (-0.025, 0.2, 0.14), M["brass"], bolt, rot=(0, math.pi / 2, 0), n=10)
    ctx["bolt"] = bolt
    ctx["bolt_home"] = (0.0, 0.0, 0.0)
    kit.box("lamp door.step", (0.5, 1.4, 0.3), (-0.2, 0, -0.15), M["stone"], f)


def build_rope(kit, ctx, M):
    z0 = 5 * RISE + 2.0
    f = feature(kit, "rope hook", 0.0, z0)
    kit.box("hook.plate", (0.03, 0.08, 0.12), (-0.015, 0, 0.05), M["iron"], f)
    kit.cyl("hook.arm", 0.02, 0.2, (-0.12, 0, 0.0), M["iron"], f, rot=(0, math.pi / 2, 0), n=8)
    for k in range(5):
        torus(kit, f"rope{k}", 0.2, 0.034, M["rope"], f, (-0.17, 0.0, -0.13 + k * 0.011), rot=(0, math.pi / 2 + 0.03 * k, 0))
    # a line hanging from the coil
    kit.cyl("rope.tail", 0.03, 0.5, (-0.17, 0.12, -0.4), M["rope"], f, n=8)


def build_ines_door(kit, ctx, M):
    """Ines's sea-blue door, halfway up (turn 4), at azimuth -14 so it sits at the frame's left edge from the rail,
    with the warm wall lamp beside it. The door swings on its +y hinge; open = degrees."""
    z0 = 4 * RISE
    az = 14.0
    f = feature(kit, "ines door", az, z0)
    kit.box("ines door.frame.top", (0.2, 1.2, 0.12), (-0.05, 0, 2.12), M["stone"], f)
    for s in (-1, 1):
        kit.box(f"ines door.frame{s}", (0.2, 0.12, 2.1), (-0.05, s * 0.58, 1.05), M["stone"], f)
    # the room beyond: a card in the wall that glows warm (a soft light in the gap)
    kit.box("ines door.room", (0.02, 1.0, 2.04), (0.1, 0, 1.02), M["roomglow"], f)
    hinge = kit.empty("ines door.hinge", (-0.06, -0.5, 0), f)
    kit.box("ines door.leaf", (0.06, 1.0, 2.04), (0, 0.5, 1.02), M["blue"], hinge, bevel=0.01)
    kit.box("ines door.knob", (0.05, 0.05, 0.05), (-0.04, 0.9, 1.0), M["brass"], hinge, bevel=0.01)
    ctx["ines_hinge"] = hinge
    # the wall lamp at azimuth -14 + 20 (beside the door), warm
    lf = feature(kit, "wall lamp", az - 20.0, z0 + 1.7)
    kit.box("wall lamp.arm", (0.14, 0.04, 0.04), (-0.07, 0, 0), M["brass"], lf)
    kit.box("wall lamp.shade", (0.12, 0.14, 0.18), (-0.16, 0, 0.02), M["shade"], lf, bevel=0.03)
    ctx["lamp_pos"] = pol(wall_r(z0) - 0.28, az - 20.0, z0 + 1.7)


def build_foot(kit, ctx, M):
    """The stair foot: slate floor (the tower's), the plank storm door at azimuth 90, the drift of sand under it."""
    f = feature(kit, "storm door", 90.0, 0.0)
    kit.box("storm.frame.top", (0.22, 1.5, 0.16), (-0.05, 0, 2.24), M["stone"], f)
    for s in (-1, 1):
        kit.box(f"storm.frame{s}", (0.22, 0.16, 2.2), (-0.05, s * 0.78, 1.1), M["stone"], f)
    kit.box("storm.leaf", (0.09, 1.4, 2.18), (-0.06, 0, 1.09), M["storm"], f, bevel=0.01)
    for k in range(3):   # iron straps
        kit.box(f"storm.strap{k}", (0.02, 1.36, 0.08), (-0.115, 0, 0.35 + 0.8 * k), M["iron"], f)
    # sand: a low pale drift under the door, thickest at the bottom steps
    for k in range(7):
        r = 0.55 + 0.1 * (k % 3)
        sx = (k - 3) * 0.2
        ob = kit.sphere(f"sand{k}", r, (-0.5 - 0.2 * (k % 2), sx, 0.0), M["sand"], f, seg=10)
        ob.scale = (1.2, 0.8, 0.14)
    # a skim of sand over the first steps, fading up
    for k in range(10):
        kit.box(f"sand step{k}", (0.5, 0.35, 0.012), (-0.9 - 0.15 * (k % 3), (k - 4.5) * 0.17, 0.014), M["sand"], f)
    # a window at the foot for the sun
    window(kit, M, "foot win", 270.0, 1.55)


def build_lamp_room(kit, ctx, M):
    """Round, glass all round (mullions, no panes), the dead lens in a brass frame in the middle, the camp bed."""
    R = WALL_R1
    disc(kit, "lamp floor", R + 0.6, LF, M["boards"])
    ring_wall(kit, "lamp parapet", R, R, LF, LF + 0.9, M["white"])
    ring_wall(kit, "lamp parapet out", R + 0.1, R + 0.1, LF, LF + 0.9, M["white"])
    disc(kit, "parapet cap", R + 0.12, LF + 0.9, M["white"], r_in=R - 0.02)
    # the gallery outside, with an iron rail
    disc(kit, "gallery", R + 0.9, LF - 0.05, M["stone"], r_in=R)
    n = 28
    for i in range(n):
        a = 360.0 * i / n
        p = pol(R + 0.85, a, LF)
        beam(kit, f"gal bal{i}", (p[0], p[1], LF), (p[0], p[1], LF + 0.95), 0.03, M["iron"])
    ring_wall(kit, "gal rail", R + 0.85, R + 0.85, LF + 0.93, LF + 0.97, M["iron"])
    # mullions and the head ring
    for i in range(14):
        a = 360.0 * i / 14
        p = pol(R - 0.02, a, LF + 0.9)
        beam(kit, f"mullion{i}", p, (p[0], p[1], LF + 0.9 + LAMP_H), 0.07, M["brass"])
    ring_wall(kit, "lamp head", R + 0.05, R + 0.05, LF + 0.9 + LAMP_H - 0.1, LF + 0.9 + LAMP_H + 0.1, M["brass"])
    # roof
    kit.cyl("roof", R + 0.5, 0.9, (0, 0, LF + 0.9 + LAMP_H + 0.45), M["roof"], None, n=32, r2=0.12)
    kit.sphere("roof ball", 0.14, (0, 0, LF + 0.9 + LAMP_H + 1.0), M["brass"])
    disc(kit, "lamp ceiling", R, LF + 0.9 + LAMP_H, M["roof"])
    # the lens: a brass base and frame, stacked glass rings, dead and dark
    cz = LF
    kit.cyl("lens base", 0.62, 0.9, (0, 0, cz + 0.45), M["brass"], None, n=24)
    kit.cyl("lens base top", 0.7, 0.08, (0, 0, cz + 0.94), M["brass"], None, n=24)
    for k in range(6):
        kit.cyl(f"lens ring{k}", 0.5 - 0.02 * abs(k - 2.5), 0.2, (0, 0, cz + 1.12 + 0.24 * k), M["lens"], None, n=24)
        kit.cyl(f"lens band{k}", 0.56, 0.035, (0, 0, cz + 1.0 + 0.24 * k), M["brass"], None, n=24)
    kit.cyl("lens cap", 0.36, 0.1, (0, 0, cz + 2.62), M["brass"], None, n=24, r2=0.2)
    for i in range(4):
        a = 90.0 * i + 45
        p = pol(0.55, a, cz + 1.0)
        beam(kit, f"lens post{i}", p, (p[0], p[1], cz + 2.58), 0.04, M["brass"])
    # the camp bed beside the lens (low, dark frame, a grey-green wool blanket and a pillow)
    cx, cy = -1.25, 0.2
    bed = kit.empty("camp bed", (cx, cy, LF), None, (0, 0, math.radians(8)))
    for sx in (-1, 1):
        for sy in (-1, 1):
            kit.box(f"cot leg{sx}{sy}", (0.05, 0.05, 0.38), (sx * 0.38, sy * 0.92, 0.19), M["cotf"], bed)
    kit.box("cot frame", (0.84, 2.0, 0.05), (0, 0, 0.4), M["cotf"], bed)
    kit.box("cot mattress", (0.8, 1.96, 0.1), (0, 0, 0.47), pbr(kit, "mattress", "#8d95a0", 0.9), bed, bevel=0.03)
    kit.box("cot blanket", (0.84, 1.15, 0.4), (0, -0.35, 0.72), M["wool"], bed, bevel=0.06)
    kit.box("cot pillow", (0.5, 0.3, 0.1), (0, 0.78, 0.57), pbr(kit, "pillow", "#d8d4cc", 0.9), bed, bevel=0.04)
    ctx["bed"] = bed
    # a bag and boots by the bed
    kit.box("duffel", (0.7, 0.35, 0.3), (-1.9, 0.9, LF + 0.15), M["bag"], None, rot=(0, 0, 0.4), bevel=0.08)


def build_ground(kit, ctx, M):
    # the cliff top (grass), the cliff to the north, the beach far below and the sea beyond
    kit.plane("grass", (160, 90), (0, -21, -0.02), M["grass"])
    kit.box("cliff", (160, 0.5, 30), (0, 24.2, -15), M["rock"])
    kit.plane("beach", (400, 46), (0, 47.5, -30.2), M["beach"])
    kit.plane("sea", (800, 500), (0, 320, -30.4), M["sea"])
    # a gravel path from the foot door
    kit.plane("path", (2.2, 12), (0, 8, 0.0), pbr(kit, "path", "#6b665c", 0.95), rot=(0, 0, 0))
    # two bags for the arrival (S04)
    kit.box("bag A", (0.7, 0.3, 0.35), (-1.3, 4.6, 0.18), M["bag"], None, rot=(0, 0, 0.5), bevel=0.07)
    kit.box("bag B", (0.5, 0.3, 0.5), (1.4, 4.3, 0.25), M["bag2"], None, rot=(0, 0, -0.3), bevel=0.07)


def build_kitchen(kit, ctx, M):
    kx, ky = KITCHEN
    W, D, H = 4.6, 4.2, 2.6
    P = lambda x, y, z: (kx + x, ky + y, z)
    kit.plane("k floor", (W, D), P(0, 0, 0), M["wood"])
    kit.plane("k ceiling", (W, D), P(0, 0, H), M["white"], rot=(math.pi, 0, 0))
    wall = M["white"]
    kit.box("k wall S", (W, 0.1, H), P(0, -D / 2, H / 2), wall)
    kit.box("k wall E", (0.1, D, H), P(W / 2, 0, H / 2), wall)
    kit.box("k wall W", (0.1, D, H), P(-W / 2, 0, H / 2), wall)
    # north wall with a big window onto the grey sea
    kit.box("k wall N a", (W, 0.1, 0.9), P(0, D / 2, 0.45), wall)
    kit.box("k wall N b", (W, 0.1, 0.5), P(0, D / 2, H - 0.25), wall)
    for s in (-1, 1):
        kit.box(f"k wall N c{s}", (1.3, 0.1, 1.2), P(s * 1.65, D / 2, 1.5), wall)
    kit.box("k sea", (2.0, 0.04, 1.2), P(0, D / 2 + 0.05, 1.5), M["sunsea"])
    kit.box("k win bar", (0.05, 0.06, 1.2), P(0, D / 2 - 0.03, 1.5), M["white"])
    kit.box("k win sill", (2.2, 0.25, 0.06), P(0, D / 2 - 0.1, 0.9), M["white"])
    # doorway to the vestibule on the south wall? no: the doorway is on the west wall, with a dark gap
    # the table and two chairs (Ines north side, me south side)
    kit.box("k table top", (1.5, 0.9, 0.05), P(0, 0.1, 0.86), M["wood"], bevel=0.01)
    for sx in (-1, 1):
        for sy in (-1, 1):
            kit.box(f"k table leg{sx}{sy}", (0.06, 0.06, 0.84), P(sx * 0.68, 0.1 + sy * 0.38, 0.42), M["wood"])
    for name, y in (("A", 0.95), ("B", -0.75), ("C", -0.55)):
        cx_ = 0.62 if name == "C" else 0.0
        kit.box(f"k chair{name} seat", (0.45, 0.45, 0.05), P(cx_, y, 0.45), M["chair"], bevel=0.01)
        for sx in (-1, 1):
            for sy in (-1, 1):
                kit.box(f"k chair{name} leg{sx}{sy}", (0.04, 0.04, 0.44), P(cx_ + sx * 0.2, y + sy * 0.2, 0.22), M["chair"])
        kit.box(f"k chair{name} back", (0.45, 0.04, 0.45), P(cx_, y + (0.22 if name == "A" else -0.22), 0.7), M["chair"])
    kit.cyl("k plate", 0.13, 0.015, P(-0.35, 0.1, 0.89), M["plate"], None, n=20)
    kit.box("k toast", (0.1, 0.1, 0.02), P(-0.35, 0.1, 0.915), M["toast"], None, rot=(0, 0, 0.3))
    for x in (0.3, 0.55):
        kit.cyl(f"k mug{x}", 0.045, 0.1, P(x, 0.15, 0.92), M["mug"], None, n=14)
    # counter along the west wall
    kit.box("k counter", (0.6, 2.4, 0.9), P(-W / 2 + 0.35, 0.2, 0.45), M["wood"], bevel=0.01)
    kit.box("k counter top", (0.66, 2.46, 0.05), P(-W / 2 + 0.35, 0.2, 0.92), M["white"], bevel=0.01)
    # the vestibule on the east side: a dark doorway, and beyond it a copy of the stair foot
    kit.box("k door N", (0.1, 1.2, 0.5), P(W / 2, -1.3, 2.35), wall)
    ctx["k_origin"] = P(0, 0, 0)
    # beyond the doorway (x > W/2): slate floor, the storm door, sand
    vx = kx + W / 2 + 1.0
    kit.plane("v floor", (2.2, 2.4), (vx, ky - 1.3, 0.0), M["slate"])
    kit.box("v wall far", (0.1, 2.4, H), (vx + 1.1, ky - 1.3, H / 2), wall)
    kit.box("v storm", (0.09, 1.1, 2.1), (vx + 1.04, ky - 1.3, 1.05), M["storm"])
    kit.box("v wall N", (2.2, 0.1, H), (vx, ky - 0.1, H / 2), wall)
    kit.box("v wall S", (2.2, 0.1, H), (vx, ky - 2.5, H / 2), wall)
    kit.box("v ceiling", (2.2, 2.4, 0.05), (vx, ky - 1.3, H), wall)
    sb = kit.sphere("v sand", 0.6, (vx + 0.8, ky - 1.3, 0.0), M["sand"], seg=10)
    sb.scale = (1.0, 1.3, 0.12)
    ctx["k_door"] = ctx.get("k_door")


# ------------------------------------------------------------------------------------------------ the Upward


def crown_image(path, mouth):
    import numpy as np
    from PIL import Image, ImageDraw, ImageFilter

    n = 768
    c = n / 2
    R = n * 0.5
    rng = np.random.default_rng(5)
    yy, xx = np.mgrid[0:n, 0:n]
    rr = np.hypot(xx - c, yy - c) / R
    # weathered skin: low-frequency mottling, darker toward the rim
    low = np.kron(rng.random((12, 12)), np.ones((n // 12, n // 12)))
    low = np.asarray(Image.fromarray((low * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(40))) / 255.0
    fine = rng.random((n, n))
    shade = 0.62 + 0.3 * low + 0.06 * fine
    shade *= np.clip(1.15 - 0.55 * rr ** 2.2, 0.35, 1.0)
    base = np.array([0xa0, 0x7a, 0x56], np.float32)
    im = Image.fromarray(np.clip(base[None, None, :] * shade[..., None], 0, 255).astype(np.uint8))
    # the sockets: deep dark smudges round the eyes
    sock = Image.new("L", (n, n), 0)
    sd = ImageDraw.Draw(sock)
    for sx in (-1, 1):
        ex, ey = c + sx * 0.36 * R, c - 0.2 * R
        sd.ellipse([ex - 0.5 * R, ey - 0.46 * R, ex + 0.5 * R, ey + 0.46 * R], fill=200)
    sock = sock.filter(ImageFilter.GaussianBlur(26))
    dark = Image.new("RGB", (n, n), (28, 18, 12))
    im = Image.composite(dark, im, sock)
    d = ImageDraw.Draw(im)
    ink = (10, 7, 7)
    for sx in (-1, 1):
        ex, ey = c + sx * 0.36 * R, c - 0.14 * R
        er = 0.3 * R
        ry = er * 0.92
        # the eye: a wide cream white, a hair-thin edge (no heavy black ring), a small pupil low in the white
        d.ellipse([ex - er - 0.012 * R, ey - ry - 0.012 * R, ex + er + 0.012 * R, ey + ry + 0.012 * R], fill=(34, 24, 18))
        d.ellipse([ex - er, ey - ry, ex + er, ey + ry], fill=(238, 233, 214))
        pr = 0.06 * R
        d.ellipse([ex - pr, ey + 0.1 * R - pr, ex + pr, ey + 0.1 * R + pr], fill=ink)
        # the upper lid hangs low over the white: opaque skin shadow with a hard edge, the inner end lower (a heavy, hooded look)
        def lid_y(x, drop=0.0):
            return ey - 0.0 * R + drop * R + 0.1 * (-sx) * (x - ex)
        poly = [(ex - 1.3 * er, ey - 1.6 * er), (ex + 1.3 * er, ey - 1.6 * er), (ex + 1.3 * er, lid_y(ex + 1.3 * er)),
                (ex - 1.3 * er, lid_y(ex - 1.3 * er))]
        lid = Image.new("L", (n, n), 0)
        ImageDraw.Draw(lid).polygon(poly, fill=255)
        eye = Image.new("L", (n, n), 0)
        ImageDraw.Draw(eye).ellipse([ex - er - 0.012 * R, ey - ry - 0.012 * R, ex + er + 0.012 * R, ey + ry + 0.012 * R], fill=255)
        m = Image.fromarray(np.minimum(np.asarray(lid), np.asarray(eye)).astype(np.uint8))
        im.paste(Image.new("RGB", (n, n), (44, 31, 24)), (0, 0), m)
        d = ImageDraw.Draw(im)
        d.line([(ex - 1.1 * er, lid_y(ex - 1.1 * er)), (ex + 1.1 * er, lid_y(ex + 1.1 * er))], fill=(14, 9, 7), width=max(2, int(0.01 * R)))
    # the mouth: a dark hole with no outline, ragged and a little soft at the edge, opening wider each sighting
    my = c + 0.5 * R
    sizes = [(0.04, 0.05), (0.07, 0.11), (0.15, 0.24), (0.3, 0.32)]
    mw, mh = sizes[max(0, min(3, int(mouth)))]
    r2 = np.random.default_rng(11)
    pts = []
    for i in range(48):
        a_ = 2 * math.pi * i / 48
        j = 1.0 + 0.04 * r2.standard_normal()
        pts.append((c + math.cos(a_) * mw * R * j, my + math.sin(a_) * mh * R * j))
    hole = Image.new("L", (n, n), 0)
    ImageDraw.Draw(hole).polygon(pts, fill=255)
    hole = hole.filter(ImageFilter.GaussianBlur(4))
    im.paste(Image.new("RGB", (n, n), (3, 2, 3)), (0, 0), hole)
    im.save(path)


def build_upward(kit, ctx, M, workdir):
    root = kit.empty("upward", (0, 0, -50))
    sc = 0.35
    root.scale = (sc, sc, sc)
    b = 0.08
    for sx in (-1, 1):
        kit.box(f"up.leg{sx}", (0.98, 1.0, 1.72), (sx * 0.5, 0, 1.14), M["rust"], root, bevel=b)
        kit.box(f"up.boot{sx}", (1.02, 1.3, 0.32), (sx * 0.5, -0.1, 0.16), M["rust"], root, bevel=b)
    kit.box("up.coat", (2.12, 1.14, 2.1), (0, 0, 3.05), M["oil"], root, bevel=0.12)
    kit.box("up.skirt", (2.3, 1.32, 1.25), (0, 0, 1.55), M["oil"], root, bevel=0.14)
    kit.box("up.collar", (1.5, 1.3, 0.32), (0, 0, 4.12), M["oil"], root, bevel=0.1)
    for sx in (-1, 1):
        kit.box(f"up.sleeve{sx}", (1.0, 1.04, 2.0), (sx * 1.58, 0, 3.0), M["oil"], root, bevel=0.1)
        kit.box(f"up.hand{sx}", (0.9, 0.9, 0.5), (sx * 1.6, 0, 1.75), M["tan"], root, bevel=0.1)
    kit.box("up.neck", (0.6, 0.6, 0.2), (0, 0, 4.25), M["tan"], root)
    HR, HH = 0.8, 1.25
    hz = 4.35 + HH / 2
    head = kit.cyl("up.head", HR, HH, (0, 0, hz), M["tan"], root, n=40)
    # the crown face: a disc just over the flat top, its picture swapped for the mouth's size
    imgs = []
    for k in range(4):
        p = workdir / f"crown-{k}.png"
        crown_image(p, k)
        im = bpy.data.images.load(str(p))
        im.colorspace_settings.name = "sRGB"
        imgs.append(im)
    m = kit._new("crown face")
    nt = m.node_tree
    bsdf = nt.nodes["Principled BSDF"]
    bsdf.inputs["Roughness"].default_value = 0.55
    tex = nt.nodes.new("ShaderNodeTexImage")
    tex.image = imgs[0]
    uvn = nt.nodes.new("ShaderNodeUVMap")
    nt.links.new(uvn.outputs["UV"], tex.inputs["Vector"])
    nt.links.new(tex.outputs["Color"], bsdf.inputs["Base Color"])
    # the whites glow a little so the eyes stay the brightest thing
    nt.links.new(tex.outputs["Color"], bsdf.inputs["Emission Color"])
    bsdf.inputs["Emission Strength"].default_value = 0.12
    kit._fogged(m, bsdf.outputs[0])
    n = 40
    verts = [(0, 0, 0)] + [(HR * 0.985 * math.cos(2 * math.pi * i / n), HR * 0.985 * math.sin(2 * math.pi * i / n), 0) for i in range(n)]
    faces_ = [(0, 1 + i, 1 + (i + 1) % n) for i in range(n)]
    face = kit.mesh_obj("up.face", verts, faces_, m, root, (0, 0, hz + HH / 2 + 0.004))
    uv = face.data.uv_layers.new(name="UVMap")
    for poly in face.data.polygons:
        for li in poly.loop_indices:
            x, y, _ = face.data.vertices[face.data.loops[li].vertex_index].co
            uv.data[li].uv = (0.5 + x / (2 * HR * 0.985) * 0.985 / 1.0, 0.5 + y / (2 * HR * 0.985) * 0.985)
    ctx["up"] = {"root": root, "tex": tex, "imgs": imgs, "mouth": 0}


# ------------------------------------------------------------------------------------------------ lights

# group -> list of light names, filled in build_lights
GROUPS: dict = {}


def add_light(kit, group, name, *a, **kw):
    ob = kit.light(name, *a, **kw)
    GROUPS.setdefault(group, []).append(name)
    return ob


def build_lights(kit, ctx):
    GROUPS.clear()
    # window lights: a point just inside each stair window (blue at night, gold sun at dawn)
    for k, (az, z) in enumerate(ctx["wins"]):
        p = pol(wall_r(z) - 0.35, az, z)
        add_light(kit, "win", f"win{k}", "POINT", p, 30.0, "#5a78b0", size=0.3)
    # the shaft: a dim bluish fill along the well
    for k, z in enumerate((1.5, 5.0, 8.5, 12.0, 15.8)):
        add_light(kit, "shaft", f"shaft{k}", "POINT", (0.2, -0.2, z), 12.0, "#5a78a8", size=0.5)
    # the foot (storm door side), the lamp room, the practicals
    add_light(kit, "foot", "foot", "POINT", (0.0, -0.5, 0.6), 120.0, "#6a88b8", size=0.4)
    add_light(kit, "lroom", "lroom", "POINT", (0.2, -0.3, LF + 2.6), 180.0, "#5a78b0", size=0.4)
    add_light(kit, "lroom", "lroom2", "POINT", (-1.0, 1.6, LF + 1.8), 90.0, "#5a78b0", size=0.4)
    add_light(kit, "lamp", "wall lamp", "POINT", ctx["lamp_pos"], 40.0, "#ffb866", size=0.12)
    # the torch and the phone are moved by cues
    add_light(kit, "torch", "torch", "SPOT", (0, 0, 20), 100.0, "#fff1c4", spot=26, blend=0.85, size=0.05)
    add_light(kit, "torch", "torch spill", "POINT", (0, 0, 20), 10.0, "#ffe9b8", size=0.15)
    add_light(kit, "phone", "phone", "POINT", (0, 0, -40), 14.0, "#cfe9e0", size=0.08)
    # the creature's rim: a faint blue from the side, moved by cues with the creature
    add_light(kit, "rim", "up rim", "SPOT", (0, 0, -40), 900.0, "#6f93d6", spot=40, blend=0.5, size=0.2)
    # exterior
    add_light(kit, "sun", "sun", "SUN", (0, 0, 40), 2.0, "#8fa6d4", rot=(math.radians(55), 0, math.radians(30)))
    # dawn: gold beams from the windows that light the seated pair, and a warm bounce
    for nm, k, w, aim_ in (("gold1", 3, 1.0, (1.9, 175, 7.6)), ("gold2", 4, 0.5, (1.9, 215, 10.5)), ("gold3", 2, 0.4, (1.8, 120, 5.2))):
        z = (PER * k + 5) * STEP + 1.55
        ob = add_light(kit, "gold", nm, "SPOT", pol(2.25, 150, z), 2600.0 * w, "#ffd59a", spot=36, blend=0.6, size=0.3)
        kit.aim(ob, pol(*aim_[:1], aim_[1], aim_[2]))
    ob = add_light(kit, "gold", "foot sun", "SPOT", pol(2.15, 270, 1.9), 900.0, "#ffd59a", spot=44, blend=0.6, size=0.3)
    kit.aim(ob, (0.0, 0.0, 0.0))
    add_light(kit, "bounce", "bounce", "POINT", (0.0, 0.0, 8.0), 900.0, "#ffe4b8", size=0.8)
    add_light(kit, "bounce", "bounce2", "POINT", (0.0, 0.0, 3.0), 600.0, "#ffe4b8", size=0.8)
    # the memory fill: cool blue, enough for faces to read
    add_light(kit, "mem", "mem", "POINT", (0.0, 0.0, 6.0), 800.0, "#7f9fd8", size=0.8)
    # kitchen
    kx, ky = KITCHEN
    add_light(kit, "kit", "kitwin", "AREA", (kx, ky + 1.8, 1.7), 140.0, "#dfe8ee", rot=(math.radians(90), 0, math.pi), size=2.0)
    add_light(kit, "kit", "kitfill", "POINT", (kx, ky - 0.2, 2.3), 60.0, "#e6ecef", size=0.6)
    add_light(kit, "kit", "kitfill2", "POINT", (kx + 0.3, ky - 1.7, 1.6), 25.0, "#f1efe6", size=0.6)
    add_light(kit, "kit", "kitlow", "POINT", (kx + 1.0, ky - 0.1, 0.5), 45.0, "#f1efe6", size=0.4)
    add_light(kit, "kit", "kitvest", "POINT", (kx + 3.3, ky - 1.3, 2.0), 40.0, "#cfd8e0", size=0.5)
    add_light(kit, "mefill", "me fill", "POINT", (0, 0, -40), 30.0, "#9db4e0", size=0.5, shadow=False)
    add_light(kit, "mefill", "ines fill", "POINT", (0, 0, -40), 30.0, "#9db4e0", size=0.5, shadow=False)
    # the camp-bed fill that keeps faces readable in the lamp room at night
    add_light(kit, "cot", "cot", "POINT", (-0.4, 0.6, LF + 1.2), 12.0, "#7a96c8", size=0.3)


# mode -> {group: (gain, colour or None)}, "exp" the scene exposure, "pane": (colour, strength), "world": strength
MODES = {
    "run": {"win": (1.2, "#7c9ad0"), "shaft": (3.0, "#8aa4d0"), "foot": (0.4, None), "lroom": (0.5, None), "lamp": (0.5, None),
            "sun": (0.15, "#5a74b0"), "gold": (0.0, None), "bounce": (0.0, None), "mem": (0.0, None), "kit": (0.0, None),
            "cot": (1.0, None), "exp": 0.5, "pane": ("#1e2c40", 0.5), "world": 0.4},
    "doorlamp": {"win": (0.3, "#4a6aa0"), "shaft": (1.6, "#8aa0c8"), "foot": (0.4, None), "lroom": (0.5, None), "lamp": (12.0, None),
                 "sun": (0.15, "#5a74b0"), "gold": (0.0, None), "bounce": (0.0, None), "mem": (0.0, None), "kit": (0.0, None),
                 "cot": (1.0, None), "exp": 1.2, "pane": ("#1e2c40", 0.5), "world": 0.4},
    "night": {"win": (0.25, "#4a6aa0"), "shaft": (0.5, None), "foot": (0.4, None), "lroom": (0.5, None), "lamp": (0.5, None),
              "sun": (0.15, "#5a74b0"), "gold": (0.0, None), "bounce": (0.0, None), "mem": (0.0, None), "kit": (0.0, None),
              "cot": (1.0, None), "exp": 0.0, "pane": ("#1e2c40", 0.5), "world": 0.4},
    "day": {"win": (0.35, "#c8d4e0"), "shaft": (0.9, "#a8b8cc"), "foot": (1.2, "#cfd8e0"), "lroom": (3.0, "#c8d4e0"),
            "lamp": (0.3, None), "sun": (0.6, "#c8d0d8"), "gold": (0.0, None), "bounce": (0.5, "#c8d0d8"), "mem": (0.0, None),
            "kit": (1.0, None), "cot": (0.0, None), "exp": 0.5, "pane": ("#9aa6b2", 1.2), "world": 1.2},
    "kday": {"win": (0.0, None), "shaft": (0.0, None), "foot": (0.0, None), "lroom": (0.0, None), "lamp": (0.0, None),
             "sun": (0.5, "#c8d0d8"), "gold": (0.0, None), "bounce": (0.0, None), "mem": (0.0, None),
             "kit": (1.2, None), "cot": (0.0, None), "exp": 0.6, "pane": ("#9aa6b2", 1.2), "world": 1.2},
    "dawn": {"win": (0.4, "#ffd59a"), "shaft": (0.6, "#ffd0a0"), "foot": (0.4, "#ffd59a"), "lroom": (0.5, "#ffd59a"),
             "lamp": (0.2, None), "sun": (0.7, "#ffd59a"), "gold": (0.0, None), "bounce": (0.5, None), "mem": (0.0, None),
             "kit": (0.0, None), "cot": (0.0, None), "exp": 0.3, "pane": ("#ffd59a", 2.2), "world": 0.8},
    "gold": {"win": (0.4, "#ffc47a"), "shaft": (0.3, "#ffc888"), "foot": (0.8, "#ffc47a"), "lroom": (1.5, "#ffc47a"),
             "lamp": (0.2, None), "sun": (1.0, "#ffc47a"), "gold": (0.8, "#ffc27a"), "bounce": (0.35, "#ffcc90"), "mem": (0.0, None),
             "kit": (0.0, None), "cot": (0.0, None), "exp": -0.1, "pane": ("#ffc47a", 1.6), "world": 1.0},
    "memory": {"win": (0.3, "#4a6aa0"), "shaft": (0.6, "#6a88c0"), "foot": (0.5, None), "lroom": (0.5, None),
               "lamp": (0.8, None), "sun": (0.15, "#5a74b0"), "gold": (0.0, None), "bounce": (0.0, None),
               "mem": (1.0, None), "kit": (0.0, None), "cot": (1.0, None), "exp": 0.2, "pane": ("#2a3c58", 0.6), "world": 0.4},
}


def _cues(tl, name):
    return [c for c in tl.get("cues", []) if c["name"] == name]


def _last(cs, t):
    out = None
    for c in cs:
        if c["t"] <= t + 1e-9:
            out = c
    return out


def _ramped(cs, t, key, default, dur_key="dur"):
    """The value of a numeric cue field, eased from the previous cue's over this cue's dur."""
    vals = [c for c in cs if key in c and c["t"] <= t + 1e-9]
    if not vals:
        return default
    cur = vals[-1]
    prev = vals[-2][key] if len(vals) > 1 else default
    d = cur.get(dur_key, 0.0)
    u = ss((t - cur["t"]) / d) if d > 0 else 1.0
    return prev + (cur[key] - prev) * u


def _hex(c):
    c = c.lstrip("#")
    return tuple(int(c[i:i + 2], 16) / 255 for i in (0, 2, 4))


def mode_state(tl, t):
    cs = _cues(tl, "mode")
    cur = _last(cs, t)
    if cur is None:
        return MODES["night"], MODES["night"], 1.0
    i = cs.index(cur)
    prev = MODES[cs[i - 1]["set"]] if i > 0 else MODES[cur["set"]]
    d = cur.get("dur", 0.0)
    u = ss((t - cur["t"]) / d) if d > 0 else 1.0
    return prev, MODES[cur["set"]], u


def apply_mode(kit, ctx, tl, t):
    a, b, u = mode_state(tl, t)
    out = {}
    for g, names in GROUPS.items():
        if g in ("torch", "phone", "rim"):
            continue
        ga, ca = a.get(g, (0.0, None))
        gb, cb = b.get(g, (0.0, None))
        gain = ga + (gb - ga) * u
        col = None
        if ca and cb:
            col = tuple(x + (y - x) * u for x, y in zip(_hex(ca), _hex(cb)))
        elif cb:
            col = _hex(cb)
        for n in names:
            out[n] = gain
            if col is not None:
                kit.LIGHTS[n]["light"].color = tuple(kit.srgb(c) for c in col)
    exp = a["exp"] + (b["exp"] - a["exp"]) * u
    bpy.context.scene.view_settings.exposure = exp
    pa, pb = a["pane"], b["pane"]
    ca, cb = _hex(pa[0]), _hex(pb[0])
    col = tuple(x + (y - x) * u for x, y in zip(ca, cb))
    node = ctx["pane_node"]
    node.inputs["Color"].default_value = (*(kit.srgb(c) for c in col), 1.0)
    node.inputs["Strength"].default_value = pa[1] + (pb[1] - pa[1]) * u
    w = a["world"] + (b["world"] - a["world"]) * u
    bg = bpy.context.scene.world.node_tree.nodes["Background"]
    bg.inputs["Strength"].default_value = w
    return out


# ------------------------------------------------------------------------------------------------ build / animate


def build(kit, story, tl):
    ctx = {}
    M = materials(kit)
    ctx["M"] = M
    ctx["pane_node"] = M["pane_node"]
    ctx["roomglow_node"] = M["roomglow_node"]
    build_tower(kit, ctx, M)
    build_ground(kit, ctx, M)
    build_kitchen(kit, ctx, M)
    work = Path(story.get("_work", "/tmp/blocky-lamp"))
    work.mkdir(parents=True, exist_ok=True)
    build_upward(kit, ctx, M, work)
    build_lights(kit, ctx)
    ctx["seen"] = {}
    return ctx


def _dress(kit, story, ctx):
    """Once the cast exists: socks and sand on me, Ines's coat and blanket."""
    M = ctx["M"]
    if ctx.get("dressed") or bpy.data.objects.get("me.leg-1") is None:
        return
    ctx["dressed"] = True
    sand = [[], [], []]
    import random
    rng = random.Random(28)
    for sx in (-1, 1):
        leg = bpy.data.objects[f"me.leg{sx}"]
        kit.box(f"me.sock{sx}", (1.0, 1.04, 0.78), (0, 0, -1.47), M["sock"], leg, bevel=0.1)
        # the foot itself: a sock with a toe that sticks out in front
        kit.box(f"me.sockfoot{sx}", (1.0, 1.56, 0.36), (0, -0.28, -1.83), M["sock"], leg, bevel=0.14)
        kit.box(f"me.sockheel{sx}", (1.0, 0.3, 0.5), (0, 0.4, -1.74), M["sock"], leg, bevel=0.1)

        def clumps(lv, k, xr, yr, z, big=(0.14, 0.3), tall=(0.07, 0.13)):
            for q in range(k):
                w = rng.uniform(*big)
                ob = kit.box(f"me.sand{sx}_{lv}_{q}", (w, w * rng.uniform(0.8, 1.4), rng.uniform(*tall)),
                             (rng.uniform(*xr), rng.uniform(*yr), z), M["sand"], leg, bevel=0.03)
                ob.rotation_euler = (0, 0, rng.uniform(0, 3))
                sand[lv].append(ob)
        # level 1: a little at the toe and the heel; level 2: the foot's top and sides crusted; level 3: up the ankle
        clumps(0, 8, (-0.4, 0.4), (-0.95, -0.55), -1.62)
        clumps(0, 3, (-0.35, 0.35), (0.3, 0.5), -1.6)
        clumps(1, 30, (-0.42, 0.42), (-1.0, 0.45), -1.62, big=(0.16, 0.34), tall=(0.08, 0.15))
        clumps(1, 8, (-0.5, -0.46), (-0.9, 0.4), -1.78)
        clumps(1, 8, (0.46, 0.5), (-0.9, 0.4), -1.78)
        clumps(2, 16, (-0.45, 0.45), (-0.5, 0.45), -1.28, big=(0.15, 0.3), tall=(0.08, 0.14))
        clumps(2, 10, (-0.52, 0.52), (-0.48, 0.48), -1.5, big=(0.15, 0.3), tall=(0.08, 0.14))
    ctx["sand"] = sand
    # Ines: a camel coat (worn), over a flannel shirt
    if bpy.data.objects.get("ines.torso") is not None:
        tor = bpy.data.objects["ines.torso"]
        coat = []
        for sx in (-1, 1):
            coat.append(kit.box(f"ines.coatf{sx}", (0.8, 1.12, 2.1), (sx * 0.62, 0, 1.0), M["camel"], tor, bevel=0.08))
            hinge = bpy.data.objects[f"ines.leg{sx}"]
            coat.append(kit.box(f"ines.coats{sx}", (1.04, 1.16, 1.65), (0, 0, -0.55), M["camel"], hinge, bevel=0.08))
            arm = bpy.data.objects[f"ines.arm{sx}"]
            coat.append(kit.box(f"ines.coata{sx}", (1.06, 1.1, 1.9), (0, 0, -0.7), M["camel"], arm, bevel=0.08))
        coat.append(kit.box("ines.coatb", (1.9, 0.2, 2.1), (0, 0.5, 1.0), M["camel"], tor, bevel=0.08))
        ctx["coat_worn"] = coat
        blk = rig.cloth({"shirt": "#6b3d3a", "pattern": "plaid", "pattern_c": "#c9b79a"}, "shirt")
        arm = kit.box("ines.blanket arm", (1.1, 1.0, 1.5), (0.1, -0.5, -0.8), blk, bpy.data.objects["ines.arm-1"], bevel=0.12)
        arm.rotation_euler = (0, 0, 0)
        bundle = kit.box("ines.blanket bundle", (2.1, 0.95, 1.15), (0, -0.85, 0.55), blk, tor, bevel=0.14)
        wrap = [kit.box("ines.wrap torso", (2.5, 1.5, 2.3), (0, -0.02, 0.9), blk, tor, bevel=0.2),
                kit.box("ines.wrap hood", (1.8, 0.4, 1.1), (0, 0.55, 2.6), blk, tor, bevel=0.2)]
        for sx in (-1, 1):
            wrap.append(kit.box(f"ines.wrap leg{sx}", (1.06, 1.1, 1.8), (0, 0, -0.9), blk, bpy.data.objects[f"ines.leg{sx}"], bevel=0.12))
        ctx["blanket_arm"] = [arm, bundle]
        ctx["blanket_wrap"] = wrap
    # the coat laid over my feet, a prop in the world
    ctx["coat_feet"] = [kit.box("coat feet", (0.9, 0.5, 0.14), (0, 0, -80), M["camel"], None, bevel=0.05)]


def _show(obs, on):
    for ob in obs:
        ob.hide_render = not on
        for c in ob.children_recursive:
            c.hide_render = not on


def animate(kit, story, tl, t, ctx):
    _dress(kit, story, ctx)
    out = apply_mode(kit, ctx, tl, t)
    # sit: R6 sitting for anyone whose key says so (legs straight out in front)
    for who in ("me", "ines"):
        keys = tl["acting"].get(who, [])
        sit = False
        for k in keys:
            if "sit" in k and k["t"] <= t + 1e-9:
                sit = k["sit"]
        for sx in (-1, 1):
            leg = bpy.data.objects.get(f"{who}.leg{sx}")
            if leg is not None and sit:
                leg.rotation_euler = (math.radians(-90), 0, 0)
    from blocky import acting as _a2
    me_h = _a2.state(tl, "me", t)["hidden"]
    in_h = _a2.state(tl, "ines", t)["hidden"]
    for who_, h_ in (("me", me_h), ("ines", in_h)):   # parts made after the first pose (socks, coat) follow the hiding
        if h_ and bpy.data.objects.get(who_) is not None:
            for ob in bpy.data.objects[who_].children_recursive:
                ob.hide_render = True
    # sand on my socks
    lv = _last(_cues(tl, "sand"), t)
    lvl = int(lv["level"]) if lv else 0
    if ctx.get("sand"):
        for i, obs in enumerate(ctx["sand"]):
            _show(obs, lvl > i and not me_h)
    # the coat and the blanket
    cc = _last(_cues(tl, "coat"), t)
    where = cc["where"] if cc else "off"
    if ctx.get("coat_worn"):
        _show(ctx["coat_worn"], where == "worn" and not in_h)
        feet = ctx["coat_feet"][0]
        if where == "feet" and cc.get("pos"):
            feet.location = cc["pos"]
            feet.rotation_euler = (0, 0, math.radians(cc.get("yaw", 0)))
            feet.hide_render = False
        else:
            feet.location = (0, 0, -80)
    bc = _last(_cues(tl, "blanket"), t)
    bl = bc["state"] if bc else "none"
    if ctx.get("blanket_arm"):
        _show(ctx["blanket_arm"], bl == "arm" and not in_h)
        _show(ctx["blanket_wrap"], bl == "wrap" and not in_h)
    # the bolt and Ines's door
    bo = _ramped(_cues(tl, "bolt"), t, "open", 0.0)
    ctx["bolt"].location = (-0.02, -0.34 * bo - 0.0 + 0.0, 0.0) if False else (-0.02, 0.0 - 0.3 * bo, 0.0)
    dc = _cues(tl, "door")
    ang = _ramped(dc, t, "open", 0.0)
    ctx["ines_hinge"].rotation_euler = (0, 0, math.radians(ang))
    glow = _ramped(dc, t, "glow", 0.0)
    ctx["roomglow_node"].inputs["Strength"].default_value = glow
    # the creature
    uc = _last(_cues(tl, "up"), t)
    up = ctx["up"]
    if uc and not uc.get("hidden"):
        up["root"].location = uc["pos"]
        up["root"].rotation_euler = (0, 0, math.radians(uc.get("face", 90) - 90))
        m = int(uc.get("mouth", 0))
        if m != up["mouth"]:
            up["tex"].image = up["imgs"][m]
            up["mouth"] = m
        # its rim: a faint blue from beside and behind, aimed at it
        rim = kit.LIGHTS["up rim"]["obj"]
        p = V(uc["pos"])
        rim.location = (p.x + 1.3, p.y - 0.9, p.z + 3.0)
        kit.aim(rim, (p.x, p.y, p.z + 1.3))
        out["up rim"] = 1.0 * uc.get("rim", 1.0)
    else:
        up["root"].location = (0, 0, -50)
        out["up rim"] = 0.0
    # the treads the view down the well needs gone
    cl = _last(_cues(tl, "clear"), t)
    for ob, az, zt in ctx["treads"]:
        hide = False
        if cl and cl.get("az") is not None:
            d = abs((az - cl["az"] + 180.0) % 360.0 - 180.0)
            hide = d < cl.get("span", 50.0) and cl["z0"] < zt < cl["z1"]
        ob.hide_render = hide
    for ob, az, zt in ctx["rails"]:
        hide = bool(cl and cl.get("rails") and abs((az - cl.get("rail_az", cl["az"]) + 180.0) % 360.0 - 180.0) < cl.get("rail_span", 40.0)
                    and cl["rails"][0] < zt < cl["rails"][1])
        ob.hide_render = hide
    # the faces' fill: a soft light a metre in front of each character, toward the middle of the room
    from blocky import acting as _act
    mode_a, mode_b, u_ = mode_state(tl, t)
    fg = {"night": 1.0, "run": 3.0, "doorlamp": 3.5, "memory": 2.5, "day": 5.0, "gold": 1.6}
    cur = _last(_cues(tl, "mode"), t)
    gain_f = fg.get(cur["set"], 1.0) if cur else 1.0
    for who, ln in (("me", "me fill"), ("ines", "ines fill")):
        st_ = _act.state(tl, who, t)
        if st_["hidden"]:
            out[ln] = 0.0
            continue
        dx, dy = math.sin(st_["yaw"]), -math.cos(st_["yaw"])   # the way they face: the camera is usually there
        kit.LIGHTS[ln]["obj"].location = (st_["x"] + dx * 1.1, st_["y"] + dy * 1.1, st_["z"] + 1.7)
        out[ln] = gain_f
    # the torch and the phone
    tc = _last(_cues(tl, "torch"), t)
    tl_on = _ramped(_cues(tl, "torch"), t, "on", 0.0)
    tor = kit.LIGHTS["torch"]["obj"]
    if tc:
        tor.location = tc["from"]
        aim = tc["aim"]
        if tc.get("aim_to"):
            u = ss((t - tc["t"]) / tc.get("aim_dur", 1.0))
            aim = [x + (y - x) * u for x, y in zip(aim, tc["aim_to"])]
        kit.aim(tor, aim)
        kit.LIGHTS["torch"]["light"].spot_size = math.radians(tc.get("spot", 26))
        kit.LIGHTS["torch"]["light"].spot_blend = tc.get("blend", 0.85)
    out["torch"] = tl_on * (tc.get("gain", 1.0) if tc else 1.0)
    out["torch spill"] = tl_on * (tc.get("spill", 1.0) if tc else 1.0)
    if tc:
        kit.LIGHTS["torch spill"]["obj"].location = tc.get("spill_at", tc["from"])
    pc = _last([c for c in _cues(tl, "phone") if "pos" in c], t)
    pon = _ramped(_cues(tl, "phone"), t, "on", 0.0)
    if pc:
        kit.LIGHTS["phone"]["obj"].location = pc["pos"]
        if pc.get("color"):
            kit.LIGHTS["phone"]["light"].color = tuple(kit.srgb(c) for c in _hex(pc["color"]))
    out["phone"] = pon
    if __import__("os").environ.get("LR_DEBUG"):
        print("DEBUG", round(t, 2), {k: round(v, 2) for k, v in out.items() if k in ("foot", "shaft0", "win0", "me fill")}, tuple(kit.LIGHTS["foot"]["obj"].location), kit.LIGHTS["foot"]["light"].energy)
    return out
