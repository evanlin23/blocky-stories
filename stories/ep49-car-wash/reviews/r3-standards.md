# ep49-car-wash: standards review, round 3

Verdict: revise

Checked the re-rendered preview (flash.json 13:58), preflight (flash PASS, 0 blocks), package.json and commit bcfd199.

Round 2 item:
- 53.0 to 55.1 s: fixed. P01 is gone, S38 (conveyor, phone and keys) runs 1.5 s from 53.57, and that window is off the peak. Mist to conveyor reads as one bright space, not a flash.

What the fixes broke:
- cover_s 98.6: fine. It lands in S68 (97.63 to 99.8): the Stutter's face, lit from below, fills the frame, caption "until its face".

## Must-fix

1. **Flash, 94.0 to 95.5 s (S63 to S66, L48/P02/L49/L49.2).** The 3-frame peak has moved here and it's exactly on the bar again: 3 flashes and 6 changes a second at 94.57 s. The dark blue S63 cuts to the bright, close bodies of S64 (P02 "hold", 0.6 s), then S65 at 94.6 s with the orange glow, then S66 at 95.47 s. Hold S64 for at least 1.0 s, or drop P02 and start S65 (L49) at 94.0. Re-run preflight and confirm general_3f is under 3/6 everywhere.
2. **package.json: `"shape": "stand-in"`.** That key isn't in RULES.md → Packaging, nothing reads it, and "stand-in" reads like a leftover placeholder. Delete the key. Keep `cover_s` at 98.6.

## Nice-to-have (carried)

- S73 "brass CLAPPER," is still under 0.5 s between bright and dark shots.
- 2 captions show for under 0.2 s ("it out", "come OUT").
