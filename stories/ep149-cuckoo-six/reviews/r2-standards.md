# ep149-cuckoo-six: standards r2 (2026-11-12)

Verdict: approve

Check only (RULES audit decision 8). Preview 24.8 s, 27 shots. Frames pulled at phone size for S02, S02b, S05, S11a, S11b, S11c and the end of the hold.

## Round-1 must-fixes
1. **Title:** in. package.json and story.json both say "This Cuckoo Clock Counts PEOPLE 🕰️". It no longer echoes ep134's shape or ep116's opening word.
2. **Pin:** in. It asks one question, about the twist (sneakers or frosting).
3. **P01 caption:** replaced with "Which one: A–D?", one chunk for the whole 4.0 s hold. It reads at phone size and passes the 3-word caption check. Accepted.
4. **cover_s 8.5:** in. It lands inside S05 (8.33 to 8.77 s): Grandpa, "SIX.", counter 5→6.
5. **S11a to S11c:** in. All four letters stay in frame for the whole hold. In S11c, A sits at the left edge but is fully readable. The red toes under the curtain show at phone size.
6. **S02 tag:** in. The counter tag is whole in S02 and S02b.

## Regressions
None. Flash preflight: PASS, 0 blocks. The 4/s and 9 changes/s warnings come from the S04 run of 0.25 s cuts. Nothing is red and the stretch isn't sustained, so the Actions measure decides. Sound: 3.6 events per 10 s.

## Should-fix (not blocking)
- The "–" in "A–D" is an en dash. Make sure the caption font draws it (it does in the preview).

## Queue
`count` / `hidden-guest`. Keep it 3 or more from ep134 and ep116 (queue lines 19 and 20) and from ep140, and never next to ep62.
