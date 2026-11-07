# ep99-statue-years, critic r4 (staging fix, changed shots only)

Checked every preview frame (30 fps, about 390 px wide) in each window; diff is make_story.py REV 3.

**1. S43-S45, 37.8-40.6 s (Mom's keys, L23).** Fixed. In S44 (38.83-39.33) Mom stands in the doorway, then steps forward from 39.10 and grows only slightly over four held drawings: a walk, no dash or slide. The door moment reads (she is framed in the blue door) and "And every morning / she was up before the SUN" still lands over S44/S45. S45 (39.35-40.6) walk across the sunflowers is unchanged and fine. Nothing worse.

**2. S61-S63, 54.8-57.9 s (Mom and Dad walk, L32).** Fixed. In S62 (56.17-56.60) the pair hold the same size, with a small even step, so no pop or growth. The S61/S62 cut (56.13/56.17) and the S62/S63 cut (56.60/56.63) are clean cuts to a wider shot and then a closer one, with no jump inside a shot. The S63 walk toward the camera, with both heads leaving the top and sides at 57.4-57.85, is unchanged code from main (L32.1) and isn't part of this fix.

**3a. S32, 29.8-30.3 s (mirrors, L17).** Fixed. The three backs sit shoulder to shoulder with their arms touching, not inside each other. The side heads are still visible behind and next to the middle one. Nothing worse.

**3b. S20/S21, 19.8-21.6 s (bakery stranger, L11).** The arms are fixed: Mom's raised arm crosses in front of Dad's shoulder, and nothing passes through. But moving Mom 0.15 m further left (CX-1.15) pushed her head onto the left frame edge. In S20 (19.83-20.50) half her face is cut. In S21 (20.55-21.50) her eye sits on the edge and by 21.17-21.45 most of her face is out of frame. At this framing 0.15 m is about 40 px of a 390 px phone frame, so this is visibly worse than main. The stranger (c2, moved to CX+1.75) also shows only as an arm at the right edge in S20, so the "stranger looks from Dad to Mom" beat no longer reads. Mom is the one we love and this is a clue shot, so her face can't be lost.

Verdict: revise

Must-fix:
1. S20/S21, 19.8-21.6 s, L11: keep the wider spacing but bring Mom's whole head and the stranger's face back into frame. Pan both camera keys of shot "stranger" left by about 0.15 m and pull them back about 0.4 m (for example, start [CX + 0.45, CY + 3.3, 1.85] to target [CX + 0.05, ...]). Or restore Mom at CX-1.0 and get the clearance by moving Dad to CX+0.45 instead. Then re-check that Mom's face, Dad's face and c2's head are all whole at 20.2 s and 21.3 s.
