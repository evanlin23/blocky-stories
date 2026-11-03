# Handoff: floor-thirteen opening fix (paused 2026-11-03, usage limit)

Branch `claude/opening-floor-thirteen`. No PR yet.

**Done**
- New warning opening, re-voiced:
  - L01 "If THIRTEEN lights up by ITSELF, don't step OUT." (2.14 s, per-line tempo 1.1)
  - L02 "Even if your KEYS are up there."
  - L02b states the rule.
- New first shot: the 13 button lit on its own, centred, with digits on every button. Then my face on the walnut wall.
- US English in L14, L23, L31 and L35.
- Polish pack on, extra sfx, drift on still shots.
- Package:
  - title "My 13 Button Lit Up By ITSELF 🔘"
  - pin "Comment KEYS if..."
  - opening "if"
  - cover_s 51.4
  - `hold` removed
- Reviews in round 7: standards approved, critic revise (avg 7.7) with ONE must-fix.

**Next (the rescue round, already counted)**
1. L36 (about 65.7 to 67.3 s): the stairs shot is a near-black frame, then a blank beige slab. Build lit concrete steps with my orange shoes running down, or use the critic's fallback: the twelve landing with the stairwell door swinging open.
2. Flash margin: the 3-frame changes reading is exactly 6 at 26.0 s (the lit 13 cuts hard to the dark indicator). Start that cue about 0.2 s earlier.
   - WIP for both is uncommitted-then-committed here: set.py, make_story.py and story.json. It is untested, and the stopped builder's last note was "Flash fails; inspect". Check its diff (`git show HEAD`) before trusting it.
3. Preview, flash and preflight, then a critic re-check of L36 only.
4. Gate, merge main, PR, merge after `test`.
5. qa on the final film.

## Update 2026-11-03 (second pause, handed to another orchestrator)
- This session re-read HANDOFF and launched a builder for the L36 stairs fix and the flash margin (26.0 s cue). The builder was stopped on handoff before reporting; any uncommitted edits it made are in this push as WIP and are UNTESTED.
- Nothing else done: no critic re-check, no gate, no PR, no proof, no qa.
- Next: steps 1-5 above. Only ONE more critic round allowed (L36 only). If it does not approve, push and write why here. At the time of writing, no proof.yml on main; branch claude/proof-render exists. Merge only after proof qa passes and `test` is success. Don't dispatch render.yml/upload.yml; don't edit queue.txt.

**On resume:** merge main first: polish v2.2 (#168) and v2.3 (#175) are in.
- Keep this story's own `sfx` to 2 to 4 events per 10 s in all. This round added many sfx, so thin them.
- Use `"hold": ["Sxx"]` for frame-exact shots.
- Read builder.md and docs/engine.md, under The polish pack.

## Update 2026-11-03 (rescue fix done)
- L36 is now the lit twelve landing with the stairwell door open and me coming through (set.py stair_door cue, open before the shot). The 13 panel cue now clears at L14-0.25 (flash margin).
- Also cleared 4 clip blocks: Grandad stands clear of the leaf (HIS_DOOR y -4.9), his door opens before the Abels' wife appears, and the stair door opens at L36-0.6. Sound rev 8.
- Preview re-drawn, finished and mixed with the real voice: flash PASS, preflight 0 blocks (warn: sound events 5.89/10 s), clipcheck 0.
- Next: critic re-check of L36 only, gate, PR, proof, qa.

## Flash fix (78.5 s, proof 3f changes = 7)
Attendant lit cues respaced to L43, L43+0.38, L43+0.72 (0.3 s ramps, inside shot S56, none on a cut); sound.rev bumped to 9. Preview flash PASS; 3f worst now at 26.0 s (6), nothing in 76-81 s above 5. Full-rate proof should be redrawn.

## Final 2026-11-03: DROPPED (proof failed twice)
- Reviews: standards approve (r7); critic r8 approve for L36 (avg 7.8). Gate OPEN, check ok, pytest 171 passed, preflight 0 blocks.
- Proof run 1 (41708580407, sha 64769c3) and proof run 2 (41721119831, sha 30c1a44) both FAILED on flash only: house bar `general_3f_changes_le_6` false, 3f changes = 7 at 78.53 s, identical in both runs. Clip 0 hits, craft ok (cuts 6.53/10 s, picture changes 19.9, motion 9.75, longest still 0.27 s), true peak -2.0 dBTP, LUFS -14.04.
- Respacing the attendant countdown cues (lit 5/4/3 at L43, +0.38, +0.72; commit 30c1a44) did not move the reading. The quarter-res preview does not show this reading; only the full-rate proof does.
- Likely cause (not tried): the 76.57 lights cue (dur 1.0) and doors cue, the cuts at 76.57, 78.93, 80.10, or the polish pack's angle cuts / crop push on the attendant shots S55-S56. A fix needs a full-rate local draw of 75-81 s, which is more than one small fix.
- Per the rescue-round rule (second proof fail = drop), PR #188 is left open for the second orchestrator to record the drop on main. Nothing merged, no qa file written.
