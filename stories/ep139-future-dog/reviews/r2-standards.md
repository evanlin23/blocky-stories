# ep139-future-dog: standards r2 (2026-11-12)

Verdict: approve

## Round-1 must-fixes
1. Reveal at the end: in. The ending runs L43, L46, L48, L44, L49. Only L49 (S49, 2.1 s) follows the reveal.
2. L38 trigger: in. L37 "SEVEN nights, he'd texted me and deleted it." sets up the ACHOO.
3. Filler: in. L15, L20 and L36 are cut, and L05 is "Mine rang at SEVEN." (L06, L39, L45 and L47 were cut too.)
4. Opening tag: in. `"opening": "cost"` matches line 1.
5. cover_s: in. 2.7 s shows Noodle, tag "1", "for my DOG."
6. hold: updated. Remove it now that both reviews approve.

## Regressions
None severe. Fiction, kids, IP and originality still pass. Title and pin are clean under hard rule 8.

Flash: picture-flash PASS. General max is 1 flash/s, general_3f max is 3 (bar 3), red 0. The general_3f "7 changes/s" at 42.9 to 45.1 s comes from ordinary cuts (S29b, S30a, S30b, S31a: patio to the bright street) and lasts 2.2 s, under the 4 s extended rule. I checked those frames in picture-flash.mp4 and found no strobe, so this is not a flash problem. It will add the "Flashing lights and fast cuts" description line, which is acceptable.

## Should-fix (not blocking)
- The preview mp4 is garbled at 42.6 to 46 s. It jumps between S28b, S29b, S30b and S31a every frame, and the clock flips 7:38, 7:39, 7:40. The cause is stale frames: frames-preview/ holds 969 PNGs from the earlier, longer timeline. picture-flash.mp4 is clean and the final draws fresh on Actions. Clear frames-preview before the next preview.
- Two captions are up for under 0.2 s ("it's YOU" in L01, "he lay" in L26). Merge each into its neighbour chunk.

## Queue
Keep ep139 at least 3 slots from ep124 and ep152 (same series). Don't put it next to ep146 or ep128 (phone), or next to ep110 (sneeze gag).
