"""Drawn textures for ep93 (PIL only): the recipe cards, the grocery list, the framed photo and the inset marker.

No letters anywhere: handwriting is looping scribble glyphs, plus numerals (the barred 7 is the one readable mark).
"""
import math
import random
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = Path(__file__).resolve().parent
FONT = HERE.parents[1] / "blocky" / "fonts" / "SchibstedGrotesk-Black.ttf"
CW, CH = 640, 384
OLD, NEW = (239, 220, 174), (251, 248, 240)
STAIN, STAIN_WET = (138, 90, 50), (92, 52, 24)
INK_OLD, INK_NEW = (52, 38, 30), (30, 44, 90)


def _hx(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def _loop_word(d, x0, base, width, amp, ink, thick, rng):
    """One looping cursive-ish word: a trochoid, so it has real loops and no letters."""
    n = max(8, int(width / 3))
    pts = []
    turns = rng.uniform(3.0, 5.0)
    for i in range(n + 1):
        u = i / n
        th = u * turns * 2 * math.pi
        x = x0 + u * width - amp * 0.55 * math.sin(th)
        y = base - amp * (0.5 - 0.5 * math.cos(th)) * (0.7 + 0.3 * math.sin(u * 5.0 + rng.random()))
        pts.append((x, y))
    d.line(pts, fill=ink, width=thick, joint="curve")


def barred_seven(d, x, y, s, ink, thick):
    d.line([(x, y), (x + s, y), (x + s * 0.35, y + s * 1.7)], fill=ink, width=thick, joint="curve")
    d.line([(x + s * 0.12, y + s * 0.85), (x + s * 0.72, y + s * 0.85)], fill=ink, width=max(2, thick - 1))


def rows(d, n, ink, seed=3, thick=8, x_start=70, y0=104, dy=44, sevens=(0, 2, 4)):
    rng = random.Random(seed)
    for r in range(n):
        y = y0 + r * dy
        x = x_start
        if r in sevens:
            barred_seven(d, 38, y - 30, 20, ink, thick)
        else:
            d.line([(40, y - 12), (58, y - 12)], fill=ink, width=thick)
        while x < CW - 80:
            w = rng.randint(70, 150)
            if x + w > CW - 50:
                break
            _loop_word(d, x, y, w, rng.uniform(20, 28), ink, thick, rng)
            x += w + rng.randint(18, 30)


def boot(d, x, y, s, fill):
    """A little boot: a shaft, a foot, a toe."""
    pts = [(0, 0), (0.42, 0), (0.46, 0.5), (0.95, 0.56), (1.07, 0.74), (1.0, 1.0), (0.46, 1.0), (0.44, 0.86),
           (0.18, 0.86), (0.16, 1.0), (0.0, 1.0), (-0.03, 0.4)]
    d.polygon([(x + px * s, y + py * s) for px, py in pts], fill=fill)


def card(kind):
    """kind: old | old_wet | new | new_line | new_stain."""
    old = kind.startswith("old")
    base = OLD if old else NEW
    ink = INK_OLD if old else INK_NEW
    im = Image.new("RGB", (CW, CH), base)
    d = ImageDraw.Draw(im)
    for yy in range(78, CH - 20, 44):                       # ruled lines
        d.line([(20, yy), (CW - 20, yy)], fill=tuple(int(c * 0.9) for c in base), width=2)
    d.rectangle([0, 0, CW - 1, 38], fill=(216, 51, 74) if old else (232, 90, 60))   # the red header band
    n = 6 if old or kind != "new" else 5
    if kind == "new":
        n = 5
    if kind in ("new_line", "new_stain"):
        n = 6
    rows(d, n if kind != "new_stain" else 6, ink, thick=8)
    if old or kind == "new_stain":
        ov = Image.new("RGBA", (CW, CH), (0, 0, 0, 0))
        od = ImageDraw.Draw(ov)
        wet = kind == "old_wet"
        boot(od, 380, 196, 170, STAIN_WET if wet else STAIN)
        od.ellipse([505, 330, 520, 352], fill=STAIN_WET if wet else STAIN)    # the drip
        if wet:
            od.ellipse([410, 214, 440, 230], fill=(255, 255, 255, 200))
            od.ellipse([455, 262, 468, 272], fill=(255, 255, 255, 170))
            od.line([(430, 350), (432, 372)], fill=STAIN_WET, width=8)
        ov = ov.filter(ImageFilter.GaussianBlur(1.2))
        im = Image.alpha_composite(im.convert("RGBA"), ov).convert("RGB")
    d = ImageDraw.Draw(im)
    d.rectangle([0, 0, CW - 1, CH - 1], outline=tuple(int(c * 0.78) for c in base), width=6)
    return im


def lst():
    """My grocery list: a torn sheet with the same loops and the same barred 7."""
    im = Image.new("RGB", (CW, CH), (252, 250, 232))
    d = ImageDraw.Draw(im)
    for r in range(4):
        d.rectangle([34, 62 + r * 74, 62, 90 + r * 74], outline=INK_NEW, width=5)
    rng = random.Random(3)
    for r in range(4):
        y = 112 + r * 74
        x = 100
        for _ in range(2):
            w = rng.randint(90, 170)
            _loop_word(d, x, y, w, 26, INK_NEW, 7, rng)
            x += w + 30
        barred_seven(d, 520, y - 40, 24, INK_NEW, 7)
    d.rectangle([0, 0, CW - 1, CH - 1], outline=(200, 190, 170), width=6)
    return im


def inset(kind, n=None):
    """The rule marker: the card on a dark rounded plate with a lemon try-counter badge. RGBA, transparent corners."""
    c = card(kind).resize((560, 336))
    W_, H_ = 640, 420
    im = Image.new("RGBA", (W_, H_), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([0, 0, W_ - 1, H_ - 1], radius=36, fill=(40, 24, 18, 255))
    d.rounded_rectangle([10, 10, W_ - 11, H_ - 11], radius=30, fill=(255, 255, 255, 255))
    im.paste(c, (40, 40))
    if n is not None:
        d.ellipse([W_ - 250, H_ - 230, W_ - 8, H_ - 8], fill=(255, 225, 77, 255), outline=(40, 24, 18, 255), width=12)
        f = ImageFont.truetype(str(FONT), 150 if n < 10 else (130 if n < 100 else 100))
        s = str(n)
        bb = d.textbbox((0, 0), s, font=f)
        cx, cy = W_ - 129, H_ - 119
        d.text((cx - (bb[0] + bb[2]) / 2, cy - (bb[1] + bb[3]) / 2), s, font=f, fill=(40, 24, 18, 255))
    return im


def timer(n, tag=None):
    """The rule marker: a round lemon-yellow kitchen timer. Face = the try count, a needle creeping toward the lemon
    mark at the top (one notch per try). RGBA 512 x 512."""
    S_ = 512
    im = Image.new("RGBA", (S_, S_), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    for fx in (110, 402):
        d.ellipse([fx - 38, 6, fx + 38, 70], fill=(40, 24, 18, 255))                 # the two bells on top
    d.ellipse([10, 30, S_ - 10, S_ - 10], fill=(40, 24, 18, 255))
    d.ellipse([34, 54, S_ - 34, S_ - 34], fill=(255, 225, 77, 255))
    d.ellipse([70, 90, S_ - 70, S_ - 70], fill=(255, 244, 190, 255), outline=(40, 24, 18, 255), width=8)
    for k in range(12):
        a = k * math.pi / 6
        x0, y0 = 256 + 170 * math.sin(a), 270 - 170 * math.cos(a)
        x1, y1 = 256 + 190 * math.sin(a), 270 - 190 * math.cos(a)
        d.line([(x0, y0), (x1, y1)], fill=(40, 24, 18, 255), width=8)
    d.ellipse([226, 98, 286, 150], fill=(255, 225, 77, 255), outline=(40, 24, 18, 255), width=7)   # the lemon mark
    d.polygon([(256, 98), (284, 80), (292, 104)], fill=(70, 170, 80, 255))
    f = ImageFont.truetype(str(FONT), 300 if n < 10 else 215)
    s_ = str(n)
    bb = d.textbbox((0, 0), s_, font=f)
    d.text((256 - (bb[0] + bb[2]) / 2, 285 - (bb[1] + bb[3]) / 2), s_, font=f, fill=(40, 24, 18, 255))
    ang = (-150 + 150 * min(1.0, n / 41.0)) * math.pi / 180        # rest at lower left, the lemon at the top
    for k in range(0, 41):                                          # a red arc of tries along the rim, never over the digit
        a2 = (-150 + 150 * min(1.0, k / 41.0)) * math.pi / 180
        if a2 > ang + 1e-6:
            break
        d.ellipse([256 + 168 * math.sin(a2) - 7, 270 - 168 * math.cos(a2) - 7, 256 + 168 * math.sin(a2) + 7, 270 - 168 * math.cos(a2) + 7], fill=(216, 51, 74, 255))
    d.polygon([(256 + 150 * math.sin(ang), 270 - 150 * math.cos(ang)),
               (256 + 196 * math.sin(ang - 0.11), 270 - 196 * math.cos(ang - 0.11)),
               (256 + 196 * math.sin(ang + 0.11), 270 - 196 * math.cos(ang + 0.11))], fill=(216, 51, 74, 255), outline=(40, 24, 18, 255))
    return im


def tag(stain=False):
    """The paper tag hung on the timer: a tiny card with loops (and a tiny boot once it is stained)."""
    im = Image.new("RGBA", (192, 128), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([0, 0, 191, 127], radius=12, fill=(40, 24, 18, 255))
    d.rounded_rectangle([8, 8, 183, 119], radius=8, fill=(239, 220, 174, 255))
    d.rectangle([8, 8, 183, 30], fill=(216, 51, 74, 255))
    rng = random.Random(5)
    for r in range(3):
        _loop_word(d, 22, 62 + r * 24, 120, 12, INK_OLD, 4, rng)
    if stain:
        boot(d, 120, 62, 46, STAIN)
    return im


def curl_pts(n=90):
    """The steam curl, in unit coordinates (x right, y up, about -0.5..0.5): a rising stem that turns over on itself."""
    ctl = [(-0.10, -0.5), (-0.20, -0.32), (-0.04, -0.14), (0.16, 0.0), (0.26, 0.2), (0.14, 0.4), (-0.06, 0.40), (-0.14, 0.26),
           (-0.04, 0.14), (0.10, 0.16)]
    P = [ctl[0]] + ctl + [ctl[-1]]
    out = []
    for i in range(1, len(P) - 2):
        p0, p1, p2, p3 = P[i - 1], P[i], P[i + 1], P[i + 2]
        for j in range(n // (len(ctl) - 1) + 1):
            t = j / (n // (len(ctl) - 1) + 1)
            out.append(tuple(0.5 * ((2 * p1[k]) + (-p0[k] + p2[k]) * t + (2 * p0[k] - 5 * p1[k] + 4 * p2[k] - p3[k]) * t * t
                                    + (-p0[k] + 3 * p1[k] - 3 * p2[k] + p3[k]) * t ** 3) for k in (0, 1)))
    out.append(ctl[-1])
    return out


def curl_overlay(size=2048):
    """A hi-res transparent plane with the same steam curl, thick and crisp, to sit 1 cm over the photo's pot."""
    S2 = size * 4
    im = Image.new("RGBA", (S2, S2), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    pts = [(S2 / 2 + x * S2 * 0.82, S2 / 2 - y * S2 * 0.82) for x, y in curl_pts()]
    d.line(pts, fill=(252, 249, 242, 255), width=int(S2 * 0.075), joint="curve")
    for q in (pts[0], pts[-1]):
        r = S2 * 0.0375
        d.ellipse([q[0] - r, q[1] - r, q[0] + r, q[1] + r], fill=(252, 249, 242, 255))
    return im.resize((size, size), Image.LANCZOS)


def sky(kind="dusk"):
    """A vertical sky gradient with a few long pink cloud bars (dusk), for the window's view."""
    W_, H_ = 256, 512
    im = Image.new("RGB", (W_, H_))
    top, bot = ((122, 96, 190), (255, 176, 140))
    d = ImageDraw.Draw(im)
    for y in range(H_):
        u = (y / (H_ - 1)) ** 0.8
        d.line([(0, y), (W_, y)], fill=tuple(int(top[k] + (bot[k] - top[k]) * u) for k in range(3)))
    for yy, ww, h, c in ((150, 190, 14, (255, 214, 200)), (205, 220, 18, (255, 200, 190)), (265, 160, 12, (255, 224, 208)),
                         (110, 140, 10, (230, 190, 220))):
        d.rounded_rectangle([W_ // 2 - ww // 2 + (yy % 40) - 20, yy, W_ // 2 + ww // 2 + (yy % 40) - 20, yy + h], radius=h // 2, fill=c)
    return im.filter(ImageFilter.GaussianBlur(2.0))


def photo():
    """The framed photo, sixty years back: young Nell at her first stove, laughing, a small card in her hand."""
    W_, H_ = 800, 1000
    im = Image.new("RGB", (W_, H_), (232, 200, 150))
    d = ImageDraw.Draw(im)
    d.rectangle([0, 0, W_, 620], fill=(206, 166, 116))            # wall
    d.rectangle([0, 620, W_, H_], fill=(196, 150, 104))           # floor
    d.rectangle([60, 70, 330, 300], fill=(160, 205, 215))         # window
    d.line([(195, 70), (195, 300)], fill=(240, 230, 210), width=10)
    d.rectangle([420, 520, 780, 840], fill=(226, 222, 208), outline=(120, 110, 100), width=8)   # old stove
    d.rectangle([450, 440, 750, 520], fill=(120, 110, 105))
    d.rectangle([500, 380, 700, 520], fill=(200, 116, 58), outline=(120, 70, 30), width=8)       # copper pot
    d.line([(600 + p_[0] * 320, 220 - p_[1] * 320) for p_ in curl_pts()], fill=(252, 249, 242), width=22, joint="curve")
    for dx, dy in ((470, 360), (730, 340), (740, 400), (480, 410)):                               # the splash
        d.ellipse([dx - 12, dy - 12, dx + 12, dy + 12], fill=(230, 160, 70))
    # young Nell
    d.rectangle([150, 560, 330, 900], fill=(60, 100, 170))        # plain blue dress
    d.rectangle([140, 700, 175, 900], fill=(60, 100, 170))
    d.rectangle([310, 690, 345, 900], fill=(60, 100, 170))
    d.rectangle([180, 900, 230, 980], fill=(60, 50, 60))
    d.rectangle([250, 900, 300, 980], fill=(60, 50, 60))
    d.rounded_rectangle([160, 330, 320, 560], radius=40, fill=(238, 190, 150))   # head
    d.rounded_rectangle([150, 310, 330, 400], radius=34, fill=(52, 34, 26))      # dark hair
    d.rounded_rectangle([320, 340, 400, 470], radius=26, fill=(52, 34, 26))      # ponytail
    d.arc([195, 410, 235, 445], 200, 340, fill=(40, 24, 18), width=7)             # laughing eyes
    d.arc([250, 410, 290, 445], 200, 340, fill=(40, 24, 18), width=7)
    d.pieslice([205, 460, 285, 530], 0, 180, fill=(120, 40, 40))                  # open laughing mouth
    d.arc([205, 460, 285, 530], 0, 180, fill=(40, 24, 18), width=6)
    d.rectangle([330, 560, 480, 600], fill=(238, 190, 150))                       # arm out over the pot
    d.rectangle([420, 540, 590, 660], fill=(239, 220, 174), outline=(90, 70, 50), width=8)    # the card in her hand
    d.rectangle([420, 540, 590, 562], fill=(216, 51, 74))
    for yy in (582, 602):
        d.line([(436, yy), (574, yy)], fill=INK_OLD, width=4)
    boot(d, 500, 574, 62, STAIN)
    # faded warm: wash it toward cream, soft
    wash = Image.new("RGB", (W_, H_), (250, 232, 196))
    im = Image.blend(im, wash, 0.22).filter(ImageFilter.GaussianBlur(1.4))
    d = ImageDraw.Draw(im)
    d.rectangle([0, 0, W_ - 1, H_ - 1], outline=(250, 244, 230), width=34)
    return im


def build_all(outdir):
    outdir = Path(outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    made = {}
    for k in ("old", "old_wet", "new", "new_line", "new_stain"):
        card(k).save(outdir / f"card_{k}.png")
        made[f"card_{k}"] = outdir / f"card_{k}.png"
    lst().save(outdir / "list.png")
    photo().save(outdir / "photo.png")
    curl_overlay().save(outdir / "curl.png")
    made["curl"] = outdir / "curl.png"
    sky().save(outdir / "sky.png")
    made["sky"] = outdir / "sky.png"
    made["list"] = outdir / "list.png"
    made["photo"] = outdir / "photo.png"
    for n in (0, 1, 9, 20, 39, 40, 41):
        timer(n).save(outdir / f"timer_{n}.png")
        made[f"timer_{n}"] = outdir / f"timer_{n}.png"
    for k, st in (("tag", False), ("tag_stain", True)):
        tag(st).save(outdir / f"{k}.png")
        made[k] = outdir / f"{k}.png"
    return made


if __name__ == "__main__":
    import sys
    print(build_all(sys.argv[1] if len(sys.argv) > 1 else "/tmp/ep93cards"))
