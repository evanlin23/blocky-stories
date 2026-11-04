# ep91-ninth-coffee: handoff (DROPPED, 2026-11-03 Central)

**Status: dropped at proof qa.** Both review rounds were used, so the proof-qa fixes don't fit (brief: 2 rounds in total, no rescue).

## Where it stands
- Branch `claude/batch8-ep91-ninth-coffee`, PR #225 (closed, not merged).
- Round 1: critic revise (average 6.4, scare 4, creature 4), standards revise. The writer rewrote L04, L23, L44 and the pin, and one builder applied every must-fix.
- Round 2: critic approve (average 7.0, scare 5, creature 5), standards approve. Hold removed, check passes, gate OPEN, pytest 197 passed.
- Proof: proof.yml run 41748339149 (sha 25c33d6) drew and concluded success. Craft 0 blocks, 0 near; pace 18.7 and 29.3 changes per 10 s, motion 11.43; -14.2 LUFS, -1.9 dBTP; flash pass; clips are all figures against their own streaks.
- **Proof qa: FAIL** (`qa/ep91-ninth-coffee.json`).

## Open must-fixes (proof qa)
1. 36.2-38.0 s (S41-S43) and 38.7-39.5 s (S45): the ten-cupper streak is a stack of hard-edged flat cyan slabs sitting beside the runner. At 37.5-38.25 s (S43, "TWICE as fast") the frame is a wall of panes with the figure a sliver at the edge. It reads as glass dividers, not speed, right at the reveal. The trail must taper and fade along its length, with soft edges, and shrink away behind the runner. (The round-2 critic flagged the same thing as advice.)
2. 55.0-55.3 s and 55.9-56.8 s (S60-S62, "He was never too busy for me"): Kai's streak is one still flat pane covering half the frame while he sits. Fade it out or drop it.
3. cover_s 51.5 has the "KAI." caption across his face and a pane behind him. Move it to about 50.5 s or 68.0 s.

## Underlying weakness for a rescue
- The creature scored 5 in both critic rounds: "eerie-ordinary", neither frightening nor silly. With the face covered it's "just a guy in a grey shirt".
- The R6 rig scales evenly, so the creature playbook's stretched limbs (rule 2) were not built; the playbook says to use kit.box in set.py for that.
- A rescue should rebuild the streak as a tapered, fading trail (fixes 1 and 2), fix the cover, and re-proof. A writer might also strengthen the scare: the story's fear is the speed, not a monster.

## Engine note (not a bug I could fix)
- After a timeline change, `out/<story>/frames-preview` keeps stale frames, which gave a false flash FAIL on one preview. Delete it before re-rendering.
