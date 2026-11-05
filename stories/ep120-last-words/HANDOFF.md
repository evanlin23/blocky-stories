# ep120-last-words: HANDOFF (STATUS dropped, 2026-11-05)

Dropped under the two-round cap: after round 2 both reviewers still said revise, and the open must-fixes are more than one concrete fix, so the single-fix rescue does not apply (build brief, RULES audit decision 3). No PR opened.

## Round 2 verdicts
- critic (reviews/r2-critic.md): revise. Average 7.4, nothing under 5. All 10 round 1 must-fixes confirmed in. Scores: hook 8, back-row 7, narrator 9, appeal 9, relationships 8, feeling 7, big idea 7, eerie 6, twist 7, lore 6, warm 8, variety 7, faces 7, sound 6 (not re-heard), captions 8.
- standards (reviews/r3-standards.md): revise. Fiction, kids/mature themes, IP, package and opening all pass.

## Open must-fixes
1. Rule tag hidden in thermos close-ups S40, S41, S43 (L27, L29): tag hangs 1.0 m off the camera (set.py ~line 982, `dist = 1.0`), cameras are nearer. Fix: give the tag its own distance 0.2 m (`td = 0.2; th = td*12.0/lens; tw = th*9/16`, scale 0.56*tw, location (-0.37*tw, 0.6*th, -td)), bezel stays on `dist`.
2. Dad's cool fill fades in over 0.3 s after each cut (S62 79.23 s, S68 88.33 s, S69 89.83 s), so each shot opens dark brown. In generator/make_story.py set `dur=0.0` on the `dadfill` cues at L46-0.05, L52-0.05, L53; move L52-0.05 to L52-0.01.
3. S67 (L51) ends on 9 blank cream frames (88.03-88.30 s): `pulls_in` camera ends behind WIN. End at about [NX-2.6, NY+0.6, AZ+1.9] and check the last 10 frames.
4. Nice-to-have: L69 in story.json is "Now I come over every SUNDAY." but script.md says "I come over / every SUNDAY now."; make them match (avoids two lines starting "Now").

## State
- Build is complete and otherwise passing: preflight 0 blocks, framing.py 0 findings, flash pass (note 3f reading 7/s at 51.2 s on S29-S30), measure 12/12, clipcheck 0, true peak -1.9 dBTP at -14.1 LUFS, ASR clean with asr_forgive = eleven, sixteen. Preview 122.4 s.
- `hold` still in package.json. Nothing was ever PR'd or merged.
- Queue spacing if revived: not next to ep89, ep28, ep55, ep47 (`must` openings); at least 3 uploads from ep89, ep99, ep48, ep42, ep55, ep92; not right after ep99. It is the batch's soft sad family reveal.
- Revival cost: three small edits above plus one re-render and one more review by the first orchestrator's call.
