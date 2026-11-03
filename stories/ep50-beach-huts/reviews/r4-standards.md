# ep50-beach-huts, round 4, standards

Verdict: revise

Checked on the 15:08 preview (quarter-res), story.json and package.json. Fiction, kids, IP: pass, with no text or signs in any frame. `gate` package lint: clean. voice.py: the `fianc`/`fiancee` → `fiance` SPELLINGS rows only relax the Whisper word check, so no film changes, and `pytest` passes (152).

Must-fixes:
1. **Flash, 0.9 s (S01/S02, L01).** At 1.0 to 1.6 s the shot alternates between the mid shot and the window close every 2 to 4 frames, over a navy-and-white striped body cartwheeling (19 changes/s, 3f). Hold one framing for at least 1 s, and calm the stripes (lower contrast, or a slower cartwheel pose).
2. **Red, 40.1 to 46.0 s (L24 to L28).** In the L26/L27 closes, the deckchair's red stripe covers up to 60% of the frame (frames 1345 to 1381), and the phone edge sparkles red. Frame on the cream and teal bands, or drop that red's saturation. The red outlines under the L06 date table (6.3 s) and the blue and magenta speckle on the coat at 59 to 63 s and 98 to 99 s come from the same grade fault: fix that in the grade.
3. **95.3 to 100 s (L59 to L61).** Blue shore, then the near-black laptop close (97.3 s), then the bright pink-red lid. Ramp the L60 glow fade, and don't cut from dark straight to the bright lid.
4. **122.2 to 127 s (L73 to L75).** A black pane behind Remi switches on and off at 124.3 to 124.8 s. Keep that pane one value, plus the red slivers at her hair and edge.
5. **L70 caption** "paint COLOURS" → "paint COLORS" (US English, and the spoken word already says colors).
6. **Title** reads like queued mirror-maze ("...Your Reflection" plus a glass emoji). Take the critic's "Her Reflection Keeps Walking AWAY 🪟". Start the description with L01's words, "If anyone sees your reflection in a window, they'll know." Never queue it next to mirror-maze or ep62.

Nice-to-have: update script.md's L01 text to match story.json.
