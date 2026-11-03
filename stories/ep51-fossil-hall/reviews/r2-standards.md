# ep51 standards r2

Verdict: revise

All my round 1 must-fixes are done except one flash issue, which has moved to a new spot:
- `cover_s` 98.67 falls in S073, the Stooped's face lit, with "It doesn't GLOW." The package lints clean, `shape` is `about-me`, `made_for_kids` is false, and the title, description and pin pass rule 8 and Packaging.
- The vest blot is gone. Abe's vest is clean at 34, 104, 116, 118 and 123 s, now that `gl abe` sits in front of the torso.
- ep20 and ep23: L13, L41, L48, L69, L73 and L80 are reworded, S017 has no gap and S101 holds on my knees and seat. `check` reports no problems.
- S062 is now 1.23 s, and its window peaks at 4 changes.
- `look.flash_safe` is true. Every unramped cue (stooped, sun, sky, sheet, stripes, glk, hall at 84.8) lands on a cut. Every on-screen change ramps 0.4 s or more, and the L57 `sface` ramps 1.0 s up and 0.5 s down.
- Fiction, rules 2 to 4: pass. Everyone is an adult, the museum sign is a fern glyph with no words, and the teeth on the face are creepy, not graphic.

## Must-fix

1. **Flashing, S087 to S089 (122.70 to 122.90 s):** the 3-frame reading is exactly at the bar again, with 3 flashes and 6 changes. This is the only window at the bar in the film. The cuts at 122.87 s (wide to a bright close-up of Abe) and 123.63 s (back to the wide) count 3 changes each, because S088 is only 0.77 s long. Delete S088 and start S089 at `L69`. S087 and S089 use the same camera, so the frame barely changes at 122.87 s, and the `stooped hidden` cue at 122.87 s already lands there. Don't just move S089 to `L70`, because that puts two cuts 0.48 s apart. Re-run `preflight` and confirm `general_3f_max_changes_per_s` is 5 or less.

## Nice-to-have

- S075 (101 to 103 s): my top clips white under the face light. Pull `stooped face` down a little or aim it lower.
