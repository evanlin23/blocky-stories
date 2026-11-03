"""ep47 "Fitting room": the covered arcade, Uncle Aurel's alterations shop (counter, workroom, fitting room), the
rooms above, a train window, and the Empty: a charcoal pinstripe suit with nobody in it. Built from kit.py's parts;
nothing here is shared with another story's set. No text anywhere: every sign is a picture, every tag carries only
our hook glyph.

Coordinates (metres, z up; a character faces -y at yaw 0, +x at yaw 90, -x at yaw -90, +y at yaw 180):
- the arcade runs along y (-34 .. 12), 8 m wide (x -4 .. 4), iron ribs every 2.8 m, sun in long bars.
  Left wall (x = -4): Uncle's shop (y -2.6 .. 3.2), the shoe shop (-9 .. -5), the salon (-14 .. -10), others.
  Right wall (x = +4): the cafe (open front, y -8 .. -1) with three tall tables outside, others.
- Uncle's shop: x -16 .. -4.2, y -2.6 .. 3.2. Counter at x -7.1 .. -6.4. Workroom from x -10 to the back wall
  (x -16): Uncle's bench (y -1.45 .. -0.55) and mine (y 0.55 .. 1.45), x -13.7 .. -11.5. The side window is in the
  y = 3.2 wall; my station is (-12.6, 1.8); the Empty stands behind it at (-12.6, 2.9). The fitting room is the
  alcove x -16 .. -14.3, y -2.6 .. -0.9, curtain across x = -14.3. The stair is x -15.9 .. -14.9, rising toward +y.
- the sitting room (x 40 .. 45), the bedroom (x 60 .. 64), the train (x 80 .. 84).

Cues read here: mode (the time of day: world and light gains, crossfaded), lamp (a practical's gain, ramped), curtain
(open 0..1), hanger, empty (pose, pos, yaw, lean, hidden), boxes (how many on the counter), tape, cloth, canvas,
pincushion, phone, ticket, aprons, sign, bell, dust, train, tags (a character's tags: n, or a fall). Every light
change ramps over at least 0.3 s (the house flash bar).
"""

from __future__ import annotations

import math

import bpy
import numpy as np
from mathutils import Vector as V

from blocky import acting, faces

S = 0.34            # the rig's metre per unit
ARC_Y0, ARC_Y1 = -34.0, 12.0
SHOP_X0, SHOP_X1 = -16.0, -4.2
SHOP_Y0, SHOP_Y1 = -2.6, 3.2
CEIL = 3.2
ME_ST = (-12.6, 1.8)      # my station
EMPTY_ST = (-12.6, 2.9)   # where the Empty stands
FOOT = (-11.6, 0.66)     # the front-left brass foot of my bench (the lore tally)
HEAP = (-11.35, 1.75)
CURTAIN_X = -14.3
HANG_AT = (-15.55, -1.75)

TAG = "#efeae0"
GLYPH = "#151515"
BRASS = "#b08a3e"
GREEN = "#2f5a43"
CREAM = "#e8dcc4"
OAK = "#8a6440"
OCHRE = "#b58a2e"
PIN = "#26262c"
STRIPE = "#6c6c78"


def ss(x):
    x = min(1.0, max(0.0, x))
    return x * x * (3 - 2 * x)


# ------------------------------------------------------------------------------------------------ cues


def _cues(tl, name):
    cache = tl.setdefault("_cache", {})
    if name not in cache:
        cache[name] = sorted((c for c in tl["cues"] if c["name"] == name), key=lambda c: c["t"])
    return cache[name]


def _last(cs, t):
    out = None
    for c in cs:
        if c["t"] <= t + 1e-9:
            out = c
    return out


def ramped(cs, key, t, default, mind=0.3):
    """A value that eases to each cue's over its dur (never under 0.3 s), from where it was."""
    prev = default
    for c in cs:
        if key not in c:
            continue
        if t < c["t"]:
            break
        d = max(mind, c.get("dur", mind))
        v = c[key]
        if t < c["t"] + d:
            return prev + (v - prev) * ss((t - c["t"]) / d)
        prev = v
    return prev


# ------------------------------------------------------------------------------------------------ materials


def pbr(kit, name, hexc, rough=0.6, metal=0.0, spec=0.4):
    if name in kit.MATS:
        return kit.MATS[name]
    m = kit._new(name)
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = kit.col(hexc)
    b.inputs["Roughness"].default_value = rough
    b.inputs["Metallic"].default_value = metal
    for k in ("Specular IOR Level", "Specular"):
        if k in b.inputs:
            b.inputs[k].default_value = spec
            break
    m.diffuse_color = kit.col(hexc)
    kit._fogged(m, b.outputs[0])
    return m


def pinstripe(kit, name, base, stripe, scale=14.0):
    """Thin vertical pale stripes on charcoal wool (in the part's own object space)."""
    if name in kit.MATS:
        return kit.MATS[name]
    m = kit._new(name)
    nt = m.node_tree
    b = nt.nodes["Principled BSDF"]
    b.inputs["Roughness"].default_value = 0.85
    tc = nt.nodes.new("ShaderNodeTexCoord")
    sep = nt.nodes.new("ShaderNodeSeparateXYZ")
    nt.links.new(tc.outputs["Object"], sep.inputs[0])
    mul = nt.nodes.new("ShaderNodeMath")
    mul.operation = "MULTIPLY"
    mul.inputs[1].default_value = scale
    nt.links.new(sep.outputs["X"], mul.inputs[0])
    fr = nt.nodes.new("ShaderNodeMath")
    fr.operation = "FRACT"
    nt.links.new(mul.outputs[0], fr.inputs[0])
    ramp = nt.nodes.new("ShaderNodeValToRGB")
    ramp.color_ramp.interpolation = "CONSTANT"
    ramp.color_ramp.elements[0].color = kit.col(base)
    ramp.color_ramp.elements[1].position = 0.93
    ramp.color_ramp.elements[1].color = kit.col(stripe)
    nt.links.new(fr.outputs[0], ramp.inputs["Fac"])
    nt.links.new(ramp.outputs["Color"], b.inputs["Base Color"])
    kit._fogged(m, b.outputs[0])
    return m


def tag_image():
    """The hook glyph on matte off-white card: one thick stroke that rises and curls over at the top into a coat hook,
    with a small open ring at its foot. Not a letter or a number. A brass pin through the top."""
    from PIL import Image, ImageDraw
    W, H = 128, 180
    im = Image.new("RGB", (W, H), (239, 234, 224))
    d = ImageDraw.Draw(im)
    d.rectangle([0, 0, W - 1, H - 1], outline=(206, 200, 188), width=4)
    ink = (21, 21, 21)
    th = 12
    pts = [(58, 138), (58, 70)]
    for k in range(0, 15):   # the curl at the top: up and over to the right, ending pointing down
        a = math.pi * (1.0 - k / 14.0 * 1.15)
        pts.append((78 + 20 * math.cos(a), 56 - 22 * math.sin(a)))
    d.line(pts, fill=ink, width=th, joint="curve")
    for x, y in (pts[0], pts[-1]):
        d.ellipse([x - th / 2, y - th / 2, x + th / 2, y + th / 2], fill=ink)
    d.ellipse([58 - 17, 148 - 13, 58 + 17, 148 + 21 - 8], outline=ink, width=9)   # the ring at the foot
    d.rectangle([40, 150, 76, 160], fill=(239, 234, 224))                         # open at the bottom
    d.ellipse([58 - 6, 16 - 6, 58 + 6, 16 + 6], fill=(176, 138, 62))               # the brass pin
    return im


def materials(kit):
    M = {}
    M["tile"] = kit.checker("#d6cab2", "#5a5855", 1.6, name="arcade tile", rough=0.5)
    M["stone"] = pbr(kit, "stone", CREAM, 0.9)
    M["stone_d"] = pbr(kit, "stone dark", "#b9ad94", 0.9)
    M["green"] = pbr(kit, "bottle green", GREEN, 0.45, spec=0.5)
    M["green_d"] = pbr(kit, "green dark", "#1f3d2e", 0.5)
    M["brass"] = kit.metal(BRASS, 0.3)
    M["iron"] = pbr(kit, "iron", "#3c423c", 0.55, metal=0.4)
    M["plaster"] = pbr(kit, "plaster", "#d9cdb4", 0.9)
    M["plaster_w"] = pbr(kit, "plaster warm", "#cdb994", 0.9)
    M["oak"] = kit.planks(OAK, "#6a4a2c", 1.0, "Y", name="oak", rough=0.5)
    M["oak_x"] = kit.planks(OAK, "#6a4a2c", 1.0, "X", name="oak x", rough=0.5)
    M["oak_d"] = pbr(kit, "oak dark", "#5a3f26", 0.5)
    M["floor"] = kit.planks("#7c5a3a", "#5a3f26", 1.0, "Y", name="shop floor", rough=0.55)
    M["ochre"] = pbr(kit, "ochre", OCHRE, 0.9)
    M["lamp_green"] = pbr(kit, "lamp green", "#3f6b4a", 0.35, spec=0.6)
    M["kraft"] = pbr(kit, "kraft", "#a98657", 0.85)
    M["kraft_d"] = pbr(kit, "kraft dark", "#8d6d44", 0.85)
    M["paper"] = pbr(kit, "paper cover", "#9b7b54", 0.8)
    M["white"] = pbr(kit, "white cloth", "#e9e5da", 0.85)
    M["canvas"] = pbr(kit, "oatmeal canvas", "#c9b996", 0.9)
    M["chalk"] = pbr(kit, "chalk blue", "#7cc4f0", 0.9)
    M["yellow"] = pbr(kit, "tape yellow", "#e8c62e", 0.6)
    M["red"] = pbr(kit, "pincushion red", "#a02a2a", 0.8)
    M["black"] = pbr(kit, "black matte", "#050506", 0.95, spec=0.0)
    M["void"] = pbr(kit, "void", "#010101", 1.0, spec=0.0)
    M["lining"] = pbr(kit, "lining", "#17171d", 0.95, spec=0.0)
    M["collar"] = pbr(kit, "collar", "#232329", 0.9)
    M["pin"] = pinstripe(kit, "pinstripe", PIN, STRIPE)
    M["pin_collar"] = pinstripe(kit, "pinstripe collar", "#2a2a31", "#62626e", scale=16.0)
    M["pin_arm"] = pinstripe(kit, "pinstripe arm", PIN, STRIPE)
    M["trouser"] = pinstripe(kit, "pinstripe trouser", PIN, STRIPE)
    M["shoe"] = pbr(kit, "empty shoes", "#5a3a22", 0.4, spec=0.5)
    M["shirt"] = pbr(kit, "empty shirt", "#9c9a94", 0.85)
    M["lining2"] = pbr(kit, "lining2", "#3b3b46", 0.95, spec=0.0)
    M["glow"] = kit.emit("#fff1d0", 6.0, name="bulb glow")
    M["screen"] = kit.emit("#d8e8ff", 1.2, name="phone screen")
    M["warm_panel"] = kit.emit("#ffd9a0", 1.1, name="warm panel")
    M["door_light"] = kit.emit("#fff6e0", 1.1, name="arcade end light")
    M["window_cool"] = kit.emit("#8aa6d0", 1.6, name="passage light")
    M["window_night"] = kit.emit("#1b2438", 0.5, name="night window")
    M["sky"] = kit.emit("#aebfd0", 1.0, name="train sky")
    M["city"] = pbr(kit, "city block", "#5d636b", 0.9)
    M["city_d"] = pbr(kit, "city block dark", "#444a52", 0.9)
    M["cake"] = pbr(kit, "cake", "#e9c9a0", 0.7)
    M["cup"] = pbr(kit, "cup", "#e8e4da", 0.4)
    M["plate"] = pbr(kit, "plate", "#f0ede4", 0.35)
    M["leaf"] = pbr(kit, "sign cream", "#efe6cc", 0.5)
    M["thread"] = pbr(kit, "thread", "#b8483a", 0.7)
    M["coin_dark"] = pbr(kit, "charcoal stroke", "#2c2b2a", 0.9)
    M["dust"] = pbr(kit, "dust", "#efeae0", 1.0, spec=0.0)
    # the tag: card with the glyph, matte
    import tempfile
    from pathlib import Path
    tp = Path(tempfile.gettempdir()) / f"ep47-tag-glyph-{__import__('os').getpid()}.png"
    tag_image().save(tp)
    img = bpy.data.images.load(str(tp))
    img.colorspace_settings.name = "sRGB"
    m = kit._new("tag card")
    nt = m.node_tree
    b = nt.nodes["Principled BSDF"]
    b.inputs["Roughness"].default_value = 0.92
    tex = nt.nodes.new("ShaderNodeTexImage")
    tex.image = img
    tex.interpolation = "Linear"
    nt.links.new(tex.outputs["Color"], b.inputs["Base Color"])
    kit._fogged(m, b.outputs[0])
    M["tag"] = m
    return M


# ------------------------------------------------------------------------------------------------ helpers


def B(kit, name, size, loc, mat, parent=None, rot=(0, 0, 0), bevel=0.0):
    return kit.box(name, size, loc, mat, parent, rot, bevel)


def walls_with_openings(kit, name, axis, c, a0, a1, height, openings, thick, mat, z0=0.0):
    """A wall in the plane `axis` = c (thick), running from a0 to a1 along the other axis, with rectangular openings
    [(p0, p1, zlo, zhi)] cut out of it."""
    pieces = []
    cur = a0
    for p0, p1, zlo, zhi in sorted(openings):
        if p0 > cur:
            pieces.append((cur, p0, z0, height))
        if zlo > z0:
            pieces.append((p0, p1, z0, zlo))
        if zhi < height:
            pieces.append((p0, p1, zhi, height))
        cur = p1
    if cur < a1:
        pieces.append((cur, a1, z0, height))
    for i, (p0, p1, lo, hi) in enumerate(pieces):
        if p1 - p0 < 1e-3 or hi - lo < 1e-3:
            continue
        if axis == "x":
            B(kit, f"{name}{i}", (thick, p1 - p0, hi - lo), (c, (p0 + p1) / 2, (lo + hi) / 2), mat)
        else:
            B(kit, f"{name}{i}", (p1 - p0, thick, hi - lo), ((p0 + p1) / 2, c, (lo + hi) / 2), mat)


def sign_picture(kit, M, kind, cx, cy, cz, s):
    """A trade sign standing out from the wall at x = cx (s = -1 left wall, +1 right): a picture, never a word."""
    root = kit.empty(f"sign {kind}{cy:.0f}", (cx, cy, cz), rot=(0, 0, 0))
    g, b, cr = M["leaf"], M["brass"], M["leaf"]
    kit_rot = (0, 0, 0)
    ox = -s * 0.07    # out into the arcade
    if kind == "spool":
        kit.cyl("sp.core", 0.1, 0.34, (ox, 0, 0), M["thread"], root, n=14)
        for z in (-0.2, 0.2):
            kit.cyl(f"sp.fl{z}", 0.2, 0.04, (ox, 0, z), g, root, n=18)
        B(kit, "sp.needle", (0.014, 0.014, 0.9), (ox - s * 0.0, 0.0, 0.02), M["iron"], root, rot=(0.0, math.radians(32), 0.0))
    elif kind == "shoe":
        B(kit, "sh.sole", (0.07, 0.62, 0.07), (ox, 0.0, -0.18), M["oak_d"], root, bevel=0.02)
        B(kit, "sh.up", (0.07, 0.4, 0.2), (ox, 0.08, -0.06), g, root, bevel=0.03)
        B(kit, "sh.leg", (0.07, 0.2, 0.32), (ox, 0.2, 0.1), g, root, bevel=0.03)
        B(kit, "sh.heel", (0.07, 0.12, 0.1), (ox, 0.25, -0.24), M["oak_d"], root)
    elif kind == "cup":
        kit.cyl("cp.body", 0.17, 0.28, (ox, 0, 0), g, root, n=18, r2=0.13)
        B(kit, "cp.handle", (0.06, 0.1, 0.18), (ox, 0.24, 0.0), g, root, bevel=0.03)
        kit.cyl("cp.saucer", 0.26, 0.03, (ox, 0, -0.17), g, root, n=18)
    elif kind == "comb":
        B(kit, "cb.bar", (0.06, 0.7, 0.1), (ox, 0, 0.12), g, root, bevel=0.02)
        for k in range(8):
            B(kit, f"cb.t{k}", (0.05, 0.05, 0.28), (ox, -0.3 + k * 0.086, -0.08), g, root)
    elif kind == "hanger":
        B(kit, "hg.a", (0.05, 0.5, 0.05), (ox, -0.2, 0.0), g, root, rot=(math.radians(25), 0, 0))
        B(kit, "hg.b", (0.05, 0.5, 0.05), (ox, 0.2, 0.0), g, root, rot=(math.radians(-25), 0, 0))
        B(kit, "hg.c", (0.05, 0.8, 0.05), (ox, 0.0, -0.2), g, root)
    return root


# ------------------------------------------------------------------------------------------------ the arcade


def arch_rib(kit, M, y, i, n=10):
    pts = []
    for k in range(n + 1):
        x = -4.15 + 8.3 * k / n
        pts.append((x, 3.55 + 1.7 * (1 - (x / 4.15) ** 2)))
    for k in range(n):
        (x0, z0), (x1, z1) = pts[k], pts[k + 1]
        ln = math.hypot(x1 - x0, z1 - z0)
        ph = math.atan2(z1 - z0, x1 - x0)
        B(kit, f"rib{i}.{k}", (ln + 0.04, 0.5, 0.4), ((x0 + x1) / 2, y, (z0 + z1) / 2), M["iron"], rot=(0, -ph, 0))


def build_arcade(kit, M, ctx):
    kit.plane("arcade floor", (8.0, ARC_Y1 - ARC_Y0), (0, (ARC_Y0 + ARC_Y1) / 2, 0), M["tile"])
    y, i = ARC_Y0 + 1.0, 0
    while y < ARC_Y1:
        arch_rib(kit, M, y, i)
        y += 2.8
        i += 1
    # end walls with a bright arched doorway
    for ye, sgn in ((ARC_Y1, 1), (ARC_Y0, -1)):
        walls_with_openings(kit, f"end{sgn}", "y", ye + sgn * 0.15, -4.4, 4.4, 5.4, [(-1.5, 1.5, 0.0, 3.4)], 0.3, M["stone"])
        B(kit, f"endlight{sgn}", (3.0, 0.05, 3.4), (0, ye + sgn * 0.5, 1.7), M["door_light"])
    # the wall bands above the shopfronts, and pilasters at each shop boundary
    bounds = {-1: [12, 8, 3.2, -2.6, -5, -9, -14, -18, -22, -26, -30, -34], 1: [12, 4, -1, -8, -12, -17, -22, -27, -34]}
    for s in (-1, 1):
        B(kit, f"band{s}", (0.3, ARC_Y1 - ARC_Y0, 0.9), (s * 4.15, (ARC_Y0 + ARC_Y1) / 2, 3.45), M["stone"])
        for y in bounds[s]:
            B(kit, f"pil{s}{y}", (0.45, 0.42, 3.4), (s * 3.9, y, 1.7), M["stone"], bevel=0.04)
            B(kit, f"pilb{s}{y}", (0.5, 0.48, 0.18), (s * 3.9, y, 0.09), M["brass"])


def shell_room(kit, M, name, s, ya, yb, depth, mat_back, glow=True, shelf=False):
    """The shallow room behind a shopfront: floor, back wall, side walls, ceiling, a warm glow on the back wall."""
    x0, x1 = (4.2, 4.0 + depth) if s > 0 else (-4.0 - depth, -4.2)
    xm = (x0 + x1) / 2
    kit.plane(f"{name}.floor", (x1 - x0, yb - ya), (xm, (ya + yb) / 2, 0.005), M["floor"])
    B(kit, f"{name}.back", (0.2, yb - ya, CEIL), (x1 + 0.1 if s > 0 else x0 - 0.1, (ya + yb) / 2, CEIL / 2), mat_back)
    for k, y in enumerate((ya, yb)):
        B(kit, f"{name}.side{k}", (x1 - x0, 0.2, CEIL), (xm, y + (0.1 if k == 0 else -0.1), CEIL / 2), M["plaster"])
    B(kit, f"{name}.ceil", (x1 - x0, yb - ya, 0.15), (xm, (ya + yb) / 2, CEIL + 0.07), M["plaster"])
    if glow:
        bx = (x1 - 0.12) if s > 0 else (x0 + 0.12)
        B(kit, f"{name}.glow", (0.05, (yb - ya) * 0.6, 1.1), (bx, (ya + yb) / 2, 1.8), M["warm_panel"])
        if shelf:
            for z in (0.9, 1.4, 1.9, 2.4):
                B(kit, f"{name}.shelf{z}", (0.3, (yb - ya) * 0.8, 0.04), (bx - s * 0.18, (ya + yb) / 2, z), M["oak_d"])


def shopfront(kit, M, name, s, ya, yb, door=None, window=None, sign=None, depth=3.0, interior=True, back="plaster_w",
              shelf=False):
    """A bottle-green painted shopfront on the wall x = s * 4 (face at the arcade), a door and a window cut out."""
    xw = s * 4.1
    ops = []
    if door:
        ops.append((door[0], door[1], 0.0, 2.2))
    if window:
        ops.append((window[0], window[1], window[2], window[3]))
    walls_with_openings(kit, f"{name}.wall", "x", xw, ya, yb, 3.0, ops, 0.2, M["green"])
    B(kit, f"{name}.fascia", (0.16, yb - ya, 0.7), (s * 4.0 - s * 0.0, (ya + yb) / 2, 3.12), M["green_d"])
    B(kit, f"{name}.fasciabr", (0.04, yb - ya, 0.04), (s * 3.93, (ya + yb) / 2, 2.78), M["brass"])
    if window:
        y0, y1, z0, z1 = window
        B(kit, f"{name}.sill", (0.3, y1 - y0 + 0.1, 0.06), (s * 3.95, (y0 + y1) / 2, z0), M["brass"])
        n = max(1, int((y1 - y0) / 0.9))
        for k in range(1, n):
            B(kit, f"{name}.mull{k}", (0.06, 0.05, z1 - z0), (s * 3.98, y0 + (y1 - y0) * k / n, (z0 + z1) / 2), M["brass"])
    if door:
        B(kit, f"{name}.doorknob", (0.05, 0.06, 0.06), (s * 3.98, door[1] - 0.12, 1.0), M["brass"])
        B(kit, f"{name}.step", (0.4, door[1] - door[0] + 0.2, 0.05), (s * 3.85, (door[0] + door[1]) / 2, 0.025), M["stone_d"])
    if sign:
        sign_picture(kit, M, sign, s * 3.9, (ya + yb) / 2, 3.12, s)
    if interior:
        shell_room(kit, M, name, s, ya + 0.1, yb - 0.1, depth, M[back], True, shelf)


def build_fronts(kit, M, ctx):
    # left wall (x = -4): the shoe shop, the salon, decoration
    shopfront(kit, M, "shoe", -1, -9.0, -5.0, door=(-7.6, -6.6), window=(-8.9, -7.7, 0.8, 2.4), sign="shoe", shelf=True)
    shopfront(kit, M, "salon", -1, -14.0, -9.0, door=(-12.6, -11.6), window=(-14.0, -12.7, 0.8, 2.4), sign="comb")
    shopfront(kit, M, "dec1", -1, 3.2, 8.0, door=(5.5, 6.5), window=(3.5, 5.4, 0.9, 2.4), sign="hanger", shelf=True)
    shopfront(kit, M, "dec2", -1, 8.0, 12.0, window=(8.4, 11.6, 0.9, 2.4), sign=None, shelf=True)
    shopfront(kit, M, "dec3", -1, -5.0, -2.6, window=(-4.8, -2.8, 0.9, 2.4), sign="cup")
    shopfront(kit, M, "dec4", -1, -18.0, -14.0, door=(-16.0, -15.0), window=(-18.0, -16.2, 0.9, 2.4), shelf=True)
    for k, (a, b) in enumerate(((-22.0, -18.0), (-26.0, -22.0), (-30.0, -26.0), (-34.0, -30.0))):
        shopfront(kit, M, f"decL{k}", -1, a, b, window=(a + 0.3, b - 0.3, 0.9, 2.4), shelf=(k % 2 == 0))
    # right wall: decoration, then the cafe's open front
    shopfront(kit, M, "decR1", 1, 4.0, 12.0, window=(4.4, 11.6, 0.9, 2.4), sign="shoe")
    shopfront(kit, M, "decR2", 1, -1.0, 4.0, door=(0.6, 1.6), window=(2.0, 3.6, 0.9, 2.4), sign="comb", shelf=True)
    shopfront(kit, M, "decR3", 1, -12.0, -8.0, window=(-11.6, -8.4, 0.9, 2.4), sign="spool", shelf=True)
    for k, (a, b) in enumerate(((-17.0, -12.0), (-22.0, -17.0), (-27.0, -22.0), (-34.0, -27.0))):
        shopfront(kit, M, f"decR{k + 4}", 1, a, b, window=(a + 0.4, b - 0.4, 0.9, 2.4), shelf=(k % 2 == 1))
    # the cafe: an open frontage
    shopfront(kit, M, "cafe", 1, -8.0, -1.0, window=None, door=(-7.4, -1.6), sign="cup", depth=6.0, interior=False)
    ctx["cafe"] = build_cafe(kit, M)
    # Uncle's shop front: window and door
    build_shop_front(kit, M)


def build_cafe(kit, M):
    x0, x1, ya, yb = 4.2, 10.0, -8.0, -1.0
    kit.plane("cafe.floor", (x1 - x0, yb - ya), ((x0 + x1) / 2, (ya + yb) / 2, 0.005), M["floor"])
    B(kit, "cafe.back", (0.2, yb - ya, CEIL), (x1 + 0.1, (ya + yb) / 2, CEIL / 2), M["plaster_w"])
    for k, y in enumerate((ya, yb)):
        B(kit, f"cafe.side{k}", (x1 - x0, 0.2, CEIL), ((x0 + x1) / 2, y + (0.1 if k == 0 else -0.1), CEIL / 2), M["plaster"])
    B(kit, "cafe.ceil", (x1 - x0, yb - ya, 0.15), ((x0 + x1) / 2, (ya + yb) / 2, CEIL + 0.07), M["plaster"])
    B(kit, "cafe.glow", (0.05, 4.0, 1.2), (x1 - 0.1, -4.5, 1.9), M["warm_panel"])
    # the counter, its back shelf with cups, a pendant
    B(kit, "cafe.counter", (0.7, 4.6, 1.0), (6.9, -4.6, 0.5), M["oak_d"], bevel=0.03)
    B(kit, "cafe.counter.top", (0.8, 4.7, 0.05), (6.9, -4.6, 1.025), M["oak"], bevel=0.02)
    B(kit, "cafe.urn", (0.3, 0.3, 0.5), (6.9, -3.2, 1.3), M["brass"], bevel=0.05)
    for k in range(5):
        kit.cyl(f"cafe.cup{k}", 0.05, 0.07, (6.85, -5.6 + k * 0.3, 1.09), M["cup"], n=10)
    for k, y in enumerate((-3.0, -6.0)):
        kit.cyl(f"cafe.pend{k}", 0.2, 0.2, (6.0, y, 2.6), M["glow"], n=14, r2=0.1)
    # three tall tables outside, each with a cup or a plate of cake
    for k, y in enumerate((-3.0, -5.2, -7.0)):
        t = kit.empty(f"table{k}", (2.7, y, 0))
        kit.cyl("t.top", 0.5, 0.05, (0, 0, 1.0), M["oak"], t, n=20)
        kit.cyl("t.leg", 0.04, 1.0, (0, 0, 0.5), M["iron"], t, n=8)
        kit.cyl("t.foot", 0.28, 0.04, (0, 0, 0.02), M["iron"], t, n=16)
        for j in range(2):
            a = j * math.pi
            px, py = 0.22 * math.cos(a + 1.0), 0.22 * math.sin(a + 1.0)
            kit.cyl("t.plate", 0.11, 0.015, (px, py, 1.035), M["plate"], t, n=14)
            kit.cyl("t.cake", 0.07, 0.07, (px, py, 1.08), M["cake"], t, n=12, r2=0.05)
    return {}


def build_shop_front(kit, M):
    s = -1
    walls_with_openings(kit, "ushop.wall", "x", -4.1, SHOP_Y0, SHOP_Y1, 3.0,
                        [(1.4, 2.4, 0.0, 2.25), (-2.2, 0.9, 0.85, 2.35)], 0.2, M["green"])
    B(kit, "ushop.fascia", (0.16, SHOP_Y1 - SHOP_Y0, 0.7), (-4.0, (SHOP_Y0 + SHOP_Y1) / 2, 3.12), M["green_d"])
    B(kit, "ushop.sill", (0.3, 3.2, 0.06), (-3.95, -0.65, 0.85), M["brass"])
    for k, y in enumerate((-1.2, -0.15)):
        B(kit, f"ushop.mull{k}", (0.06, 0.05, 1.5), (-3.98, y, 1.6), M["brass"])
    B(kit, "ushop.step", (0.4, 1.2, 0.05), (-3.85, 1.9, 0.025), M["stone_d"])
    B(kit, "window seat", (0.5, 2.5, 0.5), (-5.45, -0.8, 0.25), M["oak_d"], bevel=0.02)
    B(kit, "ushop.lintel", (0.1, 1.0, 0.1), (-4.1, 1.9, 2.3), M["brass"])
    sign_picture(kit, M, "spool", -3.9, 0.3, 3.12, -1)
    # the bell over the door
    bell = kit.empty("door bell", (-4.35, 1.9, 2.25))
    kit.cyl("bell.cup", 0.08, 0.1, (0, 0, -0.08), M["brass"], bell, n=12, r2=0.03)
    kit.cyl("bell.cord", 0.01, 0.15, (0, 0, 0.02), M["brass"], bell, n=6)


# ------------------------------------------------------------------------------------------------ Uncle's shop


def bench(kit, M, name, y):
    r = kit.empty(name, (-12.6, y, 0))
    B(kit, "body", (2.1, 0.8, 0.62), (0, 0, 0.5), M["oak_d"], r, bevel=0.02)
    B(kit, "top", (2.3, 0.95, 0.1), (0, 0, 0.86), M["oak_x"], r, bevel=0.015)
    for sx in (-1, 1):
        for sy in (-1, 1):
            kit.cyl("foot", 0.075, 0.2, (sx * 1.0, sy * 0.34, 0.1), M["brass"], r, n=12, r2=0.1)
    return r


def lamp(kit, M, name, x, y, z, tx, ty, tz, energy, spot=75):
    """A green-shaded bench lamp: a brass arm and a cone shade, a spot under it."""
    r = kit.empty(f"{name} body", (x, y, 0.91))
    kit.cyl("base", 0.1, 0.03, (0, 0, 0.015), M["brass"], r, n=14)
    kit.cyl("arm", 0.013, z - 0.91, (0, 0, (z - 0.91) / 2), M["brass"], r, n=8)
    kit.cyl("shade", 0.2, 0.17, (0, 0, z - 0.91), M["lamp_green"], r, n=18, r2=0.06)
    bulb = kit.cyl("bulb", 0.05, 0.05, (0, 0, z - 0.91 - 0.06), M["glow"], r, n=10)
    L = kit.light(name, "SPOT", (x, y, z - 0.1), energy, "#ffc27a", spot=spot, blend=0.6, size=0.06)
    kit.aim(L, (tx, ty, tz))
    return {"root": r, "bulb": bulb}


def build_shop(kit, M, ctx):
    xm = (SHOP_X0 + SHOP_X1) / 2
    wy = (SHOP_Y0 + SHOP_Y1) / 2
    wl = SHOP_Y1 - SHOP_Y0
    kit.plane("shop floor", (SHOP_X1 - SHOP_X0, wl), (xm, wy, 0.004), M["floor"])
    B(kit, "shop back", (0.2, wl, CEIL), (SHOP_X0 - 0.1, wy, CEIL / 2), M["plaster"])
    B(kit, "shop wall -y", (SHOP_X1 - SHOP_X0, 0.2, CEIL), (xm, SHOP_Y0 - 0.1, CEIL / 2), M["plaster"])
    # the +y wall has the side window: x -13.9 .. -11.3, z 0.9 .. 2.4
    walls_with_openings(kit, "shop wall +y", "y", SHOP_Y1 + 0.1, SHOP_X0, SHOP_X1, CEIL, [(-13.9, -11.3, 0.9, 2.4)], 0.2, M["plaster"])
    B(kit, "shop ceiling", (SHOP_X1 - SHOP_X0, wl, 0.15), (xm, wy, CEIL + 0.07), M["plaster"])
    for k, x in enumerate((-6.0, -9.0, -12.0, -15.0)):
        B(kit, f"beam{k}", (0.22, wl, 0.2), (x, wy, CEIL - 0.1), M["oak_d"])
    # the side window: frame, and a cool light box behind it (a side passage)
    B(kit, "win.sill", (2.8, 0.34, 0.05), (-12.6, SHOP_Y1 - 0.05, 0.9), M["oak"])
    for k, x in enumerate((-13.9, -12.6, -11.3)):
        B(kit, f"win.mull{k}", (0.07, 0.1, 1.5), (x, SHOP_Y1 + 0.05, 1.65), M["oak_d"])
    B(kit, "win.top", (2.7, 0.1, 0.07), (-12.6, SHOP_Y1 + 0.05, 2.4), M["oak_d"])
    B(kit, "passage light", (3.2, 0.05, 2.4), (-12.6, SHOP_Y1 + 0.9, 1.65), M["window_cool"])
    ctx["passage_panel"] = bpy.data.objects["passage light"]
    # the counter, its brass bell, the finished clothes
    B(kit, "counter", (0.7, 2.9, 1.0), (-6.75, -1.15, 0.5), M["oak_d"], bevel=0.03)
    B(kit, "counter top", (0.85, 3.0, 0.06), (-6.75, -1.15, 1.03), M["oak"], bevel=0.02)
    kit.cyl("counter bell", 0.07, 0.07, (-6.7, -0.2, 1.1), M["brass"], n=14, r2=0.02)
    B(kit, "bell knob", (0.03, 0.03, 0.03), (-6.7, -0.2, 1.17), M["brass"])
    for k in range(6):
        B(kit, f"cover{k}", (0.34, 0.12, 1.35), (-8.4 - k * 0.38, SHOP_Y0 + 0.3, 1.2), M["paper"], bevel=0.03)
    B(kit, "rail along x", (2.4, 0.04, 0.04), (-9.4, SHOP_Y0 + 0.3, 1.95), M["brass"])
    # packing boxes stacked on the counter, more each day (ctx["boxes"] is shown by count)
    # opening Uncle shot only (cue uncle_shot): a dark green wall behind him and a warm side key
    ctx["backdrop"] = B(kit, "uncle backdrop", (0.06, 3.2, 3.0), (-8.55, -0.6, 1.5), pbr(kit, "backdrop", "#26402f", 0.9))
    ctx["backdrop"].hide_render = True
    ctx["ukey"] = kit.light("uncle key", "SPOT", (-6.3, -2.3, 2.2), 110.0, "#ffd9a8", spot=55, blend=0.6, size=0.3)
    kit.aim(ctx["ukey"], (-7.75, -1.0, 1.45))
    ctx["boxes"] = []
    spots = [(-6.7, -2.2, 0), (-6.7, -1.75, 0), (-6.7, -2.2, 1), (-6.7, -1.75, 1), (-6.7, 0.05, 0), (-6.7, -2.2, 2),
             (-6.7, 0.05, 1), (-6.7, -1.75, 2)]
    for k, (x, y, lv) in enumerate(spots):
        m = M["kraft"] if k % 2 == 0 else M["kraft_d"]
        ctx["boxes"].append(B(kit, f"pack{k}", (0.45, 0.5, 0.42), (x, y, 1.06 + 0.21 + lv * 0.43), m, bevel=0.015))
    # the two benches, lamps
    bench(kit, M, "bench U", -1.0)
    bench(kit, M, "bench M", 1.0)
    ctx["lamp_m"] = lamp(kit, M, "lamp m", -13.45, 1.2, 1.55, -12.6, 2.7, 1.2, 520.0, spot=80)
    ctx["lamp_u"] = lamp(kit, M, "lamp u", -11.9, -1.15, 1.5, -12.6, -1.0, 0.95, 260.0, spot=80)
    # the pendant light over the workroom
    kit.cyl("pendant cord", 0.01, 0.35, (-12.6, 0.2, CEIL - 0.17), M["iron"], n=6)
    ctx["pendant"] = kit.cyl("pendant bulb", 0.09, 0.14, (-12.6, 0.2, CEIL - 0.45), M["glow"], n=14)
    # the two apron hooks on the back wall, and the aprons
    for k, y in enumerate((-0.6, -0.05)):
        B(kit, f"hook{k}", (0.12, 0.04, 0.04), (SHOP_X0 + 0.07, y, 1.55), M["brass"])
    ctx["aprons"] = [B(kit, f"apron{k}", (0.05, 0.34, 0.7), (SHOP_X0 + 0.1, y, 1.2), M["canvas"], bevel=0.01)
                     for k, y in enumerate((-0.6, -0.05))]
    # the stair: x -15.9 .. -14.9, rising toward +y
    n = 12
    for k in range(n):
        y = 0.2 + k * 0.24
        B(kit, f"step{k}", (1.0, 0.26, 0.06), (-15.4, y, 0.2 * (k + 1)), M["oak"], bevel=0.01)
        B(kit, f"riser{k}", (1.0, 0.04, 0.2), (-15.4, y - 0.12, 0.2 * k + 0.1), M["oak_d"])
    B(kit, "stair rail", (0.05, 3.0, 0.05), (-14.85, 1.7, 1.55), M["brass"], rot=(math.radians(-38), 0, 0))
    B(kit, "stair stringer", (0.06, 3.1, 0.3), (-14.9, 1.7, 1.05), M["oak_d"], rot=(math.radians(-38), 0, 0))
    B(kit, "stair dark", (1.1, 0.1, 1.2), (-15.4, 3.1, 2.5), M["black"])
    # the fitting room: a partition, the hook, the curtain on its rail
    B(kit, "fit partition", (1.8, 0.07, CEIL), (-15.1, -0.87, CEIL / 2), M["plaster"])
    B(kit, "fit floor", (1.7, 1.7, 0.01), (-15.15, -1.75, 0.012), M["oak_x"])
    B(kit, "fit hook plate", (0.03, 0.12, 0.2), (SHOP_X0 + 0.02, HANG_AT[1], 2.2), M["brass"])
    B(kit, "fit hook", (0.2, 0.03, 0.03), (SHOP_X0 + 0.12, HANG_AT[1], 2.2), M["brass"])
    B(kit, "curtain rail", (0.04, 1.75, 0.04), (CURTAIN_X, -1.73, 2.5), M["brass"])
    cur = kit.empty("curtain", (CURTAIN_X, -2.58, 0))     # gathered toward y = -2.6 when open (scale y)
    ctx["curtain"] = cur
    for k in range(9):
        d = 0.05 if k % 2 else 0.0
        B(kit, f"fold{k}", (0.07 + d, 1.72 / 9 + 0.01, 2.3), ((d / 2), 0.1 + k * 1.72 / 9 + 0.0, 1.35), M["ochre"], cur)
        kit.cyl(f"ring{k}", 0.04, 0.012, (0, 0.1 + k * 1.72 / 9, 2.5), M["brass"], cur, n=10, rot=(math.radians(90), 0, 0))
    # the hanger: a wooden hanger on the hook (shown while the suit hangs; swings a little at L43)
    hang = kit.empty("hanger", (SHOP_X0 + 0.32, HANG_AT[1], 2.2))
    ctx["hanger"] = hang
    B(kit, "hanger.bar", (0.04, 0.6, 0.035), (0.0, 0.0, -0.3), M["oak"], hang)
    B(kit, "hanger.a", (0.04, 0.4, 0.035), (0.0, -0.15, -0.14), M["oak"], hang, rot=(math.radians(35), 0, 0))
    B(kit, "hanger.b", (0.04, 0.4, 0.035), (0.0, 0.15, -0.14), M["oak"], hang, rot=(math.radians(-35), 0, 0))
    B(kit, "hanger.hook", (0.2, 0.025, 0.025), (-0.1, 0.0, -0.04), M["brass"], hang)
    # props: the tape measure (coil, outline), the pincushion, the cloth, the canvas, the phone, the bench tally
    coil = kit.empty("tape coil", (-12.9, 0.85, 0.92))
    for k in range(5):
        kit.cyl(f"coil{k}", 0.1 - k * 0.012, 0.025, (0, 0, k * 0.026), M["yellow"], coil, n=18)
    ctx["coil"] = coil
    pc = kit.empty("pincushion", (-12.25, 0.95, 0.92))
    B(kit, "cush", (0.14, 0.1, 0.06), (0, 0, 0.03), M["red"], pc, bevel=0.02)
    for k in range(5):
        kit.cyl(f"pinhead{k}", 0.008, 0.012, (-0.04 + k * 0.02, 0.0, 0.07), M["brass"], pc, n=6)
    ctx["pincushion"] = pc
    ou = kit.empty("tape outline", (ME_ST[0], ME_ST[1], 0.015))
    segs = [((0, 0.1), (0, 1.55)), ((-0.25, 1.0), (-0.25, 0.0)), ((0.25, 1.0), (0.25, 0.0)), ((-0.25, 1.0), (0.25, 1.0)),
            ((-0.25, 1.0), (-0.52, 0.55)), ((0.25, 1.0), (0.52, 0.55)), ((-0.25, 0.0), (0.25, 0.0)), ((-0.25, 1.4), (0.25, 1.4))]
    for k, ((ax, az), (bx, bz)) in enumerate(segs):
        # the outline is drawn on the floor: along x and y (the person's height runs toward -y)
        x0, y0, x1, y1 = ax, -az * 0.9, bx, -bz * 0.9
        ln = math.hypot(x1 - x0, y1 - y0)
        B(kit, f"outline{k}", (ln + 0.02, 0.025, 0.006), ((x0 + x1) / 2, (y0 + y1) / 2, 0), M["yellow"], ou,
          rot=(0, 0, math.atan2(y1 - y0, x1 - x0)))
    for k in range(10):
        a = 2 * math.pi * k / 10
        B(kit, f"outhead{k}", (0.15, 0.025, 0.006), (0.14 * math.cos(a), -1.62 + 0.14 * math.sin(a), 0), M["yellow"], ou,
          rot=(0, 0, a + math.pi / 2))
    ctx["outline"] = ou
    cl = kit.empty("cloth", (-12.6, 1.0, 0.92))
    B(kit, "cloth.sheet", (0.9, 0.7, 0.02), (0, 0, 0.01), M["pin"], cl)
    for k, (a, b, c_, d_) in enumerate([(-0.3, -0.25, 0.3, -0.25), (-0.3, -0.25, -0.35, 0.15), (0.3, -0.25, 0.35, 0.15),
                                        (-0.35, 0.15, -0.15, 0.3), (0.35, 0.15, 0.15, 0.3), (-0.15, 0.3, 0.15, 0.3)]):
        ln = math.hypot(c_ - a, d_ - b)
        B(kit, f"chalkln{k}", (ln, 0.012, 0.004), ((a + c_) / 2, (b + d_) / 2, 0.022), M["chalk"], cl,
          rot=(0, 0, math.atan2(d_ - b, c_ - a)))
    ctx["cloth"] = cl
    cv = kit.empty("canvas", (-12.6, 1.0, 0.92))
    B(kit, "canvas.sheet", (0.9, 0.7, 0.02), (0, 0, 0.01), M["canvas"], cv)
    B(kit, "canvas.line", (0.7, 0.012, 0.004), (0, -0.05, 0.022), M["chalk"], cv)
    ctx["canvas"] = cv
    ph = kit.empty("phone", (-6.75, -0.6, 1.07))
    B(kit, "phone.body", (0.09, 0.16, 0.01), (0, 0, 0.005), M["iron"], ph, bevel=0.01)
    B(kit, "phone.screen", (0.075, 0.14, 0.004), (0, 0, 0.011), M["screen"], ph)
    ctx["phone"] = ph
    # the sign card hung on the door's inside: a spool on one side, plain on the other (turns at L69)
    sc = kit.empty("sign card", (-4.3, 1.9, 1.75))
    # the plain face (toward the shop, x < 0) is bare; the face that turns to the camera at L69.3 (x > 0) carries a
    # big spool-and-needle picture on a dark green panel, every part at least 1.2 cm proud (no shared planes)
    B(kit, "card", (0.012, 0.34, 0.44), (0, 0, 0), M["leaf"], sc, bevel=0.004)
    B(kit, "card.panel", (0.006, 0.26, 0.34), (0.012, 0, 0), M["green_d"], sc)
    kit.cyl("card.spool", 0.055, 0.15, (0.024, 0, 0), M["thread"], sc, n=12)
    for k, dz in enumerate((-0.085, 0.085)):
        kit.cyl(f"card.fl{k}", 0.09, 0.02, (0.026, 0, dz), M["brass"], sc, n=14)
    B(kit, "card.needle", (0.008, 0.012, 0.3), (0.03, 0.1, 0.0), M["brass"], sc)
    ctx["sign_card"] = sc
    # the lore tally: two short upright charcoal strokes pressed into the bench foot (one shot, not narrated)
    for k, dy in enumerate((-0.03, 0.03)):
        B(kit, f"tally{k}", (0.014, 0.016, 0.1), (FOOT[0] + 0.099, FOOT[1] + dy, 0.12), M["coin_dark"])
    ctx["tally_dust"] = [kit.sphere(f"dust{k}", 0.006, (0, 0, 0), M["dust"], seg=6) for k in range(7)]
    for d in ctx["tally_dust"]:
        d.hide_render = True
    # a few CC0 pieces to fill the bare corners (kit.prop): a plant at the door, a stool by the bench, a bookshelf
    kit.prop("houseplant_1", (-4.75, 2.7, 0), height=0.8, rot=20)
    kit.prop("stool", (-10.7, -2.2, 0), rot=15, tint="#c9b08a")
    kit.prop("bookshelf", (-8.2, SHOP_Y1 - 0.25, 0), height=1.9, rot=180, tint="#b89a74")
    # lights
    ctx["lights"] = {}
    L = kit.light("sun", "SUN", (14, 8, 16), 3.2, "#ffe2a8", size=0.08)
    kit.aim(L, (0, 0, 0))
    L = kit.light("sun_eve", "SUN", (16, -3, 7), 1.0, "#ffd8a8", size=0.1)
    kit.aim(L, (0, 0, 0))
    L = kit.light("shop_front", "AREA", (-4.7, -0.5, 2.5), 260.0, "#fff1d6", size=3.0)
    kit.aim(L, (-9.5, 0.2, 1.0))
    L = kit.light("shop_front_eve", "AREA", (-4.7, -0.5, 2.5), 110.0, "#ffd9a8", size=3.0)
    kit.aim(L, (-9.5, 0.2, 1.0))
    L = kit.light("shop_mid", "POINT", (-9.0, 0.5, 2.9), 240.0, "#ffe6bf", size=0.5)
    L = kit.light("shop_work", "POINT", (-12.6, 0.0, 2.9), 220.0, "#ffe6bf", size=0.5)
    L = kit.light("passage", "AREA", (-12.6, 3.5, 1.6), 700.0, "#86a2d2", size=2.4)
    kit.aim(L, (-12.6, 0.5, 1.0))
    L = kit.light("ceiling", "POINT", (-12.6, 0.2, CEIL - 0.45), 600.0, "#ffd9a0", size=0.12)
    L = kit.light("stair_spill", "POINT", (-15.4, 2.2, 2.3), 160.0, "#ffbd78", size=0.2)
    L = kit.light("fit_light", "POINT", (-14.8, -1.7, 2.6), 160.0, "#dfe6f0", size=0.2)
    kit.light("porch", "POINT", (-4.9, 1.2, 2.5), 160.0, "#ffd29a", size=0.2)
    L = kit.light("tally", "SPOT", (-10.9, 0.1, 0.9), 60.0, "#fff0e0", spot=50, blend=0.5, size=0.05)
    kit.aim(L, (FOOT[0], FOOT[1], 0.15))
    L = kit.light("arcade_fill", "AREA", (0, -6, 4.8), 500.0, "#e8f0ff", size=6.0)
    kit.aim(L, (0, -6, 0))
    L = kit.light("empty_key", "SPOT", (-10.2, 1.4, 2.6), 520.0, "#ffe2c0", spot=75, blend=0.7, size=0.3)
    kit.aim(L, (-12.6, 2.8, 0.8))
    L = kit.light("cafe_in", "AREA", (5.4, -4.5, 2.9), 300.0, "#ffe2b0", size=3.0)
    kit.aim(L, (6.0, -4.5, 0))


# ------------------------------------------------------------------------------------------------ the rooms above


def room(kit, M, name, x0, x1, y0, y1, h=2.7, floor=None):
    xm, ym = (x0 + x1) / 2, (y0 + y1) / 2
    kit.plane(f"{name}.floor", (x1 - x0, y1 - y0), (xm, ym, 0.004), floor or M["floor"])
    B(kit, f"{name}.ceil", (x1 - x0, y1 - y0, 0.15), (xm, ym, h + 0.07), M["plaster"])
    B(kit, f"{name}.w-x", (0.2, y1 - y0, h), (x0 - 0.1, ym, h / 2), M["plaster_w"])
    B(kit, f"{name}.w+x", (0.2, y1 - y0, h), (x1 + 0.1, ym, h / 2), M["plaster_w"])
    B(kit, f"{name}.w-y", (x1 - x0, 0.2, h), (xm, y0 - 0.1, h / 2), M["plaster_w"])
    B(kit, f"{name}.w+y", (x1 - x0, 0.2, h), (xm, y1 + 0.1, h / 2), M["plaster_w"])


def build_rooms(kit, M, ctx):
    # the sitting room: a small tall table with two cups, a lamp, a window, a cupboard
    room(kit, M, "sit", 40.0, 45.0, -2.5, 2.5)
    t = kit.empty("sit table", (42.5, 0, 0))
    kit.cyl("top", 0.5, 0.05, (0, 0, 0.95), M["oak"], t, n=22)
    kit.cyl("leg", 0.05, 0.95, (0, 0, 0.47), M["oak_d"], t, n=8)
    kit.cyl("foot", 0.3, 0.04, (0, 0, 0.02), M["oak_d"], t, n=18)
    for k, a in enumerate((90, 270)):
        px, py = 0.25 * math.cos(math.radians(a)), 0.25 * math.sin(math.radians(a))
        kit.cyl("cup", 0.05, 0.08, (px, py, 1.02), M["cup"], t, n=12)
    ctx["ticket"] = B(kit, "ticket", (0.09, 0.05, 0.004), (42.6, 0.05, 0.98), M["leaf"])
    B(kit, "sit.cupboard", (0.5, 1.6, 2.0), (44.7, -1.6, 1.0), M["oak_d"], bevel=0.02)
    B(kit, "sit.sidetable", (0.5, 0.5, 0.8), (44.6, 1.6, 0.4), M["oak_d"], bevel=0.02)
    kit.cyl("sit.lampbase", 0.08, 0.1, (44.6, 1.6, 0.85), M["brass"], n=12)
    kit.cyl("sit.lampshade", 0.2, 0.28, (44.6, 1.6, 1.1), M["glow"], n=16, r2=0.12)
    B(kit, "sit.window", (0.05, 1.6, 1.2), (44.95, 0.2, 1.55), M["window_night"])
    for k, y in enumerate((-0.6, 0.2, 1.0)):
        B(kit, f"sit.win.m{k}", (0.07, 0.05, 1.3), (44.93, y, 1.55), M["oak_d"])
    B(kit, "sit.win.t", (0.07, 1.7, 0.06), (44.93, 0.2, 2.18), M["oak_d"])
    B(kit, "sit.win.b", (0.1, 1.7, 0.06), (44.93, 0.2, 0.93), M["oak_d"])
    kit.light("sit_lamp", "POINT", (44.4, 1.6, 1.35), 110.0, "#ffbf80", size=0.15)
    L = kit.light("sit_fill", "AREA", (42.5, 0, 2.5), 110.0, "#ffd8a8", size=2.0)
    kit.aim(L, (42.5, 0, 0))
    # his bedroom and mine: the bed, the peg rail
    room(kit, M, "bed", 60.0, 64.5, -2.5, 2.5)
    B(kit, "bed.frame", (2.1, 1.15, 0.45), (62.9, 0.0, 0.225), M["oak_d"], bevel=0.02)
    B(kit, "bed.mattress", (2.0, 1.05, 0.2), (62.9, 0.0, 0.55), M["white"], bevel=0.05)
    B(kit, "bed.pillow", (0.45, 0.8, 0.12), (63.75, 0.0, 0.72), M["white"], bevel=0.05)
    ctx["blanket"] = B(kit, "bed.blanket", (1.55, 1.15, 0.28), (62.35, 0.0, 0.75), pbr(kit, "blanket", "#6a7c88", 0.9), bevel=0.08)
    B(kit, "bed.headboard", (0.1, 1.25, 1.1), (63.95, 0.0, 0.7), M["oak_d"], bevel=0.02)
    B(kit, "bed.pegrail", (2.0, 0.06, 0.08), (62.5, -2.35, 1.7), M["oak_d"])
    for k in range(4):
        B(kit, f"bed.peg{k}", (0.04, 0.12, 0.04), (61.8 + k * 0.45, -2.3, 1.7), M["brass"])
    B(kit, "bed.window", (1.4, 0.05, 1.2), (62.0, 2.45, 1.6), M["window_night"])
    B(kit, "bed.win.m", (0.06, 0.07, 1.3), (62.0, 2.43, 1.6), M["oak_d"])
    B(kit, "bed.win.t", (1.5, 0.07, 0.06), (62.0, 2.43, 2.25), M["oak_d"])
    B(kit, "bed.win.b", (1.5, 0.1, 0.06), (62.0, 2.43, 0.95), M["oak_d"])
    B(kit, "bed.rug", (1.2, 1.6, 0.012), (60.9, 0.2, 0.01), pbr(kit, "rug", "#7d4f3c", 0.95))
    kit.light("bed_win", "AREA", (62.0, 2.2, 1.7), 320.0, "#9bb4d6", size=1.4)
    kit.aim(kit.LIGHTS["bed_win"]["obj"], (62.0, 0.0, 0.8))
    # the train: a window wall with the city sliding by
    room(kit, M, "train", 80.0, 84.0, -2.2, 1.6, h=2.4, floor=pbr(kit, "train floor", "#3e403f", 0.7))
    walls = walls_with_openings
    B(kit, "train.seat", (2.6, 0.55, 0.45), (82.0, 1.2, 0.225), pbr(kit, "seat", "#4a5a6a", 0.9))
    B(kit, "train.seatback", (2.6, 0.12, 0.6), (82.0, 1.5, 0.85), pbr(kit, "seat back", "#43525f", 0.9))
    kit.cyl("train.pole", 0.025, 2.4, (81.2, -0.6, 1.2), M["iron"], n=8)
    kit.cyl("train.strap", 0.01, 0.4, (82.5, -0.2, 2.1), M["iron"], n=6)
    ctx["city"] = kit.empty("city", (0, 0, 0))
    rng = np.random.default_rng(47)
    x = 60.0
    k = 0
    while x < 130.0:
        w, h, d = rng.uniform(1.2, 3.0), rng.uniform(2.0, 7.0), rng.uniform(1.0, 2.0)
        kit.box(f"blk{k}", (w, d, h), (x + w / 2, 4.2 + d / 2 + rng.uniform(0, 2.5), h / 2 - 0.5),
                M["city"] if k % 2 else M["city_d"], ctx["city"])
        x += w + rng.uniform(0.05, 0.5)
        k += 1
    B(kit, "train.sky", (40.0, 0.1, 12.0), (82.0, 14.0, 4.0), M["sky"])
    B(kit, "train.glass.t", (4.0, 0.4, 0.5), (82.0, 1.6, 2.15), M["iron"])
    B(kit, "train.glass.b", (4.0, 0.4, 0.55), (82.0, 1.6, 0.3), M["iron"])
    for k in range(3):
        B(kit, f"train.m{k}", (0.12, 0.4, 1.4), (80.2 + k * 1.8, 1.6, 1.2), M["iron"])
    kit.light("train_in", "AREA", (82.0, -0.3, 2.3), 80.0, "#dfe6ee", size=2.0)
    kit.aim(kit.LIGHTS["train_in"]["obj"], (82.0, 0.5, 0.5))
    kit.light("train_win", "AREA", (82.0, 2.6, 1.5), 140.0, "#cfd8e2", size=2.5)
    kit.aim(kit.LIGHTS["train_win"]["obj"], (82.0, 0.3, 1.2))


# ------------------------------------------------------------------------------------------------ the Empty


def funnel_mesh(kit, name, r0, r1, thick, h, hf, mat_out, mat_in, parent, n=48):
    """The raised open collar: a flared ring wall (radius r0 at the shoulders, r1 at the top). Its top edge is high at
    the back (h) and sweeps down to hf at the front (-y), so the dark inside shows over the low front."""
    verts, faces_ = [], []

    def top(a):
        d = math.atan2(math.sin(a + math.pi / 2), math.cos(a + math.pi / 2))
        w = (1 - math.cos(d)) / 2
        return hf + (h - hf) * w ** 1.3

    for k in range(n):
        a = 2 * math.pi * k / n
        c, s_ = math.cos(a), math.sin(a)
        zt = top(a)
        f = zt / h
        ro = r0 + (r1 - r0) * f
        ri = ro - thick
        verts += [(r0 * c, r0 * s_, 0.0), (ro * c, ro * s_, zt), (ri * c, ri * s_, zt), ((r0 - thick) * c, (r0 - thick) * s_, 0.0)]
    for k in range(n):
        a, b = 4 * k, 4 * ((k + 1) % n)
        faces_ += [(a, b, b + 1, a + 1), (a + 1, b + 1, b + 2, a + 2), (a + 2, b + 2, b + 3, a + 3)]
    ob = kit.mesh_obj(name, verts, faces_, mat_out, parent, smooth=True)
    ob.data.materials.append(mat_in)
    for i, p in enumerate(ob.data.polygons):
        p.material_index = 1 if i % 3 == 2 else 0
    return ob


def sleeve_mesh(kit, name, mat_out, mat_in, parent, n=20):
    """An empty cloth sleeve: a softened tube tapering from the shoulder to a narrower open cuff, with a dark lining
    running up inside the cuff and a slight sag at the elbow."""
    prof = [(0.28, 0.54, 0.0), (-0.1, 0.52, 0.0), (-0.7, 0.47, 0.03), (-1.2, 0.42, 0.07), (-1.65, 0.38, 0.1)]  # z, r, y-sag
    verts, faces_ = [], []
    rings = [(z, r, yo) for z, r, yo in prof]
    for z, r, yo in rings:
        for k in range(n):
            a = 2 * math.pi * k / n
            verts.append((r * math.cos(a), r * 0.92 * math.sin(a) + yo, z))
    for z, r, yo in (rings[-1], (-1.5, 0.3, 0.1), (-1.15, 0.27, 0.08)):   # the inner lining, going up inside
        rr = r - 0.04 if z == rings[-1][0] else r
        for k in range(n):
            a = 2 * math.pi * k / n
            verts.append((rr * math.cos(a), rr * 0.92 * math.sin(a) + yo, z))
    rows = len(rings) + 3
    for i in range(rows - 1):
        for k in range(n):
            a, b = i * n + k, i * n + (k + 1) % n
            faces_.append((a, b, b + n, a + n))
    # the last ring of the outer (index len(rings)-1) joins the first inner ring through the cuff rim
    ob = kit.mesh_obj(name, verts, faces_, mat_out, parent, smooth=True)
    ob.data.materials.append(mat_in)
    nout = len(rings) - 1
    for i, p_ in enumerate(ob.data.polygons):
        p_.material_index = 1 if i >= (nout + 1) * n else 0
    # cap the shoulder end
    cap = kit.mesh_obj(name + "cap", [(0, 0, 0.28)] + [verts[k] for k in range(n)],
                       [(0, 1 + (k + 1) % n, 1 + k) for k in range(n)], mat_out, parent, smooth=True)
    return ob


def build_empty(kit, M, ctx):
    sc = S * 1.2
    root = kit.empty("empty", (0, 0, 0))
    root.scale = (sc, sc, sc)
    e = {"root": root}
    legs = []
    for sx in (-1, 1):
        leg = kit.empty(f"empty.leg{sx}", (sx * 0.5, 0, 2.0), root)
        kit.box(f"empty.legm{sx}", (0.98, 1.0, 1.72), (0, 0, -0.86), M["trouser"], leg, bevel=0.08)
        kit.box(f"empty.cuff{sx}", (1.02, 1.04, 0.14), (0, 0, -1.65), M["trouser"], leg, bevel=0.05)
        kit.box(f"empty.shoe{sx}", (0.99, 1.45, 0.3), (0, -0.2, -1.85), M["shoe"], leg, bevel=0.1)
        legs.append(leg)
    torso = kit.empty("empty.torso", (0, 0, 2.0), root)
    kit.box("empty.jacket", (2.04, 1.06, 2.04), (0, 0, 1.0), M["pin"], torso, bevel=0.1)
    for sx in (-1, 1):   # lapels and a pale shirt V at the front
        kit.box(f"empty.lapel{sx}", (0.3, 0.05, 1.2), (sx * 0.42, -0.54, 1.3), M["pin"], torso, rot=(0, 0, sx * 0.3), bevel=0.02)
    kit.box("empty.shirtV", (0.5, 0.04, 0.9), (0, -0.535, 1.45), M["shirt"], torso)
    kit.box("empty.hem", (2.08, 1.1, 0.12), (0, 0, 0.06), M["pin"], torso, bevel=0.04)
    arms = []
    for sx in (-1, 1):
        arm = kit.empty(f"empty.arm{sx}", (sx * 1.5, 0, 1.75), torso)
        sleeve_mesh(kit, f"empty.sleeve{sx}", M["pin_arm"], M["void"], arm)
        arms.append(arm)
    # no head: a tall raised charcoal collar, flared, open and notched at the front. The dark notch is its mouth; the
    # two glints sit deep inside the back wall and only show down the notch (and only once the cue turns them on)
    neck = kit.empty("empty.neck", (0, 0, 2.0), torso)
    # jacket collar: a stiff stand-up ring, open to the sky; a taller pale shirt collar inside it. No hood, no cap.
    col = funnel_mesh(kit, "empty.collar", 0.66, 0.78, 0.08, 0.96, 0.74, M["pin_collar"], M["lining2"], neck)
    sh = funnel_mesh(kit, "empty.shirtcollar", 0.46, 0.54, 0.035, 0.9, 0.74, M["shirt"], M["lining2"], neck)
    for sx in (-1, 1):   # sloped suit shoulders into the collar, and two long lapels running down the chest
        kit.box(f"empty.shoulder{sx}", (0.95, 1.0, 0.3), (sx * 0.86, 0, 0.02), M["pin"], neck, rot=(0, sx * -0.32, 0), bevel=0.1)
        kit.box(f"empty.tip{sx}", (0.3, 0.05, 1.0), (sx * 0.5, -0.56, -0.15), M["pin_collar"], neck, rot=(0, sx * 0.35, 0), bevel=0.02)
    floor_ = kit.cyl("empty.voidfloor", 0.5, 0.02, (0, 0, 0.1), M["void"], neck, n=24)
    glints = []
    gm = kit.emit("#f4f0e2", 12.0, name="glint")
    for sx in (-1, 1):
        glints.append(kit.sphere(f"empty.glint{sx}", 0.04, (sx * 0.25, 0.2, 0.4), gm, neck, seg=10))
    e.update(legs=legs, torso=torso, arms=arms, neck=neck, void=[floor_], glints=glints)
    ctx["empty"] = e


POSES = {
    #        arms (fwd deg, out deg) l/r,           torso lean, head-neck tilt back, legs
    "hang": {"arm": (3, 2), "lean": 3, "tilt": 0},
    "stand": {"arm": (0, 2), "lean": 0, "tilt": 0},
    "sleeves_up": {"arm": (56, 24), "lean": 0, "tilt": 0},
    "lean": {"arm": (12, 4), "lean": 12, "tilt": 0},
}


def pose_empty(ctx, c):
    e = ctx["empty"]
    root = e["root"]
    hidden = bool(c.get("hidden", False)) or c.get("pose") is None
    root.hide_render = hidden
    for ob in root.children_recursive:
        ob.hide_render = hidden
    if hidden:
        return
    pose = c.get("pose", "stand")
    x, y = c["pos"][0], c["pos"][1]
    z = c["pos"][2] if len(c["pos"]) > 2 else 0.0
    root.location = (x, y, z)
    root.rotation_euler = (0, 0, math.radians(c.get("yaw", 0)))
    heap = pose == "heap"
    if heap:
        pose_heap(e)
    else:
        P = POSES.get(pose, POSES["stand"])
        lean = math.radians(c.get("lean", P["lean"]))
        e["torso"].location = (0, 0, 2.0)
        e["torso"].scale = (1, 1, 1)
        e["torso"].rotation_euler = (lean, 0, 0)
        for leg in e["legs"]:
            leg.location = (leg.location[0], 0, 2.0)
            leg.rotation_euler = (0, 0, 0)
        fwd, out = P["arm"]
        for arm, sx in zip(e["arms"], (-1, 1)):
            arm.rotation_euler = (-math.radians(fwd), sx * math.radians(out) * -1, 0)
        e["neck"].rotation_euler = (math.radians(c.get("tilt", P["tilt"])), 0, 0)
        e["neck"].scale = (1, 1, 0.5) if pose == "hang" else (1, 1, 1)   # limp: the collar slumps
    for ob in e["void"]:
        ob.hide_render = heap
    for ob in e["glints"]:
        ob.hide_render = heap or pose == "hang" or not c.get("glints", False)


def pose_heap(e):
    """Collapsed on the floor: trousers flat, the jacket over them, the sleeves splayed, the shoes tipped."""
    e["legs"][0].location = (-0.55, 0.2, 0.5)
    e["legs"][0].rotation_euler = (math.radians(86), 0, math.radians(8))
    e["legs"][1].location = (0.5, 0.35, 0.5)
    e["legs"][1].rotation_euler = (math.radians(94), math.radians(10), math.radians(-14))
    e["torso"].location = (0.1, -1.0, 0.62)
    e["torso"].rotation_euler = (math.radians(86), 0, math.radians(-6))
    e["torso"].scale = (1.05, 1, 0.75)
    e["arms"][0].rotation_euler = (math.radians(-100), math.radians(-35), 0)
    e["arms"][1].rotation_euler = (math.radians(-70), math.radians(40), 0)


# ------------------------------------------------------------------------------------------------ tags

TAG_W, TAG_H, TAG_T = 0.34, 0.5, 0.03


def tag_mesh(kit, M):
    w, h, t = TAG_W / 2, TAG_H / 2, TAG_T / 2
    verts = [(-w, -t, -h), (w, -t, -h), (w, -t, h), (-w, -t, h), (-w, t, -h), (w, t, -h), (w, t, h), (-w, t, h)]
    faces_ = [(0, 1, 2, 3), (5, 4, 7, 6), (4, 0, 3, 7), (1, 5, 6, 2), (3, 2, 6, 7), (4, 5, 1, 0)]
    me = bpy.data.meshes.new("tag")
    me.from_pydata(verts, [], faces_)
    me.update()
    me.materials.append(M["tag"])
    uv = me.uv_layers.new(name="UVMap")
    for poly in me.polygons:
        for li in poly.loop_indices:
            if poly.index == 0:
                x, _, z = verts[me.loops[li].vertex_index]
                uv.data[li].uv = ((x + w) / (2 * w), (z + h) / (2 * h))
            else:
                uv.data[li].uv = (0.04, 0.5)
    return me


def tag_slots(who, n_front, kind):
    """Slots (part, x, y, z, roll, pitch) in each part's rig units, in the order they appear. Torso: x +-1, y -0.5,
    z 0..2 from the hips. Arms and legs hang below their pivots."""
    rng = np.random.default_rng(sum(map(ord, who)) * 7 + 3)
    out = []

    def torso(n, zlo, zhi, xr=0.82, y=-0.53):
        for _ in range(n):
            out.append(("torso", rng.uniform(-xr, xr), y, rng.uniform(zlo, zhi), rng.uniform(-0.45, 0.45), 0.0))

    if kind == "uncle":
        # an apron first (low front), the speckle, both shoulders, his heart (slot 30), the chest rows up to the collar
        torso(3, 0.15, 0.9, 0.45, -0.6)      # 0.07 proud of the apron (no shared plane)
        torso(9, 0.1, 1.5, 0.8, -0.6)
        for _ in range(8):
            out.append(("torso", rng.uniform(-1.0, 1.0), rng.uniform(-0.3, 0.3), 2.04, rng.uniform(-0.5, 0.5), 0.0))
        for sx in (-1, 1):
            for _ in range(5):
                out.append(("torso", sx * rng.uniform(1.0, 1.3), rng.uniform(-0.3, 0.3), 1.98 - rng.uniform(0, 0.2),
                            rng.uniform(-0.5, 0.5), 0.0))
        out.append(("torso", 0.55, -0.53, 1.45, 0.1, 0.0))
        torso(14, 1.5, 1.95, 0.9, -0.6)
        torso(6, 1.7, 1.95, 0.9, -0.6)
        torso(8, 0.3, 1.9, 0.9, -0.6)
    elif kind == "chest":
        # the opening man: every tag on his chest, in view. 0..4 are on him already, 5 pops on LIE, 6 on the next beat
        for zl, xx, rl in ((0.55, -0.5, 0.2), (0.8, 0.45, -0.25), (1.05, -0.15, 0.3), (0.35, 0.3, 0.1), (1.25, -0.6, -0.15)):
            out.append(("torso", xx, -0.53, zl, rl, 0.0))
        out.append(("torso", 0.2, -0.56, 1.3, 0.12, 0.0))
        out.append(("torso", -0.35, -0.56, 1.05, -0.1, 0.0))
        torso(3, 0.3, 1.2, 0.7)
    elif kind == "lump":
        torso(22, 0.05, 1.95, 0.9)
        for part in ("arm-1", "arm1"):
            for _ in range(11):
                out.append((part, rng.uniform(-0.3, 0.3), -0.53, rng.uniform(-1.7, 0.1), rng.uniform(-0.5, 0.5), 0.0))
        for part in ("leg-1", "leg1"):
            for _ in range(10):
                out.append((part, rng.uniform(-0.25, 0.25), -0.53, rng.uniform(-1.6, -0.1), rng.uniform(-0.5, 0.5), 0.0))
        for _ in range(10):
            out.append(("torso", rng.uniform(-0.9, 0.9), 0.53, rng.uniform(0.1, 1.9), rng.uniform(-0.4, 0.4), math.pi))
    else:   # a speckle
        torso(5, 0.2, 1.8, 0.8)
        for part in ("leg-1", "leg1", "arm-1", "arm1"):
            out.append((part, rng.uniform(-0.2, 0.2), -0.53, rng.uniform(-1.4, -0.3), rng.uniform(-0.5, 0.5), 0.0))
        torso(4, 0.2, 1.8, 0.8)
    return out


def attach_tags(kit, M, ctx, tl):
    cast = ctx["tag_kinds"]
    me = tag_mesh(kit, M)
    ctx["tags"] = {}
    for who, kind in cast.items():
        parts = {p: bpy.data.objects.get(f"{who}.{p}") for p in ("torso", "arm-1", "arm1", "leg-1", "leg1")}
        if parts["torso"] is None:
            continue
        slots = tag_slots(who, 0, kind)
        items = []
        for i, (part, x, y, z, roll, flip) in enumerate(slots):
            ob = bpy.data.objects.new(f"tag.{who}.{i}", me)
            kit.link(ob, parts[part])
            items.append({"ob": ob, "part": part, "slot": (x, y, z, roll, flip), "i": i})
            ob.hide_render = True
        ctx["tags"][who] = items
    # the tag events per character, in order
    ctx["tag_events"] = {}
    for c in tl["cues"]:
        if c["name"] == "tags":
            ctx["tag_events"].setdefault(c["who"], []).append(c)
    for v in ctx["tag_events"].values():
        v.sort(key=lambda c: c["t"])


FALL_DUR = 2.4
FLOOR_LOCAL = {"torso": -2.0, "leg-1": -2.0, "leg1": -2.0, "arm-1": -3.75, "arm1": -3.75}


def tag_state(events, i, t):
    """(visible, pop 0..1, fall 0..1) for tag i at t from the character's events."""
    present, appear, fall0, rest = False, -9.0, None, False
    for c in events:
        if c["t"] > t:
            break
        if c.get("fall"):
            if i >= c["n"] and present:
                fall0 = c["t"] + 0.05 * (i % 9) + 0.02 * (i % 4)
                rest = bool(c.get("rest"))
                present = False
        else:
            n = c["n"]
            if i < n and not present:
                present, appear, fall0, rest = True, c["t"] + (0.0 if c.get("pop", True) else -1.0), None, False
            elif i >= n and present:
                present = False
                fall0 = None
    if present:
        return True, ss((t - appear) / 0.3), 0.0, False
    if fall0 is not None and t >= fall0:
        u = (t - fall0) / FALL_DUR
        if u < 1.0:
            return True, 1.0, u, rest
        if rest:     # opt-in (cue "rest": true): the tags stay lying on the floor
            return True, 1.0, 1.0, True
    return False, 0.0, 0.0, False


def animate_tags(kit, ctx, tl, t):
    for who, items in ctx.get("tags", {}).items():
        hidden = acting.state(tl, who, t)["hidden"]
        ev = ctx["tag_events"].get(who, [])
        for it in items:
            ob = it["ob"]
            if hidden:
                ob.hide_render = True
                continue
            vis, pop, fall, rest = tag_state(ev, it["i"], t)
            if not vis:
                ob.hide_render = True
                continue
            ob.hide_render = False
            x, y, z, roll, flip = it["slot"]
            pitch = 0.0
            if z > 2.0 or abs(x) > 1.0:
                pitch = -0.55 if z > 2.0 else 0.0
            if fall > 0:
                floor_z = FLOOR_LOCAL.get(it["part"], -2.0) + 0.05
                z2 = z + (floor_z - z) * (fall ** 1.5)
                x2 = x + 0.28 * math.sin(fall * 9 + it["i"])
                y2 = y - 0.5 * math.sin(math.pi * min(1.0, fall * 1.2)) - 0.1 * fall
                spin = roll + fall * 2.2 * (1 if it["i"] % 2 else -1)
                ob.location = (x2, y2, z2)
                ob.rotation_euler = (0.9 * fall + pitch, 0.4 * math.sin(fall * 6 + it["i"]), spin)
                ob.scale = (1.0, 1.0, 1.0) if (fall < 0.92 or rest) else (1 - (fall - 0.92) / 0.08,) * 3
                if rest:     # opt-in: land lying flat, scattered round the feet, and stay
                    f = fall ** 1.5
                    xt = x * 1.4 + 0.5 * math.sin(it["i"] * 2.3)
                    yt = 0.2 * y - 0.3 - 0.5 * ((it["i"] * 37) % 11) / 11
                    ob.location = (x + (xt - x) * f, y + (yt - y) * f, z + (floor_z + 0.1 - z) * f)
                    ob.rotation_euler = (1.5 * f + pitch * (1 - f), 0.0, roll + (roll * 2 + it["i"] - roll) * f)
            else:
                ob.location = (x, y, z)
                ob.rotation_euler = (pitch, 0, roll + flip)
                ob.scale = (pop, pop, pop)


# ------------------------------------------------------------------------------------------------ attachments


def attach_extras(kit, M, ctx, tl):
    """Things on cast members that rig.py doesn't make: Uncle's short grey beard and the yellow tape round his neck."""
    ctx["extras"] = {}
    for who in ("uncle", "uncle2"):
        hg = bpy.data.objects.get(f"{who}.headg")
        if hg is None:
            continue
        gr = pbr(kit, "beard grey", "#a8a8a6", 0.9)
        B(kit, f"{who}.beard", (0.62, 0.1, 0.34), (0, -0.6, -0.46), gr, hg, bevel=0.05)
        B(kit, f"{who}.beardL", (0.1, 0.3, 0.4), (-0.4, -0.46, -0.4), gr, hg, rot=(0, 0, 0.7), bevel=0.04)
        B(kit, f"{who}.beardR", (0.1, 0.3, 0.4), (0.4, -0.46, -0.4), gr, hg, rot=(0, 0, -0.7), bevel=0.04)
    tor = bpy.data.objects.get("uncle.torso")
    if tor is not None:
        tp = []
        for sx in (-1, 1):
            tp.append(B(kit, f"uncle.tape{sx}", (0.13, 0.06, 1.5), (sx * 0.45, -0.55, 1.2), M["yellow"], tor, bevel=0.01))
            tp.append(B(kit, f"uncle.tapeS{sx}", (0.55, 0.9, 0.1), (sx * 0.4, 0.0, 2.02), M["yellow"], tor, bevel=0.01))
        tp.append(B(kit, "uncle.tapeB", (0.9, 0.06, 0.13), (0, 0.55, 1.9), M["yellow"], tor))
        ctx["extras"]["tape"] = tp


# ------------------------------------------------------------------------------------------------ the build


MODES = {
    # world (strength, colour), then gains per light
    "day": {"world": (0.9, "#d4e4f4"), "sun": 1.0, "sun_eve": 0, "shop_front": 1.0, "shop_front_eve": 0, "shop_mid": 0.55,
            "shop_work": 0.5, "passage": 0.35, "stair_spill": 0, "fit_light": 0.2, "arcade_fill": 1.0, "cafe_in": 1.0},
    "night_w": {"porch": 1.0, "world": (0.03, "#101a2c"), "sun": 0, "sun_eve": 0, "shop_front": 0.22, "shop_front_eve": 0, "shop_mid": 0.25,
                "shop_work": 0, "passage": 1.0, "stair_spill": 1.0, "fit_light": 0.0, "arcade_fill": 0.0, "cafe_in": 0.3},
    "grey": {"world": (0.4, "#aab4c0"), "sun": 0, "sun_eve": 0, "shop_front": 0.8, "shop_front_eve": 0, "shop_mid": 0.8,
             "shop_work": 0.6, "passage": 0.8, "stair_spill": 0.5, "fit_light": 1.0, "arcade_fill": 0.5, "cafe_in": 0.8},
    "friday": {"world": (0.85, "#d4e4f4"), "sun": 1.0, "sun_eve": 0, "shop_front": 1.0, "shop_front_eve": 0, "shop_mid": 0.5,
               "shop_work": 0.3, "passage": 0.55, "stair_spill": 0, "fit_light": 0.2, "arcade_fill": 1.0, "cafe_in": 1.0,
               "empty_key": 1.0},
    "eve": {"tally": 1.0, "world": (0.5, "#e6d6c0"), "sun": 0, "sun_eve": 1.0, "shop_front": 0, "shop_front_eve": 1.0, "shop_mid": 0.35,
            "shop_work": 0.25, "passage": 0.3, "stair_spill": 0, "fit_light": 0.2, "arcade_fill": 0.5, "cafe_in": 1.0},
    "sat": {"world": (0.95, "#dbe9f6"), "sun": 1.0, "sun_eve": 0, "shop_front": 1.0, "shop_front_eve": 0, "shop_mid": 0.55,
            "shop_work": 0.5, "passage": 0.35, "stair_spill": 0, "fit_light": 0.2, "arcade_fill": 1.0, "cafe_in": 1.0},
    "up": {"world": (0.03, "#101a2c"), "sun": 0, "sun_eve": 0, "shop_front": 0, "shop_front_eve": 0, "shop_mid": 0,
           "shop_work": 0, "passage": 0.4, "stair_spill": 0.6, "fit_light": 0, "arcade_fill": 0.0, "cafe_in": 0.0, "bed_win": 0.3},
}
INTERIOR_ALWAYS = {"sit_lamp": 1.0, "sit_fill": 1.0, "train_in": 1.0, "train_win": 1.0, "bed_win": 1.0}


def build(kit, story, tl):
    ctx = {}
    M = materials(kit)
    ctx["M"] = M
    build_arcade(kit, M, ctx)
    build_fronts(kit, M, ctx)
    build_shop(kit, M, ctx)
    build_rooms(kit, M, ctx)
    build_empty(kit, M, ctx)
    ctx["tag_kinds"] = {k: v.get("tags", "speckle") for k, v in story["cast"].items() if v.get("tags")}
    ctx["tag_kinds"] = {k: v["tags"] for k, v in story["cast"].items() if v.get("tags")}
    ctx["world"] = bpy.context.scene.world
    ctx["inited"] = False
    return ctx


def _mode_vec(name):
    m = MODES[name]
    return m


def animate(kit, story, tl, t, ctx):
    M = ctx["M"]
    if not ctx["inited"]:
        attach_tags(kit, M, ctx, tl)
        attach_extras(kit, M, ctx, tl)
        ctx["inited"] = True
    over = {}
    us = bool((_last(_cues(tl, "uncle_shot"), t) or {"on": False}).get("on", False))
    ctx["backdrop"].hide_render = not us
    # --- the time of day: world and light gains, crossfaded
    cs = _cues(tl, "mode")
    cur = _last(cs, t)
    prev_name = "day"
    for c in cs:
        if c is cur:
            break
        prev_name = c["set"]
    if cur is None:
        cur_name, u = "day", 1.0
    else:
        cur_name = cur["set"]
        u = ss((t - cur["t"]) / max(0.3, cur.get("dur", 0.3)))
    A, Bm = {**INTERIOR_ALWAYS, **MODES[prev_name]}, {**INTERIOR_ALWAYS, **MODES[cur_name]}
    for key in set(A) | set(Bm):
        if key == "world":
            continue
        over[key] = A.get(key, 0.0) + (Bm.get(key, 0.0) - A.get(key, 0.0)) * u
    if us:     # about a stop less light on the opening Uncle shot (the cue ends on a cut, so there is no visible ramp)
        for key in list(over):
            over[key] = over[key] * 0.3
    over["uncle key"] = 1.0 if us else 0.0
    sa, ca = A["world"]
    sb, cb = Bm["world"]
    strength = (sa + (sb - sa) * u) * (0.3 if us else 1.0)
    colA, colB = kit.col(ca)[:3], kit.col(cb)[:3]
    bg = ctx["world"].node_tree.nodes["Background"]
    bg.inputs["Strength"].default_value = strength
    bg.inputs["Color"].default_value = (*[a + (b - a) * u for a, b in zip(colA, colB)], 1)
    # --- practicals: ceiling, bench lamps (each ramps over its own dur, never under 0.3 s)
    for nm in ("ceiling", "lamp m", "lamp u"):
        lc = [c for c in _cues(tl, "lamp") if c["light"] == nm]
        over[nm] = ramped(lc, "on", t, 0.0)
    # --- props
    c = _last(_cues(tl, "boxes"), t)
    n = int(c["n"]) if c else 0
    for i, ob in enumerate(ctx["boxes"]):
        ob.hide_render = i >= n
    c = _last(_cues(tl, "tape"), t) or {"state": "none"}
    st = c.get("state", "none")
    ctx["outline"].hide_render = st != "outline"
    for ob in ctx["outline"].children_recursive:
        ob.hide_render = st != "outline"
    for ob in [ctx["coil"]] + list(ctx["coil"].children):
        ob.hide_render = st != "coil"
    for ob in ctx["extras"].get("tape", []):
        ob.hide_render = st != "neck"
    c = _last(_cues(tl, "pincushion"), t) or {"on": False}
    for ob in [ctx["pincushion"]] + list(ctx["pincushion"].children):
        ob.hide_render = not c.get("on", False)
    for nm, key in (("cloth", "cloth"), ("canvas", "canvas")):
        c = _last(_cues(tl, key), t) or {"on": False}
        for ob in [ctx[nm]] + list(ctx[nm].children):
            ob.hide_render = not c.get("on", False)
    c = _last(_cues(tl, "phone"), t) or {"on": False}
    ph = ctx["phone"]
    for ob in [ph] + list(ph.children):
        ob.hide_render = not c.get("on", False)
    ph.location = (-6.75 + 0.006 * math.sin(t * 38) * (1 if c.get("on") else 0), -0.6, 1.07)
    ctx["ticket"].hide_render = not (_last(_cues(tl, "ticket"), t) or {"on": False}).get("on", False)
    c = _last(_cues(tl, "aprons"), t) or {"n": 0}
    for i, ob in enumerate(ctx["aprons"]):
        ob.hide_render = i >= c.get("n", 0)
    # the curtain: open 0..1, eased over its dur (never under 0.3 s); open = gathered to one side
    op = ramped(_cues(tl, "curtain"), "open", t, 1.0)
    ctx["curtain"].scale = (1.0, 0.16 + 0.84 * (1 - op), 1.0)
    # the hanger on the hook, and its small swing at the end
    c = _last(_cues(tl, "hanger"), t) or {"on": False}
    hg = ctx["hanger"]
    for ob in [hg] + list(hg.children):
        ob.hide_render = not c.get("on", False)
    sw = 0.0
    if c.get("on") and c.get("swing"):
        sw = 0.05 * math.sin((t - c["t"]) * 3.0) * math.exp(-(t - c["t"]) * 0.5)
    hg.rotation_euler = (sw, 0, math.radians(-150))
    # the door sign card, turning from plain to the spool
    flip = ramped(_cues(tl, "sign"), "turn", t, 0.0, 0.3)
    ctx["sign_card"].rotation_euler = (0, 0, math.radians(180 * flip))
    # the bell over the door
    c = _last(_cues(tl, "bell"), t)
    ang = 0.0
    if c and 0 <= t - c["t"] < 2.5:
        ang = 0.45 * math.exp(-(t - c["t"]) * 1.8) * math.sin((t - c["t"]) * 11)
    bpy.data.objects["door bell"].rotation_euler = (ang, 0, 0)
    # the dust past the tally
    c = _last(_cues(tl, "dust"), t)
    for k, d in enumerate(ctx["tally_dust"]):
        if c and 0 <= t - c["t"] < 2.4:
            u = (t - c["t"]) / 2.4
            d.hide_render = False
            d.location = (FOOT[0] + 0.1 + 0.02 * k, FOOT[1] - 0.06 + 0.02 * k, 0.4 - 0.34 * ((u + 0.13 * k) % 1.0))
        else:
            d.hide_render = True
    # the city sliding past the train window
    ctx["city"].location = (-((t * 4.5) % 40.0), 0, 0)
    # sitting: legs straight out in front (R6 can't bend), for the window seat
    for who in ("uncle2", "me2"):
        keys = tl["acting"].get(who, [])
        sit = False
        for k in keys:
            if "sit" in k and k["t"] <= t + 1e-9:
                sit = bool(k["sit"])
        if sit:
            for sx in (-1, 1):
                leg = bpy.data.objects.get(f"{who}.leg{sx}")
                if leg is not None:
                    leg.rotation_euler = (math.radians(-90), 0, 0)
    # --- the Empty
    c = _last(_cues(tl, "empty"), t)
    pose_empty(ctx, c or {"hidden": True})
    if c and c.get("pose") == "hang":
        ctx["empty"]["root"].location = (c["pos"][0], c["pos"][1], 0.22)   # hung from the hook: the shoes clear the floor
    # --- tags
    animate_tags(kit, ctx, tl, t)
    return over
