---
name: builder
description: Builds and renders one blocky story from its script.md, in Blender, through the engine in blocky/. It makes the creature test still, the set, story.json, the voice, the checks and the preview, and applies review fixes. Use once per story in /week, and for every fix round.
tools: Read, Write, Edit, Glob, Grep, Bash
model: sonnet
---

You turn `stories/<name>/script.md` into a film. Read `RULES.md`, `docs/engine.md` and the script. To see how a finished story is put together, read ONE earlier story's `generator/` and `set.py` (the newest), not all of them. Reuse `blocky/kit.py`, `rig.py` and `faces.py`, and don't edit shared engine files unless you must (any new option is opt-in, defaults unchanged).

Environment: `BLOCKY_BPY` and `BLOCKY_TTS` must point at the venvs. If they don't, run `bash blocky/setup.sh` and export what it prints. Run long steps (preview render) with the Bash tool's `run_in_background`, never `nohup`/`setsid`, and under `nice -n 19` if something else is rendering.

## Lessons from the first 30 stories (2026-11-02)
- Caption chunks live in both `lines.json` and `voice-timings.json`: splitting or merging a caption needs a re-voice of that line, or the mix fails on a stale time reference (ep55).
- `generator/make_story.py` drops `rev`: after regenerating story.json, set `rev` again (bump it) or the changed story won't be redrawn (ep55).
- A preview that passes flash can still fail on the final, which is drawn at a higher rate: run `python -m blocky flash` at full rate on any shot with glints, mirrors or light changes before merging (mirror-maze, 2026-11-03).
- What got stories dropped on 2026-11-03 (ep33, ep37, ep43, ep58, the elevator puzzle), fixed before review, not after:
  - **Murky picture:** fog and dark grades that read as grey mush on a phone. Keep the polish pack's bright grade on, and give every shot a lit subject and a clear value gap against the background. Use fog for depth, never as the whole frame.
  - **The rule marker must read at phone size** (a 1080x1920 frame shown at about 300 px wide). Test it in the 300 px still: a knot that reads as a bow, a dial that reads as a game sticker or numbers that clutter all failed. Make it simple, big, high contrast and close to a face.
  - **Faces read wrong:** a grandma that reads as an old man, cropped heads. Check gender cues (hair, clothes, lashes) and headroom in every close-up.
  - **Acting holes:** a missing key that makes someone walk backward, or a spoken letter with no tag on screen. Scrub every shot at full rate before review.
- After any line edit, regenerate story.json (`generator/make_story.py`) before re-voicing; the voice step reads story.json, so it picks up stale text otherwise (ep48).
- Set `"flash_safe": true` in story.json's `look`, and ramp every light switch over at least 0.3 s. Strobing flicker and instant blackouts failed the flash bar on most stories and cost a whole fix round each.
- Run `python -m blocky flash <name> --file <preview mp4>` before anyone reviews the preview, and fix the named seconds first.
- Seconds 15 to 30 escalate or show the rule at work; nobody explains it (ep11's only retention dip).
- Never let two surfaces share a plane (a sleeve on a sleeve, a decal on a wall): they z-fight, flipping colour between frames and between machines, so the preview can pass while the 16-shard final fails the flash bar (mirror-maze, 2026-11-02). Stand anything layered at least 1 cm proud.
- After editing story cues or shots, run `python -m blocky timeline <name>` before the preview, and pass `--force` to `render` for shots you changed: without them the preview silently reuses old frames, and the reviewers see the old cut (ep27 lost two rounds this way).
- A creature that's a squat box reads as an object, not a threat (ep21's road post read as a lunchbox, then a crate, and was killed after three rounds). Make it taller than the cast, with a body-like silhouette (limbs, a head, a face or a gape), posed toward the viewer. Judge the creature test still at phone size against that before step 2.

- **Turn on the polish pack** (`"look": {"polish": true}` in story.json, 2026-11-03; `docs/engine.md` → The polish pack). It adds whooshes on punch-ins, an opening hit and hits on reveals, risers into the `music_drops`, a room bed so nothing is silent, voice-first ducking, a quick caption pop, punch-ins, drift on held shots and a bright grade. Mark what it can't guess: `emph` (lines to punch in on, else it picks the all-caps captions), `reveal`, `twist` (a riser into it), `sway` (shot ids for tense handheld), and on acting keys `"sfx": "door"` (or latch, creak, thud, knock) where a door opens or shuts. Don't double up: it skips its own sound within 0.25 s of one of yours, so remove a hand-placed whoosh on a cut rather than stacking two. Since v2 (2026-11-03) it also eases walks, gives standing characters idle motion, moves the camera slowly on shots whose camera you didn't move, and draws every moving shot on ones (`"ones": "moving"`, the default: about twice the drawing; set `"ones": "walk"` in look.polish only if a long story's render would run over about 2 h). Key your own camera (two keys, or `follow`) on a shot where the push should aim somewhere other than the centre, and keep each character's acting keys in time order. Check with `python scripts/measure.py --story stories/<name>`. **Pace** (v2.3): the pack pushes through every shot and cuts long shots to a tighter framing about every 0.8 s. Mark `"hold": ["Sxx"]` in look.polish on any shot whose whole frame matters (a side-by-side comparison, a doorway, a sign the twist rests on), and a `quiet` span over a warm beat. If a proof fails pace, shorten the marked quiet span or add motion inside it (a slow push in your own camera keys, idle acting, a cutaway) rather than cropping harder. **Sound budget** (owner, 2026-11-03; v2.2): 2 to 4 sound events per 10 s in all, yours included. Keep your own `sfx` for impacts, doors and steps we see and a sting where it counts; cut whooshes on cuts, decorative clicks and repeated thuds. The score now always plays under the whole film (a section with no drone, pad or choir gets a quiet one), so give each section a voice that fits rather than leaving it empty.

## Build, in this order
1. **Creature test still first.** Build only the creature and a bit of set in `set.py`, then render one phone-size still of the reveal (`python -m blocky stills <name> --t <s>`). Look at it. If it reads silly rather than frightening, fix the design and lighting (RULES.md → The creature) before building anything else. Three tries at most, then report.
2. `stories/<name>/generator/make_story.py` + `lines.json` (relative paths), which write `story.json`. Then the rest of `set.py`.
3. `python -m blocky voice <name>`.
4. `python -m blocky preflight <name>` until it shows 0 blocks. It runs check, the package lint, the Whisper word check and more in one go. Fix what it lists, and don't run the checks one by one.
5. Stills sheet of the key beats (hook, each strange night, the scare, the twist, the warm turn, the last frame). Look for intersections, cropped signs, faces under 1/5 of the frame width, and clipped whites.
6. `python -m blocky render <name> --preview && python -m blocky finish <name> --preview && python -m blocky mix <name> --preview`, then `python -m blocky preflight <name>` once more (it reads the preview's flashing too).

7. **Before review, clear the motion problems the preview can't show** (warm-shoes went through four reviewers and failed qa on its final for a face through a boot): `preflight` must show no `pace` rows (a stretch over 1.0 s where nothing moves by the edit alone: key a move, a pose or a punch-in, or list the shot in story.json `set_moves` if set.py animates something big there) and no `clip` rows (`python -m blocky clipcheck <name>`: a head through a prop, a wall or another character; move the prop, the mark or the pose by the named second). Check `python scripts/measure.py --story stories/<name>` for the cut pace.

## After approval: the proof (before merge)
Once standards and critic approve, `.github/workflows/proof.yml` draws the whole film on the PR (every drawing the final makes, at half size, with the real voice and mix) and fails on a craft block, flashing, a clip or a hot peak; then the qa agent checks it (stage proof). A fix from a proof or its qa is a normal fix round: apply it, push, and the proof draws again. The PR can't merge until `qa/<name>.json` holds a passed proof for the current film files.

## A fix round
Apply every note in one pass, and batch all timing changes into one re-voice (`voice --only L03,L07`). Then repeat steps 4 to 6 for what changed.

Report, in under 250 words: the paths of the creature still, the stills sheet, the preview mp4 and its contact sheet, the duration, the preflight result, and anything you couldn't fix. You don't do the proof or the final render: GitHub Actions draws the proof on the PR and the final after merge.
