# Audit and rewrite plan (2026-11-04)

The owner, 2026-11-03: "keep a running lessons log, the goal is that afterward we can audit everything and rewrite our
entire repo to be more streamlined and efficient."

This is the plan, not the rewrite. It is built from the 28 entries in `docs/audit/lessons-log.md`, the five extra
entries at the end of `docs/research/render-throughput.md` (its 19 to 23, here R19 to R23), the research notes, the
rules, the operations doc, the agents, the workflows and issue #177. Times are US Central. Numbers are from 2026-11-02
to the morning of 2026-11-04 unless a line says otherwise.

## 1. What the system does today, in one page

### The path from idea to uploaded video

| # | Gate | Owner | Wall time | Cost | What fails here |
|---|---|---|---|---|---|
| 1 | Research note (`docs/research/<date>-week.md`) | orchestrator + research session | 1 to 2 h a batch | 1 session | rarely fails |
| 2 | Writer: batch of scripts, plan, package; cold-viewer and blind premise checks | writer agent | 1 to 2 h a batch | 1 session + 2 fresh agents per script | weak premise, a creature the rig can't make scary |
| 3 | Creature test still | builder (inside the build session) | 20 to 40 min, **after** setup | setup 15 to 60 min + 1 to 3 tries | **6 of 10 drops on 2026-11-03** |
| 4 | Build: set, story.json, voice, check, preview | builder (Sonnet), one session per story | 1 to 3 h | setup 15 to 60 min per session | crashes, stale main |
| 5 | Critic (per story) and standards (per batch) | critic, standards | 20 to 40 min a round | 2 agents a round | hook, creature, pace, staging |
| 6 | Fix rounds (cap 2, plus one rescue) | builder, writer | 1 to 2 h a round | a fresh builder each round | cap broken often: ep41 5, ep49 7+, ep53 4, ep50 4 |
| 7 | Proof (`proof.yml`, half size, every drawing) | Actions | about 40 min | 8 runners, about 165 runner-min | plan-only runs, duplicates |
| 8 | Proof qa (`qa/<story>.json`, stage proof) | qa agent, fresh session | 20 to 30 min | 1 session | pace (picture changes, motion energy), framing, flash |
| 9 | Merge (`test` = `gate --merge`) | the story's session | waits behind render jobs for `test` | about 8 runners shared | red until proof qa lands |
| 10 | Final (`render.yml`, 32 shards, 2 stories a run) | Actions, dispatched by #1 | 45 min to 2 h a story | 350 to 1,400 runner-min, about 950 typical | lost shards, guards, flash |
| 11 | Final qa (stage final) | qa agent (#2 for its stories) | 15 to 30 min | 1 session | flash, stutter, pace on pre-proof stories |
| 12 | Queue (`queue.txt`) | first orchestrator | hours (read 3 times a day) | messages on #177 | ordering rules in comments |
| 13 | Upload (`upload.yml`, cron-job.org 6:47 AM, 2 a day max) | Actions | minutes | 1,600 API units | missing ffmpeg once (#189) |
| 14 | Publish (private, scheduled 4:00 PM) | YouTube, owner watches | n/a | n/a | n/a |

### The numbers that matter

- **Throughput today:** 8 stories uploaded ever (`uploads.json`). 14 passed films are waiting to upload (#177, 8:12 AM
  2026-11-04), which covers the week to Monday Nov 9 with two spare. Finals were the limit on 2026-11-03 (15 to 20
  stories waiting); after the lane fixes (#202, #203, #222) one run drew 64 shards in about 45 min.
- **Drops:** about 25 kills recorded in `stories/ideas.md`. On 2026-11-03 alone, 10 drops: 6 on the creature (ep80,
  ep87, ep90, the ep34 revival, ep71, ep41), 2 at round 2 (ep71, ep84), ep41 after 5 rounds, and earlier the queue audit
  dropped ep31, ep32, ep33, ep36. Seven redo sessions (ep23, 25, 30, 31, 32, 33, lookout) and six opening fixes were
  spent on stories that dropped within hours. ep58's revival dropped at proof on 2026-11-04.
- **Sessions:** about 60 started in two days, up to 15 at once (the budget rule says 5). 74% of #1's week was gone a day
  after its reset. #2 is at 66% before its Thursday reset.
- **Setup:** `bash blocky/setup.sh` takes 15 to 60 minutes a session. The bpy venv installs in about a minute; the TTS
  venv (torch, Kokoro, faster-whisper) is the stall (still 29 MB after 30 minutes, entry 9).
- **Runner waste:** about 7,300 runner-minutes thrown away on 2026-11-03 (cancels, a redraw after one lost shard, 3
  finals that failed flash), plus about 48 runner-hours on moving-day from a guard that miscounted twos (entry 27).
  That is 7 to 10 finals' worth on the day finals were the bottleneck.
- **Messaging:** 61 comments on #177 in 22 hours, each one an email to the owner. #1 reads 3 times a day, #2 hourly, so
  anything urgent waits up to 6 hours one way. One rule change (entry 20) cost about 70 messages to sessions.
- **Rules:** the bar changed 4 times on 2026-11-03 (pace blocks, polish v2.3, flash bar twice), plus the opening
  recipe, plus a reversed opening rule (#209). About 10 rule or tool merges landed on main in one day.

## 2. Where the waste is, ranked

Ranked by cost on 2026-11-03. The lessons are grouped into seven root causes.

| Rank | Root cause | Lessons | Evidence | Cost |
|---|---|---|---|---|
| 1 | **Gates come too late.** The creature, the pace and the framing are judged on built or drawn work, when the decision could be made on the script or the edit. | 18, 19, 23, 26, 28, round 2 note | 6 of 10 drops were the creature, found after a build session paid setup. ep48 hit 7.25 cuts/10 s and still missed pace on a 40-minute proof. dryer-nine and ep51 failed framing a clip fix made. | Most of a day's sessions; 3 creature tries a story; 2 proofs and 16 runners for ep48 |
| 2 | **Rules move under finished work.** The bar lives in many files (RULES.md, qa.md, critic.md, measure.py, proof_report.py) and changes mid-week. | 7, 8, 20, 22, 25 | Bar changed 4 times in a day. ep55 and ep42 failed pace blocks that arrived an hour after their proof. Openings redone on stories 5 to 8 rounds deep. #209 broadcast then reversed. | Re-proofs, re-measures, ~70 messages, drops (ep41, ep43, ep33, ep37) |
| 3 | **Render waste.** Drawn frames thrown away, duplicate and no-op proofs, finals drawn before anything judged them. | 1, 2, 3, 4, 5, R19 to R23 | 7,300 runner-min lost; closing-time stuttered from a missing shard; 3 flash fails after full finals; ep55 and ep42 sat 3 h "proofed" with nothing drawn; ep48 drawn twice at once. | 7 to 10 finals; 3 h on two near-ready stories |
| 4 | **Too many sessions, each paying setup.** 20+ sessions a day each install Blender and TTS; long sessions carry huge contexts; sessions kept alive after their job. | 9, 13, operations "usage limit" | 15 to 60 min setup each; 74% of a week in a day; briefs of 6 to 8 KB pasted to ~25 sessions. | Hours of wall time and most of the usage limit |
| 5 | **Two orchestrators and slow messaging.** Two owners, two usage resets, a polled issue as the only channel. | 12, 14, 15, 16, 17, 21 | #1's hold request read after the merge it meant to stop. Wrong reset assumed. Guessed timestamps. Every comment emails the owner. Sessions refused their own orchestrator's follow-ups. | Up to 6 h lag; owner inbox noise; an hour on #178 |
| 6 | **Handoffs and branches carry no clear state.** | 10, 11, 12 | 7 handoffs said "WIP, untested". Branch names in 4 shapes, 2 to 3 stale per story. ep53's handoff gave orders outside its owner. | About an hour per story per handoff |
| 7 | **Guards and studies not tested on real data.** | 6, 24, 25, 27 | The frame guard was tested only on an all-ones case and threw away moving-day twice. A study proposed a fix shipped since #94. The upload runner lacked ffmpeg. | ~48 runner-hours; a session; a failed upload |

## 3. The target design

The aim: **decide early and cheaply, judge once against one versioned bar, draw each frame once, and keep state in
files, not in messages.** Each candidate below says what it replaces, what it saves, its risk and its effort.

| Change | Replaces | Saves | Risk | Effort | Verdict |
|---|---|---|---|---|---|
| **A. One `bar.json`, versioned.** Every number a gate checks (pace blocks and near band, flash, loudness, length split, opening recipe, round cap, creature checklist). `measure.py`, `proof_report.py`, `gate.py`, qa, critic and writer read it. Each qa file stamps `bar_version`. A change bumps the version, lands by PR, and applies to stories whose script merges after it. | Numbers scattered over RULES.md, qa.md, critic.md and code; broadcasts | Root cause 2: re-proofs and the ~70-message broadcasts | Grandfathering needs a clear rule; a bad bar still ships fast | medium | **Do.** Top value. |
| **B. Concept and creature gate at the writing stage.** The writer fills a creature card (from the playbook: no disc eyes, scale reference, no full reveal in a bright set, "a person made wrong" preferred). One cheap session makes the creature still right after the script merges, before any build. Fail twice, the script goes back or dies. | Creature test inside the build session | Root cause 1: 6 of 10 drops found before setup and build | The still needs Blender (one cached setup) | medium | **Do.** |
| **C. Pace predicted from the edit.** `measure.py` already reads the edit for `spec.*`. Add predicted picture changes and motion energy from the camera keys, acting beats and cuts, and fail `check` below target plus margin (15 against 12.5). Calibrate against the proofs already drawn. | Pace first seen on a 40-minute proof | ep48-type drops; a proof per miss | Prediction error; needs a calibration set | medium | **Do**, after A. |
| **D. Proof-gated finals as the default.** `REQUIRE_PROOF: "true"` once moving-day is through, then delete the flag. | Finals drawn before judging | ~1,500 runner-min a day of flash fails; final qa becomes a short confirm | Pre-proof stories stuck (only moving-day left) | small | **Do now.** |
| **E. One proof per commit, only after both reviews approve; plan from the PR's whole diff.** | Plan-only runs, duplicates, "proofed" with nothing drawn | 165 runner-min per duplicate; 3 h stalls | Low | small | **Do.** |
| **F. Guards tested on real timelines, with twos.** A fixture set of 3 real stories from main (one on twos, one polish, one short), with their `frame_list`. Every render or proof guard runs against them in `test`. | Synthetic-only tests | Entry 27 (48 runner-hours) | Fixture upkeep | small | **Do.** |
| **G. A setup cache, or voice only on Actions.** Local builds use the committed word timings (tests already do); the voice runs only on Actions. Cache the bpy venv (an artifact or wheelhouse); pip `--timeout`. | `blocky/setup.sh` TTS install in every session | 15 to 60 min per session, 20+ a day; the stall | A builder can't hear its own line timing until the proof | medium | **Do "voice only on Actions"**; cache bpy only if it still costs over 5 min. |
| **H. Brief templates in the repo (`.claude/briefs/`).** `story-build`, `story-fix`, `proof-qa`, `final-qa`, `creature-still`, `research`. A session gets "brief: story-fix, story: X". Each brief lists its likely extensions and says to accept scope changes from the session that made it. | 6 to 8 KB pasted briefs | Orchestrator tokens; entry 14 refusals | Templates drift from rules (they reference `bar.json`, never copy it) | small | **Do.** |
| **I. One branch per story, `story/<slug>`.** Deleted on merge or drop by a workflow. | 4 naming shapes, stale branches | Entry 11 search time and wrong-branch risk | None | small | **Do.** |
| **J. Handoffs as state checklists.** `python -m blocky handoff <story>` writes `stories/<s>/STATE.json`: each must-fix with done, verified or open, the last proof sha, the bar version. No instructions. | Free-text HANDOFF.md | About an hour per handoff | Must-fix ids must be stable in reviews | small | **Do.** |
| **K. One queue, one owner, and an inbox that wakes.** One orchestrator owns `queue.txt` and dispatches. Work requests are PRs or labeled issues on a PR the reader subscribes to (PR events do wake a session). Ordering rules move from comments in `queue.txt` to checks in code. | Two orchestrators polling #177 | Root cause 5: up to 6 h lag, conflicts, wrong-reset errors | Losing the second usage pool if it means one account | medium | **Do one owner of the queue**; keep a second account only as spare capacity (see question 1). |
| **L. A digest for the owner.** One daily issue (or one edited comment) with uploads, drops, the meter and anything needing the owner. The chatty log goes to a file or a non-notifying place. Every stamp comes from a clock script (`TZ=America/Chicago date`). | A comment per action | Owner inbox; entry 21 bad times | The owner may want live detail | small | **Do.** |
| **M. Round cap in code.** `gate` refuses review round 3 unless a `rescue: <one fix>` line is in STATE.json; a second rescue is refused. | A cap only in prose | ep49's 7+ rounds, ep41's 5 | Kills a story one fix from good (the rescue round covers it) | small | **Do.** |
| **N. Framing check after every staging change.** `measure.py` already projects heads; `check` flags a shot with no cast face in frame or a subject behind geometry. | Framing found at proof | dryer-nine, ep51 | False alarms on deliberate empty shots (an opt-out per shot) | medium | **Do**, after C. |
| **O. Judge from main.** `proof.yml` and qa take `blocky/`, `scripts/` and `bar.json` from main, not the branch. | "Merge main before judging" broadcasts | Entry 22 | A branch that changes the engine must merge that first | small | **Do.** |
| **P. One render queue of frame chunks and a per-shot frame cache.** A scheduler hands chunks of about 60 drawings from every ready story to free lanes; a cache keyed per shot by its inputs so a one-shot fix redraws one shot; finish inside the chunks. | Two-story runs, full redraws on any fix | Most of a final on every fix (moving-day drawn 3 times, closing-time and mirror-maze twice) | The biggest code change; cache keys must be complete | large | **Later.** Lanes are no longer the limit once D and E land. |
| **Q. One composite setup action** used by every workflow (ffmpeg, Python, fonts). | Per-workflow installs | Entry 6 | None | small | **Do.** |

**Weighed and not taken now:** a setup script for the cloud environment (it makes every session wait, research too;
entry 9). Shard counts by length (about 0 gain, render-throughput change 10). Fewer samples and twos for slow pushes are
already in progress through the engine A/B, so they are not in this plan.

## 4. What to delete

Check each against `uploads.json` and `queue.txt` first: never delete an uploaded or queued story.

| What | Why | Note |
|---|---|---|
| Dropped story folders: ep41, ep80, ep84, ep87, ep90, ep71 (if present), ep23, ep25, ep30, ep31, ep33, ep36 and any other line marked killed in `stories/ideas.md` that still has a folder | The /week rule says delete on drop; they stay and slow `check`, originality reads and tests | Keep the "killed: why" line in ideas.md. Revivals (ep26, ep32, ep43, ep46) stay until they drop or ship. |
| The `musicbox` voice in `blocky/sound.py` | Breaks hard rule 6 (ep89's proof 1). `checks.py` already blocks it, so it is dead code with a guard | Delete the voice, keep the check message for a while |
| `blocky/dialart.py` | One story's art (ep45) in the shared engine | Move into `stories/ep45-bee-yard/` |
| The `REQUIRE_PROOF` flag | Becomes always on (D) | After moving-day |
| `look.polish` opt-in and the non-polish path | 20 stories use polish, 23 don't; the docstring says it should become the default | Make it the default for new stories; keep the old path only while unpolished stories still wait to upload |
| `ones: "moving"` as written | Doubles drawings (R22) | Replace with the A/B result |
| 17 story folders with no `story.json` | Script-only or older formats | Either built, on hold with a STATE.json saying so, or deleted |
| Root `HANDOFF.md` (an ep62 note) and the 10 per-story `HANDOFF.md` | Replaced by STATE.json (J) | Convert open ones first |
| `actionlint_py-1.7.12.25.tar.gz` at the root and `legacy/knock-back.mp4` | Binaries in a public repo | Fetch actionlint in `test`; the uploaded film is on YouTube |
| `brand.yml` and `scripts/brand_scan.py` | The rename is done (2026-11-03) | Keep the research note |
| `scripts/plan_renders.py` + `render_plan.py`, and `test_plan_renders.py` + `test_render_plan.py` | One concern in two files and two tests | Merge into one module and one test |
| Duplicate bar checks in `measure.py`, `proof_report.py`, `qa.md` and `critic.md` | Replaced by `bar.json` (A) | |
| `docs/second-team.md` and the two-orchestrator sections of `docs/operations.md` | Replaced by one queue owner and the digest (K, L) | Only if the owner picks one orchestrator |
| Dated research notes older than two weeks (`docs/research/2026-11-0*`) | 30+ files; each session that reads "the newest" has to search | Move to `docs/research/archive/`; keep `craft-metrics`, `creature-playbook`, `render-throughput` as living docs |
| `docs/audit/*.pdf` and `*.png` | Check what links to them first | Keep if `docs/youtube-setup.md` or the OAuth app needs them |
| `stories/ideas.md` (480 lines) | Mixed ideas, kill notes and batch tables | Split: `ideas.md` (open), `killed.md` (one line each) |

## 5. The migration

Each step is a small PR that `test` gates. Uploads never stop: the daily upload reads only `queue.txt`, `uploads.json`
and film artifacts, and no step changes those until step 10. 14 passed films cover through Monday Nov 9, so there is a
week of buffer. Steps are ordered by value over effort.

| Step | Change | Effort | Done when | Test |
|---|---|---|---|---|
| 1 | **D + E:** turn on `REQUIRE_PROOF` after moving-day; one proof per sha; proof only after both reviews approve; `test` says "waiting for proof" instead of red | small | No final drawn without a passed proof qa; no plan-only or duplicate proof runs for a week | `test_plan_proofs` cases for a no-film push and a duplicate dispatch; `test_render_plan` for an unproofed story |
| 2 | **F + Q:** real-timeline fixtures (one on twos) for every guard; one setup action | small | Every guard in render and proof runs against the fixtures in `test` | A twos fixture passes `check_drawings`; a fixture with one drawing removed fails |
| 3 | **A:** `bar.json` v1 with today's numbers, read by `measure.py`, `proof_report.py` and `gate.py`; qa files stamp `bar_version` | medium | No bar number is written anywhere else in code; agents' prompts point at the file | A test changes a number in a copy of `bar.json` and sees the gate result change; a test greps for stray copies of the pace targets |
| 4 | **M + I + J:** round cap in `gate`; `story/<slug>` branches with a delete-on-merge workflow; `blocky handoff` writes STATE.json | small | `gate` refuses round 3; new stories use the branch shape; no new HANDOFF.md | Gate tests for round 3 and one rescue; a handoff test from a sample review |
| 5 | **H + O:** brief templates; proof and qa judge with tools from main | small | Every new session is started with a brief name, not a pasted brief | A brief linter: each template names only files that exist and references `bar.json` |
| 6 | **B:** creature card in the writer's output and a creature-still step before build | medium | No build session starts without a passed creature still for creature stories | Run on batch 10 (ep101 to ep107): count creature drops after build (target 0) |
| 7 | **G:** voice only on Actions; local builds use committed timings; bpy cache if still needed | medium | A build session's setup is under 5 minutes | Time a fresh builder's setup; a proof voices and mixes as now |
| 8 | **C + N:** predicted pace and the framing check in `check` | medium | `check` predicts picture changes and motion energy within an agreed error of the proof's real numbers | Calibrate on the 15+ proofs already drawn; report the error per story |
| 9 | **L + K:** the daily digest; one queue owner; a PR-based inbox | small to medium | The owner gets one digest a day; no polled channel | A week with no #177 comments and no missed handoff |
| 10 | **Section 4 deletes**, one PR per group | small each | Each list above empty | `python -m pytest -q`, `check` on every remaining story, and one proof of a polish story |
| 11 | **P:** chunk queue and per-shot cache | large | A one-shot fix redraws only that shot | Fix one shot of a drawn story; compare runner-min and frame bytes |

## 6. Open questions for the owner

**Answered 2026-11-04** (owner: "Go with your recommendations on all six"; RULES.md, "The audit decisions"):
1. One queue owner, the first orchestrator. The second account is build capacity.
2. The bar changes weekly, between batches, by PR. A story is judged on the bar in force when its script merged, and the owner's own feedback takes effect at once.
3. Yes: two rounds and one single-fix rescue, enforced in code.
4. Yes: creature-light by default.
5. Yes: one digest a day, plus direct pings only for what needs the owner.
6. Delete the dropped story folders and keep the research.

The questions as asked:

1. **One orchestrator or two?** Two gives a second usage pool, but costs the polling lag, the owner emails and the
   ownership splits (root cause 5). The plan works either way if one of them owns the queue alone.
2. **When may the bar change?** Proposed: once a week, between batches, by PR; a finished story is judged on the bar
   its script merged under. Is that strict enough, or too strict for your own feedback?
3. **How strict a round cap?** Proposed: two rounds and at most one single-fix rescue, enforced in code, no exceptions.
4. **Creature-light by default?** The playbook didn't rescue a weak creature (entry 28). Should most stories be "a person
   made wrong" or never fully shown, with full creature reveals as the exception?
5. **What do you want to hear, and how often?** Proposed: one digest a day, and a direct ping only for what needs you
   (a publish, a rule question, a blocked upload).
6. **May we delete the dropped story folders and old research,** or keep them for reference? (They stay in git history.)
