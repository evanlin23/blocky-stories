# r4 standards

Verdict: revise

Fiction, kids, IP, originality and flashing pass. `check` reports no problems and preflight has 0 blocks. Only the package needs changes, and each one is a single line.

- **Fiction:** pass. Door plates show digits only and none is cut off. The montage doors and Jo's street have no signs or numbers.
- **Kids:** pass. Me and Jo are adults, and nobody is hurt.
- **IP:** pass.
- **Originality:** pass. The rule type (a door opens by what of yours is inside) is the only one of its kind in this batch (ep23 to ep33, where only ep26 and ep28 open on a rule). It also differs from every rule-first story on the ep36 to ep58 branches. ep52's rule (lost things come home) is the closest, but its twist and ending are different. None of batch 1's banned list or the tired template shows up.
- **Flashing:** pass on the preview: 1 flash/s, 3-frame 2 flashes and 4 changes/s at 39.9 s, red 0. Things to watch in the final: the L40 to L43 ramp-up followed by the cut to the lit face (about 75 to 81 s), and the L81 lamp fade. That fade changed after this preview was rendered.
- **Package:** fails on the items below.

## Must-fix
1. **Title (package.json and story.json):** it isn't in the owner's title format (title case, one word in caps, under 60 characters where possible; see main bc69d75). Use "In This Town Doors Only OPEN If Your Stuff Is Inside" (52 characters).
2. **package.json:** add `"lane": "core"` (RULES.md, the 70/30 mix).
3. **package.json:** add `"cover_s": 0.6`. Without it the render picks 78% of the way in, which lands on a blank yard wall at 111.6 s ("By then,").

## Optional (critic's call)
- L75 (3.7 s): the sock reads as a stack of pink blocks.
- L76 (5.9 s): the spoon is hard to see at phone size.
