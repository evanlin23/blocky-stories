# dryer-nine: handoff (2026-11-03, 10:50 AM Central)

Batch 6 slot P4 ("Nobody Uses Dryer NINE 🧺", lane core, shape `price`, opening `cost`). The batch moved to a second
orchestrator, so this session stopped here.

## Where it stands
- **On main:** the whole story, approved by critic and standards in round 4 (PR #139, the new `cost` opening in
  PR #150, the font-path fix in PR #141). `python -m blocky gate dryer-nine` is OPEN.
- **No passing final yet. No `qa/dryer-nine.json`. Not in `queue.txt`.**
- **The only final so far** is artifact `film-dryer-nine` (id 13242600462) from render run 41638682740 (run 78). It
  **failed the house flash bar**, and it was also drawn **before** the `cost` opening merged, so it has the old line 1
  either way. Its report fails one reading: 3-frame changes 7/s at 56.47 s (cap 6), with a 1.53 s extended run from
  54.47 s. That's the dark climax stretch S47 to S52 (the 7:30 timer, the door ring, the shut door, the dark window).
  3-frame flashes also sit exactly at the limit (3) at 23.7 s (S21 to S25, the arm wrestle).
- Run 79 (the `cost`-opening merge) was cancelled by later merges. A later render on main (run 86 or after) may have
  drawn dryer-nine again from main. If it did, check that film's `flash.json` first: it still has the dark-climax
  problem unless the fix below lands.

## The flash fix (the lead's "one post-render fix", unfinished and unverified)
- **Branch:** `claude/p4-dryer-nine-flash` (from main). **No PR yet.**
- **WIP commit:** edits to the per-shot exposure table `GAIN` in `generator/make_story.py`, plus the matching
  `xg`/`dx` cues in `story.json`.
  - It darkens the room fill through L16.3 to L19 (`xg` 0.3, 0.2, 0.1, 0.6).
  - It halves the drum light at L39.2 (`dx` 16 to 8).
  - It lifts the L39 face light (90 to 125).
- The builder was stopped mid-way, during a full-rate render of the touched shots. **None of it has been
  flash-measured.** It may not address 54 to 58 s (S47 to S52, `GAIN` keys L47 to L50) at all, which is the stretch that
  actually failed.

## What's next (whoever picks this up)
1. On the branch, delete `out/work/dryer-nine/frames-preview` (stale frames gave a false flash failure once today).
2. Fix 53 to 58 s (L47 to L50: lift the near-black timer and window shots, ramp the cut into S52) and 22 to 25 s, at
   story level only. The narration and L01/L02 stay as they are.
3. Render those shots at **full rate** (not `--preview`) and run `python -m blocky flash` on them. Target 3-frame ≤2
   flashes and ≤5 changes, 1-frame ≤2/≤4, no extended run. The preview passed at the limit, and the final still failed.
4. Run check and preflight, then PR and merge once `test` passes. The story.json change triggers the redraw.
5. Download the new `film-dryer-nine` and run the qa agent strictly: the first 3 s against the opening recipe and the
   `cost` tag, the creature at phone size, and flash. Write `qa/dryer-nine.json`. If qa passes, add it to `queue.txt`,
   spaced from town-rule and `cost` stories.
6. The lead's rule: **if this next final fails flash or qa, drop the story.**
