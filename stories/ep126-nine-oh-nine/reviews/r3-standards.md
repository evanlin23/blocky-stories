# ep126-nine-oh-nine: standards, round 3 (build check of the r2 must-fixes)

## Round 2 must-fixes
1. **S21 to S22 (31.8 to 33.6 s):** fixed. Grandma is in moon shadow. Her eyes and red lipstick read, but she isn't easy to name, and she's fully lit from S23 at "It was GRANDMA."
2. **S41 (62.63 to 63.63 s):** fixed. The whole cream radio sits low in frame and Grandpa's hand comes in from the left. Checked on picture-flash.mp4.
3. **S35 (53.0 to 54.4 s):** fixed. The street wide has no void, and S36's bare roof is the set, not a gap.
4. **`hold` in package.json:** handled at approval, as the build brief says. `cover_s` 50.8 falls in S33, which is fine.

## Regressions
None severe. The tags at S07 to S10 read 8:50, 8:52, 9:01 and 9:09. The S12b shade slides with no blink. S43 is a wide with two faces at most. Preflight flash: PASS at a peak of 1 a second, no red. Nothing blinks, pulses or flickers, there's no profile two-shot, and there are no real words.

## Should-fix (not blocking)
1. **Preview, 49 to 69 s:** the preview mp4 mixes in 87 stale frames from the 22:15 render (f01472 to f02077) left in `frames-preview/`. Shots alternate every few frames (S41 and S42 swap at 62.5 to 63.9 s, for example). picture-flash.mp4, the one that gets measured, is clean all the way through, and the final renders fresh on Actions. So this is a preview artifact only. Clear `frames-preview/` before you build any more previews.

Verdict: approve
