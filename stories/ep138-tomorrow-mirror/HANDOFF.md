# ep138-tomorrow-mirror: handoff

Branch `claude/batch15a-ep138-tomorrow-mirror` (batch 15a, interactive-lane pilot 3 of 3).

## Where it stands
- Built and previewed; framing pre-check fixes applied.
- Round 1: standards **revise** (L20/L26 cadence, L31 to "BELIEVE"); critic **revise**, avg 6.8 (C4 empty-bench clue didn't read in S17/S18; S03 board value 13 broke the logic; date close-ups not glass-like; the meter read as a pillar; blank mirror in S04a/S21; S27 too wide; 0.6 s dead silence at the drop; L08 mystery hook).
- Word fixes are in (writer). Round 1 picture and sound fixes are with a fresh builder.
- Next: round 2 re-runs both reviewers (both said revise), checking only round 1 must-fixes and regressions. Then at most one single-fix rescue, then drop.

## Queue spacing (standards r1)
- Keep the three pilots (ep136, ep137, ep138) at least 2 apart.
- Keep ep138 3 or more from ep96-friend-card, ep94-today-again, ep124-future-call and ep130-rival-clock.
- Not next to ep92 or ep98 (both `if` openings).

## Engine bug (not fixed, engine is off limits)
`post.to_output` crashes ("box can't exceed original image size" / "box offset can't be negative") when `sway_amp` is above about 0.005 on shots at zoom 1. The build uses 0.005.
