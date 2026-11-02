# ep44-sleeper-car

**Slug:** `ep44-sleeper-car` (pitch #28, batch 4)

## Premise
In this world a little moon floats over everyone's head and fills while they sleep: full after a good night, a thin crescent after a bad one. Mine is always full, though I haven't slept a whole night in years. My twin brother Ash (adult) sleeps ten hours a night, and his moon is a sliver that keeps shrinking. We share a two-berth cabin on a four-night sleeper train to Dad's retirement party. Every night I give up on sleep and walk the corridor, and every night a person of clear glass stands one step nearer our door.

## Rule
The world's rule: your moon fills while you sleep (L01). Nobody explains it. It's shown at work: job interviews, a smug office napper, couples, a carriage of crescents (L04 to L07), Ash dozing on his feet with a sliver (S11), the café attendant pouring him a double at one look (L26). The narrator breaks the house habit of the world (sleep at night) every night by walking the corridor (L16, L30, L37, L43).

## Twist
Our moons are crossed. Mine fills while Ash sleeps, and his only fills while I do. I was never the lucky one who didn't need sleep. Every full moon I had was made of his sleep. The first line, "the moon over your head fills up while you sleep", reads on a rewatch with a second "you": the sleep isn't always yours. The last line makes it explicit: "His fills while I DO."
- **Plant 1 (L27 to L29, S30 to S33):** I nap ten minutes in the café car and wake to Ash stretching, saying he feels great, his moon visibly a little fuller. S33 holds on his moon so a rewatch sees it grow.
- **Plant 2 (L34 to L35, S38 to S39):** Ash dreams he walks a long corridor all night and never gets to rest. That's my night, the one I just walked.
- Bonus plant (S09 and S11): every time Ash is asleep on screen, my moon in the same frame is bright and full. The first time I'm shown awake at night (S09), Ash is asleep in the background.

## World
A long-distance sleeper train crossing open country at night, plus one bright morning platform for the hook. No real routes, stations, rail company names or words anywhere: no signs, no timetables, no lettering on cups or doors. Cabin doors carry small brass dot-plates (one to eight dots, our own glyph), never numbers in a real font.
- **The cabin:** a narrow two-berth sleeper, walnut panels, a bottom bunk and a top bunk with a brass ladder on the corridor side, cream blankets, a small folding table under the window, a dim amber reading lamp. A sliding door with a frosted panel onto the corridor.
- **The corridor:** long, narrow, walnut and cream, a strip of patterned carpet (geometric, no text), dim amber night lamps on the cabin side at a constant low level, a row of big dark windows on the other side, a connecting door with a small round window at the far end.
- **Outside the windows:** open fields and low hills under a pale moon, a dark blue-grey, very low contrast. It drifts by slowly. **Nothing passes:** no lamps, signals, stations, poles, tunnels or bridges. The window light never changes except by slow fades.
- **The café car:** short counter in brass and walnut, four booths with burgundy seats (spaced for 1.36 m seated riders), a blank menu board with our own dot glyphs, white cups with no print.
- **The hook platform:** a bright morning platform under a glass canopy, pale stone, iron columns, blank boards, soft sunlight. Plus montage inserts: an interview room, an open-plan office, a kitchen table, a commuter carriage.

## Cast (all adults, nobody hurt)
- **me** (adult twin, late twenties, narrator): slate-blue hoodie, grey joggers, dark brown block hair swept to one side, round eyes, calm brows. My moon is always full.
- **Ash** (adult twin brother): same hair shape and colour as me (twins), mustard knit jumper, brown cords. A tired face: heavy lids, grey under-eye strokes (opt-in `faces.py` "tired" if it doesn't exist yet), skin a touch greyer than mine until L61. From L61 his skin matches mine, eyes bright, a grin.
- **The attendant** (adult): burgundy waistcoat, white shirt, neat black block hair, small moustache. L25 to L26 only.
- **Montage extras** (adults): the interviewer (tweed jacket, glasses) and the candidate (green blazer), the office napper (striped shirt, loosened tie) and two co-workers, a couple at a kitchen table (one in a red dressing gown, one in a plaid shirt), four commuters in coats. Each has their own moon.
- **Dad** is only mentioned, never shown.

## The marker: the moon (on every person, by 2 s)
- A small flat disc, 0.16 m across, floating 0.22 m above the top of the head, always facing camera (billboard). The lit part is soft cream (#f3ecd2, emission low enough never to clip, below the eye highlights in brightness). The unlit part is a faint translucent slate (#3b4560 at 35%) so the full disc shape always reads.
- Phases: full, gibbous, half, crescent, sliver, thread, line. Phase changes are slow (at least 1 s) and only happen where the script says.
- **Me:** full in every shot, always.
- **Ash:** sliver at S11 to S14, thinner each morning (S26 eyelash, S40 thread, S47 barely there, S56 one faint line), a little fuller at S33 (plant 1), full from S68.
- **The Glass One has no moon** (L22). Keepers never carry the world's marker.

## The creature: the Glass One (never named on screen)
- One model, built once in `set.py`, posed per shot. A full R6 person made of **clear glass blocks**: torso, arms, legs and round head all glass, with thick **bottle-green edges** (#1f6b4a) where the blocks meet, like the edge of a bottle. Nothing inside. Through it you see the corridor, slightly bent.
- **Wrong in one way:** its face is on the **back** of its head. Two small bright eye glints and a short dark mouth line, set into the glass at the back of the head. So when its body faces away, its face looks at you.
- No moon above it. No clothes, no hair.
- Only its green edges and the eye glints catch light. Front lights dead, a soft amber key from the night lamp at the side, a cool moon rim from the windows. The eye glints are the brightest thing in its shots.
- Never seen moving. Only nearer each time we see it.
- **Test still first:** the S20 reveal at phone size, glass and edges reading against the dim corridor. If the glass reads as empty, thicken the green edges and add a faint inner fresnel, never a glow.

**Continuity by beat**
| Beat | Lines | Where it is |
|---|---|---|
| Night 1 | L17 to L22 | Far end of the corridor, standing in front of the connecting door, body facing the door, face (back of head) toward the camera and me. |
| Night 2 | L31 to L33 | Three cabin doors nearer, standing against the cabin side, same pose: body facing the far end, face toward me. Seen first in the dark window's reflection behind my own, then faint in the corridor when I turn. |
| Night 3 | L37 to L39 | Right outside our cabin door, body facing the windows, so its face (back of head) is turned to our door. |
| Night 4 | L43 to L46 | Not in the corridor. |
| Night 4, cabin | L47 to L51 | Lying in my top bunk under my blanket, on its side facing the wall. Its head at the ladder end, its backwards face hanging just over the bunk's edge, looking down at Ash in the bottom bunk. |
| After | L58 to L66 | Gone. The top bunk is empty when I get there. |

## Look
- **Palette:** night navy #141c33, window blue-grey #2c3a52, walnut #5b3a24, cream #efe6cf, brass #c8963c, night-lamp amber #e3a35c (always dim), burgundy seats #6e2a2e, glass edges bottle-green #1f6b4a, moon cream #f3ecd2. Platform and dawn: pale stone #d8d2c4, soft peach sky #f2c9a2.
- **Caption key colour:** pale moon lilac `#c7b8ff`.
- **Plan settings for `story.json`:** `"look": {"flash_safe": true, "fog": "#141c33", "fog_density": 0.03, "fog_start": 4.0, "sky": "#141c33", "exposure": 0.0}` for the train nights. The platform (S01 to S12) and the dawn (S68 to S75) are lit bright and warm. No `flicker` anywhere in `set.py`.
- **Music:** E dorian (root 52), 66 bpm, a slow rocking 6/8 feel. A soft pad and a low drone with our own synthesized melody, gentle and a bit sleepy in the montage, colder from L17. Drops (`music_drops`) for 0.6 s before L17 ("someone was STANDING"), before L31 ("there it WAS") and before L47 ("Something was lying in my BUNK"). From L60 the drone goes and the pad turns major and warm. No music box.
- **Sound:** a low steady train rumble (`hum` plus `wind`, about -32 LUFS) all through the train, with a soft, slow wheel rhythm (sound only, no light goes with it). A door slide for L46. Café clink for L25 to L26. Cut the rumble to near nothing for 0.7 s before L47.

## Flash plan (hard rule 7, `look.flash_safe: true`)
- **No light ever moves past a window.** No passing lamps, signals, platforms, poles, tunnels or bridges. The landscape outside is dark, low contrast and slow.
- The corridor night lamps are constant. The only light change in the night is L44 to L45: all corridor lamps fade down together over 1.5 s, hold 1 s near dark (the windows' soft moonlight stays on), and fade back up over 1.5 s. That's two changes in about 4 s.
- The cabin reading lamp stays off at night. The cabin is lit only by soft window moonlight and the corridor amber through the door's frosted panel.
- Dawn (S68) is a slow 2 s warm-up of the window light, no cut to white.
- The moons and the glass eye glints never clip. Moon phase changes take at least 1 s.
- Cuts between a bright shot and a dark shot (S12 to S13, S67 to S68) are fine as cuts but never alternate bright/dark quickly: no more than one bright/dark swap in any 2 s.
- Run `python -m blocky flash` on S01 to S14, S43 to S50 and S68 at the final's frame steps.

## The hits checklist (RULES.md → What the hits do)
1. **Rule opener (L01, 13 words):** "In this world, the MOON over your head fills up while you SLEEP."
2. **Marker by 2 s:** S01 opens on a bright platform, three travellers' faces in frame, each with a moon over the head (one full, one crescent, one half). Lit to read.
3. **Montage, first 15 s (L02 to L07, four examples):** the job interview glance (L04), the smug office napper (L05), couples who know who lay awake (L06), a carriage of crescents (L07).
4. **The exception (L08 to L10):** my moon is always full, though I haven't slept a whole night in years.
5. **Loved one at stake (L11 to L12, L24, L36, L41 to L42, L51):** Ash, my adult twin, whose moon thins toward dark.
6. **The loophole (L55 to L56):** the rule says your moon fills while you sleep, and never says whose. Ours are crossed, so I fill his by sleeping. No new magic.
7. **Twist planted twice, last line echoes the first:** plants at L27 to L29 and L34 to L35. L65 to L66 repeats the opener and adds "His fills while I DO."
8. **Readable first 2 s:** S01 bright and clear, faces at least 1/5 of the frame, moons above.
9. **Cut often:** 75 shots over about 141 s, average about 1.88 s.
- **Seconds 15 to 30 (about L08 to L16):** the rule at work, nobody explaining it. My full moon glowing at 3 a.m. while I stare at a ceiling (S09), Ash asleep on his feet against a platform column with a sliver (S11), Ash's sliver against my full moon in one frame (S12), the sleeper train, the cabin, Ash out cold before the train moves, me up and walking. Each shot adds a picture. No character speaks about the rule.

## Shot plan
| Shot | Line | Picture |
|---|---|---|
| S01 | L01 | Bright morning platform under the glass canopy. Three travellers in a row, faces in frame, sleepy, each with a moon: full, crescent, half. Slow push in. |
| S02 | L02 | Close: a yawning traveller with a fat full moon, smiling. |
| S03 | L03 | Close: a bleary traveller, a thin crescent over her head. |
| S04 | L04 | Interview room: the interviewer's eyes tilt up to the candidate's moon (a crescent). The candidate swallows. |
| S05 | L05 | Open office: the napper asleep upright in a meeting, his moon huge and full, smug grin. Two co-workers with crescents stare. |
| S06 | L06 | Kitchen table: the couple, one full, one crescent. The full one sips. The crescent one gives a long look. |
| S07 | L07 | Commuter carriage, low angle down the row: four faces, four thin crescents. |
| S08 | L08 | Back on the platform: me, close, a big bright full moon. |
| S09 | L09 | Night, my old flat: me awake in bed staring at the ceiling, full moon glowing above me. Ash asleep on the sofa through the doorway (bonus plant). |
| S10 | L10 | Me on the platform, a small shrug and half smile. |
| S11 | L11 | Ash asleep standing up, leaning on an iron column, mouth open, bag at his feet. |
| S12 | L12 | Two-shot: Ash's sliver beside my full moon. Push in on his. |
| S13 | L13 | Evening: the sleeper train at the platform, long walnut and navy carriages, warm windows, no lettering. |
| S14 | L14 | Inside the cabin from the door: bottom bunk, top bunk, the brass ladder. |
| S15 | L15 | Ash already asleep on the bottom bunk, shoes still on, sliver above him. |
| S16 | L16 | Me lying on the top bunk, eyes open, full moon glowing. |
| S17 | L16 | The corridor, long and dim, amber lamps, dark windows. Me stepping in. |
| S18 | L17 | My point of view down the corridor. At the far end by the connecting door, a faint shape. Music drop before. |
| S19 | L18 | Medium-far: the Glass One, edges and corridor seen through it. |
| S20 | L19 | **Reveal (test still).** Closer: green edges, two eye glints in the back of its head. |
| S21 | L20 | Its body faces the far door. The glints face me. |
| S22 | L21 | Close on the back of its head: the face set into the glass. |
| S23 | L22 | Tilt up above its head: empty air. No moon. |
| S24 | L22 | Me, close, my own full moon above me. Eyes wide. |
| S25 | L23 | Top bunk, me awake, the window going from blue to grey (2 s slow fade). |
| S26 | L24 | Morning, cabin: Ash sitting up, a moon as thin as an eyelash. |
| S27 | L25 | Café car: Ash at the counter, eyes closing mid-sentence, standing. |
| S28 | L25 | Close: Ash's head nodding, mouth half open. |
| S29 | L26 | The attendant glances up at Ash's moon. Cut to a white cup set down, steam (cut in already set). |
| S30 | L27 | Afternoon booth, soft daylight, fields drifting outside. Me nodding off, head against the window frame. |
| S31 | L28 | Me waking. Beside me in the booth, Ash stretching, arms up. |
| S32 | L29 | Ash, bright for once, grinning. |
| S33 | L29 | Hold on Ash's moon: a touch fuller than at S26 (plant 1). |
| S34 | L30 | Night two. Me at a big dark window in the corridor, fields under the moon. |
| S35 | L31 | Over my shoulder into the window: my reflection, and behind it, three doors down, a green-edged shape. Music drop before. |
| S36 | L32 | Closer on the reflection: its glints, its body facing away. |
| S37 | L33 | Me turning. The corridor: only faint green edges against the cabin wall, three doors down. |
| S38 | L34 | Breakfast booth, Ash and me. Ash talking, hands round nothing (cups on the table, no grip). |
| S39 | L35 | Ash, faraway look. Slow push in on his face. Plant 2. |
| S40 | L36 | His moon, a thread. |
| S41 | L37 | Night three. I slide our door, step out, stop dead. |
| S42 | L38 | Wide: the Glass One right outside our door. |
| S43 | L39 | Side angle: its body faces the windows. |
| S44 | L39 | Close: the face on the back of its head, glints turned toward our frosted door. |
| S45 | L40 | Café car at night, me alone in a booth, the window turning slowly grey (2 s fade). |
| S46 | L41 | Night four, cabin: Ash asleep. |
| S47 | L41 | Close on his moon: barely visible. |
| S48 | L42 | Me watching from the door, frightened. |
| S49 | L43 | The corridor at 3 a.m., me walking back toward camera. |
| S50 | L44 | Wide: the lamps fade slowly down together (1.5 s). Windows stay softly moonlit. Music thins. |
| S51 | L45 | Same wide, lamps fade slowly back up (1.5 s). |
| S52 | L46 | Empty corridor, from my eyeline. |
| S53 | L46 | Our door from inside the cabin as it slides open (cut on the slide), me in the gap. |
| S54 | L47 | The top bunk from the doorway: a shape under my blanket. Rumble and music drop before. |
| S55 | L48 | Closer: the blanket's cream pattern seen through a glass shoulder, green edges. |
| S56 | L49 | Over the bunk: it lies on its side facing the wall, like a sleeper. |
| S57 | L50 | Low angle from Ash's pillow, up: the backwards face hanging just over the bunk's edge, glints looking down. The scare. |
| S58 | L51 | Ash asleep below it. His moon: one faint line. |
| S59 | L52 | Me in the doorway, thinking. Brief cut to S30 (me asleep in the booth), cooler grade. |
| S60 | L53 | Brief cut to S33 (Ash's moon fuller). |
| S61 | L54 | Brief cut to S39 (Ash's faraway look), then me in the corridor from S17. |
| S62 | L55 | Me, close, looking up at my own full moon. |
| S63 | L55 | Two-shot from the door: Ash's line, my full moon. |
| S64 | L56 | Slow push from my moon to his. |
| S65 | L57 | Close on me, eyes wet, a small breath. |
| S66 | L58 | **Lore plant:** close on the brass ladder, two short bottle-green strokes etched into the side rail beside the third rung. No hand on it. Held about 1.8 s, never narrated. |
| S67 | L59 | Me lying in the top bunk. The bunk is mine alone. The blanket, plain cream. |
| S68 | L60 | Me, eyes closing. The window's moonlight soft on my face. Pad turns warm. |
| S69 | L61 | Dawn: the window light warms slowly over 2 s. Wide of the cabin: two bunks, two full moons. |
| S70 | L62 | Ash at the bunk edge, shaking my shoulder (cut in on it, his hand at the end of his sleeve on my shoulder, no grip). Bright face. |
| S71 | L62 | Close on Ash: pink cheeks, a full moon, a grin. |
| S72 | L63 | Me, face in the pillow, eyes shut, smiling. |
| S73 | L64 | Morning platform: Ash walking off ahead, my bag on his shoulder and his own on the other, laughing back at me. |
| S74 | L65 | Me stepping down after him, a full moon over each of us. Push in. |
| S75 | L66 | Two-shot of the twins on the bright platform, two full moons. Cut on "DO." back to S01. |

## The last 15 seconds turn the first line
"In this world, the MOON over your head fills up while you SLEEP" opens as a cute world rule, with the narrator as the lucky exception. The climax (L55 to L57) shows the "you" was never fixed: my moon filled on Ash's sleep, and his only fills on mine. The ending lands on the line again with "His fills while I DO." and loops straight into L01, so a rewatch hears "while you sleep" as "while someone else sleeps for you". Rewatch plants: Ash fuller after my café nap (L27 to L29, S33) and Ash's corridor dream (L34 to L35, S39). Bonus: Ash asleep and my moon full in the same frames (S09, S11, S12).

## Lore connection (one)
S66, under L58 ("So I climbed the ladder"): two short upright strokes etched into the brass bunk ladder in the Glass One's bottle-green, beside the third rung. Two strokes for a cabin built for two. In the canon (`stories/lore.md`), it's a Keeper's tally: while my bunk lay empty night after night, the Glass One came to stand in the gap, and it's gone once I fill my place. Plain tally, no extra stroke. Shown once, held about 1.8 s, never narrated.

## Narration (66 lines, 637 words, about 2:12 of speech at 290 wpm, about 2:21 with gaps)
Every line is `who: narrator`. CAPS are the caption key words. Ash's one quoted word (L62) is inside the narration.

L01. In this world, the MOON over your head fills up while you SLEEP.
L02. Sleep well, and it's FULL by morning.
L03. Lie awake, and you get a skinny little CRESCENT.
L04. Every job interview starts with a long look at your MOON.
L05. The guy who naps in every meeting has the fullest moon at WORK.
L06. Couples always know who lay AWAKE.
L07. And the early train is just a row of thin CRESCENTS.
L08. Mine is always FULL.
L09. And I haven't slept a whole night in YEARS.
L10. I thought I was the LUCKY one.
L11. My twin brother Ash sleeps like a STONE.
L12. And his moon is a SLIVER.
L13. Dad's retirement party was four nights away by sleeper TRAIN.
L14. One tiny cabin. Ash on the bottom bunk, me up a brass LADDER.
L15. Ash was out before the train even MOVED.
L16. At midnight I gave up and walked the CORRIDOR, like always.
L17. At the far end, by the connecting door, someone was STANDING.
L18. A person made of clear GLASS.
L19. Just green EDGES, and two little glints for EYES.
L20. Its back was to me. But the glints were looking AT me.
L21. Its face was on the back of its HEAD.
L22. And over that head, there was no MOON.
L23. I lay awake till DAWN.
L24. In the morning, Ash's moon was as thin as an EYELASH.
L25. He fell asleep standing at the café counter, halfway through his ORDER.
L26. The attendant saw his moon and poured him a double COFFEE.
L27. That afternoon, the rocking got me. I nodded off in the café CAR.
L28. Ten minutes. I woke to Ash stretching beside ME.
L29. He said he felt GREAT. And his moon looked a tiny bit FULLER.
L30. Night two, I stopped at a dark WINDOW.
L31. In the glass, behind my own reflection, there it WAS.
L32. Three cabins nearer than the night BEFORE.
L33. I turned around. Just faint green edges, if you knew where to LOOK.
L34. At breakfast, Ash told me about his DREAM.
L35. He walked a long corridor all night, and never got to REST.
L36. His moon was a THREAD now.
L37. Night three, I didn't even get past our own DOOR.
L38. It was standing right OUTSIDE it.
L39. Facing the window. But the face on the back of its head was turned to our DOOR.
L40. I sat in the café car till the sky went GREY.
L41. Night four, I could barely SEE Ash's moon.
L42. Nobody I knew had ever seen a moon go DARK.
L43. At three in the morning, I came back down the CORRIDOR.
L44. The lights faded slowly DOWN.
L45. And slowly came back UP.
L46. Nothing in the corridor. I slid our door OPEN.
L47. Something was lying in my BUNK.
L48. A glass person under my blanket. I could see the blanket THROUGH it.
L49. It lay facing the wall, like it was ASLEEP.
L50. But its backwards face hung over the edge, looking down at ASH.
L51. And Ash's moon was one faint LINE.
L52. Then I thought about my nap in the café CAR.
L53. Ten minutes of my sleep, and his moon got FULLER.
L54. And his dream, walking a corridor all night. That was MY night.
L55. The rule says your moon fills while you SLEEP. It never says WHOSE.
L56. Ours were CROSSED. Mine filled while he slept. His could only fill while I DID.
L57. Every full moon I ever had was made of Ash's SLEEP.
L58. So I climbed the ladder, to the bunk where it LAY.
L59. There was nobody there. Just a cold BLANKET.
L60. And for the first time in years, I let the train rock me to SLEEP.
L61. At dawn, there were two full moons in our CABIN.
L62. Then Ash was shaking my shoulder. Pink cheeks, wide awake. "Our STATION."
L63. I didn't want to get UP.
L64. He laughed, and carried my bag off for ME.
L65. In this world, the MOON over your head fills while you SLEEP.
L66. His fills while I DO.

## Notes for the builder
- Leave 0.2 to 0.3 s after "DO." before the loop cut (`tail` about 0.25, ends on picture).
- The window reflection (S35, S36) can be a glossy dark window material, or a mirrored second camera composited into the window. Either way, keep it dim and soft.
- Nobody leans out of a window. No hand grips the ladder, a cup or a bag: cut in after.
- Ash's moon phases must match the continuity list. It's the twist's evidence.
