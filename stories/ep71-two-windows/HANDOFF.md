# ep71-two-windows: handoff (2026-11-03, about 10:50 AM Central)

Batch 6, slot P2 (creepy town rule, core, long). Branch `claude/ep57-two-windows` (the branch name keeps the old slug; the folder is `ep71-two-windows`). No PR is open, nothing is merged, and no proof or render has run, so there's no run id. There's no qa file.

## Where it stopped
- **Writer:** done. Cold-viewer test passed after one fix round. Blind first-line check: 9 (the real hits 4 to 8, median 7). That score was for the old opening. The new opening hasn't been re-tested.
- **Build round 0:** preview done (131.2 s).
- **Review round 1:** critic **revise** (`reviews/r1-critic.md`, creature 4/10 blocks), standards **revise** (`reviews/r1-standards.md`).
- **Fix round 1 (builder):** **stopped mid-run** by the orchestrator's handoff order, while it was editing `generator/make_story.py` (its last note was about handling `L35-0.2` offsets in `_at`). What's done is committed. What's left is unknown and needs checking.
- **Round 2 reviews:** not run. The orchestrator allows at most 2 review rounds from 16:40 UTC, so round 2 plus one rescue are still available.

## Fix round 2 (2026-11-03, Sonnet builder): state of every round-1 row
| # | Fix | Final state |
|---|---|---|
| 1 | Creature | **Redone** in `set.py` `build_server`: shoulders fill the hatch, a pale head with a black hollow face, two narrow bright eyes and a wide row of teeth, a neck that joins head to chest, thick arms with long fingers; it faces the lane (head turned toward the camera) and leans out over the sill. Reveal cameras (S082/S083/S084) moved to a 3/4 view over the car. Test still at 92 s: `out/work/ep71-two-windows/stills/post-02760.png` (not committed) |
| 2 | Flash | Re-measured on clean frames (`frames-preview` deleted before the render); see the result line below |
| 3 | `musicbox` to `piano` | done |
| 4 | Opening | New: S001 is an oblique, close-in view along the wall with both hatches in frame (hatch one lit, the 41 bag on hatch two). A frontal frame can't make two windows 10 m apart read bigger than about 12% of the width each |
| 5 | Reveal 94 to 98 s | S085 to S087 are one framing: both hatches, camera over the bush at 2.3 m, lens 9.6 to 10.2 (the engine's sensor is 24 mm vertical, so width = 13.5 x distance / lens) |
| 6 | No shot over 2.0 s | done (longest 1.87 s) |
| 7 | Cracked headlight | A dim grey lens with a five-segment black jagged line, 1 cm proud, no yellow |
| 8 | 41 tickets in close-ups | Three ticket rows (right corner, middle, left corner) stand on the dash, 0.12 x 0.17 m, so every in-car close-up has them in frame |
| 9 | Fourth copy car | copyA to copyD already built; S088/S089 (L55) and S115/S116 (L70) now look down the back wall so all four read; L70 says FOUR |
| 10 | Key colour | done: `#6fd13a` |
| 11 | Black occluder, intersections | the S057 shot no longer shows one; `clipcheck`: 0 clips (the Server's head is kept above the sill and clear of Cal) |
| 12 | Polish hints, door sfx | `emph`, `reveal`, `twist` (L53) set; `"sfx": "door"` on Cal at L08 and L69; sound budget cut to 3.9 events per 10 s (clicks, whooshes on cars and the glitch removed) |

Make_story: `_at` now writes `L35-0.2` plus an offset as `L35+1.0` or `L35-0.1`, never `L35+-0.1`. `sound.rev` bumped to 3.

Words already changed (in script.md): L12 "I'm a GROWN MAN.", L32 "EXACTLY like / last TIME.", L70 "our FOUR old LAPS".
New opening (opening-variety rule, PR #142): L01 "This DRIVE-THRU / has ONE booth / and TWO WINDOWS." (hit on WINDOWS, at most about 2.2 s), L02 "Never pull up / to the SECOND one.", and `"opening": "count"` in package.json. All three are in place. Whether L01 and L02 were re-voiced, and frame 1 reframed onto both windows, is **unknown**.

## Next
1. `git pull`, merge origin/main, and check the voice timings for L01, L02, L12, L32 and L70.
2. A fresh builder finishes the unknown rows above, deletes `frames-preview`, and renders a new preview. Then `check`, flash, the clip check and `python scripts/measure.py --story stories/ep71-two-windows`.
3. Round 2: the critic and standards (both said revise).
4. Once both approve: the proof run (`proof.yml`), then the qa agent at stage proof. Merge once `test` is green and qa passes. Then the final render and qa on `film-ep71-two-windows`, then queue.txt.
5. Upload spacing (standards): at least a week from ep49-car-wash, and not next to ep62 (the same count-title shape).

## Round-2 results (preview, 131.9 s)
Flash PASS on the new bar (3-frame: 3 flashes, 7 changes at 3.7 s, a warning only). Clip check 0. Preflight 0 blocks. Measure: 0 blocks, 1 warn (cuts 8.9 per 10 s). Preview: `out/work/ep71-two-windows/ep71-two-windows-preview.mp4`. Next: round 2 reviews, then proof.
