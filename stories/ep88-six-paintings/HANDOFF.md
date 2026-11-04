# ep88-six-paintings: handoff (dropped, 2026-11-04)

**Status: dropped.** Not approved after review round 2 of 2 (no rescue round). No PR was opened. `package.json` still has `"hold"`.

## Where it stopped
- Built in full: rev 11, preview 33.4 s, preflight 0 blocks, preview flash passes (1/s, 2/s at 3 frames, red 0), clipcheck 0, measure 0 blocks / 0 near.
- Creature test still passed on try 3 of 3 (critic: "plain with some eerie pull, not silly, not yet frightening").
- Standards: r1 revise → **r2 approve** (`reviews/r2-standards.md`).
- Critic: r1 revise → **r2 revise** (`reviews/r2-critic.md`).

## Critic r2 scores
Hook 8, back-row 6, narrator 9, appeal 9, relationships 8, feeling 5, **big idea 6** (under 7 means revise), scare 6, creature 6, twist 6, lore 3, warm none (by design), shots 7, faces 7, sound 7, captions 8.

## Open must-fixes (critic r2)
1. **S14a (L14a, 19.5 to 22 s):** a blown-out white smear. Fog and the side of the glass don't read. Bring the exposure down, make the shot truly edge-on, and show a grey fog patch on the garden side, a dry inside and the hall red on our side.
2. **S17 (L17, 23.7 s):** the oxblood wall behind the man makes him read as inside. Put lawn and sky behind him, with the red only through the glass.
3. **S22b (about 32.2 s):** the second shadow lands on "It was just YOU". Hold it until L22b. Both shadows read as toilet-door icons on flat yellow, so give the floor wood boards and lamp pools.
4. **Big idea 6:** "a clever trick, not movie level". It needs a stronger reframe, which is a writer change, not a build fix.

## If anyone revives it
The main problem is the concept, not the build. A writer would need a stronger reframe for the window reveal before any rebuild, and fixes 1 to 3 are a single build pass after that. Standards' non-blocking note: the S13 to S14a cut is the film's biggest brightness jump, so dim S14a's sky.

No engine (`blocky/`) bugs were hit.
