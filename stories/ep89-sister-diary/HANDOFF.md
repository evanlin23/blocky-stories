# ep89-sister-diary: handoff

- **Where it is:** fix round 1 is in progress, on branch `claude/batch8-ep89-sister-diary`.
- **Round 1 reviews:**
  - critic: revise, with scores around 6 (hook 4, faces 4, relationships 5, warm turn 5);
  - standards: revise.
  - Both reviews are in `reviews/r1-*.md`.
- **Word fixes, done:**
  - L01 moved to `must` (the second orchestrator's call);
  - L12 and L70 rewritten;
  - the package description fixed;
  - all three lines re-voiced.
- **Picture and sound fixes:** the 10 must-fixes from both reviews are in progress. The container restarted partway through, and a fresh builder resumed from the last commit.
- **Next:** round 2 is the last. It re-runs critic and standards, since both said revise. If either still says revise, the story drops. If both approve:
  1. remove `hold`;
  2. run check, gate and pytest;
  3. open the PR;
  4. wait for the proof, then the proof qa;
  5. merge once `test` is green.
