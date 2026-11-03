# ep26-last-skate: standards, round 9

Verdict: revise

Round 8's fix is in. S29 now starts at `L26+0.3`, and nothing near 48.3 s counts any more. But the preview's 3-frame reading is 3 flashes and 6 changes at 52.73 s, which is the cap. The cause is the same as last round, two shots on: a short shot with a cut at each end. The L28 dim ramp is not part of it. Its downs (f1641 to 1650) begin 32 frames after the S31 cut and add nothing to the worst window. Fiction, rules 2 and 3, IP, originality and the package still pass.

## Must-fix
1. **Flash, S30 length (cuts at f1588 / 52.93 s and f1609 / 53.63 s).** S30 (Lenny's plain shirt, `"at": "L27.5"`) is only 21 frames (0.70 s). The cut into it from S29 (Pop at the table) lights about 25% of the frame and darkens about 14%. The cut out of it to S31 (high wide) lights about 36% and darkens about 21%. The 3-frame reading counts each cut as three alternating transitions (f1588 to 1590 and f1609 to 1611). Both cuts fall inside one 30-frame window, which makes 6 changes. Moving S31 later doesn't fix this, because that would push its cut into the L28 dim ramp. Instead, change S30's `"at": "L27.5"` to `"at": "L28-1.2"`. That starts S30 at about 52.45 s (f1574, during "He said,"), which makes it about 35 frames (1.17 s) long, and it still holds on the shirt through "It's on his SHIRT." I simulated this on the preview's frames (S30 from f1574), and the 3-frame reading falls to 3 changes near 52.7 s, with a film-wide maximum of 4. Re-run preflight and confirm the 3-frame reading between 52 and 55 s is at most 5 changes.

## Nice-to-have
- The builder's L25 to L28 pre-check missed this pair of cuts. Run the pre-check from L26 through L29 so that both cuts and the ramp are inside its range.
