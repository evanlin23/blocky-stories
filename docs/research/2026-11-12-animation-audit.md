# Animation audit: why the films read choppy (2026-11-12)

For the first orchestrator (issue #177, the 9:15 PM ASK). The owner said the animations "look very low quality, choppy"
and "it's also the visuals". The stories measured were ep124-future-call, ep136-one-answer and ep54-dance-hall, all on
main with `ones: "all"` (#457). The motion numbers come from the timelines, in pure Python, on every frame. The picture
numbers come from real renders at final quality, on this 4-vCPU box in the runner's layout (2 workers × 2 threads).
This box draws about 2× faster than a runner (`engine-ab.md`), so only the ratios carry over. The verdicts are from a
fresh Opus critic that looked at phone size (300 px wide) and TV size (a 1:1 crop of the 1080 frame). Stills are in
`anim-audit/`.

## 1. Drawings per second
| story | length | shots | on twos | unique drawings/s |
|---|---|---|---|---|
| ep124 | 69.5 s | 50 | 0 | 30 |
| ep136 | 62.2 s | 75 | 0 | 30 |
| ep54 | 144.7 s | 98 | 0 | 30 |

`ones: "all"` holds: no shot is on twos, and the render had no repeated frames (critic).

## 2. Character motion (in-shot frames; frames on a cut are excluded)
| | ep124 | ep136 | ep54 |
|---|---|---|---|
| biggest per-frame head-yaw jump | 8.4° | 4.9° | 7.6° |
| biggest per-frame leg jump | 12.4° | 6.0° | 23.3° (onset of a run) |
| body turns over 220°/s | 7 frames (peak 332) | 0 | 14 frames, **peak 2,856°/s (a one-frame snap)** |
| keys | eased (smoothstep, 0.25 s) | same | same |
| overlap (head leads, arms follow) | none: every channel moves on the same blend | none | none |
| idle motion | on | on | on |
| walk | legs phase-locked to distance, so no foot slide; eased starts | same | same |

The snaps are **a walk that switches its facing in one frame**: when a walk starts or stops, the body jumps between
its keyed yaw and its direction of travel. Keyed yaw also turns the long way round: 180° to -90° goes through 270°.
The shot cuts held another 5 snaps (ep124) and 27 (ep54) with `blend: 0`, but those are re-staging and can't be seen.

## 3. Camera
| | ep124 | ep136 | ep54 |
|---|---|---|---|
| shots with a 3D camera move | 13/50 | 72/75 | 22/98 (plus the pack's cam_push/arc) |
| post punch-ins | 5 | 4 | 10 |
| mid-shot angle-cut reframes (zoom step 10 to 13%) | 12 | 0 | 39 |
| frames cropped to 1.10× or more | 28% | 4% | 34% |
| tightest crop | 458 px of 540, so 2.36× upscale | 469 px | 458 px |
| crop stepping | none: `post.to_output` resamples a float box with Lanczos (subpixel already) | | |
| new shot or punch every 1 to 2 s in 0:04 to 0:10 | yes, largest gap 1.63 s | yes, 1.10 s | yes, 1.27 s |

ep136 has 4 m dollies in 0.37 s (11 m/s), whips on purpose.

## 4. Picture
| | value |
|---|---|
| drawn | 540×960, Cycles 6 samples + OIDN (albedo, normal), then Lanczos ×2 to 1080×1920 |
| sharpen | UnsharpMask r1.4, 55%, before bloom and grade |
| bloom | threshold 0.6, amount 0.35, two blurs (wide halo) |
| motion blur | off; turning it on does nothing (poses are set per frame, not keyed: bit-identical frames) |
| encode | x264 crf 17, so the crf ≤ 18 ask is met already |

## 5. A/B (same clips: ep124 S31–S32 acting; ep54 S04–S06 camera)
| candidate | cost (s/drawing, box) | sharpness Lap / p99 (ACT) | critic phone / TV | verdict |
|---|---|---|---|---|
| A: today | 6.49 | 155 / 44.7 | n/a | n/a |
| B: 60 fps at 540 | 5.98 ×2 drawings = 1.84× | 156 / n/a | slight / slight, only on fast moves | no |
| C: 720×1280 at 30 | 10.06 = 1.55× | 191 / 51.3 | none / slight to clear (eyes, brows, bevels) | yes if #1 spends: beats B at equal cost |
| D: EEVEE | 7.67 (CAM 9.67): slower | 159 | worse: washed-out skin, no contact shadows or fog | no. It runs (llvmpipe software GL) but looks wrong |
| E: motion blur | same | same | none | no: no effect |
| F: sharpen moved after the grade | 0 | 148 / 41.8 | none | no |
| F2: F plus the old sharpen, bloom threshold 0.85 | 0 | 167 / 47.0 | none to slight / slight; faint grain in flat areas | yes |
| acting overlap and turn cap (ep54 S90) | 0 | same | **big / big**: "that pop is exactly what choppy means" | **yes, the best value** |
| punch-ins at most 4 | 0 | n/a | reads cleaner, won't be missed | yes |
| new shot every 1 to 2 s at 0:04 to 0:10 | n/a | n/a | already met | no change |

## Left over
The critic's biggest remaining "low quality" cause is lifeless faces under the narration: in ACT-A, over 3 s, it saw
no change of mouth or blink. The engine has blinks (a 2 to 5 s cycle), talk flaps and idle, but a narrated "me" has no
mouth moves of its own unless the builder keys `mouth`/`flap`. Next, test auto mouth flaps on the speaker's
lines and a reaction-face swap on key words. Nothing here needs a new renderer: Blender isn't "fried".
