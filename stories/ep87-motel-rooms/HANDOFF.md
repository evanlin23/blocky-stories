# ep87-motel-rooms: handoff (2026-11-03)

**Status: dropped at the creature test.** No full build, no voice, no reviews, no PR.

The builder's creature test is gated by a critic (opus) at phone size, three tries at most. All three said retry:

1. **Try 1, retry.** Hal read as a normal-sized, friendly clerk. The camera was level, his head sat far below the ceiling, his eyes looked like round glasses with dot pupils, and the light was flat.
2. **Try 2, retry.** He read as a startled, ordinary clerk. He still had big disc eyes. There was empty ceiling above his head and no scale reference, his sleeves were stubby blocks, and the top third was a muddy brown.
3. **Try 3, retry.** He read as a bored, sleepy night clerk (like the "tired of my shift" meme), funny rather than eerie. Nothing showed he is eight feet tall, the desk bell didn't read, and the bottom 40% of the frame was empty desk. "A viewer on a phone would feel no unease."

Why we drop instead of shipping: the owner said, "We shouldn't upload anything that isnt good." Hal is the story's threat, and a silly Hal sinks the countdown.

## Open must-fixes (if someone revives it)
- Height has to read at 360 px. Hal needs something beside him at normal height for scale (a person at normal height, not a small prop), and his head has to be bent or cropped by the ceiling.
- The stare has to read unblinking, not surprised (round eyes) and not sleepy (half lids). Try small, fixed pupils in full white eyes, wide open and not round discs.
- The arms and fingers have to reach toward the camera. The frame needs no empty desk band and no muddy top third.
- Perhaps rethink the design: a stock clerk rig in a blazer may not carry "wrong" at all. The script could use a more uncanny silhouette (too-long neck, too-long arms).

## Engine note (not fixed; blocky/ is off-limits)
The `stills` step kept using a stale `out/work/ep87-motel-rooms/timeline.json`. Set and acting changes didn't show until the builder rebuilt the timeline from a stub `out/work/ep87-motel-rooms/vo/voice.json`. That cost several renders in try 2. Worth checking whether stills should rebuild the timeline when set.py or story.json changes.

## Files on the branch
These are creature-test stubs only: `set.py`, `generator/make_story.py`, `lines.json`, `story.json`. `package.json` still has `"hold"`. The script is unchanged.
