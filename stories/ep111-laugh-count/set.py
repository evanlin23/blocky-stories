"""ep111-laugh-count: a bright bowling alley on league night.

Metres, z up, cameras look +y. Foyer y -3..-10 (shoe rental at x -5.5, snack bar at x +5.5), approach y -1.5..1.5, five
glossy maple lanes (centres x -5.2 .. 5.2, ours is x 0) from y 1.5 to 19 with pins at 17.5..19 and a neon bulkhead.
No text anywhere: scoreboards carry numerals and cells only.
The rule marker: a chunky white number on a navy plate with a coloured glow rim floating over every head (billboard
to the camera), and a cream tag glued to the camera's top left that mirrors Bev's number with a bar filling toward 500.
Cues (each restates its whole state): n_<who> {v}, gray {g, dur}, ball {mode hold|roll|off}, shoe, pins, stool, shoes.
"""

from __future__ import annotations

import math
import tempfile
from pathlib import Path

import bpy
from mathutils import Vector as V

from blocky import bl_story, rig

TMP = Path(tempfile.mkdtemp(prefix="laughcount-"))
PINK, TEAL, CORAL = "#ff5fa2", "#2fe0d0", "#ff6f61"
RIM = {"me": "#2fe0d0", "bev": "#ff6f61", "earl": "#ff5fa2", "lanefour": "#c8c8c8", "wait": "#ff5fa2",
       "b1": "#ffd21a", "b2": "#7fd16a"}
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


def P(h, rough=0.45, spec=0.4):
    return K.kit.plastic(h, rough, spec=spec)


def M(h, rough=0.25):
    return K.kit.metal(h, rough)


def B(parent, size, loc, mat, name="b", bevel=0.006, rot=(0, 0, 0)):
    return K.kit.box(nm(name), size, loc, mat, parent, rot, bevel)


def CY(parent, r, h, loc, mat, name="c", rot=(0, 0, 0), n=24, r2=None):
    return K.kit.cyl(nm(name), r, h, loc, mat, parent, rot, n, r2)


def noshadow(ob):
    try:
        ob.visible_shadow = False
    except Exception:
        pass


def hide(ob, h=True):
    ob.hide_render = h
    for c in ob.children_recursive:
        c.hide_render = h


def cue_at(tl, name, t):
    out = {}
    for c in tl.get("cues", []):
        if c["name"] == name and c["t"] <= t + 1e-9:
            out = c
    return out


# ---------------------------------------------------------------------------------------------- images
def make_images():
    from PIL import Image, ImageDraw, ImageFont
    try:
        f = ImageFont.truetype("DejaVuSans-Bold.ttf", 44)
    except Exception:
        f = ImageFont.load_default()
    # scoreboard: cells with numerals and shapes
    W, Hh = 1024, 512
    im = Image.new("RGB", (W, Hh), (14, 22, 70))
    d = ImageDraw.Draw(im)
    for i in range(10):
        x0 = 20 + i * 98
        d.rectangle([x0, 60, x0 + 90, 250], outline=(255, 95, 162), width=6)
        d.rectangle([x0, 60, x0 + 90, 120], outline=(47, 224, 208), width=4)
        d.text((x0 + 14, 66), str((i * 7) % 10), fill=(255, 235, 120), font=f)
        d.text((x0 + 14, 150), str((i * 3 + 4) % 10 * 10 // 3), fill=(255, 255, 255), font=f)
    for i in range(10):
        x0 = 20 + i * 98
        d.ellipse([x0 + 20, 300, x0 + 70, 350], fill=(255, 95, 162) if i % 2 else (47, 224, 208))
        d.polygon([(x0 + 45, 380), (x0 + 15, 440), (x0 + 75, 440)], fill=(255, 210, 26))
    im.save(TMP / "score.png")
    # cubbies: a wall of shoe cubbies, red and blue
    cw, ch, cols, rows = 128, 128, 8, 3
    cb = Image.new("RGB", (cw * cols, ch * rows), (250, 240, 220))
    d = ImageDraw.Draw(cb)
    for r in range(rows):
        for c in range(cols):
            x0, y0 = c * cw, r * ch
            d.rectangle([x0 + 6, y0 + 6, x0 + cw - 6, y0 + ch - 6], fill=(74, 62, 120))
            col = (230, 64, 58) if (r + c) % 2 == 0 else (60, 120, 230)
            d.rounded_rectangle([x0 + 16, y0 + 62, x0 + 62, y0 + 104], 8, fill=col)
            d.rounded_rectangle([x0 + 68, y0 + 62, x0 + 112, y0 + 104], 8, fill=col)
    cb.save(TMP / "cubby.png")
    return str(TMP / "score.png"), str(TMP / "cubby.png")


def img_mat(kit, path, strength=1.0):
    m = kit._new(nm("img"))
    nt = m.node_tree
    nt.nodes.remove(nt.nodes["Principled BSDF"])
    tex = nt.nodes.new("ShaderNodeTexImage")
    tex.image = bpy.data.images.load(path)
    tc = nt.nodes.new("ShaderNodeTexCoord")
    nt.links.new(tc.outputs["Generated"], tex.inputs["Vector"])
    em = nt.nodes.new("ShaderNodeEmission")
    em.inputs["Strength"].default_value = strength
    nt.links.new(tex.outputs["Color"], em.inputs["Color"])
    nt.links.new(em.outputs[0], next(n for n in nt.nodes if n.type == "OUTPUT_MATERIAL").inputs["Surface"])
    return m


def text_obj(kit, parent, size, mat, name="txt"):
    cu = bpy.data.curves.new(nm(name), "FONT")
    cu.size = size
    cu.align_x = "CENTER"
    cu.align_y = "CENTER"
    cu.body = "0"
    cu.materials.append(mat)
    ob = bpy.data.objects.new(nm(name), cu)
    kit.link(ob, parent)
    noshadow(ob)
    return ob


# ---------------------------------------------------------------------------------------------- the alley
def pin(parent, x, y):
    e = K.kit.empty(nm("pin"), (x, y, 0.0), parent)
    white = P("#f7f7f2", 0.25, 0.6)
    CY(e, 0.062, 0.28, (0, 0, 0.14), white, "pb", n=14, r2=0.045)
    CY(e, 0.036, 0.1, (0, 0, 0.33), white, "pn", n=14, r2=0.05)
    CY(e, 0.052, 0.02, (0, 0, 0.3), P("#e0443a", 0.4), "ps", n=14)
    return e


def build_alley(kit, ctx):
    maple = P("#f2b872", 0.16, 0.7)
    dark = P("#3a2a4a", 0.5)
    B(None, (30, 17, 0.1), (0, -9.5 + 0, -0.05), kit.checker("#fbfbf8", "#9fe3dc", 1.5), "foyer", 0.0)
    B(None, (30, 3.2, 0.1), (0, 0.0, -0.05), P("#e9a95f", 0.18, 0.6), "approach", 0.0)
    for c in (-5.2, -2.6, 0.0, 2.6, 5.2):
        B(None, (2.0, 17.6, 0.1), (c, 10.3, -0.05), maple, "lane", 0.0)
        B(None, (2.0, 0.04, 0.02), (c, 1.5, 0.005), dark, "foul", 0.0)
        for k in (-0.5, 0.0, 0.5):
            B(None, (0.1, 0.5, 0.01), (c + k, 5.0 - abs(k) * 2.0, 0.004), P("#9a5a2a", 0.4), "arrow", 0.0)
        B(None, (2.0, 2.0, 0.05), (c, 19.2, -0.02), P("#e8d8c0", 0.4), "deck", 0.0)
    for gx in (-6.5, -3.9, -1.3, 1.3, 3.9, 6.5):
        B(None, (0.6, 17.6, 0.1), (gx, 10.3, -0.12), dark, "gutter", 0.0)
    # walls, bulkhead and neon
    teal, mint = P("#35c9bd", 0.5), P("#bdf0ea", 0.55)
    B(None, (30, 0.3, 5.5), (0, 21.3, 2.7), teal, "bulk", 0.0)
    B(None, (0.3, 34, 5.5), (-14.5, 4.5, 2.7), mint, "wallL", 0.0)
    B(None, (0.3, 34, 5.5), (14.5, 4.5, 2.7), mint, "wallR", 0.0)
    B(None, (30, 0.3, 5.5), (0, -17.5, 2.7), mint, "wallB", 0.0)
    for z, h in ((1.6, PINK), (2.1, TEAL), (4.6, PINK)):
        B(None, (30, 0.03, 0.12), (0, 21.12, z), kit.emit(h, 2.2), "neon", 0.0)
    for sx in (-14.34, 14.34):
        B(None, (0.03, 34, 0.12), (sx, 4.5, 2.4), kit.emit(PINK, 2.0), "neonw", 0.0)
        B(None, (0.03, 34, 0.12), (sx, 4.5, 1.9), kit.emit(TEAL, 2.0), "neonw", 0.0)
    score, cubby = make_images()
    sm = img_mat(kit, score, 1.1)
    for c in (-5.2, -2.6, 0.0, 2.6, 5.2):
        pl = kit.plane(nm("score"), (2.3, 1.15), (c, 20.9, 3.5), sm, None, rot=(math.pi / 2, 0, 0))
        noshadow(pl)
        B(None, (2.45, 0.08, 1.3), (c, 21.0, 3.5), M("#cfd6dc", 0.3), "scoreframe", 0.02)
    # pins: ten per lane, ours in a group the cue topples
    ctx["pins"] = []
    for c in (-5.2, -2.6, 0.0, 2.6, 5.2):
        for r, row in enumerate((1, 2, 3, 4)):
            for i in range(row):
                x = c + (i - (row - 1) / 2) * 0.3
                y = 17.9 + r * 0.26
                e = pin(None, x, y)
                if c == 0.0:
                    ctx["pins"].append((e, x, y, len(ctx["pins"])))
    # ball returns (hoods) between lanes, the lore tally on our left one
    for hx in (-1.3, 1.3):
        B(None, (0.58, 1.0, 0.46), (hx, -0.2, 0.23), M("#d9e1e8", 0.2), "hood", 0.04)
        CY(None, 0.3, 0.9, (hx, -0.2, 0.46), M("#e6eef4", 0.18), "hoodtop", rot=(math.pi / 2, 0, 0), n=20)
    B(None, (0.07, 0.02, 0.34), (-1.42, 0.31, 0.29), P(CORAL, 0.4), "tally", 0.002)
    B(None, (0.07, 0.02, 0.34), (-1.2, 0.31, 0.29), P(CORAL, 0.4), "tally", 0.002)
    # scoring desk where Bev stands, with a rail
    B(None, (2.0, 0.7, 0.95), (-3.0, -3.0, 0.475), P("#35c9bd", 0.4), "desk", 0.02)
    B(None, (2.1, 0.8, 0.06), (-3.0, -3.0, 0.97), P("#fbfbf8", 0.3), "desktop", 0.02)
    # shoe rental: counter, cubbies wall, a spray can
    B(None, (4.2, 0.8, 1.0), (-5.5, -7.4, 0.5), P("#ff9ccf", 0.45), "counter", 0.02)
    B(None, (4.4, 0.9, 0.06), (-5.5, -7.4, 1.03), P("#fbfbf8", 0.3), "countertop", 0.02)
    cm = img_mat(kit, cubby, 0.9)
    pl = kit.plane(nm("cubby"), (6.4, 2.4), (-5.5, -9.7, 1.8), cm, None, rot=(math.pi / 2, 0, 0))
    noshadow(pl)
    B(None, (6.6, 0.1, 2.6), (-5.5, -9.8, 1.8), P("#f5e8c8", 0.6), "cubbyback", 0.0)
    # snack bar
    B(None, (4.2, 0.8, 1.0), (5.5, -8.0, 0.5), P("#ff6f61", 0.45), "bar", 0.02)
    B(None, (4.4, 0.9, 0.06), (5.5, -8.0, 1.03), P("#fbfbf8", 0.3), "bartop", 0.02)
    B(None, (4.6, 0.1, 2.4), (5.5, -9.8, 1.9), P(PINK, 0.5), "barback", 0.0)
    CY(None, 0.4, 0.05, (5.5, -9.7, 2.5), kit.emit("#fff1a8", 2.0), "barsign", rot=(math.pi / 2, 0, 0), n=30)
    for sx in (4.2, 5.1, 6.0, 6.9):
        CY(None, 0.2, 0.06, (sx, -6.4, 0.5), P("#2fb8b0", 0.4), "stool", n=18)
        CY(None, 0.04, 0.5, (sx, -6.4, 0.24), M("#cfd6dc", 0.3), "stoolleg", n=10)
    ctx["stool"] = K.kit.empty(nm("bevstool"), (5.6, -5.4, 0), None)
    CY(ctx["stool"], 0.24, 0.06, (0, 0, 0.46), P("#ffd21a", 0.4), "bs", n=20)
    CY(ctx["stool"], 0.045, 0.43, (0, 0, 0.22), M("#cfd6dc", 0.3), "bsl", n=10)
    # benches
    for bx in (-10, -8.2, 8.2, 10):
        B(None, (1.4, 0.5, 0.45), (bx, -2.6, 0.22), P("#ff5fa2" if bx < 0 else "#2fb8b0", 0.5), "bench", 0.04)
    # lights
    kit.light("sun", "SUN", (0, 0, 20), 1.3, "#fff6e8", rot=(math.radians(25), math.radians(-15), 0), size=0.1)
    for lx in (-6, 0, 6):
        for ly in (-5, 3, 12):
            kit.light(nm("lamp"), "POINT", (lx, ly, 4.2), 200, "#fff0dc", size=0.5, shadow=False)


# ---------------------------------------------------------------------------------------------- number tags
class Tag:
    def __init__(self, kit, who):
        self.who = who
        self.piv = kit.empty(nm(f"tag-{who}"), (0, 0, 0), None)
        self.rim = B(self.piv, (1, 0.42, 0.02), (0, 0, 0), kit.emit(RIM[who], 2.2), "rim", 0.008)
        self.plate = B(self.piv, (1, 0.34, 0.02), (0, 0, 0.012), kit.emit("#101a4a", 0.9), "plate", 0.008)
        self.txt = text_obj(kit, self.piv, 0.3, kit.emit("#ffffff", 3.0), "num")
        self.txt.location = (0, 0, 0.03)
        self.body = None
        self.piv.rotation_mode = "XYZ"
        # the pivot's local -y points at the camera once rotated by the camera's quaternion (see place)


def build_tags(kit, ctx):
    ctx["tags"] = {w: Tag(kit, w) for w in RIM}


def place_tag(tg, ctx, cl, cq, who, v, hidden):
    ch = rig.CHARS.get(who)
    if ch is None or hidden or not v or v == "none":
        hide(tg.piv, True)
        return
    hide(tg.piv, False)
    neck = ch.neck.matrix_world.translation
    top = V((neck.x, neck.y, neck.z + (0.8 if who == 'bev' else 0.72)))
    if neck.z < 0.9:      # lying down: lift the number along the screen's up so it never sits on the face
        top = V(neck) + (cq @ V((0, 1, 0))) * 0.85 + V((0, 0, 0.1))
    tg.piv.location = top
    tg.piv.rotation_euler = cq.to_euler()
    dist = (V(cl) - top).length
    s = max(1.0, min(2.4, dist / 3.4))
    n = len(v)
    w = 0.17 * n + 0.3
    tg.plate.scale = (w, 1, 1)
    tg.rim.scale = (w + 0.08, 1, 1)
    tg.piv.scale = (0.72 * s, 0.72 * s, 0.72 * s)
    if tg.body != v:
        tg.txt.data.body = v
        tg.body = v


# ---------------------------------------------------------------------------------------------- the camera tag
def build_cam_tag(kit, ctx):
    cam = kit.OBJ["cam"]
    cream = kit.emit("#fff3d6", 1.0)
    plate = kit.plane(nm("ctag"), (1, 1), (0, 0, -0.15), cream, cam)
    rimp = kit.plane(nm("ctagrim"), (1, 1), (0, 0, -0.1502), kit.emit(CORAL, 1.2), cam)
    track = kit.plane(nm("ctrack"), (1, 1), (0, 0, -0.1497), kit.emit("#b9b4aa", 1.0), cam)
    fill = kit.plane(nm("cfill"), (1, 1), (0, 0, -0.1494), kit.emit(CORAL, 1.4), cam)
    tx = text_obj(kit, cam, 1.0, kit.emit("#14143a", 1.0), "ctagnum")
    for o in (plate, rimp, track, fill):
        noshadow(o)
    ctx["ctag"] = (plate, rimp, track, fill, tx)


def place_cam_tag(ctx, lens, v, on):
    plate, rimp, track, fill, tx = ctx["ctag"]
    u = 0.15 / lens
    cx, cy = -3.3, 9.1
    for o in ctx["ctag"]:
        o.hide_render = not on
    if not on:
        return
    rimp.location = (cx * u, cy * u, -0.1502)
    rimp.scale = (4.5 * u, 2.3 * u, 1)
    plate.location = (cx * u, cy * u, -0.1500)
    plate.scale = (4.2 * u, 2.0 * u, 1)
    # the plate must sit in front of the rim: swap the depths
    rimp.location.z, plate.location.z = -0.1500, -0.1497
    tx.location = (cx * u, (cy + 0.4) * u, -0.1490)
    tx.scale = (1.4 * u, 1.4 * u, 1.4 * u)
    track.location = (cx * u, (cy - 0.7) * u, -0.1494)
    track.scale = (3.4 * u, 0.3 * u, 1)
    f = max(0.0, min(1.0, v / 500.0))
    fill.location = ((cx - 1.7 + 1.7 * f) * u, (cy - 0.7) * u, -0.1491)
    fill.scale = (max(1e-4, 3.4 * f) * u, 0.3 * u, 1)
    s = str(int(v))
    if tx.data.body != s:
        tx.data.body = s


# ---------------------------------------------------------------------------------------------- props on the cast
def shoe_model(col, k=1.0):
    """A bowling shoe: dark sole, coloured upper and toe, cream heel patch, white laces, tongue; long axis y (toe +y)."""
    e = K.kit.empty(nm("shoe"), (0, 0, 0), None)
    sole = P("#2b2b33", 0.6)
    cream = P("#fbf6e6", 0.4)
    B(e, (0.13 * k, 0.34 * k, 0.03 * k), (0, 0, 0.015 * k), sole, "sole", 0.008)
    B(e, (0.12 * k, 0.2 * k, 0.09 * k), (0, -0.05 * k, 0.075 * k), P(col, 0.45), "upper", 0.02)
    B(e, (0.12 * k, 0.12 * k, 0.06 * k), (0, 0.1 * k, 0.06 * k), P(col, 0.45), "toe", 0.025)
    B(e, (0.125 * k, 0.07 * k, 0.07 * k), (0, -0.13 * k, 0.065 * k), cream, "heel", 0.015)
    B(e, (0.07 * k, 0.1 * k, 0.02 * k), (0, 0.0, 0.125 * k), cream, "tongue", 0.006)
    for i in range(3):
        B(e, (0.1 * k, 0.018 * k, 0.012 * k), (0, (0.03 + 0.035 * i) * k - 0.02 * k, 0.138 * k), P("#ffffff", 0.4),
          "lace", 0.003)
    return e


def build_props(kit, ctx):
    red, blue = P("#e0443a", 0.5), P("#3c78e6", 0.5)
    ctx["ball"] = kit.sphere(nm("ball"), 0.115, (0, 0, 0.115), P("#ff5fa2", 0.12, 0.9), None, 20)
    ctx["shoe"] = shoe_model("#e0443a", 1.0)
    ctx["shoes"] = [shoe_model("#e0443a", 1.6), shoe_model("#3c78e6", 1.6)]
    earl = rig.CHARS.get("earl")
    if earl:
        B(earl.P["arm1"], (0.55, 0.55, 1.0), (0, -0.7, -1.95), P("#2fe0d0", 0.3), "can", 0.1)
        B(earl.P["arm-1"], (0.8, 1.2, 0.6), (0, -0.75, -2.0), red, "sprayshoe", 0.1)
    bev = rig.CHARS.get("bev")
    ctx["covers"] = []
    if bev:
        gm = P("#9a9a9a", 0.6)
        # open the lenses: hide the opaque glass and ring each eye with a thin frame so her eyes show
        fr = P("#ff5fa2", 0.4)
        for ob in list(bpy.data.objects):
            if ob.name.startswith("bev.gl") and not ob.name.startswith("bev.glf") and not ob.name.startswith("bev.glb"):
                ob.hide_render = True
                l = ob.location
                for dx, dz, sx, sz in ((0, -0.16, 0.46, 0.04), (-0.21, 0, 0.04, 0.32), (0.21, 0, 0.04, 0.32)):
                    kit.box(nm("glring"), (sx, 0.04, sz), (l.x + dx, l.y - 0.01, l.z + dz), fr, ob.parent)
        gold = P("#ffd21a", 0.3, 0.8)
        for ob in list(bpy.data.objects):
            if ob.name.startswith("bev.glb"):
                for sx in (-1, 1):       # hoop earrings, a ring facing the viewer at each ear
                    x0, y0, z0 = sx * 0.6, ob.location.y + 0.02, -0.3
                    for dx, dz, sx_, sz_ in ((0, 0.14, 0.34, 0.06), (0, -0.14, 0.34, 0.06), (-0.14, 0, 0.06, 0.34),
                                             (0.14, 0, 0.06, 0.34)):
                        kit.box(nm("hoop"), (sx_, 0.06, sz_), (x0 + dx, y0, z0 + dz), gold, ob.parent)
        for k in ("arm-1", "arm1"):
            c = B(bev.P[k], (1.03, 1.05, 1.0), (0, 0, -1.5), gm, "gray", 0.04)
            ctx["covers"].append(c)


# ---------------------------------------------------------------------------------------------- build / animate
def build(kit, story, tl):
    K.kit = kit
    ctx = {"story": story, "shots": {s["id"]: s for s in story["shots"]}, "late": False}
    build_alley(kit, ctx)
    build_tags(kit, ctx)
    ctx["fill"] = kit.light("camfill", "POINT", (0, 0, 2), 30, "#fff0dc", size=0.6, shadow=False)
    build_cam_tag(kit, ctx)
    return ctx


def animate(kit, story, tl, t, ctx):
    if not ctx["late"]:
        build_props(kit, ctx)
        ctx["late"] = True
    shot = next((s for s in tl["shots"] if s["start"] <= t < s["end"]), tl["shots"][-1])
    sd = ctx["shots"][shot["id"]]
    cl, tgt, lens, _ = bl_story.cam_at(sd, shot, t, {}, tl)
    ctx["fill"].location = (cl[0], cl[1], cl[2])
    cq = (V(tgt) - V(cl)).to_track_quat("-Z", "Y")
    vals = {}
    bpy.context.view_layer.update()
    # ---- number tags
    for who, tg in ctx["tags"].items():
        c = cue_at(tl, f"n_{who}", t)
        v = c.get("v", "")
        ch = rig.CHARS.get(who)
        hid = ch is None or ch.root.hide_render
        place_tag(tg, ctx, cl, cq, who, v, hid)
        vals[who] = v
    bv = vals.get("bev") or "492"
    place_cam_tag(ctx, lens, int(bv.replace(",", "")), True)
    # ---- Bev's gray sleeves
    g = cue_at(tl, "gray", t)
    gv = g.get("g", 0.0) if g else 0.0
    if g and g.get("dur"):
        prev = [c for c in tl["cues"] if c["name"] == "gray" and c["t"] < g["t"]]
        g0 = prev[-1]["g"] if prev else 0.0
        gv = lerp(g0, g["g"], ss((t - g["t"]) / g["dur"]))
    for c in ctx.get("covers", []):
        c.hide_render = gv < 0.01
        c.scale = (1, 1, max(0.001, 1.75 * gv))
        c.location = (0, 0, -1.5 + 0.875 * gv)
    # ---- ball
    b = ctx["ball"]
    bc = cue_at(tl, "ball", t)
    mode = bc.get("mode", "off")
    if mode == "hold":
        ch = rig.CHARS.get(bc["who"])
        p = ch.root.location
        b.hide_render = False
        b.location = (p.x, p.y + 0.6, 1.03)
    elif mode == "roll":
        u = min(1.0, max(0.0, (t - bc["t"]) / bc["dur"]))
        b.hide_render = False
        b.location = (lerp(bc["x0"], bc["x1"], u), lerp(bc["y0"], bc["y1"], u), 0.115)
    else:
        b.hide_render = True
    # ---- flying shoe
    sh = cue_at(tl, "shoe", t)
    fs = ctx["shoe"]
    if sh and 0 <= t - sh["t"] < sh["dur"] + 0.6:
        u = min(1.0, (t - sh["t"]) / sh["dur"])
        hide(fs, False)
        fs.location = (lerp(sh["x0"], sh["x1"], u), lerp(sh["y0"], sh["y1"], u),
                       sh["z0"] + sh["lift"] * 4 * u * (1 - u) + 0.05)
        fs.rotation_euler = (u * 5.0, u * 3.0, u * 2.0)
    else:
        hide(fs, True)
    # ---- pins
    pc = cue_at(tl, "pins", t)
    for e, x, y, i in ctx["pins"]:
        u = 0.0
        if pc:
            u = ss((t - pc["t"] - 0.04 * (i % 5) - 0.02 * i) / 0.45)
        e.rotation_euler = (-1.45 * u * (1 if i % 2 else 0.8), 0.4 * u * (-1) ** i, 0.8 * u * (-1) ** (i // 2))
        e.location = (x + 0.35 * u * (-1) ** i * ((i % 3) / 2.0), y + 0.35 * u * ((i % 4) + 1) / 2.0, 0.05 * u)
    # ---- stool, shoes pair
    ctx["stool"].hide_render = not cue_at(tl, "stool", t).get("on", False)
    for o in ctx["stool"].children:
        o.hide_render = ctx["stool"].hide_render
    sc = cue_at(tl, "shoes", t).get("on", False)
    bev = rig.CHARS.get("bev")
    for i, o in enumerate(ctx["shoes"]):
        hide(o, not sc)
        if sc and bev:
            o.location = (-0.14 + (i - 0.5) * 0.26, -1.46, 1.1)
            o.rotation_euler = (0, 0, 0.5)
    return {"camfill": 1.0}
