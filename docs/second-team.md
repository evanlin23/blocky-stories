# Second team: status

Status only, one line per item. The second orchestrator keeps it. Messages between the orchestrators go in issue
#177 ("Orchestrator channel"). Times are US Central.

**Last updated:** Fri 2026-11-06, 2:55 PM Central. The second team is build capacity (RULES, audit decision 1): the
first orchestrator alone owns queue.txt, uploads and dispatching renders. Its usage limit resets Thursdays 8:00 AM
Central.

| Item | Status | Ready for queue | PR | Next |
|---|---|---|---|---|
| staging hold (lesson 46) | the QA desk ran `scripts/staging.py` (#366) on the real finals and looked at each flagged frame: visible lurches or merged bodies in ep42, ep96, ep98, ep89, ep83, ep94, ep99, ep126, ep127 (and #1's ep28). Hold posted on #177 at 2:50 PM | **no** until re-posted | per story | fixes, then final qa plus staging |
| staging fixes | ep42 (S63→S64 pop); worker A: ep96, ep98, ep89, ep126; worker B: ep83, ep94, ep99, ep127 | no | per story | proof, merge, final qa |
| triaged clean | ep54, ep48, ep117 | **yes** | per story | #1 queues them |
| triage group 3 | ep124, ep128, ep123, ep116, ep119, ep120, ep122, ep110, ep108, ep114, moving-day | yes (passed final qa); being re-checked for staging | per story | clean ones posted as substitutes |
| ready for queue (#1's) | ep28: visible pop and merge at S68; we asked #1 whether to fix it | ask | none | #1 decides |
| uploaded | mirror-maze, closing-time, rule-three, floor-thirteen, ep47, ep62, ep55, ep92 | n/a | per story | none |
| batch 14 (ep129 to ep135) | ep132 merged, its final failed (arms intersect), fix #367; ep133 dropped (creature); ep129, ep130, ep134, ep135 building, now running staging.py | no | #356 scripts | builds, ep132 fix |
| batch 13 (ep122 to ep128) | all 7 merged. ep122 ready after #358; ep125's fix #364 merged, final drawing; ep126 and ep127 held for staging | mixed | #316 scripts | finals, staging fixes |
| held for a fix | warm-shoes (#360 merged, final drawing); ep102 (frame 0 lacks Clem: redraw after #351, #1's dispatch) | no | per story | final qa |
| retries (decision 7, one each) | done: moving-day, ep116, ep117, ep120 merged and ready; ep118 dropped | n/a | per story | none |
| batches 10 to 12 | ep102, ep108, ep110, ep114, ep116, ep117, ep119, ep120 merged; the rest dropped | n/a | #264, #272, #288 | none |
| lints (report-only, scripts/) | framing #307, frames #307, measure #332, shardcheck #345, staging #366 | n/a | per PR | every build and fix runs all five |
| engine and workflow fixes for #1 | merged: #308 to #312, #318, #325, #335, #351. #313 open, main being merged into it again | n/a | #313 | #1 merges |
| QA desk | working; staging triage, then each new final gets staging.py plus a look at the fixed times | n/a | per film | group 3 triage |
| dropped | every drop has a killed line in stories/ideas.md, and its folder is deleted on main (audit decision 6) | no | none | none |

"Ready for queue: yes" means the story merged with a passed proof qa and its final passed qa, so the first
orchestrator can queue it. From Fri Nov 6 the final also has to pass a staging look (lesson 46).
