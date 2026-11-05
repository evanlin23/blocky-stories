# ep120-last-words: critic r2 (preview, 2026-11-05)

Verdict: revise

**r1 fixes:** 1–3 in (L12 "at him for", L42, L48, L71, L69/L70 reworded, `asr_forgive` cut; ASR not re-run here, no TTS venv). 4 in (my face in the car, 25–27 s). 5 in (the cab door swings open, 42.4 s). 6 in (50.5 s). 7 in (S85, 115.5 s: both heads whole, tag clear). 8 ok (S89's 731 matches S01 for the loop; my face is in by 0.13 s). 9 in (Dad gray at 79.8–88.8 s). 10 in.

**Hits:** 1 yes 0.2 · 2 yes 0.0 · 3 yes 5.6–15.2 · 4 yes 15.2 · 5 yes 15.7 · 6 yes 95–104 · 7 yes 121 · 8 yes 0.13 · 9 yes (1.38 s average).

**Scores:** hook 8 · back-row 7 · narrator 9 · appeal 9 · relationships 8 · feeling 7 · big idea 7 · eerie 6 · twist 7, lore 6 (strokes on the handle, 43.4 s) · warm 8 · variety 7 · faces 7 · sound 6 (not re-heard) · captions 8. Average 7.4. Reset: 122 s ok, sad reveals 1 in 7, bright, pace ok, title and pin ok. **The meter is not on screen the whole time** (see 1). Polish on. Preflight: 0 blocks, no pace or clip rows.

**Panel:** The creepy fan stays to the end and says "head on the wheel got me." The repeat viewer says "two strokes, Dad and me." The casual scroller may drift at the L40–L49 explainer and says "call your dad." Top comment: "Dogs here hear GOOD boy all day LONG." No count or logic slips.

**Must-fix**
1. S40, S41, S43 (L27 "And on it, a green THERMOS. With a DENT in it.", L29 "It was DAD'S.", 47.4–49.5 s and 51.3–51.7 s): the tag is a camera child 1.0 m out (`set.py` line 982, `dist = 1.0`), so the thermos close-ups bury it. It's half hidden in S40 and fully gone in S41 and S43. Give the tag its own distance of 0.2 m (clip_start is 0.05). Use `td = 0.2; th = td * 12.0 / lens; tw = th * 9 / 16` for `W["tag"].scale` (`0.56 * tw`) and `.location` (`-0.37 * tw, 0.6 * th, -td`), and leave the bezel on `dist`. This keeps the same size and place on screen in every shot.
