# ep132-bus-stop handoff (batch 14)

Branch `claude/batch14-ep132-bus-stop`.

- Built, framing pre-check (once) fixed, preflight 0 blocks, framing.py 0, frames.py 0.
- Build review round 1: standards approve (r2-standards), critic revise with 4 must-fixes (r2-critic). Fixed in 83cca426.
- Build review round 2: critic approve (r3-critic, average 7.1, none under 5). Its one should-fix (S18 window cut my face) applied in c79df28f.
- Preview: changes 17.0 / 21.9 (q) per 10 s, motion 7.24, longest still 0.27 s (q edge 0.27), flash --like-proof pass, -14.1 LUFS, -1.8 dBTP.
- `hold` removed; check clean, gate OPEN, shardcheck exit 0, pytest 255 passed.
- PR #362. Proof run 42266625052 drew sha 75e5643 and passed; proof qa passed (qa/ep132-bus-stop.json). Notes only: driver head near the right edge 15.8-18 s, bus nose reads boxy 20.5-21.3 s.
- Next: merge when `test` is green.
