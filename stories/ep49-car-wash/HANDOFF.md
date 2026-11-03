# Handoff: ep49-car-wash opening fix (paused 2026-11-03, usage limit)

Branch `claude/opening-ep49-car-wash`. No PR yet.

**Done**
- Warning opening built and previewed (141 s, polish on, 13 recorded hits).
- Round 7 reviews: critic revise (avg 7.2, hook 6), standards revise (flash only).

**Fix round in progress (stopped just before finish and mix)**
- The WIP in this commit is uncommitted builder work. Check `git show HEAD`: lines.json, make_story.py, set.py, script.md, package.json and voice-timings.json.
- It should include the opening-variety change (research lead, 2026-11-03):
  - L01 "Here, you have to FREEZE the second your COLLAR BELL rings."
  - L02 "It means you're about to MESS UP."
  - package "opening": "must"
  - The pie gag is cut.
- It should also include the r7 must-fixes:
  1. S01: the bell centred, big, above the captions, swinging hard, on a bright kiosk with sky behind (no blown-out grey), with a doubled push-in.
  2. S02: the bell above the captions, and the ding on "UP" about +4 dB.
  3. Flash: the `car:q2` cue in S42 (58.3 to 59.8 s) gives 7 changes/s. Stop the car out of frame.
  4. Set old_title to main's title. Remove `hold` once 1 to 3 pass.

**Next**
1. Verify the WIP against that list. Re-voice L01 and L02 only if they aren't already voiced (L01 under 2.2 s).
2. Timeline, preview, flash (all measures pass) and preflight.
3. Review round 8 (the last normal round), then gate, PR and qa.

**On resume:** merge main first: polish v2.2 (#168) and v2.3 (#175) are in.
- Keep this story's own `sfx` to 2 to 4 events per 10 s in all. This round added many sfx, so thin them.
- Use `"hold": ["Sxx"]` for frame-exact shots.
- Read builder.md and docs/engine.md, under The polish pack.


## Update 2026-11-03 (builder resume)
r7 must-fixes verified in make_story.py; sound rev 8; full preview rendered, finished, mixed (140.4 s). flash PASS (warnings only), preflight 0 blocks, measure 0 block/0 warn of 12 (sfx 3.92/10 s), check ok. Next: review round 8, gate, PR, qa.


## Update 2026-11-03 (builder, r9 fix round)
- Twist rewritten as "the ring I never heard" (shape echo, new title). make_story.py premise/twist match script and package; sound rev 9. Re-voiced L57, L62, L67, L70 only; film now 140.2 s.
- Shots redrawn by line: L01 to L02 (S01 to S03: man in front of the kiosk's cream wall, blue roof, whole head and both eyes, bell above captions), L56 (S76: two-shot from the +y side, nothing in front), L57 (S77: eyes from the clapper up to the five), L62 (S82: side-on walk, front copy gone), L67 (S88: S28's angle, sunrise, no footprints), L70 (S91: cold cut to the line, lamps on, front copy in the door). Shot numbers in the writer's notes are one off from L57 on.
- Gotcha: `render --preview --force` only redraws the step frames; the in-between frames of moving shots stay stale and finish/mix then use them (a stale old L67 frame flickered at 130 s and failed flash). After a retime, delete out/work/<name>/frames-preview and render everything.
