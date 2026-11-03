# HANDOFF: ep48-crazy-golf opening fix (2026-11-03)

PR: #173. Branch: claude/opening-ep48-crazy-golf. Only the opening changed (line 1, new L01b where noted, first shot).
Shape: confess. L01 'My shadow has never left my feet.', new L01b 'Everyone else's goes where they're happiest.', first shot a low feet close-up.

Where I stopped: voice is redone and committed (voice-timings.json). Local tooling: `bash blocky/setup.sh` then export BLOCKY_BPY and BLOCKY_TTS as it prints.
Critic opening check done: reviews/r6-critic.md says REVISE, so the hold is still on and main is not merged in. Must-fixes: (1) my shadow dark, hard-edged and joined to my shoes in frame 1; (2) hold the feet close-up for all of L01, cut at L01b to a stranger's shoes with no shadow and their shadow on the grass 2 m away; (3) no wide, tree or horizon shots or cropped purple figure in 0-3 s; (4) brighten the pavement shot to match the lawn; (5) rewrite the L01/L01b shots in script.md (it still lists the old 5 m mid shot). A proof also started on this PR by itself; ignore it until fixed.
Not done by me: merge (needs proof qa pass at stage proof and a green `test`). Don't dispatch render.yml or upload.yml; don't edit queue.txt.

## Update (second session, 2026-11-03)
Done: main merged. r6 must-fixes applied in story.json/set.py/script.md: my shadow is a hard, dark ("hard" variant of flat_fig) shadow joined to the shoes; S001 is a side-on feet close-up held for all L01; S002 cuts at L01b to a stranger (c1) with no shadow and a lone shadow on the grass (fig_l2); me hidden at L01b; pavement shot S003 left as is (check). look.polish turned on (it was off, which gave 61 pace blocks); S091 head-through-arm clip fixed (wrung y 20.5, me y 18.9). preflight: 0 blocks except the review warn; measure: 0 block (2 warn: face_big 0.379, sound events 4.5/10s). clipcheck 0.
Not done yet: preview + flash, r7 critic, standards, proof, qa, merge. Content note: the story ends on a sad family (dad) reveal; the queue should space those out.
