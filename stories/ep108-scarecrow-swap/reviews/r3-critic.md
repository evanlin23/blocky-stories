# ep108-scarecrow-swap, critic round 3 (single-fix look)

Preview 39.8 s, 43 shots. Preflight 0 blocks, no pace or clip rows (flash warning general_3f only, as before).

**Round 2 must-fix 1, S40 (L20, 36.77 to 37.37 s): met.** It's now a level two-shot on the couch. The sack-face straw Grandpa is on the left with his hat in frame, and Grandma is on the right with her bun and the top of her hair in frame. Her hand rests between them on the cushion with the remote on it. The hand is about 0.15 of the frame width. Face widths are about 0.23 for the sack and 0.18 for Grandma. Grandma is just under the 1/5 face rule, but both read plainly at 300 px, so I accept it. The remote itself is small here (about 4% of the width), and the next shot has to sell it.

**New finding, my miss in r2:** S41 (L20.1 `remote2`, 37.37 to 38.10 s) carries the key word "the REMOTE." Its framing is the old S40 problem, unchanged. Grandma's hand is a skin block about 0.4 of the frame width in the foreground, and her hair and crown are cut off at the top. At phone size this is the same blob I flagged in r2: a cropped head and a hand that reads as a box. I put the r2 fix on the wrong shot id, so this is my error, but the phone-size rule still makes it a must-fix.

Nothing else changed: the S40 camera is the only edit in the diff. The rest of the preview matches r2.

**Scores:** as in round 2, except faces 7 (S40 fixed, S41 still a blob). Average 7.1. Reset: all pass.

**Must-fix**
1. S41 (L20.1, 37.37 to 38.10 s): reframe `remote2` to match the new S40 rules. Pull it back and up (for example, camera near [LX+0.3, LY+2.8, 1.5] looking at [LX-0.05, LY+0.35, 0.95]). This makes a closer punch-in on Grandma's side: her whole head with the hair top in frame, her hand on the cushion under 1/6 of the frame width, and the remote clearly bigger than in S40 so "REMOTE" lands on it. If it can't be framed cleanly, drop L20.1 and hold S40 through 38.10 s with a slow push-in (1.33 s total, inside the 1.5 s still limit).

Verdict: revise
