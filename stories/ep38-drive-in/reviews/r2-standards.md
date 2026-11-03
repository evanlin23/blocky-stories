# ep38-drive-in, round 2, standards

Verdict: approve

I checked the preview (quarter-res, every 4th drawing; mp4, timeline and mix built after the 11:51 fix and sound commits), the contact sheet, the stills sheet (S24, S42) and a mid-frame of all 73 shots. `check` reports no problems, `pytest` passes (64), and preflight has 0 blocks.

- **Fiction:** pass. There's no set text anywhere. The speaker boxes (S38, S70) and the screen are blank, and the S70 tally is two plain strokes.
- **Kids and mature themes:** pass. Everyone in the cast is an adult, nobody is hurt, and the Unlit never touches Theo. `made_for_kids` is false.
- **IP:** pass. The faces, the cap and the Unlit's dash glints are our own. The package names no game.
- **Originality:** pass. It doesn't repeat any made story or anything on the batch-1 list. The ep44 Glass One overlap stays a batch note for ep44.
- **Flashing:** pass (indicative). 1-frame: 1 flash and 2 changes a second. 3-frame: 1 and 3. Nothing is extended, and red is 0. The r1 S41/S42 fix holds. S40 sits at about 94 luma, S41 at 60 to 66 (Unlit shoulder, Theo's plaid, steady, no wall, no black), and S42 at 48 with a small dash glint that is no longer a disc.
- **Package:** pass. The title is a statement of 61 characters. The description says "It's made up." and uses no banned word. Cover 0.7 s (S01) shows two lit faces with their markers. The words have no dashes or semicolons.
- **Shared engine:** `hiss_fall` is a new opt-in `sfx` kind. Defaults are unchanged and no other story uses it. The mix measures -14.1 LUFS and -1.8 dBTP.

## Must-fix
None.

## Nice-to-have
1. [build] On the final, recheck the S39 to S40 cut (76.9 s, luma 19 to 94) and the bright cream run S67 to S69 (126.7 to 131.8 s) for margin.
