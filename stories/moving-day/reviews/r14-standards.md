Verdict: approve

# moving-day r14: standards (round 2, check only; decision 8)

Checked: `git diff afef7580 -- stories/moving-day` (S11, S15, S29, S36b, S41, S48, S51, S55 reframed, Mom's L46/L48 yaw, my S15 pose, xfill at L11.1 and L42, `day mum` in the `sun` lights, the L08 oldhouse cue). The preview (20:04 UTC) is newer than story.json and set.py. I pulled 300 px frames for the outgoing frame, start, middle, end and incoming frame of each changed shot, measured mean luma across every cut, and reran `preflight` (0 blocks).

r13 had no must-fixes, so there's nothing to confirm.

1. Fiction: pass. The new framings show only the drawn window-grid photos, the marker faces on the boxes, the plain cupboard door and the quilt. There's no lettering, no signs and nothing cut off mid-word.
2. Kids and mature themes: pass. The whole cast is `adult`. In S41, Mom is asleep in daylight. S36b is still the arms coming down to the quilt, clear of Mom, with nobody hurt. S51 and S48 are laughs, and S55 is a head-down profile.
3. IP: pass. Nothing new is copied and no names appear.
4. Package: pass. `package.json` is unchanged and lints clean, and the `ban` opening still matches L01.
5. Flashing: pass. Preflight shows PASS across 2632 frames: at most 1 flash and 2 changes per second on the 1-frame reading, a 3-frame peak of 3 at 10.7 s, no red and no house warnings. The new S41 light makes a bright cut at 60.27 s (frame 1808, luma 80 to 131), followed by a step down into S42 at 61.2 s (131 to 102). That's dark, then bright, then mid inside 0.93 s. The step down is small, and preflight counts it as only one flash in that second. S29 now opens brighter (149 to 189 at 39.7 s). That's a single step and stays within the rules.

## Must-fix

None.

## Should-fix (not blocking)

None.

## Nice-to-have

- Watch S40 to S42 (60.3 to 61.2 s) in the Actions measurement. If the final counts 2 flashes there, ramp the `day mum` light over 0.3 s instead of cutting it in.
- For the critic: Mom's skin reads pale pink in S11 and S55 and brown in S48 and S51. In S36b's last second (54.5 to 55.0 s), the forearm columns still stand behind the quilt edge.
