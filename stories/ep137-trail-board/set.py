"""ep137-trail-board: a green trailhead at the edge of town, seen at morning gold, at dusk and at sunrise.

One bright plastic set (the "closer" look): a gravel lot where a town street ends, a forest-green board on two posts
(2.4 m wide, cream glyph lettering of our own, never real words), a small green warden's hut with a white door and no
lamp, a pine bench, a white picket fence, tall pines, a shallow blue creek along the right, green hills and a low sun.

Built here (everything in build(), shown and hidden by cues, nothing made lazily):
- THE BOARD: five single glyph lines ("one0".."one4") and a full four-line message ("full"); the "board" cue says which.
  Clue C1 is the count of lines: one short line against four edge-to-edge ones. A two-stroke tally on the left post.
- THE LOOKS: "m" pale morning gold (also the sunrise), "d" dusk (a huge low orange sun in a pink-orange sky). Looks
  change on cuts, except S15 (story.json shot key "fade": ["d", "m"]), a slow ease across the whole held shot.
- THE PATH: a packed-earth strip along the creek, hidden until the "path" cue; ferns stand there until then.
- A big red canoe ("canoe" cue drifts it), a giant red mushroom ("mush" cue), June's pack and stick ("gear" cue).
Cues: board (g), path (on), canoe (from, to, dur), mush (on, pos), gear (on).
"""

from __future__ import annotations

import math

import bpy
from mathutils import Vector as V

from blocky import bl_story  # noqa: F401  (cam_at)

BOARD_Y = 0.0
PANEL_Z0, PANEL_Z1 = 0.9, 2.5
_n = [0]


def nm(p):
    _n[0] += 1
    return f"{p}.{_n[0]}"


def ss(x):
    x = min(1.0, max(0.0, x))
    return x * x * (3 - 2 * x)


def lerp(a, b, u):
    return a + (b - a) * u


def hexrgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def mixhex(a, b, u):
    ra, rb = hexrgb(a), hexrgb(b)
    return tuple(lerp(x, y, u) / 255.0 for x, y in zip(ra, rb))


class K:
    kit = None


def P(hexc, rough=0.5, spec=0.35):
    return K.kit.plastic(hexc, rough, spec=spec)


def B(parent, size, loc, mat, name="b", bevel=0.01, rot=(0, 0, 0)):
    return K.kit.box(nm(name), size, loc, mat, parent, rot, bevel)


def E(parent=None, loc=(0, 0, 0), name="e", rot=(0, 0, 0)):
    return K.kit.empty(nm(name), loc, parent, rot)


def hide(ob, h=True):
    ob.hide_render = h
    for c in ob.children_recursive:
        c.hide_render = h


# --------------------------------------------------------------------------------------------------- the looks
LOOKS = {
    # pale morning gold; the sun is behind the trees (no disc)
    "m": {"sky": ["#fff3c4", "#ffe79a", "#cfe6ff", "#8cc6f6"], "world": 1.0, "sun": (35, 30, 5.0, "#fff0c0"),
          "fill": 0.8, "exp": 0.0, "disc_z": -60.0},
    # dusk: a huge low orange sun in a pink-orange sky
    "d": {"sky": ["#ffa24a", "#ff8a3c", "#f6a0a8", "#d48ad0"], "world": 0.9, "sun": (165, 10, 4.5, "#ff9a50"),
          "fill": 1.15, "exp": 0.0, "disc_z": 46.0},
}


def mix_look(a, b, u):
    out = {}
    for k in a:
        va, vb = a[k], b[k]
        if k == "sky":
            out[k] = [mixhex(x, y, u) for x, y in zip(va, vb)]
        elif k == "sun":
            out[k] = (lerp(va[0], vb[0], u), lerp(va[1], vb[1], u), lerp(va[2], vb[2], u), mixhex(va[3], vb[3], u))
        else:
            out[k] = lerp(va, vb, u)
    return out


def look_at(ctx, tl, t):
    cur = next((s for s in tl["shots"] if s["start"] <= t < s["end"]), tl["shots"][-1])
    sd = ctx["shots"][cur["id"]]
    fade = sd.get("fade")
    if fade:
        u = ss((t - cur["start"]) / max(1e-6, cur["end"] - cur["start"]))
        return mix_look(LOOKS[fade[0]], LOOKS[fade[1]], u), cur
    A = LOOKS[sd.get("look", "m")]
    return mix_look(A, A, 0.0), cur


def cue_at(tl, name, t):
    out = {}
    for c in tl.get("cues", []):
        if c["name"] == name and c["t"] <= t + 1e-9:
            out = c
    return out


# --------------------------------------------------------------------------------------------------- glyphs
def glyph(parent, seed, cx, cz, w, h, th, mat):
    """One made-up letter from a few cream bars, centred at (cx, cz) on the board's front (never a real letter)."""
    y = -0.14
    k = seed % 7
    hw, hh = w / 2, h / 2
    r = math.radians
    if k == 0:    # two slanted strokes
        bars = [(th, h, -hw * 0.45, 0, r(24)), (th, h, hw * 0.45, 0, r(24))]
    elif k == 1:  # three dots going down
        d_ = th * 1.5
        bars = [(d_, d_, 0, hh - d_ / 2, 0), (d_, d_, 0, 0, 0), (d_, d_, 0, -hh + d_ / 2, 0)]
    elif k == 2:  # a dot over a long slash
        bars = [(th * 1.5, th * 1.5, hw * 0.5, hh - th * 0.75, 0), (th, h * 0.8, -hw * 0.1, -h * 0.1, r(-30))]
    elif k == 3:  # an arrowhead
        bars = [(th, h * 0.62, 0, hh * 0.35, r(52)), (th, h * 0.62, 0, -hh * 0.35, r(-52))]
    elif k == 4:  # a stem with two side ticks
        bars = [(th, h, 0, 0, 0), (w * 0.45, th, -hw * 0.5, hh * 0.35, 0), (w * 0.45, th, hw * 0.5, -hh * 0.35, 0)]
    elif k == 5:  # two bars and a dot
        bars = [(w, th, 0, hh * 0.45, 0), (w, th, 0, -hh * 0.1, 0), (th * 1.5, th * 1.5, 0, -hh + th * 0.75, 0)]
    else:         # a diamond
        bars = [(th, h * 0.62, -hw * 0.4, hh * 0.3, r(40)), (th, h * 0.62, hw * 0.4, hh * 0.3, r(-40)),
                (th, h * 0.62, -hw * 0.4, -hh * 0.3, r(-40)), (th, h * 0.62, hw * 0.4, -hh * 0.3, r(40))]
    for sx, sz, x, z, rot in bars:
        B(parent, (sx, 0.06, sz), (cx + x, y, cz + z), mat, "glyph", 0.0, rot=(0, rot, 0))


def build_board(kit):
    root = E(None, (0, BOARD_Y, 0), "board")
    green, dark, cream, wood = P("#1f5a3a", 0.55, 0.2), P("#16442b", 0.6, 0.2), P("#fff4d6", 0.5, 0.3), P("#8a6238", 0.7, 0.1)
    B(root, (2.4, 0.10, PANEL_Z1 - PANEL_Z0), (0, -0.05, (PANEL_Z0 + PANEL_Z1) / 2), green, "panel", 0.02)
    for sx in (-1, 1):
        B(root, (0.16, 0.16, 2.3), (sx * 0.95, 0.08, 1.15), wood, "post", 0.02)
    # a cream trim frame on the front (3 cm proud of the panel)
    zc, hz = (PANEL_Z0 + PANEL_Z1) / 2, (PANEL_Z1 - PANEL_Z0) / 2
    B(root, (2.4, 0.03, 0.07), (0, -0.115, PANEL_Z1 - 0.035), cream, "trim", 0.006)
    B(root, (2.4, 0.03, 0.07), (0, -0.115, PANEL_Z0 + 0.035), cream, "trim", 0.006)
    for sx in (-1, 1):
        B(root, (0.07, 0.03, 2 * hz), (sx * 1.165, -0.115, zc), cream, "trim", 0.006)
    # the tally at the foot of the left post: two strokes, 3 cm proud of the post's front face
    tally = E(root, (0, 0, 0), "tally")
    for sx in (-0.99, -0.91):
        B(tally, (0.032, 0.03, 0.26), (sx, -0.015, 0.34), cream, "tally", 0.004)
    hide(tally, True)
    groups = {}
    for i in range(5):                        # single lines, big and few: five glyphs on the middle
        g = E(root, (0, 0, 0), f"one{i}")
        for j in range(5):
            glyph(g, (i * 3 + j * 2 + i) % 7 if (i + j) % 2 else (i + j * 3 + 1) % 7, -0.88 + 0.44 * j, 1.7, 0.30, 0.46, 0.085, cream)
        groups[f"one{i}"] = g
    g = E(root, (0, 0, 0), "full")
    for r in range(4):                        # four lines, edge to edge, top to bottom
        for j in range(7):
            glyph(g, (r * 5 + j * 3 + 2) % 7, -1.05 + 0.35 * j, 2.2 - 0.33 * r, 0.22, 0.25, 0.05, cream)
    groups["full"] = g
    for g in groups.values():
        hide(g, True)
    groups["tally"] = tally
    return groups


# --------------------------------------------------------------------------------------------------- set pieces
def build_bench(kit):
    w = P("#c89a5c", 0.7, 0.1)
    d = P("#a87a42", 0.7, 0.1)
    B(None, (1.8, 0.5, 0.07), (5.0, 1.2, 0.45), w, "seat", 0.012)
    B(None, (1.7, 0.05, 0.34), (5.0, 0.93, 0.28), d, "apron", 0.01)
    for sx in (-0.8, 0.8):
        B(None, (0.1, 0.5, 0.45), (5.0 + sx, 1.2, 0.225), d, "bleg", 0.01)
    B(None, (1.8, 0.06, 0.45), (5.0, 1.46, 0.85), w, "back", 0.012)
    for sx in (-0.8, 0.8):
        B(None, (0.08, 0.08, 0.5), (5.0 + sx, 1.46, 0.7), d, "bpost", 0.01)


def build_hut(kit):
    B(None, (2.4, 2.0, 2.3), (-5.5, 6.5, 1.15), P("#3d8f4f", 0.6, 0.2), "hut", 0.03)
    B(None, (2.8, 2.4, 0.18), (-5.5, 6.5, 2.35), P("#2a6a3a", 0.6, 0.2), "hutroof", 0.03)
    for sx in (-1, 1):
        B(None, (1.5, 2.4, 0.16), (-5.5 + sx * 0.62, 6.5, 2.62), P("#2a6a3a", 0.6, 0.2), "hutgable", 0.03, rot=(0, -sx * 0.5, 0))
    B(None, (0.95, 0.05, 1.95), (-5.5, 5.47, 1.0), P("#fbfbf6", 0.5, 0.2), "hutdoor", 0.012)
    B(None, (1.1, 0.04, 2.1), (-5.5, 5.485, 1.05), P("#d9d6c8", 0.6, 0.1), "doorframe", 0.01)


def build_fence(kit):
    white = P("#f6f6f2", 0.5, 0.2)
    for i in range(70):
        x = -14.0 + 0.4 * i
        B(None, (0.12, 0.04, 1.05), (x, 9.5, 0.525), white, "picket", 0.01)
    for z in (0.35, 0.8):
        B(None, (28, 0.05, 0.08), (0, 9.46, z), white, "frail", 0.01)


def build_canoe(kit):
    root = E(None, (8.4, 3.5, 0.0), "canoe")
    red, dk = P("#ee3a26", 0.5, 0.3), P("#8a2a20", 0.6, 0.2)
    B(root, (0.9, 3.0, 0.14), (0, 0, 0.12), red, "keel", 0.05)
    for sx in (-1, 1):
        B(root, (0.1, 3.0, 0.38), (sx * 0.45, 0, 0.33), red, "side", 0.04, rot=(0, -sx * 0.12, 0))
        B(root, (0.1, 0.9, 0.38), (sx * 0.3, -1.55, 0.35), red, "bow", 0.04, rot=(0, 0, sx * 0.42))
        B(root, (0.1, 0.9, 0.38), (sx * 0.3, 1.55, 0.35), red, "stern", 0.04, rot=(0, 0, -sx * 0.42))
    for y in (-0.7, 0.7):
        B(root, (0.9, 0.12, 0.08), (0, y, 0.44), dk, "thwart", 0.02)
    B(root, (0.7, 2.7, 0.04), (0, 0, 0.2), dk, "floor", 0.01)
    hide(root, True)
    return root


def build_mushroom(kit):
    root = E(None, (0, 0, 0), "mush")
    kit.cyl(nm("stem"), 0.1, 0.42, (0, 0, 0.21), P("#f4ead2", 0.6), root, n=20)
    cap = kit.sphere(nm("cap"), 0.3, (0, 0, 0.42), P("#d23b2a", 0.45, 0.35), root, seg=20)
    cap.scale = (1.0, 1.0, 0.62)
    for i, (x, y) in enumerate(((0.0, 0.0), (0.16, 0.1), (-0.15, 0.12), (0.1, -0.17), (-0.12, -0.14), (0.25, -0.03), (-0.24, -0.02))):
        z = 0.42 + math.sqrt(max(0.0, 0.09 - x * x - y * y)) * 0.62 + 0.0
        s = kit.sphere(nm("dot"), 0.045, (x, y, z - 0.005), P("#fffdf0", 0.5), root, seg=10)
        s.scale = (1.0, 1.0, 0.5)
    hide(root, True)
    return root


def build_gear(kit):
    root = E(None, (0, 0, 0), "gear")
    B(root, (0.5, 0.32, 0.62), (3.95, 1.2, 0.8), P("#f08a24", 0.6, 0.15), "pack", 0.05)
    B(root, (0.36, 0.06, 0.22), (3.95, 1.03, 0.78), P("#c96a12", 0.6, 0.15), "packflap", 0.02)
    K.kit.cyl(nm("stick"), 0.025, 1.3, (3.62, 1.4, 0.62), P("#8a6238", 0.7, 0.1), root, rot=(0.0, 0.18, 0.0), n=10)
    hide(root, True)
    return root


def build_world(kit):
    # ground: grass everywhere, a pale gravel lot, a strip of asphalt where the street ends
    B(None, (400, 300, 0.4), (0, 60, -0.2), P("#6cc24a", 0.85, 0.1), "lawn", 0.0)
    B(None, (15.0, 18.0, 0.06), (-2.0, 0.0, 0.0), P("#b9ae92", 0.9, 0.05), "gravel", 0.0)
    B(None, (8.0, 40.0, 0.05), (-2.0, -28.0, 0.0), kit.texture("asphalt", 0.5, tint="#b8bcc6"), "street", 0.0)
    B(None, (0.15, 40.0, 0.07), (2.1, -28.0, 0.0), P("#e8e8e0", 0.8, 0.05), "curb", 0.0)
    # the creek (a 2 cm step proud of the grass) and the path strip
    B(None, (4.0, 90.0, 0.06), (10.2, 30.0, 0.0), P("#5fb8e8", 0.12, 0.6), "creek", 0.0)
    B(None, (0.5, 90.0, 0.05), (8.0, 30.0, 0.0), P("#8fd06a", 0.85, 0.1), "bank", 0.0)
    path = B(None, (1.0, 19.0, 0.05), (7.0, 9.5, 0.0), P("#b88a58", 0.9, 0.05), "path", 0.0)
    hide(path, True)
    # hills and pines
    for i, (x, y, r, h, c) in enumerate(((-30, 78, 38, 13, "#4f9e56"), (28, 82, 42, 15, "#5aa860"), (-2, 92, 46, 30, "#6ab26a"),
                                         (-62, 70, 30, 10, "#5aa860"), (60, 72, 30, 11, "#4f9e56"))):
        kit.cyl(nm("hill"), r, h, (x, y, h / 2 - 0.2), P(c, 0.9, 0.05), None, n=24, r2=r * 0.35)
    trees = []
    for x in (-18, -15.5, -13, -10.5, -8, -5.8, -4.2):
        trees.append(("pinetree_1" if int(x) % 2 else "pinetree_2", x, 12.5 + (x * 7) % 4, 9 + (x * 3) % 3))
    for x in (4.6, 6.2, 8.6, 11.5, 14, 16.5, 19):
        trees.append(("pinetree_2" if int(x) % 2 else "pinetree_1", x, 12.0 + (x * 5) % 5, 9.5 + (x * 3) % 3))
    for i in range(10):
        trees.append(("pinetree_1" if i % 2 else "pinetree_2", 14.5 + (i * 3) % 7, -3 + i * 3.4, 9 + (i % 3)))
    for i in range(6):
        trees.append(("pinetree_2", -14 - (i % 3) * 2.5, -3 + i * 4.0, 9 + (i % 2)))
    for i, (nme, x, y, h) in enumerate(trees):
        try:
            kit.prop(nme, (x, y, 0), rot=37 * i, height=h, tint="#7fd070")
        except Exception:
            pass
    ferns = []
    for i in range(12):
        try:
            ferns.append(kit.prop("bush_2" if i % 2 else "plant_1", (6.4 + 0.5 * ((i * 7) % 3), 5.0 + 1.1 * i, 0), rot=50 * i,
                                  height=0.9 + 0.2 * (i % 3), tint="#58c24a"))
        except Exception:
            pass
    return {"path": path, "ferns": ferns}


# --------------------------------------------------------------------------------------------------- build
def build(kit, story, tl):
    K.kit = kit
    ctx = {"story": story}
    ctx["shots"] = {s["id"]: s for s in story["shots"]}
    sc = bpy.context.scene
    nt = sc.world.node_tree
    bg = nt.nodes["Background"]
    tc = nt.nodes.new("ShaderNodeTexCoord")
    sep = nt.nodes.new("ShaderNodeSeparateXYZ")
    nt.links.new(tc.outputs["Generated"], sep.inputs[0])
    mr = nt.nodes.new("ShaderNodeMapRange")
    mr.inputs["From Min"].default_value = 0.0
    mr.inputs["From Max"].default_value = 0.55
    mr.clamp = True
    nt.links.new(sep.outputs["Z"], mr.inputs["Value"])
    ramp = nt.nodes.new("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].position = 0.0
    ramp.color_ramp.elements[1].position = 1.0
    ramp.color_ramp.elements.new(0.22)
    ramp.color_ramp.elements.new(0.55)
    nt.links.new(mr.outputs["Result"], ramp.inputs["Fac"])
    nt.links.new(ramp.outputs["Color"], bg.inputs["Color"])
    ctx["ramp"], ctx["bg"] = ramp, bg
    ctx["sun"] = kit.light("sun", "SUN", (0, 0, 50), 5.0, "#fff1d8", size=0.1)
    ctx["sun"].data.angle = 0.06
    ctx["fill"] = kit.light("camfill", "POINT", (0, 0, 2), 60, "#ffe9cf", size=0.6, shadow=False)
    # the low sun: a big emissive disc far behind the board, below the horizon (hidden) in every look but dusk
    ctx["disc"] = kit.sphere("sundisc", 15.0, (1.0, 95.0, -60.0), kit.emit("#ff7a22", 3.2), None, seg=32)
    try:
        ctx["disc"].visible_shadow = False
    except Exception:
        pass
    build_world_ = build_world(kit)
    ctx.update(build_world_)
    build_bench(kit)
    build_hut(kit)
    build_fence(kit)
    ctx["groups"] = build_board(kit)
    ctx["canoe"] = build_canoe(kit)
    ctx["mush"] = build_mushroom(kit)
    ctx["gear"] = build_gear(kit)
    return ctx


# --------------------------------------------------------------------------------------------------- animate
def animate(kit, story, tl, t, ctx):
    sc = bpy.context.scene
    L, cur = look_at(ctx, tl, t)
    sd = ctx["shots"][cur["id"]]
    for el, c in zip(ctx["ramp"].color_ramp.elements, L["sky"]):
        el.color = (kit.srgb(c[0]), kit.srgb(c[1]), kit.srgb(c[2]), 1.0)
    ctx["bg"].inputs["Strength"].default_value = L["world"]
    az, el_, en, scol = L["sun"]
    azr, elr = math.radians(az), math.radians(el_)
    pos = V((math.sin(azr) * math.cos(elr), -math.cos(azr) * math.cos(elr), math.sin(elr)))
    sun = ctx["sun"]
    sun.rotation_euler = (-pos).to_track_quat("-Z", "Y").to_euler()
    sun.data.color = (kit.srgb(scol[0]), kit.srgb(scol[1]), kit.srgb(scol[2]))
    dz = L["disc_z"]
    ctx["disc"].location = (1.0, 95.0, dz)
    ctx["disc"].hide_render = dz < -20
    cl, _, _, _ = bl_story.cam_at(sd, cur, t, {}, tl)
    ctx["fill"].location = (cl[0], cl[1], cl[2])
    sc.view_settings.exposure = L["exp"] + sd.get("exp", 0.0)
    ov = {"sun": en * sd.get("sun", 1.0) / 5.0, "camfill": L["fill"] * sd.get("fill", 1.0)}
    cd = kit.OBJ["cam"].data
    dof = sd.get("dof")
    if dof:
        cd.dof.use_dof = True
        cd.dof.focus_distance = dof[0]
        cd.dof.aperture_fstop = dof[1]
    else:
        cd.dof.use_dof = False
    # the board
    g = cue_at(tl, "board", t).get("g", "one0")
    for k, o in ctx["groups"].items():
        hide(o, (not sd.get("tally")) if k == "tally" else k != g)
    # the path and the ferns
    on = bool(cue_at(tl, "path", t).get("on"))
    hide(ctx["path"], not on)
    for f in ctx["ferns"]:
        hide(f, on)
    # the canoe drifts from -> to over dur
    c = cue_at(tl, "canoe", t)
    if c.get("on"):
        hide(ctx["canoe"], False)
        u = ss((t - c["t"]) / max(1e-3, c["dur"]))
        p = [lerp(a, b, u) for a, b in zip(c["from"], c["to"])]
        ctx["canoe"].location = (p[0], p[1], 0.02)
        ctx["canoe"].rotation_euler = (0, 0, math.radians(lerp(c.get("yaw0", 0), c.get("yaw1", 0), u)))
    else:
        hide(ctx["canoe"], True)
    m = cue_at(tl, "mush", t)
    if m.get("on"):
        hide(ctx["mush"], False)
        ctx["mush"].location = tuple(m["pos"])
    else:
        hide(ctx["mush"], True)
    hide(ctx["gear"], not cue_at(tl, "gear", t).get("on"))
    return ov
