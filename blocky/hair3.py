"""The v3 hair library (`look.style: "v3"`): bold block shapes that are each character's silhouette, so a cast
reads by hair alone at phone size. Pure data (a list of boxes per style), so it's tested without Blender and the
rig only places them.

Every box is (part, size, loc, rot, bevel, mat): size and loc in rig units on the v3 head's centre (x right as the
character sees it is -x, y back, z up; the face is at y = -D/2), rot in radians, mat "hair", "hair2" (a second
colour: a band, a tie, tips) or "skin". All of it is ours: plain boxes in our own arrangements, none modelled on any
game's catalogue hair.
"""

from __future__ import annotations

import math

from .faces_v3 import EYE_GAP, EYE_RX, EYE_RY, EYE_Y, HAIRLINE, HEAD3_D as D, HEAD3_H as H, HEAD3_W as W

TOP, FRONT, BACK = H / 2, -D / 2, D / 2
FRINGE_Z = TOP - HAIRLINE * H          # the lowest a fringe comes on the face (faces_v3 draws nothing above it)


def _b(part, size, loc, rot=(0.0, 0.0, 0.0), bevel=0.08, mat="hair"):
    return (part, tuple(size), tuple(loc), tuple(rot), bevel, mat)


def _cap(sides=0.55, back=0.8, th=0.24):
    """The base most styles sit on: a slab over the top, a plate down the back and short sides at the temples."""
    return [_b("cap", (W + 0.1, D + 0.1, th), (0, 0, TOP - th / 2 + 0.07), bevel=0.1),
            _b("back", (W + 0.1, 0.24, H * back), (0, BACK - 0.07, TOP - H * back / 2), bevel=0.08),
            _b("side-1", (0.2, D * 0.85, H * sides), (-(W / 2 + 0.02), 0.06, TOP - H * sides / 2), bevel=0.06),
            _b("side1", (0.2, D * 0.85, H * sides), (W / 2 + 0.02, 0.06, TOP - H * sides / 2), bevel=0.06)]


def _fringe(th=0.22, drop=None):
    drop = TOP - FRINGE_Z if drop is None else drop
    return [_b("fringe", (W + 0.08, th, drop + 0.05), (0, FRONT - th / 2 + 0.06, TOP - drop / 2 + 0.03), bevel=0.07)]


def quiff():          # a tall wave rolling forward off the forehead, out past the face
    return _cap(0.45) + [
        _b("q0", (W * 0.86, D * 0.7, 0.5), (0, 0.05, TOP + 0.22), rot=(-0.12, 0, 0), bevel=0.16),
        _b("q1", (W * 0.8, D * 0.62, 0.5), (0, -0.2, TOP + 0.6), rot=(-0.3, 0, 0), bevel=0.16),
        _b("q2", (W * 0.74, D * 0.5, 0.46), (0, -0.5, TOP + 0.92), rot=(-0.55, 0, 0), bevel=0.16),
        _b("q3", (W * 0.66, 0.6, 0.42), (0, FRONT - 0.05, TOP + 1.0), rot=(-1.1, 0, 0), bevel=0.14),
        _b("q4", (W * 0.56, 0.42, 0.36), (0, FRONT - 0.3, TOP + 0.78), rot=(-1.9, 0, 0), bevel=0.12)]


def bigbun():         # a bun bigger than a fist, high on the crown, with a band
    return _cap(0.5, 0.7) + _fringe(0.18, 0.16) + [
        _b("bun", (W * 0.74, W * 0.74, W * 0.6), (0, 0.15, TOP + W * 0.36), bevel=0.4),
        _b("bun45", (W * 0.74, W * 0.74, W * 0.5), (0, 0.15, TOP + W * 0.36), rot=(0, 0, 0.785), bevel=0.4),
        _b("buntop", (W * 0.5, W * 0.5, 0.3), (0, 0.15, TOP + W * 0.68), rot=(0, 0, 0.39), bevel=0.14),
        _b("band", (W * 0.5, W * 0.5, 0.2), (0, 0.15, TOP + 0.08), bevel=0.06, mat="hair2")]


def spikes():         # tall blades in a fan, the front ones raking forward
    out = _cap(0.5)
    for k in range(5):
        a = -0.95 + 1.9 * k / 4
        x = W * 0.36 * math.sin(a)
        h = 1.5 - 0.35 * abs(a)
        out.append(_b(f"spk{k}", (0.44, 0.5, h), (x, 0.05 + 0.2 * abs(a), TOP + h / 2 - 0.1),
                      rot=(-0.35, a * 0.6, 0), bevel=0.06))
        out.append(_b(f"spkt{k}", (0.3, 0.36, 0.32), (x + math.sin(a * 0.6) * h * 0.5, 0.05 + 0.2 * abs(a) - 0.17 * h, TOP + h * 0.95 - 0.1),
                      rot=(-0.35, a * 0.6, 0), bevel=0.05, mat="hair2"))
    out.append(_b("spkf", (0.7, 0.36, 0.9), (0.2, FRONT + 0.1, TOP + 0.2), rot=(-0.95, 0.25, 0), bevel=0.06))
    return out


def bob():            # a blunt helmet bob to the jaw with a ruler-straight fringe
    return [_b("shell", (W + 0.6, D * 0.85, H * 0.85), (0, 0.32, TOP - H * 0.4 + 0.2), bevel=0.25),
            _b("shelltop", (W + 0.6, D + 0.3, 0.6), (0, 0.05, TOP + 0.15), bevel=0.2),
            _b("bobside-1", (0.45, D * 0.8, H * 1.0), (-(W / 2 + 0.2), 0.12, TOP - H * 0.5), bevel=0.14),
            _b("bobside1", (0.45, D * 0.8, H * 1.0), (W / 2 + 0.2, 0.12, TOP - H * 0.5), bevel=0.14),
            _b("bobfringe", (W + 0.26, 0.26, 0.48), (0, FRONT - 0.04, TOP - 0.15), bevel=0.08)]


def buzz():           # a skin-tight buzz with long block sideburns
    return [_b("buzz", (W + 0.04, D + 0.04, 0.12), (0, 0, TOP + 0.0), bevel=0.05),
            _b("buzzback", (W + 0.04, 0.1, H * 0.6), (0, BACK + 0.0, TOP - H * 0.3), bevel=0.04),
            _b("burn-1", (0.14, 0.42, H * 0.62), (-(W / 2 + 0.03), FRONT + 0.6, TOP - H * 0.31), bevel=0.04),
            _b("burn1", (0.14, 0.42, H * 0.62), (W / 2 + 0.03, FRONT + 0.6, TOP - H * 0.31), bevel=0.04)]


def curls():          # a cloud of stacked cubes, wider than the shoulders
    out = [_b("curlcore", (W + 0.5, D + 0.5, 0.9), (0, 0.05, TOP + 0.1), bevel=0.25)]
    k = 0
    k_ = W / 1.6   # the cloud scales with the head, and stands out past it
    for row, (z, r, n) in enumerate(((TOP + 0.55, 0.75 * k_, 8), (TOP + 0.1, 1.18 * k_, 12), (TOP - 0.42, 1.22 * k_, 12), (TOP - 0.95, 1.1 * k_, 10))):
        for i in range(n):
            a = 2 * math.pi * (i + 0.5 * row) / n
            y = 0.1 + r * 0.85 * math.cos(a)
            if y < FRONT + 0.25 and z < TOP + 0.2:
                continue   # leave the face open
            out.append(_b(f"curl{k}", (0.62, 0.62, 0.6), (r * math.sin(a), y, z), rot=(0.2 * i, 0.3 * row, a), bevel=0.14))
            k += 1
    return out


def braids():         # two thick braids of stacked cubes hanging forward over the shoulders, tied off in a colour
    out = _cap(0.6) + _fringe(0.2, 0.18)
    for sx in (-1, 1):
        for k in range(6):
            sz = 0.62 - 0.04 * k
            out.append(_b(f"braid{sx}{k}", (sz, sz, 0.5), (sx * (W / 2 + 0.05), FRONT + 0.55, TOP - 0.75 - 0.46 * k),
                          rot=(0, 0, 0.785), bevel=0.14))
        out.append(_b(f"btie{sx}", (0.5, 0.5, 0.2), (sx * (W / 2 + 0.05), FRONT + 0.55, TOP - 0.75 - 0.46 * 5.75), bevel=0.05, mat="hair2"))
    return out


def mohawk():         # a tall, wide fin of blocks front to back over a buzz, the front block in a second colour
    out = [_b("mbuzz", (W + 0.03, D + 0.03, 0.1), (0, 0, TOP), bevel=0.04)]
    for k in range(5):
        y = FRONT + 0.25 + k * (D - 0.4) / 4
        h = 1.5 - 0.16 * k
        out.append(_b(f"fin{k}", (0.62, 0.5, h), (0, y, TOP + h / 2 - 0.05), rot=(-0.3, 0, 0), bevel=0.08, mat="hair2" if k == 0 else "hair"))
    return out


def flattop():        # a tall flat-topped block, squared off like a hedge
    return [_b("flat", (W + 0.08, D + 0.06, 1.4), (0, 0.02, TOP + 0.62), bevel=0.06),
            _b("flatback", (W + 0.06, 0.12, H * 0.45), (0, BACK, TOP - H * 0.22), bevel=0.04)]


def mullet():         # short on top, a long wide slab down the back past the shoulders, flicked out at the end
    return _cap(0.45, 0.8) + _fringe(0.2, 0.2) + [
        _b("mull", (W + 0.2, 0.5, H * 1.05), (0, BACK + 0.08, TOP - H * 0.85), bevel=0.12),
        _b("mulls-1", (0.3, D * 0.5, H * 0.9), (-(W / 2 + 0.1), D * 0.22, TOP - H * 0.7), bevel=0.08),
        _b("mulls1", (0.3, D * 0.5, H * 0.9), (W / 2 + 0.1, D * 0.22, TOP - H * 0.7), bevel=0.08),
        _b("mulltip", (W + 0.4, 0.55, 0.36), (0, BACK + 0.25, TOP - H * 1.4), rot=(0.4, 0, 0), bevel=0.1)]


def puffs():          # two round puffs high on the head
    out = _cap(0.5) + _fringe(0.18, 0.15)
    for sx in (-1, 1):
        out.append(_b(f"puff{sx}", (0.9, 0.85, 0.85), (sx * 0.72, 0.1, TOP + 0.38), bevel=0.3))
        out.append(_b(f"ptie{sx}", (0.5, 0.5, 0.14), (sx * 0.62, 0.1, TOP + 0.02), rot=(0, sx * -0.3, 0), bevel=0.04, mat="hair2"))
    return out


def swoop():          # a big wall swept hard to one side, overhanging the ear
    return _cap(0.5) + [
        _b("sw0", (W + 0.5, D * 0.9, 0.42), (-0.25, 0.0, TOP + 0.2), rot=(0, -0.22, 0), bevel=0.14),
        _b("sw1", (0.5, D * 0.8, 0.8), (-(W / 2 + 0.25), 0.05, TOP - 0.15), rot=(0, -0.2, 0), bevel=0.12),
        _b("sw2", (W * 0.7, 0.3, 0.32), (0.2, FRONT + 0.0, TOP - 0.05), rot=(0, 0.25, 0), bevel=0.08)]


def topknot():        # shaved sides, a big knot high on the crown, tied off in a colour
    return [_b("tkbuzz", (W + 0.02, D + 0.02, 0.1), (0, 0, TOP), bevel=0.04),
            _b("tktop", (W * 0.6, D * 0.8, 0.3), (0, 0.05, TOP + 0.15), bevel=0.08),
            _b("tie", (0.55, 0.55, 0.22), (0, 0.15, TOP + 0.4), bevel=0.05, mat="hair2"),
            _b("knot", (1.0, 0.95, 0.85), (0, 0.15, TOP + 0.9), rot=(0.25, 0, 0.5), bevel=0.3)]


def curtains():       # a middle part, two slabs framing the face down to the shoulders
    out = _cap(0.6, 1.2)
    for sx in (-1, 1):
        out.append(_b(f"cur{sx}", (W * 0.52, 0.28, 0.4), (sx * W * 0.27, FRONT + 0.02, TOP - 0.05), rot=(0, sx * 0.3, 0), bevel=0.08))
        out.append(_b(f"curs{sx}", (0.55, D * 0.85, H * 1.2), (sx * (W / 2 + 0.22), 0.15, TOP - H * 0.6), bevel=0.14))
    return out


def shag():           # messy offset tiers
    out = []
    for k, (z, w, d_, off) in enumerate(((TOP + 0.3, W * 0.7, D * 0.7, 0.12), (TOP + 0.08, W + 0.25, D + 0.2, -0.1),
                                         (TOP - 0.25, W + 0.4, D + 0.1, 0.1), (TOP - 0.6, W + 0.3, D * 0.6, 0.0))):
        out.append(_b(f"tier{k}", (w, d_, 0.38), (off, 0.15 if k == 3 else 0.05 + (0.35 if k == 3 else 0), z), rot=(0, 0, 0.12 * (-1) ** k), bevel=0.12))
    out.append(_b("shagf", (W * 0.9, 0.3, 0.36), (0.1, FRONT - 0.02, TOP - 0.12), rot=(0, 0.12, 0), bevel=0.08))
    return out


def bald():           # nothing on top, the head's own shine (for a mustache or a hat to carry)
    return []


STYLES = {f.__name__: f for f in (quiff, bigbun, spikes, bob, buzz, curls, braids, mohawk, flattop, mullet, puffs,
                                  swoop, topknot, curtains, shag, bald)}


# loud features: extra blocks a side character can carry on top of any hair
def mustache():       # a giant walrus mustache: one wide block bar with heavy ends drooping past the mouth corners
    z = TOP - 0.7 * H
    out = [_b("stache", (W * 0.72, 0.32, 0.3), (0, FRONT - 0.14, z), bevel=0.14)]
    for sx in (-1, 1):
        out.append(_b(f"stache{sx}", (W * 0.2, 0.3, 0.5), (sx * W * 0.38, FRONT - 0.12, z - 0.16), rot=(0, sx * 0.15, 0), bevel=0.12))
    return out


def beard():          # a squared block beard under the mouth
    return [_b("beard", (W * 0.9, 0.7, 0.8), (0, FRONT + 0.2, -TOP - 0.2), bevel=0.2),
            _b("beardl", (0.24, D * 0.5, 0.7), (-(W / 2 - 0.05), FRONT + 0.4, -TOP + 0.15), bevel=0.06),
            _b("beardr", (0.24, D * 0.5, 0.7), ((W / 2 - 0.05), FRONT + 0.4, -TOP + 0.15), bevel=0.06)]


def glasses():        # big square frames standing off the face, round the drawn eyes
    z = TOP - EYE_Y * H
    hw, hh = EYE_RX * W * 0.95 + 0.04, EYE_RY * H + 0.08      # half the frame's width and height
    out = []
    for sx in (-1, 1):
        cx = sx * EYE_GAP * W / 2
        for part, size, dx, dz in (("t", (2 * hw + 0.1, 0.08, 0.1), 0, hh), ("b", (2 * hw + 0.1, 0.08, 0.1), 0, -hh),
                                   ("o", (0.1, 0.08, 2 * hh), sx * hw, 0), ("i", (0.1, 0.08, 2 * hh), -sx * hw, 0)):
            out.append(_b(f"gl{part}{sx}", size, (cx + dx, FRONT - 0.08, z + dz), bevel=0.02, mat="hair2"))
        out.append(_b(f"arm{sx}", (0.08, D * 0.6, 0.08), (sx * (W / 2 + 0.04), FRONT + D * 0.3, z + hh * 0.8), bevel=0.02, mat="hair2"))
    bw = 2 * (EYE_GAP * W / 2 - hw) + 0.1
    out.append(_b("bridge", (max(0.12, bw), 0.08, 0.08), (0, FRONT - 0.08, z + hh * 0.3), bevel=0.02, mat="hair2"))
    return out


FEATURES = {f.__name__: f for f in (mustache, beard, glasses)}


def parts(style: str, features=()) -> list:
    if style not in STYLES:
        raise ValueError(f"unknown v3 hair {style!r}: one of {', '.join(STYLES)}")
    out = list(STYLES[style]())
    for f in features:
        if f not in FEATURES:
            raise ValueError(f"unknown v3 feature {f!r}: one of {', '.join(FEATURES)}")
        out += FEATURES[f]()
    return out
