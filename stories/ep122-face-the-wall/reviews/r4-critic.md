# ep122-face-the-wall: critic, final fix check (r4, changed shots only)

Verdict: approve

Checked every frame of the preview from 102.8 to 104.2 s and from 105.7 to 107.2 s at 300 px wide, plus full-size crops of the tag corner at 103.97, 104.5, 105.0, 105.4, 105.8, 106.0, 106.6 and 107.0 s. I also checked the builder's v2 sheets against `old_frames.png`.

1. **Is the lurch gone?** Yes. The 0.7 m slide back to screen-left is gone. Through the socks shot the legs only move forward, to screen-right, in steady strides. The cut into S70 at 103.97 s is clean. One small thing remains: from frame 3115 to 3116 (103.83 to 103.87 s) the trailing leg goes from mid-stride to standing straight in one frame. The foot moves about a fifth of the frame width forward. It moves the same way as the walk and then holds still for 3 frames before the cut, so at full speed it reads as the last step landing, not as a jump. This doesn't block.
2. **Is the tag clear of the face and readable?** Yes. In S70 (103.97 to 105.83 s) and S71 (105.87 to 107.03 s) the tag sits above and to the left of the hair, with a clear gap on every frame. It touches no hair spike, brow or eye. At 300 px wide it is about 55 to 70 px across, and the bed icons and the "3" and "1" still read. The tag is back at full size in S72 (107.03 s on).
3. **Is anything worse?** No. The walk still reads as crossing the hall. The framing of S69, S70 and S71 is unchanged. The tag is smaller in S70 and S71 than in the shots around them, and it changes size only on cuts, so it doesn't pop within a shot.

Must-fix: none.

Should-fix (not blocking): to smooth the step landing at L57, give the hold key at L57 a short blend of about 3 frames instead of `blend=0.0`. Another way is to end the `L56>` walk about 0.1 s before L57, so the stride closes on its own.
