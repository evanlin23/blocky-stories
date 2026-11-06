# ep128-zero-feet: critic, round 2 (check only)

Verdict: approve

**Round-1 must-fixes, all in (read from this round's freshly drawn frames):**
1. L18 now says "...when I signed my LEASE." (30.36 to 32.51 s). Yes.
2. The tag now shows a house, a sole with toe dots, a gap, then 0. At 300 px it reads as a footprint, not a 5. Yes.
3. S02, S04, S34, S45, S46, S49: the tag stays whole through each punch-in. Yes.
4. S07, S08: Grandpa's 3 has its spine on the right and curled end-ticks, so it reads 3 and not E. Yes.
5. S41: slippers and rug only, no head. Yes.
6. S40 and S43 show `neutral` with a fixed stare, and S44 on shows `sad-smile`. Yes.
7. S38 is high and wide, with no flat green fill. Yes.
8. The drop (40.4 to 40.9 s) sits at about -50 dB RMS, a room bed rather than dead silence. Yes.
9. S47, S59, S61: my room is cream with an amber lamp, and Mom's flat stays lilac. Yes.
10. S29: both strokes show on the newel cap. Yes.
11. S30 and S39: the door has a frame and a knob, and her doorway reads lilac with no white bloom. Yes.

No regressions. Preflight shows 0 blocks, and flash passes.

**Scores:** hook 8, back-row 8, narrator 9, appeal 9, relationships 8, clarity 8, big idea 7, scare 6 (her stare now holds), twist 7, lore 6, warm turn 8, variety 7, faces 7, sound 7, captions 8. Average 7.6. Reset items: all yes.

**Panel:** The creepy fan stays to 75 s: "she walks over him so it stays ZERO". The repeat viewer catches the footsteps plant: "step for step was her the whole time". The casual viewer may still go at 4 s: "I don't FOLD". Top comment: "My laundry was FOLDED. I don't FOLD."

## Should-fix (not blocking)
1. **The preview file, not the story:** `frames-preview` still holds 221 stale round-1 PNGs, f00945 to f02202, from 23:22 on Nov 5. The shot grid moved by one frame after L18, so the preview mp4 mixes old and new frames from 31.5 s on. The door flips blank, and the old tag shows. Empty the folder and rebuild before anyone else watches the preview. The final draws fresh frames.
2. **S48 (54.9 s) and S38 (42.0 s):** each move ends with the face clipped at the right edge. Stop the move about 10% earlier.
3. **S38 to S39 (40.97 to 43.73 s):** the stairwell's light pools are drawn as large pale discs. Soften them.
4. **The `hear her` caption** shows for under 0.2 s. Merge it into the next chunk.
