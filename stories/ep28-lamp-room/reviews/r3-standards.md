# ep28-lamp-room: standards, round 3

Verdict: revise

The round 2 flashing fix landed. Preflight on the current preview reads 1 flash a second at most, 3 changes a second at most (99.5 s), no red and no extended run, and in the L54 run I'm in frame on the first frame. Fiction, kids and themes, IP, originality (`check` is clean) and rule 8 all pass. In S78 the Upward stands clear of me. The mix is -14.1 LUFS and -1.7 dBTP. L68's caption now matches the voice.

Must-fixes
1. **Title (`package.json` and `story.json`).** "Someone climbs the lighthouse stairs one turn higher each night." says "one turn" while L35 ("two turns HIGHER") and L43 ("Two MORE turns") say two, so on a first watch it looks like a mistake. It's only true once you know I'm walking down, so it also hints at the twist. And it isn't the world's rule that RULES (Packaging) asks for. Use this in both files: "This lighthouse has one rule: after dark, stay on your own floor." That is L10 and L11's rule, it spoils nothing, and no title on main or on the ep21 to ep35 branches uses this shape.
2. **`package.json` has no `shape`.** `scripts/upload.py` reads it to keep two same-shape stories from going out back to back. Add `"shape": "about-me"`, because the twist is "the one on the stairs was me".

Nice-to-haves
- Add `cover_s` of about 88.0. That frame shows the lit crown face at N4 under the caption "below me.".
- Note for ep41-orchard-rows, not for this story: its twist ("I have sleepwalked back...") repeats ep28's sleepwalk twist, and ep28 claimed it first in `stories/ideas.md`.
