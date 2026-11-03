# ep41-orchard-rows, round 5, standards

Verdict: revise

I checked the preview (140.3 s), its own contact sheet (out/sheets/contact.png is from 07:33 and still shows the old L01), first3s.png, 50 frames I pulled, `preflight`, `check`, and the title against all 33 packages. The branch changes nothing in `blocky/`, so the defaults are unchanged. pytest: 145 passed.

Pass: fiction, hard rules 2 to 4 and 8, `made_for_kids` false, and the voice am_adam (male). Nan is never hurt and no illness is named. The new props have no lettering. L01 and L02 match the plot and the S01 picture. The title is 6 words with one caps word and one emoji, and it spoils nothing. Its "The [thing] ..." shape is the H3 test. It is close to ep62's "The Elevator Mirror Shows FIVE" but not a reuse. The hold stays.

## Must-fix
1. **Flash, 119.6 to 125.6 s (S69 to S71): the 3-frame reading gives 7 changes a second at 123.67 s, and the bar is 6.**
   - **S70 (120.97 to 123.67 s):** it opens on 0.9 s of near black (luma 4) because a body blocks the lens. It then jumps to luma 72 at 121.9 s. Start the camera clear of both walkers so S70 is lit from its first frame.
   - **S71 (123.67 to 125.63 s):** a body sweeps across the lens at 124.4 to 125.0 s, so the top third swings between 117 and 39. Pull the camera back and to the side so no one crosses it.
   - **Walking trails `wp` and `wb` (L58):** lower the strength from 5.0 to 3.4, the same as `fp`/`fb`. Close prints now clip to white.
   - Re-run `python -m blocky flash` and confirm it passes.
2. **US English: "Nan" is British.** It is in 16 lines (L08, L09, L13, L22, L31, L48, L49, L54, L57 and others) and twice in the description. Change it to "Nana" everywhere, re-voice those lines, and update the `phonemes` if needed.

## Nice-to-have
1. In the description, "so a trail that doesn't is not ours to walk beside" is unclear, and the film never states that rule. Try "One dawn, a trail that doesn't glow showed up beside mine."
2. ep51's title also puts GLOW in caps.
