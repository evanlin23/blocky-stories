# ep24-wash-cycle: the script (writer, 2026-11-02)

- **Slug:** `ep24-wash-cycle`
- **Working title:** The dryer nobody started had a warm coat inside (the packager may change it, never to an imperative or a spoiler).
- **Pitch:** #8 `wash-cycle` in `stories/ideas.md`. Setting, creature, first-line type and kind of warmth are kept.
- **Target length:** 2:15 to 2:30.
- **Word count:** 638 spoken words in 77 lines, all `narrator` in voice A, plus 3 pause beats (P02 0.9 s, P01 0.7 s, P03 0.8 s).
- **Estimated length:** about 2:19 to 2:25. At 290 wpm the speech is about 2:10. The 0.12 s gaps add about 9 s, P01 0.7 s and the loop tail 0.25 s. If the retime lands under 2:15, add back "I read the same PAGE / TEN TIMES." after L31. If it lands over 2:30, L43 goes first, then L74.
- **Shots:** 77 (S01 to S77). The S numbers in the plan below are the beats, not the build's ids: the build (`generator/make_story.py`, `story.json`) splits some beats into several cuts, and the sections give each one's true count.
- **Name change:** the pitch's "Mr Amadi" is now **Arthur**, and he has no name at all until L68. "Amadi" risks Whisper spellings, and "Mr." reads as "mister" in Kokoro but comes back "Mr." from Whisper, which `asr` counts as a wrong word. "Arthur" is a common word in Whisper's training and Kokoro says it plainly. Until L68 he's "the old man".
- **Metrics:** `metrics/summary.md` (2026-11-01) has one row, ep11, with every number "?", so there are no lessons to apply yet. The script follows RULES.md as written.

## Premise, rule, twist, world

- **Premise:** my washer breaks in the first freeze, so I take my wash to an all-night laundromat and sit at the long folding table behind a row of six orange chairs. The first night I come in soaked, a dryer I never used buzzes, and inside is a warm green wool coat in my size. I wear it all week. From the second night a person built backwards sits in the chairs with its back to me and its face on the back of its head, one chair nearer each night. I think it wants the coat back.
- **The rule (felt, never stated):** the six chairs are a count. When one of them should be filled and isn't, something fills it.
- **Twist:** the coat belongs to the quiet old man at the far end, the only other person there on the first night. He put it in the dryer while I was at the change machine, then sat in a jumper all week so I wouldn't ask, and caught a cold. On night four his chair is empty, and the Turned sits in it and then leans its face to mine: its eyes go from the coat to his chair and back, counting. A "stranger's" coat was a neighbour looking after me.
  - **Plant 1 (L09, again at L36):** on a freezing night he wears only a grey jumper.
  - **Plant 2 (L18, again at L38):** the coat smells of lavender soap, and so does his chair. I put it down to the soap the shop sells (L39).
  - **Plant 3, picture only (L13):** in the wide behind me, the old man is no longer at his towels but walking back to them from the dryers. Unnarrated.
  - **How the last 15 seconds turn the first line:** the last line repeats L01 with one word changed, "a FRIEND's COAT". On a rewatch L01's "stranger" is wrong from the first second: the man ten feet away was giving it to me.
- **World:** a narrow all-night laundromat on a wet corner. Cream wall tiles, a chequered grey floor, a wall of twelve steel front-loaders, a row of six bolted orange plastic chairs facing six round dryer doors, a long pale wood folding table behind the chairs, a coat hook by the glass door, a change machine and a soap machine with blank coloured buttons, long fluorescent tubes. Outside, rain on black glass and a side door to stairs up to the flat over the shop. No text, logos or numbers anywhere.
- **Kind of warmth:** gratitude. I thank the man who looked after me.
- **Ending shape:** the coat handed back folded on top of his wash at his door, then two coats on the hook by the laundromat door and the towels passed across the folding table.

## Cast

- `me`: the narrator, an adult (`age: adult`). Dark brown block hair, a round face with thick black brows, a rain-soaked mustard hoodie (night one), then the green coat over it. Never in peril, never touched.
- `arthur`: an older adult (`age: adult`). Short white block hair, a white moustache, a round face with small kind eyes, a grey cable-knit jumper and brown trousers. A plaid scarf only at his door (L63). He never speaks aloud. His reported lines are in my voice (L66, L67). He has a cold, nothing worse, and he's never shown hurt.
- The Turned is a set object, not cast.

## The creature: the Turned

- **Look:** an R6 blocky person built backwards, slightly too broad in the shoulders (1.25x). Everything that should face front faces back: the overall bib and its two buttons are on its back, its shoes point heels-forward, its elbows bend the wrong way, and its face is drawn on the back of its head under the hairline. The front of its head is the back of a neat brown haircut. Overalls in laundry blue `#3f7fd0`, a white T-shirt, black shoes. The face: two wide round eyes with thick black strokes and small hard highlights, no brows, a small flat mouth. Never seen moving.
- **Light:** front tubes over its row ramp down a little in its shots. A cool rim from the dryer glass, a low warm key from the dryer windows below (amber `#d79a52`, never red). The eye highlights are the brightest thing.
- **Pose:** it sits in a chair facing the dryers like anyone else, so its back, and its face, are toward me at the table. Its head tips back a little so the face looks over the chair back.
- **Continuity:**

| Lines | Where | What it's doing |
|---|---|---|
| L01 to L18 | not there | the chairs are empty but for the old man in chair six |
| L19 to L27 | chair five, beside the old man | sitting, face over the chair back, on me |
| L28 | chair five | the same, small in the wide as I leave |
| L29 to L39 | chair four | one chair nearer. At L34 its eyes are on the hook where the coat hangs |
| L41 to L44 | chair six, the old man's | the farthest it's been, face on me |
| L45 to P01 | chair six, then dark | the tubes ramp down over one held shot. In the near-dark it's a shape |
| L48 to L58 | chair one, against the table edge | its head tipped back over the chair back, its face an inch from mine. Eyes go down to the coat (L51), to chair six and back (L53) |
| L59 | chair one | it stays sitting as I stand. It never follows |
| L69 to L76 | gone | the chairs are just chairs |

- **Test still:** L48, phone size: its upside-down face filling the top half of frame, my face in the lower third, the green collar between. Iterate until it frightens.

## Look and sound

- **Palette:** cold cream tube light, chequered grey, brushed steel, chair orange `#e2742b`, laundry blue `#3f7fd0`, coat bottle green `#2f5d43`, jumper grey, rain black-blue outside.
- **Caption key colour:** soap lavender `#b99cf2`.
- **Music:** C aeolian, 66 bpm. A low two-note ostinato that sits on the washers' drum rhythm, a soft synth pad, the tube hum as a drone. Drops for P01. From L59 the pad moves to C major and the ostinato stops. The closing chord falls a fifth under the last line.
- **Sound:** tube hum, drum slosh, a dryer buzzer (soft square tone, 0.4 s), rain on glass, coins in the change machine, all synthesized. No samples.
- **Light changes (flash plan, after ep20's preview failed on lamp glows and red light at beat changes):**
  - Every light change is a slow ramp inside one held shot, never across a cut.
  - **The stutter (L45 to L48):** one held shot from my seat down the chair row. The tubes ramp from full to 20% over 1.0 s with a soft audio crackle (the "stutter" is in the sound only, the picture never blinks), hold at 20% through P01, then ramp back to full over 1.0 s from the end of P01 into "When they came BACK", still on the held shot. The cut to the close-up lands on "its FACE", only after the ramp is finished, on matched exposure.
  - The dryer windows are a steady warm glow, never pulsing, never red. The change machine light is steady.
  - Cuts in the scare section match exposure on both sides. No white clipping.
  - Rain outside is soft and out of focus, no lightning.
  - Run `python -m blocky flash` on the preview over L44 to L50 first.

## The one lore connection

- **What:** a plain Keeper tally under the seat of chair four: six short upright strokes in laundry blue, one per chair, no extra stroke.
- **Where:** S31, under L31 ("Its face / didn't BLINK."), a low shot from the floor looking up at the underside of chair four's seat, held 1.5 s, not narrated. Nobody mentions it, and the pin doesn't ask about it.

## Format

Each line gives the id and who says it, then the caption chunks split with ` / `. The spoken text is the chunks in lowercase. CAPS are the key words, in soap lavender. Every line is `narrator`. Past tense, but L01 and L76 are present perfect, and L70 to L73 are present.

## 01 The coat (night one)

- **Where:** the laundromat at night, rain outside. **Shots:** 18 (S01 to S18).

- `L01` narrator: I've been WEARING / a stranger's COAT. / For a WEEK.
  - [S01: close on me at the folding table in the green coat, collar up, tubes humming. Slow push in]
- `L02` narrator: It came out / of a DRYER / that NOBODY / STARTED.
  - [S02: a round dryer door, a green sleeve behind the glass, turning slowly]
- `L03` narrator: My washer BROKE / in the first FREEZE / of the year.
  - [S03: rain on black glass from inside, the street a blur of cold light]
- `L04` narrator: So I went / to the all-night LAUNDROMAT.
  - [S04: outside the shop at night, warm windows, rain, me with a bag. No sign text]
- `L05` narrator: A row of orange CHAIRS / faces the DRYERS.
  - [S05: wide down the row of six bolted orange chairs facing six dryer doors]
- `L06` narrator: I sat BEHIND them / at the FOLDING TABLE.
  - [S06: reverse, me sitting at the near end of the table behind chair one]
- `L07` narrator: That first night, / I came in SOAKED / to the SKIN.
  - [S07: me at the door, mustard hoodie dark with rain, dripping on the chequered floor]
- `L08` narrator: There was ONE other person, / an OLD MAN / in the END chair.
  - [S08: down the row, the old man small in chair six at the far end, watching his drum]
- `L09` narrator: He had a grey JUMPER on. / That was ALL. / On a FREEZING NIGHT.
  - [S09: medium on him, grey cable-knit, no coat, the hook by the door empty behind me. Plant 1]
- `L10` narrator: He never LOOKED UP. / He never SAID / a WORD.
  - [S10: his profile, eyes on the turning drum]
- `L11` narrator: I sat there SHIVERING, / my teeth going like a DRUM.
  - [S11: me at the table, shoulders up, breath faint]
- `L12` narrator: I'd only got UP once, / for CHANGE.
  - [S12: the change machine, steady light, coins rattling down. Cut away before any hand]
- `L13` narrator: Then a DRYER / BUZZED / across the ROOM.
  - [S13: wide from behind me across the chairs to the dryers: the end dryer's light goes off. In the same wide, Arthur is walking back from the dryers to his towels at the table's far end. Plant 3, unnarrated]
- `L14` narrator: I hadn't USED it. / The old man / was FOLDING TOWELS.
  - [S14: him at the far end of the table, folding, back half to me]
- `L15` narrator: Inside was a COAT. / Dark GREEN WOOL, / still WARM.
  - [S15: the dryer door open, the green coat folded on the drum floor, a soft warm glow]
- `L16` narrator: I held it UP. / It was EXACTLY / my SIZE.
  - [S16: me holding the coat against me, the sleeve ends at my block hands]
- `L17` narrator: I asked the room / whose it WAS. / The old man / kept FOLDING.
  - [S17: two-shot down the table, him not turning]
- `L18` narrator: So I put it ON. / It smelled of LAVENDER SOAP.
  - [S18: close on me in the coat, collar to my chin, eyes closing for a second. Plant 2]

## 02 The Turned (night two)

- **Where:** the same, the next night. **Shots:** 11 (S19 to S29).

- `L19` narrator: The second night, / somebody ELSE / was in the CHAIRS.
  - [S19: from my seat, the row: the old man in six, and a broad figure in five, its back to me]
- `L20` narrator: Chair FIVE, / right next to the OLD MAN.
  - [S20: the two backs side by side, one grey, one blue]
- `L21` narrator: Laundry-BLUE OVERALLS. / BROAD SHOULDERS. / A neat brown HAIRCUT.
  - [S21: medium on the figure from behind, the tubes over it]
- `L22` narrator: But the BIB / of its overalls / was on its BACK.
  - [S22: closer, the bib and two buttons on its back]
- `L23` narrator: Its shoes / pointed the WRONG WAY, / HEELS to the DRYERS.
  - [S23: a low shot under the chairs of its heels-forward shoes beside Arthur's normal brown shoes]
- `L24` narrator: And on the BACK / of its HEAD / was a FACE.
  - [S24: slow tilt up from the collar to the face on the back of its head]
- `L25` narrator: It was LOOKING at me. / Over the back / of the CHAIR.
  - [S25: close on its face, eyes wide and still, the chair back's orange edge low in frame]
- `L26` narrator: I called it / the TURNED.
  - [S26: me at the table, not moving, coat buttoned]
- `L27` narrator: The old man / just watched his DRUM.
  - [S27: the old man's profile, calm, the face beside him on me]
- `L28` narrator: When I LEFT, / he went out the SIDE DOOR, / and UPSTAIRS.
  - [S28: outside in the rain, the old man going through a side door beside the shop to a lit stair. The Turned small through the window in chair five]
- `L29` narrator: I BUTTONED the coat / up to my CHIN.
  - [S29: me walking off in the rain, green coat, hood of the hoodie up]

## 03 One chair nearer (night three)

- **Where:** the same, night three. **Shots:** 12 (S30 to S41).

- `L30` narrator: Night THREE, / it was in chair FOUR.
  - [S30: from my seat, the row: the old man in six, five empty, the Turned in four]
- `L31` narrator: Its face / didn't BLINK.
  - [S31: its face, close, three-quarter, eyes open and fixed: the line is about what it shows]
- `L31b` narrator: I read the / same PAGE / TEN TIMES.
  - [S32: the lore plant. Low from the floor, the underside of chair four's seat: six short laundry-blue strokes. Held 1.5 s through the line, not narrated]
- `L32` narrator: ONE chair NEARER. / I never SAW it move.
  - [S32: close on its face over the chair back, a little bigger in frame than S25]
- `L33` narrator: I thought, / it wants the COAT BACK.
  - [S33: me, hand flat on the coat front]
- `L34` narrator: So I hung it / on the HOOK / by the DOOR.
  - [S34: the green coat on the hook by the glass door, rain behind]
- `L35` narrator: Its EYES / went to the HOOK.
  - [S35: its face, eyes slid toward the door]
- `L36` narrator: The old man COUGHED. / He was STILL / in just the JUMPER.
  - [S36: him in chair six, one cough into the crook of his arm, grey jumper. Plant 1 again]
- `L37` narrator: I went past his chair / for my COAT.
  - [S37: me walking behind the chairs, past chair six]
- `L38` narrator: And I smelled it AGAIN. / LAVENDER.
  - [S38: close on me beside his chair, a small turn of the head. Plant 2 again]
- `L39` narrator: I thought / it had to be the SOAP / the shop SELLS.
  - [S39: the soap machine, blank lavender and blue buttons, steady light]
- `L40` narrator: I put the coat back ON / and kept my eyes DOWN.
  - [S40: me at the table, coat on, eyes on my own drum]

## 04 Night four (the scare)

- **Where:** the same, night four. **Shots:** 17 (S42 to S58).

- `L41` narrator: Night FOUR, / the old man / wasn't THERE.
  - [S41: from the door, the row and table, chair six's place empty of him]
- `L42` narrator: The Turned / was in HIS chair.
  - [S42: down the row: chair six, the Turned in it, face on me]
- `L43` narrator: As FAR from me / as it had EVER been.
  - [S43: wide from my seat, it small at the far end, five empty chairs between us]
- `L44` narrator: I let out a BREATH.
  - [S44: me, shoulders dropping]
- `P02` pause: 0.9 s, no word.
  - [S44 held]
- `L45` narrator: Then the TUBES / began to FADE.
  - [S45: one held shot from my seat down the row. The tubes start their 1.0 s ramp down, a soft crackle in the hum]
- `L46` narrator: Down to a brown GLOW.
  - [S45 held: the room at 20%, the dryer windows a steady warm glow, the Turned a dark shape in six]
- `L47` narrator: The DRUMS / STOPPED.
  - [S45 held: every drum still. Music drops here]
- `P01` pause: 0.5 s, no word (the silence is 0.8 s with the line gaps).
  - [S45 held at 20%. Only the hum. The ramp back to full starts at the end of P01 and takes 1.0 s]
- `L48` narrator: When they came BACK, / its FACE / was an INCH / from MINE.
  - [S45 holds through "When they came BACK" while the ramp finishes, then S46 cuts in on "its FACE". Close: the Turned in chair one against the table edge, its head tipped back over the chair, its upside-down face filling the top half of frame, my face in the lower third, the green collar between. The hit lands on "INCH". The test still]
- `L49` narrator: I could see / every black LINE / of its EYES.
  - [S47: extreme close on its eyes, thick strokes, small hard highlights]
- `L50` narrator: I couldn't MOVE.
  - [S48: front three-quarter on my face, frozen, the green collar]
- `L51` narrator: Its eyes / slid DOWN / to the COAT.
  - [S48: its face, pupils clearly down; then S49: over its shoulder, my coat's buttons]
- `L52` narrator: Then over to / HIS chair, / and BACK.
  - [S50: its face, pupils sideways; S51: chair six, empty; S52: its face, pupils down again]
- `L53` narrator: Coat. / Chair. / Coat. / Like it was COUNTING.
  - [S53 coat, S54 chair six, S55 coat: three quick cuts on the three words; S56: its face, the pupils going down, sideways, down]
- `P03` pause: 0.8 s, no word.
  - [S51 held]

## 05 The coat was his

- **Where:** the same moment. **Shots:** 5 (S59 to S63).

- `L54` narrator: Then I KNEW / that LAVENDER.
  - [S52: front three-quarter on my face, eyes widening, the Turned's face still above me]
- `L55` narrator: He was the ONLY one / here that first NIGHT.
  - [S53: a soft replay of S13's wide, the old man walking back from the dryers. Slowed, slightly cooler]
- `L56` narrator: While I was at the CHANGE MACHINE, / he put his COAT / in that DRYER.
  - [S54: replay of S12 from a wider angle: the old man at the end dryer behind me, the door closing. Cut away before any hand]
- `L57` narrator: Then he sat / in a JUMPER / for DAYS, / so I wouldn't ASK.
  - [S55: his empty chair six, the jumper's grey fluff on the seat]
- `L58` narrator: And now he had a COLD, / and his chair / was EMPTY.
  - [S56: back to the Turned's face, eyes on the coat]

## 06 Gratitude

- **Where:** the laundromat, then the stair and his door. **Shots:** 9 (S64 to S72).

- `L59` narrator: I stood UP. / It didn't / FOLLOW.
  - [S57: me standing, it staying in chair one, its face turning only with my coat. Music turns to C major here]
- `L60` narrator: His wash / from NIGHT THREE / sat in the END MACHINE.
  - [S58: a front-loader, grey towels and jumpers resting in the drum]
- `L61` narrator: I DRIED it. / I FOLDED it / the way he DOES, / CORNERS FIRST.
  - [S59: me at the table folding towels, the stack neat, a slow push]
- `L62` narrator: I carried it / UP his STAIRS.
  - [S60: the side stair, warm bulb, me climbing with the stack, the coat folded on top]
- `L63` narrator: He opened up / in a plaid SCARF, / with a cold.
  - [S61: his door, Arthur in the scarf, nose pink, eyes small and surprised]
- `L64` narrator: I held out his WASH, / with his COAT / folded on TOP.
  - [S62: across the doorway, the stack between us. Cut away before any grip]
- `L65` narrator: I said, "THANK you." / Then I said it AGAIN.
  - [S63: me, close, earnest]
- `L66` narrator: He went PINK. / He said, / "You were SHIVERING."
  - [S64: him, looking at his slippers, a small smile]
- `L67` narrator: "What was I / supposed to DO?"
  - [S64 held]
- `L68` narrator: Then he told me / his name was ARTHUR.
  - [S65: a two-shot in the doorway with both faces, mine and Arthur's, warm light]

## 07 Two coats

- **Where:** the laundromat, a few nights later. **Shots:** 5 (S73 to S77).

- `L69` narrator: ARTHUR sat / in his own CHAIR again.
  - [S66: the row from my seat, Arthur in six, the other five chairs empty and plain]
- `L70` narrator: The chairs / are just CHAIRS now.
  - [S66 held]
- `L71` narrator: I pass him / his TOWELS.
  - [S67: the towels set on the table between us. Cut away before any hand]
- `L72` narrator: There are TWO COATS / on the HOOK / by the door.
  - [S68: the hook, his green coat and a new navy one beside it, rain on the glass]
- `L73` narrator: HIS, / and a new one / of MINE.
  - [S68 held]
- `L74` narrator: For a WEEK, / I didn't even know / his NAME.
  - [S68 held, slow pull back to the table, the two of us folding]
- `L75` narrator: But the whole TIME,
  - [S68 held]
- `L76` narrator: I've been WEARING / a FRIEND's COAT.
  - [S68 held. After "COAT", 0.25 s, then a hard cut to S01]

## Where it lands (for the critic)

- **The middle scare:** an escalation, never described: five, four, then the far end, then an inch away in the dark.
- **The warmth is shown:** the folding, the stair, the pink face, the coats on the hook. "Gratitude" is never said.
- **The Turned stays unexplained.** It isn't kind and isn't lonely. It counts and goes.

## Notes for the designer, sound and standards

- **Cast:** two adults. Neither is ever hurt or in peril. Arthur's cold is a pink nose and a scarf. The Turned never touches anyone or anything but its chair. At L48 its face stops a hand's width short of mine in the model (the line says an inch, the camera sells it).
- **Words:** no GRAPHIC, HARM, CHILD or TRUE_CLAIM word in `checks.py` (no "lost", "missing", "fell", "pulled", "dead"). No em or en dashes, no semicolons.
- **Batch 1 echoes avoided:** no "At the PLACE" opener, no "Last NIGHT," closing opener, no "pressed flat", no "it didn't touch me", no "not X, it was Y", no on-screen age, no pale grey creature, no night-shift narrator (I'm a customer). "Every night" and "the next night" are not used.
- **Set text:** none. The machines, buttons and change machine are blank. The shop has no sign.
- **Rig:** no hand grips. Every hand-off cuts away. Chairs are bolted, so seat spacing is 0.7 m for one sitter, not riders. Check the Turned's backwards elbows and heels in the stills for intersections with the chair.

## Say-it-out-loud notes

- **L01:** a flat confession, quick, "WEEK" landing by about 2 s.
- **"LAUNDROMAT"** (L04) is LAWN-druh-mat. Whisper may split nothing. Fine.
- **"Laundry-BLUE"** (L21) may come back "laundry blue". A spelling, not a mishear.
- **"ARTHUR"** (L68) is plain, AR-thur.
- **Homophones:** "TURNED" (L26) is said once as a name, could come back lower case, fine. "DOES" (L61) is the verb, "duz". "TOWELS" is two syllables. "STAIRS" and "stares" (L62). The number six is never spoken (the six-stroke tally stays picture only).
- **L53 "Coat. / Chair. / Coat."** Three one-word beats, each its own caption. If Kokoro runs them together, give the line `tempo` 0.95.
