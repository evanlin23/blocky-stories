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

## Flash fix, 2026-11-03 (second session)
- Finding: the lead's "S47-S52 / S21-S25" are line ids. In shots, the 54-58 s run is S47/S48/S49 (L39, L39.2, L40) and
  the 23.7 s run is the S19 to S20 cut (L15.3 to L16). The WIP did touch S47/S48.
- Cause of the 7 changes: a cut where more than 10% of the screen goes brighter AND more than 10% goes darker counts as 3
  changes (the detector flips direction each frame). The old film had two such cuts (56.6 and 57.4 s) one second apart,
  and 24.0 s had one more at the limit.
- Changes (generator/make_story.py, story.json regenerated): S46 rim 200 to 150; GAIN L15.3 (1.8, 3.0) to (0.2, 0.6),
  L39.2 dx 16 to 5, L41 dx 5 to 4, L41.2 dx 9 to 6, L39 face 90 to 125, WIP xg for L16.3 to L19. No cut, framing, words or
  narration change. dryer-nine has no `rev` key (it is under `sound`), nothing to bump.
- Proof-size measure (every drawing, post applied): 23-30 s run 3-frame 1 flash / 3 changes (was 3 flashes at 23.7 s on
  the final); 53-63 s run 2 flashes / 4 changes, extended 0.17 s (was 7 changes, 1.53 s).
  Left: double-sided cuts at 59.57 and 61.3 s and 29.03 s stand alone, each at least 0.9 s from other changes.
- Full-rate (final-quality, 540x960, every drawing, post applied) measure of the touched shots: 23-30 s 3-frame 1 flash /
  3 changes, 1-frame 1/2; 53-63 s 3-frame 1 flash / 3 changes, extended 0, 1-frame 1/2.
- Preview (step 4, whole film) flash: PASS (3-frame 2 flashes / 5 changes; worst seconds are 11, 43 and 68 s, outside the
  failed stretches; the 68 s extended run is 1.5 s). Preflight 0 blocks (one run showed clip and asr blocks while a
  flash run shared the machine; two clean reruns gave 0).
- `voice` rewrites voice-timings.json with split L01/L02 chunks (the cost opening); not committed here, CI makes its own.

## Head-clip fix (proof of PR #198 failed on 55 clipcheck hits only)
Fixed in `generator/make_story.py` (story.json regenerated, no cue/GAIN/camera changes): clipcheck 55 hits -> 0.
- S09 (L08): me x 0.85 -> 1.1 (jonah's sleeve).
- S22 (L17): towelman starts (-1.7,-1.5), basketlady (-0.7,-0.5) and leaves 1 m behind; she exits the door centre at L18 (no shared target).
- Standing pairs (S36-S45, S59): jonah stepped ~0.25 further from me at L29/L30/L31/L35/L37, and L48 (x 3.0); L51 hug jonah x 2.55 (S62).
- Seated pair (S52-S57): both moved 0.35 off nine's door (y 2.95 -> 2.6), me x 2.7, jonah x 3.62; L45 face-cam and its light follow.
- No `clip_ok` used. Not committed: voice-timings.json.
