# ep89-sister-diary: handoff (DROPPED for good, 2026-11-04)

**Status:** dropped. The proof qa failed, and the second orchestrator's revival terms were "a qa fail drops it for good".

## The fail
The proof qa (`qa/ep89-sister-diary.json`, stage proof, run 41776960749, sha a615559) failed on one thing: **the score uses the `musicbox` voice** at about 0 to 35 s and about 85 to 115 s. RULES hard rule 6 says "no music box".

The fix would be to swap that voice in `generator/make_story.py`, regenerate, and draw a new proof.

## What passed in the proof
- craft: 0 blocks, 0 near; 2 warns (cuts 8.09 per 10 s, character motion 0.43)
- flash: passes
- clips: 0
- loudness: -14.1 LUFS, -1.8 dBTP
- gate: OPEN

## Review history
1. Round 1: critic revise and standards revise.
2. The fix round.
3. Round 2: critic approve (average about 7.1, hook 8), standards revise (two black shots).
4. The orchestrator revived it for one targeted camera fix.
5. The standards re-check approved (`reviews/r3-standards.md`).

## For the next writer or builder
- Check `story.json`'s music voices against hard rule 6 before review. The music plan in `script.md` asked for "soft plucked plinks", and the build mapped them to `musicbox`. Nobody caught it until the proof qa.
- The PR (#236) is left open for the orchestrator to close or rescue.
- The engine still offers a `musicbox` voice that the rules forbid. Worth a guard in `check` (I didn't touch the engine).
