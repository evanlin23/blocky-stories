# ep14-floor-thirteen: designer notes (motion-designer)

## Creature test, pass 2 (2026-10-31, after the critic's "revise", 3/10 scary, 3/10 readable)

**The still:** `review/creature-test.png`, the same file as `review/creature-test-v12.png`.
- **Phone version:** `review/creature-test-phone.png`, 360 x 640.
- **Settings:** 540 x 960 with 16 samples, finished by `post.finish` with the brief's grade, grain, `red_line`, bloom and the script's caption for the held bump shot ("the DOORWAY.", L55).
- **Reproduce it:** cue `{"pose": "bump", "lit": "all", "glow": 1.0, "eye": 2.0}`. The harness variant is `v/final2_pose.json` in `/tmp/claude-0/-home-user-content/b641d2f4-4361-513a-b129-7ef6b9d31a8a/scratchpad/ct/`. The named pose reproduces the still to the pixel.

I did the critic's five changes in its order. Where I couldn't do one as written, I say why.

### 1. Clear the gap

- **Camera:** on the car's centre line at the back wall, at (0, 0.92, 1.5), 1.5 m up, with a 19 mm lens.
  - It's aimed a little down, at 1.36 m in the doorway, not 1.6 m. That puts the "13" in the top 10% (8 to 12% of the height) as the critic asked, and lifts the face clear of the caption band.
  - At 1.6 m the indicator sat at about 20%.
- **The cast:** both are side-on to the walls, cold-rimmed slivers at the frame's edges. Neither overlaps the 0.8 m gap anywhere from header to sill.
  - Me: violet hood, yaw 70, my head turned 50 degrees toward the doorway, at (-0.46, 0.10).
  - Mr. Okafor: yaw -70, head turned toward the doorway, about 15% of the width at the left edge, at (0.42, 0.15).
- **Contact probe: 0 overlaps.**
- **Why I'm not over the jamb and floor panel, as the critic suggested:**
  - I tried it, and nearer the doors the rig's hood (a 0.54 m box) swings into the right wall when my head turns.
  - My side-on sleeve also hits the floor-panel buttons, and the front wall stops a side-on R6 arm.
  - So I stand 1 m back from the doors, not "a foot from my face". Script L57 ("a FOOT / from my FACE") doesn't match this held shot. **The scriptwriter and producer should either change the line or plan a closer insert of the panel over my hood for L57.**

### 2. The bow and the folded gloves

- **The critic's `bend 30` at `[0, -1.50]` doesn't fit the head it asked for in change 4.**
  - With the deeper head, the 7 cm neck and the flared cap, any pose that keeps its arms in the car-door plane drives the cap through the 2.1 m door head and the indicator. I probed seven combinations.
  - So the head stays just on 13's side of the car-door plane.
  - I gave 13's own doorway a taller opening, 2.45 m. Its hall is "older" in the brief, and the brief only fixes the car's 2.1 m door. 13's ceiling is now 2.7 m.
  - Only the car's door head stops it, and from inside that header crops its cap, so the doorway is visibly too short for it.
- **The probed pose (`POSES["bump"]`):**

| Setting | Value |
|---|---|
| Feet | (0, -2.04), 0.56 m past the sill; they never cross it |
| Bow | 40 degrees |
| Head | lifted back 2 degrees, so the face tips about 38 degrees down at us |
| Arm fold | 1.6 |

  - The bow puts all nine buttons just under the header.
- **The arms:** they now hang under gravity, whatever the bend.
  - I set the fold in the body's upright frame and took the bow back out.
  - Before this fix, the inward swing turned into a forward swing in any bow, so the gloves never met.
  - Both swing in 19.5 degrees and the gloves cross, right over left, below its knees. At 3.6-unit arms that holds standing upright too, so the arms don't need lengthening.
- **The doors:**
  - The car leaves stop 0.80 m apart, and from inside they overlap its shoulders.
  - Its sleeves sit about 20 cm behind the leaves, not 1 cm, because of the cap.
  - **For the build:** the doors can't physically touch its shoulders in this pose. The bump animation should stop the leaves at 0.80 m as if they hit it, or the cap has to shrink so its arms can come into the door plane. That's the producer's call.

### 3. Light the monster, not us (the `thirteen` state)

- **Side key:** the floor panel's spot, now 42 W, is aimed at the folded gloves. Gloves peak at 183 luma (p90 131), the brightest thing that doesn't glow.
  - The gloves are matte now (roughness 0.88, specular 0.12), so they don't carry hot spots.
- **Sleeve rims:** two 0.2 m, 80 W area lights from 13's side, at x = ±0.75, 0.6 m past the sill and 1.5 m up, aimed down each sleeve.
  - The arms read in outline from shoulder board to glove.
  - They catch the car doors' leading edges as thin lines (change 5).
  - **Light linking:** they light only its arms and the car leaves. That keeps them off us and off its face.
- **Brass pings:** a 36 W area light of 13's light off the sill, seen only in reflections.
  - It's linked to its brass alone: jacket buttons, hem, collar edge, shoulder-board edges, trouser stripes, cap band and panel frame.
  - The buttons now ping down the jacket.
  - Unlinked, it washed the glass buttons white and clipped the bezels.
  - The cuffs are left out because they clipped.
- **No chest light:** the 16 W chest light is off in this state.
- **The ceiling:** still 5%, but a new `"cast_dark": true` on the lights cue keeps it off the cast (light linking, opt-in per shot).
- **What lights us:** only its own cold glow, a 6 W area light spread 95 degrees, rims the inner side of each of our heads.
- **13's back wall:** a 120 W wash high on it, so its head and cap stand out black against it.
- **Measured on the finished still** (luma, 0 to 255; the picture without the caption has 0.000% white pixels and 0.028% with any channel at 254 or more):

| Region | Luma |
|---|---|
| The eye | 242, the hottest thing in frame |
| The other eight buttons | 160 to 199 |
| The brass frame's glints | 207 |
| My hood's rim | 194 at peak, p90 45 (only its glow; the hood's top under 25) |
| The indicator | 185 |
| The gloves | 183 |
| Mr. Okafor | 203 at the rim, p90 22 |
| The door-edge lines | up to 200 |

  - Nine lit buttons count as nine, with no reflected ring anywhere.
  - Our faces aren't lit, so nothing of us reflects in its lacquer or brass.

### 4. Make the head a head

- **The block:** a black lacquer block 0.58 m square and 0.40 m deep (was 0.54 x 0.14), on a 7 cm wool neck block.
- **The socket:** the brass frame and plate sit 8 cm back inside a 4 cm lacquer lip (brow, cheeks, chin). The nine lights sit in a black socket and the outline is black on black.
  - The panel inside the lip is 0.52 m with its frame, and the buttons are as before.
- **The cap:**
  - a plain brass band at head width
  - a wool crown that flares 10 cm wider than the head each side
  - a glossy black visor 15 cm deep, straight out from the brow
- **Why the visor isn't 25 degrees down:** at the critic's 25 degrees, the bow tips the visor about 65 degrees down, and it hid the top row. Square to the face, the bow already puts it about 40 degrees down.
  - A small light under the visor draws it as a faint cold edge.
- **Body proportions changed so the head fits under the ceiling:** legs 2.6 units, torso 2.05, collar 0.25. Its height is 2.43 m with the cap.
- **The alternative I tried once and didn't use:** the house rounded head with the panel set in it (`set_options "head": "round"`, `review/creature-test-v11.png`).
  - At 360 px it looks almost the same as the block, because the cap and the dark hide its outline.
  - The lacquer under the panel mirrors a fourth row of rings, so nine read as twelve.

### 5. The doors visibly shut on it

- Each car leaf's leading edge is a lighter satin strip (`#c8ccd2`). The sleeve rims catch it, so two thin cold lines run down beside its sleeves, up to about 200 luma.

### Pass 2 stills (in `review/`)

- **v9:** the critic's camera, the 40-degree bow, the socket head and cap, gravity-hung folded arms. The eye, gloves and brass cuffs clipped, and my hood's top was over 40.
- **v10:** light linking. The brass ping touches only brass and the sleeve rims touch only its arms and the leaves. Its chest light is off, the ceiling is kept off us, and the buttons have a fuller glow round a hotter eye.
- **v11:** the round-head alternative, not used.
- **v12 (final):** Mr. Okafor moved into the left edge, softer door edges, matte gloves, and the script's caption.

**Render time per still** (idle 4-core machine, one Blender process):
- 13.7 s at 540 x 960, 16 samples, 4 threads
- 19.6 s at the final render's settings (10 samples, 2 threads)
- 2 s for the 270 x 480 look frames
- About 45 look frames and 10 full-size stills this pass.

### My honest read of pass 2

- **What works:** at phone size it now reads as a figure, not an object.
  - A tall thing in a black uniform fills the lift doorway, its cap cropped by the door head, so it's too tall for the door.
  - Its head is a black block whose face is nine cold lights set back in darkness, the centre one burning hotter, like an eye.
  - Brass buttons glint down its chest, and its arms run long and straight down to white gloves crossed below its knees.
  - The doors' edges show either side, with "13" over it all.
  - It's uncanny and quietly threatening, not silly. I don't see a jewellery box or a speaker any more.
- **What's still weak:**
  - The long straight arms make a V that can read as a black wedge or funnel.
  - The crossed gloves are two white blocks that could read as something set on the floor.
  - We are only rimmed slivers at the edges, so the frame gives scale by the doorway, not by us.
  - It's dread, not a jump scare.
- **What I'd expect:** a clear step up from 3/10. I'd guess about 6 on both scores.
- **Still to do after the still passes** (approved opt-in additions with defaults unchanged, held until it passes):
  - the open-front hood and headphones extras in `rig.py`
  - the producer's call on the L57 line and the bump contact

## Creature test, pass 1 (superseded where pass 2 differs: head, pose, light rig, camera, cast placement)

**The still:** was `review/creature-test.png`, now `review/creature-test-v8.png`.
- It's 1080 x 1920, drawn at 540 x 960 with 16 samples and finished by `post.finish`: bloom, the brief's grade, grain, `red_line` and a caption.
- The caption is a placeholder ("INTO the DOORS.") in the brief's key colour, brass gold `#ffbf3f`. The script's line goes in when the build starts.
- **What it shows:** the brief's bump frame, seen from inside the lift.
  - The Attendant is bowed into the half-shut doors, with its feet on 13's side of the sill.
  - All nine buttons are lit, and the centre eye is the hottest.
  - Its cap and shoulders are a silhouette against 13's cold light. The car's indicator shows "13".
  - Mr. Okafor's head is in the left foreground and my violet hood is on the right, a foot from its panel.
- **Phone-size comparison:** `review/creature-test-phone.png`, 3x3 against 2x2 at 360 px wide.
- **The 2x2 comparison:** `review/creature-test-2x2.png`, with identical settings.

### Button count: 9 (3x3), as in the brief

- **My verdict:** at phone size the 3x3 reads as lift buttons with one lit eye. The 2x2 reads as four big holes: a socket, a die face or a game pad. I agree with the producer, so 3x3 stands and the script keeps nine turns.
- **Numbering:** buttons are numbered left to right, top to bottom, as you look at its face.
- **The eye** is the centre button (4).
- **The order they go dark** (outside-in, the eye last): 0, 8, 2, 6, 1, 7, 3, 5, 4. That's top-left, bottom-right, top-right, bottom-left, top-middle, bottom-middle, middle-left, middle-right, centre.
  - It's `GRIDS[(3, 3)]["dark"]` in `set.py`.
  - A cue `"lit": n` leaves the last n of that order lit.

### The Attendant, as built (`reels/blocky/stories/floor-thirteen/set.py`)

- **One model:** `build_attendant()` builds it once and `pose_attendant()` only places it.
  - The legs hang off a root at its feet. Everything above them hangs off a waist at its hips.
  - The cue sets the pose: `pos`, `yaw`, `lean`, `bend`, `head` [pitch, roll, yaw], `fold`, and which buttons are lit.
  - `POSES["bump"]` is the doorway pose that passed the contact probe. A cue `{"pose": "bump"}` reproduces this still to the pixel (I checked).
- **Sizes** are in rig units (`rig.S` = 0.34 m), with a person's in brackets:

| Part | Rig units | Metres |
|---|---|---|
| Legs | 2.7 long, 0.84 wide (2.0, 1.0) | 0.92 long |
| Torso | 1.6 x 0.9 x 2.2 (2.0 x 1.0 x 2.0) | 0.54 x 0.31 x 0.75 |
| Arms | 0.72 square, 3.6 long (1.0, 2.0) | 0.24 square, 1.22 long |
| Gloves | the last 0.62 of the arm | 0.21 |
| Collar | 0.3 high | 0.10 |
| Head panel | 1.6 square, 0.42 deep | 0.54 square, 0.14 deep |
| Cap | 0.32 over the panel | 0.11 |
| Height with cap | 7.12 | 2.42 |

- **The panel:**
  - A 3 cm brass frame round a 0.48 m face plate.
  - Buttons on a 16 cm pitch. Each bezel is 0.14 m across, round a frosted glass face 0.10 m across.
  - Each button is about 1/11 of the frame width in the still. The brief's close-up floor is 1/12.
- **Materials and colours:**

| Part | Colour | Finish |
|---|---|---|
| Jacket and trousers (wool) | `#14151a` | roughness 0.82, faint mottle |
| Buttons, piping, side stripes, cap band | brass `#c8a050` | metal, roughness 0.3 |
| Panel frame | duller brass `#a8843f` | roughness 0.48 |
| Bezels | dark brass `#4e3d24` | roughness 0.5 |
| Head housing | black lacquer `#0c0c0f` | clear coat |
| Face plate | brushed dark metal `#1c1a17` | |
| Gloves | `#ddd8cc` | roughness 0.75; never pure white |
| Shoes and cap peak | `#0a0a0c` | gloss |
| Button glass | `#0b0e12` | roughness 0.32, so no side light glints in it like a second eye |

  - These changed from my first draft: the bezels went from `#6d5531` to `#4e3d24`, and the frame got its own duller brass (v5 to v6).
- **The glow:** `#c6dbff`, ice-white with a faint blue.
  - I tuned it from the brief's `#d4e6ff`, which went pure white under AgX at the brightness the eye needs.
  - **Ring-lit, like a real lift button:** the emission is 0.16 in the middle, 1.0 from 0.70 to 0.84 of the radius, and 0.25 at the bezel. A bright ring round a darker middle reads as an iris round a pupil.
  - **Each bulb has its own fixed brightness for the whole film:** `BULBS` = 0.9, 0.72, 1.0, 0.8, 1.0, 0.68, 0.95, 0.84, 0.76. An even grid read as an LED board.
  - In the bump, `glow` is 1.0 and the eye's gain is 1.9.
- **The arms:** folded in front, right over left, 16 degrees inward.
  - Upright they hang 6 to 9 degrees forward.
  - In the bow `fold` is 0. They hang straight from the shoulders and the stoop carries them forward.
- **The bump pose:** feet at (0, -1.82) on 13's floor, about 0.55 m past the sill line.
  - It's bowed 54 degrees at the waist so its cap clears the 2.1 m door head.
  - The panel is lifted back 24 degrees, rolled 14 and turned 13 toward me, so it points down at my face.
  - The car doors stop 0.80 m apart, a centimetre in front of its upper arms. From inside, the leaves read as closed against its shoulders.

### The set for the still (all in `set.py`, the start of the real set)

- **The car:** 2.1 m wide (see below), 1.9 m deep, with a 2.5 m ceiling. The opening is 1.1 x 2.1 m.
  - Walls: dark walnut `#3a2618` panels, satin (roughness 0.48), with dark seams and a brass handrail.
  - Doors, jambs, header and sill: satin steel `#8e9195`, metallic 0.6, roughness 0.55, so no face reads in them.
  - Floor `#141210`. Ceiling `#2a2b2d`, with one cool-white light panel at the back of the car.
- **The floor-button panel:**
  - 20 plain round buttons in two columns of ten, using the Attendant's button model with a 4.4 cm glass face.
  - The lobby's button, at the bottom, has a raised brass star.
  - Under them are door-open and door-close buttons with raised brass arrows.
  - No numbers, letters, bell or braille.
- **The floor indicator** over the doors: a black glass strip.
  - Two segment digits are built from blocks (no font), plus up and down triangles.
  - It's lit in the glow colour at 0.5, below the buttons.
- **13's hall:**
  - Umber carpet `#3b2a1c` and dark olive-brown walls `#36321f`.
  - Unlit brass sconces, and shut doors with blank brass plates.
  - The fog is `#15120f` at 0.06 from 2.5 m.
- **No text anywhere** but the indicator's digits.

### The light rig (the `thirteen` state; no front light)

- **Ceiling:** 5% of its 60 W panel, steady with no flicker. The diffuser is dim, at the top of the frame.
- **Side key from the floor panel:** a 70 W spot, neutral `#e3e6ea`, from the panel's height beside the doors, aimed at its head.
  - It's neutral so the brass still reads as brass in a cold frame.
- **13's cold light** (`#a9c4e6`):
  - an 80 W area light behind it on the hall's floor and back wall, so it stands out as a dark silhouette in a lit doorway
  - a 32 W area light right behind its head, for the rim on the cap and shoulders
  - a 140 W spot along the car floor, for its shadow
  - a 30 W point light far down the hall
- **Its own glow:**
  - a 5 W area light 0.3 m in front of the panel, spread 45 degrees, falling on whoever it's tipped at
  - a 16 W point light under its chin, which lights its collar and jacket from below
  - a 4 W point light under the cap peak
  - The last two don't show in reflections.
- **Grade:** the brief's. Shadows [0.01, 0, -0.01], highlights [-0.02, 0, 0.03], saturation 0.9, contrast 1.12, vignette 0.42, bloom 0.45, grain 0.012, `red_line` 0.79. Exposure 0.
- **Measured on the finished still** (luma, 0 to 255):

| Region | Luma |
|---|---|
| The eye | 245 (R 234, G 248, B 255) |
| The other eight buttons | 183 to 196 |
| My hood's rim, lit by its glow | 205 |
| The "13" | 176 |
| 13's wall behind it | 174 |
| Mr. Okafor's shoulder | 165 |

  - Pixels at white (all channels 250 or more): 0.000%. Pixels with any channel at 254 or more: 0.04%, all of it the blue channel inside the eye's ring.
  - No skin shows in the still.
- **Phone size:**
  - The head panel is about 45% of the frame width and sits at 27% to 55% of the height.
  - The caption band is at 61% to 70%, so it's clear of the face.

### Cast (placeholders from the brief's table, built with `rig.py`)

- **Me:**
  - a solid dusty-violet hoodie `#6a5c94` with the hood up
  - stone-khaki trousers `#8f8566` and orange sneakers
  - a short black swoop fringe, skin `#d7a17a`
  - round eyes and brows
  - "terrified" for the scare
- **Mr. Okafor:**
  - a solid sage collared shirt `#8a9a6b` with a red tie `#b8322a` (the `tie` extra)
  - brown trousers `#5a4632` and dark brown shoes
  - black cap hair `#1c1716`, skin `#5b3a28`
  - round eyes, brows and `bags`
  - "scared"; never "angry"
- **No headphones yet.** They're the brief's new rig extra.
- **Placement:** in the still I'm side-on against the front-right wall with my head turned to it. He's square in the back-left corner. Those were the only places two R6 riders fit without touching a wall, a rail or each other, with a clear line to its face.

### Contact probe

- **The script:** `probe.py` in the scratchpad, at `/tmp/claude-0/-home-user-content/b641d2f4-4361-513a-b129-7ef6b9d31a8a/scratchpad/ct/probe.py`. It poses the set and cast exactly as `bl_story` does, then runs BVH overlap on every pair of meshes from different owners (the Attendant, each cast member, the set). It ignores shoes standing on floors.
- **Final still: 0 overlaps.**
- **What earlier passes hit**, all fixed:
  - its sleeves cut through the car door leaves
  - its cap went into the door header and transom
  - its shoulder boards hit 13's door edge
  - my sleeve went into the right wall, the handrail, the jamb and the floor-panel buttons
  - his sleeve went into the left handrail and his hair into the back wall
  - our arms crossed

### Passes (all in `review/`)

1. **v1** (270 x 480): the pitch's original scare, with the lights back and it inside the car, before the brief. It had steel walls, solid cyan buttons and placeholder cast. The buttons clipped white, it was far too close, and it read as a light board.
2. **v2** (270 x 480): a smaller cap and the cast moved to the front corners. The grid still read as a die or an LED panel, and the body was invisible in the dark.
3. **v3** (540 x 960, left and right): solid glow against ring-lit buttons, close up. The rings read as real lift buttons and as pupils, so I kept the rings.
4. **v4** (540 x 960): the brief's doorway bump. It has the walnut car, satin doors, ice glow, the "13" indicator and the brief's cast. It read as a device in a doorway: the support lights were 10 to 20 times too weak next to the buttons, and the body was black.
5. **v5:** pulled back, with its own glow on its chest, the side key and a rim. The stoop and the uniform read, but the brass frame and bezels glared gold (a jewellery box) and the rings clipped.
6. **v6:** darker bezels, a duller frame, frosted glass to kill the glint that read as a second eye, uneven bulbs, a hotter centre eye and thinner rings. A sliver of 13's lit wall shows round its head. It stopped reading as an LED board.
7. **v7:** the contact-probe pass.
   - I widened the car to 2.1 m and put the cast in poses that clear the walls.
   - I deepened the bow to 54 degrees and lifted the panel back. Before, the face was tipped 50 degrees down: it pointed at my feet and read as a stove-top. The cap also went into the header.
   - The cap is now a clear silhouette against 13's light.
8. **v8 (final):** the camera went up to 1.9 m.
   - The open gap behind it becomes a lit doorway, with the dark leaves either side of it and both our heads framing it.
   - The brightness order is fixed: the eye, then the buttons, then everything else.
   - The "13" dropped below the buttons, and 13's wall went from 214 to 174.

**Tried and dropped:**
- **Low cameras:** the face sank into the caption band and the cast blocked it.
- **Close-ups over my shoulder:** the body is lost, and it reads as a speaker.
- **Diagonal two-shots:** the face is too oblique.
- **A 22 degree head roll:** its corner covered the indicator, so "13" read as "17" or "12".
- **No cap:** no difference at phone size, so the cap stays for continuity.

**Render time per still** (idle 4-core machine, one Blender process):
- 13.5 s at 540 x 960, 16 samples, 4 threads, plus about 1.5 s to build the scene
- 19 s at the final render's settings (10 samples, 2 threads)
- 2 s for the 270 x 480 look frames at 6 samples
- About 60 look frames and 12 full-size stills in all.

**The scratch harness** is in the scratchpad at `/tmp/claude-0/-home-user-content/b641d2f4-4361-513a-b129-7ef6b9d31a8a/scratchpad/ct/`. None of it is in the repo.
- `run.py` writes a scratch story whose `set.py` loads the repo's floor-thirteen set. It renders through `bl_story.py` and finishes with `post.finish`.
- The final variant is `v/final_pose.json`.

### My honest read

- **What works:** at phone size it's uncanny and not silly. It reads in one glance as a tall thing in a uniform and cap, bowed into the lift doorway, with a head of nine lift buttons and one burning eye, a foot from us. The backlit doorway, the cap silhouette and the single hot eye do the work. The brass-and-black uniform stops it reading as a vending machine.
- **What holds it back:** it's eerie rather than jump-scary.
  - A flat square head still carries a little "box head" risk. The tilt and the cap fight it.
  - The doors closing on it read only as dark leaves either side of the lit gap, because our heads cover the leaves.
  - The bottom quarter is our dark shoulders.
- **What will sell it is motion:** the doors bumping it and rolling back while it doesn't move. A still can't show that.
- **If the critic still finds it robot-like, try next:** a closer insert of the doors against its shoulders, or a hard cut from one lit eye to all nine.

### For the producer and the scriptwriter

(Answered on 2026-10-31 by the orchestrator. The 2.1 m car, the 2.42 m height, the `#c6dbff` glow and the panel past the front-wall line are all fine. The open-front hood and headphones in `rig.py` are approved as opt-in extras, to build once the still passes.)

- **Nine buttons are confirmed.** The eye is the centre, and the dark order is above.
- **The car is 2.1 m wide inside, not 1.9.**
  - R6 riders are 1.36 m wide with their arms.
  - In 1.9 m, two of them can't stand clear of the handrails and each other with a sightline to the doors.
  - Please confirm, or tell me to shrink the riders instead (the README's seated-rider fix).
- **The Attendant is 2.42 m with its cap.** The brief's 2.5 m would touch the 2.5 m ceiling, so 2.42 m is "a hand's width under".
- **The gloves:** with 3.6-unit arms, they hang at its knees when it stands upright. They're below the knees only in the bow. If Saturday's "gloves below its knees" has to read on a standing pose, the build needs about 4.0-unit arms or a lower glove. Your call.
- **The sill:** in the bow its feet stay on 13's side of the sill, but its panel reaches a few centimetres past the car's front-wall line. Standards should confirm that still counts as never crossing the sill.
- **The rig's hood covers the face.**
  - `rig.py`'s `hat: "hood"` is a closed box, so from the front my face doesn't show, and the `swoop` fringe pokes through it.
  - That's fine from behind, as in this still. Before any front shot of me ("My face, lit cold from below"), the build needs an opt-in open-front hood in `rig.py`, with defaults unchanged.
  - I didn't touch `rig.py` for the still. The headphones extra is still to build too.
- **The caption key, brass gold `#ffbf3f`,** reads well at phone size over the all-lit doorway frame. The golden balcony two-shot doesn't exist yet, so that half of the brief's check waits for the build.
