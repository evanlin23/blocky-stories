# ep125-aunts-keys: build handoff

- Branch: claude/batch13-ep125-aunts-keys
- Script-stage standards review is reviews/script-standards.md; build rounds are r1/r2.
- Round 1: critic revise (hook 8, back-row 7, relationships 8, big idea 7, scare 5, lore 6, variety 6, faces 6; 12 must-fixes), standards revise (6 must-fixes: blank S24/S47/S74, S64 bolt, L27 lock-cut flash, stale package hold).
- Writer reworded L18 ("hand the keys BACK").
- Round-1 fixes: all 12 critic + 5 standards must-fixes in (rev 10, preview 113.8 s). measure with film: changes 13.2/15.0 (bars 12.5/14.0), motion 6.67, longest still 0.53 s, held share 0.147 (bar 0.15).
- Flash --like-proof: general 3/s at 43.4 s = AT the pass cap (<=3), 3f 6/s; the L27 lock run again.
- Now: margin pass (flash + pace) by a fresh builder. Next: merge main, round 2 (both reviewers), check-only.
- Package "hold" is removed at approval (brief step 4).
- Queue note for PR body: at least 7 uploads from ep28-lamp-room; not next to a `confess` opener or a "My ..." title; at least 3 from ep128-zero-feet and ep123-sorry-shrink.
- Margin pass done (rev 12): flash general 1/s (3f 3/s), changes 14.1/15.9, motion 7.03, longest still 0.27 s.
- Round 2: standards APPROVE. Critic REVISE, avg 7.6, none under 5 (scare 6, lore 6, variety 7, faces 7); one must-fix: two-line tag on Lou's hair at S33/S34.
- Now: the ONE rescue (that fix only), then the critic alone looks once. If not approved: drop.
- Rescue: critic r3 APPROVE. Hold removed; check no problems, gate OPEN, pytest 250 passed.
- Now: PR open, waiting on proof.yml (proof-ep125-aunts-keys), then proof qa, then merge on green test.
- PR #346 opened. First proof (run 42199390652) was on rev 13.
- shardcheck (#345) found 6 objects differing at shard starts (S01/S02 extras and Lou's glasses). Fixed in set.py (rev 14), shardcheck 0, gate OPEN, pushed 4cd6bb6f.
- Now: waiting on the proof for 4cd6bb6f, then proof qa (opus), commit qa/ep125-aunts-keys.json, merge on green test.
