# ep124-future-call: standards, build round 2 (filed r3)

Verdict: approve

This round only checks. I looked at the r2 must-fix and the critic's changed shots at 300 px from the preview: S03, S04a, S04b, S10a, S11, S16, S25b, S32 and S33a.

## r2 must-fix
1. **`cover_s`:** fixed. It's now 19.3 (S11): my face, the grille, the 00:20 tag and "NOTHING.". Nothing in that frame gives away the twist.

## Regressions from the critic's fixes
- **S03 red umbrella, S04a uncle lit, S04b water in the boat:** these all read. There's no text in the set and no new figure.
- **S10a, S16, S32, S33a head framing:** S16's face now fits in frame. In S10a my head is turned and cut at the right edge, but the finger on the speaker reads. In S33a the tag sits on Dad's cap, but his face is clear.
- **S25b stray object hidden:** the door view is clean.
- **Breath sfx on the line:** the mix is -14.1 LUFS with a true peak of -1.8 dBTP, so it passes.
- **Flash:** preflight says PASS and the house bar passes. Like-proof reads 4 flashes a second for general and 6 for 3f merged, against a cap of 6. The warning is at 37.4 to 39.6 s: caption pops on Dad's face in S24/S25 ("trying not / to CRY."), then the cut to the bright door in S25b. That's not a strobe, and the longest run is about 2 s, which is under the 4 s limit. Because it trips a warning, the final will get "Flashing lights and fast cuts" in its description. upload.py adds that line from the Actions measurement, so `package.json` doesn't need it.

## Should-fix (not blocking)
- `package.json` `hold` still says "batch 13: scripts only, not built yet". When the hold is released, change it to say why it's held, or remove it.

## Queue spacing
This is unchanged from r2. Keep it at least 3 slots from ep48-crazy-golf and ep89-sister-diary, and never put it next to ep98-town-whistle (`if`) or ep128 (both are phone stories).
