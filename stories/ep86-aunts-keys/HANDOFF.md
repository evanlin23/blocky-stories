# ep86-aunts-keys: handoff (dropped, 2026-11-04)

**Status: dropped.** It is not approved after 2 review rounds, and there is no rescue round. No PR was opened.

## Verdicts
- **Round 1:** critic revise, standards revise.
- **Round 2:** standards **approve** (`reviews/r2-standards.md`, no must-fixes). Critic **revise** (`reviews/r2-critic.md`): the scores average 6.9, against a 7 bar.
- **Round 2 critic scores:**
  - hook 7, back-row 7, narrator 9, appeal 9
  - relationships 6, feeling 7, big idea 7, scare 7
  - creature (me asleep) 8, twist 7, lore 5, warm turn 6
  - variety 6, faces 5, sound 7, captions 7

## Open must-fixes (critic round 2: all picture and sound, mostly framing at phone size)
1. S16 (L09, 17.5 s): Lou's head is cropped above her glasses. Frame her whole head and the ring.
2. S86 to S87 (L49, 79.6 s) and S104 to S105 (L55, 92.6 s): a bare orange wall with a cross shape, so "her door" never reads. Show number one's door with its 1 plate, open a crack with warm light. In L55, add my sleeve on the handle.
3. Lou's face is grey in daylight in S18 to S19 (L11, 20.3 s), S35 (L23, 40 s) and S126 (L63, 110.5 s). Light her with the warm key, as at 0.5 s and 52 s.
4. S137 (L69, 119.8 s): the neighbors' heads are cut at eye level. Frame them whole, with the waving arms in shot.
5. S111 (L58, 97.8 s): a white block fills the frame. Show the door, the key and tag 7.
6. P02 (55.6 to 56.2 s): the hush is dead silent at -66 dB. Keep the room bed at about -40 dB, and keep the riser.

## Where it stands
- **Build:** the sources are all committed. The last preview was 124.77 s.
  - Flash PASS at full rate.
  - Measure: 0 block, 0 near. Sound is 3.93 events per 10 s.
  - Mix: about -14 LUFS, true peak -1.7 dBTP.
- **Words:** L29 says "every OTHER house". The new L49a, "She can't lock me IN. / My bolt turns / from inside, / and asleep, / I just TURN it.", answers "why not lock his door?".
- **package.json:** still has `"hold"`. cover_s is 0.6 (the ring in Lou's hand).
- **Lost time:** the container restarted twice during fix round 1.
- **A stale-cache trap:** the first preview after the restarts drew from cached frames of older timelines, which made a 15 Hz flicker and a false flash FAIL. Redraw with `render --preview --force` after a re-time.
- **If someone revives it:** the story and words held up in round 2 (all 9 hit points yes). What's left is a framing and lighting pass on about 8 shots plus the hush bed. A new team would need fresh review rounds.
- **Queue notes from standards:** keep it away from ep52-ferry-crossing and floor-thirteen.
