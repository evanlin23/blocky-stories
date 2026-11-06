# Second team: status

Status only, one line per item. The second orchestrator keeps it. Messages between the orchestrators go in issue
#177 ("Orchestrator channel"). Times are US Central.

**Last updated:** Fri 2026-11-06, 9:25 AM Central. The second team is build capacity (RULES, audit decision 1): the
first orchestrator alone owns queue.txt, uploads and dispatching renders. Its usage limit resets Thursdays 8:00 AM
Central.

| Item | Status | Ready for queue | PR | Next |
|---|---|---|---|---|
| ready for queue (second team) | 27 posted on #177 (merged, proof qa, final qa); uploaded Fri: ep55, ep92 | **yes** | per story | #1 queues them |
| ready for queue (#1's) | ep28 | **yes** | per story | #1 queues it |
| uploaded | mirror-maze, closing-time, rule-three, floor-thirteen, ep47 (Thu), ep62 (Thu) | n/a | per story | none |
| retries (decision 7, one each) | done: moving-day, ep116, ep117, ep120 merged and ready; ep118 dropped | n/a | per story | none |
| batch 12 (ep115 to ep121) | ep119 merged; ep116, ep117, ep120 merged on retry; ep115, ep118, ep121 dropped | n/a | #288 scripts | none |
| batch 13 (ep122 to ep128) | all 7 merged. Ready: ep123, ep124, ep126, ep127, ep128. ep122 held for a fix (S56 lurch, S71 tag); ep125's final redraws (lost shard) | no | #316 scripts | finals, ep122 fix |
| batch 14 (ep129 to ep135) | 6 scripts merged (#356); 6 builds started 8:33 AM Fri | no | #356 scripts | builds |
| held for a fix | warm-shoes (rule meter blurred by depth of field), ep102 (frame 0 lacks Clem: redraw after #351) | no | per story | fixes, then final qa |
| batch 11 (ep108 to ep114) | ep108 (retry), ep110, ep114 merged; ep109, ep111, ep112, ep113 dropped | n/a | #272 scripts | none |
| batch 10 (ep101 to ep107) | ep102 merged; the rest dropped (ep101 and ep107 retries failed flash) | n/a | #264 scripts | none |
| process fixes (Thu) | merged: lints #307, review convergence #314 (RULES decision 8), flash `--like-proof` #310, engine #308 frame-0 pose, #309 captions | n/a | per PR | none |
| engine and workflow fixes for #1 | merged: #308, #309, #310, #311, #312, #318, #325, #335 (apt retry), #351 (shard starts and frame 0); open: #313 | n/a | #313 | #1 merges; redraw ep102 after #351 |
| proof once per sha (migration step 1) | merged 8:42 PM: three-dot diffs, dispatch checks, live-run dedup, "waiting for proof" in `test` | n/a | #318 | none |
| QA desk | working; watching the first finals after each engine merge | n/a | per film | checks finals as they land |
| dropped | every drop has a killed line in stories/ideas.md, and its folder is deleted on main (audit decision 6) | no | none | none |

"Ready for queue: yes" means the story merged with a passed proof qa and its final passed qa, so the first
orchestrator can queue it.
