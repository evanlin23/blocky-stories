# ep148-frozen-seconds, round 3 (rescue check), critic

I checked the two round-2 must-fixes in the new preview, at full size and at phone size (300 px).

## Round-2 must-fixes
1. **S15b, L15 (22.2 to 23.9 s): fixed.** The camera is close and level on the green shirt and the dark pocket mouth. The cream note now has a visible fold line. It slides in from the left (22.3 to 23.3 s), sits whole and in frame over the pocket mouth (23.45 to 23.55 s, about half the frame width), then is gone into the pocket (23.65 s on). It stays above the caption band the whole time. "goodbye NOTE / into his POCKET" lands on the picture.
2. **S16b, L16 (25.9 to 26.7 s): fixed.** The pretzel on the napkin is round and whole, with no notch (26.0 and 26.6 s). The chain now reads whole (S16b), whole (S20, 30.3 s), whole (S22a, 33.0 s), then bitten (S24, 36.5 s, a clear notch). The pin's clue holds.

## Regressions
- None severe. S15a (21.5 s), S16a (25.0 s) and S17a (27.0 s) are unchanged and read. The tally marks still show under the S16b napkin.

## Should-fix (not blocking)
- S15b, 22.4 to 22.9 s: the note's top edge covers half of the rule meter for about half a second. Lower the note's path by about a tenth of the frame.
- S15b, 23.55 to 23.65 s: the note sits in front of the pocket and then disappears in one step. A short sink behind the pocket edge would sell "into". The qa proof pass should check this at full frame rate.

Verdict: approve
