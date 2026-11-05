# Second team: status

Status only, one line per item. The second orchestrator keeps it. Messages between the orchestrators go in issue
#177 ("Orchestrator channel"). Times are US Central.

**Last updated:** Wed 2026-11-04, 8:45 AM Central. The second team owns most story work and every final qa except
closing-time and mirror-maze (owner-approved). Its own usage limit resets Thursdays 8:00 AM Central. Every session
was told at about 4:20 PM Tuesday to merge the latest main before it judges anything (owner and #1).

| Item | Status | Ready for queue | PR | Next |
|---|---|---|---|---|
| ready for queue (second team) | merged, proof qa passed, final qa passed: ep42, ep48, ep54, ep55, ep62, ep89, ep92, ep96, ep98, warm-shoes | **yes** | per story | #1 queues them |
| ready for queue (#1's) | ep47 and ep28 | **yes** | #230 (ep47) | #1 queues them |
| uploaded | mirror-maze, closing-time, rule-three, floor-thirteen | n/a | per story | none |
| dropped 9:12 AM Wed: moving-day | the last-chance fix passed pace on the preview, but critic r12 still said revise on S36b | no | none | held on main; #1 removes it from queue.txt |
| ready for queue: ep99-statue-years | final qa passed (#271) | yes | #259 | #1 queues it |
| last-chance round: ep83-free-fries | critic r3 approved; proof queued | no | #265 | proof qa, merge |
| merged 11:20 AM Wed: ep94-today-again | critic r3 approved, proof qa passed; final next | no | #269 | final qa |
| dropped 10:39 AM Wed: ep97-prize-bears | critic r3 and standards approved, but the proof failed flash (7 a second at 45.1 s, the swinging closet bulb) | no | #267 closed | folder deleted |
| batch 10 (ep101 to ep107) | ep102 merged 3:01 PM Wed (#278), final next; ep105 building; ep101, ep103, ep104, ep106, ep107 dropped | no | #264 scripts | final qa (ep102) |
| batch 11 (ep108 to ep114) | 5 builds started 2:18 PM Wed (ep108 to ep111, ep114); ep112 and ep113 after the Thursday reset | no | #272 scripts | reviews, proofs |
| audit and rewrite plan | open | n/a | #258 | review and merge |
| QA desk | working | n/a | per film | checks finals as they land |
| dropped | batch 7: ep81-eleven-steps, ep82-no-door; batch 8: ep85-early-alarm, ep86-aunts-keys, ep88-six-paintings, ep91-ninth-coffee (#225 closed); batch 9: ep93-recipe-card, ep95-corn-maze, ep100-window-bridges | no | none | recorded in stories/ideas.md and each package.json hold |
| dropped (revivals and fix rounds) | ep58-swing-bridge (#244 closed), dryer-nine (#198), ep45-bee-yard (#213), ep49-car-wash, ep50-beach-huts, ep51-fossil-hall (#199), ep52-ferry-crossing (#223), ep53-car-boot, every-lock; revivals of ep26-last-skate, ep32-sitter, ep43-reading-room, ep46-choir-hall | no | none | recorded in stories/ideas.md and each package.json hold |
| dropped earlier | ep41 (5 rounds), ep71 and ep84 (round 2), ep80, ep87, ep90, the ep34 revival (creature test x3), night-mower | no | none | recorded on main and in HANDOFF.md |
| creature lab and round 2 | done: nothing passed; no CC0 meshes (owner: "Do whatever you think is best"); the playbook is in writer.md and builder.md | n/a | #220, #224, #221 | ep87 and ep71 stay dropped |
| pace near-miss band (owner) | merged | n/a | #201 | none |
| render: lanes (32 shards) and no-waste | merged; run 106 drew 64 shards at once in about 45 min | n/a | #202, #203 | after #222, a run that reuses run 106's shards |
| frame check counts drawings, not frames | merged 7:37 PM (it threw away moving-day three times) | n/a | #222 | the next run assembles moving-day from reused shards |
| engine A/B (samples 10 to 6, twos) | merged; #1 shipped 6 samples | n/a | #214, #216, #217 | twos wait for a watched 6-sample film |
| finish speedup (change 7) | already in the engine (4 workers since #94) | n/a | #218 | study row corrected |
| research: brief, premise engines, triage, throughput | merged | n/a | #182, #195, #196, #197 | none |

"Ready for queue: yes" means the story merged with a passed proof qa and its final passed qa, so the first
orchestrator can queue it.
