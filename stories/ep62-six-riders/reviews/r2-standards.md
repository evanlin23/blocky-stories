# ep62-six-riders, round 2, standards

Verdict: revise

Passes: fiction (no real place, no signs, our own lettering), kids and themes (all adults at full height, the brother is `worried` with no hand on the glass), IP (no game name or copied items), package (the title "The Elevator Mirror Shows FIVE 🛗" has one caps word with the emoji last, the description says "It's made up.", no banned words or dashes, `made_for_kids` false).

r1 fixes:
- **Originality: fixed.** It's now four riders and five faces, and "Riders" is out of the title. The idea is a puzzle in an office elevator mirror with a swap. That's clearly different from back-row (driver's count on a night bus), mirror-maze and floor-thirteen. No other title opens with "The Elevator".
- **Engine: fixed.** `"i"` and `"e"` are gone from `HOMOPHONES` in `blocky/voice.py`. Only `"c"` and `"d"` remain, and they're ASR-only.
- **C tag at S20: fixed.** It's upright until S22.
- **Flash: not fixed.** S19 is now a bright wall with a small display, and the black strip is gone. The 3-frame reading is still 3 flashes and 6 changes, now at 23.87 s, which is exactly on the house bar again. My frame check: the S18 to S19 cut at 24.17 s swaps about 45% of the frame up and 25% down. The S19 to S20 cut at 24.77 s swaps about 38% up and 39% down. The two cuts are 0.6 s apart, inside one 1 s window.

## Must-fix
1. **P02 / S19 (24.17 to 24.77 s): get the two cuts out of one 1 s window.** Lengthen P02 from 0.6 s to 1.1 s and hold S19 on the "1" with the ding. That puts the S18 to S19 and S19 to S20 cuts more than 1 s apart. Another way: make S20 a 0.3 s dissolve in from S19. Re-run `flash` until the 3-frame reading is at most 2 flashes and 5 changes, as asked in r1.
