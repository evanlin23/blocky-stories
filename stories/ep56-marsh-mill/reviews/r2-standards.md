# ep56-marsh-mill, round 2, standards

Verdict: revise

I checked the preview (quarter-res, every 4th drawing) at the middle frame of all 84 shots, plus a luminance trace of the whole file. All three round 1 must-fixes are done. L09 has no age now. The Lifter reads as warm tan wax, not pale grey. The key glow stays gold with no clipping at S02, S61 to S67 or S73.

- **Fiction:** pass. No words, signs or real places. The café awning, bakery board and doors are blank.
- **Kids and mature themes:** pass. The cast is all adults. Win is away for an ordinary reason and nobody is hurt.
- **IP:** pass. Every glyph and face is our own. No game name in the package.
- **Originality:** pass. `check` is clean, and setting, creature, rule type and warmth differ from the rest of batch 4. The tally lore plant follows canon.
- **Flashing:** preview PASS, 1 flash and 2 changes a second (3-frame: 2 and 4, worst at 27.17 s). That's indicative only. Every big luminance jump is a single cut, and no two fall within a second.
- **Package:** pass. The title is a statement, the description says "It's made up", `made_for_kids` is false, and the pin is a question. No dashes, semicolons or banned words.

## Must-fix
1. **S55, L42 (85.7 to 87.3 s), also S52 (82.4 to 84.4 s):** the warm under-key clips the lower half of the creature's full-frame face to near white. About 10% of the frame is above 230, and the cut into it goes from mean 25 to 89. That breaks "no clipped white, eye highlights the brightest thing". It's also the riskiest moment for the final flash measurement, because the bright area is a full-frame face arriving out of dark. In `set.py` (the `n in (36..42)` block), drop `lkey` for `n >= 40` from 380.0 to about 240.0, so the chin peaks below clipping while the face still reads warm. Re-run `flash` and check that S55 has no pixels above 230 apart from the eye glints.

## Nice-to-have
- The spine is still close to ep45 `bee-yard`: a dead marker, a loved one's workplace he never enters, and a twist that it was about him. Both also end on two markers on two chests. Swapping S80 (L64) for the open mill door would set the ending apart.
- ep54 `dance-hall`'s pitch also has a glyph-matching marker, an aunt and a postman in its montage. Flag that to whoever builds ep54.
