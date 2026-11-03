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
- **Health check:** list recent `render` workflow runs (GitHub MCP `actions_list`) and open issues. A failed `flash result` step means a final failed the flash bar (its film is kept as an artifact but never uploaded). Fix it first, with the builder redrawing the named shots and a `workflow_dispatch` of `render` for that story. Count the stories that are ready but not uploaded (gate open, not in `uploads.json`). **Keep a week ahead:** make N = 14 minus that count (this week's uploads plus next week's), at most 10, unless the request names a number.
- **Numbers:** read `metrics/summary.md` (the weekly `metrics` workflow writes it). If its date is more than 3 days old, the schedule didn't fire: start the `metrics` workflow yourself (GitHub MCP `actions_run_trigger`, `metrics.yml` on `main`), wait for it, and pull. Pick out at most 5 lessons (what held viewers, where they dropped, what got shares and comments) and hand them to the writer in step 1.
- **Trends:** read the newest `docs/trends/*.md` (RULES → Trends). Pass the writer the 3 fastest-rising formats, any format cooling two scans in a row, and the 70/30 mix: which stories are core and which are experiments.
- If `BLOCKY_BPY` or `BLOCKY_TTS` is unset: `bash blocky/setup.sh` and export what it prints.
- A container can be reclaimed at any time, so commit and push `WIP` checkpoints to the branch after each story's build.

## 0.5 Research before any writing (owner, 2026-11-03: "I'm worried we aren't spending enough time doing research and then just jumping into creating new shorts.")
No writer call until `docs/research/<date>-week.md` is committed. It holds:
1. **Our numbers:** every upload's views, viewed vs swiped away, average % viewed, the biggest retention drop and its second, from `metrics/` (plus anything the owner pasted from Studio). Say what held people and where we lost them, with the numbers.
2. **The market now:** the newest `docs/trends/` scan and `docs/trends/deep/` (the top Shorts' titles, lengths, descriptions and top comments). The 10 fastest Shorts in formats we could make, with one line each on why it works (premise, hook, length, title shape, what commenters react to).
3. **Three hypotheses** for this batch, each one change we can measure ("60 to 90 s beats 130 s on average % viewed"), and which stories test which.
4. **Pitches:** at least 3 times as many pitches as stories, each citing its evidence (a trend row, a comment theme or our own number). A fresh agent that has read nothing ranks them blind by title and first line, mixed with 5 of this week's fastest real titles. Keep the top N. Any of ours below the real titles' median doesn't get written.
Spend real effort here: about a fifth of the batch's time goes to research, before any building.

## 1. Write (1 writer call)
"Write a batch of N stories" (plus the owner's idea, if any). Check its variety table yourself, and check the batch for **superficial sameness** (YouTube demonetizes "narrated stories with only superficial differences"): at most a third of titles start "In This Town", and no two stories share a setting type, a rule type, a creature type, a twist shape, a palette or a music mood. Then: no shared setting, creature, first line, ending or warmth. If two rows clash, send the writer back once.

**Cold-viewer test** (RULES → "Relationships read at a glance"): for each script, a fresh general-purpose agent gets only `script.md` and answers in two sentences what happened, what the twist means, and who each person is to the narrator. Any wrong or unsure answer sends the script back to the writer once, before building.

**Blind premise check** (the scope research's H2 test): before any building, a fresh general-purpose agent that has read nothing in the repo gets only the batch's titles and first lines, mixed with 5 known hits' first lines (from `docs/research/2026-11-02-reel-watch-notes-2.md`) and with no labels. It scores each 1 to 10 for "would I stop scrolling for this?". Any of ours that scores below the hits' median goes back to the writer once.

## 2. Build (a fresh builder call per phase)
Start a **fresh builder agent for each phase** (the build, then each fix round). Never reuse one builder across phases: a long-lived builder's context passed 350K tokens and made every step expensive (pilot 1). One story at a time, because Blender takes the CPU. When a builder's preview is done, start the next builder while that story is in review. Retry a crashed step. Never drop a story for a crash.

## 3. Review
- **Critic, per story,** as each preview is done: "Review `<name>`, round 1."
- **Standards, once for the whole batch,** when every preview is done: "Review `<name1>`, `<name2>`, ... round 1." That saves re-reading the rules and every earlier story for each one.
- Read only each review's `Verdict:` line and its numbered must-fixes.
- If the two reviews' must-fixes contradict each other, standards wins on rules (lore, kids, IP, fiction, flashing) and the critic wins on craft. Drop the losing note before you send the list on (ep17: the critic wanted a six-mark tally, but standards had ruled the story out of lore).
- **revise:** send every must-fix from both reviews to the builder in one call. If any are about words or package, send them to the writer first, in one call, and pass its changed line ids on. Round 2 re-runs **only** the reviewers who said revise, with standards again batched over every story it sent back.
- **Two rounds at most, firmly** (pilot 1 ran a third and slipped hours). If a story is still not approved after round 2, or a reviewer says kill, drop it: delete its folder, add a "killed: why" line to `stories/ideas.md`, and have the writer and builder make one replacement if the week is short. Never retry an idea killed for a hard rule. **One rescue round:** when a story fails round 2 but a review names a single concrete fix (a light level, one creature shot), the builder applies just that, and only the reviewer who blocked looks once more. Then it ships or stays killed (ep37, ep41).
- Done when `python -m blocky gate <name>` says OPEN.

## 4. Ship (no agents)
- `python -m pytest -q`, and `python -m blocky gate <name>` for every story in the batch.
- Commit the story folders (never `out/`). Push, then open ONE PR with a table of slug, title and upload order. Merge it once the `test` check passes (the owner approved team merges). `test` runs `gate` on every story the PR touches, so a story whose reviews still say revise can't merge; drop it from the PR instead (or title the PR `WIP` for a checkpoint that must not render).
- The merge starts `render` on Actions, which draws each final in 16 shards and keeps the film as the artifact `film-<story>`. Then `upload` puts one story a day on PandaNanoAdventures as **private** and opens an issue for the owner to publish it. The session doesn't wait for any of this.
- Tell the owner: the stories, their titles, the upload order, and that each one will arrive as a "Ready to publish" issue.

## Usage rules
- No reviewer reads another reviewer's file, and nobody reads `blocky/*.py` unless they're changing it.
- Reports are capped (agents say how long). Never paste a whole review back into a prompt: pass the must-fix list.
- No look tests or check-ins with the owner mid-batch (owner: "you can do all of like the design like stuff. Just let me know when the full video is done"). The owner's job is the final watch and the publish click.
- Owner feedback on any story becomes a dated rule in `RULES.md`, in the same PR.

## The 2026-11-03 reset
Every batch from now on follows RULES.md "The 2026-11-03 reset": the length split (60 to 90 s and 120 to 150 s), at most a third of the batch ending on a sad family reveal, and a third of the experiment slots for the recurring-cast series. Check the whole batch against it before the PR.
