"""The post sharpen after the grade and the bloom threshold (animation audit 2026-11-12). No Blender."""

import numpy as np
from PIL import Image, ImageFilter

from blocky import polish, post


def test_sharpen_after_grade_is_opt_in_and_sharpens():
    assert polish.DEFAULTS["sharpen"] == 0.0 and polish.DEFAULTS["bloom_thresh"] is None
    img = np.zeros((64, 64, 3), np.float32)
    img[:, 32:] = 0.6
    img = np.asarray(Image.fromarray((img * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(1.5))
                     ).astype(np.float32) / 255
    out = post.sharpen(img, 0.4)
    assert out.shape == img.shape
    lap = lambda a: float(np.var(np.diff(a[..., 1], n=2, axis=1)))   # the audit's sharpness measure, in 1-D
    assert lap(out) > lap(img) * 1.1
    assert abs(float(out[:, :20].mean()) - float(img[:, :20].mean())) < 0.01   # flat areas untouched
    mid = np.full((32, 32, 3), 0.7, np.float32)
    assert np.allclose(post.bloom(mid, 0.35, 0.85), mid)          # below the threshold: no glow
    assert not np.allclose(post.bloom(mid, 0.35, 0.6), mid)       # today's threshold glows it
