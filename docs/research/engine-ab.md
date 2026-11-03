# Engine A/B: fewer samples, and twos for slow pushes (2026-11-03)

For the first orchestrator (issue #177 asked for "proposals with numbers"). It tests changes 4 and 5 of
`docs/research/render-throughput.md`. Nothing in `blocky/` changed: every setting was a CLI flag (`--samples`,
`--shots`) or a patch to the gitignored `out/work/.../timeline.json` (the `step` of one shot). The proposals are code
snippets below, not commits.

## How it was run

- Story `moving-day` (main, 2026-11-03), the real timeline, `final` quality: 540×960, denoiser on, adaptive sampling
  as now, 2 Blender processes × 2 threads on a 4-vCPU box (the runner's layout). Frames were finished with the
  engine's own `post.finish` to 1080×1920 and encoded at crf 17.
- Shots: S32 (dark hall in nightlight, fog), S21 (close scared face), S04 (bright wide street): 136 drawings each
  time. For twos: S50 (84 frames, close on a photo, authored slow push) and S32 (28 drawings on twos against 55 on
  ones, the pack's own 0.12 m/s push).
- "Runner-seconds per drawing" is the wall time of `render` over the drawings, on a box laid out like a runner. This
  box draws about twice as fast as the runner did in the study (6.5 s a drawing here against 11 to 21 there), so only
  the **ratios** carry over. Minutes saved are extrapolated by ratio to the study's 950 runner-min average final.
- Craft numbers come from `scripts/measure.py`'s `picture()` on each finished clip (its picture metrics read pixels only), and
  `python -m blocky flash` logic (`flash.measure`) on the three-shot clip. Two extra pixel metrics: sharpness (mean
  Laplacian variance) and noise crawl (mean frame-to-frame change of the high-pass residual).
- Verdicts come from a `critic` agent on Opus, looking at real frames side by side at phone (390 px wide) and TV (1:1
  crop) size. It judged from consecutive frames and edge tracking, not from playing the clips.

## Change 4: samples 10 → 6

| | 10 samples (today) | 6 samples |
|---|---|---|
| drawings | 136 | 136 |
| wall time | 14.7 min | 10.7 min |
| runner-s per drawing | 6.49 | 4.72 |
| **saved** | | **27%** (not the 35 to 40% the study guessed: about a quarter of a drawing is fixed cost) |
| **per 950 runner-min final** | 950 | **about 690, so about 260 min saved** |
| raw drawing difference | | PSNR 46 to 48 dB against the 10-sample drawing |
| picture changes per 10 s (q) S32 / S21 / S04 | 13.3 / 0.0 / 0.0 | 13.3 / 0.0 / 0.0 |
| motion energy (q) S32 / S21 / S04 | 3.15 / 1.95 / 3.03 | 3.16 / 1.96 / 3.04 |
| longest still (q) | 0.0 s in all | 0.0 s in all |
| sharpness S32 / S21 / S04 | 92.9 / 88.7 / 108.8 | 92.8 / 88.7 / 108.7 |
| noise crawl S32 / S21 / S04 | 1.00 / 1.27 / 1.37 | 1.00 / 1.27 / 1.35 |
| flash (3-shot clip) | pass, no warnings | pass, no warnings |
| critic (Opus) | | **same** |

The (q) picture-change numbers are per shot clip, not a whole film, so only the before and after matter. The critic
could not tell the pairs apart at phone or TV size. It checked eight consecutive dark-fog frames, a 16× amplified
shimmer map, the face's eyes, brows and mouth, and the bright street's edges. Neither side crawled more.
Limits: three shots of one story, and dark, fog-heavy sets other than moving-day's weren't tried. The denoiser is what
hides the sample count, so a story with more fog or bloom could differ. The first real film should be looked at.

**Recommendation: ship it.** `samples` 10 → 6 on `final`, about 26% fewer runner-minutes for every final, craft numbers
and flash unchanged, critic "same".

```python
# blocky/__main__.py, QUALITY
-    "final": {"res": [540, 960], "samples": 10, "step": None},
+    "final": {"res": [540, 960], "samples": 6, "step": None},
```

The proof (4 samples at 270×480) is unaffected. `docs/engine.md` and `render-throughput.md` table 1 say 10 samples and
need the same edit. A cheap guard: have `render` print the sample count, so a later A/B can tell which films were
drawn at 6 (it is already in `render-time.json`).

## Change 5: twos for slow pushes

| | on ones (today) | on twos |
|---|---|---|
| **S50**, an authored push (0.085 m/s of camera and target, but close to the photo so it sweeps the frame) | | |
| drawings / wall time | 84 / 10.1 min (7.2 s each) | 42 / 5.3 min (7.6 s each) |
| picture changes per 10 s (q) / motion energy (q) / longest still (q) | 32.0 / 6.68 / 0.0 s | 32.0 / 6.68 / 0.0 s |
| frame-to-frame change in the middle | steady ramp, about 5 to 6 | alternates about 10 and 0.8 |
| flash | pass | pass |
| critic | | **worse, don't ship**: the building steps 4 to 6 px per drawing (15 fps) at TV size, and the caption moving every frame makes the picture tick under it at phone size |
| **S32**, the pack's own push (0.12 m/s, `auto_cam`) | | |
| drawings / wall time | 55 | 28 / 3.4 min (7.3 s each) |
| picture changes per 10 s (q) / motion energy (q) / longest still (q) | 13.3 / 3.15 / 0.0 s | 13.3 / 3.16 / 0.0 s |
| frame-to-frame change | steady 1.6 | alternates about 0.6 and 2.7 |
| critic | | **slightly worse but fine**: steps of about 4 px at 1080 wide (1.4 px at phone size), invisible at phone size, a faint tick on bright vertical edges (the door frames) at TV size |

**The craft metrics cannot see this.** `picture changes`, `motion energy` and `longest still` are the same to the
digit on twos and ones (they sample at 0.25 s and 0.5 s, 4 to 8 times slower than the steps). S50 would have
passed every number and still juddered. Only the critic's frame-by-frame look and the alternating frame diff caught
it. A speed limit in m/s doesn't select the safe shots either: S50 measures slower (0.085 m/s) than S32 (0.12 m/s) and
juddered; what matters is how far the picture sweeps per drawing. The critic's rule of thumb: about 4 px per drawing at
1080 wide or less.

**What it would save.** Counting every drawing across the 9 stories with `ones: "moving"` that build a timeline
(`closing-time`, `dryer-nine`, `ep32-sitter`, `ep43-reading-room`, `ep47-fitting-room`, `ep62-six-riders`,
`mirror-maze`, `moving-day`, `rule-three`; 25,171 drawings now, 14,282 with `ones: "walk"`, so the pack's `moving` adds 76%):

| rule | drawings | saved |
|---|---|---|
| any camera move at or under 0.12 m/s (authored or the pack's) on twos | 18,691 | 25.7%, about 245 runner-min of 950 (but includes S50's kind: **not safe**) |
| **only the pack's own `auto_cam` moves on twos, authored moves stay on ones** | 21,968 | **12.7%, about 120 runner-min of 950** (an upper bound: it doesn't yet keep shots with acting on ones) |

It varies by story: `ep32-sitter` saves 35%, `moving-day` 28%, `rule-three` 20%, `ep43-reading-room` and `ep47-fitting-room`
0% (their slow moves are authored).

**Recommendation: ship only the narrow form, and not before the samples change has been watched on a real film.**
Pack-only moves on twos is "slightly worse but fine" and saves about 12% (about 120 runner-min a final, or about 90
once 6 samples is in); the broad "slow moves" form is "worse, don't ship". The lead's call: 90 to 120 runner-min is
worth a faint TV-size tick only if the owner's views come from phones. The critic's conditions: keep any shot with a
character acting on ones (a face doing something must not step), and put a pack move on ones if it crosses bright
vertical edges in a dark shot, or sweeps over about 4 px per drawing.

```python
# blocky/polish.py
def ones_for_moving(tl: dict, st: dict, p: dict) -> None:
    ones_for_walks(tl, st)
    specs = cam_specs(st, tl, p)
    for s in tl["shots"]:
        if s["step"] != 2:
            continue
        spec = specs.get(s["id"])
        if _static(spec):
            continue
-       s["step"] = 1
+       # the pack's own slow push or arc (<= CAM_SPEED, ~4 px a drawing) stays on twos when nobody acts in the shot;
+       # an authored move, or anyone acting, is drawn on every frame (engine-ab, 2026-11-03: S50 juddered on twos)
+       if spec.get("auto_cam") and not _acting(tl, st, s):
+           continue
+       s["step"] = 1
```

`_acting(tl, st, shot)` doesn't exist yet. It should return true when any `tl["acting"]` key of a cast member falls
inside the shot's time span (ignoring idle motion). `ones_for_walks` already covers walking.

## Both together

Samples at 6 and pack-only twos multiply: about 950 × 0.73 × 0.87 ≈ 600 runner-min, a saving of about 37% against
today's 950 (samples alone: 690, 27%). Per `render-throughput.md`, that is about 10 more finals a day on its own at
today's lane use.

## What wasn't tested

- Playback. Both verdict sets are from frames, not from watching the clips move.
- A story with a bright vertical-edge push (doorways, windows) at the 0.12 m/s limit, which is where the critic expects
  twos to show first.
- 4 or 5 samples (the time scales, but the denoiser's margin wasn't probed), and the proof's pipeline.

## Ship bar: critic scores and the four pace checks (added after the first orchestrator's bar on #177)

The bar is "the Opus critic scores sharpness and smoothness no worse, and the pace checks still pass". Scores are 1 to 10 for
each side, from frames and edge tracking (not playback). The draws used engine commit `ff28ce6` (`blocky/` is unchanged
on main since); the numbers were re-read with `scripts/measure.py` from main after #201 (the 10% near band).

| pair | sharpness A / B | smoothness A / B | no worse on both? |
|---|---|---|---|
| samples 10 vs 6 (worst shot, S32) | 8 / 8 | 8 / 8 | **yes** |
| S50 authored push, ones vs twos | 8 / 8 | 9 / **5** | **no** |
| S32 pack push, ones vs twos | 8 / 8 | 9 / **8** | no, strictly (a faint tick on a TV, same on a phone) |

Pace checks, raw, per shot clip (so well under a whole film's values; the figure that matters is that both sides read
the same). Bars: picture changes per 10 s ≥ 12.5 (0.5 s) and ≥ 14.0 (0.25 s), motion energy (q) ≥ 6.0, longest still (q) ≤ 1.0 s.
"near" is within 10% of a low bar.

| clip (both sides identical) | changes /10 s | changes /10 s (q) | motion energy (q) | longest still (q) |
|---|---|---|---|---|
| S32 (10, 6 samples, ones and twos) | 6.7 block | 13.3 near | 3.15 / 3.16 block | 0.0 ok |
| S21 (10, 6 samples) | 10.0 block | 0.0 block | 1.95 / 1.96 block | 0.0 ok |
| S04 (10, 6 samples) | 10.0 block | 0.0 block | 3.03 / 3.04 block | 0.0 ok |
| S50 (ones and twos) | 20.0 ok | 32.0 ok | 6.68 / 6.68 ok | 0.0 ok |

A single short clip can't meet a whole film's bars, so "block" on S32, S21 and S04 is the clip's size, not the change.
What the test shows is that **no status changes between the two sides of any pair**: no value moved by more than 0.02 in
motion energy, and none moved in the other three. I did not measure a whole film at 6 samples or with twos, so
"the pace checks still pass" for a full story is inferred, not measured. The first film drawn at 6 should be run through
`measure.py` before the change is trusted everywhere.

**Verdict against the bar:**
- **Samples 10 → 6: meets it** (no worse on both axes, pace statuses unchanged). Ship, with the first-film check above.
- **Twos for pack-only moves: does not strictly meet it** (smoothness 9 → 8 on a TV). It is the lead's call
  whether a faint TV-size tick for about 120 runner-min a final is worth it. Twos for authored moves: **does not meet it** (smoothness 9 → 5).
