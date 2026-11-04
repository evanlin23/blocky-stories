# ep89-sister-diary: handoff (DROPPED, 2026-11-04)

**Status:** dropped at the 2-round review cap, following the brief: "AT MOST 2 ROUNDS IN TOTAL, no rescue round". No PR was opened. Everything is pushed on `claude/batch8-ep89-sister-diary`.

## Final verdicts
- **Critic, round 2: approve** (`reviews/r2-critic.md`). Scores:
  - hook 8, back-row 7, narrator 9, appeal 9, relationships 7, feeling 7, big idea 7;
  - eerie middle 6, twist 7, lore 6, warm turn 6, variety 7, faces 7, sound 7, captions 7;
  - average about 7.1, nothing under 5.
- **Standards, round 2: revise** (`reviews/r2-standards.md`). Every round 1 fix holds, but a brightness scan of every frame found two fully black shots that round 1 missed. That is a flash risk, and the rule marker drops out.

## Open must-fixes (picture only, both small)
1. **S35, 40.43 to 40.67 s ("I shut it."):** the diary lid covers the lens as it closes. Pull the camera back and up, for example to S17's fixed start, [-0.95, 2.25, 1.35].
2. **S59, 65.77 to 67.07 s ("Her door ... an INCH."):** the camera is inside a wall at y = -0.8, so the lamplight in the door gap never shows. Move it into the hall, around y = 0.2 to 0.5.

Afterwards, check that no frame's average brightness is under about 50/255.

## If someone rescues it
Those two camera moves are the whole job. After them:
1. regenerate, render the preview, finish and mix;
2. run preflight and a brightness scan;
3. re-run standards only;
4. remove `hold` from package.json, then run check, gate and pytest;
5. open the PR, wait for the proof, then run the proof qa.

## Other notes
- The full-rate flash check on S01, S05, S38 and S43 to S50 was not run locally. The proof would draw them.
- L51c shows Nina's face, not the dust-blow (the critic accepted it).
- Nina's ponytail doesn't show.
- In the 94 s and 112 s two-shots, the faces sit at the frame edges.
- **Engine note:** `render --force` doesn't delete stale frames. Delete `out/work/<story>/frames-preview` before re-rendering, or old and new frames mix and flash fails.
