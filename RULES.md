# House rules: creepy blocky stories for PandaNanoAdventures

Every agent reads this file, and only this file, for the rules. The owner's words outrank everything here. Note numbers (9, 18, 21) are the showrunner notes these came from in `evanlin23/content`. When the owner gives new feedback, add it here as a dated quote and change the rule it touches.

## What we make
A crazy, strange, made-up story, 2:15 to 2:30 long (3:00 at most), told in first person by a fast, sped-up synthetic narrator over blocky characters we build in Blender, with big punchy captions. One story a day goes to **PandaNanoAdventures** and no other channel (note 21).
- Owner: "it should be like creepy roblox shorts and the characters should look more like roblox. also the voice should be like the sped up roblox voice... it should not be educational, it should be like crazy stories" (note 18).
- Owner: "the entire thing should be consistent blocky characters" (note 21). The characters, narrator, captions and game-world feel are the brand. They stay the same in every story. **Only the story changes.**
- The owner's reference is "In this town touching the ground is forbidden" (`docs/reference.md`).

## Hard rules (break one and the story doesn't ship)
1. **Fiction, never claimed as true.** No "true story", "this happened", "based on", "real". No real people, crimes, places, routes or street names, and that includes text and signs in the set. Keep the set free of real words: rule markers of our own design (numbers, glyphs, made-up words checked against real places) are fine.
2. **Creepy, not graphic.** Suspense and the uncanny only. No gore, killing, death words, weapons, sexual content or self-harm. No child in the cast (adults, or teens at the youngest), nobody young in peril, and nobody shown hurt.
3. **Not made for kids, every time.** The art draws young viewers, and YouTube removes kid-styled videos with mature themes. `made_for_kids` is false, and nothing in the title, description or pin aims at kids.
4. **Nothing of Roblox's own.** No assets, meshes, textures, catalogue faces, decals, UI, fonts, logo or name. Every face, pattern and mesh is made in `blocky/`. Titles, descriptions and pins never say Roblox or any other game or toy brand, not even to deny it. No character copies a specific avatar or item.
5. **Every story is new.** YouTube's first example of mass-produced content is "narrated stories with only superficial differences", and this channel is blocky-only, so the whole channel gets read for sameness. Each story has its own world, set, cast, creature, twist and ending shape. `check` blocks a shared set file, cast member, premise or twist, or more than 12% shared three-word phrases.
6. **All audio is ours.** The score, ambience and effects are synthesized in `blocky/sound.py`: no samples, no borrowed melody, no music box. The master is -14 LUFS with true peak at or below -1 dBTP.
7. **No flashing over the house bar.** New stories set `look.flash_safe: true` (slow, smooth flicker in `kit.py`), and every light switch in `set.py` ramps over at least 0.3 s. Flickering bulbs and instant blackouts failed the bar on most stories built on 2026-11-01. At most 2 flashes and 5 changes a second (1-frame reading), 3 and 6 (3-frame), 1 red, no extended run. `python -m blocky flash` measures it, and the upload refuses a film that fails.
8. **Write like a person** (note 9). No em or en dashes, semicolons, "not just X but Y", "no X, no Y", three-beat slogans, lists in parentheses, or AI words (delve, journey, fascinating, testament, unveil, "ever wondered"). One emoji at most. Read it out loud.

## The story
- **Shape:** the strange rule or hook in the first two seconds. Three or four strange nights or visits, each adding one concrete picture. The rule broken. A real scare in the middle. A twist planted early. Then a warm turn, shown and not told, and a last line that loops back into the first.
- **What the hits do** (owner, 2026-11-02: "Please update everything based on the stuff we've seen"). Patterns seen on at least 3 different channels across 27 hits on YouTube Shorts and Instagram (9.6M to 36M views; `docs/research/`). They're the default shape now. The critic checks each one:
  1. **The first line states one rule that touches everyone:** "In this world/town, …" plus a concrete rule, under 16 words ("In this town, you get 1,000,000 steps."). It's the genre's signature and viewers recognise it. Our creepy lane: a rule that starts as wonder or everyday life and turns eerie.
  2. **The rule is visible by 2 s,** ideally as a marker of our own design on or above every character: a number, a glyph, a glow, an object (counters, tags, bells, strings). Both format flops we studied hid the rule.
  3. **A 3 to 5 example montage in the first 15 s** shows how the rule shapes daily life, and it can be funny ("Date night is just two people walking sideways").
  4. **The narrator is the exception** to the rule (300 steps left, the one with no number, the bell that never rang).
  5. **A loved one is at stake** (a parent, grandparent, sibling or partner, always adult or teen).
  6. **The climax turns the rule's own logic against itself:** a loophole or a second reading, never new magic.
  7. **The twist is planted early and the last line echoes the first** (as above).
  8. **The first 2 s read clearly on a phone:** lit to read, the rule and a face in frame. Darkness and fog come after the hook.
  9. **Cut often:** a new shot every 1.2 to 2.3 s on average (`check` warns over 2.3 s).
- **The creepy lane** (`docs/research/2026-11-02-creepy-lane-notes.md`: the 10 most-viewed creepy rule Shorts, 5.7M to 16.4M views, against 2 flops):
  - **Wonder first, then the turn.** The rule's opening image is odd or funny, not scary. The first real scare lands about a quarter to two-fifths in (about 35 to 55 s for us), usually the first person taken. Before that, the montage can be played for laughs.
  - **Show the creature little and late:** shadows, sounds and **what it leaves behind** ("Only the cone was left") until about 55 to 70% through, then clearly. It's tall and slow, leans in face to face, and never chases. That's our "never seen moving, only closer", now with a timing. Taken means gone, never shown hurt (hard rule 2).
  - **Light it so it reads when it's shown.** A creature too dark to make out was one flop's problem. The other flop never showed it at all.
  - **Keep the warm turn, but end on a sting.** Most hits resolve warm, then the last line bites: a horror loop back to the first line, or a short in-voice threat. Our loop-back last line does this. Make the final beat land cold.
  - **The music builds:** thin at first, then a heavy low drone enters at the first taking and holds to the end. A short drop before a reveal is still fine. The flops never built.
  - **Avoid the genre's tired template.** Viewers now call out "we moved in, nobody told us the rule, the mayor sends him to the square at midnight". Never use a newcomer-to-town opener, a mayor, or a midnight square summons. Our rule-breaker and our stakes are personal.
- **Our own numbers so far** (ep11, `docs/research/2026-11-02-our-channel-analysis.md`): 82.6% stayed to watch and the average view was 84% of 2:18. The hook and the length work. Reach is held back by shares (3) and comments (7), so the pin question and loophole-worthy rules matter. The one dip, 0:18 to 0:26, was a character explaining the rule. **Seconds 15 to 30 escalate or show the rule at work; nobody explains it.**
- **What we keep from the owner's own calls** (the research doesn't override them): the same R6 body type, the 2:15 to 2:30 length (owner, 2026-11-01: "keep a similar length target"; YouTube's narrated hits run 54 to 162 s, so we're on the long side and `metrics` will tell), our one narrator voice and our two-or-three-word captions with a key colour (YouTube's hits mostly use phrase blocks with a coloured key word too). And no child narrators: the hits often use one, but a teen or an adult looking back is our line, because kid-styled videos with mature themes get removed.
- **Telling:** about 290 wpm while speaking, one short sentence per beat, a new shot on almost every beat. Every line is `who: narrator`, and characters are quoted inside the narration ("He looked at me and said, "Six.""). Nobody gets a voice of their own (owner, 2026-10-30).
- **The middle must actually scare** (owner: "I low-key don't think the story is like creepy enough"). Escalate, don't describe: something a row closer each time the lights come back, a voice copied, a head turned too far.
- **Deep lore and a real twist** (owner, 2026-11-01: "something I think is interesting is having deep story and lore, or like a twist. I think that sort of stuff is doing quite well on instagram and youtube should be right behind").
  - **The twist turns the whole story over.** The last 15 seconds make the first line mean something new, so a second watch plays differently. Plant it at least twice where a rewatch catches it. A twist that only adds a fact isn't one.
  - **The stories share one hidden world.** `stories/lore.md` is the canon: what's under the town, who keeps the rules, what the creatures are to each other. Each story is still complete on its own, with its own setting, creature and ending. It plants **one** small connection to the canon (a symbol, a name, a sound, an object in the background) that only a repeat viewer spots. It's never needed to follow the story, and it's never a "Part 2" or a cliffhanger.
  - **The pin can invite theories** ("what was on the back of the ticket?"). The answer is in the canon, never in the comments.
  - The lore never makes two stories alike: rule 5 still holds for setting, creature, twist and ending shape.
- **Vary the warmth** (owner, 2026-10-31: "We can have other heartwarming endings"): friendship, loyalty, helping, home. Never again "the monster was kind/lonely all along" or the ritual done back.
- **Never reuse what batch 1 shared:** a knowing elder who explains in cryptic quotes. A night-shift or one-summer narrator. A pale grey blank-faced creature. "Pressed FLAT" against glass. A closing-section opener like "Last NIGHT,". An on-screen age. "It didn't touch me". "Not X, it was Y" cadences.
- **Within a batch** no two stories share a setting, creature type, rule type (what the world's rule is about) or kind of warmth (ending shapes may repeat, owner 2026-11-02). `stories/ideas.md` lists what's been used.
- **Read every line against the picture under it.** Watch for self-contradictions ("TALL... WIDER than it's TALL"), a count that doesn't match the knocks we hear, and a line about skin landing on a character it doesn't fit.
- **Titles** are a question or a statement, never an imperative rule ("When the floor knocks, knock back" was wrong). They don't spoil the reveal or reuse an earlier title's shape.
- **Volume** (owner, 2026-11-02: "we should just be trying to pump out as many as possible right now and then I'll just rate limit and upload once per day manually"): make as many stories as we can in parallel sessions. Similar ending shapes across a batch are fine (owner, same day: "We don't need to limit how many are like that"), but the hard rules and the originality check still apply. The owner paces the uploads, one a day.

## The look
- **Characters** (`blocky/rig.py`, `faces.py`): R6 blocky bodies, a soft rounded-cylinder head, flat drawn faces with thick black strokes, block hair, hats, patterned shirts. A face at phone size is at least 1/5 of the frame width, out of the caption band.
  - **The body type stays** (owner, 2026-11-01: "I kinda want them to be the same body type"). Research found that Roblox's terms restrict off-platform commercial use of "derivatives of the classic Roblox avatars" (R6/R15), and our proportions match R6 (`docs/research/2026-11-01-web-research.md`). The owner accepted that risk. Keep it small everywhere else: every face, hair piece, outfit and pattern is our own, never a catalogue item or the default face, and there's never the name, logo or UI anywhere.
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
{"title": "...", "description": "...", "pin": "...", "made_for_kids": false, "cover_s": 107.0}
```
- **Title:** under 100 characters, by the rules above.
- **Description:** two or three short paragraphs. It sets up the story without spoiling it, says "It's made up.", and can say it's "built with code and Blender". The upload adds the measured flashing line on top by itself. Never: game or toy names, true, real, based on, kid, teen, child, baby, school, AI voice, no AI, made by hand, Kokoro, another franchise's monster.
- **Title:** state the world's rule, the way the hits do ("In this town, everyone has a price"). It's a statement, never an imperative, and it never spoils the twist.
- **Pin:** a question the viewer answers about themselves under the rule ("How many lies would your number show?"), or one about a detail planted early ("would you have sat back there?"). The owner posts it as their own first comment and pins it: on YouTube, the creator's own question sits in the top comments of 8 of the 15 Shorts studied.
- **Cover (`cover_s`):** the second of the frame that becomes the thumbnail. Pick the creature or the rule marker clearly lit, with a face if possible and the caption tying back to the title (ep20: 1:47, "stood in the MIDDLE."). Without it, the render picks 78% of the way in. The upload issue shows the cover, and the owner picks that moment in the YouTube app.
- No hashtags or tags for now. Altered or synthetic content: No (it's animated fiction).

## Budget and craft
- $0: free tools only. Renders run on GitHub Actions (free for this public repo), and uploads use the free YouTube Data API.
- The preview is quarter-res with every 4th drawing, so always say which one you're showing. The final is 540x960, sharpened to 1080x1920.
- Shared engine files (`post.py`, `sound.py`, `faces.py`, `timeline.py`, `checks.py`): a story's new option is opt-in, with defaults unchanged, so no other story's film changes.
- Never `pkill -f` (it matched our own shell twice). Kill by PID.
