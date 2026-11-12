# ep102-aunt-peaches, r9 critic (rescue recheck, head f5178583, REV 14)

Same numeric check as r8: `measure.load_timeline`, then `acting.state(tl, "carrier0", t)` yaw, x, y at every frame from 5.9 to 7.6 s (f177 to f228).

1. **r8 must-fix 1 (S06 holds, turn on the cut): in.** `make_story.py` line 220 is `[MX - 4.0, 1.5] ... yaw=90, blend=0.0, keep_yaw=True`. He stands still facing the camera to f193; yaw goes 0.1 to 90.2 degrees at f194.
2. **f194 is a cut:** S07 starts at f194 (6.467 s, L03.2). The camera changes from S06 (eye [196.6, -1.9, 1.8], 42 mm close-up) to S07 (eye [196.8, -4.6, 1.5], 34 mm wide tracking shot), so the turn is hidden by the cut.
3. **r8 must-fix 2 (stop facing right): in.** Line 221 is `yaw=90, keep_yaw=True`.
4. **Step check:** apart from the cut at f194, no frame steps more than 0.2 degrees. Pass.
5. **Crab check:** at every frame over 0.3 m/s (f195 to f222), facing matches travel within 1 degree. Pass.

**Regressions:** none. He ends S07 side-on rather than turning to camera. That reads fine on a pass-through walk, and he's hidden at L04.

Verdict: approve
