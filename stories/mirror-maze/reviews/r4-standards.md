Verdict: revise

Standards, round 4 (the redo's round 1). Preview checked: out/work/mirror-maze/ep15-mirror-maze-preview.mp4 (quarter-res, every 4th drawing), its contact sheet, stills/sheet.png and the creature test.

Passes: fiction (no signs or set text, no real places), kids and mature themes (all adults, nobody hurt, no death words; the dark one has a drawn face, so it isn't batch 1's blank-faced grey), IP (our faces and outfits, no game name), packaging (made_for_kids false, "It's made up.", no banned words, rule-stating pin), writing (no dashes, semicolons or slogans). The voice.py HOMOPHONES entries are used only by `same_spoken` in the `asr` word check. They never touch synth, timing or picture, and render.yml only triggers on `stories/*/**`, so no other story's film changes. Preflight flash: PASS. General is at 2 a second at 59.17 s, which is the bar, and that reading comes from fix 1.

Must-fix:
1. **S36 (L32 "ANYWAY", 58.2 to 58.53 s):** the frame goes to a flat, full-screen pale lilac for about 0.3 s (mean luma 56, then 166, then 80 at S37). It's an empty shot and a light jump up and back down across the whole frame. Tasha's `raw("tasha", "L33>", pos=[-5.7, ...])` move appears to drag the `follow="tasha"` camera into a pane or her coat before the cut. Key the move after S37's first frame, or drop `follow` on S36. Re-render, then check that no S36 frame averages above about 100 luma.
2. **package.json title:** "Your Reflection STAYS When You Walk Away" has the same shape as ep48's "In this town, your shadow stays where you were happiest". ep48 also opens on a crowd of left-behind shadows, with a narrator whose own never leaves. RULES (Titles) bans reusing an earlier title's shape. Change it to, say, "In This Town Mirrors KEEP Your Reflection".

Nice-to-have:
- Originality: the twist (the narrator is the leftover) and the ending stand apart from ep48. ep50-beach-huts, which isn't on disk yet, should change its "I have no reflection" exception so the channel doesn't get two narrators missing from glass. Space this story away from ep48 and ep50 in the upload order.
- Remove `hold` once standards and critic both approve.
- S16 to S18 (26 to 31 s): the panes carried past hit 5 changes a second on the 3-frame reading. Slow the carry a little to leave margin for the final.
