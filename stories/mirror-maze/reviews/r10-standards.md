# mirror-maze, r10, standards

Verdict: revise

1. **S39 (L33, 59.73 to 61.47 s): the light still pumps.** I'm framed and centred now. Face luma swings from 193.5 to 213.8, outside ±8. At 61.33 the whole figure brightens (+10, the bottom third +19). That's not a glint or a caption pop. It's in the raw render too, and the framing drifts right about 35 px, so the cause is the following camera plus the camera fill. On the 3-frame count, 59 to 62 s reads 2 flashes and 4 changes, over the bar of 1 and 3. That's a risk on the 4x-denser final. Fix: drop `follow="guy"`, fix the camera on the pane's world spot, and set `camfill` to 0.7.

S38 to S40 continuity holds. Only S39 changed.
