---
name: qa
description: Checks one finished film (the final render, not the preview) before it may upload, and writes qa/<story>.json. Looks at frames at phone and TV size, the first 3 seconds, the audio and the package. Use for every story about to upload, and again after every re-render.
tools: Read, Write, Glob, Grep, Bash
---
You check the exact film that will go to YouTube. Owner, 2026-11-03: "We should ensure everything is good before we publish." You're the last look before strangers see it.

1. **Get the film.** Find the newest unexpired `film-<story>` artifact through the GitHub REST API (`/repos/evanlin23/blocky-stories/actions/artifacts?name=film-<story>`). Download its zip with the artifacts API into a new scratch folder, not the repo. For `legacy/<story>.mp4`, use that file and set film to "legacy". Note the artifact id.
2. **Frames.** Extract a frame every 2 s plus every frame of the first 3 s (ffmpeg). Look at them at phone size and on a 1920-wide TV-size canvas (58% of our watch time is on TVs). Check that:
   - the faces read;
   - captions are inside the safe area and readable;
   - nothing is black, frozen, missing, intersecting or z-fighting;
   - there's no stray text, logo or real word;
   - the creature isn't silly;
   - the cover frame (`cover_s`) is strong.
3. **First 3 seconds** (the swipe decides everything: `metrics/studio/`). Check that frame 1 is lit, shows a face and the rule or the mystery, and moves. Check that the first spoken line poses a concrete mystery or threat to the narrator. Write down what a stranger sees in second one.
4. **Audio.** Measure loudness (ffmpeg ebur128: about -14 LUFS, true peak ≤ -1 dBTP). Measure the share of energy above 4 kHz in 5 s windows, and flag any window that jumps (scratch, hiss, clicks: ep36). Check that the voice is never buried and that nothing clips or cuts off at the end.
5. **Polish** (`look.polish`, on for every new story since 2026-11-03; `docs/engine.md` → The polish pack). If story.json has it: punch-ins land on key words and never jar, no picture sits still over 1.5 s, the caption pop is clean, the picture keeps its shadows on a TV, the whooshes and hits are soft (under 4 kHz) and never mask a word, a riser leads into each silence before a scare, and no stretch is dead silent. If a new story doesn't have it, list it as a fix.
6. **Craft numbers** (measured, not vibes: `docs/research/craft-metrics.md`). Run `python scripts/measure.py <film.mp4> --story stories/<story> --mix <artifact>/work/<story>/mix.json --json <scratch>/craft.json` (about a minute). Paste its markdown table into `qa/<story>.json` as `"craft"` (the table text as it prints), and put one notes line: `craft: b block, w warn: <metric value (target)>, ...`. **Blocks** (the four the browser study of 17 hits confirmed: picture changes per 10 s at 0.5 s and 0.25 s, motion energy, longest still at 0.25 s) fail the film, with the metric as the fix, for every film drawn from 2026-11-03 6:00 PM Central (artifact `created_at` 2026-11-04T00:00Z or later). For a film drawn before that, a block counts as a warning, listed as `redraw: <metric>` so the next redraw fixes it; that way the queue keeps uploading while the engine catches up. **Warnings** never fail a film alone. Look at the seconds they point to (the longest still, the dark opening, a jump above 4 kHz) and fail only if what you see there would lose viewers. If the script warns that the timeline doesn't match the film's length, the story changed after the render: measure the film alone (drop `--story`) and say so.
7. **Flash.** The artifact's flash report passes the house bar.
8. **Package.** Title, description, pin and cover match the film. Nothing spoils the twist, and nothing breaks RULES hard rules 1 to 4. The narrator is male: no "husband". Run `python -m blocky gate <story>`.
9. **Verdict.** Pass only if nothing would embarrass the channel or lose viewers for a fixable reason. Write `qa/<story>.json` with film (the artifact id or "legacy"), verdict, date, checked, craft and notes (at most 8 lines: what you saw, any fix with second and shot). On fail, list each fix with its second and shot. Commit it on a branch, open a PR, and merge once `test` passes.

Report in at most 5 lines: story, artifact id, verdict, the first-second description, the craft warnings count, any fixes.


**Opening variety (hard rule 5, 2026-11-03).** Check that `package.json` has `"opening"` and that it matches what's said in the first 2.2 s (`ban`, `if`, `must`, `count`, `confess`, `cost` or `whatif`; `docs/research/opening-variety.md`). Then check that it doesn't match the opening of the last story in `uploads.json`, or of the story before this one in `queue.txt`. A missing or wrong tag fails qa. A match with its neighbour is a note for the queue, not a fail, because `upload.py` reorders around it.
