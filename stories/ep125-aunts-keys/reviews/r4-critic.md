# ep125-aunts-keys, round 4 critic (render-correctness check)

Scope: this is a check of the final fix only. I looked at the two changed shots (S42 at 51.43 to 52.87 s, and the L36 room shot S47 at 56.63 to 56.93 s) frame by frame in the preview, which draws every frame here (step 1), plus the generator diff (REV 15). Preflight: 0 blocks, flash PASS. I left the fountain, the lock glyph and the 76.5 s tag alone.

## 1. S42, "her front STEPS" (51.70 to 52.22 s)
Fixed. The legs now come toward the camera a little on every frame from 51.70 to 52.23 s. The biggest change between two frames is the right leg swinging forward at 51.93 to 51.97 s, and that reads as a step, not a jump. I see no slide or pop. The framing ends the same as before, with the legs filling the frame.

## 2. S47, "Fast ASLEEP." (caption 56.00 to 56.88 s)
- The eyes are closed on every frame while ASLEEP is on screen. Fixed.
- No open-eyes moment ever reaches the screen. The `wide` key lands at 56.918 s, but S47 cuts at 56.933 s, and the frames up to 56.900 all show the eyes still shut. So the room shot is now 0.3 s of me in my room with my eyes shut. The script wants "my face (awake, in my room), stunned" here. Shut eyes in my own room can read as "I'm asleep at home", and that fights the reveal and "I watched myself" right after it. It's a small beat, but the fix is cheap.

## 3. Anything worse
Faces and framing look fine, with no pops. The only regression is the lost awake face in item 2.

## Must-fix
1. **S47 / L36 to L37 (make_story.py lines 446 to 453):** start the room shot at `L37` with `expr="wide"` from its first frame, and drop the `L36+0.88` key. Move the HIDE, the TP and the handle shot that are now at `L37` to `L37.1` (57.475 s, the start of "try her HANDLE"). The reveal S46 then holds 55.33 to 56.93 s under "Fast ASLEEP." with the eyes shut, as the script asks (held 1.6 s). The awake face plays over "I watched myself" for about 0.55 s, and the hand lands on HANDLE.

Verdict: revise
