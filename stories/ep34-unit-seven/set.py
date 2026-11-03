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
from mathutils import Vector
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
HX = 100.0             # the town house front (the montage and Jo's door): wall front face at y 0, street toward -y
CX = 140.0             # the high kitchen cupboard
# which little set is lit: (street fill, hall light, Jo's room, cupboard, house lamp, sock rack shown, taped box shown, door open)
SCENES = {
    "none": (0.0, 0.0, 0.0, 0.0, 0.0, 0, 0, 1),
    "sock": (1.0, 1.0, 0.5, 0.0, 1.0, 1, 0, 1),
    "cupboard": (0.0, 0.0, 0.0, 1.0, 0.0, 0, 0, 1),
    "box": (0.7, 1.0, 0.4, 0.0, 1.0, 0, 1, 1),
    "street": (1.7, 0.35, 1.0, 0.0, 0.0, 0, 0, 0),
}


def _ss(x):
    x = min(1.0, max(0.0, x))
    return x * x * (3 - 2 * x)


def _cues(tl, name):
    # in time order: later-listed cues (e.g. the L45/L46 stacks) must not shadow earlier-timed ones in _last/_ramp
    return sorted((c for c in tl.get("cues", []) if c["name"] == name), key=lambda c: c["t"])


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
        if ch == "7":   # a stencilled 7: a top bar and a slanted stem, so it can't read as a 1
            d.rectangle([x - 8, y0, x + dw + 8, y0 + th + 4], fill=ink)
            d.polygon([(x + dw + 8, y0), (x + dw - 30, y0), (x + 6, y0 + dh), (x + 40, y0 + dh)], fill=ink)
            continue
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
        # one loose coil that winds out from the middle: never two stacked rings (an "8"), never a loop-and-stem
        cx = w // 2 + rnd.randint(-30, 30)
        cy = h // 2 + rnd.randint(-20, 20)
        pts = []
        turns = 3.2
        for i in range(0, 241):
            a = math.radians(i * 360 * turns / 240 + rnd.uniform(-1, 1))
            r = 10 + 82 * (i / 240)
            pts.append((cx + r * 1.15 * math.cos(a), cy + r * 0.9 * math.sin(a)))
        d.line(pts, fill=ink, width=th, joint="curve")
        for p in (pts[0], pts[-1]):
            d.ellipse([p[0] - th / 2, p[1] - th / 2, p[0] + th / 2, p[1] + th / 2], fill=ink)
    else:
        # a tangled scrawl of long straight cuts at odd angles: never a W or an M
        pts = []
        ang = rnd.uniform(0, 6.28)
        x, y = w / 2 + rnd.randint(-40, 40), h / 2 + rnd.randint(-30, 30)
        for i in range(9):
            ang += rnd.choice((1, -1)) * rnd.uniform(2.0, 2.7)
            ln = rnd.uniform(95, 150)
            x = min(w - 70, max(70, x + ln * math.cos(ang)))
            y = min(h - 70, max(70, y + ln * 0.8 * math.sin(ang)))
            pts.append((x, y))
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
    M["stroke"] = kit.plastic("#2368b8", 0.6, name="stroke blue")
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
    M["brick"] = kit.grime("#8a4c3a", 0.55, 2.2, name="town brick", rough=0.85)
    M["pave"] = kit.concrete("#a29f98", scale=1.5, stains=0.3, name="pavement")
    M["trim"] = kit.plastic("#e4dfd2", 0.6, name="trim")
    M["hdoor"] = kit.plastic("#6e2a38", 0.45, name="house door", spec=0.5)
    M["hwall"] = kit.plastic("#d9ccb0", 0.9, name="hall wall")
    M["roomwall"] = kit.plastic("#cfa57e", 0.9, name="room wall")
    M["cupout"] = kit.plastic("#b99a6e", 0.7, name="cupboard wood")
    M["cupin"] = kit.plastic("#efe7d6", 0.8, name="cupboard inside")
    M["sock_r"] = kit.plastic("#8c2a2a", 0.9, name="sock red")
    M["sock_w"] = kit.plastic("#4d6482", 0.9, name="sock white")
    M["sock_c"] = kit.plastic("#d8d2c2", 0.9, name="sock cuff")
    M["tape"] = kit.plastic("#dccb9c", 0.35, name="tape")
    M["spoon"] = kit.metal("#34383d", 0.4, name="spoon")
    for st in ("round", "jagged"):
        for v in range(3):
            im = pil_image(f"box-{st}-{v}", scribble_image(st, 31 * v + (7 if st == "round" else 19)),
                           wd / f"box-{st}-{v}.png")
            M[f"{st}{v}"] = image_mat(kit, f"box {st} {v}", im)
    for n in list(range(1, 13)) + list(range(21, 27)):
        im = pil_image(f"plate-{n}", digits_image(str(n)), wd / f"plate-{n}.png")
        M[f"plate{n}"] = image_mat(kit, f"plate {n}", im, rough=0.6)
    for nm, hexc, s in (("emit_tube", "#eaf2ff", 6.0), ("emit_lamp", "#ffd28a", 6.0), ("emit_sod", "#ffa845", 8.0),
                        ("emit_ring", "#3fdc7a", 1.6), ("emit_phone", "#dff0ff", 3.0), ("emit_win", "#fff3d8", 3.0),
                        ("emit_bulb", "#ffe0a8", 6.0), ("emit_hbulb", "#ffe0a8", 6.0),
                        ("emit_roombulb", "#ffd9a0", 5.0)):
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


def uvplane(kit, name, size, loc, mat, parent=None, rot=(0, 0, 0)):
    """kit.plane with a UV map, so an image (a scribble, a number plate) lands on it whole."""
    ob = kit.plane(name, size, loc, mat, parent, rot)
    uv = ob.data.uv_layers.new(name="UVMap")
    corners = [(0, 0), (1, 0), (1, 1), (0, 1)]
    for poly in ob.data.polygons:
        for k, li in enumerate(poly.loop_indices):
            uv.data[li].uv = corners[ob.data.loops[li].vertex_index]
    return ob


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
    n = k if side == "B" else 20 + k   # side A reads 21..26 so no plate across from seven reads "1"
    root = kit.empty(f"door {n}", (P + (0.03 if side == "B" else 0.0) * 1.0, yc, 0))
    corrugated(kit, f"panel {n}", 2.0, UNIT_H, f, M["blue"], root)
    kit.box(f"rail {n}", (0.05, 2.0, 0.09), (f * 0.03, 0, 0.05), M["bluedk"], root)
    pl1 = kit.box(f"plate {n}", (0.02, 0.32, 0.2), (f * 0.04, 0.62, 1.95), M["steelp"], root)
    pl2 = uvplane(kit, f"plateimg {n}", (0.3, 0.18), (f * 0.0525, 0.62, 1.95), M[f"plate{n}"], root,
                  rot=(math.pi / 2, 0, -math.pi / 2 if f < 0 else math.pi / 2))
    ctx.setdefault("plates", []).append((root, f, (pl1, pl2)))
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
    ctx["voids"] = {}
    for k, yc in YC.items():   # a black sheet in the doorway, shown only in the shots that frame an open door from afar
        ctx["voids"][k] = kit.box(f"void {k}", (0.02, 1.9, UNIT_H), (1.0, yc, UNIT_H / 2), M["dark"])
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
        kit.box(f"stroke{i}", (0.02, 0.005, 0.11), (1.01 + dx + 0.012, face, 0.6), M["stroke"])
    kit.box("staple", (0.1, 0.012, 0.05), (1.0, face + 0.005, 0.40), M["steelp"])
    pb = kit.box("padlock", (0.07, 0.035, 0.08), (1.0, face + 0.03, 0.345), M["pad"], bevel=0.01)
    torus(kit, "shackle", 0.025, 0.006, (1.0, face + 0.03, 0.395), M["steel"], rot=(math.pi / 2, 0, 0), seg=16, tube=6)
    kit.light("plant", "SPOT", (1.0, face + 0.55, 0.62), 2.2, "#fff0d8", size=0.05, spot=38, blend=0.5, shadow=False)
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
                vv = rnd.randint(0, 2)
                dec = uvplane(kit, f"dec {side}{idx}", (BOX[0] - 0.03, BOX[2] - 0.03), (x, y - sgn * (BOX[1] / 2 + 0.004), z),
                                M[f"{st}{vv}"], None,
                                rot=(math.pi / 2, 0, math.pi if sgn < 0 else 0))
                ctx.setdefault("decvar", {})[dec.name] = (st, vv)
                ctx["boxes"][side].append((ob, dec, idx))
                if col == 5:   # the frontmost boxes also show their scribble to the corridor
                    vv = rnd.randint(0, 2)
                    fd = uvplane(kit, f"fdec {side}{idx}", (BOX[1] - 0.03, BOX[2] - 0.03),
                                   (x - BOX[0] / 2 - 0.004, y, z), M[f"{st}{vv}"], None,
                                   rot=(math.pi / 2, 0, -math.pi / 2))
                    ctx.setdefault("decvar", {})[fd.name] = (st, vv)
                    ctx["boxes"][side].append((ob, fd, idx))
                idx += 1
    # corrugated steel on unit seven's side walls (the wall the scrape runs along)
    for nm, y, f in (("wallsheet L", yc + 1.0 - 0.005, -1.0), ("wallsheet R", yc - 1.0 + 0.005, 1.0)):
        e = kit.empty(nm, (2.5, y, 0), rot=(0, 0, math.pi / 2))
        corrugated(kit, nm + " m", 3.2, UNIT_H, f, M["steelp"], e, period=0.1, amp=0.016)
    # the dent in the round stack's top front box where I sat: a crumpled ring round a sunken dark dish
    tx = DEPTH_X - 0.25 - 5 * BOX[0] - 0.03
    ty = yc - (AISLE + BOX[1] / 2 + 0.002)
    tz = 3 * BOX[2]
    ctx["dent"] = [torus(kit, "dent rim", 0.15, 0.03, (tx, ty, tz + 0.012), M["card"], seg=24, tube=8),
                   kit.cyl("dent dish", 0.15, 0.03, (tx, ty, tz - 0.004), M["dark"])]
    ctx["dent"] += [kit.box("dent lip", (0.3, 0.07, 0.04), (tx, ty + BOX[1] / 2 - 0.02, tz - 0.01), M["card"], rot=(math.radians(-25), 0, 0))]
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
    kit.light("face under", "SPOT", (0.55, yc - 0.15, 0.25), 230, "#ffd9a0", size=0.1, spot=60, blend=0.7)
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
    kit.light("mem unit", "POINT", (3.4, YC[7], 1.9), 260, "#ffe2b0", size=0.4, shadow=True)
    # distant low roofs for the dusk wide
    for i, (x, y, w, d, h) in enumerate(((-18, -22, 10, 8, 4.5), (14, -26, 12, 8, 5.5), (28, -14, 7, 7, 3.6),
                                           (-30, -9, 9, 6, 3.2))):
        kit.box(f"far {i}", (w, d, h), (x, y, h / 2), kit.plastic("#3a414d", 0.9, name="far roof"))


def door_lamp(kit, ctx, M, n, loc, axis, light=None):
    """The town's door lamp (our own design): a round lens in a galvanised ring on a dark plate, 17 cm across,
    dark unless it is lit for someone. axis: "x+" faces +x, "x-" faces -x, "y-" faces -y."""
    x, y, z = loc
    if axis == "y-":
        rot, d = (math.pi / 2, 0, 0), (0, -1, 0)
    elif axis == "x-":
        rot, d = (0, math.pi / 2, 0), (-1, 0, 0)
    else:
        rot, d = (0, math.pi / 2, 0), (1, 0, 0)

    def at(k):
        return (x + d[0] * k, y + d[1] * k, z + d[2] * k)
    m = _own_emit(kit, f"dlens{n}", "#52b4ff", 0.05)
    kit.cyl(f"dlbase{n}", 0.125, 0.02, at(0.0), M["dark"], rot=rot, n=28)
    kit.cyl(f"dlens{n}", 0.085, 0.03, at(0.03), m, rot=rot, n=28)
    torus(kit, f"dlring{n}", 0.105, 0.014, at(0.02), M["steel"], rot=rot, seg=32, tube=8)
    lname = None
    if light:
        lname = f"dl{n}"
        lx, ly, lz = at(0.25)
        kit.light(lname, "POINT", (lx, ly, lz), 3, "#6cc3ff", size=0.06, shadow=False)
    ctx.setdefault("dl", {})[n] = {"mat": m, "light": lname}


def build_dlamps(kit, ctx, M):
    # a soft blue bloom round unit seven's lamp, drawn only for the closing fade (so that fade reads at a distance)
    hm = kit._new("halo7")
    nt = hm.node_tree
    nt.nodes.remove(nt.nodes["Principled BSDF"])
    tc = nt.nodes.new("ShaderNodeTexCoord")
    mp = nt.nodes.new("ShaderNodeMapping")
    mp.inputs["Location"].default_value = (-1.0, -1.0, 0.0)
    mp.inputs["Scale"].default_value = (2.0, 2.0, 2.0)
    gr = nt.nodes.new("ShaderNodeTexGradient")
    gr.gradient_type = "SPHERICAL"
    em = nt.nodes.new("ShaderNodeEmission")
    em.inputs["Color"].default_value = kit.col("#52b4ff")
    em.inputs["Strength"].default_value = 0.0
    tr = nt.nodes.new("ShaderNodeBsdfTransparent")
    mx = nt.nodes.new("ShaderNodeMixShader")
    nt.links.new(tc.outputs["UV"], mp.inputs["Vector"])
    nt.links.new(mp.outputs["Vector"], gr.inputs["Vector"])
    nt.links.new(gr.outputs["Fac"], mx.inputs["Fac"])
    nt.links.new(tr.outputs[0], mx.inputs[1])
    nt.links.new(em.outputs[0], mx.inputs[2])
    kit._fogged(hm, mx.outputs[0])
    hm["emit_node"] = em.name
    ctx["halo7"] = (uvplane(kit, "halo7", (1.6, 1.6), (0.745, YC[7], 2.55), hm, None, (math.pi / 2, 0, -math.pi / 2)), hm)
    for k, yc in YC.items():     # side B: on the header's corridor face (x 0.78), lit lights for the doors the story lifts
        door_lamp(kit, ctx, M, k, (0.775, yc, 2.55), "x-", light=k in (7, 9, 10, 11))
    for k, yc in YA.items():
        door_lamp(kit, ctx, M, 20 + k, (-0.975, yc, 2.55), "x+")


def build_town(kit, ctx, M):
    """A terrace front for the montage and Jo's door (wall front face at y 0, pavement and street at -y), and a cupboard."""
    X = HX
    kit.plane("t pave", (20, 2.5), (X, -1.25, 0.0), M["pave"])
    kit.plane("t road", (60, 14), (X, -9.5, -0.01), M["asphalt"])
    kit.plane("t ground", (60, 30), (X, 8, -0.02), M["grass"])
    kit.box("t kerb", (20, 0.25, 0.14), (X, -2.6, 0.07), M["wall"])
    for j, (dy, h) in enumerate(((1.05, 0.18), (0.7, 0.37), (0.35, 0.55))):   # three steps up to the door
        kit.box(f"t step{j}", (1.5, dy, h), (X + 0.7, -dy / 2, h / 2), M["pave"])
    # facade, with a door opening (x +0.2 .. +1.2, to 2.15) and a window (x -2.15 .. -0.85, z 0.9 .. 2.1)
    H3 = 3.4
    for nm, (x0, x1, z0, z1) in {"l": (-3.8, -2.15, 0, H3), "m": (-0.85, 0.2, 0, H3), "r": (1.2, 3.8, 0, H3),
                                 "wb": (-2.15, -0.85, 0, 0.9), "wt": (-2.15, -0.85, 2.1, H3),
                                 "dt": (0.2, 1.2, 2.15, H3), "db": (0.2, 1.2, 0, 0.55)}.items():
        kit.box(f"t wall {nm}", (x1 - x0, 0.3, z1 - z0), (X + (x0 + x1) / 2, 0.15, (z0 + z1) / 2), M["brick"])
    cxw = X - 1.5
    kit.box("t sill", (1.5, 0.14, 0.06), (cxw, -0.06, 0.88), M["trim"])
    kit.box("t whead", (1.4, 0.05, 0.06), (cxw, -0.03, 2.13), M["trim"])
    for sx in (-1, 1):
        kit.box(f"t wpost{sx}", (0.06, 0.05, 1.2), (cxw + sx * 0.68, -0.03, 1.5), M["trim"])
        kit.box(f"t dpost{sx}", (0.07, 0.05, 2.15), (X + 0.7 + sx * 0.535, -0.03, 1.075), M["trim"])
    kit.box("t dhead", (1.14, 0.05, 0.07), (X + 0.7, -0.03, 2.18), M["trim"])
    door_lamp(kit, ctx, M, "H", (X + 0.7, -0.01, 2.42), "y-", light=True)
    bpy.data.lights["dlH"].energy = 7
    # the door leaf: hinged at its left edge, closed in the opening or swung back against the hall wall
    piv = kit.empty("t door pivot", (X + 0.2, 0.12, 0.55))
    kit.box("t door leaf", (0.98, 0.05, 1.6), (0.5, 0, 0.8), M["hdoor"], piv, bevel=0.01)
    kit.cyl("t knob", 0.035, 0.05, (0.86, -0.05, 0.5), M["brass"], piv, rot=(math.pi / 2, 0, 0))
    ctx["hdoor"] = piv
    # the hall: 1 m wide, 3.2 m deep
    kit.plane("t hall floor", (1.0, 2.1), (X + 0.7, 1.35, 0.55), M["wood"])
    kit.box("t hall wl", (0.15, 2.2, 2.6), (X + 0.125, 1.35, 1.3), M["hwall"])
    kit.box("t hall wr", (0.15, 2.2, 2.6), (X + 1.275, 1.35, 1.3), M["hwall"])
    kit.box("t hall back", (1.5, 0.1, 2.6), (X + 0.7, 2.45, 1.3), M["hwall"])
    kit.box("t hall ceil", (1.5, 2.3, 0.1), (X + 0.7, 1.35, 2.65), M["hwall"])
    kit.cyl("t hall bulb", 0.07, 0.08, (X + 0.7, 1.2, 2.56), M["emit_hbulb"])
    kit.light("hall", "POINT", (X + 0.7, 1.0, 2.3), 110, "#ffdca0", size=0.2)
    kit.light("hall back", "POINT", (X + 0.7, 1.4, 1.5), 60, "#ffdca0", size=0.3, shadow=False)
    # shoe rack on the right wall, one striped sock on its top shelf
    rk = []
    FZ = 0.55
    for j, z in enumerate((FZ + 0.16, FZ + 0.42)):
        rk.append(kit.box(f"t rack shelf{j}", (0.84, 0.26, 0.03), (X + 0.7, 2.15, z), M["table"]))
    for j, xx in enumerate((X + 0.3, X + 1.1)):
        rk.append(kit.box(f"t rack end{j}", (0.03, 0.26, 0.46), (xx, 2.15, FZ + 0.23), M["table"]))
    stripes = []
    top = FZ + 0.42 + 0.015
    # one wool sock: a long blue foot with a red toe and heel, a leg standing up from the heel, a pale ribbed cuff
    stripes.append(kit.box("t sock foot", (0.42, 0.17, 0.11), (X + 0.5, 2.15, top + 0.055), M["sock_w"], bevel=0.045))
    stripes.append(kit.box("t sock toe", (0.1, 0.172, 0.112), (X + 0.3, 2.15, top + 0.056), M["sock_r"], bevel=0.04))
    stripes.append(kit.box("t sock heel", (0.14, 0.172, 0.113), (X + 0.69, 2.15, top + 0.057), M["sock_r"], bevel=0.04))
    stripes.append(kit.box("t sock leg", (0.13, 0.17, 0.3), (X + 0.69, 2.15, top + 0.25), M["sock_w"], bevel=0.04))
    stripes.append(kit.box("t sock cuff", (0.136, 0.176, 0.07), (X + 0.69, 2.15, top + 0.43), M["sock_c"], bevel=0.025))
    ctx["rack"] = rk + stripes
    # the last taped box in the empty hall
    bx = []
    bx.append(kit.box("t tbox", (0.62, 0.52, 0.5), (X + 0.7, 1.5, 0.55 + 0.25), M["card"], bevel=0.015))
    bx.append(kit.box("t tape top", (0.07, 0.53, 0.012), (X + 0.7, 1.5, 0.55 + 0.505), M["tape"]))
    bx.append(kit.box("t tape front", (0.07, 0.01, 0.5), (X + 0.7, 1.5 - 0.265, 0.55 + 0.25), M["tape"]))
    ctx["tbox"] = bx
    # Jo's room behind the window, warm
    kit.plane("t room floor", (3.2, 3.3), (X - 1.8, 1.9, 0.0), M["wood"])
    kit.box("t room back", (3.4, 0.1, 2.6), (X - 1.8, 3.55, 1.3), M["roomwall"])
    kit.box("t room wall L", (0.1, 3.3, 2.6), (X - 3.45, 1.9, 1.3), M["roomwall"])
    kit.box("t room wall R", (0.1, 3.3, 2.6), (X - 0.1, 1.9, 1.3), M["roomwall"])
    kit.box("t room ceil", (3.5, 3.3, 0.1), (X - 1.8, 1.9, 2.65), M["roomwall"])
    kit.cyl("t room bulb", 0.08, 0.09, (X - 1.5, 1.8, 2.56), M["emit_roombulb"])
    kit.light("room", "POINT", (X - 1.5, 1.7, 2.3), 260, "#ffd29a", size=0.25)
    kit.light("room face", "AREA", (X - 1.5, -0.9, 1.9), 110, "#ffe3bd", size=1.0, shadow=False)
    kit.aim(bpy.data.objects["room face"], (X - 1.5, 0.9, 1.6))
    kit.box("t shelf", (1.4, 0.3, 0.05), (X - 2.3, 3.38, 1.5), M["table"])
    kit.cyl("t floorlamp", 0.03, 1.5, (X - 3.0, 3.0, 0.75), M["pole"])
    kit.cyl("t floorlamp shade", 0.18, 0.28, (X - 3.0, 3.0, 1.6), M["emit_roombulb"])
    # across the street: a few dim low roofs, so the dusk wide has a skyline
    for i, (dx, w, h) in enumerate(((-8, 6, 4.2), (-1, 7, 5.0), (7, 6, 3.8))):
        kit.box(f"t far{i}", (w, 5, h), (X + dx, -17, h / 2), kit.plastic("#2a303c", 0.9, name="far houses"))
    kit.light("h fill", "AREA", (X + 0.6, -4.2, 3.0), 420, "#c9d6ee", size=4.0, shadow=False)
    kit.aim(bpy.data.objects["h fill"], (X + 0.4, 0.0, 1.5))
    # the cupboard: a carcass 1.2 m wide on a kitchen wall, two doors open, one spoon at the very back
    C = CX
    kit.box("c wall", (5, 0.1, 3.2), (C, 0.75, 1.6), M["kwall"])
    kit.box("c floor", (5, 3, 0.05), (C, -1.0, 0.0), M["wood"])
    kit.box("c back", (1.2, 0.02, 1.05), (C, 0.68, 1.55), M["cupin"])
    for sx in (-1, 1):
        kit.box(f"c side{sx}", (0.03, 0.4, 1.05), (C + sx * 0.615, 0.48, 1.55), M["cupout"])
    kit.box("c top", (1.26, 0.4, 0.03), (C, 0.48, 2.085), M["cupout"])
    kit.box("c bottom", (1.2, 0.38, 0.03), (C, 0.49, 1.035), M["cupin"])
    for j, z in enumerate((1.4, 1.75)):
        kit.box(f"c shelf{j}", (1.2, 0.36, 0.025), (C, 0.5, z), M["cupin"])
    for sx in (-1, 1):
        pv = kit.empty(f"c door pivot{sx}", (C + sx * 0.6, 0.29, 1.55))
        kit.box(f"c door leaf{sx}", (0.6, 0.025, 1.0), (-sx * 0.3, 0, 0), M["cupout"], pv, bevel=0.008)
        pv.rotation_euler = (0, 0, math.radians(-sx * 108))
    sz = 1.4 + 0.0125    # the middle shelf's top
    sa = math.radians(-14)
    kit.box("c spoon handle", (0.36, 0.034, 0.012), (C + 0.17, 0.46, sz + 0.006), M["spoon"], rot=(0, 0, sa), bevel=0.004)
    bowl = kit.sphere("c spoon bowl", 0.075, (C - 0.07, 0.4, sz + 0.012), M["spoon"], seg=14)
    bowl.scale = (1.5, 1.0, 0.22)
    bowl.rotation_euler = (0, 0, sa)
    kit.light("cup", "AREA", (C + 0.1, -1.8, 2.0), 55, "#fff1dc", size=2.5, shadow=False)
    kit.aim(bpy.data.objects["cup"], (C, 0.4, 1.4))
    kit.light("cup in", "AREA", (C, 0.2, 1.7), 8, "#fff1dc", size=0.9, shadow=False)
    kit.aim(bpy.data.objects["cup in"], (C, 0.6, 1.1))


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
    """A box hugged to the chest: one per (carrier, style), parented to whoever carries it in animate()."""
    ctx["carry"] = {}
    for who in ("me", "jo"):
        for st in ("round", "jagged", "small"):
            e = kit.empty(f"carry {who} {st}", (0, 0, -30))
            if st == "small":
                kit.box(f"carry body {who} small", (0.95, 0.85, 0.7), (0, 0, 0), M["card"], e, bevel=0.03)
                uvplane(kit, f"carry dec {who} small", (0.9, 0.62), (0, -0.428, 0), M["round1"], e,
                        rot=(math.pi / 2, 0, 0))
            else:
                kit.box(f"carry body {who} {st}", (1.5, 1.35, 1.1), (0, 0, 0), M["card"], e, bevel=0.03)
                uvplane(kit, f"carry dec {who} {st}", (1.42, 1.0), (0, -0.678, 0), M[f"{st}0"], e,
                        rot=(math.pi / 2, 0, 0))
            _show(e, False)
            ctx["carry"][(who, st)] = e
    # one small box, sitting on the floor of seven at the end (a lone round-scribbled box)
    sm = kit.empty("small box", (0, 0, -30))
    kit.box("small body", (0.36, 0.3, 0.26), (0, 0, 0.13), M["card"], sm, bevel=0.01)
    uvplane(kit, "small dec", (0.34, 0.24), (0, -0.152, 0.13), M["round1"], sm, rot=(math.pi / 2, 0, 0))
    ctx["small"] = sm
    # my phone's torch and glow
    kit.light("torch", "SPOT", (0, 0, -30), 2500, "#f4f8ff", size=0.04, spot=48, blend=0.6)
    kit.light("phone", "POINT", (0, 0, -30), 14, "#dff0ff", size=0.05, shadow=False)
    # a phone prop for the call: a small dark slab with a lit face, hung from my head (placed in animate)
    ph = kit.empty("phone prop", (0, 0, -30))
    kit.box("phone body", (0.3, 0.1, 0.55), (0, 0, 0), M["dark"], ph, bevel=0.02)
    kit.box("phone screen", (0.24, 0.02, 0.45), (0, -0.055, 0), M["emit_phone"], ph)
    ctx["phoneprop"] = ph


def dress(kit, ctx, M):
    """CC0 props (builder, 2026-11-03): the corridor, the yard, the hall, the cupboard kitchen, my kitchen and Jo's
    street. Nothing with lettering. Kept clear of unit seven's interior and of every camera path."""
    steel = "#aab3b8"
    # the corridor: a steel-grey shelf unit, a stool, a chair and a bin along the shut side's wall, far end
    kit.prop("bookshelf", (-0.88, 14.4, 0), rot=90, height=1.9, tint=steel)
    kit.prop("bookshelf", (-0.88, 15.4, 0), rot=90, height=1.9, tint=steel)
    kit.prop("trashcan_cylindric", (-0.86, 12.7, 0), height=0.6, tint="#7d8a93")
    kit.prop("chair_1", (-0.82, 11.0, 0), rot=80, height=0.9, tint="#b9a27a")
    kit.prop("stool", (-0.86, 1.9, 0), height=0.7, tint="#b9a27a")
    kit.prop("houseplant_1", (-0.86, 1.9, 0.7), height=0.36)
    # the yard: a fence line, two trees, a rock
    for i in range(7):
        kit.prop("nat_fence_simple", (-9.0 + i * 3.0, -13.0, 0), rot=0, tint="#c9c0b0")
    kit.prop("sub_tree_small", (-7.0, -11.5, 0), height=3.2)
    kit.prop("sub_tree_large", (8.5, -11.8, 0), height=4.2)
    kit.prop("rock_1", (4.5, -5.5, 0), fit=0.9, tint="#a0a098")
    kit.prop("bush_2", (-6.5, -3.0, 0), fit=1.5)
    # the friend's hall: a little table, a plant, a floor lamp, a rug
    X = HX
    kit.prop("carpet_1", (X + 0.7, 1.15, 0.555), rot=90, scale=0.8)
    kit.prop("nightstand_1", (X + 0.43, 0.8, 0.55), rot=-90, tint="#d9b98a")
    kit.prop("houseplant_1", (X + 0.43, 0.8, 0.96), scale=0.9)
    kit.prop("light_floor1", (X + 1.05, 0.55, 0.55), height=0.9)
    # the high kitchen cupboard's kitchen
    C = CX
    kit.prop("kitchen_cabinet1", (C - 0.3, 0.43, 0), rot=180, tint="#d9cdb8")
    kit.prop("kitchen_cabinet1", (C + 0.25, 0.43, 0), rot=180, tint="#d9cdb8")
    kit.prop("kitchen_fridge", (C - 1.4, 0.4, 0), rot=180)
    kit.prop("kitchen_sink", (C + 0.9, 0.43, 0), rot=180)
    kit.prop("kitchen_oven", (C + 1.5, 0.43, 0), rot=180)
    # my kitchen: units along the back wall, three chairs round the table
    KX_, KY_ = 60.0, 0.0
    for nm, dx in (("kitchen_fridge", -2.0), ("kitchen_cabinet1", -1.45), ("kitchen_sink", -0.95),
                   ("kitchen_cabinet1", -0.44), ("kitchen_oven", 0.1)):
        kit.prop(nm, (KX_ + dx, KY_ + 2.17, 0), rot=180)
    kit.prop("chair_1", (KX_ - 0.2, KY_ + 1.0, 0), rot=180, height=0.9, tint="#c9a878")
    kit.prop("chair_1", (KX_ - 1.15, KY_ + 0.3, 0), rot=90, height=0.9, tint="#c9a878")
    kit.prop("chair_1", (KX_ + 0.8, KY_ + 0.3, 0), rot=-90, height=0.9, tint="#c9a878")
    # Jo's street: houses across it, a tree and a planter on the pavement
    for dx, nm, hh in ((-8.5, "sub_building_type_a", 4.2), (-1.0, "sub_building_type_c", 5.0),
                       (7.0, "sub_building_type_k", 5.2)):
        kit.prop(nm, (X + dx, -16.5, 0), rot=0, height=hh, tint="#8e96a8")
    kit.prop("sub_tree_small", (X + 4.6, -2.0, 0), height=3.0)
    kit.prop("sub_planter", (X - 4.4, -1.3, 0), fit=1.4)


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
    build_dlamps(kit, ctx, M)
    build_town(kit, ctx, M)
    dress(kit, ctx, M)
    # the number-plate planes need their images the right way up; that is checked in the stills
    ctx["wd"] = wd
    return ctx


# ------------------------------------------------------------------------------------------ the tall grey one


def build_deep(kit, ctx):
    """The tall grey one (rebuilt for "Hold Still"): a person-shape 1.6 times our height, stooped so its bowed head
    sits level with the battens, arms hanging past its knees, long flat hands. Built from boxes in the `deep` rig's
    space (rig units, so every size below is metres over RIG_S). The rig's own body is hidden; only this shows."""
    root = bpy.data.objects.get("deep")
    if root is None or ctx.get("deep_done"):
        return
    ctx["deep_done"] = True
    grey = kit.plastic("#8e9196", 0.92, name="tall grey", spec=0.05)
    pale = kit.plastic("#9fa2a8", 0.92, name="tall grey face", spec=0.05)
    dark = kit.plastic("#08090b", 0.95, name="tall grey eye", spec=0.0)
    for ob in root.children_recursive:      # the rig's body: not shown, the parts below stand in for it
        ob.hide_render = True
    ctx["deep_rig"] = list(root.children_recursive)
    parts = []

    def u(v):
        return v / RIG_S

    def J(name, loc, parent, rot=(0, 0, 0)):
        e = kit.empty(f"tall {name}", tuple(u(c) for c in loc), parent, rot)
        parts.append(e)
        return e

    def B(name, size, loc, mat, parent, rot=(0, 0, 0), bevel=0.02):
        ob = kit.box(f"tall {name}", tuple(u(c) for c in size), tuple(u(c) for c in loc), mat, parent, rot=rot,
                     bevel=u(bevel))
        parts.append(ob)
        return ob

    # legs: long and thin, a flat foot each
    for sx in (-1, 1):
        B(f"foot{sx}", (0.17, 0.42, 0.07), (sx * 0.17, -0.07, 0.035), grey, root)
        B(f"shin{sx}", (0.15, 0.15, 0.66), (sx * 0.17, 0.0, 0.40), grey, root)
        B(f"thigh{sx}", (0.18, 0.18, 0.66), (sx * 0.17, 0.0, 0.95), grey, root)
    B("pelvis", (0.50, 0.26, 0.24), (0, 0.0, 1.33), grey, root)
    # the spine leans forward over the hips (positive x turn tips the top toward -y, the way it faces)
    lean = 0.30
    sp = J("spine", (0, 0.0, 1.42), root, (lean, 0, 0))
    B("waist", (0.34, 0.22, 0.36), (0, 0, 0.20), grey, sp, bevel=0.04)
    B("chest", (0.62, 0.30, 0.52), (0, 0, 0.62), grey, sp, bevel=0.05)
    B("shoulders", (0.74, 0.22, 0.14), (0, 0.06, 0.84), grey, sp, bevel=0.05)
    B("neck", (0.11, 0.11, 0.22), (0, -0.04, 0.96), grey, sp, bevel=0.03)
    # the head: bowed hard, so the crown and the brow lead and the face looks at the floor, lit from above
    hd = J("head", (0, -0.06, 1.00), sp, (0.62, 0, 0))
    B("skull", (0.25, 0.27, 0.36), (0, 0.02, 0.17), grey, hd, bevel=0.06)
    B("brow", (0.27, 0.06, 0.05), (0, -0.135, 0.22), grey, hd, bevel=0.015)
    B("face", (0.20, 0.02, 0.26), (0, -0.125, 0.15), pale, hd, bevel=0.008)
    for sx in (-1, 1):                       # two small dark eyes set low, no mouth, no shine
        B(f"eye{sx}", (0.04, 0.012, 0.035), (sx * 0.05, -0.139, 0.10), dark, hd, bevel=0.004)
    # arms: they hang from the shoulders straight down in the world, past the knees, hands near the shins
    for sx in (-1, 1):
        sh = J(f"shoulder{sx}", (sx * 0.43, -0.22, 2.12), root, (-0.10, 0, 0))
        B(f"uarm{sx}", (0.13, 0.13, 0.76), (0, 0, -0.38), grey, sh, bevel=0.03)
        el = J(f"elbow{sx}", (0, 0, -0.76), sh, (-0.06, 0, 0))
        B(f"farm{sx}", (0.12, 0.12, 0.74), (0, 0, -0.37), grey, el, bevel=0.03)
        wr = J(f"wrist{sx}", (0, 0, -0.74), el, (-0.04, 0, 0))
        B(f"palm{sx}", (0.045, 0.15, 0.20), (0, 0, -0.10), grey, wr, bevel=0.012)
        for k, fy in enumerate((-0.054, -0.018, 0.018, 0.054)):
            B(f"finger{sx}{k}", (0.03, 0.026, 0.24 - abs(fy)), (0, fy, -0.30 + abs(fy) * 0.5), grey, wr, bevel=0.008)
    ctx["deep_parts"] = parts
    ctx["deep_profile"] = []
    ctx["deep_head_parts"] = []
    kit.light("deep rim", "SPOT", (3.0, 2.0, 1.4), 420, "#7fa8ff", size=0.25, spot=60, blend=0.7, shadow=False)
    kit.aim(bpy.data.objects["deep rim"], (1.3, 2.5, 1.2))



# ------------------------------------------------------------------------------------------ animate

TIMES = {
    "open": ("#1d2740", 0.8, 0.0, 1.0, 0.7, 0.7, 1.0, 0.45),   # sky colour, sky strength, sun gain, sodium, yard fill, mem fill, batten multiplier, exposure
    "dusk": ("#1d2740", 0.8, 0.0, 1.0, 0.7, 0.0, 1.0, 0.0),
    "mem": ("#bcd0ee", 1.6, 0.5, 0.0, 1.0, 1.0, 1.0, 0.1),
    "eve": ("#4d5f8c", 1.7, 0.0, 1.0, 1.3, 0.0, 1.0, 0.7),       # a brighter dusk for the street and the yard at the start
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
    dr_ = bpy.data.objects.get("deep")
    if dr_ is not None:     # parts built here don't inherit the root's hidden state: copy it, every frame
        for ob in ctx.get("deep_parts", []):
            ob.hide_render = dr_.hide_render
        for ob in ctx.get("deep_rig", []):      # the rig's own body stays hidden
            ob.hide_render = True
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
    shot0 = next((s_ for s_ in tl["shots"] if s_["start"] <= t < s_["end"]), None)
    for k, vo in ctx["voids"].items():
        dc = [c for c in _cues(tl, "door") if c.get("unit") == k and c.get("open", 0) > 0.5 and c["t"] <= t]
        vo.hide_render = not (k in (10, 11) and shot0 is not None and dc and abs(shot0["start"] - dc[-1]["t"]) < 0.3)
    # unit seven's stacks
    sc = _last(_cues(tl, "stacks"), t)
    for ob in ctx.get("dent", []):
        ob.hide_render = not (sc and sc.get("at") == "L46")
    nl = sc["left"] if sc else STACK_N
    nr = sc["right"] if sc else STACK_N
    scr = _last(_cues(tl, "scribble"), t)    # {"left": "round"}: the hook's boxes show round loops to the corridor
    for side, n in (("left", nl), ("right", nr)):
        for ob, dec, idx in ctx["boxes"][side]:
            st, vv = ctx["decvar"][dec.name]
            if side == "left" and scr and scr.get("left") == "round":
                st = "round"
            dec.data.materials.clear()
            dec.data.materials.append(M[f"{st}{vv}"])
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
    set_emit(M["emit_win"], 1.0 if ks == "night" else 3.5)
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
    for e in ctx["carry"].values():
        _show(e, False)
    carriers = {}
    for c_ in _cues(tl, "carry"):
        if c_["t"] <= t + 1e-9:
            carriers[c_["who"]] = c_
    sm = ctx["small"]
    smc = _last(_cues(tl, "small"), t)
    _show(sm, True)          # never toggled (a toggled hide_render drew the box black in some shards)
    sm.location = tuple(smc["pos"]) if smc and smc.get("on") else (0, 0, -30)
    me = bpy.data.objects.get("me")
    jo = bpy.data.objects.get("jo")
    bpy.context.view_layer.update()
    for who_, carry in carriers.items():
        who = bpy.data.objects.get(who_)
        tor = bpy.data.objects.get(f"{who_}.torso")
        if not carry.get("on") or who is None or tor is None or who.hide_render:
            continue
        e = ctx["carry"][(who_, carry["style"])]
        e.parent = tor
        e.location = (0, -1.15, 1.0)
        e.rotation_euler = (0, 0, 0)
        _show(e, True)
    # my battery lamp: on the floor of seven, then (from the lift) gone, then standing on the small box I carry out
    lm = _last(_cues(tl, "lampbox"), t)
    base = ctx["lamp_pos"]
    mode = lm["mode"] if lm else "floor"
    top_ = None
    if mode == "box":
        cm = carriers.get("me")
        if cm and cm.get("on") and me is not None and not me.hide_render:
            e_ = ctx["carry"][("me", cm["style"])]
            top_ = e_.matrix_world @ Vector((0.0, 0.0, 0.35))
    if mode == "floor":
        pos_ = base
    elif top_ is not None:
        pos_ = (top_.x, top_.y, top_.z + 0.08)
    else:
        pos_ = (0, 0, -30)
    for ob, dz in zip(ctx["lamp_objs"], (0.0, 0.02, 0.09)):
        ob.location = (pos_[0], pos_[1], pos_[2] + dz)
    L_ = kit.LIGHTS["lamp"]["obj"]
    L_.location = (pos_[0], pos_[1], pos_[2] + 0.12)
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
    _plates(kit, story, tl, t, ctx)
    # the town's door lamps: a 0.6 s ramp up, a 1.0 s ramp down, from the dlamp cues
    dcs = _cues(tl, "dlamp")
    scn = (_last(_cues(tl, "scene"), t) or {"set": "none"})["set"]
    S = SCENES[scn]
    for n, d in ctx["dl"].items():
        v = S[4] if n == "H" else _ramp([c for c in dcs if c.get("unit") == n], t, "on", 0.0)
        set_emit(d["mat"], 0.05 + 2.6 * v)
        if d["light"]:
            over[d["light"]] = v
    hob, hm_ = ctx["halo7"]
    d7 = [c for c in dcs if c.get("unit") == 7]
    hv = 0.0
    if d7 and d7[-1]["t"] > 100 and t > d7[-1]["t"] - 0.7:
        v7 = _ramp(d7, t, "on", 0.0)
        hv = _ss(min(1.0, (t - (d7[-1]["t"] - 0.7)) / 0.6)) * v7
    set_emit(hm_, 10.0 * hv)
    hob.hide_render = hv < 0.01
    over["h fill"], over["hall"], over["room"], over["cup"] = S[0], S[1], S[2], S[3]
    over["hall back"] = S[1]
    over["room face"] = S[2]
    over["cup in"] = S[3]
    set_emit(M["emit_hbulb"], 6.0 * S[1])
    set_emit(M["emit_roombulb"], 5.0 * max(S[2], 0.3))
    for ob in ctx["rack"]:
        ob.hide_render = not S[5]
    for ob in ctx["tbox"]:
        ob.hide_render = not S[6]
    ctx["hdoor"].rotation_euler = (0, 0, math.radians(90 if S[7] else 0))
    # the Deep One: the tube behind its head, and its edge light
    rc = _last(_cues(tl, "rim"), t)
    over["deep rim"] = float(rc["on"]) if rc else 0.0
    if rc and rc.get("on"):
        rl = kit.LIGHTS["deep rim"]["obj"]
        rl.location = tuple(rc["pos"])
        kit.aim(rl, tuple(rc["aim"]))
    pc2 = _last(_cues(tl, "profile"), t)
    dr0 = bpy.data.objects.get("deep")
    for ob in ctx.get("deep_profile", []):
        ob.hide_render = not (pc2 and pc2.get("on")) or (dr0 is not None and dr0.hide_render)
    hc = _last(_cues(tl, "headtube"), t)
    ht = bool(hc["on"]) if hc else True
    for ob in ctx.get("deep_head_parts", []):
        dr = bpy.data.objects.get("deep")
        ob.hide_render = (dr is not None and dr.hide_render) or not ht
    return over


def _plates(kit, story, tl, t, ctx):
    """A door plate is shown whole or not at all: hide any plate that the shot's frame would crop (or sees edge-on)."""
    from bpy_extras.object_utils import world_to_camera_view
    from blocky import bl_story
    shot = next((s for s in tl["shots"] if s["start"] <= t < s["end"]), tl["shots"][-1])
    spec = next(s for s in story["shots"] if s["id"] == shot["id"])
    loc, tgt, lens, roll = bl_story.cam_at(spec, shot, t, {}, tl)
    kit.place_camera(loc, tgt, lens, roll)
    sc = bpy.context.scene
    bpy.context.view_layer.update()
    for root, f, obs in ctx.get("plates", []):
        if root.hide_render and any(o.hide_render for o in obs):
            pass
        cx, cy, cz = root.location.x + f * 0.05, root.location.y + 0.62, root.location.z + 1.95
        pts = [(cx, cy + dy, cz + dz) for dy in (-0.17, 0.17) for dz in (-0.11, 0.11)]
        from mathutils import Vector
        uv = [world_to_camera_view(sc, sc.camera, Vector(p)) for p in pts]
        inside = [0.03 < v.x < 0.97 and 0.03 < v.y < 0.97 and v.z > 0 for v in uv]
        width = max(v.x for v in uv) - min(v.x for v in uv)
        ok = all(inside) or not any(inside)
        if width < 0.012 and any(inside):
            ok = False                   # a speck is a smear, not a number
        if root.hide_render:
            continue
        if spec.get("at") == "L63.3":   # side A reads 21..26, the block has twelve units, and this shot sees a plate big
            ok = False
        for o in obs:
            o.hide_render = not ok


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
        k1.location = (x + 0.085, y - 0.01, z + 0.003)    # the second key on its own beside the ring
        k1.rotation_euler = (0, 0, math.radians(80))
        _show(k1, True)
    else:
        for e in (ring, k0, k1):
            _show(e, False)
