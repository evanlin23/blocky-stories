# ep16-lookout: the script, redo 2 (writer, 2026-11-02)

- **Slug:** `ep16-lookout` (unchanged, `story.json` already has it).
- **Why redone:** held with "redo: the first line must state the world's rule" (owner, 2026-11-02). The old opener was a question ("How do you LOSE something TALLER than the TREES?") with no rule, and the old twist (a lost forest giant steering by my lamp) was a fact, not a floor dropping away. This version is rebuilt on one big idea, rule first, at about 90 s.
- **The big idea (one sentence):** in a valley where time runs slower the higher up you are, I spend four nights alone in the highest lookout, and the tall stranger who climbs my stairs on the fourth is my teenage brother, now older than me, who spent twenty years moving higher up the valley so he'd never get too far ahead of me.
- **Shape tag:** `time-gap` (new). Not `stand-in`, no Keeper, no creature.
- **Target length:** 60 to 90 s, about 1:30 at most.
- **Word count:** 380 spoken words in 46 lines, all `narrator`, plus 4 pause beats (3.1 s in all).
- **Estimated length:** at 290 wpm the speech is about 79 s. The 0.12 s gaps add about 5.5 s, the pauses 3.1 s and the loop tail 0.25 s, so about 1:27 to 1:31. Rough marks at 290 wpm: Ollie on screen 0:14, "Goodnight, SPARROW" 0:44, the man in the door 0:55, "It's OLLIE" 1:01, the rule again 1:20. If it runs over 1:32, cut L23 ("A NEW ranger. / A MAN.") first, then L02. If it lands under 1:24, leave it: shorter is better.
- **Look:** `look.flash_safe: true`. Every light change ramps 1 s or more. The town window "lighting up" at L14 is a 1.2 s fade up, and it never blinks after that (it's a steady glow by design, see the twist).

## BUILDER: what changes and what's reused

Read this first. Everything not listed under "Change" or "New" stays as it is in `set.py` and `story.json`.

**Reuse as is**
- The tower: the 4 x 4 m glass cab on braced steel legs at CAB_Z 19.6, the catwalk and rail, the 112 switchback stairs inside the legs, the hatch, the plank gate and fence 6.2 m south of the tower.
- Inside the cab: the cot, the lamp on its bail (`#ffb22e` glow), the black radio with its green light, the binoculars (and the binocular POV look `bino`), the log sheet (keep it blank).
- The ridge, terrain, the autumn pine and larch forest, `pine_data()` / `place_pine()`, the fog cards, the night glass, the `day`, `dayfar`, `night`, `nighthigh` looks.
- Cast `me` exactly as in `story.json` (adult, plaid, hood, cap hair). Same voice settings, key colour `#ffb22e`, gap 0.12, tail 0.25.
- The radio beat: green light on, click, static burst, light off (L15, L22). Her/his audio never plays.

**Change**
- `generator/lines.json`: replace with the 46 lines and 4 pauses below (old L01 to L73 and P01 to P06 are all gone, and ids are renumbered from L01). Then rerun `generator/make_story.py` and re-voice every line.
- `story.json` fields: `premise`, `twist`, `world` (text below), `title` to the package title, every `lines`, `shots`, `acting`, `cues`, `fx`, `music`, `sound` entry. `look.flash_safe: true`.
- The pines' height becomes a per-night cue: night 1 scale 1.0, night 2 about 1.12, night 3 about 1.28, so on night 3 the treetops reach the catwalk rail (the brush and scrape at L21). Ramp nothing on camera: each night is a new look.
- The valley below the cab at night: the old river, smoke layer and burn smudge go. In their place, the town's lights (see New). Fog sits on the valley floor at night as before.
- Music: the same dorian, root 40, but 72 bpm for the montage (thin, light, a little playful: `pad` and `piano`), down to `drone` and `pad` from L13, then the heavy low drone enters at L24 ("Goodnight, SPARROW.") and holds to the end. `music_drops` at P02 (0.7 s) and P03 (0.6 s), voice and hit kept.

**Remove (unused now: delete or leave unposed, but nothing of them on screen)**
- The giant (`build_giant`, `pose_giant`, its lights, stones, saplings, hollow), its footprints, the snapped treetops line, the tower lean and `shake`, the fire road walk, the rocky shelf, the river, the controlled-burn smoke, the spring saplings in prints.

**New**
- **The marker, on every character, from frame 1:** a small glass hourglass floating a hand above each head, about head width, pale brass caps, with glowing pale-gold sand (`#ffd98a`, emission low) falling from top to bottom. The rule is shown by how fast the sand falls: a gush for people low in the valley, a thin trickle up high, a few slow grains at the top of the tower. It's driven by one value per character per shot, `sand` (0.05 to 1.0), so it never changes inside a shot except where the plan says. The grains are small and steady. Nothing pulses or blinks (hard rule 7).
- **The town (montage set, day, bright, closer-style colours are fine):** a small sloping street of blocky houses on the valley side, in noon sun, no fog. Parts: a house with a high balcony over a pavement (L01), a cottage with an attic dormer window and a front garden (L03), a cellar with a stool and a pavement hatch (L04), an office front with a basement window row (L05). No text, signs or numbers anywhere. The parcel is a plain brown box with string.
- **The town at night, seen from the cab:** a cluster of warm window points on the valley floor. Night 1: a small cluster, one window marked as Ollie's (`ollie_win`, low on the valley floor). Night 2: more lights, and Ollie's lit window is now in a house higher up the hillside (`ollie_win2`). Night 3: the lights have spread up both valley sides, about twice as many, and Ollie's light is in the ranger's hut on the far ridge (`hut`, a small timber hut with one window, across the valley at about the cab's height minus 30 m). Ollie's light is always the warmest point in frame and always steady.
- **Cast `ollie` (teen):** my brother, a head shorter than me, block hair in dark brown, a red knit beanie with a cream band, a mustard rain jacket over a grey shirt with a cream chevron of our own, dark jeans, white trainers. Round eyes, brows, a quick grin. His sand gushes. `age: "teen"`. Only in L08 to L10, in daylight, never in peril.
- **Cast `ollie_old` (adult):** the same face design so a viewer knows him in one look, but taller (adult height, taller than me), a short block beard in dark brown going grey at the sides, the same red beanie faded to a dusty rose with the cream band, a dark green ranger's jacket with a plain brass glyph badge (our own: a circle over a bar, no words), a key on a ring at his belt. `age: "adult"`. Faces: `neutral`, `soft`, `smile`. L31 to the end.
- **The old ranger:** never seen, never heard. Only reported (L15).
- **Keys:** a plain iron key on a nail by the cab door (L12), and its twin on `ollie_old`'s belt ring (L41).
- **The light crossing the valley (L26 to L27):** one warm lamp point moving slowly from the hut, down into the valley fog (it glows through it), and up our ridge. Slow, steady, never blinking.

## The story

- **Premise:** In a valley where time runs slower the higher up you are, I take a one-week shift alone in the fire lookout on the highest ridge. My brother Ollie, still a teenager, walks me to the gate and makes me promise to flash my lamp at ten every night so he can flash back. His window light answers, then never goes dark, and each night it's somewhere higher up the valley.
- **Rule / hook:** "In this valley, time runs slower the higher up you are." Shown by an hourglass over every head, its sand gushing low down and trickling up high.
- **Twist:** The tall stranger who climbs my 112 stairs on the fourth night is Ollie, older than me now: four nights for me were twenty years for him. His window never went dark because he flashed it every night, seven thousand times, and from up here it blurred into one light. Every year he moved a little higher (a hillside house, then the ranger's hut) to slow his own sand, so he'd never get too far ahead of me, and he became the ranger to get the other key.
- **World:** A valley town of blocky houses in noon sun with an hourglass of falling sand over every head, and above it, on the highest ridge, a fire lookout: a glass cab on steel legs 112 stairs up, a catwalk, a lamp, a radio, autumn pines that grow taller each night, and the town's lights spreading below in the fog.
- **Where the twist is planted:**
  1. L16, about 29 s: Ollie's window "doesn't go DARK. It stays LIT ALL NIGHT." First watch, he's left it on. Second watch, it's thousands of nights of flashes.
  2. L17 and L20, about 31 s and 37 s: his light is higher each night, then in the ranger's hut. First watch, something is coming closer. Second watch, he's moving up to slow down.
  3. L12, about 22 s: "The RANGER has the only other KEY." Paid off at L41 with the key on his belt.
  4. Picture only: the pines grow each night (L18, L21) and the town spreads (L19). Years passing, never said until L36.
  5. L09: "He calls me SPARROW." Paid at L24, the scare.
- **How the last 15 s turn over the first line:** the first time, "time runs slower the higher up you are" is a joke about grandads in attics. At the end it's the cost of the job I took and the gift Ollie gave: he spent his life climbing so the gap would stop growing. L44 says the rule again, in new words, over the two of us side by side with our sand falling at the same speed, and L45 to L46 land cold: we walk down in the morning, and I don't know what year it'll be.
- **The climax turns the rule's logic:** no new magic. Ollie used the rule itself: higher means slower, so he kept moving higher until he could stand at my height and share my time.
- **Ending shape:** a held two-shot in the night cab, Ollie and me on the cot, two hourglasses at the same slow trickle, the town's lights below. Then the last line over the cab from outside, one amber lamp, the valley lights below it slowly shifting.
- **Warmth:** devotion. A brother who spent twenty years climbing toward me. Shown, not told: he sits down beside me, and our sand matches.
- **The scare (about 45 to 62 s):** a man's voice on the radio uses a name only Ollie uses, a light crosses the valley toward my tower, the locked gate clanks open, slow heavy steps climb the stairs, and a tall man fills my door, lit from below, his face in shadow.
- **Lore connection:** none. It's optional now (RULES → Deep lore: "never required"), and this story's idea stands alone. No tally, no Keeper.

## Cast

- `me` (adult, the narrator): reused from `story.json`. No age on screen or said. Faces: `neutral`, `smile`, `puzzled`, `worried`, `scared`, `terrified`, `wide`, `soft`.
- `ollie` (teen) and `ollie_old` (adult): see "New" above. Same face design, so the reveal reads in one look.
- Montage extras (adults, all with hourglasses): `balcony` (a woman in a lemon cardigan on the balcony, sand trickling), `walker` (a man in a blue coat on the pavement below, sand gushing), `grandad` (dark-haired, cane, cardigan, at the attic window, slow sand) and `son` (grey-haired, gardening below, fast sand), `cellarman` (a man on a stool in a cellar, sand pouring, a parcel landing on the hatch), `office` (three or four workers at desks in a basement window row, sand pouring, grinning).
- The old ranger: reported only, never seen.

## Palette, caption, sound

- **Palette:** the montage is bright noon colour (lemon, sky blue, brick red, grass green). The tower's days are cool pearl, its nights blue-grey fog with the lamp's amber and the town's warm points. The hourglass sand is pale gold everywhere.
- **Caption key colour:** lamp amber `#ffb22e` (unchanged).
- **Music:** dorian, root 40. 72 bpm `pad` and `piano`, thin and light for the montage (0 to L12). `drone` and `pad` at low energy from L13. At L24 the heavy low `drone` enters and holds to the end, with `pulse` from L28 to L30 on the steps. `music_drops` 0.7 s at P02, 0.6 s at P03. A clean `piano` returns at L42 under the warm turn and stops before L45, so the last two lines sit on the drone alone.
- **Sound:** wind at the tower by day, static under radio beats, a soft scrape of needles on the catwalk rail at L21, the iron gate's clank at L28 (-18 dB is fine, it's the hit), wood stair steps from L29 (heavy, slow, steady), and nothing at all of the ranger's voice.

## Format

Each line gives the id and who says it, then the caption chunks split with ` / `. The spoken text is the chunks in lowercase without the quote marks. CAPS are key words in `#ffb22e`. Every line is `narrator`. Pause beats have a length and no words.

## 01 The rule (0 to about 20 s, bright day, the town)

- `L01` narrator: In this VALLEY, / TIME runs SLOWER / the HIGHER up / you ARE.
  - [S01, frame 1, noon sun: a two-shot from street level, the `balcony` woman leaning on her rail one floor up and the `walker` on the pavement below looking up at her, both faces in frame, both hourglasses big in frame. His sand gushes, hers barely trickles. Slow push in]
  - [S02, on "HIGHER up": close on the two hourglasses one above the other, the gap in speed obvious]
- `L02` narrator: Just WATCH / everyone's SAND.
  - [S03: a quick pan along the street, people at doors and windows at different heights, faster sand low, slower high]
- `L03` narrator: Grandad's in / the ATTIC, / and looks YOUNGER / than his SON.
  - [S04: the cottage, `grandad` waving his cane from the dormer, dark-haired, slow sand. S05: his grey-haired `son` in the garden below, fast sand, rolling his eyes]
- `L04` narrator: If you're WAITING / for a PARCEL, / you sit / in the CELLAR.
  - [S06: the `cellarman` on his stool in the cellar, sand pouring, drumming his knees. S07: the parcel thumps onto the pavement hatch above him]
- `L05` narrator: And on FRIDAYS, / the whole TOWN / works DOWNSTAIRS.
  - [S08: the office's basement window row from the pavement, workers at desks, sand pouring, everyone grinning]
- `L06` narrator: Then there's ME. / I'm the LOOKOUT.
  - [S09: the tower on its ridge high over the valley in clear morning light. S10: me at the foot of the stairs, hood up, `smile`, my sand already slower than the town's]
- `L07` narrator: My TOWER / is on the / HIGHEST RIDGE, / a HUNDRED / and TWELVE / STAIRS UP.
  - [S11: low on the tower's foot, tilting up the legs and switchback stairs to the cab]
- `L08` narrator: My brother OLLIE / walks me / to the GATE.
  - [S12: the gate, Ollie and me side by side, both faces at phone size, his hourglass gushing beside my slower one. He's a head shorter, beanie, quick grin. This is the loved one, clear by about 0:14]
- `L09` narrator: He calls me / SPARROW.
  - [S13: close on Ollie, `smile`, saying it]
- `L10` narrator: He says, / "Flash your LAMP / at TEN, / and I'll / flash BACK."
  - [S14: Ollie pointing down at the town. S15: over his shoulder, the town on the valley floor far below, his house among them]
- `L11` narrator: It's ONE WEEK. / I LOCK / the gate / behind me.
  - [S16: the gate swinging shut from inside, Ollie on the far side waving. S17: close on the padlock closing (a cut, not a hand turning it)]
- `L12` narrator: The RANGER / has the only / other KEY.
  - [S18: inside the cab, the plain iron key hung on its nail by the door]

## 02 The nights (about 20 to 40 s)

- `L13` narrator: At TEN, / I lift / my LAMP / to the GLASS.
  - [S19: night, the cab from outside, one amber lamp in the blue-grey fog. S20: inside, me holding the lamp up at the glass, `neutral`. My sand is a few slow grains]
- `L14` narrator: Down in / the TOWN, / one little WINDOW / lights up BACK.
  - [S21: binocular POV, the town's small cluster of lights, `ollie_win` fading up over 1.2 s. S22: my face, `smile`]
- `L15` narrator: The radio CLICKS. / The old RANGER / says, / "Goodnight, LOOKOUT."
  - [S23: close on the radio: green light on, click, static, light off]
- `L16` narrator: Ollie's window / doesn't go DARK. / It stays LIT / ALL NIGHT.
  - [S24: binocular POV, the window steady. S25: me on the cot, lamp beside me, looking out at it, `puzzled`. Plant 1]
- `L17` narrator: The NEXT night, / his LIGHT / is somewhere ELSE, / HIGHER / up the HILL.
  - [S26: night 2, binocular POV: more town lights, `ollie_win` dark and `ollie_win2` lit on the hillside. S27: me at the glass, `worried`. Plant 2]
- `L18` narrator: And the PINES / under my tower / look TALLER.
  - [S28: from the catwalk looking down, the pine tops nearer than night 1 (scale 1.12)]
- `L19` narrator: By the / THIRD NIGHT, / the TOWN'S / TWICE as BIG.
  - [S29: night 3, the high wide from the cab over the valley: the lights spread up both sides]
- `L20` narrator: Ollie's light / is on / the FAR RIDGE, / in the / RANGER'S HUT.
  - [S30: binocular POV across the valley, the hut's one window lit, steady. S31: my face behind the binoculars, `worried`]
- `L21` narrator: And the TREETOPS / SCRAPE / the CATWALK.
  - [S32: low along the catwalk rail, pine tips brushing it (scale 1.28), the scrape heard. S33: me inside, `scared`, looking down through the glass floor edge]

## 03 The fourth night (about 40 to 60 s, the scare)

- `L22` narrator: On the / FOURTH NIGHT, / the radio CLICKS.
  - [S34: night 4, the radio's green light on in the dark cab]
- `L23` narrator: A NEW ranger. / A MAN.
  - [S35: me turning to it, lamp in hand, `worried`]
- `L24` narrator: He says, / "Goodnight, SPARROW."
  - [S36: close on the radio, the light going off. The heavy drone enters here]
- `L25` narrator: NOBODY / calls me THAT / but OLLIE.
  - [S37: my face, `terrified`, lit by the lamp]
- `P01` pause 0.8 s: none
  - [S38: the far ridge through the glass, the hut's window steady in the dark. Static only]
- `L26` narrator: Then the LIGHT / in the HUT / starts MOVING.
  - [S39: binocular POV, the light leaving the hut]
- `L27` narrator: It CROSSES / the VALLEY, / and comes UP / my RIDGE.
  - [S40: the high wide over the valley, one warm point gliding down into the fog, glowing through it. S41: the same point on our ridge, below the tower, coming up through the pines]
- `L28` narrator: Down at / my GATE, / the LOCK CLANKS.
  - [S42: low on the gate in fog, the padlock hanging open, the gate swung in. The clank is the hit]
- `L29` narrator: Someone's CLIMBING / my STAIRS.
  - [S43: from the hatch looking down the switchbacks, a lamp's glow rising flight by flight]
- `L30` narrator: SLOW and HEAVY. / A HUNDRED / and ELEVEN. / A HUNDRED / and TWELVE.
  - [S44: me backed against the far glass, lamp held out, `terrified`. S45: the cab door, the glow arriving under it]
- `P02` pause 0.7 s: none
  - [music drop. S46: the door opening inward on the cut]
- `L31` narrator: A TALL MAN / fills my DOOR, / his lamp / held LOW.
  - [S47: `ollie_old` in the doorway, his own lamp at his belt line lighting him from below, face in shadow under the dusty-rose beanie, beard edge catching the light. Taller than me. His hourglass above him. Clearly lit, rim from my lamp behind me]
- `L32` narrator: Over his head, / the SAND / barely MOVES.
  - [S48: close on his hourglass: a few slow grains, the same as mine. Plant for the end]
- `L33` narrator: He LIFTS / the LAMP / to his FACE.
  - [S49: the lamp rising (a cut to the lamp already at his chest, then to his face, never a hand gripping)]
- `P03` pause 0.6 s: none
  - [music drop, the face fills the frame in the dark before the lamp light settles]

## 04 The reveal (about 60 s to the end)

- `L34` narrator: It's OLLIE.
  - [S50: `ollie_old` lit warm from below, `soft`, the same eyes and brows as S13, a beard, grey at the sides, the old beanie. Face at least 1/4 frame width]
- `L35` narrator: He's OLDER / than ME now.
  - [S51: the two-shot, him taller, me looking up, `wide`]
- `L36` narrator: I've been / up HERE / FOUR NIGHTS. / Down there, / it's been / TWENTY YEARS.
  - [S52: over my shoulder, the night valley full of lights, twice the town of night 1. S53: my face, `wide`]
- `L37` narrator: His WINDOW / never went DARK, / because / he FLASHED it / EVERY NIGHT.
  - [S54: binocular POV of night 1 again, the steady window (reuse S24's framing)]
- `L38` narrator: SEVEN THOUSAND / TIMES. / From up here, / it looked / like ONE.
  - [S55: Ollie, `soft`, a small nod]
- `L39` narrator: And every YEAR, / he moved / a little HIGHER, / to SLOW / his SAND DOWN,
  - [S56: the valley side by night, the three places his light has been, low house, hillside house, ridge hut, left to right, all dark now except the hut. Reuse the night-3 look]
- `L40` narrator: so he'd NEVER / get too far / AHEAD of me.
  - [S57: his hourglass and mine in one frame, side by side]
- `L41` narrator: He became / the RANGER / to get / the KEY.
  - [S58: close on the key ring at his belt. S59: cut to the twin key still on its nail by the door]
- `L42` narrator: He SITS / on the COT / beside me.
  - [S60: the two of us on the cot, lamp between us, his `smile`, my `soft`. Piano in]
- `L43` narrator: Our SAND / falls at / the SAME speed.
  - [S61: close on the two hourglasses side by side over our heads, the same slow trickle, grain for grain]
- `P04` pause 1.0 s: none
  - [S62: hold the two-shot. The piano stops]
- `L44` narrator: In this VALLEY, / the HIGHER / you are, / the SLOWER / it RUNS.
  - [S63: the cab from outside at night, one amber lamp, the valley's lights far below in the fog]
- `L45` narrator: In the MORNING, / we walk / DOWN together.
  - [S64: the high wide over the valley, the town's lights slowly shifting below, some going out, new ones coming on, steady fades only]
- `L46` narrator: I don't KNOW / what YEAR / it'll BE.
  - [S65: close on my face at the glass, the town's lights reflected faint in it, `soft` to `worried`. After "BE", 0.25 s, then a hard cut to S01]

About 65 shots for about 88 s, a cut every 1.35 s.

## Continuity

| Lines | Where Ollie is | His hourglass | Mine |
|---|---|---|---|
| L01 to L07 | off screen | | slower than the town's (at the gate), a few grains (in the cab) |
| L08 to L11 | at the gate with me, then outside it | gushing | trickling (the gate is on the ridge) |
| L13 to L16 | his window `ollie_win`, valley floor, steady glow | not seen | a few slow grains |
| L17 to L18 | `ollie_win2`, hillside house, steady | not seen | same |
| L19 to L25 | the ranger's hut on the far ridge, steady | not seen | same |
| L26 to L30 | a moving lamp point: valley, our ridge, the stairs | not seen | same |
| L31 to L46 | in the cab with me | a few slow grains, the same as mine | same |

## Notes for standards

- Nobody is hurt, taken or in peril. Ollie the teen appears only in daylight at the gate. The stranger never touches me, and the door opens on a cut.
- No death words. "Seven thousand", "twenty years" and "four nights" are counts, not ages. No age appears on screen or is said.
- No text or real place anywhere. The ranger's badge is our own glyph. The hourglasses have no numerals.
- No flashing: every light fades over 1 s or more, Ollie's lights are always steady, and the sand grains are small and constant.

## Narration check

46 lines, 380 words. Every line read aloud. No dashes, semicolons, "not just", "no X, no Y", parenthesis lists, three-beat slogans or banned words. "Little" appears only in "one little WINDOW" (no child word anywhere near a harm word).
