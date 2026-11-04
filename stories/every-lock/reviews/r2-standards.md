# every-lock: standards, round 2 (2026-11-04)

Verdict: revise

Round 1's fixes hold. S009 (8.2 to 9.0 s) now shows the fridge's rows of locks in a mid-tone, and the cut into S010 is no longer listed in `bright_cuts`. The 9.5 s peak is gone. S100 to S102 keep "65,536" whole and on top. Fiction, kids, IP and package all still pass, and `gate` reports no package block. The new L01 ("ELEVEN SLAMS, and YOUR door has ONE THOUSAND and twenty-four LOCKS.") is a count, so `"opening": "count"` matches it. It uses a different template from ep42's "SIXTY-FOUR people... SIXTY-THREE are humming" (N people, N-1 things), and ep45's L01 is "In this WORLD..." (not a count). Originality passes.

## Must-fix
1. **S046 (L23 second shot, 48.6 to 49.57 s) is broken, and it's now the film's flash peak.** The camera at [39.7, -0.34, 1.58] shows only a flat pale-blue wall (luma about 205). A black void then grows across the frame (frame 1486, luma 48), and the shot cuts hard to the bright hall in S047 (1487 is in `very_different`). Preflight: general_3f 3 flashes a second at 49.4 s, which is at the bar, and 7 changes a second at 49.43 s, which sets off the house warning (old bar 6). The script calls for "Jade and me at the table, both `sheepish`". Re-aim S046 inside the kitchen set at the two of them, with no void and no blank wall, and keep its brightness close to S045 and S047. Re-run `flash` and get general_3f changes of 6 or fewer, with no house warning.

## Nice-to-have
- Keep every-lock at least 2 slots away from ep42-barber-chair in `queue.txt`, because both open with a count.
- Update the opening section of `script.md` to match the new L01 and L72.
