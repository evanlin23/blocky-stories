# night-mower, round 2: standards

Verdict: revise

Passes:
- **Fiction:** no lettering anywhere. The clock shows only "3:00", and every name is made up.
- **Kids and mature themes:** only objects tip, and nobody is hurt. Me at S28 is scared but never in danger.
- **IP:** our own faces and an unbranded mower.
- **Originality:** checked against all 40 stories and the batch.
- **Package:** no dashes, semicolons or banned words. "It's made up." is there, and `made_for_kids` is false.
- **Opening:** `"opening": "confess"` matches L01 "My NEIGHBOR mows his lawn at three a.m. with his eyes SHUT." Batch 6 has two `confess` (this story and warm-shoes) out of 7, under 1 in 3. No title in the batch, the queue or the last 7 uploads starts with "He". L46 to L01 loops as one sentence.

Round 1: must-fix 1 is done (L34 is one line and L35 is gone). Must-fix 2 is not done.

## Must-fix
1. **S27 (37.07 to 37.97 s), flashing.** The preview's 3-frame reading still sits exactly at the bar (3 flashes, 6 changes) at 37.07 s, so the full-rate final could fail on Actions. The cause is a bright, dark, bright sandwich inside 0.9 s:
   - S26 is the warm-lit Dad with binoculars (mean luma about 0.39, 25% bright area).
   - S27 is the dark blue lawn shot with sky and trees (0.33, 12%).
   - S28 is the warm room (0.45, 28%).
   - Each cut changes about 0.3 of the frame.

   Fix: merge S26 and S27 into one shot from 35.80 to 37.97 s. Start on Dad raising the binoculars, then ease over his shoulder (a slow arc, no post crossing the lens) onto the floodlit lawn with Mr. Odell mowing. This deletes the 37.07 cut. The camera keeps moving, so the 2.17 s doesn't count as a still. If a cut has to stay, reframe S27 low on the floodlit lawn with no sky or trees, so its mean luma is within 0.05 of S26 and S28, and make it at least 1.1 s long. Rerun preflight and confirm the 3-frame reading at 37 s drops to 2 flashes and 5 changes or fewer.

## Nice-to-have
- The description still opens on the old `ban` line ("Never look at the neighbor's lawn..."). Start it on the new L01.
- script.md is stale in a few places: Line 1 and Line 2, the S01 "Hit on RUNNING", and the quotable line (L06 is now "He says it's FASTER that way.").
