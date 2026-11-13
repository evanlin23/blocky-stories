# ep154-dawn-car: standards, round 1

Verdict: revise

I read the script, package and story.json, walked all 51 shots (one preview frame each at 300 px), and ran preflight, check and staging.py (0 findings).

1. **L01 and `opening` (hard rule 5, batch mix).** Batch 15 has 6 `cost` openings out of 16 (ep139, 146, 147, 148, 153, 154). That's over 1 in 3, and ep146's retag was declined. Change L01 to a `must`: "In our town, / you can't HIDE / where you'd rather BE. / Your car goes THERE." Set `"opening": "must"` and re-voice L01 only. The loop still reads ("She wants a MUFFIN. In our town, you can't hide..."). This is waived only if the orchestrator retags another cost story before merge.

Passes:
- **Fiction:** no words or plates. The diner sign is a glyph (S18a). Made-up names only.
- **Kids:** every figure reads as an adult. Nobody is in peril and nobody is hurt.
- **IP:** no game name, logos or copied items.
- **Originality:** clear of ep115, ep120, ep129, ep132 and ep150.
- **Package:** passes hard rule 8. It says "It's made up.", the pin is a real question, and the reveal (L24) runs 52.4 to 55.0 of 58.2 s.
- **Flash:** passes the house bar. The worst stretch is 14.6 to 17.0 s (S07b to S08c, bright to dark cuts), at 6 per second on 3f in the preview. Watch it in the proof.

Nice-to-have:
- The car is built open, with no doors, roof or belts. That clashes with "Click." (S13a) and "hid in the back seat", and it shows unbelted riders (S21b, S24a, S24b). Doors and a strap across each seated rider would fix both.
- `staging_ok` lists S24b with no reason, and staging finds nothing there. Drop it.
- S16b and S13a are mostly flat gray and teal. Make sure they clear final qa's flat-frame check.
