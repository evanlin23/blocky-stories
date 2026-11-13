# ep145-dog-barks: standards, round 3 (rescue re-check, 2026-11-13)

Checked only the round-2 must-fix against the new preview (61.6 s, 1849 frames), using frames at 32.7, 33.5, 34.3, 34.8 and 35.3 s.

## Round-2 must-fix
1. **S19b (32.5 to 34.5 s): fixed.** Grant's blue sleeve and hand are under the red box as it lifts off the windowsill. At 33.5 and 34.3 s the box, with its gold clasp, stays fully inside the frame.
2. **S19c (34.5 to 35.6 s): fixed.** It's now a front three-quarter view of Grant's face and chest. At 35.3 s the red lid with its gold clasp sticks out of his shirt pocket, so the caption "his pocket" matches the picture.

## Other checks
- package.json: `hold` is gone.
- Flash: preflight says `flash: PASS (1849 frames)`. General max 1/s, 3f max 3/s at 26.47 s, red 0. The final is measured on Actions.
- No regressions the fixes caused.

## Should-fix (not blocking)
- S19c, about 34.8 s: on the shot's first frames the box shows large and flat in front of his chest before it settles into the pocket. If S19c gets redrawn anyway, start it with the box already in the pocket.

Verdict: approve
