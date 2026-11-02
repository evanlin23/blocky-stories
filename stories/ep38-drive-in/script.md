# ep38-drive-in

**Slug:** `ep38-drive-in`

## Premise
In this town a little black cut-out silhouette in a thin gold ring floats over everyone's head, and it shows who they miss most. Mine has always been my own outline, cap and all, and I tell everyone it means I'm fine on my own. My husband Theo and I went to the drive-in every Friday for nine years. This year I chose to stay late at work on Fridays, and he goes alone. His silhouette has always been me, and now it's fading a shade every week. I start parking three rows behind him to watch, and something no light lands on comes one row of cars nearer each Friday.

## Rule
The world's rule is the first line (L01): "In this town, a little silhouette over your head shows who you MISS most." Everyone has one. It's never explained by anyone, only shown working (L03 to L06, L14 to L18, L23, L31, L41, L57).

## Twist
My silhouette was never me. It's Theo: his old cap, which I've worn for years, and the tuft of hair that sticks up at the back of his head. The one I've missed most all year, from my desk on late Fridays, was the man I married, three rows ahead. The last 15 seconds turn the first line over: "shows who you miss most" was pointing at Theo over my head the whole time, and the last line, "Mine wears his CAP," makes my "little cap and all" (L07) mean his.
- **Plant 1 (L07 and L12, S09 and S14):** L07 says my silhouette has a "little cap". In S14 (L12) I'm at my desk on a late Friday with the cap hung on the coat hook behind me, bareheaded, and the silhouette over my head still wears the cap. Not narrated.
- **Plant 2 (L10, S12, and the silhouette in S09):** "His hair sticks up at the back." S12 shows Theo's tuft from behind. In the S09 close-up, my silhouette has the same small tuft poking out under the back of the cap. L49 names it at the reveal.

## World
One made-up town's drive-in cinema on Friday nights in early autumn. A huge pale screen on a steel frame at the front, a gravel lot of gentle ramps in seven rows, each bay with a short post and an old metal window speaker box on a hook, a low block projection booth at the back with one square port, and a snack hut with warm windows. Beyond the lot, dark fields and a line of low trees. The screen shows only slow drifting fields of colour (no pictures, no shapes, no text, no hard cuts). One office interior for the late-Friday desk shots: a desk lamp, a coat hook, dark window. The montage uses a few quick sets: a bar table at a stag night, a harbour railing at dusk, a café table, a sofa with a phone. No words anywhere: no signs, no film titles, no menu boards, no number plates with letters (plates are blank or carry our own dot glyphs), no badges on cars.

## Cast (all adults, nobody in peril or hurt)
- **me** (adult woman, early thirties, narrator): short dark brown block hair, Theo's old faded brick-red cap with a plain peak (no logo), a mustard knit jumper over a white collar, dark trousers. Round eyes, brows. Bareheaded in the office shots (S14, S19).
- **Theo** (adult man, early thirties, my husband): block hair in sandy brown with one short **tuft sticking up at the back** (the plant), a forest-green plaid overshirt over a grey tee. Classic eyes, brows. Quiet, never explains anything.
- **Montage extras** (adults, a few seconds each): Dev and two mates at a stag night, a sailor in a navy peacoat with a dog at his side (the dog is a simple blocky dog, unharmed, only in S05), a woman and her first date at a café, a long-distance couple on a sofa and on a phone screen.
- Background: a dozen car owners and couples in the rows, all with silhouettes.

## The rule marker (on every character by 2 s)
A small flat black cut-out silhouette, head and shoulders in profile, inside a thin glowing gold oval ring (`#ffcf5a`, emissive, never clipped white), floating one hand above the head and always facing camera. Each silhouette is the outline of the person that character misses, drawn by us (no real faces). It's on every character in every shot, including the montage extras and the dog's sailor. The Unlit has none.
- **Mine:** a person in a cap with a peak, and a small tuft under the back of the cap (Theo). It never changes, even when I'm bareheaded.
- **Theo's:** a person in a cap without a tuft (me). Full black at first, then fading by beat: Friday 1 dust grey (L18), Friday 2 paler (L23), Friday 3 pale (L28), Friday 4 a faint line (L31), empty ring (L41), then fading slowly back to full black over 1.5 s (L57) and staying.
- **Montage:** Dev's is his bride with a veil, the sailor's is his dog, the first-date woman's is a man with a quiff (her ex), the long-distance couple each show the other.

## The creature: the Unlit (never named on screen)
- One model, built once in `set.py` and posed per shot. An ordinary R6 person, but **a whole head too tall** (about 2.4 m standing), so standing among the cars its head clears every car roof. It's dressed in plain work clothes, but no light lands on it: every surface is a matte black with almost no reflectance. Only a thin cool rim along its silhouette (from the screen side) and **two small eye glints** show. The glints are the brightest thing on it.
- It carries **no** silhouette and no ring. It throws **no shadow** in the projector beam (exclude it from the beam light's shadow casting, and in S29 the screen behind it is unbroken).
- Never seen moving. Only in a new place each Friday. It never touches anyone, never touches Theo, and never opens a door: between S35 and S39 it's simply in the seat.
- Seated in Theo's car (S39 to S44) its head is bent forward and down against the roof lining because it doesn't fit, its glints turned back over its shoulder through the rear window toward my car.
- Light it for fear: front lights dead, key from the screen side and below, a rim on the silhouette, the glints the brightest pixels.

**Continuity by beat**
| Beat | Lines | Where it is |
|---|---|---|
| Rule and montage | L01 to L15 | Not present. |
| Friday 1 | L19 to L22 | Standing at the very back of the lot, behind row 7, by the projection booth, facing the screen. Head clears the roofs. Rim and glints only. |
| Friday 2 | L24 to L27 | Three rows nearer, standing in the aisle in row 4, directly in the projector beam. The beam passes it, the screen shows no shadow. |
| Friday 3 | L28 to L30 | In row 1, beside the car to the left of Theo's, facing Theo's passenger door, a car width away. Its head turned 40 degrees back toward my car three rows behind. |
| Friday 4, dark | L32 to L35 | Unseen in the dark. |
| Scare | L36 to L41 | In Theo's passenger seat, head bent against the roof lining, glints turned through the rear window at me. |
| Climax | L46 to L58 | Still in the passenger seat. In the wide S58 it's a black shape in the car, and it casts nothing on the screen. |
| Theo leaves the car | L55 | Still in the seat as his door swings open (cut on the swing). |
| Ending | L60 onward | Gone. The passenger seat is empty (S68). |

## Look
- **Look config (story.json):** `look.flash_safe: true`. No flickering lights anywhere in `set.py`. Every light change is a slow fade of 1 s or more (see Flash plan).
- **Palette:** golden-hour amber `#f2a65a` for the opening, dusk violet sky `#3a2a55`, screen light cool silver-blue `#b8c8e6`, projector beam silver `#dfe6f2` with soft dust, gravel `#6a6460`, car paints in faded cream `#e8dcc0`, teal `#3b7d7a` and brick `#9a4a3a` (Theo's car is the cream one), the gold rings `#ffcf5a`, silhouettes black `#0b0b0e`, my brick-red cap `#a6402f`, mustard jumper `#c9a23a`, Theo's forest plaid `#2f5d3f`, the Unlit matte `#050506`.
- **Caption key colour:** marquee coral `#ff6f61` (ep11 lime, ep12 red, ep13 cyan and ep20 brass gold are taken, and the gold of the rings stays on the markers only).
- **Music:** C Aeolian, 6/8 at 66 bpm. A warm, slightly worn electric-organ pad with a soft brushed pulse, like a drive-in interval, our own synthesized melody. From L19 a low detuned drone creeps in under it. Drops (0.6 s) before L19 ("Something stood"), before L36 ("It was in Theo's passenger SEAT") and before L47 ("My shadow went up the screen"). From L56 it turns to C Ionian, the organ brighter, the drone gone, a slow 6/8 sway to the end.
- **Sound:** the speaker-box hiss (filtered noise) under every drive-in shot, gravel crunch on steps, a soft projector whirr from the booth, distant crickets, a low car-door clunk on S64. L34: the hiss cuts to silence with a 0.3 s fade, then nothing. All synthesized.
- **Grade:** the hook (S01 to S07) bright golden hour, faces lit to read. Fridays 1 to 4 go darker each week toward blue night. Ending warm screen light inside Theo's car.

## Flash plan (hard rule 7)
Every light change is a slow fade, never flicker or strobe.
- **Projector beam on** (S20): fades up over 1.5 s.
- **Screen light:** the screen's colour drifts slowly, every brightness change taking at least 2 s. No cuts on the screen picture.
- **Reel runs out** (S36 to S37, L32 to L33): the screen and beam fade down together over 1.5 s to near black. The car interiors keep a faint dash glow so nothing is pure black.
- **Beam fades back up** (S39, L35): over 1.5 s, slow and silver.
- **Theo's ring fading back to full** (S63, L57): a 1.5 s fade.
- **Rings and glints:** steady emissive, no pulsing.
- No headlights switching on, no camera flashes, no phone screens lighting suddenly (the montage phone in S07 is already lit when we cut to it).
- Run `python -m blocky flash` pre-check on S36 to S40 and S54 to S63 at the final's frame steps.

## Shot plan
73 shots over about 2:20, a new shot every 1.9 s on average.

| Shot | Line | Picture |
|---|---|---|
| S01 | L01 | Golden hour at the drive-in. Medium two-shot of a laughing couple leaning on a cream car, faces lit warm, both silhouettes in gold rings clear over their heads. Readable at phone size by frame 1. |
| S02 | L01 | Wide of the lot at golden hour: rows of cars, people by their doors, a gold ring over every head, the big pale screen. |
| S03 | L02 | Close on one marker: a black head-and-shoulders cut-out inside a thin gold oval, floating over a head. |
| S04 | L03 | Stag night: Dev at a bar table between two mates, his silhouette a bride with a veil. |
| S05 | L03 | His two mates groaning, heads thrown back, their own silhouettes over them. |
| S06 | L04 | Harbour rail at dusk: a sailor in a navy peacoat, kit bag, his blocky dog at his side, a dog's outline in his ring. |
| S07 | L05 | Café table: a woman on a first date, her silhouette a man with a quiff. Her date's eyes flick up to it. |
| S08 | L06 | A sofa, a woman holding up her phone (no grip, phone propped on a cushion), on the screen a man holding up his, each silhouette showing the other. |
| S09 | L07 | Me by my teal car at the drive-in, wearing the brick-red cap. Push in on my marker: a person in a cap, a small tuft under the back of the cap. Plant 2. |
| S10 | L08 | Me, close, shrugging, a brave smile. |
| S11 | L09 | Theo in the driver's seat of the cream car, his silhouette of me in a cap, full black. |
| S12 | L10 | Theo from behind, the tuft sticking up at the back of his head. Plant 2. |
| S13 | L11 | Inside the cream car, a past Friday: me in the passenger seat, Theo in the driving seat, a popcorn tub on the bench seat between us, warm screen light. |
| S14 | L12 | Office, late, dark window: me at my desk under a lamp, bareheaded, the cap on the coat hook behind me, and my silhouette over my head still wearing a cap. Plant 1. |
| S15 | L13 | The drive-in at night: Theo's cream car in the front row, one person inside. |
| S16 | L14 | Close on Theo's ring: his silhouette of me one shade lighter. |
| S17 | L15 | Same framing, a week later (cut, not a fade): lighter again. Theo's face below, tired. |
| S18 | L16 | My teal car rolling into a bay three rows back (cut in as it stops, no hands on wheel). |
| S19 | L16 | Me inside, bareheaded, the cap on the seat beside me, watching the cream car ahead. My silhouette still wears the cap. |
| S20 | L17 | From behind the lot: the projector beam fades up over the cars toward the screen. |
| S21 | L17 | The screen filling with a slow drift of silver-blue and amber colour. |
| S22 | L18 | Over Theo's shoulder from behind: his silhouette of me, dust grey. |
| S23 | L19 | Music drop before. Rear wide: at the very back, by the booth, a tall black shape standing, head above the roofs. |
| S24 | L20 | Closer: only a thin cool rim and two small glints. |
| S25 | L21 | Me, eyes wide, in my car. |
| S26 | L22 | Tight on the space over its head: nothing, no ring. |
| S27 | L23 | Friday 2. Theo's ring, the silhouette paler still. |
| S28 | L24 | From my car: the Unlit in row 4, three rows nearer, standing in the aisle. |
| S29 | L25 | Side wide: the beam passing through the aisle where it stands. |
| S30 | L26 | The screen, unbroken colour. No shadow anywhere on it. |
| S31 | L27 | Low angle on the Unlit in the beam, the dust lit around it, its body still matte black. |
| S32 | L28 | Friday 3. Wide on row 1: the Unlit beside the car next to Theo's. |
| S33 | L29 | Closer: it faces Theo's passenger door, a car width away. Theo's silhouette pale. |
| S34 | L30 | Its head turned back 40 degrees, the two glints aimed down the rows at my car. |
| S35 | L31 | Friday 4. Theo's ring with only a faint grey line inside. |
| S36 | L32 | The screen, its colour fading slowly down over 1.5 s. |
| S37 | L33 | Wide of the lot as the beam and screen fade to near black, dash glows only. |
| S38 | L34 | Close on the speaker box hooked on my window, hiss, then silence. |
| S39 | L35 | From behind the lot: the beam fades back up, slow and silver. |
| S40 | L36 | Music drop before. Through Theo's rear window from my car: the black shape in his passenger seat. |
| S41 | L37 | Close on it in the seat beside Theo, the empty popcorn spot between them. |
| S42 | L38 | Inside the car from the dash: its head bent forward against the roof lining. |
| S43 | L39 | The reveal (test still first): from my car, push in through Theo's rear window, its two glints turned back over its shoulder at me, rim lit from the screen side. |
| S44 | L40 | Theo in profile, eyes on the screen, the Unlit beside him. |
| S45 | L41 | Theo's gold ring, empty. Hold. |
| S46 | L42 | Me in my car, frozen. |
| S47 | L43 | Close on my own small marker, a tiny thing over my head. |
| S48 | L44 | Wide from behind Theo's car looking back: three rows of cars, my car tiny, my marker a gold dot. |
| S49 | L45 | Reverse wide from the back: every car facing the one huge screen. |
| S50 | L46 | My car door swinging open (cut on the swing). |
| S51 | L46 | Me walking up the aisle into the beam, gravel crunch, lit silver from behind. |
| S52 | L47 | Music drop before. The screen: my shadow rising up it, as tall as a house. |
| S53 | L48 | Tilt up the shadow to the huge ring over its head on the screen. |
| S54 | L48 | Full screen: the giant silhouette in its giant ring. |
| S55 | L49 | Close on the screen silhouette: the cap, and the tuft sticking out the back. |
| S56 | L50 | Me in the beam, looking up at it, the cap on my head. |
| S57 | L51 | Insert: the cap on my head from behind, with no tuft under it. |
| S58 | L52 | Wide from behind me: my shadow on the screen, and in Theo's car the black shape, casting nothing. |
| S59 | L53 | Theo's car, three rows ahead, Theo looking up at the screen. |
| S60 | L54 | Faces in other cars all lit by the screen, looking up. |
| S61 | L55 | Theo's driver door swinging open (cut on the swing, no grip). |
| S62 | L56 | Theo walking into the beam beside me, his tuft lit silver. |
| S63 | L57 | His ring: the faint line fades slowly back to full black over 1.5 s. Music turns to C Ionian. |
| S64 | L58 | The screen: two giant shadows side by side, over each one a giant ring with the other's outline. |
| S65 | L59 | On the screen the two shadows turn to face each other. |
| S66 | L59 | Below, the two of us in the beam, facing each other. |
| S67 | L60 | Theo's cream car, passenger door open: the seat empty. |
| S68 | L61 | Inside the car, me in the passenger seat, Theo at the wheel side, nothing between us. |
| S69 | L62 | The popcorn tub sliding along the bench seat toward me (cut in already moving, no hands on it), Theo's eyes on the screen. |
| S70 | L62 | **Lore plant:** close on the old speaker box hooked on Theo's window, and pressed into its metal face, two short soot-black tally strokes. Held 1.6 s. Not narrated. |
| S71 | L63 | Office, a Friday at five: my coat gone from the hook, the desk lamp off. |
| S72 | L64 | Inside the cream car, front seats from the dash: two of us, two rings, the silhouettes over our heads turned to each other. |
| S73 | L65 | Close on my ring: the cap and the tuft. Cut on "CAP" back to S01. |

## The last 15 seconds turn the first line
"In this town, a little silhouette over your head shows who you miss most" opens as a fun fact, and my silhouette reads as me, a woman fine on her own. The reveal (L47 to L53) puts it on the screen at the size of a house: Theo's tuft under Theo's cap. The last line, "Mine wears his CAP," loops back into the first, so on a rewatch the opening line is about Theo, and every shot of my marker (S09, S14, S19, S47) shows the man I'd been missing from my desk. Rewatch plants: the cap on my silhouette while I'm bareheaded at work (S14, S19), and Theo's tuft (L10, S12) matching the tuft on my silhouette (S09).

## What the hits do (the checklist)
1. **Rule opener:** L01, "In this town, a little silhouette over your head shows who you miss most." 14 words.
2. **Marker by 2 s:** gold rings with black silhouettes over both faces in S01, from frame 1, golden-hour lit.
3. **Montage (3 to 5, under 15 s):** Dev's bride at his stag night, the sailor's dog, the first date's ex, long-distance couples comparing (L03 to L06, ends about 14 s).
4. **Narrator as the exception:** mine is "just me", cap and all (L07).
5. **Loved one at stake:** my husband Theo, an adult, whose silhouette of me fades as he lets go, while the Unlit moves into my seat.
6. **Climax turns the rule's own logic:** the marker is a cut-out, and a cut-out throws a shadow. A silhouette is too small to read across a car park (L43, L44), but at a drive-in everyone looks at the screen (L45), and the projector throws mine the size of a house. No new magic.
7. **Twist planted twice, last line echoes the first:** see above.
8. **Readable first 2 s:** bright golden hour, two faces and two markers, no fog until Friday 1.
9. **Cut often:** 73 shots over about 2:20, about 1.9 s average.
- **15 to 30 s:** the rule works on Theo (his silhouette of me getting lighter, L14 to L15, S16 and S17) with nobody explaining it.

## Rig notes
- Cars are blocky and made up, with a wide old-style bench front seat sized for two seated riders (about 2.9 m cabin) since seated riders are about 1.36 m wide. No badges, no letters.
- No hands on wheels, doors, popcorn or phones. Doors are cut on the swing, the tub is cut in already sliding, the phone is propped.
- The Unlit seated: check the head against the roof lining for intersections in the stills. It bends, never clips through.

## Lore connection (one)
S70, under L62 ("Theo slid the popcorn over"): two short soot-black tally strokes pressed into the metal face of the old speaker box hooked on Theo's window, two for a car built for two front seats. Held 1.6 s, never narrated. Plain tally, no extra stroke (`stories/lore.md` → Third parallel batch).

## Narration (65 lines, 633 words, about 2:11 of speech at 290 wpm, about 2:20 with gaps)
Every line is `who: narrator`. CAPS are the caption key words.

L01. In this town, a little silhouette over your head shows who you MISS most.
L02. A black cut-out, in a thin GOLD ring.
L03. At his stag night, Dev's silhouette was his BRIDE, and his mates all GROANED.
L04. A sailor came home with his DOG floating over him.
L05. A woman on a first date had her EX, and her date NOTICED.
L06. Couples far apart compare theirs on video CALLS.
L07. Mine is the only one in town that's just ME. Little cap and ALL.
L08. I tell everyone it means I'm fine on my OWN.
L09. My husband Theo's silhouette has been ME for nine years.
L10. His hair sticks up at the back. It has since the day I MET him.
L11. Every Friday we went to the drive-in, one popcorn between the SEATS.
L12. This year, I chose to stay late at work on FRIDAYS.
L13. So Theo kept going ALONE.
L14. And over his head, I started getting LIGHTER.
L15. A shade fainter every WEEK, like he was letting me GO.
L16. One Friday, I drove there after work and parked three rows BEHIND him.
L17. The beam came on over the cars, and the screen filled with slow COLOUR.
L18. His silhouette of me was as grey as DUST.
L19. Something stood at the very back, a head taller than the ROOFS.
L20. Only its EDGES showed, a thin rim and two GLINTS.
L21. No light landed on it at ALL.
L22. And over its head, there was NOTHING.
L23. Next Friday, his silhouette of me was paler STILL.
L24. And the tall thing was three rows NEARER.
L25. It stood right in the path of the projector BEAM.
L26. The light crossed it, and nothing showed on the SCREEN.
L27. Not even a SHADOW.
L28. The Friday after, it was beside the car NEXT to Theo's.
L29. Facing his passenger door. The door I used to OPEN.
L30. And its glints had turned, toward MY car.
L31. Fourth Friday. His silhouette of me was a faint line in the RING.
L32. Halfway through, the reel ran OUT.
L33. The screen faded slowly to BLACK.
L34. My speaker box hissed on the window. Then the hiss STOPPED.
L35. The beam came back up, slow and SILVER.
L36. It was in Theo's passenger SEAT.
L37. My SEAT.
L38. Its head was bent against the roof. It didn't FIT.
L39. Its glints were turned round, through his back window, at ME.
L40. Theo just kept watching the SCREEN.
L41. Over his head, the gold ring was EMPTY.
L42. I couldn't walk up to his window. I didn't know what I'd SAY.
L43. And a silhouette is only the size of a HAND.
L44. From three rows back, he'd never even seen MINE.
L45. But at a drive-in, everybody looks at the same ONE thing.
L46. I got out and walked into the BEAM.
L47. My shadow went up the screen as tall as a HOUSE.
L48. And over its head, in a ring as wide as a barn DOOR, my silhouette.
L49. It had a cap on. And a tuft of hair sticking up out the BACK.
L50. It was THEO.
L51. I'd worn his old cap so long, I forgot whose it WAS.
L52. Every late Friday at my desk, I'd been missing the man I MARRIED.
L53. The one I missed most was parked three rows AHEAD.
L54. Nobody honked. The whole drive-in just LOOKED.
L55. Then Theo's car door swung OPEN.
L56. He walked into the beam and stood right BESIDE me.
L57. Over his giant shadow, his ring filled in, darker than in YEARS.
L58. Two shadows as big as houses, and over each of them, the other ONE.
L59. Up on the screen, we turned to face each OTHER.
L60. Back at his car, the passenger seat was EMPTY.
L61. I got in, and it was just the two of US.
L62. Theo slid the popcorn over without looking, like he USED to.
L63. I've left work at five every Friday SINCE.
L64. In this town, your SILHOUETTE shows who you MISS.
L65. Mine wears his CAP.

Pause beats (silent, about 0.6 s each): after L18, L22, L27, L35, L41, L50, L59. Leave 0.25 s between L65's last word and the loop cut.
