# ep85-early-alarm: standards r2 (2026-11-04)

Verdict: revise

Seen: preview (129.3 s), contact sheet, a 1 fps sheet, 6 fps of 93 to 100 s, frames at 73.3, 73.8 and 73.85 s, and the reframed shots (S13, S14, S35, S58, S59, S65a, S67 to S71).

## r1 must-fixes
1. Title: fixed. "If It Rings EARLY, Stay In Bed ⏰" states the rule, matches `opening: if` and L01, and spoils nothing.
2. cover_s: the frame is right, but see must-fix 1 below.
3. Flash: fixed. S55d and S55e are lavender and warm, the dark-head frame is gone, and preflight passes (3f worst 3/s at 95.13 s, 3f extended 2.5 s from 94.17 s, red 0). Nothing left that will risk the final.

Re-check passes: fiction (no lettering anywhere, made-up names, "It's made up."), kids and themes (narrator 17, nobody hurt, the Sun only warm), IP (own faces and clock, the sky sun now a plain ball at 24 s and 120 s), originality (unchanged from r1), opening (batch 8 is 2 `if` in 7; ep84 is also `if`, so don't upload them back to back), hard rule 8 (L10 "SIX" and L65 "held the LEVER" are clean).

## Must-fix
1. **[words] cover_s** (package.json): 73.8 sits one frame before the cut. S45 ends at 73.83 s in this timeline. The narration is voiced again on Actions, so a one-frame drift puts the cover on S46, the eye alone with "It was the SUN.", which spoils the twist on the thumbnail. Set `cover_s` to 73.3 (mid-S45: my face and the gold eye together).

## Nice-to-have
- `hold` still says "scripts only, not built yet", which is stale. Remove it once both reviews approve, or the daily upload will skip the story.
