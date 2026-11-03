# ep53-car-boot: standards, round 5

Verdict: approve

Preview: quarter-res, every 4th drawing, 136.1 s (built 21:05 UTC, after the last story.json edit). Preflight: flash PASS, 0 blocks. The gate's package lint is clean. It is closed only on the round 4 verdicts.

Passes: fiction (no set text, signs or real places), kids and themes (both siblings are adults, and no young figure is in peril), IP, originality, sfx and hard rule 8.

Round 4 items:
1. **L01, pass.** It is now "The SCARIEST coat / never changes COLOR." (voiced, 1.95 s, 6 words). It no longer shares ep34's NEVER-to-"your" template, and ep34 is dropped anyway. L02 "ESPECIALLY / your OWN." still tightens the threat.
2. **L37, pass.** The caption reads "In her SWEATER," in story.json and lines.json, and the voice says "sweater" (69.7 s).
3. **`cover_s` 82.1, pass.** The frame shows the Tilted's face lit, with both eyes and the tipped head, and the caption "something is SITTING." (81.58 to 82.57 s).
4. **S69 to S73, pass on outcome.** S71 was kept and S69's fill is still about 105 luma, so the literal asks weren't done. The reading clears the bar with margin, though. Whole-film 3-frame max is 2 flashes and 4 changes (worst at 6.97 s, outside this span). Mean luma at 100.7 to 109.5 s runs 105, 160, 108, 125, 150. The 105 to 160 to 108 swing at S69 to S71 is the one to watch on the Actions measure.

Package: the title "The Coat That NEVER Changes 🧥" has 5 words, one CAPS word, the emoji at the end and no spoiler. `opening: cost` matches line 1 (opening-variety.md assigns it). Cost is 7 of 30 in flight (23%), under 1 in 3. The pin is "Comment WHITE if...". The description says "It's made up." and has no banned words.

Must-fixes: none.

At ship (RULES → Packaging): remove `hold` from package.json and add the story to `queue.txt`.

Nice-to-haves:
- Queue it at least 7 slots away from mirror-maze, ep47-fitting-room and ep58-swing-bridge (the cap is one "Never" title per 7, and upload.py doesn't check it). Keep it off ep42 and ep54 too (also `cost`), though upload.py does enforce that.
- If S70 or S71 gets drawn again, lift S71 toward 130 luma to soften the swing.
