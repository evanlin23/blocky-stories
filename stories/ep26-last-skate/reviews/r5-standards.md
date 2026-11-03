# ep26-last-skate: standards, round 5

Verdict: revise

The S09, S16, S17 and S40 moves cleared the earlier faults. S09 cuts down once and then ramps smoothly (14.2 to 16.6 s), and S40 holds steady at luma 88 to 104. Fiction, rules 2 and 3, IP, originality and package still pass. Preview flash: PASS (2 flashes and 5 changes a second, worst at 27.5 s and 27.9 s, a 1.57 s run at 2 a second from 27.77 s).

## Must-fix
1. **Flash, S24 (L22, 41.2 to 43.6 s). The round 4 fault is still there.** Moving the camera to [-3.0, -5.4] didn't help, because the lens still looks north across the loop's south edge. Couple c2 (orbit("L16", 23.0, 5.3, ...)) is at theta 3.5 to 4.5 here, and it crosses the line of sight about 2.5 m out. The green skater fills the left half (42.2 to 42.6 s), then the purple one fills the frame (42.7 to 43.0 s). Luma goes 54, 72, 48, 55. Fix it one of two ways. Either hide c2a and c2b from L22 to L23, or re-phase c2 so that it stays at x > 0 from 41.0 to 43.8 s (th0 about 0.9). Then re-run the flash pre-check on S18 to S25.
2. **Flash, S16 to S17 (L14 to L15, 27.3 to 28.4 s).** This is now the film's worst moment, and it sits right at the 5-changes cap. The new walk("nan", "L14.4", ...) slides Nan's full-height foreground body out of frame at 27.4 to 27.7 s. Then S17 opens at 28.07 s with her large at the left edge, and she crosses out again. Start her glide at L15, not L14.4, so that she stays put through S16. In S17, start her at least 1.5 m in front of the camera so that she doesn't wipe the lens.

## Nice-to-have
- The round 4 notes still stand: the S66 booth ramp, the near-black Skater against L22/L37 "cherry and cream", and the lore.md ep26 row.
