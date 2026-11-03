# ep17-moving-day: designer notes (motion-designer)

## Creature test still

**The still:** `review/creature-test.png` (the finished 1080 x 1920 frame, drawn at 540 x 960) and `review/creature-test-phone.png` (the same at 360 x 640, to judge at phone size). This is pass 6. The critic read pass 4 at 3/10 and pass 5 at 5/10 (`review/creature-test-critique.md`). Earlier passes: `creature-test-v1.png` to `-v5.png`. It's the L48 frame, "It was BENT / over her BED, ...", with the caption on "over her BED," in the brief's lilac-violet `#b98aff`. That line is voiced for real (Kokoro, voice A) in the provisional `story.json`.

Rebuild it with `python -m reels.blocky timeline moving-day` then `python -m reels.blocky stills moving-day --t 0.84`. Set `MOVING_DAY_PROBE=1` to print the contact probe into the Blender log.

**Code:** the story's code is in `reels/blocky/stories/moving-day/`. One shared engine change, opt-in: `faces.py` gains an `asleep` expression (flat lids drooping at the outer ends). It's a new name, so every existing face draws exactly as before, and `test_blocky.py` has a test for it.
- `set.py` builds Mom's room and the Boxes.
- `marker.py` draws the faces (PIL only, so it runs outside Blender: `python marker.py <dir>` writes a sheet of every face).
- `story.json` is provisional and says so in its first key. It's one line (L48) plus a silent 30 s beat, so the shared per-story tests (30 to 180 s, zero blocks) stay green. `check` gives one warning, the pace of a one-line placeholder. `pytest reels/blocky` passes (39 tests).

### Pass 6: the critic's two must-fixes (everything else locked)

1. **The mouth is a solid black hole.**
   - `marker.face("wide")` lays a solid fill under the scribble (`Pen.solid`).
   - The marker's uneven-lay grain now applies only where the ink is thin, so solid ink is solid. In pass 5, the grain let about 5% of the board through the fill, which was the grey goatee.
   - The shape is inverted: widest across its top third, about half the box, just under the eyes, narrowing a little as it runs off the bottom edge.
   - There's no spike between the eyes. The 7° tilt and the ragged edge stay, and the eyes are unchanged.
   - The ink colour goes to `#060507`.
   - At 120 px it reads as a hole, not an emotion.
   - On the finished frame the mouth's interior is median 0.8% and p90 3.1% lightness (target: p90 under 5%).
2. **The hands read as open box ends.**
   - A new pose key, `wrist_roll`, turns each hand about its forearm: 42° for the near hand and -45° for the far one (the far hand showed more planes rolled the other way).
   - The two flaps that face the door are splayed less (34–38°), so they meet the camera broadside. The two behind still lie flat on the quilt (68–72°).
   - Each hand is now a few dark trapezoids at the quilt's edge, not wire.

**Probe** (`MOVING_DAY_PROBE=1`):
- 0 contacts.
- 0.66 m of air under the face box.
- Hands 0.147 m and 0.693 m from Mom. The probe measures to her nearest part, her hair, where pass 5's figure was to her head; it's 0.19 m to her head.
- Nothing clips (max 221 of 255 outside the caption).

**Render time:** 27 s a drawing through `stills` (2 threads, 16 samples).

**The critic's (b) list, for the build** (noted, not done now):
- Mom's near arm a stop darker than her face in the wides, and the L54 close framing it as an arm ending in a hand.
- The cold rake carried further across the quilt drape, or the black framed out per shot.
- The L48 wide keeping the ceiling line and the neck chain pressed along it in frame, so it reads "too tall for the room". L49 is its own close, with the face at 0.45 of the width or more.
- Mom's linked fill on the pillows down about 20%, so her face and the creature's eyes rank above the pillow.
- The joint-tape glints' regular spacing broken up, or some of them dark. No extra rim light.
- Mom's sideways sleeping face stays as it is.

### Pass 5: the critic's fixes and the producer's rulings

The critic scored pass 4 at 3/10. The orchestrator's phone read agreed:
- The upside-down `wide` face read as round glasses and a buck tooth under a black hairline.
- Mom read as a tan parcel.
- A black body with two lit forearms read as a cardboard costume.
- The bottom 40% was dead.

What changed, by the critic's numbering:

1. **The face, redrawn and upright from the door.**
   - **`flip`:** `set_face` takes a per-pose `flip`, which turns the drawing 180° on the box. The cached files are keyed `boxes-wide-flip-*`. The box still hangs upside down, so its crushed corner and seam sit at the bottom, a detail you notice on a second look.
   - **`wide` is redrawn:**
     - Two eyes, each gone round once, taller than wide (1.35), unequal: the right one about 25% bigger and set higher.
     - Small solid pupils (0.028) slid toward the rim, down and to the left: toward Mom as the door sees it. `marker.face()` takes a `gaze`.
     - A tall gape about 0.42 wide by 0.70 tall. Its narrow top pushes up between the eyes, and its bottom runs off the box's edge.
     - The gape tilts 7°, sits a little off centre, and has a ragged edge (0.10 radius noise, a shaky outline).
   - **No tape on the drawing:** the face box's flap-seam tape now runs on the x axis, over the top and down the two sides, so the "tooth" and the white "parting" are gone.
   - **The ink has no sheen.** Its specular drops to 0.02, so it stays black even at a grazing angle. The face box is smooth-shaded, so its mesh facets don't show under the tight light.
   - Checked at 120 px: it reads as a gaping, wrong face looking down at her, not as a character.
2. **Mom reads as a person** (producer's ruling 1):
   - Skin is `#a86a58`: hue 14° against the boards' 29–30°.
   - The `asleep` lids replace `shut`'s up-arcs, which read as smiling.
   - The pillow is pale (`#d6d3c9`), and a second pillow is propped against the headboard behind her crown.
   - Her hair is fanned on both pillows. It's built once she's posed (`dress_mum`), around her crown and behind her head, never on the face side.
   - Her head sinks into the pillow (neck lift 0.12 down to 0.04 m), so the pillow shows round it.
   - Her own fill, motivated by the window from above the bed's head, is light-linked to her face, near hand, pillows and hair only.
   - Measured on the finished frame: her face is 35% lightness and the cardboard in shadow is 1% (ruling: 25%+ against under 15%).
   - Her face sits above the caption band.
3. **Kill the costume read** (with the producer's ruling 2: hands and the quilt's edge in shadow before the lamp):
   - The window now lights none of the creature, forearms included, and the creature casts no shadow in it (shadow linking, `no_shadow`).
   - Two lights reach the creature only:
     - A rim from behind and above (the window's light off the far wall).
     - A shadowless glow from the nightlight's place. Its own legs would otherwise shadow every underside the door sees.
   - Together they give the undersides and edges a cold line, and the tape inside the joints sits nearer the gap's mouth to catch them.
   - The flap tips are a third shorter (0.13 to 0.087 m) and splayed flat (60–78°, curl 6°). The wrists are lowered so the open box ends rest on the quilt's edge at her shoulder and on the mattress edge.
4. **Re-light:**
   - The face kick is a 19° spot from the nightlight's place, aimed at the eye line (`eye_line()`). I went to 19° rather than 14° because at 14° the gape's shape was lost in the dark.
   - The nightlight's own wall glow is down to 1.2 W and sits behind the near leg. The face's peak (64% lightness) now beats the pool's (59%), and nothing clips (max 220 of 255 outside the caption).
   - The ceiling over the bed gets a faint window wash that the creature neither receives nor shadows, so the neck chain stands out dark against it. The soft black ceiling smudge is gone.
5. **The lower third:**
   - The camera is up from 1.0 to 1.45 m and tilted down 12°, still 18 mm. I'm judging this as L48 only; L49 should be its own close.
   - A low cold rake of window light picks out the quilt's drape toward the foot, cold and low in colour (quilt top 14% saturation). The bottom 25% is up from 1% to 4% lightness. It's still the darkest part of the frame and mostly sits under YouTube's controls.

**Probe on pass 5:**
- 0 contacts.
- The face box is 0.66 m above Mom's highest point (her hair).
- Hands are 0.19 m and 0.70 m from her.
- The top of the creature is 2.349 m under a 2.35 m ceiling.

**Render time:** 26.8 s a drawing through `stills` (2 threads, 16 samples), up from 23 s with the extra linked lights. Look-dev on 4 threads ran about 15 s.

**Still open after pass 5:**
- **Mom's near arm** is an R6 slab 0.34 m thick and the biggest single shape mid-frame, mostly under the caption. Her L54 close should show it as an arm with a hand.
- **Her face reads sideways,** turned 90°: a lying head seen side-on puts the drawing's top toward the wall. The pale pillow and the hair now frame it as a head.
- **The creature's body** is mostly a dark mass with faint cold edges. The box joints' tape glints are barely visible at phone size. Making them read would mean more rim light, which starts lighting whole faces and brings back the costume read.
- **The pool's broad glow** between the legs sits close to the face's brightness (95th percentile 42% against 38%), though the face holds the peak.
- **My skin** (cast key `me`, not in this still): ruled off the cardboard ramp too. Candidates: `#e8c3a4` (light, 78% lightness against the boards' 41–53%) or `#6e3f33` (deep, hue 12°). The generator picks one.

*The sections below describe the model as built and pass 4 (its `wide` face, its light levels and its tape rules). Where they differ from pass 5 above, pass 5 wins.*

### The design (to the brief's continuity list)

- **One model, 15 boxes, built once** by `build_boxes()`: the face box, a neck chain of three (N1 to N3), a torso of three (pelvis, belly, wide chest), two boxes to each leg and two to each arm.
  - It stands 2.85 m without the neck.
  - Hanging, its hands reach its knees (fingertips 1.69 m below the shoulder).
  - `pose_boxes()` only turns joints:
    - `press` folds the legs until the torso clears the ceiling.
    - The neck chain is laid in world space: N1 climbs, the rest lie flat under the ceiling toward a point, and the face box hangs from the end.
    - Each arm reaches for a point (two-bone IK).
  - A pose can show fewer neck boxes (`"neck": 0..3`), so mornings 1 to 3 (12, 13, 14 boxes) are poses of the same model.
- **The boxes:**
  - Each box is subdivided and deformed, with bulging sides, a sagging top, crushed corners, dents and a faint crumple, so the faces catch light like board rather than plastic.
  - The material is mottled board with a fibre tooth and handholds cut in the torso's sides.
  - Each box has its own packing tape along its flap seam. On the face box that's a strip over the top and down the front, which crosses the forehead between the eyes.
- **Joints are bare:** a 3.5 cm dark gap at every joint, with four short tape strips set back inside it. The outer tape rings and seam strips from my first passes are gone (brief, item 4).
- **Hands:** the forearm box's open end, four flaps split at a fold. They're 72% of the side's width, so there are gaps between them like fingers, splayed and curled.
- **The face box** is always tone `#a87b50` with one crushed top corner (its dent). At 3 a.m. it hangs face down from the end of the chain, so the drawing is upside down from the door.
- **Mom:**
  - Solid slate-blue top `#6c7c97`, dark trousers, long dark-brown-going-grey hair, skin `#c08a66`.
  - She lies on her back with her head toward the wall, turned to the door, eyes shut.
  - The quilt is loose at her shoulders, and her near arm lies out on top of it.
  - Her body under the quilt is left out of the render. The R6 torso is 0.68 m wide, which would make a mound as tall as the camera.
- **Her room:**
  - Off-white green-grey walls, honey boards, a low divan and one pillow.
  - The wooden chest of drawers just inside the door has the lamp on it, unlit.
  - The window on the right wall is curtained, dim grey and has no moon. A bare bulb near the door is never lit.
  - There are no other boxes and no marker anywhere but the face box.

### The faces (`marker.FACES`)

`frown`, `stare`, `sideways` (pupils slid hard to one side, no mouth; added for morning 3), `many_eyes` (17 eyes on the front, and five more spilling onto each side face), `wide`, `smile` and `none`.
- **One marker:** a 1.8 cm chisel nib on the face box (`LINE`), the same width in every drawing.
- **The hand:**
  - Strokes wobble a little.
  - Ink pools where a stroke starts and stops, and goes darker where strokes cross.
  - It bleeds slightly into the fibres and lays unevenly.
  - Fills are scribbled, so specks of board show near their edges.
- **`wide`** is two huge round eyes, each gone round twice: the second loop is offset so the lines cross and the weight stays one marker. The pupils are pins. Below them, a black open mouth fills the bottom of the box. There are no brows (brows read as "surprised").
- **`smile`** uses shut-arc eyes, never dot eyes, so it can't be the game's default face.
- The ink is matte (roughness 0.8). For `stare`, `set_face` drops it to 0.12, the brief's one wet face.
- Drawings are cached under file names keyed on marker.py's contents, so an edited drawing is never read back from a stale file.

### The light (the brief's 3 a.m.)

- **Key:** Mom's plug-in nightlight, cold `#d6e4ff`, a point light 7 cm off the far wall at skirting height, between and behind the Boxes' legs.
  - It throws a pool of light on the far wall that frames the legs.
  - It rims the boxes from below and behind.
  - It casts the neck chain's shadow forward over the ceiling.
  - There's no front light.
- **The face** needs help: with the key behind the figure, a face aimed at the door would be black. Two fixes, both stated here so nobody's surprised:
  - **The face points mostly down,** toward the nightlight (about 25° off straight down, toward the door). With a 1.0 m camera we look up into it.
  - **A matching spot from the nightlight's own place lights only the face box,** through light linking, and it casts no shadow. Without that, the creature's own torso blocks it. It's a cheat in the physics but not in the motivation: the light comes from the nightlight's position and colour.
- **The window** is a dim grey side light. Light linking keeps it off the creature's body, so the body stays a silhouette, while it reaches Mom, the room, the face box and the flap hands. A faint grazing light from the same side edges the boxes so they read as boxes.
- **The lamp** is built and cued (`lamp` cue, 0..1) for L51, and it's off here.
- **Fog, grade and haze:**
  - Fog density is 0.02.
  - There's no volume (the brief rules out volumetrics).
  - The grade is the brief's: saturation 0.85, contrast 1.1, vignette 0.42, bloom 0.22, grain 0.014, exposure +1.0.
- **Clipping:** none outside the caption (frame max 234 of 255). Mom's face averages about 42 of 255 with a peak of 113: dim and readable, never near clipping. The marker reads black on mid-brown.

### Phone size and the probe

- **Phone size:** the face box spans about 0.29 of the frame width, at 0.20 to 0.33 of the height, clear of the caption band. Mom's face sits at the left just above it. The violet key reads cleanly at phone size on this dark frame, so I kept it over the dusty-rose fallback.
- **Contact probe** (`set.probe`, BVH overlaps with everything in the room):
  - 0 contacts.
  - The face box's top is at 2.349 m under a 2.35 m ceiling.
  - The face box's lowest point is 0.62 m above the highest point on Mom (her hair) and about 0.9 m above the quilt directly under it.
  - The nearest flap is 0.126 m from Mom, resting on the quilt's edge at her shoulder. The other hand is 0.65 m away, on the mattress edge.

### What changed between passes, and why

1. **v1** (before the brief): the moonlit-bedroom version.
   - **Problems:**
     - The warm phone glow made the room cosy.
     - The arms came forward toward the camera as beams, with the hands meeting in front of the chest as if holding something.
     - The `wide` face (round O eyes and a round O mouth) read as a surprised emoji.
     - The figure read as a kid's cardboard robot costume.
   - **Verdict:** silly.
2. **v2** (before the brief):
   - **Changes:**
     - Cold light, with the body kept dark and only the face and hands lit.
     - The window glow behind.
     - Shorter arms, so the reach is nearly straight.
     - A new face (tall eyes, a long gape).
     - Tape glints tamed (the hot slivers turned out to be the moon and the rim light mirrored in the tape and a hand flap).
   - **Verdict:** creepy. But it used a moon key, a phone light and a volume haze, all of which the brief later ruled out, along with the tape rings.
3. **v3** (the first pass to the brief):
   - **Changes:**
     - A 15-box model with the neck chain along a 2.35 m ceiling and the face box hanging off it.
     - The nightlight key.
     - Bare joints with the tape inside.
     - The plum, lilac and rose quilt.
     - The door moved to the bed's head end so Mom's face isn't hidden behind her own near arm.
   - **Problems:**
     - The marker read grey-blue, because its specular caught the cold light.
     - The crumple facets showed through the mouth.
     - The arms were lost in the silhouette.
     - Mom was a dark shape.
4. **Final:**
   - **Changes:**
     - Matte, darker ink and a smooth face front.
     - The window lights the flap hands and Mom, and a faint grazing light edges the body.
     - Stance and hands adjusted after the probe found the shins in the bed's corner, the face box grazing the ceiling and one hand's flaps in Mom's hair.
   - **Verdict:** frightening, not a costume. The proportions, the neck along the ceiling and the face hanging upside down are no person's shape.

### Render time

- **The engine's `stills`:** 23 s a drawing at 540 x 960 and 16 samples, on 2 threads. That's about 28 s of wall time with the build.
- **My look-dev runs:** 13 to 15 s on all 4 threads.
- **The final's settings:** 10 samples on two workers should land near the brief's 14 to 17 s a drawing, since the room has no glass, volume or water. Time a 10-frame run before the long render.

### Open items for the build and the reviewers

- **Mom's near arm** is an R6 box 0.34 m thick, so from the doorway it's a dark slab across the middle of the frame, mostly under the caption here. It's there for the brief's "nothing reads as pinned". Her close (L54) should frame it as an arm with its hand.
- **The lower 30% of the frame** is the dark front of the bed. It's good for the caption, but there's not much to see.
- **The chain's shadow** is a big dark wedge over the top-left of the ceiling. It's physically right and it prefigures L46, but the critic should say whether it reads as part of the creature.
- **Neck box size:** I shortened the neck boxes to 0.27 m so the chain fits this small room. The count is the brief's, and the size was my call.
- **`land`** (move the figure so the face box hangs over a point) doesn't converge reliably, so this pose places the figure directly. Use explicit places per shot.
- **"Face-down":** I read it as the face box hanging from the chain's end with its drawing upside down from the door. That's the README's "a face upside down", and it's the uncanny part of the still. If the brief meant the face box lying flat along the ceiling, it changes only `_chain`.
- **Look-dev switches:** `MOVING_DAY_FLAT` (flat light, ceiling hidden) and `MOVING_DAY_CAM` (replaces the shot camera) are in `set.py` and off by default.

## Step 4, the non-visual part (generator, voice, checks)

**The generator:** `reels/blocky/stories/moving-day/generator/make_story.py`, with relative paths, writes the real `story.json` from the scriptwriter's `generator/lines.json`. The provisional file is gone.
- **Basics:** slug `ep17-moving-day`, voice A (`am_adam`, tempo 1.03, rate 1.45), key `#b98aff`.
- **Grade:** the brief's grade, with `red_line` 0.79 set ahead for the gold section.
- **The loop:** tail 0 (no fade at either end) plus a silent 0.25 s beat after L78 (`P03`), the brief's hard cut into L01.
- **Cast:** both skins sit off the cardboard ramp (boards: hue 29–30°, lightness 41–53%).
  - Mom is `#a86a58` (hue 14°, the ruling), at height 0.95.
  - I'm `#9c5e4c` (hue 13°, a family likeness), in a solid olive top, charcoal trousers, grey sneakers and black `cap` hair.
- **Score and sound:**
  - The brief's score: dorian on G2 at 74. The piano comes in only at P02, in the relative major (root 41).
  - The brief's ambience, sfx and three silence holes, all anchored to line ids.
- **Shots:** a 77-shot first pass from the brief's shot plan, each with its line anchor, room, description and step (ones for L48–L55 and P01, fours for the clock wides, face and night inserts and the shelf, twos for the rest).
  - Mom's room shots (L48–L62) have real cameras. The L48 wide is the creature test still.
  - The other 63 are tagged `"todo": "camera"`, with that wide as a stand-in until their rooms are built.
- **Staging so far:** only the 3 a.m. scene. The Boxes, Mom and I are hidden everywhere else until those rooms and the morning poses exist. The nightlight is on from L44 to L62, and the lamp comes up at L51.1 over 0.8 s (a new `dur` ramp on the lamp cue).

**Voice and checks:**
- `voice`: 78 lines in 220 s.
- `check`: 0 blocks. One warning: six fast filler captions are up under 0.2 s ("It was", "And on", "in there", "Back in"). They follow the voice, as the sync rule wants.
- `asr`: 0 words heard wrong (574 of 574, match 0.995).
  - "Mom" is heard as "Mom", so `voice.py` needs no Mom/mom spelling.
  - "hall"/"haul" and the flapped "ladder"/"latter" are one sound in General American, so they join "threw"/"through" in `voice.HOMOPHONES`. A test covers it, and it doesn't touch any render or mix.
  - L02 and L23 are read a touch slower: "flaps still" ran together, and "had" was swallowed.
  - L53's spoken text (only) has a comma, "Tucked, round", so it isn't heard as "tucked around". The caption doesn't change.
- `pytest reels/blocky`: 40 passed.
- The still renders from the real story at L48.1 (frame 2408, S46), and the probe is clean.

**Length: 134.43 s (2:14.4) with every hold the brief allows** (P02 2.4 s, L66 +0.3, L77 +0.2, L61's gap 0.7, P01 1.4: about +1.6 s). That's 0.57 s under the owner's 2:15 floor. The brief says the scriptwriter adds a line of real story rather than stretching silence.

**Before `mix` can run:** the brief's three new sound kinds aren't in `sound.py` yet, and they need building opt-in, with tests:
- `tape`, the packing-tape peel under L02.
- `scrape`, cardboard on boards, with `distant`.
- The cardboard `creak` (`"tone": "cardboard"`). Today's `creak` is wood, which is lookout's.

Until then `sound.sfx` raises on `tape` and `scrape`.
