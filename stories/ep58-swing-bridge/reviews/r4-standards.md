# ep58-swing-bridge, round 4 (revival), standards

Verdict: revise

Passes:
- **Fiction:** no set text, signs or real places in the frames I checked from 0 to 141 s, S91 included.
- **Kids and mature themes:** all adults, nobody hurt.
- **IP:** our own faces, and no game name.
- **Opening:** line 1 is a condition, so `"opening": "if"` matches it. L01 ends at 2.07 s. The last upload is mirror-maze (`ban`), and `queue.txt` has no `if`, so the spacing is fine.
- **Package:** polish and flash_safe are on. `cover_s` 101.9 lands on S68 ("MINE."), a lit face with the glow.
- **Flash:** preflight PASS, 0 blocks. The 1-frame max is 1/s, the 3-frame max is 2/s, red is 0, and the house bar passes.

1. **Title (RULES → Titles: "at most one Never title in any 7 uploads").** The last upload, mirror-maze, is titled "Never Walk Away From Your REFLECTION". `upload.py` doesn't enforce this rule, and ep58 can land inside that window. Change `title` in package.json, and story.json `title` to match, to a shape that isn't a ban. One option: `"Something on This Bridge Has DARK Hands 🌉"`. Seven words, one CAPS word, emoji last, no spoiler.

Notes (not blocking):
- **Queue spacing:** ep51-fossil-hall shares this skeleton (a glow marker, a narrator with no glow, an older male relative, a marker that turns out to be about me). Keep the two at least 7 uploads apart, and note it in `queue.txt`.
- **Hold:** remove `hold` only after the proof qa passes.
- **Final flash, 100.5 to 104 s:** S68 to S69's ramp, then a near-black slab over the top of the frame above two bright hands. The preview's 3-frame meter shows a 1.83 s run at 2/s. That's indicative only, so watch this stretch in the Actions measurement.
