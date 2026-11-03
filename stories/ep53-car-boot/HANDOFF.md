# ep53-car-boot handoff (2026-11-03, paused for the usage limit)

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
