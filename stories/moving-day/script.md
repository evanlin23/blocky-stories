# ep17-moving-day: the rule-first redo (writer, 2026-11-02)

- **Slug:** `ep17-moving-day` (kept, with the folder).
- **Why it's redone:** it was held because L01 wasn't the world's rule (owner, 2026-11-02, "rule first is necessary"). This is a full rewrite: a new rule, a new big idea and new line ids. The set, the cast, the Boxes model and the best old scenes are reused. The ten pitches are in `notes/pitches.md` → "Redo pitches".
- **Word count:** 369 spoken words in 49 lines, plus 2 pause beats.
- **Estimated length:** about 85 s at 290 wpm with line gaps and the two pauses, so about 88 s with the holds below. That's in the 60 to 90 s test group.
- **Shots:** 57 (S01 to S57), an average of about 1.55 s. A new shot on almost every line, two on the longer ones.
- **The machine-readable lines** are in `generator/lines.json`, rewritten to match this file.

## The big idea

**Our old house was always a ladder taller than any of us, because something tall has always lived with us, and when we moved, it packed itself and came too.**

In a town where every house grows to fit the tallest one living in it, the old house never broke the rule. It was never sized for Mum or me.

## Premise, rule, twist, world

- **Premise:** in this town a house grows, or sinks, to fit the tallest one living in it, a hand a night until it fits. Our old house was always a ladder taller than either of us, and Mum said old houses are just like that. It sold in the spring. The new one is small and fits me exactly, my hair on the ceiling. Mum hasn't laughed since. Then each morning there's more room over my head, the walls have stretched with Mum's photos on them, and the stack of moving boxes by the door is shorter.
- **The rule:** "In this town, a house grows to fit the tallest one living in it." Everyone knows it. Nobody explains it, and nobody is new to town.
- **The twist (the big idea):** the old house never broke the rule. Something tall lived in it with us the whole time, folded under its high ceilings. Mum knew, and never looked up at it. Her grief since the sale was missing it. When we moved, it taped itself into one of our boxes from the inside and came along. The new house is growing to fit it. By the end the ceilings are back to the old height, Mum laughs for the first time since the sale because it's home again (L45b says so plainly), and its box sits on the hall cupboard shelf.
- **Where it's planted:**
  1. L01 says "the tallest **one**", not "person".
  2. L05: the old house was a ladder taller than any of us. That's the exception, and it's the whole twist in plain sight.
  3. L08 (S11): the old house photo Mum hangs. In its top window, small and dim, something pale is bent under the ceiling. A rewatch catches it. The reveal at L41 is the same photo, close.
  4. L10: Mum never looks up. "Old habit." From a house where something lived up there.
  5. L11 to L13: one box nobody packed, taped shut from the inside, its marker frown facing Mum's door.
- **World:** a small single-storey house half moved into: off-white walls, honey boards, a stack of taped moving boxes by the front door, a hall with a cupboard and a low nightlight, a narrow kitchen, a front room with Mum's photos, Mum's room. The ceilings start low (right on my hair) and rise across four mornings to ladder height. Outside, for the montage only, a bright street of houses of very different heights.

## What the hits do, ticked

1. **Line 1 is the rule,** 14 words: "In this town, a house grows to fit the tallest one living in it."
2. **The marker by 2 s:** the ceiling sitting right on the tallest one's head. S01 shows it on me in our hall, lit to read: my block hair flat against the ceiling, a face in frame. The montage shows it on every house in town.
3. **The montage,** 3 examples in L02 to L04 (about 2 to 9 s), played for a smile: a tower house for a tall family, a ceiling coming down a hand a night after a tall lodger leaves, a dinner guest's tall hat raising the dining-room ceiling while the host glares.
4. **The narrator is the exception:** our old house never fit any of us. It was a ladder taller (L05).
5. **The loved one:** Mum, shown by 0:20 (L07 to L10): flat-faced in the small kitchen, hanging the old house photo without a smile, crossing the hall head down past the stack, with the box's marker frown facing her door.
6. **The climax turns the rule:** the second reading. The rule always held. The old house was as tall as the tallest one living in it, and that was never us (L42 to L44). No new magic.
7. **The twist is planted early and the last line loops:** "She CLOSED it / without / LOOKING UP." cuts straight to L01, so across the seam it reads "She closed it without looking up. In this town, a house grows to fit the tallest one living in it."
8. **The first 2 s read on a phone:** S01 is lit warm and even, my face and the ceiling contact in the upper half, the frown box beside me. Darkness comes at L14.
9. **Cut often:** 57 shots in about 88 s.

**Not used:** no mayor, no midnight square, no newcomer opener (we moved within our own town and know the rule), no backstory or flashback before 0:20 (L05 is a line over the photo in Mum's hands, in the present), one forward timeline of four mornings.

## Cast

- `me`: the narrator, an adult. Taller than Mum. The age is never on screen or in the voice. Every word is mine, in voice A.
- `mum`: an adult. Her words are reported in my lines (L09, L37), her mouth flapping under the quotes.
- Montage extras (one shot each, never named, never in peril, all adults): a tall man at a tower house's door, a lodger walking out with a suitcase, a dinner host and a guest in a tall hat. Each is new.
- Nobody is ever hurt or shown hurt. The reach at L31 is side-on and ends on the quilt.

## The creature: "it" (the team's name: the Boxes)

The narration only calls it "it". It's the existing Boxes model from `set.py`, one model, posed per shot.

1. **One model,** built once, posed per shot. Brown cardboard, black marker, packing-tape shine. No box carries a word.
2. **Never seen moving.** Every change happens between scenes.
3. **Its face box is the box nobody packed** (the L11 box): the crushed top corner, tape shine inside the seam gap. The face is a black marker drawing on it, same line weight:
   - the frown: S01, L11 to L13, and on the shelf at L47 to L48
   - the stare: L23 to L24 (down at the back of Mum's head)
   - wide open: L29 to L31, and unchanged through L33
   - in the old house photo (L08 dim, L41 close): a pale square face with the same frown, bent under the top window's ceiling
4. **Where it is, beat by beat:**

| Beat | Lines | Where it is | The stack by the door | The ceiling |
|---|---|---|---|---|
| opening | S01, L06 to L13 | one box in the stack, face out, frown toward Mum's door | full, about 24 | right on my hair |
| morning 1 | L15 to L18 | not seen (only the scrape at L14) | shorter, about 18 | a hand above my hair |
| morning 2 | L19 to L26 | kitchen: its top folded flat along the ceiling, the face box hanging at the end over Mum at the counter, the rest out of frame through the doorway | shorter again, the face box gone from it (L26) | walls stretched, photos higher, about a third of the way to ladder height |
| 3 a.m. | L27 to L34 | Mum's room: bent over her bed, top boxes folded along the ceiling, arms reaching down side-on to the quilt | not seen | creaking upward |
| morning 3 | L35 to L45b | gone | back, all but the face box | ladder height in every room |
| end | L46 to L48 | the face box alone on the hall cupboard shelf, taped from the inside, frown out | back, all but the face box | ladder height |

5. **The arms** are narrow boxes, down at its sides until L31, shot side-on with the box ends in frame, resting on the quilt near the foot of the bed, clear of Mum's shoulders.
6. **It's shown little and late:** a scrape (L14), what it leaves (the gap, the stretched walls, the shorter stack), then only its folded top and face (L22 to L23, about 45% in), then clearly at 3 a.m. (L29, about 57% in), lit from the hall's side with a rim, the face the brightest thing.

## Look, palette, music

- **Palette:** honey boards, off-white walls, cardboard brown, marker black, a cold blue-grey night, warm gold morning sun after 3 a.m. The montage street is bright and saturated.
- **Caption key colour:** `#b98aff` (violet, as in `story.json`).
- **Music:** a minor mode at about 72 bpm. Thin and light under the montage (the smile), one held low note from L11. The heavy low drone enters at L27 ("THREE A.M.") and holds. A 0.6 s drop before L29 (only the voice and a creak). It turns to the major at P02 (the laugh) and stays warm through L39, thins to a single low note from L40, and holds one soft low note under L48 so the cut back to L01 bites.
- **Sound** (all synthesized, existing kinds where they exist): the cardboard scrape (L14), a long wooden creak of the house rising (L27), one low cardboard creak at P01, a cupboard thud at -18 dB on L48.
- **Flash:** `look.flash_safe: true`. The light at L32 comes up over at least 0.5 s. The montage (L02 to L04) cuts no faster than one shot per 1.3 s, and all three montage shots share one exposure (the same bright overcast daylight), so nothing strobes. There is no quick unpacking montage at the end (the old film failed the flash bar there).

## The narration and shot plan

Each line: id, then the caption chunks split with ` / `. CAPS are the key words. Every line is `narrator`. Shots (S) under each line are for the builder. "Mum" rhymes with "come".

### 1. The rule (0 to 10 s)

- `L01` In this TOWN, / a house GROWS / to fit the TALLEST one / LIVING in it.
  - S01 (0 to 1.6 s): our hall, warm even light. Me standing, my block hair flat against the low ceiling, face in frame, upper half. Beside me the stack by the door, its one face-out box showing a black marker frown. This is the 2 s marker and the eerie thing at once.
  - S02: outside, a bright street. Houses of very different heights side by side, each with its tallest person in the doorway, head exactly at the top of the frame.
- `L02` Tall FAMILIES / live in TOWERS.
  - S03: a tower house, narrow and very tall, a tall man at its door waving. Same daylight as S02.
- `L03` When a TALL lodger / moves OUT, / the ceiling comes DOWN / a HAND a NIGHT.
  - S04: a lodger walks out of a front door with a suitcase.
  - S05: inside, a couple on a sofa looking up as their ceiling sits a little lower, a pale line on the wall where it used to be. Same exposure as S04.
- `L04` And NOBODY / wears a TALL HAT / to DINNER.
  - S06: a dinner table, a guest in a tall hat, the ceiling bulged up in a dome right over the hat, the host glaring. The one laugh in the montage.

### 2. Our house (10 to 24 s)

- `L05` Our OLD house / was a LADDER taller / than ANY of us.
  - S07: the old house photo in Mum's hands in our new kitchen, close: a tall narrow house, high windows. (Plant: its top window is dim here.)
- `L06` It SOLD / in the SPRING. / The new one / fits ME.
  - S08: the small house from outside, morning, no number on the door.
  - S09: me in the hall doorway, my hair on the ceiling, a pencil mark on the frame at my height.
- `L07` Mum hasn't / LAUGHED since.
  - S10: Mum in the kitchen doorway, face flat, tired.
- `L08` She hung / the old house PHOTO / at eye HEIGHT.
  - S11: Mum hangs the old house frame in the front room at her eye height. Hold long enough to see the top window: something pale, bent under the window's ceiling, small and dim (plant 3, read on a rewatch).
- `L09` She said, / "No more LADDER."
  - S12: Mum steps back, no smile, mouth flapping under the quote.
- `L10` She never / LOOKS UP. / Old HABIT.
  - S13: Mum crosses the hall, head down, mug in hand, past the stack by the door. In frame at the stack: the face-out box, its frown aimed down the hall at her door.
- `L11` And ONE box / in our STACK, / nobody PACKED.
  - S14: the locked-off wide of the stack by the front door (every morning reuses this frame).
  - S15: me crouched at the face-out box, frowning at it.
- `L12` It was taped SHUT / from the INSIDE.
  - S16: close, side-lit (the old L01 close, reused): the outer seam bare, tape shining through the corner gap from the inside. The box stays shut.
- `L13` Its marker FROWN / faced Mum's DOOR.
  - S17: low, from behind the box: its frown side toward Mum's shut door at the end of the hall.

### 3. The house grows (24 to 46 s)

- `L14` In the DARK, / something SCRAPED / down the HALL.
  - S18: me in bed in the dark, eyes open, not moving. Cardboard scrape.
- `L15` By MORNING, / there was a GAP / over my HEAD.
  - S19: me in the hall doorway again (S09's frame): a hand's width of air between my hair and the ceiling. The pencil mark is below the new top of the frame.
- `L16` The house / had GROWN.
  - S20: low angle up the hall, the ceiling higher.
- `L17` Nobody HERE / is TALLER / than ME.
  - S21: my face, `scared`, looking up into the gap.
- `L18` And the STACK / was SHORTER.
  - S22: the stack's locked-off wide, about six boxes gone, clean squares in the dust. Hold 0.3 s.
- `L19` Next MORNING, / the walls / had STRETCHED.
  - S23: the front room wide, walls taller, the ceiling well above.
- `L20` Mum's PHOTOS / rode UP / with them.
  - S24: the frames now high on the wall, the old house photo among them.
- `L21` Like something TALL / had HUNG them.
  - S25: from below, the frames tilted slightly, as if hung from above.
- `L22` In the KITCHEN, / cardboard was FOLDED / along the CEILING.
  - S26: the kitchen ceiling: a long run of brown boxes folded flat along it, entering from the doorway.
- `L23` At its END, / a FACE / stared DOWN / at the back / of Mum's HEAD.
  - S27: over its face box's shoulder, the box hanging at the end of the run, face down. Face: the stare. Mum at the counter below, her back to it.
  - S28: Mum's back, small, the box face above her at the top of frame.
- `L24` Mum made / her TEA / right UNDER it.
  - S29: Mum pouring tea, head down.
- `L25` She didn't / look UP.
  - S30: close on Mum's lowered face, calm. Hold 0.35 s.
- `L26` In the STACK, / the box / nobody PACKED / was GONE.
  - S31: the stack's wide, shorter again, a clean square where the face box stood. Hold 0.3 s.

### 4. Three a.m. (46 to 61 s)

- `L27` At THREE A.M., / the whole house / CREAKED UPWARD.
  - S32: the hall in the nightlight's cold glow, a long wooden creak, the ceiling's edge rising slowly (ease over the line, no snap). The low drone enters here.
- `L28` Mum's door / stood OPEN.
  - S33: Mum's door, open, darker inside. Then the 0.6 s music drop.
- `L29` It was BENT / over her BED, / TOO TALL / for the ROOM.
  - S34: side-on from the doorway (the old creature-test frame): the Boxes beside Mum's bed, top boxes folded along the ceiling, the face box hanging over her. Mum asleep on her back. Lit from the hall's side, a rim on the silhouette.
- `L30` Built from / our BOXES, / its face / drawn WIDE OPEN.
  - S35: close from below, the face box. Face: wide open (the critic's redrawn upright `wide`). Tempo 0.9.
- `L31` Its long ARMS / REACHED DOWN / to her.
  - S36: side-on, the arms coming down over the bed, box ends in frame above the quilt, clear of her shoulders.
- `P01` pause 1.0 s
  - S36 holds in near silence, one low cardboard creak.
- `L32` I hit / the LIGHT.
  - S37: the dim light on the chest of drawers by her door comes up over 0.5 s or more.
- `L33` Under its HANDS / was the OLD QUILT, / laid over her / the OLD way.
  - S38: close, the box ends resting flat on the patterned quilt near the foot of the bed.
  - S39: high and wide, the quilt laid square and flat over the bed, Mum's face clear and calm. Nothing tucked.
- `L34` Mum SLEPT / right THROUGH it.
  - S40: Mum asleep in the warm light. Hold 0.5 s.

### 5. Ladder height (61 to 71 s)

- `L35` By MORNING, / it was GONE, / and the STACK / was BACK, / all but ONE.
  - S41: Mum's room in morning light, the corner empty, the ceiling high.
  - S42: the stack's wide, back to full height, every box taped, one clean square in the dust where the face box stood.
- `L36` And for ONCE, / Mum LOOKED UP.
  - S43: Mum in the front room with her mug, her head tilting up.
  - S44: her eyeline: the frames at the top of a tall wall under a ceiling at ladder height.
- `L37` She said, / "That's / LADDER HEIGHT."
  - S45: Mum still looking up, mouthing the words.
- `P02` pause 2.0 s
  - S46: the laugh, held, one shot in low gold sun: her shoulders first, then her face from `grin` to `squeeze`, a lean. The score turns to the major. No laugh sound.
- `L38` She LAUGHED / till she / had to SIT.
  - S47: Mum sits on a box from the stack, still laughing.
- `L39` Her first LAUGH / since the SALE.
  - S48: a two-shot, me laughing too, the room tall around us. Hold 0.3 s.

### 6. The old house (71 to 88 s)

- `L40` I looked UP / at the old house PHOTO.
  - S49: from below, the old house frame at the top of the wall. The music thins to one low note.
- `L41` In its TOP WINDOW, / something TALL / was BENT / under the CEILING.
  - S50: close on the photo, slow push to the top window: a tall pale shape folded under the old house's high ceiling, its square face wearing the frown. Lit to read. Hold 0.4 s. This is the reveal picture.
- `L42` The old house / never BROKE / the RULE.
  - S51: Mum below, laughing quietly, head back, the old photo above her.
- `L43` It was always / as tall / as the tallest one / LIVING in it.
  - S52: low and wide, the front room at ladder height, Mum and me small at the bottom of a tall wall. Tempo 0.92.
- `L44` That was / never US.
  - S53: my face, looking up. Hold 0.4 s.
- `L45` It came / WITH us.
  - S54: the stack by the door, back to full height, the clean square in the dust where the face box once stood.
- `L45b` Mum KNEW. / She'd MISSED it.
  - S54b: Mum below the old photo, head tipped back to it, her laugh gone soft, eyes wet. She looks at the photo, not at the ceiling. Hold 0.4 s.
- `L46` Mum opened / the hall CUPBOARD.
  - S55: the hall, Mum opens the cupboard, head down.
- `L47` On the SHELF / sat ONE box, / taped / from the INSIDE.
  - S56: inside the cupboard: the face box alone on the shelf, the frown out, tape shine inside the corner gap, framed like S16. Still. Hold 0.45 s.
- `L48` She CLOSED it / without / LOOKING UP.
  - S57: Mum swings the door shut, head still down. The box doesn't move. A cupboard thud at -18 dB on "UP". 0.25 s after the last word, a hard cut to S01. Tempo 0.88, the slowest line.

## The connection to `stories/lore.md`

None, on purpose. The canon's Keepers are each tied to one place, and this thing moves with a family, so calling it a Keeper or stamping a tally would contradict the canon. The lore link is optional (RULES → The shared world is optional now), and the big idea stands on its own.

## Say-it-out-loud notes

- **L01:** bright and quick, wonder first. "TALLEST one" lands by 2 s.
- **L02 to L04:** light, nearly a joke. L04 is the punchline.
- **L05:** plain. It's the twist in plain sight, so don't lean on it.
- **L10 "Old HABIT."** Throwaway.
- **L12 "from the INSIDE."** Slow a touch.
- **L17:** quieter.
- **L25:** plain and flat.
- **L30:** tempo 0.9. Then hold P01 in full.
- **L32:** clipped.
- **L34:** quiet, gain -1.5 dB, a 0.5 s gap after.
- **L37:** dry, it's Mum's joke.
- **L45b:** plain and warm, a beat after "Mum KNEW." It's the feeling, not a clue. Gap 0.4 s after.
- **L42 to L44:** slow and plain. L43 at tempo 0.92. "never US" with a beat after.
- **L48:** the slowest line, tempo 0.88. Land "UP" low and don't trail off.
- **For Whisper:** "Mum" (said 10 times) may come back as "mom" (see the old notes on `SPELLINGS`). "three a.m." at L27: if Kokoro reads "a.m." as "am", change only the spoken text to "three A M". "hung"/"hang" and "rode"/"road" are spellings, not mistakes.

## Notes for the builder

- **Reused as is:** the house set (hall, kitchen, front room, Mum's room, the stack by the door, the hall cupboard), the Boxes model and its `pose_boxes` poses for Mum's bed (S34 to S39), the marker faces `frown`, `stare` and `wide`, the quilt, the dim light at her door, the nightlight, the photos high on the wall (now riding up rather than re-hung), the inside-tape box close (S16, reused at S56), the stack's locked-off wide, Mum's laugh (S46), Mum sitting on a box (S47), the cupboard shot.
- **Changed:** the ceiling height is now a per-scene value: right on my hair (opening), plus a hand (morning 1), about a third of the way to ladder height (morning 2), rising during S32, ladder height (morning 3 on). The walls and the photos on them scale up with it, so the frames ride up. The kitchen pose is new: the Boxes' top run folded flat along the kitchen ceiling with the face box hanging at the end and the body out of frame through the doorway (S26 to S28). The face box is now one box in the stack (S01, S13 to S17) and the shelf box at the end, frown out.
- **New:** the three montage exteriors and interiors (S02 to S06: a street of mixed-height houses, a tower house, a lodger and a lowered ceiling, a dinner with a tall hat and a domed ceiling), each with new extras. The old house photo prop, in two uses: dim at eye height (S07, S11) and close at the reveal (S50), showing a tall narrow house and, in its top window, a pale tall shape bent under the ceiling with the frown. A pencil height mark on my doorframe (S09, S19).
- **Cut:** the shelf box as the Boxes' "bottom box", the stack shrinking to nothing, my room at dawn (the many-eyes face), the sideways-eyes front room, the tape cores, the pull-apart, the unpacking montage.
- **Cover:** `cover_s` 49.2 (S34, the Boxes bent over Mum's bed). Not S50: the photo's top window is the reveal.
- **Standards words:** no death, weapon or gore words, no child words, nothing claimed true, no real place or brand. No words on any box, sign or photo.
