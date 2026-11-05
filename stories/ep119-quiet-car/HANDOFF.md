# ep119-quiet-car handoff (batch 12)

Stopped at: usage limit hit during fix round 1 (resumes after the Thursday 8 AM Central reset).

## State
- Built through preview. Round 1 reviews: standards approve; critic revise (avg ~6.6, faces 4, lore 4). See reviews/r1-critic.md and r1-standards.md.
- Fix round 1 builder (10 critic must-fixes + standards nice-to-haves: count monotonic and held at 1,724 L45-L59, S66/S70 fog 60%, hold text) was cut off mid-run. Its edits are committed as a WIP checkpoint and are UNVERIFIED: it had not yet run flash (full rate), measure, preflight, or the drop-loudness check, and had not viewed the changed shots.
- This is review round 2 of 2 (the fix round). Only the critic re-runs. Then at most one single-fix rescue.

## Next
1. Fresh builder: check every r1-critic must-fix is really in (S29 and both drops at 31.7 s / 80.7 s must not be dead silent; S34, S65, S86, S54, S79/80, S93/94, S16/S22/S59/S60/S74, S46, count monotonic), then preflight 0 blocks, framing.py 0 findings, preview, flash full rate, measure.
2. Flash target from the second orchestrator: 3 per second or under locally, no extended run over 3 s (local check reads low; train-window light flips brightness). Soft slow window passes.
3. Merge origin/main, run critic (opus) round 2. If approve: remove "hold", check, gate, pytest, open PR "ep119-quiet-car: build (batch 12)", proof, qa proof, merge on green test.
4. Queue spacing note for PR: keep ep119 at least 3 uploads from ep120-last-words; not adjacent to another `ban` story, ep62-six-riders, ep28-lamp-room.
