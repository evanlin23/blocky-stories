# ep51-fossil-hall handoff (paused 2026-11-03, usage limit)

**Done:** opening "confess": L01 "I kept one secret, and now I glow." L02 "In this town, everybody can see it." (re-voiced; loops with the last line). US English (Grandpa, FLASHLIGHT, TURN AROUND, Neighbors). Flash fix at 96 s. Quality pass, polish on, cover_s set, no hold. Title "Keep One Secret and You GLOW 💡", pin "Comment GLOW if ...". Standards r5: **approve**. Critic r5: **revise** (reviews/r5-critic.md), all about the glow reading in 0–5 s.

**Stopped in the rescue round** (the one allowed extra round, single named fix: make the glow read in 0–5 s). Uncommitted builder edits (make_story.py, set.py, story.json; it changed my jacket colour for the whole story so the gold rim contrasts) are committed as-is in this WIP; not rendered or checked. The fix list:
1. S001/S002 (0–1 s): close-up of me, dim background, warm gold spill on bench/wall, rim clearly brighter than the jacket.
2. S003–S004 under L02: planner's rim lamp-bright vs the guests'; pull S004 back (hair cropped).
3. S005 "STREET" must read outdoors.
4. L02–L04: swap the wind bed for the room bed.

**Next:** finish/verify 1–4 on stills 0–5 s, full `render --preview --force` (jacket changed), finish, mix, flash, preflight, then critic r6 (rescue) on that one fix. If it still fails: drop with a hold line. If it passes: gate, PR, merge, qa on the final.

## Update 2026-11-03 (handed to the second orchestrator)
Stopped before verifying the rescue fix. This container has no Blender, so the 1-4 edits (committed in the WIP) are still unrendered and unchecked. PR #171 (proof.yml) was still open on main at 16:19 UTC. Next: merge main, render stills 0-5 s and a full preview (jacket colour changed), mix, flash, preflight, then critic r6 (one round only; if it fails, drop with a hold line), then the proof and qa on the proof, merge only when qa passes and `test` is green. Don't dispatch render.yml or upload.yml; don't edit queue.txt.

## Update 2026-11-03 (second orchestrator's rescue session): STATUS dropped
Rescue fix worked: critic r6 (0-5 s) **approve**, avg 7.75, nothing under 5; standards r5 approve. Proof run 41721240075 (sha 3a5fb9c) passed its own verdict (craft 0 blocks/0 warns of 32, flash pass, clips pass, -14.0 LUFS / -1.7 dBTP). Proof qa (opus) = **fail**, two separate fixes (qa/ep51-fossil-hall.json):
1. S081, 109.3-111.3 s ("I turn and say it OUT LOUD"): narrator not in frame; a visitor's navy head + gold shoulder fill the frame. Move the visitor's L62 mark off the camera line, or move the camera.
2. S014-S015, 16.2-19.7 s ("Grandpa ABE... BRIGHTEST man in TOWN"): the passers-by (marks moved in the clip fix) stand at the lens, shielding arms fill the centre, Abe is a speck. Push them back/aside.
Minor: eyes shut on frame 0 (blink); S005 planner's arms hide his face.
Rule: only a single small fix (one shot or one cue) may be re-proofed once; this is two fixes over three shots, so dropped, not re-proofed. If the owner ever wants it back: fix 1 and 2 above, merge current main, redraw the proof (~55 min), qa again. Hold line for package.json is the second orchestrator's to record on main (no drop PR from here). PR #199 left open, not merged.

## Update 2026-11-04: revived for one fix
Builder fixed qa's S081 (camera moved, narrator in frame) and S014-S015 (passers-by behind the bench, out of frame). Critic r7 (opus, those shots only): **approve** (S005 7, S014-15 6, S081 6). Advice, not blocking: S081 has a dark block near the mouth (stair beam foot or a head?) for qa to check on the proof; Abe's rim could ramp up ~20% over the S015 push. Gate OPEN, pytest 196 pass. Proof 2 drawing on PR #199; a second qa fail means dropped for good.
