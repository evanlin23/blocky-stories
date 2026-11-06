# warm-shoes r4 critic (meter-fix rescue look, chalk-count inset on depth-of-field shots), 2026-11-06

This look covers only the rule-meter shots. I compared the before and after stills (full size, cropped top left and judged at 360 px wide) and checked the redrawn preview at 1.6, 2.0, 46.0, 48.3, 50.0 and 50.9 s.

**1. Does the chalk digit read at phone size (DoF shots)?**
- Reads, and is fixed from a grey disc: S01 (0-1.5 s, "8", sharp), S37 (45.1-46.6 s, "11"), S50 (60.5-62.3 s, "12", the clearest), S99 (113.8 s, "0"), S109 (126.0 s, "0"), S117 (135.6-137.8 s, "8").
- Reads, but soft (about as faint as the non-DoF shots, where the digit always sits half under the tag): S04, S05, S06 (4.0-9.1 s, "8"), S15 (19.2 s, "10"), S16 (20.0-21.4 s, "10"), S39 (48.1-48.9 s, "11", borderline).
- **Doesn't read: S02 (1.5-2.1 s) and S41 (49.8-51.0 s).** The occluder caps the panel at 0.15-0.17 m, which is no closer to focus than before. The panel is still a dark smudge with no digit. S02 is covered a little by the big "8" board in S01. S41 has nothing.
- S52 (63.3-64.5 s): the panel is hidden, as it was before. Only the tag shows.

**2. Anything worse?** No. The panel sits in the same place on screen at the same size, and it is a little brighter where it's now sharp. It overlaps the tag the same way as before and never covers a subject. There is no z-fighting: the frame offset is still 1.5 mm at 0.15 m and scales with depth. Inside S01 the panel shifts against the tag between 0.0 and 0.7 s. It did that before too, as the lens animates. The non-DoF shots (S24, S33, S34, S85) are pixel-identical. Nothing pops beyond what the old blur did.

**3. Fix (one):** on the shots where `inset_depth` gets capped below 0.25 m (S02, S41, and S52 if wanted), hide the 3D panel and have the finish step draw the chalk digit as a 2D card at the panel's screen position. That is the same layer as the lighthouse tag, so no blur can reach it.

Must-fix: S02 and S41, as in 3. Everything else passes.

## Rescue (S02 and S41 only), 2026-11-06

These two shots now draw with depth of field off (`INSET_NO_DOF`), and the panel sits at 0.15 m. I judged the new full-res stills at 360 px wide.
- S02 (frame 54, 1.5-2.1 s): the chalk "8" is sharp and reads, half under the tag like every other shot.
- S41 (frame 1512, 49.8-51.0 s): the chalk "11" is sharp and reads. The panel sits in front of the cat's ear tips, the same as on other shots, and it doesn't cover the eyes.
- Losing the blur doesn't hurt. S02 still reads as a close shot of the shoes: the fence behind is a little crisper, but it's still soft enough not to compete. S41's cat face is crisper and the green eyes pop. Neither one jumps out against the DoF shots next to it at 0.6 s and 1.2 s.
- Note: `warm-shoes-preview.mp4` has not picked up the change. Its frames for S02 and S41 are dated 13:29 and 13:42, before the fix. The S02,S41 re-run logs 15 frames in 0.0 minutes, and the preview still shows the old blurred panel there. So this pass rests on the two stills. Because depth of field is off for the whole shot, every frame should match them. `proof.yml`/qa should confirm across each full shot.

The must-fixes are in. Nothing got worse.

Verdict: approve
