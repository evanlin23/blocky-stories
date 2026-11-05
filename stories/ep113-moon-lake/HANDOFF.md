# ep113-moon-lake HANDOFF (batch 11, branch claude/batch11-ep113-moon-lake)

Stopped at the weekly usage limit (resets 2pm UTC / 8 AM Central). No PR opened yet.

## Done
- Recast (moon never shown whole; no creature test), built, voiced, preflight 0, framing.py 0, flash, measure pass.
- Round 1: standards revise (package: hold removed, cover_s 7.0, done), critic revise (cap, snow, payoff, etc., fixed).
- Round 2: standards APPROVE (r2-standards.md). Critic REVISE (r2-critic.md, avg 7.1) with 4 fixes.
- Rescue pass (the one allowed; RULES decision 3 says "the fixes a review named", the brief says "single"; I took the one rescue for all four) started with a builder; it hit the limit mid-way. Its edits to generator/make_story.py, set.py, story.json may be partial: check `git diff`/last commits.

## Rescue fixes still to do/verify (exactly these four, nothing else)
1. S01, S93: water under the feet blue-green #1fa6a0 with one pale cream glow disc below the feet; glow reads from frame 0.
2. Night lake (S36, S49, S55, S56, S77, S85, S86): lit water capped ~#bcd6e8; no pixel at pure white.
3. S88 (L66): me three-quarters to camera, face clear of arm, >=1/5 frame wide.
4. S73 (L54): both palms flat on the cream surface, fingers on a crater, face readable.
Plus from the second orchestrator: local `blocky flash` reads LOW. Get it to <=3/s locally, no extended run over 3 s, steady glows (worst now 4/s at 31-37 s dial close-ups S25/S28 and the S84->S85 cut).

## Then
re-render preview, finish+mix, framing.py, preflight, flash, measure; ONLY the critic reviews once more (r3-critic.md); if approve: check, gate (OPEN), pytest; open PR "ep113-moon-lake: build (batch 11)" (queue note: `cost` opening, keep off ep54, ep96, ep83, ep99), proof qa, merge when proof qa passed and `test` is success. If the critic still says revise: drop (STATUS dropped, no PR).
