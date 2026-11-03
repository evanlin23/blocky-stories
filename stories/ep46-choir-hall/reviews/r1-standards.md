# ep46-choir-hall, round 1, standards

Verdict: revise

Fiction pass. Kids and mature themes pass. IP pass. Creepy-lane template pass: the narrator is a long-time local, "since I LEFT" (L23) means the choir, there's no mayor, and nobody is summoned at midnight (rows end "by BEDTIME", the concert is a Saturday hall).

1. **Originality (hard rule 5), L26, L67, story.json `twist`.** The way the story works copies ep23-only-line: a silent narrator in an ensemble, a stand-in voice fills my missing part ("Eleven MOUTHS. / But TWELVE notes", like the Prompter answering for me), "something kept my place", and I perform and it's gone. It also matches ep32-sitter (a place built for N, a Keeper sits in the empty seat, I sit and the seat is empty). Cut L26's "But TWELVE notes / in the CHORD" (show only the chair turning). Rewrite L67 so the turn is the bead arithmetic, not me taking the seat back. For example, L66 "I walk up / the AISLE / to MUM." and L67 "I sing her / last LINE / for HER.". Delete "while I stayed away something kept my place" from `twist`.
2. **Flashing, S13 (16.9 to 19.6 s, L10).** Clipped window: 18% of the frame is over 230, and the face is washed out. It cuts from dark (luma 54) to bright (139) to dark (37) in 2.8 s. Drop the window exposure until nothing clips and the face reads.
3. **Flashing, S01 to S04 (2.3 to 4.1 s).** The 3-frame reading is already at the bar, with 3 flashes and 6 changes at 3.2 s. Lengthen S03 to at least 0.8 s or fold it into S04.
4. **Package.** Remove the `"shape": "stand-in"` key from package.json. It isn't in the RULES.md schema.
