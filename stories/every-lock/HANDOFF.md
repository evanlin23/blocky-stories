# every-lock: STATUS dropped (2026-11-04, second orchestrator's story session)

Dropped after review round 2 (the last allowed round). No PR was opened. Branch `claude/p5-lock-doors` holds everything, pushed.
The second orchestrator records the drop on main.

## Verdicts
- Round 1: critic revise (avg 6.1), standards revise.
- Round 2: critic revise (avg 6.6; hook 8, narrator 9, appeal 9, twist 6, sound 7, faces 4, lore 3), standards revise.
- Checks at the end: flash passes (strobe bar), preflight 0 blocks, clipcheck 0, measure 0 block / 0 near / 1 warn, check passes.

## Open must-fixes
Standards r2:
1. S046 (L23 second shot, 48.6-49.6 s): blank pale wall, then a black void, then a hard cut to the bright hall. It is the flash peak (7 changes/s). Aim it at Jade and me at the table.
Critic r2:
1. Meter cropped at L61, 114.5-115 s.
2. Heads cut off at 31.5, 58-59, 64.5, 109.6, 117 and 128 s.
3. Blank or black frames: L12 27 s (Jade not shown), L17 38.5 s, L46 89.5 s (black), L55 104 s, L58 tally 110-110.6 s (white then black), L65b 123 s.
4. L71.2 at 135 s: Dale's front door being pushed is not shown.
Faces (4) and lore (3) stayed low in both rounds.

Files: stories/every-lock/reviews/r1-*.md, r2-*.md. Package: title "My Bathroom Door Has 1,024 LOCKS", opening "count", L01 "ELEVEN SLAMS, and YOUR door has ONE THOUSAND and twenty-four LOCKS."

---

# every-lock: handoff (2026-11-04, review round 1 fixes applied)

## Where it stopped (latest)
- **Branch:** `claude/p5-lock-doors`. Round 1 (critic + standards) fixes are in; preview redrawn, finished, mixed.
- **Done:** L01/L72 re-voiced (L01.3 shot ref); sound events cut to 3.8 per 10 s (meter clicks and door marks off, night
  clicks thinned, `marks: false`; also teleport cuts no longer make a phantom burst of footsteps, see `endat` in
  make_story.py); meter drawn 8 cm from the lens, narrower, so it is whole on every frame; `headfit` widens or backs
  off every camera so heads stay in frame (and keeps hall cameras off the walls); cooler shot moved inside the kitchen
  and lit (`dk_c`); L13 clock widened; L53/L55/L58 hinge and tally shots cleared and tally strokes enlarged; curtain
  darkened; Jade night fill light (`h_jfill`); L71.1 shows the pile pushing Dale's front door; L05 dolly shortened so
  flash at 10 s reads 3 (was 6).
- **Checks:** flash PASS (3f max 3/s), preflight 0 blocks, clipcheck 0, measure 0 block 0 near (cuts/10s 9.19 warn only).
- **Next:** critic/standards round 2, then PR, proof, qa. Stale frames in `frames-preview` corrupt flash readings
  (a re-render after a timeline change leaves old frames): move any file older than the render out before `finish`.


## Where it stopped (latest)
- **Branch:** `claude/p5-lock-doors`, pushed, with main merged in, including polish v2.1 and the proof workflow (proof.yml, PR #171). **No PR is open.**
- **Flash:** still unmeasured after the kitchen-wall fix. The clean preview render was stopped at 1079 of 1083 frames.
  Those frames were drawn with the pre-merge polish.py, so don't use them: delete `out/work/every-lock/frames-preview`
  and draw the preview again from scratch.
- **Reviews:** none run. Two review rounds are allowed from here.
- **Proof run:** none. **qa:** none.
- **Next:** clean preview, then `flash` (with a clear margin under the house bar). Then critic and standards round 1,
  then open the PR. Proof runs on the PR (or dispatch `proof.yml`), then qa at `"stage": "proof"`, then merge once
  `test` is green. List intended overlaps in `"clip_ok"`. Report verdicts to the batch lead.

## Earlier state (10:30 AM Central)

Batch 6, slot P5 (what-if escalation, experiment, long arm). Branch `claude/p5-lock-doors`. **No PR yet, not merged.**
Stopped at the lead's request (usage limit). Per the lead: don't merge, even once approved, until the proof-render
process (a PR from the proof session) is in.

## State
- **Package:** title "My Bathroom Door Has 1,024 LOCKS 🔒", `"lane": "experiment"`, `"opening": "count"`. Lints clean.
- **Opening:** L01 "Our bathroom door has one thousand and twenty-four locks." L02 "Every time it shuts, they double."
  (count opening from docs/research/opening-variety.md, approved by the lead). Quotable line: "The locks NEVER come
  OFF. But the DOOR DOES."
- **Pre-build checks:** cold-viewer test run, and its confusions fixed in the writer's round. The blind premise check
  scored 6 on the first draft. After one rewrite it scored 7, equal to the real hits' median of 7.
  The current L01 (count opening) came later and has not been blind-checked.
- **Build:** polish v2 on (`look.polish: true`, hints added), main merged. Cameras were pulled back so no shot is a
  solid colour, and the meter shows only powers of two. Whisper word block cleared. `preflight` shows 0 blocks.
  `check` passes, with a warning that 4 captions are on screen under 0.2 s. `scripts/measure.py` gives 2 warnings
  (character motion 0.45, cuts per 10 s 9.2).
- **Preview on disk:** `out/work/every-lock/every-lock-preview.mp4` (137.9 s). It's the second-to-last render, made
  before the kitchen walls were darkened. A clean re-render with that fix was about 800 of 1083 frames in when the
  session stopped. `out/` is not committed.

## Open must-fixes
1. **Flash:** the preview fails the house bar on `general_3f` (6 flashes/s against 3, 13 changes/s against 6) at about
   8.3 s, the cut from the dark downstairs kitchen to the fridge shot. The other criteria pass. Commit 7740875 darkens
   the kitchen walls for this, but that render hasn't been measured. If it still fails, soften the cut, for example by
   matching the brightness of the two shots or bridging with a slower move.
2. Re-check frame 1 after the camera changes: it should be the 1,024-lock door, centred, pushing in.
3. Make a stills or contact sheet of the current version.

## Review verdicts
None yet. Critic round 1 and standards round 1 haven't run.

## Next step
Delete `out/work/every-lock/frames-preview` (stale frames corrupt the flash readings). Then re-render the preview,
`finish`, `mix`, and `python -m blocky flash every-lock --file out/work/every-lock/every-lock-preview.mp4`. Once flash
passes with margin, run critic round 1 and standards round 1, at most two rounds plus one rescue. Then `gate`, PR,
merge (after the proof-render PR is in), qa on the final film, queue.txt, and report to the lead.

## Clip/asr fix round (2026-11-03)
Cleared all clip rows: S032 racers spread to x +-0.4, me stepped back at L47.2, pile clearings (`MEHOLE`) around me at
L51.1/L54/L56, L67.1 me x 0.03 and Jade x 0.67. asr: spoken L57 is "i pull the bottom two out." (caption unchanged,
split into two chunks). Preview redrawn from S087 on plus S032; flash passes; preflight 0 blocks; clipcheck 0. Main merged.
