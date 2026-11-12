# ep98-town-whistle, round 5 critic: proof check of the qa fixes

Scope: only the changed shots (S92, S66, the S05/S06/S08 yaw fixes) and anything they caused. Source: `proof-ep98-town-whistle` from proof.yml run 43241370119 (sha 6c0f006, 3836 drawings, every frame), read frame by frame at 30 fps, about 150 to 270 px wide, plus per-frame luma.

## Checked
- **S66 (89.83-90.23 s): fixed.** Lamp 0.5 and fill 0.7. The wall is warm cream with a gradient. Only 0.2% of pixels have every channel at 250 or above (the meter and caption), and that holds on every frame. The rail and step edge read. Nothing clips.
- **S05 baker turn (~7.0-7.6 s): fixed.** He turns from the oven to the camera over about 6 drawings with in-between angles, then walks in facing his heading. No snap.
- **S06 team (7.7-8.6 s): fixed.** t1 to t4 face the camera, the way they walk, from their first drawing to the cut. No snap.
- **S08 mail carrier (10.6-11.6 s): fixed.** She has her back to the camera the whole walk to the door, matching her heading. No snap.
- **S92 (118.8-119.27 s): NOT fixed.** The first 0.3 s are dim brown, with the pipe dark against the wall. From 119.07 s the picture sinks: the share of pixels with luma under 16 goes 31% at 119.07, 52% at 119.10, 82% at 119.13 and 89 to 96% at 119.17-119.27. The last 5 or 6 drawings are near-black, and even brightened the pipe has merged into flat dark. Then there's a hard cut to the bright L01 basement. Moving from z -31.5 to -29 only made the drop shorter.

## Regressions
None. preflight clip: 0 hits. The flash verdict passes (max 3/s at 9.23 s, not in a changed shot).

## Must-fix
1. **S92 / L69, 119.07-119.27 s:** keep the last 0.25 s off black. Either stop the camera higher, end at `(0.8, 179.0, -27.5)` with the same target, or give L69 `fill=0.3` so the wall and pipe stay above luma 25 up to the cut. The pipe has to be visible on the last drawing.

Verdict: revise
