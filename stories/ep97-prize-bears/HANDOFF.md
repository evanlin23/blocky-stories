# ep97-prize-bears: handoff (dropped, 2026-11-04)

**Status: dropped.** Not approved after 2 review rounds (the batch 9 limit, no rescue round). No PR opened. `"hold"` is still in package.json.

## Last verdicts
- **Standards r2: approve** (`reviews/r2-standards.md`). Note for any future queueing: keep it at least 3 slots from floor-thirteen (another forgetting-ritual story).
- **Critic r2: revise**, average 7.2, nothing under 5 (`reviews/r2-critic.md`). Scores: hook 7, back-row 8, narrator 9, appeal 9, relationships 8, feeling and clarity 7, big idea 7, eerie 6, twist and loop 8, lore 5, warm 7, shots 6, faces 6, sound 7, captions 8.

## Open must-fixes (critic r2, all build fixes, all in set.py camera and blocking)
1. **S35b (66.27 to about 66.8 s):** the camera starts inside the wall or counter (cam y 10.64), so about 0.5 s on "TOKEN" is blank white or lavender and the ticket meter drops out. Start the camera at about y 10.04, where it ends, and keep the drift small.
2. **S35a (65.6 s):** the token is a tiny orange disc cut off at the right edge of an empty counter. Aim at the token, centred, filling about a third of the frame.
3. **S21b (38.87 to 39.67 s):** the closet is lit and full of bears as the prize man walks in, which spends the L23 "FULL" reveal 2 s early. Keep it dark (shut the door behind him or block the doorway with his body), with no bears before S23.

## Risk to watch if it's revived
- **Flash:** the worst extended run is 3.83 s at 37.87 to 41.7 s (S21a to S23a) on the preview, against the 4.0 s bar. Standards' fallback: lengthen the door swing in `cdoor("L22", 24.0, 85.0, 0.8)` to 1.6 s, and match S21a/S21b's `cfill` to S22a's. Fix 3 above (a dark S21b) should also help.

## State
- **Words:** fixed in round 1 (the rule is now "from whoever played LAST": L03, L05, L34; and L40). Voice, asr, preflight (0 blocks), clipcheck (0) and measure (0 block, 0 near) all pass on the round-1 fix build. Film 78.7 s.
- **Effort to revive:** the three fixes are small camera and blocking changes. Reviving it needs an owner or orchestrator call to allow a third round, then a fresh builder, critic round 3, the PR and the proof.
