# ep50-beach-huts, round 5, standards

Verdict: revise

r4 fixes: 1 to 5 pass. The opening holds one framing from 0.13 to 2.4 s, with a whole face and the reflection in a tinted pane. Red reads 0 everywhere and the L26/L27 stripe is muted. The L59 to L61 laptop beat stays lit. No pane toggles at 124 s. L70 now says COLORS. Flash: PASS. The only warning is 7 changes/s (3f), so the upload adds the flashing line on its own. Fiction, kids and IP pass, with no set text. The package lints clean, the `if` opening matches L01, and no queued story opens with `if`.

**Title (6):** pass. "On This Beach, Windows Show What You WANT 🪟" shares no opener, caps word or emoji with mirror-maze ("Never Walk Away From Your REFLECTION 🪞"). The two stories also differ in setting (day beach huts vs night fair), creature, twist (misread vs echo) and palette. Both have a reflection rule, so **never upload ep50 next to mirror-maze**. Mirror-maze went up 2026-11-03, so ep50 can't be the next upload. Keep them at least 4 apart, and say so in queue.txt when ep50 is queued. ep62 ("The Elevator Mirror Shows FIVE") has the same "glass Shows X" shape, but it's dropped. Retitle ep62 if it comes back.

Must-fixes:
1. **Music (hard rule 5).** story.json `music` is root 43, dorian, 76 bpm. That's the same as ep41-orchard-rows, and the same mode and tempo as mirror-maze (40 dorian 76), its reflection sibling. Change it to an unused combination, for example root 46, lydian, 88 bpm, and keep the section plan. This is sound only, with no redraw.
2. **Frame 0 (0.00 to 0.13 s, S01).** Drawing 0 (`frames-preview/f00000.png`) shows a different picture: a huge sideways brown head with a grille mouth and no glass, then a hard cut at 0.13 s. Key S01's glass and reflection state from frame 0 so the first drawing matches the rest. It's the hook frame.

Nice-to-have: there's a thin red tick on Remi's shirt at 124.2 to 124.5 s (L74).
