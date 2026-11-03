# ep30-top-rope, round 6 standards (redo, second review)

Verdict: approve

Checked: the changes since r5 (S14 cut, S10b, S11, S43 and S48b dropped, three 0.3 s dissolves at L13, L14 and L50, and the text edits to L12 and L44, where "white as CHALK" became "breathing FAST"), `python -m blocky preflight` (0 blocks), `python -m blocky flash --file` on the preview, the contact sheet, the stills sheet, preview frames at 19.2 to 23.2 s, 42.9 to 44.9 s and 80.5 to 92 s, and the opt-in `dissolve` in `blocky/post.py`.

- **Flash:** passes. On the preview's 3-frame reading the max is 4 changes a second, at 43.63 s (the S27 to S28 cut, a normal room cut with no bright light) against a cap of 6. The longest extended run is 0.03 s, red is 0, and bright cuts peak at 1 a second. S13 now runs 1.77 s and S14b 1.5 s, and both cuts fade in over 0.3 s, so the r5 hot spot is gone.
- **Dissolve (post.py):** the blend happens in `finish()` after the shards are assembled, so the frame before is always there. It blends linearly over 9 final frames, which only softens a light change and can never add one. It's opt-in, so no other story's film changes.
- **Fiction, kids, IP, originality, hard rule 8:** unchanged from r5. All pass, and the new wording is clean.

## Must-fix

None.

## Notes (not blocking)

- `hold` is still in package.json. The orchestrator removes it at ship, now that both reviews approve.
- S14b to S15 (22.83 s) is a hard cut from the pale anchor plate to near-black. It measures fine, so leave it unless the final's reading climbs there.
