"""ep154 "Dad's empty car leaves every dawn": six small stages, far apart, each under its own sky dome (layout.py).

  HOME     the mint bungalow at the top of the hill street, its white porch, the driveway with Dad's teal hatchback
           and Mom's yellow one, the street and the view falling away south to green fields, all at sunrise.
  KITCHEN  our bright yellow kitchen with a ceiling, a round table, two chairs, a window on the sunrise.
  BEACH    the noon beach lot: sand, the sea, Mr. Fenn's white car and his boss's gray one.
  HILL     the long hill road down through green fields to a crossroads, the low gray stone wall, a tree, flowers.
  DINER    the cherry-red diner with chrome bands and warm windows, a coffee-cup glyph on its roof sign, gravel.
  RAIN     last spring: a gray, soft, rainy stretch of road with a grass verge and a hedge.

The cars are one model (build_car) in four colours. Dad's has the full cabin the story lives in: cream seats, a
dash with one dial and a heater slider, a steering wheel that turns only slowly, the passenger seat on two steel
rails (two cream strokes on the inner rail: the lore tally), a door lock knob, and the plaid blanket on the back
seat. There is no glass anywhere, so nothing glints. The rule meter is a cream tag on the camera: a teal car glyph
over a clock, swapped by the `clock` cue. Nothing blinks or flickers; every light holds steady or eases.

Cue tracks (make_story.py): clock (s), car_dad / car_mom / car_boss (x, y, yaw, eased over dur), ride (who: the car
follows that rider in the driver's seat), door_p / door_d (0..1), wheel (a, degrees), heater (v), pseat (v: 1 is
all the way back), lock (v: 1 is down), muffin (v, where: dash | plate, drop), plate (v), mug (who), crumbs (v),
sit_<who> (v: legs bent flat forward).
"""
import math
import sys
import tempfile
from pathlib import Path

import bpy
from mathutils import Vector

sys.path.insert(0, str(Path(__file__).resolve().parent))
import layout as G  # noqa: E402

TMP = Path(tempfile.mkdtemp(prefix="dawncar-"))
FONT = Path(__file__).resolve().parent.parent.parent / "blocky" / "fonts" / "SchibstedGrotesk-Black.ttf"
W = {}
SEATED = ("me", "dad", "mom", "cook")


def ss(x):
    x = min(1.0, max(0.0, x))
    return x * x * (3 - 2 * x)


def sample(name, tl, t, defaults):
    """The state of cue track `name` at t: numeric fields eased over a cue's own "dur"."""
    cur, prev = dict(defaults), dict(defaults)
    for c in tl["cues"]:
        if c["name"] != name:
            continue
        if c["t"] > t:
            break
        prev = dict(cur)
        cur.update({k: v for k, v in c.items() if k in defaults})
        dur = c.get("dur", 0.0)
        if dur > 0 and t < c["t"] + dur:
            u = ss((t - c["t"]) / dur)
            return {k: (prev[k] + (cur[k] - prev[k]) * u if isinstance(cur[k], (int, float)) else cur[k]) for k in cur}
    return cur


def hx(h):
    return tuple(int(h[i:i + 2], 16) for i in (1, 3, 5))


def noshadow(ob):
    ob.visible_shadow = False
    for c in ob.children_recursive:
        c.visible_shadow = False


def imat(kit, name, path, strength=1.0):
    m = kit._new(name)
    nt = m.node_tree
    nt.nodes.remove(nt.nodes["Principled BSDF"])
    tex = nt.nodes.new("ShaderNodeTexImage")
    gc = nt.nodes.new("ShaderNodeTexCoord")
    em = nt.nodes.new("ShaderNodeEmission")
    em.inputs["Strength"].default_value = strength
    nt.links.new(gc.outputs["Generated"], tex.inputs["Vector"])
    nt.links.new(tex.outputs["Color"], em.inputs["Color"])
    out = next(n for n in nt.nodes if n.type == "OUTPUT_MATERIAL")
    nt.links.new(em.outputs[0], out.inputs["Surface"])
    img = bpy.data.images.load(path)
    img.colorspace_settings.name = "sRGB"
    tex.image = img
    return m, tex


# ---------------------------------------------------------------------------------------------- pictures (PIL)
def _tag_image(s):
    from PIL import Image, ImageDraw, ImageFont
    p = TMP / f"tag-{s.replace(':', '')}.png"
    if not p.exists():
        Wd, Ht = 400, 300
        im = Image.new("RGB", (Wd, Ht), hx("#183a44"))
        d = ImageDraw.Draw(im)
        d.rounded_rectangle([12, 12, Wd - 13, Ht - 13], 30, fill=hx("#fff1cf"))
        ink = hx("#183a44")
        teal = hx("#2fa3a0")
        # the car glyph, side on, nose right: body, cabin, two wheels, a window
        d.rounded_rectangle([70, 70, 330, 122], 16, fill=teal, outline=ink, width=7)
        d.polygon([(118, 74), (150, 34), (262, 34), (292, 74)], fill=teal, outline=ink)
        d.line([(118, 74), (150, 34), (262, 34), (292, 74)], fill=ink, width=7)
        d.polygon([(160, 70), (178, 46), (230, 46), (252, 70)], fill=hx("#fff1cf"))
        for cx in (124, 276):
            d.ellipse([cx - 26, 100, cx + 26, 152], fill=ink)
            d.ellipse([cx - 10, 116, cx + 10, 136], fill=hx("#d9d9d9"))
        f = ImageFont.truetype(str(FONT), 128)
        bb = d.textbbox((0, 0), s, font=f)
        tw = bb[2] - bb[0]
        d.text(((Wd - tw) / 2 - bb[0], 150 - bb[1] + 4), s, font=f, fill=ink)
        im.save(p)
    return str(p)


def _cup_image():
    """The diner's roof sign: a coffee cup glyph on cream, no words."""
    from PIL import Image, ImageDraw
    p = TMP / "cup.png"
    if not p.exists():
        Wd, Ht = 400, 240
        im = Image.new("RGB", (Wd, Ht), hx("#fff1dc"))
        d = ImageDraw.Draw(im)
        d.rounded_rectangle([6, 6, Wd - 7, Ht - 7], 26, outline=hx("#c22a2a"), width=14)
        ink = hx("#7a1414")
        d.rounded_rectangle([130, 80, 250, 190], 18, fill=hx("#d93a3a"), outline=ink, width=8)
        d.ellipse([232, 100, 292, 160], outline=ink, width=12)
        d.rounded_rectangle([110, 186, 270, 206], 8, fill=hx("#d93a3a"), outline=ink, width=6)
        for k, x in enumerate((160, 190, 220)):
            d.arc([x - 14, 26, x + 14, 76], 90 + 180 * (k % 2), 270 + 180 * (k % 2), fill=hx("#b07a50"), width=8)
        im.save(p)
    return str(p)


# ---------------------------------------------------------------------------------------------- the sky domes
def dome(kit, name, c, r, stops):
    """A big sphere seen from inside, a gradient by height: stops [(pos 0..1 of the sphere's height, hex)]. It
    lights nothing and throws no shadow; the sets' own lights and the world colour do that."""
    m = bpy.data.materials.new(name + ".mat")
    m.use_nodes = True
    nt = m.node_tree
    for n in list(nt.nodes):
        if n.type != "OUTPUT_MATERIAL":
            nt.nodes.remove(n)
    out = next(n for n in nt.nodes if n.type == "OUTPUT_MATERIAL")
    tc = nt.nodes.new("ShaderNodeTexCoord")
    sep = nt.nodes.new("ShaderNodeSeparateXYZ")
    ramp = nt.nodes.new("ShaderNodeValToRGB")
    em = nt.nodes.new("ShaderNodeEmission")
    em.inputs["Strength"].default_value = 1.0
    nt.links.new(tc.outputs["Generated"], sep.inputs[0])
    nt.links.new(sep.outputs["Z"], ramp.inputs["Fac"])
    nt.links.new(ramp.outputs["Color"], em.inputs["Color"])
    nt.links.new(em.outputs[0], out.inputs["Surface"])
    els = ramp.color_ramp.elements
    while len(els) > 1:
        els.remove(els[-1])
    els[0].position, els[0].color = stops[0][0], kit.col(stops[0][1])
    for pos, hc in stops[1:]:
        e = els.new(pos)
        e.color = kit.col(hc)
    try:
        m.emission_sampling = "NONE"
    except Exception:
        pass
    ob = kit.sphere(name, r, c, m, seg=32)
    ob.visible_shadow = False
    ob.visible_diffuse = False
    ob.visible_glossy = False
    return ob


SUNRISE = [(0.0, "#c9a07a"), (0.47, "#ffd27a"), (0.53, "#ffc08a"), (0.6, "#ffb3c7"), (0.75, "#d9b8e8"),
           (1.0, "#9fc4f0")]
NOON = [(0.0, "#bfe4ff"), (0.48, "#e6f6ff"), (0.56, "#9fd8ff"), (1.0, "#4aa8f0")]
GRAY = [(0.0, "#a9adb4"), (0.5, "#cfd3d8"), (0.62, "#b9bec6"), (1.0, "#9aa1ab")]


# ---------------------------------------------------------------------------------------------- the car
def build_car(kit, name, body_hex, cabin=True):
    """A chunky toy hatchback, front +y, origin on the ground at its middle (layout.py). Returns its parts."""
    pl = kit.plastic
    body = pl(body_hex, 0.42, spec=0.25)
    dark = pl("#2a2d33", 0.7, spec=0.1)
    tyre = pl("#22242a", 0.85, spec=0.05)
    hub = pl("#b9bec6", 0.4, spec=0.3)
    cream = pl("#efe2c4", 0.75, spec=0.05)
    lining = pl("#e8dcc0", 0.85, spec=0.03)
    root = kit.empty(name, (0, -600, 0))
    P = {"root": root}

    def b(n, size, loc, mat=body, parent=root, bevel=0.03, rot=(0, 0, 0)):
        return kit.box(f"{name}.{n}", size, loc, mat, parent, bevel=bevel, rot=rot)

    hw = G.CAR_W / 2
    # the tub: floor, sills, fenders, the engine block under the hood and the trunk under the hatch
    b("floor", (G.CAR_W - 0.2, 4.2, 0.1), (0, 0, 0.35), dark, bevel=0.0)
    b("carpet", (G.CAR_W - 0.3, 3.0, 0.02), (0, -0.4, 0.41), pl("#5a5048", 0.9, spec=0.02), bevel=0.0)
    b("hood", (G.CAR_W, 1.0, 0.75), (0, 1.8, 0.68), bevel=0.12)
    b("trunk", (G.CAR_W, 0.5, 0.75), (0, -2.05, 0.68), bevel=0.12)
    for sx in (-1, 1):
        b(f"fender{sx}", (0.12, 1.0, 0.7), (sx * (hw - 0.06), 1.3 - 0.05, 0.65), bevel=0.03)
        b(f"rear{sx}", (0.12, 1.4, 0.7), (sx * (hw - 0.06), -1.15, 0.65), bevel=0.03)
        b(f"sill{sx}", (0.16, 4.2, 0.08), (sx * (hw - 0.08), 0.0, 1.0), dark, bevel=0.01)
    # the front doors, hinged at their front edge (y 0.95), so the passenger one can swing open
    for sx, nm in ((-1, "door_d"), (1, "door_p")):
        piv = kit.empty(f"{name}.{nm}", (sx * (hw - 0.06), 0.85, 0), root)
        b(f"{nm}.panel", (0.12, 1.4, 0.7), (0, -0.7, 0.65), parent=piv)
        b(f"{nm}.frame", (0.1, 1.4, 0.08), (0, -0.7, 1.9), parent=piv, bevel=0.01)
        b(f"{nm}.post", (0.1, 0.1, 0.9), (0, -1.35, 1.45), parent=piv, bevel=0.01)
        b(f"{nm}.handle", (0.04, 0.22, 0.05), (sx * 0.075, -1.1, 0.85), hub, parent=piv, bevel=0.01)
        b(f"{nm}.trim", (0.14, 1.4, 0.05), (0, -0.7, 1.02), dark, parent=piv, bevel=0.0)
        P[nm] = piv
    # the greenhouse: pillars and the roof (no glass)
    for sx in (-1, 1):
        b(f"apillar{sx}", (0.1, 0.12, 1.05), (sx * (hw - 0.07), 1.12, 1.45), rot=(-0.33, 0, 0), bevel=0.01)
        b(f"bpillar{sx}", (0.12, 0.14, 0.95), (sx * (hw - 0.07), -0.55, 1.45), bevel=0.01)
        b(f"cpillar{sx}", (0.12, 0.35, 0.95), (sx * (hw - 0.07), -1.95, 1.45), bevel=0.01)
    b("roof", (G.CAR_W - 0.04, 3.2, 0.14), (0, -0.55, 2.0), bevel=0.06)
    b("lining", (G.CAR_W - 0.3, 3.0, 0.03), (0, -0.55, 1.915), lining, bevel=0.0)
    b("rearbar", (G.CAR_W - 0.1, 0.12, 0.1), (0, -2.1, 1.1), bevel=0.02)
    b("headrail", (G.CAR_W - 0.1, 0.1, 0.08), (0, 1.0, 1.9), bevel=0.01)
    b("cowl", (G.CAR_W - 0.1, 0.12, 0.08), (0, 1.32, 1.06), dark, bevel=0.01)
    # bumpers, lights
    b("bumper.f", (G.CAR_W + 0.04, 0.2, 0.22), (0, 2.3, 0.42), dark, bevel=0.05)
    b("bumper.r", (G.CAR_W + 0.04, 0.2, 0.22), (0, -2.3, 0.42), dark, bevel=0.05)
    for sx in (-1, 1):
        b(f"head{sx}", (0.42, 0.06, 0.22), (sx * 0.85, 2.31, 0.78), pl("#fff3d0", 0.3, spec=0.2), bevel=0.04)
        b(f"tail{sx}", (0.3, 0.06, 0.3), (sx * 0.95, -2.31, 0.8), pl("#d8322f", 0.4, spec=0.2), bevel=0.04)
    b("plate.f", (0.7, 0.03, 0.2), (0, 2.42, 0.42), pl("#e8e4d6", 0.6), bevel=0.01)
    b("plate.r", (0.7, 0.03, 0.2), (0, -2.42, 0.42), pl("#e8e4d6", 0.6), bevel=0.01)
    # the tyres
    tyres = []
    for sx in (-1, 1):
        for sy in (-1, 1):
            t_ = kit.empty(f"{name}.tyre{sx}{sy}", (sx * (hw - 0.12), sy * 1.45, 0.45), root)
            kit.cyl(f"{name}.tyre{sx}{sy}.r", 0.45, 0.36, (0, 0, 0), tyre, t_, rot=(0, math.pi / 2, 0), n=20)
            kit.cyl(f"{name}.tyre{sx}{sy}.h", 0.22, 0.38, (0, 0, 0), hub, t_, rot=(0, math.pi / 2, 0), n=10)
            tyres.append(t_)
    P["tyres"] = tyres
    if not cabin:
        b("blind", (G.CAR_W - 0.4, 3.0, 0.8), (0, -0.5, 1.4), pl("#3a3f48", 0.8), bevel=0.0)
        return P
    # ---- the cabin
    # a soft warm bounce inside, so the roof lining and the faces under it read as sunlit, never a black lid
    kit.light(f"{name}.cabin", "POINT", (0, -0.4, 1.25), 45, "#fff0dc", size=0.9, parent=root, shadow=False)
    b("dash", (G.CAR_W - 0.22, 0.42, 0.5), (0, 1.15, 0.97), pl("#5f6e78", 0.7, spec=0.08), bevel=0.05)
    b("dashtop", (G.CAR_W - 0.24, 0.42, 0.04), (0, 1.15, 1.235), pl("#6a7a84", 0.75, spec=0.05), bevel=0.01)
    b("console", (0.4, 0.5, 0.42), (0, 0.65, 0.62), pl("#3d4a52", 0.7), bevel=0.03)
    # the dial in front of the driver: a cream face, a red needle
    dx_ = G.SEATS["driver"][0]
    kit.cyl(f"{name}.dial", 0.12, 0.03, (dx_, 0.935, 1.08), cream, root, rot=(math.pi / 2, 0, 0), n=24)
    b("needle", (0.02, 0.012, 0.1), (dx_ + 0.02, 0.918, 1.1), pl("#d8322f", 0.5), rot=(0, 0.6, 0), bevel=0.0)
    # the heater slider: a dark slot, a blue-to-red strip beside it, a knob that moves along it
    b("slot", (0.06, 0.012, 0.36), (0, 0.935, 1.02), pl("#15171a", 0.8), bevel=0.0)
    b("strip.c", (0.05, 0.012, 0.17), (0.07, 0.935, 0.935), pl("#3a6ad8", 0.5), bevel=0.0)
    b("strip.h", (0.05, 0.012, 0.17), (0.07, 0.935, 1.105), pl("#e8402a", 0.5), bevel=0.0)
    P["knob"] = b("knob", (0.14, 0.05, 0.07), (0, 0.915, 0.88), pl("#f2f2ea", 0.5), bevel=0.015)
    # the steering wheel: a ring of blocks round a hub, on a column, tilted toward the driver
    col = kit.empty(f"{name}.col", (dx_, 0.78, 1.12), root, rot=(math.radians(62), 0, 0))
    b("column", (0.08, 0.08, 0.36), (0, 0, -0.2), dark, parent=col, bevel=0.01)
    wh = kit.empty(f"{name}.wheel", (0, 0, 0), col)
    rim = pl("#24272c", 0.6, spec=0.1)
    for k in range(18):
        a = 2 * math.pi * k / 18
        kit.box(f"{name}.wheel.{k}", (0.085, 0.05, 0.05), (0.21 * math.cos(a), 0.21 * math.sin(a), 0), rim, wh,
                rot=(0, 0, a + math.pi / 2), bevel=0.01)
    kit.cyl(f"{name}.wheel.hub", 0.07, 0.05, (0, 0, 0), pl("#3d4a52", 0.6), wh, n=16)
    for k in range(3):
        a = math.pi / 2 + 2 * math.pi * k / 3
        kit.box(f"{name}.wheel.sp{k}", (0.17, 0.035, 0.03), (0.1 * math.cos(a), 0.1 * math.sin(a), 0), rim, wh,
                rot=(0, 0, a), bevel=0.005)
    # a red mark at the rim's top, so a slow turn reads
    kit.box(f"{name}.wheel.mark", (0.06, 0.06, 0.06), (0, 0.21, 0.0), pl("#d8322f", 0.5), wh, bevel=0.01)
    P["wheel"] = wh
    # the rear-view mirror
    b("mirror", (0.36, 0.04, 0.12), (0, 0.9, 1.78), dark, bevel=0.02)

    # the seats
    def seat(n, x, y, parent=root, w=0.95):
        g = kit.empty(f"{name}.{n}", (x, y, 0), parent)
        kit.box(f"{name}.{n}.cush", (w, 0.62, 0.14), (0, 0.06, G.CUSH - 0.07), cream, g, bevel=0.05)
        kit.box(f"{name}.{n}.base", (w - 0.2, 0.5, 0.1), (0, 0.06, G.CUSH - 0.19), dark, g, bevel=0.01)
        kit.box(f"{name}.{n}.back", (w, 0.16, 0.86), (0, -0.28, G.CUSH + 0.42), cream, g, rot=(-0.12, 0, 0), bevel=0.05)
        kit.box(f"{name}.{n}.rest", (w * 0.55, 0.14, 0.26), (0, -0.33, G.CUSH + 1.0), cream, g, bevel=0.05)
        for sx in (-1, 1):
            kit.box(f"{name}.{n}.post{sx}", (0.03, 0.03, 0.1), (sx * w * 0.16, -0.33, G.CUSH + 0.84), hub, g)
        return g
    sd = G.SEATS["driver"]
    seat("seat_d", sd[0], sd[1])
    sp = G.SEATS["pass"]
    P["pseat"] = seat("seat_p", sp[0], sp[1])
    # the rear bench and the plaid blanket on it
    rb = kit.empty(f"{name}.bench", (0, -1.25, 0), root)
    kit.box(f"{name}.bench.cush", (G.CAR_W - 0.4, 0.62, 0.14), (0, 0.06, G.CUSH - 0.07), cream, rb, bevel=0.05)
    kit.box(f"{name}.bench.back", (G.CAR_W - 0.4, 0.16, 0.86), (0, -0.3, G.CUSH + 0.42), cream, rb,
            rot=(-0.12, 0, 0), bevel=0.05)
    plaid = kit.checker("#c8322f", "#2f5a3c", 9.0, name=f"{name}.plaid")
    kit.box(f"{name}.blanket", (0.9, 0.5, 0.05), (0.62, 0.08, G.CUSH + 0.025), plaid, rb, bevel=0.02)
    kit.box(f"{name}.blanket2", (0.9, 0.06, 0.4), (0.62, -0.21, G.CUSH + 0.22), plaid, rb, rot=(-0.12, 0, 0), bevel=0.02)
    # the passenger seat's rails, and two cream strokes on the inner rail (stood 1 cm proud of it)
    steel = pl("#9aa0aa", 0.35, spec=0.4)
    for k, dx in enumerate((-0.32, 0.32)):
        b(f"rail{k}", (0.06, 1.25, 0.05), (sp[0] + dx, 0.02, 0.43), steel, bevel=0.01)
    for k, dy in enumerate((0.3, 0.4)):   # across the rail's top, 6 mm proud; the slide back uncovers them
        b(f"tally{k}", (0.075, 0.022, 0.012), (sp[0] - 0.32, dy, 0.464), pl("#f2e6c8", 0.7), bevel=0.0)
    # the lock knob on the driver's door sill, behind the window
    P["lock"] = b("lockknob", (0.05, 0.05, 0.1), (-(hw - 0.09), -0.35, 1.06), pl("#d8d2c0", 0.5), bevel=0.015)
    return P


def build_muffin(kit, name):
    """A big blueberry muffin in a paper cup: tan, blue dots, cream pleats. Origin at its base."""
    pl = kit.plastic
    root = kit.empty(name, (0, -600, 0))
    kit.cyl(f"{name}.cup", 0.075, 0.1, (0, 0, 0.05), pl("#f2ead8", 0.7, spec=0.05), root, n=16, r2=0.095)
    for k in range(12):
        a = 2 * math.pi * k / 12
        kit.box(f"{name}.pleat{k}", (0.012, 0.012, 0.095), (0.087 * math.cos(a), 0.087 * math.sin(a), 0.05),
                pl("#d8ccb0", 0.7), root, rot=(0, 0, a))
    top = kit.sphere(f"{name}.top", 0.125, (0, 0, 0.12), pl("#d9a45b", 0.65, spec=0.08), root, seg=16)
    top.scale = (1.0, 1.0, 0.72)
    blue = pl("#3a4bd8", 0.45, spec=0.2)
    for k, (a, rr, zz) in enumerate(((0.3, 0.07, 0.19), (1.5, 0.09, 0.17), (2.6, 0.06, 0.2), (3.7, 0.095, 0.16),
                                     (4.8, 0.075, 0.185), (5.7, 0.04, 0.205), (0.9, 0.105, 0.145), (4.2, 0.03, 0.21))):
        kit.sphere(f"{name}.berry{k}", 0.022, (rr * math.cos(a), rr * math.sin(a), zz), blue, root, seg=8)
    return root


# ---------------------------------------------------------------------------------------------- home
def build_home(kit):
    pl = kit.plastic
    grass = kit.texture("grass", 0.5, tint="#7ad46a")
    conc = pl("#c9c2b4", 0.85, spec=0.03)
    road = kit.texture("asphalt", 0.5, tint="#8a8a92")
    mint = pl("#a8e6cf", 0.7, spec=0.04)
    trim = pl("#d8d3c6", 0.7, spec=0.04)           # porch white, kept under 70% so it never clips
    roofm = pl("#5a6a7a", 0.7, spec=0.05)
    dome(kit, "home.sky", (0, -10, -20), 110, SUNRISE)
    kit.box("home.lawn", (40, 26, 0.2), (-6, 4, -0.1), grass)
    kit.box("home.drive", (8.2, 16, 0.06), (6.6, 1.0, 0.0), conc)
    kit.box("home.walk", (40, 2.2, 0.08), (0, -6.9, 0.01), pl("#ddd6c6", 0.85, spec=0.03))
    kit.box("home.street", (80, 6, 0.06), (0, -11.0, -0.02), road)
    kit.box("home.curb", (80, 0.2, 0.14), (0, -8.05, 0.02), pl("#bdb6a8", 0.8))
    # the view south: the hill falls away to fields, hedges and trees
    a = math.atan(0.22)
    kit.box("home.fall", (200, 90, 0.3), (0, -14 - 45 * math.cos(a), -45 * math.sin(a) - 0.15), grass, rot=(a, 0, 0))
    for k, (x, y, w, c) in enumerate(((-30, -40, 30, "#8fdc72"), (10, -48, 40, "#6cc45a"), (40, -38, 25, "#a8e07a"),
                                      (-10, -62, 50, "#7fd06a"))):
        z = -0.22 * (-y - 14) + 0.05
        kit.box(f"home.field{k}", (w, 8, 0.1), (x, y, z), pl(c, 0.9, spec=0.02), rot=(a, 0, 0))
    for k in range(6):
        y = -24 - k * 7
        kit.box(f"home.hedge{k}", (60, 0.8, 0.9), (0, y, -0.22 * (-y - 14) + 0.4), pl("#3f9a4a", 0.85), rot=(a, 0, 0))
    for k, (x, y) in enumerate(((-14, -20), (16, -22), (-24, -30), (28, -34), (-6, -36), (8, -55), (-40, -50))):
        kit.prop("commontree_1", (x, y, -0.22 * (-y - 14)), rot=37 * k, scale=1.2)
    # the bungalow: mint walls, a gray roof, a white porch with a roof on two posts, a door, windows
    x0, x1, y0, y1, H = -8.5, 2.2, G.HOUSE_Y, 18.0, 3.1
    kit.box("home.house", (x1 - x0, y1 - y0, H), ((x0 + x1) / 2, (y0 + y1) / 2, H / 2), mint)
    kit.box("home.base", (x1 - x0 + 0.1, y1 - y0 + 0.1, 0.35), ((x0 + x1) / 2, (y0 + y1) / 2, 0.17), trim)
    rw = (y1 - y0) / 2 + 0.6
    for sy in (-1, 1):
        kit.box(f"home.roof{sy}", (x1 - x0 + 0.8, rw / math.cos(0.5), 0.25),
                ((x0 + x1) / 2, (y0 + y1) / 2 + sy * rw / 2, H + rw * math.tan(0.5) / 2),
                roofm, rot=(sy * 0.5, 0, 0))
    kit.box("home.fascia", (x1 - x0 + 0.8, 0.12, 0.25), ((x0 + x1) / 2, y0 - 0.55, H - 0.05), trim)
    px0, px1, py0, py1 = G.PORCH
    kit.box("home.porch", (px1 - px0, py1 - py0, G.PZ), ((px0 + px1) / 2, (py0 + py1) / 2, G.PZ / 2), trim)
    kit.box("home.porchroof", (px1 - px0 + 0.4, py1 - py0 + 0.3, 0.16), ((px0 + px1) / 2, (py0 + py1) / 2 - 0.1, 2.9), trim)
    for sx in (px0 + 0.2, px1 - 0.2):
        kit.box(f"home.post{sx}", (0.18, 0.18, 2.45), (sx, py0 + 0.2, G.PZ + 1.22), trim)
    for k in range(2):
        kit.box(f"home.step{k}", (1.6, 0.4, 0.15 * (k + 1)), (-2.0, py0 - 0.2 - 0.4 * (1 - k) + 0.0, 0.075 * (k + 1)), trim)
    kit.box("home.rail", (px1 - px0 - 2.4, 0.08, 0.08), (px0 + (px1 - px0 - 2.4) / 2 + 0.1, py0 + 0.2, G.PZ + 0.85), trim)
    # a bounce under the porch roof (the sun can't reach its underside)
    kit.light("home.porchfill", "POINT", (-2.0, 8.7, 1.5), 120, "#fff0dc", size=1.5, shadow=False)
    kit.box("home.door", (1.0, 0.08, 2.1), (-2.0, y0 - 0.03, G.PZ + 1.05), pl("#e8603a", 0.6), bevel=0.02)
    kit.box("home.knob", (0.08, 0.06, 0.08), (-1.65, y0 - 0.09, G.PZ + 1.0), pl("#c9a040", 0.4, spec=0.5))
    winm = pl("#5f86a8", 0.35, spec=0.2)
    for k, x in enumerate((-6.5, -4.3, 0.4)):
        kit.box(f"home.win{k}", (1.4, 0.06, 1.2), (x, y0 - 0.03, 1.75), trim)
        kit.box(f"home.winp{k}", (1.2, 0.06, 1.0), (x, y0 - 0.05, 1.75), winm)
        kit.box(f"home.winb{k}", (0.06, 0.07, 1.0), (x, y0 - 0.07, 1.75), trim)
    for k, x in enumerate((-7.7, -6.1)):   # off the porch (x -5 to 1): clear of me there (S20b) and the S07a lens
        kit.prop("bush_1", (x, y0 - 0.9, 0), scale=0.9, rot=40 * k)
    kit.prop("flowers", (-0.4, 6.8, 0), scale=1.2)
    kit.prop("sub_fence_low", (-12, -5.6, 0), rot=0)
    kit.prop("sub_tree_large", (-12.5, 4.0, 0), rot=20)
    kit.prop("sub_tree_small", (12.5, 6.0, 0), rot=80)
    # the neighbors across the street, low and pastel, far enough to stay soft
    for k, (nm, x, c) in enumerate((("sub_building_type_a", -18, "#ffd0b0"), ("sub_building_type_f", 18, "#c8d8ff"))):
        kit.prop(nm, (x, 9, 0), rot=180, tint=c)
    # the kitchen window frame (S07a looks through it): a cream frame, two blue curtains and a sill
    kw = kit.empty("kwin", (0, 0, 0))
    fr = pl("#f2ead8", 0.6)
    cur = pl("#6a8fd8", 0.8, spec=0.02)
    kit.box("kwin.top", (1.6, 0.08, 0.14), (0, 0, 0.62), fr, kw)
    kit.box("kwin.sill", (1.7, 0.2, 0.08), (0, 0, -0.62), fr, kw)
    for sx in (-1, 1):
        kit.box(f"kwin.side{sx}", (0.1, 0.08, 1.3), (sx * 0.78, 0, 0), fr, kw)
        kit.box(f"kwin.cur{sx}", (0.26, 0.06, 1.25), (sx * 0.62, -0.06, 0.0), cur, kw)
    kit.box("kwin.bar", (0.05, 0.06, 1.2), (0, 0, 0), fr, kw)
    kit.box("kwin.wall", (3.0, 0.06, 0.6), (0, 0.02, -0.95), pl("#ffe27a", 0.8), kw)
    kit.prop("houseplant_1", (0.45, -0.05, -0.58), scale=0.45, parent=kw)
    W["kwin"] = kw
    # light: a gold fill from the sun side, a soft front fill
    for i, (x, y, z, e, tgt) in enumerate(((10, -12, 6, 4200, (4, 4, 1)), (-4, -10, 5, 3200, (-1, 8, 1.4)),
                                            (2, 1.5, 4.5, 1600, (4, 4, 1.2)))):
        f = kit.light(f"home.fill{i}", "AREA", (x, y, z), e, "#fff0e0", size=6.0, shadow=False)
        kit.aim(f, tgt)


# ---------------------------------------------------------------------------------------------- kitchen
def build_kitchen(kit):
    pl = kit.plastic
    yel = pl("#ffd95a", 0.8, spec=0.03)
    cx, cy = (G.K_X0 + G.K_X1) / 2, (G.K_Y0 + G.K_Y1) / 2
    lx, ly = G.K_X1 - G.K_X0, G.K_Y1 - G.K_Y0
    kit.box("k.floor", (lx + 1, ly + 1, 0.1), (cx, cy, -0.05), kit.texture("wood", 0.7, tint="#e8c890"))
    kit.box("k.wall.n", (lx + 0.8, 0.3, G.K_H + 0.3), (cx, G.K_Y1 + 0.15, G.K_H / 2), yel)
    kit.box("k.wall.s", (lx + 0.8, 0.3, G.K_H + 0.3), (cx, G.K_Y0 - 0.15, G.K_H / 2), yel)
    kit.box("k.wall.w", (0.3, ly + 0.8, G.K_H + 0.3), (G.K_X0 - 0.15, cy, G.K_H / 2), yel)
    kit.box("k.wall.e", (0.3, ly + 0.8, G.K_H + 0.3), (G.K_X1 + 0.15, cy, G.K_H / 2), yel)
    kit.box("k.ceiling", (lx + 1, ly + 1, 0.2), (cx, cy, G.K_H + 0.1), kit.emit("#fff4dc", 0.6, "kceil"))
    kit.box("k.band", (lx, 0.03, 0.12), (cx, G.K_Y1 - 0.015, 0.95), pl("#ffffff", 0.7))
    # the window on the north wall, the sunrise behind it
    fr = pl("#f2ead8", 0.6)
    wx, wz = 0.0, 1.75
    kit.box("k.win.frame", (1.9, 0.06, 1.3), (wx, G.K_Y1 - 0.03, wz), fr)
    sky, _ = imat(kit, "k.sunrise", _sunrise_image(), 1.1)
    p = kit.plane("k.win.view", (1.7, 1.1), (wx, G.K_Y1 - 0.07, wz), sky, rot=(math.pi / 2, 0, 0))
    noshadow(p)
    kit.box("k.win.bar", (0.05, 0.08, 1.1), (wx, G.K_Y1 - 0.09, wz), fr)
    kit.box("k.win.barh", (1.7, 0.08, 0.05), (wx, G.K_Y1 - 0.09, wz), fr)
    for sx in (-1, 1):
        kit.box(f"k.cur{sx}", (0.35, 0.06, 1.4), (wx + sx * 1.1, G.K_Y1 - 0.12, wz), pl("#6a8fd8", 0.8, spec=0.02))
    kit.box("k.win.sill", (2.0, 0.2, 0.06), (wx, G.K_Y1 - 0.1, wz - 0.68), fr)
    # cabinets and a fridge along the walls
    kit.prop("kitchen_cabinet1", (-2.6, G.K_Y1 - 0.35, 0), rot=180, height=0.95, tint="#f2f0ea")
    kit.prop("kitchen_sink", (2.5, G.K_Y1 - 0.35, 0), rot=180, height=0.95, tint="#f2f0ea")
    kit.prop("kitchen_fridge", (G.K_X0 + 0.45, cy - 0.6, 0), rot=-90, height=1.9, tint="#e8f0f2")
    kit.prop("houseplant_1", (2.9, G.K_Y1 - 0.4, 0.95), scale=0.7)
    # the round table, two chairs
    tx, ty = G.TABLE
    wood = pl("#c98f55", 0.6)
    kit.cyl("k.table", 0.72, 0.06, (tx, ty, G.TABLE_Z - 0.03), wood, n=32)
    kit.cyl("k.table.leg", 0.08, G.TABLE_Z - 0.06, (tx, ty, (G.TABLE_Z - 0.06) / 2), wood, n=12)
    kit.cyl("k.table.foot", 0.35, 0.05, (tx, ty, 0.025), wood, n=20)
    for nm, (x, y), yaw in (("mom", G.MOM_K, 60), ("dad", G.DAD_K, -60)):
        ch = kit.empty(f"k.chair.{nm}", (x, y, 0), rot=(0, 0, math.radians(yaw)))
        kit.box(f"k.chair.{nm}.seat", (0.8, 0.6, 0.08), (0, 0.05, G.CHAIR_Z - 0.04), wood, ch, bevel=0.02)
        kit.box(f"k.chair.{nm}.back", (0.8, 0.08, 0.8), (0, 0.38, G.CHAIR_Z + 0.42), wood, ch, bevel=0.02)
        for sx in (-0.33, 0.33):
            for sy in (-0.2, 0.3):
                kit.box(f"k.chair.{nm}.leg{sx}{sy}", (0.06, 0.06, G.CHAIR_Z - 0.08), (sx, sy, (G.CHAIR_Z - 0.08) / 2), wood, ch)
    # the mugs and the plate on the table
    for k, (x, y) in enumerate(((G.MOM_K[0] * 0.5 + tx * 0.5, ty - 0.2), (G.DAD_K[0] * 0.5 + tx * 0.5 + 0.1, ty - 0.35))):
        kit.cyl(f"k.mug{k}", 0.06, 0.12, (x, y, G.TABLE_Z + 0.06), pl(("#e8603a", "#3a6ad8")[k], 0.5), n=14)
    W["plate"] = kit.cyl("k.plate", 0.16, 0.02, (G.DAD_K[0] * 0.45, ty - 0.12, G.TABLE_Z + 0.01), pl("#f6f2ea", 0.5), n=24)
    for i, (x, y, z, e) in enumerate(((0.0, 298.5, 2.6, 520), (-2.0, 296.5, 2.6, 420), (2.0, 296.5, 2.6, 420))):
        a = kit.light(f"k.fill{i}", "AREA", (x, y, z), e, "#fff3e0", size=2.5, shadow=False)
        kit.aim(a, (x, y + 0.5, 0.0))
    f = kit.light("k.face", "AREA", (0.0, 296.2, 1.9), 380, "#fff6ec", size=2.5, shadow=False)
    kit.aim(f, (0.0, 299.8, 1.2))


def _sunrise_image():
    from PIL import Image, ImageDraw
    p = TMP / "sunrise.png"
    if not p.exists():
        Wd, Ht = 400, 260
        im = Image.new("RGB", (Wd, Ht))
        d = ImageDraw.Draw(im)
        top, mid, low = hx("#c9b8f0"), hx("#ffb3c7"), hx("#ffd27a")
        for y in range(Ht):
            u = y / Ht
            if u < 0.55:
                c = tuple(int(top[i] + (mid[i] - top[i]) * u / 0.55) for i in range(3))
            else:
                c = tuple(int(mid[i] + (low[i] - mid[i]) * (u - 0.55) / 0.45) for i in range(3))
            d.line([(0, y), (Wd, y)], fill=c)
        d.ellipse([250, 150, 330, 230], fill=hx("#fff0b8"))
        d.rectangle([0, 200, Wd, Ht], fill=hx("#6cc45a"))
        d.polygon([(0, 200), (120, 180), (260, 196), (Wd, 184), (Wd, 205), (0, 205)], fill=hx("#5ab04a"))
        im.save(p)
    return str(p)


# ---------------------------------------------------------------------------------------------- beach
def build_beach(kit):
    pl = kit.plastic
    bx, by = G.BX, G.BY
    dome(kit, "beach.sky", (bx, by, -10), 70, NOON)
    kit.box("b.sand", (80, 30, 0.2), (bx, by + 18, -0.1), pl("#f2dca0", 0.9, spec=0.02))
    kit.box("b.lot", (14, 16, 0.06), (bx, by - 2, 0.0), kit.texture("asphalt", 0.5, tint="#9a9aa2"))
    for k in range(5):
        kit.box(f"b.stripe{k}", (0.12, 5.0, 0.012), (bx - 6 + k * 3.0, by + 2.0, 0.035), pl("#f2f0e6", 0.7))
    kit.box("b.sea", (120, 60, 0.1), (bx, by + 50, -0.05), pl("#2fa8d0", 0.25, spec=0.3))
    kit.box("b.foam", (120, 0.8, 0.04), (bx, by + 20.3, 0.0), pl("#e8f6f8", 0.6))
    for k, (x, y, c) in enumerate(((-6, 13, "#e8402a"), (7, 14, "#3a6ad8"))):
        kit.cyl(f"b.pole{k}", 0.04, 2.2, (bx + x, by + y, 1.1), pl("#efeae0", 0.6), n=8)
        kit.cyl(f"b.umb{k}", 1.3, 0.5, (bx + x, by + y, 2.3), pl(c, 0.6), n=16, r2=0.05)
    kit.prop("rock_1", (bx - 12, by + 12, 0), scale=1.5)
    kit.prop("rock_3", (bx + 12, by + 11, 0), scale=1.3)
    for i, (x, y, e) in enumerate(((0, -6, 3200), (-6, 4, 2000), (6, 4, 2000))):
        a = kit.light(f"b.fill{i}", "AREA", (bx + x, by + y, 7.0), e, "#fffaf0", size=8.0, shadow=False)
        kit.aim(a, (bx + x * 0.5, by + 6, 0.5))


# ---------------------------------------------------------------------------------------------- hill road and the wall
def build_hill(kit):
    pl = kit.plastic
    HX = G.HX
    a = math.atan(G.SLOPE)
    grass = kit.texture("grass", 0.5, tint="#7ad46a")
    road = kit.texture("asphalt", 0.5, tint="#8a8a92")
    dome(kit, "hill.sky", (HX, 10, -20), 130, SUNRISE)
    L = 70.0 / math.cos(a)
    # the slope from the crossroads (y 0) up to the crest (y 70), and flat land round the bottom
    kit.box("h.slope", (160, L, 0.3), (HX, 35.0, G.SLOPE * 35 - 0.15 / math.cos(a)), grass, rot=(a, 0, 0))
    kit.box("h.flat", (160, 80, 0.3), (HX, -40.0, -0.15), grass)
    kit.box("h.crest", (160, 40, 0.3), (HX, 90.0, G.hill_z(70) - 0.15), grass)
    kit.box("h.road", (6.0, L, 0.1), (HX, 35.0, G.SLOPE * 35 + 0.0), road, rot=(a, 0, 0))
    kit.box("h.road.s", (6.0, 60, 0.1), (HX, -30.0, 0.0), road)
    kit.box("h.cross", (120, 6.0, 0.1), (HX, 0.0, 0.004), road)
    dash = pl("#fff1b0", 0.7)
    for k in range(16):
        y = 4 + k * 4.2
        kit.box(f"h.dash{k}", (0.14, 1.8, 0.02), (HX, y, G.SLOPE * y + 0.06), dash, rot=(a, 0, 0))
    for k in range(5):
        y = -6 - k * 5
        kit.box(f"h.dashs{k}", (0.14, 1.8, 0.02), (HX, y, 0.06), dash)
    # fields: bands of greens on both sides, with hedges between them
    for sx in (-1, 1):
        for k in range(5):
            y = 6 + k * 13
            kit.box(f"h.field{sx}{k}", (30, 11, 0.06), (HX + sx * 22, y, G.SLOPE * y + 0.04),
                    pl(("#8fdc72", "#6cc45a", "#a8e07a", "#7fd06a", "#9ad87a")[(k + (sx > 0)) % 5], 0.9, spec=0.02),
                    rot=(a, 0, 0))
            kit.box(f"h.hedge{sx}{k}", (30, 0.8, 1.0), (HX + sx * 22, y + 6.2, G.SLOPE * (y + 6.2) + 0.45),
                    pl("#3f9a4a", 0.85), rot=(a, 0, 0))
        for k in range(8):
            y = 8 + k * 8.5
            kit.prop("commontree_1", (HX + sx * (5.5 + (k % 2) * 1.5), y, G.SLOPE * y), rot=40 * k, scale=1.0)
    for k, (x, y) in enumerate(((-30, -20), (25, -25), (-15, -40), (40, -12), (-45, 10))):
        kit.prop("commontree_2", (HX + x, y, 0), rot=33 * k, scale=1.4)
    # the low gray stone wall on the west side of the road at the bottom, a tree over it, wildflowers
    stone = [pl(c, 0.85, spec=0.03) for c in ("#9a9a9a", "#8a8c8e", "#a8a6a0", "#929690")]
    k = 0
    for row, z in enumerate((0.2, 0.55, 0.85)):
        y = -6.0 + (0.3 if row % 2 else 0.0)
        while y < 4.0:
            ln = 0.55 + 0.25 * ((k * 7) % 3) / 2
            ln = min(ln, 4.0 - y)
            if ln > 0.15:
                kit.box(f"h.stone{k}", (0.6 - 0.06 * row, ln - 0.04, 0.36 if row < 2 else 0.28),
                        (G.WALL_X + 0.01 * (k % 3), y + ln / 2, z), stone[k % 4], bevel=0.06)
            y += ln
            k += 1
    kit.box("h.wallcap", (0.5, 10.0, 0.08), (G.WALL_X, -1.0, 1.02), stone[0], bevel=0.03)
    kit.prop("commontree_1", (G.WALL_X - 2.2, -0.5, 0), rot=10, scale=1.6)
    for k, y in enumerate((-4.5, -2.2, 1.8, 3.2)):
        kit.prop("flowers", (G.WALL_X - 0.9, y, 0), scale=1.0, rot=50 * k)
    kit.prop("bush_2", (G.WALL_X - 1.3, 5.2, 0), scale=1.2)
    for i, (x, y, z, e, tgt) in enumerate(((HX + 6, -10, 5, 3600, (HX - 1.5, 0, 1.2)),
                                            (HX - 4, -9, 4, 2400, (HX - 2.5, 0, 1.2)),
                                            (HX + 2, 18, 8, 2400, (HX, 22, 1.0)))):
        f = kit.light(f"h.fill{i}", "AREA", (x, y, z), e, "#fff0e0", size=6.0, shadow=False)
        kit.aim(f, tgt)


# ---------------------------------------------------------------------------------------------- the diner
def build_diner(kit):
    pl = kit.plastic
    dx, dy = G.DX, G.DY
    dome(kit, "diner.sky", (dx, dy, -15), 75, SUNRISE)
    kit.box("d.lot", (40, 30, 0.1), (dx, dy - 6, -0.05), kit.texture("concrete", 0.6, tint="#d8ccb8"))
    kit.box("d.grass", (120, 120, 0.1), (dx, dy, -0.12), kit.texture("grass", 0.5, tint="#7ad46a"))
    red = pl("#d93a3a", 0.45, spec=0.2)
    chrome = pl("#a8adb6", 0.3, spec=0.5)
    x0, x1, y0, y1, H = dx - 7.5, dx + 7.5, dy + 5.0, dy + 11.0, 3.4
    kit.box("d.body", (x1 - x0, y1 - y0, H), ((x0 + x1) / 2, (y0 + y1) / 2, H / 2 + 0.3), red, bevel=0.3)
    kit.box("d.base", (x1 - x0 + 0.1, y1 - y0 + 0.1, 0.4), ((x0 + x1) / 2, (y0 + y1) / 2, 0.2), chrome, bevel=0.05)
    kit.box("d.roof", (x1 - x0 + 0.6, y1 - y0 + 0.6, 0.3), ((x0 + x1) / 2, (y0 + y1) / 2, H + 0.45), chrome, bevel=0.1)
    for k, z in enumerate((1.0, 2.75)):
        kit.box(f"d.band{k}", (x1 - x0 + 0.04, 0.06, 0.1), ((x0 + x1) / 2, y0 - 0.02, z), chrome)
    warm = kit.emit("#ffd58a", 1.4, "d.warm")
    for k in range(6):
        x = x0 + 1.4 + k * 2.2
        if abs(x - dx) < 0.8:
            continue
        kit.box(f"d.win{k}", (1.7, 0.06, 1.4), (x, y0 - 0.03, 1.85), warm)
        kit.box(f"d.winf{k}", (1.85, 0.05, 1.55), (x, y0 - 0.01, 1.85), chrome)
    kit.box("d.door", (1.1, 0.08, 2.2), (dx, y0 - 0.03, 1.4), pl("#f2ead8", 0.5))
    kit.box("d.doorwin", (0.7, 0.06, 1.0), (dx, y0 - 0.07, 1.8), warm)
    kit.box("d.step", (2.0, 0.8, 0.3), (dx, y0 - 0.4, 0.15), chrome)
    m, _ = imat(kit, "d.sign", _cup_image(), 1.0)
    kit.box("d.signpost", (0.15, 0.15, 1.0), (dx, y0 + 0.6, H + 1.0), chrome)
    s = kit.plane("d.signface", (3.0, 1.8), (dx, y0 + 0.5, H + 2.3), m, rot=(math.pi / 2, 0, 0))
    noshadow(s)
    kit.box("d.signback", (3.2, 0.1, 2.0), (dx, y0 + 0.56, H + 2.3), red)
    for k, x in enumerate((-12, 12)):
        kit.prop("commontree_1", (dx + x, dy + 6, 0), rot=50 * k, scale=1.3)
    kit.prop("bush_1", (dx - 9, dy + 4.5, 0), scale=1.2)
    for i, (x, y, z, e, tgt) in enumerate(((dx + 3, dy - 8, 5, 2600, (dx + 1, dy + 1, 1.2)),
                                            (dx - 4, dy - 6, 4, 1800, (dx - 1, dy + 2, 1.2)))):
        f = kit.light(f"d.fill{i}", "AREA", (x, y, z), e, "#fff0e0", size=6.0, shadow=False)
        kit.aim(f, tgt)


# ---------------------------------------------------------------------------------------------- last spring, in the rain
def build_rain(kit):
    pl = kit.plastic
    rx, ry = G.RX, G.RY
    dome(kit, "rain.sky", (rx, ry, -15), 70, GRAY)
    kit.box("r.grass", (120, 60, 0.2), (rx, ry, -0.1), kit.texture("grass", 0.5, tint="#8ab886"))
    kit.box("r.road", (120, 6.0, 0.06), (rx, G.RAIN_ROAD_Y, 0.0), kit.texture("asphalt", 0.5, tint="#6a6c74"))
    for k in range(12):
        kit.box(f"r.dash{k}", (1.8, 0.14, 0.02), (rx - 40 + k * 7, G.RAIN_ROAD_Y, 0.04), pl("#d8d4c0", 0.7))
    kit.box("r.hedge", (120, 1.0, 1.3), (rx, G.RAIN_ROAD_Y + 5.0, 0.65), pl("#4f8a56", 0.85))
    for k, x in enumerate((-20, -9, 4, 16, 28)):
        kit.prop("commontree_1", (rx + x, G.RAIN_ROAD_Y + 7.5, 0), rot=30 * k, scale=1.2, tint="#b8c8b8")
    kit.box("r.verge", (120, 2.2, 0.04), (rx, G.COOK_RAIN_Y, 0.02), pl("#7aa874", 0.9, spec=0.02))
    for i, (x, y, z, e) in enumerate(((rx + 4, ry - 9, 5, 2400), (rx - 6, ry - 8, 5, 1800))):
        f = kit.light(f"r.fill{i}", "AREA", (x, y, z), e, "#eef2ff", size=7.0, shadow=False)
        kit.aim(f, (x * 0.5, G.RAIN_ROAD_Y, 1.0))


# ---------------------------------------------------------------------------------------------- the tag
def build_tag(kit):
    cam = kit.OBJ["cam"]
    root = kit.empty("tag", (0, 0, 0), cam)
    W["tag"] = root
    m, tex = imat(kit, "tag", _tag_image("5:40"), 1.0)
    p = kit.plane("tag.plane", (1.0, 0.75), (0, 0, 0), m, root)
    noshadow(p)
    W["tagtex"], W["tagimgs"], W["tags"] = tex, {}, "5:40"


# ---------------------------------------------------------------------------------------------- build / animate
def build(kit, story, tl):
    tl["cues"].sort(key=lambda c: c["t"])
    build_home(kit)
    build_kitchen(kit)
    build_beach(kit)
    build_hill(kit)
    build_diner(kit)
    build_rain(kit)
    W["car_dad"] = build_car(kit, "car", "#2fa3a0")
    W["car_mom"] = build_car(kit, "momcar", "#f4c430")
    W["car_fenn"] = build_car(kit, "fenncar", "#d6d2ca", cabin=False)
    W["car_boss"] = build_car(kit, "bosscar", "#8a8f99", cabin=False)
    W["muffin"] = build_muffin(kit, "muffin")
    W["muffin2"] = build_muffin(kit, "muffin2")
    W["mug"] = kit.cyl("mug", 0.07, 0.14, (0, -600, 0), kit.plastic("#3a6ad8", 0.5), n=14)
    sun = kit.light("sun", "SUN", (20, -30, 12), 2.2, "#ffd09a", size=0.08)
    sun.data.angle = 0.08
    kit.aim(sun, (0, 0, 0))
    W["extras_done"] = False
    build_tag(kit)
    for nm, d in kit.LIGHTS.items():      # one global trim, so the bright grade never clips the sets
        f = 0.6 if nm == "sun" else 0.3
        d["light"].energy *= f
        d["base"] = d["light"].energy
    return {}


def attach_extras(kit):
    """Heads wear the extras (idempotent): Dad's round gray beard and its crumbs, my big curly top."""
    pl = kit.plastic
    if W.get("extras_done"):
        return
    dh, mh = bpy.data.objects.get("dad.headg"), bpy.data.objects.get("me.headg")
    if dh is None or mh is None:
        return
    gray = pl("#b4b4bc", 0.8)
    kit.box("dad.chin", (0.7, 0.2, 0.32), (0, -0.55, -0.5), gray, dh, bevel=0.08)
    for sx in (-1, 1):
        kit.box(f"dad.cheek{sx}", (0.22, 0.32, 0.46), (sx * 0.42, -0.45, -0.32), gray, dh, rot=(0, 0, sx * 0.55), bevel=0.06)
        kit.box(f"dad.stache{sx}", (0.32, 0.1, 0.11), (sx * 0.17, -0.65, -0.2), gray, dh, rot=(0, sx * 0.3, 0), bevel=0.03)
    crumbs = []
    tan = pl("#c8924a", 0.7)
    for k, (x, z) in enumerate(((-0.18, -0.52), (0.12, -0.6), (0.26, -0.45), (-0.05, -0.66))):
        crumbs.append(kit.box(f"dad.crumb{k}", (0.07, 0.04, 0.06), (x, -0.67, z), tan, dh, bevel=0.01))
    W["crumbs"] = crumbs
    pink = pl("#ff8a96", 0.7)
    W["blush"] = [kit.box(f"dad.blush{sx}", (0.22, 0.04, 0.13), (sx * 0.36, -0.645, -0.08), pink, dh, bevel=0.02)
                  for sx in (-1, 1)]
    hair = pl("#15151a", 0.7)
    top = 0.6
    for k, (x, y, s) in enumerate(((-0.42, -0.25, 0.36), (0.0, -0.32, 0.4), (0.42, -0.25, 0.36), (-0.45, 0.2, 0.38),
                                   (0.0, 0.1, 0.44), (0.45, 0.2, 0.38), (-0.2, 0.45, 0.36), (0.22, 0.45, 0.36))):
        kit.box(f"me.curl{k}", (s, s, s * 0.85), (x, y, top + 0.45 + 0.04 * (k % 2)), hair, mh, bevel=0.12)
    W["extras_done"] = True


def car_pose(name, tl, t, d0):
    st = sample(name, tl, t, {"x": d0[0], "y": d0[1], "yaw": d0[3]})
    x, y, yaw = st["x"], st["y"], st["yaw"]
    return x, y, G.ground(x, y), yaw


def place_car(P, pose, pitch_on=True):
    x, y, z, yaw = pose
    r = P["root"]
    pitch = 0.0
    if pitch_on and abs(x - G.HX) < 40 and 0.5 < y < 70:
        fy = math.cos(math.radians(yaw))     # the car's front along +y
        pitch = math.atan(G.SLOPE) * fy
    r.location = (x, y, z)
    r.rotation_euler = (pitch, 0, math.radians(yaw))
    fx, fy2 = -math.sin(math.radians(yaw)), math.cos(math.radians(yaw))
    roll = (x * fx + y * fy2) / 0.45
    for ty in P["tyres"]:
        ty.rotation_euler = (roll, 0, 0)


def animate(kit, story, tl, t, ctx):
    attach_extras(kit)
    sid = next((x["id"] for x in tl["shots"] if x["start"] <= t < x["end"]), "")
    # ---- the tag's clock
    s = sample("clock", tl, t, {"s": "5:40"})["s"]
    if s != W["tags"]:
        if s not in W["tagimgs"]:
            img = bpy.data.images.load(_tag_image(s))
            img.colorspace_settings.name = "sRGB"
            W["tagimgs"][s] = img
        W["tagtex"].image = W["tagimgs"][s]
        W["tags"] = s
    # ---- the cars
    ride = sample("ride", tl, t, {"who": ""})["who"]
    pose = car_pose("car_dad", tl, t, G.CAR_HOME)
    place_car(W["car_dad"], pose)
    if ride and bpy.data.objects.get(ride) is not None:     # the rider goes where the car is (no walking, no steps)
        h = story["cast"][ride].get("height", 1.0)
        bpy.data.objects[ride].location = G.seat(pose, "driver", h)[0]
    place_car(W["car_mom"], car_pose("car_mom", tl, t, G.MOM_HOME))
    place_car(W["car_fenn"], G.FENN_CAR)
    place_car(W["car_boss"], car_pose("car_boss", tl, t, (G.BOSS_CAR[0], -14.0, 0, 0)))
    P = W["car_dad"]
    P["door_p"].rotation_euler = (0, 0, math.radians(68) * sample("door_p", tl, t, {"v": 0.0})["v"])
    P["door_d"].rotation_euler = (0, 0, -math.radians(68) * sample("door_d", tl, t, {"v": 0.0})["v"])
    P["wheel"].rotation_euler = (0, 0, math.radians(sample("wheel", tl, t, {"a": 0.0})["a"]))
    P["knob"].location.z = 0.88 + 0.27 * sample("heater", tl, t, {"v": 0.0})["v"]
    P["pseat"].location.y = G.SEATS["pass"][1] - 0.35 * sample("pseat", tl, t, {"v": 0.0})["v"]
    P["lock"].location.z = 1.06 - 0.06 * sample("lock", tl, t, {"v": 0.0})["v"]
    # ---- the muffin: on the dash (it rides with the car), or on Dad's plate in the kitchen
    mf = sample("muffin", tl, t, {"v": 0.0, "where": "dash", "drop": 0.0})
    mu = W["muffin"]
    vis = mf["v"] > 0.5
    for ob in [mu] + list(mu.children):
        ob.hide_render = not vis
    if vis and mf["where"] == "dash":
        mu.location = G.to_world(pose, G.MUFFIN_L[0], G.MUFFIN_L[1], G.MUFFIN_L[2] + 0.12 * mf["drop"])
        mu.rotation_euler = (0, 0, math.radians(pose[3]))
    elif vis:
        pz = W["plate"].location
        mu.location = (pz.x, pz.y, pz.z + 0.015)
    pv = sample("plate", tl, t, {"v": 1.0})["v"] > 0.5
    W["plate"].hide_render = not pv
    m2 = W["muffin2"]
    for ob in [m2] + list(m2.children):
        ob.hide_render = True
    m2.location = (0, -600, 0)
    # ---- the mug on a flat palm
    mw = sample("mug", tl, t, {"who": ""})["who"]
    arm = bpy.data.objects.get(f"{mw}.arm1") if mw else None
    if arm is not None and not bpy.data.objects[mw].hide_render:
        bpy.context.view_layer.update()
        h = arm.matrix_world @ Vector((0, 0, -1.55))
        W["mug"].location = (h.x, h.y, h.z + 0.24)
        W["mug"].hide_render = False
    else:
        W["mug"].location = (0, -600, 0)
        W["mug"].hide_render = True
    bl = sample("blush", tl, t, {"v": 0.0})["v"]
    for c in W.get("blush", []):
        c.hide_render = bl < 0.05 or bpy.data.objects["dad"].hide_render
        c.scale = (max(0.05, bl),) * 3
    for c in W.get("crumbs", []):
        c.hide_render = sample("crumbs", tl, t, {"v": 0.0})["v"] < 0.5 or bpy.data.objects["dad"].hide_render
    # ---- the kitchen window frame, only in S07a
    kw = W["kwin"]
    on = sid == "S07a"
    for ob in [kw] + list(kw.children_recursive):
        ob.hide_render = not on
    if on:
        at, yaw = G.kwin_place()
        kw.location = at
        kw.rotation_euler = (0, 0, math.radians(yaw))
    # ---- seated riders: legs flat forward
    for who in SEATED:
        v = sample(f"sit_{who}", tl, t, {"v": 0.0})["v"]
        if v <= 0:
            continue
        for sx in (-1, 1):
            leg = bpy.data.objects.get(f"{who}.leg{sx}")
            if leg is not None:
                leg.rotation_euler = (leg.rotation_euler.x * (1 - v) - math.pi / 2 * v, 0, 0)
    # ---- the sun: low gold everywhere, dimmed under the rain and lifted at the noon beach
    gain = 1.0
    if sid.startswith("S23b") or sid.startswith("S23c"):
        gain = 0.12
    elif sid.startswith("S03") or sid.startswith("S04"):
        gain = 1.4
    return {"sun": gain}
