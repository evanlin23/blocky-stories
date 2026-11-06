# ep124-future-call: critic, build round 2 (filed r3)

Verdict: revise

Check round only. Preflight: 0 blocks, flash PASS, no pace or clip rows. Batch 13 holds: nothing blinks, two faces at most, no profile two-shot, the phone stays on the wall.

## The r2 must-fixes
1. **Breath: not fixed.** The wind is gone (no amb stem; breath is 21 dB down above 4 kHz, so no hiss). But I rebuilt the breath stem and it can't be heard. All ten breaths sit under spoken words (L12, the "Nothing." chunks, "the breathing / SHOOK", "went SOFT", "somebody laughed WITH"). They play 20 to 23 dB under the voice and about 13 dB under the music and bed in their own 70 to 600 Hz band. r2 asked for them in the gaps, and there are no gaps.
2. S10a: whole head, the finger on the button reads. Fixed.
3. S16: head inside the frame. Fixed.
4. S32, S33a: my head is out. Fixed.
5. S04a: the uncle's face is lit and matches his skin. Fixed.
6. S04b: blue water shows inside the green hull. Fixed (faint).
7. S03: red umbrella, edge and pole in frame. Fixed.
8. S25b: the duck is gone. Fixed.

No severe regressions.

## Scores
Hook 8, back-row 8, narrator fit 9, broad appeal 9, relationships 8, feeling 7, big idea 8, eerie grip 5 (the breath beats still can't be heard), twist 8, lore 5, warm turn 8, variety 7, faces 7 (the crops are fixed), sound 6 (the hiss is gone, the breath is silent), captions 8. **Average 7.4.**

## Panel
- Creepy fan: drifts at 25 s. "wait, what breathing?"
- Repeat viewer: stays. "Dad's truck laugh."
- Scroller: stays past 6 s now. "JOKE"
- Top comment: "He called to hear his dad laugh. I'm not okay."
- Slip: L16 "the breathing went quiet" and L35 "laughed WITH him" still have no sound behind them.

## Must-fix
1. **Sound, L12 to L35:** give each breath a clear space.
   - Add 0.45 s pauses after L12, L13>, L14> and L15>, plus one after L22> and one after L35>.
   - Put a breath in each of those pauses, not under words.
   - Add a `music_drops` span from L12 to L15> with `keep: ["breath"]`.
   - Raise the breaths to about -11 dB so they sit 8 to 10 dB under the voice and over the bed.
   - Keep none at L16 or L17, and nothing after the L38 click.
   - Measure it: the breath must be 6 dB or more over the music in 70 to 600 Hz in each pause.

## Should-fix (not blocking)
- S32, S33a (47.5 to 49.5 s): the meter box covers the top of Dad's cap. Lower the camera's aim a little.
- S25b: at 300 px it reads as a grey slab. Put the garage door's frame edge in shot.
