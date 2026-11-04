# ep93-recipe-card: handoff

- 2026-11-04: de-templated against ep96-friend-card (standards must-fix on ep96's r1): the rule marker is a lemon
  kitchen timer bottom-right, and the loop ends on a steam-curl match cut.
- Round 1 (both said revise):
  - Critic: average 6.5, faces 3, hook 5, 10 must-fixes.
  - Standards: 5 must-fixes. The ink-close-up opening echoed ep89, so S01 is now the blue tin with the old card
    and steam. The emoji is now 🍲. script.md was synced to lines.json.
  - The writer applied the words, title and package fixes: the rule moved to L02, L02b, L54b and L69b were added,
    and L71 was restored. Expected length is about 124 s.
- Now: one fresh builder applying all r1 build must-fixes. Next is round 2 (the last): critic and standards both
  said revise, so both re-run.

## Fix round 1 progress
- Restart 2: plan.py/set.py/cards.py already had most r1 edits; REV bumped to 4, make_story rerun, full voice re-run started (check voice-timings L71 chunks).
- voice done: 123.5 s, 156 shots.
- asr fixed (tempo/commas, asr_forgive old's), L71 caption 'nineteen year old's'; clip S018 camera moved. Next: stills + preview.
- stills of 0-29 s checked ok; preview render started (render --preview --force).
- preview rendered+mixed (out/work/ep93-recipe-card/ep93-recipe-card-preview.mp4). Next: preflight, measure, frame review.
- found stale frames in frames-preview (old run mixed in): deleted dir, re-rendering preview clean (log out/ep93/preview5.log).
- clean preview done; checking flash/preflight.
- fixed S033/34 (Nell face), S108 (black wedge), S133 reveal two-shot; re-rendering those shots (preview6.log) then finish+mix.
- r1 done: preview clean, preflight 0 blocks, cover_s 56.8. Report next.
