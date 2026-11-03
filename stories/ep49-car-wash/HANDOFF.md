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
