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
