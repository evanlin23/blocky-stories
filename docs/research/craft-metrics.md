# Craft metrics: what "high quality" measures as (2026-11-03)

The owner, 2026-11-03: "we should care a lot about the micro and the macro. Like making it so the animations feel
real and clean and good and transitions and effects on top, making it look higher quality. we should do research on
what this actually looks like, and actually measure it, not just vibes."

This file defines each metric and how it's measured, gives our numbers on nine films, and sets provisional targets.
`scripts/measure.py` computes them (ffmpeg and numpy, free). The hits' numbers come from the owner's browser extension
(`craft-metrics-protocol.md`: 17 fast-rising blocky Shorts plus 3 of ours, measured in the browser without
downloading).

```
python scripts/measure.py out/<story>.mp4 --story stories/<story> [--mix mix.json] [--json o.json]
python scripts/measure.py --story stories/<story>          # no film: the edit's metrics only
```

## Where the numbers come from
- **The film** (`macro.*`, `sound.*`): decoded by ffmpeg at 108 × 192 (1/10 size) for the picture and 48 kHz mono
  for the sound. These are the numbers a viewer gets, and the browser protocol measures the same ones on other
  people's Shorts.
- **The edit** (`spec.*`, `micro.*`): `story.json` and `voice-timings.json` go through `blocky/timeline.py`, and
  `blocky/acting.py` and the shot keys place every character and camera at each moment. This is exact for our films
  (cuts, captions, camera keys, poses) and works with no film at all. That's how back-row is measured: its final was
  made in `evanlin23/content`, which this session couldn't reach. Its picture and sound numbers come from the
  browser protocol (video 18).
- **The mix report** (`mix.json` in each `film-<story>` artifact): the stems' loudness, for the voice-to-bed gap.

The edit's numbers check out against the pixels. On ep38, 68 of the edit's 72 cuts are found in the film to the frame
(the pixel detector also finds 3 cuts that aren't in the edit: a flash, a shake, a fade). For every film, cuts per 10 s
from the pixels and from the edit agree within 0.9 (table below).

## Macro metrics (the whole picture)

| Metric | Method | Key |
|---|---|---|
| Cuts per 10 s, shot lengths | **Edit:** each shot boundary in the timeline. **Film:** a frame whose mean luma change is over 4.5% and 4× the median of the 16 frames around it, *and* whose 32-bin luma histogram moves over 0.25 (L1). At most one cut per 4 frames, none in the first or last 0.2 s. Lengths: median, 90th percentile, max, and the share of shots over 2 s | `spec.cuts_per_10s`, `spec.shot_median_s`, `spec.shot_p90_s`, `spec.shots_over_2s_share`, `macro.cuts_per_10s` |
| Picture changes per 10 s | The browser method (and the Skylox study's 0.5 s idea): each frame as an 18 × 32 grid of mean luma, compared with the frame 0.5 s later. A change is a mean grid difference over 0.04. Counted per 10 s (20 is the most possible). `_q` uses 0.25 s steps (40 possible) | `macro.picture_changes_per_10s`, `macro.picture_changes_per_10s_q` |
| Camera-motion share | **Edit (main):** the camera without its handheld drift, sampled 10 times a second. It moves if position or target goes over 3 cm/s, the aim turns over 1°/s, the lens changes over 0.3 mm/s, or a punch-in or the polish pack's crop zooms or slides. **Film:** the global shift between frames two apart by phase correlation, over 0.4 px a frame at 1080 wide (pans and slides only; it misses pushes and zooms, so it reads low) | `spec.camera_move_share`, `macro.camera_motion_share` |
| Motion energy | The mean absolute luma change between frames two apart (two, so a 15 fps drawing isn't read as still), in % of full scale, per second. Optical flow (OpenCV Farneback, mean magnitude in px per frame at 1080 wide) is added when OpenCV is installed. `_q` is the browser's 0.25 s version | `macro.motion_energy_mean`, `macro.flow_mean_px_per_frame`, `macro.motion_energy_q` |
| Longest still stretch | The longest run of frames with under 0.35% change over two frames, no global shift and no cut. `_q`: the longest run of 0.25 s samples under 0.006 grid change (the browser's) | `macro.longest_still_s`, `macro.longest_still_q_s` |
| Brightness, saturation, contrast | Every third frame. Brightness: mean Rec. 709 luma on the sRGB values (0 to 1). Saturation: HSV (max − min) / max, over pixels brighter than 0.04. Contrast: the standard deviation of luma (RMS). Plus the first 3 s' brightness, the share of frames under 0.12 mean luma (dark), and dips to black (under 0.03) | `macro.brightness_mean`, `macro.brightness_first_3s`, `macro.dark_frame_share`, `macro.saturation_mean`, `macro.contrast_mean`, `macro.black_dips` |
| Faces over 1/5 of the frame width | **Edit:** each visible cast member's head (eyes at 1.5 m × height, head 0.42 m × height wide) projected through the shot's camera (Blender's vertical sensor fit, 24 mm tall, with the punch-in zoom). Inside the frame and at least 0.2 of its width counts. Sampled 10 times a second; whether anything stands in front isn't checked | `spec.face_big_share`, `spec.face_big_first_3s` |
| Captions | **Edit:** the share of the film with a caption up (the union of caption spans), words per caption (mean, median, max), and size: a capital's height and the median caption block's height, each over the frame height | `spec.caption_share`, `spec.caption_words_median`, `spec.caption_letter_share`, `spec.caption_block_share` |
| Transitions | **Edit:** hard cuts, each effect kind (`punch`, `shake`, `black`, `flash`, `static`, `red`), the polish pack's punch-ins and whooshes, and whether the film fades in and out. Punch-ins per 10 s. **Film:** dips to black | `spec.transitions`, `spec.punch_per_10s` |

## Micro metrics (how the animation and sound feel)

| Metric | Method | Key |
|---|---|---|
| Characters move | The share of shots where a visible, in-frame character changes pose (position, facing, arms, head, lean, legs or mouth, by over 0.01) at any of the 10-a-second samples. Blinks don't count | `micro.character_motion_shot_share` |
| Easing | `acting.position` moves at a constant speed between two position keys. So a walk that doesn't continue from a key moving the same way starts or stops dead: a speed change over 0.5 m/s in one frame (about 15 m/s², where a person starting to walk is about 2). The share of walk ends that are dead. Also: camera keys that stop dead in the middle of a shot (a key between two moving segments: smoothstep halts at every key) | `micro.walk_dead_end_share`, `spec.camera_midshot_stops` |
| Secondary motion | Pose keys that aren't a walk (head, arms, side, lean, tremble, look) per minute of film. The rig has no automatic secondary motion (no hair or clothes follow-through, no breathing) | `micro.secondary_keys_per_min` |
| Idle frames | The share of 1 s windows with someone on screen in which nobody moves at all (blinks excepted) | `micro.idle_window_share` |
| Drawn on twos | The share of frames that repeat the one before (under 0.15% change). A shot with `step: 2` draws 15 frames a second, and the polish pack's crop motion hides some repeats but not the characters'. Also the share of frames in `step ≥ 2` shots | `macro.held_frame_share`, `spec.step2_frame_share` |
| Mouth and caption sync | For each line's first caption (it follows a gap, so the voice onset under it is clean), the first 5 ms window within −150 to +250 ms that rises 12 dB over the floor before it. The offset from the caption's word time, in ms (median and 90th percentile of the absolute value). The same for mouth flaps, but none of the nine films has any: the narrator is a voice-over, and no character speaks on screen | `micro.caption_sync_p90_ms`, `micro.flap_sync_p90_ms` |
| Sound events per 10 s | **Edit:** the builder's `sfx`, the polish pack's whooshes, hits and risers, and one per burst of footsteps (a walk of two steps or more), per 10 s. **Film:** spectral-flux onsets (1024-sample frames, a peak 6 MADs over a 2 s moving median, at least 80 ms apart) outside the voice's lines, per 10 s. Under the voice, effects can't be told from syllables in a mixed film | `spec.sound_events_per_10s`, `sound.sfx_onsets_per_10s_unvoiced`, `sound.onsets_per_10s` |
| Ambience (no digital silence) | The share of 50 ms windows under −60 dBFS, and the longest run | `sound.silence_share`, `sound.longest_silence_s` |
| Voice over the bed | **Stems (main):** the voice's LUFS minus the power sum of music and ambience (`mix.json`). **Film:** the 75th percentile of 50 ms RMS inside lines minus the median in the gaps between lines (rougher: tails and effects land in the gaps) | `sound.voice_bed_gap_db`, `sound.voice_bed_gap_audio_db` |
| Loudness | ffmpeg `ebur128=peak=true`: integrated LUFS, loudness range, true peak | `sound.lufs`, `sound.lra`, `sound.true_peak_dbtp` |
| Harshness | The share of spectral energy above 4 kHz: over the film, the worst 5 s window, and the biggest jump between neighbouring 5 s windows (scratch, hiss, clicks: ep36) | `sound.hf_share`, `sound.hf_share_max_5s`, `sound.hf_jump_max` |

## Our numbers (2026-11-03)

| Metric | back-row ★ | ep20 ✗ | ep38 ✗ | knock-back ✗ | closing-time | ep36 | ep55 | floor-13 | ep34 |
|---|---|---|---|---|---|---|---|---|---|
| Length (s) | 137.6 | 135.37 | 139.5 | 146.97 | 134.7 | 142.7 | 135.4 | 92.5 | 143.07 |
| Picture changes / 10 s (0.5 s) | – | 6.8 | 7.8 | 10.2 | 6.8 | 6.8 | 9.6 | 10.4 | 6.7 |
| Picture changes / 10 s (0.25 s) | – | 8.1 | 7.6 | 11.2 | 8.1 | 8.2 | 11.1 | 13.1 | 8.4 |
| Cuts / 10 s (edit) | 5.89 | 4.73 | 5.16 | 5.31 | 5.05 | 5.4 | 6.87 | 7.03 | 5.45 |
| Cuts / 10 s (pixels) | – | 4.8 | 5.09 | 6.19 | 5.05 | 5.26 | 7.02 | 7.35 | 5.52 |
| Shot median (s) | 1.67 | 2.2 | 1.93 | 1.67 | 1.73 | 1.85 | 1.45 | 1.35 | 1.8 |
| Shot p90 (s) | 2.4 | 2.77 | 2.46 | 3.21 | 3.05 | 2.58 | 1.99 | 2.25 | 2.44 |
| Shots over 2 s | 0.22 | 0.585 | 0.452 | 0.266 | 0.377 | 0.372 | 0.096 | 0.167 | 0.329 |
| Longest still (s) | – | 0.97 | 0.93 | 0.93 | 1.67 | 1.07 | 1.0 | 1.1 | 1.3 |
| Motion energy (%) | – | 1.52 | 1.42 | 2.24 | 1.56 | 1.52 | 1.95 | 2.68 | 1.63 |
| Optical flow (px/frame) | – | 1.82 | 1.06 | 2.38 | 1.9 | 1.24 | 2.11 | 2.81 | 1.15 |
| Camera moving (edit) | 0.709 | 0.323 | 0.458 | 0.656 | 0.557 | 0.097 | 0.801 | 0.038 | 0.119 |
| Camera moving (pixels, pans only) | – | 0.179 | 0.119 | 0.209 | 0.156 | 0.139 | 0.139 | 0.077 | 0.11 |
| Punch-ins / 10 s | 0.44 | 0.15 | 0.29 | 0.27 | 0.07 | 0.0 | 0.0 | 0.0 | 0.0 |
| Brightness | – | 0.222 | 0.286 | 0.257 | 0.217 | 0.393 | 0.443 | 0.295 | 0.446 |
| Brightness, first 3 s | – | 0.177 | 0.395 | 0.095 | 0.17 | 0.343 | 0.676 | 0.323 | 0.546 |
| Dark frames | – | 0.226 | 0.044 | 0.164 | 0.028 | 0.025 | 0.003 | 0.223 | 0.001 |
| Saturation | – | 0.619 | 0.445 | 0.7 | 0.639 | 0.386 | 0.398 | 0.346 | 0.355 |
| Contrast | – | 0.177 | 0.21 | 0.191 | 0.165 | 0.193 | 0.192 | 0.263 | 0.208 |
| Dips to black | – | 3 | 2 | 2 | 0 | 1 | 0 | 8 | 0 |
| Face over 1/5 width | 0.446 | 0.326 | 0.467 | 0.338 | 0.346 | 0.51 | 0.431 | 0.507 | 0.447 |
| Big face in first 3 s | no | yes | yes | yes | yes | yes | yes | yes | yes |
| Caption on screen | 0.98 | 0.953 | 0.953 | 0.979 | 0.942 | 0.957 | 0.97 | 0.968 | 0.975 |
| Words per caption (mean) | 2.46 | 2.55 | 2.65 | 2.35 | 2.6 | 2.61 | 2.59 | 2.38 | 2.58 |
| Caption capital height / frame | 0.031 | 0.031 | 0.031 | 0.031 | 0.031 | 0.031 | 0.031 | 0.031 | 0.031 |
| Shots where a character moves | 0.378 | 0.415 | 0.411 | 0.316 | 0.435 | 0.551 | 0.245 | 0.333 | 0.266 |
| Walks | 23 | 10 | 2 | 2 | 7 | 21 | 17 | 3 | 13 |
| Walk ends that stop dead | 1.0 | 0.8 | 1.0 | 1.0 | 0.929 | 1.0 | 1.0 | 1.0 | 1.0 |
| Idle 1 s windows | 0.352 | 0.192 | 0.463 | 0.253 | 0.263 | 0.484 | 0.404 | 0.291 | 0.409 |
| Secondary pose keys / min | 25.3 | 23.0 | 27.5 | 27.4 | 35.2 | 49.2 | 5.3 | 38.9 | 21.8 |
| Repeated frames (on twos) | – | 0.36 | 0.451 | 0.341 | 0.425 | 0.555 | 0.354 | 0.442 | 0.486 |
| Frames in step-2 shots | 0.765 | 0.787 | 0.814 | 0.834 | 0.989 | 1.0 | 1.0 | 0.853 | 0.94 |
| Caption sync p90 (ms) | – | 58.0 | 62.0 | 111.0 | 120.0 | 65.0 | 59.0 | 130.0 | 74.0 |
| Sound events / 10 s (edit) | 3.42 | 2.14 | 1.22 | 3.27 | 4.97 | 2.24 | 2.36 | 3.03 | 1.4 |
| Onsets / 10 s between lines (film) | – | 0.0 | 1.7 | 32.46 | 0.0 | 0.0 | 3.69 | 7.36 | 5.84 |
| Digital silence | – | 0.0022 | 0.0036 | 0.0252 | 0.0004 | 0.0032 | 0.0026 | 0.0086 | 0.0 |
| Voice over bed (dB, stems) | – | 10.7 | 8.6 | – | – | 9.0 | 9.9 | 9.6 | 8.2 |
| Voice over bed (dB, film) | – | 4.1 | 7.8 | 4.3 | -0.4 | 7.1 | 11.5 | 3.2 | 9.7 |
| Loudness (LUFS) | – | -14.1 | -14.1 | -14.1 | -14.3 | -14.1 | -14.1 | -14.2 | -14.1 |
| True peak (dBTP) | – | -1.7 | -1.6 | -1.7 | -2.1 | -1.7 | -1.7 | -2.0 | -1.7 |
| Above 4 kHz, worst 5 s | – | 0.053 | 0.052 | 0.0568 | 0.0459 | 0.0481 | 0.0419 | 0.0361 | 0.0512 |
| Above 4 kHz, biggest jump | – | 0.0277 | 0.0198 | 0.0361 | 0.0225 | 0.0277 | 0.0145 | 0.0182 | 0.0123 |

★ our hit (82.6% chose to view; edit metrics only, its final is in `evanlin23/content`). ✗ our flops (61 to 65%). The other five are the newest finals (`film-<story>` artifacts of 2026-11-03, and `legacy/` for closing-time), all drawn before the polish pack merged. Each was measured against the story files at the commit its film was drawn from (the timeline matches the film's length to the frame in all nine). "–": not measured (no film, or no mix report).

## Targets (provisional)

| Metric | Target | back-row | flops (ep20, ep38, knock-back) | newest five |
|---|---|---|---|---|
| Picture changes / 10 s (0.5 s) (`macro.picture_changes_per_10s`) | 11 to 16 | – | 6.8, 7.8, 10.2 | 6.8, 6.8, 9.6, 10.4, 6.7 |
| Cuts / 10 s (edit) (`spec.cuts_per_10s`) | 5.5 to 8.0 | 5.89 | 4.73, 5.16, 5.31 | 5.05, 5.4, 6.87, 7.03, 5.45 |
| Shots over 2 s (`spec.shots_over_2s_share`) | ≤ 0.25 | 0.22 | 0.585, 0.452, 0.266 | 0.377, 0.372, 0.096, 0.167, 0.329 |
| Shot p90 (s) (`spec.shot_p90_s`) | ≤ 2.5 | 2.4 | 2.77, 2.46, 3.21 | 3.05, 2.58, 1.99, 2.25, 2.44 |
| Longest still (s) (`macro.longest_still_s`) | ≤ 1.5 | – | 0.97, 0.93, 0.93 | 1.67, 1.07, 1.0, 1.1, 1.3 |
| Motion energy (%) (`macro.motion_energy_mean`) | ≥ 1.5 | – | 1.52, 1.42, 2.24 | 1.56, 1.52, 1.95, 2.68, 1.63 |
| Camera moving (edit) (`spec.camera_move_share`) | ≥ 0.65 | 0.709 | 0.323, 0.458, 0.656 | 0.557, 0.097, 0.801, 0.038, 0.119 |
| Punch-ins / 10 s (`spec.punch_per_10s`) | ≥ 0.4 | 0.44 | 0.15, 0.29, 0.27 | 0.07, 0.0, 0.0, 0.0, 0.0 |
| Brightness (`macro.brightness_mean`) | ≥ 0.25 | – | 0.222, 0.286, 0.257 | 0.217, 0.393, 0.443, 0.295, 0.446 |
| Brightness, first 3 s (`macro.brightness_first_3s`) | ≥ 0.3 | – | 0.177, 0.395, 0.095 | 0.17, 0.343, 0.676, 0.323, 0.546 |
| Dark frames (`macro.dark_frame_share`) | ≤ 0.15 | – | 0.226, 0.044, 0.164 | 0.028, 0.025, 0.003, 0.223, 0.001 |
| Saturation (`macro.saturation_mean`) | ≥ 0.35 | – | 0.619, 0.445, 0.7 | 0.639, 0.386, 0.398, 0.346, 0.355 |
| Contrast (`macro.contrast_mean`) | ≥ 0.15 | – | 0.177, 0.21, 0.191 | 0.165, 0.193, 0.192, 0.263, 0.208 |
| Face over 1/5 width (`spec.face_big_share`) | ≥ 0.4 | 0.446 | 0.326, 0.467, 0.338 | 0.346, 0.51, 0.431, 0.507, 0.447 |
| Caption on screen (`spec.caption_share`) | ≥ 0.9 | 0.98 | 0.953, 0.953, 0.979 | 0.942, 0.957, 0.97, 0.968, 0.975 |
| Words per caption (median) (`spec.caption_words_median`) | ≤ 3 | 2.0 | 3.0, 3.0, 2.0 | 3.0, 3.0, 3.0, 2.0, 3.0 |
| Repeated frames (on twos) (`macro.held_frame_share`) | ≤ 0.15 | – | 0.36, 0.451, 0.341 | 0.425, 0.555, 0.354, 0.442, 0.486 |
| Shots where a character moves (`micro.character_motion_shot_share`) | ≥ 0.5 | 0.378 | 0.415, 0.411, 0.316 | 0.435, 0.551, 0.245, 0.333, 0.266 |
| Walk ends that stop dead (`micro.walk_dead_end_share`) | ≤ 0.25 | 1.0 | 0.8, 1.0, 1.0 | 0.929, 1.0, 1.0, 1.0, 1.0 |
| Idle 1 s windows (`micro.idle_window_share`) | ≤ 0.3 | 0.352 | 0.192, 0.463, 0.253 | 0.263, 0.484, 0.404, 0.291, 0.409 |
| Caption sync p90 (ms) (`micro.caption_sync_p90_ms`) | ≤ 120 | – | 58.0, 62.0, 111.0 | 120.0, 65.0, 59.0, 130.0, 74.0 |
| Sound events / 10 s (edit) (`spec.sound_events_per_10s`) | ≥ 4.0 | 3.42 | 2.14, 1.22, 3.27 | 4.97, 2.24, 2.36, 3.03, 1.4 |
| Digital silence (`sound.silence_share`) | ≤ 0.005 | – | 0.0022, 0.0036, 0.0252 | 0.0004, 0.0032, 0.0026, 0.0086, 0.0 |
| Voice over bed (dB; stems, else film) (`sound.voice_bed_gap_db`) | 8.0 to 14.0 | – | 10.7, 8.6, 4.3 | -0.4, 9.0, 9.9, 9.6, 8.2 |
| Loudness (LUFS) (`sound.lufs`) | -15.0 to -13.0 | – | -14.1, -14.1, -14.1 | -14.3, -14.1, -14.1, -14.2, -14.1 |
| True peak (dBTP) (`sound.true_peak_dbtp`) | ≤ -1.0 | – | -1.7, -1.6, -1.7 | -2.1, -1.7, -1.7, -2.0, -1.7 |
| Above 4 kHz, worst 5 s (`sound.hf_share_max_5s`) | ≤ 0.08 | – | 0.053, 0.052, 0.0568 | 0.0459, 0.0481, 0.0419, 0.0361, 0.0512 |
| Above 4 kHz, biggest jump (`sound.hf_jump_max`) | ≤ 0.04 | – | 0.0277, 0.0198, 0.0361 | 0.0225, 0.0277, 0.0145, 0.0182, 0.0123 |

**How they were set.** Edit metrics: past back-row, our one hit, and outside the range of the three flops where they
separate (cuts, long shots, camera moves, punch-ins, sound events). Picture metrics: the Skylox study's 11 to 15 picture
changes per 10 s, our own "frame 1 is lit" rule and the polish pack's 1.5 s still bar. Acting metrics: craft bars, not
hit data. back-row itself misses some of them (characters move in 38% of its shots), so they can't predict views yet.
They make it look better. Sound: the house master and our harsh-sound checks.

**Warnings now, blocks later.** Every target only warns until the browser study's hit numbers arrive. Then each
target the hits confirm (the 17 hits sit inside the range, and back-row sits nearer them than the flops) becomes a
block in `qa`. A target the hits contradict gets moved to their range. Re-set the ranges here and in
`scripts/measure.py` → `TARGETS` together.

## The biggest gaps
Ranked by how far we are from the target and how many films it hits.

1. **Walks start and stop dead, in every film.** 93 to 100% of walk ends go from full speed to zero in one frame
   (the target is at most 25%). `acting.position` interpolates linearly between keys, and only the leg swing eases.
   This is an engine fix (ease the position over about 0.2 s at each start and stop, and keep the footsteps on the
   eased distance). It isn't a story fix.
2. **The characters hold still too much.** A character moves in 25 to 55% of shots (target 50%+). 19 to 48% of the
   1 s windows with someone on screen have nobody moving at all (target 30% at most). back-row is no better (38%,
   35%), so this is craft, not what made it hit. The fixes: idle keys (a weight shift, a head turn, a look) in any
   shot over 1 s, and an automatic breathing sway in the rig.
3. **Drawn on twos.** 34 to 56% of frames repeat the one before (target 15% at most). 77 to 100% of frames are in
   `step: 2` shots, so characters move at 15 drawings a second. The polish pack's crop moves smooth the camera but not
   the acting. `step: 1` on shots with a walk or a gesture doubles their draw time, so test it on one story first.
4. **The picture changes 6.7 to 10.4 times per 10 s** (0.5 s method), against the Skylox study's 11 to 15. This is
   provisional until the browser study measures hits the same way (videos 18 to 20 calibrate our three). Cuts are
   already 4.7 to 7.0 per 10 s, so the gap is movement inside a shot.
5. **The newest finals barely punch in or move the camera.** Punch-ins: 0 to 0.07 per 10 s in the newest five, against
   back-row's 0.44. Camera moving: 4 to 12% of the time in ep34, ep36 and floor-thirteen, against back-row's 71%.
   **The polish pack closes most of the punch-in gap.** On ep32-sitter's edit (polish on vs off): punch-ins 0 → 2.07
   per 10 s, sound events 1.4 → 7.7 per 10 s. Camera moving only rises 12 → 27%, because the 3% drift is gentle, mostly
   under the 0.02-per-second zoom threshold. Still-camera shots need a real camera move in the shot keys (a push or a
   slide), not only the drift. 2.07 punch-ins per 10 s is nearly 5× back-row's rate, so check the next polished
   finals for punch-in fatigue.
6. **Few sound events.** 1.2 to 3.4 per 10 s, against a target of 4. This was before the pack. Its whooshes and hits
   lift ep32 to 7.7, so polished films should pass.
7. **Two flops opened dark.** The first 3 s' mean brightness was 0.10 in knock-back and 0.18 in ep20 (target 0.30).
   ep38, the third flop, opened at 0.40, so brightness alone doesn't explain the swipe. The newest five open at 0.17
   to 0.68 (closing-time is the dark one).

**Already on target, keep it:** loudness (−14.1 to −14.3 LUFS), true peak (−1.6 to −2.1 dBTP), harshness (at most
5.7% above 4 kHz in any 5 s), no digital silence (at most 0.9% of the film, except knock-back at 2.5%, which predates
the bed), captions (94 to 98% of the film, 2.4 to 2.7 words, sync 58 to 130 ms at p90), faces over 1/5 of the width
in 33 to 51% of the film, and cuts on the edit's words (the pixel cuts match the edit).

**back-row vs the flops, in one line:** more cuts (5.9 against 4.7 to 5.3 per 10 s), fewer long shots (22% over 2 s
against 27 to 59%), more camera movement (71% against 32 to 66%), more punch-ins (0.44 against 0.15 to 0.29 per 10 s)
and more sound events (3.4 against 1.2 to 3.3). No difference in faces, captions or character motion.

## Using it
- **qa** runs `scripts/measure.py` on every final and pastes the table into its notes (`.claude/agents/qa.md`).
- **Builders** can run it with no film (`--story`) before a render to check the edit metrics.
- **Every Monday**, with `metrics/summary.md`: measure the week's finals, append them to `craft-metrics-ours.json`,
  and compare the craft numbers with Studio's "chose to view" and average % viewed.
- When the hits' numbers arrive (`craft-metrics-hits.jsonl`), re-set "Targets" from them and switch the confirmed
  ones to blocks.
