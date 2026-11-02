# ep58-swing-bridge

**Slug:** `ep58-swing-bridge` (replaces batch 4's killed ep40 `night-market`, pitch #24b)

## Premise
In this town your hands glow, soft and amber, whenever somebody needs you. Mine never have, not that I've seen, and I tell myself that suits me: my wife Ada is the strong one, and I don't need anybody either. Her dad, Emrys, swung the old iron swing bridge on the river for forty-one years, and his hands were the brightest thing on the water. This spring the new road bridge opened downriver and the old one was bolted shut. Ada asks me to sit with him in the evenings in the bridge cabin, where he still waits for boats, calls me "the lodger", and watches his hands go dark week by week. Something is crossing the bolted bridge in the fog, one stretch nearer the cabin each night, toward the second stool nobody has sat on in thirty years.

## Rule
Your hands glow while somebody needs you (L01). The montage shows it everywhere (L02 to L06), and from L10 to L17 it shows on Emrys with nobody explaining it: bright when the boats needed him, dimmer each week once nothing does. The rule says **somebody**, and it never says how big the need has to be (L53 to L54).

## Twist
My hands had been glowing for months, faintly, and it was Emrys who needed me: the gruff man who calls me the lodger and always has two mugs out before I get there. I never saw it because I only looked at my hands by the stove, where they "went orange", and I walked home with them in my pockets. The first line first reads as a rule that leaves me out (nobody needs me). After L47 to L52 it reads as a rule that was about me the whole time, and "Mine glow for EMRYS" (L64) puts it back in my mouth. The sting (L65) turns it once more: my hands woke me at three, glowing, while everyone who needs me was asleep. Something else needs me, and the cabin has a second stool.
- **Plant 1 (L18, S27):** by the stove my hands are orange, and I say it's the stove. The insert shows the backs of my hands, on the side away from the stove, holding a faint gold of their own. A rewatch sees two colours.
- **Plant 2 (L21, S31 to S32):** walking home with my hands in my pockets, a faint gold light leaks from the pocket seams, exactly as the montage set up in L06 ("Pockets don't help. The light gets OUT."). Not narrated.
- Bonus plant (L19, S28 to S29): two mugs steaming on the sill every evening before I arrive. He was waiting for me, not for boats.

## Shape
`about-me` in the package (the narrator's own marker turns out to be the loved one's need). The Keeper fits around it: the cabin was built for two bridgemen, the Heron stands at the second stool while the count is short, and it's gone once I sit there.

## World
One made-up river town in late autumn. No real names and no words anywhere in the set: no signs, no plaques, no lettering on the bridge, the cinema or the van.
- **The old swing bridge:** a short iron truss swing span in bridge green, riveted lattice sides waist high, a plank deck walkway, turning on a stone pier at the near bank. Big iron bolts and a steel plate now pin the span shut (S18). A striped barrier arm (stripes only) at the near end.
- **The cabin:** a small red-brown brick hut on the near bank beside the pivot, slate roof, a stubby chimney. Inside: a vertical iron wheel a metre across with a brass hub plate and one crank handle (never shown gripped), a squat pot-bellied stove, a lamp on a wall bracket at shoulder height, a window sill with two mugs, and two wooden stools: Emrys's by the wheel, the second one beside it. One tall window (sill at knee height) looks out at the deck at an angle of about 50 degrees, so anything on the deck is seen three-quarter from inside, never head-on.
- **The bank path:** a gravel path along the river with one iron lamp post, reeds, and far downriver the new concrete road bridge, a pale arch with a slow string of small car lights (steady, never flashing).
- **Montage places (one shot or two each):** a small cinema (the screen shows only soft coloured light), an office meeting table, a house window with a dog, a sofa in a living room.
- **Home:** our kitchen table (L13, L29) and our bedroom at night (L65).
- **Weather:** the opening is a clear late afternoon. From L22 the evenings bring river fog. The memory shots (L11, L61) are a warm summer evening.

## Cast (all adults, nobody in peril, nobody hurt, nobody in or near the water)
- **me** (narrator, man in his thirties): teal knit jumper with a cream zigzag band, dark jeans, a dark navy coat with deep pockets outdoors, short brown block hair. Our own face: round eyes, slightly raised brows, a small flat mouth that turns into a crooked grin at the end.
- **Emrys** (my father-in-law, early seventies): navy bridgeman's jacket with brass buttons, dark green flat cap, iron-grey block hair and a thick block moustache. Heavy brows, a mouth that rarely moves. Never ill or hurt, only tired and stubborn.
- **Ada** (my wife, thirties): plum coat, auburn curly block hair, quick smile. Capable. In three or four shots.
- **Montage extras (one beat each, never named):** the doctor (woman, forest-green coat, hood up), the office man (grey suit) and his dog (a blocky terrier, at home), the couple on the sofa (mustard cardigan, striped shirt), the man with his hands in his coat pockets, the man in a hard hat at the new bridge (L30 to L31).
- Characters speak only in reported speech. Nobody explains the rule on screen.

## The marker: glowing hands (visible by 2 s, on every character but the creature)
- The hand blocks themselves glow: a soft amber-gold (#ffc76a) from inside the hand, with a small soft halo and a little warm light spill on the sleeve, coat and ground (one small point light per hand). It reads as "carrying light", never as gloves or as fire.
- Brightness is the need. Bright: the doctor and Emrys in the memories. Medium: most people. Faint: me (and only visible in the dark). Dark: the Heron, always.
- Every change in brightness is a slow ramp of at least 1 s, most 2 to 2.5 s. Never a flicker, never a pulse.
- **Exposure:** the hand core never clips. Keep its brightest pixel under about 235 in 8-bit, the halo well under that, and faces always brighter than the halo spill on them. Test S01 and S80 for clipping before anything else.
- My hands in daylight show nothing visible (S10, S11). In the dark they show a faint gold (S27, S32, S69). The stove light is a redder orange (#e0682a) so the two can be told apart.

## The creature: the Heron (never named on screen)
**The one wrong thing: its knees bend backwards.** Everything else is an ordinary man. Overall height is exactly an ordinary adult's (Emrys's height plus his cap), so the bend is the only wrongness.
- **Build (one model in `set.py`, posed per shot):** ordinary R6 torso, arms and head. Each leg is two blocks, thigh and shin, with a visible fold of trouser cloth at the joint. The thigh slopes down and **back** from the hip. The knee is the point furthest back, at least one full leg-width behind the line from hip to heel. The shin slopes down and **forward** to the foot, so the foot sits under the hip. Lengthen the two blocks a little so the hips stay at ordinary height: it must never read as crouching.
- **Clothes:** an ochre work coat (#8a6424) buttoned to the neck, near-black peat-brown trousers (#2b2420) so the leg shape reads dark against pale fog, and boots with big tan toe caps (#b39a78) that point the same way as its face. Skin warm clay (#c49a74). Short peat-brown block hair. Never grey, never pale.
- **Face (our own, in `faces.py`):** an ordinary face that doesn't change: two small black eyes set a touch wide, each with one pin highlight (the brightest thing on it), no brows, a short straight mouth. Head tipped down a few degrees.
- **Hands:** the same dull clay as its face, with no glow ever. It carries none of the town's marker.
- **Pose rules (this is what makes it read):**
  - **Only ever side-on or three-quarter** (about 35 to 60 degrees off front). Never straight front: the knees vanish. Never straight back: it reads as a normal person facing away with normal knees.
  - In three-quarter shots, show the face, the coat buttons and the toe caps pointing the same way, so the direction it faces is never in doubt.
  - Behind its legs there is always something lighter than its trousers: fog, the lit plaster wall, the window. Put a rim light on the back of the thigh and the front of the shin.
  - Arms hang straight, a little forward of the body. It never touches anyone. When it leans over Emrys there's a clear hand's width between them.
  - It's never seen moving, only nearer between cuts. The lean at the reveal is a new pose across a cut.
- **Light it for fear:** front fill dead. In the cabin, key from the low lamp and the stove's last embers below and to the side, a cool blue rim from the fogged window. On the deck, it's a dark shape against bright fog first (S51 to S54), then a lit figure (S55 to S65).
- **Test still first (before any other shot):** (1) a pure-black silhouette of the Heron beside Emrys, side-on against pale fog at 270x480. A viewer must say "its knees bend the wrong way" within a second. (2) S63 finished at phone size, lit as planned. If either reads as crouching, sitting, a bird costume or a person facing the other way, push the knee further back and the shin's slope further forward before building anything else.
- How it differs from earlier creatures: it isn't too tall (the Stilted's legs were three times too long), it doesn't fold twice like the Skater, and it isn't stooped at the hips like the Stooped. One joint, the wrong way.

**Continuity by beat**
| Beat | Lines | Where it is |
|---|---|---|
| Traces only | L22 to L23 | Not seen. Wet shoe prints (ordinary size) from the far bank to below the cabin window, then none. The deck boards dip and creak in the fog. |
| Thursday, empty cabin | L24 to L27 | Not seen. The second stool is turned to face the door. |
| Monday | L34 to L35 | The far end of the deck, about 30 m off, side-on, facing along the deck toward the cabin. A dark shape in fog, legs barely readable. |
| Tuesday | L36 | Halfway across, by the bolted pivot plate, side-on. Legs read clearly in silhouette, face not yet. |
| Wednesday | L37 to L38 | On the bank just outside the tall window, three-quarter, head turned to the glass, face lit by the cabin lamp, shins visible through the low panes. |
| Thursday, inside | L40 to L46 | Standing behind Emrys beside the second stool, three-quarter. At L45 it leans down from the hips over his shoulder, knees still bent back, a hand's width from his cheek. |
| Gone | L58 | The corner behind Emrys is empty, fog at the window. Not seen again. |
| Sting | L65 | Not seen. The cabin's second stool, empty, through the fog. |

## Look
- **Palette:** bridge green #4d7461 (rivets #2f4a3e), cabin brick #8a4b3a, slate #3b4048, window frames cream #d9cfb8, river slate #435766, fog #aeb9c1 at its brightest, night sky #1d2633, lamp amber #f0a24a, stove orange #e0682a, hand glow gold #ffc76a, Heron ochre #8a6424 and peat #2b2420, my teal #2f7f86, Ada's plum #6b3a5a, Emrys's navy #26324a with brass #b8913e and a dark green cap #34493b.
- **Caption key colour:** dusk violet `#b98cff` (no other story uses it, and it sits apart from the gold hands and the ochre creature).
- **Music:** G Dorian, 76 bpm in 4/4. A thin plucked synth and a soft breathy pad for the first third, the river's lap underneath. A low sustained drone enters on L24 (the first taking) and holds to the end. `music_drops` of 0.6 s before L24 ("On Thursday, the cabin was DARK"), 0.7 s before L40 ("And it was in the cabin with US") and 0.5 s before L48 ("The stove was out"), voice and hit kept. From L57 the pad opens onto the Dorian raised sixth and the pluck plays the tune in full, warmer, then thins again for the sting.
- **Sound (all synthesized):** the river lapping, a steady far hum of road traffic from the new bridge, the iron creak of the bolted span, the stove ticking as it cools, two mugs set down, a slow pitched-down wooden groan for the deck boards (L23), footsteps on gravel, the cabin door's hinge. A soft warm swell (-18 dB) as Emrys's hands come up (L57). No boat horns, no bells.
- **Light changes (flash-safe, `look.flash_safe: true`):** every change is a slow ramp. The stove burning down (L39) is a 2 s fade. The lamp going low (L39) is a 2 s fade. Emrys's hands coming up (L57) is a 2.5 s ramp. The memory shots dissolve in and out over 0.5 s. The car lights on the far bridge move slowly and never blink. Nothing flickers, nothing strobes, nothing cuts to black. Pre-check S01 to S09 (many glowing hands) and S58 to S82 with `python -m blocky flash`.

## The hits checklist (RULES.md → What the hits do)
- **Rule line:** L01, "In this town, your HANDS glow whenever somebody NEEDS you." (10 words)
- **Marker by 2 s:** S01 is a clear late afternoon on the bridge approach. Three townsfolk walk toward camera in the blue shade of the cabin wall, low sun behind lighting the river, their hands glowing gold. The doctor's face is at least 1/4 of the frame width, high in frame, out of the caption band. Faces lit by soft bounce, brighter than the glow.
- **Montage (L02 to L06, about 2 to 13 s), four examples:** the doctor who can't hide in the cinema. The man whose dog at home makes him glow all through work. The couple after a row, both glowing, both pretending not to. Pockets don't help, the light leaks out (the setup for plant 2).
- **Narrator as the exception:** my hands have never glowed (L08), nobody needs me, and I don't need anybody (L09).
- **Loved one at stake:** Emrys, my father-in-law, an adult in his seventies. His hands go dark as nothing needs him, he goes missing for a night (L24 to L31), and the Heron closes in on the stool beside him.
- **15 to 30 s:** L09 to L14 show the rule at work on Emrys (his hands lighting the water in the memory, then the bridge bolted shut). Nobody explains it.
- **First real scare and taking:** L24 to L27 (about 55 to 63 s): the dark cabin, the open door, his cap on the wheel, his warm mug, the second stool turned to face me. He's back at breakfast for an ordinary reason (L29 to L31).
- **Creature little and late:** traces at L22 to L23, a shape in fog at L34 to L37, shown clearly from L40 (about 63% in), leaning in at L45.
- **Loophole climax:** the rule says somebody, and one person is enough (L53 to L54). I need him and say so (L55 to L56), and his hands come up (L57).
- **Readable first 2 s:** high key, faces and glowing hands in frame, no fog or dark until L22.
- **Cuts:** 91 shots over about 141 s, an average of about 1.55 s.

## The last 15 seconds turn the first line
L59 to L65. The wave he gave every boat, given to me, and my name. Then the rule comes back (L63) and lands on me: "Mine glow for EMRYS." The first line, which sounded like a rule that left me out, was about me from the first evening in the cabin. The last line turns it again and lands cold: at three in the morning my hands woke me, glowing, while everyone who needs me was asleep. The loop drops back into L01, and on a second watch the "somebody" in it has a stool by the wheel. Rewatch plants: the two colours on my hands by the stove (L18, S27) and the light leaking from my pockets (L21, S31 to S32).

## Lore connection (one)
A plain tally: two short ochre strokes scratched into the brass hub plate of the iron wheel, two for a cabin built for two bridgemen, in the Heron's own ochre (lore.md → Open threads → Third parallel batch). Shown once in S22, under L15 ("Every evening he sat in the cabin by the wheel"), held about 1.8 s, never narrated. No extra stroke, nothing else of the canon.

## Shot plan
Timings are estimates at about 290 wpm. Re-time from `voice-timings.json`. Every shot with a face as its subject keeps the face at least 1/5 of the frame width and out of the caption band. The Heron is only ever side-on or three-quarter.

| Shot | Line | Picture |
|---|---|---|
| S01 | L01 | Bridge approach, clear late afternoon: three townsfolk walking toward camera in the blue shade of the cabin wall, hands glowing gold, the doctor's face large upper frame. Hook frame. |
| S02 | L01 | Close: a passer-by's two glowing hands at his sides, warm spill on his coat. |
| S03 | L02 | A small cinema, back row: the doctor hunched with her hood up, the screen's soft colour on her face. |
| S04 | L03 | Wider from the front: her hands light up the whole back row, faces turning round to her. |
| S05 | L04 | An office meeting table: the man in the grey suit trying to look serious, his hands glowing under the table. |
| S06 | L04 | Cut: his blocky terrier at a house window, waiting, nose to the glass. |
| S07 | L05 | A living room sofa after a row: the couple at opposite ends, arms folded, both sets of hands glowing under their elbows. |
| S08 | L05 | Close: her sideways glance at his glow, then away. |
| S09 | L06 | A man shoving his hands into his coat pockets. Gold light leaks out of the pocket mouths and seams. |
| S10 | L07 | Me on the bridge approach in daylight, medium, hands at my sides, nothing showing. |
| S11 | L08 | Close: my hands held up, palms to camera, plain in daylight. |
| S12 | L09 | Ada in her plum coat lifting a crate into the car boot herself, hands glowing. Me hovering beside her, useless. |
| S13 | L09 | Me shrugging, hands in pockets. |
| S14 | L10 | Emrys at the cabin door, medium: navy jacket, green cap, moustache, the green swing bridge behind him. |
| S15 | L11 | Memory (warm summer grade, 0.5 s dissolve in): the bridge swung open, a small sailing boat's mast passing, Emrys at the cabin window, hands blazing gold. |
| S16 | L11 | Memory wide at dusk: his glow reflected in long gold streaks on the water. |
| S17 | L12 | Present, wide: downriver, the pale new road bridge with a slow line of car lights. |
| S18 | L12 | Insert: big iron bolts and a steel plate pinning the swing span shut. |
| S19 | L13 | Our kitchen table: Ada asking me, her hand on my sleeve. |
| S20 | L14 | Emrys at the cabin door, flat look, me on the path with my hands in my pockets. |
| S21 | L15 | Inside the cabin: Emrys on his stool by the iron wheel, watching the window. |
| S22 | L15 | Insert: the wheel's brass hub plate, two short ochre strokes scratched in it. Held 1.8 s. Lore plant, not narrated. |
| S23 | L16 | Emrys's hands on his knees, the glow a shade dimmer than the memory. |
| S24 | L16 | Same framing a week later (0.3 s dissolve): dimmer still. |
| S25 | L17 | October dusk, cabin lamp unlit: his hands a faint glow in the dark corner. |
| S26 | L18 | Me on an upturned crate by the stove (never on the second stool), hands held out, lit orange. |
| S27 | L18 | Insert: my hands. Stove side red-orange, the far side a faint gold of its own. Plant 1. |
| S28 | L19 | The sill as I come in the door: two mugs, both steaming. Bonus plant. |
| S29 | L19 | Emrys not looking at me. One mug already on my side of the sill. |
| S30 | L20 | The two stools by the wheel: his, worn, and the second one, empty. |
| S31 | L21 | Me walking home along the bank path at dusk, hands in my coat pockets. Plant 2. |
| S32 | L21 | Close on my coat pocket: a faint gold line of light at the seam. Plant 2, not narrated. |
| S33 | L22 | Night fog on the deck: wet shoe prints crossing the planks from the far bank. |
| S34 | L22 | The prints end on the bank below the cabin's tall window. |
| S35 | L23 | The deck in fog, a board dipping as if under weight, nobody there. Music drop after. |
| S36 | L23 | Inside: Emrys not looking up, watching his hands. |
| S37 | L24 | Thursday dusk, from the path: the cabin window dark. |
| S38 | L24 | The door standing open. |
| S39 | L25 | Inside, dim blue light: his stool empty. |
| S40 | L26 | His cap hanging on the wheel's crank handle. |
| S41 | L26 | His mug on the sill, a thin thread of steam. |
| S42 | L27 | The second stool turned to face the door, toward camera. |
| S43 | L27 | Me in the doorway, frozen. |
| S44 | L28 | The bank path in fog: me with a torch (steady beam), calling out. |
| S45 | L28 | My face lit by my phone, Ada on the line. |
| S46 | L29 | Our kitchen at breakfast: Emrys in the doorway, mud up to his knees, cap missing. |
| S47 | L30 | Wide: Emrys small under the huge concrete arch of the new bridge, facing a man in a hard hat. |
| S48 | L31 | The hard-hat man shaking his head. Emrys's face. |
| S49 | L32 | Night, the cabin: Emrys's hands with only the faintest glow left. |
| S50 | L33 | Me pulling my crate to the stove. Emrys on his stool, the second stool empty between us. |
| S51 | L34 | Through the tall window: the far end of the deck in fog, a dark figure standing side-on. |
| S52 | L34 | Long lens from the bank path, side-on: still far, a shape in the fog. |
| S53 | L35 | Closer, still in fog, side-on: the legs make the wrong angle in silhouette. No face detail. |
| S54 | L36 | Tuesday, from the bank path: halfway across by the bolt plate, side-on, the knees clearly bent back against bright fog. |
| S55 | L37 | Wednesday, from the path: on the bank beside the cabin window, three-quarter, head turned to the glass. |
| S56 | L37 | From inside, three-quarter through the glass: its face at the window, pin highlights, the slanting shins in the low panes. |
| S57 | L38 | Insert: its dull clay hands at its sides by the glass. Beyond it, inside, Emrys's faint glow. |
| S58 | L39 | Thursday: the stove's fire sinking (2 s fade). |
| S59 | L39 | The bracket lamp turning low (2 s fade). Music drop after. |
| S60 | L40 | Wide from the cabin corner: Emrys on his stool, and a figure standing behind him. |
| S61 | L41 | Three-quarter medium: the Heron by the second stool behind Emrys's shoulder, lamp key from low and to the side, cool rim from the window. |
| S62 | L42 | Its face and coat: an ordinary man, ochre coat buttoned, head tipped down. |
| S63 | L43 | The reveal (test still first): full body three-quarter, the knee points behind, the shins slanting forward to the toe caps, the lit plaster wall behind its legs. |
| S64 | L44 | Low side-on at shin height: the backward knee and the forward shin, toe caps pointing the way its face does. |
| S65 | L45 | It leans down from the hips over Emrys's shoulder, a hand's width from his cheek, knees still bent back. |
| S66 | L45 | Emrys's face, unaware, eyes down on his hands. |
| S67 | L46 | Insert: Emrys's hands, dark. |
| S68 | L47 | Me, looking down at my own hands. |
| S69 | L48 | Low over my shoulder: my two hands glowing gold in the lower left foreground, the stove black, and beyond them the Heron leaning over Emrys, clearly lit. Cover frame. |
| S70 | L49 | My face lit from below by my own hands. |
| S71 | L50 | Callback (0.3 s dissolve): S27, the gold on the far side of my hands. |
| S72 | L50 | Callback: S32, the light at my pocket seam. |
| S73 | L51 | Me looking up at Emrys. |
| S74 | L52 | Callback: S28, the two mugs steaming before I arrive. |
| S75 | L53 | Wide: the dark river and the bolted bridge in fog. |
| S76 | L54 | Me close, deciding. |
| S77 | L55 | Two-shot across the dead stove: me talking, Emrys listening, the Heron still bent behind him. |
| S78 | L56 | Emrys turning to look at me properly for the first time. |
| S79 | L57 | His hands glowing up slowly (2.5 s ramp). |
| S80 | L57 | His face lit warm from below by his own hands. |
| S81 | L58 | Me sitting down on the second stool, three-quarter. |
| S82 | L58 | Behind Emrys: nobody. The corner empty, fog at the window. |
| S83 | L59 | Next evening at dusk, side view: me crossing the old bridge on foot, hands glowing faintly. |
| S84 | L60 | Emrys at the cabin window raising one flat, bright hand. |
| S85 | L61 | Memory callback (summer grade): the same wave to a passing boat. |
| S86 | L62 | Me grinning, lifting my glowing hand back. |
| S87 | L62 | Ada on the bank path, seeing both, smiling. |
| S88 | L63 | Wide: the bridge at dusk, the cabin's warm window, two pairs of glowing hands. |
| S89 | L64 | Close: my hands and Emrys's side by side on the cabin sill by the two mugs. |
| S90 | L65 | Our bedroom at 3 a.m.: my hands glowing bright on the blanket, Ada asleep beside me. |
| S91 | L65 | The cabin in fog from the bank path, dark, the second stool empty in the window. Cut back to S01. Leave 0.25 s after the last word. |

## Narration (65 lines, 593 words, about 2:03 of speech at 290 wpm, about 2:20 with gaps)
Every line is `who: narrator`. CAPS are the caption key words.

L01. In this town, your HANDS glow whenever somebody NEEDS you.
L02. The doctor hid at the back of the CINEMA.
L03. Her hands lit up the whole ROW.
L04. His dog's waiting at HOME, so he glows all through WORK.
L05. After a row, you both glow, and you both pretend you DON'T.
L06. Pockets don't help. The light gets OUT.
L07. And then there's ME.
L08. My hands have never glowed. Not that I've SEEN.
L09. Ada's the strong one, so nobody needs me. And I don't need ANYBODY.
L10. My wife's dad, Emrys, ran the old swing bridge for forty-one YEARS.
L11. Every boat on the river needed him, and his hands lit the WATER.
L12. Then the new road bridge opened, and they bolted his SHUT.
L13. Ada asked me to sit with him in the EVENINGS.
L14. He still calls me the LODGER.
L15. Every evening he sat in the cabin by the wheel, waiting for BOATS.
L16. And week by week, his hands got DIMMER.
L17. By October, you could only see them in the DARK.
L18. I sat by the stove, and my hands went ORANGE. That was the STOVE.
L19. He always had two mugs out before I got THERE.
L20. There were two stools. Nobody had sat on the second in thirty YEARS.
L21. Walking home, I kept my hands in my POCKETS. It was COLD.
L22. Then wet prints crossed the deck to his WINDOW, and STOPPED.
L23. Something heavy made the boards CREAK, out in the FOG.
L24. On Thursday, the cabin was DARK. The door was OPEN.
L25. Emrys wasn't THERE.
L26. His cap hung on the wheel. His mug was still WARM.
L27. And the second stool was turned to face the DOOR. To face ME.
L28. I searched the bank till midnight. Nobody had SEEN him.
L29. He came home at breakfast, mud up to his KNEES.
L30. He'd walked to the new bridge to ask if they needed a HAND.
L31. They DIDN'T.
L32. That night his hands were nearly DARK.
L33. He wouldn't leave the cabin, so NEITHER did I.
L34. On Monday, something stood at the far end of the DECK.
L35. Just a shape in the fog, standing WRONG.
L36. On Tuesday, it was halfway ACROSS.
L37. On Wednesday, it was at the WINDOW.
L38. Its hands didn't glow at ALL.
L39. On Thursday, the stove burned down, and the lamp went LOW.
L40. And it was in the cabin with US.
L41. Behind Emrys, by the second STOOL.
L42. An ordinary man in an ochre COAT.
L43. But its knees bent BACKWARDS.
L44. Like a bird's, with the shins slanting out in FRONT.
L45. And slowly, it leaned down over his SHOULDER.
L46. Emrys stared at his hands. They were DARK.
L47. Then I saw MINE.
L48. The stove was out, and my hands were GLOWING.
L49. Faintly. And they'd been glowing for MONTHS.
L50. By the stove. In my POCKETS.
L51. Somebody needed me. It was HIM.
L52. Two mugs out, every night, before I got THERE.
L53. I'd thought need had to be big, like a boat or a BRIDGE.
L54. But the rule just says SOMEBODY. One is ENOUGH.
L55. So I told him I didn't know how to be in this FAMILY.
L56. And that I needed him to show ME.
L57. His hands came up slowly, like a lamp turned UP.
L58. I sat on the second stool, and behind him, there was NOBODY.
L59. The next evening, I crossed the old bridge at DUSK.
L60. Emrys raised one bright hand at the cabin WINDOW.
L61. The wave he gave every boat for forty-one YEARS.
L62. And he called me by my NAME.
L63. In this town, your hands glow when somebody NEEDS you.
L64. Mine glow for EMRYS.
L65. At three this morning, they woke me, GLOWING. Everyone who needs me was ASLEEP.
