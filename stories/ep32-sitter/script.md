# ep32-sitter: the script (writer, redo 2026-11-02)

- **Slug:** `ep32-sitter` (pitch #16 in `stories/ideas.md`, redone to rule first).
- **Target length:** about 95 to 105 s (the 60 to 100 s test band, at its long end). 
- **Word count:** 395 spoken words in 40 lines, all `narrator`, voice A. At 290 wpm the speech is about 82 s, plus about 14 s of line and chunk gaps, two music drops and the 0.25 s tail, so about 95 to 100 s. The reveal (L29 to L31) starts about 67 s in, so it sits in the last 25 to 30 s. If long, L20 goes first, then L35. If short, add "It sat with its HANDS / folded, / like it was WAITING." after L12.
- **Tense:** past, first person (L01 to L05 and L37 to L40 are present: how the town is, how things are now). Kofi, Petra and Mum are only ever quoted inside my lines.

## Changed for the builder (redo, 2026-11-02)
Every line is new, so re-voice everything once (old L01 to L76 are all gone, and the ids below restart at L01). Old `voice-timings.json` is stale.

**story.json text** (paste, so `check` compares the new story):
- `title`: "In This Town Your Face FADES If Nobody Looks"
- `premise`: "In a town where your face fades to bare wood if nobody looks at you, and lonely people sit for the portrait class to be painted back in, I join that class to learn to finish a face. I haven't spoken to Mum since spring. On the dais stool sits someone faded all the way to raw pine and pencil guide lines, and every week its face copies the line I stopped on and it sits one easel nearer."
- `twist`: "Faded all the way, nobody can see you except someone who loves you, which is why the others paint the fruit and say the stool has been empty for months. The faded sitter is Mum, gone unlooked-at since I stopped speaking to her in spring, and the half face on my canvas is the one I have been failing to finish on my portrait of her at home. I finish the face from memory without stopping, the colour comes back up her, and she says not bad. The sting: a new faded sitter on the stool, and nobody else looks up."
- `world`: "a town where unlooked-at faces fade to wood: a sunny bus stop and a cafe and a bakery counter for the montage, my small flat with one easel, and a community arts centre life room on rainy Wednesday evenings with eight easels round a pine dais, a stool, a green cushion and a bowl of fruit, plus Mum's bare front hall"

**New**
- **The fade (the rule marker, needed by 2 s).** A per-character `fade` amount from 0 to 1: painted colour thins into raw pine grain (`pine_mat`) on the face and then the body, and graphite guide lines (a cross, two eye ovals, little lines at the eye corners) show through the face. Fade 0.5 at S01 to S02 (bus-stop man), 0.4 easing to 0.05 over the shot at S05 (Mr Dobbs being filled in), 1.0 for faded Mum and the sting sitter. One shared look, so all four read as the same rule.
- **Faded Mum replaces the Unpainted.** Mum's own R6 body and silver bob hair block at normal proportions (drop the 1.4x torso), all pine at fade 1.0, no glasses (they fade with her), face texture per week: stage 0 = cross, two ovals, corner lines. Stage 1 = plus my nose line. Stage 2 = plus one mouth corner. Corner lines must read at phone size (they're plant 1).
- **The restore (S34):** fade 1.0 to 0.0 over about 2.5 s, from the face down: brown eyes with corner lines, silver hair, round tortoiseshell glasses, teal check cardigan. A soft rising paper-shimmer sound under it. Ramps only, nothing flashes.
- **Montage sets, small and daylight:** a bus stop on a sunny street (no signs, no text), a cafe table for two by a window, a bakery counter. Extras: the bus-stop man (red cap, half faded), two passers-by, a couple at breakfast, a baker and a customer.
- **My flat corner (S06 to S08):** one easel by a window, a shelf with my phone face down. **New canvas image: Mum's portrait at home**, her silver bob, round tortoiseshell glasses and teal check cardigan painted, her face only guide lines at stage 2 (cross, ovals, corner lines, a nose line stopped short, one mouth corner: where I always stop). Reused at S29 beside the class canvas.
- **The sting sitter (S39 to S40):** the same pine model, fade 1.0, with a different hair block (a short crop) and guide lines without corner lines, so it reads as somebody else.
- **The tally plant moves:** nine graphite strokes on the dais's front edge, seen at S39 (see the lore plant).
- **Sound:** thin pulse and rain to L21. A heavy low drone enters at L22 (the first scare) and holds through L31. Music drops (voice and hit only) 0.6 s before L23 and 0.7 s before L31. A major, 76 bpm, warm pad from L32 to L37. L38 to L40 back to the low drone, cold, then the closing sound.

**Dropped:** Mum's kitchen and the phone call, the old L02 to L04 backstory hall shots (Mum hanging pictures years ago), Mr Dobbs as a painter (he's now the montage sitter), the 1.4x torso, the dented-cushion beat, the stills montage of positions, the end-of-term show, the dais on its edge, and the frame-on-the-hook closing sound.

**Kept:** the life room, the eight easels, the dais, stool and flat green cushion, the fruit bowl and every fruit canvas, the power-dip ramp (one dip now, not two), the car park and the rainy window shot, Mum's bare hall, and the finished portrait (it must now read as Mum: her eyes, bob and glasses).

## Big idea (the one sentence)
In a town where your face fades if nobody looks at you, the faceless thing creeping nearer my easel every week is my own mum, faded so far that only someone who loves her can still see her, because I stopped looking at her in spring.

## Premise
In this town, a face nobody looks at fades back to bare wood and the first pencil lines it was drawn with. Lonely people sit for the Wednesday portrait class, where eight painters fill them back in. I paint, but Mum always said I never finish a face, and we haven't spoken since spring. I join the class to learn. On the dais stool sits someone faded all the way. Nobody else looks up. Every week its face copies the line I stopped on, and it sits one easel nearer.

## Rule
"In this town, if nobody looks at you, your face fades." Marker: the fade itself, raw pine grain and graphite guide lines showing through paint, on the bus-stop man's face at frame centre from 0 s, in bright daylight.

- **Montage (3 to 5, in the first 15 s):** the half-faded man at the bus stop as people walk past (S01), couples staring at each other over breakfast (S03), the baker holding your eye till your change is counted (S04), Mr Dobbs on the dais being painted back in (S05).
- **Seconds 15 to 30:** Mum's half-faced portrait, the bare hall, the class, Kofi's one instruction. Nobody explains the rule.
- **The narrator is the exception:** I'm the only one in the room who sees the sitter (L14, "Nobody else LOOKED UP"). The reason is the reveal.
- **The loved one at stake:** Mum, in a picture by about 0:15 (her portrait on my easel, her face only guide lines), with "we haven't spoken since spring, and she lives alone" under the rule we've just seen.
- **The loophole the climax turns:** the montage shows painting fills a face back in (L05). Nobody can see Mum to paint her, but I don't need to see her: I paint her face from memory, all of it, without stopping. "I never finish a face" turns over.

## Twist
Faded all the way, nobody can see you except someone who loves you. The others paint the fruit because to them the stool is empty. The sitter is Mum, who went unlooked-at since I stopped speaking to her in spring and came to the one place built for being looked at. Her face copied my canvas because painting is looking, and she sat nearer each week to the only person who could see her. Said plainly at L29 to L31, over one picture: my home portrait of Mum beside my class canvas, the same half face line for line, then her pine face through the wet window.

- **Plant 1, the corner lines:** the sitter's guide-line eyes have little lines at the corners, named at L13 ("little LINES at the CORNERS") and visible on Mum's home portrait at S06 (L06). Guide lines don't have those. Mum's eyes do (paid at L33, "with lines at the CORNERS").
- **Plant 2, since spring:** "We haven't SPOKEN since SPRING" (L07) and Petra's "empty for MONTHS" (L27). Paid at L29 ("since SPRING").
- **Plant 3, the fruit:** every other canvas is the fruit bowl (S14 Petra's sketch, S20 her pear, S28 seven bowls through the window). On a rewatch it's because they can't see her.
- **Bonus:** the pine hair block is Mum's bob shape from S11 on.

## The last 15 seconds
L36 to L40: Mum restored saying "Not BAD", her portrait in her hall with me visiting every Wednesday, then a new faded sitter on the stool and "Nobody else LOOKED UP. So why can I SEE them?" The loop cut lands on L01, which now reads as a warning about whoever you haven't called. On a second watch the first faded face at the bus stop, the couples staring, and "Nobody else LOOKED UP" all play as Mum's story.

## World
Daylight montage: a sunny street bus stop, a cafe window table, a bakery counter (no signs, no text). My small flat: one easel by a window, a shelf. The community arts centre on a hill, squat brick, rainy Wednesday evenings. The life room: cream plaster walls, a scuffed honey-board floor, a tall north window black-blue with rain, eight wooden easels in a curve each with a clamp lamp, a low pine dais in the middle with a plain stool and a fat sage-green cushion, a side table with a bowl of fruit. The car park under one lamp post. Mum's front hall, bare hooks and pale squares, then with one portrait. No text anywhere.

## Cast (all adults, nobody in peril)
- **Me (`me`):** an adult, no age on screen. Black block hair with a short fringe, a mustard knit jumper with one blue paint smudge, charcoal trousers, white trainers. Easel 8, by the window.
- **Mum (`mum`):** fifties. Silver block bob, round tortoiseshell glasses, a teal cardigan in a small check over a cream top, brown eyes with little lines at the corners. Seen as herself only on my portrait (S06), restored (S34 on) and in her hall (S37).
- **Kofi (`kofi`):** runs the class, forties. Shaved head, round black glasses, rust shirt, denim apron. Says "Paint what you see" once and explains nothing.
- **Petra (`petra`):** easel 7, thirties. Copper bun, navy and white striped top, paint rag on one shoulder.
- **Mr Dobbs (`ade`):** sixties. Grey block beard, brown flat cap, olive tweed jacket. The montage sitter at S05, half faded, being filled back in.
- **Montage extras:** the bus-stop man (red cap, blue jacket, half faded), two passers-by, a breakfast couple, a baker in a white apron and a customer. Five background painters at easels 2 to 6.

## The faded sitter (faded Mum, no monster)
- **Look:** Mum's R6 body and bob, every surface raw pine (`#d8b98a`) with grain, normal proportions. Face: graphite guide lines only, per week as above. No glasses, no clothes colour. Never seen moving, only already nearer.
- **Light it:** clamp lamps from below and the side, a cold rim from the north window, front fill dead. The empty eye ovals are the palest spot on it. Restored Mum is lit warm and bright.
- **Continuity:**
  - S11 to S16 (week 1): on the dais stool, cushion flat, facing the easels, hands on knees.
  - S17 to S18 (week 2): on a spare paint-spattered stool between easels 4 and 5, head turned to my corner.
  - S19 to S21 (week 3): on a spare stool beside Petra at easel 7, its knee level with her palette shelf, a hand's width clear of her.
  - S22 to S24 (week 4): on a spare stool at my elbow, leaning in from the waist, its face a hand's width from mine, never touching.
  - S28 to S31: still beside my empty easel, seen small through the window, then its face turned toward the glass.
  - S32 to S34: beside my easel, facing my canvas, restoring at S34.
  - S35 on: Mum herself. The pine look never returns on her.
  - Sting (S39 to S40): a different faded sitter on the dais stool.

## Palette and sound
- **Palette:** montage in bright sunny primaries, my flat in cool morning light, and the life room warm tungsten (about 3200 K) against the night-blue rainy window, raw pine and graphite, the sage cushion and Mum's teal. S32 to S37 bright and warm. S38 to S40 the room colder, lamps lower, still readable.
- **Caption key colour:** cerulean `#4cc3f0` (the paint smudge on my jumper).
- **Music:** A Aeolian, 68 bpm, a thin synth pulse with rain hiss to L21. Low heavy drone enters at L22 and holds to L31. Drops 0.6 s before L23 and 0.7 s before L31. A major, 76 bpm, warm low pad L32 to L37. L38 to L40 the drone returns alone, cold.
- **The power dip (L22):** one slow ramp, lamps 100% to 40% over 1.2 s, hold 0.8 s, cut while dim, back up over 1.2 s into S23. Never full dark. Pre-check with `flash`.
- **Closing sound:** under L40, one low two-note chord falling a fifth at about -16 dB, then 0.25 s to the loop cut.

## The lore plant
Nine short graphite strokes, plain, no extra stroke (eight easels and one sitter, the number the class is built for), scratched along the front edge of the dais. Seen in S39 under L39: the dais edge across the lower middle of the frame, above the caption band, strokes fully in frame, lit by a clamp lamp, held about 1.6 s. Never narrated. Same graphite as the guide lines.

## Shot plan and narration
Format: id, who, caption chunks split with ` / `, CAPS are key words in cerulean. Shots under each line.

### 01 The rule (0 to about 15 s)
- `L01` narrator: In this TOWN, / if nobody LOOKS at you, / your face FADES.
  - [S01: bright daylight bus stop. The bus-stop man at frame centre, face at least 1/4 frame width: half his face faded to raw pine grain, one eye only a pencil oval. Two passers-by walk past without looking. Rule marker and face readable from frame 1]
  - [S01b at "FADES": push in on the fade line across his cheek]
- `L02` narrator: Down to bare WOOD, / and the first PENCIL LINES / you were DRAWN with.
  - [S02: close on his faded half: grain, and the graphite cross and oval showing through]
- `L03` narrator: So everybody STARES. / Couples stare at each other / over BREAKFAST.
  - [S03: cafe window table, a couple staring hard at each other, toast going cold. Played for a laugh]
- `L04` narrator: The baker holds your EYE / till your change / is COUNTED.
  - [S04: bakery counter, the baker staring at the customer, unblinking. Cut to the customer's uneasy face]
- `L05` narrator: And if you're LONELY, / you sit for the PORTRAIT CLASS, / and eight painters / fill you back IN.
  - [S05: the life room in warm light: Mr Dobbs on the dais, his faded cheek warming back to colour. S05b: over a painter's shoulder, his face on the canvas]

### 02 Mum (about 15 to 23 s)
- `L06` narrator: I PAINT. / But Mum always SAID / I never FINISH / a FACE.
  - [S06: my flat, my easel: Mum's portrait, silver bob, round tortoiseshell glasses, teal check cardigan, her face only guide lines: a cross, two ovals, little lines at the eye corners, a short nose line and one mouth corner. Me beside it, face in frame. Plant 1 visible]
- `L07` narrator: We haven't SPOKEN / since SPRING, / and she lives ALONE.
  - [S07: my phone face down on the shelf, silent, no UI. S07b: Mum's front hall, bare hooks and paler squares on the paper, nobody in it]
- `L08` narrator: I told myself / someone ELSE / was looking at her.
  - [S08: me close, turning away from the portrait]

### 03 Week one (about 23 to 42 s)
- `L09` narrator: So on WEDNESDAY / I joined the PORTRAIT CLASS, / to learn to finish a FACE.
  - [S09: high wide of the squat brick arts centre on a hill in rain, warm windows, no signs. S09b: me on its steps, a canvas under my arm]
- `L10` narrator: Kofi set out / a BOWL of FRUIT, / and said, / "Paint what you SEE."
  - [S10: the fruit bowl on the side table. S10b: Kofi mid-shot, friendly, glasses catching the lamp]
- `L11` narrator: On the dais STOOL, / someone was SITTING. / Faded ALL the WAY.
  - [S11: over my shoulder from easel 8: the faded sitter on the stool, the green cushion flat under it]
- `L12` narrator: Bare PINE, / from its HAIR / to its SHOES.
  - [S12: low wide past two easels: grain, two dark knots, the pine bob, lit from below]
- `L13` narrator: Just a CROSS, / two empty OVALS, / and little LINES / at the CORNERS.
  - [S13: close on its face. The ovals the palest thing, the corner lines clear. Plant 1 named]
- `L14` narrator: Nobody else / LOOKED UP.
  - [S14: wide from behind the dais, every painter's head down. Petra's canvas: a pencil outline of the fruit bowl. Plant 3]
- `L15` narrator: So I painted IT. / I got as far / as the NOSE, / and STOPPED.
  - [S15: me at easel 8, side on. S15b: my canvas, a nose line stopped short. Cut away before a hand meets the canvas]
- `L16` narrator: HALFWAY. / AGAIN.
  - [S16: my face, jaw tight, lamp from below]

### 04 Weeks two and three (about 42 to 55 s)
- `L17` narrator: Next WEDNESDAY, / it had a NOSE. / MY nose, / right where I'd STOPPED.
  - [S17: close on its face, the short nose line. S17b: my canvas, the same line, same length]
- `L18` narrator: And it was sitting / one easel CLOSER.
  - [S18: the empty dais stool, cushion flat, pan to it on a spare stool between easels 4 and 5, head turned to my corner]
- `L19` narrator: Week THREE, / I painted half a MOUTH. / It sat by PETRA, / with half a MOUTH.
  - [S19: my canvas, one mouth corner. S19b: over my shoulder, it beside Petra at easel 7, one mouth corner on its face, its pine knee by her palette]
- `L20` narrator: Petra HUMMED, / and painted / a PEAR.
  - [S20: Petra's canvas, a green pear. Plant 3]
- `L21` narrator: Its empty EYES / never left / MY EASEL.
  - [S21: from behind easel 7, its head turned to camera at easel 8]

### 05 The scare (about 55 to 65 s)
- `L22` narrator: Week FOUR, / an hour IN, / the lights DIPPED.
  - [S22: wide of the room, clamp lamps ramping to 40%, rain up, the drone enters. Cut while dim. Music drop 0.6 s before L23]
- `L23` narrator: When they came BACK, / it was RIGHT / BESIDE ME.
  - [S23: lamps up: wide from the window side, it on a spare stool at my elbow. The hit. Cover frame]
- `L24` narrator: Leaning IN, / its face / a hand from MINE.
  - [S24: 3/4, lit from below, its pencil face leaning in toward mine, a hand's width apart, the ovals the palest thing. It never touches me]
- `L25` narrator: I left my COAT / and RAN.
  - [S25: my coat on the easel peg, the door swinging]

### 06 The car park (about 65 to 83 s)
- `L26` narrator: In the CAR PARK, / Petra brought my COAT. / I asked who our SITTER was.
  - [S26: rain, a lamp post, Petra jogging over with my coat. S26b: two-shot under the lamp]
- `L27` narrator: She LAUGHED. / "That stool's been EMPTY / for MONTHS."
  - [S27: Petra, amused, rain on her bun. S27b: me, the words landing]
- `L28` narrator: Through the WINDOW, / I could see / every CANVAS.
  - [S28: from the car park through the lit, rain-streaked window: seven bowls of fruit, then mine with the half face, the faded sitter beside it, small]
- `L29` narrator: Mine had the same half FACE / I'd been starting at HOME / since SPRING.
  - [S29: THE PICTURE. Mum's home portrait and my class canvas side by side in frame, the same lines, corner lines included. Hold it]
- `L30` narrator: Faded all the WAY, / nobody can SEE you, / except someone who LOVES you.
  - [S30: through the wet glass, the faded sitter turns its pencil face toward me. Drone holds. Music drop 0.7 s before L31]
- `L31` narrator: The thing on the STOOL / was MUM.
  - [S31: close through the glass on its face, the pine bob, the corner lines, rain running down. Held to the end of the line plus 0.6 s]

### 07 The face (about 83 to 97 s)
- `L32` narrator: I went back IN, / and I didn't STOP / this time.
  - [S32: me walking in wet, the room bright and warm, music to A major. S32b: me painting, side on, steady. Cut away before a hand meets the canvas]
- `L33` narrator: The kindest EYES I know, / BROWN, / with lines at the CORNERS.
  - [S33: my canvas, Mum's eyes. S33b: its face, the brown coming into the ovals]
- `L34` narrator: Silver HAIR. / Round GLASSES. / A mouth about to say, / "NOT BAD."
  - [S34: the restore, about 2.5 s: the colour climbs her, silver bob, glasses, teal cardigan. Mum on the stool at my elbow, looking at the canvas]
- `L35` narrator: Behind me, / Petra dropped / her BRUSH.
  - [S35: Petra staring at Mum, mouth open. S35b: the brush on the boards]
- `L36` narrator: Mum looked at it / for a long TIME. / Then she said, / "Not BAD."
  - [S36: Mum's face, glasses, eyes shining, a small smile. S36b: two-shot, me and Mum, the painting between us]

### 08 The hall, and the sting (about 97 to 105 s)
- `L37` narrator: It hangs in her HALL now. / I go round every WEDNESDAY / to LOOK at her.
  - [S37: Mum's hall, bright morning, the portrait alone among the pale squares, Mum and me in front of it, both looking at each other]
- `L38` narrator: Kofi still sets out / the STOOL.
  - [S38: the life room, colder, Kofi plumping the green cushion. Cut away before his hands meet it]
- `L39` narrator: This week, / someone NEW / was SITTING on it.
  - [S39: low on the dais: the nine graphite strokes on its front edge (lore plant, held 1.6 s), rising to the sting sitter on the stool, short pine crop, guide-line face. Behind it, every painter's head down over the fruit]
- `L40` narrator: Nobody else LOOKED UP. / So why can I / SEE them?
  - [S40: slow push on its blank pencil face, the ovals the palest thing. Closing chord, 0.25 s, loop cut to S01]

## Notes for the builder
- Hands never grip: cut away at S15b, S32b and S38. The phone lies on the shelf at S07.
- S24 leans it from the waist toward me, a hand's width clear in every shot. Check it against the easel and lamp clamp.
- S29 is the reveal picture: both canvases large, side by side, every guide line matching, out of the caption band.
- Spare stools are plain and paint-spattered. The green cushion is only on the dais stool.
- No text on canvases, signs, the bakery or the bus stop.
- Cover (`cover_s` 56.0, estimated): S23, it at my elbow under the lamps with my face in frame, caption "BESIDE ME". Re-set it from the timings.
