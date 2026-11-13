# ep119-quiet-car, critic r5 (c1 corner fix, S12/S13 only)

Verdict: approve

Checked every drawing from 12.5 to 14.5 s in the full proof (run 43297516303, sha 44140d4, frames 375 to 435), and sampled c1 and c2 from the rebuilt timeline every frame.

- **The turn:** the old 68° one-frame flip is gone. c1's heading now changes in two smaller steps, 41° at 12.93 s and 35° at 13.40 s, with only 2° in between. Each lands when c1 is almost stopped and his legs are at rest, so on screen it reads as a step-turn toward the camera, not a spin. The second step is one frame before the cut and nothing pops.
- **No touching:** the closest c1 and c2 get is 1.27 m apart (centre to centre) at 14.0 s. At the S12 to S13 cut (13.43 s) they're 1.82 m apart. In S12 c2 passes behind c1's shoulder, which is depth, not overlap. In S13 she stays a clear body-width to his right the whole time.
- **End position:** c1 ends at (5.2, -2.6) and walks out of frame left at about 13.9 s, then c2 does the same. That leaves the open door empty for the last 0.5 s, on "around that CAR.", which reads as the long way round. Faces are to camera from 13.43 to 13.8 s, and nobody's head is cropped until they exit.
- **Feet:** leg phase follows the distance walked, and no frame shows a foot sliding. Preflight: 0 blocks, no clip or pace rows here.

## Should-fix (not blocking)
1. L07, c1, 13.37 to 13.60 s: c1 stops on the key at 13.38 s, bursts to about 10 m/s across the cut, then stops again at 13.58 s. That's 1.4 m in 0.2 s. The same stop-and-go was in the old path (its last leg ran 12 m/s), so this isn't new. Optional: move the `L07+1.15` key to `L07+1.3`, or drop it, so he keeps an even pace through the corner.
