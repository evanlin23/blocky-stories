# ep89-sister-diary: handoff

**Status:** approved and proofed. Merge once `test` is green.

## History
1. **Reviews:**
   - Round 1: critic revise and standards revise.
   - Round 2: critic approve (average about 7.1, hook 8), standards revise (two black shots).
   - The second orchestrator revived it for a camera fix, and the standards re-check approved.
2. **Proof 1** (run 41776960749) failed qa: the score used the `musicbox` voice, which breaks hard rule 6.
3. **Rescue:** the second orchestrator allowed one fix. The `bubble` voice replaced the music box in sections 0 and L49.
4. **Proof 2** (run 41783437602, sha 92a5e40) passed qa (`qa/ep89-sister-diary.json`, stage proof):
   - craft: 0 blocks, 0 near
   - flash: passes
   - clips: 0
   - loudness: -14.1 LUFS, -1.8 dBTP
   - gate: OPEN

## Notes
- Engine guard idea: `check` should block the `musicbox` voice.
- `render --force` leaves stale frames. Delete `out/work/<story>/frames-preview` first.
