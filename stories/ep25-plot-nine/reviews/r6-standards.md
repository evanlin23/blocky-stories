# ep25-plot-nine: standards, round 6

Verdict: revise

Checked: preview frames and sheets, `preflight` (0 blocks, flash PASS), every story.json, "Claimed big ideas", the engine diffs, tests (105 pass).

Pass: fiction (no set text, plain stakes, made-up hill), kids and mature themes (dark tapering roots, no bones or body; everyone adult and unhurt), IP, flashing (fog ramps are smooth), shared engine (the new `lowpass` keys and the `rootcreak`/`tock` kinds are opt-in, and no other story uses them; the homophones are applied to both sides of the ASR comparison, so they only loosen ep25's check and change no film). The big idea is new: leaving and belonging, not being forgotten or unseen.

## Must-fix
1. **L02 "Old Mr PELL'S", description paragraph 1:** Mr Pell is already the montage neighbour in `ep33-chairlift` (cast `mr_pell`) and `ep36-ice-huts` ("Mr Pell walked home... behind his flame"). A third "Mr Pell does the rule" montage beat reads as templated (hard rule 5). Rename him to a new made-up name that no other story uses, re-voice L02, and update the description, script and story.json.
2. **L31 "It's HER." (S43):** this line repeats `ep32-sitter`'s reveal ("The thing on the stool was Mum"). Put the leaving up front: change it to "They're HER / ROOTS." and re-voice. Start the story.json twist with "The faceless thing is Mum's own roots".
3. **package `cover_s` 49.2:** this frame is a dark, empty bean bed ("where its ROOTS GO."). Use 48.4 (S39, Mum close, "looks right BACK.").
4. **package `hold`:** remove it in the PR that fixes 1 to 3.

## Nice-to-have
- `stories/lore.md` has the original ep25 Bench row twice. Delete the old one.
- L17 "Mum just goes QUIET" echoes ep36's "Grandad went quiet".
- Add `"lane": "core"` to package.json.
