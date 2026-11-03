# ep32-sitter: the script (writer, revival 2026-11-03)

- **Slug:** `ep32-sitter` (revival path b, `docs/research/2026-11-03-revival-triage.md` → "### 1. ep32-sitter"). A new story under hard rule 5: new script, title, twist. The folder name stays for the plumbing.
- **Engine:** the old myth of a sculptor whose statue comes to life (a made person), never any specific work's plot.
- **Target length:** the 60 to 90 s arm (playbook H1), at its long end: about 86 to 90 s.
- **Word count:** 349 spoken words in 36 lines, all `narrator`, voice A. At 290 wpm the speech is about 73 s, plus about 12 s of line and chunk gaps, two music drops and the 0.25 s tail, so about 86 to 90 s. The reveal (L23 to L26) starts about 57 s in, inside the last 30 s. If long, cut L29 first (the salt), then L33. If short, add "He knew where we KEEP / the SPOONS." after L20.
- **Tense:** past, first person. L01 to L07 and L34 to L36 are present (how the town is, how things are now). Kofi, Mom and Theo only ever speak inside my lines.
- **Opening:** `ban` (line 1 "Never..."). ep80, mirror-maze and moving-day are also `ban`, so the uploader has to space them (at most 1 in 4 a week).
- **Quotable line (marked):** L23, "Mom didn't SCREAM. / She set him a PLACE."

## Changed for the builder (revival, 2026-11-03)
Every line is new, so re-voice everything once (ids restart at L01, and the old L01 to L40 are all gone). The old `voice-timings.json` is stale.

**story.json text** (already pasted, so `check` compares the new story):
- `title`: "Never Paint A PERSON In Here 🖌️"
- `premise`, `twist`, `world`: as in story.json now, matching the sections below.

**New**
- **Theo (`theo`, new cast):** my big brother, painted. An adult, early twenties, a head taller than me (height about 1.08). Brown block hair with a swept fringe, brown eyes, a wide easy grin, a forest-green zip jacket over a cream tee, dark jeans, tan boots. As pine: every surface raw pine (`pine_mat`) with grain, the face graphite guide lines only (a cross, two eye ovals, one mouth line, no nose). **The fill climbs from the boots up** (the reverse of the old restore): Tuesday fill 0, Wednesday colour to the chest, Thursday full colour except a **nose patch** (a small square of bare pine grain on the face centre with a graphite nose outline). Finished, the patch becomes a short drawn ink nose stroke on skin like the rest of his face.
- **The ear patch (plant 1):** a decal on the left side of my head where an ear sits: a patch of raw pine grain about 1/6 of head height, with one faint graphite curve of an ear outline. It's on `me` in every shot, and it has to read at phone size in S07 (a close at about 12 s).
- **The pine bench (montage):** a plain slatted bench at the bus stop, as raw pine with graphite construction lines (S04), then coloured a bright green over about 1.5 s (S05, a ramp).
- **The rule meter (needed from frame 1 to the last):** seven small rounded squares in a row at the top of the frame, above every face and outside the caption band. Each one is a day, Monday on the left, and the fourth (Thursday) has a little graphite brush tick under it. Today's square is bare pine with a pencil outline, and the days before it are filled with colour. It steps each time the story's day changes (L03 Monday, L04 Tuesday, L05 Thursday, L09 Monday, L15 Tuesday, L17 Wednesday, L18 Thursday, L31 Monday, L34 the new week). No letters, no numbers. The opt-in `meter` overlay built for night-mower (commit 74d4ef6, branch `claude/batch6-p3-night-mower`) is the starting point.
- **The dinner table:** the cafe's table-for-two prop moved to the dining end of Mom's hall, plus a third chair and three plates.
- **Mom's old easel (bonus plant):** a folded easel in Mom's hall with an old pine panel turned face to the wall, in the background of S09 and S23, then set up in the life room at S33.

**Dropped:** the faded-face rule and the fade-from-loneliness story, faded Mum on the stool, the fruit bowl as plant, the power dip, the rain, Mum's home portrait, my flat corner, the phone, the sting sitter, Petra's car park beat and her pear.

**Kept (reused):** the life room, the eight easels, the dais and stool, the car park and its window shot, Mom's hall, the montage sets (bus stop, cafe, bakery), the pine-and-guide-line shader (`pine_mat`, `fade_setup`, `fade_update`, now driven upward on Theo), Kofi, Mom (cast key `mum`, said "Mom" everywhere), Petra (now the new student at the end), Mr Dobbs (`ade`, a bench sitter in the montage) and the background painters.

## Big idea (the one sentence)
In a town where whatever Kofi's art class paints comes to life by Thursday, I break the one rule and paint the big brother I always wanted, and Mom just sets him a place at dinner, because eighteen years ago she broke it too: she painted me.

## Premise
Kofi's art class paints the town: a bench, a cake, window flowers, and each one turns up a few days later, first as bare pine with the pencil lines still on it, then filling in with colour. The one rule is never paint a person. I've always wanted a big brother, and Mom says one of me is plenty. So I join the class and paint one, Theo. I stop at his nose when Kofi turns the lights off. By Tuesday a pine man with a pencil face is standing in our hall, one step nearer my door each night.

## Rule
"Never paint a person in Kofi's class. Paint the town." Then the rule itself: whatever the class paints shows up in town by Thursday, bare pine and pencil guide lines first, then the colour fills in.

- **Marker by 2 s:** a pine panel on an easel with a face half painted and half bare pine and pencil (frame 1), and the week meter at the top of the frame.
- **Montage (3 to 5, in the first 15 s):** the bench on Monday's panel (S03), the bench turning up at the bus stop as bare pine with pencil lines and people sitting on it anyway (S04), the bench going green (S05), a bakery cake with its frosting still filling in (S05b), the cafe's window flowers stuck half pencil because their painter moved away (S06).
- **Seconds 15 to 30:** I want a brother, the class, Kofi's brush remark, the panel. Nobody explains the rule.
- **The narrator is the exception:** I'm already a little bit pine (the birthmark, L07). The reason is the reveal.
- **The loved one at stake:** Mom, in a picture at 0:15 (S09, the two of us in her hall), and the brother I want.
- **The loophole the climax turns:** the montage shows a thing only fills in all the way if its own painter finishes it (the flowers, L06). So I'm the only one who can finish Theo's nose, and Mom is the only one who can finish my ear.

## Twist
Eighteen years ago Mom took Kofi's class, broke the rule and painted me. That's why she doesn't scream when a painted man comes down to dinner: she sets him a place. Said plainly at L23 to L26 over one picture: Mom's fingertip on the bare pine patch on my head, her folded old easel behind us.

- **Plant 1, the ear:** "a patch of bare PINE I've always called a BIRTHMARK" (L07, S07, a close at about 12 s), right after we've seen that painted things start as bare pine. Paid at L28 ("She stopped at my EAR").
- **Plant 2, the brush:** Kofi says I hold a brush exactly like someone he taught years ago (L10). Paid at L27 ("The student Kofi meant was MOM") and echoed at L33.
- **Plant 3, the easel:** Mom's folded easel and the panel turned to the wall, in the back of S09 at 0:15. A rewatch sees it.
- **Plant 4, "one of me is plenty":** a joke at L08, and on a rewatch, a mother who already painted the one she wanted.

## The last 15 seconds
L32 to L36: Mom at her old easel beside mine finishing my ear, Kofi saying we hold our brushes exactly the same, then this week's new student turning her panel to the wall, a half pine face behind it, and "So I tell every new student the same THING." The loop cut lands on L01 over that same half pine panel, so the warning plays as the thing I say, and frame 1 becomes the next brother or sister someone is painting. On a second watch the birthmark, "one of me is plenty" and Kofi's remark all read as Mom's story.

## World
A bright little town where Kofi's art class paints new things into it. The class paints on pine panels, so whatever isn't painted yet is bare pine with the pencil lines on it, the same look as a thing that's just arrived. Daylight montage: a sunny bus stop with the new bench, a bakery counter with a cake in the window, a cafe window with a flower box (no signs, no text). The community arts centre's life room on Monday afternoons into dusk: cream plaster walls, a honey-board floor, a tall north window, eight easels in a curve with clamp lamps, a low pine dais with a plain stool. The car park at dusk under one lamp post, looking back through the lit window. Mom's front hall: stairs, hooks, a folded easel against the wall, and a little dining end with a table. My room only as the foot of my bed in morning light. No text anywhere.

## Cast (all adults, nobody in peril)
- **Me (`me`):** an adult, no age on screen. Black buzzed block hair (so the ear patch shows), a mustard knit sweater, charcoal pants, white sneakers. The ear patch in every shot. Easel 8, by the window.
- **Mom (`mum`):** my mom, fifties. Silver block bob, round tortoiseshell glasses, a teal check cardigan over a cream top. Calm, warm, a little dry. Kofi taught her years ago.
- **Theo (`theo`, new):** my big brother, painted. As above. Kind, grinning, never menacing once he's in colour.
- **Kofi (`kofi`):** runs the art class, fifties (he taught Mom eighteen years ago). Shaved head, round black glasses, rust shirt, denim apron. Says the brush line and nothing about the rule.
- **Petra (`petra`):** the new student at the end, thirties. Copper bun, navy and white striped top.
- **Mr Dobbs (`ade`):** a bench sitter at the bus stop. **Extras:** two passers-by, a baker and a customer, five background painters at easels 2 to 6.

## The creature: pine Theo (continuity)
- **Look:** Theo's R6 body at his height, all raw pine (`#d8b98a`) with grain and two dark knots, graphite guide-line face: a cross, two empty ovals, one mouth line, no nose. Never seen moving, only already somewhere new. Leans in from the waist, never touches.
- **Light it:** the hall at night is lit by one warm wall lamp from the side and a cool rim from the stair window, front fill low. The empty ovals are the palest thing on him. Readable at phone size. Coloured Theo is lit warm and bright.
- **Where he is:**
  - S12 to S15: only on my panel (pencil and paint, the face finished except the nose).
  - S16 to S17 (Tuesday night): standing at the far end of Mom's hall by the stairs, all pine, facing my door.
  - S18 (Wednesday night): halfway down the hall, one step from my door, colour up to his chest (boots, jeans, jacket hem), the rest pine.
  - S19 to S22 (Thursday morning): at the foot of my bed in sunlight, full colour, the bare pine nose patch, leaning in at S22.
  - S23 to S30 (Thursday dinner): coming down the stairs, then at the table in the third chair, still with the nose patch.
  - S32 (Monday): on the dais stool as my sitter, the nose filling in.
  - S33 on: finished, warm, grinning. The pine never comes back on him.

## Palette and sound
- **Palette:** bright and saturated. Montage in sunny primaries, the new bench a bright grass green. The life room warm afternoon light going gold. Raw pine, graphite grey, Mom's teal, Theo's forest green, my mustard. The one dark-ish scene is the hall at night (S16 to S18), lamp-lit and readable. Thursday morning is bright.
- **Caption key colour:** bench green `#5fd068` (the first thing we see fill in).
- **Music:** F Lydian, 96 bpm, light plucked pulse and pad from L01 to L15 (wonder, played a little funny). A low drone enters at L15 (the pine man in the hall) and holds to L23. Music drops (voice and hit only) 0.6 s before L20 ("Morning, little BROTHER") and 0.7 s before L23 ("Mom didn't SCREAM"). D major, 84 bpm, warm pad and piano from L24 to L33. L34 to L36 back to a thin cold drone, then the closing sound.
- **Hits:** a soft low hit on "TOWN" (end of L01), on "BIRTHMARK" (L07), on "HALL" (L15), on "BROTHER" (L20) and on "PLACE" (L23). A soft rising paper shimmer under each colour fill (S05, S32, S33).
- **Lights off (L13):** Kofi's clamp lamps ramp from 100% to 35% over 1.2 s and cut while dim. Never full dark. Pre-check with `flash`.
- **Closing sound:** under L36, one low two-note chord falling a fifth at about -16 dB, then 0.25 s to the loop cut.

## The lore plant
Nine short graphite strokes, plain, no extra stroke, along the front edge of the life-room dais (the class's own count). Seen in S32 under L31, the dais edge across the lower middle of the frame above the caption band, under Theo's boots, held about 1.6 s. Never narrated. `stories/lore.md`'s ep32 row still points at the old S39 and L39, so it needs this shot and line.

## Shot plan and narration
Format: id, who, caption chunks split with ` / `, CAPS are key words in green. Shots under each line, a cut or punch-in every 1 to 2 s. The week meter is on screen in every shot.

### 01 The rule (0 to about 13 s)
- `L01` narrator: Never paint a PERSON / in Kofi's CLASS. / Paint the TOWN.
  - [S01: frame 1, close on a pine panel on an easel, bright afternoon light: a face, its left half painted in colour, its right half bare pine with a graphite cross and one empty eye oval. Push in. The meter at the top. Soft hit on "TOWN"]
  - [S01b at "CLASS": punch in on the line where paint stops and pine begins]
- `L02` narrator: Even someone / you MISS.
  - [S02: the same panel, a quick push to the empty pencil eye. Meter on Monday]
- `L03` narrator: Whatever his art class PAINTS / shows up in town / by THURSDAY.
  - [S03: the life room, a panel with a painted green bench. S03b: the meter steps toward Thursday as we cut]
- `L04` narrator: Bare PINE first, / with the PENCIL LINES / still ON it.
  - [S04: the sunny bus stop: the new bench, raw pine with graphite construction lines, Mr Dobbs sitting on it anyway. S04b: close on a pencil line along a slat]
- `L05` narrator: Then the COLOR / fills IN.
  - [S05: the bench ramps from pine to bright green over about 1.5 s, Mr Dobbs looking down at it, pleased. S05b: the bakery window, a cake whose pink frosting is still filling in up one side, the baker and a customer staring at it]
- `L06` narrator: The cafe's flowers / are still half PENCIL. / The painter moved AWAY.
  - [S06: the cafe window flower box, red flowers on the left, pencil outlines on bare pine on the right. S06b: punch in on the pencil half]
- `L07` narrator: And behind my EAR, / there's a patch of bare PINE / I've always called a BIRTHMARK.
  - [S07: me in the cafe window's reflection, then a close on the side of my head: the ear patch of raw pine grain with one faint graphite curve. At about 12 s. Hit on "BIRTHMARK". Plant 1]

### 02 The want (about 13 to 34 s)
- `L08` narrator: I've always wanted / a big BROTHER. / My mom says / one of me is PLENTY.
  - [S08: Mom's front hall, bright: Mom (silver bob, glasses, teal cardigan) smiling at me, a hand on my shoulder, the two of us only. S09: the wider hall, Mom's folded easel against the wall with a pine panel turned to it (plant 3)]
- `L09` narrator: So on MONDAY, / I joined Kofi's art CLASS.
  - [S10: me on the arts centre steps in sun, a pine panel under my arm. S10b: the life room, eight easels round the dais, Kofi waving me to easel 8]
- `L10` narrator: Kofi said I hold a brush / EXACTLY like someone / he taught YEARS ago.
  - [S11: Kofi beside me, looking down at my hand, off frame, a small puzzled smile. S11b: the brush tip on the panel, no hand in frame. Plant 2]
- `L11` narrator: Everyone else / painted the BUS STOP. / I painted my big brother, THEO.
  - [S12: over a painter's shoulder, a bus-stop panel. S12b: my panel, a young man's figure in pencil, colour going in: green jacket, brown hair]
- `L12` narrator: Older than ME, / and always on MY side.
  - [S13: my panel close, Theo's painted grin and brown eyes, his face centre still bare pine. S13b: me, proud, the ear patch in frame]
- `L13` narrator: I got as far / as his NOSE / when Kofi turned the lights OFF.
  - [S14: Kofi at the switch, the clamp lamps ramping down to 35%, cut while dim. S14b: my panel, a pine square with a pencil nose outline where the nose should be]
- `L14` narrator: From the car PARK, / his face on my EASEL / was looking OUT.
  - [S15: the car park at dusk under the lamp post, me looking back. S15b: through the lit window, my panel on easel 8, Theo's painted eyes turned to the glass]

### 03 Tuesday to Thursday (about 34 to 54 s)
- `L15` narrator: On TUESDAY, / a man of bare PINE / was standing in our HALL.
  - [S16: Mom's hall at night, one wall lamp, the drone enters: pine Theo at the far end by the stairs, facing my door. Hit on "HALL". S16b: me in my doorway, frozen]
- `L16` narrator: Pencil lines / for a FACE.
  - [S17: close on his face, the cross and two empty ovals the palest thing, no nose]
- `L17` narrator: WEDNESDAY, / the color had climbed / to his CHEST, / and he was one step / nearer my DOOR.
  - [S18: low, from my doorway: pine Theo halfway down the hall, boots to chest in colour, jacket hem green, the rest pine. S18b: his feet one board from my threshold]
- `L18` narrator: THURSDAY MORNING, / he was at the end / of my BED.
  - [S19: bright morning, from my pillow: Theo at the foot of my bed, full colour. S19b: me sitting up fast, the ear patch toward camera]
- `L19` narrator: In full COLOR, / with a bare pine NOSE.
  - [S20: close on Theo's face, warm skin, brown eyes, the pine nose patch with its pencil outline]
- `L20` narrator: He leaned in and said, / "Morning, little BROTHER."
  - [S21: music drop 0.6 s before. S22: 3/4, Theo leaning in from the waist, his face a hand from mine, grinning. Hit on "BROTHER". Never touches. Cover frame]
- `L21` narrator: I hadn't told MOM.
  - [S22b: me, eyes going to the door]

### 04 Dinner (about 54 to 72 s)
- `L22` narrator: At DINNER, / Theo came down the STAIRS / and sat at the TABLE.
  - [S23: Mom's hall, warm evening light, the dining end: Mom at the table, Theo coming down the stairs. Mom's folded easel in the back. S23b: Theo in the third chair]
- `L23` narrator: Mom didn't SCREAM. / She set him a PLACE.
  - [Music drop 0.7 s before. S24: Mom calmly laying a third plate in front of Theo. S24b: me, stunned. Hit on "PLACE". **Quotable line**]
- `L24` narrator: Then she touched the pine / behind my EAR, / and told me.
  - [S25: THE PICTURE. Mom's fingertip on the ear patch on my head, her face close and kind, her folded easel with its panel turned to the wall behind us. Hold it. D major comes in]
- `L25` narrator: Eighteen years AGO, / she took Kofi's class TOO.
  - [S26: the life room, a wide of the eight easels in afternoon light, nobody there. S26b: Kofi's glasses catching the lamp, as if remembering]
- `L26` narrator: She broke the RULE. / She painted ME.
  - [S27: Mom across the table, a small guilty smile. S27b: me, the ear patch in frame, getting it]
- `L27` narrator: The student Kofi meant / was MOM.
  - [S28: Mom's old folded easel in the hall, close, paint-worn]
- `L28` narrator: She stopped at my EAR, / and never dared touch / that canvas AGAIN.
  - [S29: Mom, glasses off for a second, looking at me like she's still scared to change a line. S29b: the old panel, turned to the wall]
- `L29` narrator: Theo asked / for the SALT.
  - [S30: Theo, grinning, a hand out, Mom sliding the salt to him with her other hand off frame. Played for the laugh]

### 05 Finishing (about 72 to 82 s)
- `L30` narrator: Mom said only the one / who PAINTED you / can FINISH you.
  - [S31: Mom and me in her hall, the old easel being unfolded, cut before hands meet it]
- `L31` narrator: So on MONDAY, / Theo sat on the DAIS, / and I painted his NOSE.
  - [S32: the life room, bright: Theo on the dais stool as my sitter, the nine strokes on the dais edge under his boots (lore plant, held 1.6 s), his nose patch warming to skin. S32b: me at easel 8, side on, steady. Cut away before a hand meets the panel]
- `L32` narrator: Mom set up her old EASEL / beside mine, / and finished my EAR.
  - [S33: Mom at the easel beside mine, her old panel back to camera, her face just over its top edge, concentrating. S33b: close on my head, the pine patch warming to skin over about 1.5 s, paper shimmer]
- `L33` narrator: Kofi said / we hold our brushes / EXACTLY the SAME.
  - [S34: Kofi behind us, arms folded, smiling. S34b: two-shot, Mom and me at our easels, Theo grinning on the dais]

### 06 The new student (about 82 to 89 s)
- `L34` narrator: This week, the new student / turned her canvas / to the WALL.
  - [S35: the life room, colder light, the drone back thin: Petra at easel 7 turning her panel to the wall, glancing around]
- `L35` narrator: Behind it, / a HALF PINE face.
  - [S36: from behind easel 7, the panel's front: a face half painted, half bare pine and pencil (the same framing as S01)]
- `L36` narrator: So I tell every new student / the same THING.
  - [S37: me at Petra's shoulder, kind, about to speak. Closing chord, 0.25 s, loop cut to S01]

## Notes for the builder
- Hands never grip: cut away at S11b, S30, S31, S32b and S33. The brush is only ever seen by its tip on a panel.
- S22: Theo leans from the waist, a hand's width clear of my face. Check it against the bed frame.
- S25 is the reveal picture: Mom's fingertip on the ear patch, the patch and her face both large, out of the caption band.
- The ear patch must be the same decal in every shot of me until S33b, then gone for good.
- Theo's nose patch is on him from S20 to S32 and gone after.
- The week meter changes only on cuts, never mid-shot.
- No text on panels, signs, the bakery, the cafe or the bus stop.
- Cover (`cover_s` 52.0, estimated): S22, Theo in colour with his pine nose leaning in at me, caption "little BROTHER". Re-set it from the timings.
