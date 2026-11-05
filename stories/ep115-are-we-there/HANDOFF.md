# ep115-are-we-there: DROPPED (batch 12)

Two review rounds used (RULES audit decision 3). Round 2 critic said revise with THREE separate fixes, so no single-fix rescue applies.

Last verdicts:
- standards r3: approve (r3-standards.md).
- critic r2: revise, avg 7.1 (hook 8, back-row 8, narrator 9, appeal 9, relationships 8, eerie middle 5, faces 5, captions 6). See reviews/r2-critic.md.

Open must-fixes:
1. Mom from the dash (S26, S29, S41-S44, S46, S49, S53-S55): mouth sits in the caption band (62-68% of height), left head edge crosses the frame. One camera change: pan right, tilt/lower so mouth is above 58% of height.
2. L19: story.json and the voiced wav say "has said four"; lines.json says "four twelve". make_story.py splitter drops leftover spoken words when a chunk has more words than its caption (engine-side generator bug in the story's make_story.py). Rebuild story.json and re-voice L19.
3. Heads cut by the edge: S04, S25, S45 (narrator, left edge), S52 (narrator and Mom), S39 (Jo's hat cut/under the tag).

State: preview built, framing lint 0 findings, measure 0 blocks, check ok. If retried, this is a multi-fix story (not eligible for the decision-7 near-miss retry).
