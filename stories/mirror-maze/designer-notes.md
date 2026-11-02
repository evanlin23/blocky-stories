# ep14-mirror-maze: designer notes (motion-designer)

## Creature test (2026-10-31)

This round is only the creature test still and the replay test. There's no `story.json` and no generator yet. The
still went through the real path: a throwaway story in the scratchpad, linked to this story's `set.py`, rendered by
`bl_story.py` and finished by `post.finish` (the grade, bloom, rain, grain and one caption).

**In `review/`:**
- `creature-test.png`: the current pair, from pass 2b (p2i, below). Each frame is 540 x 960 at 16 samples with the
  story's grade, rain and the script's L54 caption chunk "Her EYES". **Left is the copy, right is the real Tasha** in
  the same pose and light. The image isn't labelled, so a reviewer can do the cold read first.
- `creature-alone.png`: the p2i copy on its own, as its frame would be in the film, with no comparison partner.
- `creature-alone-p2h.png` and `creature-alone-p2i.png`: pass 2b's two versions, alone.
- `creature-test-p2g.png`: pass 2's final pair (p2g), kept.
- `creature-test-v17.png`: pass 1's final pair (version 17), kept.
- `creature-pass3.mp4` and `creature-pass3-strip.png`: pass 3, the face late on its own head. `creature-alone.png` is
  now its end frame.
- `truck-catchup.mp4` and `truck-catchup-strip.png`: the truck catch-up cold test.
- `replay-test.png`: the replay test, three runs of 3 s at preview size on every frame (the final's `step: 1`),
  shown every 0.1 s and cropped to the figure.

### The copy, built once (`reels/blocky/stories/mirror-maze/set.py`)

- **What it's built from:** `copy_spec()` deep-copies Tasha's cast spec and changes one thing, `face.eyes` to
  `"mirror"`. `build_copy()` builds it as `rig.Character("copy", ...)` and puts a negative x scale on its root.
  There's no second hand-made spec, so any change to Tasha carries over. The real Tasha is still cast as usual.
- **Tasha's spec as I built it** (it goes into `story.json` at the build):
  `{"age": "adult", "skin": "#b07850", "shirt": "#f0c419", "pattern": "solid", "collar": "#d8aa12", "pants": "#151518",
  "shoes": "#0c0c0e", "sleeves": "long", "hair": "swoop", "hair_c": "#5a2a48", "fringe": "hard", "hat": "none",
  "extras": ["coat", "hooddown"], "zip_c": "#3b3224", "face": {"eyes": "round", "brows": true, "ink": "#24131f"}}`.
  `set.py`'s `wet_coat()` makes the mac satin: roughness 0.42, a 0.18 coat and a 0.25 sheen. The copy shares that
  material.
- **The three flips, and nothing else:**
  1. **The fringe.** The stock swoop already hangs its chunk over her right brow (screen left when she faces us). It
     was too subtle at phone size, so `"fringe": "hard"` adds a long lock from the crown down over that brow, stopping
     above the eye. On the copy the whole fringe sits on the other side.
  2. **The smirk.** The face texture flips with the mesh, so her default `smirk` lifts on the other side. I checked it
     in a front look-dev.
  3. **Handedness.** The copy's keys are in the rig's own local terms, so the same `arms` key raises the arm on the
     other side, the way a reflection does. Its `pos` and `yaw` are world terms and aren't mirrored, because Blender
     scales before it rotates. So the copy that is my reflection is my own keys verbatim, with `pos` and `yaw`
     reflected across the glass plane. I posed the still that way: I'm the copy's reflection across the plane between
     us. Watch for this in the generator. On the copy a head yaw turns the other way, and the rig's `arms[0]`
     ("left") is screen left, which is the character's own right.
  - **Not flipped, because none of it is one-sided:** the centred zip, the two coat panels, the collar, the hood lying
    down at the back, the plain black jeans and boots. The eyes are symmetric.
- **The normals check** (the brief asked for it). I rendered the copy, then an unmirrored rig with the same
  mirror-black eyes under the mirror image of the same camera and three lights, and flipped that render left to right.
  The two match to sampling noise: a mean difference of 1.15/255 on the figure, p99 11, and 0.28% of pixels off by more
  than 24, all on edges. The negative scale shades correctly, including the bevel and weighted-normal modifiers, and
  the eyes still draw black after the face texture flips.
- **The eyes.** `faces.py`'s new `mirror` style uses a round eye's exact outline box (fill and outline both
  near-black `#07070a`), so it can never be bigger than Tasha's. It has no white, no pupil and no glint, and it keeps
  her brows and mouth. On the head, `matte_eyes()` turns the copy's head material fully rough with no specular
  wherever the texture is that black. That's needed: a look-dev without it shows a broad grey sheen across both eyes,
  which is the "sunglasses" read.
- **The rest of its continuity list as code:**
  - `LAG = 0.395` s. I'm locking it here, so 76 bpm stands. The test gave me no reason to move it.
  - `copy_blink()`: it blinks only when I blink, LAG later.
  - It isn't cast, so `sound.py` never gives it a footstep.
  - `pose_copy()` reads a story-local `stride` key (degrees the legs are held apart while it stands), for the truck's
    freeze with one foot up and the replay's step. `acting.py` ignores unknown keys, as it did with ep13's `bow`.

### The set so far (`set.py`, from `kit.py`'s parts, no text anywhere)

- **The field:** dark mud with wet patches, and two crooked lanes of plywood duckboards on battens running toward the
  maze, wet (roughness 0.3).
- **Puddles:** six still puddles on the boards and in the mud, near-black mirrors.
- **The worklight:** the crew's caged worklight on a low tripod (`WORK`). Its beam is aimed per shot, and the lamp head
  turns to match.
- **The maze front:** a trailer with a skirt, a deck, five steps and rails. It has plain violet wings with silver and
  violet diamonds, a stripe frieze, a silver band round the arch, and two rows of round lilac-white bulbs round the arch
  plus one along the roofline (110 bulbs). They're emitters that light nothing and never chase, and a wash light
  gives their glow on the facade.
- **Inside the arch:** a dark room, a ply floor and six clear panes in steel frames on a triangular grid, with 24 bulbs
  on their rails.
- **Where the scare ends:** `SCARE = (1.0, 4.3)`, on the boards by the worklight, with the arch over its shoulder.

### The final frame (version 17), so the build can reproduce it

- **The copy:** at (1.0, 4.3) on the boards, yaw 52, so its body is turned 75 degrees from the lens.
  - Local keys: `head [75, 8]` (turned back onto the lens and dropped 8 degrees), `arms [62, 6]`, `side [-6, 0]`
    (the far hand frozen half down, at chest height), `expr "blank"`, blink held.
- **Me:** its reflection at (1.29, 2.83), yaw 150, with the same local keys.
- **The real Tasha:** the same spot and yaw, with `mirror_pose` keys (arms and sides swapped, head yaw negated), so the
  picture matches.
- **The lens:** 32 mm at (0.10, 2.18, 1.32), adult chest height, aimed at (1.0, 4.3, 1.31). The depth of field is
  2.3 m at f/1.4.
- **The look:** fog `#1c1826` at density 0.1 from 3.5 m, sky `#120f18`.
  - Grade: shadows [0.03, -0.02, 0.07], highlights [-0.02, 0, 0.03], saturation 0.9, contrast 1.1, vignette 0.5,
    bloom 0.35, grain 0.012, rain gain 1.2.
- **The lights** (`looks`, in watts). Nothing comes from the lens side.
  - **face:** an area light 0.1 m across, 5 W, `#d4dcff`, at (0.89, 4.02, 1.2), about 0.35 m under the chin and in front
    of it. It reaches only `copy.headm` and `tasha.headm` (`light_only`) and casts no shadow. That's the key from below.
    It has to be shadowless, because a head turned over a side-on shoulder otherwise loses half its face to the
    shoulder's shadow.
  - **hair:** 4.5 W, linked to the hair pieces only, so the plum and the fringe read.
  - **work:** the worklight, 300 W, cone 45, aimed at the far arm and the coat's front (1.3, 4.05, 1.0).
  - **rim:** 1700 W, cone 13, `#aab4ff`, from behind left at head height.
  - **rim2:** 900 W, cone 16, `#aab4ff`, from behind right.
  - **bounce:** 6 W off the boards on her front side.
  - **kick:** 420 W, linked to `me.*`.
  - **Gains:** wash 0.5, inside 0.6, bulbs 0.12.
- **Measured** on the finish without the caption:
  - The head is 47% of the frame width.
  - The face is 0.75 at p95 and 0.96 at its brightest (the chin's bottom edge), so nothing clips.
  - The coat is 0.61 at p99 and 0.73 at its brightest.
  - No clipped pixels below the top 15% (the bulbs are up there).
  - The copy's eyes are the darkest thing near its face.
  - The face is clear of the caption band, and the caption passes `layout_problems`.
  - "EYES" in `#ffd23a` sits partly over the coat's lit front, and the dark outline carries it.
- **Cost:** 18 to 19 s a frame at 540 x 960 and 16 samples, on all 4 threads.

### The versions, in order

There are 17 finished versions, each 540 x 960 at 16 samples with the grade and the caption, after about 25
low-resolution layout and light tests. The brief's fix order is versions 2 to 4. Everything after that is staging.

1. **The brief's starting point:** Tasha's eye size (by construction), the copy wearing my `scared` face, the worklight
   low at the side, lilac rims, and the face light from below. The cold pick is instant, but it reads as a surprised
   plush toy. The skin clipped (p95 0.996), the hair went black, I was an unreadable black slab, and the face was about
   a third of the width.
2. **Fix 2:** flat level brows and a straight mouth (`blank`, my stunned stare), the face light down (p95 0.79), and
   28 mm (the face at 42%). Less cute, but a deadpan meme or a doll with button eyes.
3. **Fix 3:** the key close under the chin, so it falls off up the face, colder rims, and a kick on me. The gradient
   shows, but the chin's edge clipped, and the rims hit surfaces the low lens can't see.
4. **Fix 4:** the head dropped 6 degrees and the face light down. A little more menace, still a doll. All four fixes
   are in and it isn't frightening yet. Before version 5 I tested hand poses: a hand across the chest reads as a
   boxer's guard, a hand by the ear reads as a wave, and both near-arm reaches pull my mirrored arm toward hers. The
   far hand frozen at chest height reads most like a person.
5. That far-hand pose, rims at head height where the lens sees them, the hair in the face key, the worklight off the
   near arm, the bulbs at 75%, heavier fog and f/1.6. Eerie, not cute, but the lit hair turned into a pink hat.
6. The hair out of the key, the key moved right and closer for a diagonal fall-off, a cold edge on the far cheek, the
   bulbs at 45%, and the head turned 10 degrees toward me. The first one that unsettles, but the body went black and her
   yellow was gone.
7. The floor bounce back as the body fill, a hair light of its own, and the worklight on the far arm and the coat's
   front. The yellow is back. About 5 out of 10, but the key is too warm and the near arm is a flat plank.
8. A colder, tighter key, the near arm pulled back, the bulbs at 35%, f/1.3 and more rain. A regression: the left eye
   was lost in shadow and the plank got wider.
9. From version 7: the lens down to 1.32 m, the head down 8 degrees, 30 mm, and the bounce moved to her front side. The
   best so far: she looms and the face hangs over a black body. The bulbs are busy and I'm out of frame.
10. Me back in frame at the edge (phi 30, the kick on my shoulder) and f/1.0. A regression: my body covers her coat's
    front and her far hand.
11. Back to phi 34, the bulbs at 25%, fog 0.1, and a wider rim on her near shoulder. The silhouette holds.
12. The key very small and close under the chin, 32 mm (47%) and a 0.5 vignette. A bright chin and a dim brow band
    with the eyes in it. The moodiest, if a little "torch under the chin".
13. The near hand lifted 25 degrees. Worse: a beam toward the lens, the README's warning case. Dropped.
14. The rim narrowed to the head and the head dead on the lens. The body turns 8 degrees with it, so the coat's front
    and centred zip show. Clearly Tasha, and more confrontational, but her left eye is on darker skin.
15. The key re-centred under the chin. Both eyes sit on lit skin.
16. The hard fringe on and the zip ending under the collar. The same read, and the fringe flip shows close up.
17. The bulbs at 12% and the key down 10%. **Final.** After the AgX curve, 25% to 45% bulbs all landed near white, and
    12% is the first level where the face, not the marquee, leads the frame. I re-rendered it from the code as it
    stands and it came out bit-identical.

### The replay test (`review/replay-test.png`)

All three runs are 3 s at 270 x 480 on every frame with 6 samples, through `bl_story` and `post.finish`.
- **The shot:** one held side-on mid shot. The coat is about a tenth of the frame, well under a quarter. Rain and the
  scare's lights are on. There's no caption, because P01 is a pause beat.
- **The beats:** 0.4 s frozen, then the 2 s catch-up, then the stop.
- **Pass 1, the brief's spec:** a key every 0.25 s, each snapping in 0.05 s (one in-between frame). **It reads silly, a
  robot dance.** Hands over the face on R6 arms means arms at 124 to 128 degrees, so from the side one yellow beam
  covers her head for 1.25 s. The breaths rock at an even 4 Hz, like a beat, and the step is a lunge.
- **Pass 2, the generator's way:** my own 8 s behind the tarp, compressed 4x, so the timing is irregular. Each move
  takes 0.08 s, fast but visible, not a teleport.
  - The moves are human-sized: the head bowed into the hands at chin height, breaths as small heaves of lean, head and a
    2 cm rise, a violent 6-degree shiver and a short step.
  - **It reads silly as well, as zombie arms.** Bowing into the hands at chin height puts the arms straight out at
    shoulder height, held for 1.4 s. The shiver barely reads.
  - The one beat that reads as a person moving wrong is the last snap of the head onto the lens.
- **Why both fail:** R6 arms have no elbows. Seen from the side, "hands over the face" can only be a beam over the head
  or arms straight out.
- **So I used the brief's fallback (ruling 2):** only the last two poses, at normal speed. She's frozen with her far hand
  half up near the chin. It lowers over 0.65 s, she takes one short step (0.3 s), and her head comes round onto the lens
  (0.45 s blends) and holds. It reads calm and wrong, not silly. The scare becomes the stop and the eyes.
- **For the scriptwriter and producer:**
  - With the fallback, L52 ("She did / EVERYTHING / I'd done / back THERE, / in two SECONDS.") isn't true any more, and
    P01's note describes the full replay. Both need changing, and P01 can probably shrink from 2.3 s to about 1.8 s.
  - The generator no longer needs to compress my keys 4x for this beat.
  - An option I didn't render, because the brief says fallback after two silly passes: a 4x replay with no arm raise (the
    shiver, hunched breaths, the step, the head snap). It would keep most of L52 except the hands.
- **Flashing:** not measured yet. The fallback is slow, so the replay's flash risk drops a lot. It still gets measured
  at `step: 1` in the build.

### Engine additions (shared files, all opt-in, defaults unchanged)

| File | Option | Default unchanged, checked how | Test |
|---|---|---|---|
| `faces.py` | eye style `mirror` (`EYES`, `MIRROR_BLACK`). `face_key` puts `mirror` in the key, so a cached round-eye texture is never reused | Every existing eye style, plus six variants (bags, cheeks, freckles, glows, the line mouth, no brows), across all 13 expressions in 3 states: 1092 textures and keys, hash-identical before and after | `test_mirror_eyes_keep_the_round_outline_and_brows_but_have_no_white_pupil_or_glint` |
| `rig.py` | hat `bucket`: a crown and a brim sloping down all round, with new helpers `soften()` and `brim_mesh()`. Under a bucket only, the block hair has no top cap and its back and sides stop under the brim, so no corner pokes through | All 12 existing cast members (ep11 to ep13) built in Blender in two poses: identical object names, world matrices, mesh sizes, materials and modifiers before and after | `test_the_rig_defaults_build_no_new_parts`, `test_the_bucket_hat_has_a_crown_and_a_brim_sloping_down_all_round` (also checks no brim face points inward) |
| `rig.py` | extras `coat` (two skirt panels hinged at the hips that swing with their own legs, plus a zip, colour `zip_c`) and `hooddown` | as above. `Character.coat` is an empty list without a coat, so `pose()` does nothing new | `test_the_coat_swings_with_its_legs_and_the_hood_lies_down` |
| `rig.py` | `"fringe": "hard"` on a swoop: a third lock, `fringe3` | as above | same test (and none on other hair) |

- **How the rig tests run:** with a stand-in `bpy` that records every part, so they need no Blender. The stand-in
  modules are removed afterwards.
- **Results:** `python -m pytest -q reels/blocky` gives 41 passed, 5 of them new.
- **Not changed:** `kit.py`, `bl_story.py`, `acting.py`, `timeline.py`, `post.py`, `sound.py`, `checks.py`.
- **Story-local, in `set.py`:** the copy, the matte eyes, the shot looks with light linking (`light_only`, and `"me.*"`
  for every mesh of a character), the shadowless `face` and `hair` lights, depth of field per shot, and the `stride`
  key.

### My honest read

At phone size the copy is the wrong one in well under a second: two holes where Tasha has white eyes with a glint. It
reads eerie and wrong rather than cute, sleepy or "sunglasses". It's her own yellow mac and plum hair, soaked, lit from
below in the dark, staring dead into the lens from under a dropped head.

There's still a faint mannequin quality in the flat painted face. As a still I'd put it at about 6 out of 10 for
fright: more unsettling than frightening on its own. It will need the hole, the sting and the cut to land as a scare. I
don't think this calls for the brief's retry yet, but the critic's cold read should decide. If the critic reads "doll",
the next lever I'd try is a bigger face, about half the frame width, with the body cropped at the chest.

### Open items and deviations

- **My shoulder and hat brim in the foreground:** not in the final. Only a dark sliver of my arm reaches the right
  edge. I stand on the side the copy faces, so anything of me in frame covers her coat's front and far hand. Version
  10 shows what that costs. If scale matters there, an over-the-shoulder shot just before the stop can carry it.
- **Tasha's glint:** the brief wants her glint to be the brightest point on her face. In this shared light her chin's
  edge is brighter, which is fair for the side-by-side, but it needs handling in her own shots.
- **The fringe flip:** at phone size in this dark frame it's a quiet second tell. The plant itself (L01 against L22)
  needs the rimmed framing the script already asks for.
- **From the cast table, not built yet:** my black boots with white soles (the rig has one shoe colour) and Tasha's
  tall wellies (the shoe is a block at the foot). Neither shows in this frame.
- **The face light:** it's a cheat (linked to the heads, no shadow). The build reproduces it through `light_only`.
- **Version control:** background WIP checkpoint commits (as evanlin23) picked up my changes during this round. I
  didn't commit anything myself.

### Pass 2 (the critic's cold read)

**What the critic saw.** The cold read gave fright 4/10 and silly risk 6/10.
- It took about a second to pick the copy, and only by comparison.
- Alone at 360 px wide, it read as an ordinary blocky character with a deadpan default-toy face.
- The solid black eyes read as painted dots, not holes.
- The bulb dots overhead echoed the eyes and said "carnival".
- The black near-arm block read as a box she was holding.

**What changed, all in one frame.** Each item says which change it was.
1. **The mouth (the critic's change 1).** The copy copies my gasp, late: `neutral` (flat level brows, the eyes at
   Tasha's own neutral size) with a mouth key open at 0.67.
   - Drawn normally, at this size the mouth's ink outline is as thick as the oval is tall, so it was a plum ink oval on
     both of them (versions p2a, p2b).
   - The new `faces.py` option `mouth_inside` draws an open mouth as a hole of one colour to its edge, with no lip line.
     It's exactly the normal mouth's size. `copy_spec()` sets it to the eyes' black `#07070a`, which puts it inside the
     matte mask too.
   - The real Tasha keeps her own mouth.
2. **The framing (the critic's change 2).**
   - **The shot:** 40 mm at 2.0 m. The lens is at 1.45 m, aimed at 1.41 m.
   - **The head:** 72% of the frame width, with the eye line 34% down.
   - **Below the face:** at 9:16 a head that wide leaves about 45% of the frame under the chin, so the frame can't
     literally stop at the collar. That part is dark coat, with the lit yellow front and zip as the only colour.
   - **The background:** the lens is turned round 19 degrees (`cam_az` -42, from -23), so the arch and its bulbs are out
     of frame and the background is the dark field in the rain. The copy's body and head turn with it, so its pose
     relative to the lens is unchanged.
   - **The lights:** they move with the lens (`rel_looks` in the scratch `versions.py`). Bulbs are at 0.06, but none
     are in shot.
3. **The sockets (your depth suggestion).** The copy's eyes, and its mouth while open, are real holes in its head.
   - **The cut:** each is cut along the outline `faces.py` draws, using its own numbers, extruded radially into the
     head, so the outline on the curved head is exact and never bigger than Tasha's eyes.
   - **Inside:** the walls are matte skin and the floor is a matte void 0.45 R deep. The light from below catches a thin
     lit lip on the walls, and that's what makes them read as depth rather than paint. Because the head is pitched
     down and the lens is a little above the sockets' axis, the lip shows along the bottom inside edge. A lower lens
     puts it at the top (p2e), but there her shoulder rises over her chin.
   - **How it's built:**
     - The copy's head is swapped for a finely sampled version of `rig.head_mesh`'s own surface and UVs.
     - Each face state is cut once by an exact boolean, given sharp rims and kept as a plain mesh that swaps in. A head
       never deforms, so this works.
     - A blink, closed eyes or the angry lid put the uncut head back, so the drawn lids show. I checked open, blink and
       mouth-shut states front-on.
   - **Dead ends on the way:** a live boolean on a subdivided head took 252 s for one 270 x 480 frame. Cutting the
     stock coarse head left long smeared shading streaks. Simple subdivision left the 48 facets showing as bands.
   - **Cost:** the final renders at 17 s a frame at 540 x 960, the same as before.
   - **Only the copy changes:** Tasha's head and the rig are untouched. A story can switch the sockets off with
     `"sockets": false`.

**The pass 2 versions:**
- **p2a:** the mouth open and the tight frame. The mouth was an ink oval, and the shoulder block and blurred bulb discs
  were still there.
- **p2b:** a black inside for the mouth, which didn't show, and the lens up to 1.45 m.
- **p2c:** the mouth as a hole, and the lens turned off the arch, so no bulbs. Three black holes, but they still read as
  a shocked toy face (":O"), painted on.
- **p2d:** the sockets. Holes, not paint.
- **p2e:** a lower lens, 1.22 m. Her shoulder rises over her chin and the bulbs creep back. Dropped.
- **p2f:** the eyes onto the upper third and the face key up 20%. The bottom edge of the chin clipped in red on 2,029
  pixels.
- **p2g:** the key eased back from the chin. **Final.**

**The final frame (p2g), measured on the finish without the caption:**
- The head is 72% of the frame width, and the eye line sits 34% down.
- Skin luma is 0.33 at p50 and 0.74 at p99, with the brightest channel at 0.918. No pixel clips in any channel in the
  face rows.
- The coat is 0.46 at p99.
- The eye holes are pure black (0.000), the darkest thing near the face.
- The caption is clear of the face and passes `layout_problems`.
- **The copy:** yaw 33, local `head [75, 8]`, `arms [62, 6]`, `side [-6, 0]`, `expr "neutral"`, mouth 0.67. Its blink
  is held for the still.
- **The lens:** (-0.34, 2.81, 1.45), aimed at (1.0, 4.3, 1.41), 40 mm, focus 2.0 m at f/1.0.
- **The lights:**
  - face: 5.2 W, size 0.1, at (0.732, 4.003, 1.14).
  - hair: 4.5 W at (0.656, 3.843, 0.9).
  - rim: 1700 W, cone 9, at (2.977, 4.673, 2.0).
  - rim2: 900 W, cone 16, at (1.469, 6.3, 2.1).
  - bounce: 6 W at (0.481, 4.337, 0.07).
  - work: 300 W aimed at (1.3, 4.05, 1.0).
  - Gains: wash 0.5, inside 0.6, bulbs 0.06.
  - The rims sit on the opposite sides from version 17. My helper had screen left and right swapped. The frame was
    judged as rendered, so these are the real positions.

**Shared-file change in pass 2:** `faces.py` gets the face option `mouth_inside`. It's opt-in: I re-checked after the
change, and all 1092 existing textures and keys are identical. The test is
`test_mouth_inside_draws_an_open_mouth_as_a_hole_of_that_colour`. `python -m pytest -q reels/blocky studio`: 85
passed. Everything else in pass 2 is story-local in `set.py`: `dense_head_mesh`, `cutter_mesh`, `socket_shapes`,
`holed_mesh`, `update_sockets`, the `sockets` key, and the copy's face textures now kept in Blender's own temp folder
instead of piling up in `/tmp`.

**My read of pass 2.** Alone at phone size (`creature-alone.png` at 360 px wide), it no longer reads as a toy face with
painted dots. It reads as Tasha's face turned into a mask with three holes in it, lit from below in the rain, with
darkness behind the eyes. That's the README's "face opening onto darkness" and L54's window at night. I'd put it at
about 6 to 7 out of 10 for fright, up from about 6 for version 17, with the silly risk down to about 3 to 4.
- **What's left:** the head is still an R6 cylinder, and at full size the socket edges show small notches where the
  walls' facets catch the light.
- **If the critic still reads "toy":** I'd next try the head pitched further down, so the lit lip sits deeper, and a
  slower push-in on the shot in the film. Both are cheap.
- **For the build:** each expression and mouth opening the copy uses gets cut once (a fraction of a second each), and
  the copy's mouthed words in section 03 will open and close the mouth hole with them.

### Pass 2b (a fresh cold read of p2g)

**What the critic saw.** Fright 5/10 and silly risk 5/10. The sockets and the 72% framing were real gains. But at
360 px the open round mouth under level brows made a startled ":O", so it read as eerie first and then funny. Their
mock, with the mouth painted over, read as staring.

**p2h: the mouth closed, nothing else.**
- The copy wears `blank` instead of `neutral` and the mouth key is gone. That gives a short, thin, straight closed
  line, which is the brief's stunned stare. My own face in that shot is the same stare, so it's still copying me, late.
- The brows were already flat and level, because `neutral` doesn't raise them. `blank` keeps them at the same height
  with no tilt, so they're not angry either.
- With the mouth shut, the mouth socket isn't cut. The two eye sockets stay.
- I compared the two story files: apart from the copy's expression and the missing mouth key, p2h is p2g exactly.

**p2i: p2h with the brow in shadow.** The only change is the face key from below.
- It's now a 0.3 m square at (0.819, 4.099, 1.22), 0.27 m out from the face and just under the chin, aimed at
  (1.0, 4.3, 1.45), 3.6 W, linked to the heads only and casting no shadow as before.
- It falls off fast up the face, so the brow and the sockets sink into shadow while the chin and cheeks keep the light.
- A first try with a 0.08 m key at 2.5 W (`p2i-a` in the scratchpad) darkened the sides of the face as well. Cheek
  sides fell to 0.11 and the holes started merging into the dark upper face, so I widened it.

**Measured** (the copy's frame, finish without the caption). Luma down the face's centre column, with the cheek sides
in brackets:

| | brow | eye line | cheek | chin | brow/chin |
|---|---|---|---|---|---|
| p2g | 0.064 (0.158) | 0.38 | 0.47 (0.31) | 0.66 (0.45) | 0.097 |
| p2h | 0.064 (0.158) | 0.38 | 0.47 (0.31) | 0.66 (0.45) | 0.097 |
| p2i | 0.035 (0.070) | 0.26 | 0.36 (0.23) | 0.59 (0.41) | 0.060 |

- Both versions keep the head at 72% of the frame width, with the eye line 33% down.
- No pixel clips in any channel in the face rows. The brightest channel is 0.918 in p2h and 0.804 in p2i.
- The coat is 0.46 at p99.
- The eye holes are pure black in both (a median of 0.000). They're the darkest thing near the face, on skin of 0.37
  in p2h and 0.26 in p2i.
- The caption passes `layout_problems`.

**I picked p2i.** It's close.
- **p2h's case:** the cleaner stare, and its holes have more contrast.
- **p2i's case:** the fall-off sculpts the face, so it stops reading as a flat painted toy, and the sockets really do
  sink into the shadowed brow. That's the window at night.
- **Why p2i:** at 360 px both read as staring, with no ":O". p2i reads colder and less like a figure.
- **The risk with p2i:** the face is darker overall, so the eye holes have a little less contrast. They still read at
  phone size.

**My read.** With the mouth shut, the funny turn is gone. The cold read is now a face staring through two holes. I'd
put p2i at about 7/10 for fright and 2 to 3 for silly risk, with p2h a little behind on fright. Nothing in the code
changed in this pass. Both are lighting and acting values in the scene, which the build carries into `story.json`.

### Pass 3: the face is late on its own head (brief amendment 2)

A third cold read of p2i gave fright 5 and silly risk 6, below the bar (6 and 7). At 360 px the sockets' only depth
cue is a lit edge about 1 px tall, which vanishes, so the still face reads as a doll or a mask. Pass 3 changes the
behaviour, not the look.

**How it works** (`set.py`, story-local, on the copy only):
- `face_slide()` puts a mapping node between the copy's head UVs and its face texture. The texture wraps the whole
  head, with skin everywhere outside the face, so the face can slide round the head with no seam to see.
- Every frame, `pose_copy()` works out where the head pointed `face_lag` seconds ago (default `LAG`, 0.395 s) and
  slides the face back to that angle. So when the head turns, the face stays behind and follows it round. Its timing
  is the head's own ease, delayed, which keeps it reading as lag, not as a texture glitch. While the head holds still,
  the face sits in its place.
- While the face is off its place, the sockets give way to the plain head. They're cut where the face sits at rest,
  and each re-cut would cost minutes. They come back when it settles, within 0.5 degrees.
  - **A small risk:** the switch at the end of the settle could show as a tiny change in the eye edges. I can't see
    it in the clip.
  - The critic thinks the sockets don't read at phone size anyway. If the cold read agrees, `"sockets": false` drops
    them and nothing else changes.
- `"face_lag": false` turns the behaviour off, so the producer's fallback design drops in without code changes.

**The test clip** (`review/creature-pass3.mp4`, 3.0 s at 540 x 960 on ones, 12 samples, finished with the grade and
rain, no caption and no sound):
- **The frame:** p2i's, with the head along the body (side-on) until 0.55 s.
- **The turn:** the head comes round onto the lens over 0.45 s, then holds from 1.0 s.
- **The face:** it arrives 0.395 s after the head, settling at about 1.4 s, then holds to 3.0 s.
- **Cost:** 13 to 15 s a frame.
- **The strip:** `review/creature-pass3-strip.png` has 12 frames: the hold, the head turning with the face staying
  behind (0.8 to 1.0 s), the face sliding round a head that's already on the lens (1.1 to 1.3 s), and the hold.

**The end frame** (`review/creature-alone.png`, finished with the L54 caption chunk):
- It's p2i settled, with a mean difference of 0.012 from p2i's still. That's the sample count (12 against 16).
- No pixel clips in the face rows, and the brightest channel is 0.79.
- The eye holes are pure black, on skin of 0.26.
- p2i's still stays as `review/creature-alone-p2i.png`.

**My read:**
- The head arrives and the face isn't there yet. For about 0.4 s a blank skin front stares at the lens, then the eyes
  slide in from the side and stop.
- At phone size it reads as wrong, a mask catching up with the head, not as a glitch, because it eases in rather than
  popping.
- That's a behaviour a still can't show and a doll doesn't do. I'd call it the strongest read yet. The critic's cold
  read decides.

**The truck catch-up test** (`review/truck-catchup.mp4` and `-strip.png`, 2.27 s at 540 x 960 on ones, 10 samples):
- **The set:** the new truck in `set.py` (`build_truck`): a flatbed with no badge, plate or lettering, a stack of steel
  frames and panes held down with two straps, and panes in a rack. No boxes, tape or cardboard.
- **The shot:** the copy beside the truck's near side, three-quarters from behind, with the figure about half the
  frame height.
- **The motion:**
  - It holds frozen mid-step, one foot up (`stride` 24), until 0.55 s.
  - The frozen foot comes down by 0.75 s.
  - One dip and rise follows: a 30-degree bow at the hips with the head dropping, then straight back up, about 0.5 s
    in all, eased, with no hold at the bottom. That's my duck at about 3 to 4x.
  - Then it walks on at my pace, back in the lag.
- **The arms** hang at its sides the whole way. A new story-local acting key, `bow`, bends the torso at the hips and
  turns the arms back by the same angle, so they stay vertical. I checked their world direction straight down during
  the dip.
- **The coat** is 0.66 at p99 and 0.81 at its brightest, with no clipping.
- **Weaknesses:**
  - The ground under her is barely lit, so she can look as if she's floating in the dark. For the film shot I'd add a
    pool of light on the boards.
  - The bow is a hinge at the hips (R6 has no knees), so it reads as a bob more than a crouch.

### Scratch

Everything else is in `/tmp/claude-0/-home-user-content/536e21cc-1fd0-5adf-8cb3-ce3647d01d92/scratchpad/md14/`:
- `still.py` and `versions.py`: every version's recipe.
- `v1/` to `v17/`: each version's `pair.png`, `phone.png`, `view.png` and its raw frames.
- `p2a/` to `p2g/`: pass 2's versions.
- `p2h/`, `p2i-a/` and `p2i/`: pass 2b, with `profile.py` for the light down the face.
- `clip.py` with `pass3/` and `signtest/`, and `truck.py` with `truck/`: pass 3 and the truck test, every frame
  raw and finished.
- `sock/`: the front-on socket checks (open, blink, mouth shut).
- `replay.py` and `replay-pass1/`, `replay-pass2/`, `replay-fallback/`: the replay runs, each with a `clip.mp4`.
- `normals/`: the normals check.
- `fr1/` and `hat2/`: the fringe and bucket-hat look-devs.
- `rig-before.json` and `rig-after.json`: the rig dumps.
