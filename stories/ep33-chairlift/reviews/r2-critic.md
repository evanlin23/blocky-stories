# ep33-chairlift r2 critic

Verdict: revise

## Hits' shape (old shape, plus new 8 and 9)
- Old shape: rule at 0.25 s yes. Nights Mon to Thu yes. Rule broken Fri yes. Scare 89.6 s yes. Twist planted at L06 and L10 yes. Warm turn shown yes. Last line loops yes.
- 8, phone-readable first 2 s: yes, just. Bo's face is 28% of the width, but the blue is dim.
- 9, cuts: yes. 85 shots, 1.64 s average.
- Title is a statement: yes. Pin asks viewers about themselves: yes.

## Scores
- **Hook 6:** a clear dare on a lit face, but nothing strange until 30 s.
- **Scare 7:** the hit, the S56 cut and L53 all land at 89.63 to 89.65. The voice-only stretch runs 2.27 s (87.38 to 89.65), with 1.25 s of dead air (-58 dB).
- **Creature 6:** the dot eyes and slot mouth on a grey cube are blank and uncanny now. In mid shots it still reads as a box.
- **Twist 8:** forty years of forfeits turns L01 over. "all WEEK" fixes the r1 slip.
- **Lore 8:** the two strokes read clearly in S16 and are never mentioned.
- **Warm turn 8:** shown. The card ends up on Mr Halvor.
- **Shots 8:** varied and quick.
- **Faces 7:** both faces in S56 are whole, about 30% wide and above the captions. In S83 Mr Halvor's head is blown white.
- **Sound 6:** the closing clack is audible at about -11 dB, 139.2 s. The silence is too long.
- **Captions 8:** on the chunk times.

## Panel
- **Creepy fan:** stays through the reveal. "the back of its head is LOOKING at me 💀"
- **ep11 to ep13 regular:** stays. "two orange marks, two seats. it's been riding with every loser"
- **Casual scroller:** swipes at 10 to 16 s (rope, old couple, boots), before the creature appears at 30 s.
- **Top comment:** "so the cube guy makes sure nobody wins the bet??"
- **Slips:** none in the count. Plant 1 (S06, 9.8 s) is hidden: my head covers the Halvors, so their missing cords never show.

## Must-fix
1. **P01 / music_drops:** move P01 to after L52 and make it 0.5 s. Set the drop to `"from": "L52>", "to": "L53"`, so there's about 0.75 s of silence before the hit.
2. **Closing frame (S84 to S85, 136.7 to 139.5 s):** 36% of pixels are at luma 250 or above, not 7%. Lower the `warm2` sky and sun exposure until clipping is under 2%. Fix S83 (L79, 134.6 s) too, so Mr Halvor's face and the card read.
3. **S06 (L06, 9.1 to 10.8 s):** move the camera a step left so both Halvors' chests show beside me, without cords.
