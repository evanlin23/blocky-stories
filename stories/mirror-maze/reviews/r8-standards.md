Verdict: revise

Round 8. Preflight: 0 blocks, flash PASS (general 1 flash, 3 changes; 3-frame 2 flashes, 5 changes, worst at 59.7 s).

Passes:
- **Fiction, kids and IP.** The new S01 shows three adult strangers behind the panes (red cap, orange cap, white hair) under diagonal sheen streaks. There's no set text, no real word and nobody young-looking. The cover at 66.6 s ("looked at HERSELF.", me and Tasha in the pane) is clean.
- **US English.** L02/L03 now say "fry CART'S", "LINE" and "REAL line", the voice matches, and the description says "fry cart". No "queue" or "van" is left on screen or in the voice.
- **Pin.** "Comment PICKLE for the friend who always pays." uses one easy word tied to the story, and no sibling uses it.
- **14 to 17 s.** 1 flash and 2 changes.

Must-fix:
1. **S39 (L33, 59.73 to 61.47 s), flash. Still open.** Setting `bulbs` to 0 didn't steady the light. Face luma reads 194, 177, then 214 at 60.43 (+37), then 200, 214, 203, 216. Whole-frame luma jumps from 100 to 123. Inside the shot, 45% of the frame brightens at 60.40, then 22% darkens at 60.67 and 17% at 61.07. The 3-frame count is now 5 changes, worse than r7's 4, against a house bar of 6. The last final measured double the preview here, so it would likely fail on Actions. The cause is the walk: the guy and Tasha are still walking the carried pane (with me in it) west through S39 (`raw(..., "L33>")`), and the camera follows the guy (`follow="guy"`) past the fair's lights. Fix: end the walk when S39 starts. Add `raw("guy", "L33", pos=[-3.25, GY, BZ])` and `raw("tasha", "L33", pos=[-5.7, 3.4, BZ])` so both hold still through L33, and drop `follow="guy"` from S39. Accept it when face luma stays within ±8 across S39 and 59 to 62 s reads at most 1 flash and 3 changes on both counts.

Nice-to-have:
- The packaging section's pin form is "Comment WORD if...". "Comment PICKLE if your friend always pays." would match it exactly.
- script.md's World and shot table still say "fry van" and "queue", and spell "travelling" the UK way (planning text only).
