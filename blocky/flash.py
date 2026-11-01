"""Flash measure of a finished film (house bar, see safety.py): `python -m blocky flash <story> [--file mp4]`.

Decodes the mp4 at analysis size, runs `safety.house_report` with the story's cuts and `safety.wrap_report` on
the loop seam, and writes `<mp4>.flash.json`. The report's `description_line` is the line the description opens
with when the film has any flashing transition at all (or null). The upload workflow refuses a film whose
`house_bar.pass` is false.
"""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

import numpy as np

from blocky import safety


def decode_low(path: Path) -> np.ndarray:
    h, w = safety.LOW
    raw = subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-i", str(path), "-vf", f"scale={w}:{h}:flags=area",
                          "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.uint8).reshape(-1, h, w, 3)


def mmss(s: float) -> str:
    s = int(round(s))
    return f"{s // 60}:{s % 60:02d}"


def measure(mp4: Path, cuts: list[int] | None) -> dict:
    lum, red = [], []
    for f in decode_low(mp4):
        y, r = safety.frame_stats(f)
        lum.append(y)
        red.append(r)
    rep = safety.house_report(lum, red, cuts)
    rep["wrap"] = safety.wrap_report(lum, red)
    span = rep.get("general_span_s")
    rep["description_line"] = f"Flashing lights and fast cuts from {mmss(span[0])} to {mmss(span[1])}." if span else None
    rep["file"] = mp4.name
    rep["frames"] = len(lum)
    return _plain(rep)


def _plain(x):
    """numpy scalars and tuples to plain JSON."""
    if isinstance(x, dict):
        return {str(k): _plain(v) for k, v in x.items()}
    if isinstance(x, (list, tuple)):
        return [_plain(v) for v in x]
    if isinstance(x, np.generic):
        return x.item()
    return x


def run(mp4: Path, timeline: Path | None) -> dict:
    cuts = None
    if timeline and timeline.exists():
        tl = json.loads(timeline.read_text())
        cuts = [s["f0"] for s in tl["shots"][1:]]
    rep = measure(mp4, cuts)
    out = mp4.with_suffix(".flash.json")
    out.write_text(json.dumps(rep, indent=1))
    bar = rep["house_bar"]
    print(f"flash: {'PASS' if bar['pass'] else 'FAIL'} ({rep['frames']} frames) -> {out}")
    for k, ok in bar.items():
        if not ok:
            print(f"  failed: {k}")
    if rep["description_line"]:
        print(f"  description line: {rep['description_line']}")
    return rep
