# ep94-today-again: handoff (DROPPED, 2026-11-04)

**Status: dropped.** It wasn't approved after the two review rounds the batch-9 brief allows, and the brief has no rescue round. There's no PR.

## Verdicts
- Standards r1: revise. S60 went black for a moment, and the `hold` was out of date.
- Critic r1: revise, with 12 build must-fixes.
- Standards r2: **approve** (`reviews/r2-standards.md`).
- Critic r2: **revise** (`reviews/r2-critic.md`). Scores: hook 8, back-row 7, narrator 8, appeal 9, relationships 7, feeling 6, big idea 7, eerie 6, twist 8, lore 5, warm turn 6, variety 8, faces 5, sound 7, captions 8. All 9 hits points are yes, and the average is about 7, but faces is 5.

## Open must-fixes (critic r2). All are camera framing or a material change; no voice or timing change
1. S72, L32 "Her hands were COVERED" (56.57 to 57.3 s): the shot is a blue sleeve with no hands or glitter, so the glitter plant never pays off. Frame Pearl's two hands, thick with glitter, over the cake.
2. S77, L34 (60.7 to 61.97 s): Mom is headless and the caught cup is out of frame. Pull back or tilt up so her whole head and the cup show.
3. L39 clipboard close (68.0 to 68.9 s): her head is cut at the eyes with no bun, so it reads as someone else. Show Mom's whole head and bun above the board, or crop below the chin.
4. Okafor (48 s and 56 s): at 300 px the beard reads as a surgical mask. Make it grey and textured, with a mouth line.

## State
- Built, voiced and previewed (83.4 s, 98 shots). Preflight shows 0 blocks, flash passes on the preview, clipcheck is clean, and measure has 0 blocks and 0 near (warnings only for cuts per 10 s at 11.76 and dead-stop walks at 0.53).
- The fixes look small: one builder round, then a critic-only re-review. If the orchestrator grants another round, start there. Otherwise the story stays dropped.
- `"hold"` is still in package.json.
- The engine was never touched. A story-level bug in `set.py` was fixed: props added after the first pose kept drawing while the character was hidden.
- Not a fault in this story: standards r1 says `if` opens 4 of ep90 to ep99, over the one-in-three limit. ep94 opens on `count`.
