# ep115-are-we-there: standards r3 (preview 06:31, preflight 0 blocks, 2026-11-05)

Verdict: approve

Re-checked from r2:
- **Score (hard rule 6):** landed. No `musicbox` left. Sections `0`, `L12` and `L32` use `piano` + `pulse` + `pad`, `L31.1` uses `piano` + `pad`, and `L20`/`L27` use `drone` + `pad`. That separates the score from ep102.
- **Cover:** landed. `cover_s` 41.1 is frame 1233, inside S38 (1219 to 1246). It shows my `uneasy` face full in frame with the tag at 40 and nothing cropped.
- **Hold:** removed from `package.json`.

Still passing:
- fiction (numerals only, blank signs)
- kids and mature themes (all adults, nobody in peril)
- IP
- originality against ep102, ep94 and ep121
- opening: `if` matches L01, 1 of 7 in the batch
- description and pin
- hard rule 8
- flashing: preflight `flash: PASS`, ep10 bar passes. 3f peaks at 3/s at 3.77 s, which is right at the limit. Watch the final there (the L03 cuts), but it's not a block.
- the new L16 ("Pine AGAIN. / Then the HONK.") and L21 ("That plow guy / WAVES again.") are fine.

No must-fixes.

Nice-to-have (critic's r1 must-fix 8, which didn't land):
- **L19:** `lines.json` says "has said four twelve", but `story.json` still speaks "has said four". `make_story.py` slices the spoken words by the caption's word count (3 words), so it drops "twelve". Either caption it "has said 4 : 12", or make the splitter keep the spoken words left over when a chunk isn't split (k = 1). The same bug would cut any spoken chunk that has more words than its caption.

## Queue spacing
- ep115 isn't in `queue.txt` yet. Don't add it straight after ep99-statue-years, the current last slot: both titles are "The X That ...". Its `if` shape is fine after ep99's `cost`.
- Keep it at least 4 slots from ep102-aunt-peaches (a road that brings you back, with Mom at the center) and from ep94-today-again (a loop engine).
- Keep it away from batch-mate ep119-quiet-car (a vehicle, keeping quiet).
- `if` can't sit next to ep92-blackout-ben or ep98-town-whistle.
