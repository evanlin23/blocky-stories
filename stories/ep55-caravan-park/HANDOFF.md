# HANDOFF: ep55-caravan-park opening fix (2026-11-03)

PR: #174. Branch: claude/opening-ep55-caravan-park. Only the opening changed (line 1, new L01b where noted, first shot).
Shape: must. L01 'You can't wait for someone at the front gate.' (was 'Never wait...'); the close-up first shot and GATE sound hit were already there.

Where I stopped: voice is redone and committed (voice-timings.json). Local tooling: `bash blocky/setup.sh` then export BLOCKY_BPY and BLOCKY_TTS as it prints.
Critic opening check done: reviews/r9-critic.md approve (advice: tighten frame 1 on the chair). Hold removed. Gate OPEN. main merged in. proof.yml started on its own for this PR; I did not see it finish and did not run qa at stage proof.
Not done by me: merge (needs proof qa pass at stage proof and a green `test`). Don't dispatch render.yml or upload.yml; don't edit queue.txt.
