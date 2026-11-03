# ep53-car-boot r3 critic (confirmation: S42 only)

Verdict: approve

Scope: S42 (L35, 67.43 to 69.13 s) only, against the r3 must-fix. Nothing else was re-checked. The earlier r3 findings still stand: r2 must-fixes 1 to 3 fixed, average 7.3.

**What I checked**
- `story.json` S42 key 1 is now `[-1.115, 0.80, 0.73]`, lens 38.6, with the same target. The preview (04:04 UTC) is newer than story.json (02:52 UTC).
- Per-frame luma (YAVG) in the preview: S42 holds 115.8 to 117.7 from 67.43 to 69.10 s, with no dip at all. At r3 it fell to about 29 by 68.8 s. S43 starts at 113.8 at 69.13 s, a gap of about 3, well within 40.
- Frames at 67.5, 68.3 and 69.05 s: the green strip runs the length of the frame and stays the brightest, clearest thing in it. The arm block fills the upper middle but never covers the lens. "on the ARM." lands on a lit, readable shot, and the cut to Pip at the shelter is clean.

**r3 must-fix**
1. L35, S42: fixed. The push no longer goes near-black, and S42 stays within 40 of S43 for the whole shot.

**Scores (unchanged from r3, avg 7.3)**
Hook 7, scare 7, creature 6, twist 8, lore 8, warm turn 8, shot variety 7, faces 7, sound 7, captions 8.

**Panel (change only)**
- Casual: the blink to dark at 68.8 s is gone, so nothing in S42 gives a reason to swipe.

**Note (not a must-fix, outside scope)**
- The cut into S42 at 67.43 s goes from 162 (S41) to 116, a step of 46. That is a darkening cut, not a flash, and it was there in r3 too. The flash measure passes. Only fix it if standards asks.

**Must-fix**
None.
