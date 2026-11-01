"""Knock Back: Uncle Ray's farmhouse kitchen, its cellar under the floor, the yard at night and at dawn, and the
keeper. Built from kit.py's parts (story 2, ep12; nothing here is shared with another story's set).

Coordinates: the kitchen floor's top is z = 0. The kitchen runs x = -2.7 .. 2.7 and y = -3.2 (the front wall, with
the front door) .. 3.2 (the back wall, the stove and the clock). The ceiling is 2.45 m, with beams across it. The
floor is real boards with real gaps (one warped board leaves a gap a hand wide), over joists and a dark crawlspace
0.9 m deep. The cellar door is set into the floor near the middle of the room, by the one bulb; stone steps go down
from its front edge toward the back of the house, and its bolt is on the cellar side. Outside, the porch and its three steps are in front of the front door (-y), the yard is dry dust with low
fog, and the kitchen window over the sink is on the left wall (-x).

THE KEEPER (note 18, "Uncanny beats tentacles"): a person built from the same R6 blocks as Ray and me, but wrong. Its
torso is 2.2 times as wide as a person's and half as deep. Its limbs are a normal length and block width. It wears
faded crimson long johns with a button placket and cellar dust, its skin is pale tallow and its four knuckles
on each hand are worn pale. Its face is our house style (faces.py, round eyes) with no brows and a thin dark mouth
slot open onto black, and it never blinks or changes: the texture is drawn once. `build_keeper()` makes it once and `pose_keeper()` only places those
same parts, so it is the same thing in every shot. It crawls belly up on hands and heels, head first, and its head
stays level and still, upside down to whoever it looks at.

Cues read here (all optional):
- shot: {"look": {...} or null} one shot's own light, on for exactly that shot's frames (shot_look below)
- keeper: {"pose": "hidden" | "crawl" | "rise" | "door" | "under", ...} the keeper from here; a cue with "glide"
  moves it steadily from the one before (crawl: "where" [x, y], "heading"; rise: "neck" [y, z], "slope"; door:
  "climb" 0..1; under: "head_at" [x, y, z]; "face": "cam", "me" or a point; "hand_l"/"hand_r": a hand put there)
- keeper_knock: {"pattern": [s, ..], "side": 0 | 1} its knuckles come down on each knock
- arm_to: {"who", "arm", "to": [x, y, z] or null, "pattern", "knock_at"} a person's arm aimed at a point and
  knocking there (close-ups of a hand only: the arm stretches to reach)
- fist: {"who", "arm", "pattern"} a fist knocking (the arm lifts and comes down on each knock)
- settle: the bulb's swing dies away from here; supper: {"on"} plates on the table; trail: {"a", "b"} the drag
  trails; rake: {"on"} Ray's rake; clock: {"h", "m"} the wall clock's hands
- swing: {"amp": radians} the bulb swings from here (a damped pendulum); knock cues swing it too
- knock_below: {"amp": .., "board": true} a knock from below: the bulb swings, and with "board" the pale board jumps
- dust: {"dur": s} dust sifts down through the boards from here
- trapdoor: {"open": 0..1, "dur": s} the cellar door opens or shuts over dur
- bolt: {"open": bool, "dur": s} the bolt under the cellar door slides back or shut
- shadow: {"on": bool, "x": offset, "dur": s} the visitor's soft shadow on the frosted glass, sliding to x over dur
- time: {"time": "night" | "dawn" | "dusk" | "day"} the light outside
- truck: {"state": "parked" | "go" | "gone"} Ray's truck in the yard, pulling away into the fog, or gone
- hat: {"on": "ray" | "hook" | "fall"} where Ray's straw hat is (fall: knocked off his head)

Acting keys read here (acting.py ignores them): "sit": true bends both legs forward; "kneel": true folds them back
along the floor (put the character's z at -0.5); "bend": degrees the torso bends forward at the hips.

The story's "exterior_shots" get the yard's fog and haze; "fog_gain" {shot: x} thins it for a high or long shot.
"""

from __future__ import annotations

import math

import bpy
import numpy as np
from mathutils import Matrix, Vector as V

from blocky import faces, rig

# ------------------------------------------------------------------------------------------------ the house
X0, X1, Y0, Y1 = -2.7, 2.7, -3.2, 3.2       # the kitchen's inside
CEIL = 2.45
BOARD = 0.2                                  # floor board pitch (boards run along y)
GAP = 0.012                                  # the gap between boards
CRAWL = -0.9                                 # the crawlspace's dirt (deep enough to lie in under the joists)
# the cellar door: an opening in the floor on board seams, hinged along its back edge (y = TY1)
TX0, TX1, TY0, TY1 = -0.6, 1.2, -0.15, 0.95
TXM = (TX0 + TX1) / 2
STAIR_ANGLE = 50.0                           # degrees; the stone steps go down toward +y from the front edge
CELLAR_Z = -2.4
CX0, CX1, CY1 = -0.95, 1.55, 3.1             # the cellar box (wider than its door)
BULB = (-0.35, -0.1, 1.98)                   # the one bulb, between the cellar door and the table
CORD_TOP = (-0.35, -0.1, CEIL)
PALE_X = TX0 - 0.1                           # the worn pale board, beside the cellar door (one board's centre)
WIDE_GAP_X = -1.1                            # one board warped narrow: a gap a hand wide, the eye's gap
DOOR_X = -1.25                               # the front door's centre (front wall, y = Y0)
DOOR_W, DOOR_H = 0.92, 2.05
WIN_Y, WIN_W = 2.2, 1.0                      # the kitchen window over the sink (left wall)
STOVE = (-2.3, -1.55)                        # the cast-iron stove against the left wall, by the door
TABLE = (-1.75, 0.3)                         # the kitchen table (0.85 x 1.5, oilcloth), along the left side
CHAIRS = [(-0.98, 0.05, -1, 0), (-1.75, 1.3, 0, -1)]   # Ray's (beside the pale board, facing the table), mine
PORCH_Y = Y0 - 1.9                           # the porch's front edge; the yard is YARD_Z below the floor
YARD_Z = -0.62
TRUCK = (5.6, -9.8)                          # where Ray parks

# ------------------------------------------------------------------------------------------------ the keeper
KS = rig.S                                   # metres per rig unit, the same blocks as everyone
T_W, T_L, T_D = 2.2 * 2 * KS, 2 * KS, 0.5 * KS
LIMB, LW = 2 * KS, KS
HEAD_SC = 1.12
HH = faces.HEAD_H * KS * HEAD_SC
HR = faces.HEAD_R * KS * HEAD_SC
JOHNS, SKIN, KNUCKLE = "#7a2a2e", "#e6d7ba", "#efe6d2"   # crimson cloth, pale tallow skin (round 1, P3)
EYE_GLOW = 5.5                               # the brightest thing in its shots (round 1, P1)
BULB_W, FILL_W = 190.0, 65.0


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


def _shot(tl, t):
    for s in tl["shots"]:
        if s["start"] <= t < s["end"]:
            return s
    return tl["shots"][-1]


# ------------------------------------------------------------------------------------------------ materials


def _mixed(kit, name, base, dust, amount, scale=6.0, rough=0.9, dark=None):
    """A flat colour with soft patches of another (dust on cloth, wear on wood), in object space."""
    if name in kit.MATS:
        return kit.MATS[name]
    m = kit._new(name)
    nt = m.node_tree
    N, L = nt.nodes, nt.links
    b = N["Principled BSDF"]
    b.inputs["Roughness"].default_value = rough
    tc = N.new("ShaderNodeTexCoord")
    nz = N.new("ShaderNodeTexNoise")
    nz.inputs["Scale"].default_value = scale
    nz.inputs["Detail"].default_value = 6.0
    L.new(tc.outputs["Object"], nz.inputs["Vector"])
    ramp = N.new("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].position = 0.62 - amount * 0.5
    ramp.color_ramp.elements[0].color = kit.col(base)
    ramp.color_ramp.elements[1].position = 0.78 - amount * 0.4
    ramp.color_ramp.elements[1].color = kit.col(dust)
    if dark:
        e = ramp.color_ramp.elements.new(0.2)
        e.color = kit.col(dark)
    L.new(nz.outputs["Fac"], ramp.inputs["Fac"])
    L.new(ramp.outputs["Color"], b.inputs["Base Color"])
    kit._fogged(m, b.outputs[0])
    return m


def _image_mat(kit, name, pil, rough=0.5, emit=0.0):
    img = bpy.data.images.new(name, pil.width, pil.height, alpha=pil.mode == "RGBA")
    a = np.asarray(pil.convert("RGBA")).astype(np.float32)[::-1] / 255
    img.pixels.foreach_set(a.ravel())
    img.pack()
    m = kit._new(name)
    nt = m.node_tree
    b = nt.nodes["Principled BSDF"]
    b.inputs["Roughness"].default_value = rough
    tx = nt.nodes.new("ShaderNodeTexImage")
    tx.image = img
    nt.links.new(tx.outputs["Color"], b.inputs["Base Color"])
    if emit:
        nt.links.new(tx.outputs["Color"], b.inputs["Emission Color"])
        b.inputs["Emission Strength"].default_value = emit
    if pil.mode == "RGBA":
        nt.links.new(tx.outputs["Alpha"], b.inputs["Alpha"])
    kit._fogged(m, b.outputs[0])
    return m, img


def _wbox(kit, name, lo, hi, mat, parent=None):
    """A box given by its world corners, with object space = world space (so wood bands line up board to board)."""
    c = tuple((a + b) / 2 for a, b in zip(lo, hi))
    s = tuple(b - a for a, b in zip(lo, hi))
    return kit.mesh_obj(name, kit.box_verts(*s, c), kit.BOX_FACES, mat, parent)


def frame(x, y, z, loc):
    M = Matrix((tuple(x), tuple(y), tuple(z))).transposed().to_4x4()
    M.translation = V(loc)
    return M


# ------------------------------------------------------------------------------------------------ the keeper


def build_keeper(kit, ctx):
    """The keeper, built once: every part is an object placed by pose_keeper()."""
    johns = _mixed(kit, "long johns", JOHNS, "#86484c", 0.12, 9.0, 0.92, dark="#5c1c22")
    dusty = _mixed(kit, "long johns dusty", JOHNS, "#966a68", 0.4, 12.0, 0.95, dark="#5c1c22")
    placket = kit.plastic("#5a1a20", 0.85, name="johns placket")
    button = kit.plastic("#d8ccb0", 0.5, name="johns button")
    skin = kit.plastic(SKIN, 0.3, name="keeper wax", spec=0.55)
    knuck = kit.plastic(KNUCKLE, 0.42, name="keeper knuckles", spec=0.5)
    P = {}
    root = kit.empty("keeper")
    P["root"] = root
    # the torso: local x across, local -y the belly, local z toward the head
    tor = kit.empty("keeper.torso", (0, 0, 0), root)
    kit.box("keeper.torsom", (T_W, T_D, T_L), (0, 0, 0), johns, tor, bevel=0.03)
    kit.box("keeper.placket", (0.11, 0.02, T_L * 0.92), (0, -T_D / 2 - 0.006, 0), placket, tor, bevel=0.005)
    for k in range(5):
        kit.cyl(f"keeper.button{k}", 0.018, 0.014, (0, -T_D / 2 - 0.02, T_L * (0.38 - 0.19 * k)), button, tor,
                rot=(math.pi / 2, 0, 0), n=12)
    kit.box("keeper.collar", (0.5, T_D * 1.04, 0.05), (0, 0, T_L / 2 - 0.02), placket, tor, bevel=0.01)
    # dust on the back (the side it lies on)
    kit.box("keeper.back", (T_W * 0.96, 0.01, T_L * 0.9), (0, T_D / 2 + 0.002, 0), dusty, tor)
    P["torso"] = tor
    for side in (-1, 1):
        # an arm: local -z down the arm, the knuckles on the end face
        arm = kit.empty(f"keeper.arm{side}", (0, 0, 0), root)
        kit.box(f"keeper.sleeve{side}", (LW * 0.98, LW, LIMB * 0.52), (0, 0, -LIMB * 0.26), johns, arm, bevel=0.03)
        kit.box(f"keeper.elbow{side}", (LW * 0.99, LW * 1.01, LIMB * 0.2), (0, 0, -LIMB * 0.62), dusty, arm, bevel=0.03)
        kit.box(f"keeper.cuff{side}", (LW * 1.0, LW * 1.02, 0.05), (0, 0, -LIMB * 0.745), placket, arm, bevel=0.01)
        kit.box(f"keeper.hand{side}", (LW * 0.94, LW * 0.92, LIMB * 0.22), (0, 0, -LIMB * 0.885), skin, arm, bevel=0.035)
        for k in range(4):   # four pale knuckles across the end of the hand, worn from knocking
            kit.box(f"keeper.knuckle{side}{k}", (0.068, 0.07, 0.05),
                    (LW * (-0.33 + 0.22 * k), -LW * 0.22, -LIMB + 0.005), knuck, arm, bevel=0.02)
        P[f"arm{side}"] = arm
        leg = kit.empty(f"keeper.leg{side}", (0, 0, 0), root)
        kit.box(f"keeper.legm{side}", (LW * 0.98, LW, LIMB * 0.6), (0, 0, -LIMB * 0.3), johns, leg, bevel=0.03)
        kit.box(f"keeper.knee{side}", (LW * 0.99, LW * 1.01, LIMB * 0.2), (0, 0, -LIMB * 0.7), dusty, leg, bevel=0.03)
        kit.box(f"keeper.foot{side}", (LW * 0.96, LW * 0.98, LIMB * 0.2), (0, 0, -LIMB * 0.9), skin, leg, bevel=0.035)
        P[f"leg{side}"] = leg
    neck = kit.empty("keeper.neck", (0, 0, 0), root)
    kit.box("keeper.neckm", (0.17, 0.17, 1.0), (0, 0, 0.5), skin, neck, bevel=0.03)
    P["neck"] = neck
    head = kit.empty("keeper.head", (0, 0, 0), root)
    hs = kit.empty("keeper.heads", (0, 0, 0), head)
    hs.scale = (KS * HEAD_SC,) * 3
    hm, tex = rig.head_material("keeper", SKIN)
    hm.node_tree.nodes["Principled BSDF"].inputs["Roughness"].default_value = 0.34
    # the face is drawn once (keeper_face): it never blinks and never changes
    pil = keeper_face()
    img = bpy.data.images.new("keeper face", pil.width, pil.height)
    a = np.asarray(pil.convert("RGBA")).astype(np.float32)[::-1] / 255
    img.pixels.foreach_set(a.ravel())
    img.pack()
    img.colorspace_settings.name = "sRGB"
    tex.image = img
    # the whites of its eyes hold a little light of their own, so in the dark they're the brightest thing on it
    nt = hm.node_tree
    bsdf = nt.nodes["Principled BSDF"]
    sep = nt.nodes.new("ShaderNodeRGBToBW")
    nt.links.new(tex.outputs["Color"], sep.inputs["Color"])
    ramp = nt.nodes.new("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].position = 0.80
    ramp.color_ramp.elements[0].color = (0, 0, 0, 1)
    ramp.color_ramp.elements[1].position = 0.88
    ramp.color_ramp.elements[1].color = (1.0, 0.96, 0.88, 1)
    nt.links.new(sep.outputs["Val"], ramp.inputs["Fac"])
    nt.links.new(ramp.outputs["Color"], bsdf.inputs["Emission Color"])
    bsdf.inputs["Emission Strength"].default_value = EYE_GLOW
    ctx["eye_glow"] = bsdf.inputs["Emission Strength"]
    rig.head_mesh("keeper.headm", hm, hs)
    P["head"] = head
    ctx["keeper"] = P
    ctx["keeper_parts"] = [o for o in root.children_recursive]
    return P


def keeper_face():
    """Our house style (faces.py's strokes and proportions): round white eyes with black pupils, no brows, and a
    thin dark mouth slot, slightly open onto black with nothing in it. What's wrong is that it's fixed: the eyes a
    little too wide open, the pupils pinpricks dead in the middle with no glint, the slot never moving. With no
    brows, nothing below the eyes can pass for a mouth, so when the head hangs crown down the slot is above the
    eyes and the face can only read upside down (round 1, P1). Drawn once, so it never blinks or moves."""
    from PIL import Image, ImageDraw, ImageFilter

    im = Image.new("RGB", (faces.TEX_W, faces.TEX_H), faces.hexrgb(SKIN))
    d = ImageDraw.Draw(im)
    s = faces.FX1 - faces.FX0
    ink = faces.hexrgb("#1b1210")
    th = max(12, int(0.04 * s))
    ey, ex = faces._fy(0.40), 0.22 * s
    rx = 0.128 * s
    for side in (-1, 1):
        cx = faces._fx(0.5) + side * ex
        faces._ellipse(d, cx, ey, rx, rx, fill=(250, 248, 240), outline=ink, width=th)
        faces._ellipse(d, cx, ey, rx * 0.17, rx * 0.17, fill=(10, 7, 7))
    # the mouth: a slot about 1.5 eye widths across, a little open, black inside, with square-ish ends
    cx, my = faces._fx(0.5), faces._fy(0.74)
    hw = 1.5 * rx
    pts = []
    for k in range(41):
        u = -1 + 2 * k / 40
        pts.append((cx + hw * u, my - 0.034 * s * (1 - abs(u) ** 6) ** 0.5))
    for k in range(40, -1, -1):
        u = -1 + 2 * k / 40
        pts.append((cx + hw * u, my + 0.046 * s * (1 - abs(u) ** 6) ** 0.5))
    d.polygon(pts, fill=(3, 1, 1))
    d.line(pts + [pts[0]], fill=ink, width=max(8, int(th * 0.7)), joint="curve")
    return im.filter(ImageFilter.SMOOTH)


def _limb(ob, pivot, target, across):
    """Point a limb from its pivot at a target: local -z along it, local x near `across`. The block keeps its own
    length, but may stretch up to 10% so a hand or foot lands where it's put."""
    d = V(target) - V(pivot)
    L_ = max(1e-6, d.length)
    z = -d / L_
    x = V(across) - V(across).dot(z) * z
    if x.length < 1e-4:
        x = V((1, 0, 0)) - z.x * z
    x.normalize()
    y = z.cross(x)
    ob.matrix_world = frame(x, y, z, pivot) @ Matrix.Diagonal((1, 1, min(1.1, max(0.9, L_ / LIMB)), 1))


def pose_keeper(ctx, C, u, n, hands, feet, face_to, up=(0, 0, -1), hidden=False, neck_len=0.1, hang=True,
                neck_fwd=0.0):
    """Place the keeper. C: the torso's centre; u: toward its head; n: its belly (up when it crawls on its back);
    hands, feet: [left, right] world points where they rest; face_to: the point its face looks at; up: where
    the top of its head points (down, so the face is upside down to anyone in front of it). neck_fwd moves the
    neck's end out along the belly, so a head hung crown down clears the chest (on the door)."""
    P = ctx["keeper"]
    for ob in ctx["keeper_parts"]:
        ob.hide_render = hidden
    if hidden:
        return None
    C, u, n = V(C), V(u).normalized(), V(n).normalized()
    n = (n - n.dot(u) * u).normalized()
    v = u.cross(n)
    P["torso"].matrix_world = frame(v, -n, u, C)
    for k, side in enumerate((-1, 1)):
        sh = C + u * (T_L / 2 - LW * 0.5) + v * side * (T_W / 2 + LW * 0.42) - n * 0.0
        _limb(P[f"arm{side}"], sh, hands[k], v)
        hip = C - u * (T_L / 2 - 0.02) + v * side * (T_W / 2 - LW * 0.55)
        _limb(P[f"leg{side}"], hip, feet[k], v)
    neck = C + u * (T_L / 2 - 0.03)
    base = neck + u * neck_len + n * neck_fwd   # the head's base, where the neck meets it
    F = (V(face_to) - base)
    F.normalize()
    U = V(up) - V(up).dot(F) * F
    U.normalize()
    x = (-F).cross(U)
    hc = base + U * (HH / 2) * (1.0 if hang is True else -1.0 if hang is False else float(hang))
    P["head"].matrix_world = frame(x, -F, U, hc)
    nd = base - neck
    ln = max(0.02, nd.length)
    z = nd / ln
    xx = v - v.dot(z) * z
    xx.normalize()
    P["neck"].matrix_world = frame(xx, z.cross(xx), z, neck) @ Matrix.Diagonal((1, 1, ln + 0.06, 1))
    return {"head": tuple(hc), "face": tuple(hc + F * HR), "F": tuple(F)}


def joints(C, u, n):
    """The keeper's frame (v across) and its shoulder and hip pivots, [left, right]."""
    C, u, n = V(C), V(u).normalized(), V(n).normalized()
    n = (n - n.dot(u) * u).normalized()
    v = u.cross(n)
    sh = [C + u * (T_L / 2 - LW * 0.5) + v * side * (T_W / 2 + LW * 0.42) for side in (-1, 1)]
    hp = [C - u * (T_L / 2 - 0.02) + v * side * (T_W / 2 - LW * 0.55) for side in (-1, 1)]
    return C, u, n, v, sh, hp


def reach(pivot, horiz, floor_z):
    """Where a limb from `pivot` lands on a floor at floor_z, heading out along `horiz` (flattened)."""
    h = V((horiz[0], horiz[1], 0))
    h = h.normalized() if h.length > 1e-6 else V((1, 0, 0))
    drop = V(pivot).z - floor_z
    if drop >= LIMB * 0.99:
        return V(pivot) + V((0, 0, -LIMB))
    return V(pivot) + h * math.sqrt(max(0.0, LIMB ** 2 - drop ** 2)) + V((0, 0, -drop))


def spread(u, v, side, ang):
    """A flat direction `ang` degrees out from the head direction u, to the given side."""
    a = math.radians(ang)
    return u * math.cos(a) + v * side * math.sin(a)


def crawl_pose(at, heading, face_to, height=0.44, z0=0.0, phase=None, up=(0, 0, -1), foot_floor=None,
               arm_ang=40.0, leg_ang=132.0):
    """The belly-up crab on a flat floor: torso level, belly up, head toward `heading` (degrees, 0 = -y), hands
    out at 40 degrees from the head end and heels out at 130 from it. phase (radians) steps the diagonal pairs: one
    hand and the other heel forward while the other pair is back."""
    a = math.radians(heading)
    u = V((math.sin(a), -math.cos(a), 0))
    C = V((at[0], at[1], z0 + height))
    C, u, n, v, sh, hp = joints(C, u, V((0, 0, 1)))
    hands, feet = [], []
    for k, side in enumerate((-1, 1)):
        w = 0.0 if phase is None else 14 * math.sin(phase + (0 if k == 0 else math.pi))
        hands.append(reach(sh[k], spread(u, v, side, arm_ang - w), z0))
        fd = spread(u, v, side, leg_ang - w)
        fz = z0 if foot_floor is None else foot_floor(hp[k] + fd * 0.45)
        feet.append(reach(hp[k], fd, fz))
    return {"C": C, "u": u, "n": n, "hands": hands, "feet": feet, "face_to": face_to, "up": up}


# ------------------------------------------------------------------------------------------------ the floor


def build_floor(kit, ctx, M):
    """Real boards with real gaps (one gap a hand wide), the worn pale board, the cellar door's opening."""
    boards = []
    k0, k1 = int(math.floor(X0 / BOARD)), int(math.ceil(X1 / BOARD))
    for k in range(k0, k1):
        bx0, bx1 = k * BOARD + GAP / 2, (k + 1) * BOARD - GAP / 2
        bx0, bx1 = max(bx0, X0 - 0.3), min(bx1, X1 + 0.3)
        cxm = (bx0 + bx1) / 2
        if abs(cxm - WIDE_GAP_X) < BOARD / 2:          # one board warped narrow: a gap you can see through
            bx1 -= 0.078                                # 9 cm: an eye and the face around it show (round 1)
        mat = M["floor_pale"] if abs(cxm - PALE_X) < BOARD / 2 else M["floor"]
        spans = [(Y0 - 0.3, Y1 + 0.3)]
        if TX0 - 1e-3 < cxm < TX1 + 1e-3:
            spans = [(Y0 - 0.3, TY0 - 0.006), (TY1 + 0.006, Y1 + 0.3)]
        for j, (ya, yb) in enumerate(spans):
            if abs(cxm - PALE_X) < BOARD / 2:
                ob = pale_board(kit, ctx, bx0, bx1, ya, yb, mat)
            else:
                ob = _wbox(kit, f"board{k}.{j}", (bx0, ya, -0.045), (bx1, yb, 0.0), mat)
            boards.append(ob)
    # joists under the boards, and the crawlspace's dirt
    for k in range(-6, 7):
        y = k * 0.5
        if TY0 - 0.1 < y < TY1 + 0.1:
            _wbox(kit, f"joist{k}a", (X0 - 0.3, y - 0.05, -0.27), (CX0, y + 0.05, -0.045), M["joist"])
            _wbox(kit, f"joist{k}b", (CX1, y - 0.05, -0.27), (X1 + 0.3, y + 0.05, -0.045), M["joist"])
        else:
            _wbox(kit, f"joist{k}", (X0 - 0.3, y - 0.05, -0.27), (X1 + 0.3, y + 0.05, -0.045), M["joist"])
    _wbox(kit, "crawl dirt", (X0 - 0.5, Y0 - 0.5, CRAWL - 0.1), (X1 + 0.5, Y1 + 0.5, CRAWL), M["dirt"])
    ctx["boards"] = boards


def pale_board(kit, ctx, bx0, bx1, ya, yb, mat):
    """The board worn pale and dished in the middle from years of knuckles: a real dip in its top."""
    nx, ny = 6, 40
    verts, fcs = [], []
    ym = (TY0 + TY1) / 2
    for j in range(ny + 1):
        y = ya + (yb - ya) * j / ny
        for i in range(nx + 1):
            x = bx0 + (bx1 - bx0) * i / nx
            ux = (i / nx - 0.5) * 2
            dip = 0.012 * (1 - ux * ux) * math.exp(-((y - ym) / 0.32) ** 2)
            verts.append((x, y, -dip))
    for j in range(ny):
        for i in range(nx):
            a = j * (nx + 1) + i
            fcs.append((a, a + 1, a + nx + 2, a + nx + 1))
    top = kit.mesh_obj("pale board", verts, fcs, mat, smooth=True)
    base = _wbox(kit, "pale board base", (bx0, ya, -0.045), (bx1, yb, -0.004), kit.MATS["floor planks"])
    base.parent = top
    ctx["pale"] = top
    return top


# ------------------------------------------------------------------------------------------------ the cellar


def build_cellar(kit, ctx, M):
    """The opening's frame, the stone steps down toward the back, stone walls, the trapdoor and its bolt."""
    run = -CELLAR_Z / math.tan(math.radians(STAIR_ANGLE))
    nst = 12
    rise, tread = -CELLAR_Z / nst, run / nst
    for k in range(nst):
        z_top = -k * rise - rise          # each step's top
        y0 = TY0 + k * tread
        _wbox(kit, f"step{k}", (CX0 + 0.08, y0, CELLAR_Z - 0.1), (CX1 - 0.08, y0 + tread + 0.02, z_top + 0.0),
              M["step"])
    _wbox(kit, "cellar floor", (CX0 - 0.3, TY0 - 0.3, CELLAR_Z - 0.2), (CX1 + 0.3, CY1 + 0.3, CELLAR_Z), M["cellar"])
    _wbox(kit, "cellar wall L", (CX0 - 0.25, TY0 - 0.25, CELLAR_Z), (CX0, CY1 + 0.25, -0.045), M["stone"])
    _wbox(kit, "cellar wall R", (CX1, TY0 - 0.25, CELLAR_Z), (CX1 + 0.25, CY1 + 0.25, -0.045), M["stone"])
    _wbox(kit, "cellar wall F", (CX0, TY0 - 0.25, CELLAR_Z), (CX1, TY0, -0.045), M["stone"])
    _wbox(kit, "cellar wall B", (CX0, CY1, CELLAR_Z), (CX1, CY1 + 0.25, -0.045), M["stone"])
    # the cellar's ceiling (the floor above's underside, beyond the opening) is the boards and joists already
    # the frame round the opening: a dark header board each side
    _wbox(kit, "frame F", (TX0 - 0.05, TY0 - 0.08, -0.2), (TX1 + 0.05, TY0, -0.045), M["joist"])
    _wbox(kit, "frame B", (TX0 - 0.05, TY1, -0.2), (TX1 + 0.05, TY1 + 0.08, -0.045), M["joist"])
    # the trapdoor: thick planks across a hinge at its back edge (y = TY1); its local origin is on the hinge line
    hinge = kit.empty("trap hinge", (TXM, TY1, 0.0))
    W_, D_ = TX1 - TX0 - 0.01, TY1 - TY0 - 0.01
    for k in range(int(round(W_ / 0.19))):
        x0 = -W_ / 2 + k * (W_ / round(W_ / 0.19))
        x1 = x0 + W_ / round(W_ / 0.19) - 0.008
        ob = _wbox(kit, f"trap plank{k}", (TXM + x0, TY1 - D_, -0.06), (TXM + x1, TY1, -0.003), M["trap"])
        ob.parent = hinge
        ob.location = (-TXM, -TY1, 0)
    for side in (-1, 1):   # iron strap hinges on top
        kit.box(f"strap{side}", (0.07, D_ * 0.75, 0.012), (side * W_ * 0.32, -D_ * 0.375, 0.003), M["iron"], hinge)
        kit.cyl(f"knuckle{side}", 0.022, 0.12, (side * W_ * 0.32, 0.0, 0.0), M["iron"], hinge, rot=(0, math.pi / 2, 0))
    # battens underneath, and the bolt: a bar in two keepers on the underside, by the front edge
    for side in (-1, 1):
        kit.box(f"batten{side}", (0.12, D_ * 0.94, 0.05), (side * W_ * 0.3, -D_ / 2, -0.085), M["joist"], hinge)
    ring = kit.empty("ring", (0.0, -D_ + 0.12, 0.004), hinge)
    _torus(kit, "ring pull", 0.055, 0.009, (0, 0, 0.0), M["iron"], ring)
    kit.box("ring plate", (0.08, 0.05, 0.008), (0, 0.06, 0.0), M["iron"], ring)
    kit.box("bolt keeperA", (0.06, 0.06, 0.05), (0.1, -D_ + 0.07, -0.085), M["iron"], hinge)
    kit.box("bolt keeperB", (0.06, 0.06, 0.05), (0.32, -D_ + 0.07, -0.085), M["iron"], hinge)
    bolt = kit.empty("bolt", (0.0, -D_ + 0.07, -0.085), hinge)
    kit.box("bolt bar", (0.42, 0.032, 0.032), (0.21, 0, 0), M["bolt"], bolt, bevel=0.008)
    kit.box("bolt knob", (0.035, 0.035, 0.07), (0.2, 0, -0.04), M["bolt"], bolt, bevel=0.01)
    # the catch the bolt shoots into, on the floor's frame (cellar side)
    _wbox(kit, "bolt catch", (TXM - 0.16, TY0 - 0.07, -0.16), (TXM - 0.04, TY0 - 0.01, -0.1), M["iron"])
    ctx["trap"] = hinge
    ctx["bolt"] = bolt


def _torus(kit, name, R, r, loc, mat, parent, n=28, m_=10):
    verts, fcs = [], []
    for i in range(n):
        a = 2 * math.pi * i / n
        for j in range(m_):
            b = 2 * math.pi * j / m_
            verts.append(((R + r * math.cos(b)) * math.cos(a), (R + r * math.cos(b)) * math.sin(a), r * math.sin(b)))
    for i in range(n):
        for j in range(m_):
            a0, a1 = i * m_ + j, ((i + 1) % n) * m_ + j
            fcs.append((a0, a1, ((i + 1) % n) * m_ + (j + 1) % m_, i * m_ + (j + 1) % m_))
    return kit.mesh_obj(name, verts, fcs, mat, parent, loc, smooth=True)


# ------------------------------------------------------------------------------------------------ the bulb


def build_bulb(kit, ctx, M):
    """One bare tungsten bulb on a cord from the beam: a pendulum the knocks swing. It never flickers."""
    piv = kit.empty("bulb pivot", CORD_TOP)
    L_ = CORD_TOP[2] - BULB[2]
    kit.cyl("cord", 0.005, L_, (0, 0, -L_ / 2), M["cord"], piv, n=8)
    kit.cyl("socket", 0.022, 0.06, (0, 0, -L_ + 0.02), M["socket"], piv, n=16)
    b = kit.sphere("bulb glass", 0.042, (0, 0, -L_ - 0.045), M["bulb"], piv, seg=16)
    b.visible_shadow = False
    kit.light("bulb", "POINT", (0, 0, -L_ - 0.045), BULB_W, "#ffd2a2", size=0.025, parent=piv)
    ctx["bulb"] = piv


def materials(kit):
    M = {
        "floor": kit.planks("#b07a43", "#6f4626", 1.0, "Y", name="floor planks", rough=0.62),
        "floor_pale": kit.planks("#dcc09a", "#bf9c6e", 1.0, "Y", name="floor pale", rough=0.72),
        "joist": kit.planks("#4a3220", "#2e1f14", 0.6, "Y", name="joist wood", rough=0.85),
        "trap": kit.planks("#8c5a30", "#57361c", 1.0, "X", name="trap planks", rough=0.7),
        "dirt": kit.grime("#2a2119", 0.6, 3.0, name="crawl dirt", rough=0.95),
        "step": kit.grime("#6a6257", 0.62, 4.0, name="stone step", rough=0.9),
        "stone": kit.cobbles("#4a453e", "#6b645a", "#1c1a17", 2.2, 0.0, name="cellar stone"),
        "cellar": kit.grime("#211c17", 0.6, 2.0, name="cellar floor", rough=0.95),
        "iron": kit.metal("#2b2724", 0.6, name="black iron"),
        "bolt": kit.metal("#8f877c", 0.38, name="bolt iron"),
        "cord": kit.plastic("#1d1712", 0.6, name="cord"),
        "socket": kit.metal("#8a7a5a", 0.35, name="brass socket"),
        "bulb": kit.emit("#ffd9a0", 40.0, name="bulb filament"),
        # the room: board-and-batten walls in old cream paint, a dark board ceiling and beams
        "wall": kit.planks("#c4ab7c", "#9c855c", 0.5, "Z", name="wall boards", rough=0.8),
        "batten": kit.planks("#a68e63", "#82704c", 0.6, "Z", name="battens", rough=0.8),
        "ceil": kit.planks("#5e4129", "#3e2b1b", 0.6, "X", name="ceiling boards", rough=0.85),
        "beam": kit.planks("#4a3220", "#2b1d12", 0.4, "X", name="beam wood", rough=0.85),
        "trim": kit.planks("#7a5a38", "#5a4128", 0.8, "Z", name="trim wood", rough=0.7),
        "castiron": kit.grime("#1f1d1c", 0.7, 6.0, name="cast iron", rough=0.55),
        "fire": kit.emit("#ff7a2a", 6.0, name="fire glow"),
        "oil": kit.checker("#9e2f2a", "#e6dcc6", 14.0, name="oilcloth", rough=0.35),
        "enamel": kit.plastic("#e8e4d8", 0.25, name="enamel"),
        "enamel_in": kit.plastic("#9a978c", 0.3, name="enamel basin"),
        "brass": kit.metal("#b38a4a", 0.32, name="brass"),
        "chrome": kit.metal("#c9ccce", 0.2, name="tap chrome"),
        "phone": kit.planks("#6a4424", "#4a2e18", 1.5, "Z", name="phone oak", rough=0.5),
        "bell": kit.metal("#d6d2c8", 0.25, name="phone bells"),
        "black": kit.plastic("#121010", 0.5, name="bakelite"),
        "clockface": kit.plastic("#e9dfc5", 0.6, name="clock face"),
        "jar": kit.glass("#c7d6b8", name="jar glass"),
        "jam": kit.plastic("#5a1a1e", 0.3, name="jam"),
        "plate": kit.plastic("#efe9da", 0.3, name="plate"),
        "mug": kit.plastic("#3d5a6e", 0.35, name="mug"),
        "straw": kit.grime("#d8c48a", 0.78, 18.0, name="straw", rough=0.85),
        "hatband": kit.plastic("#5a3a22", 0.6, name="hat band"),
        "window": kit.glass("#9fb0d8", name="window glass"),
        # outside
        "siding": kit.planks("#b8ad94", "#8f8670", 0.45, "X", name="siding", rough=0.85),
        "roof": kit.grime("#3a3532", 0.6, 1.5, name="roof tin", rough=0.6),
        "found": kit.concrete("#6d665c", 2.0, 0.5, name="foundation", rough=0.9),
        "porch": kit.planks("#8a7354", "#5f4e38", 1.0, "X", name="porch boards", rough=0.8),
        "dust": kit.grime("#8a7556", 0.72, 0.9, name="yard dust", rough=0.95),
        "rail": kit.planks("#6e6250", "#4c4436", 0.5, "X", name="fence rails", rough=0.9),
        "truck": kit.plastic("#5e6b45", 0.45, name="truck paint"),
        "tyre": kit.plastic("#121212", 0.8, name="tyre"),
        "tail": kit.emit("#ff2a1c", 45.0, name="tail light"),
        "head": kit.emit("#fff0d0", 14.0, name="head light"),
        "moon": kit.emit("#dfe6ff", 6.0, name="moon"),
        "warmwin": kit.emit("#ffc878", 2.5, name="window warm"),
        "darkwin": kit.plastic("#141824", 0.1, name="window dark"),
        "rake": kit.planks("#9a7a50", "#6e5536", 2.0, "Z", name="rake handle", rough=0.7),
    }
    M["grass"] = _mixed(kit, "dry grass", "#b59a62", "#7d6a42", 0.5, 3.0, 0.9)
    M["trail"] = _mixed(kit, "trail dust", "#45372a", "#3c3026", 0.3, 1.5, 0.8)   # pushed smooth: darker, a sheen
    M["frost"] = frosted_glass(kit)
    return M


def frosted_glass(kit):
    """The front door's pane: frosted, so it glows the night's indigo and shows only a soft shadow behind it."""
    m = kit._new("frosted glass")
    nt = m.node_tree
    N, L = nt.nodes, nt.links
    out = next(n for n in N if n.type == "OUTPUT_MATERIAL")
    N.remove(N["Principled BSDF"])
    tr = N.new("ShaderNodeBsdfTranslucent")
    tr.inputs["Color"].default_value = kit.col("#aeb4cf")
    gl = N.new("ShaderNodeBsdfGlossy")
    gl.inputs["Roughness"].default_value = 0.25
    mx = N.new("ShaderNodeMixShader")
    mx.inputs[0].default_value = 0.12
    L.new(tr.outputs[0], mx.inputs[1])
    L.new(gl.outputs[0], mx.inputs[2])
    kit._fogged(m, mx.outputs[0])
    return m


def wall(kit, name, axis, at, lo, hi, holes, mat_in, mat_out, t_in=0.03, t_out=0.09, outward=-1):
    """A wall in the plane axis = at (axis "x" or "y"), from lo to hi along the other axis and 0 to CEIL+0.5, with
    rectangular holes [(a0, a1, z0, z1)]: an inner layer of boards and an outer layer of siding."""
    def piece(a0, a1, z0, z1, k):
        for layer, (mat, d0, d1) in enumerate(((mat_in, 0.0, t_in), (mat_out, t_in, t_in + t_out))):
            if mat is None:
                continue
            c0, c1 = at + outward * d0, at + outward * d1
            c0, c1 = min(c0, c1), max(c0, c1)
            if axis == "x":
                _wbox(kit, f"{name}{k}.{layer}", (c0, a0, z0), (c1, a1, z1), mat)
            else:
                _wbox(kit, f"{name}{k}.{layer}", (a0, c0, z0), (a1, c1, z1), mat)
    top = CEIL + 0.05
    if not holes:
        piece(lo, hi, YARD_Z if mat_out else 0.0, top, 0)
        return
    (h0, h1, z0, z1), = holes
    piece(lo, h0, 0.0, top, 0)
    piece(h1, hi, 0.0, top, 1)
    piece(h0, h1, 0.0, z0, 2) if z0 > 0 else None
    piece(h0, h1, z1, top, 3)


def build_room(kit, ctx, M):
    wall(kit, "wallL", "x", X0, Y0 - 0.12, Y1 + 0.12, [(WIN_Y - WIN_W / 2, WIN_Y + WIN_W / 2, 1.0, 1.9)],
         M["wall"], M["siding"], outward=-1)
    wall(kit, "wallF", "y", Y0, X0 - 0.12, X1 + 0.12, [(DOOR_X - DOOR_W / 2, DOOR_X + DOOR_W / 2, 0.0, DOOR_H)],
         M["wall"], M["siding"], outward=-1)
    wall(kit, "wallB", "y", Y1, X0 - 0.12, X1 + 0.12, [], M["wall"], M["siding"], outward=1)
    wall(kit, "wallR", "x", X1, Y0 - 0.12, Y1 + 0.12, [], M["wall"], None, outward=1)
    # battens over the board joints, inside
    for k in range(-6, 7):
        y = k * 0.5
        if not (WIN_Y - WIN_W / 2 - 0.05 < y < WIN_Y + WIN_W / 2 + 0.05):
            _wbox(kit, f"battenL{k}", (X0, y - 0.03, 0.0), (X0 + 0.02, y + 0.03, CEIL), M["batten"])
        _wbox(kit, f"battenB{k}", (y - 0.03, Y1 - 0.02, 0.0), (y + 0.03, Y1, CEIL), M["batten"])
        x = k * 0.5
        if not (DOOR_X - DOOR_W / 2 - 0.12 < x < DOOR_X + DOOR_W / 2 + 0.12):
            _wbox(kit, f"battenF{k}", (x - 0.03, Y0, 0.0), (x + 0.03, Y0 + 0.02, CEIL), M["batten"])
        _wbox(kit, f"battenR{k}", (X1 - 0.02, y - 0.03, 0.0), (X1, y + 0.03, CEIL), M["batten"])
    for nm, lo, hi in (("baseL", (X0, Y0, 0), (X0 + 0.025, Y1, 0.12)), ("baseB", (X0, Y1 - 0.025, 0), (X1, Y1, 0.12)),
                       ("baseR", (X1 - 0.025, Y0, 0), (X1, Y1, 0.12))):
        _wbox(kit, nm, lo, hi, M["trim"])
    # the low ceiling and its beams across the room
    _wbox(kit, "ceiling", (X0 - 0.12, Y0 - 0.12, CEIL), (X1 + 0.12, Y1 + 0.12, CEIL + 0.04), M["ceil"])
    for k, y in enumerate((-2.4, -0.9, 0.6, 2.1)):
        _wbox(kit, f"beam{k}", (X0, y - 0.08, CEIL - 0.2), (X1, y + 0.08, CEIL), M["beam"])
    # the door to the rest of the house, shut (right wall)
    _wbox(kit, "inner door", (X1 - 0.04, -0.2, 0.0), (X1 - 0.01, 0.65, 2.0), M["trap"])
    _wbox(kit, "inner frame", (X1 - 0.05, -0.27, 0.0), (X1 - 0.02, 0.72, 2.07), M["trim"])
    kit.sphere("inner knob", 0.03, (X1 - 0.07, 0.55, 1.0), M["brass"])
    # the window over the sink: frame, glass, a cross of muntins
    wx = X0 - 0.06
    for nm, lo, hi in (("winsill", (X0 - 0.12, WIN_Y - 0.56, 0.95), (X0 + 0.08, WIN_Y + 0.56, 1.0)),
                       ("winhead", (X0 - 0.12, WIN_Y - 0.56, 1.9), (X0 + 0.03, WIN_Y + 0.56, 1.96)),
                       ("winL", (X0 - 0.12, WIN_Y - 0.56, 1.0), (X0 + 0.03, WIN_Y - 0.5, 1.9)),
                       ("winR", (X0 - 0.12, WIN_Y + 0.5, 1.0), (X0 + 0.03, WIN_Y + 0.56, 1.9)),
                       ("munV", (wx - 0.015, WIN_Y - 0.015, 1.0), (wx + 0.015, WIN_Y + 0.015, 1.9)),
                       ("munH", (wx - 0.015, WIN_Y - 0.5, 1.435), (wx + 0.015, WIN_Y + 0.5, 1.465))):
        _wbox(kit, nm, lo, hi, M["trim"])
    _wbox(kit, "winglass", (wx - 0.004, WIN_Y - 0.5, 1.0), (wx + 0.004, WIN_Y + 0.5, 1.9), M["window"])


def build_props(kit, ctx, M):
    # the cast-iron stove against the left wall, its pipe up through the ceiling, a glow at the firebox door
    sx, sy = STOVE
    _wbox(kit, "stove", (sx - 0.32, sy - 0.38, 0.14), (sx + 0.32, sy + 0.38, 0.82), M["castiron"])
    _wbox(kit, "stove top", (sx - 0.35, sy - 0.41, 0.82), (sx + 0.35, sy + 0.41, 0.86), M["castiron"])
    for kx in (-1, 1):
        for ky in (-1, 1):
            _wbox(kit, f"stove leg{kx}{ky}", (sx + kx * 0.28 - 0.03, sy + ky * 0.34 - 0.03, 0.0),
                  (sx + kx * 0.28 + 0.03, sy + ky * 0.34 + 0.03, 0.15), M["castiron"])
    for k, oy in enumerate((-0.18, 0.18)):
        kit.cyl(f"stove lid{k}", 0.11, 0.012, (sx + 0.02, sy + oy, 0.866), M["iron"], n=20)
    _wbox(kit, "firebox", (sx + 0.32, sy - 0.2, 0.3), (sx + 0.34, sy + 0.2, 0.62), M["iron"])
    for k in range(4):
        _wbox(kit, f"fire slit{k}", (sx + 0.34, sy - 0.15 + k * 0.1, 0.36), (sx + 0.345, sy - 0.12 + k * 0.1, 0.42),
              M["fire"])
    kit.cyl("stovepipe", 0.075, CEIL - 0.86, (sx - 0.1, sy + 0.1, (CEIL + 0.86) / 2), M["castiron"], n=18)
    # the table with its oilcloth (long side along y), Ray's chair beside the pale board, mine at the far end
    tx, ty = TABLE
    _wbox(kit, "tabletop", (tx - 0.43, ty - 0.75, 0.72), (tx + 0.43, ty + 0.75, 0.76), M["oil"])
    _wbox(kit, "table apron", (tx - 0.38, ty - 0.7, 0.62), (tx + 0.38, ty + 0.7, 0.72), M["trim"])
    for kx in (-1, 1):
        for ky in (-1, 1):
            _wbox(kit, f"table leg{kx}{ky}", (tx + kx * 0.34 - 0.035, ty + ky * 0.66 - 0.035, 0.0),
                  (tx + kx * 0.34 + 0.035, ty + ky * 0.66 + 0.035, 0.72), M["trim"])
    for k, (cx, cy, fx, fy) in enumerate(CHAIRS):
        _wbox(kit, f"chair seat{k}", (cx - 0.21, cy - 0.21, 0.43), (cx + 0.21, cy + 0.21, 0.47), M["trim"])
        for kx in (-1, 1):
            for ky in (-1, 1):
                _wbox(kit, f"chair leg{k}{kx}{ky}", (cx + kx * 0.18 - 0.02, cy + ky * 0.18 - 0.02, 0.0),
                      (cx + kx * 0.18 + 0.02, cy + ky * 0.18 + 0.02, 0.43), M["trim"])
        bx, by = cx - fx * 0.19, cy - fy * 0.19
        px_, py_ = -fy, fx
        for s_ in (-1, 1):
            qx, qy = bx + px_ * s_ * 0.18, by + py_ * s_ * 0.18
            _wbox(kit, f"chair post{k}{s_}", (qx - 0.02, qy - 0.02, 0.47), (qx + 0.02, qy + 0.02, 0.98), M["trim"])
        for kz in (0.62, 0.78, 0.94):
            lo = (bx - abs(px_) * 0.18 - 0.015 * abs(fx), by - abs(py_) * 0.18 - 0.015 * abs(fy), kz - 0.03)
            hi = (bx + abs(px_) * 0.18 + 0.015 * abs(fx), by + abs(py_) * 0.18 + 0.015 * abs(fy), kz + 0.03)
            _wbox(kit, f"chair rail{k}{kz}", lo, hi, M["trim"])
    sup = []
    for k, (ox, oy) in enumerate(((0.22, -0.2), (0.0, 0.5))):
        sup.append(kit.cyl(f"plate{k}", 0.12, 0.015, (tx + ox, ty + oy, 0.768), M["plate"], n=24))
        sup.append(kit.cyl(f"mug{k}", 0.04, 0.09, (tx + ox - 0.2, ty + oy + 0.12, 0.805), M["mug"], n=14))
    ctx["supper"] = sup
    # the sink cabinet under the window, an enamel basin and a tap
    _wbox(kit, "sink cab", (X0, WIN_Y - 0.75, 0.0), (X0 + 0.58, WIN_Y + 0.75, 0.86), M["trim"])
    _wbox(kit, "counter", (X0, WIN_Y - 0.78, 0.86), (X0 + 0.62, WIN_Y + 0.78, 0.9), M["phone"])
    _wbox(kit, "basin", (X0 + 0.08, WIN_Y - 0.3, 0.84), (X0 + 0.5, WIN_Y + 0.3, 0.93), M["enamel"])
    _wbox(kit, "basin in", (X0 + 0.12, WIN_Y - 0.26, 0.89), (X0 + 0.46, WIN_Y + 0.26, 0.935), M["enamel_in"])
    kit.cyl("tap", 0.015, 0.22, (X0 + 0.06, WIN_Y, 1.02), M["chrome"], n=10)
    _wbox(kit, "tap spout", (X0 + 0.06, WIN_Y - 0.012, 1.11), (X0 + 0.2, WIN_Y + 0.012, 1.13), M["chrome"])
    # the hand-crank wall phone by the door (no dial, no screen), the coat pegs, the clock (hands only)
    px = 0.35
    _wbox(kit, "phone box", (px - 0.13, Y0, 1.25), (px + 0.13, Y0 + 0.14, 1.75), M["phone"])
    for k in (-1, 1):
        kit.sphere(f"phone bell{k}", 0.045, (px + k * 0.06, Y0 + 0.16, 1.66), M["bell"], seg=12)
    kit.cyl("phone mouth", 0.03, 0.08, (px, Y0 + 0.19, 1.47), M["black"], rot=(math.pi / 2, 0, 0), n=12)
    kit.cyl("phone ear", 0.025, 0.13, (px - 0.17, Y0 + 0.08, 1.5), M["black"], n=12)
    _wbox(kit, "phone crank", (px + 0.13, Y0 + 0.06, 1.5), (px + 0.2, Y0 + 0.08, 1.52), M["iron"])
    _wbox(kit, "peg rail", (-0.45, Y0, 1.68), (0.0, Y0 + 0.03, 1.76), M["trim"])
    for k in range(3):
        kit.cyl(f"peg{k}", 0.012, 0.09, (-0.38 + 0.16 * k, Y0 + 0.07, 1.72), M["trim"], rot=(math.pi / 2, 0, 0), n=8)
    hook_hat = kit.empty("hook hat", (-0.22, Y0 + 0.12, 1.66))
    straw_hat(kit, "hookhat", hook_hat, M)
    hook_hat.rotation_euler = (math.radians(-80), 0, 0)
    ctx["hook_hat"] = hook_hat
    clk = kit.empty("clock", (-0.1, Y1 - 0.03, 1.85))
    kit.cyl("clock rim", 0.2, 0.05, (0, 0, 0), M["beam"], clk, rot=(math.pi / 2, 0, 0), n=32)
    kit.cyl("clock face", 0.175, 0.052, (0, -0.002, 0), M["clockface"], clk, rot=(math.pi / 2, 0, 0), n=32)
    for k in range(12):   # tick marks, no numerals: long at twelve, three, six and nine
        a = k / 12 * 2 * math.pi
        ln = 0.035 if k % 3 == 0 else 0.018
        r_ = 0.16 - ln / 2
        kit.box(f"clock tick{k}", (0.012 if k % 3 == 0 else 0.007, 0.004, ln),
                (math.sin(a) * r_, -0.03, math.cos(a) * r_), M["black"], clk, rot=(0, a, 0))
    hands = []
    for k, (ln, w) in enumerate(((0.085, 0.026), (0.145, 0.01))):   # a short wide hour hand, a long thin minute
        h = kit.empty(f"clock hand{k}", (0, -0.03 - 0.006 * k, 0), clk)
        kit.box(f"clock handm{k}", (w, 0.006, ln), (0, 0, ln / 2 - 0.02), M["black"], h)
        hands.append(h)
    kit.cyl("clock hub", 0.016, 0.02, (0, -0.045, 0), M["brass"], clk, rot=(math.pi / 2, 0, 0), n=14)
    ctx["clock"] = hands
    # shelves on the back wall with jars
    for k, z in enumerate((1.35, 1.75)):
        _wbox(kit, f"shelf{k}", (1.0, Y1 - 0.25, z - 0.025), (2.3, Y1, z), M["trim"])
        for j in range(5):
            x = 1.12 + j * 0.25
            kit.cyl(f"jar{k}{j}", 0.055, 0.17, (x, Y1 - 0.12, z + 0.085), M["jar"], n=14)
            kit.cyl(f"jam{k}{j}", 0.048, 0.1 + 0.03 * ((j + k) % 3), (x, Y1 - 0.12, z + 0.06), M["jam"], n=12)


def straw_hat(kit, name, parent, M):
    """Ray's pale straw fedora (the same shape rig.py gives him), loose: on the peg, or falling off."""
    R = faces.HEAD_R * KS * 1.2
    kit.cyl(f"{name} brim", R + 0.16, 0.025, (0, 0, 0), M["straw"], parent, n=32)
    kit.cyl(f"{name} crown", R + 0.02, 0.19, (0, 0, 0.1), M["straw"], parent, n=32, r2=R - 0.02)
    kit.cyl(f"{name} band", R + 0.025, 0.04, (0, 0, 0.035), M["hatband"], parent, n=32)


def build_door(kit, ctx, M):
    """The front door: planks, frosted glass in the upper half, a brass knob. Behind the glass, outside, the
    visitor's one soft shadow card, and the night's light that makes the pane glow."""
    x0, x1 = DOOR_X - DOOR_W / 2, DOOR_X + DOOR_W / 2
    y = Y0 + 0.02
    for nm, lo, hi in (("doorL", (x0 - 0.08, Y0 - 0.12, 0.0), (x0, Y0 + 0.03, DOOR_H + 0.08)),
                       ("doorR", (x1, Y0 - 0.12, 0.0), (x1 + 0.08, Y0 + 0.03, DOOR_H + 0.08)),
                       ("doorT", (x0 - 0.08, Y0 - 0.12, DOOR_H), (x1 + 0.08, Y0 + 0.03, DOOR_H + 0.1))):
        _wbox(kit, nm, lo, hi, M["trim"])
    gx0, gx1, gz0, gz1 = x0 + 0.12, x1 - 0.12, 1.12, 1.9
    leaf = []
    leaf.append(_wbox(kit, "door low", (x0, Y0 - 0.05, 0.0), (x1, Y0 - 0.01, gz0), M["trap"]))
    leaf.append(_wbox(kit, "door top", (x0, Y0 - 0.05, gz1), (x1, Y0 - 0.01, DOOR_H), M["trap"]))
    leaf.append(_wbox(kit, "door stileL", (x0, Y0 - 0.05, gz0), (gx0, Y0 - 0.01, gz1), M["trap"]))
    leaf.append(_wbox(kit, "door stileR", (gx1, Y0 - 0.05, gz0), (x1, Y0 - 0.01, gz1), M["trap"]))
    _wbox(kit, "door glass", (gx0, Y0 - 0.033, gz0), (gx1, Y0 - 0.027, gz1), M["frost"])
    _wbox(kit, "door rail", (x0 + 0.06, Y0 - 0.008, 0.45), (x1 - 0.06, Y0, 0.55), M["trim"])
    kit.sphere("door knob", 0.032, (x1 - 0.09, Y0 + 0.02, 1.0), M["brass"], seg=14)
    kit.cyl("door rose", 0.04, 0.012, (x1 - 0.09, Y0 + 0.006, 1.0), M["brass"], rot=(math.pi / 2, 0, 0), n=14)
    # the visitor: one soft, edgeless dark smear on a card outside the glass. It has no edges at all
    from PIL import Image, ImageDraw, ImageFilter
    im = Image.new("L", (256, 384), 0)
    d = ImageDraw.Draw(im)
    d.ellipse([46, 30, 210, 360], fill=255)
    d.ellipse([20, 150, 236, 384], fill=255)
    im = im.filter(ImageFilter.GaussianBlur(34))
    rgba = Image.merge("RGBA", [Image.new("L", im.size, 4)] * 3 + [im.point(lambda v: min(255, int(v * 1.15)))])
    mat, _ = _image_mat(kit, "visitor shadow", rgba, rough=1.0)
    card = kit.empty("visitor", (DOOR_X, Y0 - 0.22, 1.3))
    pl = kit.plane("visitor card", (0.9, 1.35), (0, 0, 0), mat, card, rot=(math.pi / 2, 0, 0))
    uv = pl.data.uv_layers.new(name="UVMap")
    for poly in pl.data.polygons:
        for li, vi in zip(poly.loop_indices, poly.vertices):
            co = pl.data.vertices[vi].co
            uv.data[li].uv = (co.x / 0.9 + 0.5, co.y / 1.35 + 0.5)
    ctx["visitor"] = card
    # the night outside the door and the window: cool indigo, the only light that isn't the bulb
    kit.light("door night", "AREA", (DOOR_X + 0.15, Y0 - 1.9, 1.55), 15.0, "#8d96cc", size=0.45)
    # the porch light, outside behind the glass: off but in the shots where the visitor's shadow crosses the pane,
    # where it lights the pane from behind so the shadow reads (round 1, P6)
    kit.light("porch", "POINT", (DOOR_X + 0.05, Y0 - 1.3, 1.5), 0.0, "#ffe2b8", size=0.06)
    kit.aim(kit.LIGHTS["door night"]["obj"], (DOOR_X, Y0, 1.45))
    kit.light("window night", "AREA", (X0 - 1.6, WIN_Y, 1.6), 9.0, "#8d96cc", size=1.0)
    kit.aim(kit.LIGHTS["window night"]["obj"], (X0, WIN_Y, 1.4))


def build_outside(kit, ctx, M):
    """The porch and its three steps, the dusty yard, a split-rail fence, dry grass, the moon, Ray's truck,
    and the drag trail (the visitor's: smooth, about 1.5 m wide)."""
    px0, px1 = X0 - 0.4, 1.4
    _wbox(kit, "porch deck", (px0, PORCH_Y, -0.05), (px1, Y0 - 0.12, 0.0), M["porch"])
    _wbox(kit, "porch skirt", (px0, PORCH_Y, YARD_Z), (px1, PORCH_Y + 0.04, -0.05), M["joist"])
    for k in range(3):
        rise = -YARD_Z / 3
        z = -(k + 1) * rise + rise
        _wbox(kit, f"porch step{k}", (DOOR_X - 0.65, PORCH_Y - 0.3 * (k + 1), YARD_Z), (DOOR_X + 0.65, PORCH_Y - 0.3 * k, z - 0.0),
              M["porch"])
    for k, x in enumerate((px0 + 0.08, DOOR_X - 0.75, DOOR_X + 0.75, px1 - 0.08)):
        _wbox(kit, f"porch post{k}", (x - 0.06, PORCH_Y + 0.02, 0.0), (x + 0.06, PORCH_Y + 0.14, 2.35), M["rail"])
    _wbox(kit, "porch roof", (px0 - 0.1, PORCH_Y - 0.15, 2.35), (px1 + 0.1, Y0 - 0.12, 2.42), M["roof"])
    # the rest of the house beyond the kitchen, its roof, its foundation
    _wbox(kit, "house rest", (X1 + 0.12, Y0 - 0.12, YARD_Z), (X1 + 6.0, Y1 + 0.12, CEIL + 0.05), M["siding"])
    for k, x in enumerate((X1 + 1.6, X1 + 4.2)):
        _wbox(kit, f"rest win{k}", (x - 0.45, Y0 - 0.14, 1.0), (x + 0.45, Y0 - 0.12, 1.9), M["darkwin"])
    fx0, fx1, fy0, fy1 = X0 - 0.14, X1 + 6.02, Y0 - 0.14, Y1 + 0.14     # the foundation: walls round the crawlspace
    for nm, lo, hi in (("foundF", (fx0, fy0, YARD_Z), (fx1, fy0 + 0.14, -0.02)), ("foundB", (fx0, fy1 - 0.14, YARD_Z), (fx1, fy1, -0.02)),
                       ("foundL", (fx0, fy0, YARD_Z), (fx0 + 0.14, fy1, -0.02)), ("foundR", (fx1 - 0.14, fy0, YARD_Z), (fx1, fy1, -0.02))):
        _wbox(kit, nm, lo, hi, M["found"])
    rise = 1.9
    for side in (-1, 1):
        yc = (Y0 + Y1) / 2
        half = (Y1 - Y0) / 2 + 0.35
        ang = math.atan2(rise, half)
        L_ = math.hypot(rise, half)
        kit.box(f"roof{side}", (X1 - X0 + 6.6, L_, 0.08), (X1 + 2.65, yc + side * half / 2, CEIL + 0.05 + rise / 2),
                M["roof"], rot=(-side * ang, 0, 0))
    gable = [(X0 - 0.13, Y0 - 0.12, CEIL + 0.05), (X0 - 0.13, Y1 + 0.12, CEIL + 0.05), (X0 - 0.13, (Y0 + Y1) / 2, CEIL + 1.9)]
    kit.mesh_obj("gable", gable, [(0, 1, 2)], M["siding"])
    # the yard, the fence, the dry grass, the moon
    # the yard, with the house's footprint left open (the crawlspace and the cellar are under it)
    for nm, lo, hi in (("yardL", (-40, -50), (fx0, 30)), ("yardR", (fx1, -50), (40, 30)), ("yardF", (fx0, -50), (fx1, fy0)),
                       ("yardB", (fx0, fy1), (fx1, 30))):
        kit.plane(nm, (hi[0] - lo[0], hi[1] - lo[1]), ((lo[0] + hi[0]) / 2, (lo[1] + hi[1]) / 2, YARD_Z), M["dust"])
    for k in range(13):
        x = -13 + k * 2.4
        _wbox(kit, f"fence post{k}", (x - 0.06, -13.06, YARD_Z), (x + 0.06, -12.94, YARD_Z + 1.1), M["rail"])
    for z in (0.45, 0.85):
        _wbox(kit, f"fence rail{z}", (-13.0, -13.03, YARD_Z + z - 0.05), (15.8, -12.97, YARD_Z + z + 0.05), M["rail"])
    rng = np.random.default_rng(4)
    verts, fcs = [], []
    for _ in range(2600):
        x, y = rng.uniform(-22, 22), rng.uniform(-30, -13.6)
        h, w, a = rng.uniform(0.5, 1.15), rng.uniform(0.02, 0.05), rng.uniform(0, math.pi)
        lean = rng.uniform(-0.15, 0.15)
        dx, dy = math.cos(a) * w, math.sin(a) * w
        i = len(verts)
        verts += [(x - dx, y - dy, YARD_Z), (x + dx, y + dy, YARD_Z), (x + lean, y + lean * 0.5, YARD_Z + h)]
        fcs.append((i, i + 1, i + 2))
    kit.mesh_obj("grass", verts, fcs, M["grass"])
    kit.cyl("moon", 2.2, 0.1, (-24, -58, 21), M["moon"], rot=(math.radians(70), 0, math.radians(-20)), n=40)
    kit.light("moonlight", "SUN", (0, 0, 10), 0.35, "#8a98e8")
    kit.LIGHTS["moonlight"]["obj"].rotation_euler = (math.radians(58), 0, math.radians(200))
    kit.LIGHTS["moonlight"]["light"].angle = math.radians(1.0)
    kit.light("dawn", "SUN", (0, 0, 10), 0.0, "#ffc59a")
    kit.LIGHTS["dawn"]["obj"].rotation_euler = (math.radians(78), 0, math.radians(120))
    kit.LIGHTS["dawn"]["light"].angle = math.radians(3.0)
    # low fog lying in the yard: a few soft layers of haze, only outside
    fog = []
    for k, (z, a) in enumerate(((0.08, 0.05), (0.3, 0.035), (0.6, 0.02))):   # halved in round 1 (P6)
        im = np.zeros((128, 128, 4), np.float32)
        r = np.random.default_rng(k + 9)
        base = r.random((8, 8))
        from PIL import Image
        n = np.asarray(Image.fromarray((base * 255).astype(np.uint8)).resize((128, 128), Image.BICUBIC)) / 255.0
        im[..., :3] = 0.62
        im[..., 3] = np.clip(n * 1.4 - 0.2, 0, 1) * a
        mat, _ = _image_mat(kit, f"haze{k}", Image.fromarray((im * 255).astype(np.uint8), "RGBA"), rough=1.0)
        pl = kit.plane(f"haze{k}", (60, 60), (0, -14, YARD_Z + z), mat)
        uv = pl.data.uv_layers.new(name="UVMap")
        for poly in pl.data.polygons:
            for li, vi in zip(poly.loop_indices, poly.vertices):
                co = pl.data.vertices[vi].co
                uv.data[li].uv = (co.x / 12 + 0.5, co.y / 12 + 0.5)
        fog.append(pl)
    ctx["haze"] = fog
    # Ray's pickup: block body, no badge, red tail lights toward the house
    tr = kit.empty("truck", (TRUCK[0], TRUCK[1], YARD_Z))
    for nm, sz, c in (("bed", (1.7, 1.9, 0.55), (0, 1.0, 0.75)), ("cab", (1.7, 1.25, 0.95), (0, -0.55, 0.95)),
                      ("hood", (1.7, 1.2, 0.5), (0, -1.75, 0.72)), ("chassis", (1.6, 4.4, 0.25), (0, -0.2, 0.42))):
        kit.box(f"truck {nm}", sz, c, M["truck"], tr, bevel=0.06)
    kit.box("truck screen", (1.5, 0.05, 0.42), (0, -1.16, 1.18), M["darkwin"], tr, rot=(0.25, 0, 0))
    for k, (x, y) in enumerate(((-0.82, 1.3), (0.82, 1.3), (-0.82, -1.6), (0.82, -1.6))):
        kit.cyl(f"truck tyre{k}", 0.36, 0.28, (x, y, 0.36), M["tyre"], tr, rot=(0, math.pi / 2, 0), n=20)
    for k in (-1, 1):
        kit.box(f"truck tail{k}", (0.2, 0.04, 0.16), (k * 0.7, 1.96, 0.86), M["tail"], tr)
        kit.box(f"truck lamp{k}", (0.24, 0.04, 0.16), (k * 0.6, -2.36, 0.8), M["head"], tr)
    kit.light("tail glow", "POINT", (0, 2.3, 0.9), 0.0, "#ff2a1c", size=0.2, parent=tr)
    ctx["truck"] = tr
    # the drag trail: night two's, round the house and ending under the kitchen window; the last morning's,
    # up the porch steps to the front door. A smooth groove of pushed dust, the same 1.5 m wide each time
    ctx["trail_a"] = trail(kit, "trail a", [(-6.0, -14.0), (-5.0, -6.9), (9.6, -6.9), (X1 + 8.2, Y1 + 2.5),
                                           (X0 - 2.5, Y1 + 2.5), (X0 - 1.5, WIN_Y + 0.8), (X0 - 0.8, WIN_Y)], M["trail"])
    ctx["trail_b"] = trail(kit, "trail b", [(-3.0, -14.0), (-1.6, -8.0), (DOOR_X, PORCH_Y - 1.1)], M["trail"])
    smear = []
    for k in range(3):
        rise = -YARD_Z / 3
        z = -(k + 1) * rise + rise
        smear.append(_wbox(kit, f"smear step{k}", (DOOR_X - 0.55, PORCH_Y - 0.3 * (k + 1), z + 0.001),
                           (DOOR_X + 0.55, PORCH_Y - 0.3 * k, z + 0.004), M["trail"]))
    smear.append(_wbox(kit, "smear porch", (DOOR_X - 0.55, PORCH_Y, 0.001), (DOOR_X + 0.55, Y0 - 0.12, 0.004), M["trail"]))
    ctx["trail_b"] += smear
    # the rake Ray rakes it over with (in his hands only at L29)
    rk = kit.empty("rake")
    kit.cyl("rake handle", 0.018, 1.5, (0, 0, -0.75), M["rake"], rk, n=8)
    kit.box("rake head", (0.45, 0.04, 0.04), (0, 0, -1.5), M["iron"], rk)
    for k in range(9):
        kit.box(f"rake tine{k}", (0.012, 0.012, 0.08), (-0.2 + k * 0.05, 0.0, -1.55), M["iron"], rk)
    ctx["rake"] = rk


def trail(kit, name, pts, mat, w=1.5):
    """A smooth band along a polyline on the yard, w wide, a hair above the dust."""
    pts = [V((x, y, 0)) for x, y in pts]
    dense = []
    for a, b in zip(pts, pts[1:]):
        n = max(2, int((b - a).length / 0.4))
        dense += [a.lerp(b, i / n) for i in range(n)]
    dense.append(pts[-1])
    verts, fcs = [], []
    for i, p in enumerate(dense):
        d = (dense[min(i + 1, len(dense) - 1)] - dense[max(i - 1, 0)])
        d = V((d.x, d.y, 0)).normalized()
        nrm = V((-d.y, d.x, 0))
        for s in (-1, 1):
            q = p + nrm * s * w / 2
            verts.append((q.x, q.y, YARD_Z + 0.004))
    for i in range(len(dense) - 1):
        fcs.append((2 * i, 2 * i + 1, 2 * i + 3, 2 * i + 2))
    band = kit.mesh_obj(name, verts, fcs, mat)
    # the dust pushed up along both edges: low ridges that catch a raking dawn light and throw a thin shadow
    # into the band, so the smooth groove reads (no prints in it)
    prof = [(-0.16, 0.0), (-0.06, 0.035), (0.0, 0.006)]
    bv, bf = [], []
    for i, p in enumerate(dense):
        d = (dense[min(i + 1, len(dense) - 1)] - dense[max(i - 1, 0)])
        d = V((d.x, d.y, 0)).normalized()
        nrm = V((-d.y, d.x, 0))
        for s in (-1, 1):
            for off, h in prof:
                q = p + nrm * s * (w / 2 - off)
                bv.append((q.x, q.y, YARD_Z + h))
    m = 2 * len(prof)
    for i in range(len(dense) - 1):
        for s in range(2):
            for j in range(len(prof) - 1):
                a0 = i * m + s * len(prof) + j
                bf.append((a0, a0 + 1, a0 + 1 + m, a0 + m))
    ridge = kit.mesh_obj(name + " ridge", bv, bf, kit.MATS.get("yard dust") or mat, smooth=True)
    return [band, ridge]


def build_dust(kit, ctx, M):
    """Specks of dust that sift down through the boards when the floor knocks hard."""
    mat = kit.plastic("#b9a88a", 0.9, name="dust speck")
    rng = np.random.default_rng(3)
    specks = []
    for k in range(70):
        x = rng.uniform(-1.6, 1.4)
        y = rng.uniform(-1.6, 1.6)
        ob = kit.box(f"speck{k}", (0.008, 0.008, 0.008), (x, y, 2.3), mat)
        specks.append((ob, x, y, rng.uniform(0, 1), rng.uniform(0.7, 1.3)))
    ctx["dust"] = specks
    # round 3 (the hook): specks that kick up out of the two gaps beside the pale board, hidden until a "puff" cue
    puff = []
    for k in range(60):
        side = -1 if k % 2 else 1
        x = PALE_X + side * (BOARD / 2)
        y = rng.uniform(-0.95, 0.45)
        sz = rng.uniform(0.006, 0.013)
        ob = kit.box(f"puff{k}", (sz, sz, sz), (x, y, -1.0), mat)
        ob.hide_render = True
        puff.append((ob, x, y, rng.uniform(0, 1), rng.uniform(0.5, 1.4)))
    ctx["puff"] = puff


def build(kit, story, tl):
    ctx = {}
    M = materials(kit)
    ctx["M"] = M
    build_floor(kit, ctx, M)
    build_cellar(kit, ctx, M)
    build_bulb(kit, ctx, M)
    build_room(kit, ctx, M)
    build_props(kit, ctx, M)
    build_door(kit, ctx, M)
    build_outside(kit, ctx, M)
    build_dust(kit, ctx, M)
    build_keeper(kit, ctx)
    kit.light("fill", "AREA", (0.0, 0.0, CEIL - 0.25), FILL_W, "#ffcf9a", size=3.0)
    kit.aim(kit.LIGHTS["fill"]["obj"], (0.0, 0.0, 0.0))
    # the bulb's light coming back off the honey boards: a faint warm bounce, so the undersides aren't dead black
    kit.light("bounce", "AREA", (-0.5, -0.6, 0.03), 12.0, "#e8a868", size=3.2)
    kit.LIGHTS["bounce"]["obj"].rotation_euler = (math.pi, 0, 0)
    for nm in ("key", "key2", "under"):
        kit.light(nm, "SPOT", (0, 0, 1), 0.0, "#ffd2a0", size=0.05, spot=40, blend=0.6)
    return ctx


# ------------------------------------------------------------------------------------------------ poses

STAIR_U = V((0, -math.cos(math.radians(STAIR_ANGLE)), math.sin(math.radians(STAIR_ANGLE))))
STAIR_N = V((0, math.sin(math.radians(STAIR_ANGLE)), math.cos(math.radians(STAIR_ANGLE))))


def stair_z(y):
    """The steps' (smoothed) surface height at y, inside the cellar."""
    return -max(0.0, (y - TY0)) * math.tan(math.radians(STAIR_ANGLE))


def floor_at(p):
    """The floor under a point: the kitchen boards, or the steps inside the cellar door's opening."""
    if TX0 < p.x < TX1 and TY0 < p.y < TY1 + 1.5:
        return stair_z(p.y) - 0.05
    return 0.0


def rising_pose(neck, face_to, up=(0, -1, 0), slope=30.0, arm_ang=55.0, leg_ang=150.0, hand_z=0.0, x=TXM):
    """Coming up the steps head first and belly up. `neck` [y, z] is where its neck is; the torso lies back
    down the steps behind it at `slope` degrees. The hands reach out wide (arm_ang degrees out from straight
    ahead) and land on the kitchen floor at the opening's corners; the heels land on the steps below."""
    a = math.radians(slope)
    u = V((0, -math.cos(a), math.sin(a)))
    n = V((0, math.sin(a), math.cos(a)))
    nk = V((x, neck[0], neck[1]))
    C = nk - u * (T_L / 2 - 0.03)
    C, u, n, v, sh, hp = joints(C, u, n)
    fwd = V((0, -1, 0))
    hands, feet = [], []
    for k, side in enumerate((-1, 1)):
        hands.append(reach(sh[k], spread(fwd, v, side, arm_ang), hand_z))
        d = spread(fwd, v, side, leg_ang)
        f = reach(hp[k], d, stair_z(hp[k].y + 0.3) - 0.05)
        feet.append(f)
    return {"C": C, "u": u, "n": n, "hands": hands, "feet": feet, "face_to": face_to, "up": up}


DOOR_C = (DOOR_X, Y0 + 0.14, 0.86)          # the keeper's torso, pressed flat on the inside of the front door
DOOR_NECK = 0.3                              # on the door its neck reaches out this far so the hung head clears it
SWING_F, SWING_TAU, SWING_MAX = 0.67, 2.4, 0.72


def door_pose(face_to, climb=1.0, start=None, heading=0.0, arm=40.0, leg=132.0):
    """Pressed flat to the inside of the front door, head first (at the top), belly to the room, hands and heels
    out to the frame. Its head sits on its neck crown-down, so its face is upside down to the room. climb 0..1
    blends from crawling on the floor at the foot of the door to flat on it. start, heading, arm and leg set that
    floor crawl (round 3, R6: clear of my boots by the stove); the defaults are round 2's."""
    C1, u1, n1 = V(DOOR_C), V((0, 0, 1)), V((0, 1, 0))
    C1, u1, n1, v1, sh, hp = joints(C1, u1, n1)
    # hands out flat on the wall past the frame's edges, a little above the shoulders (not up by its ears)
    hands1 = [V((DOOR_X + side * 1.5, Y0 + 0.05, 1.32)) for side in (-1, 1)]
    feet1 = [V((DOOR_X + side * 0.98, Y0 + 0.05, 0.12)) for side in (-1, 1)]
    # its head hangs back off the top of its neck, chin up and crown down, out in front of its chest
    if climb >= 0.999:
        return {"C": C1, "u": u1, "n": n1, "hands": hands1, "feet": feet1, "face_to": face_to, "up": (0, 0, -1),
                "hang": 1.0, "neck_fwd": DOOR_NECK}
    p0 = crawl_pose(tuple(start) if start else (DOOR_X, Y0 + 1.0), heading, face_to, foot_floor=floor_at,
                    arm_ang=arm, leg_ang=leg)
    c = _ss(climb)
    u = p0["u"].lerp(u1, c).normalized()
    n = p0["n"].lerp(n1, c).normalized()
    return {"C": p0["C"].lerp(C1, c), "u": u, "n": n,
            "hands": [a.lerp(b, c) for a, b in zip(p0["hands"], hands1)],
            "feet": [a.lerp(b, c) for a, b in zip(p0["feet"], feet1)],
            "face_to": face_to, "up": (0, 0, -1), "hang": 1.0, "neck_fwd": DOOR_NECK * c}


def under_pose(head_at, face_to=None, heading=0.0, phase=None):
    """Lying flat on its back in the crawlspace, head first, face up at the boards. head_at is where its head is."""
    a = math.radians(heading)
    u = V((math.sin(a), -math.cos(a), 0))
    hc = V(head_at)
    C = hc - u * (T_L / 2 - 0.03 + 0.1 + HH / 2)
    p = crawl_pose((C.x, C.y), heading, face_to or (hc.x, hc.y, 2.0), height=hc.z - CRAWL, z0=CRAWL, phase=phase,
                   up=tuple(u), arm_ang=62, leg_ang=118)
    p["hang"] = 1.0
    return p


GLIDE = ("where", "heading", "height", "neck", "slope", "arm", "leg", "hand_z", "climb", "head_at", "lift", "x")


def _lerp(a, b, u):
    if isinstance(a, (list, tuple)):
        return [x + (y - x) * u for x, y in zip(a, b)]
    return a + (b - a) * u


def keeper_key(tl, t):
    """The keeper's pose parameters at t: the last "keeper" cue, gliding steadily toward the next one if that one
    says "glide" (the same pace the whole way: it never jumps or speeds up)."""
    ks = _cues(tl, "keeper")
    if not ks:
        return {"pose": "hidden"}
    cur = None
    for i, k in enumerate(ks):
        if k["t"] <= t + 1e-9:
            cur = i
    if cur is None:
        return {"pose": "hidden"}
    k = dict(ks[cur])
    nxt = ks[cur + 1] if cur + 1 < len(ks) else None
    if nxt and nxt.get("glide") and nxt.get("pose") == k.get("pose"):
        u = (t - k["t"]) / max(1e-6, nxt["t"] - k["t"])
        for f in GLIDE:
            if f in k and f in nxt:
                k[f] = _lerp(k[f], nxt[f], u)
        if "where" in ks[cur] and "where" in nxt:
            d = math.hypot(k["where"][0] - ks[cur]["where"][0], k["where"][1] - ks[cur]["where"][1])
            k["phase"] = k.get("phase0", 0.0) + d / 0.32 * math.pi
        if "head_at" in ks[cur] and "head_at" in nxt:
            d = (V(k["head_at"]) - V(ks[cur]["head_at"])).length
            k["phase"] = d / 0.32 * math.pi
    return k


def cam_now(story, tl, t):
    import __main__

    shot = _shot(tl, t)
    spec = next(s for s in story["shots"] if s["id"] == shot["id"])
    if hasattr(__main__, "cam_at"):
        return V(__main__.cam_at(spec, shot, t, None, tl)[0])
    return V(spec["cam"][0][1])


def person_head(tl, who, t):
    from blocky import acting

    s = acting.state(tl, who, t)
    keys = tl["acting"].get(who, [])
    z = 1.5
    if _switch(keys, "sit", t, False):
        z = 1.22
    if _switch(keys, "kneel", t, False):
        z = 1.25
    return V((s["x"], s["y"], s["z"] + z))


def place_keeper(kit, story, tl, t, ctx):
    k = keeper_key(tl, t)
    pose = k.get("pose", "hidden")
    if pose == "hidden":
        pose_keeper(ctx, (0, 0, 0), (0, 1, 0), (0, 0, 1), [], [], (0, 1, 0), hidden=True)
        return None
    f = k.get("face", "me")
    if f == "cam":
        face = cam_now(story, tl, t)
    elif f == "me":
        face = person_head(tl, "me", t)
    else:
        face = V(f)
    if pose == "crawl":
        p = crawl_pose(k["where"], k.get("heading", 0.0), face, height=k.get("height", 0.4), phase=k.get("phase"),
                       foot_floor=floor_at, arm_ang=k.get("arm", 48), leg_ang=k.get("leg", 128))
    elif pose == "rise":
        p = rising_pose(k["neck"], face, up=tuple(k.get("up", (0, -1, 0))), slope=k.get("slope", 42),
                        arm_ang=k.get("arm", -30), leg_ang=k.get("leg", 150), hand_z=k.get("hand_z", 0.16),
                        x=k.get("x", TXM))
    elif pose == "door":
        p = door_pose(face, k.get("climb", 1.0), k.get("start"), k.get("heading", 0.0), k.get("arm", 40.0),
                      k.get("leg", 132.0))
    elif pose == "under":
        p = under_pose(k["head_at"], face if f != "me" else None, k.get("heading", 0.0), k.get("phase"))
    else:
        raise ValueError(f"keeper pose {pose!r}")
    if "up" in k and pose != "rise":
        p["up"] = tuple(k["up"])
    # a hand put somewhere on purpose (the trapdoor's edge, by my boot), lifted `lift` metres for a knock
    for side, key in ((0, "hand_l"), (1, "hand_r")):
        if key in k:
            p["hands"][side] = V(k[key])
    if k.get("lift"):
        knock_hand = 1 if "hand_r" in k else 0
        p["hands"][knock_hand] = V(p["hands"][knock_hand]) + V((0, 0, k["lift"]))
    for c in _cues(tl, "keeper_knock"):     # its knuckles come down on each knock of its pattern
        for dt in c.get("pattern", [0.0]):
            x = t - (c["t"] + dt)
            if -0.16 < x < 0.06:
                side = c.get("side", 1)
                lift = 0.09 * _ss((x + 0.16) / 0.08) * (1 - _ss((x + 0.02) / 0.02)) if x < 0 else 0.0
                p["hands"][side] = V(p["hands"][side]) + V((0, 0, lift))
    hang = p.get("hang", 1.0)
    info = pose_keeper(ctx, p["C"], p["u"], p["n"], p["hands"], p["feet"], p["face_to"], p.get("up", (0, 0, -1)),
                       hang=hang, neck_fwd=p.get("neck_fwd", 0.0), neck_len=k.get("neck_len", 0.1))
    return info


def bulb_swing(tl, t):
    """The bulb on its cord: a slow idle sway, plus a damped swing from each knock from below and each "swing"
    cue. It never flickers. Clamped where the cord meets the beam."""
    ax = 0.025 * math.sin(2 * math.pi * SWING_F * t)
    ay = 0.012 * math.sin(2 * math.pi * SWING_F * 1.07 * t + 1.3)
    for c in _cues(tl, "knock_below") + _cues(tl, "swing"):
        for dt in c.get("pattern", [0.0]):
            x = t - (c["t"] + dt)
            if x < 0:
                continue
            a = c.get("amp", 0.12) * math.exp(-x / c.get("tau", SWING_TAU))
            ax += a * math.sin(2 * math.pi * SWING_F * x)
            ay += a * 0.35 * math.sin(2 * math.pi * SWING_F * 1.07 * x + 0.6)
    for c in _cues(tl, "settle"):
        if t >= c["t"]:
            g = math.exp(-(t - c["t"]) / 0.9)
            ax, ay = ax * g, ay * g
    return max(-SWING_MAX, min(SWING_MAX, ax)), max(-SWING_MAX, min(SWING_MAX, ay))


def _fog_nodes(ctx):
    if "fog_nodes" not in ctx:
        import bpy as _b

        from blocky import kit as _k

        d = _k.FOG["density"]
        ctx["fog_nodes"] = [nd for m in _b.data.materials if m.node_tree for nd in m.node_tree.nodes
                            if nd.type == "MATH" and nd.operation == "MULTIPLY" and d > 0
                            and abs(nd.inputs[1].default_value + d) < 1e-6]   # float32 sockets: 1e-9 never matched
        fc = tuple(_k.FOG["color"])
        ctx["fog_cols"] = [nd for m in _b.data.materials if m.node_tree for nd in m.node_tree.nodes
                           if nd.type == "EMISSION" and all(abs(a - b) < 1e-6 for a, b in
                                                             zip(nd.inputs["Color"].default_value[:3], fc))]
        ctx["fog_d"] = d
    return ctx["fog_nodes"]


TIMES = {   # world colour and strength, moonlight, dawn sun, the night lights at the door and window, the bulb
    "night": ("#0a0c1c", 1.0, 0.35, 0.0, 1.0, 1.0),
    "dawn": ("#a8907f", 0.75, 0.0, 4.6, 0.0, 0.55),     # a low raking sun, less sky (round 1, P6: the trails read)
    "dusk": ("#a8705a", 1.2, 0.0, 1.6, 0.0, 0.8),
    "day": ("#c9b7a4", 1.6, 0.0, 3.0, 0.0, 0.45),
}
FOG_COL = {"night": "#262b45", "dawn": "#b8a597", "dusk": "#9a7462", "day": "#c3b6a6"}   # the yard's haze


def _ease_value(cs, attr, t, default, dur_key="dur"):
    """A value that eases from one cue's setting to the next over the newer cue's dur."""
    prev, out = default, default
    for c in cs:
        if attr not in c:
            continue
        if c["t"] > t:
            break
        d = c.get(dur_key, 0.0)
        u = 1.0 if d <= 0 else _ss((t - c["t"]) / d)
        out = prev + (c[attr] - prev) * u
        prev = c[attr] if u >= 1 else out
    return out


def animate(kit, story, tl, t, ctx):
    from blocky import kit as K

    over = {}
    shot = _shot(tl, t)["id"]
    ext = shot in set(story.get("exterior_shots", []))
    # ---- fog only in the yard
    nodes = _fog_nodes(ctx)
    fg = story.get("fog_gain", {}).get(shot, 1.0)    # a high or long shot can take less of the yard's haze
    for nd in nodes:
        nd.inputs[1].default_value = -ctx["fog_d"] * fg if ext else 0.0
    for pl in ctx["haze"]:
        pl.hide_render = not ext or fg < 0.5
    tm0 = _switch(_cues(tl, "time"), "time", t, "night")
    for nd in ctx.get("fog_cols", []):
        nd.inputs["Color"].default_value = K.col(FOG_COL[tm0])
    # ---- the time of day
    tm = _switch(_cues(tl, "time"), "time", t, "night")
    sky, sky_s, moon, dawn, nights, bulb = TIMES[tm]
    w = bpy.context.scene.world.node_tree.nodes["Background"]
    w.inputs["Color"].default_value = K.col(sky)
    w.inputs["Strength"].default_value = sky_s
    over["moonlight"] = moon / 0.35 if moon else 0.0
    K.LIGHTS["dawn"]["base"] = 1.0
    over["dawn"] = dawn
    over["door night"] = nights
    over["window night"] = nights if tm == "night" else 1.2
    K.LIGHTS["window night"]["light"].color = K.col("#8d96cc" if tm == "night" else "#ffd8b0")[:3]
    over["bulb"] = bulb
    ctx["bulb_gain"] = bulb
    # ---- the bulb swings
    ax, ay = bulb_swing(tl, t)
    ctx["bulb"].rotation_euler = (ax, ay, 0.0)
    # ---- the cellar door and its bolt
    op = _ease_value(_cues(tl, "trapdoor"), "open", t, 0.0)
    ctx["trap"].rotation_euler.x = -math.radians(100.0) * op
    bo = _ease_value([{**c, "open": 1.0 if c.get("open") else 0.0} for c in _cues(tl, "bolt")], "open", t, 0.0)
    ctx["bolt"].location.x = -0.14 + 0.2 * bo
    # ---- the pale board jumps on each knock from below that says so
    # (a cue's "jump" in metres and "fall" in seconds are opt-in, for the hook's big jump in round 3)
    dz = 0.0
    for c in _cues(tl, "knock_below"):
        if not c.get("board"):
            continue
        for d in c.get("pattern", [0.0]):
            dz = max(dz, c.get("jump", 0.016) * K.bump(t, c["t"] + d, 0.025, c.get("fall", 0.09)))
    ctx["pale"].location.z = dz
    # ---- dust kicked up out of the gaps beside the pale board ("puff" cues; round 3, the hook)
    pf = [c for c in _cues(tl, "puff") if c["t"] <= t < c["t"] + c.get("dur", 1.0)]
    for ob, x, y, ph, sp in ctx["puff"]:
        if not pf:
            ob.hide_render = True
            continue
        x_ = t - pf[-1]["t"] - ph * 0.12
        ob.hide_render = x_ < 0
        if x_ >= 0:
            h = pf[-1].get("height", 0.18) * sp * (1 - math.exp(-x_ / 0.12)) - 0.12 * x_ * x_
            ob.location = (x + math.copysign(0.05 * sp * x_, x - PALE_X), y + 0.02 * math.sin(9 * ph + 5 * x_),
                           max(0.002, h))
    # ---- dust sifting down through the boards
    act = [c for c in _cues(tl, "dust") if c["t"] <= t < c["t"] + c.get("dur", 3.0) + 1.6]
    for ob, x, y, ph, sp in ctx["dust"]:
        if not act:
            ob.hide_render = True
            continue
        c = act[-1]
        u = ((t - c["t"]) * 0.75 * sp + ph) % 1.0
        ob.hide_render = (t - c["t"]) < ph * 0.6
        ob.location = (x + 0.04 * math.sin(7 * u + ph * 9), y, CEIL - 0.06 - (CEIL - 0.1) * u)
    # ---- the visitor's soft shadow on the frosted glass
    vis = ctx["visitor"]
    on = _switch(_cues(tl, "shadow"), "on", t, False)
    for ob in [vis] + list(vis.children):
        ob.hide_render = not on
    sx = _ease_value([{**c, "x": c["x"]} for c in _cues(tl, "shadow") if "x" in c], "x", t, 0.6)
    vis.location.x = DOOR_X + sx
    # ---- the truck: parked, pulling away into the fog, gone, back
    tr = ctx["truck"]
    st = _switch(_cues(tl, "truck"), "state", t, "parked")
    t_go = max([c["t"] for c in _cues(tl, "truck") if c.get("state") == "go" and c["t"] <= t] or [t])
    if st == "go":
        x = t - t_go
        tr.location.y = TRUCK[1] - (0.5 * 1.6 * x * x if x < 3 else 7.2 + 4.8 * (x - 3))
    elif st == "gone":
        tr.location.y = -400
    else:
        tr.location.y = TRUCK[1]
    over["tail glow"] = 1.0 if (st == "go" and tm == "night") else 0.0
    K.LIGHTS["tail glow"]["base"] = 6.0
    # ---- Ray's hat: on his head, on the peg, or knocked off by his laugh
    hat = _switch(_cues(tl, "hat"), "on", t, "ray")
    ray_hat = [bpy.data.objects.get(f"ray.{p}") for p in ("brim", "crown", "band")]
    ray = bpy.data.objects.get("ray")
    for ob in ray_hat:
        if ob is not None and ray is not None and not ray.hide_render:
            ob.hide_render = hat != "ray"
    hh = ctx["hook_hat"]
    for ob in [hh] + list(hh.children):
        ob.hide_render = hat == "ray"
    if hat == "hook":
        hh.location, hh.rotation_euler = (-0.22, Y0 + 0.12, 1.66), (math.radians(-80), 0, 0)
    elif hat == "fall":
        c = [c for c in _cues(tl, "hat") if c.get("on") == "fall" and c["t"] <= t][-1]
        p0 = person_head(tl, "ray", c["t"]) + V((0, 0, 0.3))
        x = min(1.0, (t - c["t"]) / 0.55)
        land = p0 + V((0.35, -0.45, 0))
        hh.location = (p0.x + (land.x - p0.x) * x, p0.y + (land.y - p0.y) * x,
                       p0.z + 0.35 * math.sin(math.pi * x) * 0.6 - (p0.z - 0.03) * x * x)
        hh.rotation_euler = (math.radians(-40) * x, math.radians(70) * x, 0)
    # ---- the clock, the supper things, the trails
    h = _switch(_cues(tl, "clock"), "h", t, 8.0)
    m_ = _switch(_cues(tl, "clock"), "m", t, 10.0)
    ctx["clock"][0].rotation_euler = (0, ((h % 12) + m_ / 60) / 12 * 2 * math.pi, 0)
    ctx["clock"][1].rotation_euler = (0, m_ / 60 * 2 * math.pi, 0)
    sup = _switch(_cues(tl, "supper"), "on", t, False)
    for ob in ctx["supper"]:
        ob.hide_render = not sup
    ta = _switch(_cues(tl, "trail"), "a", t, False)
    tb = _switch(_cues(tl, "trail"), "b", t, False)
    for ob in ctx["trail_a"]:
        ob.hide_render = not ta
    for ob in ctx["trail_b"]:
        ob.hide_render = not tb
    # ---- people: sitting, kneeling, bending at the hips, a fist knocking, Ray raking
    from blocky import acting as _ac

    for who, keys in tl["acting"].items():
        tor = bpy.data.objects.get(f"{who}.torso")
        if tor is not None:   # "bend": the torso bends forward at the hips (kneeling to knock on the floor)
            tor.rotation_euler = (math.radians(_ac._held(keys, "bend", t, 0.0)), 0, 0)
        for sx_ in (-1, 1):
            leg = bpy.data.objects.get(f"{who}.leg{sx_}")
            if leg is None:
                continue
            if _switch(keys, "sit", t, False):
                leg.rotation_euler = (-math.pi / 2, 0, 0)
            elif _switch(keys, "kneel", t, False):
                leg.rotation_euler = (math.pi / 2, 0, 0)
    for c in _cues(tl, "fist"):
        arm = bpy.data.objects.get(f"{c.get('who', 'me')}.arm{c.get('arm', 1)}")
        if arm is None:
            continue
        for d in c.get("pattern", [0.0]):
            x = t - (c["t"] + d)
            if -0.18 < x < 0.12:
                lift = math.radians(c.get("lift", 32)) * (_ss((x + 0.18) / 0.1) * (1 - _ss((x + 0.03) / 0.03))
                                                         if x < 0 else 0.0)
                arm.rotation_euler.x -= lift
    for c in [c for c in _cues(tl, "arm_to") if c["t"] <= t][-1:]:
        if not c.get("to"):
            continue
        ob = bpy.data.objects.get(f"{c['who']}.arm{c.get('arm', 1)}")
        root = bpy.data.objects.get(c["who"])
        if ob is None or root is None:
            continue
        bpy.context.view_layer.update()
        sh = ob.matrix_world.translation.copy()
        tgt = V(c["to"])
        for d in c.get("pattern", []):
            x = t - (c["t"] + c.get("knock_at", 0.0) + d)
            if -0.16 < x < 0.06:
                tgt = tgt + V((0, 0, 0.08 * _ss((x + 0.16) / 0.09) * (1 - _ss((x + 0.03) / 0.03)) if x < 0 else 0.0))
        dv = tgt - sh
        z = -dv.normalized()
        xx = V((1, 0, 0)) - z.x * z
        xx.normalize()
        sc = root.scale
        # the arm's block is 2 rig units from its pivot (+0.25 above it): stretch it to reach, in close-ups only
        k = dv.length / (1.75 * sc.z)
        ob.matrix_world = frame(xx, z.cross(xx), z, sh) @ Matrix.Diagonal((sc.x, sc.y, sc.z * k, 1))
    rk = ctx["rake"]
    rake_on = _switch(_cues(tl, "rake"), "on", t, False)
    for ob in [rk] + list(rk.children):
        ob.hide_render = not rake_on
    if rake_on and bpy.data.objects.get("ray") is not None:
        sw = math.sin(2 * math.pi * 0.9 * t)
        for sx_ in (-1, 1):
            arm = bpy.data.objects[f"ray.arm{sx_}"]
            arm.rotation_euler.x -= math.radians(48 + 16 * sw)
        bpy.context.view_layer.update()
        hand = bpy.data.objects["ray.arm1"].matrix_world @ V((0, 0, -1.75))
        root = bpy.data.objects["ray"]
        fwd = root.matrix_world.to_3x3() @ V((0, -1, 0))
        tip = V((hand.x, hand.y, YARD_Z)) + fwd * (1.1 + 0.25 * sw)
        d = (tip - hand).normalized()
        rk.location = hand + d * 0.0
        rk.rotation_euler = (-d).to_track_quat("Z", "Y").to_euler()
    # ---- the keeper
    info = place_keeper(kit, story, tl, t, ctx)
    if info is not None:
        ctx["eye_glow"].default_value = EYE_GLOW
    shot_look(kit, tl, t, ctx, over, info)
    return over


def shot_look(kit, tl, t, ctx, over, info):
    """One shot's own light, from a "shot" cue's `look` (on at the shot's first frame, off with {"look": null} at
    its last), on top of everything else. Keys: bulb / fill / night / moon / bounce: gains on those lights; porch:
    watts on the porch light behind the front door's glass; key, key2, under: [pos, aim, watts, cone degrees?,
    colour?] a spot put exactly there ("face" for aim means the keeper's face; the colour defaults to warm
    tungsten, and the keeper's shots use a cool near-white)."""
    from blocky import kit as K

    look = _switch(_cues(tl, "shot"), "look", t, None)
    for nm in ("key", "key2", "under", "porch"):
        over[nm] = 0.0
    if not look:
        return
    if "porch" in look:
        K.LIGHTS["porch"]["base"] = look["porch"]
        over["porch"] = 1.0
    if "moon" in look:
        over["moonlight"] = over.get("moonlight", 1.0) * look["moon"]
    if "bounce" in look:
        over["bounce"] = look["bounce"]
    if "bulb" in look:
        over["bulb"] = over.get("bulb", 1.0) * look["bulb"]
    if "fill" in look:
        over["fill"] = look["fill"]
    if "night" in look:
        over["door night"] = over.get("door night", 1.0) * look["night"]
        over["window night"] = over.get("window night", 1.0) * look["night"]
    for nm in ("key", "key2", "under"):
        if nm not in look:
            continue
        pos, aim, watts = look[nm][:3]
        if aim == "face":
            if info is None:      # aimed at its face, but it isn't there (it has gone, later in the shot)
                continue
            aim = info["face"]
        ob = K.LIGHTS[nm]["obj"]
        ob.location = pos
        ob.rotation_euler = (V(aim) - V(pos)).to_track_quat("-Z", "Y").to_euler()
        K.LIGHTS[nm]["base"] = watts
        if len(look[nm]) > 3:
            K.LIGHTS[nm]["light"].spot_size = math.radians(look[nm][3])
        K.LIGHTS[nm]["light"].color = K.col(look[nm][4] if len(look[nm]) > 4 else "#ffd2a0")[:3]
        over[nm] = 1.0

