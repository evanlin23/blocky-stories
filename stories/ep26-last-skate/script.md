# ep26-last-skate: the script (writer, 2026-11-02)

- **Slug:** `ep26-last-skate` (folder `stories/ep26-last-skate/`). Pitch #10 in `stories/ideas.md`, written in a parallel batch, so the upload order is the owner's.
- **Working title:** see `package.json`. A statement, no imperative, and it doesn't spoil Pop.
- **Target length:** 2:15 to 2:30 final, never over 3:00.
- **Word count:** 628 spoken words in 72 lines, all `narrator`, voice A, plus 2 pause beats (1.5 s in all).
- **Estimated length:** about 2:17 to 2:26. At 290 wpm the speech alone is about 2:09. The gaps between lines add about 9 s, the pause beats 1.5 s and the loop tail 0.25 s. If the retime lands under 2:15, add the spare line after L68 ("The FANS / kept TURNING, / slow as THEM."). If it lands over 2:30, cut L44 (the warm chips) first, then L09.
- **Opening rewrite (owner's rule-first decision, 2026-11-02):** L01 to L04 are new, L05 to L07 are gone, L19b and L74 are new. L08 to L10 and everything after stay, with L18, L20, L45, L54, L56, L64 and L72 synced to the builder's current text. The dedication now first comes at L54, as the first eerie use of the rail.

## Premise
At this rink, slow songs are couples only and everyone else waits at the rail. On its last night before it shuts for good, I take Nan and Pop back to where they met. Pop says his knees are done and sits at the snack bar, so Nan waits at the rail alone through every slow song. Each time the slow spotlight comes round, a Skater in faded cherry-and-cream stripes, with legs and arms that bend twice like a folding chair, stands nearer to her.

## The rule
L01 says it: "At this RINK, slow songs are COUPLES ONLY. Everyone ELSE waits at the RAIL." (14 words). Anyone without a partner waits at the rail. The marker is a cherry ribbon loop tied between each couple's near wrists (see 01). (The Skater keeps that count: a couples skate is built for pairs, and Nan alone at the rail is half of one.)

## The twist
The dedication was Pop's. He asked Lenny in the booth for their song, the one they met to, and he's spent six months of Tuesdays relearning to skate in secret. On the last skate he rolls out of the hire-counter door, wobbling, and holds out his hand to Nan, and when the spotlight comes round again the Skater is gone. It had been standing where he should have been. The first line's rule ("Everyone ELSE / waits at / the RAIL") reads at first as the reason Nan is alone and something stands with her. By the end it turns over: the Skater was keeping the couples count at the rail, and the last lines say there were two of them, and for once nobody waited at the rail. "The couple by the rail" (first heard at L54) turns from "who is the other one?" into Pop's dedication.

- **Plant 1 (L13 to L14):** Pop's knees, strapped in thick white tape. He says they're done, so it reads as bad knees. On a rewatch it's skating support.
- **Plant 2 (L25 to L27):** Pop thanks the man in the booth by name, "Cheers, LENNY," though he says he hasn't been here in forty years. Asked how he knows, he says it's on his shirt. The shirt in the shot is plain cherry with no name and no text (the set is text-free anyway).
- **Small extra (L33, L43):** he keeps checking his watch, and then his stool is empty with his chips still warm.

## World
An old roller rink on a hot summer evening, its last night. A maple floor polished to honey, a waist-high padded rail in cherry red with cream posts, cherry-and-cream stripes painted round every wall, three big ceiling fans turning slowly, the double doors propped open on a teal dusk. A snack bar with chrome stools and an amber lamp, a hire counter with a wall of wooden cubbies full of skates, and a raised DJ booth with one soft lamp. No glitter ball. The only moving light is one soft spotlight that creeps round the floor on slow songs. No text anywhere: no signs, no names on shirts, no logos on skates or cups.

## Cast (all adults, nobody young, nobody in peril)
- **me** (`me`, adult): Nan and Pop's grown grandchild. Teal short-sleeve shirt, block hair, our own face. I skate the fast songs and sit with Pop for the slow ones. No on-screen age.
- **Nan** (`nan`, adult, old): small, silver bob, a lilac blouse, white rink skates. Quiet and happy, and she watches the snack bar.
- **Pop** (`pop`, adult, old): broad, bald with a white fringe, a short-sleeved check shirt and cream shorts, so the knee tape shows. Cheerful. He's no guide and explains nothing.
- **Lenny** (`lenny`, adult): the man in the booth, middle-aged, headphones round his neck, a plain cherry shirt with no name. Seen only in the booth.
- **Other skaters** (adults only): four or five couples on the floor, background, gone by the last skate.

## The creature, the Skater (one model, built once in `set.py`, posed per shot)
- **Looks:** our blocky body, but every leg has two knees and every arm two elbows, so at rest it stands folded in zigzags like a folding chair, about a head taller than Pop when straight. Faded cherry-and-cream rink stripes, the same stripes as the walls but sun-faded almost to pink. Old cream rink skates with cherry wheels. Its head is our rounded cylinder with a smooth cream oval face: two dark painted eyes with a single small highlight each, and a thin painted smile that never changes. No hair. Not pale grey.
- **Never seen moving.** It's only nearer each time the spotlight comes back round. Its head turns and its arm reaches only between light passes.
- **Continuity, beat by beat:**
  - L21 to L24 (slow song 1): on the far rail across the floor, legs folded twice, arms folded flat against its stripes, face toward the floor. Gone at L24.
  - L28 to L31 (slow song 2): standing still in the middle of the floor while couples skate round it, arms folded at two elbows each, face toward Nan.
  - L35 to L41 (slow song 3): at the rail one post from Nan, body facing her. At L41 its head is turned all the way round over its back, looking at me at the snack bar.
  - L48 to L53 (last skate): right beside Nan at the rail, one arm held out to her, folded twice, the hand at the end of the sleeve (show the hand, never a long beam toward camera), head facing her again.
  - L64 to L66: gone. The rail post where it stood is empty.
- **Test still first:** the L49 to L50 frame, phone size. Key from below and to the side from the rail lights, front light dead, a cherry rim from the booth. Its eye highlights are the brightest thing in frame. If it reads silly (a toy deckchair), deepen the shadow under the folds and make the second joints sharper.

## Palette, captions, music
- **Palette:** honey maple, cherry red, cream, teal dusk through the doors, amber snack-bar lamp, the spotlight a warm soft white kept under clipping.
- **Caption key colour:** spotlight rose `#ff5f7e`.
- **Music:** all synthesized in `blocky/sound.py`, our own melody, no music box. The fast songs are a bright rink organ in D major at 132 bpm, heard under 02 and between slow songs. The slow songs are a soft organ-and-pad waltz in F Lydian, 3/4 at 72 bpm. "Their song" at the last skate is the same waltz motif, warmer, with a held low note under it. The fans give a low, slow whoosh in the ambience all night.
- **Drops (`music_drops`):** P01 (0.8 s, before the head reveal at L41 lands) and P02 (0.7 s, after the arm at L50). Voice and the hit only.

## Flash plan (for the builder)
Every light change is a slow ramp. Plan it so `python -m blocky flash` has nothing to find.
- **The spotlight sweep is slow:** one lap of the floor takes about 8 s, a soft-edged pool that crosses the frame over at least 1.5 s. It never pops on. When it "comes back round" in a shot, it slides in from the edge.
- **Slow songs dim the room over 1.2 s** and come back up over 1.5 s. The last skate dims lower, over 2 s.
- **No glitter ball, no strobe, no chase lights, no flicker** on any practical (this story overrides the house habit of flickering practicals). The snack-bar lamp, the booth lamp and the neon-style cherry tube over the hire counter are steady soft glows.
- **Red light counts:** the cherry tube and the cherry rim on the Skater stay steady and low-saturation. Never ramp a saturated red area faster than 2 s.
- **Cuts between a dim shot and a bright shot** (snack bar to floor) are planned at similar exposure, or join with a 6-frame dissolve.
- Pre-check flash on S21 to S25, S42 to S44 and S47 to S56 at the final's own frame steps.

## The twist, and the last 15 seconds
L66 to L74 replay the dedication over the overhead wide: two old skaters alone on the honey floor, the spotlight round them, the rail empty all the way round. The first line said everyone else waits at the rail. The last line says that for once nobody did, and it loops straight back into the rule over shot 1's line of singles. A rewatch catches the knee tape, "Cheers, LENNY" with the plain shirt, the watch, and the empty stool.

## The one lore connection (plain tally, touches no thread)
At the hire counter (shot under L10 to L11), the end cubby of the bottom row holds one pair of skates far too long for anyone, cherry red, laces still tied in their factory bows. Pressed into the heel leather of the near skate is a plain tally of two short upright strokes, a shade darker than the leather. Held 1.2 s, never narrated, never seen again. Two strokes for a pair, no extra stroke. It names no Keeper, Maker or Bench and points at no other story.

## Shot plan and narration

Each line gives the id and who says it, then the caption chunks split with ` / `. CAPS are the key words in `#ff5f7e`. Every line is the narrator's, voice A. Pause beats give a length and their big word, or none.

## 01 The rule (opening, one forward timeline, no backstory before 0:20)
- **Where:** the rink in warm, readable light at the start of a slow song, then the drive, then inside. Shots 1 to 10. The first 2 s are lit to read, with the rule marker and Nan's face in frame. Nothing dark until slow song one.
- **The rule marker (ours, no text):** every couple on the floor wears one short cherry ribbon loop tied between their near wrists, so the pair is joined at the wrist and nobody grips. Anyone without a partner has bare wrists and stands at the rail. In shot 1 the floor is full of ribbon-joined pairs, and the singles stand in a line along the rail.
- `L01` narrator: At this RINK, / slow songs are / COUPLES ONLY. / Everyone ELSE / waits at / the RAIL.
  - [shot 1, lit warm, the spotlight soft and not yet moving: the floor full of couples gliding, each pair joined by a cherry ribbon loop at the wrist. In the foreground at the rail, Nan's face, `soft`, smiling, her wrist bare. Cut on "Everyone ELSE" to a slow track along the line of singles at the rail]
- `L02` narrator: Tonight was / the rink's LAST night. / Then it SHUTS / for GOOD.
  - [the rink from outside at dusk, doors propped open, warm light spilling on the teal evening. A stack of folded chairs and a few taped boxes by the door, no text on any of them]
- `L03` narrator: I brought / my NAN / and my POP.
  - [the three of us coming in through the doors, Nan's arm through Pop's, Pop fanning her with his free hand]
- `L04` narrator: I drove them DOWN, / with the windows OPEN. / Nan held / Pop's ARM / the whole WAY.
  - [in the car at dusk, windows down: me driving, and in the back Nan's arm through Pop's, her head on his shoulder. Then back to the doors]
- `L08` narrator: The big FANS / were turning, / and the floor / SMELLED of WAX.
  - [low under the ceiling fans turning slowly, then down to the shine of the floor]
- `L09` narrator: CHERRY / and CREAM STRIPES / on every WALL.
  - [a slow pan along the painted stripes]
- `L10` narrator: At the / hire COUNTER, / Nan asked / for SKATES.
  - [Nan at the counter, the cubby wall behind. Then the lore shot: the bottom-row end cubby, the far-too-long cherry skates, laces in their bows, the two-stroke tally on the heel. Held 1.2 s, no line about it]

## 02 The last night
- **Where:** the hire counter and the snack bar. The rink organ at 132 bpm.
- **Plant:** the knee tape (L13 to L14).
- `L11` narrator: Pop asked / for NOTHING.
  - [Pop beside her, shaking his head, smiling]
- `L12` narrator: He sat down / at the SNACK BAR, / on a chrome STOOL.
  - [Pop settling on a stool under the amber lamp]
- `L13` narrator: Both his KNEES / were STRAPPED up / in thick white TAPE.
  - [close on his knees below the cream shorts, the tape wound thick]
- `L14` narrator: He said, / "These knees / are DONE, love. / You skate for / BOTH of us."
  - [Pop to Nan, `grin`. Nan's face, `soft`]
- `L15` narrator: Nan just SMILED, / and rolled off / to the RAIL.
  - [Nan from behind, gliding to the rail, small and steady]

## 03 Slow song one: the far rail
- **Where:** the floor dimmed for a slow song, seen from the snack bar. Shots 16 to 25. The waltz comes in.
- `L16` narrator: Every half HOUR, / the lights / went DOWN / for a SLOW song.
  - [the room dims over 1.2 s. The organ fades into the waltz]
- `L17` narrator: Couples ONLY.
  - [two couples gliding past hand in hand, seen at the elbows, cut away before any grip]
- `L18` narrator: One soft SPOTLIGHT / crept ALONG / the floor, / slow as / a CLOCK.
  - [high wide: the soft pool travelling round the floor]
- `L19` narrator: Nan waited / at the RAIL, / ALONE.
  - [Nan at the rail, bare wrist on the rail, the ribbon-joined couples passing in front of her]
- `L19b` narrator: Fifty years AGO, / she met Pop / at that same RAIL.
  - [hold on Nan at the rail in the pool's edge, looking toward the snack bar, `soft`]
- `L20` narrator: I sat beside / POP, with a / tub of CHIPS.
  - [me and Pop at the snack bar, the tub between us]
- `L21` narrator: When the light / reached the FAR wall, / someone was / STANDING there.
  - [the pool sliding along the far rail, then onto a tall striped shape]
- `L22` narrator: A SKATER, / in faded CHERRY / and cream STRIPES, / like the WALLS.
  - [medium on the Skater at the far rail, face toward the floor]
- `L23` narrator: Each LEG / had TWO KNEES, / and they FOLDED / like a folding CHAIR.
  - [side view of its legs, the two bends, a hard shadow under each]
- `L24` narrator: The light / moved ON. / When it came BACK, / the far rail / was EMPTY.
  - [the pool slides away, the room passes, the pool returns to the far rail: nothing there]

## 04 Lenny
- **Where:** the snack bar between songs, full light, the organ back. Shots 26 to 28.
- **Plant:** "Cheers, LENNY" and the plain shirt.
- `L25` narrator: Pop waved / at the BOOTH / and said, / "Cheers, LENNY."
  - [Pop waving up at the booth. Lenny waves back, `grin`]
- `L26` narrator: Pop said / he hadn't been HERE / in forty YEARS.
  - [my face, `puzzled`]
- `L27` narrator: I asked him / how he knew / the man's NAME. / He said, / "It's on his SHIRT."
  - [Pop shrugging. Then a quick shot of Lenny in the booth: a plain cherry shirt, nothing on it]

## 05 Slow song two: the middle
- **Where:** the floor dimmed again, from the snack bar. Shots 29 to 35.
- `L28` narrator: Next slow SONG, / the spotlight / came ROUND again.
  - [the dim, the pool sliding in from frame edge]
- `L29` narrator: The Skater / was in the MIDDLE / of the floor.
  - [high wide: the pool on the Skater standing dead centre]
- `L30` narrator: Each ARM / had TWO ELBOWS, / folded flat / on its STRIPES.
  - [medium on its folded arms, the zigzag dark against the cream stripes]
- `L31` narrator: And its FACE / was turned / toward NAN.
  - [its cream oval face, painted smile, eyes toward the rail. Reverse: Nan at the rail, unaware]
- `L32` narrator: I told POP. / He didn't even / LOOK UP.
  - [me pointing, Pop eating a chip]
- `L33` narrator: He just kept / checking his WATCH.
  - [close on Pop's wrist and the watch face, plain, no numbers]

## 06 Slow song three: one post away
- **Where:** the rail by Nan, from the snack bar and then closer. Shots 36 to 46.
- **The scare builds:** P01 is the music drop before the head.
- `L34` narrator: By the THIRD / slow song, / I couldn't EAT.
  - [the chip tub untouched, my face, `worried`]
- `L35` narrator: The spotlight / crept ROUND, / one board / at a TIME.
  - [low on the floor boards as the pool edges across them]
- `L36` narrator: The Skater / was at the RAIL. / ONE POST / from Nan.
  - [wide along the rail: Nan, a cream post, then the Skater, folded, facing her]
- `L37` narrator: Up close, / its STRIPES / were faded / almost to PINK.
  - [close on its sleeve stripes in the pool's edge]
- `L38` narrator: Its face / was a smooth / cream OVAL, / with two dark EYES / and a painted SMILE.
  - [its face, the eye highlights the brightest thing, key from below]
- `L39` narrator: Nan didn't TURN. / She was watching / the snack BAR.
  - [Nan's face, looking past camera toward us]
- `L40` narrator: The light / slid OFF it, / and back AGAIN.
  - [the pool slides away, black, then slides back on the same post]
- `P01` pause 0.8 s: none
  - The drop. Voice and hit only, the waltz gone.
- `L41` narrator: Now its HEAD / was turned / ALL the way ROUND, / over its BACK.
  - [the Skater's body still faces Nan, but its head faces us over its own back, its painted smile toward us]
- `L42` narrator: Looking / at ME.
  - [my face, `terrified`]
- `L43` narrator: I looked / at POP. / His stool / was EMPTY.
  - [the chrome stool beside me, empty, the amber lamp over it]
- `L44` narrator: His CHIPS / were still WARM.
  - [close on the tub, steam faint and slow]

## 07 The last skate (the scare)
- **Where:** the rink at its darkest, the spotlight on the rail. Shots 47 to 56. The dim is over 2 s.
- `L45` narrator: Then the speaker / said, / "LAST SKATE."
  - [the booth lamp, Lenny at the mic]
- `L46` narrator: The lights / went down / LOWER than BEFORE.
  - [the slow 2 s dim on the wide]
- `L47` narrator: Everyone ELSE / rolled off / the FLOOR.
  - [couples gliding off through the gaps in the rail, leaving the floor bare]
- `L48` narrator: The spotlight / found NAN, / alone at the RAIL.
  - [the pool settling on Nan]
- `L49` narrator: And the Skater / was RIGHT / BESIDE her.
  - [the pool widens and the Skater is in it, at her shoulder, a head taller]
- `L50` narrator: Its ARM / was held OUT, / folded TWICE, / like a partner / ASKING / for a DANCE.
  - [the test-still frame: its arm out to her, two bends, the hand at the end of the sleeve, cherry rim]
- `P02` pause 0.7 s: none
  - The second drop. The hit lands as Nan's eyes go to the hand.
- `L51` narrator: Nan LOOKED / at the hand.
  - [Nan's face, `soft`, eyes down to the hand]
- `L52` narrator: And she started / to lift HERS.
  - [Nan's hand rising from the rail, a hand's width from its hand. Hold]
- `L53` narrator: I tried / to SHOUT, / but the music / swelled UP / over me.
  - [me at the snack bar, `terrified`, standing, the waltz swelling warm]
- `L54` narrator: Then the voice / on the SPEAKER / said, "This one's / for the COUPLE / by the RAIL."
  - [the booth: Lenny at the mic, smiling, looking toward the hire counter]

## 08 Pop
- **Where:** the hire-counter door, then the floor, the spotlight on them. Shots 57 to 69. Their song, warmer, the low note under it.
- **The warm turn is all picture.** No line says he loves her.
- `L55` narrator: The door / by the hire COUNTER / swung OPEN.
  - [the door, warm light behind it]
- `L56` narrator: Out rolled / POP.
  - [Pop in the doorway on old brown skates, arms out]
- `L57` narrator: On SKATES.
  - [close on his skates on the honey boards]
- `L58` narrator: WOBBLING, / arms OUT, / knees in their / white TAPE.
  - [Pop coming across the floor, wobbling, `grin`, the tape on his knees]
- `L59` narrator: It was THEIR song. / The one / they MET to.
  - [Nan's face, `wide`, then softening]
- `L60` narrator: He'd ASKED / for it.
  - [my face, `wide`, putting it together]
- `L61` narrator: Lenny leaned out / of the BOOTH / and called, / "Six MONTHS / of TUESDAYS, / mate!"
  - [Lenny leaning out, `grin`, thumbs up shown as a raised sleeve]
- `L62` narrator: Pop had been / LEARNING / AGAIN. / In SECRET.
  - [Pop, wobbling, steady for one second, proud]
- `L63` narrator: He rolled UP / to the rail, / and held out / HIS hand.
  - [Pop at the rail, his hand out to her. Cut away before the hands meet]
- `L64` narrator: The spotlight / circled THEM.
  - [the pool sliding round the pair, slow]
- `L65` narrator: And the Skater / was GONE.
  - [the post beside them, empty, in the pool's edge]
- `L66` narrator: It had been / STANDING / right where / POP / should have BEEN.
  - [wider: Pop standing in exactly that place, Nan beside him]

## 09 Two of them
- **Where:** the floor, then the overhead wide. Shots 70 to 76. The ending shape: an overhead wide of two old skaters alone on the floor, the rail empty all the way round.
- `L67` narrator: Nan LAUGHED, / and it sounded / fifty years YOUNG.
  - [Nan laughing, `laugh`, Pop laughing with her]
- `L68` narrator: They went round / SO SLOWLY.
  - [low tracking: the two of them gliding, sleeve to sleeve]
- `L69` narrator: Pop WOBBLED. / Nan held him STEADY.
  - [Pop tipping a little, Nan's arm at his elbow, cut on the steadying]
- `L70` narrator: Every lap, / he said / "SORRY," / and every lap / she said, / "AGAIN."
  - [the pair coming past the snack bar, laughing]
- `L71` narrator: I watched / from the snack BAR, / on Pop's STOOL.
  - [me on the chrome stool, chin on my hand, `soft`]
- `L72` narrator: The voice / on the SPEAKER / said, "This one's / for the COUPLE / by the RAIL."
  - [crane up to the overhead wide: two old skaters alone on the honey floor in the spotlight, the rail empty all the way round]
- `L73` narrator: There were / TWO of them.
  - [hold the overhead wide, the fans turning slowly at frame edge]
- `L74` narrator: And for ONCE, / NOBODY / waited at / the RAIL.
  - [the overhead wide holds: the rail empty all the way round, the two of them below in the spotlight, joined at the wrist by one cherry ribbon loop (if that's cheap to add to the L67 to L74 shots, otherwise leave their wrists as they are). The waltz's low note falls in pitch and the fans keep turning. 0.25 s after the last word, cut back to shot 1's line of singles at the rail]

## Notes for the builder and standards
- **The rule marker (new with the opening):** a short cherry ribbon loop tied between the near wrists of every couple on the floor during slow songs, our own prop, no text. Singles have bare wrists and stand at the rail. It must read in shot 1 by 2 s, lit warm, with Nan's face in frame. Cheapest build: one ribbon mesh parented between two wrists, reused per couple. It's needed in the L01, L16 to L19b and L28 to L31 floor shots. It's optional on Nan and Pop from L67 on. The Skater never wears one.
- **Whisper-risky words, kept on purpose:** "Lenny" (a plain name), "fifty", "forty" and "Six" (Whisper may write digits, so normalize numbers in the check), "Tuesdays", "Nan". Avoided: "DJ" (could come back as "deejay" or "D.J."), "deckchair" (one word or two), any brand.
- **Checks words:** no death words, no harm words (no "fell", "lost", "grab", "took", "pulled"), no child words. Pop's knees are "done", never anything worse.
- **Rig limits:** no hand ever grips. Hands meeting are cut away (L17, L63, L69). The Skater's held-out arm shows the hand at the end of the sleeve, side-on, never foreshortened toward camera. The Skater's double joints need new pose keys in `set.py`, its own model only, nothing shared.
- **Reported speech:** Pop (L14, L25, L27), Lenny (L61) and Nan (L70) are quoted in my narration. Nobody has a voice of their own. The speaker's lines (L45, L54, L72) are mine too, read as reported speech.
- **Spare line for length:** after L68, "The FANS / kept TURNING, / slow as THEM."
