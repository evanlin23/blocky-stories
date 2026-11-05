# ep101-well-wish retry: dropped

Retry (the only one, audit decision 7). Proof run 41982799996 on PR #295 (sha 60b2531) failed on flash.

- `blocky flash` on the proof: FAIL, `general_3f_extended_under_4s` (warnings: 5 flashes/s, 11 changes/s). Local preview flash had passed at 4/s; the 270x480 proof measured higher. Suspects from standards: the gold ripple ring glows in S29 (~22.3 s) and S67.
- Craft blocks all ok; cuts_per_10s 12.7 and walk_dead_end 0.30 are warns only.
- Fixed this retry: Wes's grin is now delighted/warm (critic confirmed warm at L08, L12, L21, L24, L40), opening face by 0.5 s, 7 framing findings, S35 car lighting, S87 caption, S69/S54, S36 car at curb.
- Reviews: critic r1 revise (7.5), r2 revise then rescue approve (7.4); standards r1 approve. Review caps are spent (2 rounds + 1 rescue), so no further fix round; proof qa was not run.
- To revive (owner decision): soften the S29/S67 ring glow flashes, redraw, re-run proof. Everything else is ready.
