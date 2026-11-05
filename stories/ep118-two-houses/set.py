"""ep118-two-houses: a steep little street of narrow painted houses that lean toward whoever they feud with.

Built from kit.py's parts (no text anywhere; the only marks are the glyph-and-numeral tag on the camera).
Metres, z up, the houses face -y (the camera's street is at -y). Our house (butter yellow) is on the left, Mr. Pruitt's
(sky blue) on the right; between them a 1.6 m gap and a hedge. Each house is a root empty pivoting on its INNER bottom
edge (x -0.8 for ours, +0.8 for his) and leaning toward the gap by `deg` degrees. Local coordinates: `ux` is the
distance outward from the inner edge, y is depth from the front face, z is height.

Cues (story.json "cues"): lean (name, deg, dur), tag (v), sash (the hall window), marble, frames (the crook), fx.
Shot fields set.py reads: look (day|night), fill, hl (our hall lamp), pl (his lamp), kl (kitchen), pk (porch lamps), exp.
"""

from __future__ import annotations

import math
import tempfile
from pathlib import Path

import bpy
from mathutils import Vector as V

from blocky import bl_story, faces, rig

TMP = Path(tempfile.mkdtemp(prefix="twohouses-"))
W, D = 3.6, 4.6          # a house's width and depth
WALL_H = 5.4             # wall top
FLOOR2 = 3.0             # the hall floor (top)
FLOOR1 = 0.08            # the kitchen floor (top)
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


class K:
    kit = None


def P(hexc, rough=0.45, spec=0.4):
    return K.kit.plastic(hexc, rough, spec=spec)


def B(parent, size, loc, mat, name="b", bevel=0.01, rot=(0, 0, 0)):
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


def glow_mat(kit, hexc):
    """An emissive material of its own (so its strength can change per frame)."""
    m = kit._new(nm("glow"))
    nt = m.node_tree
    nt.nodes.remove(nt.nodes["Principled BSDF"])
    e = nt.nodes.new("ShaderNodeEmission")
    e.inputs["Color"].default_value = kit.col(hexc)
    e.inputs["Strength"].default_value = 3.0
    nt.links.new(e.outputs[0], next(n for n in nt.nodes if n.type == "OUTPUT_MATERIAL").inputs["Surface"])
    return m, e


def clear_pane(kit):
    pane = kit._new(nm("pane"))
    nt = pane.node_tree
    nt.nodes.remove(nt.nodes["Principled BSDF"])
    tr = nt.nodes.new("ShaderNodeBsdfTransparent")
    gl = nt.nodes.new("ShaderNodeBsdfGlossy")
    gl.inputs["Roughness"].default_value = 0.05
    gl.inputs["Color"].default_value = (0.8, 0.9, 1.0, 1)
    mx = nt.nodes.new("ShaderNodeMixShader")
    mx.inputs["Fac"].default_value = 0.06
    nt.links.new(tr.outputs[0], mx.inputs[1])
    nt.links.new(gl.outputs[0], mx.inputs[2])
    nt.links.new(mx.outputs[0], next(n for n in nt.nodes if n.type == "OUTPUT_MATERIAL").inputs["Surface"])
    return pane


# ------------------------------------------------------------------------------------------------ a house
class House:
    """A narrow painted house. detail=True: a real shell with openings, floors and rooms. sgn +1 leans to +x (pivot at
    its inner edge px), -1 leans to -x. axis 'x': leans toward +y about the front-bottom edge (the house across the
    street, yaw 180)."""

    def __init__(self, kit, name, sgn, px, py, wall, trim, roof, detail=False, door="#d7503a", holes=None,
                 axis="y", yaw=0.0, floor=None, interior=None, nwin=(2, 2), gap_inner=True):
        self.kit, self.name, self.sgn, self.axis, self.yaw = kit, name, sgn, axis, yaw
        self.px, self.py = px, py
        self.root = E(None, (px, py, 0), name, rot=(0, 0, yaw))
        self.deg = 0.0
        self.walls = []
        r = self.root
        wm, tm, rm = P(wall, 0.7, 0.15), P(trim, 0.5), P(roof, 0.6)
        im = P(interior or wall, 0.8, 0.1)
        self.wm, self.tm, self.im = wm, tm, im
        # the stone plinth under the lean
        self.b(r, (0, W), (0, D), (-0.95, 0.0), P("#9a9aa6", 0.9, 0.05), "plinth", 0.0)
        # front wall (y 0..0.2), back wall, inner and outer side walls
        self.fhole = (holes or {}).get("front", [])
        self.shole = (holes or {}).get("side", [])
        self.wall_front(wm)
        self.b(r, (0, W), (D - 0.2, D), (0, WALL_H), wm, "back", 0.0)
        self.b(r, (0, 0.2), (0.2, D - 0.2), (0, WALL_H), wm, "sidein", 0.0)
        self.wall_side(wm)
        if detail:
            fm = kit.checker("#f4ecd8", "#bfe0e8", 0.5) if floor is None else floor[0]
            self.b(r, (0.2, W - 0.2), (0.2, D - 0.2), (0.0, FLOOR1), fm, "floor1", 0.0)
            pm = kit.planks("#c8935a", "#a8743f", 1.0, "Y") if floor is None else floor[1]
            self.b(r, (0.2, W - 0.2), (0.2, D - 0.2), (FLOOR2 - 0.2, FLOOR2), pm, "floor2", 0.0)
            self.b(r, (0.2, W - 0.2), (0.2, D - 0.2), (WALL_H, WALL_H + 0.1), im, "ceil", 0.0)
        else:
            self.b(r, (0.2, W - 0.2), (0.2, D - 0.2), (WALL_H, WALL_H + 0.1), im, "ceil", 0.0)
        self.roof(rm, tm)

    # -- geometry in house-local ux/y/z (lx = -sgn * ux)
    def b(self, parent, ux, y, z, mat, name="b", bevel=0.01):
        ux0, ux1 = ux
        y0, y1 = y
        z0, z1 = z
        lx = -self.sgn * (ux0 + ux1) / 2
        return B(parent, (ux1 - ux0, y1 - y0, z1 - z0), (lx, (y0 + y1) / 2, (z0 + z1) / 2), mat, name, bevel)

    def cut(self, a0, a1, z0, z1, holes):
        """Pieces of a wall rectangle a0..a1 x z0..z1 with holes [(h0, h1, hz0, hz1), ...] (they may share columns)."""
        edges = sorted({a0, a1} | {min(max(h[0], a0), a1) for h in holes} | {min(max(h[1], a0), a1) for h in holes})
        for lo, hi in zip(edges, edges[1:]):
            if hi - lo < 1e-6:
                continue
            cuts = sorted((h[2], h[3]) for h in holes if h[0] <= lo + 1e-9 and h[1] >= hi - 1e-9)
            cur = z0
            for c0, c1 in cuts:
                if c0 > cur:
                    yield lo, hi, cur, c0
                cur = max(cur, c1)
            if cur < z1:
                yield lo, hi, cur, z1

    def wall_front(self, mat):
        for a0, a1, z0, z1 in self.cut(0, W, 0, WALL_H, [(h[0], h[1], h[2], h[3]) for h in self.fhole]):
            self.walls.append(self.b(self.root, (a0, a1), (0, 0.2), (z0, z1), mat, "front", 0.0))

    def wall_side(self, mat):
        for a0, a1, z0, z1 in self.cut(0.2, D, 0, WALL_H, [(h[0], h[1], h[2], h[3]) for h in self.shole]):
            self.walls.append(self.b(self.root, (W - 0.2, W), (a0, a1), (z0, z1), mat, "sideout", 0.0))
        if not self.shole:
            pass

    def frame(self, ux0, ux1, z0, z1, mat=None, on="front", y=None, sill=True):
        """A white window frame around an opening, 4 cm proud of the wall."""
        mat = mat or self.tm
        f = 0.07
        if on == "front":
            yy = (-0.04, 0.02)
            self.b(self.root, (ux0 - f, ux1 + f), yy, (z1, z1 + f), mat, "wtop", 0.01)
            self.b(self.root, (ux0 - f, ux1 + f), yy, (z0 - f, z0), mat, "wbot", 0.01)
            self.b(self.root, (ux0 - f, ux0), yy, (z0, z1), mat, "wl", 0.01)
            self.b(self.root, (ux1, ux1 + f), yy, (z0, z1), mat, "wr", 0.01)
            if sill:
                self.b(self.root, (ux0 - 0.12, ux1 + 0.12), (-0.16, 0.0), (z0 - 0.1, z0 - f + 0.01), mat, "sill", 0.015)
        else:   # on the outer side wall: ux = W face, coordinates ux0..ux1 are y
            ox = (W - 0.02, W + 0.04)
            self.b(self.root, ox, (ux0 - f, ux1 + f), (z1, z1 + f), mat, "wtop", 0.01)
            self.b(self.root, ox, (ux0 - f, ux1 + f), (z0 - f, z0), mat, "wbot", 0.01)
            self.b(self.root, ox, (ux0 - f, ux0), (z0, z1), mat, "wl", 0.01)
            self.b(self.root, ox, (ux1, ux1 + f), (z0, z1), mat, "wr", 0.01)
            if sill:
                self.b(self.root, (W - 0.2, W + 0.16), (ux0 - 0.1, ux1 + 0.1), (z0 - 0.1, z0 - f + 0.01), mat, "sill", 0.015)

    def roof(self, rm, tm):
        r = self.root
        alpha = math.radians(33)
        rise = (W / 2) * math.tan(alpha)
        lx_r = -self.sgn * W / 2
        slab_w = (W / 2) / math.cos(alpha)
        for s in (-1, 1):
            cx = lx_r + s * (W / 4)
            B(r, (slab_w + (0.0 if (s * -self.sgn) > 0 else 0.0), D + 0.45, 0.12),
              (cx, D / 2 - 0.12, WALL_H + rise / 2 + 0.06), rm, "roof", 0.02, rot=(0, s * alpha, 0))
        B(r, (0.22, D + 0.5, 0.16), (lx_r, D / 2 - 0.12, WALL_H + rise + 0.07), tm, "ridge", 0.03)
        for yy in (0.04, D - 0.04):
            self.kit.mesh_obj(nm("gable"), [(lx_r - W / 2, yy, WALL_H), (lx_r + W / 2, yy, WALL_H),
                                           (lx_r, yy, WALL_H + rise)], [(0, 1, 2)], self.wm, r)
        self.rise = rise

    def fake_windows(self, pane="#3a5a8a"):
        """Painted windows for a house with no rooms: frames + dark panes proud of the front wall."""
        pm = P(pane, 0.25, 0.7)
        for ux0, z0 in ((0.45, 1.2), (2.25, 1.2), (0.45, 3.7), (2.25, 3.7)):
            self.b(self.root, (ux0 - 0.07, ux0 + 0.9 + 0.07), (-0.04, 0.0), (z0 - 0.07, z0 + 1.1 + 0.07), self.tm, "fwf", 0.01)
            self.b(self.root, (ux0, ux0 + 0.9), (-0.06, 0.0), (z0, z0 + 1.1), pm, "fwp", 0.01)
            self.b(self.root, (ux0 + 0.43, ux0 + 0.47), (-0.08, 0.0), (z0, z0 + 1.1), self.tm, "fwm", 0.005)

    def door_slab(self, ux0, ux1, mat):
        self.b(self.root, (ux0, ux1), (0.05, 0.12), (0.0, 2.1), mat, "door", 0.015)
        self.b(self.root, (ux0 - 0.07, ux1 + 0.07), (-0.04, 0.02), (2.1, 2.17), self.tm, "dtop", 0.01)
        self.b(self.root, (ux0 - 0.07, ux0), (-0.04, 0.02), (0.0, 2.1), self.tm, "dl", 0.01)
        self.b(self.root, (ux1, ux1 + 0.07), (-0.04, 0.02), (0.0, 2.1), self.tm, "dr", 0.01)
        self.b(self.root, (ux0 - 0.3, ux1 + 0.3), (-0.7, 0.0), (0.0, 0.1), P("#cfc8bc", 0.8), "step", 0.01)

    def apply(self, deg):
        self.deg = deg
        if self.axis == "y":
            self.root.rotation_euler = (0, self.sgn * math.radians(deg), self.yaw)
        else:
            self.root.rotation_euler = (math.radians(deg), 0, self.yaw)


# ------------------------------------------------------------------------------------------------ small things
def mug(kit, parent, loc, color, name="mug", rot=(0, 0, 0), scale=1.4):
    """A hollow mug: ring wall + floor, a handle. Returns (root, inner_radius, floor_z, rim_z)."""
    r = E(parent, loc, name, rot=rot)
    R, h, t = 0.045 * scale, 0.10 * scale, 0.008 * scale
    m = P(color, 0.35, 0.5)
    n = 18
    verts, fcs = [], []
    for z, rr in ((0, R), (h, R), (h, R - t), (0.012 * scale, R - t)):
        for i in range(n):
            a = 2 * math.pi * i / n
            verts.append((rr * math.cos(a), rr * math.sin(a), z))
    verts.append((0, 0, 0))
    verts.append((0, 0, 0.012 * scale))
    for ring in range(3):
        for i in range(n):
            j = (i + 1) % n
            fcs.append((ring * n + i, ring * n + j, (ring + 1) * n + j, (ring + 1) * n + i))
    for i in range(n):
        j = (i + 1) % n
        fcs.append((j, i, 4 * n))
        fcs.append((3 * n + i, 3 * n + j, 4 * n + 1))
    o = kit.mesh_obj(nm("mugbody"), verts, fcs, m, r, smooth=True)
    for p in o.data.polygons:
        p.use_smooth = True
    hd = B(r, (0.012 * scale, 0.05 * scale, 0.07 * scale), (R + 0.012 * scale, 0, h * 0.5), m, "handle", 0.004)
    B(r, (0.012 * scale, 0.05 * scale, 0.012 * scale), (R + 0.005 * scale, 0, h * 0.85), m, "handle", 0.003)
    B(r, (0.012 * scale, 0.05 * scale, 0.012 * scale), (R + 0.005 * scale, 0, h * 0.2), m, "handle", 0.003)
    return r


def coffee_disc(kit, r_in):
    c = kit.cyl(nm("coffee"), r_in * 0.97, 0.006, (0, 0, -9), P("#3a1c0c", 0.25, 0.7), None, n=24)
    no_shadow(c)
    return c


def note_image(path, w=300, h=380):
    from PIL import Image, ImageDraw
    im = Image.new("RGB", (w, h), hexrgb("#fff7d6"))
    d = ImageDraw.Draw(im)
    for i in range(8):                       # scribble lines (nothing readable)
        y = 40 + i * 28
        x = 30
        pts = []
        while x < w - 40 - (i % 3) * 30:
            pts.append((x, y + (8 if (x // 14) % 2 else -8)))
            x += 14
        d.line(pts, fill=hexrgb("#33384a"), width=5)
    fx, fy = 150, 322                        # the little fish
    d.ellipse([fx - 62, fy - 26, fx + 42, fy + 26], outline=hexrgb("#2a5fd8"), width=7)
    d.polygon([(fx + 38, fy), (fx + 82, fy - 28), (fx + 82, fy + 28)], outline=hexrgb("#2a5fd8"), fill=hexrgb("#2a5fd8"))
    d.ellipse([fx - 40, fy - 10, fx - 28, fy + 2], fill=hexrgb("#2a5fd8"))
    im.save(path)
    return str(path)


def tag_image(v, path, w=280, h=340):
    """The rule meter: a cream tag, a tilted-house glyph and the lean. v 'a': 11. v 'b': plus the street's house at 1."""
    from PIL import Image, ImageDraw, ImageFont
    im = Image.new("RGB", (w, h), hexrgb("#fff1c9"))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([6, 6, w - 7, h - 7], 26, outline=hexrgb("#2a2430"), width=10)
    try:
        f = ImageFont.truetype("DejaVuSans-Bold.ttf", 150 if v == "a" else 120)
        f2 = ImageFont.truetype("DejaVuSans-Bold.ttf", 88)
    except Exception:
        f = f2 = ImageFont.load_default()

    def house(cx, cy, s, lean, col):
        # a tilted house: a sheared box + a roof triangle
        def sh(x, y):
            return (cx + x * s + (-y) * lean * s, cy + y * s)
        body = [sh(-0.5, 0.0), sh(0.5, 0.0), sh(0.5, -0.9), sh(-0.5, -0.9)]
        roof = [sh(-0.62, -0.9), sh(0.62, -0.9), sh(0.0, -1.5)]
        d.polygon(body, fill=hexrgb(col), outline=hexrgb("#2a2430"))
        d.polygon(roof, fill=hexrgb("#d9503a"), outline=hexrgb("#2a2430"))
        d.line(body + [body[0]], fill=hexrgb("#2a2430"), width=7)
        d.line(roof + [roof[0]], fill=hexrgb("#2a2430"), width=7)
        d.rectangle([min(sh(-0.15, -0.5)[0], sh(0.15, -0.2)[0]), sh(0, -0.5)[1], max(sh(-0.15, -0.5)[0], sh(0.15, -0.2)[0]), sh(0, -0.2)[1]], fill=hexrgb("#7ec8ff"))
    if v == "a":
        house(120, 150, 100, 0.42, "#ffd86b")
        d.line([(205, 60), (250, 40), (250, 150), (205, 150)], fill=hexrgb("#2a2430"), width=1)
        txt = "11"
        bb = d.textbbox((0, 0), txt, font=f)
        d.text(((w - (bb[2] - bb[0])) / 2 - bb[0], 205 - bb[1]), txt, fill=hexrgb("#2a2430"), font=f)
    else:
        house(90, 130, 70, 0.42, "#ffd86b")
        house(205, 130, 70, -0.36, "#8fe0b0")
        bb = d.textbbox((0, 0), "11", font=f2)
        d.text((22 - bb[0], 190 - bb[1]), "11", fill=hexrgb("#2a2430"), font=f2)
        bb = d.textbbox((0, 0), "1", font=f2)
        d.text((190 - bb[0], 190 - bb[1]), "1", fill=hexrgb("#2a2430"), font=f2)
        d.line([(30, 290), (250, 290)], fill=hexrgb("#2a2430"), width=8)
        for x in range(30, 251, 44):
            d.line([(x, 275), (x, 305)], fill=hexrgb("#2a2430"), width=7)
    im.save(path)
    return str(path)


# ------------------------------------------------------------------------------------------------ looks
# per-look floats; a shot may override any of them by name. sky: horizon, low, mid, zenith.
LOOKS = {
    "day": {"sky": ["#d8f0ff", "#b4e0ff", "#86c8ff", "#5aa4f2"], "world": 1.0, "sun": 4.6, "sunc": "#fff1d8", "az": 60, "el": 48,
            "fill": 0.45, "hl": 0.55, "pl": 0.55, "kl": 0.9, "pk": 0.0, "exp": 0.0, "tsun": 1.0},
    "night": {"sky": ["#3b5894", "#2a4078", "#1d2f5e", "#101c40"], "world": 0.55, "sun": 1.5, "sunc": "#9db4ff", "az": 25, "el": 38,
              "fill": 1.0, "hl": 1.0, "pl": 1.0, "kl": 1.0, "pk": 1.0, "exp": 0.55, "tsun": 1.0},
}


def mixhex(a, b, u):
    ra, rb = hexrgb(a), hexrgb(b)
    return tuple(lerp(x, y, u) / 255.0 for x, y in zip(ra, rb))


def params(sd, name_look):
    L = dict(LOOKS[name_look])
    for k in ("fill", "hl", "pl", "kl", "pk", "exp"):
        if k in sd:
            L[k] = sd[k]
    return L


def look_at(ctx, tl, t):
    shots = tl["shots"]
    cur = next((s for s in shots if s["start"] <= t < s["end"]), shots[-1])
    i = shots.index(cur)
    sa = ctx["shots"][cur["id"]]
    A = params(sa, sa.get("look", "day"))
    if i + 1 < len(shots) and t > cur["end"] - 0.35:
        sb = ctx["shots"][shots[i + 1]["id"]]
        Bp = params(sb, sb.get("look", "day"))
        u = ss((t - (cur["end"] - 0.35)) / 0.35)
        out = {}
        for k, va in A.items():
            vb = Bp[k]
            if k == "sky":
                out[k] = [mixhex(x, y, u) for x, y in zip(va, vb)]
            elif k == "sunc":
                out[k] = va if u < 0.5 else vb
            else:
                out[k] = lerp(va, vb, u)
        out["sky_hex"] = False
        return out, cur
    A = dict(A)
    A["sky"] = [mixhex(x, x, 0) for x in A["sky"]]
    return A, cur


def cue_at(tl, name, t):
    out = {}
    for c in tl.get("cues", []):
        if c["name"] == name and c["t"] <= t + 1e-9:
            out = c
    return out


def lean_val(tl, name, t, base=0.0):
    """A lean in degrees at t: each cue {who, deg, dur} eases from the last value to deg over dur."""
    v = base
    for c in tl.get("cues", []):
        if c["name"] != "lean" or c["who"] != name:
            continue
        if c["t"] > t + 1e-9:
            break
        u = ss((t - c["t"]) / max(1e-3, c.get("dur", 0.01)))
        if u >= 1:
            v = c["deg"]
        else:
            v = lerp(v, c["deg"], u)
            break
    return v


# ------------------------------------------------------------------------------------------------ build
def build(kit, story, tl):
    K.kit = kit
    ctx = {"story": story, "shots": {s["id"]: s for s in story["shots"]}}
    sc = bpy.context.scene

    # ---- sky gradient
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
    ramp.color_ramp.elements.new(0.22)
    ramp.color_ramp.elements.new(0.55)
    nt.links.new(mr.outputs["Result"], ramp.inputs["Fac"])
    nt.links.new(ramp.outputs["Color"], bg.inputs["Color"])
    ctx["ramp"], ctx["bg"] = ramp, bg

    # ---- lights
    ctx["sun"] = kit.light("sun", "SUN", (0, 0, 50), 4.6, "#fff1d8", size=0.1)
    ctx["sun"].data.angle = 0.06
    ctx["fill"] = kit.light("camfill", "POINT", (0, 0, 2), 70, "#ffeede", size=0.6, shadow=False)

    # ---- ground, street
    B(None, (400, 300, 0.4), (0, -60, -0.2), P("#6cc24a", 0.85, 0.1), "lawn", 0.0)
    B(None, (400, 7.0, 0.1), (0, -11.1, 0.03), kit.texture("asphalt", 0.4, tint="#b4bccb"), "road", 0.0)
    for k in range(-30, 31):
        B(None, (1.4, 0.14, 0.02), (k * 3.2, -11.1, 0.1), P("#ffd23a", 0.6), "dash", 0.0)
    for y0 in (-7.0, -15.0):
        B(None, (400, 1.8, 0.14), (0, y0 + (0.0 if y0 > -10 else 0.0), 0.07), P("#d6d2c8", 0.8, 0.1), "walk", 0.0)
    B(None, (400, 0.3, 0.2), (0, -7.95, 0.1), P("#b7b2a8", 0.8), "curb", 0.0)
    B(None, (400, 0.3, 0.2), (0, -14.25, 0.1), P("#b7b2a8", 0.8), "curb", 0.0)
    B(None, (400, 0.3, 0.3), (0, 0, -0.0), P("#6cc24a", 0.8), "lip", 0.0) if False else None

    # ---- the cast of houses
    detail_ours = dict(holes={
        "front": [(2.5, 3.4, 0.0, 2.1), (1.0, 2.1, 1.0, 2.1), (0.05, 1.0, 3.9, 4.9), (2.2, 3.1, 3.9, 4.9)], "side": []})
    ours = House(kit, "ours", +1, -0.8, 0.0, "#ffd86b", "#fffaf0", "#c4503a", detail=True, holes=detail_ours["holes"],
                 interior="#ffe49a", floor=None)
    his = House(kit, "his", -1, 0.8, 0.0, "#7ec8ff", "#fffaf0", "#2f5fa8", detail=True,
                holes={"front": [(2.5, 3.4, 0.0, 2.1), (1.0, 2.1, 1.0, 2.1), (0.05, 1.0, 3.9, 4.9), (2.2, 3.1, 3.9, 4.9)], "side": []},
                interior="#a9dcff", floor=(kit.checker("#e9f3fb", "#c9d9ea", 0.5), kit.planks("#9a7a58", "#7e5f40", 1.0, "Y")))
    ctx["ours"], ctx["his"] = ours, his
    for H in (ours, his):
        # frames and sills on the openings
        H.frame(2.5, 3.4, 0.0, 2.1, sill=False)
        H.frame(1.0, 2.1, 1.0, 2.1)
        H.frame(0.05, 1.0, 3.9, 4.9)
        H.frame(2.2, 3.1, 3.9, 4.9)
    # doors
    ours.door_slab(2.5, 3.4, P("#3f8f6a", 0.5))
    his.door_slab(2.5, 3.4, P("#c9503a", 0.5))
    # my room's door on the hall's back wall (inside face y = D-0.2), a white frame and a brown door
    ours.b(ours.root, (2.2, 3.2), (D - 0.26, D - 0.2), (FLOOR2, 5.0), P("#7a4a2a", 0.5), "mydoor", 0.01)
    ours.b(ours.root, (2.12, 2.2), (D - 0.28, D - 0.2), (FLOOR2, 5.08), ours.tm, "mydoorf", 0.01)
    ours.b(ours.root, (3.2, 3.28), (D - 0.28, D - 0.2), (FLOOR2, 5.08), ours.tm, "mydoorf", 0.01)
    ours.b(ours.root, (2.12, 3.28), (D - 0.28, D - 0.2), (5.0, 5.08), ours.tm, "mydoorf", 0.01)
    # roof chimneys
    for H in (ours, his):
        H.b(H.root, (0.5, 0.95), (1.6, 2.05), (WALL_H + 0.2, WALL_H + 1.5), P("#b86a52", 0.8), "chimney", 0.01)
    # the window sash on our hall window (slides up at L21)
    pane = clear_pane(kit)
    sash = E(ours.root, (0, 0, 0), "sash")
    ours.b(sash, (0.05, 1.0), (0.07, 0.12), (3.9, 4.9), pane, "pane", 0.0)
    ours.b(sash, (0.05, 1.0), (0.06, 0.13), (3.9, 3.97), ours.tm, "sashb", 0.005)
    ours.b(sash, (0.05, 1.0), (0.06, 0.13), (4.83, 4.9), ours.tm, "sasht", 0.005)
    ours.b(sash, (0.5, 0.54), (0.06, 0.13), (3.9, 4.9), ours.tm, "sashm", 0.005)
    ctx["sash"] = sash

    # ---- other houses on the street (pairs that lean at each other)
    others = {}

    def simple(name, sgn, px, wall, roof, door, py=0.0):
        H = House(kit, name, sgn, px, py, wall, "#fffaf0", roof, detail=False)
        H.fake_windows()
        H.door_slab(1.4, 2.3, P(door, 0.5))
        others[name] = H
        return H

    simple("lilac", +1, -11.0, "#c8a8f0", "#6a4a9a", "#f2c14e")
    simple("coral", -1, -9.8, "#ff8e72", "#a8453a", "#3f8f6a")
    simple("green", +1, 6.0, "#9be0a8", "#3a7a4a", "#d7503a")
    simple("pink", -1, 7.0, "#ffb8d0", "#a8456a", "#2f5fa8")
    ctx["others"] = others
    # the bakeries and the duplex: far off along the street, not seen from home
    bk_a = simple("bakA", +1, -60.0, "#ffcf9a", "#a8503a", "#8a5a3a")
    bk_b = simple("bakB", -1, -57.6, "#fff0c8", "#b8794a", "#8a5a3a")
    for H, c1 in ((bk_a, "#e8503a"), (bk_b, "#3a8a5a")):     # striped awnings
        for k in range(6):
            H.b(H.root, (0.3 + k * 0.5, 0.3 + k * 0.5 + 0.25), (-1.0, 0.0), (2.2 - 0.0, 2.3), P(c1 if k % 2 else "#fffaf0", 0.6), "awn", 0.01)
    du_a = simple("dupA", +1, -80.0, "#b8d8a8", "#5a8a4a", "#d7503a")
    du_b = simple("dupB", -1, -78.2, "#f0d8a8", "#9a7a4a", "#d7503a")
    # the mint house across the street (leans toward ours, about the x axis)
    mint = House(kit, "mint", +1, -2.2, -15.6, "#8fe0b0", "#fffaf0", "#3a8a6a", detail=False, axis="x", yaw=math.pi)
    mint.fake_windows()
    mint.door_slab(1.4, 2.3, P("#f2c14e", 0.5))
    ctx["mint"] = mint
    # a few far houses, trees, bushes
    for i, (x, y, c) in enumerate(((-24, 0, "#ffd0a8"), (16, 0, "#cfe8ff"), (22, 0, "#ffe08a"), (-17, -16, "#ffc4d6"), (8, -16, "#d9f0c4"))):
        hs = House(kit, f"far{i}", 1, x, y, c, "#fffaf0", "#7a5a4a", detail=False)
        hs.fake_windows()
    for i, (nme, x, y, h) in enumerate((("commontree_1", -16.5, 6, 6.0), ("birchtree_1", 12.5, 7, 7.0), ("commontree_2", 26, 4, 6.5),
                                       ("commontree_1", -30, 4, 6.0), ("birchtree_1", 4.5, -21, 7.0), ("commontree_2", -12, -22, 6.0))):
        try:
            kit.prop(nme, (x, y, 0), rot=41 * i, height=h, tint="#9be05a" if "common" in nme else "#c9f0a0")
        except Exception:
            pass
    # ---- the yards: hedge, fence, gate with the tally
    hedge = P("#3f9e4a", 0.85, 0.05)
    B(None, (0.5, 2.3, 0.6), (0, -1.45, 0.3), hedge, "hedge", 0.12)
    for k in range(2):
        B(None, (0.58, 0.9, 0.2), (0, -0.7 - k * 1.0, 0.64), P("#4cae56", 0.85, 0.05), "hedgetop", 0.12)
    for k in range(5):       # the hedge row along the bottom of the yard shots (front of the yards)
        B(None, (0.62, 0.7, 0.62 + 0.08 * (k % 2)), (-1.24 + k * 0.62, -3.0, 0.33), P("#3f9e4a" if k % 2 else "#4cae56", 0.85, 0.05), "hedgerow", 0.12)
    white = P("#f6f4ee", 0.5)
    for k in range(10):
        y = -3.45 - k * 0.27
        if -5.05 < y < -3.95:
            continue
        B(None, (0.08, 0.1, 0.92), (0, y, 0.46), white, "picket", 0.012)
    for y in (-3.4, -6.1):
        B(None, (0.1, 0.1, 1.15), (0, y, 0.575), white, "fpost", 0.012)
    B(None, (0.06, 2.8, 0.07), (0, -4.75, 0.78), white, "frail", 0.01)
    B(None, (0.06, 2.8, 0.07), (0, -4.75, 0.28), white, "frail", 0.01)
    gate = E(None, (0, -4.0, 0), "gate")
    for k in range(4):
        B(gate, (0.07, 0.1, 0.92), (0, -0.18 - k * 0.24, 0.46), white, "gpicket", 0.012)
    B(gate, (0.07, 1.0, 0.07), (0, -0.5, 0.74), white, "grail", 0.01)
    B(gate, (0.07, 1.0, 0.07), (0, -0.5, 0.26), white, "grail", 0.01)
    iron = P("#3b3f4a", 0.4, 0.6)
    B(gate, (0.045, 0.2, 0.05), (-0.055, -0.86, 0.5), iron, "latch", 0.006)      # the iron latch (lore plant)
    B(gate, (0.02, 0.24, 0.03), (-0.082, -0.86, 0.5), iron, "latchplate", 0.004)
    for k, yy in enumerate((-0.80, -0.87)):                                       # two shutter-blue strokes
        B(gate, (0.012, 0.014, 0.045), (-0.1, yy - 0.0, 0.5), P("#4aa3ff", 0.4, 0.3), "stroke", 0.002, rot=(0.3, 0, 0))
    ctx["gate"] = gate
    # the porch: boards in front of our house for the marble at L41
    B(None, (2.7, 3.4, 0.09), (-3.05, -1.7, 0.045), kit.planks("#c8935a", "#a8743f", 1.0, "X"), "porch", 0.01)
    # ---- the squirrel (hidden until it's needed)
    sq = E(None, (0, 0, 0), "squirrel")
    fur, cream = P("#a8683a", 0.8), P("#f2dcc0", 0.8)
    B(sq, (0.10, 0.2, 0.12), (0, 0, 0.11), fur, "sqbody", 0.03)
    B(sq, (0.09, 0.09, 0.09), (0, -0.12, 0.2), fur, "sqhead", 0.03)
    B(sq, (0.04, 0.02, 0.05), (0, -0.15, 0.15), cream, "sqmuzzle", 0.01)
    for sx in (-1, 1):
        B(sq, (0.02, 0.03, 0.04), (sx * 0.035, -0.11, 0.265), fur, "sqear", 0.006)
        B(sq, (0.016, 0.016, 0.016), (sx * 0.026, -0.168, 0.215), P("#14110e", 0.3), "sqeye", 0.004)
    B(sq, (0.07, 0.07, 0.26), (0, 0.17, 0.25), P("#c47a44", 0.85), "sqtail", 0.03, rot=(-0.35, 0, 0))
    ctx["squirrel"] = sq
    # ---- the note on the door of his house, the picture frames, kitchen things, the marble, the mugs
    nimg = bpy.data.images.load(note_image(TMP / "note.png"))
    nimg.colorspace_settings.name = "sRGB"
    nm_ = kit._new(nm("note"))
    n_ = nm_.node_tree
    bs = n_.nodes["Principled BSDF"]
    bs.inputs["Roughness"].default_value = 0.9
    ti = n_.nodes.new("ShaderNodeTexImage")
    gc = n_.nodes.new("ShaderNodeTexCoord")
    n_.links.new(gc.outputs["Generated"], ti.inputs["Vector"])
    n_.links.new(ti.outputs["Color"], bs.inputs["Base Color"])
    ti.image = nimg
    kit._fogged(nm_, bs.outputs[0])
    ctx["note_mat"] = nm_
    ctx["note"] = kit.plane(nm("note"), (0.3, 0.38), (his.sgn * 0 + (-his.sgn * 2.95), 0.0, 1.5), nm_, his.root, rot=(math.pi / 2, 0, 0))
    ctx["note"].location = (-his.sgn * 2.95, 0.035, 1.55)
    no_shadow(ctx["note"])
    ctx["note"].hide_render = True
    # a big copy of the note for the close shot
    ctx["note_big"] = kit.plane(nm("notebig"), (0.3, 0.38), (0, 0, -9), nm_, None, rot=(math.pi / 2, 0, 0))
    ctx["note_big"].hide_render = True
    no_shadow(ctx["note_big"])
    # picture frames hang on the back wall (inner face y = D-0.2, facing -y) and the front wall (y = 0.2, facing +y)
    ctx["frames"] = []
    pics = (("#4aa3ff", "#ffd23a"), ("#6cc24a", "#ffffff"), ("#ff8e72", "#4a3a8a"), ("#fff1c9", "#d7503a"))
    for i, (ux, y0, z, fw, fh, dirn) in enumerate((
            (2.4, D - 0.2, 2.3, 0.7, 0.55, -1),       # kitchen, behind Dad (back wall)
            (1.0, D - 0.2, 2.1, 0.55, 0.7, -1),       # kitchen, back wall
            (0.55, 0.2, 1.75, 0.5, 0.7, +1),          # kitchen, front wall left of the window
            (0.9, D - 0.2, 4.3, 0.7, 0.55, -1),       # hall, back wall
            (1.75, D - 0.2, 4.35, 0.55, 0.75, -1),
            (1.6, 0.2, 4.4, 0.45, 0.6, +1))):         # hall, front wall between the windows
        piv = E(ours.root, (-ours.sgn * ux, y0, z), f"fr{i}")
        c1, c2 = pics[i % 4]
        d = dirn
        B(piv, (fw, 0.05, fh), (0, d * 0.025, 0), P("#7a4a2a", 0.5), "frame", 0.01)
        B(piv, (fw - 0.12, 0.02, fh - 0.12), (0, d * 0.058, 0), P(c1, 0.6), "canvas", 0.004)
        if i % 4 == 0:   # a fish
            B(piv, (fw * 0.45, 0.02, fh * 0.28), (0, d * 0.072, 0), P(c2, 0.5), "fishb", 0.01)
            B(piv, (fw * 0.16, 0.02, fh * 0.28), (fw * 0.3, d * 0.072, 0), P(c2, 0.5), "fisht", 0.01)
        elif i % 4 == 1:
            B(piv, (fw * 0.5, 0.02, fh * 0.3), (0, d * 0.072, -fh * 0.15), P(c2, 0.5), "hill", 0.01)
        else:
            B(piv, (fw * 0.3, 0.02, fh * 0.3), (0, d * 0.072, fh * 0.1), P(c2, 0.5), "sun", 0.01)
        ctx["frames"].append((piv, i))
    # ---- kitchen: the back counter, sink and mugs, the table on books
    ctx["kitchen"] = build_kitchen(kit, ours, ctx)
    build_hall_bits(kit, ours, his, ctx)
    # marble
    ctx["marble"] = kit.sphere(nm("marble"), 0.12, (0, 0, -9), P("#3fa0ff", 0.12, 1.0), None, seg=16)
    ctx["marble"].hide_render = True
    # ---- the porch lamps (outside), kitchen & hall lamps
    ctx["kl"] = kit.light("kitchenl", "POINT", (-ours.sgn * 1.7, 2.3, 2.45), 300, "#fff0d0", size=0.4, parent=ours.root)
    ctx["hl"] = kit.light("halll", "POINT", (-ours.sgn * 1.7, 2.3, 5.1), 240, "#ffcf7a", size=0.3, parent=ours.root)
    ctx["pl"] = kit.light("pruittl", "POINT", (-his.sgn * 1.0, 1.3, 4.6), 200, "#ffcf7a", size=0.25, parent=his.root)
    ctx["pk1"] = kit.light("porchA", "POINT", (-ours.sgn * 2.1, -0.9, 2.7), 150, "#ffe3a8", size=0.2, parent=ours.root, shadow=False)
    ctx["pk2"] = kit.light("porchB", "POINT", (-his.sgn * 2.1, -0.9, 2.7), 150, "#ffe3a8", size=0.2, parent=his.root, shadow=False)
    ctx["gaplight"] = kit.light("gaplight", "POINT", (0.0, -1.5, 4.8), 120, "#ffcf7a", size=0.4, shadow=False)
    ctx["hlmat"], ctx["hlnode"] = glow_mat(kit, "#ffe2a0")
    ctx["plmat"], ctx["plnode"] = glow_mat(kit, "#ffd890")
    # wall lamp in our hall (a globe on a bracket), his lamp on a stand near his window
    B(ours.root, (0.12, 0.12, 0.1), (-ours.sgn * 1.7, 2.3, 5.25), P("#5a4a3a", 0.5), "lampcap", 0.02)
    ctx["lampg"] = kit.sphere(nm("lampglobe"), 0.14, (-ours.sgn * 1.7, 2.3, 5.05), ctx["hlmat"], ours.root, seg=14)
    no_shadow(ctx["lampg"])
    B(his.root, (0.1, 0.1, 0.9), (-his.sgn * 1.0, 1.3, FLOOR2 + 0.45), P("#5a4a3a", 0.5), "lampstand", 0.02)
    ctx["lampp"] = kit.sphere(nm("lampshade"), 0.2, (-his.sgn * 1.0, 1.3, FLOOR2 + 1.05), ctx["plmat"], his.root, seg=14)
    no_shadow(ctx["lampp"])
    # Mr. Pruitt's navy sleeve and flat hand reaching out of his dark window (S19, S20); his face is never in these shots
    ao = E(his.root, (0, 0, 0), "armout")
    B(ao, (0.3, 1.2, 0.28), (0.3, 0.1, 4.46), P("#26365e", 0.7, 0.1), "sleeve", 0.04, rot=(0, 0, -0.4))
    B(ao, (0.26, 0.3, 0.1), (0.0, -0.52, 4.44), P("#ecc3a0", 0.6, 0.2), "palm", 0.02, rot=(0, 0, -0.4))
    B(ao, (0.26, 0.2, 0.08), (-0.07, -0.69, 4.44), P("#ecc3a0", 0.6, 0.2), "fingers", 0.02, rot=(0, 0, -0.4))
    ctx["armout"] = ao
    hide(ao, True)
    ctx["late"] = False
    ctx["tagmat"] = None
    build_inset(kit, ctx)
    # tilt state starts at rest
    ours.apply(5.0)
    his.apply(5.0)
    return ctx


def build_kitchen(kit, ours, ctx):
    """An island with a sink and mugs; Dad's mug sits on it (it tilts with the house, the coffee stays level); the table
    (world-level) stands on books under its downhill legs (set each frame in animate)."""
    K_ = {}
    cm = P("#fffaf0", 0.5)
    top = P("#7ec8ff", 0.4, 0.5)
    y0, y1 = 2.55, 3.25
    ours.b(ours.root, (1.5, 3.2), (y0, y1), (FLOOR1, 0.9), cm, "island", 0.012)
    ours.b(ours.root, (1.46, 3.24), (y0 - 0.04, y1 + 0.04), (0.9, 0.95), top, "islandtop", 0.01)
    ours.b(ours.root, (1.65, 2.3), (y0 + 0.1, y1 - 0.1), (0.945, 0.956), P("#aeb8c4", 0.25, 0.9), "sinkbasin", 0.01)
    ours.b(ours.root, (1.9, 2.05), (y1 - 0.14, y1 - 0.06), (0.95, 1.3), P("#aeb8c4", 0.25, 0.9), "tap", 0.01)
    ym = (y0 + y1) / 2
    K_["m1"] = mug(kit, ours.root, (-ours.sgn * 1.85, ym, 0.97), "#ff8e72", "sinkmugA", rot=(0, 0.25, 0.0), scale=1.2)
    K_["m2"] = mug(kit, ours.root, (-ours.sgn * 2.12, ym + 0.02, 0.97), "#4aa3ff", "sinkmugB", rot=(0.0, -0.4, 0.6), scale=1.2)
    K_["m3"] = mug(kit, ours.root, (-ours.sgn * 1.8, y0 + 0.05, 0.95), "#ff8e72", "drainA", scale=1.2)
    K_["m4"] = mug(kit, ours.root, (-ours.sgn * 2.2, y0 + 0.05, 0.95), "#4aa3ff", "drainB", scale=1.2)
    K_["juice"] = kit.cyl(nm("juice"), 0.05, 0.13, (-ours.sgn * 3.0, ym, 1.015), P("#ff9a2e", 0.2, 0.8), ours.root, n=16)
    ours.b(ours.root, (2.55, 2.85), (2.63, 2.93), (0.95, 1.32), P("#d7503a", 0.5), "trivet", 0.01)
    K_["dadmug"] = mug(kit, ours.root, (-ours.sgn * 2.7, 2.78, 1.32), "#ffd23a", "dadmug", rot=(0, 0.2, 0), scale=2.3)
    K_["dadcoffee"] = coffee_disc(kit, 0.037 * 2.3 * 1.05)
    tm = P("#e8b070", 0.5)
    K_["ttop"] = kit.cyl(nm("ttop"), 0.62, 0.06, (0, 0, -9), tm, None, n=28)
    K_["tlegs"] = [kit.box(nm("tleg"), (0.07, 0.07, 0.75), (0, 0, -9), tm, None, bevel=0.01) for _ in range(4)]
    K_["tbooks"] = []
    bc = ["#d7503a", "#2f5fa8", "#3f8f6a", "#f2c14e", "#8a5a9a", "#ff8e72"]
    for s_ in range(2):
        K_["tbooks"].append([kit.box(nm("book"), (0.34, 0.26, 0.04), (0, 0, -9), P(bc[(s_ * 3 + j) % 6], 0.6), None, bevel=0.006)
                             for j in range(4)])
    return K_


def build_hall_bits(kit, ours, his, ctx):
    # a rug-less hall: a small side table with a coat hook... keep it plain; a doorway frame to my room is in the wall
    pass


# ------------------------------------------------------------------------------------------------ the tag (rule marker)
def build_inset(kit, ctx):
    cam = kit.OBJ["cam"]
    m = kit._new(nm("inset"))
    nt = m.node_tree
    nt.nodes.remove(nt.nodes["Principled BSDF"])
    tex = nt.nodes.new("ShaderNodeTexImage")
    gc = nt.nodes.new("ShaderNodeTexCoord")
    em = nt.nodes.new("ShaderNodeEmission")
    em.inputs["Strength"].default_value = 0.9
    nt.links.new(gc.outputs["Generated"], tex.inputs["Vector"])
    nt.links.new(tex.outputs["Color"], em.inputs["Color"])
    nt.links.new(em.outputs[0], next(n for n in nt.nodes if n.type == "OUTPUT_MATERIAL").inputs["Surface"])
    pl = kit.plane(nm("inset"), (1.0, 1.0), (0, 0, -0.15), m, cam)
    no_shadow(pl)
    ctx["inset"] = (pl, tex)
    ctx["inset_imgs"] = {}


def place_inset(kit, ctx, v, lens):
    pl, tex = ctx["inset"]
    if v not in ctx["inset_imgs"]:
        im = bpy.data.images.load(tag_image(v, TMP / f"tag-{v}.png"))
        im.colorspace_settings.name = "sRGB"
        ctx["inset_imgs"][v] = im
    tex.image = ctx["inset_imgs"][v]
    d = 0.15
    unit = d / lens
    pw = 0.23 * 13.5 * unit
    ph = pw * 340 / 280
    x = -0.665 * 6.75 * unit
    y = 0.80 * 12.0 * unit
    pl.location, pl.scale = (x, y, -d), (pw, ph, 1)


# ------------------------------------------------------------------------------------------------ late touches on the cast
def late(kit, ctx):
    ctx["dads"] = []
    wh = P("#f4f1ea", 0.7)
    gray = P("#c9c9cf", 0.7)
    for nme in ("dad", "dad_n"):
        ch = rig.CHARS.get(nme)
        if ch is None:
            continue
        hg = ch.head.children[0]
        R = faces.HEAD_R
        for sx in (-1, 1):       # two thick drooping lobes with a gap, so it reads as a mustache, not tape
            B(hg, (0.27, 0.15, 0.15), (sx * 0.15, -R - 0.05, -0.085), wh, "mustache", 0.06, rot=(0, sx * 0.45, 0))
            B(hg, (0.12, 0.13, 0.13), (sx * 0.27, -R - 0.045, -0.17), wh, "mustache", 0.05)
        for sx in (-1, 1):
            B(hg, (0.2, 0.9, 0.5), (sx * (R - 0.02), 0.18, 0.0), gray, "sidehair", 0.08)
            B(hg, (0.16, 0.5, 0.18), (sx * (R - 0.03), 0.3, 0.3), gray, "sidehair2", 0.05)


def clear_lenses(kit):
    """Pruitt's lenses: nearly clear, a faint light glint, so his eyes and his wink read (the glass shader rendered black)."""
    lens = clear_pane(kit)
    lens.node_tree.nodes[[n.name for n in lens.node_tree.nodes if n.type == "MIX_SHADER"][0]].inputs["Fac"].default_value = 0.1
    for ob in bpy.data.objects:
        if ".gl-1" in ob.name or ".gl1" in ob.name:
            if "pruitt" in ob.name:
                ob.data.materials.clear()
                ob.data.materials.append(lens)


def late_hold(kit, ctx):
    """Mugs held on flat palms: one on Mr. Pruitt's night arm, one on Dad's (parented to the rig arms, rig units)."""
    ctx["held"] = {}
    for key, who, arm in (("p", "pruitt_n", "arm-1"), ("d", "dad_n", "arm1")):
        ch = rig.CHARS.get(who)
        if ch is None:
            continue
        m = mug(kit, ch.P[arm], (0, -0.55, -1.5), "#fff1c9", f"held{key}", rot=(math.pi / 2, 0, 0), scale=8.0)
        ctx["held"][key] = m
        hide(m, True)


# ------------------------------------------------------------------------------------------------ per frame
def floor_world(H, ux, y, z):
    """World point of a house-local point at the house's current lean (for keeping things on the floor)."""
    a = math.radians(H.deg)
    s = H.sgn
    X = H.px - s * (ux * math.cos(a) - z * math.sin(a))
    Z = ux * math.sin(a) + z * math.cos(a)
    return V((X, H.py + y, Z))


def animate(kit, story, tl, t, ctx):
    if not ctx["late"]:
        late(kit, ctx)
        clear_lenses(kit)
        late_hold(kit, ctx)
        ctx["late"] = True
    hc = cue_at(tl, "hold", t)
    hide(ctx["armout"], not ctx["shots"][next((x["id"] for x in tl["shots"] if x["start"] <= t < x["end"]), tl["shots"][-1]["id"])].get("armout"))
    for key, m in ctx.get("held", {}).items():
        hide(m, not hc.get(key, False))
    sc = bpy.context.scene
    L, cur = look_at(ctx, tl, t)
    sd = ctx["shots"][cur["id"]]
    r = ctx["ramp"].color_ramp.elements
    for el, c in zip(r, L["sky"]):
        el.color = (kit.srgb(c[0]), kit.srgb(c[1]), kit.srgb(c[2]), 1.0)
    ctx["bg"].inputs["Strength"].default_value = L["world"]
    azr, elr = math.radians(L["az"]), math.radians(L["el"])
    pos = V((math.sin(azr) * math.cos(elr), -math.cos(azr) * math.cos(elr), math.sin(elr)))
    sun = ctx["sun"]
    sun.rotation_euler = (-pos).to_track_quat("-Z", "Y").to_euler()
    c = hexrgb(L["sunc"] if isinstance(L["sunc"], str) else "#ffffff")
    sun.data.color = (kit.srgb(c[0] / 255), kit.srgb(c[1] / 255), kit.srgb(c[2] / 255))
    cl, _, cl_lens, _ = bl_story.cam_at(sd, cur, t, {}, tl)
    ctx["fill"].location = (cl[0], cl[1], cl[2])
    sc.view_settings.exposure = L["exp"]
    # ---- the leans
    deg_main = lean_val(tl, "main", t, 5.0)
    ours, his = ctx["ours"], ctx["his"]
    ours.apply(deg_main)
    his.apply(deg_main)
    for nme, H in ctx["others"].items():
        base = {"lilac": 3.5, "coral": 3.5, "green": 3.0, "pink": 3.0, "bakA": 12.0, "bakB": 12.0, "dupA": 10.5, "dupB": 10.5}.get(nme, 0.0)
        H.apply(lean_val(tl, nme, t, base))
    ctx["mint"].apply(lean_val(tl, "mint", t, 0.0))
    # ---- the tag
    v = cue_at(tl, "tag", t).get("v", "a")
    place_inset(kit, ctx, v, cl_lens)
    # ---- the sash on our hall window
    sc_ = cue_at(tl, "sash", t)
    up = ss((t - sc_["t"]) / sc_.get("dur", 0.6)) * 1.0 if sc_ else 0.0
    ctx["sash"].location = (0, 0, up)
    # ---- the frames: crook (degrees in the world) so they hang at an angle on the leaning walls
    fr = cue_at(tl, "frames", t)
    crook = fr.get("deg", 3.0) if fr else 3.0
    if fr and "to" in fr:
        crook = lerp(fr["deg"], fr["to"], ss((t - fr["t"]) / fr.get("dur", 1.0)))
    for piv, i in ctx["frames"]:
        sign = 1 if i % 2 == 0 else -1
        piv.rotation_euler = (0, math.radians(sign * crook), 0)
    # ---- lights
    ov = {"sun": L["sun"] / 4.6, "camfill": L["fill"], "kitchenl": L["kl"], "halll": L["hl"], "pruittl": L["pl"],
          "porchA": L["pk"], "porchB": L["pk"], "gaplight": L["pk"] * 0.6}
    ctx["hlnode"].inputs["Strength"].default_value = 6.0 * L["hl"]
    ctx["plnode"].inputs["Strength"].default_value = 6.0 * L["pl"]
    # ---- the kitchen: sill mug with level coffee, the table on books
    K_ = ctx["kitchen"]
    dm = K_["dadmug"]
    mwm = dm.matrix_world
    ax = mwm.to_3x3() @ V((0, 0, 1))
    pt = mwm.translation + ax.normalized() * 0.185
    K_["dadcoffee"].location = (pt.x, pt.y, pt.z)
    # the table: world-level top, legs on the floor, books under the downhill pair
    a = math.radians(ours.deg)
    cx_u, cy = 0.95, 1.7
    top_z = None
    pts = []
    for sx, sy in ((+1, -1), (+1, 1), (-1, -1), (-1, 1)):    # sx=+1 : uphill (larger ux)
        p = floor_world(ours, cx_u + 0.42 * sx, cy + 0.42 * sy, FLOOR1)
        pts.append((sx, sy, p))
    up_z = max(p.z for _, _, p in pts)
    top = up_z + 0.75
    c0 = floor_world(ours, cx_u, cy, FLOOR1)
    K_["ttop"].location = (c0.x, c0.y, top + 0.03)
    for lg, (sx, sy, p) in zip(K_["tlegs"], pts):
        lg.location = (p.x, p.y, top - 0.375)
    for si, stack in enumerate(K_["tbooks"]):
        sy = (-1, 1)[si]
        p = [q for sx, sy_, q in pts if sx == -1 and sy_ == sy][0]
        h = max(0.001, (top - 0.75) - p.z)
        for j, bk in enumerate(stack):
            bk.location = (p.x + 0.02 * ((j * 7) % 3 - 1), p.y, p.z + h * (j + 0.5) / len(stack))
            bk.scale = (1.0, 1.0, max(0.05, h / len(stack) / 0.04))
            bk.rotation_euler = (0, 0, 0.12 * ((j * 5) % 3 - 1))
    # ---- the marble: dropped at t0, bounces, then rolls inward (toward his house) down the tilted hall floor
    mb = cue_at(tl, "marble", t)
    mo = ctx["marble"]
    if mb and mb.get("mode") == "step":
        u = max(0.0, t - mb["t"])
        d = 0.5 * mb.get("acc", 1.5) * u * u
        mo.hide_render = False
        mo.location = (mb["pos"][0] + mb["dir"][0] * d, mb["pos"][1] + mb["dir"][1] * d, mb["pos"][2])
    elif mb:
        u = t - mb["t"]
        ux0, yy = mb.get("ux", 2.9), mb.get("y", 2.3)
        fz = FLOOR2
        if u < 0:
            mo.hide_render = True
        else:
            mo.hide_render = False
            g = 9.8
            drop_h = 0.9
            tfall = math.sqrt(2 * drop_h / g)
            if u < tfall:
                h = drop_h - 0.5 * g * u * u
                ux = ux0
            else:
                uu = u - tfall
                tb = 0.22
                h = max(0.0, 0.18 * 4 * (uu / tb) * (1 - uu / tb)) if uu < tb else 0.0
                roll_t = max(0.0, uu - 0.12)
                acc = 1.1
                ux = ux0 - 0.5 * acc * roll_t * roll_t * (1.0 + 0.5 * min(1.0, roll_t))
                ux = max(ux, 0.28)
            p = floor_world(ours, ux, yy, fz)
            mo.location = (p.x, p.y, p.z + 0.1 + h)
    else:
        mo.hide_render = True
    # ---- the squirrel
    sqc = cue_at(tl, "squirrel", t)
    sq = ctx["squirrel"]
    if sqc and not sqc.get("hidden"):
        hide(sq, False)
        sq.location = tuple(sqc["pos"])
        sq.rotation_euler = (0, 0, math.radians(sqc.get("yaw", 0)))
    else:
        hide(sq, True)
    # ---- the note
    nc = cue_at(tl, "note", t)
    ctx["note"].hide_render = not nc.get("on", False)
    nb = cue_at(tl, "notebig", t)
    ctx["note_big"].hide_render = not nb.get("on", False)
    if nb.get("on"):
        ctx["note_big"].location = tuple(nb["pos"])
        ctx["note_big"].scale = (nb.get("scale", 1.0),) * 3
    # ---- gate latch lore: nothing to animate
    return ov
