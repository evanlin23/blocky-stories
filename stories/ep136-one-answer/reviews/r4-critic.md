# ep136-one-answer: critic r4 (rescue look, check only)

Verdict: approve

**Scores carried from r3:** hook 8, back-row 7, narrator 9, appeal 9, relationships 8, feeling 7, big idea 7, eerie 7, twist 7, warm 5, variety 7, faces 7, sound 7, captions 8. **Average 7.4.** This fix changes none of them.

## r3 must-fix check
1. **L20 shout hold: in.** In timeline.json the `shout` release for `me` is at `L21` (38.896 s), and S20 ends at 38.90. Ten frames from 37.4 to 39.2 s at 300 px show my mouth wide open on "Don't open" (37.6, 37.8), "the DOOR" (38.0) and "tonight." (38.2 to 38.8). The cut to the three-tile wall (S21, 39.0) lands with the release, so the calm "o" never shows on Eli.

## Regressions (S20, S21, S21c)
None. S20 is uncropped with clean fence framing and no head-prop clip. S21 and S21c (39.0 to 40.1) read cleanly, with "knows your NAME." in gold. Builder measures: longest still 0.27 s, flash passes, preflight 0 blocks, lints clean.

## Should-fix (not blocking, carried)
- script.md → Sound and Notes still say the canyon tail "waits on an engine change". Update them to the `space` filter.
