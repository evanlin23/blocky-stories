# ep81-eleven-steps: DROPPED after review round 2 (2026-11-04)

Not approved after 2 review rounds (the limit), so no PR was opened. No rescue round.

## Verdicts
- Round 1: critic revise (avg 6.5; creature 3, faces 4, scare 5, warm turn 5), standards revise (creature and title repeat moving-day / ep80 / warm-shoes).
- Round 2: **standards approve** (r2-standards.md): new backwards-climbing creature, new title "Ten Steps By Day, ELEVEN At Night 🪜", cover_s 70.5 all pass.
- Round 2: **critic revise** (r2-critic.md; avg 7.0, none under 5; "nothing points to a kill"; all remaining fixes are camera, lighting or shading on existing shots).

## Open must-fixes (critic r2)
1. L37 (67.4-68.8 s): show the narrator's face side-on on the floor with the flashlight at the gap (now only a striped chest).
2. L38-L40 (68.9-72.6 s): gap face reads as a toy: use the landing face's tan #cdbf9f with brow and a small kit.emit glint eye, darken the top half.
3. L60 (109-110.6 s) and L64 (114.8-115.7 s): Dad's head cropped out; pull back so both front faces are whole, >= 1/5 frame width.
4. L69-L70 (121.2-123.7 s): add side light so the wrong-way knees and hands on the step read as sitting, not a standing silhouette.
5. L56-L57 (102.5-104 s): white blowout, restore shadows.
Note: the morning tag reads 10 while the box is still on the landing (106-112 s).
Nice-to-have (standards): consider cover_s 96.5 s; grade S30-S32 tread inserts to bedroom level.

## State
- Preflight 0 blocks (a Whisper-loop `asr_forgive` "" entry was added after isolated-line checks showed the audio is correct; see story.json). Flash PASS at preview rate; measure.py 0 craft blocks.
- `hold` still in package.json. Branch claude/batch7-ep81-eleven-steps has everything (script, set, generator, story.json, voice, reviews).
- Container restarted several times during the preview render; no engine bug found.
- To revive: one fresh builder can apply the 5 must-fixes (camera/light only), then a round-3 critic.
