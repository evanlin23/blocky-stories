# ep102-aunt-peaches, r6 critic (render fix, S62 and S69 only)

I checked only S62 and S69. I looked at every full-res still from f1606 to f1640 and from f1790 to f1800 at 180 to 270 px wide, plus the preview drawings f1777 to f1816 (S68 into S69 and S69 into S70) and f1601, f1605 and f1606 (S61 into S62).

1. **S69 'turnunseen' (1785 to 1811): pass.** There's no green slab, no dark wedge and no frame inside the geometry anywhere from 1785 to 1809, and 1793 and 1794 now match their neighbours: the path, the grass edge bottom-left, the orchard trees and a whole 412 meter. The cut in from the S68 fence post and the cut out to the S70 bench are both clean, with no blank frame and no pop.
2. **S62 'carrolls' (1606 to 1636): pass.** The brocar enters on the right at 1617, crosses through 1630 and its tail is gone by 1631. That's about 14 frames, smooth and even with no jump. At phone size it reads plainly as a car driving past: two dark wheels, a yellow body, a blue cabin and a red tail-light. The road is empty before and after, and the cuts at 1605/1606 and 1636/1637 are clean with no pop.

**Regressions:** none.

**Should-fix (not blocking):**
- S62: from 1620 to 1628 the caption "every HOLIDAY." sits on the car's body. It still reads, but the car's top edge is close to the caption line. Lowering the camera target about 0.2 m would put the whole cabin above the caption.
- S69: the soft shadow band across the middle third is a little grey at phone size. This is the existing look, not something the fix caused.

Verdict: approve
