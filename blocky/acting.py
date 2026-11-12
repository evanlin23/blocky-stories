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
# `motion.overlap` (opt-in, the polish pack's "overlap"): per channel (lag s, blend stretch). The head turns first,
# the body on the key, the arms after it and a little slower, so a move reads as a body rather than one block.
OVERLAP = {"head": (-0.05, 1.0), "look": (-0.05, 1.0), "yaw": (0.0, 1.0), "lean": (0.03, 1.2), "arms": (0.07, 1.3),
           "side": (0.09, 1.35)}


def _ease(u):
    u = min(1.0, max(0.0, u))
    return u * u * (3 - 2 * u)


def _keys_with(keys, attr):
    return [k for k in keys if attr in k]


def _first(ks):
    """The key that holds from the start until the second key time: the LAST of the keys stacked at the first key
    time. A story often stacks keys at 0 (a generator's "hide everyone", then the shot's own place), and taking
    the first of them posed frame 0 from the wrong key while frame 1 had the right one (ep116: Grandpa missing on
    frame 0 of S01, a pop on every loop wrap)."""
    i = 0
    while i + 1 < len(ks) and ks[i + 1]["t"] <= ks[0]["t"] + 1e-9:
        i += 1
    return ks[i]


def _held(keys, attr, t, default, lag=0.0, stretch=1.0, cap=None, short=False):
    """`attr` at t: held from each key until the next, eased into it over that key's `blend`.
    The motion options (all off unless the story asks): `lag` shifts this channel's blends later (or earlier, when
    negative) so a head leads and arms follow; `stretch` lengthens the blend; `cap` (degrees per second) lengthens a
    blend until the eased move's peak speed is at most cap (unless the keys are too close for it: their timing wins);
    `short` turns a number in degrees the short way round (180 to -90 is 90 degrees, not 270). None of them touch a
    key with blend 0 (a re-staging on a cut must land on its frame)."""
    ks = _keys_with(keys, attr)
    if not ks:
        return default
    if t <= ks[0]["t"]:
        return _first(ks)[attr]
    for a, b in zip(ks, ks[1:]):
        bl = b.get("blend", BLEND)
        sh = lag if bl > 0 else 0.0
        if t < b["t"] + sh:
            va, vb = a[attr], b[attr]
            if short and not isinstance(va, (list, tuple)):
                vb = va + (vb - va + 180.0) % 360.0 - 180.0
            if bl > 0:
                bl *= stretch
                if cap:
                    big = max(abs(y - x) for x, y in zip(va, vb)) if isinstance(va, (list, tuple)) else abs(vb - va)
                    bl = max(bl, 1.5 * big / cap)   # smoothstep peaks at 1.5x its mean speed
                if sh or stretch != 1.0 or cap:   # (off, the old timing stays exactly as it was)
                    bl = min(bl, max(1e-6, b["t"] + sh - a["t"]))   # never starts before the key it leaves
            u = _ease((t - (b["t"] + sh - bl)) / bl) if bl > 0 else float(t >= b["t"])
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


EASE_S = 0.25   # with the polish pack's eased walks: seconds to get up to speed and to slow to a stop


def _vel(a, b):
    pa, pb = _pos3(a["pos"]), _pos3(b["pos"])
    d = b["t"] - a["t"]
    return ((pb[0] - pa[0]) / d, (pb[1] - pa[1]) / d) if d > 1e-6 else (0.0, 0.0)


def _ends(ks, i):
    """Seconds of ease at the start and end of walk segment i: none where it carries on from or into a segment
    moving about the same way (a path through several keys stays one walk)."""
    a, b = ks[i], ks[i + 1]
    v = _vel(a, b)
    sp = math.hypot(*v)
    if sp < 0.05:
        return 0.0, 0.0
    dur = b["t"] - a["t"]
    out = []
    for j in (i - 1, i + 1):
        w = _vel(ks[j], ks[j + 1]) if 0 <= j < len(ks) - 1 else (0.0, 0.0)
        cont = math.hypot(v[0] - w[0], v[1] - w[1]) < 0.5
        # a run takes longer to get up to speed: at least EASE_S, or speed / 4 m/s2 (a sprint start)
        out.append(0.0 if cont else min(max(EASE_S, sp / 4.0), dur / 3))
    return out[0], out[1]


def _frac(ks, i, t, ease):
    """How far along segment i (0..1) at t: a steady pace, or with `ease` a trapezoid of speed (it speeds up over
    the start ease and slows over the end one, and takes the same time)."""
    a, b = ks[i], ks[i + 1]
    dur = max(1e-6, b["t"] - a["t"])
    x = min(dur, max(0.0, t - a["t"]))
    if not ease:
        return x / dur
    ea, eb = _ends(ks, i)
    if not ea and not eb:
        return x / dur
    v = 1.0 / (dur - ea / 2 - eb / 2)
    if ea and x < ea:
        return v * x * x / (2 * ea)
    if eb and x > dur - eb:
        return 1.0 - v * (dur - x) ** 2 / (2 * eb)
    return v * (x - ea / 2)


def position(keys, t, ease=False):
    """(x, y, z, segment) where segment is (key a, key b) while between two pos keys, else None."""
    ks = _keys_with(keys, "pos")
    if not ks:
        return (0.0, 0.0, 0.0, None)
    if t <= ks[0]["t"]:
        return (*_pos3(_first(ks)["pos"]), None)
    for i, (a, b) in enumerate(zip(ks, ks[1:])):
        if t < b["t"]:
            u = _frac(ks, i, t, ease)
            pa, pb = _pos3(a["pos"]), _pos3(b["pos"])
            return (*(x + (y - x) * u for x, y in zip(pa, pb)), (a, b))
    return (*_pos3(ks[-1]["pos"]), None)


def distance_walked(keys, t, ease=False):
    """Metres walked by time t (only the flat distance counts)."""
    ks = _keys_with(keys, "pos")
    d = 0.0
    for i, (a, b) in enumerate(zip(ks, ks[1:])):
        if t <= a["t"]:
            break
        pa, pb = _pos3(a["pos"]), _pos3(b["pos"])
        seg = math.hypot(pb[0] - pa[0], pb[1] - pa[1])
        d += seg * _frac(ks, i, t, ease)
    return d


def idle(t, seed, scale=1.0):
    """The polish pack's idle life for a standing character: breathing, a slow weight shift and a drifting head,
    from slow sines at periods that never line up (so it never loops visibly). (bob m, lean rad, yaw rad,
    head yaw rad, head pitch rad)."""
    ph = _hash(seed + 31) * 6.283
    s = lambda period, k=0.0: math.sin(2 * math.pi * t / period + ph + k)
    bob = 0.006 * scale * s(3.7)
    lean = math.radians(0.9) * scale * (s(5.3, 1.0) + 0.5 * s(2.9, 2.2))
    yaw = math.radians(2.0) * scale * (s(7.1, 0.4) + 0.4 * s(3.3, 1.7))
    head_yaw = math.radians(5.0) * scale * (s(4.7, 2.0) + 0.6 * s(2.3, 0.3))
    head_pitch = math.radians(2.5) * scale * (s(6.1, 1.3) + 0.5 * s(1.9, 2.9))
    return bob, lean, yaw, head_yaw, head_pitch


def _wrap(a):
    """An angle difference in radians, the short way round (-pi..pi)."""
    return (a + math.pi) % (2 * math.pi) - math.pi


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
    mo = tl.get("motion") or {}
    ease = bool(mo.get("ease"))
    x, y, z, seg = position(keys, t, ease)
    legs, bob, travel_yaw, speed, run = 0.0, 0.0, None, 0.0, False
    if seg:
        a, b = seg
        pa, pb = _pos3(a["pos"]), _pos3(b["pos"])
        dx, dy = pb[0] - pa[0], pb[1] - pa[1]
        dist = math.hypot(dx, dy)
        speed = dist / max(1e-6, b["t"] - a["t"])
        if speed > 0.05:
            run = a.get("run", speed > 2.6)
            ph = distance_walked(keys, t, ease) / STRIDE * math.pi
            amp = min(0.95 if run else 0.65, 0.25 + speed * 0.3)
            # ease the swing in and out at the ends of the walk
            amp *= _ease((t - a["t"]) / 0.15) * _ease((b["t"] - t) / 0.15)
            legs = amp * math.sin(ph)
            bob = abs(math.sin(ph)) * (0.06 if run else 0.025)
            travel_yaw = math.atan2(dx, -dy)
    ov = mo.get("overlap")
    cap = float(mo.get("turn_cap") or 0) or None   # degrees per second, on body and head turns

    def held(attr, default):
        lag, k = OVERLAP.get(attr, (0.0, 1.0)) if ov else (0.0, 1.0)
        return _held(keys, attr, t, default, lag, k, cap if attr in ("yaw", "head") else None, bool(cap) and attr == "yaw")

    yk = _keys_with(keys, "yaw")
    keyed = math.radians(held("yaw", 0.0)) if yk else None
    if travel_yaw is not None and not (seg and "yaw" in seg[0] and seg[0].get("keep_yaw")):
        yaw = travel_yaw
        if cap and keyed is not None:
            # a walk turns toward where it goes, and back to its keyed facing when it stops, at the capped speed
            # (uncapped, the body snapped to the walk's direction on its first frame)
            a, b = seg
            ramp = [max(0.12, 1.5 * math.degrees(abs(_wrap(travel_yaw - math.radians(
                _held(keys, "yaw", te, 0.0, *(OVERLAP["yaw"] if ov else (0.0, 1.0)), cap, True))))) / cap)
                for te in (a["t"], b["t"])]   # fixed per walk, from the gap at its two ends
            w = _ease((t - a["t"]) / ramp[0]) * _ease((b["t"] - t) / ramp[1])
            yaw = keyed + _wrap(travel_yaw - keyed) * w
    else:
        yaw = keyed if yk else (travel_yaw or 0.0)
    arms = [math.radians(v) for v in held("arms", [0, 0])]
    if run:
        arms = [max(a, 0.35) for a in arms]
    side = [math.radians(v) for v in held("side", [0, 0])]
    head = [math.radians(v) for v in held("head", [0, 0])]
    ty, tp = tremble(keys, t)
    head = [head[0] + ty, head[1] + tp]
    lean = math.radians(held("lean", 0.0)) + (0.12 if run else 0.0)
    out = {"x": x, "y": y, "z": z, "yaw": yaw, "legs": legs, "arms": tuple(arms), "arms_side": tuple(side),
            "head_yaw": head[0], "head_pitch": head[1], "lean": lean, "bob": bob,
            "expr": _switch(keys, "expr", t, "neutral"), "look": tuple(held("look", [0, 0])),
            "blink": blink(t, seed) if _switch(keys, "blink", t, True) else 0.0,
            "mouth": max(mouth(tl["talk"].get(who, []), t), mouth_track(keys, t)),
            "hidden": bool(_switch(keys, "hidden", t, False)), "speed": speed}
    if mo.get("idle") and abs(legs) < 1e-6 and not out["hidden"]:   # the polish pack: nobody stands like a statue
        sc = float(mo.get("idle_scale", 1.0))
        if any(a <= t < b for a, b in mo.get("calm", [])):   # a reveal shot: nearly still, so the face reads
            sc *= 0.2
        ib, il, iy, ihy, ihp = idle(t, sum(map(ord, who)) + seed, sc)
        out.update(bob=out["bob"] + ib, lean=out["lean"] + il, yaw=out["yaw"] + iy,
                   head_yaw=out["head_yaw"] + ihy, head_pitch=out["head_pitch"] + ihp)
    return out


def footsteps(tl, who):
    """Times (and places) each foot lands: every half stride while walking."""
    keys = tl["acting"].get(who, [])
    ease = bool((tl.get("motion") or {}).get("ease"))
    out = []
    ks = _keys_with(keys, "pos")
    for i, (a, b) in enumerate(zip(ks, ks[1:])):
        pa, pb = _pos3(a["pos"]), _pos3(b["pos"])
        dist = math.hypot(pb[0] - pa[0], pb[1] - pa[1])
        dur = b["t"] - a["t"]
        if dist < 0.05 or dur <= 0:
            continue
        d0 = distance_walked(keys, a["t"], ease)
        k = math.ceil(d0 / STRIDE + 1e-6)
        while (k * STRIDE - d0) < dist:
            u = (k * STRIDE - d0) / dist
            tu = a["t"] + u * dur
            if ease:   # the foot lands where the eased walk has covered that distance (bisection on the profile)
                lo, hi = a["t"], b["t"]
                for _ in range(40):
                    mid = (lo + hi) / 2
                    lo, hi = (mid, hi) if _frac(ks, i, mid, True) < u else (lo, mid)
                tu = (lo + hi) / 2
            out.append({"t": round(tu, 3), "x": pa[0] + (pb[0] - pa[0]) * u,
                        "y": pa[1] + (pb[1] - pa[1]) * u, "run": a.get("run", dist / dur > 2.6)})
            k += 1
    return out
