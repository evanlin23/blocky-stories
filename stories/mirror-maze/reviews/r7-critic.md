# mirror-maze, round 7 critic (new opening, polish pack)

Verdict: revise

**Opening recipe v1:** 1 warning line 9 (8 words, 0.25 to 2.27 s). 2 frame 1 is 4: it's centred, lit and pushes in with no wide, but it reads as a man glaring from a dark doorway. You can't see any glass or the empty spot in front of it, the rim shows white rather than lilac, and by 1.5 s the push has cropped the pane edges out. 3 hit 6: the hit lands on "REFLECTION" at 1.92 s, but a polish low hit on "TOWN" (0.56 s) and a stray whoosh at 1.92 s with no cut under it, 0.36 s before the cut whoosh, crowd it. 4 line 2 is 8 (1.3 s, no names). 5 rule at work is 7 (S03 and S05 run 2.3 s, held by punch-ins). 6 title 9.

**Hits' 9 points:** 1 yes (0.3 s). 2 partly (the rim is on screen at 0 s but doesn't read as a reflection; see fix 1). 3 yes (3.8 to 15 s). 4 yes (15.1 s). 5 yes (16.6 s). 6 yes (64 to 70 s). 7 yes (74 to 77.7 s). 8 partly (fix 1). 9 yes (1.59 s average).

**Scores:** Hook 6, Back-row 7, Narrator fit 8, Broad appeal 8, Relationships 7, Feeling and clarity 7, Big idea 7, Grip 7, Creature 6, Twist 7, Lore 2 (optional), Warm turn 8, Shot variety 7, Faces 7, Sound 6 (no hiss: 0.1 to 2.2% of the energy is above 4 kHz), Captions 8. Average without lore: 7.2.

**Reset:** 78 s yes, friend want yes, not a sad family reveal yes, close-up by 1 s partly, meter yes, pace yes, bright look 5 (dark violet), loop yes but with a dip to black, title yes, pin yes. Flash passes on the preview (at most 2 per second, worst at 15.67 s), and L33 is clean.

**Panel:** The creepy fan stays and comments "the narrator was the reflection the WHOLE time". The repeat viewer stays and comments "PICKLE". The casual scroller swipes at about 1 s because it looks like a guy in a doorway and says nothing about a mirror. Top comment: the reflection twist. Two slips: S01's coral-shirted stranger can be mistaken for the pink-clad "me", and 2D rain falls on me at 17 to 21 s and at 59.6 s, which breaks the "dry" plant (advice).

**Must-fix:**
1. **S01 (0 to 2.4 s):** make it read as glass with nobody in front of it. End the push at chest height with all four lit pane edges still in frame, show the empty, lit boards in front of the pane at the bottom of the frame, and add a diagonal sheen streak across the glass. Turn the `kick` down (or warm it) until the rim reads `#c9a6ff`, and give the stranger a teal or grey coat instead of the coral.
2. **L01 sound:** delete the `whoosh` at `L01>-0.35` and add `"quiet": ["L01.0"]` to polish, so the only accent in 0 to 2 s is the hit on "REFLECTION".
3. **L02 and L03 (3.8 to 7.1 s):** use US English and re-voice. "The fry CART'S / SHINY SIDE / has a LINE / a hundred LONG." and "The REAL line / is TWO." Use "cart", not "truck", because L06 and L34 already have a truck.
4. **Loop seam (77.7 to 0 s):** set `"fade_out": false` so S49 cuts straight into S01 with no dip to black.
