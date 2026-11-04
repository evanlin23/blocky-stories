# ep95-corn-maze: standards, round 2

Verdict: revise

All five round 1 fixes are in. The move, the truck and the seed corn are gone. June stays, and the dawn face is a gift, not a keepsake, so the ending no longer follows mirror-maze. The other "waves back" lines (ep26, ep43, ep45, ep48) are people waving, never a place. L33, L39 and L40 are clean. The title is new and stays clear of every "Nobody..." title. The description has no spoilers and no banned words, `hold` is gone, `cover_s` 53.63 is the middle of S34, and `opening: if` matches L01. Batch 9's openings are fine: `if` is 2 of 9 (ep98 reads as `must`) and `confess` is 3 of 9. Fiction, adults only, no set text, no game IP and US English all pass. The flash reading passes, clipcheck shows 0, and S30a and S33 now read.

1. **S42, 64.3 to 65.6 s (L42 "a STAR"): the star is a pentacle.** It's a crossed five-line pentagram inside a ring, cut from above into a field in a creepy Short with a kid-friendly look. Viewers and YouTube's reviewers will read it as an occult sign (hard rule 3, mature themes). The change goes in `geo.py`. `layout_shapes("star")` becomes `surround([poly(STAR_OUTLINE, 2.0)])` with no `ring(...)`, and `STAR_OUTLINE` traces the outside edge of the star (10 points, alternating the outer tips and the inner corners) so no lines cross inside it. Then redraw S42 and check that June's light still walks the points.

Nice-to-haves:
- `stills/sheet.png` and some `post-*.png` files are stale (old lines "with SEED corn", "in some other TOWN"). Redraw them before the final.
- L16 "She's my best FRIEND" repeats mirror-maze's "best friend" in a maze. "She's my only FRIEND" fits L36 better.
- The 3-frame flash reading has a 1.97 s run at 2 per second from 3.9 s (the montage cuts). It's under the limit, but watch it on Actions.
