"""Adds the channel name to the rendered banner, inside YouTube's safe band, in our own font (OFL, blocky/fonts).

    python brand/name_banner.py BUHTOWN     # brand/banner-2560x1440.png -> brand/banner-buhtown-2560x1440.png
"""

import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
SAFE = (507, 508, 2053, 931)   # the 1546 x 423 band every device shows


def main(name: str) -> None:
    im = Image.open(ROOT / "brand" / "banner-2560x1440.png").convert("RGB")
    d = ImageDraw.Draw(im)
    font = ImageFont.truetype(str(ROOT / "blocky" / "fonts" / "SchibstedGrotesk-Black.ttf"), 150)
    x0, y0, x1, y1 = SAFE
    # left of the Keeper (who stands at the centre), vertically centred in the band
    box = d.textbbox((0, 0), name, font=font, stroke_width=10)
    w, h = box[2] - box[0], box[3] - box[1]
    x = x0 + 30
    y = (y0 + y1) // 2 - h // 2 - box[1]
    if x + w > 1280 - 120:              # too wide for the left half: shrink to fit
        font = ImageFont.truetype(str(ROOT / "blocky" / "fonts" / "SchibstedGrotesk-Black.ttf"),
                                  int(150 * (1280 - 120 - x) / w))
        box = d.textbbox((0, 0), name, font=font, stroke_width=10)
        h = box[3] - box[1]
        y = (y0 + y1) // 2 - h // 2 - box[1]
    d.text((x, y), name, font=font, fill="#fff4dc", stroke_width=10, stroke_fill="#1a1426")
    out = ROOT / "brand" / f"banner-{name.lower()}-2560x1440.png"
    im.save(out)
    print(out)


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "BUHTOWN")
