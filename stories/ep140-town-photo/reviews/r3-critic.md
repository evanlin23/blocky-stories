Verdict: approve

Rescue look (round 3): checks the round-2 must-fix and any regressions it caused (decision 8). Fresh preview 53.6 s, frames grabbed at 300 px: S33 at 48.9, 49.4, 49.8, 50.0 and 50.2 s, and S34 at 50.3, 50.9 and 51.5 s.

**Round-2 must-fix**
1. S33, L34 "He pats my shoulder": in. Okafor starts a step off at 48.9 s, and by 49.4 s his arm reaches level with my shoulder. From 49.8 to 50.2 s his skin-coloured hand sits on top of my yellow shoulder, next to my head. Nothing crosses my chest and there's no dark wedge. Both faces are about 1/4 of the width and the camera is a little above. At phone size it reads as a pat.

**Regressions**
- S34 (50.23 to 51.57 s), L35 "Your TURN": the fix moved Okafor to x -1.62 but left the S34 camera aimed at x -1.1. His face is now half off the right edge (one eye, no mouth), and my head is cut off at the left edge with no face. The hand on my shoulder fills the middle and the caption carries the line, so the payoff and the warm turn still read. That makes it not severe (no hard rule, no blank frame, no lost beat): **should-fix**, not blocking.

**Scores:** warm 7 (the pat now shows the warm turn), faces 6 (S34 crop). The rest are as in r2. The average is about 7.3, with nothing under 5.

## Must-fix
None.

## Should-fix (not blocking)
1. S34 (make_story.py, the `S("L35", "S34", ...)` line): move the camera target from (-1.1, -5.5, 1.5) to about (-1.55, -5.5, 1.5) so Okafor's whole face, smile and both eyes are in frame, about 1/3 of the width, with his hand still on my shoulder at the left. This is one number and worth doing before the render. The final proof will show the crop too.
2. Carried over: fill the P1 drop at 42.6 to 43.2 s, and brighten the Okafor set a little.
