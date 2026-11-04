# moving-day: dropped from the pace fix (2026-11-04)

Final qa failed on pace only (11.2 against 12.5 picture changes per 10 s, 10.9 against 14.0 at 0.25 s).
Branch `claude/moving-day-pace` split the still beats S16 to S38 and S52 into more angles and real moves, and
cut polish `quiet` to `[["P02","P02"]]`. It also cut S36c, ran S36b from 53.2 to 55.1 s with a push, and gave the
S42 clock wide a slow push. On the redrawn preview all 4 craft blocks pass: 13.8 per 10 s (bar 12.5), 14.5 at
0.25 s (bar 14.0), motion energy 7.41 (bar 6), longest still 0.8 s (limit 1.0). Preflight shows 0 blocks and
clipcheck 0. All tests pass.

**Dropped** because the last allowed critic look (r12) still says revise, and no rounds are left:
- S36b, 53.5 to 55.1 s: the push goes into the forearms, the hand ends drop below the quilt line, and the frame
  becomes two dark slabs (the "table leg" again). The fix is to reverse it: a slow pull back of about 0.4 m, or a
  lens about 4 mm wider, so the hands stay in frame and the face box comes into view.
- The preview cut between two low angles at 53.8 to 55.0 s. This is probably stale S36c drawings left in
  `out/work/moving-day/frames-preview` (only S42 was force-redrawn after the cut), so that part of the review may
  not hold for a clean render.

If the story is picked up again: make the S36b pull-back, clear `frames-preview`, redraw the whole preview, then
a critic look, the PR, the proof and proof qa. The 0.25 s margin is thin (14.5 against 14.0).
