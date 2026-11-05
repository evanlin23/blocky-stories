# ep121-blank-fortune: standards r1 (2026-11-05)

Verdict: revise

Checked the script, package, story.json, the preview's contact sheet, a sheet of all 106 stills, frame strips at 42.8 to 46.1 s and 56.8 to 61.6 s, preflight, and the flash json.

- Fiction: pass. No place or route names. Fortunes are gray bars, handwriting is zigzag scribble, pumps show dials only, shelves are blank boxes, the tag uses glyphs.
- Kids and mature themes: pass. Everyone is an adult, nobody is in peril, and there are no death words. The snowstorm is only a window.
- IP: pass. The faces, caps and phone icon are our own, and no game name appears.
- Originality: pass. Shape `yours-to-write` is new. It differs from ep101 (a wish for yourself), ep96 (double reading), ep89 (paired diaries) and ep109. The lore tally doesn't touch the twist. Opening `whatif` matches L01 and is the batch's only one, so the batch's 7 openings are all different, with 1 `ban`.
- Flashing: preflight PASS, with warnings (3-frame count of 4 flashes and 8 changes, worst at 44.13 s). See fix 1.
- Package: the title is 5 words with one CAPS word and the emoji at the end. The pin is fine, opening and lane are tagged, and lint is clean. See fix 2.

## Must-fix
1. **S47, L26 ("And it comes true", 44.3 to 44.8 s):** the camera starts inside Grandpa's head, so the frame is full of bright skin for about 0.5 s (average brightness 109, then 158, then 85). This causes the flash warning peak and is the head clip the proof blocks on. Start the push from at least 0.4 m in front of his face, and keep the whole head in frame from the shot's first frame.
2. **package.json description:** RULES → Packaging bans "true" in the description. Change "every fortune comes true by Friday" to "every fortune happens by Friday".

## Queue spacing
- No other `whatif` is queued, so there's no clash with the stories next to it.
- Keep it at least 2 slots from ep117-glow-secret. Both are an older couple's decades-long weekly habit with a Friday ritual, and both titles start "My".
- Keep it at least 2 slots from ep116-proud-inch (a quiet grandpa, fifty years) and ep96-friend-card (a written prediction).

## Nice-to-have
- `cover_s` 62.8 lands on "Grandma WOKE up". 16.0 s (the blank slip, my face, "mine was BLANK.") ties back to the title.
- The `hold` text and script.md still say "not built". Update both, and remove the hold once both reviews approve.
- The stills sheet has a fully black frame at 57.5 s. The preview doesn't, so the stills are probably stale. Re-draw them before the proof.
