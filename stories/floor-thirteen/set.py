"""Floor Thirteen: the lift of an older apartment tower, and the Attendant (story 4, ep14). Built from kit.py's
parts; nothing here is shared with another story's set.

This first version is the creature test (the /blocky skill's step 3): the lift car (walnut, satin steel doors,
the floor-button panel and the floor indicator), 13's hall beyond the doors, and the Attendant. The 12 landing,
the lobby and the balconies come with the build step (the brief's "World").

Coordinates: the car's floor is z = 0. Inside, the car runs x = -CAR_W/2 .. CAR_W/2 and y = CAR_Y0 .. CAR_Y1 under
a CAR_H ceiling. The doors are in the front wall at y = CAR_Y0, and the hall is beyond them (y < SILL_Y). Facing
the doors from inside is yaw 0 (a character faces -y). The floor-button panel is on the front wall, to the right of
the doors as you face them (x < 0). No text anywhere but the indicator's digits.

THE ATTENDANT (the brief's continuity list; the designer notes' "Creature test" has the numbers):
- R6 blocks at the cast's scale (rig.S metres a unit), but wrong: legs 2.6 units and a torso 2.05 (a person's are
  2.0 and 2.0), shoulders 1.6 wide (a person's 2.0), arms of 3.6 units (2.0) that hang folded below its knees, and
  2.43 m tall with its cap, a hand's width under the car's 2.5 m ceiling.
- A black wool jacket (#14151a), two rows of four plain brass buttons, brass piping on the collar, hem, cuffs and
  shoulder boards; black trousers with a brass side stripe; glossy black shoes; a peaked black cap with a plain brass
  band, a crown that flares 10 cm wider than the head each side and a glossy visor. Brass #c8a050, the panel's frame
  a duller brass #a8843f, the bezels' dark brass #4e3d24. No badge, number, logo or text.
- Off-white gloves (#ddd8cc), always folded in front, right over left. They never unfold.
- The head: a deep black lacquer block 0.58 m square and 0.40 m deep on a short wool neck. Its face is a lift panel
  set 8 cm back in a black socket behind a 4 cm lacquer lip (brow, cheeks, chin): a brass frame, a dark brushed face
  plate and nine round lift buttons in a 3 x 3 grid (GRIDS; set_options "grid" keeps 2 x 2 for a comparison only;
  set_options "head": "round" is the house rounded head with the panel set in it, tried once and not used).
  Each is a dark brass bezel (0.14 m across) round frosted dark glass that glows ice-white with a faint blue
  (#c6dbff, tuned from the brief's #d4e6ff so the blue survives the tone curve), lit as a ring round a dimmer middle,
  like a lit lift button. Each bulb has its own fixed brightness (BULBS). The car's floor panel uses the same model.
- Buttons are numbered left to right, top to bottom, as you look at its face. The centre (4) is its eye: at rest one
  button is lit, the eye burns hotter than the rest ("eye" gain), and the talk darkens them outside-in, so the
  centre goes out last (GRIDS "dark").
- It is never seen moving and never crosses the sill: a shot only places it and sets which buttons are lit.
  POSES holds the poses that have passed the contact probe (the doorway bump: feet on 13's floor, 0.56 m past the
  sill, bowed 40 degrees so its face comes under the car's 2.1 m door head while the head stays on 13's side of it
  and the door head crops its cap; arms hanging folded, the car doors stopped 0.8 m apart in front of its shoulders).

Cues read here (all optional; the first of each also sets the start):
- attendant: {"pose": a name in POSES (its numbers, under any given here), "pos": [x, y], "yaw": deg,
  "lean": deg (the whole body, forward), "bend": deg (forward at the waist), "head": [pitch, roll, yaw] deg
  (pitch + tips the panel down toward what it faces), "fold": 0..1 how far forward the folded arms hang (0 straight
  down, for the stoop), "lit": "all" | [indices] | n (the n left lit once the talk has darkened the rest), "glow":
  gain on every lit button, "eye": extra gain on the centre, "hidden": bool}
- lights: {"state": "on" | "thirteen", "cast_dark": bool} the car's ceiling panel (thirteen: dimmed to 5%, never
  out, with the panel's glow and 13's cold light coming in through the doors); cast_dark keeps the car's own light
  off the cast (light linking), so only the Attendant's cold glow touches us
- doors: {"gap": metres between the car doors' edges (DOOR_W = open), "hall": 0..1 13's doors open}
- panel: {"lit": [indices]} the floor-button panel's lit buttons (0 is the lobby's, at the bottom)
- indicator: {"floor": "12" | "13" | ..., "arrow": "up" | "down" | null}
"""

from __future__ import annotations

import math

import bpy
from mathutils import Matrix, Vector as V

from blocky import faces, rig

U = rig.S                      # metres per rig unit, the cast's scale

# ------------------------------------------------------------------------------------------------ the car
CAR_W = 2.1                    # inside, side to side: 1.9 can't hold two 1.36 m wide R6 riders clear of the rails
CAR_Y0, CAR_Y1 = -0.95, 0.95   # the front wall's inside face (the doors) and the back wall's: 1.9 m deep
CAR_H = 2.5                    # the ceiling
DOOR_W, DOOR_H = 1.1, 2.1      # the opening
WALL_T = 0.08
DOOR_Y = CAR_Y0 - WALL_T - 0.03   # the car doors' track, just outside the front wall
SILL_Y = CAR_Y0 - 0.32         # where 13's floor starts (past the car's sill and the hall's)
BX = 30.0                      # the balconies' x (metres east of the lift)
PANEL_X = -0.75                # the floor-button panel's centre on the front wall, beside the doors
PANEL_Z = 1.12
RAIL_Z = 0.92                  # the handrail
HALL_H = 2.7                   # 13's hall is older and taller than our floors
HALL_DOOR_H = 2.45             # and so is its lift doorway: only the car's 2.1 m door head stops what stands in it

# ------------------------------------------------------------------------------------------- the Attendant
# Per grid: its eye, and the order the talk darkens them (outside-in, the eye last).
GRIDS = {
    (3, 3): {"eye": 4, "dark": [0, 8, 2, 6, 1, 7, 3, 5, 4]},
    (2, 2): {"eye": 0, "dark": [3, 2, 1, 0]},
}
# each bulb's own brightness, fixed for the film (old lift bulbs are never even, and an even grid reads as LEDs)
BULBS = [0.9, 0.72, 1.0, 0.8, 1.0, 0.68, 0.95, 0.84, 0.76]
DEFAULT_GRID = (3, 3)
# poses that have passed the contact probe against the doors, the header, the transom and the sill (cue "pose")
POSES = {
    "bump": {"pos": [0.0, -2.04], "yaw": 180, "lean": 0, "bend": 40, "head": [-2, 0, 0], "fold": 1.6},
    # standing on 13's floor a step from the sill, upright, facing the car (the arrivals; never seen to move)
    "left": {"pos": [0.46, -1.68], "yaw": 180, "lean": 0, "bend": 0, "head": [0, 0, 0], "fold": 1.0},
    "right": {"pos": [-0.46, -1.68], "yaw": 180, "lean": 0, "bend": 0, "head": [0, 0, 0], "fold": 1.0},
    "centre": {"pos": [0.0, -1.68], "yaw": 180, "lean": 0, "bend": 0, "head": [0, 0, 0], "fold": 1.0},
}
LEG_H, LEG_W = 2.6, 0.84       # rig units (a person's legs are 2.0 x 1.0)
TORSO_W, TORSO_H, TORSO_D = 1.6, 2.05, 0.9    # narrow shoulders: the doors close on them
ARM_W, ARM_L = 0.72, 3.6       # a person's arm is 1.0 x 2.0; folded, the gloves hang below its knees
ARM_IN = 19.5                  # how far each arm swings in so the gloves meet and cross (degrees)
GLOVE_L = 0.95                 # a glove longer than it is wide reads as a hand hanging from the cuff, not a cube
GLOVE_W = 0.5
COLLAR_H = 0.25
NECK_H = 0.2                   # a wool neck block between the collar and the head (7 cm)
# the head: a deep black lacquer block, its face a lift panel set back in a socket behind a lacquer lip
HEAD_S = 1.7                   # the head's outside, 0.58 m square
HEAD_D = 1.18                  # 0.40 m deep, a cast head's depth
LIP = 0.12                     # the lacquer lip round the socket (brow, cheeks, chin), 4 cm
RECESS = 0.24                  # how far the panel sits back inside the lip, 8 cm
FRAME = 0.06                   # the brass frame round the panel, inside the lip
PLATE = HEAD_S - 2 * LIP - 2 * FRAME   # the face plate the buttons sit in, 0.46 m
CAP_H = 0.36                   # the cap's height over the head (band and crown)
VISOR_TIP = -4                 # the visor's tip from square to the face (degrees down); the bow adds its own
BUTTON_GAIN = 0.62             # emission strength of a lit button at glow 1

BRASS = "#c8a050"
BRASS_DARK = "#4e3d24"
WOOL = "#14151a"
GLOVE = "#ddd8cc"
GLOW = "#c6dbff"
WALNUT = "#3a2618"


def grid_layout(grid):
    """Button centres (x, z) on the plate and the bezel's and the glass's radius, in rig units. Big buttons, nearly
    touching, as on a crowded old lift panel, so each reads at phone size."""
    rows, cols = grid
    pitch = PLATE / max(rows, cols)
    bezel = min(0.44 * pitch, 0.24)
    face = bezel * 0.72
    pts = [((c - (cols - 1) / 2) * pitch, ((rows - 1) / 2 - r) * pitch) for r in range(rows) for c in range(cols)]
    return pts, bezel, face


# ---------------------------------------------------------------------------------------------- materials


def pbr(kit, name, hexc, rough=0.5, metal=0.0, coat=0.0, spec=0.5, noise=None, brushed=None):
    """A Principled material through the kit's fog. noise = (scale, dark) mottles the colour; brushed = (axis,
    spread) streaks the roughness along one axis."""
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
    tc = None
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
    if brushed:
        tc = tc or N.new("ShaderNodeTexCoord")
        mp = N.new("ShaderNodeMapping")
        mp.inputs["Scale"].default_value = {"X": (2.0, 300.0, 300.0), "Y": (300.0, 2.0, 300.0),
                                            "Z": (300.0, 300.0, 2.0)}[brushed[0]]
        L.new(tc.outputs["Object"], mp.inputs["Vector"])
        nz = N.new("ShaderNodeTexNoise")
        nz.inputs["Scale"].default_value = 1.0
        nz.inputs["Detail"].default_value = 2.0
        L.new(mp.outputs["Vector"], nz.inputs["Vector"])
        rr = N.new("ShaderNodeMapRange")
        rr.inputs["To Min"].default_value = max(0.02, rough - brushed[1])
        rr.inputs["To Max"].default_value = min(1.0, rough + brushed[1])
        L.new(nz.outputs["Fac"], rr.inputs["Value"])
        L.new(rr.outputs["Result"], b.inputs["Roughness"])
    m.diffuse_color = kit.col(hexc)
    kit._fogged(m, b.outputs[0])
    return m


def walnut(kit, name="walnut", hexc=WALNUT, dark="#21150c", rough=0.48):
    """Dark walnut veneer, satin (never glossy): long wavy grain running up the panel."""
    if name in kit.MATS:
        return kit.MATS[name]
    m = kit._new(name)
    N, L = m.node_tree.nodes, m.node_tree.links
    b = N["Principled BSDF"]
    b.inputs["Roughness"].default_value = rough
    for k in ("Specular IOR Level", "Specular"):
        if k in b.inputs:
            b.inputs[k].default_value = 0.35
            break
    tc = N.new("ShaderNodeTexCoord")
    mp = N.new("ShaderNodeMapping")
    mp.inputs["Scale"].default_value = (1.0, 1.0, 0.12)
    L.new(tc.outputs["Object"], mp.inputs["Vector"])
    fac = []
    for axis in ("X", "Y"):   # grain across whichever way the panel faces
        wv = N.new("ShaderNodeTexWave")
        wv.wave_type = "BANDS"
        wv.bands_direction = axis
        wv.inputs["Scale"].default_value = 9.0
        wv.inputs["Distortion"].default_value = 7.0
        wv.inputs["Detail"].default_value = 3.0
        L.new(mp.outputs["Vector"], wv.inputs["Vector"])
        fac.append(wv)
    mx = N.new("ShaderNodeMath")
    mx.operation = "MAXIMUM"
    L.new(fac[0].outputs["Fac"], mx.inputs[0])
    L.new(fac[1].outputs["Fac"], mx.inputs[1])
    ramp = N.new("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].position = 0.25
    ramp.color_ramp.elements[0].color = kit.col(dark)
    ramp.color_ramp.elements[1].position = 0.85
    ramp.color_ramp.elements[1].color = kit.col(hexc)
    L.new(mx.outputs[0], ramp.inputs["Fac"])
    L.new(ramp.outputs["Color"], b.inputs["Base Color"])
    m.diffuse_color = kit.col(hexc)
    kit._fogged(m, b.outputs[0])
    return m


def glow_mat(kit, name, hexc, strength):
    if name in kit.MATS:
        return kit.MATS[name]
    m = kit._new(name)
    nt = m.node_tree
    nt.nodes.remove(nt.nodes["Principled BSDF"])
    e = nt.nodes.new("ShaderNodeEmission")
    e.name = "glow"
    e.inputs["Color"].default_value = kit.col(hexc)
    e.inputs["Strength"].default_value = strength
    kit._fogged(m, e.outputs[0])
    return m


def button_mat(kit, name, radius, glow=GLOW, style="ring"):
    """One button's face: dark glass that glows when lit. Its own material, so each button switches alone.
    `radius` is the face's radius in its mesh's own units (the glow reads object coordinates). style "ring": the
    light is a ring just inside the bezel round a dimmer middle, like a lit lift button (and like an iris round a
    pupil); "solid": brightest in the middle, falling off to the bezel."""
    if name in kit.MATS:
        return kit.MATS[name]
    m = kit._new(name)
    N, L = m.node_tree.nodes, m.node_tree.links
    b = N["Principled BSDF"]
    b.inputs["Base Color"].default_value = kit.col("#0b0e12")
    b.inputs["Roughness"].default_value = 0.32   # frosted: the side lights don't glint in it like a second eye
    for k in ("Specular IOR Level", "Specular"):
        if k in b.inputs:
            b.inputs[k].default_value = 0.6
            break
    b.inputs["Emission Color"].default_value = kit.col(glow)
    tc = N.new("ShaderNodeTexCoord")
    sep = N.new("ShaderNodeSeparateXYZ")
    L.new(tc.outputs["Object"], sep.inputs[0])
    vec = N.new("ShaderNodeCombineXYZ")
    L.new(sep.outputs["X"], vec.inputs["X"])
    L.new(sep.outputs["Y"], vec.inputs["Y"])
    ln = N.new("ShaderNodeVectorMath")
    ln.operation = "LENGTH"
    L.new(vec.outputs[0], ln.inputs[0])
    dv = N.new("ShaderNodeMath")
    dv.operation = "DIVIDE"
    dv.inputs[1].default_value = radius
    L.new(ln.outputs["Value"], dv.inputs[0])
    ramp = N.new("ShaderNodeValToRGB")
    els = ramp.color_ramp.elements
    stops = ([(0.0, 0.55), (0.5, 0.62), (0.7, 1.0), (0.86, 1.0), (1.0, 0.3)] if style == "ring"
             else [(0.0, 1.0), (0.6, 0.6), (1.0, 0.12)])
    els[0].position, els[0].color = stops[0][0], (stops[0][1],) * 3 + (1,)
    els[1].position, els[1].color = stops[-1][0], (stops[-1][1],) * 3 + (1,)
    for pos, v in stops[1:-1]:
        e = els.new(pos)
        e.color = (v,) * 3 + (1,)
    L.new(dv.outputs[0], ramp.inputs["Fac"])
    mul = N.new("ShaderNodeMath")
    mul.name = "strength"
    mul.operation = "MULTIPLY"
    mul.inputs[1].default_value = 0.0
    L.new(ramp.outputs["Color"], mul.inputs[0])
    L.new(mul.outputs[0], b.inputs["Emission Strength"])
    kit._fogged(m, b.outputs[0])
    return m


def set_button(m, strength):
    m.node_tree.nodes["strength"].inputs[1].default_value = strength


def materials(kit):
    return {
        "brass": pbr(kit, "brass", BRASS, 0.3, metal=1.0),
        "brass_dark": pbr(kit, "brass dark", BRASS_DARK, 0.5, metal=1.0),
        "brass_frame": pbr(kit, "brass frame", "#a8843f", 0.48, metal=1.0),
        "wool": pbr(kit, "wool", WOOL, 0.82, spec=0.3, noise=(40.0, 0.8)),
        "lacquer": pbr(kit, "lacquer", "#0c0c0f", 0.22, coat=0.6),
        "shoe": pbr(kit, "shoe", "#0a0a0c", 0.2, coat=0.8),
        "visor": pbr(kit, "visor", "#08080a", 0.12, coat=1.0),
        "door_edge": pbr(kit, "door edge", "#c8ccd2", 0.42, metal=0.5),
        "glove": pbr(kit, "glove", GLOVE, 0.88, spec=0.12),   # cotton: matte, no hot spots
        "faceplate": pbr(kit, "faceplate", "#1c1a17", 0.4, metal=1.0, brushed=("X", 0.12)),
        "walnut": walnut(kit),
        "satin": pbr(kit, "satin steel", "#8e9195", 0.55, metal=0.6, brushed=("Z", 0.08)),
        "satin_dark": pbr(kit, "satin steel dark", "#4a4c50", 0.6, metal=0.9),
        "seam": pbr(kit, "seam", "#0b0907", 0.7),
        "floor": pbr(kit, "car floor", "#141210", 0.75, noise=(22.0, 0.7)),
        "ceiling": pbr(kit, "car ceiling", "#2a2b2d", 0.6, metal=0.5),
        "glass_black": pbr(kit, "black glass", "#050506", 0.08, spec=0.7),
        "carpet": pbr(kit, "13 carpet", "#3b2a1c", 0.95, noise=(5.0, 0.55)),
        "hall_wall": pbr(kit, "13 walls", "#36321f", 0.85, noise=(2.5, 0.7)),
        "hall_door": pbr(kit, "13 doors", "#2a1d14", 0.6),
        "shade": pbr(kit, "sconce shade", "#4a4236", 0.4, spec=0.5),
        "diffuser": glow_mat(kit, "ceiling diffuser", "#eaf1f6", 0.0),
        "segment": glow_mat(kit, "indicator segment", GLOW, 0.0),
    }


# ------------------------------------------------------------------------------------------- the Attendant


def build_attendant(kit, M, name="attendant", cap=True, grid=DEFAULT_GRID, style="ring", head_style="socket"):
    """The one model. The legs hang off a root at its feet and everything above them off a waist at its hips, so a
    shot only places the root, bends the waist, tilts the head and switches buttons. Front is -y, like the cast."""
    grid = tuple(grid)
    R = kit.empty(name, (0, 0, 0))
    R.scale = (U, U, U)
    bev = 0.06
    for sx in (-1, 1):   # trousers with a brass stripe down each outer seam, glossy shoes
        x = sx * LEG_W / 2
        kit.box(f"{name}.leg{sx}", (LEG_W - 0.02, LEG_W, LEG_H - 0.3), (x, 0, 0.3 + (LEG_H - 0.3) / 2), M["wool"], R,
                bevel=bev)
        kit.box(f"{name}.stripe{sx}", (0.03, 0.12, LEG_H - 0.45),
                (x + sx * (LEG_W / 2 - 0.005), 0, 0.3 + (LEG_H - 0.3) / 2), M["brass"], R)
        kit.box(f"{name}.shoe{sx}", (LEG_W, LEG_W + 0.22, 0.3), (x, -0.1, 0.15), M["shoe"], R, bevel=0.08)
    W = kit.empty(f"{name}.waist", (0, 0, LEG_H), R)
    # the jacket: the torso block, a skirt over the hips with a brass hem, two rows of four brass buttons
    kit.box(f"{name}.torso", (TORSO_W, TORSO_D, TORSO_H), (0, 0, TORSO_H / 2), M["wool"], W, bevel=bev)
    skirt = 0.42
    kit.box(f"{name}.skirt", (TORSO_W + 0.04, TORSO_D + 0.04, skirt), (0, 0, -skirt / 2 + 0.05), M["wool"], W,
            bevel=0.04)
    kit.box(f"{name}.hem", (TORSO_W + 0.07, TORSO_D + 0.07, 0.06), (0, 0, -skirt + 0.08), M["brass"], W, bevel=0.02)
    front = -TORSO_D / 2 - 0.02
    for cx in (-0.36, 0.36):
        for k in range(4):
            kit.cyl(f"{name}.btn{cx}{k}", 0.075, 0.06, (cx, front - 0.02, 0.4 + k * 0.45), M["brass"], W,
                    rot=(math.pi / 2, 0, 0), n=16)
    kit.box(f"{name}.collar", (1.0, 0.74, COLLAR_H), (0, 0, TORSO_H + COLLAR_H / 2), M["wool"], W, bevel=0.05)
    kit.box(f"{name}.collar_edge", (1.04, 0.78, 0.05), (0, 0, TORSO_H + COLLAR_H - 0.02), M["brass"], W, bevel=0.015)
    # arms: long black sleeves, brass cuffs, gloves, shoulder boards edged in brass
    arms = {}
    for sx in (-1, 1):
        a = kit.empty(f"{name}.arm{sx}", (sx * (TORSO_W / 2 + ARM_W / 2 + 0.01), 0, TORSO_H - 0.3), W)
        sl = ARM_L - GLOVE_L
        kit.box(f"{name}.sleeve{sx}", (ARM_W, ARM_W, sl), (0, 0, 0.3 - sl / 2), M["wool"], a, bevel=bev)
        kit.box(f"{name}.cuff{sx}", (ARM_W + 0.04, ARM_W + 0.04, 0.1), (0, 0, 0.3 - sl + 0.06), M["brass"], a,
                bevel=0.02)
        kit.box(f"{name}.glove{sx}", (GLOVE_W, GLOVE_W + 0.04, GLOVE_L), (0, 0, 0.3 - sl - GLOVE_L / 2), M["glove"],
                a, bevel=0.1)
        kit.box(f"{name}.board{sx}", (ARM_W + 0.06, ARM_W * 0.7, 0.07), (0, 0, 0.32), M["wool"], a, bevel=0.02)
        kit.box(f"{name}.boardedge{sx}", (0.05, ARM_W * 0.72, 0.08), (sx * (ARM_W / 2 + 0.02), 0, 0.32), M["brass"], a)
        arms[sx] = a
    # the head: a deep lacquer block on a wool neck, pivoting on the top of the collar. Its face is a lift panel set
    # back in a black socket behind a lacquer lip, so the lights sit in darkness and the outline is black on black.
    neck = kit.empty(f"{name}.neck", (0, 0, TORSO_H + COLLAR_H), W)
    kit.box(f"{name}.neckblock", (0.95, 0.8, NECK_H + 0.1), (0, 0, NECK_H / 2), M["wool"], neck, bevel=0.04)
    hc = kit.empty(f"{name}.headc", (0, 0, NECK_H + HEAD_S / 2), neck)
    front = -HEAD_D / 2
    fy = front + RECESS            # the panel's face, in the socket
    inner = HEAD_S - 2 * LIP
    if head_style == "round":
        # the house head everyone else has (rig.head_mesh), scaled up, in black lacquer, its face cut away to a
        # square socket the panel sits in: a person whose face is a lift panel
        k_r = (HEAD_S / 2 + 0.06) / faces.HEAD_R
        rg = kit.empty(f"{name}.roundg", (0, 0, 0), hc)
        rg.scale = (k_r, k_r, HEAD_S / faces.HEAD_H)
        hm = rig.head_mesh(f"{name}.housing", M["lacquer"], rg)
        cut = kit.box(f"{name}.socketcut", (inner / k_r, 2.0, inner * faces.HEAD_H / HEAD_S),
                      (0, (fy - 1.0) / k_r, 0), None, rg)
        cut.hide_render = True
        cut.display_type = "WIRE"
        bo = hm.modifiers.new("socket", "BOOLEAN")
        bo.object = cut
        bo.operation = "DIFFERENCE"
        kit.box(f"{name}.socketback", (inner + 0.02, 0.06, inner + 0.02), (0, fy + 0.04, 0), M["lacquer"], hc)
    else:
        kit.box(f"{name}.housing", (HEAD_S, HEAD_D - RECESS, HEAD_S), (0, RECESS / 2, 0), M["lacquer"], hc,
                bevel=0.06)
        for k, (sx, sz, lx, lz) in enumerate(((HEAD_S, LIP, 0, HEAD_S / 2 - LIP / 2),       # brow
                                              (HEAD_S, LIP, 0, -HEAD_S / 2 + LIP / 2),      # chin
                                              (LIP, inner, -HEAD_S / 2 + LIP / 2, 0),       # cheeks
                                              (LIP, inner, HEAD_S / 2 - LIP / 2, 0))):
            kit.box(f"{name}.lip{k}", (sx, RECESS + 0.04, sz), (lx, front + RECESS / 2 - 0.01, lz), M["lacquer"],
                    hc, bevel=0.04)
    for k, (sx, sz, lx, lz) in enumerate(((inner, FRAME, 0, inner / 2 - FRAME / 2),
                                          (inner, FRAME, 0, -inner / 2 + FRAME / 2),
                                          (FRAME, inner, -inner / 2 + FRAME / 2, 0),
                                          (FRAME, inner, inner / 2 - FRAME / 2, 0))):
        kit.box(f"{name}.frame{k}", (sx, 0.05, sz), (lx, fy - 0.02, lz), M["brass_frame"], hc, bevel=0.015)
    kit.box(f"{name}.plate", (PLATE, 0.03, PLATE), (0, fy - 0.01, 0), M["faceplate"], hc)
    pts, bezel, face = grid_layout(grid)
    buttons = []
    for i, (x, z) in enumerate(pts):
        kit.cyl(f"{name}.bezel{i}", bezel, 0.05, (x, fy - 0.045, z), M["brass_dark"], hc, rot=(math.pi / 2, 0, 0), n=40)
        bm = button_mat(kit, f"{name} button {i}", face, style=style)
        kit.cyl(f"{name}.button{i}", face, 0.05, (x, fy - 0.06, z), bm, hc, rot=(math.pi / 2, 0, 0), n=40)
        buttons.append(bm)
    if cap:   # a peaked cap: a plain brass band at head width, a crown that flares wider, a glossy visor angled down
        top = HEAD_S / 2
        band = 0.12
        kit.box(f"{name}.band", (HEAD_S + 0.04, HEAD_D + 0.04, band), (0, 0, top + band / 2), M["brass"], hc,
                bevel=0.02)
        kit.box(f"{name}.crown", (HEAD_S + 0.58, HEAD_D + 0.5, CAP_H - band),
                (0, 0.06, top + band + (CAP_H - band) / 2), M["wool"], hc, bevel=0.09)
        vis = 0.45   # 15 cm deep, straight out from the brow: in the bow the head's tip puts it about 40 degrees down
        a = math.radians(VISOR_TIP)
        kit.box(f"{name}.peak", (HEAD_S * 0.92, vis, 0.05),
                (0, front - vis / 2 * math.cos(a), top + 0.02 - vis / 2 * math.sin(a)), M["visor"], hc,
                rot=(a, 0, 0), bevel=0.02)
    return {"root": R, "waist": W, "neck": neck, "head": hc, "arms": arms, "buttons": buttons, "name": name,
            "grid": grid, "height": (LEG_H + TORSO_H + COLLAR_H + NECK_H + HEAD_S + (CAP_H if cap else 0)) * U}


def lit_gains(grid, lit, glow=1.0, eye=1.0):
    """Each button's strength from a cue's "lit": "all", a list of indices, or n (the n still lit once the talk
    has darkened the rest, outside-in)."""
    g = GRIDS[tuple(grid)]
    n = grid[0] * grid[1]
    if lit == "all":
        on = set(range(n))
    elif isinstance(lit, (int, float)):
        on = set(g["dark"][n - int(lit):])
    else:
        on = set(lit or [])
    return [glow * BULBS[i % len(BULBS)] * (eye if i == g["eye"] else 1.0) if i in on else 0.0 for i in range(n)]


def pose_attendant(att, pos=(0, 0), yaw=0.0, lean=0.0, bend=0.0, head=(0.0, 0.0, 0.0), gains=None, hidden=False,
                   fold=1.0):
    """Place the one model: its feet, which way it faces, how far the whole body leans and the waist bends, the
    panel's pitch (+ tips it down toward what it faces), roll and yaw, and each button's strength. The arms always
    hang folded: whatever the bend, they hang from the shoulders and the gloves meet low in front, right over left.
    `fold` scales how far forward they hang (0 straight down: in a stoop the shoulders already carry them forward)."""
    R = att["root"]
    R.location = (pos[0], pos[1], 0.0)
    R.rotation_euler = (math.radians(lean), 0, math.radians(yaw))
    att["waist"].rotation_euler = (math.radians(bend), 0, 0)
    for sx, a in att["arms"].items():
        # the hang is set in the body's upright frame and the bow taken back out, so the arms hang under gravity and
        # swing in (not forward) whatever the bend: the gloves meet in front, the right (sx = -1) over the left
        f = math.radians((9.0 if sx < 0 else 6.0) * fold + (2.5 if sx < 0 else 0.0))
        hang = Matrix.Rotation(math.radians(sx * ARM_IN), 3, "Y") @ Matrix.Rotation(-f, 3, "X")
        a.rotation_euler = (Matrix.Rotation(-math.radians(bend + lean), 3, "X") @ hang).to_euler()
    h = list(head) + [0.0] * (3 - len(head))
    att["neck"].rotation_euler = (math.radians(h[0]), math.radians(h[1]), math.radians(h[2]))
    gains = gains or [0.0] * len(att["buttons"])
    for m, g in zip(att["buttons"], gains):
        set_button(m, g * BUTTON_GAIN)
    R.hide_render = hidden
    for ob in R.children_recursive:
        ob.hide_render = hidden or ob.name.endswith(".socketcut")   # the boolean cutter is never drawn


# --------------------------------------------------------------------------------------------- the car


def _wbox(kit, name, lo, hi, mat, parent=None, bevel=0.0):
    """A box from two corners."""
    lo, hi = tuple(min(a, b) for a, b in zip(lo, hi)), tuple(max(a, b) for a, b in zip(lo, hi))
    size = tuple(h - l for l, h in zip(lo, hi))
    c = tuple((l + h) / 2 for l, h in zip(lo, hi))
    return kit.box(name, size, c, mat, parent, bevel=bevel)


def _prism(kit, name, pts, depth, loc, mat, rot=(-math.pi / 2, 0, 0)):
    """A flat shape (points in x, y, counter-clockwise) raised `depth` along its z: the panel's brass glyphs and the
    indicator's arrows. The default rotation stands it up facing +y, into the car."""
    n = len(pts)
    verts = [(x, y, 0.0) for x, y in pts] + [(x, y, depth) for x, y in pts]
    faces = [tuple(range(n - 1, -1, -1)), tuple(range(n, 2 * n))]
    faces += [(i, (i + 1) % n, n + (i + 1) % n, n + i) for i in range(n)]
    return kit.mesh_obj(name, verts, faces, mat, None, loc, rot)


def build_car(kit, ctx, M):
    """The car: walnut panels with dark seams, a brass handrail, a near-black floor, the ceiling with its light
    panel, the front wall with the satin steel doors, the floor-button panel and the floor indicator."""
    x0, x1 = -CAR_W / 2, CAR_W / 2
    _wbox(kit, "floor", (x0 - 0.1, CAR_Y0, -0.1), (x1 + 0.1, CAR_Y1 + 0.1, 0.0), M["floor"])
    _wbox(kit, "ceiling", (x0 - 0.1, CAR_Y0 - WALL_T, CAR_H), (x1 + 0.1, CAR_Y1 + 0.1, CAR_H + 0.1), M["ceiling"])
    _wbox(kit, "diffuser", (-0.35, 0.1, CAR_H - 0.012), (0.35, 0.7, CAR_H - 0.002), M["diffuser"])
    for k, (lo, hi) in enumerate((((-0.39, 0.06, CAR_H - 0.03), (0.39, 0.1, CAR_H)),
                                   ((-0.39, 0.7, CAR_H - 0.03), (0.39, 0.74, CAR_H)),
                                   ((-0.39, 0.06, CAR_H - 0.03), (-0.35, 0.74, CAR_H)),
                                   ((0.35, 0.06, CAR_H - 0.03), (0.39, 0.74, CAR_H)))):
        _wbox(kit, f"diffuser_rim{k}", lo, hi, M["satin"])
    span = CAR_Y1 - CAR_Y0
    for side, xw in ((-1, x0), (1, x1)):
        # three walnut panels a side over a dark backing, so the seams show
        _wbox(kit, f"backing{side}", (xw, CAR_Y0 - WALL_T, 0), (xw + side * WALL_T, CAR_Y1, CAR_H), M["seam"])
        for k in range(3):
            ya = CAR_Y0 + span * k / 3 + 0.008
            yb = CAR_Y0 + span * (k + 1) / 3 - 0.008
            _wbox(kit, f"wall{side}.{k}", (xw - side * 0.016, ya, 0.1), (xw, yb, CAR_H - 0.02), M["walnut"])
        _wbox(kit, f"kick{side}", (xw, CAR_Y0, 0), (xw - side * 0.02, CAR_Y1, 0.1), M["satin_dark"])
        xr = xw - side * 0.07   # the handrail: a brass tube on two stand-offs
        kit.cyl(f"rail{side}", 0.02, span - 0.3, (xr, (CAR_Y0 + CAR_Y1) / 2 + 0.05, RAIL_Z), M["brass"],
                rot=(math.pi / 2, 0, 0), n=14)
        for k, yy in enumerate((CAR_Y0 + 0.35, CAR_Y1 - 0.25)):
            kit.cyl(f"rail{side}.post{k}", 0.012, 0.07, (xw - side * 0.035, yy, RAIL_Z), M["brass"],
                    rot=(0, math.pi / 2, 0), n=10)
    # the back wall: walnut, for bounce, but the camera (just behind it) doesn't see it
    bw = _wbox(kit, "back_wall", (x0, CAR_Y1, 0), (x1, CAR_Y1 + WALL_T, CAR_H), M["walnut"])
    bw.visible_camera = False
    # the front wall: walnut either side of the opening and over it, satin steel jambs and header, a grooved sill
    yf = CAR_Y0
    for side, (xa, xb) in ((-1, (x0, -DOOR_W / 2 - 0.04)), (1, (DOOR_W / 2 + 0.04, x1))):
        _wbox(kit, f"front{side}", (xa, yf - WALL_T, 0), (xb, yf, CAR_H), M["walnut"])
        xj = side * (DOOR_W / 2 + 0.04)
        _wbox(kit, f"jamb{side}", (xj, yf - WALL_T - 0.02, 0), (xj - side * 0.045, yf + 0.006, DOOR_H + 0.045),
              M["satin"])
    _wbox(kit, "transom", (-DOOR_W / 2 - 0.04, yf - WALL_T, DOOR_H), (DOOR_W / 2 + 0.04, yf, CAR_H), M["walnut"])
    _wbox(kit, "header", (-DOOR_W / 2 - 0.045, yf - WALL_T - 0.02, DOOR_H),
          (DOOR_W / 2 + 0.045, yf + 0.006, DOOR_H + 0.045), M["satin"])
    _wbox(kit, "sill", (-DOOR_W / 2 - 0.04, SILL_Y, -0.02), (DOOR_W / 2 + 0.04, yf, 0.004), M["satin"])
    for k in range(7):
        yy = yf - 0.03 - k * 0.04
        _wbox(kit, f"groove{k}", (-DOOR_W / 2 - 0.03, yy - 0.006, 0.0), (DOOR_W / 2 + 0.03, yy, 0.0045), M["seam"])
    # the car's doors (centre-opening, in their track outside the front wall) and 13's, at the hall's edge
    leaf_w = DOOR_W / 2 + 0.03
    leaves = {"car": [], "hall": []}
    for kind, yy in (("car", DOOR_Y), ("hall", SILL_Y + 0.025)):
        for side in (-1, 1):
            dh = DOOR_H if kind == "car" else HALL_DOOR_H
            lf = kit.box(f"door.{kind}{side}", (leaf_w, 0.035, dh), (0, yy, dh / 2), M["satin"], bevel=0.004)
            kit.box(f"door.{kind}{side}.edge", (0.022, 0.042, dh), (-side * leaf_w / 2, 0, 0), M["door_edge"], lf)
            leaves[kind].append((lf, side))
    ctx["leaves"], ctx["leaf_w"] = leaves, leaf_w
    build_panel(kit, ctx, M)
    build_indicator(kit, ctx, M)


def build_panel(kit, ctx, M):
    """The floor-button panel beside the doors: 20 plain round buttons in two columns of ten (the Attendant's own
    model, smaller), the lobby's at the bottom with a raised brass star, then door-open and door-close with raised
    brass arrows. No numbers, letters, bell or braille."""
    yf = CAR_Y0
    pw, ph = 0.2, 0.9
    py = yf + 0.008
    _wbox(kit, "panel_edge", (PANEL_X - pw / 2 - 0.012, yf, PANEL_Z - ph / 2 - 0.012),
          (PANEL_X + pw / 2 + 0.012, py - 0.002, PANEL_Z + ph / 2 + 0.012), M["brass_dark"])
    _wbox(kit, "panel", (PANEL_X - pw / 2, yf, PANEL_Z - ph / 2), (PANEL_X + pw / 2, py, PANEL_Z + ph / 2), M["satin"])
    pr = 0.022           # a glass face's radius in metres; the bezel is 1.39 times it, as on the Attendant
    dz = 0.066
    rows = [(PANEL_X + (c - 0.5) * 0.085, PANEL_Z + ph / 2 - 0.08 - r * dz) for r in range(10) for c in range(2)]
    slots = rows[::-1]   # 0 is the bottom one on the door side: the lobby
    z_low = PANEL_Z + ph / 2 - 0.08 - 10 * dz - 0.02
    slots += [(PANEL_X + 0.0425, z_low), (PANEL_X - 0.0425, z_low)]   # 20 door-open, 21 door-close
    pbtn = []
    for i, (x, z) in enumerate(slots):
        kit.cyl(f"pbezel{i}", pr * 1.39, 0.012, (x, py + 0.004, z), M["brass_dark"], rot=(math.pi / 2, 0, 0), n=28)
        bm = button_mat(kit, f"panel button {i}", pr, style=ctx.get("style", "ring"))
        kit.cyl(f"pbutton{i}", pr, 0.012, (x, py + 0.008, z), bm, rot=(math.pi / 2, 0, 0), n=28)
        pbtn.append(bm)
    gy = py + 0.0145
    x, z = slots[0]      # the lobby's raised star
    star = [((0.016 if k % 2 == 0 else 0.0065) * math.sin(-2 * math.pi * k / 10),
             (0.016 if k % 2 == 0 else 0.0065) * math.cos(2 * math.pi * k / 10)) for k in range(10)][::-1]
    _prism(kit, "glyph.star", star, 0.003, (x, gy, z), M["brass"])
    for i, outward in ((20, True), (21, False)):   # open: <|>  close: >|<
        x, z = slots[i]
        for s in (-1, 1):
            tip, base = (s * 0.017, s * 0.004) if outward else (s * 0.004, s * 0.017)
            tri = [(tip, 0.0), (base, 0.008), (base, -0.008)]
            if (tip - base) * s < 0:
                tri = tri[::-1]
            _prism(kit, f"glyph.{i}.{s}", tri, 0.003, (x, gy, z), M["brass"])
        _wbox(kit, f"glyph.{i}.bar", (x - 0.0012, gy, z - 0.009), (x + 0.0012, gy + 0.003, z + 0.009), M["brass"])
    ctx["panel_buttons"] = pbtn


# segment: (x, z) of its centre in half-widths / half-heights of the digit, and whether it lies across
SEGS = {"a": (0, 1, True), "b": (0.5, 0.5, False), "c": (0.5, -0.5, False), "d": (0, -1, True),
        "e": (-0.5, -0.5, False), "f": (-0.5, 0.5, False), "g": (0, 0, True)}
DIGITS = {"0": "abcdef", "1": "bc", "2": "abged", "3": "abgcd", "4": "fgbc", "5": "afgcd", "6": "afgedc",
          "7": "abc", "8": "abcdefg", "9": "abcfgd"}


def build_indicator(kit, ctx, M):
    """The floor indicator over the doors inside the car: a black glass strip with two segment digits built from
    blocks (no font), and an up and a down triangle, all in the creature's cold colour."""
    z = DOOR_H + 0.2
    y = CAR_Y0 + 0.012
    _wbox(kit, "indicator", (-0.2, CAR_Y0, z - 0.075), (0.2, y, z + 0.075), M["glass_black"])
    _wbox(kit, "indicator_rim", (-0.212, CAR_Y0, z - 0.087), (0.212, y - 0.004, z + 0.087), M["brass_dark"])
    sw, sh, th = 0.028, 0.05, 0.008   # a digit's half-width and half-height, a segment's thickness
    segs = {}
    for d, cx in enumerate((0.042, -0.042)):   # seen from inside the car, +x is on the left
        for k, (sx, sz, across) in SEGS.items():
            size = (2 * sw * 0.86, 0.004, th) if across else (th, 0.004, sh * 0.86)
            segs[(d, k)] = kit.box(f"seg{d}{k}", size, (cx - sx * 2 * sw, y + 0.002, z + sz * sh), M["segment"])
    arrows = {}
    for name, sgn, cx in (("up", 1, 0.15), ("down", -1, -0.15)):
        tri = [(0.0, -sgn * 0.022), (0.02 * sgn, sgn * 0.014), (-0.02 * sgn, sgn * 0.014)]   # the stand-up flips y
        arrows[name] = _prism(kit, f"arrow.{name}", tri, 0.003, (cx, y + 0.001, z), M["segment"])
    ctx["segs"], ctx["arrows"] = segs, arrows


def set_indicator(ctx, floor="12", arrow=None):
    on = {(d, k) for d, ch in enumerate(f"{floor:>2}"[-2:]) for k in DIGITS.get(ch, "")}
    for key, ob in ctx["segs"].items():
        ob.hide_render = key not in on
    for name, ob in ctx["arrows"].items():
        ob.hide_render = name != arrow


def build_hall(kit, ctx, M):
    """13's hall beyond the doors: umber carpet, dark olive-brown walls, unlit brass sconces, shut doors with blank
    brass plates, running far back into the fog. The camera only ever sees it through the gap."""
    y0 = SILL_Y
    hh = HALL_H
    _wbox(kit, "hall_floor", (-1.6, y0 - 12.0, -0.1), (1.6, y0, 0.0), M["carpet"])
    _wbox(kit, "hall_ceiling", (-1.6, y0 - 12.0, hh), (1.6, y0, hh + 0.1), M["hall_wall"])
    for k, (lo, hi) in enumerate((((-1.6, y0 - 0.06, 0.0), (-DOOR_W / 2 - 0.06, y0, hh)),
                                   ((DOOR_W / 2 + 0.06, y0 - 0.06, 0.0), (1.6, y0, hh)),
                                   ((-DOOR_W / 2 - 0.06, y0 - 0.06, HALL_DOOR_H), (DOOR_W / 2 + 0.06, y0, hh)))):
        _wbox(kit, f"hall_front{k}", lo, hi, M["hall_wall"])
    # the hall runs across in front of the lift, and on away to the left, far longer than the tower is wide
    _wbox(kit, "hall_wall_far", (-1.6, y0 - 1.7, 0.0), (0.9, y0 - 1.6, hh), M["hall_wall"])
    _wbox(kit, "hall_wall_right", (1.5, y0 - 12.0, 0.0), (1.6, y0, hh), M["hall_wall"])
    _wbox(kit, "hall_wall_left", (-1.6, y0 - 12.0, 0.0), (-1.5, y0 - 1.7, hh), M["hall_wall"])
    for k, yy in enumerate((-3.2, -5.4, -7.6)):
        _wbox(kit, f"hall_door{k}", (1.46, y0 + yy - 0.45, 0.0), (1.5, y0 + yy + 0.45, 2.05), M["hall_door"])
        _wbox(kit, f"hall_plate{k}", (1.455, y0 + yy - 0.06, 1.55), (1.46, y0 + yy + 0.06, 1.63), M["brass_dark"])
    # the one dim cold light far down the hall: a wall lamp on the right wall, seen small and cold in the fog
    kit.box("far_lamp", (0.06, 0.34, 0.42), (1.44, y0 - 9.6, 1.9), kit.emit("#a9c4e6", 2.2), bevel=0.02)
    _wbox(kit, "hall_end", (-1.6, y0 - 12.1, 0.0), (1.6, y0 - 12.0, hh), M["hall_wall"])
    for k, x in enumerate((-1.0, 1.0)):   # unlit sconces either side of the lift
        kit.box(f"sconce{k}", (0.12, 0.08, 0.18), (x, y0 - 0.1, 1.7), M["shade"], bevel=0.02)
        kit.box(f"sconce{k}.plate", (0.08, 0.02, 0.12), (x, y0 - 0.07, 1.62), M["brass_dark"])


def set_doors(ctx, gap=DOOR_W, hall=1.0):
    """The car doors close to `gap` metres between their edges; 13's doors open by `hall` (0..1)."""
    w = ctx["leaf_w"]
    for lf, side in ctx["leaves"]["car"]:
        lf.location.x = side * (min(gap, DOOR_W + 0.06) / 2 + w / 2)
    for lf, side in ctx["leaves"]["hall"]:
        lf.location.x = side * (w / 2 + hall * (DOOR_W / 2 + 0.05))


# ------------------------------------------------------------------------------------------------ lights

LIGHT_STATES = {   # gains on each light's base energy; the ceiling never flickers
    "on": {"ceiling": 1.0, "panel_key": 0.15, "diffuser": 1.0},
    # 13: the car's panel down to 5%, the monster lit and not us (no light on its chest, none on the cast but its
    # own cold glow)
    "thirteen": {"ceiling": 0.05, "panel_key": 1.0, "hall": 1.0, "hall_rim": 1.0, "backwash": 1.0, "hall_far": 1.0,
                 "hall_low": 1.0, "sleeve_rim-1": 1.0, "sleeve_rim1": 1.0, "brass_ping": 1.0, "face": 1.0,
                 "face_peak": 1.0, "diffuser": 0.05, "floor13": 1.0, "cast_rim": 1.0},
    "land": {"ceiling": 1.0, "panel_key": 0.15, "diffuser": 1.0, "land_lamp": 1.0},
    "lobby": {"ceiling": 0.7, "panel_key": 0.15, "diffuser": 0.7, "lobby_day": 1.0, "lobby_lamp": 1.0},
    "balc_blue": {"balc_cool": 1.0, "balc_win": 1.0},
    "balc_gold": {"balc_sun": 1.0, "balc_fill": 1.0},
}
BEYOND = {"thirteen": "hall13", "land": "land", "lobby": "lobby"}   # which space shows past the doors
EXTRA_LIGHTS = ("fill", "land_lamp", "lobby_day", "lobby_lamp", "balc_cool", "balc_win", "balc_sun", "balc_fill")
ALL_LIGHTS = ("ceiling", "panel_key", "hall", "hall_rim", "backwash", "hall_far", "hall_low", "sleeve_rim-1",
              "sleeve_rim1", "brass_ping", "face", "face_under", "face_peak", "floor13", "cast_rim") + EXTRA_LIGHTS


def light_gains(c):
    """Every light's gain for a lights cue: the state's, with cast_rim and fill scaled by the cue's own numbers."""
    g = {k: 0.0 for k in ALL_LIGHTS}
    g["diffuser"] = 0.0
    g.update(LIGHT_STATES[c.get("state", "on")])
    g["cast_rim"] *= float(c.get("cast_rim", 0.0))
    g["fill"] = float(c.get("fill", 0.0))
    if "ceiling" in c:
        g["ceiling"] = float(c["ceiling"])
        g["diffuser"] = float(c["ceiling"])
    return g


def build_lights(kit, ctx):
    kit.light("ceiling", "AREA", (0, 0.4, CAR_H - 0.03), 60.0, "#edf3f8", size=0.65)
    # the floor-button panel's glow, beside the doors and at glove height: a low side key on its folded gloves
    kit.light("panel_key", "SPOT", (PANEL_X + 0.07, CAR_Y0 + 0.1, PANEL_Z - 0.15), 42.0, "#e3e6ea", spot=40,
              blend=0.7, size=0.15)   # the lit panel plate's spill: neutral, so the brass still reads as brass
    # 13's cold light: the carpet and wall behind what stands in the doors, so it stands out as a silhouette; a rim
    # on its cap and shoulders; one down each sleeve from either side, so the arms' length reads in outline (and the
    # car doors' leading edges catch it); one far down the hall, in the fog
    kit.light("hall", "AREA", (0.0, SILL_Y - 0.75, 2.42), 80.0, "#a9c4e6", size=0.5)
    kit.light("hall_rim", "AREA", (0.0, SILL_Y - 0.35, 2.3), 32.0, "#a9c4e6", size=0.35)
    # high on 13's back wall, behind its head: its cap stands out black against it, cropped by our door head
    kit.light("backwash", "AREA", (0.0, SILL_Y - 0.9, HALL_H - 0.08), 120.0, "#a9c4e6", size=0.9)
    for sx in (-1, 1):
        kit.light(f"sleeve_rim{sx}", "AREA", (sx * 0.75, SILL_Y - 0.6, 1.5), 80.0, "#a9c4e6", size=0.2)
    # lit carpet behind and beside the gloves, so they hang in front of something rather than on a black floor
    kit.light("floor13", "AREA", (0.0, SILL_Y - 1.3, 2.3), 140.0, "#a9c4e6", size=0.8)
    # a cold rim on the cast only (cue "cast_rim": a gain, 0 when absent), from the hall behind it, for shots where
    # one of us is in the foreground: it draws the hood's outline and nothing else
    kit.light("cast_rim", "AREA", (0.0, CAR_Y0 + 0.3, 2.2), 60.0, "#a9c4e6", size=0.4)
    kit.light("hall_far", "POINT", (-0.9, SILL_Y - 7.5, 2.2), 30.0, "#a9c4e6", size=0.2)
    kit.light("hall_low", "SPOT", (0.25, SILL_Y - 3.0, 0.7), 140.0, "#a9c4e6", spot=35, blend=0.5, size=0.25)
    # 13's light off the sill, seen only in reflections: the brass buttons and piping down its jacket catch it
    ping = kit.light("brass_ping", "AREA", (0.0, CAR_Y0 + 0.25, 0.06), 36.0, "#b9cde6", size=0.5)
    ping.visible_diffuse = False
    # the lit buttons' glow thrown forward from the panel, and up under its own visor
    f = kit.light("face", "AREA", (0, 0, 2.0), 6.0, GLOW, size=0.45)
    f.data.spread = math.radians(95)   # the cold glow that rims the inner side of our heads, and nothing more
    # (the chest light never shows in reflections, so no glass carries a glint that reads as a second eye)
    kit.light("face_under", "POINT", (0, 0, 2.0), 16.0, GLOW, size=0.12).visible_glossy = False
    kit.light("face_peak", "POINT", (0, 0, 2.0), 6.0, GLOW, size=0.05)   # seen in the visor: a cold line on it
    # a soft cold fill on the cast only (cue "fill"): so a face in the talk reads, lit from the doors' side
    kit.aim(kit.light("fill", "AREA", (0.0, CAR_Y0 + 0.2, 0.8), 22.0, "#9db6d6", size=0.5), (0.0, 0.4, 1.5))
    # the 12 landing's lamp, the lobby's daylight and lamp
    kit.light("land_lamp", "AREA", (0.0, SILL_Y - 2.0, 2.4), 90.0, "#f1e2c6", size=0.7)
    kit.aim(kit.light("lobby_day", "AREA", (0.0, SILL_Y - 7.4, 2.2), 380.0, "#e6eef7", size=3.0), (0.0, SILL_Y - 2.0, 1.0))
    kit.light("lobby_lamp", "AREA", (0.0, SILL_Y - 2.5, 3.0), 120.0, "#efe6d2", size=1.2)
    # the balconies (30 m east): blue hour, then low golden sun
    kit.aim(kit.light("balc_cool", "AREA", (BX, -3.0, 4.0), 260.0, "#8fa8d0", size=3.0), (BX, 0.9, 0.8))
    kit.aim(kit.light("balc_win", "AREA", (BX, 1.5, 1.6), 35.0, "#ffcf8a", size=1.0), (BX, 0.0, 1.0))
    kit.aim(kit.light("balc_sun", "AREA", (BX - 2.4, -4.5, 1.5), 1400.0, "#ffb460", size=1.2), (BX, 0.9, 1.1))
    kit.aim(kit.light("balc_fill", "AREA", (BX + 0.3, -1.6, 2.4), 160.0, "#ffd9a8", size=2.5), (BX, 0.9, 1.0))


def link_light(name, objs, state="INCLUDE"):
    """Cycles light linking: with INCLUDE only `objs` take the light; with EXCLUDE everything but them does. None or
    an empty list clears it."""
    ob = bpy.data.objects[name]
    if not objs:
        ob.light_linking.receiver_collection = None
        return
    coll = bpy.data.collections.get(f"link {name}") or bpy.data.collections.new(f"link {name}")
    for o in list(coll.objects):
        coll.objects.unlink(o)
    for o in objs:
        coll.objects.link(o)
    for co in coll.collection_objects:
        co.light_linking.link_state = state
    ob.light_linking.receiver_collection = coll


def brass_parts(att):
    """The Attendant's brass, which the ping light alone may touch: jacket buttons, hem, collar edge, cuffs,
    shoulder-board edges, trouser stripes and the cap band."""
    keys = (".btn", ".hem", ".collar_edge", ".boardedge", ".stripe", ".band", ".frame")
    return [o for o in att["root"].children_recursive if o.type == "MESH" and any(k in o.name for k in keys)]


def glove_point(att, sx=-1):
    """Where a glove's middle is in the world (sx = -1 the right glove, in front)."""
    return att["arms"][sx].matrix_world @ V((0, 0, 0.3 - (ARM_L - GLOVE_L) - GLOVE_L / 2))


def aim_lights(ctx, att):
    """The face light sits in front of the panel, facing the way it faces; the peak light under its visor; the panel
    key on its folded gloves; the sleeve rims down each arm; the ping light up at its jacket; 13's low light skims
    the car's floor past its feet, so its shadow comes in at us."""
    mw = att["head"].matrix_world
    n = (mw.to_3x3() @ V((0, -1, 0))).normalized()
    f = bpy.data.objects["face"]
    f.location = mw @ V((0, -(HEAD_D / 2 + 0.3), 0))
    f.rotation_euler = (-n).to_track_quat("Z", "Y").to_euler()
    bpy.data.objects["face_under"].location = mw @ V((0, -(HEAD_D / 2 + 0.25), -HEAD_S / 2 - 0.9))
    bpy.data.objects["face_peak"].location = mw @ V((0, -(HEAD_D / 2 + 0.05), HEAD_S / 2 - LIP - 0.1))
    head = mw.translation
    gl = (glove_point(att, -1) + glove_point(att, 1)) / 2
    ob = bpy.data.objects["panel_key"]
    ob.rotation_euler = (V(gl) - ob.location).to_track_quat("-Z", "Y").to_euler()
    for sx in (-1, 1):
        ob = bpy.data.objects[f"sleeve_rim{sx}"]
        tgt = att["arms"][sx].matrix_world @ V((0, 0, -1.2))
        ob.rotation_euler = (V(tgt) - ob.location).to_track_quat("-Z", "Y").to_euler()
        ob.data.spread = math.radians(35)   # tight: it draws the sleeve and the door edge, no halo on the leaf
    ob = bpy.data.objects["brass_ping"]
    chest = att["waist"].matrix_world @ V((0, 0, TORSO_H * 0.6))
    ob.rotation_euler = (V(chest) - ob.location).to_track_quat("-Z", "Y").to_euler()
    ob = bpy.data.objects["hall_low"]
    ob.rotation_euler = (V((head.x, CAR_Y0 + 1.2, 0.0)) - ob.location).to_track_quat("-Z", "Y").to_euler()
    ob = bpy.data.objects["floor13"]
    ob.rotation_euler = (V((0.0, SILL_Y - 2.7, 0.0)) - ob.location).to_track_quat("-Z", "Y").to_euler()
    ob = bpy.data.objects["hall"]   # the carpet and wall behind it, so its outline shows against them
    ob.rotation_euler = (V((head.x, SILL_Y - 1.3, 0.3)) - ob.location).to_track_quat("-Z", "Y").to_euler()
    ob = bpy.data.objects["backwash"]
    ob.rotation_euler = (V((0.0, SILL_Y - 1.7, 2.35)) - ob.location).to_track_quat("-Z", "Y").to_euler()
    ob = bpy.data.objects["hall_rim"]   # right behind its head: the rim on its cap, panel and shoulders
    ob.rotation_euler = (V((head.x, head.y, head.z + 0.15)) - ob.location).to_track_quat("-Z", "Y").to_euler()


# ------------------------------------------------------------------------------------- the other places
# The 12 landing, the lobby and the balconies. The landing and the lobby sit past the lift's doors where 13's hall
# does (only one of the three shows at a time: the lights cue's state picks it), and the balconies are 30 m east.


def emit_plain(kit, name, hexc, strength):
    """An emission that ignores the fog (sky cards and the far city: they are the far light itself)."""
    if name in kit.MATS:
        return kit.MATS[name]
    m = kit._new(name)
    nt = m.node_tree
    nt.nodes.remove(nt.nodes["Principled BSDF"])
    e = nt.nodes.new("ShaderNodeEmission")
    e.inputs["Color"].default_value = kit.col(hexc)
    e.inputs["Strength"].default_value = strength
    nt.links.new(e.outputs[0], next(n for n in nt.nodes if n.type == "OUTPUT_MATERIAL").inputs["Surface"])
    try:
        m.emission_sampling = "NONE"
    except Exception:
        pass
    return m


def sky_mat(kit, name, stops):
    """A vertical gradient card, unfogged: stops = [(position 0..1 bottom to top, hex, strength), ...]."""
    if name in kit.MATS:
        return kit.MATS[name]
    m = kit._new(name)
    nt = m.node_tree
    nt.nodes.remove(nt.nodes["Principled BSDF"])
    tc = nt.nodes.new("ShaderNodeTexCoord")
    sep = nt.nodes.new("ShaderNodeSeparateXYZ")
    nt.links.new(tc.outputs["Generated"], sep.inputs[0])
    ramp = nt.nodes.new("ShaderNodeValToRGB")
    els = ramp.color_ramp.elements
    c0 = kit.col(stops[0][1])
    s0 = stops[0][2]
    els[0].position, els[0].color = stops[0][0], (c0[0] * s0, c0[1] * s0, c0[2] * s0, 1)
    c1 = kit.col(stops[-1][1])
    s1 = stops[-1][2]
    els[1].position, els[1].color = stops[-1][0], (c1[0] * s1, c1[1] * s1, c1[2] * s1, 1)
    for pos, h, st in stops[1:-1]:
        e = els.new(pos)
        c = kit.col(h)
        e.color = (c[0] * st, c[1] * st, c[2] * st, 1)
    nt.links.new(sep.outputs["Y"], ramp.inputs["Fac"])
    e = nt.nodes.new("ShaderNodeEmission")
    e.inputs["Strength"].default_value = 1.0
    nt.links.new(ramp.outputs["Color"], e.inputs["Color"])
    nt.links.new(e.outputs[0], next(n for n in nt.nodes if n.type == "OUTPUT_MATERIAL").inputs["Surface"])
    try:
        m.emission_sampling = "NONE"
    except Exception:
        pass
    return m


def materials2(kit):
    return {
        "land_wall": pbr(kit, "landing wall", "#b3a58a", 0.9, noise=(3.0, 0.8)),
        "land_carpet": pbr(kit, "landing carpet", "#3b4860", 0.95, noise=(6.0, 0.6)),
        "land_ceil": pbr(kit, "landing ceiling", "#cdc4b2", 0.9),
        "land_door": pbr(kit, "landing door", "#5b4129", 0.55),
        "room_dark": pbr(kit, "room dark", "#2b2118", 0.9),
        "lobby_floor": pbr(kit, "lobby floor", "#aaa498", 0.32, noise=(4.0, 0.75)),
        "lobby_wall": pbr(kit, "lobby wall", "#928b7e", 0.85, noise=(2.0, 0.85)),
        "steel_black": pbr(kit, "steel black", "#15161a", 0.4, metal=0.8),
        "daylight": emit_plain(kit, "daylight", "#cfe0ef", 1.1),
        "concrete": pbr(kit, "balcony concrete", "#77756f", 0.9, noise=(5.0, 0.7)),
        "stucco": pbr(kit, "stucco", "#8b867a", 0.9, noise=(3.0, 0.85)),
        "terracotta": pbr(kit, "terracotta", "#a5573a", 0.8, noise=(12.0, 0.75)),
        "terra_old": pbr(kit, "terracotta old", "#865039", 0.85, noise=(9.0, 0.6)),
        "leaf": pbr(kit, "leaf", "#3f6d34", 0.7, noise=(14.0, 0.6)),
        "stake": pbr(kit, "stake", "#6a5638", 0.8),
        "tomato": pbr(kit, "tomato", "#b72c24", 0.32, spec=0.6),
        "soil": pbr(kit, "soil", "#2a1f16", 0.95),
        "slider": pbr(kit, "slider glass", "#0a1017", 0.06, spec=0.7),
        "skin_me": kit.plastic("#d7a17a", 0.5),
        "sleeve_me": kit.plastic("#6a5c94", 0.6),
        "phone": pbr(kit, "phone", "#0b0b0e", 0.2, spec=0.6),
        "scratch": pbr(kit, "scratch", "#b7babf", 0.5, metal=0.8),
        "sky_blue": sky_mat(kit, "sky blue", [(0.0, "#46627f", 0.9), (0.25, "#2a4261", 0.8), (1.0, "#0c1424", 0.7)]),
        "sky_gold": sky_mat(kit, "sky gold", [(0.0, "#f3a04c", 1.0), (0.22, "#e08a52", 0.9), (0.55, "#7a8cae", 0.7),
                                              (1.0, "#4a638f", 0.7)]),
        "city_blue": emit_plain(kit, "city blue", "#1b2535", 0.9),
        "city_gold": emit_plain(kit, "city gold", "#6e4a40", 0.9),
        "window": emit_plain(kit, "window", "#ffcf80", 1.3),
    }


def grouped(ctx, name, fn):
    before = set(bpy.data.objects)
    fn()
    ctx.setdefault("grp", {})[name] = [o for o in bpy.data.objects if o not in before]


def build_land(kit, ctx, M):
    """The 12 landing: pale beige walls, slate-blue carpet, two front doors side by side on the end wall with blank
    plates (they swing in), the lift behind us. Short and ordinary, so 13's long hall reads as wrong later."""
    y0, yE, hh = SILL_Y, SILL_Y - 3.9, 2.5
    _wbox(kit, "land_floor", (-1.6, yE, -0.1), (1.6, y0, 0.0), M["land_carpet"])
    _wbox(kit, "land_ceiling", (-1.6, yE, hh), (1.6, y0, hh + 0.1), M["land_ceil"])
    _wbox(kit, "land_wall_l", (-1.6, yE, 0.0), (-1.5, y0, hh), M["land_wall"])
    _wbox(kit, "land_wall_r", (1.5, yE, 0.0), (1.6, y0, hh), M["land_wall"])
    for k, (lo, hi) in enumerate((((-1.6, y0 - 0.06, 0.0), (-DOOR_W / 2 - 0.06, y0, hh)),
                                   ((DOOR_W / 2 + 0.06, y0 - 0.06, 0.0), (1.6, y0, hh)),
                                   ((-DOOR_W / 2 - 0.06, y0 - 0.06, 2.1), (DOOR_W / 2 + 0.06, y0, hh)))):
        _wbox(kit, f"land_front{k}", lo, hi, M["land_wall"])
    # the end wall with two door openings, a dark room behind each
    for k, (xa, xb) in enumerate(((-1.6, -1.0), (-0.1, 0.1), (1.0, 1.6))):
        _wbox(kit, f"land_end{k}", (xa, yE - 0.15, 0.0), (xb, yE, hh), M["land_wall"])
    for k, (xa, xb) in enumerate(((-1.0, -0.1), (0.1, 1.0))):
        _wbox(kit, f"land_end_top{k}", (xa, yE - 0.15, 2.05), (xb, yE, hh), M["land_wall"])
        _wbox(kit, f"room_back{k}", (xa - 0.05, yE - 1.6, 0.0), (xb + 0.05, yE - 1.5, hh), M["room_dark"])
        _wbox(kit, f"room_floor{k}", (xa - 0.05, yE - 1.6, -0.1), (xb + 0.05, yE, 0.0), M["room_dark"])
        _wbox(kit, f"room_side{k}", (xa - 0.05, yE - 1.6, 0.0), (xa - 0.04, yE, hh), M["room_dark"])
        _wbox(kit, f"room_side2{k}", (xb + 0.04, yE - 1.6, 0.0), (xb + 0.05, yE, hh), M["room_dark"])
    doors = []
    for side, hx in ((1, 1.0), (-1, -1.0)):   # side +1: the door on the right of the end wall, hinged at x = 1.0
        hinge = kit.empty(f"land_hinge{side}", (hx, yE - 0.03, 0.0))
        lf = kit.box(f"land_leaf{side}", (0.9, 0.05, 2.04), (-side * 0.45, 0, 1.02), M["land_door"], hinge, bevel=0.005)
        kit.box(f"land_plate{side}", (0.1, 0.012, 0.06), (-side * 0.75, 0.03, 1.45), M["brass_dark"], hinge)
        kit.box(f"land_handle{side}", (0.12, 0.04, 0.025), (-side * 0.8, 0.04, 1.05), M["brass"], hinge)
        doors.append((hinge, side))
        for (lo, hi) in ((((-0.05 + hx), yE - 0.02, 0.0), (hx + 0.05 if side > 0 else hx - 0.05, yE + 0.0, 2.1)),):
            pass
    ctx["land_doors"] = doors
    _wbox(kit, "land_skirt", (-1.5, yE, 0.0), (1.5, y0, 0.09), M["brass_dark"])   # a dark skirting round the landing
    # nothing else: a lamp (the lights cue) and the lift


def set_land_doors(ctx, v):
    for hinge, side in ctx["land_doors"]:
        hinge.rotation_euler = (0, 0, math.radians(side * 98.0 * v))


def build_lobby(kit, ctx, M):
    """The lobby: a pale stone floor, plain walls, the lift in the side of it, and glass street doors in black
    steel at the far end with soft daylight beyond. No signs, no mailboxes."""
    y0, yE, hh, hw = SILL_Y, SILL_Y - 8.6, 3.1, 3.4
    _wbox(kit, "lobby_floor", (-hw, yE, -0.1), (hw, y0, 0.0), M["lobby_floor"])
    _wbox(kit, "lobby_ceiling", (-hw, yE, hh), (hw, y0, hh + 0.1), M["land_ceil"])
    _wbox(kit, "lobby_wall_l", (-hw, yE, 0.0), (-hw + 0.1, y0, hh), M["lobby_wall"])
    _wbox(kit, "lobby_wall_r", (hw - 0.1, yE, 0.0), (hw, y0, hh), M["lobby_wall"])
    for k, (lo, hi) in enumerate((((-hw, y0 - 0.06, 0.0), (-DOOR_W / 2 - 0.06, y0, hh)),
                                   ((DOOR_W / 2 + 0.06, y0 - 0.06, 0.0), (hw, y0, hh)),
                                   ((-DOOR_W / 2 - 0.06, y0 - 0.06, 2.1), (DOOR_W / 2 + 0.06, y0, hh)))):
        _wbox(kit, f"lobby_front{k}", lo, hi, M["lobby_wall"])
    # the street wall: a steel frame holding bright daylight panes (a plane of light, no glass to reflect in)
    _wbox(kit, "street_light", (-hw + 0.1, yE - 0.4, 0.0), (hw - 0.1, yE - 0.35, hh), M["daylight"])
    for k, x in enumerate((-2.2, -0.8, 0.8, 2.2)):
        pass
    for k, x in enumerate((-hw + 0.1, -1.55, -0.05, 1.45, hw - 0.2)):
        _wbox(kit, f"street_post{k}", (x, yE - 0.12, 0.0), (x + 0.1, yE, hh), M["steel_black"])
    for k, z in enumerate((0.0, 1.05, 2.15, hh - 0.1)):
        _wbox(kit, f"street_rail{k}", (-hw + 0.1, yE - 0.12, z), (hw - 0.1, yE, z + 0.1), M["steel_black"])
    for k, x in enumerate((-1.1, 0.4, 1.9, -2.6)):   # push bars
        _wbox(kit, f"street_bar{k}", (x, yE - 0.2, 1.0), (x + 0.6, yE - 0.16, 1.04), M["brass"])


def build_balcony(kit, ctx, M):
    """The two balconies, 12A (mine, bare) on the left and 12B (his, crowded with pots) on the right, a low concrete
    wall between. The building's face behind, the open city before, a gradient sky card for each hour."""
    b = BX
    # the building's face and the slab above
    _wbox(kit, "facade", (b - 6.0, 1.7, -3.0), (b + 6.0, 1.85, 6.0), M["stucco"])
    _wbox(kit, "slab_above", (b - 4.4, -0.1, 2.6), (b + 4.4, 1.85, 2.8), M["concrete"])
    _wbox(kit, "slab_floor", (b - 4.4, -0.1, -0.2), (b + 4.4, 1.7, 0.0), M["concrete"])
    for side, cx in ((-1, b - 1.1), (1, b + 1.1)):
        _wbox(kit, f"slider{side}", (cx - 0.7, 1.68, 0.0), (cx + 0.7, 1.7, 2.2), M["slider"])
        _wbox(kit, f"slider_frame{side}", (cx - 0.72, 1.66, 2.2), (cx + 0.72, 1.7, 2.26), M["steel_black"])
        _wbox(kit, f"slider_mid{side}", (cx - 0.02, 1.66, 0.0), (cx + 0.02, 1.7, 2.2), M["steel_black"])
        _wbox(kit, f"slider_l{side}", (cx - 0.74, 1.66, 0.0), (cx - 0.7, 1.7, 2.2), M["steel_black"])
        _wbox(kit, f"slider_r{side}", (cx + 0.7, 1.66, 0.0), (cx + 0.74, 1.7, 2.2), M["steel_black"])
    # the low wall between, and the rail along the outer edge
    _wbox(kit, "divider", (b - 0.07, 0.0, 0.0), (b + 0.07, 1.7, 1.05), M["concrete"], bevel=0.01)
    _wbox(kit, "divider_cap", (b - 0.1, 0.0, 1.05), (b + 0.1, 1.7, 1.09), M["concrete"], bevel=0.008)
    for z0, z1 in ((1.04, 1.1), (0.5, 0.54)):
        _wbox(kit, f"rail_{z0}", (b - 4.4, 0.0, z0), (b + 4.4, 0.05, z1), M["steel_black"])
    for k in range(17):
        x = b - 4.4 + k * 0.55
        _wbox(kit, f"rail_post{k}", (x, 0.0, 0.0), (x + 0.04, 0.05, 1.1), M["steel_black"])
    _wbox(kit, "side_l", (b - 4.45, -0.1, 0.0), (b - 4.4, 1.7, 1.05), M["concrete"])
    _wbox(kit, "side_r", (b + 4.4, -0.1, 0.0), (b + 4.45, 1.7, 1.05), M["concrete"])
    # his pots and vines
    spots = [(0.55, 0.28), (1.15, 0.26), (1.8, 0.3), (2.45, 0.25), (3.1, 0.3), (1.4, 1.35), (2.2, 1.4), (3.0, 1.35),
             (3.7, 1.2)]
    plants = []
    for k, (px, py) in enumerate(spots):
        r = 0.16 + 0.02 * (k % 3)
        h = 0.3 + 0.03 * (k % 2)
        kit.cyl(f"pot{k}", r, h, (b + px, py, h / 2), M["terracotta"], r2=r * 0.78)
        kit.cyl(f"soil{k}", r * 0.92, 0.02, (b + px, py, h + 0.005), M["soil"])
        hgt = 0.9 + 0.12 * (k % 4)
        kit.cyl(f"stake{k}", 0.012, hgt, (b + px, py, h + hgt / 2), M["stake"], n=8)
        for j in range(4):
            lz = h + 0.25 + j * hgt * 0.2
            kit.box(f"leaf{k}.{j}", (0.26, 0.2, 0.05), (b + px + 0.04 * ((j % 2) * 2 - 1), py + 0.02, lz), M["leaf"],
                    rot=(0.2 * j, 0.0, 0.7 * j + k), bevel=0.01)
        if k % 2 == 0:
            ob = kit.sphere(f"tom_plant{k}", 0.034, (b + px + 0.1, py - 0.03, h + 0.42 + 0.05 * (k % 3)), M["tomato"], seg=10)
            plants.append(ob)
    # the big old pot, on a plinth by the divider: the one that was hers (no line says so)
    kit.box("plinth", (0.5, 0.5, 0.4), (b + 0.55, 1.15, 0.2), M["concrete"], bevel=0.01)
    kit.cyl("bigpot", 0.27, 0.46, (b + 0.55, 1.15, 0.63), M["terra_old"], r2=0.21)
    kit.cyl("bigsoil", 0.25, 0.02, (b + 0.55, 1.15, 0.865), M["soil"])
    kit.cyl("bigstake", 0.014, 1.3, (b + 0.55, 1.15, 1.52), M["stake"], n=8)
    for j in range(6):
        kit.box(f"bigleaf{j}", (0.3, 0.24, 0.05), (b + 0.55 + 0.05 * ((j % 2) * 2 - 1), 1.15, 1.0 + j * 0.18), M["leaf"],
                rot=(0.2 * j, 0.0, 0.7 * j), bevel=0.01)
    # tomatoes that arrive on the divider's cap (cue "tomatoes": how many)
    ctx["wall_toms"] = [kit.sphere(f"wall_tom{k}", 0.05, (b + 0.0 + (k - 1.5) * 0.0, 0.35 + k * 0.28, 1.09 + 0.05), M["tomato"], seg=12)
                        for k in range(5)]
    for ob in ctx["wall_toms"]:
        ob.hide_render = True
    # the sky cards, the far city and its windows
    ctx["sky"] = {}
    for nm in ("blue", "gold"):
        card = kit.plane(f"sky_{nm}", (700, 260), (b, -210.0, 100.0), M[f"sky_{nm}"], rot=(math.pi / 2, 0, 0))
        ctx["sky"][nm] = [card]
    import random
    rnd = random.Random(14)
    city, wins = [], []
    for k in range(34):
        w = rnd.uniform(6, 16)
        d = rnd.uniform(6, 14)
        h = rnd.uniform(8, 38)
        x = b - 120 + k * 7.2 + rnd.uniform(-2, 2)
        y = -rnd.uniform(70, 140)
        for nm in ("blue", "gold"):
            ob = kit.box(f"city_{nm}{k}", (w, d, h), (x, y, h / 2 - 2), M[f"city_{nm}"])
            ctx["sky"][nm].append(ob)
        for j in range(rnd.randint(3, 8)):
            wz = rnd.uniform(1.0, h - 3)
            wx = x + rnd.uniform(-w / 2 + 1, w / 2 - 1)
            ob = kit.box(f"cwin{k}.{j}", (0.9, 0.1, 1.1), (wx, y + d / 2 + 0.06, wz - 2), M["window"])
            ctx["sky"]["blue"].append(ob)
    # tally: five scratches on the lift's button panel, below the buttons (a small mark for anyone who looks)
    for k in range(4):
        _wbox(kit, f"tally{k}", (PANEL_X - 0.065 + k * 0.03, CAR_Y0 + 0.0075, 0.715),
              (PANEL_X - 0.0635 + k * 0.03, CAR_Y0 + 0.0095, 0.76), M["scratch"])
    ob = _wbox(kit, "tally4", (PANEL_X - 0.075, CAR_Y0 + 0.0095, 0.7375), (PANEL_X + 0.03, CAR_Y0 + 0.0115, 0.7395),
               M["scratch"])
    ob.rotation_euler = (0, math.radians(-38), 0)
    # the fog is the car's: nothing here uses it for the far light
    ctx["plants"] = plants


# -------------------------------------------------------------------------------------------- the story


def _cues(tl, name):
    return [c for c in tl.get("cues", []) if c["name"] == name]


def _last(cs, t):
    cur = None
    for c in cs:
        if c["t"] <= t + 1e-9:
            cur = c
    return cur or (cs[0] if cs else None)


def _prev(cs, c):
    i = cs.index(c) if c in cs else 0
    return cs[i - 1] if i > 0 else None


def _lerp_dict(a, b, u):
    return {k: a.get(k, 0.0) + (b.get(k, 0.0) - a.get(k, 0.0)) * u for k in set(a) | set(b)}


def _ramp_u(c, t, default=0.0):
    d = float(c.get("dur", default))
    return 1.0 if d <= 1e-6 else kit_ss((t - c["t"]) / d)


def kit_ss(x):
    x = min(1.0, max(0.0, x))
    return x * x * (3 - 2 * x)


def build(kit, story, tl):
    ctx = {}
    M = materials(kit)
    M.update(materials2(kit))
    ctx["M"] = M
    opts = story.get("set_options", {})
    ctx["style"] = opts.get("glow_style", "ring")
    build_car(kit, ctx, M)
    grouped(ctx, "hall13", lambda: build_hall(kit, ctx, M))
    grouped(ctx, "land", lambda: build_land(kit, ctx, M))
    grouped(ctx, "lobby", lambda: build_lobby(kit, ctx, M))
    ctx["att"] = build_attendant(kit, M, cap=opts.get("cap", True), grid=opts.get("grid", DEFAULT_GRID),
                                 style=ctx["style"], head_style=opts.get("head", "socket"))
    build_lights(kit, ctx)
    build_balcony(kit, ctx, M)
    link_light("brass_ping", brass_parts(ctx["att"]))
    # the sleeve rims draw its arms and the car doors' leading edges, and nothing else (not us, not its face)
    arm_parts = [o for o in ctx["att"]["root"].children_recursive if o.type == "MESH"
                 and any(k in o.name for k in (".sleeve", ".glove", ".board")) and ".boardedge" not in o.name]
    leaves = [o for lf, _ in ctx["leaves"]["car"] for o in lf.children if o.name.endswith(".edge")]   # the thin lines only
    for sx in (-1, 1):
        link_light(f"sleeve_rim{sx}", arm_parts + leaves)
    # the finger that presses a button (inserts), and its sleeve
    ctx["finger"] = [kit.box("finger", (0.024, 0.07, 0.024), (0, 0, 0), M["skin_me"], bevel=0.008),
                     kit.box("finger_sleeve", (0.07, 0.4, 0.07), (0, 0, 0), M["sleeve_me"], bevel=0.02)]
    ctx["tom_ins"] = kit.sphere("tom_ins", 0.05, (0, 0, 0), M["tomato"], seg=12)
    ctx["finger"].append(ctx["tom_ins"])
    for ob in ctx["finger"]:
        ob.hide_render = True
    animate(kit, story, tl, 0.0, ctx)
    return ctx


def panel_slot_xz(i):
    """World (x, z) of a floor-panel button (the layout build_panel uses)."""
    pw, ph, dz = 0.2, 0.9, 0.066
    rows = [(PANEL_X + (c - 0.5) * 0.085, PANEL_Z + ph / 2 - 0.08 - r * dz) for r in range(10) for c in range(2)]
    slots = rows[::-1]
    z_low = PANEL_Z + ph / 2 - 0.08 - 10 * dz - 0.02
    slots += [(PANEL_X + 0.0425, z_low), (PANEL_X - 0.0425, z_low)]
    return slots[i]


def _late(kit, story, ctx):
    """Things parented to a character: they exist only once the cast is built (after build())."""
    if ctx.get("late") or not bpy.data.objects.get("me.arm1"):
        return
    M = ctx["M"]
    arm = bpy.data.objects["me.arm1"]
    ph = kit.box("phone", (0.3, 0.05, 0.62), (0, -0.55, -1.55), M["phone"], arm, bevel=0.02)
    ctx["phone"] = ph
    tom = bpy.data.objects.get("okafor.arm1")
    if tom:
        ctx["hand_tomato"] = kit.sphere("hand_tomato", 0.16, (0, -0.66, -1.72), M["tomato"], tom, seg=12)
    ctx["late"] = True


def animate(kit, story, tl, t, ctx):
    att = ctx["att"]
    _late(kit, story, ctx)
    # --- the Attendant: pose, and each button's glow (a change eases over the cue's "dur", default 0.12 s)
    acs = _cues(tl, "attendant")
    a_c = _last(acs, t) or {}
    a = {**POSES.get(a_c.get("pose"), {}), **a_c}
    grid = att["grid"]

    def gains_of(c):
        cc = {**POSES.get(c.get("pose"), {}), **c}
        return lit_gains(grid, cc.get("lit", [GRIDS[grid]["eye"]]), cc.get("glow", 1.0), cc.get("eye", 1.0))

    gains = gains_of(a_c) if a_c else [0.0] * len(att["buttons"])
    pc = _prev(acs, a_c) if a_c else None
    if pc is not None:
        u = _ramp_u(a_c, t, 0.12)
        if u < 1.0:
            gains = [x + (y - x) * u for x, y in zip(gains_of(pc), gains)]
    pose_attendant(att, a.get("pos", (0.0, SILL_Y - 0.4)), a.get("yaw", 180.0), a.get("lean", 0.0), a.get("bend", 0.0),
                   a.get("head", (0.0, 0.0, 0.0)), gains, a.get("hidden", not a_c), a.get("fold", 1.0))
    bpy.context.view_layer.update()
    aim_lights(ctx, att)
    # --- the doors (eased over the cue's "dur") and the landing's
    dcs = _cues(tl, "doors")
    d = _last(dcs, t) or {}
    gap, hall = d.get("gap", 0.0), d.get("hall", 0.0)
    pd = _prev(dcs, d) if d else None
    if pd is not None:
        u = _ramp_u(d, t, 0.0)
        gap = pd.get("gap", 0.0) + (gap - pd.get("gap", 0.0)) * u
        hall = pd.get("hall", 0.0) + (hall - pd.get("hall", 0.0)) * u
    if d.get("recoil"):   # a stop dead with a 2 cm recoil and a short shudder (the bump)
        gap += kit.spring(t, d["t"], d["recoil"], 14.0, 9.0)
    set_doors(ctx, gap, hall)
    ldc = _last(_cues(tl, "land_doors"), t) or {}
    set_land_doors(ctx, kit_ss((t - ldc["t"]) / ldc.get("dur", 0.6)) * ldc.get("open", 0.0) if ldc else 0.0)
    ind = _last(_cues(tl, "indicator"), t) or {}
    set_indicator(ctx, str(ind.get("floor", "12")), ind.get("arrow"))
    # --- the lights (a change eases over the cue's "dur": the car's panel dims, never cuts)
    lcs = _cues(tl, "lights")
    lc = _last(lcs, t) or {}
    g = light_gains(lc)
    pl_ = _prev(lcs, lc) if lc else None
    if pl_ is not None:
        u = _ramp_u(lc, t, 0.0)
        if u < 1.0:
            g = _lerp_dict(light_gains(pl_), g, u)
    state = lc.get("state", "on")
    beyond = BEYOND.get(state)
    if pl_ is not None and _ramp_u(lc, t, 0.0) < 1.0 and BEYOND.get(pl_.get("state")):
        beyond = beyond or BEYOND.get(pl_.get("state"))
    for name, objs in ctx["grp"].items():
        for o in objs:
            o.hide_render = name != beyond
    dark = bool(lc.get("cast_dark")) and bool(story.get("cast"))
    cast = [o for o in bpy.data.objects if o.type == "MESH"
            and any(o.name == n or o.name.startswith(n + ".") for n in story.get("cast", {}))]
    if ctx.get("cast_dark") != dark and (cast or not dark):
        link_light("ceiling", cast if dark else [], "EXCLUDE")
        ctx["cast_dark"] = dark
    if (g["cast_rim"] or g["fill"]) and cast:
        if not ctx.get("cast_rim"):
            link_light("cast_rim", cast)
            link_light("fill", cast)
            ctx["cast_rim"] = True
    lit = sum(1 for x in gains if x > 0)
    for k in ("face", "face_under", "face_peak"):
        g[k] = g[k] * lit / len(gains) * a.get("glow", 1.0) if lit and not a.get("hidden", not a_c) else 0.0
    g["face_peak"] *= a.get("peak", 1.0)
    for k in ("backwash", "hall", "hall_rim"):
        g[k] *= a.get("wash", 1.0)
    g["panel_key"] *= a.get("key", 1.0)
    ctx["M"]["diffuser"].node_tree.nodes["glow"].inputs["Strength"].default_value = 3.0 * g.pop("diffuser")
    ctx["M"]["segment"].node_tree.nodes["glow"].inputs["Strength"].default_value = 0.5
    pl = (_last(_cues(tl, "panel"), t) or {}).get("lit", [])
    for i, m in enumerate(ctx["panel_buttons"]):
        set_button(m, 2.4 if i in pl else 0.0)
    # --- the finger: on a floor-panel button, pressed in by "press" (0..1), coming in from the car
    fc = _last(_cues(tl, "finger"), t) or {}
    if fc.get("on"):
        x, z = panel_slot_xz(fc["button"])
        press = fc.get("press", 0.0)
        if fc.get("dur"):
            press *= kit_ss((t - fc["t"]) / fc["dur"])
        y0 = CAR_Y0 + 0.02 + 0.035 - 0.012 * press
        if fc.get("tomato"):
            ctx["tom_ins"].location = (x, y0 + 0.045 - 0.04 * (1 - press), z)
        else:
            ctx["finger"][0].location = (x, y0, z)
            ctx["finger"][1].location = (x + 0.02, y0 + 0.035 + 0.2, z - 0.03)
            ctx["finger"][1].rotation_euler = (math.radians(-6), 0, 0)
    for k, ob in enumerate(ctx["finger"]):
        ob.hide_render = not fc.get("on") or (k == 2) != bool(fc.get("tomato"))
    # --- the balconies: which hour, the tomatoes on the wall
    sky = (_last(_cues(tl, "sky"), t) or {}).get("hour")
    for nm, objs in ctx["sky"].items():
        for o in objs:
            o.hide_render = nm != sky
    n_t = (_last(_cues(tl, "tomatoes"), t) or {}).get("n", 0)
    for k, ob in enumerate(ctx["wall_toms"]):
        ob.hide_render = k >= n_t
    for ob in ctx["plants"]:
        ob.hide_render = False
    # --- props and the headphones (on my ears, then round my neck from L65)
    pr = _last(_cues(tl, "props"), t) or {}
    if ctx.get("phone"):
        ctx["phone"].hide_render = not pr.get("phone")
    if ctx.get("hand_tomato"):
        ctx["hand_tomato"].hide_render = not pr.get("tomato")
    from blocky import acting
    me_hidden = acting.state(tl, "me", t)["hidden"] if tl.get("acting", {}).get("me") else True
    hpc = (_last(_cues(tl, "headphones"), t) or {}).get("where", "ears")
    for o in bpy.data.objects:
        if o.name.startswith("me.hpe_"):
            o.hide_render = me_hidden or hpc != "ears"
        elif o.name.startswith("me.hpn_"):
            o.hide_render = me_hidden or hpc != "neck"
    return g
