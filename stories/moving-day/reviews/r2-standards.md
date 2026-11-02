# moving-day, round 2: standards

Verdict: revise

Preview checked: quarter-res, every 4th drawing, one frame per shot (S01 to S81).

- Fiction: pass. The set has no words or numbers, and the photos show only faces and a house.
- Kids and mature themes: pass. Both characters are adults. Mum sleeps unharmed, and the box ends stay on the quilt at the foot of the bed (S51, S54). No death words.
- IP: pass. The faces are our own marker drawings, and no game name appears.
- Originality: round 1's fix holds. There's no tuck (L53, S55), and the shelf box has no face (S79, S80). One must-fix below.
- Flashing: pass (preview, indicative). At most 1 flash and 2 changes a second, 0 red. Watch the near-clipped window in S10 (18.5 to 21 s) and the lamp coming up in S53 (91.4 s). Don't brighten either.
- Package: pass. No dashes or semicolons in the lines or the package.

## Must-fix
1. **S01 (0 to 2.2 s), S79 and S80 (132 to 136.6 s): a lore tally is on screen.** The L01 box has a black marker tally on its front, four strokes and a slash. It sits large in the hook and the end frames. The owner said this story skips the lore connection, and `lore.md` can't record it. The canon also says a tally matches the number of people a place was built for, so five strokes in a house of two is an unregistered extra-stroke thread. Delete the tally decal in `stories/moving-day/set.py` (the `if sx == 1:` block at about line 746, `boxes-shin-tally`) so the L01 box front is plain cardboard. Re-render S01, S79 and S80.

## Nice-to-haves
- `story.json` `twist` still says "tucking the old quilt round Mum". `check` compares it with later stories, so rewrite it to match the round 1 twist: the shelf box is the L01 box.
- `out/work/moving-day/stills` is older than the timeline (it has a still at f04154, but the film has 4146 frames). Rebuild the stills.
