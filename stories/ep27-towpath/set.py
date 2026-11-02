"""ep27-towpath: a narrowboat moored on a still canal in autumn fog. Daylight only, no lamp in any shot.

Places (metres): x runs along the canal from the boat's stern (x = 0) to its bow (x = 12), y is across it (the
towpath side is +y, the water -y, the boat's towpath skin at y = -0.15), z is up (the water at 0, the towpath at
0.5). The back deck is x 0 to 2.2, the back cabin 2.2 to 10 (three steps down from the doorway at x 2.2, Moss's bed
at their foot, my bunk against the towpath wall under the round window at x = 5), the well deck 10 to 12.
Mooring rings sit on the quay edge at x = 5, 8.5, 12, 15.5, 19, 22.5. The Long Man lies on the verge, face up.

Cues read here (all optional, each holds until the next of its kind):
- time: {"set": name in STATES, "dur": s}  light, fog and exposure: the state eases from the last one over dur
- moss: {"pos": [x, y, z], "yaw": deg, "pose": stand|sit|lie|held|climb, "head": [yaw, pitch], "ears": 0..1,
         "tail": deg, "wag": 0..1, "hold": "me", "dur": s}  Moss from here (pos and yaw ease over dur)
- long: {"x": head x, "turn": 0..1, "hidden": bool, "face": "wide"}  the Long Man's head (lying on the verge)
- hatch: {"open": 0..1, "dur": s}   the sliding roof hatch
- bolt: {"on": bool}                the bolt under the hatch
- wipe: {"to": 0..1, "dur": s}      the condensation wiped off the bunk window
- flat: {"on": bool}                the verge flattened where it lay
- tally: {"on": bool}               the two strokes on the back ring
Acting keys read here (acting.py ignores them): "lie": [x, y, z] degrees for a character lying down.
"""

from __future__ import annotations

import math
from pathlib import Path

import bpy
from mathutils import Euler, Matrix, Vector as V

from blocky import faces, kit, rig

ROOT = Path(__file__).resolve().parents[2]
BOAT_L = 12.0
SKIN_P, SKIN_C = -0.15, -1.95           # the boat's outer sides (towpath, canal)
BANK_Y = -0.13                          # the quay's edge
GROUND = 0.5                            # towpath height
DECK = 0.72                             # back deck floor
FLOOR = 0.05                            # cabin floor
ROOF = 2.0
RINGS = [5.0, 8.5, 12.0, 15.5, 19.0, 22.5]
WIN_X, WIN_Z = 5.0, 0.84                # the bunk window
LONG_KT, LONG_KL = 6.5, 11.98            # the Long Man: torso and leg stretch (rig units)
LONG_H = 1.0
PATCH = (5.15, 0.5)                    # Moss's spot by the back ring

# ---------------------------------------------------------------------------------------------- light states
# fog colour, fog density, world strength, exposure, then multipliers on the lights
STATES = {
    "past":   dict(fog="#d9cdb4", dens=0.02, ws=1.00, exp=-0.25, key=0.4, rim=0.3, fill=1.00, eye=0.0, warm=1.0),
    "grey1":  dict(fog="#c2cac9", dens=0.030, ws=0.95, exp=-0.25, key=0.7, rim=0.6, fill=1.00, eye=0.5, warm=0.0),
    "grey2":  dict(fog="#c2cac9", dens=0.024, ws=0.95, exp=-0.25, key=0.7, rim=0.6, fill=1.00, eye=0.5, warm=0.0),
    "grey3":  dict(fog="#b4bec2", dens=0.026, ws=0.90, exp=-0.25, key=0.7, rim=0.6, fill=1.00, eye=0.5, warm=0.0),
    "dawn":   dict(fog="#c8d0cf", dens=0.026, ws=1.00, exp=-0.05, key=0.9, rim=0.7, fill=1.00, eye=0.5, warm=0.0),
    "far":    dict(fog="#c2cac9", dens=0.012, ws=0.95, exp=-0.25, key=0.7, rim=0.6, fill=1.00, eye=0.5, warm=0.0),
    "wide":   dict(fog="#c6cecd", dens=0.006, ws=1.00, exp=-0.20, key=0.7, rim=0.6, fill=1.00, eye=1.0, warm=0.0),
    "wide3":  dict(fog="#a9b5ba", dens=0.003, ws=0.85, exp=-0.15, key=1.0, rim=1.0, fill=0.9, eye=1.0, warm=0.0),
    "wide2":  dict(fog="#aab6bb", dens=0.012, ws=0.85, exp=-0.20, key=1.0, rim=1.0, fill=0.85, eye=1.0, warm=0.0),
    "night":  dict(fog="#7f8f99", dens=0.026, ws=0.75, exp=-0.15, key=0.5, rim=0.4, fill=0.90, eye=0.5, warm=0.0),
    "thick":  dict(fog="#a3aeb3", dens=0.055, ws=0.55, exp=-0.25, key=1.0, rim=1.0, fill=0.85, eye=0.45, warm=0.0),
    "hook":   dict(fog="#c8d0cf", dens=0.013, ws=1.00, exp=-0.12, key=0.9, rim=0.7, fill=1.00, eye=0.5, warm=0.0),
    "scare":  dict(fog="#8e9ca2", dens=0.05, ws=0.28, exp=-0.05, key=0.3, rim=1.0, fill=0.45, eye=1.8, warm=0.0),
    "clear1": dict(fog="#c2cac9", dens=0.030, ws=0.95, exp=-0.25, key=0.7, rim=0.6, fill=1.00, eye=0.5, warm=0.0),
    "clear2": dict(fog="#cad3d1", dens=0.012, ws=1.00, exp=-0.30, key=0.5, rim=0.4, fill=1.00, eye=0.5, warm=0.4),
    "morning": dict(fog="#d4dcd8", dens=0.014, ws=1.00, exp=-0.08, key=0.4, rim=0.3, fill=1.00, eye=0.0, warm=0.6),
}
for _k, _v in STATES.items():           # the water's mirror (specular level, roughness): the high wides turn it matte so they don't white out
    _v.setdefault("wsp", 0.15 if _k in ("wide", "wide2", "wide3") else 0.9)
    _v.setdefault("wr", 0.55 if _k in ("wide", "wide2", "wide3") else 0.12)
LIGHT_BASE = {            # name -> (kind, loc, aim, power, colour, size)
    "sky": ("AREA", (8, -6, 14), (8, 0, 0), 1500, "#dfe6ea", 22),
    "warm": ("AREA", (8, -24, 5), (8, 0, 1), 9000, "#ffd9a0", 14),
    "key": ("AREA", (9, -9, 3.2), (14, 0.3, 0.5), 2200, "#a9c4d8", 6),
    "rim": ("AREA", (14, 7, 3.0), (9, 0.3, 0.6), 1800, "#cfe0e8", 5),
    "eyes": ("POINT", (5.0, 0.25, 1.6), (5.0, 0.1, 0.8), 25, "#e8f0f4", 0.3),
    "winglow": ("SPOT", (5.0, -1.55, 1.0), (5.0, 0.03, 0.84), 90, "#b9d3e6", 0.4),
    "faceside": ("AREA", (2.5, 0.9, 1.8), (5.0, 0.2, 0.85), 500, "#b4d0e2", 1.6),
    "cab a": ("AREA", (3.0, -1.05, 1.9), (3.0, -1.05, 0), 170, "#c4d2dc", 1.2),
    "cab b": ("AREA", (4.9, -1.0, 1.9), (4.9, -1.0, 0), 170, "#bccbd6", 1.4),
    "cab d": ("AREA", (7.4, -1.0, 1.85), (6.5, -1.0, 0), 170, "#bccbd6", 1.6),
    "cab e": ("AREA", (4.0, -1.65, 1.2), (4.6, -0.6, 0.9), 40, "#c4d2dc", 1.2),
    "cab c": ("AREA", (5.6, -1.0, 1.0), (4.5, -0.3, 0.8), 90, "#b4c4d0", 1.0),
    "porch": ("AREA", (1.0, -1.05, 2.6), (2.4, -1.05, 0.5), 700, "#d4dde2", 2.5),
    "hatch": ("AREA", (3.0, -1.05, 2.6), (3.0, -1.05, 0.2), 0, "#e0e8ec", 1.4),
    "lamp": ("AREA", (0, 0, 3), (0, 0, 0), 1, "#dfe8ea", 3.0),
}


def _cues(tl, name):
    return sorted((c for c in tl["cues"] if c["name"] == name), key=lambda c: c["t"])


def _last(cs, t):
    out = None
    for c in cs:
        if c["t"] <= t + 1e-9:
            out = c
    return out


def _ss(x):
    x = min(1.0, max(0.0, x))
    return x * x * (3 - 2 * x)


def _eased(cs, key, t, default):
    """A cue value that eases from the previous cue's value (for this key) over the cue's dur."""
    ks = [c for c in cs if key in c and c["t"] <= t + 1e-9]
    if not ks:
        return default
    last = ks[-1]
    before = ks[-2][key] if len(ks) > 1 else default
    u = _ss((t - last["t"]) / last["dur"]) if last.get("dur") else 1.0
    return before + (last[key] - before) * u


def workdir(tl) -> Path:
    d = ROOT / "out" / "work" / tl.get("name", "ep27-towpath") / "faces"
    d.mkdir(parents=True, exist_ok=True)
    return d


# ----------------------------------------------------------------------------------------------- small parts
def B(name, size, loc, mat, bevel=0.0, rot=(0, 0, 0), parent=None):
    return kit.box(name, size, loc, mat, parent, rot, bevel=bevel)


def span(name, x0, x1, y0, y1, z0, z1, mat, bevel=0.0):
    return kit.box(name, (x1 - x0, y1 - y0, z1 - z0), ((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2), mat, None,
                   (0, 0, 0), bevel=bevel)


def holed_panel(name, cx, cz, half, r, y0, y1, mat, n=28):
    """A square panel (y0..y1 thick, in the x-z plane) with a round hole of radius r."""
    verts, faces_ = [], []
    for k in range(n):
        a = 2 * math.pi * k / n
        c, s = math.cos(a), math.sin(a)
        m = half / max(abs(c), abs(s))
        for y in (y0, y1):
            verts.append((cx + r * c, y, cz + r * s))
            verts.append((cx + m * c, y, cz + m * s))
    for k in range(n):
        j = (k + 1) % n
        a0, a1 = 4 * k, 4 * j                      # inner y0, outer y0, inner y1, outer y1
        faces_.append((a0 + 3, a0 + 1, a1 + 1, a1 + 3))      # y1 face
        faces_.append((a0 + 0, a1 + 0, a1 + 2, a0 + 2)[::-1])      # y0 face
        faces_.append((a0 + 2, a0 + 0, a1 + 0, a1 + 2))            # the hole's rim
    return kit.mesh_obj(name, verts, faces_, mat)


def tube_ring(name, R, r, loc, mat, rot=(0, 0, 0), nu=28, nv=8):
    verts, faces_ = [], []
    for i in range(nu):
        a = 2 * math.pi * i / nu
        for j in range(nv):
            b = 2 * math.pi * j / nv
            verts.append(((R + r * math.cos(b)) * math.cos(a), (R + r * math.cos(b)) * math.sin(a), r * math.sin(b)))
    for i in range(nu):
        for j in range(nv):
            i2, j2 = (i + 1) % nu, (j + 1) % nv
            faces_.append((i * nv + j, i2 * nv + j, i2 * nv + j2, i * nv + j2))
    return kit.mesh_obj(name, verts, faces_, mat, loc=loc, rot=rot, smooth=True)


def clear_mat(kit_, name, tint="#dfe8ea", gloss=0.05):
    """A cheap window: transparent with a faint glossy sheen (no refraction, no noise)."""
    if name in kit_.MATS:
        return kit_.MATS[name]
    m = kit_._new(name)
    nt = m.node_tree
    nt.nodes.remove(nt.nodes["Principled BSDF"])
    tr = nt.nodes.new("ShaderNodeBsdfTransparent")
    gl = nt.nodes.new("ShaderNodeBsdfGlossy")
    gl.inputs["Color"].default_value = kit_.col(tint)
    gl.inputs["Roughness"].default_value = 0.08
    mix = nt.nodes.new("ShaderNodeMixShader")
    mix.inputs[0].default_value = gloss
    nt.links.new(tr.outputs[0], mix.inputs[1])
    nt.links.new(gl.outputs[0], mix.inputs[2])
    out = next(n for n in nt.nodes if n.type == "OUTPUT_MATERIAL")
    nt.links.new(mix.outputs[0], out.inputs["Surface"])
    return m


def bunk_glass_mat(kit_):
    """The bunk window: clear glass with condensation on it. ctx's node 'fog' (0 clear .. 1 white) is animated."""
    m = kit_._new("bunk glass")
    nt = m.node_tree
    nt.nodes.remove(nt.nodes["Principled BSDF"])
    tr = nt.nodes.new("ShaderNodeBsdfTransparent")
    gl = nt.nodes.new("ShaderNodeBsdfGlossy")
    gl.inputs["Color"].default_value = kit_.col("#dfe8ea")
    gl.inputs["Roughness"].default_value = 0.08
    m1 = nt.nodes.new("ShaderNodeMixShader")
    m1.inputs[0].default_value = 0.02
    nt.links.new(tr.outputs[0], m1.inputs[1])
    nt.links.new(gl.outputs[0], m1.inputs[2])
    df = nt.nodes.new("ShaderNodeBsdfDiffuse")
    df.inputs["Color"].default_value = kit_.col("#dfe6e8")
    m2 = nt.nodes.new("ShaderNodeMixShader")
    m2.inputs[0].default_value = 0.92
    nt.links.new(m1.outputs[0], m2.inputs[1])
    nt.links.new(df.outputs[0], m2.inputs[2])
    out = next(n for n in nt.nodes if n.type == "OUTPUT_MATERIAL")
    nt.links.new(m2.outputs[0], out.inputs["Surface"])
    return m, m2


# ------------------------------------------------------------------------------------------------ the world
def materials(kit_, ctx):
    M = {}
    M["water"] = kit_.plastic("#3d5750", 0.12, "water", spec=0.9)
    M["gravel"] = kit_.grime("#8a8174", 0.55, 14.0, "gravel", 0.95)
    M["verge"] = kit_.grime("#56683f", 0.55, 9.0, "verge", 0.95)
    M["flat"] = kit_.grime("#7a8352", 0.65, 12.0, "flatgrass", 0.95)
    M["hedge"] = kit_.grime("#3e4f2c", 0.5, 4.0, "hedge", 0.95)
    M["farbank"] = kit_.grime("#4c5c3a", 0.55, 5.0, "farbank", 0.95)
    M["willow"] = kit_.grime("#5d7048", 0.6, 7.0, "willow", 0.95)
    M["bark"] = kit_.plastic("#4b4034", 0.9, "bark")
    M["stone"] = kit_.concrete("#8d8a82", 2.2, 0.5, "quay")
    M["stonedk"] = kit_.concrete("#5d5b56", 2.0, 0.5, "quaydk")
    M["navy"] = kit_.plastic("#1d2d47", 0.4, "hull")
    M["cream"] = kit_.plastic("#e6dbc0", 0.5, "coach")
    M["roof"] = kit_.plastic("#cdc4a8", 0.6, "roof")
    M["honey"] = kit_.planks("#a77a45", "#85602f", 1.4, "X", "honey")
    M["honey2"] = kit_.planks("#a77a45", "#85602f", 1.4, "Y", "honeyY")
    M["floor"] = kit_.planks("#8f6a3b", "#6e4f28", 1.6, "X", "cabfloor")
    M["iron"] = kit_.plastic("#2a2a2a", 0.45, "iron", spec=0.6)
    M["tally"] = kit_.plastic("#4d6638", 0.8, "tally")
    M["bed"] = kit_.plastic("#7c4a3a", 0.95, "mosbed")
    M["mattress"] = kit_.plastic("#6f7f8a", 0.95, "mattress")
    M["quilt"] = kit_.plastic("#a99f86", 0.95, "quilt")
    M["pillow"] = kit_.plastic("#2b3538", 0.95, "pillow")
    M["earth"] = kit_.grime("#6b5a46", 0.7, 10.0, "earth", 0.95)
    M["tuft"] = kit_.plastic("#86a35a", 0.9, "tuft")
    M["leak"] = kit_.emit("#cfd8dc", 1.0, "leak")
    M["glass"] = clear_mat(kit_, "porthole glass")
    M["brass"] = kit_.metal("#8a6a38", 0.4, "brass")
    ctx["M"] = M
    return M


def build_world(kit_, ctx, M):
    # water and the far bank
    kit_.plane("water", (260, 160), (30, -70, 0.0), M["water"])
    span("farbank", -80, 140, -26, -17, -0.6, 0.55, M["farbank"])
    for i, wx in enumerate(range(-40, 120, 7)):
        wy = -18.5 - 1.2 * ((i * 5) % 3)
        kit_.cyl(f"trunk{i}", 0.22, 4.0, (wx + 0.7 * (i % 3), wy, 2.3), M["bark"], n=8)
        for k in range(7):
            a = 2 * math.pi * k / 7 + i
            B(f"wl{i}.{k}", (0.5, 0.5, 4.6 - 0.3 * (k % 3)), (wx + 1.7 * math.cos(a), wy + 1.7 * math.sin(a), 3.0),
              M["willow"], 0.15)
        B(f"wlc{i}", (3.2, 3.2, 1.3), (wx, wy, 4.9), M["willow"], 0.4)
    # the quay: stone face and coping, the verge, the path, the hedge
    span("quay face", -80, 140, -0.9, BANK_Y, -0.6, GROUND, M["stone"])
    span("coping", -80, 140, BANK_Y - 0.03, BANK_Y + 0.38, GROUND, GROUND + 0.07, M["stonedk"], 0.02)
    span("verge", -80, 140, BANK_Y + 0.38, 1.9, GROUND, GROUND + 0.02, M["verge"])
    span("path", -80, 140, 1.9, 4.2, GROUND, GROUND + 0.015, M["gravel"])
    span("meadow", -80, 140, 4.2, 14, GROUND, GROUND + 0.02, M["verge"])
    span("hedge", -80, 140, 7.6, 9.4, GROUND, 2.9, M["hedge"], 0.4)
    for i in range(36):
        hx = -70 + i * 5.4
        B(f"hedgetop{i}", (3.4, 1.6, 0.9), (hx, 8.5, 3.0 + 0.2 * (i % 3)), M["hedge"], 0.3)
    # the flattened strip where it lay (alongside the boat), shown from L72
    ctx["flat"] = [span("flat strip", 4.6, 17.2, -0.05, 0.85, GROUND + 0.022, GROUND + 0.034, M["flat"], 0.01)]
    # Moss's worn patch by the back ring (the past) and the grass that has grown over it (the present)
    import random
    ctx["patch"] = [span("worn patch", PATCH[0] - 0.55, PATCH[0] + 0.55, PATCH[1] - 0.4, PATCH[1] + 0.4,
                         GROUND + 0.021, GROUND + 0.032, M["earth"], 0.04)]
    rnd = random.Random(11)
    ctx["tufts"] = []
    for i in range(110):
        a = rnd.uniform(0, 2 * math.pi)
        rr = math.sqrt(rnd.uniform(0.05, 1.0))
        bx, by = PATCH[0] + 0.6 * rr * math.cos(a), PATCH[1] + 0.45 * rr * math.sin(a)
        h = rnd.uniform(0.07, 0.13) if rr < 0.55 else rnd.uniform(0.16, 0.3)
        t = B(f"tuft{i}", (0.018, 0.018, h), (bx, by, GROUND + h / 2), M["tuft"], 0.008,
              rot=(rnd.uniform(-0.25, 0.25), rnd.uniform(-0.25, 0.25), rnd.uniform(0, 3)))
        ctx["tufts"].append(t)
    # rings: an iron ring lying on the coping with its staple
    for i, rx in enumerate(RINGS):
        tube_ring(f"ring{i}", 0.13, 0.027, (rx, 0.08, GROUND + 0.07 + 0.027), M["iron"])
        B(f"staple{i}", (0.07, 0.06, 0.05), (rx, 0.24, GROUND + 0.095), M["iron"], 0.01)
    # the two strokes on the back ring (x = 5): short uprights across the iron's top, in canal-weed green
    z_top = GROUND + 0.07 + 0.027 * 2 + 0.002
    ctx["tally"] = []
    for k, off in enumerate((-0.025, 0.025)):
        # the ring's near side (toward the camera at -y... the front) at angle -90 degrees: radial strokes
        ctx["tally"].append(B(f"tally{k}", (0.012, 0.062, 0.006), (WIN_X + off, 0.08 - 0.13, z_top), M["tally"], 0.002))


def build_boat(kit_, ctx, M):
    L = BOAT_L
    # hull below the waterline and the skin up to the gunwale
    span("hull bottom", 0, L, SKIN_C, SKIN_P, -0.5, -0.1, M["navy"], 0.05)
    span("hull stern", 0, 0.1, SKIN_C, SKIN_P, -0.5, 1.05, M["navy"], 0.03)
    span("hull bow", L - 0.1, L, SKIN_C, SKIN_P, -0.5, 0.95, M["navy"], 0.03)
    for side, yo, yi, sgn in (("p", SKIN_P - 0.04, SKIN_P, 1), ("c", SKIN_C, SKIN_C + 0.04, -1)):
        pass
    # walls: outer navy skin (0.04) and inner honey (0.06), with round windows
    holes_p = [WIN_X, 8.5]
    holes_c = [WIN_X, 8.5]
    for tag, (yo0, yo1, yi0, yi1), holes in (
            ("p", (SKIN_P - 0.04, SKIN_P, SKIN_P - 0.10, SKIN_P - 0.04), holes_p),
            ("c", (SKIN_C, SKIN_C + 0.04, SKIN_C + 0.04, SKIN_C + 0.10), holes_c)):
        # the lower skin everywhere, then the cabin skin in pieces around the windows
        span(f"skin low {tag}", 0, L, yo0, yo1, -0.5, 0.6, M["navy"])
        span(f"skin deck {tag}", 0, 2.2, yo0, yo1, 0.6, 1.05, M["navy"])
        span(f"skin well {tag}", 10, L, yo0, yo1, 0.6, 0.95, M["navy"])
        span(f"in low {tag}", 2.2, 10, yi0, yi1, FLOOR, 0.6, M["honey2"])
        edges = [2.2] + [v for h in holes for v in (h - 0.32, h + 0.32)] + [10.0]
        pieces = [(edges[i], edges[i + 1]) for i in range(0, len(edges), 2)]
        for pi, (a, b) in enumerate(pieces):
            span(f"skin cab {tag}{pi}", a, b, yo0, yo1, 0.6, ROOF, M["navy"])
            span(f"in cab {tag}{pi}", a, b, yi0, yi1, 0.6, ROOF, M["honey2"])
        for hi, h in enumerate(holes):
            for z0, z1 in ((0.6, WIN_Z - 0.32), (WIN_Z + 0.32, ROOF)):
                span(f"skin pc {tag}{hi}{z0}", h - 0.32, h + 0.32, yo0, yo1, z0, z1, M["navy"])
                span(f"in pc {tag}{hi}{z0}", h - 0.32, h + 0.32, yi0, yi1, z0, z1, M["honey2"])
            holed_panel(f"port o {tag}{hi}", h, WIN_Z, 0.32, 0.2, yo0, yo1, M["navy"])
            holed_panel(f"port i {tag}{hi}", h, WIN_Z, 0.32, 0.2, yi0, yi1, M["honey2"])
            if tag == "p":
                # a short brass housing standing out from the skin, then the glass at its outer end
                yb = SKIN_P + 0.08
                for k, yy in enumerate((SKIN_P + 0.012, SKIN_P + 0.05, yb)):
                    tube_ring(f"housing {tag}{hi}.{k}", 0.222, 0.03, (h, yy, WIN_Z), M["brass"], rot=(math.pi / 2, 0, 0))
                gm = M["glass"]
                if hi == 0:
                    gm, ctx["fog_node"] = bunk_glass_mat(kit_)
                kit_.cyl(f"glass {tag}{hi}", 0.2, 0.006, (h, yb, WIN_Z), gm, rot=(math.pi / 2, 0, 0), n=28)
            else:
                kit_.cyl(f"glass {tag}{hi}", 0.2, 0.006, (h, yo0 - 0.0, WIN_Z), M["glass"], rot=(math.pi / 2, 0, 0), n=28)
    # coach lines (cream) low and on the cabin top
    for y, tag in ((SKIN_P + 0.001, "p"), (SKIN_C - 0.001, "c")):
        span(f"coach lo {tag}", 0.1, L - 0.1, y - 0.006, y + 0.006, 0.6, 0.66, M["cream"])
        span(f"coach hi {tag}", 2.2, 10, y - 0.006, y + 0.006, 1.7, 1.77, M["cream"])
    # decks
    span("deck", 0.1, 2.2, SKIN_C + 0.04, SKIN_P - 0.04, 0.6, DECK, M["honey"])
    span("well", 10, L - 0.1, SKIN_C + 0.04, SKIN_P - 0.04, 0.5, 0.62, M["honey"])
    span("rail stern", 0.0, 0.1, SKIN_C, SKIN_P, 1.05, 1.1, M["cream"])
    span("rail deck p", 0.0, 2.2, SKIN_P - 0.04, SKIN_P, 1.05, 1.1, M["cream"])
    span("rail deck c", 0.0, 2.2, SKIN_C, SKIN_C + 0.04, 1.05, 1.1, M["cream"])
    span("rail well p", 10, L, SKIN_P - 0.04, SKIN_P, 0.95, 1.0, M["cream"])
    span("rail well c", 10, L, SKIN_C, SKIN_C + 0.04, 0.95, 1.0, M["cream"])
    span("rail bow", L - 0.1, L, SKIN_C, SKIN_P, 0.95, 1.0, M["cream"])
    # the cabin's back wall (doorway at y -1.5 to -0.6) and bulkhead, floor, ceiling and roof
    span("back wall l", 2.2, 2.3, SKIN_C + 0.1, -1.5, FLOOR, ROOF, M["honey2"])
    span("back wall r", 2.2, 2.3, -0.6, SKIN_P - 0.1, FLOOR, ROOF, M["honey2"])
    span("lintel", 2.2, 2.3, -1.5, -0.6, 1.92, ROOF, M["honey2"])
    span("bulkhead", 9.9, 10.0, SKIN_C + 0.1, SKIN_P - 0.1, FLOOR, ROOF, M["honey2"])
    span("cabin floor", 2.3, 10, SKIN_C + 0.1, SKIN_P - 0.1, -0.1, FLOOR, M["floor"])
    span("roof a", 3.4, 10, SKIN_C, SKIN_P, ROOF, ROOF + 0.08, M["roof"], 0.02)
    span("roof b", 2.2, 3.4, SKIN_C, -1.5, ROOF, ROOF + 0.08, M["roof"], 0.02)
    span("roof c", 2.2, 3.4, -0.6, SKIN_P, ROOF, ROOF + 0.08, M["roof"], 0.02)
    kit_.cyl("chimney", 0.07, 0.5, (8.0, -1.05, ROOF + 0.33), M["iron"], n=12)
    # light leaking round the shut hatch (hidden when it opens)
    ctx["leak"] = []
    for k, (x0, x1, y0, y1) in enumerate(((2.3, 3.4, -1.52, -1.5), (2.3, 3.4, -0.6, -0.58), (3.39, 3.41, -1.5, -0.6))):
        ctx["leak"].append(span(f"leak{k}", x0, x1, y0, y1, ROOF - 0.004, ROOF - 0.002, M["leak"]))
    # steps (three), Moss's bed, the bunk
    for i, (x0, top) in enumerate(((2.3, 0.54), (2.7, 0.36), (3.1, 0.2))):
        span(f"step{i}", x0, x0 + 0.4, SKIN_C + 0.1, SKIN_P - 0.1, FLOOR, top, M["honey"], 0.015)
    B("moss bed", (0.95, 0.72, 0.14), (4.15, -1.05, FLOOR + 0.07), M["bed"], 0.05)
    B("moss bed rim", (1.05, 0.82, 0.07), (4.15, -1.05, FLOOR + 0.035), M["bed"], 0.03)
    span("bunk base", 4.6, 7.2, -1.0, SKIN_P - 0.1, FLOOR, 0.45, M["honey"], 0.02)
    span("mattress", 4.6, 7.2, -1.0, SKIN_P - 0.1, 0.45, 0.6, M["mattress"], 0.05)
    B("pillow", (0.5, 0.4, 0.12), (4.85, -0.62, 0.66), M["pillow"], 0.05)
    ctx["quilt"] = B("quilt", (1.7, 0.85, 0.12), (6.1, -0.68, 0.66), M["quilt"], 0.05)
    # hatch: a wooden slide on the roof, a bolt on its under edge
    hatch = span("hatch", 2.15, 3.45, -1.56, -0.54, ROOF + 0.08, ROOF + 0.16, M["honey"], 0.02)
    ctx["hatch"] = hatch
    ctx["hatch0"] = tuple(hatch.location)
    # rails for the hatch on the roof
    for k, y in enumerate((-1.6, -0.5)):
        span(f"hrail{k}", 2.1, 5.0, y - 0.02, y + 0.02, ROOF + 0.08, ROOF + 0.12, M["honey"])
    bh = B("bolt housing", (0.12, 0.05, 0.05), (3.2, -0.62, ROOF - 0.04), M["iron"], 0.01)
    ctx["bolt"] = B("bolt bar", (0.16, 0.025, 0.025), (3.2, -0.62, ROOF - 0.075), M["iron"], 0.005)
    ctx["bolt0"] = tuple(ctx["bolt"].location)
    # my sleeve's cuff, crossing the glass with the wipe (no hand: an oatmeal knit cuff)
    ctx["cuff"] = B("cuff", (0.2, 0.34, 0.2), (WIN_X, SKIN_P - 0.2, WIN_Z), M["quilt"], 0.06)


def build_lights(kit_, ctx):
    for name, (kind, loc, aim, power, hexc, size) in LIGHT_BASE.items():
        ob = kit_.light(name, kind, loc, power, hexc, size=size, shadow=(name not in ("eyes",)))
        kit_.aim(ob, aim)
    ctx["lights"] = LIGHT_BASE


# --------------------------------------------------------------------------------------------------- Moss
class Moss:
    COAT, TAN, WHITE, DARK, GREY = "#6e4a2c", "#b98a57", "#d7d3c8", "#1a1512", "#a9a79d"

    def __init__(self, kit_):
        c, t, w = kit_.plastic(self.COAT, 0.9, "moss coat"), kit_.plastic(self.TAN, 0.9, "moss tan"), \
            kit_.plastic(self.WHITE, 0.9, "moss white")
        gr = kit_.plastic(self.GREY, 0.9, "moss grey")
        dk = kit_.plastic(self.DARK, 0.5, "moss dark")
        sad = kit_.plastic("#4f3320", 0.9, "moss back")
        hi = kit_.emit("#ffffff", 4.0, "moss glint")
        self.root = kit_.empty("moss")
        self.root.scale = (1.25, 1.25, 1.25)
        self.body = kit_.empty("moss.body", (0, 0, 0.3), self.root)
        kit_.box("moss.torso", (0.30, 0.62, 0.28), (0, 0.02, 0.0), t, self.body, bevel=0.06)          # tan belly and flanks
        kit_.box("moss.saddle", (0.28, 0.52, 0.14), (0, 0.04, 0.10), sad, self.body, bevel=0.05)        # dark back
        kit_.box("moss.chest", (0.28, 0.16, 0.30), (0, -0.25, -0.005), w, self.body, bevel=0.06)
        kit_.box("moss.rump", (0.29, 0.14, 0.26), (0, 0.30, 0.0), c, self.body, bevel=0.06)
        kit_.box("moss.neck", (0.19, 0.16, 0.24), (0, -0.33, 0.16), c, self.body, bevel=0.05)
        self.legs = {}
        for name, (x, y) in {"fl": (-0.10, -0.24), "fr": (0.10, -0.24), "bl": (-0.10, 0.24), "br": (0.10, 0.24)}.items():
            piv = kit_.empty(f"moss.{name}", (x, y, 0.14), self.body)
            kit_.box(f"moss.{name}m", (0.105, 0.115, 0.24), (0, 0, -0.10), t, piv, bevel=0.035)
            kit_.box(f"moss.{name}p", (0.115, 0.15, 0.07), (0, -0.02, -0.2), w, piv, bevel=0.03)     # white sock
            self.legs[name] = piv
        self.head = kit_.empty("moss.head", (0, -0.40, 0.24), self.body)
        kit_.box("moss.skull", (0.24, 0.22, 0.22), (0, 0.0, 0.03), t, self.head, bevel=0.05)
        kit_.box("moss.brow", (0.20, 0.07, 0.06), (0, -0.09, 0.11), c, self.head, bevel=0.02)
        kit_.box("moss.muzzle", (0.15, 0.20, 0.11), (0, -0.19, -0.04), gr, self.head, bevel=0.04)       # greying muzzle
        kit_.box("moss.chin", (0.12, 0.12, 0.05), (0, -0.17, -0.10), w, self.head, bevel=0.02)
        kit_.box("moss.nose", (0.075, 0.04, 0.055), (0, -0.30, -0.005), dk, self.head, bevel=0.015)
        self.ears = []
        for sx in (-1, 1):
            piv = kit_.empty(f"moss.ear{sx}", (sx * 0.125, 0.02, 0.12), self.head)
            kit_.box(f"moss.earm{sx}", (0.055, 0.13, 0.24), (sx * 0.02, 0.0, -0.11), sad, piv, bevel=0.025)
            self.ears.append((piv, sx))
            kit_.sphere(f"moss.eye{sx}", 0.024, (sx * 0.072, -0.113, 0.07), dk, self.head, seg=10)
            kit_.sphere(f"moss.glint{sx}", 0.0085, (sx * 0.072 - sx * 0.006, -0.133, 0.083), hi, self.head, seg=6)
        self.tail = kit_.empty("moss.tail", (0, 0.40, 0.13), self.body)
        kit_.box("moss.tailm", (0.075, 0.075, 0.26), (0, 0.0, -0.13), c, self.tail, bevel=0.03)
        kit_.box("moss.tailtip", (0.08, 0.08, 0.09), (0, 0.0, -0.29), w, self.tail, bevel=0.03)

    def pose(self, st, t, pos, yaw):
        r = self.root
        r.location = pos
        r.rotation_euler = (0, 0, math.radians(yaw))
        p = st.get("pose", "stand")
        self.body.location = (0, 0, 0.3)
        self.body.rotation_euler = (0, 0, 0)
        hp = [0.0, 0.0]
        for n, leg in self.legs.items():
            leg.rotation_euler = (0, 0, 0)
            leg.location = (leg.location[0], leg.location[1], 0.14)
        hy, hpitch = st.get("head", [0, 0])
        if p == "sit":
            self.body.rotation_euler = (math.radians(-34), 0, 0)    # nose up, rump down
            self.body.location = (0, 0.12, 0.27)
            for n in ("bl", "br"):
                self.legs[n].rotation_euler = (math.radians(-88), 0, 0)
                self.legs[n].location = (self.legs[n].location[0], 0.2, 0.07)
            for n in ("fl", "fr"):
                self.legs[n].rotation_euler = (math.radians(34), 0, 0)
        elif p == "lie":
            self.body.location = (0, 0.0, 0.17)
            for n in self.legs:
                self.legs[n].rotation_euler = (math.radians(-88 if n[0] == "b" else -80), 0, 0)
                self.legs[n].location = (self.legs[n].location[0], self.legs[n].location[1] + (0.0 if n[0] == "b" else -0.05), 0.08)
            hpitch += 18
        elif p == "roll":
            # rolled on her back in the grass, chin up to the sky: the body flipped, the legs bent in the air
            self.body.rotation_euler = (0, math.radians(180), 0)
            self.body.location = (0, 0.0, 0.2)
            for n, leg in self.legs.items():
                leg.rotation_euler = (math.radians(30 if n[0] == "f" else -30), 0, 0)
            self.head.location = (0, -0.38, 0.0)
            self.head.rotation_euler = (math.radians(-62), math.radians(180), 0)
            self.tail.rotation_euler = (math.radians(30), 0, 0)
            e = st.get("ears", 0.5)
            for piv, sx in self.ears:
                piv.rotation_euler = (math.radians(12 - 50 * e), 0, math.radians(sx * 24))
            return
        elif p == "held":
            for n in self.legs:
                self.legs[n].rotation_euler = (math.radians(14), 0, 0)
            self.body.rotation_euler = (math.radians(-6), 0, 0)
        elif p == "climb":
            self.legs["fl"].rotation_euler = (math.radians(-62), 0, 0)
            self.body.rotation_euler = (math.radians(-12), 0, 0)
        if st.get("walk"):
            sw = 24 * math.sin(2 * math.pi * 1.6 * t)
            for n, leg in self.legs.items():
                leg.rotation_euler = (math.radians(sw if n in ("fl", "br") else -sw), 0, 0)
        self.head.location = (0, -0.40, 0.24)
        self.head.rotation_euler = (math.radians(hpitch), 0, math.radians(hy))
        e = st.get("ears", 0.5)
        for piv, sx in self.ears:   # 0 flat and down, 1 pricked and forward
            piv.rotation_euler = (math.radians(12 - 50 * e), 0, math.radians(sx * (8 + 22 * (1 - e))))
        wag = st.get("wag", 0.0)
        base = st.get("tail", 20)
        # the tail is built hanging down from the rump: tail > 0 lets it hang, tail < 0 lifts it (-45 nearly level)
        lift = 0 if base > 0 else min(1.0, -base / 45.0)
        self.tail.rotation_euler = (math.radians(80 * lift), 0, math.radians(32 * wag * math.sin(2 * math.pi * 1.9 * t)))


# ----------------------------------------------------------------------------------------- the Long Man
def stretch_long(kit_, ctx):
    """Called once the cast exists: the rig's body becomes 12 m long, head and shoulders left alone. Everything that makes
    it read as a person lying down (coat, belt, buttons, collar, separate arms with hands, two legs, boots) is built here."""
    kt, kl = LONG_KT, LONG_KL
    ob = lambda n: bpy.data.objects.get(f"longman.{n}")
    shirt = ob("torsom").data.materials[0]
    pants = ob("legm-1").data.materials[0]
    shoe = ob("shoe-1").data.materials[0]
    skin = ob("skinarm-1").data.materials[0]
    sleeve = ob("sleeve-1").data.materials[0]
    tor = bpy.data.objects["longman.torso"]
    for n in ("torsom", "legm-1", "legm1", "shoe-1", "shoe1", "sleeve-1", "sleeve1", "skinarm-1", "skinarm1"):
        o = ob(n)
        if o is not None:
            bpy.data.objects.remove(o, do_unlink=True)
    dark = kit_.plastic("#26331f", 0.8, "ln dark")
    lapel = kit_.plastic("#7d9460", 0.8, "ln lapel")
    belt = kit_.plastic("#2b2118", 0.55, "ln belt")
    brass = kit_.metal("#9a7a42", 0.4, "ln buckle")
    rope = kit_.plastic("#b39a6a", 0.85, "ln rope")
    sole = kit_.plastic("#17120e", 0.7, "ln sole")
    cuff = kit_.plastic("#7b8a52", 0.8, "ln cuff")
    # the coat: shoulders full width, the body a little narrower, the hem flaring over the thighs
    kit_.box("longman.torsom", (1.9, 1.0, 2 * kt), (0, 0, 2 - kt), shirt, tor, bevel=0.1, seg=2)
    kit_.box("longman.yoke", (2.06, 1.08, 1.5), (0, 0, 1.25), shirt, tor, bevel=0.12)
    kit_.box("longman.hem", (2.16, 1.12, 3.0), (0, 0, 2 - 2 * kt - 1.1), shirt, tor, bevel=0.14)
    kit_.box("longman.placket", (0.1, 0.03, 2 * kt - 0.6), (0, -0.515, 2 - kt - 0.25), dark, tor, bevel=0.01)
    for k in range(7):
        kit_.cyl(f"longman.button{k}", 0.1, 0.05, (0.0, -0.53, 0.1 - 1.55 * k), brass, tor, rot=(math.pi / 2, 0, 0), n=10)
    for sx in (-1, 1):
        kit_.box(f"longman.lapel{sx}", (0.5, 0.1, 1.9), (sx * 0.42, -0.53, 0.95), lapel, tor, rot=(0, sx * 0.3, 0), bevel=0.03)
        kit_.box(f"longman.pocket{sx}", (0.7, 0.07, 0.4), (sx * 0.58, -0.52, -7.2), dark, tor, bevel=0.03)
        kit_.box(f"longman.pocketb{sx}", (0.7, 0.07, 0.4), (sx * 0.58, -0.52, -8.2), dark, tor, bevel=0.03)
    kit_.box("longman.belt", (2.1, 1.1, 0.55), (0, 0, 2 - 2 * kt + 1.9), belt, tor, bevel=0.05)
    kit_.box("longman.buckle", (0.4, 0.06, 0.4), (0, -0.57, 2 - 2 * kt + 1.9), brass, tor, bevel=0.02)
    hips_z = 4.0 - 2 * kt
    for sx in (-1, 1):
        leg = bpy.data.objects[f"longman.leg{sx}"]
        leg.location = (sx * 0.58, 0, hips_z)
        kit_.box(f"longman.legm{sx}", (0.8, 1.0, 1.72 * kl), (0, 0, -0.86 * kl), pants, leg, bevel=0.1)
        for k, ox in enumerate((-0.2, 0.2)):
            kit_.box(f"longman.rope{sx}{k}", (0.07, 0.03, 1.6 * kl), (ox, -0.512, -0.86 * kl - 0.1), rope, leg, bevel=0.01)
        kit_.box(f"longman.shoe{sx}", (0.84, 1.7, 1.5), (0, -0.4, -1.72 * kl - 0.2), shoe, leg, bevel=0.14)
        kit_.box(f"longman.toe{sx}", (0.84, 0.5, 0.7), (0, -1.0, -1.72 * kl - 0.45), shoe, leg, bevel=0.14)
        kit_.box(f"longman.sole{sx}", (0.86, 1.72, 0.18), (0, -0.4, -1.72 * kl - 1.0), sole, leg, bevel=0.03)
        arm = bpy.data.objects[f"longman.arm{sx}"]
        arm.location = (sx * 1.74, 0, 1.75)
        La = 2 * kt - 0.9
        kit_.box(f"longman.sleeve{sx}", (0.78, 1.0, La - 1.3), (0, 0, 0.25 - (La - 1.3) / 2), sleeve, arm, bevel=0.1)
        kit_.box(f"longman.cuff{sx}", (0.84, 1.06, 0.4), (0, 0, 0.25 - (La - 1.3) - 0.2), cuff, arm, bevel=0.06)
        kit_.box(f"longman.hand{sx}", (0.8, 0.9, 1.3), (0, 0, 0.25 - (La - 1.3) - 0.4 - 0.65), skin, arm, bevel=0.12)
        kit_.box(f"longman.thumb{sx}", (0.22, 0.4, 0.6), (-sx * 0.38, -0.32, 0.25 - (La - 1.3) - 0.9), skin, arm, bevel=0.06)
    # beads of water that never run: small clear spheres on the face and the coat
    bead = kit_.plastic("#7f9591", 0.03, "bead", spec=1.0)
    head = bpy.data.objects["longman.headg"]
    ctx["beads"] = []
    import random
    rnd = random.Random(5)
    for i in range(14):
        a = math.radians(rnd.uniform(-38, 38))
        zz = rnd.uniform(-0.45, 0.4)
        R = faces.HEAD_R
        ctx["beads"].append(kit_.sphere(f"longman.bead{i}", rnd.uniform(0.012, 0.024),
                                        (R * math.sin(a), -R * math.cos(a) * 1.0 - 0.005, zz), bead, head, seg=8))
    for i in range(24):
        ctx["beads"].append(kit_.sphere(f"longman.cbead{i}", rnd.uniform(0.02, 0.04),
                                        (rnd.uniform(-0.85, 0.85), -0.53, 2.0 - rnd.uniform(0.3, 2 * kt - 0.5)), bead, tor, seg=8))
    # hair lying flat and wet on the skull: a thin cap and a short swept fringe, never upright
    hair = kit_.plastic("#2f4026", 0.5, "ln wet hair")
    kit_.box("longman.fringe", (1.0, 0.5, 0.1), (0.12, -0.5, 0.66), hair, head, rot=(0.0, 0.1, 0.0), bevel=0.04)
    kit_.box("longman.fringe2", (0.7, 0.45, 0.1), (-0.3, -0.5, 0.62), hair, head, rot=(0.0, -0.2, 0.0), bevel=0.04)
    glint = kit_.emit("#f4faf6", 14.0, "eye glint")
    for sx in (-1, 1):
        kit_.sphere(f"longman.glint{sx}", 0.034, (sx * 0.228, -0.598, 0.09), glint, head, seg=8)
        kit_.sphere(f"longman.glintb{sx}", 0.012, (sx * 0.228 + 0.02, -0.62, 0.115), glint, head, seg=6)
    ctx["long_ready"] = True


def place_long(tl, t, ctx):
    root = bpy.data.objects.get("longman")
    if root is None:
        return
    if not ctx.get("long_ready"):
        stretch_long(kit, ctx)
    cs = _cues(tl, "long")
    c = _last(cs, t)
    hide = bool(c and c.get("hidden", False)) or c is None
    sc = rig.S * LONG_H
    hx = _eased(cs, "x", t, 22.5) if c else 22.5
    turn = _eased(cs, "turn", t, 0.0) if c else 0.0
    y = _eased(cs, "y", t, 0.30) if c else 0.30
    M = Matrix(((0, 0, -1), (1, 0, 0), (0, -1, 0)))
    root.rotation_euler = M.to_euler()
    head_local = V((0, 0, 4.62)) * sc
    z = GROUND + (0.28 if y < 0.25 else 0.24)       # the head lies on its back on the coping or the verge
    target = V((hx, y, z))
    root.location = target - M @ head_local
    neck = bpy.data.objects["longman.neck"]
    neck.rotation_euler = (0, 0, math.radians(-92 * turn))
    for o in [root] + list(root.children_recursive):
        o.hide_render = hide


# ------------------------------------------------------------------------------------------------ build
def collect_fog(kit_):
    """Every material's fog emission node and its density node, so animate can ease the fog."""
    ems, dens = [], []
    for m in kit_.MATS.values():
        nt = m.node_tree
        if nt is None or m.name in ("bunk glass", "porthole glass"):
            continue
        for n in nt.nodes:
            if n.type == "EMISSION":
                for lk in n.outputs[0].links:
                    if lk.to_node.type == "MIX_SHADER" and lk.to_socket == lk.to_node.inputs[2]:
                        ems.append(n)
            if n.type == "MATH" and n.operation == "MULTIPLY" and abs(n.inputs[1].default_value + kit_.FOG["density"]) < 1e-9:
                dens.append(n)
    return ems, dens


def build(kit_, story, tl):
    ctx = {"story": story}
    M = materials(kit_, ctx)
    build_world(kit_, ctx, M)
    build_boat(kit_, ctx, M)
    build_lights(kit_, ctx)
    ctx["moss"] = Moss(kit_)
    ctx["fog_em"], ctx["fog_dn"] = collect_fog(kit_)
    ctx["wnode"] = M["water"].node_tree.nodes["Principled BSDF"]
    ctx["wd"] = workdir(tl)
    return ctx


# ---------------------------------------------------------------------------------------------- animate
def _state_at(tl, t):
    cs = _cues(tl, "time")
    cur = _last(cs, t)
    if cur is None:
        return STATES["grey1"]
    i = cs.index(cur)
    b = STATES[cur["set"]]
    if i == 0 or not cur.get("dur"):
        return b
    a = STATES[cs[i - 1]["set"]]
    u = _ss((t - cur["t"]) / cur["dur"])
    out = {}
    for k, v in b.items():
        if k == "fog":
            ca, cb = kit.col(a[k])[:3], kit.col(v)[:3]
            out[k] = tuple(x + (y - x) * u for x, y in zip(ca, cb))
        else:
            out[k] = a[k] + (v - a[k]) * u
    return out


def animate_people(tl, t):
    for who, keys in tl.get("acting", {}).items():
        root = bpy.data.objects.get(who)
        if root is None or who == "longman":
            continue
        lie = None
        for k in keys:
            if "lie" in k and k["t"] <= t + 1e-9:
                lie = k["lie"]
        if lie:
            root.rotation_euler = tuple(math.radians(a) for a in lie)


def animate_moss(tl, t, ctx):
    m = ctx["moss"]
    cs = _cues(tl, "moss")
    c = _last(cs, t)
    if c is None:
        m.root.hide_render = True
        for o in m.root.children_recursive:
            o.hide_render = True
        return
    state = {}
    for cc in cs:
        if cc["t"] <= t + 1e-9:
            state.update({k: v for k, v in cc.items() if k not in ("name", "at", "t", "dur")})
    hidden = state.get("hidden", False)
    for o in [m.root] + list(m.root.children_recursive):
        o.hide_render = hidden
    i = cs.index(c)
    pos, yaw = list(state.get("pos", [0, 0, 0])), state.get("yaw", 0)
    if c.get("dur") and i > 0:
        prev = {}
        for cc in cs[:i]:
            prev.update({k: v for k, v in cc.items() if k not in ("name", "at", "t", "dur")})
        u = _ss((t - c["t"]) / c["dur"])
        pp, py = prev.get("pos", pos), prev.get("yaw", yaw)
        pos = [a + (b - a) * u for a, b in zip(pp, pos)]
        yaw = py + (yaw - py) * u
    if state.get("hold"):
        me = bpy.data.objects.get(state["hold"])
        if me is not None:
            my = me.rotation_euler.z
            f = V((math.sin(my), -math.cos(my), 0))
            loc = me.location + f * 0.30
            pos = [loc.x, loc.y, loc.z + 0.62]
            yaw = math.degrees(my) + 90
    m.pose(state, t, tuple(pos), yaw)


def animate(kit_, story, tl, t, ctx):
    animate_people(tl, t)
    animate_moss(tl, t, ctx)
    place_long(tl, t, ctx)
    # the hatch, its leaks, the bolt, the wipe, the flattened verge, the tally
    h = _eased(_cues(tl, "hatch"), "open", t, 0.0)
    hx, hy, hz = ctx["hatch0"]
    ctx["hatch"].location = (hx + 1.55 * h, hy, hz)
    for o in ctx["leak"]:
        o.hide_render = h > 0.02
    bc = _last(_cues(tl, "bolt"), t)
    bon = 1.0 if (bc and bc.get("on")) else 0.0
    b0 = ctx["bolt0"]
    ctx["bolt"].location = (b0[0], b0[1] + 0.07 * bon, b0[2])
    ctx["bolt"].hide_render = False
    w = _eased(_cues(tl, "wipe"), "to", t, 0.0)
    ctx["fog_node"].inputs[0].default_value = 0.93 * (1.0 - w)
    cuff = ctx["cuff"]
    cuff.location = (WIN_X - 0.42 + 0.84 * w, SKIN_P - 0.25, WIN_Z - 0.05)
    cuff.hide_render = not (0.02 < w < 0.98 and _last(_cues(tl, "wipe"), t) is not None and t < 1e9
                            and any(c["t"] <= t < c["t"] + c.get("dur", 0) + 0.05 and c.get("to") == 1.0 for c in _cues(tl, "wipe")))
    fc = _last(_cues(tl, "flat"), t)
    for o in ctx["flat"]:
        o.hide_render = not (fc and fc.get("on"))
    pc = _last(_cues(tl, "patch"), t)
    pon = bool(pc and pc.get("on"))
    lc0 = _last(_cues(tl, "long"), t)
    lx0 = _eased(_cues(tl, "long"), "x", t, 22.5) if lc0 else 22.5
    long_here = bool(lc0 and not lc0.get("hidden", False) and abs(lx0 - 5.0) < 0.3)
    for o in ctx["patch"]:
        o.hide_render = not pon
    mroot = ctx["moss"].root
    moss_here = (not mroot.hide_render) and abs(mroot.location.x - PATCH[0]) < 0.8 and abs(mroot.location.y - PATCH[1]) < 0.8
    for o in ctx["tufts"]:
        inside = abs(o.location.y - PATCH[1]) < 0.34 and abs(o.location.x - PATCH[0]) < 0.6
        o.hide_render = pon or ((long_here or moss_here) and inside)
    tc = _last(_cues(tl, "tally"), t)
    for o in ctx["tally"]:
        o.hide_render = not (tc and tc.get("on"))
    # light, fog, exposure
    s = _state_at(tl, t)
    fogc = s["fog"] if isinstance(s["fog"], tuple) else kit.col(s["fog"])[:3]
    for n in ctx["fog_em"]:
        n.inputs["Color"].default_value = (*fogc, 1)
    for n in ctx["fog_dn"]:
        n.inputs[1].default_value = -s["dens"]
    wn = ctx["wnode"]
    wn.inputs["Roughness"].default_value = s["wr"]
    for k in ("Specular IOR Level", "Specular"):
        if k in wn.inputs:
            wn.inputs[k].default_value = s["wsp"]
            break
    bg = bpy.context.scene.world.node_tree.nodes["Background"]
    bg.inputs["Color"].default_value = (*fogc, 1)
    bg.inputs["Strength"].default_value = s["ws"]
    bpy.context.scene.view_settings.exposure = s["exp"]
    cs = _cues(tl, "long")
    lc = _last(cs, t)
    hx = _eased(cs, "x", t, 22.5) if lc else 22.5
    turn = _eased(cs, "turn", t, 0.0) if lc else 0.0
    ly = _eased(cs, "y", t, 0.3) if lc else 0.3
    fo = (-2.6 + 1.5 * turn, 1.2 - 1.1 * turn, 1.1 - 0.7 * turn)
    for name, off, aim in (("faceside", fo, (0, 0.0, -0.1)), ("rim", (3.2, 3.4, 1.4), (0, 0, 0)),
                           ("eyes", (0.0, 0.9, 0.7), (0, 0, 0)), ("key", (-1.2, -8.0, 2.6), (0, 0.2, -0.1))):
        ob = kit.LIGHTS[name]["obj"]
        ob.location = (hx + off[0], ly + off[1], GROUND + 0.30 + off[2])
        kit.aim(ob, (hx + aim[0], ly + aim[1], GROUND + 0.30 + aim[2]))
    over = {
        "faceside": s["eye"] * ((1.0 - turn) + 0.06 * turn), "winglow": 0.0,
        "sky": 1.0, "warm": s["warm"], "key": s["key"], "rim": s["rim"], "eyes": s["eye"],
        "cab a": s["fill"], "cab b": s["fill"], "cab c": s["fill"], "cab d": s["fill"], "cab e": s["fill"], "porch": s["fill"],
        "hatch": 0.0,
    }
    # the open hatch lets the day in, eased with the slide
    # a soft daylight fill for shots whose subject sits away from every other light (shot key "lamp": its power)
    lamp = 0.0
    for sh, ts in zip(story["shots"], tl["shots"]):
        if ts["start"] - 1e-6 <= t < ts["end"] and sh.get("lamp"):
            cam = sh["cam"][0]
            tgt, loc = V(cam[2]), V(cam[1])
            d = (loc - tgt)
            d.normalize()
            kit.LIGHTS["lamp"]["obj"].location = tgt + d * 1.2 + V((0, 0, 0.6))
            kit.aim(kit.LIGHTS["lamp"]["obj"], tuple(tgt))
            lamp = float(sh["lamp"])
    over["lamp"] = lamp
    over["cab a"] *= 1.0 + 0.35 * h
    over["hatch"] = h
    return over
