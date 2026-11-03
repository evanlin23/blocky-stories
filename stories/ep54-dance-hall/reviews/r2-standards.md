# ep54-dance-hall: standards, round 2

Verdict: revise

Checked the 13:51 preview (quarter-res, every 4th drawing), its contact sheet and frames I pulled from 0.5 to 141 s.

Round 1:
- L64 now reads "A match / can be FAMILY." The cadence is gone from the film.
- Cover 97.9 s lands in S68, the L49 shot ("with HERS."). Ros and the Stilted are lit face to face, and nothing reads as bare skin. S81 and S82 are wider now, and both sleeves show. Fixed.
- Opener: S04 is 0.8 s. The 1-frame reading at 3.6 s is 1 flash and 2 changes, and preflight passes. Fixed.

Fiction, kids, IP and originality still pass, with no overlap with any other story.

## Must-fix
1. **story.json `twist`, and `generator/make_story.py` line 468, which writes it.** This was part of round-1 fix 1. It still ends "a match was never only for love, it is whoever you fit with." `check` and later writers read this field. Change the end to "a match can be family. It's whoever you fit with."

## Nice-to-have
- **Flash at S20 (26.67 to 27.33 s, 0.67 s long).** The 3-frame reading is 3 flashes and 6 changes at 26.43 s. That's at the bar but not over it. Both cuts around S20 brighten one area and darken another, so each counts as 3 changes. The final cuts on the same frames, so it should read the same, but there's no headroom. Starting S20 at L12's start, so it runs 1.0 s or longer, clears it.
- **`shape: "about-me"`.** RULES.md → Packaging doesn't list this field, and nothing reads it. It's harmless, but it does nothing until it's added to RULES.md.
- `stills/` is older than story.json (11:19 against 12:55), and there's no `stills/sheet.png`. Re-run the stills.
