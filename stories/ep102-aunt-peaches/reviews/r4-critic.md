# ep102-aunt-peaches, r4 critic (staging-fix render check)

Narrow check of the rev 9 staging fixes only (frame 0, S09, S14, S48, S79). I looked at the fixstills at 270 px and pulled preview frames and strips at 0, 8.4 to 9.6, 14.0 to 15.8, 39.8 to 41.0 and 68.5 to 69.9 s. S70 to S72 and S80 were not re-checked.

1. **Frame 0, Clem's peach: pass.** Clem is in the frame, front on, with the peach on his right hand at his side. It no longer floats in front of the window.
2. **S09, carrier walk: pass.** From 8.6 to 9.4 s he stays near the middle of the frame and walks with normal leg swings. No zipping.
3. **S14, b3 and b4: fail.** There's a clear gap between the two boys now, so they read as two people at 14.1 s. But the camera pushes in from y -7.9 to -7.07, and by 15.4 s ("brings them BACK.", the stills at f460) both heads are cut off by the frame edges. Only half of the left boy's face shows, with one eye, and the right boy's head runs off the right edge. That breaks the phone-size rule ("a head is cropped").
4. **S48, my entrance: pass.** From 40.1 to 40.6 s I come in from the right in one even move. No hold and no leg snap.
5. **S79, the hug: pass.** It reads as two separate people. Clem is on the right with her face clear and smiling, arms open. Mom is on the left in profile, reaching in. No arm goes through a head. Clem's left hand comes close to Mom's glasses but stays beside them.

**Regressions:** none in the fixed shots apart from item 3, where the push-in now crops the heads.

**Should-fix (not blocking):** in S79 we see Mom from behind and in profile, so her lashes don't show. With short black cap hair and glasses she can read as a man at phone size. A front-on angle or a longer hair style would help. Her design is the same one approved in earlier rounds, so this doesn't block.

Verdict: revise

## Must-fix
1. **S14 (L06.2, 14.10 to 15.70 s):** take out the push-in. Set the second camera key to the same position as the first, `[100.3, -7.9, 1.7]` (or pull both keys back about 0.4 m in y), so both boys' heads stay whole and inside the frame through 15.7 s. Then redraw f430 and f460 to confirm.
