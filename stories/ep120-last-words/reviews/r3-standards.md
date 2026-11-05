# ep120-last-words: standards r3 (preview 07:34, 2026-11-05)

Verdict: revise

The r2 fix mostly works. Once the cool `dadfill` is on, Dad keeps his gray hair and light skin in S62 to S66 and S68, as at S61. The thermos dent shows at S27.

Passes:
- **Fiction:** no words in the set. The tag shows glyphs and numerals only.
- **Kids and mature themes:** everyone is an adult and there are no death words. The reworded L12, L42, L48, L53, L69, L70 and L71 are clean, warm and in US English ("apartment", "place").
- **IP:** our own faces. No game name anywhere.
- **Originality:** no change since r2.
- **Flashing:** preflight PASS. General is 1/s and 3f is 3/s. There is one house warning (3f changes 7/s at 51.2 s, the S29 to S30 thermos cuts), so the upload adds "Flashing lights" to the description. Keep an eye on it on Actions.
- **Package:** no change. The opening is `must`, which matches L01.

1. **The fill pops on after each cut: S62 (79.23 s, frames 2377 to 2384), S68 (88.33 s, frames 2650 to 2654), S69 (89.83 s, frames 2695 to 2699).** Each shot opens with Dad dark brown with near-black hair, the r2 problem, then brightens over 0.3 s. In `generator/make_story.py`, set `dur=0.0` on the `dadfill` cues at `L46-0.05`, `L52-0.05` (move it to `L52-0.01`) and `L53`, so the first frame of each shot is already lit.
2. **S67 ends on 9 blank cream frames (88.03 to 88.30 s, frames 2641 to 2649, L51 "pulled in DOWNSTAIRS").** The `pulls_in` camera ends at `[NX-2.6, NY+1.1, AZ+1.75]` and backs into geometry behind the window. The frame jumps from a night lot to full cream and back. End the move in front of the glass (for example `[NX-2.6, NY+0.6, AZ+1.9]`) and check that the last 10 frames show the lot.

Nice-to-haves:
- L69 is built as "Now I come over every SUNDAY.", but script.md has "I come over / every SUNDAY now." Make them match. The script's version avoids two "Now" lines in three.

Spacing (no change): never next to ep89, ep28, ep55 or ep47 (all `must`). Keep it at least 3 uploads from ep89, ep99, ep48, ep42, ep55 and ep92. Never right after ep99.
