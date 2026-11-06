# ep133-tent-zip handoff

**STATUS: dropped (2026-11-06): the creature test failed three tries** (builder step 1, audit decision 4). Nothing past the creature still was built. No PR was opened.

## The tries
- **Try 1:** failed my own check, so it wasn't sent to critics. With the face covered it read as a yellow-and-green slab with a candy-cane pipe for a neck and a floating head. The tent apex was 1.95 m, so the roof proved nothing, and there was no blue rim.
- **Try 2:** failed my own check. The head poked in from the frame edge on a neck that read as a scarf. A pole arch crossed the middle of the frame with empty roof above it, the legs and lantern took the bottom half, and the figure wasn't visibly bigger than the narrator.
- **Try 3:** two fresh critics judged it.
  - Critic A: **3/10, frightening: no.** With the face covered it reads as a padded armchair or a toy robot. The bright yellow torso and the green ribbed panels are friendly colours, the lantern lights the whole front, there's no dark pocket, and the face still has eye whites and a mouth line.
  - Critic B: **4/10, frightening: no.** It reads as a glowing yellow lawn chair with green straps. The face looks goofy ("smirking dude") instead of wrong.
  - What both said worked: the head lying sideways against the bulging roof reads for scale.

## Why it failed, for a retry or a rewrite
The script puts Dev's own bright costume (yellow hoodie, green puffer vest) on the creature. The lantern lights it from below, which lights the whole front, so the stretched seated torso reads as furniture. The critics' fix:
- a dark matte body;
- the lantern lighting only under the chin;
- a hard moon rim from behind;
- glints for eyes and no mouth.

That means changing the face (the `faces.py` options or a custom face) and the costume. It's a redesign, and the cap of three tries is used up. Under audit decision 7 it doesn't qualify as a near-miss (the scores are 3 and 4).

The files stay on branch `claude/batch14-ep133-tent-zip`: `set.py` holds try 3, and the generator is a stub with S29 only.
