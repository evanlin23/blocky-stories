# ep137-trail-board: standards, build round 1 (r2)

Verdict: revise

I walked all 39 shots of the preview at 300 px, one frame each, and also checked the S08 tally and the cover frame. Fiction passes. The board is our own block glyphs: squares, bars, 2x2 grids and stacks of three. None reads as a letter, a word or an arrow at phone size, and the "II" tally passes as a number. There are no real names, and the description says "It's made up." Kids passes: all four are adults, there's one face per shot, S24 has June plus a soft shoulder, and June is never shown in danger. IP passes. The flash preflight passes (max 1 flash a second, a 0.73 s extended run from 26.4 s, no red). The 1.6 s S15 fade is slow and the S11 sun is not clipped. Originality passes against the earlier stories. The package passes: "DUSK" is the one caps word, 🌲 is the one emoji at the end, the pin starts "Comment 1 or 2", the opening is `must` and matches L01, there are no dashes, and `hold` is left on purpose.

## Must-fix
1. **L27 / S27 (51.0 to 52.3 s): round-1 must-fix 2 was never applied.** The line is still "Which board / do I TRUST?". ep136 L32 ends "Which echo / do I TRUST?" and ep138 L31 ends "Which me / do I TRUST?", so three uploads in a row would close on the same line. That is the "superficial differences" pattern hard rule 5 exists to stop. Change L27 to "Which board / do I FOLLOW?" with FOLLOW as the key word. Change it in script.md and in story.json (both the caption and the spoken chunk), then re-voice L27. This matches the pin and still loops into L01.

## Nice-to-have
- `cover_s` 24.3 lands on S12: a dim board with no face and the caption "Theo doesn't walk". About 26.3 (S13: my face lit orange in front of the board) fits RULES → Cover better.

## Queue spacing
- ep136, ep137 and ep138 share the shape `open-choice` and the "Comment 1 or 2" pin. Never put two of them next to each other, so keep at least one story between each.
- ep137 is a `must`. Keep it away from ep89-sister-diary and ep28-lamp-room, which are also `must`. Do not put it next to ep138 either, because both titles open "The ...".
