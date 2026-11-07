# ep129-gift-box: standards, build round 2 (r3)

Verdict: approve

This round only checks. I pulled frames at the r2 must-fix shots from the new preview (the times have moved a little, and S56 is now split into S56 and S56b).

## r2 must-fixes
1. **S24 (37.6 to 39.1 s) and S33 (51.3 to 52.8 s): fixed.** The bow sits under Dad's chin and the box is held at chest height. His arms come down at the sides of the box, and no tan block comes at the camera.
2. **S35 (54.7 to 56.3 s): fixed.** The checked blanket is in, and my arms are low and out of sight.
3. **S59 (92.9 to 94.7 s): fixed.** The open box is in frame at chest height and Dad's arms are low.
4. **S03 and S04 (4.5 to 8.5 s): fixed.** Mrs. Albee's arms are down at about 45, with her hands at the ends of the shoebox. Nothing is near her face.
5. **package.json `hold`: handled by the orchestrator's step after approval** (see the build brief). It still has to come out before merge.

## Regressions
None are severe. The five spot fills don't change over time. The flash pass (3180 frames) reads 1/s general, with no red and no 2/s run, and preflight shows 0 blocks. S55's head is now lit, and the S38b mantel has its box back.

## Should-fix (not blocking)
- The 3-frame flash count reads 3/s at 47.1 s, which is right at the limit. It comes from the quick S29, S30a, S30b and S31 cuts between mid-tone shots, not from the fills. Watch this on the Actions final. If it goes over, lengthen S30a or S30b by about 4 frames.
- S40 (63.4 to 65.3 s): the truck still doesn't read through the window at phone size.
- script.md line 17's Hold note goes stale once `hold` is removed.

## Queue spacing
ep129 isn't in `queue.txt` yet. The queue has no `ban` openings and ends on ep99 (`cost`), so ep129 (`ban`) can go anywhere without a same-shape neighbour. It's a sad family reveal, so keep it 3 or more slots from ep48-crazy-golf and ep89-sister-diary.
