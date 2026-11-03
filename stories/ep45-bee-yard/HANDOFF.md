# Handoff: ep45-bee-yard opening fix (paused 2026-11-03, usage limit)

Branch `claude/opening-ep45-bee-yard`. No PR yet.

**Done**
- New opening:
  - L01 "Two people in the BEE YARD. Only ONE CLOCK." (opening "count", research lead's variety rule)
  - L02 "Every clock counts down to your next HUG."
  - L03 "boat arrivals"
- Package:
  - title "One Man Here Has NO Clock ⏳"
  - pin "Comment HUG if..."
  - cover_s 1.1
  - `hold` removed
- Round 3 fixes are in: real hugs, the end dials centred, the sting at -8 dB.
- Polish on. The round 3 reviews were both revise. Round 4 has NOT been run yet.

**Rescue pass in progress (stopped during finish; WIP in this commit, untested)**
1. Split S00, because frame 1 read as a plain guy with Lena tiny:
   - S00a: a chest-up two-shot, Lena's big dial (24) beside the empty air over his head, both faces at least 1/5 of the frame.
   - S00b: a low insert on his floating boots and his loose shadow, with the sting on "CLOCK".
2. L01 is 2.29 s. Give it a per-line tempo to reach about 2.1 s, and re-voice L01 only.
3. Flash fails `general_3f_changes_le_6` (7/s at 38.83 s, S24: the narrator's pale blank dial under the polish grade). Fix it with margin.
4. Preflight block: Whisper misses "On Monday as I waved" (L16).

**Next**
1. Verify the WIP.
2. Preview, flash and preflight.
3. Review round 4. It is the second and last normal round, then one rescue at most. Drop the story if it can't pass.
4. Gate, PR, qa.

**On resume:** merge main first: polish v2.2 (#168) and v2.3 (#175) are in.
- Keep this story's own `sfx` to 2 to 4 events per 10 s in all. This round added many sfx, so thin them.
- Use `"hold": ["Sxx"]` for frame-exact shots.
- Read builder.md and docs/engine.md, under The polish pack.

## Rescue pass result (2026-11-03, later)
- S00a/S00b verified by stills (out/work/ep45-bee-yard/stills/sheet.png); the two stand at x +-0.52 (a sleeve clipped Lena's head at 0.38).
- L01 2.14 s (tempo 1.1); L16 tempo 0.92 so Whisper passes. NOTE: `voice --only` wipes other lines in voice-timings.json locally; run the full `voice` instead.
- Flash: blank dial strength scaled by vis (0.72 at vis 0); preview flash PASS, worst 2/s (limit 6).
- clip: 0 (smoke puffs and Lena's bees in story.json clip_ok; S71 Lena moved to x -0.85).
- sfx: removed the decorative clicks and 3 whooshes: 3.12 events/10 s. measure.py: 0 blocks. rev 5.
- Preview: out/work/ep45-bee-yard/ep45-bee-yard-preview.mp4 (137.8 s). Next: review round 4.
