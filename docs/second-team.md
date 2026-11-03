# Second team: status

Status only, one line per item. The second orchestrator keeps it. Messages between the orchestrators go in issue
#177 ("Orchestrator channel"). Times are US Central.

**Last updated:** Tue 2026-11-03, 11:05 AM Central. Since 11:00 AM the second team also owns most of the first
orchestrator's story work and final qa (the owner approved it; #1 is near its usage limit). Up to 6 sessions at once.

| Item | Status | Ready for queue | PR | Next |
|---|---|---|---|---|
| final-film qa desk (all films except closing-time, mirror-maze) | working | n/a | per film | ep47, ep54, moving-day, rule-three, dryer-nine, warm-shoes as their films land |
| ep55-caravan-park (must) | proof qa (QA desk) | no | #174 | proof qa, then merge, then final |
| ep42-barber-chair (count) | proof qa (QA desk) | no | #172 | proof qa, then merge, then final |
| floor-thirteen (if) | working | no | none yet | L36 rescue fix, one critic look, proof |
| dryer-nine (cost) | working | no | none yet | flash fix, proof (a second flash fail drops it) |
| warm-shoes (confess) | working | no | none yet | boot clip fix, proof (a second qa fail drops it) |
| rule-three (cost) | waiting for its film | no | none | final qa on a film from run #89 or later (not run 87, the old cut) |
| ep50-beach-huts (if) | working | no | none yet | r4 fixes, then review r5 (r6 is the last) |
| ep52-ferry-crossing (if) | working | no | none yet | new-opening preview, then review r4 (r5 is the last) |
| ep51-fossil-hall (confess) | next | no | none yet | rescue fix at 0 to 5 s, one critic look |
| ep48-crazy-golf (confess) | next | no | #173 | r6 critic fixes on the opening, one more look |
| every-lock (count) | next | no | none yet | clean preview, flash, reviews r1 and r2 |
| ep71-two-windows (count) | next | no | none yet | round-1 fixes (creature first), review r2 is the last |
| ep49-car-wash (must) | next | no | none yet | review r8 (r9 is the last) |
| ep45-bee-yard (count) | next | no | none yet | review r4 (r5 is the last) |
| ep53-car-boot (cost) | next | no | none yet | review r5 (r6 is the last) |
| ep41-orchard-rows | dropped 2026-11-03 | no | none | 5 rounds, r5 hook 4 and creature 4; the build stays on `claude/ep41-orchard-rows-opening` |
| render.yml: assemble waits only for its own shards | PR open, `test` green | n/a | #178 | the first orchestrator merges it between render runs |
| research brief `docs/research/2026-11-09-week.md` | starts Thu Nov 5 | n/a | none yet | pitches only, no stories before the Monday reset |

"Ready for queue: yes" means the story merged with a passed proof qa and its final passed qa, so the first
orchestrator can queue it. ep41's hold on main still says "awaiting the opening fix". It is dropped all the same
(see `stories/ideas.md`).
