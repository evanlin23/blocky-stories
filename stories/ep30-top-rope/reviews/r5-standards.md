# ep30-top-rope, round 5 standards (redo, first review of the new version)

Verdict: revise

Checked: script.md, package.json, story.json, the preview contact sheet, stills sheets A and B and single stills (S13, S38, S44), every other story's premise and twist, and `python -m blocky preflight` (0 blocks, flash PASS on the preview).

Passes:
- **Fiction:** no set text, signs or real places. The anchor plate's two strokes are plain marks, not a word.
- **Kids and mature themes:** the whole cast is adult (date pair in their twenties, Mum in her sixties). Falls end soft on the rope, nobody is hurt, and there are no death words. made_for_kids is false.
- **IP:** faces, hair and outfits are our own. No game name anywhere.
- **Originality:** check passes. The new premise, twist (`it-was-them`, used by no other story) and set are distinct. ep38 (a silhouette of who you miss most) is the nearest rule, but its mechanism and twist differ.
- **Hard rule 8:** captions, title, description and pin are clean.

## Must-fix

1. **Flash, S13 to S14b (19.5 to 22.7 s).** The preview's 3-frame reading hits 6 changes a second at 20.73 s, which is exactly the cap, with a 0.67 s extended run from 16.33 s. The final has every frame, so it will likely go over. S14 runs only 0.40 s (21.23 to 21.63) between the lit roof and the anchor close. Cut S14 and let S13 run to 21.63, or hold S14 for at least 0.8 s by trimming S13. Then re-run preflight and confirm that 3-frame changes are 5 or fewer there.
2. **Package `hold` (package.json).** The `"hold": "redo: ..."` key is still there. Remove it in the same PR once both r5 reviews approve. If it stays, the story never uploads (Packaging → Hold).

## Nice-to-have

- S44 (L44 "Two SHOE PRINTS"): no prints can be seen in the preview still. Light them so the line matches the picture.
- S04: his_mum's head leaves the top of the frame as she lifts. Keep her face in frame.
