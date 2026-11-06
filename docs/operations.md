# Operations: how the channel runs itself (learned 2026-11-01 to 11-02)

Read this before changing anything about schedules, sessions, uploads or renders. Every line here was learned
the hard way.

## The clocks
- **GitHub's `schedule:` never fires for this owner.** Zero schedule-event runs, ever, in either repo. Don't rely
  on cron lines in workflows. They stay only as a harmless backup.
- **cron-job.org is the real clock** (`docs/external-cron.md`). It sends `workflow_dispatch` to upload.yml (6:47 AM
  Central daily), metrics.yml (Mondays 2:37 PM) and render.yml (3:17 AM daily catch-up). It needs no Claude usage.
  The token expires 2027-01-31 (a reminder is set for 2027-01-20).
- **Claude scheduled tasks run late and are sometimes skipped.** They were seen 0 to 75 minutes late, and a
  reminder waits while its target session is mid-turn. Use them only for work where an hour doesn't matter:
  checks, merges, batches and reports. Never for the upload.

## Claude sessions and scheduled tasks
- **A task that starts a fresh session per fire gets no repo, no GitHub MCP and no create_session.** Tested
  2026-11-02: it can't do our work. Scheduled tasks must fire into a persistent session that was created with
  the repo as a source.
- **`fire_trigger` (run now) always starts a fresh, tool-less session,** even for a task bound to a persistent
  session. To test a task, schedule a one-off run into the persistent session instead.
- **The operator session** (`session_019n1tKDvYn1BhSdFd2PKhPL`, created with this repo as its source) receives:
  - the daily check, 7:17 AM Central: confirm the upload ran (dispatch if not), count the queue, fix renders, and
    on Mondays dispatch metrics
  - the weekly `/week`, Mondays 4:13 PM Central, right after the usage reset: numbers → rules → the next batch
    It reports to the orchestrating session `session_019n1tKHLkea725KWepZp2PU`.
- **Sessions can't use `gh api` for Actions.** The proxy blocks it. Use the GitHub MCP tools (actions_list,
  list_workflow_run_artifacts, actions_run_trigger).

## The usage limit
- The account has a seven-day limit that **resets Mondays at 4:00 PM Central**. Near the limit, sessions see
  `allowed_warning`, and at it, every session's turn stops ("You've hit your weekly limit").
- **Stopped sessions don't resume on their own.** After the reset, every session whose status_bucket is FAILED
  and that hasn't finished its story needs a "continue" message, but only if its story is still needed (see the budget below).
- Nothing is lost while stopped, because all state lives in GitHub: PRs, branches, `queue.txt`, `uploads.json`
  and the stories.
- Watch spend: about 20 parallel story sessions used most of a week's limit in a day (2026-11-02).
- **It happened again (2026-11-03): 74% of the week was gone less than a day after the reset**, with about 60 sessions
  started over 2 days and up to 15 working at once. Where it went:
  - **Work on stories later dropped.** 7 redo sessions (ep23, 25, 30, 31, 32, 33, lookout), then opening fixes on
    ep26, 33, 34, 37, 43 and 46, and all of them dropped within hours. Decide keep or drop *before* paying to fix.
  - **Failures found after the final render** (moving-day, ep58, ep62, warm-shoes) cost a re-render plus a fix round
    and another QA each. The proof render before merge exists to stop this.
  - **Review rounds:** up to 8 critic rounds on one story. Two rounds, then drop.
  - **Long-lived sessions:** this orchestrator and the batch leads carry huge contexts, and every check-in or
    message re-reads them. The check-in went from every 2 h to 3 a day.
  - **Sessions kept alive after their task** (waiting on renders, then given a second job).
- **The budget rules:**
  - At most **5 sessions working** at once.
  - **One story, one task per session.** It ends when its PR merges or the story drops. QA on a new film gets a fresh,
    short session (the qa agent alone), not the builder's long one.
  - **No new batch while 4 or more days of ready stories exist.**
  - **Triage first:** queue audit and keep/drop decisions happen before any fix work.
  - **Plan by the meter:** check the usage meter before starting a batch. At 50% before Thursday, pause everything except
    QA and uploads.

## Two orchestrators (from 2026-11-03)
- **The first orchestrator** runs the channel day to day (queue, uploads, dispatching renders, `blocky/`). **The second** runs on a
  separate subscription: since 2026-11-03 (owner-approved) it owns most story work and every final qa except the first's own
  stories, plus the research brief. Neither can message the other directly.
- **Two usage limits.** The first's seven-day limit resets Mondays at 4:00 PM Central, the second's Thursdays at 8:00 AM Central.
  When one is near its limit, the other takes the work (2026-11-03: the first was near its limit with the second at 15%).
- **Messages go on issue #177 ("Orchestrator channel"),** not in a file: every PR waits behind the render jobs for its `test` run,
  so a doc PR is too slow for messages. `[#1]` / `[#2]`, then ASK, FYI or DONE. At most one batched comment per check-in (each one
  notifies the owner), with the Claude Code footer. The owner asked the second to post after everything it does (2026-11-03),
  so the second posts one comment per check-in or action that changed something, and none for a quiet check. The channel test on 2026-11-03 went both ways within minutes.
- **Both sides read it on a schedule, with no person in between.** A comment can't wake a session (GitHub only pushes PR events to a
  session), so each side polls with a Claude scheduled task that fires into its own persistent session. The first orchestrator
  reads at 8:41 AM, 2:41 PM and 8:41 PM Central (its usage limit is tight). The second reads every hour at :21 and answers an
  URGENT ask within the hour.
  `docs/second-team.md` holds the second team's status, one line per item.
- **The render pool is shared:** about 40 jobs at once for the account, not 20 (39 ran together at 19:58:45 UTC on
  2026-11-03, and waiting shards started within 4 s of other jobs ending; `docs/research/render-throughput.md`). Finals take
  up to 32 (two slots of 16) and a proof 8, leaving about 8 for PR tests. A proof started while a render draws may wait a
  few minutes. Never cancel a `render` run while it is drawing.
- **proof.yml gap (2026-11-03):** a waiting PR proof run that a newer push replaces is planned again for the new push only. If that
  push touched no film files (a main merge, a handoff note), nothing is drawn and the story never gets a proof (ep55 and ep42).
  Check that a proof run has draw jobs, and if it only ran `plan`, dispatch proof.yml with the story and the branch.
  The plan's reasons are on the run's summary page (2026-11-05).

## Uploads (YouTube)
- **API uploads are not locked to private.** YouTube's API team confirmed this on 2026-11-02 and closed our
  audit request as unnecessary. Each upload is private with a scheduled `publishAt` (4:00 PM Central, or an hour
  out if that's past), so it goes public on its own.
- `YT_AUDITED=true` (a repo variable or a secret, both read) switches on API uploads. Without it, upload.py opens
  an "Upload by hand" issue instead. The run log prints which condition is missing, without values.
- **No duplicates:** the `upload` concurrency group runs one at a time; there's up to UPLOADS_PER_DAY (2) per UTC day, the second only while 5+ stories stay ready
  (`uploads.json`); the uploads.json push retries across a moving main; and any title already in the channel's last
  50 uploads is recorded, not re-uploaded. `--story NAME` skips the one-a-day check, for the owner's explicit
  extra uploads only.
- **Comments:** the API can post a comment only with the `youtube.force-ssl` scope. **Pinning isn't possible
  through the API, and the owner can't pin either**, so the pin text is posted as the channel's own comment once
  the video is public.
- The OAuth app is "In production", so refresh tokens don't expire after 7 days. The "unverified app" warning is
  normal for a personal tool.

## Renders (GitHub Actions)
- **Releases are blocked** (403 even with contents: write), so films are run artifacts, `film-<story>`, kept 90 days.
- One render run at a time. **A waiting run is replaced by each newer push**, so many "cancelled" render runs are
  normal: the next run picks up every story without a film, or with a film older than its last picture or sound
  change.
- At most 2 stories a run, in two slots, **both drawing at once** (`draw-b` no longer waits for `draw-a`): each story's
  assemble waits only for its own shards (a shared wait delayed the first film by hours on 2026-11-03). Each story is
  drawn in **32 shards** (finer, so a fast runner takes the next one instead of waiting on the slowest), and each slot's
  `max-parallel` is 16, so a run uses at most 32 draw lanes of the account's ~40 and leaves about 8 for one proof and the
  PR tests. The `again` job chains the next run. If a story's shard fails, its assemble is skipped (no film), the other
  story and `again` still run, and the next plan draws it again; "Re-run failed jobs" on the run redraws just the failed
  shard, then assembles. A run of 8 stories takes about 5 hours.
- **A final can be held until a proof has passed (2026-11-03). It is OFF for now.** With it on, `plan_renders.py` skips a
  story unless `qa/<story>.json` is `"stage": "proof"`, passed, at a sha with no film file changed after it
  (`blocky.gate.proof_problems`, the check `test` makes), or its final qa already passed, and the plan log says why. Turn it
  on by setting `REQUIRE_PROOF: "true"` in render.yml's `env` once the stories merged before proofs existed (closing-time,
  ep47-fitting-room, moving-day, ep54-dance-hall, rule-three) have uploaded or been proofed; until then they'd be stuck. An
  explicit `story` dispatch input is never held back.
- **Drawn shards are reused.** Each shard is kept as `frames-<story>-<k>of<n>` (5 days; the count is in the name so a
  16-shard cut is never taken for a 32-shard one). The plan reuses a shard whose artifact is unexpired and whose commit
  has no change to `blocky/`, `assets/` or the story's film files since, and draws only the rest. When every shard is
  there, `draw` is skipped and only `assemble` runs (it downloads the kept shards through the API with `GH_TOKEN`,
  `scripts/fetch_shards.py`). The narration is made again, so a story drawn on one voice and mixed on another would drift:
  if a reused film is out of sync, redraw it by changing a film file.
- **Never cancel a render run while it is drawing.** Drawn frames are the only expensive thing here (about 7,300
  runner-minutes were thrown away on 2026-11-03 by cancels). A newer push waits in the queue and is picked up by the
  next run.
- A film is only assembled from a complete set of shards (closing-time, run 87, 2026-11-03).
- The narration is made once on Actions (the `voice` job) and the picture is drawn to it. Local and Actions
  synthesis differed by up to 0.85 s per line, which broke sync before that change.
- A film that fails the flash bar is kept but never uploaded, and the upload skips to the next story. The usual
  causes are light flicker on bright close-ups and z-fighting (coplanar surfaces), which can pass the preview and
  fail the final.

## Proofs (before merge, 2026-11-03)
- Every story PR draws a **proof** (`proof.yml`): the whole film at half size, every drawing the final makes. It
  starts by itself once both reviews approve, and again whenever the film files or the reviews change on the PR.
- Its own concurrency group (`proof-<PR>`), so it never cancels or queues behind `render`. It takes 8 runners for
  the drawing, `render` takes 16 of the 20 free ones: a proof started while a render draws simply waits.
- A proof costs about 40 minutes of wall time a story (voice 5, draw 10 to 20 in 8 shards, assemble about 20).
- `test` won't merge a story without `qa/<story>.json` at `"stage": "proof"`, passed, whose `sha` is a commit in
  the branch with no film file changed after it. So the last push before a merge must be the one the proof drew.
- A proof that fails leaves its artifact anyway (`proof-<story>`, 14 days), so the qa agent can still look.
- **One proof per commit, for the PR's own stories (2026-11-05, migration step 1).** The PR's stories come from
  `base...HEAD` (where the branch left main): a two-dot diff against main's tip had proofed stories main changed
  on other PRs (dryer-nine on two PRs, warm-shoes on ep58's, about 340 runner-min in 48 h). A dispatch now passes
  the same checks as a PR run: both reviews approve, not held, no passed proof check, no live `proof-<story>` of
  the same film, and no older run of the same commit drawing it (ep28 and ep45 were drawn twice, about 360
  runner-min). Such a dispatch only runs `plan` and says why on its summary page; `force` draws it anyway.
- `test` marks a story whose only block is its proof as **waiting for proof** (a warning and a summary line). It
  still blocks the merge.

## Merging
- `test` gates every story a PR touches, so a story whose reviews say revise can't merge. A `WIP` title skips it.
- Many sessions merge their own PRs. Shared files (`blocky/*.py`, `stories/lore.md`, `stories/ideas.md`) conflict
  often, and `stories/lore.md` uses `merge=union` (`.gitattributes`).

## GitHub's schedule woke up (2026-11-02)
After weeks of never firing, GitHub's `schedule:` triggers started on 2026-11-02, hours late: an upload run meant for
3:47 PM ran at 9:04 PM Central and uploaded knock-back, public at 10:04 PM. upload.py counted days in UTC, so it saw
a fresh day. Fixes: no workflow has a `schedule:` any more (cron-job.org is the only clock), the upload day is the
Central date, and an automatic upload only starts between 5 AM and 7 PM Central. A manual run with a story still
works any time.

## YouTube API units (free quota: 10,000 a day, all workflows share it)
- Daily upload: about 1,600 (an insert is 1,600). Monday metrics: `trends.py` about 2,230 (22 searches at 100 each: ten blocky, twelve wide for the port study,
  plus about 17 videos.list and channels.list),
  `trends_deep.py` about 45 (one videos.list, one channels.list, 40 commentThreads.list at 1 each), capped at 300 in
  the script. A metrics run and an upload on the same day total about 3,900. A by-hand metrics dispatch on an upload day
  adds another 2,270: three runs in one day is the most that fits.
- `trends_deep.py` writes `docs/trends/deep/<date>.json` and `.md`. Descriptions and comments are trimmed and
  @handles masked, because the repo is public.
