# every-lock: the script (writer, 2026-11-03)

- **Slug:** `every-lock` (batch 6, slot P5, the lead's slug, and it uploads in the order the queue sets)
- **From:** batch 6 brief pitch W4 ("Every Door I Close Gets Another LOCK 🔒"), the what-if escalation lane (`docs/research/port-study.md` → What-if escalation). Kept: the lock meter that doubles, the apartment's doors, a fight over a door. Changed: the escalation is stated as fact, the slammer is my big sister, and the title is now a statement about the slam ("Every Slam DOUBLES The Locks 🔒").
- **Lane:** experiment (what-if escalation). **Length arm:** long.
- **Word count:** 568 spoken words in 72 lines, all `narrator`, plus 2 music drops (1.2 s) and the lore shot held inside L57.
- **Estimated length:** 568 words at 290 wpm is 1:58 of speech. The 0.12 s gaps add 8.5 s, the drops 1.2 s and the loop tail 0.25 s: about 2:08 to 2:12. If it lands under 2:00, add "The DOG next door / walks in / for BREAKFAST." after L06. If it lands over 2:30, cut L45 first, then L62.
- **Look:** `look.style: "closer"`, `look.flash_safe: true`, `look.polish: true` if the polish pack has merged. Bright and saturated everywhere except one scene (the night, L36 to L54), which is lit by warm night lights, never black.

## The big idea

**A lock is a little door too: every lock has a flap over its keyhole, so once a door carries enough locks, one flap swings shut on its own, that lock gets a lock, and the door starts doubling itself, forever. The locks never come off, so the only way out is to take the door off and give it away.**

The "wait, what": the rule we've watched all story (closing a door doubles its locks) turns out to apply to the locks themselves, so the doubling no longer needs anyone. The fix is the rule's own wording, and the last 10 s show that the door is still going, now across the hall.

## The story

- **Premise:** In our apartment building, closing a door doubles its locks, and the locks never come off, so everybody lives with their doors open. I've never closed a door in my life. My big sister Jade slams them. We have one bathroom, we both need it at 7:15, and every morning she gets there first and slams it. The bathroom door doubles from 4 to 1,024 locks as our fight escalates, until it's so thick it leans into the hall.
- **Rule / hook:** "Never close a door in our building. Its locks double." A door that has never been closed has no locks. Every close doubles the count (a new door's first close gives it one). Each lock arrives shut, with its own key and its own little brass keyhole flap.
- **The turn:** the night after the 1,024th lock, one keyhole flap swings shut on its own (the door is so heavy it leans). A flap is a little door, so that lock gets a lock. Then those flaps close. The door doubles by itself, and by three in the morning it fills our hall and is pushing my bedroom door shut.
- **The loophole (the climax turns the rule's own words):** "the locks never come off." The door does. Jade and I pull the three hinge pins, lift the whole clicking pile out of the frame together and carry it down to the curb.
- **The sting and loop:** in the morning the curb is empty. Mr. Dale across the hall, who takes home anything left at the curb, has a new, very thick bathroom door, and through his open front door we can hear it clicking. "So, Mr. Dale, whatever you do," loops into "Never close a door in our building."
- **Where the turn is planted (a rewatch catches both):**
  - Plant 1, L04 (the fridge downstairs): the insert on the fridge's locks shows each one's little brass keyhole flap, and one lock near the top already has a tiny lock of its own growing on it. Not narrated.
  - Plant 2, L17 ("Every lock comes with its own KEY."): close on one new lock on our door, its keyhole flap swinging and settling half shut. Not narrated.
  - Plant for the sting, L10 and L34: Mr. Dale takes home anything left at the curb, and he looks at our 1,024-lock door and says it's a good door.
- **How the last 15 seconds turn over the first line:** the first time, "Never close a door in our building" is a warning to the viewer about how this building works. On the loop it's me pleading with Mr. Dale, who now owns a door that closes itself. The rule never needed a person at all.
- **Ending shape:** a door given away (the problem moves across the hall). Shape tag `runaway`.
- **Warmth:** a sibling truce. Shown: Jade laughing so hard she sits on the door on the stairs, then the next morning she lets me go first, and we knock on the bare frame.
- **Not a sad family reveal.** Nobody is gone, sick, estranged or secretly grieving. The fight is a bathroom fight.

## World

A bright, slightly shabby four-floor city apartment building on a sunny morning street, all made up. Our apartment is on the top floor (four flights up).

- **The building's hall:** a long corridor with mint-green walls (`#8fdcc2`), a warm terracotta tile floor (`#d9774a`) and round ceiling lights. Every front door stands wide open, propped with whatever's handy (a boot, a watering can, a brick), so each apartment's lit living room shows from the hall. Doors carry locks in proportion to their family's fights: Mr. Dale's has none. The brothers' next door has two.
- **Our apartment:** a short inner hallway off the front door, with three doors along it: the bathroom at the end (painted sunny yellow `#f6c844`), my bedroom on the left, Jade's on the right, Mom's room past Jade's. A kitchen at the front with a sink (`kitchen_sink.glb`) and a bowl by the door for keys that becomes a galvanised bucket. Props: `kitchen_fridge.glb`, `bathroom_sink.glb`, `bathroom_bathtub.glb`, `bookshelf.glb`, `couch_medium1.glb`, `carpet_1.glb`, `houseplant_1.glb`, `door_1.glb` as the base for every door (locks built in `set.py`).
- **Downstairs:** the fridge man's kitchen, the same layout one floor down, with a red-and-white picnic cooler on the floor.
- **The stairs:** a square stairwell with a wooden handrail and sunny windows.
- **The street:** a sunny sidewalk and curb outside the building's front steps, a street tree, a parked car. No signs, no numbers on the building, no text anywhere.
- **The locks (our own design, no brands or lettering):** chunky, slightly toy-like. Three kinds, mixed: a brass box lock (`#d9a441`), a chrome barrel bolt (`#c9d1d9`) and a round brass deadbolt rose. Every lock has a small brass keyhole flap on a pivot at its top, which swings. New locks pop on with a short 0.2 s scale-in from the door's surface (no light change). At 512 and up the locks cover the door so no wood shows, and the pile grows outward in lumps, locks on locks.
- **What's true underneath (never said):** in this building closing anything doubles its locks, and a lock's flap counts as a door. Nobody knows why. It never involves the Keepers.

## Cast

All adults or older teens. Nobody young is ever in peril or hurt. Every word is the narrator's.

- `me` (older teen boy, the narrator): short dark-brown block hair with a cowlick, a mustard hoodie with a navy stripe across the chest, grey sweatpants, white sneakers. Faces: `neutral`, `annoyed`, `worried`, `scared`, `smile`. No age on screen.
- `jade` (my big sister, about twenty, named plainly in L12 and on screen in the same beat): a long black block ponytail, a teal sleep T-shirt with a white cloud pattern of our own, pajama pants in navy check, fluffy pink slippers. From L35 a lilac blanket over her shoulders. Faces: `annoyed`, `smug`, `worried`, `sheepish`, `laugh`.
- `mom` (our mom): a short brown block bob, rectangular glasses, a coral cardigan over a white top. Faces: `neutral`, `stern`, `smile`. L23, L27, L28 and L65 to L67 in the background.
- `downstairs` (adult man, the fridge man): a bald block head, a big brown beard, a green bathrobe. L03, L04, L46.
- `brothers` (two adult brothers next door): matching red flannel shirts, one with a beanie. L07 only, arguing on the stairs.
- `pike` (Mrs. Pike upstairs, an older woman): white curly block hair, a purple floral housecoat, a shower cap in L08 and L09. L08, L09, L33.
- `dale` (Mr. Dale, across the hall, an older man): grey block hair, a big grey mustache, a tan cardigan with patched elbows, slippers. His apartment is full of curb finds (a lamp, two mismatched chairs, a wheel). L10, L34, L69 to L72.

## The door (the story's "creature") and its continuity

There's no monster. The thing that grows is the bathroom door. It's one model in `set.py`, posed by its lock count: the same yellow door, the same three-lock kit, the pile instanced in lumps.

| Beat | Lines | Meter | What the door looks like |
|---|---|---|---|
| Frame 1 | L01 | 2 → 4 on "DOUBLE" | yellow door, two locks (a chrome bolt at head height, a brass box lock crooked at knee height). It swings shut and two more pop on. |
| Montage | L02 to L11 | 4 | not shown (the meter holds) |
| Mornings | L12 to L15 | 4 → 8 on "SLAMS it" (L15) | eight locks down the latch side |
| A minute | L16 to L18 | 8 → 16 (L18 cut) | 16, a column of them, one flap swinging (plant 2, L17) |
| Alarms | L19 to L22 | 32 → 64 (L19), 64 → 128 (L22) | locks in rows across half the door |
| Late | L24 | 256 | most of the door, wood only round the edges |
| No wood | L25 to L27 | 512 | no wood shows. The handle is under the locks |
| The shoe | L28 to L29 | 512 → 1,024 on L30 | the shoe wedged at the foot, then gone, the door shut |
| Thick | L31 to L35 | 1,024 | a lumpy bulge 40 cm thick, the top leaning a little out into the hall |
| The flap | L36 to L40 | 1,024 → 1,025 on L40 | one flap near the top swings shut, a tiny lock pops onto that lock |
| By itself | L41 to L44 | 2,048, 4,096, 8,192 as spoken | lumps of locks budding on locks, growing outward |
| The hall | L45 to L54 | 16,384 → 32,768 → 65,536 | fills our inner hall from the bathroom almost to my door, floor to ceiling, a gap near the top where Jade's face shows |
| Off its hinges | L55 to L60 | 65,536 | the pile still on the door: lifted as one lump, the bare frame behind it |
| Stairs, curb | L61 to L64 | 131,072 | carried down, then standing on end at the curb, the size of a parked car |
| Across the hall | L69 to L72 | 262,144 | seen through Mr. Dale's open front door, set in his bathroom doorway |

## The meter (the rule never leaves the screen)

- A padlock icon in lock amber `#ffb21f` with a thick black outline and the count beside it in white Schibsted Grotesk Black, black outline, top centre, about 9% down the frame (above every face and well clear of the caption band). A tiny sunny-yellow door shape sits behind the padlock, so it reads as our bathroom door's count.
- It's on screen from the first frame to the last, including over the montage, where other doors show their own locks in the set.
- Each doubling: the number pops to 1.2x scale and back over 0.25 s, with one soft brass "clack" in the mix. No brightness change, no flash. During L41 to L44 the pops come fast but no faster than 3 a second.
- Numbers use commas (1,024). At the loop it snaps back to 2 with L01's first frame.

## Palette and light

- **Palette:** hall mint `#8fdcc2`, tile terracotta `#d9774a`, bathroom door yellow `#f6c844`, lock brass `#d9a441`, chrome `#c9d1d9`, our walls sky blue `#8cc8f2`, kitchen cabinets white `#f4f1ea`, Jade's teal `#3fb8b0`, my mustard `#e3a62f`, Mom's coral `#f08a6c`, Mr. Dale's tan `#c8a878`, sidewalk `#cfcac0`, sky `#79c3ff`.
- **Caption key colour:** lock amber `#ffb21f`.
- **Light:**
  - L01 to L35: bright morning sun through the windows, every face lit to read. The building's hall lights warm and on.
  - L36 to L54 (the one night scene): our hall lit by a warm amber nightlight in an outlet (`#ffb86b`) and blue moonlight from my bedroom window. Brass locks catch both, so the pile glints. Faces stay readable. The dim comes in across the cut at L36, never a switch in frame.
  - L55 to L60: I switch the hall's ceiling light on across a cut (L55 opens lit).
  - L61 to L72: bright day again (the stairs at dawn warming to sun across L61 to L64, a sunny morning L65 to L72).
  - No flicker, no blackout, nothing red that flashes. Lock pops are scale only.

## Sound and music

- **Music:** C mixolydian, 116 bpm, bouncy and light: a plucky square bass, a marimba-like sine pluck on the off-beats, and a soft tick (a filtered tap on the hi-hat line) whose density follows the meter. Eighths to L15, sixteenths from L19, sixteenths with a doubled tap from L25. No music box or chime.
- **The night (L36 to L54):** the pluck and bass drop out with music drop P01. A low drone on C and G enters at L41 and holds through L54. The ticks become the clicks: synthesized soft brass clacks, sparse then dense (never a buzz), kept low and under 4 kHz.
- **The loophole (L56):** the bouncy bass comes back on "But the DOOR / DOES." with the drone still under it. A plain warm lead melody in C major enters at L63 (Jade laughing) and runs to L67.
- **The sting (L68 to L72):** the lead drops out, the drone and a slow tick remain, and the clicks come faintly from across the hall.
- **Drops (`music_drops`):** P01 (0.6 s, before L36): everything but the voice drops, then one tiny brass click hit. P02 (0.6 s, before L68): everything drops, then one soft low thud.
- **Sound hit on L01's last word:** a heavy bolt "clunk" doubled (two clunks 0.12 s apart) as the door shuts on "DOUBLE".
- **Ambience:** apartment room tone, a far-off street, the brothers' muffled argument at L07, Mrs. Pike singing (a hummed synth vowel, no words) at L08 and L09, the key bucket's rattle at L45, the ceiling light's creak at L46, footsteps on stairs (soft recorded steps from `assets/audio/`).
- **The loop:** 0.25 s after "DO,", cut to L01's first frame.

## The opening recipe (playbook v1), point by point

1. **Line 1 is a warning to "you":** "Never close a DOOR / in our BUILDING. / Its locks DOUBLE." 10 words, about 2.1 s.
2. **Frame 1 looks straight at the warned-of thing, already slightly wrong:** a tight close on our yellow bathroom door with two locks, one of them crooked at knee height where no lock goes. Lit bright, centred, pushing in. No wide, no establishing shot in the first 3 s.
3. **A sound hit on the last word:** the door swings shut and the doubled bolt clunk lands on "DOUBLE", two more locks popping on as the meter goes 2 → 4.
4. **Line 2 tightens it in at most 1.5 s:** "And they NEVER / come OFF." 5 words, about 1.0 s. No names, places or backstory before 4 s (the first name, Mrs. Pike, is at about 14 s).
5. **Lines 3 to 5 show the rule at work, one shot each, none over 2 s:** the sneeze and the fridge swinging shut (L03), the 64-lock fridge and the cooler (L04, two shots), every front door open (L05).
6. **The title is a concrete, countable thing:** "Every Slam DOUBLES The Locks 🔒", 5 words, a statement, never a question.
7. **Measure:** chose to view in Studio, against the recipe's 75% bar.

## The hits' shape

- **The rule in the first line,** visible by frame 1 (the locks on the door and the meter).
- **The montage (L03 to L10, about 3 to 20 s), five examples:** the sneeze fridge with 64 locks and the milk in a cooler, every front door open, the hall smelling like six dinners, the brothers who only argue on the stairs where there's nothing to slam, Mrs. Pike who hasn't shut her bathroom in twelve years and just sings louder, and Mr. Dale who takes home anything left at the curb.
- **The narrator is the exception:** I've never closed a door in my life (L11).
- **The relatable fight:** one bathroom, two of us, 7:15. The alarm war (L20 to L22) and Mom's rule (L23).
- **15 to 30 s show, never explain:** the morning fights, the slam, the meter climbing.
- **The loved one at stake:** my big sister Jade, and the fight between us.
- **The first real scare (about 65 s, 51%):** the first flap swinging shut on its own at night. Later than the creepy-lane norm on purpose: the what-if lane's first half is the funny escalation, and the turn is the doubling's own logic.
- **The climax turns the rule's own words:** the locks never come off, but the door does.
- **The loop:** L72 runs into L01 as one sentence.

## Quotable line (marked)

**L56: "The locks NEVER come OFF. But the DOOR DOES."** Short, flat and typable, and it's the loophole. (The montage's L09, "She just SINGS LOUDER.", is the funny backup.)

## Comment pin

"Comment SLAM if someone in your house slams every door." One easy word tied to the story, a family engine (playbook item 6 and 9).

## The lore connection (one only)

Three brass-coloured tally strokes scratched into the top hinge plate of the bathroom door frame, three for an apartment built for three (Mom, Jade and me). Plain tally, no extra stroke, no Keeper, no thread touched. Seen in L57's second shot: as the top hinge pin comes out, a close on the bare hinge plate on the frame, the strokes beside the screw holes. Held 1.6 s. Not narrated. The building's rule is simply how that building is and never involves the Keepers.

## Format

Each line gives the id and who says it, then the caption chunks split with ` / `. The spoken text is the chunks in lowercase without quote marks. CAPS are the key words, in `#ffb21f`. Shots under each line. A cut or punch-in every 1 to 2 s, no still over 2 s. Every line over 2 s has two shots.

## 01 The rule (L01 to L10, about 0 to 20 s)

- **Where:** our bathroom door, the downstairs kitchen, the building's hall, the stairwell, upstairs.
- **Shots:** 14.

- `L01` narrator: Never close a DOOR / in our BUILDING. / Its locks DOUBLE.
  - [tight close, centred: our yellow bathroom door, bright morning, two locks (a chrome bolt at head height, a brass box lock crooked at knee height). Push in through the line. On "DOUBLE" the door swings the last few centimetres shut by itself (pushed from inside, nobody seen) and two new locks pop on. The doubled clunk. Meter 2 → 4]
- `L02` narrator: And they NEVER / come OFF.
  - [punch in to the new box lock, its brass flap swinging. A short shove on the door from inside shakes it, and every lock holds fast]
- `L03` narrator: The guy DOWNSTAIRS / SNEEZED / by his FRIDGE.
  - [the downstairs man in his green bathrobe, `neutral`, mid sneeze beside his open fridge. The fridge door swings shut]
- `L04` narrator: Now it has / SIXTY-FOUR LOCKS, / so he keeps the MILK / in a COOLER.
  - [two shots: the fridge door covered in 64 locks, the man `sheepish` beside it. Then an insert on the fridge's locks (plant 1: the little keyhole flaps, and one lock near the top with a tiny lock growing on it), tilting down to the picnic cooler on the floor with a milk jug in it]
- `L05` narrator: Every FRONT DOOR / on our floor / stands OPEN.
  - [the building hall, a quick dolly down it: every front door wide open, propped with a boot, a watering can, a brick]
- `L06` narrator: The HALL / smells like / SIX DINNERS.
  - [through two open doors, two families at two tables eating, lit living rooms, steam off the plates]
- `L07` narrator: The BROTHERS next door / only ARGUE / on the STAIRS, / where there's nothing / to SLAM.
  - [two shots: the two brothers in red flannel nose to nose on the stairwell landing, `annoyed`. Then a low angle up the open stairwell: no door anywhere in it]
- `L08` narrator: Mrs. PIKE upstairs / hasn't shut her BATHROOM / in TWELVE YEARS.
  - [two shots: up the stairwell, Mrs. Pike's front door open. Then her bathroom doorway, open, a frosted shower curtain with her shower-capped head above it, `neutral`, singing. Nothing below the shoulders seen]
- `L09` narrator: She just / SINGS LOUDER.
  - [punch in on Mrs. Pike, `smile`, mouth wide on a long note]
- `L10` narrator: And MR. DALE / across the hall / takes home ANYTHING / left at the CURB.
  - [two shots: Mr. Dale in his tan cardigan in his open doorway across the hall from ours, `smile`, his place full of mismatched curb finds. Then the street: him carrying a curb lamp up the front steps]

## 02 Me and Jade (L11 to L15, about 20 to 30 s)

- **Where:** our apartment's inner hall, morning.
- **Shots:** 7.

- `L11` narrator: ME? / I've never closed a door / in my LIFE.
  - [me in my mustard hoodie in my bedroom doorway, `smile`, my door wide open behind me, not a single lock on it]
- `L12` narrator: But my big sister, JADE, / SLAMS them.
  - [Jade in her teal cloud T-shirt and pink slippers, `annoyed`, stepping past me toward the bathroom. Her own bedroom door behind her has 16 locks]
- `L13` narrator: We have ONE BATHROOM, / and we both need it / at SEVEN FIFTEEN.
  - [two shots: a wall clock in the kitchen at 7:15 (hands only, no numbers on its face). Then the two of us side by side in the inner hall, facing the bathroom door, `annoyed`]
- `L14` narrator: So every MORNING, / we FIGHT / for it.
  - [quick: the two of us shoulder to shoulder racing down the inner hall]
- `L15` narrator: And every morning, / she gets there FIRST / and SLAMS it.
  - [two shots: Jade inside the doorway, `smug`, the door swinging. Then the door shut in my face: four new locks pop on. Meter 4 → 8]

## 03 Doubling (L16 to L35, about 30 to 65 s)

- **Where:** our apartment, a run of mornings, bright.
- **Shots:** 26.

- `L16` narrator: At EIGHT locks, / it takes a MINUTE / to get IN.
  - [two shots: me at the door, `annoyed`, working a key into a lock. Then the eight locks, half open]
- `L17` narrator: Every lock comes / with its own KEY.
  - [close on one new brass lock on our door, its key in it and its keyhole flap swinging and settling half shut (plant 2)]
- `L18` narrator: Our key BOWL / is a key BUCKET.
  - [the galvanised bucket by our front door, heaped with brass keys. Meter 8 → 16 on the cut]
- `L19` narrator: At SIXTY-FOUR, / it takes TEN MINUTES.
  - [the door with rows of locks, me sitting on the hall floor with the bucket, `neutral`. Meter 16 → 32 → 64 in two pops]
- `L20` narrator: So Jade sets her alarm / for SIX, / to BEAT me.
  - [two shots: Jade in bed, `smug`, a phone glowing on her pillow (blank screen, no text). Then dawn light at her window]
- `L21` narrator: I set mine / for FIVE-THIRTY.
  - [me in bed in the dark blue before dawn, `worried`, phone glowing]
- `L22` narrator: She sets hers / for FIVE.
  - [Jade already at the bathroom door in the half dark, `smug`. The slam. Meter 64 → 128]
- `L23` narrator: Mom says the next one / who SLAMS it / sleeps in the HALL.
  - [two shots: Mom in her coral cardigan in the kitchen, `stern`, pointing at the inner hall. Then Jade and me at the table, both `sheepish`]
- `L24` narrator: At TWO FIFTY-SIX, / Jade's late for WORK, / and I'm late for PRACTICE.
  - [two shots: Jade running out the front door with her bag. Then me running down the stairs with a sports bag. Meter 128 → 256]
- `L25` narrator: At FIVE HUNDRED / and TWELVE, / there's no WOOD / left to SEE.
  - [two shots: the bathroom door, covered edge to edge, no yellow showing. Then a close slide across the locks. Meter 256 → 512]
- `L26` narrator: It takes an HOUR / to get IN.
  - [me, `annoyed`, on a stool at the door with the key bucket, the kitchen clock's hands a whole hour round in an insert]
- `L27` narrator: Mom brushes her TEETH / in the KITCHEN SINK.
  - [Mom at the kitchen sink, toothbrush, `neutral`, toothpaste foam]
- `L28` narrator: Then one morning, / she wedges it OPEN / with her SHOE.
  - [two shots: the bathroom door ajar, Mom's flat shoe wedged at its foot. Then Mom, `smile`, dusting off her hands]
- `L29` narrator: Jade KICKS / the shoe.
  - [low close: a pink slipper flicks the shoe away across the tile]
- `L30` narrator: ONE THOUSAND / TWENTY-FOUR.
  - [the door slams. A wave of locks pops on in a ripple. Meter 512 → 1,024]
- `L31` narrator: The door's so THICK now, / it LEANS out / into the HALL.
  - [two shots: side-on down the inner hall, the door a lumpy brass bulge 40 cm thick, its top tilted out. Then Jade beside it, `sheepish`, the meter above her (cover frame)]
- `L32` narrator: The whole FLOOR / comes to LOOK at it.
  - [wide-ish from our front door: neighbours crowding into our inner hall, the brothers, the downstairs man, Mrs. Pike in her shower cap]
- `L33` narrator: Mrs. Pike says / it's the WORST one / she's ever SEEN.
  - [Mrs. Pike, `neutral`, peering over her glasses at the door]
- `L34` narrator: Mr. Dale says / it's a GOOD door.
  - [Mr. Dale, `smile`, a hand flat on the locks as if testing a melon]
- `L35` narrator: And Jade sleeps / in the HALL.
  - [Jade on a camping mat in the inner hall by her doorway, lilac blanket, `annoyed`, Mom's door open behind her. Bright evening light]

## 04 By itself (L36 to L54, about 65 to 96 s)

- **Where:** our inner hall at night, nightlight and moonlight. The one dim scene, faces still lit.
- **Shots:** 24.
- **Drop P01 before L36.**

- `L36` narrator: That NIGHT, / I hear a tiny / CLICK.
  - [two shots: me in bed, eyes open, `worried`, moonlight. Then my open doorway, the hall beyond in nightlight amber]
- `L37` narrator: Every lock has a little FLAP / over its KEYHOLE.
  - [close on one brass lock high on the pile, its keyhole flap catching the amber light]
- `L38` narrator: A little DOOR.
  - [punch in on the flap]
- `L39` narrator: And one of them / just SWUNG SHUT.
  - [the flap swings closed with a tiny click]
- `L40` narrator: Now THAT lock / has a LOCK.
  - [a tiny lock pops onto that lock. Meter 1,024 → 1,025]
- `L41` narrator: CLICK. / Click click. / Click click click click.
  - [three quick shots, one per chunk: one flap shutting, two flaps, four flaps, each followed by new locks budding. The drone enters]
- `L42` narrator: NOBODY'S / touching it.
  - [wide on the inner hall: the pile, Jade asleep on her mat at the far side, me in my doorway, nobody near it]
- `L43` narrator: It's DOUBLING / by ITSELF.
  - [the lump of locks bulging outward. Meter climbing in pops]
- `L44` narrator: TWO THOUSAND. / FOUR THOUSAND. / EIGHT.
  - [three quick shots matched to the numbers: the pile swelling, a side close of locks on locks, my face `scared`. Meter 2,048, 4,096, 8,192]
- `L45` narrator: In the KITCHEN, / the key BUCKET / RATTLES / and FILLS.
  - [two shots: the bucket in moonlight, keys rising over its rim. Then a few keys sliding off the heap onto the floor]
- `L46` narrator: Downstairs, / the guy's CEILING LIGHT / starts to SWING.
  - [the downstairs kitchen at night, the round ceiling light swaying gently on its cord, the man in his doorway in his bathrobe, `worried`, looking up]
- `L47` narrator: By THREE / in the MORNING, / it fills the HALL / up to MY door.
  - [two shots: the inner hall filled floor to ceiling with glinting locks, a lumpy wall of brass. Then my doorway, the pile right at the frame. Meter 16,384 → 32,768]
- `L48` narrator: And it's PUSHING / my door SHUT.
  - [my bedroom door, wide open against the wall, being nudged by the pile, starting to swing]
- `L49` narrator: If my door SHUTS, / it starts doing it TOO.
  - [close on my lockless door's bare face, the pile's edge pressing it]
- `L50` narrator: I hold it OPEN / with my FOOT.
  - [low close: my white sneaker against the bottom of my door, holding it]
- `L51` narrator: Jade's on the other side / of the PILE, / in her BLANKET.
  - [two shots: a gap near the top of the pile, Jade's face in it, lilac blanket over her head, `worried`, lit by the nightlight. Then me, `worried`, looking back. Meter 65,536]
- `L52` narrator: Through the GAPS, / she says she's SORRY.
  - [Jade in the gap, `sheepish`]
- `L53` narrator: She says / I always BANG on it / till she RUSHES.
  - [a quick insert: me pounding the bathroom door on an earlier morning, `annoyed`, the lit day colours. Then back to Jade in the gap]
- `L54` narrator: I tell her / I'm sorry TOO.
  - [me, `sheepish`, foot still on the door]

## 05 The loophole (L55 to L64, about 96 to 113 s)

- **Where:** our inner hall, the ceiling light on, then the stairs at dawn and the street.
- **Shots:** 15.

- `L55` narrator: Then I look / at the HINGES.
  - [the hall lit by its ceiling light now (across the cut). Close on the bathroom door's hinge side, three steel hinges along the frame, the only bare metal not under locks]
- `L56` narrator: The locks NEVER / come OFF. / But the DOOR / DOES.
  - [two shots: me, `smile`, an idea. Then Jade's face in the gap, `smile` back. The bouncy bass comes back on "DOES"]
- `L57` narrator: Three HINGE PINS. / Jade does the TOP, / I do the BOTTOM.
  - [two shots: Jade reaching up at the top hinge from her side (cut away before her hand meets the pin). Then a close on the bare top hinge plate, its pin gone, three tally strokes scratched beside the screw holes, held 1.6 s (lore plant)]
- `L58` narrator: We meet / in the MIDDLE.
  - [a hinge pin dropping onto the tile with a ring, then a second]
- `L59` narrator: It's a TWO-PERSON door.
  - [the two of us either side of the pile, `neutral`, braced]
- `L60` narrator: We lift it / out of the FRAME, / still CLICKING / in our ARMS.
  - [two shots: the whole pile tipping free of the frame, the bare yellow-painted frame behind. Then the two of us under it, the pile on our shoulders, faces visible either side]
- `L61` narrator: Down FOUR FLIGHTS / of STAIRS.
  - [high angle down the stairwell at dawn, the glinting pile going down between us. Meter 131,072]
- `L62` narrator: Every STEP down, / it CLICKS / a little LOUDER.
  - [low on the stairs, locks budding on the pile as it bumps a step]
- `L63` narrator: Jade's LAUGHING / so hard / she has to SIT on it.
  - [two shots: Jade, `laugh`, sitting on the pile on a landing. Then me, `laugh`, leaning on the rail. Warm lead melody enters]
- `L64` narrator: We stand it / at the CURB, / and BACK away / SLOWLY.
  - [two shots: the pile on end at the sunny curb, the size of a parked car. Then the two of us walking backward up the front steps, `smile`]

## 06 The next morning (L65 to L72, about 113 to 128 s)

- **Where:** our apartment and the building's hall, sunny morning.
- **Shots:** 11.
- **Drop P02 before L68.**

- `L65` narrator: Now our bathroom / has a SHOWER CURTAIN / for a door.
  - [two shots: the bare bathroom frame with a bright striped shower curtain hung across it on a tension rod. Then Mom, `smile`, straightening it]
- `L66` narrator: We KNOCK / on the FRAME.
  - [close: my knuckles at the wooden frame beside the curtain (cut before contact, the knock heard)]
- `L67` narrator: The next MORNING, / Jade lets me / go FIRST.
  - [two shots: the kitchen clock at 7:15. Then Jade in the inner hall, `smile`, waving me past toward the curtain]
- `L68` narrator: And the CURB / is EMPTY.
  - [from our front window, the sunny curb, nothing on it]
- `L69` narrator: Across the HALL, / Mr. Dale has / a NEW / BATHROOM DOOR.
  - [two shots: from our open front door, across the building hall, through Mr. Dale's open front door: the pile set in his bathroom doorway at the end of his hall. Then Mr. Dale, `smile`, admiring it]
- `L70` narrator: It's VERY / THICK.
  - [punch in on the pile in his doorway, glinting]
- `L71` narrator: And through his open DOOR, / we can hear it / CLICKING.
  - [two shots: Jade and me in our doorway, `worried`, side by side. Then a close on one of its flaps swinging shut. Meter 262,144]
- `L72` narrator: So, Mr. DALE, / whatever you DO,
  - [me looking straight down the lens, `worried`, then 0.25 s after "DO," cut to L01's first frame: our yellow door, two locks, meter back to 2]

## Risks

- **"locked", "trapped", "took", "pulled":** all in `checks.HARM`, and none is in the narration. The rule's word is always "lock" or "locks" (nouns), never the past tense. Keep it that way in any revision.
- **Peril:** the pile pushing my door (L48 to L50) is comic tension, never shown as danger. Nobody is shut in anywhere, the pile never touches a person's body, and Jade is in her own doorway, not under it. If a reviewer reads it as peril, cut L49 and keep L48 and L50.
- **The meter's numbers:** the spoken counts (4, 8, 64, 256, 512, 1,024, 2,048, 4,096, 8,192) must match the meter on the same beat. The 1,025 at L40 is on purpose (one new lock on a lock).
- **"Mr. Dale":** Whisper may hear "Mr. Day" or "Mr. Gale". If `asr` flags it, respell for the voice only ("Mister Dayl"), captions unchanged.
- **Mrs. Pike in the shower (L08, L09):** head and shower cap above an opaque curtain only. Keep it clearly comic and never below the shoulders.
- **The lifted pile:** keep it a solid lump on the door, about car-sized at the curb, not bigger than the stairwell allows. A cheat of scale on the stairs is fine, cut tightly.
- **Unit-seven (ep34) also uses doors and locks.** Its rule is what makes a door open (something of yours inside), and this one is what closing does. Different rule, set, twist and warmth.
- **Light:** the night comes in across a cut, and the hall light at L55 is on across a cut. No step change in frame. Pre-check the flash bar on the meter pops in L41 to L44 (scale only, no brightness).
