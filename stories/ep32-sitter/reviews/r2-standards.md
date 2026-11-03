# ep32-sitter: standards, round 2 (rule-first redo, 2026-11-03)

Verdict: approve

Checked: script.md, story.json, package.json, `check` (warnings only), `preflight` (0 blocks), the preview contact sheet, 55 frames from 0.1 to 86.0 s, luma through S22 to S27, S33 to S36b, the diff since round 1, and the premise and twist of every story. No story in the batch changed since round 1.

1. **Fiction:** pass. No text or signs at the bus stop, cafe, bakery, arts centre or hall. The canvases carry no words.
2. **Kids and mature themes:** pass. Every character is an adult. Nobody is hurt, and S24 keeps a gap at 51.4 s. The package doesn't aim at kids.
3. **IP:** pass. The faces, hair, glasses and outfits are our own. No game is named anywhere.
4. **Originality:** pass, as in round 1. ep43 is still the nearest, but its marker, setting, creature, twist and ending all differ.
5. **Flashing:** pass. The preview reads PASS: at most 1 flash a second (2 on the 3-frame reading), 2 bright cuts a second, and an extended 3-frame run of 0.57 s. The S22 dip ramps from 63 down to 22 and back up to 67 with no black frame. The S34 restore rises smoothly over about 1 s.
6. **Package:** pass. The title, description and pin are clean. `cover_s` 50.0 lands in S23 (48.7 to 50.5 s) on "BESIDE ME.", with both faces lit and in frame.

## Round 1 must-fixes
- S35b (75.60 to 76.33 s): fixed. The dropped brush now reads clearly on the boards.
- `cover_s`: fixed (50.0).

## Nice-to-haves
- S35b now overshoots. Its mean luma is about 180, against 91 in S35 and 97 in S36. That makes a 0.73 s bright pop, which passes now. Lowering its `ev` by about 1 would put it at S35's level and remove the risk in the final.
- Take `"hold"` out of package.json once the critic approves too.
- Don't upload ep32 right next to ep43.
