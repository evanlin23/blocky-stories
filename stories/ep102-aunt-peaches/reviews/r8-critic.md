# ep102-aunt-peaches, r8 critic (rescue recheck, S06 to S07, head 53071bae)

No Blender here, so I checked numerically: `measure.load_timeline`, then `acting.state(tl, "carrier0", t)` yaw, x, y at every frame from 5.9 to 7.6 s (f177 to f228). Yaw is in radians, 0 faces -y, travel heading = atan2(dx, -dy).

1. **r7 must-fix (23 degree one-frame pop at f184): in.** The turn now starts after L03.1 (f184) with no jump.
2. **Per-frame step over 8 degrees: fails.** S06 f187 to f192 turns 10 to 13.5 degrees a frame (the 90 degree turn eased over 10 frames). S07 f216 to f221 turns 9.7 to 14.9 degrees a frame.
3. **Crab (facing vs travel over 30 degrees at over 0.3 m/s): fails twice.**
   - S06 f186 to f190 (6.20 to 6.33 s): the 0.2 m step right at 0.5 to 0.9 m/s while still facing the camera, off by 81 to 32 degrees. In a close-up.
   - S07 f218 to f222 (7.27 to 7.40 s): turning back to the camera while still moving right at 4.2 to 0.95 m/s, off by 43 to 89 degrees. `blend=0.3` put the turn in the slow-down but the slow-down is still fast.

## Must-fix
1. `generator/make_story.py` line 220: `go("carrier0", "L03.2", [MX - 3.8, 1.5], ..., yaw=90, blend=0.33, ...)` becomes `go("carrier0", "L03.2", [MX - 4.0, 1.5], ..., yaw=90, blend=0.0, keep_yaw=True)`. He holds still facing the camera through S06 and is facing right from the first frame of S07 (the yaw change lands on the cut at f194, not on screen).
2. Line 221: `go("carrier0", "L03.2+0.95", [MX + 1.2, 1.5], ..., yaw=0, blend=0.3)` becomes `yaw=90, keep_yaw=True` (drop the blend). He stops facing right; there are only 5 frames before he's hidden at L04, too few for a smooth turn to camera.

I ran both changes on a copy of the timeline: from f177 to f228 nothing steps more than 8 degrees within a shot, and nothing crabs. Rebuild story.json and run the proof again.

Verdict: revise
