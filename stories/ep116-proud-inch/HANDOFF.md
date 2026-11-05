# ep116-proud-inch: DROPPED (round cap spent, proof qa failed)

Reviews: standards approve (r2). Critic r1 revise 6.9, r2 revise 7.1 (single fix L44), r3 rescue approve 7.2 (hedged: S66 doorway only implied, mark above heads).
Proof run 41984950365 (sha 18ffb0f4) drew fine: flash pass, clip 0, -14.1 LUFS / -1.8 dBTP, craft 0 blocks (warns: cuts 8.81/10s, saturation 0.388).
Proof qa (qa/ep116-proud-inch.json): FAIL, two fixes:
1. Frame 0 of S01: Grandpa missing (empty doorway), appears at frame 1. Pops on every loop wrap. Suspect frame-0 pose/sit in set.py animate (`root.location.z +=`).
2. S17 15.63-17.17 s (L08 "so customers can see his FACE"): Grandpa's head cut by top edge, tag over one eye. Pull camera back/lower so whole head sits centre-right below the tag. (framing.py did not catch it.)
Notes: tag "5'10"" illegible at phone size from 71.4 s; L44 doorway implied only.
Dropped per brief because rounds + rescue were already used. Both fixes are small; if the orchestrator allows one more builder pass, apply them, rerun proof, re-qa. Hold restored in package.json.
