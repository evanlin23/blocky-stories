# ep98-town-whistle, round 6 critic: S92 recheck (92b7e48)

Scope: only S92 / L69, the r5 must-fix. No Blender here (BLOCKY_BPY unset), so judged against the r5 proof (run 43241370119, sha 6c0f006) frame by frame.

## Checked
- **S92 timing in that proof:** about 117.47-119.30 s, camera eased with smoothstep from (0, 172, -26) to (0.8, 182, -29).
- **Where the old frames went black:** luma stays 26-33 through 119.00 s (eased v of about 0.93: y 181.3, z -28.8). The drop starts at 119.07 s (v 0.96, y 181.6) and goes near-black from 119.13 s (v 0.98, y 181.8, z -28.9).
- **The new end pose (0.8, 179.0, -27.5):** y 179 is where the old path was at v 0.7 (about 118.6 s, luma 29, under 16 on 22% of pixels). That's 2.6 units short of where the dark began, and 1.4 units higher. At 300 px the 118.6 s frame shows the pipe plainly, dark against the brown wall, under the 28 meter. Target and lens haven't changed, so the framing holds. Adding fill 0.3 (it was 0.0) only lifts the wall and the pipe more.
- So the whole new move stays inside the volume that was well lit in the proof. I'm confident the last drawings won't go near-black and that the pipe stays in view to the cut. The proof qa should confirm the luma on the drawn last 10 frames: wall and pipe above 25.

## Regressions
None expected. Only L69's end key and fill changed.

## Must-fix
None.

Verdict: approve
