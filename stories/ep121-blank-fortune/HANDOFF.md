# ep121-blank-fortune: HANDOFF (dropped, 2026-11-05)

STATUS: dropped. The proof qa failed after the round cap (two rounds plus the one rescue) was spent, so there is no round left to fix it.

## Verdicts
- Critic: r1 revise, r2 revise (one fix), r3 approve after the rescue (average about 7.3).
- Standards: r1 revise, r2 approve.
- Gate OPEN, `check` clean, 202 tests pass.
- Proof run 41989825036 (sha 0edb268e, artifact 13398409713) passed its own verdict: 0 craft blocks, flash pass, 0 clip hits, -14.1 LUFS, -1.8 dBTP.
- Proof qa (qa/ep121-blank-fortune.json): FAIL.

## Open must-fixes from the proof qa
1. 0.00 s, S01: the narrator is missing on frame 0 and pops in on the next frame.
2. 63.83 to 64.6 s, S64: the video-call phone left over from S62 cuts through the left side of the narrator's face.
3. 44.6 to 46.07 s (S48) and 60.17 to 61.83 s (S59): the caption sits on Grandpa's mustache and mouth.
4. Noted, not a fail: 65.4 to 67.4 s (S65) both heads are cropped at the frame edges and the narrator's arm reaches into Grandpa's side.
Warnings only: cuts per 10 s 9.41 (target 5.5 to 8.0), voice-bed gap 7.5 dB (target 8 to 14).

## Notes for whoever picks it up
- The fixes are small and concrete (S01 pop-in, S64 leftover phone, caption placement, S65 framing). If the owner or the first orchestrator allows a new round, a fresh builder can do them in one pass.
- Delete out/work/<story>/frames-preview before any re-render: stale frames got mixed in and caused a false 7 Hz flicker earlier.
- PR #300 is open and not merged. `test` blocks the merge without a passed proof qa, so it is safe to leave.
