# House rules: creepy blocky stories for PandaNanoAdventures

Every agent reads this file, and only this file, for the rules. The owner's words outrank everything here. Note numbers (9, 18, 21) are the showrunner notes these came from in `evanlin23/content`. When the owner gives new feedback, add it here as a dated quote and change the rule it touches.

## What we make
A crazy, strange, made-up story, 2:15 to 2:30 long (3:00 at most), told in first person by a fast, sped-up synthetic narrator over blocky characters we build in Blender, with big punchy captions. One story a day goes to **PandaNanoAdventures** and no other channel (note 21).
- Owner: "it should be like creepy roblox shorts and the characters should look more like roblox. also the voice should be like the sped up roblox voice... it should not be educational, it should be like crazy stories" (note 18).
- Owner: "the entire thing should be consistent blocky characters" (note 21). The characters, narrator, captions and game-world feel are the brand. They stay the same in every story. **Only the story changes.**
- The owner's reference is "In this town touching the ground is forbidden" (`docs/reference.md`).

## Hard rules (break one and the story doesn't ship)
1. **Fiction, never claimed as true.** No "true story", "this happened", "based on", "real". No real people, crimes, places, routes or street names, and that includes text and signs in the set. Keep the set free of text, or use made-up words checked against real places.
2. **Creepy, not graphic.** Suspense and the uncanny only. No gore, killing, death words, weapons, sexual content or self-harm. No child in the cast (adults, or teens at the youngest), nobody young in peril, and nobody shown hurt.
3. **Not made for kids, every time.** The art draws young viewers, and YouTube removes kid-styled videos with mature themes. `made_for_kids` is false, and nothing in the title, description or pin aims at kids.
4. **Nothing of Roblox's own.** No assets, meshes, textures, catalogue faces, decals, UI, fonts, logo or name. Every face, pattern and mesh is made in `blocky/`. Titles, descriptions and pins never say Roblox or any other game or toy brand, not even to deny it. No character copies a specific avatar or item.
5. **Every story is new.** YouTube's first example of mass-produced content is "narrated stories with only superficial differences", and this channel is blocky-only, so the whole channel gets read for sameness. Each story has its own world, set, cast, creature, twist and ending shape. `check` blocks a shared set file, cast member, premise or twist, or more than 12% shared three-word phrases.
6. **All audio is ours.** The score, ambience and effects are synthesized in `blocky/sound.py`: no samples, no borrowed melody, no music box. The master is -14 LUFS with true peak at or below -1 dBTP.
7. **No flashing over the house bar.** At most 2 flashes and 5 changes a second (1-frame reading), 3 and 6 (3-frame), 1 red, no extended run. `python -m blocky flash` measures it, and the upload refuses a film that fails.
8. **Write like a person** (note 9). No em or en dashes, semicolons, "not just X but Y", "no X, no Y", three-beat slogans, lists in parentheses, or AI words (delve, journey, fascinating, testament, unveil, "ever wondered"). One emoji at most. Read it out loud.

## The story
- **Shape:** the strange rule or hook in the first two seconds. Three or four strange nights or visits, each adding one concrete picture. The rule broken. A real scare in the middle. A twist planted early. Then a warm turn, shown and not told, and a last line that loops back into the first.
- **Telling:** about 290 wpm while speaking, one short sentence per beat, a new shot on almost every beat. Every line is `who: narrator`, and characters are quoted inside the narration ("He looked at me and said, "Six.""). Nobody gets a voice of their own (owner, 2026-10-30).
- **The middle must actually scare** (owner: "I low-key don't think the story is like creepy enough"). Escalate, don't describe: something a row closer each time the lights come back, a voice copied, a head turned too far.
- **Deep lore and a real twist** (owner, 2026-11-01: "something I think is interesting is having deep story and lore, or like a twist. I think that sort of stuff is doing quite well on instagram and youtube should be right behind").
  - **The twist turns the whole story over.** The last 15 seconds make the first line mean something new, so a second watch plays differently. Plant it at least twice where a rewatch catches it. A twist that only adds a fact isn't one.
  - **The stories share one hidden world.** `stories/lore.md` is the canon: what's under the town, who keeps the rules, what the creatures are to each other. Each story is still complete on its own, with its own setting, creature and ending. It plants **one** small connection to the canon (a symbol, a name, a sound, an object in the background) that only a repeat viewer spots. It's never needed to follow the story, and it's never a "Part 2" or a cliffhanger.
  - **The pin can invite theories** ("what was on the back of the ticket?"). The answer is in the canon, never in the comments.
  - The lore never makes two stories alike: rule 5 still holds for setting, creature, twist and ending shape.
- **Vary the warmth** (owner, 2026-10-31: "We can have other heartwarming endings"): friendship, loyalty, helping, home. Never again "the monster was kind/lonely all along" or the ritual done back.
- **Never reuse what batch 1 shared:** the "At the PLACE, rule" first line (start mid-scare, on a sound, a question or dialogue instead). A knowing elder who explains in cryptic quotes. A night-shift or one-summer narrator. A pale grey blank-faced creature. "Pressed FLAT" against glass. A closing-section opener like "Last NIGHT,". An on-screen age. "It didn't touch me". "Not X, it was Y" cadences.
- **Within a batch** no two stories share a setting, creature type, first-line type, ending shape or kind of warmth. `stories/ideas.md` lists what's been used.
- **Read every line against the picture under it.** Watch for self-contradictions ("TALL... WIDER than it's TALL"), a count that doesn't match the knocks we hear, and a line about skin landing on a character it doesn't fit.
- **Titles** are a question or a statement, never an imperative rule ("When the floor knocks, knock back" was wrong). They don't spoil the reveal or reuse an earlier title's shape.

## The look
- **Characters** (`blocky/rig.py`, `faces.py`): R6 blocky bodies, a soft rounded-cylinder head, flat drawn faces with thick black strokes, block hair, hats, patterned shirts. A face at phone size is at least 1/5 of the frame width, out of the caption band.
- **Sets:** realistic materials around the plastic avatars (brick, wood, cobbles, concrete), practical lights that flicker, long shadows, game-engine fog. Each story's `set.py` is new.
- **The creature** is the thing that makes or breaks a story:
  - It's built from the same blocks as everyone else, but wrong: too tall, too wide or too flat, limbs too long, a face blank, upside down or opening onto darkness. It's never seen moving, only closer. Thin rods and tentacles read as props (owner: "the tentacle just looks silly").
  - It's one model, built once in `set.py` and posed per shot, so it's the same in every shot.
  - **Test still first.** Render one finished, phone-size still of the reveal before building anything else, and iterate until it's frightening, not silly.
  - **Light it for fear:** front lights dead, a key from below or the side, a rim on the silhouette, no clipped white. The eye highlights are the brightest thing.
- **Captions:** Schibsted Grotesk Black at 84 px, white with key words in CAPS and the story's own colour, two or three words, each one appearing on its own first word (sync beats hold time).
- **Voice:** Kokoro `am_adam`, tempo 1.03, sped up 1.45 times (the owner's pick, "Voice A sounds the best"). It's matched by ear, never cloned from anyone.
- **Sound:** drop everything but the voice and the hit for 0.5 to 0.8 s before a scare (`music_drops`). A closing sound needs -18 dB or a pitch fall to be heard. Leave 0.2 to 0.3 s between the last word and the loop cut.

## The rig's limits (plan shots around them)
- R6 hands can't grip: cut away instead of showing a hand on a wheel or a knock.
- No cross-legged sitting and no reach to the floor from a chair.
- Seated riders are about 1.36 m wide, so space seats for that.
- Long arms foreshortened toward camera read as beams: show the hand at the end of the sleeve.
- Check every creature beat and every pose near the set for intersections in the stills before the final.

## Packaging (`stories/<story>/package.json`)
```json
{"title": "...", "description": "...", "pin": "...", "made_for_kids": false}
```
- **Title:** under 100 characters, by the rules above.
- **Description:** two or three short paragraphs. It sets up the story without spoiling it, says "It's made up.", and can say it's "built with code and Blender". The upload adds the measured flashing line on top by itself. Never: game or toy names, true, real, based on, kid, teen, child, baby, school, AI voice, no AI, made by hand, Kokoro, another franchise's monster.
- **Pin:** a question about a detail planted early ("would you have sat back there?").
- No hashtags or tags for now. Altered or synthetic content: No (it's animated fiction).

## Budget and craft
- $0: free tools only. Renders run on GitHub Actions (free for this public repo), and uploads use the free YouTube Data API.
- The preview is quarter-res with every 4th drawing, so always say which one you're showing. The final is 540x960, sharpened to 1080x1920.
- Shared engine files (`post.py`, `sound.py`, `faces.py`, `timeline.py`, `checks.py`): a story's new option is opt-in, with defaults unchanged, so no other story's film changes.
- Never `pkill -f` (it matched our own shell twice). Kill by PID.
