# ep53-car-boot: standards, round 4

Verdict: revise

Preview: quarter-res, every 4th drawing, 136.5 s. Preflight: flash PASS, 0 blocks.

Passes: fiction, kids and themes, IP and title, pin, sfx, and hard rule 8. Props pass too: none of the 17 kinds has an image texture, so none can carry lettering, a sign or a logo.

Must-fixes:
1. **Originality, L01 (0 to 2.1 s).** ep34 now opens "NEVER leave / anything of YOURS / behind a DOOR." It has the same `about-me` shape and a "mine" loop into a "your" warning. Two openers that both start on a capitalised NEVER and turn on "your own" read as one template. Re-voice L01 as a statement: "The SCARIEST coat / never changes COLOR." L02 stays.
2. **L37 caption (about 70 s):** the voice says "sweater" but the caption reads "In her JUMPER,". Change chunk 1 to `["In her SWEATER,", "in her sweater,"]` in `story.json` and `generator/lines.json`.
3. **`cover_s`:** the timings moved, so 83.3 s now lands on the Tilted's headless torso. Set it to `82.3`: its face lit, caption "something is SITTING."
4. **Flashing, S69 to S73 (104.0 to 109.8 s):** the 3-frame reading is 3 flashes and 6 changes at 108.9 s, both exactly at the bar, with a 1.4 s run from 104.03 s. Mean luma runs 157, 92, 141, 118, 106, 135, 114. Three changes:
   - End S69 before my white coat crosses the lens (the blip at 105.1 s).
   - Delete S71 and extend S70 to 107.9 s.
   - Lift S69's fill to a mean luma of 120 or more.

   Re-run preflight and confirm the reading there is under 3 and 6.

Nice-to-have: in S1 and S2 my cream anorak reads pale blue in the shade. Warm the fill so it doesn't look like its L61 blue.
