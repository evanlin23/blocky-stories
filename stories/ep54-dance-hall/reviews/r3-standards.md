# ep54-dance-hall: standards, round 3 (final)

Verdict: approve

Checked the re-rendered 15:38 preview (quarter-res, every 4th drawing), its contact sheet, `stills/sheet.png` (now present and newer than story.json), the cover frame at 97.9 s and frames I pulled at 26.5 to 28.5 s, 65 to 66 s and 132.9 to 138.3 s. Preflight: 0 blocks, flash PASS.

Round 2:
- **Twist text.** story.json `twist` and `generator/make_story.py` line 470 both end "a match can be family. It's whoever you fit with." Fixed.
- **L34** reads "out of BREATH." on Ros in her coat, unhurt. Fine.
- **Cover 97.9 s** is S68 ("with HERS."). The Stilted's face is three-quarter front, well lit and over 1/5 of the frame, with Ros's closed-eye face beside it. The faces and hat are our own and nothing reads as skin. Pass.
- **Package.** Title is 42 characters and a statement. The description says "It's made up." and has no banned words, dashes or semicolons. The pin is a question about the viewer. `made_for_kids` is false. `shape` is kept, by the lead's call. Pass.

Fiction, kids, IP and originality are unchanged from round 2 and pass.

## Must-fix
None.

## Nice-to-have
- **Flash, S20 to S22 (26.67 to 28.33 s).** S20 is 1.0 s now, but `S21.at` moved to "L13.2+0.35", so S21 (the bright gloved hand by the lamp) shrank to 0.67 s. The 3-frame worst is still 3 flashes and 6 changes, now at 27.43 s. That's at the bar with no headroom, and frame 850 (S21 to S22) is one of the five "very different" cuts. It passes. The final cuts on the same frames, so it should read the same. If the Actions measure fails, set S22 `at` to "L14+0.35". That gives S21 about 1.0 s (and restores the script's 0.8 s palm plant), or you can dim the lamp highlight on the glove in S21.
- Other stretches are fine. The 3-frame 2-per-second run of 1.83 s from 136.73 s (palm glow) and the extended 1.0 s from 132.93 s are both well under 4 s.
