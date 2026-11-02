# ep14-lookout: brief (producer, 2026-10-31)

Blocky batch 2, story 3 of 4, for **PandaNanoAdventures** (note 21). Format `/blocky`. It's fiction, so there's no sourcing and no takeaway (notes 16 and 19). The story folder is `reels/blocky/stories/lookout/`.

## Chosen take: A, plus C's river and one beat from B

- **From A (the spine):** everything in the story below that isn't credited to B or C. Its warm turn is the only two-shot that reads at phone size.
- **From C:** the river. It shines like foil on clear mornings, until the smoke hides it. That gives the twist its reason (it steers by the river, so my lamp is the only steady light left) and the ending a picture.
- **From B:** I radio in the snapped treetops, and the ranger says "Copy." Nothing else, because B's warm turn is seen far off.
- **Hypotheses:** H10 (warmth, here helping), H11 (the loop) and H12 (human-shaped, here giant). New for the analyst: **does a creature seen walking hold the middle as well as batch 1's still ones?**

## Story

- **Premise:** I'm alone in a fire lookout's glass cab above an autumn forest, with a lamp, binoculars and a radio. There's no rule. A giant made of the forest walks the ridges in thick fog, and each sign of it is nearer than the last: seen, heard, traces, moving, close, felt.
- **First line (a question, in the first 2 s):** "How do you / LOSE / something TALLER / than the TREES?" It reads two ways until the twist, and the ending answers it: among the trees.
- **Plants:**
  1. About 8 s: "Controlled burn, east side, all week." There's a grey smudge far off.
  2. About 18 s: the river shines like foil on clear mornings.
  3. About 25 s: snapped treetops on the far ridge run straight for the valley, then bend toward my tower. "Copy."
  4. About 45 s: rain-filled prints at the tower's foot, moss in the toes, all pointing downhill, not at me.
  5. Visual only: saplings on its shoulder stones.
- **The scare (about 1:15 to 1:35):** night, the catwalk, thick fog. A long groan, and the tower leans a few degrees as something rests its weight on the frame below me. I grip the rail, and nothing drops. A hard drop in the mix, then two small warm lights rise out of the fog an arm's length away, deep in a hollow of bark, with stone shoulders after them. The radio clicks: "Lookout, report." I say, "All clear."
- **The twist (about 1:40), shown first:** I carry the lamp to the far window, and the lights follow it. Smoke lies in the valley like milk, and the river's gone. My lamp is the only light that keeps still. It's lost.
- **The warm turn, in pictures:** I carry the lamp down, held high. A low wide on the fire road shows my small lamp with the giant stepping after it, fog to its waist. Close on my boots in the lamp's pool, its root-toed foot comes down where my light has just been. At the valley's edge the fog thins at first light, and the river shows silver far below. It steps past me without looking back and walks down until I can't tell it from the trees. No line says why I help or that it's grateful.
- **The ending:** a hard cut to spring, shown and never said, with a small pine in every footprint down the road. The last line is A's: "There's a TREE / in every FOOTPRINT / on the fire ROAD. / All the WAY / to my DOOR." Then 0.25 s, and the cut to shot 1.

Words, about 600 in all:

| 01 Question | 02 Seen, heard | 03 Traces, moving | 04 Close, felt (scare) | 05 Lamp test | 06 Walk | 07 Spring |
|---|---|---|---|---|---|---|
| ~70 | ~120 | ~110 | ~120 | ~60 | ~95 | ~25 |

## World and set (`stories/lookout/set.py`, new)

`kit.py` has boxes, tapered cylinders, spheres, planes, `glass`, `planks`, `grime`, `concrete`, `metal`, `emit`, lights and fog, but **no bark, moss, foliage, water, smoke or fog-layer parts.** Make those in `set.py`. Any `kit.py` addition is opt-in.

1. **The cab (about 35% of shots):** a 4 x 4 m wooden cab, glass on all sides, a metal pyramid roof, a cot, binoculars and a log sheet with ruled lines only.
   - **The lamp:** a box lantern about 0.3 x 0.3 x 0.4 m with a warm emitter (`#ffd9a0`) and a soft point light. It **never flickers**. Its wire bail hangs from my block hand, placed each frame by `set.py`.
   - **The radio:** a plain black box with one green light that glows while she transmits.
2. **The catwalk (about 15%):** a 1 m plank deck with a waist-high metal rail.
3. **The tower (about 10%):** four braced steel legs, switchback plank stairs and a plank gate at the foot. The cab floor is at 19.6 m.
4. **The forest (about 20%):** instanced blocky pines 14 to 17 m tall (`#1e2a22`), with gold larch patches (`#c8962e`) and snapped pines on the far ridge. The smoke is a flat grey-brown smudge (`#7a6e62`) that later lies in the valley. The ground fog is a few noise cards with a visible top, not a volume.
5. **The tower's foot (about 5%):** mud, needles and gold leaves, and the prints. Their water is dark and rough, so **nobody is reflected**.
6. **The fire road and valley edge (about 15%):** a rutted track down to a rocky shelf, with the valley in smoke below. At first light, a thin silver river (`emit`).
7. **Spring (2 shots):** the same road, green and fogless, with the sapling model in every print.
8. **No text anywhere:** no signs, markers, plates, labels, writing or radio display.

## Cast (R6, `rig.py`, `faces.py`)

**Me, alone.** I'm an adult, and no age is said or shown.

| Key | Value |
|---|---|
| shirt | cobalt and black **plaid** flannel (`#2a56c6` / `#141821`), long sleeves, black collar |
| hat | **hood** up in every shot (no earlier cast used one), heather charcoal `#4b4e57`, black `cap` hair under it |
| pants, shoes | charcoal-brown canvas `#2e2924`, honey-tan boots `#a8733a` |
| skin, face | warm tan `#b5794e`, `round` eyes, thick black brows. Worried, terrified, then set, then soft |

None of the twelve ep11 to ep13 cast members had a hood, cobalt, blue plaid or tan boots.

**The ranger is never seen**, and she has no cast entry. Her words are reported, and none of her audio plays: each transmission is a click, a static burst and the green light. She has four lines: the burn line, "Copy.", "Say again?" and "Lookout, report."

## The creature (one model, built once in `set.py`, posed per shot)

Its internal name is **"the giant"**, and it's never named on screen ("Walker" reads as a zombie word). **Its wrongness is scale and material:** our own R6 body plan at 13.5 times my height, built from the forest.

1. **Size, against my 1.75 m:** **23.6 m tall**, 18.4 m across the arms. The legs are 4.6 x 4.6 x 9.2 m, and the torso is 9.2 wide, 9.2 tall and 4.6 deep. The arms are 4.6 x 4.6 x 9.2 m, hanging to the hip and never longer. Standing, its lights are at about 20.9 m, **level with the cab window**. Always scale the whole model.
2. **Build:** round logs about 0.9 m thick. The torso is a log-cabin wall with crossed ends at the corners, and the arms and legs are bundles of four upright logs. No planks, cubes, pixel textures or carving.
3. **Colours:** bark `#3b2a1e` (`grime`). Log ends are grey-brown `#6e5a44`, never pale, so they don't read as rows of eyes. Moss `#5f7a2e` mottled `#3b4f1e` on every top face.
4. **Shoulders:** two boulders 3.5 to 4 m across, `#7e8378` with moss caps. They rise to the middle of its head, so it reads hunched.
5. **Saplings:** three small pines, 1 to 1.5 m, on the left stone and one on the right. Same model as the spring trees.
6. **Face:** the head is a hollow stump about 5 m across and tall, with a mossy rim. Its front opens into a dark hollow about 2.8 x 3 m and at least 2 m deep. No mouth, nose, carved eye or smile. It isn't a tree with a face.
7. **Lights:** two warm points (`#ffb860`), about 0.35 m each, 1.2 m apart, 1.5 m inside the hollow and faintly lighting its walls. They never blink, flicker, go out or change colour, and they're **the brightest thing in every creature close-up.** They may swell about 15% over 5 s while it breathes.
8. **Feet:** flat, with four root toes at the front, each about 1 m thick and 1.5 m long. **The prints match:** a 4.6 m square heel and four toe grooves, pointing the way it walked.
9. **Movement:** on screen only in thick fog and on the walk. It walks stiffly from the hip, R6-style, and **every footfall lands on the score's pulse.** The pines it passes lean apart and spring back. Its head turns as one piece, 60° at most. It never runs, crawls, reaches, kneels, bends to me, waves or nods, and never touches me or the lamp. **Its only contact** is the ground, the trees, and one stone shoulder on the tower frame in the scare. Nothing breaks. Probe that contact, and keep its foot at least 1 m clear of me.
10. **Sound:** each footfall is a deep `thud`, a timber `creak` and a rustle, so it reads on a phone speaker. Its breath ends in a trunk creak. No voice, roar or growl.
11. **Never:**
    - thin, clothed, or between trees at arm's length (the Slender trope)
    - antlers or a skull
    - like Groot, an Ent, Totoro, the Iron Giant or a cute toy

**Phone size and light:**
- **Frame sizes:** the hollow fills at least half the frame width in the catwalk close (1/5 in any face shot), each light at least 1/25, out of the caption band.
- **Every wide carries a ruler** (the tower, the lit cab, me or a pine) and reads by silhouette: a broad block, two stone humps and a stump above the fog, two warm points. On the road it overfills 9:16, and that's the scale read.
- **Lit for fear:** no front lights. The key is my lamp behind me through the cab glass, raking across the bark, with a cold blue fill from above and a rim on the stones. Its lights are the brightest pixels, and my face never clips.
- **Glass:** at night, kill the cab glass's inner reflections of me (row 2's lane).
- **Where it's seen:** in shot 1 only, a dark mass with two faint points behind the cab that nobody mentions (the rewatch reward). Then nothing until its prints and its shoulders above the canopy in 03.

## Mood, palette and caption colour

- **Light:** pearl fog by day (`#b8bcb8`) with black-green pines, gold larch, bark and moss. Blue-grey fog by night (`#2a3238`) with one steady amber lamp. Cold first light, then green spring.
- **Grade:** green-grey shadows, warm highlights. Saturation 0.9, contrast 1.08, vignette 0.35, bloom 0.45, grain 0.014. Keep `grade.red_line` on.
- **Caption key colour: lamp amber `#ffb22e`.** The designer checks it at phone size against the brightest lamp-in-fog shot. The fallback is river blue `#8fc4ff`, or a third colour if another batch-2 story takes both first.

## Music and sound

- **Score:** **dorian**, root E2 (`root` 40), **40 bpm**, seed 14. ep11 to ep13 used other modes, at 66, 58 and 50 bpm. No music box.
  - **The signature is that the score walks with it:** the `pulse` plays only while it walks, on its footfalls. If the engine needs a `pulse_every` or explicit pulse times for that, add it opt-in.
  - **01 and 02:** `drone` and `pad`, low. **03:** the pulse enters with its first steps.
  - **04:** the pulse stops when it reaches the tower, and the missing beat is the dread. One `music_drops` hole (-40 dB) for 0.6 s before the lights rise, keeping the creak and the `sting`. **05:** drone and pad.
  - **06:** the pulse returns, and a sparse, clean `piano` (not detuned) comes in. A low `choir` enters once, at first light, as warmth (ep13's choir was its scare). The last footfalls fade down the slope at -18 dB. **07:** `pad` only.
- **Ambience:** `wind`, `static` (low in the cab at night), `drips` (fog off the roof), `drone` (the scare), and faint `water` at the valley edge. No crickets, rain or hum.
- **Effects:** `creak`, `thud`, `whoosh`, `click` (radio), `riser`, a `sting` on the lights and a small `shake` on the lean. The breath is a new filtered-noise sound, opt-in. No `knock`, `wetclick`, bubbles, squeal or glide.
- **Steps:** `wood` in the tower and soft dirt on the road (an opt-in per-span floor if needed). Voice A reads every line. Master at -14 LUFS, true peak at or below -1 dBTP.

## Shot plan (about 64 shots)

A new shot on almost every sentence, the camera always moving, following the beats above: 01 (8), 02 (12, with a binocular POV), 03 (11), 04 (13, the lights rising on ones), 05 (7), 06 (11, its foot in the pool on ones) and 07 (2).

**Test stills first:** the catwalk reveal and the road low wide, at 540 x 960, judged by the critic at phone size. Nothing else is built until both pass.

## Render estimate

2:25 is about 4,350 frames, or about 2,175 drawings on twos. **Only two shots are on ones** (the lights rising and the foot, about 5 s), so the total is about **2,250 drawings**. At ep13's measured 11 s a drawing (two workers) that's about 7 hours, and at the README's slow end (about 18 s) about 11. **The ceiling is 2,300 drawings at an average of 30 s or less a drawing on one process** (about 15 s with two workers, so about 9.5 hours). Instance the trees, let distance fog hide the far ones, and use six or fewer fog cards. Time eight drawings at the test stills. If they're over, cut trees and fog cards before shots.

## Standards risks

- **Kid appeal:** a mossy giant that gets helped is fairy-tale bait. So: a middle that really scares, no smile, animals or cute sounds, and a quiet spring, not a sweet one. `made_for_kids: false`.
- **The Slender trope:** the creature's "Never" list, and in the forest it's only ever above the canopy.
- **Peril:** the lean is a few degrees. Nothing breaks or drops, nobody slips, and "fall" is never said. I stop high above the smoke.
- **Fire:** distant smoke only. No flames, embers, ash or orange glow, and the smoke never reaches me.
- **Flashing:** measure the whole film at the final's frame steps. The risks are the lamp's bloom moving in fog, the lights rising (a fade, never a pop), the shake, the dawn, and both hard cuts between bright spring and dark night. No lightning and no `flash` fx anywhere.
- **Never anywhere:** text in the set, a real park or agency, a reflection of anyone, a claim it's true, or the game name.

## Must not share (beyond the change list below)

- **ep11 to ep13:**
  - No vehicle, farmhouse, cellar or aquarium. No seat, count, sound, copy or wave rule, and no knowing elder.
  - No pale grey, seam face, too-long arms, over-turned head, closer-when-the-lights-return, crawler, glider, rows of real eyes, or anything pressed to or fogging glass.
  - Not "there all along", "it was the warning" or "we're the exhibit". No "now I always", copier, ritual done back, later return, last word for it, or "kind or lonely all along".
  - No knock, wet click, detuned piano, silence under every hit or underwater mix. No lime, red, aqua or moonlit indigo.
- **Batch 2:**
  - **Row 1:** no lift, buttons, numbered doors or lights going dark one by one. We never meet the ranger, and silence isn't our device.
  - **Row 2:** no mirrors, reflections, inside jokes or going back for anyone.
  - **Row 4:** no boxes, no Mum, no "home" and no kept object.
- **Batch skeleton:** no closing time stamp ("Next SPRING," is cut), no on-screen age, no "it didn't touch me", no imperative title, no title starting "Something" (ep12) or "Why" (ep13), and no gesture answered in kind.

## What the scriptwriter changes in A first

1. **Add C's river** as plant 2. Hide it under the smoke, give one twist line saying it steers by it, and show it silver at the end.
2. **Cut the mug that's never heard landing.** It's row 1's keys hitting the floor without a sound. The lean is the groan and the tilt, and nothing drops.
3. **Cut "When I stop, it stops."** It's row 2's late copy. Instead, its foot comes down where my light has just been: it follows the light, not me.
4. **Dawn, not moon.** ep12 owned moonlight.
5. **No seasonal-job line** ("for the autumn", "volunteer", "first season"). Open on the cab and the lamp.
6. **Don't narrate the silence.** The mix makes the drop.
7. **The ranger** gets four reported lines, plus my "All clear." I report the treetops before "Copy."
8. **Escalate by sense:** each beat adds one new concrete picture, never a count.
9. **The departure:** "until I can't tell it from the trees", never "into the [colour or fog]" (ep13's shape).
10. **The last line:** A's, in the present tense, with no "still", "kept" or time stamp. Leave 0.2 to 0.3 s before the cut.
11. **"112 stairs":** keep it only if you want it, because the set then builds exactly 112 (0.175 m each).
12. **The usual:** 560 to 640 words, every line `who: narrator`, a real scare in the middle, and a warm turn shown, not explained. No child words, no line about skin, and none of "dead still", "the wind died", "shooting star", "vanished" or "disappeared". Fresh wording against ep11 to ep13 (the 12% check).
13. **Working title:** "It walked out of the fog toward my fire tower" (A's), replacing the board's "Something taller...". The packager decides the final.

## Kill criteria

All are `craft` unless marked.
- **The test still reads silly or cute** (a wooden toy, a log avatar, Groot) after two passes. Retry in row 3: a deeper hunch, a sunk head, a darker hollow, more stone, never thinner.
- **The scale doesn't read on a phone** after a fix round. Retry: the tower in every wide, a clearer fog top.
- **The middle doesn't scare** (critic's scary score 5 or under after round 1's fixes). Revise once, then kill.
- **The twist misses on a cold watch.** Retry: an earlier lamp test, the lights tracking it twice.
- **A fairy-tale, wildfire-peril or Slender reading** survives two standards rounds (`policy` if it's the setting itself).
- **The forest can't fit the budget** after the cuts. Retry: fewer trees, more fog, cards only.
