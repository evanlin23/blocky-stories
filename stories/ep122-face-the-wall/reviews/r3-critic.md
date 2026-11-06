# ep122-face-the-wall: critic, build round 2 (r3, check-only)

Verdict: approve

I checked this at 300 px against the preview after the re-voice: 123.1 s, 81 shots. The builder's runs found 0 blocks in preflight, framing, frames, clipcheck and measure. Flash peaks at 3/s and the longest still is 0.27 s.

**Scores:** hook 8; back-row 8; narrator 9; appeal 9; relationships 8; feeling 8; big idea 8; scare 7; creature n/a; twist 8; lore 7; warm turn 8; variety 6; faces 7; sound 8; sync 8. Reset: length 8 (123 s), want 9, sad reveal none, rule close-up yes, meter 7, cuts 8, bright 8, loop 9, title 9, pin 8.

## Round-1 must-fixes
1. S49 (69.8-71.5): fixed. The shot shows the gold floor stripe with the tag in.
2. S12 (18.1-19.9) and S71 (105.9-107.0): fixed. The tag is clear in both.
3. Captions over faces in S28, S40, S57, S68, S73 and S74: fixed. Every face now sits above the caption band.
4. Tag over a head in S65, S72 and S79: fixed.
5. Dad at S55 and S56 (81.2-84.7): fixed. His plaid shoulder is beside Grandma.
6. S45 and S46: fixed. The room is moon blue and the face is still lit.
7. S59 to S61: fixed. They now run 0.54, 0.56 and 0.54 s.
8. Tag glyphs: fixed. The beds and the 1s read.
9. S48: fixed. The quilt shows a small hand.
10. Length: fixed (123.1 s).
11. cover_s 36.3: fixed. It falls inside S24 (35.83-36.77). The `hold` field is not counted, as briefed.

No regressions.

## Should-fix (not blocking)
- S55 and S56: Dad's shoulder is dark and unlit. Put the warm low lamp on it.
- Tag, second row: the door divider touches the first "1", so it reads "1|". Add a pixel of gap.
