# ep129-gift-box staging fix: stopped (2026-11-07)

Branch `claude/ep129-gift-box-staging-fix`, PR #414 (not merged). The story on main (#406) is unchanged.

## What was fixed
`staging.py` found two places where me and Dad stood too close, with arms in bodies. Both are fixed on this branch:
- **S21:** 1.4 m apart, near arms in. The camera was pulled back from 3.8 to 4.8 m, with push 0.
- **S61:** ±0.7 m at the counter, arms down. The camera was pulled back from 4.8 to 5.8 m, with push 0.03.

`staging.py`, framing.py and frames.py all find nothing. Critic r4 said revise (S61 cropped the heads). One rescue (the S61 camera) followed, then critic r5 approved.

## Why it stopped
The proof qa (run 42345647821, `qa/ep129-gift-box.json`) failed on S21. The polish drift carries my head off the right edge from about 33.3 to 34.70 s. That's about 42 frames, about 9% of the head (hair and sideburn), under "my JOB. / I say / it's FINE.". Dad keeps only 1 to 5 px at the left edge. S61 and everything else pass.

The one rescue was already used, so per the round cap this goes back to the second orchestrator.

## The remaining fix (one line, mechanical)
In `generator/make_story.py`, change S21's `ocam("R1", 0.2, 1.6, 1.4, 4.8, 30, push=0.0, arc=0.0)` from distance 4.8 to 5.2, or take S21 out of the polish drift. Each head should then keep about 8% of the frame width at every frame from 32.87 to 34.70 s. Check it on the film at 270x480 (frames at 33.0, 34.0 and 34.6 s).

Then:
1. Run the timeline, `render --preview --force`, finish and mix.
2. Run framing, staging and measure.
3. Push, which draws a new proof.
4. Run the proof qa.
