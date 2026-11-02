# ep14-lookout: the script (scriptwriter, 2026-10-31)

- **Working title:** It walked out of the fog toward my fire tower. That's A's, and it replaces the board's "Something taller...". The packager picks the upload title. It can't be an imperative, start with "Something" or "Why", or spoil the lamp.
- **Takeaway:** none, on purpose. It's a made-up blocky story for PandaNanoAdventures, which notes 16, 19 and 21 cover.
- **Target length:** 2:15 to 2:30, never over 3:00.
- **Word count:** 593 spoken words in 73 lines, all `narrator` in voice A, plus 6 pause beats (6.4 s in all).
- **Estimated length:** about 2:18 to 2:24. At 290 wpm the speech is about 2:03. At 278 wpm, ep13's measured rate on lines this short, it's about 2:08. The 0.12 s gaps add about 9 s, the pause beats 6.4 s and the loop tail 0.25 s. If the retime lands under 2:15, I add back "FOG to its WAIST, / its LIGHTS / on my LAMP." after L64 rather than slow anything. If it lands over 2:30, L16 goes first.
- **Shots:** about 64, as the brief plans them. Each section gives its count.
- **From the brief's change list:**
  - C's river is plant 2 (L06 to L07). The smoke hides it at L56 to L57, L58 says it steers by it, and it shines silver at L69 to L70.
  - There's no mug. The lean is the groan, the tilt and the lamp swinging on its wire, and nothing drops.
  - There's no "When I stop, it stops." Its root toes come down where my light just was (L65).
  - The end is at first light, with no moon anywhere.
  - There's no seasonal-job line. L02 opens on me and the lamp.
  - The silence is never narrated. The pulse stops under L35, and P03 is the hole.
  - The ranger has four reported lines, at L04, L13, L19 and L50. I say "All CLEAR." at L51, and I report the treetops at L12 before "COPY."
  - Each beat adds one new sense. It's seen at L08, heard at L15, traces at L22, moving at L27, close at L35 and felt at L39.
  - It leaves "until I can't / TELL it / from the TREES" (L72).
  - The last line is A's, word for word, in the present tense.
  - The 112 stairs stay (L03), so the set builds exactly 112 at 0.175 m, which is the 19.6 m cab floor. The pines are 14 to 17 m, so the line says "STAIRS UP" and never "above the pines".
  - The brief's "It's lost." is now "It can't FIND / its WAY." (L60), because `lost` is a HARM word in `checks.py`. The first line's "LOSE" isn't trapped, so it stays. L72 still answers the riddle.

## Format

Each line gives the id and who says it, then the caption chunks split with ` / `. The spoken text is the chunks in lowercase, without the quote marks, the way `story.json` stores them. CAPS are the key words, in lamp amber `#ffb22e`.

- **Who:** every line is `narrator`, read in voice A. That's me, cast key `me`. The ranger has no cast entry, no voice and no picture. Her four lines are reported in mine, which is note 18's "one voice". Each time she talks we get the radio's click, a static burst and its green light, and none of her audio.
- **Pause beats** (`P01` ...) are sound beats with no words. Each gives a length and its one big on-screen word, or none.
- **Where** heads each section. A line that moves somewhere else says so in brackets under it.
- **Tense:** I tell it in the present tense, which none of batch 1 did. Anything that happened before the moment I'm in is in the past tense ("Whatever BROKE them").

## 01 The question

- **Where:** the cab and the tower by day, in pearl fog. L01 is the outside wide of the lit cab. L02 is inside the cab with me and the lamp. L03 is the tower from below. L04 is the radio. L05 to L07 look out of the cab glass.
- **Shots:** 8.
- **Plants:** the dark mass with two faint warm points behind the cab at L01, never mentioned (the rewatch reward). The burn line at L04, about 8 s, with the grey smudge at L05. The river at L06 to L07, about 11 s. The 112 stairs at L03.

- `L01` narrator: How do you / LOSE / something TALLER / than the TREES?
  - [shot 1: the cab from outside on a pearl-fog morning, the lamp lit inside and me at the glass in my hood. Far back behind the cab, in the fog, a dark mass and two faint warm points. Slow push in]
- `L02` narrator: Up here, / it's just ME / and my LAMP.
  - [inside the cab, the lamp on its bail in my block hand, the cot, the binoculars, the log sheet]
- `L03` narrator: It's a GLASS ROOM / on STEEL LEGS, / a hundred and TWELVE / STAIRS UP.
  - [low on the tower's foot, tilting up the braced legs and the switchback stairs to the cab. The pines round it stop a few metres short of the cab floor]
- `L04` narrator: The radio CLICKS, / and the RANGER says, / "Controlled BURN, / EAST SIDE, / all WEEK."
  - [close on the black radio, its green light on. A static burst, then the light goes off]
- `L05` narrator: Way off EAST, / a GREY SMUDGE / sits on the HILLS.
  - [over my shoulder through the glass: the flat grey-brown smudge far off]
- `L06` narrator: On CLEAR MORNINGS, / the RIVER / in the VALLEY / SHINES like FOIL.
  - [a clear morning before the smoke spreads: the valley far below, a thin silver line in it]
- `L07` narrator: You could STEER / by it.
  - [my face, `neutral`, at the glass. Then a short push down the silver line]

## 02 Seen, heard

- **Where:** the cab by day, with the binocular POV on the far ridge (two soft circles), then the cab at night in blue-grey fog with the lamp steady and the radio's static low.
- **Shots:** 12.
- **Plants:** the snapped treetops that bend toward my tower, about 15 to 22 s, and "COPY." (L08 to L13). The lamp as the only light (L14), for the twist. The breath's creak (L17), paid off at L48 to L49.

- `L08` narrator: Through my BINOCULARS, / the PINES / on the FAR RIDGE / are SNAPPED / at the TOP.
  - [binocular POV: the far ridge, broken pine tops]
- `L09` narrator: A long LINE / of them, / all the SAME HEIGHT.
  - [the POV pans along the line of snapped pines]
- `L10` narrator: Whatever BROKE them / was TALLER / than the TREES.
  - [my face behind the binoculars, `worried`]
- `L11` narrator: The line runs STRAIGHT / for the VALLEY, / then BENDS / toward my TOWER.
  - [wide from behind me in the cab: the snapped line running down the far ridge. Then the binocular POV follows it round the bend until it points at us]
- `L12` narrator: I radio it IN. / "SNAPPED TREETOPS, / FAR RIDGE, / coming THIS WAY."
  - [me at the radio, thumb on the button. The green light stays off while I talk]
- `L13` narrator: The ranger says, / "COPY."
  - [close on the radio: green light, click, static burst, light off]
- `L14` narrator: That NIGHT, / there's no LIGHT / out there / but MINE.
  - [the cab from outside at night: one amber lamp in a black and blue-grey world]
- `L15` narrator: Under the radio's HISS, / I hear BREATHING.
  - [inside, me on the cot, sitting up, `worried`]
- `L16` narrator: SLOW and HEAVY, / out in the FOG.
  - [the night glass, the lamp's glow ending in fog. The cab glass shows no reflection of me]
- `L17` narrator: Every breath / ENDS in a CREAK, / like a TRUNK / in the WIND.
- `P01` pause 0.9 s: none
  - One whole breath under the static, then its trunk creak. The lamp doesn't move.
- `L18` narrator: I key the RADIO / and HOLD it UP / to the DARK.
  - [me at the glass holding the radio out toward the fog. It doesn't touch the glass]
- `L19` narrator: The ranger says, / "Say AGAIN?"
  - [the green light, a click and static]
- `L20` narrator: I let GO / of the BUTTON.
  - [close on my block hand coming off the radio, `scared`]

## 03 Traces, moving

- **Where:** the stairs and the tower's foot in the morning, then the catwalk at dusk looking down the ridge, then the fog-top wide with the tower in frame.
- **Shots:** 11.
- **Plants:** the prints, about 42 s (L22 to L26), all pointing downhill. The saplings on its shoulder stones in the L30 and L31 shots, never said. The pulse enters at P02 with its first step.

- `L21` narrator: In the MORNING, / I take / the STAIRS DOWN.
  - [the switchback plank stairs from above, me going down in daylight]
- `L22` narrator: At the tower's FOOT, / there are PRINTS.
  - [the tower's foot: mud, needles, gold larch leaves, and a print the size of a room]
- `L23` narrator: Each one's / big enough / to LIE DOWN in.
  - [high angle: me standing in one heel, small]
- `L24` narrator: A square HEEL, / and four long TOES / like ROOTS.
  - [close on the four toe grooves]
- `L25` narrator: They're full of RAINWATER, / and GREEN with MOSS.
  - [close on the water, dark and rough, so nothing and nobody shows in it. Moss in the toes]
- `L26` narrator: Every one / points DOWNHILL, / AWAY from ME.
  - [crane up: a trail of prints leading off down the slope, away from the tower. Then my face, puzzled]
- `L27` narrator: At DUSK, / the PINES below me / start to PART.
  - [from the catwalk at dusk, looking down the ridge]
- `L28` narrator: They LEAN AWAY / in a MOVING LINE,
  - [the canopy: a line of pines leaning apart and springing back, travelling uphill]
- `L29` narrator: as something WIDE / walks THROUGH them.
- `P02` pause 1.5 s: THUD
  - Its first footfall, and the pulse comes in on it: a deep thud, a timber creak and a rustle. The lamp on its bail trembles. The pines in the line lean apart.
- `L30` narrator: Then its SHOULDERS / come UP / over the FOG.
  - [the wide with the tower as the ruler: two stone humps and a stump rising above the fog top, three saplings on the left stone and one on the right]
- `L31` narrator: Two BOULDERS / under MOSS, / HIGHER than the TREES.
  - [closer on the stones, moss caps, the saplings]
- `L32` narrator: And between them, / a STUMP / for a HEAD.
  - [the stump in silhouette, no face seen yet]
- `L33` narrator: It's coming / UP the RIDGE. / Toward ME.
  - [my face, `scared`. Behind me through the glass, the shoulders moving uphill along the fog top]

## 04 Close, felt (the scare)

- **Where:** night. The cab, then the catwalk in thick blue-grey fog. L38 to L40 go low on the steel legs for the lean. L41 to L49 are on the catwalk, the face an arm's length off the rail. L50 is inside the cab behind me.
- **Shots:** 13. The lights rising (L42) are on ones.
- **The sound:** the pulse plays on the thuds at L34 to L35 and stops on the step at L35. Nothing replaces it. P03 is the brief's one `music_drops` hole, 0.6 s at -40 dB, keeping the creak and the `sting`.

- `L34` narrator: After DARK, / the THUDS CLIMB / through the FOG.
  - [the cab from outside, the fog top just under the catwalk, no trees showing. Then inside, me at the glass with the lamp, `terrified`, the cab's frame humming on each thud]
- `L35` narrator: Then one LANDS / at the FOOT / of my TOWER.
  - [low on the tower's foot in fog. The pulse stops on this step]
- `L36` narrator: I take my LAMP / out on the CATWALK.
  - [the cab door, then the catwalk, the rail waist-high, fog everywhere past it]
- `L37` narrator: My light STOPS / at a GREY WALL / past the RAIL.
  - [over my shoulder: the lamp's pool lights a flat wall of fog a step out]
- `L38` narrator: Below me, / the tower GROANS.
  - [low on the steel legs and their braces, in fog. A long groan]
- `L39` narrator: The deck TILTS / under my BOOTS.
  - [the small `shake`. The whole tower leans a few degrees]
- `L40` narrator: Something's LEANING / its WEIGHT / on my TOWER.
  - [low again: a dark stone shape in the fog, resting on the frame below the cab. Nothing breaks]
- `L41` narrator: I GRIP the RAIL. / The LAMP SWINGS / on its WIRE.
  - [close on my block hand on the rail and the lamp swinging on its bail. It never flickers]
- `P03` pause 0.6 s: none
  - The hole. Music, ambience and steps fall 40 dB. Only the tower's long creak goes on, and the `sting` lands at the end as the lights start to rise.
- `L42` narrator: Two small LIGHTS RISE / out of the FOG.
  - [on ones: two warm points fading up out of the fog below the rail, never popping on]
- `L43` narrator: WARM ones, / an ARM'S LENGTH / from my FACE.
  - [my face in the lamp's light, `terrified`, the two lights in frame]
- `L44` narrator: They sit DEEP / in a HOLLOW / of BARK.
  - [the catwalk close: the hollow fills half the frame width, the lights its brightest pixels, my lamp raking the bark from behind me]
- `L45` narrator: Its STONE SHOULDERS / come up AFTER them.
  - [wider: the stones rising into the lamp's edge, moss caps, a sapling]
- `L46` narrator: Its HEAD / is WIDER / than my ROOM.
  - [from the cab's far side through the glass: the stump filling the window, the lit cab as the ruler]
- `L47` narrator: It BREATHES OUT, / and the LIGHTS SWELL.
  - [back on the hollow. The lights swell about 15% over the breath]
- `L48` narrator: The breath ENDS / in a CREAK.
- `L49` narrator: I KNOW / that CREAK.
  - [my face, `terrified`, a tiny `tremble`]
- `L50` narrator: The radio CLICKS. / The ranger says, / "LOOKOUT, REPORT."
  - [inside the cab behind me, the radio's green light on]
- `L51` narrator: I say, / "All CLEAR."
  - [me with my thumb on the button, my eyes never leaving the lights]
- `P04` pause 1.0 s: none
  - Hold on the lights an arm's length off the rail. One more breath and its creak. A click as the green light goes off.

## 05 The lamp test

- **Where:** inside the cab at night. L52 to L55 play across the cab with the lights outside the glass. L56 is through the far window over the valley.
- **Shots:** 7.
- **The twist is shown first:** the lights follow the lamp, then stay on it when I step away (L53 to L55). Only then do the words say why.

- `L52` narrator: I back INSIDE. / I carry the LAMP / to the FAR WINDOW.
  - [inside, me crossing the cab with the lamp. Through the glass behind me, the head turns as one piece, under 60°, and the lights go with the lamp]
- `L53` narrator: The two LIGHTS / FOLLOW it.
  - [from outside: the lit cab, the lamp moving along the glass, the two points tracking it]
- `L54` narrator: I set it DOWN / and step AWAY.
  - [I set the lamp on the cot and back into the corner]
- `L55` narrator: They STAY / on the LAMP.
  - [the two lights through the glass, fixed on the cot. I'm out of their line]
- `L56` narrator: In the VALLEY, / SMOKE lies / like MILK.
  - [through the far window: the valley under a flat, pale layer of smoke]
- `L57` narrator: The RIVER / hasn't SHONE / since the BURN.
- `L58` narrator: It STEERS / by the RIVER.
  - [my face, `wide`, putting it together]
- `L59` narrator: And my LAMP / is the only LIGHT / it can SEE.
  - [the lamp on the cot, the two warm points beyond it in the glass]
- `L60` narrator: It can't FIND / its WAY.
- `P05` pause 1.2 s: none
  - Hold the lamp, the lights and the milky valley. Drone and pad only.

## 06 The walk

- **Where:** the stairs, the gate at the tower's foot, the fire road down the mountain at night, then the rocky shelf over the valley at first light.
- **Shots:** 11. Its foot in the lamp's pool (L65) is on ones.
- **The sound:** the pulse comes back on its first step at L64, with a clean, sparse `piano`. The low `choir` comes in once, at P06. The last footfalls fade down the slope at -18 dB.
- **The warm turn is all picture.** No line says why I do it or that it's grateful.

- `L61` narrator: I pick it UP / and HOLD it HIGH.
  - [me lifting the lamp off the cot, `set`]
- `L62` narrator: On the STAIRS, / its LIGHTS / TRACK the LAMP.
  - [the switchback stairs inside the legs. Past the steel, in the fog, the two lights sinking with the lamp]
- `L63` narrator: At the GATE, / I step onto / the FIRE ROAD.
  - [the plank gate at the tower's foot swinging open, the rutted road going down into fog]
- `L64` narrator: BEHIND me, / it STEPS / OUT of the FOG.
  - [the low wide: my small lamp on the road, and behind it the giant stepping after, fog to its waist. It overfills 9:16. The pulse comes back on the footfall. Then closer on its upper half above the fog, the two lights on the lamp]
- `L65` narrator: Its ROOT TOES / come DOWN / where my LIGHT / just WAS.
  - [on ones: close on my boots in the lamp's pool as I walk out of it, and its root-toed foot comes down where the pool just was, well over a metre behind my heels]
- `L66` narrator: My ARM ACHES. / I hold it HIGHER.
  - [close on the lamp held high and my face, `set`]
- `L67` narrator: All NIGHT, / we walk DOWN / the MOUNTAIN.
  - [side wide: the pines along the road leaning apart for it and springing back. Then a high wide: a small amber point on the road, two warm points behind it, the dark forest]
- `L68` narrator: At FIRST LIGHT, / we come out / over the VALLEY.
  - [cold first light. The rocky shelf, the smoke below it, me high above the smoke]
- `L69` narrator: Below us, / the SMOKE is LIFTING, / and the RIVER SHINES.
  - [the valley, smoke thinning, the river showing]
- `P06` pause 1.2 s: none
  - The low `choir` comes in once, as warmth, with faint `water`. The river shows silver far below.
- `L70` narrator: THIN and SILVER, / like FOIL.
  - [over its shoulder stones and saplings: the silver line far below]
- `L71` narrator: It steps PAST me / without LOOKING BACK.
  - [it steps past me with its foot well clear. Its lights leave the lamp and turn down the slope. My face goes `soft`]
- `L72` narrator: It walks DOWN / the SLOPE / until I can't / TELL it / from the TREES.
  - [from the shelf, looking down: its stump and stones, saplings on top, sinking into the canopy until there's only forest. The footfalls fade at -18 dB]

## 07 Spring

- **Where:** the same fire road, green and fogless, with the sapling model in every print. It's shown and never said. There's no time stamp.
- **Shots:** 2.
- **The sound:** `pad` only. A hard cut in from the shelf, and a hard cut out to shot 1.

- `L73` narrator: There's a TREE / in every FOOTPRINT / on the fire ROAD. / All the WAY / to my DOOR.
  - [hard cut from the shelf to spring: low on the road, a small pine in a print, then a slow tilt up the line of them to the tower's gate. After "DOOR", 0.25 s, then a hard cut to shot 1]

## Where it appears

It's "it" in every line and is never named on screen. Its internal name is "the giant".

| Lines | Where | What it's doing |
|---|---|---|
| L01 | far back behind the cab, in fog | a dark mass with two faint points, unmoving, never mentioned |
| L02 to L29 | off screen | only its traces: the snapped line, the breath, the prints, the pines parting |
| P02 | off screen, below the ridge | its first footfall, heard |
| L30 to L33 | above the fog top, mid-distance | its shoulder stones and stump moving uphill. No face seen |
| L34 to L35 | in fog below the cab | heard only, the thuds climbing, then the step at the foot |
| L38 to L41 | low on the tower | one stone shoulder resting on the frame below the cab. The tower leans |
| L42 to P04 | an arm's length off the catwalk rail | the lights rising out of the fog, the hollow, the stones, breathing |
| L52 to P05 | outside the cab glass | its head turning with the lamp, its lights fixed on it |
| L62 to L67 | following the lamp down the stairs and the road | walking stiffly on the pulse, fog to its waist, root toes where my light just was |
| L68 to L70 | behind me on the shelf | standing, its lights on the river as it shows |
| L71 to L72 | stepping past me, down the slope | no look back, until it's part of the trees |
| L73 | off screen | only its prints, each with a small pine |

## Notes for the designer, sound and standards

- **Cast:** `me` is the only cast member, an adult. My age is never on screen or in the voice. The ranger is never seen and her audio never plays.
- **The lamp never flickers** and never goes out, in any shot. At L41 it swings on its bail and doesn't drop.
- **Contact:** its only contact is the ground, the trees and the one stone shoulder on the frame at L38 to L41. It never touches me or the lamp, and its foot stays at least 1 m clear of me at L65 and L71.
- **Peril:** the lean is a few degrees. Nobody slips and nothing breaks or drops. The word "fall" is never said. At L68 I stop high above the smoke.
- **Fire:** the smoke is distant all through. There's no flame, ember, ash or orange glow, and the smoke never reaches me.
- **Words:** the lines contain none of the GRAPHIC, HARM, CHILD or TRUE_CLAIM words in `checks.py`, and none of the brief's extra list. There's no "lost", "still", "kept", "real" or "home", and no real place, park or agency.
- **Fresh against batch 1:** at most 0.5% of its three-word phrases are in any batch 1 story (the block is at 12%). It avoids "one by one", "one after another", "every night", "the next night", "right at me", "pressed flat", "a little closer", "the last one", any "into the [colour or fog]", "it didn't touch me" and "Last night".
- **For `story.json`:** the stub's `twist` still says "so it's lost". That's fine for `check`, which reads lines, but the packager shouldn't lift it.

## Say-it-out-loud notes

- **Voice A** is Kokoro `am_adam` at tempo 1.03, sped up 1.45 times. Everything below is for Kokoro's read and Whisper's word check (`python -m reels.blocky asr`).
- **L01:** a real question, with the lift on "TREES?". Keep it moving so "TREES" lands by about 2.3 s.
- **Words Kokoro might misread:**
  - "wind" (L17) is the noun, WIND with a short i. If it reads "wynd", give it phonemes.
  - "binoculars" (L08) is bih-NOK-yuh-lerz.
  - "LOOKOUT" (L50) is one word, LOOK-out, stressed on the first part.
  - "shone" (L57) can come out "shown" or "shon". Either is fine.
  - "Say AGAIN?" (L19) takes the lift on the last word.
  - "key" (L18) is the verb, said plainly.
  - "a hundred and TWELVE" (L03) is written out, so it's read in full.
  - "ACHES" (L66) is "aykes".
  - "BOULDERS" (L31) is BOHL-derz.
- **Homophones and spellings Whisper could get wrong:**
  - "creak" could come out "creek" at L17, L48 and L49. It's the likeliest one, because there's a river in the story.
  - "through" and "threw" at L08, L29 and L34.
  - "STAIRS" and "stares" at L03, L21 and L62.
  - "STEERS" and "stares" at L07 and L58.
  - "WEIGHT" and "wait" (L40).
  - "hear" and "here" (L15), and "Up here" (L02).
  - "four" and "for" (L24).
  - "ROOT" and "route" (L65).
  - "HISS" and "his" (L15).
  - "key" and "keep" (L18). If Whisper hears "keep", slow the line, never add a gap.
  - "LOOKOUT" and "look out", "RAINWATER" and "rain water", "TREETOPS" and "tree tops", "CATWALK" and "cat walk". These are spelling splits, not mishears.
- **Pauses and beats:**
  - **L13** "COPY." is clipped, and the radio click sits in the gap after it.
  - **P01** (0.9 s) comes after L17, so the breath and its creak play alone.
  - **P02** (1.5 s) comes after L29. It's the first THUD, and the pulse enters on it.
  - **L35** "of my TOWER." lands, and the pulse stops under it. Don't add a pause, because the mix makes the gap.
  - **P03** (0.6 s) comes after L41. It's the hole, and the sting lands as it ends.
  - **L42 to L44** get slower and quieter, line by line.
  - **L49** "I KNOW that CREAK." is the quietest line in the scare.
  - **L51** "All CLEAR." is flat, almost too calm. Then **P04** (1.0 s).
  - **L60** "It can't FIND its WAY." is even, then **P05** (1.2 s). It's the twist, so don't push it.
  - **P06** (1.2 s) comes after L69, where the choir comes in.
  - **L66** "I hold it HIGHER." has a touch of effort, and no smile in the voice.
  - **L72:** soft and slow, the slowest line in the film.
  - **L73:** plain and warm, and not a whisper. Don't trail off after "DOOR". The cut comes 0.25 s after the word ends (`tail` 0.25).
- **Reported speech** is at L04, L12, L13, L19, L50 and L51. It's my voice telling it, with a tiny lift on each quote and no ranger voice.
