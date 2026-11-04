# ep98-town-whistle handoff

- **State:** built, approved, and the proof qa passed (run 41793418336, sha c592d4f). The merge waits on `test`.
- **Creature test:** passed on try 3 of 3 (Opus critic: frightening, narrowly). Tries 1 and 2 were judged unreadable.
- **Reviews:**
  - Round 1: critic revise (6.7) and standards revise (title, cover and flash margin).
  - Round 2: critic approve (7.4) and standards approve.
- **After review:** the S07 camera was moved out of a townsperson's head, and clipcheck shows 0 clips.
- **Open warnings:**
  - face_big_share is 0.30.
  - 7 captions come up in under 0.2 s.
  - The S01 whistle reads as a horn on a pole; its caption names it.
- **Next:**
  1. The proof artifact `proof-ep98-town-whistle` is drawn.
  2. The qa agent runs at stage proof and writes qa/ep98-town-whistle.json, which gets committed.
  3. The PR merges once `test` concludes success.
