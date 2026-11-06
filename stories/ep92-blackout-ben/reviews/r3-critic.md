# ep92-blackout-ben, r3 critic: render-correctness check (S54a only)

Not a review round. Checked only the shots the rev-4 fix touches (S53 tail, S54a, S54b head).

What I checked
- `git diff origin/main`: Ben 6.6 -> 9.6, me 5.6 -> 8.5 at L54; both `go` to the old marks (11.0 / 9.9) at L54.2, so the walk runs the whole of S54a. S54b camera and Ben's yaw-60 hold unchanged.
- Preview frames f03106-f03167 at about 300 px wide, plus the stills sheet ep92-S54-v2.png.

Result
- Cut at f03114: the first S54a frame is sharp and lit. Hallway, wall plants and me's back (striped shirt) read at once, with Ben's head just ahead. No dark blur and no camera inside a head at 3114-3117.
- f03114-f03138: me shrinks steadily as the pair walks away (about 1.4 m in 0.83 s, about 1.7 m/s). No lurch, no 4.4 m dash, no dead stop inside the shot. The ease lands on the S54b cut.
- f03139 onward (S54b): the same marks and framing as before. The door-frame tally plant and Ben's flashlight turn still read, and there is no jump in position across the cut.
- Nothing worse: no new clip, no blank or dark frame, and no pop across either cut.

Verdict: approve
