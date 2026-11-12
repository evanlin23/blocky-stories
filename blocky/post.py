"""The finish on every rendered frame: scale up to 1080 x 1920, bloom, the story's grade, its effects (flashes,
blackouts, static, shake, rain), vignette, grain, and the captions. Then H.264.

Captions follow the reference and note 13: a heavy grotesk (Schibsted Grotesk Black, OFL) at 84 px, which
is a cap height over 56 px, white with the key words in CAPS and the story's key colour, a dark outline and a
soft shadow. Two or three words at a time, two lines at most, centred a little below the middle of the
frame as the reference does, and inside x <= 898 and y <= 1400 (clear of the right 15% and the bottom 20%).
"""

from __future__ import annotations

import json
import math
import subprocess
from functools import lru_cache
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

from blocky import polish

HERE = Path(__file__).resolve().parent
FONT = HERE / "fonts" / "SchibstedGrotesk-Black.ttf"
W, H = 1080, 1920
CAP_PX = 84
BIG_PX = 130
MAX_W = 740                 # caption block width, outline included
CX, CY = 528, 1260          # caption block centre (right edge at most 898)
SAFE_RIGHT, SAFE_BOTTOM = int(W * 0.85), int(H * 0.80)
WHITE, INK = (255, 255, 255), (14, 12, 18)
KEY = {"c": (255, 214, 64)}  # the story's key colour, set by finish()


@lru_cache(maxsize=8)
def font(px: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(FONT), px)


def is_key(word: str) -> bool:
    core = "".join(ch for ch in word if ch.isalnum())
    return bool(core) and (core.isupper() and len(core) > 1 or core.isdigit() or word == "÷")


def wrap(words: list[str], f: ImageFont.FreeTypeFont, max_w: int) -> list[list[str]]:
    """One line if it fits, else the most even two-line split."""
    sp = f.getlength(" ")
    width = lambda ws: sum(f.getlength(w) for w in ws) + sp * (len(ws) - 1)
    if width(words) <= max_w or len(words) == 1:
        return [words]
    best = min(range(1, len(words)), key=lambda k: max(width(words[:k]), width(words[k:])))
    return [words[:best], words[best:]]


@lru_cache(maxsize=64)
def caption_image(text: str, big: bool, key: tuple = (255, 214, 64), key_stroke: int = 0, ink: tuple = INK,
                  stroke_add: int = 0, shadow: float = 0.55) -> tuple[Image.Image, dict]:
    """The caption as an RGBA block, with its measurements for the layout check. A story's "caption" settings can
    darken the outline (ink), thicken it (stroke_add px) and darken the drop shadow (0..1), for a busy background."""
    px = BIG_PX if big else CAP_PX
    f = font(px)
    stroke = (9 if big else 7) + stroke_add
    lines = wrap(text.split(), f, MAX_W - 2 * stroke)
    sp = f.getlength(" ")
    lh = int(px * 1.08)
    widths = [sum(f.getlength(w) for w in ln) + sp * (len(ln) - 1) for ln in lines]
    bw = int(max(widths) + 2 * (stroke + key_stroke) + 24)
    bh = int(lh * len(lines) + 2 * (stroke + key_stroke) + 30)
    txt = Image.new("RGBA", (bw, bh), (0, 0, 0, 0))
    d = ImageDraw.Draw(txt)
    ascent = f.getmetrics()[0]
    for i, (ln, lw) in enumerate(zip(lines, widths)):
        x = (bw - lw) / 2
        y = stroke + key_stroke + 8 + i * lh
        for w in ln:   # a story can give its key words a thicker outline (red over bright wood)
            k = is_key(w)
            d.text((x, y), w, font=f, fill=key if k else WHITE, stroke_width=stroke + (key_stroke if k else 0),
                   stroke_fill=ink)
            x += f.getlength(w) + sp
    shadow_k = shadow
    shadow = Image.new("RGBA", txt.size, (0, 0, 0, 0))
    a = txt.split()[3].filter(ImageFilter.GaussianBlur(7))
    shadow.putalpha(a.point(lambda v: int(v * shadow_k)))
    out = Image.new("RGBA", (bw, bh + 10), (0, 0, 0, 0))
    out.alpha_composite(shadow, (0, 8))
    out.alpha_composite(txt, (0, 0))
    cap_h = f.getbbox("H")[3] - f.getbbox("H")[1]
    return out, {"lines": len(lines), "cap_h": cap_h, "w": bw, "h": bh, "words": len(text.split())}


def caption_box(cap: dict) -> tuple[int, int, int, int]:
    big = cap.get("big", False)
    im, m = caption_image(cap["text"], big)
    x0 = int(CX - im.width / 2)
    y0 = int(CY - im.height / 2)
    return x0, y0, x0 + im.width, y0 + im.height


def layout_problems(caps: list[dict]) -> list[str]:
    out = []
    for c in caps:
        im, m = caption_image(c["text"], c.get("big", False))
        x0, y0, x1, y1 = caption_box(c)
        if m["cap_h"] < 56:
            out.append(f"{c['text']!r}: cap height {m['cap_h']} px < 56")
        if m["lines"] > 2:
            out.append(f"{c['text']!r}: {m['lines']} lines")
        if m["words"] > 3:
            out.append(f"{c['text']!r}: {m['words']} words (2 or 3 at a time)")
        if x1 - 12 > SAFE_RIGHT or x0 < 0:
            out.append(f"{c['text']!r}: x {x0}-{x1} runs into the right 15%")
        if y1 > SAFE_BOTTOM:
            out.append(f"{c['text']!r}: bottom {y1} in the bottom 20%")
    return out


def pop(u: float) -> float:
    """Scale for a caption's entrance: 0.84 -> 1.06 -> 1.0 over 0.16 s."""
    if u >= 1:
        return 1.0
    if u < 0.6:
        return 0.84 + (1.06 - 0.84) * math.sin(u / 0.6 * math.pi / 2)
    return 1.06 - 0.06 * (u - 0.6) / 0.4


def draw_captions(img: Image.Image, t: float, caps: list[dict], shake: float = 0.0, quick: bool = False) -> None:
    """quick: the polish pack's pop-in (90 to 100% over 80 ms) instead of the default overshoot."""
    for c in caps:
        if not (c["start"] <= t < c["end"]):
            continue
        im, _ = caption_image(c["text"], c.get("big", False), KEY["c"], KEY.get("stroke", 0), KEY.get("ink", INK),
                              KEY.get("stroke_add", 0), KEY.get("shadow", 0.55))
        k = polish.caption_scale(t - c["start"]) if quick else pop((t - c["start"]) / 0.16)
        if k != 1.0:
            im = im.resize((max(1, int(im.width * k)), max(1, int(im.height * k))), Image.BICUBIC)
        dx = dy = 0
        if shake:
            r = np.random.default_rng(int(t * 1000))
            dx, dy = (r.uniform(-1, 1, 2) * 10 * shake).astype(int)
        img.alpha_composite(im, (int(CX - im.width / 2 + dx), int(CY - im.height / 2 + dy)))


def _meter_val(cs: list, t: float, key: str) -> float:
    vals = [c for c in cs if key in c and c["t"] <= t + 1e-9]
    if not vals:
        return 7.0 if key == "me" else 4.0
    cur = vals[-1]
    prev = vals[-2][key] if len(vals) > 1 else cur[key]
    d = cur.get("dur", 0.0)
    u = min(1.0, max(0.0, (t - cur["t"]) / d)) if d > 0 else 1.0
    u = u * u * (3 - 2 * u)
    return prev + (cur[key] - prev) * u


def draw_meter(img: Image.Image, t: float, tl: dict) -> None:
    """Opt-in (ep28): cues named "meter" ({"me": 7, "ines": 4, "dur": 0.4}, in stair turns) draw a small tower glyph
    top-left, outside the caption band, with seven ticks and a sea-glass dot (me) and a blue dot (Ines) on them.
    Only cues that carry a me or ines value count, so another story's own "meter" cue can't switch the panel on
    (warm-shoes' chalk override drew it over its slate, 2026-11-06)."""
    cs = [c for c in tl.get("cues", []) if c["name"] == "meter" and ("me" in c or "ines" in c)]
    if not cs:
        return
    k = 3
    pw, ph = 230, 260
    pat = Image.new("RGBA", (pw * k, ph * k), (0, 0, 0, 0))
    d = ImageDraw.Draw(pat)

    def R(x0, y0, x1, y1, **kw):
        d.rounded_rectangle([x0 * k, y0 * k, x1 * k, y1 * k], **kw)

    R(0, 0, pw - 1, ph - 1, radius=22 * k, fill=(10, 14, 24, 150))
    cream = (240, 232, 214, 255)
    d.polygon([(c_[0] * k, c_[1] * k) for c_ in ((46, 70), (74, 70), (84, 235), (36, 235))], fill=cream)   # tower
    d.polygon([(c_[0] * k, c_[1] * k) for c_ in ((42, 70), (78, 70), (60, 50))], fill=(200, 70, 60, 255))   # roof
    R(48, 58, 72, 70, radius=3 * k, fill=(255, 214, 110, 255))                                               # lamp
    top, bot = 80, 225
    for n in range(1, 8):
        y = bot - (n - 1) / 6 * (bot - top)
        d.line([(92 * k, y * k), (120 * k, y * k)], fill=(240, 232, 214, 255), width=3 * k)
    me, ines = _meter_val(cs, t, "me"), _meter_val(cs, t, "ines")
    for val, col, x in ((ines, (96, 150, 255, 255), 152), (me, (110, 224, 190, 255), 188)):
        y = bot - (val - 1) / 6 * (bot - top)
        d.ellipse([(x - 13) * k, (y - 13) * k, (x + 13) * k, (y + 13) * k], fill=col, outline=(8, 12, 20, 255), width=3 * k)
    pat = pat.resize((pw, ph), Image.LANCZOS)
    img.alpha_composite(pat, (36, 120))


# ----------------------------------------------------------------------------------------- the image


def _blur(a: np.ndarray, r: float) -> np.ndarray:
    im = Image.fromarray(np.clip(a * 255, 0, 255).astype(np.uint8))
    return np.asarray(im.filter(ImageFilter.GaussianBlur(r))).astype(np.float32) / 255


def bloom(img: np.ndarray, amount: float = 0.35, thresh: float = 0.6) -> np.ndarray:
    h, w = img.shape[:2]
    luma = img @ np.array([0.2126, 0.7152, 0.0722], np.float32)
    k = np.clip((luma - thresh) / (1 - thresh), 0, 1)[..., None]
    small = np.asarray(Image.fromarray(np.clip(img * k * 255, 0, 255).astype(np.uint8)).resize((w // 4, h // 4), Image.BILINEAR)
                       ).astype(np.float32) / 255
    g = _blur(small, 3) * 0.6 + _blur(small, 10) * 0.9
    up = np.asarray(Image.fromarray(np.clip(g * 255, 0, 255).astype(np.uint8)).resize((w, h), Image.BILINEAR)
                    ).astype(np.float32) / 255
    return img + amount * up


def sharpen(img: np.ndarray, amount: float) -> np.ndarray:
    """An unsharp mask (radius 1 px at 1080 x 1920, `amount` 0.4 = 40%, no threshold) on a float frame."""
    im8 = Image.fromarray(np.clip(img * 255 + 0.5, 0, 255).astype(np.uint8))
    return np.asarray(im8.filter(ImageFilter.UnsharpMask(radius=1.0, percent=int(round(amount * 100)), threshold=0))
                      ).astype(np.float32) / 255


@lru_cache(maxsize=4)
def _vignette(h: int, w: int, amount: float) -> np.ndarray:
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    r = np.hypot((xx - w / 2) / (w / 2), (yy - h / 2) / (h / 2))
    return (1.0 - amount * np.clip(r - 0.4, 0, None) ** 1.5)[..., None]


LIFT_SCALE_MAX = 3.0   # the most the polish lift may scale a pixel; the rest of its lift is added as grey


def grade(img: np.ndarray, g: dict) -> np.ndarray:
    """The story's look: shadows and highlights tinted, contrast around mid-grey, saturation, vignette."""
    luma = (img @ np.array([0.2126, 0.7152, 0.0722], np.float32))[..., None]
    sh = np.clip(1 - luma * 2.2, 0, 1)
    hi = np.clip(luma * 1.6 - 0.6, 0, 1)
    out = img * (1 + sh * np.array(g.get("shadows", [-0.03, 0.0, 0.06]), np.float32)
                 + hi * np.array(g.get("highlights", [0.04, 0.01, -0.04]), np.float32))
    sat = g.get("saturation", 1.0)
    if sat != 1.0:
        out = luma + (out - luma) * sat
    c = g.get("contrast", 1.05)
    out = 0.5 + (out - 0.5) * c if c != 1.0 else out
    out = out * g.get("exposure", 1.0)
    if g.get("lift"):   # the polish grade's toe: the darkest tones come up, so a TV doesn't crush them. It scales each
        # pixel by the lift of its luma, so the colour keeps its saturation (adding grey washed it out: ep62, 0.19)
        # Clamp first: contrast can push a dark pixel's channels below zero, and then its luma sits near the 1e-4
        # floor, so l1 / l0 ran to about 1000x and blew the one positive channel up to pure red (ep47 r8, 2026-11-03).
        # The scale is capped, and whatever lift it can't give comes in as grey, so near-blacks lift without colour.
        out = np.clip(out, 0.0, None)
        l0 = np.clip(out @ np.array([0.2126, 0.7152, 0.0722], np.float32), 1e-4, None)[..., None]
        l1 = l0 + g["lift"] * np.clip(1 - l0, 0, 1) ** 3
        k = np.minimum(l1 / l0, LIFT_SCALE_MAX)
        out = out * k + (l1 - l0 * k)
    return out * _vignette(*img.shape[:2], g.get("vignette", 0.35))


def _to_lin(a: np.ndarray) -> np.ndarray:
    a = np.clip(a, 0.0, 1.0)
    return np.where(a <= 0.04045, a / 12.92, ((a + 0.055) / 1.055) ** 2.4)


def _to_srgb(a: np.ndarray) -> np.ndarray:
    a = np.clip(a, 0.0, 1.0)
    return np.where(a <= 0.0031308, a * 12.92, 1.055 * a ** (1 / 2.4) - 0.055)


def red_clamp(img: np.ndarray, line: float = 0.78, blue: float = 0.25) -> np.ndarray:
    """Keep every pixel's linear red ratio R / (R + G + B) under `line`, by lifting green and blue just enough. WCAG
    counts a pixel at 0.8 or more as saturated red, so a warm grade (tungsten, oxblood, deep brown shadows) would
    turn every cut into a red flash. The lift is mostly green, so a deep red becomes a deep brick red."""
    lin = _to_lin(img)
    r = lin[..., 0:1]
    add = np.clip(r / line - lin.sum(axis=2, keepdims=True), 0.0, None)
    if not np.any(add):
        return img
    lin[..., 1:2] += add * (1.0 - blue)   # mostly green: an over-red pixel turns brick or rust, not mauve
    lin[..., 2:3] += add * blue           # (a story can lift more blue, so a crimson stays crimson)
    return _to_srgb(lin).astype(np.float32)


class Rain:
    """Streaks in three depths, falling a little to the left."""

    def __init__(self, seed: int = 3):
        r = np.random.default_rng(seed)
        self.layers = []
        for n, length, width, alpha, speed in ((70, 120, 3, 0.16, 3400), (180, 60, 2, 0.12, 2600), (360, 28, 1, 0.09, 1800)):
            self.layers.append((r.uniform(0, W, n), r.uniform(0, H, n), r.uniform(0.7, 1.3, n), length, width, alpha, speed))

    def draw(self, t: float, gain: float = 1.0) -> np.ndarray:
        im = Image.new("L", (W, H), 0)
        d = ImageDraw.Draw(im)
        dx, dy = -0.16, 1.0
        for x0, y0, sp, length, width, alpha, speed in self.layers:
            a = int(255 * min(1.0, alpha * gain))
            ys = (y0 + t * speed * sp) % (H + 200) - 100
            xs = (x0 + dx * t * speed * sp) % (W + 100) - 50
            for x, y in zip(xs, ys):
                d.line([(x, y), (x + dx * length, y + dy * length)], fill=a, width=width)
        return np.asarray(im).astype(np.float32)[..., None] / 255 * np.array([0.78, 0.85, 1.0], np.float32)


def _read(path: Path) -> np.ndarray:
    a = np.asarray(Image.open(path).convert("RGB"))
    return a.astype(np.float32) / 255


def to_output(a: np.ndarray, zoom: float = 1.0, dx: float = 0.0, dy: float = 0.0) -> np.ndarray:
    """A render at any size to 1080 x 1920 (a centred crop for a punch-in or a shake), Lanczos up, a light sharpen."""
    h, w = a.shape[:2]
    im8 = Image.fromarray(np.clip(a[..., :3] * 255 + 0.5, 0, 255).astype(np.uint8))
    if zoom > 1.0001 or dx or dy:
        z = max(zoom, 1.0 + 2 * max(abs(dx), abs(dy)) + 1e-3)
        cw, ch = w / z, h / z
        cx, cy = w / 2 + dx * w, h / 2 + dy * h
        im8 = im8.resize((W, H), Image.LANCZOS, box=(cx - cw / 2, cy - ch / 2, cx + cw / 2, cy + ch / 2))
    elif w != W:
        im8 = im8.resize((W, H), Image.LANCZOS)
    if w != W:
        im8 = im8.filter(ImageFilter.UnsharpMask(radius=1.4, percent=55, threshold=2))
    return np.asarray(im8).astype(np.float32) / 255


def drawing_for(tl: dict, f: int, frames_dir: Path) -> Path:
    """The rendered drawing for frame f: its own, or the last one before it in the same shot (shots on twos)."""
    s = next((x for x in tl["shots"] if x["f0"] <= f < x["f1"]), tl["shots"][-1])
    g = f
    while g > s["f0"] and not (frames_dir / f"f{g:05d}.png").exists():
        g -= 1
    if not (frames_dir / f"f{g:05d}.png").exists():
        g = f
        while g > 0 and not (frames_dir / f"f{g:05d}.png").exists():
            g -= 1
    return frames_dir / f"f{g:05d}.png"


def fx_at(tl: dict, t: float) -> dict:
    """The effects on at time t: flash (white), black, static, red, shake, punch (zoom), and their strength."""
    out = {"flash": 0.0, "black": 0.0, "static": 0.0, "red": 0.0, "shake": 0.0, "punch": 1.0}
    for e in tl["fx"]:
        x = t - e["t"]
        d = e.get("dur", 0.25)
        if x < 0 or x > d + e.get("fade", 0.0):
            continue
        a = e.get("amp", 1.0)
        if x > d:  # fading out
            a *= 1 - (x - d) / max(1e-6, e.get("fade", 0.0))
        k = e["kind"]
        if k == "shake":
            out["shake"] = max(out["shake"], a * math.exp(-x * 4.0))
        elif k == "punch":
            u = min(1.0, x / 0.12)
            out["punch"] = max(out["punch"], 1 + (e.get("zoom", 1.15) - 1) * u)
        elif k == "flash":
            out["flash"] = max(out["flash"], a * math.exp(-x * 10.0))
        else:
            out[k] = max(out[k], a)
    return out


_EMPH: dict = {}   # the polish punch-in times, worked out once per film


def finish(tl: dict, st: dict, f: int, raw: Path, rain: Rain | None = None, grain_seed: int = 0) -> np.ndarray:
    t = f / tl["fps"]
    KEY["c"] = tuple(int(st.get("key_color", "#ffd640").lstrip("#")[i:i + 2], 16) for i in (0, 2, 4))
    KEY["stroke"] = int(st.get("key_stroke", 0))
    cs = st.get("caption", {})
    KEY["ink"] = tuple(int(cs["ink"].lstrip("#")[i:i + 2], 16) for i in (0, 2, 4)) if cs.get("ink") else INK
    KEY["stroke_add"] = int(cs.get("stroke_add", 0))
    KEY["shadow"] = float(cs.get("shadow", 0.55))
    fx = fx_at(tl, t)
    dx = dy = 0.0
    if fx["shake"]:
        r = np.random.default_rng(f)
        dx, dy = r.uniform(-1, 1, 2) * 0.012 * fx["shake"]
    pol = polish.spec(st)
    zoom = fx["punch"]
    if pol:   # the polish pack's punch-ins, drift and sway, on the crop (smooth on every frame, drawings on twos)
        key = (id(tl), id(st))
        if key not in _EMPH:
            _EMPH.clear()
            _EMPH[key] = polish.emph_times(tl, pol)
        pz, pdx, pdy = polish.motion(tl, st, pol, t, _EMPH[key])
        zoom, dx, dy = zoom * pz, dx + pdx, dy + pdy
    img = to_output(_read(raw), zoom, dx, dy)
    g = st.get("grade", {})
    sid = next((s["id"] for s in tl["shots"] if s["start"] <= t < s["end"]), tl["shots"][-1]["id"])
    if st.get("shot_grades", {}).get(sid):      # opt-in (ep42): a shot's own grade over the story's (a flashback is warmer)
        g = {**g, **st["shot_grades"][sid]}
    if pol:
        g = polish.grade(g, pol)
    img = bloom(img, g.get("bloom", 0.35), float(pol.get("bloom_thresh") or 0.6) if pol else 0.6)
    img = grade(img, g)
    if pol and pol.get("sharpen"):   # opt-in (animation audit 2026-11-12): an unsharp mask after the grade, before grain
        img = sharpen(img, float(pol["sharpen"]))
    if rain is not None and sid in set(st.get("rain_shots", [])):
        img = 1 - (1 - img) * (1 - rain.draw(t, st.get("rain_gain", 1.0)))
    if fx["red"]:
        luma = (img @ np.array([0.2126, 0.7152, 0.0722], np.float32))[..., None]
        img = img * (1 - fx["red"]) + fx["red"] * luma * np.array([1.25, 0.18, 0.16], np.float32)
    if fx["static"]:
        r = np.random.default_rng(f * 7 + 1)
        n = r.random((H // 4, W // 4)).astype(np.float32)
        n = np.asarray(Image.fromarray((n * 255).astype(np.uint8)).resize((W, H), Image.NEAREST)).astype(np.float32)[..., None] / 255
        img = img * (1 - 0.6 * fx["static"]) + n * 0.6 * fx["static"]
        rows = r.integers(0, H, 6)
        for y in rows:  # a few torn lines
            img[y:y + 6] = np.roll(img[y:y + 6], int(r.integers(-60, 60)), axis=1)
    if fx["flash"]:
        img = img * (1 - 0.7 * fx["flash"]) + 0.7 * fx["flash"]
    if fx["black"]:
        img = img * (1 - fx["black"])
    n = tl["frames"]
    if tl.get("tail", 1.0) > 0:   # a fade in and out; a film with no tail is a loop, so neither end goes dark
        img = img * min(1.0, (f + 1) / 4 if tl.get("fade_in", True) else 1.0, (n - f) / 6 if tl.get("fade_out", True) else 1.0)
    rng = np.random.default_rng(grain_seed * 100003 + f)
    gr = rng.normal(0, g.get("grain", 0.012), img.shape[:2]).astype(np.float32)[..., None]
    img = img + gr * (0.4 + 0.6 * img)
    if g.get("red_line"):   # a warm story's picture stays under WCAG's saturated red (the captions are drawn after)
        img = red_clamp(img, g["red_line"], g.get("red_lift_blue", 0.25))
    out = Image.fromarray(np.clip(img * 255 + 0.5, 0, 255).astype(np.uint8)).convert("RGBA")
    draw_meter(out, t, tl)
    draw_captions(out, t, tl["captions"], fx["shake"] * 0.6, quick=bool(pol and pol["pop"]))
    return np.asarray(out.convert("RGB"))


_JOB: dict = {}


def _init(tl, st, frames_dir, rain):
    _JOB.update(tl=tl, st=st, frames_dir=frames_dir, rain=rain)


def _frame(f: int) -> bytes:
    j = _JOB
    return finish(j["tl"], j["st"], f, drawing_for(j["tl"], f, j["frames_dir"]), j["rain"]).tobytes()


def encode(tl: dict, st: dict, frames_dir: Path, out: Path, threads: int = 2, crf: int = 17,
           workers: int | None = None) -> None:
    """Finish every frame and encode. Frames are finished in parallel worker processes (every effect is seeded by
    the frame number, so the picture is identical to finishing them one by one) and written in order."""
    import multiprocessing as mp
    import os

    workers = workers or int(os.environ.get("BLOCKY_POST_WORKERS", 0)) or os.cpu_count() or 1
    proc = subprocess.Popen(
        ["ffmpeg", "-nostdin", "-loglevel", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r",
         str(tl["fps"]), "-i", "-", "-c:v", "libx264", "-preset", "medium", "-crf", str(crf), "-pix_fmt", "yuv420p",
         "-threads", str(threads), "-g", str(tl["fps"] * 2), "-an", str(out)], stdin=subprocess.PIPE)
    rain = Rain() if st.get("rain_shots") else None
    if workers <= 1:
        _init(tl, st, frames_dir, rain)
        frames = map(_frame, range(tl["frames"]))
        pool = None
    else:
        pool = mp.get_context("fork").Pool(workers, initializer=_init, initargs=(tl, st, frames_dir, rain))
        frames = pool.imap(_frame, range(tl["frames"]), chunksize=4)
    try:
        for b in frames:
            proc.stdin.write(b)
    finally:
        if pool is not None:
            pool.close()
            pool.join()
    proc.stdin.close()
    if proc.wait() != 0:
        raise RuntimeError("ffmpeg failed")
