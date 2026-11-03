"""warm-shoes: our cat Biscuit brings home warm shoes; the tall stranger one streetlight behind Dad is Biscuit.

One bright, saturated, plastic world (the "closer" look): a mint-green single-storey house with a white porch and a
long rail, a picket gate, one straight road with eight streetlights and a bus shelter at the far end, a gold field.
The house is a real shell (walls, ceiling, my room, the hall with the cat flap), so inside shots are inside.

Built here, by hand, from kit.py's parts (no text anywhere; the only marks are the chalk digits on the slate post):
- SHOES: seven kinds of blocky shoe, built into pairs and placed by the "pairs" cue; warm ones give off steam.
- THE RAIL: twelve slots along the porch rail; the "count" cue says how many pairs stand there and which digit the
  slate panel on the post shows (the rule meter).
- BISCUIT: a fat ginger tabby of blocks, with a drawn face; the "cat" cue places and poses him.
- THE STRIDER: the rig's 'strider' character, stretched here (arms, coat, head, ears and a tail at the hem, green eyes).
- LIGHT: five looks (morning, afternoon, sundown, night, dawn), each shot names one; the light ramps into the next
  look over the last 0.35 s of the shot before a cut, so no light ever switches (flash bar).
Cues (story.json "cues", each restates its whole state): count, pairs, cat, strider, flap, tap, bus, car, props.
"""

from __future__ import annotations

import math
import tempfile
from pathlib import Path

import bpy
from mathutils import Vector as V

from blocky import bl_story, faces, rig

DECK = 0.4            # the porch deck and the house floor (top)
RAIL_Z = DECK + 1.0   # the rail ledge's top
TMP = Path(tempfile.mkdtemp(prefix="warmshoes-"))
INK = "#2b2230"

# ------------------------------------------------------------------------------------------------ small helpers
_n = [0]


def nm(p):
    _n[0] += 1
    return f"{p}.{_n[0]}"


def ss(x):
    x = min(1.0, max(0.0, x))
    return x * x * (3 - 2 * x)


def lerp(a, b, u):
    return a + (b - a) * u


def hexrgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def mixhex(a, b, u):
    ra, rb = hexrgb(a), hexrgb(b)
    return tuple((lerp(x, y, u) / 255.0) for x, y in zip(ra, rb))


class K:
    """kit shortcuts bound once in build()."""
    kit = None


def P(hexc, rough=0.45, spec=0.4):
    return K.kit.plastic(hexc, rough, spec=spec)


def B(parent, size, loc, mat, name="b", bevel=0.006, rot=(0, 0, 0)):
    return K.kit.box(nm(name), size, loc, mat, parent, rot, bevel)


def E(parent, loc=(0, 0, 0), name="e", rot=(0, 0, 0)):
    return K.kit.empty(nm(name), loc, parent, rot)


def no_shadow(ob):
    try:
        ob.visible_shadow = False
    except Exception:
        pass


def hide(ob, h=True):
    ob.hide_render = h
    for c in ob.children_recursive:
        c.hide_render = h


# ------------------------------------------------------------------------------------------------ shoes
# every shoe: toe toward -y, 0.30 m long, origin at the middle of the sole's underside


def shoe(kind, side, parent, c=None, sock=False):
    """One blocky shoe. kind: sneaker, boot, low, slipper, heel, sandal, rubber. c: colours (body, accent, sole)."""
    c = c or {}
    R = E(parent, (0, 0, 0), f"shoe-{kind}")
    body, acc, sole = c.get("body", "#f6f6f2"), c.get("acc", "#e23a3a"), c.get("sole", "#f2f2ee")
    if kind == "sneaker":
        B(R, (0.100, 0.30, 0.035), (0, 0, 0.0175), P(sole, 0.6), "sole")
        B(R, (0.104, 0.304, 0.010), (0, 0, 0.012), P(acc, 0.5), "stripe", 0.003)
        B(R, (0.092, 0.20, 0.055), (0, -0.04, 0.0625), P(body, 0.5), "vamp", 0.012)
        B(R, (0.094, 0.07, 0.05), (0, -0.12, 0.058), P(body, 0.5), "toe", 0.02)
        B(R, (0.092, 0.11, 0.145), (0, 0.09, 0.1075), P(body, 0.5), "collar", 0.014)
        for i, y in enumerate((-0.095, -0.055, -0.015)):
            B(R, (0.088, 0.012, 0.012), (0, y, 0.094), P(acc, 0.5), "lace", 0.004)
        B(R, (0.05, 0.06, 0.012), (0, 0.045, 0.13), P(acc, 0.5), "tongue", 0.004)
        if sock:
            cols = ("#ffffff", "#2fb5a8", "#ffffff")
            for i, cc in enumerate(cols):
                B(R, (0.072, 0.072, 0.022), (0, 0.09, 0.19 + 0.022 * i + 0.011), P(cc, 0.8), "sock", 0.006,
                  rot=(0.0, 0.0, 0.0))
    elif kind == "boot":
        B(R, (0.108, 0.31, 0.04), (0, 0, 0.02), P(sole, 0.7), "sole")
        B(R, (0.100, 0.21, 0.085), (0, -0.045, 0.0825), P(body, 0.55), "vamp", 0.015)
        B(R, (0.100, 0.075, 0.07), (0, -0.115, 0.075), P(acc, 0.55), "toe", 0.025)
        B(R, (0.098, 0.13, 0.17), (0, 0.075, 0.165), P(body, 0.55), "shaft", 0.015)
        B(R, (0.104, 0.03, 0.02), (0, 0.075, 0.255), P(acc, 0.6), "cuff", 0.006)
        for i in range(3):
            B(R, (0.07, 0.01, 0.01), (0, 0.0 + 0.0 * i + 0.03 * i, 0.128 + 0.0 * i + 0.0), P("#efe4c8", 0.7), "lace", 0.003)
    elif kind == "low":
        B(R, (0.096, 0.30, 0.02), (0, 0, 0.01), P(sole, 0.5), "sole")
        B(R, (0.092, 0.27, 0.05), (0, -0.01, 0.045), P(body, c.get("rough", 0.3), spec=0.7), "upper", 0.018)
        B(R, (0.07, 0.10, 0.02), (0, 0.03, 0.078), P(body, c.get("rough", 0.3), spec=0.7), "tongue", 0.008)
        B(R, (0.096, 0.03, 0.05), (0, 0.145, 0.045), P(sole, 0.5), "heel", 0.008)
    elif kind == "tap":
        B(R, (0.088, 0.29, 0.02), (0, 0, 0.01), P("#16161a", 0.4), "sole")
        B(R, (0.084, 0.22, 0.05), (0, 0.0, 0.045), P("#1d1d22", 0.25, spec=0.8), "upper", 0.015)
        B(R, (0.084, 0.07, 0.04), (0, -0.115, 0.04), P("#1d1d22", 0.25, spec=0.8), "toe", 0.02)
        B(R, (0.07, 0.04, 0.012), (0, -0.145, 0.006), P("#c9ced6", 0.2, spec=0.9), "plate", 0.003)
        B(R, (0.06, 0.03, 0.012), (0, 0.135, 0.006), P("#c9ced6", 0.2, spec=0.9), "plate2", 0.003)
        B(R, (0.04, 0.02, 0.05), (0, 0.045, 0.085), P("#d7263d", 0.5), "bow", 0.006)
    elif kind == "slipper":
        pk = body
        B(R, (0.118, 0.29, 0.09), (0, 0, 0.045), P(pk, 0.95, spec=0.1), "shell", 0.034)
        B(R, (0.07, 0.12, 0.02), (0, 0.06, 0.094), P(acc, 0.95, spec=0.1), "inside", 0.008)
        for i in range(7):
            ang = i * 0.9
            B(R, (0.03, 0.03, 0.03), (0.04 * math.cos(ang), -0.07 + 0.045 * math.sin(ang) * 2.0, 0.088 + 0.004 * (i % 3)),
              P(pk, 0.95, spec=0.1), "fuzz", 0.012)
        if c.get("sand"):
            for i in range(9):
                B(R, (0.02, 0.02, 0.014), (0.03 * math.sin(i * 2.1) + 0.015, 0.16 + 0.03 * (i % 4), 0.007 + 0.012 * (i // 6)),
                  P("#e9cf8f", 0.9), "sand", 0.005)
            B(R, (0.07, 0.07, 0.04), (0.0, 0.15, 0.02), P("#e9cf8f", 0.9), "sandpile", 0.015)
            B(R, (0.04, 0.05, 0.05), (0.0, 0.1, 0.07), P("#e9cf8f", 0.9), "sandspill", 0.012)
    elif kind == "heel":
        B(R, (0.07, 0.17, 0.014), (0, -0.06, 0.12), P(body, 0.3, spec=0.7), "sole", 0.005, rot=(-0.28, 0, 0))
        B(R, (0.075, 0.10, 0.045), (0, -0.095, 0.108), P(body, 0.3, spec=0.7), "toebox", 0.016, rot=(-0.28, 0, 0))
        B(R, (0.07, 0.07, 0.05), (0, 0.065, 0.1), P(body, 0.3, spec=0.7), "back", 0.012)
        B(R, (0.022, 0.022, 0.1), (0, 0.105, 0.05), P(body, 0.3, spec=0.7), "stick", 0.006)
        B(R, (0.072, 0.012, 0.012), (0, 0.0, 0.135), P(acc, 0.4), "strap", 0.004)
    elif kind == "sandal":
        B(R, (0.094, 0.29, 0.02), (0, 0, 0.01), P(sole, 0.6), "sole")
        for y in (-0.07, 0.0, 0.06):
            B(R, (0.1, 0.022, 0.03), (0, y, 0.034), P(body, 0.6), "strap", 0.006)
        B(R, (0.03, 0.03, 0.03), (0.0, -0.13, 0.034), P(acc, 0.6), "flower", 0.01)
    elif kind == "rubber":
        B(R, (0.116, 0.32, 0.045), (0, 0, 0.0225), P("#2c2a22", 0.8), "sole")
        B(R, (0.112, 0.22, 0.10), (0, -0.04, 0.095), P(body, 0.35, spec=0.6), "foot", 0.02)
        B(R, (0.108, 0.10, 0.085), (0, -0.12, 0.085), P(body, 0.35, spec=0.6), "toe", 0.03)
        B(R, (0.112, 0.15, 0.32), (0, 0.075, 0.245), P(body, 0.35, spec=0.6), "shaft", 0.02)
        mud = P("#6a4a2a", 0.95, spec=0.1)
        B(R, (0.122, 0.33, 0.06), (0, 0, 0.065), mud, "mud", 0.02)
        for i, (x, y, z) in enumerate(((0.04, -0.1, 0.14), (-0.05, 0.02, 0.17), (0.05, 0.08, 0.2), (-0.04, 0.1, 0.12))):
            B(R, (0.04, 0.05, 0.03), (x, y, z), mud, "splat", 0.012)
        for i in range(7):
            ang = i * 0.8
            B(R, (0.006, 0.09, 0.006), (0.06 * math.cos(ang), 0.02 + 0.03 * math.sin(i * 1.7), 0.16 + 0.03 * i),
              P("#e8c34a", 0.9), "hay", 0.002, rot=(0.5 * math.sin(i), 0.4, ang))
    if c.get("sawdust"):
        for i in range(10):
            B(R, (0.014, 0.014, 0.008), (0.03 * math.sin(i * 2.3), -0.09 - 0.02 * (i % 4) + 0.04 * (i // 5), 0.126 + 0.001 * i),
              P("#f0dca8", 0.95), "sawdust", 0.003)
    return R


def pair(name, kind, c=None, sock=False, sawdust=False, sand=False, parent=None, gap=0.085):
    root = E(parent, (0, 0, 0), name)
    cc = dict(c or {})
    if sawdust:
        cc["sawdust"] = True
    if sand:
        cc["sand"] = True
    L = shoe(kind, -1, root, cc, sock)
    L.location = (-gap, 0, 0)
    Rr = shoe(kind, 1, root, {**cc, "sawdust": cc.get("sawdust")}, False)
    Rr.location = (gap, 0, 0)
    root["L"] = L.name
    root["R"] = Rr.name
    return root


RAIL_KINDS = [
    ("boot", {"body": "#b98a4e", "acc": "#8f6430", "sole": "#4a3320"}),
    ("slipper", {"body": "#ff8fc0", "acc": "#d95c97"}),
    ("tap", {}),
    ("heel", {"body": "#d7263d", "acc": "#f2c14e"}),
    ("sneaker", {"body": "#5b8def", "acc": "#fdfdfd", "sole": "#f6f6f2"}),
    ("low", {"body": "#6b3d1e", "sole": "#2b1a0e", "rough": 0.5}),
    ("boot", {"body": "#23232b", "acc": "#3a3a46", "sole": "#111115"}),
    ("sandal", {"body": "#f2c14e", "acc": "#ff7a3d", "sole": "#c9a05a"}),
    ("sneaker", {"body": "#6cc24a", "acc": "#fdfdfd", "sole": "#f6f6f2"}),
    ("rubber", {"body": "#f2c14e"}),
    ("slipper", {"body": "#7fc4ff", "acc": "#4a8fd0"}),
    ("low", {"body": "#0c0c10", "sole": "#16161a", "rough": 0.08}),   # Thursday's shiny pair is the twelfth
]
RAIL_SLOTS = [(-1.5 - 0.72 * k, -3.0) for k in range(7)] + [(2.15 + 0.72 * k, -3.0) for k in range(5)]
# the six named pairs the story moves about
NAMED = {
    "sneaker": ("sneaker", {"body": "#fbfbf8", "acc": "#e23a3a", "sole": "#f6f6f2"}, {"sock": True}),
    "work": ("boot", {"body": "#c89a5a", "acc": "#8f6430", "sole": "#3a2616"}, {"sawdust": True}),
    "slipper": ("slipper", {"body": "#ff8fc0", "acc": "#d95c97"}, {"sand": True}),
    "tap": ("tap", {}, {}),
    "shiny": ("low", {"body": "#08080b", "sole": "#16161a", "rough": 0.06}, {}),
    "rubber": ("rubber", {"body": "#2f9a4a"}, {}),
    "dadboots": ("boot", {"body": "#c89a5a", "acc": "#8f6430", "sole": "#3a2616"}, {}),
    "oldsneak": ("sneaker", {"body": "#fbfbf8", "acc": "#e23a3a", "sole": "#f6f6f2"}, {}),
    "slipper2": ("slipper", {"body": "#ff8fc0", "acc": "#d95c97"}, {}),
}


# ------------------------------------------------------------------------------------------------ Biscuit
GINGER, STRIPE, CREAM, PINKN = "#f08a2c", "#c4621a", "#fbe3c0", "#ff8aa8"


def cat_face(expr, path):
    from PIL import Image, ImageDraw

    W, H = 320, 250
    im = Image.new("RGB", (W, H), hexrgb(GINGER))
    d = ImageDraw.Draw(im)
    # forehead stripes
    for x in (-34, 0, 34):
        d.rounded_rectangle([W / 2 + x - 8, 6, W / 2 + x + 8, 56 - abs(x) * 0.3], 6, fill=hexrgb(STRIPE))
    # cream muzzle
    d.ellipse([W / 2 - 66, 128, W / 2 + 66, 238], fill=hexrgb(CREAM))
    # eyes
    eye_r = 52
    for sx in (-1, 1):
        cx, cy = W / 2 + sx * 84, 98
        if expr == "asleep":
            d.arc([cx - 40, cy - 22, cx + 40, cy + 30], 20, 160, fill=hexrgb(INK), width=9)
            continue
        d.ellipse([cx - eye_r, cy - eye_r, cx + eye_r, cy + eye_r], fill=(120, 214, 98))
        d.ellipse([cx - eye_r + 8, cy - eye_r + 8, cx + eye_r - 8, cy + eye_r - 8], fill=(148, 232, 112))
        d.ellipse([cx - 11, cy - 40, cx + 11, cy + 40], fill=(14, 12, 16))                  # the slit
        d.ellipse([cx - 30, cy - 36, cx - 12, cy - 18], fill=(255, 255, 255))               # the highlight
        lid = {"neutral": 0.0, "smug": 0.5, "slowblink": 0.7}.get(expr, 0.0)
        if lid:
            d.rectangle([cx - eye_r - 3, cy - eye_r - 3, cx + eye_r + 3, cy - eye_r + 2 * eye_r * lid],
                        fill=hexrgb(GINGER))
            d.line([cx - eye_r, cy - eye_r + 2 * eye_r * lid, cx + eye_r, cy - eye_r + 2 * eye_r * lid],
                   fill=hexrgb(INK), width=7)
    # nose and the w mouth
    d.polygon([(W / 2 - 22, 150), (W / 2 + 22, 150), (W / 2, 176)], fill=hexrgb(PINKN))
    d.line([(W / 2, 176), (W / 2, 190)], fill=hexrgb(INK), width=6)
    sm = 12 if expr == "smug" else 0
    d.arc([W / 2 - 40, 178 - sm, W / 2, 210], 10, 170, fill=hexrgb(INK), width=6)
    d.arc([W / 2, 178 - sm, W / 2 + 40, 210], 10, 170, fill=hexrgb(INK), width=6)
    # whisker dots
    for sx in (-1, 1):
        for dy in (-10, 6):
            d.ellipse([W / 2 + sx * 48 - 4, 168 + dy - 4, W / 2 + sx * 48 + 4, 168 + dy + 4], fill=hexrgb("#b8714a"))
    im.save(path)
    return path


class Cat:
    """Biscuit. Front is -y at yaw 0. A fat ginger tabby: long block body, four short legs, a block head with two
    triangle ears, a long block tail in three segments, darker stripe bands, a cream chest and muzzle, a drawn face."""

    def __init__(self, kit):
        self.kit = kit
        g, st, cr = P(GINGER, 0.55), P(STRIPE, 0.55), P(CREAM, 0.6)
        self.root = E(None, (0, 0, 0), "biscuit")
        self.bodyg = E(self.root, (0, 0, 0.0), "bodyg")
        self.body = B(self.bodyg, (0.27, 0.46, 0.25), (0, 0, 0.21), g, "cbody", 0.06)
        for i, y in enumerate((-0.12, -0.02, 0.08, 0.18)):
            B(self.bodyg, (0.29, 0.05, 0.27), (0, y, 0.215), st, "cstripe", 0.018)
        B(self.bodyg, (0.19, 0.10, 0.15), (0, -0.20, 0.17), cr, "cchest", 0.04)
        B(self.bodyg, (0.19, 0.12, 0.05), (0, 0.0, 0.098), cr, "cbelly", 0.02)
        self.legs = []
        for sx in (-1, 1):
            for yy in (-0.16, 0.17):
                lg = B(self.root, (0.075, 0.08, 0.13), (sx * 0.085, yy, 0.065), g, "cleg", 0.025)
                pw = B(self.root, (0.08, 0.09, 0.03), (sx * 0.085, yy - 0.006, 0.016), cr, "cpaw", 0.012)
                self.legs += [lg, pw]
        self.headg = E(self.bodyg, (0, -0.30, 0.31), "headg")
        B(self.headg, (0.215, 0.19, 0.19), (0, 0, 0), g, "chead", 0.05)
        for sx in (-1, 1):   # triangle ears
            v = [(-0.045, 0, 0), (0.045, 0, 0), (0.0, 0.0, 0.10), (-0.045, 0.05, 0), (0.045, 0.05, 0), (0.0, 0.03, 0.10)]
            f = [(0, 1, 2), (3, 5, 4), (0, 3, 4, 1), (0, 2, 5, 3), (1, 4, 5, 2)]
            ear = self.kit.mesh_obj(nm("cear"), v, f, g, self.headg, (sx * 0.06, -0.02, 0.085),
                                    (0, sx * 0.12, 0))
            inner = self.kit.mesh_obj(nm("cearin"), [(-0.026, 0, 0.004), (0.026, 0, 0.004), (0, 0, 0.07)], [(0, 1, 2)],
                                      P(PINKN, 0.6), self.headg, (sx * 0.06, -0.024, 0.088), (0, sx * 0.12, 0))
        # face plane, a decal 1.2 cm proud of the head's front
        self.face_mat = self.kit._new(nm("catface"))
        nt = self.face_mat.node_tree
        b = nt.nodes["Principled BSDF"]
        b.inputs["Roughness"].default_value = 0.6
        self.face_tex = nt.nodes.new("ShaderNodeTexImage")
        gc = nt.nodes.new("ShaderNodeTexCoord")
        nt.links.new(gc.outputs["Generated"], self.face_tex.inputs["Vector"])
        nt.links.new(self.face_tex.outputs["Color"], b.inputs["Base Color"])
        self.kit._fogged(self.face_mat, b.outputs[0])
        self.imgs = {}
        for e in ("neutral", "smug", "slowblink", "asleep"):
            p = cat_face(e, str(TMP / f"cat-{e}.png"))
            im = bpy.data.images.load(p)
            im.colorspace_settings.name = "sRGB"
            self.imgs[e] = im
        self.face_tex.image = self.imgs["neutral"]
        self.facepl = self.kit.plane(nm("catface"), (0.205, 0.16), (0, -0.107, -0.005), self.face_mat, self.headg,
                                     rot=(math.pi / 2, 0, 0))
        self.facepl.rotation_euler = (math.pi / 2, 0, 0)
        # whiskers
        for sx in (-1, 1):
            for k, dz in enumerate((-0.012, 0.012)):
                B(self.headg, (0.10, 0.004, 0.004), (sx * 0.15, -0.1, -0.035 + dz * 1.4), P("#fff6e6", 0.6), "whisk", 0.0015,
                  rot=(0, 0, sx * (0.15 + 0.1 * k)))
        # tail: three segments, each a child of the one before
        self.tail = []
        parent = E(self.bodyg, (0, 0.23, 0.26), "tail0")
        self.tail.append(parent)
        for i, (ln, col) in enumerate(((0.17, g), (0.16, st), (0.15, g))):
            B(parent, (0.06, 0.06, ln), (0, 0, ln / 2), col, "ctail", 0.022)
            nxt = E(parent, (0, 0, ln - 0.01), f"tail{i + 1}")
            self.tail.append(nxt)
            parent = nxt
        B(parent, (0.063, 0.063, 0.05), (0, 0, 0.02), st, "ctip", 0.02)
        self.pose_state = None
        self.carry = {}

    def place(self, x, y, z, yaw, pose="stand", face="neutral", tail="up", t=0.0, pitch=0.0, hidden=False, carry=None):
        r = self.root
        r.location = (x, y, z)
        r.rotation_euler = (0, 0, math.radians(yaw))
        hide(r, hidden)
        lie = pose in ("lie", "asleep")
        for lg in self.legs:
            lg.hide_render = lie or hidden
        self.bodyg.location = (0, 0, -0.10 if lie else 0.0)
        self.bodyg.rotation_euler = (math.radians(pitch), 0, 0)
        sw = math.sin(t * 2.2) * 0.12
        shapes = {"up": (-0.45, 0.35, 0.55), "down": (-1.9, 0.2, 0.2), "high": (-0.2, 0.2, 0.3)}
        if lie:
            self.tail[0].rotation_euler = (-1.5, 0, 0)
            self.tail[1].rotation_euler = (0, 0.8, 0)
            self.tail[2].rotation_euler = (0, 0.9, 0)
        else:
            a = shapes.get(tail, shapes["up"])
            self.tail[0].rotation_euler = (a[0], sw, 0)
            self.tail[1].rotation_euler = (a[1], sw * 0.5, 0)
            self.tail[2].rotation_euler = (a[2], 0, 0)
        self.face_tex.image = self.imgs.get(face, self.imgs["neutral"])
        for k, ob in self.carry.items():
            hide(ob, hidden or k != carry)


# ------------------------------------------------------------------------------------------------ the Strider
def strider_late(kit, ctx):
    """The rig's 'strider' stretched into the stranger (called on the first frame, once the cast exists)."""
    ch = rig.CHARS.get("strider")
    if ch is None:
        return
    ctx["strider"] = ch
    for k in ("arm-1", "arm1"):
        ch.P[k].scale = (1.0, 1.0, 1.42)         # hands down by the knees
    for hinge, sx in ch.coat:
        hinge.scale = (1.0, 1.0, 2.35)           # the coat to the shins
    ch.head.scale = (1.05, 1.0, 1.45)            # a head too long
    toff = P("#9a6a3c", 0.7)
    dark = P("#6f4a28", 0.7)
    hg = ch.head.children[0]                     # headg, centred at the head's middle
    # eyeshine: two small emissive discs on the dark hollow eyes; pale before the reveal (L61), cat-green after
    glow = kit.emit("#e6f0ea", 0.9, name="eyeshine")
    ctx["glow"] = glow
    ctx["eyes"] = []
    for sx in (-1, 1):
        d = kit.cyl(nm("eyeshine"), 0.03, 0.02, (sx * 0.232, -0.585, 0.08), glow, hg, rot=(math.pi / 2, 0, 0), n=16)
        no_shadow(d)
        ctx["eyes"].append(d)
    ctx["stail"] = []
    # buttons down the coat, a collar
    gold = P("#e8c34a", 0.4)
    for i in range(5):
        B(ch.torso, (0.16, 0.05, 0.16), (0.0, -0.52, 0.2 + 0.36 * i), gold, "sbutton", 0.03)
    # shoes: one variant per leg, switched by the "strider" cue
    ctx["sshoes"] = {}
    legs = [ch.P["leg-1"], ch.P["leg1"]]
    variants = {
        "shiny": [("#08080b", 0.05, (1.04, 1.45, 0.5), (0, -0.2, -1.75))],
        "sneaker": [("#fbfbf8", 0.5, (1.04, 1.5, 0.6), (0, -0.22, -1.74)), ("#e23a3a", 0.5, (1.06, 0.9, 0.12), (0, -0.2, -1.6))],
        "rubber": [("#2f9a4a", 0.35, (1.12, 1.35, 1.25), (0, -0.1, -1.38)), ("#6a4a2a", 0.95, (1.16, 1.4, 0.45), (0, -0.1, -1.8)),
                   ("#e8c34a", 0.9, (0.05, 0.9, 0.05), (0.45, 0.2, -1.2)), ("#e8c34a", 0.9, (0.05, 0.9, 0.05), (-0.4, 0.0, -1.0)),
                   ("#e8c34a", 0.9, (0.05, 0.8, 0.05), (0.1, 0.5, -0.95))],
    }
    for kind, parts in variants.items():
        lst = []
        for lg in legs:
            for hexc, rough, size, loc in parts:
                o = kit.box(nm("sshoe"), size, loc, kit.plastic(hexc, rough, spec=0.6), lg, bevel=0.06)
                o.hide_render = True
                lst.append(o)
        ctx["sshoes"][kind] = lst


# ------------------------------------------------------------------------------------------------ looks
# sky: horizon, low, mid, zenith. sun: azimuth (0 = from -y, the road's far end; 90 = from +x), elevation, energy, colour
LOOKS = {
    "morning": {"sky": ["#cfeeff", "#a9dcff", "#7cc2ff", "#4f9cf0"], "world": 1.0, "sun": (70, 40, 5.0, "#fff1d8"),
                "fill": 0.25, "street": 0.0, "hall": 0.8, "room": 0.8, "lamp": 0.0, "win": 1.0, "exp": 0.0},
    "afternoon": {"sky": ["#ffe3a8", "#ffd08a", "#ffc08a", "#8cc0ff"], "world": 1.0, "sun": (100, 24, 5.5, "#ffd08a"),
                  "fill": 0.3, "street": 0.0, "hall": 0.7, "room": 0.7, "lamp": 0.0, "win": 0.8, "exp": 0.0},
    "sundown": {"sky": ["#ff9d4d", "#ff6f6a", "#e0569b", "#7a4fd0"], "world": 0.8, "sun": (14, 6, 7.0, "#ffa860"),
                "fill": 0.55, "street": 1.0, "hall": 0.8, "room": 0.8, "lamp": 0.3, "win": 0.4, "exp": 0.0},
    "night": {"sky": ["#3a2a66", "#2c2058", "#1d1442", "#120a2c"], "world": 0.22, "sun": (200, 30, 0.9, "#8f8cff"),
              "fill": 0.0, "street": 1.0, "hall": 0.0, "room": 0.0, "lamp": 1.0, "win": 0.0, "exp": 0.6},
    "dawn": {"sky": ["#ffe3b0", "#ffd2b8", "#b0ccff", "#7aa4f2"], "world": 0.8, "sun": (80, 10, 3.8, "#ffe6bc"),
             "fill": 0.35, "street": 0.15, "hall": 0.7, "room": 0.6, "lamp": 0.0, "win": 0.5, "exp": 0.0},
}


def mix_look(a, b, u):
    out = {}
    for k in a:
        va, vb = a[k], b[k]
        if k == "sky":
            out[k] = [mixhex(x, y, u) for x, y in zip(va, vb)]
        elif k == "sun":
            out[k] = (lerp(va[0], vb[0], u), lerp(va[1], vb[1], u), lerp(va[2], vb[2], u), va[3] if u < 0.5 else vb[3],
                      mixhex(va[3], vb[3], u))
        else:
            out[k] = lerp(va, vb, u)
    return out


# ------------------------------------------------------------------------------------------------ build
def build(kit, story, tl):
    K.kit = kit
    ctx = {"story": story}
    ctx["shots"] = {s["id"]: s for s in story["shots"]}
    sc = bpy.context.scene

    # ---- the sky: a gradient from the horizon up (the camera sees it; it also lights the set softly)
    w = sc.world
    nt = w.node_tree
    bg = nt.nodes["Background"]
    tc = nt.nodes.new("ShaderNodeTexCoord")
    sep = nt.nodes.new("ShaderNodeSeparateXYZ")
    nt.links.new(tc.outputs["Generated"], sep.inputs[0])
    mr = nt.nodes.new("ShaderNodeMapRange")
    mr.inputs["From Min"].default_value = 0.0
    mr.inputs["From Max"].default_value = 0.55
    mr.clamp = True
    nt.links.new(sep.outputs["Z"], mr.inputs["Value"])
    ramp = nt.nodes.new("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].position = 0.0
    ramp.color_ramp.elements[1].position = 1.0
    e1 = ramp.color_ramp.elements.new(0.22)
    e2 = ramp.color_ramp.elements.new(0.55)
    nt.links.new(mr.outputs["Result"], ramp.inputs["Fac"])
    nt.links.new(ramp.outputs["Color"], bg.inputs["Color"])
    ctx["ramp"], ctx["bg"] = ramp, bg

    # ---- lights
    ctx["sun"] = kit.light("sun", "SUN", (0, 0, 50), 5.0, "#fff1d8", size=0.1)
    ctx["sun"].data.angle = 0.06
    ctx["fill"] = kit.light("camfill", "POINT", (0, 0, 2), 60, "#ffe9cf", size=0.6, shadow=False)
    ctx["hall"] = kit.light("hall", "POINT", (2.5, 3.2, 3.0), 260, "#fff2dc", size=0.4)
    ctx["room"] = kit.light("roomlight", "POINT", (-4.2, 3.4, 3.0), 240, "#fff2dc", size=0.4)
    ctx["lamp"] = kit.light("lamp", "POINT", (-5.55, 6.6, 1.5), 90, "#ffb866", size=0.12)
    ctx["win"] = kit.light("winlight", "AREA", (-3.5, 1.2, 2.4), 260, "#fff6e6", size=1.6,
                           rot=(math.radians(60), 0, 0))
    ctx["win"].data.size, ctx["win"].data.size_y = 1.7, 0.9
    kit.aim(ctx["win"], (-3.8, 4.5, 1.0))
    ctx["winkey"] = kit.light("winkey", "SPOT", (-5.2, 1.6, 1.9), 120, "#ffb866", size=0.25, spot=70, blend=0.6)
    kit.aim(ctx["winkey"], (-3.5, -2.0, 2.0))
    ctx["rimout"] = kit.light("rimout", "SPOT", (-3.5, -7.5, 3.4), 900, "#9a8cff", size=0.5, spot=40, blend=0.5)
    kit.aim(ctx["rimout"], (-3.5, -2.0, 2.0))
    ctx["streets"] = []
    ctx["porch"] = kit.light("porchfill", "POINT", (0.0, -1.2, 2.6), 120, "#ffe3bd", size=0.5, shadow=False)

    # ---- ground, road, sidewalk
    lawn = P("#6cc24a", 0.8, 0.15)
    B(None, (200, 160, 0.4), (0, -50, -0.2), lawn, "lawn", 0.0)
    road = kit.texture("asphalt", 0.4, tint="#9aa2b4")
    B(None, (6.6, 118, 0.1), (0, -70.5, 0.03), road, "road", 0.0)
    B(None, (5.2, 3.0, 0.1), (0, -10.3, 0.04), P("#c8c6c0", 0.7), "walk", 0.0)   # the sidewalk by the gate
    B(None, (24, 0.6, 0.18), (0, -9.0, 0.09), P("#cfcfc8", 0.7), "curb", 0.0)
    for k in range(8):                                                         # path stones from the gate to the steps
        B(None, (1.3, 0.62, 0.06), (0, -8.4 + 0.72 * k, 0.03), P("#d9d6cf", 0.7), "stone", 0.012)
    # gold field on the right, with tall grass tufts
    B(None, (60, 80, 0.12), (38, -62, 0.0), P("#e8b84a", 0.85, 0.1), "field", 0.0)
    for i in range(34):
        gx, gy = 7 + (i * 7) % 29, -27 - (i * 11) % 66
        try:
            kit.prop("grass", (gx + 0.3 * math.sin(i), gy, 0), rot=i * 40, height=1.2 + 0.2 * (i % 3), tint="#f0c24a")
        except Exception:
            pass

    # ---- the house
    ctx["house"] = build_house(kit)
    # ---- the gate and the fence
    white, white2 = P("#f6f3ec", 0.5), P("#ffffff", 0.5)
    for sx in (-1, 1):
        B(None, (0.28, 0.28, 1.45), (sx * 1.2, -9.0, 0.725), white, "gatepost", 0.025)
        B(None, (0.34, 0.34, 0.07), (sx * 1.2, -9.0, 1.485), white2, "postcap", 0.02)
    ctx["gatepost_top"] = (1.2, -9.0, 1.52)
    for sx in (-1, 1):                                       # picket fence out to both sides
        for i in range(24):
            x = sx * (1.5 + 0.38 * i)
            B(None, (0.12, 0.05, 1.05), (x, -9.0, 0.525), white, "picket", 0.012)
        B(None, (9.4, 0.05, 0.08), (sx * 5.7, -9.0, 0.78), white, "rail1", 0.01)
        B(None, (9.4, 0.05, 0.08), (sx * 5.7, -9.0, 0.30), white, "rail2", 0.01)
    gate = E(None, (-1.05, -9.0, 0), "gate")
    for i in range(6):
        B(gate, (0.12, 0.05, 1.05), (0.1 + i * 0.38, 0, 0.525), white, "gpicket", 0.012)
    B(gate, (2.0, 0.05, 0.08), (1.0, 0, 0.78), white, "grail", 0.01)
    B(gate, (2.0, 0.05, 0.08), (1.0, 0, 0.30), white, "grail", 0.01)
    # mailbox on a post (no lettering)
    B(None, (0.12, 0.12, 1.1), (-2.6, -9.9, 0.55), P("#8a6a4a", 0.7), "mpost", 0.01)
    B(None, (0.26, 0.5, 0.24), (-2.6, -9.9, 1.2), P("#d7263d", 0.4), "mailbox", 0.06)

    # ---- streetlights (eight, the nearest first), the bus shelter and a bus
    for k in range(8):
        y = -14.0 - 10.0 * k
        B(None, (0.12, 0.12, 5.1), (3.9, y, 2.55), P("#3b4252", 0.5), "pole", 0.02)
        B(None, (1.3, 0.09, 0.09), (3.3, y, 5.05), P("#3b4252", 0.5), "arm", 0.02)
        B(None, (0.46, 0.3, 0.14), (2.75, y, 5.0), P("#3b4252", 0.5), "head", 0.03)
        B(None, (0.34, 0.2, 0.05), (2.75, y, 4.92), kit.emit("#ffc75a", 14.0, name="bulb"), "bulb", 0.01)
        L = kit.light(f"street{k}", "POINT", (2.75, y, 4.7), 900, "#ffc75a", size=0.2)
        ctx["streets"].append(L)
    build_shelter(kit, ctx)
    ctx["bus"] = build_bus(kit)
    ctx["car"] = build_car(kit)
    # ---- neighbours, trees, a trash can
    for i, (x, y, rot, tint) in enumerate(((-16, -26, 90, "#ffd9a8"), (-17, -52, 90, "#cfe8ff"), (-16, -78, 90, "#ffc4d6"),
                                          (-27, -14, 90, "#d9f0c4"))):
        try:
            kit.prop("bldg_1story", (x, y, 0), rot=rot, scale=1.0, tint=tint)
        except Exception:
            pass
    for i, (nme, x, y, h) in enumerate((("commontree_1", -9, -16, 5.5), ("birchtree_1", -9.5, -40, 7.0), ("commontree_2", 9.5, -18, 6.0),
                                       ("commontree_1", -9, -64, 5.5), ("birchtree_1", 9.5, -34, 7.0), ("commontree_2", 12, -72, 6.0),
                                       ("birchtree_1", 14, -12, 7.0), ("commontree_1", -11, -88, 6.0))):
        try:
            kit.prop(nme, (x, y, 0), rot=37 * i, height=h, tint="#9be05a" if "common" in nme else "#c9f0a0")
        except Exception:
            pass
    for (x, y) in ((-6, -11.5), (6, -11.5), (-7, -30), (8, -46)):
        try:
            kit.prop("bush_1", (x, y, 0), rot=x * 9, height=1.2, tint="#58c24a")
        except Exception:
            pass
    ctx["trash"] = kit.prop("trashcan_cylindric", (-4.4, -22.0, 0), height=0.95, tint="#3fa5ff")
    ctx["trash_lid"] = kit.cyl("trashlid", 0.27, 0.05, (-4.4, -22.0, 0.98), P("#2f86d8", 0.4), None, n=18)
    # ---- the shoes: the twelve on the rail, the named pairs, the carried singles
    ctx["rail"] = []
    for i, (kind, c) in enumerate(RAIL_KINDS):
        pr = pair(f"rail{i}", kind, c)
        pr.rotation_euler = (0, 0, 0)
        pr.location = (RAIL_SLOTS[i][0], RAIL_SLOTS[i][1], RAIL_Z + 0.03)
        ctx["rail"].append(pr)
    ctx["named"] = {}
    for key, (kind, c, ex) in NAMED.items():
        pr = pair(f"named-{key}", kind, c, **ex)
        hide(pr, True)
        ctx["named"][key] = pr
    # the rail ledge and the shoes' tap shoe pivot: the left tap shoe rocks
    # ---- steam: pools of puffs
    smat = kit._new(nm("steam"))
    n_ = smat.node_tree
    n_.nodes.remove(n_.nodes["Principled BSDF"])
    tr = n_.nodes.new("ShaderNodeBsdfTransparent")
    em = n_.nodes.new("ShaderNodeEmission")
    em.inputs["Color"].default_value = (1, 1, 1, 1)
    em.inputs["Strength"].default_value = 1.6
    mx = n_.nodes.new("ShaderNodeMixShader")
    mx.inputs["Fac"].default_value = 0.16
    n_.links.new(tr.outputs[0], mx.inputs[1])
    n_.links.new(em.outputs[0], mx.inputs[2])
    out = next(n for n in n_.nodes if n.type == "OUTPUT_MATERIAL")
    n_.links.new(mx.outputs[0], out.inputs["Surface"])
    ctx["steam"] = []
    for s in range(3):
        site = []
        for j in range(14):
            o = kit.sphere(nm("steam"), 0.03, (0, 0, 0), smat, None, seg=16)
            no_shadow(o)
            o.hide_render = True
            site.append(o)
        ctx["steam"].append(site)
    # ---- Biscuit and what he carries
    ctx["cat"] = Cat(kit)
    for key, (kind, c) in (("heel", ("heel", {"body": "#d7263d", "acc": "#f2c14e"})),
                           ("shiny", ("low", {"body": "#08080b", "sole": "#16161a", "rough": 0.06}))):
        s = shoe(kind, -1, ctx["cat"].headg, c)
        s.location = (0.0, -0.13, -0.09)
        s.rotation_euler = (0.2, 0, 0)
        s.scale = (0.85, 0.85, 0.85)
        hide(s, True)
        ctx["cat"].carry[key] = s
    # ---- props that come and go
    ctx["props"] = build_props(kit)
    ctx["count_img"] = None
    ctx["late"] = False
    ctx["reveal_t"] = tl["lines"]["L61"]["onset"] if "lines" in tl and "L61" in tl["lines"] else 1e9
    build_inset(kit, ctx)
    return ctx


def wall_seg(parent, kit, x0, x1, z0, z1, y0=0.0, y1=0.25, outside="#8fd6b5", inside="#fbf0dc"):
    """A wall block between x0..x1, z0..z1 with its outer skin mint and its inner skin cream (no shared faces)."""
    if x1 - x0 < 0.01 or z1 - z0 < 0.01:
        return
    cx, cz = (x0 + x1) / 2, (z0 + z1) / 2
    B(parent, (x1 - x0, 0.18, z1 - z0), (cx, y0 + 0.09, cz), P(outside, 0.7, 0.1), "wallo", 0.0)
    B(parent, (x1 - x0, 0.07, z1 - z0), (cx, y1 - 0.035, cz), P(inside, 0.8, 0.05), "walli", 0.0)


def build_house(kit):
    H = {}
    mint = "#8fd6b5"
    floor_w = kit.texture("wood", 0.7, tint="#f1d8b0")
    # slab and deck
    B(None, (14.6, 7.4, DECK), (0, 3.7, DECK / 2 - 0.0), P("#d8cfc0", 0.8), "slab", 0.0)
    B(None, (14.6, 3.4, DECK), (0, -1.7, DECK / 2), P("#f6f1e6", 0.5), "deck", 0.0)
    B(None, (14.6, 7.3, 0.03), (0, 3.65, DECK + 0.015), floor_w, "floor", 0.0)       # wood floor inside
    B(None, (14.6, 3.2, 0.03), (0, -1.6, DECK + 0.015), P("#f1ece0", 0.55), "deckcap", 0.0)
    for k in (-1, 1):                                                              # two steps down to the path
        B(None, (2.2, 0.5, DECK * 0.5), (0, -3.5 - 0.0, DECK * 0.25), P("#f6f1e6", 0.5), "step1", 0.0) if k == 1 else None
    B(None, (2.2, 0.5, 0.2), (0, -3.75, 0.1), P("#f6f1e6", 0.5), "step2", 0.0)
    wz0, wz1 = DECK, DECK + 2.8
    # front wall with a door opening (x 0..1) and a window (x -4.4..-2.6, z 1.5..2.5)
    wall_seg(None, kit, -7.2, -4.4, wz0, wz1)
    wall_seg(None, kit, -4.4, -2.6, wz0, 1.5)
    wall_seg(None, kit, -4.4, -2.6, 2.5, wz1)
    wall_seg(None, kit, -2.6, 0.0, wz0, wz1)
    wall_seg(None, kit, 0.0, 1.0, 2.5, wz1)
    wall_seg(None, kit, 1.0, 7.2, wz0, wz1)
    # window frame, sill, a nearly clear pane, curtains
    wf = P("#ffffff", 0.45)
    B(None, (1.96, 0.1, 0.07), (-3.5, -0.03, 1.5), wf, "wsill", 0.01)
    B(None, (1.96, 0.1, 0.07), (-3.5, -0.03, 2.5), wf, "whead", 0.01)
    for x in (-4.45, -2.55):
        B(None, (0.07, 0.1, 1.07), (x, -0.03, 2.0), wf, "wjamb", 0.01)
    pane = kit._new(nm("pane"))
    nt = pane.node_tree
    nt.nodes.remove(nt.nodes["Principled BSDF"])
    tr = nt.nodes.new("ShaderNodeBsdfTransparent")
    gl = nt.nodes.new("ShaderNodeBsdfGlossy")
    gl.inputs["Roughness"].default_value = 0.05
    gl.inputs["Color"].default_value = (0.8, 0.9, 1.0, 1)
    mx = nt.nodes.new("ShaderNodeMixShader")
    mx.inputs["Fac"].default_value = 0.05
    nt.links.new(tr.outputs[0], mx.inputs[1])
    nt.links.new(gl.outputs[0], mx.inputs[2])
    nt.links.new(mx.outputs[0], next(n for n in nt.nodes if n.type == "OUTPUT_MATERIAL").inputs["Surface"])
    p = kit.plane(nm("pane"), (1.84, 1.0), (-3.5, 0.06, 2.0), pane, None, rot=(math.pi / 2, 0, 0))
    no_shadow(p)
    for sx in (-1, 1):
        B(None, (0.24, 0.05, 1.25), (-3.5 + sx * 1.1, 0.3, 1.95), P("#2fb5a8", 0.8, 0.1), "curtain", 0.02)
    # back and side walls, partition (x -1.7, doorway y 3..4), ceiling, roof
    wall_seg(None, kit, -7.2, 7.2, wz0, wz1, 7.15, 7.4, outside=mint, inside="#fbf0dc")
    for sx in (-1, 1):
        B(None, (0.18, 7.4, 2.8), (sx * 7.29, 3.7, DECK + 1.4), P(mint, 0.7, 0.1), "sidew", 0.0)
        B(None, (0.07, 7.2, 2.8), (sx * 7.165, 3.7, DECK + 1.4), P("#fbf0dc", 0.8), "sidewi", 0.0)
    B(None, (0.2, 3.1, 2.8), (-1.7, 1.65, DECK + 1.4), P("#f3e6d0", 0.8), "part1", 0.0)
    B(None, (0.2, 3.2, 2.8), (-1.7, 5.6, DECK + 1.4), P("#f3e6d0", 0.8), "part2", 0.0)
    B(None, (0.2, 1.0, 0.7), (-1.7, 3.5, DECK + 2.45), P("#f3e6d0", 0.8), "part3", 0.0)
    B(None, (14.9, 7.5, 0.2), (0, 3.65, wz1 + 0.1), P("#fbf0dc", 0.9), "ceiling", 0.0)
    # roof: two sloped slabs and gable ends, a deep red-orange
    roof = P("#e0573f", 0.55)
    for yc, ang in ((1.4, 0.25), (5.9, -0.25)):
        B(None, (15.6, 4.9, 0.2), (0, yc, wz1 + 0.75), roof, "roof", 0.02, rot=(ang, 0, 0))
    B(None, (15.6, 0.3, 0.25), (0, 3.65, wz1 + 1.38), P("#c24a35", 0.55), "ridge", 0.02)
    for sx in (-1, 1):   # gable triangles
        kit.mesh_obj(nm("gable"), [(0, -0.9, wz1 + 0.2), (0, 8.2, wz1 + 0.2), (0, 3.65, wz1 + 1.35)], [(0, 1, 2)],
                     P(mint, 0.7), None, (sx * 7.25, 0, 0))
    # the porch: posts, roof beam skipped, a rail with a wide ledge and balusters, with a gap for the steps
    pw = P("#f6f3ec", 0.5)
    for x in (-7.0, -1.1, 1.1, 7.0):
        B(None, (0.18, 0.18, 2.6), (x, -3.0, DECK + 1.3), pw, "ppost", 0.02)
    for (x0, x1) in ((-7.1, -1.0), (1.0, 7.1)):
        cx = (x0 + x1) / 2
        B(None, (x1 - x0, 0.36, 0.06), (cx, -3.0, RAIL_Z), pw, "ledge", 0.012)
        B(None, (x1 - x0, 0.08, 0.06), (cx, -3.0, DECK + 0.12), pw, "lowrail", 0.01)
        n = int((x1 - x0) / 0.3)
        for i in range(n):
            B(None, (0.04, 0.04, RAIL_Z - DECK - 0.12), (x0 + 0.15 + i * 0.3, -3.0, DECK + 0.12 + (RAIL_Z - DECK - 0.12) / 2),
              pw, "bal", 0.006)
    # side rails of the porch
    for sx in (-1, 1):
        B(None, (0.36, 3.2, 0.06), (sx * 7.0, -1.6, RAIL_Z), pw, "sideledge", 0.012)
    # the slate panel on the post by the door, and the digits
    B(None, (0.62, 0.05, 0.74), (1.1, -2.88, DECK + 1.62), P("#3d4652", 0.8), "slate", 0.015)
    B(None, (0.7, 0.03, 0.82), (1.1, -2.9, DECK + 1.62), P("#c9a05a", 0.7), "slateframe", 0.01)
    dm = kit._new(nm("digit"))
    dn = dm.node_tree
    bsdf = dn.nodes["Principled BSDF"]
    bsdf.inputs["Roughness"].default_value = 0.9
    tex = dn.nodes.new("ShaderNodeTexImage")
    gc = dn.nodes.new("ShaderNodeTexCoord")
    dn.links.new(gc.outputs["Generated"], tex.inputs["Vector"])
    dn.links.new(tex.outputs["Color"], bsdf.inputs["Base Color"])
    kit._fogged(dm, bsdf.outputs[0])
    H["digit_tex"] = tex
    H["digit_imgs"] = {}
    H["digit_plane"] = kit.plane(nm("digits"), (0.56, 0.68), (1.1, -2.84, DECK + 1.62), dm, None, rot=(-math.pi / 2, 0, math.pi))
    H["digit_plane"].rotation_euler = (math.pi / 2, 0, math.pi)
    H["digit_plane"].location = (1.1, -2.845, DECK + 1.62)
    # a second panel on the street side so the count reads from the road side of the post too
    # the doormats (outside by the door, inside), the door with its cat flap, the flap's frame and the three strokes
    B(None, (0.96, 0.62, 0.03), (0.5, -0.85, DECK + 0.045), P("#6a4a2a", 0.95, 0.05), "matborder", 0.01)
    B(None, (0.84, 0.5, 0.02), (0.5, -0.85, DECK + 0.07), P("#a37a46", 0.95, 0.05), "mat", 0.01)
    B(None, (0.96, 0.62, 0.03), (0.5, 0.85, DECK + 0.045 + 0.03), P("#6a4a2a", 0.95, 0.05), "imatborder", 0.01)
    B(None, (0.84, 0.5, 0.02), (0.5, 0.85, DECK + 0.1), P("#a37a46", 0.95, 0.05), "imat", 0.01)
    door = P("#5b8def", 0.4)
    dz0, dz1 = DECK, DECK + 2.1
    hx0, hx1, hz0, hz1 = 0.28, 0.72, DECK + 0.10, DECK + 0.62
    B(None, (hx0, 0.08, dz1 - dz0), (hx0 / 2, 0.1, (dz0 + dz1) / 2), door, "doorL", 0.01)
    B(None, (1 - hx1, 0.08, dz1 - dz0), ((1 + hx1) / 2, 0.1, (dz0 + dz1) / 2), door, "doorR", 0.01)
    B(None, (hx1 - hx0, 0.08, dz1 - hz1), (0.5, 0.1, (hz1 + dz1) / 2), door, "doorT", 0.01)
    B(None, (hx1 - hx0, 0.08, hz0 - dz0), (0.5, 0.1, (dz0 + hz0) / 2), door, "doorB", 0.01)
    B(None, (0.07, 0.1, 0.07), (0.88, -0.0, DECK + 1.0), P("#f2c14e", 0.3, 0.8), "knob", 0.02)
    wood = P("#c98d4d", 0.6)
    fw = 0.07
    B(None, (hx1 - hx0 + 2 * fw, 0.035, fw), (0.5, 0.165, hz1 + fw / 2), wood, "fr_t", 0.006)
    B(None, (hx1 - hx0 + 2 * fw, 0.035, fw), (0.5, 0.165, hz0 - fw / 2), wood, "fr_b", 0.006)
    B(None, (fw, 0.035, hz1 - hz0), (hx0 - fw / 2, 0.165, (hz0 + hz1) / 2), wood, "fr_l", 0.006)
    B(None, (fw, 0.035, hz1 - hz0), (hx1 + fw / 2, 0.165, (hz0 + hz1) / 2), wood, "fr_r", 0.006)
    scr = P("#d9791f", 0.5)
    for k, x in enumerate((0.40, 0.47, 0.54, 0.61)):                               # the tally scratches (lore), big
        B(None, (0.026, 0.014, 0.15), (x, 0.152, DECK + 0.86), scr, "stroke", 0.004)
    B(None, (0.30, 0.014, 0.022), (0.505, 0.153, DECK + 0.86), scr, "stroke", 0.004, rot=(0, 0.45, 0))
    H["flap_pivot"] = E(None, (0.5, 0.1, hz1 - 0.01), "flappivot")
    B(H["flap_pivot"], (hx1 - hx0 - 0.02, 0.012, hz1 - hz0 - 0.02), (0, 0.0, -(hz1 - hz0) / 2), P("#5a6270", 0.3, 0.7), "flap", 0.004)
    B(H["flap_pivot"], (hx1 - hx0, 0.016, 0.02), (0, 0.0, -0.005), P("#2d3340", 0.4), "flaptop", 0.004)
    # inside: a hall with a table, a bowl, a coat hook; my room with the bed, a nightstand, the lamp, a rug
    B(None, (0.5, 0.5, 0.05), (1.7, 0.7, DECK + 0.055), P("#ff7a3d", 0.45), "bowlmat", 0.01)
    bowl = E(None, (1.7, 0.7, DECK + 0.08), "bowl")
    kit.cyl(nm("bowlo"), 0.17, 0.09, (0, 0, 0.045), P("#f08a2c", 0.35), bowl, n=20, r2=0.2)
    kit.cyl(nm("bowlf"), 0.15, 0.04, (0, 0, 0.09), P("#8a4a22", 0.85), bowl, n=20)
    H["bowl_food"] = bowl
    try:
        kit.prop("bed_single", (-6.4, 4.7, DECK + 0.03), rot=0, scale=1.25)
        kit.prop("nightstand_1", (-5.55, 6.75, DECK + 0.03), rot=180, scale=1.2)
        kit.prop("light_desk", (-5.55, 6.75, DECK + 0.03 + 0.5), rot=180, scale=1.5, tint="#ffe2a8")
        kit.prop("houseplant_1", (-2.4, 6.5, DECK + 0.03), scale=1.4)
        kit.prop("drawer_1", (-3.4, 6.7, DECK + 0.03), rot=180, scale=1.1)
        kit.prop("couch_medium1", (4.8, 5.4, DECK + 0.03), rot=-90, scale=1.1, tint="#ff9d6a")
        kit.prop("kitchen_fridge", (6.5, 6.4, DECK + 0.03), rot=180, scale=1.0)
    except Exception as ex:   # props are dressing; the set stands without them
        print("props:", ex)
    B(None, (2.6, 1.8, 0.02), (-4.0, 4.2, DECK + 0.045), P("#ff7a5c", 0.9, 0.05), "rug", 0.006)
    B(None, (0.7, 0.06, 1.0), (4.4, 7.05, DECK + 1.9), P("#cfe8ff", 0.6), "kwin", 0.01)
    return H


def build_shelter(kit, ctx):
    y = -96.0
    steel = P("#e8e8f0", 0.4)
    for sx in (-1, 1):
        B(None, (0.12, 0.12, 2.6), (3.2 + sx * 1.4, y, 1.3), steel, "sp", 0.02)
        B(None, (0.12, 0.12, 2.6), (3.2 + sx * 1.4, y + 1.2, 1.3), steel, "sp", 0.02)
    B(None, (3.2, 1.6, 0.12), (3.2, y + 0.6, 2.65), P("#2fb5a8", 0.4), "sroof", 0.03)
    B(None, (3.0, 0.08, 1.9), (3.2, y + 1.25, 1.4), P("#9be0d6", 0.4), "sback", 0.02)
    B(None, (2.4, 0.5, 0.08), (3.2, y + 0.9, 0.5), P("#8a6a4a", 0.7), "sbench", 0.01)
    B(None, (0.56, 0.03, 0.56), (3.2, y + 1.18, 1.62), P("#ffffff", 0.5), "gdisc_bg", 0.05)
    kit.cyl("gdisc", 0.2, 0.02, (3.2, y + 1.15, 1.7), P("#1a1a22", 0.5), None, rot=(math.pi / 2, 0, 0), n=24)
    for dz in (0.0, 0.1):
        B(None, (0.34, 0.02, 0.05), (3.2, y + 1.15, 1.46 + dz), P("#1a1a22", 0.5), "gbar", 0.004)


def build_bus(kit):
    R = E(None, (-1.6, -99.0, 0), "bus")
    B(R, (2.7, 9.5, 2.5), (0, 0, 1.55), P("#ffcf3a", 0.4), "busbody", 0.1)
    B(R, (2.74, 9.0, 0.7), (0, 0, 1.95), P("#2b3a55", 0.2, 0.8), "buswin", 0.04)
    B(R, (2.74, 9.6, 0.18), (0, 0, 0.75), P("#1a1a22", 0.5), "busskirt", 0.03)
    for sy in (-3, 3):
        for sx in (-1, 1):
            kit.cyl(nm("buswheel"), 0.5, 0.3, (sx * 1.3, sy, 0.5), P("#111114", 0.8), R, rot=(0, math.pi / 2, 0), n=14)
    return R


def build_car(kit):
    R = E(None, (-1.7, -12.5, 0), "car")
    B(R, (1.9, 4.4, 0.8), (0, 0, 0.75), P("#e8503a", 0.3, 0.7), "carbody", 0.12)
    B(R, (1.7, 2.3, 0.7), (0, 0.2, 1.45), P("#e8503a", 0.3, 0.7), "carcab", 0.14)
    B(R, (1.74, 1.9, 0.5), (0, 0.2, 1.48), P("#2b3a55", 0.1, 0.9), "carwin", 0.08)
    for sy in (-1.4, 1.4):
        for sx in (-1, 1):
            kit.cyl(nm("carwheel"), 0.38, 0.28, (sx * 0.92, sy, 0.38), P("#111114", 0.8), R, rot=(0, math.pi / 2, 0), n=14)
    cr = B(R, (0.5, 0.36, 0.34), (0, 1.2, 1.38), P("#9aa3b2", 0.5), "carrier_in", 0.04)
    return R


def build_props(kit):
    pr = {}
    # the cat carrier (with a grille), a trash bag, the mug
    c = E(None, (0, 0, 0), "carrier")
    blue = P("#3b82f6", 0.45)
    B(c, (0.46, 0.66, 0.04), (0, 0, 0.02), blue, "cbase", 0.01)
    B(c, (0.46, 0.66, 0.04), (0, 0, 0.5), blue, "croof", 0.01)
    for sx in (-1, 1):
        B(c, (0.03, 0.66, 0.44), (sx * 0.215, 0, 0.26), blue, "cside", 0.008)
    B(c, (0.46, 0.03, 0.44), (0, 0.315, 0.26), blue, "cback", 0.008)
    for z in (0.065, 0.455):
        B(c, (0.46, 0.03, 0.04), (0, -0.315, z), blue, "cbar", 0.008)
    for i in range(8):
        B(c, (0.014, 0.025, 0.4), (-0.18 + i * 0.0514, -0.318, 0.26), P("#eef0f6", 0.4), "grille", 0.003)
    B(c, (0.22, 0.05, 0.05), (0, 0, 0.55), P("#1c4fb8", 0.45), "carrierhandle", 0.015)
    hide(c, True)
    pr["carrier"] = c
    bag = E(None, (0, 0, 0), "bag")
    B(bag, (0.7, 0.6, 0.8), (0, 0, 0.4), P("#1b1b22", 0.2, 0.7), "bagbody", 0.18)
    B(bag, (0.2, 0.2, 0.18), (0, 0, 0.88), P("#1b1b22", 0.2, 0.7), "bagtop", 0.08)
    hide(bag, True)
    pr["bag"] = bag
    return pr


# ------------------------------------------------------------------------------------------------ animate
def cue_at(tl, name, t):
    out = {}
    for c in tl.get("cues", []):
        if c["name"] == name and c["t"] <= t + 1e-9:
            out = c
    return out


def digit_image(n, kit):
    from PIL import Image, ImageDraw, ImageFont

    p = TMP / f"digit-{n}.png"
    if not p.exists():
        im = Image.new("RGB", (280, 340), hexrgb("#3d4652"))
        d = ImageDraw.Draw(im)
        try:
            f = ImageFont.truetype("DejaVuSans-Bold.ttf", 220 if n < 10 else 170)
        except Exception:
            f = ImageFont.load_default()
        txt = str(n)
        bb = d.textbbox((0, 0), txt, font=f)
        d.text(((280 - (bb[2] - bb[0])) / 2 - bb[0] + 3, (340 - (bb[3] - bb[1])) / 2 - bb[1]), txt, fill=hexrgb("#f2f2ee"), font=f)
        # chalk smudge: a faint rubbed rim
        for i in range(60):
            x, y = (i * 53) % 280, (i * 97) % 340
            d.ellipse([x, y, x + 6, y + 3], fill=hexrgb("#4a5564"))
        im.save(p)
    return str(p)


def look_at(ctx, tl, t):
    shots = tl["shots"]
    cur = next((s for s in shots if s["start"] <= t < s["end"]), shots[-1])
    i = shots.index(cur)
    A = LOOKS[ctx["shots"][cur["id"]].get("look", "sundown")]
    if i + 1 < len(shots) and t > cur["end"] - 0.35:
        nb = LOOKS[ctx["shots"][shots[i + 1]["id"]].get("look", "sundown")]
        if nb is not A:
            return mix_look(A, nb, ss((t - (cur["end"] - 0.35)) / 0.35)), cur
    return mix_look(A, A, 0.0), cur


def animate(kit, story, tl, t, ctx):
    if not ctx["late"]:
        strider_late(kit, ctx)
        ctx["late"] = True
    sc = bpy.context.scene
    L, cur = look_at(ctx, tl, t)
    sd = ctx["shots"][cur["id"]]
    # ---- sky and light
    r = ctx["ramp"].color_ramp.elements
    for el, c in zip(r, L["sky"]):
        el.color = (kit.srgb(c[0]), kit.srgb(c[1]), kit.srgb(c[2]), 1.0)
    ctx["bg"].inputs["Strength"].default_value = L["world"]
    az, el_, en, _, scol = L["sun"]
    azr, elr = math.radians(az), math.radians(el_)
    pos = V((math.sin(azr) * math.cos(elr), -math.cos(azr) * math.cos(elr), math.sin(elr)))
    sun = ctx["sun"]
    sun.rotation_euler = (-pos).to_track_quat("-Z", "Y").to_euler()
    sun.data.color = (kit.srgb(scol[0]), kit.srgb(scol[1]), kit.srgb(scol[2]))
    cl, _, cl_lens, _ = bl_story.cam_at(sd, cur, t, {}, tl)
    cam = kit.OBJ["cam"]
    ctx["fill"].location = (cl[0], cl[1], cl[2])
    sc.view_settings.exposure = L["exp"] + sd.get("exp", 0.0)
    ov = {"sun": en * sd.get("sun", 1.0) / 5.0, "camfill": L["fill"] * sd.get("fill", 1.0), "hall": L["hall"], "roomlight": L["room"], "lamp": L["lamp"],
          "winlight": L["win"], "winkey": L["lamp"] * sd.get("key", 0.0), "rimout": L["lamp"] * sd.get("rim", 0.0), "porchfill": sd.get("porch", 0.0)}
    for k in range(8):
        ov[f"street{k}"] = L["street"] * sd.get("street", 1.0)
    # ---- camera depth of field per shot: [focus distance m, f-stop]
    dof = sd.get("dof")
    cd = cam.data
    if dof:
        cd.dof.use_dof = True
        cd.dof.focus_distance = dof[0]
        cd.dof.aperture_fstop = dof[1]
    else:
        cd.dof.use_dof = False
    # ---- the count: pairs on the rail and the digit on the slate
    cnt = cue_at(tl, "count", t).get("n", 8)
    for i, pr in enumerate(ctx["rail"]):
        hide(pr, i >= cnt)
    H = ctx["house"]
    if cnt not in H["digit_imgs"]:
        im = bpy.data.images.load(digit_image(cnt, kit))
        im.colorspace_settings.name = "sRGB"
        H["digit_imgs"][cnt] = im
    H["digit_tex"].image = H["digit_imgs"][cnt]
    place_inset(kit, ctx, cnt, cl_lens)
    # ---- named pairs and steam
    pc = cue_at(tl, "pairs", t)
    steam_sites = []
    for key, pr in ctx["named"].items():
        spec = pc.get(key)
        if not spec:
            hide(pr, True)
            continue
        hide(pr, False)
        pr.location = tuple(spec["pos"])
        pr.rotation_euler = (0, 0, math.radians(spec.get("yaw", 0)))
        s = spec.get("scale", 1.0)
        pr.scale = (s, s, s)
        if spec.get("steam"):
            steam_sites.append((spec["pos"], s))
        if key == "tap":                                    # the tap shoe's left toe rocks twice
            tp = cue_at(tl, "tap", t)
            Lsh = bpy.data.objects.get(pr["L"])
            rk = 0.0
            if tp and "t" in tp:
                u = t - tp["t"]
                if 0 <= u < 0.9:
                    rk = max(0.0, math.sin(u * 2 * math.pi / 0.45)) * 0.28
            if Lsh:
                Lsh.rotation_euler = (-rk, 0, 0)
                Lsh.location = (-0.085, 0, 0.0)
    for si, site in enumerate(ctx["steam"]):
        for j, o in enumerate(site):
            if si >= len(steam_sites):
                o.hide_render = True
                continue
            (px, py, pz), sc_ = steam_sites[si]
            ph = ((t * 0.6 + j / len(site) + si * 0.31) % 1.0)
            env = math.sin(math.pi * ph) ** 0.9
            o.hide_render = False
            sw = 0.035 * math.sin(j * 2.1 + t * 1.6 + ph * 5.0)
            o.location = (px + 0.05 * math.sin(j * 1.9) + sw, py + 0.04 * math.cos(j * 1.7) + 0.5 * sw,
                          pz + 0.06 + 0.5 * ph * sc_ ** 0.3)
            o.scale = (0.4 * env + 0.001, 0.4 * env + 0.001, (2.0 + 1.6 * ph) * env + 0.001)
    # ---- Biscuit
    cc = cue_at(tl, "cat", t)
    cat = ctx["cat"]
    if cc and not cc.get("hidden"):
        pos_ = cc["pos"]
        if "to" in cc:                                       # a move: pos -> to over t0..t1
            u = ss((t - cc["t"]) / max(1e-3, cc["dur"]))
            pos_ = [lerp(a, b, u) for a, b in zip(cc["pos"], cc["to"])]
        cat.place(pos_[0], pos_[1], pos_[2], cc.get("yaw", 0), cc.get("pose", "stand"), cc.get("face", "neutral"),
                  cc.get("tail", "up"), t, cc.get("pitch", 0.0), False, cc.get("carry"))
    else:
        cat.place(0, 0, -5, 0, hidden=True)
    # ---- the flap swings with the times in its cue ("swing": list of [t0, dur, peak])
    ang = 0.0
    for c in tl.get("cues", []):
        if c["name"] == "flapswing":
            u = t - c["t"]
            if 0 <= u < c["dur"]:
                ang = max(ang, c["peak"] * math.exp(-3.0 * u / c["dur"]) * abs(math.cos(u * 9.0)))
    H["flap_pivot"].rotation_euler = (-ang, 0, 0)
    # ---- the Strider: shoes, the slow blink, the tail
    sd_ = cue_at(tl, "strider", t)
    for kind, lst in ctx["sshoes"].items():
        for o in lst:
            o.hide_render = sd_.get("shoes") != kind
    ch = ctx.get("strider")
    if ch is not None:
        bl = 1.0
        bc = cue_at(tl, "blink", t)
        if bc:
            u = (t - bc["t"]) / bc["dur"]
            if 0 <= u <= 1:
                bl = 1 - math.sin(math.pi * u) ** 0.8 * 0.93
        sq = sd_.get("sq", 1.0)
        sc0 = 1.5 * 0.34
        ch.root.scale = (sc0 * 0.82, sc0, sc0 * sq)
        for e in ctx["eyes"]:
            e.scale = (1, 1, max(0.07, bl))
        late_ = t >= ctx["reveal_t"]
        for nd in ctx["glow"].node_tree.nodes:
            if nd.type == "EMISSION":
                c_ = (0.18, 0.88, 0.48, 1.0) if late_ else (0.8, 0.86, 0.82, 1.0)
                nd.inputs["Color"].default_value = c_
                nd.inputs["Strength"].default_value = 1.6 if late_ else 0.9
    # ---- props (carrier, bag), the bus, the car, the trash can's lid
    pp = cue_at(tl, "props", t)
    for k, o in ctx["props"].items():
        s = pp.get(k)
        if not s:
            hide(o, True)
            continue
        hide(o, False)
        o.location = tuple(s["pos"])
        o.rotation_euler = (0, 0, math.radians(s.get("yaw", 0)))
        sc_ = s.get("scale", 1.0)
        o.scale = (sc_, sc_, sc_)
    bs = cue_at(tl, "bus", t)
    hide(ctx["bus"], not bs.get("on"))
    if bs.get("on"):
        u = ss((t - bs["t"]) / bs["dur"]) if bs.get("go") else 0.0
        ctx["bus"].location = (-1.6, lerp(-99.0, -128.0, u), 0)
    cs = cue_at(tl, "car", t)
    hide(ctx["car"], not cs.get("on"))
    if cs.get("on"):
        u = ss((t - cs["t"]) / cs["dur"]) if cs.get("go") else 0.0
        ctx["car"].location = (-1.7, lerp(-12.5, -48.0, u), 0)
    hide(ctx["trash_lid"], not cue_at(tl, "lid", t).get("on", True))
    hr = cue_at(tl, "hide_rail", t).get("idx", [])
    for i in hr:
        hide(ctx["rail"][i], True)
    return ov


# ------------------------------------------------------------------------------------------------ the rule meter inset
def build_inset(kit, ctx):
    """A small chalk-count panel glued to the camera, top left, so the meter is in every shot."""
    cam = kit.OBJ["cam"]
    m = kit._new(nm("inset"))
    nt = m.node_tree
    nt.nodes.remove(nt.nodes["Principled BSDF"])
    tex = nt.nodes.new("ShaderNodeTexImage")
    gc = nt.nodes.new("ShaderNodeTexCoord")
    em = nt.nodes.new("ShaderNodeEmission")
    em.inputs["Strength"].default_value = 0.85
    nt.links.new(gc.outputs["Generated"], tex.inputs["Vector"])
    nt.links.new(tex.outputs["Color"], em.inputs["Color"])
    out = next(n for n in nt.nodes if n.type == "OUTPUT_MATERIAL")
    nt.links.new(em.outputs[0], out.inputs["Surface"])
    pl = kit.plane(nm("inset"), (1.0, 1.0), (0, 0, -0.15), m, cam)
    fr = kit.plane(nm("insetframe"), (1.0, 1.0), (0, 0, -0.1515), kit.emit("#e0b050", 0.9, name="insetframe"), cam)
    for o in (pl, fr):
        no_shadow(o)
    ctx["inset"] = (pl, fr, tex)
    ctx["inset_imgs"] = {}


def place_inset(kit, ctx, cnt, lens):
    pl, fr, tex = ctx["inset"]
    if cnt not in ctx["inset_imgs"]:
        im = bpy.data.images.load(digit_image(cnt, kit))
        im.colorspace_settings.name = "sRGB"
        ctx["inset_imgs"][cnt] = im
    tex.image = ctx["inset_imgs"][cnt]
    d = 0.15
    unit = d / lens                       # metres per mm of sensor at the panel's distance
    pw = 0.17 * 13.5 * unit
    ph = pw * 340 / 280
    x = -0.70 * 6.75 * unit
    y = 0.74 * 12.0 * unit
    pl.location, pl.scale = (x, y, -d), (pw, ph, 1)
    fr.location, fr.scale = (x, y, -d - 0.0015), (pw * 1.1, ph * 1.08, 1)
