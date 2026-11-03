# ep47-fitting-room r8 critic (rescue round)

Verdict: revise

**r7 fixes**
1. Shoes, 54.17 to 56.2 s (L32): fixed. Two lit brown lace-ups in the middle of the frame, about 60% of its width between them, warm pool on the floor, held through "of SHOES." It reads at phone size.
2. Tape and pincushion, 50.0 to 52.47 s (L30): fixed. Both sit in the middle third, and the push shows from 50.3 to 52.3 s. The coil reads as a tape measure only with the caption's help, which is fine.
3. Mrs. Kettle, about 125.5 to 127.3 s (L71): fixed. She smiles calmly beside her white-tagged husband, so "a lie you BELIEVE" plays over a woman who believes it.

**v2.1 spot-checks:** the first 5 s and last 5 s aren't washed out (the green wall, the tags and the hanger all hold their colour). Voice against the bed in 0 to 5 s: the voice runs at about -15 dB RMS while it speaks and everything else at about -28, so it sits about 12 dB over. That's good.

**New: red fringes from the v2.1 lift.** The raw drawings (frames-preview/f01657.png) are clean, but after post the near-black pixels turn saturated red. You can see it under both shoes at 55 s (the clearest case, it looks like a glow), as a red band under the bench at 50 to 53 s, on the curtain seam, round the narrator's hair at 0.3 and 1.5 s, and round Mr. Kettle's cap at 125.7 s. Cause: in `blocky/post.py` `grade()`, contrast pushes near-blacks below 0, and the luma floor of 1e-4 then scales them by up to about 350 times. For a pixel of (0.06, 0.03, 0.02) at contrast 1.15, the output is (0.81, -0.13, -0.58).

**Scores:** hook 8 · back-row 8 · narrator 9 · appeal 9 · relationships 8 · feeling 7 · big idea 6 (advice only) · scare 8 (the shoes land now) · creature 7 · twist 8 · lore 7 · warm 7 · variety 8 · faces 7 (the red hair fringe) · sound 8 · captions 8. Average 7.7.

**Panel:** as r7, except the creepy fan now says "the SHOES 😭" at 55 s. Risk: "why are the shoes glowing red?"

**Must-fix**
1. Engine, `blocky/post.py` `grade()`, lift block, every shot (worst at 54 to 57 s): clamp `out` to 0 or more before the lift, floor `l0` at about 0.02 rather than 1e-4, and add the rest of the lift as neutral grey (`s = l1 / max(l0, 0.02); out = out * s + (l1 - l0 * s)`). Add a test that a near-black warm pixel stays near-black. Then redraw the post and check 55 s.
