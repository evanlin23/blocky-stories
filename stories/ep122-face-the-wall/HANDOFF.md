# ep122-face-the-wall: handoff (build session, batch 13)

STATUS: working (fix round 1). Branch `claude/batch13-ep122-face-the-wall`.

- Done: story files, set, voice (phase 1, preflight 0 blocks, framing.py 0 findings); framing pre-check (12 fixes listed).
- In progress: phase 2, applying the framing fixes, preview, frames lint, `flash --like-proof`, measure. A container restart killed the first phase 2 builder; a fresh one resumed it.
- Next: critic + standards round 1, then the PR and proof.
- Build round 1 (r2-critic, r2-standards): both revise. Critic 11 must-fixes (S49 blank, tag/caption over faces, Dad missing at reveal S55/S56, scare room too bright, S60 too short, tag glyphs, S48 pat, length 113 s -> re-voice at rate 1.32 for >=120 s, cover_s). Standards 3 (S49, S39 washed out, S78 floating slab). Fix round 1 running; cover_s goes to the writer once the re-voiced S24 time is known. Round 2 re-runs both (both said revise).
