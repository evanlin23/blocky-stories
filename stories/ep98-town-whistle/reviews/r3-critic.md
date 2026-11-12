# ep98-town-whistle, round 3 critic: staging-fix render check

Scope: only the changed shots and the five staging_ok calls, from the preview (consecutive frames at 8 to 15 fps, phone size).

## Changed shots
- **S05 baker (6.3-7.7 s): fixed.** No snap and no glide: a readable turn over about 0.3 s, then a short walk toward the lens. Should-fix: `gone("baker", "L05-0.05")` leaves one or two frames of an empty bakery before the cut at 7.67 s (he blinks out). Move it to `"L05"`.
- **S07 stair runners (8.5-10.2 s): fixed, nothing worse.** The four runners now run, not hop. Lamp off: the doorway light still keeps the shot bright and warm, not murky. No lens through a head (the r2 polish note at 9.4-9.6 s is gone). As before, the bodies fill the frame near the lens. That reads as a rush past, not a fault.
- **S33 me (48.3-49.8 s): fixed.** It's one smooth walk off to the left, with no jump back and no height pop.

## staging_ok calls
- **S36, S37 me+arlo: OK.** Two clearly separate heads with a gap between them. The shoulders meet at the frame bottom, but nothing passes through anything.
- **S66 me+dad: OK as staging.** Only Dad's body is in frame, so nothing overlaps. The shot is a hard-to-read diagonal slab at phone size, but it is unchanged and out of scope.
- **S94 dinner: OK.** Three seated people with distinct heads and shirts (green, red, blue). The shoulders touch but don't merge.
- **S82 me+dad (106.3-107.5 s): NOT OK.** The pair climb to stair 5, right under the camera at stair 4. From about 106.7 s, Dad's dusty white body is drawn across my torso. From about 106.8 s to the cut (about 0.7 s), the frame is two flat slabs, my pink shoulder and Dad's beige one, with no faces. Two people read as one block. The staging_ok text ("one shoulder; the other is out of frame") is wrong: both are in frame.

## Must-fix
1. **S82 / L62:** stop the climb short of the lens. Change both `raw("dad", "L62.1+0.2", pos=[stair(5)...])` and `raw("me", ...stair(5)...)` to `stair(8)` (same lanes, y 0.5 and -0.5). Both faces then stay whole and separate to the cut. Then drop the S82 entry from `staging_ok`, or re-justify it.

Verdict: revise
