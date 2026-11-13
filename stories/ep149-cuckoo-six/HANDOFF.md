# ep149 handoff (builder)
- Caption position: the script wants "A, B, C or D?" in the top third, but `blocky/post.py` draws every caption at the fixed CY (about 66% down) and has no per-caption position. Not changed (engine). The master is framed so the caption sits over the rug and the sixth chair, not faces. An opt-in `cap_y` on a pause line (timeline.build passes it, post.draw_captions uses it) would fix it.

## 2026-11-13: proof qa FAIL (blocked, waiting on orchestrator)
- PR #503. Reviews: standards approve (r2), critic approve (rescue look r3). Rounds and the rescue are used up.
- Proof run 43344373847, artifact 14000734377, sha 2a5fac5c: verdict.json passes, craft 0 blocks, flash/peak/clips pass.
- qa FAIL reason: in the puzzle hold P01 (S11a-c, 12.4-16.4 s) the frosting clue can't be found at phone size (the D badge and Mom hide the cake's scoop; the curtain smudge is ~4 pt). S09 shows the cake from the front only, so the scoop is first seen in the answer (18.2 s), yet the pin asks "the sneakers or the frosting?". The sneakers, letters and caption read fine.
- Fix qa named: move the D badge off the cake so the scooped corner shows and make the smudge ~3x bigger (or raise the S09 camera so the scoop shows before the hold). This needs a redraw and a new proof, beyond the round cap.
- Cheaper option (no film change): a pin about the sneakers only, then re-qa the same proof.
