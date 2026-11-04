# ep94-today-again: standards, round 2

Verdict: approve

No must-fixes.

Round-1 items:
1. **S60 light drop: fixed.** I measured mean luma frame by frame across 46 to 52 s at the full 30 fps. S59 holds at 154 to 157, S60 (48.43 to 48.77 s) at 167 to 170, and S61 at 155 to 162. There are no dark frames. A scan of the whole film finds no frame below 50, and every jump over 45 lands on a cut between two lit shots. Preflight passes, with general_3f warnings (5 flashes and 10 changes in a second), so the auto line "Flashing lights and fast cuts from 0:01 to 1:22" stays in the description. The final is measured on Actions.
2. **`hold`:** the producer removes it on approval, as the round-1 must-fix asked. This doesn't block.

Re-check after the fix round (story.json, set.py, make_story.py):
- **Fiction:** the new set text is numerals and glyphs only. That covers the digital "9:02" clock inset, the pink tally strokes, the clipboard ticks with their doodle face, and the surprised-face "ghost" in the cake-case glass. There are no names, signs or routes, and nothing is cropped mid-word.
- **Kids and mature themes:** the cast is still all adults. Okafor on his ladder and the second yard ladder show no fall or peril. The bigger coffee splash cuts to a puddle and shows no injury.
- **IP:** the ghost face is our own cartoon drawing. The new framings show only our own faces and outfits, and no game is named.
- **Originality and opening:** the premise, twist, shape (`rehearsal`) and `count` opening are unchanged, so they pass as in round 1.
- **Package:** unchanged, and it still passes (5-word title, one word in caps, one emoji, no spoiler, "It's made up.", pin "Comment AGAIN").

Nice-to-have: the water streaks are now thin and dimmer (#86bdf0 at 0.55), which lowers the flash risk on the window close-ups. Keep them that way.
