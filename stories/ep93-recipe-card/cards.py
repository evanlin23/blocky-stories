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
    pts = [(0, 0), (0.42, 0), (0.46, 0.5), (0.95, 0.58), (1.05, 0.78), (1.0, 1.0), (0.0, 1.0), (-0.03, 0.4)]
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


def photo():
    """The framed photo, sixty years back: young Nell at her first stove, laughing, a small card in her hand."""
    W_, H_ = 800, 1000
    im = Image.new("RGB", (W_, H_), (232, 200, 150))
    d = ImageDraw.Draw(im)
    d.rectangle([0, 0, W_, 620], fill=(238, 214, 168))            # wall
    d.rectangle([0, 620, W_, H_], fill=(196, 150, 104))           # floor
    d.rectangle([60, 70, 330, 300], fill=(160, 205, 215))         # window
    d.line([(195, 70), (195, 300)], fill=(240, 230, 210), width=10)
    d.rectangle([420, 520, 780, 840], fill=(226, 222, 208), outline=(120, 110, 100), width=8)   # old stove
    d.rectangle([450, 440, 750, 520], fill=(120, 110, 105))
    d.rectangle([500, 380, 700, 520], fill=(200, 116, 58), outline=(120, 70, 30), width=8)       # copper pot
    for sx in (520, 600, 680):                                    # painted steam
        d.arc([sx - 30, 250, sx + 30, 370], 200, 340, fill=(250, 245, 235), width=12)
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
    d.rectangle([430, 520, 510, 600], fill=(239, 220, 174), outline=(120, 100, 70), width=5)    # the small card
    boot(d, 465, 552, 34, STAIN)
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
    made["list"] = outdir / "list.png"
    made["photo"] = outdir / "photo.png"
    states = {"old": ("old", None), "old0": ("old", 0), "new0": ("new", 0), "new1": ("new", 1), "new9": ("new", 9),
              "new20": ("new", 20), "new39": ("new", 39), "new40": ("new", 40), "new41": ("new", 41),
              "new41s": ("new_stain", 41)}
    for k, (kind, n) in states.items():
        inset(kind, n).save(outdir / f"inset_{k}.png")
        made[f"inset_{k}"] = outdir / f"inset_{k}.png"
    return made


if __name__ == "__main__":
    import sys
    print(build_all(sys.argv[1] if len(sys.argv) > 1 else "/tmp/ep93cards"))
