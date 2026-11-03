# ep53-car-boot: standards, round 3 (scoped: flashing)

Verdict: revise

I measured the current preview (137.5 s, house bar PASS). The round 2 peak at 68.23 s is gone: 67 to 69 s reads 2 flashes and 4 changes on the 3-frame reading. But removing the L35.2 cut means S42 now carries two `tfill` changes on screen.

1. **S42 opening, 67.43 to 67.63 s, `tfill` cue `"at": "L35"`.** The strip flickers. Mean luma goes 77, 118, 98, 118 in 0.2 s (1-frame transitions down, up, down, up, each 25 to 47% of the screen). The 1-frame reading from 66.67 s is 2 flashes, which is exactly the bar. Delete the `L35` cue and change the `L34` cue to `"to": 0.6, "dur": 1.0` so the fill is fully up before the cut. S42 should open steady. Confirm S41 shows no new transition.
2. **S42 end, 68.36 to 69.13 s, `tfill` cue `"at": "L35.2"`.** In round 2 this ramp sat under a cut. Now it plays on screen: luma goes 119, 99, 47, then 0 (full black for 0.37 s under "on the ARM."), then the cut to 115. That light drop starts 3 frames after the window above. In the final, which draws every frame, it can fall into that window and make 3 flashes. Change `"at"` to `"L36"` so the fill drops under the cut to the shelter.

Re-run preflight. Both readings at 66 to 70 s should be 1 flash or fewer.

On 109.93 s (3 flashes and 6 changes on the 3-frame reading): this is acceptable for the final. It comes from two hard cuts 0.87 s apart (S71 to S72 at 109.97, S72 to S73 at 110.83). Each cut brightens and darkens over 10% of the screen, so the 3-frame reading always scores it as exactly 3 changes, whatever the resolution. S72 is a static still with flat luma (131), so drawing every frame can't add a change. These shots haven't changed since round 2.
