# ep102-aunt-peaches, r12 critic: S19 rescue check (93714bda, rev 18)

Verdict: approve

Scope: the r11 must-fix (S19 / L08.2, "on the SILL.", 19.50-20.27 s, f585-607) and anything new it caused. No proof is drawn yet at rev 18, so I checked it by projection. I used `measure.project` with S19's camera as `polish.cam_specs` / `checks._cam_at` give it (the way staging.py loads it), the head box from framing.py (HEAD_Z, HEAD_HALF_W/H), and the peach and sill positions from set.py.

## r11 must-fix 1: in
- **The peach clears his head from the first frame.** Peach 0, the one already on the sill at the cut, is at screen (-0.49,-0.24) to (-0.46,-0.29). His head box is x 0.27-0.86, y -0.22-0.10, so the gap is 0.76-0.84 for all 23 frames. Inside the shot the row grows to about 7 peaches (n 1 to 12 over 1.4 s). Every peach that shows clears the head by 0.35 or more. Only peach 11, which is still hidden during S19, comes within 0.09. All the peaches sit inside x ±0.49. The builder's "0.23 over 61 frames" doesn't match my count: the shot is 23 frames. The result holds either way.
- **A new angle from S18.** The view direction differs by 97° (104° in plan). The camera is now high and on the left, looking down 34-35°, where S18 was low and on the right. It no longer plays like a jump cut.
- **No speck, no warp.** His head is 0.46-0.48 of the frame's width and the sill 1.01, so he is a clear foreground figure and the sill a clear half-frame shelf. Lens 16 here gives about 74° vertical and 45° horizontal: wide, but the room isn't stretched at that distance (2.5 m to him).
- **S56 (L26) unchanged.** The diff touches only line 281 and REV.

## Should-fix (not blocking)
1. **S19, the first frames:** the camera sits at z 3.4, the walls' own height, and the room has no ceiling. The back wall's top edge projects at y 0.89 at f585 and leaves the frame by f607, so the top 5% of the frame looks past the wall. That band is mostly under the meter. qa should check the proof's top strip there. If it reads as a gap, drop the camera z to 3.1 or tilt the aim 0.2 lower.
