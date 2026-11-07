# ep96-friend-card: r3 critic (render-correctness check, changed shots only)

Checked against `git diff 88585d3` (rev 8), the current preview (every drawn frame; strips of every 2nd frame over each move) at about 300 px wide, and out/ep96-fixes-sheet.png.

## QA desk flaws
- S08b: fixed. Maya and me_d no longer merge, no arm comes out of a shoulder. **Worse:** the framing is tighter for the gap: the pair now spans about 0.42 of the camera distance, up from 0.33. With the 0.12 push, Maya's face slides half out of frame on the left from about 0.25 s, and me_d's right side gets cut. This is the shot that introduces Maya ("MAYA. My best friend").
- S09a, S09b, S10a: fixed. Both faces whole, no merge.
- S10b: fixed. me_d's head edge touches the right side in the last frames, but both eyes still read (should-fix).
- S15a, S15b: fixed. There is a clear gap on the sofa and the faces are whole.
- S07c: fixed. The friend walks away in even steps, no 3 m jump.
- S16b: fixed. Nate walks in with stepping legs, no slide.
- S47a: fixed. Nate and me_d step through the door at walking speed, no 2.3 m whoosh.

## Builder extras
- S21a: fixed. Maya's run is smooth across the cut.
- S37a: fixed. Maya's pull into the hug has no lurch.
- S06b, S06c, S17a, S17b, S18a, S19a, S19b, S19c, S20a, S20b, S24c, S27a, S27b, S28a, S30b, S35a, S44b: fixed, nothing worse. The pairs are spaced, the faces are whole and read at phone size, and no head is cut. In S30b, nate_s's head edge touches the right side, which is fine.
- S41b ("my SISTER"): the pair is spaced, but **worse:** at 40 mm with F 3.9, me's face is cut by about a third on the right edge for the whole shot.

## Must-fix
1. S08b (L08.1): the camera is too tight for the new 1.4 m gap. Change `C("curb", (0.7, 3.2, 1.15), -6, 3.3, 40, ...)` to F 4.1, or keep F 3.3 and set push 0.12 to 0.04, so that both faces stay fully in frame to the last frame.
2. S41b (L41.1): change `C("roof", (0.05, 10.9, 1.4), 0, 3.9, 40, ...)` to F 4.6, so that me's face is whole on the right.

## Should-fix (not blocking)
- S10b: F 4.0 to 4.3, to give me_d's head some room on the right.

Verdict: revise
