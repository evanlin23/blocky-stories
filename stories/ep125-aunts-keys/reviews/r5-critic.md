# ep125-aunts-keys, round 5 critic (rescue look, must-fix check only)

Scope: the r4 must-fix (S47 awake face) and the five checks asked for. I looked at every preview frame from 51.6 to 52.4 s and from 56.6 to 58.2 s, plus the REV 16 diff. I left the fountain, the lock glyph and the 76.5 s tag alone.

## Checks
- (a) **ASLEEP, eyes shut:** yes. S46 holds under "Fast ASLEEP." until the cut at 56.93 s, with the eyes shut on every frame.
- (b) **Awake face in the room shot:** yes. WNDP opens wide-eyed on its first frame (56.93 s) and holds through "I watched myself". **The r4 must-fix is fixed.**
- (c) **Hand on HANDLE:** yes. The HANDLE caption comes up at 57.50 s and the cut to the hand on the handle comes at 57.67 s, inside the word.
- (d) **S42 step at 51.7 to 52.3 s:** still smooth. The legs come toward the camera a little on every frame, with no slide or pop. The `L32.1+0.05` yaw change doesn't cause a jump.
- (e) **55.2 to 58.0 s:** no pops, no stale frames, and the framing is fine. The "I watched myself" caption shows on one frame (56.90 s) of the reveal before the cut. That's 33 ms with no visible clash, so it isn't a problem.

## Should-fix (not blocking)
1. **WNDP, about 57.33 to 57.43 s:** the eyes close for 4 frames mid-shot, during "I watched myself". It reads as a blink, but it's 0.13 s of shut eyes in the one shot meant to read as awake. If it's an auto-blink, suppress it for this shot (or hold `expr="wide"` to the cut).

Verdict: approve
