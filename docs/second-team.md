# Second team: status

Status only, one line per item. The second orchestrator keeps it. Messages between the orchestrators go in issue
#177 ("Orchestrator channel"). Times are US Central.

**Last updated:** Tue 2026-11-03, 10:45 AM Central.

| Item | Status | Ready for queue | PR | Next |
|---|---|---|---|---|
| ep50-beach-huts (if) | working | no | none yet | finish the r4 fixes, then review r5 (r6 is the last) |
| ep52-ferry-crossing (if) | working | no | none yet | preview the new opening, then review r4 (r5 is the last) |
| ep49-car-wash (must) | not started | no | none yet | starts when a slot frees, then review r8 (r9 is the last) |
| ep45-bee-yard (count) | not started | no | none yet | starts after ep49, then review r4 (r5 is the last) |
| ep53-car-boot (cost) | not started | no | none yet | starts after ep45, then review r5 (r6 is the last) |
| ep41-orchard-rows | dropped 2026-11-03 | no | none | none (5 rounds, r5 hook 4 and creature 4; the build stays on `claude/ep41-orchard-rows-opening`) |
| render.yml: assemble waits only for its own shards | working | n/a | none yet | the first orchestrator merges it between render runs |
| research brief `docs/research/2026-11-09-week.md` | starts Thu Nov 5 | n/a | none yet | pitches only, no stories before the Monday reset |

"Ready for queue: yes" means the story's PR merged with a passed proof qa, and the first orchestrator can queue it.
ep41's hold on main still says "awaiting the opening fix". It is dropped all the same (see `stories/ideas.md`).
