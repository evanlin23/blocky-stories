# ep89-sister-diary, round 4 critic: rescue look (S58 only)

Checked the round-3 must-fix and any regressions it caused. I used the preview from 2026-11-07 02:24 UTC, commit f5d2f15, and pulled every frame from 63.9 to 66.2 s at 300 px.

## Round-3 must-fix 1: S58 / L40 opening (64.17 to 66.0 s): fixed
- Me now starts at X(-0.4, -0.7). In the first drawing (64.20 s) the whole head is in frame. About 25 px of wall shows above the hair at full size, so nothing is cut off. The blue back, arms and legs read plainly as me walking away on "So I went" at phone size.
- Brightness: S57 ends at 0.50 to 0.53. S58 opens at 0.31, then rises smoothly as he walks off: 0.33, 0.36, 0.38, 0.40 and on to 0.48. The bar was about 0.3, so it clears. It no longer reads as a blank frame.
- Motion: the figure gets smaller steadily and the legs swing, with no dart, slide or pop between drawings. The cut to "Her door" at 66.0 s is clean.
- Preflight: 0 blocks, and no pace or clip row on S57 to S59.

## Regressions
None that are severe.

## Should-fix (not blocking)
1. S58, 64.2 to 64.6 s: the rule meter (the diary icon, top right) sits over the right corner of me's head for the first few drawings. The meter still reads and so does the head. If you touch the shot again, start me about 0.1 m to the left (X(-0.5, -0.7)) so the meter sits over the wall.

Verdict: approve
