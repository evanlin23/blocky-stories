# ep20-photo-strip

**Slug:** `ep20-photo-strip`

## Premise
At a cousin's wedding in an old hotel, I (an adult) and my older sister Wren haven't spoken in two years. Mum asks for one photo of the two of us from the old coin photo booth in the hall, "sitting in the middle, together". We sit at opposite ends of the bench every time. Every strip that comes out has a faded brown hand on the velvet between our heads, and each strip shows more of the figure it belongs to.

## Rule
Mum's one ask: sit in the MIDDLE, together (L08). We break it on every visit by sitting at the far ends, and break it hardest on the last coin (L30), with the curtain shut.

## Twist
The figure never moved. Its hand is on the same seam, at the same height, in every frame. Wren and I were sliding further apart each strip, and every inch we gave it showed more of it. "It's getting closer" (L01) first reads as the thing coming for us. After L44 to L47 it reads as the two of us drifting apart, and after the last line (L60, "she leaned IN, and whispered,") it loops back as Wren saying it about us, warmly.
- **Plant 1 (L14, S12 and S14):** the hand rests "right on the SEAM down the middle". The seam is in shot in every strip close-up.
- **Plant 2 (L17 and L22, S17 and S22):** "Wren slid to the very edge of the bench, so I slid to MINE." and "my elbow poked out past the CURTAIN." Each strip close-up shows the two of us a little further out to the frame edges.
- Bonus plant (L20): Wren says "it was leaning IN". A rewatch hears that she's the one leaning out.

## World
One old hotel on a wedding night. A long hall with bottle-green plain wallpaper, a dark patterned carpet (geometric, no text), three brass wall lamps (the middle one over a small side table), a closed ballroom door at the far end with warm light and a muffled waltz behind it. In an alcove halfway down: the photo booth, older than the hotel. Dark wood cabinet, a plum velvet curtain at the front on a brass rail, one long bench inside, plum velvet hung on the back panel with one vertical seam down the centre, a single dome lamp above a round dark lens, a brass coin slot and a brass delivery slot outside. No lettering anywhere: no signs, no logos, no names on the booth, cake, banners or strips.

## Cast (all adults, nobody in peril or hurt)
- **me** (adult, mid-twenties, narrator): navy suit jacket with a breast pocket that can hold a half strip, white shirt, loosened mustard tie, short swept hair, dark brown. Round eyes, brows.
- **Wren** (adult, older sister, late twenties): forest-green dress (shirt and pants the same green, knit pattern), block bob hair in auburn, small brass hair clip. Classic eyes, brows, a "fish face" expression for L56 (lips pushed out and cheeks in, an opt-in `faces.py` face).
- **Mum** (adult): lilac blazer, grey bob, glasses. Appears at L07 to L08 and L16 only. She asks and sighs, she explains nothing and knows nothing.

## The creature: the Third (never named on screen)
- One model, built once in `set.py` and posed per shot. A full R6 person in an old-fashioned dark three-piece suit, **far too tall (2.6 m, its head sits up inside the booth's roof cavity)** and **perfectly flat: 2 cm thick**. From the front it reads as a person. From the side it's a single dark line.
- Its whole surface is one faded sepia-brown tone with a fine grain, like an old print (suit a darker sepia, skin and hands a paler sepia #b59878, never grey). Face: two small black dot eyes set too high and too far apart, no highlight, and a long thin smile cut as a dark slot (opening onto black), wider than the head should allow.
- Its right hand is always flat on the back velvet, exactly on the centre seam, at Wren's ear height when seated. **This position never changes in any beat.** Only what we can see of it changes.
- Never seen moving. Lit from below by the booth lamp, with a cold rim from the hall.

**Continuity by beat**
| Beat | Lines | Where it is / what shows |
|---|---|---|
| Hook, strip 1 | L01 to L04, L12 to L15 | Behind the bench at the seam. Only the hand shows in the strip, between our heads. Not visible in the room. |
| Strip 2 | L17 to L20 | Same spot. In the strip: hand, forearm, sleeve and one shoulder, because we sit further out. |
| Strip 3 | L21 to L26 | Same spot. In the strip: whole body from the mouth down, the frame top cuts it at the smile. Frame 4: the smile slot drawn wider (a face swap, same model). |
| Scare, booth dark | L31 to L40 | Same spot, now seen in the room at the second glow. Hand on the seam. Head up in the roof cavity, turned about 150 degrees to face me (the head is the only re-posed part). S38 side view: a dark line between us. |
| Hall | L48 to L52 | Standing in the dark midpoint of the hall between Wren and me, flat, face-on to camera. Each step shot (S50 to S52) the dark pool around it is smaller, it never moves. Gone by S53. |
| Last strip | L58 | Not in the strip: no space between us. |

## Look
- **Palette:** plum velvet #5a2448, brass #c8963c, bottle-green walls #1d3a2c, tungsten warm #ffb86a, the Third's sepia #8a6a4a / #b59878 with black ink, Wren's green #2f6b46, my navy #26324f.
- **Caption key colour:** brass gold `#ffc04a` (ep11 lime, ep12 red and ep13 cyan are taken).
- **Music:** D Lydian, 3/4 waltz at 72 bpm. A slow detuned waltz pad, as if leaking from the ballroom, with our own synthesized melody (no borrowed tune, no music box). Drops for 0.6 s before L31 ("Then it went OUT") and before L35 ("It was THERE"), and again before L49. From L55 the waltz comes back clean and brighter, the drone gone.
- **Sound:** a soft electric hum and a rising whine for each booth glow, a mechanical whirr and paper slide as the strip comes out, a dry paper flick for L33 (synthesized noise burst), curtain-ring scrape, distant ballroom murmur.

## Flash plan (hard rule 7)
The booth lamp is the risk. Every glow is a 0.3 s warm ramp to about 70% (never clipped white), at least 0.7 s apart, and L11 shows the four glows on the outside of the curtain in one shot, not four cuts. L31 to L40: one ramp down, one glow up, one dark: three changes over about 4 s. Run `python -m blocky flash` pre-check on S10, S30 to S39 at the final's frame steps.

## Shot plan
| Shot | Line | Picture |
|---|---|---|
| S01 | L01 | Inside the booth, close on the strip lying on the bench between our two knees (no hands on it). Frame 4 shows the brown hand between our heads. |
| S02 | L02 | Wren at the far left end, face lit by the lamp, looking at me. Cut away from the slide. |
| S03 | L03 | Wide of the hall, the booth in its alcove, ballroom glow at the far end. |
| S04 | L04 | Insert: the strip, push in on the hand in frame 1. |
| S05 | L05 | Two-shot outside the booth, Wren and me, a whole metre apart, both looking away. |
| S06 | L06 | Close on me, jaw set. |
| S07 | L07 | Mum between us in the hall, hopeful. |
| S08 | L08 | Mum, close, warm smile. |
| S09 | L09 | Into the booth past the curtain: the bench and the back velvet with its seam lit by the dome lamp. |
| S10 | L10 | From the lens: Wren far left, me far right, the empty middle of the bench. |
| S11 | L11 | Outside, the curtain glows four times. Then the delivery slot (strip appears, cut on it). |
| S12 | L12 | Insert of strip 1: our two heads at the edges, a hand between them. |
| S13 | L13 | Extreme close on the hand in the print: sepia, grain. |
| S14 | L14 | The real back velvet, empty, the seam sharp. Plant 1. |
| S15 | L15 | Side angle outside: the booth's back flush against the hall wall. |
| S16 | L16 | Mum's face, sigh. |
| S17 | L17 | From the lens: both of us shuffled to the very ends. Plant 2. |
| S18 | L18 | Insert strip 2: arm in a dark suit, a shoulder. |
| S19 | L19 | Close on its hand on the seam in the print. |
| S20 | L20 | Wren, small voice, eyes on the strip. |
| S21 | L21 | Hall, the cake on a trolley passing the ballroom door (blank white cake, no topper text). |
| S22 | L22 | Outside the booth: my elbow poking out past the curtain edge. Plant 2. |
| S23 | L23 | Insert strip 3, frame 1: the whole flat body behind the bench between us. |
| S24 | L24 | Strip 3 frame 2: the frame top cuts it at the mouth. |
| S25 | L25 | Close on the slot smile in the print. |
| S26 | L26 | Strip 3 frame 4: the smile wider. Hold. |
| S27 | L27 | Two-shot in the hall, us facing off, me then Wren. |
| S28 | L28 | Curtain closed from outside. Cut to the coin slot (no hand). |
| S29 | L29 | Wren inside, not looking at me. |
| S30 | L30 | From the lens: us at the ends, shoulders to the side walls. Middle empty, seam lit. |
| S31 | L31 | One glow, then the dome lamp out. Music drop before. |
| S32 | L32 | Near-black, Wren's eye highlights and a faint rim on her edge. |
| S33 | L33 | Black, the middle of the bench, a dry paper flick. |
| S34 | L34 | The glow ramps up from below. |
| S35 | L35 | The reveal (test still first): from my end, the Third standing behind the bench in the middle, lit from below, rim from the curtain gap. Music drop before. |
| S36 | L36 | Close on its hand on the seam. |
| S37 | L37 | Low angle up past my shoulder: its head in the roof, turned round too far, dot eyes and slot smile on me. |
| S38 | L38 | Me leaning, eyes wide. |
| S39 | L39 | Side view along the bench: between Wren and me a single dark line, floor to roof. |
| S40 | L40 | Dark again. Curtain thrown open from outside (cut on the swing, no grip). |
| S41 | L41 | Wide hall: Wren out one side, me the other, going opposite ways. |
| S42 | L42 | The middle lamp's side table: four strips laid in a row (cut in already laid). |
| S43 | L43 | Close on my face, realising. |
| S44 | L44 | Slow slide along all sixteen frames: the hand on the seam, same height. |
| S45 | L45 | Frame 1 of strip 1 and frame 4 of strip 4 side by side, the hand identical. |
| S46 | L46 | Same frames: our two heads further to the edges strip by strip. |
| S47 | L47 | Strip 3 frame 1 again. Push in on the gap. |
| S48 | L48 | Wide hall: Wren at the far end under the far lamp, me under the near lamp. |
| S49 | L49 | Between us in the unlit middle, the flat Third, face-on. Music drop before. |
| S50 | L50 | Wren looks at it, then steps toward me (one step, cut on it). |
| S51 | L51 | My step toward her. The pool of dark around it smaller. |
| S52 | L52 | Wide again: the dark smaller still, the Third dimmer. |
| S53 | L53 | Under the middle lamp, us side by side, nothing between. |
| S54 | L54 | Wren half smiles. Me, the same. |
| S55 | L55 | From the lens: both of us in the middle of the bench, squashed, her elbow in my ribs. Waltz comes back clean. |
| S56 | L56 | Wren pulls the fish face. |
| S57 | L57 | Me pulling it back. Wren laughing (open mouth face, eyes squeezed). |
| S58 | L58 | Insert last strip: the two of us, shoulders touching, no gap, no hand. |
| S59 | L59 | Two half strips: one sticking out of my breast pocket, the other face down on the side table. **Lore plant:** on its back, three short faded-brown stamped strokes, held 1.5 s, never mentioned. |
| S60 | L60 | Walking back toward the ballroom glow, Wren bumps my shoulder and leans in. Cut on "whispered," back to S01. |

## The last 15 seconds turn the first line
"It's getting CLOSER" opens as a whispered warning about the thing in the strip. The twist (L44 to L47) shows it never came closer: we were drifting apart. The last line ends on Wren leaning in to whisper, and the loop drops straight into "It's getting CLOSER." On a second watch the opening line is Wren about the two of us, and the creeping strips become a record of how far apart we'd sat. Rewatch plants: the hand on the seam (L14, S12 and S14) and the two of us sliding to the ends (L17, L22, S17 and S22).

## Lore connection (one)
The back of Wren's half of the last strip (S59, under L59, "Wren tore it in half") carries three short stamped strokes in the Third's faded brown: a tally. Only two of us are in the photo. In the canon (`stories/lore.md`), this is a Keeper's count, and the third stroke is the Third, still counted, standing where it always stands. Not narrated. The pin points at it.

## Narration (60 lines, 633 words, about 2:11 of speech at 290 wpm, about 2:18 with gaps)
Every line is `who: narrator`. CAPS are the caption key words.

L01. "It's getting CLOSER."
L02. My sister Wren slid the strip along the bench to ME.
L03. Four pictures from the old booth at our cousin's WEDDING.
L04. And between our heads, in every picture, a HAND.
L05. Wren and I hadn't spoken in two YEARS.
L06. Over something too small to even NAME.
L07. Mum wanted one photo of her two, from the booth in the hotel HALL.
L08. "Sit in the MIDDLE," she said. "TOGETHER."
L09. Inside was one long bench, with plum velvet behind it.
L10. Wren sat at the far LEFT end. I sat at the far RIGHT.
L11. The lamp glowed four times, slow and WARM, and the strip slid OUT.
L12. That's when we saw the HAND.
L13. Faded brown, like a very OLD photo.
L14. Resting on the velvet behind us, right on the SEAM down the middle.
L15. But the back of the booth was solid wood, flush with the WALL.
L16. Mum looked at the strip and sighed. "That's not TOGETHER."
L17. Wren slid to the very edge of the bench, so I slid to MINE.
L18. Second strip. An ARM now, in a dark old suit, and a SHOULDER.
L19. Its hand was still on the SEAM.
L20. Wren's voice went small. She said it was leaning IN.
L21. Third strip, after the CAKE.
L22. We sat so far apart my elbow poked out past the CURTAIN.
L23. Now it was a whole BODY, standing behind the bench between us.
L24. So tall the top of every picture cut it off at the MOUTH.
L25. A long, thin smile, as dark as the coin SLOT.
L26. In the fourth picture, the smile was WIDER.
L27. I told Wren I was done with this. She said she'd been done for two YEARS.
L28. Then she shut the curtain and fed in our last COIN.
L29. One more, she said. For MUM.
L30. We sat at opposite ends, not looking at each OTHER.
L31. The lamp glowed once. Then it went OUT.
L32. In the dark, Wren was breathing at her END.
L33. And in the MIDDLE, a sound like a page being TURNED.
L34. The second glow lit the booth.
L35. It was THERE. Right between us.
L36. Its hand on the seam, exactly where the photos SAID.
L37. Its head was up by the roof, turned all the way round to ME.
L38. I leaned to see it from the SIDE.
L39. From the side, it was a LINE. As thin as a sheet of PAPER.
L40. The lamp went dark again, and we both RAN.
L41. Wren went out one side of the curtain. I went out the OTHER.
L42. Under a hall lamp I spread all four strips on a TABLE.
L43. And then I SAW it.
L44. Its hand was on the seam in every picture, at the same HEIGHT.
L45. It had never come one inch CLOSER.
L46. Wren and I had been sliding APART, a little more every STRIP.
L47. It had always been THERE. We just kept giving it more ROOM.
L48. I looked up. Wren was at the far end of the hall. I was at THIS one.
L49. And in the dark between us, something tall and flat stood in the MIDDLE.
L50. Wren looked at it. Then she took one step toward ME.
L51. I took one toward HER.
L52. With every step, the dark between us got SMALLER.
L53. We met under the middle lamp, with nothing left between us at ALL.
L54. She said she couldn't remember what we'd fought about. Neither could I.
L55. We went back in and sat right in the MIDDLE, her elbow in my RIBS.
L56. She pulled the fish face from every family photo we'd ever TAKEN.
L57. I pulled it right back, and she laughed so hard she SNORTED.
L58. The strip came out. Just the two of us, without a sliver of space BETWEEN.
L59. Wren tore it in half and tucked two pictures in my jacket POCKET.
L60. On the way back to the dance, she bumped my shoulder, leaned IN, and whispered,
