# ep47-fitting-room: handoff for the final-film check (2026-11-03)

Shipped in #155 (critic r9 approve, standards r7 approve, gate OPEN). Next: run qa on `film-ep47-fitting-room` when it lands. It's 7th in `queue.txt`, and `plan_renders` draws 2 stories a run.

Watch in the final (advice from the reviews, not blockers):
- **Flash:** the preview's worst readings were 5 changes/s at 14.07 s (limit 6) and 1 flash/s at 0.73 s. A coat colour change cleared red at 0.73 s. Check both on the 16-shard final first.
- **Red near-blacks:** polish v2.1 turned near-black areas pure red until #143 (merged before #155). Check under the curtain shoes (54 to 56 s) and the bench front (50 to 52 s, dark oxblood wood is expected).
- **First 3 s:** a tag pops on "LIE" at about 0.3 to 0.7 s with the whole head in frame. The Uncle shot (2.6 to 4.4 s) should be readable on its dark wall, with about 2 to 5% near-white.
- **Loop:** the gap from the last word to the cut is about 0.8 s, against the house 0.2 to 0.3 s. It's advice only, so recut only if it feels slack.
- **Cover:** 94.7 s, the empty suit with eyes in the collar.
- **Engine:** this story uses polish's opt-in `punch_cap` (blocky/polish.py) to keep heads in frame on S01/S03.
