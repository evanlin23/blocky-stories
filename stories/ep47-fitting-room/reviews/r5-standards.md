# ep47-fitting-room: standards, round 5

Verdict: approve

## Round-4 must-fixes

1. **Title:** done in package.json: "In This Town Every LIE Pins a Tag to Your Clothes" (49 characters, title case, one word in caps, no spoiler).
2. **`hold`:** still in place, which is correct. Remove it at ship once the critic approves (Packaging).
3. **`shape`:** now `"about-me"`. Done.

## What I checked (all pass)

- **Fiction:** the frames have no words anywhere. The signs are pictures, the tags show only the hook glyph, and the phone (S34), the ticket and the sign card are blank. The voice.py homophone (`orel` to `aurel`) only affects the ASR match, and the caption still says AUREL.
- **Kids and mature themes:** the cast is all adults and nobody is hurt. The pincushion appears only as a cutaway. The Empty's lean (S63 to S66) is held poses and never touches anyone.
- **IP:** all faces are our own, and no game is named in the package or the captions.
- **Originality:** `check` has 0 blocks, and the montage cut doesn't change the world, rule, creature or twist.
- **Flashing:** the preview passes: 1 flash and 3 changes a second (1-frame), and 2 flashes and 5 changes (3-frame) at 15.6 s. The description line is 0:01 to 2:10. The loop seam with `fade_in: false` reads 0 flashes (1-frame) and 1 (3-frame), with no dark first frame. The engine change is opt-in, and the tests pass (91). The tightest stretch is now 15.3 to 20 s: the S11 push toward Uncle's white apron (frame mean 0.38 to 0.64 in about 1 s), the cut to S12, the drop to the dark train (S13, 0.24) and the bright S14. That's 5 of the 3-frame changes the bar allows (6). Re-check this stretch first on the Actions final.
- **Package and hard rule 8:** the description says "It's made up.", `made_for_kids` is false, and nothing has dashes, semicolons or banned words.

## Nice-to-have

- story.json `title` still reads "In this town, every lie you tell pins a tag to your clothes". The upload never shows it, but copy in the package.json title so they match.
- If the final comes close on the 15.3 to 20 s stretch, slow the S11 push or bring the apron's exposure down a little.
