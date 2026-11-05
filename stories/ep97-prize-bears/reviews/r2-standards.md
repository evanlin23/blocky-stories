# ep97-prize-bears: standards r2 (preview, fix round 1)

Verdict: approve

Round 1 must-fixes, checked against the new build:
1. **Flash, S05 to S07.** Fixed. The jackpot beacon is at half emission (`jackpot` 1.5, `jpbeam` 1.25), it spins at 0.35 rad/s instead of 0.9, S05b has `cfill=2.0`, and S06a's camera is moved off the door. The old run is gone.
2. **Flash, closet.** Fixed. The bulb swing is halved (set.py line 940). The worst 3f second is down from 9 to 8 flashes, and red is 0.
3. **Bear foot in the car.** Removed from set.py.
4. **Queue.** Still applies at merge: keep it at least 3 slots from floor-thirteen.

Re-check: the words are fine. L03, L05, L34 and L40 introduce no real names and none of the GRAPHIC, HARM or CHILD words. L34 repeating L03's "from whoever played LAST" works as a planted callback. The frames show only `CAL`, numerals and scribbled tags, with no cropped word, and every figure is an adult. The IP, opening (`confess`, which matches L01) and package all pass, the same as in r1.

**Flash margin.** The house bar passes (`house_bar.pass: true`). The worst general_3f extended run is 3.83 s from 37.87 s (S21a to S23a), against the 4.0 s bar. That is 4% of headroom, measured on a preview drawn every 4th frame, so the full-rate final could come out above the bar. I accept the margin rather than make it a must-fix, because the proof (proof.yml, full drawing rate) fails on the flash bar and blocks the merge. The upload also re-measures the film. The only risk is a failed proof, not an unsafe upload.

## Nice-to-have
- If the proof's general_3f extended run is 3.9 s or more, or the proof fails, lengthen the door swing in `cdoor("L22", 24.0, 85.0, 0.8)` to 1.6 s. Also match S21a and S21b's `cfill` to S22a so the white shirt and counter stop pumping between cuts.
- The title backup from r1 still stands.
