# ep98-town-whistle, round 4 critic: rescue look

Scope: the r3 must-fix (S82) and the r3 S05 should-fix, plus regressions. Consecutive preview frames at 10 to 15 fps, 106.0 to 107.6 s and 7.2 to 7.9 s, at about 300 px wide, plus out/ep98-rescue-sheet.png.

## r3 must-fix
1. **S82 / L62 (106.3-107.5 s): fixed.** In code, dad goes to stair(12) and me to stair(8) (lanes 0.5 and -0.5), the camera is at y -0.15 with F 17, and S82 is gone from `staging_ok`. In the preview, from the cut at about 106.3 s to 107.5 s, me's head (black cap, face, round eyes) stays whole and in frame. The cap top stops just under the meter, with no head cut. Dad sits back and to the left, with grey hair, a blue shirt and part of his face. He is occluded, not merged: he is a full stair-depth behind, and no arm passes through a body. At phone size the two read as two people, kept apart by hair colour and shirt colour. Dad's face is small and half hidden behind me's near arm in the last 0.5 s. That is acceptable. The line is "I got Dad up the stairs", so me leads and Dad follows, and it is far better than the old one-block frame.

## r3 should-fix
- **S05 baker: fixed.** He is in frame on every drawing up to the L05 cut at about 7.67 s. There are no empty-bakery frames.

## Regressions
None severe.

## Should-fix (not blocking)
- S82: the warm stair lamp grades me's red shirt to a salmon close to his skin tone. In the last frames his torso and arms read as one peach mass. A touch less `lamp` (1.0 to 0.8) or a cooler `fill` would bring the red back. This is cosmetic.

Verdict: approve
