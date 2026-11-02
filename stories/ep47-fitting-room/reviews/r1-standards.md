# ep47-fitting-room: standards, round 1

Verdict: revise

Passes: fiction (picture signs, a blank phone and ticket), kids and mature themes (all adults, nobody hurt, no death words or blades), IP, package (title 59 chars and a statement, "It's made up.", no banned words, made_for_kids false), and writing.

## Must-fix

1. **Originality, batch-1 list ("a pale grey blank-faced creature"). S59 to S69 (85.6 to 103.4 s), cover 86.4 s.** `empty.collar` in `set.py` is a 1.35-tall tube in `#5c5c64`, with a black oval `empty.gape` and two glints on its front. It renders as a pale grey cylinder head with a blank black face (stills "It's the SUIT.", "at my old BENCH,"), so the suit stops reading as headless. The fix:
   - Cut `empty.collar` and `empty.void` to about 0.35 high, a shirt collar.
   - Colour its outside charcoal (`M["lining"]` or the pinstripe), never pale grey.
   - Delete `empty.gape` and put the glints deep inside the tube, so they show only down the collar (S62 from above, S68 at eye level).
   - Then re-render the S68 test still and the stills sheet.

## Nice-to-have

- S87, the lore plant, runs 0.47 s, not 1.8 s, and its still shows the chalk line, not the brass foot. Check that the tally is in the cut.
- At phone size the hook glyph reads a little like "ʃ" or "J". A thicker ring at its foot would keep it clearly ours.
- The flash risk is low (preview: 1-frame 1 of 2, 3-frame 2 of 3). The tightest spot is the loop seam, S95's dim sleeve straight into S01's bright arcade (3-frame changes 4 of 6). Re-read it on the Actions final. Keep L61's falling tags matte and slow.
