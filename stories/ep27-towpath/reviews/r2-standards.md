# ep27-towpath: standards, round 2

Verdict: revise

The round 1 fixes hold. The copied voice and roll call are gone, the title and pin are new, and the pin asks about the L11 plant. Fiction, kids, IP and package pass. The set has no text, the creature is olive and weed green, and the description has "It's made up." and no banned words. On originality, the gap it fills is a dog's spot, and the setting, creature, rule and warmth are all unused in this batch. Preflight flash (preview, quarter-res, every 4th drawing) passes. The worst reading is 2 flashes a second at 91.6 s, which is right at the bar.

## Must-fix

1. **Loop cut (S83 to S01).** The film still dips to dark across the wrap. Mean luma goes 179, 150, 121 over the last frames and 44, 88, 132, 175 over the first. This happens because `post.py` fades both ends whenever `tail` > 0. Every Shorts replay would flash. Set `"tail": 0` and add a pause beat `P04` of 0.25 s after L72 (no words), so the water still plays and neither end fades.
2. **S54, L48 "It didn't BLINK" (91.0 to 91.9 s).** This is a dark, blurred frame (luma 93) between S53 (165) and S55 (150). It is the preview's worst stretch. At full res and every drawing it could go over the bar. Show the eyes through the white fogged glass, like S47's intended white, so it stays within about 20% of the shots on either side.
3. **S78, L67 (126.5 to 128.4 s), and S76, L66 (about 124.8 s).** I'm tipped about 25 degrees over Moss at the water's edge. It reads as me falling onto her, and the script promises she is never in peril. Pose me upright, crouched on the hedge side of her, as scripted.

## Nice-to-have

- S01 and S83: my face is mostly hidden behind the hatch top.
