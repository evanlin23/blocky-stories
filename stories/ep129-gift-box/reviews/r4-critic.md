Verdict: revise

Changed-shots look only (S21, S61), no rescore. Checked fixcheck film-33.0/33.8/34.5/96.0/96.9 and every preview frame 32.6-35.0 s and 95.4-97.4 s at 270x480.
- S21 (32.87-34.70 s): fixed. Dad in the armchair, me on the couch end, a clear gap; his near arm rests at the armchair side and doesn't touch me. Both faces still read at phone size, and the beat ("He asks about... it's FINE") reads. Both heads are whole but with only 2 to 5 px to spare at the edges at the end of the push (should-fix: push 0.03 to 0.0, not blocking).
- S61 (95.67-97.13 s): the arms are fixed. They sit side by side over the counter, no arm through a body. Regression: the push-in crops both heads. By about 96.6 s my head is about a third off the left edge (half an eye gone), and Dad's hair touches the right edge. It's already tight at 95.67 s. A cropped head at phone size is a must-fix.
- No pop at the S20/S21, S21/S22, S60/S61 or S61/S62 cuts.
Fix (S61, make_story.py): `ocam("KG", 0.0, 1.85, 0.95, 4.8, 30, el=7, push=0.09, arc=1.0)` becomes `ocam("KG", 0.0, 1.85, 0.95, 5.4, 30, el=7, push=0.03, arc=1.0)`. Keep the pair at ±0.7 with CAKE61 arms. Then check that both heads keep at least about 8% of the frame width as margin at 97.1 s.
