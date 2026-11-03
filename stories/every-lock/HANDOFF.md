# every-lock: handoff (2026-11-03, about 10:45 AM Central, handed to the second batch-6 orchestrator)

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
