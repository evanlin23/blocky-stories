# Creature playbook: why our creatures read silly, and how to make them frightening on a phone

2026-11-03. On this day 6 of 10 dropped stories died on the creature. In every case an Opus critic looked at the
creature test still at phone size and said "silly". The owner asked: "why are so many being dropped? ... Can we
model the monsters based on anyhting we can get free or online?" This file has three parts: the causes, the rules
that answer them, and a lab that tested the rules on our rig (arm A) and on free CC0 models (arm B).

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

These borrow general horror craft (silhouette over detail, wrong proportion, under and rim light, negative space,
partial reveal), not any film's, game's or Roblox's creature design, and nothing of Roblox's (hard rule 4).

## 3. A/B results

(Filled in by the lab below.)
