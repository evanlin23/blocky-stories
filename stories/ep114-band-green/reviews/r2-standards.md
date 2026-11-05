# ep114-band-green: standards r2 (2026-11-05)

Verdict: revise

r1 fixes, checked against the new preview:
- **L01:** fixed. The voice and captions now say "On our town GREEN, / everyone has to DANCE / to the band. / EVERYONE." (0.25 to 2.9 s). There's no When clause, and `opening: must` matches it.
- **hold:** removed from package.json.
- **S68 / L42 (71.6 to 73.4 s):** fixed. The foreground man lies on his back with his hands behind his head and a `laugh` face, the camera is low and close, and the figures behind him lie on their backs with faces showing. It reads as rest, not collapse.

Fiction: pass. Kids: pass (all adults, nobody hurt). IP: pass. Flashing: preflight PASS, warnings only. The worst stretch is 54.97 to 57 s (L31, L32: quick cuts from the navy bench to the lit shopfronts, 4 flashes in 1 s on the 3f bar). The final may land near the bar there. The cover (47.2 s, the two lights under the brim with "looking at ME.") is good.

## Must-fix
1. **Title.** "Everyone Here Has to DANCE 🎺" opens with the same two words as queued ep42's "Everyone Here HUMS Their Own Note 🎵", and both are music titles with a music emoji. That breaks hard rule 5 ("never reuse an earlier title's shape"). I suggested this title in r1, and that was wrong. Change the title to an opening no other title uses, still one CAPS word with the emoji at the end, for example "Saturday's Band Makes Everyone DANCE 🎺". Update `title` in story.json to match.

## Nice-to-have
- script.md still says "Hold: scripts only" and `cover_s` 46.6. Make both match package.json.

## Opening variety and queue spacing
Batch 11 (ep108 to ep114) has 2 `must` openings in 7 (ep109, ep114), 1 `ban` and no other shape more than once. That passes. Keep ep114 at least 3 uploads away from ep42-barber-chair (music theme, "Everyone Here"), ep54-dance-hall (dancing), ep98-town-whistle and ep109-said-your-name. Never put it next to another `must` (ep28, ep47, ep55, ep89).
