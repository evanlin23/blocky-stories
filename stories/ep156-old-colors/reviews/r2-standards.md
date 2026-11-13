# ep156-old-colors: standards, round 2 (built preview, 2026-11-13)

This round checks the fixes for the round-1 built review (r1-standards.md). It replaces the script-stage r2. Preview mp4 05:03 UTC, drawn after the story.json edit (04:42). Preflight: 0 blocks, flash PASS, 44.83 s.

## Round-1 must-fixes
1. **Music box:** in. The L18 section is now `piano`, `pad` and `bubble`, and no section uses `musicbox`. Re-mixed at 05:02.
2. **cover_s:** in. At 29.95 s the cover is S12a: the calendar shows "31", the yellow pillow stripe is big, and Leo's face is clear (checked at 300 px).
3. **"It's YOU" caption:** NOT in. L17 is still three chunks. "It's YOU who" is up from 42.314 to 42.606 s, which is **0.29 s**. That's better than 0.19 s, but the key word of the reveal still flickers at phone speed. Exact change in story.json L17: `"chunks": [["Leo.", "Leo."], ["It's YOU who misses it.", "It's you who misses it."]]`. That holds about 1.05 s. Then rebuild the timeline and preview.
4. **hold:** in. The field is gone from package.json.

No regression. The S17b reveal still reads: blue face and hands, the yellow stripe and the plum hoodie, with the calendar on "41".

## Title
"Miss Your Old House, Turn Its COLORS 🏠" passes hard rule 5. No other title starts with "Miss". It shares the words "Old House" with ep143 ("My Old House Key Went WARM"), but the openings, rule and price are different. ep55's "Turns You Green" is a different kind of rule (moss from waiting) with a different title opening. Hard rule 8 is clean.

## Should-fix (not blocking)
1. The 44.83 s runtime is just under the script's 45 to 75 s length arm. Fix 3 adds nothing, so check it with the critic.

## Queue spacing
ep156 and ep143 share the `if` opening, the warm lane and an old house, so put at least 3 slots between them. Keep at least 2 slots from ep123 and ep117 (a mark on the body) and from ep114. Never put it next to ep110, ep124, ep141 or another `if`. Coming right after ep155 (`must`) is fine.

Verdict: revise
