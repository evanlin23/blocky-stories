# blocky-stories

Creepy blocky story Shorts for the owner's YouTube channel **PandaNanoAdventures**, one a day. This repo makes them end to end: stories are written and built here by Claude, GitHub Actions renders the finals and uploads them as private videos, and the owner watches and publishes.

- **Rules:** `RULES.md` is the only rules file. It outranks everything except the owner's own words. When the owner gives feedback, add it there as a dated quote, in the same PR.
- **Make stories:** `/week [n]` (`.claude/skills/week/SKILL.md`). The agents are writer, builder, standards and critic (`.claude/agents/`).
- **Engine:** `blocky/` (`python -m blocky <step> <story>`; reference in `docs/engine.md`). Stories live in `stories/<name>/`. Working files go to `out/` (gitignored, never committed).
- **Ship gate:** `python -m blocky gate <story>`: `check` passes, `package.json` lints clean, and the latest standards and critic reviews say `Verdict: approve`.
- **After merge:** `.github/workflows/render.yml` draws the finals (16 shards), mixes, flash-measures and makes a `render-<story>` release. `.github/workflows/upload.yml` uploads the next ready story daily, private, and opens an issue for the owner. `uploads.json` records what's been uploaded. `.github/workflows/metrics.yml` writes `metrics/summary.md` every Monday, and `/week` feeds its lessons to the writer. Setup: `docs/youtube-setup.md`.
- **Tests:** `python -m pytest -q` (no Blender or TTS needed).
- **Budget is $0:** free tools only.

## Commit identity (required)
```bash
git config user.name evanlin23
git config user.email 113861384+evanlin23@users.noreply.github.com
```
Work on a branch and open a PR. The team merges once `test` passes (owner, 2026-10-29: "You can merge things when you want, I approve").
