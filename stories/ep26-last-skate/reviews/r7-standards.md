# ep26-last-skate: standards, round 7

Verdict: revise

All of round 6 is in. The booth shot (now S28) has `"expo": 0.55`, the L25 dim is `"dur": 1.0`, the L28 dim is at `"L28+0.4"`, and `package.json` has `"shape": "stand-in"` and `"cover_s": 93.6`. That cover now lands on S52 (the Skater lit beside Nan, "was RIGHT"), which is fine. Fiction, rules 2 and 3, IP, originality and rule 8 still pass. In the preview the 1-frame reading is 1 flash and 2 changes, but the 3-frame reading sits exactly at the cap: 3 flashes and 6 changes at 48.23 s.

## Must-fix
1. **Flash, S28 (L25.3 to L26, 48.27 to 49.13 s).** A final drawn at every frame won't fix this, because it isn't a sampling artefact. It's a real step inside the shot. Lenny's raised arm (`lenny` acting `L25.3`, arms [0, 100]) shades the booth ceiling. At `L25>` the arm drops with `"blend": 0.5`, and the ceiling lights up in one drawing at 48.73 s (luma 117 to 133, dark share 29% to 18%). Add the two cuts on either side (139 to 120 at 48.27 s, 120 to 139 at 49.13 s) and the window holds 6 changes with no margin. The final is measured at 540x960 on Actions, so one more counted change fails the upload. The fix is to change Lenny's `{"at": "L25>", "arms": [0, 0], "blend": 0.5}` to `"at": "L26"`. The arm then stays up for all of S28 and drops off screen during S29 (Pop), before S30 shows the booth at 52.93 s. After that, re-run the flash pre-check on S26 to S30 and confirm the 3-frame reading at about 48.2 s is at most 5 changes.
