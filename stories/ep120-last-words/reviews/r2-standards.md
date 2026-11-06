# ep120-last-words: standards r2 (2026-11-06)

Verdict: approve

This round checks only the round 1 must-fixes and regressions. I used the redrawn preview (122.3 s), with frames pulled at 300 and 540 px.

## Round 1 must-fixes
1. **L22: fixed.** The line reads "One night, / it was there / at eleven. / Like ALWAYS." in script.md and story.json. voice-timings.json has the new L22 text ("One night, it was there at eleven. Like always."), and "Last night" is gone. The captions at 40.3, 41.2 and 42.0 s match.
2. **S41: fixed.** The dent lip is `#6fd88a` and rough (set.py:369), and the lens is 35. At 48.7 and 49.2 s it reads as a green thermos with a cap and a round dent. Nothing reads as a blade any more.
3. **cover_s: fixed.** It is 62.9. The frame is S50: my face in Dad's doorway inside the ripple, "Out LOUD.", tag at 0. No spoiler.

## Regression check on the critic's fixes
- **S34 (40.1 to 42.2 s):** the shape stays in the cab with the door shut. Nothing graphic, no flash risk.
- **S68 (89.8 to 92.0 s) and S61/S62:** the buzzer panel has four blank round buttons and no text, numbers or names, so it passes fiction. Dad is an adult.
- **S79/S80 (107.4 to 110.7 s):** the pan is on the stove and the toaster and black toast are on the counter. No text and nothing unsafe.
- **S11/S12:** the dog's ears now fold over. It's a made-up dog, no IP.
- `check` is clean. preflight reads `flash: PASS (3669 frames)`, but that json is from 04:26, older than the 05:28 preview, so it's stale. The caller checks the full like-proof report against the 5/s bar. None of the fixes adds a light drop or a bright pan.

## Should-fix (not blocking)
- S80: the toaster sits off to the left on the counter, not in front of Dad's face. That's the critic's call.

Queue spacing: no change. ep120 isn't in queue.txt yet. Its opening is `must`, so the upload must not sit next to another `must`.
