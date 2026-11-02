# ep30-top-rope: the script (writer, redo 2026-11-02)

- **Slug:** `ep30-top-rope`. Folder `stories/ep30-top-rope/`. Redo of the held version ("redo: the first line must state the world's rule", owner 2026-11-02). Premise, rule, twist, cast roles and narration are all new.
- **Title (package):** In This Town, When You Fall, Someone Goes UP
- **Word count:** 421 spoken words in 56 lines, all `narrator`, plus 2 pause beats (1.3 s).
- **Estimated length:** about 1:35. At 290 wpm the speech is 1:27, the 0.12 s gaps add about 7 s, the pauses 1.3 s and the tail 0.25 s. If it retimes over 1:45, cut L25 first, then L32. Never cut a line from L41 to L48.
- **Every line is re-voiced.** No line from the old script survives as it was, so voice all 56 fresh.

## For the builder: what's reused and what changes

**Reused unchanged (don't rebuild):**
- The whole mill shell: floor, brick walls, ceiling, timber beams, iron columns, arched windows, lamps on chains, floodlights, window fill, the `hall` light, and the lamp ramp cue (`lamps` with `to` and `dur`).
- The climbing wall: panels, seams, holds, top hold, the overhang roof and its holds, the fascia.
- The anchor plate, ring, bolts and the two lilac tally strokes (the lore plant, now under L14).
- The auto-belay box and its red tag (dressing only now: no line names it, and the `tag` cue is unused).
- Crash mats, chalk bucket, rope coil, tape roll.
- Cast `me`, exactly as it is.
- The old `sam` model's look, unchanged, renamed to cast key `mum` (she's now my Mum).
- The creature lighting rig (`ckey`, `crim`, `cfill`) and the flip-and-pose code for a figure standing upside down on the roof (POSES `t1`, `t2`, `t3`, `lip`). It now flips and poses **Mum's** model.
- Rope mode `me` (my harness to the ring) and mode `sam` (renamed `mum`: my harness up to the ring and down to Mum's harness).

**Removed:**
- The Headstander creature (`story["creature"]`, its lilac body, black harness and knot). Nothing else stands on the ceiling.
- Rope modes `creature`, `end_up`, `end_down`, the lilac-dusted rope end (`coil` cue), and the phone prop on the mat.
- The `belay` pose.

**New or changed:**
1. **Mum on the ceiling.** POSES `t1` to `lip` now place Mum's model, flipped, soles flat on the roof. Her face uses a clear wide smile (so upside down it reads as a frown). In `t1` to `t3` she's lit as a silhouette only: front dead, the cold blue rim, a dim key from below, eye highlights the brightest thing. At `lip` (S37, S38) the key from below is up enough to read her face in the blue. Her bun hangs "down" toward the floor.
2. **Mum's bench moves.** One timber bench (the old `benchs`/`benchl` parts) is moved per beat by a new cue `bench: {"at": "home" | "t1" | "t2" | "t3" | "lip"}`. `home` is beside the mats (the old spot), the others sit directly under the matching ceiling pose, nearer the wall each Thursday. When Mum is on the ceiling, the bench is empty.
3. **Lilac dust on the roof.** A thin matte lilac `#b9a3d9` dust layer on the underside of the overhang roof, patchy, never glowing. Two sole-shaped bare patches (the shoe prints) sit above the `lip` bench spot (S45).
4. **Mum's dust and soles.** A cue `mum_dust: {"hair": bool, "soles": bool}`: a lilac dust tint on the top of her bun (from S22 on Thursday 1, then after each fall) and lilac soles (S42).
5. **The lift ring (the rule's marker).** A soft amber `#ffb54a` emissive ring, about 0.9 m across and 4 cm wide, lying flat on the floor or mat under anyone who's gone up. Cue `ring: {"who": name, "on": bool}`. It ramps on over 0.4 s and off over 0.6 s, never instant (flash rule 7).
6. **Lifting.** A cue `lift: {"who": name, "h": metres}` raises a standing person straight up, feet dangling a little, arms out from the sides. Used on the date, his mum, me and Mum.
7. **New background cast:** `date_guy`, `date` and `his_mum` (below). Hall montage only.
8. **New props:** Mum's flask (a dark green cylinder on the bench), a plain cup, a wooden chair for `his_mum`.
9. **Halfway pose (S54 to S56).** Me and Mum each hanging on one strand of the same rope, halfway up the wall, side by side and face to face, both the right way up. Mum wears the navy harness only from S50 on.

## The big idea

**In a town where your fall lifts the one who loves you most, the thing standing upside down on the climbing-wall ceiling every time I fell was Mum, who's scared of heights, going up for me.**

## Premise

In this town, when you fall, the one who loves you most goes up, wherever they are. I only started climbing this autumn, in a wall built inside an old brick mill. Mum, who won't even stand on a chair, comes every Thursday and sits on a bench by the mats with her flask. When she trips, I go up. When I fall, I've never seen anyone go up for me. Then, every Thursday I come off the top of the wall, someone is standing upside down on the ceiling above me, one hold closer each week.

## Rule

- **The world's rule (L01):** when you fall, the one who loves you most goes up. They lift straight off the floor while you come down soft, and an amber ring glows where they were standing. Shown at work at once (S01 to S04), as a joke (L03, L04), as love (L07, L08), and turned in the climax (L49 to L53).
- **The narrator's exception (L10, L11):** when I fall, I've never *seen* anyone go up for me. Not even Mum. It's true as said, and it's the mistake the whole story turns on.
- **Seconds 15 to 30** show the rule at work on me (I come off at the top, and something is on the ceiling). Nobody explains anything.

## Twist

Every time I fell, Mum went up, all the way to the ceiling. She put her feet on it and stood there upside down until I was lowered, and came back down to her bench as I came down to the mat. She's scared of heights, and never said a word, because she didn't want me to stop climbing. The "someone" on the ceiling was her, seen from below in the dark: her bun hanging down, her smile upside down.

The first line turns over. At the start, "the one who loves you most goes up" is a fun town fact, and my exception reads as "nobody loves me most". After L45 and L46 it's a plain description of what Mum has done every Thursday. The last line, the same rule, then "So next time you FALL, / look UP.", lands cold on the dark ceiling.

**Plants a rewatch catches:**
- **Plant 1, the knot of hair (L17, S17):** "A knot of HAIR / hung off its head / like a WEIGHT." That's Mum's bun, hanging toward the floor. Mum's bun is in every bench shot.
- **Plant 2, the bench and the dust (L21, L22, L29):** each time I land she's on her bench with lilac dust in her hair, and on the third Thursday "she'd moved her BENCH / right under my ROUTE." The bench is under the figure every week (it's one hold closer because she sat closer).
- **Plant 3, the frown (L26):** "Its mouth / curved DOWN / in a FROWN." It's her smile, upside down. Paid off at L49.
- **Plant 4, the fear (L06, L32, L38, L41):** "She won't even stand / on a CHAIR." Then the figure breathing fast, its eyes wet, and Mum white as chalk when the lamps come back.
- **Plant 5, the empty bench and the ring (S18, S41):** the wide shots while I'm lowered hold the bench at the frame edge, empty, a faint amber ring on the mat under it. Never narrated.
- **Plant 6, "I never look DOWN" (L12):** why I never saw her bench empty.
- **Plant 7, the slow lower (L19):** "slower than a MACHINE / should be": Mum's weight coming down as I do.

**The loophole (climax, L49 to L53):** the rule's own logic, read again. If Mum goes up whenever I fall, she can do it on the other end of my rope. That's all a belay is. She holds my rope, I let go at the top on purpose, she goes up as I come down, and we meet halfway, the right way up.

## World

An indoor climbing wall built inside a tall old brick mill, Thursday evenings in autumn. Soot-dark brick, cast-iron columns, heavy timber beams, tall arched windows of deep evening blue. Iron factory lamps on chains (warm tungsten). The wall is grey-green plywood with muted holds, 12 m high, leaning out at the top into a 3 m overhang roof of holds. The roof's underside is coated in old lilac dust that nobody ever brushes. A steel anchor plate and ring at the top of my route, and the grey auto-belay box beside it. Blue crash mats. Floodlights at the foot of the wall. Mum's timber bench, her flask, a chair across the hall. No text anywhere: no signs, grades or brands.

## Cast (all adults, nobody hurt, nobody young)

- **`me`** (adult, narrator, started climbing this autumn): unchanged. Short dark brown block hair, rust-orange tee with a cream pin-stripe, slate trousers, sand harness, cream shoes, white chalk bag. Worried brows in the scare, a wide grin at the end.
- **`mum`** (adult, my mum, sixties): the old `sam` model. Silver-grey block bun, forest-green long-sleeve, grey trousers. A clear, kind smile. She sits, waves, pours tea, asks once, and holds the rope at the end. Her words are reported (L27, L47). She never explains the rule.
- **`date_guy`** (adult, twenties, montage only): mustard tee, dark blue trousers, black block hair with a side part, a red harness.
- **`date`** (adult, twenties, montage only): teal long-sleeve, black trousers, a long auburn block ponytail.
- **`his_mum`** (adult, fifties, montage only): a plum cardigan over a cream top, grey curls, round glasses, on a wooden chair across the hall.

## The figure on the ceiling (it's Mum, not a creature)

- One model, Mum's, flipped once and posed per shot. Never seen moving, only nearer between Thursdays.
- Lit as a silhouette until S36: front lamps dead in its shots, key from below (the floodlights) kept dim, the cold blue window rim on its outline, eye highlights the brightest point. The bun hangs toward the floor. At S37 and S38 her face reads clearly in the blue, upside down, the smile reading as a frown, but the light stays cold so it's a scare first.
- She never touches me. A hand's width of air between our faces at S38.

| Beat | Lines | Mum is | Bench (cue) |
|---|---|---|---|
| Hook, montage | L01 to L08 | on the bench, then tripping at the mat edge (S07) | `home` |
| Exception | L09 to L11 | on the bench pouring tea (S11) | `home` |
| Thursday 1 | L13 to L19 | on the ceiling at `t1`, three holds back from the lip | `t1`, empty |
| Landing | L20 to L22 | back on the bench, lilac dust in her bun | `t1` |
| Thursday 2 | L23 to L26 | ceiling `t2` | `t2`, empty |
| Asks | L27, L28 | standing by the bench holding out the rope end | `t2` |
| Thursday 3 | L29 | on the bench | `t3` |
| Thursday 3 fall | L30 to L32 | ceiling `t3`, right over my route | `t3`, empty |
| Thursday 4 scare | L33 to L39 | ceiling `lip`, face level with mine (L37, L38) | `lip`, empty |
| Lamps back | L40 to L44 | on the bench, white, lilac soles | `lip` |
| Reveal and warm turn | L45 to L56 | on the mat, then on my rope halfway up | `lip` |

## Look and sound

- **Palette:** soot brick `#3b2a24`, timber `#6b4a2e`, wall panel grey-green `#5f6e64`, tungsten `#ffc77a`, window blue `#1d3a6b`, crash-mat blue `#2a4c8f`, ceiling dust lilac `#b9a3d9`, lift ring amber `#ffb54a`, Mum's green `#2f5a3e`, her silver `#a9acb2`.
- **Caption key colour:** rope teal `#3ee0c8` (unchanged).
- **Music:** E Phrygian, 74 bpm. Thin and light for the montage: a soft plucked figure, almost playful. A low drone enters at L15 (the first sighting) and holds to L44. Drop (voice and hit only) for 0.7 s before L37. From L49 the plucked figure returns in E major over a warm pad. For L56 the drone comes back under "look UP" and the major pad drops out, so the last beat lands cold.
- **Ambience:** a big hollow room, a lamp chain ticking. Fast breathing from the ceiling at L32 and L37 (synthesized, soft).
- **Closing sound:** a low ceiling creak with a falling pitch under the last word, at -16 dB, then the 0.25 s tail and the loop cut back to S01.

## Light changes (flash plan)

- **Lamps out (L33):** ramp from full to 15% over 0.7 s. The window blue stays as fill, so no frame goes black. Hold through P01 to L39.
- **Lamps back (L40):** ramp from 15% to full over 0.6 s, landing as my feet touch the mat.
- **Lift rings:** on over 0.4 s, off over 0.6 s. No two rings switch in the same half second.
- **Warm turn (L49 to L55):** all lamps full, floodlights on. Brightest shots in the film. L56 dims the roof shot only by framing (camera on the dark roof), with no light change.

## Lore plant

- **What:** the two lilac tally strokes already scratched into the steel anchor plate beside the ring, two for a climb built for two. No extra stroke. No Keeper is shown, and none is needed: Mum was my other end all along, so the count was never short.
- **Where:** S14b, under L14 ("The rope CAUGHT me."), a close on the anchor ring with my rope running through it, the two strokes beside it in the upper middle of the frame, out of the caption band. Held about 1.4 s. Not narrated.

## Shot plan and narration

Each line gives the id, then the caption chunks split with ` / `. CAPS are the key words, in rope teal. Every line is `narrator`. Hands never grip: cut away before any hand closes, and show a hand at the end of its sleeve.

### 01 The rule (0:00 to 0:08)

- `L01` narrator: In this TOWN, / when you FALL, / the one who LOVES you most / goes UP.
  - [S01: lamps full, bright. Medium on the low wall: `date_guy` coming off a hold a metre up, and behind him on the mat `date` already lifting off the floor, the amber ring glowing under her feet. Both faces in frame, out of the caption band. 1.4 s]
  - [S01b: closer on `date`, a metre up, arms out, laughing, the ring under her. Held to the end of the line]
- `L02` narrator: He comes down SOFT. / She goes up / a METRE.
  - [S02: `date_guy` settling gently on the mat, looking up at her, delighted]
- `L03` narrator: First DATES / come here / to fall off / on PURPOSE.
  - [S03: two-shot, `date` coming back down onto the mat as the ring fades, the two of them grinning at each other]
- `L04` narrator: Sometimes / it's his MUM.
  - [S04: across the hall, `his_mum` lifted a metre straight up off her wooden chair, ring under the chair, glasses askew, startled. A comic beat]

### 02 Mum (0:08 to 0:18)

- `L05` narrator: My MUM / comes every THURSDAY.
  - [S05: Mum on her bench by the mats (`home`), flask beside her, waving up at the wall. Her face clear, the silver bun clear]
- `L06` narrator: She won't even stand / on a CHAIR.
  - [S06: Mum seated, looking firmly at her flask, nowhere near up]
- `L07` narrator: When SHE trips, / I go UP.
  - [S07: Mum catching her toe on the mat edge. Cut to S07b: me lifting a metre off the floor, amber ring under me, arms out]
- `L08` narrator: That's how I KNOW.
  - [S08: Mum steadied, laughing up at me hanging in the air. The picture of who I love]

### 03 My exception (0:18 to 0:24)

- `L09` narrator: I only started / climbing this AUTUMN.
  - [S09: me at the base clipping into the auto-belay line, from behind (cut on the reach)]
- `L10` narrator: And when I FALL, / I've never SEEN / anyone go UP / for ME.
  - [S10: me coming off a low hold onto the rope, facing the wall. 1.4 s]
  - [S10b: my face over my shoulder, looking round the hall at the mats: nobody in the air. The bench is out of frame]
- `L11` narrator: Not even MUM.
  - [S11: Mum on her bench, pouring tea from the flask into the cup on the bench (no grip), not looking at me]

### 04 Thursday one (0:24 to 0:39)

- `L12` narrator: I never look DOWN / on the wall.
  - [S12: me mid-wall, eyes fixed on the panel in front]
- `L13` narrator: The first THURSDAY / I came off / at the TOP.
  - [S13: over my shoulder at the top hold, the anchor and box above. My hands coming off, open, at the ends of the sleeves]
- `L14` narrator: The rope CAUGHT me. / I looked UP.
  - [S14: me hanging just below the top hold, the rope taut. 1.0 s]
  - [S14b, LORE PLANT: close on the anchor ring with my rope through it, the two lilac strokes beside it, upper middle of frame. Held 1.4 s]
- `L15` narrator: Someone was STANDING / on the CEILING.
  - [S15: my eye-line up the roof: a dark figure standing upside down at `t1`, three holds back from the lip. Silhouette, blue rim, two eye highlights. The drone enters]
- `L16` narrator: Upside DOWN, / its feet FLAT / on the overhang.
  - [S16: side view of the roof, its soles flat on the dusty lilac panels, head hanging toward the floor]
- `L17` narrator: A knot of HAIR / hung off its head / like a WEIGHT.
  - [S17: closer on the silhouette's head, the bun hanging down, lit only by the rim]
- `L18` narrator: Was THAT / who went UP / for me?
  - [S18: my face, looking up, worried brows]
- `L19` narrator: The box LOWERED me, / slower than a MACHINE / should be.
  - [S19: PLANT 5. Wide from low across the hall: me coming down the wall, the figure small on the roof above. Mum's bench at the right edge in shadow, empty, a faint amber ring on the mat under it. Never narrated]
- `L20` narrator: When I LANDED, / it was GONE.
  - [S20: up at the roof from the mat: empty, only lilac dust]
- `L21` narrator: Mum was on her BENCH / with her FLASK.
  - [S21: Mum on the bench (`t1` spot), flask in her lap, a small smile]
- `L22` narrator: There was lilac DUST / in her HAIR.
  - [S22: close on the top of her bun, a lilac powdering on the silver]

### 05 Thursday two (0:39 to 0:51)

- `L23` narrator: Next THURSDAY / I fell AGAIN.
  - [S23: me coming off at the top hold, from the side]
- `L24` narrator: It was one hold / CLOSER.
  - [S24: side view of the roof, the silhouette at `t2`]
- `L25` narrator: Its arms hung UP / at the ceiling, / like that was DOWN.
  - [S25: its arms along its body pointing at the roof, sleeves dark against the lilac dust]
- `L26` narrator: Its mouth / curved DOWN / in a FROWN.
  - [S26: closer on its upside-down face in rim light: the mouth curve reads as a frown, eyes bright]
- `L27` narrator: Mum asked / to hold my ROPE.
  - [S27: back on the floor, Mum standing by her bench holding out the rope end, laid over her forearm (no grip)]
- `L28` narrator: I said NO. / I didn't want her / watching me FALL.
  - [S28: my face, a small shake of the head. 1.2 s]
  - [S28b: me turning to the wall, Mum behind me lowering her arm]

### 06 Thursday three (0:51 to 1:00)

- `L29` narrator: The third THURSDAY / she'd moved her BENCH / right under my ROUTE.
  - [S29: wide, Mum on her bench now on the mat under my route (`t3` spot), flask beside her]
- `L30` narrator: I came off / at the TOP.
  - [S30: me coming off the top hold]
- `L31` narrator: It was one hold / from the EDGE, / right over ME.
  - [S31: straight up my route from my position: the silhouette at `t3`, directly above]
- `L32` narrator: I could hear it / BREATHING, / FAST.
  - [S32: close on me hanging, listening, eyes up. Soft fast breathing in the mix]

### 07 Thursday four, the scare (1:00 to 1:13)

- `L33` narrator: The fourth THURSDAY, / at the top HOLD, / the lamps went OUT.
  - [S33: over my shoulder at the top hold, 1.2 s. Cut to S33b: wide of the hall from below as the lamps ramp down over 0.7 s]
- `P01` pause: 0.7 s. No word. The hall in window blue, a lamp chain ticking.
- `L34` narrator: Only the BLUE / from the WINDOWS.
  - [S34: me at the top in blue, the arched windows behind]
- `L35` narrator: My foot SLIPPED.
  - [S35: me coming off in the blue, the rope snapping straight]
- `L36` narrator: Something BREATHED / right in front / of my FACE.
  - [S36: close on my face in blue, dark space in front of me. The music drops for 0.7 s before S37's hit]
- `L37` narrator: Its face / was level / with MINE.
  - [S37: two-shot side on in blue: its upside-down face (Mum at `lip`) and my face level, a hand's width of air between. The hit]
- `L38` narrator: A hand's width AWAY. / Its eyes were WET.
  - [S38: its face from my eye-line, key from below, blue rim, the smile reading as a frown, the eye highlights the brightest thing in frame]
- `L39` narrator: I shut my EYES / the whole way DOWN.
  - [S39: my face, eyes shut, sliding down out of frame in the blue]
- `L40` narrator: The lamps came BACK / as I touched the MAT.
  - [S40: PLANT 5. Wide from the hall: my shoes on the mat as the lamps ramp up over 0.6 s. At the frame edge, Mum's bench (`lip` spot), Mum on it, the amber ring under it fading out]

### 08 The reveal (1:13 to 1:27)

- `L41` narrator: Mum was on her BENCH, / white as CHALK.
  - [S41: Mum on the bench in full lamp light, pale, still, flask in her lap, breathing fast]
- `L42` narrator: The SOLES / of her shoes / were LILAC.
  - [S42: low close on her crossed ankles, the soles of her shoes powdered lilac]
- `L43` narrator: I looked UP.
  - [S43: my face, looking up]
- `L44` narrator: Two SHOE PRINTS / in the lilac DUST, / right over her BENCH.
  - [S44: THE PICTURE. Straight up at the roof's underside above the bench: two clear sole prints in the lilac dust, well lit]
- `P02` pause: 0.6 s. No word. Hold on the prints.
- `L45` narrator: When I FALL, / Mum goes UP.
  - [S45: two-shot, Mum on the bench, me standing beside her, both looking at each other]
- `L46` narrator: All the way UP. / Every TIME.
  - [S46: from below, the roof and its lilac dust, empty, the prints at the lip]
- `L47` narrator: She said, / "I didn't want you / to stop CLIMBING."
  - [S47: Mum's face, a small sorry smile]
- `L48` narrator: Upside DOWN, / her SMILE / looks like a FROWN.
  - [S48: a cut back to S38's blue face, 0.9 s. Then S48b: Mum's face on the bench in warm light, the same smile the right way up]

### 09 Halfway (1:27 to 1:35)

- `L49` narrator: The next THURSDAY / Mum held my ROPE.
  - [S49: Mum in the navy harness, the rope through her device, laid over her forearm (no grip), bright lamps]
- `L50` narrator: At the TOP / I let go / on PURPOSE.
  - [S50: me at the top hold, hands opening, face calm]
- `L51` narrator: She went UP / as I came DOWN.
  - [S51: wide, the rope through the anchor: me dropping, Mum lifting off the mat on the other strand, amber ring under her start spot]
- `L52` narrator: That's all / a BELAY is.
  - [S52: Mum rising, her eyes shut tight, then opening]
- `L53` narrator: And HALFWAY / up the wall, / we MET.
  - [S53: THE ENDING SHAPE. Me and Mum hanging side by side halfway up the wall on the two strands, face to face, both the right way up. Bright, floodlit]
- `L54` narrator: The right way UP. / She was SMILING.
  - [S54: close on Mum's face, a wide smile, bun swinging]

### 10 The loop (1:35 to the cut)

- `L55` narrator: In this TOWN, / when you FALL, / the one who LOVES you most / goes UP.
  - [S55: wide from the mats, the two of us hanging halfway, the amber ring glowing on the mat below. 1.4 s]
  - [S55b: Mum and me laughing, close, to the end of the line]
- `L56` narrator: So next time you FALL, / look UP.
  - [S56: straight up at the dark underside of the roof, lamps out of frame, only the lilac dust and the old prints in cold blue rim light. The creak lands under "UP". Tail 0.25 s, loop cut to S01]

## Where the plants appear

| Plant | Lines and shots |
|---|---|
| Mum's fear of heights | L06 (S06), L32, L38 ("eyes were WET"), L41 ("white as CHALK"), S52 |
| The bun hanging like a weight | L17 (S17), every bench shot |
| Bench nearer each week | S21, S29 (L29), S40, S41 |
| Lilac dust on Mum | L22 (S22), L42 (S42) |
| The frown that's a smile | L26 (S26), S38, paid at L48 |
| Empty bench and amber ring | S19, S40 (never narrated) |
| "I never look DOWN" | L12 |
| The slow lower | L19 |
| Lore: two lilac strokes on the anchor | S14b, 1.4 s, not narrated |

## Say-it-out-loud notes

- **L01:** quick and bright, a fun fact. "UP" lands by about 2.7 s.
- **L03, L04:** played for the laugh. A beat of timing before "MUM".
- **L10, L11:** plain. It's the line a rewatch hears differently ("SEEN").
- **L17, L18:** quieter. L18 is a real question.
- **L33 to L39:** slower and quieter, line by line. L36 is the quietest line in the film. L37 clipped, on the hit.
- **L45:** even, never pushed. It's the twist.
- **L47:** my voice telling it, a tiny lift on the quote, no character voice.
- **L55:** warm, the same words as L01.
- **L56:** flat and low, not a whisper. Don't trail off after "UP".
- **Mishear watch:** "BELAY" and "delay", "METRE" and "meter" (same sound, the caption uses METRE), "SOLES" and "souls". If Whisper hears the wrong one, slow the line, never add a gap.

## Packaging checks (hard rule 8)

Title, description, pin and every caption checked: no em or en dashes, no semicolons, no "not just X but Y", no "no X, no Y", no three-beat slogans, no lists in parentheses, no AI words, no emoji. No game or toy names, no claim it's true, nothing aimed at kids, no ages on screen, no death words. The title states the rule and doesn't give away who goes up.
