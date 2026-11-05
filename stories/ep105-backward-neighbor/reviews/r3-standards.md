# ep105-backward-neighbor: standards, round 3 (2026-11-05)

Verdict: approve

This round checks only the one r2 must-fix.

- **L01 is now `count`.** "Vern's calendar says / almost eleven thousand days LEFT. / He said goodbye / the day we MET." It opens on a number, not on "I…" or "My…", and the number doesn't add up: almost eleven thousand days left, and yet he says goodbye on day one. That fits opening-variety.md's "a count that's wrong" ("Four people got in the elevator. The mirror shows five."). `package.json` `"opening": "count"` matches it. Batch 10 now runs confess, ban, must, count, cost, so no shape is over 1 in 3 and `ban` is 1 of 5.
- **The tag matches.** Frames 0 to 120 (0 to 4 s) show "10,950" with a comma, top-left, from frame 0. 10,950 days is exactly 30 years, which "almost eleven thousand" and "thirty YEARS" (L03) both match.
- **The loop reads as one sentence.** "So that's why he cried. Vern's calendar says almost eleven thousand days left. He said goodbye the day we met." The cry gets its reason, and the count sets up the goodbye.
- **Nothing new broke.** The title still lands on L01's "the day we MET". The description and pin still match the story, and nothing in them claims to be real. Preflight shows 0 blocks, flash PASS, 3f at 7/s (warn only). On the final, still watch 15.5 to 18.5 s and 100.8 s.

## Queue note
Keep ep105 away from ep94 (`count`) and ep99 (aging), and away from ep106 (`count`) if it comes back.

## Nice-to-have
- script.md line 6 ("Changed from the pitch") and line 60 still quote the old line 1, "My neighbor VERN / counts our days BACKWARD." Update both so they quote the new line 1.
- `package.json` `"hold"` still says "scripts only, not built yet". The team clears it at release.
