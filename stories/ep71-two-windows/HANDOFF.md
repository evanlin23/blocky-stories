# ep71-two-windows: handoff (2026-11-03, about 10:50 AM Central)

Batch 6, slot P2 (creepy town rule, core, long). Branch `claude/ep57-two-windows` (the branch name keeps the old slug; the folder is `ep71-two-windows`). No PR is open, nothing is merged, and no proof or render has run, so there's no run id. There's no qa file.

## Where it stopped
- **Writer:** done. Cold-viewer test passed after one fix round. Blind first-line check: 9 (the real hits 4 to 8, median 7). That score was for the old opening. The new opening hasn't been re-tested.
- **Build round 0:** preview done (131.2 s).
- **Review round 1:** critic **revise** (`reviews/r1-critic.md`, creature 4/10 blocks), standards **revise** (`reviews/r1-standards.md`).
- **Fix round 1 (builder):** **stopped mid-run** by the orchestrator's handoff order, while it was editing `generator/make_story.py` (its last note was about handling `L35-0.2` offsets in `_at`). What's done is committed. What's left is unknown and needs checking.
- **Round 2 reviews:** not run. The orchestrator allows at most 2 review rounds from 16:40 UTC, so round 2 plus one rescue are still available.

## Round-1 must-fixes, and their state as far as we know
| # | Fix | State |
|---|---|---|
| 1 | Creature (the Server) reads cute and floats. Redesign it, test still first | **Unknown.** New stills exist in `out/work/ep71-two-windows/stills/` (not committed). Check `post-02754.png`, about 92 s |
| 2 | Flash miss: 3-frame changes 7 against 6 at 41.6 s | The 16:16 UTC preview's `flash.json` says `pass: true`, but it lists `general_3f_max_changes_per_s: 8` at 63.1 s. **Re-measure** on clean frames: delete `out/work/ep71-two-windows/frames-preview` first (stale frames gave false readings) |
| 3 | `musicbox` changed to `piano` in 3 music sections (hard rule 6) | done in story.json |
| 4 | Opening: sleeve and hand in S001, hatch centred, punch-in at 1.2 s, second hatch visible in S002 | Unknown. Superseded in part by the new opening (below) |
| 5 | Reveal at 94 to 98 s: both hatches at one framing, L54 over the windows | Unknown |
| 6 | No shot over 2.0 s (S110 is 3.6 s) | Unknown |
| 7 | Cracked headlight drawn as a crack, not a yellow "envelope" | Unknown |
| 8 | The 41 tickets in frame in the Cal close-ups (47, 56, 75 and 103 s) | Unknown |
| 9 | A fourth copy car in S081 and S109 (L70 now says FOUR) | Unknown |
| 10 | Key colour moved off ep25's green | done: `#6fd13a` |
| 11 | Black occluder in S054 at 62.9 s; intersections | Unknown. Run the new clip check, and put overlaps we intend in `clip_ok` |
| 12 | Polish hints, `"sfx": "door"` | Unknown. Polish v2 is on, `ones` at its default |

Words already changed (in script.md): L12 "I'm a GROWN MAN.", L32 "EXACTLY like / last TIME.", L70 "our FOUR old LAPS".
New opening (opening-variety rule, PR #142): L01 "This DRIVE-THRU / has ONE booth / and TWO WINDOWS." (hit on WINDOWS, at most about 2.2 s), L02 "Never pull up / to the SECOND one.", and `"opening": "count"` in package.json. All three are in place. Whether L01 and L02 were re-voiced, and frame 1 reframed onto both windows, is **unknown**.

## Next
1. `git pull`, merge origin/main, and check the voice timings for L01, L02, L12, L32 and L70.
2. A fresh builder finishes the unknown rows above, deletes `frames-preview`, and renders a new preview. Then `check`, flash, the clip check and `python scripts/measure.py --story stories/ep71-two-windows`.
3. Round 2: the critic and standards (both said revise).
4. Once both approve: the proof run (`proof.yml`), then the qa agent at stage proof. Merge once `test` is green and qa passes. Then the final render and qa on `film-ep71-two-windows`, then queue.txt.
5. Upload spacing (standards): at least a week from ep49-car-wash, and not next to ep62 (the same count-title shape).
