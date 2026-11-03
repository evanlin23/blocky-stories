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
  and that hasn't finished its story needs a "continue" message (send_message). The 2-hour check-in does this.
- Nothing is lost while stopped, because all state lives in GitHub: PRs, branches, `queue.txt`, `uploads.json`
  and the stories.
- Watch spend: about 20 parallel story sessions used most of a week's limit in a day (2026-11-02).

## Two orchestrators (from 2026-11-03)
- **The first orchestrator** runs the channel day to day (queue, uploads, qa, its stories). **The second** runs on a separate
  subscription with its own usage limit: backup stories, render infra and the research brief. Neither can message the other
  directly.
- **Messages go on issue #177 ("Orchestrator channel"),** not in a file: every PR waits behind the render jobs for its `test` run,
  so a doc PR is too slow for messages. `[#1]` / `[#2]`, then ASK, FYI or DONE. At most one batched comment per check-in (each one
  notifies the owner), with the Claude Code footer. The channel test on 2026-11-03 went both ways within minutes.
- **Both sides read it on a schedule, with no person in between.** A comment can't wake a session (GitHub only pushes PR events to a
  session), so each side polls with a Claude scheduled task that fires into its own persistent session. The first orchestrator
  reads at 8:41 AM, 2:41 PM and 8:41 PM Central (its usage limit is tight). The second reads every hour at :21 and answers an
  URGENT ask within the hour. Otherwise it posts once, batched, at 8:21 AM, 2:21 PM or 8:21 PM, just before the first reads.
  `docs/second-team.md` holds the second team's status, one line per item.
- **The render pool is shared:** 20 jobs at once for the account, and finals take 16. Never start a proof while a final render run
  is in progress or queued.

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
- At most 2 stories a run (each story's assemble waits for the whole draw matrix, so big runs delayed the first film by hours on 2026-11-03; the `again` job chains the next run) and 16 draw jobs at a time (leaving 4 runners for PR
  tests). A run of 8 stories takes about 5 hours.
- The narration is made once on Actions (the `voice` job) and the picture is drawn to it. Local and Actions
  synthesis differed by up to 0.85 s per line, which broke sync before that change.
- A film that fails the flash bar is kept but never uploaded, and the upload skips to the next story. The usual
  causes are light flicker on bright close-ups and z-fighting (coplanar surfaces), which can pass the preview and
  fail the final.

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
