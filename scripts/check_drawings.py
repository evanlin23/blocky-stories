"""Every drawing a film needs is there, before finish turns them into frames.

    python scripts/check_drawings.py <story> <frames dir>

A shot on twos draws every other frame, and `post.finish` reuses each drawing for the frame after it, so a complete
film has fewer PNGs than frames. This checks the drawings the timeline asks for (`timeline.frame_list`), not the
frame count: a missing shard still fails, a shot on twos doesn't. Exits 1 and names what's missing.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from blocky.timeline import frame_list  # noqa: E402


def missing(tl: dict, frames_dir: Path) -> list[int]:
    return [f for f in frame_list(tl) if not (frames_dir / f"f{f:05d}.png").exists()]


def main(argv: list[str] | None = None) -> int:
    story, d = (argv if argv is not None else sys.argv[1:])[:2]
    tl = json.loads((ROOT / "out" / "work" / story / "timeline.json").read_text())
    want = frame_list(tl)
    gone = missing(tl, Path(d))
    if gone:
        print(f"::error::{story} has {len(want) - len(gone)} of {len(want)} drawings ({tl['frames']} frames): "
              f"{len(gone)} missing, first {gone[:8]}. A draw shard is missing. No film is made from missing "
              f"drawings (finish would hold the frame before over each gap); the next plan draws it again.")
        return 1
    print(f"{story}: all {len(want)} drawings for {tl['frames']} frames are there")
    return 0


if __name__ == "__main__":
    sys.exit(main())
