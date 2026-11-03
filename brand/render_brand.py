"""Channel art from our own engine: the Keeper (the recurring rulebook host) as the avatar, and a town banner.

    $BLOCKY_BPY brand/render_brand.py [avatar|banner|both] [samples]

Writes brand/avatar-800.png (800 x 800) and brand/banner-2560x1440.png (YouTube's banner size; everything that
matters sits inside the 1546 x 423 middle band that shows on every device). Everything is built in blocky/ (rig.py,
kit.py): no outside assets except the CC0 props the engine already allows, and no letters anywhere (hard rule 1).
"""

import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from blocky import kit, rig  # noqa: E402

OUT = ROOT / "brand"
WORK = ROOT / "out" / "brand"

KEEPER = {
    "age": "adult", "skin": "#e7b48c", "shirt": "#2f6f6a", "pattern": "knit", "pattern_c": "#285e5a",
    "collar": "#f2e6c8", "pants": "#26303f", "shoes": "#1b1b20", "sleeves": "long",
    "hair": "swoop", "hair_c": "#5a3a22", "hat": "tophat", "hat_c": "#1f2b33",
    "extras": ["scarf", "coat"], "extra_c": "#e0a32a",
    "face": {"eyes": "dot", "brows": True},
}


def book(parent=None, loc=(0, 0, 0), rot=(0, 0, 0), s=1.0):
    """The town rulebook: a thick oxblood book with a brass clasp and a stamped glyph (no letters)."""
    cover = kit.plastic("#7a1f2b", 0.5)
    pages = kit.plastic("#f3ead2", 0.8)
    brass = kit.metal("#d8a840", 0.3)
    root = kit.empty("book", loc, parent, rot)
    kit.box("book.back", (0.34 * s, 0.015 * s, 0.46 * s), (0, 0.035 * s, 0), cover, root, bevel=0.004)
    kit.box("book.front", (0.34 * s, 0.015 * s, 0.46 * s), (0, -0.035 * s, 0), cover, root, bevel=0.004)
    kit.box("book.spine", (0.03 * s, 0.085 * s, 0.46 * s), (-0.16 * s, 0, 0), cover, root, bevel=0.006)
    kit.box("book.pages", (0.31 * s, 0.056 * s, 0.43 * s), (0.01 * s, 0, 0), pages, root)
    kit.box("book.clasp", (0.06 * s, 0.1 * s, 0.07 * s), (0.17 * s, 0, 0), brass, root, bevel=0.005)
    kit.cyl("book.glyph", 0.07 * s, 0.01 * s, (0, -0.045 * s, 0.05 * s), brass, root, rot=(math.pi / 2, 0, 0), n=6)
    return root


def keeper(pose_expr="smirk"):
    (WORK / "faces").mkdir(parents=True, exist_ok=True)
    c = rig.Character("keeper", KEEPER, WORK / "faces")
    c.pose(0, 0, 0, 0, 0.0, (0.75, 0.75), (-0.12, -0.12), 0.0, 0.0, 0.0, 0.0, pose_expr, 0.0, (0, 0), 0.0, False)
    return c


def avatar(samples):
    kit.reset()
    kit.world("#3b2f6b", 1.0)          # violet dusk behind a warm face: high contrast, reads at 98 px
    kit.set_fog("#3b2f6b", 0.0, 50)
    kit.setup_render((800, 800), samples, 4, -0.2)
    keeper()
    book(None, (0.0, -0.52, 1.1), (0.15, 0, 0.0), 1.0)
    bg = kit.plastic("#4a3a86", 0.9)
    kit.box("wall", (6, 0.2, 6), (0, 1.6, 1.5), bg)
    kit.aim(kit.light("key", "AREA", (-1.2, -2.2, 2.4), 140, "#ffd8a8", size=1.6), (0, 0, 1.4))
    kit.aim(kit.light("rim", "AREA", (1.4, 1.0, 2.2), 220, "#7fe0ff", size=1.0), (0, 0, 1.4))
    kit.aim(kit.light("fill", "AREA", (1.6, -2.0, 1.2), 30, "#c8b0ff", size=2.0), (0, 0, 1.4))
    kit.place_camera((0.0, -3.4, 1.7), (0.0, 0.0, 1.52), 52)
    WORK.mkdir(parents=True, exist_ok=True)
    kit.render_to(OUT / "avatar-800.png")


def banner(samples):
    kit.reset()
    kit.world("#2b2350", 1.0)          # dusk: violet sky
    kit.set_fog("#6a4d7a", 0.035, 6)
    kit.setup_render((2560, 1440), samples, 4, 0.35)
    ground = kit.plastic("#5aa04a", 0.7)
    road = kit.plastic("#5a5c66", 0.8)
    kit.box("ground", (80, 60, 0.2), (0, 20, -0.1), ground)
    kit.box("road", (80, 3.2, 0.21), (0, 2.5, -0.09), road)
    colours = ["#e8584a", "#f2c14e", "#4fa3d9", "#9b6ad6", "#f08bb0", "#58c08a", "#f2994a"]
    win = kit.emit("#ffd98a", 6.0)
    for k, x in enumerate(range(-22, 23, 4)):
        h = 3.0 + (k * 37 % 5) * 0.5
        mat = kit.plastic(colours[k % len(colours)], 0.45)
        kit.box(f"house{k}", (3.2, 3.0, h), (x, 7.5, h / 2), mat, bevel=0.05)
        roof = kit.plastic("#3a2f3f", 0.6)
        kit.box(f"roof{k}", (3.5, 3.3, 0.35), (x, 7.5, h + 0.17), roof, bevel=0.03)
        if k % 3 != 1:                 # some windows lit, some dark
            kit.box(f"win{k}", (0.7, 0.05, 0.8), (x - 0.6, 5.98, h * 0.55), win)
        else:                          # a dark window; in one of them, two small eyes
            kit.box(f"win{k}", (0.7, 0.05, 0.8), (x - 0.6, 5.98, h * 0.55), kit.plastic("#0e0c14", 0.9))
            if x == 6:
                for ex in (-0.12, 0.12):
                    kit.sphere(f"eyes{ex}", 0.035, (x - 0.6 + ex, 5.94, h * 0.55 + 0.1), kit.emit("#f4f8ff", 5.0))
        kit.box(f"door{k}", (0.8, 0.05, 1.5), (x + 0.7, 5.98, 0.75), roof)
    for k, x in enumerate(range(-20, 21, 8)):
        pole = kit.metal("#2a2a30", 0.4)
        kit.cyl(f"pole{k}", 0.06, 3.2, (x, 4.6, 1.6), pole)
        kit.sphere(f"lamp{k}", 0.22, (x, 4.6, 3.25), kit.emit("#ffe2a0", 12.0))
        kit.light(f"lampl{k}", "POINT", (x, 4.4, 3.0), 120, "#ffd38a", size=0.3)
    keeper()
    book(None, (0.0, -0.52, 1.1), (0.15, 0, 0.0), 1.0)
    kit.aim(kit.light("key", "AREA", (-1.5, -3.0, 2.6), 260, "#fff0d8", size=2.0), (0, 0, 1.4))
    kit.light("moon", "SUN", (0, 0, 10), 1.2, "#b8c4ff", rot=(0.9, 0.2, 0.6))
    # the quiet-dread cue: something far too tall waits in the gap between two houses, unlit, faint in the fog
    shade = kit.plastic("#15121c", 0.9)
    kit.box("tall.body", (0.45, 0.4, 5.2), (4.0, 9.6, 2.6), shade, bevel=0.04)
    kit.box("tall.head", (0.5, 0.45, 0.5), (4.0, 9.6, 5.45), shade, bevel=0.08)
    kit.sphere("tall.eye", 0.045, (3.92, 9.36, 5.5), kit.emit("#e8f4ff", 4.0))
    kit.place_camera((0.0, -8.0, 1.6), (0.0, 0.0, 1.6), 32)
    WORK.mkdir(parents=True, exist_ok=True)
    kit.render_to(OUT / "banner-2560x1440.png")


if __name__ == "__main__":
    which = sys.argv[1] if len(sys.argv) > 1 else "both"
    samples = int(sys.argv[2]) if len(sys.argv) > 2 else 32
    if which in ("avatar", "both"):
        avatar(samples)
    if which in ("banner", "both"):
        banner(samples)
