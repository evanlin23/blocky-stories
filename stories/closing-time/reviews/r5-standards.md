Verdict: approve

Reviewed: the round diff (lines.json, make_story.py, story.json, package.json, blocky/sound.py), preflight, and preview frames of L01, L48, L53, L56, L66, L67, the S03 close (3.6 to 5 s, 5 fps), and 22.4 to 25 s and 86.4 to 89.8 s at 15 fps with per-frame luma.

r4 must-fixes, all done:
1. L48 is now "And the REGULAR / was LEANING / on the GLASS."
2. L53 is now "Every SLIT / was an EYE."
3. L66 and L67 are now "And every / WAVE GOODBYE" and "was a / CURTAIN CALL."
4. The pin is now "Comment WAVE before the Regular sees you skip it."

New this round:
- L01 "You have to wave goodbye to the big tank." is a `must` opening, and package.json has `"opening": "must"`. The next story in the queue, moving-day, opens "In this town", so the two neighbours don't share a shape. Pass.
- L56 "MOP in hand." Pass.
- `sting_mid` is a new kind in the shared `sfx_synth`. `sting` is untouched, and only this story's L01.3 cue uses the new kind, so it's opt-in and other stories' defaults don't change. Pass.
- Fiction, kids, IP: pass. No set text or signs in any frame I pulled. S03 is three adult staff at the rail. Dev with the mop is an adult. No game name.

Flashing: preflight PASS (0 blocks). The worst 1-frame reading is 2/s at 87.5 s (a 1.3 s run) and the worst 3-frame reading is 3/s at 23.6 s. Both are at the bar, not over it.

Nice-to-have (picture only, do it before merge; no re-review needed):
1. S50 (87.8 to 88.47 s): in 0.67 s the camera flies from behind Dev's head out through the glass (luma 82, 68, 87, 60, 46, 61), and then the L60.3 `hallfill: 3.0` step comes in. Drop S50's first cam key so it starts at `[3.9,-1.0,2.2]`, already in the water. Ramp `hallfill` in over about 0.4 s instead of stepping it.
2. S15 (23.07 to 23.73 s): the pillar caustics crawl, then two cuts follow in 1.4 s. Change L19.1 `caustic` from 0.25 to 0.12. Give L19.2 the same 0.12.
