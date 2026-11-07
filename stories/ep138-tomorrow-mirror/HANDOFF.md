# ep138-tomorrow-mirror: handoff

Branch `claude/batch15a-ep138-tomorrow-mirror` (batch 15a, interactive-lane pilot 3 of 3).

## Where it stands
- Round 1: standards revise, critic revise (6.8). All must-fixes applied; the mirror marker was rebuilt as world-fixed scene geometry (it had ridden on the camera).
- Round 2: standards **approve**, critic **approve** (avg 7.2, all four clues read at phone size).
- Hold removed; check, gate (OPEN), shardcheck, staging and pytest pass. PR #416. Proof run 42346838910 passed; proof qa PASS (qa/ep138-tomorrow-mirror.json). Merge once `test` is green. Proof qa should-fix: S25 punch-in pushes the chrome post out of frame for about 1 s.
- Should-fixes (not blocking): S03's backward 12 can read as "51"; S04a/S21 mirror still a bit like window panes; S27 could push in; L08 and L20 both key "TWO".

## Queue spacing (standards r1)
- Keep the three pilots (ep136, ep137, ep138) at least 2 apart.
- Keep ep138 3 or more from ep96-friend-card, ep94-today-again, ep124-future-call and ep130-rival-clock.
- Not next to ep92 or ep98 (both `if` openings).

## Engine bug (not fixed, engine is off limits)
`post.to_output` crashes ("box can't exceed original image size" / "box offset can't be negative") when `sway_amp` is above about 0.005 on shots at zoom 1. The build uses 0.005.
