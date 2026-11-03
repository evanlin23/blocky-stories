# ep37-comet-night, round 5, standards

Verdict: revise

Must-fixes:
1. **Flash (hard rule 7), S02 under L02, 2.77 to 4.07 s:** the preview fails `general_3f_changes_le_6`, with 7 changes at 3.93 s. S02 pushes in on the knot against the dark backdrop with `"step": 4`, so it moves in 4-frame jumps. Each jump adds a slab of Dad's bright white hair cap (the bright share goes from 16% to 23.5% in one jump at 3.97 s), and the cut at 4.07 s lands on the sunny square. The final also draws S02 at step 4, so this isn't only a preview effect. In `generator/make_story.py`, line 149, change S02's last element from `4` to `1`, so the push runs smoothly with no hand shake. Regenerate story.json. The preview always draws at step 4, so check it on the final: render S02 alone at final quality, or let Actions measure it. If it still reads over 6, also end the push higher (end camera z 1.72 to 1.66), so the hair cap stops growing.

Pass:
- **Round 4 fixes:** the captions now read "Gray and hard," (L11), "looked GRAY under" (L24), "Thick and gray," (L49) and "the gray knot" (L62), and L35 reads "AROUND." in the text, the captions and script.md.
- **Package:** the title, description, pin and `made_for_kids: false` are unchanged and still pass. The cover at 79.5 s shows the creature clearly lit, with its eyes and the stars in its chest. `"opening": "cost"` is a harmless tag, and `hold` stays until ship.
- **Hard rules 1 to 8:** the opening is a charcoal knot over Dad, with no lettering, nothing in peril and no game names. The story is still distinct from the others. The text has no dashes or semicolons, and on-screen text is US English.
- **sound.py:** `band` and `peak` are opt-in. Without them `sfx()` returns `_sfx()` unchanged, and 145 tests pass.

Nice-to-have:
- Document `band` and `peak` in docs/engine.md's sfx options.
- L41 "took ages", and script.md's Marker and Cast notes still describe the bride and groom S01, plus "Mum" and "neighbour" in the prose.
