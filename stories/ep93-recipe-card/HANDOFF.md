# ep93-recipe-card: handoff (DROPPED 2026-11-04)

**Status: dropped.** Not approved after round 2 of 2 (the brief allows no rescue round). No PR opened.

## Verdicts
- Standards r2: **approve** (no must-fixes). It passes originality against ep96-friend-card and ep89-sister-diary,
  the kids rule, set text and flash. Watch 106 to 109 s and the loop seam on any final.
- Critic r2: **revise**. Average 6.9 (bar 7), faces 4 (floor 5), warm 5. Scores: hook 6, back-row 7, narrator 9,
  appeal 9, relationships 7, feeling 6, big idea 8, eerie 6, twist 8, lore 7, warm 5, variety 7, faces 4, sound 7,
  captions 8. All 10 r1 must-fixes were done or nearly done.

## Open must-fixes (critic r2, `reviews/r2-critic.md`)
1. S40 (69.2 s), S54b (89.6 s), S68a (113 s): Grandma must face the camera, close and soft, with her whole head
   in frame. Today these show the back of her head (including over "She didn't look SURPRISED").
2. S13 (27.0 s) and S22 (40.5 s): the back of her head fills the frame. Frame the tin or the card instead.
3. S24 (44.0 s): my head is cut off at the top. Frame the hand writing.
4. L69b (117.5 to 119.5 s): drop Grandma's cut-off head from the bottom-right corner.
5. S38b (66 s): the wet stain's bead reads as an orange ball. Make it a thin glossy streak.

The fixes are all framing, and the premise scored well (big idea 8, twist 8). If a later batch revives it, one
builder pass on Grandma's faces is likely enough, followed by a fresh 2-round review.

## State of the build (on this branch)
- Preview 123.7 s, 156 shots, preflight 0 blocks, clipcheck 0, flash pass (worst point 107.8 s).
- measure.py on the preview: picture changes 15.4 and 16.9 per 10 s, motion energy 7.15, longest still 0.27 s,
  sound 2.02 events per 10 s. Warns: character-motion share 0.455 and the spec cut rate.
- Title "Grandma's Recipe Is In My HANDWRITING 🍲", cover_s 56.8, hold "batch 9a: in review" (kept).
- History: de-templated against ep96 (lemon timer marker bottom-right, steam loop). r1 moved S01 to the blue tin
  (an ink close-up had echoed ep89), put the rule in L02, and added L02b, L54b and L69b.
- No engine bug found.
