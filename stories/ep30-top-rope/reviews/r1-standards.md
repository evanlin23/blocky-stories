# ep30-top-rope, round 1, standards

Verdict: revise

Passes: fiction (no set text, phone glow blank, tally reads as strokes), kids and mature themes (all adults, the slip is told, nobody hurt), IP (own faces, no names), package (`made_for_kids` false, "It's made up.", no banned words). Preflight: 0 blocks, 2:22.

## Must-fix
1. **Flashing, S40 to S43 (64.6 to 70.0 s).** The preview fails `general_3f_changes_le_6` (7 at 68.77 s). S40 and S41 sit at lamps 0.06 with a hot glow on the creature, then S42 cuts to full lamps (mean luma about 40 to 116) and S43 follows. Bridge the cut. Add `"S42": {"lamps": 0.45}` and `"S43": {"lamps": 0.6}` to `looks`, and drop the S41 glow strength from 90 to 45. Re-run the preview flash until the house bar passes.
2. **Hard rule 8, L47.** "Don't look UP. / Touch the TOP. / Go DOWN." is a three-beat slogan. Change it to "I kept my EYES / on the WALL."
3. **Originality inside the batch, L75.** "A climb is built / for TWO. / One on the WALL, / one on the other END." states the shared canon formula. Pitch #17 `chairlift` has "A chair is built for two, and nobody rides alone", and #18 `unit-seven` has "counted for two". Say it in this story's own climbing terms instead: "Every ROPE / has two ENDS. / Mine was never / LOOSE."

## For the caller (not this story's fix)
- #17 `chairlift` shares this twist: something fills the empty second place of a two-person thing because I insist on going alone, and then a person takes over. ep30 is already built, so #17's twist should change before it's scripted.
- #18 `unit-seven` is also "Thursday evenings" and opens on "Every THURSDAY". ep30 says Thursday 8 times. Move unit-seven to another night.

## Nice-to-have
- `story.json` title differs from `package.json`. Sync them.
- S01 (lamps 2.6) clips the near arm to white. Lower it to about 1.6.
