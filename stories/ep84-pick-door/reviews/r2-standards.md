# ep84-pick-door: standards, round 2 (final)

Verdict: revise

Judged on the new preview (32.3 s) and its frames.

1. Fiction: pass. Numerals only, no signs. L19 "MOM left the hall LIGHT on" is over the lamp only, no family on screen.
2. Kids and mature themes: pass. One adult "you", nobody hurt.
3. IP: pass. No game name. Door 4's black plate with a white 4 reads as our painted numeral, not a brass hotel plate.
4. Originality: pass, as in round 1. Batch openings ban, count, confess, cost, if, one each. Nothing from the batch is in `queue.txt` yet, and `uploads.json` is empty.
5. Flashing: must-fix. Preflight still says PASS on the house bar, but it went from 3 to 11 changes/s since round 1, and general_3f extended is 3.5 s from 24.8 s, close to the 4 s block. Two causes, both in S19:
6. Package: pass. `hold` is now "awaiting proof qa". Delete it once proof qa passes.

## Must-fix
1. S19a, 28.7 to 28.9 s (L19 "the hall"): the camera goes through door four's slab. The frame turns dark grey (mean light drops from 193 to 89 and back) for about 0.4 s. Move the dolly path clear of the door leaf, or open the leaf wider, so the lamp shot stays bright the whole time.
2. S19b, 29.27 to 29.87 s (L19 "for you."): the picture switches between your `soft` face and a back view of you on the mat every 2 to 3 frames, about 7 times a second (seen in the mp4 too). It looks like the two preview jobs disagree on the camera or the figure for this shot (frames 879, 883, 887... are the back view). Give S19b one camera and one figure state, then re-run preview and preflight. Changes/s should drop back near round 1's 3.

## Nice-to-have
- S01, S21: the mat scuffs still read as letter shapes at phone size.
- Don't queue ep82-no-door next to this one.
