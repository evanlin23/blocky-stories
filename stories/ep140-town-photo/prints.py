"""ep140-town-photo: every picture that is a flat image (PIL only): the town prints, the chalkboard and the rule tag.

A town print is the bleachers seen from the camera: five rows of people on pale seats under a strip of brick wall. The
crowd is drawn here in simple blocks (a head, hair, a torso) in the same colours as the set's crowd. Gaps are exact:
one seat wide, left bare so the pale seat shows. Nothing here has letters except numerals (the chalkboard and tag).
"""
from __future__ import annotations

import random

from PIL import Image, ImageDraw, ImageFilter, ImageFont

FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
SKINS = ["#f1c9a0", "#e8b891", "#c98f62", "#a8714a", "#f6d5b5", "#8a5a3a"]
HAIRS = ["#2a1c14", "#5a3a22", "#c9a46a", "#8a8a8a", "#7a2a1a", "#171717", "#e8d9a8"]
SHIRTS = ["#ff6f61", "#ffd23f", "#2bb3a3", "#4a7fd0", "#f4f4f0", "#9a63c8", "#e2884a", "#6dbf5a", "#d94f7a", "#3f4a66"]
GREEN = (126, 217, 87)
W, H = 640, 560
COLS, ROWS = 9, 5
SEATS = {"me": (2, 0), "mom": (2, -1), "grandma": (0, -1), "okafor": (0, 0)}


def rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def seat_xy(r, k):
    """Print pixel centre of the seat (row r from the front, k seats from the middle): the front row is at the bottom."""
    sp = 64
    x = W / 2 + sp * k + (sp / 2 if r % 2 else 0)
    y = H - 112 - r * 72
    return x, y


def person(d, x, y, skin, hair, shirt, s=1.0, long=False, cap=False, beard=False, white=False, hand_to=None, bun=False):
    hw = 22 * s
    d.rounded_rectangle([x - hw, y - 8 * s, x + hw, y + 52 * s], radius=int(8 * s), fill=rgb(shirt))
    d.rounded_rectangle([x - 20 * s, y - 52 * s, x + 20 * s, y - 10 * s], radius=int(10 * s), fill=rgb(skin))
    if long:
        d.rectangle([x - 22 * s, y - 52 * s, x - 14 * s, y - 14 * s], fill=rgb(hair))
        d.rectangle([x + 14 * s, y - 52 * s, x + 22 * s, y - 14 * s], fill=rgb(hair))
    d.rounded_rectangle([x - 22 * s, y - 58 * s, x + 22 * s, y - 38 * s], radius=int(8 * s), fill=rgb(hair))
    if bun:
        d.ellipse([x - 12 * s, y - 80 * s, x + 12 * s, y - 56 * s], fill=rgb(hair))
    if cap:
        d.rectangle([x - 24 * s, y - 62 * s, x + 24 * s, y - 46 * s], fill=rgb("#3a3d44"))
    if beard:
        d.rounded_rectangle([x - 17 * s, y - 24 * s, x + 17 * s, y - 6 * s], radius=int(6 * s), fill=(244, 244, 240))
    for sx in (-8, 8):
        d.ellipse([x + sx * s - 3 * s, y - 36 * s, x + sx * s + 3 * s, y - 30 * s], fill=(30, 22, 28))
    d.arc([x - 8 * s, y - 28 * s, x + 8 * s, y - 14 * s], 20, 160, fill=(120, 40, 40), width=max(1, int(2 * s)))


def seat_bar(d, r):
    y = H - 112 - r * 72 + 52
    d.rectangle([0, y, W, y + 14], fill=rgb("#f6f3ea"))
    d.rectangle([0, y + 14, W, y + 20], fill=rgb("#bdb8a6"))


def draw_crowd(seed, gap=None, ring=False, okafor=False, hand_gap=False, tint=None, grass=False, chk=0):
    """gap: (row, k) to leave bare. okafor: put him in the front row middle. tint: 'sepia'/'blue'/'rose' for old prints."""
    rng = random.Random(seed)
    im = Image.new("RGB", (W, H), rgb("#7cc8ff"))
    d = ImageDraw.Draw(im)
    d.rectangle([0, 0, W, 175], fill=rgb("#c8553d"))
    for i in range(6):
        d.rectangle([40 + i * 110, 28, 40 + i * 110 + 56, 112], fill=rgb("#dfeaf2"))
    d.rectangle([0, 175, W, H], fill=rgb("#e9e4d3"))
    ring_xy = None
    ok_xy = None
    for r in range(ROWS - 1, -1, -1):
        for k in range(-5, 6):
            x, y = seat_xy(r, k)
            if x < 18 or x > W - 18:
                continue
            if gap is not None and (r, k) == gap:
                ring_xy = (x, y)
                continue
            if okafor and (r, k) == (0, 0):
                ok_xy = (x, y)
                continue
            if (r, k) == (2, -1):
                person(d, x, y, "#f1c9a0", "#2a1c14", "#2bb3a3", long=True, bun=True)
                continue
            if (r, k) == (0, -1):
                person(d, x, y, "#f6d5b5", "#f2f2f2", "#b9a0e0", long=True)
                continue
            person(d, x, y, rng.choice(SKINS), rng.choice(HAIRS), rng.choice(SHIRTS), long=rng.random() < 0.35)
        d.rectangle([0, y + 52, W, y + 64], fill=rgb("#f6f3ea"))
    if ok_xy:
        x, y = ok_xy
        person(d, x, y + 10, "#f1c9a0", "#f4f4f0", "#3c3f46", s=1.7, cap=True, beard=True)
        d.ellipse([x - 62, y - 100, x + 62, y + 96], outline=GREEN, width=9)
    if hand_gap and ring_xy:
        x, y = ring_xy
        mx, my = seat_xy(2, -1)
        d.rounded_rectangle([mx + 14, my + 6, x - 4, my + 28], radius=10, fill=rgb("#f1c9a0"))
        d.ellipse([x - 20, my + 4, x + 6, my + 32], fill=rgb("#f1c9a0"))
    if ring and ring_xy:
        x, y = ring_xy
        d.ellipse([x - 44, y - 76, x + 44, y + 70], outline=GREEN, width=11)
    if grass:
        d.rectangle([0, H - 70, W, H], fill=rgb("#5bd16a"))
    im = im.filter(ImageFilter.GaussianBlur(0.6))
    if tint:
        g = im.convert("L")
        if tint == "sepia":
            im = Image.merge("RGB", [g.point(lambda v: min(255, int(v * 1.06 + 20))), g.point(lambda v: int(v * 0.92 + 12)),
                                     g.point(lambda v: int(v * 0.72 + 6))])
        elif tint == "blue":
            im = Image.merge("RGB", [g.point(lambda v: int(v * 0.78 + 6)), g.point(lambda v: int(v * 0.92 + 10)),
                                     g.point(lambda v: min(255, int(v * 1.05 + 25)))])
        else:
            im = Image.merge("RGB", [g.point(lambda v: min(255, int(v * 1.05 + 28))), g.point(lambda v: int(v * 0.88 + 18)),
                                     g.point(lambda v: int(v * 0.8 + 22))])
    return im


def test_print():
    """Thursday's test shot: Mom close on the left, her hand out to the right holding the air where I sat."""
    im = Image.new("RGB", (W, H), rgb("#c8553d"))
    d = ImageDraw.Draw(im)
    d.rectangle([0, 330, W, H], fill=rgb("#e9e4d3"))
    d.rectangle([0, 0, W, 330], fill=rgb("#c8553d"))
    for i in range(3):
        d.rectangle([40 + i * 210, 40, 40 + i * 210 + 110, 190], fill=rgb("#dfeaf2"))
    person(d, 150, 330, "#f1c9a0", "#2a1c14", "#2bb3a3", s=4.2, long=True, bun=True)
    d.rectangle([0, 440, W, H], fill=rgb("#f6f3ea"))
    # her arm reaches right and her hand closes on nothing
    d.rounded_rectangle([190, 360, 470, 430], radius=30, fill=rgb("#2bb3a3"))
    d.ellipse([440, 346, 540, 446], fill=rgb("#f1c9a0"))
    d.ellipse([478, 372, 508, 420], fill=rgb("#d9a678"))
    # the bare seat where I sat, one person wide, with a green ring
    d.ellipse([420, 150, 640, 540], outline=GREEN, width=16)
    return im


def hall_photo(seed, tint, grass=False):
    return draw_crowd(seed, tint=tint, grass=grass)


def chalk(state):
    """The headcount board's face. states: a (212 / 211), a900, a859, smudge, b859."""
    bw, bh = 960, 700
    im = Image.new("RGB", (bw, bh), rgb("#2f5d4a"))
    rng = random.Random(7)
    px = im.load()
    for _ in range(14000):
        x, y = rng.randrange(bw), rng.randrange(bh)
        v = rng.randrange(-10, 14)
        r, g, b = px[x, y]
        px[x, y] = (max(0, min(255, r + v)), max(0, min(255, g + v)), max(0, min(255, b + v)))
    d = ImageDraw.Draw(im)
    f = ImageFont.truetype(FONT, 270)
    cw = (244, 241, 230)
    clock = state in ("a900", "a859", "b859")
    nx = 60 if clock else 150
    top = "212"
    bot = "212" if state == "b859" else "211"
    d.text((nx, 20), top, font=f, fill=cw)
    d.line([nx, 350, nx + 540, 350], fill=cw, width=10)
    if state == "smudge":
        # a wiped patch where the bottom number was, a few chalk dust streaks
        d.text((nx, 370), "211", font=f, fill=(118, 148, 134))
        for i in range(7):
            d.line([nx - 20 + i * 90, 380 + (i % 3) * 40, nx + 70 + i * 90, 560 + (i % 2) * 60], fill=(96, 130, 116), width=46)
    else:
        d.text((nx, 370), bot, font=f, fill=cw)
    if clock:
        cx, cy, r = 780, 210, 120
        d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=cw, width=12)
        if state == "a900":
            d.line([cx, cy, cx, cy - 78], fill=cw, width=12)           # minute hand up
            d.line([cx, cy, cx - 70, cy], fill=cw, width=14)           # hour hand to 9
            small = "9:00"
        else:
            d.line([cx, cy, cx - 6, cy - 100], fill=cw, width=10)      # minute hand nearly 12
            d.line([cx, cy, cx - 58, cy - 4], fill=cw, width=14)
            small = "8:59"
        d.ellipse([cx - 10, cy - 10, cx + 10, cy + 10], fill=cw)
        d.text((cx - 130, 380), small, font=ImageFont.truetype(FONT, 130), fill=cw)
    return im.filter(ImageFilter.GaussianBlur(0.7))


def tag(state):
    """The rule tag: a chalk-green tile with white numerals, 212 over 211 (or 212 over 212)."""
    tw, th = 420, 300
    im = Image.new("RGB", (tw, th), rgb("#fff4d6"))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([14, 14, tw - 14, th - 14], radius=26, fill=rgb("#2f5d4a"))
    f = ImageFont.truetype(FONT, 118)
    d.text((tw // 2, 74), "212", font=f, fill=(255, 255, 255), anchor="mm")
    d.line([90, 150, tw - 90, 150], fill=(255, 255, 255), width=7)
    d.text((tw // 2, 226), "212" if state == "b" else "211", font=f, fill=(255, 255, 255), anchor="mm")
    return im
