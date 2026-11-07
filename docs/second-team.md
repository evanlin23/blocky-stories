# Second team: status

Status only, one line per item. The second orchestrator keeps it. Messages between the orchestrators go in issue
#177 ("Orchestrator channel"). Times are US Central.

**Last updated:** Fri 2026-11-06, 7:25 PM Central. The second team is build capacity (RULES, audit decision 1): the
first orchestrator alone owns queue.txt, uploads and dispatching renders. Its usage limit resets Thursdays 8:00 AM
Central.

| Item | Status | Ready for queue | PR | Next |
|---|---|---|---|---|
| clean and ready (final qa plus a staging look) | ep54, ep42, ep48, ep117, ep128, ep123, ep116, ep122, ep114, ep132, warm-shoes (11) | **yes** | per story | #1 queues them |
| staging fixes merged, finals pending qa | ep102 (failed final qa on S69 camera inside grass: fix 2 running), ep108 #375, ep110 #381, ep124 #371, moving-day #385, ep83 #387, ep119 #388 | no | per story | final qa |
| staging fixes in progress | worker A: ep96 #395, ep98, ep89, ep126; worker B: ep94, ep99 #392, ep127; worker D: ep130 | no | per story | proof, merge, final qa |
| held for good | ep120: its staging fix needed a second pass after the one rescue (#383 closed), and the old final keeps visible merges. Not uploading | no | none | none |
| held, #1's | ep28: visible pop and merge at S68; we asked #1 whether to fix it | ask | none | #1 decides |
| uploaded with staging flaws | ep55 and ep92 (Fri): drop-in fixes #384 and #377 made; a re-upload is the owner's call and #1's dispatch. Public, not fixing: ep47, ep62, closing-time, rule-three, floor-thirteen, mirror-maze | n/a | #377, #384 | owner decides |
| ep125 | fixes confirmed; the final has 2 black-face frames from a render race (fix #380, for #1). Redraw after #380 | no | #380 | #1 merges, redraws |
| batch 15a (interactive pilots, owner 2026-11-06) | scripts #389; building ep136-one-answer, ep137-trail-board, ep138-tomorrow-mirror | no | #389 | builds |
| batch 14 (ep129 to ep135) | ep132 ready; ep130 merged (#378), staging fix running; ep134 #391 and ep135 #390 in proof (ep135 on its decision-7 retry); ep129 building; ep133 dropped | no | #356 | builds |
| engine PRs for #1 | #380 (face-PNG race, urgent), #373 (draw_meter only for me/ines cues), #313 (camera inside the set) | n/a | per PR | #1 merges |
| lints (report-only, scripts/) | framing, frames (#307), measure (#332), shardcheck (#345), staging (#366) | n/a | per PR | every build and fix runs all five |
| QA desk | each new final gets qa, staging.py plus a look, and a black-frame scan | n/a | per film | checks finals as they land |
| dropped | every drop has a killed line in stories/ideas.md, and its folder is deleted on main (audit decision 6) | no | none | none |

"Ready for queue: yes" means the story merged with a passed proof qa and its final passed qa, plus a staging look
(lesson 46) since Fri Nov 6, so the first orchestrator can queue it.
