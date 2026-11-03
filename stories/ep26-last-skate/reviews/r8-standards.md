# ep26-last-skate: standards, round 8

Verdict: revise

Round 7's fix is in: Lenny's arm drop is at `L26`, and the step inside the shot is gone (S28 holds luma 135 to 137 across 48.27 to 49.07 s). But the preview's 3-frame reading is still 3 flashes and 6 changes at 48.23 s, right at the cap. Round 7 got the cause wrong. All six changes come from the two cuts around S28, and nothing inside the shot adds to them. Fiction, rules 2 and 3, IP, originality and the package still pass.

## Must-fix
1. **Flash, S28 length (cuts at f1448 / 48.27 s and f1474 / 49.13 s).** S27 to S28 (Pop to booth) and S28 to S29 (booth back to Pop) each light about 27% of the frame and darken about 19%. The 3-frame reading counts each of those cuts as three alternating transitions: f1448 to 1450 and f1474 to 1476. S28 is only 26 frames (0.87 s) long, so both cuts fit in one 30-frame window, which makes 6 changes. One more counted change on Actions fails the upload. The fix is to make S28 longer than 1 s. Change S29's `"at": "L26"` to `"at": "L26+0.3"`, which makes S28 35 frames (1.17 s). Then move Lenny's arm drop `{"at": "L26", "arms": [0, 0], "blend": 0.5}` to `"at": "L26+0.3"` as well, so the arm stays up for all of S28 and drops off screen. With the measured transitions moved 9 frames later, the window peaks at 3 changes. Re-run preflight and confirm the 3-frame reading near 48.3 s is at most 5 changes.
