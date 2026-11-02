# ep26-last-skate: standards, round 6

Verdict: revise

Both round 5 faults are gone. S16 and S17 and S24 no longer show up, and the 1-frame worst is now 1 flash and 2 changes at 13.97 s. The new opening (L01 to L04, shots S01 to S06), L19b, L74 and the ribbon marker pass on fiction (no set text, no signs), on rules 2 and 3 (only adults, nobody young in peril), on IP, on originality and on rule 8. The preview flash reading is PASS, but the 3-frame reading sits at the cap: 3 flashes and 6 changes at 52.73 s, with a 0.83 s extended run from 48.67 s.

## Must-fix
1. **Flash, S26 to S31 (L25 to L28, 47.1 to 54.4 s).** The L25 dim-up (47.1 s, 1.5 s) is still rising when S27 starts at 48.27 s. As a result, the booth shot brightens on screen (luma 144 to 171) while its lower 40% clips to cream (36 to 44% of the frame above 200). It sits between S26 (127) and S28 (117). Then S30 cuts in bright, and the L28 dim starts on the S31 cut itself (53.63 s, luma 130 to 86). Make three changes. (a) Give S27 `"expo": 0.55`, the same as S30. (b) Shorten the L25 dim to `"dur": 1.0` so that it finishes inside S26. (c) Move the L28 dim to `"at": "L28+0.4"` so that S31 opens at S30's level. Then re-run the flash pre-check on S25 to S32.
2. **Package (RULES → Packaging).** `package.json` has no `shape` and no `cover_s`. The twist is a Skater keeping Pop's empty place, so add `"shape": "stand-in"`. That lets the upload keep it away from the other stand-in stories. Also add `"cover_s": 93.6` (S53, the Skater lit beside Nan, "was RIGHT").

## Nice-to-have
- S04 to S07 (7.0 to 10.3 s) cuts bright, dark, bright, dark about once a second (luma 137, 65, 126, 49), and Pop's head clips white in the car (S05). This is under the bar, but a softer key in the car would help.
