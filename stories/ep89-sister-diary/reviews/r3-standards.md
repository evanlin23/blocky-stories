# ep89-sister-diary: standards, round 3

Verdict: approve

This round only re-checks the two round 2 must-fixes. Everything else in round 2 still stands.

Checked: frames pulled from the preview at 40.2 to 41.0 s (10 fps) and 65.5 to 67.3 s (5 fps), and a signalstats YAVG scan of all 3672 preview frames.

1. **S35 (L24, "I shut it.", 40.4 to 40.7 s): fixed.** The camera now looks down at the desk from above. The lamp, the desk and the diary are lit through the whole close, and the lid never covers the lens. The shot cuts cleanly to the lit bed shot for "I didn't SLEEP."
2. **S59 (L41, "Her door ... an INCH.", 65.8 to 67.1 s): fixed.** The camera is in the hall now. A hand pushes the lilac door, and her lamp-lit room shows through the gap. The shot's point reads.
3. **Brightness scan:** the lowest frame mean is 55.8/255 (frame 1293, 43.1 s), and no frame is under 50. That matches the builder's report. No full-black stretches are left.

No must-fixes. `hold` in package.json is removed after approval, as noted.
