"""ep34 "unit seven": a self-storage block's one indoor corridor, twelve blue roller doors, a yard, and the Deep One.

Places (metres, z up). The corridor runs along +y from the yard door (y -1.2) to the end wall (y 16.0), x -1.1 .. 0.9.
Side B (x > 0.9) holds units 7 to 12, each 2.0 wide (centres YC) and 3.2 deep (x 0.9 .. 4.1); side A (x < -1.1) holds
doors 1 to 6, always shut. Looking into a unit from the corridor (facing +x), left is +y, right is -y. Unit seven:
the jagged (Jo's) stack on the left against unit eight's wall, the round (mine) stack on the right.
A character with yaw 0 faces -y, yaw 90 faces +x, yaw -90 faces -x (into the corridor from a unit).

Cues read here (timeline cues, "t" resolved):
  time    {"set": dusk|mem|day|sun}           sky, sun, sodium lamp, ceiling mood
  corr    {"level": 0..1, "dur": s}           the corridor battens (slow ramps only, never a strobe)
  door    {"unit": 1..12, "open": 0..1, "dur"}  a roller door, 1 = rolled up
  stacks  {"left": n, "right": n}             boxes showing in unit seven's stacks (0..18)
  lamp    {"on": 0..1}                        my battery lamp
  phone   {"on": 0..1}                        a small cool glow that follows me
  torch   {"on": 0..1}                        my phone torch, a beam ahead of me
  carry   {"who", "style": round|jagged, "on"}  a box hugged to a character's chest
  keys    {"mode": none|ring2|table}          the key ring (unit-seven box top, or my kitchen table)
  plant   {"on": 0..1}                        a small light on the two strokes and the padlock
  kitchen {"set": night|day}                  my kitchen's ceiling light and window
  car     {"pos": [x, y], "yaw": deg, "dur"}  Jo's car (hidden until the first cue)
  facelight {"on": 0..1}                      the underlight on the Deep One's face (the scare)
  headtube {"on": bool}                       the tube behind the Deep One's head
  under   {"on": 0..1}                        a dim fill under the corridor ceiling at the far end
"""

from __future__ import annotations

import math
import random
from pathlib import Path

import bpy
from PIL import Image, ImageDraw

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
RIG_S = 0.34

CORR_X = (-1.1, 0.9)
YARD_Y = -1.2
END_Y = 16.0
YC = {7: 3.0, 8: 5.3, 9: 7.6, 10: 9.9, 11: 12.2, 12: 14.5}
YA = {1: 3.0, 2: 5.3, 3: 7.6, 4: 9.9, 5: 12.2, 6: 14.5}
DEPTH_X = 4.1
CEIL = 2.8
UNIT_H = 2.3
AISLE = 0.5            # half-width of unit seven's aisle
BOX = (0.43, 0.5, 0.4)  # one box: along x, across y, tall
STACK_N = 18

SUN_DIR = (-0.55, 0.8, -0.28)


def _ss(x):
    x = min(1.0, max(0.0, x))
    return x * x * (3 - 2 * x)


def _cues(tl, name):
    return [c for c in tl.get("cues", []) if c["name"] == name]


def _last(cs, t):
    cs = [c for c in cs if c["t"] <= t + 1e-9]
    return cs[-1] if cs else None


def workdir(tl) -> Path:
    d = ROOT / "out" / "work" / tl.get("name", "ep34-unit-seven") / "faces"
    d.mkdir(parents=True, exist_ok=True)
    return d


def _ramp(cs, t, key, default, durkey="dur"):
    """A value that eases to each cue's `key` over its dur (smoothstep), from wherever the last one left it."""
    v = default
    for c in cs:
        if key not in c or c["t"] > t + 1e-9:
            continue
        d = float(c.get(durkey, 0.0))
        u = 1.0 if d <= 1e-6 else _ss((t - c["t"]) / d)
        if u < 1.0:
            return v + (float(c[key]) - v) * u
        v = float(c[key])
    return v


# ------------------------------------------------------------------------------------------ drawings


def pil_image(name, im, path):
    path = path.with_name(f"{path.stem}{path.suffix}")
    im.save(path)
    img = bpy.data.images.load(str(path), check_existing=False)
    img.colorspace_settings.name = "sRGB"
    return img


def image_mat(kit, name, img, rough=0.85):
    m = kit._new(name)
    nt = m.node_tree
    b = nt.nodes["Principled BSDF"]
    tex = nt.nodes.new("ShaderNodeTexImage")
    tex.image = img
    nt.links.new(tex.outputs["Color"], b.inputs["Base Color"])
    b.inputs["Roughness"].default_value = rough
    b.inputs["Specular IOR Level"].default_value = 0.15
    kit._fogged(m, b.outputs[0])
    return m


SEG = {  # seven segments a b c d e f g
    "0": "abcdef", "1": "bc", "2": "abdeg", "3": "abcdg", "4": "bcfg", "5": "acdfg", "6": "acdefg", "7": "abc",
    "8": "abcdefg", "9": "abcdfg",
}


def digits_image(text, w=360, h=220):
    """A galvanised number plate with stencilled digits only (seven-segment bars), no letters."""
    im = Image.new("RGB", (w, h), (150, 158, 162))
    d = ImageDraw.Draw(im)
    d.rectangle([5, 5, w - 6, h - 6], outline=(104, 110, 114), width=6)
    n = len(text)
    dw, dh, th = 92, 150, 22
    gap = 34
    x0 = (w - (n * dw + (n - 1) * gap)) // 2
    y0 = (h - dh) // 2
    ink = (24, 26, 30)
    for k, ch in enumerate(text):
        x = x0 + k * (dw + gap)
        s = SEG[ch]
        mid = y0 + dh // 2
        bars = {"a": (x, y0, x + dw, y0 + th), "d": (x, y0 + dh - th, x + dw, y0 + dh),
                "g": (x, mid - th // 2, x + dw, mid + th // 2),
                "f": (x, y0, x + th, mid + th // 2), "b": (x + dw - th, y0, x + dw, mid + th // 2),
                "e": (x, mid - th // 2, x + th, y0 + dh), "c": (x + dw - th, mid - th // 2, x + dw, y0 + dh)}
        for seg in s:
            d.rectangle(bars[seg], fill=ink)
    return im


def scribble_image(style, seed, w=420, h=340):
    """A cardboard box side with marker scribbles: round loops (mine) or jagged zigzags (Jo's). Never words."""
    rnd = random.Random(seed)
    base = (184 + rnd.randint(-6, 6), 137 + rnd.randint(-6, 6), 90 + rnd.randint(-5, 5))
    im = Image.new("RGB", (w, h), base)
    d = ImageDraw.Draw(im)
    for _ in range(260):   # cardboard fibres
        x, y = rnd.randint(0, w), rnd.randint(0, h)
        dd = rnd.randint(-10, 10)
        d.line([(x, y), (x + rnd.randint(8, 26), y)], fill=(base[0] + dd, base[1] + dd, base[2] + dd), width=1)
    d.rectangle([w // 2 - 6, 0, w // 2 + 6, h], fill=(base[0] - 20, base[1] - 18, base[2] - 14))   # tape seam
    ink = (14, 14, 18)
    th = 15
    if style == "round":
        for k in range(rnd.randint(2, 3)):
            cx = rnd.randint(110, w - 110)
            cy = rnd.randint(105, h - 105)
            r0 = rnd.randint(22, 36)
            pts = []
            for i in range(0, 241, 6):
                a = math.radians(i * 3)
                r = r0 + i * 0.16
                pts.append((cx + r * math.cos(a), cy + r * 0.86 * math.sin(a)))
            d.line(pts, fill=ink, width=th, joint="curve")
            for p in (pts[0], pts[-1]):
                d.ellipse([p[0] - th / 2, p[1] - th / 2, p[0] + th / 2, p[1] + th / 2], fill=ink)
    else:
        for k in range(rnd.randint(2, 3)):
            x = rnd.randint(40, 120)
            y0 = rnd.randint(70, h - 140)
            pts = []
            n = rnd.randint(6, 8)
            for i in range(n):
                pts.append((x + i * (w - 200) / (n - 1), y0 + (110 if i % 2 else 0) + rnd.randint(-10, 10)))
            d.line(pts, fill=ink, width=th, joint="curve")
            for p in (pts[0], pts[-1]):
                d.ellipse([p[0] - th / 2, p[1] - th / 2, p[0] + th / 2, p[1] + th / 2], fill=ink)
    return im


# ------------------------------------------------------------------------------------------ materials


def materials(kit, wd):
    M = {}
    M["floor"] = kit.concrete("#8b8c8a", scale=1.2, stains=0.5)
    M["wall"] = kit.grime("#b3b9bb", 0.7, 2.0, rough=0.8)
    M["wallin"] = kit.grime("#9ea5a7", 0.65, 2.5, rough=0.85)
    M["ceil"] = kit.plastic("#c6cccf", 0.9)
    M["steel"] = kit.metal("#9aa3a8", 0.45)
    M["steelp"] = kit.plastic("#9aa3a8", 0.5)
    M["blue"] = kit.plastic("#3d6fa8", 0.5, spec=0.5)
    M["bluedk"] = kit.plastic("#2c527e", 0.55)
    M["stroke"] = kit.plastic("#58b6ff", 0.5, name="stroke blue")
    M["brass"] = kit.plastic("#e0b64a", 0.3, name="brass", spec=0.9)
    M["pad"] = kit.plastic("#c99a38", 0.28, name="padlock", spec=0.9)
    M["dark"] = kit.plastic("#08090b", 0.9, name="dark")
    M["card"] = kit.plastic("#b8895a", 0.9)
    M["asphalt"] = kit.concrete("#3c3e42", scale=1.6, stains=0.6)
    M["grass"] = kit.plastic("#27312a", 0.95, name="grass")
    M["pole"] = kit.plastic("#2d3035", 0.6, name="pole")
    M["dust"] = kit.plastic("#8a6f52", 0.95, name="dust")
    M["tan"] = kit.plastic("#c2a98a", 0.6, name="tan")
    M["wood"] = kit.planks("#7b5a3a", "#5d4229", scale=1.0)
    M["table"] = kit.planks("#a07a50", "#7d5e3c", scale=1.0)
    M["kwall"] = kit.plastic("#d9d2c4", 0.9, name="kwall")
    M["car"] = kit.plastic("#2e7d84", 0.35, name="car", spec=0.8)
    M["tyre"] = kit.plastic("#101114", 0.8, name="tyre")
    M["glassd"] = kit.plastic("#1b2b36", 0.1, name="cabin", spec=1.0)
    for st in ("round", "jagged"):
        for v in range(3):
            im = pil_image(f"box-{st}-{v}", scribble_image(st, 31 * v + (7 if st == "round" else 19)),
                           wd / f"box-{st}-{v}.png")
            M[f"{st}{v}"] = image_mat(kit, f"box {st} {v}", im)
    for n in list(range(1, 13)):
        im = pil_image(f"plate-{n}", digits_image(str(n)), wd / f"plate-{n}.png")
        M[f"plate{n}"] = image_mat(kit, f"plate {n}", im, rough=0.6)
    for nm, hexc, s in (("emit_tube", "#eaf2ff", 6.0), ("emit_lamp", "#ffd28a", 6.0), ("emit_sod", "#ffa845", 8.0),
                        ("emit_ring", "#3fdc7a", 1.6), ("emit_phone", "#dff0ff", 3.0), ("emit_win", "#fff3d8", 5.0),
                        ("emit_bulb", "#ffe0a8", 6.0)):
        M[nm] = _own_emit(kit, nm, hexc, s)
    return M


def _own_emit(kit, name, hexc, strength):
    m = kit._new(name)
    nt = m.node_tree
    nt.nodes.remove(nt.nodes["Principled BSDF"])
    e = nt.nodes.new("ShaderNodeEmission")
    e.inputs["Color"].default_value = kit.col(hexc)
    e.inputs["Strength"].default_value = strength
    kit._fogged(m, e.outputs[0])
    m["emit_node"] = e.name
    return m


def set_emit(m, strength):
    m.node_tree.nodes[m["emit_node"]].inputs["Strength"].default_value = strength


# ------------------------------------------------------------------------------------------ parts


def torus(kit, name, R, r, loc, mat, rot=(0, 0, 0), parent=None, seg=28, tube=8):
    verts, faces = [], []
    for i in range(seg):
        a = 2 * math.pi * i / seg
        for j in range(tube):
            b = 2 * math.pi * j / tube
            verts.append(((R + r * math.cos(b)) * math.cos(a), (R + r * math.cos(b)) * math.sin(a), r * math.sin(b)))
    for i in range(seg):
        for j in range(tube):
            a0, a1 = i * tube + j, ((i + 1) % seg) * tube + j
            b0, b1 = i * tube + (j + 1) % tube, ((i + 1) % seg) * tube + (j + 1) % tube
            faces.append((a0, a1, b1, b0))
    return kit.mesh_obj(name, verts, faces, mat, parent, loc, rot, smooth=True)


def corrugated(kit, name, w, h, f, mat, parent, period=0.1, amp=0.014):
    """A roller-door panel: a triangle-wave profile up its height, extruded across w. f = which way the corridor lies."""
    n = int(h / (period / 2))
    verts, faces = [], []
    for i in range(n + 1):
        z = h * i / n
        off = f * (amp if i % 2 else 0.0)
        verts += [(off, -w / 2, z), (off, w / 2, z)]
    for i in range(n):
        a = 2 * i
        faces.append((a, a + 2, a + 3, a + 1) if f > 0 else (a, a + 1, a + 3, a + 2))
    return kit.mesh_obj(name, verts, faces, mat, parent)


def build_door(kit, ctx, M, side, k, yc):
    """One roller door with its steel frame, header, number plate and hasp. side "B" (x>0.9) or "A"."""
    f = -1.0 if side == "B" else 1.0
    P = 0.9 if side == "B" else -1.1
    n = k
    root = kit.empty(f"door {n}", (P + (0.03 if side == "B" else 0.0) * 1.0, yc, 0))
    corrugated(kit, f"panel {n}", 2.0, UNIT_H, f, M["blue"], root)
    kit.box(f"rail {n}", (0.05, 2.0, 0.09), (f * 0.03, 0, 0.05), M["bluedk"], root)
    kit.box(f"plate {n}", (0.02, 0.32, 0.2), (f * 0.04, 0.62, 1.95), M["steelp"], root)
    kit.plane(f"plateimg {n}", (0.3, 0.18), (f * 0.0525, 0.62, 1.95), M[f"plate{n}"], root,
              rot=(math.pi / 2, 0, -math.pi / 2 if f < 0 else math.pi / 2))
    kit.box(f"hasp {n}", (0.03, 0.12, 0.05), (f * 0.04, 0.0, 0.14), M["steelp"], root)
    if side == "B":
        hdr = kit.box(f"header {n}", (0.24, 2.0, 0.5), (P - 0.0, yc, UNIT_H + 0.25), M["steelp"], bevel=0.01)
        for s in (-1, 1):   # steel jambs, proud of the partition
            kit.box(f"jamb {n}{s}", (0.2, 0.1, UNIT_H), (P - 0.02, yc + s * 1.05, UNIT_H / 2), M["steelp"])
    else:
        kit.box(f"header {n}", (0.24, 2.0, 0.5), (P, yc, UNIT_H + 0.25), M["steelp"])
        for s in (-1, 1):
            kit.box(f"jamb {n}{s}", (0.2, 0.1, UNIT_H), (P, yc + s * 1.05, UNIT_H / 2), M["steelp"])
    return root


def build_shell(kit, ctx, M):
    # floor under everything, and the dark ground outside
    kit.plane("floor", (9.2, 17.6), (-0.2, 7.4, 0), M["floor"])
    kit.plane("yard", (60, 40), (0, -21.2, -0.005), M["asphalt"])
    kit.plane("ground", (200, 200), (0, 0, -0.02), M["grass"])
    # the corridor and the units
    kit.box("roof", (8.8, 17.6, 0.3), (-0.2, 7.4, CEIL + 0.15), M["ceil"])
    kit.box("corr ceiling", (2.0, 17.2, 0.05), (-0.1, 7.4, CEIL - 0.02), M["ceil"])
    kit.box("wall A", (3.3, 17.2, CEIL), (-2.75, 7.4, CEIL / 2), M["wall"])
    kit.box("end wall", (2.0, 0.3, CEIL), (-0.1, END_Y + 0.15, CEIL / 2), M["wall"])
    kit.box("B front", (3.2, 2.9, CEIL), (2.5, 0.25, CEIL / 2), M["wall"])
    for i, y in enumerate((1.85, 4.15, 6.45, 8.75, 11.05, 13.35, 15.65)):
        kit.box(f"part {i}", (3.2, 0.3, CEIL), (2.5, y, CEIL / 2), M["wallin"])
    kit.box("B end", (3.2, 0.5, CEIL), (2.5, 15.95, CEIL / 2), M["wallin"])
    # building outside faces and the yard door's frame
    kit.box("facade L", (3.5, 0.3, CEIL + 0.3), (-2.75, YARD_Y - 0.15, (CEIL + 0.3) / 2), M["wall"])
    kit.box("facade R", (3.5, 0.3, CEIL + 0.3), (2.5, YARD_Y - 0.15, (CEIL + 0.3) / 2), M["wall"])
    kit.box("facade top", (1.8, 0.3, 0.7), (-0.1, YARD_Y - 0.15, 2.6 + 0.35), M["wall"])
    kit.box("yard door frame T", (2.0, 0.4, 0.1), (-0.1, YARD_Y - 0.1, 2.58), M["steelp"])
    for s in (-1, 1):
        kit.box(f"yard frame {s}", (0.1, 0.4, 2.6), (-0.1 + s * 0.95, YARD_Y - 0.1, 1.3), M["steelp"])
    kit.box("yard door roll", (1.9, 0.25, 0.25), (-0.1, YARD_Y - 0.05, 2.45), M["steelp"])
    kit.box("kerb", (8.0, 0.3, 0.12), (0, -9.5, 0.06), M["wall"])
    # unit interiors 7 to 12: back wall, side walls come from the partitions, a low ceiling slab
    for k, yc in YC.items():
        kit.box(f"back {k}", (0.2, 2.0, UNIT_H), (DEPTH_X + 0.1, yc, UNIT_H / 2), M["wallin"])
        kit.box(f"uceil {k}", (3.2, 2.0, 0.1), (2.5, yc, UNIT_H + 0.05), M["ceil"])
    # doors
    ctx["doors"] = {}
    for k, yc in YC.items():
        ctx["doors"][k] = build_door(kit, ctx, M, "B", k, yc)
    for k, yc in YA.items():
        build_door(kit, ctx, M, "A", k, yc)
    # the number plates: 7..12 on side B, 1..6 on side A, drawn as image planes above (done in build_door)
    # unit seven's bare bulb socket
    kit.cyl("socket", 0.03, 0.08, (2.3, YC[7], UNIT_H - 0.02), M["steelp"])
    kit.cyl("socket2", 0.02, 0.1, (2.3, YC[7], UNIT_H - 0.08), M["steelp"])


def build_post(kit, ctx, M):
    """Unit seven's frame post (inside face) with the two strokes and the padlock on its staple."""
    yc = YC[7]
    y = yc - 1.0 + 0.03
    kit.box("post7", (0.22, 0.04, UNIT_H), (1.01, yc - 1.0 + 0.02, UNIT_H / 2), M["steelp"])
    face = yc - 1.0 + 0.043   # the post's inside face
    for i, dx in enumerate((-0.035, 0.035)):
        kit.box(f"stroke{i}", (0.022, 0.005, 0.15), (1.01 + dx + 0.012, face, 0.6), M["stroke"])
    kit.box("staple", (0.1, 0.012, 0.05), (1.0, face + 0.005, 0.43), M["steelp"])
    pb = kit.box("padlock", (0.07, 0.035, 0.08), (1.0, face + 0.03, 0.385), M["pad"], bevel=0.01)
    torus(kit, "shackle", 0.025, 0.006, (1.0, face + 0.03, 0.43), M["steel"], rot=(math.pi / 2, 0, 0), seg=16, tube=6)
    kit.light("plant", "SPOT", (1.0, face + 0.55, 0.62), 40, "#fff0d8", size=0.05, spot=38, blend=0.5, shadow=False)
    kit.aim(bpy.data.objects["plant"], (1.0, face, 0.52))


def build_unit_seven(kit, ctx, M):
    yc = YC[7]
    ctx["boxes"] = {"left": [], "right": []}
    rnd = random.Random(5)
    for side, sgn, st in (("left", 1, "jagged"), ("right", -1, "round")):
        idx = 0
        for col in range(6):          # 6 along x from the back? idx order: back first so the front goes last
            for row in range(3):
                x = DEPTH_X - 0.25 - col * BOX[0] - 0.03
                y = yc + sgn * (AISLE + BOX[1] / 2 + 0.002)
                z = BOX[2] / 2 + row * BOX[2]
                ob = kit.box(f"box {side}{idx}", (BOX[0] - 0.01, BOX[1] - 0.01, BOX[2] - 0.01), (x, y, z), M["card"],
                             rot=(0, 0, math.radians(rnd.uniform(-1.4, 1.4))), bevel=0.012)
                dec = kit.plane(f"dec {side}{idx}", (BOX[0] - 0.03, BOX[2] - 0.03), (x, y - sgn * (BOX[1] / 2 + 0.004), z),
                                M[f"{st}{rnd.randint(0, 2)}"], None,
                                rot=(math.pi / 2, 0, math.pi if sgn < 0 else 0))
                ctx["boxes"][side].append((ob, dec, idx))
                if col == 5:   # the frontmost boxes also show their scribble to the corridor
                    fd = kit.plane(f"fdec {side}{idx}", (BOX[1] - 0.03, BOX[2] - 0.03),
                                   (x - BOX[0] / 2 - 0.004, y, z), M[f"{st}{rnd.randint(0, 2)}"], None,
                                   rot=(math.pi / 2, 0, -math.pi / 2))
                    ctx["boxes"][side].append((ob, fd, idx))
                idx += 1
    # my battery lamp on the floor in front of the right-hand stack
    ctx["lamp_pos"] = (1.08, yc - 0.55, 0.09)
    lx, ly, lz = ctx["lamp_pos"]
    ctx["lamp_objs"] = [kit.cyl("lamp body", 0.06, 0.16, (lx, ly, lz), M["dark"]),
                        kit.cyl("lamp glow", 0.052, 0.1, (lx, ly, lz + 0.02), M["emit_lamp"]),
                        kit.cyl("lamp cap", 0.062, 0.02, (lx, ly, lz + 0.09), M["steelp"])]
    kit.light("lamp", "POINT", (lx, ly, lz + 0.12), 30, "#ffcf8a", size=0.08)
    kit.light("unit glow", "POINT", (2.2, yc, 2.0), 14, "#ffcf8a", size=0.3, shadow=False)
    kit.light("lamp bounce", "POINT", (1.25, yc + 0.1, 0.35), 25, "#ffcf8a", size=0.08)
    kit.light("back rim", "SPOT", (2.1, yc + 0.15, 2.1), 160, "#9fc0ff", size=0.15, spot=70, blend=0.6, shadow=False)
    kit.aim(bpy.data.objects["back rim"], (1.1, yc, 1.5))
    kit.light("face under", "SPOT", (0.55, yc - 0.15, 0.25), 90, "#ffd9a0", size=0.1, spot=60, blend=0.7)
    kit.aim(bpy.data.objects["face under"], (1.0, yc, 1.55))
    # the keys on a box top: a ring and two brass keys
    top = (1.62, yc - AISLE - 0.25, 1.2)
    ctx["key_top"] = top
    ring = torus(kit, "ring", 0.04, 0.0055, top, M["steel"], seg=24, tube=6)
    ctx["ring"] = ring
    ctx["keys"] = []
    for i in range(2):
        e = kit.empty(f"key{i}", top)
        kit.box(f"keyshank{i}", (0.095, 0.011, 0.007), (0.06, 0, 0.004), M["brass"], e)
        torus(kit, f"keybow{i}", 0.017, 0.0055, (0.0, 0, 0.004), M["brass"], parent=e, seg=18, tube=6)
        for j in range(3):
            kit.box(f"keytooth{i}{j}", (0.012, 0.016, 0.007), (0.085 + j * 0.0, -0.011, 0.004), M["brass"], e)
        ctx["keys"].append(e)
    kit.light("key fill", "POINT", (1.6, yc - 0.9, 1.65), 12, "#ffe6bf", size=0.1, shadow=False)
    # the stroke plant has its own light (built with the post)


def build_corridor_props(kit, ctx, M):
    # push button with a dim green ring, by the entrance on side A
    kit.cyl("btn ring", 0.075, 0.02, (-1.1 + 0.015, 0.55, 1.25), M["emit_ring"], rot=(0, math.pi / 2, 0))
    kit.cyl("btn", 0.05, 0.03, (-1.1 + 0.03, 0.55, 1.25), M["steel"], rot=(0, math.pi / 2, 0))
    kit.box("btn plate", (0.02, 0.2, 0.3), (-1.1 + 0.005, 0.55, 1.25), M["dark"])
    kit.light("btn glow", "POINT", (-0.95, 0.55, 1.25), 3, "#3fdc7a", size=0.05, shadow=False)
    # the key-return slot in the wall by the entrance: a steel plate, a dark slot, no text
    kit.box("slot plate", (0.03, 0.34, 0.5), (-1.1 + 0.015, -0.3, 1.2), M["steelp"])
    kit.box("slot", (0.035, 0.2, 0.025), (-1.1 + 0.02, -0.3, 1.3), M["dark"])
    kit.light("slot light", "SPOT", (-0.1, -0.3, 1.9), 60, "#ffd9a0", size=0.1, spot=40, blend=0.6, shadow=False)
    kit.aim(bpy.data.objects["slot light"], (-1.1, -0.3, 1.25))
    # battens: emissive tubes and area lights, six along the ceiling; and a dim fill so the far end isn't black
    ctx["tubes"] = []
    for i, y in enumerate((0.7, 3.3, 5.9, 8.5, 11.1, 13.7)):
        kit.box(f"batten {i}", (0.14, 1.3, 0.05), (-0.1, y, CEIL - 0.07), M["emit_tube"])
        kit.light(f"batten{i}", "AREA", (-0.1, y, CEIL - 0.12), 150, "#e6eef8", size=1.4, shadow=True)
    kit.light("under", "POINT", (-0.1, 12.0, 2.2), 1, "#cfe0ff", size=0.3, shadow=False)
    # the sun, through the yard door
    sun = kit.light("sun", "SUN", (0, -10, 6), 5.0, "#ffc56b", size=0.1)
    kit.aim(sun, (SUN_DIR[0], -10 + SUN_DIR[1], 6 + SUN_DIR[2]))
    # a general sky fill outside (dim) so the yard is readable; the sodium lamp
    kit.cyl("pole", 0.07, 5.0, (-3.6, -6.5, 2.5), M["pole"])
    kit.box("pole arm", (0.9, 0.08, 0.08), (-3.2, -6.5, 5.0), M["pole"])
    kit.box("sod head", (0.5, 0.25, 0.1), (-2.85, -6.5, 4.98), M["emit_sod"])
    kit.light("sodium", "SPOT", (-2.85, -6.5, 4.9), 900, "#ffa845", size=0.2, spot=100, blend=0.8)
    kit.aim(bpy.data.objects["sodium"], (-1.5, -4.0, 0))
    kit.light("yard fill", "AREA", (0, -8, 6), 1500, "#aebfe0", size=14, shadow=False)
    kit.aim(bpy.data.objects["yard fill"], (0, -5, 0))
    # warm fill for the memory shots (corridor and unit seven)
    kit.light("mem fill", "AREA", (-0.1, 2.0, 2.6), 220, "#ffe2b0", size=3.0, shadow=False)
    kit.aim(bpy.data.objects["mem fill"], (-0.1, 3.0, 0.5))
    kit.light("mem unit", "POINT", (2.0, YC[7], 2.0), 90, "#ffe2b0", size=0.4, shadow=True)
    # distant low roofs for the dusk wide
    for i, (x, y, w, d, h) in enumerate(((-18, -22, 10, 8, 4.5), (14, -26, 12, 8, 5.5), (28, -14, 7, 7, 3.6),
                                           (-30, -9, 9, 6, 3.2))):
        kit.box(f"far {i}", (w, d, h), (x, y, h / 2), kit.plastic("#161a22", 0.9, name="far roof"))


def build_car(kit, ctx, M):
    car = kit.empty("car", (0, -14, 0))
    kit.box("car body", (1.7, 3.6, 0.6), (0, 0, 0.55), M["car"], car, bevel=0.1)
    kit.box("car cab", (1.5, 1.8, 0.55), (0, -0.2, 1.1), M["glassd"], car, bevel=0.12)
    for sx in (-1, 1):
        for sy in (-1, 1):
            kit.cyl(f"wheel{sx}{sy}", 0.3, 0.2, (sx * 0.85, sy * 1.15, 0.3), M["tyre"], car, rot=(0, math.pi / 2, 0))
    ctx["car"] = car
    car.hide_render = True
    for ob in car.children_recursive:
        ob.hide_render = True


def build_kitchen(kit, ctx, M):
    X, Y = 60.0, 0.0
    kit.plane("k floor", (5, 5), (X, Y, 0), M["wood"])
    kit.box("k back", (5, 0.1, 2.6), (X, Y + 2.5, 1.3), M["kwall"])
    kit.box("k side L", (0.1, 5, 2.6), (X - 2.5, Y, 1.3), M["kwall"])
    kit.box("k side R", (0.1, 5, 2.6), (X + 2.5, Y, 1.3), M["kwall"])
    kit.box("k front", (5, 0.1, 2.6), (X, Y - 2.5, 1.3), M["kwall"])
    kit.box("k ceil", (5, 5, 0.1), (X, Y, 2.65), M["kwall"])
    ctx["win"] = kit.box("k window", (1.6, 0.04, 1.2), (X + 1.0, Y + 2.44, 1.5), M["emit_win"])
    kit.box("k table", (1.4, 0.9, 0.06), (X - 0.2, Y + 0.3, 0.74), M["table"], bevel=0.01)
    for sx in (-1, 1):
        for sy in (-1, 1):
            kit.box(f"k leg{sx}{sy}", (0.06, 0.06, 0.74), (X - 0.2 + sx * 0.62, Y + 0.3 + sy * 0.38, 0.37), M["table"])
    kit.box("k mug", (0.08, 0.08, 0.1), (X - 0.55, Y + 0.45, 0.82), kit.plastic("#d7d0c4", 0.5, name="mug"))
    kit.cyl("k bulb", 0.07, 0.1, (X - 0.2, Y + 0.3, 2.45), M["emit_bulb"])
    kit.light("k lamp", "POINT", (X - 0.2, Y + 0.3, 2.3), 180, "#ffd9a0", size=0.2)
    kit.light("k day", "AREA", (X + 1.0, Y + 2.3, 1.6), 200, "#fff0dc", size=1.6, shadow=False)
    kit.aim(bpy.data.objects["k day"], (X + 0.6, Y, 1.3))
    kit.light("k fill", "AREA", (X, Y - 1.5, 2.4), 160, "#ffe6c8", size=3.0, shadow=False)
    kit.aim(bpy.data.objects["k fill"], (X, Y + 1, 1))
    ctx["kitchen"] = (X, Y)
    ctx["table_top"] = (X - 0.2, Y + 0.3, 0.775)


def build_carry(kit, ctx, M):
    """A box hugged to the chest: three variants parented later to whoever carries it."""
    ctx["carry"] = {}
    for st in ("round", "jagged", "small"):
        e = kit.empty(f"carry {st}", (0, 0, -30))
        if st == "small":
            kit.box("carry body small", (0.95, 0.85, 0.7), (0, 0, 0), M["card"], e, bevel=0.03)
            kit.plane("carry dec small", (0.9, 0.62), (0, -0.428, 0), M["round1"], e, rot=(math.pi / 2, 0, 0))
            e.hide_render = True
            for ob in e.children_recursive:
                ob.hide_render = True
            ctx["carry"][st] = e
            continue
        kit.box(f"carry body {st}", (1.5, 1.35, 1.1), (0, 0, 0), M["card"], e, bevel=0.03)
        kit.plane(f"carry dec {st}", (1.42, 1.0), (0, -0.678, 0), M[f"{st}0"], e, rot=(math.pi / 2, 0, 0))
        e.hide_render = True
        for ob in e.children_recursive:
            ob.hide_render = True
        ctx["carry"][st] = e
    # one small box, sitting on the floor of seven at the end (a lone round-scribbled box)
    sm = kit.empty("small box", (0, 0, -30))
    kit.box("small body", (0.36, 0.3, 0.26), (0, 0, 0.13), M["card"], sm, bevel=0.01)
    kit.plane("small dec", (0.34, 0.24), (0, -0.152, 0.13), M["round1"], sm, rot=(math.pi / 2, 0, 0))
    ctx["small"] = sm
    # my phone's torch and glow
    kit.light("torch", "SPOT", (0, 0, -30), 450, "#f4f8ff", size=0.04, spot=48, blend=0.6)
    kit.light("phone", "POINT", (0, 0, -30), 14, "#dff0ff", size=0.05, shadow=False)
    # a phone prop for the call: a small dark slab with a lit face, hung from my head (placed in animate)
    ph = kit.empty("phone prop", (0, 0, -30))
    kit.box("phone body", (0.3, 0.1, 0.55), (0, 0, 0), M["dark"], ph, bevel=0.02)
    kit.box("phone screen", (0.24, 0.02, 0.45), (0, -0.055, 0), M["emit_phone"], ph)
    ctx["phoneprop"] = ph


def build(kit, story, tl):
    ctx = {"story": story}
    wd = workdir(tl)
    M = materials(kit, wd)
    ctx["M"] = M
    build_shell(kit, ctx, M)
    build_post(kit, ctx, M)
    build_unit_seven(kit, ctx, M)
    build_corridor_props(kit, ctx, M)
    build_car(kit, ctx, M)
    build_kitchen(kit, ctx, M)
    build_carry(kit, ctx, M)
    # the number-plate planes need their images the right way up; that is checked in the stills
    ctx["wd"] = wd
    return ctx


# ------------------------------------------------------------------------------------------ the Deep One


def build_deep(kit, ctx):
    """Extrude the rig's body straight back, 2.7 m: a person pushed out of a mould and never cut off."""
    root = bpy.data.objects.get("deep")
    if root is None or ctx.get("deep_done"):
        return
    ctx["deep_done"] = True
    M = ctx["M"]
    blue = kit.plastic("#3d6fa8", 0.5, name="deep blue", spec=0.5)
    blue2 = kit.plastic("#33608f", 0.55, name="deep rib")
    skin = kit.plastic("#b3a187", 0.6, name="deep skin")
    cap = kit.plastic("#54432f", 0.92, name="deep cap")
    dust = kit.plastic("#7d6548", 0.95, name="deep dust")
    L = 2.7 / RIG_S
    y0 = 0.5
    yc = y0 + L / 2
    ctx["deep_parts"] = []
    for sx in (-1, 1):
        kit.box(f"deep leg{sx}", (0.98, L, 1.72), (sx * 0.5, yc, 1.14), blue, root, bevel=0.03)
        kit.box(f"deep shoe{sx}", (0.99, L, 0.3), (sx * 0.5, yc, 0.15), dust, root, bevel=0.03)
        kit.box(f"deep arm{sx}", (0.96, L, 1.9), (sx * 1.5, yc, 3.0), blue, root, bevel=0.03)
        # ribs along the outer flank, like a roller door, and dust along the foot of it
        for j, z in enumerate((2.25, 2.62, 2.99, 3.36, 3.73)):
            kit.box(f"deep rib a{sx}{j}", (0.06, L, 0.1), (sx * 2.0, yc, z), blue2, root)
        for j, z in enumerate((0.6, 0.95, 1.3, 1.65)):
            kit.box(f"deep rib l{sx}{j}", (0.05, L, 0.09), (sx * 1.0 + sx * 0.02, yc, z), blue2, root)
        kit.box(f"deep grime{sx}", (0.07, L, 0.62), (sx * 1.0 + sx * 0.03, yc, 0.42), dust, root)
        kit.box(f"deep grimea{sx}", (0.08, L, 0.45), (sx * 2.0 + sx * 0.02, yc, 2.28), dust, root)
    kit.box("deep torso", (2.0, L, 2.0), (0, yc, 3.0), blue, root, bevel=0.03)
    for j, z in enumerate((2.3, 2.7, 3.1, 3.5, 3.85)):
        kit.box(f"deep rib t{j}", (2.02, L, 0.08), (0, yc, z), blue2, root)
    kit.box("deep dust top", (1.9, L * 0.8, 0.07), (0, yc + L * 0.1, 4.03), dust, root)
    ht = kit.cyl("deep headtube", 0.58, L, (0, yc + 0.12, 4.62), skin, root, rot=(math.pi / 2, 0, 0))
    capb = kit.box("deep captop", (1.36, L, 0.42), (0, yc + 0.12, 5.31), cap, root, bevel=0.1)
    ctx["deep_head_parts"] = [ht, capb]


# ------------------------------------------------------------------------------------------ animate

TIMES = {   # sky colour, sky strength, sun gain, sodium, yard fill, mem fill, batten multiplier, exposure
    "dusk": ("#161d2e", 0.45, 0.0, 1.0, 0.15, 0.0, 1.0, 0.0),
    "mem": ("#bcd0ee", 1.6, 0.5, 0.0, 1.0, 1.0, 1.0, 0.1),
    "day": ("#a9c4ea", 1.5, 0.9, 0.0, 1.0, 0.0, 0.85, 0.0),
    "sun": ("#f3b574", 1.5, 1.0, 0.0, 0.8, 0.5, 1.0, 0.0),
}


def _hexrgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))


def _lin(c):
    return tuple(x / 12.92 if x <= 0.04045 else ((x + 0.055) / 1.055) ** 2.4 for x in c)


def _time_state(tl, t):
    cs = _cues(tl, "time")
    cur = _last(cs, t)
    name = cur["set"] if cur else "dusk"
    vals = list(TIMES[name])
    # blend over 0.8 s from the previous state
    prev_i = cs.index(cur) - 1 if cur else -1
    if cur and prev_i >= 0:
        u = _ss((t - cur["t"]) / float(cur.get("dur", 0.6)))
        pv = TIMES[cs[prev_i]["set"]]
        c0, c1 = _lin(_hexrgb(pv[0])), _lin(_hexrgb(vals[0]))
        vals[0] = tuple(a + (b - a) * u for a, b in zip(c0, c1))
        for i in range(1, 8):
            vals[i] = pv[i] + (vals[i] - pv[i]) * u
    else:
        vals[0] = _lin(_hexrgb(vals[0]))
    return vals


def animate(kit, story, tl, t, ctx):
    M = ctx["M"]
    build_deep(kit, ctx)
    over = {}
    sky, skys, sun, sod, yfill, mfill, bmul, expo = _time_state(tl, t)
    w = bpy.context.scene.world
    bg = w.node_tree.nodes["Background"]
    bg.inputs["Color"].default_value = (*sky, 1)
    bg.inputs["Strength"].default_value = skys
    bpy.context.scene.view_settings.exposure = expo
    # the corridor battens: slow ramps only
    corr = _ramp(_cues(tl, "corr"), t, "level", 1.0)
    for i in range(6):
        over[f"batten{i}"] = corr * bmul
    set_emit(M["emit_tube"], 0.3 + 5.7 * corr)
    over["under"] = 0.0
    over["sun"] = sun
    over["sodium"] = sod
    over["yard fill"] = yfill
    over["mem fill"] = mfill
    over["mem unit"] = mfill
    # the doors
    for k, root in ctx["doors"].items():
        cs = [c for c in _cues(tl, "door") if c.get("unit") == k]
        v = _ramp(cs, t, "open", 0.0)
        root.location.z = v * (UNIT_H + 0.05)
        for ob in root.children_recursive:
            ob.hide_render = v > 0.995
    # unit seven's stacks
    sc = _last(_cues(tl, "stacks"), t)
    nl = sc["left"] if sc else STACK_N
    nr = sc["right"] if sc else STACK_N
    for side, n in (("left", nl), ("right", nr)):
        for ob, dec, idx in ctx["boxes"][side]:
            on = idx < n
            ob.hide_render = not on
            dec.hide_render = not on
    # my lamp
    lamp = _ramp(_cues(tl, "lamp"), t, "on", 1.0)
    over["lamp"] = lamp
    over["unit glow"] = lamp
    for ob in ctx["lamp_objs"][1:2]:
        ob.hide_render = lamp < 0.05
    set_emit(M["emit_lamp"], 6.0 * lamp)
    fl = _last(_cues(tl, "facelight"), t)
    fon = float(fl["on"]) if fl else 0.0
    over["lamp bounce"] = fon
    over["face under"] = fon
    over["back rim"] = fon
    # plant light, key fill, slot light
    pc = _last(_cues(tl, "plant"), t)
    over["plant"] = float(pc["on"]) if pc else 0.0
    kc = _last(_cues(tl, "keys"), t)
    mode = kc["mode"] if kc else "none"
    over["key fill"] = 1.0 if mode == "ring2" else 0.0
    sl = _last(_cues(tl, "slotlight"), t)
    over["slot light"] = float(sl["on"]) if sl else 0.0
    place_keys(ctx, mode)
    # the kitchen
    kt = _last(_cues(tl, "kitchen"), t)
    ks = kt["set"] if kt else "night"
    over["k lamp"] = 1.0 if ks == "night" else 0.0
    over["k day"] = 1.0 if ks == "day" else 0.0
    over["k fill"] = 1.0 if ks == "day" else 0.25
    set_emit(M["emit_bulb"], 6.0 if ks == "night" else 0.5)
    set_emit(M["emit_win"], 1.0 if ks == "night" else 8.0)
    # Jo's car
    cc = _cues(tl, "car")
    car = ctx["car"]
    if cc:
        pos, yaw, shown = None, 0.0, False
        for i, c in enumerate(cc):
            if c["t"] > t + 1e-9:
                break
            shown = True
            d = float(c.get("dur", 0.0))
            a = (cc[i - 1]["pos"], cc[i - 1].get("yaw", 0.0)) if i else (c["pos"], c.get("yaw", 0.0))
            u = 1.0 if d <= 1e-6 else _ss((t - c["t"]) / d)
            pos = [a[0][0] + (c["pos"][0] - a[0][0]) * u, a[0][1] + (c["pos"][1] - a[0][1]) * u]
            yaw = a[1] + (c.get("yaw", 0.0) - a[1]) * u
            if c.get("hide"):
                shown = False
        car.hide_render = not shown
        for ob in car.children_recursive:
            ob.hide_render = not shown
        if pos:
            car.location = (pos[0], pos[1], 0)
            car.rotation_euler = (0, 0, math.radians(yaw))
    # who carries what
    cr = {k: v for k, v in ctx["carry"].items()}
    for e in cr.values():
        _show(e, False)
    carry = _last(_cues(tl, "carry"), t)
    sm = ctx["small"]
    smc = _last(_cues(tl, "small"), t)
    if smc and smc.get("on"):
        sm.location = tuple(smc["pos"])
        _show(sm, True)
    else:
        _show(sm, False)
    me = bpy.data.objects.get("me")
    jo = bpy.data.objects.get("jo")
    bpy.context.view_layer.update()
    if carry and carry.get("on"):
        who = bpy.data.objects.get(carry["who"])
        tor = bpy.data.objects.get(f"{carry['who']}.torso")
        e = cr[carry["style"]]
        if who is not None and tor is not None and not who.hide_render:
            e.parent = tor
            e.location = (0, -1.15, 1.0)
            e.rotation_euler = (0, 0, 0)
            e.scale = (1, 1, 1)
            _show(e, True)
    # my lights: phone glow and torch follow me
    pg = _ramp(_cues(tl, "phone"), t, "on", 0.0)
    tc = _ramp(_cues(tl, "torch"), t, "on", 0.0)
    L = kit.LIGHTS
    if me is not None and not me.hide_render:
        mx, my = me.location.x, me.location.y
        yaw = me.rotation_euler.z
        fx, fy = math.sin(yaw), -math.cos(yaw)
        L["phone"]["obj"].location = (mx + fx * 0.3, my + fy * 0.3, 1.1)
        L["torch"]["obj"].location = (mx + fx * 0.25, my + fy * 0.25, 1.15)
        kit.aim(L["torch"]["obj"], (mx + fx * 3.0, my + fy * 3.0, 0.9))
        over["phone"] = pg * 0.6
        over["torch"] = tc
    else:
        over["phone"] = 0.0
        over["torch"] = 0.0
    # the phone at my ear (the call)
    ppc = _last(_cues(tl, "call"), t)
    pp = ctx["phoneprop"]
    if ppc and ppc.get("on") and me is not None and not me.hide_render:
        head = bpy.data.objects.get("me.head")
        pp.parent = head
        pp.location = (-0.75, -0.05, 0.62)
        pp.rotation_euler = (0, 0, math.radians(90))
        _show(pp, True)
    else:
        _show(pp, False)
    # the Deep One: the tube behind its head, and its edge light
    hc = _last(_cues(tl, "headtube"), t)
    ht = bool(hc["on"]) if hc else True
    for ob in ctx.get("deep_head_parts", []):
        dr = bpy.data.objects.get("deep")
        ob.hide_render = (dr is not None and dr.hide_render) or not ht
    return over


def _show(e, on):
    e.hide_render = not on
    for ob in e.children_recursive:
        ob.hide_render = not on


def place_keys(ctx, mode):
    ring = ctx["ring"]
    k0, k1 = ctx["keys"]
    if mode == "ring2":
        x, y, z = ctx["key_top"]
        _show(ring, True)
        ring.location = (x, y, z + 0.006)
        for kk, a in ((k0, 35), (k1, -75)):
            kk.location = (x + 0.04 * math.cos(math.radians(a)), y + 0.04 * math.sin(math.radians(a)), z + 0.006)
            kk.rotation_euler = (0, 0, math.radians(a))
        _show(k0, True)
        _show(k1, True)
    elif mode == "table":
        x, y, z = ctx["table_top"]
        _show(ring, True)
        ring.location = (x - 0.05, y, z + 0.006)
        k0.location = (x - 0.05 + 0.04 * math.cos(math.radians(30)), y + 0.04 * math.sin(math.radians(30)), z + 0.006)
        k0.rotation_euler = (0, 0, math.radians(30))
        _show(k0, True)
        k1.location = (x + 0.2, y - 0.05, z + 0.003)    # the second key on its own beside the ring
        k1.rotation_euler = (0, 0, math.radians(-20))
        _show(k1, True)
    else:
        for e in (ring, k0, k1):
            _show(e, False)
