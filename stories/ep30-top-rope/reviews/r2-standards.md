# ep30-top-rope, round 2, standards

Verdict: revise

Passes: fiction (no set text, the tag and box are blank, the phone glow is blank, the anchor tally reads as two strokes), kids and mature themes (all adults, the slip is only told, nobody hurt, nothing touches me), IP (own faces and outfits, no game names), originality (L47 and L75 fixed, no "built for two" left in the words), package (`made_for_kids` false, "It's made up.", a statement title, no banned words, no dashes or semicolons). Preflight: 0 blocks, 2:20. Preview flash passes, but the 1-frame reading sits exactly on the bar.

## Must-fix
1. **Flashing, S41 to S45 (67.0 to 73.0 s, L41 to L45).** The worst second is still here: 2 flashes a second at 69.07 s (the bar is 2), with a 0.47 s extended run from 64.53 s. Mean luma goes 29.6 (S41) to 104.6 (S42) on the cut at 68.0 s, rises to 113 in S43, then drops to 81 (S44, 71.0 s) and 32 (S45, 72.2 s). The round 1 bridge only took S42 from about 116 to 105. Change `looks` to `"S42": {"lamps": 0.2, "flood": 0.3, "fill": 0.8}`, `"S43": {"lamps": 0.35}`, `"S44": {"lamps": 0.5}`, and add `"S45": {"lamps": 0.5}`. Each cut should step by about 30 or less. Re-run the preview flash until the 1-frame reading is 1 a second here.
2. **Flashing, S57 to S58 (89.3 to 91.8 s, L57 to L58).** S57 is the creature's pale lilac face filling the frame at luma 155, the brightest frame in the scare. It drops to 88.5 on the cut to S58 at 91.03 s and climbs back to 112 at 91.80 s. That's a full-frame swing the final's every-frame measure can count. In S57 set `"flood": 0.15, "fill": 0.4` so the face lands near 110, with the eye highlights still the brightest point.

## For the caller (not this story's fix)
- `lamp-room` (#12), `chairlift` (#17) and `unit-seven` (#18) still carry the "place built for two, the creature fills the empty place" twist that ep30 uses. ep30 is built, so those three should change twist before they're scripted. `unit-seven` is still on Thursday evenings.

## Nice-to-have
- `story.json` title still differs from `package.json`. Sync them.
