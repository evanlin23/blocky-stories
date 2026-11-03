# ep55-caravan-park: standards, round 4 (the recast)

Verdict: revise

Checked: script.md, story.json (rev 4), package.json, the preview contact sheet and stills sheet (84.5 s), frames pulled from the quarter-res preview (every 4th drawing) at 10 to 38 s, 56 to 76 s and 104 to 135 s, `preflight` (0 blocks), and every other story's premise and twist.

1. Fiction: pass. No real names, places or set words. The bus-stop sign is our own glyph.
2. Kids and mature themes: pass. All adults. Maggie being away is shown with the cap, the coat and the phone, never in harm words.
3. IP: pass. No game names in the package. Faces and outfits are ours.
4. Originality: pass. The changes touch only the cast and L10. An older married couple doesn't match ep38 (her silhouette), ep45 (a hug countdown) or ep33.
5. Flashing: pass. The preview measures 2 a second at 74.4 s and the 3-frame reading 2 at 4.4 s. The porch-light fades at L27 and L39 ramp. 74.4 s (dark grass, then the caravan side, then the fog wide) is the stretch to watch on Actions.
6. Package: pass. No hold. `cover_s` 84.5 is the lit Kneeler face. "It's made up." is there and no banned words. Hard rule 8 is clean in the lines and the description.

Narrator and audience: pass. "My wife, Maggie" (L10) is plain, she/her throughout, nothing narrows the audience. The narrator has grey hair and a moustache and reads as a man. Cold-viewer (my read of the narration only): who she is and what the twist means both come through. No fresh-agent run is logged for the recast.

## Must-fix

1. **Maggie doesn't look like a woman on screen** (RULES: "looks it on screen in the same beat"). S13 at L10 (17.6 to 20.1 s), then S20 onward. Her short white `cap` hair under the beanie and plain round eyes give the same face as his. It's also the same hair as the montage's bench husband at L06. Next to him she can read as a second old man, which is ep38's misread turned the other way. Change `cast.jory` to `"hair": "long"` (keep `hair_c` `#f2f2ee` and the beanie) and `"face": {"eyes": "lashes", "brows": true}`. Re-render her shots, check the L17 and L56 shoulder moss and the L20 flowers against the long side panels in stills, then rebuild the preview and re-run flash.

## Nice-to-have

- Log a fresh-agent cold-viewer run for the recast in script.md.
- Give `benchwife` lashes too, so L07 reads at a glance.
