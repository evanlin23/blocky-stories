# ep15-mirror-maze: brief (redo, writer, 2026-11-02)

**This redo outranks everything below it.** The story was held because its first line wasn't the world's rule. The new script (`script.md`) keeps the set, the cast and the look, and changes the premise and twist. Big idea: the narrator is the reflection someone left in a maze pane before moving away, and Tasha has come every night of the fair to visit a reflection. About 1:22, 43 lines, about 46 shots.

## What stays (reuse as built)
- **The set:** the rainy field, duckboards and puddles, the flatbed truck with its glass panels, the fry van with its steel side, the maze front with its lilac bulbs, the inside grid with the roof off and the rain, the far tarps and wheel, the worklight. Grade, fog and rain settings.
- **The cast specs:** `me`, `tasha` and `guy`, unchanged. The bucket hat, the coat, the wet coat for Tasha.
- **The machinery:** `build_ghosts` / `pose_ghosts` (instanced figures in the glass) now place the leftovers. `copy_spec` (Tasha mirrored) now makes **Tasha's reflection** at L39 to L43, with **normal round eyes and glint**, no sockets, no lag. The `mirror` eye style and `matte_eyes` now go on the dark one. The maze guy's pane-carry shot (old L81) and the find-through-the-glass framing (old L68 to L78, roles swapped: Tasha outside, me inside).
- **Music:** dorian E2 at 76 bpm with the piano's late echo. Sections move (see script.md → Look and sound).

## What's dropped
The copy's half-beat lag, the walk out, the truck duck and catch-up, the bumper-car hide, the P01 replay, the black-eyed Tasha, the fry-van warm ending, and the five-stroke facade tally (`maze.tally0` to `maze.tally4`, delete them: no lore plant this time). The bumper cars aren't needed; leave them as background or skip them.

## What's new (build these)
1. **The leftover marker:** a thin emissive lilac outline (about `#c9a6ff`, an inverted-hull shell or rim pass) on every leftover reflection, plus a slight desaturation. It must read at phone size by 2 s. Our own design, not a game highlight effect.
2. **Leftover extras:** about six to eight simple adult stranger specs (varied coats, hats, hair, no catalogue look), placed in glass:
   - the maze front's panes at L01 (a crowd standing where nobody stands)
   - the fry van's steel side at L02 (a long queue; build it like the maze, clear panel with the figures behind it), and two real customers at the hatch at L03
   - one man tying his boot under a puddle on the boards at L04 and L05 (an upside-down figure under a clear puddle plane), with nobody above it
   - the truck's glass panels at L06, waving
   - the carried panes at L14 to L17, faces turning to watch me
3. **Me behind the glass:** every shot of me has a pane between me and the camera or between me and Tasha. My side is dry: no rain on me or near me (split the rain so it falls on her side only). I carry the same lilac rim, kept subtle and always backed by the bulbs, so it reads as their light on a first watch.
4. **Her breath fog:** an animated soft fog patch on her side of the pane at L18. My side stays clear at L19.
5. **The dark one (the creature):** one old leftover stranger in faded grey-violet, a head too tall for its pane (about 1.25x height), mirror-black eyes with no shine (`mirror` style), a flat mouth, a dull grey rim (about `#7a7484`). One model, posed per shot, never seen moving, only a pane nearer between cuts. **Test still first:** the L24/L25 frame, its face at least 1/3 of the frame width behind my shoulder in my pane, key from below, front lights dead, rim on its silhouette, eyes the darkest thing near its face. Bar: fright 6 and silly risk 7 on a cold phone-size read.
6. **The tilt (L28 and P02):** my side of the pane (floor patch, frames behind me, me) tips about 25 degrees over 0.6 s as the maze guy lifts the pane. Then from her side: Tasha level in the rain, me tilted inside the carried pane. Parent my side to the pane frame, or roll the camera on an inside shot and cut. Ease it, no snap.
7. **Tasha looks at herself (L36 to L39):** she turns her face to the glass, and her reflection (the mirrored model, normal eyes, lilac rim) appears beside me. She walks back into the rain. It stays.
8. **The last two shots (L42 and L43):** the pane on the truck from outside, me and her reflection in it, the real Tasha small on the duckboards waving. Then a slow push into the pane: deep behind us, the dark one, small, clearly lit, a pane nearer. Cut 0.25 s after the last word.

9. **story.json:** set `title`, `premise`, `twist` and `world` from script.md → Premise, rule, twist and package.json, and replace `lines`, `shots`, `cues` and `music` sections for the new 43 lines.

## The 2 s hook, lit to read
The first frame is the maze front lit bright: the bulbs plus a soft warm front fill on Tasha (face at least 1/4 of the frame width, out of the caption band), the leftover crowd in the panes behind her with their lilac rims clean against the dark glass. Light fog only. Darkness and heavy fog come after 0:15.

## Cut rate and timing
About 46 shots, a new one every 1.2 to 2.3 s. Line start estimates are in script.md's shot plan. Cover (`cover_s` 44.5): the dark one right behind me in my glass, Tasha's face outside if it fits.

## Standards notes
- Nothing in the set has text. Coins, if shown, are plain discs.
- The dark one is a stranger, never shown hurting anyone, never touching anyone. "Nobody had come to see them in years" is the only sadness, and no death words.
- The real me "moved away", an ordinary reason. Every cast member is an adult.
- Flashing: the tilt and every light change ramp over at least 0.3 s. The lilac rims don't pulse.

---

## The old brief (2026-10-31), kept for the set and cast details only
Where it talks about the copy's lag, the replay, the truck catch-up, the bumper-car hide or the fry-van ending, it's superseded by the redo above.

# ep14-mirror-maze: brief (producer, 2026-10-31, amended the same day after the creature tests)

Creepy blocky story reel, batch 2 story 2 of 4 (row 2, `mirror-maze`, in `reels/blocky/batch2-pitches.md`), for **PandaNanoAdventures** (note 21). Format `/blocky`, note 18 in full. It's fiction with no facts and no sourcing step. There's no takeaway on purpose (notes 16 and 21), so there's no "where the viewer meets this" section either. Story folder: `reels/blocky/stories/mirror-maze/`. Working title: **"Only one of us walked out of the mirror maze"**. It's a statement, not an imperative, and the packager owns the upload title.

**The look is identical to ep11 to ep13:** the same R6 rig and drawn faces, the same narrator (voice A, `am_adam` 1.03 x 1.45), the same captions. Only the story changes. Every line is `who: narrator`, the cast's words are reported speech, and it runs 2:15 to 2:30 (about 580 to 630 words, never over 3:00).

## Amended after the creature tests (producer, 2026-10-31)

Three things happened after this brief was written: the replay test, the first two creature passes (`designer-notes.md` → "Creature test"), and new engine options. These rulings outrank the sections below, which are edited to match.

1. **The replay uses the fallback (ruling 2).** Both replay passes read silly. R6 arms have no elbows, so from the side "hands over the face" can only be a beam over the head (pass 1) or zombie arms (pass 2), and pass 1's even 4 Hz snaps read as a robot dance. The final P01 (1.8 s, silent, one held side-on shot) is the fallback: frozen about 0.4 s, the far hand comes down at a person's pace (about 0.65 s), one short step (about 0.3 s), then the head comes round onto the lens (about 0.45 s). Nothing snaps. The scriptwriter rewrote L52 to match (`She didn't / HURRY / this time. / Hand DOWN, / like I DID. / ONE STEP.`). The generator no longer compresses my keys for this beat.
   - **Which beat is fast now: only the truck.** L40 to L42 ("did my DUCK, way too FAST") stays a fast catch-up, and L52's "didn't HURRY this time" answers it. The scare is calm and wrong. Its hit is the stop and the eyes.
   - **The truck catch-up, so it doesn't read silly.** It's one move: the frozen foot goes down, then my duck and stand as a single dip and rise at about 3 to 4x my own speed (about 0.5 s in all), then it drops back into the lag.
     - **Never an arm raise.** The arms hang at its sides all the way through, with the walk's own swing at most. No hand to the head, no reach and no arms out, because block arms with no elbows read as beams.
     - It's eased. No near-zero snaps, no string of poses on an even beat, and no hold at the bottom of the dip. The script's L40 bracket ("snapping pose to pose") is superseded by this.
     - It's shot side-on or three-quarter from behind, with the figure at least 1/3 of the frame height, so the drop of the head and shoulders is the read. The coat skirts follow the legs and never flick up.
     - **It's tested before the build:** a 2 s run at `step: 1`, which the critic reads cold at phone size. It must read as a person moving wrong, not a dance, a robot or a glitch.
     - **If it reads silly,** first cut away on the dip to my face on "way too FAST", and come back to it already in the lag. If that still reads silly, play it at a person's pace too, and the scriptwriter changes L40, L41 and L52's "this time" together (the script header plans for this). That's not a kill.
   - **My own hands over my face at L46** have the same beam problem. Frame that shot close on my face, with the hands at the ends of the sleeves and never the arm's full length side-on (README).
   - **The gap: the fallback keeps it.** The one step goes sideways along the glass plane (about 0.2 m in the test), never toward me. So the centre-to-centre gap stays about 1.5 m or more on every frame from P01 to L55, and the copy ends no closer than it began. Standards' contact probe measures that gap as well as contact.
2. **The creature test, and how it counts against the kill criterion.**
   - **Pass 1 (v17):** a cold critic read gave fright 4/10 and silly risk 6/10 (10 = not silly). The painted black dots read as a default toy face.
   - **Pass 2 (p2g):** real eye sockets cut along Tasha's eye outline (on the copy only), a frame where the head is 72% of the frame width with no bulbs in it, and an open gasp mouth drawn as a hole. A fresh critic gave fright 5/10 and silly risk 5/10: eerie, but the ":O" read as startled, then funny.
   - **Pass 2b (rendering now):** the mouth only, a closed flat line (fix 2's "stunned stare"), plus a forehead-shadow variant.
   - **Ruling: 2b is part of pass 2, not a third pass.** It keeps pass 2's design (the sockets, the frame and the light) and changes one thing that's already in the fix order. A fresh critic who has seen no earlier version reads both variants cold and names the better one. That read is pass 2's verdict.
   - **The bar, on a cold read at phone size:** silly risk 7 or better, and fright 6 or better on the still, on both the pair and `creature-alone`. Fright is set one below the 7 asked for because the still has none of the things the scare is built on: the hole, the sting, the slow head turn and the cut. **Fright 7 is then required on the preview** (round 1's critic row "Creature: scary"). Missing it there is a revise, not a pass. Silly risk doesn't drop, because silly is the owner's note 18 failure.
   - **If 2b misses the bar,** pass 2 has failed. That's the `craft` stop on this creature design, but not a kill of ep14. The story, script and set stand, and nothing has gone to review. The row's retry runs inside ep14 as **creature pass 3**, with the same bar:
     - **The redesign: its face is late on its own head.** The copy's face trails its head's turn by the lag (0.395 s). When the head comes round onto the lens at the end of P01, the face gets there after it, sliding round the head and settling. It's the film's own rule turned on its own body, it's human-shaped, and a still can't fake it. This applies to every head turn the copy makes, but before the scare its face is never seen from the front, so P01 is the first time it reads.
     - Keep the mirror-black eyes at Tasha's size (so L54 and L55 stand) and the flat-line mouth. Whether the sockets survive a moving face is the designer's call. Never pale grey, never rods, never bigger eyes.
     - **Its test is a 3 s clip** of P01's head turn plus the end still, read cold at phone size. It must not read as a texture glitch.
     - **If pass 3 misses,** the producer kills ep14 with `craft: the copy still read silly after three passes`. The retry note: a new wrongness for the row, carried by timing and staging rather than the face (for example the flipped face alone, with no shine, at Tasha's eye size, seen only in the glass), with a fresh brief.
3. **Engine additions now in the tree.** All are opt-in with defaults unchanged, and all are tested (`python -m pytest -q reels/blocky`: 42 passed on 2026-10-31).
   - **`faces.py`:**
     - the `mirror` eye style: a round eye's exact outline, filled near-black, with no white, pupil or glint, and the brows and mouth kept
     - `mouth_inside`: an open mouth drawn as a hole of one colour, the normal mouth's size
   - **`rig.py`:**
     - the `bucket` hat
     - the `coat` extra: skirt panels that swing with the legs, plus a zip
     - the `hooddown` extra
     - `"fringe": "hard"` on a swoop
   - **Story-local, in `set.py`:** the copy's sockets (real holes cut along the drawn outlines, switched off by `"sockets": false`), the matte eyes, and the `stride` key.
   - **For standards (the IP look):**
     - the bucket hat is our own shape, with no logo and no catalogue item or known character's hat
     - the satin coat, with its skirt panels and its hood down, reads as an adult's mac, never a child's yellow slicker (ruling 3)
     - the sockets read as a mask with holes, never a wound: no blood, no gore and no eyeball. The copy is still no known creature
   - **For the critic:**
     - Every read is cold, at phone size.
     - The sockets show small notches at full size, where the walls' facets catch the light. Judge those on the final.
     - The open-mouth hole comes back when the copy mouths words in section 03. Those shots are side-on or back-lit, so check on the preview that it never reads as ":O".
4. **Pass 3's verdict, pass 3b and the truck (producer, 2026-10-31, after the pass 3 and truck cold reads).** This outranks item 2's last bullet and the kill criteria's pass 3 line.
   - **Pass 3 missed:** fright 5 and silly risk 7, against a bar of 6 and 7. Silly passes for the first time. Fright missed because the clip never showed the design. The head started side-on with one eye on its edge, so a face sliding round a cylinder read the same as a head turning.
   - **Ruling: 3b is part of pass 3, not a fourth pass, and it's the last try.** Like 2b, it keeps the pass's design (the face late on its own head, the look, the light, the frame, the ease and the 1.7 s end hold) and changes one thing: the start pose, which is the cold critic's single change. The miss doesn't trigger the kill yet. I won't discount fright a second time for the missing sound, because the bar of 6 already allows for the hole, the sting and the silence.
   - **3b is staging only:**
     - The copy starts with its body about three-quarters away and its head 120 to 130 degrees off the lens, with the back of the hair to camera. The head lands on a smooth blank front, held about 0.3 to 0.4 s, then the eyes come over the edge and settle.
     - `face_lag` stays the film's lag (0.395 s). The blank hold comes from the bigger start angle, never from a longer lag.
     - The face, eyes, mouth, light and frame don't change. The sockets stay the designer's call (`"sockets": false` is fine). It's one render, and the clip may run past 3 s.
   - **It's not a turn too far, as long as the body turns too.** A head swinging 120 to 130 degrees on a still body is ep11's beat (see "What this story must not share"). It also breaks the copy rule, because the copy only makes moves I can make. So:
     - The body comes round on the one sideways step to p2i's end yaw, and the neck is never more than about 80 degrees off the body on any frame. The end pose's 75 is the most.
     - The start pose is the copy rule too: it froze copying me turning away to slip behind the tarp (L44), so I'm staged turning away from it there. The gap rule stands.
   - **The bar:** a fresh cold critic, using pass 3's method so the scores compare. It must reach fright 6 or better and silly risk 7 or better, and read as a face arriving, never as a texture glitch.
     - **On a pass:** build. The bar of fright 7 on the preview at round 1 stands, and missing it there is a revise.
     - **On a miss on either score:** I kill ep14 at once with `craft: the copy's face never reached the fright bar in three passes`. No build-and-see and no pass 4. **The retry note:** a new wrongness carried by timing, staging and the body, never by a drawn R6 face held to the lens, which read as a toy at phone size in every pass. Keep what worked: the soaked yellow figure, lit from below, calm and never hurried.
   - **If 3b passes, the scare's shots:** the face can't read at mid size, so its arrival plays in the close it was tested in. The side-on mid carries the freeze, the hand down, the step and the start of the turn. A cut on the action (or a push, the designer's call) goes into the close for the head and the face. The `hit` and `sting` land when the eyes settle. The scriptwriter retimes P01 and P02 at the build, and L52 and L53 stand.
   - **The truck: the cut-away is in** (item 1's first fallback, after a silly risk of 4: the bow folds the collar into a beak, and she floats).
     - Her foot comes down fast on screen, so the speed is seen. On the start of the dip, cut to my face for L40 and L41, then come back on L42 to her already walking in the lag. The dip is never on screen.
     - Her shots get lit boards under her and the truck's side in frame.
     - **L40 and L41 hold unchanged:** my face is the narrator seeing it, and the fast foot is the evidence. L52's "didn't HURRY this time" still answers it.
     - There's no new truck test, and it's judged on the preview. If it still reads silly there, item 1's second fallback applies. It's not a kill.

## The decisions in one place

| Question | Decision |
|---|---|
| Pitch | **B, "Out of sight"**, with three things from A and one from C (below) |
| Mirrored rig for the copy | **Yes.** It's Tasha's rig built from her spec and mirrored left to right. Exactly three things show the flip: her fringe, her lopsided smirk and her handedness. Nothing else on Tasha is one-sided, so nothing else flips |
| The two-second replay | **Replaced by the fallback (amended).** Both replay passes read silly, so the scare is calm: the hand down, one step, the head round. Only the truck's catch-up stays fast (amendment item 1) |
| Yellow raincoat and the IT (Georgie) echo | **Keep the yellow and soften the echo.** It's in the owner's row, and it's the read: one yellow figure you can find among a hundred reflections at phone size. The echo is handled by her cut, her hood and the set (see "Rulings") |
| The *Us* hall-of-mirrors swap | **Soften.** Keep the double in the glass. Ban its images, and ban its ending: nothing ever hints that the Tasha who comes out, or I, am the copy |
| Harm to Tasha | She's "still in there", never taken, hurt or in danger. In the glass her face is urgent, then grinning. The copy never touches anyone |
| Hands and knocks | Nobody holds hands and nobody is pulled out. The one touch is a light shoulder bump after she's out. There's **no knock anywhere** in the film, and nothing is pressed to the glass |
| Key colour | **Raincoat yellow `#ffd23a`**. Fallback: fry-van amber `#ffa040` |
| Score | Dorian on E2, 76 bpm. Drone, pad, piano and pulse, with **no choir and no music box**. Its signature is **the late echo**: copied notes come half a beat late, and the real ones land together |

## Chosen pitch: B, "Out of sight"

- **Only this creature could do this middle.** First she's late. Then she freezes mid-step when she can't see me, and at the truck she replays what she missed, at speed. Then, at the scare, she doesn't hurry: she comes calmly into my pose with black eyes. Each beat is bigger than the last, it's shown on screen in the light, and nothing in batch 1 or rows 1, 3 and 4 moves like it. The README's first story lesson is that the middle must escalate, and this one does.
- **The rule drives the ending, and nobody explains it.** The viewer sees the freeze twice before it's said. The find and the way out both use it. No elder knows anything, and nobody needs a hand to grip.
- **It has the fewest batch-1 echoes.** It has no knocks, no glass "from the inside", and the copy never says a word. A has two taps, a copied "pickle" and a face in a window. C has a rule-shaped opener, ep13's cascade and ep11's face-beside-mine.
- **Its loop is the joke starting again.** The last line is the first line's picture.

**Taken from A:**
1. The line "For once, I came out FIRST." Tasha always wins, so it sounds like a win, and it re-reads at the twist.
2. The fry van's warm strip light is the only warm light in the film, and the score turns to the major there.
3. The maze's bulbs go off in one slow fade, and the copy's pane goes dark with them.

The maze guy keeping his back to us is in both A and B.

**Taken from C:** the warm image. In the fry van's polished steel side, our two reflections look up at the rain at the same moment we do, and nobody's late.

**Declined:**
- A's booth-window scare and taps on glass (ep11, ep12).
- The copy saying "pickle" aloud (ep11's "In MY voice").
- C's fry patch. It's C's twist, and one spoken flip is enough.
- C's heads turning down the glass (ep13's cascade).
- C's "She PAID" ending. It doesn't fit B's joke.
- From the row: the bus stop (ep11's bus), the sign with words (text in the set), and "I grab that hand" (the rig can't grip, and "grab" is on `check`'s harm list).

**Hypotheses** (`studio/learnings.md`):
- **H12** (an uncanny human-shaped creature beats a non-human one). This is the most human creature yet: a friend's own rig, wrong only in its eyes, its timing and a flipped fringe. It sits next to ep13's non-human diamond.
- **H10** (a warm turn after the scare). This is the first warmth that's between two people, with the creature playing no part in it.
- **A narrow one for the analyst to log:** does a plant the viewer can check on screen (her fringe parted the wrong way, and her dark eyes in two mid shots) raise rewatches and comments that name the moment?

## Rulings on the open questions

1. **The mirrored rig: yes.** The copy is generated from Tasha's cast spec, never a hand-edited second spec, so any change to Tasha carries over. It's mirrored left to right as a whole.
   - **Flipped, and seen:** her swoop fringe sweeps to the other side. That's the plant, said once.
   - **Flipped, never said:** her default `smirk` lifts on the other side, because the face texture is mirrored. You only see it in close-ups.
   - **Mirror-handed:** it does what I do the way a reflection does. When I raise my right arm, it raises its left.
   - **Kept symmetric on purpose:** Tasha's coat has a centred zip and no patch, badge or one-sided pocket. Her boots and jeans are plain.
   - **Designer's check:** a negative scale flips normals. Check the mirrored mesh's normals and shading, and confirm the eyes still draw mirror-black after the face texture flips.
2. **The replay: the fallback is in (amended 2026-10-31).** The original plan was about 8 poses in 2 s, snapping, and it read silly in both test passes (amendment item 1). P01 is now 1.8 s: the hand comes down at a person's pace, she takes one short step sideways along the plane, and her head comes round onto the lens. Nothing snaps, and the scare is the stop and the eyes.
   - Render it at `step: 1`, and flash-measure it at that step.
   - The truck's catch-up is the one fast beat: one move at about 3 to 4x, never an arm raise, with its own 2 s test (amendment item 1).
3. **The yellow raincoat stays.** Changing a colour the owner approved needs a strong reason, and the Georgie echo can be removed without one.
   - **The coat:** an adult cut, long to mid-thigh, a satin sulphur yellow (about `#f0c419`), not a glossy lemon slicker.
   - **Her hood is always down,** so her adult hair and face lead every frame. That's also what makes the fringe readable.
   - **Boots and jeans:** black wellies and black jeans, never yellow boots.
   - **Scale:** she's my height and never small in frame.
   - **Never in the film:** storm drains, gutters, paper boats, sewers, balloons, clowns, and a child's-eye low angle on her alone in the rain.
   - It must also read apart from ep11's matte mustard knit hoodie (`#c8952a`). The coat is lighter, satin and cut as a coat.
4. ***Us* (2019): soften, don't change.** A double in a mirror is old folklore, and our place, cast, joke, rule and ending are our own.
   - **None of its images:** no boardwalk, beach or pier, no red jumpsuits, scissors, rabbits or gold gloves, no sign of any kind, no child in a hall of mirrors, no flashback.
   - **None of its ending:** no identity-swap sting, and no "or was it?" beat. The ending proves she's real three ways: the shine is back in her eyes, she starts the joke, and our reflections are on time in the van's steel.
   - The packager keeps the title and description off the film's name and off "doppelgänger".
5. **Harm.** Tasha is "still in there".
   - **In the glass:** her face is `worried`, then `wide`, then `grin`. Never `crying`, `terrified` or `squeeze`.
   - **What she does:** she waves both arms. She never pounds and never presses to the glass.
   - **The copy and her:** they never share a frame space and are never seen crossing.
   - **The panels:** nobody is near a falling panel, and no glass cracks or breaks.
   - **Words that stay out of every line:** lost, missing, trapped, taken, took, pulled, grab, scream, fell, locked, crack, shatter, shards, "dead end", "dead still". `check` blocks "dead" and "die" outright.
   - **Also out:** "since we were kids" or any child word. Say "since forever".
6. **Hands and knocks.**
   - The rig can't grip. So there's no held hand, no pulling and nobody holding a coin. My coins are already on the counter.
   - The one touch in the film is Tasha's light shoulder bump when she's out. It's staged side-on, and it's the only allowed contact in the contact probe.
   - There's no knock sound or tap anywhere, as in ep13.

## Story

- **Premise:** the last weekend of a travelling fair, in the rain, half packed up. Me and Tasha, best friends since forever, go into the mirror maze before it comes down. It's the only ride still lit. Tasha always wins at everything, especially at her joke.
- **First line (an inside joke, in the first 2 s):** Tasha points at anything green and goes, "what's THAT?" I say PICKLE, every time. Whoever says PICKLE buys the fries, so she yells FRIES and I pay. I've never once won.
  - It opens side-on on Tasha pointing at my green bucket hat under the maze's glow.
- **The rule (it's shown twice before it's said):** the copy stands where my reflection would be and does what I do, half a beat late. It can only copy what it can see. When it can't see me it freezes. When it sees me again it catches up: fast at the truck, and calm at the scare (amendment item 1).
- **Plants** (each one re-reads at the twist):
  1. **About 25 s:** a hundred Tashas in the glass all move, except one far down that stands still. "I figured it was the angles." That's her, the only thing in there not copying anyone. At the find she's in the same spot.
  2. **About 33 s:** "For once, I came out FIRST." Then she comes out, her hair parted on the other side. "I figured it was the wind."
  3. **About 45 s:** her boots don't splash. In the picture, my steps hit the puddles and hers make no sound. One short line says it.
  4. **About 50 s:** I try her own trick on her. I point at my hat and go, "what's that?" She points at her own head, at nothing green, and her mouth makes the words with no sound, half a beat late. She never says pickle and never yells fries.
  5. **Shown, never said:** her eyes. They're mirror-black in every shot, but before the scare her face is only seen side-on, from behind or back-lit. A sharp viewer can catch them in two mid shots in section 03.
- **Escalation:**
  1. She's late.
  2. **About 62 s, at the truck:** I duck behind the truck for a second. She's frozen mid-step with one foot up, rain running off her coat. She sees me, puts the foot down and does my duck and stand in one fast move (about 3 to 4x, arms at her sides, never raised), and she's half a beat behind me again.
  3. **The scare at the bumper cars.**
- **The scare (about 75 to 100 s):**
  1. I hide behind the bumper cars' tarp for a long time, shaking. I put my hands over my face and take three breaths.
  2. Cut to her out on the open ground in the rain, frozen with one hand half up.
  3. I step out. She's exactly where I left her. "Then she SAW me."
  4. Everything drops to silence. In one held side-on shot with no cuts and no sound at all, she doesn't hurry: her hand comes down at a person's pace, she takes one short step sideways, and her head comes round onto the lens (about 1.8 s, the fallback in ruling 2).
  5. She stops in my pose, facing me the way a reflection would, about 1.5 m away, and doesn't come closer. Her face is lit from below, and her eyes are black like a window at night, with no shine. That's the hit.
- **The twist:** `That's what / a REFLECTION does.` / `It can't MOVE / if it can't / SEE you.` / `It came out / of the GLASS.` / `Tasha was / still IN there.` From here the narration calls the copy "it". Before here it's "she".
- **Back in (the loyalty):** the fair is packing up around me and I run back in anyway, with it at my glass side, half a beat behind. Half the panels are out, the roof tarp is off and rain falls in. Every pane shows Tasha copying me, and none of them shows me.
  - **The find:** I step behind a stacked steel frame. I step out, and for half a beat, before anything in the glass can see me and catch up, nothing moves. Except one, far down the glass in the same spot as before, waving both arms. (The lag is the window. I can only see them when they can see me.)
  - **The proof:** she points at my green hat and goes, "what's THAT?" A copy can't start anything. I say PICKLE, on purpose, and she yells FRIES. She's still Tasha, and she's still winning.
  - **The way out:** in front of her pane it's between me and the glass, facing me, the way a reflection stands. I step back. It steps back too, half a beat late, right into her pane. Cut on the action to Tasha stepping out of that same pane, soaked and grinning, with the shine in her eyes. Nobody is seen crossing.
    - Then the shoulder bump.
    - In the pane behind her, the copy stands in my pose, half a beat behind us.
  - **The close of the creature:** the maze guy carries that panel to the truck with his back to us. In its glass, the copy watches us go, half a beat late. The maze's bulbs fade off in one slow fade, and that pane goes dark. It's never explained or redeemed.
- **The warm turn (shown, about 2:12):**
  - The fry van's warm strip light, side by side. My coins are already on the counter before she even points.
  - In the van's steel side our two reflections look up at the rain at the same moment we do, and nobody's late.
  - A close-up of her eyes with their shine back.
  - The score turns to the major, and the piano notes land together with no echo.
- **Last line:** `At the / fry VAN, / she pointed / at my HAT.` Cut on picture 0.2 to 0.3 s after "HAT" to the first shot (`tail` 0), so the loop is the joke starting again.

### Beats and length (580 to 630 words at about 290 wpm, cut at about 2:20 to 2:28)

| # | Section | Words | Time | What it does |
|---|---|---|---|---|
| 01 | The joke | ~80 | 0:00 to 0:17 | the joke happening, Tasha always wins, the fair packing up, the maze guy rolling back the roof tarp in silence |
| 02 | The maze | ~100 | 0:17 to 0:38 | in, the glass, a hundred Tashas, splitting up, the one standing still, "for once I came out FIRST", the flipped fringe |
| 03 | Walking out | ~100 | 0:38 to 0:59 | half a beat late, always on my puddle side, no splash, I stop and she stops late, her own trick done back at her, mouthed with no sound |
| 04 | The truck | ~55 | 0:59 to 1:11 | the quick hide, the freeze with one foot up, the small catch-up |
| 05 | The bumper cars | ~110 | 1:11 to 1:38 | the long hide, the freeze, "then she SAW me", silence, the replay, the stop, the eyes, the twist |
| 06 | Back in | ~135 | 1:38 to 2:12 | running back in, every pane her and none me, the find, the proof, the step back, her out, the shoulder bump, the panel on the truck, the slow fade |
| 07 | The fry van | ~40 | 2:12 to 2:25 | the warm turn in the picture, the last line, the cut back to the first shot |

## World and set (`reels/blocky/stories/mirror-maze/set.py`, new, from `kit.py`)

Nothing in the set has text: no lettering, logos, signs, price boards, numbers, plates or badges. Coins are plain discs. There are no real fair or showmen's brands. Nothing is cropped so it could read as a word.

1. **The fairground (about 55% of shots).**
   - **Ground:** a trodden field gone to dark mud, with plywood duckboard walkways (footsteps on `wood`). Big still puddles on the boards mirror the maze, and those are the puddle-side plant.
   - **The other rides:** lumpy and anonymous under dark slate and black tarps. Far back in the fog there's one unlit big-wheel skeleton with half its cars already off, as a silhouette only.
   - **The truck:** a flatbed with no badge, stacked with steel frames and glass panels held down with straps. No boxes, no tape, no cardboard (row 4).
   - **The bumper cars:** a steel-plated floor under a sagging tarp, the blocky cars shoved together under a cover, steel pillars.
   - **The worklight:** a caged worklight on a tripod near the rink, left on by the crew. It's steady, never flickers, and is the scare's light from below.
   - **The fry van:** far across the field, a small warm lit hatch seen in the wides all film long. It only fills the frame at the end.
   - **The only green thing in the film is my hat.** Grass, tarps and props carry no green.
   - **Never in the set:** fairgoers, kiddie rides (carousel, teacups, hook-a-duck), plush prizes, balloons, candy floss, clowns, painted faces, drains or gutters.
2. **The mirror maze (about 35%).**
   - **The front:** a trailer ride with steps up to a platform. A wide arch is framed by two rows of round lilac-white bulbs, with one row more along the roofline. They burn steady and never chase. The facade is plain geometric panels (diamonds and stripes in faded violet and silver), with no faces, eyes or lettering.
   - **Inside:** a triangular grid of tall glass panes in steel frames on a plywood floor, plus a few plain dark panels. On the first trip the tarp roof is on, and the light comes from bulbs along the top rails. On the second trip half the panes are out, the roof is off, rain falls in and the bare steel grid shows.
   - **The build:** the panes are clear glass, windows rather than mirrors, with a mirrored corridor built behind them. The copy is instanced where my reflection would stand. On the first trip, mirrored stand-ins for me and Tasha make it read as a normal mirror maze. Real mirror bounces go only in shots that need them, and the designer decides which. Never pan across reflected bulbs.
3. **The fry van (about 10%, the end).**
   - A boxy van with a lit hatch: one warm amber strip light, a steel counter, paper trays of block fries, plain disc coins.
   - One **polished steel side panel**, where our reflections are seen.
   - No menu, text or logo. The vendor is never in frame, and the framing keeps the inside of the hatch out of shot.

## Cast (R6 style, `rig.py`, faces in `faces.py`)

Three adults and the copy. Nobody has a voice of their own, and every word is voice A. No on-screen ages and no ages in the narration. Me and Tasha are young adults (`age` "adult").

| Who | Clothes | Hair / hat | Skin | Face |
|---|---|---|---|---|
| **Me** (narrator) | **dusty-rose** solid rain jacket (about `#b8697a`) with a darker rose collar and long sleeves, black jeans, black boots with white soles | short black `cap` hair under a **pickle-green bucket hat** (about `#6f9a2e`, matte) | light-medium warm (about `#d9a27a`) | round white eyes, black pupils with the glint, thin black brows. Easy, then `worried`, `scared` and `wide`, then `grin` at the end |
| **Tasha** | **sulphur-yellow** rain mac (about `#f0c419`, satin), long to mid-thigh, centred zip, hood down at the collar, nothing one-sided. Black jeans, black wellies. Soaked at the end (darker, glossier hair and coat) | dark-plum **swoop** (about `#5a2a48`), the fringe swept hard to her right | medium brown (about `#b07850`) | round white eyes with the glint, which is **her shine**. Thin plum-black brows. A lopsided `smirk` as her default, `grin` when she wins. In the glass, `worried` then `grin`, never crying or terrified |
| **The maze guy** | black solid rain poncho, dark-grey work trousers, black wellies, built about 1.15x wide | rig `hood`, up, in black | deep brown (about `#6e4a33`) | round eyes, heavy straight brows, `neutral`. Seen almost always from behind. He never speaks, never looks at us and knows nothing. He's never in danger |
| **The copy** | Tasha, mirrored (see the continuity list) | | | |

**The bucket hat is a new opt-in hat** in `rig.py` (`bucket`): a short round crown and a sloped brim all the way round, our own shape, with no logo. Defaults stay unchanged for every other story.

**Checked against batch 1:**
- **No hats it used:** no ballcap, fedora, straw hat, beanie or tabard.
- **No clothes it used:** no mustard knit, navy stripes, bottle-green coat, brown or rust plaid, denim work shirt, cream knit, plum knit or scarlet polo.
- **No hair it used:** no spiky dark brown, sandy swoop, grey bun, auburn cap, silver spiky or blond buzz. The swoop is a reused shape, but this is its first time in plum, on a woman, with no hat.
- **New to the channel:** the bucket hat and a hood that's up.
- **Copies nothing:** no game avatar or catalogue item.

**Rows 1, 3 and 4 aren't cast yet.** If one of them merges first with a bucket hat or a rose jacket, my look changes, and Tasha's coat doesn't.

## The creature: the copy (one model, built once, posed per shot)

Name it "the copy" in the code and notes. The narration says "she" until the twist and "it" after. It's Tasha's own rig gone slightly wrong. It's never pale grey, never thin, never rods or tentacles, and never explained.

### Continuity list (every shot uses these and nothing else)

1. **One model.** Tasha's spec, generated from it and mirrored left to right: the same blocks, skin, coat, hair, height and boots. Every Tasha in the glass is an instance of this one model, sharing its mesh and material data and posed from the same state. It's never a second hand-made spec. The real Tasha behind the glass is Tasha's own model.
2. **Exactly what's flipped:**
   - the swoop fringe (the plant)
   - her lopsided smirk
   - her handedness (my right arm is its left)
   Nothing else.
3. **The eyes are mirror-black.**
   - **Shape:** Tasha's own eye outline and size exactly. Never bigger, because bigger reads cute.
   - **Inside:** the white and the pupil are gone, filled near-black (about `#07070a`). No glint, glow, eyeshine or reflection.
   - **Brows and mouth:** Tasha's own, copying my expression, late.
   - **Built (amended):** `faces.py`'s opt-in `mirror` style, with story-local sockets in `set.py` that make the eyes real holes (amendment item 3). If pass 2b passes, the mouth at the stop is a closed flat line.
4. **The lag is half a beat of the score:** 0.395 s at 76 bpm, constant all film. Everything lags: steps, turns, arms, head, expression, mouth and blinks.
   - It blinks only when I blink, half a beat later, and never on its own. It never holds a no-blink stare, because that's ep12's keeper.
   - The designer may set the lag between 0.36 and 0.42 s at the test render. After that it's locked, and the bpm follows (bpm = 30 / lag).
5. **Where it stands:** where my reflection would be. That's on my puddle side outdoors and my glass side in the maze, across a plane about 0.8 m to my side. It walks beside me when I walk and faces me when I turn to it. The rigs are about 1.4 m wide, so it's never closer than about 1.5 m centre to centre.
6. **It's silent.** No footsteps, no splashes, no voice, no breath. Its mouth moves with my words, late, with no sound. Rain hits it like anyone else.
7. **The freeze:** when it can't see me, it holds exactly the pose it had, mid-step if it was stepping. Only the rain on it moves.
8. **The catch-up (amended):** it's fast once, at the truck. That's one move (the foot down, then my duck and stand) at about 3 to 4x, eased, never with an arm raise, then it settles back into the lag. At the scare it doesn't hurry (ruling 2's fallback). In the maze we cut away before the glass copies catch up, so a crowd of them never snaps at once.
9. **Its hood is down,** like Tasha's, in every shot.
10. **What it never does:**
   - touch anyone, lunge, jump or get closer between cuts
   - speak, start anything or laugh
   - get explained, redeemed or called kind or lonely
   - cross the glass on screen (the swap is a cut on the action)
   - appear outside the maze as more than one
11. **Sound:** none of its own. Its beats are marked by the score and the silence (see "Music and sound").

### Phone-size rules

- **Reveal and find shots:** the face is at least 1/5 of the frame width, and at least 1/3 in the scare's end shot.
- **Lit for fear:** front lights dead. The key comes from below (the worklight bounced off wet boards) or from the side, with a rim from the lilac maze glow behind.
  - **The copy's eyes are the darkest thing near its face.** This flips the batch-1 rule: the scare is the missing shine.
  - Tasha's real glint is the brightest point on her face. The coat stays below about 0.85 value, and skin never clips.
- **The lag must read in the wides.**
  - Figures are at least 1/3 of the frame height wherever the lag is the point.
  - Walks are side-on, so the out-of-step legs are the read. At 0.4 s our legs are nearly opposite in phase.
- **The fringe flip:** the opening shot and the exit shot are framed from the same angle, with her face at least 1/4 of the frame width and the fringe rimmed by the maze light. The viewer compares the two.
- **Before the scare:** the copy's face is never in a lit front close-up. It's side-on, from behind, half behind me or back-lit, except for the two mid shots in section 03 where a sharp viewer can catch the eyes.
- **In the maze:** at most 6 to 8 readable copies a frame. In the find shot, the real Tasha is at least 1/8 of the frame height and separated by motion.
- **The caption band:** faces and eyes are never under it.

### The test still (built first, before any set dressing)

- **The frame:** the scare's end at 540 x 960.
  - The copy, frozen in my pose: body side-on, head turned to the lens, one hand half down from its face, standing on wet duckboards in the rain about 1.5 m from me.
  - Lit from below and the side, rimmed lilac, front lights dead.
  - My shoulder and hat brim in the foreground, soft, for scale. The caption band is clear.
  - **Amended:** from pass 2 on, the test frame is the critic's tighter one, with the head at 72% of the frame width and no bulbs in shot. My shoulder isn't in it, and an over-the-shoulder shot just before the stop carries the scale.
- **The companion still:** the real Tasha in the same pose and light, for the critic's side-by-side.
- **The pass:** at phone size, a cold viewer picks the wrong one in under a second, and it reads frightening, not cute, sleepy, a doll or "sunglasses". **The scored bar (amended):** silly risk 7 or better and fright 6 or better on the still, then fright 7 on the preview (amendment item 2).
- **If it fails, change it in this order:**
  1. eye size equal to Tasha's (never bigger)
  2. brows flat and level with a straight mouth (copying my stunned stare), instead of my scared face
  3. a stronger light from below and a colder rim
  4. the head dropped about 5 degrees, with the eyes level on the lens
- **The motion tests:** the replay test is done, and the fallback is in (ruling 2). The truck catch-up's 2 s test is next (amendment item 1).
- **Two failed passes is a `craft` stop on the creature** (kill criteria). Pass 2 includes 2b. Pass 3, the in-row redesign, is in amendment item 2.

## Mood, palette and caption colour

- **The night:** overcast rain with no moon and no stars. Sky and fog are violet-grey (about `#1c1826`). It's not indigo (ep12's yard), not navy (ep13) and not blue-green (ep11).
- **The maze's lilac-white bulbs are the main light.** The wet black ground mirrors them, and the rain streaks lilac in front of the arch.
  - There are no fluorescent tubes, no tungsten bulbs, no swinging light, no caustics and no flicker.
- **The fry van's amber strip is the only warm light.** It's a small square in the wides, and it fills the frame only at the end.
- **The grade:**
  - violet-black shadows and neutral-cool highlights
  - saturation about 0.9, with the yellow held
  - contrast about 1.1, vignette about 0.4, bloom about 0.35 on the bulbs, grain about 0.012
  - `red_line` on the fry-van shots, because warm grades fail WCAG red (ep12 lesson)
- **Colour by person:** Tasha's yellow is the strongest colour in the film. My rose and the green hat are second.
- **Caption key colour: raincoat yellow `#ffd23a`.** PICKLE, FRIES and TASHA are her colour. It's the complement of the lilac light and unused by batch 1. It's a gold, kept apart from ep11's lime `#c8ff5a`, ep12's red `#ff4a3d` and ep13's aqua `#3fe0d0`.
  - The designer checks it at phone size against the coat in the brightest maze shot. The dark outline should carry it.
  - **Fallback: fry-van amber `#ffa040`.** Switch to it if it washes out, or if row 1 or row 3 merges first with a gold or amber key within about 15 degrees of hue. That's the designer's call.

## Music and sound

- **The score:** synthesized, `dorian` on E2 (`root` 40), **76 bpm**. Batch 1 used phrygian at 66, harmonic at 58 and whole-tone at 50.
- **Voices:** `drone`, `pad`, `piano` and `pulse` only. There's **no choir** (all three batch-1 reveals used one) and no music box, calliope, organ or fairground tune.
- **The signature is the late echo.** From the first trip into the maze, every piano note is answered half a beat later by a quieter copy of itself, at the same pitch with no detune (that's ep11's piano).
  - From the walk out, the pulse sits on the beat, and its copy sits on the off-beat.
  - When Tasha steps out of the pane, one piano note plays with no echo, the first one that isn't copied.
  - At the fry van, the score turns to the major for a few bars, and every note lands together. Nobody's late.
  - This needs an opt-in `echo` on score voices in `sound.py` (delay half a beat, about −8 dB), with defaults unchanged. How is the designer's call.
- **Sections:**
  - **01:** drone and pad.
  - **02:** add the piano with its echo.
  - **03 and 04:** add the pulse with its echo, with the energy rising.
  - **05:** builds, then the hole.
  - **06:** fast pulse and piano echo. A short drop when the glass freezes, then the unechoed note at her exit, then everything down with the slow fade.
  - **07:** the major, with no echo.
- **Silence before the scare:**
  - About 0.7 s before the replay, everything drops out (`music_drops`, −40 dB, the rain too) and only the voice plays.
  - The replay itself is silent: the copy makes no sound.
  - A `hit` and `sting` (`keep`) land when it stops in my pose.
  - Then about 0.5 s of nothing, then the rain comes back first, then the drone under the twist lines.
- **Ambience:** `rain` on tarps, boards and puddles, and on the open maze in section 06. `wind`, light, for the flapping tarps. `hum` for the maze's generator. `drips` under the half roof. No crickets, water or room tone.
- **Effects:**
  - my footsteps on `wood` with a puddle splash on every wet board, and none for the copy
  - panel bolts (`click`), a panel set on the truck and the tailgate (`thud`), coins on the counter (`click`)
  - a soft `whoosh` under the cut through the pane
  - a low `riser` under "Tasha was still IN there"
  - **No `knock` and no `bell` anywhere.** A bell is row 1's DING.
- **The closing sound:** the generator winds down with a falling pitch as the bulbs fade, at −18 dB or louder so it's heard (README lesson).
- **The voice:** voice A for every line. Tasha's words are reported. The maze guy and the copy never speak. Add phonemes for "Tasha" if `asr` mishears it.
- **The master:** −14 LUFS, true peak at or below −1 dBTP.

## Shot plan (broad strokes, about 72 shots)

A new shot on almost every sentence. The camera is low and moving: side-on two-shots for the lag, low shots across the puddles, and close faces lit by the maze.

- **01 The joke (about 10):**
  - The open: side-on two-shot under the maze glow in the rain, Tasha pointing at my green hat. Her face close: grin, the shine, the fringe to her right (this framing comes back at the exit). My face, resigned.
  - Her FRIES yell (a mouth flap). The fair packing up: tarps, the truck, the dark big wheel.
  - The maze guy rolling the roof tarp back, his back to us. The fry van's warm square far off.
- **02 The maze (about 12):**
  - Up the steps under the bulbs. Inside, the glass and a hundred of us. We split up.
  - A slow track past the panes. Far down the glass, one Tasha standing still (hold it long enough to read).
  - Me out first, rain. Her stepping out, the exit framing matching the open, her fringe swept the other way.
- **03 Walking out (about 10):**
  - Side-on walks across the duckboards, her legs out of step. A low shot along a puddle: my splash, her silent boots.
  - I stop and she stops, late. My trick: I point at my hat, she points at her own head, mirror-handed, mouthing with no sound.
  - Two mid shots where her dark eyes can be caught.
- **04 The truck (about 7):** I duck behind the stacked truck. Her frozen with one foot up, rain on her coat. Me stepping out. Her catching up in one fast move (the foot down, the duck and stand, arms at her sides), then back in the lag.
- **05 The bumper cars (about 12):**
  - Behind the tarp, me shaking, hands over my face, three breaths (close, side-on, with the hands at the ends of the sleeves and never the arm's full length). Cut to her frozen on the open ground, one hand half up, the worklight below her.
  - Me stepping out. The hole. The replay (the fallback: hand down, one step, head round) in one held side-on mid shot at `step: 1`, her coat under a quarter of the frame.
  - The stop: her face, lit from below, black eyes, the hit. My `wide` face. The twist lines over slow push-ins.
- **06 Back in (about 16):**
  - Running back across the field. It at my glass side.
  - The open-roofed maze in the rain. A wide of panes, every one her, none me.
  - Behind the stacked frame. Stepping out to the frozen gallery, one waving (hold about 0.6 s).
  - Her pointing at my hat. My PICKLE, her FRIES.
  - In front of her pane, it facing me. My step back, its step back. Cut on the action. Her stepping out, soaked, grinning.
  - The eye close-up with the shine back. The shoulder bump, side-on.
  - The panel carried to the truck, the copy in its glass watching us go. The slow fade of the bulbs, the pane going dark.
- **07 The fry van (about 5):**
  - The warm two-shot. My coins already on the counter. Her finger rising toward my hat.
  - The steel side: our reflections look up at the rain with us, on time.
  - The last line, then the cut to the open.

**Budget:** about 2:25 on twos is about 8 to 10 hours (README).
- The glass is the costly part. Use thin clear panes and instanced copies, and keep true reflection for the steel van side and any shot that needs it.
- Do a stills pass and the 10 s opening first.
- Batch every timing change into one re-voice before the final.

## Script lines the scriptwriter must write or change

There's no script yet. Write pitch B in full with these changes. The references are to pitch B's own lines in `01-pitches.md`. I don't write the lines myself, so the wording below is a suggestion unless it's quoted as fixed.

| Where in B | Change | Why |
|---|---|---|
| First line (`Tasha points / at anything GREEN...`) | Keep the first two lines. Make the rule plain in two short lines: I say PICKLE, so she yells FRIES and I pay. Add one line that she always wins (e.g. `I have NEVER / won. / Not ONCE.`) | the proof and the last line need her FRIES yell planted, and "for once I came out FIRST" and "still winning" need her streak |
| Every "cap" (beat 3, the proof, the last line) | becomes **hat**. The last line is `At the / fry VAN, / she pointed / at my HAT.` | it's a bucket hat now, because ballcaps were used in batch 1 |
| Beat 1, the maze guy | silent, with no quoted line. Keep him rolling the tarp back | no knowing elder |
| Beat 2 | add `For once, / I came out / FIRST.` (from A) before she comes out. Keep "I figured it was the angles" and "I figured it was the wind" as a pair, and don't add a third | a plant that re-reads at the twist |
| Beat 3, her "what's that?" | she **mouths** it, with no sound (e.g. `Her mouth / made the WORDS. / No SOUND.`). Add one short line for the silent boots (e.g. `Her boots / didn't SPLASH.`) | the copy never speaks (ep11's copied voice), and the silent steps are a fair plant the viewer can hear |
| Beat 4 | the quick hide moves from the bumper cars' booth to **the truck**. "rain running off her hood" becomes "her coat" | the scare owns the bumper cars, and her hood is always down |
| The scare | keep B's four steps. Add a short line before the hole (e.g. `Then she / SAW me.`). The replay is a **pause beat with no words and no caption** (amended: 1.8 s for the fallback, and L52 rewritten to match, both done in the script). Her black eyes are mentioned for the first time here, after the stop | silence before the scare, and the eyes saved for the reveal |
| The twist | keep `That's what / a REFLECTION does.` / `It can't MOVE / if it can't / SEE you.` / `Tasha was / still IN there.` Change "She came out of the GLASS" to **`It came out / of the GLASS.`** Use "it" for the copy from here on | the pronoun turn is the twist landing |
| The find | rewrite the logic: I hide behind the frame, step out, and for half a beat nothing in the glass moves, except one, in the same spot as before, waving both arms (e.g. `For HALF a beat, / NOTHING moved.` / `Except ONE.`) | B's version has me watching them freeze from where they can't see me, which doesn't hold up |
| The proof | keep it, with "I say PICKLE" made deliberate (I lose on purpose). Keep `She's still TASHA. / And she's still WINNING.` | the loyalty, shown in the joke |
| The way out | keep the step-back logic. Never "home", "guide", "lead" or "follow". Never describe a crossing. The shoulder bump is shown, and at most one short line | row 3 guides its creature home, and the swap is a cut |
| New, after she's out | one or two short lines: the maze guy loads that panel on the truck, and the copy in it watches us go, late. The bulbs' slow fade can carry no words | closes the creature without explaining it |
| The warm turn | keep "we look up at the rain at the same moment, and nobody's late", now seen in the van's steel side. "I've got the money out" becomes `My coins were / already on / the COUNTER.` | the rig can't hold coins, and C's reflection image |
| Whole script | 580 to 630 words. No "Last NIGHT,", no ages, no "it didn't touch me", no "only moves when", no "not X, it was Y", no "now I always / we never" line, no "from the INSIDE", "pressed", "every night", "the next night", "one by one", "just said" or "In MY voice", no child words, and none of ruling 5's words. Read every line against the picture under it (README) | the batch skeleton and `check` |

## Standards risks

- **Not made for kids:** `made_for_kids: false`.
  - A fair, fries and a pickle joke in blocky art lean young. So the frame is two adults on a rainy night out, no fairgoers, no kiddie rides, no prizes, plush, balloons or candy floss, a dark violet-grey palette, and no music box or fairground tune.
  - The title and description never target kids.
- **Harm to Tasha:** ruling 5, every frame and every word. The copy never touches her or anyone.
  - **The replay's** one step goes sideways along the plane, and the gap stays about 1.5 m or more on every frame from P01 to L55. The copy doesn't advance. Standards' contact probe covers the replay, every copy beat and the shoulder bump. The bump is the only allowed contact: touching, not intersecting.
  - **The maze guy** is never near a falling panel. No glass breaks.
- **Flashing** (`safety.house_report` at the final's own frame steps):
  - the truck catch-up: a yellow coat moving fast, at `step: 1` (the replay is slow now, but it's still measured at that step)
  - every maze shot with bulbs or their reflections
  - rain streaks catching the bulbs
  - the bulbs' slow fade (one fade, never a cut to dark)
  - the fry van's warm grade (red)
  - No chasing bulbs and no pans across reflected bulbs.
- **IP and look:**
  - Our rig, faces, bucket hat and coat. Nothing from the game, and "Roblox" appears nowhere. The new engine options and what to check on each are in amendment item 3.
  - The copy isn't a known creature. Ours freezes when it can't see you, the reverse of the famous "moves when unseen" monsters, which are never named.
  - The IT echo is ruling 3, and the *Us* echo is ruling 4.
- **No real places or brands:** the fair, the town and the van are unnamed. No text in the set.
- **Never claimed as true:** no "true story", "this happened" or "real" in the video, title, description or pin.
- **One voice:** voice A reads everything. No cast `voice`.
- **The pin, for the packager:** a question about a detail planted early, e.g. when they first noticed her hair.

## What this story must not share

**The batch skeleton (README):**
- a closing-section opener "Last NIGHT,"
- an on-screen age
- a spoken "it didn't touch me"
- an imperative-rule title
- an ending where I gesture and the creature answers in kind (here Tasha points and the copy is gone)
- "the monster was kind/lonely all along", the ritual done back, or a later-night return
- an "At the PLACE, rule" opener
- a knowing elder
- a night-shift or one-summer narrator
- a pale grey creature
- "pressed FLAT" or a wet click
- "not X, it was Y"
- a last line to the creature

| Against | Not in ep14 |
|---|---|
| **ep11, the back row** | a bus, a seat or a headcount. Fluorescent tubes, flicker or a blue-green grade. A lime key. A grey, blank or seam-mouthed creature, too-long arms, a head turning too far, "closer each time the lights come back". A copied voice, handprint, "from the inside". Detuned piano. A warning regular or silent authority. Its cast looks |
| **ep12, knock-back** | knocks of any kind. A floor, cellar or crawling. An upside-down or never-blinking face. A too-wide flat creature. Red long johns or wax skin. Anything pressed across a door. A relative who leaves. Warm tungsten, a swinging bulb or moonlit indigo. A red key. Harmonic minor at 58. Silence under every hit as the signature. "Now I knock first", or "something learned our knock" as the ending |
| **ep13, closing time** | water, tanks or caustics. Real modelled eyes, rows of eyes, eyes opening one after another. Any cascade. A bow, a wave ritual, applause, a small one. "We're the exhibit". Whole-tone, or the muffled-through-water filter. An aqua key. Tabards. A supervisor who stays. Counting. Its cast looks |
| **Row 1, floor-thirteen** | a lift, floors, buttons, numbers, a DING or any bell. "The Attendant". Lights out, then closer. Brass, black and button glow. Talking our way out. Strangers becoming friends. A "we never ride alone" style last line |
| **Row 3, lookout** | a forest, a giant, a tower, a radio, binoculars, footprints. Fog that lifts, or moving only in fog. Moss and bark. Lantern eyes. Carrying a light, or guiding or leading a creature home. A question to the viewer as the opener. Something growing toward my door |
| **Row 4, moving-day** | boxes, tape, cardboard or marker faces. Moving house, Mum. "From the INSIDE". A face that changes while nobody's looking (ours copies live, in front of me). A mid-scare opener. Tucking in, a quilt. Keeping the creature |

`check` compares premise, twist, world and three-word phrases against every story on disk. Rows 1, 3 and 4 are being written now, so run `check` again after merging main before the final.

## Kill criteria

- **The creature test still reads as silly** (cute, sleepy, a doll or "sunglasses") after the two passes in its fix order. That's `craft` on the creature.
  - **The retry, within the row:** the same Tasha-gone-wrong, with a different wrongness. For example, her face a half beat behind her head's turn, or the flipped face alone with no shine, at Tasha's eye size. Never pale grey, never rods.
  - **Amended:** pass 2 includes 2b. The bar is silly risk 7 and fright 6 on the still. If 2b misses, the retry is creature pass 3 inside ep14 (the face late on its own head). If pass 3 misses, ep14 is killed `craft` (amendment item 2).
- **The replay reads as funny or as a video glitch** after two passes. That's the fallback in ruling 2, not a kill. **Done:** both passes read silly, and the fallback is in. If the scare then fails the cold watch (fright under 7 on the preview), revise first, then `craft`. If the truck catch-up reads silly, its fallbacks are in amendment item 1, and it's not a kill.
- **The lag doesn't read at phone size** on the preview (critic or audience panel). Revise: set the lag to 0.42 s, with more side-on two-shots. If it still fails, `craft`, with the retry note "make the copy's lateness the first thing in the film".
- **The twist or the way out fails a cold watch:** reviewers can't say who was real, or how she got out. That's `craft`.
  - **The retry note:** plant the one still Tasha louder in section 02, and show the step-back from a wide where the plane between us is obvious.
- **Standards flags kid appeal, an IT or *Us* reading, or harm to Tasha,** and it survives two rounds. That's `craft` for our build, or `policy` if it's the setting itself. Only then may the coat's colour change.
- **The maze can't be drawn inside the budget,** so the glass reads as flat cards. That's `craft`, with the retry note: fewer panes, more dark panels, and the copies only in the shots that need them.
