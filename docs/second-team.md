# Second team: status

Status only, one line per item. The second orchestrator keeps it. Messages between the orchestrators go in issue
#177 ("Orchestrator channel"). Times are US Central.

**Last updated:** Tue 2026-11-03, 9:25 PM Central. The second team owns most story work and every final qa except
closing-time and mirror-maze (owner-approved). Its own usage limit resets Thursdays 8:00 AM Central. Every session
was told at about 4:20 PM to merge the latest main before it judges anything (owner and #1).

| Item | Status | Ready for queue | PR | Next |
|---|---|---|---|---|
| final-film qa desk | working | n/a | per film | ep42 and ep48 finals as they land |
| ep42-barber-chair (count) | merged, proof qa passed | not yet | #172 | final render, then final qa |
| ep48-crazy-golf (confess) | merged, proof qa passed under the near band (#201) | not yet | #173 | final render, then final qa |
| ep55-caravan-park (must) | merged, proof qa passed, final qa passed | **yes** | #174, #233 | #1 queues it |
| warm-shoes (confess) | merged, proof qa passed | not yet | #205 | final render, then final qa |
| ep62-six-riders (revival) | merged | not yet | #207 | final render, then final qa |
| floor-thirteen (if) | merged, proof qa passed, final qa passed | **yes** | #188, #228 | #1 queues it |
| dryer-nine (cost) | revived for one fix (S54 too dark) | no | #198 | critic look, proof, proof qa; a fail drops it for good |
| ep51-fossil-hall (confess) | revived for one fix (two staging fixes) | no | #199 | critic look, proof, proof qa; a fail drops it for good |
| every-lock (count) | reviews | no | none yet | reviews r1 and r2 |
| ep49-car-wash (must) | last review round | no | none yet | review r9 is the last |
| ep45-bee-yard (count) | both reviews approve | no | #213 | proof qa, merge |
| ep53-car-boot (cost) | revived for one fix (three r6 craft fixes) | no | none yet | critic look, PR, proof qa; a fail drops it for good |
| ep50-beach-huts (if) | r5 fixes | no | none yet | review r6 is the last |
| ep52-ferry-crossing (if) | PR open | no | #223 | proof, proof qa |
| rule-three (cost) | final qa passed (film 13285412545) | yes (in #1's queue) | #227 | upload |
| ep47-fitting-room (#1's queue) | final qa passed (film 13282116306) | yes (in #1's queue) | #230 | Wednesday's second slot |
| moving-day (#1's queue) | final qa FAILED on pace (11.2 against 12.5, 10.9 against 14.0) | no | none yet | one fix session (from 9:19 PM): a proof must clear pace before a new final |
| batch 7 builds: ep81-eleven-steps, ep82-no-door, ep83-free-fries | reviews | no | none yet | reviews, proof |
| batch 8 builds: ep85-early-alarm, ep86-aunts-keys, ep88-six-paintings, ep89-sister-diary, ep91-ninth-coffee | building; ep91 has a PR | no | #225 (ep91) | reviews, proof |
| batch 9 builds: ep92-blackout-ben, ep93-recipe-card, ep94-today-again, ep95-corn-maze, ep96-friend-card, ep97-prize-bears, ep98-town-whistle, ep99-statue-years, ep100-window-bridges | building (from 4:21 PM) | no | none yet | creature still, build, reviews |
| revival: ep58-swing-bridge (craft fixes) | working | no | none yet | 2 review rounds, proof |
| revivals: ep26-last-skate, ep46-choir-hall (new reveals) | working | no | none yet | 2 review rounds, proof |
| revivals: ep32-sitter, night-mower, ep43-reading-room (triage picks) | working | no | none yet | 2 review rounds, proof |
| dropped today | ep41 (5 rounds), ep71 and ep84 (round 2), ep80, ep87, ep90 and the ep34 revival (creature test x3) | no | none | recorded on main and in HANDOFF.md |
| creature lab and round 2 | done: nothing passed; no CC0 meshes (owner: "Do whatever you think is best"); the playbook is in writer.md and builder.md | n/a | #220, #224, #221 | ep87 and ep71 stay dropped |
| pace near-miss band (owner) | merged | n/a | #201 | none |
| render: lanes (32 shards) and no-waste | merged; run 106 drew 64 shards at once in about 45 min | n/a | #202, #203 | after #222, a run that reuses run 106's shards |
| frame check counts drawings, not frames | merged 7:37 PM (it threw away moving-day three times) | n/a | #222 | the next run assembles moving-day from reused shards |
| engine A/B (samples 10 to 6, twos) | merged; #1 shipped 6 samples | n/a | #214, #216, #217 | twos wait for a watched 6-sample film |
| finish speedup (change 7) | already in the engine (4 workers since #94) | n/a | #218 | study row corrected |
| research: brief, premise engines, triage, throughput | merged | n/a | #182, #195, #196, #197 | none |

"Ready for queue: yes" means the story merged with a passed proof qa and its final passed qa, so the first
orchestrator can queue it.
