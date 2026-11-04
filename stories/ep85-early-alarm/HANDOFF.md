# ep85-early-alarm: handoff (dropped, 2026-11-04)

**Status: dropped.** It wasn't approved after the 2 review rounds the batch-8 brief allows (no rescue round). No PR was opened.

## Where it stands
- It's fully built: the creature test passed on try 2, the set, story.json (rev 12), the voice and preflight are done (0 blocks), and the preview is 129.3 s.
- Checks on the last preview:
  - measure 0 block / 0 near / 2 warn (face_big_share 0.363, character_motion_shot_share 0.423)
  - sound 2.09 events per 10 s
  - flash passes (worst 3f 3/s at 95.13 s, red 0)
  - clipcheck 0 clips
  - true peak -1.8 dBTP, -14.1 LUFS
- `hold` is still in package.json.
- Reviews: `reviews/r1-critic.md`, `r1-standards.md`, `r2-critic.md`, `r2-standards.md`.

## Last verdicts
- **Critic r2: revise.** Average 7.3. Scores: hook 8, back-row 8, narrator 9, appeal 9, relationships 8, feeling 7, big idea 8, eerie 6, creature 6, twist 7, lore 7, warm turn 7 (up from 4), variety 7, faces 5, sound 8, captions 7. All 7 r1 must-fixes were fixed.
- **Standards r2: revise.** All 3 r1 must-fixes hold.

## Open must-fixes (all small, no words change)
1. [critic] S65b (116.13 to 116.97 s, L65 "and I CRANKED"): my head is behind the clock inset the whole shot. Lower the camera or move me left.
2. [critic] S68 (120.47 to 121.27 s, L68 "Dad watched it / with somebody"): Dad's face is cut off at the left edge and washed out. Frame both faces whole, as in S68b.
3. [standards] package.json `cover_s` 73.8 becomes 73.3 (mid-S45; 73.8 is one frame before the cut to S46, which gives away the twist).
- Advice: in S67 (118.3 to 119.5 s) the rising Sun reads as a yellow cloud or flower before it turns round.

## If someone picks it up
The three fixes are about an hour of work: two reframes in generator/make_story.py, a re-render of those shots, and the cover_s edit. After that it would need a fresh review round and the proof. That's for an orchestrator to decide. No engine bugs were found.
