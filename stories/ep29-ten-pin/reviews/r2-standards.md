# ep29-ten-pin, r2 standards

Verdict: approve

Read from the quarter-res preview (every 4th drawing, 137.1 s, built 09:26 UTC after commit 05649e8), its contact sheet, one frame a second pulled from the preview mp4, the stills sheet, `preflight` and `check`.

## Checks
1. Fiction: pass. Made-up names only. The score screen shows bars, slashes, crosses, our own tiny faces and an empty square, with no digits or text. No signs, nothing cropped mid-word, and the shirts are plain.
2. Kids and mature themes: pass. Everyone is an adult (Mags is older). No death words or weapons, nobody is hurt, and nobody young is in peril. The package doesn't aim at kids.
3. IP: pass. Faces, the stacked-head creature, the shirts and the carpet squiggle are our own. No game name in the package.
4. Originality: pass. The alley, the stacked-head bowler, the nickname first line and the play warmth (the Forklift dance) aren't used anywhere else in the repo. The lore plant is a plain five-stroke tally, as `lore.md` asks. Nothing from the batch-1 list.
5. Flashing: pass. The r1 must-fix is fixed. The preview's worst second is now 1 flash and 3 changes (1-frame and 3-frame), 0 red, no extended run, and 14 very different cuts at most 2 a second. The light dips at L41 and L53/L54 (about 94 to 96 s) stay smooth.
6. Package: pass. Lints clean, `made_for_kids` false, the title is a statement and doesn't spoil the twist, and the pin asks about the rule. No banned words, dashes or semicolons.

## Must-fixes
None.

## Nice-to-haves
- Description: make "It's made up." its own sentence, then "It's a creepy blocky story, built with code and Blender."
- `stills-key.png` (07:32 UTC) is older than the round 1 fixes and still shows the old cream heads. Re-run `stills` so the sheet matches the film.
- From r1, still open: `sitter` ("in the spring") and `top-rope` and `unit-seven` (Thursdays) aren't in this checkout, so I couldn't check against them. Check `check` again once they land.
