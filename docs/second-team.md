# Second team: status

Status only, one line per item. The second orchestrator keeps it. Messages between the orchestrators go in issue
#177 ("Orchestrator channel"). Times are US Central.

**Last updated:** Fri 2026-11-13, 8:30 PM Central. The second team is build capacity (RULES, audit decision 1): the
first orchestrator alone owns queue.txt, uploads, dispatching renders, blocky/ and .github/. The second's usage limit
resets Thursdays 8:00 AM Central. It is at "allowed_warning" until Thu Nov 19, so it's running lean (two check-ins a day,
no new sessions).

| Item | Status | Ready for queue | PR | Next |
|---|---|---|---|---|
| batch 15 ready (14) | ep139, ep140, ep141, ep143, ep144, ep145, ep146, ep147 (v3), ep148 (v3), ep149, ep150, ep152 (v3), ep154, ep155 | **yes** | per story | queued by #1 (#507, #526, #529); ep152 to queue |
| batch 15 in fix | ep156 (final qa failed: the S17b hands vanish at 43.53 s; fix job with one rescue) | no | to come | final qa |
| batch 15 dropped | ep142 (r2, big idea thinned by the cut), ep151 (creature test x3), ep153 (too thin at the first look) | no | #488, this PR | none |
| style v3 | approved by the owner; engine #472 merged; both pilots passed their finals (ep148 warm, ep147 eerie) | n/a | #471, #472 | batch 16 all v3 |
| animation audit | #475-#478 and #499 (talk) merged; 720p (#478) stays off (#1: not worth +200 runner-min) | n/a | #475-#478, #499 | batch 16 turns on overlap, turn_cap, punch_max, sharpen, talk |
| held for good | ep120 (staging after its one rescue); ep28 (#1's call 2026-11-13: drop) | no | none | none |
| uploaded with flaws | ep55 and ep92: drop-in fixes #384 and #377 merged; a re-upload is the owner's call | n/a | #377, #384 | owner decides |
| lints (scripts/) | framing, frames, measure, shardcheck, staging (with yaw, #465; blocks `gate --merge`, decision 11) | n/a | per PR | every build and fix runs all five |
| batch 16 | after the Thu Nov 19 reset: all v3, audit flags and talk, gentler punch-ins, "find the extra one" #2, the fine-print engine, openings other than if and cost | no | to come | writer after the reset |
| dropped | every drop has a killed line in stories/ideas.md, and its folder is deleted on main (audit decision 6) | no | none | none |

"Ready for queue: yes" means the story merged with a passed proof qa and its final passed qa, so the first orchestrator
can queue it.
