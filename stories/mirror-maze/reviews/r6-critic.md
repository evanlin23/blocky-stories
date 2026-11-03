# mirror-maze, round 6 critic (rescue, last look)

Verdict: approve

**r5 must-fix 1 (L01, S01, 0-2.8 s): done.** Frames at 0.3, 0.8, 1.3, 1.8 and 2.4 s show Tasha's mouth held still through the whole line. She no longer seems to say the narrator's words. The lilac-rimmed strangers in the panes still read at phone size, and the captions are in sync.

**S14 (L13, 22.7-24.5 s): no regression.** Tasha's back is to camera and the lit me, smiling in the bucket hat, carries the shot. With the flap gone, nothing reads as her speaking "I never have", which also fixes the r5 advice about chewing. No other shots changed: the diff touches only the two `mouth()` calls.

**Note (advice, not blocking):** her held face is the engine's `grin`, which `blocky/faces.py` draws as "the uncanny one": a wide row of teeth. With her raised brow it reads as a clenched grimace, not the soft smile in the older still f00018 (stills sheet from Nov 2). It doesn't break logic. It even plays as unease under a "fun fact", but it shades L01's "wonder first". If anyone touches S01 again, the fix is one word: `expr="smile"` (or `"soft"`) on Tasha's S01 stage entry.

**Scores (r5 stand, one updated):** Hook 7, Feeling and clarity 7, Big idea 7, Middle grip 7, Creature 6, Twist 7, Lore 2 (optional), Warm turn 8, Shot variety 7, Faces 7, Sound 7, Captions 8. Lore is optional by rule. Every other score is 6 or more, and the average without lore is 7.1.

**Panel (r5 stands, with one change):** the casual scroller's "who is 'me'" confusion at 1-2 s is weaker now that Tasha's lips no longer match the voice. Likely top comment: "the narrator was the reflection the WHOLE time".

**Must-fix:** none.
