# ep126-nine-oh-nine: r5 critic (rescue look, r4 must-fix only)

Checked on the preview (built 01:49 UTC, after the story.json change at 01:23; matches HEAD 90ebed1), every frame from 40.3 to 41.4 s at 30 fps, plus out/ep126-rescue-sheet.png at about 300 px wide. Preflight: 0 blocks, flash PASS, no clip or staging rows.

## r4 must-fix 1 (S28 / L28 overlap): fixed
- Grandma and grandpa are now teleported to SIT_G / GP_STAND on L28, and the L28+0.2 / L28+0.4 walk keys and the `staging_ok` entry are gone.
- From the first frame of S28 (about 40.67 s) grandma is alone and centred with her face clear. Grandpa is out of frame, and no purple or tan limbs tangle. The bodies don't jump or slide into place after the cut. The only motion is the scripted sit and pat (from L28+0.6), and it plays smoothly.
- S27b's end still reads: `me` in a wide-eyed close-up on "at THEM." holds to the cut, and nobody walks through his shot.

## Should-fix (not blocking)
1. The "Grandma said," caption shows up on S27b's last frame, about one frame (0.03 s) before the cut to grandma. You can barely see it. Snapping the caption start to L28 would tidy it.
2. Once grandma sits, her knees render as pale white blocks (sheet, last 4 frames). This comes from the unchanged sit cue, not from this fix. It's worth a glance in the proof.

No regressions. The scores stand as they were in the earlier rounds.

Verdict: approve
