# mirror-maze, round 3, critic (fix-check, scoped)

Verdict: approve

I checked only the two round-2 must-fixes and the 97 to 122 s range. All other scores stay as they were in r2.

## Must-fix 1: L63/L64 copy Tashas. Landed.
- L63 (99.1 to 100.7 s): there are 6 or more copy Tashas in the near panes, 3 to 4 on each side. The nearest faces are about 1/7 of the frame height, with eyes and mouths readable at preview size. Their `scared` faces and lean change a beat apart while the line plays, so "COPYING me" reads. None of the panes shows me.
- L64: the close-up row of copy faces makes "None of them showed ME" land clearly. No hat appears anywhere.

## Must-fix 2: hat in her pane at L75 to L77. Landed.
- In the L75, L76 and L77 stills and in the preview (about 117.6 to 121.5 s), the pane behind it holds only the real Tasha (wide eyes, gritted teeth). My green hat appears only in the foreground, on the real me.

## Nothing new broken
Captions stay in sync through the range, and the cut on "whoosh" into L78 is intact.

## Scores (changed only)
- Faces 6 -> 7: L63 and L64 now have readable faces.

The new average is 7.2. No score is under 5.

## Non-blocking note (already in r2, not caused by this fix)
- L76 (about 119.5 s): the copy shows the back of its head for about 1 s on "So I stepped BACK", one line after "FACING me", and then faces me again at L77. If there's a spare pass, keep yaw 180 through L76 so that only the step-back copies me.
