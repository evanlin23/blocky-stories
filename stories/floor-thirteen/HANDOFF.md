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
