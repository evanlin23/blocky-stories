# warm-shoes: handoff (2026-11-03, qa fix PR)

## State
- Branch `claude/warm-shoes-qa-fix`. qa fix done: S91/S92 Biscuit clip gone (checked every 0.1 s), cover_s 9.9, S79 zoom checked.
- Also cleared clipcheck blocks from the new engine: S58 and S67 by moving the figure back and cutting the lean; S09 head-in-pillow accepted with story.json clip_ok S09/bed_single (critic round 4, opus: approve).
- Preview: flash PASS, preflight 0 blocks, check ok, gate OPEN, pytest 171 passed. measure.py has 2 warns only (cuts/10 s 8.42, big faces 0.357).
- Voice unchanged.

## Next
- PR: proof.yml draws proof-warm-shoes; run qa stage proof; merge when qa passes and `test` is green.
- If proof qa fails again: drop the story.
