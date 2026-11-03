# ep50-beach-huts handoff

**STATUS: dropped (2026-11-03).** Round limit reached; the second orchestrator records the drop on main. No drop PR was opened. No hold removed, not queued.

## Why
Reviews r5 and r6 (the last two allowed rounds) after the r4 fix pass:
- r5: critic revise, standards revise (music setting duplicated ep41 and mirror-maze; frame 0 stray head).
- r6: **standards approve**, **critic kill** (avg about 6.4; middle 4, creature 4, twist 4; approval needs avg 7 and nothing under 5).

## Open must-fixes (critic r6, `reviews/r6-critic.md`)
1. L42-43 (66-70 s) wall shadow reads as rooftop shadows: no huge shoulders / tiny head.
2. Creature (72-83 s) is a grey robot-like head behind a striped canvas: reads as a deckchair with a head, silly not scary.
3. L75 (125.7 s) dim green frame, doesn't read as glass. L76: reflection about 12 px tall, laptop a clipped white slab.
4. Faces cropped to half at L52 (83.5 s) and L57 (92.5 s). Opening reflection reads as a blurry face, not upside down. Logic slips: L34 "a DOT" shows a full figure; L69 "in the puddle" has no puddle.

## What passed
Flash (strobe-only bar; 7 changes/s on the 3-frame reading is a warning, upload adds the "Flashing lights and fast cuts" line), measure.py 0 blocks, preflight 0 blocks, clipcheck 0, `check` clean, loudness -14.1 LUFS / -1.8 dBTP. Title "Beach Hut Windows Know What You WANT 🪟" (7 words), music root 46 lydian 88 bpm (unused elsewhere), L01 "If anyone sees your reflection in a window, they'll know."

## Notes if ever revived
- Never upload ep50 next to mirror-maze (both have a reflection rule); at least 4 uploads apart. Also keep away from ep38-drive-in.
- Fixed this session: inverted laptop hinge, grade/panes tint, re-voiced L34/L42/L43/L71 for ASR.
- Real fix needs the creature and the shadow/twist shots redesigned, not another polish pass.
- No engine bugs blocked this work.
