"""ep147 "Room Six": three small stages, all bright and sunny, far apart so their lights never mix.

  ROOM    Room Six at the origin: cream walls with a mint wainscot, two orange beds on the west wall, a desk with a drawer
          of review cards and a sunny blinds window on the back wall, a louvered closet beside it, a door on the east wall.
          It has a ceiling, a west and an east wall and a back wall; the camera stands where the south wall would be.
  EXT     the motel row at x 60: a pink stucco wall with mint doors and numerals, an awning, a palm, an ice machine and
          the patio with the bucket "pool" and its tiny diving board.
  OFFICE  the pink office at x -60: a counter with a desk bell, the key board with the empty hook on the back wall.

The rule meter is a cream review card on the camera (five printed stars, filled by the `stars` cue), placed by the engine's
hud. Props follow cues: `card` (a card in a hand, or flat on the desk under the key), `pen`, `key` (on the desk), `shirts`,
`shirt` (a folded shirt in Dad's hands), `drawer`, `closet` (the doors, eased), `win` (the window's light, eased over at
least 0.4 s). Handwriting is scribble strokes, never words; numerals only. Nothing ever blinks or flickers.
"""
import math
import random
import sys
import tempfile
from pathlib import Path

import bpy
from mathutils import Vector

sys.path.insert(0, str(Path(__file__).resolve().parent))
import layout as G  # noqa: E402

from blocky import hair3  # noqa: E402


def _neat():
    """The closet man's hair, this story only (it takes the library's "buzz" slot, set.py loads before the cast is built): a
    black block cut close with a skin-coloured side part, a swept fringe, clean ear blocks and a bare nape, so from behind
    it reads as a neat head and not a grey box."""
    b, T, F, K, Wd, D, H = hair3._b, hair3.TOP, hair3.FRONT, hair3.BACK, hair3.W, hair3.D, hair3.H
    out = [b("cap", (Wd + 0.04, D + 0.06, 0.3), (0, 0, T - 0.08), bevel=0.12),
           b("back", (Wd + 0.06, 0.3, H * 0.84), (0, K - 0.04, T - H * 0.42 + 0.06), bevel=0.05),
           b("sweep", (Wd * 0.62, 0.2, 0.34), (Wd * 0.14, F + 0.02, T - 0.12), bevel=0.07)]
    for sx in (-1, 1):
        out.append(b(f"side{sx}", (0.2, D * 0.85, H * 0.34), (sx * (Wd / 2 + 0.02), 0.06, T - H * 0.17), bevel=0.06))
        out.append(b(f"ear{sx}", (0.3, 0.4, 0.62), (sx * (Wd / 2 + 0.17), 0.1, T - H * 0.56), bevel=0.05, mat="hair2"))
    return out


hair3.STYLES["buzz"] = _neat


def _dadstache():
    """Dad's mustache, up under the nose so the drawn mouth shows below it: a thin bar with two drooping tips."""
    b, T, F, Wd, H = hair3._b, hair3.TOP, hair3.FRONT, hair3.W, hair3.H
    z = T - 0.6 * H
    out = [b("dstache", (Wd * 0.62, 0.3, 0.17), (0, F - 0.13, z), bevel=0.07)]
    for sx in (-1, 1):
        out.append(b(f"dstache{sx}", (0.26, 0.28, 0.4), (sx * Wd * 0.3, F - 0.11, z - 0.12), rot=(0, sx * 0.15, 0), bevel=0.09))
    return out


def _shades():
    """Sunglasses pushed up on the hair: two dark lenses and a bridge, standing on the front of the head's top."""
    b, T, F, Wd = hair3._b, hair3.TOP, hair3.FRONT, hair3.W
    out = [b("shbridge", (0.5, 0.16, 0.12), (0, F + 0.3, T + 0.42), bevel=0.03, mat="hair2")]
    for sx in (-1, 1):
        out.append(b(f"shlens{sx}", (0.95, 0.18, 0.55), (sx * 0.62, F + 0.3, T + 0.42), bevel=0.08, mat="hair2"))
    return out


_shag = hair3.STYLES["shag"]
hair3.STYLES["shag"] = lambda: _shag() + _dadstache() + _shades()     # Dad's hair, this story only: shag + a high mustache + shades

TMP = Path(tempfile.mkdtemp(prefix="room6-"))
W = {}
ORANGE = "#ff9f43"
WALL = "#efd9bb"


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


# ---------------------------------------------------------------------------------------------- pictures (PIL)
def _star(d, cx, cy, r, on):
    pts = []
    for i in range(10):
        a = -math.pi / 2 + i * math.pi / 5
        rr = r if i % 2 == 0 else r * 0.42
        pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
    d.polygon(pts, fill=hx("#ffb703") if on else hx("#e4d9bd"), outline=hx("#7a4a00") if on else hx("#a8996f"))
    d.line(pts + [pts[0]], fill=hx("#7a4a00") if on else hx("#a8996f"), width=6)


def _scribble(d, kind, Wd, y0):
    """Handwriting as strokes, never words."""
    rnd = random.Random(hash(kind) % 1000 + 7)
    ink = {"ours": "#1c2c78", "old": "#4a2e0c", "mine": "#101010", "last": "#101820"}[kind]
    for row in range(3):
        y = y0 + row * 42
        if kind == "last":      # a neat unfamiliar hand: even small ticks, perfectly level
            x = 44
            while x < Wd - 70 - (row == 2) * 120:
                d.line([(x, y), (x, y + 18)], fill=hx(ink), width=8)
                d.line([(x, y + 18), (x + 12, y + 18)], fill=hx(ink), width=8)
                x += 22
        else:
            pts, x = [], 44
            while x < Wd - 60 - (row == 2) * 130:
                pts.append((x, y + rnd.randint(-9, 9) + (8 if len(pts) % 2 else 0)))
                x += 15 + rnd.randint(0, 9)
            d.line(pts, fill=hx(ink), width=10, joint="curve")


def card_image(kind, n):
    from PIL import Image, ImageDraw
    p = TMP / f"card-{kind}-{n}.png"
    if not p.exists():
        Wd, Ht = 400, 300
        paper = "#e6cd8e" if kind == "old" else "#fff1cf"
        edge = "#7a5a1a" if kind == "old" else "#5a3410"
        im = Image.new("RGB", (Wd, Ht), hx(edge))
        d = ImageDraw.Draw(im)
        d.rounded_rectangle([12, 12, Wd - 13, Ht - 13], 26, fill=hx(paper))
        for i in range(5):
            _star(d, 64 + i * 68, 72, 33, i < n)
        d.line([(30, 124), (Wd - 30, 124)], fill=hx("#c9b27a"), width=4)
        _scribble(d, kind, Wd, 152)
        im.save(p)
    return str(p)


def numeral_image(ch, fg, bg):
    from PIL import Image, ImageDraw, ImageFont
    p = TMP / f"num-{ch}-{fg[1:]}-{bg[1:]}.png"
    if not p.exists():
        im = Image.new("RGB", (256, 256), hx(bg))
        d = ImageDraw.Draw(im)
        try:
            f = ImageFont.truetype("DejaVuSans-Bold.ttf", 220)
        except Exception:
            f = ImageFont.load_default()
        d.text((128, 132), ch, fill=hx(fg), font=f, anchor="mm")
        im.save(p)
    return str(p)


def sunburst_image():
    from PIL import Image, ImageDraw
    p = TMP / "picture.png"
    if not p.exists():
        im = Image.new("RGB", (480, 360), hx("#ffd9a0"))
        d = ImageDraw.Draw(im)
        d.rectangle([0, 230, 480, 360], fill=hx("#e8a25a"))
        d.ellipse([300, 50, 400, 150], fill=hx("#ff7a59"))
        d.polygon([(0, 230), (110, 120), (230, 230)], fill=hx("#c96f3a"))
        d.polygon([(150, 230), (290, 100), (440, 230)], fill=hx("#b85d2e"))
        for k in range(8):
            a_ = k * math.pi / 4
            d.line([(350 + 62 * math.cos(a_), 100 + 62 * math.sin(a_)), (350 + 88 * math.cos(a_), 100 + 88 * math.sin(a_))],
                   fill=hx("#ff7a59"), width=8)
        im.save(p)
    return str(p)


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


def noshadow(ob):
    ob.visible_shadow = False
    for c in ob.children_recursive:
        c.visible_shadow = False


def numeral(kit, name, ch, size, loc, fg="#ffffff", bg="#2a7a66", parent=None, rot=(math.pi / 2, 0, 0)):
    m, _ = imat(kit, f"num {name}", numeral_image(ch, fg, bg), 0.95)
    return noshadow(kit.plane(name, (size, size), loc, m, parent, rot=rot))


# ---------------------------------------------------------------------------------------------- Room Six
def build_room(kit):
    pl = kit.plastic
    wall = pl(WALL, 0.85, spec=0.03)
    wood = kit.texture("wood", 0.7, tint="#e8c890")
    ceil = kit.emit("#fff1dc", 0.75, "roomceil")
    mint = pl("#7fe0c4", 0.75, spec=0.03)
    trim = pl("#fffaf0", 0.6)
    dark = pl("#8a5a30", 0.6)
    X0, X1, Y0, Y1, H = G.RX0, G.RX1, G.RY0, G.RY1, G.RH
    cx, cy = (X0 + X1) / 2, (Y0 + Y1) / 2
    lx, ly = X1 - X0, Y1 - Y0
    kit.box("room.floor", (lx + 1, ly + 1, 0.1), (cx, cy, -0.05), wood)
    kit.box("room.ceiling", (lx + 1, ly + 1, 0.2), (cx, cy, H + 0.1), ceil)
    kit.box("room.wall.w", (0.4, ly + 0.8, H + 0.3), (X0 - 0.2, cy, H / 2 - 0.05), wall)
    kit.box("room.wall.e", (0.4, ly + 0.8, H + 0.3), (X1 + 0.2, cy, H / 2 - 0.05), wall)
    # the back wall in pieces round the window and the closet (y 2.5 .. 2.8)
    by = Y1 + 0.15
    wx0, wx1, wz0, wz1 = G.WIN[0] - 0.7, G.WIN[0] + 0.7, 1.2, 2.5
    kit.box("room.back.l", (wx0 - X0 + 0.4, 0.3, H + 0.3), ((X0 - 0.4 + wx0) / 2, by, H / 2 - 0.05), wall)
    kit.box("room.back.m", (G.CL0 - wx1, 0.3, H + 0.3), ((wx1 + G.CL0) / 2, by, H / 2 - 0.05), wall)
    kit.box("room.back.r", (X1 + 0.4 - G.CL1, 0.3, H + 0.3), ((G.CL1 + X1 + 0.4) / 2, by, H / 2 - 0.05), wall)
    kit.box("room.back.below", (wx1 - wx0, 0.3, wz0), ((wx0 + wx1) / 2, by, wz0 / 2), wall)
    kit.box("room.back.above", (wx1 - wx0, 0.3, H - wz1 + 0.3), ((wx0 + wx1) / 2, by, (wz1 + H + 0.3) / 2), wall)
    kit.box("room.back.head", (G.CL1 - G.CL0, 0.3, H - G.CLH + 0.3), (G.CLX, by, (G.CLH + H + 0.3) / 2), wall)
    # mint wainscot, 1.5 cm proud of the walls
    for nm, size, loc in (("w", (0.03, ly, 0.9), (X0 + 0.015, cy, 0.45)), ("e", (0.03, ly, 0.9), (X1 - 0.015, cy, 0.45))):
        kit.box(f"room.band.{nm}", size, loc, mint)
    kit.box("room.band.bl", (wx0 - X0, 0.03, 0.9), ((X0 + wx0) / 2, Y1 - 0.015, 0.45), mint)
    kit.box("room.band.br", (X1 - G.CL1, 0.03, 0.9), ((G.CL1 + X1) / 2, Y1 - 0.015, 0.45), mint)
    kit.box("room.band.bm", (G.CL0 - wx1, 0.03, 0.9), ((wx1 + G.CL0) / 2, Y1 - 0.015, 0.45), mint)
    # the window: a glowing pane well behind the wall plane, blinds 2 cm proud of it
    blindm = pl("#d9c9a8", 0.6)     # beige slats: white ones clipped
    wm = kit.emit("#9ccdf0", 0.7, "roomwin")
    W["winmat"] = wm
    pane = kit.box("room.win.pane", (wx1 - wx0, 0.02, wz1 - wz0), ((wx0 + wx1) / 2, Y1 + 0.2, (wz0 + wz1) / 2), wm)
    noshadow(pane)
    for k in range(13):
        z = wz0 + 0.06 + k * (wz1 - wz0 - 0.1) / 12
        kit.box(f"room.blind{k}", (wx1 - wx0 - 0.06, 0.04, 0.055), ((wx0 + wx1) / 2, Y1 - 0.02, z), blindm, rot=(0.35, 0, 0))
    for nm, size, loc in (("t", (wx1 - wx0 + 0.12, 0.06, 0.07), ((wx0 + wx1) / 2, Y1 - 0.03, wz1 + 0.03)),
                          ("b", (wx1 - wx0 + 0.12, 0.08, 0.07), ((wx0 + wx1) / 2, Y1 - 0.04, wz0 - 0.03)),
                          ("l", (0.07, 0.06, wz1 - wz0 + 0.1), (wx0 - 0.03, Y1 - 0.03, (wz0 + wz1) / 2)),
                          ("r", (0.07, 0.06, wz1 - wz0 + 0.1), (wx1 + 0.03, Y1 - 0.03, (wz0 + wz1) / 2))):
        kit.box(f"room.win.f{nm}", size, loc, trim)
    # the desk: a solid wood body against the back wall, a top, and a drawer that slides out of its front
    dx, dfy, dtop = G.DESK[0], G.DESK[1], G.DESK_TOP
    dd = Y1 - dfy
    kit.box("desk.body", (G.DESK_W - 0.1, dd - 0.02, dtop - 0.05), (dx, dfy + dd / 2 - 0.01, (dtop - 0.05) / 2), dark, bevel=0.01)
    kit.box("desk.top", (G.DESK_W, dd, 0.05), (dx, dfy + dd / 2, dtop - 0.025), pl("#b07a4b", 0.5), bevel=0.01)
    for sx in (-1, 1):
        kit.box(f"desk.leg{sx}", (0.07, dd, dtop - 0.05), (dx + sx * (G.DESK_W / 2 - 0.035), dfy + dd / 2, (dtop - 0.05) / 2),
                pl("#b07a4b", 0.5))
    drw = kit.empty("desk.drawer", (dx, dfy, 0.0))
    W["drawer"] = drw
    kit.box("drawer.front", (0.95, 0.04, 0.22), (0, -0.03, dtop - 0.2), pl("#c8905a", 0.5), drw, bevel=0.01)
    kit.box("drawer.knob", (0.16, 0.05, 0.04), (0, -0.07, dtop - 0.2), pl("#e0a830", 0.3, spec=0.7), drw, bevel=0.015)
    inner = pl("#6b4220", 0.7)
    kit.box("drawer.floor", (0.92, 0.46, 0.03), (0, 0.22, dtop - 0.29), inner, drw)
    kit.box("drawer.l", (0.03, 0.46, 0.18), (-0.45, 0.22, dtop - 0.21), inner, drw)
    kit.box("drawer.r", (0.03, 0.46, 0.18), (0.45, 0.22, dtop - 0.21), inner, drw)
    kit.box("drawer.back", (0.92, 0.03, 0.18), (0, 0.45, dtop - 0.21), inner, drw)
    lm, _ = imat(kit, "leadcard", card_image("ours", 5), 1.0)
    lead = kit.plane("drawer.lead", (0.5, 0.375), (0, 0.05, dtop - 0.03), lm, drw, rot=(math.pi / 2 - 0.55, 0, 0))
    noshadow(lead)
    W["lead"] = lead
    tints = ("#fff1cf", "#ffe3e8", "#e4f6ee", "#fff1cf", "#ffe9b8", "#fff1cf", "#e6f0ff")
    for k in range(14):
        kit.box(f"drawer.card{k}", (0.012, 0.3, 0.2), (-0.4 + k * 0.062, 0.22, dtop - 0.16 + (k % 3) * 0.012), pl(tints[k % 7], 0.7),
                drw, rot=(0, 0.12 * ((k % 5) - 2) / 2, 0))
        kit.box(f"drawer.star{k}", (0.014, 0.05, 0.02), (-0.4 + k * 0.062, 0.1, dtop - 0.07), pl("#ffb703", 0.5), drw)
    # the closet: side panels, a back panel, a rail, hangers, a shelf; its own soft light
    cl0, cl1, ch, cy1 = G.CL0, G.CL1, G.CLH, G.CLY
    cin = kit.emit("#f6dcc0", 0.8, "closetin")
    kit.box("closet.back", (cl1 - cl0 + 0.2, 0.06, ch), (G.CLX, cy1 + 0.03, ch / 2), cin)
    kit.box("closet.l", (0.08, cy1 - Y1 + 0.1, ch), (cl0 - 0.04, (Y1 + cy1) / 2 + 0.05, ch / 2), cin)
    kit.box("closet.r", (0.08, cy1 - Y1 + 0.1, ch), (cl1 + 0.04, (Y1 + cy1) / 2 + 0.05, ch / 2), cin)
    kit.box("closet.top", (cl1 - cl0 + 0.2, cy1 - Y1 + 0.1, 0.06), (G.CLX, (Y1 + cy1) / 2 + 0.05, ch + 0.03), cin)
    kit.box("closet.floor", (cl1 - cl0, cy1 - Y1, 0.04), (G.CLX, (Y1 + cy1) / 2, 0.02), pl("#8a6a48", 0.7))
    kit.box("closet.shelf", (cl1 - cl0 - 0.04, 0.4, 0.04), (G.CLX, cy1 - 0.2, 2.62), pl("#b07a4b", 0.6))
    kit.cyl("closet.rail", 0.016, cl1 - cl0 - 0.04, (G.CLX, cy1 - 0.25, 2.5), pl("#c9ced6", 0.3, spec=0.7), rot=(0, math.pi / 2, 0), n=10)
    sun_s = kit.emit("#fff1c8", 0.95, "closetsun")
    for k in range(9):      # blind-striped sunlight on the back wall (2 cm proud)
        noshadow(kit.box(f"closet.sun{k}", (cl1 - cl0 + 0.1, 0.02, 0.15), (G.CLX, cy1 - 0.012, 0.35 + k * 0.27), sun_s))
    hw = pl("#e8b878", 0.5)
    for k in range(5):      # empty wooden hangers on the rail
        hxx = cl0 + 0.2 + k * 0.25
        kit.box(f"closet.hook{k}", (0.025, 0.025, 0.09), (hxx, cy1 - 0.25, 2.55), pl("#c9ced6", 0.3, spec=0.7))
        for sx in (-1, 1):
            kit.box(f"closet.harm{k}{sx}", (0.24, 0.02, 0.025), (hxx + sx * 0.1, cy1 - 0.25, 2.43), hw, rot=(0, -sx * 0.4, 0))
        kit.box(f"closet.hbar{k}", (0.42, 0.025, 0.03), (hxx, cy1 - 0.25, 2.33), hw)
    lamp = kit.light("closet.fill", "AREA", (G.CLX, 3.1, 2.55), 100, "#fff3e0", size=1.2, shadow=False)
    kit.aim(lamp, (G.CLX, 3.2, 1.0))
    # the closet doors: two leaves hinged at the opening's edges, solid panels with louver slats 1 cm proud
    sage = pl("#d9a066", 0.7, spec=0.05)
    slat = pl("#b9733a", 0.7, spec=0.05)
    W["doors"] = []
    for side, hx_, sgn in ((-1, cl0, 1), (1, cl1, -1)):
        piv = kit.empty(f"closet.pivot{side}", (hx_, Y1 - 0.02, 0.0))
        kit.box(f"closet.leaf{side}", (0.7, 0.04, ch - 0.03), (sgn * 0.35, 0.0, ch / 2), sage, piv, bevel=0.008)
        for k in range(14):
            kit.box(f"closet.slat{side}{k}", (0.6, 0.035, 0.07), (sgn * 0.35, -0.035, 0.2 + k * 0.17), slat, piv, rot=(0.5, 0, 0))
        kit.box(f"closet.knob{side}", (0.05, 0.05, 0.05), (sgn * 0.62, -0.05, 1.05), pl("#e0a830", 0.3, spec=0.7), piv, bevel=0.015)
        W["doors"].append((piv, side))
    # the beds: wood frames, orange spreads with a darker band, white pillows, a nightstand with a glowing lamp
    spread, band = pl(ORANGE, 0.85, spec=0.02), pl("#e07a1f", 0.85, spec=0.02)
    pillow = pl("#fffaf0", 0.8, spec=0.02)
    frame = pl("#b07a4b", 0.55)
    for nm, y in (("a", -2.6), ("b", -1.1)):
        kit.box(f"bed{nm}.frame", (2.0, 1.1, 0.32), (X0 + 1.0, y, 0.16), frame, bevel=0.02)
        kit.box(f"bed{nm}.mattress", (1.9, 1.0, 0.18), (X0 + 1.0, y, 0.41), pl("#f4ecd8", 0.8), bevel=0.04)
        kit.box(f"bed{nm}.spread", (1.5, 1.04, 0.1), (X0 + 1.2, y, 0.55), spread, bevel=0.04)
        kit.box(f"bed{nm}.band", (0.2, 1.06, 0.115), (X0 + 1.55, y, 0.55), band, bevel=0.02)
        kit.box(f"bed{nm}.pillow", (0.55, 0.7, 0.14), (X0 + 0.38, y, 0.6), pillow, bevel=0.06)
        kit.box(f"bed{nm}.head", (0.1, 1.2, 0.95), (X0 + 0.05, y, 0.55), frame, bevel=0.02)
    kit.box("night.table", (0.5, 0.45, 0.5), (X0 + 0.3, -1.85, 0.25), frame, bevel=0.02)
    shade = kit.emit("#ffe2b0", 1.3, "lampshade")
    noshadow(kit.cyl("night.shade", 0.14, 0.22, (X0 + 0.3, -1.85, 0.62), shade, n=10, r2=0.1))
    # a rug, a framed picture on the west wall, a sun-faded pennant, a wall lamp, the east door
    kit.box("room.rug", (2.6, 1.7, 0.02), (1.2, -0.6, 0.01), pl("#2ec4b6", 0.9, spec=0.02))
    kit.box("room.rug.edge", (2.4, 1.5, 0.012), (1.2, -0.6, 0.025), pl("#fff1cf", 0.9, spec=0.02))
    pm, _ = imat(kit, "picture", sunburst_image(), 0.9)
    kit.box("room.pic.frame", (0.04, 1.1, 0.85), (X0 + 0.02, -1.85, 1.9), trim)
    noshadow(kit.plane("room.pic", (0.96, 0.72), (X0 + 0.05, -1.85, 1.9), pm, rot=(math.pi / 2, 0, math.pi / 2)))
    ez, ey = G.DOOR[0], G.DOOR[1]
    kit.box("room.door", (0.06, 0.95, 2.1), (ez - 0.03, ey, 1.05), mint, bevel=0.01)
    kit.box("room.door.frame", (0.08, 1.15, 2.2), (ez - 0.04, ey, 1.1), trim)
    kit.box("room.door.knob", (0.08, 0.07, 0.07), (ez - 0.09, ey - 0.35, 1.0), pl("#e0a830", 0.3, spec=0.7), bevel=0.02)
    numeral(kit, "room.door6", "6", 0.3, (ez - 0.075, ey, 1.55), "#ffffff", "#2a7a66", rot=(math.pi / 2, 0, -math.pi / 2))
    # lights: soft, constant, no shadows
    for i, (x, y) in enumerate(((0.0, 1.0), (2.0, 1.0), (0.0, -1.0), (2.0, -1.0), (0.0, -3.0), (2.0, -3.0), (-1.5, 0.0))):
        a = kit.light(f"room.fill{i}", "AREA", (x, y, H - 0.15), 150, "#fff3e0", size=2.5, shadow=False)
        kit.aim(a, (x, y, 0.0))
    s = kit.light("room.face", "AREA", (0.6, -3.5, 2.4), 200, "#fff6ec", size=2.5, shadow=False)
    kit.aim(s, (0.6, 1.0, 1.4))
    wl = kit.light("win.light", "AREA", (G.WIN[0], 2.0, 2.2), 120, "#ffe2b0", size=1.2, shadow=False)
    kit.aim(wl, (G.WIN[0], -1.0, 1.0))
    W["winlight"] = wl


# ---------------------------------------------------------------------------------------------- the motel row
def build_ext(kit):
    pl = kit.plastic
    EX, WY = G.EX, G.EXT_WALL_Y
    asph = pl("#6a6e7a", 0.85, spec=0.03)
    conc = pl("#e2d8c6", 0.8, spec=0.03)
    pink = pl("#f0b4c0", 0.8, spec=0.03)
    mint = pl("#7fe0c4", 0.7, spec=0.05)
    trim = pl("#fffaf0", 0.6)
    teal = pl("#2ec4b6", 0.7)
    kit.box("ext.road", (60, 9, 0.1), (EX, -4.0, -0.05), asph)
    kit.box("ext.stripe", (60, 0.18, 0.012), (EX, -4.0, 0.01), pl("#ffe27a", 0.6))
    kit.box("ext.walk", (60, 5.2, 0.14), (EX, 2.1 + 0.5, -0.0), conc)
    for k in range(-14, 15):
        kit.box(f"ext.joint{k}", (0.03, 5.2, 0.01), (EX + k * 2.1, 2.6, 0.075), pl("#b9ad98", 0.9))
    kit.box("ext.wall", (40, 0.5, 3.6), (EX, WY + 0.25, 1.75), pink)
    kit.box("ext.fascia", (40, 0.2, 0.42), (EX, WY - 0.08, 3.55), teal)
    kit.box("ext.base", (40, 0.04, 0.5), (EX, WY - 0.02, 0.32), pl("#e08aa0", 0.8))
    kit.box("ext.awning", (40, 1.5, 0.08), (EX, WY - 0.75, 2.75), trim)
    kit.box("ext.awning.stripe", (40, 0.08, 0.2), (EX, WY - 1.52, 2.7), teal)
    nums = {-3: "3", -2: "4", -1: "5", 0: "6", 1: "7", 2: "8", 3: "9"}
    for k, ch in nums.items():
        x = EX + k * 4.2
        kit.box(f"ext.door{k}", (1.0, 0.06, 2.1), (x, WY - 0.03, 1.05), mint, bevel=0.01)
        kit.box(f"ext.doorframe{k}", (1.2, 0.05, 2.25), (x, WY - 0.01, 1.12), trim)
        kit.box(f"ext.knob{k}", (0.07, 0.07, 0.07), (x - 0.38, WY - 0.09, 1.0), pl("#e0a830", 0.3, spec=0.7), bevel=0.02)
        kit.box(f"ext.win{k}", (1.0, 0.04, 0.95), (x + 1.75, WY - 0.02, 1.55), trim)
        kit.box(f"ext.glass{k}", (0.86, 0.04, 0.81), (x + 1.75, WY - 0.05, 1.55), kit.emit("#9fd8ff", 0.9, "extglass"))
        kit.box(f"ext.curtain{k}", (0.4, 0.04, 0.75), (x + 1.55, WY - 0.08, 1.55), pl("#ff9f43", 0.8))
        big = 0.5 if k == 0 else 0.3
        numeral(kit, f"ext.num{k}", ch, big, (x, WY - 0.075, 1.55 if k == 0 else 1.8),
                "#ffffff", "#2a7a66" if k == 0 else "#e08aa0")
    # palm: leaning trunk, ringed, with block fronds
    trunk = pl("#a6794a", 0.8)
    for px, py, h in ((EX - 5.6, 5.0, 4.2), (EX + 7.4, 5.1, 3.6)):
        for s_ in range(7):
            kit.box(f"palm{px}.t{s_}", (0.3 - s_ * 0.012, 0.3 - s_ * 0.012, 0.62), (px + s_ * 0.04, py, 0.3 + s_ * h / 7), trunk, bevel=0.04)
        green = pl("#3f9a4a", 0.7)
        for a in range(8):
            ang = a * 45
            kit.box(f"palm{px}.f{a}", (1.5, 0.22, 0.07), (px + 0.28 + 0.65 * math.cos(math.radians(ang)), py + 0.65 * math.sin(math.radians(ang)), h + 0.18 - 0.14),
                    green, rot=(0, 0.35 * math.cos(math.radians(ang)), math.radians(ang)), bevel=0.02)
    # an ice machine and a bench
    kit.box("ext.ice", (0.95, 0.7, 1.9), (EX - 9.5, 5.5, 0.95), pl("#9fd8ff", 0.5, spec=0.3), bevel=0.04)
    kit.box("ext.ice.panel", (0.7, 0.04, 0.9), (EX - 9.5, 5.13, 1.1), trim)
    # the patio and the bucket "pool": a turquoise bucket of water with a tiny diving board and ladder
    px, py = G.EXT_POOL
    kit.box("ext.patio", (3.4, 2.4, 0.05), (px, py - 0.1, 0.08), pl("#ffd9a0", 0.8))
    kit.box("ext.patio.edge", (3.5, 2.5, 0.03), (px, py - 0.1, 0.06), pl("#ff9f43", 0.8))
    bk = pl("#2ec4d6", 0.4, spec=0.4)
    kit.cyl("bucket.body", 0.3, 0.55, (px, py, 0.38), bk, n=24, r2=0.36)
    kit.cyl("bucket.rim", 0.37, 0.05, (px, py, 0.67), pl("#1b9fb0", 0.4), n=24)
    kit.cyl("bucket.water", 0.33, 0.02, (px, py, 0.66), kit.emit("#7ff0ff", 0.9, "bucketwater"), n=24)
    for sx in (-1, 1):
        kit.box(f"bucket.handle{sx}", (0.04, 0.04, 0.34), (px + sx * 0.38, py, 0.82), pl("#c9ced6", 0.3, spec=0.7), rot=(0, sx * 0.3, 0))
    kit.box("bucket.handle.top", (0.8, 0.04, 0.04), (px, py, 0.99), pl("#c9ced6", 0.3, spec=0.7))
    kit.box("bucket.board", (0.5, 0.12, 0.03), (px + 0.5, py - 0.15, 0.72), pl("#fffaf0", 0.5), rot=(0, 0.08, 0.35))
    kit.box("bucket.boardstand", (0.1, 0.1, 0.2), (px + 0.38, py - 0.1, 0.55), pl("#c9ced6", 0.3, spec=0.7))
    kit.box("bucket.ladder1", (0.03, 0.03, 0.4), (px - 0.38, py - 0.12, 0.8), pl("#c9ced6", 0.3, spec=0.7))
    kit.box("bucket.ladder2", (0.03, 0.03, 0.4), (px - 0.28, py - 0.3, 0.8), pl("#c9ced6", 0.3, spec=0.7))
    # a lounge chair for scale and a striped parasol
    kit.box("ext.lounge", (0.7, 1.7, 0.1), (px - 1.2, py - 0.2, 0.34), pl("#fffaf0", 0.7))
    kit.box("ext.lounge.back", (0.7, 0.1, 0.8), (px - 1.2, py + 0.55, 0.65), pl("#ff9f43", 0.7), rot=(0.4, 0, 0))
    for sx in (-1, 1):
        kit.box(f"ext.lounge.leg{sx}", (0.06, 0.06, 0.3), (px - 1.2 + sx * 0.3, py - 0.9, 0.15), pl("#c9ced6", 0.3))
    kit.box("ext.parasol.pole", (0.05, 0.05, 2.1), (px + 1.3, py + 0.3, 1.05), pl("#c9ced6", 0.3, spec=0.7))
    kit.cyl("ext.parasol", 0.9, 0.3, (px + 1.3, py + 0.3, 2.05), pl("#ff5fa2", 0.7), n=12, r2=0.1)
    # the desert, far off, and the sun
    kit.box("ext.hills", (120, 6, 5), (EX, 55, 2.0), pl("#e8b878", 0.9, spec=0.01))
    kit.box("ext.hills2", (120, 6, 9), (EX + 10, 70, 4.0), pl("#d9a066", 0.9, spec=0.01))
    sun = kit.light("sun", "SUN", (EX - 14, -8, 22), 1.6, "#fff0d0", size=0.06)
    sun.data.angle = 0.06
    kit.aim(sun, (EX, 4.0, 1.0))
    ef = kit.light("ext.face", "AREA", (EX, -4.0, 3.2), 1400, "#fff2e0", size=6.0, shadow=False)
    kit.aim(ef, (EX, 4.4, 1.2))


# ---------------------------------------------------------------------------------------------- the office
def build_office(kit):
    pl = kit.plastic
    pink = pl("#f0b4c0", 0.8, spec=0.03)
    wood = kit.texture("wood", 0.7, tint="#e8c890")
    ox0, ox1, oy0, oy1, oh = G.OX - 4.0, G.OX + 4.0, -7.0, 3.2, 3.0
    kit.box("off.floor", (9, 11, 0.1), (G.OX, -2.0, -0.05), wood)
    kit.box("off.ceiling", (9, 11, 0.2), (G.OX, -2.0, oh + 0.1), kit.emit("#fff1dc", 0.75, "offceil"))
    kit.box("off.wall.b", (9, 0.4, oh + 0.3), (G.OX, oy1 + 0.2, oh / 2 - 0.05), pink)
    kit.box("off.wall.w", (0.4, 11, oh + 0.3), (ox0 - 0.2, -2.0, oh / 2 - 0.05), pink)
    kit.box("off.wall.e", (0.4, 11, oh + 0.3), (ox1 + 0.2, -2.0, oh / 2 - 0.05), pink)
    band = pl("#7fe0c4", 0.75)
    kit.box("off.band.b", (8, 0.03, 0.9), (G.OX, oy1 - 0.015, 0.45), band)
    # the counter, with a front panel and a darker top
    kit.box("off.counter", (3.4, 0.6, 1.0), (G.OX - 0.2, G.CNT_Y, 0.5), pl("#b07a4b", 0.55), bevel=0.01)
    kit.box("off.counter.top", (3.5, 0.7, 0.05), (G.OX - 0.2, G.CNT_Y, 1.025), pl("#7a4a28", 0.5), bevel=0.01)
    kit.box("off.counter.stripe", (3.4, 0.03, 0.14), (G.OX - 0.2, G.CNT_Y - 0.315, 0.7), pl("#ff5fa2", 0.7))
    # the desk bell: a brass dome on a base, a button on top (a big, readable bell)
    bx, by = G.BELL
    brass = pl("#e0a830", 0.25, spec=0.8)
    kit.cyl("bell.base", 0.3, 0.05, (bx, by, 1.075), pl("#9a6a18", 0.3, spec=0.7), n=20)
    kit.sphere("bell.dome", 0.25, (bx, by, 1.1), brass, seg=18).scale = (1.0, 1.0, 0.8)
    kit.cyl("bell.button", 0.045, 0.07, (bx, by, 1.33), pl("#c9ced6", 0.3, spec=0.7), n=10)
    # a sunny window and a framed picture
    kit.box("off.win.frame", (1.5, 0.06, 1.4), (G.OX - 2.4, oy1 - 0.03, 1.7), pl("#fffaf0", 0.6))
    noshadow(kit.box("off.win", (1.3, 0.04, 1.2), (G.OX - 2.4, oy1 - 0.06, 1.7), kit.emit("#cfeaff", 1.3, "offwin")))
    pm, _ = imat(kit, "offpic", sunburst_image(), 0.9)
    kit.box("off.pic.frame", (1.2, 0.04, 0.95), (G.OX + 0.3, oy1 - 0.02, 2.0), pl("#fffaf0", 0.6))
    noshadow(kit.plane("off.pic", (1.08, 0.81), (G.OX + 0.3, oy1 - 0.045, 2.0), pm, rot=(math.pi / 2, 0, 0)))
    kit.prop("houseplant_1", (G.OX - 3.4, 2.5, 0), scale=2.0)
    # the key board: wood, three columns of two hooks, a numeral plate over each, keys with diamond fobs
    bxx, byy = G.BOARD[0], oy1 - 0.02
    kit.box("board", (1.2, 0.04, 0.95), (bxx, byy, 1.55), pl("#8a5a30", 0.6), bevel=0.01)
    kit.box("board.inset", (1.1, 0.02, 0.85), (bxx, byy - 0.03, 1.55), pl("#a8703a", 0.6))
    steel = pl("#c9ced6", 0.3, spec=0.7)
    fobm = pl("#ff9f43", 0.5)
    for ci, (ch, n_keys) in enumerate((("5", 2), ("6", 0), ("7", 2))):
        cxx = bxx + (ci - 1) * 0.36
        numeral(kit, f"board.num{ch}", ch, 0.2, (cxx, byy - 0.045, 1.88), "#ffffff", "#2a7a66")
        for hi in range(2):
            hxx = cxx + (hi - 0.5) * 0.16
            kit.box(f"board.hook{ch}{hi}", (0.025, 0.07, 0.025), (hxx, byy - 0.07, 1.68), brass)
            if hi < n_keys:
                kit.box(f"board.ring{ch}{hi}", (0.04, 0.012, 0.04), (hxx, byy - 0.085, 1.62), steel)
                kit.box(f"board.fob{ch}{hi}", (0.14, 0.03, 0.14), (hxx, byy - 0.1, 1.5), fobm, rot=(0, math.pi / 4, 0), bevel=0.01)
    for i, (x, y) in enumerate(((-1.0, 0.0), (1.0, 0.0), (-1.0, -3.0), (1.0, -3.0))):
        a = kit.light(f"off.fill{i}", "AREA", (G.OX + x, y, oh - 0.15), 150, "#fff3e0", size=2.5, shadow=False)
        kit.aim(a, (G.OX + x, y, 0.0))
    s = kit.light("off.face", "AREA", (G.OX, -3.2, 2.4), 220, "#fff6ec", size=2.5, shadow=False)
    kit.aim(s, (G.OX, 2.0, 1.4))


brass = None


def build_props(kit):
    global brass
    pl = kit.plastic
    # the held card: a cream slab with the picture 8 mm in front of it
    root = kit.empty("card", (0, 0, -40))
    kit.box("card.body", (0.55, 0.012, 0.42), (0, 0, 0), pl("#fff1cf", 0.7), root, bevel=0.003)
    m, tex = imat(kit, "cardpic", card_image("ours", 5), 1.0)
    pic = kit.plane("card.pic", (0.53, 0.4), (0, -0.016, 0), m, root, rot=(math.pi / 2, 0, 0))
    noshadow(pic)
    W["card"], W["cardtex"], W["cardimgs"], W["cardnow"] = root, tex, {}, ("ours", 5)
    # the pen
    pen = kit.empty("pen", (0, 0, -40))
    kit.box("pen.body", (0.014, 0.014, 0.17), (0, 0, 0), pl("#1c2744", 0.4), pen, bevel=0.004)
    kit.box("pen.tip", (0.008, 0.008, 0.03), (0, 0, -0.1), pl("#c9ced6", 0.3, spec=0.7), pen)
    W["pen"] = pen
    # the key with its big diamond fob, lying on the desk: pink tally of two strokes scratched in it (the lore)
    key = kit.empty("key", (0, 0, -40))
    kit.box("key.fob", (0.22, 0.22, 0.03), (0, 0, 0.016), pl("#ff9f43", 0.45), key, rot=(0, 0, math.pi / 4), bevel=0.01)
    numeral(kit, "key.num", "6", 0.1, (0, 0.04, 0.036), "#ffffff", "#e8742a", key, rot=(0, 0, 0))
    for i in (-1, 1):   # the lore tally: two strokes, motel pink, big enough to read
        kit.box(f"key.tally{i}", (0.02, 0.1, 0.006), (i * 0.04, -0.07, 0.045), pl("#ff5fa2", 0.5), key)
    brs = pl("#e0a830", 0.25, spec=0.8)
    kit.box("key.ring", (0.06, 0.06, 0.012), (0.02, 0.17, 0.008), brs, key, bevel=0.004)
    kit.box("key.shaft", (0.2, 0.02, 0.012), (0.12, 0.24, 0.008), brs, key, bevel=0.004)
    kit.box("key.tooth", (0.03, 0.05, 0.012), (0.2, 0.27, 0.008), brs, key, bevel=0.004)
    W["key"] = key
    # the shirts on the desk: two stacks of folded squares
    st = kit.empty("shirts", (0, 0, -40))
    for i in range(3):
        kit.box(f"shirts.teal{i}", (0.38, 0.32, 0.07), (-0.26, 0.0, 0.035 + i * 0.07), pl("#2ec4b6", 0.8), st, bevel=0.012)
        kit.box(f"shirts.yel{i}", (0.38, 0.32, 0.07), (0.26, 0.0, 0.035 + i * 0.07), pl("#ffb02e", 0.8), st, bevel=0.012)
    kit.box("shirts.tealstripe", (0.38, 0.012, 0.07), (-0.26, -0.165, 0.105), pl("#1b8f84", 0.8), st)
    kit.box("shirts.yelstripe", (0.38, 0.012, 0.07), (0.26, -0.165, 0.105), pl("#ff7a2e", 0.8), st)
    W["shirts"] = st
    # the one folded teal square Dad holds
    sh = kit.empty("shirt", (0, 0, -40))
    kit.box("shirt.body", (0.6, 0.05, 0.56), (0, 0, 0), pl("#2ec4b6", 0.8), sh, bevel=0.025)
    kit.box("shirt.fold", (0.6, 0.012, 0.1), (0, -0.03, -0.23), pl("#1b8f84", 0.8), sh)
    kit.box("shirt.collar", (0.22, 0.014, 0.08), (0, -0.032, 0.24), pl("#f4ecd8", 0.8), sh)
    W["shirt"] = sh


def build_tag(kit):
    cam = kit.OBJ["cam"]
    root = kit.empty("tag", (0, 0, 0), cam)
    W["tag"] = root
    m, tex = imat(kit, "tag", card_image("ours", 5), 1.0)
    noshadow(kit.plane("tag.plane", (1.0, 0.75), (0, 0, 0), m, root))
    W["tagtex"], W["tagimgs"], W["tagn"] = tex, {}, 5


# ---------------------------------------------------------------------------------------------- build / animate
def build(kit, story, tl):
    tl["cues"].sort(key=lambda c: c["t"])
    global brass
    brass = kit.plastic("#e0a830", 0.3, spec=0.7)
    build_room(kit)
    build_ext(kit)
    build_office(kit)
    build_props(kit)
    build_tag(kit)
    return {}


def cam_now(story, tl, t):
    from blocky import polish
    if "specs" not in W:
        W["specs"] = polish.cam_specs(story, tl, polish.spec(story))
    shot = next((x for x in tl["shots"] if x["start"] <= t < x["end"]), tl["shots"][-1])
    keys = W["specs"][shot["id"]]["cam"]
    u = (t - shot["start"]) / max(1e-6, shot["end"] - shot["start"])
    if u <= keys[0][0] or len(keys) == 1:
        k = keys[0]
        return k[1], k[2], k[3]
    for a, b in zip(keys, keys[1:]):
        if u <= b[0]:
            v = ss((u - a[0]) / max(1e-6, b[0] - a[0]))
            lerp = lambda p, q: [p[i] + (q[i] - p[i]) * v for i in range(3)]
            return lerp(a[1], b[1]), lerp(a[2], b[2]), a[3] + (b[3] - a[3]) * v
    k = keys[-1]
    return k[1], k[2], k[3]


def hand(who, sx):
    ob = bpy.data.objects.get(f"{who}.arm{sx}")
    if ob is None:
        return None
    return ob.matrix_world @ Vector((0, 0, -1.55))


def set_img(root_tex, store, key, maker):
    if key not in store:
        img = bpy.data.images.load(maker(*key))
        img.colorspace_settings.name = "sRGB"
        store[key] = img
    root_tex.image = store[key]


def animate(kit, story, tl, t, ctx):
    _animate(kit, story, tl, t, ctx)
    win = sample("win", tl, t, {"v": 1.0})["v"]
    return {"win.light": 0.25 + 0.75 * win}


def _animate(kit, story, tl, t, ctx):
    if "mancollar" not in W:
        up = bpy.data.objects.get("man.upper") or bpy.data.objects.get("man.torso")
        if up is not None:      # a white shirt collar, wider than the suit's, so the back of his neck reads
            W["mancollar"] = kit.box("man.collar2", (1.5, 1.12, 0.3), (0, 0, 1.97), kit.plastic("#f6f6f6", 0.6), up, bevel=0.06)
    bpy.context.view_layer.update()
    camloc, _, _ = cam_now(story, tl, t)
    # ---- the rule card on the camera
    n = max(1, min(5, int(round(sample("stars", tl, t, {"n": 5})["n"]))))
    if n != W["tagn"]:
        set_img(W["tagtex"], W["tagimgs"], ("ours", n), card_image)
        W["tagn"] = n
    # ---- the window: day, night, dawn, eased
    wv = sample("win", tl, t, {"v": 1.0})["v"]
    day, night, dawn = (0.81, 0.92, 1.0), (0.1, 0.16, 0.36), (1.0, 0.72, 0.5)
    if wv >= 0.55:
        u = (wv - 0.55) / 0.45
        c = tuple(dawn[i] + (day[i] - dawn[i]) * u for i in range(3))
    else:
        u = wv / 0.55
        c = tuple(night[i] + (dawn[i] - night[i]) * u for i in range(3))
    em = W["winmat"].node_tree.nodes["Emission"]
    em.inputs["Color"].default_value = (c[0], c[1], c[2], 1.0)
    em.inputs["Strength"].default_value = 0.3 + 0.45 * min(1.0, wv / 0.55)
    # ---- the drawer and the closet doors
    W["drawer"].location.y = G.DESK[1] - 0.42 * sample("drawer", tl, t, {"v": 0.0})["v"]
    cv = sample("closet", tl, t, {"v": 0.0})["v"]
    for piv, side in W["doors"]:
        piv.rotation_euler = (0, 0, math.radians(-165 * cv if side == -1 else 165 * cv))
    # ---- the held card, the pen, the key on the desk, the shirts, the shirt in Dad's hands
    cd = sample("card", tl, t, {"mode": "none", "who": "me", "kind": "ours"})
    card = W["card"]
    cx, cy = camloc[0], camloc[1]
    if cd["mode"] == "hand":
        h = hand(cd["who"], 1)
        if h is not None:
            ph = math.atan2(cy - h.y, cx - h.x)
            card.location = (h.x + 0.12 * math.cos(ph), h.y + 0.12 * math.sin(ph), h.z + 0.2)
            card.rotation_euler = (0, 0, ph + math.pi / 2)
            card.scale = (1.3, 1.3, 1.3)
            _card_pic(cd["kind"])
        else:
            card.location = (0, 0, -40)
    elif cd["mode"] == "desk":
        card.location = (G.DESK[0] + 0.12, G.DESK[1] + 0.2, G.DESK_TOP + 0.008)
        card.rotation_euler = (-math.pi / 2, 0, math.radians(14))
        _card_pic(cd["kind"])
    else:
        card.location = (0, 0, -40)
    pc = sample("pen", tl, t, {"mode": "none", "who": "me"})
    pen = W["pen"]
    h = hand(pc["who"], -1) if pc["mode"] == "hand" else None
    if h is not None and cd["mode"] == "hand" and card.location.z > -10:
        # the pen scribbles on the card face: it rides the card, in front of it, sweeping along the writing lines
        ph = math.atan2(cy - card.location.y, cx - card.location.x)
        sw, dn = 0.14 * math.sin(t * 11.0), 0.06 * math.sin(t * 5.3)
        pen.location = (card.location.x + 0.1 * math.cos(ph) + sw * math.cos(ph + math.pi / 2),
                        card.location.y + 0.1 * math.sin(ph) + sw * math.sin(ph + math.pi / 2), card.location.z - 0.02 + dn)
        pen.rotation_euler = (math.radians(-25), 0, ph + math.pi / 2 + math.radians(20))
    elif h is not None:
        pen.location = (h.x, h.y - 0.03, h.z + 0.07)
        pen.rotation_euler = (math.radians(-25), 0, math.radians(20))
    else:
        pen.location = (0, 0, -40)
    kc = sample("key", tl, t, {"mode": "none"})
    W["key"].location = (G.DESK[0] + 0.45, G.DESK[1] + 0.3, G.DESK_TOP + 0.16) if kc["mode"] == "desk" else (0, 0, -40)
    W["key"].rotation_euler = (1.05, 0, math.radians(6))    # the fob leans back against the wall, facing the room
    W["key"].scale = (3.0, 3.0, 3.0)
    W["lead"].location = (0, 0.05, G.DESK_TOP - 0.03 if sample("drawer", tl, t, {"v": 0.0})["v"] > 0.5 else -40)
    W["shirts"].location = (G.DESK[0] - 0.05, G.DESK[1] + 0.3, G.DESK_TOP) if sample("shirts", tl, t, {"v": 0.0})["v"] > 0.5 else (0, 0, -40)
    sc = sample("shirt", tl, t, {"mode": "none", "who": "dad", "f": 0.0})
    f = sc["f"]
    f1, f2 = min(1.0, max(0.0, f)), min(1.0, max(0.0, f - 1.0))
    fs = (1 - 0.5 * f1, 1 + f1 * 0.5 + f2 * 1.0, 1 - 0.5 * f2)      # two folds: half the width, then half the height
    sh = W["shirt"]
    ha, hb = hand(sc["who"], 1), hand(sc["who"], -1)
    if sc["mode"] == "hand" and ha is not None and hb is not None:
        mid = (ha + hb) / 2
        ph = math.atan2(cy - mid.y, cx - mid.x)
        sh.location = (mid.x + 0.1 * math.cos(ph), mid.y + 0.1 * math.sin(ph), mid.z - 0.12)
        sh.rotation_euler = (0, 0, ph + math.pi / 2)
        sh.scale = (1.25 * fs[0], 1.25 * fs[1], 1.25 * fs[2])
    elif sc["mode"] == "desk":
        sh.location = (G.DESK[0] + 0.15, G.DESK[1] + 0.25, G.DESK_TOP + 0.11)
        sh.rotation_euler = (-math.pi / 2, 0, math.radians(8))     # flat on the desk, its face up
        sh.scale = (1.7 * fs[0], 1.7 * fs[1], 1.7 * fs[2])
    else:
        sh.location = (0, 0, -40)
    return {}


def _card_pic(kind):
    key = (kind, 1 if kind in ("old", "last") else 5)
    if W["cardnow"] != key:
        set_img(W["cardtex"], W["cardimgs"], key, card_image)
        W["cardnow"] = key
