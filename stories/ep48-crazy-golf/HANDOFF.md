# HANDOFF: ep48-crazy-golf opening fix (2026-11-03)

PR: #173. Branch: claude/opening-ep48-crazy-golf. Only the opening changed (line 1, new L01b where noted, first shot).
Shape: confess. L01 'My shadow has never left my feet.', new L01b 'Everyone else's goes where they're happiest.', first shot a low feet close-up.

Where I stopped: voice is redone and committed (voice-timings.json). Local tooling: `bash blocky/setup.sh` then export BLOCKY_BPY and BLOCKY_TTS as it prints.
Critic opening check done: reviews/r6-critic.md says REVISE, so the hold is still on and main is not merged in. Must-fixes: (1) my shadow dark, hard-edged and joined to my shoes in frame 1; (2) hold the feet close-up for all of L01, cut at L01b to a stranger's shoes with no shadow and their shadow on the grass 2 m away; (3) no wide, tree or horizon shots or cropped purple figure in 0-3 s; (4) brighten the pavement shot to match the lawn; (5) rewrite the L01/L01b shots in script.md (it still lists the old 5 m mid shot). A proof also started on this PR by itself; ignore it until fixed.
Not done by me: merge (needs proof qa pass at stage proof and a green `test`). Don't dispatch render.yml or upload.yml; don't edit queue.txt.

## Update (second session, 2026-11-03)
Done: main merged. r6 must-fixes applied in story.json/set.py/script.md: my shadow is a hard, dark ("hard" variant of flat_fig) shadow joined to the shoes; S001 is a side-on feet close-up held for all L01; S002 cuts at L01b to a stranger (c1) with no shadow and a lone shadow on the grass (fig_l2); me hidden at L01b; pavement shot S003 left as is (check). look.polish turned on (it was off, which gave 61 pace blocks); S091 head-through-arm clip fixed (wrung y 20.5, me y 18.9). preflight: 0 blocks except the review warn; measure: 0 block (2 warn: face_big 0.379, sound events 4.5/10s). clipcheck 0.
Not done yet: preview + flash, r7 critic, standards, proof, qa, merge. Content note: the story ends on a sad family (dad) reveal; the queue should space those out.
r7 critic: approve. r6 standards: approve. Hold removed. check clean, gate OPEN, pytest 171 passed, flash PASS (3-flash reading at 36.17 s is at the limit, S025-S027; the proof decides). Next: proof on PR #173, qa stage proof, merge.
Proof run 29 (sha 49c75ad) failed on 3 craft blocks only (flash, clip, loudness all passed): picture_changes_per_10s 12.0 (12.5), _q 13.7 (14.0), motion_energy_q 5.78 (6.0). One fix: look.polish {"punch":0.07,"punch_rate":1.3,"fill":1.2} (punch_per_10s 0.7 to 2.39). Re-proof is the one allowed re-run; a second fail means drop.

## STATUS dropped (2026-11-03, second proof fail)
Reviews: critic r7 approve (hook 8/10, no must-fixes), standards r6 approve. check clean, gate OPEN, pytest 171 passed, flash PASS, clipcheck 0, loudness -14.1 LUFS / -1.7 dBTP.
Proof run 29 (sha 49c75ad) and proof run 32 (sha 98adf33, after one fix) both failed on the same 3 craft blocks, and nothing else:
- run 29: picture_changes_per_10s 12.0 (min 12.5), _q 13.7 (min 14.0), motion_energy_q 5.78 (min 6.0)
- run 32: picture_changes_per_10s 12.0, _q 13.8, motion_energy_q 5.8
The one fix (look.polish punch 0.07, punch_rate 1.3, fill 1.2; punch-ins 0.7 to 2.39 per 10 s) moved the numbers by 0.1 at most: punch-ins don't count as picture changes. The film is already at 7.25 cuts per 10 s, near the 8.0 cap, so the shortfall is in how much each shot changes, not in how many cuts. A real fix is a rework across the film (more camera moves and acting in the 104 one-camera-key shots), not one shot or one cue.
Dropped per the brief (second fail). Not merged, no qa file written, hold was removed from package.json on this branch (re-add it if the branch is ever reused). Note for the queue: this story ends on a sad family (dad) reveal.
