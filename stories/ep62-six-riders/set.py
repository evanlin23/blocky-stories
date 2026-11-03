"""ep62 Six Riders: a bright steel office elevator whose mirror doors show one rider too many.

Everything is built from kit.py's parts. The only lettering in the set is our own: the A to E tags over the riders
(caption font, flat game-style plates that always face the camera) and the teal digits on the floor display.

The mirror is faked. Doors sit on the plane y = 0 and the car runs toward the camera (y > 0). Behind the glass is a second
room (y < 0) with the mirror cast standing in it: each reflection is a character at the rider's own x, at -y, turned to
face us. A real reflection keeps its rider's screen side, and so does this. The copy is not a reflection at all: it is
C's model turned round, so its bag lands on the other screen side. Bags are separate orange blocks, parented to the
torso, whose side comes from the "bags" cue (a side of -1 is the rig's -x). Screen right is world -x.

The glass is one plane per door half, drawn over the frame, 4 cm in front of the frame's face on the car side. Its steel
tint eases from 10% to 100% as the halves start to part, and the mirror room is hidden once it is opaque, so the faces
leave with the doors and nothing pops. Layered surfaces stand at least 1 cm proud of each other throughout.

Cues read here:
  digit {d}                  the floor display (and its corner copy)
  tag {who}                  a tag pops in over a rider, easing in over 0.15 s
  tagflip {who}              that tag is drawn backwards from here on
  door {open, dur}           the halves slide to open (1) or closed (0)
  bags {name: side}          which side each bag is on (0: none); names are cast names
  ring {on}                  the orange ring round the two blue jackets in the glass, easing in over 0.3 s
"""

from __future__ import annotations

import math
import tempfile
from pathlib import Path

import bpy
from mathutils import Vector as V
from PIL import Image, ImageDraw, ImageFont

from blocky import rig

HERE = Path(__file__).resolve().parent
FONT = HERE.parent.parent / "blocky" / "fonts" / "SchibstedGrotesk-Black.ttf"

HW = 1.95          # the car's half width
CD = 4.4           # the car's depth (the back wall)
CH = 4.0           # the ceiling
DH = 2.5           # the doors' height
LEN = 9.0          # how far the corridor runs beyond the doors
TEAL = "#20e3d2"
ORANGE = "#ff8a1f"

# a rider's spot is (x, y); the mirror cast stands at (x, -y) and faces us
ROWS = {"c": (-1.1, 0.35), "a": (1.35, 0.35), "b": (0.9, 1.6), "d": (-0.6, 1.6), "e": (-1.5, 1.6)}
GAP = (0.1, 0.35)
TAG_Z = 1.3

SHOT_NO_DISPLAY = {"S01", "S02", "S04", "S05b", "S06", "S09b", "S12", "S13", "S14", "S15", "S15b", "S16", "S17",
                   "S18", "S19b", "S22", "S23", "S24", "S25"}   # overridden by the story's "corner" list when present


def ss(x):
    x = min(1.0, max(0.0, x))
    return x * x * (3 - 2 * x)


def cue_list(tl, name):
    return [c for c in tl.get("cues", []) if c["name"] == name]


def cue_at(tl, name, t):
    out = {}
    for c in tl.get("cues", []):
        if c["name"] == name and c["t"] <= t + 1e-9:
            out = c
    return out


def shot_at(tl, t):
    for s in tl["shots"]:
        if s["start"] <= t < s["end"]:
            return s
    return tl["shots"][-1]


# ------------------------------------------------------------------------------------------------ pictures


def digit_png(path, d):
    im = Image.new("RGBA", (512, 256), (4, 8, 9, 255))
    dr = ImageDraw.Draw(im)
    dr.rounded_rectangle([6, 6, 505, 249], 28, outline=(20, 70, 68, 255), width=5)
    f = ImageFont.truetype(str(FONT), 190)
    txt = str(d)
    w = dr.textlength(txt, font=f)
    dr.text((300 - w / 2, 128), txt, font=f, fill=(32, 227, 210, 255), anchor="lm")
    # a small down arrow
    ax, ay = 110, 128
    dr.polygon([(ax - 52, ay - 22), (ax + 52, ay - 22), (ax, ay + 56)], fill=(32, 227, 210, 255))
    dr.rectangle([ax - 18, ay - 70, ax + 18, ay - 20], fill=(32, 227, 210, 255))
    im.save(path)


def tag_png(path, letter, flip=False):
    n = 256
    im = Image.new("RGBA", (n, n), (0, 0, 0, 0))
    dr = ImageDraw.Draw(im)
    dr.rounded_rectangle([6, 6, n - 7, n - 7], 52, fill=(255, 255, 255, 255), outline=(32, 227, 210, 255), width=18)
    f = ImageFont.truetype(str(FONT), 180)
    dr.text((n / 2, n / 2 + 6), letter, font=f, fill=(10, 10, 12, 255), anchor="mm")
    if flip:
        im = im.transpose(Image.FLIP_LEFT_RIGHT)
    im.save(path)


def img_mat(kit, name, path, strength=1.6, solid_alpha=False):
    """An unlit picture plane: the PNG's colour, its alpha cutting the shape out."""
    m = kit._new(name)
    nt = m.node_tree
    N, L = nt.nodes, nt.links
    N.remove(N["Principled BSDF"])
    tc = N.new("ShaderNodeTexCoord")
    tx = N.new("ShaderNodeTexImage")
    L.new(tc.outputs["Generated"], tx.inputs["Vector"])
    tx.image = bpy.data.images.load(str(path), check_existing=False)
    tx.image.colorspace_settings.name = "sRGB"
    tx.interpolation = "Linear"
    em = N.new("ShaderNodeEmission")
    em.inputs["Strength"].default_value = strength
    L.new(tx.outputs["Color"], em.inputs["Color"])
    out = next(n for n in N if n.type == "OUTPUT_MATERIAL")
    if solid_alpha:
        L.new(em.outputs[0], out.inputs["Surface"])
    else:
        tr = N.new("ShaderNodeBsdfTransparent")
        mx = N.new("ShaderNodeMixShader")
        L.new(tx.outputs["Alpha"], mx.inputs[0])
        L.new(tr.outputs[0], mx.inputs[1])
        L.new(em.outputs[0], mx.inputs[2])
        L.new(mx.outputs[0], out.inputs["Surface"])
    return m, tx


def steel_mat(kit, name, hexc, metal=0.35, rough=0.45):
    if name in kit.MATS:
        return kit.MATS[name]
    m = kit._new(name)
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = kit.col(hexc)
    b.inputs["Metallic"].default_value = metal
    b.inputs["Roughness"].default_value = rough
    m.diffuse_color = kit.col(hexc)
    kit._fogged(m, b.outputs[0])
    return m


def glass_mat(kit, name):
    """Steel-tinted glass: a mix of transparent and a pale steel, the mix set from animate()."""
    m = kit._new(name)
    nt = m.node_tree
    N, L = nt.nodes, nt.links
    b = N["Principled BSDF"]
    b.inputs["Base Color"].default_value = kit.col("#cfd8dd")
    b.inputs["Metallic"].default_value = 0.3
    b.inputs["Roughness"].default_value = 0.4
    tr = N.new("ShaderNodeBsdfTransparent")
    mx = N.new("ShaderNodeMixShader")
    mx.inputs[0].default_value = 0.10
    L.new(tr.outputs[0], mx.inputs[1])
    L.new(b.outputs[0], mx.inputs[2])
    kit._fogged(m, mx.outputs[0])
    return m, mx


# ------------------------------------------------------------------------------------------------ build


def build(kit, story, tl):
    work = Path(tempfile.mkdtemp(prefix="ep62-"))
    ctx = {"work": work}
    kit.FLASH_SAFE = True
    steel = steel_mat(kit, "steel", "#c9d1d6")
    steel_d = steel_mat(kit, "steel dark", "#8f9aa1", 0.5, 0.4)
    white = kit.plastic("#f1f4f6", 0.6, spec=0.2)
    floor = kit.plastic("#d9dde0", 0.35, spec=0.5)
    wallw = kit.plastic("#eef1f3", 0.7, spec=0.2)
    stripe = kit.plastic(TEAL, 0.4)
    panel = kit.emit("#f4fbff", 4.0, name="led")
    black = kit.plastic("#08090b", 0.5)
    glassm, glass_mix = glass_mat(kit, "door glass")
    ctx["glass_mix"] = glass_mix

    Z = CH / 2
    # ---- the shell: floor and ceiling run the whole way and wide; the car's side walls stop at the doors
    WW = 3.0   # the glass room is wider than the car (a reflection wider than its car is never checked)
    kit.box("floor", (2 * WW + 0.4, CD + LEN, 0.1), (0, (CD - LEN) / 2, -0.05), floor)
    kit.box("ceiling", (2 * WW + 0.4, CD + LEN, 0.1), (0, (CD - LEN) / 2, CH + 0.05), white)
    for sx in (-1, 1):
        kit.box(f"wall{sx}", (0.2, CD + 0.1, CH), (sx * (HW + 0.1), CD / 2 - 0.05, Z), steel)
    kit.box("backwall", (2 * HW + 0.4, 0.2, CH), (0, CD + 0.1, Z), steel)
    kit.box("header", (2 * HW, 0.2, CH - DH), (0, 0.05, DH + (CH - DH) / 2), steel)
    # a darker kick strip at the foot of the car's walls, and the ceiling's LED panels 1 cm below it
    for sx in (-1, 1):
        kit.box(f"kick{sx}", (0.03, CD - 0.1, 0.12), (sx * (HW - 0.015), CD / 2 + 0.05, 0.06), steel_d)
        kit.box(f"rail{sx}", (0.05, CD - 0.3, 0.05), (sx * (HW - 0.05), CD / 2 + 0.05, 0.95), steel_d)
    kit.box("ledcar", (2.4, 2.8, 0.04), (0, 2.1, CH - 0.02), panel)
    kit.box("ledcar_frame", (2.56, 2.96, 0.02), (0, 2.1, CH - 0.01), steel_d)
    kit.box("ledmir", (2.4, 2.8, 0.04), (0, -2.1, CH - 0.02), panel)
    kit.box("ledmir_frame", (2.56, 2.96, 0.02), (0, -2.1, CH - 0.01), steel_d)
    # the backwall's handrail and the door header's display plate
    kit.box("rail_back", (2 * HW - 0.1, 0.05, 0.05), (0, CD - 0.05, 0.95), steel_d)

    # ---- the floor display on the header (car side), digits 1.5 cm proud of the plate
    kit.box("dispplate", (0.62, 0.03, 0.34), (0, 0.15 + 0.015, DH + 0.42), black)
    ctx["digit_mats"] = {}
    for d in range(1, 8):
        p = work / f"digit{d}.png"
        digit_png(p, d)
        ctx["digit_mats"][d] = img_mat(kit, f"digit {d}", p, 2.2, solid_alpha=True)
    dm, dtx = ctx["digit_mats"][7]
    plane = kit.plane("disp", (0.56, 0.28), (0, 0.15 + 0.045, DH + 0.42), dm, rot=(math.pi / 2, 0, math.pi))
    ctx["disp"] = plane
    ctx["disp_tx"] = dtx
    # a small corner copy of the display on the camera, for the tight shots
    cm, ctx_ = img_mat(kit, "digit corner", work / "digit7.png", 2.2, solid_alpha=True)
    corner = kit.plane("corner", (0.26, 0.13), (0, 0, -1), cm)
    corner.parent = kit.OBJ["cam"]
    corner.hide_render = True
    ctx["corner"] = corner
    ctx["corner_tx"] = ctx_

    # ---- the doors: two halves, frame boxes with the glass on the car side
    ctx["halves"] = []
    ctx["glass_objs"] = []
    for sx in (1, -1):
        grp = kit.empty(f"half{sx}", (0, 0, 0))
        w = HW
        cx = sx * w / 2
        kit.box(f"half{sx}.top", (w, 0.06, 0.06), (cx, 0.0, DH - 0.03), steel_d, grp)
        kit.box(f"half{sx}.bot", (w, 0.06, 0.06), (cx, 0.0, 0.03), steel_d, grp)
        kit.box(f"half{sx}.out", (0.06, 0.06, DH), (sx * (w - 0.03), 0.0, DH / 2), steel_d, grp)
        kit.box(f"half{sx}.mid", (0.06, 0.06, DH), (sx * 0.03, 0.0, DH / 2), steel_d, grp)
        gp = kit.plane(f"glass{sx}", (w - 0.06, DH - 0.12), (cx, 0.04, DH / 2), glassm, grp, rot=(math.pi / 2, 0, 0))
        ctx["halves"].append((grp, sx))
        ctx["glass_objs"].append(gp)

    # ---- the mirror room (wider than the car), and the corridor that shows when the doors open
    mirror, corr = [], []
    mirror.append(kit.box("mirror_back", (2 * WW + 0.4, 0.2, CH), (0, -CD - 0.1, Z), steel))
    mirror.append(kit.box("mrail_back", (2 * WW - 0.1, 0.05, 0.05), (0, -CD + 0.05, 0.95), steel_d))
    for sx in (-1, 1):
        mirror.append(kit.box(f"mwall{sx}", (0.2, CD + 0.1, CH), (sx * (WW + 0.1), -CD / 2 + 0.05, Z), steel))
        mirror.append(kit.box(f"mkick{sx}", (0.03, CD - 0.1, 0.12), (sx * (WW - 0.015), -CD / 2 - 0.05, 0.06), steel_d))
        mirror.append(kit.box(f"mrail{sx}", (0.05, CD - 0.3, 0.05), (sx * (WW - 0.05), -CD / 2 - 0.05, 0.95), steel_d))
        corr.append(kit.box(f"cwall{sx}", (0.2, LEN, CH), (sx * (HW + 0.1), -LEN / 2, Z), wallw))
    ctx["mirror_objs"] = mirror
    corr.append(kit.box("stripe", (0.3, LEN - 0.3, 0.02), (0, -LEN / 2, 0.01), stripe))
    corr.append(kit.box("corr_far", (2 * HW + 0.4, 0.2, CH), (0, -LEN - 0.1, Z), wallw))
    corr.append(kit.box("corr_ledl", (2.0, 3.0, 0.04), (0, -CD - 1.0, CH - 0.02), panel))
    ctx["corr_objs"] = corr

    # ---- the ring round the two blue jackets in the glass (the mirror room), flat, orange, facing us
    ring = _ring(kit, kit.emit(ORANGE, 3.0, name="ring"))
    ctx["ring"] = ring
    mirror.append(ring)

    # ---- tags
    ctx["tags"] = {}
    for L_ in "ABCDE":
        p = work / f"tag{L_}.png"
        pf = work / f"tag{L_}f.png"
        tag_png(p, L_)
        tag_png(pf, L_, flip=True)
        m, _ = img_mat(kit, f"tag {L_}", p, 1.4)
        mf, _ = img_mat(kit, f"tag {L_} flipped", pf, 1.4)
        x, y = ROWS[L_.lower()]
        t = kit.plane(f"tag{L_}", (0.32, 0.32), (x, y + 0.24, TAG_Z + (0.15 if L_ == "A" else 0)), m, rot=(math.pi / 2, 0, math.pi))
        t.hide_render = True
        ctx["tags"][L_] = (t, m, mf)

    # ---- lights: cool white from the ceiling in the car, in the glass room and in the corridor, a soft warm fill
    kit.light("car", "AREA", (0, 1.9, CH - 0.1), 380, "#eaf6ff", size=2.6)
    kit.light("glassroom", "AREA", (0, -1.9, CH - 0.1), 380, "#eaf6ff", size=2.6)
    kit.light("corr", "AREA", (0, -CD - 1.0, CH - 0.1), 520, "#f0fbff", size=2.6)
    kit.light("fill", "POINT", (0.3, CD - 0.25, 1.9), 120, "#ffe9d0", size=0.6)
    kit.light("front", "AREA", (0, 0.9, 1.8), 55, "#e8f4ff", rot=(math.pi / 2, 0, 0), size=3.0)
    ctx["bags"] = {}
    return ctx


def _ring(kit, mat):
    """An elliptical band, 4 cm thick in y, standing in the glass room round the two blue jackets."""
    n = 64
    cx, cz, rx, rz, w = -0.4, 1.22, 0.85, 0.6, 0.07
    verts, faces = [], []
    for i in range(n):
        a = 2 * math.pi * i / n
        for k, rr in enumerate((1.0, 1.0 - w / rz * 1.0)):
            r1 = (rx - (0 if k == 0 else w)) * math.cos(a)
            r2 = (rz - (0 if k == 0 else w)) * math.sin(a)
            verts.append((r1, 0, r2))
    for i in range(n):
        j = (i + 1) % n
        faces.append((i * 2, j * 2, j * 2 + 1, i * 2 + 1))
    ob = kit.mesh_obj("ring", verts, faces, mat, None, (cx, -0.12, cz))
    ob.hide_render = True
    return ob


# ------------------------------------------------------------------------------------------------ animate


def door_p(tl, t):
    """How far open the doors are (0 shut, 1 open), eased over each door cue's dur."""
    p = 0.0
    for c in cue_list(tl, "door"):
        dur = c.get("dur", 0.8)
        tgt = float(c["open"])
        if t >= c["t"] + dur:
            p = tgt
        elif t > c["t"]:
            u = ss((t - c["t"]) / dur)
            p = p + (tgt - p) * u
            return p
    return p


def _bag(kit, ch):
    """An orange bag on a strap, parented to the torso, in rig units (1 unit = 0.34 m)."""
    org = kit.plastic(ORANGE, 0.5, spec=0.5)
    flap = kit.plastic("#e06a00", 0.5, spec=0.4)
    root = kit.empty(f"{ch.name}.bag", (0, 0, 0), ch.torso)
    kit.box(f"{ch.name}.bagbody", (0.85, 1.2, 1.6), (0, 0.25, 0.5), org, root, bevel=0.12)
    kit.box(f"{ch.name}.bagflap", (0.89, 1.24, 0.5), (0, 0.25, 1.2), flap, root, bevel=0.09)
    # the strap runs up from the bag over the shoulder: a flat band 3 cm proud of the back
    kit.box(f"{ch.name}.strap", (0.2, 0.08, 1.9), (-0.55, 0.56, 1.05), org, root, rot=(0, -0.3, 0), bevel=0.02)
    return root


def animate(kit, story, tl, t, ctx):
    p = door_p(tl, t)
    # glass tint and the doors' slide
    ctx["glass_mix"].inputs[0].default_value = 0.10 + 0.90 * ss(p / 0.3)
    for grp, sx in ctx["halves"]:
        grp.location = (sx * (HW + 0.05) * p, 0, 0)
    mirror_on = p < 0.3
    for o in ctx["mirror_objs"]:
        o.hide_render = not mirror_on
    for o in ctx["corr_objs"]:
        o.hide_render = mirror_on
    ring_on = cue_at(tl, "ring", t)
    rg = ctx["ring"]
    if mirror_on and ring_on.get("on"):
        u = ss((t - ring_on["t"]) / 0.3)
        rg.hide_render = u <= 0.001
        rg.scale = (0.4 + 0.6 * u,) * 3
    else:
        rg.hide_render = True
    # the mirror cast goes with the doors
    for name in ("ra", "rb", "rc", "rd", "re", "x", "bro"):
        ch = rig.CHARS.get(name)
        if ch is None:
            continue
        if not mirror_on:
            ch.root.hide_render = True
            for ob in ch.root.children_recursive:
                ob.hide_render = True
    # bags
    bags = cue_at(tl, "bags", t)
    for name, side in (bags.get("sides") or {}).items():
        ch = rig.CHARS.get(name)
        if ch is None:
            continue
        b = ctx["bags"].get(name)
        if b is None:
            b = ctx["bags"][name] = _bag(kit, ch)
        hidden = ch.root.hide_render or side == 0
        for ob in [b] + list(b.children_recursive):
            ob.hide_render = hidden
        if side:
            b.scale = (1 if side > 0 else -1, 1, 1)
            b.location = (side * 1.5, 0.0, 0.0)
    for name, b in ctx["bags"].items():
        if name not in (bags.get("sides") or {}):
            for ob in [b] + list(b.children_recursive):
                ob.hide_render = True
    # the display
    d = cue_at(tl, "digit", t).get("d", 7)
    dm, dtx = ctx["digit_mats"][d]
    ctx["disp"].data.materials[0] = dm
    ctx["corner"].data.materials[0] = dm
    shot = shot_at(tl, t)
    corner_shots = set(story.get("corner", []))
    show_corner = shot["id"] in corner_shots
    sh = next((s for s in story["shots"] if s["id"] == shot["id"]), None)
    lens = sh["cam"][0][3] if sh else 14
    cor = ctx["corner"]
    cor.hide_render = not show_corner
    dist = 0.9
    k = 12.0 / lens           # half height at 1 m
    cor.location = (0.62 * dist * k * 0.5625, 0.80 * dist * k, -dist)
    cor.scale = (dist * k, dist * k, 1)
    # tags
    for L_, (obj, m, mf) in ctx["tags"].items():
        started = [c for c in cue_list(tl, "tag") if c.get("who") == L_]
        if not started:
            obj.hide_render = True
            continue
        t0 = started[0]["t"]
        u = ss((t - t0) / 0.15)
        obj.hide_render = u <= 0.001
        flip = any(c.get("who") == L_ and c["t"] <= t for c in cue_list(tl, "tagflip"))
        obj.data.materials[0] = mf if flip else m
        sc = 0.3 + 0.7 * u
        obj.scale = (sc, sc, sc)
    return {}
