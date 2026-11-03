"""Dryer Nine: a small all-night laundromat, bright inside like a toy, on a dark parking lot (set for dryer-nine).

Coordinates (metres, z up, front is -y, +x is right as the camera looks +y): the floor is z = 0. The room runs
x -5.5 .. 5.5, y -4.5 (the glass front wall) .. 4.2 (the back wall). Ten front-load dryers stand along the back wall,
their door faces at y = 3.2; dryer n is at x = -4.05 + 0.9 (n - 1), so NINE is at x = 3.15 (second from the right),
eight at 2.25, ten at 4.05. A folding table at x = 2.5, y = 0.3. Outside: a dark lot, a street light, Jonah's white box
truck at x = -0.8, y = -10, the moon far out at y = -32.

THE NIGHT (the creature): the night itself, the load nine has always dried. A blocky person far too long, always folded:
a deep navy cloth body with warm star specks, a cream-yellow moon-disc face with three grey-gold craters (two are eyes
with one white highlight each, the third a shallow mouth). Posed from `night_pose` (half out of nine's door, then
leaned toward me). Inside the drum it shows as pieces of the same cloth that ride round with the drum.

Cues read here (all optional; every ramp is a "dur" in seconds, and the story keeps every light ramp at 0.3 s or more):
- pan: {"n": 0..5, "v": 0..1, "dur"} a ceiling panel (n = 5 is the one over dryer ten); amb: {"v", "dur"} the sky fill
- dl: {"v", "dur"} nine's drum light; am: {"v", "dur"} the amber glow of nine's timer
- spin: {"v": rad/s, "dur"} the drum's turn (the moon outside turns with it)
- timer: {"who": 8 | 9, "s": "0:41"} the readout; door: {"v": degrees open, "dur"}
- moon: {"z": height, "dur"} and {"show": bool}; dawn: {"v": 0..1, "dur"} sunrise through the windows
- dc: {"what": bulk|sleeve|fingers|face|hand|folded, "v": 0|1}; fill: {"v": 0..1} how full the drum is
- night: {"show": bool}; nlean: {"v": 0..1, "dur"} half out (0) to leaned in (1); pool: {"v": 0..1, "dur"}
- roll: {"v": 0|1} the paper roll of quarters on nine; coin: {"p0", "p1", "dur"} a quarter moving to the slot
- phone: {"show": bool, "pos", "yaw"}; cap: {"who": "me"|"jonah", "v": 0|1}
- shot: {"look": {"face": [pos, aim, watts], "rim": [pos, aim, watts, cone, colour]} or null} a shot's own light
"""

from __future__ import annotations

import math

import bpy
import numpy as np
from mathutils import Vector as V
from PIL import Image, ImageDraw, ImageFilter, ImageFont

from blocky import acting as AC
from blocky import faces, rig

FONT = "/home/user/blocky-stories/blocky/fonts/SchibstedGrotesk-Black.ttf"
NX = {n: -4.05 + 0.9 * (n - 1) for n in range(1, 11)}
X9 = NX[9]
FACE_Y = 3.2            # the dryers' door faces
DRUM_Z = 0.62
CEIL = 3.3
TAU = math.pi * 2

NAVY = "#1b2570"
NAVY_D = "#131a4a"
MOON = (242, 227, 160)
CRATER = (201, 182, 118)


def _ss(x):
    x = min(1.0, max(0.0, x))
    return x * x * (3 - 2 * x)


def _cues(tl, name, key=None, val=None):
    k = ("cc", name, key, val)
    C = tl.setdefault("_cc", {})
    if k not in C:
        C[k] = sorted([c for c in tl["cues"] if c["name"] == name and (key is None or c.get(key) == val)],
                      key=lambda c: c["t"])
    return C[k]


def _ramped(cs, t, key, default):
    cs = [c for c in cs if key in c]
    idx = -1
    for i, c in enumerate(cs):
        if c["t"] <= t + 1e-9:
            idx = i
    if idx < 0:
        return default

    def val(i, tt):
        c = cs[i]
        prev = default if i == 0 else val(i - 1, c["t"])
        d = c.get("dur", 0.0)
        u = 1.0 if d <= 0 else _ss((tt - c["t"]) / d)
        return prev + (c[key] - prev) * u
    return val(idx, t)


def _latest(cs, t, key, default):
    v = default
    for c in cs:
        if c["t"] <= t + 1e-9 and key in c:
            v = c[key]
    return v


# ------------------------------------------------------------------------------------------------ images


def _font(sz):
    return ImageFont.truetype(FONT, sz)


def img_number(n):
    im = Image.new("RGBA", (256, 256), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    f = _font(200)
    d.text((128, 128), str(n), font=f, fill=(255, 255, 255, 255), anchor="mm", stroke_width=12, stroke_fill=(24, 32, 96, 255))
    return im


def img_timer(s):
    im = Image.new("RGB", (320, 120), (26, 14, 6))
    d = ImageDraw.Draw(im)
    if s:
        d.text((160, 62), s, font=_font(92), fill=(255, 176, 46), anchor="mm")
    return im.filter(ImageFilter.GaussianBlur(0.6))


def img_moon(highlights=False, size=512, alpha=True):
    """The moon: a cream disc, three soft grey-gold craters (two eyes, one shallow mouth). Same as the Night's face."""
    ss = 2
    n = size * ss
    im = Image.new("RGBA", (n, n), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.ellipse([0, 0, n - 1, n - 1], fill=MOON + (255,))
    R = n / 2
    for sx in (-1, 1):
        cx, cy, rx, ry = R + sx * 0.3 * R, R - 0.12 * R, 0.17 * R, 0.21 * R
        d.ellipse([cx - rx, cy - ry, cx + rx, cy + ry], fill=CRATER + (255,))
        if highlights:
            d.ellipse([cx + 0.02 * R, cy - 0.12 * R, cx + 0.09 * R, cy - 0.05 * R], fill=(255, 255, 255, 255))
    d.arc([R - 0.34 * R, R + 0.18 * R, R + 0.34 * R, R + 0.62 * R], 20, 160, fill=CRATER + (255,), width=int(0.08 * R))
    im = im.resize((size, size), Image.LANCZOS)
    if not alpha:
        bg = Image.new("RGB", (size, size), (20, 28, 80))
        bg.paste(im, mask=im.split()[3])
        return bg
    return im


def img_phone(s):
    im = Image.new("RGB", (240, 480), (18, 22, 40))
    d = ImageDraw.Draw(im)
    d.pieslice([40, 90, 200, 250], 180, 360, fill=(255, 176, 46))      # a half sun over a line
    d.rectangle([20, 170, 220, 182], fill=(255, 226, 150))
    d.text((120, 320), s, font=_font(96), fill=(255, 255, 255), anchor="mm")
    return im


def img_clock():
    im = Image.new("RGBA", (256, 256), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.ellipse([2, 2, 253, 253], fill=(248, 248, 244, 255), outline=(40, 60, 70, 255), width=8)
    for k in range(12):
        a = k * TAU / 12
        d.line([128 + 100 * math.sin(a), 128 - 100 * math.cos(a), 128 + 116 * math.sin(a), 128 - 116 * math.cos(a)],
               fill=(40, 60, 70, 255), width=7)
    d.line([128, 128, 128 + 60 * math.sin(2.4), 128 - 60 * math.cos(2.4)], fill=(30, 40, 50, 255), width=9)
    d.line([128, 128, 128 + 90 * math.sin(5.4), 128 - 90 * math.cos(5.4)], fill=(30, 40, 50, 255), width=6)
    return im


def img_sky(kind):
    w, h = 1024, 256
    im = Image.new("RGB", (w, h))
    px = im.load()
    rng = np.random.default_rng(5)
    for y in range(h):
        u = y / (h - 1)          # 0 top
        if kind == "night":
            c = (int(14 + 34 * u), int(20 + 40 * u), int(70 + 60 * u))
        else:
            c = (int(255 - 20 * (1 - u) + 0), int(150 + 80 * u), int(120 + 40 * u))
            if u < 0.5:
                k = 1 - u * 2
                c = (int(255 * (1 - 0.35 * k)), int(176 + 40 * (1 - k)), int(150 + 40 * (1 - k)))
        for x in range(w):
            px[x, y] = c
    d = ImageDraw.Draw(im)
    if kind == "night":
        for _ in range(260):
            x, y = int(rng.integers(0, w)), int(rng.integers(0, int(h * 0.75)))
            r = int(rng.integers(2, 5))
            d.ellipse([x - r, y - r, x + r, y + r], fill=(255, 244, 204))
    return im


def pil_image(name, pil):
    img = bpy.data.images.new(name, pil.width, pil.height, alpha=True)
    a = np.asarray(pil.convert("RGBA")).astype(np.float32)[::-1] / 255
    img.pixels.foreach_set(a.ravel())
    img.pack()
    return img


# ------------------------------------------------------------------------------------------------ materials


def img_mat(kit, name, img, emit=0.0, rough=0.5, alpha=False):
    m, N, L, b = kit._mat(name)
    tx = N.new("ShaderNodeTexImage")
    tx.name = "tex"
    tx.image = img
    tx.interpolation = "Linear"
    uvn = N.new("ShaderNodeUVMap")
    L.new(uvn.outputs["UV"], tx.inputs["Vector"])
    L.new(tx.outputs["Color"], b.inputs["Base Color"])
    b.inputs["Roughness"].default_value = rough
    if emit:
        L.new(tx.outputs["Color"], b.inputs["Emission Color"])
        b.inputs["Emission Strength"].default_value = emit
    if alpha:
        L.new(tx.outputs["Alpha"], b.inputs["Alpha"])
    kit._fogged(m, b.outputs[0])
    return m


def uvplane(name, size, loc, mat, parent=None, rot=(0, 0, 0)):
    """A plane with UVs, facing -y (rotate it for others). size = (w, h) in x and z."""
    x, z = size[0] / 2, size[1] / 2
    verts = [(-x, 0, -z), (x, 0, -z), (x, 0, z), (-x, 0, z)]
    me = bpy.data.meshes.new(name)
    me.from_pydata(verts, [], [(0, 3, 2, 1)])
    me.update()
    uv = me.uv_layers.new(name="UVMap")
    for poly in me.polygons:
        for li, (u, v) in zip(poly.loop_indices, [(0, 0), (0, 1), (1, 1), (1, 0)]):
            uv.data[li].uv = (u, v)
    ob = bpy.data.objects.new(name, me)
    ob.data.materials.append(mat)
    ob.location, ob.rotation_euler = loc, rot
    from blocky import kit as K
    return K.link(ob, parent)


def annulus(kit, name, r_in, r_out, depth, loc, mat, parent=None, n=32, rot=(0, 0, 0)):
    """A flat ring (axis z), depth thick, centred on loc."""
    verts, faces_ = [], []
    for z in (-depth / 2, depth / 2):
        for r in (r_in, r_out):
            for i in range(n):
                a = TAU * i / n
                verts.append((r * math.cos(a), r * math.sin(a), z))
    for i in range(n):
        j = (i + 1) % n
        a0, a1 = 0 * n, 1 * n      # bottom inner/outer; top inner = 2n, outer = 3n
        faces_.append((n + i, n + j, 3 * n + j, 3 * n + i))      # outer wall
        faces_.append((2 * n + i, 2 * n + j, j, i))              # inner wall (flipped)
        faces_.append((2 * n + i, 3 * n + i, 3 * n + j, 2 * n + j))  # top
        faces_.append((i, j, n + j, n + i))                      # bottom
    ob = kit.mesh_obj(name, verts, faces_, mat, parent, loc, rot, smooth=True)
    return ob


def night_cloth(kit, name, base=NAVY, fold="#2b3b9a", star="#fff4cc", star_e=5.0, scale=9.0, rough=0.9, thr=0.5):
    """Deep navy cloth with soft folds and steady warm star specks (object space, so they ride the object)."""
    if name in kit.MATS:
        return kit.MATS[name]
    m, N, L, b = kit._mat(name)
    tc = N.new("ShaderNodeTexCoord")
    nz = N.new("ShaderNodeTexNoise")
    nz.inputs["Scale"].default_value = 5.0
    nz.inputs["Detail"].default_value = 4.0
    L.new(tc.outputs["Object"], nz.inputs["Vector"])
    ramp = N.new("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].position = 0.3
    ramp.color_ramp.elements[0].color = kit.col(base)
    ramp.color_ramp.elements[1].position = 0.7
    ramp.color_ramp.elements[1].color = kit.col(fold)
    L.new(nz.outputs["Fac"], ramp.inputs["Fac"])
    L.new(ramp.outputs["Color"], b.inputs["Base Color"])
    b.inputs["Roughness"].default_value = rough
    kit._bump(N, L, b, nz.outputs["Fac"], 0.35, 0.03)
    vor = N.new("ShaderNodeTexVoronoi")
    vor.feature = "F1"
    vor.inputs["Scale"].default_value = scale
    L.new(tc.outputs["Object"], vor.inputs["Vector"])
    dot = N.new("ShaderNodeValToRGB")
    dot.color_ramp.elements[0].position = 0.07
    dot.color_ramp.elements[0].color = (1, 1, 1, 1)
    dot.color_ramp.elements[1].position = 0.12
    dot.color_ramp.elements[1].color = (0, 0, 0, 1)
    L.new(vor.outputs["Distance"], dot.inputs["Fac"])
    sep = N.new("ShaderNodeSeparateColor")
    L.new(vor.outputs["Color"], sep.inputs["Color"])
    cm = N.new("ShaderNodeMath")
    cm.operation = "GREATER_THAN"
    cm.inputs[1].default_value = thr
    L.new(sep.outputs["Red"], cm.inputs[0])
    mul = N.new("ShaderNodeMath")
    mul.operation = "MULTIPLY"
    L.new(dot.outputs["Color"], mul.inputs[0])
    L.new(cm.outputs[0], mul.inputs[1])
    st = N.new("ShaderNodeMath")
    st.operation = "MULTIPLY"
    st.inputs[1].default_value = star_e
    L.new(mul.outputs[0], st.inputs[0])
    b.inputs["Emission Color"].default_value = kit.col(star)
    L.new(st.outputs[0], b.inputs["Emission Strength"])
    kit._fogged(m, b.outputs[0])
    return m


def emit_mat(kit, name, hexc, strength):
    return kit.emit(hexc, strength, name)


def limb(kit, name, mat, length, w, d, parent=None, bevel=0.05):
    return kit.box(name, (w, d, length), (0, 0, 0), mat, parent, bevel=bevel)


def _aim(ob, a, b, length):
    a, b = V(a), V(b)
    d = b - a
    ln = d.length
    ob.location = (a + b) / 2
    up = "X" if abs(d.z) / max(ln, 1e-6) > 0.92 else "Y"
    ob.rotation_euler = d.to_track_quat("Z", up).to_euler()
    ob.scale = (1, 1, ln / length)


def ik(S, W, a, b, pole):
    """Two-bone IK: the elbow for shoulder S, wrist W, bone lengths a, b, bent toward `pole` (a direction)."""
    S, W, pole = V(S), V(W), V(pole)
    d = W - S
    ln = min(d.length, a + b - 1e-3)
    dn = d.normalized()
    x = (ln * ln + a * a - b * b) / (2 * ln)
    h = math.sqrt(max(a * a - x * x, 0.0))
    p = pole - dn * pole.dot(dn)
    p = p.normalized() if p.length > 1e-6 else V((0, 0, 1))
    return S + dn * x + p * h


# ------------------------------------------------------------------------------------------------ the room


def build_room(kit, ctx, M):
    # floor (white tile with a faint mint chequer), ceiling, walls
    kit.box("floor", (11.4, 9.4, 0.1), (0, -0.15, -0.05), M["tile"])
    kit.box("ceiling", (11.4, 9.4, 0.1), (0, -0.15, CEIL + 0.05), M["white"])
    kit.box("wall back", (11.4, 0.2, CEIL), (0, 4.3, CEIL / 2), M["mint"])
    kit.box("wall back dado", (11.3, 0.03, 0.2), (0, 4.17, 0.1), M["teal"])
    for sx in (-1, 1):
        kit.box(f"wall side{sx}", (0.2, 9.4, CEIL), (sx * 5.6, -0.15, CEIL / 2), M["mint"])
    # front wall with a window band (z .85 .. 2.7) and a door gap (x -4.8 .. -3.8)
    FY = -4.55
    kit.box("fw low a", (0.8, 0.12, 0.85), (-5.2, FY, 0.425), M["mint"])
    kit.box("fw low b", (9.4 - 0.0, 0.12, 0.85), (0.9, FY, 0.425), M["mint"])
    kit.box("fw up", (11.4, 0.12, CEIL - 2.7), (0, FY, 2.7 + (CEIL - 2.7) / 2), M["mint"])
    kit.box("fw lintel", (1.0, 0.12, 0.5), (-4.3, FY, 2.45), M["mint"])
    kit.box("fw pier", (0.8, 0.12, 2.0), (-5.2, FY, 1.85), M["mint"])
    for x in (-2.0, 0.5, 3.0, 5.4):
        kit.box(f"mullion{x}", (0.09, 0.14, 1.9), (x, FY, 1.78), M["white"], bevel=0.015)
    kit.box("sill", (9.4, 0.2, 0.05), (0.9, FY + 0.04, 0.87), M["white"], bevel=0.01)
    kit.box("door frame a", (0.07, 0.14, 2.3), (-4.83, FY, 1.15), M["white"], bevel=0.01)
    kit.box("door frame b", (0.07, 0.14, 2.3), (-3.77, FY, 1.15), M["white"], bevel=0.01)
    # a pale yellow row of washers along the left wall
    for i in range(5):
        y = -3.2 + 1.05 * i
        kit.box(f"washer{i}", (0.78, 0.8, 1.0), (-5.15, y, 0.5), M["yellow"], bevel=0.04)
        kit.cyl(f"washer lid{i}", 0.3, 0.04, (-5.1, y, 1.02), M["white"], n=24)
        kit.cyl(f"washer dial{i}", 0.04, 0.04, (-4.76, y, 0.82), M["mint"], rot=(0, math.pi / 2, 0), n=14)
    # the folding table (long, pale top, two steel legs) and four sunflower chairs in a row
    kit.box("table top", (2.2, 0.8, 0.06), (0.4, 0.3, 0.9), M["white"], bevel=0.02)
    for sx in (-1, 1):
        kit.box(f"table leg{sx}", (0.06, 0.7, 0.88), (0.4 + sx * 1.0, 0.3, 0.44), M["steel"])
    for i in range(4):
        kit.prop("chair_1", (0.9 + 0.95 * i, -3.85, 0.0), rot=0, height=0.95, tint="#ffc93c")
    kit.prop("houseplant_1", (-4.9, 3.6, 0.0), height=0.6, tint="#a8ffb0")
    kit.prop("trashcan_cylindric", (-2.3, 3.75, 0.0), height=0.7, tint="#7fd0ff")
    # snack machine (coral, rows of coloured snack shapes, no lettering) and a change machine (coin glyph) on the right
    kit.box("snack body", (0.7, 1.0, 1.9), (5.1, -2.2, 0.95), M["coral"], bevel=0.05)
    kit.box("snack glass", (0.03, 0.78, 1.25), (4.74, -2.2, 1.1), M["dark"])
    cols = ["#ffd23c", "#4cc9ff", "#ff6bd6", "#7dff7a", "#ffffff"]
    for r in range(5):
        for c in range(4):
            kit.box(f"snack{r}{c}", (0.05, 0.12, 0.12), (4.71, -2.55 + 0.23 * c, 0.65 + 0.22 * r),
                    kit.plastic(cols[(r + c) % 5], 0.4), bevel=0.02)
    kit.box("change body", (0.6, 0.8, 1.6), (5.15, -0.6, 0.8), M["blue"], bevel=0.05)
    kit.cyl("change coin", 0.12, 0.03, (4.84, -0.6, 1.25), M["brass"], rot=(0, math.pi / 2, 0), n=24)
    # the wall clock: round, tick marks, no numbers, high over the front door
    clk = img_mat(kit, "clock", pil_image("clock img", img_clock()), 0.0, 0.5, alpha=True)
    uvplane("clock", (0.7, 0.7), (-4.3, FY + 0.075, 2.95), clk, rot=(0, 0, math.pi))
    # lights: ceiling panels (area light + the glowing panel)
    ctx["pans"] = []
    for i in range(6):
        x = -4.5 + 1.8 * i
        mat = kit.emit("#f4fbff", 6.0, f"pan{i}")
        kit.box(f"pan{i}", (1.4, 1.0, 0.04), (x, 0.8, CEIL - 0.02), mat)
        kit.light(f"pan{i}", "AREA", (x, 0.8, CEIL - 0.1), 290.0, "#f1f8ff", rot=(0, 0, 0), size=1.6)
        ctx["pans"].append(mat)
    ctx["pan_x"] = [-4.5 + 1.8 * i for i in range(6)]


def build_dryers(kit, ctx, M):
    ctx["doors"] = {}
    ctx["timers"] = {}
    ctx["numimgs"] = {}
    bez_mats = {}
    iron = kit.plastic("#7bd1b6", 0.45, "mint iron")
    for n in range(1, 11):
        x = NX[n]
        nine = n == 9
        # deep body behind, a front frame round a square hole (half .22), a round collar, a dark tube and the drum
        kit.box(f"dryer{n}", (0.88, 0.76, 1.38), (x, 3.72, 0.69), M["mint"], bevel=0.035)
        for nm, sz, lc in (("l", (0.22, 0.14, 1.38), (x - 0.33, 3.27, 0.69)), ("r", (0.22, 0.14, 1.38), (x + 0.33, 3.27, 0.69)),
                           ("b", (0.44, 0.14, 0.4), (x, 3.27, 0.2)), ("t", (0.44, 0.14, 0.54), (x, 3.27, 1.11))):
            kit.box(f"dryer{n} fr{nm}", sz, lc, M["mint"], bevel=0.02)
        annulus(kit, f"collar{n}", 0.215, 0.31, 0.03, (x, 3.185, DRUM_Z), M["mint2"], n=36, rot=(math.pi / 2, 0, 0))
        annulus(kit, f"tube{n}", 0.205, 0.215, 0.16, (x, 3.28, DRUM_Z), M["dark"], n=36, rot=(math.pi / 2, 0, 0))
        if not nine:
            kit.cyl(f"drum steel{n}", 0.205, 0.02, (x, 3.35, DRUM_Z), M["steel"], rot=(math.pi / 2, 0, 0), n=36)
        kit.box(f"dryer{n} strip", (0.84, 0.04, 0.3), (x, 3.19, 1.2), M["mint2"], bevel=0.015)
        kit.box(f"dryer{n} foot", (0.84, 0.04, 0.06), (x, 3.19, 0.03), M["white"])
        bm = M["brass"] if nine else M["white"]
        # the timer: a frame (brass for nine), the readout plane proud of it
        kit.box(f"timer frame{n}", (0.38, 0.02, 0.2), (x, 3.168, 1.2), bm, bevel=0.008)
        img0 = pil_image(f"timer{n} off", img_timer(""))
        tm = img_mat(kit, f"timer mat{n}", img0, emit=1.6, rough=0.3)
        uvplane(f"timer{n}", (0.34, 0.13), (x, 3.147, 1.2), tm)
        ctx["timers"][n] = tm
        # the number again on the control strip, so it stays in frame when the door is open
        if n not in ctx["numimgs"]:
            ctx["numimgs"][n] = img_mat(kit, f"num{n}", pil_image(f"num img{n}", img_number(n)), 0.0, 0.4, alpha=True)
        uvplane(f"badge{n}", (0.2, 0.2), (x - 0.3, 3.158, 1.2), ctx["numimgs"][n])
        # coin slot on a plate
        kit.box(f"plate{n}", (0.15, 0.015, 0.11), (x + 0.28, 3.173, 1.2), bm, bevel=0.005)
        kit.box(f"slot{n}", (0.07, 0.02, 0.014), (x + 0.28, 3.162, 1.2), M["dark"])
        # the door, hinged on its left edge
        hinge = kit.empty(f"hinge{n}", (x - 0.4, 3.14, 0.0))
        ctx["doors"][n] = hinge
        pm = M["mint"]
        kit.box(f"door l{n}", (0.2, 0.05, 0.96), (0.1, 0, 0.52), pm, hinge, bevel=0.012)
        kit.box(f"door r{n}", (0.2, 0.05, 0.96), (0.7, 0, 0.52), pm, hinge, bevel=0.012)
        kit.box(f"door b{n}", (0.4, 0.05, 0.38), (0.4, 0, 0.23), pm, hinge, bevel=0.012)
        kit.box(f"door t{n}", (0.4, 0.05, 0.18), (0.4, 0, 0.91), pm, hinge, bevel=0.012)
        ring = M["brass"] if nine else M["white"]
        annulus(kit, f"door ring{n}", 0.2, 0.3, 0.04, (0.4, -0.035, 0.62), ring, hinge, n=36, rot=(math.pi / 2, 0, 0))
        if n not in ctx["numimgs"]:
            ctx["numimgs"][n] = img_mat(kit, f"num{n}", pil_image(f"num img{n}", img_number(n)), 0.0, 0.4, alpha=True)
        uvplane(f"num{n}", (0.2, 0.2), (0.4, -0.037, 0.19), ctx["numimgs"][n], hinge)
        if nine:
            for k in range(12):
                a = TAU * k / 12
                kit.sphere(f"rivet{k}", 0.012, (0.4 + 0.25 * math.cos(a), -0.07, 0.62 + 0.25 * math.sin(a)), M["rivet"], hinge, seg=8)
            kit.box("latch", (0.07, 0.05, 0.16), (0.78, -0.055, 0.62), M["brass"], hinge, bevel=0.012)
            for z in (0.57, 0.67):
                kit.sphere(f"latch rivet{z}", 0.011, (0.78, -0.085, z), M["rivet"], hinge, seg=8)
            # riveted seams down the iron body under the mint paint
            for z in (0.15, 0.5, 0.85, 1.15):
                for sx in (-1, 1):
                    kit.sphere(f"seam{z}{sx}", 0.012, (x + sx * 0.43, 3.19, z), M["rivet"], seg=8)
        else:
            kit.box(f"latch{n}", (0.05, 0.04, 0.14), (0.77, -0.05, 0.62), M["white"], hinge, bevel=0.012)
    # the drum behind nine's door: a turning cloth disc with fins and tumbling blobs on it
    base = kit.empty("drumbase", (X9, 3.30, DRUM_Z), rot=(math.pi / 2, 0, 0))
    spin = kit.empty("drumspin", (0, 0, 0), base)
    ctx["drum_base"], ctx["spin"] = base, spin
    cloth = night_cloth(kit, "drum cloth", base="#121a50", fold="#1f2b80", scale=11.0, star_e=6.0)
    cloth2 = night_cloth(kit, "drum cloth b", base="#1a2470", fold="#2a3a98", scale=8.0, star_e=6.0, thr=0.35)
    ctx["drum_disc"] = [kit.cyl("drum disc", 0.2, 0.02, (0, 0, 0.0), cloth, spin, n=40)]
    for k in range(3):
        a = TAU * k / 3 + 0.4
        f_ = kit.box(f"drum fin{k}", (0.05, 0.19, 0.07), (0.1 * math.cos(a), 0.1 * math.sin(a), 0.045), cloth2, spin, bevel=0.015)
        f_.rotation_euler = (0, 0, a - math.pi / 2)
    ctx["drum_cloth"] = kit.MATS["drum cloth"]
    steel = kit.cyl("drum steel9", 0.2, 0.02, (0, 0, 0.001), M["steel"], spin, n=40)
    steel.hide_render = True
    ctx["steel9"] = steel
    blobs = []
    spots = [(0.07, 0.05, 0.12, 0.09, 0.07), (-0.07, 0.02, 0.14, 0.1, 0.08), (0.02, -0.08, 0.12, 0.09, 0.07),
             (-0.03, 0.09, 0.12, 0.09, 0.07), (0.09, -0.04, 0.1, 0.08, 0.06), (-0.08, -0.07, 0.11, 0.09, 0.07)]
    for i, (px, py, sx, sy, sz) in enumerate(spots):
        b_ = kit.box(f"drum blob{i}", (sx, sy, sz), (px, py, 0.05 + sz / 2), cloth2 if i % 2 else cloth, spin, bevel=0.04)
        b_.rotation_euler = (0.3 * i, 0.2 * i, 0.7 * i)
        blobs.append(b_)
    ctx["blobs"] = blobs
    # pieces of the Night that ride round with the drum
    dc = {}
    dc["bulk"] = [kit.box("dc bulk", (0.32, 0.2, 0.12), (0.04, 0.02, 0.09), cloth, spin, bevel=0.06, rot=(0, 0, 0.5)),
                  kit.box("dc bulk2", (0.22, 0.26, 0.1), (-0.08, 0.06, 0.1), cloth2, spin, bevel=0.05, rot=(0, 0, -0.4))]
    dc["sleeve"] = [kit.box("dc sleeve", (0.1, 0.5, 0.1), (0.02, 0.0, 0.12), cloth, spin, bevel=0.04, rot=(0, 0, 0.35))]
    fng = []
    fng.append(kit.box("dc palm", (0.1, 0.07, 0.03), (-0.11, -0.1, 0.15), cloth, spin, bevel=0.012, rot=(0, 0, 0.5)))
    for k in range(4):
        fng.append(kit.box(f"dc finger{k}", (0.026, 0.24, 0.024), (-0.04 + 0.03 * k, -0.07 + 0.012 * k, 0.15), cloth, spin,
                           bevel=0.01, rot=(0, 0, 0.5)))
    dc["fingers"] = fng
    face_mat = img_mat(kit, "dc face", pil_image("dc face img", img_moon(True)), emit=0.8, rough=0.6, alpha=True)
    fp = uvplane("dc face", (0.17, 0.17), (0.07, 0.0, 0.12), face_mat, spin, rot=(-math.pi / 2, 0, 0))
    dc["face"] = [fp]
    dc["folded"] = [kit.box("dc fold", (0.4, 0.15, 0.14), (-0.02, -0.03, 0.12), cloth, spin, bevel=0.07, rot=(0, 0, 0.9)),
                    kit.box("dc fold2", (0.3, 0.2, 0.1), (0.1, 0.07, 0.13), cloth2, spin, bevel=0.06, rot=(0, 0, 0.1))]
    # the hand that holds a quarter up to the glass (fixed, on the drum base, not turning)
    hand = []
    hz = 0.15
    hand.append(kit.box("hd palm", (0.12, 0.13, 0.03), (0.0, -0.08, hz), cloth, base, bevel=0.012))
    for k in range(4):
        hand.append(kit.box(f"hd finger{k}", (0.028, 0.2, 0.026), (-0.045 + 0.03 * k, 0.05 + (0.012 if k in (1, 2) else 0), hz),
                            cloth, base, bevel=0.01))
    hand.append(kit.box("hd thumb", (0.03, 0.12, 0.026), (0.085, -0.02, hz), cloth, base, bevel=0.01, rot=(0, 0, -0.5)))
    hand.append(kit.box("hd arm", (0.1, 0.4, 0.07), (0.0, -0.38, 0.14), cloth, base, bevel=0.03))
    hand.append(kit.cyl("hd quarter", 0.035, 0.008, (0.0, 0.14, 0.168), M["silver"], base, n=24))
    dc["hand"] = hand
    ctx["dc"] = dc
    # the dryer's light: inside the drum
    kit.light("drumlight", "POINT", (X9, 3.26, DRUM_Z), 1.5, "#cfe6ff", size=0.12)
    kit.light("amber", "POINT", (X9 - 0.12, FACE_Y - 0.25, 1.2), 3.0, "#ffb02e", size=0.1)
    # the paper roll of quarters on top of nine, and a quarter that goes into the slot
    roll = [kit.cyl("roll paper", 0.05, 0.22, (X9 - 0.2, 3.5, 1.38 + 0.05), M["paper"], rot=(0, math.pi / 2, 0), n=16),
            kit.cyl("roll coins", 0.043, 0.1, (X9 - 0.06, 3.5, 1.38 + 0.05), M["silver"], rot=(0, math.pi / 2, 0), n=16),
            kit.cyl("roll tear", 0.052, 0.05, (X9 - 0.15, 3.5, 1.38 + 0.05), M["paper2"], rot=(0, math.pi / 2, 0), n=16)]
    ctx["roll"] = roll
    ctx["coin"] = kit.cyl("coin", 0.03, 0.006, (0, 0, -9), M["silver"], rot=(math.pi / 2, 0, 0), n=24)
    # eight's towels (stacked to its edge); nine's top stays bare
    tc = ["#ff7a6b", "#ffd23c", "#4cc9ff", "#ff6bd6", "#7dff7a"]
    for i in range(6):
        kit.box(f"towel{i}", (0.7, 0.55, 0.07), (NX[8] + 0.02 * (i % 2), 3.65, 1.38 + 0.04 + 0.07 * i), kit.plastic(tc[i % 5], 0.8), bevel=0.025)
    kit.box("towel loose", (0.6, 0.4, 0.07), (NX[8] - 0.1, 3.5, 1.38 + 0.04 + 0.42), kit.plastic("#ffffff", 0.8), bevel=0.025)
    # Jonah's armful of snacks (coloured shapes, no lettering), at the snack machine
    sn = []
    for i, cc in enumerate(["#ffd23c", "#4cc9ff", "#ff6bd6", "#7dff7a", "#ffffff", "#ff7a6b"]):
        sn.append(kit.box(f"armful{i}", (0.1, 0.16, 0.12), (4.52 + 0.01 * (i % 2), -2.38 + 0.09 * i, 1.0 + 0.04 * (i % 3)),
                          kit.plastic(cc, 0.4), bevel=0.02))
        sn[-1].hide_render = True
    ctx["snacks"] = sn
    # the dark pool that spills out
    pm = night_cloth(kit, "pool cloth", scale=7.0, star_e=5.0, thr=0.3)
    pool = kit.cyl("pool", 1.0, 0.01, (X9, FACE_Y - 0.1, 0.012), pm, n=48)
    pool.scale = (0.01, 0.01, 1.0)
    pool.hide_render = True
    ctx["pool"] = pool


def build_outside(kit, ctx, M):
    # lot, street light, the truck, sky and the moon
    kit.box("lot", (140, 80, 0.1), (0, -44, -0.06), kit.plastic("#27377f", 0.9, "lot"))
    kit.box("lot pool", (7, 5, 0.01), (5.5, -8.5, -0.003), kit.plastic("#4f6bc4", 0.9, "lot light"))
    kit.box("kerb", (16, 0.4, 0.15), (0, -5.2, 0.075), M["white"], bevel=0.03)
    kit.box("pole", (0.14, 0.14, 4.2), (5.5, -8.5, 2.1), M["dark"])
    kit.box("pole arm", (0.1, 0.8, 0.1), (5.5, -8.1, 4.2), M["dark"])
    kit.sphere("lamp", 0.2, (5.5, -7.7, 4.1), kit.emit("#ffe9a8", 8.0, "lamp glow"), seg=12)
    kit.light("lamp", "POINT", (5.5, -7.7, 4.0), 250.0, "#ffe2a0", size=0.3)
    wh = kit.plastic("#f5f7fa", 0.45, "truck white")
    tx, ty = 0.0, -10.0
    troot = kit.empty("truck", (-0.8, 0.0, 0.0))
    ctx["truck"] = troot
    kit.box("truck box", (4.6, 2.3, 2.5), (tx - 0.3, ty, 1.7), wh, troot, bevel=0.05)
    kit.box("truck cab", (1.4, 2.2, 1.7), (tx + 2.9, ty, 1.15), wh, troot, bevel=0.1)
    kit.box("truck cab win", (0.04, 1.8, 0.7), (tx + 3.6, ty, 1.55), kit.plastic("#7fa8d8", 0.2, "cabwin"), troot, bevel=0.02)
    kit.box("truck chassis", (6.0, 2.0, 0.3), (tx + 0.5, ty, 0.35), M["dark"], troot)
    for wx in (tx - 1.5, tx + 2.8):
        for sy in (-1, 1):
            kit.cyl(f"wheel{wx}{sy}", 0.42, 0.3, (wx, ty + sy * 1.05, 0.42), M["dark"], troot, rot=(math.pi / 2, 0, 0), n=20)
    kit.box("truck stripe", (4.6, 0.02, 0.3), (tx - 0.3, ty + 1.16, 1.0), M["teal"], troot)
    # a street-light-coloured fill for the lot so the truck reads
    kit.light("lot", "SPOT", (2.0, -16.0, 9.0), 900.0, "#9fb4ff", size=1.0, spot=40, blend=0.5)
    ctx["lot_light"] = kit.LIGHTS["lot"]["obj"]
    ctx["lot_light"].rotation_euler = (V((-0.5, -9.0, 0.0)) - V((2.0, -16.0, 9.0))).to_track_quat("-Z", "Y").to_euler()
    # sky: night and dawn planes
    sky_n = kit.emit("#ffffff", 1.0, "sky night")
    nt = sky_n.node_tree
    tx_ = nt.nodes.new("ShaderNodeTexImage")
    tx_.image = pil_image("sky n", img_sky("night"))
    uvn = nt.nodes.new("ShaderNodeUVMap")
    nt.links.new(uvn.outputs["UV"], tx_.inputs["Vector"])
    em = nt.nodes["Emission"]
    nt.links.new(tx_.outputs["Color"], em.inputs["Color"])
    sky_d = kit.emit("#ffffff", 0.0, "sky dawn")
    nt2 = sky_d.node_tree
    tx2 = nt2.nodes.new("ShaderNodeTexImage")
    tx2.image = pil_image("sky d", img_sky("dawn"))
    uv2 = nt2.nodes.new("ShaderNodeUVMap")
    nt2.links.new(uv2.outputs["UV"], tx2.inputs["Vector"])
    nt2.links.new(tx2.outputs["Color"], nt2.nodes["Emission"].inputs["Color"])
    uvplane("sky night", (240, 60), (0, -45, 18), sky_n, rot=(0, 0, math.pi))
    uvplane("sky dawn", (240, 60), (0, -44.5, 18), sky_d, rot=(0, 0, math.pi))
    ctx["sky_n"], ctx["sky_d"] = sky_n, sky_d
    # the moon: a disc with the same three craters as the Night's face, turning with the drum
    mm = img_mat(kit, "moon", pil_image("moon img", img_moon(False)), emit=1.0, rough=0.9, alpha=True)
    mroot = kit.empty("moon root", (0.3, -32.0, 6.0))
    mspin = kit.empty("moon spin", (0, 0, 0), mroot)
    uvplane("moon disc", (5.0, 5.0), (0, 0, 0), mm, mspin, rot=(0, 0, math.pi))
    ctx["moon_root"], ctx["moon_spin"], ctx["moon_mat"] = mroot, mspin, mm
    # the outdoor light for sunrise (off until the dawn cue)
    kit.light("dawn", "AREA", (0.0, -16.0, 3.0), 0.0, "#ffb27a", size=10.0)
    kit.LIGHTS["dawn"]["obj"].rotation_euler = (V((0, -3.0, 1.0)) - V((0.0, -16.0, 3.0))).to_track_quat("-Z", "Y").to_euler()
    # lot colour for dawn
    ctx["lot_mat"] = kit.MATS["lot"]


def materials(kit):
    M = {}
    M["tile"] = kit.checker("#f6f8f4", "#e1f0ea", 2.6, "tile", 0.25)
    M["white"] = kit.plastic("#f5f7f6", 0.5, "white")
    M["mint"] = kit.plastic("#86e0c3", 0.4, "mint")
    M["mint2"] = kit.plastic("#6fd2b2", 0.4, "mint2")
    M["teal"] = kit.plastic("#3aa39a", 0.5, "teal")
    M["yellow"] = kit.plastic("#ffe27a", 0.4, "washer yellow")
    M["coral"] = kit.plastic("#ff7a6b", 0.4, "coral")
    M["blue"] = kit.plastic("#5ab4ff", 0.4, "changeblue")
    M["dark"] = kit.plastic("#232a3a", 0.6, "dark")
    M["steel"] = kit.metal("#b9c2cc", 0.3, "steel")
    M["brass"] = kit.metal("#b8892f", 0.32, "brass")
    M["rivet"] = kit.metal("#6b5a3a", 0.4, "rivet")
    M["silver"] = kit.metal("#d4d8de", 0.25, "silver")
    M["paper"] = kit.plastic("#e8c07a", 0.8, "paper")
    M["paper2"] = kit.plastic("#cfa05a", 0.8, "paper2")
    gl = kit._new("dglass")
    b = gl.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = kit.col("#cfeaff")
    b.inputs["Roughness"].default_value = 0.05
    b.inputs["Alpha"].default_value = 0.16
    kit._fogged(gl, b.outputs[0])
    M["glass"] = gl
    return M


# ------------------------------------------------------------------------------------------------ the Night


def night_face():
    """A full moon: pale cream disc, soft darker seas across it, and three grey-gold craters (two tall eyes, one thin mouth)."""
    im = Image.new("RGB", (faces.TEX_W, faces.TEX_H), (232, 224, 176))
    sea = Image.new("L", (faces.TEX_W, faces.TEX_H), 0)
    sd = ImageDraw.Draw(sea)
    rng = np.random.default_rng(11)
    for _ in range(26):
        cx, cy = int(rng.integers(0, faces.TEX_W)), int(rng.integers(0, faces.TEX_H))
        r = int(rng.integers(40, 150))
        sd.ellipse([cx - r, cy - r * 0.8, cx + r, cy + r * 0.8], fill=int(rng.integers(40, 110)))
    sea = sea.filter(ImageFilter.GaussianBlur(40))
    dark = Image.new("RGB", im.size, (178, 160, 98))
    im = Image.composite(dark, im, sea.point(lambda v: min(255, v * 2)))
    d = ImageDraw.Draw(im)
    s = faces.FX1 - faces.FX0
    def poly(cx, cy, rx, ry, rot, fill, n=40):
        pts = []
        for i in range(n):
            a = TAU * i / n
            x, y = rx * math.cos(a), ry * math.sin(a)
            pts.append((cx + x * math.cos(rot) - y * math.sin(rot), cy + x * math.sin(rot) + y * math.cos(rot)))
        d.polygon(pts, fill=fill)
    for sx, ey, er in ((-1, 0.38, 0.108), (1, 0.43, 0.082)):      # not quite a pair: one larger, one set a little high
        cx, cy = faces._fx(0.5 + sx * 0.22), faces._fy(ey)
        r = er * s
        poly(cx, cy, r * 1.3, r * 1.3, 0.0, (176, 160, 104))                  # the crater's pale rim
        poly(cx - 0.012 * s, cy - 0.01 * s, r * 1.0, r * 1.0, 0.0, (30, 25, 13))   # the dark floor, shaded to one side
        poly(cx + 0.3 * r, cy - 0.3 * r, 0.1 * r, 0.1 * r, 0.0, (255, 250, 225))
    # the mouth: one long thin crescent, a little off level, wider than the eyes are apart
    mx, my = faces._fx(0.5), faces._fy(0.77)
    upper, lower = [], []
    for i in range(41):
        u = -1 + i / 20
        x = mx + u * 0.38 * s
        rise = (-(u * u) * 0.02 + u * 0.018) * s
        upper.append((x, my + rise))
        lower.append((x, my + rise + 0.026 * s * (1 - u * u) ** 0.7))
    d.polygon(upper + lower[::-1], fill=(70, 59, 33))
    return im.filter(ImageFilter.SMOOTH)


NIGHT_HEAD_SC = 0.41


def build_night(kit, ctx, M):
    cloth = night_cloth(kit, "night cloth", base="#141c52", fold="#222f86", scale=8.0, star_e=8.0, thr=0.3)
    cloth2 = night_cloth(kit, "night cloth2", base="#0f1545", fold="#1b2679", scale=9.0, star_e=8.0, thr=0.3)
    root = kit.empty("night", (0, 0, 0))
    parts = {}
    P = []

    def mk(nm, w, d, ln, mat=cloth, bevel=0.05):
        ob = kit.box(nm, (w, d, ln), (0, 0, 0), mat, root, bevel=bevel)
        P.append(ob)
        parts[nm] = (ob, ln)
        return ob
    mk("torso", 0.42, 0.34, 1.0)
    mk("shoulders", 0.8, 0.3, 0.3, cloth2, 0.08)
    for sx in (-1, 1):
        mk(f"upper{sx}", 0.2, 0.2, 1.0)
        mk(f"fore{sx}", 0.19, 0.18, 1.1)
        mk(f"palm{sx}", 0.2, 0.05, 0.16, cloth2, 0.02)
        for k in range(4):
            mk(f"fing{sx}{k}", 0.042, 0.04, 0.42, cloth2, 0.015)
        mk(f"thumb{sx}", 0.05, 0.04, 0.25, cloth2, 0.015)
    mk("neck", 0.16, 0.16, 0.4, cloth2, 0.04)
    head = kit.empty("night.head", (0, 0, 0), root)
    hs = kit.empty("night.heads", (0, 0, 0), head)
    hs.scale = (NIGHT_HEAD_SC,) * 3
    hm, tex = rig.head_material("night", "#f2e3a0")
    hm.node_tree.nodes["Principled BSDF"].inputs["Roughness"].default_value = 0.6
    pil = night_face()
    img = bpy.data.images.new("night face", pil.width, pil.height)
    a = np.asarray(pil.convert("RGBA")).astype(np.float32)[::-1] / 255
    img.pixels.foreach_set(a.ravel())
    img.pack()
    img.colorspace_settings.name = "sRGB"
    tex.image = img
    nt = hm.node_tree
    bsdf = nt.nodes["Principled BSDF"]
    nt.links.new(tex.outputs["Color"], bsdf.inputs["Emission Color"])
    bw = nt.nodes.new("ShaderNodeRGBToBW")
    nt.links.new(tex.outputs["Color"], bw.inputs["Color"])
    ramp = nt.nodes.new("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].position = 0.93
    ramp.color_ramp.elements[0].color = (0.0, 0.0, 0.0, 1)
    ramp.color_ramp.elements[1].position = 0.985
    ramp.color_ramp.elements[1].color = (1.0, 1.0, 1.0, 1)
    nt.links.new(bw.outputs["Val"], ramp.inputs["Fac"])
    ad = nt.nodes.new("ShaderNodeMath")
    ad.operation = "MULTIPLY_ADD"
    ad.inputs[1].default_value = 6.0
    ad.inputs[2].default_value = 0.14
    nt.links.new(ramp.outputs["Color"], ad.inputs[0])
    nt.links.new(ad.outputs[0], bsdf.inputs["Emission Strength"])
    rig.head_mesh("night.headm", hm, hs)
    P.append(head)
    ctx["night"] = {"root": root, "parts": parts, "head": head, "all": [root] + list(root.children_recursive)}


def night_pose(ctx, u):
    """Half out of nine's door (u = 0): head over the door, forearms flat on the floor toward us; then bent down to my
    eye level, 40 cm from my face (u = 1)."""
    N = ctx["night"]
    pr = N["parts"]
    lerp = lambda a, b: tuple(x + (y - x) * u for x, y in zip(a, b))
    hip = (X9, 3.5, 0.55)
    neck0 = lerp((X9, 2.78, 0.98), (X9 - 0.06, 2.85, 1.12))
    sho = (neck0[0], neck0[1] - 0.02, neck0[2] - 0.06)
    hd = lerp((X9, 2.52, 1.72), (X9 - 0.12, 2.5, 1.5))
    _aim(pr["torso"][0], hip, neck0, 1.0)
    pr["shoulders"][0].location = sho
    _aim(pr["neck"][0], neck0, (hd[0], hd[1] + 0.05, hd[2] - 0.22), 0.4)
    N["head"].location = hd
    N["head"].rotation_euler = (math.radians(-8 - 14 * u), 0, math.radians(9 - 3 * u))
    for sx in (-1, 1):
        S = (sho[0] + sx * 0.42, sho[1] - 0.02, sho[2] - 0.04)
        W = lerp((X9 + sx * 0.75, 1.0, 0.07), (X9 + sx * 0.8, 1.45, 0.07))
        E = ik(S, W, 1.0, 1.1, (sx * 0.7, 0.2, 0.4))
        _aim(pr[f"upper{sx}"][0], S, E, 1.0)
        _aim(pr[f"fore{sx}"][0], E, W, 1.1)
        fd = (V(W) - V(E)).normalized()
        fd.z = 0.0
        fd = fd.normalized() if fd.length > 1e-6 else V((0, -1, 0))
        palm_c = V(W) + fd * 0.07
        palm_c.z = 0.045
        _aim(pr[f"palm{sx}"][0], palm_c - fd * 0.08, palm_c + fd * 0.08, 0.16)
        for k in range(4):
            off = V((fd.y, -fd.x, 0.0)) * ((k - 1.5) * 0.052)
            base = palm_c + fd * 0.1 + off
            tip = base + fd * 0.36 + off * 0.35
            base.z = tip.z = 0.03
            _aim(pr[f"fing{sx}{k}"][0], base, tip, 0.42)
        tb = palm_c + V((fd.y, -fd.x, 0)) * (0.1 * sx * -1) + fd * 0.03
        tb.z = 0.03
        _aim(pr[f"thumb{sx}"][0], tb, tb + fd * 0.2 + V((fd.y, -fd.x, 0)) * (0.07 * -sx), 0.25)


# ------------------------------------------------------------------------------------------------ build


def build(kit, story, tl):
    ctx = {"story": story}
    M = materials(kit)
    ctx["M"] = M
    build_room(kit, ctx, M)
    build_dryers(kit, ctx, M)
    build_outside(kit, ctx, M)
    build_night(kit, ctx, M)
    kit.light("face", "AREA", (0, 0, 4), 0.0, "#fff4ea", size=1.6)
    kit.light("rim", "SPOT", (0, 0, 4), 0.0, "#bcd2ff", size=0.3, spot=70, blend=0.6)
    kit.light("key2", "SPOT", (0, 0, 4), 0.0, "#ffe9d0", size=0.3, spot=60, blend=0.6)
    # timer readouts: every string used
    ctx["timer_imgs"] = {}
    for c in tl["cues"]:
        if c["name"] == "timer" and c["s"] not in ctx["timer_imgs"]:
            ctx["timer_imgs"][c["s"]] = pil_image(f"timer {c['s']}", img_timer(c["s"]))
    ctx["timer_imgs"][""] = pil_image("timer off", img_timer(""))
    # phone
    ph = kit.empty("phone", (0, 0, -9))
    kit.box("phone body", (0.075, 0.012, 0.155), (0, 0, 0), M["dark"], ph, bevel=0.008)
    pm = img_mat(kit, "phone screen", pil_image("phone img", img_phone("0:41")), emit=1.2, rough=0.2)
    uvplane("phone screen", (0.066, 0.14), (0, -0.0075, 0), pm, ph)
    ctx["phone"] = ph
    # sync the light list after
    ctx["wall_hdri"] = None
    return ctx


def _cap_build(kit, ctx, who):
    hg = bpy.data.objects[f"{who}.headg"]
    R, H = faces.HEAD_R, faces.HEAD_H
    top = H / 2
    mat = kit.plastic("#2a3f8f", 0.6, "cap navy")
    parts = [kit.box(f"{who}.capc", (2 * R + 0.12, 2 * R + 0.12, 0.42), (0, 0.0, top + 0.08), mat, hg, bevel=0.18),
             kit.box(f"{who}.capb", (2 * R * 0.8, 0.6, 0.07), (0, R + 0.22, top - 0.08), mat, hg, bevel=0.03)]
    return parts


def animate(kit, story, tl, t, ctx):
    from blocky import kit as K

    over = {}
    if "caps" not in ctx:
        ctx["caps"] = {w: _cap_build(kit, ctx, w) for w in ("me", "jonah") if f"{w}.headg" in bpy.data.objects}
        for n in range(1, 11):
            pass
        # find the HDRI fill node (the Background fed by the environment texture)
        wn = bpy.context.scene.world.node_tree.nodes
        lit = [n for n in wn if n.type == "BACKGROUND" and n.inputs["Color"].is_linked]
        ctx["hdri_node"] = lit[0] if lit else None
        ctx["hdri_base"] = lit[0].inputs["Strength"].default_value if lit else 0.0
        # the drum angle table
        dt = 0.02
        rate = lambda tt: _ramped(_cues(tl, "spin"), tt, "v", 0.9)
        tbl, a = [0.0], 0.0
        for i in range(int(110 / dt)):
            a += rate(i * dt) * dt
            tbl.append(a)
        ctx["spin_tbl"] = (dt, tbl)
    # ---- panels and the sky fill
    pans = _cues(tl, "pan")
    for i in range(6):
        g = _ramped([c for c in pans if c["n"] == i], t, "v", 1.0)
        over[f"pan{i}"] = g
        ctx["pans"][i].node_tree.nodes["Emission"].inputs["Strength"].default_value = 6.0 * g
    amb = _ramped(_cues(tl, "amb"), t, "v", 1.0)
    if ctx["hdri_node"] is not None:
        ctx["hdri_node"].inputs["Strength"].default_value = ctx["hdri_base"] * amb
    over["drumlight"] = _ramped(_cues(tl, "dl"), t, "v", 1.0)
    over["amber"] = _ramped(_cues(tl, "am"), t, "v", 1.0)
    # ---- the drum's turn
    dt, tbl = ctx["spin_tbl"]
    i = min(len(tbl) - 2, int(t / dt))
    ang = tbl[i] + (tbl[i + 1] - tbl[i]) * (t / dt - i)
    ctx["spin"].rotation_euler = (0, 0, ang)
    ctx["moon_spin"].rotation_euler = (0, -ang, 0)
    # ---- the moon
    mz = _ramped(_cues(tl, "moon"), t, "z", 6.0)
    ctx["moon_root"].location = (0.3, -32.0, mz)
    msh = _latest(_cues(tl, "moon"), t, "show", True)
    for ob in [ctx["moon_root"]] + list(ctx["moon_root"].children_recursive):
        ob.hide_render = not msh
    # ---- dawn: the sky, the lot and the light through the windows
    dv = _ramped(_cues(tl, "dawn"), t, "v", 0.0)
    ctx["sky_n"].node_tree.nodes["Emission"].inputs["Strength"].default_value = 1.8 * (1.0 - dv)
    ctx["sky_d"].node_tree.nodes["Emission"].inputs["Strength"].default_value = dv * 1.1
    K.LIGHTS["dawn"]["base"] = 2600.0 * dv
    lb = ctx["lot_mat"].node_tree.nodes["Principled BSDF"].inputs["Base Color"]
    c0, c1 = (0.02, 0.04, 0.2), (0.75, 0.55, 0.4)
    lb.default_value = tuple(c0[k] + (c1[k] - c0[k]) * dv for k in range(3)) + (1,)
    K.LIGHTS["lot"]["base"] = 900.0 * (1 - dv)
    # ---- timers
    for n in (8, 9):
        cs = _cues(tl, "timer", "who", n)
        s = _latest(cs, t, "s", "")
        tm = ctx["timers"][n]
        tm.node_tree.nodes["tex"].image = ctx["timer_imgs"].get(s, ctx["timer_imgs"][""])
    # ---- doors
    for n in (9,):
        dv_ = _ramped(_cues(tl, "door"), t, "v", 0.0)
        ctx["doors"][n].rotation_euler = (0, 0, -math.radians(dv_))
    # ---- drum contents
    fill = _ramped(_cues(tl, "fill"), t, "v", 0.0)
    for k, b_ in enumerate(ctx["blobs"]):
        on = k < 2 or fill > (k - 1) / 5.0
        b_.hide_render = not on
        b_.scale = tuple(0.8 + 0.5 * fill for _ in range(3))
    for what, obs in ctx["dc"].items():
        v = _latest(_cues(tl, "dc", "what", what), t, "v", 0)
        for ob in obs:
            ob.hide_render = not v
    # ---- the Night
    nshow = _latest(_cues(tl, "night"), t, "show", False)
    for ob in ctx["night"]["all"]:
        ob.hide_render = not nshow
    if nshow:
        night_pose(ctx, _ramped(_cues(tl, "nlean"), t, "v", 0.0))
    pv = _ramped(_cues(tl, "pool"), t, "v", 0.0)
    ctx["pool"].hide_render = pv < 0.01
    r = 2.9 * pv
    ctx["pool"].scale = (max(r, 0.01), max(r * 0.8, 0.01), 1.0)
    # ---- the empty drum at dawn, the truck, the snacks, people sitting on the floor
    emp = _latest(_cues(tl, "empty"), t, "v", 0)
    ctx["steel9"].hide_render = not emp
    for ob in ctx["dc"]["bulk"][:0]:
        pass
    if emp:
        for b_ in ctx["blobs"]:
            b_.hide_render = True
        for what, obs in ctx["dc"].items():
            for ob in obs:
                ob.hide_render = True
    for ob in ctx["drum_disc"]:
        ob.hide_render = bool(emp)
    ctx["truck"].location = (_ramped(_cues(tl, "truck"), t, "x", -0.8), 0.0, 0.0)
    sv = _latest(_cues(tl, "snacks"), t, "v", 0)
    for ob in ctx["snacks"]:
        ob.hide_render = not sv
    for who, kk in tl["acting"].items():
        for sx_ in (-1, 1):
            leg = bpy.data.objects.get(f"{who}.leg{sx_}")
            if leg is not None and AC._switch(kk, "sit", t, False):
                leg.rotation_euler = (-math.pi / 2, 0, 0)
    # ---- props
    rv = _latest(_cues(tl, "roll"), t, "v", 0)
    for ob in ctx["roll"]:
        ob.hide_render = not rv
    cn = [c for c in _cues(tl, "coin") if c["t"] <= t + 1e-9]
    coin = ctx["coin"]
    coin.hide_render = True
    if cn:
        c = cn[-1]
        u = (t - c["t"]) / max(c.get("dur", 0.4), 1e-3)
        if u <= 1.0:
            coin.hide_render = False
            coin.location = tuple(c["p0"][k] + (c["p1"][k] - c["p0"][k]) * _ss(u) for k in range(3))
    ph = ctx["phone"]
    pc = _cues(tl, "phone")
    if _latest(pc, t, "show", False):
        ph.location = _latest(pc, t, "pos", (0, 0, -9))
        ph.rotation_euler = (0, 0, math.radians(_latest(pc, t, "yaw", 0.0)))
    else:
        ph.location = (0, 0, -9)
    for who, parts in ctx["caps"].items():
        v = _latest(_cues(tl, "cap", "who", who), t, "v", 1 if who == "jonah" else 0)
        for ob in parts:
            ob.hide_render = not v
    shot_look(kit, tl, t, ctx, over)
    return over


def shot_look(kit, tl, t, ctx, over):
    from blocky import kit as K

    look = None
    for c in _cues(tl, "shot"):
        if c["t"] <= t + 1e-9:
            look = c.get("look")
    for nm in ("face", "rim", "key2"):
        over[nm] = 0.0
    if not look:
        return
    for nm in ("face", "rim", "key2"):
        if nm not in look:
            continue
        spec = look[nm]
        pos, aim, watts = spec[:3]
        ob = K.LIGHTS[nm]["obj"]
        ob.location = pos
        ob.rotation_euler = (V(aim) - V(pos)).to_track_quat("-Z", "Y").to_euler()
        K.LIGHTS[nm]["base"] = watts
        if len(spec) > 3 and K.LIGHTS[nm]["light"].type == "SPOT":
            K.LIGHTS[nm]["light"].spot_size = math.radians(spec[3])
        if len(spec) > 4:
            K.LIGHTS[nm]["light"].color = K.col(spec[4])[:3]
        over[nm] = 1.0
