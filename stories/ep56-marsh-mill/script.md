# ep56-marsh-mill

**Slug:** `ep56-marsh-mill` (replaces batch 4's killed ep39 `glass-house`)

## Premise
In this town everyone is born with a brass key on a cord round the neck. It opens exactly one door in town, and never your own, and it only goes warm and gold at the locked door it fits. I've tried every door in town and mine has never opened anything. My great-aunt Win, eighty-one, runs the windmill on the marsh. I was her mate on the millstones for six years, then left two years ago to open my own bakery, and now I only pick her flour up off the step. Her mill door has been open day and night for thirty years. This Monday it's locked, and each night a clean, flour-free patch in the shape of two boots stands nearer behind her on the stone floor, in my old place by the sack hoist.

## Rule
Your key opens one door in town, never your own (L01), and it only goes warm at a locked door it fits (L02, L44). Nobody can open their own locked door. I break my own habit, never going in (L13), on Saturday (L48 to L51).

## Twist
The one door my key fits is Win's. I never found it because it was the only door in town that had never been locked. Win has known since I was born that the shape on my key matches her lock. She kept the door open for thirty years so I'd never feel I had to come, and this week she locked it, and then locked herself out of her own mill when she went for sail cloth, so that only my key could let her back in. The first line first reads as a rule of exclusion, "never your own". After L58 to L61 it reads as the rule that someone else's door is where you're let in, and L64 says it: "It's the one somebody leaves OPEN for you."
- **Plant 1 (L08, S11):** "I've tried every door in town." Wide of me trying my key in a shop door at dusk. Far behind, out on the marsh, the windmill's door stands wide open with warm light spilling out. Never pointed at.
- **Plant 2 (L12 to L13, S17 and S18):** picking up the flour, a wider shot of the open mill door's edge, its iron lock plate and the step. The plate's keyhole escutcheon has the same four-spoke glyph as the head of my key, which S12 showed in close-up at L08. Never narrated.
- Bonus (L14, L46): "Thirty years, open day and NIGHT." and "Before that, it was never locked." The lines that hide the answer.

## World
One small made-up marsh town, late autumn. No real places, no words on any sign.
- **The street (opener and montage):** a sunny terraced street, painted front doors in five colours, brick, low walls, a café front with striped awning and blank windows, a bakery front (mine, a plain loaf glyph on the board, no lettering). High morning sun for S01 to S10, then dusk for S11.
- **The marsh:** flat reed beds and dykes under a big sky, a raised track of packed earth to the mill, fog later.
- **The windmill (a place of work):** a tarred black brick tower mill, a white weatherboarded cap, four white sails (stopped in every shot, never turning in front of a light, so no sweeping shadows), a gallery rail high up. One oak door with a small square window at face height, an iron lock plate, and a stone step. Inside, the stone floor: two millstones in a wooden casing with a hopper above, a flour chute and bins, the sack hoist (a chain and hook hanging from a trapdoor in the beams, plus an oak post beside it), heavy oak beams overhead, a ladder up, whitewashed walls, a small stove, two wooden stools by the stones (Win's and my old one). Flour dust hangs in the window light as soft haze and lies white on every surface, which is what makes the clean patch read.
- **The bus stop (L54 only, implied):** not shown. Win walks in from the track.

## Cast (all adults, nobody hurt or in peril)
- **me** (adult man, about thirty, narrator, the town's new baker): a flour-dusted cream baker's jacket over a rust-and-navy check shirt, dark trousers, short brown block hair, straight brows. My key: plain brass, the head a four-spoke wheel glyph, never glowing until L48.
- **Great-aunt Win** (adult, eighty-one): white block hair in a bun under a flour-white headscarf, a navy miller's smock, a red neckerchief, round glasses drawn on the face, a lively sideways smile. Her key hangs on her cord like everyone's (its head a crescent glyph). She is never unwell and never in peril. She says nothing on screen except the reported "Took you long enough" (L57).
- **Montage extras (adults, one beat each, never named except Mr Ames):** the postman (grey jacket, satchel, cap) in the café. Mr Ames (fifties, cardigan) on his own doorstep, and his ex-wife (fifties, green coat) letting him in. A bride and groom at his front door, both in pale wedding clothes, no veil text or confetti words. The S01 neighbour (yellow cardigan) and her friend.
- Nobody explains the rule on screen.

## The marker: the keys (visible by 2 s, on every character but the creature)
- A brass key a hand long on a dark cord, hanging mid-chest over the clothes, always turned a little to camera. It's built in `set.py` (our own mesh), big enough to read at phone size.
- Each key head is a different glyph of our own design. Never letters. Every glyph belongs to one character only, and nobody else wears it:
  - me: four-spoke wheel. Win: crescent.
  - Mr Ames: a step. His ex-wife: a leaf.
  - postman: three dots. Bride: a ring. Groom: a triangle.
  - S01 neighbour: a diamond. Her friend: a cross. Street extras (S03, S04): a bell, a fish, a wave, one each.
- Escutcheons are only seen on Win's door (the wheel). No other door shows a glyph.
- A key glows only once it's in the keyhole of the locked door it fits: it fades up to a soft warm gold over 1 s (never a flash), with a faint gold light on the wearer's chin and the door. Never on a chest, a path or a hand away from a lock. It fades back over 1 s when the door opens.
- My key: brass, never glowing, until L48 (1.2 s fade up).
- The creature has no key and no cord.

## The creature: the Lifter (never named on screen)
- One model, built once in `set.py`, posed per shot. Test still first: S47 at phone size.
- A person, unmistakably: an R6 body a head and a half taller than an adult, in a plum smock buttoned to the neck (#5a2d4f) and oatmeal trousers (#d9c9a6), dark boots, short plum-black block hair. Skin a warm wax tone (#c9a27a), never grey or pale.
- Wrong in one way: **four arms.** One ordinary pair hangs straight at its sides. A second, full-size pair comes out of the top of the shoulders just behind the first and is held straight up, hands open at the end of the sleeves, palms up, as if holding a sack against the beams. In one silhouette it reads as a person (head, shoulders, legs) with arms up and arms down at once. The raised pair keeps a clear gap of sky or wall between arms and head, so it never merges into a block. The raised hands stop a hand short of the beams, never through them.
- Face (our own, in `faces.py`): two round black eyes set level and a little too far apart, one pin highlight each (the brightest thing on it), no brows, a mouth that is a short flat line. Expression never changes. Head tilted back, looking up at its own raised hands, except at L40 to L42, when it bends at the waist and the head comes down to the glass.
- Never seen moving, only nearer. It never touches anyone, carries no key, says nothing, and never chases.
- Light: front fill dead. Key from below and the side (the stove glow, later the moonlight from the window), a cool rim on the silhouette so the four arms read against the dark beams. No clipped white.

**Continuity by beat**
| Beat | Lines | Where it is (or its trace) |
|---|---|---|
| Tuesday | L19 | Not seen. My old stool turned to face Win. |
| Wednesday | L20 to L22 | Not seen. A clean boot-shaped patch in the flour beside the hoist post, two metres from Win. |
| Thursday | L23 to L24 | Not seen. The clean patch right behind Win's stool, a hand's width from her shoulder. |
| Friday | L28 | Not seen. My stool turned to face the door. |
| Friday night | L30 to L32 | Only its shadow on the whitewashed wall, thrown by my torch through the window: four arms, two up. |
| Saturday, moon | L36 to L39 | In full, standing in the clean patch by the hoist, raised hands under the beams, behind the door window. |
| Saturday, glass | L40 to L42 | Bent down at the waist, its face just behind the glass, level with mine, raised arms still up. |
| Gone | L52 | The clean patch empty, flour drifting down into it. Not seen again. |

## Look
- **Palette:** tar black #23201f, sail white #efeae0, flour white #f4f0e6 (never clipped), oak #7a5a3c, brick #8a4a36, marsh reed #a89a5c, dyke water #4f6a6e, sky #a9c8e0, fog #b9bfc0, key brass #c8a24a, key glow #ffcc66, Win's navy #2b3a5c, her neckerchief #c0392b, my cream #eadfc8, creature plum #5a2d4f and oatmeal #d9c9a6.
- **Caption key colour:** marsh violet `#b48cff` (not used by any other story).
- **Music:** C harmonic minor, 76 bpm in 6/8. A thin plucked synth and a soft wooden tick for the first third. A slow low drone (a synthesized bowed bass with a little grain, like stones turning) enters at L25 (the mill dark) and holds to the end. Drops of 0.6 s before L26 ("Win was GONE"), 0.7 s before L36 ("And it was RIGHT there") and 0.5 s before L48 (the key). From L53 the pluck plays the tune in full over the drone, brighter, then thins on L65 so the sting lands cold. All synthesized in `sound.py`, our own melody, no music box.
- **Sound:** the millstones as a low rumbling grind (synth noise through a slow filter), the sack-hoist chain's soft clink, a wooden latch, a knock, reed wind on the marsh, a key's warm rising tone at L48 (-18 dB), the door creak at L53. No samples.
- **Light changes (flash-safe, `look.flash_safe: true`):** every change is a slow fade. The key glows fade up and down over 1 s (only one in frame at a time in the montage). Dusk to night happens between scenes, never on screen. The mill going dark (L25) is shown already dark. My torch is switched on off screen and only ever seen already lit, its beam steady. The moon coming up through the window (L35) is a 2 s fade. My key at L48 fades up over 1.2 s. The stove glow is steady. No flicker, no strobe, no blackouts, no turning sails in front of any light. Pre-check S01 to S10, S44 to S60 with `python -m blocky flash`.

## The hits checklist (RULES.md → What the hits do)
- **Rule line:** L01, "In this town, your KEY opens exactly one door, and it's never your OWN." (14 words)
- **Marker by 2 s:** S01, sunny street, two neighbours on a doorstep face to camera, both keys on their chests, one fading up gold at the door. High key, both faces at least 1/5 of the frame width, keys clear of the caption band.
- **Montage (L02 to L07, about 3 to 16 s), four examples:** the postman first into the café, Mr Ames locked out and let in by his ex-wife in silence, and a bride's key opening her husband's door first try, with the keys glowing gold at their doors in each.
- **Narrator as the exception:** my key has never opened anything (L08).
- **Loved one at stake (on screen by L09 to L10, about 0:18):** Great-aunt Win, my only family, adult, eighty-one (never said or shown on screen). A clean patch closes in behind her each night, then she's gone with the mill dark (L25 to L28).
- **15 to 30 s:** L08 to L14 put the rule on me and on Win's door (my key cold at door after door, the mill door the only open one). The escalation starts at L15. Nobody explains the rule.
- **Loophole climax:** a key only wakes at a locked door, and Win's is the one door I never tried: all week it was locked and I only knocked, and before that it was never locked (L44 to L47). The same rule, read again, no new magic.
- **First scare:** L25 to L28, about 55 to 61 s: Win gone, the mill dark, her scarf in the door. She's away for an ordinary reason (L54 to L55) and back by the end.
- **Creature clearly:** L36 to L42, about 75 to 89 s (54 to 64%).
- **Readable first 2 s:** sunny street, faces and keys in frame. No fog or dark until L25.
- **Cuts:** 82 shots over about 140 s, an average of about 1.7 s.

## The last 15 seconds turn the first line
L58 to L65. The opening line sounds like a rule about being shut out: never your own door. The reveal is that the one door my key opens was Win's, kept open thirty years so I'd never feel I had to come, then locked so I'd know I always could. L63 repeats the rule in my mouth, L64 gives its new reading, and L65 lands cold: when I'm late, the patch by the hoist stays clean, so something would stand there again. Rewatch plants: the open mill door far behind me at L08 (S11) and the matching glyph on the lock plate (S17 to S18).

## Lore connection (one)
Two plum strokes scratched into the oak post beside the sack hoist, at shoulder height: a plain tally, two for a mill worked by two (miller and mate), in the Lifter's colour (lore.md → Third parallel batch). Shown once in S29, under L21 ("Two boot shapes, where someone had been STANDING."), upper third, held about 1.8 s, never narrated. No extra stroke, nothing else of the canon.

## Shot plan
Timings are at about 290 wpm. Faces are at least 1/5 of the frame width where a face is the subject, and keys sit clear of the caption band.

| Shot | Line | Picture |
|---|---|---|
| S01 | L01 | Sunny terraced street, medium two-shot on a red front door: a neighbour in a yellow cardigan lifts her key to her friend's lock, both faces to camera, both keys on their chests, hers fading up gold (1 s) once it's in the keyhole. The hook frame. |
| S02 | L01 | Close on the glowing key at the keyhole, the door swinging in. |
| S03 | L02 | Medium wide of the street: five painted doors, a few people with keys on cords, one key glowing gold in a keyhole. |
| S04 | L02 | Insert: three street extras' key heads side by side on three chests: bell, fish, wave. All cold. |
| S05 | L03 | Dawn, the café door: the postman's three-dot key glowing in the keyhole, chairs still up inside. |
| S06 | L03 | Inside: the postman alone at a table with a cup, satchel on the floor, smug. |
| S07 | L04 | Mr Ames on his own step, patting his pockets, his step-glyph key cold on his chest. |
| S08 | L05 | His ex-wife in a green coat coming up the path, her leaf key cold on her chest. |
| S09 | L06 | Two-shot: she puts her key in his lock and it fades up gold in the keyhole, both staring straight ahead, not a word. |
| S10 | L07 | The bride at the groom's door, her ring key glowing in the keyhole first try, the groom grinning in the doorway. |
| S11 | L08 | Dusk, wide: me trying my key in a shop door, cold. Far behind, out on the marsh, the windmill with its door wide open and warm light spilling. Plant 1. |
| S12 | L08 | Close: my key in my hand, the four-spoke wheel glyph on its head, dull brass. Plant 2's other half. |
| S13 | L09 | Wide of the marsh in afternoon sun: the black tower mill, white cap, four still sails, the earth track. |
| S14 | L09 | Win at the mill door in her smock and headscarf, flour on her sleeves, her crescent key on its cord, smiling sideways, face at least 1/4 of the frame. |
| S15 | L10 | This morning, two-shot: me on the step, Win in the open doorway a pace behind, both faces to camera, her hand lifting in a wave. Present day, no memory grade. |
| S16 | L11 | Through the open door, present day: two wooden stools side by side at the millstones, Win's worn, mine with untouched flour on its seat. The history shown, not told. |
| S17 | L12 | The mill step: three flour sacks by the open door, my hands out of frame lifting one (cut before any grip). |
| S18 | L13 | Wider shot, not full frame: the open door's edge, the iron lock plate and the stone step in one frame, the plate about a quarter of the frame width. Its keyhole escutcheon is a four-spoke wheel, the same as my key, readable but not pointed at. Held 1.0 s. Plant 2. |
| S19 | L13 | Me walking back down the track toward town and my bakery, a sack on my shoulder, not looking back. Win small in the doorway behind. |
| S20 | L14 | Night, wide: the mill door open, a warm rectangle of light on the dark marsh. |
| S21 | L15 | Monday, day: the mill door shut. Medium on me at the step, stopped. |
| S22 | L15 | Close: the closed door, the lock plate, my cold key hanging on my chest a hand's width in front of it. The key never touches the plate. |
| S23 | L16 | The empty step, no sacks. Low rumble from inside. |
| S24 | L17 | Me knocking (cut away before the knuckles land: my raised arm, then the door). |
| S25 | L17 | Insert through the small door window: the millstones turning in their casing, flour haze. |
| S26 | L18 | Through the window, medium: Win at the hopper alone, back three-quarters to us, flour in the air. |
| S27 | L19 | Tuesday, through the window: my old stool by the stones turned to face Win's back. |
| S28 | L20 | Wednesday, through the window: the floor white with flour, and by the hoist post a clean dark patch. |
| S29 | L21 | Closer: the patch is two boot shapes, side by side. On the oak post above, two plum strokes scratched at shoulder height, upper third, held 1.8 s. Lore plant, not narrated. |
| S30 | L22 | Insert: flour drifting down onto everything in the window light, a beam, the hopper, Win's shoulders, never the patch. |
| S31 | L23 | Thursday, through the window: the clean boot patch right behind Win's stool. |
| S32 | L24 | Low close: the patch a hand's width behind her shoulder, empty air above it. |
| S33 | L24 | Win's face, calm, working, not turning. |
| S34 | L25 | Friday dusk, wide: the mill dark against a grey sky, sails still. The drone enters. |
| S35 | L25 | Me at the step, the silence, my breath. Music drop after. |
| S36 | L26 | Through the dark window: Win's stool empty by the silent stones. |
| S37 | L27 | Close: Win's flour-white headscarf caught in the shut door, stirring in the reed wind. |
| S38 | L28 | Through the window, dim: my stool turned round to face the door, toward me. |
| S39 | L29 | Night: me on the track with a torch already lit, its beam steady on the mill. |
| S40 | L30 | Through the window, the torch beam on the whitewashed wall inside, and across it a big shadow. |
| S41 | L31 | The shadow closer: head, shoulders, two arms hanging at its sides. |
| S42 | L32 | The same shadow: a second pair of arms held straight up into the beams' shadow, hands open. Hold 1.5 s. |
| S43 | L33 | My kitchen at night, one warm lamp: me at the table, the cold key in my open palm. |
| S44 | L34 | Saturday night, wide: the mill in thick fog, me a small figure on the track. |
| S45 | L35 | The door window from outside, dark, then moonlight fading up through the far window inside (2 s fade). |
| S46 | L35 | Me at the glass, face lit cool by the moon, breath on the pane. Music drop after. |
| S47 | L36 | The reveal (test still first): through the glass, the Lifter standing in the clean patch by the hoist, full figure, rim lit, two arms down, two up. |
| S48 | L37 | Low wide inside, from behind the stones: it stands taller than the door frame, the hoist chain beside it. |
| S49 | L38 | Up its body: the raised pair of arms, sleeves to open hands, palms up, a hand short of the oak beams. |
| S50 | L39 | Close on the raised palms, flour dusting on them, holding nothing. |
| S51 | L40 | Side-on: it bending at the waist toward the door, raised arms still up, head coming down. |
| S52 | L40 | My side of the glass: its face arriving behind the pane, eyes level and too far apart, pin highlights. |
| S53 | L41 | Two faces either side of the glass, a hand apart. My key on my chest. |
| S54 | L41 | Insert: its bare chest of plum smock, no cord, no key. |
| S55 | L42 | Its face, unmoved, the flat mouth. Hold. |
| S56 | L43 | Me, close, eyes dropping to my key. |
| S57 | L44 | Memory insert: S01's key glowing at a locked door. |
| S58 | L45 | Quick memory: S24, me knocking at the locked mill door this week, my key hanging cold on my chest, never at the lock. |
| S59 | L46 | Memory: S20, the mill door open at night, years of it. |
| S60 | L47 | Me, realising, face lit by the moon. |
| S61 | L48 | My key going into the keyhole, cold, then fading up gold over 1.2 s once it's in. Music drop before. |
| S62 | L49 | Gold light on my chin and the door, the Lifter's face still behind the glass above. Cover frame. |
| S63 | L50 | Insert: the key turning in the wheel-shaped escutcheon (cut away from any grip, key and plate only). |
| S64 | L51 | Inside: the door opening, moonlight and fog behind me, my foot onto the floury floor. |
| S65 | L51 | Low: my boots stepping into the clean boot patch by the hoist. |
| S66 | L52 | Wide inside: the space by the hoist is empty. Just me. The beams, the chain. |
| S67 | L52 | Close: flour drifting down onto my boots. |
| S68 | L53 | Dawn light through the door, the door opening behind me, a soft creak. |
| S69 | L54 | Win in the doorway, rolled red sail cloth under her arm, her headscarf back on. |
| S70 | L55 | The postman in the café window waving, cup in hand (a short call-back). |
| S71 | L56 | Win looking from the open door to my glowing key. |
| S72 | L57 | Win's sideways grin, close. |
| S73 | L58 | The lock plate and my key side by side in one insert: the same wheel. |
| S74 | L59 | Memory grade: S11 again, me at the shop door, the mill door open far behind. |
| S75 | L60 | Memory: Win pulling the mill door shut behind her at Friday dawn, setting off down the track. |
| S76 | L61 | Win and me on the step, my key's glow fading back over 1 s. |
| S77 | L62 | Noon: the millstones running, both of us at the stones on our two stools, flour to the elbows. |
| S78 | L62 | Win laughing, flour on her glasses. |
| S79 | L63 | Wide outside: the mill door wide open again, warm light, the sails still. |
| S80 | L64 | Close on two keys on two chests, mine and hers. |
| S81 | L65 | Monday, through the window, empty mill at dawn: by the hoist post, a clean patch of boot shapes in the fresh flour. |
| S82 | L65 | Hold on the patch, the drone thinning to nothing. Cut back to S01. Leave 0.25 s after the last word. |

## Narration (65 lines, 630 words, about 2:10 of speech at 290 wpm, about 2:20 with gaps)
Every line is `who: narrator`. CAPS are the caption key words.

L01. In this town, your KEY opens exactly one door, and it's never your OWN.
L02. It goes warm and GOLD at the one locked door it FITS.
L03. The postman's key opens the CAFE, so he's first IN.
L04. Mr Ames locked himself out of his own HOUSE.
L05. The only key that fits it is his EX-wife's.
L06. She lets him in every evening. Neither of them says a WORD.
L07. A bride's key opened her husband's door on the first TRY.
L08. I've tried every door in town. Mine has never opened ANYTHING.
L09. My great-aunt Win runs the WINDMILL on the marsh.
L10. She's the only family I've GOT.
L11. My old stool still sits beside hers at the STONES.
L12. Every morning I pick up her flour for my BAKERY.
L13. It's left on the step by the open door. I never go IN.
L14. Thirty years, open day and NIGHT.
L15. Then, this Monday, it was LOCKED.
L16. No sacks on the step. Just the stones rumbling INSIDE.
L17. I knocked. Nobody hears a thing over the STONES.
L18. Through the window, she was working ALONE.
L19. Tuesday, my old stool by the stones had been turned to face HER.
L20. Wednesday, there was a clean patch on the floury floor by the HOIST.
L21. Two boot shapes, where someone had been STANDING.
L22. Flour settles on everything in a mill. It hadn't settled THERE.
L23. Thursday, the clean patch was right behind HER.
L24. A hand's width from her SHOULDER. She never turned AROUND.
L25. Friday, the stones were SILENT. The mill was DARK.
L26. Win was GONE.
L27. Her headscarf was caught in the door, still white with FLOUR.
L28. Through the window, my old stool had been turned to face the DOOR.
L29. That night I went back with a TORCH.
L30. On the white wall inside, there was a SHADOW.
L31. A person, with two arms hanging at its SIDES.
L32. And two more arms, held straight UP.
L33. I sat up all night holding my useless KEY.
L34. Saturday, I went back in the FOG.
L35. The moon came up slowly through the little WINDOW.
L36. And it was RIGHT there.
L37. Standing in my place by the hoist. Taller than the DOOR.
L38. Two arms hanging. Two more reaching up into the BEAMS.
L39. Palms open, like it was holding up a sack that wasn't THERE.
L40. Then it bent down, SLOWLY, until its face was at the GLASS.
L41. Level with mine. There was no key around its NECK.
L42. It just looked at me, like I was LATE.
L43. And I thought about the RULE.
L44. A key only goes warm at a LOCKED door.
L45. All week it was locked, and I only ever KNOCKED.
L46. Before that, it was never locked. Not ONCE.
L47. So I'd never tried mine in IT.
L48. I lifted my key to her lock, and it went WARM.
L49. Gold, for the first time in my LIFE.
L50. It turned like it had been waiting thirty YEARS.
L51. I stepped inside, into the clean patch by the HOIST.
L52. And it was GONE. Flour started settling on my BOOTS.
L53. At dawn, the door creaked open behind ME.
L54. Win, off the first bus, new sail cloth under her ARM.
L55. She had told the postman where she was going. I never asked HIM.
L56. Win looked at the open door, then at my glowing KEY.
L57. And she said, "Took you long ENOUGH."
L58. She had known since I was born. The shape on my key matches her LOCK.
L59. She never locked it, so I'd never feel I HAD to come.
L60. This week she locked herself out of her own MILL.
L61. Only one key in town could let her back IN.
L62. By noon the stones were RUNNING. We were white to the ELBOWS.
L63. In this town, your KEY opens one door, and it's never your OWN.
L64. It's the one somebody leaves OPEN for you.
L65. When I'm late on Mondays, the flour by the hoist stays CLEAN.
