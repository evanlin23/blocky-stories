"""ep71 "Two windows": a bright roadside drive-thru on a golden Friday evening. No text anywhere: the only characters
are numerals (menu board 1 to 9, the speaker screen and the tickets, 41 then 42), drawn here with PIL.

Metres. Zone A (the drive-thru) is at the origin:
  the lane runs along +x at y = 2.65 (cars face +x, so the driver, on the left, is on the +y side nearest the wall);
  the building's front wall is the plane y = 4.6, x -9 .. 6.4, with the ONE window (hatch 1) at x = 0;
  "wall B" (x 6.8 .. 13.6, a cue can hide it) carries hatch 2, the second window, at x = 10.1;
  the speaker post is at x = -12, y = 3.9; the menu board at x = -14.8; the bun road sign at x = -22;
  the back lane (cars face -x) is y = 10.6 and the brick back wall is y = 15.5, Mr. Dale's eight trucks and then
  our three copies wait nose to tail at y = 12.9 (x = 15 down to -26).
Zone D (300, 0): Mr. Dale's front door. Zone R (600, 0): the open road.
Cars are groups moved by "car" cues; Cal and me (and the lime car's driver) ride on matching acting keys.
Cues read here: car {id,pos,yaw}, vis {id,on}, server {lv}, scr {n}, h2 {v}, dim {v}, bagcar {on}.
"""

from __future__ import annotations

import math
import tempfile
from pathlib import Path

import bpy

from blocky import rig

ROOT = Path(__file__).resolve().parents[2]
FONT = ROOT / "blocky" / "fonts" / "SchibstedGrotesk-Black.ttf"
LANE_Y = 2.65
WALL_Y = 4.6
H1X, H2X = 0.0, 10.1
SILL_Z = 1.1


# ------------------------------------------------------------------------------------------------ helpers
def _cues(tl, name):
    return sorted((c for c in tl.get("cues", []) if c["name"] == name), key=lambda c: c["t"])


def _last(cs, t):
    cs = [c for c in cs if c["t"] <= t + 1e-9]
    return cs[-1] if cs else None


def _ss(x):
    x = min(1.0, max(0.0, x))
    return x * x * (3 - 2 * x)


def _eased(cs, key, t, default):
    level = prev = default
    for c in cs:
        if c["t"] > t + 1e-9 or key not in c:
            continue
        prev, level = level, c[key]
        d = float(c.get("dur", 0.0))
        if d > 0 and t < c["t"] + d:
            level = prev + (level - prev) * _ss((t - c["t"]) / d)
    return level


def _lin_pos(cs, t):
    """Linear interpolation of pos and yaw between consecutive cues (a car's path, like acting.py's keys)."""
    if not cs:
        return None
    if t <= cs[0]["t"]:
        return cs[0]["pos"], cs[0].get("yaw", 0.0)
    for a, b in zip(cs, cs[1:]):
        if t < b["t"]:
            if b.get("snap") or b.get("hide"):
                return a["pos"], a.get("yaw", 0.0)
            u = (t - a["t"]) / max(1e-6, b["t"] - a["t"])
            p = [x + (y - x) * u for x, y in zip(a["pos"], b["pos"])]
            return p, a.get("yaw", 0.0) + (b.get("yaw", 0.0) - a.get("yaw", 0.0)) * u
    return cs[-1]["pos"], cs[-1].get("yaw", 0.0)


def _show(objs, on):
    for o in objs:
        for oo in [o] + list(o.children_recursive):
            oo.hide_render = not on


def _lin(c):
    return tuple(((v + 0.055) / 1.055) ** 2.4 if v > 0.04045 else v / 12.92 for v in c)


# ------------------------------------------------------------------------------------------------ drawn pictures
def _font(size):
    from PIL import ImageFont
    return ImageFont.truetype(str(FONT), size)


def _num(d, xy, n, size, fill, anchor="mm"):
    d.text(xy, str(n), font=_font(size), fill=fill, anchor=anchor)


def draw_menu(path):
    from PIL import Image, ImageDraw
    W, H = 1536, 1056
    im = Image.new("RGB", (W, H), "#fff1d6")
    d = ImageDraw.Draw(im)
    cw, ch = W // 3, H // 3
    for i in range(9):
        cx0, cy0 = (i % 3) * cw, (i // 3) * ch
        d.rounded_rectangle((cx0 + 10, cy0 + 10, cx0 + cw - 10, cy0 + ch - 10), 28, outline="#e9c08a", width=6)
        n = i + 1
        _num(d, (cx0 + 60, cy0 + 62), n, 84, "#d8433a")
        cx, cy = cx0 + cw // 2 + 30, cy0 + ch // 2 + 14
        if n == 1:       # bun
            d.pieslice((cx - 90, cy - 90, cx + 90, cy + 70), 180, 360, fill="#e7a25a")
            d.rectangle((cx - 95, cy - 12, cx + 95, cy + 8), fill="#7fc34a")
            d.rounded_rectangle((cx - 90, cy + 8, cx + 90, cy + 38), 12, fill="#7a4a2a")
            d.rounded_rectangle((cx - 90, cy + 38, cx + 90, cy + 66), 14, fill="#e7a25a")
        elif n == 2:     # fries cup
            for k in range(-3, 4):
                d.rounded_rectangle((cx + k * 22 - 9, cy - 85 + abs(k) * 6, cx + k * 22 + 9, cy), 5, fill="#f4c430")
            d.polygon([(cx - 70, cy - 20), (cx + 70, cy - 20), (cx + 52, cy + 80), (cx - 52, cy + 80)], fill="#d8433a")
        elif n == 3:     # drink
            d.polygon([(cx - 55, cy - 50), (cx + 55, cy - 50), (cx + 42, cy + 80), (cx - 42, cy + 80)], fill="#5aa9e6")
            d.rectangle((cx - 62, cy - 62, cx + 62, cy - 48), fill="#ffffff")
            d.rectangle((cx + 8, cy - 110, cx + 22, cy - 60), fill="#d8433a")
        elif n == 4:     # stacked bun, tall
            d.pieslice((cx - 80, cy - 112, cx + 80, cy - 4), 180, 360, fill="#e7a25a")
            for k, c in enumerate(("#7a4a2a", "#f4c430", "#7a4a2a", "#7fc34a")):
                d.rounded_rectangle((cx - 82, cy - 6 + k * 24 - 4, cx + 82, cy + 16 + k * 24 - 4), 10, fill=c)
            d.rounded_rectangle((cx - 80, cy + 92, cx + 80, cy + 118), 12, fill="#e7a25a")
        elif n == 5:     # a round pickle slice
            d.ellipse((cx - 88, cy - 88, cx + 88, cy + 88), fill="#5f9f35")
            d.ellipse((cx - 66, cy - 66, cx + 66, cy + 66), fill="#a9d36a")
            for k in range(8):
                a = k * math.pi / 4
                d.ellipse((cx + 38 * math.cos(a) - 7, cy + 38 * math.sin(a) - 7, cx + 38 * math.cos(a) + 7, cy + 38 * math.sin(a) + 7), fill="#e6f0b0")
            d.ellipse((cx - 14, cy - 14, cx + 14, cy + 14), fill="#e6f0b0")
        elif n == 6:     # cone
            d.polygon([(cx - 52, cy - 10), (cx + 52, cy - 10), (cx, cy + 100)], fill="#d9a05a")
            d.ellipse((cx - 62, cy - 85, cx + 62, cy + 5), fill="#f7c6d9")
        elif n == 7:     # bowl of greens
            d.pieslice((cx - 95, cy - 70, cx + 95, cy + 80), 0, 180, fill="#5aa9e6")
            for k in range(-3, 4):
                d.ellipse((cx + k * 24 - 20, cy - 62 + abs(k) * 5, cx + k * 24 + 20, cy - 12 + abs(k) * 5), fill="#7fc34a")
        elif n == 8:     # shake
            d.polygon([(cx - 50, cy - 40), (cx + 50, cy - 40), (cx + 38, cy + 82), (cx - 38, cy + 82)], fill="#f0b6cf")
            d.ellipse((cx - 58, cy - 82, cx + 58, cy - 20), fill="#ffffff")
            d.ellipse((cx - 12, cy - 100, cx + 12, cy - 76), fill="#d8433a")
        else:            # soup bowl, steam
            d.pieslice((cx - 95, cy - 70, cx + 95, cy + 80), 0, 180, fill="#e9743a")
            d.ellipse((cx - 95, cy - 90, cx + 95, cy - 50), fill="#f5a04a")
            for k in (-40, 0, 40):
                d.line((cx + k, cy - 100, cx + k + 14, cy - 125, cx + k - 6, cy - 150), fill="#bbb", width=8)
    im.save(path)


def draw_digits(path, n, bg="#15110f", fg="#ffb38a", size=300, w=512, h=384):
    from PIL import Image, ImageDraw
    im = Image.new("RGB", (w, h), bg)
    _num(ImageDraw.Draw(im), (w // 2, h // 2 + 6), n, size, fg)
    im.save(path)


def draw_sign(path):
    from PIL import Image, ImageDraw
    im = Image.new("RGB", (512, 512), "#2f9e6a")
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((16, 16, 496, 496), 40, outline="#ffffff", width=10)
    cx, cy = 256, 210
    d.pieslice((cx - 120, cy - 110, cx + 120, cy + 70), 180, 360, fill="#e7a25a")
    d.rectangle((cx - 126, cy - 20, cx + 126, cy), fill="#7fc34a")
    d.rounded_rectangle((cx - 120, cy, cx + 120, cy + 34), 14, fill="#7a4a2a")
    d.rounded_rectangle((cx - 120, cy + 34, cx + 120, cy + 70), 16, fill="#e7a25a")
    d.polygon([(110, 400), (330, 400), (330, 360), (410, 430), (330, 500), (330, 460), (110, 460)], fill="#ffffff")
    im.save(path)


def img_mat(kit, name, path, emit=0.0, rough=0.7):
    m = kit._new(name)
    nt = m.node_tree
    b = nt.nodes["Principled BSDF"]
    t = nt.nodes.new("ShaderNodeTexImage")
    t.image = bpy.data.images.load(str(path))
    t.image.colorspace_settings.name = "sRGB"
    uv = nt.nodes.new("ShaderNodeUVMap")
    nt.links.new(uv.outputs["UV"], t.inputs["Vector"])
    nt.links.new(t.outputs["Color"], b.inputs["Base Color"])
    b.inputs["Roughness"].default_value = rough
    if emit:
        k = "Emission Color" if "Emission Color" in b.inputs else "Emission"
        nt.links.new(t.outputs["Color"], b.inputs[k])
        b.inputs["Emission Strength"].default_value = emit
    kit._fogged(m, b.outputs[0])
    return m


def quad(kit, name, w, h, loc, rot, mat, parent=None):
    x, y = w / 2, h / 2
    ob = kit.mesh_obj(name, [(-x, -y, 0), (x, -y, 0), (x, y, 0), (-x, y, 0)], [(0, 1, 2, 3)], mat, parent, loc, rot)
    uv = ob.data.uv_layers.new(name="UVMap")
    for li, c in zip(ob.data.polygons[0].loop_indices, [(0, 0), (1, 0), (1, 1), (0, 1)]):
        uv.data[li].uv = c
    return ob


FACE_NEG_Y = (math.pi / 2, 0, 0)          # a quad facing -y (toward the lane / the camera in the lot)
FACE_NEG_X = (math.pi / 2, 0, -math.pi / 2)   # facing -x


# ------------------------------------------------------------------------------------------------ cars
def build_car(kit, M, name, color, kind="open", cracked=False, tix=False, bag=False, glow=1.0):
    """Local frame: heading +x, left (the driver's side) is +y. Seat tops at z = 0.5."""
    root = kit.empty(name, (0, 0, -60))
    body = kit.plastic(color, 0.35, f"car {color}")
    dark = kit.plastic("#2a2d33", 0.6, "car dark")
    trim = kit.plastic("#f2f0ea", 0.4, "car trim")
    seat = kit.plastic("#3b3f4a", 0.7, "car seat")
    parts = {"root": root}
    B = lambda n, s, l, m=body, bv=0.06, rot=(0, 0, 0): kit.box(f"{name}.{n}", s, l, m, root, rot, bevel=bv)
    if kind == "van":
        B("box", (4.2, 1.9, 1.55), (0, 0, 1.2), body, 0.1)
        B("cab", (0.2, 1.7, 0.6), (2.12, 0, 1.5), dark, 0.03)
        B("under", (4.2, 1.9, 0.3), (0, 0, 0.45), dark, 0.05)
        # cardboard taped over the side window (right side, -y)
        card = kit.plastic("#b98a55", 0.9, "cardboard")
        B("card", (1.2, 0.03, 0.7), (0.5, -0.96, 1.45), card, 0.01)
        for k, dx in enumerate((-0.45, 0.0, 0.45)):
            B(f"tape{k}", (0.07, 0.04, 0.75), (0.5 + dx, -0.975, 1.45), kit.plastic("#d8d0b8", 0.5, "tape"), 0.0)
        B("tapeh", (1.25, 0.04, 0.07), (0.5, -0.975, 1.45), kit.plastic("#d8d0b8", 0.5, "tape"), 0.0)
    else:
        B("floor", (3.7, 1.7, 0.2), (0, 0, 0.4), dark, 0.03)
        for sy in (-1, 1):
            B(f"side{sy}", (3.7, 0.12, 0.72), (0, sy * 0.89, 0.72))
        B("hood", (1.2, 1.9, 0.62), (1.3, 0, 0.66))
        B("trunk", (1.0, 1.9, 0.62), (-1.45, 0, 0.66))
        B("dash", (0.25, 1.7, 0.4), (0.82, 0, 0.82), dark, 0.05)
        B("rail", (0.12, 1.9, 0.12), (-0.62, 0, 1.12), body, 0.03)
        for sy, nm in ((-1, "r"), (1, "l")):
            B(f"seat{nm}", (0.8, 0.7, 0.18), (-0.25, sy * 0.45, 0.42), seat, 0.05)
            B(f"back{nm}", (0.16, 0.7, 0.55), (-0.66, sy * 0.45, 0.72), seat, 0.05)
        wheel_c = body if kind == "truck" else body
        B("stalk", (0.04, 0.04, 0.4), (0.74, 0.0, 1.28), dark, 0.01)
        # the windshield: a thin frame only, so the camera can look through it
        # wheel steering
        kit.cyl(f"{name}.wheelrim", 0.22, 0.04, (0.55, 0.45, 1.0), dark, root, rot=(0, 1.1, 0), n=16)
        if kind == "truck":
            B("cab", (1.3, 1.9, 0.12), (0.0, 0, 1.58))      # cab roof over the front seats
            for sy in (-1, 1):
                B(f"cabpost{sy}", (0.1, 0.1, 0.55), (-0.62, sy * 0.88, 1.32))
            B("bedwall", (1.5, 1.9, 0.05), (-1.4, 0, 0.98), body, 0.02)
            for sy in (-1, 1):
                B(f"bed{sy}", (1.5, 0.08, 0.4), (-1.42, sy * 0.92, 0.95))
    for sx in (-1.2, 1.2):
        for sy in (-1, 1):
            kit.cyl(f"{name}.wheel{sx}{sy}", 0.36, 0.24, (sx, sy * 0.9, 0.36), kit.plastic("#1d1f24", 0.8, "tyre"), root,
                    rot=(math.pi / 2, 0, 0), n=18)
            kit.cyl(f"{name}.hub{sx}{sy}", 0.17, 0.26, (sx, sy * 0.9, 0.36), kit.plastic("#d8dce0", 0.4, "hub"), root,
                    rot=(math.pi / 2, 0, 0), n=12)
    hx = 2.03 if kind == "van" else 1.93
    lens_r = kit.emit("#fff4d0", 6.0 * glow, "headlight r")
    lens_l = kit.emit("#a39a84", 1.5 * glow, "headlight cracked") if cracked else lens_r
    B("hlr", (0.06, 0.34, 0.2), (hx, -0.62, 0.8), lens_r, 0.02)
    B("hll", (0.06, 0.34, 0.2), (hx, 0.62, 0.8), lens_l, 0.02)
    if cracked:
        # a jagged dark line down the dim lens: five short segments joined point to point (a crack, not an X)
        crack = kit.plastic("#030201", 0.9, "crack")
        pts = ((0.62 - 0.06, 0.89), (0.62 + 0.05, 0.85), (0.62 - 0.05, 0.81), (0.62 + 0.06, 0.77), (0.62 - 0.02, 0.72))
        for i, ((y0, z0), (y1, z1)) in enumerate(zip(pts, pts[1:])):
            ln_ = math.hypot(y1 - y0, z1 - z0)
            ang = math.atan2(y1 - y0, z1 - z0)        # tilt of a z-long bar about x: z axis -> (0, -sin, cos)
            B(f"crack{i}", (0.01, 0.016, ln_ + 0.012), (hx + 0.045, (y0 + y1) / 2, (z0 + z1) / 2), crack, 0.0, (-ang, 0, 0))
    plate = kit.plastic("#ffb38a", 0.5, "plate")
    B("plateb", (0.04, 0.5, 0.16), (-hx + 0.0, 0, 0.62), plate, 0.01)
    B("platef", (0.04, 0.5, 0.16), (hx + 0.0, 0, 0.5), plate, 0.01)
    B("tail1", (0.05, 0.3, 0.12), (-hx - 0.0, 0.62, 0.8), kit.emit("#ff5a4a", 1.5, "tail"), 0.01)
    B("tail2", (0.05, 0.3, 0.12), (-hx - 0.0, -0.62, 0.8), kit.emit("#ff5a4a", 1.5, "tail"), 0.01)
    parts["tix"] = []
    if tix:
        # three ticket rows stand on the dash (right corner, middle, left corner), big, so every in-car close-up has
        # the count in frame whichever side the camera is on
        for r, yc in enumerate((-0.58, 0.0, 0.58)):
            B(f"tixrail{r}", (0.06, 0.34, 0.05), (0.86, yc, 1.04), dark, 0.01)
            for i in range(5):
                m = M["tix42"] if i == 4 else M["tix41"]
                yy = yc - 0.14 + 0.07 * i
                q = quad(kit, f"{name}.tix{r}_{i}", 0.12, 0.17, (0.86 - 0.012, yy, 1.16), FACE_NEG_X, m, root)
                q2 = quad(kit, f"{name}.tixf{r}_{i}", 0.12, 0.17, (0.86 + 0.012, yy, 1.16), (math.pi / 2, 0, math.pi / 2), m, root)
                parts["tix"].append(q)
                parts.setdefault("tixf", []).append(q2)
    if tix:
        parts["cup"] = kit.cyl(f"{name}.cup", 0.06, 0.13, (0.78, 0.38, 1.08), kit.plastic("#6fd13a", 0.5, "cup"), root, n=14)
    if bag:
        bg = kit.empty(f"{name}.bag", (0, 0, 0), root)
        kit.box(f"{name}.bagm", (0.4, 0.26, 0.36), (-0.05, -0.43, 0.72), kit.plastic("#c9955a", 0.9, "bag"), bg, bevel=0.02)
        kit.box(f"{name}.bagt", (0.3, 0.02, 0.12), (-0.05, -0.57, 0.8), kit.plastic("#ffffff", 0.6, "bagt"), bg)
        parts["bag"] = bg
    return parts


def build_server(kit, M, ctx):
    """The Server: the window lady's mint uniform on a body too big for the hatch. Its shoulders fill the opening
    jamb to jamb, its head is a tall pale slab with a black hollow for a face: two narrow bright eyes and a wide
    row of small teeth. Levels: 0 only the arm with the bag, 1 face in the hatch, 2 shoulders and face out over the
    sill, 3 leaning out, face to face with Cal. Arms are thick, with long fingers."""
    mint = kit.plastic("#7fe0c4", 0.45, "srv mint")
    peach = kit.plastic("#ffb38a", 0.45, "srv peach")
    skin = kit.plastic("#8d858b", 0.9, "srv skin")
    skin2 = kit.plastic("#c9b4a0", 0.7, "srv hand")
    black = kit.plastic("#030203", 0.9, "srv black")
    teeth = kit.plastic("#f3ead8", 0.6, "srv teeth")
    root = kit.empty("server", (H2X, 4.85, 0.0))
    g = kit.empty("server.g", (0, 0, 1.75), root)       # the shoulder line; moves out and pitches with the level
    kit.box("srv.chest", (1.46, 0.5, 0.62), (0, 0, 0.0), mint, g, bevel=0.07)
    kit.box("srv.stripe", (1.48, 0.52, 0.1), (0, 0, -0.1), peach, g, bevel=0.02)
    kit.box("srv.torso", (1.1, 0.45, 1.6), (0, 0.05, -1.0), mint, g, bevel=0.06)
    ctx["neck"] = kit.box("srv.neck", (0.3, 0.3, 1.0), (0, 0, -60), skin, root, bevel=0.04)
    hd = kit.empty("server.head", (0, -0.3, 1.7), root)
    # head 0.74 wide, 1.1 tall, 0.46 deep; centre z measured from hd
    kit.box("srv.head", (0.74, 0.46, 0.98), (0, 0, 0.0), skin, hd, bevel=0.1)
    kit.box("srv.cap", (0.78, 0.5, 0.12), (0, 0.0, 0.5), peach, hd, bevel=0.04)
    kit.box("srv.visor", (0.7, 0.34, 0.05), (0, -0.3, 0.45), peach, hd, bevel=0.02)
    # the hollow face
    kit.box("srv.void", (0.6, 0.03, 0.7), (0, -0.235, -0.07), black, hd, bevel=0.04)
    glint = kit.emit("#fff6e0", 9.0, "srv glint")
    for sx in (-1, 1):
        kit.box(f"srv.eye{sx}", (0.15, 0.02, 0.032), (sx * 0.16, -0.262, 0.14), glint, hd, bevel=0.008, rot=(0, sx * 0.3, 0))
    for k in range(-6, 7):
        h = 0.12 if k % 2 == 0 else 0.075
        kit.box(f"srv.tooth{k}", (0.036, 0.02, h), (k * 0.043, -0.262, -0.2 + 0.1 * (k * k) / 36.0 - h / 2 + 0.06), teeth, hd, bevel=0.004)
    arms = []
    for sx in (-1, 1):
        ar = kit.empty(f"server.arm{sx}", (sx * 0.82, 0, 0.0), g)
        kit.box(f"srv.sleeve{sx}", (0.26, 0.26, 0.75), (0, 0, -0.375), mint, ar, bevel=0.05)
        kit.box(f"srv.fore{sx}", (0.17, 0.17, 0.8), (0, 0, -1.15), skin2, ar, bevel=0.04)
        kit.box(f"srv.palm{sx}", (0.22, 0.07, 0.22), (0, 0, -1.65), skin2, ar, bevel=0.02)
        for k in range(4):
            kit.box(f"srv.fing{sx}{k}", (0.04, 0.05, 0.46), ((k - 1.5) * 0.055, 0, -2.0), skin2, ar, bevel=0.01)
        arms.append(ar)
    bag = kit.empty("server.bagL", (0, 0.0, -2.1), arms[1])
    kit.box("srv.bagLm", (0.5, 0.3, 0.46), (0, 0, 0.0), kit.plastic("#c9955a", 0.9, "bag"), bag, bevel=0.02)
    kit.box("srv.bagLf", (0.5, 0.32, 0.05), (0, 0, 0.25), kit.plastic("#b98448", 0.9, "bag fold"), bag)
    quad(kit, "srv.ticketL", 0.26, 0.34, (0, -0.156, 0.0), FACE_NEG_Y, M["tix41"], bag)
    # level 0: the ordinary arm with the bag, from behind the wall
    root0 = kit.empty("server.r0", (H2X, 4.87, 0))
    arm0 = kit.empty("server.arm0", (0.42, 0.18, 1.2), root0)
    kit.box("srv.sleeve0", (0.22, 1.0, 0.22), (0, -0.5, 0), mint, arm0, bevel=0.04)
    kit.box("srv.hand0", (0.2, 0.22, 0.12), (0, -1.1, -0.04), skin2, arm0, bevel=0.03)
    bag0 = kit.empty("server.bag0", (0, -1.12, 0.0), arm0)
    kit.box("srv.bagm0", (0.5, 0.3, 0.46), (0, 0, 0.26), kit.plastic("#c9955a", 0.9, "bag"), bag0, bevel=0.02)
    kit.box("srv.bagfold0", (0.5, 0.32, 0.05), (0, 0, 0.5), kit.plastic("#b98448", 0.9, "bag fold"), bag0)
    quad(kit, "srv.ticket0", 0.26, 0.34, (0, -0.156, 0.26), FACE_NEG_Y, M["tix41"], bag0)
    ctx["server"] = {"root": root, "g": g, "head": hd, "arms": arms, "r0": root0, "neck": ctx["neck"]}


# ------------------------------------------------------------------------------------------------ materials
def materials(kit, d):
    M = {}
    draw_menu(d / "menu.png")
    draw_sign(d / "sign.png")
    for n in (41, 42):
        draw_digits(d / f"scr{n}.png", n)
        draw_digits(d / f"tix{n}.png", n, bg="#fffdf4", fg="#15110f", size=330, w=384, h=512)
    M["menu"] = img_mat(kit, "menu board", d / "menu.png", 0.0, 0.8)
    M["sign"] = img_mat(kit, "road sign", d / "sign.png", 0.0, 0.8)
    M["scr41"] = img_mat(kit, "scr41", d / "scr41.png", 2.5)
    M["scr42"] = img_mat(kit, "scr42", d / "scr42.png", 2.5)
    M["tix41"] = img_mat(kit, "tix41", d / "tix41.png", 0.5, 0.9)
    M["tix42"] = img_mat(kit, "tix42", d / "tix42.png", 0.5, 0.9)
    M["mint"] = kit.plastic("#7fe0c4", 0.4, "mint")
    M["mint2"] = kit.plastic("#68cdb0", 0.45, "mint dark")
    M["peach"] = kit.plastic("#ffb38a", 0.4, "peach")
    M["cream"] = kit.plastic("#fff1d6", 0.6, "cream")
    M["steel"] = kit.metal("#aeb4b8", 0.3, "steel")
    M["asph"] = kit.texture("asphalt", 0.5, tint="#c9c6c6", mat_name="asph")
    M["asph2"] = kit.texture("asphalt", 0.5, tint="#b0aeb0", mat_name="asph2")
    M["conc"] = kit.texture("concrete", 0.5, tint="#e8e2da", mat_name="conc")
    M["brick"] = kit.texture("brick", 1.0, tint="#e0a090", mat_name="brickw")
    M["grass"] = kit.texture("grass", 0.5, tint="#c8e090", mat_name="grassw")
    M["white"] = kit.plastic("#fbfaf4", 0.5, "line white")
    M["dark"] = kit.plastic("#2a2d33", 0.6, "dark")
    M["warm"] = kit.emit("#fff0d0", 1.0, "hatch glow")
    return M


# ------------------------------------------------------------------------------------------------ the world
def hatch(kit, M, name, cx, y0, wall_h, x0, x1, thick=0.2):
    """A front wall along y = y0 (x0..x1) with an opening (cx +-0.75, z 1.1 .. 2.3), a steel sill and a peach awning."""
    mi = M["mint"]
    kit.box(f"{name}.wl", ((cx - 0.78) - x0, thick, wall_h), ((x0 + cx - 0.78) / 2, y0 + thick / 2, wall_h / 2), mi, bevel=0.03)
    kit.box(f"{name}.wr", (x1 - (cx + 0.78), thick, wall_h), ((x1 + cx + 0.78) / 2, y0 + thick / 2, wall_h / 2), mi, bevel=0.03)
    kit.box(f"{name}.wb", (1.56, thick, SILL_Z), (cx, y0 + thick / 2, SILL_Z / 2), mi, bevel=0.03)
    kit.box(f"{name}.wt", (1.56, thick, wall_h - 2.3), (cx, y0 + thick / 2, 2.3 + (wall_h - 2.3) / 2), mi, bevel=0.03)
    kit.box(f"{name}.sill", (1.7, 0.7, 0.06), (cx, y0 - 0.25, SILL_Z + 0.03), M["steel"], bevel=0.02)
    for sx in (-1, 1):
        kit.box(f"{name}.jamb{sx}", (0.1, thick + 0.12, 1.3), (cx + sx * 0.8, y0 + thick / 2 - 0.04, 1.7), M["peach"], bevel=0.02)
    kit.box(f"{name}.head", (1.7, thick + 0.12, 0.1), (cx, y0 + thick / 2 - 0.04, 2.35), M["peach"], bevel=0.02)
    kit.box(f"{name}.awn", (2.3, 1.0, 0.1), (cx, y0 - 0.45, 2.62), M["peach"], bevel=0.03)
    kit.box(f"{name}.awnf", (2.3, 0.08, 0.3), (cx, y0 - 0.95, 2.52), M["peach"], bevel=0.03)


def build_world(kit, M, ctx):
    # ground: asphalt everywhere, a lighter lane, grass strips on the far side, white dashes
    kit.box("ground", (260, 140, 0.2), (0, 20, -0.1), M["asph2"])
    kit.box("lane", (120, 3.4, 0.02), (-10, LANE_Y, 0.01), M["asph"])
    kit.box("lane back", (120, 3.0, 0.02), (-5, 10.6, 0.01), M["asph"])
    for i in range(-14, 14):
        kit.box(f"dash{i}", (1.4, 0.12, 0.02), (i * 2.8, 0.88, 0.025), M["white"])
    kit.box("kerb lot", (120, 0.3, 0.2), (-10, -0.6, 0.1), M["conc"], bevel=0.04)
    kit.box("grass lot", (140, 22, 0.12), (-10, -12.4, 0.06), M["grass"])
    kit.box("kerb end", (0.5, 0.9, 0.2), (6.6, 4.1, 0.1), M["conc"], bevel=0.04)
    # painted exit arrow on the asphalt, pointing +x (an arrow of blocks, no words)
    kit.box("arrow shaft", (1.8, 0.22, 0.02), (14.5, LANE_Y, 0.03), M["white"])
    kit.box("arrow a", (0.7, 0.2, 0.02), (15.2, LANE_Y + 0.22, 0.03), M["white"], rot=(0, 0, -0.7))
    kit.box("arrow b", (0.7, 0.2, 0.02), (15.2, LANE_Y - 0.22, 0.03), M["white"], rot=(0, 0, 0.7))
    # the building
    H = 3.3
    hatch(kit, M, "h1", H1X, WALL_Y, H, -9.0, 6.4)
    kit.box("bld side L", (0.2, 4.6, H), (-8.9, 6.9, H / 2), M["mint"], bevel=0.03)
    kit.box("bld side R", (0.2, 4.6, H), (6.3, 6.9, H / 2), M["mint"], bevel=0.03)
    kit.box("bld back", (15.4, 0.2, H), (-1.3, 9.1, H / 2), M["mint2"], bevel=0.03)
    kit.box("bld roof", (15.6, 4.8, 0.2), (-1.3, 6.9, H + 0.1), M["mint"], bevel=0.03)
    kit.box("bld band", (15.8, 0.15, 0.55), (-1.3, 4.5, H - 0.25), M["peach"], bevel=0.03)
    kit.box("bld floor", (15.4, 4.4, 0.1), (-1.3, 6.9, 0.05), M["cream"])
    kit.box("bld in back", (15.0, 0.1, H), (-1.3, 8.9, H / 2), M["cream"])
    kit.box("counter", (4.0, 0.6, 1.05), (0, 5.2, 0.52), M["cream"], bevel=0.03)
    # wall B and hatch 2
    wb = kit.empty("wallB", (0, 0, 0))
    ctx["wallB"] = wb
    before = set(bpy.data.objects)
    hatch(kit, M, "h2", H2X, WALL_Y, H, 6.8, 13.6)
    kit.box("wb sideL", (0.2, 1.6, H), (6.9, 5.5, H / 2), M["mint"], bevel=0.03)
    kit.box("wb sideR", (0.2, 1.6, H), (13.5, 5.5, H / 2), M["mint"], bevel=0.03)
    kit.box("wb back", (6.8, 0.2, H), (10.2, 6.3, H / 2), kit.plastic("#1d3a36", 0.8, "wb inner"), bevel=0.03)
    kit.box("wb roof", (6.9, 1.9, 0.2), (10.2, 5.5, H + 0.1), M["mint"], bevel=0.03)
    kit.box("wb band", (7.0, 0.15, 0.55), (10.2, 4.5, H - 0.25), M["peach"], bevel=0.03)
    kit.box("wb floor", (6.8, 1.7, 0.1), (10.2, 5.5, 0.05), kit.plastic("#6b8d86", 0.8, "wb floor"))
    for nm, rz in (("h2.head", 0.05), ("h2.jamb-1", 0.035), ("h2.jamb1", 0.035)):
        ob = bpy.data.objects.get(nm)
        if ob is not None:
            ob.rotation_euler = (0, rz, 0)
    ctx["wallB_objs"] = [o for o in bpy.data.objects if o not in before and o.parent is None]
    # the lore: one short peach stroke on the one real window's sill (1 cm proud), and the ticket by it
    kit.box("tally", (0.012, 0.16, 0.012), (-0.45, 4.2, SILL_Z + 0.066), M["peach"])
    ctx["sillticket"] = quad(kit, "sillticket", 0.14, 0.2, (-0.2, 4.3, SILL_Z + 0.075), (0, 0, 0.3), M["tix41"])
    # speaker post, screen, menu board, road sign
    kit.box("post", (0.22, 0.22, 1.5), (-12.0, 3.95, 0.75), M["mint2"], bevel=0.04)
    kit.cyl("grille", 0.2, 0.06, (-12.0, 3.80, 1.15), kit.metal("#6c7074", 0.5, "grille"), rot=(math.pi / 2, 0, 0), n=20)
    kit.box("scrbox", (0.62, 0.1, 0.46), (-12.0, 3.8, 1.62), M["dark"], bevel=0.03)
    ctx["scr"] = {41: quad(kit, "scr41", 0.54, 0.4, (-12.0, 3.745, 1.62), FACE_NEG_Y, M["scr41"]),
                  42: quad(kit, "scr42", 0.54, 0.4, (-12.0, 3.745, 1.62), FACE_NEG_Y, M["scr42"])}
    for sx in (-1.5, 1.5):
        kit.box(f"mpost{sx}", (0.16, 0.16, 3.4), (-14.8 + sx, 4.2, 1.7), M["mint2"], bevel=0.03)
    kit.box("mboard", (3.4, 0.14, 2.3), (-14.8, 4.2, 2.05), M["peach"], bevel=0.04)
    quad(kit, "menu", 3.2, 2.1, (-14.8, 4.12, 2.05), FACE_NEG_Y, M["menu"])
    kit.box("signpost", (0.14, 0.14, 2.2), (-22.0, 0.4, 1.1), M["mint2"], bevel=0.03)
    kit.box("signb", (1.1, 0.1, 1.1), (-22.0, 0.4, 2.35), M["cream"], bevel=0.04)
    quad(kit, "sign", 1.0, 1.0, (-22.0, 0.34, 2.35), FACE_NEG_Y, M["sign"])
    # back wall of bricks
    kit.box("backwall", (60, 0.4, 3.2), (-5, 15.8, 1.6), M["brick"], bevel=0.02)
    kit.box("backcap", (60, 0.6, 0.2), (-5, 15.8, 3.3), M["conc"], bevel=0.03)
    # props round the lot
    P = kit.prop
    for nm, loc, kw in (("bush_1", (-6, -2.4, 0), dict(height=1.4)), ("bush_2", (4, -2.6, 0), dict(height=1.3)),
                        ("bush_1", (-19, -2.2, 0), dict(height=1.5)), ("sub_planter", (7.4, 3.2, 0), dict(fit=1.4)),
                        ("trashcan_cylindric", (-7.2, 3.9, 0), dict(height=0.95)),
                        ("sub_tree_small", (-3, -5, 0), dict(height=4.0)), ("commontree_1", (9, -7, 0), dict(height=6.5)),
                        ("commontree_1", (-17, -8, 0), dict(height=6.0)), ("bush_2", (16.5, 2.0, 0), dict(height=1.3)),
                        ("sub_tree_small", (14, -4, 0), dict(height=4.2)), ("bush_1", (17, 6.5, 0), dict(height=1.6)),
                        ("commontree_1", (22, 9, 0), dict(height=6.5)), ("commontree_1", (-30, 4, 0), dict(height=6.5))):
        P(nm, loc, **kw)
    # Mr. Dale's door (zone D)
    kit.box("dale ground", (40, 30, 0.2), (300, 8, -0.1), M["grass"])
    kit.box("dale drive", (4.0, 14, 0.04), (295.0, 0.0, 0.02), M["asph"])
    kit.box("dale path", (1.4, 6, 0.04), (300, -1.0, 0.02), M["conc"])
    P("sub_building_type_a", (300, 6.5, 0), rot=0, fit=8.0, tint="#d9c4a8")
    kit.box("dale door", (1.1, 0.12, 2.1), (300, 3.2, 1.05), M["peach"], bevel=0.03)
    P("bush_1", (296.5, 3.0, 0), height=1.2)
    P("commontree_1", (306, 1, 0), height=6.0)
    # zone R: the open road
    kit.box("road ground", (300, 80, 0.2), (600, 0, -0.1), M["grass"])
    kit.box("road", (300, 7.0, 0.04), (600, 0, 0.02), M["asph"])
    for i in range(-40, 40):
        kit.box(f"rdash{i}", (2.0, 0.14, 0.05), (600 + i * 5, 0, 0.05), M["white"])
    for i in range(-4, 5):
        P("commontree_1" if i % 2 else "sub_tree_small", (600 + i * 14, 11 + (i % 3) * 3, 0), height=6.0 if i % 2 else 4.0)
        P("bush_2", (600 + i * 16, -9.0, 0), height=1.4)


def build_lights(kit, ctx):
    sun = kit.light("sun", "SUN", (-30, -22, 20), 1.0, "#ffd9a0", size=0.02)
    kit.aim(sun, (0, 0, 0))
    sun.data.angle = 0.2
    sun.data.energy = 4.0
    ctx["sun_e"] = 4.0
    fill = kit.light("fill", "SUN", (20, -30, 24), 1.0, "#cfe0ff", size=0.02)
    kit.aim(fill, (0, 0, 0))
    fill.data.energy = 1.6
    kit.LIGHTS["fill"]["base"] = 1.6
    kit.LIGHTS["sun"]["base"] = 4.0
    # in-car fills (kept near the lane so faces read)
    kit.light("h1 in", "POINT", (0, 5.8, 2.3), 380, "#ffe6bd", size=0.4)
    kit.light("h2 warm", "POINT", (10.1, 5.6, 2.2), 260, "#ffe9c4", size=0.3)
    kit.light("h2 cool", "POINT", (10.1, 5.6, 2.2), 260, "#eaf6ff", size=0.3)
    kit.light("h2 face", "POINT", (10.1, 4.2, 1.05), 90, "#fff4e0", size=0.2)
    kit.light("lane key", "AREA", (0, -3.5, 6.0), 700, "#fff1da", size=6.0)
    kit.aim(kit.LIGHTS["lane key"]["obj"], (0, 2.8, 1.0))
    kit.light("lane key2", "AREA", (-12, -3.5, 6.0), 500, "#fff1da", size=6.0)
    kit.aim(kit.LIGHTS["lane key2"]["obj"], (-12, 3.0, 1.0))
    kit.light("lane key3", "AREA", (10.1, -3.5, 6.0), 500, "#fff1da", size=6.0)
    kit.aim(kit.LIGHTS["lane key3"]["obj"], (10.1, 3.0, 1.0))
    kit.light("back key", "AREA", (-5, 7.0, 8.0), 900, "#ffe3c0", size=8.0)
    kit.aim(kit.LIGHTS["back key"]["obj"], (-5, 12.0, 1.0))
    for nm, sx in (("srv rimL", -1), ("srv rimR", 1)):
        kit.light(nm, "POINT", (10.1 + sx * 1.5, 3.7, 2.1), 150, "#bfe6ff", size=0.15)
    kit.light("dale key", "AREA", (300, -5, 6.0), 800, "#fff1da", size=6.0)
    kit.aim(kit.LIGHTS["dale key"]["obj"], (300, 2.0, 1.4))
    kit.light("road key", "AREA", (600, -6, 6.0), 900, "#fff1da", size=8.0)
    kit.aim(kit.LIGHTS["road key"]["obj"], (600, 0, 1.0))


def build(kit, story, tl):
    d = Path(tempfile.mkdtemp(prefix="twowin"))
    M = materials(kit, d)
    ctx = {"M": M, "inited": False}
    build_world(kit, M, ctx)
    build_lights(kit, ctx)
    build_server(kit, M, ctx)
    cars = {}
    cars["ours"] = build_car(kit, M, "ours", "#5aa9e6", "open", cracked=True, tix=True, bag=True)
    for k in "ABCD":
        cars["copy" + k] = build_car(kit, M, "copy" + k, "#5aa9e6", "open", cracked=True)
    cars["lime"] = build_car(kit, M, "lime", "#a8e03a", "open")
    cars["van"] = build_car(kit, M, "van", "#dfe3e6", "van")
    for i in range(8):
        cars[f"truck{i}"] = build_car(kit, M, f"truck{i}", "#d8433a", "truck")
    ctx["cars"] = cars
    # dummy riders for the copies that are far away (block people in our colours)
    ctx["dummies"] = {}
    for k in "BCD":
        r = cars["copy" + k]["root"]
        parts = []
        for sy, sh, hc in ((0.45, "#e0a92e", "#3b2a20"), (-0.45, "#8ec9f5", "#3b2a20")):
            parts.append(kit.box(f"dm{k}{sy}t", (0.3, 0.5, 0.55), (-0.3, sy, 0.8), kit.plastic(sh, 0.5, f"dm {sh}"), r, bevel=0.05))
            parts.append(kit.sphere(f"dm{k}{sy}h", 0.2, (-0.3, sy, 1.3), kit.plastic("#e8b88f", 0.5, "dm skin"), r))
            parts.append(kit.box(f"dm{k}{sy}x", (0.34, 0.4, 0.14), (-0.3, sy, 1.43), kit.plastic(hc, 0.6, "dm hair"), r, bevel=0.04))
        ctx["dummies"][k] = parts
    return ctx


# ------------------------------------------------------------------------------------------------ animate
def animate(kit, story, tl, t, ctx):
    bpy.context.view_layer.update()
    # seated riders: legs forward (sitting characters are those with a "sit" key)
    for who, keys in tl["acting"].items():
        sit = False
        for k in keys:
            if k["t"] <= t + 1e-9 and "sit" in k:
                sit = bool(k["sit"])
        if sit:
            for sx in (-1, 1):
                ob = bpy.data.objects.get(f"{who}.leg{sx}")
                if ob is not None:
                    ob.rotation_euler = (-math.pi / 2, 0, 0)
    for who, keys in tl["acting"].items():
        tor = bpy.data.objects.get(f"{who}.torso")
        if tor is not None:
            from blocky import acting as _ac
            tor.rotation_euler = (0, math.radians(_ac._held(keys, "roll", t, 0.0)), 0)
    cars = ctx["cars"]
    cc = _cues(tl, "car")
    for cid, car in cars.items():
        cs = [c for c in cc if c["id"] == cid]
        r = _lin_pos(cs, t)
        root = car["root"]
        last = _last(cs, t)
        if r is None or last is None or last.get("hide"):
            root.location = (0, 0, -60)
            continue
        p, yaw = r
        root.location = (p[0], p[1], 0.0)
        root.rotation_euler = (0, 0, math.radians(yaw))
    # visibility cues
    vc = _cues(tl, "vis")
    def vis(i, default):
        c = _last([c for c in vc if c["id"] == i], t)
        return c["on"] if c else default
    for o in ctx["wallB_objs"]:
        _show([o], vis("wallB", True))
    o_ = cars["ours"]
    n_tix = 0
    for c in [c for c in vc if c["id"] == "tix"]:
        if c["t"] <= t + 1e-9:
            n_tix = c["n"]
    for j, q in enumerate(o_["tix"]):
        i = j % 5
        q.hide_render = not ((i < n_tix and i < 4) or (i == 4 and n_tix == 42))
        if n_tix == 42 and i < 4:
            q.hide_render = True
        o_["tixf"][j].hide_render = q.hide_render
    _show([ctx["sillticket"]], vis("sillticket", False))
    cup = o_.get("cup")
    if cup is not None:
        cup.hide_render = not vis("cup", False)
    bc = _last(_cues(tl, "bagcar"), t)
    _show([o_["bag"]], bool(bc and bc.get("on")))
    for k in "BCD":
        for d in ctx["dummies"][k]:
            d.hide_render = False
    sc = _last(_cues(tl, "scr"), t)
    n = sc["n"] if sc else 41
    ctx["scr"][41].hide_render = n != 41
    ctx["scr"][42].hide_render = n != 42
    # the Server: level 0..3, eased between cues
    srv = ctx["server"]
    sv = _cues(tl, "server")
    lv = float(_eased(sv, "lv", t, 0.0))
    cur = _last(sv, t)
    on = bool(cur and cur.get("on", True))
    for r_, want in ((srv["root"], lv >= 0.5), (srv["r0"], lv < 0.5)):
        _show([r_], on and want)
    if lv >= 0.5:
        u1, u2 = min(1.0, max(0.0, lv - 1.0)), min(1.0, max(0.0, lv - 2.0))
        out = 0.35 * u1 + 0.3 * u2                    # metres the face comes out over the sill (toward -y)
        srv["g"].location = (0, -0.4 * out + 0.05 * (1 - min(1.0, lv)), 1.85 - 0.05 * u1 - 0.05 * u2)
        srv["g"].rotation_euler = (math.radians(4 + 10 * u1 + 8 * u2), 0, 0)
        srv["head"].location = (0, -0.3 - 1.0 * out, 1.74)
        srv["head"].rotation_euler = (math.radians(4 + 3 * u1 + 3 * u2), 0, math.radians(-34 * u1))
        # the neck runs from the shoulders to the chin
        gy, gz = srv["g"].location[1], srv["g"].location[2] + 0.15
        hy, hz = srv["head"].location[1], srv["head"].location[2] - 0.45
        ln = max(0.1, math.hypot(hy - gy, hz - gz))
        srv["neck"].location = (0, (hy + gy) / 2, (hz + gz) / 2)
        srv["neck"].scale = (1, 1, ln)
        srv["neck"].rotation_euler = (math.atan2(-(hy - gy), hz - gz), 0, 0)
        T = 150 - 45 * u1 - 15 * u2               # the arms' angle from straight down (180) toward out (90)
        for sx, ar in zip((-1, 1), srv["arms"]):
            ar.rotation_euler = (math.radians(T - 180), 0, sx * math.radians(6 + 4 * u2))
    # lights: every change is a slow ramp
    h2 = float(_eased(_cues(tl, "h2"), "v", t, 0.0))
    dim = float(_eased(_cues(tl, "dim"), "v", t, 0.0))
    # the front lights die slowly (1.2 s ramps, never a global flash) while it is out
    slc = [{"t": c["t"], "v": 1.0 if (c.get("lv", 0) >= 1 and c.get("on", True)) else 0.0, "dur": 1.2}
           for c in sv if "lv" in c]
    sl = float(_eased(slc, "v", t, 0.0))
    return {"h2 warm": 1.0 - h2, "h2 cool": h2, "h2 face": (0.4 + 0.5 * h2) * min(1.0, max(0.0, lv)),
            "sun": (1.0 - 0.55 * dim) * (1.0 - 0.4 * sl), "fill": (1.0 - 0.5 * dim) * (1.0 - 0.3 * sl),
            "lane key": 1.0 - 0.5 * dim, "lane key2": 1.0 - 0.5 * dim,
            "lane key3": (1.0 - 0.5 * dim) * (1.0 - 0.5 * sl), "back key": 1.0 - 0.5 * dim,
            "srv rimL": sl, "srv rimR": sl}
