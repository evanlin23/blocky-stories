# ep80-snow-globe: HANDOFF (dropped, 2026-11-03)

**Status: dropped at the creature test.** No PR opened. Not voiced, not previewed, still on `"hold"`.

## Why
The Stander (a far-too-tall person outlined only by settling snow) failed the creature test three times. The three-try limit is used up. An Opus critic judged each still at phone size:
- Try 1: "silly". A solid white snowman or robot in a hat.
- Try 2: "silly". Snow on top surfaces with gaps worked better, but the face read as a surprised puppy and the cap as a snowy shed.
- Try 3: "silly". A soft rounded white box with a flat cap; two slits over a tall "O" mouth read as a cartoon gasp; the mouth ran into the body like a necktie; warm frontal light; small in a busy bright set.

The critic's root-cause note: tweaks to the face cannot save it, the whole figure is wrong. It needs a new silhouette (taller and thinner, filling the frame), light from below or behind, a jagged mouth that stops above the body, and tiny or missing eyes. The block-and-snow-cap approach reads as friendly (snowman) at 270 px.

## Open must-fixes if someone retries
- Redesign the Stander silhouette; do not reuse the snow-capped block body.
- Grandpa's face is not readable in the L47 shot (back of the head only); cut to a separate profile shot.
- Gus is moved about 350 px left on L47 as a hack; needs a proper staging pass.
- Rim light barely registers.

## State
Stills: `out/ep80-creature-still-try{1,2,3}.png` (gitignored, may be gone). Partial `set.py`, `generator/make_story.py`, `story.json` and `voice-timings.json` are committed on `claude/batch7-ep80-snow-globe`. No engine bugs found. No review scores (no reviews run).
