# ep28-lamp-room: standards, round 2

Verdict: revise

Pass on fiction (no names, no set text, the bolt-plate strokes aren't letters), kids and mature themes (all adults, nobody hurt), IP (own faces, no game names), originality (`check` clean, the L69 fix landed, the batch-1 list is clear) and rule 8 in the lines. Mix is -14.2 LUFS and -1.6 dBTP.

Flashing (preview, indicative): 2 flashes a second at 1:33.9, with no red. That is the house bar exactly, so there's no margin. The peak is the L54 run, S62 to S64 (1:33.5 to 1:35.4). S63 and S64 each open on bare lit wall (mean luma about 120) and fall to about 65 within 0.4 s as I run in. That's two up-and-down swings in under 1 s. The final draws every frame at full res, so it can tip to 3.

Must-fixes
1. **L54, S63 and S64 (1:33.9 to 1:35.4), flashing.** Have me already in frame on each shot's first frame (start the run pose about 0.4 s earlier). In `set.py` `MODES["run"]`, lower `shaft` from 3.0 to 1.8 so the bare wall is no brighter than S62. Re-run preflight. It should read 1 flash a second, and no run shot should swing more than about 25 luma levels.
2. **Title (`package.json` and `story.json`).** "Every night in the lighthouse, her text asked..." copies the "Every X, ..." shape of ep23, ep26, ep27 and ep34, and RULES bans reusing an earlier title's shape. Use "Who was on the lighthouse stairs every night?" in both files.

Nice-to-haves
- S80 (L69, about 2:02): the Upward's head overlaps my sleeping body from above, so it reads as touching. Put a clear step between us.
- L68 caption "ASLEEP," but the voice says "Fast asleep,". Match them.
- Pin: "Why was there sand on my socks every morning?"
