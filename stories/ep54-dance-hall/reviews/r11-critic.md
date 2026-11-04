# ep54-dance-hall, round 11, critic (polish pack check)

Verdict: revise

I pulled frames from the 144.7 s picture preview at 0.1, 0.8, 1.4, 2.2, 4.6, 5.5, 6.6, 7.8, 88, 90.5, 94, 99.4, 130.4, 131.3, 132.2, 139 and 141 s, and looked at the stills sheet and those frames at 300 px wide. Preflight: 0 blocks, no `pace` or `clip` rows.

- **Opener (S01 to S03): works.** The S01 punch-in makes Ros's dim half bigger, and the half stays the brightest thing in frame the whole time. By 1.4 s her face is cut to one closed eye at the top edge, but this is a close-up on the hand and her hair and eye still read as her. The bus-stop halves bloom whole on "REST" with nothing cropped out.
- **S04/S05 clip_ok: fine.** At phone size the overlapping dancers read as a crowd at a counter, and no face is cut through. The striped brothers (7.8 s) still read as a matching pair.
- **Scare: intact.** The legs (88 s), the chandelier drops (90.5 s) and the bend (94 s) stay low-key and warm with real shadows. The bright grade hasn't flattened them.
- **Cover (99.4 s): intact.** The held smile and the brow are fully in frame, and Ros is at the left edge as before.
- **Warm turn and ending (S90 to S96): calm, not busy.** In S90 the heads touch sleeves, but at 300 px it reads as a close hold, with both faces and the whole glyph clear. S96 is the half glyph, big and clean, under "Mine is my AUNT."
- **Polish hurts nothing.** Only the sound below remains.

**Scores:** the r8/r9 scores stand (average 7.5, no score under 5). Sound drops 1 until the fix below is made.

**Must-fix:**
1. **L23.1 `glitch` (the record skip, about 45.5 s), sound:** it is at -14 dB, and preflight warns that it can sound scratchy above -24 dB (the owner pulled ep36 for scratchy effects). With the whooshes now on top, set `"db": -26`, or swap it for a soft low `thud` at the same cue. No other change.
