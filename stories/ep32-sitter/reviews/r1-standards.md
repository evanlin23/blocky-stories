# ep32-sitter: standards, round 1 (rule-first redo, 2026-11-02)

Verdict: revise

Checked: script.md, story.json, package.json, `check`, `preflight`, preview contact sheet, stills sheet, preview frames at 16.9 to 85.8 s, and the premise and twist of every story.

1. **Fiction:** pass. No real places or claims. The bus stop, cafe, bakery and arts centre have no text or signs.
2. **Kids and mature themes:** pass. The cast is all adults (Mum is in her fifties). Nobody is hurt, and S24 keeps a hand's gap. The package doesn't aim at kids.
3. **IP:** pass. The faces, hair and outfits are our own, and no game is named.
4. **Originality:** pass. ep43 is close in theme (being known vs being looked at, a loved one going unseen, a figure one table or easel nearer). But the marker (fade to pine vs a number), setting, creature (the faded loved one herself vs the Negative), twist (`loved-one`: the thing is Mum vs `about-me`: you don't count yourself) and ending (painting her face, then a cold sting vs saying names aloud) all differ. `check` passes on the phrase overlap.
5. **Flashing:** preview PASS (max 1 flash/s 1-frame, 2 on 3-frame). One stretch must change (must-fix 1).
6. **Package:** title, description, pin and `made_for_kids` are clean, with no dashes or banned words. `cover_s` is wrong (must-fix 2).

## Must-fix
1. **S35b, L35 "her BRUSH", 75.60 to 76.33 s:** the shot renders almost black (mean luma about 1 to 4 against about 97 in S35 and 86 in S36). The camera at z 0.85 looking down to z 0.05 is probably inside or under Petra's easel. The picture doesn't show the brush, and bright to black to bright in 0.73 s is a full light drop that the final may flag. Move the camera clear (for example, raise it to z 1.1 and pull back 0.4 m) so the dropped brush is lit at about S35's level.
2. **package.json `cover_s` 56.0:** this lands on S27 (car park, "our SITTER was."), not S23. Set it to `50.0` (S23, caption "BESIDE ME.", 49.64 to 50.46 s).

## Notes
- `faces.py` `corners` is opt-in. It defaults to False, `face_key` only adds `co-` when it's set, and no other story uses it, so other films don't change.
- Once both reviews approve, remove `"hold"` from package.json.
- Nice-to-have: don't upload ep32 next to ep43. Their shape tags differ, so the uploader won't keep them apart.
- The loop seam (dark S40 to sunny S01) and the car park cuts at 55.7 s pass now. Watch them in the final's flash reading.
