# ep49-car-wash: standards review, round 4 (flash and package recheck)

Verdict: approve

Checked the re-rendered preview (138.93 s, flash.json 15:09 after commit 6623072), preflight (flash PASS, 0 blocks) and the gate (package lints clean; the only block was the r3 verdict).

Round 3 items:
1. Flash at 94.0 to 95.5 s: fixed. Over the whole film the 3-frame worst is now 2 flashes/s at 33.2 s and 5 changes/s at 120.4 s, both under the 3/6 bar. Nothing near 94 s is a peak any more. The longest 2/s run is 1.87 s from 87.57 s, and the extended run is 0.9 s from 83.47 s, both well under 4 s. Red is 0 throughout. Frames at 93.6 to 95.9 s show S64 holding on the close bodies before the orange glow, with no hard bright and dark alternation.
2. Package: `"shape": "stand-in"` is the pending RULES.md key, so leave it. cover_s 98.6 lands on the Stutter's face, lit from below and filling the frame, with the caption "SLOWLY,". It still works as the thumbnail.

## Must-fix

None.

## Nice-to-have (carried)

- 120.4 s (5 changes/s) is the new 3-frame peak. Don't tighten cuts there.
- 2 captions show for under 0.2 s ("it out", "come OUT").
