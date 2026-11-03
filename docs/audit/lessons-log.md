# Lessons log (running, from 2026-11-03)

The owner, 2026-11-03: "keep a running lessons log, the goal is that afterward we can audit everything and rewrite our
entire repo to be more streamlined and efficient."

Every entry is something that cost time, runners, usage or a film, with its evidence and the fix it suggests for the
rewrite. The second orchestrator adds entries as they happen. The first orchestrator can add its own under its
initials, or post them on issue #177 for the second to copy in. Times are US Central.

Format: **what happened** (date, evidence) → **cost** → **fix for the rewrite**.

## Render and proof pipeline
1. **A film was assembled from an incomplete set of shards.** Render run 87 (2026-11-03): closing-time's draw shard 2
   never finished, `assemble` ran anyway (`if: !cancelled()`), and `finish` filled the 251 missing frames with copies.
   The film stuttered twice a second and failed final qa (`qa/closing-time.json`, #185).
   → One of today's two uploads lost, and a full redraw (run 92).
   → Assemble only after every shard of that story succeeded, check the frame count before `finish`, and make `finish`
   refuse to fill gaps. #178 adds the first two for render.yml. proof.yml probably has the same gap.
2. **A proof can be planned away and never drawn.** When a newer push that touches no film files replaces a waiting PR
   proof run, the new run only plans. ep55 (#174) and ep42 (#172) sat for hours looking proofed when nothing had been
   drawn (runs 41676785797, 41676773322).
   → About 3 hours on two near-ready stories.
   → Plan from the PR's whole diff, not the latest push, or have `test` say "no proof drawn yet" plainly.
3. **Duplicate and no-op proof runs.** ep48 had its PR proof run (28) and a hand-dispatched one (29) drawing the same
   commit at once, on 8 runners each. ep48 also got four plan-only runs (22, 24, 25, 26) while its reviews were still
   open.
   → 8 runners for about 30 minutes, plus a runner start-up per no-op run.
   → One proof per commit (key the concurrency group on the sha), and no proof trigger until both reviews approve.
4. **Final renders are the throughput limit, not usage or sessions.** The account runs 20 jobs at once. A final takes
   16 shards for about 1.5 to 2 hours a story, two stories a run, so about 12 finals a day at best. Proofs (8 runners)
   compete with finals.
   → On 2026-11-03, 15 to 20 stories queued for finals, about a day and a half of serial drawing.
   → Cheaper finals (fewer samples, smarter shard counts, reusing the proof's frames where they're identical), one
   render queue across stories instead of per-run pairs, and a scheduler that keeps proofs off the final's runners.
5. **Each story's assemble waited for the other story's shards** (moving-day, 2026-11-03). Fixed in #178.
6. **The upload runner had no ffmpeg for the flash re-measure** (#189). mirror-maze's first upload try failed.
   → Every workflow that measures needs the same tool set. Keep one composite "setup" action that all of them use.

## Rules that moved under finished work
7. **The bar changed mid-week, three times in a day:** the craft-metric pace blocks (from 6 PM 2026-11-03), polish
   v2.3 (11:58 AM), and the flash bar twice (#183 published standards, then #186 strobe-only). Proofs drawn hours
   earlier failed bars that changed before the fix landed (ep55 and ep42 failed all four pace blocks, drawn an hour
   before v2.3).
   → Re-proofs, re-measures and messages to every session.
   → Version the bar (one `bar.json` with a version and date), stamp every proof and qa with the version it was
   judged on, and change it at most once a week, between batches.
8. **Openings were redone across the whole queue** after the opening recipe (queue-audit, 2026-11-03), on stories
   already built 5 to 8 rounds deep (ep41, ep49, ep50, ep53).
   → Many sessions of fix rounds. ep41 was dropped after 5 rounds, ep43, ep33 and ep37 earlier.
   → Decide the opening recipe before building. Keep it in one place the writer, critic and qa all read.

## Sessions, handoffs and briefs
9. **Every session reinstalls Blender and the voice engine** (`bash blocky/setup.sh`, 15 to 60 minutes each, sometimes
   in the background while the session polls). There are 20+ sessions a day.
   → Hours of wall time and usage spent waiting.
   → Measured 2026-11-03 at 2:33 PM in the second orchestrator's container: the bpy venv (about 1 GB) installed in about a
   minute, but the TTS venv (torch CPU, Kokoro, faster-whisper) was still at 29 MB after 30 minutes and was stopped. The
   PyTorch index answers in under a second through the proxy, so the stall is in a big wheel download or a model fetch.
   An environment setup script would only move that wait before the session starts, and it would make every session
   wait, writers and research included. So it wasn't added.
   → Cache the TTS wheels and models (a pip wheelhouse or an artifact), or split the voice step out of local builds
   entirely, since proofs and finals voice on Actions anyway. Add a pip `--timeout` so a stall fails fast.
10. **Handoffs pass along untested work in progress.** Most handoffs said "WIP committed as it stood, untested"
    (ep45, ep49, ep50, ep51, floor-thirteen, dryer-nine, ep71). The next session spent its first hour working out
    what was done.
    → An hour per story.
    → A handoff is a checklist with a state per must-fix (done, verified, open), written by a tool that diffs the WIP
    against the review's must-fixes.
11. **Branch names are inconsistent:** `claude/opening-<story>`, `claude/<story>-opening`, `claude/ep53-opening`,
    `claude/ep57-two-windows` for ep71, and two or three stale branches per story.
    → Time spent finding the right branch, and risk of building on the wrong one.
    → One branch per story, `story/<slug>`, with stale branches deleted on merge or drop.
12. **Some handoffs gave orders outside the new ownership** (ep53's said "add the story to queue.txt").
    → Every brief had to override them.
    → Handoffs hold state, never instructions. Ownership lives in one file.
13. **Briefs are 6 to 8 KB each, pasted inline,** for about 25 sessions.
    → Orchestrator output tokens and time.
    → Brief templates in the repo (`.claude/briefs/`), and a session gets "brief: story-fix, story: X".
14. **Sessions treat their orchestrator's follow-ups as peer data.** The render session stopped to ask for
    confirmation before applying a design fix sent by its own orchestrator. The QA desk refused proof qa as outside its
    brief (right by its brief, but slow).
    → An hour on #178, and a re-plan for ep55 and ep42.
    → Write briefs with the likely extensions inside them, and have sessions accept scope changes from the session that
    created them.

## Coordination between orchestrators
15. **Messages wait for a poll.** Issue #177 can't wake a session. #1 reads 3 times a day, #2 hourly. #1's request to
    hold story merges (1:50 PM) was read after #187 merged (2:01 PM). It did no harm, because run 92 had already
    started.
    → Up to an hour of lag on anything time-sensitive.
    → A PR-based inbox that wakes the reader, or one orchestrator with a single queue.
16. **Two accounts with different usage resets were confused** (the second assumed the first's Monday 4 PM reset; its
    own is Thursday 8 AM). Fixed in `docs/operations.md`.
17. **Every comment emails the owner.** The posting rule went from batched to "after everything" in one day.
    → A digest the owner reads once, and the chatty log somewhere that doesn't notify.

## Review loop
18. **Two rounds is the right cap, and the stories that blew through it should have been dropped earlier.** ep41 had 5
    rounds, ep49 7, ep53 4, ep50 4, with the creature or the hook still failing.
    → Most of a day's sessions.
    → Enforce the cap in code (gate refuses round 3), and score the creature test still before any other build work.

## Waste to watch (open)
- Proof runs for stories likely to be dropped. Proof only after both reviews approve, and draw once.
- `test` stays red on every story PR until its proof qa lands, which reads like breakage. Name it "waiting for proof qa".

## From the first orchestrator (2026-11-03)
- **Usage went in a day.** 74% of a week's limit was gone less than a day after the reset: about 60 sessions in 2 days, up to 15 at once, long orchestrator contexts re-read on every check-in, and redo or fix work on stories that were dropped hours later. Rewrite target: decide keep or drop before any fix, one task per session, short-lived sessions, and check-ins only as often as something can change.
- **QA came after the expensive step.** Reviews saw a quarter-size preview drawn every 4th frame, so clipping, stills, flash and pace showed up only on the final (moving-day, ep58, ep62, warm-shoes). proof.yml fixed it. Rewrite target: one gate before merge, measured on the real frame rate.
- **A flash bar copied from another channel blocked transitions.** The ep10 house extras (2 flashes or 5 changes a second) counted fast cuts as flicker and fought the pace rules. The owner watched both "failing" films and saw no flashes. Rewrite target: start from the published standard, and check any stricter rule against what a person sees before it blocks.
- **The uploader trusted a stale reading and a missing tool.** upload.py fell back silently when ffmpeg wasn't on the runner, and refused a film that passed. Rewrite target: a missing dependency fails loudly, and every workflow's tools are installed in that workflow.
- **A failed shard still made a film.** run 87 assembled closing-time with every 16th frame copied (a stutter in the hook). Fixed by the complete-shards guard (#178, #194). Rewrite target: every assemble checks that its inputs are complete.
- **An urgent message read as the owner saying stop.** A `priority: now` send_message interrupted a tool call, and the session took the cancel as the user's "stop" and held for 70 minutes. Rewrite target: use `next` for messages to working sessions, and the session prompt says an interrupt from the orchestrator isn't the owner.
- **Cancelling a drawing run to jump the queue costs more than waiting** once frames can be reused. Rewrite target: render priority comes from queue.txt, never from cancels.
- **One upload slot needed four hops.** QA verdict, then my dispatch, then the workflow, then the issue, with reminders in case a message was missed. Rewrite target: upload.yml runs itself when a qa pass lands for the next queued story inside the day's window.
