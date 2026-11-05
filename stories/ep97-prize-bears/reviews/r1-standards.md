# ep97-prize-bears: standards r1 (quarter-res preview)

Verdict: revise

Passes: fiction (only `CAL`, scores and numerals in the set, no cropped word), kids and themes (all adults, nobody hurt, nothing aimed at kids), IP (our own bear, crown, duck and meter), opening (`confess` matches L01, batch 9b has one each of confess, if, cost and count), package ("It's made up.", no banned words, dashes or semicolons, a one-word pin). Originality passes with condition 4.

## Must-fix
1. **Flash, S05 to S07 (10.2 to 14.1 s), build.** The general_3f extended run is 3.93 s against the 4.0 s house bar, and the final is measured at full rate. Bring S05b (rim close) up to S05a's brightness, halve the jackpot beacon's emission (`jackpot` 3.0, `jpbeam` 2.5, set.py about line 494) and slow its spin, and keep the sunlit door out of S06's background. Get the run under 3 s in preflight.
2. **Flash, closet (38 to 45 s), build.** The worst 3f second (9 flashes, 44.8 s) is the swinging bulb over the bears (S25), after the door's light slice at 38.1 s. Halve the swing (set.py line 938) or hold the bulb still in S24 to S26.
3. **Contradicting plant, S08 and S29, build.** The bear foot in Tess's back window (set.py line 620) says she takes the bears home, which L32 denies. Remove it.
4. **Queue, at merge.** Another forgetting ritual, so keep it at least 3 slots from floor-thirteen.

## Nice-to-have
- "MEMORIES, Not Coins" isn't the banned reveal cadence. If another title uses a contrast, switch to the backup "This Arcade Charges In MEMORIES 🕹️".
