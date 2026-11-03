# ep23-only-line: the script (writer, redo of 2026-11-02, round 4 of 2026-11-03)

## Round 4 changes

Standards ruled the old twist repeated ep43-reading-room (solid because a loved one pays me attention, he fades while I tune him out with earbuds, the fix is attention in a quiet room). Now I'm solid because Grandad has always said my mumbled words again, louder, so everyone hears them, and the fix is me doing the same for him in front of a full house.

- **Re-voice these lines:** L12, L15, L45, L46, L47, L48, L49, L50, L51, L52, L54. **L53 is cut** (id kept, like L23). Every other line is unchanged.
- **Changed shots:** S12, S15, S28, S29, S39, S41, S43, S44, S45, S46, S47, S48, S49, S50, S51, S52, S54. S53 is gone. Old S46 to S54 pictures are replaced, not moved.
- **Props:** the white earbuds are removed everywhere. New prop: my **script roll**, a plain cream rolled-up script with no text, tucked under my arm (parented to the torso) or resting on my lap. Hands never grip it. In S44 it slips from under my arm and rolls to the yellow cross (a simple rigid tween). Gone from S48 on.
- **Gesture swap:** Grandad's hand cupped to his ear (old S15, S45, S54) becomes his hand held flat beside his mouth, calling out to the back row. I copy it in S49.
- **Light and sound:** the fix moves to Saturday under the full wash, so the ghost stretch now ends at S45 and the 2 s ramp up is under L46. Soft synthesized applause under L52.
- **package.json:** new pin. `shape` stays `misread`. `hold` kept.

- **Slug:** `ep23-only-line` (folder `stories/ep23-only-line/`). Redo of pitch #7, held because its first line wasn't the world's rule.
- **Title:** see `package.json` ("In This Town The Quiet Ones FADE").
- **Length:** about 441 spoken words in 55 lines (L01 to L57, L23 and L53 cut), all `narrator` in voice A, plus 2 pause beats (1.8 s). At 290 wpm the speech is about 89 s, the 0.12 s gaps add about 7 s, so **about 1:39** (in the 60 to 100 s test band). If it lands over 1:40, cut L29 first, then L05. If under 1:25, leave it.
- **Shape tag:** `misread` (the rule's own word, "quiet", means something other than everyone thinks).

## The big idea (one sentence)

In this town "quiet" means unheard: my grandad, who never stops talking, is fading because I stopped listening to him years ago, and I, the quietest person in town, have never faded because every word I ever mumbled, he said again, louder, for me.

- **The test:** "oh no" (I'm the reason he's fading), then "wait, what" (the quietest person in town was never quiet, because Grandad has been my voice my whole life, and half of all his talking was mine). Both strange details from the first 20 s, the chatty man fading and the silent narrator solid, click at once.
- **Said plainly** in L42 to L45 (about 1:06 to 1:15), with one picture: Grandad nearly glass, turned out to the empty seats with his hand beside his mouth, calling my frozen line to the back row for me (S45).
- **Not ep43:** there, a loved one's attention keeps the narrator real and the fix is speaking up in a silent room. Here nobody's attention keeps me solid. Grandad lends me his voice, and the fix is me lending him mine, on a lit stage before a full, murmuring house, inside the play itself. The rhyme that closes it is Grandma, who once said his line for him from the wings.
- **Pitched and dropped** (ten for the one kept): The old twist (the Prompter kept my place, `stand-in`, too small). A gold mask that says your words when you freeze, and Grandad's says mine (muddled: whose mask, whose voice). I'm an understudy for Grandad's real grandchild (`stand-in` in disguise). Every day happens twice and the first is a rehearsal (no feeling at the end). You hear every word a day early (no loved one at stake). The playhouse rehearses next year (points at a death). A tape mark shows where you'll stand in ten years (same). Applause follows whoever is proud of you (small). The whole week is one night repeating (confusing, ep20's problem). Everyone's life has a script and mine has one line (abstract, no picture).

## What changed against the old version (for the builder)

Everything is re-voiced: every line is new, numbered L01 to L57 from scratch. Old line and shot ids mean nothing now.

- **Kept:** the stage, the four stage left curtain legs, the brick back wall, the ghost light, the house of plum-grey seats, the yellow tape cross and the five white marks, the full-house audience silhouettes (Saturday), costumes (Walt's robe, tin crown and beard piece, my charcoal cloak). The folding chairs aren't used. Cast keys `me`, `walt`, `marion`, `p1` to `p5` stay with their looks. The caption key colour, voice and grade stay.
- **Removed (round 4):** the earbuds. **Removed:** the Prompter (its model, cues and lights), my flat (old S69 to S77), my car (old S53), the chalk tally on the brick (no lore plant now), the dark reverb on quoted lines, the flask.
- **Changed:** Walt is now **Grandad** (never called Walt aloud). He's in his seventies: same white hair, add the short white beard piece in every shot, not only in costume. He **fades**: a per-character transparency driven by a new `fade` cue (see "Fading" below). Marion has a small part (two shots).
- **New set (one small one):** a sunny town street corner for the opening montage (S01 to S08) and the playhouse stage door (S09 to S12). See "World".
- **New characters (all adults):** `stopman` (the man at the bus stop), `mime`, `wife9` and `husband9` (the arguing couple), `busker`, `walker1` and `walker2` (two passers-by, backs to camera), and the faded ones `f1` to `f4`. Each has its own hair and outfit, none copied.
- **New props:** a green-painted wooden bus shelter (no text), a lamp post, a terrace door with a brass numeral 9, a box guitar on a strap (the busker never strums on screen), a beret (mime), my script roll (plain cream, no text, under my arm or on my lap, never gripped), a tall wooden throne chair (Walt, S31).
- **Light:** a new "ghost" mood (the stage wash ramped to about 6%, the ghost light the key). The faded ones are only ever visible in the ghost mood.

## Premise, rule, twist, world

- **Premise:** in a town where the quiet ones fade (you can see the street through them), I'm the quietest person in town and perfectly solid. My grandad, who never stops talking, is fading. This week he's the king in the playhouse play and got me one line so I'd come. Every run I freeze on it, he goes a shade fainter, and under the ghost light the people who faded all the way stand in the wings, nearer each night.
- **The rule (L01):** "In this TOWN, / the QUIET ones / FADE." 7 words. It's the big idea seen from inside: true, but everyone reads "quiet" as "doesn't talk".
- **The marker by 2 s:** a see-through person. S01 is the man at the bus stop in bright sun, half transparent, the brick terrace showing through his chest, his face drawn clear and looking at us.
- **Montage (first 15 s, played for laughs):** the bus-stop man you can see the street through, mimes are basically windows, the couple at number nine argue all day and are solid as brick, the busker never stops singing and is barely there (plant 1).
- **The narrator is the exception:** the quietest person in town, never faded a bit (S07, S08).
- **Loved one at stake, by 0:20, in pictures:** Grandad mid-story at the stage door (S09), the brick through his cheek (S10). What I could lose: him, faded all the way, standing in the wings with the others (shown from L21 on).
- **Seconds 15 to 30, the rule at work, nobody explains:** I turn away to mutter over my line while he's mid-story and he goes a shade fainter (S12). When I mumble my line, he says it again, louder, to the back of the house (S15).
- **The loophole (the climax turns the rule's logic):** he's been on a stage with an audience all week and kept fading, so being loud was never the cure. "Quiet" means unheard, and the reveal shows a voice can be lent: he's been lending me his all my life. On Saturday the house can't hear the faded king, so I do what he always did for me. I say his line again, louder, for the back row, then answer it, and every word they hear brings him back a shade (L46 to L51).
- **Twist and how the last 15 s turn over the first line:** the first line plays as "shy people fade" and the narrator as the strange exception. By the end it means "people nobody hears fade", the narrator is the cause, and the sting ends on someone else in town nobody listened to. The last line, "SOMEBODY / stopped LISTENING / to HIM.", runs straight into "In this TOWN, / the QUIET ones / FADE."
- **Plants a rewatch catches:**
  1. **The busker** (L06, about 0:10): he never stops singing and he's barely there. That breaks the first reading, and it's said in the montage as a joke.
  2. **"Did I ever tell you how I met your Grandma?"** (L11 and L12 at about 0:18, then L27 and L28 at about 0:48): I cut him off both times, and both times he goes a shade fainter in the shot.
  3. **He says it again for me** (L15, about 0:27): I mumble my line and he says it again, louder, to the back of the house. First time it reads as a proud grandad. On a rewatch it's why I'm solid.
  4. **Picture only** (S09): at the stage door he's telling Marion something with his hand on my shoulder while I say nothing. He's talking for me.
- **World:** a small town in late spring. The opening is a sunny street corner: a brick terrace with painted doors, cobbles, a green wooden bus shelter, an iron lamp post, a corner where the busker stands. Then the old playhouse at dusk and in rehearsal week: the stage door (brick, a green door, one lamp), a raked stage of scuffed dark boards, a soot-black proscenium with worn gilt, four bottle-green velvet legs down stage left, the cold brick back wall, a ghost light on a stand, six tape marks in a curve (five white, my yellow cross last, nearest the stage left wings), an empty house of plum-grey seats. Nothing written anywhere. The only numeral is the brass 9 on the couple's door.
- **Ending shape:** a warm button at the bow (Grandma said his line for him from the wings, forty years ago), then the stage empty under the ghost light, the faded back in the wings, and one new one at the back: the bus-stop man from the first shot. A cold sting after the warm turn, looping into his own first shot.
- **Kind of warmth:** a lent voice, handed down. Grandma said his line for him, he said mine for me, and I say his for him.
- **Lore:** no plant. RULES.md → "The shared world is optional now", and a tally here would only muddy the big idea. The faded ones aren't Keepers and have nothing to do with the canon.

## Cast

All adults. Nobody is in peril or shown hurt. Fading never hurts anyone: it's quiet, a shade at a time.

- **Me** (`me`): adult, late twenties, short dark brown block hair, the mustard cable-knit jumper, the charcoal cloak over it on Friday and Saturday. The script roll under my arm in S12, S15, S41 and S43, on my lap in S28 and S29, dropped in S44, gone from S48 on. Always fully solid.
- **Grandad** (`walt`): in his seventies, white block hair, short white beard piece, brown corduroy shirt, and the robe and tin crown in the play shots. Warm, talkative. When I mumble, he holds a flat hand beside his mouth and calls my words out again.
- **Marion** (`marion`): the director, fifties, grey bob, round glasses, teal cardigan. She leaves the ghost light on (only the light is seen, S20) and writes notes without looking up (S39). No quoted lines.
- **The company** (`p1` to `p5`): five adult players on the white marks. They answer the king and look out at the seats. No quoted lines.
- **The bus-stop man** (`stopman`): fifties, flat cap in olive, a tan raincoat, a brown scarf. Half faded in town (S01, S02, S07), fully faded in S56 and S57.
- **The mime** (`mime`): thirties, black and white striped top, black beret, white face paint as a flat white skin colour with our own drawn face. Nearly glass.
- **The arguing couple** (`wife9`, `husband9`): sixties, she in a cherry cardigan, he in a navy jumper and braces. Vivid, saturated, fully solid.
- **The busker** (`busker`): twenties, long block hair, a patched denim jacket, a box guitar on a strap. Faint.
- **Walkers** (`walker1`, `walker2`): two passers-by seen from behind, solid.

## The faded ones (the eerie element, not a monster)

- **Who:** four ordinary townsfolk who faded all the way (`f1` a woman in a long plum coat, `f2` an older man in a cardigan, `f3` a young adult in a hoodie with no print, `f4` a woman in a work tabard of plain sage). Built from the normal rig, nothing wrong in their shape. What's wrong is that they're almost not there.
- **Look:** body alpha about 0.15, so only a warm rim along the silhouette, the drawn face strokes at about 0.35, and two small warm eye glints (the brightest thing in frame). Never grey, never blank-faced: their clothes keep a ghost of their colour.
- **Rules for them:** only visible in the ghost mood. Never seen moving, only nearer. Heads always turned toward whoever is speaking on stage, tilted in when close. They never touch anyone and never come off the stage into the house.
- **Light them so they read:** the ghost light is a low warm key from its stand, plus a thin cool rim from the blue running light in the wings. Test still first: render S37 at phone size before anything else and iterate until the ring of glass people round Grandad reads instantly.

### Continuity

| Beat | Lines | Where the faded ones are | Grandad's alpha |
|---|---|---|---|
| Town | L01 to L08 | not shown (`stopman` half faded at the stop, 0.45) | not shown |
| Stage door | L09 to L12 | not shown | 0.85, ramps to 0.80 under L12 |
| Play set-up | L13 to L15 | not shown | 0.80 |
| Monday | L16 to L23 | `f1` to `f3` behind the 4th leg, facing the stage | 0.80, ramps to 0.72 under L19 |
| Tuesday | L24 to L26 | `f1` to `f4` at the 3rd leg | 0.60 |
| Wednesday | L27 to L30 | not shown (work light) | 0.55, ramps to 0.45 under L28, the crown stays fully solid |
| Thursday | L31 to L33 | `f1` to `f4` at the 1st leg, at the lip of the stage, faces turned to Grandad on the throne | 0.35 |
| Friday dress | L34 to L45 | in a close ring round Grandad at centre stage, heads tilted in toward him | 0.25, then 0.15 from L37 |
| Saturday show | L46 to L51 | not visible (full wash) | 0.15 (the crown floats over a ghost of a robe), ramps to 0.50 under L50, 0.95 under L51 |
| The bow | L52 to L54 | not visible (full wash) | 1.0 |
| After the show | L55 to L57 | `f1` to `f4` behind legs 2 to 4, and `stopman` (alpha 0.15) behind the 4th leg at the back | not shown |

### Fading (the builder's mechanism)

- A cue `fade {"who": key, "a": target, "dur": s}` sets a character's transparency, eased. ep49's `make_fade` in `stories/ep49-car-wash/set.py` is a working pattern (copy it into this set.py, never share the file).
- Face strokes stay stronger than the body: ink alpha = min(1, body alpha x 1.6), so a face always reads at phone size.
- Costume pieces worn over a fading body (the robe) fade with it. The **tin crown never fades**, so from Wednesday it looks like it floats (S30 is the cover candidate).
- Every change of alpha takes at least 1.0 s. No alpha change ever coincides with a cut.

## Look and sound

- **Palette:** town: warm sunny brick, butter-yellow light, painted doors in teal, cherry and navy, green shelter, grey cobbles. Playhouse: bottle-green velvet, soot black, worn gilt, dark boards, cold brick, warm amber wash, cold blue running light, the yellow tape cross, the bare warm ghost light. Keep red out of any frame that changes brightness (the cherry cardigan is only in S04 and S05, steady light).
- **Caption key colour:** greasepaint rose `#ff8fb1` (unchanged).
- **Music:** opens light: A Dorian, 66 bpm, the soft wooden tick on every beat and a bright plucked pad, played for the montage's jokes (L01 to L15). At L16 it turns A Phrygian with a thin drone. The tick stops under each freeze (L18, L24, L35). At L22 (the first faded ones) the heavy low drone enters and holds to L45. At L46 the drone thins with the light coming up and holds low under L47. At L48 it drops out and the pad warms. Under L50 and L51 it turns A major. L52 and L54: A major, quiet, under soft synthesized applause. L55 on: the drone returns, Phrygian, cold, and stops dead on the loop cut.
- **Drops** (`music_drops`): 0.6 s before L33 ("Every FACE / turned to HIM."), and P01, the dim hold before L37, voice and hit only.
- **Sound:** synthesized street air and a far murmur for the town, the busker's song as a soft synthesized reed line of our own (no words, no borrowed tune), the full house's murmur under L47 and its applause under L52, board creaks, the velvet swish, the ghost light's faint hum. The couple's shouting is silent (picture only).
- **Tail:** 0.25 s between the last word and the loop cut.

### Every light change is a slow ramp (flash bar)

- No flicker anywhere. The ghost light glows steady.
- Town shots are steady daylight. The cut from S08 (sun) to S09 (dusk at the stage door) goes between two mid-bright frames: S08 is my hand against the sun but exposed down, S09 has the door lamp and a warm sky.
- **Ghost mood (S20 to S23, S26, S31 to S33, S36 to S45, S55 to S57):** the wash ramps down over 1.6 s to about 6% (under L20, under L36, under L55). Cuts inside a ghost stretch stay at the same dim level. Coming out of it (S24, S27, S46) is a hard cut only to a wash frame of similar brightness, or a 1.8 s ramp up.
- **P01 (1.0 s):** holds the ghost level.
- **Saturday (L46):** the wash ramps up over 2 s from the ghost level, starting on the cut out of P02.
- **Loop seam:** no fade to black. S57 holds the dim ghost-lit close on the bus-stop man. S01 opens on the same man in daylight with a 0.4 s exposure ramp up from about S57's level, so the seam doesn't jump and the rule still reads by 2 s.
- Flash pre-check: the three ghost ramps, the fades under L12, L19, L28, L50 and L51, the Saturday ramp under L46, and the loop seam.

## Format

Each line gives the id and who says it, then the caption chunks split with ` / `. The spoken text is the chunks in lowercase, without quote marks. CAPS are the key words, in greasepaint rose. Every line is `narrator`. Grandad and I are quoted inside the narration and have no voices of their own. Pause beats are sound only. Shots are numbered by the line they sit under, and a line longer than about 2.3 s gets a second shot (`a`, `b`). Present tense for the town (L01 to L15), past for the week.

## Narration and shot plan

### 01 The rule (0:00 to 0:14)

- `L01` narrator: In this TOWN, / the QUIET ones / FADE.
  - [S01: sunny street, mid-close on the bus-stop man under the green shelter, half see-through, the brick terrace and a painted door showing through his chest, his face clear, eyes to camera, `sad`. Slow push in. 0.4 s exposure ramp from the loop seam]
- `L02` narrator: You can see the STREET / right THROUGH / the man at the bus STOP.
  - [S02a: wider: the shelter, the lamp post through his shoulder. S02b: low, the cobbles and a walker's legs passing behind him, seen through his coat]
- `L03` narrator: MIMES / are basically WINDOWS.
  - [S03: the mime doing "the box" on the pavement, nearly glass, the terrace showing through, a solid walker passing without a look. Played for the laugh]
- `L04` narrator: The couple at number NINE / ARGUE all DAY.
  - [S04: a terrace doorstep, the brass 9 on the door, wife9 and husband9 face to face, arms up mid-shout, `angry`]
- `L05` narrator: They're SOLID / as BRICK.
  - [S05: closer on the two, vivid and saturated, still mid-row, the brick wall solid behind them]
- `L06` narrator: The BUSKER on the corner / never STOPS singing, / and he's barely THERE.
  - [S06a: the busker on the corner, mouth open singing, the guitar on its strap, faint (0.4). S06b: walker1 and walker2 passing him, backs to us, not looking. Plant 1]
- `L07` narrator: I'm the QUIETEST person / in TOWN.
  - [S07: me at the bus stop beside the faint man, hands at my sides, mouth shut, `neutral`, fully solid and bright]
- `L08` narrator: I've never faded / a BIT.
  - [S08: my hand raised against the low sun, solid, a crisp shadow across my face. Exposed down a touch for the cut to dusk]

### 02 Grandad (0:14 to 0:28)

- `L09` narrator: My GRANDAD / never STOPS TALKING.
  - [S09: the playhouse stage door at dusk, one lamp, Grandad mid-story to Marion, one hand on my shoulder, the other out wide, `happy`, the white beard piece. I'm silent beside him. Plant 4]
- `L10` narrator: And he's FADING.
  - [S10: close on Grandad's face, the brick of the stage door wall faintly through his cheek (0.85). Readable at phone size]
- `L11` narrator: At the stage DOOR, / he ASKED, / "Did I ever TELL you / how I met your GRANDMA?"
  - [S11a: Grandad leaning toward me, brows up, eager. S11b: over his shoulder to me, half turned away. Plant 2]
- `L12` narrator: I said, / "YES, Grandad," / and went over my LINE / under my BREATH.
  - [S12a: me half turned to the door, eyes down on the script roll under my arm, lips moving. S12b: Grandad's smile dropping, and he goes a shade fainter, 0.85 to 0.80 over 1.2 s. Plant 2]
- `L13` narrator: This week, / he's the KING / in the playhouse PLAY.
  - [S13: wide from the house in warm work light: Grandad in robe and tin crown downstage centre, the company on the five white marks behind him]
- `L14` narrator: He got me ONE LINE, / so I'd COME.
  - [S14: Grandad pointing me onto the yellow cross at the end of the curve, delighted]
- `L15` narrator: When I MUMBLED it, / he said it AGAIN, / LOUDER, / to the BACK / of the HOUSE.
  - [S15a: me on the cross, mouth barely open, the script roll under my arm, `embarrassed`. S15b: Grandad turned out to the empty plum-grey seats, one hand flat beside his mouth, calling my line to the back row, beaming. Plant 3]

### 03 Monday (0:28 to 0:40)

- `L16` narrator: MONDAY, / the king ASKED, / "Who STANDS / with me?"
  - [S16: Walt in robe and crown, arms out, chin up, warm wash]
- `L17` narrator: Five VOICES / ANSWERED.
  - [S17: a quick track along p1 to p5, mouths moving, faces to the seats]
- `L18` narrator: Then ME. / I FROZE.
  - [S18: close on my face, `scared`. The tick stops]
- `L19` narrator: And Grandad / went a SHADE / FAINTER.
  - [S19: Grandad waiting on me, kind, his robe and face easing 0.80 to 0.72 over 1.2 s. The crown stays solid]
- `L20` narrator: After the run, / Marion left the GHOST LIGHT on.
  - [S20: the bare bulb on its stand at centre stage. The wash ramps down over 1.6 s to the ghost mood around it]
- `L21` narrator: In the WINGS, / something CAUGHT the light.
  - [S21: slow push from my mark past legs 1 to 3. Behind the 4th, at head height, two small warm glints and a thin rim]
- `L22` narrator: PEOPLE. / Faded ALL the WAY.
  - [S22a: f1 to f3 standing behind the 4th leg, glass-faint, eye glints, their clothes a ghost of colour, all facing the stage. The heavy drone enters. S22b: closer on f1's face, faint strokes, eyes steady, the brick showing through]
- (`L23` cut while writing. The id is kept so the tables stay right.)

### 04 Tuesday to Thursday (0:40 to 0:58)

- `L24` narrator: TUESDAY, / I FROZE again.
  - [S24: hard cut to warm wash, my face on the cross, `scared`. Tick stops]
- `L25` narrator: You could see the BRICK WALL / through Grandad's ROBE.
  - [S25: wide from the house, Grandad (0.60) at centre, the back wall's brick plain through his body, the crown solid]
- `L26` narrator: And in the ghost LIGHT, / they'd come one curtain NEARER.
  - [S26: ghost mood: f1 to f4 at the 3rd leg, the edge of the velvet across them]
- `L27` narrator: WEDNESDAY, / on our BREAK, / he started AGAIN.
  - [S27: work light: the company and me sitting on the stage lip, legs over the edge, Grandad beside me mid-gesture, `happy`]
- `L28` narrator: I said, / "You TOLD me, Grandad," / before he got to GRANDMA.
  - [S28a: me with the script roll on my lap, lips moving over my line, not looking at him. S28b: Grandad's hand coming down, and he eases 0.55 to 0.45 over 1.2 s. Plant 2 again]
- `L29` narrator: Nobody ELSE / even LOOKED up.
  - [S29: the company along the lip, each looking out at the empty seats, me at the end, eyes on the script roll in my lap]
- `L30` narrator: That RUN, / his CROWN / looked like it was FLOATING.
  - [S30: the tin crown, solid and catching the wash, over a head you can barely make out (0.45). Cover candidate]
- `L31` narrator: THURSDAY, / he stayed on his THRONE, / talking to the empty SEATS.
  - [S31a: wide from the house, the ghost mood, Grandad (0.35) alone on the tall throne at centre, mid-sentence, hands out. S31b: the empty plum-grey rows from behind him]
- `L32` narrator: And the faded ones / were at the EDGE / of the STAGE.
  - [S32: f1 to f4 at the 1st leg, their feet at the stage lip line, close to him]
- `L33` narrator: Every FACE / turned to HIM.
  - [S33: low angle: four faint faces, all turned the same way toward Grandad, eye glints the brightest thing. First real scare]

### 05 Friday, the dress rehearsal (0:58 to 1:16)

- `L34` narrator: FRIDAY, / the dress REHEARSAL.
  - [S34: hard cut to warm wash: wide, everyone in costume, Grandad (0.25), the crown floating over him]
- `L35` narrator: The king ASKED. / I FROZE.
  - [S35: me in the charcoal cloak on the cross, `scared`. Tick stops]
- `L36` narrator: The lights SANK / for the scene CHANGE.
  - [S36: wide from the house, the wash ramping down over 1.6 s to the ghost mood]
- `P01` pause 1.0 s: none
  - The dim hold. Everything out but a low drone.
- `L37` narrator: In the ghost LIGHT, / they were all AROUND him.
  - [S37: the reveal still. Centre stage, Grandad nearly glass (0.15), crown solid, and f1 to f4 in a close ring round him, heads tilted in. Me a step off my mark. Ghost light key low and warm, cool rim from the wings. Test this still first]
- `L38` narrator: CLOSE. / Heads TILTED, / like they were LISTENING.
  - [S38: closer: two faint faces tilted toward him, ears turned in, eye glints]
- `L39` narrator: Grandad was still TALKING.
  - [S39: Grandad's faint face mid-word, `happy`, in the middle of them, turned out to the seats. Behind, the company in the ghost light looking out at the seats, and Marion in the third row, head bowed over her notes]
- `L40` narrator: The faded ones / were the only ones / LISTENING.
  - [S40: wider: the ring of glass people round him, everyone else turned away]
- `L41` narrator: That's when I GOT it.
  - [S41: my face, close, `shocked`, the script roll under my arm at frame edge]
- `L42` narrator: In this town, / QUIET means / NOBODY HEARS you.
  - [S42: Grandad's mouth moving in the ghost light. The music drops to the drone]
- `L43` narrator: And the one he'd been TALKING to / all WEEK / was ME.
  - [S43: from Grandad's eye line: me, a step away, eyes down on the script roll under my arm]
- `L44` narrator: I'd stopped LISTENING / YEARS ago.
  - [S44: low on the boards: the script roll drops from under my arm and rolls to a stop on the yellow tape cross. No hands in frame]
- `L45` narrator: And I'd never FADED, / because every word I ever MUMBLED, / he said AGAIN, / LOUDER.
  - [S45: the one picture. Grandad, almost glass, the crown solid, turned out to the empty seats, one hand flat beside his mouth, calling my frozen line to the back row for me. The ring of faded faces turned with him. Hold]
- `P02` pause 0.8 s: none
  - The ghost light's hum only.

### 06 Saturday (1:16 to 1:29)

- `L46` narrator: SATURDAY, / the king ASKED, / "Who STANDS / with me?"
  - [S46: from the back of the full house over dim heads, the wash ramping up over 2 s. At centre, the tin crown floats over a robe you can barely see (0.15)]
- `L47` narrator: Nobody in the HOUSE / could HEAR him.
  - [S47: the full house from the stage: rows of adults, one leaning to whisper to the next, a man frowning with a hand to his ear. The murmur]
- `L48` narrator: So I did / what he'd always DONE / for ME.
  - [S48: me on the yellow cross in the cloak, no script, `determined`, glancing at him. The drone drops out]
- `L49` narrator: I said his line AGAIN, / LOUDER, / for the BACK ROW.
  - [S49a: me facing the house, one hand flat beside my mouth (his gesture), chin up. S49b: over my shoulder to the back rows, faces lifting]
- `L50` narrator: Then I ANSWERED it. / "I'm HERE, / my LORD."
  - [S50: two-shot: Grandad turning to me, smiling, the colour coming back, 0.15 to 0.50 over 1.5 s. The pad turns to A major]
- `L51` narrator: Every word they HEARD, / he came back / a SHADE.
  - [S51: from behind Grandad (ramping 0.50 to 0.95 over 1.8 s) out to the full house, every face on him, the crown on a solid head again]

### 07 The bow, and the sting (1:29 to 1:39)

- `L52` narrator: At the BOW, / he whispered, / "Did I ever TELL you / how I met your GRANDMA?"
  - [S52: the curtain call along the stage lip, the company bowing, Grandad solid beside me, head turned to me mid-bow. Soft applause. Plant 2 pays off]
- (`L53` cut in round 4. The id is kept so the tables stay right.)
- `L54` narrator: Forty years AGO, / GRANDMA said this line for HIM, / from the WINGS.
  - [S54a: the 1st curtain leg, stage left, empty, warm in the full wash, a step from my yellow cross. S54b: Grandad's face, fully solid, grinning at me]
- `L55` narrator: After, / under the ghost LIGHT, / the faded ones / stood in the WINGS.
  - [S55a: the empty stage, the wash ramping down to the ghost mood. S55b: f1 to f4 behind legs 2 to 4, facing the empty stage. The cold drone returns]
- `L56` narrator: There was a NEW one / at the BACK.
  - [S56: a slow push past the legs: behind the 4th, a fifth faint shape in a flat cap and raincoat]
- `L57` narrator: SOMEBODY / stopped LISTENING / to HIM.
  - [S57: close on him: the bus-stop man from S01, glass-faint now, eyes on the stage. Hold, then the 0.25 s tail and the loop cut to S01 (same man, daylight, half there)]

## Checks done while writing

- Line 1 states the world's rule in 7 words. The see-through man, lit and with a face, is the first picture.
- Four montage examples (bus-stop man, mimes, the couple, the busker) by about 0:12, the exception at 0:12 to 0:14, the loved one fading in a picture at 0:16.
- No backstory or flashback before 0:20. One forward timeline from the street to Saturday. Grandad's story (L54) is one line told in the present, over present-day shots.
- Nobody explains the rule. The reveal is mine, from what I see (S37 to S40), said in L42 to L45 and held on S45.
- The fix uses only the rule and what the reveal showed: a line said again louder gets heard, so it counts (S15, S45, L49).
- Plants: the busker (L06), the cut-off Grandma story twice (L11 to L12, L27 to L28) with a fade in each shot, my line said again louder (L15), Grandad talking for me at the stage door (S09). The last line runs into the first.
- The counts: five white marks and five players (p1 to p5), five voices in L17. Four faded ones until S56, five in S56 and S57.
- Picture against line: "solid as brick" over vivid solid people in front of a brick wall. "Barely there" over a 0.4 busker. "The brick wall through Grandad's robe" with the back wall behind him at 0.60. The crown is the only thing that never fades.
- Batch 1 echoes avoided: no knowing elder (Grandad never explains the rule), no night shift or one summer, no pale grey blank face (the faded keep faces and colour), no "pressed flat", no "Last NIGHT," opener, no age said or shown, no "it didn't touch me", no "not X, it was Y" (L42 states what quiet means without a contrast).
- Hard rule 2: nobody is hurt or in danger of harm, no death words. Fading is quiet and reversible (L50, L51). Grandma in Grandad's story was an adult.
- Hard rule 8 on every line, the title, description and pin: no dashes, semicolons, slogans, parenthetical lists or AI words.
- Originality (round 4, checked against every story's twist): the rule type (being heard) is new on the channel. ep43 keeps its narrator real through a loved one's attention and fixes it by speaking up in a silent room. Here I'm solid through a voice lent to me, and the fix is lending it back, on a lit stage before a full house, inside the play. No headphones, earbuds or tuning out by device. floor-thirteen (talking breaks the lift's spell) and ep47 (a truth said aloud) use speech differently. The shape stays `misread`.
