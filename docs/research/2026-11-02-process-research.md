# Blocky story Shorts: free tools and techniques (research, 2026-11-03)

How sure each finding is: **[V]** means checked against a primary source (official repo or docs). **[S]** means it comes only from secondary coverage. **[U]** means I couldn't verify it, so test before relying on it. The fetches to support.google.com and developer.blender.org were blocked in this session, so the YouTube policy and Blender 5.0 points rely on press coverage and search snippets.

## 1. Rendering on free CPU runners

**A. Tune Cycles for 10 samples. Effort is low: a few lines in the render setup.**
- **Denoising:** turn on OpenImageDenoise with **Albedo + Normal** passes and prefilter "Accurate". The manual warns that with no prefilter at low samples, "None can blur out details". [V, Blender manual](https://docs.blender.org/manual/en/4.1/render/cycles/render_settings/sampling.html)
- **Adaptive sampling:** set max samples to 16–24 with `adaptive_threshold` 0.05–0.1. Flat blocky surfaces converge early, so the average sample count often lands below 10 while the dark corners get more.
- **Light paths:** cap bounces at 2–3 diffuse, 0–1 glossy and 0 transmission, and turn caustics off. Turn on Fast GI approximation (AO) and **Simplify** (texture limit, AO bounces). Blocky shading gains almost nothing from deep bounces.
- **Path guiding** runs only on CPU and helps interiors lit by a few lamps. It costs time per sample, so A/B test it on one shot.
- **Flicker:** OIDN at very low samples can "boil" from frame to frame. Seeding noise by frame (`use_animated_seed`) together with denoising can raise the flicker score. Keep the seed fixed, or measure both on one shot.

**B. Persistent Data. Effort is low.** It keeps the BVH and synced scene data between frames and re-renders. Blender's commit claims "on average ... a 3x speedup" on animated scenes, at a memory cost. [V, BlenderNation](https://www.blendernation.com/2021/04/10/cycles-gets-massive-performance-boost-for-animations/)
- It only helps when **one Blender process renders a range of frames** (`-s A -e B -a`). Starting a new process per frame gets nothing.
- Make each shard render a contiguous range.
- Watch RAM: runners have 16 GB.

**C. EEVEE headless. Effort is medium, and success is uncertain.**
- EEVEE (Next, 4.2+) is OpenGL/Vulkan only. It needs a GL context, which means a GPU or software GL. Old dev threads say it needs a display; the standard workaround is `xvfb-run`. [S, devtalk](https://devtalk.blender.org/t/blender-2-8-unable-to-open-a-display-by-the-rendering-on-the-background-eevee/1436)
- Mesa **llvmpipe** gives software GL 4.5 over EGL with no GPU [S, yrom.net](https://www.yrom.net/blog/2025/07/27/develop-opengl-apps-in-docker-without-gpu/). One vendor claims EEVEE-Next returns black frames when run headless [S, iRender](https://irendering.net/eevee-next-headless-dilemma-cloud-render-farm-guide/).
- **[U]**: I found nobody confirming Blender 5.0 EEVEE on llvmpipe. The test is about an hour: run `xvfb-run -a blender -b -E BLENDER_EEVEE ...` on one shot in Actions.
- Even if it works, llvmpipe EEVEE may not beat tuned Cycles CPU. Try it only after A and B.

**D. Upscaling. Not worth it.**
- Real-ESRGAN is BSD-3 [S](https://aireiter.com/blog/real-esrgan-guide-download-gui). Its ncnn build hasn't been updated since 2022, and the only published speeds are on a V100 GPU (AnimeVideo-v3 at 10 fps, 1080p) [V, comparisons](https://mintlify.com/xinntao/Real-ESRGAN/resources/comparisons). On a 4-vCPU runner it would take seconds per frame.
- **Do instead:** render at **720x1280** with OIDN and upscale with ffmpeg `scale=1080:1920:flags=lanczos`. The time from B can pay for the 1.8x pixel increase.

## 2. Blender add-ons and libraries you can drive from scripts

- **Rigify** ships with Blender, GPL, and `bpy.ops.pose.rigify_generate()` works from a script. The "basic" metarig suits blocky limbs. For six rigid boxes, plain object parenting plus drivers is simpler than any rig, so use Rigify only if limbs need to bend. Effort: low.
- **Camera Shakify** is GPL-3 code with CC0 shake data. It adds real recorded handheld shake to a camera, for subtle creepy drift. Version 0.5+ needs Blender 4.4+. [V, GitHub](https://github.com/EatTheFuture/camera_shakify) Keep the amplitude small, because large shake fails flash and motion checks. Effort: low.
- **Poly Haven:** CC0 HDRIs, textures and models through a public API. Script night or overcast HDRIs and "dirty" textures to make sets look less plain. [U on current API terms; assets are CC0]. Effort: low.
- **Procedural buildings:** I found no free, maintained GPL generator. The marketplace ones cost $7–60 and fall outside a $0 budget. [S](https://superhivemarket.com/products/scifix) Build our own **Geometry Nodes** "street kit" instead (windows, doors, lamp posts, fog cards) as one `.blend` asset that `set.py` instances. Effort: medium.
- **Lighting presets without add-ons:**
  - Make a `lights.py` library of 4–5 looks: moonlit blue key with orange practical, single flickerless streetlamp, TV glow, red emergency.
  - Add World volume scatter or fog cards for depth, plus contact-shadow AO.
  - This addresses "plain" sets more than any add-on would.

## 3. TTS (local, licence allows monetized use)

| Option | Why it fits | Licence | Effort |
|---|---|---|---|
| **Kokoro, kept but tuned** | Use its native `speed=1.3–1.45` instead of ffmpeg `atempo`, which sounds less phasey | Apache-2.0 | Very low |
| **Chatterbox-Turbo / Nano** (Resemble) | More expressive, with `[laugh]`, `[cough]` and similar tags. Nano (110M) runs "3x faster than realtime on 8 CPU cores" | MIT; output carries an inaudible Perth watermark | Low to medium [V](https://github.com/resemble-ai/chatterbox) |
| **Kyutai Pocket TTS** | About 100M params, 2.3–2.5x realtime on a 4-vCPU VM, clones a voice from a WAV sample | Code MIT; licences for weights and voices are listed separately, so check them on HF | Low to medium [V](https://github.com/kyutai-labs/pocket-tts) |

- **Avoid:**
  - F5-TTS and XTTS-v2 weights are non-commercial.
  - Orpheus's licence is reported inconsistently. [S](https://tts.ai/blog/open-source-text-to-speech-guide-2026/)
- **Cloning:** clone only a voice we own the rights to, such as a Kokoro render or the owner's own voice. Pocket TTS bans cloning without consent.

## 4. Audio

- **Loudness and peaks:**
  - **pyloudnorm** (MIT) for BS.1770 LUFS measurement. [S](https://depscope.dev/pkg/pypi/pyloudnorm)
  - **ffmpeg `loudnorm` in two passes** to -14 LUFS integrated and -1 dBTP, plus `alimiter`.
  - `astats` reports peaks and clipped-sample counts.
  - All are free and already in our stack. Effort: low.
- **Harshness fix:**
  - ffmpeg `deesser` on the voice.
  - A gentle shelf above 4 kHz with `equalizer`/`highshelf` on effects.
  - Low-pass synthesized effects at 6–8 kHz.
  - **Matchering** can master a mix to match a reference track, but it is GPL-3. That's fine as a CLI tool that we don't distribute. [S](https://awesome.ecosyste.ms/projects/github.com%2Fsergree%2Fmatchering)
- **Automatic harshness QA**, a numpy gate we write ourselves:
  - Fail if the ratio of 2–5 kHz to total energy goes over a threshold in any 250 ms window.
  - Fail if crest factor is under about 6 dB, or if `astats` counts any clipped samples.
  - Fail if a sound effect peaks more than 6 dB over the voice.
- **SFX libraries:**
  - **Sonniss GDC bundles**: about 7 GB a year, royalty-free, commercial use allowed, no attribution. Reportedly bans AI/ML training, which doesn't affect us. [S](https://rekkerd.org/sonniss-releases-gdc-2026-game-audio-bundle/)
  - **Freesound** with the licence filter set to **CC0 only**. Log each file's ID.
  - **Kenney audio** packs are CC0. [S](https://gtstu.com/?p=5011)
  - **Pixabay** sounds: commercial use OK, no attribution, but the files can't be redistributed on their own, so don't commit them to a public repo.
  - **OpenGameArt** items tagged CC0.

## 5. QA automation

- **Photosensitivity:**
  - **EA IRIS** (BSD-3, C++). Checks luminance flashes, red-saturation flashes, extended failures (2–3 flashes/s over 5 s) and spatial patterns, with JSON output. It doesn't certify compliance. [V](https://github.com/electronicarts/IRIS)
  - **iris-pse-detection**, an MIT Python port on PyPI. [S](https://pypi.org/project/iris-pse-detection/1.1.2/)
  - Run IRIS beside our flash-measure as a second opinion. Effort: low.
  - **Fix the root causes:** z-fighting comes from coplanar faces, so offset decals by at least 1 mm and raise camera clip-start. Flicker comes from per-frame noise seeds and emissive "TV" materials, so cap luminance change per frame in `set.py`.
- **Captions:**
  - Re-run faster-whisper on the **final mix**.
  - Use **jiwer** (Apache-2.0) to compute WER against the script.
  - Check that every caption's on-screen window overlaps its word timing within ±80 ms.
  - Fail if WER is over 5% or any proper noun is missed. Effort: low.
- **Cold-viewer clarity:**
  - Give a fresh agent only ~12 sampled frames plus the ASR transcript, with no script and no brief.
  - Ask it to state who the main character is, where they are, what the threat is, what happened at the end and what's confusing.
  - Compare its answers with the writer's intended answers, and fail on any mismatch.
  - Repeat with captions only, since many viewers watch muted.
  - Costs $0 with the Claude agents we already run. Effort: low.

## 6. YouTube Shorts in 2026 (most credible sources first)

- **Mass-produced content: the biggest risk.**
  - On 2025-07-15, YouTube renamed the "repetitious content" YPP rule to **"inauthentic content"**. It covers mass-produced or repetitive videos "regardless of how the content was made".
  - Press examples name **"narrated stories & slideshows with only superficial differences"**, which describes our format exactly. [S, SEJ](https://searchenginejournal.com/youtube-targets-mass-produced-content-in-monetization-update/550337/), [Social Media Today](https://www.socialmediatoday.com/news/youtube-clarifies-monetization-update-inauthentic-repeated-content/752892/)
  - **Mitigation:** each story needs a genuinely different premise, set, creature and twist, plus visible craft.
  - Avoid one fixed template intro, voice line and music bed on every upload.
  - The owner's review and selection is the human value-add; keep it real.
- **AI labels:** disclosure is required only for **realistic** altered or synthetic content: real people's likeness, altered real events, realistic scenes. AI used for scripts or captions is exempt. Stylized blocky animation with a stock synthetic voice is very likely exempt. [S, NBC](https://www.nbcnews.com/tech/tech-news/youtube-says-will-require-creators-label-ai-content-rcna143937), [9to5Google](https://9to5google.com/2024/03/18/youtube-altered-content-disclosure/)
- **Hooks and loops:**
  - Make the first 1–3 s the creature or the rule ("In this town, never answer the door at 3:07"), not a title card.
  - Judge hooks by **Viewed vs. swiped away** in Studio. Numeric targets vary by source and aren't official. [S, vidIQ](https://vidiq.com/blog/post/youtube-shorts-algorithm/)
  - Write the last line to run into the first.
- **Funnel:** use the Shorts **Related video** link, which YouTube recommends as the bridge to other content [S](https://www.socialmediatoday.com/news/youtube-offers-tips-on-working-with-shorts-videos/). Link each story to a playlist-style compilation or Part 2.
- **Posting times:** I found no credible universal best time. Use Studio's "When your viewers are on YouTube" after about 4 weeks of data.

## Do these first (ranked)

1. **Cycles tune plus Persistent Data, at 720p.** Use OIDN with albedo and normal, adaptive sampling, 2–3 bounces, Simplify and contiguous frame ranges per shard. This is the biggest render win for a few lines of code.
2. **Inauthentic-content guardrail.** Add a variety check in `/week` so no two stories in a week share a premise, set kit, creature type or opening line. Vary the intro and music.
3. **Flash root-cause fixes plus IRIS as a second checker.** Offset coplanar faces, fix the seed, clamp emissive flicker per frame.
4. **Cold-viewer agent plus ASR/WER caption gate.** Both are free with the agents and tools we already run.
5. **Audio gate and CC0/Sonniss library.** Use two-pass loudnorm, a deesser and a high shelf, and fail on 2–5 kHz energy, clipping or a sound effect too far over the voice. Then A/B test Kokoro's native speed against Chatterbox-Nano and Pocket TTS on one story.
