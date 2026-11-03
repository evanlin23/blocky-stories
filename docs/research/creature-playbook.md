# Creature playbook: why our creatures read silly, and how to make them frightening on a phone

2026-11-03. On this day 6 of 10 dropped stories died on the creature. In every case an Opus critic looked at the
creature test still at phone size and said "silly". The owner asked: "why are so many being dropped? ... Can we
model the monsters based on anyhting we can get free or online?" This file has four parts: the causes, the rules
that answer them, and a lab that tested the rules on our rig (arm A) and on free CC0 models (arm B), and proposed agent lines.

RULES.md → The look → The creature already says "too tall", "front lights dead, a key from below or the side, a
rim". The drops show those lines aren't enough: three of the six scripts asked for the opposite ("lit warm by the
desk lamp", "bright, steady lighting", "ordinary height"), and builders tuned faces when the silhouette was wrong.
The playbook makes the rules concrete enough to check on one still, and moves them to the writing stage.

## 1. Diagnosis: the critic's notes, grouped by cause

| Cause | Critic notes it explains | Design choice or rig limit? |
|---|---|---|
| **Familiar silhouette.** The whole outline matches a friendly object or a costume before any detail reads. | ep80 "a solid white snowman or robot in a hat"; ep90 "a friendly toy robot in a sticky-note costume", "a cardboard-box mascot or a pile of shipping boxes"; ep71 "a smiling TV or toaster, a grey box"; ep34 "a crash-test dummy", "a wooden posing mannequin", "a grey block robot or golem"; ep41 "a mauve box" | **Design.** Set-built creatures (`kit.box` in `set.py`) can take any outline. The R6 `rig.Character` can't: its outline is the cast's outline, so a creature made from it reads as one more person or a mascot. |
| **Normal proportions.** Taller only by uniform scale, so nothing in it is wrong. | ep87 "normal-sized friendly clerk", "nothing showed he is eight feet tall", "stubby block sleeves"; ep34 "the arms ended at the hips", "didn't read as taller than the cast" | **Rig limit for `rig.Character`**: `height` scales the whole body evenly, and arms and legs are fixed 1 x 2 x 1 blocks. No spec key stretches a limb, the neck or the torso. A set-built figure has no such limit. |
| **No scale reference.** Height is a number in the script, not something the frame proves. | ep87 "camera level; his head sat far below the ceiling", "empty ceiling above his head, no scale reference"; ep34 "didn't read as taller than the cast at depth"; ep80 "small in a busy bright set" | **Design** (camera and set). |
| **Cute eyes.** Discs with dot pupils are the cartoon "surprised" face. | ep87 "eyes like round glasses with dot pupils", "big disc eyes"; ep80 "face read as a surprised puppy"; ep41 "dot eyes"; ep34 "bold eyes"; ep90 "a pink visor like sunglasses" | **Design**, with one **rig limit**: the face is an unlit texture (`rig.head_material` has no emission), so a drawn glint goes dark with the face. A glint that has to be the brightest thing in a dark frame must be a tiny `kit.emit` piece in `set.py`. `faces.py` already has `pin`, `hollow` with `glow` and `eye_scale`, `none` and `negative`. |
| **Cartoon mouths.** An O reads as a gasp, a row of teeth as a grin. | ep80 "two slits over a tall O mouth read as a cartoon gasp"; ep71 "a grey box with a comb grin"; ep90 "a mouth line plus a bar-graph read-out that made a cute second face" | **Partly a rig limit**: `faces.py` mouths are `auto`, `line`, `none`, `flat` and `crescent`, and an open `auto` mouth is round. There's no jagged or uneven mouth. `none` works; a gape has to be built as geometry (a dark recess) in `set.py`. |
| **Warm or flat frontal light.** Light from the camera's side flattens every block into a toy. | ep80 "warm frontal light", "rim light barely registers"; ep87 "flat light"; ep90 "bright, flat overhead light", "no shadow, red glow or silhouette"; ep34 "the face was lit" | **Design**, and it starts in the script: ep87's script says "lit warm by the desk lamp", ep90's says "bright, steady lighting". `kit.light` places spots and areas anywhere. |
| **Whole body shown at once, small, in a bright busy set.** | ep80 "small in a busy bright set"; ep90 "flat tan-orange fills the frame"; ep87 "the top third was a muddy brown" | **Design** (shot and set). |
| **Friendly materials and colours.** Paper, cardboard, soft white, mid grey and mauve plastic read as packaging or a toy. | ep90 "warm orange, paper-like stickers reads as cardboard and costume"; ep80 "a soft rounded white box"; ep34 "near the batch-1 ban on a pale grey blank-faced creature"; ep41 "mauve" | **Design.** |

The pattern: each critic note was a symptom, and builders fixed symptoms (the face, the hat) one try at a time.
The ep80 critic said it plainly: "tweaks to the face cannot save it, the whole figure is wrong." Every drop had
**two or more** causes at once. A creature reads as frightening only when the silhouette, the light and the
framing are all right before the face is drawn.

What the engine can't do (hard limits) is short: stretch a `rig.Character`'s limbs, light a drawn face's eyes,
draw a jagged mouth. All three are answered by building the creature in `set.py` from `kit` parts, which RULES
already allows ("built from the same blocks as everyone else, but wrong"; "one model, built once in `set.py`").

## 2. The playbook

Each rule names the critic note it answers. A writer applies rules 1 to 4 and 9 in the script's creature section
and its shot list; a builder applies all of them in the creature test still, and checks the still against the
list at 390 px wide before anything else is built.

1. **Name the wrong silhouette in one line, and check it isn't an object.** Write the outline as a shape a
   viewer sees in black: "a person whose arms hang past its knees and whose head is bent sideways under the
   ceiling". Then ask: "at a glance, could this outline be a robot, a mascot, a snowman, an appliance, a box, a
   dummy or a costume?" If yes, change the outline, not the face. (ep80 "snowman or robot in a hat"; ep90
   "cardboard-box mascot"; ep71 "TV or toaster"; ep34 "crash-test dummy", "posing mannequin", "golem")
2. **Stretch one or two parts, never the whole body evenly.** Wrong is relative: legs or arms 1.5 to 2 times the
   cast's length, a neck that's too long, a torso too thin for its height, shoulders too narrow, an extra joint
   in an arm, a head too small for the body. Hands at the end of long sleeves, below the knees. Build it from
   `kit.box` in `set.py` (the R6 rig can only scale evenly). (ep87 "stubby block sleeves", "nothing showed he is
   eight feet tall"; ep34 "the arms ended at the hips")
3. **Prove the scale in the same frame.** Something of known size touches it: the ceiling it stoops under, a
   door frame it has to duck, a person's head at its chest, a car roof at its hip. No empty space above the head:
   the head touches or bends against the top of the set, or the top of the frame crops it. Use a low camera (at
   the narrator's chest or below) looking up. (ep87 "camera level", "empty ceiling above his head, no scale
   reference"; ep34 "didn't read as taller than the cast at depth")
4. **Reveal part of it first, and the whole only in the dark.** The first look is a part: fingers on a door
   frame, a shoulder behind a shelf, eyes in a dark doorway, an outline behind frosted glass or snow. The full
   reveal is still a silhouette more than a lit body: at least half of it in shadow. (ep80 "small in a busy bright
   set"; RULES "show the creature little and late")
5. **Light it from below or behind, never from the camera's side.** A key from below (a floor light, a desk lamp
   under the face, a work light) or from behind (a hard rim on the head and shoulders), cold or wrong-coloured
   (blue-white, sodium, sick green, a dim red). The side of it facing the camera is mostly dark. No warm
   frontal fill on it at all, even when the set around it is warm. (ep80 "warm frontal light", "rim light barely
   registers"; ep87 "flat light"; ep90 "bright, flat overhead light", "no shadow")
6. **Cut a dark space around it, even in a bright set.** The set can stay bright for the polish grade, but the
   creature stands in a dark pocket (a doorway, an unlit back room, the gap between shelves), so its outline reads
   against black or against a bright wall in black. Few other objects in the frame. (ep80 "small in a busy
   bright set"; ep90 "flat tan-orange fills the frame")
7. **Eyes are two small glints or nothing, never discs.** Use `faces.py` `none` or `hollow` (dark sockets), and
   put the glint as two tiny `kit.emit` pieces just in front of the face so it's the brightest thing in the
   frame. No round whites, no dot pupils, no visor or bar that reads as sunglasses. (ep87 "eyes like round glasses
   with dot pupils", "big disc eyes"; ep80 "surprised puppy"; ep41 "dot eyes"; ep90 "visor like sunglasses")
8. **No mouth, or a dark recess. Never an O, a grin or a row of teeth.** `mouth: "none"`, or a gape built as a
   dark, uneven recess below the eyes that stops above the chin. Nothing on the chest that reads as a second face
   or a screen. (ep80 "a tall O mouth read as a cartoon gasp"; ep71 "a comb grin"; ep90 "a bar-graph read-out that
   made a cute second face")
9. **Dark, matte, or wrong materials; no friendly colours.** Avoid soft white, mid grey, mauve, tan, orange,
   paper and cardboard on the body. Use near-black, a deep wet colour, or the set's own material on the wrong
   thing (wallpaper on a body, a blazer too long). Let the light give the colour. (ep90 "warm orange, paper-like
   stickers reads as cardboard"; ep80 "soft rounded white box"; ep34 "pale grey"; ep41 "mauve box")
10. **Pose it toward the viewer and slightly wrong.** Head tilted or bent too far, leaning in, shoulders uneven,
    one arm longer or hanging lower. Never square-on and upright like a mascot. It's never seen moving, only
    closer (RULES), so the pose carries the threat. (ep90 "square-on stance"; ep34 "upright lit face"; RULES
    "leans in face to face")
11. **Judge the still at 390 px with the face covered.** Cover the face with a thumb: if the outline, the light
    and the scale aren't already unsettling, no face will save it (ep80 root cause: "tweaks to the face cannot
    save it, the whole figure is wrong"). Then uncover it and check rules 7 and 8.

12. **Readable first, then wrong** (added after the lab, section 3). A viewer must name what it is (a clerk, a
    person, a shop worker) in half a second, from one lit identity cue: a blazer and collar, an apron, a hat
    brim. Dark is for the pocket around it and the top half of its face, never for the whole figure: a hard rim
    traces the full outline, and the lit cue sits in the light. Every lab still that went fully dark scored 3 or
    4 ("green box robot in dark", "murky shape with glowing eyes"), the same as the bright ones.
13. **Frame medium-low, not close and not far** (lab). Too close hides the height ("the close framing also hides
    the eight feet"), too far makes it small. Show head to knees, the head in the top third against the ceiling
    or door frame, and a normal-height person or a door in the same frame.
14. **An invisible creature has no eyes at all** (lab, the Stander). Glints on empty air make a cartoon face
    ("a grumpy box face"). Show it only by what rests on it, thick on every upward surface, never dashes down
    its sides ("a dotted-line doorway").
15. **A drawn R6 face on the creature reads cute** (lab, Hal try 2: "derpy googly-eyed tilted head guy"). If
    the creature uses `rig.Character`, the face is `eyes: "none"` or `"pin"` at a small `eye_scale`, never
    `round` with rings, and the top half of the face sits in shadow from an under-light.

These borrow general horror craft (silhouette over detail, wrong proportion, under and rim light, negative space,
partial reveal), not any film's, game's or Roblox's creature design, and nothing of Roblox's (hard rule 4).


## 3. A/B results (lab, 2026-11-03)

How it ran: a lab harness (local only, not committed) rendered one standalone creature scene at 540 x 960 through
`blocky.kit` and `blocky.rig`, with no story, voice or grade (so the polish pack's bright grade and bloom weren't
on). Each try was a fresh Sonnet `builder`. Each still was judged by a fresh Opus `critic` at 390 px wide, told
only the script's creature description and the channel's look, not the playbook. Two tries per creature.
Small copies of the stills are in `docs/research/creature-lab/` (our own renders).

### Hal (ep87-motel-rooms)

| Arm | Try | Score | Read | Critic's why |
|---|---|---|---|---|
| A (playbook) | 1 | 3 | silly | "green box robot in dark": a small mint cube head with two dots, no blazer, stoop, desk or ceiling, the bottom 40% black |
| A (playbook + rule 12) | 2 | 3 | silly | "derpy googly-eyed tilted head guy": bullseye eyes and a bright flat face read cute, and the close framing hid the eight feet |
| B (CC0 model) | 1 | 3 | murky | "glowing-eyed hooded penguin thing": nothing says motel clerk. Same world as our cast: **no** |

### The Stander (ep80-snow-globe)

| Arm | Try | Score | Read | Critic's why |
|---|---|---|---|---|
| A | 1 | 3 | silly | "grumpy box face in doorway": snow dashes trace a door frame, and the glint eyes and brows on the hat make a cartoon face |
| A | 2 | 4 | silly | "snow wireframe ghost": evenly spaced dashes draw a tombstone with a hat; no head, the arms don't reach past the knees |

### The Tallyman (ep90-closing-page)

| Arm | Try | Score | Read | Critic's why |
|---|---|---|---|---|
| A | 1 | 4 | faintly frightening | "glitchy robot with red visor": the stickers blur into shards, too dark to read as a clerk |
| A | 2 | 4 | silly | "robot with a siren head": the red glow on the head reads as an alarm light, the long dark legs and barcodes as a shelf unit |

**Nothing passed (7 needed).** Best: arm A 4 (the Stander try 2, the Tallyman tries 1 and 2), arm B 3. The
playbook didn't rescue these creatures in two tries. It did move the critic's words: no try was "snowman",
"mascot", "cardboard box" or "friendly clerk" any more. The failures moved from cute and bright to murky and
abstract, which is what rules 12 to 15 were added for. Those four rules come from the lab and are **untested**.

What the lab showed, beyond the first eleven rules:
- **The two failure modes are symmetric.** Bright, frontal and familiar reads as a toy; dark, abstract and
  unidentifiable reads as "a box robot in the dark". Both scored 3 to 4. The pass zone is narrow: an
  identifiable person-shape with one lit identity cue, a full rim, the face half in shadow, framed head to knees
  against a scale reference.
- **Critics disagree with each other across tries.** Hal's try-1 critic asked for "a warm key light" and "wide,
  unblinking white eyes"; the try-2 critic called exactly that "googly-eyed" and asked for small black pupils
  and an under-light. A single still judged cold gives a noisy score. A creature that passes should pass two
  fresh critics, not one.
- **The concept carries most of the risk.** Creatures defined by a material (stickers, snow) or by being
  invisible failed hardest, because the material has to read at 390 px before the shape can. A creature that is
  a person made wrong (Hal) is the easiest base, but the drawn R6 face pulls it back toward cute (rule 15).
- **Lab limit:** the stills had no grade or bloom, and each builder had one pass of a few minutes. Real story
  builds get the polish grade and three tries, so these scores may be a little low, but not by 3 points.

### Which dropped stories look revivable

- **ep87 (Hal): maybe, the best bet.** A person made wrong is the easiest base. It needs one more design round
  with rules 12 to 15 together (no drawn round eyes, medium-low framing, sleeves past the desk edge, lit
  blazer, night office with a pink rim), judged by two critics. Revive only if that still scores 7.
- **ep71 (two windows): maybe** (not tested here). Creature 5 on its last round and strong elsewhere (big idea 7,
  narrator 9, appeal 9). Its fixes are already concrete ("raise the camera, tilt the head, uneven jaw and teeth,
  eyes that aren't flat dashes"), and rules 8 and 13 answer them. Second best.
- **ep34 (unit seven): unlikely** (not tested). Five creature tries already scored 3 to 4, and its last note asks
  for a new silhouette concept, which is a writer change.
- **ep80 (the Stander): unlikely without a concept change.** Five tries in all (three earlier, two here) never
  passed 4. An outline in snow can't read at phone size. Showing it once in the globe and only by what it leaves
  on the street may be the story, and that's a writer call.
- **ep90 (the Tallyman): unlikely without a concept change.** Four tries never passed 4: a figure made of
  stickers reads as a robot, a shelf or a costume. A writer would need a new creature (not paper, not a material
  costume).

### Arm B: free CC0 creature models

Downloaded into a local, gitignored folder and opened only with Blender's importers. Nothing was committed.

| Model | Author | URL | Licence line | Used? |
|---|---|---|---|---|
| 3D Horror Game Monster (FBX, 6 overlaid poses, ~11k verts, a smooth realistic humanoid) | City Building Game Art / HorrorGameMaker.com | https://opengameart.org/content/3d-horror-game-monster | OpenGameArt: CC0. Pack README: 'Credit "HorrorGameMaker.com", this is not mandatory.' | Yes: one pose, scaled to 2.45 m, a flat matte blazer and grey head, decimated to flat facets, two glints |
| LowPoly Animated Monsters (Bat, Dragon, Skeleton, Slime) | Quaternius | https://opengameart.org/content/lowpoly-animated-monsters | OpenGameArt: CC0. Pack License.txt: "CC0 1.0 Universal (CC0 1.0) Public Domain Dedication" | No: all four are cute, and a skeleton is close to hard rule 2 |
| Ultimate Monsters (50 models) | Quaternius | https://quaternius.com/packs/ultimatemonsters.html | Page: "License CC0" | No: the Google Drive download answered "Quota exceeded" |

Kenney and Poly Pizza returned 403 from this session, and Sketchfab wasn't tried (downloads need a login).

**Do CC0 models help? No, not on this evidence.** The one usable humanoid scored 3, no better than our own
blocks, and the critic said it doesn't belong in our world: "sharp low-poly facets and a pointed, faceless head
clash with our box limbs and rounded-cylinder heads with drawn faces." Restyling fights the model: stretching
its arms tore the mesh, and its anatomy is the wrong kind of detail for an R6 world. The free packs that are
CC0 are mostly cute game monsters (bats, slimes, dragons), which is the "silly" we're trying to escape. The
critic's own first fix was "rebuild him from our blocks, stretched".

**Rule change the owner would need:** hard rule 4 ("Every face, pattern and mesh is made in `blocky/`") and hard
rule 6 ("the characters, their faces and the story stay ours") both forbid a downloaded creature mesh. Allowing
one would mean a line in rule 6 such as "a creature's body mesh may be a CC0 model from `assets/` with its
licence row, restyled in our materials; faces stay ours". **We don't recommend it:** it gave nothing here and
it would weaken rule 5's "every story is new" (the same free monster pack is in many other channels' videos).

## 4. Proposed lines for the agents (not applied; for the orchestrator or owner to add)

For `.claude/agents/writer.md`, in the script's creature section:

> - If the story has a creature, apply `docs/research/creature-playbook.md` section 2 while writing it, not
>   after: name its wrong silhouette in one line and check it isn't a robot, mascot, snowman, appliance, box,
>   dummy or costume (rule 1); say what part is stretched (rule 2), what proves its size in the reveal shot
>   (rule 3, 13), its one lit identity cue (rule 12), and light from below or behind (rule 5). Never write
>   "lit warm from the front", "bright, steady lighting" or "ordinary height" for a creature. Avoid creatures
>   that are only a material (stickers, snow, paper) or invisible: they failed every phone-size test in the lab.

For `.claude/agents/builder.md`, step 1:

> 1. **Creature test still first, before any other build work.** Build only the creature, a scale reference and
>    a bit of set, and render one phone-size still of the reveal. Check it against
>    `docs/research/creature-playbook.md` section 2 at 390 px wide, first with the face covered (rule 11).
>    Build the creature from `kit` parts when its proportions are wrong (the R6 rig only scales evenly), give it
>    no drawn round eyes (rule 15), and frame it head to knees against a ceiling or door (rule 13). A creature
>    passes when two fresh critics score it 7 or more. Three tries at most, then report.
