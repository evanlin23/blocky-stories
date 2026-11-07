# ep92-blackout-ben, r3 critic: render-correctness re-check (S54a/S54b only)

Not a review round. Re-checked on the truly redrawn preview frames (frames-preview f03106-f03171, written 21:58-21:59 from the committed rev-4 story.json, plus sheet ep92-S54-v3.png). The earlier note was written on stale frames and is replaced.

What changed (`git diff origin/main`): Ben 6.6 -> 9.6, me 5.6 -> 8.5 at L54; both `go` to the old marks (11.0 / 9.9) at L54.2, so the walk fills S54a. S54b camera and Ben's yaw-60 hold unchanged.

What I saw at phone size (about 270-300 px wide)
- f03110 -> f03114 cut: living room to hallway. The first S54a frame is sharp and lit: hallway, wall plants, red runner, me's striped back about 3 m out, Ben's head just ahead. No dark blur and no camera against a head at 3114-3117.
- f03114-f03138: me and Ben shrink steadily down the hall with walking legs in every sample. No lurch, no 4.4 m dash, no dead stop inside the shot.
- f03139-f03163 (S54b): the low door-frame hold with the tally plant and the flashlight glow, same as the uploaded film. No pop across the cut.
- f03167 (S55): Ben's close-up reads cleanly. No new problem at that cut.
- Nothing worse: no blank or dark frame, no new clip, the tally meter stays on screen the whole time. Ben is mostly behind me in S54a, but that was true before and it is not a beat problem.

Verdict: approve
