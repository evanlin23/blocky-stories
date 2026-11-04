# ep96-friend-card handoff

- **Status:** fix round 1 done: preview re-rendered, finished, mixed; preflight 0 blocks, flash PASS, clipcheck 0, 74.9 s. Ready for round 2 (critic, standards).
- **Round 1:** critic revise (hook 8, relationships 6, scare 5, faces 6, lore 4; must-fix S06 faces, S07 Abbott's face, S24a rooftop + tally), standards revise (opening recast confess -> cost, done in 6e6c5b60; shared skeleton with ep93, passed to ep93's session by the second orchestrator).
- **Fixes:** code for all four must-fixes and the L01-L03 re-voice is committed (83f93a9a). The container restarted twice during the preview render.
- **Resume:** the preview is re-rendering into a fresh `out/work/ep96-friend-card/frames-preview` without `--force`, so a rerun of `python -m blocky render ep96-friend-card --preview` resumes. Then finish, mix, a stills sheet (S01, S06, S07, S24a, the reveal), flash, measure, clipcheck, then round 2 (critic and standards; standards checks ep96 against ep93's new plan on `claude/batch9-ep93-recipe-card`).
