# ep138-tomorrow-mirror: standards, round 2 (check only)

Verdict: approve

## Round-1 must-fixes
1. **L20 and L26 ("Not X, it was Y" cadence): fixed.** L20 is now "Tomorrow's the THIRTEENTH. / That was TWO days out." and L26 is "And twelve / was TODAY." in script.md, generator/lines.json and story.json. S20/S20b (36.2 to 38.3 s) and S26/S26b (45.5 to 46.8 s) are re-timed to the new captions. I checked them at phone size: the captions match the shots and sit clear of the faces, and there's no "not" cadence anywhere in the film.
2. **L31 "do I TRUST?": fixed.** It's now "Which me / do I BELIEVE?" (S31, 53.1 to 54.2 s). It matches the pin and still loops into L01.

## Regressions
- **L08 (critic change), "Tomorrow-you / never LIES. / So why did mine / say TWO things?":** no regression. S08/S08b (14.6 to 17.2 s) captions are in sync. It doesn't spoil the twist, because the two messages and their dates still play out in order, and L14's "never TALKS" still lands. It's no hard-rule issue.
- Preflight shows 0 blocks, flash PASS (1625 frames), and a 54.17 s timeline. The preview's length matches the timeline. Nothing is blank or broken.

## Should-fix (not blocking)
- "TWO" is the key word in both L08 and L20. That's fine, but you could key "THINGS" in L08 instead so "TWO days out" stands alone as the clue.
- Carried from r1 (nice-to-have): the description's "or quit a job" isn't in the film. "Or sell a painting" is.
- The `hold` key in package.json comes out on approval, as planned.
