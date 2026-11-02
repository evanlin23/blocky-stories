# ep48-crazy-golf: standards, round 1

Verdict: revise

1. Fiction: pass. Made-up names only, and the set shows nothing but hole numbers.
2. Kids and mature themes: pass. Every character is an adult, Dad is taken off-screen, and the L54 lean stops short of him.
3. IP: pass. Every face and outfit is our own, and no game name appears anywhere.
4. Originality: pass. `check` is clean, and the shadow swap is unlike ep45's dial and the empty places in ep30 and ep31.
5. Flashing: the preview passes, but the 3-frame reading sits exactly at the bar (3 flashes and 6 changes at 36.23 s). See fixes 2 and 3.
6. Package: see fix 1.

## Must-fix

1. **package.json `cover_s` 82.4 (S062, L43).** The top of the frame crops off the Wrung One's eyes, so the thumbnail is a headless torso. Change it to `90.3` (L48, with the whole face and both highlights in frame).
2. **S097 (L70, 128.87 s) and S088 (L64.4, 117.7 s).** Both shots open on the previous scene's light and then ramp inside the shot. The Sunday shot goes from luma 27 to 179 in 0.7 s, so it opens at night, and S088 drops from 70 to 37. Set each shot's light state at the cut so the change is one clean cut. The 3-frame extended run starts at 129.87 s.
3. **Shadow material, worst at S026 to S028 (L18 to L19, 35.4 to 37.1 s).** The shadows render near-solid navy, where the script asks for #2f3a4a at about 55% with a 6 cm blur. Restore that so the cuts in this stretch leave the final some headroom.

## Nice-to-have

- S087 (L64): the window clips to pure white and Dad is a black silhouette. Expose for the window so his face reads.
- The pin copies ep45's shape. One option is "Would you have taken the second putter?"
