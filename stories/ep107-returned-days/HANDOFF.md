# ep107-returned-days: HANDOFF (dropped after the one retry, batch 10)

**Status: dropped.** The proof failed the flash bar after both review rounds and the single rescue were spent (RULES audit decisions 3 and 7).

## Verdicts
- Standards r1: approve.
- Critic: r1 revise (picture: S34, S35, S56, S58, S107, S139, S126), r2 revise (one fix: `grin` read angry on L68/L69, rescued to `smile`), r3 approve (avg ~7.3, nothing under 5).
- check, gate (OPEN) and pytest (201) were green; PR #293 `test` failed only on the merge gate (no qa file yet).

## Proof (run 41976344532, sha 6b5b3717) FAILED on flash
- general flashes 7/s at 49.47 s (cap 6); the 3-frame meter shows a 4.87 s extended run from 47.23 s (bar under 4 s).
- Cause (standards r1 warned of it): the S25/S26 red-ring stamps (L24 to L26) flip between white and blue-green. The preview's full-rate flash check passed with 4/s; the proof's numbers are higher.
- Everything else in the proof was fine: -14.1 LUFS, -1.8 dBTP, clip 0 hits. The qa agent was never run.

## If revived
One concrete fix: keep the S25/S26 ring on one background (no white/blue-green flip) in 46 to 51 s, then redraw the proof. Known non-blocking nits: S126 waiver (Dad off screen), S143 palm reads as a tan block, S67 and S18 near-blank walls, S87 eyes behind the shelf, S138 phone off frame.
