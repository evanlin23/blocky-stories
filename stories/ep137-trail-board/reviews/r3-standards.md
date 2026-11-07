# ep137-trail-board: standards, build round 2 (r3)

Verdict: approve

This round only checks whether the last round's must-fix went in, plus any regressions from the fix pass. I pulled 300 px frames at S01a, S05, S06b, S09b, S10, S15, S16a, S16b, S17, S18, S19, S20 to S27 and the cover (26.3 s).

## Round-1 must-fix
1. **L27 "Which board / do I FOLLOW?": fixed.** It's in script.md, in the story.json caption and spoken chunks, and in vo/voice.json ("which board do i follow?"). L27.wav was re-voiced before the mix. On screen at 51.5 to 52.5 s the caption reads "do I FOLLOW?" on Theo's close-up. It no longer repeats the "do I TRUST?" ending of ep136 and ep138. It still loops into L01.

## Regressions from the fix pass
- **L24 "June's going, / with or without ME."** The caption, chunks and voice all match, and it plays in S24 at 46.9 to 48.4 s. There are two faces at most, and June is never shown in peril. Pass.
- **Blank green trail marker at the path mouth (S20 and S22):** it has no glyph, letter or word on it. Pass on fiction.
- **Bench moved:** in S15 and S16a the bench sits empty off the path. June's bench in S17 and S24 is consistent with it. No broken frames. Pass.
- **Flash:** preflight passes (general max 1 a second, no red). The 3-frame 1.37 s run from 30.97 s is the slow S15 sunrise fade, which is indicative only. Pass.
- **Package:** `cover_s` 26.3 now lands on S13 (my face lit orange in front of the board), which applies the earlier nice-to-have. `opening` `must` matches L01. `hold` is kept on purpose. Pass.

No must-fixes. No should-fixes.

## Queue spacing
- ep136, ep137 and ep138 are all `open-choice` with a "Comment 1 or 2" pin. Keep at least one story between each.
- ep137 is a `must`. Keep it away from ep89-sister-diary and ep28-lamp-room, which are also `must`.
- Don't put it next to ep138 ("The Gym Where...") either, because both titles open "The ...".
