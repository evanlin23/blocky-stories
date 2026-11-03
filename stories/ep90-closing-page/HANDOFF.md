# ep90-closing-page handoff (2026-11-03)

**STATUS: dropped** at the creature test (builder.md step 1: three tries at most). No full build, no voice, no reviews, no PR. `package.json` keeps its `"hold"`.

## Why
The Tallyman (a clerk made of price stickers with a red scanner-line face) never read as frightening at phone size. An Opus critic judged each still:
1. **Try 1: fix.** "A friendly toy robot in a sticky-note costume." Bright, flat overhead light, square-on stance, a pink visor like sunglasses, and a mouth line plus a bar-graph read-out that made a cute second face.
2. **Try 2: fix.** "A kid in a cardboard-box costume wearing a lime mailbox, marshmallow hands." The scanner rendered pink-white and the tilted head read as a stack of boxes.
3. **Try 3: fail.** "A cardboard-box mascot or a pile of shipping boxes." Flat tan-orange fills the frame, the scanner reads as a salmon visor, the green bib looks like a costume, and there's no shadow, red glow or silhouette. Fixing it means relighting, recolouring and reframing, which is more than a small fix.

## What's left for a future attempt
- `set.py` and `generator/make_story.py` (creature plus a bit of the back room only) are committed. The engine stills render to `out/work/ep90-closing-page/stills/` and are not kept.
- The core problem: a creature made entirely of warm orange, paper-like stickers reads as cardboard and costume in this blocky look. A rescue would need a new creature concept (a darker, non-paper material, a silhouette against light), not more tuning. That's a writer call, and the script's look also asks for bright, steady lighting.
- An engine note, not a bug: `python -m blocky stills --t 30` crashed because the stub shot was 1 s long. That's expected for a stub.
