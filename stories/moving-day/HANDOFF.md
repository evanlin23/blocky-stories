# moving-day: pace fix handoff (2026-11-04)

Final qa failed on pace only (11.2 against 12.5 picture changes per 10 s, 10.9 against 14.0 at 0.25 s).
Branch `claude/moving-day-pace` splits the still beats S16 to S38 and S52 into more angles and real moves, and
cuts polish `quiet` to `[["P02","P02"]]`. Before the r10 fixes the preview measured 14.1 and 15.0, with cuts at
7.86 per 10 s (the bar is 8.0). Preflight shows 0 blocks and clipcheck 0 (narrow `clip_ok` for intended pillow,
quilt and doorway contacts). All tests pass.

r10 critic said revise on five shots, and one builder round fixed four of them. r11 critic still says revise on
**S36c** only (53.8 to 55.1 s, the 1.0 s silent hold): aimed up, it reads as one dark arm column, like a table
leg. The fix is one of two:
- pull the camera about 1 m back, use a lens of 22 mm or less, aim at about z 1.6 so the face box, both arm
  ends and the quilt are in frame; or
- cut S36c and run S36b from 53.2 to 55.1 s with a slow push.

That would be a third builder round, past the one extra round this session was allowed, so it stopped here. No
PR is open and the proof hasn't been drawn. After the S36c fix: a critic re-look, open the PR, and the proof's pace
numbers must clear the bars; then proof qa.
