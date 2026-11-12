# ep102-aunt-peaches: r10 critic (round-2 check, S78 tree fix)

Verdict: approve

Checked against proof `proof-ep102-aunt-peaches` (run 43303761062, sha 5b891ca, 2175 frames, every drawing).

## The must-fix from the proof pass
- **S78, 67.10 to 68.27 s (f2013 to f2047), camera inside commontree_1.109: fixed.** I looked at all 35 frames. The trunk wedge is gone from f2013 to f2016, and no trunk or canopy is in the lens anywhere in the shot. Tree ra4 now stands at y 19.5, 5 m behind the camera start (y 24.5), and the camera looks +y, away from it.
- **clip.json:** `hits: []`, `cam: []`. The tree is no longer flagged. verdict.json passes.
- **Framing and subject:** they read as before. The teal car comes up the road, swings in past the fence post on "the TURN" and fills the bottom of the frame by "for the first time". The meter reads 12, the rows of trees sit behind, and the captions are clear.

## Regression sweep (cameras within 40 m of x 291)
I pulled frames from S22, S23, S24, S31, S32, S33, S42, S44, S45, S57, S62, S68 and S69. Nothing is clipped and there are no gaps or holes in the tree rows. S32, S33 and S68 start at (292, 26), facing +y, so the moved tree is behind them. S69 faces -x and the tree is out of frame.

`scripts/frames.py --film` on the proof finds one item: an S02 "pop" at 1.47 s. That is the rule meter ticking 411 to 412 on the cut, as intended, so it is not a defect.

## Must-fixes
None.

## Should-fix (not blocking)
None.
