# ep115-are-we-there: critic r2 (preview, quarter-res; preflight 0 blocks, flash PASS)

Verdict: revise

**Hits:** 1 rule 0.0 s yes. 2 tag 0.0 s yes. 3 montage 3 to 8 s yes. 4 exception 5.1 s yes. 5 Mom and Jo 12 to 15 s yes. 6 ask on purpose 64.6 s yes. 7 plants 19 s, 33 s, echo 65 s yes. 8 phone-readable yes. 9 9.2 cuts/10 s yes.

**r1 fixes:** 2 to 7 (plow blade and wave), 8 for L10, 10, 11 and 12 landed, plus the cover at 41.1 and no music box. Not landed: fix 1 (only the top of Mom's head is fixed), fix 6 for the three-shots, and fix 8 for L19.

**Scores:** hook 8. Back-row 8. Narrator 9. Appeal 9. Relationships 8 (S48 now reads as Jo). Feeling 7. Big idea 7. Eerie middle 5 (the squall is a few flakes on white). Twist and loop 7. Lore 7. Warm turn 7. Variety 7. Faces 5. Sound 7 (clean 0.4 s drop at 37.6 s, closing tune audible, nothing hissy). Captions 6. Average 7.1.
**Reset:** all pass (66 s short arm, bright, meter in every shot, loop, title, pin).

**Panel:** The creepy fan swipes at 39 s because the squall reads as a sunny road: "mom said speedrun 50 laps". The repeat viewer stays: "three scratches on the handle again 👀". The casual scroller swipes at 47 s, because the caption covers Mom's mouth on the reveal and they never see her say it: "wait who asked??" **Top comment:** "Mom packed for FIFTY laps 💀". **Slip:** L19 still voices "four" under a "4:12" caption and phone.

## Must-fix (three fixes, not one)
1. **Mom from the dash: S43 (L26, the reveal), with S41, S42, S44, S46 (L24, L25, L27, L28), S26 (L15), S29 (L17), S49 (L30) and S53 to S55 (L33, L34).** Her mouth sits in the caption band (about 62 to 68% of the height), and the left side of her head crosses the frame edge. Pan right so her whole head sits centre-right, and tilt or lower the camera so her mouth is above 58% of the height. That's one camera change applied to all 11 shots.
2. **L19:** `story.json` still has "has said four" and the wav says "four". `lines.json` has "four twelve". Rebuild story.json and re-voice L19.
3. **Heads cut by the edge:** in S04 (L02), S25 (L14) and S45 (L28) my head is cut by the left edge, and in S52 (L32) both my head and Mom's are cut. Pull back or recentre so every head is fully in frame. In S39 (L22), Jo's hat is cut at the top and sits under the tag: lower the camera so her whole head is clear of the tag.
