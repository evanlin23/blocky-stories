Verdict: revise

Round 7. Preflight: 0 blocks, flash PASS (2 flashes, 4 changes).

Pass: fiction, kids, IP. The new S01 stranger is an adult, there's no set text, and the rule reads by 2 s. Title: 6 words, one caps word, emoji last, the only "Never" title. The reset allows a warning as the title.

Must-fix:
1. **S39 (L33, 59.53 to 61.27 s), flash.** The light on my face rises and falls inside the shot (face luma 183, 215, 193, 207). 20 to 33% of the frame changes at 60.33, 60.47, 60.60 and 61.13, then the cut down at 61.27. The preview reads 2 flashes and 4 changes here (3-frame). The old final failed this shot at 4 and 8. The likely cause is the carried pane moving me past the bulbs (`L33>`). Start the carry after the cut, or set S39's `bulbs` to 0. Accept it when face luma stays within ±8 and 59 to 62 s reads at most 1 flash and 3 changes.
2. **L02 and L03, US English.** This is a must-fix, not a carry-over: RULES names spoken lines, QUEUE is on screen, and the film is being re-voiced anyway. Change them to "has a LINE / a hundred LONG." and "The REAL line / is TWO." "Fry van" can stay. Change the description's "fry truck" to "fry van" so it matches the film.
3. **Pin.** Moving-day and closing-time also use "Comment X if you would have ...". Change this pin to "Comment PICKLE for the friend who always pays."

Nice-to-have:
- Change story.json's `title` to the new title.
- The cover's caption, "like a WINDOW", doesn't tie back to the title.
- Each loop says "In this town" twice about 5 s apart (L42, then L01).
