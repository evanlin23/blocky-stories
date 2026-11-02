# ep45-bee-yard

**Slug:** `ep45-bee-yard`

## Premise
In this world everyone has a small round dial over their head that counts down to their next hug. Mine has always been blank, and I tell myself it suits me, because I don't do hugs. My girlfriend Lena keeps bees in a yard on the hill above the harbour. In two years I've never gone into the yard: every evening I walk her to the gate and wave. Her dial has always read months. This week it starts counting hours toward noon on Saturday, the harvest, and a man in honey gold and smoke grey, whose feet never touch the grass and who has no dial at all, stands two hives nearer each day.

## Rule
Everyone's dial counts down to their next hug, and at zero the hug comes (L01). The dial says when, never who (L49). I keep the yard's unspoken rule of my own, never past the gate (L13, L15), and break it on Saturday (L52).

## Twist
Lena's dial was never counting down to someone else. It was counting down to me: every time I nearly hugged her goodbye at the gate it dropped to seconds, and every time I only waved it jumped back up. My own dial was blank because it was waiting for me to decide. The first line first reads as fate, a clock that happens to you. After L60 to L65 it reads as a countdown to somebody choosing, and the last line ("Mine has NUMBERS now", L70) means I finally chose.
- **Plant 1 (L16 to L17, S19 to S21):** on Monday, as I nearly hug her goodbye at the gate and turn it into a wave, her dial drops to a few seconds, then jumps back to months, and I blame the bees. S20 shows me half-lifting my arms before I turn it into a wave.
- **Plant 2 (L35 to L36, S41 to S43):** my veil, never worn, was hung on its hook the week we met. She's been ready for the second person in the yard for two years.
- Bonus plant (L18, S22): I offer to carry the honey down on Saturday, and the next shot of her dial is the first one counting hours. A rewatch sees the countdown start the day I said I'd come.

## World
One small harbour town on a hill, early summer, clear light.
- **The pier (opener and montage only):** a sunny wooden ferry pier with a white rail, a little blocky ferry moored at the end, a ticket hut with a shutter, benches, and a café table on the quay. Bright, high sun, blue water, a few gulls as dots far off. No lettering anywhere: the ticket hut, ferry and café carry only stripes and shapes.
- **The bee yard:** a steep grassy hillside above the town, clover and buttercups, a dry-stone wall round the yard with one wooden gate. Inside: twelve white wooden hives in three rows of four up the slope (row 1 nearest the gate, row 3 "the last row" highest), a small weathered shed just inside the gate, on its side wall a wooden board with two hooks and two veils. A smoker on an upturned crate. The harbour and sea are far below in wides. Bees are a soft hum and a few small dark dots drifting near the hives, never a swarm, never on a face. No brand names or text on hives or kit.

## Cast (all adults, nobody in peril or hurt, nobody is stung)
- **me** (adult man, late twenties, narrator): navy-and-cream striped tee, dark grey jeans, short black block hair. Round eyes, straight brows. Arms usually folded or hands in pockets until L52. My dial is blank: cream face, no arc, no digits.
- **Lena** (adult, late twenties, girlfriend): white beekeeping smock over a sage-green shirt, tan trousers, dark brown curly block hair tied up, a wide-brimmed veil hat with a fine dark mesh hung behind when not in use. Warm, easy smile. Her dial is the one we follow.
- **Montage extras (adults, one shot each, never named):** the hugging couple on the pier. Arrivals, a crowd of six to eight. The ticket man in a grey cardigan and flat cap, scowling on his stool in the hut. A first-date pair at the café table. Two strangers on the pier steps, a backpacker and a woman with a shopping bag.
- Lena asks nothing and explains nothing. She laughs, works and waves back. Nobody explains the rule on screen.

## The marker: the dials (visible by 2 s, on every character but the creature)
- A small round dial, about the size of the head's width, floating a hand above every head, always facing camera a little. Thin brass rim, cream face.
- Two readings on each dial, both our own design: a coloured arc ring round the edge that empties as the time runs down (coral at long times, honey gold under one hour), and a centre readout in our own blocky segment digits built in `blocky/` (not a font). The unit is shown by a row of small pips under the digits: one pip seconds, two minutes, three hours, four days, five months, six years. Never letters.
- At zero the face fades up to a soft warm gold glow over 0.8 s (never a flash) and holds while the hug lasts, then fades back over 1 s and starts a new count.
- My dial: cream face, empty rim, nothing on it at all until L57, when the arc and digits fade in over 1 s.
- The creature has no dial.

## The creature: the Hover (never named on screen)
- One model, built once in `set.py`, posed per shot. An ordinary-sized adult R6 man in a honey-gold work smock buttoned to the neck and smoke-grey trousers and boots, short smoke-grey block hair. Skin a warm wax tone (#d8b27a), never grey or pale.
- Wrong in one dimension: **height off the ground.** His boot soles are always a hand's width (12 cm) above the grass, the same in every shot, and his shadow lies on the grass apart from him, with a bright strip of sunlit grass between boots and shadow. Seen low and side-on, the gap is the scare.
- Face (our own, in `faces.py`): two small round black eyes set a touch too close, each with one pin highlight (the brightest thing on him), no brows, a mouth that is a short flat line slightly parted onto black. Expression never changes. Head tilted down a few degrees as if looking at something just below him.
- Arms straight at his sides, hands open. Never seen moving, only nearer. No dial over his head, ever.
- A few bee dots circle his head in a slow ring in every shot he's in (the same three to five dots, slow orbit).
- Light: front fill dead on him. Key low and side (the sun bounced off the grass or the hive whites), a cool rim on his silhouette. In the smoke, lit from below and behind so he reads as a shape first.

**Continuity by beat**
| Beat | Lines | Where he is |
|---|---|---|
| Wednesday | L23 to L28 | Last row (row 3), between hives 11 and 12, facing downhill toward the gate. Gone in S31 (L28) when Lena turns. |
| Thursday | L30 to L31 | Row 3 to row 2, two hives nearer: beside hive 7, facing the gate. |
| Friday | L33 to L37 | Beside the shed just inside the gate, side-on to us, his shoulder by my empty veil hook board, facing the gate. |
| Saturday, smoke | L44 to L47 | In the gateway itself, facing out, a pace from me, face a hand above mine and tilted down. |
| After | L52 | I pass him on his left (no contact, a clear gap). |
| Gone | L59 | Gateway empty, smoke thinning. Not seen again. |

## Look
- **Palette:** hive white #f1ede2, honey gold #e3a53a, smoke grey #8c8f94, clover green #5e8a3c, buttercup #f2cf4a, sky #9cc8ea, sea #3f7fa8, dry-stone #9a8f7e, Lena's sage #8aa37f, my navy #273550, dial cream #f3ead6 with brass #b8913e, dial arc coral #ff7f6a.
- **Caption key colour:** clover pink `#ff86b8` (lime, red, cyan and brass gold are taken by ep11 to ep20).
- **Music:** A Mixolydian, 92 bpm in 4/4. A light plucked synth over a soft bowed drone that sits near a bee's hum (synthesized in `sound.py`, our own melody, no music box). From L19 a slow ticking pulse joins at the tempo (a filtered click, synthesized). Drops of 0.6 s before L23 ("Then I saw someone"), before L44 ("And he was RIGHT there") and 0.5 s before L54 (the count). From L56 the drone resolves and the pluck plays the tune in full, brighter.
- **Sound:** a soft steady bee hum near the hives (low, never loud), gulls far off on the pier, wooden gate latch click, the smoker's puffs as soft noise breaths, a tiny tick from dials in close-ups, a warm chime swell for each zero (rising, -18 dB). No samples.
- **Light changes (flash-safe, `look.flash_safe: true`):** there are almost none. The zero glows are 0.8 s fades up and 1 s down, never more than one in a 2 s window near the camera. The smoke fills the yard over 3 s (L40 to L41), a slow fade from sunlit to soft grey, and thins over 3 s (L59). My dial lighting (L57) is a 1 s fade. No flicker, no strobe, no blackouts, no lamp switches. Pre-check S01 to S03 (several zero glows in frame) and S48 to S64 with `python -m blocky flash`.

## The hits checklist (RULES.md → What the hits do)
- **Rule line:** L01, "In this world, a CLOCK over your head counts down to your next HUG." (13 words)
- **Marker by 2 s:** S01 opens on the pier couple hugging under two gold zero dials, faces over each other's shoulders toward camera, with two passers-by behind whose dials read coral arcs and digits. Sunlit, high key, both faces at least 1/5 frame width, dials clear of the caption band.
- **Montage (L02 to L08, about 3 to 16 s), four examples:** the arrivals end of the pier is a field of gold zeros. The ticket man's dial reads years and he's happy about it. On a first date both dials read four hours and both blush. Two strangers hit zero together and look anywhere but at each other.
- **Narrator as the exception:** my dial is blank, not even a zero (L10), and I don't do hugs (L11).
- **Loved one at stake:** Lena, girlfriend, adult. Her dial counts down toward a hug with someone I can't see coming, while the Hover closes in on the yard.
- **15 to 30 s:** L12 to L22 show the rule at work on Lena (the Monday dip, the switch to hours, the hours falling as she works). Nobody explains it.
- **Loophole climax:** the dial says when, never who (L49 to L52). The hug will happen at zero whatever I do, so I make sure it's me.
- **Readable first 2 s:** high sun on the pier, faces and dials in frame, no fog or dark until L40.
- **Cuts:** 81 shots over about 140 s, an average of about 1.7 s.

## The last 15 seconds turn the first line
L60 to L70. The opening line sounds like fate: a clock that runs down to a hug that happens to you. The reveal (L60 to L65) is that Lena's clock was counting to me every time I nearly hugged her, and mine was blank because I hadn't decided. The last lines put the rule back in my own mouth ("the CLOCK over my head counts down to my next HUG. Mine has NUMBERS now."), and the loop drops back into L01, which on a second watch is about choosing. Rewatch plants: the Monday dip at the gate (L16 to L17, S19 to S21) and the veil hung the week we met (L35 to L36, S41 to S43).

## Lore connection (one)
On the board that holds the two veil hooks, two short honey-gold strokes are scratched into the wood between the hooks: a plain tally, two for a yard built for two (lore.md → Third parallel batch). Shown once in S42, under L35 ("One is Lena's. The other is mine."), held about 1.8 s, never narrated. No extra stroke, nothing else of the canon.

## Shot plan
Timings are at about 290 wpm. Every shot keeps faces at least 1/5 of the frame width where a face is the subject, and dials clear of the caption band.

| Shot | Line | Picture |
|---|---|---|
| S01 | L01 | Sunny ferry pier, medium: a couple hugging, faces toward camera over each other's shoulders, both dials glowing soft gold at zero. Two passers-by behind with coral arcs and digits. The hook frame (readable at 2 s). |
| S02 | L01 | Close on a passer-by's dial ticking down, arc coral, three pips. |
| S03 | L02 | Wider: the couple at the pier end, the little ferry moored behind, sea sparkling (soft, no glints clipped). |
| S04 | L03 | High wide: the arrivals end, six to eight people meeting, a field of gold zero dials. |
| S05 | L04 | The ticket man on his stool in the hut, scowling, his dial on six pips and a full coral arc. |
| S06 | L04 | Close: he glances up at it and gives a small satisfied nod. |
| S07 | L05 | Café table on the quay: the first-date pair, both eyes flicking up. |
| S08 | L06 | Insert, both dials side by side: the digit 4, three pips. |
| S09 | L06 | Two-shot: both blushing faces, looking at the table. |
| S10 | L07 | The pier steps: two strangers side by side, both dials fading to gold together. |
| S11 | L08 | Same pair, heads turned hard away from each other, eyes wide. |
| S12 | L09 | Me on the quay, medium, hands in pockets, a bright day behind. |
| S13 | L10 | Close up on my dial: brass rim, cream face, nothing on it. |
| S14 | L11 | Me walking past a hugging pair, arms folded, a little shrug. |
| S15 | L12 | Wide of the hillside above the harbour: the dry-stone wall, the gate, three rows of white hives. Lena walking up the path in her smock. |
| S16 | L13 | Me outside the gate, the latch between us and the yard. |
| S17 | L14 | Lena close, her dial on five pips (months), a full arc. |
| S18 | L15 | Golden evening: Lena just inside the gate, me outside, waving. |
| S19 | L16 | Monday: me at the gate, my arms half lifting toward her, then turning it into a wave. Plant 1. |
| S20 | L16 | Insert: her dial dropped to a few seconds, one pip, the arc nearly empty. Plant 1. |
| S21 | L17 | Her dial back to five pips. Me shrugging at a bee dot drifting by. Plant 1. |
| S22 | L18 | Me and Lena at the gate, a crate of empty jars stacked inside by the shed. I point at the gatepost. Bonus plant. |
| S23 | L19 | Wednesday, insert: her dial now on three pips, 72. |
| S24 | L20 | Me at the gate, looking round the empty hill, uneasy. |
| S25 | L21 | Lena bent over an open hive in row 1 (frame already lifted, no grip shown), bee dots around. |
| S26 | L22 | Insert: her dial, 70. |
| S27 | L22 | Insert: her dial, 66, the light lower. Music drop after. |
| S28 | L23 | From the gate, up the slope: someone standing in the last row. |
| S29 | L24 | Long lens: the Hover between hives 11 and 12, facing downhill, perfectly still. |
| S30 | L25 | Low side-on at grass height: his boots, a hand of bright grass under them, his shadow lying apart. Test still. |
| S31 | L26 | Closer on the gap, a buttercup under his sole, untouched. |
| S32 | L27 | Tilt up: his head, empty air above it, three bee dots circling. |
| S33 | L28 | Me calling out, mouth open, at the gate. |
| S34 | L28 | Lena turning to look. The last row behind her is empty. |
| S35 | L29 | Thursday, insert: her dial, 48. |
| S36 | L30 | From the gate: the Hover beside hive 7 in row 2, facing us. |
| S37 | L31 | Close: bee dots circling his head in a slow ring, his face unmoved. |
| S38 | L32 | Friday, insert: her dial, 24, the arc smaller. |
| S39 | L33 | From the gate: the Hover side-on by the shed, beside the veils, his soles above the grass. |
| S40 | L34 | The board on the shed wall: two wooden hooks, two veils. |
| S41 | L35 | Lena's veil: white mesh, a sage band, worn soft. Plant 2. |
| S42 | L35 | My veil: pale, mesh still creased flat. Between the two hooks, two short honey-gold strokes scratched in the wood. Held 1.8 s. Lore plant, not narrated. Plant 2. |
| S43 | L36 | Lena beside the board, smiling at me through the gate, my veil beside her. Plant 2. |
| S44 | L37 | Dusk: the Hover by my veil, low sun, his long shadow apart from his boots. |
| S45 | L38 | Night: me sitting on the quay wall, dial blank, looking up at the dark hill. |
| S46 | L38 | Moonlit close on the Hover's face by the shed, cool rim, pin highlights. |
| S47 | L39 | Saturday, bright: me at the gate with the crate of empty jars. |
| S48 | L40 | Lena puffing the smoker by row 1. Soft grey smoke rolls over the yard (a 3 s fade). |
| S49 | L41 | Her dial glowing through the smoke: two pips, 1. |
| S50 | L42 | My view: grey, the hive shapes dissolving into it. |
| S51 | L43 | Me waving smoke from my face. Music drop after. |
| S52 | L44 | The reveal (test still first): the Hover in the gateway, a pace from me, lit from below and behind, rim on his shape. |
| S53 | L45 | Low angle up past my shoulder: his face a hand above mine, tilted down at me. |
| S54 | L45 | Insert: his boots above the gate's threshold stone, smoke curling through the gap. |
| S55 | L46 | Bee dots going round his head in a slow ring. |
| S56 | L47 | Past his shoulder: Lena's dial through the smoke, 20, one pip. |
| S57 | L48 | Me, close, eyes on her dial. |
| S58 | L49 | Insert: my blank dial. |
| S59 | L49 | Insert: her dial, just digits and pips, nothing else. |
| S60 | L50 | Lena in the smoke by the hives, calm, working. |
| S61 | L51 | Me, jaw set. |
| S64 | L52 | Wide: I step past him on his left, a clear metre between us, into the yard. |
| S62 | L52 | The board: my hook, now empty (cut from veil to empty hook), as I run on. |
| S63 | L53 | Me running with my veil on, brim crooked. |
| S65 | L54 | Insert: her dial, 3, 2, 1. Music drop before. |
| S66 | L55 | The hug in the smoke: my arms round her, the two veil brims bumping. |
| S67 | L56 | Her dial at zero, a slow warm gold fade (0.8 s). |
| S68 | L57 | My dial: an arc fading in for the first time (1 s). |
| S69 | L58 | Close on my digits and pips. |
| S70 | L59 | The gateway, smoke thinning (3 s), empty, a strip of trodden grass. |
| S71 | L60 | Me looking back at the gate, still holding her. |
| S72 | L61 | Monday again (same grade, a 0.5 s dissolve in): me at the gate, her dial on one pip. |
| S73 | L62 | Same evening: my wave, and her dial back to five pips. |
| S74 | L63 | Lena's face through her veil, smiling at me. |
| S75 | L64 | Me realising, close. |
| S76 | L65 | My dial counting, small numbers. |
| S77 | L66 | Lena laughing, the inside of her mesh misted. |
| S78 | L67 | Next morning: the board, both hooks empty. |
| S79 | L68 | At the gate, I hug her first. Her surprised laugh. |
| S80 | L69 | Pull out wide: two dials over two heads in the yard, small numbers, the harbour below. |
| S81 | L70 | Close on both dials. Cut back to S01. Leave 0.25 s after the last word. |

## Narration (70 lines, 629 words, about 2:10 of speech at 290 wpm, about 2:20 with gaps)
Every line is `who: narrator`. CAPS are the caption key words.

L01. In this world, a CLOCK over your head counts down to your next HUG.
L02. That couple on the ferry pier just hit ZERO.
L03. So the arrivals end is a field of ZEROS.
L04. The ticket man's dial says YEARS. He likes it that WAY.
L05. On a first date, you both sneak a look UP.
L06. These two both read four HOURS. Both went RED.
L07. Worst is two strangers hitting zero TOGETHER.
L08. They look everywhere except at each OTHER.
L09. And then there's ME.
L10. My dial is BLANK. Not even a ZERO.
L11. That suits me fine. I don't do HUGS.
L12. My girlfriend Lena keeps bees on the HILL.
L13. In two years, I've never set foot in the YARD.
L14. Her dial has always said MONTHS.
L15. Every evening I walk her to the gate, and I WAVE.
L16. On Monday, as I waved, her dial dropped to a few SECONDS.
L17. Then it jumped straight back to MONTHS. I blamed the BEES.
L18. I said I'd help carry honey down on SATURDAY. From the gate, obviously.
L19. On Wednesday, her dial started counting HOURS.
L20. Seventy-two. And I had no idea who was COMING.
L21. She worked the hives all afternoon. I watched from the GATE.
L22. Seventy. SIXTY-six.
L23. Then I saw someone in the last row of HIVES.
L24. A man in honey gold and smoke GREY, perfectly STILL.
L25. Between his boots and the grass was a gap, a hand WIDE.
L26. His feet weren't touching the GROUND.
L27. And over his head there was no dial at ALL.
L28. I called to Lena. When she turned round, the row was EMPTY.
L29. Thursday, she was on FORTY-eight.
L30. And he was back. Two hives NEARER.
L31. The bees circled him slowly, the way they circle a HIVE.
L32. Friday, she was down to TWENTY-four.
L33. He was at the shed inside the gate, beside the VEILS.
L34. Two veils hang there on wooden HOOKS.
L35. One is Lena's. The other is mine. I've never WORN it.
L36. She hung it up the week we MET.
L37. He stood by my veil all evening, a hand above the GRASS.
L38. Somebody was going to hug Lena at noon on Saturday. I thought it would be HIM.
L39. Saturday was the harvest. I waited at the gate with empty JARS.
L40. Lena lit the smoker, and the yard went soft and GREY.
L41. Her dial said ONE minute.
L42. I couldn't see her. I couldn't see the HIVES.
L43. I waved the smoke away from my FACE.
L44. And he was RIGHT there.
L45. Floating in the gateway, his face a hand above mine, looking DOWN.
L46. Bees went round his head in a slow RING.
L47. Behind him, her dial said TWENTY seconds.
L48. And I thought about the RULE.
L49. The dial tells you WHEN. It never tells you WHO.
L50. Somebody was going to hug Lena in twenty seconds, whatever I DID.
L51. So I decided it was going to be ME.
L52. I stepped past him, grabbed my veil off its HOOK and RAN.
L53. I pulled it on as I ran, for the first time EVER.
L54. Her dial said three. Two. ONE.
L55. I hugged her so hard our veils BUMPED.
L56. Her dial hit zero and glowed slow GOLD.
L57. And over MY head, something lit up.
L58. Numbers. For the first time in my LIFE.
L59. When the smoke cleared, the gateway was EMPTY.
L60. Then I understood Monday at the GATE.
L61. Every time I nearly hugged her goodbye, it had dropped to SECONDS.
L62. And every time I only waved, it jumped back to MONTHS.
L63. All this time, it had been counting down to ME.
L64. To every time I nearly did IT.
L65. And mine was blank because it was waiting for me to DECIDE.
L66. Lena laughed so much her veil steamed UP.
L67. Now both veils come off their hooks every MORNING.
L68. At the gate now, I hug FIRST.
L69. In this world, the CLOCK over my head counts down to my next HUG.
L70. Mine has NUMBERS now.
