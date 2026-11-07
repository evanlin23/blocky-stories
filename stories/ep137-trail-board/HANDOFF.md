# ep137-trail-board: handoff

- **State:** both build reviews approve (round 2: critic r3 7.1 average, nothing under 5; standards r3 approve). `hold` removed, check clean, gate OPEN, staging 0, shardcheck 0, pytest green.
- **Next:** PR open, waiting on proof.yml, then proof qa, then merge on green `test`.
- **Clues (critic r3):** C1 to C5 all read at phone size; 2 clues per side, C5 both ways.
- **Should-fix, not done:** S17 June's hands and boots sit below frame (critic r3).
- **Engine note:** `render --preview --force` leaves stale frames in `frames-preview`; delete it and `frames-flash` before a re-render after a re-cut.
