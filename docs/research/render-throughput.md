# Render throughput: where final-render time goes (2026-11-03)

A study for the second orchestrator. Its question: how do more finals finish per day, for $0? Nothing in the workflows
or the engine was changed here. Each change below names who owns it: `render.yml` and `plan_renders.py` belong to
the second team (PR #178), `blocky/` and `proof.yml` to the first orchestrator.

`render.yml` here means main after #178 merged (each story has its own draw and assemble slot). All times are UTC (Central is UTC-6). The numbers come from the GitHub Actions API (job and step timestamps), the
draw-job logs (`rendered N frames in M min`) and `python -m blocky timeline` run locally on main.

## The short answer

1. **The account runs about 40 jobs at once, not 20.** At 19:58:45 on 2026-11-03, 39 jobs were running together:
   three proofs (8 draws each, plus clips), a proof assemble and 12 render shards. Render shards that were still
   waiting started within 4 s of other jobs ending: shard 12 at 19:59:39 when a clip ended at 19:59:38, and shard 9 at
   20:05:34 when a proof shard ended at 20:05:32. That is a hard cap, and it sits near 40. `render.yml` draws on 16
   at most, and in practice keeps 16 lanes only 61 to 69% busy (table 2). **The free lanes are the biggest gain.**
2. **About 7,250 runner-minutes were thrown away today**, at least 7 finals' worth. The causes were a 15-story run that
   got cancelled, a fully drawn story whose run was cancelled by hand, a full redraw after one shard was lost, and
   three finals drawn and then failed on the flash bar (table 4).
3. **One final costs 350 to 1,400 runner-minutes**, about 14 s of a runner per drawing (11 to 21 s) at 540×960 with
   10 samples. The polish pack's `ones: "moving"` puts nearly every shot on ones. It raised moving-day from 348 to
   571 runner-minutes (+64%), and closing-time, mirror-maze and dryer-nine now draw 100% of their frames.
4. **Runners differ in speed by 2×.** Shards of the same story do identical work (the frames are interleaved, and the
   artifacts are the same size), yet they finish in three tiers. closing-time's shards took 54, 78 or 91 to 107 min.
   A story finishes when its slowest shard does.

## Measurements

### 1. What a final draws versus the proof

| | preview | proof (`proof.yml`) | final (`render.yml`) |
|---|---|---|---|
| resolution drawn | 270×480 | 270×480 | 540×960 |
| Cycles samples | 4 | 4 | 10 |
| denoise | OIDN (albedo + normal, accurate prefilter), adaptive sampling 0.05, seed fixed | same | same |
| drawings | every 4th frame | every drawing the final makes | each shot's own step: twos, or ones under the pack |
| finish | to 1080×1920 | to 1080×1920 (Lanczos ×4) | to 1080×1920 (Lanczos ×2 + unsharp 1.4/55/2) |
| shards × workers | local | 8 shards × 2 Blender processes × 2 threads | 16 shards × 2 × 2 (4 vCPU runner) |
| runner-seconds per drawing (measured) | | about 1.6 (ep48: about 125 runner-min of drawing for 4,262 drawings) | 11 to 21 (table 3) |

A proof drawing costs about a tenth of a final one, and a tenth is also the ratio of pixels times samples
(¼ × 0.4). So Cycles time here scales almost linearly with samples, and the fixed cost per frame (scene update,
BVH, denoise) is small. That is why cutting samples (change 5) pays off nearly in proportion.

Proof frames can't stand in for final ones: they're a quarter of the pixels at 4 samples.

### 2. Render runs: wall time and how busy the lanes were

| run | stories | wall (min) | runner-min drawing | lane use (of 16) | result |
|---|---|---|---|---|---|
| 62 (06:50) | moving-day, mirror-maze | 71 | 691 | 61% | moving-day ok; mirror-maze failed flash |
| 70 (11:10) | ep54-dance-hall, ep58-swing-bridge | 104 | 1,015 | 61% | both ok |
| 78 (12:47) | moving-day, dryer-nine, warm-shoes | 142 | 1,490 | 66% | 2 ok; dryer-nine failed flash |
| 87 (14:53, plan 15:17) | closing-time, mirror-maze | 189 | 2,101 | 69% | closing-time shard 2 lost (runner died at 107 min, no log); the film was assembled with gaps anyway and failed qa; mirror-maze failed flash |
| 90 (18:26) | moving-day, ep47-fitting-room | 84, then cancelled by hand | 1,179 | | moving-day fully drawn (16/16, 578 runner-min), never assembled |
| 92 (19:50) | closing-time (redraw) | running | | | |

The wall clock runs from the first job queued to the last job done. Lane use is the drawing runner-minutes over
(the draw span × 16). Each run also loses 6 to 10 min to plan and voice before any shard draws, and the gap between
runs adds more: no final drew from 18:26 to 19:50 except run 90's, which was then cancelled.

### 3. Per story: shards, speed, tail and finish

| story | film (s) | drawings (on ones) | shard draw min/median/max (min) | runner-min | runner-s / drawing | slowest-shard idle (runner-min) | finish + mix (min) |
|---|---|---|---|---|---|---|---|
| closing-time (87) | 133.7 | 4,012 (100%) | 54 / 91 / 107 | 1,391 | 20.8 | 325 | 23 |
| mirror-maze (87) | 78.1 | 2,344 (100%) | 25 / 46 / 53 | 710 | 18.2 | 148 | 9 |
| moving-day (78) | 87.8 | 2,398 (88% of shots) | 18 / 39 / 40 | 571 | 14.3 | 87 | 10 |
| moving-day (62, before `ones: moving`) | 87.8 | about 1,300 | 12 / 23 / 24 | 348 | about 16 | 52 | 11 |
| dryer-nine (78) | 82.4 | 2,472 (100%) | 17 / 28 / 37 | 461 | 11.2 | 141 | 11 |
| warm-shoes (78) | 137.8 | 2,208 (7%) | 16 / 28 / 37 | 458 | 12.4 | 137 | 22 |
| ep54-dance-hall (70) | 144.7 | 2,194 (0%) | 20 / 37 / 40 | 524 | 14.3 | 124 | 21 |
| ep58-swing-bridge (70) | 140.7 | 2,131 (0%) | 17 / 35 / 36 | 491 | 13.8 | 95 | 19 |

- Drawing counts are from today's timelines on main, so a story's timeline may have changed a little since it was
  drawn. The 2026-11-03 stories draw at 30 fps on ones: 4,000 to 4,300 drawings for a 135 to 145 s film (ep48: 4,262,
  ep42: 4,150, ep55: 4,113).
- Each draw job spends 0.5 to 1.5 min outside the draw step (checkout, apt, the 374 MB `bpy` wheel, voice
  download). That is under 2% of a 40-minute shard. Checkout sometimes takes up to 2 min at busy times.
- Queue waits inside a run come from the matrix, not the account: the second and third stories waited 25 to
  106 min for the first story's shards to free up `max-parallel: 16`.
- Assemble waited for the run's whole draw matrix before #178 (27 to 73 min after its own shards were done). #178 (merged
  tonight) fixes that by giving each story its own slot. But in it, `draw-b` needs `draw-a`, so the two stories still draw one
  after the other.
- `finish` then `mix` runs in one process on one runner for 9 to 23 min (about 0.33 s per frame at 1080×1920). It's
  on the critical path of every film and every proof (a proof's finish + mix took 15 to 26 min).

### 4. Runner time thrown away on 2026-11-03

| what | runner-min | finals' worth (at about 700) |
|---|---|---|
| run 57: 15 stories in one run, cancelled after 1 h 50 with no film (only the first 100 of its 258 jobs were read: 51 shards done, 33 cancelled mid-draw) | ≥ 3,168 | ≥ 4.5 |
| run 90 cancelled by hand: moving-day fully drawn but never assembled, ep47 15/16 shards cancelled mid-draw | 1,173 | 1.7 |
| closing-time redrawn in full (run 92) after one shard of run 87 was lost | about 1,284 (1,391 minus the one shard) | 1.8 |
| three finals drawn and then failed flash at assemble (mirror-maze twice, dryer-nine) | 1,514 | 2.2 |
| duplicate ep48 proof (runs 28 and 29, the same sha at the same time) | about 165 | 0.2 |
| **total** | **≥ 7,300** | **≥ 10** |

### 5. Who used the runners

The day's runner-minutes couldn't all be pulled (the job lists are big), so the split comes from the runs measured.
A real proof costs about 165 runner-min (8 draws of 8 to 23 min, clip 4, voice 6, assemble 20 to 30), plus 1 to 3 min
for each plan-only proof run. There were 33 proof runs by 20:50 (ep48 alone had 9). Taking 10 to 15 real proofs a
day gives 1,650 to 2,500 runner-min, about 2 to 3 finals. Finals drew about 9,000 runner-min across runs 62 to 90,
and 30 to 40% of those were wasted (table 4). PR `test` checks are short (about 1 min each) and don't matter here.

At 19:58 the 40 slots were split about 26 proof, 12 final and 1 assemble. That was the one time proofs held back a
final: render shards waited 1 to 8 min for proof jobs to end.

## What limits finals per day now

```
finals/day ≈ lanes for finals × lane use × 1440 / runner-min per final
today:      16 × 0.65 × 1440 / about 950 ≈ 15 at best, about 10 after the waste in table 4
```

(950 runner-min is a 135 to 145 s story on ones at about 14 runner-s per drawing.)

## Ranked changes

Gains are in finals a day, for the 135 to 145 s stories on ones that make up the backlog, starting from about 10 a
day realised and 15 at best.

| # | change | gain | risk to the hit bar / flash bar | effort | owner |
|---|---|---|---|---|---|
| 1 | **Use the lanes there are.** In `render.yml` (since #178), drop `draw-b`'s need on `draw-a`, so both slots draw at once (16 + 16 = 32), and leave 8 for one proof. Then measure the cap on purpose (queue times when 40+ jobs are wanted) and write it in `docs/operations.md`. | 16 → 32 lanes: **about +10 to 15 a day** (2×). Both films also land about 1 h sooner (run 87 would have taken about 110 min, not 189). | None; same frames. If the cap ever drops back to 20, shards just queue (as today), though PR `test` jobs would queue too: give `test` a short timeout, or keep `max-parallel` at 12 each. | small (one `needs:` line) | second team |
| 2 | **Never throw drawn frames away.** (a) Don't cancel a render that is drawing; let the next push queue. (b) Plan draws only the missing shards: if `frames-<story>-<k>` artifacts from an earlier run exist at the same story commit (kept 5 days), download them and draw only the rest. (c) Have an assemble-only path for a story whose 16 shards are all there (moving-day's run-90 frames can still be assembled today). | Today's cancels and redraw cost about 2,450 runner-min: **about +2 to 3 a day** on a day like today, and closing-time would have been redrawn in about 107 min, not 1 h 50. | None. | medium (plan looks up artifacts by name with `gh api`, and the draw matrix becomes per-shard) | second team |
| 3 | **No final without a passed proof.** `plan_renders.py` skips a story unless `qa/<story>.json` is `"stage": "proof"`, passed, at a sha with no film file changed after it (the same check `test` does). Older stories merged before proofs existed get a proof first (about 165 runner-min, against a final's about 950). | The flash fails alone cost 1,514 runner-min today: **about +1.5 a day** while the backlog holds pre-proof stories, and about 0 after. | Lowers it: a final is only drawn for a film already judged. | small | second team (plan), using the first's gate |
| 4 | **Fewer samples: 10 → 6** with the denoiser already on (and adaptive sampling as now). | Time scales with samples here (section 1): about 35 to 40% fewer runner-min a final, so **about +50% a day on any lane count** (15 → 22 at today's lanes). | Medium. OIDN at 6 samples can crawl in dark, fog-heavy shots (frame-to-frame noise), and the critic scores sharpness. The flash bar is safe: noise is far under a flash. A/B it first: draw 3 shots at 10 and at 6 (dark fog, a close face, a bright wide) with `render --shots`, then finish them and compare at phone size with `flash` and `scripts/measure.py`. | small to change, an hour to test | first orchestrator (`blocky/__main__.py` `QUALITY`) |
| 5 | **Ones only where they show.** Today `ones: "moving"` draws a shot on ones when its camera moves or someone walks, and with the pack that's nearly every shot (+64% measured on moving-day, 1.9× drawings). Keep ones for walks, runs and fast camera moves, and draw the pack's slow push-ins and arcs (at most 0.12 m/s) on twos: the 2D crop push and drift already move every output frame. | About 30 to 45% fewer drawings for most of the backlog: **about +40% a day**. | Medium, and it's the lead's call: slow 3D moves on twos can judder. A/B one slow-push shot on ones and on twos at phone size. | small (a threshold in `polish.ones_for_moving`) | first orchestrator |
| 6 | **Finer shards, so fast runners take more.** Runners split into 2× speed tiers, and a story waits for its slowest shard (the slowest-shard idle in table 3 is 20 to 35% of a story's lane time). Make it 32 shards a story, with both slots' `max-parallel` filling the lanes: a fast runner finishes its shard and the queue hands the next one to whoever is free. | Lane use 65% → about 80%: **about +20%**. Each story's film also lands about 25% sooner. Each extra shard costs about 1 min of setup (2 to 3%). | None. | small (`SHARDS: 32`, and GitHub's 256-job matrix limit is fine at 2 stories) | second team |
| 7 | **Finish in the shards.** Each draw shard runs `finish` on its own frames (a frame's finish depends only on itself and the timeline), and assemble only encodes and mixes. Or `finish` runs 4 processes on the runner's 4 vCPUs. | Not more lanes, but 9 to 23 min off every film and 15 to 26 min off every proof, so stories merge sooner. | None if the output is the same bytes (a test can compare 10 frames). Captions and effects are per-frame in `post.finish`, so check any state carried between frames (rain). | medium | first orchestrator (engine), second team (workflow) |
| 8 | **One proof per commit.** Key the proof concurrency on the story and sha (or have a dispatch on a PR branch reuse the PR's group), and start no proof until both reviews approve (already in the lessons log, entry 3). | About 165 runner-min for each duplicate: **about +0.2 to 0.5 a day**. It also keeps the 8 proof lanes free in change 1. | None. | small | first orchestrator (`proof.yml`) |
| 9 | Caching the voice or the Blender install. | Under 2%: setup is 0.5 to 1.5 min a job, and the voice runs once a story in 3 to 5 min. Not worth the complexity. Reusing the proof's voice would take 5 min off a final's start if the sha matches, which is a convenience, not throughput. | | | |
| 10 | Shard counts by length, or longest shard first. | About 0. Shard count barely changes runner-min (change 6 is the useful form), and shards of a story are equal by construction, so the spread is hardware. Longest *story* first helps the last film of a queue by minutes. | | | |

**Together:** 1 + 2 + 3 take the realised count from about 10 to about 25 to 30 a day, with no change to a
single frame. The backlog of about 30 waiting stories would clear in about a day. Adding 4 and 5, if their A/B
tests pass, roughly doubles that again, and helps the proofs too: they draw the same drawings at the same samples
ratio.

### A second free runner pool (what it would take; nothing set up)

- **A self-hosted runner on the owner's own computer.** It costs $0 and GitHub allows it, and it adds as many lanes as
  the machine has (4 cores ≈ 1 GitHub runner). But this is a public repository: a runner that takes `pull_request`
  jobs can run anyone's code. It would have to be restricted to `push` and `workflow_dispatch` on main (a separate
  label that only `render.yml` asks for), and the computer has to stay on. It's the owner's decision, and a small
  gain next to change 1.
- **A free organisation (or a second account) with a mirror** would get its own concurrency quota. GitHub's terms
  allow one free personal account per person, and a second quota used to get round limits is against the spirit of
  the terms. Not recommended.
- **Free GPU notebooks (Kaggle: about 30 GPU-hours a week)** would draw Cycles many times faster than 2 CPU threads.
  But they're made for interactive data science: automating renders through them is unclear under their terms, and
  it adds a second pipeline. Only worth asking the owner if changes 1 to 5 still leave a backlog.

## Plan

**This week (no engine rewrite):**
1. Second team: change 1 in `render.yml` (both slots at once), then change 6 (`SHARDS: 32`). Watch the first run's queue
   times, record the cap in `docs/operations.md`, and in the meantime never cancel a drawing run.
2. Second team: change 3 (proof-gated plan), then change 2 (redraw only missing shards; assemble moving-day from
   run 90's frames if they are still kept).
3. First orchestrator: the A/B for changes 4 and 5 on one story (3 shots each). Ship whichever passes the critic's
   sharpness and smoothness checks and the flash bar.
4. First orchestrator: change 8 (one proof per commit).

**In the rewrite:**
- One render queue: a scheduler job that hands out small chunks of frames (about 60 drawings each) across every
  ready story to whatever lanes are free, instead of per-run pairs. Each film is assembled when its own chunks are
  in.
- Finish frames inside the draw chunks (change 7), so assemble is only encode and mix.
- A frame cache keyed per shot by its inputs (set.py, the shot's timeline slice, story.json's look and cast, the
  engine version), so a one-shot fix redraws one shot, not 4,000 frames. Today a fix after the final redraws
  everything (on 2026-11-03 alone: moving-day three times, closing-time and mirror-maze twice each).
- One `bar.json` (lessons log, entry 7) that both the proof and the final read, so a final is never drawn against a
  bar the proof didn't use.
