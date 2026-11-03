# HANDOFF: ep42-barber-chair opening fix (2026-11-03)

PR: #172. Branch: claude/opening-ep42-barber-chair. Only the opening changed (line 1, new L01b where noted, first shot).
Shape: count. L01 'Sixty-four people on this street. Sixty-three are humming.', L01b states the rule, first shot a close-up on me and my ring.

Where I stopped: voice is redone and committed (voice-timings.json). Local tooling: `bash blocky/setup.sh` then export BLOCKY_BPY and BLOCKY_TTS as it prints.
Critic opening check done: reviews/r4-critic.md approve (advice only: vary 1.5/3.0/4.5 s framing, tint my silent ring dim). Hold removed. Gate OPEN. main merged in. proof.yml started on its own for this PR; I did not see it finish and did not run qa at stage proof.
Not done by me: merge (needs proof qa pass at stage proof and a green `test`). Don't dispatch render.yml or upload.yml; don't edit queue.txt.

## 2026-11-03 later: proof fixed
Polish pack on, S01 t=0 offstage key dropped (head clips), c4/c5 off the lamp post. Proof run 41695750035 (sha cf0004c) passed automatic checks; qa at stage proof passed (Opus). Optional qa notes: cover_s 1.6 shows back of head; S70 head flat; S61 empty counter 1.2 s. Local preflight asr block is Whisper noise on the unchanged voice; the proof and gate are fine.
