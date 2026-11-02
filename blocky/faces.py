"""Our own drawn faces for the blocky characters, as flat textures (PIL only, so it runs in the repo's Python,
the tests and Blender's).

The style is the owner's reference (note 18): big round white eyes with dark pupils, thin brows, a small
mouth that changes with the mood, tears when someone cries. Every face is drawn here from shapes. None is
traced from or modelled on a game's catalogue face, and `check_original` refuses the one combination that
would read as the classic default (two plain black ovals over a curved smile).

The texture wraps the whole head: u runs once around it (the face's centre at u = 0.5, which the rig turns to
the front) and v runs bottom to top. Everything outside the face is skin.
"""

from __future__ import annotations

import math
from functools import lru_cache

from PIL import Image, ImageDraw, ImageFilter

# the head the texture wraps (rig.py uses the same numbers): radius and height in rig units, so a texture pixel
# is square on the surface and a circle drawn here is a circle on the head
HEAD_R, HEAD_H = 0.62, 1.2
TEX_W = 2048
TEX_H = int(round(TEX_W * HEAD_H / (2 * math.pi * HEAD_R)))
# the face's box in the texture: about +-50 degrees around the head and the middle 70% of its height
FX0, FX1 = int(TEX_W * (0.5 - 50 / 360)), int(TEX_W * (0.5 + 50 / 360))
FY0, FY1 = int(TEX_H * 0.08), int(TEX_H * 0.92)

EXPRESSIONS = ("neutral", "worried", "scared", "crying", "angry", "smirk", "blank", "wide", "shut", "grin",
               "terrified", "squeeze", "soft", "asleep", "warm")
# warm: eyes open and a touch narrowed, brows level and relaxed, a wide closed smile with no teeth. Opt-in.
# terrified: the widest eyes with pin pupils, brows high and pulled up in the middle, the wavy worried mouth.
# soft: eyes gently closed (the content up-arcs), relaxed brows and a small closed smile: touched, not scared.
# squeeze: eyes screwed shut (short arcs sagging down, not the content up-arcs of "shut"), brows pinched low.
# asleep: lids closed in flat lines that droop a little at the outer ends (asleep, not content: "shut" and "soft"
# use up-arcs, which read as smiling eyes), brows level and low, a short slack mouth. Opt-in: no other face changes.
EYES = ("round", "classic", "dot", "tired", "lashes", "button", "hollow", "none", "mirror")
# mirror (ep14's copy): a "round" eye's own outline and size, filled to the edge with near-black. No white, no pupil and
# no glint, but the brows and the mouth stay, so the face still makes every expression. A face's "mouth_inside" (a hex
# colour) draws an open mouth as a hole of that colour to its edge, with no lip line, instead of the usual dark red
# inside an ink outline: the copy's opens onto the same black.
MIRROR_BLACK = (7, 7, 10)
# "auto" is the mood mouth; "line" is one long hairline that only parts into a dark slit when it talks (a
# mannequin's seam, no lips or teeth); "none" draws no mouth
MOUTHS = ("auto", "line", "none")


def hexrgb(h: str) -> tuple[int, int, int]:
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def check_original(face: dict) -> list[str]:
    """Problems with a face spec: unknown styles, or the classic default face."""
    out = []
    if face.get("eyes", "round") not in EYES:
        out.append(f"eyes {face.get('eyes')!r} isn't one of {EYES}")
    if face.get("mouth", "auto") not in MOUTHS:
        out.append(f"mouth {face.get('mouth')!r} isn't one of {MOUTHS}")
    if face.get("eyes") in ("dot", "classic") and face.get("default_expr", "neutral") in ("smirk", "grin", "smile"):
        out.append("black oval eyes over a smile is the game's default face: give this character another look")
    return out


def _fx(u: float) -> float:
    return FX0 + u * (FX1 - FX0)


def _fy(v: float) -> float:
    return FY0 + v * (FY1 - FY0)  # v from the top of the face box down


def _ellipse(d, cx, cy, rx, ry, **kw):
    d.ellipse([cx - rx, cy - ry, cx + rx, cy + ry], **kw)


def _stroke(d, pts, ink, th):
    """A thick ink line with round ends, like a marker: the classic game-face stroke."""
    d.line(pts, fill=ink, width=int(th), joint="curve")
    for x, y in (pts[0], pts[-1]):
        _ellipse(d, x, y, th / 2, th / 2, fill=ink)


def _curve(cx, cy, w, bend, n=16):
    """Points on a smooth smile (bend > 0) or frown (bend < 0) of width w."""
    return [(cx - w / 2 + w * i / n, cy + bend * (1 - (2 * i / n - 1) ** 2)) for i in range(n + 1)]


def _brow(d, cx, cy, w, tilt, ink, th, side):
    """A thin brow: tilt > 0 raises the inner end (worried), < 0 lowers it (angry)."""
    dx = w / 2
    inner = cx - side * dx
    outer = cx + side * dx
    _stroke(d, [(outer, cy), (inner, cy - tilt * w * 0.45)], ink, th * 1.15)


def _line_mouth(d, cx, cy, s, ink, open_):
    """A seam, not a mouth: a hairline wider than the eyes are apart, the ends fading into the skin. Talking parts
    it into a narrow dark slit, never round, never lips or teeth."""
    w = 0.62 * s
    th = max(6, int(0.016 * s))
    if open_ > 0.05:
        h = (0.012 + 0.05 * open_) * s
        pts = [(cx - w / 2 + w * i / 32, cy - h / 2 * math.sin(math.pi * i / 32) ** 0.7) for i in range(33)]
        pts += [(cx + w / 2 - w * i / 32, cy + h / 2 * math.sin(math.pi * i / 32) ** 0.7) for i in range(33)]
        d.polygon(pts, fill=(6, 5, 7))
        return
    n = 40
    for i in range(n):
        x0, x1 = cx - w / 2 + w * i / n, cx - w / 2 + w * (i + 1) / n
        k = math.sin(math.pi * (i + 0.5) / n) ** 0.35
        d.line([(x0, cy), (x1, cy)], fill=ink, width=max(2, int(th * k)))


def _mouth(d, expr, cx, cy, s, ink, open_, inside, hole=False):
    w = 0.22 * s
    th = max(12, int(0.042 * s))
    if open_ > 0.05 and expr not in ("blank",):
        h = (0.035 + 0.075 * open_) * s
        ww = w * (0.55 if expr in ("scared", "wide", "crying", "worried", "terrified", "squeeze") else 0.75)
        # a hole (a face's "mouth_inside") is that colour to its edge, with no lip line: the same size as the mouth
        _ellipse(d, cx, cy, ww / 2, h / 2, fill=inside, outline=inside if hole else ink, width=th)
        return
    if expr in ("worried", "crying", "terrified", "squeeze"):
        pts = [(cx - w * 0.45 + w * 0.9 * i / 24, cy + 0.022 * s * math.sin(i / 24 * 3 * math.pi)) for i in range(25)]
        _stroke(d, pts, ink, th)
    elif expr == "scared" or expr == "wide":
        _ellipse(d, cx, cy, w * 0.18, w * 0.22, outline=ink, width=th, fill=inside)
    elif expr == "angry":
        _stroke(d, _curve(cx, cy + 0.03 * s, w * 0.8, -0.05 * s), ink, th)
    elif expr == "smirk":
        pts = [(x, y + (x - cx) * -0.25) for x, y in _curve(cx, cy, w * 0.8, 0.04 * s)]
        _stroke(d, pts, ink, th)
    elif expr == "grin":
        # too wide and too many teeth: the uncanny one
        ww = w * 2.4
        d.rounded_rectangle([cx - ww / 2, cy - w * 0.18, cx + ww / 2, cy + w * 0.26], radius=w * 0.12, fill=(250, 248, 240),
                            outline=ink, width=max(6, th // 2))
        for k in range(1, 10):
            x = cx - ww / 2 + k * ww / 10
            d.line([(x, cy - w * 0.18), (x, cy + w * 0.26)], fill=ink, width=max(4, th // 3))
        d.line([(cx - ww / 2, cy + w * 0.04), (cx + ww / 2, cy + w * 0.04)], fill=ink, width=max(4, th // 3))
    elif expr == "warm":   # a wide closed smile, no teeth
        _stroke(d, _curve(cx, cy - 0.012 * s, w * 1.0, 0.05 * s), ink, th)
    elif expr == "soft":   # a small closed smile
        _stroke(d, _curve(cx, cy - 0.006 * s, w * 0.6, 0.026 * s), ink, th)
    elif expr == "blank" or expr == "shut" or expr == "asleep":
        _stroke(d, [(cx - w * 0.25, cy), (cx + w * 0.25, cy)], ink, th)
    else:  # neutral: a short flat stroke, a little off centre (never the default smile)
        _stroke(d, [(cx - w * 0.28, cy + 0.004 * s), (cx + w * 0.22, cy - 0.004 * s)], ink, th)


@lru_cache(maxsize=256)
def _draw(skin: str, eyes: str, brows: bool, ink: str, pupil: str, glow: str | None, expr: str, open_: float,
          look: tuple[float, float], blink: float, freckles: bool, cheeks: str | None, bags: bool,
          mouth: str = "auto", inside: str | None = None) -> Image.Image:
    im = Image.new("RGB", (TEX_W, TEX_H), hexrgb(skin))
    d = ImageDraw.Draw(im)
    s = FX1 - FX0                      # face box width in px
    inkc, pup = hexrgb(ink), hexrgb(pupil)
    white = (250, 250, 246)
    ey = _fy(0.42)
    ex = 0.22 * s
    th = max(12, int(0.04 * s))
    lx, ly = look
    shut = expr in ("shut", "squeeze", "soft") or blink > 0.8
    for side in (-1, 1):
        cx = _fx(0.5) + side * ex
        if eyes == "none":
            continue
        if eyes == "hollow":
            _ellipse(d, cx, ey, 0.12 * s, 0.15 * s, fill=(8, 6, 10))
            if glow:
                _ellipse(d, cx + lx * 0.02 * s, ey + ly * 0.02 * s, 0.035 * s, 0.035 * s, fill=hexrgb(glow))
            continue
        if expr == "asleep":   # a flat lid, its outer end drooping (the outer side is +side)
            w = 0.17 * s
            pts = [(cx - side * w / 2 + side * w * i / 12, ey + 0.004 * s + 0.03 * s * max(0.0, (i / 12 - 0.45) / 0.55) ** 2)
                   for i in range(13)]
            _stroke(d, pts, inkc, th)
            if brows:
                _brow(d, cx, ey - 0.15 * s, 0.15 * s, 0.0, inkc, th, side)
            continue
        if shut:
            if expr == "squeeze" and blink <= 0.8:   # screwed shut: short, sagging, tilted down to the nose
                pts = [(x, y + side * (x - cx) * -0.18) for x, y in _curve(cx, ey + 0.01 * s, 0.13 * s, 0.03 * s)]
                _stroke(d, pts, inkc, th * 1.1)
            else:
                _stroke(d, _curve(cx, ey, 0.17 * s, -0.035 * s), inkc, th)
            if expr == "squeeze" and brows:
                _brow(d, cx, ey - 0.13 * s, 0.15 * s, 1.1, inkc, th, side)
            if expr == "soft" and brows:   # relaxed: level, a little raised, no pinch
                _brow(d, cx, ey - 0.17 * s, 0.16 * s, 0.12, inkc, th, side)
            continue
        if eyes in ("round", "lashes", "tired", "mirror"):
            rx = 0.112 * s * (1.28 if expr == "terrified" else 1.2 if expr in ("wide", "scared") else 1.0)
            ry = rx * (1.0 - 0.85 * blink)
            if eyes == "tired" or expr == "angry":
                ry *= 0.78
            if expr == "warm":
                ry *= 0.86
            if eyes == "mirror":   # the same box as a round eye's outline, so never bigger; black to the edge
                _ellipse(d, cx, ey, rx, max(2, ry), fill=MIRROR_BLACK, outline=MIRROR_BLACK, width=th)
            else:
                _ellipse(d, cx, ey, rx, max(2, ry), fill=white, outline=inkc, width=th)
                pr = rx * (0.2 if expr == "terrified" else 0.28 if expr in ("blank", "wide") else 0.42)
                if ry > rx * 0.3:
                    px, py = cx + lx * rx * 0.35, ey + ly * ry * 0.3
                    _ellipse(d, px, py, pr, min(pr, ry * 0.9), fill=pup)
                    if glow:
                        _ellipse(d, px, py, pr * 0.5, pr * 0.5, fill=hexrgb(glow))
                    else:
                        _ellipse(d, px - pr * 0.35, py - pr * 0.4, pr * 0.28, pr * 0.28, fill=white)
            if expr == "angry":  # a lid across the top
                d.polygon([(cx - rx - 4, ey - ry - 6), (cx + rx + 4, ey - ry - 6),
                           (cx + side * rx, ey - ry * 0.1), (cx - side * rx * 0.2, ey - ry * 0.55)], fill=hexrgb(skin))
                d.line([(cx - side * rx * 0.2, ey - ry * 0.55), (cx + side * rx, ey - ry * 0.1)], fill=inkc, width=th)
            if eyes == "lashes":
                for k in (-1, 0, 1):
                    a = math.radians(-90 + side * (35 + k * 18))
                    x0, y0 = cx + rx * math.cos(a), ey + ry * math.sin(a)
                    d.line([(x0, y0), (x0 + 0.03 * s * math.cos(a), y0 + 0.03 * s * math.sin(a))], fill=inkc, width=th)
            if eyes == "tired" or bags:
                d.arc([cx - rx * 0.9, ey + ry * 0.6, cx + rx * 0.9, ey + ry * 1.6], 20, 160,
                      fill=tuple(int(c * 0.8) for c in hexrgb(skin)), width=th)
        elif eyes == "classic":
            # solid black ovals with a white glint, big and tall
            rx, ry = 0.062 * s * (1.15 if expr in ("wide", "scared", "terrified") else 1.0), 0.1 * s * (1.0 - 0.9 * blink)
            if expr == "angry":
                ry *= 0.7
            _ellipse(d, cx + lx * 0.02 * s, ey + ly * 0.01 * s, rx, max(3, ry), fill=pup)
            if ry > 0.03 * s and not glow:
                _ellipse(d, cx + lx * 0.02 * s - rx * 0.3, ey - ry * 0.45, rx * 0.32, rx * 0.36, fill=white)
            if glow:
                _ellipse(d, cx, ey, rx * 0.45, rx * 0.45, fill=hexrgb(glow))
        elif eyes == "dot":
            ry = 0.07 * s * (1.0 - 0.85 * blink)
            _ellipse(d, cx + lx * 0.015 * s, ey, 0.045 * s, max(2, ry), fill=pup)
        elif eyes == "button":
            r = 0.075 * s
            _ellipse(d, cx, ey, r, r, fill=pup, outline=inkc, width=th)
            for qx, qy in ((-1, -1), (1, -1), (-1, 1), (1, 1)):
                _ellipse(d, cx + qx * r * 0.35, ey + qy * r * 0.35, r * 0.12, r * 0.12, fill=(230, 225, 215))
        if brows and eyes not in ("hollow", "none"):
            tilt = {"worried": 0.9, "crying": 1.0, "scared": 0.7, "angry": -0.9, "wide": 0.4, "smirk": -0.25,
                    "grin": -0.4, "terrified": 1.0, "warm": 0.08}.get(expr, 0.0)
            by = ey - 0.175 * s - (0.05 * s if expr == "terrified" else 0.03 * s if expr in ("scared", "wide", "warm") else 0)
            _brow(d, cx, by, 0.16 * s, tilt, inkc, th, side)
    if expr == "crying" and not shut:
        tear = (120, 190, 255)
        for side in (-1, 1):
            cx = _fx(0.5) + side * ex
            d.line([(cx, ey + 0.1 * s), (cx - side * 0.012 * s, ey + 0.3 * s)], fill=tear, width=int(th * 1.6))
            _ellipse(d, cx - side * 0.012 * s, ey + 0.31 * s, th * 1.2, th * 1.5, fill=tear)
    if cheeks:
        for side in (-1, 1):
            _ellipse(d, _fx(0.5) + side * 0.3 * s, _fy(0.64), 0.055 * s, 0.032 * s, fill=hexrgb(cheeks))
    if freckles:
        for side in (-1, 1):
            for k, (fx, fy) in enumerate(((0.21, 0.58), (0.25, 0.61), (0.19, 0.63), (0.24, 0.66))):
                _ellipse(d, _fx(0.5) + side * (fx + 0.06) * s, _fy(fy), 6, 6, fill=tuple(int(c * 0.72) for c in hexrgb(skin)))
    if mouth == "line":
        _line_mouth(d, _fx(0.5), _fy(0.7), s, inkc, open_)
    elif mouth != "none":
        _mouth(d, expr, _fx(0.5), _fy(0.74), s, inkc, open_, (90, 30, 36) if inside is None else hexrgb(inside),
               hole=inside is not None)
    return im.filter(ImageFilter.SMOOTH)


def face_image(face: dict, skin: str, expr: str = "neutral", open_: float = 0.0, look=(0.0, 0.0),
               blink: float = 0.0) -> Image.Image:
    """The head's whole texture for one expression, mouth opening (0..1), gaze (-1..1 each way) and blink (0..1).
    Values are snapped so a film reuses a few dozen textures, not thousands."""
    q = lambda x, n: round(x * n) / n
    return _draw(skin, face.get("eyes", "round"), bool(face.get("brows", True)), face.get("ink", "#1a1416"),
                 face.get("pupil", "#141012"), face.get("glow"), expr, q(open_, mouth_steps(face)), (q(look[0], 2), q(look[1], 2)),
                 1.0 if blink > 0.5 else 0.0, bool(face.get("freckles")), face.get("cheeks"), bool(face.get("bags")),
                 face.get("mouth", "auto"), face.get("mouth_inside"))


def mouth_steps(face: dict) -> int:
    """How finely a mouth's opening is snapped: thirds for a talking mouth, tenths for the seam, so a slow
    manual opening (acting's mouth keys) reads as a slow parting and not three jumps."""
    return 10 if face.get("mouth") == "line" else 3


def face_key(face: dict, skin: str, expr: str, open_: float, look, blink: float) -> str:
    q = lambda x, n: round(x * n) / n
    # a non-default eye or mouth style is in the key, so a cached texture of the old style is never reused
    style = "".join(f"{k}{face[k]}-" for k in ("eyes", "mouth") if k in face and face[k] in ("none", "line", "mirror"))
    if face.get("mouth_inside"):   # an open mouth's own inside colour (the copy's opens onto black)
        style += f"in{face['mouth_inside'].lstrip('#')}-"
    return f"{style}{expr}-{q(open_, mouth_steps(face))}-{q(look[0], 2)}-{q(look[1], 2)}-{int(blink > 0.5)}"
