# ep58-swing-bridge, round 5 (revival, final), standards

Verdict: approve

Passes:
- **Title (the r4 must-fix):** "Something on This Bridge Has DARK Hands 🌉" has 7 words, one CAPS word and the emoji last. It's a hook, not a ban or "Never" shape, so mirror-maze's "Never" title no longer clashes. It doesn't give away the about-me turn or the 3 AM floor-drop. No queued or uploaded title starts with "Something".
- **Opening:** line 1 is still the condition, so `"opening": "if"` still matches. `queue.txt` has no other `if` opening.
- **Fiction:** S01 (narrator at the green rail, dark sleeves along the top chord), S62, S66 and S91 show no set text, signs or real places.
- **Kids and mature themes:** the narrator in S01 and the creature's face in S62, S66 and S67b are adult blocky figures. Nobody is near the water or touched.
- **IP:** the faces are ours, including the creature's near-black hair and small black eyes. The dark cloth sleeves with folds are a plain mesh, not a catalogue item. No game name anywhere.
- **Originality:** unchanged since r4. The new S66 two-shot and the cloth sleeves don't move it toward any earlier story.
- **Package:** `cover_s` 105.0 lands on S70, the narrator's face lit from below by his own glow. It's clear, lit and has no spoiler. polish and flash_safe are on, and `made_for_kids` is false.
- **Check:** `python -m blocky check ep58-swing-bridge` says "no problems" (141.03 s, 86 shots).
- **Flash:** preflight PASS with 0 blocks. The 1-frame max is 1/s, the 3-frame max is 2/s, red is 0, and the house bar and the ep10 bar both pass.

Notes (not blocking):
- **Final flash, 100.5 to 104 s:** this is the same as r4. There's a 1.83 s run at 2/s on the 3-frame meter (S68's ramp into S69's near-black top over two bright hands). There's also a new 3-frame extended stretch of 0.87 s from 96.4 s (S66 into S67). Both are far under the 4 s house bar. Watch both in the Actions measurement. If the final fails, soften S69's black slab first.
- story.json `title` is still the old line ("In this town, your hands glow..."). That's harmless, but match it to the package if you touch the file.
- script.md S01 still says "No body", but the shot now has the narrator in frame. Update the row so it matches the film.
- Keep the spacing from ep51-fossil-hall in the queue (r4). Remove `hold` only after the proof qa passes.
