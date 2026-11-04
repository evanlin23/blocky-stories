# ep101-well-wish: dropped (batch 10, 2026-11-04)

**Why:** the proof qa failed after the round cap was spent (2 review rounds + the single-fix rescue, RULES audit decision 3). No more fixes allowed.

## Open must-fix (proof qa, `qa/ep101-well-wish.json`)
Wes's `expr: "grin"` (blocky/faces.py: "the uncanny one", too many teeth) plus furrowed brows reads angry or sinister on warm beats, muddling the twist:
- 70.6-72.6 s, S92/S93, L40 "there he was on our PORCH again" (the payoff, worst)
- 37.3-37.8 s, S51, L21 "dream JOB"
- 14-16 s, S20-S22, L08 "my big brother WES"
- Also check the other grin keys: L12 S30-S31, L34 S79-S81.
Fix would be: swap to `smile`/`warm`/`delighted`. Cheap, so a future retry as a fresh story is plausible.
Should-fix: opening shows no face until Wes at 1.6 s.

## Scores / verdicts
- Standards: r1 revise (S92 near-black), r2 approve, rescue re-look (flash) approve.
- Critic: r1 revise (6 picture must-fixes), r2 approve (avg 7.4: hook 7, narrator 9, appeal 9, twist 7, lore 5).
- Proof 1 (run 41897297886) failed flash (general_3f_extended 4.27 s from 33.07 s); rescue darkened the living-room/bedroom walls.
- Proof 2 (run 41906475044, sha 597261f) passed craft, flash, clip, peak (-1.8 dBTP). Proof qa: FAIL (faces above).

PR #276 closed, not merged. Branch claude/batch10-ep101-well-wish holds everything. No engine bug blocked this.
