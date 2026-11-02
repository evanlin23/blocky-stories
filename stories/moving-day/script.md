# ep17-moving-day: the 2-minute script (scriptwriter, 2026-10-31)

- **Working title:** The box was taped shut from the inside. L01 says it word for word. The upload title is the packager's, and it isn't an imperative rule.
- **Takeaway:** none on purpose. It's a made-up blocky story for PandaNanoAdventures (notes 16 and 21).
- **Target length:** 2:15 to 2:20, never over 3:00.
- **Word count:** 593 spoken words in 81 lines, all in voice A, plus 2 pause beats. That's 572 after the new L78, plus 21 for L29b, L34b and L34c.
- **Estimated length:** about 2:19.
  - The first real `voice` run measured 2:14.4 (134.43 s), with all five of the brief's holds already in. The voice ran at 292 wpm while speaking.
  - That was 0.6 s under the owner's 2:15 floor, so the fix is more story, not more silence. The three new lines add 21 words, about 4.3 s at that pace, plus 0.36 s of line gaps. That comes to about 139 s, which is 2:19, inside 2:15 to 2:20 with some margin.
- **Shots:** about 73, with a new shot on almost every line. Each section gives its own count. The three new lines need entries in the designer's shot list.
- **The machine-readable lines** are in `reels/blocky/stories/moving-day/generator/lines.json`, in the same shape as closing-time's. Shots, acting, cues and sound are the designer's.

**Producer, 2026-10-31 (brief):** L13, L32 and L55 are changed below for logic and standards, and L78 is back with the scriptwriter. `02-brief.md` → "Script changes" has the reasons, and its continuity list and picture rulings win where a bracket here differs.

**Scriptwriter, 2026-10-31:** L78 is now "Mum CLOSED / the CUPBOARD / on it." Section 08 gives the reason.

## The producer's nine changes, and where they are

1. **L01's picture is fixed.** The outer tape is peeled back, the flaps still hold, and tape shines through a gap at one corner. The box stays shut. L02 says "PEELED" rather than "slit", so no blade is implied.
2. **The seams are taped from the inside.** That's L30 to L34, the one middle beat where I act. I try to pull it apart and it won't come apart. It isn't damaged, and no line gives the Boxes a reason.
3. **The 3 a.m. shadow comes first.** L46 is the nightlight's square shadow, and only then L47 to L48.
4. **The stack by the door is the clock.** It's the same locked-off wide at L14 to L15, L25, L35 and L41, then whole again at L63. Six boxes go, then half, then four are left, then none. The Boxes get taller by folding along the ceiling. What it points at goes from nothing, to the back of Mum's head, to Mum's door, to me. No line says "closer" or "each time".
5. **None of B's rule is used.** Nothing looks away, turns back or blinks. Every face change happens between scenes, off screen.
6. **The laugh pays off Mum's own line.** At L07 she says "No more LADDER to hang PHOTOS." At L67 she says "That's LADDER HEIGHT."
7. **The tuck and the twist stay about the house.** No word for care, kindness, missing, loneliness or looking after, and no motive. L61 is the producer's line as written.
8. **The end is still.** From L77 the smiling box never moves or changes. I have the last line, with 0.25 s to the cut.
9. **One house set, no room in a second state.** There are four mornings, and the only thing that comes back whole is the stack.

## Format

Each line gives the id and who says it, then the caption chunks split with ` / `. CAPS are the key words, in the brief's key colour. The designer's provisional `story.json` has amber `#ffb547`.

- **Spoken text:** the chunks in sentence case without the quote marks, the way `lines.json` stores them.
- **Who:** every line is `narrator`, read in voice A. That's me, cast key `me`.
  - Mum is cast key `mum`. She has no voice of her own, and her words are reported in my lines, as note 18's "one voice" asks. Her mouth flaps under the words I quote, at L07, L11 and L67.
  - The Boxes never speak.
- **Pause beats** (`P01` and `P02`) have no words. Each gives its length and its big word. Neither has a big word.
- **Where** heads each section. A line that moves somewhere else says so in brackets under it.
- **Faces:** the brackets name the face the Boxes wear in that shot.
- **Timing:** the `gap`, `tempo` and `gain_db` keys in `lines.json` are provisional, for the designer to retune after `voice`. A `gap` is the hold after its line.

## 01 The box

- **Where:** L01 to L04 are the hall at dawn. L05 to L12 are quick pictures from our first days in the house: its front, Mum hanging a frame, me at a box, the quilt going into a box and the mug on the front-room windowsill.
- **Shots:** about 10.
- **Plants:** all land by about 23 s.
  - The inside tape at L01 to L02 pays off at L33 and at the very end.
  - Mum's ladder line at L07, about 14 s, pays off at L59 and L67.
  - The old-hall smell at L08, about 16 s, pays off at L60.
  - The quilt left packed at L09, about 18 s, pays off at L52 to L54.
  - The mug and Mum's line about it at L10 to L11, about 22 s, pay off at L58.
  - Mum not looking up at L12, about 23 s, pays off at L24 and L66.

- `L01` narrator: The box / was taped SHUT. / From the INSIDE.
  - [close on the bottom box of a stack in the hall. Its outer tape is peeled back along the seam, but the flaps still hold. Through a gap at one corner, tape shines on the inside. The box stays shut]
- `L02` narrator: I'd PEELED / the outside TAPE. / The flaps / still HELD.
  - [my hands flat on the flaps, pressing. They don't give]
- `L03` narrator: It was / the BOTTOM box / of a STACK / TALLER than ME.
  - [a slow tilt up the Boxes, standing still in the hall. Its top box just touches the ceiling]
- `L04` narrator: And on / the TOP box, / in black MARKER, / a FROWN.
  - [close on the front box. Face: the frown, aimed down the hall at nothing]
- `L05` narrator: The new house / is SMALLER, / with LOW CEILINGS.
  - [outside, the small house at dawn. No number on the door]
- `L06` narrator: The OLD one / got SOLD, / and Mum hasn't / LAUGHED since.
  - [Mum in the kitchen doorway, tired, her face flat]
- `L07` narrator: She said, / "No more LADDER / to hang PHOTOS."
  - [Mum hangs a frame at eye height without a smile. Her mouth flaps under the quote]
- `L08` narrator: Every BOX / still smells like / the OLD HALL.
  - [me with my face to a box, eyes shut]
- `L09` narrator: Mum left / the OLD QUILT / PACKED. / Too WARM / for it HERE.
  - [the folded quilt going into a box. It's the only patterned cloth in the house, so it reads again at 3 a.m.]
- `L10` narrator: And every MORNING, / her MUG / was on the / front-room WINDOWSILL.
  - [the mug on the front-room windowsill in morning light]
- `L11` narrator: Mum said, / "That's where / I always / KEPT it."
- `L12` narrator: She didn't / LOOK UP.
  - [Mum picks up the mug with her head down. Hold 0.35 s]

## 02 The stack

- **Where:**
  - L13 is the hall, with Mum walking past the Boxes.
  - L14 and L15 are the stack by the front door, in a locked-off wide that every morning repeats exactly.
  - L16 is my room in the dark.
  - L17 to L21 are the kitchen, and L22 to L24 the front room.
  - L25 goes back to the stack's wide.
- **Shots:** about 12.
- **Plants:** the stack's wide at L14 starts the clock. The photos up at the ceiling at L22 to L23 wait for the ladder payoff, and Mum not looking up at L24 keeps them hidden from her.

- `L13` narrator: Mum thinks / I MOVED it / in my SLEEP.
  - [Mum walks past the Boxes with her mug in her hand and doesn't look at it. Face: the frown]
- `L14` narrator: We'd STACKED / the REST / of our BOXES / by the DOOR.
  - [the locked-off wide: the front door with the stack beside it, about 24 boxes. Every morning uses this exact frame]
- `L15` narrator: SIX / had GONE.
  - [the same wide. Six clean squares in the dust where boxes stood]
- `L16` narrator: In the NIGHT, / something SCRAPED, / like CARDBOARD / across the FLOOR.
  - [me lying in bed in the dark, eyes open, not moving]
- `L17` narrator: Next MORNING, / it was in / the KITCHEN.
  - [the kitchen. The Boxes stand by the fridge, still]
- `L18` narrator: TALLER. / Its top box / FOLDED / along the CEILING.
  - [low angle: its top box bent over along the ceiling]
- `L19` narrator: The FROWN / was GONE. / Now it STARED / at the BACK / of Mum's HEAD.
  - [over the Boxes' shoulder: Mum at the counter making tea, her back to it. Face: the stare]
- `L20` narrator: The MARKER / was still WET.
  - [close: the stare's lines are glossy. It's the only wet face in the film]
- `L21` narrator: Mum made / her TEA / right under it.
- `L22` narrator: And every PHOTO / was moved UP / to the CEILING.
  - [the front room: every frame hung at the very top of the wall, its top edge bent over onto the ceiling. The photos show only me, Mum and the old house from outside]
- `L23` narrator: Like something TALL / had HUNG them.
- `L24` narrator: Mum never / LOOKED UP.
  - [Mum crosses under the photos with her head down]
- `L25` narrator: The STACK / by the door / was HALF GONE.
  - [the locked-off wide, half the boxes gone. Hold 0.3 s]

## 03 The seams

- **Where:** the front room. L29b looks across the hall to Mum's shut door. L34b and L34c are the kitchen counter in cold morning light, and L35 is the stack's wide.
- **Shots:** about 12.
- **Plants:** none new. L33 pays off L01 to L02, and the empty tape at L34b and L34c is the proof you can see.

- `L26` narrator: The morning AFTER, / it was in / the FRONT ROOM.
  - [the Boxes in the front-room corner, now with two boxes bent along the ceiling]
- `L27` narrator: Every box / in there / had EYES now.
  - [a slow pan across the other boxes, with two marker eyes on each, dry]
- `L28` narrator: Drawn in MARKER. / ALL of them / AIMED / at Mum's DOOR.
  - [the reverse: through the front-room doorway and across the hall to Mum's shut door]
- `L29` narrator: Its own FACE / looked SIDEWAYS, / the SAME way.
  - [Face: two eyes slid hard to one side, toward Mum's door. No mouth]
- `L29b` narrator: And Mum / was still / ASLEEP.
  - [from the front room, across the hall: Mum's shut door, quiet, in grey early light. Nothing moves. The Boxes' sideways eyes are at the frame's edge]
- `L30` narrator: So I tried / to PULL it / APART.
  - [me at the Boxes, both hands flat on a seam, leaning back]
- `L31` narrator: I PULLED / till my ARMS / SHOOK.
  - [my arms tremble. Its boxes don't move at all]
- `L32` narrator: No TAPE / to PEEL.
  - [cutaway: my hand at a bare joint between two of its boxes. There's no tape on the outside]
- `L33` narrator: Every SEAM / was taped / from the INSIDE.
  - [close on a seam. The outside is bare, and tape shine shows through the gap, inside. Hold 0.3 s]
- `L34` narrator: Not ONE box / would SHIFT.
  - [I step back. It isn't marked, dented or torn]
- `L34b` narrator: In the KITCHEN, / every TAPE ROLL / was EMPTY.
  - [the kitchen in cold morning light. I stand at the counter, looking down at what's on it]
- `L34c` narrator: Just CARDBOARD / RINGS, / STOOD UP / in a ROW.
  - [close and low along the counter: five bare tape cores standing on end in a neat, evenly spaced line. We never see them being stood up]
- `L35` narrator: By the DOOR, / FOUR boxes / LEFT.
  - [the locked-off wide, four boxes. Hold 0.3 s]

## 04 My room

- **Where:** my room, before dawn and at first light. L41 and L42 are the stack's wide, now empty. L43 is the kitchen.
- **Shots:** about 7.

- `L36` narrator: I WOKE UP / with it / in MY room.
  - [from my pillow, in the dark: the Boxes in the corner, its top boxes bent along the ceiling toward my bed]
- `L37` narrator: Its top box / hung DOWN / over my PILLOW.
  - [looking up from the pillow at the front box, hanging face-down above me]
- `L38` narrator: Its face / was far too / many EYES.
  - [Face: far too many eyes, dry marker, every pupil on me]
- `L39` narrator: ALL on ME.
  - [my face, `terrified`, not moving. A quieter line]
- `L40` narrator: I didn't MOVE / till DAWN.
  - [the window going grey. I haven't moved]
- `L41` narrator: The STACK / by the door / was GONE.
  - [the locked-off wide: an empty floor and the clean squares where every box stood]
- `L42` narrator: Every BOX / we BROUGHT / was IN it.
- `L43` narrator: At BREAKFAST, / Mum said / I looked TIRED.
  - [the kitchen. Mum with her tea, me across from her, wrecked. Hold 0.45 s]

## 05 Three a.m.

- **Where:** the hall, then Mum's room seen from her doorway.
- **Shots:** about 11.
- **The silence:** music, ambience and footsteps drop from L49 to L51, so "WIDE OPEN" and the reach land with only the voice. P01 has one low cardboard creak. The room tone comes back with the light.

- `L44` narrator: At THREE A.M., / the SCRAPING / STOPPED.
  - [my room in the dark. My eyes open]
- `L45` narrator: I went / into the HALL.
  - [the hall, with a small nightlight low on the wall]
- `L46` narrator: A SQUARE SHADOW / filled the WALL / and BENT / over the CEILING.
  - [the nightlight throws one huge square shadow up the wall and over the ceiling. It holds still. No figure yet]
- `L47` narrator: It came / from Mum's ROOM. / Her door / stood OPEN.
  - [Mum's door, open and darker inside]
- `L48` narrator: It was BENT / over her BED, / TOO TALL / for the ROOM.
  - [side-on from the doorway: the Boxes beside Mum's bed. Its top boxes fold along the ceiling, so the front box hangs face-down over her. Mum is asleep on her back. The only light is the hall's, from the side]
- `L49` narrator: Its face / was drawn / WIDE OPEN.
  - [close, from below. Face: wide open, with huge round eyes and a black open mouth that fills the box. A slower line]
- `L50` narrator: Its long ARMS / REACHED DOWN / to her.
  - [side-on: its arms come down over the bed, and the box ends are in frame above her shoulders. Never the full length toward camera]
- `P01` pause 1.2 s: none
  - [hold the side-on wide in near silence, with one low, slow creak of cardboard]
- `L51` narrator: I hit / the LIGHT.
  - [a dim lamp on the chest of drawers by her door comes up slowly. Flash pre-check it at the final's frame steps]
- `L52` narrator: Under its HANDS / was the / OLD QUILT.
  - [close: the box ends resting on the quilt's edge]
- `L53` narrator: TUCKED round / her SHOULDERS, / the edges FOLDED / under the MATTRESS.
  - [Mum asleep with the quilt at her shoulders, her face clear and calm, breathing slow]
- `L54` narrator: The QUILT / she'd left / PACKED.
- `L55` narrator: Mum SLEPT / right THROUGH it.
  - [Mum sleeping, warm in the lamp light. A quieter line. Hold 0.5 s]

## 06 Where it lived

- **Where:** L56 and L57 are Mum's room in the lamp light, with me in the doorway and the Boxes still bent over the bed. L58 to L60 cut to the mug on the windowsill, the photos at the ceiling and the Boxes' taped seams. L61 goes back to Mum's room.
- **Shots:** about 6.
- **The twist is the house.** Every line here is about where things lived. None of them says why the Boxes did it.

- `L56` narrator: Back in / the OLD house, / Mum's ROOM / was the / COLD one.
- `L57` narrator: She slept / under that QUILT / all WINTER.
- `L58` narrator: Her MUG / LIVED / on the WINDOWSILL.
  - [the mug on the front-room windowsill]
- `L59` narrator: Her PHOTOS / hung at / LADDER HEIGHT.
  - [the frames at the ceiling, from below]
- `L60` narrator: These BOXES / came from / the OLD house.
  - [the Boxes in Mum's room, the lamp light on their seams]
- `L61` narrator: Everything / it MOVED / was where / it LIVED / BEFORE.
  - [back on the Boxes over Mum's bed, still. Face: wide open, unchanged. A slower line. Hold 0.5 s]

## 07 Ladder height

- **Where:** L62 is Mum's room in the morning, with the corner empty. L63 is the stack's wide, whole again. L64 to L74 are the front room and kitchen in low gold sun.
- **Shots:** about 11.
- **The warm turn is in the picture.** P02 is the laugh, with no words over it. The lines after it are short and come after we've seen it.

- `L62` narrator: In the MORNING, / it was GONE.
  - [Mum's room in the morning. The corner is empty, and Mum is still asleep under the quilt]
- `L63` narrator: Our STACK / was BACK / by the DOOR.
  - [the locked-off wide: the stack whole again, every box taped]
- `L64` narrator: Mum came out / WRAPPED / in the QUILT.
  - [Mum in the hall with the quilt round her shoulders]
- `L65` narrator: She went / for her MUG / on the SILL.
- `L66` narrator: And for ONCE, / she LOOKED UP.
  - [her head tilts up. Cut to her eyeline: the frames at the ceiling, their tops bent over onto it]
- `L67` narrator: She said, / "That's / LADDER HEIGHT."
  - [Mum still looking up, mouthing the words]
- `P02` pause 2.0 s: none
  - [the laugh, held. A two-shot in low gold sun, with the mug on the sill catching it. Her shoulders go first, then her face, from `grin` to `squeeze`, with a tremble and a lean. The score turns to the major here]
- `L68` narrator: She LAUGHED / till she / had to SIT.
  - [Mum sits down on a box from the stack, still laughing]
- `L69` narrator: Her first LAUGH / since the SALE.
- `L70` narrator: I was / LAUGHING TOO.
  - [a two-shot, both of us laughing. Hold 0.3 s]
- `L71` narrator: So we UNPACKED / the STACK / the OLD way.
  - [the quick two-shots begin]
- `L72` narrator: She POINTED. / I put it / THERE.
  - [Mum points, and the next cut shows the thing in place]
- `L73` narrator: COATS / by the DOOR. / The KETTLE / on the LEFT.
  - [coats on hooks by the front door at the old height. The kettle moved to the left of the sink]
- `L74` narrator: The PHOTOS / stayed UP.
  - [Mum looks up at them again, smiling, and leaves them where they are. Hold 0.35 s]

## 08 The last box

- **Where:** the hall, at the open hall cupboard. The last shot holds on the box on the shelf.
- **Shots:** about 4.
- **The end is still.** From L77 the box never moves and its face never changes. The narrator has the last line.

- `L75` narrator: When we'd EMPTIED / the LAST box, / Mum opened / the hall CUPBOARD.
  - [the hall, with our folded boxes in a neat pile by Mum's feet. She opens the cupboard]
- `L76` narrator: On the SHELF / sat ONE more, / still taped SHUT.
  - [inside the cupboard, on the shelf: one box, made up and taped. It's the Boxes' front box]
- `L77` narrator: On its FRONT, / in black MARKER, / a SMILE.
  - [close. Face: the smile, on the same box with the same line weight. Hold 0.45 s]
- `L78` narrator: Mum CLOSED / the CUPBOARD / on it.
  - [Mum swings the cupboard door shut. The box doesn't move, and its smile stays in view until the last of the gap closes on "it". Hold on the shut door, then 0.25 s after "it", a hard cut to L01's close on the taped box, with no fade. The slowest line]

Across the loop it reads "Mum closed the cupboard on it. The box was taped shut. From the inside." The old L78 ("The SMILING box / is still / on that SHELF. / We've NEVER / OPENED it.") had floor-thirteen's "X is still there. We never Y." shape. The new line is one plain action with no "still" and no "never". It isn't a rule Mum keeps (ep12's lane) and it isn't a gesture at the box. "Closed" doesn't double L01's "SHUT" across the seam.

## The Boxes, the same in every shot (continuity list)

The narration calls it "it". "The Boxes" is the team's name only and never said. It has no other name.

1. **One model,** built once in `set.py` and posed per shot. It's brown cardboard, black marker and packing-tape shine. No box carries a word.
2. **It's never seen moving.** Every change, its height, its room and its face, happens between scenes, off screen. It's still in every shot, L48 to L61 included.
3. **The front box is its only face.** It's the same box with the same line weight, and the faces go in this order:
   - the frown, L03 to L13
   - the stare, L19 to L21. It's the only wet face.
   - two eyes slid sideways toward Mum's door, L26 to L34
   - far too many eyes, L36 to L42. Flat and dry, never opening one after another (that's ep13).
   - wide open, L48 to L61
   - the smile, on the cupboard shelf, L77 to the end
4. **Its height** grows by folding along the ceiling, never by stretching. On morning 1 the top box touches the ceiling. On morning 2 the top box bends along it, and on morning 3 two boxes do. On morning 4 it bends toward my bed and the front box hangs over my pillow. At 3 a.m. it's the same over Mum's bed.
5. **What it points at:** down the hall at nothing, then the back of Mum's head, then Mum's door, then me. At 3 a.m. it's over Mum.
6. **Arms:** long, made of narrow boxes, and kept down at its sides until L50. They're shot side-on, with the box ends in frame.
7. **The seams** have tape only on the inside. The outside of every seam is bare. L33 shows it close.
8. **Sound:** a synthesized cardboard scrape at L16 and just before L44, and one low cardboard creak at P01. Nothing else, and no samples.

### The stack by the door, the clock

| Morning | Lines | The stack | The Boxes | It points at |
|---|---|---|---|---|
| 1 | L01 to L15 | six gone, about 18 left | the hall, top box touching the ceiling, the frown | down the hall |
| 2 | L17 to L25 | half gone | the kitchen, top box bent along the ceiling, the stare | the back of Mum's head |
| 3 | L26 to L35 | four left | the front room, two boxes bent along the ceiling, sideways eyes | Mum's door |
| 4 | L36 to L43 | gone | my room, hanging over my pillow, far too many eyes | me |
| after 3 a.m. | L62 to L63 | back, whole | gone | nothing |

## Notes for the designer, sound and standards

- **Cast:** `me` is the narrator, an adult. The age is in the brief's cast table only, never on screen or in the voice. `mum` is an adult. Nobody else appears, and every word is voice A.
- **The tuck:** Mum's face stays clear of the quilt and nothing presses on her. Her eyes stay shut and calm through L48 to L62. The arms are side-on with the box ends in frame. "Reached" and "tucked" are the only touch words, and both land on the quilt.
- **The light at L51** is a dim lamp by her door, so I don't cross the room past it. It comes up as one slow change.
- **L30 to L34:** R6 hands can't grip. My hands sit flat on a seam, I lean back, and my arms tremble. The cutaway shows my hand at the seam's edge. The Boxes aren't marked, dented or torn, and nothing comes off.
- **L34b and L34c, the tape cores:** five bare cardboard cores, made from kit cylinders, with no printing and no brand. They stand on end on the kitchen counter. I'd keep them there, untouched and never mentioned, in the L43 breakfast shot, then have them gone from L62 on, as the L35 eyes are. That's the producer's call.
- **L68:** Mum sits on a box. Check the seated pose against the box, and probe contact.
- **The set:** no words on any box. No brand on the kettle, the mug or anything else. No house number and no street sign. The photos show only me, Mum and the old house from outside.
- **Sound:**
  - The scrape and the creak are new synthesized sfx kinds in `sound.py`. They're opt-in, with defaults unchanged.
  - There's no laugh sound. Mum's laugh is picture and score only, because there's one voice and everything is synthesized.
  - The score turns to the major at P02 and stays warm to the end. Keep one soft low note under L78 so the cut back to L01 bites.
- **Standards words:** no words for death, killing, weapons or gore, and no child words. Nothing claims it's true, and the game's name isn't in it. The town and the house are unnamed.
- **Avoided from batch 1 and the other batch 2 rows:**
  - "Last night", "That night", "the next night", "every night", "one by one" and "all along"
  - "closer", "each time" and "every time"
  - "it didn't touch me" and "pressed flat"
  - "lonely" or any word for kindness or care, and "thanks"
  - "lamp", which is lookout's word. On screen it's a lamp, but the line says "LIGHT".
  - "DING", any reflection, a blink, looking away or turning round
  - a knowing elder, a night-shift or one-summer narrator, a ritual done back and a return on a later night
- **Phrase overlap:** checked against ep11 to ep13's story files and the quoted lines in the three batch-2 sibling pitches (none has lines yet). The highest is 0.9%, with ep11. The shared phrases are "from the inside", "by the door" and "with it in". The block is at 12%.

## Say-it-out-loud notes

- **L01:** flat and quick, as if mid-scare. "INSIDE" lands by about 2 s.
- **L02:** a little faster, matter-of-fact.
- **L07, L11 and L67:** it's my voice reporting Mum, not a Mum voice. Give the quote a small lift.
- **L12 "She didn't LOOK UP."** Plain. It's a plant, so don't lean on it.
- **L20 "still WET."** A tiny catch before "WET".
- **L21:** dry, nearly funny.
- **L33 "from the INSIDE."** Slow a touch, because it calls back L01.
- **L29b "And Mum was still ASLEEP."** Quiet and plain. It's what makes L30 my reaction.
- **L34b and L34c:** flat, like noting something odd. "STOOD UP in a ROW" is even, with no push.
- **L39 "ALL on ME."** Quieter, at -2 dB.
- **L49:** slower, at tempo 0.9. Then hold P01 in full.
- **L51 "I hit the LIGHT."** Clipped.
- **L55 "Mum SLEPT right THROUGH it."** Quiet, and let it settle.
- **L61:** slower, at tempo 0.9, with a beat after it. It's the twist line.
- **L66 "And for ONCE":** a small lift.
- **L67 "LADDER HEIGHT."** Dry, because it's Mum's joke. P02 holds the laugh.
- **L69:** warm, not bright.
- **L78 "Mum CLOSED the CUPBOARD on it."** The slowest line, at tempo 0.88. Plain and final, like closing any cupboard. Land "it" low and don't trail off, because the cut comes 0.25 s after it and L01 picks the sentence up.
- **Pronunciation:** "Mum" rhymes with "come", never "mom".
- **For Whisper (`asr`):**
  - **"Mum"** is the biggest risk. It's said 14 times, and small.en may write "mom", which `asr` counts as a wrong word each time. If Kokoro says it right, the fix is a "mum"/"mom" entry in `voice.py`'s `SPELLINGS`, which is a shared engine file, so that's the designer's call. If Kokoro says it wrong, give "Mum" a phoneme (mˈʌm) under `phonemes`.
  - **"three a.m."** at L44: Whisper's "3 a.m." comes back as the same words. If Kokoro reads "a.m." as "am", change only the spoken text to "three A M".
  - **Homophones it may pick:** "four" as "for" at L35, "roll" as "role" at L34b, "too" as "two" at L09 and "sale" as "sail" at L69. They're the same sound, so they're spellings, not mistakes. `voice.py`'s homophone list has only "threw"/"through", which already covers L55's "right THROUGH it".
  - "front-room windowsill" is fine. `asr` treats spacing and hyphens as spellings.
  - There are no made-up names, so no other phonemes are needed.

## Open questions for the brief

1. **L02 says "PEELED", not "slit"**, so no blade is implied. L01's picture becomes outer tape peeled back along the seam. Is that all right?
2. **After 3 a.m. the Boxes are gone and the whole stack is back by the door** (L62 to L63). L42 put every box into the figure, so the stack has to come back for there to be anything left to unpack. It's unexplained and never seen happening.
3. **The smiling box on the shelf is the Boxes' own front box.** I've written it that way for continuity. Confirm it in the creature's continuity list.
4. **The stack's size.** About 24 boxes, so six gone on morning 1 still leaves a figure taller than me. The designer may change the number, but not L15's "SIX".
5. **Engine changes the script needs:** two new synthesized sfx kinds (the scrape and the creak), and possibly the "mum"/"mom" spelling in `voice.py`. All of them should be opt-in.
6. **Length.** The estimate is the bottom of the range. If the retime lands short, the brief should say where the extra hold goes. I'd put it on P02 first, then the photos after L66, then the smile after L77.
