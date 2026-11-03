# warm-shoes: handoff (2026-11-03, 10:20 AM Central)

## State
- Merged on main in PR #149. Critic and standards both approved in round 3.
- The first final (render run 41638682740, artifact `film-warm-shoes` id 13241014928, 137.7 s) passed the flash check (general 2/s, 3f 3/s, red 0) and the audio check (-14.1 LUFS).
- That final **failed qa**: `qa/warm-shoes.json`, merged in PR #169. The story is not in `queue.txt`.
- This is the one allowed qa fix. If the re-rendered film fails qa again, drop the story.

## The fix (branch `claude/warm-shoes-qa-fix`, not merged)
1. **The qa must-fix: S91/S92, 103.65 to 104.6 s.** Biscuit's face slid up the front of the boot (clipping). He now starts inside the boot's thickness (x 1.80, y -10.04). Checked on one still only (104.1 s): he's hidden, but a few thin whiskers poke out to the right.
2. **Cover:** `cover_s` 9.9 is Biscuit's lit face at the cat flap. It doesn't show the tall form.
3. **S79 (the still at about 91.5 s):** the lens now zooms 135 to 185 mm with a slight drift. Not looked at yet.

No preview, preflight or `measure.py` run exists for this state yet. The voice is unchanged.

## Next step
1. Render S91/S92 (103.3 to 104.8 s) every frame and look at each one.
   - Hide the whiskers too, by moving Biscuit slightly left or deeper.
   - Check S79's move by eye.
2. Clear `out/work/warm-shoes/frames-preview`, re-render the preview, then run `python -m blocky preflight warm-shoes` (it should show 0 blocks and flash PASS) and `python scripts/measure.py --story stories/warm-shoes`.
3. Open a PR from this branch and merge it once `test` passes. The merge re-renders the final on Actions.
4. Download the new `film-warm-shoes` and check its flash report.
5. Run the qa agent on it.
   - If qa passes: add `warm-shoes` to `queue.txt` in a small PR, away from other town-rule stories.
   - If qa fails: drop the story.
