# ep41-orchard-rows handoff (paused 2026-11-03 for the usage limit)

**Where it stopped:** the round-5 fix round. Every r5 critic and standards must-fix is applied in the files and committed (615f4402), and the changed lines are re-voiced. It stopped just before the full preview render, so none of it has been seen in frames yet. The story is on hold, and package.json still has its "hold".

What's applied:
- L01 "Two trails of footprints. Only mine glows." (opening "count").
- L02 "Every footprint here glows. Except the ones beside MINE." The lead chose this over the critic's "Never..." line, for opening variety.
- L56 "I looked back down the row. Only FOG."
- Nan → Nana everywhere.
- Sky #4f8fe0, fog halved, boot-sole prints and pressed squares, creature relit (deep face cuts, cold key, #a8482e).
- The S70/S71 flash reframes and the trails at 3.4.

**Next:**
1. Stills of the first 3 s and of S35. Check that the squares read as footprints at phone size.
2. `render --preview --force`, then finish, mix, flash and preflight to 0 blocks, then `scripts/measure.py`.
3. Round 6 critic and standards. This is the last normal round, then at most one single-fix rescue. If it doesn't approve, drop it with a hold line.
4. Ship: remove the hold, merge main, PR, merge after `test`. Then the qa agent on the final film.

ep37 and ep33 were dropped (#154 and #156). Their builds are on their claude/*-opening branches.

**Before resuming:** merge main first. Polish v2.2 (#168) and v2.3 (#175) landed while paused, and look.polish turns both on.
- Keep the story's own sfx to 2 to 4 events per 10 s.
- Use `"hold": ["Sxx"]` on frame-exact shots: S01, the two trails side by side, may need it.
- If pace fails, shorten the quiet span (L55 to L63) or add motion inside it. See builder.md and docs/engine.md → The polish pack.
