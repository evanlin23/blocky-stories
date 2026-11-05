# Second team: status

Status only, one line per item. The second orchestrator keeps it. Messages between the orchestrators go in issue
#177 ("Orchestrator channel"). Times are US Central.

**Last updated:** Thu 2026-11-05, 2:50 PM Central. The second team is build capacity (RULES, audit decision 1): the
first orchestrator alone owns queue.txt, uploads and dispatching renders. Its usage limit resets Thursdays 8:00 AM
Central.

| Item | Status | Ready for queue | PR | Next |
|---|---|---|---|---|
| ready for queue (second team) | merged, proof qa passed, final qa passed: ep42, ep48, ep54, ep55, ep83, ep89, ep92, ep94, ep96, ep98, ep99, ep102, ep108, ep110, ep114, warm-shoes | **yes** | per story | #1 queues them |
| ready for queue (#1's) | ep28 | **yes** | per story | #1 queues it |
| uploaded | mirror-maze, closing-time, rule-three, floor-thirteen, ep47 (Thu), ep62 (Thu) | n/a | per story | none |
| retries (decision 7, one each) | running: moving-day, ep118 (since 10:23 AM Thu); ep116, ep117, ep120 (since 2:24 PM Thu) | no | per story | fresh reviews, proof, proof qa |
| batch 12 (ep115 to ep121) | ep119 building (fix round 1); ep115, ep121 dropped; ep116, ep117, ep118, ep120 on retry | no | #288 scripts | ep119 critic r2 |
| batch 13 (ep122 to ep128) | scripts merged 2:37 PM Thu; 7 builds started 2:44 PM Thu | no | #316 scripts | builds |
| batch 11 (ep108 to ep114) | ep108 (retry), ep110, ep114 merged; ep109, ep111, ep112, ep113 dropped | n/a | #272 scripts | none |
| batch 10 (ep101 to ep107) | ep102 merged; the rest dropped (ep101 and ep107 retries failed flash) | n/a | #264 scripts | none |
| process fixes (Thu) | merged: lints #307, review convergence #314 (RULES decision 8), flash `--like-proof` #310, engine #308 frame-0 pose, #309 captions | n/a | per PR | none |
| engine fixes for #1 | #311 light cues at cuts, #313 camera-in-set report, #312 rule tag: main being merged in (#1's 2:45 PM ask) | n/a | #311, #312, #313 | #1 merges on green |
| QA desk | working; watching the first finals after each engine merge | n/a | per film | checks finals as they land |
| dropped | every drop has a killed line in stories/ideas.md, and its folder is deleted on main (audit decision 6) | no | none | none |

"Ready for queue: yes" means the story merged with a passed proof qa and its final passed qa, so the first
orchestrator can queue it.
