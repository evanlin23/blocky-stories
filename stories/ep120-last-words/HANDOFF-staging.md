# ep120-last-words: staging fix stopped (2026-11-07)

PR #383 (branch claude/ep120-last-words-staging-fix). Stopped after the one allowed rescue. Nothing is merged, and the old final (with the fused bodies) still stands.

## Done
- **S16 (the photo, 16.10–17.60 s):** me and dad are spread from 0.80 to 1.50 m. The lens is 17.5 and the push 0.1 m. It was already in polish.hold. Both the critic and the proof qa say it's fixed.
- **S81–S84 (the café table):** the chairs and seat keys are spread from 0.90 to 1.42 m (`CH`; set.py chair x). All four table cameras' lenses are 20.5.
- **S05/me+neighbor:** in `staging_ok`.
- `staging.py`: 0 findings.

## Why it stopped
The proof qa (run 42312415046, artifact 13552291548, qa/ep120-last-words.json) failed:
- **S81–S83 (111.3–115.1 s):** the pace crop cuts both heads at the side edges. S82 (113.0–113.9 s) is worst, with about half my head out on the left. The drawn frames were fine. The post crop (push and reframe up to max_zoom 1.18) is what cuts them.
- **S84 (115.5–116.3 s):** my raised arm still touches dad's plaid.

## A likely clean fix (one pass)
1. Add the S81–S84 shot names (`names["table2"]`, `names["sorry"]`, `names["laugh2"]`, `names["cold_eggs"]`) to `polish["hold"]` in make_story.py, which turns off the pace crop. Or widen those lenses to about 17.5. Pace has margin: the preview read 20.8 at 0.25 s against 14.
2. In S84, lower or turn in my raised arm (the `arms` on my L68 beat), or add 0.1 m to `CH`.
3. Check at the worst-case crop: crop the drawn frames by max_zoom, centred, before calling it done.
