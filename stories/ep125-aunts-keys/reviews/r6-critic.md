# ep125-aunts-keys, round 6 critic (check of the changed shots only)

Scope: the staging fixes in 78d8589. I looked at the proof artifact `proof-ep125-aunts-keys` (run 43239867841, every drawing at 270x480, 30 fps) frame by frame across each changed shot. Preflight: 0 blocks. I didn't re-review the rest of the story.

## Checks
- **S39 (47.53 to 49.20 s):** fixed. Lou reaches the door and stops, then turns to the camera over about 8 frames (48.83 to 49.07 s), with no one-frame flip. The blanket swings across her front during the turn, and nothing clips.
- **S42 (51.43 to 52.87 s):** fixed. The legs step steadily toward the camera on every frame with no spin.
- **S45 (54.73 to 55.33 s):** fixed. The shoulder twist holds still with no yaw pop through to the cut at 55.33 s.
- **S32 (38.83 to 39.63 s):** fixed. Lou's change of place lands on the cut at 39.63 s, so no slide shows inside the shot.
- **S35 (42.97 to 44.33 s):** fixed. It's one smooth walk off the porch, with no stall or pop.
- **S43, S50 and S60 (staging_ok):** they read apart. S43 shows one body only (legs, then the face). In S50 and S60 the blue shirt and the yellow coat are separate at phone size, with two clear heads. Lou's hand on my shoulder in S50 is the blanket action we want.

## Should-fix (not blocking)
1. **S60, about 77.4 to 78.0 s:** at the end of the push-in, the left edge crops the narrator's head to half a face. If it's cheap, start the push-in a touch wider or move it about 0.3 m right.
2. **S60, about 77.3 s:** the narrator's hand crosses in front of Lou's coat for a few frames. The colours keep the two apart, so it's fine to leave.

Scores carry over from r5. No regression is severe.

Verdict: approve
