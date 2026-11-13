# ep152 standards rescue check

Verdict: approve

This checks only round-2 must-fix #7, plus regressions (decision 8).

**Source note.** `ep152-future-late-preview.mp4` (20:23) is older than the fix commit 215d70e8 (20:35), so it still shows the round-2 picture. I checked S21a on `picture-flash.mp4` instead (20:52, drawn after the fix), with frames at 32.3, 33.0 and 33.7 s at phone size.

## Round-2 must-fix
7. **S21a, fixed.** A gold-rimmed watch dial sits at frame left, about 0.3 of the frame width. Its hour hand is just short of 12 and its minute hand is on 48, so it reads 11:48, and it sits above and left of the captions without overlapping them. The 11:58 kitchen clock stays in frame just above it, and my stunned face fills the right side. The shelf clock that read about 1:52 is gone, so "It was really 11:48." now reads, with the two times in one frame.

## Regressions
- Flash: preflight reads `flash: PASS (1352 frames)` on picture-flash.flash.json (20:52), and the --like-proof re-run passed. Preflight shows 0 blocks.
- Nothing new in S21a is broken, blank or unsafe.

## Should-fix (not blocking)
- At phone size, the orange sleeve under the dial looks more like a clock stand than a wrist. Showing more of the dark strap around the wrist, or tilting the dial slightly, would make it read as a watch.
- Re-run the preview so `ep152-future-late-preview.mp4` matches the current picture before the owner or critic looks at it.
