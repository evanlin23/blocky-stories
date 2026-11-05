"""ep119 "quiet car": a bright commuter train on a sunny elevated line. The quiet car is cream and sea-green, ten rows of
high-backed seat pairs, big windows, steel luggage racks; beside it a loud, busy car; a sunlit platform; a party
corner, a bus window and a bathroom for the short flashbacks.

The forty riders are never built: only what they do to things (warm seats, a coffee, a lunch, candles, a hat, breath
fogging the windows, handprints, a smiley, dipped cushions, shadows on the platform).

Everything the story moves is driven by cues in story.json (see animate). The rule meter is a cream tag on the camera
(top left): a hush glyph and my silent-morning count in big seven-segment digits.
"""
import math
import random
import sys
from pathlib import Path

import bpy
from mathutils import Vector

sys.path.insert(0, str(Path(__file__).resolve().parent))
import layout as G  # noqa: E402

D2R = math.pi / 180.0
W = {}
HALF = G.HALF


def ss(x):
    x = min(1.0, max(0.0, x))
    return x * x * (3 - 2 * x)


def kit_col(h):
    h = h.lstrip("#")
    f = lambda c: (c / 12.92) if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
    return tuple(f(int(h[i:i + 2], 16) / 255) for i in (0, 2, 4))


def _L(**kw):
    base = dict(sun=3.4, sun_col="#fff0d8", el=42.0, az=70.0, fill=0.9, fill_col="#fff0e0", sky="#8fd3ff", sky_str=1.0)
    base.update(kw)
    return base


LOOKS = {
    "day": _L(),
    "tunnel": _L(sun=0.0, fill=0.05, sky="#101830", sky_str=0.25),
    "night": _L(sun=0.0, fill=0.12, sky="#1c2658", sky_str=0.35),
}


def look_at(tl, t):
    cues = [c for c in tl["cues"] if c["name"] == "look"]
    cur = LOOKS[cues[0]["id"]] if cues else LOOKS["day"]
    for c in cues:
        if c["t"] > t:
            break
        cur = LOOKS[c["id"]]
    return {k: (kit_col(v) if isinstance(v, str) else v) for k, v in cur.items()}


def sample(name, tl, t, defaults):
    """The state of cue track `name` at t: numeric fields eased over a cue's own "dur"."""
    cues = [c for c in tl["cues"] if c["name"] == name]
    cur, prev = dict(defaults), dict(defaults)
    for c in cues:
        if c["t"] > t:
            break
        prev = dict(cur)
        cur.update({k: v for k, v in c.items() if k in defaults})
        dur = c.get("dur", 0.0)
        if dur > 0 and t < c["t"] + dur:
            u = ss((t - c["t"]) / dur)
            return {k: (prev[k] + (cur[k] - prev[k]) * u if isinstance(cur[k], (int, float)) else cur[k]) for k in cur}
    return cur


def noshadow(ob):
    ob.visible_shadow = False
    for c in ob.children_recursive:
        c.visible_shadow = False


def _hide(ob, hide):
    ob.hide_render = hide
    for c in ob.children_recursive:
        c.hide_render = hide


def amat(kit, name, hexc, alpha, rough=0.6, emit=0.0):
    """A see-through plastic whose alpha the story animates."""
    m = kit._new(name)
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = kit.col(hexc)
    b.inputs["Roughness"].default_value = rough
    b.inputs["Alpha"].default_value = alpha
    kit._fogged(m, b.outputs[0])
    if emit:
        b.inputs["Emission Color"].default_value = kit.col(hexc)
        b.inputs["Emission Strength"].default_value = emit
    return m, b


# ------------------------------------------------------------------------------------------- seven-segment numerals
SEG = {"a": (0, 1, 1, 0), "b": (1, 0.5, 0, 1), "c": (1, -0.5, 0, 1), "d": (0, -1, 1, 0), "e": (-1, -0.5, 0, 1),
       "f": (-1, 0.5, 0, 1), "g": (0, 0, 1, 0)}
DIG = {"0": "abcdef", "1": "bc", "2": "abged", "3": "abgcd", "4": "fgbc", "5": "afgcd", "6": "afgedc", "7": "abc",
       "8": "abcdefg", "9": "abcdfg"}


def digit_boxes(kit, name, ch, w, h, t, mat, parent, loc, plane="xy", z=0.0):
    """One digit as segment boxes; returns {segment: box}. plane "xy": flat on the camera tag (layer z);
    plane "xz": standing on a wall facing -y (layer y)."""
    out = {}
    for s, (sx, sy, hz, vt) in SEG.items():
        # horizontal segments: width w - t, thickness t; vertical: height h/2, thickness t
        if hz:
            size2 = (w - t, t)
        else:
            size2 = (t, h / 2 - t * 0.2)
        px, py = sx * (w / 2 - t / 2), sy * (h / 2 - t / 2)
        if plane == "xy":
            size, pos = (size2[0], size2[1], 0.004), (loc[0] + px, loc[1] + py, z)
        else:
            size, pos = (size2[0], 0.012, size2[1]), (loc[0] + px, loc[1], loc[2] + py)
        out[s] = kit.box(f"{name}.{s}", size, pos, mat, parent)
    for s, ob in out.items():
        ob.hide_render = s not in DIG[ch]
    return out


# ------------------------------------------------------------------------------------------------ the cars
def seat_pair(kit, name, y, side, M, plaque=None):
    """A pair of seats (aisle seat and window seat) facing +y, side -1 or +1."""
    for kind, cx, wd in (("a", 0.75, 0.7), ("w", 1.625, 0.95)):
        x = side * cx
        kit.box(f"{name}.{kind}.base", (wd, 0.8, 0.3), (x, y, 0.15), M["seatdark"], bevel=0.02)
        c = kit.box(f"{name}.{kind}.cush", (wd - 0.04, 0.78, 0.16), (x, y, 0.42), M["seat"], bevel=0.04)
        kit.box(f"{name}.{kind}.back", (wd, 0.12, 1.2), (x, y - 0.45, 0.6), M["seat"], bevel=0.04)
        kit.box(f"{name}.{kind}.head", (wd * 0.55, 0.1, 0.26), (x, y - 0.44, 1.28), M["cream"], bevel=0.04)
        W.setdefault("cush", []).append((c, name, kind, side, y))
    if plaque:
        # a numeral on the rear top of the aisle seat's back, readable from behind
        x = side * 0.75
        kit.box(f"{name}.plq", (0.5, 0.02, 0.34), (x, y - 0.525, 1.0), M["cream"])
        digs = str(plaque)
        for i, ch in enumerate(digs):
            dx = (i - (len(digs) - 1) / 2) * 0.2
            digit_boxes(kit, f"{name}.n{i}", ch, 0.14, 0.26, 0.04, M["navy"], None, (x + dx, y - 0.54, 1.0), plane="xz")


def build_car(kit, y0, M, quiet, tag):
    """A car with interior y0 .. y0+28, windows each row. quiet: fog panes, racks, plaques, door."""
    L = G.CAR_L
    cx = 0.0
    kit.box(f"{tag}.floor", (2 * HALF + 0.3, L + 0.3, 0.06), (0, y0 + L / 2, -0.01), M["floor"])
    kit.box(f"{tag}.runner", (0.62, L, 0.012), (0, y0 + L / 2, 0.025), M["runner"])
    kit.box(f"{tag}.ceil", (2 * HALF + 0.3, L + 0.3, 0.06), (0, y0 + L / 2, G.CEIL + 0.03), M["cream"])
    kit.box(f"{tag}.under", (2 * HALF - 0.4, L, 0.5), (0, y0 + L / 2, -0.32), M["dark"])
    for k in range(6):
        kit.box(f"{tag}.panel{k}", (0.7, 3.4, 0.02), (0, y0 + 2.4 + k * 4.6, G.CEIL - 0.012), M["panel"])
    win_h = (0.95, 2.15)
    rows = [y0 + G.row_y(i) for i in range(G.ROWS)]

    def wall(side, ya, yb, za, zb, nm):
        if yb - ya < 0.02 or zb - za < 0.02:
            return
        yc, zc = (ya + yb) / 2, (za + zb) / 2
        kit.box(f"{tag}.{nm}.liner", (0.05, yb - ya, zb - za), (side * (HALF + 0.025), yc, zc), M["cream"])
        kit.box(f"{tag}.{nm}.skin", (0.06, yb - ya, zb - za), (side * (HALF + 0.1), yc, zc), M["silver"])

    for side in (-1, 1):
        door = quiet and side == 1
        # below and above the windows (door gap in the right wall of the quiet car)
        if door:
            wall(side, y0, y0 + G.DOOR[0], 0, G.CEIL, "wd0")
            wall(side, y0 + G.DOOR[1], y0 + L, 0, win_h[0], "wlo")
            wall(side, y0 + G.DOOR[1], y0 + L, win_h[1], G.CEIL, "whi")
            wall(side, y0 + G.DOOR[0], y0 + G.DOOR[1], 2.3, G.CEIL, "wdt")
        else:
            wall(side, y0, y0 + L, 0, win_h[0], f"lo{side}")
            wall(side, y0, y0 + L, win_h[1], G.CEIL, f"hi{side}")
        # pillars between windows
        edges = [y0] + [v for y in rows for v in (y - 0.72, y + 0.72)] + [y0 + L]
        for k in range(0, len(edges), 2):
            ya, yb = edges[k], edges[k + 1]
            if door and yb <= y0 + G.DOOR[1] + 0.001:
                continue
            if door:
                ya = max(ya, y0 + G.DOOR[1])
            wall(side, ya, yb, win_h[0], win_h[1], f"pil{side}_{k}")
        # the green stripe on the outside skin
        if not door:
            kit.box(f"{tag}.stripe{side}", (0.02, L, 0.2), (side * (HALF + 0.14), y0 + L / 2, 0.55), M["stripe"])
            kit.box(f"{tag}.stripe2{side}", (0.02, L, 0.08), (side * (HALF + 0.14), y0 + L / 2, 2.4), M["stripe"])
        else:
            kit.box(f"{tag}.stripe{side}a", (0.02, G.DOOR[0], 0.2), (side * (HALF + 0.14), y0 + G.DOOR[0] / 2, 0.55), M["stripe"])
            kit.box(f"{tag}.stripe{side}b", (0.02, L - G.DOOR[1], 0.2), (side * (HALF + 0.14), y0 + (L + G.DOOR[1]) / 2, 0.55), M["stripe"])
        # seats
        for i, y in enumerate(rows):
            plaque = None
            if quiet and side == 1 and i == 7:
                plaque = 9
            if quiet and side == -1 and i == 6:
                plaque = 12
            seat_pair(kit, f"{tag}.s{side}_{i}", y, side, M, plaque)
    # the end walls with a door window (x in -0.55..0.55, z 0.95..2.05)
    for yy, nm in ((y0 + L, "far"), (y0, "near")):
        closed_end = (not quiet and yy == y0)
        if closed_end or (quiet and nm == "far"):
            kit.box(f"{tag}.{nm}.wall", (2 * HALF + 0.3, 0.15, G.CEIL), (0, yy + (0.075 if nm == "far" else -0.075), G.CEIL / 2), M["cream"])
            continue
        yo = yy + (0.075 if nm == "far" else -0.075)
        kit.box(f"{tag}.{nm}.wl", (HALF - 0.55 + 0.15, 0.15, G.CEIL), (-(HALF + 0.55) / 2 - 0.075, yo, G.CEIL / 2), M["cream"])
        kit.box(f"{tag}.{nm}.wr", (HALF - 0.55 + 0.15, 0.15, G.CEIL), ((HALF + 0.55) / 2 + 0.075, yo, G.CEIL / 2), M["cream"])
        kit.box(f"{tag}.{nm}.wt", (1.1, 0.15, G.CEIL - 2.05), (0, yo, 2.05 + (G.CEIL - 2.05) / 2), M["cream"])
        kit.box(f"{tag}.{nm}.wb", (1.1, 0.15, 0.95), (0, yo, 0.475), M["door"])
        kit.box(f"{tag}.{nm}.fr1", (0.08, 0.18, 1.1), (-0.58, yo, 1.5), M["stripe"])
        kit.box(f"{tag}.{nm}.fr2", (0.08, 0.18, 1.1), (0.58, yo, 1.5), M["stripe"])
    # ceiling lights, steady
    for k in range(7):
        kit.light(f"{tag}.lamp{k}", "POINT", (0, y0 + 2.0 + k * 4.0, G.CEIL - 0.35), 130.0, "#fff4e0", size=0.7, shadow=False)
    # steel luggage racks
    for side in (-1, 1):
        kit.box(f"{tag}.rack{side}", (0.5, L - 1.0, 0.04), (side * 1.85, y0 + L / 2, 2.0), M["steel"])
        for k in range(10):
            yy = y0 + 1.0 + k * 2.8
            kit.box(f"{tag}.rb{side}_{k}", (0.04, 0.04, 0.5), (side * 1.6, yy, 2.25), M["steel"])
            kit.box(f"{tag}.rb2{side}_{k}", (0.5, 0.04, 0.04), (side * 1.85, yy, 2.03), M["steel"])
        kit.box(f"{tag}.rrail{side}", (0.04, L - 1.0, 0.04), (side * 1.62, y0 + L / 2, 2.04), M["steel"])


def tree_at(kit, nm, x, y, M, parent):
    kit.cyl(f"{nm}.tr", 0.18, 1.6, (x, y, -0.2), M["trunk"], parent, n=8)
    cr = kit.sphere(f"{nm}.cr", 1.25, (x, y, 1.0), M["crown"], parent, seg=10)
    W["crowns"].append(cr)


def build_env(kit, M):
    env = kit.empty("env", (0, 0, 0))
    W["env"] = env
    W["crowns"] = []
    rng = random.Random(119)
    pastel = ["#ffd9b8", "#ffc4c4", "#c8e6ff", "#fff0b0", "#d8f0c8", "#f4cfe8", "#cfe0ff", "#ffe2a8"]
    pat = []
    for k in range(4):
        pat.append({s: dict(r=rng.randint(0, 2), h=rng.uniform(-1.5, 4.5), c=rng.choice(pastel), w=rng.uniform(5, 9),
                            d=rng.uniform(7, 11)) for s in (-1, 1)})
    for p in range(-2, 4):
        for k in range(4):
            y = (p * 4 + k) * 12.0 + 3.0
            for s in (-1, 1):
                b = pat[k][s]
                x = s * (10.0 + b["r"] * 7.0)
                top = b["h"]
                kit.box(f"env.b{p}_{k}_{s}", (b["d"], b["w"] + 4, top + 12), (x, y, (top - 12) / 2),
                        kit.plastic(b["c"], 0.8, spec=0.1), env)
                kit.box(f"env.r{p}_{k}_{s}", (b["d"] + 0.3, b["w"] + 4.3, 0.3), (x, y, top + 0.15),
                        kit.plastic("#e07a5f" if (k + s) % 2 else "#7a9cc6", 0.7, spec=0.1), env)
                if k in (0, 2):
                    tree_at(kit, f"env.t{p}_{k}_{s}", s * (5.2 + 0.9 * (k == 2)), y + 6.0, M, env)
    # the elevated line: dark girders and rails under the train
    kit.box("rail.girder", (4.2, 400, 0.6), (0, 14, -1.1), M["dark"])
    for s in (-1, 1):
        kit.box(f"rail.r{s}", (0.1, 400, 0.12), (s * 0.75, 14, -0.72), M["steel"])


def build_tunnel(kit, M):
    tun = kit.empty("tunnel", (0, 0, 0))
    W["tunnel"] = tun
    tm = kit.plastic("#1c2848", 0.9, spec=0.05)
    kit.box("tun.l", (0.3, 260, 7.0), (-3.3, 14, 1.2), tm, tun)
    kit.box("tun.r", (0.3, 260, 7.0), (3.3, 14, 1.2), tm, tun)
    kit.box("tun.top", (7.0, 260, 0.3), (0, 14, 4.8), tm, tun)
    kit.box("tun.floor", (7.0, 260, 0.3), (0, 14, -1.6), tm, tun)
    lam = kit.empty("tunlamps", (0, 0, 0), tun)
    W["lamps"] = lam
    lm = kit.emit("#ffe9c0", 2.2)
    for k in range(-2, 40):
        for s in (-1, 1):
            kit.box(f"tun.lamp{k}_{s}", (0.1, 0.5, 0.3), (s * 3.12, -8 + k * 8.0, 2.1), lm, lam)
    _hide(tun, True)


def build_platform(kit, M):
    x0, x1, y0, y1 = G.PLAT
    plat = kit.empty("platform", (0, 0, 0))
    W["plat"] = plat
    conc = kit.texture("concrete", 1.0, tint="#efe6d4")
    kit.box("plat.slab", (x1 - x0, y1 - y0, 0.6), ((x0 + x1) / 2, (y0 + y1) / 2, -0.3), conc, plat)
    kit.box("plat.edge", (0.3, y1 - y0, 0.02), (x0 + 0.5, (y0 + y1) / 2, 0.012), kit.plastic("#ffd23f", 0.7), plat)
    green = kit.plastic("#2fa58f", 0.6, spec=0.1)
    kit.box("plat.canopy", (6.0, y1 - y0 + 1, 0.2), (6.4, (y0 + y1) / 2, 3.6), green, plat)
    for yy in (y0 + 0.5, y1 - 0.5):
        kit.box(f"plat.pole{yy}", (0.2, 0.2, 3.6), (8.9, yy, 1.8), M["steel"], plat)
    # a steel bench
    bx, by = 7.2, 6.0
    kit.box("plat.bench.seat", (1.0, 2.2, 0.08), (bx, by, 0.5), M["steel"], plat)
    kit.box("plat.bench.back", (0.08, 2.2, 0.6), (bx + 0.45, by, 0.85), M["steel"], plat)
    for dy in (-0.9, 0.9):
        kit.box(f"plat.bench.l{dy}", (0.9, 0.08, 0.5), (bx, by + dy, 0.25), M["steel"], plat)
    # shadows of people stepping off (flat, translucent), moved by the 'shadows' cue
    sm, sb = amat(kit, "shadowmat", "#2a2f44", 0.4, 0.9)
    W["shadows"] = []
    for i in range(7):
        sh = kit.empty(f"shadow{i}", (3.0, 0.0, 0.03))
        for nm, size, loc in (("hd", (0.24, 0.24, 0.01), (0, 0.0, 0)), ("bd", (0.3, 0.9, 0.01), (0, 0.55, 0)),
                              ("lg", (0.24, 0.85, 0.01), (0, 1.4, 0))):
            kit.box(f"shadow{i}.{nm}", size, loc, sm, sh)
        noshadow(sh)
        W["shadows"].append(sh)


def build_party(kit, M):
    px, py = G.PARTY
    wall = kit.plastic("#ffd9a8", 0.85, spec=0.05)
    kit.box("party.floor", (12, 10, 0.1), (px, py, -0.05), kit.plastic("#d9a56b", 0.7))
    kit.box("party.wall", (12, 0.3, 3.4), (px, py + 4.5, 1.7), wall)
    for s in (-1, 1):
        kit.box(f"party.side{s}", (0.3, 10, 3.4), (px + s * 6, py, 1.7), wall)
    kit.box("party.ceil", (12, 10, 0.2), (px, py, 3.5), wall)
    kit.box("party.table", (3.0, 1.0, 0.1), (px - 2.3, py + 3.4, 0.95), kit.plastic("#fffaf0", 0.6))
    kit.box("party.table.b", (2.8, 0.8, 0.9), (px - 2.3, py + 3.4, 0.45), kit.plastic("#ff7a2e", 0.6))
    for i, c in enumerate(["#ff5d73", "#ffd23f", "#4dc3ff", "#7be0a1", "#c58bff", "#ff9f43"]):
        kit.sphere(f"party.balloon{i}", 0.33, (px + 1.5 + i * 0.7 - 2.2, py + 3.9, 2.5 + 0.2 * (i % 2)), kit.plastic(c, 0.2, spec=0.6),
                   seg=12)
        kit.box(f"party.string{i}", (0.015, 0.015, 1.2), (px + 1.5 + i * 0.7 - 2.2, py + 3.9, 1.7 + 0.2 * (i % 2) - 0.0),
                kit.plastic("#fffaf0", 0.6))
    for i in range(10):
        c = ["#ff5d73", "#ffd23f", "#4dc3ff", "#7be0a1"][i % 4]
        kit.box(f"party.flag{i}", (0.4, 0.04, 0.4), (px - 3.6 + i * 0.8, py + 4.3, 3.0 - 0.1 * (i % 2)), kit.plastic(c, 0.6),
                rot=(0, 0.785, 0))
    try:
        kit.prop("couch_medium1", (px + 3.6, py + 3.2, 0), rot=180, height=1.0, tint="#c8e6ff")
        kit.prop("houseplant_1", (px - 5.0, py + 3.6, 0), height=1.5)
    except Exception:
        pass
    kit.light("party.lamp", "POINT", (px, py - 1.0, 3.0), 380.0, "#fff4e0", size=0.8, shadow=False)
    kit.light("party.lamp2", "POINT", (px - 1.5, py + 2.0, 2.6), 160.0, "#ffe0c0", size=0.5, shadow=False)


def smiley(kit, nm, loc, mat, parent=None, axis="x", s=1.0, edge=None, grow=0.03, back=0.0075):
    """A smiley wiped in fog: two eyes and a mouth of four pieces, each with a dark edge behind it (`edge` material,
    `grow` m bigger all round, `back` m further into the fog). axis "x": the pane faces x (pieces spread in y, z);
    axis "y": the pane faces y (pieces spread in x, z). Returns [[wipe, edge], ...]; edge is None without a material."""
    parts = [(-0.11, 0.09, 0.05, 0.07), (0.11, 0.09, 0.05, 0.07), (-0.15, -0.03, 0.06, 0.045), (-0.05, -0.09, 0.07, 0.045),
             (0.05, -0.09, 0.07, 0.045), (0.15, -0.03, 0.06, 0.045)]
    obs = []
    for j, (dx, dz, w, h) in enumerate(parts):
        pair = []
        for k, (m, g, th, bk) in enumerate(((mat, 0.0, 0.012, 0.0), (edge, grow, 0.006, back))):
            if m is None:
                pair.append(None)
                continue
            if axis == "x":
                ob = kit.box(f"{nm}.p{j}.{k}", (th, w * s + g, h * s + g),
                             (loc[0] + bk, loc[1] + dx * s, loc[2] + dz * s), m, parent)
            else:
                ob = kit.box(f"{nm}.p{j}.{k}", (w * s + g, th, h * s + g),
                             (loc[0] + dx * s, loc[1] + bk, loc[2] + dz * s), m, parent)
            ob.visible_shadow = False
            pair.append(ob)
        obs.append(pair)
    return obs


def handprint(kit, nm, loc, mat, k=1.7):
    """A hand wiped in the fog (palm and four fingers and a thumb), k times life-ish size."""
    obs = [kit.box(f"{nm}.palm", (0.012, 0.15 * k, 0.17 * k), loc, mat)]
    for j, (dy, dz, h, rz) in enumerate([(-0.065, 0.14, 0.12, 10), (-0.022, 0.16, 0.14, 3), (0.022, 0.16, 0.14, -3),
                                          (0.065, 0.14, 0.12, -10)]):
        ob = kit.box(f"{nm}.f{j}", (0.012, 0.035 * k, h * k), (loc[0], loc[1] + dy * k, loc[2] + dz * k), mat)
        ob.rotation_euler = (rz * D2R, 0, 0)
        obs.append(ob)
    obs.append(kit.box(f"{nm}.th", (0.012, 0.1 * k, 0.04 * k), (loc[0], loc[1] + 0.1 * k, loc[2] + 0.04 * k), mat, rot=(0.5, 0, 0)))
    return obs


def build(kit, story, tl):
    tl["cues"].sort(key=lambda c: c["t"])
    pl = kit.plastic
    M = dict(
        cream=pl("#f3ecd8", 0.75, spec=0.05), seat=pl("#2fa58f", 0.55, spec=0.25), seatdark=pl("#1f7f6e", 0.6),
        floor=pl("#cfc6b0", 0.8, spec=0.05), runner=pl("#2fa58f", 0.7), dark=pl("#40454e", 0.7), silver=pl("#c9d1d6", 0.35, spec=0.6),
        stripe=pl("#2fa58f", 0.5, spec=0.3), steel=kit.metal("#b8bec4", 0.35), panel=kit.emit("#fffaf0", 2.2),
        navy=kit.emit("#1d2a44", 1.0), door=pl("#2fa58f", 0.6),
        trunk=pl("#7a5a3a", 0.8), crown=pl("#ff9fc2", 0.8, spec=0.05),
    )
    # a loud car's own palette
    ML = dict(M)
    ML.update(seat=pl("#ff9f2e", 0.55, spec=0.25), seatdark=pl("#d9731c", 0.6), runner=pl("#4dc3ff", 0.7),
              stripe=pl("#4dc3ff", 0.5, spec=0.3), door=pl("#4dc3ff", 0.6), cream=pl("#fff1c4", 0.75, spec=0.05))
    W["M"] = M
    # ------------------------------------------------------------------ outside lights
    sun = kit.light("sun", "SUN", (0, -30, 40), 1.0, "#fff0d8", size=0.06)
    sun.data.angle = 0.06
    fill = kit.light("fill", "SUN", (0, -30, 30), 1.0, "#cfe6ff", shadow=False)
    fill.data.angle = 0.5
    kit.aim(fill, (0, 0, 0))
    kit.light("platfill", "POINT", (6.0, 2.0, 3.0), 300.0, "#fff4e0", size=1.0, shadow=False)
    # ------------------------------------------------------------------ cars
    build_car(kit, 0.0, M, True, "q")
    build_car(kit, G.LOUD_Y0, ML, False, "L")
    build_env(kit, M)
    build_tunnel(kit, M)
    build_platform(kit, M)
    # the gap between the cars: a dark bellows
    for s in (-1, 1):
        kit.box(f"bell{s}", (0.1, 1.0, 2.4), (s * 0.7, -0.5, 1.2), M["dark"])
    kit.box("bell.top", (1.5, 1.0, 0.1), (0, -0.5, 2.4), M["dark"])
    kit.box("bell.floor", (1.5, 1.0, 0.05), (0, -0.5, 0.0), M["dark"])
    # ------------------------------------------------------------------ the quiet car's window fog
    W["fog"] = []
    W["patch"] = None
    for side in (-1, 1):
        for i in range(G.ROWS):
            y = G.row_y(i)
            m, b = amat(kit, f"fogm{side}_{i}", "#f4f9fb", 0.0, 0.9, emit=0.45)
            pane = kit.box(f"fog{side}_{i}", (0.01, 1.38, 1.18), (side * (HALF - 0.01), y, 1.55), m)
            noshadow(pane)
            W["fog"].append((b, side, i, pane))
    # Teddy's window: a small patch of fog (plant 1) and the smiley drawn inside it
    tx, ty = G.TED
    pm, pb = amat(kit, "patchm", "#f4f9fb", 0.0, 0.9)
    patch = kit.box("patch", (0.01, 0.62, 0.46), (HALF - 0.025, ty, 1.5), pm)
    noshadow(patch)
    W["patch"] = pb
    W["patchob"] = patch
    wipe = kit.plastic("#8fd4f8", 0.5, spec=0.2)
    edge = kit.plastic("#123a5e", 0.6)
    W["smiley"] = smiley(kit, "tsmile", (HALF - 0.05, ty, 1.5), wipe, s=2.3, edge=edge, grow=0.045, back=0.0075)
    # handprints on the fog (both sides), wiped clear in pale blue
    W["prints"] = []
    spots = [(1, 6, 1.45), (-1, 5, 1.5), (1, 8, 1.35), (-1, 7, 1.6), (1, 3, 1.5), (-1, 4, 1.4), (1, 9, 1.5), (-1, 2, 1.55)]
    for j, (side, row, z) in enumerate(spots):
        y = G.row_y(row) + 0.15
        loc = (side * (HALF - 0.032), y, z - 0.18)
        obs = handprint(kit, f"hp{j}", loc, kit.plastic("#5fb4e6", 0.5, spec=0.2))
        for ob in obs:
            ob.visible_shadow = False
        W["prints"].append(obs)
    # ------------------------------------------------------------------ warm seats and dipped cushions
    wm, wb = amat(kit, "warmm", "#ffb066", 0.0, 0.9)
    W["warmb"] = wb
    W["warm"] = []
    wm1, wb1 = amat(kit, "warmm1", "#ffb066", 0.0, 0.9)
    W["warm1b"] = wb1
    for c, nm, kind, side, y in W["cush"]:
        if nm.startswith("q.") and not nm.startswith("qq"):
            x = side * (0.75 if kind == "a" else 1.625)
            wd = 0.7 if kind == "a" else 0.95
            ov = kit.box(f"warmov.{nm}.{kind}", (wd - 0.1, 0.7, 0.012), (x, y, 0.512),
                         wm1 if (kind == "w" and side == 1 and abs(y - G.TED[1]) < 0.1) else wm)
            noshadow(ov)
            W["warm"].append(ov)
    # ------------------------------------------------------------------ props on seats
    sx9, sy9 = G.SEAT9
    # the flat cap on the rear top of seat nine, the lunch bag, the crumbs
    cap = pl("#7a5230", 0.8, spec=0.05)
    kit.box("cap.top", (0.34, 0.3, 0.07), (sx9 + 0.05, sy9 - 0.5, 1.45), cap, bevel=0.03, rot=(0, 0, 0.15))
    kit.box("cap.brim", (0.26, 0.14, 0.03), (sx9 + 0.05, sy9 - 0.64, 1.42), cap, bevel=0.01)
    bagm = pl("#c8935a", 0.9, spec=0.05)
    W["bag"] = kit.box("lunchbag", (0.3, 0.2, 0.34), (sx9 + 0.1, sy9 + 0.05, 0.5 + 0.17), bagm, bevel=0.02)
    W["bagtop"] = kit.box("lunchbag.top", (0.32, 0.22, 0.05), (sx9 + 0.1, sy9 + 0.05, 0.5 + 0.35), pl("#b07f48", 0.9), bevel=0.01)
    W["crumbs"] = [kit.box(f"crumb{k}", (0.04, 0.04, 0.02), (sx9 - 0.2 + 0.13 * (k % 4) + 0.02 * k, sy9 - 0.18 + 0.13 * (k // 4), 0.515),
                           pl("#d9a56b", 0.9)) for k in range(8)]
    # Teddy's coffee, its steam, and the phone
    cupm, cupl = pl("#fffaf0", 0.5), pl("#ff7a2e", 0.5)
    cup = kit.empty("cup", (tx + 0.1, ty + 0.1, 0.5))
    kit.cyl("cup.body", 0.1, 0.22, (0, 0, 0.11), cupm, cup, n=14, r2=0.085)
    kit.cyl("cup.sleeve", 0.095, 0.11, (0, 0, 0.11), cupl, cup, n=14, r2=0.09)
    kit.cyl("cup.lid", 0.105, 0.03, (0, 0, 0.235), pl("#3a3f4a", 0.5), cup, n=14)
    W["cup"] = cup
    stm = kit.plastic("#f3f8fa", 0.9, spec=0.0)
    W["steam"] = [kit.sphere(f"steam{k}", 0.05, (tx + 0.1, ty + 0.1, 0.8), stm, seg=8) for k in range(5)]
    for s_ in W["steam"]:
        s_.visible_shadow = False
    phone = kit.empty("phone", (tx - 0.2, ty - 0.1, 0.51))
    kit.box("phone.body", (0.17, 0.32, 0.03), (0, 0, 0.015), pl("#1b2030", 0.4), phone, bevel=0.01)
    kit.box("phone.screen", (0.14, 0.27, 0.01), (0, 0, 0.034), kit.emit("#7fd6ff", 1.4), phone)
    W["phone"] = phone
    # a hat on the rack (rack at z 2.0), pulled in and out by the hat cue
    hx, hy = G.RACK_HAT
    hat = kit.empty("rackhat", (-1.85, hy, 2.04))
    hm = pl("#e8493a", 0.8, spec=0.05)
    kit.cyl("rackhat.brim", 0.27, 0.025, (0, 0, 0.0125), hm, hat, n=20)
    kit.cyl("rackhat.crown", 0.17, 0.2, (0, 0, 0.12), hm, hat, n=20, r2=0.14)
    kit.cyl("rackhat.band", 0.172, 0.05, (0, 0, 0.06), pl("#fffaf0", 0.7), hat, n=20)
    W["hat"] = hat
    # the cake on seat twelve, candles lit or out
    cx12, cy12 = G.SEAT12
    cake = kit.empty("cake", (cx12, cy12 + 0.05, 0.5))
    kit.cyl("cake.base", 0.25, 0.14, (0, 0, 0.07), pl("#ffd9e0", 0.6), cake, n=24)
    kit.cyl("cake.top", 0.2, 0.1, (0, 0, 0.19), pl("#fffaf0", 0.6), cake, n=24)
    flame = kit.emit("#ffcf6e", 6.0)
    W["flames"] = []
    for k in range(3):
        a = k * 2.094
        kit.cyl(f"cake.c{k}", 0.014, 0.1, (0.09 * math.cos(a), 0.09 * math.sin(a), 0.29), pl(["#4dc3ff", "#ff5d73", "#ffd23f"][k], 0.6), cake, n=8)
        W["flames"].append(kit.sphere(f"cake.f{k}", 0.025, (0.09 * math.cos(a), 0.09 * math.sin(a), 0.36), flame, parent=cake, seg=8))
    sm_ = pl("#d8dce0", 0.9, spec=0.0)
    W["smoke"] = [kit.sphere(f"cake.sm{k}", 0.035, (0.09 * math.cos(k * 2.094), 0.09 * math.sin(k * 2.094), 0.4), sm_, cake, seg=8)
                  for k in range(3)]
    for ob in W["smoke"]:
        ob.visible_shadow = False
    W["cake"] = cake
    # the puzzle book on my aisle seat, a maze half traced in green
    mx_, my_ = -1.62, G.ME[1]
    book = kit.empty("book", (mx_, my_ + 0.05, 0.5))
    kit.box("book.cover", (0.34, 0.44, 0.03), (0, 0, 0.015), pl("#4dc3ff", 0.6), book, bevel=0.01)
    kit.box("book.page", (0.3, 0.4, 0.012), (0, 0, 0.033), pl("#fffaf0", 0.7), book)
    ink = pl("#2a3550", 0.7)
    for j, (x, y, w, h) in enumerate([(-0.12, 0.0, 0.02, 0.32), (0.0, 0.08, 0.02, 0.24), (0.12, -0.04, 0.02, 0.28),
                                       (-0.06, -0.14, 0.12, 0.02), (0.06, 0.16, 0.12, 0.02), (0.0, -0.02, 0.1, 0.02)]):
        kit.box(f"book.w{j}", (w, h, 0.004), (x, y, 0.042), ink, book)
    pen = pl("#2fd05a", 0.5)
    W["maze"] = [kit.box(f"book.g{j}", (w, h, 0.005), (x, y, 0.046), pen, book) for j, (x, y, w, h) in enumerate(
        [(-0.06, -0.19, 0.06, 0.03), (-0.06, -0.1, 0.03, 0.14), (-0.06, 0.0, 0.03, 0.06), (0.0, 0.05, 0.09, 0.03),
         (0.06, 0.1, 0.03, 0.1), (0.03, 0.16, 0.06, 0.03)])]
    kit.box("book.pen", (0.02, 0.2, 0.02), (0.22, -0.1, 0.03), pen, book)
    # ------------------------------------------------------------------ the pale stone door frame and the side door
    stone = pl("#f0e4c4", 0.95, spec=0.04)
    d0, d1 = G.DOOR
    X0, X1 = HALF - 0.04, HALF + 0.16
    kit.box("frame.j0", (X1 - X0, 0.22, 2.4), ((X0 + X1) / 2, d0 - 0.11, 1.2), stone)
    kit.box("frame.j1", (X1 - X0, 0.22, 2.4), ((X0 + X1) / 2, d1 + 0.11, 1.2), stone)
    kit.box("frame.lt", (X1 - X0, d1 - d0 + 0.44, 0.22), ((X0 + X1) / 2, (d0 + d1) / 2, 2.31), stone)
    # mortar lines between the stone blocks, standing 1 cm proud so they never z-fight
    mort = pl("#a89468", 0.95)
    for k_, zz in enumerate((0.45, 0.9, 1.35, 1.8)):
        for nm_, yy in (("j0", d0 - 0.11), ("j1", d1 + 0.11)):
            kit.box(f"frame.m{k_}{nm_}", (X1 - X0 + 0.02, 0.24, 0.02), ((X0 + X1) / 2, yy, zz), mort)
    for k_, yy in enumerate((d0 + 0.45, (d0 + d1) / 2, d1 - 0.45)):
        kit.box(f"frame.ml{k_}", (X1 - X0 + 0.02, 0.02, 0.22), ((X0 + X1) / 2, yy, 2.31), mort)
    leaf_m = M["silver"]
    glyph_g, glyph_c = pl("#2fa58f", 0.6), pl("#f3ecd8", 0.7)
    glyph_n, glyph_o = pl("#1d2a44", 0.6), pl("#ff9f43", 0.6)
    W["door_leaves"] = []
    for nm, x, face in (("in", HALF - 0.075, -1), ("out", HALF + 0.185, 1)):
        leaf = kit.empty(f"dleaf.{nm}", (x, (d0 + d1) / 2, 0))
        kit.box(f"dleaf.{nm}.panel", (0.05, d1 - d0, 2.25), (0, 0, 1.125), leaf_m, leaf)
        gx = face * 0.032
        kit.box(f"dleaf.{nm}.g", (0.012, 0.6, 0.6), (gx, 0, 1.45), glyph_g, leaf)
        kit.box(f"dleaf.{nm}.face", (0.012, 0.4, 0.44), (gx + face * 0.012, 0, 1.45), glyph_c, leaf)
        for s in (-1, 1):
            kit.box(f"dleaf.{nm}.eye{s}", (0.012, 0.06, 0.06), (gx + face * 0.024, s * 0.09, 1.55), glyph_n, leaf)
        kit.box(f"dleaf.{nm}.mouth", (0.012, 0.16, 0.035), (gx + face * 0.024, 0, 1.36), glyph_n, leaf)
        kit.box(f"dleaf.{nm}.finger", (0.012, 0.085, 0.34), (gx + face * 0.036, 0, 1.4), glyph_o, leaf)
        W["door_leaves"].append(leaf)
    # ------------------------------------------------------------------ flashback corners
    build_party(kit, M)
    # a bus window (a real frame, a street outside) with a bold smiley drawn in its fog
    bx, by = G.BUS
    wl = pl("#ffe2a8", 0.85)
    wy = by + 2.0
    hw, hh, hz = 0.8, 0.62, 1.75          # the window: half width, half height, centre height
    kit.box("bus.floor", (8, 6, 0.1), (bx, by, -0.05), pl("#b9c4cc", 0.8))
    kit.box("bus.w.l", (4 - hw, 0.3, 3.4), (bx - (4 + hw) / 2, wy, 1.7), wl)
    kit.box("bus.w.r", (4 - hw, 0.3, 3.4), (bx + (4 + hw) / 2, wy, 1.7), wl)
    kit.box("bus.w.lo", (2 * hw, 0.3, hz - hh), (bx, wy, (hz - hh) / 2), wl)
    kit.box("bus.w.hi", (2 * hw, 0.3, 3.4 - hz - hh), (bx, wy, hz + hh + (3.4 - hz - hh) / 2), wl)
    fr = pl("#3c4652", 0.5, spec=0.3)
    ft = 0.09
    kit.box("bus.fr.l", (ft, 0.34, 2 * hh + 2 * ft), (bx - hw - ft / 2, wy - 0.04, hz), fr)
    kit.box("bus.fr.r", (ft, 0.34, 2 * hh + 2 * ft), (bx + hw + ft / 2, wy - 0.04, hz), fr)
    kit.box("bus.fr.t", (2 * hw + 2 * ft, 0.34, ft), (bx, wy - 0.04, hz + hh + ft / 2), fr)
    kit.box("bus.fr.b", (2 * hw + 2 * ft, 0.34, ft), (bx, wy - 0.04, hz - hh - ft / 2), fr)
    kit.box("bus.sill", (2 * hw + 0.4, 0.4, 0.07), (bx, wy - 0.05, hz - hh - ft - 0.035), pl("#fffaf0", 0.7))
    # the street outside: sky, pastel buildings, a road
    kit.box("bus.o.sky", (30, 0.2, 14), (bx, wy + 14, 5), pl("#8fd3ff", 0.9))
    for k, (ox, w_, h_, c_) in enumerate([(-3.6, 2.6, 3.2, "#ffd9b8"), (-1.2, 2.2, 2.0, "#c8e6ff"), (1.1, 2.4, 3.6, "#ffc4c4"),
                                           (3.4, 2.6, 2.4, "#d8f0c8")]):
        kit.box(f"bus.o.b{k}", (w_, 1.0, h_), (bx + ox, wy + 5.5, h_ / 2 + 0.4), pl(c_, 0.8, spec=0.05))
        kit.box(f"bus.o.r{k}", (w_ + 0.1, 1.1, 0.12), (bx + ox, wy + 5.5, h_ + 0.46), pl("#e07a5f", 0.7))
    kit.box("bus.o.road", (30, 6, 0.1), (bx, wy + 3.5, 0.15), pl("#5a5f68", 0.8))
    bm, bb = amat(kit, "busfog", "#f1f7fa", 0.72, 0.9)
    pane = kit.box("bus.fog", (2 * hw, 0.01, 2 * hh), (bx, wy - 0.06, hz), bm)
    noshadow(pane)
    W["bussm"] = smiley(kit, "bussmile", (bx, wy - 0.1, hz), pl("#8fd4f8", 0.5, spec=0.2), axis="y", s=3.4,
                        edge=pl("#123a5e", 0.6), grow=0.07, back=0.012)
    kit.light("bus.lamp", "POINT", (bx, by - 1.0, 2.8), 300.0, "#fff4e0", size=0.8, shadow=False)
    # the bathroom at night
    tx0, ty0 = G.BATH
    kit.box("bath.floor", (6, 5, 0.1), (tx0, ty0, -0.05), kit.checker("#fffaf0", "#9ad8d0", 1.0))
    kit.box("bath.wall", (6, 0.3, 3.2), (tx0, ty0 + 2.5, 1.6), kit.checker("#fffaf0", "#bfe8e2", 2.0))
    for s in (-1, 1):
        kit.box(f"bath.side{s}", (0.3, 5, 3.2), (tx0 + s * 3, ty0, 1.6), pl("#bfe8e2", 0.8))
    kit.box("bath.ceil", (6, 5, 0.2), (tx0, ty0, 3.3), pl("#fffaf0", 0.8))
    kit.box("bath.win", (1.4, 0.1, 1.2), (tx0 + 1.6, ty0 + 2.33, 1.9), pl("#1c2658", 0.4))
    kit.box("bath.cabinet", (1.2, 0.2, 0.9), (tx0 - 1.4, ty0 + 2.3, 1.7), pl("#fffaf0", 0.5))
    kit.box("bath.counter", (1.6, 0.7, 0.85), (tx0 - 1.4, ty0 + 2.0, 0.425), pl("#4dc3ff", 0.5))
    kit.box("bath.basin", (0.7, 0.45, 0.06), (tx0 - 1.4, ty0 + 2.0, 0.88), pl("#fffaf0", 0.3))
    kit.light("bath.lamp", "POINT", (tx0, ty0 - 0.6, 2.9), 330.0, "#ffe6c0", size=0.7, shadow=False)
    # the rule meter
    build_tag(kit)
    return {}


# ------------------------------------------------------------------------------------------------- the rule meter
def build_tag(kit):
    """A cream plate on the camera (top left): a hush glyph (a face with a finger over its mouth) and my silent
    mornings in seven-segment digits."""
    cam = kit.OBJ["cam"]
    root = kit.empty("tag", (0, 0, 0), cam)
    W["tag"] = root
    cream = kit.emit("#f6efdc", 0.95, "tagcream")
    navy = kit.emit("#1d2a44", 0.9, "tagnavy")
    green = kit.emit("#2fa58f", 0.9, "taggreen")
    orange = kit.emit("#ff8a2e", 1.0, "tagorange")
    edge = kit.emit("#1d2a44", 0.8, "tagedge")

    def b(name, size, loc, mat):
        ob = kit.box(name, size, loc, mat, root)
        noshadow(ob)
        return ob

    # the plate is 2.2 x 1.16: a hush glyph 1.5x the first cut (a face with a bold finger over its mouth) and the digits
    b("tag.edge", (2.26, 1.22, 0.004), (0, 0, 0.0), edge)
    b("tag.plate", (2.18, 1.14, 0.004), (0, 0, 0.004), cream)
    GX = -0.55
    b("tag.g", (0.98, 0.98, 0.004), (GX, 0, 0.008), green)
    b("tag.face", (0.7, 0.76, 0.004), (GX, 0.0, 0.012), cream)
    for s in (-1, 1):
        b(f"tag.eye{s}", (0.12, 0.13, 0.004), (GX + s * 0.16, 0.16, 0.016), navy)
    W["tag_mouth"] = b("tag.mouth", (0.32, 0.07, 0.004), (GX, -0.17, 0.016), navy)
    W["tag_open"] = b("tag.open", (0.22, 0.27, 0.004), (GX, -0.17, 0.016), navy)
    # the finger: a thick orange bar with a navy outline, down over the mouth
    W["tag_finger_o"] = b("tag.fingero", (0.25, 0.66, 0.004), (GX, -0.04, 0.019), navy)
    W["tag_finger"] = b("tag.finger", (0.18, 0.6, 0.004), (GX, -0.04, 0.022), orange)
    W["digits"] = []
    for i, x in enumerate([0.2, 0.44, 0.68, 0.92]):
        W["digits"].append(digit_boxes(kit, f"tag.d{i}", "8", 0.17, 0.5, 0.06, navy, root, (x, 0.0), plane="xy", z=0.012))
        for ob in W["digits"][-1].values():
            noshadow(ob)
    b("tag.comma", (0.05, 0.05, 0.004), (0.325, -0.22, 0.012), navy)
    b("tag.comma2", (0.035, 0.065, 0.004), (0.31, -0.27, 0.012), navy)


def _first_frame(kit, story):
    # a long gray beard and a mustache; fogged glasses; the conductor's mustache
    bg = bpy.data.objects.get("beard.headg")
    if bg is not None:
        m = kit.plastic("#c9ccd2", 0.8)
        kit.box("beard.jaw", (0.82, 0.3, 0.55), (0, -0.55, -0.35), m, bg, bevel=0.1)
        kit.box("beard.long", (0.66, 0.26, 0.62), (0, -0.55, -0.82), m, bg, bevel=0.1)
        kit.box("beard.stache", (0.56, 0.1, 0.12), (0, -0.62, -0.2), m, bg, bevel=0.03)
        kit.box("beard.brow", (0.7, 0.05, 0.05), (0, -0.62, 0.17), m, bg)
    cg = bpy.data.objects.get("conductor.headg")
    if cg is not None:
        m = kit.plastic("#8d9096", 0.8)
        kit.box("cond.stache", (0.56, 0.1, 0.11), (0, -0.62, -0.19), m, cg, bevel=0.03)
    mg = bpy.data.objects.get("me.headg")
    W["glassfog"] = []
    if mg is not None:
        rim = kit.plastic("#15151a", 0.4)
        for s_ in (-1, 1):
            cx_ = s_ * 0.24
            for nm, sz, lc in (("t", (0.5, 0.05, 0.05), (cx_, 0.17)), ("b", (0.5, 0.05, 0.05), (cx_, -0.21)),
                               ("l", (0.05, 0.05, 0.38), (cx_ - 0.225, -0.02)), ("r", (0.05, 0.05, 0.38), (cx_ + 0.225, -0.02))):
                kit.box(f"me.rim{s_}{nm}", sz, (lc[0], -0.62 - 0.03, lc[1]), rim, mg)
        kit.box("me.bridge", (0.1, 0.05, 0.05), (0, -0.65, 0.1), rim, mg)
        fm, fb = amat(kit, "glassfogm", "#f2f8fa", 0.0, 0.9)
        for s in (-1, 1):
            ob = kit.box(f"me.lensfog{s}", (0.44, 0.02, 0.34), (s * 0.24, -0.62 - 0.02, -0.02), fm, mg)
            noshadow(ob)
        W["glassfogb"] = fb
        wipe = kit.plastic("#7fc8f0", 0.5, spec=0.2)
        for j, (dx, dz, w, h) in enumerate([(-0.24, 0.05, 0.07, 0.07), (0.24, 0.05, 0.07, 0.07), (-0.2, -0.07, 0.07, 0.04),
                                            (-0.07, -0.12, 0.09, 0.04), (0.07, -0.12, 0.09, 0.04), (0.2, -0.07, 0.07, 0.04)]):
            ob = kit.box(f"me.lensmile{j}", (w, 0.012, h), (dx, -0.62 - 0.045, dz), wipe, mg)
            ob.visible_shadow = False
            W["glassfog"].append(ob)
    barm = bpy.data.objects.get("beard.arm1")
    if barm is not None:
        W["bbag"] = kit.box("beard.bag", (0.7, 0.5, 0.8), (0, -0.7, -1.95), kit.plastic("#c8935a", 0.9, spec=0.05), barm, bevel=0.03)
    # the cup that I carry (a second coffee), parented to my right arm
    arm = bpy.data.objects.get("me.arm1")
    if arm is not None:
        cm = kit.plastic("#fffaf0", 0.5)
        W["cup2"] = kit.cyl("cup2.body", 0.3, 0.7, (0, -0.45, -1.9), cm, arm, n=14, r2=0.25)
        W["cup2lid"] = kit.cyl("cup2.lid", 0.31, 0.1, (0, -0.45, -1.5), kit.plastic("#3a3f4a", 0.5), arm, n=14)
        W["cup2sl"] = kit.cyl("cup2.sleeve", 0.29, 0.35, (0, -0.45, -1.9), kit.plastic("#ff7a2e", 0.5), arm, n=14, r2=0.27)
    W["inited"] = True


def _setfog(b, a):
    b.inputs["Alpha"].default_value = max(0.0, min(1.0, a))


_POL = {}


def _crop_at(story, tl, t):
    """(zoom, dx, dy) of the polish pack's crop at t, the same call post.finish makes."""
    try:
        from blocky import polish
        pol = polish.spec(story)
        key = id(tl)
        if key not in _POL:
            _POL.clear()
            _POL[key] = polish.emph_times(tl, pol)
        return polish.motion(tl, story, pol, t, _POL[key])
    except Exception:
        return 1.25, 0.0, 0.0


def animate(kit, story, tl, t, ctx):
    if not W.get("inited"):
        _first_frame(kit, story)
    look = look_at(tl, t)
    gains = {}
    az, el = look["az"] * D2R, look["el"] * D2R
    d = Vector((math.sin(az) * math.cos(el), math.cos(az) * math.cos(el), math.sin(el)))
    so = kit.LIGHTS["sun"]["obj"]
    so.location = d * 60
    kit.aim(so, (0, 0, 0))
    kit.LIGHTS["sun"]["light"].color = look["sun_col"]
    kit.LIGHTS["fill"]["light"].color = look["fill_col"]
    gains["sun"], gains["fill"] = look["sun"], look["fill"]
    # in the tunnel: the exposure drops hard (blue-black windows) and only the ceiling panel lights the faces; ramped 0.3 s
    te = [c for c in tl["cues"] if c["name"] == "env" and "tunnel" in c]
    tun_a, tprev_ = 0.0, 0.0
    for c in te:
        if c["t"] > t:
            break
        tun_a = max(0.0, min(1.0, tprev_ + (c["tunnel"] - tprev_) * ss((t - c["t"]) / 0.3)))
        tprev_ = c["tunnel"]
    bpy.context.scene.view_settings.exposure = 0.25 - 1.15 * tun_a
    for k_ in range(7):
        gains[f"q.lamp{k_}"] = 1.0 - 0.45 * tun_a
        gains[f"L.lamp{k_}"] = 1.0 - 0.45 * tun_a
    w = bpy.context.scene.world
    bg = w.node_tree.nodes["Background"]
    bg.inputs["Color"].default_value = (*look["sky"], 1.0)
    bg.inputs["Strength"].default_value = look["sky_str"]
    env = sample("env", tl, t, {"tunnel": 0.0, "plat": 0.0})
    tun = env["tunnel"] > 0.5
    _hide(W["tunnel"], not tun)
    _hide(W["env"], tun)
    _hide(W["plat"], env["plat"] < 0.5 or tun)
    # scenery slides past while the train moves ("move" cues switch it on a cut)
    pos, speed, tprev = 0.0, 1.0, 0.0
    for c in sorted((c for c in tl["cues"] if c["name"] == "move"), key=lambda c: c["t"]):
        if c["t"] > t:
            break
        pos += speed * G.SPEED * (c["t"] - tprev)
        speed, tprev = float(c.get("v", 1.0)), c["t"]
    pos += speed * G.SPEED * (t - tprev)
    W["env"].location.y = -(pos % G.ENV_PERIOD)
    W["lamps"].location.y = -(pos % 8.0)
    # the season (trees on the line)
    se = sample("season", tl, t, {"s": 0.0})["s"]
    cols = [(1.0, 0.62, 0.76), (0.28, 0.66, 0.3), (0.95, 0.5, 0.15)]
    if se <= 1.0:
        a, b_, u = cols[0], cols[1], se
    else:
        a, b_, u = cols[1], cols[2], se - 1.0
    c = tuple(a[i] + (b_[i] - a[i]) * u for i in range(3))
    mc = W["M"]["crown"]
    bsdf = mc.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (*kit_col("#%02x%02x%02x" % tuple(int(255 * v) for v in c)), 1.0)
    # the window fog: sweeps front (high y) to back, clears row by row
    fg = sample("fog", tl, t, {"p": 0.0})["p"]
    cl = sample("clear", tl, t, {"q": 0.0})["q"]
    sw = sample("swell", tl, t, {"s": 0.0})["s"]
    for b, side, i, pane in W["fog"]:
        rank = (G.ROWS - 1 - i) / (G.ROWS - 1)
        a_in = ss((fg - rank * 0.5) / 0.5)
        a_cl = ss((cl - (i / (G.ROWS - 1)) * 0.6) / 0.4)
        a = min(0.97, 0.88 * a_in * (1.0 - a_cl) * (1.0 + 0.08 * sw))
        _setfog(b, a)
        pane.hide_render = a < 0.01
    pa = sample("patch", tl, t, {"a": 0.0})["a"]
    _setfog(W["patch"], 0.72 * pa)
    sm = sample("smiley", tl, t, {"p": 0.0})["p"]
    grow = ss(sm / 1.5)
    W["patchob"].scale = (1.0, 1.0 + 0.6 * grow, 1.0 + 0.7 * grow)
    for j, pair in enumerate(W["smiley"]):
        for ob in pair:
            if ob is not None:
                ob.hide_render = sm < j + 0.5
    pr = sample("prints", tl, t, {"p": 0.0})["p"]
    for j, obs in enumerate(W["prints"]):
        for ob in obs:
            ob.hide_render = pr < j + 0.5
    # warm seats: a faint heat shimmer (slow)
    wa = sample("warm", tl, t, {"a": 0.0})["a"]
    wa1 = sample("warm1", tl, t, {"a": 0.0})["a"]
    shim = 0.85 + 0.15 * math.sin(t * 1.7)
    _setfog(W["warmb"], 0.38 * wa * shim)
    _setfog(W["warm1b"], 0.38 * max(wa, wa1) * shim)
    for ov in W["warm"]:
        ov.hide_render = (wa < 0.01 and wa1 < 0.01)
    dp = sample("dip", tl, t, {"u": 0.0})["u"]
    for c_, nm, kind, side, y in W["cush"]:
        if nm.startswith("q."):
            c_.scale.z = 1.0 - 0.5 * dp
    # a door that slides
    do = sample("door", tl, t, {"u": 0.0})["u"]
    for lf in W["door_leaves"]:
        lf.location.y = (G.DOOR[0] + G.DOOR[1]) / 2 + 1.55 * do
    # the coffee: 0 none, 1 steaming, 2 cold
    cv = sample("cup", tl, t, {"v": 0.0})["v"]
    _hide(W["cup"], cv < 0.5)
    for k, s_ in enumerate(W["steam"]):
        ph = (t * 0.45 + k * 0.2) % 1.0
        s_.hide_render = not (0.5 < cv < 1.5)
        s_.location = (G.TED[0] + 0.1 + 0.03 * math.sin(t * 2 + k * 1.3), G.TED[1] + 0.1, 0.8 + 0.3 * ph)
        r = 0.05 * (1.0 - ph * 0.5)
        s_.scale = (r / 0.05, r / 0.05, r / 0.05)
    # the phone buzz
    pv = sample("phone", tl, t, {"v": 0.0})["v"]
    _hide(W["phone"], pv < 0.5)
    ph0 = (G.TED[0] - 0.2, G.TED[1] - 0.1)
    off = 0.012 * math.sin(t * 22) if pv > 1.5 else 0.0
    W["phone"].location = (ph0[0] + off, ph0[1] + off * 0.6, 0.51)
    # the hat on the rack
    hv = sample("hat", tl, t, {"v": 0.0})["v"]
    _hide(W["hat"], hv < 0.5)
    # the cake: 0 none, 1 lit, 2 out
    cakev = sample("cake", tl, t, {"v": 0.0})["v"]
    _hide(W["cake"], cakev < 0.5)
    for k, f in enumerate(W["flames"]):
        f.hide_render = not (0.5 < cakev < 1.5)
        f.scale = (1, 1, 1.0 + 0.2 * math.sin(t * 5 + k * 2))
    for k, s_ in enumerate(W["smoke"]):
        ph = (t * 0.4 + k * 0.3) % 1.0
        s_.hide_render = cakev < 1.5
        s_.location.z = 0.4 + 0.25 * ph
        s_.location.x = 0.09 * math.cos(k * 2.094) + 0.03 * math.sin(t * 2 + k)
    # the lunch bag: 0 none, 1 bag, 2 flat with crumbs
    lv = sample("lunch", tl, t, {"v": 0.0})["v"]
    W["bag"].hide_render = lv < 0.5 or lv > 1.5
    W["bagtop"].hide_render = lv < 0.5 or lv > 1.5
    # on the wife's flat palm until she sets it down on the seat
    lf = sample("lift", tl, t, {"u": 0.0})["u"]
    sx9, sy9 = G.SEAT9
    hand = (sx9 - 0.25, sy9 - 0.1, 1.0)
    seat_ = (sx9 + 0.1, sy9 + 0.05, 0.5 + 0.17)
    for ob, dz in ((W["bag"], 0.0), (W["bagtop"], 0.18)):
        ob.location = tuple(seat_[i] + (hand[i] - seat_[i]) * lf + (dz if i == 2 else 0.0) for i in range(3))
    for cr in W["crumbs"]:
        cr.hide_render = lv < 1.5
    # the maze
    mz = sample("maze", tl, t, {"p": 0.0})["p"]
    for j, ob in enumerate(W["maze"]):
        ob.hide_render = mz < j + 0.5
    # shadows of the riders stepping out
    sh_t = sample("shadows", tl, t, {"t0": 1e9})["t0"]
    for i, sh in enumerate(W["shadows"]):
        tt = t - sh_t - i * 0.32
        if tt < 0 or sh_t > 1e8:
            sh.hide_render = True
            for c_ in sh.children:
                c_.hide_render = True
            continue
        sh.hide_render = False
        for c_ in sh.children:
            c_.hide_render = False
        lane = (-1.0 + (i % 3) * 1.0) * 1.1
        sh.location = (2.4 + 1.5 * tt, 1.1 + lane - 0.0, 0.03)
        sh.rotation_euler = (0, 0, 90 * D2R)
        sh.scale = (1.0 + 0.1 * (i % 2), 1.4, 1.0)
    # the glasses fog (Teddy's hug) and its smiley
    ga = sample("glass", tl, t, {"a": 0.0, "s": 0.0})
    if "glassfogb" in W:
        _setfog(W["glassfogb"], 0.7 * ga["a"])
        for j, ob in enumerate(W["glassfog"]):
            ob.hide_render = ga["s"] < j + 0.5
    # the hush glyph opens its mouth
    gy = sample("glyph", tl, t, {"u": 0.0})["u"]
    for k_ in ("tag_finger", "tag_finger_o"):
        W[k_].scale = (max(0.001, 1 - gy), max(0.001, 1 - gy), 1)
        W[k_].hide_render = gy > 0.97
    W["tag_mouth"].scale = (max(0.001, 1 - gy), 1, 1)
    W["tag_open"].scale = (max(0.001, gy), max(0.001, gy), 1)
    W["tag_open"].hide_render = gy < 0.03
    W["tag_mouth"].hide_render = gy > 0.97
    # the count
    n = int(round(sample("count", tl, t, {"n": 1512.0})["n"]))
    txt = "%04d" % min(9999, max(0, n))
    for dg, ch in zip(W["digits"], txt):
        for s_, ob in dg.items():
            ob.hide_render = s_ not in DIG[ch]
    # the second coffee in my hand
    c2 = sample("cup2", tl, t, {"v": 0.0})["v"]
    for k in ("cup2", "cup2lid", "cup2sl"):
        if k in W:
            W[k].hide_render = c2 < 0.5
    # who sits: legs straight out forward, hips on the seat
    sits = {}
    for c in tl["cues"]:
        if c["name"] == "sit" and c["t"] <= t:
            sits[c["who"]] = c
    for who, c in sits.items():
        root = bpy.data.objects.get(who)
        if c.get("on") and root is not None:
            root.location.z += c.get("z", G.HIP) - 0.68
            for sx in (-1, 1):
                leg = bpy.data.objects.get(f"{who}.leg{sx}")
                if leg:
                    leg.rotation_euler = (-math.pi / 2 * 0.97, 0, 0)
    # the tag sits in the top-left corner at a fixed size, whatever the lens
    lens = 40.0
    shot = next((s for s in tl["shots"] if s["start"] <= t < s["end"]), tl["shots"][-1])
    spec = next((s for s in story["shots"] if s["id"] == shot["id"]), None)
    if spec:
        keys = spec["cam"]
        u = (t - shot["start"]) / max(1e-6, shot["end"] - shot["start"])
        lens = keys[0][3]
        if len(keys) > 1:
            for a, b in zip(keys, keys[1:]):
                if u <= b[0]:
                    lens = a[3] + (b[3] - a[3]) * ss((u - a[0]) / max(1e-6, b[0] - a[0]))
                    break
            else:
                lens = keys[-1][3]
    dist = 0.3          # close to the lens, so nothing in the set can stand between it and the camera
    h2 = dist * 12.0 / lens
    w2 = h2 * 9.0 / 16.0
    # the polish pack crops the drawing (zoom, slide): put the tag in the corner of what is left of it, so it is
    # never cut off, and shrink it with the crop so it holds one size on the screen
    zoom, dx, dy = _crop_at(story, tl, t)
    z = max(zoom, 1.0 + 2 * max(abs(dx), abs(dy)) + 1e-3)
    cx, cy = 2 * w2 * dx, -2 * h2 * dy
    s = 0.40 * w2 / z
    tag = W["tag"]
    tag.scale = (s, s, s)
    tag.location = (cx - 0.93 * w2 / z + 1.13 * s, cy + 0.90 * h2 / z - 0.61 * s, -dist)
    return gains
