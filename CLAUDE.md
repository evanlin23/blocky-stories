# blocky-stories

Creepy blocky story Shorts for the owner's YouTube channel **PandaNanoAdventures**, one a day. This repo makes them end to end: stories are written and built here by Claude, GitHub Actions renders the finals and uploads them as private videos, and the owner watches and publishes.

- **Rules:** `RULES.md` is the only rules file. It outranks everything except the owner's own words. When the owner gives feedback, add it there as a dated quote, in the same PR.
- **Make stories:** `/week [n]` (`.claude/skills/week/SKILL.md`). The agents are writer, builder, standards and critic (`.claude/agents/`).
- **Engine:** `blocky/` (`python -m blocky <step> <story>`; reference in `docs/engine.md`). Stories live in `stories/<name>/`. Working files go to `out/` (gitignored, never committed).
- **Ship gate:** `python -m blocky gate <story>`: `check` passes, `package.json` lints clean, and the latest standards and critic reviews say `Verdict: approve`.
- **After merge:** `.github/workflows/render.yml` makes the narration on Actions, draws the finals to it (16 shards), mixes, flash-measures and keeps the film as the run artifact `film-<story>` (90 days). A story whose picture or sound files change after its film is drawn again on the next push. `.github/workflows/upload.yml` uploads the next ready story daily, private, and opens an issue for the owner. `uploads.json` records what's been uploaded. `.github/workflows/metrics.yml` writes `metrics/summary.md` every Monday, and `/week` feeds its lessons to the writer. Setup: `docs/youtube-setup.md`. GitHub cron never fires for this owner: cron-job.org starts the workflows (`docs/external-cron.md`).
- **Operations:** `docs/operations.md` holds everything learned about schedules, sessions, the usage limit, uploads and renders. Read it before changing any of them.
- **Tests:** `python -m pytest -q` (no Blender or TTS needed).
- **Budget is $0:** free tools only.
- **Times:** always tell the owner times in US Central (owner, 2026-11-01). Workflows run on UTC; convert. Central is UTC-6 from Nov 1 to early March and UTC-5 in summer.

## Commit identity (required)
```bash
git config user.name evanlin23
git config user.email 113861384+evanlin23@users.noreply.github.com
```
Work on a branch and open a PR. The team merges once `test` passes (owner, 2026-10-29: "You can merge things when you want, I approve").
