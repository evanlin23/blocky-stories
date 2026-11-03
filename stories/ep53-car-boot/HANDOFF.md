# ep53-car-boot handoff (2026-11-03, round 5 fix pass done, reviews not yet run)

**Where it stopped:** the round 5 fix pass (after r4 critic and r4 standards, both revise) was mid-way when the orchestrator paused all work. The last commits on `claude/ep53-opening` hold the fixes made so far.
- **Done:**
  - L01 is "The SCARIEST coat / never changes COLOR." (re-voiced), and L02 "ESPECIALLY / your OWN." is unchanged.
  - The title is "The Coat That NEVER Changes 🧥".
  - `"opening": "cost"` is set.
  - The Tilted model is rebuilt (head on the neck), the opening is restaged, and the long shots are split.
  - Light and flash tuning on the trunk lamp, and Pip's face shot is merged into the go shot.
  - US English: TRUNK, SWEATER, BUS.
- **Uncommitted when paused:** small `make_story.py` and `story.json` edits, committed with this note as they stood. Run `generator/make_story.py` again before trusting story.json.
- **Not verified:** the latest preview may predate the last edits. Nobody has reviewed round 5.

**Next:**
1. Pull main. It has polish v2.1, PR #143 (the near-black red fix) and the opening-variety rule.
2. Regenerate story.json, then run `timeline`, `preflight` (0 blocks, flash clearly under the bar) and `pytest`.
3. Re-render the preview (`render --preview --force` on changed shots, `finish`, `mix`), plus a whole-film key-beats sheet and a first-3-s strip.
4. Check every must-fix in `reviews/r4-critic.md` and `reviews/r4-standards.md`.
5. Run round 5: critic and standards. This is the last full round, plus one rescue round for a single named fix. If it can't pass, drop it with a hold line.
6. At ship:
   - Remove `hold` from package.json and confirm `cover_s` on a face-lit Tilted frame.
   - Write the pin: "Comment WHITE if you always let someone else decide."
   - Add the story to `queue.txt`.
   - Open the PR, then merge once `test` passes.
7. After the final render, run the qa agent and write `qa/ep53-car-boot.json`.

**Since the pause:** polish v2.2 (#168) and v2.3 (#175) are merged. When you pull main, check the following against builder.md and docs/engine.md → The polish pack:
- Keep ep53's own sfx to 2 to 4 events per 10 s. Round 4 added a lot of hits.
- Mark the frame-exact shots with `"hold": ["Sxx"]`: the coat comparisons and the trunk.
- Keep the quiet span over L60 to L68 short enough to pass pace.

## Round 5 builder pass (done, 2026-11-03; no reviews run yet)
- story.json regenerated, `sound.rev` 3. Clips fixed (Pip off the kitchen door and the shelter back: SHELTER_P x -13.4, doorway x 98.05). Own sfx thinned (13 events cut); measure: 2.64 events per 10 s, 0 blocks.
- `look.polish.hold`: S02, S09, S23, S31, S60, S67, S68, S84, S85. Quiet span L60-L68 unchanged and passes pace.
- Trunk close (S84 to S85) now snaps at the cut, bootb lamp held up: that was the only flash failure (124.3 to 124.9 s, 3f changes 7). Door sfx moved to the cut.
- S64 (face to face) reframed so both faces show (lens 21, aim [-1.3, -0.1, 1.95]).
- Preview: out/work/ep53-car-boot/ep53-car-boot-preview.mp4 (136.1 s). Sheets: out/ep53-first3s.png, out/ep53-keybeats.png.
- Not done: the S71 (103.7 s) fill is still about luma 108, not 120 (the S69-S73 flash numbers now pass with margin so left as is); warm fill in the opening for the cream anorak not applied. `pytest` needs `pip install pytest` in the system python (171 pass).
- Remember: `python -m blocky timeline` must be run after make_story.py, or render reads the stale out/work timeline.json.

## Round 5 critic must-fixes applied (2026-11-03, no reviews run)
- S64: camera side-on from -x (long lens 34 to 42, pan), Tilted lean 48 (face about 40 cm from mine), me turned to face it (yaw 215, at [-1.0, -0.45]); both heads whole above the captions.
- S67: new light preset `goldlo` (sun 1.9, rim 1.5) cued L53 and back to `gold` at L54; camera pulled back to show the cuff and the table edge.
- S41/S42: long lens from further back (lens 50/52 from [-13.5, -10.5] / [-9.5, -8.0]); silhouette colour lifted to #1b212d so the sideways head reads against the fog.
- S02: camera x -0.2, lens 17 to 19, my face whole at the left.
- Not done: S62 hair advice. `sound.rev` 4.
- Preview re-rendered (S02, S41, S42, S64, S67 forced), finished, mixed: 136.1 s. Flash PASS (max 1 flash/s, 3f 2), preflight 0 blocks, measure 0 blocks, pytest 171 pass.

## DROPPED (2026-11-03, after review round r6)
Two review rounds (r5, r6) used; no rescue round allowed by the brief. Not approved.
- r5: standards **approve**; critic **revise** (avg 7.2).
- r6 critic: **revise** (avg 7.2, every score 6+, all 9 hits yes). Open must-fixes:
  1. S02 (1.97 to 2.23 s, under "ESPECIALLY"): drawings f00059 to f00066 are solid black (luma ~25 vs ~170 either side). The r5 reframe (camera x -0.2 move) likely starts inside a prop or figure.
  2. S41 to S42 (60.8 to 64.7 s): still a close, dark heap of chair blocks; sideways head doesn't read. Needs long lens from the hedge, figure about a third of frame height.
  3. S64 (92.8 s, "face to FACE"): lean reads, but faces ~1 m apart; bring to ~40 cm or change L50 line/caption.
- Passing: flash, preflight 0 blocks, measure 0 blocks (one warn walk_dead_end_share 0.5), pytest 171, S67 fixed.
- Branch claude/ep53-opening holds all work. No drop PR (second orchestrator records drops on main). `hold` left in package.json. Not added to queue.txt.
