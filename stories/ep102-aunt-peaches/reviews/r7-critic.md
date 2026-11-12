# ep102-aunt-peaches, r7 critic (yaw-blend fix, S06 to S09 only)

I checked only the changed shots, frame by frame in proof-ep102-aunt-peaches (run 43287636858, sha 27990b3): f166 to f193 (S06), f194 to f227 (S07), f228 to f257 (S08, where the S09 turn now starts) and f258 to f281 (S09), at 200 px wide. I also read the carrier's yaw from `acting.state` at each frame.

1. **S06 'carbite' (close-up): still pops, not fixed.** The face holds at 0 degrees to f183, then jumps to 23 degrees at f184 (6.13 s) in one frame. After that it turns smoothly to the side by f193. The L03.2 key's 0.5 s blend starts at 5.97 s, before the L03.1 beat at 6.119 s, so the turn begins part-way through its curve. At phone size it reads as a twitch in a close-up.
2. **S07 'carwalk': pass.** The carrier walks to the right facing right (no moonwalk), then turns smoothly to the camera from f208 to f222. The legs follow the distance, so I see no foot slide.
3. **S08 to S09 'cargray' into 'carroute': pass.** The turn to -90 runs smoothly from f247 to f257, he walks left facing left, and he turns back to the camera from f268 to f279 as he slows down. The cuts at f258 and f281 are clean.

**Regressions:** none apart from item 1.

**Should-fix (not blocking):**
- S07, f214 to f221 (7.13 to 7.37 s): he turns to face the camera while still running at full speed, so for about 0.2 s his legs stride toward the lens while his body slides right, which reads as a slight crab. Setting `blend=0.3` on `go("carrier0", "L03.2+0.95", ...)` would put the turn inside the slow-down.

## Must-fix
1. Generator `make_story.py`, L03 (S06, 6.12 s): on `go("carrier0", "L03.2", [MX - 3.8, 1.5], ...)` change `blend=0.5` to `blend=0.33`. The turn then starts after the L03.1 key at 6.119 s and runs 0 to 90 degrees evenly over 10 frames, with no jump. Rebuild story.json (REV 13) and run the proof again.

Verdict: revise
