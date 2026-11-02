"""Top Rope (ep30): a climbing wall built inside a tall old brick mill, and the Headstander. Built from kit.py's
parts (nothing here is shared with another story's set). There is no text anywhere in it: no signs, grades or brands.

Coordinates (metres): the floor is z = 0. The climbing wall is the plane y = 0 (the panels, x -2.6 .. 2.6, z 0 .. 9.8),
and the room is on the -y side, so the camera usually looks toward +y. A climber faces the wall, i.e. yaw 180. At
z = 9.8 the wall meets the overhang roof, a 3 m slab (y -3 .. 0) whose underside is the "ceiling" of holds. The
top hold is at TOP_HOLD (z 8.35), the anchor plate and ring at x = ANCHOR_X (z about 8.9), the grey auto-belay box
at x = +0.55 with the red tag hanging from it.

THE HEADSTANDER: an ordinary blocky person, its down set the wrong way. It is a rig.Character built once here
(`story["creature"]` is its spec) and flipped over (a half turn about x) so its soles stand flat on the roof's
underside, arms hanging toward the ceiling. Its whole body is chalk-dust lilac and matte, with a black harness round
the waist, and a drawn grin that, seen from below, reads as a frown. It is never seen moving: a "head" cue names its
POSE (where it stands) and the story only ever cuts from one pose to the next. Its key is a lamp from below and a cold
blue rim from the windows (see `looks`), its eyes are the brightest thing on it.

Cues read here (all optional; times from the timeline):
- head: {"pose": a name in POSES} or {"hidden": true}
- lamps: {"to": 0..1, "dur": s} the iron lamps' level, ramped from where it was. flood: the same for the floodlights.
- rope: {"mode": "me" | "creature" | "sam" | "end_up" | "end_down" | "none"} what the rope joins:
  me = my harness to the anchor ring and up to the roof; creature = the same, and on to its waist;
  sam = my harness to the ring and down to Sam's harness; end_up / end_down = the free end sliding.
- tag: {"swing": amplitude in degrees}
- coil: {"on": bool} the rope end lying on the mat (the lilac-dusted end)
Story keys: "looks": {shot id: {"lamps": g, "flood": g, "key": [pos, aim, watts], "rim": [...], "fill": g}}.
"""

from __future__ import annotations

import math
import tempfile
from pathlib import Path

import bpy
from mathutils import Vector as V

from blocky import acting, rig

ANCHOR_X = -0.45
ANCHOR_Z = 8.9
TOP_HOLD = 8.35
ROOF_Z = 9.8
LILAC = "#b9a3d9"
ROPE_C = "#d4cae4"
S = rig.S

# where the Headstander stands on the roof: x, y of its feet, yaw (degrees, 0 faces the wall), lean (degrees past a half
# turn: + leans its body toward the room), head pitch
POSES = {
    "t1": {"pos": (0.15, -2.55), "yaw": 0, "lean": 0},        # three holds back from the lip
    "t2": {"pos": (0.15, -1.75), "yaw": 0, "lean": 0},        # two holds back
    "t3": {"pos": (0.15, -1.05), "yaw": 0, "lean": 0},        # one hold back, right over my route
    "lip": {"pos": (0.66, -0.4), "yaw": 125, "lean": 0},      # at my shoulder, face level with mine
    "belay": {"pos": (0.66, -0.4), "yaw": 125, "lean": -22},  # leaning back from the lip, the rope tied round it
}


def _ss(x):
    x = min(1.0, max(0.0, x))
    return x * x * (3 - 2 * x)


def _cues(tl, name):
    return [c for c in tl.get("cues", []) if c["name"] == name]


def _last(cs, t):
    cs = [c for c in cs if c["t"] <= t + 1e-9]
    return cs[-1] if cs else None


def level(cs, t, start=1.0):
    v = start
    for i, c in enumerate(cs):
        if c["t"] > t:
            break
        d = max(1e-3, c.get("dur", 0.01))
        u = _ss((t - c["t"]) / d)
        v = v + (c["to"] - v) * u
        if u < 1:
            return v
        v = c["to"]
    return v


# ------------------------------------------------------------------------------------------------ small parts


def torus(kit, name, R, r, loc, mat, rot=(0, 0, 0)):
    bpy.ops.mesh.primitive_torus_add(major_radius=R, minor_radius=r, major_segments=28, minor_segments=8,
                                     location=loc, rotation=rot)
    ob = bpy.context.active_object
    ob.name = name
    ob.data.materials.append(mat)
    for p in ob.data.polygons:
        p.use_smooth = True
    return ob


def seg_between(ob, a, b):
    a, b = V(a), V(b)
    d = b - a
    ln = max(1e-4, d.length)
    ob.location = (a + b) / 2
    ob.rotation_euler = d.to_track_quat("Z", "Y").to_euler()
    ob.scale = (1, 1, ln)
    ob.hide_render = False


def hold_spots(seed, n, xr, zr):
    out, k = [], 0
    while len(out) < n:
        k += 1
        x = xr[0] + (xr[1] - xr[0]) * ((math.sin(k * 12.9898 + seed) * 43758.5453) % 1.0)
        z = zr[0] + (zr[1] - zr[0]) * ((math.sin(k * 78.233 + seed * 3.1) * 24634.6345) % 1.0)
        if all(abs(x - a) > 0.38 or abs(z - b) > 0.32 for a, b in out):
            out.append((x, z))
    return out


# ------------------------------------------------------------------------------------------------ build


def build(kit, story, tl):
    ctx = {"rope": [], "extras": False}
    brick = kit.bricks("#4a342b", "#38261f", "#2a2522", scale=1.0)
    timber = kit.planks("#6b4a2e", "#4e3520", scale=1.0)
    iron = kit.metal("#2b2d30", 0.5)
    steel = kit.metal("#9a9fa4", 0.3)
    floor = kit.concrete("#4b4a47", 1.4, 0.5)
    panel = kit.plastic("#5f6e64", 0.8, spec=0.15)
    seam = kit.plastic("#3d4740", 0.9, spec=0.1)
    mat_blue = kit.plastic("#2a4c8f", 0.85, spec=0.1)
    rope_m = kit.plastic(ROPE_C, 0.9, spec=0.1)
    lilac = kit.plastic(LILAC, 0.9, spec=0.1)
    win = kit.emit("#1d3a6b", 4.0)
    frame = kit.plastic("#16181c", 0.7)

    # --- the mill: floor, walls, ceiling
    kit.box("floor", (22, 16, 0.3), (0, -7.0, -0.15), floor)
    kit.box("back", (22, 0.4, 15), (0, 0.2, 7.5), brick)
    kit.box("wallL", (0.4, 16, 15), (-9.6, -7.0, 7.5), brick)
    kit.box("wallR", (0.4, 16, 15), (9.6, -7.0, 7.5), brick)
    kit.box("wallF", (22, 0.4, 15), (0, -15.0, 7.5), brick)
    kit.box("ceil", (22, 16, 0.3), (0, -7.0, 14.9), kit.plastic("#1a1512", 0.9))
    for k, y in enumerate((-2.2, -6.0, -9.8, -13.2)):          # timber beams across the hall
        kit.box(f"beam{k}", (19.2, 0.5, 0.65), (0, y, 13.0), timber)
    for k, (x, y) in enumerate(((-7.6, -4.2), (7.6, -4.2), (-7.6, -9.4), (7.6, -9.4))):   # cast-iron columns
        kit.cyl(f"col{k}", 0.24, 14.0, (x, y, 7.0), iron)
        kit.box(f"colb{k}", (0.6, 0.6, 0.2), (x, y, 0.1), iron)

    # --- arched windows: deep evening blue (the fill), in both side walls and the back wall either side of the panels
    def window(name, x, y, facing):
        w, h = 1.5, 3.4
        if facing == "x":      # in a side wall, facing across the hall
            kit.box(f"{name}.g", (0.06, w, h), (x, y, 4.6), win)
            kit.cyl(f"{name}.a", w / 2, 0.06, (x, y, 4.6 + h / 2), win, rot=(0, math.pi / 2, 0), n=24)
            kit.box(f"{name}.m1", (0.09, 0.07, h + w / 2), (x, y, 4.6 + w / 4), frame)
            kit.box(f"{name}.m2", (0.09, w, 0.07), (x, y, 5.0), frame)
            kit.box(f"{name}.m3", (0.09, w, 0.07), (x, y, 6.6), frame)
        else:                  # in the back wall
            kit.box(f"{name}.g", (w, 0.06, h), (x, y, 4.6), win)
            kit.cyl(f"{name}.a", w / 2, 0.06, (x, y, 4.6 + h / 2), win, rot=(math.pi / 2, 0, 0), n=24)
            kit.box(f"{name}.m1", (0.07, 0.09, h + w / 2), (x, y, 4.6 + w / 4), frame)
            kit.box(f"{name}.m2", (w, 0.09, 0.07), (x, y, 5.0), frame)
            kit.box(f"{name}.m3", (w, 0.09, 0.07), (x, y, 6.6), frame)
    for k, y in enumerate((-3.2, -7.6, -12.0)):
        window(f"winL{k}", -9.38, y, "x")
        window(f"winR{k}", 9.38, y, "x")
    for k, x in enumerate((-5.6, 5.6)):
        window(f"winB{k}", x, -0.02, "y")

    # --- the climbing wall: panels, seams, holds, the overhang roof
    kit.box("panels", (5.2, 0.12, 9.8), (0, -0.06, 4.9), panel)
    for k in range(1, 4):
        kit.box(f"seamv{k}", (0.025, 0.125, 9.8), (-2.6 + k * 1.3, -0.063, 4.9), seam)
    for k in range(1, 8):
        kit.box(f"seamh{k}", (5.2, 0.125, 0.025), (0, -0.063, k * 1.2), seam)
    kit.box("kick", (5.2, 0.2, 0.3), (0, -0.1, 0.15), seam)
    hold_cols = ["#c9923a", "#4c5760", "#8c3a2c", "#d8c9a0"]
    for k, (x, z) in enumerate(hold_spots(1.0, 62, (-2.4, 2.4), (0.7, 9.4))):
        if abs(x - ANCHOR_X) < 0.5 and 8.4 < z < 9.5:
            continue
        if abs(x - 0.4) < 0.5 and 8.4 < z < 9.5:
            continue
        if abs(x) < 0.32 and abs(z - TOP_HOLD) < 0.3:
            continue
        sx, sy, sz = 0.26 + 0.12 * ((k * 7) % 3) / 2, 0.17, 0.17 + 0.1 * ((k * 5) % 3) / 2
        kit.box(f"hold{k}", (sx, sy, sz), (x, -0.12 - sy / 2 + 0.02, z), kit.plastic(hold_cols[k % 4], 0.5, spec=0.2),
                rot=(0, 0.35 * math.sin(k), 0.5 * math.cos(k * 1.7)), bevel=0.05)
    kit.box("tophold", (0.4, 0.2, 0.2), (0.0, -0.2, TOP_HOLD), kit.plastic("#c9923a", 0.5, spec=0.2), bevel=0.06)
    kit.box("roof", (5.2, 3.0, 0.3), (0, -1.5, ROOF_Z + 0.15), panel)
    kit.box("fascia", (5.2, 0.14, 0.55), (0, -3.0, ROOF_Z + 0.05), seam)
    for k, (x, y) in enumerate(hold_spots(5.0, 44, (-2.4, 2.4), (-2.85, -0.25))):
        sx, sy, sz = 0.24, 0.24, 0.16
        kit.box(f"rhold{k}", (sx, sy, sz), (x, y, ROOF_Z - sz / 2 + 0.02), kit.plastic(hold_cols[(k + 2) % 4], 0.5, spec=0.2),
                rot=(0.3 * math.sin(k * 2), 0.3 * math.cos(k), 0.7 * k), bevel=0.05)

    # --- the anchor: a steel plate with the ring, two upright lilac strokes scratched beside it (the lore tally)
    kit.box("plate", (0.5, 0.03, 0.56), (ANCHOR_X, -0.135, ANCHOR_Z - 0.02), steel, bevel=0.012)
    for k, (dx, dz) in enumerate(((-0.16, 0.2), (-0.16, -0.2), (0.16, 0.2), (0.16, -0.2))):
        kit.cyl(f"bolt{k}", 0.025, 0.03, (ANCHOR_X + dx, -0.158, ANCHOR_Z - 0.02 + dz), steel, rot=(math.pi / 2, 0, 0), n=10)
    torus(kit, "ring", 0.085, 0.017, (ANCHOR_X, -0.19, ANCHOR_Z + 0.07), steel, rot=(math.pi / 2, 0, 0))
    glow = kit.emit(LILAC, 0.9)
    kit.box("stroke1", (0.04, 0.012, 0.26), (ANCHOR_X - 0.085, -0.153, ANCHOR_Z - 0.14), glow, rot=(0, 0.06, 0))
    kit.box("stroke2", (0.04, 0.012, 0.26), (ANCHOR_X + 0.085, -0.153, ANCHOR_Z - 0.14), glow, rot=(0, -0.05, 0))

    # --- the auto-belay box (broken for weeks) and its red tag on a cord
    kit.box("abox", (0.42, 0.3, 0.56), (0.4, -0.17, 8.95), kit.plastic("#7d8388", 0.55, spec=0.3), bevel=0.03)
    kit.box("abox2", (0.46, 0.06, 0.1), (0.4, -0.33, 9.16), kit.plastic("#5a6065", 0.6), bevel=0.02)
    tag = kit.empty("tagpivot", (0.3, -0.3, 8.66))
    kit.cyl("cord", 0.008, 0.14, (0, 0, -0.07), kit.plastic("#222222", 0.8), tag, n=8)
    kit.box("tag", (0.13, 0.02, 0.21), (0, 0, -0.24), kit.plastic("#c8322a", 0.55, spec=0.2), tag, bevel=0.008)
    ctx["tag"] = tag

    # --- the base: crash mats, bench, chalk bucket, a coil of rope, the lilac-dusted rope end
    kit.box("mat", (6.6, 3.6, 0.3), (0, -1.9, 0.15), mat_blue, bevel=0.04)
    kit.box("matb", (6.6, 3.0, 0.3), (0, -5.1, 0.15), mat_blue, bevel=0.04)
    kit.box("benchs", (1.9, 0.5, 0.08), (4.4, -4.6, 0.46), timber)
    for sx in (-0.8, 0.8):
        kit.box(f"benchl{sx}", (0.1, 0.45, 0.45), (4.4 + sx, -4.6, 0.22), timber)
    kit.cyl("bucket", 0.22, 0.4, (3.3, -4.9, 0.2), kit.plastic("#ddd9cf", 0.8), n=20)
    kit.cyl("coil", 0.34, 0.14, (-4.6, -4.4, 0.07), rope_m, n=24)
    kit.cyl("coil2", 0.2, 0.15, (-4.6, -4.4, 0.08), kit.plastic("#222222", 0.9), n=16)
    coil = []
    for k in range(5):
        o = kit.cyl(f"coilend{k}", 0.026, 1.0, (0, 0, -9), kit.emit("#a48fcb", 0.6), n=8)
        coil.append(o)
    ctx["coil"] = coil
    kit.box("phone", (0.075, 0.155, 0.012), (1.9, -3.55, 0.306), kit.emit("#bfe0ff", 2.2), rot=(0, 0, 0.4))
    kit.cyl("tape", 0.06, 0.04, (4.0, -4.6, 0.52), kit.plastic("#e8e2d0", 0.8), n=16)
    # --- the rope: a pool of thin rods between points
    for k in range(7):
        ctx["rope"].append(kit.cyl(f"rope{k}", 0.016, 1.0, (0, 0, -9), rope_m, n=8))
        ctx["rope"][-1].hide_render = True

    # --- lamps on chains, floodlights, the window fill
    lamp_pos = ((-5.2, -5.2), (5.2, -5.2), (0.0, -8.4), (-5.2, -11.4), (5.2, -11.4), (-3.0, -3.6), (3.0, -3.6))
    for k, (x, y) in enumerate(lamp_pos):
        zt = 11.2
        beam_z = 12.67
        kit.cyl(f"chain{k}", 0.012, beam_z - zt - 0.2, (x, y, (beam_z + zt + 0.2) / 2), iron, n=6)
        kit.cyl(f"shade{k}", 0.34, 0.26, (x, y, zt + 0.1), iron, n=20, r2=0.1)
        kit.sphere(f"bulb{k}", 0.1, (x, y, zt - 0.05), kit.emit("#ffc77a", 14.0), seg=10)
        kit.light(f"lamp{k}", "POINT", (x, y, zt - 0.2), 520.0, "#ffc77a", size=0.25)
    kit.light("flood0", "SPOT", (-2.2, -2.8, 0.25), 2600.0, "#ffd9a8", size=0.3, spot=46, blend=0.5)
    kit.light("flood1", "SPOT", (2.2, -2.8, 0.25), 2600.0, "#ffd9a8", size=0.3, spot=46, blend=0.5)
    kit.aim(kit.LIGHTS["flood0"]["obj"], (0.0, 0.0, 5.0))
    kit.aim(kit.LIGHTS["flood1"]["obj"], (0.0, 0.0, 5.0))
    kit.light("winL", "AREA", (-8.8, -6.0, 6.0), 700.0, "#5f86d4", size=7.0)
    kit.light("winR", "AREA", (8.8, -6.0, 6.0), 700.0, "#5f86d4", size=7.0)
    kit.aim(kit.LIGHTS["winL"]["obj"], (0, -6.0, 4.0))
    kit.aim(kit.LIGHTS["winR"]["obj"], (0, -6.0, 4.0))
    kit.light("winB", "AREA", (0.0, -12.0, 7.0), 260.0, "#6a90d8", size=9.0)
    kit.aim(kit.LIGHTS["winB"]["obj"], (0.0, 0.0, 5.0))
    # the creature's key (from below) and its blue rim, placed each frame
    kit.light("ckey", "SPOT", (0, 0, 0), 0.0, "#ffd0a0", size=0.2, spot=38, blend=0.6)
    kit.light("crim", "SPOT", (0, 0, 0), 0.0, "#7ea6ff", size=0.2, spot=38, blend=0.6)
    kit.light("cfill", "POINT", (0, 0, 0), 0.0, "#9fb4ff", size=0.3, shadow=False)
    kit.light("hall", "AREA", (0.0, -9.0, 5.5), 900.0, "#ffd9b0", size=10.0)
    kit.aim(kit.LIGHTS["hall"]["obj"], (0.0, 0.0, 4.5))
    kit.light("glow", "POINT", (0, -1.4, 9.0), 0.0, "#ffd7a0", size=0.4)

    # --- the Headstander
    spec = story["creature"]
    fdir = Path(bpy.app.tempdir or tempfile.gettempdir()) / "head-faces"
    fdir.mkdir(parents=True, exist_ok=True)
    c = rig.Character("head", spec, fdir)
    ctx["head"] = c
    # powdery, matte; the face glows a little so the eyes are the brightest thing on it
    for key, m in kit.MATS.items():
        if key.startswith("plastic " + LILAC.lower()) or key.startswith("plastic " + LILAC):
            m.node_tree.nodes["Principled BSDF"].inputs["Roughness"].default_value = 0.9
    hb = c.head_mat.node_tree
    pb = hb.nodes["Principled BSDF"]
    pb.inputs["Roughness"].default_value = 0.85
    em_in = pb.inputs.get("Emission Color")
    if em_in is not None:
        hb.links.new(c.face_tex.outputs["Color"], em_in)
        pb.inputs["Emission Strength"].default_value = 0.12
    black = kit.plastic("#141414", 0.6)
    kit.box("head.harness", (2.12, 1.12, 0.42), (0, 0, 0.32), black, c.torso, bevel=0.05)
    ctx["knot"] = kit.box("head.knot", (0.3, 0.3, 0.3), (-0.9, -0.62, 0.32), kit.plastic("#d4cae4", 0.9), c.torso, bevel=0.06)
    return ctx


def _dress(kit, ctx):
    """Harnesses and the chalk bag on the two climbers (made by bl_story before the first frame)."""
    if ctx["extras"]:
        return
    ctx["extras"] = True
    obs = bpy.data.objects
    spec = {"me": ("#cdb98e", True), "sam": ("#26344f", False)}
    for who, (hc, bag) in spec.items():
        tor = obs.get(f"{who}.torso")
        if tor is None:
            continue
        hm = kit.plastic(hc, 0.7)
        kit.box(f"{who}.harness", (2.1, 1.1, 0.42), (0, 0, 0.28), hm, tor, bevel=0.05)
        for sx in (-1, 1):
            leg = obs.get(f"{who}.leg{sx}")
            if leg is not None:
                kit.box(f"{who}.hloop{sx}", (1.04, 1.06, 0.3), (0, 0, -0.18), hm, leg, bevel=0.05)
        if who == "me":
            ctx["knots"] = [kit.box("me.knot", (0.62, 0.3, 0.5), (0.0, -0.66, 0.28), kit.plastic("#d4cae4", 0.9), tor, bevel=0.1),
                            kit.box("me.knot2", (0.4, 0.32, 0.34), (0.1, -0.7, 0.28), kit.plastic("#c2b6d6", 0.9), tor, bevel=0.08)]
        if who == "sam":
            for sx in (-1, 1):
                arm = obs.get(f"sam.arm{sx}")
                if arm is not None:
                    kit.box(f"sam.cuff{sx}", (1.02, 1.04, 0.4), (0, 0, -1.3), kit.plastic("#e6e6e0", 0.9), arm, bevel=0.05)
            arm = obs.get("sam.arm-1")
            ctx["tag2"] = kit.box("sam.tag", (0.66, 0.9, 0.08), (0.0, -0.7, -2.1), kit.plastic("#c8322a", 0.55), arm, bevel=0.02)
        if bag:
            kit.box(f"{who}.bag", (0.8, 0.55, 0.8), (0.8, 0.8, 0.28), kit.plastic("#f2f0ea", 0.85), tor, bevel=0.1)
            kit.box(f"{who}.bagt", (0.8, 0.5, 0.12), (0.8, 0.8, 0.74), kit.plastic("#d8d4c8", 0.85), tor, bevel=0.04)


# ------------------------------------------------------------------------------------------------ animate


def _shot(tl, t):
    return next((s for s in tl["shots"] if s["start"] <= t < s["end"]), tl["shots"][-1])


def waist(who, tl, t):
    s = acting.state(tl, who, t)
    return V((s["x"], s["y"], s["z"] + 0.78))


def place_head(kit, story, tl, t, ctx):
    c = ctx["head"]
    cu = _last(_cues(tl, "head"), t)
    if cu is None or cu.get("hidden"):
        c.pose(0, 0, -50, 0, hidden=True)
        ctx["head_state"] = None
        return
    p = POSES[cu["pose"]]
    x, y = p["pos"]
    c.pose(x, y, ROOF_Z - 0.0, math.radians(p["yaw"]), 0, (0, 0), (0, 0), 0, cu.get("pitch", 0.0), math.pi + math.radians(p["lean"]),
           0, "grin", 0.0, (0, 0), 0.0, False)
    ctx["head_state"] = (x, y, p["yaw"])


def animate(kit, story, tl, t, ctx):
    _dress(kit, ctx)
    shot = _shot(tl, t)
    look = story.get("looks", {}).get(shot["id"], {})
    place_head(kit, story, tl, t, ctx)

    # the red tag sways, a little always
    sw = _last(_cues(tl, "tag"), t)
    amp = (sw or {}).get("swing", 3.0)
    ctx["tag"].rotation_euler = (math.radians(amp * math.sin(t * 2.1)), math.radians(amp * 0.6 * math.sin(t * 1.3 + 1)), 0)

    for k in ctx.get("knots", []):
        k.hide_render = not (_last(_cues(tl, "knot"), t) or {}).get("on", False)
    if "tag2" in ctx:
        ctx["tag2"].hide_render = not (_last(_cues(tl, "tag2"), t) or {}).get("on", False)
    # the rope
    mode = (_last(_cues(tl, "rope"), t) or {}).get("mode", "me")
    me = acting.state(tl, "me", t)
    ring = V((ANCHOR_X, -0.2, ANCHOR_Z + 0.1))
    roof = V((ANCHOR_X, -0.14, ROOF_Z - 0.06))
    hip_me = V((me["x"] - 0.4, me["y"], me["z"] + 0.78))
    pts = []
    hs = ctx.get("head_state")
    if mode in ("me", "creature"):
        pts = [hip_me, ring, roof]
        if mode == "creature" and hs:
            pose = _last(_cues(tl, "head"), t)["pose"]
            hx, hy = POSES[pose]["pos"]
            pts += [V((hx - 0.15, hy + 0.1, ROOF_Z - 0.35)), V((hx - 0.2, hy, ROOF_Z - 0.95))]
    elif mode == "sam":
        sm = acting.state(tl, "sam", t)
        hip_sam = V((sm["x"], sm["y"] + 0.15, sm["z"] + 0.8))
        pts = [hip_sam, ring, hip_me]
    elif mode == "gathered":
        hx, hy = POSES["belay"]["pos"]
        pts = [ring, roof, V((hx - 0.15, hy + 0.1, ROOF_Z - 0.35)), V((hx - 0.2, hy, ROOF_Z - 0.95))]
    elif mode in ("end_up", "end_down"):
        cu = _last(_cues(tl, "rope"), t)
        u = _ss((t - cu["t"]) / cu.get("dur", 1.0))
        u = u if mode == "end_up" else 1 - u
        hx, hy = POSES["belay"]["pos"]
        end = V((ANCHOR_X - 0.6, -1.6, 0.4)).lerp(V((ANCHOR_X, -0.2, ANCHOR_Z)), u)
        pts = [end, ring, roof, V((hx - 0.15, hy + 0.1, ROOF_Z - 0.35)), V((hx - 0.2, hy, ROOF_Z - 0.95))]
        if u > 0.01 and mode == "end_up":
            pts = [end, ring, roof, V((hx - 0.15, hy + 0.1, ROOF_Z - 0.35)), V((hx - 0.2, hy, ROOF_Z - 0.95))]
    for k, ob in enumerate(ctx["rope"]):
        if k < len(pts) - 1:
            seg_between(ob, pts[k], pts[k + 1])
        else:
            ob.hide_render = True

    # the lilac-dusted rope end on the mat
    on = (_last(_cues(tl, "coil"), t) or {}).get("on", False)
    cpts = [(-1.4, -2.4), (-1.0, -2.1), (-0.5, -2.2), (-0.1, -2.0), (0.3, -2.3), (0.7, -2.1)]
    for k, ob in enumerate(ctx["coil"]):
        if on and k < len(cpts) - 1:
            seg_between(ob, (cpts[k][0], cpts[k][1], 0.33), (cpts[k + 1][0], cpts[k + 1][1], 0.33))
        else:
            ob.hide_render = True

    # lights
    lamps = level(_cues(tl, "lamps"), t, 1.0) * look.get("lamps", 1.0)
    flood = level(_cues(tl, "flood"), t, 1.0) * look.get("flood", 1.0)
    over = {k: lamps for k in kit.LIGHTS if k.startswith("lamp")}
    over["flood0"] = over["flood1"] = flood
    warm = level(_cues(tl, "warm"), t, 0.0)
    over["hall"] = lamps * (0.35 + 0.9 * warm)
    over["winL"] = over["winR"] = over["winB"] = look.get("fill", 1.0)
    for nm, key in (("ckey", "key"), ("crim", "rim"), ("cfill", "cfill")):
        L = kit.LIGHTS[nm]
        spec = look.get(key)
        if spec is None and hs and nm != "cfill":
            hx, hy, hyaw = hs
            head_c = V((hx, hy, ROOF_Z - 1.55))
            if nm == "ckey":
                spec = [[hx - 0.9, hy - 1.4, 6.9], [hx, hy, ROOF_Z - 1.6], 150.0]
            else:
                spec = [[hx + 1.2, hy + 0.8, ROOF_Z - 1.4], [hx, hy, ROOF_Z - 1.5], 110.0]
        if nm == "cfill" and hs and "cfill" in look:
            L["obj"].location = (hs[0], hs[1] - 0.8, ROOF_Z - 1.7)
            L["base"] = look["cfill"]
            continue
        if spec is None:
            L["base"] = 0.0
            continue
        L["obj"].location = tuple(spec[0])
        kit.aim(L["obj"], tuple(spec[1]))
        L["base"] = spec[2] * look.get(nm + "_g", 1.0)
    L = kit.LIGHTS["cfill"]
    if not (hs and "cfill" in look):
        L["base"] = 0.0
    G = kit.LIGHTS["glow"]
    if "glow" in look:
        G["obj"].location = tuple(look["glow"][0])
        G["base"] = look["glow"][1]
    else:
        G["base"] = 0.0

    return over
