# ep20-photo-strip: standards, round 2

Verdict: revise

Passes: fiction (no set, strip or cake text, the hotel is never named), kids and mature themes (all adults, nobody hurt, no death words), IP (own faces and outfits, no game name in the package), package (it says "It's made up.", the title is a question, made_for_kids false) and rule 8 (no dashes, semicolons or AI words). Round 1 fixed: the S63 tally shows three full strokes for 1.8 s, and S56 and S57 are lit.

## Must-fix
1. **S11 (L11, 20.67 to 22.6 s), full-frame glow at the flash bar.** The curtain fills the whole frame and pulses from dusky pink to near-white. The preview still reads 2 flashes a second at 21.63 s, with a 1.1 s run. Round 1 asked for 1 or less. The peaks also look clipped, which breaks "no clipped white". Make the four peaks `to` 0.55 (now 0.7) and the four dips `to` 0.42 (now 0.55). Pull the S11 camera back so the curtain fills at most half the frame, with the dark hall wall around it. Re-run preflight and confirm the reading at 21.6 s is 1 or less.
2. **The Third's head reads pale cream, not sepia (S35 to S39 at about 71 to 79 s, and S51 at 106 s).** The underlight washes the head (`rig.head_material("third", "#b59878")`) far paler than its sepia hands. A pale head on a far-too-tall figure whose head turns too far is ep11's creature (back-row), and it moves toward batch 1's "pale grey blank-faced" figure. Darken the head to `#8f7152`, or keep the key off the head, so it is no brighter than the hand on the seam in those shots. Check S37 and S51 again in the stills.

## Nice-to-have
- S46 (92.1 to 94.0 s): the slide across the white strips still gives the top 3-frame reading (5 changes a second, with a 1.87 s run at 2/s). Grade the paper down about 15%.
- S51: once the head is sepia, the tall dark suit in an empty hall leans less toward the slender-man trope. Keep the dot eyes and smile lit.
- `stills-sheet-key-beats.png` dates from before the round 2 build. Re-render it.
