# ep43-reading-room, round 6, standards

Verdict: approve

Checked the changes since r5: the new L01 and L02, the rewordings at L06, L07, L08, L24, L62 and L71 (voice-timings.json matches script.md), package.json, the new props in set.py, and the quarter-res preview (contact-full, contact-first3s, plus my own frames at 0.1, 2.5, 5, 9, 12, 14, 20, 31, 32.9, 34, 58, 76 and 128 s).

1. **Fiction:** pass. The new street opening is a plank wall and a plain blue window with no sign. The props (carpet_1, houseplant_1, light_floor1, sub_planter) are CC0 rows in assets/LICENSES.md and show no lettering or logo on screen. The wall clock has tick marks only, and the pages have ruled lines only.
2. **Kids:** pass. The cast is all adults, nobody is shown hurt, and there are no death words in the new lines.
3. **IP:** pass. There's no game name in the title, description or pin.
4. **Originality:** pass. No other queued story opens with "Don't let..." (every other L01 is "In this town/world" or ep20's line). No other title starts with "Only" or uses ONE. The title is a 6-word statement, with ONE as its only CAPS word and one emoji at the end. It isn't an imperative and doesn't say who the one is, so it doesn't spoil.
5. **Flashing:** preflight PASS, which is indicative only. The worst points are 3-frame flashes 2/3 at 5.17 s (the party rolls) and 3-frame changes 5/6 at 32.9 s (the bright dome cut into the dim room). The lamp dim is still a 1.5 s ramp.
6. **Package and hard rule 8:** pass. The new lines and the package have no dashes, semicolons or AI words. The text uses US English (mailman, neighbor, sweater). The description includes "It's made up". `made_for_kids` is false, and the pin follows the "Comment ONE if..." format.

## Nice-to-have
- Remove `hold` from package.json in this same fix PR once the critic approves.
- script.md is stale in two places: the cast still lists the baker, and "Marker by 2 s" still describes the sunny steps. Bring both in line with the film.
- 32.9 s sits one change under the 3-frame bar. If the final reads 6 there, soften the dome shot's exposure or move the cut.
