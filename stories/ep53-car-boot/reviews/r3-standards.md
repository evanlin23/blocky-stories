# ep53-car-boot: standards, round 3 (confirmation, S42 only)

Verdict: approve

Scope: S42 (L35, 67.43 to 69.13 s) against my two round 3 must-fixes. Nothing else was re-reviewed. I measured the preview drawn at 03:17 UTC from the edits saved at 02:52 (committed as ea8121a). Preflight: flash PASS, 0 blocks.

Both fixes are in `story.json` and `generator/make_story.py`:
- The `L35` `tfill` cue is deleted, and `L34` is now `"to": 0.6, "dur": 1.0`.
- The ramp-down cue is now `"at": "L36"` (`"to": 0.0, "dur": 0.4`).

**Flicker at 67.43 s: gone.** Mean luma across S42 holds at 116 to 117 from the first frame to the last. The opening cut (171 to 116, one darkening) is the shot's only transition. On the 1-frame reading S42 has no transitions of its own. On the 3-frame reading it has only the cut, counted as one change down.

**Black fade at the end of S42: gone.** The last frame is 117. There is no drop under "on the ARM." The cut to S43 lands at 114, and the L36 ramp-down plays under the shelter shot without showing (S43 stays flat at 113 to 114). Windows from 66 to 69.5 s: 1-frame reading 0 flashes and 1 change, 3-frame reading 1 flash and 3 changes or fewer. Both are under the bar.

**S41: no new transition.** The fill now rises on screen through S41 (luma 143 to 170, 65.90 to 66.70 s, a soft brightening of the canopy in the fog). Every step goes the same way (up), so it merges with the S41 opening cut into a single change and can't pair into a flash. The two step-ups the preview's 1-frame reading logs at 66.30 and 66.43 s come from S41 being drawn every 4 frames. The final draws every frame, so this 1.0 s ramp is smooth (hard rule 7).

The new S42 push (end camera `[-1.115, 0.80, 0.73]`, lens 38.6) is gentle and keeps the strip and chair arm readable throughout.

I accepted 109.93 s in round 3, and that still stands.

No must-fixes.
