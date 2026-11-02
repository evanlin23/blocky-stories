"""Swing Bridge (ep58). Creature-test build so far: the Reach, a rough rail, a cabin window. Rest of the set to come.

Coordinates: metres, z up, front of a character is -y at yaw 0. The bridge deck runs along +x.
"""
from __future__ import annotations

import math

import bpy
from mathutils import Vector as V

from blocky import rig

OCHRE, PEAT, TAN, CLAY = "#8a6424", "#2b2420", "#b39a78", "#c49a74"
REACH_SPEC = {
    "age": "adult", "skin": CLAY, "shirt": OCHRE, "pattern": "solid", "collar": PEAT, "pants": PEAT, "shoes": TAN,
    "sleeves": "none", "hair": "cap", "hair_c": "#3a2e26", "hat": "none", "body_width": 0.78,
    "face": {"eyes": "pin", "mouth": "flat", "brows": False, "ink": "#161012"},
}


def seg(kit, name, a, b, t, mat, up_t=None):
    a, b = V(a), V(b)
    d = b - a
    ob = kit.box(name, (t, up_t or t, d.length), tuple((a + b) / 2), mat, rot=d.to_track_quat("Z", "Y").to_euler(),
                 bevel=0.03)
    return ob


def long_arm(kit, name, shoulder, rail_pt, end, t=0.26, fold=1.5):
    """Shoulder -> drop to the rail's top chord -> straight along it to the hand. Sleeve blocks laid end to end,
    each join with a small fold of cloth (a slightly fatter, shorter collar), a cool rim strip on top, a clay hand."""
    sl = kit.plastic(PEAT, 0.9)
    rim = kit.emit("#6f8ca6", 0.55)
    skin = kit.plastic(CLAY, 0.5)
    seg(kit, f"{name}.drop", shoulder, rail_pt, t * 1.05, sl)
    a, e = V(rail_pt), V(end)
    d = (e - a)
    n = max(2, int(d.length // fold))
    pts = [a + d * (i / n) for i in range(n + 1)]
    for i in range(n):
        seg(kit, f"{name}.s{i}", pts[i], pts[i + 1] - d.normalized() * 0.02, t, sl)
        # rim: a thin lighter line along the top of the sleeve
        up = V((0, 0, 1))
        seg(kit, f"{name}.r{i}", pts[i] + up * (t / 2 + 0.004), pts[i + 1] + up * (t / 2 + 0.004), 0.035, rim, 0.01)
    for i in range(1, n):   # folds
        c = pts[i]
        kit.box(f"{name}.f{i}", (t * 1.12, t * 1.14, 0.1), tuple(c), sl, rot=d.to_track_quat("Z", "Y").to_euler(),
                bevel=0.05)
    # hand: ordinary size, flat, palm down, fingers together, no glow
    hand_c = e + d.normalized() * 0.1 - V((0, 0, t / 2 - 0.035))
    kit.box(f"{name}.hand", (0.09, 0.19, 0.075), tuple(hand_c), skin, rot=(0, 0, math.atan2(d.y, d.x)), bevel=0.02)
    kit.box(f"{name}.cuff", (t * 1.2, t * 1.2, 0.07), tuple(e - d.normalized() * 0.0), sl,
            rot=d.to_track_quat("Z", "Y").to_euler(), bevel=0.03)


def make_reach(kit, workdir, pos, yaw=0.0, lean=0.0, head_pitch=0.0, rail_pts=None, hands=None):
    """One Reach: a man, plus two straight sleeves from his shoulders to rail_pts (where each arm meets the rail)
    and on to hands (far ends)."""
    ch = rig.Character("reach", REACH_SPEC, workdir)
    ch.pose(pos[0], pos[1], pos[2], yaw, lean=lean, head_pitch=head_pitch, expr="neutral")
    for sx in (-1, 1):   # the rig's own arms are replaced by the long sleeves
        for ob in ch.P[f"arm{sx}"].children_recursive:
            ob.hide_render = True
    bpy.context.view_layer.update()
    sh = []
    for sx in (-1, 1):
        w = ch.torso.matrix_world @ V((sx * 1.5 * REACH_SPEC["body_width"], 0, 1.75))
        sh.append(w)
    for i, name in enumerate(("armL", "armR")):
        long_arm(kit, name, sh[i], rail_pts[i], hands[i])
    return ch


def bridge(kit, length, rail_y=0.0, rail_z=0.98, dirv=(1, 0), origin=(0, 0)):
    green = kit.plastic("#6f9a84", 0.6)
    dark = kit.plastic("#2f4a3e", 0.7)
    deck = kit.plastic("#5a4a3a", 0.9)
    d = V((*dirv, 0)).normalized()
    o = V((origin[0], origin[1], 0))
    ang = math.atan2(d.y, d.x)
    mid = o + d * (length / 2)
    kit.box("deck", (length, 1.6, 0.12), (mid.x, mid.y, -0.06), deck, rot=(0, 0, ang))
    n = int(length / 1.5)
    perp = V((-d.y, d.x, 0))
    for side in (0,):
        base = o + perp * rail_y
        kit.box("topchord", (length, 0.5, 0.07), (mid.x + perp.x * rail_y, mid.y + perp.y * rail_y, rail_z - 0.035), green,
                rot=(0, 0, ang))
        kit.box("lowchord", (length, 0.05, 0.05), (mid.x + perp.x * rail_y, mid.y + perp.y * rail_y, 0.3), green, rot=(0, 0, ang))
        for i in range(n + 1):
            p = base + d * (i * length / n)
            kit.box(f"post{i}", (0.07, 0.07, rail_z), (p.x, p.y, rail_z / 2), dark, rot=(0, 0, ang))
    return d
