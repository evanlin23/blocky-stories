"""What every character is doing at time t, from the keyed beats in a story's `acting` (pure Python: Blender poses
from it, and the sound puts a footstep on every step it takes).

A key: {"at": <time ref>, "pos": [x, y] or [x, y, z] metres, "yaw": degrees (0 faces -y), "arms": [left, right]
degrees raised forward, "side": [left, right] degrees out, "head": [yaw, pitch] degrees, "lean": degrees,
"expr": one of faces.EXPRESSIONS, "look": [x, y] in -1..1, "hidden": bool, "blend": seconds, "run": bool,
"blink": false (eyes held open from here until a key says true), "tremble": degrees (a small fast head shake,
held and eased like the other numbers)}.

A mouth key moves a mouth whether or not the character is speaking: {"from": <time ref>, "to": <time ref>,
"mouth": [open at from, open at to]} (0..1, eased between them, shut outside every such key). It combines with
the talking flaps by taking the larger, so a line spoken over it still flaps. With "flap": true it flaps open and
shut about every 0.11 s instead (a character whose words the narrator reports: their mouth moves under them).

- `pos` is where the character is at that moment, so between two keys it walks there at a steady pace, and the
  legs swing with the distance covered. Two keys with the same pos make it stand still.
- While walking with no `yaw` of its own, a character faces where it's going.
- Every other number holds until the next key that sets it, then eases to it over `blend` (default 0.25 s).
- `expr` and `hidden` switch at their key.
"""

from __future__ import annotations

import math

STRIDE = 0.62   # metres per step
FLAP = 0.11     # seconds per mouth flap, for a mouth key with "flap": true
BLEND = 0.25


def _ease(u):
    u = min(1.0, max(0.0, u))
    return u * u * (3 - 2 * u)


def _keys_with(keys, attr):
    return [k for k in keys if attr in k]


def _held(keys, attr, t, default):
    ks = _keys_with(keys, attr)
    if not ks:
        return default
    if t <= ks[0]["t"]:
        return ks[0][attr]
    for a, b in zip(ks, ks[1:]):
        if t < b["t"]:
            bl = b.get("blend", BLEND)
            u = _ease((t - (b["t"] - bl)) / bl) if bl > 0 else float(t >= b["t"])
            va, vb = a[attr], b[attr]
            if isinstance(va, (list, tuple)):
                return [x + (y - x) * u for x, y in zip(va, vb)]
            return va + (vb - va) * u
    return ks[-1][attr]


def _switch(keys, attr, t, default):
    v = default
    for k in keys:
        if attr in k and k["t"] <= t + 1e-9:
            v = k[attr]
    return v


def _pos3(p):
    return (p[0], p[1], p[2] if len(p) > 2 else 0.0)


def position(keys, t):
    """(x, y, z, segment) where segment is (key a, key b) while between two pos keys, else None."""
    ks = _keys_with(keys, "pos")
    if not ks:
        return (0.0, 0.0, 0.0, None)
    if t <= ks[0]["t"]:
        return (*_pos3(ks[0]["pos"]), None)
    for a, b in zip(ks, ks[1:]):
        if t < b["t"]:
            u = (t - a["t"]) / max(1e-6, b["t"] - a["t"])
            pa, pb = _pos3(a["pos"]), _pos3(b["pos"])
            return (*(x + (y - x) * u for x, y in zip(pa, pb)), (a, b))
    return (*_pos3(ks[-1]["pos"]), None)


def distance_walked(keys, t):
    """Metres walked by time t (only the flat distance counts)."""
    ks = _keys_with(keys, "pos")
    d = 0.0
    for a, b in zip(ks, ks[1:]):
        if t <= a["t"]:
            break
        pa, pb = _pos3(a["pos"]), _pos3(b["pos"])
        seg = math.hypot(pb[0] - pa[0], pb[1] - pa[1])
        u = min(1.0, (t - a["t"]) / max(1e-6, b["t"] - a["t"]))
        d += seg * u
    return d


def _hash(x):
    x = (int(x) * 2654435761) & 0xFFFFFFFF
    return ((x >> 7) % 1000) / 1000


def blink(t, seed):
    period = 2.6 + 1.7 * _hash(seed)
    ph = (t + _hash(seed + 11) * period) % period
    return 1.0 if ph < 0.11 else 0.0


def mouth(flaps, t):
    for a, d in flaps:
        if a <= t < a + d:
            return math.sin(math.pi * (t - a) / d)
    return 0.0


def mouth_track(keys, t):
    """The manual mouth: the opening from the "mouth" keys that span t (the largest, if two overlap), else 0."""
    out = 0.0
    for k in keys:
        if "mouth" not in k or "t0" not in k:
            continue
        a, b = k["t0"], k["t1"]
        if a <= t < b:
            m0, m1 = k["mouth"]
            m = m0 + (m1 - m0) * _ease((t - a) / max(1e-6, b - a))
            if k.get("flap"):   # talking under someone else's voice: one flap about every 0.11 s
                m *= abs(math.sin(math.pi * (t - a) / FLAP))
            out = max(out, m)
    return out


def tremble(keys, t):
    """(yaw, pitch) radians of the head tremble at t: two fast sines, so it never settles into a nod."""
    amp = _held(keys, "tremble", t, 0.0)
    if not amp:
        return 0.0, 0.0
    a = math.radians(amp)
    return (a * math.sin(2 * math.pi * 9.3 * t) * 0.8 + a * 0.4 * math.sin(2 * math.pi * 13.7 * t + 1.1),
            a * 0.6 * math.sin(2 * math.pi * 7.1 * t + 2.3))


def state(tl, who, t, seed=0):
    keys = tl["acting"].get(who, [])
    x, y, z, seg = position(keys, t)
    legs, bob, travel_yaw, speed, run = 0.0, 0.0, None, 0.0, False
    if seg:
        a, b = seg
        pa, pb = _pos3(a["pos"]), _pos3(b["pos"])
        dx, dy = pb[0] - pa[0], pb[1] - pa[1]
        dist = math.hypot(dx, dy)
        speed = dist / max(1e-6, b["t"] - a["t"])
        if speed > 0.05:
            run = a.get("run", speed > 2.6)
            ph = distance_walked(keys, t) / STRIDE * math.pi
            amp = min(0.95 if run else 0.65, 0.25 + speed * 0.3)
            # ease the swing in and out at the ends of the walk
            amp *= _ease((t - a["t"]) / 0.15) * _ease((b["t"] - t) / 0.15)
            legs = amp * math.sin(ph)
            bob = abs(math.sin(ph)) * (0.06 if run else 0.025)
            travel_yaw = math.atan2(dx, -dy)
    yk = _keys_with(keys, "yaw")
    if travel_yaw is not None and not (seg and "yaw" in seg[0] and seg[0].get("keep_yaw")):
        yaw = travel_yaw
    else:
        yaw = math.radians(_held(keys, "yaw", t, 0.0)) if yk else (travel_yaw or 0.0)
    arms = [math.radians(v) for v in _held(keys, "arms", t, [0, 0])]
    if run:
        arms = [max(a, 0.35) for a in arms]
    side = [math.radians(v) for v in _held(keys, "side", t, [0, 0])]
    head = [math.radians(v) for v in _held(keys, "head", t, [0, 0])]
    ty, tp = tremble(keys, t)
    head = [head[0] + ty, head[1] + tp]
    lean = math.radians(_held(keys, "lean", t, 0.0)) + (0.12 if run else 0.0)
    return {"x": x, "y": y, "z": z, "yaw": yaw, "legs": legs, "arms": tuple(arms), "arms_side": tuple(side),
            "head_yaw": head[0], "head_pitch": head[1], "lean": lean, "bob": bob,
            "expr": _switch(keys, "expr", t, "neutral"), "look": tuple(_held(keys, "look", t, [0, 0])),
            "blink": blink(t, seed) if _switch(keys, "blink", t, True) else 0.0,
            "mouth": max(mouth(tl["talk"].get(who, []), t), mouth_track(keys, t)),
            "hidden": bool(_switch(keys, "hidden", t, False)), "speed": speed}


def footsteps(tl, who):
    """Times (and places) each foot lands: every half stride while walking."""
    keys = tl["acting"].get(who, [])
    out = []
    ks = _keys_with(keys, "pos")
    for a, b in zip(ks, ks[1:]):
        pa, pb = _pos3(a["pos"]), _pos3(b["pos"])
        dist = math.hypot(pb[0] - pa[0], pb[1] - pa[1])
        dur = b["t"] - a["t"]
        if dist < 0.05 or dur <= 0:
            continue
        d0 = distance_walked(keys, a["t"])
        k = math.ceil(d0 / STRIDE + 1e-6)
        while (k * STRIDE - d0) < dist:
            u = (k * STRIDE - d0) / dist
            out.append({"t": round(a["t"] + u * dur, 3), "x": pa[0] + (pb[0] - pa[0]) * u,
                        "y": pa[1] + (pb[1] - pa[1]) * u, "run": a.get("run", dist / dur > 2.6)})
            k += 1
    return out
