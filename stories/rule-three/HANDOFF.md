# rule-three: handoff (2026-11-03, 10:50 AM Central)

Batch 6 slot P6, the Buhkeeper pilot. The story session stopped here on the orchestrator's instruction (usage limit); a second orchestrator picks it up.

## State
- **Merged:** PR #161 (the story) and PR #165 (flash margin: every pair of cuts 31+ frames apart, 62 shots, `cover_s` 52.7 on the torn page). Main includes both from `293b535`.
- **Reviews:** standards approve (r2), critic approve (r3, the one rescue look, avg 7.4). `gate rule-three` OPEN. #165 changed only cut timing and dropped two short shots (S36 guests through the window, S63 page back into the pocket); no words, voice or set changed, and nobody re-reviewed it.
- **Full-rate flash (local, every frame the final draws, quarter res, #165 cut):** PASS with margin. 3-frame reading: 2 flashes and 4 changes in the worst second (19.9 s), cap 3 and 6. 1-frame: 1 flash, 3 changes. Extended 0.87 s.
- **Render on Actions:** no film of the #165 cut yet.
  - Run 41658149582 (#87, sha `f4e2cd9`) is still **queued at the pre-#165 commit**. If it produces `film-rule-three`, that film is the OLD cut: don't qa it, don't queue it.
  - Run 41663722827 (#88, sha `293b535`, the #165 merge) was cancelled by a newer push.
  - Run 41664698017 (#89, sha `66ca56c`, includes #165) is pending. Its film, or a later run's, is the right one.
- **qa:** not run. No `qa/rule-three.json` yet.

## Next
1. When a render run at `293b535` or later finishes with `film-rule-three`, download it and run the qa agent on that film (`qa/rule-three.json`). Check that the film is 77.6 s with 62 shots, so you know it's the new cut.
2. If qa passes, add `rule-three` to `queue.txt` in a small PR, spaced away from other lanes' shapes (experiment lane, shape `about-me`).
3. If qa fails: fix and re-render once (brief rule); a second fail drops it.
4. Report the verdict to the batch lead.

## Notes for later episodes
- The Buhkeeper never says "Buhtown" aloud (lore.md host section). L02's caption reads BUHTOWN, spoken "this town". The critic flagged that a caption-reader may comment on the mismatch.
- Pacing lesson: on the 3-frame flash reading every cut counts 3 changes, so two cuts under 1 s apart sit exactly at the cap. Keep cuts 31+ frames apart.
