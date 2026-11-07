# ep94-today-again, critic r4 (staging fix, changed shots only)

I pulled every preview frame in each window at about 390 px wide, with extra crops where a body came near a prop. `preflight` gives 0 blocks.

1. S28 to S29, 22.2 to 24.5 s: fixed. S28 ends with Pearl at DOOR-0.5 and S29 opens on that same mark, so she doesn't jump on the cut (22.93). The S28 camera, now aimed 0.5 m over, keeps her head and face in frame. In S29 she walks forward and trips at 23.6, then holds still from 23.9 to 24.5 with no slide. Her head goes out past the top right for about 0.2 s at the bottom of the trip lunge (23.65 to 23.8). That lean is the same pose and end mark as on main, so it's not new, and the trip still reads.

2. S33 to S35, 26.6 to 29.1 s: fixed. Her path from (-2.4, 0.2) to (-1.2, 0.9) passes at least 0.96 m from the centre of the nearest table (tbl0, top radius 0.34). On screen the near table hides her legs from in front, and none of her body enters a table top (27.75 to 28.5). The cut to the counter at 28.5 reads.

3. S58 to S60, 45.5 to 48.4 s: fixed. S59 (46.17 to 47.13) is now one steady walk away from the lens: her hair gets smaller from frame to frame, with no bob and no dart. The green slab swings away and shows the brick alley and sky by about 46.9, so the door opening reads. With -95 the hinge turns the slab into +y, away from me, and my end mark (y 7.0) stays short of the door plane (y 7.15). Nothing passes through the slab.

4. S91 to S93, 73.9 to 76.8 s: fixed. In S92 (74.73 to 75.67) Mom walks away from the lens, seen from behind, and gets a little smaller each frame. She doesn't shoot back or slide. The top of her bun is clipped at the frame edge for the first few frames. That's the back of her head, not her face, and her white hair and pink top still read as Mom creeping past. S93 shows her face and the clipboard clearly.

5. S94 to S95, 76.8 to 78.4 s: fixed. In S94 she walks toward the lens one step at a time, growing steadily, with her face readable the whole shot and no rush. The 0.6 m change of mark into S95 (8.2 to 7.6) happens on a camera change and doesn't show.

6. staging_ok stills, at 300 px wide. S09 (6.6) and S11 (8.2): the crowd is at the edges and nobody touches anyone. S14 (11.3 to 11.7): two walkers at different depths pass in front of each other for about 4 frames. It reads as a pass, not a merge. S47, S48 and S50 (38.2, 38.8, 39.9): Mom and the seated customer read as two separate people, and no arm goes through a body. S75 (59.4): the crowd is at the edges. None of the 7 is a visible arm-through-body at phone size.

Around the changed shots, nothing new is worse: no new head crop, no face lost, no clip. The frames.py pops at S96, S98 and S99 are out of scope.

Verdict: approve
