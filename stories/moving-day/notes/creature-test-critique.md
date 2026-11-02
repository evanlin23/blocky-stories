---
role: critic
stage: creature test still (blocky step 3)
still: review/creature-test.png, review/creature-test-phone.png (the L48 frame, "over her BED,")
verdict: revise
score: 3/10 frightening at phone size
---

# ep17-moving-day: creature test still, cold read

## Gut read (written before I opened the brief, the script or the designer notes)

My eye went straight to the box head. It reads as a goofy cartoon face: two round spectacles, a black afro or beret on top, and one white buck tooth. It looks like a nerd or a beaver, not a gaping mouth. The body is a black silhouette with tan cardboard planks for limbs, so it reads as a kid in a cardboard robot costume, or a desk-lamp toy. Mum, on the left, is a tan box with a sleepy smiley drawn on it, the same brown as the cardboard. She reads as a pillow or a parcel, not a person. The bottom third is murky black. **It's silly, not frightening.**

## Score: 3/10 for frightening at phone size

The mood is right: a cold, dim room, a dark figure looming over a bed, legs that are too long. The face undoes all of it. The face is the focal point, and at 360 x 640 it reads as a friendly character. Mum doesn't read as a person, so there's no victim and no stakes. The designer's verdict ("frightening, not a costume") doesn't hold at phone size. The costume read the brief fears ("a kid's cardboard robot costume") is the first read here: one lit box head with a face, on a black body, with cardboard sleeves.

**Against the earlier passes:** v2 had the scariest face of the four: tall eyes, pupils off centre and a long vertical gape, drawn upright. The final improves the light, the palette and the model, but its face goes back toward v1's "surprised emoji" (round O eyes and an O mouth) and then hides it by turning it upside down. The fix is to combine v2's face with the final's room.

Measured on the 1080 x 1920 frame (HLS):
- **Mum's face:** hue 21, lightness 15%, saturation 34%.
- **The face box's shadowed side:** hue 27, 16%, 31%.
- **The forearms:** hue 24 to 31, 8 to 9%.

So in the render, Mum sits inside the cardboard's band. The nightlight pool between the legs (lightness 49%) is brighter than the lit face board (40%). The bottom 25% of the frame averages 2% lightness.

## Fixes, ranked by impact

### 1. Redraw `wide` and make it upright from the door (`marker.py`, `set.py`). This is most of the score.

**The upside-down hang doesn't read.** Nothing tells the viewer the head is inverted: the neck is black on black, so the box looks like a normal box. The brain reads inverted features as an upright face, so the wide black mouth on top becomes hair. The double-looped rings become spectacle frames. The tape strip between the eyes becomes a buck tooth. Turning it back upright (I rotated the crop) gives a plain shocked emoji, so the drawing is the problem as well as the hang.

- **Orientation.** In `set_face`, add a per-pose `flip` that rotates the front image 180° (key the cached file name on it, e.g. `boxes-wide-front-flip.png`). The drawing then reads upright from the door while the box itself still hangs inverted: the crushed-corner dent and the flap seam sit at the bottom. That keeps the hang as a detail you notice on a second look. Every appearance is a new drawing anyway, and a face drawn so it reads right on a box hanging upside down is creepier than one that doesn't.
- **The eyes (`marker.face("wide")`):**
  - Draw them with one lap, not `laps=2`. Two crossing loops read as glasses frames at phone size.
  - Make them taller than wide (`circle(..., squash≈1.35)`).
  - Make them unequal: one about 25% bigger and set higher, e.g. (0.29, 0.26, r 0.12) and (0.71, 0.22, r 0.15).
- **The pupils.**
  - Keep them small and solid (about 0.028), but slide them to the lower inner edge of each eye, toward Mum, as the camera sees it.
  - Centred pin pupils are googly eyes. Aimed pupils give the face intent and match the brief's "Aimed at: Mum".
- **The mouth.**
  - Make it a tall gape, not a wide oval: about 0.42 wide by 0.70 tall.
  - Its top should push up between the eyes (around y 0.40), and its bottom should run off the bottom edge of the box, so it's never closed. That's "opening onto darkness".
  - Tilt it 6 to 8° and set it a little off centre.
  - Give it a ragged edge: radius noise about 0.10 instead of 0.03 to 0.04, and `stroke(amp≈0.25)`.
  - A clean ellipse reads as a hole, a hairdo or an O-mouth emoji.
- **Take the tape off the drawn front.** The head's flap-seam band currently laps the front at both edges, which makes the tooth and the white "parting" above the mouth. In `build_boxes`, pass the head's `part(...)` tape axis as `"x"` instead of `"y"`, so its seam tape laps the two side faces and never the drawing. This also removes the hottest white spot next to the face.
- **Check:** `python marker.py <dir>`, then judge the sheet tile at 120 px wide, rotated exactly as the camera sees it. If it reads as a character with a personality, it isn't done.

### 2. Make Mum a person (`set.py` dressing and materials, `story.json` cast, framing). Without a victim there's no scare.

**The problem:** at phone size her head is a rounded tan rectangle with "( |" on it, turned 90°. It's the same hue and value as the cardboard. Her hair is invisible against the dark headboard and the grey pillow, her head is cut off by the left edge of the frame, and the "o" of "over" sits on her chin.

- **The pillow.** Change `M["pillow"]` from `#a3a4a8` (grey, which goes black at night) to a pale off-white around `#d6d3c9`, so her head and hair cut a silhouette against it.
- **The hair.** Lying on her back, her R6 `long` hair box disappears into the pillow. Add a flat fan of hair (`hair_c`, about 0.45 x 0.35 m, 2 cm thick) spread on the pillow on the camera side. Her silhouette has to be a head with hair, never a rectangle.
- **The light.** Add a soft fill linked only to Mum's head and near hand, from the window side so it's motivated. Aim for her face at 25% lightness or more while the cardboard in shadow stays under 15%.
- **The skin tone.** If the light alone doesn't separate her, move her skin off the cardboard ramp. `#c08a66` is hue 24°, and the board `TONES` are 29 to 30°. Use a rosier warm brown, e.g. `#a86a58` (about 13°). She stays warm brown, but she's now redder and darker than every box. The brief lets the designer change her look, but get the producer's OK since it's the cast table.
- **Framing.** Her whole head, hair and pillow should be inside the frame and clear of the caption band (about 0.62 to 0.70 of the height).
- **Her sleeping eyes.** They're ∩ arcs, the same shape as the creature's `smile` eyes, so she reads as content or happy. Use flat lid lines that droop a little at the outer ends (asleep, not smiling). This lives in the shared `faces.py`, so make it opt-in.

### 3. Kill the costume read: the head is the only box that reads as a box (`set.py` `build()`, `build_lights`, the hands).

**The problem:** the face box and the two forearms are the only lit boxes. Everything else is flat black, so it reads as a person in black wearing a box on their head and cardboard sleeves. The right forearm, lit full length, shows fibre streaks that read as a wooden plank, which makes it look like a marionette.

- **The forearms.** Remove `".fore"` from the `hands` list in `build()`, so the window lights only the flap hands. The forearms then get the same edge light as the rest of the body.
- **The edges.** Raise `window edge` (40 W, size 0.4) until every torso, leg, upper-arm and neck box shows a cold edge of 1 to 2 px at 360 x 640. The body has to read as a dozen separate boxes, not one black suit.
- **The joints.** Let the `joint_tape` strips inside the dark gaps catch a glint from the nightlight. A few tiny cold glints down a black body are the most "made of boxes, and wrong" detail you have, and right now none show.
- **The hands.**
  - The right hand's long curled flap reads as a thin black hook, which is note 18's "rods read as props".
  - Cut the second flap segment (`f2`) by about a third and splay all four flaps flatter onto the quilt's edge.
  - Let the window catch the flaps' paler inner faces, so each hand reads as an opened box end resting on the quilt.

### 4. Re-light the face and the frame's brightest spots (`build_lights`).

- **The face is lit evenly, like a sign,** and that's half of why it reads as a mask.
  - On the `nightlight kick` spot, change `spot=24, blend=0.8` to about 14° and blend 0.35.
  - Aim it at the eye line, so the bare board inside the eyes is the brightest thing on the creature. The box's edges and the bottom of the mouth should fall toward black.
  - That's the README's "the eye highlights should be the brightest thing", and it makes the face come out of the dark instead of being displayed.
- **The pool between the legs.** The nightlight's pool on the wall is the brightest broad area in the frame, so the eye drops from the face to the creature's crotch. Take the `nightlight` point from 80 W to about 45 to 50 W, or slide it until the near leg covers the hot spot. The face must outshine it.
- **The ceiling shadow** (the designer's open question). At phone size it doesn't read as part of the creature. It reads as a soft black smudge, like smoke or a render error.
  - It also swallows the neck chain, so "too tall, folded along the ceiling" (the whole point of the 15 boxes) doesn't read at all.
  - It falls leftward, away from the right-hand window, with a soft edge, so it's most likely the 1.0 m `window` area light rather than the nightlight. Check by toggling the window.
  - Shadow-link the Boxes out of the window light, using a blocker collection that excludes the body, so the ceiling behind the chain stays lit and N1 to N3 stand out against it.
  - Let only the nightlight cast a shadow, hard-edged (it's already `size=0.03`). That also plants L46's SQUARE SHADOW.

### 5. Recompose the dead lower third (camera, via `MOVING_DAY_CAM`).

- **The problem:** the bottom 30% averages 2% lightness. It's the unlit front of the bed, the navy slab of Mum's near arm and a murky purple drape. On a phone that's a third of the screen showing nothing, and the caption sits on it.
- **The camera.** Raise it from 1.0 m by about 0.2 to 0.3 m and tilt down a few degrees, keeping 18 mm so the figure still towers.
- **The lower third.** It should then show the quilt's top surface, raked by the window: plum, lilac and rose, the only strong colour in the house. The near flap hand rests on the quilt's edge. Leading up from the quilt, the arms carry the eye to the face. The bed's black front should drop out of the frame.
- **Check after reframing:** Mum must stay clear of the caption band and the left edge (fix 2). If raising the camera pushes her into the band, yaw left and move toward the foot of the bed instead.
- **The bigger issue:** this still is trying to be both L48 (the side-on silhouette wide) and L49 (the face from below), and it does neither job fully.
  - For L49 the face is too small: 0.29 of the width passes the 1/5 rule but isn't a scare close.
  - For L48 the silhouette is too cropped to read "too tall for the room" on its own.
  - The shot list already splits them, so judge this still as L48 and build L49 as its own close with the face at 0.45 of the width or more.

## Smaller notes (do these if they're cheap)

- **Scale.** The face box and Mum's head are about the same size on screen, which reads as two heads of one size, so the thing seems person-sized. After the fixes, check that the body around the face box makes it read as huge. If it doesn't, move the face box further over the middle of the bed so its size reads as real size rather than nearness.
- **The A-frame legs against the wall glow** are the best part of the silhouette, because they're plainly not a person's stance. Keep them, just dimmer (fix 4).
- **For the producer (continuity, not taste):** this L48 frame has the arms already down. Brief item 5 says the arms hang at its sides until L50, but item 2 says the pose never changes inside a scene. Those two can't both hold across L48 to L50. Bent over the bed like this, "hanging at its sides" points down at the bed anyway, so I'd rule that L48 to L61 share this one arms-down pose.
- **Mum's near-arm slab** reads as the bed's edge, not an arm. That's fine under the caption here, but the L54 close has to show her hand.

## What would make this a 7

Fixes 1 to 3 together. The bar: at 360 x 640, within a second, a viewer should see a face drawn wrong, aimed at a sleeping woman on a pale pillow, by something made of boxes that's folded under the ceiling. A viewer who sees a guy in glasses or a costume will scroll on. Re-render the still and send it back to me cold before the set build goes on.

## Re-read, pass 5

**Gut read (phone view, before the notes):**
- It's now a woman asleep in a bed: pale pillow, hair, blue top, quilt. That's a person and a victim at a glance.
- Above her, top right, a box-headed thing leans in. Its pupils look down at her, and that's the first thing on it that actually unsettles.
- The mouth lets it down. It's a grey, mottled, bell-shaped smudge under the eyes, and at phone size it reads as a goatee or a big nose as much as a gape.
- With the eyes looking down, the whole face reads as a worried "uh-oh" glance: an expression, so a character.
- The hands are thin black hooks, like bent wire.
- Uneasy, not scary.

**Score: 5/10 frightening at phone size** (pass 4: 3).

**Verdict: one more pass.** It's narrow: the face's mouth and the hands' silhouette only. Lock everything else as it is.
- **Lock:** the room, the light, Mum, the camera and the tape moved off the face.
- **What's fixed:**
  - Mum is a person: skin hue 8° rendered against the board's 24°, lightness 38%, framed by the pillow and hair, and her face is out of the caption.
  - The costume read is gone: there are no lit planks, and the body is a dark mass with cold edges.
  - The face is upright, single-loop, unequal, and its gaze is aimed at her.
  - The diagonal works: victim bottom left, the thing top right, an arm between them.

### (a) Must fix before the build starts

1. **Make the mouth a solid black maw, not a textured bell** (`marker.face("wide")`).
   - **The ink:** the gape renders at a median 7% and p90 12% lightness, mottled by the scribbled fill's board specks. The pupils and eye lines hit 0%. Texture plus grey reads as fur, which is the goatee.
     - Lay a solid polygon fill under the hatch passes, so the board shows only in a thin ragged rim at the outline.
     - Target: p90 under 5% on the rendered frame.
   - **The taper:** the narrow top that pushes up between the eyes, widening toward the bottom, is a beard's outline.
     - Invert it: widest across the top third, just under the eyes, at about 0.50 of the box width, then narrowing a little as it runs off the bottom edge.
     - Drop the spike between the eyes. Keep the 7° tilt and the ragged edge.
   - **The read:** a mouth bigger than a mouth should be is a maw, but a small one is an expression. The eyes are fine. Don't touch them.
   - **Check:** at 120 px, rotated as the camera sees it, it must not read as any emotion (worried, surprised or sad). It should read as a hole.
2. **Make the hands silhouette as open box ends, not wire** (the 3 a.m. pose, wrist roll in `pose_boxes`/`_reach`).
   - In shadow (the producer's ruling), the flaps are edge-on to the door, so each one is a 6 mm black line: a hook or a coat hanger. That's note 18's "thin black rods read as props", and on the reach beat itself.
   - Roll each wrist about 35–50° so at least two flaps of each hand face the door broadside. The silhouette is then a splayed box end, a few dark trapezoids, at the quilt's edge.
   - Re-run the probe after the roll (the near hand is 0.19 m from her).

Re-render the same still and send it to me. If those two land, this is a 7, and the build starts on it.

### (b) Polish to fold into the build

- **Mum's near arm:** a 0.34 m slate-blue slab, the biggest single shape mid-frame, reading as a bolster. In the wides, let it fall a stop darker than her face. In the L54 close, frame it as an arm ending in its hand.
- **The lower third:** about 3–5% lightness. The bottom left is black (the bed front and floor) and the bottom right is dim quilt. It mostly sits under the YouTube controls, so it's acceptable. In the build, let the cold rake carry the quilt drape further across the bottom, or frame the black out per shot.
- **The L48 wide has to show "too tall for the room":**
  - Here the body runs off the top right, so we can't see where it meets the ceiling. It reads as big and leaning in, not as folded under the ceiling.
  - In the build's L48 (side-on, as the shot list has it), keep the ceiling line and the neck chain pressed along it in frame.
  - This still is judged as L48. L49, the face from below, is its own close with the face at 0.45 of the frame width or more.
- **The pillow:** at 44% lightness it ties the face board for the brightest large area. Take Mum's linked fill on the pillows down about 20%, so her face and the creature's eyes rank above it.
- **The joint-tape glints:** along the top they sit in a regular row of small grey squares, which reads as lit windows or studs. Break the spacing, or let a few of them go dark. Don't add rim light to make them read (the designer's right: that brings back the costume).
- **Mum's sleeping face:** turned 90°, "|| |" reads as asleep now that the pillow and hair frame it. Leave it.

## Re-read, pass 6

**Gut read (phone view, before the notes):**
- The goatee is gone. Under the eyes there's now a black hole running off the bottom of the box.
- With the pupils sliding down at her, it reads as a thing gaping down at a sleeping woman. That's the scare the line describes.
- The hands are dark, splayed shapes on the quilt's edge. The near one reads as a claw, the far one as an open box end. Neither reads as wire.
- It's still top-heavy, and the body runs off the top right.
- This is the first pass that does something to my stomach.

**Score: 7/10 frightening at phone size** (pass 4: 3, pass 5: 5).

**Verdict: pass. The build starts on this model, face and light.**

Both must-fixes landed:
- The mouth's interior is a median 0.8% and p90 3.1% lightness, and it reads as a hole, not an emotion.
- Each hand silhouettes as a few trapezoids. Probe: 0 contacts, 0.66 m of air under the face box.

### (b) Last polish for the build

- **The mouth's top edge.** It runs nearly straight across under the eyes. At phone size that's fine, but in the L49 close (face at 0.45 of the width or more) a flat-topped black block can read as a full beard. Before drawing L49, give the top edge the same ragged wobble as its sides, plus a slight upward bulge in the middle. Keep the eyes untouched.
- **Keep the hands as they are.** The claw-like near hand is a gift. In the L50 side-on shot and after the lamp (L51 on), re-check that the broadside flaps still read as box ends in light, not just in silhouette.
- **The pass 5 (b) list stands as the designer logged it:**
  - Mum's near arm a stop darker than her face in the wides, and the L54 close framing it as an arm with a hand.
  - The quilt rake carried further across the bottom, or the black framed out per shot.
  - The L48 side-on wide showing the ceiling line with the neck chain pressed along it. This is the one that matters most: it's the "too tall for the room" read, and this still doesn't carry it.
  - The pillow fill down about 20%.
  - The tape-glint spacing broken up, with no extra rim light.
  - Mum's sleeping face left as it is.
