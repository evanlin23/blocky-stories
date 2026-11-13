# ep146-one-percent: standards, round 2

Verdict: approve

Checked the round-1 must-fixes against the redrawn picture (picture-flash.mp4, after commit 4d723ac4) and pulled one frame per shot (32 shots) at phone size to look for regressions.

## Round-1 must-fixes
1. **Description:** fixed. It now says "a silly bet the two of us made three years ago", with no boat bet.
2. **S20 (36.4 to 38.4 s):** fixed. The white charger brick sits on Dex's raised hand at chest height, and there is no cable. It reads as held up, with nothing floating.
3. **`hold`:** still in package.json. The team removes it at the approval step (build brief), so it does not block. It must be gone before the gate.
4. **Opening:** still `cost`. The batch orchestrator decided to keep it, so it does not block. See should-fix.

## Regressions
- Flash: preflight PASS (1201 frames), max 1 per second, no red, ep10 bar met. Pass.
- Fiction, kids themes, IP: no change. Screens show glyphs only, there is no set text, and every figure is an adult. Pass.
- Originality: no change. Pass. Keep it 7 or more slots from ep143.
- Moving the tally post: it is clear of every phone shot, and no frame is flat or broken. `check`: no problems.

## Should-fix (not blocking)
- The opening mix is still 5 `cost` out of 14 in batch 15. L01 already reads as `must`, so `"opening": "must"` would fix the ratio with no change to the line.
- From round 1: the S13b call glyph still reads a little like a bone at phone size.
