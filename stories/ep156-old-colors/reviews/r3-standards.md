# ep156-old-colors: standards, round 3 (rescue check, 2026-11-13)

This round checks only the open round-2 must-fix (the "It's YOU" caption). It uses the timeline from 07:00 UTC, the preview mp4 (1349 frames, 44.97 s) and preflight.

## Round-2 must-fix
3. **"It's YOU" caption:** in. A 5-word chunk can't be made (split_chunk re-splits anything over 3 words), so the builder re-voiced L17 as "Leo. It's you who... misses it." with a pause. The caption "Leo. It's YOU who" is now up from 42.047 to 42.726 s, which is **0.68 s**, up from 0.29 s. The pink YOU holds through the pause, and "misses it." follows at 42.736 to 43.48 s. Checked at 300 px at 42.5 s and 42.9 s: S17b shows the blue face and hands with the calendar on "41", and the caption is readable.

## Remit check
- **Spoken words:** the same as before. Only an ellipsis was added, and L17 now runs 1.67 s instead of 1.55 s. No other line changed in voice-timings.json.
- **Package:** package.json hasn't changed since round 2.
- **Flash:** preflight passes with 0 blocks. The flash like-proof is PASS on 1349 frames (general 0, general_3f 1, red 0, no very different bright cuts).
- **Regressions:** none in my remit.

Verdict: approve
