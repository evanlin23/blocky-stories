# External cron (the clock that doesn't depend on Claude)

GitHub's `schedule:` triggers have never fired for this owner (zero schedule-event runs in either repo), and
Claude's scheduled tasks stop when the usage limit runs out. So the daily upload is started by
[cron-job.org](https://cron-job.org) (free). It sends GitHub's "run this workflow" request. Everything after
that runs on GitHub Actions and needs no Claude usage at all.

## 1. A token that can only start this repo's workflows
GitHub → Settings → Developer settings → Fine-grained tokens → **Generate new token**:
- Name: `cron-job.org dispatch`. Expiration: 90 days (renew it when GitHub emails you).
- Repository access: **Only select repositories** → `evanlin23/blocky-stories`.
- Permissions → Repository → **Actions: Read and write**. Nothing else.

Copy the token. It goes only into cron-job.org, never into a chat or a commit.

## 2. The jobs on cron-job.org
Create a free account, then **Create cronjob** for each row. Every job uses:
- Advanced → Request method **POST**
- Headers:
  - `Accept: application/vnd.github+json`
  - `Authorization: Bearer <your token>`
  - `X-GitHub-Api-Version: 2022-11-28`
- Request body: `{"ref":"main"}`
- Time zone **America/Chicago**

| Title | URL | Schedule |
|---|---|---|
| blocky upload | `https://api.github.com/repos/evanlin23/blocky-stories/actions/workflows/upload.yml/dispatches` | every day, 6:47 |
| blocky metrics | `https://api.github.com/repos/evanlin23/blocky-stories/actions/workflows/metrics.yml/dispatches` | Mondays, 14:37 |
| blocky comments | `https://api.github.com/repos/evanlin23/blocky-stories/actions/workflows/comments.yml/dispatches` | every day, 16:17 |
| blocky compilation | `https://api.github.com/repos/evanlin23/blocky-stories/actions/workflows/compile.yml/dispatches` | Sundays, 8:17 |
| blocky render catch-up | `https://api.github.com/repos/evanlin23/blocky-stories/actions/workflows/render.yml/dispatches` | every day, 3:17 |

A successful run returns **HTTP 204**. Use **Test run** on each job once, then check the repo's Actions tab
for a new `workflow_dispatch` run.

## What still needs Claude
Writing and building new stories (the Monday `/week` task) and the daily check. If the usage limit runs out,
uploads keep going from the queue (`queue.txt`, plus every ready story) until it's empty. The Claude tasks pick
up again after the limit resets, because every step's state lives in GitHub.
