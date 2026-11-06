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

19. **Pace is set in the edit but only measured on the drawn film.** The owner, 2026-11-03: "don't we control all of
    this beforehand? like we are the ones that set hte pacing ande veyrthing so i dont understand how we are just
    creating stuff that is bad." We set the cuts and camera keys, but "picture changes" and "motion energy" count how
    much the whole frame changes every 0.5 s and 0.25 s, which depends on how much characters and the camera move
    inside each shot once it's drawn. The preview (quarter size, every 4th drawing) can't measure it, so a builder first
    sees the real number on a 30 to 40 minute proof. ep48 had 7.25 cuts per 10 s, near the 8.0 cap, and still came in at
    12.0 against 12.5. The bar also arrived after most of the queue was built (entry 7).
    → ep48 dropped after two proofs and 16 runners, and a near-miss band added (#201).
    → Predict picture changes and motion energy from the edit before drawing (measure.py already reads the edit for
    the `spec.*` metrics), build to a target with margin (15, not 12.5), and plan acting beats into every shot instead of
    retrofitting punch-ins, which don't count as picture changes.

20. **A change was broadcast before the owner had settled it.** About 4:15 PM, #1 reported the calm-opening fix (#209)
    as the owner's choice, and the second orchestrator messaged about 30 sessions. Within minutes the owner reversed it
    ("I meant that we should be doing the swoosh bc thats what ive seen online"), #209 closed unmerged, and a
    correction went to 41 sessions. The 9 new batch 9 builds had already started with the wrong rule in their brief.
    → About 70 messages, every session woken twice, and a rule in 9 briefs that had to be overridden.
    → Broadcast a rule only once its PR has merged. Better: sessions read the current bar from one file on main at each
    step, so a change needs no messages at all.
21. **Times were guessed, not read from a clock.** The second orchestrator stamped messages "4:40 PM" and "4:45 PM", and
    a #177 post "4:50 PM", when the clock said 4:15 to 4:26 PM. Relayed #1 posts carried times that hadn't happened yet
    either.
    → Times that don't line up, between two orchestrators who coordinate by them.
    → Stamp every post and message from the clock (`TZ=America/Chicago date`), in a script, never by hand.
22. **Long sessions drift from main.** About 10 rule and tool merges landed on main in one day: the flash bar, the near
    band, proof fixes, render lanes. Sessions that started in the morning were judging with old `measure.py`, `qa.md` and
    flash code until the owner asked: "Can we make sure that everything thats running has the latest on main?"
    → A broadcast to every session, and judgments made against stale bars.
    → Every brief has a "merge origin/main" step before each judge step (review, proof, qa, merge). Also, `proof.yml`
    and qa should take their tools from main, not from the branch.

23. **Most drops are the creature, and the test comes too late.** On 2026-11-03, 6 of 10 drops died on the creature,
    with the Opus critic saying "silly": ep80, ep87, ep90, the ep34 revival, ep71 (creature 5) and ep41 (creature 4).
    The notes repeat: warm frontal light, disc or dot eyes, no scale reference, the whole body shown small in a bright
    set, soft boxy shapes. The writer designs a creature the rig can't make frightening, and the creature test only runs
    after a build session has spent its setup.
    → 6 stories and their sessions, and 3 creature tries each.
    → A creature playbook (a lab started 5:10 PM) that the writer applies in the script, and a creature test still made
    right after the script merges, by one cheap session, before any build is started.
24. **A study's top fix was already shipped.** Render-throughput change 7 ("finish on 4 processes") was already in the
    engine since PR #94. The study misread the measured 0.33 s a frame as single-process. A session was spent finding
    that out.
    → One session.
    → A study checks the code path it's measuring (a grep for the worker pool) before it proposes a change.
25. **The orchestrator asserted how a workflow triggers without reading it.** It told #1 that merging the samples change
    would replace the pending render run. render.yml only triggers on `stories/*/**`, so it wouldn't have, and #1 caught
    it.
    → A near-miss: the next finals would have drawn at 10 samples.
    → Read the `on:` block before any claim about what a merge starts.
26. **Small staging fixes made new framing errors.** dryer-nine (S54 black after the pair moved) and ep51 (passers-by at
    the lens after the clip fix) failed on framing that a clip fix introduced, and both were dropped at the round cap.
    → Two near-ready stories (revived 5:10 PM for one targeted fix each).
    → An automated framing check after every staging change: is the shot's subject in frame and unblocked? `measure.py`
    already projects heads for `face_big`, so it can flag a shot where no cast face is visible.

27. **Our own guard threw away complete films.** The "every frame must be there" check (#178, #194) counted PNGs
    against the timeline's frames. A shot on twos draws every other frame and `finish` holds it over the next, so
    every film with a twos shot failed. moving-day was refused twice: run 97 (2,398 of 2,635, exactly its drawings)
    and run 106. The guard was tested only on a synthetic all-ones case.
    → Two moving-day finals, about 16 + 32 runner-hours, and the 7:41 PM slot's backup.
    → Fixed in #222 (`scripts/check_drawings.py` checks each drawing `frame_list` asks for, by name). For the rewrite,
    a guard is tested on a real timeline from main, with twos, before it ships.
28. **Two creature rounds with the playbook didn't rescue a dropped creature.** The lab (#220) and round 2 (#224,
    two critics each) both failed Hal (ep87) and ep71's creature. The playbook moved the critics' words (no more
    "mascot" or "snowman"), but not the scores.
    → Two sessions, and ep87 and ep71 stay dropped.
    → Pick creature concepts the rig can carry, at the writing stage: a person made wrong, or a threat that never
    needs a full creature reveal. Don't spend build sessions trying to rescue a weak creature design.

29. **"Creature-light" still put two full reveals into batch 10, and both failed the creature test.** ep104's dream
    giant (5, 5, 4) and ep106's split Grandma (3 to 4 every try) were "a person made wrong", shown in full. Both
    dropped within 40 minutes of starting, before any voice or preview. The test is cheap, but the scripts were spent.
    → Batch 11 has zero creature tests: nothing frightening is shown in full (a shadow, a hand, a partial shape, the
    effect on people). Move this check to the writing stage, as the plan's step 6 says.
30. **A proof failed flash on a light the builder didn't treat as a light change.** ep97 passed both reviews and its
    rescue, then failed its proof at 7 flashes a second (cap 6) from a closet bulb swinging in frame (S24 to S26).
    → Any swinging, flickering or switching practical light gets a full-rate flash check before reviews, with margin
    (5 a second or under). Batch 10 was told on 2026-11-04. Make `check` flag moving practical lights (plan step 8).

31. **A build session went idle while its proof ran, and nothing woke it.** ep83's proof failed at 10:21 AM, and the
    session didn't look until the orchestrator found it at 12:15 PM. Sessions don't wake on Actions events.
    → Briefs say to wait on runs with a Monitor until-loop, never by ending the turn (docs/briefs/build.md). The
    plan's PR-based inbox (step 9) should subscribe build sessions to their PR's events.

32. **Batch 10's framing pre-check didn't lift the pass rate: 1 merged, 1 still building and 5 dropped out of 7.** Two of the
    drops failed the creature test. The other three failed on single shots framed on the wrong thing: the back of a head, an
    empty wall, a crop of hair over the line it should show, and one sinister `grin` face on a warm beat. The pre-check
    looks at the key beats only, and these shots weren't key beats. Film length isn't the cause: most of the 15 passed
    films are long too.
    → An automated check over EVERY shot: face box size, a head cut by the frame, a back-of-head shot on a line about
    that person, and the line's named object in frame. That is plan step 8 (C + N), the most valuable step left.

33. **A rescue fixed the named shot and missed its twin.** ep108's rescue reframed S40 as the critic asked, but S41,
    the next shot on the same line, kept the same bad framing, so the re-look failed and the story dropped.
    → A rescue applies the fix to every shot of the same line or beat, not just the one the review names. Put this in
    docs/briefs/build.md. The framing lint (scripts/framing.py) should catch the twin before the re-look.

34. **The framing lint missed ep112's three framing blockers.** scripts/framing.py reported 0 findings, but critic r2
    dropped ep112 for a raised hand covering a face (S12), a head cut at the left edge (S20) and the back of a head
    on a line about that person (S26). The second and third are exactly what the lint checks for.
    → Recalibrate framing.py on ep112's branch (claude/batch11-ep112-hide-and-seek): head bounds against the left and
    right edges, and the facing test for a character named in the line, not only the speaker. Add a hand-over-face
    check. This is the first job for plan step 8 after the reset.
35. **ep97's retry fixed the wrong light.** Holding the closet bulb still didn't change the reading: still 7 a second at
    45.13 s. The fix was guessed from the review, not measured.
    → Before fixing a flash fail, find its source frame by frame (`python -m blocky flash` with per-frame luma) and
    name the shot and the light that changes.

36. **The local flash check reads lower than the proof, and it cost three retries.** ep97 (twice), ep107 and ep101 each
    passed `blocky flash` on their preview (about 4 a second) and then failed the proof (5 to 7 a second, or an
    extended run over 4 s). The sources were glows, ring stamps and a lit closet: steady-looking lights that flip
    brightness between frames at full rate.
    → After the reset, the first infra job: run `blocky flash` on a proof artifact and on the matching preview for the
    same sha, find why they differ (frame rate, resolution, polish pass, frames held over), and make the local check
    measure what the proof measures. Until then, a story with a glow or a flipping light needs the proof's numbers
    at 5 a second or under before reviews spend rounds on it.
    → Done 2026-11-05 (#310, merged 2:42 PM): the preview draws every 4th frame and holds it, so lights that flip
    every 1 to 3 frames alias low. Meter size is not the cause. `blocky flash <story> --like-proof` draws every frame
    at the meter's size and reads what the proof reads. The build brief and builder.md now use it, at 5 a second or under.
37. **The framing lint still misses heads cut at the frame edge and mouths in the caption band.** ep115 reported 0
    findings but had five heads cut at the left edge and a mouth inside the caption band; ep112 the same (lesson 34).
    → Plan step 8's recalibration adds a caption-band check (a mouth inside the bottom 62 to 70 percent of the
    height) and tests the head box against all four edges on ep112's and ep115's branches.

38. **Review rounds don't converge: each critic round finds new shot problems.** ep120 fixed all 10 r1 must-fixes, and
    r2 found 3 new ones. ep117 fixed 7, and r2 found 2 new ones. ep115, ep112 and ep103 show the same pattern. With
    about 100 shots a story, a reviewer samples different shots each round, and two rounds plus one rescue can't
    close the gap. Batch 12 so far: 0 merged, 5 dropped.
    → Proposal for the owner and #1 (it touches critic.md and the round rules): round 1 walks EVERY shot and lists
    every must-fix it can find. Round 2 checks only those fixes and any regressions. A new, non-severe finding in
    round 2 becomes a should-fix, not a block. Pair it with the framing lint so mechanical misses never reach a
    reviewer.
    → Done 2026-11-05: the owner said "yes, do the review change" (RULES decision 8; critic.md, standards.md, the week skill and the build brief).
39. **The same engine defaults keep killing stories** (blocky/, #1's). In the last 24 hours:
    - the rule tag sits at a fixed 1.0 m from the camera, so it vanishes in close-ups or lands over a face (ep120, ep116, ep111, ep112);
    - fill lights fade in over 0.3 s after a cut, so the shot opens dark (ep120);
    - characters pose on frame 1, so frame 0 pops on the loop (ep116);
    - camera moves can end inside walls, leaving blank frames (ep120, moving-day);
    - the caption splitter drops spoken words (ep115).
    → One engine PR per default, for #1 to merge: the tag placed relative to the camera's near plane and clear of
    faces, cut-aligned light cues with no fade-in at a cut, the pose applied on frame 0, a camera-in-geometry check in
    preflight, and the caption splitter keeping all words. Each fix removes a whole class of drop.

40. **Proof qa finds what the critic didn't, and by then no round is left.** ep105 (blank frames at S85 and S139), ep116
    (frame-0 pop and a head cut) and ep121 (four fixes) all had critic and standards approval, then failed proof qa.
    Several of the misses are mechanical: blank or near-uniform frames, a character missing on frame 0, a head cut
    at an edge.
    → A frame lint over the preview (scripts/, report-only, like framing.py) before reviews: near-uniform frames,
    frame 0 against frame 1 for a pop, and the head-cut check on the rendered frames, not just the geometry. And the
    proposal in lesson 38 applies to qa too: the proof qa's checklist runs once on the preview, so the critic sees a
    clean film.
    → Done 2026-11-05: scripts/frames.py (#307) and the frame-0 pose fix (#308).

41. **A full `flash --like-proof` can take more than 30 minutes, and a background task with the default timeout is
    killed before it measures.** ep118's first run drew all 1145 frames and was killed at the 30-minute limit, so it
    had to be run again (2026-11-05).
    → Run the first full one in the background with a 2 h timeout. After a fix, re-check only the changed shots with
    `--like-proof --shots S12,S13`, which keeps the other drawings. The build brief says so.

42. **Small props that must read as a particular shape at phone size keep spending the last round.** ep118's retry
    passed everything but the S12b squirrel (a fist, then a bent pipe at 300 px), and ep117's discs read as stickers
    and its moths as blades (2026-11-05). Each was one small object the critic had to be able to name.
    → The writer avoids such props (batch 13 note 3). In a fix round, cut or replace a prop that fails to read once,
    rather than refining it: a second try at the same shape rarely lands.

43. **The craft numbers read differently at each stage, and each gap cost a round (calibrated 2026-11-06).** ep126's
    proof read a longest still of 0.8 s and its final 1.07 s (a block). ep117 passed its local measure and its proof
    read 12.5 picture changes per 10 s at 0.25 s against 14. Measured on every story with a live `proof-` and
    `film-` artifact of the same film files and engine (7 pairs; the proof's sha has no film-file and no `blocky/`
    or `assets/` change before the final's), re-run with `scripts/measure.py`, which matched each proof's own
    `craft.json`:

    | story | changes/10 s at 0.5 s | at 0.25 s | motion energy | longest still |
    |---|---|---|---|---|
    | moving-day | 13.7 / 13.7 | 14.6 / 14.8 | 7.25 / 7.25 | 0.80 / 0.80 |
    | ep102 | 16.9 / 16.9 | 25.1 / 25.1 | 9.13 / 9.16 | 0.27 / 0.27 |
    | ep108 | 17.7 / 17.7 | 24.2 / 24.4 | 8.77 / 8.80 | 0.00 / 0.00 |
    | ep110 | 14.7 / 14.7 | 17.0 / 17.1 | 6.50 / 6.50 | 0.53 / 0.53 |
    | ep114 | 17.0 / 17.0 | 23.0 / 22.8 | 8.87 / 8.83 | 0.27 / 0.27 |
    | ep117 | 15.2 / 15.2 | 16.8 / 17.0 | 6.87 / 6.86 | 0.27 / 0.27 |
    | ep126 | 12.8 / 12.8 | 14.6 / 14.5 | 5.70 / 5.66 | **0.80 / 1.07** |
    | final − proof | 0.0 (all 7) | +0.03 (−0.2 to +0.2) | 0.00 (−0.04 to +0.03) | 0 on 6, +0.27 on 1 |

    (proof / final.) The proof and the final read the same: resolution, the polish pass, the encoder and
    measure.py's own downscale add nothing that shows (both are cut to the same 108 x 192 and 18 x 32 grid, and the
    frame counts match). The one gap is **render noise at the still threshold**: the proof draws 4 samples at
    270 x 480 and the final 6 at 540 x 960, so a quiet 0.25 s step reads about 0.5e-3 higher on the proof (median;
    up to 2.5e-3) against the still threshold of 6e-3. ep126's quiet span at 53 s had one step at 6.6e-3 on the proof
    and 5.5e-3 on the final, so its still was split on the proof and whole on the final. The still moves in 0.27 s
    steps (8 frames), so one step is the difference between 0.8 s (passes) and 1.07 s (blocks).
    ep117's gap was a different one: the build brief's `measure.py --story` had **no film**, and with no film the 4
    craft blocks were silently left out ("0 block"). Its failing proof (9695bc5, 12.0 / 12.5 / 6.09 / 0.53) reads
    13.0 / 12.5 / 6.09 / 0.53 when held every 4th drawing like the preview (the preview and the proof draw at the
    same size and samples), so measuring the preview would have caught it.
    → Done 2026-11-06 (#332): `measure.py --story` measures the preview film when there is one, and the 4 blocks
    read `unmeasured` (counted as blocked) when there is none. A new warning, `longest_still_q_edge_s` (the still
    at a 10% looser threshold), reads 1.6 s on both of ep126's films and equals the plain reading on the other 6
    pairs: over 1.0 s on a proof means the final may block. The build brief's measure step has the margins.
    → Engine side (for #1, not done here): drawing the proof at the final's 6 samples, or denoising it, would make
    its quiet steps read like the final's. Until then the edge warning stands in.

44. **A shard start saw a different scene from a continuous run, and only the final showed it (2026-11-06).**
    ep117's final failed qa: in S02, frames 48 to 63, Dad's moustache and Mom's earring floated in the air while Mom
    and Dad were hidden. Its set.py made those extras in `_first_frame()` on the first `animate` call of each render
    process (guarded by `W["inited"]`). Each final shard is fresh processes: `--shard k/32` keeps frames[k::32] and
    the engine's 2 workers split that again, so the 64 processes start at the first 64 drawn frames. A process that
    started after the hide made the extras afterwards, visible. The proof's 8 shards never started there. 15 set.py
    files used the same lazy pattern.
    → Done 2026-11-06: `scripts/shardcheck.py --story stories/<story>` (report-only) poses every process start two
    ways through bl_story's own `main()` without drawing (a fresh process at that frame, and one process over the
    frame list from frame 0) and compares hide_render, world location (1 mm), scale, emission strength and light
    energy per object. About 30 s a story. The build brief runs it before the proof; fix every difference. The
    fix in a set.py: make extras in `build()`, or set every object's state from `t` on every call, never only on a
    change.
    → Done 2026-11-06 (#351, merged 9 AM Fri): the engine hides any object a story's `animate` creates under a hidden
    cast root on the frame it's made. Shardcheck failures went from 16 stories to 3 (carried state in ep117, ep48,
    ep55), and frame-0 floats from 15 stories to 0. A blanket "hide every child of a hidden object" erased parts
    stories show on purpose (POV gloves, shoes), so the rule is narrow. Of the finals drawn before it, the QA desk
    viewed frames 0 to 63 of all 14 flagged: only ep102's frame 0 showed it (Clem missing), and it gets a redraw.

45. **One runner in 32 had an empty apt mirror list, and the whole render failed on that shard (2026-11-05/06).**
    Render runs 42144845576, 42152717471 and 42217922531 each lost one draw shard at the apt step: `E: Unable to
    locate package libegl1`. The failing runner's `apt-get update` fetched only packages.microsoft.com; a passing
    runner on the same Ubuntu 26.04 image also fetched azure.archive.ubuntu.com through `/etc/apt/apt-mirrors.txt`.
    The other lane's story still assembled, but the run read "failure", so the QA desk skipped ep117's good final
    for hours.
    → Done 2026-11-06 (#335): every apt step in every workflow retries update and install 3 times, 20 s apart. The
    QA desk checks a story's final whenever its own assemble job passed, even if the run failed.

## Waste to watch (open)
- Proof runs for stories likely to be dropped. Proof only after both reviews approve, and draw once.
- `test` stays red on every story PR until its proof qa lands, which reads like breakage. Name it "waiting for proof qa".

## Creature round 2 (2026-11-03, second orchestrator)
- Two creature tries each for Hal (ep87) and the Server (ep71), each judged by two Opus critics: best 5/4 and 4/4, neither passed (`docs/research/creature-round-2.md`). Cost: 4 builder runs (the ep71 one about 28 min) and 8 critic reads. Suggested fix: a wide-slab head reads as an appliance whatever the design, so send such creatures back to the writer before any build try; and a builder should self-check the two scale facts (head against a lit ceiling, the reference person's whole head in frame) before reporting.

## From the first orchestrator (2026-11-03)
- **Usage went in a day.** 74% of a week's limit was gone less than a day after the reset: about 60 sessions in 2 days, up to 15 at once, long orchestrator contexts re-read on every check-in, and redo or fix work on stories that were dropped hours later. Rewrite target: decide keep or drop before any fix, one task per session, short-lived sessions, and check-ins only as often as something can change.
- **QA came after the expensive step.** Reviews saw a quarter-size preview drawn every 4th frame, so clipping, stills, flash and pace showed up only on the final (moving-day, ep58, ep62, warm-shoes). proof.yml fixed it. Rewrite target: one gate before merge, measured on the real frame rate.
- **A flash bar copied from another channel blocked transitions.** The ep10 house extras (2 flashes or 5 changes a second) counted fast cuts as flicker and fought the pace rules. The owner watched both "failing" films and saw no flashes. Rewrite target: start from the published standard, and check any stricter rule against what a person sees before it blocks.
- **The uploader trusted a stale reading and a missing tool.** upload.py fell back silently when ffmpeg wasn't on the runner, and refused a film that passed. Rewrite target: a missing dependency fails loudly, and every workflow's tools are installed in that workflow.
- **A failed shard still made a film.** run 87 assembled closing-time with every 16th frame copied (a stutter in the hook). Fixed by the complete-shards guard (#178, #194). Rewrite target: every assemble checks that its inputs are complete.
- **An urgent message read as the owner saying stop.** A `priority: now` send_message interrupted a tool call, and the session took the cancel as the user's "stop" and held for 70 minutes. Rewrite target: use `next` for messages to working sessions, and the session prompt says an interrupt from the orchestrator isn't the owner.
- **Cancelling a drawing run to jump the queue costs more than waiting** once frames can be reused. Rewrite target: render priority comes from queue.txt, never from cancels.
- **One upload slot needed four hops.** QA verdict, then my dispatch, then the workflow, then the issue, with reminders in case a message was missed. Rewrite target: upload.yml runs itself when a qa pass lands for the next queued story inside the day's window.
