Verdict: approve

Round 8 (new L01/L02, L33, the dial, new title). Preview 66.97 s, 44 shots.

**r7 fixes:** 1 L20 "comes AROUND": done. 2 L24 "swings AROUND": done. 3 L03 display "Mr. PELL": done.

**Passes:**
- Fiction: L01 "An HOUR on the top BENCH costs two WEEKS down HERE." and L02 "She's been up THERE since TUESDAY." claim nothing real. The rule-meter dial is gold and blue halves, a cream rim and a red hand with a hub. It has no letters, numerals or glyphs in any frame (0 to 66.5 s).
- Dial build: the back, faces, rim, hand and hub sit at separate depths (y -0.015, -0.02 to -0.04, -0.055 to -0.085, -0.095 to -0.125). Nothing is coplanar, and no z-fighting shows in the preview or the r8d stills.
- Kids and mature themes: everyone is an adult. L33 "So NOW I STAY up THERE, and SIT beside her," is warm and safe. `made_for_kids` is false.
- IP: no game name anywhere. The dial is our own design.
- Title: "An Hour Up Here Costs Two WEEKS 🚡" has 6 words, one in caps, an emoji at the end and 34 characters. It's a statement and doesn't spoil the twist. No other title starts with "An" or uses the "X costs Y" shape (ep45 is "A Clock Counts Down..."). US English is clean, and L35's "ROUND and ROUND" is fine.
- Package: the description and pin pass hard rule 8. `"opening": "cost"` lints clean.
- Shared code: `still` defaults to false (`_switch(..., False)`), so idle motion is unchanged for every other story. `ramp: 0` and `dur: 0` exist only in this story's set.py, and the one `ramp: 0` cue is at t=0, so no light switches mid-film. voice.py's `"around": "round"` only loosens the speech match. pytest: 145 passed.
- Flashing: PASS. 1 flash and 3 changes a second (1-frame), 3 and 6 (3-frame, at the bar, 12.83 s, a dark-to-dark cut), red 0. Preview only.

**Nice-to-haves:**
1. Loop seam (66.7 s to 0 s): the 0.2 s fade to near black, then the bright blue S01, is the biggest risk on Actions. Consider ending on S44's light, without the dark fade.
2. L33: "up THERE" clashes with the title's "Up Here" and L36's "down THERE". "up HERE" fits.
3. script.md "The rule" still quotes the old "Don't sit..." L01. Update it.
4. The `hold` string has a semicolon. It's internal and removed at ship.
