# ep95-corn-maze: handoff (second orchestrator's story session)

**STATUS: dropped (2026-11-04).** Not approved after review round 2 (the brief allows 2 rounds, no rescue). No PR opened.

## History
- Creature test: try 1 failed (it read as a smiley emoji on a rug), try 2 passed (opus critic).
- Build: two container restarts; resumed from checkpoints.
- Round 1: critic revise (scare 4; the night read as day; the overhead read as a rug on flat blue; S47 inside the pickup; June a faceless head from behind). Standards revise (the ending was too close to mirror-maze; a banned "Not X, it's Y" cadence; the "Nobody Gets…" title opening; the stale package; two cameras inside objects).
- Fix round 1: the writer rewrote the ending (June stays, and at dawn the maze shows her face), changed the reveal line to "I don't have FEET." / "I'm the MAZE." and retitled it "Lights Out Means You STAY All Night 🌽". The builder fixed the night, the overheads, June's facing and the cameras.
- Fixed preview (79.6 s): preflight 0 blocks; flash PASS (2387 frames); picture changes per 10 s 18.1 and 30.3; motion energy 10.1; longest still 0.07 s. Warnings: cuts per 10 s 10.3, sound events per 10 s 4.15.

## Round 2 verdicts (final)
- **Standards: revise.** S42 (64.3 s): the "STAR" is a crossed pentagram in a ring, which reads as an occult pentacle (hard rule 3). Every round 1 fix landed.
- **Critic: revise.** Scores: hook 8, back-row 7, narrator fit 9, broad appeal 4, relationships 8, feeling 7, big idea 7, scare 6, creature 6, twist 6, lore 5, warm turn 7, shots 7, faces 7, sound 7, captions 8. "The reveal and the payoff don't read for a cold phone viewer."

## Open must-fixes
1. S42: the star is a pentacle. Use a plain 10-point star outline with no ring (`geo.py` `layout_shapes("star")`).
2. S33: "I don't have FEET." plays over a flat beige blur. Show an empty straw path with stalks.
3. S49a: June's dawn face is gold on gold and reads as a smiley. It needs high contrast and a hat and braid that read at 300 px.
4. S48a to S50a: the dawn sky is a flat orange wall and the porch roof reads as a white counter.
5. S34: the reveal crops the face. Frame both eyes and the whole smile.
6. Broad appeal 4: the reveal and the payoff need to land cold, which is a concept and clarity issue, not just polish.

If anyone revives it: the premise (the maze is the narrator) is sound (narrator fit 9), but it needs a reveal picture that reads at once at 300 px, and a payoff a cold viewer gets.
