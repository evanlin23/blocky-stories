"""ep82-no-door: a pizza for the house with no door; the house is somebody enormous sitting very still.

One bright sundown street, built here from kit.py's parts (no text anywhere; the only marks are digits on the badge):
- THE HOUSE: a lemon-brick two-storey house with no door, built as one body group (torso, head, roof, chimney, eyes,
  two brass slots) plus two legs and two arms that only show once it stands. Channels (cue "ch", each one restates a
  target, a duration): rise (0 sitting, 1 standing), crack (lawn splits), eyes (window glow), turn (deg), bow (deg),
  flap and mflap (the slot flaps), plight0..3 (porch lights), tiny (the folded twenty).
- THE BADGE: the rule marker, a delivery timer glued to the camera, top left, in every shot (cue "badge").
- THE STREET: four painted houses with porch lights, a far row, a pizza place at the corner, a red car, a dog.
Cues: ch, badge, obj (box, bag, bill, slip, car, dog, box2: place or move them), puff (a chimney puff).
"""

from __future__ import annotations

import math
import tempfile
from pathlib import Path

import bpy
from mathutils import Vector as V

from blocky import acting, bl_story, rig

TMP = Path(tempfile.mkdtemp(prefix="nodoor-"))
FONT = Path(__file__).resolve().parents[2] / "blocky" / "fonts" / "SchibstedGrotesk-Black.ttf"
Y0 = 2.5            # the doorless house: front wall at y 0, body 6 x 5, centred on y 2.5
RISE = 6.4          # how high its legs lift it
_n = [0]


def nm(p):
    _n[0] += 1
    return f"{p}.{_n[0]}"


def ss(x):
    x = min(1.0, max(0.0, x))
    return x * x * (3 - 2 * x)


def lerp(a, b, u):
    return a + (b - a) * u


class K:
    kit = None


def P(hexc, rough=0.5, spec=0.35):
    return K.kit.plastic(hexc, rough, spec=spec)


def B(parent, size, loc, mat, name="b", bevel=0.01, rot=(0, 0, 0)):
    return K.kit.box(nm(name), size, loc, mat, parent, rot, bevel)


def E(parent, loc=(0, 0, 0), name="e", rot=(0, 0, 0)):
    return K.kit.empty(nm(name), loc, parent, rot)


def hide(ob, h=True):
    ob.hide_render = h
    for c in ob.children_recursive:
        c.hide_render = h


def no_shadow(ob):
    try:
        ob.visible_shadow = False
    except Exception:
        pass


def emat(kit, hexc, strength, name=None):
    """A private emission material (so a channel can dim it): returns (material, its Emission node)."""
    m = kit._new(nm(name or "emat"))
    nt = m.node_tree
    nt.nodes.remove(nt.nodes["Principled BSDF"])
    e = nt.nodes.new("ShaderNodeEmission")
    e.inputs["Color"].default_value = kit.col(hexc)
    e.inputs["Strength"].default_value = strength
    out = next(n for n in nt.nodes if n.type == "OUTPUT_MATERIAL")
    nt.links.new(e.outputs[0], out.inputs["Surface"])
    return m, e


# ------------------------------------------------------------------------------------------------ channels
def chan(tl, k, t, default=0.0):
    v = default
    for c in tl.get("cues", []):
        if c["name"] != "ch" or c.get("k") != k:
            continue
        if c["t"] > t + 1e-9:
            break
        dur = c.get("dur", 0.0)
        if dur <= 0 or t >= c["t"] + dur:
            v = c["v"]
        else:
            v = v + (c["v"] - v) * ss((t - c["t"]) / dur)
            break
    return v


def cue_at(tl, name, t, key=None):
    out = {}
    for c in tl.get("cues", []):
        if c["name"] == name and c["t"] <= t + 1e-9 and (key is None or c.get("k") == key):
            out = c
    return out


# ------------------------------------------------------------------------------------------------ pictures
def hexrgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def glyph_slice(d, cx, cy, s, fill, dot):
    """A pizza slice glyph: a point-down triangle with a crust arc and two dots."""
    d.polygon([(cx - s, cy - s * 0.8), (cx + s, cy - s * 0.8), (cx, cy + s * 1.0)], fill=fill)
    d.rounded_rectangle([cx - s * 1.05, cy - s * 1.0, cx + s * 1.05, cy - s * 0.62], radius=int(s * 0.18), fill=fill)
    for dx, dy in ((-0.38, -0.22), (0.3, -0.08), (-0.02, 0.38)):
        r = s * 0.15
        d.ellipse([cx + dx * s - r, cy + dy * s - r, cx + dx * s + r, cy + dy * s + r], fill=dot)


def badge_image(txt, mode):
    from PIL import Image, ImageDraw, ImageFont

    p = TMP / f"badge-{mode}-{txt.replace(':', '_').replace('+', 'p')}.png"
    if p.exists():
        return str(p)
    W, H = 560, 260
    bg = {"norm": "#ff4d2e", "late": "#fff3dc", "ok": "#22b04b"}[mode]
    fg = "#d4141c" if mode == "late" else "#ffffff"
    im = Image.new("RGB", (W, H), hexrgb("#ff4d2e" if mode == "late" else "#fff3dc"))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([14, 14, W - 14, H - 14], radius=84, fill=hexrgb(bg))
    if mode == "ok":
        d.line([(120, 138), (220, 200), (440, 70)], fill=hexrgb("#ffffff"), width=36, joint="curve")
    else:
        glyph_slice(d, 120, 128, 62, hexrgb(fg if mode == "late" else "#fff3dc"), hexrgb(bg))
        f = ImageFont.truetype(str(FONT), 150)
        bb = d.textbbox((0, 0), txt, font=f)
        w_, h_ = bb[2] - bb[0], bb[3] - bb[1]
        k = min(1.0, 330 / w_)
        if k < 1.0:
            f = ImageFont.truetype(str(FONT), int(150 * k))
            bb = d.textbbox((0, 0), txt, font=f)
            w_, h_ = bb[2] - bb[0], bb[3] - bb[1]
        d.text((222 + (330 - w_) / 2 - bb[0], (H - h_) / 2 - bb[1]), txt, fill=hexrgb(fg), font=f)
    im.save(p)
    return str(p)


def lid_image():
    from PIL import Image, ImageDraw

    p = TMP / "lid.png"
    if not p.exists():
        im = Image.new("RGB", (256, 256), hexrgb("#fff3dc"))
        d = ImageDraw.Draw(im)
        glyph_slice(d, 128, 128, 70, hexrgb("#ff4d2e"), hexrgb("#fff3dc"))
        im.save(p)
    return str(p)


def slip_image():
    """The order slip: a doorless house glyph only (a yellow block, a roof, two eyes' windows, no door)."""
    from PIL import Image, ImageDraw

    p = TMP / "slip.png"
    if not p.exists():
        im = Image.new("RGB", (256, 320), hexrgb("#fffaf0"))
        d = ImageDraw.Draw(im)
        d.rectangle([58, 130, 198, 270], fill=hexrgb("#ffd21f"))
        d.polygon([(40, 134), (128, 52), (216, 134)], fill=hexrgb("#7a3f8a"))
        d.rectangle([84, 156, 114, 190], fill=hexrgb("#2b2230"))
        d.rectangle([142, 156, 172, 190], fill=hexrgb("#2b2230"))
        d.rectangle([108, 230, 148, 242], fill=hexrgb("#b8892e"))
        d.rectangle([20, 20, 236, 34], fill=hexrgb("#ff4d2e"))
        im.save(p)
    return str(p)


def img_mat(kit, path, strength=0.9, emit=True):
    m = kit._new(nm("img"))
    nt = m.node_tree
    tex = nt.nodes.new("ShaderNodeTexImage")
    tex.image = bpy.data.images.load(path)
    tex.image.colorspace_settings.name = "sRGB"
    gc = nt.nodes.new("ShaderNodeTexCoord")
    nt.links.new(gc.outputs["UV"], tex.inputs["Vector"])
    b = nt.nodes["Principled BSDF"]
    if emit:
        nt.nodes.remove(b)
        em = nt.nodes.new("ShaderNodeEmission")
        em.inputs["Strength"].default_value = strength
        nt.links.new(tex.outputs["Color"], em.inputs["Color"])
        out = next(n for n in nt.nodes if n.type == "OUTPUT_MATERIAL")
        nt.links.new(em.outputs[0], out.inputs["Surface"])
    else:
        nt.links.new(tex.outputs["Color"], b.inputs["Base Color"])
        b.inputs["Roughness"].default_value = 0.6
    return m, tex


def uv_plane(kit, name, size, loc, mat, parent=None, rot=(0, 0, 0)):
    x, y = size[0] / 2, size[1] / 2
    o = kit.mesh_obj(nm(name), [(-x, -y, 0), (x, -y, 0), (x, y, 0), (-x, y, 0)], [(0, 1, 2, 3)], mat, parent, loc, rot)
    uv = o.data.uv_layers.new(name="UVMap")
    for i, c in enumerate(((0, 0), (1, 0), (1, 1), (0, 1))):
        uv.data[i].uv = c
    return o


# ------------------------------------------------------------------------------------------------ the doorless house
def slot(kit, parent, cx, cz, s, brass, dark, red, name, y=0.0, sz=None):
    """A worn brass slot with a hinged flap, front face at y -0.07. Returns (pivot of the flap, top object)."""
    root = E(parent, (cx, y, cz), name)
    z = s if sz is None else sz
    B(root, (1.0 * s, 0.07, 0.48 * z), (0, -0.03, 0), brass, "plate", 0.015 * min(s, z))
    B(root, (0.72 * s, 0.02, 0.17 * z), (0, -0.07, 0), dark, "mouth", 0.0)
    piv = E(root, (0, -0.088, 0.1 * z), "flap-pivot")
    B(piv, (0.76 * s, 0.018, 0.21 * z), (0, 0, -0.1 * z), brass, "flap", 0.004)
    for i in range(8):                       # the tally (lore): eight tomato-red strokes, never narrated
        B(piv, (0.034 * s, 0.02, 0.16 * z), (-0.31 * s + i * 0.088 * s, -0.012, -0.1 * z), red, "stroke", 0.002)
    return root, piv


def window(kit, parent, x, zc, w, h, white, mat_pane, y=0.0, muntin=False):
    B(parent, (0.14, 0.1, h + 0.28), (x - w / 2 - 0.07, y - 0.04, zc), white, "wf", 0.012)
    B(parent, (0.14, 0.1, h + 0.28), (x + w / 2 + 0.07, y - 0.04, zc), white, "wf", 0.012)
    B(parent, (w + 0.28, 0.1, 0.14), (x, y - 0.04, zc + h / 2 + 0.07), white, "wf", 0.012)
    B(parent, (w + 0.28, 0.12, 0.16), (x, y - 0.05, zc - h / 2 - 0.08), white, "sill", 0.015)
    B(parent, (w, 0.05, h), (x, y - 0.015, zc), mat_pane, "pane", 0.0)
    if muntin:
        B(parent, (w, 0.03, 0.07), (x, y - 0.06, zc), white, "mun", 0.004)
        B(parent, (0.07, 0.03, h), (x, y - 0.06, zc), white, "mun", 0.004)


def build_creature(kit, ctx):
    brick = kit.bricks("#ffe440", "#f5d02a", "#f8e48a", 0.8, rough=0.7, grime_amt=0.12)
    white, plum, red = P("#fffaf0", 0.5), P("#6a3a86", 0.5), P("#c8463a", 0.6)
    brass = P("#c9a24c", 0.35, 0.7)
    dark = P("#241418", 0.9, 0.05)
    tally = P("#ff4d2e", 0.6)
    bodyg = E(None, (0, Y0, 0), "body")
    ctx["body"] = bodyg

    def BB(size, x, y, z, mat, name, bevel=0.02, rot=(0, 0, 0)):
        return B(bodyg, size, (x, y - Y0, z), mat, name, bevel, rot)

    BB((6, 5, 2.5), 0, 2.5, 1.25, brick, "lower", 0.03)
    BB((6, 5, 2.5), 0, 2.5, 3.75, brick, "upper", 0.03)
    BB((6.12, 5.12, 0.16), 0, 2.5, 2.5, white, "band", 0.02)
    BB((6.1, 5.1, 0.2), 0, 2.5, 0.12, white, "base", 0.02)
    # roof: two plum slabs, gable ends in brick, a white edge
    ang = math.atan2(1.8, 2.9)
    for sgn in (-1, 1):
        BB((6.5, 3.5, 0.18), 0, 2.5 + sgn * 1.45, 5.92, plum, "roof", 0.03, rot=(-sgn * ang, 0, 0))
        BB((6.5, 0.2, 0.2), 0, 2.5 + sgn * 2.85, 5.0, white, "eave", 0.03)
    BB((6.5, 0.22, 0.22), 0, 2.5, 6.83, white, "ridge", 0.03)
    verts = [(-2.95, 0.1 - Y0, 5.0), (-2.95, 4.9 - Y0, 5.0), (-2.95, 2.5 - Y0, 6.4),
             (2.95, 0.1 - Y0, 5.0), (2.95, 4.9 - Y0, 5.0), (2.95, 2.5 - Y0, 6.4)]
    kit.mesh_obj(nm("gable"), verts, [(0, 2, 1), (3, 4, 5), (0, 1, 4, 3), (0, 3, 5, 2), (1, 2, 5, 4)], brick, bodyg)
    # chimney, red brick, and the cap
    BB((0.9, 0.9, 1.9), 2.0, 3.6, 6.55, red, "chimney", 0.03)
    BB((1.1, 1.1, 0.14), 2.0, 3.6, 7.55, dark, "chcap", 0.02)
    ctx["chimney"] = (2.0, 3.6 - Y0, 7.65)
    # the eyes: two curtainless top windows, plain until a pupil/pinpoint channel turns them into a face (no brows)
    ctx["panes"] = []
    for sx in (-1, 1):
        m, node = emat(kit, "#ff9d2e", 1.9, "eye")
        ctx["panes"].append(node)
        window(kit, bodyg, sx * 1.7, 3.9, 1.2, 0.95, white, m, y=-Y0)
        pup = kit.cyl(nm("pupil"), 0.13, 0.04, (sx * 1.7, -Y0 - 0.065, 3.9), dark, bodyg, rot=(math.pi / 2, 0, 0), n=16)
        pup.scale = (0.001,) * 3
        ctx.setdefault("pupils", []).append(pup)
        pm, pn = emat(kit, "#fff1c8", 16.0, "pin")
        pin = kit.sphere(nm("pin"), 0.065, (sx * 1.7, -Y0 - 0.07, 3.9), pm, bodyg, seg=10)
        no_shadow(pin)
        pin.scale = (0.001,) * 3
        ctx.setdefault("pins", []).append(pin)
    # pupils/eyes need body-local y (-Y0 offset is for BB only; windows above were placed with y relative to the body origin)
    # the chest: a bay window in the lower storey
    mb, nb = emat(kit, "#ffd890", 1.3, "bay")
    ctx["bay"] = nb
    window(kit, bodyg, 1.6, 1.5, 2.3, 1.2, white, mb, y=-Y0, muntin=True)
    # the low slot, at knee height (sitting), and the mouth (standing, in the upper storey, under the eyes)
    ctx["slot_low"], ctx["flap_low"] = slot(kit, bodyg, -1.5, 0.5, 1.0, brass, dark, tally, "slot-low", -Y0)
    ctx["slot_mouth"], ctx["flap_mouth"] = slot(kit, bodyg, 0.0, 3.0, 2.3, brass, dark, tally, "slot-mouth", -Y0, 1.3)
    B(bodyg, (0.95, 0.24, 0.04), (-1.5, -Y0 - 0.13, 0.21), brass, "tray", 0.01)
    # arms (the side walls unfolding): pivots at the shoulders, hanging
    ctx["arms"] = []
    for sx in (-1, 1):
        piv = E(bodyg, (sx * 3.65, 0, 2.2), "arm")
        B(piv, (1.0, 1.5, 4.0), (0, 0, -2.0), brick, "arm", 0.05)
        B(piv, (1.2, 1.7, 0.45), (0, 0, 0.1), white, "shoulder", 0.05)
        B(piv, (1.1, 1.6, 0.7), (0, 0, -4.15), white, "hand", 0.08)
        ctx["arms"].append((piv, sx))
        hide(piv, True)
    # legs (they show once it stands)
    ctx["legs"] = []
    for sx in (-1, 1):
        g = E(None, (sx * 1.75, Y0, 0), "leg")
        leg = B(g, (1.3, 1.5, 1.0), (0, 0, 0.5), brick, "leg", 0.04)
        knee = B(g, (1.45, 0.5, 0.6), (0, -0.75, 0.5), brick, "knee", 0.1)
        band = B(g, (1.4, 1.6, 0.35), (0, 0, 0.6), white, "cuff", 0.05)
        foot = B(g, (1.5, 2.4, 0.5), (0, -0.4, 0.25), white, "foot", 0.1)
        ctx["legs"].append((g, leg, knee, band))
        hide(g, True)
    # the bare patch it sat on, and the lawn cracks along the knees
    dirt = P("#6a4a30", 0.95, 0.05)
    B(None, (6.3, 5.3, 0.05), (0, Y0, 0.025), dirt, "patch", 0.0)
    ctx["cracks"] = []
    crack_m = P("#3a2618", 0.95, 0.05)
    for sx in (-1, 1):
        c = B(None, (0.3, 2.6, 0.05), (sx * 1.75, -1.35, 0.026), crack_m, "crack", 0.0)
        ctx["cracks"].append(c)
        hide(c, True)
    # chimney puffs
    smat = kit._new(nm("steam"))
    n_ = smat.node_tree
    n_.nodes.remove(n_.nodes["Principled BSDF"])
    tr = n_.nodes.new("ShaderNodeBsdfTransparent")
    em = n_.nodes.new("ShaderNodeEmission")
    em.inputs["Color"].default_value = (1, 1, 1, 1)
    em.inputs["Strength"].default_value = 1.8
    mx = n_.nodes.new("ShaderNodeMixShader")
    mx.inputs["Fac"].default_value = 0.5
    n_.links.new(tr.outputs[0], mx.inputs[1])
    n_.links.new(em.outputs[0], mx.inputs[2])
    out = next(n for n in n_.nodes if n.type == "OUTPUT_MATERIAL")
    n_.links.new(mx.outputs[0], out.inputs["Surface"])
    ctx["puffs"] = []
    for j in range(5):
        o = kit.sphere(nm("puff"), 0.4, (0, 0, 0), smat, bodyg, seg=12)
        no_shadow(o)
        o.hide_render = True
        ctx["puffs"].append(o)


def build_lemon_far(kit):
    """A second lemon house, far off on another street (the sting): sitting, one chimney."""
    brick = kit.bricks("#ffe14d", "#f6d23a", "#fff4b0", 0.8, rough=0.7, grime_amt=0.1)
    white, plum, red = P("#fffaf0"), P("#6a3a86"), P("#c8463a")
    g = E(None, (150, 60, 0), "far-lemon")
    B(g, (6, 5, 5), (0, 2.5, 2.5), brick, "wall", 0.03)
    B(g, (6.12, 5.12, 0.16), (0, 2.5, 2.5), white, "band", 0.02)
    ang = math.atan2(1.8, 2.9)
    for sgn in (-1, 1):
        B(g, (6.5, 3.5, 0.18), (0, 2.5 + sgn * 1.45, 5.92), plum, "roof", 0.03, rot=(-sgn * ang, 0, 0))
    B(g, (0.9, 0.9, 1.9), (2.0, 3.6, 6.55), red, "chimney", 0.03)
    em, _ = emat(kit, "#ffd27a", 2.0, "farwin")
    for sx in (-1, 1):
        B(g, (1.2, 0.05, 1.4), (sx * 1.7, -0.015, 3.9), em, "pane", 0.0)
        B(g, (1.3, 0.04, 1.5), (sx * 1.7, -0.01, 3.9), white, "frame", 0.01)
    B(None, (60, 60, 0.3), (150, 60, -0.15), P("#5fd35a", 0.85, 0.1), "farlawn", 0.0)
    B(None, (60, 8, 0.1), (150, 25, 0.0), P("#8a8f9e", 0.8, 0.1), "farroad", 0.0)
    sm = []
    for j in range(5):
        o = kit.sphere(nm("fpuff"), 0.4, (0, 0, 0), kit.emit("#ffffff", 1.4), g, seg=12)
        no_shadow(o)
        sm.append(o)
    return g, sm


# ------------------------------------------------------------------------------------------------ the street
def painted_house(kit, ctx, x, y, body_c, door_c, roof_c, facing, idx=None):
    """A painted house, front wall at (x, y) facing -y (facing=1) or +y (facing=-1); idx: its porch light."""
    g = E(None, (x, y, 0), "house", rot=(0, 0, 0 if facing == 1 else math.pi))
    white = P("#fffaf0")
    B(g, (6, 4.5, 4.3), (0, 2.25, 2.15), P(body_c, 0.6), "wall", 0.03)
    B(g, (6.1, 4.6, 0.2), (0, 2.25, 0.1), white, "base", 0.02)
    ang = math.atan2(1.6, 2.7)
    for sgn in (-1, 1):
        B(g, (6.5, 3.3, 0.18), (0, 2.25 + sgn * 1.35, 5.1), P(roof_c, 0.5), "roof", 0.03, rot=(-sgn * ang, 0, 0))
    B(g, (6.4, 0.2, 0.16), (0, 2.25, 6.15), white, "ridge", 0.02)
    # door and window
    B(g, (1.3, 0.12, 2.4), (1.4, -0.05, 1.3), white, "doorframe", 0.02)
    B(g, (1.0, 0.1, 2.2), (1.4, -0.1, 1.2), P(door_c, 0.5), "door", 0.02)
    wm, _ = emat(kit, "#ffe0a8", 1.1, "win")
    window(kit, g, -1.5, 2.0, 1.4, 1.3, white, wm, muntin=True)
    # porch: deck, two posts, a small roof, the porch light
    B(g, (2.8, 1.8, 0.24), (1.4, -0.9, 0.12), white, "deck", 0.02)
    B(g, (0.14, 0.14, 2.7), (0.2, -1.7, 1.5), white, "post", 0.02)
    B(g, (0.14, 0.14, 2.7), (2.6, -1.7, 1.5), white, "post", 0.02)
    B(g, (3.0, 2.0, 0.14), (1.4, -0.95, 2.9), P(roof_c, 0.5), "porchroof", 0.02)
    if idx is not None:
        m, node = emat(kit, "#ffc66e", 12.0, "bulb")
        kit.sphere(nm("bulb"), 0.2, (1.4, -0.45, 2.7), m, g, seg=10)
        wp = g.matrix_world @ V((1.4, -0.45, 2.6)) if False else V((x + (1.4 if facing == 1 else -1.4), y - facing * 0.45, 2.6))
        kit.light(f"porch{idx}", "POINT", tuple(wp), 90, "#ffb866", size=0.2, shadow=False)
        ctx["bulbs"][idx] = node
    return g


def picket_fence(kit, x0, x1, y, white):
    n = int((x1 - x0) / 0.5)
    for i in range(n + 1):
        B(None, (0.12, 0.05, 0.95), (x0 + i * 0.5, y, 0.475), white, "picket", 0.01)
    B(None, (x1 - x0, 0.05, 0.07), ((x0 + x1) / 2, y, 0.7), white, "frail", 0.008)
    B(None, (x1 - x0, 0.05, 0.07), ((x0 + x1) / 2, y, 0.25), white, "frail", 0.008)


def build_shop(kit, ctx):
    """The pizza place at the corner (x -40): open window onto a counter, a red door with a warm light, a red awning."""
    X0, W = -40.0, 7.0
    cream, red, redd = P("#f0d8bc"), P("#ff4d2e", 0.5), P("#d93a22", 0.5)
    g = E(None, (X0, 0, 0), "shop")
    # front wall in pieces around the window opening (x -2.4..1.4 from the shop centre, z 0.9..2.5)
    B(g, (1.2, 0.3, 3.6), (-2.9, 0.15, 1.8), cream, "pierL", 0.02)
    B(g, (3.8, 0.3, 0.9), (-0.5, 0.15, 0.45), cream, "under", 0.02)
    B(g, (3.8, 0.3, 1.1), (-0.5, 0.15, 3.05), cream, "over", 0.02)
    B(g, (0.6, 0.3, 3.6), (1.7, 0.15, 1.8), cream, "pierM", 0.02)
    B(g, (1.7, 0.3, 1.3), (2.65, 0.15, 2.95), cream, "overdoor", 0.02)
    B(g, (1.5, 0.3, 2.3), (2.75, 0.15, 1.15), cream, "doorwall", 0.0)
    B(g, (1.0, 0.12, 2.2), (2.45, -0.04, 1.1), red, "door", 0.02)
    # counter: the window sill carries on inside as a counter top
    B(g, (4.0, 1.1, 0.12), (-0.5, 0.55, 1.0), P("#f4d9a8", 0.5), "counter", 0.01)
    B(g, (4.0, 1.0, 1.0), (-0.5, 0.6, 0.5), redd, "counterbody", 0.02)
    # awning: alternating red and cream stripes sloping out over the window
    for i in range(8):
        B(g, (0.9, 1.2, 0.1), (-3.2 + i * 0.9 + 0.45 - 0.3, -0.5, 3.15), red if i % 2 == 0 else cream, "awn", 0.01, rot=(0.25, 0, 0))
    # warm bulb over the door
    m, node = emat(kit, "#ffc66e", 4.0, "shopbulb")
    kit.sphere(nm("sb"), 0.14, (2.45, -0.3, 2.55), m, g, seg=10)
    kit.light("shopdoor", "POINT", (X0 + 2.45, -0.5, 2.4), 35, "#ffb866", size=0.2, shadow=False)
    # interior
    B(g, (W, 6.0, 0.1), (0, 3.0, -0.05), kit.checker("#ff4d2e", "#fff3dc", 2.0), "floor", 0.0)
    B(g, (W, 0.3, 3.6), (0, 6.15, 1.8), cream, "back", 0.0)
    B(g, (0.3, 6.0, 3.6), (-W / 2 - 0.15, 3.0, 1.8), cream, "sideL", 0.0)
    B(g, (0.3, 6.0, 3.6), (W / 2 + 0.15, 3.0, 1.8), cream, "sideR", 0.0)
    B(g, (W + 0.6, 6.4, 0.2), (0, 3.0, 3.7), redd, "roof", 0.02)
    om, _ = emat(kit, "#ff9a3c", 2.4, "oven")
    B(g, (2.0, 0.1, 1.2), (-1.5, 5.95, 1.4), om, "oven", 0.0)
    B(g, (2.4, 0.5, 1.2), (-1.5, 5.6, 0.6), P("#6b5a52", 0.7), "ovenbase", 0.02)
    kit.light("shopin", "POINT", (X0, 2.8, 3.1), 700, "#fff0d8", size=0.5)
    # the shop's sides and the corner: a hedge and a lamp
    return g


def build_car(kit):
    g = E(None, (0, 0, -50), "car")
    red, dk, wh = P("#ff4d2e", 0.4, 0.5), P("#2b2230", 0.8), P("#fff3dc", 0.5)
    B(g, (1.9, 4.2, 0.55), (0, 0, 0.62), red, "body", 0.12)
    B(g, (1.9, 1.5, 0.35), (0, -1.3, 0.97), red, "hood", 0.1)
    B(g, (1.9, 0.9, 0.45), (0, 1.5, 1.0), red, "trunk", 0.1)
    B(g, (1.7, 0.1, 0.1), (0, -0.45, 1.25), wh, "wind", 0.03)
    ctx_w = []
    for sx in (-1, 1):
        for sy in (-1, 1):
            w = kit.cyl(nm("wheel"), 0.4, 0.3, (sx * 0.97, sy * 1.3, 0.4), dk, g, rot=(0, math.pi / 2, 0), n=16)
            kit.cyl(nm("hub"), 0.2, 0.32, (sx * 0.97, sy * 1.3, 0.4), wh, g, rot=(0, math.pi / 2, 0), n=12)
            ctx_w.append(w)
    g["wheels"] = [w.name for w in ctx_w]
    return g


def build_dog(kit):
    g = E(None, (0, 0, -50), "dog")
    tan, dk = P("#d9a05b", 0.7), P("#6b4a2e", 0.7)
    B(g, (0.3, 0.7, 0.3), (0, 0, 0.45), tan, "body", 0.06)
    B(g, (0.26, 0.28, 0.26), (0, -0.46, 0.6), tan, "head", 0.06)
    B(g, (0.14, 0.14, 0.12), (0, -0.62, 0.55), dk, "snout", 0.03)
    B(g, (0.06, 0.06, 0.2), (0, 0.4, 0.62), tan, "tail", 0.02, rot=(0.7, 0, 0))
    for sx in (-1, 1):
        for sy in (-1, 1):
            B(g, (0.09, 0.09, 0.32), (sx * 0.1, sy * 0.25, 0.16), dk, "leg", 0.02)
        B(g, (0.06, 0.1, 0.16), (sx * 0.13, -0.42, 0.74), dk, "ear", 0.02)
    return g


def build_props(kit):
    pr = {}
    kraft = P("#fff3dc", 0.7, 0.1)
    # the pizza box: kraft, with the slice glyph on the lid
    g = E(None, (0, 0, -50), "box")
    B(g, (0.5, 0.5, 0.06), (0, 0, 0), kraft, "boxbase", 0.01)
    lm, _ = img_mat(kit, lid_image(), 0.9, emit=False)
    uv_plane(kit, "lid", (0.46, 0.46), (0, 0, 0.0305), lm, g)
    pr["box"] = g
    # the red insulated bag
    g = E(None, (0, 0, -50), "bag")
    B(g, (0.5, 0.2, 0.5), (0, 0, 0), P("#ff4d2e", 0.5), "bag", 0.04)
    B(g, (0.36, 0.04, 0.12), (0, 0, 0.3), P("#d93a22", 0.5), "bagstrap", 0.01)
    pr["bag"] = g
    # the folded twenty: a flat green bill, and the tiny house it folds into
    g = E(None, (0, 0, -50), "bill")
    B(g, (0.34, 0.15, 0.006), (0, 0, 0), P("#6bc77a", 0.6), "bill", 0.002)
    B(g, (0.08, 0.1, 0.004), (0, 0, 0.0045), P("#4fa95d", 0.6), "billmark", 0.001)
    pr["bill"] = g
    g = E(None, (0, 0, -50), "tiny")
    gm, gd, gr = P("#5fc46f", 0.5), P("#2f7d3e", 0.6), P("#3f9a50", 0.5)
    B(g, (0.13, 0.1, 0.08), (0, 0, 0.04), gm, "tbody", 0.004)
    for sgn in (-1, 1):
        B(g, (0.15, 0.08, 0.012), (0, sgn * 0.035, 0.1), gr, "troof", 0.002, rot=(-sgn * 0.8, 0, 0))
    verts = [(-0.065, -0.05, 0.08), (-0.065, 0.05, 0.08), (-0.065, 0, 0.14), (0.065, -0.05, 0.08), (0.065, 0.05, 0.08), (0.065, 0, 0.14)]
    kit.mesh_obj(nm("tgable"), verts, [(0, 2, 1), (3, 4, 5), (0, 3, 5, 2), (1, 2, 5, 4)], gm, g)
    B(g, (0.03, 0.012, 0.045), (0, -0.054, 0.027), gd, "tdoor", 0.002)
    B(g, (0.028, 0.012, 0.028), (-0.04, -0.054, 0.05), gd, "twin", 0.002)
    pr["tiny"] = g
    # the order slip
    g = E(None, (0, 0, -50), "slip")
    sm, _ = img_mat(kit, slip_image(), 0.9, emit=False)
    uv_plane(kit, "slipface", (0.2, 0.25), (0, 0, 0.004), sm, g)
    B(g, (0.2, 0.25, 0.006), (0, 0, 0), P("#fffaf0", 0.8), "slipback", 0.0)
    pr["slip"] = g
    g = E(None, (0, 0, -50), "slip2")
    uv_plane(kit, "slipface2", (0.2, 0.25), (0, 0, 0.004), sm, g)
    B(g, (0.2, 0.25, 0.006), (0, 0, 0), P("#fffaf0", 0.8), "slipback2", 0.0)
    pr["slip2"] = g
    # the second pizza, open: base, a hinged lid, a plain pie
    g = E(None, (0, 0, -50), "box2")
    B(g, (0.52, 0.52, 0.05), (0, 0, 0), kraft, "b2base", 0.01)
    kit.cyl(nm("crust"), 0.22, 0.03, (0, 0, 0.04), P("#e8a448", 0.7), g, n=24)
    kit.cyl(nm("cheese"), 0.19, 0.034, (0, 0, 0.042), P("#ffd36b", 0.5), g, n=24)
    lid = E(g, (0, 0.26, 0.02), "b2hinge", rot=(1.9, 0, 0))
    B(lid, (0.52, 0.5, 0.025), (0, -0.25, 0), kraft, "b2lid", 0.008)
    pr["box2"] = g
    return pr


# ------------------------------------------------------------------------------------------------ build
def build(kit, story, tl):
    K.kit = kit
    ctx = {"story": story, "bulbs": {}}
    ctx["shots"] = {s["id"]: s for s in story["shots"]}
    sc = bpy.context.scene

    # ---- sky: hot sunset gradient, horizon orange to a purple top
    nt = sc.world.node_tree
    bg = nt.nodes["Background"]
    tc = nt.nodes.new("ShaderNodeTexCoord")
    sep = nt.nodes.new("ShaderNodeSeparateXYZ")
    nt.links.new(tc.outputs["Generated"], sep.inputs[0])
    mr = nt.nodes.new("ShaderNodeMapRange")
    mr.inputs["From Min"].default_value = 0.0
    mr.inputs["From Max"].default_value = 0.6
    mr.clamp = True
    nt.links.new(sep.outputs["Z"], mr.inputs["Value"])
    ramp = nt.nodes.new("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].position = 0.0
    ramp.color_ramp.elements[1].position = 1.0
    ramp.color_ramp.elements.new(0.25)
    ramp.color_ramp.elements.new(0.6)
    nt.links.new(mr.outputs["Result"], ramp.inputs["Fac"])
    nt.links.new(ramp.outputs["Color"], bg.inputs["Color"])
    for el, c in zip(ramp.color_ramp.elements, ("#ffa04a", "#ff6a7e", "#d94a9e", "#7b44c0")):
        r, g_, b_ = (int(c[i:i + 2], 16) / 255 for i in (1, 3, 5))
        el.color = (kit.srgb(r), kit.srgb(g_), kit.srgb(b_), 1.0)
    bg.inputs["Strength"].default_value = 0.85

    # ---- lights: the low sun behind the house (a hot pink-orange rim), a front key, a camera fill
    def sun(name, az, el, energy, hexc):
        o = kit.light(name, "SUN", (0, 0, 50), energy, hexc, size=0.1)
        o.data.angle = 0.05
        a, e = math.radians(az), math.radians(el)
        pos = V((math.sin(a) * math.cos(e), -math.cos(a) * math.cos(e), math.sin(e)))
        o.rotation_euler = (-pos).to_track_quat("-Z", "Y").to_euler()
        return o

    sun("sunset", 180, 9, 6.5, "#ff8a5a")
    sun("key", -28, 38, 1.7, "#fff4e4")
    sun("rim", 160, 22, 5.0, "#ff6fb0")
    kit.light("uplight", "POINT", (0, -5.5, 0.3), 1800, "#ffb878", size=0.4, shadow=False)
    ctx["fill"] = kit.light("camfill", "SUN", (0, 0, 2), 1.3, "#ffe9cf", size=0.1, shadow=False)
    kit.light("slotglow", "POINT", (-1.5, -0.3, 0.45), 14, "#ffb866", size=0.1, shadow=False)
    # the low red sun itself, a disc behind the house
    sm, _ = emat(kit, "#ffd89a", 5.0, "sundisc")
    d = kit.cyl("sundisc", 9, 0.2, (14, 120, 9), sm, None, rot=(math.pi / 2, 0, 0), n=40)
    no_shadow(d)

    # ---- ground
    kit.box("lawn", (400, 200, 0.4), (0, 90, -0.2), P("#5fd35a", 0.85, 0.1), None, (0, 0, 0), 0.0)
    B(None, (400, 7.6, 0.1), (0, -10.2, 0.0), kit.texture("asphalt", 0.4, tint="#8f8aa8"), "road", 0.0)
    kit.box("lawn2", (400, 60, 0.4), (0, -47, -0.2), P("#5fd35a", 0.85, 0.1), None, (0, 0, 0), 0.0)
    B(None, (400, 2.4, 0.16), (0, -5.0, 0.04), P("#b4ada3", 0.8), "walk", 0.0)
    B(None, (400, 0.3, 0.3), (0, -6.28, 0.15), P("#9a948b", 0.8), "curb", 0.0)
    B(None, (400, 3.0, 0.16), (0, -15.5, 0.04), P("#b4ada3", 0.8), "walk2", 0.0)
    for x in range(-60, 60, 6):                                   # lane dashes
        B(None, (2.2, 0.16, 0.02), (x, -10.2, 0.06), P("#fff3dc", 0.8), "dash", 0.0)

    # ---- the creature, the neighbours, the shop
    build_creature(kit, ctx)
    ctx["far"] = build_lemon_far(kit)
    specs = ((-10, "#8de3c4", "#ff4d2e", "#6a3a86", 0), (-20, "#c9a8ff", "#ffd21f", "#4a6fd0", 1),
             (-30, "#8ec9ff", "#ff4d2e", "#6a3a86", 2), (22, "#ffc9a0", "#3fa5ff", "#4a6fd0", 3))
    white = P("#fffaf0")
    for x, bc, dc, rc, idx in specs:
        painted_house(kit, ctx, x, 0, bc, dc, rc, 1, idx)
        picket_fence(kit, x - 4.9, x - 1.1, -3.7, white)
        picket_fence(kit, x + 1.1, x + 4.9, -3.7, white)
    for x, bc, dc, rc in ((-32, "#ffe0a0", "#ff4d2e", "#6a3a86"), (-14, "#ffc4d6", "#3fa5ff", "#4a6fd0"), (4, "#8de3c4", "#ffd21f", "#6a3a86"),
                          (22, "#c9a8ff", "#ff4d2e", "#4a6fd0"), (-48, "#8ec9ff", "#ffd21f", "#6a3a86")):
        painted_house(kit, ctx, x, -19.5, bc, dc, rc, -1, None)
    painted_house(kit, ctx, 40, 0, "#8ec9ff", "#ffd21f", "#6a3a86", 1, None)
    painted_house(kit, ctx, -50, 0, "#c9a8ff", "#ffd21f", "#4a6fd0", 1, None)
    build_shop(kit, ctx)
    B(None, (3.4, 0.7, 0.45), (0.5, -5.75, 0.225), P("#a8a29a", 0.8), "ledge", 0.02)
    # hydrant, trees
    B(None, (0.34, 0.34, 0.6), (6.5, -4.4, 0.4), P("#ff4d2e", 0.4), "hydrant", 0.06)
    B(None, (0.46, 0.46, 0.1), (6.5, -4.4, 0.75), P("#d93a22", 0.4), "hydrantcap", 0.04)
    for nme, x, y, h in (("commontree_1", -5.5, 9, 7), ("commontree_2", 6.0, 10, 7.5), ("birchtree_1", -17, 8, 7.5),
                         ("commontree_1", 18, 9, 7), ("birchtree_1", -26, 9, 7.5), ("commontree_2", -36, 10, 7)):
        try:
            kit.prop(nme, (x, y, 0), rot=x * 17, height=h, tint="#9be05a" if "common" in nme else "#d4f0a8")
        except Exception:
            pass
    for x, y in ((-6.5, -2.4), (6.8, -2.2), (-16, -2.2), (16, -2.2), (-26, -2.4)):
        try:
            kit.prop("bush_1", (x, y, 0), rot=x * 9, height=1.1, tint="#58c24a")
        except Exception:
            pass

    # ---- movers
    ctx["car"] = build_car(kit)
    ctx["dog"] = build_dog(kit)
    ctx["props"] = build_props(kit)
    build_badge(kit, ctx)
    return ctx


# ------------------------------------------------------------------------------------------------ the badge
def build_badge(kit, ctx):
    cam = kit.OBJ["cam"]
    m, tex = img_mat(kit, badge_image("6:00", "norm"), 1.0, emit=True)
    ctx["badge_nodes"] = (m, tex)
    pl = uv_plane(kit, "badge", (1.0, 1.0), (0, 0, -0.15), m, cam)
    no_shadow(pl)
    ctx["badge"] = pl
    ctx["badge_imgs"] = {}


def place_badge(kit, ctx, lens, txt, mode):
    key = (txt, mode)
    if key not in ctx["badge_imgs"]:
        im = bpy.data.images.load(badge_image(txt, mode))
        im.colorspace_settings.name = "sRGB"
        ctx["badge_imgs"][key] = im
    ctx["badge_nodes"][1].image = ctx["badge_imgs"][key]
    d = 0.15
    unit = d / lens
    pw = 4.3 * unit
    ph = pw * 260 / 560
    pl = ctx["badge"]
    pl.location, pl.scale = (-3.3 * unit, 8.55 * unit, -d), (pw, ph, 1)


# ------------------------------------------------------------------------------------------------ animate
def animate(kit, story, tl, t, ctx):
    sc = bpy.context.scene
    shots = tl["shots"]
    cur = next((s for s in shots if s["start"] <= t < s["end"]), shots[-1])
    sd = ctx["shots"][cur["id"]]
    cl, ctg, lens, _ = bl_story.cam_at(sd, cur, t, {}, tl)
    ctx["fill"].rotation_euler = (V(ctg) - V(cl)).to_track_quat("-Z", "Y").to_euler()
    ov = {"slotglow": chan(tl, "glow", t, 0.15), "camfill": sd.get("fill", 1.0)}
    sc.view_settings.exposure = sd.get("exp", 0.0)
    # ---- channels
    rise, crack = chan(tl, "rise", t), chan(tl, "crack", t)
    eyes, turn, bow = chan(tl, "eyes", t, 1.0), chan(tl, "turn", t), chan(tl, "bow", t)
    shift = chan(tl, "shift", t) * 8.0
    ctx["body"].location = (shift, Y0, RISE * rise)
    ctx["body"].rotation_euler = (math.radians(bow + 5.0 * ss(rise)), 0, math.radians(turn))
    H = RISE * rise
    for g, leg, knee, band in ctx["legs"]:
        vis = rise > 0.02
        hide(g, not vis)
        if vis:
            g.location.x = (-1.75 if leg.name == ctx["legs"][0][1].name else 1.75) + shift
            leg.scale = (1, 1, max(H, 0.05))
            knee.location = (0, -0.75, max(H * 0.52, 0.2))
            band.location = (0, 0, 0.6)
    au = ss((rise - 0.45) / 0.55)
    swing = math.sin(t * 0.9) * 0.025
    for piv, sx in ctx["arms"]:
        hide(piv, au < 0.03)
        piv.scale = (1, 1, max(au, 0.02))
        piv.rotation_euler = (0, -sx * ((1 - au) * 0.9 + 0.05) + swing * sx, 0)
    for c in ctx["cracks"]:
        hide(c, crack < 0.02)
        c.scale = (max(crack * 1.6, 0.02), 1.0, 1.0)
    low_vis = 1.0 - ss(rise / 0.15)
    mouth_vis = ss((rise - 0.3) / 0.25)
    for root, v in ((ctx["slot_low"], low_vis), (ctx["slot_mouth"], mouth_vis)):
        hide(root, v < 0.02)
        root.scale = (max(v, 0.01),) * 3
    ctx["slot_low"].location = (-1.5, -Y0, 0.5)
    ctx["slot_mouth"].location = (0.0, -Y0, 3.0)
    for k, piv in (("flap", ctx["flap_low"]), ("mflap", ctx["flap_mouth"])):
        piv.rotation_euler = (-0.55 * chan(tl, k, t), 0, 0)
    for node in ctx["panes"]:
        node.inputs["Strength"].default_value = 1.9 * eyes
    for key, objs_ in (("pupil", ctx["pupils"]), ("pin", ctx["pins"])):
        v = max(chan(tl, key, t), 0.001)
        for o in objs_:
            o.scale = (v, v, v)
    rs = ss(rise / 0.6)
    ov["uplight"] = rs * chan(tl, "up", t, 1.0)
    ov["rim"] = rs
    ov["camfill"] = sd.get("fill", 1.0) * (1.0 - 0.8 * rs)
    ov["key"] = 1.0 - 0.7 * rs
    ov["sunset"] = 1.0 + 0.4 * rs
    sc.view_settings.exposure = sd.get("exp", 0.0) - 0.45 * rs
    # ---- chimney puffs: each "puff" cue is a 1.8 s plume
    cx, cy, cz = ctx["chimney"]
    used = 0
    for c in tl.get("cues", []):
        if c["name"] != "puff":
            continue
        u = (t - c["t"]) / 1.8
        if 0 <= u <= 1:
            for j, o in enumerate(ctx["puffs"]):
                uj = u - j * 0.1
                if 0 <= uj <= 1:
                    env = math.sin(math.pi * uj) ** 0.8
                    o.hide_render = False
                    o.location = (cx + 0.35 * uj + 0.08 * math.sin(j * 2.1 + uj * 4), cy, cz + 0.2 + 1.9 * uj)
                    s = (0.35 + 0.7 * uj) * env + 0.001
                    o.scale = (s, s, s)
                else:
                    o.hide_render = True
            used = 1
            break
    if not used:
        for o in ctx["puffs"]:
            o.hide_render = True
    # ---- the far lemon house's puffs (the sting)
    far, fpuffs = ctx["far"]
    for j, o in enumerate(fpuffs):
        uj = ((t * 0.5) % 1.0) - j * 0.1
        if 0 <= uj <= 1:
            env = math.sin(math.pi * uj) ** 0.8
            o.hide_render = False
            o.location = (2.35 + 0.35 * uj, 3.6, 7.8 + 1.9 * uj)
            s = (0.35 + 0.7 * uj) * env + 0.001
            o.scale = (s, s, s)
        else:
            o.hide_render = True
    # ---- porch lights
    for i, node in ctx["bulbs"].items():
        v = chan(tl, f"plight{i}", t, 1.0)
        node.inputs["Strength"].default_value = 12.0 * v
        ov[f"porch{i}"] = v
    # ---- the badge
    bd = cue_at(tl, "badge", t)
    place_badge(kit, ctx, lens, bd.get("txt", "6:00"), bd.get("mode", "norm"))
    # ---- objects: the box, bag, bill, tiny house, slip, second box, car, dog
    objs = {}
    for c in tl.get("cues", []):
        if c["name"] == "obj" and c["t"] <= t + 1e-9:
            objs[c["k"]] = c
    for k in ("box", "bag", "bill", "tiny", "slip", "slip2", "box2"):
        o = ctx["props"][k]
        c = objs.get(k)
        if not c or not c.get("on", True):
            hide(o, True)
            continue
        hide(o, False)
        pos = c["pos"]
        if "to" in c:
            u = ss((t - c["t"]) / max(1e-3, c["dur"]))
            pos = [lerp(a, b, u) for a, b in zip(pos, c["to"])]
        yaw = c.get("yaw", 0.0)
        if c.get("follow"):
            s = acting.state(tl, c["follow"], t)
            a = math.radians(s["yaw"])
            dx, dy, dz = c["off"]
            pos = [s["x"] + dx * math.cos(a) - dy * math.sin(a), s["y"] + dx * math.sin(a) + dy * math.cos(a), s["z"] + dz]
            yaw = s["yaw"] + c.get("yaw", 0.0)
        o.location = tuple(pos)
        o.rotation_euler = (math.radians(c.get("pitch", 0.0)), 0, math.radians(yaw))
        sc_ = c.get("scale", 1.0)
        o.scale = (sc_, sc_, sc_)
    car = ctx["car"]
    c = objs.get("car")
    if c and c.get("on", True):
        hide(car, False)
        pos = c["pos"]
        if "to" in c:
            u = ss((t - c["t"]) / max(1e-3, c["dur"]))
            pos = [lerp(a, b, u) for a, b in zip(pos, c["to"])]
        car.location = (pos[0], pos[1], 0)
        car.rotation_euler = (0, 0, math.radians(c.get("yaw", 90)))
        for i, wn in enumerate(car["wheels"]):
            w = bpy.data.objects[wn]
            flat = c.get("flat", False) and i == 2
            w.scale = (0.7, 0.7, 1.0) if flat else (1, 1, 1)
            w.location.z = 0.3 if flat else 0.4
    else:
        hide(car, True)
    dog = ctx["dog"]
    c = objs.get("dog")
    if c and c.get("on", True):
        hide(dog, False)
        pos = c["pos"]
        if "to" in c:
            u = ss((t - c["t"]) / max(1e-3, c["dur"]))
            pos = [lerp(a, b, u) for a, b in zip(pos, c["to"])]
        dog.location = (pos[0], pos[1], 0.03 * abs(math.sin(t * 9)))
        dog.rotation_euler = (0, 0, math.radians(c.get("yaw", 0)))
    else:
        hide(dog, True)
    return ov
