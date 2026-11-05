# ep117-glow-secret: standards r2 (first build review, preview, 2026-11-05)

Verdict: approve

r1's flash fixes are in. Mom's flare (S23, 29.5 to 30.07 s) rises smoothly over 0.57 s (frame mean 120 to 129, nothing clipped), then cuts to the gumball shadows (S24). The lot shots (S11 to S13 in the script, 13.2 to 21.5 s) stay in the lot's blue and each holds 0.6 s or more, with no clipped bloom. All 33 voiced lines match the script.

Passes:
- **Fiction:** the set has no words anywhere. The tag shows a bulb glyph, bars and dots only, and the pizza box is plain. The description says "It's made up."
- **Kids and mature themes:** everyone reads as an adult (me 27, Mom, Dad, the roommate, the planner, the bus-stop woman). Nobody is in peril or hurt. `made_for_kids` is false.
- **IP:** the faces, mustache, glasses, plaid and shades are our own. No game name anywhere.
- **Originality:** shape `tiny-secret` is new. The lie tags in ep47 and the half glyphs in ep54 are different rules with different twists. ep118's "thirty years" overlap was fixed on ep118's side (forty years).
- **Flashing:** preflight PASS. general 1/s, 3f 3/s at 29.17 s (S22 to S24), 3f extended 1.23 s from 24.6 s, red 0. One very-different cut at 33.13 s (S25 Mom at the gumballs to S26 Dad in the dark lot, mean 118 to 77) stands alone. Nothing here is near a strobe or a 4 s busy run, so the full-rate proof should pass.
- **Package:** title, pin "Comment PIZZA…", US English and hard rule 8 pass. `confess` matches L01. Batch 12 has one of each opening shape.

Must-fixes: none.

Before merge (orchestrator):
- The `"hold"` in `package.json` still says "scripts only, not built yet". Remove it once proof qa passes. While it's there, the story won't render or upload.

Queue spacing:
- At least 2 uploads from ep118 (r1), and from ep112 (also a decades-long family pretense played for comedy, also `confess`).
- Not next to ep83 (Mom and a diner), ep47 (a body marker for hiding the truth) or ep113 (a "Glows" title).

Nice-to-haves:
- **Cover:** `cover_s` 48.6 now lands on L28 "I wouldn't TELL" before I glow. The script's cover is L30 (S39). Set it to 51.2 ("GLOWING", my lit face).
- **L20:** `check` warns that "Same glow. / Same PROMISE." reads like a slogan. If L20 gets re-voiced, try "He glowed the same, / and made me PROMISE too."
