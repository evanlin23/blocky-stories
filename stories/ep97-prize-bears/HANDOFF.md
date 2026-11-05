# ep97-prize-bears: handoff (dropped for good, 2026-11-05)

**Status: dropped.** The one retry (audit decision 7) failed its proof on flash again. PR #290 is open and unmerged; the second orchestrator decides whether to close it. No proof qa was run.

## What the retry did
- Held the closet bulb still (no swing). It was NOT the cause (see below).
- Eased the S24b tilt and its fill; fixed 6 framing findings (S10a/b, S14b, S19a, S31b, S32a/b, S42a in framing_ok); fixed S32b opening on white (critic r1 must-fix).
- Reviews: standards r1 approve; critic r1 revise (S32b white open, one fix); critic r2 approve (avg ~7.75, lowest 6). check clean, gate OPEN, pytest 200 passed.
- Preview flash passed the house bar (general max 3/s, 3f extended 3.83 s), but the preview is quarter size with every 4th drawing, so it could not see what the proof sees.

## Why the proof failed (run 41965645205, sha 4399d74, attempt 2; attempt 1 lost shard 4 to a hung runner and was re-run)
verdict.json: `flash: fails the house bar`, two sub-checks:
- `general_flashes_le_6`: general max **7 per s at 45.13 s** (same as the first proof, 7 at 45.13 s).
- `general_3f_extended_under_4s`: the 3f extended run is **4.53 s from 37.67 s**. The 3f max is 10 per s at 45.23 s (also identical to the first proof).

Everything else passed: red flash 0, craft 0 blocks, clip 2 allowed shimmer hits (S03b, S30b), mix -14.0 LUFS, true peak -2.0 dBTP.

## The real cause (not the bulb)
The numbers did not move when the bulb stopped, so the bulb was never it. At 45 s the shot is **S24, the wall of about 40 bears** with the camera pushing and tilting across it. Mean brightness is flat (Y 131 to 135 over 44.9 to 45.5 s) but the dense pattern of dark eyes and orange bows on cream fur shifts under the camera, and the region-based flash measure (area threshold 0.1) counts those patches. S21b to S24b (37.7 to 46 s) adds fast bright/dark cuts that stretch the 3f run past 4 s.

## If anyone ever revives it
Rebuild the 37 to 46 s span so the bear wall is not a moving high-frequency pattern: hold the camera still (or a very slow pure push) on the wall, soften or defocus the shelf rows, cut the number of bears in frame, and cut the bright/dark alternation between S21b and S24b. Test on a FULL-RATE render of just 36 to 47 s, not the quarter preview, and aim for general max 4 or fewer and a 3f run under 3 s. Queue note if it ever ships: keep it at least 3 slots from floor-thirteen (met), after ep99-statue-years, 3+ from ep89-sister-diary, 2+ from ep94-today-again and ep102-aunt-peaches.
