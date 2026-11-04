# ep89-sister-diary: handoff

**Status:** approved. The PR is open and the proof is next.

## History
1. It was dropped at the 2-round cap, then revived by the second orchestrator for one targeted fix.
2. Round 2 critic: approve (`reviews/r2-critic.md`). Average about 7.1, hook 8, nothing under 5.
3. Round 2 standards: revise. Two black shots, S35 and S59.
4. Both shots were fixed with new cameras (rev 11). The darkest of all 3672 frames averages 55.8/255, and none is under 50.
5. The standards re-check approved (`reviews/r3-standards.md`).

## Before the PR
- `hold` was removed from package.json.
- check: passes.
- gate: OPEN.
- pytest: 201 passed.

## Next
1. proof.yml draws the proof on the PR.
2. The qa agent checks it at stage proof and writes `qa/ep89-sister-diary.json`.
3. Merge once qa passes and `test` is green.

## Notes
- The full-rate flash check on the bright shots was not run locally. The proof covers it.
- L51c shows Nina's face, not the dust-blow (the critic accepted it).
- Nina's ponytail doesn't show.
- Engine: `render --force` leaves stale frames. Delete `out/work/<story>/frames-preview` first.
