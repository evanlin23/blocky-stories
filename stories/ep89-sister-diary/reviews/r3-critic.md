# ep89-sister-diary, round 3 critic: staging-fix render check

This only checks the changed shots and the staging_ok calls (rev 12, preview from 2026-11-07 01:43 UTC). I pulled consecutive 300 px frames from the preview.

## Changed shots
- **S99 (119.3 to 121.0 s), me and Nina merged: fixed.** Nina (-1.9, 0.92) sits clearly behind me (-0.85, 1.28). Her face, hair and purple top stay visible in all five frames and nothing overlaps. Both faces read at phone size. Nothing is worse.
- **S58 (64.2 to 65.8 s), 1.33 m dart: the dart is fixed, but the shot is now worse.** The walk is smooth and nothing slides. The cost is that me stands right in front of the lens for the first 0.45 s (64.18 to 64.6). The frame is a wall of dark blue back with the head cut off by the top edge, and the brightness falls from 0.52 at the end of S57 to 0.18. The old dart cleared the lens within a few frames, so this is new. At phone size it reads as a blank dark frame on "So I went". The 0.24 "fade-up" is only me walking out of the lens, not a grade change.

## staging_ok calls
- S15/me+nina: OK. Both are slivers at the frame edges, and the car keys are the subject. No overlap.
- S82/me+nina: OK. Me is in profile at the left, Nina at the right. The bodies are apart and no arm crosses an arm.
- S91/me+nina: OK. Two heads seen from behind in three-quarter view. They are close, but the hair colours differ (near-black and brown) and no body is inside another.
- S92/me+nina: OK. Same set-up. In the last frame (112.7 s) the heads almost touch but stay apart.

## Must-fix
1. **S58 / L40 (64.2 s): the opening is a dark frame with the head cut off.** In `S("L40", ...)` move me's start from `X(-1.1, -0.85)` to `X(-0.4, -0.7)`. Keep `raw("me", "L40+1.7", pos=[1.0, -0.6])`, which gives a 1.4 m walk over 1.7 s, so no dart. Another fix that works: pull the camera start back to `(-3.6, -2.0, 1.3)`. Either way, me's whole head must be in frame from the first drawing, and that first drawing should not be darker than about 0.3.

Verdict: revise
