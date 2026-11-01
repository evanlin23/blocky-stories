---
name: week
description: Make a week of creepy blocky stories for PandaNanoAdventures (default 7, one upload a day). The writer writes the batch, the builder builds and previews each story, standards and critic review it, and one PR merges them. After that GitHub Actions renders each final and uploads one a day as a private video for the owner to publish. Use when asked for the week's stories, a batch, more stories, or one story ("/week 1").
argument-hint: "[how many, default 7] [an idea or premise, optional]"
---

# /week: a batch of blocky stories

Request: **$ARGUMENTS** (a number is the batch size, and any words are an idea for one of the stories).

You're the orchestrator. Keep your own context small: you read reports and verdict lines, not whole reviews or code. Agents do the work (`.claude/agents/`), and their prompts name the story and the round, and nothing else they can read for themselves.

## 0. Preflight (no agents)
- `git config user.name evanlin23 && git config user.email 113861384+evanlin23@users.noreply.github.com`, then work on a branch, never `main`.
- **Health check:** list the repo's releases (GitHub MCP `list_releases`) and open issues. A `render-*` prerelease means a final failed the flash bar. Fix it first, with the builder redrawing the named shots and a `workflow_dispatch` of `render` for that story. Count the stories that are ready but not uploaded (gate open, not in `uploads.json`). If there are 7 or more, make fewer this week.
- If `BLOCKY_BPY` or `BLOCKY_TTS` is unset: `bash blocky/setup.sh` and export what it prints.
- A container can be reclaimed at any time, so commit and push `WIP` checkpoints to the branch after each story's build.

## 1. Write (1 writer call)
"Write a batch of N stories" (plus the owner's idea, if any). Check its variety table yourself: no shared setting, creature, first line, ending or warmth. If two rows clash, send the writer back once.

## 2. Build (1 builder call per story)
One story at a time, because Blender takes the CPU. When a builder's preview is done, start the next builder while that story is in review. Retry a crashed step. Never drop a story for a crash.

## 3. Review (standards + critic in parallel, per story)
- Prompt: "Review `<name>`, round 1." Then read only each review's `Verdict:` line and its numbered must-fixes.
- **revise:** send every must-fix from both reviews to the builder in one call. If any are about words or package, send them to the writer first, in one call, and pass its changed line ids on. Round 2 re-runs **only** the reviewers who said revise.
- **Two rounds at most.** If a story is still not approved after round 2, or a reviewer says kill, drop it: delete its folder, add a "killed: why" line to `stories/ideas.md`, and have the writer and builder make one replacement if the week is short. Never retry an idea killed for a hard rule.
- Done when `python -m blocky gate <name>` says OPEN.

## 4. Ship (no agents)
- `python -m pytest -q`, and `python -m blocky gate <name>` for every story in the batch.
- Commit the story folders (never `out/`). Push, then open ONE PR with a table of slug, title and upload order. Merge it once the `test` check passes (the owner approved team merges).
- The merge starts `render` on Actions, which draws each final in 16 shards and publishes a `render-<story>` release. Then `upload` puts one story a day on PandaNanoAdventures as **private** and opens an issue for the owner to publish it. The session doesn't wait for any of this.
- Tell the owner: the stories, their titles, the upload order, and that each one will arrive as a "Ready to publish" issue.

## Usage rules
- No reviewer reads another reviewer's file, and nobody reads `blocky/*.py` unless they're changing it.
- Reports are capped (agents say how long). Never paste a whole review back into a prompt: pass the must-fix list.
- No look tests or check-ins with the owner mid-batch (owner: "you can do all of like the design like stuff. Just let me know when the full video is done"). The owner's job is the final watch and the publish click.
- Owner feedback on any story becomes a dated rule in `RULES.md`, in the same PR.
