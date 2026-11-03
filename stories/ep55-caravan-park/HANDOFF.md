# HANDOFF: ep55-caravan-park opening fix (2026-11-03)

PR: #174. Branch: claude/opening-ep55-caravan-park. Only the opening changed (line 1, new L01b where noted, first shot).
Shape: must. L01 'You can't wait for someone at the front gate.' (was 'Never wait...'); the close-up first shot and GATE sound hit were already there.

Where I stopped: voice is redone and committed (voice-timings.json). Local tooling: `bash blocky/setup.sh` then export BLOCKY_BPY and BLOCKY_TTS as it prints.
Critic opening check done: reviews/r9-critic.md approve (advice: tighten frame 1 on the chair). Hold removed. Gate OPEN. main merged in. proof.yml started on its own for this PR; I did not see it finish and did not run qa at stage proof.
Not done by me: merge (needs proof qa pass at stage proof and a green `test`). Don't dispatch render.yml or upload.yml; don't edit queue.txt.

## Proof-fix round (2026-11-03)
Proof failed 4 craft blocks (picture changes, motion energy, longest still) and head clips. Changes (no words, title, L01 or first shot touched):
- story.json `look.polish: true` (the story had it off: that was the whole pace gap; no hand-keyed pace was possible on 95 shots). rev 4 -> 5. Preview rebuilt with it: longest still 0.57 s (was 1.33), no pace rows, flash PASS (general 2/s, 3f 3/s; 0 red), mix -14.1 LUFS / -1.8 dBTP, measure 0 block.
- S90: Jory walked at x=0.7 through gatepost 1 (post spans 0.56-0.94); walk now x=0.3.
- `clip_ok` (by design): S75/S76/S77 jory (moss pads on Jory), S81 flake40/flake46 (the moss shower), S01/me+jory, S05/S06 train, S07 flakes, S23 me (the clipcheck hits at t=0 on S01 involve hidden cast; train door exit; sleeve brush). Not visible in stills at those seconds.
- Preflight now 0 blocks except `asr`: local Whisper hears L15 "Then she waits" as "When" and L33 "Her chair" as "The chair" on the preview mix. Words unchanged; the earlier proof passed asr. pytest is not installed in this sandbox, so `pytest -q` was not run.
