# ep97-prize-bears: handoff (dropped for good, 2026-11-04)

**Status: dropped.** It passed review: critic r3 approved after the one rescue round the second orchestrator granted, and standards r2 approved. Then the **proof failed on flash** (run 41860945381, sha bd60346, artifact `proof-ep97-prize-bears`). The rescue round was the last one ("a fail drops it for good"), so no further fix round. PR #267 stays open but unmerged; the second orchestrator decides whether to close it.

## Why the proof failed
`verdict.json`: `flash: fails the house bar`. Only one sub-check failed:
- **`general_flashes_le_6`: false.** `general_max_flashes_per_s` is **7 at 45.13 s**, and the 3f measure reads 10 per s at 45.23 s.

That's the closet bulb swinging over the bears (S24 to S26). Standards r1 flagged it (9 per s on the preview); the swing was halved, but at full rate it's still over 6.

Everything else passed:
- Extended runs: general 3f longest is 3.07 s and extended is 3.5 s at 10.5 s, both under 4 s.
- Red flash: 0.
- Craft: all ok, with warns on cuts per 10 s (10.55) and saturation (0.418).
- Mix: -14.0 LUFS, true peak -2.0 dBTP.
- Clip: 2 shimmer hits, S03b and S30b, both on `clip_ok`.

## If anyone ever revives it
The likely fix is small: hold the closet bulb still in S24 to S26 (no swing), or swap the swing for a slow brightness breathe below flash amplitude. Then re-run `python -m blocky flash` at full rate over 40 to 47 s, aiming for a max of 4 or fewer flashes per s. The critic r3 notes (ring post at S36, the yellow shape at 64.8 s) were advice only. At queueing, keep it 3 slots from floor-thirteen (standards).

## Verdicts
- Standards r2: approve.
- Critic r3: approve (avg 7.2; hook 7, back-row 8, narrator 9, appeal 9, relationships 8, feeling 7, big idea 7, eerie 6, twist and loop 8, lore 5, warm 7, shots 6, faces 6, sound 7, captions 8).
- No proof qa was run, because the proof failed by itself.
