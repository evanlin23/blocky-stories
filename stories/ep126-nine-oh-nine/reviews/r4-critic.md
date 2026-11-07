# ep126-nine-oh-nine: r4 critic (render-correctness check, changed shots only)

Checked on the preview (rebuilt 2026-11-07 01:15 UTC, timeline S08 12.70-14.27, S09 14.27-15.37, S28 40.67-42.57), consecutive frames at phone size.

## S08 (L08, bus broke down): fixed
- 12.70-14.27: `me` now walks steadily toward camera from the bus; no hop, no slide. The 13.23 s jump is gone.
- Nothing worse: head stays in frame to the cut (largest at 14.17, still uncropped), face reads, no hold over 1 s.

## S09 (L09, running): fixed
- 14.27-15.37: the run starts at once and is smooth; no 0.3 m pop near 14.37.
- Nothing worse. (He passes into shadow from 14.97 and the face darkens, but the eyes still read; that's the lighting, not this change.)

## S28 (L28, "Grandma said, 'Well. You'd better SIT down.'"): not fixed, the overlap is visible
- 40.67-41.0 (the first ~10 drawings of the shot): grandma's purple arm and body go through grandpa's tan torso, and grandpa's head sits right against her face, so the two read as one tangled block. Her face is half hidden in the frames where the line starts. It's plain at 300 px wide. Listing it in `staging_ok` just hides the finding; the picture still shows it.
- From 41.0 on it's clean: grandma alone, centred, face clear.

## Must-fix
1. S28 / L28: the two move in from L27.1+0.3 and cross right where the shot cuts in (grandma key L28+0.2, grandpa L28+0.4). The cut can hide a jump, so put them where they end up at L28: `teleport("grandma", "L28", list(G.SIT_G), yaw=180, expr="smirk", arms=[0, 0])` and `teleport("grandpa", "L28", list(G.GP_STAND), yaw=0, expr="sad-smile")`. Then drop the L28+0.2 and L28+0.4 keys and the `staging_ok` entry. Also acceptable: finish both walks by L28-0.05, off camera in S27b. Check that S28's first frame shows grandma alone with her face clear.

Verdict: revise
