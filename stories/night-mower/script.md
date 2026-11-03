# night-mower: the script (writer, 2026-11-03, batch 6 slot P3)

- **Slug:** `night-mower` (no ep number yet: parallel sessions are numbering at once, and the lead numbers it at queue time).
- **From:** batch 6 brief `docs/research/2026-11-03-week.md`, slot P3 (T8, premise bank P07). Lane: creepy town rule, `"lane": "core"`. Length arm: MID, 60 to 90 s.
- **Title:** He Mows With His Eyes SHUT 🌿 (improved from the working "He Only Mows At 3 AM 🌿": no number, per playbook item 5, and the concrete thing that doesn't add up is the face in frame 1. Starts with "He", this slot's own word.)
- **Word count:** 325 spoken words in 46 lines, all `narrator`, plus two music drops (1.2 s in all).
- **Estimated length:** 325 words at 290 wpm is 67 s of speech. With 0.12 s gaps (5.5 s), the drops (1.2 s) and the loop tail (0.25 s), about 74 s. If it lands under 65 s, add "Dad says / it's the SPRINKLER." after L21. If over 85 s, cut L30 and L42 first.
- **Look:** `look.style: "closer"`, `look.flash_safe: true`, and `look.polish: true` once the polish pack is on main (it isn't at the time of writing: `grep -rn polish blocky/` is empty. The builder greps again before the build and the final). `look.hdri: "moonless_golf"` (most of the film is the 3 AM lawn), strength about 0.6, hidden.

## The big idea (one sentence)
Our whole street is built on top of a giant sleeping head: the neighbor's perfect lawn is its eyebrow, Dad's bald spot is its receding hairline, and when the eyebrow gets trimmed it wakes and turns toward whoever is watching.

- **The "wait, what":** Dad has spent ten years losing a lawn war to an eyebrow. You can't out-grow a hairline.
- **How it reframes line 1:** "Never look" sounds like superstition. It's physics and manners: nobody likes being watched at the barber's, and this one turns its head to see you, which tips every house on top of it toward you. The leaning house across the street, the blinds that snap shut, the neighbor's shut eyes and our crooked pictures were all the head turning.
- **How it reframes the rivalry:** the neighbor never cheated. He's the head's barber, alone, at 3 AM, eyes shut. Our round bald patch was never Dad's failure.
- **Pitched and dropped (10 for 1):** the mower cuts away the night so dawn can come (no stakes). The grass is people who looked (peril, sad). The stripes are a landing strip for something above (no family). Grass grows wherever people look, so Dad's envy grows it (too abstract to picture). Dad sleepwalks and mows it himself (ep41 already did sleepwalking). The lawn is the back of a sleeping animal (weaker than a head, no bald joke). The mower mows time, a stripe a day (ep33's time-price lane). The neighbor is mowing the shape of our house to keep a count (stand-in). The lawn is a mirror of our yard (ep15's reflection lane). Kept: the head.
- **Checked against Claimed big ideas and every story.json twist:** no story builds the town on a creature, nobody's rule is about being watched while asleep, it isn't forgotten or unseen, and it isn't a stand-in. Ep13 used modelled realistic eyes in rows: ours is one flat drawn eye, our own face style, at giant size.

## The story
- **Premise:** Our neighbor, Mr. Odell, has the most perfect lawn on the street, and his mower only runs at 3 AM. Everyone obeys one rule: never look at his lawn while his mower's running. My dad has hated that lawn for ten years, because ours has one perfectly round bald spot that nothing will grow in. Dad decides Mr. Odell is cheating, and sets an alarm to catch him.
- **Rule:** "Never look at the neighbor's lawn while his mower's running." Whoever looks, their house leans toward his lawn.
- **Twist:** The street is built on a giant head lying face up under it. His lawn is its eyebrow, our yard is where it's going bald, and when he trims the brow it wakes and turns toward whoever's watching. Mr. Odell mows with his eyes shut so it never turns toward him.
- **Where it's planted:**
  - Plant 1, L08 to L09 (about 12 to 14 s): our bald spot is "perfectly ROUND", a top-down shot of a clean circle of bare tan ground in green grass, at the hairline side of our yard. A rewatch sees a bald patch.
  - Plant 2, L17 (about 25 s): his lawn is "COMBED / in long, CURVED stripes", every stripe arcing the same way round one low oval hump, like hair brushed over a brow. A rewatch sees an eyebrow.
  - Plant 3, L03 to L04 and L19 to L20: the house across the street leans toward his lawn, and our pictures slide crooked toward it. A rewatch sees a head turning.
  - Plant 4, L01 and L06: he mows with his eyes shut, and says it's faster that way. On a rewatch it's the one way to work there without being looked at back.
- **How the last 15 seconds turn over line 1:** the first time, line 1 is a spooky neighborhood superstition and Dad is the hero breaking it. By L38 we know it's a head that turns to whoever watches. From L39, Dad shuts his eyes, the street settles, and he crosses the fence for the first time in ten years. The last line ("So if you're ever on our street at three,") runs straight into line 1, which now reads as advice from someone who knows. The very last shot is the seam opening a crack and the eye looking into the lens, at the viewer, who has been watching the whole time.
- **Ending shape:** a loop with a look to camera. Warm turn first (two rivals mowing together, eyes shut), then the cold beat: the eye opens on us.
- **Warmth:** neighbors. Two men who fought over a fence for ten years end up a two-man crew. Shown, not told: Dad crossing the low fence, then Dad holding the cord while Mr. Odell steers, both eyes shut. Not a sad family reveal: nobody in the family is gone, ill or estranged.

## The rule and the hits' shape (RULES → What the hits do, the reset, the opening recipe)
- **Line 1 (confess opening, batch lead 2026-11-03, `docs/research/opening-variety.md`):** "My neighbor mows his lawn at three a.m. with his eyes shut." 12 words, about 2.24 s. A concrete mystery about one odd adult.
- **Frame 1:** straight at the warned-of thing, already wrong: a close, low, floodlit shot of the neighbor's bright green lawn with Mr. Odell pushing his mower straight at camera, **his eyes shut**, face at least 1/5 of frame width, centred. Push in through the line. No wide or establishing shot until L12 (about 17 s).
- **Sound hit:** on "SHUT" (about 2.1 s): a soft low thud (`assets/audio/sfx/thud`, low-passed) and the mower's synthesized hum swelling in on D under it.
- **Line 2:** "Don't look while it's running." The rule as a warning to "you", about 1.0 s. No names, places or backstory before L07 (about 10 s). Mr. Odell is first named at L12 (about 17 s).
- **Lines 3 to 5:** the rule at work, one shot each, every one under 2 s: the leaning house, its lean, the blinds snapping shut. L06 adds the fourth example (his own reason).
- **The rule meter (on screen the whole time):** a small spirit-level badge, top left, outside the caption band: a rounded lime-green glass vial (`#b6ff3b`) with three short black tick lines and one white bubble, our own design, no text. It shows how far **our** house is turned toward his lawn. Its in-world twin is Dad's yellow spirit level (L22). Bubble per beat: centred L01 to L17. Slides one tick right (toward his lawn) at L18 to L20. Holds. Two ticks at L24. Jammed against the right end at L31. Slides back to centre over 1 s at L40. And twitches a hair right on the very last shot (the eye looks at the lens). It moves on eased curves only, never snaps. If the engine has no overlay for this, the builder adds it as an opt-in in `post.py` (defaults unchanged) rather than dropping it.
- **Montage (L03 to L06, 3 to 10 s):** four examples: the house across the street leans. Every blind snaps shut at three. The neighbor mows eyes shut. By L08, our bald spot.
- **The narrator's family is the exception:** our house is the one that looks, because Dad won't obey.
- **The loved one at stake:** my dad. The eye looks straight at him, and our whole house tips toward it.
- **15 to 30 s:** shows and escalates, nobody explains: the alarm, the mower starting, the bent slat, the combed lawn, the creak, the crooked pictures. Dad's "the foundation" is a joke, not an explanation.
- **First real scare:** L24 (about 35 s, 47%): my desk chair rolls to the window by itself.
- **Creature shown clearly:** L27 to L31 (about 40 to 48 s, 54 to 65%), lit to read.
- **The loophole the climax turns:** the rule's own logic. It turns toward whoever's watching, so stop watching: Dad shuts his eyes and the pictures slide back straight. Mr. Odell had the answer in frame 1. No new magic.
- **Twist said plainly:** L34 to L38, four short lines, one picture (the eye in his lawn with our bald patch beyond the fence in the same frame).

## Quotable line (marked)
- **L06: "He says it's FASTER that way."** Odd, flat, six words, typeable, right after the title's detail. (Backup laughs, not marked: L37 "Ours is where it's going BALD." and L45 "Dad still WATERS / the bald spot. / Out of RESPECT.")

## World
A bright suburban cul-de-sac (props `sub_building_type_a`, `_c`, `_f`, `_k`, `_p`), one place: our upstairs window, our yard, the low fence, and Mr. Odell's lawn next door, plus the house across the street.
- **Our house** (`sub_building_type_a`, tinted butter yellow `#ffd970`): my upstairs bedroom window (`window_large1`, `curtains_double`) with white plastic blinds built as boxes, a desk (`light_desk`, `chair_1` on casters), `bed_single`. A hallway with three framed pictures (flat colour blocks, no faces or text). Our front yard: `kit.texture("grass")` tinted mid green `#6cc24a`, with a perfectly round bald circle (about 2.4 m across) of bare tan soil `#c49a5c` near the fence. A porch (`kit.texture("wood")`). Dad's hose reel and sprinkler.
- **Mr. Odell's house** (`sub_building_type_c`, mint `#8fe3c8`): the lawn is `kit.texture("grass", tint="#2fe05a")`, the most saturated thing in the film, mowed in long curved stripes (alternating light and dark bands built as thin tinted boxes or a stripe texture), all bowing round one long low oval hump (the brow ridge, 0.3 m high). Four floodlight poles at the corners (built, warm `#fff1c2`, static, no flicker) light it like a little stadium at night. Flower beds (`flowers`, `bush_1`, `bush_2`), `sub_planter` on his porch, `sub_path_stones_long`.
- **Between them:** a low white fence (`sub_fence_low`, tint `#f4f1e8`), knee height, that Dad steps over at L41.
- **Across the street** (`sub_building_type_f`, coral `#ff8f7a`): rotated about 6 degrees on its base so it leans toward Mr. Odell's lawn, its porch light hanging at the same slant. Its windows' blinds are shut.
- **The street:** `kit.texture("asphalt")`, `kit.texture("concrete")` sidewalks and driveways (`sub_driveway_long`), plain box mailboxes on posts (no lettering, no numbers), `trashcan_cylindric` at the curbs, `sub_tree_small`, `sub_tree_large`.
- **No text anywhere.** No house numbers, no street sign, no lettering on the mower or mailboxes. Dad's bedside clock shows digits only ("3:00").
- **The mower** (built in `set.py`, one model): a chunky boxy push mower, bright red `#ff3b30` deck, black wheels, a long chrome handle, an orange extension cord `#ff9a1f` trailing back to his porch. No brand, no decal. It hums (synthesized), it doesn't roar.
- **What's true underneath (never said beyond L34 to L38):** the street is laid over a giant head lying face up, far older than the street. Mr. Odell's lawn is its right eyebrow, our yard the hairline above it, going bald. The trim wakes it a little every night. Whatever it sees watching, it turns toward, and the houses on top tip with it.

## Cast
All adults except me, a teen boy. Nobody young is ever in peril or hurt.
- `me` (teen boy, the narrator): short dark-brown block hair, a teal hoodie `#1fb5a8`, gray sweatpants, white socks. Faces: `neutral`, `worried`, `scared`, `smile`. On screen at my window and desk. No age on screen.
- `dad` (adult, "my dad", named plainly at L07): short sandy block hair, a sandy block mustache, a red-and-white checked short-sleeve shirt (our own pattern), khaki shorts, white sneakers, a green garden cap by day. At night a navy robe over the shirt. Faces: `neutral`, `angry` (glaring, comic), `worried`, `scared`, `smile`, `eyes_shut` (two thick curved down strokes, as Mr. Odell's).
- `odell` (older adult, "our neighbor, Mr. Odell", named plainly at L12): white block hair combed flat, big white block eyebrows, a forest-green cardigan `#2f6b3a` over a white shirt, brown slacks, brown slippers. Faces: `eyes_shut` (default at night: two thick curved strokes, a calm small smile), `smile` (by day, eyes open, waving). He never opens his eyes at night.
- No other cast. The family across the street is never seen, only their leaning house and shut blinds.

Every word is the narrator's. Mr. Odell's one quote (L33) is inside the narration.

## The creature: the Head
- **Look:** a person's head, built from the same plastic as ours, but far too big: a soft rounded-cylinder head the size of the street, lying face up under it. Only its right eye area is ever seen. The eyelid is a long lens-shaped flap of turf (the striped lawn on top, warm pale plastic `#f2d9a6` on its underside and edge) that rises along the hump. Under it, one eye drawn the way our faces are drawn, flat, with thick black strokes: a huge rounded-square black pupil `#0b0b0f` about 2.5 m across (the size of our garage door), on a flat off-white `#f6f3ea`, with one small warm-white highlight `#fff6dc` (the brightest thing in its frames), ringed by a thick black lid stroke. The lawn's stripes are its brow hair. It's wrong in one dimension only: size.
- **Never seen moving, only closer, apart from two slow ramps:** the lid lifting over 1.5 s (L27), and the pupil's highlight shifting to aim at Dad across a cut (L28 to L29). It never rises out of the ground, never chases, never touches anyone.
- **Light it for fear, and to read:** the floodlights are its key from the sides and above (warm), a cool moon rim `#a9c4ff` along the lid edge, the pupil highlight brightest. No clipped white on the lawn.
- **One model**, built once in `set.py`, posed per shot. **Test still first:** render the L28 phone-size still (the eye looking up past the open lid, Mr. Odell's mower in foreground, eyes shut) before anything else, and iterate until it reads as an eye at a glance and is eerie, not silly.

### Continuity: where the Head is in each beat
| Beat | Lines | What shows |
|---|---|---|
| 01 Rule | L01 to L06 | only the lawn's curved stripes over the low hump. The lid shut and flat with the lawn |
| 02 Dad | L07 to L14 | daylight: the hump is a gentle rise in his lawn. Our bald circle |
| 03 Night one | L15 to L22 | the stripes curving round the hump (L17). Nothing opens |
| 04 Night two | L23 to L25 | the hump, a faint shadow line along it at L25 |
| 05 The eye | L26 to L31 | the seam lifts (L26 to L27), the eye looks up (L28), aims at Dad (L29 to L30), the street tips (L31) |
| 06 Said plainly | L32 to L38 | eye open, still, under the floodlights. L34 high shot shows the eye in his lawn with our bald circle beyond the fence |
| 07 Neighbors | L39 to L45 | the lid sinks shut over 1 s at L40. Shut and flat after |
| Last shot | L46 | the seam opens a crack, the eye looks into the lens |

### Continuity: Dad and Mr. Odell
- Dad: day (L07 to L13) in the garden cap, in our yard. Night one (L14 to L22) in the robe at my window, upstairs. Night two (L23 to L40) on our porch with binoculars (black boxes, built). L41 steps over the fence, cap off. L43 to L45 on Mr. Odell's lawn holding the orange cord, eyes shut.
- Mr. Odell: always on his lawn at night, behind the mower, eyes shut. By day (L12) on his porch, waving, eyes open.

## Palette and light
- **Day (L07 to L13):** bright and saturated, game-style sky `#7ec8ff`, sun key, butter-yellow, mint and coral houses, his lawn `#2fe05a`, ours `#6cc24a`, the bald circle `#c49a5c`.
- **Night (everything else):** a saturated deep blue sky `#1b2a6b` (never black), moonlight fill `#a9c4ff`, his lawn blazing green under warm floodlights `#fff1c2`, my window's desk lamp orange `#ffb45e`. Our yard reads in blue moonlight. Fog only light and only at the street's far end.
- **Caption key colour:** `#b6ff3b` (lime, the meter's colour).
- **Flash safety:** the floodlights are static. The lid lift, the tips, the pictures sliding and the meter all ease over 0.6 s or more. No light switches on or off.

## Sound and music
- **Music:** D mixolydian, 100 bpm. Light and bouncy for the montage and the day beats: a plucky square bass on the root and fifth, a soft marimba-like sine pluck with the flat seventh (C natural) for the funny suburban odd. No music box, no chime.
- **The drone:** the mower's hum is the score's drone, a low synthesized motor tone on D (two detuned saws low-passed under 800 Hz with a slow wobble). It enters on L01's hit, sits quietly under the day beats as a memory (off in L07 to L13), returns at L15 ("The mower STARTED") and holds. A heavier low D and A drone joins at L27 and holds to the end. At L32 ("mower STOPPED") the hum stops dead and only the heavy drone remains. At L43 the hum returns, softer, under a plain warm melody in D major on a soft square lead to L45. At L46 the lead drops out.
- **Drops (`music_drops`):** P01 0.7 s before L26: everything but the voice drops, then one soft wet turf creak as "TURF" lands. P02 before 'is built' (L34.1): everything drops, one low soft thud on "HEAD".
- **Hits:** L01 "SHUT" (thud plus the hum swelling in). L05 "SNAPS SHUT" (a soft plastic blind clatter, under 4 kHz). L18 "CREAKED" (`assets/audio/sfx/creak`). L24 a slow caster roll. L31 a soft wooden tilt-groan.
- **Ambience:** `assets/audio/amb/crickets.wav` low at night, birds synthesized soft by day, grass steps for Dad crossing the fence (`assets/audio/steps/grass`). All effects under about 4 kHz.
- **The loop:** 0.25 s after "STREET." cut to L01's frame, the hum already running.

## The lore connection (one only)
Two lime-green upright strokes scratched into the chrome of the mower's handle bar, by the left grip, two for a job built for two. Under L43 ("Now Dad holds the CORD, / and Mr. Odell / STEERS."), the line's second shot: a close on the handle, the orange cord in Dad's sleeve at one side, the two strokes plain in the floodlight. Held 1.6 s. Not narrated, never shown again. Plain tally, no extra stroke, touches no thread. (In the canon the Head is one of the Makers' first tries, far too big, older than the street built over it, and its place is kept by a crew of two. Mr. Odell kept it alone for years. Never said.)

## Format
Each line gives the id and who says it, then the caption chunks split with ` / `. The spoken text is the chunks without quote marks. CAPS are the key words, in `#b6ff3b`. Past tense for the story, present for the rule and the ending. Every shot is 2.0 s or less. Times are estimates at 290 wpm.

## 01 The rule (L01 to L06, about 0 to 10 s)
- **Where:** the floodlit lawn at 3 AM, then the street.
- `L01` narrator: My NEIGHBOR / mows his lawn / at three a.m. / with his eyes / SHUT.
  - [S01, 0 to 2.1 s: low close on the blazing green lawn, Mr. Odell pushing the red mower straight at camera, `eyes_shut`, calm smile, face about a quarter of frame width, centred, floodlit. Slow push in. Hit on SHUT.]
- `L02` narrator: Don't LOOK / while it's RUNNING.
  - [S02: inside my dark bedroom, close on the white blinds: one slat dips by itself and the green glow cuts a bright stripe across the frame. Push in.]
- `L03` narrator: The family across the street / PEEKED once.
  - [S03: night, mid shot of the coral house across the street, one blind slat in its upstairs window bent down.]
- `L04` narrator: Their HOUSE has leaned / toward his lawn / ever SINCE.
  - [S04: the coral house straight on, camera level, so the house's 6-degree lean toward his lawn reads, its porch light hanging at the slant.]
- `L05` narrator: At THREE, / every blind on our street / SNAPS SHUT.
  - [S05: a row of three upstairs windows down the street, blinds dropping shut one after another left to right, each over 0.3 s. Hit on SNAPS SHUT.]
- `L06` narrator: He says / it's FASTER / that way. **(quotable)**
  - [S06: tight close on Mr. Odell's face, `eyes_shut`, the floodlights behind his white hair, mower handle at the bottom of frame. Cover frame candidate.]

## 02 Dad (L07 to L14, about 10 to 22 s)
- **Where:** the two front yards by day, bright sun. Then my room at night.
- `L07` narrator: My DAD / has hated that lawn / for TEN YEARS.
  - [S07: bright day, Dad at the low fence in his garden cap, `angry`, glaring over at the green lawn, hose in his sleeve's direction.]
- `L08` narrator: Ours has one BALD SPOT / Dad can't FIX.
  - [S08: our yard, Dad on one knee by the bald circle, a seed bag (built, plain) beside him, `worried`.]
- `L09` narrator: It's perfectly ROUND.
  - [S09: top-down on the bald circle, clean edge, grass all round. Plant 1.]
- `L10` narrator: He's tried SEED. / Then SOD.
  - [S10: seed scattering on the circle, `neutral`. S11: a roll of sod laid on it, already yellowing at the edges.]
- `L11` narrator: Nothing GROWS / in that CIRCLE.
  - [S12: the circle, bare again, a sprinkler ticking over it.]
- `L12` narrator: Our neighbor, / Mr. ODELL, / just WAVES.
  - [S13: first wide: the two houses side by side, the low fence between, Mr. Odell on his mint porch, `smile`, waving, his lawn glowing perfect. Dad in the foreground, arms folded.]
- `L13` narrator: Dad says nobody's grass / is that green / without CHEATING.
  - [S14: Dad's face, `angry`, comic squint. S15: Mr. Odell's lawn, every blade even, the stripes curving.]
- `L14` narrator: So on FRIDAY, / Dad set an ALARM / for THREE.
  - [S16: night, close on Dad's bedside clock reading 3:00 in red digits, then S17: Dad in his robe in my doorway, `neutral`, pointing at my window.]

## 03 Night one (L15 to L22, about 22 to 32 s)
- **Where:** my bedroom window, 3 AM.
- `L15` narrator: The mower STARTED.
  - [S18: through the blinds' gaps, the floodlit lawn, the red mower starting its line. The hum comes in.]
- `L16` narrator: Dad bent ONE slat / of the BLINDS.
  - [S19: close on the blinds from inside, one slat dipping, Dad's eye and mustache in the gap, `neutral`, green light on his face. Me behind him, `worried`.]
- `L17` narrator: The lawn was COMBED / in long, CURVED stripes.
  - [S20: high angle from our window down onto his lawn: every stripe bowing round the low oval hump, like hair brushed over a brow. Plant 2. Held 1.6 s.]
- `L18` narrator: Then OUR house / CREAKED.
  - [S21: wide-ish inside my room, the desk lamp swaying a little. Hit on CREAKED. Meter bubble slides one tick right.]
- `L19` narrator: Every picture in the hall / slid CROOKED.
  - [S22: the hallway, three framed pictures easing to a tilt over 0.8 s.]
- `L20` narrator: Toward HIS lawn.
  - [S23: the three pictures, all tilted the same way, the window at the hall's end glowing green.]
- `L21` narrator: Dad said it was / the FOUNDATION.
  - [S24: Dad at the window, `neutral`, shrugging, me beside him, `worried`.]
- `L22` narrator: He checked it / with his LEVEL anyway.
  - [S25: close on Dad's yellow spirit level on my windowsill, its bubble off-centre toward the window, matching the meter.]

## 04 Night two (L23 to L25, about 32 to 38 s)
- **Where:** our porch and my room, 3 AM.
- `L23` narrator: The next night, / he carried BINOCULARS / out on the PORCH.
  - [S26: our porch, Dad in his robe stepping out, binoculars raised, `angry`. S27: over his shoulder, the floodlit lawn next door, Mr. Odell mowing, eyes shut.]
- `L24` narrator: My desk CHAIR / rolled to the WINDOW / by ITSELF.
  - [S28: my room, me at the desk standing, `scared`, as the empty desk chair rolls slowly across the floor and bumps the wall under the window. Meter two ticks.]
- `L25` narrator: Out there, / the mower crossed / the middle STRIPE.
  - [S29: low on the lawn, the mower rolling over the top of the hump, Mr. Odell `eyes_shut`.]

## 05 The eye (L26 to L31, about 38 to 48 s)
- **Where:** Mr. Odell's lawn under the floodlights. P01 drop before L26.
- `L26` narrator: And the TURF / LIFTED.
  - [S30: close on the lawn by the hump: a long line along the stripes rises 10 cm. Turf creak on TURF.]
- `L27` narrator: A long SEAM / opened in the grass, / slow as an EYELID.
  - [S31: mid shot, the lens-shaped flap of turf lifting along the hump over 1.5 s, warm pale underside showing. S32: lower, the dark gap widening.]
- `L28` narrator: Under it, / an EYE / as big as our GARAGE DOOR / looked UP.
  - [S33: the test still: looking down into the open lid, the huge flat-drawn eye looking up, white highlight, thick black lid stroke, the red mower at the edge of frame with Mr. Odell `eyes_shut`. S34: closer on the pupil, the highlight.]
- `L29` narrator: Straight at DAD.
  - [S35: reverse: Dad on our porch, binoculars lowered a little, `scared`, lit green.]
- `L30` narrator: It didn't BLINK.
  - [S36: the eye, the highlight now aimed toward our porch (moved across the cut).]
- `L31` narrator: Every MAILBOX on the street / tipped our WAY.
  - [S37: the street at night, a row of plain mailboxes leaning toward our house over 0.8 s. Wooden groan. Meter jammed right. S38: our porch light swaying toward the lawn.]

## 06 Said plainly (L32 to L38, about 48 to 60 s)
- `L32` narrator: Mr. Odell's mower / STOPPED.
  - [S39: the mower halting on the lawn. The hum stops dead.]
- `L33` narrator: He kept his eyes SHUT / and called up to me, / "Your dad's LOOKING, / isn't he?"
  - [S40: Mr. Odell's face, `eyes_shut`, tilted up toward my window. S41: me at the window, `scared`, nodding.]
- `L34` narrator: Our whole street / is built / on a HEAD.
  - [S42: low across the lawn, the open eye in the middle ground, his mint house behind.]
  - [P02 drop before. S43: high shot from above our roof: the open eye in his lawn, the curved stripes over it like a brow, the low fence, and our round bald circle just beyond it, all in one frame. Thud on HEAD.]
- `L36` narrator: His lawn / is its EYEBROW.
  - [S44: the striped lawn over the eye, the stripes bowing over it.]
- `L37` narrator: Ours is where / it's going BALD.
  - [S45: top-down on our bald circle again, in moonlight.]
- `L38` narrator: When he trims, / it wakes up / and turns toward / whoever's WATCHING.
  - [S46: the eye, highlight on Dad. S47: the leaning coral house across the street, now read as turned toward the lawn.]

## 07 Neighbors (L39 to L46, about 60 to 74 s)
- `L39` narrator: Dad put down / the BINOCULARS.
  - [S48: Dad on the porch lowering the binoculars, `worried`.]
- `L40` narrator: He SHUT his eyes, / and our pictures / slid back STRAIGHT.
  - [S49: Dad's face, `eyes_shut`. S50: the hall pictures easing back level over 1 s. Meter bubble slides back to centre. The lid sinks shut.]
- `L41` narrator: Then he crossed / the FENCE / to HELP.
  - [S51: Dad stepping over the low white fence onto the green lawn, eyes shut, cap off. Grass steps.]
- `L42` narrator: First time / in TEN YEARS.
  - [S52: Mr. Odell, `eyes_shut`, smiling, turning his face toward Dad's steps.]
- `L43` narrator: Now Dad holds the CORD, / and Mr. Odell / STEERS.
  - [S53: the two of them on the lawn, Dad with the orange cord, Mr. Odell at the handle, both `eyes_shut`, the hum back. S54: the lore shot, close on the handle bar, two lime strokes by the left grip, held 1.6 s.]
- `L44` narrator: Both with their / eyes SHUT.
  - [S55: the pair from my window, mowing a perfect curved stripe.]
- `L45` narrator: Dad still WATERS / the bald spot. / Out of RESPECT.
  - [S56: dawn-blue morning light, Dad with the hose watering the bald circle, `smile`. S57: Mr. Odell waving over the fence, eyes open, `smile`.]
- `L46` narrator: Ask ANYONE / on our street.
  - [S58: back to 3 AM, low on the floodlit lawn, empty, the stripes. The seam opens a crack and the eye looks straight into the lens. Meter twitches right. 0.25 s after STREET, cut to S01.]

## Risks
- **The eye must read as an eye at phone size** (S33): if the flat-drawn style reads as a hole or a sticker, add a second thick lash stroke and more lid curve. Never a realistic modelled eye (ep13's).
- **"Odell":** if `asr` mishears it, respell for the voice only ("Oh-dell"), captions unchanged.
- **Harm words:** none of `checks.HARM` in any line (checked: no took, fell, fall, lost, missing, locked). Nobody is hurt, the tipping is slow and only objects tip.
- **The meter** needs an overlay. If it can't be built, the fallback is Dad's spirit level visible in a corner of every shot, which is weaker.
- **Hands:** R6 hands can't grip. The binoculars sit at Dad's face with the hands out of frame or at the sleeve end. The cord is shown running into his sleeve. The blind slat dips without a hand in close shots.
- **Day vs night HDRI:** one HDRI for the story. The day beats (S07 to S15) are keyed by a sun lamp and the bright sky colour. If they read dull, the builder may lift exposure on those shots only.
