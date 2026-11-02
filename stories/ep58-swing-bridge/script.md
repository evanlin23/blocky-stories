# ep58-swing-bridge

**Slug:** `ep58-swing-bridge` (replaces batch 4's killed ep40 `night-market`, pitch #24b)

## Premise
In this town your hands glow, soft and amber, whenever somebody needs you. Mine never have, not that I've seen, and I tell myself that suits me: my wife Ada is the strong one, and I don't need anybody either. Her dad, Emrys, swung the old iron swing bridge on the river for forty-one years, and his hands were the brightest thing on the water. This spring the new road bridge opened downriver and the old one was bolted shut. Ada asks me to sit with him in the evenings in the bridge cabin, where he still waits for boats, calls me "the lodger", and watches his hands go dark week by week. Something stands on the far bank in the fog with its arms laid along the bolted bridge, and each night its hands rest a little nearer the cabin, and the second stool nobody has sat on in thirty years.

## Rule
Your hands glow while somebody needs you (L01). The montage shows it everywhere (L02 to L06), and from L10 to L17 it shows on Emrys with nobody explaining it: bright when the boats needed him, dimmer each week once nothing does. The rule says **somebody**, and it never says how big the need has to be (L53 to L54).

## Twist
My hands had been glowing for months, faintly, and it was Emrys who needed me: the gruff man who calls me the lodger and always has two mugs out before I get there. I never saw it because I only looked at my hands by the stove, where they "went orange", and I walked home with them in my pockets. The first line first reads as a rule that leaves me out (nobody needs me). After L47 to L52 it reads as a rule that was about me the whole time, and "Mine glow for EMRYS" (L64) puts it back in my mouth. The sting (L65) turns it once more: my hands woke me at three, glowing, while everyone who needs me was asleep. Something else needs me, and the cabin has a second stool.
- **Plant 1 (L18, S27):** by the stove my hands are orange, and I say it's the stove. The insert shows the backs of my hands, on the side away from the stove, holding a faint gold of their own. A rewatch sees two colours.
- **Plant 2 (L21, S31 to S32):** walking home with my hands in my pockets, a faint gold light leaks from the pocket seams, exactly as the montage set up in L06 ("Pockets don't help. The light gets OUT."). Not narrated.
- Bonus plant (L19, S28 to S29): two mugs steaming on the sill every evening before I arrive. He was waiting for me, not for boats.

## Shape
`about-me` in the package (the narrator's own marker turns out to be the loved one's need). The Keeper fits around it: the cabin was built for two bridgemen, the Span's hands rest on the second stool while the count is short, and it's gone once I sit there.

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
- Brightness is the need. Bright: the doctor and Emrys in the memories. Medium: most people. Faint: me (and only visible in the dark). Dark: the Span's hands, always.
- Every change in brightness is a slow ramp of at least 1 s, most 2 to 2.5 s. Never a flicker, never a pulse.
- **Exposure:** the hand core never clips. Keep its brightest pixel under about 235 in 8-bit, the halo well under that, and faces always brighter than the halo spill on them. Test S01 and S80 for clipping before anything else.
- My hands in daylight show nothing visible (S10, S11). In the dark they show a faint gold (S27, S32, S69). The stove light is a redder orange (#e0682a) so the two can be told apart.

## The creature: the Span (never named on screen)
**The one wrong thing: its arms are as long as the bridge.** Everything else is an ordinary man of ordinary height (Emrys's height plus his cap), standing like an old lock-keeper leaning on a balance beam. He stays on the far bank, about 30 m off, the whole film. Only his hands come nearer.
- **The read in one silhouette:** a small figure on the far bank, and two thin lines running the whole length of the bridge rail to two hands at the near end. That's the shot the whole design serves.
- **Build (one model in `set.py`, posed per shot):** ordinary R6 torso, legs and head, standing upright, leaning a few degrees forward from the ankles, never bent at the hips. Each arm leaves the shoulder, drops forward and down to the top chord of the rail at waist height, then runs flat along it: a chain of thin sleeve blocks, each about 1.5 m, laid end to end with a small fold of cloth at each join so it reads as one long sleeve, not a pipe. The two arms lie side by side on the near-side rail, a hand's width apart, perfectly straight. Arm thickness stays ordinary (the same as an ordinary forearm), so the length is the only wrongness. Hands are ordinary size.
- **Clothes:** a lock-keeper's ochre waistcoat (#8a6424) buttoned to the neck over a near-black peat-brown shirt (#2b2420), so the long sleeves read as dark lines against pale fog and apart from the green rail. Peat trousers, boots with tan toe caps (#b39a78). Skin warm clay (#c49a74). Short peat-brown block hair. Never grey, never pale.
- **Face (our own, in `faces.py`):** an ordinary face that doesn't change: two small black eyes set a touch wide, each with one pin highlight (the brightest thing on it), no brows, a short straight mouth. Head tipped down a few degrees, looking along its own arms toward the cabin.
- **Hands:** the same dull clay as its face, with no glow ever (it carries none of the town's marker). Always flat, palms down, fingers together, resting. **Never gripping, never curled, never closed on anything.** They never touch anyone and nobody is ever pulled: the nearest they come is a hand's width from Emrys's own hand on the sill.
- **Pose rules (this is what makes it read):**
  - It's never seen moving, only nearer between cuts. The hands are the only thing that changes place, and the arms are as long as they need to be to reach.
  - Shoot the arms along their length or from the side, so the lines run out of frame toward the far bank. Whenever the hands are in frame, at least a stretch of the two sleeves runs away from them, so nobody reads them as cut-off hands.
  - Behind the sleeves there is always something lighter: fog, the window, the lit plaster wall. A thin cool rim along the top of each sleeve.
  - The body is only ever seen far off on the far bank, by long lens. Its face is shown once clearly (S62), by long lens through the fog, at least 1/5 of the frame width.
- **Light it for fear:** front fill dead. The hands keyed low from the lamp and the stove's last embers, a cool blue rim from the fogged window along the sleeves. The far bank is a dark shape against bright fog (S51 to S54), then a lit figure for S62 only, caught in the slow car lights from the new bridge.
- **Test still first (before any other shot):** (1) a pure-black silhouette, side-on to the bridge against pale fog at 270x480: the small figure, the two lines along the rail, two hands at the near end. A viewer must say "its arms are as long as the bridge" within a second. (2) S63 finished at phone size, lit as planned. If either reads as a rope, a pipe, a handrail or two people, thicken the sleeve folds, lift the lines a few centimetres clear of the rail's top chord and brighten the fog behind them before building anything else.
- How it differs from earlier creatures: the Attendant's long arms were folded, white-gloved and close by, and its face was a button panel. This one's arms are laid out straight and flat, its face is ordinary, and its body never comes near. Big Hands (killed `fire-ring`) had huge hands, and these are ordinary size. It isn't too tall (the Stilted, the Walker), and it isn't bent anywhere (the Stooped, the Skater, the Wrung One). One wrong length, lying still.

**Continuity by beat**
| Beat | Lines | Where it is |
|---|---|---|
| Traces only | L22 to L23 | Not seen. Two wet handprints, flat and ordinary size, on the near end of the rail by the cabin window. The whole rail creaks in the fog, end to end. |
| Thursday, empty cabin | L24 to L27 | Not seen. The second stool is turned to face the door. |
| Monday | L34 to L35 | Body on the far bank, a small dark shape in fog. Two thin lines along the near-side rail, fading into fog halfway. Hands not seen. |
| Tuesday | L36 | Body unchanged on the far bank. Hands resting flat on the near end of the rail, by the pivot, the sleeves running back across the whole bridge. |
| Wednesday | L37 to L38 | Body unchanged. The arms run off the rail's end, across the bank, and both hands rest flat on the outside sill of the cabin's tall window, beyond the glass. |
| Thursday, inside | L40 to L46 | Body unchanged. The window's lower sash is pushed up. The arms come in over the sill and both hands rest flat on the second stool. At L45, across a cut, they rest on the inside sill by the two mugs, a hand's width from Emrys's hand. |
| Gone | L58 | The second stool is mine, the sill clear, the sash down. The far bank is empty fog, the rail bare. Not seen again. |
| Sting | L65 | Not seen. The cabin's second stool, empty, through the fog. |

## Look
- **Palette:** bridge green #4d7461 (rivets #2f4a3e), cabin brick #8a4b3a, slate #3b4048, window frames cream #d9cfb8, river slate #435766, fog #aeb9c1 at its brightest, night sky #1d2633, lamp amber #f0a24a, stove orange #e0682a, hand glow gold #ffc76a, the Span's ochre #8a6424 and peat #2b2420, my teal #2f7f86, Ada's plum #6b3a5a, Emrys's navy #26324a with brass #b8913e and a dark green cap #34493b.
- **Caption key colour:** dusk violet `#b98cff` (no other story uses it, and it sits apart from the gold hands and the ochre creature).
- **Music:** G Dorian, 76 bpm in 4/4. A thin plucked synth and a soft breathy pad for the first third, the river's lap underneath. A low sustained drone enters on L24 (the first taking) and holds to the end. `music_drops` of 0.6 s before L24 ("On Thursday, the cabin was DARK"), 0.7 s before L40 ("And it was in the cabin with US") and 0.5 s before L48 ("The stove was out"), voice and hit kept. From L57 the pad opens onto the Dorian raised sixth and the pluck plays the tune in full, warmer, then thins again for the sting.
- **Sound (all synthesized):** the river lapping, a steady far hum of road traffic from the new bridge, the iron creak of the bolted span, the stove ticking as it cools, two mugs set down, a long, slow iron creak running the whole rail end to end (L23), footsteps on gravel, the cabin door's hinge. A soft warm swell (-18 dB) as Emrys's hands come up (L57). No boat horns, no bells.
- **Light changes (flash-safe, `look.flash_safe: true`):** every change is a slow ramp. The stove burning down (L39) is a 2 s fade. The lamp going low (L39) is a 2 s fade. Emrys's hands coming up (L57) is a 2.5 s ramp. The memory shots dissolve in and out over 0.5 s. The car lights on the far bridge move slowly and never blink. Nothing flickers, nothing strobes, nothing cuts to black. Pre-check S01 to S09 (many glowing hands) and S58 to S82 with `python -m blocky flash`.

## The hits checklist (RULES.md → What the hits do)
- **Rule line:** L01, "In this town, your HANDS glow whenever somebody NEEDS you." (10 words)
- **Marker by 2 s:** S01 is a clear late afternoon on the bridge approach. Three townsfolk walk toward camera in the blue shade of the cabin wall, low sun behind lighting the river, their hands glowing gold. The doctor's face is at least 1/4 of the frame width, high in frame, out of the caption band. Faces lit by soft bounce, brighter than the glow.
- **Montage (L02 to L06, about 2 to 13 s), four examples:** the doctor who can't hide in the cinema. The man whose dog at home makes him glow all through work. The couple after a row, both glowing, both pretending not to. Pockets don't help, the light leaks out (the setup for plant 2).
- **Narrator as the exception:** my hands have never glowed (L08), nobody needs me, and I don't need anybody (L09).
- **Loved one at stake:** Emrys, my father-in-law, an adult in his seventies. His hands go dark as nothing needs him, he goes missing for a night (L24 to L31), and the Span's hands rest nearer each night, until they lie on the stool beside him.
- **15 to 30 s:** L09 to L14 show the rule at work on Emrys (his hands lighting the water in the memory, then the bridge bolted shut). Nobody explains it.
- **First real scare and taking:** L24 to L27 (about 55 to 63 s): the dark cabin, the open door, his cap on the wheel, his warm mug, the second stool turned to face me. He's back at breakfast for an ordinary reason (L29 to L31).
- **Creature little and late:** traces at L22 to L23, a shape in fog at L34 to L35, its hands nearer at L36 to L37, shown clearly from L40 (about 63% in), its hands nearer Emrys at L45.
- **Loophole climax:** the rule says somebody, and one person is enough (L53 to L54). I need him and say so (L55 to L56), and his hands come up (L57).
- **Readable first 2 s:** high key, faces and glowing hands in frame, no fog or dark until L22.
- **Cuts:** 91 shots over about 141 s, an average of about 1.55 s.

## The last 15 seconds turn the first line
L59 to L65. The wave he gave every boat, given to me, and my name. Then the rule comes back (L63) and lands on me: "Mine glow for EMRYS." The first line, which sounded like a rule that left me out, was about me from the first evening in the cabin. The last line turns it again and lands cold: at three in the morning my hands woke me, glowing, while everyone who needs me was asleep. The loop drops back into L01, and on a second watch the "somebody" in it has a stool by the wheel. Rewatch plants: the two colours on my hands by the stove (L18, S27) and the light leaking from my pockets (L21, S31 to S32).

## Lore connection (one)
A plain tally: two short ochre strokes scratched into the brass hub plate of the iron wheel, two for a cabin built for two bridgemen, in the Span's own ochre (lore.md → Open threads → Third parallel batch). Shown once in S22, under L15 ("Every evening he sat in the cabin by the wheel"), held about 1.8 s, never narrated. No extra stroke, nothing else of the canon.

## Shot plan
Timings are estimates at about 290 wpm. Re-time from `voice-timings.json`. Every shot with a face as its subject keeps the face at least 1/5 of the frame width and out of the caption band. The Span's body is only ever seen far off, on the far bank. Its hands are only ever seen with the sleeves running away from them.

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
| S33 | L22 | Night fog on the deck: the near end of the rail, beaded with wet. |
| S34 | L22 | Insert: two wet handprints, flat, ordinary size, side by side on the rail's top chord, and nothing beyond them. |
| S35 | L23 | Long lens down the whole rail in fog: the iron flexing faintly end to end, nobody there. Music drop after. |
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
| S51 | L34 | Through the tall window: the far bank in fog, a small dark figure at the end of the rail. |
| S52 | L34 | Long lens from the bank path, side-on to the bridge: the figure leaning on the far end of the rail, like a man at a lock gate. |
| S53 | L35 | Same lens, wider: two thin dark lines along the top of the rail, out from the figure into the fog. No face detail. |
| S54 | L36 | Tuesday, side-on to the bridge against bright fog: the figure small on the far bank, two lines along the whole rail, two hands resting flat at our end. The silhouette read. |
| S55 | L37 | Wednesday, from the path: the arms running off the rail, across the bank, up to the cabin's tall window. |
| S56 | L37 | From inside, through the glass: two flat clay hands resting on the outside sill, the sleeves running back into the fog. |
| S57 | L38 | Insert: its dull clay hands on the sill outside the glass. Inside, beyond the pane, Emrys's faint glow. |
| S58 | L39 | Thursday: the stove's fire sinking (2 s fade). |
| S59 | L39 | The bracket lamp turning low (2 s fade). Music drop after. |
| S60 | L40 | Wide from the cabin corner: Emrys on his stool, the window's lower sash pushed up, two dark lines coming in over the sill. |
| S61 | L41 | Three-quarter medium: its two hands resting flat on the second stool beside Emrys, the sleeves running back out of the window, lamp key from low and to the side, cool rim from the window. |
| S62 | L42 | Long lens from the cabin window across the bridge: the man on the far bank, ochre waistcoat buttoned, head tipped down, caught in the slow car lights. Face at least 1/5 of the frame width. |
| S63 | L43 | The reveal (test still first): wide, side-on to the bridge, the whole span in frame: the small figure on the far bank, the two sleeves along the full rail, over the bank, in at the cabin window. |
| S64 | L44 | Low along the rail at its height: the two sleeves running straight away to a vanishing point in the fog, side by side, a hand's width apart. |
| S65 | L45 | After a cut: the hands now resting on the inside sill by the two mugs, a hand's width from Emrys's hand. Still, flat, not gripping. |
| S66 | L45 | Emrys's face, unaware, eyes down on his hands. |
| S67 | L46 | Insert: Emrys's hands, dark. |
| S68 | L47 | Me, looking down at my own hands. |
| S69 | L48 | Low over my shoulder: my two hands glowing gold in the lower left foreground, the stove black, and beyond them its two dark hands on the sill beside Emrys's, the sleeves running out of the window, clearly lit. Cover frame. |
| S70 | L49 | My face lit from below by my own hands. |
| S71 | L50 | Callback (0.3 s dissolve): S27, the gold on the far side of my hands. |
| S72 | L50 | Callback: S32, the light at my pocket seam. |
| S73 | L51 | Me looking up at Emrys. |
| S74 | L52 | Callback: S28, the two mugs steaming before I arrive. |
| S75 | L53 | Wide: the dark river and the bolted bridge in fog. |
| S76 | L54 | Me close, deciding. |
| S77 | L55 | Two-shot across the dead stove: me talking, Emrys listening, its hands still on the sill beside him. |
| S78 | L56 | Emrys turning to look at me properly for the first time. |
| S79 | L57 | His hands glowing up slowly (2.5 s ramp). |
| S80 | L57 | His face lit warm from below by his own hands. |
| S81 | L58 | Me sitting down on the second stool, three-quarter. |
| S82 | L58 | Through the window: the sill clear, the sash down, the rail bare, the far bank empty fog. |
| S83 | L59 | Next evening at dusk, side view: me crossing the old bridge on foot, hands glowing faintly. |
| S84 | L60 | Emrys at the cabin window raising one flat, bright hand. |
| S85 | L61 | Memory callback (summer grade): the same wave to a passing boat. |
| S86 | L62 | Me grinning, lifting my glowing hand back. |
| S87 | L62 | Ada on the bank path, seeing both, smiling. |
| S88 | L63 | Wide: the bridge at dusk, the cabin's warm window, two pairs of glowing hands. |
| S89 | L64 | Close: my hands and Emrys's side by side on the cabin sill by the two mugs. |
| S90 | L65 | Our bedroom at 3 a.m.: my hands glowing bright on the blanket, Ada asleep beside me. |
| S91 | L65 | The cabin in fog from the bank path, dark, the second stool empty in the window. Cut back to S01. Leave 0.25 s after the last word. |

## Narration (65 lines, 605 words, about 2:05 of speech at 290 wpm, about 2:22 with gaps)
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
L22. Then two wet handprints appeared on the rail by his WINDOW.
L23. And the whole rail CREAKED in the FOG.
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
L34. On Monday, something stood on the far BANK.
L35. Just a shape in the fog, leaning on the RAIL.
L36. On Tuesday, its hands were at OUR end.
L37. On Wednesday, they were on the cabin WINDOWSILL.
L38. Its hands didn't glow at ALL.
L39. On Thursday, the stove burned down, and the lamp went LOW.
L40. And its hands were in the cabin with US.
L41. Resting on the second STOOL, beside Emrys.
L42. Out on the far bank, an ordinary man in an ochre WAISTCOAT.
L43. But its arms were as long as the BRIDGE.
L44. Laid flat along the rail, all the way to US.
L45. Every time I looked away, they lay nearer HIM.
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
L58. I sat on the second stool, and the far bank was EMPTY.
L59. The next evening, I crossed the old bridge at DUSK.
L60. Emrys raised one bright hand at the cabin WINDOW.
L61. The wave he gave every boat for forty-one YEARS.
L62. And he called me by my NAME.
L63. In this town, your hands glow when somebody NEEDS you.
L64. Mine glow for EMRYS.
L65. At three this morning, they woke me, GLOWING. Everyone who needs me was ASLEEP.
