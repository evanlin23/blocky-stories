# Second team: status

Status only, one line per item. The second orchestrator keeps it. Messages between the orchestrators go in issue
#177 ("Orchestrator channel"). Times are US Central.

**Last updated:** Thu 2026-11-12, 8:45 AM Central. The second team is build capacity (RULES, audit decision 1): the
first orchestrator alone owns queue.txt, uploads, dispatching renders, blocky/ and .github/. The second's usage limit
resets Thursdays 8:00 AM Central.

| Item | Status | Ready for queue | PR | Next |
|---|---|---|---|---|
| ready, not yet uploaded | 16 in queue.txt (ep94, ep123, ep130, ep99, ep135, ep126, ep127, ep132, ep117, ep83, ep114, ep102, ep119, ep108, ep122, moving-day): about 8 days at 2 a day, to about Fri Nov 20 | **yes** | per story | uploads |
| animation audit | measuring ep124, ep136, ep54; A/B 60 fps, EEVEE, eased acting, turn cap, 3D camera paths, sharpen and crf, fewer punch-ins (ones: all is in, #457) | n/a | to come, for #1 | results table on #177 |
| style v3 sheet | 6 characters x 6 expressions plus a 5 s acting test, for the owner's approval; engine behind `look.style: "v3"` | n/a | to come | #1 takes the sheet to the owner |
| fix worker | yaw check in scripts/staging.py, then ep125 (yaw snaps), ep129 (box through Dad, S49 flat; #414), ep138 (key never shows), ep110 (no ceiling), ep98 (S92 black, S66 white). Each a new fix job with one rescue | no | per story | final qa, then ready |
| batch 15 (ep139 to ep154) | writer started 8:32 AM Thu: 16 scripts to land 14, about half warm (2 in ep124's world), 2 puzzles (one "find the extra one" #2), 2 interactive; bar is #463 | no | to come | builds Fri to Tue, finals by Wed Nov 18 |
| held for good | ep120 (staging fix needed a second pass after the one rescue) | no | none | none |
| held, #1's | ep28 (visible pop and merge at S68) | ask | #419 | #1 decides |
| uploaded with flaws | ep55 and ep92: drop-in fixes #384 and #377 merged; a re-upload is the owner's call | n/a | #377, #384 | owner decides |
| lints (scripts/) | framing, frames, measure, shardcheck, staging (staging blocks `gate --merge`, decision 11) | n/a | per PR | every build and fix runs all five |
| dropped | every drop has a killed line in stories/ideas.md, and its folder is deleted on main (audit decision 6) | no | none | none |

"Ready for queue: yes" means the story merged with a passed proof qa and its final passed qa, plus a staging look
(lesson 46), so the first orchestrator can queue it.
