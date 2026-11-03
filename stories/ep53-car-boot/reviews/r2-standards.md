# ep53-car-boot: standards, round 2

Verdict: revise

I checked the preview (quarter-res, every 4th drawing) and preflight: 137.5 s, flash PASS, 0 blocks. Round 1 fixes 1, 2, 3 and 5 are in: L56 is "All WEEK, / Pip was waiting / on ME.", L69 is "Her chair / is EMPTY / on SUNDAYS now.", the S42 tarp strip is lit and `cover_s` is 83.3. Fix 4 also worked: 103.6 to 111.1 s now peaks at 2 flashes. Fiction, kids, IP, originality and package all pass. The set has no text, the bus blind and radio dial are blank, every cast member is an adult, nobody is hurt, the title is a statement and the description says "It's made up."

1. **Flashing, S41 to S42 (67.1 to 68.4 s): one cue time.** The S42 lighting fix created a new reading at the bar. The `tfill` cue at `"L35-0.3"` (t 67.12, 0.3 s) ramps the fill up while the S41 fog wide is still on screen. Mean luma goes 142 to 161 to 175 in 0.2 s, then the cut to the strip drops it to 145, and the cut to my face at 68.36 drops it to 103. The 3-frame reading at 68.23 s is now 3 flashes and 6 changes, both exactly at the bar, and the final gets measured fresh on Actions. Change that cue's `"at"` to `"L35"` so the fill turns up under the cut into S42 and S41 holds steady to its last frame. Keep the `L35.2` ramp down as it is. Re-run preflight and confirm the 3-frame figures at 67 to 69 s are below 3 and 6.

Nice-to-have: S55 (84.6 to 86.2 s, "like a COAT.", the tarp-knot close) is nearly black (luma 2 to 4) between shots at 38 and 21. It passes the flash reading, but nobody can see the knot. Giving it the S54 key would read better and remove a light drop.
